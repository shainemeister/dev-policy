---
title: "Rust Ecosystem Policy"
description: Curated map of how a Rust crate lives — Cargo.toml, lockfile, SemVer, crates.io, RustSec. Not rustfmt and not Debian NEW.
version: "1.0.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - README.md
  - rust-language-policy.md
last_updated: "2026-08-29"
---

# Rust Ecosystem Policy

Reference pack for **how a hosted Rust crate lives**: the Cargo
manifest, lockfile, SemVer, crates.io, licenses on the crate, and the
advisory database.

**Role:** curated map (working memory). **Not** L4 for any one crate.
**Not** rustfmt, Clippy groups, or the Nomicon — that is
[rust-language-policy.md](rust-language-policy.md).
**Not** Debian NEW, FHS, or Flathub.

Last verified against official Cargo, crates.io, and RustSec documents
as of 2026-08-29. rustc **1.98.0**. Edition **2024** (resolver **3**
default).

Cargo is "how the package is described and built."
crates.io is the store.
RustSec is the advisory database the Secure Code Working Group
maintains.
`cargo deny` and `cargo vet` are **audit extras**, not rust-lang
Policy.

------------------------------------------------------------------------
0. LAYERING
------------------------------------------------------------------------

This pack owns:

- `Cargo.toml` / workspace identity (name, version, license, edition
  *field*, `rust-version`, features, metadata)
- `Cargo.lock` policy and `--locked` / `--frozen`
- Dependency sources (crates.io, git+rev, path, vendor)
- SemVer as Cargo uses it
- crates.io usage, publish, yank, ownership
- SPDX / `license` on the crate
- RustSec and `cargo audit`
- Labeled extras: `cargo deny`, `cargo vet`, `cargo-auditable`, SBOM

This pack does **not** own:

- rustc language rules, rustfmt, Clippy groups, tests, unsafe writing
  → [rust-language-policy.md](rust-language-policy.md)
- What a public function's Safety section must say
  → Language pack
- `debian/copyright`, `Static-Built-Using`, dh-cargo, NEW
  → linux-dev-policy Debian Application
- Debian security tracker / `rustsec.debian.net` as *OS* mapping
  → linux-dev-policy Debian OS (cite from here; do not copy)
- Flathub inclusion, Flatpak manifest
  → linux-dev-policy GNOME OS payload

------------------------------------------------------------------------
1. FOUNDATIONAL DOCUMENTS
------------------------------------------------------------------------

The Cargo Book
https://doc.rust-lang.org/cargo/
Manifest:
https://doc.rust-lang.org/cargo/reference/manifest.html
`rust-version`:
https://doc.rust-lang.org/cargo/reference/rust-version.html
Lockfile vs manifest:
https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html
Why lockfiles in VCS:
https://doc.rust-lang.org/cargo/faq.html#why-have-cargolock-in-version-control
Resolver / SemVer:
https://doc.rust-lang.org/cargo/reference/resolver.html
https://doc.rust-lang.org/cargo/reference/semver.html
Publish:
https://doc.rust-lang.org/cargo/reference/publishing.html
Source replacement / vendor:
https://doc.rust-lang.org/cargo/reference/source-replacement.html
Build scripts:
https://doc.rust-lang.org/cargo/reference/build-scripts.html
CI:
https://doc.rust-lang.org/cargo/guide/continuous-integration.html

crates.io
https://crates.io/policies
(the live HTML 404s some bots; source:
https://github.com/rust-lang/crates.io/blob/main/svelte/src/routes/policies/+page.svelte)
Package ownership (first-come, first-served names):
https://crates.io/policies

Rust Code of Conduct (crates.io incorporates it)
https://www.rust-lang.org/policies/code-of-conduct

RustSec Advisory Database (Secure Code Working Group)
https://rustsec.org/
https://github.com/rustsec/advisory-db
`cargo audit`:
https://github.com/rustsec/rustsec/blob/main/cargo-audit/README.md

Debian's importer of RustSec (OS compose, not this pack's gate):
https://rustsec.debian.net

