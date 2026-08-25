# AGENTS.md — orientation for coding agents

Read this before editing. It tells you what this project is, the one rule that
matters, and exactly where things live.

## What this is

A single-file, auto-playing 16:9 HTML slide deck shown on trade-fair TVs for
Uploadcare. Vanilla HTML/CSS/JS — **no framework, no bundler, no npm.** The only
tooling is a Python build step (`build.py`) that inlines assets. Keep it that
way unless explicitly asked otherwise.

## The one rule

**Edit `src/index.template.html` and `assets/`. Never hand-edit
`dist/uploadcare-show.html`** — it is generated. After any change run:

```bash
python build.py
```

`dist/uploadcare-show.html` is the artifact that goes on the TV. If you edit it
directly, your changes are lost on the next build and the source drifts out of
sync.

### Second deck: the simplified booth loop

There is a parallel, shorter 7-card cut for the Webflow booth. It has its own
source + build + output and is fully independent of the main deck:

- Source: `src/simple.template.html` (a superset copy of the main template with
  extra card types: `dropin`, `features`, `quote2`, `logos`, `scale`,
  `pipeline`). Card 7 is a `board` slide with `layout:'outro'` and `qr:true`.
- Build: `python build_simple.py` → `dist/uploadcare-simple.html`.
- Same rule applies: never hand-edit `dist/uploadcare-simple.html`.
- `build_simple.py` reuses every encoder from `build.py` and adds four tokens
  of its own: `__QR_SVG__` (the card-7 QR — destination is `CTA_URL`, generated
  with the optional `segno` dependency), `__LOGOS_JSON__` (the customer marks
  in `assets/logos/`), `__UPLOADERUI_JSON__` (the uploader widget's icons
  and the two file thumbnails in `assets/uploader/`, exported at 240x300 so one
  file serves both the 120x150 drag card and the 32px row thumb), and
  `__DEMO_JSON__` (the pipeline card's photo and its three transformed frames,
  in `assets/demo/`), and `__CAPS_JSON__` (card 2's capability icons in
  `assets/caps/`, which carry their own accent colours and so can't be
  recoloured from CSS).

Card 6 is a port of the three-panel demo on the marketing site
(upload | analyse | deliver). Two things about it differ from the original and
should stay that way: it **plays once and has no Replay button** — a booth
screen has nobody to press it, and the deck re-runs the card each loop anyway —
and its type is set at 20px rather than the site's 13px, with the boxes
rescaled around that, because the card is read from across a stand. Its frames
in `assets/demo/` are the CDN's own renders of the three transforms the
on-screen URL builds (`crop/face` → `scale_crop` → `border_radius`), so
changing a transform in `PD_TRANSFORMS` means re-fetching the matching frame.

Card 1 is the real uploader widget playing its whole story: a stack of two
files is dragged in under a single cursor, dropped, and the widget hands over
to the compact "Uploading N files" panel, where each file fills its ring and
settles into a checkmark plus a bin before the window dismisses itself. The
travel is a spring rather than a tween, because a dragged object carries
momentum; `tl.spring()` reports its settle time synchronously through
`onArrive`, and the rest of the score is written against that, so the drop
always follows the landing however the spring is retuned. The progress ring is
drawn in the template (`DI_RING`) rather than exported, because the storyboard's
icon is a snapshot at one arbitrary percentage and this one has to fill.

Card 2 is the storyboard's capability row: five 265x316 panels that rise in a
70ms stagger, each icon tile landing a beat after its own card. Above them sits
a status chip running `LOADER` — four squares stepping round a 2x2 ring. All
four share one set of keyframes and one start position; the negative
`animation-delay` is what spreads them around the ring, so the whole loop
retimes from `--ld-dur` alone. Two squares carry the highlight, which is what
makes the bright pair sweep instead of the ring reading as uniform. Reduced
motion has to pin each square to its own corner explicitly, or they collapse
into a single stack.

