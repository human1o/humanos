"""Lamina — diacritical marks.

Marks follow the same three rules: the dots are the same small sheets as the
dot of i, every stroke ends in a horizontal or vertical cut, and the ogonek is
the foot of t in miniature.
"""
import math

from geom import Shape, Skel, poly, rect, stroked
from params import ASC, CAP, XH
from parts import oval, squircle
from registry import G, glyph


def mix(a, b, w):
    return a + (b - a) * w


def dsize(p):
    return p.V * 1.16


def lc_base(p):
    """Bottom of lowercase marks: the bottom of the dot of i."""
    return ASC - 2 - dsize(p)


def cap_base(p):
    return CAP + mix(66, 56, p.w)


def acc_h(p, case):
    return mix(150, 160, p.w) * (0.82 if case else 1.0)


def acc_t(p):
    return p.V * mix(0.96, 0.92, p.w)


def _slant(p, y0, h, lean, t):
    """A slanted stroke with horizontal cuts, centred on x = 0.
    lean: horizontal travel of the centre line from bottom to top."""
    wh = t * math.hypot(lean, h) / h
    xb, xt = -lean / 2, lean / 2
    return poly((xb - wh / 2, y0), (xb + wh / 2, y0), (xt + wh / 2, y0 + h), (xt - wh / 2, y0 + h))


def acute_shape(p, case=False):
    y0 = cap_base(p) if case else lc_base(p)
    h = acc_h(p, case)
    return _slant(p, y0, h, h * 0.86, acc_t(p))


def grave_shape(p, case=False):
    return acute_shape(p, case).mirror_x(0)


def circumflex_shape(p, case=False, flip=False):
    y0 = cap_base(p) if case else lc_base(p)
    h = acc_h(p, case) * 0.92
    t = acc_t(p) * 0.92
    w = mix(330, 360, p.w)
    a = _slant(p, y0, h, w / 2 - t * 0.2, t).move(-w / 4 + t * 0.05)
    b = a.mirror_x(0)
    sh = (a | b) & rect(-1000, y0, 1000, y0 + h)
    if flip:
        sh = sh.mirror_y(y0 + h / 2)
    return sh


def breve_shape(p, case=False):
    y0 = cap_base(p) if case else lc_base(p)
    h = acc_h(p, case) * 0.86
    t = acc_t(p) * 0.86
    w = mix(300, 320, p.w)
    H = t * 0.84
    yb = y0 + H / 2
    r = h * 0.62
    from geom import nib
    s = Skel(-w / 2 + t / 2, y0 + h).L(-w / 2 + t / 2, yb + r).bend((-w / 2 + t / 2, yb), (0, yb))
    s.bend((w / 2 - t / 2, yb), (w / 2 - t / 2, yb + r)).L(w / 2 - t / 2, y0 + h)
    return stroked(s, nib(t, H))


def tilde_shape(p, case=False):
    y0 = cap_base(p) if case else lc_base(p)
    h = acc_h(p, case) * 0.72
    t = acc_t(p) * 0.86
    w = mix(340, 360, p.w)
    from geom import nib
    yb, yt = y0 + t * 0.45, y0 + h - t * 0.45
    s = Skel(-w / 2, yb).C((-w * 0.30, yt + 10), (-w * 0.14, yt + 4), (0, (yb + yt) / 2))
    s.C((w * 0.14, yb - 4), (w * 0.30, yb - 10), (w / 2, yt))
    return stroked(s, nib(t * 0.92, t * 0.80)) & rect(-w / 2, -1000, w / 2, 3000)


def macron_shape(p, case=False):
    y0 = cap_base(p) if case else lc_base(p)
    w = mix(300, 330, p.w)
    H = p.H
    return rect(-w / 2, y0 + 10, w / 2, y0 + 10 + H)


def dot_shape(p, case=False, x=0):
    d = dsize(p)
    y0 = cap_base(p) if case else lc_base(p)
    return squircle(x, y0 + d / 2, d, d)


def dieresis_shape(p, case=False):
    d = dsize(p)
    gap = d * 1.0 + mix(70, 64, p.w)
    return dot_shape(p, case, -gap / 2 - 0) | dot_shape(p, case, gap / 2)


def ring_shape(p, case=False):
    y0 = cap_base(p) if case else lc_base(p)
    s = mix(220, 240, p.w) * (0.92 if case else 1.0)
    t = acc_t(p) * 0.80
    from geom import nib
    if case:
        y0 = y0 - 26
    return oval(-s / 2, s / 2, y0, y0 + s, t, t * 0.9, s * 0.30, nib(t, t * 0.9))


def hungarumlaut_shape(p, case=False):
    a = acute_shape(p, case)
    gap = mix(150, 166, p.w)
    return a.move(-gap / 2) | a.move(gap / 2)


