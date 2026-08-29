---
title: "Python OS Policy"
description: Curated map of how Python lives on Debian, Arch, macOS, and Windows — interpreters, venv, PEP 668, ship formats. Not Ruff and not PyPI.
version: "1.0.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - README.md
  - python-language-policy.md
  - python-ecosystem-policy.md
last_updated: "2026-08-29"
---

# Python OS Policy

Reference pack for **how a hosted Python project lives on an
operating system**: which interpreter you run, venv vs distro
site-packages, and how each OS ships the result.

**Role:** curated map (working memory). **Not** PEP 8 —
[python-language-policy.md](python-language-policy.md).
**Not** the trust bar or `pip-audit` —
[python-ecosystem-policy.md](python-ecosystem-policy.md).

Last verified against PEP 668 and OS installer docs as of
2026-08-29.

Shared half plus four carve-outs. Apply **one** carve-out per ship
format. Do not import apt into pacman, Homebrew into Debian, or
the python.org Windows installer into Linux.

------------------------------------------------------------------------
0. LAYERING
------------------------------------------------------------------------

This pack owns:

- How CPython is **installed**
- `venv` / PEP 668 externally-managed environments
- Distro `python3-*` packages vs pip
- Ship-format placement
- OS security updates of *the interpreter* and of distro-packaged
  Python libraries

This pack does **not** own:

- `requires-python` dialect → Language
- Hash pins, PyPI, trust bar → Ecosystem
- Ruff → Language extra

Hard rules:

1. Never `pip install` into a distro-managed interpreter.
   Use a venv, or the OS package manager. PEP 668.
2. Distro Python may lag 3.14. That is **this pack**, not a silent
   Language freeze.
3. One payload OS per artifact.
4. Do not import Debian NEW into pacman, Homebrew, or MSI.
5. OS packages of Python libraries (`python3-cryptography`) get OS
   hashes (apt/pacman). Do not overlay pip on top of them.
6. `ruff` is never an OS packaging check.

------------------------------------------------------------------------
1. FOUNDATIONAL DOCUMENTS (SHARED)
------------------------------------------------------------------------

PEP 668 — Externally Managed Environments
https://peps.python.org/pep-0668/

`venv`
https://docs.python.org/3/library/venv.html

python.org downloads (upstream binaries; Sigstore, not PGP, since
3.14 — PEP 761)
https://www.python.org/downloads/
https://peps.python.org/pep-0761/

Version status
https://devguide.python.org/versions/

------------------------------------------------------------------------
2. INTERPRETER AND VENV (SHARED)
------------------------------------------------------------------------

Development and CI: a **venv** (or uv venv extra) on a known
CPython. `python -m venv .venv` then install the Ecosystem lock
with `--require-hashes`.

The OS may provide `python3`. That binary's site-packages is
**externally managed** on Debian/Fedora-style distros (PEP 668
`EXTERNALLY-MANAGED`). `pip install` there should fail. Do not
`--break-system-packages`.

Free-threaded `python3.14t` is a supported build (PEP 779), not
the default `python3`.

Record `python -VV` in CI.

------------------------------------------------------------------------
DEBIAN CARVE-OUT — section 3
------------------------------------------------------------------------

https://wiki.debian.org/Python
https://www.debian.org/doc/packaging-manuals/python-policy/
dh-python:
https://manpages.debian.org/unstable/dh-python/dh-python.1.en.html

- `python3` from apt. Version follows the suite (Trixie lags
  3.14). A `.deb` that must build on Trixie sets `requires-python`
  to what that `python3` is, or uses a documented backport.
- `python3-venv`, `python3-pip` — pip into a **venv**, not `/usr`.
- App as `.deb`: `dh-python`, depend on `python3` and
  `python3-foo` **Debian packages** when they exist. That is the
  OS hash story. Missing from the archive: vendor with hashes in
  the source package (no-network `debian/rules`) — Ecosystem lock
  plus this no-network rule.
- `python3-cryptography` etc. receive DSAs. A venv copy of the
  same project does **not**.

Do not `pip install` as root. Do not run Ruff from `debian/rules`
as Policy.

