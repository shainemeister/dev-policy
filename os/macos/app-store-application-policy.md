---
title: "Mac App Store application policy"
description: Curated map of App Review and App Store Connect for a Mac app. Not the Human Interface Guidelines and not Developer ID notarization.
version: "1.0.0"
status: current
audience:
  - developers
  - maintainers
doc_type: other
related:
  - README.md
  - direct-application-policy.md
  - direct-os-policy.md
  - app-store-os-policy.md
last_updated: "2026-10-02"
---

# Mac App Store application policy

Reference pack for **what App Review checks on a Mac app**, and for
the metadata you enter in App Store Connect. The program itself
(Human Interface Guidelines, bundle contents, purpose strings) stays
in [direct-application-policy.md](direct-application-policy.md).

**Role:** curated map. **Not** a copy of the App Review Guidelines.
**Not** notarization. **Not** the store installer and sandbox
machinery — those are [app-store-os-policy.md](app-store-os-policy.md).

Last verified against the App Review Guidelines as of 2026-10-02.
The Guidelines page says last updated **June 8, 2026**.

The five sections of the Guidelines are Safety, Performance,
Business, Design, and Legal. This pack maps the Mac delta and the
submit checklist. The full text stays on Apple's site.

iOS notarization, alternative app marketplaces, and web distribution
are called out on that page for other platforms. They are not Mac
payloads. Ignore the "Highlight Notarization Review Guidelines
Only" filter when the artifact is a Mac app.

------------------------------------------------------------------------
0. LAYERING
------------------------------------------------------------------------

This pack owns:

- App Review as the queue for a Mac App Store app
- The Mac-specific product rules in guideline 2.4.5 that are about
  the program (license screens, copy protection, single bundle of
  localizations) together with the system half the OS pack enforces
- Payments and purchase rules as they apply to a store app
- App Store Connect metadata: description, screenshots, privacy
  details, age rating, review notes
- Trademark and marketing limits on how the listing presents Apple

This pack does **not** own:

- Human Interface Guidelines, menus, icons, `Info.plist`, purpose
  strings, the privacy manifest file
  → [direct-application-policy.md](direct-application-policy.md)
- Sandbox enforcement, the installer package, store updates as a
  mechanism
  → [app-store-os-policy.md](app-store-os-policy.md)
- Developer ID and the notary log
  → Direct OS and Direct Application

------------------------------------------------------------------------
1. FOUNDATIONAL DOCUMENTS
------------------------------------------------------------------------

https://developer.apple.com/app-store/review/guidelines/
https://developer.apple.com/help/app-store-connect/
https://developer.apple.com/app-store/submitting/

Review scans for malware and also reads the program. A notary pass
on some other build does not satisfy this queue. The build you
upload is the store-signed package from the OS pack.

You are responsible for third-party SDKs in the binary, including
ads and analytics. Review holds the app to the Guidelines for their
behavior too.

Some capabilities are entitlements Apple grants for limited cases
(the Guidelines' examples include CarPlay Audio, HyperVisor, and
Privileged File Operations). A missing grant is a review blocker,
not a local entitlement you flip on.

------------------------------------------------------------------------
2. BEFORE YOU SUBMIT
------------------------------------------------------------------------

Apple's own pre-submit list, kept short:

- The build does not crash. Backend services are live.
- Metadata matches the binary.
- The account contact in App Store Connect reaches a person.
- Review can open every feature. Account-gated apps include a demo
  account or a full demo mode, plus any hardware or QR code the
  path needs. Say so in the review notes.
- Non-obvious features and in-app purchases are explained in those
  notes.
- The binary follows the developer documentation it claims
  (AppKit, SwiftUI, app extensions) and the Human Interface
  Guidelines in Direct Application.

An app you no longer stand behind is removed. Shipping a broken
update to keep a listing is not a strategy this pack accepts.

TestFlight is the store's beta channel for this payload. It is not
a Developer ID release.

------------------------------------------------------------------------
3. MAC-SPECIFIC REVIEW (GUIDELINE 2.4.5)
------------------------------------------------------------------------

https://developer.apple.com/app-store/review/guidelines/#software-requirements

2.4.5 is the Mac list. The OS pack owns enforcement of sandbox,
packaging, login items, extra code, root, and store-only updates.
This pack owns the product rules and the expectation that review
will look at all of them together:

| Clause | This pack checks |
|--------|------------------|
| (i) | The program uses the real APIs for other apps' data. Bookmarks, contacts, and calendars are not scraped out of files. |
| (ii) | One app bundle, Xcode packaging. No second product hidden in the archive. |
| (iii) | The program does not add itself to the Dock or the desktop, and does not keep working after quit, without the user asking. |
| (iv) | What review ran is what the user gets. No later download that changes features. |
| (v) | The program does not ask for root. |
| (vi) | No license screen at launch, no license keys, no private copy protection. |
| (vii) | The program does not contain its own updater. |
| (viii) | The program runs on the shipping OS and does not need an optional runtime such as Java. |
| (ix) | Every localization ships inside the one bundle. |

(vi) and (vii) are the sharp split with direct distribution. A
Developer ID app may show a license and may ship its own next
version. A store app uses in-app purchase and store updates instead.

Guideline 2.5.1: public APIs only, used for the purpose you describe.
Guideline 2.5.2: the app stays inside its container and does not
download code that changes features. Teaching tools that download
student code are the limited exception in that clause, and the
source has to be visible and editable by the learner.

