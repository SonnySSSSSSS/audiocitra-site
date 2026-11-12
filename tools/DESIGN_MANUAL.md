# Audio Citra site design manual

Started 2026-11-12. Read it together with `DEFAULT_DESIGN_CATALOG.md`: the catalog says what to avoid, and this says what to do instead.

## Part 1: what good sites do

These lessons come from WebDesignerDepot's "40 Best New Websites, 2024" (https://webdesignerdepot.com/40-best-new-websites-2024/). They're taken from the article's own descriptions; I didn't open the 40 sites themselves.

**1. The concept comes from the subject, literally.**
The best entries turn their subject into the interface:
- **Accordion** is an agency whose homepage *is* an accordion menu.
- **855-How-To-Quit** is a quit-opioids helpline whose phone extensions use pill imprint codes, with speckled, pill-like backgrounds.
- **Insight**'s landing page is a photographer's contact sheet you inspect with a magnifier.
- **Pizzato**, a plumbing supplier, uses blue for water.

None of them asked "what looks modern?" They asked "what is this thing, physically?"
→ *For us: a museum of plug-ins. The site behaves like a visit.*

**2. Colour has a reason.**
- **Kozowood** uses gold, chocolate and taupe for timber.
- **Kahlua** uses a telenovela palette for its Mexican roots.
- **Nord Quantique** uses pink to make quantum computing approachable.

Unexpected is fine when it's explained. Default never is.
→ *For us: each room takes its colour from its plug-in. The building itself is neutral.*

**3. Type with a person in it.**
- **Oliver Jeffers** has a display font made from the artist's own handwriting.
- **Art-Toi** uses hand-drawn lettering.
- **Daylight** uses a gently flared typeface to say "gentle".

The type says who made the thing.
→ *For us: museum signage type for structure, and the owner's own hand somewhere (signature, handwritten exhibit notes).*

**4. Images lead, and the layout gets out of the way.**
**L'Enclume**, **207 Ouest**, **Base Habitation** and **Studio Size** all use generous space, few elements and one strong image per moment.
→ *Our 3D renders are the exhibits. Light them; don't box them.*

**5. Tell a story through the material.**
- **Anai Wood** follows the forest to the finished product.
- **Cargo Kite** turns technical data into a story.
- **I See My Light Shining** pairs oral histories with illustration.

→ *For us: each plug-in's room tells how it was made, from the measurement to the part to the sound. The analysis plots are the wall text.*

**6. Unusual navigation, still obvious.**
- **Acre** clicks through like a magazine.
- **Bolt** stacks cards as you scroll.
- **Scalvini Marmi** scrolls in more than one direction.

Each is praised *only* because it stays intuitive.
→ *A floor plan and room numbers, with ordinary links underneath.*

**7. Motion is restrained and meaningful.**
**Accordion** and **Intrepid** use small motion that serves the idea. No animation runs just to fill space.
→ *Light coming up on an exhibit is fine. Fade-up on every paragraph is not.*

**8. Be useful.**
- **Few and Far** gives away free tools.
- **Following Wildfire** builds a real map from real data.

→ *Our measurements, level-matched listening and parts builder are the useful part. Feature them; they're what no template site has.*

**9. A big site still feels like one place.**
Large sites are praised for staying coherent.
→ *One building and one sign system. Every room follows the same signage rules, even when its colour changes.*

## Part 2: the museum direction

Every piece below maps to something real on the site, so the theme isn't decoration.

| Museum piece | Site piece |
|---|---|
| Building, entrance hall | Home page: "my little museum" |
| Rooms / galleries, one per collection | One page per plug-in, in its own colour |
| Exhibit placard (object, date, medium, accession no.) | Already exists. Becomes the main sign system: name, kind, on display since, medium (C++ on JUCE), build no. |
| Wall text | Section intros, in the owner's voice |
| Object on a plinth under a spotlight | The 3D rack renders, on a lit, dark wall rather than in a card |
| Audio guide | The listen players ("press 3 for the dry/wet") |
| Conservation lab / research room | Measurements, plots, parts builder |
| Floor plan | Navigation: rooms numbered 01–07 |
| Curator's note, signed | The About page |
| Museum shop | Buy |
| Visitor information | Install, Contact, Refunds, Terms |
| "Coming soon" | "In conservation", "Opening 2027" |

### Rules

1. **Sign system first.** Design one placard, one wall-text block and one room sign. Everything else is built from those three. They replace eyebrows, two-tone headlines and cards.
2. **Type:** a museum-signage face for labels and room numbers, plus a readable text face for wall text. Pick from type with a real signage or print history. Nothing from catalog tell T1. Choose by setting a real placard in three candidates side by side.
3. **The building is quiet, the exhibits are loud.** The walls are one material colour, either warm gallery white or deep gallery wall (not gray-purple). Product colour appears only inside its room: placard rule, spotlight tint, links.
4. **Lighting, not boxes.** Exhibits sit on the wall with space and a soft spotlight falloff. No borders or rounded cards around them. Use thin rules like printed signage.
5. **Numbers are a feature.** Room numbers, accession numbers and build counts. The owner counts things, so the museum does too.
6. **Rhythm changes from room to room**, like walking through a building: a full-wall image, then a narrow text column, then a vitrine (grid of small objects), then a bench (a pause, a quote).
7. **The owner's hand:** a signed curator's note, and maybe handwritten annotations on one or two exhibits. Not everywhere.
8. **Logo:** the lotus at the entrance and in the nav, unchanged, per the logo rule.
9. **Don't make it a pastiche.** No marble textures, velvet ropes, gold frames or fake brass. The museum is in the *structure* (signs, rooms, lighting, placards), not in costume. Keep the 3D renders as the only "real objects".
10. **Check against the catalog before every merge.** Any tell left in needs a written reason.

### Process

1. Build a mock of one room (Spanda) and the entrance (home) only.
2. The owner reviews it before anything else is changed.
3. Roll out to the other rooms, then the visitor pages.

## Sources

- WebDesignerDepot, "40 Best New Websites, 2024": https://webdesignerdepot.com/40-best-new-websites-2024/
