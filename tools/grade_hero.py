#!/usr/bin/env python3
"""Give the hero product photo a still, cinematic colour grade.

    images-src/hero/hero-photo.jpg  ->  images-src/hero/hero-cinematic.jpg

Steps: crop to the jewellery (3:4), mute the busy backdrop (pink wall, green
grass) while keeping the piece itself rich, apply a filmic S-curve with warm
highlights and cool shadows, then a heavy vignette that falls off to black so
the photo melts into the dark page. Run tools/optimize_images.py afterwards.

Usage: python3 tools/grade_hero.py [crop_left crop_top crop_width]
       (crop defaults suit the current photo; height is always width * 4/3)
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "images-src" / "hero" / "hero-photo.jpg"
OUT = ROOT / "images-src" / "hero" / "hero-cinematic.jpg"

# Focus ellipse (fractions of the cropped frame) — the area kept vivid.
FOCUS_CX, FOCUS_CY = 0.5, 0.44
FOCUS_RX, FOCUS_RY = 0.46, 0.40


def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def main():
    left, top, width = (int(v) for v in sys.argv[1:4]) if len(sys.argv) == 4 else (60, 150, 1080)
    img = Image.open(SRC).convert("RGB")
    img = img.crop((left, top, left + width, top + width * 4 // 3))
    rgb = np.asarray(img).astype(np.float32) / 255.0
    h, w, _ = rgb.shape

    yy, xx = np.mgrid[0:h, 0:w]
    dist = np.sqrt(((xx / w - FOCUS_CX) / FOCUS_RX) ** 2 + ((yy / h - FOCUS_CY) / FOCUS_RY) ** 2)
    focus = 1.0 - smoothstep(0.55, 1.25, dist)          # 1 at the jewellery, 0 at the edges
    focus = np.asarray(Image.fromarray((focus * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(40))).astype(np.float32)[..., None] / 255.0

    # 1. Desaturate the backdrop, keep the piece rich.
    luma = (rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32))[..., None]
    sat = 0.18 + 0.92 * focus
    rgb = luma + (rgb - luma) * sat

    # 2. Filmic S-curve with slightly lifted blacks.
    rgb = np.clip(rgb, 0, 1)
    rgb = rgb * rgb * (3 - 2 * rgb) * 0.9 + rgb * 0.1
    rgb = 0.03 + rgb * 0.97

    # 3. Split tone: cool shadows, warm (gold) highlights.
    luma = (rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32))[..., None]
    shadows = (1 - luma) ** 2
    highlights = luma ** 2
    rgb = rgb + shadows * np.array([-0.02, 0.0, 0.03]) + highlights * np.array([0.05, 0.025, -0.04])

    # 4. Vignette to black, strongest at the corners.
    vignette = 0.12 + 0.88 * (1.0 - smoothstep(0.5, 1.55, dist))[..., None]
    rgb = rgb * (0.35 + 0.65 * focus) * vignette

    out = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))
    out.save(OUT, "JPEG", quality=92, optimize=True)
    print(f"Wrote {OUT.relative_to(ROOT)} ({out.width}x{out.height})")


if __name__ == "__main__":
    main()
