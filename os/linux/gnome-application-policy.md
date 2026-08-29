---
title: "GNOME Application Policy"
description: Curated map of GNOME HIG, GTK 4 + Libadwaita, application identity, accessibility, and Circle app quality. Not Flatpak/Flathub and not Debian packaging.
version: "1.1.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - README.md
  - gnome-os-policy.md
  - debian-os-policy.md
  - debian-application-policy.md
last_updated: "2026-08-25"
---

# GNOME Application Policy

Reference pack for **what the program is** when it is a GNOME-platform
application: Human Interface Guidelines, GTK 4, Libadwaita, application
ID, identity files' *contents*, accessibility, license and trademark.

**Role:** curated map (working memory). **Not** L4 for any one product.
**Not** Flatpak, Flathub, or GNOME runtime EOL — that is
[gnome-os-policy.md](gnome-os-policy.md).
**Not** debian/control, man pages as Policy, or NEW — that is
[debian-application-policy.md](debian-application-policy.md).

Last verified against official GNOME and Freedesktop documents as of
2026-08-25.

History

- 1.0.0: initial map
- 1.1.0: AppCriteria content rows (CoC, crypto focus, user reviews);
  remaining HIG guideline pages; Exec/URI/D-Bus notification rule;
  GNOME 50/51 pin for toolkit context only

The HIG applies to the running UI whether the binary is uninstalled, in
a `.deb`, or in a Flatpak. Circle *app quality* is this pack. Circle
*must be on Flathub* is GNOME OS.

------------------------------------------------------------------------
0. LAYERING
------------------------------------------------------------------------

This pack owns:

- HIG and Adwaita widget patterns
- Application ID, D-Bus name, GSettings schema id (the string)
- Contents of .desktop, metainfo, icons, gschema, MIME, .doap
- GtkApplication behavior; portals as **GTK APIs**
- Accessibility of the UI
- Trademark: third-party apps must not call themselves "GNOME"
- OSI license / no CLA as Circle-shaped app quality
- Circle / Releng review of the **running app**

This pack does **not** own:

- `/usr` vs `/app`, apt, Flatpak manifest, finish-args, runtime EOL
- debian/changelog, Standards-Version, lintian, ITP
- Whether the first store is apt or Flathub

Identity files are named here. The payload OS maps `share/` onto a
prefix (`/usr/share` on Debian; `/app/share` on Flatpak).

------------------------------------------------------------------------
1. FOUNDATIONAL DOCUMENTS
------------------------------------------------------------------------

GNOME Human Interface Guidelines (THE design standard)
https://developer.gnome.org/hig/
Source: https://gitlab.gnome.org/Teams/Websites/developer.gnome.org-hig

Written for GTK 4 + Libadwaita. Sections:

- Design principles
  https://developer.gnome.org/hig/principles.html
- Guidelines (naming, app icons, pointer, keyboard, UI icons, styling,
  writing, typography, navigation, adaptive, a11y)
  https://developer.gnome.org/hig/guidelines.html
- Patterns (windows, navigation, controls, feedback)
  https://developer.gnome.org/hig/patterns.html
- Reference (shortcuts, palette)
  https://developer.gnome.org/hig/reference.html

HIG in short (4 principles):

1. Design for people (ability, culture, form factor)
2. Make it simple (one job; progressive disclosure)
3. Reduce user effort (automate; fewer steps; less to remember)
4. Be considerate (prevent mistakes; undo instead of confirm; no
   needless interruption)

GNOME Foundation Software Policy (who may use the name)
https://wiki.gnome.org/Foundation/SoftwarePolicy
Licensing guidelines: https://foundation.gnome.org/licensing-guidelines
Implementation: https://gitlab.gnome.org/Teams/Releng/AppOrganization

Two kinds of software (board, 2023-08-10) — **identity**, not a `.deb`
vs Flatpak choice:

1. Official GNOME software (Core). May use GNOME trademarks and
   `org.gnome.*`. Hosted under gitlab.gnome.org/GNOME and listed in
   gnome-build-meta.
2. GNOME Circle. OSI-licensed, uses or extends the GNOME platform,
   **not** official. Cannot use GNOME trademarks to identify itself.

A third-party app must not be named "GNOME Foo", must not set
developer/author to "GNOME", and must not use `org.gnome.*`.
`Categories=GNOME;` in a .desktop file is a Freedesktop additional
category (menu classification), not product branding.

