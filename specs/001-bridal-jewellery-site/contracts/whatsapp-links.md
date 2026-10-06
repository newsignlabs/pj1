# Contract: WhatsApp Click-to-Chat Links

## URL format

```text
https://wa.me/<NUMBER>?text=<URL-ENCODED MESSAGE>
```

- `<NUMBER>`: full international number, digits only, no `+`, spaces, dashes or leading
  zeros. Placeholder: `919876543210`.
- `text`: encoded with `encodeURIComponent` semantics (spaces → `%20`, newlines → `%0A`,
  `&` → `%26`).

## Markup

Every WhatsApp link:

```html
<a href="https://wa.me/919876543210?text=..." target="_blank" rel="noopener">…</a>
```

- MUST be a real `href` (works without JS).
- MUST open in a new tab (`target="_blank" rel="noopener"`) so the site stays open.
- Piece enquiry links carry the piece-specific message in the `href` itself.

## Contact form (JS enhanced)

`<form id="enquiry-form" data-wa-number="919876543210">` with fields
`name` (required), `wedding-date` (optional, `type="date"`), `phone` (optional, `type="tel"`),
`message` (required). On submit `main.js`:

1. Lets native validation run; aborts if invalid.
2. Builds the message (see data-model.md), trimming each field.
3. Opens `https://wa.me/<data-wa-number>?text=<encoded>` in a new tab.
4. Does not store or send the data anywhere else.

## Invariants (checked by `tools/check_site.py`)

- All `wa.me` links and `data-wa-number` attributes across all pages use the same number.
- Every page contains at least one `wa.me` link and the floating button.
