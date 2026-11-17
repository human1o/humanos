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
FLANK_VERTICAL = 1.36     # handle at the vertical end of a quarter curve
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


def _is_dot(contour):
    pts = contour.points
    if len(pts) != 4 or any(p.type != "line" for p in pts):
        return None
    xs = sorted({round(p.x, 1) for p in pts})
    ys = sorted({round(p.y, 1) for p in pts})
    if len(xs) != 2 or len(ys) != 2:
        return None
    w, h = xs[1] - xs[0], ys[1] - ys[0]
    if not (50 <= w <= 200 and 50 <= h <= 200 and 0.72 <= w / h <= 1.38):
        return None
    return xs[0], ys[0], xs[1], ys[1]


def _area(pts):
    a = 0
    for i in range(len(pts)):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[i]
        a += x0 * y1 - x1 * y0
    return a / 2


DOT_GLYPHS = {"i", "j", "period", "period.ss02", "exclam", "exclamdown", "question", "questiondown",
              "dotaccentcomb", "dotaccentcomb.case", "dieresiscomb", "dieresiscomb.case", "divide"}


def tile(glyph, without):
    if "tile" in without or glyph.name not in DOT_GLYPHS:
        return 0
    n = 0
    for c in glyph.contours:
        box = _is_dot(c)
        if not box:
            continue
        x0, y0, x1, y1 = box
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        k = TILE_K
        top, right, bot, left = (cx, y1), (x1, cy), (cx, y0), (x0, cy)

        def q(a, corner, b):
            return [Point(a[0] + (corner[0] - a[0]) * k, a[1] + (corner[1] - a[1]) * k),
                    Point(b[0] + (corner[0] - b[0]) * k, b[1] + (corner[1] - b[1]) * k),
                    Point(b[0], b[1], "curve", True)]
        # clockwise (TrueType/PostScript outer direction in UFO is counter-clockwise;
        # keep whatever the original used)
        cw = _area([(p.x, p.y) for p in c.points]) < 0
        if cw:
            new = [Point(top[0], top[1], "curve", True)] + q(top, (x1, y1), right)[:] + q(right, (x1, y0), bot) + q(bot, (x0, y0), left) + q(left, (x0, y1), top)[:-1]
        else:
            new = [Point(top[0], top[1], "curve", True)] + q(top, (x0, y1), left) + q(left, (x0, y0), bot) + q(bot, (x1, y0), right) + q(right, (x1, y1), top)[:-1]
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
    i.copyright = ("Copyright 2026 The Lamina Project Authors. Based on Zalando Sans, "
                   "Copyright 2025 The Zalando Sans Project Authors (https://github.com/zalando/sans)")
    i.trademark = None
    i.openTypeNameDesigner = "Lamina: Murèlle & Lamelio. Zalando Sans: Jakob Ekelund, KH Type, Zalando"
    i.openTypeNameDesignerURL = None
    i.openTypeNameManufacturer = "Lamina Project"
    i.openTypeNameManufacturerURL = None
    i.openTypeNameDescription = ("A slender grotesk on the rhythm of the lamella: bowls stand on "
                                 "straight flanks, dots are small tiles of stone.")
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
    """Tabular figures change only the figures. Upstream also swaps the word
    space for a figure-wide space, which spreads every word apart in a table
    set with tabular-nums."""
    t = font.features.text
    for line in ("sub space by space.tf;\n", "sub space.tf by space;\n"):
        assert line in t, line
        t = t.replace(line, "")
    font.features.text = t


def apply(font, style, italic=False, without=()):
    features(font)
    stats = {"flank": 0, "tile": 0}
    for g in font:
        stats["flank"] += flank(g, without)
        stats["tile"] += tile(g, without)
    rename(font, style, italic)
    font.lib["lamina.stats"] = stats
    return stats
