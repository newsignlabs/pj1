# Cute Look Bridal Collections — static website

A fast, image-led brochure website for a bridal jewellery business: **Home**,
**Collections** and **Contact** pages. Dark theme in the logo's silver and pink, with
WhatsApp as the way to get in touch.

- Plain HTML, one CSS file (~16 KB) and one small JS file (~3 KB). No frameworks, no build step.
- Every image is compressed **WebP** in several sizes (`srcset`), **lazy loaded**, with
  fixed dimensions so the page never jumps while loading.
- Full-screen, always-dark hero slider: three portrait photos that melt into black (top of
  the screen on phones, on the right on wide screens) and change every 6 s (stops on hover,
  touch or focus, and for visitors who ask for reduced motion), with progress-bar
  indicators and swipe on phones.
- Quote interludes that alternate between soft-focus photo quotes with scroll-linked
  parallax (off for visitors who ask for reduced motion) and full-screen cards with an
  embroidered border.
- Dark theme by default, with a light (ivory) theme from the switch in the top bar,
  remembered on the device.
- On phones the menu opens as a full-screen, embroidered "programme" of scenes.
- Logo as a hanging medallion in the header on phones, and an end-credits footer with a
  large ringed emblem.
- Artistic, editorial design: self-hosted Cormorant Garamond, outlined chapter numerals,
  staggered layouts and rounded cards.
- Mobile-first and responsive from 320px phones to wide desktops.
- WhatsApp click-to-chat (`wa.me`) through a floating button on every page, plus the
  header, footer and Contact page. No contact form; nothing is stored.
- Contact page with opening hours and a Google Maps embed that loads only when scrolled to.

> **Placeholder content:** the brand name, copy, contact details, map address, WhatsApp
> number and product images are placeholders (the logo is the real one). Replace them before going live (see below).

## Project layout

```text
index.html, collections.html, contact.html, 404.html   pages
assets/css/styles.css      all styles (mobile-first)
assets/js/main.js          mobile menu toggle (optional enhancement)
assets/fonts/              Cormorant Garamond WOFF2 (self-hosted, SIL OFL)
assets/img/                generated WebP images: do not edit by hand
assets/icons/              favicon-32.png, apple-touch-icon.png (built from the logo)
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
   (e.g. `images-src/pieces/necklaces-1.jpg`).
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

### Hero photo, scenes and quote backgrounds

Scene I of the hero is the studio photograph `images-src/hero/hero-studio.jpg` (lit on
black with pink smoke); it only gets an edge vignette. The close-up scenes and the quote
backgrounds are cut from the original product photo, `images-src/hero/hero-photo.jpg`.
To change either, replace the file and run:

```bash
python3 tools/grade_hero.py          # writes images-src/hero/*.jpg and images-src/quotes/*.jpg
python3 tools/optimize_images.py     # writes the WebP variants
```

The script crops each frame (full set, earrings close-up, pendant close-up, and three
square close-ups for quotes), mutes the background, adds a filmic curve and vignette, and
softly blurs the quote frames. If a new photo is framed differently, adjust the crop boxes
in `FRAMES` at the top of `tools/grade_hero.py`. Adding more product photos later can give
each slide and quote its own picture.

### Logo

The logo source is `images-src/brand/logo.png` (drawn on black). After replacing it, run:

```bash
python3 tools/build_brand_assets.py
```

This turns the black background transparent and writes `assets/img/brand/logo-{64,128,256}.webp`,
`assets/icons/favicon-32.png` and `assets/icons/apple-touch-icon.png`.

### Adding photos to Collections (folders)

Photos live in one folder per category and sub-collection:

```text
images-src/pieces/
  bridal-sets/            <- category (its title and intro are in content/collections.json)
    antique/              <- sub-collection = one card titled "Antique"
      cover.jpg           <- card cover (optional; otherwise the first photo by name)
      temple-necklace-set.jpg
      IMG_0912.jpg
    antique-premium/      <- card "Antique Premium"
  necklaces/
  ...
