# 004 — Pace card 1 for a booth, and fix its two element handovers

- **Status**: DONE (applied in the same pass; measured results at the foot of
  this file)
- **Commit**: `bb44aa7`
- **Severity**: HIGH
- **Category**: Purpose & frequency (§1), Easing & duration (§2), Cohesion (§7)
- **Estimated scope**: 1 template + 3 verifier/doc files, ~60 lines of timing

## Problem

Card 1 tells a five-step story — a file is dragged in, dropped, uploaded,
analysed, then shown live on a storefront — but every beat is timed like UI
feedback rather than like the explanatory animation it is. AUDIT.md §2 puts
marketing/explanatory motion outside the sub-300ms UI budget; this card is
built almost entirely out of 180–420ms beats, so the whole story lands in
about 3.2s inside a 5s slide.

Measured beat times in the current build (spring settle is 733ms for
`{response:.62}`, so `landed` = .30 + .733 = 1.033s):

| Beat | Time |
| --- | --- |
| file starts travelling | 0.30s |
| lands / drops | 1.03s → 1.11s |
| "1 file added" | 1.29s |
| widget → compact panel | 1.53s |
| upload ring fills | 1.71s → 2.26s |
| photo + first readout | 2.33s → 2.63s |
| trust marks visible | ~2.97s |
| `OPTIMIZED: 10 KB [-97%]` | 2.78s → 2.98s |
| storefront starts replacing it | 3.18s |

Three concrete consequences, each its own finding:

**A. The payoff is unreadable at booth distance (HIGH, §1/§2).** The line that
carries the card's whole claim finishes arriving at 2.98s and the storefront
begins wiping the panel away at 3.18s — about 200ms of hold. The upload itself
is 550ms, which reads as "nothing was uploaded" rather than as work happening.

```js
/* src/simple.template.html:3848-3853 — current */
const UPLOAD = SWAP + .18;
tl.to(arc,[{strokeDashoffset:DI_RING_LEN},{strokeDashoffset:0}],
      {at:UPLOAD,dur:.55,ease:'linear'});
const ANALYSE = UPLOAD + .62;
```

**B. The three trust marks flash (HIGH, §1).** They enter at 2.69s and are
explicitly faded out at 3.18s, so they are on screen for roughly half a second
— and because the fade-out (.22s) starts before the browser's clip reveal has
grown down to their strip at y≈1015, you watch them dim rather than being
covered. They are decoration that never gets read.

```js
/* src/simple.template.html:3866-3868, 3884-3885 — current */
badges.forEach((b,i)=>tl.to(b,
  [{opacity:0,transform:'translateY(10px)'},{opacity:.5,transform:'translateY(0)'}],
  {at:ANALYSE+.36+i*.07,dur:.28,ease:EASE.out}));
// ...
badges.forEach(b=>tl.to(b,[{opacity:.5},{opacity:0}],
  {at:SITE,dur:.22,fill:'forwards'}));
```

**C. Two handovers double-expose (MEDIUM, §7).** AUDIT.md §7 flags crossfades
that show two overlapping states. Both of these are in-place crossfades between
elements of very different size, with no spatial connection:

```js
/* src/simple.template.html:3844-3847 — current: 400px widget over a 52px row */
tl.to(widget,[{opacity:1,transform:'scale(1)'},{opacity:0,transform:'scale(.97)'}],
      {at:SWAP,dur:.20,fill:'forwards'});
tl.to(panel,[{opacity:0,transform:'scale(.97)'},{opacity:1,transform:'scale(1)'}],
      {at:SWAP+.05,dur:.24,ease:EASE.out});
```

The widget starts leaving and the panel starts arriving 50ms later over 240ms,
so for ~150ms the full uploader is visible on top of the one-file row, both
sitting between `scale(.97)` and `scale(1)` — they dissolve through each other
instead of one becoming the other. The deck already solved this exact problem
on the install card, where the label swap is deliberately asymmetric (old out
in 130ms, new starting at 120ms) with a 4px blur over the remaining overlap;
`AGENTS.md` documents that as the pattern to follow for morphing elements.

```js
/* src/simple.template.html:3858-3859 — current: label reads through the photo */
tl.to(placeholder,[{opacity:1},{opacity:0}],{at:ANALYSE,dur:.16,fill:'forwards'});
tl.to(image,[{opacity:0},{opacity:1}],{at:ANALYSE,dur:.28});
```

Both start on the same frame, so the words `UPLOAD IMAGE` sit over the
incoming photograph for about 160ms.

## Target

Phase 1 (everything before the storefront) runs roughly 2x slower, each beat
separated enough to be read across a stand, and the completed readout holds
before the storefront arrives. Phase 2 (the storefront reveal) is **unchanged**
— it is the payoff arriving and snappy is correct for it.

