# 006 — Commit the outgoing card’s visual state before cancelling WAAPI

- **Status**: TODO
- **Commit**: e279fbe
- **Severity**: MEDIUM
- **Category**: Interruptibility
- **Estimated scope**: 1 source file (`src/simple.template.html`), plus regenerated `dist/uploadcare-simple.html`

## Problem

`enter()` kills the current Timeline at the *top* of a slide change. WAAPI
`cancel()` reverts each animation to the inline styles `reset()` wrote at
score build time. Cards 1, 4 and 6 already pin their *finished* frames with
`settle()` / `settleSite()` so a kill at the end of the slot is safe — but an
operator hitting ArrowRight / ArrowLeft (or a fade that starts before the last
`tl.at` cue) can catch a card mid-score. The outgoing slide then flashes its
opening state (hidden storefront, file back at Upload, pointer at opacity 0)
while it is still 70% visible through the 480ms crossfade.

```js
/* src/simple.template.html:5436–5439 — current */
// the outgoing slide's score owns every timer and animation it scheduled,
// so one kill retires all of it
if (tl) tl.kill();
tl = new Timeline({reduced:REDUCED});
```

```js
/* src/simple.template.html:2279–2285 — current */
kill(){
  killed = true;
  timers.forEach(clearTimeout); timers.length=0;
  anims.forEach(a=>{ try{ a.cancel(); }catch(e){} }); anims.length=0;
  teardown.forEach(fn=>{ try{ fn(); }catch(e){} }); teardown.length=0;
  cues.length=0;
  return api;
}
```

```js
/* src/simple.template.html:5907–5908 — rehearsal can hit this mid-score */
if (e.key==='ArrowRight'){ enter(idx+1); }
if (e.key==='ArrowLeft'){ enter(idx-1); }
```

The comments on Card 4 already name the trap:

```js
/* src/simple.template.html:4397–4400 */
// Same reason card 1 pins its storefront inline: leaving a card kills its
// timeline, and a cancelled WAAPI animation reverts to inline style — which
// reset() left hidden. The kill happens at the top of the outgoing crossfade,
```

`settle()` only covers the late-score case. Mid-score kills need the current
computed frame committed to inline style *before* cancel.

## Target

`Timeline.kill()` commits every live WAAPI animation’s current keyframe to
inline style, then cancels:

```js
kill(){
  killed = true;
  timers.forEach(t=>clearTimeout(t.id != null ? t.id : t)); timers.length=0;
  anims.forEach(a=>{
    try{ a.commitStyles(); }catch(e){}
    try{ a.cancel(); }catch(e){}
  }); anims.length=0;
  teardown.forEach(fn=>{ try{ fn(); }catch(e){} }); teardown.length=0;
  cues.length=0;
  return api;
}
```

`Animation.commitStyles()` writes the current interpolated values onto
`element.style`, so `cancel()` no longer reverts to `reset()`’s opening
styles. The next visit of that card still starts clean: each `setup*` already
calls `reset()` synchronously before building the new score (e.g.
`src/simple.template.html:4130`, `4373`, `4737–4749`).

Do not call `finish()` — that would jump every tween to its last keyframe and
make a mid-flight file teleport to Deliver during the fade.

## Repo conventions to follow

- Cards whose closing frame must survive exit already pin inline styles in a
  `settle*` cue (`src/simple.template.html:4239–4241`, `4524–4526`,
  `4870–4876`). Keep those cues; `commitStyles` is the mid-score complement,
  not a replacement.
- `fill:'forwards'` is already required so a tween’s first keyframe does not
  paint from t=0 (`AGENTS.md` Timeline notes). That does not survive
  `cancel()`. `commitStyles` is the missing piece of the same rule.
- If plan 005 has already turned `timers` into records, clear `t.id`; if not,
  keep `clearTimeout` on raw ids. Support both: `t.id != null ? t.id : t`.

## Steps

1. Replace the `anims.forEach(a=>{ try{ a.cancel(); }catch(e){} })` line in
   `Timeline.kill()` (`src/simple.template.html:2282`) with commit-then-cancel
   as in Target.

2. Do not add per-card freeze helpers and do not call `settle()` from
   `enter()`. A mid-Card-1 kill must leave the file where the spring had it,
   not jump to the storefront.

3. Rebuild with `python build_simple.py`.

## Boundaries

- Do NOT retune any score, duration, or easing.
- Do NOT replace `cancel()` with `finish()`.
- Do NOT commit CSS transitions (`.reveal`, `.eb-card`, `.qt-panel`). Those
  are not WAAPI and are not what flashes the opening frame.
- Do NOT edit `tools/verify_timeline.py` unless a new assertion is required
  to prove inline styles survive kill; prefer extending that file only if the
  existing “score is fully retired” check starts failing because committed
  styles look like leaked animations. They are not — `kill()` still
  `cancel()`s every animation.
- Plan 005 may land first and change timer record shape; adapt the
  `clearTimeout` line, do not revert 005.

## Verification

- **Mechanical**: `python build_simple.py`. `python tools/verify_timeline.py`
  still passes (killed timelines create no further timers).
  `python tools/check_commerce_flow.py`, `python tools/check_editor.py`, and
  `python tools/check_infrastructure.py` still pass on a *second* visit —
  `reset()` must still clear committed inline styles on re-entry.
- **Feel check**:
  - On Card 1, wait until the file is over the drop zone, press ArrowRight.
    During the 480ms fade the file must stay over the zone, not jump back to
    the left of the widget. The incoming Card 2 is unaffected.
  - On Card 4, skip ahead while the pointer is mid-throw. The pointer must
    not blink to `opacity:0` at `APPROACH[0]` during the fade.
  - On Card 6, skip ahead while the file is between Optimize and Deliver.
    It must not snap back to Upload during the fade.
  - Let a card finish normally: the existing `settle*` pin still holds the
    last frame, same as today.
  - Loop the deck without touching the keyboard: no visual change vs commit
    `e279fbe`.
  - Reduced motion: still opens on settled frames; `commitStyles` on empty
    `anims` is a no-op.
- **Done when**: skipping a card mid-score never flashes that card’s opening
  `reset()` state, and a full loop plus a second visit of Cards 1/4/6 still
  starts from their opening frames.
