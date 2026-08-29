---
title: "Python Ecosystem Policy"
description: Curated map of how a Python project lives — pyproject.toml, hash-pinned lockfiles, PyPI, trusted-library bar, pip-audit. Security over feature sprawl.
version: "1.0.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - README.md
  - python-language-policy.md
  - python-os-policy.md
last_updated: "2026-08-29"
---

# Python Ecosystem Policy

Reference pack for **how a hosted Python project lives**: packaging
metadata, lockfiles, PyPI, and **which third-party libraries may be
depended on**.

**Role:** curated map (working memory). **Not** L4 for any one app.
**Not** PEP 8 or `secrets` — that is
[python-language-policy.md](python-language-policy.md).
**Not** apt/pacman/Homebrew/python.org installers — that is
[python-os-policy.md](python-os-policy.md).

Last verified against PyPA and PyPI documents as of 2026-08-29.

Python has tens of thousands of importable projects. This pack
**enforces a trusted-library bar** and **prefers security over
available features**. It does **not** ship a named allowlist of
PyPI projects (those rot and become product law). It ships the
**admission rules**. The names that passed live in *your* lockfile.

pip is the PyPA installer. **uv** and **Poetry** are lock/install
*tools* (extras) that still must emit a hash-pinned lock this pack
can audit.

------------------------------------------------------------------------
0. LAYERING
------------------------------------------------------------------------

This pack owns:

- `pyproject.toml` (PEP 517/518/621) identity
- Dependency declaration and **trust bar**
- Lockfiles and **hash pinning**
- PyPI store rules, yank, trusted publishing
- `pip-audit` / OSV as the advisory gate
- SPDX in project metadata
- Build backends (setuptools, hatchling, flit) as *how you build*,
  not OS install

This pack does **not** own:

- Whether `eval` is UB-shaped — Language
- Distro `python3` / EXTERNALLY-MANAGED — OS
- `dh-python` — OS Debian

------------------------------------------------------------------------
1. FOUNDATIONAL DOCUMENTS
------------------------------------------------------------------------

PyPA packaging guide
https://packaging.python.org/en/latest/

PEP 517 / 518 / 621 (pyproject.toml)
https://peps.python.org/pep-0517/
https://peps.python.org/pep-0518/
https://peps.python.org/pep-0621/

pip
https://pip.pypa.io/en/stable/
Hash-checking
https://pip.pypa.io/en/stable/topics/secure-installs/

PyPI
https://pypi.org/policy/terms-of-use/
https://docs.pypi.org/project_accounts/
Trusted publishing:
https://docs.pypi.org/trusted-publishers/
Attestations:
https://docs.pypi.org/attestations/

pip-audit (PyPA)
https://github.com/pypa/pip-audit
https://pypi.org/project/pip-audit/

PEP 668 (externally managed — OS also cites this)
https://peps.python.org/pep-0668/

PEP 751 (pylock.toml, standard lockfile)
https://peps.python.org/pep-0751/

OpenSSF / OSV (advisory extra interchange)
https://osv.dev/

------------------------------------------------------------------------
2. PYPROJECT IDENTITY
------------------------------------------------------------------------

https://packaging.python.org/en/latest/guides/writing-pyproject-toml/

Must-haves for a hosted project:

- `[project]` name, version, description
- `requires-python` (Language owns the dialect; this field stores it)
- `license` / `license-files` (SPDX)
- `dependencies` — every entry has passed §4
- `[build-system]` with a **pinned** backend (`requires = ["setuptools==…"]`
  or a lock that pins the backend)

Should: `readme`, `authors` or `maintainers`, `urls.repository`,
optional `classifiers`.

Do not put unpinned extras that pull the internet (`foo[all]` from
an unknown project). Extra names you *define* are fine; extra names
you *consume* are more supply chain.

`tool.*` tables (ruff, mypy, pytest) are CI extras. They must not
sneak in new runtime deps.

------------------------------------------------------------------------
3. LOCKFILES AND HASHES
------------------------------------------------------------------------

https://pip.pypa.io/en/stable/topics/secure-installs/
https://peps.python.org/pep-0751/

