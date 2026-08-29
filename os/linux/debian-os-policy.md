---
title: "Debian OS Policy"
description: Curated map of Debian as an operating system — archive, apt, FHS, usr-merge, systemd, Policy 10–11 files and virtual programs. Not application packaging and not HIG.
version: "1.1.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - README.md
  - debian-application-policy.md
  - gnome-os-policy.md
  - gnome-application-policy.md
last_updated: "2026-08-25"
---

# Debian OS Policy

Reference pack for **Debian as an operating system**: how the archive
is structured, how packages are installed, where files may live, how
services start, and how the system is kept free and upgradable.

**Role:** curated map (working memory). **Not** L4 for any one product.
**Not** the application packaging cookbook — that is
[debian-application-policy.md](debian-application-policy.md).
**Not** a desktop HIG — Debian is desktop-agnostic.

Last verified against official Debian documents as of 2026-08-25.
Debian Policy version in current docs: **4.7.4.1** (released 2026-03-31).
Stable example in this map: Debian 13 (trixie) when a concrete suite is
needed. Testing after Trixie is Forky. Policy text is suite-independent
unless noted. `Standards-Version` in `debian/control` is three digits
(`4.7.4`); that field belongs in the Application pack.

This pack is what the OS actually enforces. Application maintainers
still read it, because a `.deb` is an OS artifact. They do not take HIG
or Circle/Flathub rules from here. Split **contents** from
**placement**: this pack owns OS behavior and placement.

------------------------------------------------------------------------
0. LAYERING
------------------------------------------------------------------------

This pack owns:

- Debian Social Contract and DFSG as **archive law**
- apt / dpkg / the suite graph (unstable → testing → stable)
- FHS as implemented by Debian, including usr-merge
- systemd as default init; /run; users and groups
- Multiarch library layout
- Policy 10 files: PATH uniqueness, scripts, conffiles, logs, locale,
  devices, permissions
- Policy 11 customized programs and OS virtual packages
- alternatives and diversions as **OS namespace** tools
- Security updates, the DSA/LTS clock, and reboot-required signaling
- Reproducible binaries as an **archive quality** gate for testing

This pack does **not** own:

- debian/control field-by-field, ITP, mentors, NEW review taste,
  lintian, tag2upload, DEP-8
  → [debian-application-policy.md](debian-application-policy.md)
- Maintainer-script *packaging* (when `preinst`/`postinst` run, how
  to write them). OS interpreter and PATH rules for scripts stay here.
- Shipping a man page or `/usr/share/doc` tree (Application). Runtime
  must not *require* man/info trees (this pack).
- HIG, GTK, application ID semantics, a11y of a GUI
  → [gnome-application-policy.md](gnome-application-policy.md)
- Flatpak `/app`, GNOME runtime, Flathub
  → [gnome-os-policy.md](gnome-os-policy.md)
- GNOME Shell / portals as session services
  → [gnome-os-policy.md](gnome-os-policy.md) session half (applies when
  the user session is GNOME)

Payload rule: a Debian `.deb` installs under `/usr` (this pack). A
Flatpak installs under `/app` (GNOME OS pack). One artifact, one prefix.

------------------------------------------------------------------------
1. FOUNDATIONAL DOCUMENTS
------------------------------------------------------------------------

Debian Social Contract
https://www.debian.org/social_contract
Promise: Debian remains 100% free. Contains the DFSG.

Debian Free Software Guidelines (DFSG)
https://www.debian.org/social_contract#guidelines
Wiki: https://wiki.debian.org/DebianFreeSoftwareGuidelines
License notes: https://wiki.debian.org/DFSGLicenses
FAQ: https://people.debian.org/~bap/dfsg-faq

DFSG in short (10 guidelines):

1. Free redistribution (no royalties for selling or giving away)
2. Source code must be available
3. Derived works must be allowed
4. Integrity of author's source may be protected via patches
5. No discrimination against persons or groups
6. No discrimination against fields of endeavor
7. Rights apply to all recipients
8. License must not be specific to Debian
9. License must not contaminate other software
10. Example free licenses: GPL, BSD, Artistic

