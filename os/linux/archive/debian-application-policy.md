---
title: "Debian Application Policy"
description: Curated map of Debian Policy as it applies to an application package — control, copyright, lintian, ITP, NEW. Not FHS/apt internals and not HIG.
version: "1.0.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - README.md
  - debian-os-policy.md
  - gnome-os-policy.md
  - gnome-application-policy.md
last_updated: "2026-08-25"
---

# Debian Application Policy

Reference pack for **what Debian requires of an application as a
package**: source and binary metadata, copyright documentation, build
in a clean chroot, quality checks, and the path into apt.

**Role:** curated map (working memory). **Not** L4 for any one product.
**Not** the OS filesystem/init/archive map — that is
[debian-os-policy.md](debian-os-policy.md).
**Not** the HIG — that is
[gnome-application-policy.md](gnome-application-policy.md).

Last verified against official Debian documents as of 2026-08-25.
Debian Policy **4.7.4.1** (2026-03-31).
`Standards-Version` in `debian/control` uses **three digits** (`4.7.4`),
not `4.7.4.1`.

Policy is "what must be true of the package."
Developer's Reference is "how Debian people actually work."
Guides teach packaging. Mentors/NEW decide whether it lands.

Daily development may stay uninstalled. This pack applies when producing
an installable `.deb` or a source package for the archive.

------------------------------------------------------------------------
0. LAYERING
------------------------------------------------------------------------

This pack owns:

- Binary and source package rules (Policy ch. 3–5)
- `debian/control`, `debian/copyright`, `debian/changelog`, `debian/rules`
- Package relationships (Depends, Conflicts, …)
- Maintainer scripts as *package* behavior
- Man pages and `/usr/share/doc/<package>/` as Policy documentation
- Desktop / AppStream files as **packaging artifacts** (exist, validate,
  install under the OS prefix)
- lintian, sbuild, ITP, RFS, NEW legality review

This pack does **not** own:

- FHS, usr-merge, systemd, apt suite graph
  → [debian-os-policy.md](debian-os-policy.md)
- HIG naming, Adwaita widgets, Orca testing, Circle app quality
  → [gnome-application-policy.md](gnome-application-policy.md)
- Flatpak manifests, Flathub, GNOME runtime
  → [gnome-os-policy.md](gnome-os-policy.md)

Compose a GNOME GUI `.deb` as:

  Debian OS + Debian Application + GNOME Application

Same `.desktop` file: this pack requires it to exist and validate; GNOME
Application requires HIG Name/icon/summary; Debian OS requires
`/usr/share/applications/`.

------------------------------------------------------------------------
1. FOUNDATIONAL DOCUMENTS
------------------------------------------------------------------------

Debian Policy Manual (application chapters)
https://www.debian.org/doc/debian-policy/
Upgrading checklist:
https://www.debian.org/doc/debian-policy/upgrading-checklist.html

Key chapters for an application package:

- Ch. 2 Archive areas (which area *this package* may enter)
  https://www.debian.org/doc/debian-policy/ch-archive.html
- Ch. 3 Binary packages
  https://www.debian.org/doc/debian-policy/ch-binary.html
- Ch. 4 Source packages
  https://www.debian.org/doc/debian-policy/ch-source.html
- Ch. 5 Control files and fields
  https://www.debian.org/doc/debian-policy/ch-controlfields.html
- Ch. 6 Maintainer scripts
  https://www.debian.org/doc/debian-policy/ch-maintainerscripts.html
- Ch. 7 Package relationships
  https://www.debian.org/doc/debian-policy/ch-relationships.html
- Ch. 12 Documentation
  https://www.debian.org/doc/debian-policy/ch-docs.html

DFSG (whether `main` is allowed) is archive law in the OS pack. This
pack documents the license in `debian/copyright` so NEW can check it.

Developer's Reference
https://www.debian.org/doc/manuals/developers-reference/
New packages:
https://www.debian.org/doc/manuals/developers-reference/pkgs.html
New maintainer:
https://www.debian.org/doc/developers-reference/new-maintainer.html

------------------------------------------------------------------------
2. PACKAGING TUTORIALS
------------------------------------------------------------------------

Guide for Debian Maintainers (preferred modern tutorial)
HTML: https://www.debian.org/doc/manuals/debmake-doc/
Index: https://www.debian.org/doc/devel-manuals#debmake-doc
Package: debmake-doc
Git: https://salsa.debian.org/debian/debmake-doc

Debian New Maintainers' Guide (older, still useful)
https://www.debian.org/doc/manuals/maint-guide/index.en.html
Official pages say use Guide for Debian Maintainers as primary.

