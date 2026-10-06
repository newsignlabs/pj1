# Implementation Plan: Bridal Jewellery Showcase Website

**Branch**: `001-bridal-jewellery-site` | **Date**: 2026-10-06 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-bridal-jewellery-site/spec.md`

## Summary

A three-page static brochure site (Home, Collections, Contact) for a bridal jewellery
business, written in plain HTML5, one CSS file and one small vanilla JS file, in a dark
theme using the logo's silver and pink. Visitors convert through WhatsApp click-to-chat
links (`https://wa.me/<number>?text=<message>`): a floating button on every page plus a
few clear entry points. The Contact page shows details and a lazy-loaded Google Maps
embed; there is no contact form. All imagery is served as
compressed, multi-width WebP with native lazy loading and reserved dimensions; a Python
(Pillow) script turns original photos into the required WebP variants. The Home hero is a
single static `<picture>` filling `100svh`. No animation of any kind.

Revision 3 (art direction): the hero is the client's product photo, colour-graded offline by
`tools/grade_hero.py` and framed as a letterboxed film still (CSS letterbox bars, blurred
ambient glow of the same frame, static SVG grain, vignette). Typography uses self-hosted
Cormorant Garamond (~47 KB WOFF2). Cards use `clip-path` chamfers with a 1px gradient edge.
Hosting: Zoho Catalyst Slate (static framework) auto-deploys `main`.

Revision 4 (mobile richness): the hero becomes a CSS scroll-snap slider of three scenes
(full set, earrings close-up, pendant close-up — all cut from the product photo by
`tools/grade_hero.py`), with JS arrows/counter that jump instantly. Quote interludes use
soft-focus close-ups with CSS scroll-driven parallax (`animation-timeline: view()`), a
passive scroll-listener fallback, and no motion under `prefers-reduced-motion`. The header
logo becomes a hanging medallion on phones; the footer becomes "end credits" with a large
emblem ringed by SVG text. Constitution 2.0.0 permits exactly these two kinds of motion.

## Technical Context

**Language/Version**: HTML5, CSS3 (custom properties, grid, `svh` units), ES2017 vanilla JavaScript; Python 3.10+ for offline image tooling only

**Primary Dependencies**: None at runtime. Tooling: Pillow ≥ 10 (WebP encoder) for image optimisation

**Storage**: N/A (static files; no visitor data stored)

**Testing**: `tools/check_site.py` static audit (images, lazy-loading, links, budgets, no-motion rules) + manual responsive checks + Lighthouse

**Target Platform**: Modern evergreen browsers (Chrome/Edge/Firefox/Safari, iOS Safari 14+, Android Chrome); any static host

**Project Type**: Static website (frontend only)

**Performance Goals**: Lighthouse mobile ≥ 90; LCP ≤ 2.5 s on 4G; CLS < 0.1

**Constraints**: No frameworks, no build step to serve, no third-party runtime requests, no animation/transition, JS ≤ 10 KB, CSS ≤ 25 KB, image variants ≤ 120 KB (hero ≤ 250 KB)

**Scale/Scope**: 3 pages, 6 collections, 24 pieces (≈35 source images, ≈110 WebP variants)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | How the design complies |
|-----------|--------|-------------------------|
| I. Static & Framework-Free | ✅ | Plain HTML/CSS/JS; no deps; JS only enhances (menu toggle); every link works without JS; system font stacks, no web fonts/CDNs |
| II. Image Performance First | ✅ | WebP only; `loading="lazy"` + `decoding="async"` on all non-hero images; hero `loading="eager"` (default) + `fetchpriority="high"`; `width`/`height` on every `<img>`; `srcset`/`sizes`; `tools/optimize_images.py` enforces quality and size budgets |
| III. Calm, Motion-Free | ✅ | No `animation`, `transition`, `@keyframes`, carousels or video; `scroll-behavior: auto`; static `100svh` hero; enforced by `check_site.py` |
| IV. Mobile-First Responsive | ✅ | Mobile-first CSS with `min-width` breakpoints at 640/960/1200px; 44px touch targets; collapsible nav |
| V. WhatsApp Conversion | ✅ | Floating button, header and footer WhatsApp links on every page; no per-piece buttons; single number replaced site-wide (see quickstart) |
| VI. Accessible & Semantic | ✅ | Landmarks, skip link, alt text, visible focus, AA contrast palette (silver/pink on near-black), labelled fields |

**Post-design re-check (after Phase 1)**: ✅ No violations; Complexity Tracking empty.

## Project Structure

### Documentation (this feature)

```text
specs/001-bridal-jewellery-site/
├── plan.md              # This file
├── research.md          # Phase 0 decisions
├── data-model.md        # Content entities (collections, pieces, image variants)
├── quickstart.md        # Run, preview, replace images / number
├── contracts/
│   ├── whatsapp-links.md   # Click-to-chat URL & message contract
│   └── image-pipeline.md   # Source → WebP variant naming & markup contract
├── checklists/requirements.md
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
index.html               # Home
collections.html         # Collections
contact.html             # Contact
404.html                 # Not-found page
robots.txt
_headers                 # Cache/security headers (Netlify / Cloudflare Pages)
assets/
├── css/styles.css       # Single mobile-first stylesheet
├── fonts/             # Cormorant Garamond WOFF2 (self-hosted, OFL)
├── js/main.js           # Menu toggle, manual slider arrows, parallax fallback
├── icons/              # favicon-32.png, apple-touch-icon.png (UI icons are an inline <symbol> sprite in each page)
└── img/                 # GENERATED WebP variants (do not edit by hand)
    ├── hero/            # hero-cinematic-{540,810,1080}.webp, hero-detail-*-{450,600}.webp (slider scenes)
    ├── collections/     # <slug>-{400,600,800}.webp (cover images)
    ├── pieces/          # <slug>-{400,600,800}.webp
    ├── quotes/          # quote-*-{600,1200}.webp (soft-focus parallax backgrounds)
    ├── about/           # about-{600,900,1200}.webp
    └── brand/           # logo-{64,128,256}.webp (transparent)
images-src/              # Original photos (JPG/PNG), same folder layout as assets/img
tools/
├── build_brand_assets.py      # images-src/brand/logo.png → transparent logo WebP + favicons
├── grade_hero.py              # images-src/hero/hero-photo.jpg → hero-cinematic.jpg (cinematic grade)
├── generate_placeholders.py   # Creates placeholder originals in images-src/
├── optimize_images.py         # images-src/ → assets/img/*.webp (multi-width, compressed)
└── check_site.py              # Static audit against the constitution
```

**Structure Decision**: Flat static site at repository root so it can be deployed by any
static host (including GitHub Pages from the branch root) without configuration. Generated
images live under `assets/img/` and are committed so no build step is needed at deploy time.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Third-party Google Maps iframe on Contact page | Client asked for a map of the showroom | A static map image needs an API key or manual screenshots and is not interactive; the iframe is lazy loaded so it costs nothing until the visitor scrolls to it |