API Guidelines C-METADATA / C-RELNOTES / C-PERMISSIVE / C-STABLE
live in the language-pack checklist but the *keys* are this pack.

Audit extras (not rust-lang Policy):

- cargo-deny
  https://embarkstudios.github.io/cargo-deny/
- cargo-vet
  https://mozilla.github.io/cargo-vet/
- cargo-auditable
  https://github.com/rust-secure-code/cargo-auditable
- cargo-semver-checks
  https://github.com/obi1kenobi/cargo-semver-checks

------------------------------------------------------------------------
2. CRATE IDENTITY AND THE MANIFEST
------------------------------------------------------------------------

https://doc.rust-lang.org/cargo/reference/manifest.html

A package is what `[package]` describes. The crate name on crates.io
is `package.name`. It is **not** the Debian binary name and **not** a
GNOME application ID.

Must-haves for a crate you intend to publish (Cargo + C-METADATA):

- `name`, `version`
- `edition` (this pack stores the field; Language pack owns the
  language meaning). New crates: `"2024"`.
- `description`
- `license` (SPDX expression) or `license-file`
- `repository`
- `rust-version` (MSRV; optional in Cargo, expected here)

Should:

- `readme`
- `keywords`, `categories` (crates.io discoverability)
- `documentation` only if docs are not on docs.rs
- `homepage` only if it is a distinct site (do not duplicate
  `repository`)
- `authors` is **deprecated** in the Cargo Book. Optional; do not
  treat a missing authors list as a publish blocker

`package.publish = false` (or a restricted registry list) for crates
that must not hit crates.io (workspace glue, examples).

Features
https://doc.rust-lang.org/cargo/reference/features.html

- Additive. Do not use a feature to *remove* API.
- `default` should be the reasonable hosted set, not "everything
  including experimental".
- C-FEATURE: no placeholder names.
- Resolver 2/3 unifies features across the tree. Edition 2024
  defaults to resolver **3** (requires rustc 1.84+).

https://doc.rust-lang.org/cargo/reference/resolver.html

Workspaces: `[workspace.package]`, `[workspace.dependencies]`,
`[workspace.lints]`. Members share the lockfile of the workspace
root.

Binary names: Cargo's `non_kebab_case_bins` style lint (warn). A
binary that must match an OS command name documents the exception
(Debian PATH uniqueness is linux-dev-policy Debian OS).

------------------------------------------------------------------------
3. MSRV (`rust-version`)
------------------------------------------------------------------------

https://doc.rust-lang.org/cargo/reference/rust-version.html

`rust-version` is a bare version (`"1.85"`). Cargo errors on an older
toolchain unless `--ignore-rust-version`. `cargo add` uses it when
picking dependency versions. Clippy can honor it (`incompatible_msrv`).

This pack's default for a **new** hosted crate: MSRV is a **stable**
compiler you actually CI, often "current stable minus a small
window", not "latest only" and not "Debian oldstable rustc" unless
you ship as a `.deb` that must build there.

Debian suite rustc is a **payload** constraint. If you need to build
as a Debian package on Trixie, either:

- set `rust-version` to what Debian ships and keep the language
  pack's edition compatible, or
- vendor / use a newer toolchain in a way Debian Application allows
  (that procedure is not this pack).

Do not silently require nightly in `rust-version`. Nightly is not an
MSRV.

------------------------------------------------------------------------
4. LOCKFILE AND DEPENDENCIES
------------------------------------------------------------------------

https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html
https://doc.rust-lang.org/cargo/faq.html#why-have-cargolock-in-version-control

`Cargo.toml` is the range you wrote. `Cargo.lock` is the exact graph
Cargo last resolved. Do not edit the lockfile by hand.

Cargo's own FAQ: `cargo new` **defaults to tracking** `Cargo.lock`.
When in doubt, commit it. Deterministic builds, bisect, CI, MSRV
verification all want a lockfile.

