"""Lamina — drawing engine.

Glyphs are drawn as skeletons (centre lines) that are expanded into outlines
with a contrast model, plus plain rectangles for stems and bars. Pieces are
merged and cut with boolean operations (skia-pathops), so every terminal can
be cut exactly horizontally or vertically.
"""
import math

import pathops

from fit import fit_curve

# The bend: handle length of a quarter turn, as a fraction of each leg.
# 0.5523 draws a circle; Lamina's bend is a little squarer, like a sheet of
# stone pressed around a column.
K_BEND = 0.60


def lerp(a, b, t):
    return a + (b - a) * t


def add(p, q):
    return (p[0] + q[0], p[1] + q[1])


def sub(p, q):
    return (p[0] - q[0], p[1] - q[1])


def mul(p, s):
    return (p[0] * s, p[1] * s)


def norm(v):
    d = math.hypot(v[0], v[1])
    return (v[0] / d, v[1] / d) if d else (0.0, 0.0)


# ---------------------------------------------------------------------------
# skeletons
# ---------------------------------------------------------------------------

class Skel:
    """A smooth open (or closed) centre line made of cubic segments."""

    def __init__(self, x, y):
        self.start = (x, y)
        self.cur = (x, y)
        self.segs = []

    def L(self, x, y):
        p0 = self.cur
        p3 = (x, y)
        self.segs.append((p0, lerp_pt(p0, p3, 1 / 3), lerp_pt(p0, p3, 2 / 3), p3))
        self.cur = p3
        return self

    def C(self, c1, c2, p):
        self.segs.append((self.cur, c1, c2, p))
        self.cur = p
        return self

    def bend(self, corner, end, k=None, k2=None):
        """Quarter turn from the current point to `end`; `corner` is where
        the two tangents meet."""
        k = K_BEND if k is None else k
        k2 = k if k2 is None else k2
        p0 = self.cur
        c1 = lerp_pt(p0, corner, k)
        c2 = lerp_pt(end, corner, k2)
        return self.C(c1, c2, end)

    def close(self):
        if self.cur != self.start:
            self.L(*self.start)
        return self


def lerp_pt(p, q, t):
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


def bez(seg, t):
    p0, p1, p2, p3 = seg
    mt = 1 - t
    a, b, c, d = mt * mt * mt, 3 * mt * mt * t, 3 * mt * t * t, t * t * t
    return (a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
            a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1])


def bez_d(seg, t):
    p0, p1, p2, p3 = seg
    mt = 1 - t
    a, b, c = 3 * mt * mt, 6 * mt * t, 3 * t * t
    return (a * (p1[0] - p0[0]) + b * (p2[0] - p1[0]) + c * (p3[0] - p2[0]),
            a * (p1[1] - p0[1]) + b * (p2[1] - p1[1]) + c * (p3[1] - p2[1]))


def seg_len(seg, n=24):
    total, prev = 0.0, seg[0]
    for i in range(1, n + 1):
        q = bez(seg, i / n)
        total += math.hypot(q[0] - prev[0], q[1] - prev[1])
        prev = q
    return total


# ---------------------------------------------------------------------------
# stroke expansion
# ---------------------------------------------------------------------------

def nib(V, H):
    """Contrast model: a stroke travelling vertically is V thick, one
    travelling horizontally is H thick, in between follows an ellipse."""
    def width(tx, ty):
        # tx, ty: unit tangent. Thickness is measured across the stroke.
        return math.sqrt((V * ty) ** 2 + (H * tx) ** 2)
    return width


def _samples(skel, step=3.0):
    """Points along the skeleton with tangent and arc-length position."""
    out = []
    lens = [seg_len(s) for s in skel.segs]
    total = sum(lens)
    acc = 0.0
    for seg, L in zip(skel.segs, lens):
        n = max(4, int(math.ceil(L / step)))
        for i in range(n + (1 if seg is skel.segs[-1] else 0)):
            t = i / n
            p = bez(seg, t)
            d = bez_d(seg, t)
            if math.hypot(*d) < 1e-6:
                d = bez_d(seg, min(1, max(0, t + (1e-3 if t < 0.5 else -1e-3))))
            out.append((p, norm(d), (acc + L * t) / total if total else 0))
        acc += L
    return out


def _taper(taper, s):
    """taper: list of (position 0..1, multiplier); smooth interpolation."""
    if not taper:
        return 1.0
    pts = sorted(taper)
    if s <= pts[0][0]:
        return pts[0][1]
    for (s0, m0), (s1, m1) in zip(pts, pts[1:]):
        if s <= s1:
            u = (s - s0) / (s1 - s0) if s1 > s0 else 1
            u = u * u * (3 - 2 * u)  # smoothstep
            return m0 + (m1 - m0) * u
    return pts[-1][1]


