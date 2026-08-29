---
title: "C/C++ development policy packs"
description: Modular language, ecosystem, and OS policy maps for C and C++. Compose packs; do not merge them into one rulebook.
version: "1.0.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - c-language-policy.md
  - c-ecosystem-policy.md
  - c-os-policy.md
  - sources.yaml
last_updated: "2026-08-29"
---

# C/C++ development policy packs

Curated maps of **what each layer actually checks**. Not tutorials. Not
product law for any one library.

Three axes. Compose packs; do not merge them. Language and ecosystem
are **OS-agnostic**. OS tools and ship formats live in **carve-outs**
(Debian, Arch, macOS, Windows). Same shape as
[rust](../rust/README.md).

```text
                 LANGUAGE                         ECOSYSTEM                        OS
                 (what the code is)               (how the project lives)          (how it lives on a system)
C/C++            c-language-policy.md             c-ecosystem-policy.md            c-os-policy.md
                                                                                   Debian | Arch | macOS | Windows
```

**Role:** working memory for humans and agents. Cite official manuals;
do not treat this folder as a substitute for ISO/IEC 9899, ISO/IEC
14882, the CMake docs, or an OS packaging guide.

C and C++ share a compiler family and a link/ABI world. They are
**two halves of the language pack**, not two distros. A C library and
a C++ library still compose the same ecosystem and OS packs.

Last verified against WG14, WG21, GCC, Clang, CMake, Meson, and OS
installer docs as of 2026-08-29. Pins and the watch workflow are in
**Retrieving updates from official sources**.

------------------------------------------------------------------------
How to compose
------------------------------------------------------------------------

Always take **Language** (the C half, the C++ half, or both). Add
**Ecosystem** when there is a build description (CMake, Meson,
pkg-config). Add **OS (shared half)** whenever a compiler must
actually run. Add **exactly one OS carve-out** per ship format.

| Deliverable | Language | Ecosystem | OS |
|-------------|----------|-----------|-----|
| Hosted C or C++ library (any dev OS) | yes | yes | shared + developer host carve-out |
| Same project, unpublished | yes | yes (skip registry extras) | shared + developer host |
| Debian `.deb` | yes | yes | Debian |
| Arch `.pkg.tar.zst` | yes | yes | Arch |
| macOS dylib / framework / Homebrew | yes | yes | macOS |
| Windows `.dll` / `.lib` / MSI | yes | yes | Windows |

Do **not** apply the Debian carve-out to an MSI. Do **not** apply
MSVC to a `.deb`. Do **not** apply `clang-format` to an OS packaging
script as if it were that OS's policy. Do **not** import CMake
`install()` paths into a second OS.

Hosted libraries and binaries only. Freestanding / bare-metal,
CUDA, and Objective-C are out of scope until a later revision.

------------------------------------------------------------------------
Conflict resolution
------------------------------------------------------------------------

When two packs mention the same object, split **contents** from
**placement** and **queue**.

| Object | Who owns contents | Who owns placement | Who owns the queue |
|--------|-------------------|--------------------|--------------------|
| Source text, types, UB | Language | — | CI / code review |
| clang-format / compiler warnings / clang-tidy | Language | CI / CMake properties | CI |
| CMakeLists / meson.build / .pc | — | Ecosystem | the build you run |
| Library SONAME / soversion | Ecosystem (the number you declare) | OS (how the linker loads it) | OS packager |
| License | Language (no ISO rule) | Ecosystem (SPDX / LICENSE) | OS carve-out |
| Include / header names | Language (what they mean) | Ecosystem (`include/` layout) | OS (`/usr/include` vs SDK) |
| Advisories | — | Ecosystem (OSV extra) | OS security tracker |
| gcc/clang/msvc **install** | — | OS | OS package manager |
| Distro compiler lag | — | OS carve-out | OS suite |
| `/usr` vs Homebrew prefix vs Program Files | — | OS carve-out | OS packager |

Hard rules:

1. One language dialect per translation-unit family. Do not mix
   `-std=c17` and `-std=c++23` in one library without a documented
   C API boundary.
