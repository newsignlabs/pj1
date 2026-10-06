# Feature Specification: Bridal Jewellery Showcase Website

**Feature Branch**: `001-bridal-jewellery-site`

**Created**: 2026-10-06

**Status**: Ready for planning

**Input**: User description: "I need to create a static website for a bridal jewellery business. The website will have home, collections and Contact page. The page will have whatsapp integration so the clients send messages through website. The website will be full of images so lazy loading needs to be implemented with webp file formats. Compressed images are to be served throughout the site for fast loading. Screen height static hero banner. No motion, animation or marquee. No heavy frameworks as it is a simple frontend only site. Mobile responsive."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Browse collections and enquire about a piece on WhatsApp (Priority: P1)

A bride-to-be (or a family member) opens the website on a phone, browses the bridal
collections, finds a piece she likes and taps "Enquire on WhatsApp". WhatsApp opens with
a message that already names the piece, and she sends it to the business.

**Why this priority**: This is the business outcome of the site: turning browsing into a
conversation with the jeweller. Collections plus WhatsApp enquiry is a viable MVP alone.

**Independent Test**: Open the Collections page on a phone, tap the enquiry button on any
piece, and confirm WhatsApp opens to the business number with the piece name pre-filled.

**Acceptance Scenarios**:

1. **Given** a visitor on the Collections page, **When** they tap "Enquire on WhatsApp" on
   a piece, **Then** WhatsApp (app on mobile, web/desktop app on computer) opens a chat with
   the business number and a pre-filled message containing the piece name and collection.
2. **Given** a visitor on the Collections page, **When** they choose a category
   (e.g. Necklaces), **Then** they are taken directly to that category's pieces.
3. **Given** a visitor scrolling a long collection on mobile data, **When** images come into
   view, **Then** each image appears without the page jumping, and images further down
   are not downloaded until the visitor approaches them.

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
   image fills the visible screen height with the heading and two calls to action readable
   on top of it.
2. **Given** the Home page is displayed, **When** the visitor waits or scrolls, **Then** no
   element animates, slides, fades, auto-rotates or scrolls on its own.
3. **Given** a visitor on the Home page, **When** they tap a featured collection,
   **Then** they land on that collection's section of the Collections page.

---

### User Story 3 - Contact the business (Priority: P3)

A visitor wants to book a store visit or ask a general question. On the Contact page they
see the WhatsApp number, phone, email, address and opening hours, and can fill a short
form (name, occasion/wedding date, message) that opens WhatsApp with their details composed
into a message.

**Why this priority**: General enquiries and appointments matter, but WhatsApp is already
reachable from every page, so this page completes rather than enables the core flow.

**Independent Test**: Fill the Contact form and submit; confirm WhatsApp opens with a message
containing the entered name, wedding date and message.

**Acceptance Scenarios**:

1. **Given** a visitor on the Contact page, **When** they fill name and message and submit,
   **Then** WhatsApp opens with a composed message containing those details.
2. **Given** a visitor submits the form with the required name or message empty,
   **Then** they see which field needs completing and WhatsApp does not open.
3. **Given** a visitor on the Contact page, **When** they tap the phone number or email,
   **Then** their device's dialler or mail app opens.

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
- **Special characters in form input** (accents, emoji, "&", line breaks) are preserved in
  the WhatsApp message.
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
  visible screen height on all devices, showing a heading, a short tagline, a
  "View Collections" button and a "Chat on WhatsApp" button.
- **FR-006**: The Home page MUST show featured collections (at least 4) linking to the
  matching section of the Collections page.
- **FR-007**: The Home page MUST include a short "about the business" section, a highlights
  section (e.g. certified gold, custom designs, bridal styling) and a closing WhatsApp
  call to action.

**Collections page**

- **FR-008**: The Collections page MUST group pieces into categories: Bridal Sets,
  Necklaces, Earrings, Bangles & Bracelets, Maang Tikka & Headpieces, and Rings.
- **FR-009**: The Collections page MUST provide category links at the top that jump to each
  category section.
- **FR-010**: Each piece MUST show an image, name and a short description, and an
  "Enquire on WhatsApp" action.
- **FR-011**: Each category MUST show at least 4 pieces.

**WhatsApp integration**

- **FR-012**: A WhatsApp action MUST be reachable on every page, including a fixed,
  non-animated floating button that does not cover page content or buttons.
- **FR-013**: Piece enquiries MUST pre-fill a message naming the piece and its collection.
- **FR-014**: The Contact form MUST compose the visitor's name, optional wedding date,
  optional phone and message into a WhatsApp message and open it; name and message are
  required.
- **FR-015**: All WhatsApp actions MUST target a single, configurable business number.
- **FR-016**: The website MUST NOT store or transmit visitor form data anywhere other than
  the WhatsApp message the visitor sends themselves.

**Contact page**

- **FR-017**: The Contact page MUST show WhatsApp number, phone (tap to call), email
  (tap to mail), store address and opening hours.

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

- **FR-023**: The site MUST NOT use any animation, transition, carousel, slider, marquee,
  parallax or auto-playing media.
- **FR-024**: The site MUST be fully responsive from 320px to wide desktop screens without
  horizontal scrolling.
- **FR-025**: The site MUST be built without heavy frameworks and run without a server
  backend.

### Key Entities

- **Collection (category)**: A group of pieces; has a name, short description, anchor
  identifier and cover image.
- **Piece**: A jewellery item shown on the Collections page; has a name, short description,
  collection, and image.
- **Enquiry message**: The text pre-filled into WhatsApp; composed from a piece (name +
  collection) or from the Contact form fields (name, wedding date, phone, message).
- **Business contact details**: WhatsApp number, phone, email, address, opening hours.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A visitor can go from the Home page to a pre-filled WhatsApp enquiry about a
  specific piece in 3 taps or fewer.
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
- **SC-007**: Zero moving elements on any page at any time.

## Assumptions

- The business name, copy, prices and real product photography are not yet provided. The
  first release uses a placeholder brand name ("Aurelia Bridal Jewels"), placeholder
  copy, a placeholder WhatsApp number and generated placeholder images, all designed to be
  replaced without code changes beyond content edits.
- Prices are not shown; pricing is discussed on WhatsApp (common for bridal jewellery).
- Content is in English only.
- The catalogue is small enough (tens of pieces) to be maintained by editing HTML directly;
  no content management system is needed.
- The site will be hosted on a standard static host (e.g. GitHub Pages, Netlify,
  Cloudflare Pages) that serves files over HTTPS with compression enabled.
- Visitors use modern browsers released within the last ~4 years (all support WebP and
  native lazy loading).