Official GNOME App Definition
https://gitlab.gnome.org/Teams/Releng/AppOrganization/-/blob/main/OfficialAppDefinition.md

Core apps: essential desktop functionality, coherent suite, generic
name, avoid overlapping other Core apps. Circle-shaped apps may overlap
a Core job if they are a different product (specialized editor vs
generic Text Editor). Do not claim Core's generic slot.

App Criteria — **application** rows
https://gitlab.gnome.org/Teams/Releng/AppOrganization/-/blob/main/AppCriteria.md

Use: General App Criteria (quality, GTK 4 + Libadwaita, HIG, a11y,
metadata content, OSI, repository hygiene) and the application halves
of Circle/Core (no GNOME branding, valid ID shape, explainable code,
i18n).

Content rows (General App Criteria — this pack; archive 1.0.0 missed
them):

- Must not contradict the intentions of the GNOME Code of Conduct
  https://conduct.gnome.org
- Must not promote cryptocurrencies or related services as the app's
  **focus**. Supporting crypto as a non-priority feature is OK
  (AppCriteria footnote).
- User reviews generally positive; no repeated complaints about
  critical issues (Circle-shaped quality of the running app)

Do **not** take from that file while using only this pack:

- "Uses the GNOME runtime on Flathub"
- "Available on Flathub" / x86_64 + aarch64
- Runtime currency on Flathub
- gnome-build-meta / org.gnome.<codename> process

Those are [gnome-os-policy.md](gnome-os-policy.md).

GNOME Code of Conduct
https://conduct.gnome.org
https://handbook.gnome.org/foundation/committees/coc.html
conduct@gnome.org

Circle-shaped projects link the CoC from the README. The running app's
**content** must also not contradict the CoC.

GNOME Developer Documentation
https://developer.gnome.org/documentation/
Platform intro:
https://developer.gnome.org/documentation/introduction.html
Guidelines (programming, a11y, l10n, maintainer):
https://developer.gnome.org/documentation/guidelines.html

The HIG is "what the UI must feel like."
General App Criteria is "what must be true of the running app."
Developer docs are "how GNOME people actually build."
Software Policy is "who may say they are GNOME."

------------------------------------------------------------------------
2. HOW TO BUILD THE APPLICATION
------------------------------------------------------------------------

Welcome to GNOME
https://welcome.gnome.org/

Application ID
https://developer.gnome.org/documentation/tutorials/application-id.html

Using GtkApplication
https://developer.gnome.org/documentation/tutorials/application.html

Integrating with GNOME (desktop, icons, D-Bus, MIME — file *roles* and
field *contents*)
https://developer.gnome.org/documentation/guidelines/maintainer/integrating.html

Programming languages
https://developer.gnome.org/documentation/introduction/languages.html

GNOME platform libraries are C + GObject-Introspection. Applications
may be C, Vala, JavaScript (GJS), Python (PyGObject), Rust (gtk-rs),
C++ (gtkmm), C# (gir.core), Java (Java-GI). C remains the library
language. New Circle apps are majority Rust; Core is still mostly C,
then Vala, JS, Rust.

gtk-rs
https://gtk-rs.org/
GTK4 book: https://gtk-rs.org/gtk4-rs/stable/latest/book/

Programming guidelines (application, not OS)
https://developer.gnome.org/documentation/guidelines/programming.html

- Namespacing: unique prefix on every symbol and public header path;
  snake_case functions, CamelCase types, UPPER_CASE macros
  https://developer.gnome.org/documentation/guidelines/programming/namespacing.html
- Memory: one owner per allocation; document `(transfer)` GI
  annotations; do not free what you do not own
  https://developer.gnome.org/documentation/guidelines/programming/memory-management.html
- Introspection if you export a library (or a private convenience
  library): annotate public API; `g-ir-scanner --warn-all`
  https://developer.gnome.org/documentation/guidelines/programming/introspection.html

Localization (application)
https://developer.gnome.org/documentation/guidelines/localization.html
Practices:
https://developer.gnome.org/documentation/guidelines/localization/practices.html

gettext. intltool is dead — new apps use GNU gettext and Meson
`i18n.merge_file` for desktop/metainfo. Mark UI strings; do not mark
empty strings; US English source; translator comments. Damned Lies
enrollment is listing-side (GNOME OS / Circle membership).

