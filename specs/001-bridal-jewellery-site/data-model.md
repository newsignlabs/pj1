# Data Model: Bridal Jewellery Showcase Website

The site has no database; these entities describe the content embedded in the HTML and
the image files on disk.

## Collection

| Field | Example | Rules |
|-------|---------|-------|
| `slug` | `necklaces` | Lowercase, hyphenated; used as section `id` on `collections.html` and as image file name |
| `name` | `Necklaces` | Shown as section heading and in WhatsApp messages |
| `description` | `Statement chokers, rani haars and layered pieces…` | 1–2 sentences |
| `cover` | `assets/img/collections/necklaces-{400,600,800}.webp` | 4:5 aspect |

Collections (in display order): `bridal-sets`, `necklaces`, `earrings`, `bangles`,
`maang-tikka`, `rings`.

## Piece

| Field | Example | Rules |
|-------|---------|-------|
| `slug` | `kundan-choker` | Unique; image file name |
| `name` | `Kundan Choker` | Shown on card and in WhatsApp message |
| `description` | `22k gold choker with uncut kundan stones…` | ≤ 120 characters |
| `collection` | `necklaces` | Must match a Collection slug |
| `image` | `assets/img/pieces/kundan-choker-{400,600,800}.webp` | 4:5 aspect |

Relationship: Collection 1 — N Piece (min 4 per collection).

## Image variant

| Field | Rules |
|-------|-------|
| Source | `images-src/<group>/<slug>.(jpg|jpeg|png|webp)` |
| Output | `assets/img/<group>/<slug>-<width>.webp` |
| Widths | By group (see `contracts/image-pipeline.md`) |
| Budget | ≤ 120 KB per variant (hero ≤ 250 KB) |

## Greeting message

| Where | Template |
|-------|----------|
| Floating button, header, footer, Contact page | `Hello! I'd like to know more about your bridal jewellery collections.` |
| Collections page call to action | `Hello! I'd like to ask about a piece from your bridal collections.` |

## Business contact details

- WhatsApp and phone: `+91 97901 12593` (`919790112593` in `wa.me` and `tel:` links)
- Shop: 2390 Adhithya complex, Kanjappalli pirivu, Avinashi road, Annur, Coimbatore - 641653
  (also the Google Maps query on the Contact page)
- Tagline: "Bridal Collections" (brand shown as "Cute Look Bridal Collections")
- Still placeholders: email `hello@cutelookbridal.example` (shown on the Contact page;
  commented out in the footer) and opening hours.
