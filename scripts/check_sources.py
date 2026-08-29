#!/usr/bin/env python3
"""Check official sources for drift against dev-policy pins.

Fetches each ``canonical_url`` in each family's ``sources.yaml`` and
compares the configured ``detect`` regex (or git HEAD) to the stored
``pin``. Network errors are expected and reported as ``FETCH_FAIL``,
not tracebacks.

On DRIFT, patch the owning pack with a bite-sized rule; then bump
``pin``. Do **not** auto-merge official HTML into the packs. Do not dump
manuals into packs.

This checker never prints secrets. Requests use User-Agent
``dev-policy-check/<version>``.

Examples:
    Validate every family (no network)::

        python3 scripts/check_sources.py --offline

    One family::

        python3 scripts/check_sources.py --offline --family os/linux

    Check one source (family required if the id is not unique)::

        python3 scripts/check_sources.py --family program-language/rust \\
            --source rust-releases -v

Exit codes:
    0  all checked sources UNCHANGED, or ``--offline`` schema OK
    1  unexpected error (bad YAML, missing file, programmer error)
    2  at least one DRIFT (takes precedence over FETCH_FAIL)
    3  at least one FETCH_FAIL and no DRIFT
"""

from __future__ import annotations

import argparse
import html
import logging
import os
import re
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    import yaml
except ImportError as exc:  # pragma: no cover - import guard
    raise SystemExit(
        "PyYAML is required. Install with: pip install pyyaml\n"
        "Or from the repo root: pip install -e ."
    ) from exc

__version__ = "1.0.0"
__all__ = ["main"]

USER_AGENT = f"dev-policy-check/{__version__}"
LOGGER = logging.getLogger("check_sources")

BUCKETS = ("os", "program-language")
ALLOWED_SPLITS = frozenset(
    {"language", "ecosystem", "os", "application", "both", "meta"}
)
ALLOWED_PIN_KINDS = frozenset({"version", "date", "commit", "regex"})
REQUIRED_FIELDS = (
    "id",
    "title",
    "canonical_url",
    "git",
    "watch_path",
    "packs",
    "split",
    "pin_kind",
    "pin",
    "detect",
    "notes",
)

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_DRIFT = 2
EXIT_FETCH_FAIL = 3


class SchemaError(ValueError):
    """``sources.yaml`` failed structural validation."""


@dataclass(frozen=True)
class DetectSpec:
    """How to extract an observed pin from a fetched body or git remote.

    Attributes:
        method: ``regex`` (HTTP body) or ``git_ls_remote`` (git HEAD).
        regex: Pattern applied to the response body.
        group: Capture group to use when ``join`` is unset. ``0`` is the
            full match. ``None`` means group 1 if the pattern has groups,
            else 0.
        join: If set, join all numbered capture groups with this string.
        flags: Optional ``re`` flag letters: ``I``, ``M``, ``S``.
        ref: Git ref for ``git_ls_remote`` (default ``HEAD``).
    """

    method: str = "regex"
    regex: str | None = None
    group: int | None = None
    join: str | None = None
    flags: str = ""
    ref: str = "HEAD"

    def compiled(self) -> re.Pattern[str]:
        """Compile ``regex`` with the configured flags.

        Returns:
            Compiled pattern.

        Raises:
            SchemaError: If no regex is configured or it does not compile.
        """
        if not self.regex:
            raise SchemaError("detect.regex is required for method=regex")
        flag_value = 0
        for char in self.flags.upper():
            if char == "I":
                flag_value |= re.IGNORECASE
            elif char == "M":
                flag_value |= re.MULTILINE
            elif char == "S":
                flag_value |= re.DOTALL
            elif char in {" ", ","}:
                continue
            else:
                raise SchemaError(f"unknown detect.flags letter {char!r}")
        try:
            return re.compile(self.regex, flag_value)
        except re.error as exc:
            raise SchemaError(f"invalid detect.regex: {exc}") from exc


