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
- Placement: floating button (every page), header button (desktop), footer link,
  Contact page details, and at most one in-content call to action per page. No
  per-piece WhatsApp buttons. No contact form.

## Invariants (checked by `tools/check_site.py`)

- All `wa.me` links across all pages use the same number.
- Every page contains at least one `wa.me` link and the floating button.
