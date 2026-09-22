# 011 — Select the Brand sage chip while Card 4 types its prompt

- **Status**: TODO
- **Commit**: e279fbe
- **Severity**: LOW
- **Category**: Missed opportunities
- **Estimated scope**: 1 source file (`src/simple.template.html`), plus regenerated `dist/uploadcare-simple.html` and a small assertion in `tools/check_editor.py` if a chip selector is easy to add

## Problem

Card 4 types the production prompt into the composer while a row of five
preset chips sits idle under it. The last chip is labelled “Brand sage
backdrop”, which is the named preset for this generation (`EVENT.md` /
`CE_PROMPT`), but nothing in the UI ever marks it selected. The typed
sentence and the chip row look like two unrelated pieces of chrome.

```js
/* src/simple.template.html:2533 — current */
const CE_PROMPT = 'Replace the background with a flat sage green studio backdrop, keep the bottle and its natural shadow';
```

```js
/* src/simple.template.html:2873–2876 — current */
<div class="ce-presets">
  ${['Clean studio white','Campaign: in hand','Forest moss','Marble shelf','Brand sage backdrop']
    .map(x=>`<span class="ce-chip">${x}</span>`).join('')}
</div>
```

```css
/* src/simple.template.html:1814–1816 — current */
.ce-presets{position:absolute;left:16px;bottom:13px;display:flex;gap:7px}
.ce-chip{padding:7px 10px;border-radius:8px;background:#f1f1f2;color:#3e3e40;
  font-size:12px;font-weight:520;line-height:1}
```

```js
/* src/simple.template.html:4478–4487 — typing never touches the chips */
const TYPE = EDITOR + .52;
tl.at(TYPE,()=>{
  promptCursor.classList.add('on');
  let i=0;
  const tick = ()=>{
    prompt.textContent = CE_PROMPT.slice(0,++i);
    if(i < CE_PROMPT.length) tl.timeout(18,tick);
  };
  tick();
});
```

Do not change `CE_PROMPT`. The typed string is the real production prompt;
the chip is its short label. Selecting the chip is the spatial link.

## Target

Mark the sage chip selected as the editor becomes the working surface, just
before typing starts. Press feedback is a colour change, not a scale (chips
are not the thing being pressed; the pointer is going to the prompt field).

```css
.ce-chip{
  padding:7px 10px;border-radius:8px;background:#f1f1f2;color:#3e3e40;
  font-size:12px;font-weight:520;line-height:1;
  transition:background-color 160ms ease, color 160ms ease;
}
.ce-chip.on{
  background:#171717;color:#fff;
}
```

160ms and `ease` are the button/color budget: press feedback 100–160ms,
hover/color → `ease`. Do not use `--ease-out` here and do not `scale()`.

Markup: add `data-preset` so JS does not match on display text:

```js
${['Clean studio white','Campaign: in hand','Forest moss','Marble shelf','Brand sage backdrop']
  .map(x=>`<span class="ce-chip" data-preset="${esc(x)}">${x}</span>`).join('')}
```

`Brand sage backdrop` is already a constant string in that array. JS:

```js
const sageChip = slideEl.querySelector('.ce-chip[data-preset="Brand sage backdrop"]');
```

In `reset()`: `sageChip && sageChip.classList.remove('on')`.

In `settle()`: `sageChip && sageChip.classList.add('on')` (reduced motion
opens on the finished editor, chip already selected).

In the score, at `TYPE` (same cue that starts typing), `tl.cls(sageChip,'on', TYPE)`.
Do not wait until the prompt has finished — the preset is chosen *then* one
types. Selecting it at `EDITOR+.08` (modal arrival) is also acceptable if it
reads as the modal opening already on that preset; prefer `TYPE` so the
selection is caused by the same beat as the first character.

Do not animate the other four chips. Do not scroll or reorder the row.

## Repo conventions to follow

- Timeline `tl.cls(el, 'on', t)` is the class-at-t helper
  (`src/simple.template.html:2220–2224`).
- `reset()` clears anything a later cue will set
  (`src/simple.template.html:4353–4373`).
- `settle()` paints the finished editor, including reduced motion
  (`src/simple.template.html:4379–4395`).
- Colour transitions use `ease` (`.ei-step` at `:1894` is the exemplar).
- Pointer still goes to `FIELD` then `GEN`; do not route it through the chip.

## Steps

1. Add `data-preset` to each `.ce-chip` in `commerceEditor()` at
   `src/simple.template.html:2873–2876`. Use `esc()` on the attribute.

2. Extend `.ce-chip` CSS at `:1815–1816` with the 160ms colour transition and
   add `.ce-chip.on` as in Target. Keep padding, radius, type unchanged for
   the rest state so the row’s layout does not shift; the selected chip is
   inverse (dark) and the same 12px type, so widths stay put. If “Brand sage
   backdrop” grows because white text measures wider, that is unacceptable —
   the chips are `padding:7px 10px` with no min-width. Verify in a screenshot
   that the five chips do not wrap or shove `.ce-ratio`. If they do, keep
   colours but give `.ce-chip` `box-sizing:border-box` only (already on `*`)
   and do **not** add a border to `.on`.

3. In `setupCommerceEditor`, query `sageChip`. `reset` removes `on`; `settle`
   adds `on`; `tl.cls(sageChip, 'on', TYPE)` in the motion score. If `sageChip`
   is null (prompt rewrite), skip — do not throw.

4. Rebuild with `python build_simple.py`.

5. Optional: in `tools/check_editor.py`, after the prompt-visible assertion,
   assert `document.querySelector('.ce-chip.on')` text is
   `Brand sage backdrop` during typing. If the checker’s `read()` snapshot
   has no cheap place for this, skip the checker and rely on the feel check.

## Boundaries

- Do NOT change `CE_PROMPT`, result UUID, or pointer paths.
- Do NOT click the chip with the cursor.
- Do NOT add a new chip, remove chips, or restyle the unselected rest state
  beyond the transition property.
- Do NOT use `scale(0)` or `scale(0.9)` on the chip.
- Do NOT edit `src/index.template.html`.

## Verification

- **Mechanical**: `python build_simple.py`. `python tools/check_editor.py`
  still passes (pointer sequence, backend freeze, reduced storefront).
- **Feel check**:
  - Card 4: backend has no selected chip. When the editor opens and the
    first character lands, “Brand sage backdrop” is already (or becomes)
    dark-on-white inverse. The other four chips stay grey.
  - In DevTools at 10%, the fill colour interpolates over 160ms; it does not
    pop on a single frame unless reduced motion.
  - Reduced motion: editor+storefront settled path still runs; if settle()
    is skipped because reduced jumps to the storefront, the chip may never
    show — that is fine. If reduced still paints the editor first, the chip
    is `on`.
  - Re-entry: `reset()` clears `on` before the backend phase, so the chip is
    not pre-selected on the product page.
- **Done when**: a visitor can see which preset produced the sage result
  without reading the whole prompt, and nothing in the pointer score moved.
