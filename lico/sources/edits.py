"""Lico — edits to upstream outlines: derived glyphs, alternates, composites."""
import copy

from ufoLib2.objects import Point

from shapes import K, set_anchor


def _pt(x, y, t="line", smooth=False):
    return Point(round(x), round(y), t, smooth)


def _off(x, y):
    return Point(round(x), round(y), None)


def _splice(contour, start, end, new_points):
    """Replace every point strictly between the on-curve points `start` and
    `end` (walking forward, cyclically) with `new_points`."""
    pts = list(contour.points)
    i0 = next(i for i, q in enumerate(pts) if (q.x, q.y) == start and q.type)
    pts = pts[i0:] + pts[:i0]
    i1 = next(i for i, q in enumerate(pts) if (q.x, q.y) == end and q.type and i > 0)
    contour.points = [pts[0]] + list(new_points) + pts[i1:]


def _arc(p0, corner, p1, k=K):
    """Off-curve points + on-curve end for a quarter turn p0 -> p1."""
    return [
        _off(p0[0] + (corner[0] - p0[0]) * k, p0[1] + (corner[1] - p0[1]) * k),
        _off(p1[0] + (corner[0] - p1[0]) * k, p1[1] + (corner[1] - p1[1]) * k),
        _pt(p1[0], p1[1], "curve"),
    ]


def duplicate(font, src, dst):
    g = copy.deepcopy(font[src])
    g._name = dst
    g.unicodes = []
    font.layers.defaultLayer.insertGlyph(g, dst, overwrite=True, copy=False)
    order = font.lib.get("public.glyphOrder")
    if order is not None and dst not in order:
        order.insert(order.index(src) + 1, dst)
    return font[dst]


def edit_a(font, p):
    """a — the stem lands square on the baseline; no tail."""
    g = font["a"]
    c = g.contours[0]
    if p.name == "Regular":
        _splice(c, (818, 226), (949, 688),
                [_pt(789, 252), _pt(789, 0), _pt(949, 0)])
        right = 949
    else:
        _splice(c, (847, 283), (1153, 604),
                [_pt(773, 318), _pt(773, 0), _pt(1153, 0)])
        right = 1153
    g.width = right + p.lerp(143, 104)
    set_anchor(g, "ogonek", right, 0)


def edit_J(font, p):
    """J — no top bar; the stem simply ends at cap height."""
    g = font["J"]
    c = g.contours[0]
    if p.name == "Regular":
        _splice(c, (951, 1440), (771, 407), [_pt(771, 1440)])
        set_anchor(g, "top", 861, 1440)
    else:
        _splice(c, (1187, 1440), (777, 487), [_pt(777, 1440)])
        set_anchor(g, "top", 982, 1440)


def make_g(font, p):
    """g — single-storey: the bowl of q, the stem bending left into a flat
    tail (the upstream double-storey g is kept as g.ss01)."""
    old = duplicate(font, "g", "g.ss01")
    for n in ("gbreve", "gcaron", "gcircumflex", "gcommaaccent", "gdotaccent"):
        alt = duplicate(font, n, n + ".ss01")
        for comp in alt.components:
            if comp.baseGlyph == "g":
                comp.baseGlyph = "g.ss01"
    g = font["g"]
    q = font["q"]
    anchors = {a.name: (a.x, a.y) for a in g.anchors}
    g.clearContours()
    for c in q.contours:
        g.contours.append(copy.deepcopy(c))
    g.width = q.width
    V, H = p.V, p.H
    R = p.lerp(430, 590)
    d = p.desc
    xl, xr = p.lerp((877, 1045), (824, 1224))
    join = p.lerp((877, 225), (824, 211))
    end = p.lerp(206, 150)
    rix, riy = R - V, R - H
    pts = [_pt(xl, d + H + riy)]
    pts += _arc((xl, d + H + riy), (xl, d + H), (xl - rix, d + H))
    pts += [_pt(end, d + H), _pt(end, d), _pt(xr - R, d)]
    pts += _arc((xr - R, d), (xr, d), (xr, d + R))
    c = g.contours[0]
    _splice(c, join, (xr, 1080), pts)
    g.anchors = []
    set_anchor(g, "bottom", (end + xr) / 2 + 20, -494)
    set_anchor(g, "top", p.lerp(560, 632), 1080)
    return old


# --------------------------------------------------------------------------
# kerning
# --------------------------------------------------------------------------

def _groups_of(font, name, side):
    return [k for k, v in font.groups.items()
            if k.startswith(f"public.kern{side}.") and name in v]


def _leave(font, name, side):
    for k in _groups_of(font, name, side):
        font.groups[k] = [n for n in font.groups[k] if n != name]


def _join_like(font, name, model, side):
    """Give `name` the kerning class of `model` on one side (1 = its right
    edge, 2 = its left edge), dropping its own exceptions on that side."""
    _leave(font, name, side)
    for k in _groups_of(font, model, side):
        font.groups[k] = list(font.groups[k]) + [name]
    idx = side - 1
    for pair in [q for q in font.kerning if q[idx] == name]:
        del font.kerning[pair]


