---
title: "C/C++ Ecosystem Policy"
description: Curated map of how a C/C++ project lives — CMake, Meson, pkg-config, soversion, SPDX. Not clang-format and not OS packaging.
version: "1.0.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - README.md
  - c-language-policy.md
  - c-os-policy.md
last_updated: "2026-08-29"
---

# C/C++ Ecosystem Policy

Reference pack for **how a hosted C/C++ project is described and
built**: the build specification, public install interface
(pkg-config / CMake package files), library versioning, and SPDX.

**Role:** curated map (working memory). **Not** L4 for any one
library. **Not** `-std=` / clang-format / UB — that is
[c-language-policy.md](c-language-policy.md).
**Not** apt, pacman, Homebrew, or MSVC — that is
[c-os-policy.md](c-os-policy.md).

Last verified against CMake, Meson, and pkg-config docs as of
2026-08-29.

C/C++ has **no Cargo and no crates.io**. The common *build contract*
this pack maps is **CMake**. **Meson** is a first-class alternative
(compose, do not merge). Autotools, Bazel, and plain Make exist;
they are not this pack's default map. **vcpkg** and **Conan** are
registry extras, not CMake Policy.

------------------------------------------------------------------------
0. LAYERING
------------------------------------------------------------------------

This pack owns:

- CMakeLists.txt / CMake package config as the common contract
- meson.build as the alternative contract
- pkg-config `.pc` contents (the keys; install path is OS)
- CMake `XxxConfig.cmake` / `XxxConfigVersion.cmake`
- `VERSION` / `SOVERSION` as *declared* numbers
- How tests are *invoked* (CTest, `meson test`)
- SPDX / LICENSE at the project root
- Dependency *declaration* (`find_package`, `dependency()`, extras)

This pack does **not** own:

- `-std=`, `-Wall`, clang-format
  → Language
- gcc/clang/cl.exe install, `/usr` vs Program Files, dylib IDs
  → OS
- How `dpkg-shlibdeps` or `install_name_tool` rewrite the binary
  → OS

------------------------------------------------------------------------
1. FOUNDATIONAL DOCUMENTS
------------------------------------------------------------------------

CMake
https://cmake.org/cmake/help/latest/
`cmake-packages`:
https://cmake.org/cmake/help/latest/manual/cmake-packages.7.html
`install`:
https://cmake.org/cmake/help/latest/command/install.html
`CTest`:
https://cmake.org/cmake/help/latest/manual/ctest.1.html

Meson
https://mesonbuild.com/
https://mesonbuild.com/Reference-manual.html

pkg-config
https://www.freedesktop.org/wiki/Software/pkg-config/
File format (historical):
https://people.freedesktop.org/~dbn/pkg-config-guide.html
pkgconf (typical implementation):
https://github.com/pkgconf/pkgconf

GNU/ELF SONAME (declared here; loaded by the OS)
https://www.gnu.org/software/libtool/manual/html_node/Libtool-versioning.html

SPDX
https://spdx.dev/specifications/

vcpkg / Conan (**extras**)
https://vcpkg.io/
https://docs.conan.io/

------------------------------------------------------------------------
2. CMAKE (COMMON BUILD CONTRACT)
------------------------------------------------------------------------

https://cmake.org/cmake/help/latest/

A CMake project is what `CMakeLists.txt` describes. Out-of-source
build is the documented norm.

Minimum `cmake_minimum_required` is a **compatibility pin**, like
Cargo `rust-version`. Set it to a version you CI. Do not claim
"latest CMake only" if an OS carve-out's cmake lags (Debian suite
cmake is OS).

Must-haves for a hosted library:

- `project(... VERSION ... LANGUAGES C)` and/or `CXX`
- Targets (`add_library` / `add_executable`), not glob-compiled
  spaghetti without a target
- `PUBLIC` / `PRIVATE` / `INTERFACE` include and link usage
  requirements (`target_include_directories`,
  `target_link_libraries`)
