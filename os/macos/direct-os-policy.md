---
title: "Direct distribution OS policy"
description: Curated map of macOS as the system a Developer ID product lands on — filesystem, signing enforcement, Gatekeeper, notarization tickets, optional sandbox, containers. Not the Human Interface Guidelines and not App Review.
version: "1.0.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - README.md
  - direct-application-policy.md
  - app-store-os-policy.md
  - app-store-application-policy.md
last_updated: "2026-10-02"
---

# Direct distribution OS policy

Reference pack for **macOS as the system a directly distributed
product lands on**: where files may live, which signature Gatekeeper
accepts, how a notarization ticket is checked, and which container
carries the bytes to the user.

**Role:** curated map (working memory). **Not** product law for one
app. **Not** the Human Interface Guidelines — that is
[direct-application-policy.md](direct-application-policy.md).
**Not** the Mac App Store payload — that is
[app-store-os-policy.md](app-store-os-policy.md).

Last verified against Apple's packaging, notarization, sandbox, and
developer news as of 2026-10-02.

This pack is what the OS actually enforces for a Developer ID ship.
Application maintainers still read it, because a `.app`, `.dmg`,
`.pkg`, or `.zip` is an OS artifact. Split **contents** from
**placement**: this pack owns OS behavior and placement.

------------------------------------------------------------------------
0. LAYERING
------------------------------------------------------------------------

This pack owns:

- The current macOS train and the Apple silicon ship host
- Filesystem placement for a direct product, including containers
  and System Integrity Protection
- Developer ID as the signature the system requires outside the store
- Hardened runtime as an OS protection
- Gatekeeper, quarantine, translocation, and the stapled ticket
- Notarization as trust (what the ticket means). The submit steps
  are the application pack
- App Sandbox and TCC **when a direct app opts in**, and Full Disk
  Access as an extraordinary grant
- `launchd` and `SMAppService` for helpers shipped inside the product
- Zip, disk image, and installer containers, including sign order

This pack does **not** own:

- Human Interface Guidelines, icons, menus, bundle-id choice
  → [direct-application-policy.md](direct-application-policy.md)
- `Info.plist` keys, purpose-string text, privacy manifest, the
  entitlements file as authored
  → [direct-application-policy.md](direct-application-policy.md)
- `notarytool` / Organizer steps and notary failure logs
  → [direct-application-policy.md](direct-application-policy.md)
- App Review, App Store Connect, store certificates, mandatory
  sandbox, store updates
  → [app-store-os-policy.md](app-store-os-policy.md)
  and [app-store-application-policy.md](app-store-application-policy.md)
- Xcode Command Line Tools as a C compiler, rustup, Homebrew prefixes
  → the language `*-os-policy.md` carve-out

Payload rule: a direct product is signed with Developer ID and
notarized. A Mac App Store product uses the store certificates and
is not notarized through this queue. One artifact, one payload.

------------------------------------------------------------------------
1. FOUNDATIONAL DOCUMENTS AND THE CURRENT TRAIN
------------------------------------------------------------------------

https://developer.apple.com/documentation/macos-release-notes/macos-27-release-notes
https://developer.apple.com/news/
https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution
https://developer.apple.com/documentation/xcode/packaging-mac-software-for-distribution

Current train, verified 2026-10-02:

- **macOS 27 Golden Gate** is the shipping release. The macOS 27 SDK
  ships in **Xcode 27**.
- Golden Gate runs on **Apple silicon only**.
- **macOS 26** is the last release that installs on Intel Macs.
- **macOS 27** is the last release that includes Rosetta. Intel-only
  apps stop running on Apple silicon after this release. Apple's
  stated exception is older unmaintained games that depend on
  Intel-only frameworks.
- New work in this pack targets **arm64**. A universal binary (arm64
  plus an Intel slice) is still one direct payload, used only when
  Intel Macs on macOS 26 remain in the product's support list. Record
  that choice. Intel is not a second OS pack.

