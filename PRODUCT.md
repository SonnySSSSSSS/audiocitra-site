# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
Home and project-studio producers and mixers on Windows. They're tired of plug-ins that get a unit's behaviour right but never its tone. They try a plug-in for 14 days and buy only what they're already using.

## Product Purpose
audiocitra.com presents and sells Audio Citra's VST3 plug-ins for Windows. Success means a visitor understands what a plug-in does and how it sounds, tries it, and keeps it.

What's on sale changes. `buy.html` is the source of truth. As of 2026-11-18, Spanda (channel strip), Ākāśa (coloured reverb) and Tulā (mix utility) are on sale in early access, and Gālana, Agni, Shunya and Lahari are "coming soon".

## Positioning
Plug-ins that sound like the gear, not just act like it. Parts are fitted to analysis of real hardware units, then checked by ear, and visitors can hear the result in before/after clips. Built with AI, said openly.

The maker is in the buyer's own situation: a long-time mixer, not a pro studio, building the plug-ins they wanted and couldn't find. The site says this plainly, as a strength, and never claims to be a pro studio.

## Operating Context
- Visitors judge sound: before/after audio clips (`audio/`), a "try it" player with sample stems, measurement figures and 3D renders of each plug-in's skins.
- Buying goes through Paddle, the reseller and merchant of record. The licence is e-mailed, or fetched inside the plug-in.
- Requirements: Windows 10 or 11 (64-bit) and a VST3 host. Mac isn't supported yet.
- The site is static HTML/CSS/JS on GitHub Pages. Every push to `main` deploys to audiocitra.com.

## Capabilities and Constraints
- Every released plug-in runs fully for 14 days. One licence covers all of the buyer's own computers.
- Early access (beta): every update is free, including 1.0 and all 1.x.
- Refunds: `refund.html` offers a full refund within 14 days of purchase, for any reason. Open: the owner decided on 2026-11-05 that each plug-in in the Everything bundle gets 14 days from its own release, but the site doesn't say so yet. Settle this before changing refund copy.
- Coming-soon plug-ins have no Download or single-licence Buy until they're released.
- As of 2026-11-18, plug-ins aren't code-signed.
- Walkthrough videos are on the product pages. Spanda's 15:20 walkthrough is marked "Draft".
- Tech: static files with no build step. Each page links `site.css`, `site.js` and other scripts with its own `?v=` string, so a changed file needs that string bumped on every page that loads it.
- Open: may the site name the hardware units the plug-ins are fitted to? Undecided. Until it is, don't add hardware names that aren't already on the site.

## Brand Commitments
- Name: Audio Citra. Plug-in names keep their diacritics (Ākāśa, Gālana, Tulā).
- Voice: the owner's own, first person, plain and honest, including doubt ("I'm no audio genius"). No marketing speak.
- Maker story: a long-time mixer with a lot of gripes. The About page states over two decades of audio production, mixing and mastering, and brief work with two Grammy award winners. Tell it in the owner's words, never inflated.
- Logo: the owner's cyan lotus artwork, used only as supplied. Never redraw, retrace or recolour it, and never substitute another mark. A dark backing behind it is the only allowed treatment. The owner's standing rule; ask before any change to the logo.

## Evidence on Hand
- Real assets: before/after audio clips (`audio/`, listed in `audio/clips.json`), renders and screenshots (`img/`), measurement figures on product pages, and the About story.
- None exist yet: customer testimonials, user counts, press, or A/B comparisons against named competitors. Never invent these.

## Product Principles
1. Only say what's true and buyable today. Availability, price and policy copy must match what's actually for sale.
2. Speak as one person, not a company.
3. Try first, keep only what you use. No pressure tactics: no countdowns, fake scarcity or nagging upsells.
4. Let the sound carry the claims. Where a page claims something about sound, put a way to hear it close by. This doesn't require restructuring existing pages.
5. Show the work: measurements and listening, with AI's role stated plainly.

## Accessibility & Inclusion
Hold the site to WCAG 2.2 AA.
