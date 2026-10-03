---
title: "Direct distribution application policy"
description: Curated map of what a directly distributed Mac program is — Human Interface Guidelines, bundle contents, entitlements, privacy strings, and the notarization queue. Not Gatekeeper enforcement and not App Review.
version: "1.0.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - README.md
  - direct-os-policy.md
  - app-store-os-policy.md
  - app-store-application-policy.md
last_updated: "2026-10-02"
---

# Direct distribution application policy

Reference pack for **what a Mac program is** when you ship it
yourself: the Human Interface Guidelines, the bundle's contents, the
entitlements you declare, and the steps that submit that bundle to
Apple's notary.

**Role:** curated map (working memory). **Not** a Swift tutorial.
**Not** Gatekeeper, filesystem placement, or container formats —
those are [direct-os-policy.md](direct-os-policy.md). **Not** App
Review — that is
[app-store-application-policy.md](app-store-application-policy.md).

Last verified against the Human Interface Guidelines, bundle
resources, and notarization documents as of 2026-10-02.

A Mac App Store app reads this pack for the program. It does not
read §11–12 as its submit queue. Those sections are the Developer
ID queue.

------------------------------------------------------------------------
0. LAYERING
------------------------------------------------------------------------

This pack owns:

- Human Interface Guidelines for a Mac app
- Bundle identifier and version identity
- Icons, menus, windows, keyboard, and document UX
- `Info.plist` and the privacy manifest as authored
- Entitlement keys the program declares, including hardened-runtime
  exceptions and an optional sandbox
- Purpose strings
- Accessibility of the running program
- The notarization **queue** (Organizer, `notarytool`, staple steps,
  common failures)

This pack does **not** own:

- Where the `.app` is copied, Gatekeeper, quarantine, translocation,
  the ticket as a launch check, System Integrity Protection
  → [direct-os-policy.md](direct-os-policy.md)
- Zip, disk image, and installer construction
  → [direct-os-policy.md](direct-os-policy.md)
- App Review Guidelines, App Store Connect metadata, store privacy
  details, age rating
  → [app-store-application-policy.md](app-store-application-policy.md)
- Mandatory sandbox, store certificates, store updates
  → [app-store-os-policy.md](app-store-os-policy.md)
- Swift, SwiftUI as a language, or a package manager
  → a future `program-language` family, not this pack

------------------------------------------------------------------------
1. FOUNDATIONAL DOCUMENTS
------------------------------------------------------------------------

https://developer.apple.com/design/human-interface-guidelines/
https://developer.apple.com/design/human-interface-guidelines/designing-for-macos
https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution

Design principles Apple states across platforms: purpose, agency,
familiarity, and simplicity. A Mac app also follows the macOS
chapter. iOS layout, tab bars as the primary structure, and
phone-sized modality are not this chapter.

The notarization overview states the split this family uses:
notarization of macOS software is not App Review.

------------------------------------------------------------------------
2. APPLICATION IDENTITY
------------------------------------------------------------------------

https://developer.apple.com/documentation/bundleresources/information-property-list

- The bundle identifier is reverse-DNS (`com.example.app`). It is
  stable across updates. It is the code-signing identifier for the
  bundle. Changing it creates a different app and a different
  sandbox container.
- `CFBundleName` is the short name. `CFBundleDisplayName` is the
  name people see when it differs.
- `CFBundleShortVersionString` is the version people read.
  `CFBundleVersion` is the build number. Both are present on a
  build you notarize. The build number increases on every upload
  you submit anywhere, including a later store upload of the same
  sources.
- `CFBundlePackageType` for an app is `APPL`.
- `CFBundleExecutable` names the binary inside `Contents/MacOS`.
- `LSMinimumSystemVersion` records the oldest macOS the binary
  actually runs on. For a new arm64-only app that matches this
  family's ship host, that floor is macOS 27. A universal binary
  that still supports Intel records the Intel floor separately in
  the product's support list (Direct OS §1). The plist and the
  support list must agree.

One program, one bundle id, one payload. A direct app and a Mac
App Store app are two artifacts when they are two submissions.
They may share sources. They do not share a certificate.

------------------------------------------------------------------------
3. DESIGNING FOR THE MAC
------------------------------------------------------------------------

https://developer.apple.com/design/human-interface-guidelines/designing-for-macos

People use a Mac at a desk, on a large display, often with other
apps open, for minutes or for hours. Design for that:

- Use the display. Prefer more content at one level over deep
  stacks of modal sheets.
- Let people resize, move, hide, and show windows. Support full
  screen as a focus mode, not as the only mode.