def _inherit(font, alt, src):
    """`alt` takes over every class and explicit pair of `src`."""
    for k, v in font.groups.items():
        if src in v and alt not in v:
            font.groups[k] = list(v) + [alt]
    for (l, r), val in list(font.kerning.items()):
        if l == src or r == src:
            font.kerning[(alt if l == src else l, alt if r == src else r)] = val


def _prune(font):
    """Drop empty classes and any pair that points at a missing class/glyph."""
    for k in [k for k, v in font.groups.items() if k.startswith("public.kern") and not v]:
        del font.groups[k]
    for pair in list(font.kerning):
        for side in pair:
            if side.startswith("public.kern"):
                if side not in font.groups:
                    del font.kerning[pair]
                    break
            elif side not in font:
                del font.kerning[pair]
                break


G_ACCENTED = ("gbreve", "gcaron", "gcircumflex", "gcommaaccent", "gdotaccent")
A_FAMILY = ("a", "aacute", "abreve", "acaron", "acircumflex", "adieresis",
            "adotbelow", "agrave", "amacron", "aogonek", "aring", "aringacute",
            "atilde")


def rekern(font):
    # alternates keep the upstream kerning of the shapes they preserve
    _inherit(font, "I.ss03", "I")
    _inherit(font, "l.ss02", "l")
    _inherit(font, "g.ss01", "g")
    for n in G_ACCENTED:
        _inherit(font, n + ".ss01", n)
    # plain l: an ascender stem on both sides
    for n in ("l", "lacute", "lcommaaccent", "ldot", "lslash", "lcaron"):
        _join_like(font, n, "h", 2)
        if n != "lcaron":
            _join_like(font, n, "d", 1)
    _join_like(font, "l.ss02", "h", 2)
    # plain I: a capital stem on both sides
    _join_like(font, "I", "H", 1)
    _join_like(font, "I", "H", 2)
    for n in list(font.groups.get("public.kern2.I", [])):
        if n != "I.ss03":
            _join_like(font, n, "H", 2)
    # single-storey g: the sides of q
    for n in ("g",) + G_ACCENTED:
        _join_like(font, n, "q", 1)
        _join_like(font, n, "q", 2)
    # tail-less a: an x-height stem on the right
    for n in A_FAMILY:
        _join_like(font, n, "u", 1)
    _prune(font)


# --------------------------------------------------------------------------
# features, names
# --------------------------------------------------------------------------

STYLISTIC_SETS = '''
feature ss01 {
    featureNames { name "Double-storey g"; };
    sub g by g.ss01;
    sub gbreve by gbreve.ss01;
    sub gcaron by gcaron.ss01;
    sub gcircumflex by gcircumflex.ss01;
    sub gcommaaccent by gcommaaccent.ss01;
    sub gdotaccent by gdotaccent.ss01;
} ss01;

feature ss02 {
    featureNames { name "Bent l"; };
    sub l by l.ss02;
} ss02;

feature ss03 {
    featureNames { name "Serifed I"; };
    sub I by I.ss03;
} ss03;
'''


def refeature(font):
    text = font.features.text
    text = text.replace("feature zero;\n\n} aalt;",
                        "feature zero;\nfeature ss01;\nfeature ss02;\nfeature ss03;\n\n} aalt;")
    assert "feature ss01;" in text
    font.features.text = text.rstrip() + "\n" + STYLISTIC_SETS


FAMILY = "Lico"
VERSION = (1, 0)


def rename(font, style):
    i = font.info
    i.familyName = FAMILY
    i.styleName = style
    i.versionMajor, i.versionMinor = VERSION
    i.copyright = ("Copyright 2026 The Lico Project Authors. Based on Schibsted Grotesk, "
                   "Copyright 2023 The Schibsted-Grotesk Project Authors "
                   "(https://github.com/schibsted/schibsted-grotesk)")
    i.openTypeNameDesigner = ("Lico: redesign for Murelle and Lamelio. "
                              "Schibsted Grotesk: Bakken & Baeck AS, Henrik Kongsvoll")
    i.openTypeNameDesignerURL = None
    i.openTypeNameManufacturer = "Lico Project"
    i.openTypeNameManufacturerURL = None
    i.openTypeOS2VendorID = "LICO"
    i.openTypeNameDescription = ("A quiet grotesk with one gesture: every stroke that turns, "
                                 "turns through the same bend.")
    i.postscriptFontName = f"{FAMILY}-{style}"
    i.postscriptFullName = f"{FAMILY} {style}"
    i.openTypeNameUniqueID = None
    i.openTypeNameVersion = None
    for key in [k for k in font.lib if "glyphs" in k.lower() and "Axis" not in k
                and k.startswith("com.schriftgestaltung.customParameter.GSFont.")]:
        pass


# --------------------------------------------------------------------------
# composites
# --------------------------------------------------------------------------

REDRAWN = ("t", "l", "f", "jdotless", "y", "g", "a", "I", "J")
LIGATURES = {  # order matters: parts before the ligatures built from them
    "ij": "i j", "IJ": "I J", "f_f": "f f", "f_f_i": "f f i", "f_f_l": "f f l",
    "f_i": "f i", "f_l": "f l", "fi": "f i", "fl": "f l", "f_ij": "f ij",
    "f_f_ij": "f_f ij",
}