Packaging tutorial (Lucas Nussbaum PDF)
https://www.debian.org/doc/manuals/packaging-tutorial/packaging-tutorial.en.pdf

Packaging portal
https://wiki.debian.org/Packaging

Mentors intro
https://mentors.debian.net/intro-maintainers

Language-specific addenda (when the application is in that language):

- Python: https://www.debian.org/doc/packaging-manuals/python-policy/
- Perl: https://www.debian.org/doc/packaging-manuals/perl-policy/
- Java: https://www.debian.org/doc/packaging-manuals/java-policy/
- Emacs: https://www.debian.org/doc/packaging-manuals/debian-emacs-policy
- Rust crates in Debian have extra archive practice (crate packages vs
  vendored binary). That is still this pack, not OS FHS.

------------------------------------------------------------------------
3. PACKAGE IDENTITY AND CONTROL
------------------------------------------------------------------------

Policy ch. 3 and ch. 5
https://www.debian.org/doc/debian-policy/ch-binary.html
https://www.debian.org/doc/debian-policy/ch-controlfields.html

Binary package name: lowercase, unique in the archive. Collisions with
an existing package name are a NEW reject.

Source package vs binary package may differ (one source, several
binaries). GUI apps are often one binary named after the program.

`debian/control` must-haves:

- Source and binary names
- Maintainer (and Uploaders if any)
- Section, Priority
- Standards-Version (three digits, e.g. `4.7.4`)
- Build-Depends
- Depends / Recommends / Suggests / Breaks / Replaces / Conflicts
- Homepage, Vcs-Git, Vcs-Browser
- Short Description (one line) and long Description (extended)

Description rules that reviewers actually apply:

- Short description is not a sentence with a full stop
- Long description explains what the user gets, not only the toolkit
- Do not start the long description by repeating the short one poorly
- Homepage should work

Section for a desktop utility is typically `editors`, `utils`, `gnome`,
`graphics`, etc. `Priority: optional` is the usual application value.
Never `required` / `essential` for a normal app.

The **application ID** used by GNOME (reverse DNS) is *not* the Debian
package name. Package `md-edit` may ship ID
`io.github.example.App`. GNOME Application pack owns the ID string.
This pack owns the dpkg name.

------------------------------------------------------------------------
4. LICENSE AND COPYRIGHT (PACKAGE DOCUMENTATION)
------------------------------------------------------------------------

Machine-readable `debian/copyright` (DEP-5 / copyright-format 1.0)
https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Wiki: https://wiki.debian.org/debian/copyright

Required ideas, even if format-1.0 is formally optional:

- Every file's copyright holder and license must be documented
- License must be DFSG-free for `main` (OS pack)
- Include the full license text or a standard short name plus text
- Do not ship non-free fonts, icons, or generated blobs without source
- Do not ship convenience copies of libraries Debian already has; link
  against packaged libs (OS ABI + this pack)

Common NEW rejects:

- Missing source for minified JS, PDFs, or binaries
- Unclear license on images/icons
- "All rights reserved" files mixed into an otherwise free tree
- Generated files treated as preferred form of modification
- Source renamed only because DFSG files were stripped
  (use `+dfsg` in the version instead)

NEW-queue priority #1 is legality and DFSG, not polish.

SPDX in AppStream `project_license` is GNOME/AppStream metadata (GNOME
Application pack). It must not contradict `debian/copyright`. It does
not replace `debian/copyright`.

------------------------------------------------------------------------
5. REQUIRED PACKAGING FILES
------------------------------------------------------------------------

Typical `debian/` directory:

debian/control
- Metadata listed in section 3
https://www.debian.org/doc/debian-policy/ch-controlfields.html

debian/copyright
https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/

debian/changelog
- Debian revision history
- First official upload should close the ITP: `Closes: #NNNNNN`

debian/rules
- Build script (makefile)
- Modern default: dh sequencer (debhelper)
https://manpages.debian.org/debhelper
https://manpages.debian.org/dh

debian/source/format
- Almost always: `3.0 (quilt)`

debian/watch
- Lets uscan detect new upstream versions
https://wiki.debian.org/debian/watch

debian/install or dh_auto_install from the upstream build
- Must land files on FHS paths (OS pack)

Maintainer scripts (preinst, postinst, prerm, postrm)
https://www.debian.org/doc/debian-policy/ch-maintainerscripts.html
- Idempotent; no interactive questions without debconf
- Do not fail the whole OS on a missing optional helper
- Prefer dpkg triggers (glib-compile-schemas, mime, icons) over
  handwritten cache updates
