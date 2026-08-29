---
title: "Rust development policy packs"
description: Modular language and ecosystem policy maps for Rust. Compose packs; do not merge them into one rulebook.
version: "1.0.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - rust-language-policy.md
  - rust-ecosystem-policy.md
  - sources.yaml
last_updated: "2026-08-29"
---

# Rust development policy packs

Curated maps of **what each layer actually checks**. Not tutorials. Not
product law for any one crate.

Two axes, two packs. Compose packs; do not merge them. Add more languages
later on the same axes (Go language, Python ecosystem, and so on) without
rewriting these files.

```text
                 LANGUAGE                            ECOSYSTEM
                 (what the code is)                  (how the crate lives)
Rust             rust-language-policy.md             rust-ecosystem-policy.md
```

**Role:** working memory for humans and agents. Cite official manuals;
do not treat this folder as a substitute for the Rust Reference, the
Cargo Book, or crates.io policy.

This is a **sibling** of linux-dev-policy, not a fifth Debian or GNOME
pack. Language is a third axis. A GNOME-shaped Rust `.deb` still
composes the linux-dev-policy packs for OS and UI, plus these two for
Rust.

Last verified against official rust-lang, Cargo, crates.io, and RustSec
documents as of 2026-08-29. Pins and the watch workflow are in
**Retrieving updates from official sources**.

------------------------------------------------------------------------
How to compose
------------------------------------------------------------------------

Pick the **language** pack whenever the program is written in Rust. Add
the **ecosystem** pack when the crate has a Cargo manifest, a lockfile,
or a registry identity. Optionally add linux-dev-policy packs when the
artifact is a `.deb` or a Flatpak.

| Deliverable | Language | Ecosystem | linux-dev-policy (if any) |
|-------------|----------|-----------|---------------------------|
| Hosted Rust library or binary, crates.io or git | Language | Ecosystem | — |
| Same crate, unpublished workspace member | Language | Ecosystem (manifest + lockfile; skip store) | — |
| Native `.deb` of a Rust CLI on Debian | Language | Ecosystem | Debian OS + Debian Application |
| Native `.deb` of a GNOME-shaped Rust GUI | Language | Ecosystem | Debian OS + Debian Application + GNOME Application + GNOME OS session |
| Flatpak of a GNOME-shaped Rust GUI | Language | Ecosystem | GNOME Application + GNOME OS (session + payload) |

Default for a GNOME-platform app that is written in Rust and ships first
as a Debian `.deb`:

  Rust Language + Rust Ecosystem
  + GNOME Application + Debian Application + Debian OS
  + GNOME OS *session* (portals, settings, Shell)

Do **not** apply GNOME OS *payload* rules (Flatpak `/app`, Flathub AI
store ban, GNOME runtime EOL) to that `.deb`. Do **not** apply crates.io
yank/publish rules to Debian NEW. Do **not** apply `cargo fmt` to
`debian/rules` as if it were Debian Policy.

First version of these packs covers **hosted libraries and binaries**.
FFI / C ABI and `no_std` / embedded are out of scope until a later pack
revision. Ferrocene and other qualified Rust specs are not this map.

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
| License | Both (API C-PERMISSIVE is a *recommendation*) | Ecosystem (`license` / SPDX) | crates.io vs Debian NEW vs Flathub |
| Crate name | Language (C-CASE / RFC 430) | Ecosystem (crates.io uniqueness) | Debian binary name / Flatpak id |
| Advisories | — | Ecosystem (RustSec) | Debian security tracker on a `.deb` |
| SemVer of a published API | Language (what broke) | Ecosystem (version bump) | crates.io |
| `build.rs` / proc macros | Language (code) | Ecosystem (supply chain) | RustSec / deny extra |
| HIG, widgets, app ID | GNOME Application | Payload OS | Circle / Flathub |
| `debian/control`, NEW, lintian | — | Debian Application | Debian NEW |
| FHS, usr-merge, apt | — | Debian OS | Debian NEW |
| Flatpak finish-args, runtime | — | GNOME OS payload | Flathub |

Hard rules:

1. One edition per package. Do not mix 2018 / 2021 / 2024 in one
   package without a documented workspace exception.
2. rustfmt defaults **are** the style guide. A custom `rustfmt.toml`
   that fights the defaults is a house fork, not rust-lang Policy.