The DFSG is **OS/archive** law. A program that is not DFSG-free cannot
go in `main`. It may go in `contrib` or `non-free` only if the license
still allows Debian to distribute it. Application packaging still has
to *document* that license
([debian-application-policy.md](debian-application-policy.md)).

Debian Policy Manual (OS chapters live here too)
https://www.debian.org/doc/debian-policy/
PDF: https://www.debian.org/doc/debian-policy/policy.pdf
Upgrading checklist:
https://www.debian.org/doc/debian-policy/upgrading-checklist.html
Wiki: https://wiki.debian.org/DebianPolicy

Policy is the contract the installed system must satisfy. OS-heavy
chapters:

- Ch. 2 Archive areas
  https://www.debian.org/doc/debian-policy/ch-archive.html
- Ch. 8 Shared libraries
  https://www.debian.org/doc/debian-policy/ch-sharedlibs.html
- Ch. 9 The operating system
  https://www.debian.org/doc/debian-policy/ch-opersys.html
- Ch. 10 Files (PATH, scripts, conffiles, logs — this pack)
  https://www.debian.org/doc/debian-policy/ch-files.html
- Ch. 11 Customized programs (editor/pager, web, X, virtual names)
  https://www.debian.org/doc/debian-policy/ch-customized-programs.html

Chapters 3–7 (binary/source packages, control, maintainer-script
packaging, relationships) and chapter 12 documentation *shipping* are
**application packaging**. Read them from the Debian Application pack.
Policy 12.1 / 12.2 **runtime** (must work without man/info trees) is
this pack.

Debian Constitution (project governance, not packaging syntax)
https://www.debian.org/devel/constitution

Debian Developer's Reference is **how people work**, not OS law. Do
not take ITP, NEW, or `debian/` workflow from it here.
https://www.debian.org/doc/manuals/developers-reference/
Version 14.14, released 2026-06-25.

Release documentation
https://www.debian.org/releases/
Release team: https://release.debian.org/
Testing migration: https://release.debian.org/testing/freeze.html

------------------------------------------------------------------------
2. THE ARCHIVE AND APT
------------------------------------------------------------------------

What Debian *is* on disk: a set of suites served by apt, consumed by
dpkg.

Suites (life cycle of an OS image):

- **unstable (sid)** — daily uploads. Breakage is allowed.
- **testing** — migrates from unstable when dependencies, RC bugs, and
  (for new packages) reproducibility allow. Current testing name
  changes each cycle (Forky after Trixie).
- **stable** — the released OS. Security and point updates only.
- **oldstable** / LTS — still an OS Debian supports for a time.

Areas (freedom of the OS image):

- **main** — DFSG-free, and all dependencies in main
- **contrib** — DFSG-free, but depends on something outside main
- **non-free** / **non-free-firmware** — not DFSG-free; firmware split
  is what default install media often enable

https://www.debian.org/doc/debian-policy/ch-archive.html

dpkg is the installer of `.deb` files. apt is the solver and fetcher.
Neither cares about GTK versus Qt. Desktop choice is a set of packages,
not a second OS.

Packages search
https://packages.debian.org/

Security tracker (OS integrity)
https://security-tracker.debian.org/
https://www.debian.org/security/

A package that lands in the archive **is** part of the OS for everyone
who installs it. That is why NEW review exists (application pack) and
why DFSG is not optional (this pack).

------------------------------------------------------------------------
3. FILESYSTEM HIERARCHY AND USR-MERGE
------------------------------------------------------------------------

Official FHS 3.0 (Freedesktop)
https://specifications.freedesktop.org/fhs/latest
Root filesystem:
https://specifications.freedesktop.org/fhs/latest/rootFilesystem.html

Debian Handbook
https://www.debian.org/doc/manuals/debian-handbook/sect.filesystem-hierarchy.en.html

