# Ecommerce Expo assets

Drop final event artwork here using these exact filenames, then run
`python build_simple.py`.

## Product imagery

- `product.jpg` — catalog product image used by cards 1 and 6. Until supplied,
  both cards reuse the existing flower thumbnail.
- `card1-flower.png` — the transparent storefront flower from Figma frame
  `229:443`. `card1-browser-{os,left,right}.svg` are that frame's browser
  controls. These four assets are required by Card 1 and inlined for offline
  playback.
- `editor-before` — the AI Image Editor input: the product on its original
  background.
- `editor-after` — the editor's own output for that exact file.

Both are currently in as **layout/motion placeholders**, exported from Figma
frame 213:1313 and cropped to 623x455 — the well's native size, so the card
never resamples them. They still need to be replaced by a better, confirmed AI
Image Editor example before the event. Crop from the plate export at (9,9):
1px border plus 8px padding. **Re-export the pair together.** The card wipes
between them, which only reads as a background change because the product
registers at offset (0,0); `tools/check_editor.py` fails verification if it
stops doing so.

Either may be `.png`, `.jpg` or `.jpeg`; the build picks whichever exists.

Card 4 displays an asset-needed state until *both* exist. Presence only makes
the motion available; it does not mean placeholders are approved for the
event. Do not synthesize the final pair or fake the replacement with CSS — the
after ultimately has to be confirmed editor output.

### Which Uploadcare feature produced these

The current pair depicts an **AI Image Editor** flow: the near rock the bottle
stands on is kept and only the sea and far background resolve to studio white.
It is a placeholder example, not yet the final provenance-approved claim.

Do not relabel it as background removal. `remove_bg` is a different feature
with a different result — it cuts the subject out and puts a **solid colour**
behind it, so the rock would be gone too. It is also REST-only, asynchronous,
and not in the dashboard UI. If that is ever the effect you want instead, the
round trip is scripted:

    export UPLOADCARE_PUBLIC_KEY=... UPLOADCARE_SECRET_KEY=...
    python tools/remove_bg.py assets/ecommerce/editor-before.jpg --bg ffffff --shadow

`--bg` makes the add-on composite the studio colour itself, so what comes back
is already a finished shot and no transparent PNG is ever a deliverable.
`--shadow` adds the contact shadow. Both are fixed at REST call time and cannot
be added later with a URL operation, so re-run the script to change them. It
needs a paid plan. See https://uploadcare.com/docs/remove-bg/.

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
