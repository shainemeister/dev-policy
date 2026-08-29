---
title: "Rust Language Policy"
description: Curated map of what Rust requires of the code — edition, rustc, rustfmt, Clippy, tests, API Guidelines, unsafe. Not crates.io and not Debian packaging.
version: "1.0.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - README.md
  - rust-ecosystem-policy.md
last_updated: "2026-08-29"
---

# Rust Language Policy

Reference pack for **what the code is** when it is a hosted Rust
library or binary: edition, compiler lints, rustfmt, Clippy, tests,
API shape, documentation, and unsafe/soundness.

**Role:** curated map (working memory). **Not** L4 for any one crate.
**Not** crates.io, lockfiles, or `cargo publish` — that is
[rust-ecosystem-policy.md](rust-ecosystem-policy.md).
**Not** Debian Policy, HIG, or Flatpak.

Last verified against official rust-lang documents as of 2026-08-29.
rustc **1.98.0** (2026-08-20). Edition **2024** (stable since 1.85.0).

The compiler is "what must be true of the program."
The Style Guide / rustfmt is "how the text is laid out."
Clippy is "additional lints, grouped, not all deny-by-default."
API Guidelines are recommendations from the library team, not rustc
errors.
The Nomicon and Unsafe Code Guidelines are how unsafe must be thought
about when it exists.

------------------------------------------------------------------------
0. LAYERING
------------------------------------------------------------------------

This pack owns:

- rustc language rules and rustc lint groups
- Edition (2015 / 2018 / 2021 / 2024) and edition-migration lints
- rustfmt and the Rust Style Guide (default style)
- Clippy lint *groups* (what each group means; defaults vs opt-in)
- `cargo test`, doctests, and what those commands actually check
- API Guidelines (C-* checklist) as *convention*, not compiler law
- rustdoc contents (examples, Safety, panics)
- Unsafe Rust: when it is allowed, how it must be documented, which
  extra tools exist (Miri, fuzz)

This pack does **not** own:

- `Cargo.toml` identity, features, lockfile, MSRV field, crates.io
  → [rust-ecosystem-policy.md](rust-ecosystem-policy.md)
- RustSec advisories, `cargo audit`, `cargo deny`, `cargo vet`
  → Ecosystem pack (official vs extra)
- `debian/control`, lintian, NEW, `Static-Built-Using`
  → linux-dev-policy Debian Application
- HIG, GTK, application ID, Flatpak finish-args
  → linux-dev-policy GNOME packs

Compose a GNOME-shaped Rust `.deb` as:

  this pack + Rust Ecosystem
  + Debian OS + Debian Application + GNOME Application
  + GNOME OS session only

------------------------------------------------------------------------
1. FOUNDATIONAL DOCUMENTS
------------------------------------------------------------------------

The Rust Reference (language contract)
https://doc.rust-lang.org/reference/

The rustc Book (compiler, lints, codegen)
https://doc.rust-lang.org/rustc/
Lint groups:
https://doc.rust-lang.org/rustc/lints/groups.html

The Edition Guide
https://doc.rust-lang.org/edition-guide/
Rust 2024 (RFC 3501, rustc 1.85.0):
https://doc.rust-lang.org/edition-guide/rust-2024/

Rust Style Guide (default rustfmt style)
https://doc.rust-lang.org/style-guide/
Cargo.toml conventions:
https://doc.rust-lang.org/style-guide/cargo.html

Clippy
https://doc.rust-lang.org/clippy/
Lint groups:
https://doc.rust-lang.org/clippy/lints.html
Lint index:
https://rust-lang.github.io/rust-clippy/

The Rustonomicon (Unsafe Rust)
https://doc.rust-lang.org/nomicon/

Unsafe Code Guidelines
https://rust-lang.github.io/unsafe-code-guidelines/

Rust API Guidelines (library team; recommendations)
https://rust-lang.github.io/api-guidelines/
Checklist:
https://rust-lang.github.io/api-guidelines/checklist.html

Cargo commands used as *language* gates (the ecosystem pack owns the
manifest):

- `cargo test`
  https://doc.rust-lang.org/cargo/commands/cargo-test.html
- `cargo fmt`
  https://doc.rust-lang.org/cargo/commands/cargo-fmt.html
- `cargo clippy`
  https://doc.rust-lang.org/cargo/commands/cargo-clippy.html

