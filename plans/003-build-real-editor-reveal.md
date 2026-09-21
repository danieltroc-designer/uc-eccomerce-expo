# 003 — Make card 4 a real before/after reveal

- **Status**: OBSOLETE — superseded by the upload → prompt → AI Enhancer flow
- **Commit**: e122bf0
- **Severity**: HIGH
- **Category**: Purpose
- **Estimated scope**: 2 source/test files plus regenerated `dist/uploadcare-simple.html`; about 80 lines

## Problem

> This plan targeted the previous two-pane placeholder and then a one-well
> wipe. Card 4 has since been rebuilt around the production standalone AI
> Enhancer: it reuses Card 1's source, types the exact production prompt,
> reproduces the tool's pending shimmer, and settles on the genuine generated
> result recorded in `EVENT.md`. Do not execute the old geometry below.

Card 4 currently creates two side-by-side panes:

```js
/* src/simple.template.html:2327–2335 — current */
commerceEditor(s){
  const ready = !!(ECOMMERCE.editorBefore && ECOMMERCE.editorAfter);
  const pane = (src,label)=>ready
    ? `<div class="ee-pane"><img src="${esc(src)}" alt=""><span class="ee-pane-label">${label}</span></div>`
    : `<div class="ee-pane"><div class="ee-pending">Genuine AI Image Editor<br>${label.toLowerCase()} asset needed</div><span class="ee-pane-label">${label}</span></div>`;
  return `<div class="ee-wrap">
    <div class="ec-head reveal">${esc(s.heading||'')}</div>
    <div class="ee-demo">${pane(ECOMMERCE.editorBefore,'Before')}${pane(ECOMMERCE.editorAfter,'Catalog ready')}<i class="ee-wipe"></i></div>
  </div>`;
}
```

The CSS keeps both images static while an unrelated line changes `left`:

```css
/* src/simple.template.html:1518–1534 — current */
.ee-demo {
  position:absolute;
  left:350px;
  top:390px;
  width:1220px;
  height:470px;
  overflow:hidden;
  display:grid;
  grid-template-columns:1fr 1fr;
}
.ee-pane { position:relative; overflow:hidden; }
.ee-wipe {
  position:absolute;
  left:50%;
  top:0;
  bottom:0;
  width:2px;
  opacity:0;
}
.slide.active .ee-wipe {
  animation:eeWipe 1.1s var(--ease-in-out) .65s both;
}
@keyframes eeWipe {
  0% { left:8%; opacity:0; }
  10% { opacity:1; }
  90% { opacity:1; }
  100% { left:92%; opacity:0; }
}
```

This does not show a before/after transformation. Even when genuine assets are
present, viewers see two comparison images while a line scans over them. It
also animates `left`, causing per-frame layout and paint. When assets are
missing, the line still scans across the asset-needed placeholder despite
having nothing to reveal.

## Target

When both genuine images exist:

1. Stack `editor-before.jpg` and `editor-after.jpg` in the same 1220×470 frame.
2. Show the full before image initially.
3. Reveal the after image from left to right with
   `clip-path:inset(0 100% 0 0)` to `clip-path:inset(0 0 0 0)`.
4. Move the 2px divider from 8% to 92% using
   `transform:translateX(0)` to `transform:translateX(1025px)`, not `left`.
   The travel is `1220 × (0.92 - 0.08) = 1024.8px`, rounded to 1025px.
5. Run reveal and divider together for the existing 1.1s, after the existing
   650ms delay, with the existing `--ease-in-out`.
6. Keep the product perfectly registered between frames: identical image box,
   `object-fit:cover`, and object position.
7. Do not animate anything when either asset is absent.

Target structure:

```html
<div class="ee-demo is-ready">
  <div class="ee-layer ee-before">
    <img src="...editorBefore..." alt="">
    <span class="ee-pane-label">Before</span>
  </div>
  <div class="ee-layer ee-after">
    <img src="...editorAfter..." alt="">
    <span class="ee-pane-label">Catalog ready</span>
  </div>
  <i class="ee-wipe"></i>
</div>
```

Target motion:

```css
.ee-layer {
  position:absolute;
  inset:0;
  overflow:hidden;
}
.ee-layer img {
  width:100%;
  height:100%;
  object-fit:cover;
  object-position:center;
}
.ee-after {
  clip-path:inset(0 100% 0 0);
}
.ee-wipe {
  left:8%;
  transform:translateX(0);
}
.slide.active .ee-demo.is-ready .ee-after {
  animation:eeReveal 1.1s var(--ease-in-out) .65s forwards;
}
.slide.active .ee-demo.is-ready .ee-wipe {
  animation:eeWipe 1.1s var(--ease-in-out) .65s both;
}
@keyframes eeReveal {
  to { clip-path:inset(0 0 0 0); }
}
@keyframes eeWipe {
  0% { opacity:0; transform:translateX(0); }
  10% { opacity:1; }
  90% { opacity:1; }
  100% { opacity:0; transform:translateX(1025px); }
}
```