https://developer.apple.com/documentation/apple-silicon

------------------------------------------------------------------------
2. THE DIRECT PAYLOAD
------------------------------------------------------------------------

https://developer.apple.com/documentation/xcode/packaging-mac-software-for-distribution

Two Apple payloads exist. This pack is the one **outside** the Mac
App Store.

- Sign with a **Developer ID** certificate. The notary rejects a Mac
  App Store distribution certificate, an ad-hoc signature, an Apple
  Development certificate, and a local development certificate.
- **Developer ID Application** signs apps, command-line executables,
  and disk images.
- **Developer ID Installer** signs installer packages (`.pkg`). It is
  a different certificate from Developer ID Application.
- Include a **secure timestamp**.
- Notarize the file the user downloads. Staple the ticket.

The original Developer ID Sub-CA expires **February 1, 2027**.
Certificates it issued stop working that day. New certificates come
from **Developer ID Certification Authority (G2)**. That authority
is valid until 2031. Certificates issued under it expire annually
and are renewed each year. Select the G2 intermediary when creating
a certificate. Update Xcode first if it is 11.4 or earlier.

What to re-sign before February 1, 2027:

- Installer packages signed by the expiring Sub-CA stop installing
  that day. Re-sign them with a G2 certificate.
- Apps already signed and notarized with a secure timestamp keep
  launching. Sign later updates with the new certificate and a
  secure timestamp.

https://developer.apple.com/help/account/certificates/replace-developer-id-certificates

------------------------------------------------------------------------
3. FILESYSTEM
------------------------------------------------------------------------

A direct product does not use the Filesystem Hierarchy Standard and
does not install under Debian `/usr`.

Places a Mac product actually uses:

| Path | Role |
|------|------|
| `/Applications` | Machine-wide apps |
| `~/Applications` | Apps for one user |
| `~/Library/Application Support/<Name>` | Per-user support files, unsandboxed |
| `~/Library/Preferences/<bundle-id>.plist` | Preferences, unsandboxed |
| `~/Library/Caches` | Recreatable caches |
| `~/Library/Logs` | Logs |
| `~/Library/Containers/<bundle-id>` | Sandbox container, when sandboxed |
| `~/Library/Group Containers/<group-id>` | App Group container |
| `Foo.app/Contents/MacOS/` | The executable inside the bundle |

System Integrity Protection covers the system volume (`/System` and
the parts of `/usr` Apple seals). A direct app does not write there.
`/usr/local` is not a Mac app prefix. Homebrew's prefix
(`/opt/homebrew` on Apple silicon, `/usr/local` on Intel) belongs to
the language toolchain carve-out, not to this payload.

https://developer.apple.com/documentation/xcode/protecting-local-app-data-using-containers

In macOS 14 and later the sandbox container is tied to the app's
code signature. In macOS 15 and later, App Group containers get
System Integrity Protection even for an app that is not sandboxed.
Members of the group can use the container. Other apps cannot.

------------------------------------------------------------------------
4. WHERE THE BUNDLE SITS
------------------------------------------------------------------------

The bundle layout (`Contents/MacOS`, `Contents/Info.plist`,
`Contents/Resources`) is application contents. This pack owns the
directory the user copies the bundle into.

- A disk image or zip does not choose the final path. The user
  copies the app, often to `/Applications`.
- An installer package may place components in specific locations.
  That is why a multi-component product uses a `.pkg`.
- Launching from the disk image or from the zip's unpack directory
  is a first-launch case this pack tests (see §12). It is not the
  installed location.

------------------------------------------------------------------------
5. CODE SIGNING (ENFORCEMENT)
------------------------------------------------------------------------

https://developer.apple.com/documentation/xcode/creating-distribution-signed-code-for-the-mac
https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution

The system checks, for every executable you distribute:

