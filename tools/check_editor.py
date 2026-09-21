#!/usr/bin/env python3
"""Card 4: verify backend -> Edit with AI -> genuine catalog result.

The slide records the production ai-catalog-admin interaction offline. This
check protects the sequence, the exact preset prompt, source/result
provenance, replay reset and reduced-motion payoff.

Two properties here are easy to lose in a refactor and are asserted directly:
the backend is live DOM rather than a screenshot of one, and the card never
zooms — the page it works in holds still while only the pointer moves.
"""

import pathlib
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
DECK = ROOT / "dist" / "uploadcare-simple.html"
CHROME = next(
    (p for root in (pathlib.Path.home() / ".cache/ms-playwright-stable",
                    pathlib.Path.home() / "Library/Caches/ms-playwright")
     for p in sorted(root.glob("chromium-*/chrome-mac-arm64/*.app/Contents/MacOS/*"),
                     reverse=True)
     if p.is_file()), None)

CARD = 3
PROMPT = ("Replace the background with a flat sage green studio backdrop, "
          "keep the bottle and its natural shadow")
fails = []


def check(label, ok, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}{'  ' + detail if detail else ''}")
    if not ok:
        fails.append(label)


def read(pg):
    return pg.evaluate("""() => {
      const root = document.querySelector('.slide.active .ce-wrap');
      const q = s => root && root.querySelector(s);
      const opacity = e => e ? parseFloat(getComputedStyle(e).opacity) : null;
      const natural = e => e ? [e.naturalWidth, e.naturalHeight] : null;
      const rect = e => { if (!e) return null; const r = e.getBoundingClientRect();
                          return [r.left, r.top, r.width, r.height]; };
      const stage = q('.ce-stage');
      return {
        stage: stage ? [stage.offsetLeft, stage.offsetTop,
                        stage.offsetWidth, stage.offsetHeight] : null,
        backend: opacity(q('.ce-backend')),
        cursor: opacity(q('.ce-admin-cursor')),
        ring: opacity(q('.ce-click-ring')),
        hot: !!q('.ce-shot')?.classList.contains('hot'),
        edit: opacity(q('.ce-edit')),
        shot: rect(q('.ce-shot')),
        tip: rect(q('.ce-admin-cursor'))?.slice(0, 2) || null,
        // .ce-page, not .ce-backend: the pointer itself is an inlined SVG img
        backendImages: [...(q('.ce-page')?.querySelectorAll('img') || [])]
                         .map(i => [i.naturalWidth, i.naturalHeight]),
        crumb: q('.ce-crumb-now')?.textContent || '',
        action: q('.ce-edit')?.textContent.trim() || '',
        editor: opacity(q('.ce-editor')),
        prompt: q('.ce-prompt span')?.textContent || '',
        after: opacity(q('.ce-after')),
        veil: opacity(q('.ce-veil')),
        shimmer: opacity(q('.ce-shimmer')),
        done: q('.ce-done') ? getComputedStyle(q('.ce-done')).backgroundColor : '',
        sourceNatural: natural(q('.ce-before')),
        afterNatural: natural(q('.ce-after')),
      };
    }""")


