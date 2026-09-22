# 009 — Put entrance opacity on `--ease-out` and strengthen `--ease-in-out`

- **Status**: TODO
- **Commit**: e279fbe
- **Severity**: LOW
- **Category**: Cohesion & tokens
- **Estimated scope**: 1 source file (`src/simple.template.html`), plus regenerated `dist/uploadcare-simple.html`

## Problem

The deck already declares a motion scale, then splits it. Shared entrances
fade opacity with the CSS keyword `ease` while their `transform` uses
`--ease-out`. On-screen travel uses `--ease-in-out: cubic-bezier(.4, 0, .2, 1)`,
which is the Material default — too soft for deliberate movement. JS duplicates
the same two curves in `EASE` instead of reading the CSS tokens.

```css
/* src/simple.template.html:50–62 — current */
--ease-out:cubic-bezier(.16,1,.3,1);
--ease-in-out:cubic-bezier(.4,0,.2,1);
--ease-pop:cubic-bezier(.34,1.45,.64,1);
```

```js
/* src/simple.template.html:2093 — current */
const EASE = { out:'cubic-bezier(.16,1,.3,1)', inOut:'cubic-bezier(.4,0,.2,1)', pop:'cubic-bezier(.34,1.45,.64,1)' };
```

```css
/* src/simple.template.html:158 — current, used by Cards 1, 4, 6 headlines */
.reveal{opacity:0;transform:translateY(16px);transition:opacity var(--dur-2) ease,transform var(--dur-3) var(--ease-out)}
```

Bare `ease` on opacity also sits on the shipped 7-card path at:

- `.watermark` `src/simple.template.html:105`
- `.qt-panel` `:1169` (Card 3)
- `.qt-in` `:1181` (Card 3)
- `.eb-card` `:1588` (Card 2)
- `.eb-badge` `:1636` (Card 2)
- `.ce-edit` `:1716` (Card 4 pill)
- `.el-logo` `:1870` (Card 5)
- `.ef-ucheck` / `.ef-ubin` `:1492`, `:1497` (Card 1) — micro opacity, still
  an entrance

## Target

Keep the repo’s expo `--ease-out`. Do **not** replace it with
`cubic-bezier(0.23, 1, 0.32, 1)` — `.16, 1, .3, 1` is already the stronger
curve this file comments as “snappy expo out” (`src/simple.template.html:50–52`).

Change only `--ease-in-out` (and its JS twin) to the strong on-screen curve:

```css
--ease-out: cubic-bezier(.16, 1, .3, 1);
--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
--ease-pop: cubic-bezier(.34, 1.45, .64, 1);
```

```js
const EASE = {
  out: 'cubic-bezier(.16, 1, .3, 1)',
  inOut: 'cubic-bezier(0.77, 0, 0.175, 1)',
  pop: 'cubic-bezier(.34, 1.45, .64, 1)'
};
```

On every **entrance opacity** that currently uses the keyword `ease` *and*
already pairs it with `var(--ease-out)` on transform, swap that `ease` for
`var(--ease-out)`. Resulting pattern:

```css
.reveal{
  opacity:0;transform:translateY(16px);
  transition:opacity var(--dur-2) var(--ease-out),transform var(--dur-3) var(--ease-out);
}
```

Watermark (opacity only):

```css
.watermark{
  position:absolute;right:45px;bottom:43px;width:36px;height:auto;z-index:35;
  opacity:0;transition:opacity 600ms var(--ease-out);pointer-events:none;
}
```

Leave these **alone**:

- Color / border / background transitions that use `ease` (hover-class
  changes): `.ef-drop`, `.ei-step`, `.ce-chip` if any. Hover/color → `ease`
  is correct.
- Card 7 looping ambient that uses the CSS **keyword** `ease-in-out`
  (`.hb-globe.spin`, `.hb-dot.pulse`, `.hb-node.float .hb-inner`,
  `.hb-wave`, `.hb-wave i`, `.hb-mark path` twinkle, `.ef-dots` / `pdDot`).
  The wave comment at `src/simple.template.html:629–630` requires standard
  pendulum `ease-in-out` between stops. Substituting
  `cubic-bezier(0.77, 0, 0.175, 1)` there would make the hand mechanical.
