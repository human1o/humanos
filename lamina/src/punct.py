"""Lamina — punctuation, symbols, currency, arrows."""
import math

from geom import Shape, Skel, poly, rect, stroked
from params import ASC, CAP, DESC, OS, OSC, XH
from parts import diag, oval, squircle
from registry import G, glyph


def mix(a, b, w):
    return a + (b - a) * w


def dsize(p):
    """Size of every dot: period, colon, i, ü, ż."""
    return p.V * 1.16


def pdot(p, cx, y0):
    d = dsize(p)
    return squircle(cx, y0 + d / 2, d, d)


def mid_y():
    return XH * 0.50 + 14   # optical centre of the lowercase: hyphen, math


def fig_mid():
    return CAP * 0.5        # centre of figures and capitals


# --- dots -------------------------------------------------------------------------

@glyph("period", 0x2E)
def period(p):
    return G(pdot(p, 0, 0), 46, 46)


def comma_shape(p, x=0, y=0):
    d = dsize(p)
    cx = x
    dot = squircle(cx, y + d / 2, d, d)
    tail = poly((cx + d * 0.50, y + d * 0.5), (cx - d * 0.08, y + d * 0.5),
                (cx - d * 0.62, y - mix(150, 160, p.w)), (cx - d * 0.04, y - mix(150, 160, p.w)))
    return dot | (tail & rect(-500, -500, cx + d / 2, y + d * 0.5))


@glyph("comma", 0x2C)
def comma(p):
    return G(comma_shape(p), 46, 46)


@glyph("colon", 0x3A)
def colon(p):
    d = dsize(p)
    return G(pdot(p, 0, 0) | pdot(p, 0, XH - d), 52, 52)


@glyph("semicolon", 0x3B)
def semicolon(p):
    d = dsize(p)
    return G(comma_shape(p) | pdot(p, 0, XH - d), 52, 52)


@glyph("ellipsis", 0x2026)
def ellipsis(p):
    d = dsize(p)
    gap = d * 1.9
    return G(pdot(p, 0, 0) | pdot(p, gap, 0) | pdot(p, 2 * gap, 0), 50, 50)


@glyph("periodcentered", 0xB7)
def periodcentered(p):
    d = dsize(p)
    return G(pdot(p, 0, mid_y() - d / 2), 46, 46)


@glyph("bullet", 0x2022)
def bullet(p):
    d = dsize(p) * 1.9
    return G(squircle(0, mid_y(), d, d), 60, 60)


@glyph("exclam", 0x21)
def exclam(p):
    d = dsize(p)
    V = p.VC * 0.98
    return G(rect(-V / 2, d + 120, V / 2, CAP) | pdot(p, 0, 0), 64, 64)


@glyph("exclamdown", 0xA1)
def exclamdown(p):
    return G(exclam(p).shape.rot180(0, CAP / 2).move(0, XH - CAP), 64, 64)


def question_shape(p):
    V, H = p.VC * 0.96, p.HC
    d = dsize(p)
    W = mix(380, 420, p.w)
    xl, xr = V / 2, W - V / 2
    xc = W / 2
    yt = CAP + OSC - H / 2
    r = mix(150, 156, p.w)
    stem_x = xc - 4
    s = Skel(xl, CAP - 196 - 30)
    s.bend((xl, yt), (xc, yt), k=0.62).bend((xr, yt), (xr, yt - r))
    s.L(xr, CAP * 0.66).bend((xr, CAP * 0.46), (stem_x + 60, CAP * 0.46 - 10), k=0.55, k2=0.5)
    s.bend((stem_x, CAP * 0.44), (stem_x, CAP * 0.36), k=0.6)
    s.L(stem_x, d + 120)
    from geom import nib
    sh = stroked(s, nib(V, H)) - rect(-100, CAP - 196 - 60, xl + 1.2 * V, CAP - 196)
    return sh | pdot(p, stem_x, 0)


@glyph("question", 0x3F)
def question(p):
    return G(question_shape(p), 34, 40)


