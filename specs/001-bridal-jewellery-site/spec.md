# Feature Specification: Bridal Jewellery Showcase Website

**Feature Branch**: `001-bridal-jewellery-site`

**Created**: 2026-10-06

**Status**: Implemented (revision 9)

**Revision 2 (2026-10-06)**, from client feedback on the first build: no contact form; add a
map to the Contact page; no "Enquire on WhatsApp" buttons on every piece; use the supplied
logo; dark background in the logo's silver and pink.

**Revision 3 (2026-10-06)**: artistic rather than corporate look; the hero shows the
client's product photo (emerald and gold necklace set) in a cinematic style; cards with
clipped edges. The site is hosted on Zoho Catalyst Slate, auto-deployed from `main`.

**Revision 4 (2026-10-06)**: richer mobile experience. The logo was too small in the header
and footer; the first section becomes a manual slider (arrows, no automatic motion); more
quote sections with parallax background images; an artistic footer instead of a corporate
template.

**Revision 5 (2026-10-06)**: a more creative full-screen phone menu; some parallax quotes
become full-screen cards with embroidered borders so the page is not monotonous; a light
version with a switch in the top bar.

**Revision 6 (2026-10-07)**: the logo must look as big on desktop as on phones; the hero's
first scene uses the client's new studio photograph (black backdrop, pink smoke).

**Revision 7 (2026-10-07)**: the brand name becomes **Cute Look** everywhere; collection
card captions become a solid white strip with a clipped corner in light mode (see-through
in dark mode) instead of a white gradient; the client's photograph of a worn temple
necklace goes inside the framed quote card "Some jewels are worn. Ours are inherited."

**Revision 8 (2026-10-09)**: real business details applied on every page (Annur shop
address, phone/WhatsApp 919790112593, tagline "Bridal Collections"); "atelier" becomes
"shop"/"our shop"; Roman numerals become natural numbers; wording such as "scenes" and
"chapters" removed; copy rewritten in a light business tone, with the Our Story section
describing a new shop in Annur.

**Revision 9 (2026-10-09)**: the hero headline is set on three lines ("Bridal jewellery /
for your / special day"); the hero slider auto-advances, with redesigned controls (round
chevron arrows, progress bars, pause/play). 

**Input**: User description: "I need to create a static website for a bridal jewellery business. The website will have home, collections and Contact page. The page will have whatsapp integration so the clients send messages through website. The website will be full of images so lazy loading needs to be implemented with webp file formats. Compressed images are to be served throughout the site for fast loading. Screen height static hero banner. No motion, animation or marquee. No heavy frameworks as it is a simple frontend only site. Mobile responsive."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Browse collections and contact the business on WhatsApp (Priority: P1)

A bride-to-be (or a family member) opens the website on a phone, browses the bridal
collections and finds pieces she likes. She taps the WhatsApp button and sends the business
a message naming the pieces.

**Why this priority**: This is the business outcome of the site: turning browsing into a
conversation with the jeweller. Collections plus WhatsApp is a viable MVP alone.

**Independent Test**: Open the Collections page on a phone, tap the floating WhatsApp button,
and confirm WhatsApp opens a chat with the business number and a greeting pre-filled.

**Acceptance Scenarios**:

1. **Given** a visitor on any page, **When** they tap the WhatsApp button, **Then** WhatsApp
   (app on mobile, web/desktop app on computer) opens a chat with the business number and a
   short greeting pre-filled.
2. **Given** a visitor on the Collections page, **When** they choose a category
   (e.g. Necklaces), **Then** they are taken directly to that category's pieces.
3. **Given** a visitor scrolling a long collection on mobile data, **When** images come into
   view, **Then** each image appears without the page jumping, and images further down
   are not downloaded until the visitor approaches them.
4. **Given** a visitor browsing pieces, **Then** each piece shows only its image, name and
   description, with no per-piece buttons.

---

### User Story 2 - First impression on the Home page (Priority: P2)

A visitor arrives on the Home page and sees a full-screen, still hero image of bridal
jewellery with the business name, a short promise and clear buttons to view collections or
chat on WhatsApp. Scrolling down shows featured collections, the business's story and
highlights, and a final call to action.

**Why this priority**: The Home page sets the brand impression and routes visitors to the
Collections page or WhatsApp, but the enquiry flow (P1) delivers value without it.

**Independent Test**: Open the Home page on phone and desktop; confirm the hero fills exactly
one screen height, nothing moves, and both buttons lead to the right destinations.

**Acceptance Scenarios**:

1. **Given** a visitor opens the Home page, **When** it loads, **Then** a single still hero
   image fills the visible screen height with the heading and two calls to action
   ("View Collections", "Visit the Showroom") readable on top of it.
2. **Given** the Home page is displayed, **When** the visitor waits, **Then** nothing moves;
   the hero changes scene only when the visitor swipes or taps an arrow, instantly.