Toolkit pin (application context — **not** store / runtime EOL)

https://release.gnome.org/calendar/

- Stable: GNOME **50** (released 2026-03-18). Libadwaita 1.9.
  https://release.gnome.org/50/developers/
- Old-stable: GNOME 49. Libadwaita 1.8 (`AdwShortcutsDialog`)
- Unstable: GNOME 51 (51.0 tarballs 2026-09-12, release 2026-09-16)

Match the toolkit you compile against (GNOME 50 ⇒ current Libadwaita
for that stack). Which GNOME runtime id a Flatpak uses, and when that
runtime is EOL, is [gnome-os-policy.md](gnome-os-policy.md).

Libadwaita
Latest: https://gnome.pages.gitlab.gnome.org/libadwaita/doc/main/
Pick the docs for the version you compile against (1.6 / 1.7 / 1.8 /
1.9 / …).

Patterns expected of a modern GNOME app: AdwApplication,
AdwApplicationWindow, AdwToolbarView, AdwHeaderBar, AdwDialog (not
legacy GtkDialog as the primary modal), AdwPreferencesDialog,
AdwAboutDialog, AdwStyleManager, breakpoints instead of Leaflet/Flap.

Deprecated in 1.6+ (do not add): AdwAboutWindow, AdwPreferencesWindow,
AdwMessageDialog, AdwLeaflet, AdwFlap, AdwSqueezer.
AdwShortcutsDialog exists since 1.8; older Libadwaita still uses
GtkShortcutsWindow. GNOME 50 / Libadwaita 1.9: AdwSidebar,
AdwViewSwitcherSidebar; autoloaded `style-dark.css` / `style-hc.css`
deprecated — use `style.css` + CSS media queries.

GTK 4
https://docs.gtk.org/gtk4/

GNOME Builder
https://apps.gnome.org/Builder/
https://builder.readthedocs.io/
Useful IDE. Not a ship-format requirement.

Meson
https://mesonbuild.com/
Usual GNOME app build. App Criteria *recommends* Meson, Automake, or
CMake. That is build hygiene, not `.deb` vs Flatpak.

Design resources
https://developer.gnome.org/hig/resources.html
App Icon Preview: https://flathub.org/apps/org.gnome.design.AppIconPreview
Contrast: https://flathub.org/apps/org.gnome.design.Contrast
Icon Library: https://flathub.org/apps/org.gnome.design.IconLibrary
Icon template: https://gitlab.gnome.org/Teams/Design/HIG-app-icons
Design Matrix: https://matrix.to/#/#design:gnome.org

------------------------------------------------------------------------
3. APPLICATION IDENTITY
------------------------------------------------------------------------

Application ID (reverse DNS)
https://developer.gnome.org/documentation/tutorials/application-id.html
g_application_id_is_valid:
https://docs.gtk.org/gio/type_func.Application.id_is_valid.html

The ID string is used as:

- GtkApplication / GApplication id (single-instance, open files)
- D-Bus well-known name
- .desktop basename
- GSettings schema id
- AppStream component id
- Icon name
- Notification / search-provider identity

The same string may later become a Flatpak id. That does not make
Flatpak an application requirement. Store-specific verification
(Flathub deriving a GitHub URL) is GNOME OS.

Rules that bite here:

- Two or more dot-separated elements, < 255 characters
- No leading digit in an element; no empty elements
- Prefer no hyphens (D-Bus). Replace `-` with `_` in the domain part
- Do not end in `.desktop`, `.app`, or `.linux`
- `org.gnome.*` is reserved unless Releng listed you as official
- GitHub-shaped ids: `io.github.<user>.<app>` (four components) if you
  want them valid for a later store pack. `com.github.*` is reserved
- Changing the ID later breaks GSettings, desktop files, and any store.
  Do it before the first OS submission
- Devel builds may suffix `.Devel`

XDG storage APIs
https://specifications.freedesktop.org/basedir-spec/latest/
Use GLib: `g_get_user_config_dir`, `g_get_user_data_dir`, …
Do not hardcode `~/.config/<shortname>`. A payload OS may remap
directories.

