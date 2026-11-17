"""Lico — parametric glyph drawings.

Every redrawn glyph is one function of a master's parameters (`P`), so the
Regular and Black masters always receive point-compatible outlines and the
weight axis interpolates cleanly.

Design rule — "the bend": wherever a stroke changes direction (the foot of t,
the hook of f, the tail of j / y / g, the bracket of t) it turns through one
generous, near-circular arc, like a sheet of flexible stone wrapping a corner.
All bends share the same outer radius per weight (`P.R`).
"""
from dataclasses import dataclass

K = 0.56  # handle length for a quarter turn (0.5523 = circle; a touch squarer)


@dataclass
class P:
    """Per-master parameters, in font units (UPM 2048)."""
    name: str
    V: float      # lowercase vertical stem
    H: float      # horizontal bar / terminal thickness
    VC: float     # capital vertical stem
    HC: float     # capital horizontal bar
    R: float      # outer radius of the bend
    xh: float = 1080
    cap: float = 1440
    asc: float = 1500
    desc: float = -390
    os: float = 24  # overshoot

    def lerp(self, reg, black):
        """Pick a hand-tuned value for this master."""
        return reg if self.name == "Regular" else black


REGULAR = P("Regular", V=168, H=140, VC=184, HC=150, R=300, os=24)
BLACK = P("Black", V=400, H=280, VC=420, HC=300, R=520, os=28)


class Path:
    """Tiny contour builder. `arc` turns a corner through a quarter curve."""

    def __init__(self):
        self.contours = []
        self.cur = None

    def M(self, x, y):
        self.contours.append([("move", (x, y))])
        self.cur = (x, y)
        return self

    def L(self, x, y):
        self.contours[-1].append(("line", (x, y)))
        self.cur = (x, y)
        return self

    def C(self, c1, c2, p):
        self.contours[-1].append(("curve", c1, c2, p))
        self.cur = p
        return self

    def arc(self, corner, end, k=K, k2=None):
        """Curve from the current point to `end`; `corner` is where the two
        tangents meet. k / k2 are the handle lengths as fractions of each leg."""
        k2 = k if k2 is None else k2
        x0, y0 = self.cur
        cx, cy = corner
        x1, y1 = end
        c1 = (x0 + (cx - x0) * k, y0 + (cy - y0) * k)
        c2 = (x1 + (cx - x1) * k2, y1 + (cy - y1) * k2)
        return self.C(c1, c2, end)

    def draw(self, glyph):
        pen = glyph.getPen()
        for contour in self.contours:
            for seg in contour:
                if seg[0] == "move":
                    pen.moveTo(_r(seg[1]))
                elif seg[0] == "line":
                    pen.lineTo(_r(seg[1]))
                else:
                    pen.curveTo(_r(seg[1]), _r(seg[2]), _r(seg[3]))
            pen.closePath()


def _r(p):
    return (round(p[0]), round(p[1]))


def set_anchor(glyph, name, x, y):
    for a in glyph.anchors:
        if a.name == name:
            a.x, a.y = round(x), round(y)
            return
    glyph.appendAnchor({"name": name, "x": round(x), "y": round(y)})


# --------------------------------------------------------------------------
# glyphs
# --------------------------------------------------------------------------

def draw_t(g, p):
    """t — flat top, the left of the crossbar bends up into the stem (the
    bracket), the foot bends through the shared radius to a flat terminal."""
    V, H, R = p.V, p.H, p.R
    xl = p.lerp(232, 172)            # stem left
    xr = xl + V
    bar_l = p.lerp(48, 24)           # crossbar left tip
    bar_r = p.lerp(622, 772)         # crossbar right tip
    top = p.lerp(1352, 1372)         # flat top of the stem
    rb = p.lerp(204, 228)            # bracket height above the bar
    end = p.lerp(650, 812)           # foot terminal
    xh = p.xh
    rix, riy = R - V, R - H          # inner radii, concentric with the outer

    pa = Path()
    pa.M(xl + R, 0).L(end, 0).L(end, H).L(xr + rix, H)
    pa.arc((xr, H), (xr, H + riy))
    pa.L(xr, xh - H).L(bar_r, xh - H).L(bar_r, xh).L(xr, xh)
    pa.L(xr, top).L(xl, top).L(xl, xh + rb)
    pa.arc((xl, xh), (bar_l, xh), k=0.62, k2=0.5)   # the bracket
    pa.L(bar_l, xh - H).L(xl, xh - H).L(xl, R)
    pa.arc((xl, 0), (xl + R, 0))
    g.clearContours()
    pa.draw(g)
    g.width = round(end + p.lerp(62, 40))
    set_anchor(g, "bottom", xl + R * 0.72, 0)
    set_anchor(g, "center", (xl + xr) / 2, p.lerp(150, 96))
    set_anchor(g, "ttop", (xl + xr) / 2, xh)
    set_anchor(g, "centerExt", g.width - 14, 720)



