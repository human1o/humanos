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

CSS = """/* Plissé — Regular 400, Medium 500, SemiBold 600, Bold 700{italic_note}. Paths are relative to this file. */
@font-face {{
  font-family: "Plisse";
  src: url("Plisse[wght].woff2") format("woff2-variations"), url("Plisse[wght].woff2") format("woff2");
  font-weight: 400 700;
  font-style: normal;
  font-display: swap;
}}
{italic_face}
:root {{
  --font-plisse: "Plisse", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}

/* Prices and tables: tabular figures keep the columns straight. */
.plisse-tabular {{ font-variant-numeric: tabular-nums; }}
"""
ITALIC_FACE = """@font-face {
  font-family: "Plisse";
  src: url("Plisse-Italic[wght].woff2") format("woff2-variations"), url("Plisse-Italic[wght].woff2") format("woff2");
  font-weight: 400 700;
  font-style: italic;
  font-display: swap;
}
"""


def variable(ds, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["fontmake", "-m", str(ds), "-o", "variable", "--output-path", str(out),
                    "--flatten-components", "--filter", "DecomposeTransformedComponentsFilter"],
                   check=True, capture_output=True)
    f = TTFont(out)
    italic = "Italic" in out.name
    buildStatTable(f, [dict(tag="wght", name="Weight", values=[
        dict(value=w, name=s, **({"flags": 0x2, "linkedValue": 700} if w == 400 else {})) for s, w in WEIGHTS]),
        dict(tag="ital", name="Italic", values=[dict(value=1 if italic else 0, name="Italic" if italic else "Roman",
                                                      **({} if italic else {"flags": 0x2, "linkedValue": 1}))])])
    gasp = newTable("gasp")
    gasp.gaspRange = {0xFFFF: 0x000F}
    f["gasp"] = gasp
    f["OS/2"].fsSelection |= 0x80   # USE_TYPO_METRICS
    f["OS/2"].achVendID = "PLSE"
    # ASCII prefix for PostScript names of instances (the family name has an é)
    f["name"].setName(FAMILY, 25, 3, 1, 0x409)
    f.save(out)
    return out


def autohint(src, dst):
    from ttfautohint import ttfautohint
    ttfautohint(in_file=str(src), out_file=str(dst), no_info=True)


def woff2(src, dst):
    f = TTFont(src)
    f.flavor = "woff2"
    f.save(dst)


def statics(vf, italic=False):
    out = []
    for style, w in WEIGHTS:
        f = instancer.instantiateVariableFont(TTFont(vf), {"wght": w}, updateFontNames=True)
        if italic:
            style = "Italic" if style == "Regular" else f"{style}Italic"
        f["name"].setName(f"{FAMILY}-{style}", 6, 3, 1, 0x409)
        f["name"].removeNames(nameID=25)
        raw = ROOT / "build" / f"{FAMILY}-{style}.ttf"
        f.save(raw)
        dst = FONTS / "ttf" / f"{FAMILY}-{style}.ttf"
        autohint(raw, dst)
        woff2(dst, FONTS / "web" / f"{FAMILY}-{style}.woff2")
        out.append(dst)
    return out


def run(ds, italic_ds=None):
    for d in ("ttf", "web", "variable"):
        if (FONTS / d).exists():
            shutil.rmtree(FONTS / d)
        (FONTS / d).mkdir(parents=True)
    vf = variable(ds, FONTS / "variable" / f"{FAMILY}[wght].ttf")
    woff2(vf, FONTS / "web" / f"{FAMILY}[wght].woff2")
    statics(vf)
    if italic_ds:
        vfi = variable(italic_ds, FONTS / "variable" / f"{FAMILY}-Italic[wght].ttf")
        woff2(vfi, FONTS / "web" / f"{FAMILY}-Italic[wght].woff2")
        statics(vfi, italic=True)
    (FONTS / "web" / "plisse.css").write_text(CSS.format(
        italic_note=" (upright and italic)" if italic_ds else "",
        italic_face=ITALIC_FACE if italic_ds else ""))
    for d in ("web", "ttf", "variable"):
        shutil.copy(ROOT / "OFL.txt", FONTS / d / "OFL.txt")
    for p in sorted(FONTS.rglob("*")):
        if p.is_file():
            print(p.relative_to(ROOT), p.stat().st_size)
