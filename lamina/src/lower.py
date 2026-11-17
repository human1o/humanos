"""Lamina — lowercase."""
from geom import Shape, Skel, halfplane_above, halfplane_below, poly, rect, stroked, union
from params import ASC, DESC, OS, XH
from parts import terminal_cut, arch, diag, hook_down_left, hook_down_right, hook_up_right, lc_oval, oval, squircle, vee, _edge_stroke
from registry import G, glyph

T_TOP = XH - 150     # horizontal cut of top terminals: a c e s
T_BOT = 140          # horizontal cut of bottom terminals: c s


def o_width(p):
    return p.C + 2 * p.V


def dot(p, cx):
    d = p.V * 1.16
    top = ASC - 2
    return squircle(cx, top - d / 2, d, d)


# --- straight letters -------------------------------------------------------

@glyph("l", 0x6C)
def l_(p):
    return G(rect(0, 0, p.V, ASC), "S", "S")


@glyph("dotlessi", 0x131)
def dotlessi(p):
    return G(rect(0, 0, p.V, XH), "S", "S")


@glyph("i", 0x69)
def i_(p):
    return G(rect(0, 0, p.V, XH) | dot(p, p.V / 2), "S", "S")


# --- arches -----------------------------------------------------------------

def n_shape(p, stem_top=XH):
    V = p.V
    xr = V + p.C + V / 2
    return rect(0, 0, V, stem_top) | arch(p, V, xr)


@glyph("n", 0x6E)
def n_(p):
    return G(n_shape(p), "S", "S")


@glyph("h", 0x68)
def h_(p):
    return G(n_shape(p, ASC), "S", "S")


@glyph("m", 0x6D)
def m_(p):
    V = p.V
    c = p.C * 0.86
    x2 = V + c + V / 2
    x3 = x2 + V / 2 + c + V / 2
    sh = rect(0, 0, V, XH) | arch(p, V, x2, apex_shift=0) | arch(p, x2 + V / 2, x3)
    return G(sh, "S", "S")


@glyph("u", 0x75)
def u_(p):
    sh = n_shape(p)
    b = sh.bounds()
    cx = (b[0] + b[2]) / 2
    return G(sh.rot180(cx, XH / 2), "S", "S")


@glyph("r", 0x72)
def r_(p):
    V = p.V
    xr = V + p.C + V / 2
    cut = V + p.C * 0.60
    arm = arch(p, V, xr) - rect(cut, -500, 2000, 2000)
    return G(rect(0, 0, V, XH) | arm, "S", 20)


# --- rounds -----------------------------------------------------------------

@glyph("o", 0x6F)
def o_(p):
    return G(lc_oval(p, 0, o_width(p)), "R", "R")


def bowl_with_stem(p, side, stem_top, stem_bottom):
    """b d p q: the o ring fused with a stem on one side."""
    W = o_width(p)
    ring = lc_oval(p, 0, W)
    if side == "right":
        stem = rect(W - p.V, stem_bottom, W, stem_top)
    else:
        stem = rect(0, stem_bottom, p.V, stem_top)
    return ring | stem


@glyph("d", 0x64)
def d_(p):
    return G(bowl_with_stem(p, "right", ASC, 0), "R", "S")


@glyph("b", 0x62)
def b_(p):
    return G(bowl_with_stem(p, "left", ASC, 0), "S", "R")


@glyph("p", 0x70)
def p_(p):
    return G(bowl_with_stem(p, "left", XH, DESC), "S", "R")


@glyph("q", 0x71)
def q_(p):
    return G(bowl_with_stem(p, "right", XH, DESC), "R", "S")


@glyph("c", 0x63)
def c_(p):
    W = o_width(p) - 18
    ring = lc_oval(p, 0, W)
    top_cut = T_TOP
    bot_cut = T_BOT
    cut = terminal_cut(W * 0.52, (bot_cut + top_cut) / 2, W, top_cut, bot_cut)
    return G(ring - cut, "R", 30)


@glyph("e", 0x65)
def e_(p):
    W = o_width(p)
    ring = lc_oval(p, 0, W)
    bar_top = XH * 0.555 + p.H / 2
    bar = rect(p.V / 2, bar_top - p.H, W - p.V / 2, bar_top)
    ap = terminal_cut(W * 0.52, (T_BOT - 16 + bar_top - p.H) / 2, W, bar_top - p.H, T_BOT - 16)
    return G((ring - ap) | bar, "R", 34)


# --- hooks ------------------------------------------------------------------

@glyph("t", 0x74)
def t_(p):
    V, H = p.V, p.H
    xc = 56 + V / 2
    top = XH + 150
    reach = 118 + 20 * p.w
    foot = xc + V / 2 + 112
    stem = hook_down_right(p, xc, top, 0, reach, foot)
    bar = rect(0, XH - H, xc + V / 2 + 122, XH)
    return G(stem | bar, 14, 18)


