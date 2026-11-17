"""Shared parts: the oval, the arch, the bend hook, the dot.

Every round letter, arch and hook in Lamina is built from these few parts,
so the same flank and the same bend appear everywhere.
"""
from geom import K_BEND, Shape, Skel, poly, rect, stroked
from params import OS, OSC, XH


def oval_skel(xl, xr, yb, yt, r, k=None):
    """Closed skeleton: straight vertical flanks, bends top and bottom."""
    from params import WITHOUT
    xc = (xl + xr) / 2
    ym = (yb + yt) / 2
    r = min(r, (yt - yb) / 2 - 1)
    if "flank" in WITHOUT:
        r = (yt - yb) / 2 - 0.5
        k = 0.5523
    s = Skel(xr, ym)
    s.L(xr, yb + r).bend((xr, yb), (xc, yb), k)
    s.bend((xl, yb), (xl, yb + r), k).L(xl, yt - r)
    s.bend((xl, yt), (xc, yt), k).bend((xr, yt), (xr, yt - r), k)
    s.L(xr, ym)
    return s


def oval(x0, x1, y0, y1, V, H, r, nib, k=None):
    """A ring whose outer box is x0..x1, y0..y1 (overshoots included)."""
    s = oval_skel(x0 + V / 2, x1 - V / 2, y0 + H / 2, y1 - H / 2, r, k)
    return stroked(s, nib, closed=True)


def lc_oval(p, x0, width):
    """Lowercase o ring: outer box x0..x0+width, -OS..XH+OS."""
    return oval(x0, x0 + width, -OS, XH + OS, p.V, p.H, p.R, p.nib())


def arch(p, x_stem_right, x_flank_center, top=XH, bottom=0, join=None, taper=0.58,
         apex_shift=0.0, flank_bottom=None):
    """The arch of n / h / m: leaves the stem on the left, crosses at the
    top and bends down into a right flank identical to the flank of o.

    x_stem_right: right edge of the left stem
    x_flank_center: centre line of the right stem
    """
    V, H = p.V, p.H
    yt = top + OS - H / 2
    r = p.R
    xr = x_flank_center
    xl = x_stem_right - V / 2           # skeleton enters at the stem centre
    xa = (xl + xr) / 2 + apex_shift
    yj = top - (join if join is not None else 0.50 * top)
    s = Skel(xl, yj)
    # rise out of the stem: tangent starts vertical, bends to the apex
    s.bend((xl, yt), (xa, yt), k=0.66, k2=0.62)
    s.bend((xr, yt), (xr, yt - r))
    yb = bottom if flank_bottom is None else flank_bottom
    s.L(xr, yb)
    sh = stroked(s, p.nib(), taper=[(0.0, taper), (0.30, 1.0), (1.0, 1.0)])
    return sh


def squircle(cx, cy, w, h, k=0.70):
    """A filled lamina 'dot': a small square sheet with bent corners."""
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    def q(a, c, b):
        c1 = (a[0] + (c[0] - a[0]) * k, a[1] + (c[1] - a[1]) * k)
        c2 = (b[0] + (c[0] - b[0]) * k, b[1] + (c[1] - b[1]) * k)
        return ("C", c1, c2, b)
    top, right, bot, left = (cx, y1), (x1, cy), (cx, y0), (x0, cy)
    contour = [("M", top), q(top, (x1, y1), right), q(right, (x1, y0), bot),
               q(bot, (x0, y0), left), q(left, (x0, y1), top)]
    return Shape.of([contour])


def _square(p, xc, y_far, y_corner_edge, end_x, V, H, down):
    """The hook without the bend: a stem and a bar meeting at a right angle."""
    if down:
        return rect(xc - V / 2, y_corner_edge, xc + V / 2, y_far) | rect(min(xc - V / 2, end_x), y_corner_edge, max(xc + V / 2, end_x), y_corner_edge + H)
    return rect(xc - V / 2, y_far, xc + V / 2, y_corner_edge) | rect(min(xc - V / 2, end_x), y_corner_edge - H, max(xc + V / 2, end_x), y_corner_edge)


