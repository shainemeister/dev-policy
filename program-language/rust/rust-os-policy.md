---
title: "Rust OS Policy"
description: Curated map of how a Rust crate lives on Debian, Arch, macOS, and Windows — rustup vs distro rustc, linkers, ship formats. Not rustfmt and not crates.io.
version: "1.1.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - README.md
  - rust-language-policy.md
  - rust-ecosystem-policy.md
last_updated: "2026-08-29"
---

# Rust OS Policy

Reference pack for **how a hosted Rust crate lives on an operating
system**: how rustc arrives, which target triples are guaranteed,
which C toolchain links the binary, and how each OS ships the
result.

**Role:** curated map (working memory). **Not** L4 for any one crate.
**Not** rustfmt, Clippy, or the Nomicon — that is
[rust-language-policy.md](rust-language-policy.md).
**Not** crates.io, lockfiles, or `cargo publish` — that is
[rust-ecosystem-policy.md](rust-ecosystem-policy.md).

Last verified against rustc platform support, the rustup book, and
each OS's packaging docs as of 2026-08-29.

This pack has a **shared half** and four **OS carve-outs**. Apply the
shared half everywhere. Apply **one** carve-out per ship format. Do
not import apt into pacman, Homebrew into Debian, or MSVC into
Linux.

1. **Shared** — rustup, target tiers, host triples, rustup vs distro
   packages as a *choice*. Sections 1–2.
2. **Debian** — apt, distro rustc, dh-cargo, FHS. Section 3.
3. **Arch** — pacman `rust` vs `rustup`, Arch Wiki. Section 4.
4. **macOS** — Apple Silicon tier 1, Intel tier 2, Xcode CLT,
   Homebrew rustup PATH. Section 5.
5. **Windows** — MSVC vs GNU, Visual Studio Build Tools,
   rustup-init. Section 6.

A crate published only to crates.io still uses the shared half
(developers have an OS). A `.deb` / `.pkg.tar` / `.pkg` / `.msi`
adds exactly one carve-out.

------------------------------------------------------------------------
0. LAYERING
------------------------------------------------------------------------

This pack owns:

- rustc **target triples** and tier policy (what is guaranteed to
  work as a host)
- rustup as the rust-lang installer on every OS here
- Distro / vendor rustc packages as an **OS opinion**
- C/C++ linkers and SDKs the OS requires (gcc/clang, Xcode CLT,
  MSVC + Windows SDK)
- Ship-format placement (`/usr`, Homebrew prefix, Program Files)
- OS package-manager queues (apt, pacman, Homebrew, WinGet / MSI)
- Mapping RustSec onto OS security trackers, when the OS has one

This pack does **not** own:

- rustfmt, Clippy groups, `cargo test`, unsafe writing
  → Language pack
- `Cargo.toml` identity, crates.io, `cargo audit`, SemVer
  → Ecosystem pack
- Desktop HIG, application IDs, Flatpak finish-args
  → a desktop/application policy, not this map

Hard rules:

1. **rustup is rust-lang's installer on Debian, Arch, macOS, and
   Windows.** Distro packages are OS opinions, not a language
   requirement.
2. Distro rustc may lag this repo's stable pin. That is **this
   pack**, not a reason to freeze the language edition.
3. One payload OS per artifact. Do not ship one binary that claims
   both Debian FHS and a Homebrew cellar.
4. Do not import Debian NEW into pacman, Homebrew, or MSI.
5. Do not import MSVC into Linux, or Xcode into Windows.
6. `cargo fmt` / Clippy are never an OS package-manager check.

------------------------------------------------------------------------
1. FOUNDATIONAL DOCUMENTS (SHARED)
------------------------------------------------------------------------

rustc platform support (tiers and triples)
https://doc.rust-lang.org/rustc/platform-support.html
Target tier policy:
https://doc.rust-lang.org/rustc/target-tier-policy.html

rustup (official installer)
https://rust-lang.github.io/rustup/
https://www.rust-lang.org/tools/install
Windows:
https://rust-lang.github.io/rustup/installation/windows.html
Other package managers (apt, Homebrew, …):
https://rust-lang.github.io/rustup/installation/other.html

