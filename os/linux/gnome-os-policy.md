---
title: "GNOME OS Policy"
description: Curated map of GNOME as desktop session and as ship format — Shell, portals, Flatpak, runtime, Flathub, GNOME OS images. Not HIG and not Debian FHS.
version: "1.1.0"
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

1. **Session** — GNOME Shell, gnome-session, settings daemon, portals,
   gvfs, Software UI, GDM. Applies to *any* payload (`.deb`, rpm,
   Flatpak) while the user is on GNOME. Sections 2–5.
2. **Payload** — Flatpak `/app`, GNOME runtime, Flathub inclusion,
   Circle store gates, GNOME OS images. Applies only when that ship
   format is chosen. Sections 6–9.

A GNOME-shaped `.deb` on Debian uses half (1) and Debian OS for half
(2). Do **not** apply sections 6–9 to that `.deb`.

Release pin (https://release.gnome.org/calendar/):

- GNOME **stable 50** (released 2026-03-18)
- GNOME **old-stable 49**
- GNOME **unstable 51** (51.0 tarballs 2026-09-12, release 2026-09-16)
- Current Flathub GNOME runtime to target: **50**
- GNOME **49 runtime** goes EOL around **51.1 (2026-10-10)** after the
  Flatpak grace period (point-zero to point-one)

------------------------------------------------------------------------
0. LAYERING
------------------------------------------------------------------------

This pack owns:

- GNOME session stack and D-Bus session services
- xdg-desktop-portal as an **OS service** (implementations, catalog)
- gvfs as the session VFS; Flatpak talk/filesystem grants to reach it
- GNOME Software as the OS software center UI (and its backends)
- Flatpak sandbox, `/app` prefix, GNOME runtime / SDK EOL
- Flathub as the GNOME-adjacent store (inclusion policy and store AI)
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
SESSION HALF — any payload on GNOME (sections 2–5)
------------------------------------------------------------------------

These sections apply while the user is logged into a GNOME session,
whether the app is a `.deb`, an rpm, or a Flatpak. They do not choose
a ship format.

------------------------------------------------------------------------
2. SESSION STACK
------------------------------------------------------------------------

A GNOME user session is not "whatever GTK is installed." It is a
graph of services:

- **GDM** — display manager; greeter is a kiosk gnome-session. Screen
  lock on this OS is GDM's job.
  https://gitlab.gnome.org/GNOME/gdm
- **GNOME Shell** — compositor, overview, system status, app grid,
  notification server, search
- **gnome-session** — starts the session, owns shutdown
  https://gitlab.gnome.org/GNOME/gnome-session
- **gnome-settings-daemon** — applies settings (input, power,
  xsettings, house-keeping) to the OS
- **Mutter** — Wayland compositor (and Xwayland)
- **xdg-desktop-portal** + **xdg-desktop-portal-gnome** — permissioned
  OS APIs for sandboxed *and* unsandboxed apps
- **xdg-desktop-portal-gtk** — GTK file chooser / print fallback
- **PipeWire** — camera, screenshare, audio on modern GNOME
- **gvfs** — user-visible mounts (trash, smb, google-drive, MTP)
- **DConf / GSettings backend** — settings storage the session hosts
- **GNOME Software** — install UI for the OS (`.deb` and/or Flatpak
  depending on the distro)
- **malcontent** — parental controls; Settings and Software consult it
  https://gitlab.gnome.org/GNOME/malcontent
- **gnome-initial-setup** — first-boot / first-login kiosk session, not
  an app store listing
  https://gitlab.gnome.org/GNOME/gnome-initial-setup

Developer docs for integration (file *roles* the session reads):
https://developer.gnome.org/documentation/guidelines/maintainer/integrating.html

D-Bus activation is how this OS prefers to launch applications
(pristine environment, cgroup, persistent notifications). The
application pack describes `DBusActivatable` + a service file. This pack
is why that mechanism exists. Host apps should land in an XDG-named
cgroup; see section 4 (host Registry).

Search, notifications, screencast, secret service, inhibit-idle, USB,
and camera are session buses. Apps consume them; they do not replace
them.

When Debian (or Fedora, Arch, …) ships GNOME, **this session stack is
still GNOME OS**. The payload of those apps may still be distro
packages.

Search providers (session service)
https://developer.gnome.org/documentation/tutorials/search-provider.html

- Overview search is GNOME Shell. Apps opt in with
  `$datadir/gnome-shell/search-providers/*.ini` plus
  `org.gnome.Shell.SearchProvider2` on the session bus.
- Queries must not open a window. The provider should D-Bus-activate in
  service mode. User configuration lives in Settings → Search, not in
  the app.
- A `.deb` installs the `.ini` under `/usr/share/gnome-shell/…`. A
  Flatpak exports it. Same session API.

GNotification delivery (session service)
https://developer.gnome.org/documentation/tutorials/notifications.html

- Delivery is Shell as `org.freedesktop.Notifications`. Persistent
  notifications require GApplication, a matching desktop file, and
  D-Bus activation.
- Desktop key `X-GNOME-UsesNotifications=true` puts the app in
  Settings → Notifications. Users can mute per-app or globally; do not
  treat notifications as a required control path.
- Sandboxed apps should use the Notification portal (section 4). GTK
  `g_application_send_notification()` already does. HIG of *when* to
  notify is the GNOME Application pack.

systemd user units vs XDG autostart

- Session *services* (settings daemon modules, portal backends, Shell)
  start as **systemd user units** under `gnome-session@.target` /
  `graphical-session.target`. That is the GNOME 49+ path. Do not add
  new session daemons as `/etc/xdg/autostart/*.desktop` only.
- User *applications* at login may still use XDG Autostart
  (`~/.config/autostart`, `$XDG_CONFIG_DIRS/autostart`). Prefer a
  systemd user unit `WantedBy=graphical-session.target` when the thing
  is a service, not a windowed app.
- GDM's greeter is a kiosk session (`Kiosk=true`): it does not autostart
  random desktop files. Agents in the login session belong on
  `gnome-session@gnome-login.target`.
- Flatpak finish-args and Flathub autostart policy live in the payload
  half. A `.deb` autostart file is a session integration, not a
  Flathub permission.

malcontent, gnome-initial-setup, GDM — session, not store

- malcontent is the parental-controls policy store. Software hides or
  blocks apps from it. Do not ship a second parental-controls daemon.
- gnome-initial-setup runs once (or per new user). It is not an
  application to put on Flathub, and it is not Debian NEW.
- Replacing GDM drops GNOME's lock screen and greeter contract. Other
  display managers can start a GNOME session; they do not become GDM.

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
- `~/.local/share/gnome-shell/search-providers` — user search providers
- `~/.local/share/flatpak/exports` — user Flatpak exports
- `/var/lib/flatpak/exports` — system Flatpak exports
- `$XDG_RUNTIME_DIR` — `/run/user/<uid>` portals, buses, Pulse/PipeWire,
  gvfs sockets (`gvfsd`, `gvfs`)

Do not document Debian `/usr` here as the Flatpak prefix.

------------------------------------------------------------------------
4. PORTALS AS OS SERVICES
------------------------------------------------------------------------

xdg-desktop-portal
https://flatpak.github.io/xdg-desktop-portal/docs/
API reference (full catalog):
https://flatpak.github.io/xdg-desktop-portal/docs/api-reference.html
Flatpak portal chapter (GTK subset):
https://docs.flatpak.org/en/latest/portals.html

The portal is a **session service**. GTK implements client support for
a subset. Applications should call GtkFileDialog / GtkUriLauncher
(application pack). This OS must actually be running a portal backend
or those calls degrade.

Portal catalog vs GTK subset

The OS exposes the portal *catalog*. GTK (and Libadwaita) auto-use
only some of it inside a sandbox. Everything else the app must call
on `org.freedesktop.portal.Desktop` itself, or via a convenience
library. Do not assume "we use GTK, so every portal is covered."

Catalog this session is expected to implement (GNOME backend; names
are the public portal interfaces):

- **File** — FileChooser / Documents / Trash
- **Open URI**
- **Print**
- **Inhibit** (idle, suspend, logout)
- **Notification**
- **Screenshot / ScreenCast** (PipeWire)
- **Settings** (accent, color-scheme, contrast) — Libadwaita follows
  this
- **USB** — `org.freedesktop.portal.Usb`
  https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Usb.html
- **Camera** (PipeWire; prefer this over raw `/dev/video*`)
- **Location**
- **Account / Email**
- **Background**
- **Wallpaper**
- **Secret** (libsecret / gnome-keyring backend)

The API reference lists more (Clipboard, DynamicLauncher, GlobalShortcuts,
InputCapture, NetworkMonitor, RemoteDesktop, …). Use the reference, not
this map, when you need an interface that is not in the list above.
Presence of the D-Bus name does not mean every GNOME version implements
every method.

GTK's transparent subset (from the Flatpak portals chapter) is
roughly: native file chooser, print, open-URI, inhibit, GNotification,
screensaver-active. USB, camera, location, wallpaper, background,
account, and the Settings portal's extra keys are **not** "GTK did it
for us."

Host app Registry (deprecated)

https://flatpak.github.io/xdg-desktop-portal/docs/api-reference.html
https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.host.portal.Registry.html
cgroup replacement:
https://systemd.io/DESKTOP_ENVIRONMENTS/#xdg-standardization-for-applications

`org.freedesktop.host.portal.Registry` lets unsandboxed apps associate
their D-Bus connection with an application ID. That overwrites
automatic detection from the **XDG cgroup pathname** for applications.
The interface is expected to go away. Apps and launchers must:

- Place the app in a cgroup named to the XDG application convention
- Treat Registry `Register()` as optional
- Survive the name or method vanishing (do not fail startup)

Sandboxed Flatpaks never used Registry; Flatpak already labels them.

Flathub (payload) rule: if a suitable portal exists and covers the use,
using the portal is **mandatory** instead of a static sandbox
permission. That sentence is store/payload law. On a `.deb` there is no
finish-arg; the same GTK API still talks to this OS service.

gvfs (session daemon + Flatpak talk grants)

https://docs.flatpak.org/en/latest/sandbox-permissions.html#gvfs-access

gvfs is a **session** component. Distro `.deb` apps just Depend on
gvfs. Flatpak apps must be granted a way to talk to the daemons
already running on the host. Those grants are payload finish-args;
the daemon is still this OS.

- GTK / GIO apps:
  `--talk-name=org.gtk.vfs.*` and `--filesystem=xdg-run/gvfsd`
- FUSE / legacy / non-GIO:
  `--filesystem=xdg-run/gvfs`
- **Never** `--talk-name=org.gtk.vfs` (no such bus name)

`--talk-name=org.gtk.vfs.*` is a broad host-VFS grant (trash, SMB,
Google Drive, MTP, even local backends). Prefer portals (FileChooser,
Documents, OpenURI, USB) when they cover the feature. Repeat: these
finish-args exist only on a Flatpak artifact. Do not invent them for
a `.deb`.

------------------------------------------------------------------------
5. GNOME SOFTWARE AND APPSTREAM ON THIS OS
------------------------------------------------------------------------

GNOME Software is the OS's graphical installer. It reads AppStream
from whatever backends the distro enabled.

https://gitlab.gnome.org/GNOME/gnome-software
https://apps.gnome.org/Software

Backends (plugins; distro chooses which are on):

- **PackageKit** — traditional packages (apt, rpm, …). Typical Debian /
  Fedora workstation. Off on image-based OS (GNOME OS, Silverblue).
- **Flatpak** — Flathub and other remotes. GNOME's preferred app
  payload. On GNOME OS.
- **fwupd** — device firmware (LVFS). Session/OS, not an app store
  listing.
  https://fwupd.org/
- **ODRS** — ratings and reviews.
  https://odrs.gnome.org/

Software is also a Shell search provider and a background update
notifier. On GNOME OS it additionally talks to systemd-sysupdate
(section 8). Snap, rpm-ostree, and similar plugins are distro
additions, not this pack's default.

Metadata meanings (safety tile, hardware, OARS, license tile, links):
https://gnome.pages.gitlab.gnome.org/gnome-software/help/C/software-metadata.html

Safety tile:

- For Flatpak, **static sandbox holes** (host/home filesystem, full
  session-bus, `--device=all`, …) lower the displayed safety.
- **Portals do not.** FileChooser, USB portal, Notification portal,
  Camera portal keep the tile higher than the equivalent static grant.
- For `.deb` / rpm, Software often cannot know sandbox shape and must
  guess. That is an OS limitation, not a reason to apply Flatpak
  finish-args to a `.deb`.

Featured apps list used by GNOME Software (Circle membership feeds it):
https://gitlab.gnome.org/GNOME/gnome-app-list/-/blob/main/data/gnome-apps.txt

AppStream spec (file format):
https://www.freedesktop.org/software/appstream/docs/
Contents of the XML: GNOME Application pack.
Where it is installed: payload OS (`/usr/share/metainfo` vs
`/app/share/metainfo`).

------------------------------------------------------------------------
PAYLOAD HALF — only when the artifact is Flatpak / GNOME OS
(sections 6–9)
------------------------------------------------------------------------

Do **not** apply sections 6–9 to a Debian `.deb` (or rpm, AppImage,
upstream tarball). A GNOME-shaped GUI on Debian uses the session half
plus Debian OS / Debian Application. Flathub AI policy, GNOME runtime
EOL, `/app`, and Circle store gates are not Debian Policy.

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

Support is about **one year**. A branch is EOL'd after the *next* GNOME
stable plus the Flatpak grace window (GNOME point-zero to point-one).
Calendar note:
https://release.gnome.org/calendar/

Pin for this pack (2026-08-25):

- Target **org.gnome.Platform//50** (and matching Sdk) on Flathub.
- GNOME **49** runtime goes EOL around **51.1 (2026-10-10)**.
- GNOME **51** is unstable until 2026-09-16; do not ship new stable
  apps on 51 until it is the current stable runtime on Flathub.

Circle maintenance: stay on a **supported** GNOME runtime. The Circle
Committee reminds maintainers months before SDK EOL (announced
2026-05-29). A `.deb` built against Debian 13's GNOME 48 libraries does
not freeze the Flathub SDK at 48, and Debian's GNOME version is not a
Flathub runtime pin.

Architectures: GNOME runtime on Flathub is x86_64 and aarch64. 32-bit
compatibility extensions (`org.gnome.Platform.i386.Compat`) were
dropped in the GNOME 49 era:
https://blogs.gnome.org/alatiera/2025/10/13/flatpak-32bit/

Typical finish-args for a GTK4 Wayland document app:

- `--socket=wayland`
- `--socket=fallback-x11`
- `--share=ipc`
- `--device=dri`
- No `--share=network` unless a feature needs it
- No `--filesystem=host`
- gvfs (if the app opens non-native URIs via GIO): section 4 grants

Permissions (payload law; also Flathub section 7):
https://docs.flatpak.org/en/latest/sandbox-permissions.html

- `--socket=session-bus` and `--socket=system-bus` drop D-Bus
  filtering. Treat them as a **security fail** except for development
  tools.
- `--own-name=` beyond the app id (and MPRIS
  `org.mpris.MediaPlayer2.$FLATPAK_ID`) is usually unnecessary.
- `--filesystem=host` and `--filesystem=home` are last resort. Prefer
  portals, then a named XDG dir (`xdg-download`, `xdg-pictures`, …).
- USB: **USB portal** (`org.freedesktop.portal.Usb` + `--usb=`
  enumerable devices) over `--device=all`. `--device=usb` is still
  broader than the portal.
  https://docs.flatpak.org/en/latest/sandbox-permissions.html#usb-portal
- Camera: Camera portal / PipeWire over `--device=all`.

Conditional permissions (Flatpak **1.17+**):
https://docs.flatpak.org/en/latest/sandbox-permissions.html#conditional-permissions

`--device-if=`, `--socket-if=`, `--share-if=`, `--allow-if=` grant a
permission only when a runtime condition matches (`has-usb-portal`,
`has-usb-device`, `has-input-device`, `has-wayland`, …). Manifests
that use them **require Flatpak 1.17 to build**. Older builders error
on the unknown flag. Use them to fall back from `--device=all` to
USB/input, or from X11 to Wayland, without abandoning old hosts.

`flatpak-builder` has no network during the build. `--share=network` in
`build-args` will not work. Cargo/npm/pip dependencies must be vendored
as sources (or generated dependency manifests).

------------------------------------------------------------------------
7. FLATHUB (STORE)
------------------------------------------------------------------------

Requirements (inclusion — this is store law):
https://docs.flathub.org/docs/for-app-authors/requirements
Quality (promotion, **not** admission):
https://docs.flathub.org/docs/for-app-authors/metainfo-guidelines/quality-guidelines
Maintenance:
https://docs.flathub.org/docs/for-app-authors/maintenance

Flathub is not GNOME and not Debian. GNOME Circle treats it as the
required store. GNOME Software on many distros shows it. These bullets
apply **only** to a Flatpak submitted to Flathub. Do not copy them onto
a `.deb`.

English UI + metainfo
Complete English localisation of UI, desktop file, metainfo, and
user-facing docs. Exceptions: inherently region-locked apps (banking,
government) and authors whose native language is not English who could
not find translators. Non-English-only apps must say so in the
metainfo description.

Build from source
Build the app and its runtime dependencies entirely from source. No
binaries in the PR. `extra-data` is only for non-redistributable
blobs. Well-known vendor exceptions are case-by-case.

License files
Install each module's licenses to
`$FLATPAK_DEST/share/licenses/$FLATPAK_ID` (flatpak-builder does this
for common names at the source root; otherwise `install` / `post-install`).

Manifest and build
Manifest named `<id>.yml`, `<id>.yaml`, or `<id>.json` at the Flathub
repo root. YAML: 2-space indent, LF, UTF-8, trailing newline; do not
alphabetise keys (id, runtime, sdk, finish-args, modules, …). JSON:
4 tabs if you must use JSON. Sub-manifests only when a generator
produced them. Dependency generators:
https://github.com/flatpak/flatpak-builder-tools
`--share=network` in `build-args` will not work (no network at build).

Application ID (store rules, stricter than GNOME Application)

https://docs.flathub.org/docs/for-app-authors/requirements#application-id

- Reverse DNS; at least 3 components, **at most 5**; ≤255 characters.
- Each component `[A-Za-z0-9_]`; a dash `-` is allowed **only in the
  last** component.
- Code-hosting user repos: `io.github.`, `io.gitlab.`, `page.codeberg.`,
  `io.frama.` — **not** `com.github.` / `com.gitlab.` (those are
  reserved for the platform's own projects). Four components minimum.
- The domain computed from the ID must be under the author's control
  and reachable over **HTTPS**.
- `org.gnome.*` is protected (registered-app-ids list).
- Rename after accept is **conservative** and often a resubmit. Refused:
  same-domain cosmetic rename, rename without intent to verify, rename
  immediately after accept, frequent renames.
  https://docs.flathub.org/docs/for-app-authors/requirements#renaming-flatpak-id

Inclusion refusals (non-exhaustive; case-by-case):

- Console software (exception: Flatpak/Flathub tooling)
- Minimal / thin wrappers / launchers
- Web wrappers without real desktop integration
- Tray-only applets
- GNOME Shell / DE extensions
- Host system utilities
- Environment-locked (needs one DE or one distro), except e.g. a
  GNOME settings panel
- Host-dependent (needs host bits or a complicated post-install)
- Wine / emulation unless **official upstream** maintains it
- Duplicates (same app, or a trivial fork, or the same app in two
  toolkits)
- Third-party Flatpak of an app that upstream already ships as a
  Flatpak elsewhere
- Insufficient development history
- Gambling / real-money games of chance
- Unethical / dark-pattern design
- EOL runtime, or EOL high-risk deps (**OpenSSL 1.x**, **Python 2**,
  Qt5 WebKit, …) **with network** (or other invasive permissions)
- Insecure design, impersonation, malware

Required store files besides the manifest: generated dependency
manifests; optional `flathub.json` to limit architectures (Circle
wants both x86_64 and aarch64 — do not limit without cause).
Desktop/metainfo/icons come from **upstream** (application pack).

License: redistributable; SPDX in metainfo matches source; no trademark
confusion (including "GNOME" in a third-party name or icon).

Generative AI policy (store, 2026) — **payload/store only**:
https://docs.flathub.org/docs/for-app-authors/requirements#generative-ai-policy

- Applies to the **app** and to the **submission**: manifest, metadata,
  patches, build scripts, and the PR (comments, description, opening
  the PR).
- PRs must not be generated, opened, or automated by AI/agents.
  Review comments must not be LLM-generated.
- Disable Copilot auto-review on the `flathub` GitHub org (exclude
  that repository, or turn off global automatic Copilot review):
  https://github.com/settings/copilot/coding_agent
  https://github.com/settings/copilot/features
- Apps containing AI-generated or AI-assisted code or docs are not
  allowed.
- Exceptions may exist for mature, well-maintained projects.
- Repeated violations can ban the submitter.

Circle's application-side AI bar (explain the code; no slop) is the
GNOME Application pack. Debian NEW has no AI policy. **Do not copy this
store ban into a `.deb` workflow.**

Stable vs nightly

- Flathub **stable** is for stable software only.
- Nightlies / daily snapshots belong in neither stable nor beta.
- New submissions are **not** accepted to the beta repo.
- Switching a user from beta to stable later is a manual migration.

Quality guidelines are **promotion, not admission**
https://docs.flathub.org/docs/for-app-authors/metainfo-guidelines/quality-guidelines

Passing them helps banners, App of the Day, trending. Failing them does
not block the PR. Store extras (curated, not a checklist dump):

- Brand colors (light + dark, contrast against the icon)
- Name about **15 characters** (hard cap 20), just the name
- Summary about **10–25 characters** (cap 35), not technical, no
  trailing period
- Window-only screenshots **with native shadow and rounded corners**,
  captions, taken on Linux, default settings
- Release notes that actually say what changed

These are store presentation. They must **not** silently rename the
app. The HIG name (and whether the name is allowed to include
"GNOME") is [gnome-application-policy.md](gnome-application-policy.md).
Do not ship a Flathub-only display name that disagrees with the
running application and the metainfo `<name>`.

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

Unless you are building gnome-build-meta, treat the image mechanics
as light context:

- Updates: **systemd-sysupdate** (migration from OSTree). GNOME
  Software's sysupdate plugin is a session feature of this OS.
- **systemd sysext** — developer workaround for things Flatpak cannot
  express; not an app ship format.
- Factory reset and a boot-to-userspace trust chain are project goals.
- Secure Boot is optional and uses GNOME's own keys (enroll in UEFI
  Setup Mode; `auto` keeps Microsoft keys, `private` does not). The
  nightly ISO currently expects Secure Boot **disabled** to install.
  Details: install.md. Do not document a Debian shim/mok dance here.

Apps on GNOME OS: **Flatpak**. Host-path installers and `.deb` are the
wrong payload.

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
- Keep a supported runtime (section 6 pin: 50 now; 49 until ~51.1)
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
- D-Bus activation actually starts the service (cgroup / notifications)
- GtkFileDialog works (portal backend present)
- Dark / accent follow Settings (Settings portal)
- Notifications arrive; `X-GNOME-UsesNotifications` shows in Settings
- Open With / default handler behave
- Search provider, if shipped, answers from Overview without opening
  a window
- gvfs URIs the app advertises actually open (session gvfs running)
- USB / camera / location, if used, go through portals — not a static
  device node — unless the session backend is missing

Payload / Flatpak (skip on a `.deb`):

- `flatpak-builder` clean build, no network, no binaries in the PR
- Manifest named `<id>.yml` / `.yaml` / `.json`; YAML 2-space
- License files under `$FLATPAK_DEST/share/licenses/$FLATPAK_ID`
- `appstreamcli compose` on the sandbox tree
- Both architectures if targeting Circle
- Permission review: portals vs static filesystem; no session-bus
  socket; USB portal over `--device=all`; 1.17 `--device-if` /
  `--socket-if` only if the builder is ≥1.17
- Runtime branch **50** on Flathub (49 only until ~2026-10-10)
- English UI + metainfo (or a documented localisation exception)
- Builder can build the Flatpak (Circle recommended)
- Flathub quality extras (brand colors, ~15 char name, captions) are
  optional promotion — they must not rename the HIG name

------------------------------------------------------------------------
11. COMPOSING WITH OTHER PACKS
------------------------------------------------------------------------

`.deb` GUI on Debian GNOME:

  Debian OS (payload `/usr`, apt)
  + Debian Application (control, copyright, NEW)
  + GNOME Application (HIG, ID, metainfo contents)
  + **this pack, session half only** (sections 2–5: portals, Shell,
    Software, gvfs, GDM)

  Do **not** apply sections 6–9 (Flatpak prefix, Flathub inclusion or
  AI policy, GNOME runtime EOL, Circle store, GNOME OS images) to that
  `.deb`. A Debian GNOME library version is not a Flathub runtime pin.
  Copilot-on-Flathub and "no binaries in the PR" are not Debian NEW.

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
https://flatpak.github.io/xdg-desktop-portal/docs/api-reference.html
GTK subset: https://docs.flatpak.org/en/latest/portals.html

Flatpak
https://docs.flatpak.org/en/latest/
Sandbox / gvfs / USB / 1.17 conditionals:
https://docs.flatpak.org/en/latest/sandbox-permissions.html

Flathub
https://docs.flathub.org/docs/for-app-authors/requirements
https://docs.flathub.org/docs/for-app-authors/runtimes
https://docs.flathub.org/docs/for-app-authors/metainfo-guidelines/quality-guidelines

GNOME Software
https://gitlab.gnome.org/GNOME/gnome-software
https://gnome.pages.gitlab.gnome.org/gnome-software/help/C/software-metadata.html
ODRS: https://odrs.gnome.org/

GNOME OS
https://os.gnome.org/
https://gitlab.gnome.org/GNOME/gnome-build-meta
https://gitlab.gnome.org/GNOME/gnome-build-meta/-/blob/master/docs/install.md

Circle
https://circle.gnome.org/
https://gitlab.gnome.org/Teams/Circle

Search / notifications (session)
https://developer.gnome.org/documentation/tutorials/search-provider.html
https://developer.gnome.org/documentation/tutorials/notifications.html

Sister packs
./gnome-application-policy.md
./debian-os-policy.md
./debian-application-policy.md
./README.md

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.0.0 | Initial pack: session vs payload split, Software Policy / Circle vs Core, portals as OS services, Flatpak `/app`, Flathub AI, GNOME OS images |
| 1.1.0 | Flathub inclusion policy (English, from-source, ID rules, refusals, licenses, stable≠nightly). Portal catalog vs GTK subset; host Registry deprecation; gvfs talk grants; USB portal. GNOME 50/51 runtime EOL pin (49 → ~51.1). Flatpak 1.17 `--device-if` / `--socket-if`. Software backends and safety tile. Session services: search, GNotification, systemd vs autostart, malcontent, initial-setup, GDM |