Policy enforcement
https://www.debian.org/doc/debian-policy/ch-files.html
https://www.debian.org/doc/debian-policy/ch-opersys.html#file-system-hierarchy

Debian FHS exceptions that actually bite (Policy 9.1.1):

- Architecture-independent files *should* live in `/usr/share`; a mix
  of arch-dependent and independent files may live under `/usr/lib`
- Multiarch: libraries in `/usr/lib/<triplet>/` where triplet is
  `dpkg-architecture -qDEB_HOST_MULTIARCH`. 64-bit packages must **not**
  install into `/usr/lib64`
- C/C++ headers may use `/usr/include/<triplet>/`
- Only the dynamic linker and libc may install in `/lib64`
- `/var/run` → `/run`, `/var/lock` → `/run/lock` (required symlinks)
- `/var/www` is allowed
- Packages must not install files in both `/path` and `/usr/path`
  (usr-merge aliasing). Policy 10.1

usr-merge
https://wiki.debian.org/UsrMerge
Technical Committee: bookworm onward, merged-usr only.
`/bin`, `/lib`, `/sbin` are symlinks into `/usr`.
Packages must install under `/usr`, not the old root aliases.
Policy 10.1 / upgrading checklist 4.7.1: packages **must not** install
to `/bin/*`, `/lib/*`, `/lib*/*`, `/sbin/*`. Packages **may assume**
`/bin`, `/lib` and `/sbin` are always symbolic links, so files under
`/usr/bin`, `/usr/lib` and `/usr/sbin` are reachable via those aliases.
https://www.debian.org/doc/debian-policy/upgrading-checklist.html#version-4-7-1
DEP-17 documents remaining aliasing hazards:
https://dep.debian.org/deps/dep17.html

What that means for any payload on this OS:

- Program binary: `/usr/bin/<name>` (or `/usr/sbin` for system admin)
- Libraries: `/usr/lib/<triplet>/` or `/usr/lib/<name>/`
- Architecture-independent data: `/usr/share/<name>/`
- Icons: `/usr/share/icons/hicolor/...`
- Desktop launcher: `/usr/share/applications/<id>.desktop`
- AppStream: `/usr/share/metainfo/<id>.metainfo.xml`
- Man page: `/usr/share/man/man1/<name>.1`
- Docs: `/usr/share/doc/<package>/`
- Config defaults that are conffiles: `/etc/<name>/`

Do not install into:

- `/usr/local` — administrator-managed. Policy 9.1.2: packages must
  not place files there. Empty child directories for local add-ons are
  a special case and must be created in maintainer scripts, not the
  `.deb` data.tar
- `/opt` — third-party extras, not normal Debian packages
- `/bin`, `/lib`, `/sbin` directly — usr-merge; install under `/usr`

`/run` is a tmpfs, cleared at boot. Packages must not ship files under
`/run`, `/var/run`, or `/var/lock`. Create runtime dirs from units or
scripts after boot (Policy 9.1.4).

XDG Base Directory is a Freedesktop spec, not Debian-invented:
https://specifications.freedesktop.org/basedir-spec/latest/
Debian follows it. Application code should use toolkit helpers. This
OS pack does not remap XDG the way a Flatpak sandbox does.

PATH clashes (same name in `/usr/bin` and `/usr/sbin` is still a
clash) are Policy 10.1 — see section 4.

------------------------------------------------------------------------
4. FILES, SCRIPTS, AND CONFIGURATION (POLICY 10)
------------------------------------------------------------------------

Rules that reject or mis-ship a `.deb` even when FHS paths look right.
https://www.debian.org/doc/debian-policy/ch-files.html

PATH uniqueness (Policy 10.1, upgrading checklist 4.7.1 / 4.7.2)
https://www.debian.org/doc/debian-policy/ch-files.html#binaries
https://www.debian.org/doc/debian-policy/upgrading-checklist.html#version-4-7-1
https://www.debian.org/doc/debian-policy/upgrading-checklist.html#version-4-7-2

- Two packages must not install different programs under the same
  filename. That includes **different directories on the default PATH**:
  `/usr/bin/foo` and `/usr/sbin/foo` is a clash.