2. clang-format **LLVM** is the default style this pack maps. Other
   `-style=` values are house forks. Document them.
3. `-Werror`, clang-tidy `*` , and sanitizers are **CI extras**, not
   ISO and not gcc/clang defaults.
4. Language and ecosystem packs do **not** require apt, pacman,
   Homebrew, or MSVC.
5. There is **no rustup** for C. The compiler comes from the OS
   carve-out (distro package, Xcode CLT, Visual Studio, or an
   upstream LLVM/GCC tarball).
6. Distro gcc/clang lag is the OS pack. It is not a reason to freeze
   the language dialect in the language pack forever.
7. One payload OS per artifact. Do not import Debian NEW into
   pacman, Homebrew, or MSI. Do not import MSVC into Linux, or
   Xcode into Windows.
8. CMake is the common *build contract* in the ecosystem pack, not
   a requirement to abandon Meson. Compose; do not merge.
9. vcpkg and Conan are **registry extras**, not ISO and not CMake
   Policy.

------------------------------------------------------------------------
Official map vs audit extra
------------------------------------------------------------------------

C/C++ has **no Cargo and no crates.io**. ISO is paywalled. Compilers,
build systems, and OS packagers each check a different bar.

- **Official map** — ISO WG14/WG21 (via public drafts and status
  pages), GCC and Clang language status, CMake/Meson, pkg-config,
  and each OS's *own* compiler and packaging docs.
- **Audit extra** — sanitizers, clang-tidy beyond compiler warnings,
  `-Werror`, vcpkg/Conan lockfiles, OSV/cve scanning, Apple
  notarization, namcap. Labeled in the packs.

A later agent must not turn `-Werror` or `bugprone-*` into ISO, or
`clang-format` into apt Policy.

------------------------------------------------------------------------
What each pack is
------------------------------------------------------------------------

[c-language-policy.md](c-language-policy.md)

What C and C++ require of the *code*: ISO dialect, undefined
behavior, compiler warning groups, clang-format, tests. C half and
C++ half. Not CMake. Not apt/MSVC.

[c-ecosystem-policy.md](c-ecosystem-policy.md)

How a project *builds and is described*: CMake (common contract),
Meson (alternative), pkg-config, CMake package files, soversion,
SPDX. vcpkg/Conan labeled extras.

[c-os-policy.md](c-os-policy.md)

How a compiler and a binary exist on a system. Shared: host
triples, C ABI. Carve-outs: Debian, Arch, macOS, Windows.

------------------------------------------------------------------------
Adding another language
------------------------------------------------------------------------

C/C++ already shares this tree. Do not fold Rust or Go into these
files. Rust is [../rust](../rust/README.md); a later Go family is a
new directory under [program-language/](../). Debian Policy and the
HIG live in [os/linux](../../os/linux/README.md). To add Fedora or
NixOS as a *C/C++* carve-out, add a section to the OS pack.

------------------------------------------------------------------------
Retrieving updates from official sources
------------------------------------------------------------------------

Packs are maps. Official manuals remain the authority.

[sources.yaml](sources.yaml) is the watch registry.
[../../scripts/check_sources.py](../../scripts/check_sources.py)
(`--family program-language/c`) prints `UNCHANGED` or `DRIFT`. On
drift, patch the owning pack with a bite-sized rule, then bump the
pin. Never auto-merge HTML into packs.

Cadence:

- GCC / Clang / CMake releases: about every few months
- WG14 / WG21 status: around meetings
- OS packaging pages: weekly

Current pins as of 2026-08-29:

- C **23** (ISO/IEC 9899:2024); public draft **N3220**
- C++ **23** published; C++ **26** technical work complete (DIS),
  not yet the ship bar for this pack
- New C projects: **C23** if the claimed compiler implements it,
  else **C17**
- New C++ projects: **C++23** if the claimed compiler implements
  it, else **C++20**
- clang-format default style: **LLVM**

`archive/` is reserved for a frozen snapshot after the next version
bump.

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.0.0 | Initial three-pack split: C/C++ Language (two halves), Ecosystem (CMake/Meson), OS (Debian, Arch, macOS, Windows). |