- `install(TARGETS ... EXPORT ...)` plus a CMake package file so
  consumers can `find_package`
- Tests wired to CTest (`enable_testing` / `add_test`) when you
  have tests (Language says tests must exist)

`CMAKE_BUILD_TYPE` (single-config) vs multi-config generators
(Visual Studio, Xcode) is a generator fact. Do not assume
`CMAKE_BUILD_TYPE=Release` exists on Windows VS generators.

`FetchContent` / git submodules as the *only* dependency path is a
supply-chain choice. Pin revisions. Unpinned git is the same failure
mode as unpinned Cargo git deps.

Do **not** put OS-specific `/usr/lib` into `CMakeLists` as the
install prefix. `GNUInstallDirs` + `CMAKE_INSTALL_PREFIX` (OS
default `/usr`, `/usr/local`, Homebrew prefix, or a prefix the
packager passes).

https://cmake.org/cmake/help/latest/module/GNUInstallDirs.html

Compile flags that are *language dialect* (`-std=c23`) belong in
the target as a language requirement (`target_compile_features` /
`CMAKE_C_STANDARD`). Warning extras can live in CMake but they are
still Language.

------------------------------------------------------------------------
3. MESON (ALTERNATIVE CONTRACT)
------------------------------------------------------------------------

https://mesonbuild.com/

Meson is not CMake. Do not translate a Meson project into CMake
inside this pack. If the project is Meson:

- `meson.build` + `meson_options.txt`
- `library()` / `executable()` with version:
  `version:` / `soversion:`
- `pkg.generate()` for `.pc`
- `test()` for the test runner
- Wrap files (`subprojects/`) pin wrap-db or git revisions

Consumers still get a `.pc` and/or CMake config if you generate
them. A Meson-only library that ships no `.pc` is hard to consume
from CMake; that is an ecosystem stall.

------------------------------------------------------------------------
4. PKG-CONFIG AND CMAKE PACKAGES
------------------------------------------------------------------------

These are how *other* build systems find you. Install **path** is
OS (`/usr/lib/pkgconfig` vs Homebrew). **Keys** are this pack.

`.pc` must-haves:

- `Name`, `Description`, `Version`
- `Cflags` (`-I` usage requirements)
- `Libs` (`-L` `-l`)
- `Requires` / `Requires.private` for public vs private deps

A `.pc` that puts `-Werror` in `Cflags` is a language extra leaked
into every consumer. Do not.

CMake package files:

https://cmake.org/cmake/help/latest/manual/cmake-packages.7.html

- `XxxConfig.cmake` + `XxxConfigVersion.cmake` (`SameMajorVersion`
  or documented compatibility)
- Imported targets (`Xxx::Xxx`), not just `XXX_LIBRARIES`
  variables
- Namespace matches the project

A library should ship **at least one** of: `.pc`, CMake package.
Hosted C libraries usually ship both.

------------------------------------------------------------------------
5. LIBRARY VERSIONING (DECLARED)
------------------------------------------------------------------------

ELF `SONAME` / Mach-O compatibility version / Windows DLL naming
are **loaded by the OS**. The *numbers you put in the build file*
are this pack.

libtool-style current:revision:age is GNU convention, not ISO.
CMake `VERSION` + `SOVERSION` on `add_library(SHARED)`:

https://cmake.org/cmake/help/latest/command/add_library.html

Breaking the C ABI (removed exported symbol, changed struct layout
in a public header, changed calling convention) requires a SONAME
bump. That is the ecosystem analog of Cargo major. C++ ABI breaks
more easily (any class layout change); many C++ libraries treat the
whole shared object as major-per-release or ship static.

Do not bump SONAME on every commit. Do not skip a bump when you
broke the ABI.

Windows: DLLs have no SONAME. Import `.lib` + DLL name + optional
side-by-side is the OS carve-out. This pack still wants a
documented version in the project().

------------------------------------------------------------------------
6. DEPENDENCIES AND REGISTRIES (OFFICIAL VS EXTRA)
------------------------------------------------------------------------