- Same functionality, different implementations: use alternatives or
  `Conflicts`. Different functionality: rename. Take it to
  `debian-devel`. No consensus ⇒ **both** names change.
- Grandfather exception: existing programs in `/usr/games` may keep a
  name that already collides elsewhere on PATH. **No new clashes** in
  `/usr/games`; existing ones should move to non-conflicting names.

usr-merge install ban (Policy 10.1, same 4.7.1 wording as section 3):
do not ship into `/bin`, `/lib`, `/sbin` aliases. Assume those paths
are always symlinks into `/usr`.

No static linking against glibc (Policy 10.1). That is OS ABI: security
fixes flow through the shared C library. Exception: recovery and
diagnostics that must work when glibc is unusable (rescue shells,
`ldconfig`). Policy also allows a security-benefit exception; do not
invent one for a normal application.

Scripts (Policy 10.4) — OS interpreter and PATH rules. Maintainer-script
*packaging* (dpkg calling convention) is the Application pack.
https://www.debian.org/doc/debian-policy/ch-files.html#scripts

- `#!` names the interpreter. `/bin/sh` is POSIX.1-2017 plus Policy's
  listed extras (`echo -n`, `test -a`/`-o`, `local`, XSI `kill`/`trap`).
- `set -e`, or check every command's exit status. (`init.d` is the
  documented special case.)
- Perl on PATH: `#!/usr/bin/perl`.
- No `.sh` or `.pl` (or other language suffix) on a PATH name.
- Avoid `csh`/`tcsh`. If upstream ships them, `#!/bin/csh` and Depend
  on the `c-shell` virtual package.
- Files in `/tmp` (and other world-writable dirs): create atomically
  or fail. Use `tempfile` or `mktemp`.

Conffiles vs configuration files (Policy 10.7)
https://www.debian.org/doc/debian-policy/ch-files.html#configuration-files

- Configuration lives in `/etc`. A `conffile` is the subset dpkg
  tracks in the package's `conffiles` list. Not interchangeable.
- Local edits survive upgrade. Config is deleted only on **purge**,
  not on remove.
- Never mix dpkg-conffile style (file shipped in the `.deb`) with
  generated-file style (maintainer scripts write it). Mixing makes
  dpkg prompt on every upgrade.
- No hard links to conffiles. Do not divert conffiles.
- Do not ship `~/.dotfiles` as the Debian default. Site defaults go
  in `/etc`. `/etc/skel` only if the program cannot grow a site-wide
  default and the maintainer cannot add one. Keep skel empty.

Logs (Policy 10.8)
https://www.debian.org/doc/debian-policy/ch-files.html#log-files
https://manpages.debian.org/trixie/logrotate/logrotate.8.en.html

- `/var/log/<pkg>` or `/var/log/<pkg>/` (directory when many files or
  non-root writers).
- logrotate drop-in: `/etc/logrotate.d/<pkg>`.
- Remove logs on **purge**, not on remove.

Locale (Policy 10.9 / upgrading checklist 4.7.1)
https://www.debian.org/doc/debian-policy/ch-files.html#locale-files

Must function in `C` and `C.UTF-8` without any files under
`/usr/share/locale/` existing.

Man and info not required at runtime (Policy 12.1 / 12.2, 4.7.1)
https://www.debian.org/doc/debian-policy/ch-docs.html#manual-pages
https://www.debian.org/doc/debian-policy/ch-docs.html#info-documents

Only man-page readers may require `/usr/share/man/`. Only info readers
may require `/usr/share/info/`. The Application pack still wants a man
page **shipped**.

Devices (Policy 10.6)
https://www.debian.org/doc/debian-policy/ch-files.html#device-files

Never ship device nodes or FIFOs in the `.deb`. Create them at runtime
from units or scripts (`mkfifo`, not `mknod`, for named pipes).

Permissions and filenames (Policy 10.10–10.11)
https://www.debian.org/doc/debian-policy/ch-files.html#permissions-and-owners
https://www.debian.org/doc/debian-policy/ch-files.html#file-names

