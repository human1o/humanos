"""Lamina — figures.

Figures are drawn as capitals: cap height, their own stem weight, the same
oval, the same bend and the same horizontal cuts. Each figure has exactly one
drawing; the tabular forms are the same outlines centred on one width.
"""
import math

from geom import Skel, rect, stroked
from params import CAP, OSC
from parts import diag, oval
from registry import G, glyph


def mix(a, b, w):
    return a + (b - a) * w


def fw(p):
    """Body width of the round figures."""
    return mix(446, 488, p.w)


def tab_width(p):
    return fw(p) + 2 * mix(56, 48, p.w)


def f_oval(p, x0, x1, y0, y1, r=None):
    return oval(x0, x1, y0, y1, p.VF, p.HF, r if r is not None else p.RC * 0.94, p.nibF())


F_TOP = CAP - 196     # cuts of the open figures, same as C and S
F_BOT = 176
FIG = {}


def figure(name, uni):
    def deco(fn):
        FIG[name] = fn
        glyph(name, uni)(fn)
        return fn
    return deco


@figure("zero", 0x30)
def zero(p):
    W = fw(p)
    return G(f_oval(p, 0, W, -OSC, CAP + OSC), "R0", "R0")


@figure("one", 0x31)
def one(p):
    V, H = p.VF, p.HF
    W = fw(p)
    xc = W * 0.62
    reach = mix(118, 128, p.w)
    end = xc - V / 2 - mix(128, 120, p.w)
    yt = CAP - H / 2
    s = Skel(xc, 0).L(xc, yt - reach).bend((xc, yt), (xc - reach, yt)).L(end, yt)
    return G(stroked(s, p.nibF()), 60, 60)


@figure("two", 0x32)
def two(p):
    V, H = p.VF, p.HF
    W = fw(p) - 10
    xl, xr = V / 2 + 2, W - V / 2
    xc = W / 2
    yt = CAP + OSC - H / 2
    r = p.RC * 0.80
    s = Skel(xl, F_TOP - 30)
    s.bend((xl, yt), (xc, yt), k=0.62).bend((xr, yt), (xr, yt - r))
    # the spine falls from the right flank into the bottom-left corner
    y_end = H * 0.95
    s.C((xr, yt - r - 150), (xl + 40, y_end + 170), (xl + 4, y_end))
    s.L(xl + 4 - 60 * 0.30, y_end - 60)        # run on into the bar
    sh = stroked(s, p.nibF(), taper=[(0, 1), (0.55, 1), (0.8, mix(1.08, 1.04, p.w)), (1, 1.06)])
    sh = sh - rect(-100, F_TOP - 60, xl + 1.2 * V, F_TOP)
    sh = (sh & rect(0, H * 0.5, 2000, 2000)) | rect(0, 0, W + 6, H)
    return G(sh, "R0", "R0")


@figure("three", 0x33)
def three(p):
    V, H = p.VF, p.HF
    W = fw(p) - 10
    xl, xr = V / 2 + 2, W - V / 2
    xc = W / 2
    yt = CAP + OSC - H / 2
    yb = -OSC + H / 2
    mid = CAP * 0.56
    ym = mid - H / 2 + H / 2
    # upper bowl, narrower, ending in the middle bar
    xr_u = xr - 22
    r_u = (yt - ym) * 0.44
    s1 = Skel(xl, F_TOP - 30)
    s1.bend((xl, yt), (xc - 11, yt), k=0.62).bend((xr_u, yt), (xr_u, yt - r_u)).L(xr_u, ym + r_u)
    s1.bend((xr_u, ym), (xr_u - r_u * 1.05, ym)).L(W * 0.34, ym)
    up = stroked(s1, p.nibF()) - rect(-100, F_TOP - 60, xl + 1.2 * V, F_TOP)
    r_l = (ym - yb) * 0.46
    s2 = Skel(W * 0.34, ym).L(xr - r_l * 1.05, ym).bend((xr, ym), (xr, ym - r_l)).L(xr, yb + r_l)
    s2.bend((xr, yb), (xc, yb), k=0.6).bend((xl, yb), (xl, F_BOT + 30), k=0.62)
    lo = stroked(s2, p.nibF()) - rect(-100, F_BOT, xl + 1.2 * V, F_BOT + 60)
    return G(up | lo, "R0", "R0")