Releases (toolchain pin, not a crate SemVer rule)
https://blog.rust-lang.org/releases/latest
https://doc.rust-lang.org/releases.html
https://blog.rust-lang.org/2026/08/20/Rust-1.98.0/

The Book and rustlings teach the language. Mentors and CI decide
whether a PR lands. This pack is the map of gates, not a tutorial.

------------------------------------------------------------------------
2. TOOLCHAIN AND EDITION
------------------------------------------------------------------------

Ship bar for this pack: **stable** rustc. Pin as of 2026-08-29:
**1.98.0** (2026-08-20). Beta and nightly are development channels, not
a release requirement.

https://blog.rust-lang.org/2026/08/20/Rust-1.98.0/

Install and update via rustup. A crate that needs a specific compiler
records it as `package.rust-version` (MSRV) — that *field* is
Ecosystem. This pack owns the language consequences of that pin
(which lints and edition features exist).

https://doc.rust-lang.org/cargo/reference/rust-version.html

Editions
https://doc.rust-lang.org/edition-guide/

- Editions are opt-in compatibility epochs. They are not a new
  language.
- `cargo new` on current stable writes `edition = "2024"`.
- One edition per package. Workspace members may differ; do not mix
  editions inside one package.
- Migrating: `cargo fix --edition`, then bump `edition`. Run the
  matching `rust-20xx-compatibility` lint group first.

Rust 2024 (stable 1.85.0, 2025-02-20)
https://doc.rust-lang.org/edition-guide/rust-2024/
https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/

Material 2024 language changes this map cares about (not a dump of
the guide):

- RPIT lifetime capture is maximal by default; be explicit with
  `use<..>` when you capture less (that is a SemVer commitment —
  Ecosystem pack owns the version bump).
- `unsafe` on `extern` blocks; `unsafe_op_in_unsafe_fn` is part of
  the 2024 compatibility group.
- Never-type fallback flowing into unsafe is deny-by-default in the
  2024 compatibility group.

Edition-migration lint groups (rustc Book):

- `rust-2018-compatibility`, `rust-2021-compatibility`,
  `rust-2024-compatibility`

https://doc.rust-lang.org/rustc/lints/groups.html

Do not stay on 2018/2021 "because Debian's rustc is old" without
recording MSRV in the Ecosystem pack. Debian rustc lag is a payload
OS fact. The language of a new crate is 2024 unless MSRV forbids it.

`rust-toolchain.toml` pins the *developer* toolchain. CI should use
the same channel the MSRV and the docs claim. Nightly-only features
are not this pack's ship bar.

------------------------------------------------------------------------
3. STYLE (rustfmt AND THE STYLE GUIDE)
------------------------------------------------------------------------

https://doc.rust-lang.org/style-guide/

The Style Guide defines the **default** Rust style and recommends that
developers and tools follow it. rustfmt implements that default.

"Everything in this style guide … refers to the default style. This
should not be interpreted as forbidding developers from following a
non-default style."

What that means here:

- `cargo fmt --all -- --check` is the language consistency gate.
- rustfmt **defaults** are the official style. A `rustfmt.toml` that
  only sets `edition` (to match the crate) is fine.
- Changing `max_width`, `use_small_heuristics`, or similar is a
  **house fork**. Document it if you do it. Do not call it rust-lang
  Policy.
- If rustfmt and the Style Guide disagree, that is a bug in one of
  them — report it. Do not invent a third style in this pack.

https://doc.rust-lang.org/style-guide/cargo.html

Cargo.toml formatting (Style Guide, not Cargo Book law): `[package]`
first; `name` then `version`; blank line between sections, not inside
them. That is style. Required *keys* are Ecosystem (C-METADATA).

Do not run rustfmt as a Debian Policy substitute. lintian does not
speak rustfmt.

------------------------------------------------------------------------
4. COMPILER AND CLIPPY LINTS
------------------------------------------------------------------------

rustc lint groups
https://doc.rust-lang.org/rustc/lints/groups.html

Groups that actually bite on hosted crates:

- `warnings` — all warn-by-default lints. `-D warnings` makes them
  errors. That is a **CI extra**, not rustc's default.
- `deprecated-safe` / `deprecated-safe-2024`
- `future-incompatible`
- `nonstandard-style` (camel case types, snake_case, UPPER_CASE
  statics) — RFC 430 naming, overlapping API Guidelines C-CASE