- Default: `root:root`, mode 644 (files) or 755 (dirs/executables).
- Names on PATH (`/usr/bin`, `/usr/sbin`, `/usr/games`, and the
  usr-merge aliases) **must** be ASCII. Other installed names must be
  UTF-8; prefer ASCII when possible.
- `dpkg-statoverride` is the administrator hook for local owner/mode.
  Ship normal permissions; do not invent a second policy.

------------------------------------------------------------------------
5. INIT, SYSTEMD, AND SYSTEM SERVICES
------------------------------------------------------------------------

Default init and service manager: **systemd** (Policy 9.3.1).
https://www.debian.org/doc/debian-policy/ch-opersys.html#starting-system-services
https://manpages.debian.org/systemd.service

OS rule: a package that automatically starts a system service **must**
ship a systemd unit, unless the service is only for alternate inits.
Optional sysvinit script may exist with the **same name** as the unit
so systemd ignores the script.

Common case: unit named `<package>.service`.

Do not:

- Ship `/etc/rcn.d` links in the `.deb`
- Call `/etc/init.d/*` directly from maintainer scripts
- Use alternatives for systemd configuration files
- Divert systemd configuration files

Use `dh_installsystemd` / `init-system-helpers`. `update-rc.d` and
`invoke-rc.d` are the compatibility tools when scripts still exist.

`/etc/default/<service>` holds administrator knobs; the unit or script
must still work if that file is deleted.

Cron as an OS facility (Policy 9.5):

- Do not edit `/etc/crontab` or `/var/spool/cron/crontabs`
- Drop scripts in `/etc/cron.{hourly,daily,weekly,monthly}` or a file
  in `/etc/cron.d`
- Cron file names: no `.` or `+` (cron ignores them); use `_`

Reboot-required (Policy 9.12):
`touch /run/reboot-required` and append the package name to
`/run/reboot-required.pkgs` if a reboot is needed to finish an upgrade.
No guarantee when the reboot happens.

This pack describes the OS service manager. Whether *your application*
should be a daemon at all is a product question, not Debian OS law.

------------------------------------------------------------------------
6. USERS, GROUPS, AND ENVIRONMENT
------------------------------------------------------------------------

Policy 9.2
https://www.debian.org/doc/debian-policy/ch-opersys.html#users-and-groups

UID/GID classes (do not invent globally allocated ids):

- 0–99 — globally allocated, same on every Debian system (`base-passwd`)
- 100–999 — dynamic system users (`adduser --system`)
- 1000–59999 — normal user accounts
- 60000–64999 — globally allocated, created on demand
- 65534 — nobody / nogroup
- 65535, 4294967294, 4294967295 — forbidden sentinels

New system usernames should start with `_` to avoid colliding with
local people.

Packages other than `base-passwd` must not edit `/etc/passwd`,
`/etc/shadow`, `/etc/group`, `/etc/gshadow` by hand. Use `adduser`.

Non-existent home directory: `/nonexistent`. Autobuilders set `HOME`
there so packages that write to `$HOME` at build time fail.

Environment (Policy 9.9): programs on PATH must not require custom
environment variables for reasonable defaults. No shipping
`/etc/profile.d` hooks as the only configuration. Wrapper scripts that
set defaults are an OS-integration last resort.

Keyboard (Policy 9.8): Backspace deletes left, Delete deletes right,
independent of terminal. Rarely an application-packaging issue; it is
an OS consistency rule.

------------------------------------------------------------------------
7. SHARED LIBRARIES AND MULTIARCH
------------------------------------------------------------------------

Policy ch. 8
https://www.debian.org/doc/debian-policy/ch-sharedlibs.html

The OS ABI is ELF + glibc + the shared libraries in the archive.
Applications on this OS **link against packaged libraries**. They do
not vendor copies of zlib, GTK, or WebKit "for convenience" if Debian
already has them. That is both an OS integrity rule (security updates
flow through apt) and a NEW reject. Static linking against glibc is
Policy 10.1 (section 4).