- No network

Man page
- Policy: each program should have a man page
- Missing man page is considered a bug
https://www.debian.org/doc/debian-policy/ch-docs.html
Install: `/usr/share/man/man1/<binary>.1`

`/usr/share/doc/<package>/`
- copyright (required)
- changelog.Debian.gz
- upstream changelog if reasonable
- examples under `examples/`

------------------------------------------------------------------------
6. DESKTOP, MIME, AND APPSTREAM AS PACKAGING ARTIFACTS
------------------------------------------------------------------------

This section is **does the package ship the files Debian's software
centers need**. How the UI is named and how screenshots look is GNOME
Application (if GNOME-shaped) or generic Freedesktop taste.

Desktop entry
https://specifications.freedesktop.org/desktop-entry-spec/latest/
Policy 9.6 (OS also cites this): `/usr/share/applications/`
Validate: `desktop-file-validate`

Minimum this pack cares about:

- File is installed
- Name, Comment, Exec, Icon, Type=Application
- Categories includes a registered main category
- Exec uses `%f` / `%F` / `%u` / `%U` correctly if it opens files
- Does not ship `mimeapps.list` that hijacks defaults unless that is
  the explicit job of a desktop-task package

AppStream metainfo
https://www.freedesktop.org/software/appstream/docs/
https://wiki.debian.org/AppStream
https://wiki.debian.org/AppStream/Guidelines
Install: `/usr/share/metainfo/<id>.metainfo.xml`
Validate: `appstreamcli validate`

Minimum this pack cares about:

- Valid XML
- id, name, summary, metadata_license, project_license
- launchable matching the desktop file
- component type `desktop-application` for a GUI

Icons
https://specifications.freedesktop.org/icon-theme-spec/latest/
hicolor, named after the desktop Icon key. Policy 9.6 minima (22×22 PNG
or SVG). GNOME Application asks for scalable + symbolic; that is extra
application-ecosystem quality, still installed via this package.

MIME package if you own a type:
`/usr/share/mime/packages/<id>.xml`
Do not also mailcap-register if you already have a desktop MimeType
(Policy 9.7.2).

GSettings schemas (if the app uses GSettings):
`/usr/share/glib-2.0/schemas/<id>.gschema.xml`
Compilation is a dpkg trigger from glib, not a custom postinst, when
Depends pull in GTK/GLib.

------------------------------------------------------------------------
7. QUALITY CHECKS BEFORE UPLOAD
------------------------------------------------------------------------

lintian (static policy checker)
Tags: https://lintian.debian.org/
Git: https://salsa.debian.org/lintian/lintian
Typical:

  lintian -i -I --pedantic *.changes

NEW reviewers expect no serious lintian errors. Warnings should be
understood and either fixed or justified.

Other checks:

- `desktop-file-validate` on every .desktop
- `appstreamcli validate` on metainfo
- Build in a clean chroot (sbuild or pbuilder), not only the laptop
- Test install, remove, purge, and upgrade
- No embedded copies of other projects
- No files outside the package tree during build except `/tmp`
- Reproducible build (OS pack explains the testing-migration gate;
  new applications should still treat it as a hard goal)

sbuild
https://wiki.debian.org/sbuild

autopkgtest / DEP-8 when you have tests worth running on the installed
package: `debian/tests/control`.

------------------------------------------------------------------------
8. SUBMISSION PROCESS
------------------------------------------------------------------------

Step A — Confirm it is not already packaged
https://packages.debian.org/
Also search WNPP so you do not duplicate an ITP.

Step B — File an ITP (Intent To Package)
https://www.debian.org/devel/wnpp/
https://wiki.debian.org/ITP
https://wiki.debian.org/WNPP
https://wnpp.debian.net/

  reportbug wnpp

Choose ITP. Include name, description, license, upstream URL.

Step C — Package it using Policy + a maintainer guide (this pack) and
the OS pack for paths.

Step D — Find a sponsor (you cannot upload until you are a DD/DM)
https://mentors.debian.net/
https://mentors.debian.net/intro-maintainers
https://mentors.debian.net/sponsors/
https://mentors.debian.net/sponsors/rfs-howto/
https://wiki.debian.org/DebianMentorsFaq
debian-mentors@lists.debian.org
https://lists.debian.org/debian-mentors/

File an RFS bug against sponsorship-requests after upload to mentors.

Step E — Sponsor uploads to incoming. Package hits NEW.