- A valid signature. Changing the bundle after signing invalidates it.
- The Developer ID certificate named in §2, matched to the container
  type (Application vs Installer).
- A secure timestamp on Developer ID signatures.
- Entitlements stored as properly formed XML, ASCII-encoded.
- No `com.apple.security.get-task-allow` entitlement set true on the
  build you notarize.
- The binary is linked against the macOS 10.9 SDK or later. That is
  the notary's floor. This pack's ship host for new work is the
  macOS 27 SDK on arm64 (§1).

Sign **inside out**. Sign the deepest nested bundle, framework, or
tool first, then each parent. Sign every nested container that
supports signing. A zip archive cannot be signed; sign its contents
before you archive them.

https://developer.apple.com/documentation/xcode/packaging-mac-software-for-distribution

------------------------------------------------------------------------
6. HARDENED RUNTIME
------------------------------------------------------------------------

https://developer.apple.com/documentation/security/hardened-runtime

Hardened Runtime, together with System Integrity Protection, blocks
classes of code injection, library hijacking, and process-memory
tampering. Notarization requires it on app and command-line targets.

Turn it on for those targets. Add an exception entitlement only for
a capability the app actually uses (JIT, unsigned executable memory,
disabling library validation, and the other exceptions Apple lists).
Shared libraries, frameworks, and in-process plug-ins do not get
their own entitlements. They inherit the host executable's.

The entitlements file is authored in the application pack. This pack
owns the fact that the OS refuses to run a notarized app that needed
hardened runtime and shipped without it.

------------------------------------------------------------------------
7. GATEKEEPER, QUARANTINE, AND TRANSLOCATION
------------------------------------------------------------------------

https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution

Gatekeeper is the launch-time check. Notarization is the earlier
scan. A ticket does not skip Gatekeeper. It lets Gatekeeper describe
the software as notarized on first open.

- Files received from the internet or AirDrop carry the quarantine
  attribute. Gatekeeper assesses quarantined code.
- The ticket is stapled to the file the user received, or Gatekeeper
  looks it up online. Without a staple, an offline Mac can block
  the product.
- On macOS 10.15 and later, a quarantined plug-in loads only if that
  plug-in is notarized, unless the user approves it in System
  Settings.

**Translocation.** On the first launch of an app opened straight
from a zip or a disk image, Gatekeeper presents a randomized path
from bundle-URL APIs. That stops the app from loading adjacent
files that the signature does not seal. Translocation applies to
that first launch. A later launch, or a launch after the user moves
the app, uses the real path. Test both.

------------------------------------------------------------------------
8. NOTARIZATION AS TRUST
------------------------------------------------------------------------

https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution

The notary service scans for malicious content and code-signing
problems. It is automated. **It is not App Review.** If the scan
passes, Apple issues a ticket and publishes it for Gatekeeper.
Staple that ticket to the distribution file.

Deliverables the service accepts include:

- macOS apps
- Non-app bundles
- UDIF disk images
- Flat installer packages
- Zip archives

The service also keeps an audit trail for the Developer ID key. A
compromised key is revoked with Apple against the tickets for the
unauthorized builds. That recovery is an OS trust action, not a
store appeal.

Submit steps, Organizer, `notarytool`, and the failure log belong to
[direct-application-policy.md](direct-application-policy.md).

------------------------------------------------------------------------
9. SANDBOX WHEN A DIRECT APP OPTS IN
------------------------------------------------------------------------

https://developer.apple.com/documentation/xcode/configuring-the-macos-app-sandbox
https://developer.apple.com/documentation/security/accessing-files-from-the-macos-app-sandbox

App Sandbox is a kernel access control. It limits the damage a
compromised app can do. On **this** payload it is optional. The Mac
App Store payload makes it mandatory. Do not import that requirement
here.

When a direct app does opt in:

- The first launch creates `~/Library/Containers/<bundle-id>`. The
  app can read and write that container.
