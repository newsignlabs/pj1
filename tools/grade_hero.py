#!/usr/bin/env python3
"""The cinematic colour grade used for the Home slider and quote backgrounds.

Used by tools/build_slots.py, which takes the photo in each slot folder
(images-src/hero/slide-N/, images-src/quotes/quote-*/), crops it and applies grade():

  - "studio": the photo is already lit on black, so only a gentle edge vignette.
  - "slide":  mute the backdrop outside the jewellery, filmic S-curve with warm
              highlights and cool shadows, vignette to black.
  - "quote":  darker and softly blurred (shallow depth of field) so text sits on top.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent

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

    # 1. Mute the backdrop, keep the jewellery rich (the studio shot keeps its colours).
    if kind != "studio":
        luma = (rgb @ LUMA)[..., None]
        sat = (0.18 + 0.92 * focus) if kind == "slide" else 0.75
        rgb = luma + (rgb - luma) * sat

    if kind == "studio":
        # Already lit on pure black: keep its blacks and colours, only deepen the edges.
        vignette = 0.12 + 0.88 * (1.0 - smoothstep(0.5, 1.55, dist))[..., None]
        rgb = rgb * (0.6 + 0.4 * vignette)
        return Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))

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



if __name__ == "__main__":
    sys.exit("Photos are now graded by tools/build_slots.py (drop a photo into its slot folder).")
