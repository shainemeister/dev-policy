---
title: "Debian Application Policy"
description: Curated map of Debian Policy as it applies to an application package — control, copyright, build contract, lintian, ITP, NEW. Not FHS/apt internals and not HIG.
version: "1.1.0"
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
package**: source and binary metadata, copyright documentation, the
`debian/rules` build contract, quality checks, and the path into apt.

**Role:** curated map (working memory). **Not** L4 for any one product.
**Not** the OS filesystem/init/archive map — that is
[debian-os-policy.md](debian-os-policy.md).
**Not** the HIG — that is
[gnome-application-policy.md](gnome-application-policy.md).

Last verified against official Debian documents as of 2026-08-25.
Debian Policy **4.7.4.1** (2026-03-31).
`Standards-Version` in `debian/control` uses **three digits** (`4.7.4`),
not `4.7.4.1`.

Developer's Reference **14.14** (2026-06-25).

Policy is "what must be true of the package."
Developer's Reference is "how Debian people actually work."
Guides teach packaging. Mentors and the DFSG, Licensing & New Packages
Team decide whether it lands.

Daily development may stay uninstalled. This pack applies when producing
an installable `.deb` or a source package for the archive.

Watch https://lists.debian.org/debian-devel-announce/ for freeze dates,
DFSG-team process, and the AI GR (section 13).

------------------------------------------------------------------------
0. LAYERING
------------------------------------------------------------------------

This pack owns:

- Binary and source package rules (Policy ch. 3–5)
- `debian/control`, `debian/copyright`, `debian/changelog`, `debian/rules`
- The `debian/rules` build contract (Policy 4.9) and related source
  files (`README.source`, `missing-sources`, patches, watch, tests)
- Package relationships (Depends, Conflicts, Built-Using, …)
- Maintainer scripts as *package* behavior
- Man pages and `/usr/share/doc/<package>/` as Policy documentation
- Desktop / AppStream files as **packaging artifacts** (exist, validate,
  install under the OS prefix)
- lintian, sbuild, salsa CI, autopkgtest, ITP, RFS, NEW legality review
- tag2upload / git-debpush as an upload path

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
- Ch. 4 Source packages (build contract lives here)
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

Developer's Reference 14.14 (2026-06-25)
https://www.debian.org/doc/manuals/developers-reference/
New packages and uploads:
https://www.debian.org/doc/manuals/developers-reference/pkgs.en.html
New maintainer:
https://www.debian.org/doc/manuals/developers-reference/new-maintainer.en.html
Tools appendix:
https://www.debian.org/doc/manuals/developers-reference/tools.en.html

NEW review is the **DFSG, Licensing & New Packages Team** (DPL
delegation, January 2026), not a single ftp-master person. Archive
operations is a separate team.

https://lists.debian.org/debian-devel-announce/2026/01/msg00008.html
https://lists.debian.org/debian-devel-announce/2026/01/msg00010.html
https://wiki.debian.org/Teams/DFSG
https://dfsg-new-queue.debian.org/

Do **not** cite https://ftp-master.debian.org/REJECT-FAQ.html or
https://ftp-master.debian.org/NEW-checklist.html (both 404 as of
2026-08-25). Use the live NEW queue, rejection-mail decoder, salsa
ftp-team website, NewQueue wiki, and the DFSG dashboard instead
(section 9).

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
  vendored binary). That is still this pack, not OS FHS. Use
  `Static-Built-Using` for the static bits (section 3).

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

Potentially offensive material split into its own binary uses the
`-offensive` suffix (Policy 3.1.1). Suggest it; do not Depends or
Recommends it from the core package.
https://www.debian.org/doc/debian-policy/ch-binary.html#packages-with-potentially-offensive-content

The **application ID** used by GNOME (reverse DNS) is *not* the Debian
package name. Package `md-edit` may ship ID
`io.github.example.App`. GNOME Application pack owns the ID string.
This pack owns the dpkg name.

`debian/control` must-haves (source stanza unless noted):

- Source and binary names
- Maintainer (and Uploaders if any; a team Maintainer requires at least
  one human in Uploaders)
- Section
- Standards-Version (three digits, e.g. `4.7.4`)
- Build-Depends
- Homepage, Vcs-Git, Vcs-Browser (https URLs)
- Short Description (one line) and long Description (extended) on each
  binary stanza
- Depends / Recommends / Suggests / Breaks / Replaces / Conflicts as
  needed on binary stanzas

