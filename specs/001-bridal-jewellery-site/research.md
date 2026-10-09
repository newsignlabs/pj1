# Research: Bridal Jewellery Showcase Website

## 1. WhatsApp integration

- **Decision**: WhatsApp click-to-chat links `https://wa.me/<countrycode+number>?text=<urlencoded>`.
- **Rationale**: Official, free, no API key or backend; opens the app on mobile and
  WhatsApp Web/Desktop on computers; works as a plain `<a href>` without JavaScript.
- **Alternatives considered**: WhatsApp Business Platform (Cloud API) — needs a backend,
  Meta app review and per-conversation pricing; third-party chat widgets — add heavy
  third-party scripts and often animate. Both rejected.

## 2. Lazy loading

- **Decision**: Native `loading="lazy"` with `decoding="async"` on all below-the-fold
  images; hero uses eager loading and `fetchpriority="high"`. No `<link rel="preload">`:
  the hero `<img>` is near the top of the HTML so the preload scanner finds it, and a
  preload for an art-directed `<picture>` risks downloading both variants.
- **Rationale**: Supported by all evergreen browsers (Chrome 77+, Firefox 75+, Safari 15.4+);
  zero JavaScript; browsers apply sensible look-ahead margins.
- **Alternatives considered**: IntersectionObserver + `data-src` — needs JS, breaks
  without it, and duplicates browser behaviour. Rejected.

## 3. Image format, compression and sizes

- **Decision**: WebP only, encoded with Pillow (`quality=72`, `method=6`, metadata stripped).
  Widths: pieces and collection covers 400/600/800 px at 4:5; about image 600/900/1200 px;
  hero landscape 1280/1920/2560 px at 16:9 and hero portrait 480/720/1080 px at 9:16 for
  phones (art direction via `<picture><source media>`).
- **Rationale**: WebP is 25–35% smaller than equivalent JPEG and supported by >97% of
  browsers. Card widths cover 2-column phone grids at 2–3× density up to 4-column desktop.
  Portrait hero avoids sending a wide image that phones would crop by 70%.
- **Alternatives considered**: AVIF (smaller, but slower encode and patchier Pillow
  support); `<picture>` with JPEG fallback (doubles files for <3% of users). Rejected
  for simplicity; AVIF can be added later behind `<source type="image/avif">`.
- **Budget enforcement**: `optimize_images.py` lowers quality in steps (72 → 50) if a
  variant exceeds its budget and reports any that still exceed it.

## 4. Full-screen static hero

- **Decision**: `height: 100vh; height: 100svh;` with the image as an absolutely positioned
  `object-fit: cover` `<img>` (not a CSS background), and a transparent header overlaid.
- **Rationale**: `svh` avoids mobile browser toolbar jumps; `vh` is the fallback. Using
  `<img>` keeps the image discoverable by the preload scanner, supports `srcset` and alt
  text, and lets it be the LCP element.

## 5. Typography

- **Decision**: System font stacks only — serif display stack
  (`"Didot", "Bodoni 72", "Bodoni MT", "Playfair Display", Georgia, serif`) for headings
  and `system-ui` for body text.
- **Rationale**: Zero font downloads and no third-party requests; Didot/Bodoni on Apple
  devices give the luxury feel, Georgia is a good universal fallback.

## 6. Mobile navigation without a framework

- **Decision**: `<html class="no-js">` swapped to `js` by an inline one-liner. Without JS,
  the three nav links are always visible; with JS, they collapse behind a
  `<button aria-expanded>` toggle on screens under 960px. Open/close is instant
  (`display` toggle, no transition).

## 7. Contact page map (revision 2)

- **Decision**: Google Maps embed via `https://www.google.com/maps?q=<address>&output=embed`
  in an `<iframe loading="lazy">` with a title, plus an "Open in Google Maps" link.
- **Rationale**: No API key, familiar to visitors, and lazy loading means the map's
  scripts and tiles load only when the visitor scrolls to it.
- **Alternatives considered**: Maps Embed API (needs an API key); OpenStreetMap embed (less
  familiar to visitors); static screenshot (not interactive).
- The contact form from revision 1 was removed at the client's request.

## 8. Dark brand theme (revision 2)

