---
title: "Mac App Store OS policy"
description: Curated map of the Mac App Store payload — store certificates, the Xcode installer package, mandatory sandbox, and the system behaviors review forbids. Not Developer ID and not the Human Interface Guidelines.
version: "1.0.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - README.md
  - direct-os-policy.md
  - direct-application-policy.md
  - app-store-application-policy.md
last_updated: "2026-10-02"
---

# Mac App Store OS policy

Reference pack for **the Mac App Store as a payload**: which
certificate seals the product, where the store puts it, and which
system behaviors a store app is not allowed to have.

**Role:** curated map. **Not** the Human Interface Guidelines and
**not** the reviewer's checklist of content — those are
[direct-application-policy.md](direct-application-policy.md) and
[app-store-application-policy.md](app-store-application-policy.md).
**Not** Developer ID, Gatekeeper tickets, or notarization.

Last verified against Apple's packaging document and App Review
Guidelines as of 2026-10-02. The Guidelines were last updated
June 8, 2026.

Read [direct-os-policy.md](direct-os-policy.md) for the platform
facts this payload shares: Apple silicon as the new-work host,
System Integrity Protection, standard directories, TCC prompts, and
Full Disk Access. This pack states only where the store overrides
that map. When they disagree, this pack wins for a store artifact.

------------------------------------------------------------------------
0. LAYERING
------------------------------------------------------------------------

This pack owns:

- The Mac App Store certificate family and the installer package
  Apple accepts
- Mandatory App Sandbox and the store container
- Store-managed install location and a self-contained bundle
- The prohibitions in guideline 2.4.5 that are system behavior:
  no third-party installer, no shared-location install, no silent
  login item, no leftover process, no extra code, no root, no
  setuid, updates only through the store
- The requirement to run on the currently shipping OS

This pack does **not** own:

- Human Interface Guidelines, icons, menus, `Info.plist` authorship,
  purpose strings, privacy manifest
  → [direct-application-policy.md](direct-application-policy.md)
- Review criteria for content, payments, metadata, and the submit
  notes
  → [app-store-application-policy.md](app-store-application-policy.md)
- Developer ID certificates, notarization, stapling, optional sandbox
  → [direct-os-policy.md](direct-os-policy.md)
- Language toolchains and Homebrew prefixes
  → `program-language/*-os-policy.md`

Payload rule: one store app, one store payload. Do not also staple
a Developer ID ticket and call it the same artifact.

------------------------------------------------------------------------
1. FOUNDATIONAL DOCUMENTS
------------------------------------------------------------------------

https://developer.apple.com/documentation/xcode/packaging-mac-software-for-distribution
https://developer.apple.com/app-store/review/guidelines/
https://developer.apple.com/documentation/xcode/configuring-the-macos-app-sandbox

Guideline 2.4.5 is the Mac-specific list. The rest of the Guidelines
are the application pack. The filesystem document 2.4.5 points at
is the archive File System Programming Guide. Container behavior
for a sandboxed app is also the current sandbox articles below.

https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/Introduction/Introduction.html
https://developer.apple.com/documentation/security/accessing-files-from-the-macos-app-sandbox

------------------------------------------------------------------------
2. THE STORE PAYLOAD
------------------------------------------------------------------------

A Mac App Store app is submitted as an **installer package** built
with Xcode's tools. Third-party installers are not accepted.

The package is signed with the **Mac Installer Distribution**
identity. In the packaging document that identity is named
`3rd Party Mac Developer Installer`. It is not Developer ID
Installer. The app inside the package is signed for Mac App Store
distribution. It is not signed with Developer ID Application.
A Developer ID signature will not pass this queue, and a store
signature will not pass the notary.

Upload uses the tool Apple's packaging document names (Transporter,
or `altool` as that page still describes) or Xcode's App Store
distribution path. The upload lands in App Store Connect. The
queue after that is review, not notarization.

https://developer.apple.com/help/app-store-connect/

A simple single-app package, as that document gives it:

```text
productbuild --sign <Mac Installer Distribution identity> \
  --component <PathToApp> /Applications <PathToPackage>
```

The `/Applications` argument is the install location the store
package records. It is not a license to write arbitrary files
beside the bundle.

------------------------------------------------------------------------
3. MANDATORY SANDBOX
------------------------------------------------------------------------

https://developer.apple.com/documentation/xcode/configuring-the-macos-app-sandbox

Guideline 2.4.5 (i): a Mac App Store app is sandboxed and follows
the macOS file system rules. It touches other apps' user data
(bookmarks, contacts, calendars) only through the APIs meant for
that data.

- `com.apple.security.app-sandbox` is true on the app you submit.
  The declaration is reviewed as contents. The container is this
  pack.
- The container is `~/Library/Containers/<bundle-id>`. Support
  files, preferences, caches, and logs for a store app live there,
  not in the unsandboxed `~/Library` locations Direct OS lists for
  an opted-out app.
