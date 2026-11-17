#!/usr/bin/env python3
"""Build Lico from the vendored Schibsted Grotesk sources.

    python3 lico/sources/build.py            # masters + variable font + webfonts
    python3 lico/sources/build.py --masters  # only write the patched UFO masters

Pipeline: upstream .glyphs -> UFO masters -> Lico redesign (shapes.py,
edits.py) -> fontmake variable TTF -> WOFF2 + static instances.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import ufoLib2

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BUILD = ROOT / "build"
UPSTREAM = HERE / "upstream" / "SchibstedGrotesk.glyphs"
sys.path.insert(0, str(HERE))

import shapes  # noqa: E402

FAMILY = "Lico"
MASTERS = {"Regular": shapes.REGULAR, "Black": shapes.BLACK}


def export_upstream():
    base = BUILD / "upstream"
    if (base / "SchibstedGrotesk-Regular.ufo").exists():
        return base
    base.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["fontmake", "-g", str(UPSTREAM), "-o", "ufo", "--master-dir", str(base),
         "--designspace-path", str(base / "upstream.designspace")],
        check=True, capture_output=True)
    return base


def patch_master(font, p):
    import edits
    rec = edits.pre(font, p)      # derived glyphs + alternates first
    for name, fn in shapes.DRAW.items():
        fn(font[name], p)
    edits.post(font, p, rec)      # composites, kerning, features, names


LIGHT = 0.19  # how far the Light master sits beyond Regular, away from Black


def extrapolate_light(reg, black, f=LIGHT):
    """Light = Regular + f * (Regular - Black). Both drawn masters are
    point-compatible, so the lighter master is a straight extrapolation of
    every coordinate, advance, anchor and kerning value."""
    import copy

    def ex(a, b):
        return round(a + f * (a - b))

    light = copy.deepcopy(reg)
    light.info.styleName = "Light"
    light.info.postscriptFontName = f"{FAMILY}-Light"
    light.info.postscriptFullName = f"{FAMILY} Light"
    for g in light:
        gb = black[g.name]
        g.width = ex(g.width, gb.width)
        for c, cb in zip(g.contours, gb.contours):
            for q, qb in zip(c.points, cb.points):
                q.x, q.y = ex(q.x, qb.x), ex(q.y, qb.y)
        for a, ab in zip(g.anchors, gb.anchors):
            a.x, a.y = ex(a.x, ab.x), ex(a.y, ab.y)
        for comp, compb in zip(g.components, gb.components):
            t, tb = list(comp.transformation), compb.transformation
            t[4], t[5] = ex(t[4], tb[4]), ex(t[5], tb[5])
            comp.transformation = tuple(t)
    for pair in set(reg.kerning) | set(black.kerning):
        v = ex(reg.kerning.get(pair, 0), black.kerning.get(pair, 0))
        if v:
            light.kerning[pair] = v
        elif pair in light.kerning:
            del light.kerning[pair]
    return light


def write_masters():
    base = export_upstream()
    out = BUILD / "masters"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    fonts = {}
    for style, p in MASTERS.items():
        font = ufoLib2.Font.open(base / f"SchibstedGrotesk-{style}.ufo")
        patch_master(font, p)
        fonts[style] = font
    fonts["Light"] = extrapolate_light(fonts["Regular"], fonts["Black"])
    paths = {}
    for style, font in fonts.items():
        dst = out / f"{FAMILY}-{style}.ufo"
        font.save(dst, overwrite=True)
        paths[style] = dst
    return paths


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--masters", action="store_true")
    args = ap.parse_args()
    paths = write_masters()
    print("masters:", *paths.values())
    if not args.masters:
        import compile_fonts
        compile_fonts.run(paths)