def _anchor(g, name):
    for a in g.anchors:
        if a.name == name:
            return a
    return None


def record(font):
    """Before anything moves, note how every composite of a glyph we redraw
    is put together: which anchor each mark hangs from."""
    rec = {}
    for g in font:
        if not g.components or g.name in LIGATURES or g.name.startswith("_"):
            continue
        base = g.components[0].baseGlyph
        if base not in REDRAWN:
            continue
        b = font[base]
        marks = []
        for comp in g.components[1:]:
            m = font[comp.baseGlyph]
            dx, dy = comp.transformation[4], comp.transformation[5]
            hit = None
            for ma in m.anchors:
                if not ma.name.startswith("_"):
                    continue
                ba = _anchor(b, ma.name[1:])
                if ba and abs(ba.x - ma.x - dx) <= 1 and abs(ba.y - ma.y - dy) <= 1:
                    hit = ma.name[1:]
                    break
            marks.append((comp.baseGlyph, hit, dx, dy))
        rec[g.name] = dict(
            base=base, marks=marks, extra=g.width - b.width, base_width=b.width,
            base_anchors={a.name: (a.x, a.y) for a in b.anchors})
    return rec


def reattach(font, rec):
    for name, r in rec.items():
        g, b = font[name], font[r["base"]]
        g.width = b.width + r["extra"]
        new = {a.name: (a.x, a.y) for a in b.anchors}
        old = r["base_anchors"]
        for comp, (mark, anchor, dx, dy) in zip(g.components[1:], r["marks"]):
            if anchor and anchor in new:
                ma = _anchor(font[mark], "_" + anchor)
                dx, dy = new[anchor][0] - ma.x, new[anchor][1] - ma.y
            else:  # free-standing part: follow the base's right edge
                dx += b.width - r["base_width"]
            t = list(comp.transformation)
            t[4], t[5] = dx, dy
            comp.transformation = tuple(t)
        for a in g.anchors:
            key = a.name if a.name in old and a.name in new else (
                "top" if "top" in old and "top" in new else None)
            if key:
                a.x += new[key][0] - old[key][0]
                if a.name in new:
                    a.y += new[key][1] - old[key][1]


def record_ligatures(font):
    """Upstream tucks some parts together (ij, IJ); remember by how much."""
    rec = {}
    for name, parts in LIGATURES.items():
        g = font[name]
        parts = parts.split()
        assert [c.baseGlyph for c in g.components] == parts, (name, parts)
        x, tucks = 0, []
        for comp, part in zip(g.components, parts):
            tucks.append(comp.transformation[4] - x)
            x += font[part].width
        rec[name] = tucks
    return rec


def religate(font, rec):
    """Ligatures and digraphs are their parts set side by side."""
    for name, parts in LIGATURES.items():
        g = font[name]
        x, starts = 0, []
        for comp, part, tuck in zip(g.components, parts.split(), rec[name]):
            t = list(comp.transformation)
            starts.append((t[4], x + tuck))
            t[4] = x + tuck
            comp.transformation = tuple(t)
            x = x + tuck + font[part].width
        g.width = x
        for a in g.anchors:
            # an anchor (or caret) belongs to the part it sat over
            k = max(i for i, (o, _) in enumerate(starts) if o <= a.x or i == 0)
            a.x += starts[k][1] - starts[k][0]


ROMAN = {
    "One-roman": "I", "Two-roman": "II", "Three-roman": "III", "Four-roman": "IV",
    "Five-roman": "V", "Six-roman": "VI", "Seven-roman": "VII", "Eight-roman": "VIII",
    "Nine-roman": "IX", "Ten-roman": "X", "Eleven-roman": "XI", "Twelve-roman": "XII",
    "Fifty-roman": "L", "Hundred-roman": "C", "Fivehundred-roman": "D",
    "Thousand-roman": "M",
}


def romanize(font):
    """Roman numerals are set from the family's own capitals (upstream ships
    them in a serif style)."""
    from ufoLib2.objects import Component
    for name, letters in ROMAN.items():
        g = font[name]
        g.clearContours()
        g.components.clear()
        g.anchors = []
        x = 0
        for ch in letters:
            g.components.append(Component(ch, (1, 0, 0, 1, x, 0)))
            x += font[ch].width
        g.width = x


def remove_glyph(font, name):
    del font[name]
    order = font.lib.get("public.glyphOrder")
    if order and name in order:
        order.remove(name)
    for k, v in font.groups.items():
        if name in v:
            font.groups[k] = [n for n in v if n != name]


def pre(font, p):
    rec = (record(font), record_ligatures(font))
    duplicate(font, "I", "I.ss03")
    duplicate(font, "l", "l.ss02")
    make_g(font, p)
    edit_a(font, p)
    edit_J(font, p)
    return rec


def post(font, p, rec):
    reattach(font, rec[0])
    romanize(font)
    remove_glyph(font, "version")
    religate(font, rec[1])
    rekern(font)
    refeature(font)
    rename(font, p.name)
