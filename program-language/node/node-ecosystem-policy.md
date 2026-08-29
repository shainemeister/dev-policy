---
title: "Node.js Ecosystem Policy"
description: Curated map of how a Node.js project lives — package.json, lockfile, npm, trusted-module bar, install scripts, npm audit. Security over feature sprawl.
version: "1.0.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - README.md
  - node-language-policy.md
  - node-os-policy.md
last_updated: "2026-08-29"
---

# Node.js Ecosystem Policy

Reference pack for **how a hosted Node.js project lives**: packaging
metadata, lockfiles, the npm registry, **which third-party modules
may be depended on**, and install-script policy.

**Role:** curated map (working memory). **Not** L4 for any one app.
**Not** `node:crypto` — that is
[node-language-policy.md](node-language-policy.md).
**Not** apt/pacman/Homebrew/nodejs.org installers — that is
[node-os-policy.md](node-os-policy.md).

Last verified against npm CLI and npmjs.com docs as of 2026-08-29.

npm's module universe is large. This pack **enforces a trusted-module
bar** and **prefers security over available features**. It does
**not** ship a named allowlist of npm packages (those rot). It ships
the **admission rules**. The names that passed live in *your*
lockfile.

npm is the default installer. **pnpm** and **Yarn** are lock/install
*tools* (extras) that still must emit a committed lock this pack can
audit. **Bun's** npm-compatible installer is not this pack's default.

------------------------------------------------------------------------
0. LAYERING
------------------------------------------------------------------------

This pack owns:

- `package.json` identity (`name`, `version`, `engines`, `license`)
- Dependency declaration and **trust bar**
- `package-lock.json` (lockfileVersion 2+)
- npm registry rules, yank, trusted publishing
- **Lifecycle scripts** (deny third-party by default)
- `npm audit` as the advisory gate

This pack does **not** own:

- Builtin API contracts → Language
- Distro `nodejs` / nvm → OS

------------------------------------------------------------------------
1. FOUNDATIONAL DOCUMENTS
------------------------------------------------------------------------

npm CLI
https://docs.npmjs.com/cli
`npm ci`:
https://docs.npmjs.com/cli/v10/commands/npm-ci
`npm audit`:
https://docs.npmjs.com/cli/v10/commands/npm-audit
package.json:
https://docs.npmjs.com/cli/configuring-npm/package-json
package-lock:
https://docs.npmjs.com/cli/v10/configuring-npm/package-lock-json

npmjs.com
https://www.npmjs.com/policies
Trusted publishing:
https://docs.npmjs.com/trusted-publishers

Node security
https://github.com/nodejs/security-wg
https://githubadvisories.github.com  (npm ecosystem)

------------------------------------------------------------------------
2. PACKAGE.JSON IDENTITY
------------------------------------------------------------------------

Must-haves:

- `name`, `version`
- `engines.node` (Language owns the dialect; this field stores it)
- `license` (SPDX)
- `dependencies` / `devDependencies` — every direct entry has
  passed §4
- `"private": true` if it must not hit the registry