def draw_l(g, p):
    """l — the lamella: one straight slat, same stem and spacing as i."""
    xl = p.lerp(164, 125)
    xr = xl + p.V
    Path().M(xl, 0).L(xr, 0).L(xr, p.asc).L(xl, p.asc).draw(_clear(g))
    g.width = round(xr + xl)
    mid = (xl + xr) / 2
    set_anchor(g, "bottom", mid, 0)
    set_anchor(g, "center", mid, p.lerp(720, 750))
    set_anchor(g, "centerExt", g.width - 14, 720)
    set_anchor(g, "top", mid, p.asc)
    set_anchor(g, "topright", xr + p.lerp(36, 14), 1950)


def draw_l_tail(g, p):
    """l.ss02 — the bent lamella, for codes where I / l / 1 must not be confused."""
    V, H, R = p.V, p.H, p.R
    xl = p.lerp(164, 125)
    xr = xl + V
    end = xl + R + p.lerp(96, 100)
    rix, riy = R - V, R - H
    pa = Path()
    pa.M(xl + R, 0).L(end, 0).L(end, H).L(xr + rix, H)
    pa.arc((xr, H), (xr, H + riy))
    pa.L(xr, p.asc).L(xl, p.asc).L(xl, R)
    pa.arc((xl, 0), (xl + R, 0))
    pa.draw(_clear(g))
    g.width = round(end + p.lerp(62, 40))
    mid = (xl + xr) / 2
    set_anchor(g, "bottom", xl + R * 0.72, 0)
    set_anchor(g, "center", mid, p.lerp(720, 750))
    set_anchor(g, "centerExt", g.width - 14, 720)
    set_anchor(g, "top", mid, p.asc)
    set_anchor(g, "topright", xr + p.lerp(36, 14), 1950)


def draw_f(g, p):
    """f — the hook is the t's foot turned upside down: same arc, flat terminal."""
    V, H = p.V, p.H
    R = p.R * 0.9
    xl = p.lerp(218, 159)
    xr = xl + V
    bar_l, bar_r = p.lerp(57, 30), p.lerp(628, 731)
    end = xl + R + p.lerp(132, 150)
    rix, riy = R - V, R - H
    xh, asc = p.xh, p.asc
    pa = Path()
    pa.M(xl, 0).L(xr, 0).L(xr, xh - H).L(bar_r, xh - H).L(bar_r, xh).L(xr, xh)
    pa.L(xr, asc - H - riy)
    pa.arc((xr, asc - H), (xr + rix, asc - H))
    pa.L(end, asc - H).L(end, asc).L(xl + R, asc)
    pa.arc((xl, asc), (xl, asc - R))
    pa.L(xl, xh).L(bar_l, xh).L(bar_l, xh - H).L(xl, xh - H)
    pa.draw(_clear(g))
    g.width = round(p.lerp(698, 804) + (end - p.lerp(601, 754)) * 0.5)


def draw_jdotless(g, p):
    """j — stem drops and bends left through the shared arc."""
    V, H = p.V, p.H
    R = p.R * 0.9
    xl = p.lerp(228, 153)
    xr = xl + V
    end = p.lerp(34, 6)
    d = p.desc
    rix, riy = R - V, R - H
    pa = Path()
    pa.M(end, d).L(xr - R, d)
    pa.arc((xr, d), (xr, d + R))
    pa.L(xr, p.xh).L(xl, p.xh).L(xl, d + H + riy)
    pa.arc((xl, d + H), (xl - rix, d + H))
    pa.L(end, d + H)
    pa.draw(_clear(g))