Multiarch: one dpkg database, libraries co-installable by triplet.
`Architecture: any` binaries use the host triplet path.

Runpath / RPATH: Policy dislikes embedded rpaths that escape the
package. Prefer dpkg-shlibdeps and `Depends` on the SONAME package.

Essential packages and `Priority: required` form the bootable OS. An
application is almost never Essential. Do not declare it so.

------------------------------------------------------------------------
8. CUSTOMIZED PROGRAMS (POLICY 11)
------------------------------------------------------------------------

OS-level program names and paths. Not HIG. Not `debian/control`
field-by-field.
https://www.debian.org/doc/debian-policy/ch-customized-programs.html
Virtual package names (authoritative list):
https://www.debian.org/doc/packaging-manuals/virtual-package-names-list.yaml

Editor and pager (Policy 11.4)
https://www.debian.org/doc/debian-policy/ch-customized-programs.html#editors-and-pagers

- Launchers use `$EDITOR` / `$VISUAL` and `$PAGER`. Unset ⇒
  `/usr/bin/editor` and `/usr/bin/pager` (alternatives).
- Packages that *are* an editor or pager register those alternatives
  (with a slave man page). `sensible-editor` / `sensible-pager` are
  the fallback wrappers.

`x-terminal-emulator` (Policy 11.8.3)
https://www.debian.org/doc/debian-policy/ch-customized-programs.html#packages-providing-a-terminal-emulator

- `Provides: x-terminal-emulator` and an alternative at
  `/usr/bin/x-terminal-emulator`.
- `-e command`: `command` may be multiple arguments, passed as if to
  `execvp`, **bypassing the shell**. (`xterm`'s single-arg shell
  fallback is permitted, not required.)
- `-T title` sets the window title. VT100-compatible.

`x-window-manager` (Policy 11.8.4): `Provides` plus alternative at
`/usr/bin/x-window-manager`. Priority starts at 40; +40 for EWMH;
+10 if the default config can switch WM without killing the X server.

Other OS virtual names that actually bite:

- `www-browser` — something that can browse HTML
- `dbus-session-bus` / `default-dbus-session-bus` — session bus vs
  Debian's preferred implementation
- `logind` / `default-logind` — `org.freedesktop.login1` (versioned
  Provides) vs Debian's preferred implementation

Web (Policy 11.5)
https://www.debian.org/doc/debian-policy/ch-customized-programs.html#web-servers-and-applications

- Document root: `/var/www/html`
- CGI: `/usr/lib/cgi-bin` (URL `/cgi-bin/...`)
- Prefer `/usr/share/doc/<package>/` over stuffing the document root.
- Images: `/usr/share/images/<package>`, aliased as `/images/`
- Servers `Provide: httpd` and `httpd-cgi` when they have CGI.

X (Policy 11.8)
https://www.debian.org/doc/debian-policy/ch-customized-programs.html#programs-for-the-x-window-system

- Fonts: `/usr/share/fonts/X11/{100dpi,75dpi,misc,Type1}/`
- `/usr/X11R6` is gone. Do not install there. App-defaults:
  `/etc/X11/app-defaults/`, not old X11R6 paths.
- Includes that used to live under X11R6 go to `/usr/include/X11/`.

alternatives and diversions are OS namespace tools, not a packaging
style guide.
https://www.debian.org/doc/debian-policy/ap-pkg-alternatives.html
https://www.debian.org/doc/debian-policy/ap-pkg-diversions.html
https://www.debian.org/doc/debian-policy/ch-binary.html#maintainer-scripts

- Same command name, cooperating packages: `update-alternatives`.
- Last-resort file hijack: `dpkg-divert`. Prefer native override
  mechanisms (Policy 3.9 / upgrading checklist 4.7.0).
  https://www.debian.org/doc/debian-policy/upgrading-checklist.html#version-4-7-0
- **Must not** divert systemd configuration (units, udev rules,
  tmpfiles, sysusers, `system.conf`, …). Use drop-ins and masks.