Keep a single centered pending panel when assets are absent:

```html
<div class="ee-demo is-pending">
  <div class="ee-pending">
    Genuine AI Image Editor<br>before/after assets needed
  </div>
</div>
```

No `.ee-wipe` should exist in pending markup.

## Repo conventions to follow

- Optional images are already loaded into `ECOMMERCE.editorBefore` and
  `ECOMMERCE.editorAfter` by `build_simple.py`; do not add another asset path or
  runtime request.
- The deck must remain fully offline.
- Predetermined explanatory motion belongs in CSS and is scoped to
  `.slide.active` so it restarts every loop.
- `clip-path:inset()` is already an accepted reveal mechanism in this codebase
  (`.wf-sweep` at `src/simple.template.html:1287–1290`).
- Reduced motion should show the completed catalog-ready image immediately,
  with no divider travel.

## Steps

1. Rewrite `R.commerceEditor` in `src/simple.template.html`:
   - Compute `ready` exactly as it does now.
   - For ready state, emit two stacked `.ee-layer` elements plus `.ee-wipe`.
   - For missing assets, emit one `.ee-pending` element and no wipe.
   - Add `is-ready` or `is-pending` to `.ee-demo`.
2. Replace the two-column grid rules with absolute stacked-layer rules.
3. Add `eeReveal` and change `eeWipe` to transform-based travel using the exact
   target values above.
4. Ensure both labels remain legible:
   - “Before” belongs to the bottom layer.
   - “Catalog ready” belongs to the revealed layer and becomes visible only as
     that area is revealed.
5. Update reduced-motion CSS:
   - `.ee-after{clip-path:inset(0)!important}`.
   - `.ee-wipe{display:none!important}`.
   - The pending state remains unchanged.
6. Update `tools/verify_simple.py` card 4 captures if needed so screenshots
   include pre-reveal, mid-wipe, and completed states.
7. Add a focused browser assertion:
   - Pending build: no `.ee-wipe` exists.
   - Ready build: after the animation, `.ee-after` computes to
     `clip-path:inset(0px)` or the browser-equivalent zero inset.
8. Run `python3 build_simple.py`.

## Boundaries

- Do not create, generate, retouch, or approximate the before/after images.
- Do not begin implementation until genuine `assets/ecommerce/editor-before.jpg`
  and `assets/ecommerce/editor-after.jpg` are available for the visual
  verification pass. Structural code may be prepared only if the executor can
  retain and verify the honest pending state.
- Do not alter the product itself between frames; only the background may
  change.
- Do not introduce draggable comparison UI, a replay button, controls, or
  pointer interaction. This is an autoplay booth card.
- Do not change the headline, six-second card duration, frame geometry, or
  global slide fade.
- Do not modify `build_simple.py` asset names or add runtime network requests.
- Do not edit `dist/uploadcare-simple.html` by hand.
- Do not add dependencies.
- If the renderer or asset keys have drifted since commit `e122bf0`, stop and
  report instead of guessing.

## Verification

- **Mechanical**:
  - `python3 build_simple.py` succeeds with and without the optional editor
    files.
  - `python3 tools/verify_simple.py` reports 7 slides, loaded fonts, and zero
    console issues in normal and reduced-motion modes.
  - `python3 tools/verify_timeline.py` passes.
  - `rg "@keyframes eeWipe.*left:" src/simple.template.html` returns no match.
- **Feel check**:
  - Use the genuine before/after pair and view card 4 at 10% playback speed.
  - Confirm the product does not jump, resize, or change position at the reveal
    boundary. Only the background changes.
  - Confirm the divider sits exactly on the reveal boundary throughout; it must
    never lead or trail the new image.
  - At normal speed, the transition should read as one smooth transformation,
    not two images crossfading and not a scanner line passing over a static
    comparison.
  - Leave and re-enter card 4; the before state and reveal must restart cleanly.
  - Enable reduced motion: the final catalog-ready image should appear
    immediately, with no moving divider.
  - Remove either editor asset and rebuild: the honest asset-needed panel should
    appear, with no animated wipe.
- **Done when**: Genuine input cleanly reveals into genuine editor output in one
  registered frame, the divider tracks the boundary, the sequence replays every
  loop, and missing assets never imply that a transformation occurred.
