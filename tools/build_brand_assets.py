#!/usr/bin/env python3
"""Build logo and favicon files from images-src/brand/logo.png.

The source logo is drawn on solid black. The black is converted to
transparency so the mark sits cleanly on any dark background.

Outputs:
    assets/img/brand/logo-{64,128,256}.webp   transparent logo (header/footer)
    assets/icons/favicon-32.png               browser tab icon
    assets/icons/apple-touch-icon.png         180x180 home-screen icon (on black)

Usage: python3 tools/build_brand_assets.py
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "images-src" / "brand" / "logo.png"
OUT_IMG = ROOT / "assets" / "img" / "brand"
OUT_ICONS = ROOT / "assets" / "icons"
WIDTHS = [64, 128, 256]


def black_to_alpha(img):
    """Treat black as transparent: alpha = brightest channel, colour un-premultiplied."""
    img = img.convert("RGB")
    out = Image.new("RGBA", img.size)
    px = [
        (0, 0, 0, 0) if (a := max(p)) == 0
        else (min(255, p[0] * 255 // a), min(255, p[1] * 255 // a), min(255, p[2] * 255 // a), a)
        for p in getattr(img, "get_flattened_data", img.getdata)()
    ]
    out.putdata(px)
    return out


def square_crop(img, pad_ratio=0.04):
    """Crop to the visible mark, padded into a square."""
    bbox = img.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
    left, top, right, bottom = bbox
    side = max(right - left, bottom - top)
    side += int(side * pad_ratio * 2)
    cx, cy = (left + right) // 2, (top + bottom) // 2
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(img.crop(bbox), (side // 2 - (cx - left), side // 2 - (cy - top)))
    return canvas


def main():
    logo = square_crop(black_to_alpha(Image.open(SRC)))
    OUT_IMG.mkdir(parents=True, exist_ok=True)
    OUT_ICONS.mkdir(parents=True, exist_ok=True)
    for w in WIDTHS:
        dest = OUT_IMG / f"logo-{w}.webp"
        logo.resize((w, w), Image.LANCZOS).save(dest, "WEBP", quality=80, alpha_quality=80, method=6)
        print(f"  {dest.relative_to(ROOT)}  {dest.stat().st_size / 1024:.1f} KB")

    logo.resize((32, 32), Image.LANCZOS).save(OUT_ICONS / "favicon-32.png", optimize=True)
    touch = Image.new("RGBA", (180, 180), (0, 0, 0, 255))
    mark = logo.resize((156, 156), Image.LANCZOS)
    touch.alpha_composite(mark, (12, 12))
    touch.convert("RGB").save(OUT_ICONS / "apple-touch-icon.png", optimize=True)
    print("  assets/icons/favicon-32.png, assets/icons/apple-touch-icon.png")


if __name__ == "__main__":
    main()
