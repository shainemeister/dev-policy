---
title: "Linux development policy packs"
description: Modular OS and application policy maps for Debian and GNOME. Compose packs; do not merge them into one rulebook.
version: "1.1.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - debian-os-policy.md
  - debian-application-policy.md
  - gnome-os-policy.md
  - gnome-application-policy.md
  - sources.yaml
last_updated: "2026-08-29"
---

# Linux development policy packs

Curated maps of **what each layer actually checks**. Not tutorials. Not
product law for any one repository.

Two axes, four packs. Compose packs; do not merge them. Add more distros
later on the same axes (Fedora OS, KDE Application, and so on) without
rewriting these files.

```text
                 APPLICATION                         OS
                 (what the program is)               (how it lives on a system)
                 ---------------------               --------------------------
Debian           debian-application-policy.md        debian-os-policy.md
GNOME            gnome-application-policy.md         gnome-os-policy.md
```

**Role:** working memory for humans and agents. Cite official manuals;
do not treat this folder as a substitute for Debian Policy or the HIG.

Last verified against official Debian, GNOME, Freedesktop, Flatpak, and
Flathub documents as of 2026-08-25. Pins and the watch workflow are in
**Retrieving updates from official sources**.

Read the root files. [archive/](archive/) is the frozen 1.0.0 snapshot,
kept for comparison only.

------------------------------------------------------------------------
How to compose
------------------------------------------------------------------------

Pick **one payload OS** per ship format. Add an **application** pack for
each ecosystem the program belongs to. Optionally add a **session OS**
when the desktop is not the same as the payload OS.

| Deliverable | Payload OS | Session OS (if any) | Application pack(s) |
|-------------|------------|---------------------|---------------------|
| Native `.deb` on Debian, any toolkit | Debian OS | — | Debian Application |
| Native `.deb` on Debian, GNOME-shaped GUI | Debian OS | GNOME OS (session + portals only) | Debian Application + GNOME Application |
| Flatpak on Flathub / GNOME OS image | GNOME OS | GNOME OS | GNOME Application |
| GNOME Circle listing of a Flatpak | GNOME OS | GNOME OS | GNOME Application (quality) + GNOME OS (store gates) |
| Official Debian package of a GNOME app | Debian OS | GNOME OS (session) | both Application packs |

Default for a GNOME-platform app that ships first as a Debian `.deb`:

  GNOME Application + Debian Application + Debian OS
  (+ GNOME OS *session* services: portals, settings, Shell)

Do **not** apply GNOME OS *payload* rules (Flatpak `/app`, Flathub AI
store ban, GNOME runtime EOL) to that `.deb`.

------------------------------------------------------------------------
Conflict resolution
------------------------------------------------------------------------

When two packs mention the same object, split **contents** from
**placement** and **queue**.

| Object | Who owns contents | Who owns placement | Who owns the queue |
|--------|-------------------|--------------------|--------------------|
| Binary, data, icons | Application pack of the UI toolkit | Payload OS pack | Payload OS pack |
| `.desktop` / metainfo | GNOME Application (HIG, summary, OARS) if GNOME-shaped; else Debian Application minima | Payload OS (`/usr/share` vs `/app/share`) | Payload OS |
| License | Both application packs (DFSG vs OSI) plus OS archive rules | Debian Application (`debian/copyright`) or Flathub SPDX | Debian NEW vs Flathub PR |
| App ID string | GNOME Application | — | Stores (GNOME OS) may add verification |
| HIG, a11y, widgets | GNOME Application | — | Circle review (app quality) |
| FHS, usr-merge, apt | — | Debian OS | Debian NEW |
| Sandbox finish-args, GNOME runtime | — | GNOME OS | Flathub / Circle store |
| Portals as GTK APIs | GNOME Application | — | — |
| Portals as session services | — | GNOME OS (session) | — |
| `%f`/`%u` Exec codes | Application (GNOME if GNOME-shaped) | Payload OS desktop path | Payload store |
| Conffiles / `/etc` | Debian Application (declare / migrate conffiles) | Debian OS (`/etc`, purge vs remove, Policy 10.7) | NEW |
| tag2upload / Git-Tag-* | Debian Application | — | dak |
| Portal implementation | — | GNOME OS session | — |
| Portal GTK/libportal calls | GNOME Application | — | — |
| Flathub English / license-files / extra-data | — | GNOME OS payload | Flathub PR |
| Circle no-crypto / CoC content | GNOME Application | — | Circle |
| Debian AI GR (if it passes) | Debian Application (+ OS if Social Contract) | — | Debian vote / NEW |

Hard rules:

1. Payload prefix follows the payload OS. Debian OS ⇒ `/usr`. GNOME OS
   Flatpak ⇒ `/app`. Never both for one artifact.