- Put commands in the **menu bar**. A Mac app that hides its
  commands only in a custom toolbar is incomplete.
- Honor the keyboard, including keyboard-only use, and honor
  high-precision pointer work.
- Let people customize toolbars and the views they keep open.

Inputs people expect: keyboard, pointing device, and Siri. Game
controllers are an addition, not a replacement, unless the product
is a game and says so.

Do not ship an iOS layout stretched to a window and call it a Mac
app. The store pack can reject that at review. This pack rejects
it as the program, including for direct distribution, where there
is no reviewer.

------------------------------------------------------------------------
4. MENUS, WINDOWS, AND THE KEYBOARD
------------------------------------------------------------------------

https://developer.apple.com/design/human-interface-guidelines/menus

- Menu item titles are verbs for actions (`Close`, `Select`).
  An ellipsis means the command needs more input before it runs.
- Use the system icons for Share, Print, Search, and the other
  standard actions. Add a menu-item icon only when it identifies
  the command. In a group, icon all of the items or none of them.
- On the macOS 27 SDK, menu-item symbol images are hidden by
  default (the pre-macOS 26 density). Set
  `preferredImageVisibility` on an item that must keep its image.
  Review the Human Interface Guidelines before forcing images back
  on. System items such as Settings, Share, and Print still receive
  a default image.

https://developer.apple.com/documentation/macos-release-notes/macos-27-release-notes

Standard menus a document-based app is expected to have: the app
menu, File, Edit, View, Window, and Help. Format and other menus
appear when the program has those commands. Keyboard shortcuts for
the standard commands stay on the standard items.

Windows remember their frame when that is part of the work style.
Open and save panels are system panels. On macOS 27 the Recents
list in those panels is reachable with Command-Shift-F. Do not
replace the system open panel with a custom file browser for
ordinary documents.

------------------------------------------------------------------------
5. ICONS AND SYMBOLS
------------------------------------------------------------------------

https://developer.apple.com/design/human-interface-guidelines/app-icons
https://developer.apple.com/design/human-interface-guidelines/icons

App icons for macOS are layered, square, 1024×1024, authored in
Icon Composer, and masked by the system into the rounded rectangle.
Supply the appearances the Human Interface Guidelines list (default,
dark, and the clear and tinted variants). Do not pre-round the
artwork.

Interface icons are SF Symbols, simple, and used the same way
everywhere in the app. A document icon reads as a document (the
folded corner), not as a second app icon.

The icon file in the bundle is this pack. The path of the `.app`
is the OS pack.

------------------------------------------------------------------------
6. BUNDLE CONTENTS
------------------------------------------------------------------------

https://developer.apple.com/documentation/bundleresources/information-property-list

Minimum contents of an app bundle this pack expects:

- `Contents/Info.plist` with the identity keys in §2
- `Contents/MacOS/<executable>` matching `CFBundleExecutable`
- An app icon in the asset catalog or `CFBundleIconFile`
- Localized `InfoPlist.strings` or string catalogs for every
  user-visible plist string, in the same bundle
- Every purpose string the binary can trigger (§8)
- A privacy manifest when the binary or an embedded SDK is required
  to carry one (§8)

Document types, exported UTTypes, and URL schemes live in the plist
when the program handles files or links. They match the document
model in §10. They are not store metadata.

A license key, a purchase screen, or a vendor updater may exist in
a **direct** app. The Mac App Store forbids those (store application
pack). This pack does not require a license screen. It requires
that a license screen, if present, is reachable and does not block
a notarized first launch with an unsigned helper.

------------------------------------------------------------------------
7. ENTITLEMENTS YOU DECLARE
------------------------------------------------------------------------

https://developer.apple.com/documentation/bundleresources/entitlements
https://developer.apple.com/documentation/security/hardened-runtime

The entitlements file is a declaration of capabilities. The OS
enforces it. Declare the minimum set.

- Hardened runtime is on for every notarized app and command-line
  target (OS pack §6). Exception entitlements
  (`com.apple.security.cs.allow-jit`,
  `com.apple.security.cs.allow-unsigned-executable-memory`,
  `com.apple.security.cs.disable-library-validation`, and the
  others Apple lists) are added only for a feature the program
  uses.
- `com.apple.security.get-task-allow` is a development entitlement.
  It is absent from the build you notarize. Any true value fails
  the notary.
- Sandbox entitlements, including
  `com.apple.security.app-sandbox`, are present only when this
  direct app opts into the sandbox. They are not implied by
  hardened runtime.
- App Groups (`com.apple.security.application-groups`) are declared
  here when the program shares a container. The container path is
  the OS pack.