@dataclass(frozen=True)
class Source:  # pylint: disable=too-many-instance-attributes
    """One official document watched by a policy family."""

    id: str
    title: str
    canonical_url: str
    git: str | None
    watch_path: str | None
    packs: tuple[str, ...]
    split: str
    pin_kind: str
    pin: str
    detect: DetectSpec
    notes: str
    cadence: str | None = None
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False)


@dataclass(frozen=True)
class Family:
    """One ``sources.yaml`` and the sources it owns."""

    rel: str
    path: Path
    sources: tuple[Source, ...]


@dataclass(frozen=True)
class BoundSource:
    """A source tagged with the family that declared it."""

    family: str
    source: Source


@dataclass(frozen=True)
class CheckResult:
    """Outcome of checking one source."""

    status: str
    source_id: str
    detail: str = ""
    family: str = ""

    def line(self) -> str:
        """Return the one-line report for stdout."""
        prefix = f"{self.family} " if self.family else ""
        if self.status == "UNCHANGED":
            return f"UNCHANGED {prefix}{self.source_id}"
        if self.status == "DRIFT":
            return f"DRIFT {prefix}{self.source_id} {self.detail}"
        return f"FETCH_FAIL {prefix}{self.source_id} {self.detail}"


def repo_root_from(script_file: Path) -> Path:
    """Return the repository root (parent of ``scripts/``).

    Args:
        script_file: Path of this file.

    Returns:
        Directory that contains ``os/`` and ``program-language/``.
    """
    return script_file.resolve().parent.parent


def parse_detect(raw: Any, source_id: str) -> DetectSpec:
    """Parse a ``detect`` field into :class:`DetectSpec`.

    Args:
        raw: Mapping or regex string from YAML.
        source_id: Source id for error messages.

    Returns:
        Parsed detect spec.

    Raises:
        SchemaError: If the value is not a supported shape.
    """
    prefix = f"{source_id}.detect"
    if isinstance(raw, str):
        return DetectSpec(method="regex", regex=raw)
    if not isinstance(raw, dict):
        raise SchemaError(f"{prefix} must be a mapping or regex string")
    method = str(raw.get("method") or "regex")
    if method not in {"regex", "git_ls_remote"}:
        raise SchemaError(f"{prefix}.method must be regex or git_ls_remote")
    regex = raw.get("regex")
    if regex is not None and not isinstance(regex, str):
        raise SchemaError(f"{prefix}.regex must be a string")
    group = raw.get("group")
    if group is not None and not isinstance(group, int):
        raise SchemaError(f"{prefix}.group must be an int")
    join = raw.get("join")
    if join is not None and not isinstance(join, str):
        raise SchemaError(f"{prefix}.join must be a string")
    flags = raw.get("flags") or ""
    if not isinstance(flags, str):
        raise SchemaError(f"{prefix}.flags must be a string")
    ref = raw.get("ref") or "HEAD"
    if not isinstance(ref, str):
        raise SchemaError(f"{prefix}.ref must be a string")
    spec = DetectSpec(
        method=method,
        regex=regex,
        group=group,
        join=join,
        flags=flags,
        ref=ref,
    )
    if method == "regex":
        spec.compiled()
    return spec


def _optional_str(value: Any) -> str | None:
    """Return ``None`` for YAML null/empty, else a string."""
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    raise SchemaError(f"expected string or null, got {type(value).__name__}")