------------------------------------------------------------------------
ARCH CARVE-OUT — section 4
------------------------------------------------------------------------

https://wiki.archlinux.org/title/Python
https://wiki.archlinux.org/title/Python_package_guidelines

- `extra/python` tracks upstream closely (often current 3.14).
- `python-pip`, venv module in stdlib.
- pacman `python-foo` vs pip: pick one per package name. Mixing
  in `/usr` is the failure PEP 668 exists to prevent.
- PKGBUILD: `depends=(python python-bar)`, wheels in
  `prepare`/`build` with hashes; namcap is not pip-audit.

Do not import `dh-python`. AUR is not official Arch.

------------------------------------------------------------------------
MACOS CARVE-OUT — section 5
------------------------------------------------------------------------

https://www.python.org/downloads/macos/

- Ship host: Apple Silicon. python.org installer or Homebrew
  `python@3.14`. Apple `/usr/bin/python3` is Xcode's and **lags**;
  do not target it for new apps.
- venv from the interpreter you mean (`/Library/Frameworks/...` or
  Homebrew).
- Framework builds vs unix layout: document which.
- Signing/notarization extra for a bundled `.app` (py2app/briefcase
  extra — those bundlers still pass the Ecosystem trust bar).

Do not install wheels into `/usr`. Do not import MSVC.

------------------------------------------------------------------------
WINDOWS CARVE-OUT — section 6
------------------------------------------------------------------------

https://www.python.org/downloads/windows/
https://docs.python.org/3/using/windows.html
https://peps.python.org/pep-0773/

- **Python Install Manager** (PEP 773, `py install` / `py list`) is
  the current official tool. The traditional `.exe` installer and
  standalone `py.exe` launcher are **deprecated since 3.14** and
  scheduled to go away around 3.16.
- `python` launches the default runtime; `py -3.14` still selects a
  version under the install manager. Pin which you CI.
- venv: `py -3.14 -m venv .venv` (or `python -m venv` from that
  runtime).
- Native extensions: MSVC Build Tools if you build from sdist.
  Prefer hashed **wheels** (Ecosystem §4.2 native-code clause).
- Microsoft Store Python is restricted (file access, aliases). Do
  not use it as the ship interpreter. Turn off Store app-execution
  aliases that shadow `python.exe`.

Do not import apt. Do not assume `python3` is on PATH.

------------------------------------------------------------------------
7. QUALITY CHECKS (THIS OS)
------------------------------------------------------------------------

Shared:

```text
python -VV
python -m venv .venv
```

Debian: PEP 668 file present; chroot no-network; `python3-foo`
Depends instead of pip into `/usr`.

Arch: pacman XOR pip per name.

macOS: not `/usr/bin/python3` as the ship interpreter.

Windows: install manager / `python -VV`; wheels not forced sdist
compiles.

------------------------------------------------------------------------
8. WHAT THIS PACK EXPLICITLY IS NOT
------------------------------------------------------------------------

Not the trust bar. Not Ruff. Not conda. Not pyenv-as-required
(pyenv is a tool extra for installing *upstream* CPython; the
carve-out still says which binary you ship).

------------------------------------------------------------------------
9. COMPOSING
------------------------------------------------------------------------

App in a venv on any OS:

  Language + Ecosystem + this pack **shared** + host carve-out

Debian `.deb`:

  same + **Debian** (apt python3, dh-python; lock may collapse
  into `Depends: python3-foo`)

------------------------------------------------------------------------
10. QUICK OFFICIAL LINK LIST
------------------------------------------------------------------------

https://peps.python.org/pep-0668/
https://docs.python.org/3/library/venv.html
https://www.debian.org/doc/packaging-manuals/python-policy/
https://wiki.archlinux.org/title/Python
https://docs.python.org/3/using/windows.html
https://peps.python.org/pep-0773/
https://www.python.org/downloads/

Sister packs
./python-language-policy.md
./python-ecosystem-policy.md
./README.md

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.0.0 | Initial OS pack: PEP 668, venv; Debian, Arch, macOS, Windows carve-outs |
