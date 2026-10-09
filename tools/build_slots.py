#!/usr/bin/env python3
"""Turn the photo "slot" folders into the source files the site is built from.

Every picture on the site outside the Collections galleries has its own folder. Drop a
photo into the folder (any name, JPG/PNG/WebP/HEIC) and it replaces the picture:

    images-src/hero/slide-1/              Home slider, slide 1 (studio shot; edge vignette)
    images-src/hero/slide-2/              Home slider, slide 2 (close-up; cinematic grade)
    images-src/hero/slide-3/              Home slider, slide 3 (close-up; cinematic grade)
    images-src/quotes/quote-chain/        quote background (soft focus, darkened)
    images-src/collections/<category>/    Home page category card (one per category)
    images-src/features/                  photo inside the "Some jewels are worn..." card
    images-src/about/                     Our Story photo
    images-src/brand/                     logo (drawn on black) -> logo files and favicons

A folder holds one photo. If it has several, the most recently added one wins and the
others are deleted (they stay in git history). Photos are centre-cropped to the shape
each place needs, so keep the subject in the middle.

The prepared files are written next to the folders (e.g. images-src/hero/hero-cinematic.jpg,
images-src/collections/necklaces.jpg) and then encoded by tools/optimize_images.py.
A slot is only rebuilt when its photo changes (hashes in images-src/.slots.json).

Usage: python3 tools/build_slots.py [--force]
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps

try:  # photos straight from iPhones (optional: pip install pillow-heif)
    from pillow_heif import register_heif_opener

    register_heif_opener()
except ImportError:
    pass

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "images-src"
STATE = SRC / ".slots.json"
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
QUOTE_SIZE = 1200

sys.path.insert(0, str(ROOT / "tools"))
from grade_hero import grade  # noqa: E402  (the cinematic grade)

# folder -> (prepared file, kind, aspect h/w or None, focus box for the grade)
GRADED = {
    "hero/slide-1": ("hero/hero-cinematic.jpg", "studio", 4 / 3, (0.5, 0.45, 0.6, 0.55)),
    "hero/slide-2": ("hero/hero-detail-earrings.jpg", "slide", 4 / 3, (0.5, 0.36, 0.5, 0.42)),
    "hero/slide-3": ("hero/hero-detail-pendant.jpg", "slide", 4 / 3, (0.5, 0.42, 0.5, 0.45)),
    "quotes/quote-chain": ("quotes/quote-chain.jpg", "quote", 1.0, (0.5, 0.5, 0.6, 0.6)),
}
# Folders that are themselves the slot: the photo is renamed to this file name.
FLAT = {
    "about": "about.jpg",
    "features": "worn-temple-pendant.jpg",
    "brand": "logo.png",
}


def photos_in(folder, exclude=()):
    if not folder.is_dir():
        return []
    return [p for p in folder.iterdir()
            if p.is_file() and p.suffix.lower() in EXTENSIONS and p.name not in exclude]


def added_time(path):
    """When the file was last committed (newest wins); uncommitted files count as newest."""
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%ct", "--", str(path)], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout.strip()
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", str(path)], cwd=ROOT,
                                 capture_output=True).returncode == 0
    except (OSError, subprocess.CalledProcessError):
        out, tracked = "", False
    if not tracked or not out:
        return float("inf"), path.stat().st_mtime
    return float(out), path.stat().st_mtime


def newest(photos):
    """Keep the most recently added photo; delete the rest."""
    photos = sorted(photos, key=added_time)
    for old in photos[:-1]:
        old.unlink()
        print(f"  removed older photo {old.relative_to(ROOT)}")
    return photos[-1]


def load(path):
    with Image.open(path) as im:
        img = ImageOps.exif_transpose(im)
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGBA")
            base = Image.new("RGB", img.size, (0, 0, 0))
            base.paste(img, mask=img.split()[3])
            return base
        return img.convert("RGB")


def centre_crop(img, aspect_hw):
    w, h = img.size
    if h / w > aspect_hw:
        new_h = round(w * aspect_hw)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))
    new_w = round(h / aspect_hw)
    left = (w - new_w) // 2
    return img.crop((left, 0, left + new_w, h))


def digest(path):
    return hashlib.sha1(path.read_bytes()).hexdigest()


def main():
    force = "--force" in sys.argv
    try:
        state = json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        state = {}
    new_state, built = {}, []

    def changed(key, photo, dest):
        h = digest(photo)
        new_state[key] = h
        return force or state.get(key) != h or not dest.exists()

    # Graded slots: hero slides and quote backgrounds
    for folder, (prepared, kind, aspect, focus) in GRADED.items():
        photos = photos_in(SRC / folder)
        if not photos:
            continue
        photo = newest(photos)
        dest = SRC / prepared
        if not changed(folder, photo, dest):
            continue
        frame = centre_crop(load(photo), aspect)
        if kind == "quote":
            frame = frame.resize((QUOTE_SIZE, round(QUOTE_SIZE * aspect)), Image.LANCZOS)
            frame = frame.filter(ImageFilter.GaussianBlur(5))
        grade(frame, focus, kind).save(dest, "JPEG", quality=92, optimize=True)
        built.append(dest)

    # Home page category cards: images-src/collections/<category>/ -> <category>.jpg
    for folder in sorted(d for d in (SRC / "collections").iterdir() if d.is_dir()):
        photos = photos_in(folder)
        if not photos:
            continue
        photo = newest(photos)
        dest = folder.parent / f"{folder.name}.jpg"
        if not changed(f"collections/{folder.name}", photo, dest):
            continue
        if photo.suffix.lower() in (".jpg", ".jpeg"):
            shutil.copyfile(photo, dest)
        else:
            load(photo).save(dest, "JPEG", quality=93)
        built.append(dest)

    # Flat slots: the newest photo becomes the canonical file
    for folder, name in FLAT.items():
        canonical = SRC / folder / name
        photos = photos_in(SRC / folder)
        if not photos:
            continue
        photo = newest(photos)
        if photo != canonical:
            if name.endswith(".png"):
                with Image.open(photo) as im:
                    ImageOps.exif_transpose(im).convert("RGB").save(canonical, "PNG")
            elif photo.suffix.lower() in (".jpg", ".jpeg"):
                shutil.copyfile(photo, canonical)
            else:
                load(photo).save(canonical, "JPEG", quality=93)
            photo.unlink()
            print(f"  {photo.relative_to(ROOT)} -> {canonical.relative_to(ROOT)}")
        if changed(folder, canonical, canonical) or photo != canonical:
            built.append(canonical)
            if folder == "brand":
                subprocess.run([sys.executable, str(ROOT / "tools" / "build_brand_assets.py")], check=True)

    # Photos dropped next to the slot folders instead of inside one are not used
    generated = {Path(p).name for p, *_ in GRADED.values()}
    generated |= {f"{d.name}.jpg" for d in (SRC / "collections").iterdir() if d.is_dir()}
    for parent in ("hero", "quotes", "collections"):
        for stray in photos_in(SRC / parent, exclude=generated):
            print(f"::warning file={stray.relative_to(ROOT)}::Not used: put this photo inside one of "
                  f"the folders in images-src/{parent}/ (see README, 'Updating photos').")

    STATE.write_text(json.dumps(new_state, indent=0, sort_keys=True) + "\n", encoding="utf-8")
    for dest in built:
        print(f"  prepared {dest.relative_to(ROOT)}")
    print(f"Slots: {len(built)} updated")


if __name__ == "__main__":
    main()
