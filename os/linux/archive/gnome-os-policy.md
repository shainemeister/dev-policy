---
title: "GNOME OS Policy"
description: Curated map of GNOME as desktop session and as ship format — Shell, portals, Flatpak, runtime, Flathub, GNOME OS images. Not HIG and not Debian FHS.
version: "1.0.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - README.md
  - gnome-application-policy.md
  - debian-os-policy.md
  - debian-application-policy.md
last_updated: "2026-08-25"
---

# GNOME OS Policy

Reference pack for **GNOME as an operating environment**: the session
you log into, the services apps talk to, and GNOME's preferred way to
distribute applications (Flatpak + GNOME runtime + Flathub). Also
covers **GNOME OS** the image (nightly immutable OS).

**Role:** curated map (working memory). **Not** L4 for any one product.
**Not** the HIG or GTK widget contract — that is
[gnome-application-policy.md](gnome-application-policy.md).
**Not** Debian apt/FHS — that is
[debian-os-policy.md](debian-os-policy.md).

Last verified against official GNOME, Flatpak, and Flathub documents as
of 2026-08-25.

This pack has two halves that must not be collapsed:

1. **Session** — GNOME Shell, gnome-session, settings daemon, portals.
   Applies to *any* payload (`.deb`, rpm, Flatpak) while the user is on
   GNOME.
2. **Payload** — Flatpak `/app`, GNOME runtime, Flathub, Circle store
   gates, GNOME OS images. Applies only when that ship format is chosen.

A GNOME-shaped `.deb` on Debian uses half (1) and Debian OS for half (2).

------------------------------------------------------------------------
0. LAYERING
------------------------------------------------------------------------

This pack owns:

- GNOME session stack and D-Bus session services
- xdg-desktop-portal as an **OS service** (implementations)
- GNOME Software as the OS software center UI
- Flatpak sandbox, `/app` prefix, GNOME runtime / SDK EOL
- Flathub as the GNOME-adjacent store (including store AI policy)
- GNOME OS images (gnome-build-meta, systemd-sysupdate)
- Circle / Core **membership of the OS image / store** (Flathub
  architectures, nightly Flatpaks, gnome-build-meta)

This pack does **not** own:

- HIG, application ID *semantics*, gschema keys, a11y of widgets
  → [gnome-application-policy.md](gnome-application-policy.md)
- FHS `/usr`, apt, DFSG, NEW
  → Debian OS + Debian Application packs
- Portals as **GTK API calls** (GtkFileDialog)
  → GNOME Application pack (the app must call them; this pack provides
  the session side)

------------------------------------------------------------------------
1. FOUNDATIONAL DOCUMENTS
------------------------------------------------------------------------

GNOME Foundation Software Policy (what is "GNOME" on this OS)
https://wiki.gnome.org/Foundation/SoftwarePolicy
App Organization:
https://gitlab.gnome.org/Teams/Releng/AppOrganization
Official app definition:
https://gitlab.gnome.org/Teams/Releng/AppOrganization/-/blob/main/OfficialAppDefinition.md
Lifecycle (Incubator → Core):
https://gitlab.gnome.org/Teams/Releng/AppOrganization/-/blob/main/AppLifecycle.md

Official GNOME software is what the Release Team puts in
gnome-build-meta (`core`, `core-deps`, `sdk`, `sdk-deps`) under
gitlab.gnome.org/GNOME. Only that software may use GNOME trademarks
and `org.gnome.*` as a matter of OS identity.

GNOME Circle is recognized third-party software. It is **not** official
GNOME software. Circle *app quality* is the GNOME Application pack.
Circle *must ship on Flathub with a GNOME runtime* is this pack.

GNOME Handbook (how the project operates the OS)
https://handbook.gnome.org/
Development: https://handbook.gnome.org/development.html
Release calendar: https://release.gnome.org/calendar/

GNOME components (session modules)
https://developer.gnome.org/components/

Platform intro (tools of the OS)
https://developer.gnome.org/documentation/introduction.html
Builder, Flatpak, Meson as platform tools:
https://developer.gnome.org/documentation/

------------------------------------------------------------------------
2. SESSION STACK
------------------------------------------------------------------------

A GNOME user session is not "whatever GTK is installed." It is a
graph of services:

- **GNOME Shell** — compositor, overview, system status, app grid
- **gnome-session** — starts the session, owns shutdown
- **gnome-settings-daemon** — applies settings (input, power, xsettings,
  house-keeping) to the OS
- **Mutter** — Wayland compositor (and Xwayland)
- **xdg-desktop-portal** + **xdg-desktop-portal-gnome** — permissioned
  OS APIs for sandboxed *and* unsandboxed apps
