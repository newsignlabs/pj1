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

## Enquiry message (transient — never stored)

| Source | Template |
|--------|----------|
| Piece | `Hello! I'm interested in the {piece name} from your {collection name} collection. Could you share more details?` |
| General | `Hello! I'd like to know more about your bridal jewellery collections.` |
| Contact form | `Hello, I'm {name}.` + optional `Wedding date: {date}` + optional `Phone: {phone}` + `{message}` (one item per line) |

## Business contact details

Placeholders, to be replaced before launch: WhatsApp `+91 98765 43210`
(`919876543210` in links), phone, email `hello@aureliabridal.example`, address,
opening hours.
