# Changelog

History of the **dev-policy** maps (OS and program-language packs).
Family document versions in YAML frontmatter stay independent of this
repo version.

Structure: `## dev-policy` → `### [X.Y.Z] - YYYY-MM-DD` → Keep a Changelog
categories. Dates are ISO 8601.

---

## dev-policy

### [1.0.0] - 2026-08-29

#### Added

- Combined layout: `os/linux` and `program-language/{rust,python,c,node}`.
- One official-source checker (`scripts/check_sources.py`, User-Agent
  `dev-policy-check/1.0.0`) that walks every family’s `sources.yaml`.
- Root landing README with a cross-family composition table.

#### Notes

- Packs are not merged. Family document versions are unchanged:
  linux 1.1.0, rust 1.1.0, python 1.0.0, c 1.0.0, node 1.0.0.
- Language `*-os-policy.md` files remain under `program-language/<id>/`.
- Frozen `archive/` snapshots moved with each family and must not be
  edited.
