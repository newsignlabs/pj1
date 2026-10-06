#!/usr/bin/env python3
"""Cut cinematic frames out of the hero product photo and colour-grade them.

    images-src/hero/hero-photo.jpg  ->  images-src/hero/hero-cinematic.jpg        (slide I, full set)
                                        images-src/hero/hero-detail-earrings.jpg   (slide II, close-up)
                                        images-src/hero/hero-detail-pendant.jpg    (slide III, close-up)
                                        images-src/quotes/quote-*.jpg              (soft-focus quote backgrounds)

Slides: crop to 3:4, mute the busy backdrop (pink wall, green grass) outside the
jewellery, filmic S-curve with warm highlights and cool shadows, vignette to black.
Quote backgrounds: square close-ups, darker and softly blurred (shallow depth of
field), so text sits on top legibly. Run tools/optimize_images.py afterwards.

Crops are (left, top, width) in pixels of the original photo; adjust FRAMES when the
photo changes.

Usage: python3 tools/grade_hero.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "images-src" / "hero" / "hero-photo.jpg"

# name -> (output path, (left, top, width), aspect h/w, focus (cx, cy, rx, ry), kind)
FRAMES = {
    "hero-cinematic": ("hero", (60, 150, 1080), 4 / 3, (0.5, 0.44, 0.46, 0.40), "slide"),
    "hero-detail-earrings": ("hero", (225, 150, 600), 4 / 3, (0.5, 0.36, 0.5, 0.42), "slide"),
    "hero-detail-pendant": ("hero", (300, 600, 600), 4 / 3, (0.5, 0.42, 0.5, 0.45), "slide"),
    "quote-chain": ("quotes", (170, 330, 460), 1.0, (0.5, 0.5, 0.6, 0.6), "quote"),
    "quote-pendant": ("quotes", (380, 760, 460), 1.0, (0.5, 0.45, 0.6, 0.6), "quote"),
    "quote-earrings": ("quotes", (330, 220, 460), 1.0, (0.5, 0.5, 0.6, 0.6), "quote"),
}
QUOTE_SIZE = 1200
LUMA = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)


def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def grade(img, focus_box, kind):
    rgb = np.asarray(img).astype(np.float32) / 255.0
    h, w, _ = rgb.shape
    cx, cy, rx, ry = focus_box

    yy, xx = np.mgrid[0:h, 0:w]
    dist = np.sqrt(((xx / w - cx) / rx) ** 2 + ((yy / h - cy) / ry) ** 2)
    focus = 1.0 - smoothstep(0.55, 1.25, dist)
    blur = max(8, w // 27)
    focus = np.asarray(Image.fromarray((focus * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(blur))).astype(np.float32)[..., None] / 255.0

    # 1. Mute the backdrop, keep the jewellery rich.
    luma = (rgb @ LUMA)[..., None]
    sat = (0.18 + 0.92 * focus) if kind == "slide" else 0.75
    rgb = luma + (rgb - luma) * sat

    # 2. Filmic S-curve with slightly lifted blacks.
    rgb = np.clip(rgb, 0, 1)
    rgb = rgb * rgb * (3 - 2 * rgb) * 0.9 + rgb * 0.1
    rgb = 0.03 + rgb * 0.97

    # 3. Split tone: cool shadows, warm (gold) highlights.
    luma = (rgb @ LUMA)[..., None]
    rgb = rgb + (1 - luma) ** 2 * np.array([-0.02, 0.0, 0.03]) + luma ** 2 * np.array([0.05, 0.025, -0.04])

    # 4. Vignette to black.
    vignette = 0.12 + 0.88 * (1.0 - smoothstep(0.5, 1.55, dist))[..., None]
    if kind == "slide":
        rgb = rgb * (0.35 + 0.65 * focus) * vignette
    else:
        rgb = rgb * 0.62 * vignette  # quotes sit under text: keep them dark
    return Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))


def main():
    photo = Image.open(SRC).convert("RGB")
    for name, (folder, (left, top, width), aspect, focus_box, kind) in FRAMES.items():
        height = round(width * aspect)
        frame = photo.crop((left, top, left + width, top + height))
        if kind == "quote":
            # Upscale then blur: a deliberate shallow-focus look that hides the low resolution.
            frame = frame.resize((QUOTE_SIZE, round(QUOTE_SIZE * aspect)), Image.LANCZOS)
            frame = frame.filter(ImageFilter.GaussianBlur(5))
        out = grade(frame, focus_box, kind)
        dest = ROOT / "images-src" / folder / f"{name}.jpg"
        dest.parent.mkdir(parents=True, exist_ok=True)
        out.save(dest, "JPEG", quality=92, optimize=True)
        print(f"Wrote {dest.relative_to(ROOT)} ({out.width}x{out.height})")


if __name__ == "__main__":
    main()
