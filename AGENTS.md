# AGENTS.md — Ecommerce Expo booth

This is the **Ecommerce Expo** cut. It was cloned from the latest Webflow booth
deck, but is now isolated on local branch `ecommerce-expo` with no remote.
Never edit or push to `../UC-slides/uploadcare-show` from this workspace.

Read `EVENT.md` before changing event copy or assets. Confirmed facts go there;
never infer booth details, giveaway copy, QR destinations, or customer claims.

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

### Ecommerce Expo booth loop

The simplified seven-card deck is the Ecommerce Expo working cut. It has its
own source + build + output and is fully independent of the main deck:

- Source: `src/simple.template.html` (a superset copy of the main template with
  extra card types: `dropin`, `features`, `quote2`, `logos`, `scale`,
  `pipeline`). Card 7 is a `board` slide with `layout:'outro'`.
- Build: `python build_simple.py` → `dist/uploadcare-simple.html`.
- Same rule applies: never hand-edit `dist/uploadcare-simple.html`.
- Current default sequence is 5/6/6/6/5/6/10 seconds (44 seconds total):
  product flow, benefits, Zephyr proof point, AI Editor, customer logos,
  infrastructure, booth CTA.
- Optional event imagery is auto-inlined from `assets/ecommerce/`; see its
  README for exact filenames. Card 4 renders an explicit asset-needed state
  unless *both* editor frames exist, so there is no way to half-ship it.

Ecommerce card 4 is the AI Image Editor swap, laid out to frame 213:1313: a
641x473 plate at (640,485) whose 1px rule and 8px pad are border-box, leaving
the well at exactly 623x455 — the pixel size of the exports, so neither frame
is ever resampled. The current pair is explicitly a layout/motion placeholder;
replace it with a confirmed editor example before the event. Two things about
the implementation are load bearing:

- **It is a wipe, not a crossfade, and that is a claim about the assets.** The
  after frame is clipped to the sweep's trailing edge, so the new background
  arrives *behind* the light rather than dissolving in everywhere at once. That
  only reads as "the background changed" because the two exports register on
  the product: `tools/check_editor.py` cross-correlates the silhouettes and
  fails unless the best offset is (0,0). Re-export the pair together or the
  swap becomes a jump cut. The band and the clip share a duration, delay and
  easing so the light lands just before the change it causes; retime one and
  the other has to follow.
- **Measure geometry after `.reveal` settles.** The plate wears `reveal d2`,
  which animates `transform`, so a panel sampled mid-entrance reads ~16px low
  and the frame's y looks wrong when only the animation is unfinished.
