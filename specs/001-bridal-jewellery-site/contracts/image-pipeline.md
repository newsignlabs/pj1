# Contract: Image Pipeline & Markup

## Folders and widths

| Group (`images-src/<group>/`) | Aspect (centre-cropped) | Output widths (px) | Budget per file |
|-------------------------------|-------------------------|--------------------|-----------------|
| `hero` — `hero-landscape` | 16:9 | 1280, 1920, 2560 | 250 KB |
| `hero` — `hero-portrait` | 9:16 | 480, 720, 1080 | 250 KB |
| `collections` | 4:5 | 400, 600, 800 | 120 KB |
| `pieces` | 4:5 | 400, 600, 800 | 120 KB |
| `about` | 4:5 | 600, 900, 1200 | 120 KB |

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

## Markup — hero (eager, art-directed)

```html
<picture>
  <source media="(orientation: portrait) and (max-width: 959px)"
          srcset="…hero-portrait-480.webp 480w, …-720.webp 720w, …-1080.webp 1080w" sizes="100vw">
  <img src="…hero-landscape-1280.webp"
       srcset="…-1280.webp 1280w, …-1920.webp 1920w, …-2560.webp 2560w" sizes="100vw"
       width="2560" height="1440" fetchpriority="high" decoding="async" alt="…">
</picture>
```