@figure("four", 0x34)
def four(p):
    V, H = p.VF, p.HF
    W = fw(p) + 10
    t = V * mix(0.96, 0.94, p.w)
    xs = W * 0.70                       # stem's left edge
    bar = CAP * 0.29
    stem = rect(xs, 0, xs + V, CAP)
    wh = t * math.hypot(xs - 0, CAP - bar) / (CAP - bar)
    d = rect(0, 0, 0, 0)
    from geom import poly
    d = poly((0, bar - H / 2), (wh, bar - H / 2), (xs + V, CAP), (xs + V - wh, CAP))
    d = d & rect(0, bar - H / 2, xs + V, CAP)
    barr = rect(0, bar - H / 2, W, bar + H / 2)
    return G(stem | d | barr, "R0", "R0")


@figure("five", 0x35)
def five(p):
    V, H = p.VF, p.HF
    W = fw(p) - 6
    xl, xr = V / 2 + 4, W - V / 2
    yb = -OSC + H / 2
    top = rect(xl - V / 2 + 14, CAP - H, W - 10, CAP)
    # the stem falls from the top bar, then bends into the bowl
    yj = CAP * 0.58
    ytb = CAP * 0.60 - H / 2 + 6
    stem = rect(xl - V / 2 + 14, ytb - 76, xl + V / 2 + 14, CAP)
    r = (ytb - yb) * 0.46
    s = Skel(xl + 14, ytb - 76)
    s.bend((xl + 14, ytb), (xl + 14 + r * 1.1, ytb), k=0.66)
    s.L(xr - r * 1.05, ytb).bend((xr, ytb), (xr, ytb - r)).L(xr, yb + r)
    s.bend((xr, yb), ((xl + xr) / 2, yb), k=0.6).bend((xl, yb), (xl, F_BOT + 30), k=0.62)
    bowl = stroked(s, p.nibF(), taper=[(0, 0.86), (0.14, 1), (1, 1)])
    bowl = bowl - rect(-100, F_BOT, xl + 1.2 * V, F_BOT + 60)
    return G(top | stem | bowl, "R0", "R0")


def six_shape(p):
    V, H = p.VF, p.HF
    W = fw(p)
    xl = V / 2
    xc = W / 2
    top = CAP * 0.615
    ring = f_oval(p, 0, W, -OSC, top + OSC * 0.5, r=p.RC * 0.78)
    yt = CAP + OSC - H / 2
    xr = W - V / 2 - 8
    r = p.RC * 0.86
    s = Skel(xl, top * 0.5).L(xl, yt - r).bend((xl, yt), (xc, yt), k=0.62)
    s.bend((xr, yt), (xr, F_TOP - 30), k=0.62)
    hook = stroked(s, p.nibF()) - rect(xr - 1.2 * V, F_TOP - 60, W + 100, F_TOP)
    return ring | hook


@figure("six", 0x36)
def six(p):
    return G(six_shape(p), "R0", "R0")


@figure("nine", 0x39)
def nine(p):
    sh = six_shape(p)
    b = sh.bounds()
    return G(sh.rot180((b[0] + b[2]) / 2, CAP / 2), "R0", "R0")


@figure("eight", 0x38)
def eight(p):
    V, H = p.VF, p.HF
    W = fw(p)
    mid = CAP * 0.545
    lo = f_oval(p, 0, W, -OSC, mid + H / 2, r=p.RC * 0.80)
    inset = mix(26, 22, p.w)
    up = f_oval(p, inset, W - inset, mid - H / 2, CAP + OSC, r=p.RC * 0.70)
    return G(lo | up, "R0", "R0")


@figure("seven", 0x37)
def seven(p):
    V, H = p.VF, p.HF
    W = fw(p) - 4
    t = V * mix(1.0, 0.98, p.w)
    top = rect(0, CAP - H, W, CAP)
    d = diag(W - t * 0.62, CAP - H / 2, W * 0.30, 0, t) & rect(-100, 0, W, CAP - H / 2)
    return G(top | d, "R0", "R0")
