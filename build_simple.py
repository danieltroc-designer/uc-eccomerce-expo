#!/usr/bin/env python3
"""
Build the *simplified* Uploadcare TV show (the 7-card booth loop).

Standalone from build.py so the main deck is never touched: this reads
src/simple.template.html, inlines the same assets (reusing build.py's
encoders) plus a generated QR code, and writes a separate self-contained
file to dist/uploadcare-simple.html.

Usage:
    python build_simple.py            # writes dist/uploadcare-simple.html
    python build_simple.py --watch    # rebuild on any change under src/ or assets/

The QR points at CTA_URL below — change it once the final booth/landing URL
is confirmed.
"""

import base64
import json
import re
import sys
import time
from pathlib import Path

import build  # reuse every encoder + the ROOT/asset paths from the main build

ROOT = build.ROOT
SRC = ROOT / "src" / "simple.template.html"
OUT = ROOT / "dist" / "uploadcare-simple.html"
LOGOS = ROOT / "assets" / "logos"
UPLOADER_UI = ROOT / "assets" / "uploader"
DEMO = ROOT / "assets" / "demo"

# The three-panel pipeline card runs on one photo and the three transforms the
# on-screen URL builds up, so the frames have to match the ops exactly:
#   crop/face -> scale_crop/460x460/center -> border_radius/50p
# They're pre-rendered by the CDN and inlined here because the deck has to run
# with no network at the booth.
DEMO_FRAMES = {
    "original": "portrait.jpg",
    "step1":    "step1-crop.jpg",
    "step2":    "step2-square.jpg",
    "step3":    "step3-round.png",
}

# Customer logos for the "Trusted by" wall, in the storyboard's order. Each is
# the isolated white vector exported from the Figma frame — not a wordmark we
# set in type, so the marks stay correct.
LOGO_ORDER = ("zapier", "soundcloud", "loreal", "sequoia",
              "usertesting", "prezly", "aryeo", "marko")

# The real uploader widget's chrome: the dropzone glyph and one icon per
# upload source. Keys are what the template looks them up by. The pointer is
# not here — it reuses the deck's existing cursor (see encode_uploader_ui).
UPLOADER_ICONS = {
    "upload": "icon-upload.svg", "device": "icon-device.svg",
    "camera": "icon-camera.svg", "dropbox": "icon-dropbox.svg",
    "gdrive": "icon-gdrive.svg", "link": "icon-link.svg",
}

# Where the card-7 QR sends people. Swap for the final Webflow-integration /
# landing URL when confirmed.
CTA_URL = "https://uploadcare.com/webflow/"


def inline_svg(path: Path) -> str:
    """Minify an SVG and hand sizing over to CSS.

    Figma exports carry a fixed width/height plus preserveAspectRatio="none";
    both have to go or the mark stretches when CSS sets only one dimension.
    The viewBox survives, so the intrinsic aspect ratio still applies.

    Some exports also emit `Cnan nan x2 y2 x y` — Figma drops the first control
    point when it writes a circular arc as a cubic. Those arcs are smooth
    joins, so the missing point is exactly the reflection of the previous
    segment's second control point, which is what `S` means. The substitution
    is lossless rather than a guess.
    """
    svg = build.minify_svg(path)
    svg = re.sub(r"C\s*nan\s+nan\s+", "S", svg)
    m = re.match(r"<svg[^>]*>", svg)
    if not m:
        return svg
    head = re.sub(r'\s(?:width|height)="[\d.]+(?:px)?"', "", m.group(0))
    head = head.replace(' preserveAspectRatio="none"', "")
    return head + svg[m.end():]


def encode_logos() -> str:
    """JSON map of customer-logo name -> inline SVG, for the trusted-by wall."""
    return json.dumps({n: inline_svg(LOGOS / f"{n}.svg") for n in LOGO_ORDER})


def encode_uploader_ui() -> str:
    """JSON map of the uploader-widget chrome: inline SVG icons + file thumbs.

    Icons stay as inline SVG (crisp at any scale, styleable); the two dragged
    file thumbnails are photos, so they go in as base64 PNG data URIs.
    """
    out = {k: inline_svg(UPLOADER_UI / f) for k, f in UPLOADER_ICONS.items()}
    # the storyboard's cursor exported as an empty mask, so use the pointer the
    # upload-demo slide already uses — same mark, and one cursor across the deck
    out["cursor"] = inline_svg(build.PHOTOS / "Cursor.svg")
    for key in ("file-mp4", "file-png"):
        b64 = base64.b64encode((UPLOADER_UI / f"{key}.png").read_bytes()).decode()
        out[key] = f"data:image/png;base64,{b64}"
    return json.dumps(out)