**Official-ish (build system native):**

- `find_package` / `pkg_check_modules` / Meson `dependency()`
  against OS-provided or user-provided prefixes
- `FetchContent` with a **pinned** git tag/commit

**Registry extras (not CMake Policy, not ISO):**

- **vcpkg** — `vcpkg.json` manifest, baseline pin
  https://learn.microsoft.com/en-us/vcpkg/reference/vcpkg-json
- **Conan** — `conanfile` + lockfile
  https://docs.conan.io/

If you use a registry extra, pin it (baseline, lockfile) the way
Cargo pins `Cargo.lock`. Do not float `latest`.

There is no crates.io yank analog. Deleting a tag you FetchContent'd
is a supply-chain incident. Prefer hashes.

System libraries (OpenSSL, zlib, ICU): **link the OS copy** when
the OS carve-out ships them and security updates flow through that
OS. Vendoring TLS/crypto is an OS integrity issue (see OS pack)
plus this pack's "document the vendor."

------------------------------------------------------------------------
7. LICENSE
------------------------------------------------------------------------

ISO does not require an SPDX identifier. This pack does, for a
hosted project:

- `LICENSE` (or `COPYING`) at the repository root
- SPDX expression in CMake `project(LICENSE ...)` if the CMake
  version you require supports it, and/or in README / `.pc`

OS archives add their own files (`debian/copyright`, pacman
`license=()`, Homebrew formula, MSI). Those are OS. They must not
contradict this SPDX.

------------------------------------------------------------------------
8. SUPPLY CHAIN EXTRA
------------------------------------------------------------------------

No RustSec-for-C that is as central. Extras:

- OSV / GitHub Advisory for C/C++ dependencies you vendored
- `cmake --graphviz` / SBOM from the lock (CycloneDX extra)
- Pin FetchContent and wraps

Do not copy an OS generative-AI rule into CMake.

------------------------------------------------------------------------
9. QUALITY CHECKS (THE PROJECT)
------------------------------------------------------------------------

Every PR (CMake project):

```text
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release   # or multi-config
cmake --build build --target all
ctest --test-dir build --output-on-failure
```

Meson:

```text
meson setup build
meson compile -C build
meson test -C build
```

Must-haves (ecosystem)

- Out-of-source build
- Documented dialect via CMake/Meson language standard, not a
  README-only hope
- `.pc` and/or CMake package for a library
- SONAME / VERSION declared for a shared library
- LICENSE / SPDX
- Pinned FetchContent / wraps / vcpkg baseline if used

Common stalls

- In-source builds that dump `*.o` on the user
- `Cflags: -Werror` in a public `.pc`
- Unpinned git submodules
- Public headers that require a private include path

Not this pack:

- clang-format / `-Werror` / sanitizers → Language
- `build-essential` / Xcode / VS → OS

------------------------------------------------------------------------
10. COMPOSING WITH OTHER PACKS
------------------------------------------------------------------------

Hosted C library:

  Language (C) + this pack + OS (shared + one carve-out)

CMake vs Meson: pick **one** as the source of truth. A second
generated file (Meson wrapping CMake, or a Makefile that calls
CMake) is fine; two handwritten graphs that drift are not.

OS `install` prefix is not this pack. `GNUInstallDirs` is.

------------------------------------------------------------------------
11. QUICK OFFICIAL LINK LIST
------------------------------------------------------------------------

CMake
https://cmake.org/cmake/help/latest/
https://cmake.org/cmake/help/latest/manual/cmake-packages.7.html

Meson
https://mesonbuild.com/

pkg-config
https://www.freedesktop.org/wiki/Software/pkg-config/

Extras
https://vcpkg.io/
https://docs.conan.io/

Sister packs
./c-language-policy.md
./c-os-policy.md
./README.md

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.0.0 | Initial ecosystem pack: CMake common contract, Meson alternative, pkg-config/CMake packages, soversion, vcpkg/Conan extras |
