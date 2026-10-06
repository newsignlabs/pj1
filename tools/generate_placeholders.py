#!/usr/bin/env python3
"""Generate placeholder source images in images-src/.

These stand in for real product photography until the business supplies it.
Replace any file in images-src/ with a real photo of the same name and re-run
tools/optimize_images.py.

Usage: python3 tools/generate_placeholders.py [--force]
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "images-src"

# (slug, motif) for every piece, grouped by collection.
CATALOGUE = {
    "bridal-sets": [
        "royal-kundan-bridal-set", "polki-heritage-set",
        "temple-gold-bridal-set", "pearl-meenakari-set",
    ],
    "necklaces": [
        "kundan-choker", "rani-haar", "layered-pearl-necklace", "emerald-drop-necklace",
    ],
    "earrings": [
        "chandbali-earrings", "jhumka-earrings", "diamond-drop-earrings", "kundan-ear-chains",
    ],
    "bangles": [
        "kundan-kada", "gold-bangle-set", "diamond-bracelet", "meenakari-bangles",
    ],
    "maang-tikka": [
        "classic-maang-tikka", "matha-patti", "jhoomar-passa", "pearl-borla",
    ],
    "rings": [
        "solitaire-engagement-ring", "polki-cocktail-ring", "couple-bands", "emerald-halo-ring",
    ],
}

BACKGROUNDS = {
    "bridal-sets": ("#3d0c16", "#8c2f3f"),
    "necklaces": ("#2a1a12", "#7a5236"),
    "earrings": ("#3b1f2b", "#b3727f"),
    "bangles": ("#132a24", "#3f7a68"),
    "maang-tikka": ("#2b1630", "#7d4d86"),
    "rings": ("#1d2230", "#5b6b8c"),
    "about": ("#4a2c1d", "#c79a73"),
    "hero": ("#22060c", "#7a1f30"),
}

GOLD = (212, 175, 106)
GOLD_LIGHT = (246, 222, 160)
GOLD_DARK = (150, 112, 52)
GEMS = {
    "ruby": (160, 20, 45),
    "emerald": (20, 110, 75),
    "pearl": (240, 236, 226),
    "polki": (232, 232, 240),
    "sapphire": (30, 60, 140),
}

SCALE = 2  # supersample for smooth edges


def background(size, colours, rng):
    """Soft radial gradient, light centre fading to dark edges."""
    w, h = size
    dark, light = colours
    grad = Image.radial_gradient("L").resize((w, h), Image.BILINEAR)
    grad = ImageOps.colorize(grad, black=light, white=dark)
    # Gentle diagonal sheen so images are not perfectly symmetrical.
    sheen = Image.linear_gradient("L").rotate(rng.choice([30, 45, -30, -45]), expand=False)
    sheen = sheen.resize((w, h), Image.BILINEAR).point(lambda v: v // 6)
    return Image.composite(Image.new("RGB", (w, h), light), grad, sheen)


def bead(draw, cx, cy, r, colour=GOLD):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GOLD_DARK)
    r2 = r * 0.82
    draw.ellipse((cx - r2, cy - r2, cx + r2, cy + r2), fill=colour)
    hr = r * 0.3
    hx, hy = cx - r * 0.3, cy - r * 0.3
    if colour == GOLD:
        draw.ellipse((hx - hr, hy - hr, hx + hr, hy + hr), fill=GOLD_LIGHT)
    else:
        draw.ellipse((hx - hr, hy - hr, hx + hr, hy + hr), fill=(255, 255, 255))


def drop(draw, cx, cy, r, gem):
    """Teardrop pendant: gold frame with a gem."""
    pts = []
    for i in range(60):
        t = 2 * math.pi * i / 60
        x = cx + r * math.sin(t) * (1 - 0.35 * math.cos(t))
        y = cy - r * 1.3 * math.cos(t)
        pts.append((x, y))
    draw.polygon(pts, fill=GOLD_DARK)
    inner = [(cx + (x - cx) * 0.75, cy + (y - cy) * 0.75) for x, y in pts]
    draw.polygon(inner, fill=gem)
    draw.ellipse((cx - r * 0.25, cy - r * 0.5, cx, cy - r * 0.2), fill=(255, 255, 255))


def necklace(draw, w, h, rng, cx=None, top=None, width=None, depth=None, gem=None):
    cx = cx if cx is not None else w / 2
    top = top if top is not None else h * 0.22
    width = width if width is not None else w * 0.62
    depth = depth if depth is not None else h * 0.38
    gem = gem or GEMS[rng.choice(list(GEMS))]
    strands = rng.randint(1, 3)
    for s in range(strands):
        n = 34 + s * 6
        r = width * (0.026 - s * 0.003)
        for i in range(n + 1):
            t = math.pi * i / n
            x = cx - width / 2 * math.cos(t) * (1 + s * 0.08)
            y = top + depth * math.sin(t) * (1 + s * 0.18)
            colour = gem if (i % 4 == 0 and s == 0) else GOLD
            bead(draw, x, y, r, colour)
    drop(draw, cx, top + depth * (1 + 0.18 * (strands - 1)) + width * 0.145, width * 0.1, gem)


def earrings(draw, w, h, rng):
    gem = GEMS[rng.choice(list(GEMS))]
    for cx in (w * 0.32, w * 0.68):
        top = h * 0.25
        bead(draw, cx, top, w * 0.045, gem)
        # bell (jhumka dome)
        bw, bh = w * 0.13, h * 0.16
        draw.pieslice((cx - bw, top + h * 0.06, cx + bw, top + h * 0.06 + bh * 2), 180, 360, fill=GOLD)
        draw.pieslice((cx - bw * 0.8, top + h * 0.09, cx + bw * 0.8, top + h * 0.09 + bh * 1.6),
                      200, 340, fill=GOLD_LIGHT)
        base = top + h * 0.06 + bh
        for i in range(7):
            x = cx - bw + i * (2 * bw / 6)
            bead(draw, x, base + h * 0.03, w * 0.014, GEMS["pearl"])
        drop(draw, cx, base + h * 0.12, w * 0.035, gem)


def bangles(draw, w, h, rng):
    gem = GEMS[rng.choice(list(GEMS))]
    count = rng.randint(2, 4)
    for i in range(count):
        cx = w * 0.5 + (i - (count - 1) / 2) * w * 0.12
        cy = h * 0.5
        rx, ry = w * 0.3, h * 0.13
        thick = w * 0.03
        draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=GOLD_DARK, width=int(thick))
        draw.ellipse((cx - rx + 4, cy - ry + 4, cx + rx - 4, cy + ry - 4),
                     outline=GOLD, width=int(thick * 0.6))
        for k in range(12):
            t = 2 * math.pi * k / 12
            bead(draw, cx + rx * 0.97 * math.cos(t), cy + ry * 0.94 * math.sin(t), w * 0.011, gem)


def ring(draw, w, h, rng, cx=None, cy=None, scale=1.0, gem=None):
    cx = cx if cx is not None else w / 2
    cy = cy if cy is not None else h * 0.58
    gem = gem or GEMS[rng.choice(list(GEMS))]
    rx, ry = w * 0.2 * scale, h * 0.12 * scale
    draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=GOLD_DARK, width=int(w * 0.04 * scale))
    draw.ellipse((cx - rx + 6, cy - ry + 6, cx + rx - 6, cy + ry - 6),
                 outline=GOLD, width=int(w * 0.022 * scale))
    gr = w * 0.07 * scale
    gy = cy - ry - gr * 0.6
    draw.regular_polygon((cx, gy, gr * 1.15), 8, fill=GOLD_DARK)
    draw.regular_polygon((cx, gy, gr), 8, fill=gem)
    draw.polygon([(cx - gr * 0.5, gy - gr * 0.3), (cx, gy - gr * 0.7), (cx + gr * 0.1, gy - gr * 0.2)],
                 fill=(255, 255, 255))


def tikka(draw, w, h, rng):
    gem = GEMS[rng.choice(list(GEMS))]
    cx = w / 2
    for i in range(18):
        bead(draw, cx, h * 0.12 + i * h * 0.022, w * 0.012)
    # side chains (matha patti feel)
    if rng.random() > 0.4:
        for side in (-1, 1):
            for i in range(16):
                t = i / 15
                x = cx + side * w * 0.38 * t
                y = h * 0.12 + h * 0.2 * math.sin(math.pi * t * 0.9)
                bead(draw, x, y, w * 0.01)
    cy = h * 0.58
    r = w * 0.12
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GOLD_DARK)
    draw.ellipse((cx - r * 0.82, cy - r * 0.82, cx + r * 0.82, cy + r * 0.82), fill=GOLD)
    for k in range(10):
        t = 2 * math.pi * k / 10
        bead(draw, cx + r * 0.62 * math.cos(t), cy + r * 0.62 * math.sin(t), w * 0.016, GEMS["pearl"])
    bead(draw, cx, cy, w * 0.04, gem)
    drop(draw, cx, cy + r + h * 0.07, w * 0.04, gem)


def bridal_set(draw, w, h, rng):
    gem = GEMS[rng.choice(list(GEMS))]
    necklace(draw, w, h, rng, top=h * 0.18, width=w * 0.56, depth=h * 0.34, gem=gem)
    for cx in (w * 0.12, w * 0.88):
        bead(draw, cx, h * 0.62, w * 0.035, gem)
        drop(draw, cx, h * 0.74, w * 0.035, gem)


MOTIFS = {
    "bridal-sets": bridal_set,
    "necklaces": necklace,
    "earrings": earrings,
    "bangles": bangles,
    "maang-tikka": tikka,
    "rings": ring,
}


def render(size, colours, painter, seed):
    rng = random.Random(seed)
    w, h = size[0] * SCALE, size[1] * SCALE
    img = background((w, h), colours, rng)
    draw = ImageDraw.Draw(img)
    painter(draw, w, h, rng)
    img = img.resize(size, Image.LANCZOS)
    return img.filter(ImageFilter.SMOOTH)


def save(img, path, force):
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "JPEG", quality=90, optimize=True, progressive=True)
    return True


def main():
    force = "--force" in sys.argv
    made = 0
    piece_size = (1200, 1500)

    for collection, pieces in CATALOGUE.items():
        motif = MOTIFS[collection]
        colours = BACKGROUNDS[collection]
        made += save(render(piece_size, colours, motif, collection),
                     SRC / "collections" / f"{collection}.jpg", force)
        for slug in pieces:
            made += save(render(piece_size, colours, motif, slug), SRC / "pieces" / f"{slug}.jpg", force)

    def hero_landscape(draw, w, h, rng):
        necklace(draw, w, h, rng, cx=w * 0.72, top=h * 0.1, width=w * 0.36, depth=h * 0.42,
                 gem=GEMS["ruby"])

    def hero_portrait(draw, w, h, rng):
        necklace(draw, w, h, rng, cx=w * 0.5, top=h * 0.58, width=w * 0.78, depth=h * 0.2,
                 gem=GEMS["ruby"])

    made += save(render((2560, 1440), BACKGROUNDS["hero"], hero_landscape, "hero-l"),
                 SRC / "hero" / "hero-landscape.jpg", force)
    made += save(render((1080, 1920), BACKGROUNDS["hero"], hero_portrait, "hero-p"),
                 SRC / "hero" / "hero-portrait.jpg", force)

    def about(draw, w, h, rng):
        ring(draw, w, h, rng, cx=w * 0.5, cy=h * 0.7, scale=0.8, gem=GEMS["emerald"])
        bead(draw, w * 0.25, h * 0.25, w * 0.05, GEMS["ruby"])
        bead(draw, w * 0.75, h * 0.3, w * 0.04, GEMS["pearl"])

    made += save(render((1200, 1500), BACKGROUNDS["about"], about, "about"),
                 SRC / "about" / "about.jpg", force)

    print(f"Placeholder sources written: {made} (use --force to overwrite existing files)")


if __name__ == "__main__":
    main()