3. **Given** a visitor scrolling past a quote section, **Then** its background drifts slower
   than the page (parallax); **Given** the device asks for reduced motion, **Then** it stays
   still.
3. **Given** a visitor on the Home page, **When** they tap a featured collection,
   **Then** they land on that collection's section of the Collections page.

---

### User Story 3 - Find and contact the showroom (Priority: P3)

A visitor wants to visit the store or ask a question. On the Contact page they see the
WhatsApp number, phone, email, address, opening hours and a map of the showroom location.

**Why this priority**: Showroom visits matter, but WhatsApp is already reachable from every
page, so this page completes rather than enables the core flow.

**Independent Test**: Open the Contact page; confirm the map shows the showroom, "Open in
Google Maps" gives directions, and the phone, email and WhatsApp links open the right apps.

**Acceptance Scenarios**:

1. **Given** a visitor on the Contact page, **When** they scroll to the map, **Then** an
   interactive map centred on the showroom address loads.
2. **Given** a visitor on the Contact page, **When** they tap "Open in Google Maps" or
   "Get directions", **Then** Google Maps opens with the showroom address.
3. **Given** a visitor on the Contact page, **When** they tap the phone number, email or
   WhatsApp number, **Then** their dialler, mail app or WhatsApp opens.

---

### Edge Cases

- **JavaScript disabled or failed to load**: navigation, all images and every WhatsApp link
  still work; WhatsApp links fall back to a generic or item-specific pre-filled message
  built into the link itself.
- **WhatsApp not installed (desktop)**: the link opens WhatsApp Web, which offers to open
  the desktop app or continue in the browser.
- **Browser without WebP support** (very old browsers only): images may not display; this is
  accepted given current browser support (>97% of users).
- **Very small screens (320px)** and **landscape phones**: the hero still fills one screen
  height and the heading and buttons remain visible and readable.
- **Map cannot load** (offline, blocked by an ad blocker): the address, hours and the
  "Open in Google Maps" link remain visible next to the map area.
- **Slow connection**: text and layout appear immediately; images reserve their space and
  fill in as they arrive.
- **Visitor prefers reduced motion**: nothing changes, because there is no motion anywhere.

## Requirements *(mandatory)*

### Functional Requirements

**Pages & navigation**

- **FR-001**: The site MUST have three pages: Home, Collections and Contact.
- **FR-002**: Every page MUST share a header with the business name and navigation to all
  three pages, and a footer with contact details, WhatsApp link and copyright.
- **FR-003**: On small screens the navigation MUST collapse into a menu button that opens and
  closes instantly, and MUST still be usable without JavaScript.
- **FR-004**: The current page MUST be indicated in the navigation.

**Home page**

- **FR-005**: The Home page MUST open with a static hero banner that fills exactly the
  visible screen height on all devices, presenting the client's product photograph as a
  graded, letterboxed "film still" (no motion), showing a heading, a short tagline, a
  "View Collections" button and a "Chat on WhatsApp" button.
- **FR-006**: The Home page MUST show featured collections (at least 4) linking to the
  matching section of the Collections page.
- **FR-007**: The Home page MUST include a short "about the business" section, a highlights
  section (e.g. certified quality, custom designs, bridal styling) and a closing call to
  action to visit the showroom.

**Collections page**

- **FR-008**: The Collections page MUST group pieces into categories: Bridal Sets,
  Necklaces, Earrings, Bangles & Bracelets, Maang Tikka & Headpieces, and Rings.
- **FR-009**: The Collections page MUST provide category links at the top that jump to each
  category section.
- **FR-010**: Each piece MUST show an image, name and a short description. Pieces MUST NOT
  carry individual WhatsApp buttons.
- **FR-011**: Each category MUST show at least 4 pieces.

**WhatsApp integration**

- **FR-012**: A WhatsApp action MUST be reachable on every page through a fixed,
  non-animated floating button that does not cover page content or buttons. Beyond the
  floating button, header and footer, each page has at most one in-content WhatsApp
  call to action.
- **FR-013**: WhatsApp links MUST pre-fill a short greeting.
- **FR-014**: The site MUST NOT include a contact form.
- **FR-015**: All WhatsApp actions MUST target a single, configurable business number.
- **FR-016**: The website MUST NOT collect or store visitor data.

**Contact page**

- **FR-017**: The Contact page MUST show WhatsApp number, phone (tap to call), email
  (tap to mail), store address, opening hours, and an embedded map of the showroom with
  a link that opens Google Maps for directions. The map MUST load only when scrolled near.

**Brand & art direction**

- **FR-030**: The Home hero MUST be a slider of at least three slides from the client's
  product photography that auto-advances about every 6 s, with round previous/next arrows,
  one progress bar per slide (click to jump), a pause/play button, and swipe on touch.
  Auto-advance pauses on hover, keyboard focus, touch and hidden tabs, and is off for
  reduced motion.