**Every ship and every CI install is hash-pinned.** Unpinned
`pip install package` is not a release path.

Acceptable lock shapes (pick one, commit it):

- PEP 751 `pylock.toml`
- `requirements.txt` with `--hash=` (pip-tools or `pip freeze` is
  not enough without hashes)
- `uv.lock` (tool extra) if `uv export` / install uses hashes
- Poetry `poetry.lock` (tool extra) with installation that verifies
  hashes

Install:

```text
python -m pip install --require-hashes -r requirements.txt
```

or the uv/poetry equivalent that refuses unhashed artifacts.

`==` without hashes still allows a substituted wheel from an extra
index. Hashes close that. `--no-deps` plus a fully expanded lock
prevents resolver surprises.

Commit the lockfile for applications. Libraries still lock *their*
CI extra-deps (dev/audit tools) so `pip-audit` has a graph.

Do not float `>=0` or `*`. PyPI will accept many ranges; this pack
does not. Direct deps: lower bound you tested + upper bound you
mean (compatible release `~=1.2.3` is allowed *in pyproject* if the
**lock** still pins exact + hash).

------------------------------------------------------------------------
4. TRUSTED-LIBRARY BAR (SECURITY OVER FEATURES)
------------------------------------------------------------------------

This section is the expansion this repo exists for. It is **this
pack's bar**, not a PEP. Labeled as such.

A **trusted library** is a third-party distribution you have
admitted. Stdlib modules are not "trusted libraries"; they are
Language. OS packages of Python libs (`python3-requests` on Debian)
are an OS carve-out of *the same project* — they still need hashes
if you install them with pip; apt has its own hashes (OS pack).

### 4.1 Stdlib first

Before adding a PyPI project, name the stdlib module you are
rejecting and why. Examples this map actually uses:

| Job | Stdlib first | Third-party only after the bar |
|-----|--------------|--------------------------------|
| HTTP client | `urllib.request` | `httpx` / `requests` |
| JSON | `json` | orjson / ujson (perf) |
| TOML read | `tomllib` | tomli on <3.11 only |
| CLI argv | `argparse` | click / typer |
| Tests | `unittest` | pytest |
| Templating | none great | jinja2 (bar) |
| TLS | `ssl` | never roll your own |

"The third-party API is nicer" is **not** enough by itself. "The
stdlib cannot do X safely" is.

### 4.2 Admission checklist (every new direct dep)

Record the answers in the PR (not in this pack). All must hold:

1. **Name** — exact PyPI normalized name. Check for typosquats
   (`reqeusts`, `colourama`, `python-dateutil` lookalikes).
2. **Purpose** — one sentence. No "might need later."
3. **Stdlib gap** — §4.1.
4. **Maintained** — a release or security commit in a reasonable
   window; not a single 0.0.1 upload.
5. **License** — SPDX you can ship (OS archive may be stricter).
6. **Advisories** — `pip-audit` clean for that pin, including
   transitives after the lock update.
7. **Provenance extra** — prefer projects that publish with
   **Trusted Publishing** and/or **attestations**. Not a PEP
   requirement; this bar's extra. Lack of attestations is not an
   automatic reject; a brand-new anonymous upload is.
8. **Native code** — wheels from the *same* project; a random
   source tree that compiles C at install time is a build-script
   supply-chain surface (see [rust ecosystem](../rust/rust-ecosystem-policy.md)
   2026 crates.io incident analog). Prefer sdists you don't need, or review
   `setup.py`/`build.rs`-equivalents.
9. **Transitives** — you own them. A tiny direct dep that pulls
   forty packages fails the bar unless you accept each.

Do **not** add a dep to "keep options open." Features lose.

### 4.3 What this bar is not

- Not a frozen list of `numpy`, `django`, `flask`. Those can pass
  the bar in a product; they are not blessed here.
- Not "stars on GitHub."
- Not "it is on conda-forge" (that is another ecosystem).
- Not PyPI's malware scan as your only control.

If a dep fails later (`pip-audit` red, abandoned, yanked for
malware): pin a fixed release, or **remove the feature**. Do not
`--ignore-vuln` without an expiry and a ticket.

------------------------------------------------------------------------
5. ADVISORIES
------------------------------------------------------------------------

