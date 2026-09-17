#!/usr/bin/env python3
"""Card 1's two loop-sensitive beats: the optimize sharpen and the upload meter.

Both are CSS animations with `forwards`, so both hold their end frame after the
card is left — and a card that keeps its end frame shows the payoff already
delivered when the deck comes back round. The sharpen was the one that did:
unscoped, it ran once on first render and every later loop opened on an
already-crisp photo. Checking a second visit is the whole point; a single pass
passes either way.
"""
import pathlib
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
DECK = ROOT / "dist" / "uploadcare-simple.html"
PROFILE = ROOT / "tools" / "_profile" / "cf"
# the bundled driver resolves an x64 path on this machine; use the arm64 build
CHROME = (pathlib.Path.home()
          / ".cache/ms-playwright-stable/chromium-1223/chrome-mac-arm64"
          / "Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing")
CARD = 0                                            # commerceFlow


def read(pg):
    return pg.evaluate("""() => {
      const img = document.querySelector('.slide.active .ef-opt .ef-photo img');
      const bar = document.querySelector('.slide.active .ef-meter i');
      const cs = bar && getComputedStyle(bar);
      return {
        blur: img ? getComputedStyle(img).filter : null,
        // scaleX lands in the matrix' first component
        fill: cs ? new DOMMatrix(cs.transform).a : null,
        width: cs ? parseFloat(cs.width) : null,
      };
    }""")


def main():
    fails = []

    def check(label, ok, detail):
        print(f"  {'ok  ' if ok else 'FAIL'}  {label}  {detail}")
        if not ok:
            fails.append(label)

    with sync_playwright() as p:
        b = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE),
            executable_path=str(CHROME) if CHROME.exists() else None,
            viewport={"width": 1440, "height": 900},
            reduced_motion="no-preference",
        )
        pg = b.new_page()
        pg.goto(DECK.as_uri())
        pg.wait_for_timeout(600)

        for visit in (1, 2):
            print(f"visit {visit}")
            # arrive from elsewhere, the way the loop does. Calling enter() on the
            # card that is already live never toggles `.active`, so the CSS
            # choreography carries on from wherever the page load left it.
            pg.evaluate("enter(3)")
            pg.wait_for_timeout(700)
            pg.evaluate(f"enter({CARD})")
            pg.wait_for_timeout(250)
            early = read(pg)
            check("photo opens soft", "blur(3px)" in (early["blur"] or ""),
                  early["blur"])
            check("meter opens empty", early["fill"] < .1, f"scaleX {early['fill']:.2f}")

            pg.wait_for_timeout(1900)
            late = read(pg)
            check("photo resolves crisp", "blur(0px)" in (late["blur"] or "")
                  or "blur" not in (late["blur"] or ""), late["blur"])
            check("meter fills", late["fill"] > .98, f"scaleX {late['fill']:.2f}")
            # scaleX only reads as a full bar if the element is already full width
            check("meter is laid out full width", late["width"] > 200,
                  f"{late['width']:.0f}px")

        b.close()

    print()
    if fails:
        print(f"{len(fails)} check(s) failed")
        sys.exit(1)
    print("card 1 replays clean on every loop")


if __name__ == "__main__":
    main()
