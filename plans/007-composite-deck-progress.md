# 007 — Drive the deck progress hairline with scaleX, not width

- **Status**: TODO
- **Commit**: e279fbe
- **Severity**: MEDIUM
- **Category**: Performance
- **Estimated scope**: 1 source file (`src/simple.template.html`), plus regenerated `dist/uploadcare-simple.html`

## Problem

The 3px progress hairline at the bottom of the stage is updated on a 60ms
interval for the entire 63-second loop by writing `style.width`. That is a
layout property. It runs independently of each card’s Timeline, so it is the
one animation that is always on.

```css
/* src/simple.template.html:140–148 — current */
#progress{
  position:absolute;left:0;bottom:0;height:3px;width:100%;
  background:rgba(255,255,255,.06);z-index:6;
}
#progress i{
  display:block;height:100%;width:0;
  background:rgba(255,255,255,.28);
}
```

```html
<!-- src/simple.template.html:1975 — current -->
<div id="progress"><i id="progressBar"></i></div>
```

```js
/* src/simple.template.html:5483–5489 — current */
function arm(){
  const remain = slideDuration(idx) - elapsedBeforePause;
  timer = setTimeout(()=>enter(idx+1), remain);
  tickTimer = setInterval(()=>{
    const p = (elapsedBeforePause + (performance.now()-slideStart)) / slideDuration(idx);
    progressBar.style.width = Math.min(100, p*100)+'%';
  }, 60);
}
```

`plans/002-composite-progress-motion.md` is **OBSOLETE** and targeted deleted
selectors (`.ef-meter`, `.ei-progress`). Do not execute 002. This plan is only
the deck-level `#progress` hairline.

## Target

The fill is always 100% wide and grows by `transform: scaleX(p)` from the
left. Under reduced motion the hairline does not move: it stays at `scaleX(0)`
and the interval is not started.

```css
#progress{
  position:absolute;left:0;bottom:0;height:3px;width:100%;
  background:rgba(255,255,255,.06);z-index:6;
}
#progress i{
  display:block;height:100%;width:100%;
  transform:scaleX(0);
  transform-origin:left center;
  background:rgba(255,255,255,.28);
  will-change:transform;
}
@media (prefers-reduced-motion: reduce){
  #progress i{ transform:scaleX(0) !important; }
}
```

```js
function arm(){
  const remain = slideDuration(idx) - elapsedBeforePause;
  timer = setTimeout(()=>enter(idx+1), remain);
  if (REDUCED){
    progressBar.style.transform = 'scaleX(0)';
    return;
  }
  tickTimer = setInterval(()=>{
    const p = (elapsedBeforePause + (performance.now()-slideStart)) / slideDuration(idx);
    progressBar.style.transform = 'scaleX('+Math.min(1, Math.max(0, p))+')';
  }, 60);
}
```

On `enter()`, before `arm()`, reset the bar to `scaleX(0)` so a new card does
not inherit the previous card’s fill. Do not animate that reset (no
transition on `#progress i`).

`REDUCED` is the JS flag. Plan 008 may turn it into a live `let`; read
whatever the identifier currently is, do not snapshot a second copy.

## Repo conventions to follow

- Animate `transform` and `opacity` only (`AGENTS.md`). Card 6 already
  converted a layout contraction into transforms
  (`src/simple.template.html:4712–4719`).
- `transform-origin:left center` matches a left-origin progress fill. Do not
  use `scaleX` with the default center origin — the bar would grow from the
  middle of the stage.
- Reduced motion keeps comprehension fades and drops positional motion
  (`src/simple.template.html:1933–1964`). A travelling progress line is
  positional motion.
- Do not use `transition: all`.

## Steps

1. Replace the `#progress i` rule at `src/simple.template.html:145–148` with
   the Target CSS (full width, `scaleX(0)`, left origin).

2. Add `#progress i{ transform:scaleX(0) !important; }` inside the existing
   `@media (prefers-reduced-motion:reduce)` block
   (`src/simple.template.html:1933`), next to the other “stop looping / ambient
   motion” rules around line 1949. Do not put it in the long
   `transition:none` selector list; this element has no transition.

3. In `enter()`, immediately after `clearTimeout(timer); clearInterval(tickTimer);`
   (`src/simple.template.html:5478`), set
   `progressBar.style.transform = 'scaleX(0)'`.

4. Replace `progressBar.style.width = ...` in `arm()` with the Target JS.
   Skip the interval when `REDUCED`.

5. Search `src/simple.template.html` for `progressBar.style.width` and
   `#progress i` `width:0` — there must be no remaining width writes.

6. Rebuild with `python build_simple.py`.

## Boundaries

- Do NOT resurrect `.ef-meter` / `.ei-progress` from obsolete plan 002.
- Do NOT change the 60ms tick rate, the 3px height, or the bar colours.
- Do NOT add a CSS transition on `#progress i` (the JS already steps it;
  a transition would lag the true elapsed ratio and overshoot on card change).
- Do NOT edit `src/index.template.html` unless the same `#progress` pattern
  exists there *and* you are also rebuilding the full deck; the booth loop
  is `src/simple.template.html` only.

## Verification

- **Mechanical**: `python build_simple.py`. In DevTools, `#progress i`
  computed `width` is `1920px` (or 100% of `#progress`) at all times;
  `transform` is `matrix(p, 0, 0, 1, 0, 0)` (or `scaleX(p)`) as the card
  plays. `python tools/verify_simple.py` still reports a clean console.
- **Feel check**:
  - Watch one full card: the hairline still grows left → right and snaps
    back at the slide change, same as today, with no dip in the middle of
    the stage.
  - Pause (after 005, Space freezes it; before 005, it will still tick —
    that is 005’s job).
  - Toggle `prefers-reduced-motion` in Rendering: the hairline stays empty
    (`scaleX(0)`) and does not creep.
  - At a 1280×800 viewport, the bar still spans the scaled stage edge-to-edge
    (transform, not a leftover `%` width on a scaled parent).
- **Done when**: no JS writes `progressBar.style.width`, the fill is a left
  origin `scaleX`, and reduced motion keeps the bar at 0.
