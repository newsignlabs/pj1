# Implementation Plan: Bridal Jewellery Showcase Website

**Branch**: `001-bridal-jewellery-site` | **Date**: 2026-10-06 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-bridal-jewellery-site/spec.md`

## Summary

A three-page static brochure site (Home, Collections, Contact) for a bridal jewellery
business, written in plain HTML5, one CSS file and one small vanilla JS file. Visitors
convert through WhatsApp click-to-chat links (`https://wa.me/<number>?text=<message>`),
which are pre-filled per piece and composed from the Contact form. All imagery is served as
compressed, multi-width WebP with native lazy loading and reserved dimensions; a Python
(Pillow) script turns original photos into the required WebP variants. The Home hero is a
single static `<picture>` filling `100svh`. No animation of any kind.

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
| I. Static & Framework-Free | ✅ | Plain HTML/CSS/JS; no deps; JS only enhances (menu toggle, form → WhatsApp); every link works without JS; system font stacks, no web fonts/CDNs |
| II. Image Performance First | ✅ | WebP only; `loading="lazy"` + `decoding="async"` on all non-hero images; hero `loading="eager"` (default) + `fetchpriority="high"`; `width`/`height` on every `<img>`; `srcset`/`sizes`; `tools/optimize_images.py` enforces quality and size budgets |
| III. Calm, Motion-Free | ✅ | No `animation`, `transition`, `@keyframes`, carousels or video; `scroll-behavior: auto`; static `100svh` hero; enforced by `check_site.py` |
| IV. Mobile-First Responsive | ✅ | Mobile-first CSS with `min-width` breakpoints at 640/960/1200px; 44px touch targets; collapsible nav |
| V. WhatsApp Conversion | ✅ | Header/hero/footer/floating WhatsApp links on every page; per-piece pre-filled messages; single number replaced site-wide (see quickstart) |
| VI. Accessible & Semantic | ✅ | Landmarks, skip link, alt text, visible focus, AA contrast palette, labelled form fields |

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
├── js/main.js           # Menu toggle + contact form → WhatsApp
├── icons/favicon.svg    # (UI icons are an inline <symbol> sprite in each page: no extra request, works from file://)
└── img/                 # GENERATED WebP variants (do not edit by hand)
    ├── hero/            # hero-landscape-{1280,1920,2560}.webp, hero-portrait-{480,720,1080}.webp
    ├── collections/     # <slug>-{400,600,800}.webp (cover images)
    ├── pieces/          # <slug>-{400,600,800}.webp
    └── about/           # about-{600,900,1200}.webp
images-src/              # Original photos (JPG/PNG), same folder layout as assets/img
tools/
├── generate_placeholders.py   # Creates placeholder originals in images-src/
├── optimize_images.py         # images-src/ → assets/img/*.webp (multi-width, compressed)
└── check_site.py              # Static audit against the constitution
```

**Structure Decision**: Flat static site at repository root so it can be deployed by any
static host (including GitHub Pages from the branch root) without configuration. Generated
images live under `assets/img/` and are committed so no build step is needed at deploy time.

## Complexity Tracking

No violations.
