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

Customer SVGs live in `assets/logos/`. Add:

- `crayola.svg`
- `samsonite.svg`
- `gempages.svg`
- `shogun.svg`

The build scans that folder automatically. L'Oréal, Marko, and Zephyr already
have real vectors; missing wall marks render as neutral text in the first
layout pass.

## CTA

Replace `assets/qr/booth-qr.png` only after the Ecommerce Expo destination is
confirmed. Keep `qrConfirmed:false` on card 7 until then, so the inherited
Webflow-event QR can never appear by accident.
