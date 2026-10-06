#!/usr/bin/env python3
"""Static audit of the site against the project constitution.

Checks every top-level HTML page for:
  - images: WebP only, files exist, width/height/alt present, lazy loading
    (loading="lazy" + decoding="async") on everything except the hero
  - local links and assets resolve to real files (and #anchors exist)
  - WhatsApp: every page has a wa.me link and all links use one number
  - no motion: no animation/transition/@keyframes/marquee/autoplay/smooth scroll
  - no third-party scripts, stylesheets or fonts
  - size budgets for HTML, CSS, JS and image variants

Usage: python3 tools/check_site.py      (exit code 1 on any failure)
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
KB = 1024
BUDGETS = {
    "html": 40 * KB,
    "css": 25 * KB,
    "js": 10 * KB,
    "image": 120 * KB,
    "hero": 250 * KB,
}
MOTION_CSS = re.compile(r"\b(animation|transition)\s*:|@keyframes|scroll-behavior\s*:\s*smooth", re.I)
WA_LINK = re.compile(r"^https://wa\.me/(\d+)(\?text=.*)?$")

errors = []


def fail(where, message):
    errors.append(f"{where}: {message}")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.imgs, self.links, self.ids, self.scripts, self.styles = [], [], set(), [], []
        self.wa_numbers, self.tags = [], []
        self.in_picture = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append(tag)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "picture":
            self.in_picture = True
        if tag == "img":
            self.imgs.append(a)
        if tag == "source" and self.in_picture:
            self.imgs.append({**a, "_source": True})
        if tag == "a" and "href" in a:
            self.links.append(a["href"])
        if tag == "link" and "href" in a:
            self.styles.append(a["href"])
        if tag == "script" and "src" in a:
            self.scripts.append(a["src"])
        for key in ("autoplay",):
            if key in a:
                fail(self.name, f"<{tag}> uses '{key}' (no motion allowed)")
        if "data-wa-number" in a:
            self.wa_numbers.append(a["data-wa-number"])

    def handle_endtag(self, tag):
        if tag == "picture":
            self.in_picture = False


def srcset_urls(value):
    return [part.strip().split()[0] for part in value.split(",") if part.strip()]


def check_local(page_name, url, ids_by_page):
    parsed = urlparse(url)
    if parsed.scheme or url.startswith("//"):
        return
    target = parsed.path or page_name
    path = ROOT / target
    if not path.exists():
        fail(page_name, f"broken local link/asset '{url}'")
        return
    if parsed.fragment and target in ids_by_page and parsed.fragment not in ids_by_page[target]:
        fail(page_name, f"anchor '#{parsed.fragment}' not found in {target}")


def main():
    pages = sorted(ROOT.glob("*.html"))
    if not pages:
        sys.exit("No HTML pages found.")
    parsed = {}
    for page in pages:
        p = Page()
        p.name = page.name
        text = page.read_text(encoding="utf-8")
        p.feed(text)
        parsed[page.name] = (p, text)

    ids_by_page = {name: p.ids for name, (p, _) in parsed.items()}
    numbers = set()

    for name, (p, text) in parsed.items():
        size = len(text.encode("utf-8"))
        if size > BUDGETS["html"]:
            fail(name, f"HTML is {size / KB:.1f} KB (budget {BUDGETS['html'] // KB} KB)")
        if "<marquee" in text.lower():
            fail(name, "uses <marquee>")
        if "<video" in text.lower():
            fail(name, "uses <video> (no motion allowed)")
        if MOTION_CSS.search(text):
            fail(name, "inline CSS contains animation/transition/keyframes")

        # Images
        for img in p.imgs:
            urls = srcset_urls(img.get("srcset", "")) + ([img["src"]] if "src" in img else [])
            for url in urls:
                if not url.lower().endswith(".webp"):
                    fail(name, f"image '{url}' is not WebP")
                check_local(name, url, ids_by_page)
            if img.get("_source"):
                continue
            label = img.get("src", "?")
            if "width" not in img or "height" not in img:
                fail(name, f"<img {label}> missing width/height")
            if "alt" not in img:
                fail(name, f"<img {label}> missing alt")
            is_hero = img.get("fetchpriority") == "high"
            if not is_hero:
                if img.get("loading") != "lazy":
                    fail(name, f"<img {label}> is not lazy loaded")
                if img.get("decoding") != "async":
                    fail(name, f"<img {label}> missing decoding=\"async\"")
            elif img.get("loading") == "lazy":
                fail(name, f"hero <img {label}> must not be lazy loaded")

        # Links & assets
        page_has_wa = False
        for href in p.links:
            m = WA_LINK.match(href)
            if href.startswith("https://wa.me"):
                if not m:
                    fail(name, f"malformed WhatsApp link '{href[:60]}'")
                    continue
                page_has_wa = True
                numbers.add(m.group(1))
            elif not href.startswith(("http://", "https://", "mailto:", "tel:")):
                check_local(name, href, ids_by_page)
        numbers.update(p.wa_numbers)
        if not page_has_wa:
            fail(name, "no WhatsApp link on page")
        if 'class="wa-float"' not in text:
            fail(name, "floating WhatsApp button missing")

        for url in p.scripts + p.styles:
            if urlparse(url).scheme or url.startswith("//"):
                fail(name, f"third-party resource '{url}' (not allowed)")
            else:
                check_local(name, url, ids_by_page)

    if len(numbers) > 1:
        fail("WhatsApp", f"multiple numbers in use: {sorted(numbers)}")

    # CSS / JS
    css_total = 0
    for css in (ROOT / "assets" / "css").glob("*.css"):
        text = css.read_text(encoding="utf-8")
        css_total += len(text.encode())
        stripped = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
        for m in MOTION_CSS.finditer(stripped):
            line = stripped[: m.start()].count("\n") + 1
            fail(css.name, f"motion rule '{m.group(0)}' near line {line}")
        if "@import" in stripped:
            fail(css.name, "@import is not allowed (extra request)")
    if css_total > BUDGETS["css"]:
        fail("CSS", f"{css_total / KB:.1f} KB (budget {BUDGETS['css'] // KB} KB)")

    js_total = sum(len(f.read_bytes()) for f in (ROOT / "assets" / "js").glob("*.js"))
    if js_total > BUDGETS["js"]:
        fail("JS", f"{js_total / KB:.1f} KB (budget {BUDGETS['js'] // KB} KB)")
    for js in (ROOT / "assets" / "js").glob("*.js"):
        if re.search(r"requestAnimationFrame|\.animate\(|setInterval", js.read_text(encoding="utf-8")):
            fail(js.name, "script appears to animate (requestAnimationFrame/animate/setInterval)")

    # Image files
    img_root = ROOT / "assets" / "img"
    count = 0
    for img in img_root.rglob("*"):
        if not img.is_file():
            continue
        count += 1
        rel = img.relative_to(ROOT)
        if img.suffix.lower() != ".webp":
            fail(str(rel), "non-WebP file in assets/img")
        budget = BUDGETS["hero"] if img.parent.name == "hero" else BUDGETS["image"]
        if img.stat().st_size > budget:
            fail(str(rel), f"{img.stat().st_size / KB:.0f} KB (budget {budget // KB} KB)")

    print(f"Checked {len(pages)} pages, {count} image files, CSS {css_total / KB:.1f} KB, JS {js_total / KB:.1f} KB")
    if errors:
        print(f"\n{len(errors)} problem(s):")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    print("✓ All checks passed")


if __name__ == "__main__":
    main()
