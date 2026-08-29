---
title: "Node.js OS Policy"
description: Curated map of how Node.js lives on Debian, Arch, macOS, and Windows — interpreters, official vs distro binaries, ship formats. Not ESLint and not npm.
version: "1.0.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - README.md
  - node-language-policy.md
  - node-ecosystem-policy.md
last_updated: "2026-08-29"
---

# Node.js OS Policy

Reference pack for **how a hosted Node.js project lives on an
operating system**: which `node` binary you run, official vs distro
packages, and how each OS ships the result.

**Role:** curated map (working memory). **Not** `node:crypto` —
[node-language-policy.md](node-language-policy.md).
**Not** the trust bar or `npm audit` —
[node-ecosystem-policy.md](node-ecosystem-policy.md).

Last verified against nodejs.org install docs and OS packaging as of
2026-08-29.

Shared half plus four carve-outs. Apply **one** carve-out per ship
format.

------------------------------------------------------------------------
0. LAYERING
------------------------------------------------------------------------

This pack owns:

- How Node.js / npm are **installed**
- Official binaries vs distro `nodejs`
- nvm / fnm / volta as *tool extras* for fetching upstream
- Ship-format placement
- OS security updates of *the interpreter* and of distro `node-*`
  packages

This pack does **not** own:

- `engines.node` dialect → Language
- lockfile, trust bar, install scripts → Ecosystem

Hard rules:

1. Distro `nodejs` may lag LTS 24. That is **this pack**.
2. Never `npm install -g` into a distro prefix as the *app* ship
   path. A venv-analog is a local prefix or an OS package.
3. One payload OS per artifact.
4. Do not import Debian NEW into pacman, Homebrew, or MSI.
5. Mixing apt `node-foo` and npm `foo` in `/usr` is an integrity
   fail (same idea as PEP 668).
6. ESLint is never an OS packaging check.

------------------------------------------------------------------------
1. FOUNDATIONAL DOCUMENTS (SHARED)
------------------------------------------------------------------------

Downloads
https://nodejs.org/en/download
https://github.com/nodejs/node#building-nodejs

Release schedule
https://github.com/nodejs/Release
https://nodejs.org/en/about/previous-releases

Docker official images (CI extra, not a ship OS)
https://github.com/nodejs/docker-node

------------------------------------------------------------------------
2. INTERPRETER (SHARED)
------------------------------------------------------------------------

Development and CI: official **Node 24 LTS** (nodejs.org, or
`fnm`/`nvm` extra pointing at that line). Record `node -v` and
`npm -v` in CI.

There is no PEP 668 for Node, but the same idea holds: the OS
package manager owns `/usr`; npm owns a **project** `node_modules`
or a user prefix. Do not write into `/usr/lib/nodejs` from `npm
install`.

Corepack (ships with Node) can pin Yarn/pnpm versions. Extra. npm
bundled with the Node line is the default.

------------------------------------------------------------------------
DEBIAN CARVE-OUT — section 3
------------------------------------------------------------------------

https://wiki.debian.org/Javascript
https://packages.debian.org/stable/nodejs

- `nodejs` from apt **lags** upstream on stable. A `.deb` that must
  build on Trixie sets `engines.node` to that version or uses a
  documented backport/NodeSource — NodeSource is an extra repo;
  treat it like an extra index (document, pin).
- App as `.deb`: `dh-nodejs` / `pkg-js-tools`, depend on
  `nodejs` and Debian `node-*` packages when they exist. No-network
  `debian/rules`: the Ecosystem lock must already contain tarballs
  (npm cache / `npm ci --offline` after a prepared cache).
- Do not `npm install -g` in maintainer scripts.

------------------------------------------------------------------------
ARCH CARVE-OUT — section 4
------------------------------------------------------------------------

https://wiki.archlinux.org/title/Node.js

- `extra/nodejs` tracks upstream closely (often current major).
- `npm` may be a split package. pacman `nodejs-*` vs npm: pick one
  per name in `/usr`.
- PKGBUILD: `depends=(nodejs)`, npm offline in `build()` from
  `source=` tarballs / committed lock.

AUR is not official Arch.

------------------------------------------------------------------------
MACOS CARVE-OUT — section 5
------------------------------------------------------------------------

https://nodejs.org/en/download

- Official pkg/binary from nodejs.org, or Homebrew `node@24`.
  Apple `/usr/bin` has no Node.
- Ship host: Apple Silicon.
- Signing/notarization extra for a bundled `.app` (packagers like
  `pkg` / electron-builder still pass the Ecosystem trust bar).

------------------------------------------------------------------------
WINDOWS CARVE-OUT — section 6
------------------------------------------------------------------------

https://nodejs.org/en/download

- Official MSI/binary from nodejs.org. winget/chocolatey extras:
  pin which you CI.
- Native addons: MSVC Build Tools + Python for `node-gyp`. Prefer
  prebuilt binaries (Ecosystem §4.2).
- `node` / `npm` on PATH after the official installer. Do not assume
  Unix layout.

------------------------------------------------------------------------
7. QUALITY CHECKS (THIS OS)
------------------------------------------------------------------------

```text
node -v
npm -v
```

Debian: chroot no-network; `nodejs` Depends; no global npm in
`postinst`.

Arch: pacman XOR npm per `/usr` name.

macOS: official or Homebrew `@24`, not a random nvm in CI unless
documented.

Windows: official installer; wheels/prebuilds not forced `node-gyp`
on the user.

------------------------------------------------------------------------
8. COMPOSING
------------------------------------------------------------------------

App with project `node_modules`:

  Language + Ecosystem + this pack **shared** + host carve-out

Debian `.deb`:

  same + **Debian** (apt nodejs; lock may collapse into
  `Depends: node-*`)

------------------------------------------------------------------------
9. QUICK OFFICIAL LINK LIST
------------------------------------------------------------------------

https://nodejs.org/en/download
https://github.com/nodejs/Release
https://wiki.debian.org/Javascript
https://packages.debian.org/stable/nodejs
https://wiki.archlinux.org/title/Node.js

Sister packs
./node-language-policy.md
./node-ecosystem-policy.md
./README.md

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.0.0 | Initial OS pack: Node 24 LTS; Debian, Arch, macOS, Windows carve-outs |
