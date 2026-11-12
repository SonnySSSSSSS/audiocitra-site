# Default-design catalog: what reads as "vibe-coded"

Started 2026-11-12. These are design-writer opinions and patterns gathered from many generated sites, not measured research. A tell is a *default*, something a model or template reaches for when nobody decided. One tell alone is fine. A pile of them reads as unowned.

The rule for this site is that every visual choice must have a reason tied to Audio Citra: studio, gear, plug-ins, or the owner's voice. "It looked modern" is not a reason. And swapping one default for the next default (for example cream background + serif + sage, which is already being called the 2026 tell) doesn't count as fixing it.

## Catalog

| # | Tell | Why models do it | Our site today |
|---|---|---|---|
| T1 | **Default fonts:** Inter, Geist, Space Grotesk, Poppins, Syne, Instrument Sans, JetBrains Mono for labels | Top picks in templates and Google Fonts "trending" | **Yes.** Syne + Instrument Sans + JetBrains Mono is a textbook generated stack |
| T2 | **Purple, violet or lavender accent on near-black** | The most common "tech dark mode" in training data | **Yes.** `--spanda:#c58bff` on `#0c0b10`, and it is the site's default accent |
| T3 | **Two-tone headline:** "Plain words, *coloured words.*" | A landing-page template pattern | **Yes,** on every section head (`.head h2 em`) |
| T4 | **Eyebrow labels:** small spaced uppercase mono above each heading | Template habit | **Yes,** on 18 pages |
| T5 | **Everything in a rounded card** with a 1px border | Component-library default | **Partly.** `.credits`, bays, panels; 34 border-radius rules |
| T6 | **Pill buttons** (radius 999px), a solid one and a ghost one | shadcn and Tailwind default | **Yes** |
| T7 | **Sticky blurred glass nav** | Default in Vercel-style templates | **Yes** (`backdrop-filter:blur(12px)`) |
| T8 | **Three-column feature grid:** icon or title + two lines | The "features" section template | **Yes.** `.feats`, and I just added one to About |
| T9 | **Gradient or glow hero,** aurora backgrounds, particles | Visual filler | No glow. Uses real 3D renders (good) |
| T10 | **Emoji or line icons as decoration** (Lucide, Heroicons) | Easy visual punctuation | No |
| T11 | **Bento grids** of mixed-size cards | 2024–26 trend | Not really |
| T12 | **Fade-up on scroll,** everything animates in | Library default | No |
| T13 | **Decorative status dots and badges** ("New", "Coming soon" chips) | Filler meaning | **Some** (`soon-tag`, `draft-tag`) |
| T14 | **Centered hero + two buttons + one-line promise** | Template order | Partly (left-aligned, three buttons) |
| T15 | **Copy tells:** "Built for…", "Unlock…", "Seamless", rule-of-three slogans | Marketing training data | Mostly avoided, because the voice is the owner's |
| T16 | **Text wordmark in a display font** instead of a real mark | No asset supplied | **Yes.** Nav shows "AUDIO CITRA" in Syne, not the lotus |
| T17 | **Generic dark theme:** gray-purple panels, every surface one step lighter | Default dark-mode ramps | **Yes** (`--panel #16141d`, `--line #2a2733`) |
| T18 | **Even rhythm everywhere:** same padding, same section shape, no surprises | Templates repeat one section | **Yes.** Every section is head → body at 88px |

## What is already ours (keep and build on)

- **Real 3D renders of the plug-ins as rack gear.** No template has these.
- **The museum idea:** "this is my little museum", exhibit placards, "Build 1,605. Yes, I count them." That's a real concept, and the strongest unique thing on the site.
- **Per-product colours** set by each plug-in's own UI, not by a theme.
- **Measurements and plots made from the actual plug-in,** level-matched audio.
- **The owner's voice.**
- **The lotus logo** exists, but the site doesn't use it.

## How to move away (principles, not a design)

1. **Start from one concrete reference, not "modern".** Pick something real: a museum's exhibit labels, a gear manual, a studio track sheet, a rack front panel, a record sleeve. Every write-up agrees that a concrete reference is what breaks the default.
2. **Choose fonts for a reason.** For example, a typeface with a studio, engraving, museum or Indian-print history. Avoid anything on the T1 list.
3. **The colour comes from the products,** not violet-on-black. The dark base could become a real material colour (lacquer, anodised panel, warm black) instead of gray-purple.
4. **Fewer boxes.** Use rules, columns and labels like printed material, not cards.
5. **Vary the rhythm.** Some sections full-bleed images, some narrow text, some a placard.
6. **Use the lotus.**
7. **Re-check with this table after every change.** Any new "Yes" needs a written reason.

## Sources (opinion pieces, used as a pattern list)

- Fountain Institute, "7 Signs a UI Has Been Vibe Coded": https://www.thefountaininstitute.com/blog/signs-vibe-coded-ui
- MindStudio, "Avoid vibe-coded landing pages": https://www.mindstudio.ai/blog/avoid-vibecoded-landing-pages
- CodeMySpec, "Vibe-coded websites look the same": https://codemyspec.com/blog/vibe-coded-websites-look-the-same
- Superdesign, "Why AI design looks generic": https://superdesign.dev/blog/why-ai-design-looks-generic
- AI Smells, "Bento Box Sprawl" and "Gradient Fog": https://aismells.pages.dev/bento-box-sprawl.html
- Built In, "AI Makes Bad Design Look Good Enough": https://builtin.com/articles/ai-design-slop-era
