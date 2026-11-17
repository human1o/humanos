"""Plissé — compile: variable font, four static weights, hinting, WOFF2, CSS."""
import shutil
import subprocess
from pathlib import Path

from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib import TTFont, newTable
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"
FAMILY = "Plisse"   # file names and the CSS family; font menus show "Plissé"
WEIGHTS = [("Regular", 400), ("Medium", 500), ("SemiBold", 600), ("Bold", 700)]

CSS = """/* Plissé {version}: Regular 400, Medium 500, SemiBold 600, Bold 700.
   Paths are relative to this file; ?v= makes browsers fetch a new release. */
@font-face {{
  font-family: "Plisse";
  src: url("Plisse[wght].woff2?v={version}") format("woff2");
  font-weight: 400 700;
  font-style: normal;
  font-display: swap;
}}

:root {{
  --font-plisse: "Plisse", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}

/* Prices, tables, totals: every figure the same width, columns line up. */
.plisse-tabular {{ font-variant-numeric: tabular-nums; }}
/* Order numbers and codes: 0 with a tile inside, never confused with O. */
.plisse-code {{ font-feature-settings: "zero"; }}
"""


def _overlap_flags(f):
    """Mark every glyph as possibly overlapping (OVERLAP_SIMPLE / _COMPOUND),
    so macOS and every other rasteriser fill overlaps correctly."""
    glyf = f["glyf"]
    for name in f.getGlyphOrder():
        g = glyf[name]
        if g.isComposite():
            g.components[0].flags |= 0x0400
        elif g.numberOfContours > 0:
            g.flags[0] |= 0x40


def variable(ds, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["fontmake", "-m", str(ds), "-o", "variable", "--output-path", str(out),
                    "--flatten-components", "--filter", "DecomposeTransformedComponentsFilter"],
                   check=True, capture_output=True)
    f = TTFont(out)
    buildStatTable(f, [dict(tag="wght", name="Weight", values=[
        dict(value=w, name=s, **({"flags": 0x2, "linkedValue": 700} if w == 400 else {})) for s, w in WEIGHTS])])
    gasp = newTable("gasp")
    gasp.gaspRange = {0xFFFF: 0x000F}
    f["gasp"] = gasp
    f["OS/2"].fsSelection |= 0x80   # USE_TYPO_METRICS
    f["OS/2"].achVendID = "PLSE"
    # ASCII prefix for PostScript names of instances (the family name has an é)
    f["name"].setName(FAMILY, 25, 3, 1, 0x409)
    _overlap_flags(f)
    f.save(out)
    return out


def autohint(src, dst):
    from ttfautohint import ttfautohint
    ttfautohint(in_file=str(src), out_file=str(dst), no_info=True)


def woff2(src, dst):
    f = TTFont(src)
    f.flavor = "woff2"
    f.save(dst)


def statics(vf):
    out = []
    for style, w in WEIGHTS:
        # overlaps are merged into single outlines: static fonts go to print,
        # PDF and old rasterisers that do not all fill overlaps the same way
        f = instancer.instantiateVariableFont(TTFont(vf), {"wght": w}, updateFontNames=True,
                                              overlap=instancer.OverlapMode.REMOVE)
        f["name"].setName(f"{FAMILY}-{style}", 6, 3, 1, 0x409)
        f["name"].removeNames(nameID=25)
        raw = ROOT / "build" / f"{FAMILY}-{style}.ttf"
        f.save(raw)
        dst = FONTS / "ttf" / f"{FAMILY}-{style}.ttf"
        autohint(raw, dst)
        woff2(dst, FONTS / "web" / f"{FAMILY}-{style}.woff2")
        out.append(dst)
    return out


def run(ds):
    from build import VERSION
    version = f"{VERSION[0]}.{VERSION[1]:03d}"
    for d in ("ttf", "web", "variable"):
        if (FONTS / d).exists():
            shutil.rmtree(FONTS / d)
        (FONTS / d).mkdir(parents=True)
    vf = variable(ds, FONTS / "variable" / f"{FAMILY}[wght].ttf")
    woff2(vf, FONTS / "web" / f"{FAMILY}[wght].woff2")
    statics(vf)
    (FONTS / "web" / "plisse.css").write_text(CSS.format(version=version))
    for d in ("web", "ttf", "variable"):
        shutil.copy(ROOT / "OFL.txt", FONTS / d / "OFL.txt")
    for p in sorted(FONTS.rglob("*")):
        if p.is_file():
            print(p.relative_to(ROOT), p.stat().st_size)