**Priority (Policy 4.7.3 / 5.6.6).** Omit `Priority` on the source
stanza unless you are overriding the default. Default is `optional`;
binaries inherit. Never `required` / `essential` for a normal app.
https://www.debian.org/doc/debian-policy/ch-controlfields.html#priority
https://www.debian.org/doc/debian-policy/upgrading-checklist.html#version-4-7-3

Description rules that reviewers actually apply:

- Short description is not a sentence with a full stop
- Long description explains what the user gets, not only the toolkit
- Do not start the long description by repeating the short one poorly
- Homepage should work

Section for a desktop utility is typically `editors`, `utils`, `gnome`,
`graphics`, etc.

**Rules-Requires-Root.** Prefer `no`.
https://www.debian.org/doc/debian-policy/ch-controlfields.html#rules-requires-root

**Testsuite + DEP-8.** If `debian/tests/control` exists, dpkg adds
`Testsuite: autopkgtest` to the `.dsc`. Write as-installed tests there.
https://www.debian.org/doc/debian-policy/ch-controlfields.html#testsuite
https://dep-team.pages.debian.net/deps/dep8/
https://ci.debian.net/

**Git-Tag-Tagger and Git-Tag-Info (Policy 4.7.3 / 5.6.32–33).** Present
only on uploads produced by tag2upload. Do not invent them by hand.
tag2upload / `git-debpush` is a real upload path (section 9).
https://www.debian.org/doc/debian-policy/ch-controlfields.html#git-tag-tagger
https://wiki.debian.org/tag2upload
https://manpages.debian.org/unstable/git-debpush/tag2upload.5.en.html
https://manpages.debian.org/unstable/git-debpush/git-debpush.1.en.html

**Multi-Arch.** Set `same` / `foreign` / `allowed` when the binary is a
library or a Multi-Arch helper. A normal GUI app on `Architecture: any`
usually omits the field (meaning `no`).
https://www.debian.org/doc/debian-policy/ch-controlfields.html#multi-arch

**Built-Using** (Policy 7.8) when a license/DFSG duty requires the
archive to retain the exact source that was incorporated (static copies
with copyleft obligations).
https://www.debian.org/doc/debian-policy/ch-relationships.html#additional-source-packages-used-to-build-the-binary-built-using

**Static-Built-Using** for Rust/Go/header-only/static rebuild tracking.
The archive does *not* retain those versions. If the license also
requires retained source, list the same package in `Built-Using` too.
https://manpages.debian.org/unstable/dpkg-dev/deb-control.5.en.html

**Epochs and `+really` (Policy 5.6.12).** Do not bump the epoch without
consensus on debian-devel. To roll back an upload, use
`2.3+really2.2-1`, not a new epoch.
https://www.debian.org/doc/debian-policy/ch-controlfields.html#s-f-version

**`+dfsg`.** When DFSG-nonfree files are stripped from the orig tarball,
put `+dfsg` in the upstream version. Drive the strip from
`Files-Excluded` in `debian/copyright` plus uscan (section 4).

**DEP-12** `debian/upstream/metadata` — YAML about *upstream* (bug
tracker, repository, citations). Not a substitute for Homepage or
`debian/copyright`.
https://dep-team.pages.debian.net/deps/dep12/

**DEP-14** branch and tag layout for packaging Git
(`debian/latest`, `debian/<version>` tags, `upstream/latest`).
https://dep-team.pages.debian.net/deps/dep14/

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

**Files-Excluded** in the copyright header stanza tells uscan /
mk-origtargz which paths to drop when repacking. Pair it with a
`+dfsg` (or similar) version and a watch `repacksuffix`.
https://wiki.debian.org/UscanEnhancements
https://manpages.debian.org/unstable/devscripts/uscan.1.en.html

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
- Build script (makefile). Contract in section 6.
https://www.debian.org/doc/debian-policy/ch-source.html#main-building-script-debian-rules
https://manpages.debian.org/debhelper
https://manpages.debian.org/dh

debian/source/format
- Almost always: `3.0 (quilt)`

debian/watch
- Lets uscan detect new upstream versions
https://wiki.debian.org/debian/watch
https://www.debian.org/doc/debian-policy/ch-source.html#upstream-source-location-debian-watch

