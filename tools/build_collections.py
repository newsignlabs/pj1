#!/usr/bin/env python3
"""Build the collection sections of collections.html from content/collections.json.

Each category in the JSON becomes one <section class="collection" id="..."> and replaces
the section with the same id in collections.html (add a new category by first copying a
section in the HTML, then adding it to the JSON). Everything else on the page is left
alone.

Per piece the JSON needs "image" (the slug of images-src/pieces/<slug>.jpg) and "name"
(the title shown on the card, e.g. a sub-collection such as "Antique Premium"); "alt"
describes the photo and is optional (it defaults to the name). Cards show the title only.

To keep the page fast with hundreds of photos:
  - every thumbnail is lazy loaded and offered at 300/450/600 px;
  - only the first INITIAL pieces of a category are shown; the rest are revealed by a
    "Show all" button (main.js). Hidden thumbnails are never downloaded. Without
    JavaScript every piece is shown, still lazy loaded;
  - each card links to the 1080 px image, which main.js opens in a viewer only on tap.

Usage: python3 tools/build_collections.py   (then run tools/optimize_images.py for new photos)
"""

import json
import re
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "content" / "collections.json"
PAGE = ROOT / "collections.html"
SRC = ROOT / "images-src" / "pieces"
INITIAL = 8
THUMBS = (300, 450, 600)
LARGE = 1080
SIZES = "(min-width: 1200px) 280px, (min-width: 960px) 22vw, (min-width: 640px) 30vw, 46vw"


def card(piece, hidden):
    slug = piece["image"]
    base = f"assets/img/pieces/{slug}"
    srcset = ", ".join(f"{base}-{w}.webp {w}w" for w in THUMBS)
    name = escape(piece["name"])
    alt = escape(piece.get("alt") or piece["name"])
    more = " piece--more" if hidden else ""
    return (
        f'<li class="card piece{more}"><a class="card__inner piece__link" href="{base}-{LARGE}.webp" data-zoom>'
        f'<img src="{base}-{THUMBS[0]}.webp" srcset="{srcset}" sizes="{SIZES}" width="600" height="750" '
        f'loading="lazy" decoding="async" alt="{alt}">'
        f'<span class="piece__body"><h3>{name}</h3></span></a></li>'
    )


def section(num, cat):
    pieces = cat["pieces"]
    cid = escape(cat["id"])
    count = len(pieces)
    label = f"{count} design" + ("" if count == 1 else "s")
    cards = "\n          ".join(card(p, i >= INITIAL) for i, p in enumerate(pieces))
    button = ""
    if count > INITIAL:
        button = (
            f'\n        <button class="btn btn--outline more-btn" type="button" data-more '
            f'aria-controls="{cid}-grid" hidden>Show all {count} designs</button>'
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
        <ul class="piece-grid" id="{cid}-grid" role="list">
          {cards}
        </ul>{button}
      </div>
    </section>"""


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    page = PAGE.read_text(encoding="utf-8")
    problems = []
    for num, cat in enumerate(data["categories"], 1):
        for p in cat["pieces"]:
            if not any((SRC / f"{p['image']}{ext}").exists() for ext in (".jpg", ".jpeg", ".png", ".webp")):
                problems.append(f"{cat['id']}: no photo images-src/pieces/{p['image']}.jpg")
        pattern = re.compile(rf'<section class="collection" id="{re.escape(cat["id"])}".*?</section>', re.S)
        if not pattern.search(page):
            problems.append(f'{cat["id"]}: no <section class="collection" id="{cat["id"]}"> in collections.html')
            continue
        page = pattern.sub(lambda _m, n=num, c=cat: section(n, c), page, count=1)
    if problems:
        sys.exit("\n".join(problems))
    PAGE.write_text(page, encoding="utf-8")
    total = sum(len(c["pieces"]) for c in data["categories"])
    print(f"collections.html: {len(data['categories'])} categories, {total} pieces")


if __name__ == "__main__":
    main()
