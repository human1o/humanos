#!/usr/bin/env python3
"""Lamina 2 — built on Zalando Sans (KH Type, OFL).

    python3 lamina/src/build.py            # masters, variable font, statics, WOFF2, CSS
    python3 lamina/src/build.py --masters  # only the edited UFO masters
    LAMINA_WITHOUT=flank,tile ...          # control builds for the specimen

Pipeline
  1. Zalando Sans source (.glyphs, 18 masters) -> designspace
  2. two new masters interpolated at width 86: 400 and 700
  3. Lamina edits on both masters (identical, so they stay compatible):
       flank  — curves that turn vertical get longer handles: bowls stand
                on straighter sides, the lamella rhythm
       tile   — every dot becomes a small stone tile with bent corners
       space  — slightly tighter spacing for a compact text colour
       names  — new family name (the upstream Reserved Font Name is not used)
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
UPSTREAM = ROOT / "sources" / "upstream" / "ZalandoSans.glyphs"
sys.path.insert(0, str(HERE))

FAMILY = "Lamina"
VERSION = (2, 0)
WIDTH_USER = 86.0
# design coordinates of the upstream weight axis for 400 and 700
W400, W700 = 94.0, 174.0
WEIGHTS = [("Regular", 400), ("Medium", 500), ("SemiBold", 600), ("Bold", 700)]
WITHOUT = set(filter(None, os.environ.get("LAMINA_WITHOUT", "").split(",")))


def run(cmd, **kw):
    subprocess.run(cmd, check=True, capture_output=True, **kw)


def upstream_designspace():
    out = BUILD / "upstream"
    ds = out / "upstream.designspace"
    if not ds.exists():
        out.mkdir(parents=True, exist_ok=True)
        run(["fontmake", "-g", str(UPSTREAM), "-o", "ufo", "--master-dir", str(out),
             "--designspace-path", str(ds)])
    return ds


def width_design(user):
    """Upstream wdth map: 75->396, 87.5->473, 100->547."""
    pts = [(75, 396), (87.5, 473), (100, 547), (112.5, 620), (125, 730)]
    for (u0, d0), (u1, d1) in zip(pts, pts[1:]):
        if u0 <= user <= u1:
            return d0 + (user - u0) / (u1 - u0) * (d1 - d0)
    raise ValueError(user)


def base_masters(slant=0.0):
    """Interpolate the two masters at our width."""
    tag = "Italic" if slant else "Upright"
    out = BUILD / f"base-{tag}"
    want = [out / f"Base-{s}.ufo" for s in ("Regular", "Bold")]
    if all(p.exists() for p in want):
        return want
    doc = DesignSpaceDocument.fromfile(upstream_designspace())
    doc.instances = []
    wd = width_design(WIDTH_USER)
    for name, wt in (("Regular", W400), ("Bold", W700)):
        i = InstanceDescriptor()
        i.familyName, i.styleName = "Base", name
        i.filename = str(out / f"Base-{name}.ufo")
        i.location = {"Width": wd, "Weight": wt, "Slant": slant}
        doc.addInstance(i)
    tmp = BUILD / "upstream" / f"base-{tag}.designspace"
    doc.write(tmp)
    run(["fontmake", "-m", str(tmp), "-o", "ufo", "-i"])
    return want


def masters(slant=0.0):
    import edits
    out = BUILD / ("masters-italic" if slant else "masters")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    paths = {}
    for src, style in zip(base_masters(slant), ("Regular", "Bold")):
        font = ufoLib2.Font.open(src)
        edits.apply(font, style, italic=bool(slant), without=WITHOUT)
        dst = out / f"{FAMILY}-{style}.ufo"
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
    out = Path(paths["Regular"]).parent / f"{FAMILY}.designspace"
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
    release.run(designspace(paths), italic_ds=designspace(masters(-10.0), italic=True) if args.italic else None)


if __name__ == "__main__":
    main()