- Plug-ins do not carry their own entitlements. The host declares
  every entitlement and purpose string its plug-ins need, or the
  plug-in fails to load. A host that loads third-party bundles
  which are not signed by the same team needs the library-validation
  exception, and each quarantined plug-in still has to be notarized
  (OS pack §7).

Entitlements on the notarized build are XML and ASCII. A binary
plist or a non-ASCII file is a notary failure, not a style choice.

------------------------------------------------------------------------
8. PRIVACY STRINGS AND THE PRIVACY MANIFEST
------------------------------------------------------------------------

https://developer.apple.com/documentation/bundleresources/privacy-manifest-files
https://developer.apple.com/documentation/uikit/requesting-access-to-protected-resources

Every protected resource the process touches has its purpose string
in `Info.plist` before the first call. The string says what this
program does with the data, in the language of the person using it.
A missing or generic string is a broken program on this payload,
not only a store rejection.

Typical keys when the feature exists: camera, microphone, contacts,
location, calendars, reminders, photos, speech recognition, Apple
events, Desktop, Documents, Downloads, removable volumes, and
network volumes. Declare the keys you use. Do not declare keys for
hardware the program never opens.

The privacy manifest (`PrivacyInfo.xcprivacy`) lists required-reason
APIs, tracking domains, and collected data for the app and for
embedded SDKs that ship one. Carry the manifest the current SDK
requires. Do not invent reasons.

App Store privacy details (the nutrition label in App Store Connect)
are the store application pack. A direct-only app still ships
purpose strings and the manifest. It does not fill in App Store
Connect.

Full Disk Access is not requested from this pack. See Direct OS §10.

------------------------------------------------------------------------
9. ACCESSIBILITY
------------------------------------------------------------------------

https://developer.apple.com/design/human-interface-guidelines/

- Standard controls, which already expose accessibility, are the
  default. Custom views provide labels, values, and actions.
- The menu bar and keyboard shortcuts in §4 are the accessibility
  path for commands, not an extra.
- Type respects the system text size where the control supports it.
  Do not ship an image of text for a control label.
- VoiceOver can reach every primary action.

The App Store accessibility nutrition label is store metadata. The
behavior it describes is this pack, for both payloads.

------------------------------------------------------------------------
10. DOCUMENTS AND FILE PANELS
------------------------------------------------------------------------

https://developer.apple.com/documentation/security/accessing-files-from-the-macos-app-sandbox

- Ordinary documents open and save through the system panels.
- A sandboxed app that must reopen a user-selected file stores a
  security-scoped bookmark and resolves it on the next launch.
  Creating the bookmark is this pack. Honoring it is the OS.
- Related files (a sidecar next to a document) use the related-items
  API rather than a path built by string concatenation. Translocation
  (OS pack §7) makes hand-built relative paths fail on first launch
  from a zip or disk image.
- An unsandboxed direct app may read paths the user can read. It
  still uses the open panel for documents. Walking the whole disk
  is Full Disk Access, which this family does not treat as normal.

------------------------------------------------------------------------
11. THE NOTARIZATION QUEUE
------------------------------------------------------------------------

https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution
https://developer.apple.com/documentation/security/customizing-the-notarization-workflow

This is the submit queue for the direct payload. It is not a review
of the user interface.

Xcode, for a macOS app archive:

1. Archive the app.
2. Organizer → Distribute App → **Developer ID** → **Upload**.
3. Wait for the scan (often under an hour).
4. Export again after Xcode staples the ticket.

The Account Holder's Developer ID is the signing identity that
workflow uses. If Organizer will not upload, confirm the archive is
a macOS archive. Other targets (command-line tools, non-app
bundles, packages, disk images) use `notarytool`.

Custom and scripted flow:

1. Sign inside out with the certificates in Direct OS §2 and §5.
2. Build the outer container (Direct OS §12).
3. `xcrun notarytool submit` the outer file. Authenticate with an
   App Store Connect API key or an app-specific password kept
   outside the source tree. The notary REST API is the same queue
   when the build machine is not a Mac.
4. Read the log. Fix. Resubmit. Do not staple a rejected upload.
5. `xcrun stapler staple` the file you will give users, or follow
   the staple flow for an app inside a zip.

Notarize preexisting releases you still offer for download, not
only the next version. Apple relaxes some rules for old unsigned
software. New software meets the full list in Direct OS §5 and §6.

Accepted upload types: app bundles, UDIF disk images, flat
installer packages, and zip archives. Nested products: submit the
outermost container only.

------------------------------------------------------------------------
12. COMMON NOTARY FAILURES
------------------------------------------------------------------------

https://developer.apple.com/documentation/security/resolving-common-notarization-issues