When upstream signs releases (Policy 4.1.0 / 4.11): ship
`debian/upstream/signing-key.asc` and set `pgpsigurlmangle` (or the
equivalent uscan v5 signing config) so uscan can verify.
https://manpages.debian.org/unstable/devscripts/uscan.1.en.html

debian/install or dh_auto_install from the upstream build
- Must land files on FHS paths (OS pack)

debian/README.source (Policy 4.14)
- Required when `dpkg-source -x` is not enough to edit and rebuild.
  Explain how to patch, unpatch, and import a new upstream.
https://www.debian.org/doc/debian-policy/ch-source.html#source-package-handling-debian-readme-source

debian/missing-sources (Policy 4.16)
- Preferred-form-of-modification for minified/generated files that
  upstream did not ship, *or* repack the orig tarball instead.
https://www.debian.org/doc/debian-policy/ch-source.html#missing-sources-debian-missing-sources

debian/patches (3.0 quilt)
- DEP-3 headers (`Description`/`Subject`, `Origin` or `Author`,
  `Forwarded`, `Bug`).
https://dep-team.pages.debian.net/deps/dep3/
- Vendor-specific series files (`debian/patches/foo.series`) **must
  not** be used (Policy 4.17).
https://www.debian.org/doc/debian-policy/ch-source.html#vendor-specific-patch-series

debian/tests/control
- DEP-8 as-installed tests (section 3).

debian/upstream/metadata
- DEP-12 (section 3).

Maintainer scripts (preinst, postinst, prerm, postrm)
https://www.debian.org/doc/debian-policy/ch-maintainerscripts.html
- Idempotent; no interactive questions without debconf
- Do not fail the whole OS on a missing optional helper
- Prefer dpkg triggers (glib-compile-schemas, mime, icons) over
  handwritten cache updates
- No network

Conffiles (packaging — how dpkg treats them)
https://www.debian.org/doc/debian-policy/ch-files.html#configuration-files
https://manpages.debian.org/unstable/dpkg/dpkg-maintscript-helper.1.en.html
- This pack owns *declaring* a conffile and migrating it. Debian OS
  owns `/etc` placement, purge-vs-remove, and "must work if the admin
  deleted the file" (Policy 10.7).
- Files shipped under `/etc` are usually conffiles (debhelper marks
  them). Local edits must survive upgrade.
- Do not mix a shipped conffile with a maintainer script that
  regenerates the same path.
- Rename or drop obsolete conffiles with `dpkg-maintscript-helper`
  (`rm_conffile`, `mv_conffile`), not ad-hoc `rm` in `postinst`.
- Do not hard-link conffiles. Do not divert them.

Man page
- Policy: each program should have a man page
- Missing man page is considered a bug
https://www.debian.org/doc/debian-policy/ch-docs.html
Install: `/usr/share/man/man1/<binary>.1`

`/usr/share/doc/<package>/`
- copyright (required)
- changelog.Debian.gz
- upstream changelog *may* be `changelog.gz`; upstream release notes
  *should* be `NEWS.gz` (Policy 12.7). Installing upstream notes as
  `changelog.gz` is permitted but deprecated.
- Debian-specific user-visible changes go in `NEWS.Debian.gz` (from
  `debian/NEWS` via dh_installchangelogs), not in the upstream path.
https://www.debian.org/doc/debian-policy/ch-docs.html#changelog-files-and-release-notes
https://www.debian.org/doc/manuals/developers-reference/best-pkging-practices.en.html#supplementing-changelogs-with-news-debian-files
- examples under `examples/`

Strip binaries with **dh_strip** so automatic dbgsym packages work. Do
not `install -s` (Policy 10.1). The strip *flags* as an OS binary rule
are the Debian OS pack; this pack owns the packaging action.
https://www.debian.org/doc/debian-policy/ch-files.html#binaries
https://manpages.debian.org/unstable/debhelper/dh_strip.1.en.html

------------------------------------------------------------------------
6. BUILD CONTRACT (Policy 4.9)
------------------------------------------------------------------------

https://www.debian.org/doc/debian-policy/ch-source.html#main-building-script-debian-rules
https://www.debian.org/doc/debian-policy/ch-source.html

`debian/rules` must be an executable makefile starting
`#!/usr/bin/make -f`.

Required targets: `clean`, `binary`, `binary-arch`, `binary-indep`,
`build`, `build-arch`, `build-indep`. All required targets are
non-interactive.

