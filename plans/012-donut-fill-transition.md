# 012 — Let Card 1’s analysis donut fill instead of snapping

- **Status**: TODO
- **Commit**: e279fbe
- **Severity**: LOW
- **Category**: Missed opportunities
- **Estimated scope**: 1 source file (`src/simple.template.html`), plus regenerated `dist/uploadcare-simple.html`

## Problem

When Card 1’s analysis beat starts, `setupCommerceFlow` lights each donut
segment by toggling `.lit`. The CSS swaps `fill` with no transition, so the
ring teleports from idle grey to brand yellow in one frame, 14ms apart. The
copy next to it fades in; the donut does not, which makes the analysis read
as a skipped state rather than as work resolving.

```css
/* src/simple.template.html:891–893 — current */
.pd-donut{flex-shrink:0;width:30px;height:30px}
.pd-donut .c{fill:rgba(255,255,255,.13)}
.pd-donut .c.lit{fill:#ffcf3e}
```

```js
/* src/simple.template.html:4231–4232 — current */
tl.to(lines[0],[{opacity:0},{opacity:1}],{at:ANALYSE+.45,dur:.26});
donut.forEach((c,i)=>tl.cls(c,'lit',ANALYSE+.20+i*.014));
```

Card 1 reuses `.pd-donut` inside `.ef-right` (`src/simple.template.html:4098`).
The 14ms stagger can stay — it is a travelling fill around the ring, not a
group entrance that needs 30–80ms. What is missing is the fill interpolation
on each segment.

## Target

Keep the colours and the stagger. Add a colour transition on the segment
fill, 160ms, `ease` (state colour change, not an entrance move):

```css
.pd-donut{flex-shrink:0;width:30px;height:30px}
.pd-donut .c{
  fill:rgba(255,255,255,.13);
  transition:fill 160ms ease;
}
.pd-donut .c.lit{fill:#ffcf3e}
```

Under reduced motion, Card 1 never plays the score (`setupCommerceFlow`
calls `settle(); settleSite(); return` at `:4160`). `settle()` already adds
`.lit` to every segment (`:4143`). The CSS media block currently does **not**
need a new rule if the class is applied with transitions disabled on those
nodes. SVG `fill` is not in the big `transition:none` list. Add `.pd-donut .c`
to that list so reduced motion does not interpolate fill on a card that is
supposed to appear finished:

```css
/* append to the existing transition:none selector list at :1936–1946 */
.pd-donut .c,
```

Do not animate `stroke-dashoffset` on the donut (it is a filled pie of `<path
class="c">` segments, not the upload ring). Do not change
`ANALYSE+.20+i*.014`.

## Repo conventions to follow

- Brand yellow is `#FFCF3E` / `--brand` (`src/simple.template.html` `:root`).
  The donut already uses `#ffcf3e`; keep the hex, do not switch to
  `var(--brand)` unless you also verify the SVG is not in a shadow tree
  (it is inline — `var(--brand)` would work, but is out of scope).
- Colour → `ease`, 100–160ms (`AUDIT.md` easing table, button press /
  small state).
- `tl.cls` remains the way segments light (`src/simple.template.html:4232`).
- Reduced motion jumps to the settled frame; do not introduce a 160ms fill
  after that jump.

## Steps

1. Replace `.pd-donut .c` rules at `src/simple.template.html:892–893` with
   the Target CSS (add `transition:fill 160ms ease` only).

2. Add `.pd-donut .c` to the `@media (prefers-reduced-motion:reduce)`
   `transition:none` list at `src/simple.template.html:1936`.

3. Do not edit `setupCommerceFlow` unless a comment next to line 4232 should
   note that fill interpolation lives on `.pd-donut .c`. Optional, one line.

4. Rebuild with `python build_simple.py`.

## Boundaries

- Do NOT change the upload ring (`.di-ring` / `strokeDashoffset`) — that is
  a 1.45s linear progress beat on purpose.
- Do NOT change donut geometry, segment count, or `#ffcf3e`.
- Do NOT add a pulse or `ftPulse`-style wash on the donut.
- Do NOT touch Card 4.
- Inherited `setupPipeline` also lights `.pd-donut .c.lit`; the CSS change
  will affect it if that card is injected. That is acceptable and consistent.
  Do not add pipeline-only exceptions.

## Verification

- **Mechanical**: `python build_simple.py`. `python tools/check_commerce_flow.py`
  still passes (including second visit and reduced). Segments still receive
  `.lit`; only the paint of `fill` is slower.
- **Feel check**:
  - Card 1 analysis beat: the donut fills clockwise (existing 14ms stagger)
    and each slice eases grey → yellow over 160ms instead of blinking.
  - In DevTools, select a `.pd-donut .c`, force class `lit`, and confirm
    `fill` interpolates (Animations panel).
  - Reduced motion: storefront (or settled analysis if you inspect before
    `settleSite`) shows a fully yellow donut with no in-progress grey.
  - Loop: `reset()` removes `.lit` (`:4127`); on the second visit the donut
    starts grey again, then fills. If it opens already yellow, `reset` is
    missing a classList clear — it currently has one; do not remove it.
- **Done when**: the analysis ring resolves as colour, not as a snap, and
  every other Card 1 beat is untouched.