Exact score, replacing the beats listed above. `landed` comes from the spring's
own `onArrive`; with `{response:.86,bounce:.12}` the sampled settle is 975ms,
so `landed` ≈ 1.475s.

```js
/* target — phase 1 */
tl.to(drag,[{opacity:0},{opacity:1}],{at:.30,dur:.26});
const FROM = {x:0,y:0}, OVER = {x:235,y:81};
const FLY = {at:.50,response:.86,bounce:.12};
let landed = 1.55;

const DROP = landed + .16;
tl.to(dragCard,[{opacity:1,transform:'scale(1)'},{opacity:0,transform:'scale(.28)'}],
      {at:DROP,dur:.52,ease:EASE.inOut,fill:'forwards'});
tl.to(cursor,[{opacity:1},{opacity:0}],{at:DROP+.06,dur:.24,fill:'forwards'});
tl.at(DROP+.24,()=>{ dropText.textContent='1 file added'; });
tl.cls(drop,'hot',DROP+.40,false);

const SWAP = DROP + .85;
tl.to(widget,[{opacity:1,transform:'scale(1)',filter:'blur(0)'},
              {opacity:0,transform:'scale(.94)',filter:'blur(2px)'}],
      {at:SWAP,dur:.22,fill:'forwards'});
tl.to(panel,[{opacity:0,transform:'scale(.96)'},{opacity:1,transform:'scale(1)'}],
      {at:SWAP+.16,dur:.30,ease:EASE.out});

const UPLOAD = SWAP + .46;
tl.to(arc,[{strokeDashoffset:DI_RING_LEN},{strokeDashoffset:0}],
      {at:UPLOAD,dur:1.45,ease:'linear'});
const ANALYSE = UPLOAD + 1.85;

tl.to(placeholder,[{opacity:1},{opacity:0}],{at:ANALYSE,dur:.18,fill:'forwards'});
tl.to(image,[{opacity:0},{opacity:1}],{at:ANALYSE+.14,dur:.40});
tl.to(wash,[{clipPath:'inset(0 0 100% 0)'},{clipPath:'inset(0 0 0% 0)'}],
      {at:ANALYSE+.14,dur:.85,ease:EASE.out});
tl.to(lines[0],[{opacity:0},{opacity:1}],{at:ANALYSE+.45,dur:.26});
donut.forEach((c,i)=>tl.cls(c,'lit',ANALYSE+.20+i*.014));
tl.to(deleteButton,[{opacity:0},{opacity:.92}],{at:ANALYSE+1.00,dur:.24});
tl.to(lines[1],[{opacity:0},{opacity:1}],{at:ANALYSE+1.15,dur:.26});
tl.at(ANALYSE+1.55,()=>{ dots[0].dataset.state='standby'; });
tl.at(ANALYSE+1.62,settle);

const SITE = ANALYSE + 2.45;
```

Trust marks enter with the card and never leave; the storefront covers them,
which is honest, because the browser box (334,426,1252x814) contains their
strip entirely:

```js
/* target */
badges.forEach((b,i)=>tl.to(b,
  [{opacity:0,transform:'translateY(10px)'},{opacity:.5,transform:'translateY(0)'}],
  {at:.55+i*.09,dur:.34,ease:EASE.out}));
```

Slide duration goes 5s → 10s, making the loop 49s (10/6/6/6/5/6/10).

## Repo conventions to follow

- Motion is scored in absolute seconds on the card's `Timeline`; retiming means
  changing one number. Never convert a beat to `setTimeout`.
- Easing comes from the `EASE` map at `src/simple.template.html:1921`
  (`out:cubic-bezier(.16,1,.3,1)`, `inOut:cubic-bezier(.4,0,.2,1)`). Do not
  introduce new curves — these are the repo's strong-ease-out/ease-in-out
  tokens and match AUDIT.md's recommended values closely enough that adding a
  parallel curve would be a cohesion regression.
- `ease:'linear'` stays on the upload arc: it is constant-rate progress
  (AUDIT.md §2).
- **Exemplar for the asymmetric, blur-masked handover**: the install card's
  label swap, `setupInstall()` in the same file — old label out in 130ms, new
  one starting at 120ms, 4px blur covering the residue. `AGENTS.md` explains
  why symmetric crossfades fail there.
- A tween whose first keyframe is a state the element only reaches later must
  pass `fill:'forwards'` (documented in `AGENTS.md`).
- `reset()` runs synchronously and must clear every property a later cue
  writes, including any new `filter`.

## Steps

1. `src/simple.template.html`, `setupCommerceFlow()`: replace the phase-1 score
   with the target block above. Leave the phase-2 (`SITE`) tweens exactly as
   they are apart from deleting the badge fade-out.