def parse_source(  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    raw: Any,
    index: int,
    allowed_packs: frozenset[str],
) -> Source:
    """Validate and parse one YAML source mapping.

    Args:
        raw: YAML node.
        index: Zero-based index in the ``sources`` list.
        allowed_packs: Filenames listed at the document ``packs:`` key.

    Returns:
        Parsed :class:`Source`.

    Raises:
        SchemaError: On missing or invalid fields.
    """
    loc = f"sources[{index}]"
    if not isinstance(raw, dict):
        raise SchemaError(f"{loc} must be a mapping")
    missing = [name for name in REQUIRED_FIELDS if name not in raw]
    if missing:
        raise SchemaError(f"{loc} missing fields: {', '.join(missing)}")
    source_id = raw["id"]
    if not isinstance(source_id, str) or not source_id.strip():
        raise SchemaError(f"{loc}.id must be a non-empty string")
    source_id = source_id.strip()
    if not re.fullmatch(r"[a-z][a-z0-9-]*", source_id):
        raise SchemaError(f"{loc}.id {source_id!r} is not a slug")
    title = raw["title"]
    if not isinstance(title, str) or not title.strip():
        raise SchemaError(f"{source_id}.title must be a non-empty string")
    url = raw["canonical_url"]
    if not isinstance(url, str) or not url.startswith("https://"):
        raise SchemaError(f"{source_id}.canonical_url must be an https URL")
    try:
        git = _optional_str(raw["git"])
        watch_path = _optional_str(raw["watch_path"])
    except SchemaError as exc:
        raise SchemaError(f"{source_id}: {exc}") from exc
    if git is not None and not git.startswith(("https://", "git://")):
        raise SchemaError(f"{source_id}.git must be a git URL or null")
    packs_raw = raw["packs"]
    if not isinstance(packs_raw, list) or not packs_raw:
        raise SchemaError(f"{source_id}.packs must be a non-empty list")
    packs: list[str] = []
    for pack in packs_raw:
        if pack not in allowed_packs:
            raise SchemaError(
                f"{source_id}.packs contains unknown file {pack!r} "
                f"(allowed: {sorted(allowed_packs)})"
            )
        packs.append(str(pack))
    split = raw["split"]
    if split not in ALLOWED_SPLITS:
        raise SchemaError(f"{source_id}.split must be one of {sorted(ALLOWED_SPLITS)}")
    pin_kind = raw["pin_kind"]
    if pin_kind not in ALLOWED_PIN_KINDS:
        raise SchemaError(
            f"{source_id}.pin_kind must be one of {sorted(ALLOWED_PIN_KINDS)}"
        )
    pin = raw["pin"]
    if not isinstance(pin, (str, int, float)) or str(pin).strip() == "":
        raise SchemaError(f"{source_id}.pin must be a non-empty scalar")
    notes = raw["notes"]
    if not isinstance(notes, str) or not notes.strip():
        raise SchemaError(f"{source_id}.notes must be a one-line string")
    cadence = raw.get("cadence")
    if cadence is not None and not isinstance(cadence, str):
        raise SchemaError(f"{source_id}.cadence must be a string if set")
    detect = parse_detect(raw["detect"], source_id)
    if pin_kind == "commit" and detect.method != "git_ls_remote" and not detect.regex:
        raise SchemaError(
            f"{source_id}: commit pins need detect.method=git_ls_remote or a regex"
        )
    return Source(
        id=source_id,
        title=title.strip(),
        canonical_url=url,
        git=git,
        watch_path=watch_path,
        packs=tuple(packs),
        split=str(split),
        pin_kind=str(pin_kind),
        pin=str(pin).strip(),
        detect=detect,
        notes=notes.strip(),
        cadence=str(cadence).strip() if cadence else None,
        raw=raw,
    )


def _parse_allowed_packs(document: Mapping[str, Any], yaml_path: Path) -> frozenset[str]:
    """Read and verify the document-level ``packs:`` allowlist.

    Args:
        document: Parsed YAML root.
        yaml_path: Path of the YAML file (pack files sit beside it).

    Returns:
        Allowed pack filenames.

    Raises:
        SchemaError: If the list is missing, empty, or names a missing file.
    """
    packs_raw = document.get("packs")
    if not isinstance(packs_raw, list) or not packs_raw:
        raise SchemaError(f"{yaml_path}: top-level packs must be a non-empty list")
    allowed: list[str] = []
    family_dir = yaml_path.parent
    for pack in packs_raw:
        if not isinstance(pack, str) or not pack.strip():
            raise SchemaError(f"{yaml_path}: packs entries must be non-empty strings")
        name = pack.strip()
        if "/" in name or name in {".", ".."}:
            raise SchemaError(f"{yaml_path}: pack {name!r} must be a basename")
        pack_file = family_dir / name
        if not pack_file.is_file():
            raise SchemaError(f"{yaml_path}: pack file missing: {name}")
        allowed.append(name)
    return frozenset(allowed)