Identity files (roles). Payload OS chooses the prefix.

  share/applications/<id>.desktop
  share/metainfo/<id>.metainfo.xml
  share/glib-2.0/schemas/<id>.gschema.xml
  share/icons/hicolor/scalable/apps/<id>.svg
  share/icons/hicolor/symbolic/apps/<id>-symbolic.svg
  share/mime/packages/<id>.xml
  share/dbus-1/services/<id>.service     (if D-Bus activatable)
  share/gnome-shell/search-providers/…  (if search provider; see §4)
  share/<app-private>/…

Freedesktop specs:

- Desktop Entry
  https://specifications.freedesktop.org/desktop-entry-spec/latest/
- Icon Theme
  https://specifications.freedesktop.org/icon-theme-spec/latest/
- Shared MIME-info
  https://specifications.freedesktop.org/shared-mime-info-spec/latest/
- AppStream
  https://www.freedesktop.org/software/appstream/docs/

Two apps must not share an application ID.

Do not ship a mimeapps.list that steals another app's default handler
unless hijacking defaults is the product.

------------------------------------------------------------------------
4. INTEGRATION APIS
------------------------------------------------------------------------

GtkApplication / AdwApplication
https://developer.gnome.org/documentation/tutorials/application.html

Single-instance, `startup` / `activate` / `open` / `shutdown`,
GActionMap. Command-line files arrive as GFiles. Second instances
forward to the primary.

D-Bus activation (preferred)
https://developer.gnome.org/documentation/guidelines/maintainer/integrating.html#d-bus-activation

- Desktop key `DBusActivatable=true`
- Session service file, Name = application ID
- Exec uses `--gapplication-service`
- With DBusActivatable, GNOME launches via D-Bus (desktop `Exec` is
  ignored for that launch). Still ship a correct `Exec=` for
  implementations that do not understand D-Bus activation.

Persistent notifications require D-Bus activation (official integrating
doc, "Advanced integration"). GNotification + DBusActivatable.

https://developer.gnome.org/documentation/tutorials/notifications.html
https://docs.gtk.org/gio/class.Notification.html
HIG: https://developer.gnome.org/hig/patterns/feedback/notifications.html

- Valid desktop file named as the application ID
- `g_application_send_notification`; actions are `app.` actions only
- `X-GNOME-UsesNotifications=true` so the app appears in Notifications
  settings
- Users can disable notifications; do not rely on them exclusively

GSettings
https://docs.gtk.org/gio/class.Settings.html
Schema id and path follow the application ID.

Portals as **GTK APIs** (application obligation)
https://flatpak.github.io/xdg-desktop-portal/docs/

Use the toolkit, not host path rips:

- GtkFileDialog / GtkFileLauncher — open and save
- GtkUriLauncher — http(s), mailto
- Print via GTK / WebKit print APIs
- Libadwaita StyleManager follows the settings portal (accent, dark)

This remains true on Debian GNOME: xdg-desktop-portal-gnome is the
session implementation (GNOME OS session half). Sandbox finish-args are
GNOME OS payload.

MIME types you open go in the desktop `MimeType=` key and, if you own a
type, in a shared-mime package named after the ID.

URI schemes (official integrating doc)
https://developer.gnome.org/documentation/guidelines/maintainer/integrating.html#uri-schemes-handling

- Add `x-scheme-handler/<scheme>` to `MimeType=` (mailto, http, https,
  ftp, gemini, or a custom scheme)
- `Exec` uses `%u` (one URI) or `%U` (several). If the app handles both
  files and URIs, use only `%u`/`%U` — do not also put `%f`/`%F`
- Files-only: `%f` one file, `%F` several
  https://specifications.freedesktop.org/desktop-entry-spec/latest/

Search-provider identity (if you offer overview search)
https://developer.gnome.org/documentation/tutorials/search-provider.html

- Implement `org.gnome.Shell.SearchProvider2` (interface XML)
- Install a registration `.ini` under
  `share/gnome-shell/search-providers/` with `DesktopId`, `BusName`,
  `ObjectPath`, `Version=2`
- Start in service mode: `startup()` must not open windows

The XML / registration file is **application identity** (this pack).
GNOME Shell consuming it is GNOME OS **session**.

------------------------------------------------------------------------
5. LICENSE AND TRADEMARK
------------------------------------------------------------------------

OSI-approved license (Circle-shaped)
https://opensource.org/licenses
No contributor license agreement.
Must work without requiring proprietary software.

Debian `main` also wants DFSG (Debian OS pack). GPL-2/3, LGPL, MIT,
BSD, Apache-2.0 generally satisfy both. debian/copyright is still
Debian Application.

