#!/usr/bin/env python3
"""Card 4: assert the swap is a swap, not a jump cut.

The card's whole claim is that only the background changes. That is a property
of the two exports registering against each other, which no amount of CSS can
fix and a screenshot at one instant cannot show. So this samples across the
wipe and checks three things:

  * geometry — the plate and well sit on Figma frame 213:1313, and the well is
    the exports' native 623x455 so neither frame is ever resampled;
  * the wipe actually travels — the after frame's clip moves left to right
    rather than the two photos crossfading;
  * the product does not move — the bottle's silhouette lands in the same
    column band before and after, which is what makes a wipe legible at all.

Run with the same launch path as the other tools/ checks.
"""

import pathlib
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist" / "uploadcare-simple.html"
PROFILE = ROOT / "tools" / "_profile"

# the bundled driver resolves an x64 path on this machine; find an arm64 build.
# Two caches are in play depending on how Playwright was last installed, and the
# revision moves, so glob rather than pin — a missing browser should read as
# "install one", not as a geometry failure.
CHROME = next(
    (p for root in (pathlib.Path.home() / ".cache/ms-playwright-stable",
                    pathlib.Path.home() / "Library/Caches/ms-playwright")
     for p in sorted(root.glob("chromium-*/chrome-mac-arm64/*.app/Contents/MacOS/*"),
                     reverse=True)
     if p.is_file()), None)

CARD = 3  # zero-based: card 4

# left, top, width, height — from frame 213:1313
SPEC = {
    ".ee-panel": (640, 485, 641, 473),
    ".ee-well": (649, 494, 623, 455),
}

fails = []


def check(label, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {label}{'  ' + detail if detail else ''}")
    if not ok:
        fails.append(label)


def main():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(PROFILE), headless=True,
            executable_path=str(CHROME) if CHROME else None,
            viewport={"width": 1920, "height": 1080},
            reduced_motion="no-preference", device_scale_factor=1)
        pg = ctx.pages[0] if ctx.pages else ctx.new_page()
        errors = []
        pg.on("console", lambda m: m.type == "error" and errors.append(m.text))
        pg.goto(DIST.as_uri())
        pg.wait_for_timeout(700)

        # land on the card from elsewhere so .active toggles and the CSS
        # animations restart from zero — entering the live card is a no-op.
        # Geometry is measured after .reveal settles: that class animates
        # transform, so a panel sampled mid-entrance reads ~16px low and the
        # frame's y looks wrong when only the animation is unfinished.
        pg.evaluate("enter(0)")
        pg.wait_for_timeout(250)
        pg.evaluate(f"enter({CARD})")
        pg.wait_for_timeout(1000)

        print("\ngeometry (frame 213:1313)")
        for sel, want in SPEC.items():
            box = pg.evaluate(
                """(s)=>{const e=document.querySelector('.slide.active '+s);
                   if(!e) return null; const r=e.getBoundingClientRect(),
                   st=document.getElementById('stage').getBoundingClientRect(),
                   k=st.width/1920;
                   return [(r.x-st.x)/k,(r.y-st.y)/k,r.width/k,r.height/k];}""", sel)
            if box is None:
                check(sel, False, "missing")
                continue
            got = tuple(round(v, 1) for v in box)
            ok = all(abs(g - w) <= 1 for g, w in zip(got, want))
            check(sel, ok, f"{got} want {want}")

        nat = pg.evaluate(
            """()=>{const i=document.querySelector('.slide.active .ee-well img');
               return i?[i.naturalWidth,i.naturalHeight]:null;}""")
        check("exports are the well's native size", nat == [623, 455], str(nat))

        print("\nthe wipe travels left to right")
        pg.evaluate("enter(0)")
        pg.wait_for_timeout(250)
        pg.evaluate(f"enter({CARD})")
        pg.wait_for_timeout(120)
        seen = []
        for _ in range(16):
            seen.append(pg.evaluate(
                """()=>{const a=document.querySelector('.slide.active .ee-after');
                   if(!a) return null; const c=getComputedStyle(a);
                   return [c.clipPath, c.opacity];}"""))
            pg.wait_for_timeout(120)
        rights = []
        for cp, _op in [s for s in seen if s]:
            if cp and "inset" in cp:
                parts = cp.replace("inset(", "").rstrip(")").split()
                rights.append(parts[1] if len(parts) > 1 else parts[0])
        uniq = [r for i, r in enumerate(rights) if i == 0 or r != rights[i - 1]]
        check("after frame is clipped, not crossfaded",
              len(uniq) >= 4, f"{len(uniq)} distinct clips")
        pcts = [float(r.rstrip("%")) for r in rights if r.endswith("%")]
        check("clip opens monotonically",
              bool(pcts) and all(b <= a + 0.5 for a, b in zip(pcts, pcts[1:])),
              f"{pcts[0]:.0f}% -> {pcts[-1]:.0f}%" if pcts else "no % clips")

        pg.wait_for_timeout(1200)
        end = pg.evaluate(
            """()=>{const a=document.querySelector('.slide.active .ee-after');
               const c=getComputedStyle(a); return [c.clipPath,c.opacity];}""")
        check("settles fully revealed",
              end[1] == "1" and ("inset(0" in end[0] or end[0] == "none"),
              str(end))

        print("\nthe product does not move")
        ecom = ROOT / "assets" / "ecommerce"
        dx, dy, overlap = _register(ecom / "editor-before.jpg", ecom / "editor-after.jpg")
        check("exports register on the product",
              (dx, dy) == (0, 0), f"best offset ({dx},{dy}), {overlap:.1%} silhouette overlap")
        check("silhouettes are the same product",
              overlap >= 0.95, f"{overlap:.1%}")

        shots = ROOT / "tools" / "_shots"
        shots.mkdir(parents=True, exist_ok=True)
        (shots / "card4-after.png").write_bytes(pg.screenshot(clip=_wellbox(pg)))
        drift = _mean_abs_diff(shots / "card4-after.png", ecom / "editor-after.jpg")
        check("settled frame is the after export",
              drift is not None and drift < 6, f"mean abs diff {drift:.1f}/255")

        print("\nconsole")
        check("clean", not errors, "; ".join(errors[:3]))
        ctx.close()

    print("\n" + ("all checks passed" if not fails else f"{len(fails)} FAILED: " + ", ".join(fails)))
    return 1 if fails else 0


