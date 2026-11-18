---
name: Audio Citra
description: VST3 plug-ins for Windows, shown like gear in a studio after dark.
colors:
  night: "#0c0b10"
  panel: "#16141d"
  line: "#2a2733"
  night-fg: "#ece9f2"
  night-mute: "#8d8899"
  on-accent: "#111111"
  spanda: "#c58bff"
  galana: "#ffb35c"
  akasa: "#e895a0"
  shunya: "#1f6a82"
  shunya-lt: "#5fb0cc"
  agni: "#ff6a3d"
  lahari: "#5fd4b4"
  tula: "#e8b04a"
  pale: "#eef0ee"
  pale-fg: "#1d2124"
  pale-mute: "#5f676c"
  paper: "#f4f1ea"
  ink: "#2b2830"
  film-warm: "#fff3dc"
typography:
  display:
    fontFamily: "Bodoni Moda, Georgia, serif"
    fontSize: "clamp(40px, 7vw, 92px)"
    fontWeight: 800
    lineHeight: 0.98
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Bodoni Moda, Georgia, serif"
    fontSize: "clamp(32px, 5vw, 60px)"
    fontWeight: 800
    lineHeight: 1.02
    letterSpacing: "-0.02em"
  title:
    fontFamily: "IBM Plex Sans, system-ui, sans-serif"
    fontSize: "18px"
    fontWeight: 600
  body:
    fontFamily: "IBM Plex Sans, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.55
  lede:
    fontFamily: "IBM Plex Sans, system-ui, sans-serif"
    fontSize: "18px"
    fontWeight: 400
  label:
    fontFamily: "IBM Plex Mono, ui-monospace, monospace"
    fontSize: "12px"
    fontWeight: 500
    letterSpacing: "0.14em"
  handwriting:
    fontFamily: "Reenie Beanie, cursive"
    fontSize: "24px"
    fontWeight: 400
    lineHeight: 1
rounded:
  paper: "2px"
  sm: "6px"
  video: "12px"
  card: "14px"
  plate: "20px"
  pill: "999px"
spacing:
  xs: "6px"
  sm: "12px"
  md: "16px"
  lg: "24px"
  xl: "40px"
  section: "88px"
components:
  button:
    textColor: "{colors.night-fg}"
    rounded: "{rounded.pill}"
    padding: "12px 22px"
  button-solid:
    backgroundColor: "{colors.night-fg}"
    textColor: "{colors.night}"
    rounded: "{rounded.pill}"
    padding: "12px 22px"
  tab:
    textColor: "{colors.night-fg}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "9px 16px"
  card-ab:
    backgroundColor: "{colors.panel}"
    rounded: "{rounded.card}"
    padding: "14px 16px"
  card-measurement:
    backgroundColor: "{colors.night}"
    textColor: "{colors.night-fg}"
    rounded: "{rounded.card}"
  polaroid:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.handwriting}"
    rounded: "{rounded.paper}"
    padding: "12px 12px 0"
---

# Design System: Audio Citra

## Overview

**Creative North Star: "Studio after dark"**

A control room at night. The page is lacquered black, the gear is lit, and a film grade sits over the whole thing: warm lifted blacks, grain, a faint projector flicker, halation on the highlights. Each plug-in owns one colour, and its page wears it.

The renders of the plug-ins as rack gear do the selling. Type and interface stay out of their way: words sit beside the pictures, never on top of them. Personal touches come in on paper. Polaroids, handwritten captions and taped notes make it clear that one person built this.

**Key Characteristics:**
- Dark by default. The only light page is Shunya, which flips to a pale room.
- One accent per plug-in, set per page through `--accent`.
- A film grade over the stage: grain, flicker, halo, vignette, dust.
- Paper and ink for anything personal: polaroids, notes, handwritten captions.
- Pills for actions, soft cards for data, square-ish paper for keepsakes.

## Colors

A near-black lacquer with cool grey text. Saturated colour appears only as the current plug-in's accent.

### Primary
Each product page sets `--accent` to its plug-in's colour, and the home rooms set `--c` per room.
- **Spanda Violet** (spanda): channel strip.
- **Gālana Amber** (galana): effects box.
- **Ākāśa Rose** (akasa): coloured reverb.
- **Shunya Deep Teal** (shunya), with **Shunya Light Teal** (shunya-lt) where it sits on dark: transparent reverb.
- **Agni Ember** (agni): distortion.
- **Lahari Mint** (lahari).
- **Tulā Brass** (tula): mix utility.

### Neutral
- **Night** (night): page background. Also the fixed dark for measurement cards that must stay dark on the pale page.
- **Panel** (panel): raised surfaces, A/B cards, hover rows.
- **Line** (line): every hairline border and section rule.
- **Night Text** (night-fg): body text and solid button fill.
- **Night Mute** (night-mute): secondary text, captions, nav links at rest.
- **On Accent** (on-accent): text on an accent fill.
- **Pale Room** (pale, pale-fg, pale-mute): Shunya's light page only.

### Tertiary: paper and film
- **Polaroid Paper** (paper): polaroid cards, photo plates, speech bubbles, lightbox frames.
- **Handwriting Ink** (ink): handwritten captions on paper.
- **Projector Warm** (film-warm): the film flicker light.

### Named Rules
**The One Accent Rule.** A page wears one plug-in's colour. Don't mix two plug-in accents on one page except in navigation strips that list all of them.

