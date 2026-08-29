---
title: "Python Language Policy"
description: Curated map of what Python requires of the code — dialect, stdlib security APIs, typing, PEP 8, tests. Not PyPI and not OS packaging.
version: "1.0.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - README.md
  - python-ecosystem-policy.md
  - python-os-policy.md
last_updated: "2026-08-29"
---

# Python Language Policy

Reference pack for **what the code is** when it is hosted Python:
language version, stdlib security contracts, typing, PEP 8, tests.

**Role:** curated map (working memory). **Not** L4 for any one app.
**Not** PyPI, lockfiles, or `twine` — that is
[python-ecosystem-policy.md](python-ecosystem-policy.md).
**Not** apt, pacman, Homebrew, or the python.org installer — that is
[python-os-policy.md](python-os-policy.md).

Last verified against docs.python.org and PEPs as of 2026-08-29.
Current stable: **3.14** (bugfix). **3.15** is prerelease (rc1
2026-08-04; final expected 2026-10-01) and is **not** the ship bar.

Security-over-features starts here: prefer **stdlib** APIs that
already have a security story (`ssl`, `hashlib`, `secrets`,
`subprocess`, `tomllib`, `json`, `urllib`) over a third-party
import. Whether a third-party package is *allowed at all* is the
Ecosystem trust bar.

------------------------------------------------------------------------
0. LAYERING
------------------------------------------------------------------------

This pack owns:

- `requires-python` *meaning* (which language you write)
- Stdlib modules and their security-relevant contracts
- Typing (PEP 484 family) as convention
- PEP 8 as style convention; Ruff/black as extras that implement it
- Tests that must exist (`unittest` is stdlib)

This pack does **not** own:

- `pyproject.toml` keys, lockfiles, PyPI, pip-audit
  → Ecosystem
- Which `python3` binary is on PATH, venv vs distro, PEP 668
  → OS

------------------------------------------------------------------------
1. FOUNDATIONAL DOCUMENTS
------------------------------------------------------------------------

Language reference
https://docs.python.org/3/reference/

Library reference (stdlib)
https://docs.python.org/3/library/

What’s new in 3.14
https://docs.python.org/3/whatsnew/3.14.html

Version status
https://devguide.python.org/versions/
https://peps.python.org/pep-0745/  (3.14)
https://peps.python.org/pep-0790/  (3.15 schedule)

PEP 8
https://peps.python.org/pep-0008/

Typing
https://docs.python.org/3/library/typing.html
https://typing.python.org/en/latest/

Security (language/stdlib)
https://docs.python.org/3/library/security_warnings.html
https://docs.python.org/3/library/ssl.html
https://docs.python.org/3/library/hashlib.html
https://docs.python.org/3/library/secrets.html
https://docs.python.org/3/library/subprocess.html

Ruff (**extra** linter/formatter)
https://docs.astral.sh/ruff/

------------------------------------------------------------------------
2. DIALECT AND VERSION
------------------------------------------------------------------------

Ship bar: **3.14** in CI for a new hosted project. `requires-python`
minimum **3.12** unless an OS carve-out forces lower (then record it
in the OS pack and test that interpreter).

Do not write 3.15-only syntax until 3.15.0 final. Do not require
free-threaded `python3.14t` as the default (PEP 779: supported
build, GIL still default).

https://peps.python.org/pep-0779/

`from __future__ import annotations` is optional on 3.14 (PEP 649
deferred evaluation). Public libraries that support 3.12 should
still type-check on 3.12.

One dialect per package. Optional extras that need 3.14 APIs must be
gated (`sys.version_info`) and tested.

------------------------------------------------------------------------
3. STDLIB SECURITY CONTRACTS
------------------------------------------------------------------------

These are **language** facts. A third-party replacement must still
pass the Ecosystem trust bar *and* not weaken these.

**Do not**

- `eval` / `exec` / `compile(..., exec)` on untrusted input
- `pickle` / `marshal` / `shelve` on untrusted bytes
- `yaml.load` without a `SafeLoader` (that call is third-party;
  the *pattern* is language)