```

- Each sub-collection folder becomes one card; its name is the card title
  (`antique-premium` → "Antique Premium"). A number prefix (`1-antique`, `2-classic`) sets
  the order and is not shown.
- Tapping a card opens a gallery of all its photos (arrows, thumbnails, swipe).
- A new category folder appears automatically at the end of the page; add it to
  `content/collections.json` to set its title, intro and position.
- Photos can be JPG, PNG, WebP or HEIC (iPhone). Any size; tall photos are shown whole in
  the gallery and cropped to 4:5 for the card. Deleting a photo removes it from the site.

**Quick upload (no tools needed):** on github.com open the sub-collection folder, for example
`images-src/pieces/bridal-sets/antique/`, choose **Add file → Upload files**, drop the photos
and commit to `main`. For a new sub-collection, open the category folder instead and drag a
whole folder of photos onto the upload page; GitHub keeps the folder name. To remove a
photo, open it on github.com and delete the file.

The **Build collections from photo folders** workflow (`.github/workflows/build-collections.yml`)
then makes the WebP images, rebuilds `collections.html` and commits them; Catalyst Slate
publishes the site, usually within two or three minutes. (GitHub Actions must be enabled
for the repository, and `main` must accept pushes from the workflow.)

**On a computer with Python:** copy photos into the folders and run

```bash
python3 tools/optimize_images.py --prune   # WebP thumbnails + gallery photos; drops deleted ones
python3 tools/build_collections.py         # rewrites the collection sections of collections.html
python3 tools/check_site.py
```

## WhatsApp number and contact details

All WhatsApp and phone links use `919790112593` (country code + number, digits only).
To change it everywhere:

```bash
sed -i 's/919790112593/91XXXXXXXXXX/g' *.html
sed -i 's/+91 97901 12593/+91 XXXXX XXXXX/g' *.html
```

Also update the email (`hello@cutelookbridal.example`), address, opening hours and brand
name in the HTML files.

## Map

The Contact page map is a Google Maps embed driven by the address text. In `contact.html`,
replace the encoded address in both the `<iframe src="https://www.google.com/maps?q=…&amp;output=embed">`
and the "Open in Google Maps" / "Get directions" links. Tip: in Google Maps, search for the
business listing and use its exact name and address (e.g. `Cute Look Bridal Collections, Main Bazaar, Jaipur`)
so the pin lands on the shop.

## Browser caching

CSS and JS links carry a content version (`styles.css?v=3f9a1c2b`). After editing CSS or
JS, run `python3 tools/stamp_assets.py` (the site check fails until you do; the GitHub
workflow does it automatically for edits made on github.com). Visitors' browsers then load
the new files on their next visit instead of showing a cached old design. When replacing a
photo, give the new file a new name so phones don't keep the old image.

## Quality checks

```bash
python3 tools/check_site.py
```

This checks that images are WebP, lazy loaded (except the hero), have dimensions and alt text;
that local links and anchors work; that every page has WhatsApp links using one
number; that the only iframe is the lazy-loaded Google Maps embed; that there is no
animation/transition CSS or third-party scripts; and that HTML,
CSS, JS and images stay within their size budgets. The full rules are in
[`.specify/memory/constitution.md`](.specify/memory/constitution.md).

## Deploying

The live site is hosted on **Zoho Catalyst Slate** (static framework, root `./`), which
auto-deploys every push to `main`. Merge a pull request into `main` and Slate rebuilds the
site within a minute.

Any other static host also works: upload the pages, `assets/`, `robots.txt` and
`_headers`. `images-src/`, `tools/`, `specs/`, `.specify/` and `.claude/` are not needed on
the server. `_headers` sets caching and security headers on Netlify and Cloudflare Pages.

## Spec Kit

The project was planned with [GitHub Spec Kit](https://github.com/github/spec-kit):

- Constitution: `.specify/memory/constitution.md`
- Feature 001 spec, plan, research, contracts and tasks: `specs/001-bridal-jewellery-site/`
- Claude Code skills: `/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-implement`, …