- **FR-031**: The Home page MUST include at least three full-width quote sections;
  Collections and Contact MUST include one each. Quote styles MUST alternate between
  parallax photo quotes and full-screen cards with an embroidered border (FR-035).
- **FR-032**: The logo MUST be prominent on every screen size (a hanging medallion of at
  least 80px on phones and 100px on desktop); the footer MUST show it as a large emblem.
- **FR-033**: The footer MUST be artistic (end-credits style), not a corporate link grid.
- **FR-034**: On phones the menu MUST open as a full-screen, artistic overlay (numbered
  scenes, embroidered frame, contact line) that traps keyboard focus, closes with Escape or
  by choosing a link, and prevents the page behind from scrolling.
- **FR-035**: Quote cards MUST fill the screen and carry an embroidered border in the
  brand's silver and pink, adapted to the active theme. A card MAY hold a photograph in an
  arched window (the Home card "Some jewels are worn…" shows the worn temple necklace).
- **FR-036**: Collection card captions MUST sit on a strip with a clipped corner: solid
  white in the light theme, see-through in the dark theme (no gradient fades).

- **FR-028**: The visual style MUST feel artistic and editorial rather than like a typical
  corporate website (display serif typography, outlined numerals, asymmetric layouts).
- **FR-029**: Collection, piece, highlight, contact and map cards MUST have clipped
  (chamfered) corners.

- **FR-026**: The supplied logo MUST appear in the header and footer of every page and be
  used as the favicon.
- **FR-027**: All pages MUST use a dark theme by default with the logo's silver and pink as
  accent colours. A light theme MUST be available from a switch in the top bar on every
  page, apply instantly without a flash on reload, and be remembered on the device.

**Images & performance**

- **FR-018**: All content images MUST be served in WebP format, compressed.
- **FR-019**: All images except the hero MUST be lazy loaded so they are only fetched when
  approaching the viewport.
- **FR-020**: Each image MUST be available in multiple sizes and the browser MUST pick the
  smallest suitable size for the device.
- **FR-021**: Images MUST reserve their space before loading so the page does not shift.
- **FR-022**: The project MUST include a repeatable process for turning new original photos
  into compressed WebP images in the required sizes.

**Presentation constraints**

- **FR-023**: Nothing on the site may move on its own (no autoplay, auto-advancing
  carousel, marquee, looping/entrance animation, transitions or video). Allowed: the manual
  hero slider (instant changes) and scroll-linked parallax on quote backgrounds, which is
  disabled for reduced-motion users.
- **FR-024**: The site MUST be fully responsive from 320px to wide desktop screens without
  horizontal scrolling.
- **FR-025**: The site MUST be built without heavy frameworks and run without a server
  backend.

### Key Entities

- **Collection (category)**: A group of pieces; has a name, short description, anchor
  identifier and cover image.
- **Piece**: A jewellery item shown on the Collections page; has a name, short description,
  collection, and image.
- **Greeting message**: The short text pre-filled into WhatsApp links.
- **Business contact details**: WhatsApp number, phone, email, address, opening hours,
  map location.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A visitor can open a WhatsApp chat with the business from any page in one tap.
- **SC-002**: On a mid-range phone over a 4G connection, the Home page's hero and heading are
  visible within 2.5 seconds.
- **SC-003**: Opening the Collections page downloads no more than the images visible in the
  first screen plus a small look-ahead margin; total initial page weight on mobile stays
  under 500 KB.
- **SC-004**: No visible layout shift occurs as images load (layout shift score below 0.1).
- **SC-005**: All pages score 90 or higher for performance and accessibility in a standard
  mobile page-quality audit.
- **SC-006**: All three pages display correctly with no horizontal scrolling at 320px, 360px,
  768px, 1024px and 1440px widths.
- **SC-007**: Zero elements move without visitor input (the hero changes only on swipe or
  arrow; quote parallax only while scrolling, and never with reduced motion).

## Assumptions

- The business name is **Cute Look** (shown as "Cute Look Bridal Jewels"; it replaced the
  first-release placeholder "Aurelia" in revision 7). Copy, prices, contact details and most
  product photography are still placeholders, designed to be replaced without code changes
  beyond content edits.
- Prices are not shown; pricing is discussed on WhatsApp (common for bridal jewellery).
- Content is in English only.
- The catalogue is small enough (tens of pieces) to be maintained by editing HTML directly;
  no content management system is needed.
- The site will be hosted on a standard static host (e.g. GitHub Pages, Netlify,
  Cloudflare Pages) that serves files over HTTPS with compression enabled.
- Visitors use modern browsers released within the last ~4 years (all support WebP and
  native lazy loading).