2. Same function, `reset()`: add `filter:'none'` to the `widget` style
   assignment so the new blur cannot survive a loop.
3. Same function, `settle()`: set the widget's pinned exit state to
   `transform:'scale(.94)'` and `filter:'blur(2px)'` to match the tween's end.
4. Same function, `settleSite()`: delete `badges.forEach(b=>b.style.opacity='0')`
   so the marks stay at `.5` and are occluded by the browser instead of fading.
5. Same function: delete the `badges.forEach(...)` fade-out scheduled at `SITE`.
6. `DEFAULT_DECK` and `NEW.commerceFlow`: `duration:5` → `duration:10`. Update
   the stale comment above `DEFAULT_DECK` to the real sequence
   `10/6/6/6/5/6/10` (49 seconds).
7. `tools/check_commerce_flow.py`: the storefront now settles at ~8.1s, so
   raise the wait before the `late` read from 4000ms to 8600ms.
8. `tools/verify_timeline.py`: the upload ring now completes at ~4.4s, so raise
   the wait before the `late` dash read from 4000ms to 5200ms.
9. `tools/verify_simple.py`: retime card 0's `SHOTS` to
   `[700, 1600, 2600, 3600, 4900, 6100, 7400, 8600]`.
10. Update the card-1 notes in `AGENTS.md` and the loop timing in `EVENT.md`.

## Boundaries

- Do NOT touch any other card's score, CSS, or duration.
- Do NOT change card 1's markup, geometry, copy, or assets — this is timing and
  transition shape only. The Figma boxes (1252x554 process shell, 1252x814
  browser, 561x590 product slot) must stay exactly as they are.
- Do NOT add dependencies or new easing curves.
- Do NOT move the trust marks' position to keep them visible during the
  storefront; occlusion by the browser is the intended behaviour.
- If the code does not match the excerpts above, STOP and report rather than
  improvising.

## Verification

- **Mechanical**:
  - `python build_simple.py` → rebuilds `dist/uploadcare-simple.html`.
  - `python tools/check_commerce_flow.py` → all checks ok on both visits,
    including `storefront replaces process shell  site-live`.
  - `python tools/verify_timeline.py` → all timeline checks pass, no page
    errors.
  - `python tools/verify_simple.py` → `slides=7 mono=True` in both modes,
    `console issues: 0`.
- **Feel check**: load `dist/uploadcare-simple.html`, run `enter(0)` and watch
  at full speed:
  - The upload ring visibly fills over about 1.5s; it reads as work, not as a
    flicker.
  - `OPTIMIZED: 10 KB [-97%]` is on screen and still for well over a second
    before the browser starts to arrive.
  - The three trust marks are up within the first second and never dim — the
    browser page covers them.
  - At the widget → panel swap, sample frames ~60ms apart: you should never see
    a legible full uploader sitting on top of the compact row. The widget
    should read as collapsing away as the row arrives.
  - `UPLOAD IMAGE` must not be readable over the product photograph.
  - Toggle `prefers-reduced-motion`: card 1 opens directly on the storefront,
    with the trust marks occluded and no movement.
- **Done when**: the three verifiers pass, the phase-1 story spans ~7s of a 10s
  slide, and the badge opacity never returns to 0 after its entrance.

## Measured result (post-execution)

Sampled from the built deck. Step 1 of the plan used `SWAP+.12` rather than the
drafted `SWAP+.16`: at +.16 the widget's opacity reached 0 about 50ms before
the row began, so the left cell blinked empty — the same failure the dropin
card documents, in miniature. At +.12 the row rises while the widget is still
at ~.04.

| Beat | Was | Now |
| --- | --- | --- |
| drop zone lights | 0.78s | 0.80s |
| "1 file added" | 1.29s | 2.10s |
| widget → panel | 1.53s | 2.49s |
| upload ring fills | 1.71–2.26s (.55s) | 2.95–4.40s (1.45s) |
| product photo | 2.33s | 4.79–5.19s |
| `OPTIMIZED: 10 KB [-97%]` | 2.78–2.98s | 5.94–6.20s |
| storefront starts | 3.18s | 7.25s |
| storefront settled | 3.98s | ~8.10s |
| trust marks visible | 2.97s, gone by 3.40s | 0.89s onward, never fade |

Handover overlap, sampled every 30ms: peak widget/panel co-visibility 0.012
(was ~150ms of a legible uploader over the row); placeholder/photo
co-visibility 0.000 (was ~160ms of legible `UPLOAD IMAGE` over the photo).

`check_commerce_flow.py`, `verify_timeline.py` and `verify_simple.py` all pass
with `console issues: 0`.
