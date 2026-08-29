# Official-source checker

Watch lists: each family’s [`sources.yaml`](../os/linux/sources.yaml)
(and the same filename under `program-language/*`).

This checker **fetches official pages and compares pins**. It does **not**
dump manuals into the policy packs. On `DRIFT`, patch the owning pack with
a **bite-sized rule**, then bump `pin` in that family’s `sources.yaml`.

Packs stay maps, not copies of Debian Policy, the HIG, the Rust Reference,
PEPs, or npm docs.

## Requirements

- Python 3.11+
- [PyYAML](https://pypi.org/project/PyYAML/) (`pip install pyyaml`)

From the repo root you can also install the optional project extra:

```bash
pip install -e .
```

That provides the `dev-policy-check` console script.

## Run

Schema only (no network), every family:

```bash
python3 scripts/check_sources.py --offline
```

One family:

```bash
python3 scripts/check_sources.py --offline --family os/linux
python3 scripts/check_sources.py --offline --family program-language/rust
```

Check every source (network):

```bash
python3 scripts/check_sources.py --timeout 20
```

Check one source:

```bash
python3 scripts/check_sources.py --family program-language/rust --source rust-releases -v
```

```bash
python3 -m py_compile scripts/check_sources.py
```

### Output

One line per source:

- `UNCHANGED <family> <id>`
- `DRIFT <family> <id> <pin> -> <observed>`
- `FETCH_FAIL <family> <id> <reason>`

Exit codes: `0` all unchanged (or `--offline` OK), `2` any drift, `3` fetch
failures with no drift, `1` unexpected error.

If the same `--source` id exists in more than one loaded family, pass
`--family`. Network failures are normal. User-Agent is
`dev-policy-check/1.0.0`. The checker never prints secrets.

The document-level `packs:` list in each YAML is the allowlist. Those
files must sit beside the YAML. `split` may be `language`, `ecosystem`,
`os`, `application`, `both`, or `meta`.

## After a drift

1. Open `canonical_url` (and `git` / `watch_path` if present).
2. Write a short rule in each file listed under that source’s `packs`.
3. Bump `pin` (and `detect` if the page shape changed).
4. Re-run the checker.

Do not paste chapters of official manuals into the packs.
