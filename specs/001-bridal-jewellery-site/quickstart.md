# Quickstart: Bridal Jewellery Showcase Website

## Preview locally

```bash
python3 -m http.server 8080
# open http://localhost:8080
```

## Replace the images with real photos

```bash
pip install Pillow
# put originals in images-src/<group>/<slug>.jpg (same names as the placeholders)
python3 tools/optimize_images.py          # writes assets/img/**/*.webp
python3 tools/check_site.py               # verify budgets, lazy loading, links
```

Adding a new piece: add `images-src/pieces/<slug>.jpg`, run the optimiser, then copy an
existing `<article class="piece">` block in `collections.html` and change the slug, name,
description, alt text and WhatsApp message.

## Set the WhatsApp number

The placeholder `919876543210` is used in every link. Replace it site-wide:

```bash
grep -rl 919876543210 --include=*.html . | xargs sed -i 's/919876543210/<your number>/g'
```

Also update the human-readable `+91 98765 43210` text in the same files.

## Validate

```bash
python3 tools/check_site.py
```

Then check pages at 360px, 768px and 1280px widths in browser dev tools and run a
Lighthouse mobile audit.

## Deploy

Upload the repository root (excluding `images-src/`, `tools/`, `specs/`, `.specify/`,
`.claude/`) to any static host, or point GitHub Pages / Netlify / Cloudflare Pages at the
branch root.