def load_family(path: Path, rel: str) -> Family:
    """Load and validate one family's ``sources.yaml``.

    Args:
        path: Path to the YAML file.
        rel: Family id relative to the repo root (``os/linux``).

    Returns:
        Parsed family.

    Raises:
        SchemaError: If the document is invalid.
        OSError: If the file cannot be read.
    """
    with path.open(encoding="utf-8") as handle:
        document = yaml.safe_load(handle)
    if not isinstance(document, dict):
        raise SchemaError(f"{rel}: sources.yaml root must be a mapping")
    allowed = _parse_allowed_packs(document, path)
    items = document.get("sources")
    if not isinstance(items, list) or not items:
        raise SchemaError(f"{rel}: sources.yaml must contain a non-empty sources list")
    sources = [
        parse_source(item, index, allowed) for index, item in enumerate(items)
    ]
    seen: set[str] = set()
    for source in sources:
        if source.id in seen:
            raise SchemaError(f"{rel}: duplicate source id {source.id!r}")
        seen.add(source.id)
    return Family(rel=rel, path=path, sources=tuple(sources))


def discover_source_files(root: Path) -> list[Path]:
    """Return ``sources.yaml`` paths under ``os/`` and ``program-language/``.

    Args:
        root: Repository root.

    Returns:
        Paths in bucket order, then sorted by family name.
    """
    found: list[Path] = []
    for bucket in BUCKETS:
        bucket_dir = root / bucket
        if not bucket_dir.is_dir():
            continue
        found.extend(sorted(bucket_dir.glob("*/sources.yaml")))
    return found


def family_rel_for(yaml_path: Path, root: Path) -> str:
    """Return the family id for a YAML path.

    Args:
        yaml_path: Path to ``sources.yaml``.
        root: Repository root.

    Returns:
        POSIX path relative to ``root`` of the family directory.
    """
    try:
        return yaml_path.parent.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return yaml_path.parent.name


def resolve_yaml_targets(
    root: Path,
    families: Sequence[str],
    sources_file: str | None,
) -> list[Path]:
    """Resolve which YAML files to load.

    Args:
        root: Repository root.
        families: ``--family`` values (empty = all discovered).
        sources_file: Explicit ``--sources`` path.

    Returns:
        YAML paths to load.

    Raises:
        SchemaError: If flags conflict or a family is unknown.
    """
    if sources_file and families:
        raise SchemaError("use --sources or --family, not both")
    if sources_file:
        return [Path(sources_file)]
    discovered = discover_source_files(root)
    if not discovered:
        raise SchemaError(
            f"no sources.yaml under {root}/os or {root}/program-language"
        )
    if not families:
        return discovered
    by_rel = {family_rel_for(path, root): path for path in discovered}
    resolved: list[Path] = []
    missing: list[str] = []
    for rel in families:
        if rel in {".", ".."} or rel.startswith("/") or ".." in Path(rel).parts:
            raise SchemaError(f"invalid --family {rel!r}")
        path = by_rel.get(rel)
        if path is None:
            missing.append(rel)
        else:
            resolved.append(path)
    if missing:
        known = ", ".join(sorted(by_rel)) or "(none)"
        raise SchemaError(
            f"unknown --family {', '.join(missing)} (known: {known})"
        )
    return resolved


def one_line(text: str, limit: int = 160) -> str:
    """Collapse whitespace so a value fits on one report line.

    Args:
        text: Raw observed or error text.
        limit: Maximum characters after collapse.

    Returns:
        Single-line string, possibly truncated with an ellipsis.
    """
    collapsed = re.sub(r"\s+", " ", text).strip()
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 3] + "..."