@glyph("f", 0x66)
def f_(p):
    V, H = p.V, p.H
    xc = 62 + V / 2
    reach = 124 + 20 * p.w
    end = xc + V / 2 + 136
    stem = hook_up_right(p, xc, 0, ASC + 4, reach, end)
    bar = rect(0, XH - H, xc + V / 2 + 128, XH)
    return G(stem | bar, 14, 6)


@glyph("dotlessj", 0x237)
def dotlessj(p):
    V = p.V
    xc = V / 2
    reach = 112 + 20 * p.w
    sh = hook_down_left(p, xc, XH, DESC, reach, xc - reach - 52)
    return G(sh, 18, "S")


@glyph("j", 0x6A)
def j_(p):
    g = dotlessj(p)
    b = rect(0, 0, p.V, XH).bounds()
    return G(g.shape | dot(p, p.V / 2), g.left, g.right)


# --- a, s -------------------------------------------------------------------

@glyph("a", 0x61)
def a_(p):
    V, H = p.V, p.H
    W = o_width(p) - 6
    xr = W - V / 2                      # stem centre
    # top: the arch of n seen from the left, its tail cut horizontally
    yt = XH + OS - H / 2
    r = p.R
    xl = V / 2 + 8
    xa = (xl + xr) / 2 + 6
    s = Skel(xl, XH - 230)
    s.bend((xl, yt), (xa, yt), k=0.62).bend((xr, yt), (xr, yt - r)).L(xr, 0)
    top = stroked(s, p.nib()) - rect(-100, -100, xa - 20, A_CUT)
    # bowl: a flat-topped half-oval hung from the stem
    bt = XH * 0.585
    yb = -OS + H / 2
    ytb = bt - H / 2
    xlb = V / 2 + 2
    rb = min(118, (ytb - yb) / 2 - 1)
    sb = Skel(xr, ytb)
    sb.L(xlb + 120, ytb).bend((xlb, ytb), (xlb, ytb - rb), k=0.62)
    sb.L(xlb, yb + rb).bend((xlb, yb), ((xlb + xr) / 2 - 6, yb))
    sb.bend((xr, yb), (xr, yb + rb * 1.5), k=0.6)
    bowl = stroked(sb, p.nib(), taper=[(0, 1), (0.78, 1), (1.0, 0.7)])
    return G(top | bowl, 34, "S")


A_CUT = T_TOP


@glyph("s", 0x73)
def s_(p):
    V, H = p.V, p.H
    W = o_width(p) * mix(0.86, 0.91, p.w)
    xl, xr = V / 2 + 4, W - V / 2 - 4
    xc = W / 2
    yt = XH + OS - H / 2
    yb = -OS + H / 2
    ym = XH / 2 + 4
    r1 = ((XH + OS - H / 2) - (-OS + H / 2)) * mix(0.25, 0.235, p.w)
    top_cut, bot_cut = T_TOP + 6, T_BOT + 8
    slope = mix(0.50, 0.40, p.w)        # the spine's fall to the right
    d = (1, -slope)
    import math
    n = math.hypot(*d)
    d = (d[0] / n, d[1] / n)
    a_ = 0.58 * ((yt - r1) - ym)
    b_ = 0.74 * (xc - xl)
    s = Skel(xr, top_cut - 30)
    s.bend((xr, yt), (xc, yt), k=0.62).bend((xl, yt), (xl, yt - r1), k=0.60)
    s.C((xl, yt - r1 - a_), (xc - d[0] * b_, ym - d[1] * b_), (xc, ym))
    s.C((xc + d[0] * b_, ym + d[1] * b_), (xr, yb + r1 + a_), (xr, yb + r1))
    s.bend((xr, yb), (xc, yb), k=0.60).bend((xl, yb), (xl, bot_cut + 30), k=0.62)
    spine = mix(1.14, 1.10, p.w)
    sh = stroked(s, p.nib(), taper=[(0.0, 1), (0.30, 1), (0.46, spine), (0.54, spine), (0.70, 1), (1, 1)])
    sh = sh - rect(xr - 1.2 * V, top_cut - 60, W + 100, top_cut)
    sh = sh - rect(-100, bot_cut, xl + 1.2 * V, bot_cut + 60)
    return G(sh, 32, 32)


def mix(a, b, w):
    return a + (b - a) * w


# --- diagonals ----------------------------------------------------------------

def diag_t(p):
    return p.V * mix(0.98, 0.94, p.w)


@glyph("v", 0x76)
def v_(p):
    W = p.C + 2 * p.V + mix(-6, 6, p.w)
    return G(vee(p, W, XH, diag_t(p), flat=p.V * 1.14), 8, 8)


