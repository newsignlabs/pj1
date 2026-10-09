#!/usr/bin/env python3
"""Convert original photos in images-src/ into compressed, multi-width WebP files.

    images-src/<group>/<slug>.(jpg|jpeg|png|webp|heic)
        -> assets/img/<group>/<slug>-<width>.webp

The "pieces" group is read recursively, one folder per category and sub-collection:

    images-src/pieces/<category>/<sub-collection>/<photo>.jpg
        -> assets/img/pieces/<category>/<sub-collection>/<photo>-<width>.webp

File and folder names are turned into URL-safe slugs ("IMG 0912.JPG" -> "img-0912").
Each rule centre-crops to its aspect ratio (or keeps the photo's own shape when the
aspect is None), resizes to every target width (never upscaled), encodes WebP and checks
a size budget, lowering quality step by step if needed.

A source is re-encoded only when its contents change (hashes are kept in
images-src/.optimized.json), so the script is cheap to run after every upload.

Usage: python3 tools/optimize_images.py [--force] [--prune]
       --force  re-encode everything
       --prune  delete pieces WebP files whose source photo was removed
"""
import hashlib
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageOps

try:  # photos straight from iPhones (optional: pip install pillow-heif)
    from pillow_heif import register_heif_opener

    register_heif_opener()
except ImportError:
    pass

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "images-src"
OUT = ROOT / "assets" / "img"
HASHES = SRC / ".optimized.json"

KB = 1024
QUALITY = 72
MIN_QUALITY = 50

# group -> list of (slug prefix or None for "any", aspect w/h or None to keep, widths, budget bytes)
RULES = {
    "hero": [
        # hero-photo.jpg / hero-studio.jpg are ungraded originals; tools/grade_hero.py makes the rest
        ("hero-cinematic", 3 / 4, [540, 720, 895], 250 * KB),
        ("hero-detail", 3 / 4, [450, 600], 120 * KB),
    ],
    # Soft-focus quote backgrounds, also cut by tools/grade_hero.py
    "quotes": [(None, 1, [600, 1200], 120 * KB)],
    # Photographs shown inside quote cards
    "features": [(None, 3 / 4, [400, 600, 895], 120 * KB)],
    "collections": [(None, 4 / 5, [400, 600, 800], 120 * KB)],
    # 4:5 thumbnails for the cards; the whole, uncropped photo for the gallery
    "pieces": [
        (None, 4 / 5, [300, 450, 600], 120 * KB),
        (None, None, [1080], 120 * KB),
    ],
    "about": [(None, 4 / 5, [600, 900, 1200], 120 * KB)],
}
RECURSIVE = {"pieces"}

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "photo"


def out_stem(src, group):
    """assets/img/<group>/<slugified relative path without extension>"""
    rel = src.relative_to(SRC / group)
    parts = [slugify(p) for p in rel.parent.parts] + [slugify(rel.stem)]
    return OUT / group / Path(*parts)


def rules_for(group, slug):
    return [r for r in RULES[group] if r[0] is None or slug.startswith(r[0])]


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


def flatten(img):
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        base = Image.new("RGB", img.size, (0, 0, 0))
        base.paste(img, mask=img.split()[3])
        return base
    return img.convert("RGB")


def process(src, group, stem):
    rules = rules_for(group, src.stem)
    if not rules:
        print(f"  skip {src.relative_to(ROOT)} (no rule for group '{group}')")
        return 0, []

    with Image.open(src) as im:
        original = flatten(ImageOps.exif_transpose(im))

    stem.parent.mkdir(parents=True, exist_ok=True)
    written, over = 0, []
    for _prefix, aspect, widths, budget in rules:
        img = crop_to_aspect(original, aspect) if aspect else original
        for width in widths:
            target = min(width, img.width)
            dest = stem.parent / f"{stem.name}-{width}.webp"
            height = round(img.height * target / img.width)
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
    prune = "--prune" in sys.argv
    if not SRC.exists():
        sys.exit("images-src/ not found. Add photos or run tools/generate_placeholders.py first.")

    try:
        hashes = json.loads(HASHES.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        hashes = {}
    seen = {}

    total, over_budget, expected = 0, [], set()
    for group in RULES:
        folder = SRC / group
        if not folder.exists():
            continue
        print(f"[{group}]")
        sources = folder.rglob("*") if group in RECURSIVE else folder.iterdir()
        for src in sorted(sources):
            if not src.is_file() or src.suffix.lower() not in EXTENSIONS:
                continue
            key = src.relative_to(ROOT).as_posix()
            digest = hashlib.sha1(src.read_bytes()).hexdigest()
            seen[key] = digest
            stem = out_stem(src, group)
            if group in RECURSIVE:
                expected.add(stem.relative_to(OUT).as_posix())
            outputs_exist = any(stem.parent.glob(f"{stem.name}-*.webp"))
            if not force and hashes.get(key) == digest and outputs_exist:
                continue
            written, over = process(src, group, stem)
            total += written
            over_budget += over

    if prune:
        for group in RECURSIVE:
            for webp in sorted((OUT / group).rglob("*.webp")):
                stem = re.sub(r"-\d+$", "", webp.relative_to(OUT).with_suffix("").as_posix())
                if stem not in expected:
                    webp.unlink()
                    print(f"  removed {webp.relative_to(ROOT)} (source deleted)")
            for d in sorted((OUT / group).rglob("*"), reverse=True):
                if d.is_dir() and not any(d.iterdir()):
                    d.rmdir()

    HASHES.write_text(json.dumps(seen, indent=0, sort_keys=True) + "\n", encoding="utf-8")
    print(f"\nDone: {total} WebP file(s) written.")
    if over_budget:
        print("WARNING: still over budget after quality reduction:")
        for path in over_budget:
            print(f"  {path.relative_to(ROOT)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
