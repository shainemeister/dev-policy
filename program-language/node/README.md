---
title: "Node.js development policy packs"
description: Modular language, ecosystem, and OS policy maps for Node.js. Security and trusted modules over feature sprawl. Compose packs; do not merge them.
version: "1.0.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - node-language-policy.md
  - node-ecosystem-policy.md
  - node-os-policy.md
  - sources.yaml
last_updated: "2026-08-29"
---

# Node.js development policy packs

Curated maps of **what each layer actually checks**. Not tutorials. Not
product law for any one application.

Three axes. Compose packs; do not merge them. Language and ecosystem
are **OS-agnostic**. OS tools and ship formats live in **carve-outs**
(Debian, Arch, macOS, Windows). Same shape as
[python](../python/README.md): **security over available features**,
**trusted libraries** via an admission bar — not a rotting npm
allowlist.

```text
                 LANGUAGE                         ECOSYSTEM                        OS
                 (what the code is)               (how the project lives)          (how it lives on a system)
Node.js          node-language-policy.md          node-ecosystem-policy.md         node-os-policy.md
                                                                                   Debian | Arch | macOS | Windows
```

**Role:** working memory for humans and agents. Cite official manuals;
do not treat this folder as a substitute for the Node.js docs, the
npm CLI docs, or an OS packaging guide.

npm's module universe is large. A new `dependencies` entry is a
supply-chain decision. Node **builtins** (`node:fs`, `node:crypto`,
`fetch`) first. Lock and audit everything else. Install scripts are
untrusted by default. Do **not** treat this folder as a list of
blessed packages (`lodash`, `express`, `left-pad`). The **bar**
lives here; the **names** live in each product's lockfile.

Last verified against nodejs.org, npm docs, and OS installer docs as
of 2026-08-29.

------------------------------------------------------------------------
How to compose
------------------------------------------------------------------------

Always take **Language**. Add **Ecosystem** when there is a
`package.json` or a registry identity. Add **OS (shared half)**
whenever a `node` binary must run. Add **exactly one OS carve-out**
per ship format.

| Deliverable | Language | Ecosystem | OS |
|-------------|----------|-----------|-----|
| Hosted library or app (any dev OS) | yes | yes | shared + developer host |
| Same project, unpublished | yes | yes (skip npm publish) | shared + developer host |
| Debian `.deb` | yes | yes | Debian |
| Arch `.pkg.tar.zst` | yes | yes | Arch |
| macOS app / Homebrew formula | yes | yes | macOS |
| Windows `.exe` / MSI | yes | yes | Windows |

Do **not** apply the Debian carve-out to an MSI. Do **not** `npm
install -g` into a distro-managed prefix as the ship path. Do **not**
apply ESLint to `debian/rules` as if it were Debian Policy.

Hosted libraries and applications only. Deno, Bun, browsers-only, and
Electron as a *ship format* are out of scope until a later revision
(Electron is an extra runtime on top of Node).

------------------------------------------------------------------------
Conflict resolution
------------------------------------------------------------------------

| Object | Who owns contents | Who owns placement | Who owns the queue |
|--------|-------------------|--------------------|--------------------|
| Source text, `eval`, `node:crypto` | Language | — | CI / code review |
| ESLint / Prettier | Language extra | CI / `eslint.config` | CI |
| `package.json` identity, `engines` | — | Ecosystem | npm or the git host |
| `package-lock.json` | — | Ecosystem | CI (`npm ci`) |
| Third-party import | Language (how you call it) | Ecosystem (**trust bar**) | npm + advisory DBs |
| License | — | Ecosystem (`license` field) | OS carve-out |
| Advisories | — | Ecosystem (`npm audit`) | OS tracker if any |
| `node` / `npm` **install** | — | OS | OS package manager |
| Distro Node lag | — | OS carve-out | OS suite |
| Install / postinstall scripts | — | Ecosystem (deny by default) | npm |
| `/usr` vs Homebrew vs Program Files | — | OS carve-out | OS packager |

Hard rules:

1. One `engines.node` per package. Ship on **LTS**, not Current,
   unless you are testing Current on purpose.
2. ESLint `eslint:all` is Clippy restriction. Cherry-pick. Do not
   call it ECMA-262.
3. Language and ecosystem packs do **not** require apt, pacman,
   Homebrew, or the nodejs.org Windows MSI.
4. Distro `nodejs` lag is the OS pack.
5. One payload OS per artifact. Do not import Debian NEW into
   pacman, Homebrew, or MSI.
6. **Builtins first.** A third-party module is allowed only after it
   passes the Ecosystem **trust bar**. Features you could get from
   npm do not outrank that bar.
7. Every CI/ship install is **lockfile-strict** (`npm ci`) with
   **lifecycle scripts off** unless a named package is allowlisted
   (`ignore-scripts` / npm 12 `allowScripts`).
8. `npm audit` is the advisory gate. A known high/critical in
   production deps is a stall.
9. Extra registries (`registry=` other than registry.npmjs.org) are
   denied unless named, documented, and under your control.
10. Git dependencies (`git+https://`) are a supply-chain extra, not
    a default. Prefer a registry tarball with integrity.
11. Do not copy npm yank into apt. Do not copy an OS generative-AI
    rule into `npm publish`.

------------------------------------------------------------------------
Official map vs audit extra vs trust bar
------------------------------------------------------------------------

- **Official map** — Node.js API docs, release schedule, npm CLI
  (ci, audit, package-lock), npmjs.com policies, trusted publishing.
- **Trust bar** (this repo's security-over-features rule, labeled) —
  builtins first; new deps documented; lockfile; scripts denied;
  `npm audit`; no extra registry by default; trusted publishing when
  *you* publish.
- **Audit extra** — ESLint, Prettier, `npm audit signatures`,
  Socket/Snyk, SBOM, pnpm/yarn as lock *tools* (the lock *contract*
  is still a committed lockfile).

------------------------------------------------------------------------
What each pack is
------------------------------------------------------------------------

[node-language-policy.md](node-language-policy.md)

What Node requires of the *code*: `engines.node`, builtins,
crypto/http/child_process contracts, tests. Not npm. Not apt.

[node-ecosystem-policy.md](node-ecosystem-policy.md)

How a project *lives*: `package.json`, lockfile, npm, **trusted-module
bar**, install-script policy, `npm audit`.

[node-os-policy.md](node-os-policy.md)

How a `node` binary exists on a system. Shared: official binaries vs
distro. Carve-outs: Debian, Arch, macOS, Windows.

------------------------------------------------------------------------
Retrieving updates from official sources
------------------------------------------------------------------------

[sources.yaml](sources.yaml) /
[../../scripts/check_sources.py](../../scripts/check_sources.py)
(`--family program-language/node`). On `DRIFT`, bite-sized rule then
bump the pin.

Current pins as of 2026-08-29:

- **Node.js 24** Active LTS (`24.20.0`). **26** is Current (LTS
  October 2026) — not the ship bar.
- New projects: `engines.node = ">=20"` minimum; CI on **24**.
- npm **12** lifecycle-script limits / `allowScripts` — treat
  third-party install scripts as denied unless listed.

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.0.0 | Initial three-pack split. Security-over-features: trusted-module bar, lockfile + ignore-scripts, npm audit. OS carve-outs Debian/Arch/macOS/Windows. |