AppStream SPDX
https://www.freedesktop.org/software/appstream/docs/chap-Metadata.html#tag-project_license
`project_license` is the **code** license, not documentation. Mixing
CC-BY-SA into project_license makes GNOME Software show the app as
proprietary. `metadata_license` covers the metainfo file (often CC0-1.0).

GNOME trademark: no "GNOME" in the app name or author; no official
GNOME artwork as identity. Software Policy (section 1).

Circle AI policy (new *app* submissions, 2026) — about **the code**,
not the store:

  While it is not prohibited to use AI as a learning aid or a development
  tool (i.e. code completions), app developers should be able to justify
  and explain the code they submit, within reason. Submissions with large
  amounts of unnecessary code, inconsistent code style, imaginary API
  usage, comments serving as LLM prompts, or other indications of
  AI-generated output will be rejected.

https://blogs.gnome.org/sophieh/2026/05/29/updates-from-the-circle-committee/
https://gitlab.gnome.org/Teams/Releng/AppOrganization/-/blob/main/AppCriteria.md

Flathub's stricter "no AI-assisted apps" rule is GNOME OS / store.
Debian NEW has no standing AI policy. A Debian GR on LLM usage is open
15–28 Aug 2026 (https://www.debian.org/vote/2026/vote_002) — that is
Debian Application; do not copy either way.

------------------------------------------------------------------------
6. REQUIRED APPLICATION FILES (CONTENTS)
------------------------------------------------------------------------

.data desktop file

- Filename = application ID
- Name: header capitalization
  https://developer.gnome.org/hig/guidelines/app-naming.html
  One or two simple nouns; short (< 15 characters ideal); related to
  the domain; easy to pronounce; pairable with an icon metaphor
  Avoid: trademarks of others, G-prefix, puns, inside jokes,
  SuperWriter-style mashups, made-up words
- Comment: short user-facing blurb, not the toolkit
- GenericName: optional generic type ("Text Editor"); localize it
- Keywords=: semicolon-separated search terms; trailing semicolon;
  localize
- Icon = application ID
- Categories: a registered main category plus GTK. `GNOME;` is
  additional category, not branding
- StartupNotify=true
- Exec: the binary plus **one** of `%f` / `%F` / `%u` / `%U` if you
  open files or URIs (see §4). Keep Exec even when DBusActivatable
- MimeType if you open files and/or URI schemes
  (`x-scheme-handler/<scheme>`)
- DBusActivatable=true when the service file exists
- X-GNOME-UsesNotifications=true if you send notifications
- Localize Name, Comment, GenericName, and Keywords
- Validate: `desktop-file-validate`

HIG primary menu (UI, not a desktop key)
https://developer.gnome.org/hig/patterns/controls/menus.html
Tail group: Preferences, Keyboard Shortcuts, Help (if any), About
<App>. Button icon `open-menu-symbolic`. Tooltip "Main Menu".
No Close/Quit items. Ctrl+Q may still quit.

Help (if you ship user documentation): the Help item opens it in the
Help app (Yelp). Mallard is the usual GNOME format; DocBook or HTML is
an acceptable equivalent. yelp-tools builds it. This is not a man page
(Debian Application).
https://gitlab.gnome.org/GNOME/yelp-tools
https://apps.gnome.org/Yelp/

metainfo.xml

- component type desktop-application
- id, name, summary, description, launchable, icon, provides,
  categories, developer id, licenses
- Validate: `appstreamcli validate --explain`
https://www.freedesktop.org/software/appstream/docs/sect-Metadata-Application.html
GNOME Software field meanings:
https://gnome.pages.gitlab.gnome.org/gnome-software/help/C/software-metadata.html
Apps-for-GNOME extras:
https://gitlab.gnome.org/World/apps-for-gnome/-/blob/main/METADATA.md
Screenshots:
https://gitlab.gnome.org/GNOME/Initiatives/-/wikis/Update-App-Screenshots
Summary:
https://gitlab.gnome.org/GNOME/Initiatives/-/wikis/App-Metadata#summary
OARS: https://hughsie.github.io/oars/

Application-quality metainfo:

- Valid XML
- HIG name and icon
- Screenshots of the actual window, default theme
- Summary a person can read (not "GTK4 Rust crate")
- Hardware `<requires>` / `<recommends>` / `<supports>`
- OARS 1.1. Empty = all ages; missing = unknown
- Developer id (reverse DNS)

Flathub featured extras (10–25 char summary, brand colors, screenshot
shadow rules) are GNOME OS store quality, not this pack's must-haves.
Debian archive AppStream guidelines are Debian Application. Do not
import Flathub's English-localisation *store* rule; gettext-ready UI
is already required here.

Icons
https://developer.gnome.org/hig/guidelines/app-icons.html

- Unique metaphor. Reusing another app's identity is strongly
  discouraged
- 128×128 drawing area, GNOME perspective (top + front), no outer shadow
- Full-color SVG + symbolic SVG
- Nightly variant if you ship a nightly
- App Icon Preview exports both

.doap at the repository root
Filename = VCS project name + `.doap`
https://gitlab.gnome.org/World/apps-for-gnome/-/blob/main/METADATA.md#doap
List GTK 4 + Libadwaita as `<platform>`, plus a maintainer account.
Builder and Apps for GNOME read this.

Standard shortcuts
https://developer.gnome.org/hig/reference/keyboard.html
https://developer.gnome.org/hig/guidelines/keyboard.html

Among HIG defaults: Ctrl+N/O/S, Shift+Ctrl+S, Ctrl+P, Ctrl+F, Ctrl+W,
Ctrl+Q, Ctrl++, Ctrl+-, Ctrl+0, Ctrl+,, Ctrl+?, F1, F9 (utility pane),
F10 (menu), F11 if you implement fullscreen. Access keys on labelled
controls. No Super; no Alt for accelerators (conflicts with mnemonics).

Writing style
https://developer.gnome.org/hig/guidelines/writing-style.html
Short, header capitalization on chrome, sentence capitalization on
running text, no "you"/"my", no toolkit jargon in the UI.

Adaptive
https://developer.gnome.org/hig/guidelines/adaptive.html
If you claim mobile / small display, use Libadwaita breakpoints and
declare form factor in metainfo (GNOME OS / Software also read that).

Pointer & Touch (this bites)
https://developer.gnome.org/hig/guidelines/pointer-touch.html
Large click targets. Do not rely on hover, double-click, or chording.
Do not say "move the mouse" in the UI. Secondary click is a context
menu, not delete. Esc cancels in-progress pointer ops. Three- and
four-finger gestures and top/bottom edge drags are reserved for the
system. Every pointer action also has a keyboard path.

UI Icons (chrome — not the app icon)
https://developer.gnome.org/hig/guidelines/ui-icons.html
Symbolic 16×16 style; GTK / Icon Library first. Label XOR icon on a
control (sidebars and view switchers excepted). Only use icons users
will recognize (search, menu, back/forward, share, and domain-specific
sets).

UI Styling
https://developer.gnome.org/hig/guidelines/ui-styling.html
Adwaita light and dark. Follow the system style unless a per-app
preference is justified (text editors, long sessions): then Light /
Dark / Follow system (`AdwStyleManager`). Test high contrast. Do not
break Adwaita with custom CSS; use style classes and CSS variables.
Color is never the only signal. No flashing.

Typography (distinct from writing style)
https://developer.gnome.org/hig/guidelines/typography.html
System / Adwaita Sans. GTK standard font styles (`body`, `heading`,
`caption`, `title-1`…`title-4`, `large-title`). No hard-coded sizes
(breaks large-text a11y). No all-caps. Unicode punctuation (… “ ” × –).

------------------------------------------------------------------------
7. QUALITY CHECKS (THE RUNNING APPLICATION)
------------------------------------------------------------------------

Validate identity files:

  desktop-file-validate <id>.desktop
  appstreamcli validate --explain <id>.metainfo.xml

GSettings (uninstalled: GSETTINGS_SCHEMA_DIR):

  glib-compile-schemas
  gsettings list-keys <id>

Accessibility
https://developer.gnome.org/hig/guidelines/accessibility.html
https://developer.gnome.org/documentation/guidelines/accessibility.html
https://docs.gtk.org/gtk4/section-accessibility.html

- Every control reachable from the keyboard
- Standard shortcuts where the action exists
- High-contrast style
- Large text
- Contrast of content vs background
- Orca (Alt+Super+S): tooltips on image buttons; accessible names
- On-screen keyboard reaches every text entry

Design / HIG (reviewer judgment)

- Dark mode; no dark-on-dark; no unexpected white surfaces
- Header bar, primary menu, preferences dialog, about dialog, toasts
  rather than modal chatter
- First run is obvious (empty state, recents; not a setup wizard)
- No data-loss bugs; undo destructive actions where possible

Content (AppCriteria)

- UI, copy, and shipped assets do not contradict the Code of Conduct
- Cryptocurrency is not the product's focus
- Where a public listing exists: reviews generally positive; no
  repeated critical complaints

Repository hygiene (the project, not the distro)

- Recent development
- Default branch `main` (Circle-shaped new apps)
- Passing CI
- Public issue tracker and source (hosting site is not prescribed)
- CoC linked from the README

Localization
https://developer.gnome.org/documentation/guidelines/localization.html
gettext-ready UI. Damned Lies enrollment is listing-side (GNOME OS /
Circle membership). First Circle inclusion may precede full l10n
infrastructure; later reviews expect it. Flathub's English-only store
gate is GNOME OS, not this pack.

------------------------------------------------------------------------
8. GNOME-PROJECT LISTING (APPLICATION BAR)
------------------------------------------------------------------------

Being a native GNOME application needs no form. Users are the reviewers.

GNOME-project *listing* (Circle, Core) is recognition. Application bar:
this pack. Store / runtime bar: GNOME OS pack.

Circle (application side)
https://circle.gnome.org/
https://gitlab.gnome.org/Teams/Circle
Membership guide (care for HIG, a11y, metadata):
https://gitlab.gnome.org/Teams/Circle/-/blob/main/membership_guide.md
Review procedure (they test a development build of the **app**):
https://gitlab.gnome.org/Teams/Circle/-/blob/main/review_procedure.md
Matrix: https://matrix.to/#/#circle:gnome.org

As of 2026-05-29 new Circle issues are closed until the backlog shrinks.
When they review, they weigh: works, first run, follows the HIG
(reviewer discretion). Those checks belong here even if you never file.

Core / Incubator (application side)
https://gitlab.gnome.org/Teams/Releng/AppOrganization/-/blob/main/OfficialAppDefinition.md
Not the usual path. Do not apply to Core to "become more GNOME."

apps.gnome.org / welcome.gnome.org pages are Circle benefits (GNOME OS
membership), not something a `.deb` upload grants.

------------------------------------------------------------------------
9. WHAT APPLICATION REVIEWERS LOOK FOR
------------------------------------------------------------------------

Must-haves (application)

- GTK 4 + Libadwaita
- OSI license, no CLA, no proprietary runtime *dependency of the app*
- Works; easy first run; no data-loss bugs
- HIG-shaped UI
- Dark mode, contrast, high-contrast, large text
- Full keyboard use + Orca-usable chrome
- Valid metainfo *content*, HIG name, HIG icon, screenshots, summary
- Hardware tags + OARS
- .doap present and current
- Public repo, CI, branch `main`, CoC in README
- Content does not contradict the CoC
- Not a cryptocurrency-promotion app (incidental support is OK)
- No GNOME branding in name or author
- Valid application ID (not org.gnome.* unless official)
- Explainable code (Circle AI policy)
- Where listed: generally positive reviews / no repeated critical
  complaints

Strong expectations

- D-Bus activatable GtkApplication
- GTK portal APIs for files and URIs
- Correct Exec field codes and `x-scheme-handler/<scheme>` if you
  handle files or URIs
- GNotification + D-Bus activation if you send persistent notifications
- Preferences + Shortcuts + About in the primary menu; Help if you
  ship user documentation
- Standard accelerators
- gettext-ready strings

Common application rejects / stalls

- GTK3, Electron, or "GNOME-ish" CSS on a foreign toolkit
- org.gnome.* ID or "GNOME" in the name/author
- Unbuildable development branch
- First-run dead end
- Dark mode regressions, white embedded web view in dark chrome
- Missing tooltips on icon buttons
- Invalid metainfo, no screenshots, technical summary
- Duplicate *job* with no distinct description
- AI slop (unused code, invented APIs, prompt-comments)
- Content that contradicts the GNOME Code of Conduct
- Cryptocurrency as the app's focus
- Opens files or URIs but wrong Exec field (`%f` vs `%u`) or missing
  `x-scheme-handler/<scheme>`
- Persistent notifications without D-Bus activation / GNotification

Not this pack (send to an OS pack):

- Flathub presence, GNOME runtime version, aarch64
- `--filesystem=host`, finish-args, sandbox safety tile
- lintian, FHS, debian/copyright, NEW
- Flathub generative-AI store ban
- Debian GR outcome on LLM usage

------------------------------------------------------------------------
10. PATTERNS CHEAT SHEET
------------------------------------------------------------------------

Containers
https://developer.gnome.org/hig/patterns/containers.html
AdwApplicationWindow + AdwToolbarView. Dialogs: AdwDialog /
AdwAlertDialog, adaptive. About: AdwAboutDialog (from metainfo when
possible). Preferences: AdwPreferencesDialog with pages/groups/rows.

Navigation
https://developer.gnome.org/hig/guidelines/navigation.html
View switchers, NavigationView, OverlaySplitView / NavigationSplitView
for sidebars. F9 toggles a utility pane. Libadwaita 1.9: AdwSidebar /
AdwViewSwitcherSidebar if you compile against GNOME 50.

Controls
https://developer.gnome.org/hig/patterns/controls.html
Boxed lists, switches, split buttons. Suggested / destructive button
styles sparingly. Insensitive, not error-on-click, for invalid actions.

Feedback
https://developer.gnome.org/hig/patterns/feedback.html
Toasts over modal chatter. Banners for persistent status. No
notification spam. Persistent desktop notifications: GNotification +
D-Bus activation (§4).

Do one thing well (HIG principle). A GNOME application is not an
Electron shell and not a settings dump.

------------------------------------------------------------------------
11. COMPOSING WITH OS PACKS
------------------------------------------------------------------------

GNOME-shaped `.deb` on Debian (common):

  This pack
  + [debian-application-policy.md](debian-application-policy.md)
  + [debian-os-policy.md](debian-os-policy.md)
  + [gnome-os-policy.md](gnome-os-policy.md) **session half only**

Flatpak / GNOME OS image:

  This pack
  + GNOME OS (session + payload)

Same desktop/metainfo/icons. This pack fills them. Payload OS installs
them. Debian Application still wants a man page and debian/copyright
on a `.deb` even if the HIG never mentions man pages.

Conflict rule: HIG Name vs Flathub quality "just a short name" — HIG
and product naming live here; Flathub featured-banner extras are GNOME
OS and must not silently rename the application.

------------------------------------------------------------------------
12. QUICK OFFICIAL LINK LIST
------------------------------------------------------------------------

HIG
https://developer.gnome.org/hig/
https://developer.gnome.org/hig/guidelines.html
https://developer.gnome.org/hig/guidelines/pointer-touch.html
https://developer.gnome.org/hig/guidelines/ui-icons.html
https://developer.gnome.org/hig/guidelines/ui-styling.html
https://developer.gnome.org/hig/guidelines/typography.html

Software Policy
https://wiki.gnome.org/Foundation/SoftwarePolicy

App Criteria (filter OS rows)
https://gitlab.gnome.org/Teams/Releng/AppOrganization/-/blob/main/AppCriteria.md

Code of Conduct
https://conduct.gnome.org

Developer docs
https://developer.gnome.org/documentation/
https://developer.gnome.org/documentation/guidelines/programming.html
https://developer.gnome.org/documentation/guidelines/localization.html
https://developer.gnome.org/documentation/guidelines/maintainer/integrating.html
https://developer.gnome.org/documentation/tutorials/notifications.html
https://developer.gnome.org/documentation/tutorials/search-provider.html

Release calendar (toolkit pin)
https://release.gnome.org/calendar/

Application ID
https://developer.gnome.org/documentation/tutorials/application-id.html

Libadwaita
https://gnome.pages.gitlab.gnome.org/libadwaita/doc/main/

GTK 4
https://docs.gtk.org/gtk4/

gtk-rs
https://gtk-rs.org/

AppStream (contents)
https://www.freedesktop.org/software/appstream/docs/

Desktop Entry / icons / MIME / XDG
https://specifications.freedesktop.org/desktop-entry-spec/latest/
https://specifications.freedesktop.org/icon-theme-spec/latest/
https://specifications.freedesktop.org/shared-mime-info-spec/latest/
https://specifications.freedesktop.org/basedir-spec/latest/

OARS
https://hughsie.github.io/oars/

Sister packs
./gnome-os-policy.md
./debian-os-policy.md
./debian-application-policy.md
./README.md