`rustc --version --verbose` prints the **host** triple. CI and
release jobs should print it.

Tier 1 with host tools (guaranteed to work as a *development*
platform; rustc 1.98 era):

| Triple | OS carve-out |
|--------|----------------|
| `x86_64-unknown-linux-gnu` | Debian, Arch (and other glibc Linux) |
| `aarch64-unknown-linux-gnu` | Debian, Arch (arm64) |
| `i686-unknown-linux-gnu` | Debian, Arch (32-bit Linux) |
| `aarch64-apple-darwin` | macOS (Apple Silicon, 11+) |
| `x86_64-pc-windows-msvc` | Windows (64-bit MSVC) |
| `aarch64-pc-windows-msvc` | Windows (ARM64 MSVC) |
| `i686-pc-windows-msvc` | Windows (32-bit MSVC) |
| `x86_64-pc-windows-gnu` | Windows (64-bit MinGW) |

`x86_64-apple-darwin` (Intel Mac) is **Tier 2 with host tools**
after RFC 3841: official binaries still exist; tests are not a
tier-1 gate. Prefer `aarch64-apple-darwin` as the macOS ship host.

https://rust-lang.github.io/rfcs/3841-demote-x86_64-apple-darwin.html

These four OS carve-outs do **not** cover Android, iOS, WASM, or
`*-linux-musl`. Those are later triples, not missing Debian.

------------------------------------------------------------------------
2. INSTALLING RUST (SHARED)
------------------------------------------------------------------------

https://www.rust-lang.org/tools/install
https://rust-lang.github.io/rustup/

rust-lang's recommended install is **rustup**, on every OS in this
pack. It installs compiler + cargo + rustfmt + rust-std from the
stable/beta/nightly channels and can add extra targets.

```text
rustup default stable
rustup update
rustc --version --verbose
```

`rust-toolchain.toml` in the crate pins the *channel or version*
developers and CI use. That pin is Ecosystem (MSRV) plus this pack
(the bits that actually run on the host).

Two legitimate ways to get a compiler:

| Method | Who | What you get |
|--------|-----|----------------|
| rustup (script, or OS package of rustup) | rust-lang | Current stable; extra targets; `rustup update` |
| Distro / vendor `rustc` package | the OS | Whatever that OS rebuilt; often one version; extra targets vary |