3. `clippy::pedantic` and `clippy::restriction` are opt-in. Clippy
   warns if you enable the whole restriction group. Do not call them
   rustc defaults.
4. `forbid(unsafe_code)` is a **product bar**, not a language
   requirement. The language pack maps how unsafe must be written when
   it exists.
5. Do not import crates.io yank/publish into Debian NEW.
6. Do not import `cargo fmt` or Clippy into `debian/rules` as Policy.
7. Do not import Flathub's generative-AI store ban into `cargo publish`.
8. Debian's rustc in a suite may lag this pack's stable pin. That is a
   payload OS problem (`rust-version` / MSRV), not a reason to stay on
   an old edition forever.

------------------------------------------------------------------------
Official map vs audit extra
------------------------------------------------------------------------

Rust has **no Debian Policy equivalent**. rustc, rustfmt, Clippy, Cargo,
crates.io, and RustSec do not all enforce the same bar.

- **Official map** — what rust-lang, Cargo, crates.io, and the Rust
  Secure Code Working Group (RustSec) actually check or document as
  convention.
- **Audit extra** — widely used tools that are **not** rust-lang
  Policy: `cargo deny`, `cargo vet`, Miri, `cargo fuzz`,
  `cargo-auditable`, `cargo geiger`, `cargo semver-checks`.

Each extra is labeled in the packs. A later agent must not turn
`clippy::restriction` or `cargo deny` into a fake rustc error.

Same pattern as linux-dev-policy: Circle *app quality* vs Flathub
*store* vs Debian *Policy*.

------------------------------------------------------------------------
What each pack is
------------------------------------------------------------------------

[rust-language-policy.md](rust-language-policy.md)

What Rust requires of the *code*: edition, rustc lints, rustfmt,
Clippy groups, `cargo test` / doctest, API Guidelines, unsafe and
soundness (Nomicon, Unsafe Code Guidelines), rustdoc. Not crates.io,
not lockfiles, not Debian NEW.

[rust-ecosystem-policy.md](rust-ecosystem-policy.md)

What the crate needs in order to *live* in the Cargo world: manifest
identity, features, MSRV, lockfile, SemVer, crates.io store rules,
SPDX on the crate, publish/yank, RustSec / `cargo audit`. Audit extras
(`cargo deny`, `cargo vet`) live here, labeled.

------------------------------------------------------------------------
Adding another language
------------------------------------------------------------------------

Copy the axes, not the files.

1. Write `<lang>-language-policy.md` for compiler, formatter, tests,
   and language-level unsafety.
2. Write `<lang>-ecosystem-policy.md` for the package manager, registry,
   lockfile, and advisory database.
3. Desktop and OS packs stay in linux-dev-policy. A GTK app in Go is
   GNOME Application + Debian OS + (future) Go packs. Do not fold
   `gofmt` into Debian OS.
4. Update this README composition table. Do not silently overload an
   existing pack.

------------------------------------------------------------------------
Retrieving updates from official sources
------------------------------------------------------------------------

Packs are maps. Official manuals remain the authority.

[sources.yaml](sources.yaml) is the watch registry. Each entry records
a canonical URL, the owning pack, a pin, a detector, and whether the
source splits **language** vs **ecosystem**.

[scripts/check_sources.py](scripts/check_sources.py) prints `UNCHANGED`
or `DRIFT`. On drift, patch the owning pack with a bite-sized rule,
then bump the pin. Never auto-merge HTML into packs.

Cadence:

- rustc / Cargo / Clippy stable releases: about every six weeks
- crates.io policy and RustSec: continuous
- API Guidelines, Nomicon, UCG, Style Guide: slower (on material change)

Current pins as of 2026-08-29:

- rustc **1.98.0** (2026-08-20)
- Edition **2024** (stable since 1.85.0, 2025-02-20)
- Cargo resolver **3** is the edition-2024 default
- This pack's ship bar is **stable** rustc. Beta and nightly are not
  a release requirement.

`archive/` is reserved for a frozen snapshot of this 1.0.0 set after
the next version bump. Read the root files.

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.0.0 | Initial two-pack split: Rust Language, Rust Ecosystem. Official map plus labeled audit extras. Hosted libs and bins only. |