def encode_demo() -> str:
    """JSON map of pipeline-card frame name -> base64 data URI."""
    out = {}
    for key, name in DEMO_FRAMES.items():
        path = DEMO / name
        mime = "image/png" if path.suffix == ".png" else "image/jpeg"
        b64 = base64.b64encode(path.read_bytes()).decode()
        out[key] = f"data:{mime};base64,{b64}"
    return json.dumps(out)


def make_qr(url: str) -> str:
    """Return an inline monochrome SVG QR for `url`.

    Uses segno if available (pure-python, no deps); falls back to a neutral
    placeholder tile so the build never breaks offline. The SVG is sized by CSS
    (viewBox only), foreground pure white so it reads on the dark card.
    """
    try:
        import segno  # type: ignore
        import io as _io

        qr = segno.make(url, error="m")
        buf = _io.BytesIO()
        # dark modules on a solid white field so it scans on the white CTA card
        qr.save(buf, kind="svg", border=2, dark="#0b0b0f", light="#ffffff",
                xmldecl=False, svgns=True, nl=False)
        svg = buf.getvalue().decode("utf-8")
        # segno emits width/height in module units but no viewBox — add one so the
        # QR scales to fill its CSS box, then drop the fixed size.
        import re as _re
        wm = _re.search(r'width="([\d.]+)"', svg)
        hm = _re.search(r'height="([\d.]+)"', svg)
        if wm and hm:
            svg = svg.replace("<svg", f'<svg viewBox="0 0 {wm.group(1)} {hm.group(1)}"', 1)
        svg = _re.sub(r'\swidth="[\d.]+"', "", svg, count=1)
        svg = _re.sub(r'\sheight="[\d.]+"', "", svg, count=1)
        return svg
    except Exception as exc:  # pragma: no cover - placeholder path
        print(f"  (segno unavailable: {exc} — using placeholder QR)")
        return (
            '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">'
            '<rect width="100" height="100" fill="none" stroke="#ffffff" '
            'stroke-width="2"/><text x="50" y="54" fill="#ffffff" '
            'font-size="10" text-anchor="middle" font-family="monospace">QR</text></svg>'
        )


def build_simple() -> None:
    html = SRC.read_text()

    # The main deck's token set (this template is a superset of it) plus the
    # three that only exist here: the CTA QR, the customer logos, and the
    # uploader-widget chrome.
    replacements = {
        "/*__COMMIT_MONO__*/": build.encode_fonts(),
        "/*__INTER_VAR__*/":   build.encode_variable_font(),
        "/*__JB_MONO__*/":     build.encode_jbmono(),
        "__LOGO_SVG__":        build.prepare_logo(),
        "__GLYPH_SVG__":       build.prepare_glyph(),
        "__GLOBE_SVG__":       build.minify_svg(build.BRAND / "globe.svg"),
        "__ASSETS_JSON__":     build.encode_photos(),
        "__UPLOADER_JSON__":   build.encode_uploader(),
        "__PIXEL_JSON__":      build.encode_pixel_reveal(),
        "__QR_SVG__":          make_qr(CTA_URL),
        "__LOGOS_JSON__":      encode_logos(),
        "__UPLOADERUI_JSON__": encode_uploader_ui(),
        "__DEMO_JSON__":       encode_demo(),
    }
    for token, value in replacements.items():
        if token not in html:
            raise SystemExit(f"ERROR: token {token!r} not found in template")
        html = html.replace(token, value)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html)
    print(f"built {OUT.relative_to(ROOT)}  ({len(html):,} bytes)")


def watch() -> None:
    watched = list((ROOT / "src").rglob("*")) + list((ROOT / "assets").rglob("*"))
    mtimes = {p: p.stat().st_mtime for p in watched if p.is_file()}
    build_simple()
    print("watching for changes… (Ctrl-C to stop)")
    try:
        while True:
            time.sleep(0.6)
            changed = False
            for base in ("src", "assets"):
                for p in (ROOT / base).rglob("*"):
                    if p.is_file() and mtimes.get(p) != p.stat().st_mtime:
                        mtimes[p] = p.stat().st_mtime
                        changed = True
            if changed:
                try:
                    build_simple()
                except SystemExit as e:
                    print(e)
    except KeyboardInterrupt:
        print("\nstopped.")


if __name__ == "__main__":
    (watch if "--watch" in sys.argv else build_simple)()