@glyph("w", 0x77)
def w_(p):
    t = diag_t(p) * 0.94
    Wv = (p.C + 2 * p.V) * 0.78
    flat = p.V * 1.04
    left = vee(p, Wv, XH, t, flat)
    right = vee(p, Wv, XH, t, flat).move(Wv - t * 1.15)
    return G(left | right, 6, 6)


@glyph("y", 0x79)
def y_(p):
    import math
    V, H = p.V, p.H
    W = p.C + 2 * V + mix(-6, 6, p.w)
    t = diag_t(p)
    flat = V * 1.14
    xc = W / 2
    left = _edge_stroke(0, XH, xc - flat / 2, 0, t, "left")
    # the right diagonal runs on below the baseline and bends into a flat tail
    x_top_c = W - t * 0.55                       # centre of its top cut
    x_base_c = xc + flat / 2 - t * 0.55          # centre at the baseline
    slope = (x_top_c - x_base_c) / XH            # dx per unit of height
    yb = DESC + H / 2
    x_at = lambda y: x_base_c + slope * y
    reach = 150
    y0 = yb + reach * 0.55
    s = Skel(x_at(XH + 80), XH + 80)
    s.L(x_at(y0), y0)
    corner = (x_at(yb), yb)
    s.bend(corner, (corner[0] - reach * 0.9, yb), k=0.55, k2=0.62)
    s.L(corner[0] - reach * 0.9 - 70, yb)
    wid = lambda tx, ty: math.hypot(t * ty, H * tx) if abs(tx) > 0.7 else t
    tail = stroked(s, _diag_nib(t, H, slope)) & rect(-500, DESC, 2000, XH)
    return G(left | tail, 8, 8)


def _diag_nib(t, H, slope):
    import math
    # along the diagonal keep the true thickness t; in the flat tail use H
    def width(tx, ty):
        a = abs(ty)
        return H + (t - H) * min(1.0, a / 0.92) ** 2
    return width


@glyph("x", 0x78)
def x_(p):
    W = p.C + 2 * p.V - mix(10, 0, p.w)
    t = diag_t(p)
    a = _edge_stroke(0, XH, W - 0, 0, t, "left")
    b = _edge_stroke(W, XH, 0, 0, t, "right")
    # keep the outer edges flush: shift each so its outer edge hits the box
    import math
    wh = t * math.hypot(W, XH) / XH
    a = poly((W - wh, 0), (W, 0), (wh, XH), (0, XH))
    b = poly((0, 0), (wh, 0), (W, XH), (W - wh, XH))
    return G(a | b, 10, 10)


@glyph("z", 0x7A)
def z_(p):
    import math
    H = p.H
    W = p.C + 2 * p.V - 40
    t = diag_t(p) * 1.0
    top = rect(0, XH - H, W, XH)
    bot = rect(0, 0, W, H)
    wh = t * math.hypot(W, XH - 2 * H) / (XH - 2 * H)
    d = poly((0, H), (wh, H), (W, XH - H), (W - wh, XH - H))
    return G(top | bot | d, 26, 26)


@glyph("k", 0x6B)
def k_(p):
    import math
    V = p.V
    t = diag_t(p) * 0.96
    W = p.C + V * 1.62
    stem = rect(0, 0, V, ASC)
    yj = XH * 0.44                       # the arm leaves the stem here (centre line)
    # arm: from the stem up to x-height, top cut horizontal
    wh = t * math.hypot(W - V, XH - yj) / (XH - yj)
    xt = W - wh / 2
    xb = V - wh * 0.30
    arm = diag(xt, XH, xb, yj - 30, t)
    # extend the arm's line below yj so it buries itself in the stem
    arm = arm - rect(-100, -100, V * 0.5, 2000)
    # leg: branches from the arm's centre line at 42 % of its length
    f = 0.40
    yb_ = yj - 30
    xs = xb + (xt - xb) * ((yj + (XH - yj) * f) - yb_) / (XH - yb_)
    ys = yj + (XH - yj) * f
    whl = t * math.hypot(W - xs, ys) / ys
    leg = diag(xs, ys, W - whl / 2 + 6, 0, t * 1.02)
    # trim the leg where it would poke above the arm
    sh = stem | arm | (leg & rect(-100, -100, 2000, ys))
    sh = sh & rect(0, 0, 2000, ASC)
    return G(sh, "S", 6)


@glyph("g", 0x67)
def g_(p):
    V, H = p.V, p.H
    W = o_width(p)
    ring = lc_oval(p, 0, W)
    xr = W - V / 2
    xl = V / 2 + 6
    xc = W / 2
    yb = DESC - OS + H / 2
    r = 140
    s = Skel(xr, XH)
    s.L(xr, yb + r).bend((xr, yb), (xc, yb)).bend((xl, yb), (xl, yb + r * 0.9), k=0.62)
    tail = stroked(s, p.nib()) - rect(-100, DESC + 120, xc - 20, 0)
    return G(ring | tail, "R", "S")