- User-selected files and security-scoped bookmarks are how a
  store app keeps access to documents. See Direct Application §10
  for the program side.
- App Groups are the supported share between this developer's
  apps. Arbitrary paths in `/Library` are not.
- Network, hardware, and folder entitlements are the minimum the
  program uses. Review can reject a sandbox that asks for
  everything. The entitlement text is Direct Application §7. The
  requirement that the sandbox exist is this pack.

An unsandboxed build is a direct-distribution product. It is not
this payload.

------------------------------------------------------------------------
4. INSTALL LOCATION AND A SELF-CONTAINED BUNDLE
------------------------------------------------------------------------

Guideline 2.4.5 (ii) and (ix):

- Packaged and submitted with Xcode technologies.
- One self-contained app bundle. All localizations live in that
  bundle.
- The app does not install code or resources into shared locations.
- It does not install a second app beside itself.

Helpers that must exist are embedded in the bundle and registered
with `SMAppService` where the system requires a login item (Direct
OS §11 describes the mechanism). A store app still has to meet §5
below before that helper may start.

------------------------------------------------------------------------
5. PROHIBITED SYSTEM BEHAVIOR
------------------------------------------------------------------------

Guideline 2.4.5, system half. The application pack repeats the
items that are product behavior (license screens, copy protection)
so a reviewer and an implementer share one list. Enforcement is
here.

- **(iii)** No auto-launch at startup or login without consent. No
  process left running after the user quits. No Dock icon and no
  desktop shortcut added automatically.
- **(iv)** No downloading or installing standalone apps, kernel
  extensions, extra code, or resources that add features or change
  the app from the build review saw.
- **(v)** No root. No `setuid`.
- **(viii)** Runs on the currently shipping OS. Does not depend on
  deprecated or optionally installed technology (the guideline's
  example is Java). As of 2026-10-02 the shipping OS is macOS 27
  Golden Gate.

Direct OS allows a Developer ID daemon and a vendor-shipped update.
This payload does not.

------------------------------------------------------------------------
6. UPDATES COME FROM THE STORE
------------------------------------------------------------------------

Guideline 2.4.5 (vii): updates are distributed by the Mac App
Store. Other update mechanisms are not allowed. Sparkle, a
hand-rolled downloader, and a Developer ID disk image offered as
the upgrade path are out of this payload.

The store delivers the update. The app does not notarize its own
patch. A receipt check, if you validate purchases, uses StoreKit.
It is not a Developer ID notarization ticket.

------------------------------------------------------------------------
7. QUALITY CHECKS (THIS PAYLOAD)
------------------------------------------------------------------------

On the package you upload:

- Signed with the Mac Installer Distribution identity, not
  Developer ID
- `com.apple.security.app-sandbox` is true
- No `get-task-allow`
- One bundle, resources inside it, localizations inside it
- No installer technology other than Xcode's
- No helper that starts at login without a consent path
- No updater other than the App Store
- Runs on macOS 27, arm64, unless the product's support list still
  includes an older OS and says so in App Store Connect

Platform checks that are identical to a direct app (purpose strings
present, hardened runtime if you turn it on, icon, menu bar) stay
in Direct Application. Do not run `notarytool` and treat a pass as
store acceptance.

------------------------------------------------------------------------
8. WHAT THIS PACK EXPLICITLY IS NOT
------------------------------------------------------------------------

Not Developer ID. Not notarization. Not Gatekeeper policy for a
disk image. Not the Human Interface Guidelines. Not payments and
metadata (application pack). Not iOS App Store rules, iOS
notarization, or alternative marketplaces. Not a Homebrew cask.

------------------------------------------------------------------------
9. COMPOSING WITH OTHER PACKS
------------------------------------------------------------------------

Mac App Store app:

  this pack
  + [app-store-application-policy.md](app-store-application-policy.md)
  + [direct-application-policy.md](direct-application-policy.md)
    for the program (skip that pack's notary queue)
  + language packs and the macOS toolchain carve-out

Leave [direct-os-policy.md](direct-os-policy.md) closed except to
cite shared platform facts (train, SIP, TCC, `SMAppService`).
Where this pack overrides those facts, follow this pack.

Direct Developer ID app:

  Do not open this pack.

------------------------------------------------------------------------
10. QUICK OFFICIAL LINK LIST
------------------------------------------------------------------------

https://developer.apple.com/documentation/xcode/packaging-mac-software-for-distribution
https://developer.apple.com/app-store/review/guidelines/
https://developer.apple.com/documentation/xcode/configuring-the-macos-app-sandbox
https://developer.apple.com/documentation/security/accessing-files-from-the-macos-app-sandbox
https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/Introduction/Introduction.html
https://developer.apple.com/help/app-store-connect/
https://developer.apple.com/documentation/servicemanagement/smappservice

Sister packs
./direct-os-policy.md
./direct-application-policy.md
./app-store-application-policy.md
./README.md

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.0.0 | Initial Mac App Store OS map. Store installer, mandatory sandbox, guideline 2.4.5 system rules. |
