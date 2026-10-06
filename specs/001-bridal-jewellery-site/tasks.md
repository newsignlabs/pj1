---

description: "Task list for the bridal jewellery showcase website"
---

# Tasks: Bridal Jewellery Showcase Website

**Input**: Design documents from `/specs/001-bridal-jewellery-site/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: No unit test suite was requested. Validation is the static audit
`tools/check_site.py` (constitution gate) plus manual responsive checks.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = Collections + WhatsApp, US2 = Home, US3 = Contact

---

## Phase 1: Setup

- [x] T001 Create folder structure (`assets/{css,js,icons,img}`, `images-src/`, `tools/`) per plan.md
- [x] T002 [P] Add `.gitignore`, `robots.txt` and `_headers` (cache + security headers) at repository root
- [x] T003 [P] Add `README.md` with project overview, local preview, image workflow and WhatsApp number replacement

---

## Phase 2: Foundational (blocks all stories)

- [x] T004 Write `tools/generate_placeholders.py` producing placeholder originals for hero, collections, pieces and about in `images-src/`
- [x] T005 Write `tools/optimize_images.py` converting `images-src/**` to multi-width compressed WebP in `assets/img/**` per `contracts/image-pipeline.md` (crop, resize, quality fallback, budget report)
- [x] T006 Run the placeholder generator and the optimiser; commit generated WebP variants
- [x] T007 [P] Create favicon (replaced by logo-based icons in T027) and an inline `<symbol>` icon sprite (whatsapp, phone, mail, pin, clock, menu, close) in each page
- [x] T008 Create `assets/css/styles.css`: design tokens, mobile-first base, header/nav, footer, floating WhatsApp button, buttons, grids, focus styles; no transitions/animations
- [x] T009 [P] Create `assets/js/main.js`: `no-js` → `js` handling, nav toggle with `aria-expanded`, current year
- [x] T010 Write `tools/check_site.py` audit (WebP-only images, lazy/decoding attributes, width/height/alt, local link and asset existence, single WhatsApp number, no motion CSS/markup, size budgets)

**Checkpoint**: Shared layout, images and tooling ready.

---

## Phase 3: User Story 1 — Browse collections & enquire on WhatsApp (P1) 🎯 MVP

**Goal**: Collections page with six categories and piece cards; WhatsApp via the floating button and one call to action.

**Independent Test**: Tap the WhatsApp button → WhatsApp opens a chat with the business.

- [x] T011 [US1] Build `collections.html` shell (header, page intro, category jump links, footer, floating WhatsApp button)
- [x] T012 [US1] Add six collection sections with 4 piece cards each (lazy WebP `srcset`, dimensions, alt text) in `collections.html`
- [x] T013 [US1] ~~Add per-piece `wa.me` links~~ (removed in revision 2, see T030)
- [x] T014 [US1] Style category navigation and responsive piece grid (2 → 3 → 4 columns) in `assets/css/styles.css`

**Checkpoint**: MVP — browsing and enquiry works on its own.

---

## Phase 4: User Story 2 — Home page first impression (P2)

**Goal**: Static full-screen hero and sections routing to Collections and WhatsApp.

**Independent Test**: Hero fills one screen height on phone and desktop; nothing moves; CTAs work.

- [x] T015 [US2] Build `index.html` hero with art-directed `<picture>`, `fetchpriority="high"`
- [x] T016 [US2] Add featured collections grid linking to `collections.html#<slug>` in `index.html`
- [x] T017 [US2] Add about section (lazy image), highlights and closing WhatsApp CTA in `index.html`
- [x] T018 [US2] Style hero (`100vh`/`100svh`, overlaid header, legible overlay) and home sections in `assets/css/styles.css`

---

## Phase 5: User Story 3 — Contact (P3)

**Goal**: Contact details and a showroom map.

**Independent Test**: Map shows the showroom; phone, email, WhatsApp and directions links work.

- [x] T019 [US3] Build `contact.html` with contact details (tel:, mailto:, address, hours)
- [x] T020 [US3] ~~Implement form → WhatsApp message~~ (removed in revision 2, see T029)
- [x] T021 [US3] Style contact layout in `assets/css/styles.css`

---

## Phase 6: Polish & Cross-Cutting

- [x] T022 [P] Add `404.html`
- [x] T023 Run `python3 tools/check_site.py` and fix all findings
- [x] T024 Manual responsive check at 320/360/768/1280px (no horizontal scroll, hero = one screen)
- [ ] T025 Replace placeholder brand name, copy, contact details, WhatsApp number and photography with the business's real content (needs client input)
- [ ] T026 Run Lighthouse mobile audit on the deployed site and record scores (needs hosting)

---

## Phase 7: Revision 2 — client feedback

- [x] T027 Add supplied logo as `images-src/brand/logo.png`; write `tools/build_brand_assets.py` (black → transparent, logo WebP sizes, favicons)
- [x] T028 Restyle `assets/css/styles.css` to dark background with silver + pink brand palette; recolour placeholders in `tools/generate_placeholders.py`
- [x] T029 Remove the contact form from `contact.html` and its JS from `assets/js/main.js`
- [x] T030 Remove per-piece WhatsApp buttons from `collections.html`; hero/home CTAs point to Collections and Contact
- [x] T031 Add lazy-loaded Google Maps embed and "Open in Google Maps" link to `contact.html`
- [x] T032 Update `tools/check_site.py` (header logo eager, map iframe rules), constitution v1.1.0, spec and docs
- [ ] T033 Replace the placeholder address so the map points at the real showroom (needs client input)

---

## Phase 8: Revision 3 — art direction

- [x] T035 Remove the GitHub Pages workflow (site is hosted on Catalyst Slate, auto-deployed from `main`)
- [x] T036 Add the client's product photo as `images-src/hero/hero-photo.jpg`; write `tools/grade_hero.py` (cinematic grade) and switch the hero pipeline to `hero-cinematic-{540,810,1080}.webp`
- [x] T037 Self-host Cormorant Garamond in `assets/fonts/` (with OFL licence) and preload it
- [x] T038 Rewrite `assets/css/styles.css`: cinematic letterboxed hero (glow, grain, vignette), clipped-edge cards, outlined numerals, staggered grids, editorial type
- [x] T039 Rebuild `index.html`, `collections.html`, `contact.html`, `404.html` with chapter-style sections and clipped cards
- [x] T040 Add font budget to `tools/check_site.py`; update constitution v1.2.0, spec, plan, research, contracts and README

---

## Phase 9: Revision 4 — mobile richness

- [x] T041 Extend `tools/grade_hero.py` to cut two close-up scenes and three soft-focus quote backgrounds; add `hero-detail` and `quotes` rules to `tools/optimize_images.py`
- [x] T042 Hero becomes a manual scroll-snap slider (3 scenes) with arrows, counter, keyboard and swipe in `index.html`, `assets/css/styles.css`, `assets/js/main.js`
- [x] T043 Add parallax quote interludes (3 on Home, 1 on Collections, 1 on Contact) with CSS scroll-driven animation, JS fallback and reduced-motion opt-out
- [x] T044 Header: logo medallion hanging below the bar on phones, call button, display-serif mobile menu
- [x] T045 Footer: end credits with ringed logo emblem, credit rows, scene links, "Fin." and outlined wordmark
- [x] T046 `tools/check_site.py`: allow only the marked parallax block, ban timers/autoplay in JS (comments ignored), CSS budget 35 KB; constitution 2.0.0 and docs updated

---

## Phase 10: Revision 5 — menu, cards, light theme

- [x] T047 Tokenise colours; add `:root[data-theme="light"]` ivory palette; keep `.hero` and `.quote` dark
- [x] T048 Theme switch in the top bar (`role="switch"`, remembered, no flash via inline head script, updates theme-color)
- [x] T049 Full-screen phone menu with embroidered frame, numbered scenes, contact line, focus trap, scroll lock
- [x] T050 Embroidered border and lattice SVGs (`assets/icons/embroidery-*.svg`, `jaali-*.svg`)
- [x] T051 Convert three quotes to full-screen embroidered cards (Home II, Collections, Contact); two parallax quotes remain on Home
- [x] T052 CSS budget 40 KB; constitution 2.1.0, spec revision 5, plan, research, README updated

---

## Dependencies & Execution Order

- Setup (T001–T003) → Foundational (T004–T010) → US1, US2, US3 (independent of each other) → Polish.
- T005 depends on T004 for placeholder sources; T006 depends on T004–T005.
- T023 depends on all page tasks.