Treat the notary log as the rejection list. The usual causes:

| Log | Fix in this pack |
|-----|------------------|
| The signature of the binary is invalid | Sign every executable, then do not modify the bundle. Sign inside out. |
| Wrong certificate | Use Developer ID Application or Developer ID Installer. A Mac App Store certificate will not notarize. |
| Missing timestamp | Sign with a secure timestamp. |
| Hardened runtime missing | Enable it on app and command-line targets. |
| `get-task-allow` | Remove it from the distribution entitlements. |
| Entitlements not XML or not ASCII | Re-export the entitlements as XML, ASCII. |
| SDK older than macOS 10.9 | Relink. New work uses the macOS 27 SDK. |
| Staple failed | Staple the same file you uploaded, after the ticket exists. |

A notary pass does not mean the Human Interface Guidelines are met.
It means the scan and the signature checks passed.

------------------------------------------------------------------------
13. PLUG-INS
------------------------------------------------------------------------

https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution

- Each plug-in you distribute is notarized, or a quarantined host
  on macOS 10.15 and later will refuse it until the user approves
  it in System Settings.
- The host's entitlements and purpose strings cover the plug-in
  (§7). Add them before you ship the host, not after a plug-in
  fails in the field.
- A plug-in that needs JIT or unsigned executable memory forces
  that exception onto the host. That exception is a product
  decision, recorded next to the entitlement, because it weakens
  the hardened runtime for the whole process.

------------------------------------------------------------------------
14. QUALITY CHECKS (THIS PROGRAM)
------------------------------------------------------------------------

Before you call the OS pack's `codesign` / `spctl` checks:

- Menu bar contains the commands the window also exposes
- Standard keyboard shortcuts are intact
- Bundle id, short version, and build number are set and the build
  number is new
- Icon is the Icon Composer asset, not a pre-rounded bitmap
- Every TCC API the binary calls has a purpose string
- Privacy manifest present when the SDK or an embedded SDK requires it
- Distribution entitlements have no `get-task-allow`
- Hardened-runtime exceptions match features you can point at
- Sandbox entitlements are present only if this direct app opted in
- Open and save go through the system panels
- VoiceOver reaches the primary actions

Then run the OS pack §14 checks on the file you will publish, and
staple it.

------------------------------------------------------------------------
15. WHAT THIS PACK EXPLICITLY IS NOT
------------------------------------------------------------------------

Not Gatekeeper, not the filesystem, not container construction.
Not App Review, App Store Connect, or store privacy details.
Not Swift or SwiftUI language rules. Not a Homebrew cask. Not an
iOS Human Interface Guidelines chapter. Not a license to request
Full Disk Access.

------------------------------------------------------------------------
16. COMPOSING WITH OTHER PACKS
------------------------------------------------------------------------

Direct Mac app:

  this pack + [direct-os-policy.md](direct-os-policy.md)
  + language packs and the macOS toolchain carve-out

Mac App Store app:

  this pack (everything except §11–12)
  + [app-store-application-policy.md](app-store-application-policy.md)
  + [app-store-os-policy.md](app-store-os-policy.md)

  The store app's submit queue is App Review. Its sandbox is
  mandatory. Its Human Interface Guidelines are still this pack.

Command-line tool with no UI:

  Skip this pack unless the tool has a bundle, a plist, or
  entitlements you author. Signing and notarization still follow
  Direct OS, and the notarytool steps in §11 still apply.

------------------------------------------------------------------------
17. QUICK OFFICIAL LINK LIST
------------------------------------------------------------------------

Design
https://developer.apple.com/design/human-interface-guidelines/
https://developer.apple.com/design/human-interface-guidelines/designing-for-macos
https://developer.apple.com/design/human-interface-guidelines/menus
https://developer.apple.com/design/human-interface-guidelines/app-icons
https://developer.apple.com/design/human-interface-guidelines/icons

Bundle
https://developer.apple.com/documentation/bundleresources/information-property-list
https://developer.apple.com/documentation/bundleresources/entitlements
https://developer.apple.com/documentation/bundleresources/privacy-manifest-files
https://developer.apple.com/documentation/uikit/requesting-access-to-protected-resources

Notary queue
https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution
https://developer.apple.com/documentation/security/customizing-the-notarization-workflow
https://developer.apple.com/documentation/security/resolving-common-notarization-issues
https://developer.apple.com/documentation/notaryapi

Sister packs
./direct-os-policy.md
./app-store-os-policy.md
./app-store-application-policy.md
./README.md

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.0.0 | Initial direct-distribution application map. Mac HIG, bundle contents, notarization queue. |
