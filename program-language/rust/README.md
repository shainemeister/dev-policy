---
title: "Rust development policy packs"
description: Modular language, ecosystem, and OS policy maps for Rust. Compose packs; do not merge them into one rulebook.
version: "1.1.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - rust-language-policy.md
  - rust-ecosystem-policy.md
  - rust-os-policy.md
  - sources.yaml
last_updated: "2026-08-29"
---

# Rust development policy packs

Curated maps of **what each layer actually checks**. Not tutorials. Not
product law for any one crate.

Three axes. Compose packs; do not merge them. Language and ecosystem
are **OS-agnostic**. OS tools and ship formats live in **carve-outs**
(Debian, Arch, macOS, Windows). Add more languages later on the same
axes without rewriting these files.

```text
                 LANGUAGE                         ECOSYSTEM                        OS
                 (what the code is)               (how the crate lives)            (how it lives on a system)
Rust             rust-language-policy.md          rust-ecosystem-policy.md         rust-os-policy.md
                                                                                   Debian | Arch | macOS | Windows
```

**Role:** working memory for humans and agents. Cite official manuals;
do not treat this folder as a substitute for the Rust Reference, the
Cargo Book, crates.io policy, or an OS packaging guide.

Last verified against official rust-lang, Cargo, crates.io, RustSec,
and OS installer docs as of 2026-08-29. Pins and the watch workflow
are in **Retrieving updates from official sources**.

The **1.0.0** snapshot (two packs, Debian-centric composition) is
frozen in [archive/](archive/). Read the root files.

------------------------------------------------------------------------
How to compose
------------------------------------------------------------------------

Always take **Language**. Add **Ecosystem** when there is a Cargo
manifest, lockfile, or registry identity. Add **OS (shared half)**
whenever a compiler must actually run. Add **exactly one OS
carve-out** per ship format.

| Deliverable | Language | Ecosystem | OS |
|-------------|----------|-----------|-----|
| Hosted crate on crates.io (any dev OS) | yes | yes | shared + developer host carve-out |
| Unpublished workspace member | yes | yes (skip store) | shared + developer host |
| Debian `.deb` | yes | yes | Debian |
| Arch `.pkg.tar.zst` | yes | yes | Arch |
| macOS binary / Homebrew formula | yes | yes | macOS |
| Windows `.exe` / MSI | yes | yes | Windows |

Do **not** apply the Debian carve-out to an MSI. Do **not** apply
MSVC to a `.deb`. Do **not** apply crates.io yank to apt, pacman,
brew, or WinGet. Do **not** apply `cargo fmt` to an OS packaging
script as if it were that OS's policy.

First version of the language/ecosystem packs covers **hosted
libraries and binaries**. FFI / `no_std` are out of scope until a
later revision. Android, iOS, WASM, musl-first images are not in the
OS pack yet.

------------------------------------------------------------------------
Conflict resolution
------------------------------------------------------------------------

When two packs mention the same object, split **contents** from
**placement** and **queue**.

| Object | Who owns contents | Who owns placement | Who owns the queue |
|--------|-------------------|--------------------|--------------------|
| Source text, types, `unsafe` | Language | — | CI / code review |
| rustfmt / Clippy / rustc lints | Language | CI config in the crate | CI |
| `Cargo.toml` identity, features, MSRV | — | Ecosystem | crates.io or the git host |
| `Cargo.lock` | — | Ecosystem | CI (`--locked`) |
| License | Language (C-PERMISSIVE is a *recommendation*) | Ecosystem (`license` / SPDX) | OS carve-out (apt / pacman / brew / MSI) and crates.io |
| Crate name | Language (C-CASE) | Ecosystem (crates.io uniqueness) | OS package name (carve-out) |
| Advisories | — | Ecosystem (RustSec / `cargo audit`) | OS tracker if any (e.g. rustsec.debian.net) |
| SemVer of a published API | Language (what broke) | Ecosystem (version bump) | crates.io |
| `build.rs` / proc macros | Language (code) | Ecosystem (supply chain) | RustSec / deny extra |
| rustc install, linker, SDK | — | OS (rustup vs distro package) | OS package manager |
| Distro rustc version lag | — | OS carve-out | OS suite / extra |
| Target triple | — | OS (tier table) | rustc CI |
| `/usr` vs Homebrew prefix vs Program Files | — | OS carve-out | OS packager |

Hard rules:

1. One edition per package. Do not mix 2018 / 2021 / 2024 in one
   package without a documented workspace exception.
2. rustfmt defaults **are** the style guide. A custom `rustfmt.toml`
   that fights the defaults is a house fork, not rust-lang Policy.
3. `clippy::pedantic` and `clippy::restriction` are opt-in. Do not
   call them rustc defaults.