------------------------------------------------------------------------
4. PAYMENTS
------------------------------------------------------------------------

https://developer.apple.com/app-store/review/guidelines/#business

Guideline 3.1.1: unlocking features, subscriptions, content, or a
full version inside a store app uses in-app purchase. License keys,
and the other off-store unlocks the clause lists, are grounds for
rejection.

Mac-specific line in that clause: a Mac App Store app may host
plug-ins or extensions that are enabled by a mechanism other than
the App Store. Those plug-ins are still code. Direct Application §13
and the sandbox rules still apply. This exception is not permission
to download a changed app.

Restorable purchases need a restore path. Odds for randomized items
are disclosed before purchase. Subscriptions that remove a feature
someone already paid for are a rejection.

External-purchase link entitlements in 3.1.1(a) are written for
specific regions and, in the current text, for the iOS and iPadOS
stores. Do not copy an iOS external-link entitlement onto a Mac app
unless Apple's Mac entitlement for that program says you can.

------------------------------------------------------------------------
5. METADATA, PRIVACY DETAILS, AND AGE RATING
------------------------------------------------------------------------

https://developer.apple.com/help/app-store-connect/
https://developer.apple.com/app-store/user-privacy-and-data-use/

The listing is part of the program review sees:

- Name, subtitle, description, and screenshots show the Mac app.
  They do not show an iOS UI and call it the Mac product.
- Keywords and description match features that exist in the binary.
- Privacy details (the data-collection answers in App Store
  Connect) match the privacy manifest and the purpose strings in
  Direct Application §8. The file is that pack. The form is this
  pack.
- Age rating answers are complete, including the social-media and
  time-allowance questions Apple has required on current
  submissions. Starting points are in developer news. The answers
  live in App Store Connect.
- The accessibility nutrition label on the product page, added for
  current OS releases, describes features the app actually has
  (Direct Application §9).

Screenshots are Mac windows at the sizes App Store Connect asks
for. Product-page headers and search assets follow Apple's current
asset guide when you use them.

https://developer.apple.com/app-store/asset-best-practices/

------------------------------------------------------------------------
6. DESIGN, SAFETY, AND MARKS
------------------------------------------------------------------------

Guideline 4 (Design) points review at the Human Interface
Guidelines. The Mac chapter is Direct Application §3–5. Review can
reject a store app that does not follow it. That does not move
ownership of the guidelines into this pack.

Guideline 1 (Safety) is content: objectionable material,
user-generated content with filtering, reporting, blocking, and a
published contact, and the Kids category when you opt into it.
Those rules apply to the Mac listing the same way. This pack does
not restate each example.

Do not use Apple's trademarks as the app's name or icon. Marketing
and identity guidelines:

https://developer.apple.com/app-store/marketing/guidelines/
https://www.apple.com/legal/intellectual-property/guidelinesfor3rdparties.html

Cheating review (hidden features, fake ratings, misleading
metadata) removes the app and can remove the developer account.
The binary review runs is the binary users get (§3, clause iv).

------------------------------------------------------------------------
7. QUALITY CHECKS (THIS QUEUE)
------------------------------------------------------------------------

Before you upload the store package from the OS pack:

- Demo account or demo mode written into review notes
- 2.4.5 table in §3 checked, including no license key and no
  private updater
- In-app purchase used for anything that unlocks the program
- Privacy answers match the manifest
- Age rating complete
- Screenshots are the Mac app
- Human Interface Guidelines checks in Direct Application §14
  already done
- Sandbox and installer checks in App Store OS §7 already done

A `notarytool` success is not an item on this list.

------------------------------------------------------------------------
8. WHAT THIS PACK EXPLICITLY IS NOT
------------------------------------------------------------------------

Not the Human Interface Guidelines. Not `Info.plist`. Not
notarization. Not the installer certificate. Not iOS review
highlights, alternative marketplaces, or web distribution. Not
Swift. Not a Homebrew cask.

------------------------------------------------------------------------
9. COMPOSING WITH OTHER PACKS
------------------------------------------------------------------------

Mac App Store app:

  this pack
  + [app-store-os-policy.md](app-store-os-policy.md)
  + [direct-application-policy.md](direct-application-policy.md)
    except that pack's notary queue
  + language packs and the macOS toolchain carve-out

Direct Developer ID app:

  Do not open this pack. A license screen and a vendor update are
  allowed there and rejected here.

------------------------------------------------------------------------
10. QUICK OFFICIAL LINK LIST
------------------------------------------------------------------------

https://developer.apple.com/app-store/review/guidelines/
https://developer.apple.com/help/app-store-connect/
https://developer.apple.com/app-store/submitting/
https://developer.apple.com/app-store/user-privacy-and-data-use/
https://developer.apple.com/app-store/asset-best-practices/
https://developer.apple.com/app-store/marketing/guidelines/
https://www.apple.com/legal/intellectual-property/guidelinesfor3rdparties.html
https://developer.apple.com/design/human-interface-guidelines/

Sister packs
./direct-application-policy.md
./app-store-os-policy.md
./direct-os-policy.md
./README.md

------------------------------------------------------------------------
Document history
------------------------------------------------------------------------

| Version | Notes |
|---------|--------|
| 1.0.0 | Initial Mac App Store application map. Review queue, guideline 2.4.5 product rules, App Store Connect metadata. |
