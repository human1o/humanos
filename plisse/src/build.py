#!/usr/bin/env python3
"""Plissé — built on Instrument Sans (Rodrigo Fuenzalida, Jordan Egstad; OFL).

    python3 plisse/src/build.py            # masters, variable font, statics, WOFF2, CSS
    python3 plisse/src/build.py --masters  # only the edited UFO masters
    PLISSE_WITHOUT=tile,space,forms,kreska  # control builds for the specimen

Pipeline
  1. Instrument Sans sources (.glyphs: wdth 75–100 × wght 400–700; upright and italic)
  2. two masters interpolated at width 97, weight 430 and 700 — measured
     against ABC Diatype: the same stem, the same set width
  3. Plissé edits on both masters (identical, so they stay compatible):
       forms  — the open R and the full-stroke $ ¢ become the default
       tile   — every dot becomes a small stone tile with bent corners
       space  — lowercase set a little closer; no pair may touch (guard)
       liga   — arrow and www ligatures moved from liga to dlig
       names  — new family name, upstream attribution kept
  4. variable font (wght 400–700), static 400/500/600/700, hinted, WOFF2
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

import ufoLib2
from fontTools.designspaceLib import (AxisDescriptor, DesignSpaceDocument,
                                      InstanceDescriptor, SourceDescriptor)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BUILD = ROOT / "build"
FONTS = ROOT / "fonts"
UPSTREAM = {False: ROOT / "sources" / "upstream" / "InstrumentSans.glyphs",
            True: ROOT / "sources" / "upstream" / "InstrumentSans-Italic.glyphs"}
sys.path.insert(0, str(HERE))

FAMILY = "Plissé"          # the name people see in font menus
FILE = "Plisse"            # ASCII: file names, PostScript names, CSS
VERSION = (1, 0)
# upstream locations of Plissé's two masters (design coordinates)
W400, W700 = 430.0, 700.0
WIDTH = 96.875            # user wdth 97 through the upstream axis map 88→87.5
WEIGHTS = [("Regular", 400), ("Medium", 500), ("SemiBold", 600), ("Bold", 700)]
WITHOUT = set(filter(None, os.environ.get("PLISSE_WITHOUT", "").split(",")))


def run(cmd, **kw):
    subprocess.run(cmd, check=True, capture_output=True, **kw)


def upstream_designspace(italic=False):
    out = BUILD / ("upstream-italic" if italic else "upstream")
    ds = out / "upstream.designspace"
    if not ds.exists():
        out.mkdir(parents=True, exist_ok=True)
        run(["fontmake", "-g", str(UPSTREAM[italic]), "-o", "ufo", "--master-dir", str(out),
             "--designspace-path", str(ds)])
    return ds


def base_masters(italic=False):
    """Interpolate the two masters, 400 and 700, from the upstream design space."""
    tag = "Italic" if italic else "Upright"
    out = BUILD / f"base-{tag}"
    want = [out / f"Base-{s}.ufo" for s in ("Regular", "Bold")]
    if all(p.exists() for p in want):
        return want
    doc = DesignSpaceDocument.fromfile(upstream_designspace(italic))
    doc.instances = []
    for name, wt in (("Regular", W400), ("Bold", W700)):
        i = InstanceDescriptor()
        i.familyName, i.styleName = "Base", name
        i.filename = str(out / f"Base-{name}.ufo")
        i.location = {"Weight": wt, "Width": WIDTH}
        doc.addInstance(i)
    tmp = upstream_designspace(italic).parent / f"base-{tag}.designspace"
    doc.write(tmp)
    run(["fontmake", "-m", str(tmp), "-o", "ufo", "-i"])
    return want


def masters(italic=False):
    import edits
    out = BUILD / ("masters-italic" if italic else "masters")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    paths = {}
    srcs = base_masters(italic)
    # a dot is tiled only where it is a dot in both masters, so they stay compatible
    dots = set.intersection(*(edits.dot_candidates(ufoLib2.Font.open(p)) for p in srcs))
    fonts = {}
    for src, style in zip(srcs, ("Regular", "Bold")):
        font = ufoLib2.Font.open(src)
        edits.apply(font, style, italic=italic, without=WITHOUT, dots=dots)
        fonts[style] = font
    if "space" not in WITHOUT:
        edits.guard(list(fonts.values()))
    for style, font in fonts.items():
        dst = out / f"{FILE}-{style}.ufo"
        font.save(dst, overwrite=True)
        paths[style] = dst
    return paths


def designspace(paths, italic=False):
    ds = DesignSpaceDocument()
    a = AxisDescriptor()
    a.tag, a.name = "wght", "Weight"
    a.minimum, a.default, a.maximum = 400, 400, 700
    ds.addAxis(a)
    for style, loc in (("Regular", 400), ("Bold", 700)):
        s = SourceDescriptor()
        s.path = str(paths[style])
        s.location = {"Weight": loc}
        if style == "Regular":
            s.copyInfo = s.copyLib = s.copyGroups = s.copyFeatures = True
        ds.addSource(s)
    for style, wt in WEIGHTS:
        i = InstanceDescriptor()
        sty = (style + " Italic").replace("Regular Italic", "Italic") if italic else style
        i.familyName, i.styleName = FAMILY, sty
        i.location = {"Weight": wt}
        ds.addInstance(i)
    out = Path(paths["Regular"]).parent / f"{FILE}.designspace"
    ds.write(out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--masters", action="store_true")
    ap.add_argument("--italic", action="store_true", help="also build the italic")
    ap.add_argument("--out", help="variable font only, to this path (control builds)")
    args = ap.parse_args()
    paths = masters()
    if args.masters:
        print(*paths.values())
        return
    import release
    if args.out:
        release.variable(designspace(paths), Path(args.out))
        print(args.out)
        return
    release.run(designspace(paths), italic_ds=designspace(masters(True), italic=True) if args.italic else None)


if __name__ == "__main__":
    main()
