#!/usr/bin/env python3
"""Card 4: verify upload -> prompt -> shimmer -> genuine AI result.

The card is a recording of a real AI Enhancer interaction, rebuilt offline.
This check protects the parts that make that claim honest:

* the uploader, editor source and Card 1 all use one identical inlined photo;
* the committed result is the real generated 2:3 asset, not CSS treatment;
* phase timing exposes upload progress, prompt typing and the dot-grid pending
  state before settling on the generated result;
* a second visit resets synchronously, and reduced motion opens on the payoff.
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
PROMPT = ("Replace only the background with a sleek, light modern studio "
          "backdrop. Keep the product, crop, and shadow unchanged.")
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
      const stage = q('.ce-stage');
      const editor = q('.ce-editor');
      const arc = q('.ef-uaction .di-ring .arc');
      const sourceImages = [q('.ce-drag img'), q('.ef-uthumb img'), q('.ce-before')];
      const after = q('.ce-after');
      return {
        stage: stage ? [stage.offsetLeft, stage.offsetTop,
                        stage.offsetWidth, stage.offsetHeight] : null,
        uploader: opacity(q('.ce-upload-phase')),
        editor: opacity(editor),
        widget: opacity(q('.ef-widget')),
        panel: opacity(q('.ef-panel')),
        dash: arc ? parseFloat(getComputedStyle(arc).strokeDashoffset) : null,
        prompt: q('.ce-prompt span')?.textContent || '',
        after: opacity(after),
        veil: opacity(q('.ce-veil')),
        shimmer: opacity(q('.ce-shimmer')),
        done: q('.ce-done') ? getComputedStyle(q('.ce-done')).backgroundColor : '',
        sourcesReady: sourceImages.every(i => i && i.src),
        sourceCount: new Set(sourceImages.map(i => i && i.src)).size,
        afterNatural: after ? [after.naturalWidth, after.naturalHeight] : null,
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
            headless=True,
            args=["--no-sandbox", "--disable-gpu"],
        )
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
            pg.wait_for_timeout(300)
            early = read(pg)
            check("editor stage matches composition",
                  early["stage"] == [334, 400, 1252, 640], str(early["stage"]))
            check("uploader opens before editor",
                  early["uploader"] > .98 and early["editor"] < .02,
                  f"uploader {early['uploader']:.2f}, editor {early['editor']:.2f}")
            check("one source photo feeds drag, row, and editor",
                  early["sourcesReady"] and early["sourceCount"] == 1,
                  f"{early['sourceCount']} source(s)")
            check("upload ring resets empty", early["dash"] > 57,
                  f"dash {early['dash']:.1f}")
            check("prompt resets empty", early["prompt"] == "", repr(early["prompt"]))

            # Sample the score rather than betting on one wall-clock instant:
            # headless scheduling can move a short state by a frame or two.
            # What matters is that every phase is observable in order.
            samples = []
            for _ in range(36):
                pg.wait_for_timeout(250)
                samples.append(read(pg))

            uploading = next((s for s in samples
                              if s["panel"] > .98 and 5 < s["dash"] < 55), None)
            check("compact upload visibly progresses",
                  uploading is not None,
                  (f"dash {uploading['dash']:.1f}" if uploading
                   else "no in-progress ring sample"))

            typing = next((s for s in samples
                           if 10 < len(s["prompt"]) < len(PROMPT)
                           and PROMPT.startswith(s["prompt"])), None)
            editor_state = next((s for s in samples
                                 if s["editor"] > .98 and s["uploader"] < .02), None)
            check("editor replaces uploader",
                  editor_state is not None,
                  "observed" if editor_state else "not observed")
            check("production prompt types in place",
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
            check("exact production prompt is shown",
                  final["prompt"] == PROMPT, f"{len(final['prompt'])} chars")
            check("genuine result keeps source aspect",
                  final["afterNatural"] == [832, 1248],
                  str(final["afterNatural"]))
            check("Done resolves active",
                  final["done"] == "rgb(47, 90, 232)", final["done"])

        check("no page errors", not errors, "; ".join(errors[:3]))
        browser.close()

        # Reduced motion skips demonstration movement but must retain its payoff.
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
              state["editor"] > .98 and state["uploader"] < .02
              and state["after"] > .98 and state["prompt"] == PROMPT,
              f"editor {state['editor']}, after {state['after']}")
        red.close()

    print()
    if fails:
        print(f"{len(fails)} check(s) failed")
        return 1
    print("card 4 replays the genuine AI Enhancer flow cleanly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
