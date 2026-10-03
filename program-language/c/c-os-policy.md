---
title: "C/C++ OS Policy"
description: Curated map of how a C/C++ program lives on Debian, Arch, macOS, and Windows — compilers, linkers, ship formats. Not clang-format and not CMake.
version: "1.0.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - README.md
  - c-language-policy.md
  - c-ecosystem-policy.md
last_updated: "2026-08-29"
---

# C/C++ OS Policy

Reference pack for **how a hosted C/C++ project lives on an
operating system**: how gcc/clang/MSVC arrive, which C ABI the
host uses, and how each OS ships the result.

**Role:** curated map (working memory). **Not** L4 for any one
library. **Not** `-std=` or clang-format —
[c-language-policy.md](c-language-policy.md).
**Not** CMake/Meson/pkg-config *contents* —
[c-ecosystem-policy.md](c-ecosystem-policy.md).

Last verified against OS compiler and packaging docs as of
2026-08-29.

Shared half plus four carve-outs. Apply the shared half everywhere.
Apply **one** carve-out per ship format. Do not import apt into
pacman, Homebrew into Debian, or MSVC into Linux.

1. **Shared** — host triples, C ABI, compiler *families*. §1–2.
2. **Debian** — apt gcc/clang, build-essential, dpkg. §3.
3. **Arch** — pacman `base-devel`, extra/gcc. §4.
4. **macOS** — Xcode CLT, Apple clang, Homebrew. §5.
5. **Windows** — MSVC vs MinGW vs clang-cl. §6.

------------------------------------------------------------------------
0. LAYERING
------------------------------------------------------------------------

This pack owns:

- How gcc, clang, and MSVC are **installed**
- Host triples / PE vs ELF vs Mach-O
- C library (glibc, Apple libc, UCRT/MSVC CRT)
- Linkers and SDKs (binutils/lld, Xcode SDK, Windows SDK)
- Ship-format placement (`/usr`, Homebrew prefix, Program Files)
- OS package-manager queues
- Mapping CVEs onto OS packages of *your* binary and of gcc/openssl

This pack does **not** own:

- ISO dialect and warnings → Language
- CMakeLists, `.pc` keys, SONAME *number* → Ecosystem
- How `install(TARGETS)` is written → Ecosystem
  (this pack owns the prefix the packager passes)

Hard rules:

1. There is **no rustup** for C. Compilers come from the OS
   carve-out or an upstream tarball you document.
2. Distro gcc/clang may lag this pack's preferred `-std=`. That is
   **this pack**, not a reason to freeze the language dialect in
   the language pack without recording it.
3. One payload OS per artifact.
4. Do not import Debian NEW into pacman, Homebrew, or MSI.
5. Do not import MSVC into Linux, or Xcode into Windows.
6. `clang-format` is never an OS package-manager check.
7. Link OS-provided OpenSSL/zlib when the OS ships them; security
   updates flow through that OS. Vendoring crypto is an OS
   integrity hole unless the OS carve-out has no package.

------------------------------------------------------------------------
1. FOUNDATIONAL DOCUMENTS (SHARED)
------------------------------------------------------------------------

ELF / System V ABI (Linux)
https://refspecs.linuxfoundation.org/

Mach-O / Darwin (Apple)
https://developer.apple.com/documentation/xcode

PE / COFF / MSVC
https://learn.microsoft.com/en-us/cpp/build/

GNU GCC
https://gcc.gnu.org/onlinedocs/

LLVM/Clang
https://clang.llvm.org/docs/UsersManual.html

Typical **hosted** triples this pack maps (not a rustc tier table —
C has no single tier policy):

| Triple / toolchain | OS carve-out |
|--------------------|----------------|
| `x86_64-linux-gnu` / `aarch64-linux-gnu` (gcc or clang, glibc) | Debian, Arch |
| `arm64-apple-darwin` (Apple clang) | macOS |
| `x86_64-pc-windows-msvc` | Windows MSVC |
| `x86_64-w64-mingw32` | Windows GNU |

Intel Mac (`x86_64-apple-darwin`) still exists; Apple Silicon is
the ship host for new macOS work (same fact as rustc RFC 3841:
Intel is not the future).

------------------------------------------------------------------------
2. INSTALLING A COMPILER (SHARED)
------------------------------------------------------------------------

Pick a **family** and a **version you CI**:

| Family | How you usually get it | Notes |
|--------|------------------------|-------|
| GCC | OS package or upstream | GNU dialect extras exist; ISO is `-std=c23` / `c++23` |
| Clang/LLVM | OS package, Xcode, or llvm.org | clang-format/tidy live here |
| MSVC | Visual Studio / Build Tools | `/std:c++latest` is not ISO C++23 until you pin `/std:c++23` |

