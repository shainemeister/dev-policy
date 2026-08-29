---
title: "C/C++ Language Policy"
description: Curated map of what C and C++ require of the code — ISO dialect, UB, compiler warnings, clang-format, tests. Not CMake and not OS packaging.
version: "1.0.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - README.md
  - c-ecosystem-policy.md
  - c-os-policy.md
last_updated: "2026-08-29"
---

# C/C++ Language Policy

Reference pack for **what the code is** when it is hosted C, C++, or
both: ISO dialect, undefined behavior, compiler diagnostics,
clang-format, and tests.

**Role:** curated map (working memory). **Not** L4 for any one
library. **Not** CMake/Meson/pkg-config — that is
[c-ecosystem-policy.md](c-ecosystem-policy.md).
**Not** apt, pacman, Xcode, or MSVC *install* — that is
[c-os-policy.md](c-os-policy.md).

Last verified against WG14, WG21, GCC, and Clang documents as of
2026-08-29.

This pack has two halves that must not be collapsed:

1. **C** — ISO/IEC 9899. Sections 3–4.
2. **C++** — ISO/IEC 14882. Sections 5–6.

Shared gates (warnings, format, tests, sanitizers) are sections 2
and 7–8. A C-only library skips the C++ half. A C++ library that
exports a C API uses **both**.

------------------------------------------------------------------------
0. LAYERING
------------------------------------------------------------------------

This pack owns:

- ISO C and ISO C++ dialect (`-std=`, `/std:`)
- Undefined / unspecified / implementation-defined behavior as
  *language* facts
- Compiler *warning groups* (`-Wall`, `-Wextra`, `/W4`) as what gcc,
  clang, and MSVC actually emit
- clang-format (default LLVM style)
- clang-tidy as a **linter extra**, not a compiler
- Sanitizers (ASan, UBSan, TSan, MSan) as **audit extras**
- What a test program must show (the test *exists and runs*)

This pack does **not** own:

- CMakeLists, meson.build, .pc files, soversion
  → Ecosystem
- How gcc/clang/cl.exe is installed, SDK, `/usr` vs Program Files
  → OS pack
- CERT C, MISRA, AUTOSAR as if they were ISO
  → labeled extras or out of scope

Compose a hosted library as:

  this pack (C and/or C++ half)
  + Ecosystem + OS (shared + one carve-out)

------------------------------------------------------------------------
1. FOUNDATIONAL DOCUMENTS
------------------------------------------------------------------------

ISO C (WG14)
https://www.open-std.org/JTC1/SC22/wg14/
Projects / drafts:
https://www.open-std.org/JTC1/SC22/wg14/www/projects
C23 (ISO/IEC 9899:2024): public draft **N3220**
https://www.open-std.org/JTC1/SC22/wg14/www/docs/n3220.pdf
`__STDC_VERSION__` for C23 is `202311L`.

ISO C++ (WG21)
https://isocpp.org/std/status
Working draft (not a substitute for the paid standard):
https://github.com/cplusplus/draft
C++23 is published (ISO/IEC 14882:2024). C++26 technical work was
completed mid-2026; DIS/publication is not this pack's ship bar.

Compiler language-status (what actually implements the dialect):

- GCC C++ status
  https://gcc.gnu.org/projects/cxx-status.html
- GCC C status
  https://gcc.gnu.org/projects/c-status.html
- Clang C++ status
  https://clang.llvm.org/cxx_status.html
- Clang C status
  https://clang.llvm.org/c_status.html
- MSVC `/std` (OS pack installs the compiler; this pack owns the
  *flag*)
  https://learn.microsoft.com/en-us/cpp/build/reference/std-specify-language-standard-version

clang-format
https://clang.llvm.org/docs/ClangFormat.html
https://clang.llvm.org/docs/ClangFormatStyleOptions.html

clang-tidy
https://clang.llvm.org/extra/clang-tidy/

Sanitizers (Clang)
https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html
https://clang.llvm.org/docs/AddressSanitizer.html
GCC:
https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html

ISO text is paywalled. Public drafts and compiler status pages are
what this map cites. Do not dump the standard into the pack.

------------------------------------------------------------------------
2. SHARED GATES (C AND C++)
------------------------------------------------------------------------

