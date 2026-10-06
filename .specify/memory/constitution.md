<!--
Sync Impact Report
- Version change: 1.0.0 → 1.1.0
- Modified principles: I (one permitted third-party embed: lazy Google Maps iframe),
  V (WhatsApp kept to a few clear entry points; no per-item buttons)
- Added sections: Brand & Visual Identity
- Templates requiring updates: none ✅
- Follow-up TODOs: none
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

### III. Calm, Motion-Free Presentation (NON-NEGOTIABLE)

- No animations, transitions, carousels, sliders, marquees, parallax, auto-playing
  media or scroll-triggered effects.
- The home page hero banner is a single static image filling the viewport height.
- Interactive state changes (hover, focus, menu open) happen instantly.

**Rationale**: The jewellery is the focus. Motion distracts, costs performance and
can cause discomfort for motion-sensitive visitors.

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

- The supplied logo (`images-src/brand/logo.png`) is used in the header and footer and as
  the favicon.
- Dark background throughout, with the logo's silver and pink as the only accent colours
  (WhatsApp green is allowed on WhatsApp buttons only).

## Performance Budgets

| Metric | Budget |
|--------|--------|
| HTML per page (uncompressed) | ≤ 40 KB |
| Total CSS | ≤ 25 KB |
| Total JavaScript | ≤ 10 KB |
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

**Version**: 1.1.0 | **Ratified**: 2026-10-06 | **Last Amended**: 2026-10-06
