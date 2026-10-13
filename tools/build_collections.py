#!/usr/bin/env python3
"""Build the Collections page from the photo folders.

    images-src/pieces/<category>/<sub-collection>/<photo>.jpg

  - Each category folder is one section of collections.html. Its order, title and intro
    come from content/collections.json; a folder not listed there is added at the end,
    titled from its name.
  - Each sub-collection folder is one card. The folder name is the card title
    ("antique-premium" -> "Antique Premium"); a number prefix ("1-antique") sets the
    order and is not shown. The card cover is a photo named "cover..." if there is one,
    otherwise the first photo by file name.
  - A photo placed directly in a category folder becomes a card of its own, titled from
    its file name.
  - Tapping a card opens a gallery of all its photos (collections.js). Without
    JavaScript the card opens its cover photo.
  - Prices come from content/prices.json (edited in the admin page): whole rupees per
    photo, keyed by the photo's path under images-src/pieces/. A card shows the lowest
    price of its photos ("From ₹12,500"; one photo: "₹12,500"), the gallery shows each
    photo's price, and an unpriced photo or card shows "Price on request". With
    "show": false no prices appear anywhere on the site.

Keeps the page fast with hundreds of photos: only the cover thumbnail of each card is on
the page (lazy loaded, 300/450/600 px); the first INITIAL cards of a category are shown
and the rest wait behind "Show all"; gallery photos load only when opened.

Run tools/optimize_images.py first (it makes the WebP files this page points to).
Usage: python3 tools/build_collections.py
"""

import json
import re
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "content" / "collections.json"
PRICES = ROOT / "content" / "prices.json"
PAGE = ROOT / "collections.html"
SRC = ROOT / "images-src" / "pieces"
OUT = ROOT / "assets" / "img" / "pieces"
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
INITIAL = 8
THUMBS = (300, 450, 600)
LARGE = 1080
SIZES = "(min-width: 1200px) 280px, (min-width: 960px) 22vw, (min-width: 640px) 30vw, 46vw"
PREFIX = "assets/img/pieces/"
ON_REQUEST = "Price on request"


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "photo"


def natural(path):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", path.stem.lower())]


def title_from(name):
    name = re.sub(r"^\d+[\s._-]+", "", name)
    words = re.sub(r"[-_]+", " ", name).split()
    return " ".join(w if w.isupper() else w.capitalize() for w in words) or name


def photos_in(folder):
    """Photos in name order; one named "cover..." comes first and is the card cover."""
    photos = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in EXTENSIONS]
    return sorted(photos, key=lambda p: (not p.stem.lower().startswith("cover"), natural(p)))