**Dialect pin (this pack's default for a new hosted project):**

| Language | Prefer | Fallback if the claimed compiler lacks it |
|----------|--------|-------------------------------------------|
| C | `-std=c23` (or `/std:c17` + documented C23 bits) | `-std=c17` |
| C++ | `-std=c++23` | `-std=c++20` |

Pick **one** dialect per library. Record it in the build file
(Ecosystem) so every TU agrees. Distro gcc that cannot do C23/C++23
is an **OS** constraint: lower the dialect or use a newer compiler
the OS carve-out allows. Do not silently compile as gnu2x in CI and
gnu89 on the buildd.

GNU extensions (`gnu17`, `gnu++20`) are implementation extras, not
ISO. If you need them, document why. A library with a public header
should compile as ISO C or ISO C++ for consumers.

**Compiler warning groups** (not ISO; this is what the compilers
ship):

| Family | Baseline (map) | CI extra |
|--------|----------------|----------|
| gcc / clang | `-Wall -Wextra` | `-Werror` and extra `-W…` |
| MSVC | `/W4` | `/WX` |

`-Wall` is not "all warnings." Do not claim it is. `-Werror` /
`/WX` turn diagnostics into failures; that is a **CI extra**, not
gcc's default.

**clang-format**

Default `-style=LLVM` (clang-format's default). `clang-format
--dry-run -Werror` is the language consistency gate, analogous to
`cargo fmt --check`.

A `.clang-format` that only sets `Language` / `Standard` is fine. A
file that fights LLVM (Google, GNU, WebKit, BasedOnStyle with a
custom ColumnLimit) is a **house fork**. Document it. Do not call it
ISO.

**Tests**

This pack requires that behavior you claim has a test that runs.
How you *drive* tests (CTest, meson test, a shell script) is
Ecosystem. `assert` in a test program is language-level. A library
with no tests is a language stall, not an OS one.

------------------------------------------------------------------------
3. C HALF — DIALECT
------------------------------------------------------------------------

C23 is current ISO C (9899:2024). C17 remains the portable fallback.
C11 is old for a *new* hosted library. C99/C89 only for documented
inter-op with an ancient consumer.

Bite-sized C23 facts this map cares about (not a dump):

- `bool`, `true`, `false` in `<stdbool.h>` become ordinary keywords
  in C23; code that `#define bool` will break.
- `typeof` / `typeof_unqual`, `#embed`, bit-precise integers
  (`_BitInt`), `nullptr`.
- `__STDC_VERSION__ == 202311L`.

Public headers of a C library:

- Compilable as C with the claimed `-std=`.
- If also included from C++, wrap with `extern "C"` in the header
  (the C++ half consumes that; this half provides it).
- Do not require C++ to parse a C public header.

`restrict`, `_Atomic`, and VLA: C99/C11 features. VLAs are optional
in C11+ and a common portability hazard (MSVC). A hosted library
that needs MSVC consumers treats VLA as **off**. That is language
portability, not the Windows carve-out inventing a dialect.

------------------------------------------------------------------------
4. C HALF — UNDEFINED BEHAVIOR
------------------------------------------------------------------------

The C abstract machine leaves many operations undefined. Compilers
will not reliably diagnose them. This pack does not list every UB
clause.

Language gates that actually bite:

- Use-after-free, buffer overflow, signed overflow, invalid
  `free` — sanitizers extra, not `-Wall`.
- Strict aliasing: `-fno-strict-aliasing` is a **house** flag, not
  ISO. Prefer `memcpy` / `union` as the standard allows.
- Sequence points / unsequenced side effects: C17/C23 wording.
- Data races: C11 threads + atomics, or "don't share." TSan extra.

`gets` is gone. `strncpy` is not a bounds-checked sprintf. Prefer
the Annex K extras only if the implementation has them; they are
optional. Do not treat Annex K as required ISO.

------------------------------------------------------------------------
5. C++ HALF — DIALECT
------------------------------------------------------------------------

C++23 is current published ISO C++. C++20 is the portable fallback
for new libraries. C++17 is old for a *new* hosted library unless
MSRV (Ecosystem/OS) forces it. C++14/C++11 only with a documented
consumer.

C++26 is **not** the ship bar yet (technical work complete;
publication pending as of 2026). Do not require `-std=c++26` in this
pack.

Bite-sized C++20/23 facts this map cares about:

- Concepts, ranges, `constexpr` expansion, modules (C++20). Modules
  are ISO; toolchain support still varies — treat a *public* module
  interface as extra until all claimed compilers implement it.
  Headers remain the portable public surface.
- `std::expected` (C++23), `std::mdspan`, `std::print`.
- Do not `#define` around missing `std::format` if you claim C++23.

Public headers of a C++ library:

- Self-contained (include what you use).
- No `using namespace` at namespace scope in a header.
- ABI: a stable C++ library either ships in-line with the
  application or versions SONAME (Ecosystem + OS). Inline namespaces
  / ABI tags are language tools for that.

Linking C++ with C: the C API is `extern "C"`. Exceptions must not
cross that boundary unless both sides agree (they almost never
should).

------------------------------------------------------------------------
6. C++ HALF — UNDEFINED BEHAVIOR AND SAFETY
------------------------------------------------------------------------

C++ has all of C's memory UB plus object lifetime, `const`, and
data races in the memory model.

Language facts (not MISRA):

- A dangling reference/pointer is UB. Compilers may warn
  (`-Wdangling-gsl` extra); they will not catch all of it.
- Uninitialized reads: `-Wuninitialized` helps; UBSan extra.
- `new`/`delete` in application code is not *forbidden by ISO*.
  RAII (unique_ptr, containers) is the usual hosted style. A
  `forbid raw new` clang-tidy check is **extra**.
- Unsigned wrap is defined; signed overflow is UB (same as C).
- One Definition Rule (ODR): headers that define non-inline
  functions or globals are an ODR time bomb.

Exceptions and RTTI are ISO. Disabling them (`-fno-exceptions`) is
a product/OS embedded bar, not this hosted pack's default.

------------------------------------------------------------------------
7. LINTERS AND SANITIZERS (EXTRAS)
------------------------------------------------------------------------

**clang-tidy** is not the compiler. Enabling `*` is like Clippy
`restriction`: do not. Cherry-pick check groups
(`bugprone-*`, `clang-analyzer-*`, `performance-*`). A
`.clang-tidy` file in the repo is the extra's config.

https://clang.llvm.org/extra/clang-tidy/checks/list.html

**Sanitizers** (gcc/clang; MSVC has ASan in recent VS — OS pack
installs it):

| Tool | What it catches | When |
|------|-----------------|------|
| UBSan | UB the compiler can instrument | extra, every PR if the toolchain has it |
| ASan | heap/stack overflow, UAF | extra, test runs |
| TSan | data races | extra, if you have threads |
| MSan | uninitialized (Clang, extra runtime) | extra |

Do not ship production binaries with ASan linked unless that is the
product. Do not run sanitizers as an OS package build requirement
(Debian buildds, etc.) — that is a language extra in *project* CI.

**CERT C / MISRA / AUTOSAR** are industry extras, not ISO. Do not
import them into this pack as if they were `-std=`. If a product
needs them, that is product law.

------------------------------------------------------------------------
8. QUALITY CHECKS (THE CODE)
------------------------------------------------------------------------

Official-ish language gates (every PR):

```text
clang-format --dry-run -Werror <sources>   # or cmake clang-format extra
# compile with the claimed -std= and -Wall -Wextra (or /std /W4)
# run the project's tests
```

**CI extra:**

```text
# gcc/clang
-Werror
-fsanitize=address,undefined   # test build only
clang-tidy -p build            # cherry-picked checks
```

Must-haves (language)

- Compiles as the claimed ISO dialect on the claimed compilers
- Public C headers compile as C; C++ headers compile as C++
- `extern "C"` on C APIs consumed by C++
- clang-format check clean (LLVM or a documented house file)
- Tests exist for claimed behavior

Strong expectations

- `-Wall -Wextra` / `/W4` clean, or documented pragmas *local* to
  the lie
- No VLAs if MSVC is a claimed consumer
- No `using namespace` in C++ headers

Common language rejects / stalls

- GNU dialect in public headers with no ISO fallback
- `-Werror` presented as ISO
- clang-tidy `*` as a must-have
- C++26 as a ship requirement in 1.0.0 of this pack
- Mixing C++ exceptions across a C API

Not this pack:

- CMake `install()`, `.pc`, SONAME → Ecosystem / OS
- `build-essential`, Xcode CLT, VS Build Tools → OS
- vcpkg/Conan → Ecosystem extra

------------------------------------------------------------------------
9. WHAT THIS PACK EXPLICITLY IS NOT
------------------------------------------------------------------------

Not the ISO PDFs.

Not CMake or Meson.

Not CERT/MISRA as default law.

Not freestanding, kernel, or CUDA.

Not how to *install* gcc.

------------------------------------------------------------------------
10. COMPOSING WITH OTHER PACKS
------------------------------------------------------------------------

C library on any OS:

  this pack **C half** + Ecosystem + OS (shared + one carve-out)

C++ library:

  this pack **C++ half** (and C half if you export `extern "C"`)
  + Ecosystem + OS

Same source as a Debian `.deb` or a Windows DLL: the dialect and
warnings stay here. The linker and prefix are OS.

------------------------------------------------------------------------
11. QUICK OFFICIAL LINK LIST
------------------------------------------------------------------------

WG14 / C
https://www.open-std.org/JTC1/SC22/wg14/www/projects
https://www.open-std.org/JTC1/SC22/wg14/www/docs/n3220.pdf

WG21 / C++
https://isocpp.org/std/status
https://github.com/cplusplus/draft

GCC / Clang status
https://gcc.gnu.org/projects/c-status.html
https://gcc.gnu.org/projects/cxx-status.html
https://clang.llvm.org/c_status.html
https://clang.llvm.org/cxx_status.html

Format / tidy / sanitizers
https://clang.llvm.org/docs/ClangFormat.html
https://clang.llvm.org/extra/clang-tidy/
https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html

Sister packs
./c-ecosystem-policy.md
./c-os-policy.md
./README.md

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.0.0 | Initial language pack: C23/C17 and C++23/C++20 halves, compiler warning groups, clang-format LLVM, sanitizers/tidy labeled extras |
