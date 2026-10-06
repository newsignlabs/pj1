# Aurelia Bridal Jewels — static website

A fast, image-led brochure website for a bridal jewellery business: **Home**,
**Collections** and **Contact** pages, with WhatsApp enquiries throughout.

- Plain HTML, one CSS file (~16 KB) and one small JS file (~3 KB). No frameworks, no build step.
- Every image is compressed **WebP** in several sizes (`srcset`), **lazy loaded**, with
  fixed dimensions so the page never jumps while loading.
- Static full-screen hero banner. **No animation, transitions, sliders or marquees.**
- Mobile-first and responsive from 320px phones to wide desktops.
- WhatsApp click-to-chat links (`wa.me`) with pre-filled messages for every piece, plus a
  contact form that writes the visitor's details into a WhatsApp message. Nothing is stored.

> **Placeholder content:** the brand name, copy, contact details, WhatsApp number and
> images are placeholders. Replace them before going live (see below).

## Project layout

```text
index.html, collections.html, contact.html, 404.html   pages
assets/css/styles.css      all styles (mobile-first)
assets/js/main.js          mobile menu + contact form → WhatsApp (optional enhancement)
assets/img/                generated WebP images: do not edit by hand
assets/icons/favicon.svg
images-src/                original photos (input to the image optimiser)
tools/                     image tools and site audit (Python)
specs/, .specify/, .claude/  Spec Kit: constitution, spec, plan and tasks
```

## Preview locally

```bash
python3 -m http.server 8080
# then open http://localhost:8080
```

## Images

Requires Python 3.10+ and Pillow (`pip install Pillow`).

1. Put the original photo in `images-src/<group>/<slug>.jpg`. Groups are `hero`, `collections`,
   `pieces` and `about`. To replace a placeholder, reuse its file name
   (e.g. `images-src/pieces/kundan-choker.jpg`).
2. Run the optimiser:

   ```bash
   python3 tools/optimize_images.py           # only re-encodes changed sources
   python3 tools/optimize_images.py --force   # re-encode everything
   ```

   Each image is centre-cropped (pieces and collections 4:5, hero 16:9 landscape and 9:16 portrait),
   resized to several widths and saved as WebP at quality 72. Files over budget
   (120 KB, or 250 KB for the hero) are re-encoded at lower quality automatically.
3. Photos look best when the jewellery sits in the centre of the frame. For the hero,
   keep the left side (landscape) or the top half (portrait) fairly plain, because the
   headline is placed there.

`tools/generate_placeholders.py` recreates the placeholder artwork if needed.

### Adding a piece

1. Add `images-src/pieces/<new-slug>.jpg` and run the optimiser.
2. In `collections.html`, copy an existing `<article class="piece">` block inside the right
   collection and update the image paths, `alt` text, name, description and WhatsApp
   message (the text after `?text=` is URL-encoded; spaces are `%20`).

## WhatsApp number and contact details

All WhatsApp links use the placeholder number `919876543210` (country code + number,
digits only). Replace it everywhere:

```bash
sed -i 's/919876543210/91XXXXXXXXXX/g' *.html
sed -i 's/+91 98765 43210/+91 XXXXX XXXXX/g' *.html
```

Also update the email (`hello@aureliabridal.example`), address, opening hours and brand
name in the HTML files.

## Quality checks

```bash
python3 tools/check_site.py
```

This checks that images are WebP, lazy loaded (except the hero), have dimensions and alt text;
that local links and anchors work; that every page has WhatsApp links using one
number; that there is no animation/transition CSS or third-party scripts; and that HTML,
CSS, JS and images stay within their size budgets. The full rules are in
[`.specify/memory/constitution.md`](.specify/memory/constitution.md).

## Deploying

Any static host works (GitHub Pages, Netlify, Cloudflare Pages, shared hosting). Upload the
pages, `assets/`, `robots.txt` and `_headers`. `images-src/`, `tools/`, `specs/`,
`.specify/` and `.claude/` are not needed on the server. `_headers` sets caching and
security headers on Netlify and Cloudflare Pages.

## Spec Kit

The project was planned with [GitHub Spec Kit](https://github.com/github/spec-kit):

- Constitution: `.specify/memory/constitution.md`
- Feature 001 spec, plan, research, contracts and tasks: `specs/001-bridal-jewellery-site/`
- Claude Code skills: `/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-implement`, …
