---
title: "Node.js Language Policy"
description: Curated map of what Node.js requires of the code — engines, builtins, crypto/http/child_process, tests. Not npm and not OS packaging.
version: "1.0.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - README.md
  - node-ecosystem-policy.md
  - node-os-policy.md
last_updated: "2026-08-29"
---

# Node.js Language Policy

Reference pack for **what the code is** when it is hosted Node.js:
runtime version, builtin APIs, security-relevant stdlib contracts,
tests.

**Role:** curated map (working memory). **Not** L4 for any one app.
**Not** `package.json` lockfiles or npm — that is
[node-ecosystem-policy.md](node-ecosystem-policy.md).
**Not** apt, nvm-as-required, or the nodejs.org MSI — that is
[node-os-policy.md](node-os-policy.md).

Last verified against nodejs.org as of 2026-08-29.
**24** is Active LTS. **26** is Current (not the ship bar).

Security-over-features starts here: prefer **Node builtins**
(`node:crypto`, `node:fs`, `node:path`, `node:http`, `fetch`,
`node:test`) over a third-party import. Whether a third-party
package is *allowed at all* is the Ecosystem trust bar.

------------------------------------------------------------------------
0. LAYERING
------------------------------------------------------------------------

This pack owns:

- `engines.node` *meaning* (which runtime you write for)
- Builtin modules (`node:` specifier)
- Crypto, TLS, child_process, path, vm contracts
- ECMAScript dialect Node implements (not a second language pack)
- Tests that must exist (`node:test` is builtin)

This pack does **not** own:

- `dependencies`, lockfile, npm audit, install scripts → Ecosystem
- How `node` is installed → OS

------------------------------------------------------------------------
1. FOUNDATIONAL DOCUMENTS
------------------------------------------------------------------------

Node.js API
https://nodejs.org/docs/latest/api/
https://nodejs.org/docs/latest-v24.x/api/  (LTS line)

Releases
https://nodejs.org/en/about/previous-releases
https://github.com/nodejs/Release#release-schedule

`engines`
https://docs.npmjs.com/cli/v10/configuring-npm/package-json#engines

Builtins
https://nodejs.org/docs/latest/api/crypto.html
https://nodejs.org/docs/latest/api/tls.html
https://nodejs.org/docs/latest/api/child_process.html
https://nodejs.org/docs/latest/api/test.html
https://nodejs.org/docs/latest/api/globals.html  (fetch)

ESLint (**extra**)
https://eslint.org/docs/latest/

------------------------------------------------------------------------
2. RUNTIME VERSION
------------------------------------------------------------------------

Ship bar: **Node.js 24 LTS** in CI for a new hosted project.
`engines.node`: `>=20` minimum unless an OS carve-out forces lower
(then record it and test that binary). Do not require **26**
(Current) until it is LTS (scheduled October 2026).

Odd majors (25) are already EOL under the old even/odd model. Node
27+ will LTS under the new yearly schedule; that is future OS/runtime
news, not this 1.0.0 ship bar.

Use the `node:` specifier for builtins (`import fs from 'node:fs'`).
Bare `'fs'` still works; `node:` makes the dependency graph honest.

`"type": "module"` (ESM) vs CommonJS: pick one per package. Dual
packages are an Ecosystem packaging extra.

------------------------------------------------------------------------
3. BUILTIN SECURITY CONTRACTS
------------------------------------------------------------------------

**Do not**

- `eval`, `new Function`, `vm.runInNewContext` on untrusted input
- `child_process` with `shell: true` and unsanitised input
- `fs` paths from users without resolving inside a root
  (`path.normalize` is not a jail)
- `http`/`https` `rejectUnauthorized: false`
- custom crypto instead of `node:crypto` / Web Crypto
- `Math.random()` for tokens (`crypto.randomUUID` /
  `crypto.randomBytes`)
- dynamic `import()` / `require()` of attacker-controlled strings
- `Buffer` alloc from untrusted length without caps (`Buffer.alloc`
  not `Buffer.allocUnsafe` for secrets)

**Do**

- `fetch` or `node:https` with default TLS
- `node:crypto` for hashes (SHA-256+), HMAC, timing-safe equal
  (`crypto.timingSafeEqual`)
- `node:path` + explicit root prefix checks
- `node:test` / `assert` for tests until a runner passes the
  Ecosystem bar
- structuredClone / Object.hasOwn / Array.flat — **stdlib first**
  vs lodash helpers

`express` / `fastify` / `ws` are Ecosystem trust decisions. A
builtin `node:http` server is enough until the bar says otherwise.

------------------------------------------------------------------------
4. STYLE AND LINTERS (EXTRAS)
------------------------------------------------------------------------

There is no PEP 8 for JS. Language style is "don't invent a dialect."
ESLint recommended + Prettier are **extras**. `eslint:all` is not a
language requirement.

TypeScript is a **language extra** (not Node). If you use it, `tsc
--noEmit` is CI extra; `engines` still names Node, not the TS
version. `@types/*` packages still pass the Ecosystem trust bar.

------------------------------------------------------------------------
5. TESTS
------------------------------------------------------------------------

Claimed behavior has a test that runs. **`node:test`** is builtin
(Node 18+; mature on 20/24). `jest` / `vitest` / `mocha` are
third-party — Ecosystem trust bar. Security-over-features: `node:test`
until a runner is justified.

https://nodejs.org/docs/latest/api/test.html

------------------------------------------------------------------------
6. QUALITY CHECKS (THE CODE)
------------------------------------------------------------------------

Every PR:

```text
node --check file.js    # or tsc --noEmit extra
node --test
```

**CI extra:**

```text
npx eslint .            # only if eslint passed the trust bar
```

Must-haves: runs on claimed `engines.node`; no `eval` on untrusted
input; TLS verify on; tests exist.

Not this pack: `npm ci`, `npm audit`, dh-nodejs, MSVC.

------------------------------------------------------------------------
7. COMPOSING
------------------------------------------------------------------------

  this pack
  + [node-ecosystem-policy.md](node-ecosystem-policy.md)
  + [node-os-policy.md](node-os-policy.md) shared + one carve-out

A new `import 'foo'` is an Ecosystem trust-bar event.

------------------------------------------------------------------------
8. QUICK OFFICIAL LINK LIST
------------------------------------------------------------------------

https://nodejs.org/docs/latest-v24.x/api/
https://nodejs.org/en/about/previous-releases
https://nodejs.org/docs/latest/api/crypto.html
https://nodejs.org/docs/latest/api/test.html

Sister packs
./node-ecosystem-policy.md
./node-os-policy.md
./README.md

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.0.0 | Initial language pack: Node 24 LTS ship bar, builtins-first security contracts, node:test |
