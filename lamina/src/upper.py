"""Lamina — capitals."""
import math

from geom import Skel, poly, rect, stroked
from params import CAP, OSC
from parts import _edge_stroke, diag, oval, terminal_cut, vee
from registry import G, glyph


def mix(a, b, w):
    return a + (b - a) * w


def cap_oval(p, x0, width):
    return oval(x0, x0 + width, -OSC, CAP + OSC, p.VC, p.HC, p.RC, p.nibC())


def o_cap_width(p):
    return p.CC * 1.06 + 2 * p.VC


def h_width(p):
    return p.CC + 2 * p.VC


def tdiag(p):
    return p.VC * mix(0.98, 0.95, p.w)


C_TOP = CAP - 196     # horizontal cut of capital top terminals: C G S
C_BOT = 186           # and of bottom terminals: C S J


# --- straight -------------------------------------------------------------------

@glyph("I", 0x49)
def I_(p):
    return G(rect(0, 0, p.VC, CAP), "SC", "SC")


@glyph("H", 0x48)
def H_(p):
    V, Hh = p.VC, p.HC
    W = h_width(p)
    bar = CAP * 0.5 + Hh * 0.08
    return G(rect(0, 0, V, CAP) | rect(W - V, 0, W, CAP) | rect(V / 2, bar - Hh / 2, W - V / 2, bar + Hh / 2), "SC", "SC")


@glyph("E", 0x45)
def E_(p):
    V, Hh = p.VC, p.HC
    W = h_width(p) * 0.78
    mid = CAP * 0.5 + Hh * 0.08
    sh = (rect(0, 0, V, CAP) | rect(0, CAP - Hh, W, CAP) | rect(0, 0, W + 8, Hh)
          | rect(0, mid - Hh / 2, W * 0.92, mid + Hh / 2))
    return G(sh, "SC", 40)


@glyph("F", 0x46)
def F_(p):
    V, Hh = p.VC, p.HC
    W = h_width(p) * 0.76
    mid = CAP * 0.5 + Hh * 0.08
    sh = rect(0, 0, V, CAP) | rect(0, CAP - Hh, W, CAP) | rect(0, mid - Hh / 2, W * 0.92, mid + Hh / 2)
    return G(sh, "SC", 34)


@glyph("L", 0x4C)
def L_(p):
    V, Hh = p.VC, p.HC
    W = h_width(p) * 0.74
    return G(rect(0, 0, V, CAP) | rect(0, 0, W, Hh), "SC", 30)


@glyph("T", 0x54)
def T_(p):
    V, Hh = p.VC, p.HC
    W = h_width(p) * 0.88
    return G(rect(0, CAP - Hh, W, CAP) | rect(W / 2 - V / 2, 0, W / 2 + V / 2, CAP), 18, 18)


# --- rounds ---------------------------------------------------------------------

@glyph("O", 0x4F)
def O_(p):
    return G(cap_oval(p, 0, o_cap_width(p)), "RC", "RC")


@glyph("C", 0x43)
def C_(p):
    W = o_cap_width(p) - 34
    ring = cap_oval(p, 0, W)
    return G(ring - terminal_cut(W * 0.52, (C_BOT + C_TOP) / 2, W, C_TOP, C_BOT), "RC", 34)


@glyph("G", 0x47)
def G_(p):
    V, Hh = p.VC, p.HC
    W = o_cap_width(p) - 8
    ring = cap_oval(p, 0, W)
    bar_top = CAP * 0.47 + Hh / 2
    sh = ring - rect(W * 0.52, bar_top, W + 200, C_TOP)
    sh = sh | rect(W * 0.53, bar_top - Hh, W, bar_top)
    return G(sh, "RC", "SC")


@glyph("Q", 0x51)
def Q_(p):
    W = o_cap_width(p)
    ring = cap_oval(p, 0, W)
    t = tdiag(p) * 0.96
    tail = diag(W * 0.60, CAP * 0.24, W * 0.84, -150, t)
    return G(ring | tail, "RC", "RC")


@glyph("D", 0x44)
def D_(p):
    V, Hh = p.VC, p.HC
    W = p.CC * 1.0 + 2 * V
    yt, yb = CAP - Hh / 2, Hh / 2
    xs = V / 2
    xr = W - V / 2
    r = p.RC * 1.02
    rx = min(r * 1.05, xr - xs - 10)
    s = Skel(xs, yt).L(xr - rx, yt).bend((xr, yt), (xr, yt - r)).L(xr, yb + r)
    s.bend((xr, yb), (xr - rx, yb)).L(xs, yb)
    bowl = stroked(s, p.nibC())
    return G(rect(0, 0, V, CAP) | bowl, "SC", "RC")