- `subprocess` with `shell=True` and unsanitised input
- `random` for tokens, reset codes, or crypto (`secrets` instead)
- `hashlib.md5` / `sha1` for security (non-crypto checksums: say so)
- `ssl._create_unverified_context` or `verify=False` in http clients
- Temporary files in world-writable dirs without `O_EXCL` /
  `tempfile.TemporaryDirectory`

**Do**

- `ssl.create_default_context()` for TLS
- `hashlib.sha256` or better; `hashlib.scrypt` / `hashlib.pbkdf2_hmac`
  for passwords (or a trusted KDF after the Ecosystem bar)
- `secrets.token_urlsafe` / `secrets.compare_digest`
- `subprocess.run(..., shell=False, check=True)` with a *sequence*
  argv
- `json` / `tomllib` (3.11+) for config; not `pickle`
- `pathlib` for paths; do not concatenate unsanitised `..`

`http.client` / `urllib.request` are stdlib. `requests` /
`httpx` are Ecosystem trust decisions. Security-over-features:
stdlib until the trust bar says the extra is worth it.

Logging must not write secrets. `repr()` of auth headers is a
language leak.

------------------------------------------------------------------------
4. TYPING AND API SHAPE
------------------------------------------------------------------------

Public functions have annotations. `mypy` / `ty` / Ruff's type
rules are **extras** that check this. `Any` as a public contract is
a stall unless documented.

`TypedDict` / `dataclasses` / `enum` are stdlib. Pydantic is
Ecosystem (trust bar). Prefer stdlib data shapes for *internal*
code; a validation library is allowed when the bar passes.

------------------------------------------------------------------------
5. STYLE
------------------------------------------------------------------------

PEP 8 is the convention.
https://peps.python.org/pep-0008/

Ruff format / Ruff lint default rules are extras that implement a
PEP 8-shaped bar plus bugbear. `ruff check` / `ruff format --check`
are the usual CI extra (like `cargo fmt` + clippy defaults).

`select = ["ALL"]` plus a wall of ignores is Clippy restriction.
Cherry-pick. Do not call ALL "PEP 8".

A house line length other than PEP 8's 79 (or Ruff's 88 default) is
a fork. Document it.

------------------------------------------------------------------------
6. TESTS
------------------------------------------------------------------------

Claimed behavior has a test that runs. **`unittest`** is stdlib and
is enough. `pytest` is a third-party runner — allowed only via the
Ecosystem trust bar. Security-over-features: `unittest` until pytest
is justified (fixtures, parametrize at scale).

https://docs.python.org/3/library/unittest.html

Doctest is stdlib; keep it for public examples.

------------------------------------------------------------------------
7. QUALITY CHECKS (THE CODE)
------------------------------------------------------------------------

Every PR:

```text
python -m compileall -q src tests
python -m unittest discover
```

**CI extra** (not PEP 8 itself):

```text
ruff check .
ruff format --check .
```

Must-haves

- Runs on the claimed `requires-python`
- No `eval`/`pickle` on untrusted input
- TLS verify on
- Tests exist

Not this pack: lockfile hashes, pip-audit, dh-python, MSVC.

------------------------------------------------------------------------
8. WHAT THIS PACK EXPLICITLY IS NOT
------------------------------------------------------------------------

Not PyPI. Not a list of blessed packages. Not PEP 668 (OS). Not
Django/Flask tutorials.

------------------------------------------------------------------------
9. COMPOSING
------------------------------------------------------------------------

  this pack
  + [python-ecosystem-policy.md](python-ecosystem-policy.md)
  + [python-os-policy.md](python-os-policy.md) shared + one carve-out

A new `import foobar` is an Ecosystem trust-bar event even if the
call site is Language.

------------------------------------------------------------------------
10. QUICK OFFICIAL LINK LIST
------------------------------------------------------------------------

https://docs.python.org/3/reference/
https://docs.python.org/3/library/
https://devguide.python.org/versions/
https://peps.python.org/pep-0008/
https://docs.python.org/3/library/ssl.html
https://docs.python.org/3/library/secrets.html
https://docs.python.org/3/library/subprocess.html

Sister packs
./python-ecosystem-policy.md
./python-os-policy.md
./README.md

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.0.0 | Initial language pack: 3.14 ship bar, stdlib security contracts, PEP 8, unittest-first |