- `unused`
- `rust-2024-compatibility` when migrating

`rustc -W help` lists what *your* compiler actually contains.

Clippy groups
https://doc.rust-lang.org/clippy/lints.html
https://github.com/rust-lang/rfcs/blob/master/text/2476-clippy-uno.md

| Group | Default | Meaning |
|-------|---------|---------|
| `clippy::correctness` | **deny** | Outright wrong or useless. Do not `allow` the group. |
| `clippy::suspicious` | warn | Likely wrong; local `allow` needs a reason. |
| `clippy::complexity` | warn | Simpler form exists. |
| `clippy::perf` | warn | Optimizer-hostile pattern. |
| `clippy::style` | warn | Idiom. Opinionated; crate-level `allow` is allowed. |
| `clippy::pedantic` | allow | Power-user. False positives are expected. Cherry-pick. |
| `clippy::restriction` | allow | Forbids language features. **Do not enable the whole group** — Clippy warns if you `#![warn(clippy::restriction)]`. Cherry-pick. |
| `clippy::cargo` | allow | Manifest suggestions (Ecosystem-adjacent). |
| `clippy::nursery` | allow | Unfinished. Cherry-pick only. |

Configure in the manifest (Cargo applies this to the *current*
package, not to crates.io dependencies):

https://doc.rust-lang.org/cargo/reference/manifest.html#the-lints-section
https://doc.rust-lang.org/clippy/configuration.html

```toml
[lints.rust]
# product bar example — not a language requirement:
# unsafe_code = "forbid"

[lints.clippy]
# cherry-pick; do not dump restriction here
```

Workspace: `[workspace.lints]` plus `[lints] workspace = true`.

Clippy MSRV: set `msrv` in Clippy config or inherit from
`package.rust-version` so new-syntax lints do not fire below MSRV.

**CI extra (not rustc default):**

```text
cargo clippy --all-targets --all-features -- -D warnings
```

Cargo 1.97+ also has `build.warnings` in `.cargo/config.toml` for
local-package rustc warnings (`deny` / `warn` / `allow`). That is a
CI extra that does not bust the build cache the way flipping
`-D warnings` on the rustc command line used to.

https://doc.rust-lang.org/releases.html
https://doc.rust-lang.org/cargo/reference/config.html

`forbid(unsafe_code)` (`[lints.rust] unsafe_code = "forbid"`) is a
**product bar**. Enable it when the crate can be safe-only. Disable
it, locally, for a reviewed unsafe module — do not pretend Rust
forbids unsafe.

------------------------------------------------------------------------
5. TESTS
------------------------------------------------------------------------

https://doc.rust-lang.org/cargo/commands/cargo-test.html
https://doc.rust-lang.org/book/ch11-00-testing.html

What `cargo test` actually runs:

- `#[test]` unit tests (the crate with `cfg(test)`)
- Integration tests under `tests/`
- Doc-tests in rustdoc examples (unless `no_run` / `ignore`)
- Examples and benches only when selected

Language gate:

```text
cargo test --all-targets --all-features
```

`--all-targets` does **not** include doc-tests. Also run:

```text
cargo test --doc --all-features
```

when the crate ships rustdoc examples (API Guidelines C-EXAMPLE).

`cargo test` is **correctness of the tests you wrote**. It is not a
memory-safety proof, not RustSec, and not an audit. Unsafe code that
has no test still compiles.

Doctest style (API Guidelines C-QUESTION-MARK): examples use `?`,
not `unwrap`, in library docs. `unwrap` in a unit test that is
asserting a panic-free path is still normal.

**Audit extra (not `cargo test`):**

- Feature combinatorics: `cargo hack --feature-powerset` (or a
  documented subset) when features are not additive. Not rust-lang
  Policy.
- MSRV test job: Ecosystem (`rust-version`) plus this pack's
  language commands on that toolchain.

------------------------------------------------------------------------
6. UNSAFE AND SOUNDNESS
------------------------------------------------------------------------

https://doc.rust-lang.org/nomicon/meet-safe-and-unsafe.html
https://rust-lang.github.io/unsafe-code-guidelines/

Safe Rust is memory-safe. Unsafe Rust is the same language plus
operations the compiler will not check. Undefined behavior in unsafe
can break safety of the safe API around it.