- **Must not** use alternatives for systemd configuration files.
- Do not divert conffiles. Coordinate with the other maintainer
  before diverting their file. Pass `--package`, never `--local`.

------------------------------------------------------------------------
9. DESKTOP-AGNOSTIC SESSION
------------------------------------------------------------------------

Debian the OS does not require GNOME, KDE, or any GUI.

Policy 9.6 (menus) and 9.7 (multimedia handlers) are **OS integration
hooks** for when a GUI *is* installed:

- Desktop entries in `/usr/share/applications` (Freedesktop)
  https://specifications.freedesktop.org/desktop-entry-spec/latest/
- MIME via desktop `MimeType` and/or
  `/usr/share/mime/packages/<id>.xml`
- If you ship a Freedesktop desktop entry, do **not** also ship a
  legacy Debian menu file
- mailcap is generated from desktop entries; do not double-register

Minima Policy states for a visible menu entry (OS-level, not HIG):

- PNG or SVG icon, transparent background, at least 22×22, preferably
  up to 64×64; hicolor encouraged
- `NoDisplay=true` if the entry is not useful standalone
- Coordinate `OnlyShowIn` / `NotShowIn` with debian-desktop if the
  package is part of an install task

AppStream on Debian is how **GNOME Software / Discover / the OS
software center** see `.deb` applications:
https://wiki.debian.org/AppStream
https://wiki.debian.org/AppStream/Guidelines
https://appstream.debian.org/

Install metainfo at `/usr/share/metainfo/`. That is this OS's placement.
What the XML *says* (summary quality, screenshots, OARS) is application
content: Debian Application minima, plus GNOME Application if the UI is
GNOME-shaped.

Display managers, PipeWire, NetworkManager, and the default desktop
task are package selections. They are not a second Debian Policy.

When the user session is GNOME, **session** services (portals, settings
daemon, Shell) come from the GNOME OS pack. The `.deb` still obeys this
pack for paths and apt.

------------------------------------------------------------------------
10. SECURITY UPDATES AND TRUST
------------------------------------------------------------------------

Debian Security
https://www.debian.org/security/
https://security-tracker.debian.org/tracker/
LTS: https://www.debian.org/lts/
https://wiki.debian.org/LTS

Stable gets DSAs. LTS gets DLAs after the Security team hands over.
The OS promise is that a user of `main` can apply security updates with
apt without rebuilding the world.

Security support clock (suite-specific; Debian 13 as the concrete
stable example):

- Debian 13 (Trixie) released **2025-08-09**; point **13.6** as of
  **2026-07-11**.
  https://www.debian.org/releases/trixie/
- Debian Security (DSA) until **~2028-08-09**.
- LTS (DLA) until **2030-06-30**.
- Bookworm (Debian 12) is LTS (until 2028-06-30).
  https://www.debian.org/News/2026/20260712
- Bullseye (Debian 11) LTS ends **2026-08-31**.
- ELTS is **unofficial** (third-party paid extension, not Debian).
  https://www.debian.org/lts/

A `.deb` in `main` inherits distro security. Vendored crypto, TLS, or
WebKit does **not**. Depend on the archive's shared libraries.

Implications for payloads on this OS:

- Depend on distro shared libraries that receive security support
  (especially browsers, WebKit, OpenSSL, media codecs)
- Do not embed a private copy of a security-sensitive library if Debian
  already ships it
- `no-network` during the official package build (application pack
  details; OS archive rule is that builds are from source in the
  archive)

Reboot-required is the OS signal after kernel or certain library
upgrades (Policy 9.12).

------------------------------------------------------------------------
11. REPRODUCIBLE BUILDS (ARCHIVE QUALITY)
------------------------------------------------------------------------

https://reproducible-builds.org/
https://wiki.debian.org/ReproducibleBuilds/Howto
https://reproduce.debian.net/
https://tests.reproducible-builds.org/debian/reproducible.html