This deck is laid out directly against the Figma storyboard ("Storyboard –
Webflow – 2"). Three conventions come from there and are worth keeping:

- **Headlines are anchored, not centred.** Every card pins its headline to
  `--head-y` (205px) rather than centring the column, so type doesn't shift as
  the deck advances. Cards position their supporting art at the storyboard's
  own coordinates — the stage is a native 1920x1080, so Figma numbers are used
  verbatim.
- **The wireframe globe belongs to card 7 only.** The ambient substrate behind
  the other cards is now just the occasional signal blip in the margins; the
  globe read as wallpaper everywhere except the payoff, so it was removed from
  `#substrate` and lives solely in `.hb-globe`. Card 7 still switches the
  substrate off (`sb-off`) so the blips don't duplicate the board's own dots.
- **The rebuilt headline block is `.shd`** — an 88px title over a 32px sub, both
  Inter 580, trimmed to their cap box with `text-box-trim` so they land on the
  storyboard's y=168 and y=264 exactly rather than by eye. Card 1 uses it; the
  rest still sit on `--head-y` and adopt `.shd` as they get rebuilt. Because
  Figma trims to the cap box, any element measured against it needs the same
  trim, or it will read ~21px low at 88px.
- **`.reveal` animates `transform`.** Anything wearing it must be centred with
  an explicit `left` offset, never `translateX(-50%)`, or the two rules fight
  and the element slides sideways as it enters.

### Choreography: the `Timeline`

Cards don't schedule their own timers. `enter()` builds one `Timeline` per
slide, hands it to that card's `setup*` function, and calls `play()`; moving to
the next slide is a single `tl.kill()` that retires every timer and animation
the card scheduled. A card's choreography is written as a score in absolute
seconds, so retiming a beat means changing one number:

```js
tl.cls(zone, 'hot', 1.95);                            // class on at t
tl.cls(zone, 'hot', 3.45, false);                     // ...and off again
tl.to(card, [{opacity:0},{opacity:1}], {dur:.4, at:2.45});
tl.spring(cursor, START, OVER, {at:.9, onArrive:t=>arrive=t});
tl.at(2.95, ()=>txt.textContent='2 files added');
```

`tl.timeout(ms, fn)` is the escape hatch for recursive work that isn't a fixed
score (the two typewriters); it's still owned by the timeline, so it dies with
it. `spring()` reports its settle time through `onArrive` synchronously, which
is how the cursor demos anchor the tap that follows the travel. `tl.anim(a)`
adopts an animation the card had to start itself — usually because a keyframe
can only be measured at the moment it runs, like the pipeline card's
`height:auto` rows — and `tl.onKill(fn)` registers teardown for anything with a
lifetime of its own, such as that card's `requestAnimationFrame` canvas.

Three things to keep in mind when adding a card:

- **Reset state synchronously, schedule the animation.** The deck loops, so a
  card is re-entered with the previous visit's DOM intact. Anything a cue will
  later overwrite must be cleared while the score is being *built*, not when
  the cue fires, or the card shows a stale frame until then.
- **Reduced motion collapses the score.** Tweens jump to their last keyframe
  and cues fire in time order at `play()`. Where the settled frame is
  deliberately *not* the end of the animation (card 1 holds the files above the
  zone rather than dropping them), branch on `REDUCED` and return before
  building a score.
- **A tween that removes something must not fill backwards.** `tl.to()` defaults
  to `fill:'both'`, so an exit tween opening on `{opacity:1}` paints that
  keyframe from t=0 and the element is on screen before it ever arrived. Pass
  `fill:'forwards'` whenever the first keyframe is the visible state.

Verify with `python tools/verify_simple.py`, which screenshots all eight cards
in both normal and reduced motion to `tools/_shots/` and fails loudly on
console errors, and `python tools/verify_timeline.py`, which asserts a slide's
score is fully retired on exit and replays from the top on re-entry.

The template contains placeholder tokens that `build.py` fills:
`/*__COMMIT_MONO__*/`, `/*__INTER_VAR__*/`, `/*__JB_MONO__*/`, `__LOGO_SVG__`,
`__GLOBE_SVG__`, `__GLYPH_SVG__`, `__ASSETS_JSON__`, `__UPLOADER_JSON__`,
`__PIXEL_JSON__`. `__GLYPH_SVG__` is the pixel glyph shown bottom-right on every
slide. Layout is authored against an invisible Swiss grid (75px margins, 4x4
modules — CSS vars `--gm`/`--gcol`/`--grow`/`--g2` on `:root`); press **g** to
toggle the grid overlay for design checks.
Don't remove or rename them. `__PIXEL_JSON__` carries the dot-halftone data
(parsed from `assets/photos/Pixelated-image.svg`) plus the inlined
`Full-image.png`; the reveal slide's `startPixelReveal` paints the dots on a
canvas and dissolves them into the photo.

## Verify your work

There is no test suite; verify visually. If a headless browser is available
(e.g. Playwright), load `dist/uploadcare-show.html`, call `enter(n)` in the page
to jump to slide *n*, wait, and screenshot. Otherwise open it in a browser and
check the slide you touched. Also confirm `document.fonts.check("18px 'Commit
Mono'")` is `true` and the console is clean.

## Architecture in one breath

A `deck` object (`{ settings, slides:[…] }`) drives everything. Each slide has a
`type`; a renderer in the `R` map turns it into DOM; `enter(i)` activates a slide
and kicks off its animations; the editor panel reads/writes the same `deck` and
re-renders live. Slides are pure data — copy, order, durations, and per-slide
options are just fields. Assets (photos/logo/globe/fonts) are the only things
that require a rebuild.

## Where things live in `src/index.template.html`

CSS (in `<style>`):
- L37  `#stage` — the fixed 1920×1080 stage that scales to any screen
- L85–155 per-slide-type styles (`statement`, `number`, `chart`, `stats`, logo)
- L157 `HERO BOARD SLIDE` — globe, floating `.hb-node`s, `.hb-meta` terminal text
- L242 `EDITOR` — the slide-out control panel

JS (in the last `<script>`):
- L430 `DEFAULT_DECK` — the shipped deck; edit here to change default content
- L471 stage scaling (`fit()`)
- L483 `R = { … }` — **the renderers**, one function per slide type
- L608 `fitText()` — auto-shrinks oversized headlines to fit
- L636 `buildChart()` — the self-drawing line chart
- L676 `animateLogo()` — the six logo choreographies (`switch(variant)`)
- L832 `BOARD_META` — the terminal readout content for the file board
- L918 `setupBoard()` — globe spin, photo float, and typewriter wiring
- `enter()` — slide activation + animation dispatch (add new types here)
- `applyTextFx()` / `wrapWords()` (just after `multiline()`) — the shared
  "Text animation" system (rise/blur/weight/stagger). Runs once per slide
  inside `renderDeck()`, driven by each slide's `textFx` field. `fx-weight`
  needs the Inter Variable font; `fx-stagger` word-wraps plain-text
  `.reveal` elements only (skips structural containers automatically).
- editor: `TYPE_LABEL`, `slideTitle()`, `TEXT_FX_LABEL`/`textFxFieldHTML()`,
  `fieldsFor()` (per-type controls — every case gets the shared text-fx
  control for free via the `dur` prefix), the `NEW` templates, and the
  add-slide menu

## Common tasks

**Change default copy / numbers / order:** edit `DEFAULT_DECK` (L430). No asset
change → still run `build.py` to refresh `dist/`.

**Add a new slide type:** (1) add a renderer to `R`; (2) add its CSS; (3) if it
animates, dispatch it in `enter()`; (4) register it in `TYPE_LABEL`,
`slideTitle()`, `fieldsFor()`, the `NEW` templates, and the add-slide menu so the
editor supports it. Follow `board`/`logoAnim` as the fullest examples.

**Swap a photo:** replace `assets/photos/<name>.png` (keep the filename) and
rebuild. Sizing/quality knobs: `PHOTO_SPEC` and `JPEG_QUALITY` in `build.py`.
Photo keys used by the board: `tennis`, `blonde` (portrait.png), `car`, `docx`.

**New logo / globe:** replace the SVG under `assets/brand/` and rebuild. The logo
is made responsive by `prepare_logo()` in `build.py` (it strips the fixed
width/height so CSS controls size). If your SVG differs structurally, check that
still works.

**Tune motion:** float animation lives in the `.hb-node.float …` CSS + the
`fdur`/`--fdelay` setup in `setupBoard()`; the typewriter is `typeMeta()` /
`BOARD_META`; the logo animations are in `animateLogo()`.

## Conventions & gotchas

- Brand palette: bg `#090909`, mark yellow `#FFCF3E`, status green `#008B4B`
  (`--ok`), terminal grey `#8E8E8E`, footer grey `#595959`. Use the CSS vars.
- Fonts: Inter Variable (display, `--sans`), JetBrains Mono (`--mono`), Commit
  Mono (`--cmono`, terminal). All three are embedded as base64 woff2 (see
  `encode_fonts`/`encode_variable_font`/`encode_jbmono` in `build.py`), so
  everything works fully offline — don't replace any of them with a bare CDN
  link. Inter is embedded as a single ranged (`100 900`) variable font on
  purpose: it's what lets the "weight morph" text animation (see
  `TEXT_FX_LABEL`) interpolate `font-weight` smoothly instead of snapping
  between static instances.
- Everything is positioned inside the 1920×1080 stage; use px within that frame,
  not viewport units. The stage handles scaling to the TV.
- Respect `REDUCED` (prefers-reduced-motion): new animations should no-op or
  render instantly when it's set, like the existing ones.
- No `localStorage`/`sessionStorage` and no external runtime requests — the deck
  must run fully offline from the single file.
- Keep it dependency-free at run time. Pillow is build-time only.
