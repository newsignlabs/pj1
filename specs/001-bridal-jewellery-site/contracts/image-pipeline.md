# Contract: Image Pipeline & Markup

## Folders and widths

| Group (`images-src/<group>/`) | Aspect (centre-cropped) | Output widths (px) | Budget per file |
|-------------------------------|-------------------------|--------------------|-----------------|
| `hero` — `hero-cinematic` (graded by `tools/grade_hero.py` from `hero-photo.jpg`) | 3:4 | 540, 810, 1080 | 250 KB |
| `collections` | 4:5 | 400, 600, 800 | 120 KB |
| `pieces` | 4:5 | 400, 600, 800 | 120 KB |
| `about` | 4:5 | 600, 900, 1200 | 120 KB |
| `brand` — `logo` (via `tools/build_brand_assets.py`) | 1:1, black → transparent | 64, 128, 256 | — |

Output: `assets/img/<group>/<slug>-<width>.webp`. Sources smaller than a target width are
not upscaled; the largest available width is used instead.

## Encoding

WebP, `quality=72`, `method=6`, EXIF/ICC metadata stripped, sRGB. If a variant is over
budget the script retries at lower quality (down to 50) and warns if still over.

## Markup — lazy content image

```html
<img src="assets/img/pieces/kundan-choker-400.webp"
     srcset="assets/img/pieces/kundan-choker-400.webp 400w,
             assets/img/pieces/kundan-choker-600.webp 600w,
             assets/img/pieces/kundan-choker-800.webp 800w"
     sizes="(min-width: 1200px) 270px, (min-width: 960px) 22vw, (min-width: 640px) 30vw, 46vw"
     width="800" height="1000" loading="lazy" decoding="async"
     alt="Kundan choker necklace in 22k gold">
```

## Markup — hero (eager, cinematic still)

```html
<picture class="hero__media">
  <img src="assets/img/hero/hero-cinematic-810.webp"
       srcset="…-540.webp 540w, …-810.webp 810w, …-1080.webp 1080w"
       sizes="(min-width: 960px) 60vh, (orientation: landscape) 60vh, 100vw"
       width="1080" height="1440" fetchpriority="high" decoding="async" alt="…">
</picture>
```