- `encode_logos()` scans `assets/logos/*.svg`; new customer marks require no
  build-script registration. Card 3 (the Zephyr proof point) is laid out to
  Figma frame 204:1081: the shared `.shd` headline sits at `--shd-y:380px` and
  the mark is pinned at 863,620 in its 193×157 export box. Card 5's wall comes
  from frame 207:1131 and is two rows of three, **not a grid** — `ECOM_WALL`
  pins each mark to its own slot at its own export size, because the frame
  places them optically (row 2's vertical centres differ by 15px) and six
  wordmarks of unequal weight at one shared width read as ragged. Order in the
  slide's `logos` field fills those slots in reading order.
- Ecommerce Card 2 comes from frame 212:1213: a fixed 1389×361 row at
  (266,359.5), made from five 265px panels and 16px gutters. Each panel is
  `justify-between`, which pins its 96px icon well to (41,224) while keeping
  the two-line copy at (41,41). Its five 48px icons are the frame's real SVG
  exports under `assets/ecommerce/benefit-*.svg`; their accent colours are
  baked into the art, and `encode_ecommerce()` deliberately fails if one is
  missing rather than silently substituting an approximation.
- Ecommerce Card 6 comes from frame 218:1470. Its 989px rail is pinned at
  (466,701) and uses Figma's real 8.14062px endpoint and 308.719px line SVGs.
  The 120x150 file opens at (602,529), moves to the exact optical centres of
  Optimize and Deliver, and counts 680KB down to 118KB while staying exactly
  120x150. The delivery crop starts only after travel stops; combining the two
  made the reframing disappear inside the larger motion. It turns the export's
  141.67x188.90 image at (-10.84,0.1) into a centred 120x160 cover crop using
  `translate(10.84px,-5px) scale(.847)`. After that the file fades without
  shrinking, the rail contracts to frame 219:1578's centred 475px yellow state
  using its exact 66.281px connector exports, and hands over to frame
  219:1612's 339x61 lockup at (791,693). `tools/check_infrastructure.py`
  asserts every beat and the rail geometry. Target distances are calculated
  from `offsetLeft`/`offsetWidth`, never screen-space rects, so the file still
  lands correctly when the 1920px stage is scaled on a laptop.
- `build_simple.py` reuses every encoder from `build.py` and adds six tokens
  of its own: `__QR_SVG__` (the booth QR, vectorised out of
  `assets/qr/booth-qr.png` — see card 7 below), `__LOGOS_JSON__` (the marks
  in `assets/logos/`), `__UPLOADERUI_JSON__` (the uploader widget's icons
  and the two file thumbnails in `assets/uploader/`, exported at 240x300 so one
  file serves both the 120x150 drag card and the 32px row thumb),
  `__DEMO_JSON__` (the pipeline card's photo and its three transformed frames,
  in `assets/demo/`), `__CAPS_JSON__` (card 2's capability icons in
  `assets/caps/`, which carry their own accent colours and so can't be
  recoloured from CSS), `__MARKET_JSON__` (card 5's marketplace chrome in
  `assets/marketplace/` — just the download glyph; its app tile reuses the
  deck's own Uploadcare glyph, recoloured to brand yellow from CSS), and
  `__COMPLIANCE_JSON__` (card 6's three trust marks in `assets/compliance/`,
  inlined as markup so they inherit the card's opacity).

Card 6 is a port of the three-panel demo on the marketing site
(upload | analyse | deliver), laid out to storyboard frame 184:5610. One thing
about it differs from the original and should stay that way: it **plays once
and has no Replay button** — a booth screen has nobody to press it, and the
deck re-runs the card each loop anyway. Its frames in `assets/demo/` are the
CDN's own renders of the three transforms the on-screen URL builds
(`crop/face` → `scale_crop` → `border_radius`), so changing a transform in
`PD_TRANSFORMS` means re-fetching the matching frame.

The panel is the storyboard's size to the pixel — 1252x554 at (334, 384), an
11px gutter around a `1fr .8fr 1fr` grid of 532px-tall cells — which is also
the marketing site's own scale. That box is what sets the type, not taste:
the delivery URL is 37 monospace characters plus a 20px indent against the
421px column's 358px of usable width, so **15px is the ceiling for `.pd-url`**
and the rest of the mono is set to match it. The storyboard asks for 13px;
15px is as much legibility as the geometry will give back, and it is still
small enough that the readouts are texture rather than copy at booth distance
— the 88px headline is what carries the card. An earlier revision ran this
type at 20px in a 1500px panel and had to abbreviate the UUID to fit; if the
panel ever grows again, `PD_UUID` can go back to being written in full only
because it fits, so re-measure rather than assume. `tools/check_pipeline.py`
asserts every box against the frame and prints the URL row's width next to the
room it has, which is the check that matters when any of this is touched.

**The URL is paged, not one block.** Width was never the only constraint: the
whole tag is seven rows (bracket, host, UUID, three transforms, closing
bracket), and after the 297px picture and its margins the column has room for
about six, so the tail was being cut off by `.pd-cell`'s `overflow:hidden`.
`.pd-u1` shows the plain address and `.pd-u2` builds the transforms in the space
it leaves. Both pages are absolutely positioned inside a fixed four-row (78px)
`.pd-body`, so the swap is a crossfade with no reflow and the picture above never
shifts — which also means `.pd-url` needs an explicit width, because `.pd-cell`
centres its children and a box with only absolute content collapses to nothing.
Paging is the better read regardless of the clipping: the address and the
operations stop competing for the same glance. Three things about it are load
bearing and were each a bug first:

- **The opening `<img src="` lives outside both pages and never leaves.** With
  the address gone, `-/crop/face/...` on its own does not read as part of a URL,
  and the closing bracket that would say so does not arrive until the last op is
  in — some 3.5s later. The open bracket also gives the swap an anchor, so the
  block changes underneath a fixed line instead of turning over wholesale.
- **The pages overlap; they do not take turns.** Clearing the address first and
  then bringing the transforms in left ~300ms where the column held nothing but
  the photo, and an empty box under a picture reads as a failed render, not as a
  beat. The address now leaves *across* the first op's arrival, lifting and
  blurring as it goes so the op growing into the same line never competes with
  legible text.
- **`.pd-url`'s top margin pays for the bracket's row.** The cell centres its
  column, so the extra 19.5px would lift the picture ~10px off the storyboard's
  y. The margin is the frame's 32px minus that row; total column height, and so
  the picture, is unchanged. `check_pipeline.py` asserts this — if the URL block
  ever grows another row (a fourth transform, say) the margin has to pay for it
  again, and the four-row `.pd-body` has to grow too.

The three compliance marks along the bottom come from the storyboard's own logo
sheet (node 189:493) and keep its relative sizing: `PD_BADGES` draws each at
.839 of its size there, which is why HIPAA is smaller than the other two — it
is a wider, shorter lockup and matching heights would make it shout. They are
laid out as a row centred on the stage rather than pinned at the frame's x/y.
The frame's own spacing was uneven because the marks reached it as slices of
one padded sprite; the real vectors are within 2px of each other in width, so
even gaps are what the eye wants, and centring on 960 puts the row under the
headline and the panel instead of 13px right of them. They settle at
`opacity:.5`, which is the frame's, not a fade that hasn't finished.

Figma exports these wrapped in whatever artboard they were sitting on — a
`#1E1E1E` backdrop and a page-sized path running thousands of units outside the
viewBox. Only the named `<g>` is the mark, so anything re-exported here has to
be unwrapped before it is committed.

Ecommerce Card 1 follows Figma frame 229:443, with its uploader completion
state from 229:544. The three beats share one final composition rather than
replacing each other: the compact uploader is already visible and finishes its
ring, the 220x275 optimized file lands at the frame's confirmed 120KB value,
then the 514x401 browser opens with the product already present. The score
resolves in ~1.9s and
holds for the rest of the 5s card. `setupCommerceFlow()` resets all three beats
synchronously and writes the completed file/browser state inline before the
outgoing crossfade, because killing a WAAPI animation otherwise restores the
hidden opening styles. The reduced-motion state is the completed composition.
The browser's transparent flower and exact chrome vectors are required offline
assets under `assets/ecommerce/card1-*`; do not replace them with the full-frame
Figma screenshot.

The inherited `dropin` card type is a separate, reusable uploader demo: a stack
of two files is dragged in under a single cursor, dropped, and the widget hands
over to the compact "Uploading N files" panel, where each file fills its ring
and settles into a checkmark plus a bin. The travel is a spring rather than a
tween, because a dragged object carries momentum; `tl.spring()` reports its
settle time synchronously through `onArrive`, and the rest of the score is
written against that, so the drop always follows the landing however the spring
is retuned. The progress ring is drawn in the template (`DI_RING`) rather than
exported, because the storyboard's icon is a snapshot at one arbitrary
percentage and this one has to fill.

Three things about how it ends and how the zone lights:

- **The window no longer dismisses itself.** The storyboard's third frame has
  it disappear, but that made the payoff — both files ticked — the one frame
  you never got to look at, and it left the card empty from 6.9s to its 8s
  slot. Both files are done at ~5.8s; the card now holds that frame and cuts at
  7.5s.
- **The finished panel is pinned to inline style as well as to the tween's
  fill.** Leaving a card kills its timeline, and a cancelled WAAPI animation
  reverts to inline style — which `reset()` left at `opacity:0`. Because the
  kill happens at the *top* of the crossfade, the panel blinked out while the
  card was still 70% visible. Any card whose closing frame must survive its own
  exit needs the same treatment; the fill alone is not enough.
- **The drop zone lights on the frame the pointer tip enters it.** It used to
  get its `hot` class 350ms before the stack landed and ramp in over a matching
  350ms transition, which read as lag. The fill is now instant (`transition:
  none` on `.hot`, with the base rule's transition still running on the way
  out, where a hard cut would pop under the panel swap), and `springCrossing()`
  re-integrates the spring to find when the tip actually crosses into the zone
  rather than guessing an offset back from the settle time. Positions there are
  `offsetLeft`/`offsetTop`, not `getBoundingClientRect()` — see the note below
  on why that matters when the stage is scaled.

Card 2 is the storyboard's capability row: five 265x316 panels that rise in a
60ms stagger, then the icons land in their (already present) wells one after
another, left to right, on a 190ms gap. The gap is the point of the card and is
deliberately much wider than the panels' — across a booth anything near 70ms
reads as all five arriving at once. Each pop runs longer than the gap, so the
row fills as one travelling wave rather than five separate ticks. An earlier
version put a spinner chip above the row to signal that something was
happening; the sequence now carries that itself, so there is nothing above the
row and it sits centred in the stage.

Once the icons land the row used to just sit there, which was the one card in
the deck that read as a static slide rather than a paused one. A pulse now
loops across it left to right: each panel washes to 10% of **its own icon's**
accent and back, 300ms apart. That gap was 180ms first and read as a single
wash sliding across the row rather than five panels taking turns; each pulse
still runs far longer than the gap (1.5s against 300ms) so neighbours overlap
and the row never breaks into five separate blinks. Per-card colour
rather than a house colour is what makes it read as five capabilities lighting
up in turn instead of one effect painted over the row, so `FEATURES[].ac`
duplicates the accent baked into each SVG and the two have to be kept in step —
CSS cannot read a colour out of inlined markup. The wash rides a `::before`
overlay's opacity rather than the card's `background-color`: opacity composites
where colour repaints, and this runs forever on a panel nobody touches. The
overlay pairs a full-strength inset ring with a 40%-alpha fill so the peak sits
at a 25% edge over a 10% wash — at booth distance the ring is what actually
carries the pulse across the room; the fill alone is too quiet. It is scoped to
`.slide.active` and delayed past the entrance so it starts on top of a built
row, and pinned off under reduced motion.

Card 3 is the customer quote as a two-panel spread: the lime pull-quote at
229,307 (938x465) beside the customer panel at 1183,307 (507x465). Both are
`justify-between`, which is what lands the attribution and the company blurb on
a shared bottom edge even though the columns hold different content. The quote
panel enters first and the customer panel ~220ms later, so the pair reads as a
claim and then its source. Two details on this card are load-bearing:

- **Panels fade fast and move slow.** They sit inside the slide's own 520ms
  crossfade, so a long fade here compounds into a second one. On the lime block
  that is visible as a *colour* rather than a dimming — part-opaque `#d8ff6e`
  over near-black is olive, which is nowhere in the palette. Opacity runs on
  `--dur-1` and the rise on `--dur-3`.
- **`.qt-quote` carries a 0.96px right margin as tracking compensation.** CSS
  adds letter-spacing after the last glyph on a line; Figma only puts it between
  glyphs. At -0.96px that makes every candidate line measure 0.96px narrower
  here than in the design — enough to pull one more word onto line 2 and change
  the rag. Handing that width back to the measuring box makes lines break where
  the design breaks them. Watch for this on any other tracked, wrapping type.

Card 4 is the trusted-by wall, and the marks are **not** on a grid. The
storyboard places all eight optically — column centres drift by up to 13px
between the two rows, vertical centres by up to 16px — because these logos carry
very different visual weight at a common width. So each mark is centred on its
own slot (`LW_SLOTS`, reading order) at its own exported size (`LOGO_BOX`, the
asset viewBoxes). A `repeat(4,1fr)` grid gets within ~13px, which is visible at
booth scale. The eight land 75ms apart in reading order; they used to arrive
together on one 1.1s fade, which reads as the slide brightening rather than as
logos appearing. Note the assets in `assets/logos/` are exported from this frame
and carry its bounding boxes, padding included — re-export from the same frame
or the boxes stop matching `LOGO_BOX`.

The ambient particles are the storyboard's: 5px squares in white, `#b6b7ff` and
the quote card's `#d8ff6e` (`SB_COLORS`). They stay in the margin zones rather
than the middle of the stage where the design draws them, because the substrate
runs behind all of cards 1–6 and the middle is where those cards put their
content. They no longer run amber-to-green — that was the file board's
in-flight/landed vocabulary, and out here it signalled a state nothing on screen
has.

Card 5 is the Webflow marketplace listing, installed by the pointer. The listing
is rebuilt rather than dropped in as the storyboard's bitmap, because the button
has to change state; the geometry is Figma's to the pixel and
`tools/check_install.py` asserts it, so a stray padding shows up as a number
rather than as a screenshot someone has to eyeball. Three things here:

- **Entrance and press live on different elements.** `.wf-btnwrap` owns the
  translate that brings the button in, `.wf-btn` owns the scale it takes on
  press. One element can't do both without the two fighting over `transform`.
- **The label swap is asymmetric on purpose.** The old label leaves in 130ms and
  the new one doesn't begin until 120ms in. Crossfade them evenly — even with
  blur — and there is a long stretch where you read "Installing" printed over
  "Install App"; the frame-by-frame strip makes it obvious. The 4px blur covers
  what overlap is left. Same pattern applies to any morphing-label button.
- **The pointer goes in as a data URI, not inline SVG.** Card 1 already inlines
  the same mark, and `Cursor.svg` carries a mask referenced by id. Two inline
  copies in one document collide on that id and the second renders as *nothing* —
  present, positioned, opacity 1, invisible. `UPLOADER.cursor` sidesteps it.

Timing is sized like a real button rather than like a marketing loop: press
140ms, release quicker, and only the install itself slow (1.15s, `WF_INSTALL_MS`,
which must stay in step with the sweep's CSS duration). The score runs ~4.2s.

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
  `assets/brand/globe.svg` used to declare `height="712"` against artwork that
  runs to 995, so the bottom third was cropped inside its own viewBox and no
  amount of CSS could recover it. The header now matches the artwork, and
  `.hb-globe` sets both axes explicitly rather than trusting `height:auto`.
- **The rebuilt headline block is `.shd`** — an 88px title over a 32px sub, both
  Inter 580, trimmed to their cap box with `text-box-trim` so they land on the
  storyboard's cap-tops exactly rather than by eye. Cards 1, 5 and 6 use it; the
  rest still sit on `--head-y` and adopt `.shd` as they get rebuilt. Its anchor
  is `--shd-y` (default 168px) and cards override it — the storyboard moves the
  block down as the headline gains lines, so the whole thing stays balanced
  instead of the anchor staying put and the type growing off it. Card 5 sets
  212px for its two-liner. Because Figma trims to the cap box, any element
  measured against it needs the same trim, or it will read ~21px low at 88px.
- **`.reveal` animates `transform`.** Anything wearing it must be centred with
  an explicit `left` offset, never `translateX(-50%)`, or the two rules fight
  and the element slides sideways as it enters.
- **Card 7's headline is not on the shared type scale.** `.hb-outro-line` was in
  the `.hd, .cd-line, …` list and silently inherited `--h-size: 72px` over its
  own 80px, which is easy to miss because it only shows up as a 14px error in
  the block's height. The storyboard sets the last card in 80px bold on two
  hand-broken lines, so it now stands on its own rule; keep it out of that list.

### Card 7, the outro

Ecommerce frame 219:1638 deliberately reuses the Webflow storyboard frame
184:5666 composition and its existing renderer. Four things about it are
deliberate:

- **The centre line is pinned, not stacked.** Lockup, headline, glyph and
  sign-off each sit at their own `top` from the frame, because the glyph lands
  between the headline and the sign-off and a flow layout would have the three
  of them shoving each other whenever the copy changes.
- **The corner files are backdrop.** Their telemetry runs at 9px, far below
  anything readable across a stand, and that is the intent — they are texture
  that says "files are moving" while the centre line does the talking. Sizes and
  positions are the frame's; `.hb-outro-mode` carries the whole small-scale
  treatment so the non-outro board layout keeps its original 18px.
- **The glyph sparkles per pixel.** `setupBoard()` gives each of the mark's 47
  squares its own period, phase and opacity floor/ceiling, so it shimmers
  without ever reading as a pulse. This is not an invention: the frame's own
  render is a still of exactly this, a field of squares sitting at different
  greys between roughly 20% and 100% of `#454545`. The mark keeps its `#090909`
  pad, which knocks the wireframe's crossing lines out from behind it.
- **The sign-off is two lines and carries the booth QR.** `Come say hi 👋` runs
  on over the current Figma placeholder `and enter to win something!`, both at
  the frame's 1.065 leading. Neither the giveaway nor destination is confirmed
  Expo copy yet. The QR under it is pinned at `857,711`, not stacked, for the
  same reason the rest of the column is.
  - **The destination lives in the artwork, not in a constant.** `make_qr()`
    reads `assets/qr/booth-qr.png` — design's black-on-white export — recovers
    its module grid via `tools/qr_lib.py` and re-emits it as white vector
    rectangles. To point the booth somewhere else, replace that PNG; the build
    prints what it decodes to (currently `https://l.ead.me/bgyXox`). It is
    deliberately not wrapped in a try/except: every silent fallback here ships
    something that looks scannable and goes somewhere other than intended, so
    unreadable artwork fails the build.
  - **Why vectorise rather than inline the PNG.** The box is 204px and the
    export is 1024px; scaling a raster gives soft module edges, which is what a
    scanner works hardest to threshold. It is also the wrong polarity.
  - **The 204px box is mostly quiet zone.** The frame's node is 204 holding
    164.5 of ink, so `to_svg` pads the viewBox by 3 modules. Checking the box
    alone would pass at any ink size, so `check_outro.py` measures the drawn
    `getBBox()` too.
  - **It is a reverse-polarity code** — white modules on dark, per the frame.
    Phone cameras read inverted codes fine, and at 204px the modules are ~4mm
    on a 55-inch panel, far past what a scanner needs. If a scanner ever does
    baulk at a booth, the fix is a light plate behind it, not a bigger code.
- **The sign-off's hand actually waves.** `emojiHTML()` splits every
  emoji out of the sign-off into `.hb-wave > i` so the gesture can be
  animated without swinging the words with it. It matches anywhere in the
  string, not just at the end — the giveaway line put the hand mid-copy — and
  everything it wraps shares one animation, so two emoji in a sign-off would
  gesture in unison rather than take turns. Two nested elements because a
  wave is two motions on different clocks — the hand lifts (and scales a hair)
  over the whole burst while it pivots much faster. Three things do the work:
  the pivot is at the wrist, the arc damps, and it comes in bursts.
  - **The pivot is measured, not guessed.** `transform-origin:65% 88%` is a
    fraction of the *line box*, which the emoji does not fill. Eyeballing "the
    bottom of the hand" as ~100% drops the pivot into empty space below the
    glyph, and rotating about a point outside the artwork reads as the hand
    sliding rather than turning. 65/88 is where the ink tapers to a point — the
    forearm. If the emoji font ever changes, re-measure by differencing a frame
    against one with the `<i>` set to `visibility:hidden`; that isolates the
    glyph's ink from the warm pixels in the corner cards nearby.
  - **It winds up, holds its energy, then gives out.** A 6° counter-tip first,
    because a gesture loads before it fires; then 22 → 18 → 20 → 16 → 17 → 12 →
    10 → 4 → rest. The arc deliberately does *not* damp monotonically: holding
    the amplitude and dropping it at the end reads as someone happy to see you
    who stops because they are done, where a smooth decay reads as a wave
    running down. Half-swings land 160ms apart, a little over 3Hz, which is an
    excited wave rather than a polite one. `ease-in-out` between every stop is
    what makes the ends of the arc settle and the middle move quickly; that is
    pendulum motion, and `linear` or `ease-out` here reads mechanical.
  - **The arc is TV-sized.** ±22° looks large on a laptop and is about right at
    2–4m; at ±12 the hand covers a couple of millimetres of panel and the
    gesture is lost.
  - **It rests between bursts.** ~1.5s of waving inside a 4.4s cycle. A
    continuous wave reads as a looping GIF. The card runs 10s, so a visitor sees
    the burst, a pause, and a second one.
  - **Scoped to `.slide.active`.** Unscoped, a CSS animation starts when the deck
    renders, so the card inherits whatever phase it lands on — as likely to
    arrive mid-swing as at rest, and somewhere else again on the next loop. The
    1.5s delay puts the wave just after the sign-off's own entrance (`d5`,
    .46s + .58s) so the hand reads as noticing you rather than waving before it
    is there. Reduced motion pins it still. The same scoping rule applies to
    card 2's capability pulse and to any looping animation added later.
    A one-shot `forwards` animation needs it just as much, for the opposite
    reason: it holds its end frame after the card is left, so unscoped it plays
    on the first render and every later loop opens on the settled result. Card
    1's `efCrisp` did exactly that — the photo was already sharp before the
    optimize beat ran, so the card only told its story once per page load.
    `tools/check_commerce_flow.py` checks a *second* visit; one pass passes
    either way.
- **The corner watermark is suppressed here.** `enter()` skips it on
  `layout:'outro'` — the mark is already the centre of the composition, and the
  frame has no second copy.

`tools/check_outro.py` asserts the geometry, that the globe is neither clipped
by the stage nor by its own viewBox, and that the glyph's pixels are spread
across opacities rather than moving as one. Run it with the drift off; the
corner files wander ±13px and half a degree, which is enough to fail a
pixel comparison for no reason.

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
- **A tween scheduled for later must not fill backwards.** `tl.to()` defaults to
  `fill:'both'`, so a tween opening on `{opacity:1}` paints that keyframe from
  t=0 and the element is on screen before it ever arrived. The same trap catches
  `transform`, and there it is much quieter: card 5's press dip opens on the
  pointer's *landed* position, so with `fill:'both'` it silently pinned the
  pointer to the button from t=0 and the spring that was supposed to carry it
  there never had any visible effect — the pointer simply faded up on target and
  every trace of the travel was gone. Pass `fill:'forwards'` whenever the first
  keyframe is a state the element is only supposed to reach later.
  `tools/trace_cursor.py` prints position and opacity per frame, which is how
  that one was caught; screenshots alone read as "the animation is just fast".

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

### Never feed `getBoundingClientRect()` back in as a length

`#stage` is CSS-scaled to fit the viewport (`fit()` sets `scale(min(w/1920,
h/1080))`), so **every** rect measured inside it is in screen pixels, not layout
pixels. Assigning one back as a width, height or offset makes the result wrong
by exactly the scale factor. This is a nasty one because at a 1920x1080 viewport
the scale is 1 and the two agree — so it passes every check here, every
screenshot, and the booth TV, and only breaks on a smaller display. It shipped
once: the pipeline card's transform rows animated to
`row.getBoundingClientRect().height`, which on a 1440-wide laptop set a 19.5px
line into a 14.6px clip box and sheared the descenders off all three lines.

Use a layout source instead — `offsetHeight`/`offsetWidth`, or better a computed
value like `parseFloat(getComputedStyle(el).lineHeight)`. If you genuinely need
to convert a rect, divide by
`stage.getBoundingClientRect().width / stage.offsetWidth`. Rects are still fine
for comparing two things measured in the same space (hit-testing, relative
offsets); it is only the round-trip into a style that breaks. When you touch
sizing code, verify at 1280x800 as well as 1:1.

### A CSS/JS comment trap worth knowing

Both of this file's long explanatory comments and the template's have bitten the
same way twice: appending a paragraph to an existing `/* … */` block **after**
its closing `*/` leaves the new prose loose in the stylesheet or the script. In
JS it is an instant `SyntaxError` and the whole deck fails to boot (`deck is not
defined`); in CSS it silently swallows the next rule's declarations, which is far
worse because the page still renders and only a geometry check catches it. When
extending a comment, put the text *before* the terminator.

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
