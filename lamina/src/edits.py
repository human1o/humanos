"""Lamina 2 — the edits applied to both masters.

Every edit is a rule, applied the same way to every glyph and to both
masters, so the two masters stay point-compatible and the weights in between
inherit the idea.
"""
import math

from ufoLib2.objects import Point

# --- the flank -----------------------------------------------------------------
# Where a curve becomes vertical, its handles are lengthened (measured as a
# fraction of the leg to the corner where the two tangents meet). Bowls then
# stand on straighter sides: a sheet of stone wrapped around a column.
FLANK_VERTICAL = 1.14     # handle at the vertical end of a quarter curve
FLANK_HORIZONTAL = 1.03   # handle at the horizontal end
FLANK_MAX = 0.88          # never longer than this share of the leg


def _quarter_segments(contour):
    """Yield (i0, i1, i2, i3) point indices of every cubic segment."""
    pts = contour.points
    n = len(pts)
    on = [i for i, p in enumerate(pts) if p.type is not None]
    for k, i3 in enumerate(on):
        if pts[i3].type != "curve":
            continue
        i0 = on[k - 1]
        i1, i2 = (i0 + 1) % n, (i0 + 2) % n
        if (i2 + 1) % n != i3 or pts[i1].type is not None or pts[i2].type is not None:
            continue
        yield i0, i1, i2, i3


def flank(glyph, without):
    if "flank" in without:
        return 0
    changed = 0
    for c in glyph.contours:
        pts = c.points
        for i0, i1, i2, i3 in _quarter_segments(c):
            p0, p1, p2, p3 = pts[i0], pts[i1], pts[i2], pts[i3]
            v0 = abs(p1.x - p0.x) < 0.75 and abs(p1.y - p0.y) > 1     # vertical at p0
            h0 = abs(p1.y - p0.y) < 0.75 and abs(p1.x - p0.x) > 1     # horizontal at p0
            v3 = abs(p2.x - p3.x) < 0.75 and abs(p2.y - p3.y) > 1
            h3 = abs(p2.y - p3.y) < 0.75 and abs(p2.x - p3.x) > 1
            if v0 and h3:
                corner = (p0.x, p3.y)
                _stretch(p0, p1, corner, FLANK_VERTICAL)
                _stretch(p3, p2, corner, FLANK_HORIZONTAL)
                changed += 1
            elif h0 and v3:
                corner = (p3.x, p0.y)
                _stretch(p0, p1, corner, FLANK_HORIZONTAL)
                _stretch(p3, p2, corner, FLANK_VERTICAL)
                changed += 1
    return changed


def _stretch(on, off, corner, factor):
    leg = math.hypot(corner[0] - on.x, corner[1] - on.y)
    if leg < 1:
        return
    cur = math.hypot(off.x - on.x, off.y - on.y)
    frac = cur / leg
    new = min(frac * factor, max(frac, FLANK_MAX))
    s = new / frac if frac else 1
    off.x = on.x + (off.x - on.x) * s
    off.y = on.y + (off.y - on.y) * s


# --- the tile ----------------------------------------------------------------------
# Upstream dots are sharp squares. Lamina's dot is a small tile of stone with
# bent corners: the same corner law as the bowls, at the scale of a dot.
TILE_K = 0.70


def _shear(font):
    """Horizontal shift per unit of height for italic masters."""
    a = font.info.italicAngle or 0
    return math.tan(math.radians(-a))


def _is_dot(contour, shear=0.0):
    pts = contour.points
    if len(pts) != 4 or any(p.type != "line" for p in pts):
        return None
    un = [(p.x - p.y * shear, p.y) for p in pts]
    xs = sorted({round(x, 0) for x, _ in un})
    ys = sorted({round(y, 0) for _, y in un})
    if len(xs) != 2 or len(ys) != 2:
        return None
    w, h = xs[1] - xs[0], ys[1] - ys[0]
    if not (50 <= w <= 260 and 50 <= h <= 260 and 0.72 <= w / h <= 1.38):
        return None
    return xs[0], ys[0], xs[1], ys[1]


def dot_candidates(font):
    """(glyph, contour index) pairs that are dots in this master."""
    sh = _shear(font)
    out = set()
    for name in DOT_GLYPHS:
        if name in font:
            for i, c in enumerate(font[name].contours):
                if _is_dot(c, sh):
                    out.add((name, i))
    return out


def _area(pts):
    a = 0
    for i in range(len(pts)):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[i]
        a += x0 * y1 - x1 * y0
    return a / 2


DOT_GLYPHS = {"period", "colon", "semicolon", "ellipsis", "exclam", "exclamdown", "question", "questiondown",
              "periodcentered", "dotaccent", "dotaccentcomb", "dotaccentcomb.case", "dotbelowcomb",
              "dieresiscomb", "dieresiscomb.case", "dieresistonos", "divide", "twodotenleader", "bullet"}


def tile(glyph, without, allowed=None, shear=0.0):
    if "tile" in without or glyph.name not in DOT_GLYPHS:
        return 0
    n = 0
    for idx, c in enumerate(glyph.contours):
        if allowed is not None and (glyph.name, idx) not in allowed:
            continue
        box = _is_dot(c, shear)
        if not box:
            continue
        x0, y0, x1, y1 = box
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        k = TILE_K
        top, right, bot, left = (cx, y1), (x1, cy), (cx, y0), (x0, cy)

        def P(x, y, t=None):
            return Point(x + y * shear, y, t, t is not None)

        def q(a, corner, b):
            return [P(a[0] + (corner[0] - a[0]) * k, a[1] + (corner[1] - a[1]) * k),
                    P(b[0] + (corner[0] - b[0]) * k, b[1] + (corner[1] - b[1]) * k),
                    P(b[0], b[1], "curve")]
        cw = _area([(p.x, p.y) for p in c.points]) < 0
        if cw:
            new = [P(*top, "curve")] + q(top, (x1, y1), right) + q(right, (x1, y0), bot) + q(bot, (x0, y0), left) + q(left, (x0, y1), top)[:-1]
        else:
            new = [P(*top, "curve")] + q(top, (x0, y1), left) + q(left, (x0, y0), bot) + q(bot, (x1, y0), right) + q(right, (x1, y1), top)[:-1]
        c.points = new
        n += 1
    return n