def cap_bowl(p, x_stem, x_right, y_top, y_bot, r=None):
    """A bowl hung from the stem: flat top, bend, flank, bend, flat bottom.
    y_top / y_bot are the outer edges."""
    Hh = p.HC
    yt, yb = y_top - Hh / 2, y_bot + Hh / 2
    xr = x_right - p.VC / 2
    r = min(r or p.RC * 0.78, (yt - yb) / 2 - 2)
    rx = min(r * 1.12, xr - x_stem - 20)
    s = Skel(x_stem, yt).L(xr - rx, yt).bend((xr, yt), (xr, yt - r)).L(xr, yb + r)
    s.bend((xr, yb), (xr - rx, yb)).L(x_stem, yb)
    return stroked(s, p.nibC())


@glyph("P", 0x50)
def P_(p):
    V, Hh = p.VC, p.HC
    W = p.CC * 0.86 + 2 * V
    mid = CAP * 0.43
    return G(rect(0, 0, V, CAP) | cap_bowl(p, V / 2, W, CAP, mid - Hh / 2), "SC", "RC")


@glyph("R", 0x52)
def R_(p):
    V, Hh = p.VC, p.HC
    W = p.CC * 0.88 + 2 * V
    mid = CAP * 0.43
    bowl = cap_bowl(p, V / 2, W - 10, CAP, mid - Hh / 2)
    t = tdiag(p)
    leg = _edge_stroke(W + 6, 0, W * 0.50, mid, t, "right") & rect(0, 0, 2000, mid)
    return G(rect(0, 0, V, CAP) | bowl | leg, "SC", 14)


@glyph("B", 0x42)
def B_(p):
    V, Hh = p.VC, p.HC
    W = p.CC * 0.90 + 2 * V
    mid = CAP * 0.535
    up = cap_bowl(p, V / 2, W - 30, CAP, mid - Hh / 2, r=p.RC * 0.66)
    lo = cap_bowl(p, V / 2, W, mid + Hh / 2, 0, r=p.RC * 0.74)
    return G(rect(0, 0, V, CAP) | up | lo, "SC", "RC")


@glyph("U", 0x55)
def U_(p):
    V, Hh = p.VC, p.HC
    W = h_width(p) - 6
    xl, xr = V / 2, W - V / 2
    yb = -OSC + Hh / 2
    r = p.RC * 1.0
    s = Skel(xl, CAP).L(xl, yb + r).bend((xl, yb), ((xl + xr) / 2, yb)).bend((xr, yb), (xr, yb + r)).L(xr, CAP)
    return G(stroked(s, p.nibC()), "SC", "SC")


@glyph("J", 0x4A)
def J_(p):
    V, Hh = p.VC, p.HC
    W = h_width(p) * 0.70
    xl, xr = V / 2, W - V / 2
    yb = -OSC + Hh / 2
    r = p.RC * 0.92
    s = Skel(xr, CAP).L(xr, yb + r).bend((xr, yb), ((xl + xr) / 2, yb)).bend((xl, yb), (xl, C_BOT + 40))
    sh = stroked(s, p.nibC()) - rect(-100, C_BOT, (xl + xr) / 2, C_BOT + 200)
    return G(sh, 30, "SC")


@glyph("S", 0x53)
def S_(p):
    V, Hh = p.VC, p.HC
    W = o_cap_width(p) * mix(0.80, 0.84, p.w)
    xl, xr = V / 2 + 4, W - V / 2 - 4
    xc = W / 2
    yt = CAP + OSC - Hh / 2
    yb = -OSC + Hh / 2
    ym = CAP / 2 + 8
    r1 = (yt - yb) * mix(0.25, 0.24, p.w)
    slope = mix(0.42, 0.36, p.w)
    n = math.hypot(1, slope)
    d = (1 / n, -slope / n)
    a_ = 0.58 * ((yt - r1) - ym)
    b_ = 0.74 * (xc - xl)
    top_cut, bot_cut = C_TOP + 8, C_BOT + 10
    s = Skel(xr, top_cut - 30)
    s.bend((xr, yt), (xc, yt), k=0.62).bend((xl, yt), (xl, yt - r1), k=0.60)
    s.C((xl, yt - r1 - a_), (xc - d[0] * b_, ym - d[1] * b_), (xc, ym))
    s.C((xc + d[0] * b_, ym + d[1] * b_), (xr, yb + r1 + a_), (xr, yb + r1))
    s.bend((xr, yb), (xc, yb), k=0.60).bend((xl, yb), (xl, bot_cut + 30), k=0.62)
    spine = mix(1.12, 1.08, p.w)
    sh = stroked(s, p.nibC(), taper=[(0.0, 1), (0.30, 1), (0.46, spine), (0.54, spine), (0.70, 1), (1, 1)])
    sh = sh - rect(xr - 1.2 * V, top_cut - 60, W + 100, top_cut)
    sh = sh - rect(-100, bot_cut, xl + 1.2 * V, bot_cut + 60)
    return G(sh, 40, 40)