**No network** on required targets for `main`. Since Policy 4.7.0 the
same ban applies to `contrib` and to `non-free` with `Autobuild: yes`.
Loopback to services the build itself started is allowed. Required
targets must not write outside the unpacked source tree except the
parent directory (binary packages) and `/tmp`, `/var/tmp`, `$TMPDIR`.

**dh is recommended, not required** (Policy 4.4.0). Language-specific
helpers or multiple-build patterns are acceptable reasons to skip it.
https://www.debian.org/doc/debian-policy/upgrading-checklist.html#version-4-4-0

**DEB_BUILD_OPTIONS** (honour these):

- `nocheck` — skip the build-time test suite
- `nodoc` — skip generated docs; still ship copyright and changelog
- `parallel=n` — up to n jobs if the build system allows
- `terse` — less verbose than the Policy default (builds should
  otherwise be verbose)

https://www.debian.org/doc/debian-policy/ch-source.html#debian-rules-and-deb-build-options

**DEB_BUILD_PROFILES** — `nocheck` / `noinsttest` are the standard
names; others live in the BuildProfileSpec wiki.
https://www.debian.org/doc/debian-policy/ch-source.html#debian-rules-and-deb-build-profiles
https://wiki.debian.org/BuildProfileSpec

Hard links are permitted in source packages (Policy 4.8 as of 4.7.0).
Device nodes, sockets, and setuid/setgid files still are not.
https://www.debian.org/doc/debian-policy/ch-source.html#restrictions-on-objects-in-source-packages

**Reproducible builds (Policy 4.15).** This pack treats bit-for-bit
reproducibility as a hard goal for a new application. The
testing-migration gate is Debian OS.
https://www.debian.org/doc/debian-policy/ch-source.html#reproducibility
https://wiki.debian.org/ReproducibleBuilds/Howto

------------------------------------------------------------------------
7. DESKTOP, MIME, AND APPSTREAM AS PACKAGING ARTIFACTS
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
8. QUALITY CHECKS BEFORE UPLOAD
------------------------------------------------------------------------

lintian (static policy checker)
Tags: https://lintian.debian.org/
Git: https://salsa.debian.org/lintian/lintian
Typical:

  lintian -i -I --pedantic *.changes

NEW reviewers expect no serious lintian errors. Warnings should be
understood and either fixed or justified.

Build in a clean chroot, not only the laptop.

sbuild
https://wiki.debian.org/sbuild
https://www.debian.org/doc/manuals/developers-reference/tools.en.html#sbuild