Should: `repository`, `files` (don't publish tests/secrets),
`type` (`module` or omit for CJS).

`optionalDependencies` still install (and may run scripts). Treat
them as dependencies for the trust bar. `peerDependencies` are a
contract with the consumer; they still need a lock in *this* repo
for CI.

Do not use `*` or `latest` as a version. Caret ranges in
`package.json` are acceptable **only** because the **lockfile** pins
the tree. Without a lock, a caret is an unpinned install.

------------------------------------------------------------------------
3. LOCKFILE AND INSTALL
------------------------------------------------------------------------

https://docs.npmjs.com/cli/v10/commands/npm-ci
https://docs.npmjs.com/cli/v10/configuring-npm/package-lock-json

**Every CI and ship install is lockfile-strict.**

```text
npm ci --ignore-scripts
```

`npm ci` fails if `package.json` and the lock disagree. That is the
point. Commit `package-lock.json` (lockfileVersion **2 or 3**). Apps
always; libraries lock their own CI graph too so `npm audit` has a
tree.

**Lifecycle scripts:** third-party `preinstall` / `install` /
`postinstall` are the usual malware path. This pack's default:

- CI: `--ignore-scripts`
- npm 12+: third-party install scripts blocked unless listed in
  `allowScripts` (or equivalent). Do **not**
  `--dangerously-allow-all-scripts`.
- `.npmrc` in the repo: `ignore-scripts=true` unless you maintain an
  explicit allowlist.

Your **own** `prepare` / `test` scripts still run via `npm test` /
`npm run`. That is not a license to enable all dependency scripts.

Integrity: the lockfile's `integrity` hashes are npm's analog of
pip `--require-hashes`. Do not delete them. Do not `npm install`
without a lock on a release job.

Git/URL dependencies (`git+https://`, `github:`) skip the usual
tarball integrity story and can overwrite config. Prefer a published
tarball. If you must git-pin, pin a **full commit SHA**, not a
branch.

------------------------------------------------------------------------
4. TRUSTED-MODULE BAR (SECURITY OVER FEATURES)
------------------------------------------------------------------------

This section is the expansion this repo exists for. It is **this
pack's bar**, not an npm Policy clause. Labeled as such.

A **trusted module** is a third-party package you have admitted.
Node builtins are Language, not "trusted modules." Distro packages
of Node libs (`node-foo` on Debian) are an OS carve-out of *the same
project*.

### 4.1 Builtins first

Before adding an npm package, name the builtin you are rejecting and
why.

| Job | Builtin first | Third-party only after the bar |
|-----|---------------|--------------------------------|
| HTTP client | `fetch` / `node:https` | `axios` / `got` |
| Test runner | `node:test` | jest / vitest / mocha |
| CLI argv | `util.parseArgs` (Node 18.3+) | commander / yargs |
| Hash / HMAC / random | `node:crypto` | (almost never) |
| Path / URL | `node:path` / `node:url` | — |
| lodash-style helpers | native (`Object.hasOwn`, `Array.flat`, `structuredClone`) | lodash |
| Process spawn | `node:child_process` | execa |

"The third-party API is nicer" is **not** enough. "The builtin
cannot do X safely" is.

### 4.2 Admission checklist (every new direct dep)

Record the answers in the PR. All must hold:

1. **Name** — exact npm name. Check typosquats (`lodahs`,
   `event-stream` lookalikes, scoped vs unscoped confusion).
2. **Purpose** — one sentence. No "might need later."
3. **Builtin gap** — §4.1.
4. **Maintained** — recent release or security commit; not a single
   0.0.1.
5. **License** — SPDX you can ship.
6. **Advisories** — `npm audit` clean for production at the lock
   pin, including transitives.
7. **Install scripts** — none, or listed in `allowScripts` with a
   reason. A dep whose only job is a postinstall binary is a
   supply-chain surface.
8. **Provenance extra** — prefer Trusted Publishing / attestations
   on *their* uploads. A brand-new anonymous package fails.
9. **Native addons** (`node-gyp`) — need a compiler on the OS
   carve-out; prefer prebuilds from the same project. Review
   `binding.gyp`.
10. **Transitives** — you own them. A tiny direct dep that pulls
    forty packages fails unless you accept each (or `overrides`
    to a tree you did accept).

Do **not** add a dep to keep options open. Features lose.

### 4.3 What this bar is not

- Not a frozen list of `express`, `react`, `lodash`. Those can pass
  in a product; they are not blessed here.
- Not download counts.
- Not "it is in the Node monorepo."
- Not `npm audit` with `--audit-level=none`.

If a dep fails later (advisory, hijack, abandoned): pin a fixed
release via `overrides` if needed, or **remove the feature**. Do not
`npm audit --force` as ritual.

------------------------------------------------------------------------
5. ADVISORIES
------------------------------------------------------------------------

https://docs.npmjs.com/cli/v10/commands/npm-audit

```text
npm ci --ignore-scripts
npm audit --omit=dev --audit-level=high
```

Fail CI on high/critical in **production** deps. Dev-only findings
are tracked, not ignored silently. `npm audit signatures` is an
extra (sigstore attestations).

The GitHub Advisory Database (ecosystem npm) is the interchange.
OSV extra.

Yank does not update your lock. You do.

------------------------------------------------------------------------
6. NPM STORE
------------------------------------------------------------------------

https://www.npmjs.com/policies
https://docs.npmjs.com/trusted-publishers

Default registry: `https://registry.npmjs.org/`. Extra registries
enable dependency confusion. **Denied** unless the registry is
named, under your control, and the lock records resolved URLs.

Publish: **Trusted Publishing** (OIDC from GitHub/GitLab) over
long-lived tokens. Classic tokens were revoked (2025–2026). Granular
tokens expire. CI should not store `NODE_AUTH_TOKEN` when OIDC works.

https://docs.npmjs.com/trusted-publishers

Do not import npm names into Debian binary names. Do not import yank
into apt.

------------------------------------------------------------------------
7. INSTALL TOOLS (OFFICIAL VS EXTRA)
------------------------------------------------------------------------

| Tool | Status | Notes |
|------|--------|--------|
| `npm ci` | official (ships with Node) | Lockfile-strict |
| pnpm | extra | Frozen lockfile; `allowBuilds` for scripts |
| Yarn | extra | `enableScripts: false` default on modern Yarn |
| bun | extra / not this pack's runtime | Installer only if lock is still auditable |
| nvm / fnm | OS extra | How you *get* Node, not the lock |

------------------------------------------------------------------------
8. QUALITY CHECKS (THE PROJECT)
------------------------------------------------------------------------

Every PR:

```text
npm ci --ignore-scripts
npm audit --omit=dev --audit-level=high
npm test
```

Must-haves: `package.json` with `engines` and SPDX; committed lock;
every direct dep admitted; scripts denied except allowlist;
`npm audit` production high/critical clean; default registry only.

Common stalls: `npm install foo` in README as the story; no lock;
`--dangerously-allow-all-scripts`; git+http deps; `postinstall` that
downloads more code.

------------------------------------------------------------------------
9. COMPOSING
------------------------------------------------------------------------

Hosted app:

  Language + this pack + OS (shared + one carve-out)

Debian `.deb` may install `node-foo` from apt **instead of** npm
for those packages. Do not then npm-install the same name over the
distro copy.

------------------------------------------------------------------------
10. QUICK OFFICIAL LINK LIST
------------------------------------------------------------------------

https://docs.npmjs.com/cli/v10/commands/npm-ci
https://docs.npmjs.com/cli/v10/commands/npm-audit
https://docs.npmjs.com/cli/v10/configuring-npm/package-lock-json
https://docs.npmjs.com/trusted-publishers
https://www.npmjs.com/policies

Sister packs
./node-language-policy.md
./node-os-policy.md
./README.md

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.0.0 | Initial ecosystem pack: lockfile + ignore-scripts, npm audit, trusted-module admission bar, builtins-first, extra registries denied |
