# 002 — Move progress animation onto the compositor

- **Status**: TODO
- **Commit**: e122bf0
- **Severity**: HIGH
- **Category**: Performance
- **Estimated scope**: 2 source/test files plus regenerated `dist/uploadcare-simple.html`; about 30 lines

## Problem

Two prominent Expo animations change `width` on every frame:

```css
/* src/simple.template.html:1440–1442 — current */
.ef-meter i {
  display:block;
  height:100%;
  width:0;
  background:#6e8cff;
  border-radius:inherit;
}
.slide.active .ef-meter i {
  animation:efMeter 1s linear .18s forwards;
}
@keyframes efMeter { to { width:100% } }
```

```css
/* src/simple.template.html:1556–1559 — current */
.ei-progress {
  position:absolute;
  left:0;
  top:0;
  height:100%;
  width:0;
  background:#b6b7ff;
}
.slide.active .ei-progress {
  animation:eiProgress 2.8s var(--ease-in-out) .55s forwards;
}
@keyframes eiProgress { to { width:100% } }
```

Animating width triggers layout and paint for every frame. These are
explanatory animations on a 1920×1080 stage that is also exported at
3840×2160, so avoidable main-thread work directly increases the chance of held
frames in the booth video.

Card 4 also animates `left`, but plan 003 owns that markup and motion. Do not
touch `.ee-wipe` in this plan.

## Target

Render both bars at full width and reveal them with a left-anchored
`scaleX(0 → 1)`. Preserve their existing timing and easing:

```css
/* target: card 1 */
.ef-meter i {
  display:block;
  height:100%;
  width:100%;
  background:#6e8cff;
  border-radius:inherit;
  transform:scaleX(0);
  transform-origin:left center;
}
.slide.active .ef-meter i {
  animation:efMeter 1s linear .18s forwards;
}
@keyframes efMeter { to { transform:scaleX(1) } }
```

```css
/* target: card 6 */
.ei-progress {
  position:absolute;
  left:0;
  top:0;
  height:100%;
  width:100%;
  background:#b6b7ff;
  transform:scaleX(0);
  transform-origin:left center;
}
.slide.active .ei-progress {
  animation:eiProgress 2.8s var(--ease-in-out) .55s forwards;
}
@keyframes eiProgress { to { transform:scaleX(1) } }
```

For reduced motion, pin both transforms to `scaleX(1)` rather than overriding
width:

```css
@media (prefers-reduced-motion:reduce) {
  .ef-meter i,
  .ei-progress {
    transform:scaleX(1)!important;
  }
}
```

## Repo conventions to follow

- Predetermined motion uses CSS; retain that architecture.
- Travel and morphing already use `--ease-in-out` and progress already uses
  `linear`. This is a performance-only change; do not retime or re-ease it.
- Left-origin reveals already exist at `src/simple.template.html:238`:

```css
.pl-row.pl-anim .pl-line span {
  transform:scaleX(0);
  transform-origin:left;
}
```

- Edit `src/simple.template.html`, then regenerate
  `dist/uploadcare-simple.html` with the build script.

## Steps

1. In the card 1 meter rule, set `width:100%`, add
   `transform:scaleX(0)` and `transform-origin:left center`, and change
   `efMeter` to animate `transform:scaleX(1)`.
2. In the card 6 progress rule, make the same base-state changes and change
   `eiProgress` to animate `transform:scaleX(1)`.
3. In the reduced-motion block, replace
   `.ef-meter i,.ei-progress{width:100%!important}` with a transform override
   that pins both to `scaleX(1)`.
4. Extend `tools/verify_timeline.py` or a focused browser assertion to confirm:
   - Both bars have a constant `offsetWidth` before, during, and after motion.
   - Their computed transform progresses from a near-zero X scale to 1.
5. Run `python3 build_simple.py`.

## Boundaries

- Do not alter `.ee-wipe`; plan 003 owns the editor transition.
- Do not change animation delays, durations, curves, colors, dimensions, or
  card copy.
- Do not add `will-change`; these short, active-only animations do not need
  permanent layer promotion.
- Do not change the moving `.ei-file` choreography.
- Do not edit `dist/uploadcare-simple.html` by hand.
- Do not add dependencies.
- If the selectors have drifted since commit `e122bf0`, stop and report rather
  than applying the pattern to unrelated bars.

## Verification

- **Mechanical**:
  - `rg "@keyframes (efMeter|eiProgress).*width" src/simple.template.html`
    returns no matches.
  - `python3 build_simple.py` succeeds.
  - `python3 tools/verify_simple.py` reports zero console issues.
  - `python3 tools/verify_timeline.py` passes.
- **Feel check**:
  - Record cards 1 and 6 at 10% playback speed in Chrome DevTools.
  - Confirm each bar still grows from the exact left edge without stretching
    its rounded container or changing nearby layout.
  - In the Performance panel, confirm the bar growth does not create per-frame
    Layout events.
  - At normal speed, compare against the pre-change deck and confirm timing is
    perceptually unchanged.
  - Enable reduced motion and confirm both bars are immediately full.
- **Done when**: Both bars look identical to the current deck but animate only
  `transform`, with constant `offsetWidth` throughout.