2. Session APIs follow the running desktop. A `.deb` on GNOME still
   talks to `xdg-desktop-portal-gnome`. That is GNOME OS session, not
   a license to ship a Flatpak.
3. "Preferred distribution" is an OS opinion, not an application
   requirement. Debian OS prefers `.deb`+apt. GNOME OS prefers Flatpak.
   The product chooses a first store; the unused OS pack stays optional.
4. Do not import Circle "must be on Flathub" into Debian Policy.
5. Do not import lintian or `Standards-Version` into a Flatpak manifest.

------------------------------------------------------------------------
What each pack is
------------------------------------------------------------------------

[debian-os-policy.md](debian-os-policy.md)

Debian as an operating system: Social Contract, archive, apt/dpkg, FHS,
usr-merge, systemd, users/groups, multiarch, security updates. Desktop
agnostic. Does not own HIG or `debian/control` field-by-field packaging.

[debian-application-policy.md](debian-application-policy.md)

What Debian requires of a *package* that is an application: source and
binary package rules, control fields, copyright-format, changelog, man
pages, relationships, maintainer scripts, lintian, ITP/NEW. Desktop and
AppStream as **packaging artifacts** (must exist, must validate, must
live under FHS). Not the HIG.

[gnome-os-policy.md](gnome-os-policy.md)

GNOME as a desktop OS and as a ship format: Shell, session, settings
daemon, portals, GNOME Software, Flatpak, GNOME runtime, Flathub, GNOME
OS images (systemd-sysupdate), Circle/Core as release-train membership.
Session parts apply to `.deb` apps running under GNOME. Payload parts
apply only to Flatpak / GNOME OS images.

[gnome-application-policy.md](gnome-application-policy.md)

What GNOME requires of the *program*: HIG, GTK 4 + Libadwaita, application
ID, GSettings, desktop/metainfo/icon **contents**, accessibility, OSI
license, no GNOME trademark on third-party apps. Circle *app quality*
lives here. Circle *Flathub + runtime* lives in GNOME OS.

------------------------------------------------------------------------
Adding another distro
------------------------------------------------------------------------

Copy the axes, not the files.

1. Write `<distro>-os-policy.md` for that distro's filesystem, installer,
   package manager, init, and archive/store.
2. Write `<distro>-application-policy.md` only if the distro has
   application packaging rules distinct from the OS (Fedora Packaging
   Guidelines, Arch PKGBUILD conventions, …).
3. Desktop ecosystems stay separate (GNOME Application, later KDE
   Application). A KDE app on Debian is Debian OS + Debian Application +
   (future) KDE Application. Do not fold KDE HIG into Debian OS.
4. Update this README composition table. Do not silently overload an
   existing pack.
5. A new distro is a new directory under ``os/`` (for example
   ``os/fedora``), not a new git repository. Languages live under
   [program-language/](../../program-language/).

------------------------------------------------------------------------
Retrieving updates from official sources
------------------------------------------------------------------------

Packs are maps. Official manuals remain the authority.

The **1.0.0** snapshot lives in [archive/](archive/) and must not be
edited.

[sources.yaml](sources.yaml) is the watch registry. Each entry records
a canonical URL, the owning pack, a pin, a detector, and whether the
source splits **OS** vs **application**.

[../../scripts/check_sources.py](../../scripts/check_sources.py)
(`--family os/linux`) prints `UNCHANGED` or `DRIFT`. On drift, patch
the owning pack with a bite-sized rule, then bump the pin. Never
auto-merge HTML into packs.

Cadence:

- Announce lists and the GNOME ICS calendar: continuous
- Debian Policy, Developer's Reference, Flathub requirements,
  AppCriteria: weekly
- HIG, portal docs, AppStream: on GNOME point-zero releases

Current pins as of 2026-08-25:

- Debian Policy **4.7.4.1**
- Developer's Reference **14.14**
- GNOME **50** stable / **49** old-stable / **51** unstable
  (51.0 on 2026-09-12)
- Debian **13** (trixie) stable
- Debian AI GR voting through **2026-08-28**
- Circle intake closed **2026-05-29**

`REJECT-FAQ.html` 404s. NEW process links live in the Debian Application
pack.

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.1.0 | Reliability pins, gap fill from official docs, source watch (`sources.yaml` + `scripts/check_sources.py`). |
| 1.0.0 | Initial four-pack split: Debian OS, Debian Application, GNOME OS, GNOME Application |

The 1.0.0 snapshot is frozen in [archive/](archive/). Root files were
sourced from that snapshot and then hardened. Read the root files, not
`archive/`, unless you are comparing versions.
