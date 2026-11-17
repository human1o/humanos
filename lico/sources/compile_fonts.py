"""Compile the Lico masters: variable TTF, static instances, WOFF2."""
import shutil
import subprocess
from pathlib import Path

from fontTools.designspaceLib import (AxisDescriptor, DesignSpaceDocument,
                                      InstanceDescriptor, SourceDescriptor)
from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib import TTFont, newTable
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
FONTS = ROOT / "fonts"
FAMILY = "Lico"

# user weight -> design coordinate (the upstream optical weight curve)
WEIGHTS = [("Light", 300, 305), ("Regular", 400, 400), ("Medium", 500, 476), ("SemiBold", 600, 572),
           ("Bold", 700, 680), ("ExtraBold", 800, 793), ("Black", 900, 900)]


def designspace(paths):
    ds = DesignSpaceDocument()
    axis = AxisDescriptor()
    axis.tag, axis.name = "wght", "Weight"
    axis.minimum, axis.default, axis.maximum = 300, 400, 900
    axis.map = [(user, design) for _, user, design in WEIGHTS]
    ds.addAxis(axis)
    for style, loc in (("Light", 305), ("Regular", 400), ("Black", 900)):
        s = SourceDescriptor()
        s.path = str(paths[style])
        s.familyName, s.styleName = FAMILY, style
        s.location = {"Weight": loc}
        if style == "Regular":
            s.copyLib = s.copyGroups = s.copyFeatures = s.copyInfo = True
        ds.addSource(s)
    for style, user, design in WEIGHTS:
        i = InstanceDescriptor()
        i.familyName, i.styleName = FAMILY, style
        i.name = f"{FAMILY} {style}"
        i.postScriptFontName = f"{FAMILY}-{style}"
        i.location = {"Weight": design}
        if style in ("Regular", "Bold"):
            i.styleMapFamilyName, i.styleMapStyleName = FAMILY, style.lower()
        else:
            i.styleMapFamilyName, i.styleMapStyleName = f"{FAMILY} {style}", "regular"
        ds.addInstance(i)
    out = BUILD / "masters" / f"{FAMILY}.designspace"
    ds.write(out)
    return out


def finish(font, variable):
    """Tables fontmake leaves to the project: STAT, gasp, clean names."""
    if variable:
        buildStatTable(font, [dict(
            tag="wght", name="Weight",
            values=[dict(value=user, name=style,
                         **({"flags": 0x2, "linkedValue": 700} if user == 400 else {}))
                    for style, user, _ in WEIGHTS])])
    gasp = newTable("gasp")
    gasp.gaspRange = {0xFFFF: 0x000F}
    font["gasp"] = gasp


def autohint(path):
    """Static fonts get TrueType hints for Windows rasterisers (the variable
    font is left unhinted, as ttfautohint cannot hint variations)."""
    try:
        from ttfautohint import ttfautohint
    except ImportError:
        print("ttfautohint not installed; static fonts left unhinted")
        return
    tmp = path.with_suffix(".hinted.ttf")
    ttfautohint(in_file=str(path), out_file=str(tmp), no_info=True)
    tmp.replace(path)


def save_woff2(src, dst):
    f = TTFont(src)
    f.flavor = "woff2"
    f.save(dst)


def run(paths):
    ds = designspace(paths)
    var_dir, static_dir, web_dir = FONTS / "variable", FONTS / "static", FONTS / "web"
    for d in (var_dir, static_dir, web_dir):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
    vf_path = var_dir / f"{FAMILY}[wght].ttf"
    subprocess.run(
        ["fontmake", "-m", str(ds), "-o", "variable", "--output-path", str(vf_path),
         "--flatten-components", "--no-production-names"],
        check=True, capture_output=True, cwd=BUILD)
    vf = TTFont(vf_path)
    finish(vf, variable=True)
    vf.save(vf_path)
    save_woff2(vf_path, web_dir / f"{FAMILY}-Variable.woff2")
    for style, user, _ in WEIGHTS:
        inst = instancer.instantiateVariableFont(
            TTFont(vf_path), {"wght": user}, updateFontNames=True)
        finish(inst, variable=False)
        p = static_dir / f"{FAMILY}-{style}.ttf"
        inst.save(p)
        autohint(p)
        save_woff2(p, web_dir / f"{FAMILY}-{style}.woff2")
    print("fonts:", vf_path)