- **Decision**: Near-black background `#0a090b`, silver text `#dfe1e5`/`#f2f3f5`, pink
  accents `#fc65b0` sampled from the logo. Pink buttons use near-black text (contrast
  ≈ 7.5:1). The logo's black background is converted to transparency by
  `tools/build_brand_assets.py`, so it sits on any dark surface.

## 9. Cinematic hero without motion (revision 3)

- **Decision**: Grade the product photo offline (crop to 3:4, mute the pink wall and green
  grass outside a focus ellipse, filmic S-curve, cool shadows / warm highlights, vignette to
  black) with `tools/grade_hero.py`. In CSS, frame it as a film still: black letterbox bars
  (header on top, credits below), the graded frame melting into black via `mask-image`, a
  blurred copy of the same frame as ambient glow, and a static SVG noise layer for grain.
- **Rationale**: "Cinematic" without any motion, so it honours Principle III; grading at
  build time keeps the delivered WebP small (27–79 KB) and avoids heavy runtime filters on
  the main image.
- **Alternatives considered**: Video/Ken Burns pan (motion, banned); CSS filters on the
  photo (cannot do selective desaturation, and costs paint time on phones).

- **Revision 6**: scene I now uses a studio photograph already lit on pure black with pink
  smoke (`images-src/hero/hero-studio.jpg`, 895×1193). It gets only an edge vignette: the
  filmic curve and split tone used for the older photo lifted its blacks to grey-blue.
  CSS adds two faint pink radial hazes so the smoke seems to continue past the photo's
  masked edges. The close-up scenes and quote backgrounds still come from the higher-
  resolution original.

## 10. Typography and clipped cards (revision 3)

- **Decision**: Self-host Cormorant Garamond (normal variable + italic, Latin subset, 47 KB)
  with `font-display: swap` and a preload for the upright face. Cards are chamfered with
  `clip-path: polygon(...)`; a 1px gradient edge comes from a padded outer element whose
  inner face is cut 0.6px less, so the diagonal edge stays ~1px. Focus rings on clipped
  links are drawn with `drop-shadow` on an unclipped wrapper.
- **Rationale**: A display serif is the strongest single lever for an artistic, editorial
  feel; self-hosting keeps Principle I (no third-party requests).

## 11. Manual hero slider (revision 4)

- **Decision**: A horizontal `scroll-snap` track (`scroll-snap-type: x mandatory`,
  `scroll-snap-stop: always`) of full-height slides. Touch users swipe natively. `main.js`
  adds previous/next arrows and a counter; arrows call `scrollTo({behavior: "instant"})`, so
  scenes change without animation, and wrap around. Off-screen slides are `inert`.
  Without JS the track is still swipeable and the bar shows "Swipe for more scenes".
- **Rationale**: No library, no autoplay, accessible (carousel/slide roles, labelled
  buttons, `aria-live` counter, keyboard arrows on the focused track).
- **Alternatives considered**: CSS-only `:target`/radio sliders (break history and
  keyboard use); slider libraries (heavy, animate by default).

- **Revision 9**: by client request the slider now auto-advances every 6 s with a smooth
  slide (instant when wrapping round or under reduced motion). Controls: round chevron
  arrows, three progress bars whose active bar fills over the interval (CSS, inside the
  motion-allowed block, paused with the slideshow), and a pause/play button
  (`aria-pressed`). Following the WAI carousel pattern, the status region is
  `aria-live="off"` while playing and `polite` when paused. The timer lives between
  `autoplay-allowed` markers so the audit can confirm it is the only one.
- **Revision 10**: by client request the arrow and pause buttons are gone and each slide's
  photo fills the whole hero (`object-fit: cover`, under the transparent header) with
  gradients for legibility; the progress bars sit over the photo. Without a pause button
  (WCAG 2.2.2 trade-off accepted by the client), the slideshow still stops on hover,
  focus, touch and hidden tab and never runs with reduced motion.
- **Revision 11**: full bleed was reverted. The photos are 3:4 portraits at most 895 px
  wide; covering a 1440 px landscape hero enlarged them about 1.6× and cropped away the top
  and bottom, so they looked soft. The portrait framing is back (no blurred ambient glow, by
  request); full bleed needs landscape photos of at least 1920 × 1080.

## 12. Parallax quotes (revision 4)

