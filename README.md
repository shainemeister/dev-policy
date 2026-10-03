# Development policy packs

Curated maps of **what each layer actually checks**. Not tutorials. Not
product law for any one repository. **Not** [repo-kit](https://github.com/shainemeister/repo-kit)
(that kit is how a git repo is kept honest).

Two buckets. Compose packs; do not merge them into one rulebook.

```text
os/                         how an artifact lives on a system / store
  linux/                    Debian × GNOME (OS and application packs)
  macos/                    Direct distribution × Mac App Store

program-language/           what the code and its package world require
  rust/  python/  c/  node/ language × ecosystem × toolchain-on-OS
```

Official manuals remain the authority. These files are working memory
for humans and agents. Cite them; do not treat this tree as a substitute
for Debian Policy, the GNOME HIG, the macOS Human Interface Guidelines,
Apple's distribution docs, the Rust Reference, PEPs, or npm docs.

## Overview

| Bucket | Question | Family |
|--------|----------|--------|
| [os/linux](os/linux/README.md) | How this artifact is placed, packaged, and queued | Debian OS / Debian Application / GNOME OS / GNOME Application |
| [os/macos](os/macos/README.md) | How a Mac app is sealed, placed, and queued | Direct OS / Direct Application / App Store OS / App Store Application |
| [program-language/rust](program-language/rust/README.md) | What rustc, Cargo, and rustup check | Language / Ecosystem / OS carve-outs |
| [program-language/python](program-language/python/README.md) | What CPython, PyPA, and PEP 668 check | Language / Ecosystem / OS carve-outs |
| [program-language/c](program-language/c/README.md) | What ISO C/C++, compilers, and CMake check | Language / Ecosystem / OS carve-outs |
| [program-language/node](program-language/node/README.md) | What Node, npm, and the lockfile check | Language / Ecosystem / OS carve-outs |

Language `*-os-policy.md` files stay **under the language**. They own
toolchain install and distro lag (rustup vs apt rustc, PEP 668, MSVC).
They do **not** own Debian Policy, FHS, lintian, NEW, or the GNOME
HIG — those live in [os/linux](os/linux/README.md). They do **not**
own Developer ID, notarization, Gatekeeper, App Review, or the macOS
Human Interface Guidelines — those live in
[os/macos](os/macos/README.md).

Windows stays a carve-out inside each language OS pack until it has
its own manuals. The macOS carve-out still owns the toolchain (Xcode
Command Line Tools, rustup, Homebrew prefixes).

## How to compose

Pick **one payload OS** per ship format. Add language packs for the
language you ship. Add `os/linux` packs when the artifact is a `.deb`,
a Flatpak, or a GNOME-session app. Add `os/macos` packs when the
artifact is a Developer ID product, a signed Mac command-line tool,
or a Mac App Store app. Direct distribution is the primary map.

| Deliverable | Open |
|-------------|------|
| Hosted Rust crate (any dev OS) | [rust](program-language/rust/README.md) language + ecosystem; OS shared half + host carve-out |
| Hosted Python / Node library | matching `program-language/*` language + ecosystem; OS shared half + host carve-out |
| Hosted C/C++ library | [c](program-language/c/README.md) language (C half, C++ half, or both) + ecosystem; OS shared + host carve-out |
| Debian `.deb` of a Rust CLI | rust language + ecosystem + rust-os **Debian carve-out** + [Debian OS](os/linux/debian-os-policy.md) + [Debian Application](os/linux/debian-application-policy.md) |
| GNOME-shaped Rust `.deb` | previous + [GNOME Application](os/linux/gnome-application-policy.md) + [GNOME OS](os/linux/gnome-os-policy.md) **session only** (not Flatpak payload) |
| Flatpak / Flathub | [GNOME OS](os/linux/gnome-os-policy.md) payload + [GNOME Application](os/linux/gnome-application-policy.md) |
| Direct Mac app (Developer ID) | language packs + macOS toolchain carve-out + [Direct OS](os/macos/direct-os-policy.md) + [Direct Application](os/macos/direct-application-policy.md) |
| Signed Mac command-line tool (Gatekeeper must open it) | language packs + macOS toolchain carve-out + [Direct OS](os/macos/direct-os-policy.md) only |
| Mac App Store app | language packs + macOS toolchain carve-out + [App Store OS](os/macos/app-store-os-policy.md) + [App Store Application](os/macos/app-store-application-policy.md) + [Direct Application](os/macos/direct-application-policy.md) for the macOS HIG and bundle contents. Cite [Direct OS](os/macos/direct-os-policy.md) for Apple silicon, System Integrity Protection, directories, and TCC. App Store OS wins on certificate, mandatory sandbox, and store updates. Skip the notary queue. |
| PyPI package / `npm publish` | matching language + ecosystem (skip OS store queues) |

Hard rules:

1. One payload OS per artifact. Do not import Debian NEW into pacman,
   Homebrew, MSI, crates.io, PyPI, or npm.
2. Language-os carve-out ≠ the OS pack. rust-os cites `/usr` and
   dh-cargo; debian-os owns FHS and apt. The macOS carve-out owns
   Xcode Command Line Tools, rustup, and the Homebrew prefix. Direct
   Application owns the macOS Human Interface Guidelines and bundle
   contents.
3. Do not apply GNOME OS *payload* rules (Flatpak `/app`, Flathub AI
   store ban, GNOME runtime EOL) to a `.deb`.
4. Do not fold a second language into an existing `*-language-policy.md`.
   Add a directory under `program-language/` instead.
5. Do not fold a second distro into `os/linux`. Add a directory under
   `os/` instead.
6. One macOS payload per artifact. Do not import App Store review,
   sandbox-must, or store updates into Developer ID. Do not import
   notarization or a Developer ID certificate into the Mac App Store.
   A Homebrew formula stays in the language carve-out. A Homebrew
   cask only installs an app that was already built and signed. A
   cask is not a third payload beside Developer ID and the Mac App
   Store.

Family READMEs own the detailed composition tables and conflict-resolution
grids. Start there after you pick the rows above.

## Retrieving updates

[scripts/check_sources.py](scripts/check_sources.py) compares pins in each
family’s `sources.yaml`. On `DRIFT`, write a bite-sized rule in the owning
pack, then bump the pin. Never dump official HTML into packs.

```bash
python3 scripts/check_sources.py --offline
python3 scripts/check_sources.py --offline --family os/linux
python3 scripts/check_sources.py --offline --family os/macos
python3 scripts/check_sources.py --offline --family program-language/rust
```

Details: [scripts/README.md](scripts/README.md).

## Adding a family

Copy the axes, not the files.

- New OS family: `os/<id>/` with OS × application packs, one row per
  payload, and its own `sources.yaml`. `os/macos` is that shape
  (Direct distribution and the Mac App Store). A Linux distro uses
  the same shape. Do not fold it into `os/linux` or into a language
  carve-out.
- New language: `program-language/<id>/` with language × ecosystem × OS
  packs and its own `sources.yaml`.
- Do **not** create a new git repository for one family.

## Operator prompts

Session load path for **this** repository. Law for git hygiene stays in
repo-kit. This section is not a second RULES tree.

1. Open this README — buckets, composition table, checker.
2. Open only the family READMEs for surfaces in play.
3. Language OS packs for toolchain; `os/linux` for Debian/GNOME
   placement; `os/macos` for Developer ID or the Mac App Store.
4. `python3 scripts/check_sources.py --offline` before claiming a pin bump
   is complete.
