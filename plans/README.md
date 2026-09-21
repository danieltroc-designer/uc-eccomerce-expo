# Ecommerce Expo animation plans

| # | Plan | Severity | Status |
|---|---|---|---|
| 001 | [Replay card 1 optimization on every loop](001-replay-card-one-optimization.md) | HIGH | OBSOLETE |
| 002 | [Move progress animation onto the compositor](002-composite-progress-motion.md) | HIGH | OBSOLETE |
| 003 | [Make card 4 a real before/after reveal](003-build-real-editor-reveal.md) | HIGH | OBSOLETE |
| 004 | [Pace card 1 for a booth, and fix its two element handovers](004-pace-card-one-for-a-booth.md) | HIGH | DONE |

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
  either plan; they would not apply.
- **003 is obsolete.** Its old one-well wipe was superseded by Card 4's
  production-derived upload → prompt → AI Enhancer flow. The genuine result,
  source UUID and exact prompt are now recorded in `EVENT.md`, and
  `tools/check_editor.py` verifies that flow twice plus reduced motion.
- **004 is done** (card 1 retimed to its 10s slot, trust marks held for the
  whole card, widget→panel and placeholder→photo handovers de-crossfaded).

## Dependencies

- 003 has no remaining dependency; do not execute it against the rebuilt card.
- 004 is independent and already applied; any future retiming of card 1 should
  start from its "Target" section, which records why each number is what it is.
