#!/usr/bin/env python3
"""Add a content version to every CSS and JS link in the HTML pages (and the admin page).

    <link rel="stylesheet" href="assets/css/styles.css?v=3f9a1c2b">

The version is the first 8 hex digits of the file's SHA-1, so it changes only when the
file changes. Browsers and phones that cached the old file then fetch the new one at
once instead of waiting for their cache to expire. tools/check_site.py fails if a
version is missing or out of date, so run this after editing CSS or JS.

Usage: python3 tools/stamp_assets.py
"""
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Local CSS/JS files, relative to the page ("assets/css/styles.css", "admin.js")
PATTERN = re.compile(r'((?:href|src)=")([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:css|js))(\?v=[0-9a-f]*)?(")')


def pages():
    return sorted(ROOT.glob("*.html")) + [ROOT / "admin" / "index.html"]


def stamp(text, folder=ROOT):
    def repl(m):
        file = folder / m.group(2)
        if not file.is_file():
            return m.group(0)
        return f"{m.group(1)}{m.group(2)}?v={hashlib.sha1(file.read_bytes()).hexdigest()[:8]}{m.group(4)}"
    return PATTERN.sub(repl, text)


def stale_pages():
    """Pages whose CSS/JS versions are missing or out of date."""
    return [p.relative_to(ROOT).as_posix() for p in pages()
            if stamp(p.read_text(encoding="utf-8"), p.parent) != p.read_text(encoding="utf-8")]


def main():
    stale = stale_pages()
    for name in stale:
        page = ROOT / name
        page.write_text(stamp(page.read_text(encoding="utf-8"), page.parent), encoding="utf-8")
    print("Stamped: " + (", ".join(stale) if stale else "all pages already up to date"))


if __name__ == "__main__":
    main()