`Cargo.lock` does **not** constrain your *dependents*. Their Cargo
resolves from your `Cargo.toml` ranges. `cargo install` without
`--locked` may pick newer transitive crates than you tested.

Language of this pack for hosted crates:

- **Binaries and anything you ship as an artifact:** commit
  `Cargo.lock`. Build and CI with `--locked`.
- **Libraries:** committing `Cargo.lock` is still Cargo's "when in
  doubt" advice and is required for `cargo audit` in CI of *this*
  repo. Dependents will not use your lockfile.

Git dependencies: pin `rev` (or a tag that you treat as immutable).
An unpinned git dep is the example the Cargo Book uses for
irreproducible builds.

https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html

crates.io **rejects** wildcard (`*`) version requirements
(since 2016). Write a real range.

https://doc.rust-lang.org/cargo/faq.html#can-libraries-use--as-a-version-for-their-dependencies

`cargo update` is how you refresh the lockfile. CI extra: a scheduled
job that *proposes* updates (Cargo Book: verifying latest
dependencies) without silently moving production off `--locked`.

Vendor / `--offline` / `--frozen`:
https://doc.rust-lang.org/cargo/reference/source-replacement.html

Debian builds are no-network on required targets (Debian
Application). Vendoring or a pre-fetched vendor dir is how a `.deb`
obeys that OS rule. Do not invent a second Debian Policy here.

Build scripts (`build.rs`) and proc macros run at compile time on
the developer/CI/buildd machine. They are a **supply-chain surface**.
The August 2026 crates.io incident (`arrayref` 0.3.10 and related
crates pulling a malicious `proc-macro1` build-time dropper) is why
this pack wants lockfiles, advisory checks, and no surprise
`build-dependencies`. RustSec is the official advisory path; `cargo
deny` sources/bans is extra.

------------------------------------------------------------------------
5. SEMVER
------------------------------------------------------------------------

https://doc.rust-lang.org/cargo/reference/semver.html
https://doc.rust-lang.org/cargo/reference/resolver.html#semver-compatibility

Cargo treats the leftmost non-zero component as the compatibility
line: `1.y.z` breaks on `x`; `0.y.z` breaks on `y`; `0.0.z` always
breaks.

The SemVer chapter is **guidelines**, not a compiler. It classifies
major / minor / possibly-breaking. Highlights that actually cause
ecosystem pain:

- Removing or renaming a public item is major
- Adding a public item is minor (glob imports are a known hazard)
- Adding a private field to an all-public struct is major (use
  `#[non_exhaustive]` or a constructor)
- Adding an enum variant without `non_exhaustive` is major
- Tightening generic bounds is major
- MSRV bump is **possibly-breaking**
- Adding a Cargo feature is minor; removing one is major

Language pack owns *what* in the source broke. This pack owns the
version number you publish.

**Audit extra:** `cargo semver-checks` against the last published
crate. Not rust-lang Policy; it is how you catch accidental majors.

C-STABLE: public dependencies of a stable (`1.x`) crate should
themselves be stable. A public `pub use` of a `0.x` type makes your
1.x API as unstable as that type.

------------------------------------------------------------------------
6. SUPPLY CHAIN — OFFICIAL (RustSec)
------------------------------------------------------------------------

https://rustsec.org/
https://github.com/rustsec/advisory-db

RustSec is the advisory database for crates.io packages, maintained
by the Rust Secure Code Working Group. Advisory kinds include
vulnerability, unsound, unmaintained, and notice.

`cargo audit` reads `Cargo.lock` and fails on known vulnerable crate
versions.

```text
cargo audit
```

That is the official ecosystem security gate. It is only as good as
the lockfile and the database. It does not review *your* unsafe. It
does not replace Miri.