`cc` / `c++` on POSIX are OS alternatives (Debian `update-alternatives`,
macOS `xcrun`). Do not assume `cc` is gcc.

Record `cc -v` / `clang --version` / `cl` banner in CI logs. Language
dialect flags stay in the language pack; this pack makes sure the
binary exists.

------------------------------------------------------------------------
DEBIAN CARVE-OUT — section 3
------------------------------------------------------------------------

Apply when the host or ship format is Debian (apt/dpkg).

------------------------------------------------------------------------
3. DEBIAN
------------------------------------------------------------------------

https://www.debian.org/doc/debian-policy/ch-sharedlibs.html
https://wiki.debian.org/ToolChain
https://manpages.debian.org/unstable/dpkg-dev/dpkg-architecture.1.en.html

Toolchain packages:

- `build-essential` — gcc, g++, make, libc-dev (the usual C/C++
  hosted build)
- `clang` / `clang-tidy` / `clang-format` — LLVM extra from apt
- Cross: `gcc-aarch64-linux-gnu` etc.

Debian's gcc **lags** upstream on stable. Sid/testing is closer.
If a `.deb` must build on Trixie, the dialect you claim in Language
must match that gcc (or you document a toolchain exception the
archive allows). Do not run a sid clang in a Trixie buildd and call
it the package.

C library: glibc. Multiarch: libraries in
`/usr/lib/<triplet>/`. 64-bit packages must not install into
`/usr/lib64` (Debian Policy).

Shared libraries: Policy chapter 8. `dpkg-shlibdeps`,
`${shlibs:Depends}`, runtime symbol versions. SONAME the Ecosystem
pack declared must match the `*.so.N` you ship. `DEBIAN/shlibs`.

Headers: `/usr/include` or `/usr/include/<triplet>`. pkg-config:
`/usr/lib/<triplet>/pkgconfig` and `/usr/share/pkgconfig`.

Build: **no network** on required `debian/rules` targets. CMake
`FetchContent` that hits GitHub will fail. Vendor or use Debian
`-dev` packages. That is this carve-out applying Ecosystem's
"pin dependencies" under a no-network OS rule.

`debian/copyright` documents DFSG. It must not contradict SPDX.

Do **not** run clang-format from `debian/rules` as Policy. Do
**not** copy CMake `install()` prefixes other than `/usr` into a
`.deb`.

------------------------------------------------------------------------
ARCH CARVE-OUT — section 4
------------------------------------------------------------------------

Apply when the host or ship format is Arch (pacman).

------------------------------------------------------------------------
4. ARCH
------------------------------------------------------------------------

https://wiki.archlinux.org/title/C++
https://wiki.archlinux.org/title/Arch_package_guidelines
https://wiki.archlinux.org/title/Makepkg

- `base-devel` — gcc, make, pkgconf, …
- `clang`, `llvm` — extra
- `extra/gcc` tracks upstream closely (unlike Debian stable)

`gcc` and `clang` can coexist. `cc` is gcc by default.

PKGBUILD: `makedepends` for the toolchain, `depends` for shared
libs you link. namcap is the OS static checker; it is not
clang-tidy. Builds should be repeatable; network in `build()` is
an Arch packaging smell (fetch in `prepare()` / source=()).

Placement: `/usr`. Do not import `dh-make` or `Static-Built-Using`.
Do not treat Arch's new gcc as Debian MSRV.

AUR is not official Arch. This carve-out does not map it.

------------------------------------------------------------------------
MACOS CARVE-OUT — section 5
------------------------------------------------------------------------

Apply when the host or ship format is macOS.

------------------------------------------------------------------------
5. MACOS
------------------------------------------------------------------------

https://developer.apple.com/xcode/resources/
https://clang.llvm.org/docs/UsersManual.html

Default compiler: **Apple clang** via **Xcode Command Line Tools**
(`xcode-select --install`). `xcrun --show-sdk-path` is the SDK.
This clang **lags** llvm.org; C++23/26 features may be missing.
Homebrew `llvm` is an extra compiler, not `cc` unless you change
PATH. Document which clang you mean.

Host for new work: Apple Silicon (`arm64-apple-darwin`). Intel is
legacy.

Mach-O install names (`LC_ID_DYLIB`, `@rpath`) are this OS.
`install_name_tool` / CMake `MACOSX_RPATH` rewrite what Ecosystem
declared. Do not Debian-SONAME a dylib.

