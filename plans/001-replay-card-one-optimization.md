# 001 — Replay card 1 optimization on every loop

- **Status**: TODO
- **Commit**: e122bf0
- **Severity**: HIGH
- **Category**: Interruptibility
- **Estimated scope**: 2 source/test files plus regenerated `dist/uploadcare-simple.html`; under 20 lines

## Problem

Card 1's sharpen animation is not scoped to the active slide:

```css
/* src/simple.template.html:1443 — current */
.ef-opt .ef-photo img {
  filter: saturate(.86) brightness(.82) blur(3px);
  animation: efCrisp .65s var(--ease-out) 1.12s forwards;
}
```

`renderDeck()` creates every slide at startup:

```js
/* src/simple.template.html:2928–2937 — current */
function renderDeck(){
  slidesEl.innerHTML = '';
  deck.slides.forEach(s=>{
    const el = document.createElement('div');
    el.className = 'slide';
    el.style.setProperty('--fade', (deck.settings.fade||900)+'ms');
    el.innerHTML = (R[s.type]||R.statement)(s);
    applyTextFx(el, s.textFx);
    slidesEl.appendChild(el);
  });
}
```

The animation therefore starts when the DOM is rendered, not when card 1
becomes active. It happens to look correct on the first pass because card 1 is
the opening card. On later loops, the animation has already filled forwards and
the image begins fully crisp. A browser measurement confirmed that 50ms after
re-entering card 1 the computed filter was still
`saturate(1) brightness(1) blur(0px)`.

## Target

Keep the existing 650ms sharpen, 1.12s delay, `--ease-out` curve, and 3px blur,
but make the animation exist only while card 1 is active:

```css
/* target */
.ef-opt .ef-photo img {
  filter: saturate(.86) brightness(.82) blur(3px);
}
.slide.active .ef-opt .ef-photo img {
  animation: efCrisp .65s var(--ease-out) 1.12s forwards;
}
```

Removing `.active` must remove the filled animation and restore the base
filtered state while the card is hidden. Adding `.active` again must create a
fresh animation from that base state.

## Repo conventions to follow

- Per-card CSS animations are scoped to `.slide.active` so they restart on each
  visit. `src/simple.template.html:1433` does this correctly for `efUpload`:

```css
.slide.active .ef-upload .ef-photo {
  animation: efUpload 5s var(--ease-out) both;
}
```

- Reduced motion already pins this image to `filter:none!important` at
  `src/simple.template.html:1633`; retain that behavior.
- Edit the source template only, then regenerate the distribution file with
  `python3 build_simple.py`.

## Steps

1. In `src/simple.template.html`, leave the initial filter declaration on
   `.ef-opt .ef-photo img` but move its `animation` declaration to a new
   `.slide.active .ef-opt .ef-photo img` rule.
2. In `tools/verify_timeline.py`, extend the card 1 replay check:
   - Let the first optimization finish.
   - Enter card 2, then re-enter card 1.
   - At 50ms after re-entry, assert the computed filter still contains a
     nonzero blur.
   - At 1900ms, assert the filter is `blur(0px)`.
3. Run `python3 build_simple.py` to regenerate
   `dist/uploadcare-simple.html`.

## Boundaries

- Do not change the delay, duration, filter values, or easing.
- Do not replace the effect with JavaScript or the `Timeline` class.
- Do not change card 1 layout, copy, image source, upload meter, or store-page
  reveal.
- Do not edit `dist/uploadcare-simple.html` by hand.
- Do not add dependencies.
- If the cited selector or `renderDeck()` lifecycle has changed since commit
  `e122bf0`, stop and report the drift instead of improvising.

## Verification

- **Mechanical**:
  - `python3 build_simple.py` completes successfully.
  - `python3 tools/verify_timeline.py` reports all checks passed.
  - `python3 tools/verify_simple.py` reports 7 slides, fonts loaded, and zero
    console issues in normal and reduced-motion modes.
- **Feel check**:
  - Open `dist/uploadcare-simple.html`, let the complete 38-second loop run
    twice, and watch card 1 both times.
  - In Chrome DevTools Animations, set playback to 10%. Confirm the optimization
    image begins dimmer and blurred, then becomes crisp at the same moment on
    both visits.
  - Manually press Right Arrow to leave card 1 and Left Arrow to return; confirm
    the sharpen restarts rather than inheriting the completed frame.
  - Enable reduced motion and confirm the image is crisp immediately.
- **Done when**: The computed filter contains blur at 50ms after every card 1
  entry and reaches `blur(0px)` after the existing animation completes.