- `ebFlash`’s `linear` (Card 2 highlight slots are timed, not eased).
- Authored cursor paths that run `ease:'linear'` so waypoint `offset`s stay
  fractions of elapsed time (Card 4 `APPROACH` / `reach()`).

## Repo conventions to follow

- Tokens live on `:root` in this file (`src/simple.template.html:50–62`).
  There is no separate tokens.css. Do not add a file.
- JS must stay in lockstep with CSS: `EASE` is the “JS twin of the CSS
  motion tokens” (`src/simple.template.html:2086–2088`).
- `--ease-pop` stays reserved for momentum landings (checkmarks, Card 6
  lockup is `--ease-out` + `scale(.94)`, not pop). Do not retarget pop.

## Steps

1. In `:root` (`src/simple.template.html:57`) set
   `--ease-in-out:cubic-bezier(0.77, 0, 0.175, 1);`

2. In `EASE` (`src/simple.template.html:2093`) set
   `inOut:'cubic-bezier(0.77, 0, 0.175, 1)'`.
   Keep `out` and `pop` byte-for-byte.

3. On the shipped 7-card selectors listed in Problem, replace the opacity
   timing-function `ease` with `var(--ease-out)` when it is part of a
   `transition:` that also moves `transform` with `--ease-out`, plus
   `.watermark`, `.ef-ubin`, `.eb-card`. Also update `.reveal.fx-blur`,
   `.reveal.fx-weight`, `.reveal.fx-stagger .w` so the shared text-fx
   presets do not reintroduce the split.

4. Optional cohesion, same file: `.lw-title` / `.lw-logo` (inherited wall,
   unused in the 7-card loop) may receive the same opacity swap if you touch
   them while editing `.qt-panel` nearby. Do not spend a pass hunting unused
   slide types.

5. Rebuild with `python build_simple.py`.

## Boundaries

- Do NOT change durations (`--dur-*`, `settings.fade`, per-card `duration`).
- Do NOT change `--ease-out` or `--ease-pop`.
- Do NOT retune Card 4 pointer paths or Card 6 `RAIL_SPRING`.
- Do NOT replace Card 7 wave/globe `ease-in-out` keywords with the token.
- If a selector uses `ease` for `border-color` or `background`, leave it.

## Verification

- **Mechanical**: `python build_simple.py`. Grep the template:
  `.reveal{` and `.eb-card{` and `.qt-panel{` opacity transitions mention
  `var(--ease-out)`, not `ease`. `EASE.inOut` contains `0.77, 0, 0.175, 1`.
  `python tools/check_infrastructure.py` still passes (travel still uses
  `EASE.inOut`, just a stronger curve; geometry must not move).
- **Feel check**:
  - Cards 1, 2, 3, 5: headline/panels/logos should feel the same speed, with
    a slightly snappier fade (less “ease” hang at the start of opacity).
  - Card 6 file travel Upload→Optimize→Deliver: still ease-in-out (accelerates
    then slows into the chip), but more decisive. If it reads as a slam,
    STOP and revert only `--ease-in-out` / `EASE.inOut`, keep the opacity
    token swap.
  - Card 4 generation veil (1.75s): still a smooth in-out, not an ease-out
    that dumps the veil on instantly.
  - Card 7 wave: still a pendulum. If the hand looks snappier at the ends,
    you accidentally replaced the keyword — revert those rules.
  - Reduced motion: unchanged (transitions are already `none`).
- **Done when**: entrance opacity and transform share `--ease-out` on the
  7-card path, `--ease-in-out` is `cubic-bezier(0.77, 0, 0.175, 1)` in both
  CSS and JS, and Card 7’s wave still uses the CSS keyword `ease-in-out`.