Homebrew prefix: `/opt/homebrew` (Apple Silicon), `/usr/local`
(Intel). Linking Homebrew OpenSSL is this OS, not `libssl-dev`.

Ship: dylib, framework, `.app`, or a Homebrew formula. Signing,
notarization, and App Store rules for a Mac app are
[os/macos](../../os/macos/README.md), not clang.

Do **not** install into Debian `/usr`. Do **not** import MSVC.

------------------------------------------------------------------------
WINDOWS CARVE-OUT — section 6
------------------------------------------------------------------------

Apply when the host or ship format is Windows.

------------------------------------------------------------------------
6. WINDOWS
------------------------------------------------------------------------

https://learn.microsoft.com/en-us/cpp/build/reference/compiler-options
https://learn.microsoft.com/en-us/visualstudio/install/build-tools-container

Three hosted toolchains. **Pick one per artifact.**

| Toolchain | Compiler | CRT | When |
|-----------|----------|-----|------|
| MSVC (default native) | `cl.exe` | MSVC CRT / UCRT | Recommended Windows native |
| clang-cl | Clang in MSVC mode | MSVC CRT | LLVM extras + MSVC ABI |
| MinGW-w64 | gcc | mingw CRT | GNU ABI; not MSVC-compatible |

MSVC requires **Visual Studio Build Tools** (or VS) with the
Windows SDK and the C++ workload. Without `cl.exe` / `link.exe`
the build fails. That is this OS, not a CMake bug.

C11/C17: MSVC C support is historically incomplete (no VLAs; C11
atomics lagged). Language pack already says no VLAs if MSVC is a
consumer. `/std:c11` / `/std:c17` exist on recent VS; C23 is not
a MSVC ship bar in this 1.0.0 map — document fallback C17.

C++: `/std:c++20` and `/std:c++23` on VS 2022+. `/std:c++latest` is
not a dialect pin.

DLLs: no SONAME. Export via `__declspec(dllexport)` or a `.def`
file. Import library `.lib` ships with the DLL. CRT mismatch
(debug vs release, static vs DLL CRT) is a classic Windows fail —
link the same CRT the OS carve-out documents.

Do **not** import Xcode or apt. WinGet/MSI metadata is this OS;
CMake `install()` still uses a prefix the packager passes.

------------------------------------------------------------------------
7. QUALITY CHECKS (THIS OS)
------------------------------------------------------------------------

Shared:

```text
cc -v   # or clang --version / cl
```

Debian extra (`.deb`):

- Clean chroot, no network
- Files under `/usr`, multiarch-correct
- `dpkg-shlibdeps` happy
- `debian/copyright` vs SPDX

Arch extra:

- PKGBUILD sources pinned; namcap
- `base-devel` in the chroot

macOS extra:

- `xcode-select -p` / `xcrun --show-sdk-path`
- Apple Silicon host for new binaries
- `@rpath` sane; Gatekeeper acceptance is [os/macos](../../os/macos/README.md)

Windows extra:

- One of MSVC / clang-cl / MinGW, documented
- `cl` or MinGW gcc on PATH in CI
- Matching CRT

------------------------------------------------------------------------
8. WHAT THIS PACK EXPLICITLY IS NOT
------------------------------------------------------------------------

Not ISO. Not CMake. Not clang-format. Not Android NDK / iOS /
freestanding.

------------------------------------------------------------------------
9. COMPOSING WITH OTHER PACKS
------------------------------------------------------------------------

C library as a Debian `.deb`:

  Language (C) + Ecosystem + this pack **Debian**

Same sources as a Windows DLL:

  Language + Ecosystem + this pack **Windows**
  (drop the Debian half)

Compiler version vs `-std=`: OS supplies the compiler; Language
owns the dialect. If they fight, either raise the OS toolchain or
lower the dialect — record it.

------------------------------------------------------------------------
10. QUICK OFFICIAL LINK LIST
------------------------------------------------------------------------

GCC / Clang
https://gcc.gnu.org/onlinedocs/
https://clang.llvm.org/docs/UsersManual.html

Debian
https://www.debian.org/doc/debian-policy/ch-sharedlibs.html
https://wiki.debian.org/ToolChain

Arch
https://wiki.archlinux.org/title/C++
https://wiki.archlinux.org/title/Arch_package_guidelines

macOS
https://developer.apple.com/xcode/resources/

Windows
https://learn.microsoft.com/en-us/cpp/build/

Sister packs
./c-language-policy.md
./c-ecosystem-policy.md
./README.md

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.0.0 | Initial OS pack: shared compiler families; Debian, Arch, macOS, Windows carve-outs |