This pack does **not** require `forbid(unsafe_code)`. Hosted crates
often need a small unsafe kernel (FFI is out of scope for v1; even
safe hosted code hits `unsafe` for performance or layout).

When `unsafe` exists, official docs require:

- An `unsafe fn` or `unsafe` block only as large as needed.
- A **Safety** section on every public unsafe function (API
  Guidelines C-FAILURE; rustdoc). Preconditions the caller must
  uphold.
- Invariants next to private unsafe: what the module assumes after
  the block. Reviewers read this; rustc does not.
- No undefined behavior. The Nomicon and UCG are the maps. rustc
  will not catch all of it.

Never-type fallback flowing into unsafe is a 2024 deny-by-default
compatibility lint — fix it, do not `allow` the group.

**Audit extra (labeled; not rustc):**

- **Miri** — interprets a test binary and flags many classes of UB.
  https://github.com/rust-lang/miri
  `cargo miri test` on tests that exercise unsafe. Nightly toolchain.
  Not a ship-channel requirement; it is the soundness extra.
- **cargo fuzz** — coverage-guided fuzzing of parsers and decoders.
  https://rust-fuzz.github.io/book/
- **cargo geiger** — counts unsafe usage. A *budget*, not a ban.
  Zero unsafe is a product bar, not a language rule.
- **clippy restriction cherry-picks** that bite on unsafe, if you
  opt in (for example `undocumented_unsafe_blocks`). Still extra.

Do not run Miri on Debian buildds as if it were Policy 4.9. It is
not.

------------------------------------------------------------------------
7. API AND RUSTDOC
------------------------------------------------------------------------

https://rust-lang.github.io/api-guidelines/
https://rust-lang.github.io/api-guidelines/checklist.html

The API Guidelines are **recommendations**. "These guidelines should
not in any way be considered a mandate that crate authors must
follow." Crates that follow them integrate better.

Map the checklist; do not paste it.

Naming (C-CASE, C-CONV, C-GETTER, C-ITER, C-FEATURE, C-WORD-ORDER)
overlaps rustc `nonstandard-style`. Feature names without placeholder
words (`foo`, `bar`, `dev`) are convention — Cargo will still accept
them.

Interoperability: implement the obvious traits (`Clone`, `Debug`,
`Send`/`Sync` when true). Error types that are just `String` fight
C-GOOD-ERR. Serde (C-SERDE) is a library-team *when it applies*
recommendation, not a compiler lint.

Documentation:

