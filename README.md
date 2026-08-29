# Development policy packs

Curated maps of **what each layer actually checks**. Not tutorials. Not
product law for any one repository. **Not** [repo-kit](https://github.com/shainemeister/repo-kit)
(that kit is how a git repo is kept honest).

Two buckets. Compose packs; do not merge them into one rulebook.

```text
os/                         how an artifact lives on a system / store
  linux/                    Debian × GNOME (OS and application packs)

program-language/           what the code and its package world require
  rust/  python/  c/  node/ language × ecosystem × toolchain-on-OS
```

Official manuals remain the authority. These files are working memory
for humans and agents. Cite them; do not treat this tree as a substitute
for Debian Policy, the HIG, the Rust Reference, PEPs, or npm docs.

## Overview

| Bucket | Question | Family |
|--------|----------|--------|
| [os/linux](os/linux/README.md) | How this artifact is placed, packaged, and queued | Debian OS / Debian Application / GNOME OS / GNOME Application |
| [program-language/rust](program-language/rust/README.md) | What rustc, Cargo, and rustup check | Language / Ecosystem / OS carve-outs |
| [program-language/python](program-language/python/README.md) | What CPython, PyPA, and PEP 668 check | Language / Ecosystem / OS carve-outs |
| [program-language/c](program-language/c/README.md) | What ISO C/C++, compilers, and CMake check | Language / Ecosystem / OS carve-outs |
| [program-language/node](program-language/node/README.md) | What Node, npm, and the lockfile check | Language / Ecosystem / OS carve-outs |

Language `*-os-policy.md` files stay **under the language**. They own
toolchain install and distro lag (rustup vs apt rustc, PEP 668, MSVC).
They do **not** own Debian Policy, FHS, lintian, NEW, or the HIG — those
live in [os/linux](os/linux/README.md).

Do not create empty `os/macos` or `os/windows` until those have their
own manuals to map. macOS and Windows today are carve-outs inside each
language OS pack.

## How to compose

Pick **one payload OS** per ship format. Add language packs for the
language you ship. Add `os/linux` packs when the artifact is a `.deb`,
a Flatpak, or a GNOME-session app.

| Deliverable | Open |
|-------------|------|
| Hosted Rust crate (any dev OS) | [rust](program-language/rust/README.md) language + ecosystem; OS shared half + host carve-out |
| Hosted Python / Node library | matching `program-language/*` language + ecosystem; OS shared half + host carve-out |
| Hosted C/C++ library | [c](program-language/c/README.md) language (C half, C++ half, or both) + ecosystem; OS shared + host carve-out |
| Debian `.deb` of a Rust CLI | rust language + ecosystem + rust-os **Debian carve-out** + [Debian OS](os/linux/debian-os-policy.md) + [Debian Application](os/linux/debian-application-policy.md) |
| GNOME-shaped Rust `.deb` | previous + [GNOME Application](os/linux/gnome-application-policy.md) + [GNOME OS](os/linux/gnome-os-policy.md) **session only** (not Flatpak payload) |
| Flatpak / Flathub | [GNOME OS](os/linux/gnome-os-policy.md) payload + [GNOME Application](os/linux/gnome-application-policy.md) |
| PyPI package / `npm publish` | matching language + ecosystem (skip OS store queues) |

Hard rules:

1. One payload OS per artifact. Do not import Debian NEW into pacman,
   Homebrew, MSI, crates.io, PyPI, or npm.
2. Language-os carve-out ≠ `os/linux` Debian Policy. rust-os cites
   `/usr` and dh-cargo; debian-os owns FHS and apt.
3. Do not apply GNOME OS *payload* rules (Flatpak `/app`, Flathub AI
   store ban, GNOME runtime EOL) to a `.deb`.
4. Do not fold a second language into an existing `*-language-policy.md`.
   Add a directory under `program-language/` instead.
5. Do not fold a second distro into `os/linux`. Add a directory under
   `os/` instead.

Family READMEs own the detailed composition tables and conflict-resolution
grids. Start there after you pick the rows above.

## Retrieving updates

[scripts/check_sources.py](scripts/check_sources.py) compares pins in each
family’s `sources.yaml`. On `DRIFT`, write a bite-sized rule in the owning
pack, then bump the pin. Never dump official HTML into packs.

```bash
python3 scripts/check_sources.py --offline
python3 scripts/check_sources.py --offline --family os/linux
python3 scripts/check_sources.py --offline --family program-language/rust
```

Details: [scripts/README.md](scripts/README.md).

## Adding a family

Copy the axes, not the files.

- New distro: `os/<id>/` with OS × application packs and its own
  `sources.yaml`.
- New language: `program-language/<id>/` with language × ecosystem × OS
  packs and its own `sources.yaml`.
- Do **not** create a new git repository for one family.

## Operator prompts

Session load path for **this** repository. Law for git hygiene stays in
repo-kit. This section is not a second RULES tree.

1. Open this README — buckets, composition table, checker.
2. Open only the family READMEs for surfaces in play.
3. Language OS packs for toolchain; `os/linux` for Debian/GNOME placement.
4. `python3 scripts/check_sources.py --offline` before claiming a pin bump
   is complete.