OSV and GitHub Advisory Database import RustSec. Dependabot may open
PRs. Debian maps advisories onto `.deb`s at rustsec.debian.net —
compose with Debian OS; do not copy that tracker into this pack.

No standing crates.io rule says "you must run `cargo audit`." This
pack still treats it as the official tool the Working Group publishes
for the database they maintain. Hosted crates that claim auditability
run it in CI on the committed lockfile.

------------------------------------------------------------------------
7. SUPPLY CHAIN — AUDIT EXTRA (labeled)
------------------------------------------------------------------------

These tools are widely used. They are **not** rustc, not Cargo
Policy, and not crates.io admission.

**cargo-deny**
https://embarkstudios.github.io/cargo-deny/

```text
cargo deny check
```

Four checks: `advisories` (RustSec, overlapping `cargo audit`),
`licenses` (SPDX vs an allow list), `bans` (crate bans, duplicate
versions, wildcards), `sources` (unknown registries / git).

`sources` is the extra that would have constrained a surprise git or
typosquat registry fetch. `licenses` is how you enforce "we only take
MIT/Apache-2.0/…" *as a product bar*. C-PERMISSIVE is a
recommendation; this extra is how you machine-check it.

**cargo-vet**
https://mozilla.github.io/cargo-vet/

Human audits imported from trusted organizations. Built-in criteria
`safe-to-run` and `safe-to-deploy`. Does not prove absence of bugs.
Does record that someone accepted the crate contents.

Git and path deps are first-party unless you set `audit-as-crates-io`.

**cargo-auditable**
https://github.com/rust-secure-code/cargo-auditable

Embeds the dependency tree in the binary so `cargo audit` can run
against production artifacts, not just the source lockfile.

**SBOM extra:** CycloneDX / SPDX from the lockfile. Useful when a
Debian or enterprise queue asks; not crates.io Policy.

Do not copy Flathub's "no AI-assisted code" store ban into these
extras. crates.io has no such rule. Debian's 2026 GR (responsible
use, human remains accountable) is Debian Application if you ship a
`.deb`.

------------------------------------------------------------------------
8. crates.io STORE
------------------------------------------------------------------------

https://crates.io/policies
https://doc.rust-lang.org/cargo/reference/publishing.html

crates.io is not rustc and not Debian. These bullets apply when you
`cargo publish` to that registry.

Usage policy (short map, not a dump): no CoC violations; no unlawful
or fraudulent content; no malware, phishing, or license-key
generators; no using the index as a generic file host (a package must
be cargo-compatible, not a raw JPEG); no automated abuse. Names are
**first-come, first-served**. Taking over a name starts with the
current owner.

A crate must be a Cargo package. `cargo publish` packages the files
Cargo includes (respect `.gitignore` and an exclude/include list).
Secrets in the package are a store and security incident.

Yank: yanked versions are not gone. They stay for builds that already
depend on them; new resolves should not pick them. Yank is not a
security recall by itself — file RustSec and yank.

Trusted publishing (crates.io / GitHub Actions) is how official
rust-lang crates avoid long-lived tokens. Recommended extra for a
crate with CI; not a language rule.

Do **not** import:

- crates.io name uniqueness into Debian package names
- yank into `apt` removals
- Flathub quality banners into crate descriptions

Insufficient development history, malware, and typosquatting are
store/enforcement matters. This pack does not invent extra admission
criteria beyond the published policy.

------------------------------------------------------------------------
9. LICENSE ON THE CRATE
------------------------------------------------------------------------

`package.license` is an SPDX expression. crates.io displays it.
cargo-deny can allow-list it (extra).

C-PERMISSIVE (API Guidelines) prefers MIT / Apache-2.0 dual, which is
the rust-lang std convention. It is **not** a crates.io requirement.
GPL crates exist on the registry.

Compose:

| Gate | Who | What |
|------|-----|------|
| SPDX on the crate | this pack | `license` / `license-file` |
| C-PERMISSIVE | Language (recommendation) | dual MIT/Apache taste |
| DFSG `main` | Debian OS | archive law |
| `debian/copyright` | Debian Application | NEW |
| Flathub SPDX | GNOME OS payload | store |