# --- names -----------------------------------------------------------------------

def rename(font, style, italic):
    from build import FAMILY, VERSION
    i = font.info
    sty = style if not italic else ("Italic" if style == "Regular" else f"{style} Italic")
    i.familyName = FAMILY
    i.styleName = sty
    i.styleMapFamilyName = FAMILY
    i.styleMapStyleName = {"Regular": "regular", "Bold": "bold", "Italic": "italic", "Bold Italic": "bold italic"}.get(sty, "regular")
    i.versionMajor, i.versionMinor = VERSION
    i.copyright = ("Copyright 2026 The Lamina Project Authors. Based on Hanken Grotesk, "
                   "Copyright 2021 The Hanken Grotesk Project Authors (https://github.com/marcologous/hanken-grotesk)")
    i.trademark = None
    i.openTypeNameDesigner = "Lamina: Murèlle & Lamelio. Hanken Grotesk: Alfredo Marco Pradil, Hanken Design Co."
    i.openTypeNameDesignerURL = None
    i.openTypeNameManufacturer = "Lamina Project"
    i.openTypeNameManufacturerURL = None
    i.openTypeNameDescription = ("A warm, precise grotesk for Murèlle and Lamelio, set close like "
                                 "a wall of lamellae; its dots are small tiles of stone.")
    i.openTypeNameLicense = ("This Font Software is licensed under the SIL Open Font License, Version 1.1. "
                             "This license is available with a FAQ at: https://openfontlicense.org")
    i.openTypeNameLicenseURL = "https://openfontlicense.org"
    i.openTypeOS2VendorID = "LMNA"
    i.openTypeNameUniqueID = None
    i.openTypeNameVersion = None
    i.openTypeNamePreferredFamilyName = None
    i.openTypeNamePreferredSubfamilyName = None
    i.postscriptFontName = f"{FAMILY}-{sty.replace(' ', '')}"
    i.postscriptFullName = f"{FAMILY} {sty}"
    # drop upstream naming leftovers stored in the lib
    for k in [k for k in font.lib if "name" in k.lower() and "glyph" not in k.lower()]:
        del font.lib[k]


def features(font):
    """Text ligatures only. Upstream turns '->' and '<-' into arrows by
    default, which rewrites what partners type into forms; those move to the
    optional dlig feature."""
    t = font.features.text
    for pair in ("sub hyphen greater by hyphen_greater.liga;\n", "sub less hyphen by less_hyphen.liga;\n"):
        if pair in t:
            t = t.replace(pair, "")
            t += "\nfeature dlig {\n" + pair + "} dlig;\n"
    font.features.text = t


# --- spacing ---------------------------------------------------------------------------
# Lowercase and figures are set a little closer, measured against ABC Diatype:
# its lowercase alphabet runs 4.7 % shorter for the same cap height.
TIGHTEN = {"lower": 12, "figure": 14}


def _category(name, font):
    import unicodedata
    g = font[name]
    base = name.split(".")[0]
    cps = list(g.unicodes)
    if not cps and base in font:
        cps = list(font[base].unicodes)
    if not cps and "_" in base:                   # ligatures like f_f_i
        parts = base.split("_")
        if all(p in font and font[p].unicodes and unicodedata.category(chr(font[p].unicodes[0])) == "Ll" for p in parts):
            return "lower"
    for cp in cps:
        cat = unicodedata.category(chr(cp))
        if cat == "Ll":
            return "lower"
        if cat == "Nd":
            return "figure"
    if base in ("fi", "fl", "dotlessi", "dotlessj", "idotless", "jdotless"):
        return "lower"
    return None


def _decompose(font, name):
    from fontTools.pens.recordingPen import DecomposingRecordingPen
    from fontTools.pens.pointPen import SegmentToPointPen
    g = font[name]
    if not g.components:
        return
    rec = DecomposingRecordingPen(font)
    g.draw(rec)
    g.clearContours()
    g.clearComponents()
    rec.replay(g.getPen())


def tighten(font, without):
    if "space" in without:
        return 0
    cats = {n: _category(n, font) for n in font.keys()}
    targets = {n for n, c in cats.items() if c}
    # anything built from a target is drawn out first, so moving the target
    # cannot drag an accent or a ligature part out of place
    for g in list(font):
        if g.components and (g.name in targets or any(c.baseGlyph in targets for c in g.components)):
            _decompose(font, g.name)
    n = 0
    for name in targets:
        g = font[name]
        if g.width <= 0:
            continue
        d = TIGHTEN[cats[name]]
        g.move((-d, 0))
        for a in g.anchors:
            a.x += 0          # anchors move with g.move
        g.width = max(0, g.width - 2 * d)
        n += 1
    return n


def apply(font, style, italic=False, without=(), dots=None):
    features(font)
    stats = {"flank": 0, "tile": 0}
    sh = _shear(font)
    for g in font:
        stats["flank"] += flank(g, without)
        stats["tile"] += tile(g, without, dots, sh)
    stats["tight"] = tighten(font, without)
    rename(font, style, italic)
    font.lib["lamina.stats"] = stats
    return stats
