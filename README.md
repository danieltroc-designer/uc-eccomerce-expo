# Uploadcare — Ecommerce Expo booth

This workspace is the isolated **Ecommerce Expo** cut, based on the latest
Uploadcare Webflow booth deck. The working presentation is the seven-card loop:

```bash
python build_simple.py
# open dist/uploadcare-simple.html
```

Event copy, confirmed details, missing assets, and open questions live in
`EVENT.md`. The prior Webflow project remains in `../UC-slides/uploadcare-show`
and must not be edited from here.

## Original project architecture

A self-contained, auto-playing HTML slide deck for display on external TVs at
trade fairs. Dark keynote aesthetic (`#090909`), Inter + Commit Mono, animated
numbers, a self-drawing chart, six logo animations, and a "file board" hero that
recreates the Uploadcare marketing screen with floating photo cards and terminal
readouts that type themselves in.

The thing you actually put on the TV is a **single HTML file** —
`dist/uploadcare-show.html` — with every asset (fonts, logo, globe, photos)
inlined. No build step, no server, no network needed at run time. Open it in a
browser, press **F** for fullscreen, done.

## Quick start

```bash
# 1. install the one build dependency
pip install -r requirements.txt

# 2. build the single-file deck
python build.py            # -> dist/uploadcare-show.html

# 3. preview (any static server works; this avoids file:// quirks)
python -m http.server 8080
#    then open http://localhost:8080/dist/uploadcare-show.html

# during development, auto-rebuild on save:
python build.py --watch
```

## Playback / kiosk controls

| Key            | Action                              |
| -------------- | ----------------------------------- |
| `F`            | Fullscreen                          |
| `Space`        | Pause / resume                      |
| `←` / `→`      | Previous / next slide               |
| `E`            | Open / close the slide editor       |
| `Esc`          | Close editor / dialogs              |

The cursor and on-screen chrome auto-hide after a few seconds of no input, so it
looks clean on a fair floor. A hairline progress bar sits at the bottom.

## Why the two-layer structure

Editing a 360 KB file full of base64 blobs is miserable. So the **source** is
kept small and readable, and a build step inlines the heavy assets:

```
src/index.template.html   ← edit this (HTML/CSS/JS, ~55 KB, has __TOKENS__)
assets/                    ← edit these (photos, logo, globe, fonts)
        │
        │  python build.py   (Pillow resizes/compresses photos, base64s fonts,
        ▼                     minifies SVGs, replaces the __TOKENS__)
dist/uploadcare-show.html  ← generated; this is what ships to the TV
```

Never hand-edit `dist/` — it's output. Edit `src/` + `assets/`, then rebuild.

## Repo layout

```
uploadcare-show/
├── README.md                  you are here
├── AGENTS.md                  orientation for AI coding agents (Cursor etc.)
├── build.py                   inlines assets -> dist/uploadcare-show.html
├── requirements.txt           Pillow (only build-time dependency)
├── .gitignore
├── src/
│   └── index.template.html    the editable deck: all HTML/CSS/JS logic
├── assets/
│   ├── photos/                tennis.png, portrait.png, sneaker.png, docx.png
│   ├── brand/                 uploadcare-logo-lockup.svg, globe.svg
│   └── fonts/                 commit-mono-400.woff2, commit-mono-500.woff2
└── dist/
    └── uploadcare-show.html   BUILD OUTPUT — the file you put on the TV
```

## Slide types

The deck is data-driven: a `deck` object (settings + an array of `slides`) is
rendered by a small set of type renderers. Each slide type has matching controls
in the in-app editor.

| Type       | What it is                                                            |
| ---------- | -------------------------------------------------------------------- |
| `logo`     | Split logo + tagline with a shimmering pixel-mosaic field            |
| `board`    | The "file board" hero: globe backdrop, 4 floating photo cards, typed terminal readouts |
| `statement`| Two-line statement, optional mono second line                        |
| `number`   | Big count-up number with prefix/suffix + label                       |
| `chart`    | Self-drawing line chart with start/end markers                       |
| `stats`    | Three big figures with brand-yellow rules                            |
| `logoAnim` | Logo-only animation, six choreographies (see below)                  |

**Logo animations (`logoAnim.variant`):** `assemble`, `rise`, `sweep` (whole
lockup) and `mark-ring`, `mark-scatter`, `mark-breathe` (yellow mark only).

## Saving & sharing decks

Open the editor (**E**) → **Export / Import**. You get the whole deck as JSON:
download it to save, or paste one back and **Apply**. Handy for keeping a
different deck per event. Decks are pure data — no rebuild needed to change copy,
ordering, durations, or slide content; rebuild is only for swapping the embedded
**assets** (photos/logo/globe/fonts).

## Editing the embedded content

- **Swap a photo:** drop a new file over `assets/photos/<name>.png` (keep the
  name) and `python build.py`. Tune target size/quality in `PHOTO_SPEC` /
  `JPEG_QUALITY` in `build.py`.
- **New logo or globe:** replace the SVG in `assets/brand/` and rebuild.
- **Background color / fonts / layout:** edit `src/index.template.html`.

See `AGENTS.md` for a map of where things live inside the template.