@glyph("questiondown", 0xBF)
def questiondown(p):
    sh = question_shape(p)
    b = sh.bounds()
    return G(sh.rot180((b[0] + b[2]) / 2, CAP / 2).move(0, XH - CAP), 40, 34)


# --- quotes ---------------------------------------------------------------------------

def quote_low(p):
    return comma_shape(p)


def quote_high(p):
    return comma_shape(p, 0, CAP - dsize(p))


@glyph("quoteright", 0x2019)
def quoteright(p):
    return G(quote_high(p), 48, 48)


@glyph("quoteleft", 0x2018)
def quoteleft(p):
    sh = quote_high(p)
    b = sh.bounds()
    return G(sh.rot180((b[0] + b[2]) / 2, (b[1] + b[3]) / 2), 48, 48)


@glyph("quotesinglbase", 0x201A)
def quotesinglbase(p):
    return G(quote_low(p), 48, 48)


def _pair(sh, gap):
    return sh | sh.move(gap)


@glyph("quotedblright", 0x201D)
def quotedblright(p):
    return G(_pair(quote_high(p), dsize(p) * 1.62), 48, 48)


@glyph("quotedblleft", 0x201C)
def quotedblleft(p):
    return G(_pair(quoteleft(p).shape, dsize(p) * 1.62), 48, 48)


@glyph("quotedblbase", 0x201E)
def quotedblbase(p):
    return G(_pair(quote_low(p), dsize(p) * 1.62), 48, 48)


@glyph("quotesingle", 0x27)
def quotesingle(p):
    V = p.V * 1.02
    return G(rect(0, CAP - 230, V, CAP), 56, 56)


@glyph("quotedbl", 0x22)
def quotedbl(p):
    V = p.V * 1.02
    gap = V * 1.9
    return G(rect(0, CAP - 230, V, CAP) | rect(gap, CAP - 230, gap + V, CAP), 56, 56)


def chevron(p, w, h, cy, t, flat):
    """A '<' made of two diagonals meeting at a vertical flat cut."""
    x_tip = 0
    top = poly((x_tip, cy + flat / 2), (x_tip, cy - flat / 2 + 0), (w, cy + h / 2 - 0), (w, cy + h / 2))
    up = _bar(x_tip, cy, w, cy + h / 2, t)
    dn = _bar(x_tip, cy, w, cy - h / 2, t)
    sh = (up | dn) & rect(x_tip, cy - h / 2 - 300, w, cy + h / 2 + 300)
    sh = sh & poly((x_tip, cy), (w, cy + h / 2 + t), (w, cy - h / 2 - t))
    return sh & rect(-1000, cy - h / 2 - t * 2, w, cy + h / 2 + t * 2)