- **Decision**: Background `<img>` (lazy, `srcset`) in a 126%-tall layer, moved -10% → +10%
  by a CSS scroll-driven animation (`animation-timeline: view()`) inside
  `@media (prefers-reduced-motion: no-preference)` and `@supports`. Browsers without scroll
  timelines get a passive, rAF-throttled scroll listener doing the same maths. The quote
  section uses `overflow: clip` (not `hidden`, which would create a scroll container and
  freeze the view timeline).
- **Rationale**: Runs on the compositor in modern browsers, no library, honours reduced
  motion, and lazy-loads the background like any other image.
- **Alternatives considered**: `background-attachment: fixed` (ignored on iOS, janky on
  Android, and CSS backgrounds can't lazy-load or use `srcset`).

## 13. Logo and footer on phones (revision 4)

- **Decision**: Header logo becomes an 88px round medallion centred between the menu and
  call buttons, hanging below the header bar like a pendant. The footer is styled as end
  credits: a 240px emblem (logo inside an SVG `textPath` ring reading "CUTE LOOK ◆ BRIDAL
  JEWELS ◆ HANDCRAFTED SINCE 1998"), a closing line, role/name credit rows, scene links,
  "Fin." and a giant outlined wordmark.

## 14. Embroidered border (revision 5)

- **Decision**: A 90×90 SVG tile used as `border-image` (slice 30, `round`): an outer
  running stitch, a fine thread, a row of pink beads (dot-dashed stroke with round caps),
  diamond knots and a rosette at each corner. One file per theme
  (`assets/icons/embroidery-{dark,light}.svg`, 3.6 KB each), plus a faint lattice ("jaali")
  tile for the ground. The SVG must declare `width`/`height`, or the browser assumes
  300×150 and the slices land in the wrong places.
- **Rationale**: Scales to any card size, crisp at any DPR, no images to download per card.

## 15. Light theme (revision 5)

- **Decision**: All colours are custom properties. Dark on `:root`; light on
  `:root[data-theme="light"]`; `.hero, .quote` re-declare the dark set so photographic
  sections stay dark. An inline script in `<head>` reads `localStorage["cutelook-theme"]`
  before first paint (no flash); the switch is `role="switch"` with `aria-checked`, hidden
  without JS, and updates `<meta name="theme-color">`. Light pink `#b8155f` keeps text
  contrast at ≈5.8:1 on ivory.
- **Alternatives considered**: following `prefers-color-scheme` by default (rejected: the
  brand is dark-first; the visitor chooses).

## 16. Full-screen phone menu (revision 5)

- **Decision**: Under 960px the `<nav>` becomes a fixed full-screen overlay: embroidered
  frame, "Choose a scene" eyebrow, numbered italic scenes with small notes, a call/WhatsApp
  line and hours. Opening is instant. JS locks page scroll, focuses the first link, keeps
  Tab inside (toggle, links, theme switch), and closes on Escape, link choice or resizing
  to desktop. The floating WhatsApp button is hidden while it is open.

## 17. Brand rename, caption strips, photo quote card (revision 7)

- **Brand**: "Aurelia" became **Cute Look** in every page, the footer ring text, credits,
  quote captions, email placeholder, page titles and the theme storage key
  (`cutelook-theme`; a previously saved theme choice resets once). The footer wordmark
  drops from 31vw to 23vw to fit the longer name.
- **Caption strips**: the gradient fade at the bottom of collection cards read as a muddy
  white haze in light mode. It is now a solid band (`--strip-bg`: `#ffffff` light,
  `rgba(8,7,10,.55)` dark) with its own clipped top-right corner, which the card's
  bottom-right chamfer also clips.
- **Photo in a quote card**: the client's photograph of a worn temple necklace
  (`images-src/features/worn-temple-pendant.jpg`, 3:4, WebP 400/600/895) sits in an arched
  window (rounded top, thin pink rule, inner mat) — stacked above the quote on phones,
  beside it on desktop. New image group `features`.

## 18. Hosting & caching

- **Decision**: Zoho Catalyst Slate (static framework, root `./`) auto-deploys `main`. Any
  other static host also works. A `_headers` file sets long caching for `/assets/img/*`
  (30 days) and shorter caching for CSS/JS (7 days), plus basic security headers.
  Hosts like Netlify/Cloudflare Pages apply Brotli/gzip automatically.