Same source + same declared build environment ⇒ bit-for-bit identical
`.deb` files.

Typical unreproducibility: timestamps, unsorted file lists, embedded
hostname/username/build path, gzip headers, compiler output without
`SOURCE_DATE_EPOCH`.

Tooling: `reprotest`, `debrebuild` / `debootsnap`, `.buildinfo`.

Status as of 2026: the Release Team blocks unreproducible **new**
packages and reproducibility regressions from migrating into testing
(Forky and later), with limited exceptions. That is a
**testing-migration OS gate**, not a NEW-queue legality rule, and not
a Flatpak rule.

------------------------------------------------------------------------
12. WHAT THIS PACK EXPLICITLY IS NOT
------------------------------------------------------------------------

Not application packaging procedure (ITP, `debian/rules`, lintian,
tag2upload, DEP-8, `Standards-Version` three-digit bookkeeping). That
is the Debian Application pack.

Not a dump of Debian Policy chapters 10–11. This pack lists the OS
rules that reject or mis-ship; Policy is the contract.

Not "how Debian people actually work." That is the Developer's
Reference (cited once in section 1). Do not steal Application chapters
from it.

Not "how a GNOME app should look." HIG is GNOME Application.

Not Flatpak. GNOME's preferred *app* distribution is a GNOME OS opinion.
Debian's OS distribution is apt.

Not systemd upstream's image-based vision (Discoverable Disk Images,
sysext). Debian stable is a traditional mutable `/` with usr-merge.
GNOME OS images are the GNOME OS pack.

------------------------------------------------------------------------
13. COMPOSING WITH OTHER PACKS
------------------------------------------------------------------------

`.deb` of a CLI tool:

  Debian OS + Debian Application

`.deb` of a GNOME-shaped GUI:

  Debian OS + Debian Application + GNOME Application
  + GNOME OS *session* (portals, Shell) at runtime

Do not add GNOME OS *payload* (Flathub, `/app`, GNOME runtime EOL).

Flatpak of the same GUI:

  GNOME OS (payload + session) + GNOME Application
  Debian OS does not apply to that artifact.

License: DFSG (this pack, for `main`) and debian/copyright (Debian
Application) and OSI/SPDX in metainfo (GNOME Application) can all hold
at once. GPL-2/3, LGPL, BSD, MIT, Apache-2.0 generally do.

------------------------------------------------------------------------
14. QUICK OFFICIAL LINK LIST
------------------------------------------------------------------------

Policy
https://www.debian.org/doc/debian-policy/

Social Contract + DFSG
https://www.debian.org/social_contract

FHS
https://specifications.freedesktop.org/fhs/latest
https://www.debian.org/doc/packaging-manuals/fhs/

usr-merge
https://wiki.debian.org/UsrMerge

Operating system chapter
https://www.debian.org/doc/debian-policy/ch-opersys.html

Files chapter (Policy 10)
https://www.debian.org/doc/debian-policy/ch-files.html

Customized programs (Policy 11)
https://www.debian.org/doc/debian-policy/ch-customized-programs.html

Virtual packages
https://www.debian.org/doc/packaging-manuals/virtual-package-names-list.yaml

logrotate
https://manpages.debian.org/trixie/logrotate/logrotate.8.en.html

Archive areas
https://www.debian.org/doc/debian-policy/ch-archive.html

apt / packages
https://packages.debian.org/
https://www.debian.org/distrib/packages

Security and LTS
https://www.debian.org/security/
https://www.debian.org/lts/
https://wiki.debian.org/LTS
https://www.debian.org/releases/trixie/

Reproducible Builds
https://reproducible-builds.org/
https://wiki.debian.org/ReproducibleBuilds/Howto

AppStream (Debian)
https://wiki.debian.org/AppStream/Guidelines

Sister packs
./debian-application-policy.md
./gnome-os-policy.md
./gnome-application-policy.md
./README.md

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.0.0 | Initial four-pack split |
| 1.1.0 | Reliability pins + Policy 10–11 OS rules that reject/mis-ship + LTS clock |
