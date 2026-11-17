#!/usr/bin/env python3
"""Lamina — build static fonts from the glyph drawings."""
import argparse
import importlib
import sys
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.areaPen import AreaPen

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import params  # noqa: E402
from params import ASC, CAP, DESC, UPM, XH  # noqa: E402
from registry import GLYPHS, ORDER, G  # noqa: E402

FAMILY = "Lamina"
MODULES = ["lower", "upper", "figures", "punct", "marks", "accented"]


def load_modules(names=MODULES):
    for m in names:
        try:
            importlib.import_module(m)
        except ModuleNotFoundError as e:
            if e.name != m:
                raise


def spacing(p):
    return {
        "S": p.sbS, "R": p.sbR, "SC": p.sbSC, "RC": p.sbRC, "R0": params.mix(46, 40, p.w),
    }


def draw_all(p, only=None):
    """Evaluate every glyph for parameters p. Returns name -> dict."""
    sp = spacing(p)
    out = {}
    for name in ORDER:
        if only and name not in only:
            continue
        fn, unis = GLYPHS[name]
        g = fn(p)
        if g.components is not None:
            out[name] = dict(components=g.components, advance=g.advance, unis=unis, anchors=g.anchors)
            continue
        shape = g.shape
        b = shape.bounds()
        if g.advance is not None:
            out[name] = dict(shape=shape, advance=g.advance, unis=unis, anchors=g.anchors, shift=0)
            continue
        lsb = sp[g.left] if isinstance(g.left, str) else g.left
        rsb = sp[g.right] if isinstance(g.right, str) else g.right
        shift = lsb - b[0]
        adv = (b[2] - b[0]) + lsb + rsb
        out[name] = dict(shape=shape.move(shift) if shift else shape, advance=adv, unis=unis,
                         anchors={k: (x + shift, y) for k, (x, y) in g.anchors.items()}, shift=shift)
    add_composites(p, out, only)
    return out


def _band(shape, y0, y1):
    from geom import rect
    sh = shape & rect(-5000, y0, 5000, y1)
    return sh.bounds()


def anchor(p, out, base, kind):
    from params import OS, OSC
    from marks import dsize, lc_base
    g = out[base]
    sh = g["shape"]
    b = sh.bounds()
    upper = base[0].isupper()
    if kind == "top":
        bb = _band(sh, (CAP if upper else XH) - 40, (CAP + OSC if upper else XH + OS) + 1)
        return (bb[0] + bb[2]) / 2, 0
    if kind == "top_asc":
        bb = _band(sh, ASC - 40, ASC + 1)
        return (bb[0] + bb[2]) / 2, (ASC + 78) - lc_base(p)
    if kind in ("alt", "altcap"):
        d = dsize(p) * 0.92
        if base == "t":
            bb = _band(sh, XH + 60, XH + 140)
        elif kind == "altcap":
            bb = _band(sh, CAP - 60, CAP)
        else:
            bb = _band(sh, ASC - 60, ASC)
        dy = (CAP - ASC) if kind == "altcap" else 0
        return bb[2] + d * 0.5 + 44, dy
    if kind == "ogonek":
        bb = _band(sh, 0, 40)
        if base in ("a", "u"):
            return bb[2] - p.V / 2, 0
        if base == "A":
            return bb[2] - p.VC * 0.62, 0
        if base == "E":
            return bb[2] - p.VC * 0.9, 0
        if base in ("e", "U"):
            bb = _band(sh, -OSC, 40)
            return (bb[0] + bb[2]) / 2 + (bb[2] - bb[0]) * 0.20, 0
        return (bb[0] + bb[2]) / 2, 0
    if kind == "bottom":
        if base in ("t", "T"):
            bb = _band(sh, 60, 200)
        else:
            bb = _band(sh, -OSC, 40)
        return (bb[0] + bb[2]) / 2, 0
    raise KeyError(kind)


def add_composites(p, out, only=None):
    try:
        from accented import COMPOSITES
    except ModuleNotFoundError:
        return
    for name, uni, base, marks in COMPOSITES:
        if only and name not in only:
            continue
        if base not in out or "shape" not in out[base]:
            continue
        comps = [(base, 0, 0)]
        adv = out[base]["advance"]
        for mark, kind in marks:
            x, dy = anchor(p, out, base, kind)
            comps.append((mark, x, dy))
            if kind in ("alt", "altcap"):
                from marks import dsize
                right = x + dsize(p) * 0.46
                adv = max(adv, right + (16 if base == "t" else 30))
        out[name] = dict(components=comps, advance=adv, unis=[uni] if uni else [], anchors={})


def tt_glyph(shape):
    pen = TTGlyphPen(None)
    # TrueType wants clockwise outer contours
    area = AreaPen()
    shape.path.draw(area)
    target = ReverseContourPen(pen) if area.value > 0 else pen
    shape.path.draw(Cu2QuPen(target, max_err=0.6, reverse_direction=False))
    return pen.glyph()


