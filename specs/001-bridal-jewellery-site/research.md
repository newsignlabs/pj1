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

## 9. Hosting & caching

- **Decision**: Any static host. A `_headers` file sets long caching for `/assets/img/*`
  (30 days) and shorter caching for CSS/JS (7 days), plus basic security headers.
  Hosts like Netlify/Cloudflare Pages apply Brotli/gzip automatically.
