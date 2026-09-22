# Ecommerce Expo animation plans

| # | Plan | Severity | Status |
|---|---|---|---|
| 001 | [Replay card 1 optimization on every loop](001-replay-card-one-optimization.md) | HIGH | OBSOLETE |
| 002 | [Move progress animation onto the compositor](002-composite-progress-motion.md) | HIGH | OBSOLETE |
| 003 | [Make card 4 a real before/after reveal](003-build-real-editor-reveal.md) | HIGH | OBSOLETE |
| 004 | [Pace card 1 for a booth, and fix its two element handovers](004-pace-card-one-for-a-booth.md) | HIGH | DONE |
| 005 | [Pause and resume the active card’s motion with the deck clock](005-pause-resume-active-motion.md) | MEDIUM | TODO |
| 006 | [Commit the outgoing card’s visual state before cancelling WAAPI](006-commit-outgoing-card-before-kill.md) | MEDIUM | TODO |
| 007 | [Drive the deck progress hairline with scaleX, not width](007-composite-deck-progress.md) | MEDIUM | TODO |
| 008 | [Keep JS reduced-motion in sync with the OS setting](008-live-reduced-motion.md) | MEDIUM | TODO |
| 009 | [Put entrance opacity on `--ease-out` and strengthen `--ease-in-out`](009-unify-entrance-easing.md) | LOW | TODO |
| 010 | [Let Card 5’s “Trusted by” rise with the logo wall](010-card-five-title-entrance.md) | LOW | TODO |
| 011 | [Select the Brand sage chip while Card 4 types its prompt](011-select-sage-preset-chip.md) | LOW | TODO |
| 012 | [Let Card 1’s analysis donut fill instead of snapping](012-donut-fill-transition.md) | LOW | TODO |

## Status notes

- **001 and 002 are obsolete, not executed.** Both were written against the
  first version of card 1 (`.ef-opt`, `.ef-photo`, `efCrisp`, `.ef-meter`) and
  002 also against card 6's old `.ei-progress`. None of those selectors exist
  any more: card 1 was rebuilt against Figma `234:979`/`234:1415` and card 6
  against `218:1470`. The underlying findings are nonetheless satisfied in the
  current code — the card-1 score is scoped to the active slide and reset
  synchronously on re-entry (asserted by `tools/check_commerce_flow.py` on a
  *second* visit), and the surviving progress animations run on
  `stroke-dashoffset` and `clip-path` rather than on `width`. Do not execute
  either plan; they would not apply. The **deck-level** `#progress` hairline
  still writes `width`; that is plan **007**, not 002.
- **003 is obsolete.** Its old one-well wipe was superseded by Card 4's
  production-derived catalog backend → Edit with AI → variant flow. The
  genuine result, source UUID and exact preset are recorded in `EVENT.md`, and
  `tools/check_editor.py` verifies that flow twice plus reduced motion.
- **004 is done** (card 1 retimed to its 10s slot, trust marks held for the
  whole card, widget→panel and placeholder→photo handovers de-crossfaded).

## Recommended execution order

005 → 006 → 007 → 008 → 009 → 010 → 012 → 011

005 and 006 both edit `Timeline`; land 005 first so 006’s `kill()` can clear
timer *records* (`t.id`) instead of raw ids. 007 should land before 008 so
the live reduced-motion listener rebuilds `arm()` against a progress bar that
already uses `scaleX`. 009 is a global token swap: do it before 010 so Card
5’s new title transition is written with `var(--ease-out)` once. 011 and 012
are independent of the Timeline work; 012 is smaller and has no checker
risk, so it goes before 011.

## Dependencies

- **006** depends on **005** if 005 has already changed `timers` into
  records; 006’s `clearTimeout` line is written to accept both shapes.
- **007** is independent of 005/006 except that after 005 a Space pause
  should leave the `scaleX` hairline frozen (005 pauses the interval via
  `clearInterval(tickTimer)`; 007 only changes what that interval writes).
- **008** depends on `enter()` / `startSubstrate()` remaining the rebuild
  path; it should run after 007 so `REDUCED` skips the new `scaleX` tick.
- **009** has no code dependency; visually it retunes Card 6 travel and
  Card 4’s veil. If those feel like a slam, revert only `--ease-in-out` /
  `EASE.inOut` and keep the opacity token swap.
- **010** should use `--ease-out` on title opacity (009’s rule) even if 009
  has not landed — the token already exists.
- **011** and **012** are independent. Do not retune Card 4’s pointer to
  click the chip (011).