- Symlinks inside the container point at user folders such as
  Downloads and Pictures. Those locations still need the matching
  entitlement before the symlink target is usable.
- User-selected files are a separate grant (the open panel and
  security-scoped bookmarks). The bookmark behavior is application
  contents. The grant is this OS.
- POSIX permissions and other mandatory controls still apply inside
  the container. The sandbox is not a blanket allow.
- The app cannot run programs that sit outside the bundle, the
  container, or an App Group container merely by holding the
  user-selected-file entitlement.

Declaring `com.apple.security.app-sandbox` is the application pack.
Creating the container and enforcing the grants is this pack.

------------------------------------------------------------------------
10. TCC AND FULL DISK ACCESS
------------------------------------------------------------------------

Transparency, Consent, and Control prompts are this OS. The purpose
string the user reads is application contents. The app must have
that string before the prompt can succeed. The string does not
itself grant access.

Protected folders (Desktop, Documents, Downloads, removable volumes,
network volumes) and devices (camera, microphone, contacts, and the
rest Apple lists) follow that split.

**Full Disk Access** is not one of those prompts. It bypasses the
normal controls so backup-class tools can read the disk. Apple's
developer news of October 2, 2026 says further controls are coming
so this grant requires a very explicit user action, including
because agent-style software raises the stakes. A direct app uses
the open panel, security-scoped bookmarks, and the specific TCC
entitlements. It does not request Full Disk Access for ordinary
document access.

https://developer.apple.com/news/

------------------------------------------------------------------------
11. LAUNCHD AND LOGIN ITEMS
------------------------------------------------------------------------

https://developer.apple.com/documentation/servicemanagement/smappservice

Helpers that belong to the app ship **inside the bundle**. On macOS
13 and later, `SMAppService` registers a login item, Launch Agent,
or Launch Daemon from that embedded property list. That replaces
copying a plist into `~/Library/LaunchAgents`, `/Library/LaunchAgents`,
or `/Library/LaunchDaemons`.

- A Launch Agent runs in the user domain.
- A Launch Daemon runs in the system domain and needs an install
  path that can write there, which for a direct product usually
  means an installer package, not a dragged `.app`.

The property-list keys are the Service Management framework's. The
choice to start at login is a product decision the application pack
states. This pack owns registration and the domain.

The Mac App Store forbids silent login items. That ban is the store
OS pack. A direct app may register a login item, and the system
still surfaces it for the user to approve.

------------------------------------------------------------------------
12. CONTAINERS — ZIP, DISK IMAGE, INSTALLER
------------------------------------------------------------------------

https://developer.apple.com/documentation/xcode/packaging-mac-software-for-distribution

Pick one outer container for the file users download.

| Container | Signature | When |
|-----------|-----------|------|
| `.zip` | Cannot sign the archive. Sign the contents. Build with `ditto -c -k --keepParent`. | Single bundle the user moves by hand |
| `.dmg` | Sign with **Developer ID Application**, `--timestamp`, and an identifier that is unique and not the bundle id. Prefer a UDIF read-only zip-compressed image (UDZO) when a layout tool builds it. | Single bundle, with a signed seal over the whole image |
| `.pkg` | Sign with **Developer ID Installer**. | Several components, fixed install paths, or scripts during install |

Nest from the inside out. An app inside a package on a disk image:
sign the app, build and sign the package, build and sign the disk
image, **notarize only the disk image**. Staple the ticket to that
outer file. `xcrun stapler staple` works on disk images and
packages. A zip needs the staple flow Apple documents for apps
inside archives.

Gatekeeper can block an unstapled product while the Mac is offline.

Test on a Mac that is not the build machine:

- First install on a clean account
- Upgrade over an older copy, including a copy that lived elsewhere
- A second copy of the same version in another path
- A user account that is not the account that ran the installer
- For zip and disk image: first open in place (translocation), then
  open again, then open after a move to `/Applications`

