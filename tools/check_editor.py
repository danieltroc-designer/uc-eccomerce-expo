#!/usr/bin/env python3
"""Card 4: verify backend -> Edit with AI -> genuine catalog result.

The slide records the production ai-catalog-admin interaction offline. This
check protects the sequence, supplied backend frames, exact preset prompt,
source/result provenance, replay reset and reduced-motion payoff.
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
      const stage = q('.ce-stage');
      return {
        stage: stage ? [stage.offsetLeft, stage.offsetTop,
                        stage.offsetWidth, stage.offsetHeight] : null,
        backend: opacity(q('.ce-backend')),
        overview: opacity(q('.ce-admin-overview')),
        focus: opacity(q('.ce-admin-focus')),
        cursor: opacity(q('.ce-admin-cursor')),
        ring: opacity(q('.ce-click-ring')),
        editor: opacity(q('.ce-editor')),
        prompt: q('.ce-prompt span')?.textContent || '',
        after: opacity(q('.ce-after')),
        veil: opacity(q('.ce-veil')),
        shimmer: opacity(q('.ce-shimmer')),
        done: q('.ce-done') ? getComputedStyle(q('.ce-done')).backgroundColor : '',
        overviewNatural: natural(q('.ce-admin-overview')),
        focusNatural: natural(q('.ce-admin-focus')),
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
                  early["backend"] > .98 and early["overview"] > .98
                  and early["editor"] < .02,
                  f"backend {early['backend']:.2f}, editor {early['editor']:.2f}")
            check("prompt resets empty", early["prompt"] == "", repr(early["prompt"]))
            check("supplied backend frames are native",
                  early["overviewNatural"] == [1024, 899]
                  and early["focusNatural"] == [1024, 791],
                  f"{early['overviewNatural']}, {early['focusNatural']}")
            check("catalog source is the production original",
                  early["sourceNatural"] == [1536, 2048],
                  str(early["sourceNatural"]))

            samples = []
            for _ in range(36):
                pg.wait_for_timeout(250)
                samples.append(read(pg))

            focused = next((s for s in samples
                            if s["backend"] > .98 and s["focus"] > .95
                            and s["overview"] < .05), None)
            check("Media card focus replaces overview",
                  focused is not None, "observed" if focused else "not observed")
            pointer = next((s for s in samples
                            if s["focus"] > .95 and s["cursor"] > .8), None)
            check("pointer commits to Edit with AI",
                  pointer is not None, "observed" if pointer else "not observed")

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
