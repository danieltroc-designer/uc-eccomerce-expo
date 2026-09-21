# Ecommerce Expo assets

Drop final event artwork here using these exact filenames, then run
`python build_simple.py`.

## Product imagery

- `product.jpg` — optional shared catalog product image.
- `card1-product.jpg` — the exact tube photograph from Figma frame `234:979`.
  Card 1 uses this one source for the dragged file, compact upload row,
  optimization preview, blurred wash, and frame `234:1415` storefront. It is
  required and inlined for offline playback.
- `card1-browser-{os,left,right,back}.svg` — exact browser controls for Card 1's
  storefront payoff.
- `editor-after.jpg` — Card 4's real AI Enhancer result for
  `card1-product.jpg`. It was generated in the production standalone tool from
  Uploadcare UUID `7bfcb94a-3f88-41a1-90b3-cc56a3c42360`; result UUID
  `9c081b6e-6892-4bda-8233-9d21584a1c07`.

Card 4 deliberately has no separate `editor-before` asset: its source is the
same inlined `card1Product` value used by Card 1, so the slide cannot quietly
drift to a different product shot. The exact production prompt is stored as
`CE_PROMPT` in `src/simple.template.html` and documented in `EVENT.md`.

The result is 832×1248 (2:3), matching the source aspect ratio. The source and
result appear in the same 300×450 editor slot; the tool's dense dot-grid
pending state covers the generative swap. Do not replace the result with a CSS
background treatment or a synthetic mockup: regenerate it through the real
tool and update its UUID and prompt provenance together.

## Benefit icons

Card 2 uses five required 48×48 SVG exports from storyboard frame 212:1213:

- `benefit-mobile.svg`
- `benefit-conversions.svg`
- `benefit-peak.svg`
- `benefit-maintain.svg`
- `benefit-store.svg`

Their accent colours are part of the artwork. The build fails instead of
substituting a different glyph if one is missing.

## Infrastructure flow

Card 6 uses the exact exports from Figma frame 218:1470:

- `infrastructure-product.png` — the 1800×2400 cosmetics photograph.
- `infrastructure-node.svg` — the rail's 8.14062×8.14062 endpoint.
- `infrastructure-line.svg` — its 308.719×1 connector stroke.
- `infrastructure-collapsed.svg` — frame 219:1578's yellow 66.281×8.14062
  compact connector.
- `infrastructure-lockup.svg` — frame 219:1612's final 339×61 Uploadcare
  lockup.

All five are required. The build fails rather than falling back to the flower
thumbnail or redrawing the path, because their crop and native boxes are part
of the card's animation geometry.

## Customer logos

Customer SVGs live in `assets/logos/`, and the build scans that folder
automatically — dropping in `<normalized-name>.svg` is all a new mark needs.

All six wall marks and the Zephyr attribution are now real vectors. They are
exported from storyboard frames 207:1131 and 204:1081 and carry those frames'
bounding boxes, which `ECOM_WALL` in the template is measured against: re-export
from the same frames or the slot sizes stop matching. A name with no vector
still renders as neutral text rather than disappearing.

## CTA

Replace `assets/qr/booth-qr.png` only after the Ecommerce Expo destination is
confirmed. Card 7 currently shows it because frame 219:1638 is an explicit
mockup of the inherited Webflow board/outro, but `qrConfirmed` must stay
`false`: the visible code still points to `https://l.ead.me/bgyXox` and is not
approved for Ecommerce Expo.