- **xdg-desktop-portal-gtk** — GTK file chooser backend where used
- **PipeWire** — camera, screenshare, audio on modern GNOME
- **gvfs** — user-visible mounts (trash, smb, google-drive, MTP)
- **DConf / GSettings backend** — settings storage the session hosts
- **GNOME Software** — install UI for the OS (`.deb` and/or Flatpak
  depending on the distro)

Developer docs for integration (file *roles* the session reads):
https://developer.gnome.org/documentation/guidelines/maintainer/integrating.html

D-Bus activation is how this OS prefers to launch applications
(pristine environment, cgroup, persistent notifications). The
application pack describes `DBusActivatable` + a service file. This pack
is why that mechanism exists.

Search providers, notifications, screencast, secret service, and
inhibit-idle are session buses. Apps consume them; they do not replace
them.

When Debian (or Fedora, Arch, …) ships GNOME, **this session stack is
still GNOME OS**. The payload of those apps may still be distro
packages.

------------------------------------------------------------------------
3. XDG AND USER STATE ON THIS OS
------------------------------------------------------------------------

XDG Base Directory
https://specifications.freedesktop.org/basedir-spec/latest/

On a normal distro GNOME session (no Flatpak):

- config: `~/.config`
- data: `~/.local/share`
- cache: `~/.cache`
- state: `~/.local/state`

Inside a Flatpak sandbox (payload half) Flatpak remaps these to
`~/.var/app/<id>/{config,data,cache}`:
https://docs.flatpak.org/en/latest/conventions.html#xdg-base-directories

Application code must use GLib/XDG helpers (GNOME Application pack) so
both session types work. This pack is the remapping.

Well-known session paths the OS owns:

- `~/.local/share/applications` — user desktop overrides
- `~/.local/share/flatpak/exports` — user Flatpak exports
- `/var/lib/flatpak/exports` — system Flatpak exports
- `$XDG_RUNTIME_DIR` — `/run/user/<uid>` portals, buses, Pulse/PipeWire

Do not document Debian `/usr` here as the Flatpak prefix.

------------------------------------------------------------------------
4. PORTALS AS OS SERVICES
------------------------------------------------------------------------

xdg-desktop-portal
https://flatpak.github.io/xdg-desktop-portal/docs/
Flatpak portal chapter:
https://docs.flatpak.org/en/latest/portals.html

The portal is a **session service**. GTK implements client support.
Applications should call GtkFileDialog / GtkUriLauncher (application
pack). This OS must actually be running a portal backend or those calls
degrade.

Services the OS exposes through portals (non-exhaustive):

- File chooser / save / open-file
- Open URI
- Print
- Inhibit suspend / idle / logout
- Notification
- Screenshot / screencast
- Settings (accent, color-scheme) — Libadwaita follows this
- Device / USB (newer)
- Account / email / camera where implemented

Flathub (payload) rule: if a suitable portal exists and covers the use,
using the portal is **mandatory** instead of a static sandbox
permission. That sentence is store/payload law. On a `.deb` there is no
finish-arg; the same GTK API still talks to this OS service.

gvfs
Typical GNOME GTK apps on this OS need to talk to gvfs daemons for
non-native URIs. Flatpak permission details live in section 6. Distro
`.deb` apps just Depends on gvfs as a session component.

------------------------------------------------------------------------
5. GNOME SOFTWARE AND APPSTREAM ON THIS OS
------------------------------------------------------------------------

GNOME Software is the OS's graphical installer. It reads AppStream
from whatever backends the distro enabled (apt, rpm, Flatpak).

Metadata meanings (safety tile, hardware, OARS, license tile, links):
https://gnome.pages.gitlab.gnome.org/gnome-software/help/C/software-metadata.html

Safety tile: for Flatpak, sandbox holes lower the displayed safety.
Portals do not. For `.deb` / rpm, Software often cannot know sandbox
shape and must guess. That is an OS limitation, not a reason to apply
Flatpak finish-args to a `.deb`.

Featured apps list used by GNOME Software (Circle membership feeds it):
https://gitlab.gnome.org/GNOME/gnome-app-list/-/blob/main/data/gnome-apps.txt

AppStream spec (file format):
https://www.freedesktop.org/software/appstream/docs/
Contents of the XML: GNOME Application pack.
Where it is installed: payload OS (`/usr/share/metainfo` vs
`/app/share/metainfo`).