------------------------------------------------------------------------
13. UPDATES AND THE DEVELOPER ID CLOCK
------------------------------------------------------------------------

Apple's Software Update does not update a Developer ID app. The
next version is another notarized container the vendor ships. A
third-party updater (Sparkle and similar) is not mapped in this
family. If one is used, the helper it downloads is still code this
pack requires to be signed and notarized.

Do not check a Mac App Store receipt on this payload. Do not ship
a store update mechanism here.

The live clock for certificates is §2 (Sub-CA on February 1, 2027,
and annual certificate renewal under G2).

------------------------------------------------------------------------
14. QUALITY CHECKS (THIS OS)
------------------------------------------------------------------------

On the file you will actually ship:

```text
codesign -dv --verbose=4 Foo.app
codesign --verify --deep --strict Foo.app
spctl --assess --type execute -v Foo.app
xcrun stapler validate Foo.app
```

Use the outer container (the `.dmg` or `.pkg`) in the stapler and
Gatekeeper checks when that is the downloaded file.

Also confirm:

- Certificate is Developer ID Application or Developer ID Installer,
  matched to the container, and is a G2 certificate for anything
  you still need to install after February 1, 2027
- Secure timestamp present
- Hardened runtime enabled on app and command-line targets
- `get-task-allow` absent
- arm64, unless a documented universal binary still supports Intel
  on macOS 26
- Signature still valid after the last byte you add to the bundle

------------------------------------------------------------------------
15. WHAT THIS PACK EXPLICITLY IS NOT
------------------------------------------------------------------------

Not the Human Interface Guidelines. Not `Info.plist` authorship.
Not App Review or App Store Connect. Not a Mac App Store
distribution certificate. Not Swift, and not the Xcode Command Line
Tools as a language toolchain. Not Homebrew formulae or casks. Not
iOS notarization, alternative marketplaces, or web distribution.
Not kernel extensions or system extensions (a system extension that
needs a hardened-runtime exception is refused by macOS; map those
products in a later pack if they get their own manuals).

------------------------------------------------------------------------
16. COMPOSING WITH OTHER PACKS
------------------------------------------------------------------------

Direct Mac app:

  [direct-application-policy.md](direct-application-policy.md)
  + this pack
  + the language packs for the language you ship
  + that language's macOS carve-out for the compiler and prefix

Command-line tool that Gatekeeper must open, with no app UI:

  this pack (sign, hardened runtime, notarize, staple)
  + the language packs
  Skip Direct Application.

Mac App Store app:

  Do not apply this pack's certificate, notary queue, or optional
  sandbox. Open the App Store OS pack. Human Interface Guidelines
  still come from Direct Application.

------------------------------------------------------------------------
17. QUICK OFFICIAL LINK LIST
------------------------------------------------------------------------

Release train
https://developer.apple.com/documentation/macos-release-notes/macos-27-release-notes
https://developer.apple.com/news/
https://developer.apple.com/documentation/apple-silicon

Signing, notarization, packaging
https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution
https://developer.apple.com/documentation/security/hardened-runtime
https://developer.apple.com/documentation/xcode/packaging-mac-software-for-distribution
https://developer.apple.com/documentation/xcode/creating-distribution-signed-code-for-the-mac
https://developer.apple.com/help/account/certificates/replace-developer-id-certificates

Sandbox, files, helpers
https://developer.apple.com/documentation/xcode/configuring-the-macos-app-sandbox
https://developer.apple.com/documentation/security/accessing-files-from-the-macos-app-sandbox
https://developer.apple.com/documentation/xcode/protecting-local-app-data-using-containers
https://developer.apple.com/documentation/servicemanagement/smappservice

Sister packs
./direct-application-policy.md
./app-store-os-policy.md
./app-store-application-policy.md
./README.md

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.0.0 | Initial direct-distribution OS map. Golden Gate 27, Developer ID G2, notarization as trust, optional sandbox. |
