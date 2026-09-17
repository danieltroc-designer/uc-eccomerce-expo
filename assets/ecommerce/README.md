# Ecommerce Expo assets

Drop final event artwork here using these exact filenames, then run
`python build_simple.py`.

## Product imagery

- `product.jpg` — catalog product image used by cards 1 and 6. Until supplied,
  both cards reuse the existing flower thumbnail.
- `editor-before.jpg` — genuine AI Image Editor input: the product on its
  original messy background.
- `editor-after.jpg` — genuine AI Image Editor output: the same unaltered
  product on the final studio-white background.

Card 4 deliberately displays an asset-needed state until both editor files
exist. Do not synthesize either image or fake the replacement with CSS.

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
confirmed. Keep `qrConfirmed:false` on card 7 until then, so the inherited
Webflow-event QR can never appear by accident.