def extract_observed(body: str, detect: DetectSpec) -> str | None:  # pylint: disable=too-many-return-statements
    """Extract the observed pin from an HTTP body.

    Args:
        body: Decoded response text.
        detect: Detect spec with a regex.

    Returns:
        Extracted string, or ``None`` if the pattern did not match.
    """
    match = detect.compiled().search(body)
    if match is None:
        return None
    if detect.join is not None:
        if not match.groups():
            return match.group(0)
        return detect.join.join(group or "" for group in match.groups())
    if detect.group is not None:
        try:
            value = match.group(detect.group)
        except IndexError:
            return None
        return value if value is not None else None
    if match.groups():
        return match.group(1)
    return match.group(0)


def pins_match(pin: str, observed: str) -> bool:
    """Return whether ``observed`` equals the stored pin.

    Comparison is case-sensitive after trimming and collapsing internal
    whitespace, so HTML/ICS wrapping does not cause false drift.
    """
    return one_line(pin) == one_line(observed)


def fetch_url(url: str, timeout: float) -> str:
    """HTTP GET ``url`` and return the decoded body.

    Args:
        url: Absolute https URL.
        timeout: Socket timeout in seconds.

    Returns:
        Response body as text.

    Raises:
        urllib.error.URLError: Network failure.
        urllib.error.HTTPError: Non-success HTTP status.
        TimeoutError: Deadline exceeded.
        OSError: Local socket errors.
    """
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": (
                "text/html,application/xhtml+xml,text/plain,"
                "text/calendar,text/markdown,*/*;q=0.8"
            ),
        },
        method="GET",
    )
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=timeout, context=context) as resp:
        raw = resp.read()
        charset = resp.headers.get_content_charset() or "utf-8"
    try:
        return raw.decode(charset, errors="replace")
    except LookupError:
        return raw.decode("utf-8", errors="replace")


def git_ls_remote(repo: str, ref: str, timeout: float) -> str:
    """Return the object id of ``ref`` from ``git ls-remote``.

    Args:
        repo: Git URL.
        ref: Ref to resolve (usually ``HEAD``).
        timeout: Subprocess timeout in seconds.

    Returns:
        Hex object id.

    Raises:
        FileNotFoundError: ``git`` is not on PATH.
        subprocess.CalledProcessError: Git failed.
        subprocess.TimeoutExpired: Git exceeded ``timeout``.
        SchemaError: Output was empty or malformed.
    """
    result = subprocess.run(
        ["git", "ls-remote", repo, ref],
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    )
    line = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
    sha = line.split()[0] if line else ""
    if not re.fullmatch(r"[0-9a-f]{7,40}", sha):
        raise SchemaError(f"unexpected git ls-remote output: {one_line(result.stdout)}")
    return sha


def fetch_fail_reason(exc: BaseException) -> str:  # pylint: disable=too-many-return-statements
    """Map a network/git exception to a short FETCH_FAIL reason.

    Args:
        exc: Raised error.

    Returns:
        Single-line reason with no secrets.
    """
    if isinstance(exc, urllib.error.HTTPError):
        return f"HTTP {exc.code}"
    if isinstance(exc, TimeoutError):
        return "timeout"
    if isinstance(exc, urllib.error.URLError):
        reason = exc.reason
        if isinstance(reason, TimeoutError) or "timed out" in str(reason).lower():
            return "timeout"
        return one_line(str(reason) or "url error")
    if isinstance(exc, subprocess.TimeoutExpired):
        return "git timeout"
    if isinstance(exc, FileNotFoundError):
        return "git not installed"
    if isinstance(exc, subprocess.CalledProcessError):
        return f"git exit {exc.returncode}"
    if isinstance(exc, ssl.SSLError):
        return "tls error"
    return one_line(f"{type(exc).__name__}: {exc}")


