"""Lamina 4 — the edits applied to both masters.

Every edit is a rule, applied the same way to every glyph and to both
masters, so the two masters stay point-compatible and the weights in between
inherit the idea.
"""
import math

from ufoLib2.objects import Point

# --- the forms ---------------------------------------------------------------------
# Instrument Sans ships alternates; two of them are closer to the idea and to
# Diatype, so they become the default: the R whose leg leaves the bowl and
# drops almost straight (ss05), and $ ¢ with the stroke drawn through (ss12).
# The names are swapped everywhere (outlines, components, kerning groups,
# features), so every accented R follows and kerning stays with its shape.
FORMS = ("ss05", "ss09", "ss12")
DROP_FEATURES = ("ss01", "ss05", "ss09", "ss12")   # ss01 = round dots, against the tile

# Q: Instrument's alternate tail (ss09) crosses the bowl but runs long and
# steep. Lamina's tail is the one measured on Diatype: it starts inside the
# counter, at 59 % of the bowl's width and 30 % of the cap height, and ends
# under the bowl's right flank, just below the baseline.
Q_START = (0.59, 0.30)
Q_END = (0.875, -0.05)


def q_tail(font, without):
    if "forms" in without or "Q.ss09" not in font:
        return 0
    g = font["Q.ss09"]
    sh = _shear(font)
    tails = [c for c in g.contours if len(c.points) == 4 and all(p.type == "line" for p in c.points)]
    bowls = [c for c in g.contours if c not in tails]
    if len(tails) != 1 or not bowls:
        return 0
    xs = [p.x - p.y * sh for c in bowls for p in c.points]
    x0, x1 = min(xs), max(xs)
    cap = font.info.capHeight
    pts = tails[0].points
    tw = math.hypot(pts[2].x - pts[1].x, pts[2].y - pts[1].y)
    S = (x0 + Q_START[0] * (x1 - x0), Q_START[1] * cap)
    E = (x0 + Q_END[0] * (x1 - x0), Q_END[1] * cap)
    L = math.hypot(E[0] - S[0], E[1] - S[1])
    d = ((E[0] - S[0]) / L, (E[1] - S[1]) / L)
    n = (-d[1], d[0]) if d[0] * 0 - d[1] > 0 else (d[1], -d[0])
    if n[0] < 0:
        n = (-n[0], -n[1])
    h = tw / 2
    new = [(S[0] - n[0] * h, S[1] - n[1] * h), (E[0] - n[0] * h, E[1] - n[1] * h),
           (E[0] + n[0] * h, E[1] + n[1] * h), (S[0] + n[0] * h, S[1] + n[1] * h)]
    for p, (x, y) in zip(pts, new):
        p.x, p.y = x + y * sh, y
    return 1


DIGITS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")


def _swap_pairs(font):
    # figures: the tabular drawing becomes the default, so prices and tables
    # line up with no CSS; proportional figures stay behind pnum
    pairs = [(d, d + ".tf") for d in DIGITS if d in font and d + ".tf" in font]
    for name in font.keys():
        parts = name.split(".")
        for ss in FORMS:
            if ss in parts[1:]:
                base = ".".join(p for p in parts if p != ss)
                if base in font:
                    pairs.append((base, name))
    return pairs


def forms(font, without):
    import re
    if "forms" in without:
        return 0
    pairs = _swap_pairs(font)
    m = {}
    for a, b in pairs:
        m[a], m[b] = b, a
    # outlines: each glyph keeps its unicodes, takes its partner's drawing
    snap = {}
    for a, b in pairs:
        for n in (a, b):
            g = font[n]
            snap[n] = ([c for c in g.contours], [c for c in g.components],
                       [x for x in g.anchors], g.width)
    for a, b in pairs:
        for n, o in ((a, b), (b, a)):
            g = font[n]
            cs, comps, anch, w = snap[o]
            g.clearContours(); g.clearComponents(); g.clearAnchors()
            for c in cs: g.contours.append(c)
            for c in comps: g.components.append(c)
            for x in anch: g.anchors.append(x)
            g.width = w
    for g in font:
        for c in g.components:
            if c.baseGlyph in m:
                c.baseGlyph = m[c.baseGlyph]
    for k, v in list(font.groups.items()):
        font.groups[k] = [m.get(n, n) for n in v]
    for (l, r), v in list(font.kerning.items()):
        nl, nr = m.get(l, l), m.get(r, r)
        if (nl, nr) != (l, r):
            del font.kerning[(l, r)]
            font.kerning[(nl, nr)] = v
    t = font.features.text
    for ss in DROP_FEATURES:
        t = re.sub(r"feature %s \{.*?\} %s;\n?" % (ss, ss), "", t, flags=re.S)
        t = re.sub(r"^\s*feature %s;\n" % ss, "", t, flags=re.M)
    if m:
        pat = re.compile(r"(?<![\w.@])(%s)(?![\w.])" % "|".join(re.escape(n) for n in sorted(m, key=len, reverse=True)))
        t = pat.sub(lambda x: m[x.group(1)], t)
    font.features.text = t
    return len(pairs)


# --- the tile ----------------------------------------------------------------------
# Instrument's dots are sharp squares. Lamina's dot is a small tile of stone with
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
    i.copyright = ("Copyright 2026 The Lamina Project Authors. Based on Instrument Sans, "
                   "Copyright 2022 The Instrument Sans Project Authors (https://github.com/Instrument/instrument-sans)")
    i.trademark = None
    i.openTypeNameDesigner = "Lamina: Murèlle & Lamelio. Instrument Sans: Rodrigo Fuenzalida, Jordan Egstad"
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
    """Text ligatures only. Upstream turns '->', '<-' and 'www' into single
    glyphs by default, which rewrites what partners type into forms and
    addresses; those move to the optional dlig feature."""
    t = font.features.text
    for pair in ("sub hyphen greater by hyphen_greater.liga;\n", "sub less hyphen by less_hyphen.liga;\n",
                 "sub w w w by w_w_w.liga;\n"):
        if pair in t:
            t = t.replace(pair, "")
            t += "\nfeature dlig {\n" + pair + "} dlig;\n"
    font.features.text = t


# --- spacing ---------------------------------------------------------------------------
# Lowercase is set a little closer, measured against ABC Diatype: at width 97
# its lowercase alphabet runs about 4 % shorter for the same cap height.
# Figures already match and stay as drawn.
TIGHTEN = {"lower": 9, "figure": 0}


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
        if not d:
            continue
        g.move((-d, 0))
        for a in g.anchors:
            a.x += 0          # anchors move with g.move
        g.width = max(0, g.width - 2 * d)
        n += 1
    return n


def apply(font, style, italic=False, without=(), dots=None):
    features(font)
    q_tail(font, without)
    stats = {"forms": forms(font, without), "tile": 0}
    sh = _shear(font)
    for g in font:
        stats["tile"] += tile(g, without, dots, sh)
    stats["tight"] = tighten(font, without)
    rename(font, style, italic)
    font.lib["lamina.stats"] = stats
    return stats