Also run (Developer's Reference tools appendix):

- piuparts — install / upgrade / remove / purge
  https://piuparts.debian.org/
- adequate — installed-state Policy holes
  https://manpages.debian.org/unstable/adequate/adequate.1.en.html
- duck — Homepage / Vcs / debian/copyright URLs
  https://manpages.debian.org/unstable/duck/duck.1.en.html
- blhc — missing hardening flags in the build log
  https://manpages.debian.org/unstable/blhc/blhc.1.en.html
- diffoscope — why two `.deb`s differ (reproducibility)
  https://diffoscope.org/

https://www.debian.org/doc/manuals/developers-reference/tools.en.html

Salsa CI (pipeline template used by packaging repos on salsa)
https://salsa.debian.org/salsa-ci-team/pipeline
https://wiki.debian.org/salsaci

Other checks:

- `desktop-file-validate` on every .desktop
- `appstreamcli validate` on metainfo
- No embedded copies of other projects
- No files outside the package tree during build except `/tmp`
- Reproducible build (OS pack explains the testing-migration gate;
  new applications should still treat it as a hard goal)

autopkgtest / DEP-8 when you have tests worth running on the installed
package: `debian/tests/control`. Results land on ci.debian.net after
the package is in the archive.

------------------------------------------------------------------------
9. SUBMISSION PROCESS
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

Step E — Sponsor uploads to incoming. First source **and** binaries go
to NEW (Developer's Reference 5.6.1). After that, uploads to unstable
are **source-only**; the buildds produce the binaries.

https://www.debian.org/doc/manuals/developers-reference/pkgs.en.html#source-and-binary-uploads

**tag2upload / git-debpush.** A signed DEP-14 tag with
`[dgit ... please-upload ...]` is enough; the tag2upload service builds
the source package and uploads. The resulting `.dsc`/`.changes` carry
`Git-Tag-Tagger` and `Git-Tag-Info`. Still a real upload: NEW, DFSG,
and lintian apply the same.
https://wiki.debian.org/tag2upload
https://manpages.debian.org/unstable/git-debpush/tag2upload.5.en.html

NEW / DFSG review
https://dfsg-new-queue.debian.org/
https://dfsg-new-queue.debian.org/dashboard
https://wiki.debian.org/NewQueue
https://wiki.debian.org/Teams/DFSG
Live NEW queue (the old NEW-checklist.html 404s, as does REJECT-FAQ):
https://ftp-master.debian.org/new.html
NewQueue wiki:
https://wiki.debian.org/NewQueue
Rejection mails:
https://ftp-master.debian.org/reject.html
Salsa copy of the ftp-team website (historical REJECT-FAQ):
https://salsa.debian.org/ftp-team/website
Queue times: https://people.debian.org/~roehling/new_queue/

NEW checking priorities (checklist order):

1. Keep the archive legal (DFSG + distributable)
2. Keep the package namespace sane
3. Reduce obvious bugs

Read the checklist before upload. Worth-including, naming, duplicate
function, and descriptions are first-class:

- Is it maintained upstream, or a security/quality problem?
- Can another source package already provide the same function?
- Unique, sensible names; no PATH clashes
- Description that tells a user what they get
- Valid reason for each new binary

After accept: unstable (sid) → testing → stable.
You remain the listed Maintainer. Sponsors upload. You fix bugs.

Getting into Debian does not make the app a GNOME Circle or Core app.
Getting into Circle does not put the app in apt.
[README.md](README.md) composition table.

------------------------------------------------------------------------
10. WHAT REVIEWERS TYPICALLY LOOK FOR
------------------------------------------------------------------------

From Policy, the NEW checklist, and DFSG team materials:

Must-haves

- DFSG-free source for everything shipped (or honest non-free area)
- Accurate debian/copyright (Files-Excluded + `+dfsg` when stripped)
- Unique, sensible package name
- Builds in a clean environment with no network on required targets
- Follows FHS / usr-merge (OS pack)
- Valid control fields and current Standards-Version (`4.7.4`)
- No filename clashes on PATH
- Useful Description
- Homepage and Vcs fields
- ITP referenced in changelog

Strong expectations

- lintian-clean of errors
- Man page
- Desktop file + AppStream metainfo for a GUI
- Reproducible build
- watch file (and upstream OpenPGP key when upstream signs)
- No vendored libraries Debian already has
- Reasonable Depends (not bloated, not missing)
- DEP-8 tests when the package has a meaningful as-installed suite
- dh_strip / dbgsym, not `install -s`

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
11. RELATIONSHIPS AND DEPENDENCIES
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
- Built-Using / Static-Built-Using: section 3

GUI toolkit apps Depends on the **shared libraries** Debian ships, not
on a bundled GTK. Versioned Depends match the SONAME / .so version you
built against.

Do not Depends on another desktop's entire meta-package "to be safe."

Vendoring: if archive policy for that language (Rust crates, minified
JS) makes a proper library package impractical, document it in
copyright and the package README. NEW still wants source for minified
files. That is this pack plus DFSG (OS pack), not a GNOME rule.

------------------------------------------------------------------------
12. AFTER ACCEPTANCE
------------------------------------------------------------------------

You stay responsible.

- Bugs: https://bugs.debian.org/<package>
- Upload new upstream versions (source-only to unstable)
- Fix RC bugs before the freeze
- Keep Standards-Version current
- If you disappear, the package can be orphaned (O) or removed

Debian Maintainer later
https://wiki.debian.org/DebianMaintainer
https://www.debian.org/devel/join/newmaint
https://nm.debian.org/

Application-level HIG regressions are not RC unless they make the
package unusable. RC is "the OS cannot release with this bug."

**NMU / DELAYED/.** A non-maintainer upload fixes a bug the maintainer
has not. Version the Debian revision with `.1` (or `+nmu1` for native).
Upload to `DELAYED/X-day` (X is 0–15) so the maintainer can still
react; they can cancel with dcut. Do not NMU into NEW.
https://www.debian.org/doc/manuals/developers-reference/pkgs.en.html#non-maintainer-uploads-nmus
https://www.debian.org/doc/manuals/developers-reference/pkgs.en.html#using-the-delayed-queue

**experimental.** A separate suite for unfinished or disruptive work.
It never auto-migrates to testing. Useful for a new binary that will
hit NEW, or an ABI bump, without blocking unstable.
https://www.debian.org/doc/manuals/developers-reference/resources.en.html#experimental
https://wiki.debian.org/DebianExperimental

**stable-proposed-updates.** Fixes for the released stable OS. Minimal
diff, already in unstable, severity important or higher, version
`+debNuX` / `~debNuX`. File a `release.debian.org` bug with a source
debdiff and wait for the stable release managers; do not treat this as
a NEW-style review.
https://www.debian.org/doc/manuals/developers-reference/pkgs.en.html#special-case-uploads-to-the-stable-and-oldstable-distributions

**backports.** Rebuild a testing/unstable package for stable
(`~bpoNuX`). The package must exist in testing first except for narrow
documented exceptions. Separate archive and NEW-like queue.
https://www.debian.org/doc/manuals/developers-reference/pkgs.en.html#the-stable-backports-archive
https://backports.debian.org/

------------------------------------------------------------------------
13. AI CONTRIBUTIONS (LIVE WATCH, 2026-08-25)
------------------------------------------------------------------------

Debian currently has **no standing AI contribution policy** for
packaging. Flathub's store ban on AI-assisted apps is GNOME OS payload
law. Do **not** copy it onto `.deb` / NEW / mentors workflows until
Debian says so.

A General Resolution on LLM / generative-AI contributions is open
**15–28 August 2026**:
https://www.debian.org/vote/2026/vote_002
https://lists.debian.org/debian-devel-announce/

Watch debian-devel-announce for the result.

- If the winning option amends packaging, NEW, or contributor rules,
  **this pack** owns the follow-up.
- If it amends the Social Contract, **Debian OS** owns that text and
  this pack cites it.

Until then: copyright, DFSG, and "you are accountable for what you
upload" still apply to every file in the source package, regardless of
the editor used.

------------------------------------------------------------------------
14. QUICK OFFICIAL LINK LIST
------------------------------------------------------------------------

Policy 4.7.4.1
https://www.debian.org/doc/debian-policy/

Upgrading checklist
https://www.debian.org/doc/debian-policy/upgrading-checklist.html

Copyright format
https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/

Developer's Reference 14.14
https://www.debian.org/doc/manuals/developers-reference/

Guide for Debian Maintainers
https://www.debian.org/doc/manuals/debmake-doc/

New Maintainers' Guide
https://www.debian.org/doc/manuals/maint-guide/index.en.html

WNPP / ITP
https://www.debian.org/devel/wnpp/

Mentors
https://mentors.debian.net/

NEW queue (NEW-checklist.html 404s)
https://ftp-master.debian.org/new.html
https://wiki.debian.org/NewQueue

Rejection mails
https://ftp-master.debian.org/reject.html

DFSG / NEW dashboard
https://dfsg-new-queue.debian.org/

ftp-team website (salsa; historical REJECT-FAQ lives here)
https://salsa.debian.org/ftp-team/website

tag2upload
https://wiki.debian.org/tag2upload
https://manpages.debian.org/unstable/git-debpush/tag2upload.5.en.html

DEP-8 / ci.debian.net
https://dep-team.pages.debian.net/deps/dep8/
https://ci.debian.net/

DEP-12 / DEP-14 / DEP-3
https://dep-team.pages.debian.net/deps/dep12/
https://dep-team.pages.debian.net/deps/dep14/
https://dep-team.pages.debian.net/deps/dep3/

lintian
https://lintian.debian.org/

sbuild / salsa CI / tools
https://wiki.debian.org/sbuild
https://salsa.debian.org/salsa-ci-team/pipeline
https://www.debian.org/doc/manuals/developers-reference/tools.en.html

AI GR (open 15–28 Aug 2026)
https://www.debian.org/vote/2026/vote_002

debian-devel-announce
https://lists.debian.org/debian-devel-announce/

AppStream (Debian)
https://wiki.debian.org/AppStream/Guidelines

Packages search
https://packages.debian.org/

Sister packs
./debian-os-policy.md
./gnome-application-policy.md
./gnome-os-policy.md
./README.md

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.0.0 | Initial four-pack split: Debian Application as package rules (control, copyright, lintian, ITP, NEW) |
| 1.1.0 | Build contract (Policy 4.9); Policy 4.7.3 fields (Priority default, Git-Tag-*); tag2upload; DEP-8/12/14; DFSG team / live NEW queue (NEW-checklist.html 404); conffile packaging vs OS 10.7; AI-GR watch; dead URL fixes |