def check_source(source: Source, timeout: float) -> CheckResult:  # pylint: disable=too-many-return-statements
    """Fetch one source and compare the observed value to ``pin``.

    Args:
        source: Source entry.
        timeout: HTTP/git timeout in seconds.

    Returns:
        UNCHANGED, DRIFT, or FETCH_FAIL result (family filled by caller).
    """
    detect = source.detect
    if detect.method == "git_ls_remote":
        if not source.git:
            return CheckResult("FETCH_FAIL", source.id, "git url missing")
        try:
            observed = git_ls_remote(source.git, detect.ref, timeout)
        except (
            FileNotFoundError,
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            SchemaError,
            OSError,
        ) as exc:
            LOGGER.debug("git ls-remote failed for %s", source.id, exc_info=True)
            return CheckResult("FETCH_FAIL", source.id, fetch_fail_reason(exc))
        if _commit_matches(source.pin, observed):
            return CheckResult("UNCHANGED", source.id)
        return CheckResult(
            "DRIFT",
            source.id,
            f"{source.pin} -> {observed}",
        )

    try:
        body = fetch_url(source.canonical_url, timeout)
    except (
        urllib.error.HTTPError,
        urllib.error.URLError,
        TimeoutError,
        ssl.SSLError,
        OSError,
        ValueError,
    ) as exc:
        LOGGER.debug("fetch failed for %s", source.id, exc_info=True)
        return CheckResult("FETCH_FAIL", source.id, fetch_fail_reason(exc))

    LOGGER.debug("fetched %s (%d bytes)", source.id, len(body))
    observed = extract_observed(html.unescape(body), detect)
    if observed is None:
        return CheckResult("DRIFT", source.id, f"{source.pin} -> <no match>")
    observed = observed.strip()
    if pins_match(source.pin, observed):
        return CheckResult("UNCHANGED", source.id)
    return CheckResult("DRIFT", source.id, f"{source.pin} -> {one_line(observed)}")


def _commit_matches(pin: str, observed: str) -> bool:
    """Compare commit pins allowing a short prefix of a full SHA."""
    pin_l = pin.lower()
    obs_l = observed.lower()
    if pin_l == obs_l:
        return True
    if len(pin_l) >= 7 and obs_l.startswith(pin_l):
        return True
    if len(obs_l) >= 7 and pin_l.startswith(obs_l):
        return True
    return False


def bind_sources(families: Sequence[Family]) -> list[BoundSource]:
    """Flatten families into sources tagged with their family id."""
    bound: list[BoundSource] = []
    for family in families:
        for source in family.sources:
            bound.append(BoundSource(family=family.rel, source=source))
    return bound


def select_sources(
    bound: Sequence[BoundSource],
    wanted: Sequence[str],
) -> list[BoundSource]:
    """Filter sources by id.

    Args:
        bound: All loaded sources.
        wanted: Ids requested on the command line (empty = all).

    Returns:
        Selected sources in family-then-YAML order.

    Raises:
        SchemaError: If an id is unknown or present in more than one family.
    """
    if not wanted:
        return list(bound)
    by_id: dict[str, list[BoundSource]] = {}
    for item in bound:
        by_id.setdefault(item.source.id, []).append(item)
    selected: list[BoundSource] = []
    missing: list[str] = []
    ambiguous: list[str] = []
    for source_id in wanted:
        hits = by_id.get(source_id, [])
        if not hits:
            missing.append(source_id)
        elif len(hits) > 1:
            places = ", ".join(hit.family for hit in hits)
            ambiguous.append(f"{source_id} ({places})")
        else:
            selected.append(hits[0])
    if missing:
        known = ", ".join(item.source.id for item in bound)
        raise SchemaError(
            f"unknown --source id(s): {', '.join(missing)} (known: {known})"
        )
    if ambiguous:
        raise SchemaError(
            "source id(s) in more than one family; pass --family: "
            + "; ".join(ambiguous)
        )
    wanted_set = set(wanted)
    return [item for item in bound if item.source.id in wanted_set]


