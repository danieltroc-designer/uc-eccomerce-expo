# Ecommerce Expo — event notes

Working source of truth for this booth cut. Do not invent event facts.

## Confirmed

- Event name: **Ecommerce Expo**
- Seven-card loop, approximately 63 seconds:
  1. Product image upload → optimization → live store payoff (10s)
  2. Five ecommerce benefits, two one-second highlight passes (11s)
  3. Zephyr proof point (6s)
  4. Marketplace backend → Edit with AI → catalog variant → Add to media → storefront (13s)
  5. Customer logo wall (5s)
  6. Upload → Optimize → Deliver infrastructure view (8s)
  7. Booth CTA / file-board outro (10s)
- Card 4 records the production `ai-catalog-admin` demo: the Ashfold product
  backend opens, the pointer crosses its catalogue image so “Edit with AI”
  appears under it, and the click hands over to the editor. The backend is
  rebuilt as live DOM from the reference captures in `assets/ecommerce/`, so it
  stays sharp on the booth panel and the page never zooms. Its real source UUID is
  `01362b9d-462f-4db4-8c8a-acd0b4c2a06a`; the “Brand sage backdrop” preset
  generated result UUID `3d5bbd80-9f76-46d0-b7ff-263dbb1ec4fe` with:
  “Replace the background with a flat sage green studio backdrop, keep the
  bottle and its natural shadow”. The committed 1536×2048 source and 880×1168
  result are `assets/ecommerce/catalog-source.jpg` and `editor-after.jpg`. The
  finished result holds, a second pointer clicks “Add to media,” and the card
  ends with that result live on an Ashfold product page, reusing Card 1's
  storefront frame. Its copy and €49.00 price come from the demo's own backend
  record, not from invented catalogue data.
- Logo wall: L'Oréal, Crayola, Samsonite, GemPages, Shogun, Marko.
- Card 1's first phase follows Figma frame `234:979`: the complete uploader
  interaction from the Webflow booth card runs in the left cell with one tube
  photo, then the same photo resolves through the frame's simplified two-line
  optimization readout in the right cell. Its payoff follows frame `234:1415`:
  the completed process shell recedes into a 1252px browser where the same tube
  photo is already live on the Velour Essentials product page. It is paced for
  booth distance — the upload takes 1.45s and the optimization claim holds ~1.3s
  before the storefront arrives — which is what the 10s slot buys. The SOC 2,
  GDPR and HIPAA marks now sit beneath Card 2's benefit row rather than Card 1.
- Card 3 follows Figma frame `234:1237`: “2x faster page loads. Faster pages,
  more sales.” beside the Zephyr mark and “This way, we get the absolute most
  speed we can when loading our web pages across mobile devices.” attributed
  to Sam McKinney, Director of Agency Services at Zephyr. The two green-panel
  claims are separate paragraphs with a 40px gap.
- Card 6 preserves its existing choreography and uses its added two seconds
  solely to hold the final Uploadcare lockup longer.
- Card 7 follows Figma frame `219:1638` and otherwise retains the Webflow
  outro unchanged: “Load faster, sell more.” over “Come say hi 👋 and enter
  to win LEGO Polaroid Camera Building Set.” Its central pixel glyph shimmers
  across five near-identical Uploadcare yellows, so it stays brand yellow
  while it moves rather than drifting between cream and amber.

## Assets still needed

- Ecommerce product image (optional replacement for the current flower)
- ~~Customer SVG marks~~ — all six wall logos and Zephyr are in
- Ecommerce Expo QR artwork after its destination is confirmed

See `assets/ecommerce/README.md` for exact filenames.

## Open / TBD

- Event dates, venue, and booth number
- QR destination (likely ecommerce landing page, not yet confirmed)
- Replace the visible inherited QR before the event; its current destination
  remains `https://l.ead.me/bgyXox` and is not confirmed for Ecommerce Expo
- Whether “2x faster page loads” and Zephyr attribution require legal/source
  annotation in the final artwork
- Final visual refinement pass and motion-skill audit

## Inherited placeholders

The clone still contains Webflow-specific types and assets for reuse, but the
default deck no longer uses the Webflow marketplace card, Webflow headline, or
previous-event QR.