def enter(pg):
    pg.evaluate("enter(0)")
    pg.wait_for_timeout(200)
    pg.evaluate(f"enter({CARD}); playing=false; clearTimeout(timer); clearInterval(tickTimer)")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=str(CHROME) if CHROME else None,
            headless=True, args=["--no-sandbox", "--disable-gpu"])
        pg = browser.new_page(
            viewport={"width": 1920, "height": 1080},
            reduced_motion="no-preference")
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(DECK.as_uri())
        pg.wait_for_timeout(800)

        for visit in (1, 2):
            print(f"visit {visit}")
            enter(pg)
            pg.wait_for_timeout(250)
            early = read(pg)
            check("editor stage matches composition",
                  early["stage"] == [334, 400, 1252, 640], str(early["stage"]))
            check("product backend opens before editor",
                  early["backend"] > .98 and early["editor"] < .02,
                  f"backend {early['backend']:.2f}, editor {early['editor']:.2f}")
            check("prompt resets empty", early["prompt"] == "", repr(early["prompt"]))
            # live DOM, not a capture: the only bitmaps in the backend are the
            # production source photo, in the Media slot and the preview card
            check("backend is rebuilt UI, not a screenshot",
                  early["backendImages"] == [[1536, 2048], [1536, 2048]]
                  and early["crumb"] == "Resurfacing Body Lotion"
                  and early["action"] == "Edit with AI",
                  f"{early['backendImages']}, {early['crumb']!r}")
            check("Edit with AI waits for the pointer",
                  not early["hot"] and early["edit"] < .02,
                  f"hot {early['hot']}, pill {early['edit']:.2f}")
            check("catalog source is the production original",
                  early["sourceNatural"] == [1536, 2048],
                  str(early["sourceNatural"]))

            # 125ms, not 250: the click ripple is only readable for ~230ms, and
            # a cadence longer than the shortest beat turns this into a coin toss
            samples = []
            for _ in range(72):
                pg.wait_for_timeout(125)
                samples.append(read(pg))

            # the pointer crosses the image, and the pill is a consequence of
            # that crossing rather than something that was always on the page
            inside = [s for s in samples
                      if s["cursor"] > .8 and s["tip"] and s["shot"]
                      and s["shot"][0] <= s["tip"][0] <= s["shot"][0] + s["shot"][2]
                      and s["shot"][1] <= s["tip"][1] <= s["shot"][1] + s["shot"][3]]
            check("pointer crosses the catalogue image",
                  bool(inside), f"{len(inside)} sample(s) with the tip in the slot")
            check("hover reveals Edit with AI under it",
                  any(s["hot"] and s["edit"] > .95 for s in inside),
                  "observed" if inside else "not observed")
            check("pointer commits to the action",
                  any(s["ring"] > .1 for s in samples), "click ring observed")

            # the user-visible contract of this card: the backend does not zoom
            held = [s["shot"] for s in samples if s["backend"] > .5 and s["shot"]]
            drift = max((max(abs(r[i] - held[0][i]) for i in range(4))
                         for r in held), default=0)
            check("the backend never zooms", drift < .6, f"{drift:.2f}px drift")

            editor_state = next((s for s in samples
                                 if s["editor"] > .98 and s["backend"] < .02), None)
            check("editor modal replaces backend",
                  editor_state is not None,
                  "observed" if editor_state else "not observed")
            typing = next((s for s in samples
                           if 10 < len(s["prompt"]) < len(PROMPT)
                           and PROMPT.startswith(s["prompt"])), None)
            check("exact preset prompt types in place",
                  typing is not None,
                  (f"{len(typing['prompt'])}/{len(PROMPT)} chars"
                   if typing else "no partial prompt sample"))
            pending = next((s for s in samples
                            if s["veil"] > .25 and s["shimmer"] > .1), None)
            check("dot-grid shimmer covers generation",
                  pending is not None,
                  (f"veil {pending['veil']:.2f}, shimmer {pending['shimmer']:.2f}"
                   if pending else "no pending-state sample"))

            final = samples[-1]
            check("generated result settles",
                  final["after"] > .98 and final["veil"] < .02
                  and final["shimmer"] < .02,
                  f"after {final['after']:.2f}, veil {final['veil']:.2f}")
            check("production prompt is shown",
                  final["prompt"] == PROMPT, f"{len(final['prompt'])} chars")
            check("genuine result asset is loaded",
                  final["afterNatural"] == [880, 1168],
                  str(final["afterNatural"]))
            check("Add to media resolves active",
                  final["done"] == "rgb(24, 24, 24)", final["done"])

        check("no page errors", not errors, "; ".join(errors[:3]))
        browser.close()

        red = p.chromium.launch(
            executable_path=str(CHROME) if CHROME else None,
            headless=True, args=["--no-sandbox", "--disable-gpu"])
        pg = red.new_page(viewport={"width": 1920, "height": 1080},
                          reduced_motion="reduce")
        pg.goto(DECK.as_uri())
        pg.wait_for_timeout(700)
        enter(pg)
        pg.wait_for_timeout(100)
        state = read(pg)
        check("reduced motion opens on final result",
              state["editor"] > .98 and state["backend"] < .02
              and state["after"] > .98 and state["prompt"] == PROMPT,
              f"editor {state['editor']}, after {state['after']}")
        red.close()

    print()
    if fails:
        print(f"{len(fails)} check(s) failed")
        return 1
    print("card 4 replays the catalog-admin AI flow cleanly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