# --- diagonals ------------------------------------------------------------------

@glyph("V", 0x56)
def V_(p):
    W = h_width(p) * 0.98
    return G(vee(p, W, CAP, tdiag(p), flat=p.VC * 1.18), 6, 6)


@glyph("A", 0x41)
def A_(p):
    V, Hh = p.VC, p.HC
    W = h_width(p) * 1.0
    t = tdiag(p)
    sh = vee(p, W, CAP, t, flat=V * 1.18).mirror_y(CAP / 2)
    bar = CAP * 0.28
    inner = sh.bounds()
    sh = sh | (rect(0, bar - Hh / 2, W, bar + Hh / 2) & _inside_a(W, t, V))
    return G(sh, 6, 6)


def _inside_a(W, t, V):
    # the region between the two diagonals' outer edges
    flat = V * 1.18
    return poly((0, 0), (W, 0), (W / 2 + flat / 2, CAP), (W / 2 - flat / 2, CAP))


@glyph("W", 0x57)
def W_(p):
    t = tdiag(p) * 0.92
    Wv = h_width(p) * 0.76
    flat = p.VC * 1.08
    a = vee(p, Wv, CAP, t, flat)
    b = vee(p, Wv, CAP, t, flat).move(Wv - t * 1.12)
    return G(a | b, 4, 4)


@glyph("X", 0x58)
def X_(p):
    W = h_width(p) * 0.94
    t = tdiag(p)
    wh = t * math.hypot(W, CAP) / CAP
    a = poly((W - wh, 0), (W, 0), (wh, CAP), (0, CAP))
    b = poly((0, 0), (wh, 0), (W, CAP), (W - wh, CAP))
    return G(a | b, 8, 8)


@glyph("Y", 0x59)
def Y_(p):
    V = p.VC
    W = h_width(p) * 0.94
    t = tdiag(p)
    yj = CAP * 0.40
    arms = vee(p, W, CAP, t, flat=V * 1.0, bottom=yj)
    stem = rect(W / 2 - V / 2, 0, W / 2 + V / 2, yj + 10)
    return G(arms | stem, 4, 4)


@glyph("Z", 0x5A)
def Z_(p):
    Hh = p.HC
    W = h_width(p) * 0.86
    t = tdiag(p)
    wh = t * math.hypot(W, CAP - 2 * Hh) / (CAP - 2 * Hh)
    d = poly((0, Hh), (wh, Hh), (W, CAP - Hh), (W - wh, CAP - Hh))
    return G(rect(4, CAP - Hh, W, CAP) | rect(0, 0, W + 4, Hh) | d, 30, 30)


@glyph("N", 0x4E)
def N_(p):
    V = p.VC * 0.94
    W = h_width(p)
    t = tdiag(p)
    wh = t * math.hypot(W, CAP) / CAP
    d = poly((W - wh, 0), (W, 0), (wh, CAP), (0, CAP))
    return G(rect(0, 0, V, CAP) | rect(W - V, 0, W, CAP) | d, "SC", "SC")


@glyph("M", 0x4D)
def M_(p):
    V = p.VC * 0.94
    W = h_width(p) * 1.10
    t = tdiag(p) * 0.94
    flat = V * 0.96
    xc = W / 2
    left = _edge_stroke(0, CAP, xc - flat / 2, 0, t, "left") - rect(-10, -10, V * 0.5, CAP + 10)
    right = _edge_stroke(W, CAP, xc + flat / 2, 0, t, "right") - rect(W - V * 0.5, -10, W + 10, CAP + 10)
    sh = rect(0, 0, V, CAP) | rect(W - V, 0, W, CAP) | left | right
    return G(sh, "SC", "SC")


@glyph("K", 0x4B)
def K_(p):
    V = p.VC
    t = tdiag(p) * 0.96
    W = p.CC * 0.86 + V * 1.7
    yj = CAP * 0.44
    wh = t * math.hypot(W - V, CAP - yj) / (CAP - yj)
    xt = W - wh / 2
    xb = V - wh * 0.30
    arm = diag(xt, CAP, xb, yj - 40, t) - rect(-100, -100, V * 0.5, 2000)
    f = 0.34
    yb_ = yj - 40
    ys = yj + (CAP - yj) * f
    xs = xb + (xt - xb) * (ys - yb_) / (CAP - yb_)
    whl = t * math.hypot(W - xs, ys) / ys
    leg = diag(xs, ys, W - whl / 2 + 8, 0, t * 1.02) & rect(-100, -100, 2000, ys)
    sh = (rect(0, 0, V, CAP) | arm | leg) & rect(0, 0, 2000, CAP)
    return G(sh, "SC", 6)