def build_parser() -> argparse.ArgumentParser:
    """Return the CLI parser."""
    parser = argparse.ArgumentParser(
        prog="check_sources.py",
        description=(
            "Fetch official sources and report pin drift. On DRIFT, patch the "
            "owning pack with a bite-sized rule; then bump pin. Do not dump "
            "manuals into packs."
        ),
    )
    parser.add_argument(
        "--sources",
        metavar="FILE",
        default=None,
        help="path to one sources.yaml (default: every family)",
    )
    parser.add_argument(
        "--family",
        action="append",
        default=[],
        metavar="REL",
        help="family directory relative to repo root (repeatable; e.g. os/linux)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="validate YAML schema only; do not fetch",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        metavar="SEC",
        help="HTTP/git timeout in seconds (default: 20)",
    )
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        metavar="ID",
        help="check only this source id (repeatable)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="verbose logging; repeat for debug",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="log errors only; still print one line per source",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def configure_logging(verbose: int, quiet: bool) -> None:
    """Configure the module logger.

    Args:
        verbose: ``-v`` count.
        quiet: If true, only log errors.
    """
    if quiet:
        level = logging.ERROR
    elif verbose >= 2:
        level = logging.DEBUG
    elif verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def load_selected_families(
    root: Path,
    yaml_paths: Sequence[Path],
) -> list[Family]:
    """Load each YAML path as a family.

    Args:
        root: Repository root (for relative ids).
        yaml_paths: Files to load.

    Returns:
        Parsed families in the given order.
    """
    families: list[Family] = []
    for yaml_path in yaml_paths:
        resolved = yaml_path if yaml_path.is_absolute() else (Path.cwd() / yaml_path)
        rel = family_rel_for(resolved, root)
        LOGGER.info("reading %s (%s)", resolved, rel)
        families.append(load_family(resolved, rel))
    return families


def run(argv: Sequence[str] | None = None) -> int:  # pylint: disable=too-many-return-statements
    """Run the checker.

    Args:
        argv: Command-line arguments without the program name. ``None``
            uses :data:`sys.argv`.

    Returns:
        Process exit code (0, 1, 2, or 3).
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.verbose, args.quiet)
    if args.timeout <= 0:
        LOGGER.error("--timeout must be positive")
        return EXIT_ERROR

    root = repo_root_from(Path(__file__))
    try:
        yaml_paths = resolve_yaml_targets(root, args.family, args.sources)
        families = load_selected_families(root, yaml_paths)
        bound = bind_sources(families)
        selected = select_sources(bound, args.source)
    except FileNotFoundError as exc:
        LOGGER.error("sources file not found: %s", exc)
        return EXIT_ERROR
    except OSError as exc:
        LOGGER.error("cannot read sources: %s", exc)
        return EXIT_ERROR
    except SchemaError as exc:
        LOGGER.error("schema: %s", exc)
        return EXIT_ERROR
    except yaml.YAMLError as exc:
        LOGGER.error("YAML parse error: %s", exc)
        return EXIT_ERROR

    if args.offline:
        LOGGER.info("schema OK (%d sources in %d families)", len(selected), len(families))
        return EXIT_OK

    had_drift = False
    had_fetch_fail = False
    for item in selected:
        LOGGER.info(
            "checking %s/%s (%s)",
            item.family,
            item.source.id,
            item.source.canonical_url,
        )
        try:
            result = check_source(item.source, args.timeout)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            LOGGER.debug("unexpected error for %s", item.source.id, exc_info=True)
            result = CheckResult("FETCH_FAIL", item.source.id, fetch_fail_reason(exc))
        result = CheckResult(result.status, result.source_id, result.detail, item.family)
        print(result.line())
        if result.status == "DRIFT":
            had_drift = True
        elif result.status == "FETCH_FAIL":
            had_fetch_fail = True

    if had_drift:
        return EXIT_DRIFT
    if had_fetch_fail:
        return EXIT_FETCH_FAIL
    return EXIT_OK


def main() -> int:
    """Entry point returning an exit code."""
    try:
        return run()
    except KeyboardInterrupt:
        LOGGER.error("interrupted")
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
