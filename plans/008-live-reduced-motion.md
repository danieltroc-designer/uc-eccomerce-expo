# 008 — Keep JS reduced-motion in sync with the OS setting

- **Status**: TODO
- **Commit**: e279fbe
- **Severity**: MEDIUM
- **Category**: Accessibility
- **Estimated scope**: 1 source file (`src/simple.template.html`), plus regenerated `dist/uploadcare-simple.html`

## Problem

CSS already respects `prefers-reduced-motion` live, via a media query. JS
captures it once at parse time. A change after load (booth laptop, accessibility
preview, Rendering panel) stops CSS loops but leaves WAAPI scores, substrate
spawning, and `Timeline({reduced:REDUCED})` on the value from page load.

```js
/* src/simple.template.html:2084 — current */
const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
```

```js
/* src/simple.template.html:3475–3477 — substrate uses the snapshot */
function startSubstrate(){
  const field = document.getElementById('sbField');
  if (!field || REDUCED) return;      // reduced motion runs no ambient layer
```

```css
/* src/simple.template.html:1933–1964 — CSS is live */
@media (prefers-reduced-motion:reduce){
  /* transitions none, looping animations none, .eb-card::before pinned off */
}
```

`enter()` builds `new Timeline({reduced:REDUCED})` at
`src/simple.template.html:5439`. Every `setup*` that branches on `REDUCED`
(Cards 1, 4, 6, 7) reads the same snapshot.

## Target

`REDUCED` is a `let`, updated from a `change` listener. When the flag flips:

1. Stop or start the substrate so it matches.
2. Re-enter the current slide so the active Timeline is built with the new
   flag (`enter(idx)` already `kill()`s the old score and calls `reset()`).

```js
const motionQuery = matchMedia('(prefers-reduced-motion: reduce)');
let REDUCED = motionQuery.matches;
const onMotionPref = ()=>{
  REDUCED = motionQuery.matches;
  if (REDUCED) stopSubstrate();
  else startSubstrate();
  if (typeof idx === 'number' && slidesEl && slidesEl.children.length){
    const wasPlaying = playing;
    enter(idx);
    if (!wasPlaying) pause();
  }
};
motionQuery.addEventListener('change', onMotionPref);
```

`startSubstrate` must be idempotent (a second call does not stack spawn
loops). `stopSubstrate` must:

- set a `substrateOn = false` flag that `spawn()` checks
- remove every `.sb-blip` currently in `#sbField`
- clear `live`

Safari still supports `addListener` and not `addEventListener` on
`MediaQueryList` in some older versions. Use:

```js
if (motionQuery.addEventListener) motionQuery.addEventListener('change', onMotionPref);
else motionQuery.addListener(onMotionPref);
```

Reduced motion means fewer and gentler animations, not zero: keep the
existing `if (REDUCED){ settle(); settleSite(); return; }` branches that paint
the settled frame. Do not hide the deck.

## Repo conventions to follow

- Substrate already no-ops when `REDUCED` is true at boot
  (`src/simple.template.html:3477`). Give it a matching stop path.
- Card 7 already tears down CSS loops in `tl.onKill(stopMotion)`
  (`src/simple.template.html:3843–3854`). Re-entering via `enter(idx)` reuses
  that; do not duplicate globe/twinkle teardown in the listener.
- `enter(idx)` is the only legal way to rebuild a score. Do not call
  `setupCommerceFlow` from the listener.
- Plan 005 may add `tl.pause()`. If the deck was paused when the preference
  flips, restore that paused state after `enter(idx)` as in Target
  (`wasPlaying`). `enter()` currently sets `playing` via `arm()` when
  `playing` is true (`src/simple.template.html:5480`); it does not force play
  if `playing` is already false — preserve that. Capture `wasPlaying` *before*
  `enter`, because 005’s `enter` must not un-pause as a side effect. If
  `enter()` still calls `if (playing) arm();` and does not call `resume()` on
  the new timeline, a paused deck that flips reduced-motion should:
  - `enter(idx)` with `playing` still false (so `arm()` is skipped)
  - not `pause()` a brand-new timeline that never started
  Follow the code you find: if `playing` is left untouched by `enter()`, you
  only need `enter(idx)` and the substrate swap.

## Steps

1. Replace `const REDUCED = ...` at `src/simple.template.html:2084` with the
   `let` + `motionQuery` from Target. Register the listener **after**
   `startSubstrate`, `enter`, `pause`, and `idx` exist, so the callback can
   call them. That means: keep `let REDUCED = motionQuery.matches` next to
   the other constants, but attach `onMotionPref` at the bottom of the
   playback section (after `togglePlay`, around `src/simple.template.html:5496`),
   not at line 2084.

2. Refactor `startSubstrate()` (`src/simple.template.html:3475`):

```js
let substrateOn = false;
function stopSubstrate(){
  substrateOn = false;
  const field = document.getElementById('sbField');
  if (field) field.replaceChildren();
}
function startSubstrate(){
  const field = document.getElementById('sbField');
  if (!field || REDUCED || substrateOn) return;
  substrateOn = true;
  /* existing rnd / live / place / spawn, but spawn must:
     if (!substrateOn) return;
     if (!playing) { setTimeout(spawn, rnd(700,1600)); return; }
     ...existing blip create...
     setTimeout(spawn, rnd(700,1600));
  */
}
```

   Preserve `SB_ZONES`, `SB_MAX`, `SB_COLORS`, placement rejection, and
   `--life` / `--c` exactly.

3. `startSubstrate()` is invoked once at boot (search for the call near the
   end of the file, currently around the `startSubstrate(); enter(0);`
   sequence). Leave that call. Do not invoke it a second time at registration.

4. Rebuild with `python build_simple.py`.

## Boundaries

- Do NOT remove the CSS `@media (prefers-reduced-motion:reduce)` block.
- Do NOT invent a new reduced-motion look. Re-entering the current slide is
  the whole JS response.
- Do NOT `location.reload()`.
- Do NOT change `settle()` / `settleSite()` contents.
- If plan 007 already skips the progress interval when `REDUCED`, the listener
  + `enter(idx)` will rebuild `arm()` against the new flag; do not duplicate
  progress logic here.

## Verification

- **Mechanical**: `python build_simple.py`. Reduced-motion checkers still
  pass: `python tools/check_editor.py`, `python tools/check_commerce_flow.py`,
  `python tools/check_outro.py` (each already asserts a reduced path).
- **Feel check**:
  - Load the deck with motion on. In Chrome Rendering, check
    “Emulate CSS prefers-reduced-motion: reduce”. Within one frame of the
    change: Card 1/4/6 jump to their settled storefront/lockup (no leftover
    cursor flying); Card 2 wash stops; Card 7 globe/wave/twinkle freeze as
    the CSS already does; substrate blips vanish and no new ones spawn.
  - Uncheck the emulation: the current card rebuilds its *opening* score
    (same as a loop re-entry), substrate resumes, CSS loops run again.
  - Flip the flag while paused (after 005): the settled-or-scored frame
    updates to match the new preference, and the deck stays paused.
  - Flip twice quickly: only one substrate spawn loop (no stacked blips).
- **Done when**: changing `prefers-reduced-motion` after load updates both
  CSS and JS on the active card, and `REDUCED` is no longer a `const`.