https://github.com/pypa/pip-audit

```text
python -m pip_audit --require-hashes -r requirements.txt
```

(or `pip-audit` on the venv / uv lock). Fail CI on known
vulnerabilities. This is the RustSec analog. PyPA maintains it.

OSV and GitHub Advisory import the same data. Dependabot extra.

Yank on PyPI does not remove already-locked hashes. Update the lock
and ship. OS package removal is the OS pack.

------------------------------------------------------------------------
6. PYPI STORE
------------------------------------------------------------------------

https://docs.pypi.org/
https://pypi.org/policy/terms-of-use/

PyPI is not pip and not Debian. These bullets apply when you
**upload** or **download**.

Download: default index **https://pypi.org/simple**. Extra indexes
(`--extra-index-url`) enable dependency confusion. **Denied** unless
the index is named in the lock, uses hashes, and is under your
control (private company index). Then document it.

Upload: Trusted Publishing (OIDC from GitHub/GitLab) over long-lived
tokens.
https://docs.pypi.org/trusted-publishers/

Attestations extra:
https://docs.pypi.org/attestations/

Yank is not deletion. Malware reports go to PyPI security, not this
pack's inbox.

Project names are first-come. Do not typosquat. Do not import PyPI
names into Debian binary names.

------------------------------------------------------------------------
7. INSTALL TOOLS (OFFICIAL VS EXTRA)
------------------------------------------------------------------------

| Tool | Status | Notes |
|------|--------|--------|
| `python -m pip` | official PyPA | Hash-checking mode |
| `python -m venv` | stdlib / Language+OS | Always; never `--break-system-packages` |
| uv | extra | Fine if lock is hashed and auditable |
| Poetry | extra | Same |
| pip-tools | extra | Classic hashed requirements.txt |
| conda | **not this pack** | Different ecosystem; do not mix into a pip lock |

`ensurepip` / `get-pip.py` on distro Python may be the wrong
path — OS PEP 668.

------------------------------------------------------------------------
8. LICENSE
------------------------------------------------------------------------

SPDX in `[project]`. OS archives add `debian/copyright` etc. Must
not contradict. GPL vs Apache on a transitive dep is your problem
at admission time (§4).

------------------------------------------------------------------------
9. QUALITY CHECKS (THE PROJECT)
------------------------------------------------------------------------

Every PR:

```text
python -m pip install --require-hashes -r requirements.txt
python -m pip_audit --require-hashes -r requirements.txt
python -m unittest discover
```

Must-haves

- `pyproject.toml` with `requires-python` and SPDX
- Hash-pinned lock committed (apps) or for CI extras (libs)
- Every direct dep has a recorded trust-bar admission
- `pip-audit` clean
- No extra-index-url unless documented
- Build backend pinned

Common stalls

- `pip install -U foo` in README as the install story
- Unpinned `dependencies = ["requests"]` with no lock
- `--ignore-vuln` without expiry
- `subprocess` to `pip install` at runtime

Not this pack: ruff as a *PEP*; dh-python; MSVC.

------------------------------------------------------------------------
10. COMPOSING
------------------------------------------------------------------------

Hosted app:

  Language + this pack + OS (shared + one carve-out)

Debian `.deb` of the same app: OS Debian may install
`python3-foo` from apt **instead of** pip. That replaces the lock
for *those* packages with apt's hashes. Do not then pip-install the
same name over the distro copy. Mixing is an OS integrity fail.

------------------------------------------------------------------------
11. QUICK OFFICIAL LINK LIST
------------------------------------------------------------------------

https://packaging.python.org/en/latest/
https://pip.pypa.io/en/stable/topics/secure-installs/
https://peps.python.org/pep-0621/
https://peps.python.org/pep-0668/
https://peps.python.org/pep-0751/
https://docs.pypi.org/trusted-publishers/
https://docs.pypi.org/attestations/
https://github.com/pypa/pip-audit

Sister packs
./python-language-policy.md
./python-os-policy.md
./README.md

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.0.0 | Initial ecosystem pack: hash pins, pip-audit, trusted-library admission bar, stdlib-first, extra indexes denied |