def stroke(skel, width, taper=None, closed=False, tol=0.6):
    """Expand a skeleton into outline contours (list of point lists in the
    form [('M',p), ('C',c1,c2,p) | ('L',p) ...])."""
    smp = _samples(skel)
    if closed:
        smp = smp[:-1] if smp[0][0] == smp[-1][0] else smp
    left, right = [], []
    for p, (tx, ty), s in smp:
        w = width(tx, ty) * _taper(taper, s) / 2
        nx, ny = -ty, tx
        left.append(((p[0] + nx * w, p[1] + ny * w), (tx, ty)))
        right.append(((p[0] - nx * w, p[1] - ny * w), (tx, ty)))
    left, right = _unloop(left), _unloop(right)
    if closed:
        return [_fit_closed(left, tol), _fit_closed(right[::-1], tol)]
    a = _fit_open(left, tol)
    b = _fit_open(right[::-1], tol)
    contour = [("M", left[0])] + a + [("L", right[-1])] + b + [("L", left[0])]
    return [contour]


def _unloop(side):
    """Drop offset points that run backwards against the skeleton: on the
    inside of a bend tighter than half the stroke the offset folds into a
    loop; removing the fold leaves a clean edge."""
    out = [side[0][0]]
    for q, (tx, ty) in side[1:]:
        last = out[-1]
        if (q[0] - last[0]) * tx + (q[1] - last[1]) * ty > 0.02:
            out.append(q)
    if out[-1] != side[-1][0]:
        out.append(side[-1][0])
    return out


def _fit_open(pts, tol):
    pts = _dedupe(pts)
    out = []
    for c in fit_curve(pts, tol):
        p0, p1, p2, p3 = c
        if _is_line(c):
            out.append(("L", p3))
        else:
            out.append(("C", p1, p2, p3))
    return out


def _fit_closed(pts, tol):
    pts = _dedupe(pts)
    pts = pts + [pts[0]]
    segs = _fit_open(pts, tol)
    return [("M", pts[0])] + segs


def _dedupe(pts):
    out = [pts[0]]
    for p in pts[1:]:
        if math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > 0.05:
            out.append(p)
    return out


def _is_line(c, eps=0.35):
    p0, p1, p2, p3 = c
    dx, dy = p3[0] - p0[0], p3[1] - p0[1]
    L = math.hypot(dx, dy)
    if L < 1e-6:
        return True
    for q in (p1, p2):
        d = abs((q[0] - p0[0]) * dy - (q[1] - p0[1]) * dx) / L
        if d > eps:
            return False
    return True


# ---------------------------------------------------------------------------
# shapes (boolean geometry)
# ---------------------------------------------------------------------------

def _to_path(contours):
    path = pathops.Path()
    pen = path.getPen()
    for c in contours:
        for op in c:
            if op[0] == "M":
                pen.moveTo(op[1])
            elif op[0] == "L":
                pen.lineTo(op[1])
            else:
                pen.curveTo(op[1], op[2], op[3])
        pen.closePath()
    return path


class Shape:
    def __init__(self, path=None):
        self.path = path if path is not None else pathops.Path()

    @staticmethod
    def of(contours, evenodd=True):
        p = _to_path(contours)
        p.fillType = pathops.FillType.EVEN_ODD if evenodd else pathops.FillType.WINDING
        p = pathops.simplify(p, fix_winding=True)
        return Shape(p)

    def copy(self):
        p = pathops.Path()
        p.addPath(self.path)
        return Shape(p)

    def __or__(self, other):
        return Shape(pathops.op(self.path, other.path, pathops.PathOp.UNION, fix_winding=True))

    def __sub__(self, other):
        return Shape(pathops.op(self.path, other.path, pathops.PathOp.DIFFERENCE, fix_winding=True))

    def __and__(self, other):
        return Shape(pathops.op(self.path, other.path, pathops.PathOp.INTERSECTION, fix_winding=True))

    def transform(self, a=1, b=0, c=0, d=1, e=0, f=0):
        p = pathops.Path()
        pen = p.getPen()
        from fontTools.pens.transformPen import TransformPen
        self.path.draw(TransformPen(pen, (a, b, c, d, e, f)))
        p = pathops.simplify(p, fix_winding=True)
        return Shape(p)

    def move(self, dx, dy=0):
        return self.transform(1, 0, 0, 1, dx, dy)

    def mirror_x(self, axis):
        return self.transform(-1, 0, 0, 1, 2 * axis, 0)

    def mirror_y(self, axis):
        return self.transform(1, 0, 0, -1, 0, 2 * axis)

    def rot180(self, cx, cy):
        return self.transform(-1, 0, 0, -1, 2 * cx, 2 * cy)

    def bounds(self):
        b = self.path.bounds
        return b if b else (0, 0, 0, 0)

    def empty(self):
        return not self.path.bounds or self.path.bounds == (0, 0, 0, 0)


def union(*shapes):
    out = Shape()
    for s in shapes:
        if s is None:
            continue
        out = out | s
    return out


def rect(x0, y0, x1, y1):
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    return Shape.of([[("M", (x0, y0)), ("L", (x1, y0)), ("L", (x1, y1)), ("L", (x0, y1))]])


def poly(*pts):
    return Shape.of([[("M", pts[0])] + [("L", p) for p in pts[1:]]])


def stroked(skel, width, taper=None, closed=False):
    return Shape.of(stroke(skel, width, taper, closed), evenodd=False)


def halfplane_below(y, x0=-2000, x1=4000):
    return rect(x0, -4000, x1, y)


def halfplane_above(y, x0=-2000, x1=4000):
    return rect(x0, y, x1, 4000)