VERSION = "1.000"
COPYRIGHT = "Copyright 2026 The Lamina Project Authors"
LICENSE = ("This Font Software is licensed under the SIL Open Font License, Version 1.1. "
           "This license is available with a FAQ at: https://openfontlicense.org")
DESCRIPTION = ("Lamina: a grotesk built on the lamella. Every letter stands on an even "
               "vertical rhythm; every stroke that turns bends through the same curve, "
               "and every stroke that ends is cut square to the page.")


def build_font(style, out_path, only=None, kern=True, features=True):
    from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
    from fontTools.ttLib import newTable
    weight, w = params.WEIGHTS[style]
    p = params.P(w)
    glyphs = draw_all(p, only)
    if not only:
        add_derived(p, glyphs)
    order = [".notdef", "space"] + [n for n in ORDER if n in glyphs and n not in (".notdef", "space")]
    order += [n for n in glyphs if n not in order]
    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    cmap = {}
    for n in order:
        for u in glyphs.get(n, {}).get("unis", []):
            cmap[u] = n
    fb.setupCharacterMap(cmap)
    ttg, metrics = {}, {}
    from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent
    for n in order:
        if n == ".notdef":
            pen = TTGlyphPen(None)
            for c in [((60, 0), (60, 700), (440, 700), (440, 0)), ((120, 60), (380, 60), (380, 640), (120, 640))]:
                pen.moveTo(c[0])
                for q in c[1:]:
                    pen.lineTo(q)
                pen.closePath()
            ttg[n] = pen.glyph()
            metrics[n] = (500, 60)
            continue
        g = glyphs[n]
        if "components" in g:
            gl = Glyph()
            gl.numberOfContours = -1
            gl.components = []
            for i, (base, dx, dy) in enumerate(g["components"]):
                c = GlyphComponent()
                c.glyphName = base
                c.x, c.y = round(dx), round(dy)
                c.flags = 0x4 if i == 0 else 0   # first component sets the metrics
                gl.components.append(c)
            ttg[n] = gl
        elif g["shape"].empty():
            ttg[n] = TTGlyphPen(None).glyph()
        else:
            ttg[n] = tt_glyph(g["shape"])
        metrics[n] = (round(g["advance"]), 0)
    fb.setupGlyf(ttg)
    glyf = fb.font["glyf"]
    for n in order:
        gl = glyf[n]
        if gl.isComposite() or gl.numberOfContours:
            gl.recalcBounds(glyf)
            metrics[n] = (metrics[n][0], gl.xMin)
    fb.setupHorizontalMetrics(metrics)
    asc, desc = 940, -260
    fb.setupHorizontalHeader(ascent=asc, descent=desc, lineGap=0)
    is_rib = style in ("Regular", "Bold")
    fam = FAMILY if is_rib else f"{FAMILY} {style}"
    sub = style if is_rib else "Regular"
    names = dict(
        copyright=COPYRIGHT, familyName=fam, styleName=sub,
        uniqueFontIdentifier=f"{VERSION};LMNA;{FAMILY}-{style}",
        fullName=f"{FAMILY} {style}", version=f"Version {VERSION}", psName=f"{FAMILY}-{style}",
        description=DESCRIPTION, licenseDescription=LICENSE, licenseInfoURL="https://openfontlicense.org",
        typographicFamily=FAMILY, typographicSubfamily=style,
    )
    fb.setupNameTable(names)
    ybox = [glyf[n].yMin for n in order if hasattr(glyf[n], "yMin")]
    ytop = [glyf[n].yMax for n in order if hasattr(glyf[n], "yMax")]
    fs = (0x20 if style == "Bold" else 0x40) | 0x80   # BOLD or REGULAR, USE_TYPO_METRICS
    fb.setupOS2(version=4, sTypoAscender=asc, sTypoDescender=desc, sTypoLineGap=0,
                usWinAscent=max(ytop + [asc]), usWinDescent=-min(ybox + [desc]),
                sxHeight=XH, sCapHeight=CAP, usWeightClass=weight, usWidthClass=5,
                fsSelection=fs, achVendID="LMNA", fsType=0,
                ulUnicodeRange1=0b11, ulCodePageRange1=0b11)
    fb.setupPost(keepGlyphNames=True)
    from fontTools.misc.timeTools import timestampNow
    fb.setupHead(unitsPerEm=UPM, fontRevision=float(VERSION), macStyle=1 if style == "Bold" else 0,
                 created=timestampNow(), modified=timestampNow())
    gasp = newTable("gasp")
    gasp.gaspRange = {0xFFFF: 0x000F}
    fb.font["gasp"] = gasp
    if features and not only:
        kerns = {}
        if kern:
            import kerning
            base = ([c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"]
                    + FIG_NAMES + ["germandbls", "ae", "oe", "AE", "OE", "lslash", "Lslash", "oslash", "Oslash",
                                   "period", "comma", "hyphen", "endash", "quoteright", "quotedblright", "quoteleft",
                                   "quotedblleft", "quotesinglbase", "quotedblbase", "colon", "semicolon",
                                   "parenleft", "parenright", "slash", "guillemetleft", "guillemetright",
                                   "quotesingle", "quotedbl", "ampersand", "question", "exclam"])
            kerns = kerning.compute(glyphs, [n for n in base if n in glyphs and "shape" in glyphs[n]], p)
        fea = feature_text(p, glyphs, kerns)
        Path(out_path).with_suffix(".fea").write_text(fea)
        addOpenTypeFeaturesFromString(fb.font, fea)
    fb.save(out_path)
    return glyphs


# ---------------------------------------------------------------------------
# derived glyphs: tabular figures, case punctuation, superiors
# ---------------------------------------------------------------------------

FIG_NAMES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
CASE = ["hyphen", "endash", "emdash", "parenleft", "parenright", "bracketleft", "bracketright",
        "braceleft", "braceright", "guillemetleft", "guillemetright", "guilsinglleft", "guilsinglright",
        "periodcentered", "bullet", "slash", "backslash", "colon", "at", "uni00B7"]


def add_derived(p, out):
    from figures import tab_width
    from punct import mid_y
    tw = round(tab_width(p))
    for n in FIG_NAMES + ["period", "comma", "colon", "uni2007"]:
        if n not in out or "shape" not in out[n]:
            continue
        b = out[n]["shape"].bounds()
        if n in ("period", "comma", "colon"):
            continue
        dx = (tw - (b[2] - b[0])) / 2 - b[0]
        out[n + ".tf"] = dict(components=[(n, dx, 0)], advance=tw, unis=[], anchors={})
    lift = round(CAP / 2 - mid_y())
    for n in CASE:
        if n in out:
            out[n + ".case"] = dict(components=[(n, 0, lift)], advance=out[n]["advance"], unis=[], anchors={})
    # superior figures for ¹ ² ³ and fractions: heavier drawings scaled down
    import figures as F
    q = params.P(min(1.0, p.w + 0.55))
    sc = 0.60
    for n, uni in (("one", 0xB9), ("two", 0xB2), ("three", 0xB3)):
        sh = F.FIG[n](q).shape.transform(sc, 0, 0, sc, 0, 0)
        b = sh.bounds()
        sh = sh.move(-b[0] + 30, CAP - CAP * sc)
        out[n + "superior"] = dict(shape=sh, advance=(b[2] - b[0]) + 60, unis=[uni], anchors={}, shift=0)


def feature_text(p, out, kerns):
    fea = ["languagesystem DFLT dflt;", "languagesystem latn dflt;", "languagesystem latn PLK;", ""]
    tf = [n for n in FIG_NAMES if n + ".tf" in out]
    fea.append("feature tnum {\n" + "".join(f"  sub {n} by {n}.tf;\n" for n in tf) + "} tnum;")
    fea.append("feature pnum {\n" + "".join(f"  sub {n}.tf by {n};\n" for n in tf) + "} pnum;")
    cs = [n for n in CASE if n + ".case" in out]
    fea.append("feature case {\n" + "".join(f"  sub {n} by {n}.case;\n" for n in cs) + "} case;")
    # kerning: base glyphs carry their accented forms in classes
    from accented import COMPOSITES
    groups = {}
    for name, uni, base, marks in COMPOSITES:
        if name in out:
            kinds = {k for _, k in marks}
            if kinds <= {"top", "top_asc", "bottom", "ogonek"}:
                groups.setdefault(base, []).append(name)
    used = {a for a, _ in kerns} | {b for _, b in kerns}
    for g in sorted(used):
        members = [g] + groups.get(g, [])
        fea.append(f"@K_{g.replace('.', '_')} = [{' '.join(members)}];")
    lines = [f"  pos @K_{a.replace('.', '_')} @K_{b.replace('.', '_')} {v};" for (a, b), v in sorted(kerns.items())]
    fea.append("feature kern {\n  lookupflag 0;\n" + "\n".join(lines) + "\n} kern;")
    return "\n".join(fea)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--style", default="Regular")
    ap.add_argument("--out", default=str(ROOT / "build" / "test.ttf"))
    ap.add_argument("--quick", action="store_true", help="no kerning")
    ap.add_argument("--release", action="store_true", help="all weights, hinted TTF and WOFF2")
    args = ap.parse_args()
    load_modules()
    if args.release:
        import release
        release.run()
    else:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        build_font(args.style, args.out, kern=not args.quick)
        print(args.out)