def _bar(x0, y0, x1, y1, t):
    """A straight bar between two points, thickness t, square ends."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * t / 2, dx / L * t / 2
    ex, ey = dx / L * t, dy / L * t
    return poly((x0 - nx - ex, y0 - ny - ey), (x1 - nx + ex, y1 - ny + ey), (x1 + nx + ex, y1 + ny + ey), (x0 + nx - ex, y0 + ny - ey))


def angle(p, w, h, cy, t, right=False):
    """'<': two strokes from a tip; the tip is cut vertically, the open ends
    too, so no edge of the sign is oblique to the page."""
    sh = _bar(0, cy, w, cy + h / 2, t) | _bar(0, cy, w, cy - h / 2, t)
    sh = sh & rect(-t * 0.18, -2000, w, 4000)
    if right:
        b = sh.bounds()
        sh = sh.mirror_x((b[0] + b[2]) / 2)
    return sh


@glyph("guilsinglleft", 0x2039)
def guilsinglleft(p):
    return G(angle(p, mix(206, 220, p.w), mix(300, 320, p.w), mid_y(), p.V * 0.90), 40, 40)


@glyph("guilsinglright", 0x203A)
def guilsinglright(p):
    return G(angle(p, mix(206, 220, p.w), mix(300, 320, p.w), mid_y(), p.V * 0.90, right=True), 40, 40)


@glyph("guillemetleft", 0xAB)
def guillemetleft(p):
    a = angle(p, mix(206, 220, p.w), mix(300, 320, p.w), mid_y(), p.V * 0.90)
    return G(a | a.move(mix(176, 196, p.w)), 40, 40)


@glyph("guillemetright", 0xBB)
def guillemetright(p):
    a = angle(p, mix(206, 220, p.w), mix(300, 320, p.w), mid_y(), p.V * 0.90, right=True)
    return G(a | a.move(mix(176, 196, p.w)), 40, 40)


# --- dashes and brackets ------------------------------------------------------------------

def dash_t(p):
    return p.H * 1.08


@glyph("hyphen", 0x2D, aliases=(0x2010, 0x2011))
def hyphen(p):
    t = dash_t(p)
    return G(rect(0, mid_y() - t / 2, mix(230, 250, p.w), mid_y() + t / 2), 40, 40)


@glyph("endash", 0x2013)
def endash(p):
    t = dash_t(p)
    return G(rect(0, mid_y() - t / 2, 500, mid_y() + t / 2), 30, 30)


@glyph("emdash", 0x2014)
def emdash(p):
    t = dash_t(p)
    return G(rect(0, mid_y() - t / 2, 940, mid_y() + t / 2), 30, 30)


@glyph("underscore", 0x5F)
def underscore(p):
    t = dash_t(p)
    return G(rect(0, -150 - t, 500, -150), 10, 10)


PAREN_TOP, PAREN_BOT = CAP + 140, DESC + 30


@glyph("parenleft", 0x28)
def parenleft(p):
    V, H = p.V * 1.0, p.H
    w = mix(150, 170, p.w)
    r = 250
    x0 = V / 2
    yt, yb = PAREN_TOP - H / 2, PAREN_BOT + H / 2
    s = Skel(x0 + w, yt).bend((x0, yt), (x0, yt - r), k=0.5, k2=0.62).L(x0, yb + r)
    s.bend((x0, yb), (x0 + w, yb), k=0.62, k2=0.5)
    from geom import nib
    return G(stroked(s, nib(V, H)), 50, 24)


@glyph("parenright", 0x29)
def parenright(p):
    sh = parenleft(p).shape
    b = sh.bounds()
    return G(sh.mirror_x((b[0] + b[2]) / 2), 24, 50)


@glyph("bracketleft", 0x5B)
def bracketleft(p):
    V, H = p.V, p.H
    w = mix(170, 190, p.w)
    return G(rect(0, PAREN_BOT, V, PAREN_TOP) | rect(0, PAREN_TOP - H, w, PAREN_TOP) | rect(0, PAREN_BOT, w, PAREN_BOT + H), 60, 24)


@glyph("bracketright", 0x5D)
def bracketright(p):
    sh = bracketleft(p).shape
    b = sh.bounds()
    return G(sh.mirror_x((b[0] + b[2]) / 2), 24, 60)


@glyph("braceleft", 0x7B)
def braceleft(p):
    V, H = p.V, p.H
    from geom import nib
    n = nib(V, H)
    xm = mix(110, 124, p.w)
    w = xm + mix(110, 120, p.w)
    mid = (PAREN_TOP + PAREN_BOT) / 2
    yt, yb = PAREN_TOP - H / 2, PAREN_BOT + H / 2
    r = 110
    s1 = Skel(w, yt).bend((xm, yt), (xm, yt - r)).L(xm, mid + r).bend((xm, mid), (0, mid), k=0.55)
    s2 = Skel(w, yb).bend((xm, yb), (xm, yb + r)).L(xm, mid - r).bend((xm, mid), (0, mid), k=0.55)
    sh = stroked(s1, n) | stroked(s2, n)
    return G(sh & rect(0, -2000, 2000, 2000), 40, 24)


@glyph("braceright", 0x7D)
def braceright(p):
    sh = braceleft(p).shape
    b = sh.bounds()
    return G(sh.mirror_x((b[0] + b[2]) / 2), 24, 40)


@glyph("slash", 0x2F)
def slash(p):
    t = p.V * 0.98
    return G(diag(330, PAREN_TOP, 0, PAREN_BOT, t), 10, 10)


@glyph("backslash", 0x5C)
def backslash(p):
    t = p.V * 0.98
    return G(diag(0, PAREN_TOP, 330, PAREN_BOT, t), 10, 10)


@glyph("fraction", 0x2044)
def fraction(p):
    t = p.V * 0.9
    return G(diag(300, CAP, 0, 0, t), -60, -60)


@glyph("bar", 0x7C)
def bar(p):
    return G(rect(0, PAREN_BOT - 40, p.V, PAREN_TOP + 40), 90, 90)


@glyph("brokenbar", 0xA6)
def brokenbar(p):
    m = (PAREN_TOP + PAREN_BOT) / 2
    return G(rect(0, PAREN_BOT - 40, p.V, m - 60) | rect(0, m + 60, p.V, PAREN_TOP + 40), 90, 90)


# --- math ----------------------------------------------------------------------------------

def math_t(p):
    return p.V * 0.92


MW = 480          # width of the math operators
MC = None


def mc():
    return CAP * 0.5 - 10   # centre of + − = etc. (between x-height and cap height)


@glyph("plus", 0x2B)
def plus(p):
    t = math_t(p)
    c = mc()
    return G(rect(0, c - t / 2, MW, c + t / 2) | rect(MW / 2 - t / 2, c - MW / 2, MW / 2 + t / 2, c + MW / 2), 50, 50)


@glyph("minus", 0x2212)
def minus(p):
    t = math_t(p)
    c = mc()
    return G(rect(0, c - t / 2, MW, c + t / 2), 50, 50)


@glyph("equal", 0x3D)
def equal(p):
    t = math_t(p)
    c = mc()
    g = mix(84, 92, p.w)
    return G(rect(0, c + g - t / 2, MW, c + g + t / 2) | rect(0, c - g - t / 2, MW, c - g + t / 2), 50, 50)


@glyph("notequal", 0x2260)
def notequal(p):
    t = math_t(p)
    c = mc()
    sh = equal(p).shape | (diag(MW * 0.72, c + 240, MW * 0.28, c - 240, t * 0.92))
    return G(sh, 50, 50)


@glyph("multiply", 0xD7)
def multiply(p):
    t = math_t(p)
    c = mc()
    s = MW * 0.80
    cx = MW / 2
    a = _bar(cx - s / 2, c - s / 2, cx + s / 2, c + s / 2, t)
    b = _bar(cx - s / 2, c + s / 2, cx + s / 2, c - s / 2, t)
    # ends cut square to the page, not to the stroke
    return G((a | b) & rect(cx - s / 2, c - s / 2, cx + s / 2, c + s / 2), 70, 70)


@glyph("divide", 0xF7)
def divide(p):
    t = math_t(p)
    c = mc()
    d = dsize(p)
    sh = rect(0, c - t / 2, MW, c + t / 2) | squircle(MW / 2, c + 150, d, d) | squircle(MW / 2, c - 150, d, d)
    return G(sh, 50, 50)


@glyph("plusminus", 0xB1)
def plusminus(p):
    t = math_t(p)
    c = mc() + 50
    arm = MW * 0.42
    sh = rect(0, c - t / 2, MW, c + t / 2) | rect(MW / 2 - t / 2, c - arm, MW / 2 + t / 2, c + arm)
    sh = sh | rect(0, c - arm - 90 - t, MW, c - arm - 90)
    return G(sh, 50, 50)


@glyph("less", 0x3C)
def less(p):
    return G(angle(p, MW * 0.86, MW * 0.92, mc(), math_t(p)), 64, 64)


@glyph("greater", 0x3E)
def greater(p):
    return G(angle(p, MW * 0.86, MW * 0.92, mc(), math_t(p), right=True), 64, 64)


@glyph("lessequal", 0x2264)
def lessequal(p):
    t = math_t(p)
    a = angle(p, MW * 0.86, MW * 0.78, mc() + 70, t)
    return G(a | rect(0, mc() - 250 - t / 2, MW * 0.86, mc() - 250 + t / 2), 64, 64)


@glyph("greaterequal", 0x2265)
def greaterequal(p):
    t = math_t(p)
    a = angle(p, MW * 0.86, MW * 0.78, mc() + 70, t, right=True)
    b = a.bounds()
    return G(a | rect(b[0], mc() - 250 - t / 2, b[2], mc() - 250 + t / 2), 64, 64)


@glyph("asciitilde", 0x7E)
def asciitilde(p):
    t = math_t(p)
    c = mc()
    w = MW
    s = Skel(0, c - 30).C((w * 0.18, c + 70), (w * 0.34, c + 60), (w * 0.5, c)).C((w * 0.66, c - 60), (w * 0.82, c - 70), (w, c + 30))
    from geom import nib
    return G(stroked(s, nib(t, t * 0.9)), 50, 50)


@glyph("approxequal", 0x2248)
def approxequal(p):
    a = asciitilde(p).shape
    return G(a.move(0, 90) | a.move(0, -90), 50, 50)


@glyph("asciicircum", 0x5E)
def asciicircum(p):
    t = p.V * 0.92
    w, h = 400, 300
    top = CAP
    sh = _bar(w / 2, top, 0, top - h, t) | _bar(w / 2, top, w, top - h, t)
    sh = sh & rect(-1000, top - h, 2000, top)
    return G(sh, 40, 40)


@glyph("degree", 0xB0)
def degree(p):
    from geom import nib
    s = 230
    return G(oval(0, s, CAP - s, CAP, p.V * 0.86, p.V * 0.78, 70, nib(p.V * 0.86, p.V * 0.78)), 50, 50)


@glyph("asterisk", 0x2A)
def asterisk(p):
    t = p.V * 0.94
    cy = CAP - 190
    h = 360
    v = rect(-t / 2, cy - h / 2, t / 2, cy + h / 2)
    a = _bar(-h * 0.52, cy - h * 0.30, h * 0.52, cy + h * 0.30, t)
    b = _bar(-h * 0.52, cy + h * 0.30, h * 0.52, cy - h * 0.30, t)
    sh = (v | a | b) & rect(-1000, cy - h / 2, 1000, cy + h / 2)
    sh = sh & rect(-h * 0.46, -1000, h * 0.46, 2000)
    return G(sh, 40, 40)


@glyph("numbersign", 0x23)
def numbersign(p):
    # the lamella grid: vertical strokes, never slanted
    t = p.V * 0.92
    W = 560
    h = CAP * 0.86
    sh = rect(W * 0.25, 0, W * 0.25 + t, h) | rect(W * 0.75 - t, 0, W * 0.75, h)
    sh = sh | rect(0, h * 0.30 - t / 2, W, h * 0.30 + t / 2) | rect(0, h * 0.70 - t / 2, W, h * 0.70 + t / 2)
    return G(sh, 30, 30)


@glyph("percent", 0x25)
def percent(p):
    from geom import nib
    V = p.V * 0.86
    H = V * 0.86
    w, h = 230, 320
    n = nib(V, H)
    a = oval(0, w, CAP - h, CAP + 6, V, H, 80, n)
    b = oval(w + 160, 2 * w + 160, -6, h, V, H, 80, n)
    s = diag(2 * w + 60, CAP, w + 0, 0, p.V * 0.9)
    return G(a | b | s, 40, 40)


@glyph("perthousand", 0x2030)
def perthousand(p):
    from geom import nib
    V = p.V * 0.86
    H = V * 0.86
    w, h = 230, 320
    n = nib(V, H)
    a = oval(0, w, CAP - h, CAP + 6, V, H, 80, n)
    b = oval(w + 160, 2 * w + 160, -6, h, V, H, 80, n)
    c = b.move(w + 60)
    s = diag(2 * w + 60, CAP, w + 0, 0, p.V * 0.9)
    return G(a | b | c | s, 40, 40)


# --- signs ---------------------------------------------------------------------------------

@glyph("at", 0x40)
def at(p):
    from geom import nib
    V, H = p.V * 0.96, p.H * 0.96
    n = nib(V, H)
    W = 860
    top, bot = CAP + 30, DESC + 90
    outer = oval(0, W, bot, top, V, H, 250, n)
    # an a-bowl with its stem inside the ring
    iw = 340
    x0 = (W - iw) / 2 - 20
    ib, it = 160, 160 + 400
    inner = oval(x0, x0 + iw, ib, it, V, H, 130, n)
    stem = rect(x0 + iw - V, ib, x0 + iw, it)
    # the ring opens where the stem would meet it
    outer = outer - rect(W * 0.52, bot - 50, W + 50, ib + 70)
    tail = rect(x0 + iw - V, ib, W - V / 2, ib + H)
    tail = rect(x0 + iw - V, bot + 0, x0 + iw, ib + 10)
    return G(outer | inner | stem, 50, 50)


@glyph("ampersand", 0x26)
def ampersand(p):
    V, H = p.VC, p.HC
    nb = p.nibC()
    W = mix(600, 660, p.w)
    # upper loop: a small ring
    lw = W * 0.56
    lx = W * 0.10
    loop = oval(lx, lx + lw, CAP * 0.56, CAP + OSC, V * 0.94, H, 110, nb)
    # lower bowl: a ring opened at the upper right, its arm cut horizontally
    lo = oval(0, W * 0.86, -OSC, CAP * 0.62, V, H, 150, nb)
    lo = lo - rect(W * 0.40, CAP * 0.36, W + 50, CAP * 0.70)
    lo = lo - rect(lx + V * 0.5, CAP * 0.50, W, CAP)
    t = p.VC * mix(1.0, 0.98, p.w)
    d = diag(lx + V * 0.9, CAP * 0.62, W - t * 0.55, 0, t)
    d = d & rect(-100, 0, 2000, CAP * 0.62)
    return G(loop | lo | d, 40, 20)


@glyph("section", 0xA7)
def section(p):
    from upper import S_
    s = S_(p).shape
    b = s.bounds()
    sc = 0.70
    s = s.transform(sc, 0, 0, sc, 0, 0)
    return G(s.move(0, 230) | s.move(0, -60), 40, 40)


@glyph("paragraph", 0xB6)
def paragraph(p):
    V = p.VC
    W = 520
    sh = rect(W - V, DESC + 40, W, CAP) | rect(W - 2 * V - 70, DESC + 40, W - V - 70, CAP)
    from geom import nib
    bowl = oval(0, W - V - 50, CAP * 0.36, CAP, V * 2.2, p.HC, 120, nib(V * 2.2, p.HC))
    return G(sh | (squircle((W - V - 70) / 2, CAP * 0.68, W - V - 70, CAP * 0.64, 0.62)) | rect((W - V - 70) / 2, CAP - p.HC, W, CAP), 40, 50)


def _ring(p, size, y0):
    from geom import nib
    V, H = p.V * 0.86, p.V * 0.78
    return oval(0, size, y0, y0 + size, V, H, size * 0.32, nib(V, H))


@glyph("copyright", 0xA9)
def copyright(p):
    size = 820
    y0 = CAP / 2 - size / 2
    ring = _ring(p, size, y0)
    from geom import nib
    V, H = p.V * 0.88, p.V * 0.80
    cw = 330
    c = oval(size / 2 - cw / 2, size / 2 + cw / 2, CAP / 2 - 200, CAP / 2 + 200, V, H, 100, nib(V, H))
    c = c - rect(size / 2, CAP / 2 - 90, size, CAP / 2 + 90)
    return G(ring | c, 40, 40)


@glyph("registered", 0xAE)
def registered(p):
    size = 820
    y0 = CAP / 2 - size / 2
    ring = _ring(p, size, y0)
    from upper import R_
    r = R_(params_scaled(p)).shape
    b = r.bounds()
    sc = 0.50
    r = r.transform(sc, 0, 0, sc, 0, 0)
    b = r.bounds()
    r = r.move(size / 2 - (b[0] + b[2]) / 2, CAP / 2 - (b[1] + b[3]) / 2)
    return G(ring | r, 40, 40)


def params_scaled(p):
    """Parameters for small marks inside a ring: heavier stems so that,
    scaled down, they match the surrounding weight."""
    import params as pm
    q = pm.P(min(1.6, p.w + 0.9))
    return q


@glyph("trademark", 0x2122)
def trademark(p):
    from upper import M_, T_
    q = params_scaled(p)
    sc = 0.44
    t = T_(q).shape.transform(sc, 0, 0, sc, 0, 0)
    m = M_(q).shape.transform(sc, 0, 0, sc, 0, 0)
    tb = t.bounds()
    m = m.move(tb[2] + 40, 0)
    sh = (t | m).move(0, CAP - CAP * sc)
    return G(sh, 40, 40)


@glyph("dagger", 0x2020)
def dagger(p):
    V = p.V
    W = 420
    return G(rect(W / 2 - V / 2, DESC + 40, W / 2 + V / 2, CAP) | rect(0, CAP - 250, W, CAP - 250 + p.H), 30, 30)


@glyph("daggerdbl", 0x2021)
def daggerdbl(p):
    V = p.V
    W = 420
    sh = rect(W / 2 - V / 2, DESC + 40, W / 2 + V / 2, CAP) | rect(0, CAP - 250, W, CAP - 250 + p.H)
    sh = sh | rect(0, 120, W, 120 + p.H)
    return G(sh, 30, 30)


# --- currency ---------------------------------------------------------------------------------

@glyph("dollar", 0x24)
def dollar(p):
    from upper import S_
    s = S_(p).shape
    b = s.bounds()
    cx = (b[0] + b[2]) / 2
    t = p.V * 0.82
    line = rect(cx - t / 2, -110, cx + t / 2, CAP + 110)
    line = line - rect(-100, 40, 2000, CAP - 40)
    return G(s | line, 40, 40)


@glyph("cent", 0xA2)
def cent(p):
    from lower import c_
    s = c_(p).shape
    b = s.bounds()
    cx = (b[0] + b[2]) / 2
    t = p.V * 0.82
    line = rect(cx - t / 2, -120, cx + t / 2, XH + 120) - rect(-100, 30, 2000, XH - 30)
    return G(s | line, "R", 30)


@glyph("Euro", 0x20AC)
def euro(p):
    from upper import C_
    c = C_(p).shape
    b = c.bounds()
    t = p.HC
    sh = c.move(70)
    bars = rect(0, CAP * 0.58 - t / 2, b[2] * 0.70, CAP * 0.58 + t / 2) | rect(0, CAP * 0.40 - t / 2, b[2] * 0.66, CAP * 0.40 + t / 2)
    return G(sh | bars, 20, 30)


@glyph("sterling", 0xA3)
def sterling(p):
    V, H = p.VC, p.HC
    from parts import hook_up_right
    W = 520
    xc = 110 + V / 2
    q = p
    stem = hook_up_right(p, xc, H / 2, CAP + OSC, p.RC * 0.78, xc + 260, nib=p.nibC())
    sh = stem | rect(0, 0, W, H) | rect(10, CAP * 0.42 - H / 2, xc + V / 2 + 180, CAP * 0.42 + H / 2)
    sh = sh | rect(xc - V / 2, 0, xc + V / 2, 200)
    return G(sh, 40, 40)


@glyph("yen", 0xA5)
def yen(p):
    from upper import Y_
    y = Y_(p).shape
    b = y.bounds()
    t = p.HC
    w = b[2] - b[0]
    sh = y | rect(b[0] + w * 0.18, CAP * 0.30 - t / 2, b[2] - w * 0.18, CAP * 0.30 + t / 2)
    sh = sh | rect(b[0] + w * 0.18, CAP * 0.12 - t / 2, b[2] - w * 0.18, CAP * 0.12 + t / 2)
    return G(sh, 20, 20)


# --- arrows and marks for interfaces ----------------------------------------------------------------

def arrow_right(p, length=700):
    t = math_t(p)
    c = mc()
    head = angle(p, 300, 560, c, t, right=True)
    hb = head.bounds()
    head = head.move(length - hb[2])
    shaft = rect(0, c - t / 2, length - t * 0.6, c + t / 2)
    return shaft | head


@glyph("arrowright", 0x2192)
def arrowright(p):
    return G(arrow_right(p), 50, 50)


@glyph("arrowleft", 0x2190)
def arrowleft(p):
    sh = arrow_right(p)
    b = sh.bounds()
    return G(sh.mirror_x((b[0] + b[2]) / 2), 50, 50)


@glyph("arrowup", 0x2191)
def arrowup(p):
    sh = arrow_right(p, 720).transform(0, 1, -1, 0, 0, 0)
    b = sh.bounds()
    return G(sh.move(-b[0], -b[1] - 20), 50, 50)


@glyph("arrowdown", 0x2193)
def arrowdown(p):
    sh = arrow_right(p, 720).transform(0, -1, 1, 0, 0, 0)
    b = sh.bounds()
    return G(sh.move(-b[0], -b[1] - 20), 50, 50)


@glyph("arrownortheast", 0x2197)
def arrownortheast(p):
    t = math_t(p)
    s = 560
    shaft = _bar(0, 0, s - t * 0.4, s - t * 0.4, t)
    head = rect(s - 380, s - t, s, s) | rect(s - t, s - 380, s, s)
    sh = (shaft | head) & rect(0, 0, s, s)
    return G(sh.move(0, mc() - s / 2), 60, 60)


@glyph("arrowsoutheast", 0x2198)
def arrowsoutheast(p):
    sh = arrownortheast(p).shape
    b = sh.bounds()
    return G(sh.mirror_y((b[1] + b[3]) / 2), 60, 60)


@glyph("checkmark", 0x2713)
def checkmark(p):
    t = math_t(p) * 1.05
    c = mc()
    a = _bar(0, c + 10, 190, c - 190, t)
    b = _bar(190, c - 190, 560, c + 250, t)
    sh = (a | b) & rect(0, c - 190 - t, 560, c + 250)
    return G(sh, 50, 50)


@glyph("uni25CF", 0x25CF)
def blackcircle(p):
    s = 640
    return G(squircle(s / 2, mc(), s, s, 0.60), 60, 60)


@glyph("uni25CB", 0x25CB)
def whitecircle(p):
    from geom import nib
    s = 640
    return G(oval(0, s, mc() - s / 2, mc() + s / 2, p.V * 0.9, p.V * 0.9, s * 0.30, nib(p.V * 0.9, p.V * 0.9)), 60, 60)


# --- spaces ---------------------------------------------------------------------------------

def space_w(p):
    return round(mix(236, 244, p.w))


@glyph("space", 0x20)
def space(p):
    return G(Shape(), advance=space_w(p))


@glyph("uni00A0", 0xA0)
def nbspace(p):
    return G(Shape(), advance=space_w(p))


@glyph("uni2009", 0x2009)
def thinspace(p):
    return G(Shape(), advance=round(space_w(p) * 0.66))


@glyph("uni202F", 0x202F)
def narrownbspace(p):
    return G(Shape(), advance=round(space_w(p) * 0.66))


@glyph("uni2007", 0x2007)
def figurespace(p):
    from figures import tab_width
    return G(Shape(), advance=round(tab_width(p)))