def hook_down_left(p, xc, ytop, ybase, reach, end_x, nib=None, k=None):
    """A stem that falls and bends left into a flat tail (j, and others).
    ybase is the bottom edge of the tail."""
    from params import WITHOUT
    if "bend" in WITHOUT:
        return _square(p, xc, ytop, ybase, end_x, p.V, p.H, True)
    nib = nib or p.nib()
    H = p.H
    yb = ybase + H / 2
    s = Skel(xc, ytop)
    s.L(xc, yb + reach).bend((xc, yb), (xc - reach, yb), k)
    s.L(end_x, yb)
    return stroked(s, nib)


def hook_down_right(p, xc, ytop, ybase, reach, end_x, nib=None, k=None):
    """A stem that falls and bends right into a flat foot (t, l-tail)."""
    from params import WITHOUT
    if "bend" in WITHOUT:
        return _square(p, xc, ytop, ybase, end_x, p.V, p.H, True)
    nib = nib or p.nib()
    H = p.H
    yb = ybase + H / 2
    s = Skel(xc, ytop)
    s.L(xc, yb + reach).bend((xc, yb), (xc + reach, yb), k)
    s.L(end_x, yb)
    return stroked(s, nib)


def hook_up_right(p, xc, ybottom, ytop, reach, end_x, nib=None, k=None):
    """A stem that rises and bends right into a flat hook (f)."""
    from params import WITHOUT
    if "bend" in WITHOUT and nib is None:
        return _square(p, xc, ybottom, ytop, end_x, p.V, p.H, False)
    nib = nib or p.nib()
    H = p.H
    yt = ytop - H / 2
    s = Skel(xc, ybottom)
    s.L(xc, yt - reach).bend((xc, yt), (xc + reach, yt), k)
    s.L(end_x, yt)
    return stroked(s, nib)


# --- diagonals ----------------------------------------------------------------

def diag(xt, yt, xb, yb, t):
    """A straight stroke between two horizontal cuts. (xt, yt) and (xb, yb)
    are the centres of its top and bottom cuts; t is its true thickness."""
    import math
    dx, dy = xt - xb, yt - yb
    wh = t * math.hypot(dx, dy) / abs(dy)    # width measured along the cut
    return poly((xb - wh / 2, yb), (xb + wh / 2, yb), (xt + wh / 2, yt), (xt - wh / 2, yt))


def vee(p, W, top, t, flat, bottom=0):
    """Two diagonals meeting at a flat-cut vertex at `bottom`."""
    import math
    xc = W / 2
    # the outer edges run from the top corners to the ends of the flat cut
    wl = t * 1.0
    left = _edge_stroke(0, top, xc - flat / 2, bottom, t, outer="left")
    right = _edge_stroke(W, top, xc + flat / 2, bottom, t, outer="right")
    return left | right


def _edge_stroke(x_out_top, yt, x_out_bot, yb, t, outer):
    """A diagonal given by its outer edge; thickness t inward."""
    import math
    dx, dy = x_out_top - x_out_bot, yt - yb
    wh = t * math.hypot(dx, dy) / abs(dy)
    if outer == "left":
        return poly((x_out_bot, yb), (x_out_bot + wh, yb), (x_out_top + wh, yt), (x_out_top, yt))
    return poly((x_out_bot - wh, yb), (x_out_bot, yb), (x_out_top, yt), (x_out_top - wh, yt))




def terminal_cut(xc, yc, x_far, y_top, y_bot):
    """Region removed to open a ring (c, e, C, G). By rule the cut is
    horizontal; with the rule switched off it is radial, square to the
    stroke, as in most grotesks."""
    from params import WITHOUT
    if "cut" in WITHOUT:
        def far(y):
            # extend the ray from the centre through (x_far, y)
            dx, dy = x_far - xc, y - yc
            s = 6.0
            return (xc + dx * s, yc + dy * s)
        return poly((xc, yc), far(y_bot), far(y_top))
    return rect(xc, y_bot, x_far + 200, y_top)
