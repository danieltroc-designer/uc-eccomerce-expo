# Ecommerce Expo — event notes

Working source of truth for this booth cut. Do not invent event facts.

## Confirmed

- Event name: **Ecommerce Expo**
- Seven-card loop, approximately 44 seconds:
  1. Product image upload → optimization → live store payoff (5s)
  2. Five ecommerce benefits (6s)
  3. Zephyr proof point (6s)
  4. AI Image Editor background replacement (6s)
  5. Customer logo wall (5s)
  6. Upload → Optimize → Deliver infrastructure view (6s)
  7. Booth CTA / file-board outro (10s)
- Card 4's final version must use genuine AI Image Editor input/output:
  background replacement only, no altered product, mockup, or generated model.
- Logo wall: L'Oréal, Crayola, Samsonite, GemPages, Shogun, Marko.
- Card 1 follows Figma frame `229:443`, with uploader final state `229:544`:
  one visible upload finishes its progress and stays checked, the resulting
  optimized product card arrives at the frame's 120KB final value, then the
  storefront browser opens with the image already in place. The three beats
  resolve quickly and hold as one completed composition.

## Assets still needed

- Ecommerce product image (optional replacement for the current flower)
- Genuine AI Image Editor before/after pair — the current pair is an explicit
  **layout/motion placeholder** and will be replaced with a better confirmed
  editor example. It is cropped to the well's native 623x455 and registers at
  offset (0,0), which makes it safe for testing the wipe, but that geometric
  check is not evidence of production provenance.
- ~~Customer SVG marks~~ — all six wall logos and Zephyr are in
- Ecommerce Expo QR artwork after its destination is confirmed
- Final giveaway wording for card 7; `and enter to win something!` is a visible
  Figma placeholder, not confirmed event copy

See `assets/ecommerce/README.md` for exact filenames.

## Open / TBD

- Event dates, venue, and booth number
- QR destination (likely ecommerce landing page, not yet confirmed)
- Raffle / swag line
- Replace the visible inherited QR before the event; its current destination
  remains `https://l.ead.me/bgyXox` and is not confirmed for Ecommerce Expo
- Whether “2x faster page loads” and Zephyr attribution require legal/source
  annotation in the final artwork
- Final visual refinement pass and motion-skill audit

## Inherited placeholders

The clone still contains Webflow-specific types and assets for reuse, but the
default deck no longer uses the Webflow marketplace card, Webflow headline, or
previous-event QR.