def _wellbox(pg):
    r = pg.evaluate("""()=>{const e=document.querySelector('.slide.active .ee-well');
        const b=e.getBoundingClientRect();
        return {x:b.x,y:b.y,width:b.width,height:b.height};}""")
    return r


def _dark(path, thr=60):
    """Near-black mask, cropped to the column band the bottle occupies.

    Thresholding the whole frame is useless here: the before frame's rock is
    dark too, so a naive column profile reports the rock's edge as the
    product's. The band keeps the comparison on the one object that must not
    move.
    """
    from PIL import Image
    im = Image.open(path).convert("L")
    if im.size != (623, 455):
        im = im.resize((623, 455))
    px = im.load()
    return {(x, y) for y in range(30, 440) for x in range(240, 430) if px[x, y] < thr}


def _register(a_path, b_path, span=6):
    """Offset that best aligns the two silhouettes, and how well they overlap.

    A wipe only reads as "the background changed" if the product is pinned. If
    the best offset is anything but (0,0) the swap is a jump cut, however
    pretty the sweep is.
    """
    a, b = _dark(a_path), _dark(b_path)
    if not a or not b:
        return 99, 99, 0.0
    best = (99, 99, 0.0)
    for dy in range(-span, span + 1):
        for dx in range(-span, span + 1):
            hit = len(a & {(x + dx, y + dy) for x, y in b})
            score = hit / max(len(a), len(b))
            if score > best[2]:
                best = (dx, dy, score)
    return best


def _mean_abs_diff(a_path, b_path):
    """How far the rendered well is from the after export, 0-255."""
    from PIL import Image, ImageChops, ImageStat
    a = Image.open(a_path).convert("RGB")
    b = Image.open(b_path).convert("RGB")
    if a.size != b.size:
        a = a.resize(b.size)
    return sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / 3


if __name__ == "__main__":
    sys.exit(main())