Do not put GPL-incompatible extra crates in a product that claims
MIT-only via cargo-deny without noticing.

`license-file` for licenses that are not SPDX-named. Include the
texts Cargo should package.

------------------------------------------------------------------------
10. QUALITY CHECKS (THE CRATE)
------------------------------------------------------------------------

Official ecosystem gates (every PR, when a lockfile exists):

```text
cargo audit
cargo metadata --locked --format-version 1 >/dev/null
```

Publish dry-run before a crates.io release:

```text
cargo publish --dry-run --locked
```

**Audit extra** (release / high-assurance; not rust-lang Policy):

```text
cargo deny check
cargo vet
cargo semver-checks
```

Binaries you ship to users: build with `cargo-auditable` if you want
the extra of auditing the artifact.

Must-haves (ecosystem)

- Valid manifest; `edition` and (for new crates) `rust-version` set
- SPDX `license` or `license-file`
- `repository` URL that works
- `Cargo.lock` committed for bins; `--locked` in CI
- Git deps pin `rev`
- No `*` version reqs (crates.io will reject anyway)
- `cargo audit` clean, or documented exceptions with a tracking issue

Strong expectations

- `cargo deny check` in release CI (extra)
- Features additive; `cargo hack` extra if you have a matrix
- C-RELNOTES / changelog for published versions
- MSRV CI job

Common ecosystem rejects / stalls

- Unpinned git dependencies
- Secrets or huge generated blobs in the published crate
- Public 1.x API re-exporting a 0.x type (C-STABLE)
- Silent MSRV bump on a patch release without considering
  possibly-breaking
- Treating yank as deletion
- `cargo publish` of a crate whose `build.rs` pulls unreviewed code

Not this pack:

- rustfmt / Clippy / Miri → Language
- lintian, FHS, NEW → Debian packs
- HIG, app ID → GNOME Application
- Flathub AI / runtime EOL → GNOME OS payload

------------------------------------------------------------------------
11. COMPOSING WITH OTHER PACKS
------------------------------------------------------------------------

Hosted crate on crates.io:

  [rust-language-policy.md](rust-language-policy.md) + this pack

Same crate as a Debian `.deb`:

  both Rust packs
  + Debian OS + Debian Application
  Vendoring / `Static-Built-Using` / no-network builds are Debian
  Application. This pack still wants a lockfile and SPDX.

GNOME-shaped Rust GUI as Flatpak:

  both Rust packs + GNOME Application + GNOME OS (session + payload)
  crates.io may still host the library; Flathub hosts the app.
  Do not put Flathub finish-args in `Cargo.toml`.

------------------------------------------------------------------------
12. QUICK OFFICIAL LINK LIST
------------------------------------------------------------------------

Cargo
https://doc.rust-lang.org/cargo/
https://doc.rust-lang.org/cargo/reference/manifest.html
https://doc.rust-lang.org/cargo/reference/rust-version.html
https://doc.rust-lang.org/cargo/faq.html#why-have-cargolock-in-version-control
https://doc.rust-lang.org/cargo/reference/semver.html
https://doc.rust-lang.org/cargo/reference/publishing.html

crates.io
https://crates.io/policies

CoC
https://www.rust-lang.org/policies/code-of-conduct

RustSec
https://rustsec.org/
https://github.com/rustsec/advisory-db

Extras
https://embarkstudios.github.io/cargo-deny/
https://mozilla.github.io/cargo-vet/
https://github.com/rust-secure-code/cargo-auditable

Sister pack
./rust-language-policy.md
./README.md

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.0.0 | Initial ecosystem pack: manifest/MSRV/lockfile, SemVer, crates.io, RustSec official, deny/vet/auditable labeled extras. Notes 2026-08 crates.io build-script incident as supply-chain motivation. |