def caron_shape(p, case=False):
    return circumflex_shape(p, case, flip=True)


def cedilla_shape(p):
    t = p.V * 0.84
    H = p.H * 0.84
    from geom import nib
    s = Skel(0, 30).L(0, -46).bend((0, -46 - 0), (0, -46))
    stub = rect(-t / 2, -50, t / 2, 30)
    yb = -190 + H / 2
    r = 64
    hook = Skel(-t / 2, -50 + H / 2).L(60, -50 + H / 2).bend((120, -50 + H / 2), (120, -50 + H / 2 - r * 0.9))
    hook.bend((120, yb), (60, yb)).L(-70, yb)
    return stub | stroked(hook, nib(t, H))


def ogonek_shape(p, case=False):
    """The foot of t, in miniature."""
    t = p.V * 0.90
    H = p.H * 0.92
    from geom import nib
    yb = -mix(170, 176, p.w) + H / 2
    r = mix(80, 86, p.w)
    s = Skel(0, 40).L(0, yb + r).bend((0, yb), (r, yb)).L(r + mix(46, 40, p.w), yb)
    return stroked(s, nib(t, H))


def commabelow_shape(p):
    d = dsize(p) * 0.92
    y = -80 - d
    dot = squircle(0, y + d / 2, d, d)
    tail = poly((d * 0.46, y + d * 0.5), (-d * 0.08, y + d * 0.5), (-d * 0.56, y - 120), (-d * 0.02, y - 120))
    return dot | (tail & rect(-500, -500, d / 2, y + d * 0.5))


def commaabove_shape(p):
    """Turned comma above (ģ)."""
    sh = commabelow_shape(p)
    b = sh.bounds()
    sh = sh.rot180((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
    b = sh.bounds()
    return sh.move(0, lc_base(p) - b[1])


def caron_alt_shape(p):
    """The apostrophe-caron of ď ľ ť: a small comma beside the ascender."""
    d = dsize(p) * 0.92
    y = ASC - d
    dot = squircle(0, y + d / 2, d, d)
    tail = poly((d * 0.46, y + d * 0.5), (-d * 0.08, y + d * 0.5), (-d * 0.50, y - 110), (0, y - 110))
    return dot | (tail & rect(-500, -500, d / 2, y + d * 0.5))


MARKS = {
    # name: (combining code point, drawing, case-variant?)
    "acutecomb": (0x301, acute_shape, True),
    "gravecomb": (0x300, grave_shape, True),
    "circumflexcomb": (0x302, circumflex_shape, True),
    "caroncomb": (0x30C, caron_shape, True),
    "brevecomb": (0x306, breve_shape, True),
    "tildecomb": (0x303, tilde_shape, True),
    "macroncomb": (0x304, macron_shape, True),
    "dieresiscomb": (0x308, dieresis_shape, True),
    "dotaccentcomb": (0x307, dot_shape, True),
    "ringcomb": (0x30A, ring_shape, True),
    "hungarumlautcomb": (0x30B, hungarumlaut_shape, True),
    "cedillacomb": (0x327, lambda p, case=False: cedilla_shape(p), False),
    "ogonekcomb": (0x328, ogonek_shape, False),
    "commaaccentcomb": (0x326, lambda p, case=False: commabelow_shape(p), False),
    "commaturnedabovecomb": (0x312, lambda p, case=False: commaabove_shape(p), False),
    "caroncomb.alt": (None, lambda p, case=False: caron_alt_shape(p), False),
}

SPACING = {  # spacing accents: name -> (code point, mark)
    "acute": (0xB4, "acutecomb"), "grave": (0x60, "gravecomb"), "circumflex": (0x2C6, "circumflexcomb"),
    "caron": (0x2C7, "caroncomb"), "breve": (0x2D8, "brevecomb"), "tilde": (0x2DC, "tildecomb"),
    "macron": (0xAF, "macroncomb"), "dieresis": (0xA8, "dieresiscomb"), "dotaccent": (0x2D9, "dotaccentcomb"),
    "ring": (0x2DA, "ringcomb"), "hungarumlaut": (0x2DD, "hungarumlautcomb"), "cedilla": (0xB8, "cedillacomb"),
    "ogonek": (0x2DB, "ogonekcomb"),
}


def _register():
    for name, (uni, fn, has_case) in MARKS.items():
        def make(fn=fn):
            return lambda p: G(fn(p), advance=0)
        glyph(name, uni)(make())
        if has_case:
            def make_c(fn=fn):
                return lambda p: G(fn(p, True), advance=0)
            glyph(name + ".case")(make_c())
    for name, (uni, mark) in SPACING.items():
        fn = MARKS[mark][1]

        def make_s(fn=fn):
            def f(p):
                sh = fn(p)
                return G(sh, 40, 40)
            return f
        glyph(name, uni)(make_s())


_register()