NEW / DFSG review
https://dfsg-new-queue.debian.org/
https://dfsg-new-queue.debian.org/dashboard
https://wiki.debian.org/NewQueue
https://wiki.debian.org/Teams/DFSG
Reject FAQ: https://ftp-master.debian.org/REJECT-FAQ.html
Queue times: https://people.debian.org/~roehling/new_queue/

NEW checking priorities:

1. Keep the archive legal (DFSG + distributable)
2. Keep the package namespace sane
3. Reduce obvious bugs

After accept: unstable (sid) → testing → stable.
You remain the listed Maintainer. Sponsors upload. You fix bugs.

Getting into Debian does not make the app a GNOME Circle or Core app.
Getting into Circle does not put the app in apt.
[README.md](README.md) composition table.

------------------------------------------------------------------------
9. WHAT REVIEWERS TYPICALLY LOOK FOR
------------------------------------------------------------------------

From Policy, Reject FAQ, and DFSG team materials:

Must-haves

- DFSG-free source for everything shipped (or honest non-free area)
- Accurate debian/copyright
- Unique, sensible package name
- Builds in a clean environment
- Follows FHS / usr-merge (OS pack)
- Valid control fields and current Standards-Version
- No filename clashes on PATH
- Useful Description
- Homepage and Vcs fields
- ITP referenced in changelog

Strong expectations

- lintian-clean of errors
- Man page
- Desktop file + AppStream metainfo for a GUI
- Reproducible build
- watch file
- No vendored libraries Debian already has
- Reasonable Depends (not bloated, not missing)

Common rejects

- Non-free or undocumented files
- Missing preferred form of modification
- Convenience copies of system libraries
- Broken helper output in debian/control
- Toy / duplicate package with no clear benefit
- Immature 0.x code with no real users or docs
- DFSG-stripped source without `+dfsg` version

Not this pack's rejects (send elsewhere):

- "Does not follow the HIG" → GNOME Application
- "Not on Flathub" / "EOL GNOME runtime" → GNOME OS
- "org.gnome.* trademark" → GNOME Application / GNOME OS identity

------------------------------------------------------------------------
10. RELATIONSHIPS AND DEPENDENCIES
------------------------------------------------------------------------

Policy ch. 7
https://www.debian.org/doc/debian-policy/ch-relationships.html

- Depends: required to run
- Recommends: expected for normal use
- Suggests: extra
- Breaks + Replaces: file moves and upgrades
- Conflicts: last resort
- Provides: virtual packages (mail-transport-agent, www-browser, …)
- Build-Depends: build-time only

GUI toolkit apps Depends on the **shared libraries** Debian ships, not
on a bundled GTK. Versioned Depends match the SONAME / .so version you
built against.

Do not Depends on another desktop's entire meta-package "to be safe."

Vendoring: if archive policy for that language (Rust crates, minified
JS) makes a proper library package impractical, document it in
copyright and the package README. NEW still wants source for minified
files. That is this pack plus DFSG (OS pack), not a GNOME rule.

------------------------------------------------------------------------
11. AFTER ACCEPTANCE
------------------------------------------------------------------------

You stay responsible.

- Bugs: https://bugs.debian.org/<package>
- Upload new upstream versions
- Fix RC bugs before the freeze
- Keep Standards-Version current
- If you disappear, the package can be orphaned (O) or removed

Debian Maintainer later
https://wiki.debian.org/DebianMaintainer
https://www.debian.org/devel/join/newmaint
https://nm.debian.org/

Application-level HIG regressions are not RC unless they make the
package unusable. RC is "the OS cannot release with this bug."

------------------------------------------------------------------------
12. QUICK OFFICIAL LINK LIST
------------------------------------------------------------------------

Policy
https://www.debian.org/doc/debian-policy/

Copyright format
https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/

Developer's Reference
https://www.debian.org/doc/manuals/developers-reference/

Guide for Debian Maintainers
https://www.debian.org/doc/manuals/debmake-doc/

New Maintainers' Guide
https://www.debian.org/doc/manuals/maint-guide/index.en.html

WNPP / ITP
https://www.debian.org/devel/wnpp/

Mentors
https://mentors.debian.net/

NEW / DFSG team
https://dfsg-new-queue.debian.org/

Reject FAQ
https://ftp-master.debian.org/REJECT-FAQ.html

lintian
https://lintian.debian.org/

AppStream (Debian)
https://wiki.debian.org/AppStream/Guidelines

Packages search
https://packages.debian.org/

Sister packs
./debian-os-policy.md
./gnome-application-policy.md
./gnome-os-policy.md
./README.md