def rupees(amount):
    """Whole rupees with Indian digit grouping: 125000 -> "₹1,25,000"."""
    digits = str(int(amount))
    head, tail = digits[:-3], digits[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    return "₹" + ",".join(([head] if head else []) + groups + [tail])


def load_prices():
    """{photo path under images-src/pieces: rupees}, or None when prices are switched off."""
    if not PRICES.exists():
        return {}
    data = json.loads(PRICES.read_text(encoding="utf-8"))
    if not data.get("show", True):
        return None
    return {k: int(v) for k, v in (data.get("prices") or {}).items() if isinstance(v, int) and v > 0}


def web_path(src):
    """Path of a photo's WebP files under assets/img/pieces/, without the -<width> suffix."""
    rel = src.relative_to(SRC)
    return "/".join([slugify(p) for p in rel.parent.parts] + [slugify(rel.stem)])


def collect(folder, prices):
    """Cards of one category: (title, [photo web paths], [price or None per photo])."""
    def card_of(title, photos):
        keys = [p.relative_to(SRC).as_posix() for p in photos]
        return title, [web_path(p) for p in photos], [prices.get(k) if prices else None for k in keys]

    cards = []
    for sub in sorted((d for d in folder.iterdir() if d.is_dir()), key=natural):
        photos = photos_in(sub)
        if photos:
            cards.append(card_of(title_from(sub.name), photos))
    for photo in photos_in(folder):
        cards.append(card_of(title_from(photo.stem), [photo]))
    return cards


def card_price(amounts):
    known = [a for a in amounts if a]
    if not known:
        return ON_REQUEST
    return rupees(min(known)) if len(amounts) == 1 else "From " + rupees(min(known))


def card(title, photos, amounts, category, hidden, show_prices):
    base = PREFIX + photos[0]
    srcset = ", ".join(f"{base}-{w}.webp {w}w" for w in THUMBS)
    more = " piece--more" if hidden else ""
    count = len(photos)
    label = f"{count} photo" + ("" if count == 1 else "s")
    price, data = "", ""
    if show_prices:
        price = f'<span class="piece__price">{escape(card_price(amounts))}</span>'
        data = f' data-prices="{escape("|".join(rupees(a) if a else "" for a in amounts))}"'
    return (
        f'<li class="card piece{more}"><a class="card__inner piece__link" href="{base}-{LARGE}.webp" '
        f'data-gallery="{escape("|".join(photos))}"{data}>'
        f'<img src="{base}-{THUMBS[0]}.webp" srcset="{srcset}" sizes="{SIZES}" width="600" height="750" '
        f'loading="lazy" decoding="async" alt="{escape(title)} — {escape(category)}">'
        f'<span class="piece__body"><h3>{escape(title)}</h3>{price}<span class="piece__count">{label}</span></span></a></li>'
    )


def section(num, cat, cards, show_prices):
    cid = escape(cat["id"])
    photos = sum(len(p) for _t, p, _a in cards)
    label = f"{photos} design" + ("" if photos == 1 else "s")
    items = "\n          ".join(
        card(t, p, a, cat["title"], i >= INITIAL, show_prices) for i, (t, p, a) in enumerate(cards)
    )
    if cards:
        body = f'<ul class="piece-grid" id="{cid}-grid" role="list">\n          {items}\n        </ul>'
    else:
        body = '<p class="collection__empty">New designs coming soon.</p>'
    button = ""
    if len(cards) > INITIAL:
        button = (
            f'\n        <button class="btn btn--outline more-btn" type="button" data-more '
            f'aria-controls="{cid}-grid" hidden>Show all {len(cards)}</button>'
        )
    intro = f"\n          <p>{escape(cat['intro'])}</p>" if cat.get("intro") else ""
    return f"""<section class="collection" id="{cid}" aria-labelledby="{cid}-title">
      <div class="container">
        <header class="section-title">
          <span class="section-title__num" aria-hidden="true">{num}</span>
          <div>
            <span class="eyebrow">{label}</span>
            <h2 id="{cid}-title">{escape(cat['title'])}</h2>
          </div>{intro}
        </header>
        {body}{button}
      </div>
    </section>"""


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    page = PAGE.read_text(encoding="utf-8")
    prices = load_prices()
    categories = list(data["categories"])
    known = {c["id"] for c in categories}
    if SRC.exists():
        for folder in sorted(d for d in SRC.iterdir() if d.is_dir()):
            if folder.name not in known:
                categories.append({"id": slugify(folder.name), "folder": folder.name, "title": title_from(folder.name)})

    problems, total = [], 0
    for num, cat in enumerate(categories, 1):
        folder = SRC / cat.get("folder", cat["id"])
        cards = collect(folder, prices) if folder.is_dir() else []
        for _t, photos, _a in cards:
            for p in photos:
                if not (OUT / f"{p}-{THUMBS[0]}.webp").exists():
                    problems.append(f"{p}: no WebP yet, run tools/optimize_images.py first")
        total += sum(len(p) for _t, p, _a in cards)
        html = section(num, cat, cards, prices is not None)
        pattern = re.compile(rf'<section class="collection" id="{re.escape(cat["id"])}".*?</section>', re.S)
        if pattern.search(page):
            page = pattern.sub(lambda _m, h=html: h, page, count=1)
        else:  # new category: add it after the last collection section
            last = list(re.finditer(r'<section class="collection" id="[^"]+".*?</section>', page, re.S))[-1]
            page = page[: last.end()] + "\n    " + html + page[last.end():]

    # Categories that were removed (no JSON entry and no folder): drop their sections
    wanted = {c["id"] for c in categories}
    for m in list(re.finditer(r'\n\s*<section class="collection" id="([^"]+)".*?</section>', page, re.S)):
        if m.group(1) not in wanted:
            page = page.replace(m.group(0), "", 1)

    nav = "\n".join(f'          <li><a href="#{escape(c["id"])}">{escape(c["title"])}</a></li>' for c in categories)
    page = re.sub(r'(<nav class="category-nav"[^>]*>\s*<div class="container">\s*<ul>\n).*?(\n\s*</ul>)',
                  lambda m: m.group(1) + nav + m.group(2), page, count=1, flags=re.S)
    if problems:
        sys.exit("\n".join(problems))
    PAGE.write_text(page, encoding="utf-8")
    shown = "prices hidden" if prices is None else f"{len(prices)} prices"
    print(f"collections.html: {len(categories)} categories, {total} photos, {shown}")


if __name__ == "__main__":
    main()
