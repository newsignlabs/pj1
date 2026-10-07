<!--
Sync Impact Report
- Version change: 2.1.0 → 2.1.1 (PATCH: wording)
- Brand & Visual Identity: the hanging logo medallion now applies on every screen size
- Templates requiring updates: none ✅
-->

# Bridal Jewellery Website Constitution

## Core Principles

### I. Static & Framework-Free (NON-NEGOTIABLE)

The site is a frontend-only static website built from hand-written HTML, CSS and
minimal vanilla JavaScript.

- No UI frameworks or libraries (React, Vue, Angular, jQuery, Bootstrap, Tailwind, etc.).
- No server-side runtime, database, or build step required to serve the site; every
  page MUST be deployable by copying files to any static host.
- JavaScript is progressive enhancement only. All content, navigation and WhatsApp
  links MUST work with JavaScript disabled.
- Web fonts MUST be self-hosted (WOFF2, openly licensed, `font-display: swap`).
- Third-party runtime requests (web fonts, analytics, CDNs, embeds) are not allowed
  unless justified in the plan's Complexity Tracking table. The only approved exception
  is the Google Maps embed on the Contact page, which MUST be lazy loaded.

**Rationale**: A small business brochure site gains nothing from a framework but pays
for it in load time, maintenance and hosting cost.

### II. Image Performance First (NON-NEGOTIABLE)

The site is image-heavy, so image delivery decides how fast it feels.

- Every content image MUST be served as compressed WebP.
- Every image below the first screen MUST use native lazy loading
  (`loading="lazy"`) and asynchronous decoding.
- The hero image is the only exception: it MUST load eagerly with high fetch priority.
- Every image MUST declare intrinsic `width` and `height` (or an aspect ratio) so the
  layout does not shift while images load.
- Images MUST be offered at multiple widths (`srcset`/`sizes`) so phones never
  download desktop-sized files.
- Source images are never served directly; they pass through the repository's
  optimisation script, which enforces size and quality limits.

**Rationale**: Bridal clients browse on phones, often on mobile data. Fast, light images
are the single biggest factor in whether they keep browsing.

### III. Calm, Visitor-Driven Motion (NON-NEGOTIABLE)

- Nothing moves on its own: no autoplay, auto-advancing carousels, marquees, looping or
  entrance animations, hover transitions, video or timers.
- The home hero MAY be a slider of still "scenes" that changes only when the visitor swipes
  or presses an arrow, and the change is instant (no slide animation).
- Quote interludes MAY use parallax on their background image, tied directly to the
  visitor's scrolling (CSS scroll-driven animation, with a small scroll-listener fallback),
  and MUST be disabled for `prefers-reduced-motion: reduce`. This is the only motion
  allowed, and it lives between the `motion-allowed` markers in the stylesheet.
- A "cinematic" look is achieved with still means: colour grading, letterbox bars,
  vignette, static grain and glow.

**Rationale**: The jewellery is the focus. Visitor-driven effects add richness on phones;
autonomous motion distracts, costs performance and can cause discomfort.

### IV. Mobile-First Responsive

- Styles are written mobile-first and scale up with `min-width` media queries.
- Layouts MUST work from 320px wide up to large desktop with no horizontal scrolling.
- Touch targets are at least 44×44 CSS pixels.
- Navigation MUST stay usable on small screens.

### V. WhatsApp as the Conversion Channel

- WhatsApp is the primary way visitors contact the business. A WhatsApp link MUST be
  reachable from every page (the floating button), without cluttering the design: no
  per-item WhatsApp buttons; a page has at most one in-content WhatsApp call to action.
- There is no contact form; visitors message the business directly.
- All WhatsApp links use one business number written as a single placeholder string,
  so it can be changed site-wide with one find-and-replace (documented in the README).
- No visitor data is collected or stored by the website itself.

### VI. Accessible & Semantic

- Semantic HTML landmarks (`header`, `nav`, `main`, `footer`) and a logical heading order.
- All meaningful images have descriptive `alt` text; decorative images use `alt=""`.
- Text contrast meets WCAG 2.1 AA; keyboard focus is always visible.
- A skip-to-content link is provided on every page.

## Brand & Visual Identity

- The supplied logo (`images-src/brand/logo.png`) is used as the favicon, as a large round
  medallion that hangs below the header bar on every screen size, and as a large emblem (inside a
  ring of text) in the footer.
- Dark is the default theme. A light (ivory) theme is available from a switch in the top
  bar and is remembered on the device. The hero and photographic quote sections stay dark
  in both themes, like a cinema screen. The logo's silver and pink are the only accent
  colours (WhatsApp green is allowed on WhatsApp buttons only).
- Art direction is artistic and editorial, not corporate: a large display serif
  (Cormorant Garamond), italic pink accents, outlined numerals, asymmetric/staggered
  layouts, generous space.
- Content cards (collections, pieces, highlights, contact, map) use clipped (chamfered)
  corners with a thin silver-to-pink edge.
- The footer is styled as a film's end credits, never as a corporate link grid.
- On phones the menu is a full-screen "programme" framed by an embroidered border, never a
  plain drop-down list.
- Quote interludes alternate between parallax photo quotes and full-screen cards with an
  embroidered border (running stitch, beaded row, diamond knots, corner rosettes).

## Performance Budgets

| Metric | Budget |
|--------|--------|
| HTML per page (uncompressed) | ≤ 40 KB |
| Total CSS | ≤ 40 KB (≈ 8.5 KB compressed) |
| Total JavaScript | ≤ 10 KB |
| Self-hosted fonts | ≤ 60 KB |
| Hero image (largest variant) | ≤ 250 KB |
| Any product/collection image variant | ≤ 120 KB |
| Initial page weight on mobile (before scrolling) | ≤ 500 KB |
| Lighthouse Performance (mobile) | ≥ 90 |
| Cumulative Layout Shift | < 0.1 |

## Development Workflow & Quality Gates

1. Features are specified with Spec Kit (`/speckit-specify` → `/speckit-plan` →
   `/speckit-tasks` → `/speckit-implement`).
2. Every plan MUST pass the Constitution Check before implementation.
3. Before merging, the change MUST pass:
   - `python3 tools/check_site.py` (lazy-loading, WebP, dimensions, alt text,
     no-animation, broken local links and budget checks);
   - a manual check at 360px, 768px and 1280px widths.

## Governance

This constitution overrides other practices for this repository. Amendments require a
documented reason, an updated version number and a review of dependent templates.
Versioning follows semantic versioning: MAJOR for removed or redefined principles,
MINOR for new principles or sections, PATCH for wording clarifications.

**Version**: 2.1.1 | **Ratified**: 2026-10-06 | **Last Amended**: 2026-10-06
