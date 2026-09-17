# Ecommerce Expo animation plans

Plans are based on commit `e122bf0` plus the current uncommitted Ecommerce Expo
working tree.

| # | Plan | Severity | Status |
|---|---|---|---|
| 001 | [Replay card 1 optimization on every loop](001-replay-card-one-optimization.md) | HIGH | TODO |
| 002 | [Move progress animation onto the compositor](002-composite-progress-motion.md) | HIGH | TODO |
| 003 | [Make card 4 a real before/after reveal](003-build-real-editor-reveal.md) | HIGH | TODO |

## Recommended execution order

1. **001** — correctness fix, isolated, no asset dependency.
2. **002** — 4K performance fix, isolated from card 4.
3. **003** — execute when the genuine AI Image Editor before/after pair is
   available. Until then, retain the honest asset-needed state.

## Dependencies

- 001 and 002 are independent.
- 003 depends on genuine `assets/ecommerce/editor-before.jpg` and
  `assets/ecommerce/editor-after.jpg` for final visual verification.
- Plan 002 intentionally does not touch `.ee-wipe`; all card 4 motion,
  including transform-based divider travel, belongs to plan 003.