4. `forbid(unsafe_code)` is a **product bar**, not a language
   requirement.
5. Language and ecosystem packs do **not** require apt, pacman,
   Homebrew, or MSVC.
6. rustup is rust-lang's installer on Debian, Arch, macOS, and
   Windows. Distro `rustc` packages are OS opinions.
7. Distro rustc lag is the OS pack. It is not a reason to freeze the
   language edition.
8. One payload OS per artifact. Do not import Debian NEW into
   pacman, Homebrew, or MSI. Do not import MSVC into Linux, or Xcode
   into Windows.
9. Do not import crates.io yank/publish into an OS package manager.

------------------------------------------------------------------------
Official map vs audit extra
------------------------------------------------------------------------

Rust has **no single OS Policy equivalent**. rustc, rustfmt, Clippy,
Cargo, crates.io, and RustSec do not all enforce the same bar, and
neither do apt, pacman, Homebrew, or MSVC.

- **Official map** — what rust-lang, Cargo, crates.io, the Rust
  Secure Code Working Group (RustSec), and each OS's *own* installer
  / packaging docs actually check.
- **Audit extra** — widely used tools that are **not** rust-lang
  Policy: `cargo deny`, `cargo vet`, Miri, `cargo fuzz`,
  `cargo-auditable`. OS extras (Apple notarization, namcap, MSI) are
  labeled in the OS pack.

Each extra is labeled. A later agent must not turn `clippy::restriction`
or `cargo deny` into a fake rustc error, or `cargo fmt` into apt
Policy.

------------------------------------------------------------------------
What each pack is
------------------------------------------------------------------------

[rust-language-policy.md](rust-language-policy.md)

What Rust requires of the *code*: edition, rustc lints, rustfmt,
Clippy groups, `cargo test` / doctest, API Guidelines, unsafe and
soundness. Not crates.io. Not apt/pacman/brew/MSVC.

[rust-ecosystem-policy.md](rust-ecosystem-policy.md)

What the crate needs in order to *live* in the Cargo world: manifest
identity, features, MSRV, lockfile, SemVer, crates.io, SPDX on the
crate, RustSec / `cargo audit`. Audit extras labeled.

[rust-os-policy.md](rust-os-policy.md)

How a compiler and a binary exist on a system. Shared: rustup, target
tiers. Carve-outs: Debian, Arch, macOS, Windows. Apply one carve-out
per ship format.

------------------------------------------------------------------------
Adding another language or OS
------------------------------------------------------------------------

Copy the axes, not the files. Do **not** create a sibling git repo.

1. A new language is a new directory under
   [program-language/](../) (for example `../go/`).
2. OS carve-outs for *this* toolchain stay in `rust-os-policy.md`.
3. Debian Policy, FHS, lintian, NEW, and the HIG live in
   [os/linux](../../os/linux/README.md) — cite them; do not copy.
4. To add Fedora or NixOS as a *language* carve-out, add a section to
   this OS pack. A full distro map is a new directory under `os/`.
5. Do not silently overload Debian's section with another distro.

------------------------------------------------------------------------
Retrieving updates from official sources
------------------------------------------------------------------------

Packs are maps. Official manuals remain the authority.

The **1.0.0** snapshot lives in [archive/](archive/) and must not be
edited.

[sources.yaml](sources.yaml) is the watch registry. Each entry records
a canonical URL, the owning pack, a pin, a detector, and whether the
source splits **language**, **ecosystem**, or **os**.

[../../scripts/check_sources.py](../../scripts/check_sources.py)
(`--family program-language/rust`) prints `UNCHANGED` or `DRIFT`. On
drift, patch the owning pack with a bite-sized rule, then bump the
pin. Never auto-merge HTML into packs.

Cadence:

- rustc / Cargo / Clippy stable releases: about every six weeks
- crates.io policy and RustSec: continuous
- rustup / platform-support / OS packaging pages: weekly
- API Guidelines, Nomicon, UCG, Style Guide: slower

Current pins as of 2026-08-29:

- rustc **1.98.0** (2026-08-20)
- Edition **2024** (stable since 1.85.0, 2025-02-20)
- Cargo resolver **3** is the edition-2024 default
- Ship bar is **stable** rustc
- macOS ship host: `aarch64-apple-darwin` (tier 1); Intel Mac is
  tier 2 with host tools (RFC 3841)

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.1.0 | OS pack with Debian, Arch, macOS, Windows carve-outs. Language and ecosystem made OS-agnostic. |
| 1.0.0 | Initial two-pack split: Rust Language, Rust Ecosystem. Official map plus labeled audit extras. Hosted libs and bins only. |

The 1.0.0 snapshot is frozen in [archive/](archive/). Root files were
sourced from that snapshot and then split. Read the root files, not
`archive/`, unless you are comparing versions.