- C-CRATE-DOC — crate-level rustdoc with examples
- C-EXAMPLE — public items have rustdoc examples (strong for a
  library; a small binary's `main` is not a public API)
- C-FAILURE — errors, panics, Safety
- C-LINK — links in prose
- C-METADATA — manifest keys. **Owned by Ecosystem**; listed here
  because the checklist lives in this document family
- C-RELNOTES — changelog. Ecosystem publish process cites it
- C-HIDDEN — `#[doc(hidden)]` for glue, not for the real API

Predictability / type safety / future-proofing that actually reject
reviews:

- C-DEREF — only smart pointers implement `Deref`
- C-SEALED — seal traits you do not want downstream to implement
- C-STRUCT-PRIVATE — private fields so you can evolve (SemVer:
  Ecosystem)
- C-STABLE — public dependencies of a *stable* crate are stable
- C-PERMISSIVE — "permissive license" is a library-team taste.
  crates.io accepts GPL. Debian `main` wants DFSG. Do **not** treat
  C-PERMISSIVE as a store rule.

rustdoc is part of the language surface. `cargo test --doc` is how
examples stay true.

------------------------------------------------------------------------
8. QUALITY CHECKS (THE RUNNING CODE)
------------------------------------------------------------------------

Official language gates (every PR):

```text
cargo fmt --all -- --check
cargo test --all-targets --all-features
cargo test --doc --all-features
```

Clippy at default groups (correctness is already deny):

```text
cargo clippy --all-targets --all-features
```

**CI extra** (high-assurance bar this pack recommends for hosted
crates that claim auditability; not rustc default):

```text
cargo clippy --all-targets --all-features -- -D warnings
```

Optional Cargo config extra (1.97+): `build.warnings = "deny"` for
local rustc warnings.

Unsafe extra, when the crate has unsafe or parses untrusted input:

```text
cargo miri test
cargo fuzz run <target>
```

Must-haves (language)

- Compiles on the claimed stable / MSRV toolchain
- rustfmt check clean (defaults, or a documented house `rustfmt.toml`)
- `clippy::correctness` clean (default deny)
- Tests exist for the behavior you claim; `cargo test` passes
- Public unsafe has Safety docs
- rustdoc examples that you ship actually run (`cargo test --doc`)

Strong expectations

- `-D warnings` in CI (extra)
- C-CASE / `nonstandard-style` clean
- C-DEBUG on public types
- Private fields on public structs you intend to evolve

Common language rejects / stalls

- Unformatted diffs (`cargo fmt --check` fails)
- `allow(clippy::correctness)` at crate level
- Enabling all of `clippy::restriction`
- Public unsafe with no Safety section
- Doc-tests that `unwrap` as the documented happy path
- Nightly-only features on a crate that claims stable
- Custom rustfmt width presented as "the Rust style"

Not this pack (send elsewhere):

- Yank, crates.io name squat, missing `license` key → Ecosystem
- `RUSTSEC-*` in the tree → Ecosystem (audit)
- lintian, FHS, NEW → Debian Application / Debian OS
- HIG, Adwaita, application ID → GNOME Application
- Flathub finish-args → GNOME OS payload

------------------------------------------------------------------------
9. WHAT THIS PACK EXPLICITLY IS NOT
------------------------------------------------------------------------

Not the Cargo Book's store and lockfile rules.

Not a dump of the Reference or the Nomicon.

Not FFI / `extern "C"` / bindgen. Hosted libs and bins only for
1.0.0.

Not `no_std`, `panic = abort`, or linker scripts.

Not Ferrocene or any qualified-compiler safety case.

Not `cargo deny`, `cargo vet`, or RustSec — Ecosystem.

Not Debian rustc packaging (`dh-cargo`, crate packages vs a single
binary with vendored crates). linux-dev-policy Debian Application
already owns `Static-Built-Using`.

------------------------------------------------------------------------
10. COMPOSING WITH OTHER PACKS
------------------------------------------------------------------------

Rust library or CLI, crates.io only:

  this pack + [rust-ecosystem-policy.md](rust-ecosystem-policy.md)

GNOME-shaped `.deb` written in Rust:

  this pack + Rust Ecosystem
  + Debian OS + Debian Application + GNOME Application
  + GNOME OS session

Same source text. This pack formats, lints, and tests it. Ecosystem
publishes the crate. Debian Application wraps a `.deb`. GNOME
Application fills `.desktop` / metainfo *contents*.

Conflict rule: C-PERMISSIVE vs DFSG vs crates.io vs Flathub SPDX —
license *taste* here is a recommendation; license *file and SPDX*
are Ecosystem; DFSG is Debian OS; `debian/copyright` is Debian
Application.

------------------------------------------------------------------------
11. QUICK OFFICIAL LINK LIST
------------------------------------------------------------------------

Reference / rustc
https://doc.rust-lang.org/reference/
https://doc.rust-lang.org/rustc/
https://doc.rust-lang.org/rustc/lints/groups.html

Editions
https://doc.rust-lang.org/edition-guide/
https://doc.rust-lang.org/edition-guide/rust-2024/

Style / rustfmt
https://doc.rust-lang.org/style-guide/
https://doc.rust-lang.org/cargo/commands/cargo-fmt.html

Clippy
https://doc.rust-lang.org/clippy/
https://doc.rust-lang.org/clippy/lints.html
https://rust-lang.github.io/rust-clippy/

Tests
https://doc.rust-lang.org/cargo/commands/cargo-test.html

Unsafe
https://doc.rust-lang.org/nomicon/
https://rust-lang.github.io/unsafe-code-guidelines/
https://github.com/rust-lang/miri

API Guidelines
https://rust-lang.github.io/api-guidelines/
https://rust-lang.github.io/api-guidelines/checklist.html

Releases
https://blog.rust-lang.org/releases/latest
https://doc.rust-lang.org/releases.html

Sister pack
./rust-ecosystem-policy.md
./README.md

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.0.0 | Initial language pack: edition 2024 / rustc 1.98, rustfmt defaults, Clippy groups, tests, unsafe extras labeled, API Guidelines as convention |
