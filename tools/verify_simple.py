"""Screenshot every card of the simplified booth deck, normal + reduced motion.

No test suite here, so this is the check: load dist/uploadcare-simple.html in a
headless browser, jump to each card, and capture it at the moments its
choreography matters. Also asserts the console stays clean and the embedded
mono font actually loaded.

    python tools/verify_simple.py           # writes tools/_shots/*.png
"""
import pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist" / "uploadcare-simple.html"
OUT = ROOT / "tools" / "_shots"
PROFILE = ROOT / "tools" / "_profile"

# card index -> ms after enter() worth capturing
SHOTS = {
    0: [1400, 2300, 3400],   # dropin: files in flight, over the zone, dropped
    1: [1800],               # feature row
    2: [2200],               # quote
    3: [2000],               # logo wall
    4: [4000],               # install
    # pipeline: mid-drag, bar filling, first delivery frame, two transforms in,
    # and the settled end state
    5: [1000, 2400, 4200, 6600, 8200, 11800],
    6: [3000],               # outro board + QR
}

# the bundled driver resolves an x64 path on this machine; use the arm64 build
CHROME = (pathlib.Path.home()
          / ".cache/ms-playwright-stable/chromium-1223/chrome-mac-arm64"
          / "Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing")


def run(reduced, tag):
    OUT.mkdir(parents=True, exist_ok=True)
    issues = []
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE / tag),
            executable_path=str(CHROME) if CHROME.exists() else None,
            headless=True,
            viewport={"width": 1920, "height": 1080},
            reduced_motion="reduce" if reduced else "no-preference",
            args=["--no-sandbox", "--disable-gpu"],
        )
        pg = ctx.new_page()
        pg.on("console", lambda m: issues.append(f"{m.type}: {m.text}")
              if m.type in ("error", "warning") else None)
        pg.on("pageerror", lambda e: issues.append(f"pageerror: {e}"))
        pg.goto(DIST.as_uri())
        pg.wait_for_timeout(1200)
        n = pg.evaluate("deck.slides.length")
        mono = pg.evaluate("document.fonts.check(\"18px 'Commit Mono'\")")
        print(f"[{tag}] slides={n} mono={mono}")
        for i in range(n):
            pg.evaluate(f"enter({i}); playing=false; clearTimeout(timer); clearInterval(tickTimer);")
            prev = 0
            for t in SHOTS.get(i, [2000]):
                pg.wait_for_timeout(t - prev)
                prev = t
                pg.screenshot(path=str(OUT / f"{tag}-{i}-{t}.png"))
        ctx.close()
    for msg in issues:
        print(f"[{tag}] CONSOLE {msg}")
    return issues


if __name__ == "__main__":
    bad = run(False, "norm") + run(True, "red")
    print("console issues:", len(bad))