**Development of a crate** (this repo's default): rustup, current
stable, matching the language pack pin unless MSRV says otherwise.

**Building an OS package of that crate**: the OS carve-out decides
whether the buildd/chroot uses distro rustc (must honor MSRV) or a
vendored/newer toolchain the OS allows.

Do not mix rustup's `~/.cargo/bin` ahead of `/usr/bin` on a machine
that is *building distro packages* unless the OS packagers document
that. The reverse also bites: a distro `rustc` on `PATH` hiding
rustup during crate CI.

The rustup book documents OS package-manager wrappers (Debian 13
`apt install rustup`, Homebrew `brew install rustup`, Arch `pacman
-S rustup`). Those wrappers are still rustup. They are **not** the
same as the distro `rustc` package.

https://rust-lang.github.io/rustup/installation/other.html

------------------------------------------------------------------------
DEBIAN CARVE-OUT — section 3
------------------------------------------------------------------------

Apply when the host or the ship format is Debian (or a Debian
derivative using apt/dpkg). Do not apply to an Arch pkg, a Homebrew
bottle, or an MSI.

------------------------------------------------------------------------
3. DEBIAN
------------------------------------------------------------------------

Rust Team book (how Debian packages Rust)
https://rust-team.pages.debian.net/book/
Wiki:
https://wiki.debian.org/Teams/RustPackaging
dh-cargo:
https://manpages.debian.org/unstable/dh-cargo/dh-cargo.7.en.html

Two apt-installable toolchains:

- **`rustup` package** (Debian 13 / Trixie onward, rustup book).
  Installs rustup; you still pick a toolchain (`rustup default
  stable`). This is rust-lang's installer, wrapped by apt.
- **`rustc` / `cargo` packages**. Distro-rebuilt compiler. Version
  follows the suite (stable lags upstream; sid is closer). This is
  what official Debian *packages of Rust programs* usually compile
  with.

https://rust-lang.github.io/rustup/installation/other.html

Host triples Debian actually ships as first-class: GNU/Linux
`x86_64-unknown-linux-gnu` and `aarch64-unknown-linux-gnu` (and
others the archive enables). Musl and Windows-gnu cross are extra
packages, not this carve-out's default.

C toolchain: `build-essential` (gcc, libc-dev). `-sys` crates need
pkg-config and the `-dev` package of the C library. Link against
Debian shared libraries; do not vendor OpenSSL if `libssl-dev` is
the OS ABI (security updates flow through apt).

Ship format: `.deb` via dpkg. Placement is FHS / usr-merge:
`/usr/bin`, `/usr/lib/<triplet>/`, `/usr/share`. A Debian payload is
`/usr`, not `~/.cargo/bin` and not `/opt/homebrew`.

Packaging a crate for the archive:

- `dh-cargo` / `debcargo` for library crates in the Rust Team
  layout, or a single binary package that vendors with
  `Static-Built-Using`.
- **No network** on required `debian/rules` targets. Vendor
  (`cargo vendor`) or a Debian rust-crate package graph. Ecosystem
  lockfile still exists; the buildd will not fetch crates.io.
- `debian/copyright` (copyright-format 1.0) is the OS documentation
  of the license. It must not contradict `package.license`. DFSG is
  archive law for `main`.
- Binary package **name** is not the crates.io crate name.

Security: RustSec is still `cargo audit` (Ecosystem). Debian maps
those advisories onto binary packages at
https://rustsec.debian.net
DSA/bookworm-or-trixie rustc updates are apt. A rustup toolchain in
`$HOME` is **not** covered by Debian Security.

Do **not** run `cargo fmt` from `debian/rules` as if it were Policy.
Do **not** copy crates.io yank into `apt remove`.

------------------------------------------------------------------------
ARCH CARVE-OUT — section 4
------------------------------------------------------------------------

Apply when the host or the ship format is Arch Linux (pacman).

------------------------------------------------------------------------
4. ARCH
------------------------------------------------------------------------

ArchWiki (OS map for Rust on this distro)
https://wiki.archlinux.org/title/Rust

Official extra packages (they **conflict**):

- **`rust`** (`extra/rust`) — distro-rebuilt rustc + cargo + rustfmt.
  Tracks upstream closely (1.98.0 in extra as of 2026-08-20).
  Split packages: `rust-src`, `rust-musl`, `rust-wasm`, …
- **`rustup`** (`extra/rustup`) — Arch's rustup wrapper. Does **not**
  install a toolchain until `rustup default stable`. Proxies
  `/usr/bin/rustc` → rustup. `rustup self update` does not work;
  pacman updates the wrapper. `rustup update` still updates
  toolchains.

https://archlinux.org/packages/extra/x86_64/rust/
https://archlinux.org/packages/extra/x86_64/rustup/

ArchWiki: for *developing* software, rustup is the recommended
method (matches rust-lang). The `rust` package is the distro
compiler for building other official packages.

C toolchain: `base-devel` (gcc, make, pkgconf). `-sys` crates:
install the C library via pacman (`openssl`, `sqlite`, …), not a
private copy, when the official package exists.

Ship format: `.pkg.tar.zst` via pacman. Placement is Arch FHS
(`/usr`). PKGBUILDs that call `cargo` should use
`--locked --offline` after a prepare() that vendors or uses the
source tarball's lockfile. namcap is the OS static checker; it is
not Clippy.

Do **not** install `rust` and `rustup` together (pacman conflict).
Do **not** import Debian `dh-cargo` or `Static-Built-Using` into a
PKGBUILD. Do **not** treat Arch's fast rustc pin as Debian MSRV.

AUR helpers are not official Arch. This carve-out does not map them.

------------------------------------------------------------------------
MACOS CARVE-OUT — section 5
------------------------------------------------------------------------

Apply when the host or the ship format is macOS.

------------------------------------------------------------------------
5. MACOS
------------------------------------------------------------------------

https://doc.rust-lang.org/rustc/platform-support.html
https://rust-lang.github.io/rustup/

Host triple for new work: **`aarch64-apple-darwin`** (Tier 1, macOS
11+). Intel **`x86_64-apple-darwin`** is Tier 2 with host tools
(RFC 3841). Universal binaries are two triples, not a third OS.

Installer: rustup (rust-lang.org). Homebrew also wraps rustup:

```text
brew install rustup
```

Homebrew's rustup does **not** put `rustc`/`cargo` on `PATH` until
you run rustup's setup (rustup book; homebrew-core#177582). Treat
`brew install rust` (a distro compiler formula, if present) as an OS
opinion, same as Debian's `rustc` package: fine for consumers, not
the default for developing this pack's crates.

C toolchain: **Xcode Command Line Tools** (`xcode-select --install`).
The linker is Apple's. SDK via `xcrun --show-sdk-path`. `-sys` crates
often need Homebrew for the C library (`brew install openssl@3`)
*or* the crate's vendored feature. Document which. Linking Homebrew
OpenSSL on macOS is this OS, not Debian `libssl-dev`.

Ship format: a Mach-O binary, an `.app` bundle, or a Homebrew
formula. Placement:

- rustup tools: `~/.cargo/bin`
- Homebrew: `/opt/homebrew` (Apple Silicon) or `/usr/local` (Intel)
- App bundle: `Foo.app/Contents/MacOS/`

Do not install into Debian `/usr` on this OS.

A Mac app's signing, notarization, Gatekeeper rules, and App Store
payload are [os/macos](../../os/macos/README.md). This carve-out keeps
the toolchain and the host triple.

Do **not** import MSVC, apt, or pacman. Do **not** treat Intel Mac
CI as tier 1.

------------------------------------------------------------------------
WINDOWS CARVE-OUT — section 6
------------------------------------------------------------------------

Apply when the host or the ship format is Windows.

------------------------------------------------------------------------
6. WINDOWS
------------------------------------------------------------------------

https://rust-lang.github.io/rustup/installation/windows.html
https://doc.rust-lang.org/rustc/platform-support.html

Installer: `rustup-init.exe` from rust-lang.org. rustup runs on
Windows. The first-run prompt picks the default host ABI.

Two Windows ABIs (both tier 1 on x86_64). **Pick one per artifact.**

| Triple | Linker / CRT | When |
|--------|----------------|------|
| `x86_64-pc-windows-msvc` (default) | MSVC + Windows SDK | Native Windows; recommended |
| `aarch64-pc-windows-msvc` | MSVC + Windows SDK | ARM64 Windows (tier 1) |
| `x86_64-pc-windows-gnu` | MinGW | GNU toolchain; interop with mingw |

MSVC path requires **Visual Studio Build Tools** (or VS) with the
Windows SDK and the MSVC C++ workload. rustup's docs say so. Without
them, `link.exe` is missing and the build fails. That is this OS, not
a Cargo bug.

GNU path needs a MinGW gcc. Do not mix `windows-msvc` and
`windows-gnu` in one "the binary" story; they are different CRTs.

C/`-sys` crates: vcpkg, the crate's vendored feature, or MSVC-built
libraries. pkg-config is not the Windows default.

Ship format: `.exe` / `.dll`, optionally MSI/MSIX/WinGet. Placement
is not FHS. rustup tools live under `%USERPROFILE%\.cargo\bin`.
Do not document `/usr/bin`.

Long paths and Developer Mode are OS knobs; Cargo can fail on deep
`target\` trees without long-path support. CRLF vs LF in the crate
is Language/style (rustfmt), not this carve-out.

Do **not** import Xcode, apt, or pacman. Do **not** require
`debian/rules`. WinGet/MSI metadata is this OS's store; crates.io
identity stays Ecosystem.

------------------------------------------------------------------------
7. QUALITY CHECKS (THIS OS)
------------------------------------------------------------------------

Shared (every developer host):

```text
rustc --version --verbose
rustup show
```

Confirm the **host** triple matches the carve-out you claim.

Debian extra (when the artifact is a `.deb`):

- Clean chroot build, no network on required targets
- Files under `/usr`, usr-merge-safe
- `debian/copyright` consistent with `package.license`
- Do not invoke rustfmt/Clippy as the package check (Language CI
  already did)

Arch extra (when the artifact is a pacman package):

- PKGBUILD `--locked --offline` after prepare
- `rust` XOR `rustup` in makedepends, not both
- namcap clean enough to ship; still not Clippy

macOS extra (when you ship a Mac binary):

- Host `aarch64-apple-darwin` (or a documented Intel tier-2 build)
- Xcode CLT present; `xcrun --show-sdk-path` works
- If Gatekeeper must accept the binary, follow
  [os/macos](../../os/macos/README.md) Direct OS

Windows extra (when you ship a Windows binary):

- Host triple `*-pc-windows-msvc` or `*-pc-windows-gnu`, documented
- `link.exe` or MinGW gcc actually on PATH in CI
- One ABI per artifact

------------------------------------------------------------------------
8. WHAT THIS PACK EXPLICITLY IS NOT
------------------------------------------------------------------------

Not rustfmt, Clippy, or `cargo test`.

Not crates.io policy or RustSec's database (Ecosystem still runs
`cargo audit` on every OS).

Not a dump of Debian Policy or the ArchWiki. Apple signing,
notarization, and App Review live in
[os/macos](../../os/macos/README.md). Not MSDN.

Not Android, iOS, WASM, or musl-first images.

Not a requirement to use all four OSes. Pick the carve-outs you
ship.

------------------------------------------------------------------------
9. COMPOSING WITH OTHER PACKS
------------------------------------------------------------------------

Crate on crates.io, developed on any of these OSes:

  Language + Ecosystem + **this pack, shared half**
  + the carve-out of the *developer* OS (so the linker exists)

Debian `.deb` of a Rust CLI:

  Language + Ecosystem + this pack **Debian**

Arch package of the same CLI:

  Language + Ecosystem + this pack **Arch**
  (do not keep the Debian half)

macOS binary / Homebrew formula:

  Language + Ecosystem + this pack **macOS**

Windows `.exe` / MSI:

  Language + Ecosystem + this pack **Windows**

Same source. Language formats and tests it. Ecosystem publishes the
crate. This pack installs the compiler and places the binary.

License: SPDX on the crate is Ecosystem. DFSG / `debian/copyright`
are Debian carve-out. Pacman `license=()` is Arch. Homebrew
`license` stanza is macOS. MSVC redistributable terms are Windows.
Do not copy DFSG into an MSI.

------------------------------------------------------------------------
10. QUICK OFFICIAL LINK LIST
------------------------------------------------------------------------

Platform support
https://doc.rust-lang.org/rustc/platform-support.html
https://doc.rust-lang.org/rustc/target-tier-policy.html

rustup
https://rust-lang.github.io/rustup/
https://www.rust-lang.org/tools/install
https://rust-lang.github.io/rustup/installation/windows.html
https://rust-lang.github.io/rustup/installation/other.html

Debian
https://rust-team.pages.debian.net/book/
https://wiki.debian.org/Teams/RustPackaging
https://rustsec.debian.net
https://rust-lang.github.io/rustup/installation/other.html

Arch
https://wiki.archlinux.org/title/Rust
https://archlinux.org/packages/extra/x86_64/rust/
https://archlinux.org/packages/extra/x86_64/rustup/

macOS
https://doc.rust-lang.org/rustc/platform-support.html
https://rust-lang.github.io/rfcs/3841-demote-x86_64-apple-darwin.html

Windows
https://rust-lang.github.io/rustup/installation/windows.html

Sister packs
./rust-language-policy.md
./rust-ecosystem-policy.md
./README.md

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.1.0 | Initial OS pack: shared rustup + tiers; carve-outs for Debian, Arch, macOS, Windows |
