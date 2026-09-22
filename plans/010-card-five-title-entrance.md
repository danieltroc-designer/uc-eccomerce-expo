# 010 — Let Card 5’s “Trusted by” rise with the logo wall

- **Status**: TODO
- **Commit**: e279fbe
- **Severity**: LOW
- **Category**: Cohesion & tokens
- **Estimated scope**: 1 source file (`src/simple.template.html`), plus regenerated `dist/uploadcare-simple.html`

## Problem

On `commerceLogos` (booth Card 5) the six marks fade and rise in reading
order, but `.el-title` is fully visible the instant the slide becomes
`.active`. The title and the wall assemble on different clocks, so the card
reads as a static caption with logos popping in under it.

```css
/* src/simple.template.html:1865–1872 — current */
.el-title{position:absolute;left:302px;top:175px;width:1316px;text-align:center;
  font-size:32px;font-weight:580;letter-spacing:-.48px;line-height:1.065;color:#bcbdc0;
  text-box-trim:trim-both;text-box-edge:cap alphabetic}
.el-logo{position:absolute;color:#fff;
  opacity:0;transform:translateY(12px);
  transition:opacity .28s ease,transform .44s var(--ease-out);
  transition-delay:calc(.12s + var(--i)*.075s)}
.slide.active .el-logo{opacity:1;transform:none}
```

```js
/* src/simple.template.html:2925–2928 — title has no reveal class */
return `<div class="el-wrap">
  ${s.title?`<div class="el-title">${esc(s.title)}</div>`:''}
  ${marks}
</div>`;
```

The inherited Webflow wall already does this correctly with `.lw-title`:

```css
/* src/simple.template.html:1218–1223 — exemplar */
.lw-title{position:absolute;top:175px;left:302px;width:1316px;text-align:center;
  font-size:32px;font-weight:580;line-height:1.065;letter-spacing:-.48px;
  color:#bcbdc0;text-box-trim:trim-both;text-box-edge:cap alphabetic;
  opacity:0;transform:translateY(12px);
  transition:opacity var(--dur-1) ease,transform var(--dur-3) var(--ease-out)}
.slide.active .lw-title{opacity:1;transform:none}
```

`.lw-logo` then waits `calc(.30s + var(--i)*.075s)` so the title leads.

## Target

Give `.el-title` the same rise as `.lw-title`, using this file’s duration
tokens. Opacity uses `--ease-out` (plan 009’s entrance rule; if 009 has not
landed, still write `var(--ease-out)` — it already exists). The title leads;
the first logo still starts at `.12s`.

```css
.el-title{position:absolute;left:302px;top:175px;width:1316px;text-align:center;
  font-size:32px;font-weight:580;letter-spacing:-.48px;line-height:1.065;color:#bcbdc0;
  text-box-trim:trim-both;text-box-edge:cap alphabetic;
  opacity:0;transform:translateY(12px);
  transition:opacity var(--dur-1) var(--ease-out),transform var(--dur-3) var(--ease-out)}
.slide.active .el-title{opacity:1;transform:none}
```

Keep `.el-logo` stagger exactly:
`transition-delay:calc(.12s + var(--i)*.075s)` — do not copy `.lw-logo`’s
`.30s` base delay. Card 5 is a 5-second slide; a 300ms title-only hold would
steal time from the six marks. `--dur-1` is `.30s`, so the title is already
well under way when logo 0 starts at 120ms, which is the lead we want.

Add `.el-title` to the reduced-motion pin next to `.el-logo`:

```css
/* src/simple.template.html:1962 — current */
.eb-card,.el-logo{transition:none!important;opacity:1!important;transform:none!important}

/* target */
.eb-card,.el-logo,.el-title{transition:none!important;opacity:1!important;transform:none!important}
```

Do not wrap the title in `.reveal`. `.reveal` translates 16px over `--dur-3`
and would fight if anyone later animates transform on `.el-wrap`. Match
`.lw-title`: opacity + 12px rise on the title node itself.

## Repo conventions to follow

- Headlines on Cards 1, 4, 6 use `.shd` / `.reveal` because those cards are
  rebuilt to `--shd-y`. Card 5’s title is a 32px caption at `(302, 175)`, same
  as `.lw-title` — copy that, not `.shd`.
- `.el-logo` already animates `transform`, which is why logos are placed with
  `left`/`top` rather than `translateX(-50%)` (`AGENTS.md` `.reveal` rule).
  The title is a full-width box; a Y-only transform is safe.
- Stagger is decorative and must not block anything; there is no interaction
  on this card.

## Steps

1. Replace the `.el-title` rule at `src/simple.template.html:1865–1867` with
   the Target block (keep geometry, type, colour, `text-box-trim` identical).

2. Add `.slide.active .el-title{opacity:1;transform:none}` immediately after
   it, before `.el-logo`.

3. Extend the reduced-motion selector at `src/simple.template.html:1962` with
   `.el-title`.

4. Do not change `commerceLogos()` markup unless `s.title` is missing a
   class — it already renders `el-title`.

5. Rebuild with `python build_simple.py`.

## Boundaries

- Do NOT move the title, change its 32px size, or restage `ECOM_WALL`.
- Do NOT change `.el-logo` delay, duration, or distance.
- Do NOT reuse `.lw-title` as a class on this card (different parent, Expo
  wall is two rows of three).
- Do NOT add a blur-masked crossfade.

## Verification

- **Mechanical**: `python build_simple.py`. `python tools/verify_simple.py`
  still clean. In a screenshot at t=0 of Card 5 (jump with `enter(4)` then
  capture immediately) the title opacity is ~0; at t=400ms it is ~1 and
  logo 0 is mid-rise.
- **Feel check**:
  - Play Card 5: “Trusted by” rises first, then the six marks in reading
    order. The title must not still be sitting at rest while logo 0 is
    moving.
  - In DevTools at 10% playback, title `transform` is `translateY(12px) → none`
    over `--dur-3` (.58s), opacity over `--dur-1` (.30s).
  - Reduced motion: title and logos are visible at rest on the first frame,
    no rise.
  - Loop the card twice: the title resets (because `.active` is toggled off
    in `enter()`), it does not stay at `opacity:1` from the previous visit.
- **Done when**: Card 5’s caption and wall share one entrance family, title
  leading by ~120ms, reduced motion still instant.
