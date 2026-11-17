"""Lamina — kerning computed from the drawings.

For every pair the white between the two glyphs is measured band by band
(depth-limited, so deep counters do not count as space) and compared with the
white between two straight stems. Only pairs with a diagonal, an open side or
punctuation are kerned; straight and round letters are spaced by their
sidebearings alone.
"""
from fontTools.pens.basePen import BasePen

from params import CAP, XH

STEP = 10


class _Flatten(BasePen):
    def __init__(self):
        super().__init__(None)
        self.edges = []
        self.start = self.cur = None

    def _moveTo(self, p):
        self.start = self.cur = p

    def _lineTo(self, p):
        self.edges.append((self.cur, p))
        self.cur = p

    def _curveToOne(self, a, b, c):
        p0 = self.cur
        n = 12
        prev = p0
        for i in range(1, n + 1):
            t = i / n
            mt = 1 - t
            q = (mt ** 3 * p0[0] + 3 * mt * mt * t * a[0] + 3 * mt * t * t * b[0] + t ** 3 * c[0],
                 mt ** 3 * p0[1] + 3 * mt * mt * t * a[1] + 3 * mt * t * t * b[1] + t ** 3 * c[1])
            self.edges.append((prev, q))
            prev = q
        self.cur = c

    def _qCurveToOne(self, a, b):
        p0 = self.cur
        n = 8
        prev = p0
        for i in range(1, n + 1):
            t = i / n
            mt = 1 - t
            q = (mt * mt * p0[0] + 2 * mt * t * a[0] + t * t * b[0], mt * mt * p0[1] + 2 * mt * t * a[1] + t * t * b[1])
            self.edges.append((prev, q))
            prev = q
        self.cur = b

    def _closePath(self):
        if self.cur != self.start:
            self.edges.append((self.cur, self.start))
        self.cur = self.start


def profiles(shape, y0=-200, y1=900):
    """Left and right ink extremes per horizontal band."""
    pen = _Flatten()
    shape.path.draw(pen)
    left, right = {}, {}
    for y in range(y0, y1 + 1, STEP):
        xs = []
        for (a, b) in pen.edges:
            if (a[1] <= y < b[1]) or (b[1] <= y < a[1]):
                t = (y - a[1]) / (b[1] - a[1])
                xs.append(a[0] + (b[0] - a[0]) * t)
        if xs:
            left[y] = min(xs)
            right[y] = max(xs)
    return left, right


LOWER = set("abcdefghijklmnopqrstuvwxyz") | {"dotlessi", "dotlessj", "germandbls", "ae", "oe", "oslash", "eth", "thorn", "lslash", "dcroat", "mu"}
FIGS = {"zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"}
PLAIN = (set("bcdeghilmnopqsu") | set("BCDEGHIMNOPQSU") | {"zero", "two", "three", "five", "six", "eight", "nine", "dotlessi"})


def zone(name):
    if name in LOWER:
        return "lc"
    if name[:1].isupper() and len(name) <= 2 or name in ("AE", "OE", "Oslash", "Lslash", "Dcroat", "Thorn"):
        return "uc"
    if name in FIGS:
        return "uc"
    return "punct"


def band_for(a, b):
    za, zb = zone(a), zone(b)
    if "punct" in (za, zb):
        z = zb if za == "punct" else za
        if z == "punct":
            return (0, CAP)
        return (0, CAP) if z == "uc" else (0, XH)
    if za == "lc" or zb == "lc":
        return (0, XH)
    return (0, CAP)


def compute(glyphs, names, p):
    prof = {}
    for n in names:
        g = glyphs[n]
        prof[n] = profiles(g["shape"])
    depth = {"lc": p.C * 0.42, "uc": p.CC * 0.36}
    def white(a, b):
        y0, y1 = band_for(a, b)
        la, ra = prof[a]
        lb, rb = prof[b]
        adv = glyphs[a]["advance"]
        D = depth["uc"] if y1 > XH else depth["lc"]
        tot, n = 0.0, 0
        for y in range(y0 + STEP, y1, STEP):
            gap_a = (adv - ra[y]) if y in ra else D
            gap_b = lb[y] if y in lb else D
            g = min(gap_a, D) + min(gap_b, D)
            tot += min(g, 2 * D)
            n += 1
        return tot / max(n, 1)
    ref_lc = white("n", "n")
    ref_uc = white("H", "H")
    ref_mix = white("H", "n")
    kerns = {}
    for a in names:
        for b in names:
            if a in PLAIN and b in PLAIN:
                continue
            w = white(a, b)
            y0, y1 = band_for(a, b)
            ref = ref_uc if y1 > XH and zone(a) != "lc" and zone(b) != "lc" else (ref_mix if "uc" in (zone(a), zone(b)) and "lc" in (zone(a), zone(b)) else ref_lc)
            if "punct" in (zone(a), zone(b)):
                ref = ref_lc if y1 <= XH else ref_uc
            k = (ref - w) * 0.56
            k = max(-140, min(50, k))
            if abs(k) >= 16:
                kerns[(a, b)] = round(k / 2) * 2
    return kerns
