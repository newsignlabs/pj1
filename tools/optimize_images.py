#!/usr/bin/env python3
"""Convert original photos in images-src/ into compressed, multi-width WebP files.

    images-src/<group>/<slug>.(jpg|jpeg|png|webp)
        -> assets/img/<group>/<slug>-<width>.webp

Each image is centre-cropped to its group's aspect ratio, resized to every
target width (never upscaled), encoded as WebP and checked against a size
budget. If a file is over budget, quality is lowered step by step.

Usage: python3 tools/optimize_images.py [--force]
       (without --force, outputs newer than their source are skipped)
"""
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "images-src"
OUT = ROOT / "assets" / "img"

KB = 1024
QUALITY = 72
MIN_QUALITY = 50

# group -> list of (slug prefix or None for "any", aspect w/h, widths, budget bytes)
RULES = {
    "hero": [
        # hero-photo.jpg is the ungraded original; tools/grade_hero.py makes hero-cinematic.jpg
        ("hero-cinematic", 3 / 4, [540, 810, 1080], 250 * KB),
        ("hero-detail", 3 / 4, [450, 600], 120 * KB),
    ],
    # Soft-focus quote backgrounds, also cut by tools/grade_hero.py
    "quotes": [(None, 1, [600, 1200], 120 * KB)],
    "collections": [(None, 4 / 5, [400, 600, 800], 120 * KB)],
    "pieces": [(None, 4 / 5, [400, 600, 800], 120 * KB)],
    "about": [(None, 4 / 5, [600, 900, 1200], 120 * KB)],
}

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def rule_for(group, slug):
    for prefix, aspect, widths, budget in RULES[group]:
        if prefix is None or slug.startswith(prefix):
            return aspect, widths, budget
    return None


def crop_to_aspect(img, aspect):
    w, h = img.size
    if w / h > aspect:
        new_w = round(h * aspect)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    new_h = round(w / aspect)
    top = (h - new_h) // 2
    return img.crop((0, top, w, top + new_h))


def encode(img, path, budget):
    quality = QUALITY
    while True:
        img.save(path, "WEBP", quality=quality, method=6)
        size = path.stat().st_size
        if size <= budget or quality <= MIN_QUALITY:
            return size, quality
        quality -= 6


def process(src, group, force):
    slug = src.stem
    rule = rule_for(group, slug)
    if rule is None:
        print(f"  skip {src.relative_to(ROOT)} (no rule for group '{group}')")
        return 0, []
    aspect, widths, budget = rule

    with Image.open(src) as im:
        img = ImageOps.exif_transpose(im).convert("RGB")
    img = crop_to_aspect(img, aspect)

    out_dir = OUT / group
    out_dir.mkdir(parents=True, exist_ok=True)
    written, over = 0, []
    available = [w for w in widths if w <= img.width] or [img.width]
    for width in widths:
        target = width if width in available else max(available)
        dest = out_dir / f"{slug}-{width}.webp"
        if not force and dest.exists() and dest.stat().st_mtime >= src.stat().st_mtime:
            continue
        height = round(target / aspect)
        resized = img.resize((target, height), Image.LANCZOS)
        size, quality = encode(resized, dest, budget)
        written += 1
        note = "" if quality == QUALITY else f" (q{quality})"
        print(f"  {dest.relative_to(ROOT)}  {target}x{height}  {size / KB:.0f} KB{note}")
        if size > budget:
            over.append(dest)
    return written, over


def main():
    force = "--force" in sys.argv
    if not SRC.exists():
        sys.exit("images-src/ not found. Add photos or run tools/generate_placeholders.py first.")

    total, over_budget = 0, []
    for group in RULES:
        folder = SRC / group
        if not folder.exists():
            continue
        print(f"[{group}]")
        for src in sorted(folder.iterdir()):
            if src.suffix.lower() in EXTENSIONS:
                written, over = process(src, group, force)
                total += written
                over_budget += over

    print(f"\nDone: {total} WebP file(s) written.")
    if over_budget:
        print("WARNING: still over budget after quality reduction:")
        for path in over_budget:
            print(f"  {path.relative_to(ROOT)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
