# 005 — Pause and resume the active card’s motion with the deck clock

- **Status**: TODO
- **Commit**: e279fbe
- **Severity**: MEDIUM
- **Category**: Interruptibility
- **Estimated scope**: 1 source file (`src/simple.template.html`), plus regenerated `dist/uploadcare-simple.html`

## Problem

Space toggles `togglePlay()`, which only stops the *advance* timer and the
progress tick. The active card’s Timeline (WAAPI, `setTimeout` cues, typing)
and its CSS animations keep running. A paused booth loop, or a rehearsal
pause, still finishes the story under the frozen progress bar.

```js
/* src/simple.template.html:5491–5496 — current */
function pause(){
  playing=false; clearTimeout(timer); clearInterval(tickTimer);
  elapsedBeforePause += performance.now()-slideStart;
}
function resume(){ playing=true; slideStart=performance.now(); arm(); }
function togglePlay(){ playing ? pause() : resume(); }
```

```js
/* src/simple.template.html:2279–2285 — Timeline.kill only; no pause/resume */
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
/* src/simple.template.html:5909 — Space is the pause control */
if (e.key===' '){ e.preventDefault(); togglePlay(); }
```

CSS loops on the active card (Card 2 `ebFlash`, Card 7 globe / float /
twinkle / wave) are not keyed off `playing` at all.

## Target

While `playing === false`:

- every WAAPI animation owned by the active `Timeline` is `pause()`d
- every pending Timeline timeout is frozen with its remaining delay
- CSS animations on the active slide (and substrate blips) use
  `animation-play-state: paused`
- substrate spawning does not add new blips
- the progress hairline stays where it was (plan 007 owns how it is drawn)

On `resume()`:

- WAAPI `play()`s from the paused frame (not from zero)
- remaining Timeline timeouts are rescheduled
- CSS `animation-play-state` returns to `running`

Exact CSS:

```css
#stage.deck-paused .slide.active,
#stage.deck-paused .slide.active *,
#stage.deck-paused .sb-blip{
  animation-play-state: paused !important;
}
```

Do **not** set `transition: none` here. Slide crossfades and CSS entrance
transitions are not what Space is pausing; interrupting them would pop the
outgoing card.

## Repo conventions to follow

- One `Timeline` per slide already owns every timer and WAAPI animation
  (`src/simple.template.html:2196–2288`). Extend that object; do not add a
  second pause system.
- `enter()` already calls `tl.kill()` before building a new score
  (`src/simple.template.html:5438`). Kill must still cancel, not pause.
- Reduced-motion cards that skip building a score (`if (REDUCED){ settle();
  return; }`) have nothing to pause; `tl.pause()` must be a no-op on an empty
  timeline.
- Exemplar for scoped CSS on the active card: `.slide.active .eb-card::before`
  at `src/simple.template.html:1623–1625`.

## Steps

1. In `Timeline()` (`src/simple.template.html:2196`), change `timers` from an
   array of timeout ids into an array of records `{id, fn, due, remaining}`.
   `timeout(ms, fn)` and `play()`’s `setTimeout` wrappers both push records
   whose `due` is `performance.now() + delay`.

2. Add `pause()` and `resume()` on the Timeline API, next to `kill()`:

```js
pause(){
  if (killed || paused) return api;
  paused = true;
  const now = performance.now();
  timers.forEach(t=>{
    clearTimeout(t.id);
    t.remaining = Math.max(0, t.due - now);
  });
  anims.forEach(a=>{ try{ a.pause(); }catch(e){} });
  return api;
},
resume(){
  if (killed || !paused) return api;
  paused = false;
  const now = performance.now();
  timers.forEach(t=>{
    t.due = now + t.remaining;
    t.id = setTimeout(()=>{ if(!killed && !paused) t.fn(); }, t.remaining);
  });
  anims.forEach(a=>{ try{ a.play(); }catch(e){} });
  return api;
},
```

3. Update `kill()` to `timers.forEach(t=>clearTimeout(t.id))` instead of
   `timers.forEach(clearTimeout)`.

4. Guard `timeout()` so a call while `paused` still records the delay against
   `due = performance.now() + ms` but does not schedule until `resume()`
   (or simply do not call `timeout` while paused — recursive typing is already
   on the timeline; pausing mid-tick must freeze the next `tl.timeout(18,tick)`
   as a record with `remaining`).

5. Add the `#stage.deck-paused` CSS rule in the Playback / stage section near
   `#progress` (`src/simple.template.html:140–148`).

6. Change `pause()` / `resume()`:

```js
function pause(){
  playing=false; clearTimeout(timer); clearInterval(tickTimer);
  elapsedBeforePause += performance.now()-slideStart;
  if (tl) tl.pause();
  stageEl.classList.add('deck-paused');
}
function resume(){
  playing=true; slideStart=performance.now();
  stageEl.classList.remove('deck-paused');
  if (tl) tl.resume();
  arm();
}
```

7. In `startSubstrate()`’s `spawn()` (`src/simple.template.html:3496`), skip
   creating a blip when `!playing`, but keep the recursive `setTimeout` so
   spawning resumes after play.

8. Rebuild with `python build_simple.py`. Do not hand-edit `dist/`.

## Boundaries

- Do NOT change slide durations, scores, or easing.
- Do NOT pause `#stage` CSS *transitions* (slide fade, `.reveal`).
- Do NOT add a library. WAAPI `Animation.pause()` / `play()` is the API.
- Do NOT change `tl.kill()` semantics other than reading `t.id` from records.
- If `Timeline` no longer stores `anims` / `timers` as described at commit
  `e279fbe`, STOP and report.

## Verification

- **Mechanical**: `python build_simple.py` succeeds. `python tools/verify_timeline.py`
  still passes (exit still retires the score).
- **Feel check**:
  - Open `dist/uploadcare-simple.html`, wait until Card 1’s file is mid-flight,
    press Space. The file, cursor, and progress hairline must freeze on that
    frame. Press Space again: they continue from that frame, not from the
    start of the throw.
  - On Card 2, pause during a highlight: the wash holds; resume continues the
    same pass, it does not restart `ebFlash` from 0%.
  - On Card 4, pause while the prompt is typing: no further characters appear
    until resume, then typing continues (not a full reset).
  - In DevTools Animations panel at 10%, pause mid-Card-6 travel and confirm
    WAAPI animations go to paused, not finished/cancelled.
  - Toggle `prefers-reduced-motion`: Space still pauses advance; there is no
    WAAPI to freeze, and the settled frame stays settled.
- **Done when**: a Space pause freezes every visible motion on the active card
  and resume continues it, and autoplay advance still uses the remaining
  `slideDuration` (pause does not stretch or shrink the card’s slot).