def draw_y(g, p):
    """y — the right diagonal runs on below the baseline and bends into a
    flat tail, the same gesture as j."""
    xh, d, H = p.xh, p.desc, p.H
    # right stroke, outer edge: from the top-right corner down
    tr = p.lerp((1073, 1080), (1336, 1080))
    so = p.lerp(0.3818, 0.3945)           # dx per unit of descent, outer edge
    ti = p.lerp((887, 1080), (888, 1080))
    li = p.lerp((237, 1080), (457, 1080))
    lo = p.lerp((49, 1080), (9, 1080))
    vtx = p.lerp((561, 143), (673, 345))  # inner vertex of the V
    jn = p.lerp((488, -68), (495, -80))   # left stroke meets the tail
    y_a = p.lerp(-40, 20)                 # where the outer arc leaves the diagonal
    end = p.lerp(150, 180)                # tail terminal
    a_end = p.lerp(326, 470)              # outer arc lands on the descender line
    i_end = p.lerp(300, 430)              # inner arc lands on the tail's top edge

    def outer_x(y):
        return tr[0] - so * (tr[1] - y)

    si = p.lerp(0.348, 0.39)              # slope of the tail's inner edge
    i_corner = (jn[0] - si * (jn[1] - (d + H)), d + H)
    pa = Path()
    pa.M(end, d).L(a_end, d)
    pa.arc((outer_x(d), d), (outer_x(y_a), y_a), k=0.6, k2=0.5)
    pa.L(*tr).L(*ti).L(*vtx).L(*li).L(*lo).L(*jn)
    pa.arc(i_corner, (i_end, d + H), k=0.5, k2=0.6)
    pa.L(end, d + H)
    pa.draw(_clear(g))


def draw_qtail(g, p):
    """Q tail — a short stem through the bowl that bends right."""
    V = p.lerp(168, 380)
    H = p.lerp(144, 280)
    R = p.lerp(262, 440)
    xl = p.lerp(151, 99)
    xr = xl + V
    top = p.lerp(60, 84)
    bot = p.lerp(-300, -390)
    end = p.lerp(566, 722)
    rix, riy = R - V, R - H
    pa = Path()
    pa.M(xl + R, bot).L(end, bot).L(end, bot + H).L(xr + rix, bot + H)
    pa.arc((xr, bot + H), (xr, bot + H + riy))
    pa.L(xr, top).L(xl, top).L(xl, bot + R)
    pa.arc((xl, bot), (xl + R, bot))
    pa.draw(_clear(g))


def draw_I(g, p):
    """I — one plain slat (the serifed form lives in I.ss03)."""
    xl = p.lerp(164, 125)
    xr = xl + p.lerp(180, 410)
    Path().M(xl, 0).L(xr, 0).L(xr, p.cap).L(xl, p.cap).draw(_clear(g))
    g.width = round(xl + xr)
    mid = (xl + xr) / 2
    set_anchor(g, "bottom", mid, 0)
    set_anchor(g, "top", mid, p.cap)
    set_anchor(g, "ogonek", xr, 0)
    set_anchor(g, "topleft", p.lerp(4, 70), p.cap)


def _draw_hook(g, p, xl, V, top, end):
    H = p.H
    R = p.R * 0.9
    xr = xl + V
    d = p.desc
    rix, riy = R - V, R - H
    pa = Path()
    pa.M(end, d).L(xr - R, d)
    pa.arc((xr, d), (xr, d + R))
    pa.L(xr, top).L(xl, top).L(xl, d + H + riy)
    pa.arc((xl, d + H), (xl - rix, d + H))
    pa.L(end, d + H)
    pa.draw(_clear(g))


def draw_palatalhook(g, p):
    """Hook of eng / n-hook — the j bend."""
    _draw_hook(g, p, p.lerp(487, 377), p.V, p.lerp(38, 19), p.lerp(296, 232))


def draw_palatalhook_case(g, p):
    _draw_hook(g, p, p.lerp(481, 385), p.lerp(174, 390), p.lerp(38, 19), p.lerp(290, 236))


def _clear(g):
    g.clearContours()
    return g


DRAW = {
    "t": draw_t,
    "l": draw_l,
    "l.ss02": draw_l_tail,
    "f": draw_f,
    "jdotless": draw_jdotless,
    "y": draw_y,
    "_part.Qtail": draw_qtail,
    "I": draw_I,
    "palatalhookcomb": draw_palatalhook,
    "palatalhookcomb.case": draw_palatalhook_case,
}