------------------------------------------------------------------------
6. FLATPAK PAYLOAD (GNOME'S PREFERRED APP OS)
------------------------------------------------------------------------

https://docs.flatpak.org/en/latest/
https://developer.gnome.org/documentation/introduction/flatpak.html
Conventions: https://docs.flatpak.org/en/latest/conventions.html
Manifests: https://docs.flatpak.org/en/latest/manifests.html
Sandbox: https://docs.flatpak.org/en/latest/sandbox-permissions.html

Inside the sandbox:

- Runtime provides `/usr`
- Application provides `/app`
- Identity files:
  `/app/share/applications/<id>.desktop`
  `/app/share/metainfo/<id>.metainfo.xml`
  `/app/share/icons/hicolor/...`
  `/app/share/dbus-1/services/<id>.service`

This prefix **conflicts** with Debian OS `/usr` if you try to use both
on one artifact. Do not.

GNOME runtime on Flathub
https://docs.flathub.org/docs/for-app-authors/runtimes
Built from gnome-build-meta:
https://gitlab.gnome.org/GNOME/gnome-build-meta

Circle maintenance: stay on a **supported** GNOME runtime. The Circle
Committee reminds maintainers months before SDK EOL (announced
2026-05-29). A `.deb` built against Debian 13's GNOME 48 libraries does
not freeze the Flathub SDK at 48.

Architectures: GNOME runtime on Flathub is x86_64 and aarch64. 32-bit
compatibility extensions were dropped (GNOME 49 era).

Typical finish-args for a GTK4 Wayland document app:

- `--socket=wayland`
- `--socket=fallback-x11`
- `--share=ipc`
- `--device=dri`
- No `--share=network` unless a feature needs it
- No `--filesystem=host`

Permissions guidelines and D-Bus filtering:
https://docs.flatpak.org/en/latest/sandbox-permissions.html

`flatpak-builder` has no network during the build. Cargo/npm
dependencies must be vendored as sources.

------------------------------------------------------------------------
7. FLATHUB (STORE)
------------------------------------------------------------------------

Requirements
https://docs.flathub.org/docs/for-app-authors/requirements
Quality (promotion, not admission):
https://docs.flathub.org/docs/for-app-authors/metainfo-guidelines/quality-guidelines
Maintenance:
https://docs.flathub.org/docs/for-app-authors/maintenance

Flathub is not GNOME and not Debian. GNOME Circle treats it as the
required store. GNOME Software on many distros shows it.

Application ID extra rules (store verification):
https://docs.flathub.org/docs/for-app-authors/requirements#application-id

- Reverse DNS; `io.github.<user>.<app>` maps to
  `https://github.com/<user>/<app>`
- `org.gnome.*` is protected
- `com.github.*` reserved for GitHub official projects
- Rename of ID after accept is a resubmission

Required store files: manifest named `<id>.yml` at the Flathub repo
root; dependency manifests; optional `flathub.json` to limit
architectures (Circle wants both arches — do not limit without cause).
Desktop/metainfo/icons come from **upstream** (application pack).

License: redistributable; SPDX in metainfo matches source; no trademark
confusion.

Generative AI policy (store, 2026) — **payload/store only**:
https://docs.flathub.org/docs/for-app-authors/requirements#generative-ai-policy

- PRs, comments, descriptions must not be LLM-generated or agent-opened
- Apps containing AI-generated or AI-assisted code or docs are not
  allowed
- Exceptions may exist for mature, well-maintained projects
- Repeated violations can ban the submitter

Circle's application-side AI bar (explain the code; no slop) is the
GNOME Application pack. Debian NEW has no AI policy. Do not copy this
store ban into a `.deb` workflow.

Inclusion refusals (wrappers, tray-only, EOL runtime, insufficient
history, duplicates) are on the requirements page. They are store law.

------------------------------------------------------------------------
8. GNOME OS IMAGES
------------------------------------------------------------------------

GNOME OS Nightly
https://os.gnome.org/
Build: gnome-build-meta
https://gitlab.gnome.org/GNOME/gnome-build-meta
Install notes:
https://gitlab.gnome.org/GNOME/gnome-build-meta/-/blob/master/docs/install.md
Matrix: https://matrix.to/#/#gnome-os:gnome.org

GNOME OS is an immutable, image-based OS for running GNOME itself
(QA and increasingly daily driving). It is **not** Debian.

Update mechanism: **systemd-sysupdate** (migration from OSTree).
Goals: boot-to-userspace trust chain, image-based design, factory
reset, Secure Boot. GNOME Software integration for sysupdate is a
session feature of this OS.

Apps on GNOME OS: **Flatpak**. Host-path installers and `.deb` are the
wrong payload. Workarounds for things Flatpak cannot express: systemd
sysext (developer territory).

GNOME OS is the purest composition of this pack's payload + session
halves. Distro GNOME (Debian, Fedora, …) is session-half + that
distro's payload OS.

------------------------------------------------------------------------
9. CIRCLE AND CORE AS OS MEMBERSHIP
------------------------------------------------------------------------

Circle
https://circle.gnome.org/
https://gitlab.gnome.org/Teams/Circle
README: https://gitlab.gnome.org/Teams/Circle/-/blob/main/README.md
Membership guide:
https://gitlab.gnome.org/Teams/Circle/-/blob/main/membership_guide.md
Review procedure:
https://gitlab.gnome.org/Teams/Circle/-/blob/main/review_procedure.md
Apply:
https://gitlab.gnome.org/Teams/Circle/-/issues/new?issuable_template=app_application

As of 2026-05-29 new Circle issues are closed until the backlog shrinks.
https://blogs.gnome.org/sophieh/2026/05/29/updates-from-the-circle-committee/

OS/store gates taken from App Criteria (leave HIG/a11y to the
application pack):
https://gitlab.gnome.org/Teams/Releng/AppOrganization/-/blob/main/AppCriteria.md

- Uses the GNOME runtime on Flathub
- Available on Flathub for x86_64 and aarch64
- Keep a supported runtime
- Valid ID *for the store* (verification / no org.gnome.*)
- After inclusion: gnome-apps.txt featured list; Damned Lies optional;
  runtime EOL group notices with deadlines

Core / Incubator (becoming part of the GNOME OS image)
https://gitlab.gnome.org/Incubator/Submission
https://gitlab.gnome.org/GNOME/gnome-build-meta
Must follow the GNOME release schedule, nightly Flatpaks if viable,
Release Team approved dependencies, l10n.gnome.org as a module.
Additions finalize before GNOME Alpha:
https://release.gnome.org/calendar/

Core is not regularly extended. Barrier is much higher than Circle.
Do not apply to Core to "become more GNOME."

Getting into Circle does not put the app in apt.
Getting into Debian does not put the app on Flathub.

------------------------------------------------------------------------
10. QUALITY CHECKS (THIS OS)
------------------------------------------------------------------------

Session (any payload on GNOME):

- App launches via desktop file in the Shell grid
- GtkFileDialog works (portal backend present)
- Dark / accent follow Settings
- Notifications, Open With, default handler behave

Payload / Flatpak:

- `flatpak-builder` clean build, no network
- `appstreamcli compose` on the sandbox tree
- Both architectures if targeting Circle
- Permission review: portals vs static filesystem
- Runtime branch supported on Flathub
- Builder can build the Flatpak (Circle recommended)

------------------------------------------------------------------------
11. COMPOSING WITH OTHER PACKS
------------------------------------------------------------------------

`.deb` GUI on Debian GNOME:

  Debian OS (payload `/usr`, apt)
  + Debian Application (control, copyright, NEW)
  + GNOME Application (HIG, ID, metainfo contents)
  + **this pack, session half only** (portals, Shell, Software)

  Do not apply sections 6–9 (Flatpak prefix, Flathub AI, runtime EOL,
  Circle store) to that `.deb`.

Flatpak on Flathub or GNOME OS:

  This pack (session + payload)
  + GNOME Application

  Debian OS / Debian Application do not apply to that artifact.

License: OSI (GNOME Application) and Flathub redistribution (this pack)
and DFSG (Debian OS) are three gates. Satisfy the gates of the packs
you actually compose.

------------------------------------------------------------------------
12. QUICK OFFICIAL LINK LIST
------------------------------------------------------------------------

Software Policy
https://wiki.gnome.org/Foundation/SoftwarePolicy

App Organization
https://gitlab.gnome.org/Teams/Releng/AppOrganization

Handbook / calendar
https://handbook.gnome.org/
https://release.gnome.org/calendar/

Components
https://developer.gnome.org/components/

Portals
https://flatpak.github.io/xdg-desktop-portal/docs/

Flatpak
https://docs.flatpak.org/en/latest/

Flathub
https://docs.flathub.org/docs/for-app-authors/requirements
https://docs.flathub.org/docs/for-app-authors/runtimes

GNOME Software metadata
https://gnome.pages.gitlab.gnome.org/gnome-software/help/C/software-metadata.html

GNOME OS
https://os.gnome.org/
https://gitlab.gnome.org/GNOME/gnome-build-meta

Circle
https://circle.gnome.org/
https://gitlab.gnome.org/Teams/Circle

Sister packs
./gnome-application-policy.md
./debian-os-policy.md
./debian-application-policy.md
./README.md