**The Night Stays Night Rule.** Elements that must stay dark on the pale page use the `--night*` tokens, never `--bg`/`--fg`, which flip there.

## Typography

**Display Font:** Bodoni Moda (with Georgia)
**Body Font:** IBM Plex Sans (with system-ui)
**Label/Mono Font:** IBM Plex Mono (with ui-monospace)
**Notes:** Reenie Beanie, for handwriting on paper only

**Character:** a high-contrast fashion serif for the big claims, against a plain engineering sans and a mono for anything measured or labelled. Mixing desk on one side, magazine cover on the other.

### Hierarchy
- **Display** (800, clamp(40px–92px), 0.98): page heroes. Home rooms run larger, up to 120px.
- **Headline** (800, clamp(32px–60px), 1.02): section heads.
- **Title** (600, 18px, Plex Sans): feature titles.
- **Body** (400, 16px, 1.55): running text. The lede is 18px and muted, max about 58ch.
- **Label** (500, 12px, mono, 0.14em, uppercase): small kicker labels above headings, captions, specs and tab labels.
- **Handwriting** (24–32px Reenie Beanie): polaroid and plate captions, only on paper.

### Named Rules
**The Measured Mono Rule.** Numbers, specs, timings and units are set in IBM Plex Mono with tabular figures.

## Layout

A 1200px column with a 16px minimum gutter. Sections are separated by an 88px vertical rhythm and a single hairline rule. The home page is a sideways carousel of rooms, one plug-in per screen. On desktop the picture sits on the right 62% and fades in from black, with words in their own column on the left. Between 701px and 1099px it's a 50/50 split. On phones the picture sits above the words, with dots replacing the room names.

Main breakpoint: 700px (phone). Secondary: 820px and 1100px.

**The Words Beside Gear Rule.** Text never sits on top of a product render. Give it its own column or put it below.

## Elevation & Depth

Depth comes from light and grade, not stacked cards. Surfaces are mostly flat on black, separated by hairlines. Shadows are long and soft, used only for things that sit "in the room" (photo plates, polaroids, lightbox frames) and as the coloured glow under play buttons. The film overlay adds the atmosphere: lifted warm blacks, grain, vignette and occasional light rays.

### Shadow Vocabulary
- **Plate drop** (`box-shadow: 0 40px 80px -30px #000c`): screenshot plates.
- **Paper drop** (`box-shadow: 0 14px 28px -10px #000c, 0 2px 4px #0006`): polaroids and paper.
- **Accent glow** (`box-shadow: 0 8px 32px -6px var(--accent)`): the walkthrough play button.

### Named Rules
**The Film Grade Rule.** The film grade (grain, flicker, halation, vignette, dust) is part of the identity. Keep it, and keep its reduced-motion fallback: grade and grain stay, still; dust, flicker and rays go.

## Shapes

Three families. Pills (999px) for every action and toggle. Soft cards (12–20px) for data, video and screenshots. Near-square paper (1–2px) with a small tilt for keepsakes. Circles for play buttons and carousel arrows.

## Components

### Buttons
- **Shape:** pill (999px).
- **Default:** transparent with a hairline border, 12px × 22px, Plex Sans 600 15px.
- **Solid:** Night Text fill with Night text. In the home rooms the solid button takes the room's colour.
- **Hover / Focus:** a slight brightness lift. Focus is a 2px accent outline offset 2px.

### Chips (tabs and segmented toggles)
- **Style:** mono 13px pills with a hairline border.
- **State:** the selected one fills with the accent and switches to On Accent text.

### Cards / Containers
- **A/B card:** Panel fill, hairline, 14px radius, round accent play button. Plays a plug-in's dry and wet clips.
- **Measurement card:** always Night, hairline, 14px radius, mono caption.
- **Plate:** 20px radius on black with the plate drop shadow.

### Navigation
Sticky, 56px (48px on phones), Night at 85% with a 12px backdrop blur and a bottom hairline. The lotus logo sits on the left. Links are Night Mute at 14px and turn Night Text on hover or when current. On phones the link row scrolls sideways with a right-edge fade.

### Signature: Rooms carousel
The home page stepper. One room per plug-in, a peek of the next room on the right, arrows, a position counter (`00 / 07`) and a named progress strip.

### Signature: Polaroids and notes
Gallery cards and photo plates on Polaroid Paper, tilted a degree or two, with captions in Reenie Beanie and Handwriting Ink. Notes carry a strip of tape.

## Do's and Don'ts

### Do:
- **Do** keep pages dark on `--night`. Shunya's pale room is the only light page.
- **Do** give each product page exactly one accent, through `--accent`.
- **Do** keep the film grade and the paper vocabulary (polaroids, handwriting, tape). The owner made both binding.
- **Do** set numbers and specs in IBM Plex Mono.
- **Do** keep words beside the gear renders, never on top of them.

### Don't:
- **Don't** add a light theme or light sections outside Shunya. The owner's decision.
- **Don't** redraw, recolour or replace the lotus logo. A dark backing is the only allowed treatment.
- **Don't** use Reenie Beanie anywhere except on paper.

### Open to change
The owner didn't mark these as binding, so later work may revisit them with a reason: the italic word in Bodoni headings, the uppercase mono kicker labels above headings, and the coloured glows.
