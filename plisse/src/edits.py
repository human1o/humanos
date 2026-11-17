"""Plissé — the edits applied to both masters.

Every edit is a rule, applied the same way to every glyph and to both
masters, so the two masters stay point-compatible and the weights in between
inherit the idea.
"""
import math

from ufoLib2.objects import Point

# --- the forms ---------------------------------------------------------------------
# Instrument Sans ships alternates; two of them are closer to the idea and to
# Diatype, so they become the default: the R whose leg leaves the bowl and
# drops almost straight (ss05), and $ ¢ with the stroke drawn through (ss12).
# The names are swapped everywhere (outlines, components, kerning groups,
# features), so every accented R follows and kerning stays with its shape.
FORMS = ("ss05", "ss09", "ss12")
DROP_FEATURES = ("ss01", "ss05", "ss09", "ss12")   # ss01 = round dots, against the tile

# Q: Instrument's alternate tail (ss09) crosses the bowl but runs long and
# steep. Plissé's tail is the one measured on Diatype: it starts inside the
# counter, at 59 % of the bowl's width and 30 % of the cap height, and ends
# under the bowl's right flank, just below the baseline.
Q_START = (0.59, 0.30)
import os as _os0
Q_RIGHT_GROUP = _os0.environ.get("PLISSE_QRIGHT", "") == "O"
Q_END = (0.875, -0.05)


def q_tail(font, without):
    if "forms" in without or "Q.ss09" not in font:
        return 0
    g = font["Q.ss09"]
    sh = _shear(font)
    tails = [c for c in g.contours if len(c.points) == 4 and all(p.type == "line" for p in c.points)]
    bowls = [c for c in g.contours if c not in tails]
    if len(tails) != 1 or not bowls:
        return 0
    xs = [p.x - p.y * sh for c in bowls for p in c.points]
    x0, x1 = min(xs), max(xs)
    cap = font.info.capHeight
    pts = tails[0].points
    tw = math.hypot(pts[2].x - pts[1].x, pts[2].y - pts[1].y)
    S = (x0 + Q_START[0] * (x1 - x0), Q_START[1] * cap)
    E = (x0 + Q_END[0] * (x1 - x0), Q_END[1] * cap)
    L = math.hypot(E[0] - S[0], E[1] - S[1])
    d = ((E[0] - S[0]) / L, (E[1] - S[1]) / L)
    n = (-d[1], d[0]) if d[0] * 0 - d[1] > 0 else (d[1], -d[0])
    if n[0] < 0:
        n = (-n[0], -n[1])
    h = tw / 2
    new = [(S[0] - n[0] * h, S[1] - n[1] * h), (E[0] - n[0] * h, E[1] - n[1] * h),
           (E[0] + n[0] * h, E[1] + n[1] * h), (S[0] + n[0] * h, S[1] + n[1] * h)]
    for p, (x, y) in zip(pts, new):
        p.x, p.y = x + y * sh, y
    # the long tail's kerning does not fit the new tail: the Q is spaced by
    # its own sidebearing on the right
    for grp in list(font.groups):
        if grp.startswith("public.kern1.") and "Q.ss09" in font.groups[grp]:
            font.groups[grp] = [n for n in font.groups[grp] if n != "Q.ss09"]
    for (l, r) in [k for k in font.kerning if k[0] == "Q.ss09"]:
        del font.kerning[(l, r)]
    k1 = {n: grp for grp, ms in font.groups.items() if grp.startswith("public.kern1.") for n in ms}
    if Q_RIGHT_GROUP and "O" in k1:
        font.groups[k1["O"]].append("Q.ss09")
    return 1


def _swap_pairs(font):
    # Figures stay proportional by default, as in Diatype: in running text and
    # headlines every figure keeps its own width, so a 1 never stands in a
    # hole. Tables and prices switch to tabular figures with tnum.
    pairs = []
    for name in font.keys():
        parts = name.split(".")
        for ss in FORMS:
            if ss in parts[1:]:
                base = ".".join(p for p in parts if p != ss)
                if base in font:
                    pairs.append((base, name))
    return pairs


def forms(font, without):
    import re
    if "forms" in without:
        return 0
    pairs = _swap_pairs(font)
    m = {}
    for a, b in pairs:
        m[a], m[b] = b, a
    # outlines: each glyph keeps its unicodes, takes its partner's drawing
    snap = {}
    for a, b in pairs:
        for n in (a, b):
            g = font[n]
            snap[n] = ([c for c in g.contours], [c for c in g.components],
                       [x for x in g.anchors], g.width)
    for a, b in pairs:
        for n, o in ((a, b), (b, a)):
            g = font[n]
            cs, comps, anch, w = snap[o]
            g.clearContours(); g.clearComponents(); g.clearAnchors()
            for c in cs: g.contours.append(c)
            for c in comps: g.components.append(c)
            for x in anch: g.anchors.append(x)
            g.width = w
    for g in font:
        for c in g.components:
            if c.baseGlyph in m:
                c.baseGlyph = m[c.baseGlyph]
    side = {pre: {n: g for g, ms in font.groups.items() if g.startswith(pre) for n in ms}
            for pre in ("public.kern1.", "public.kern2.")}
    for k, v in list(font.groups.items()):
        font.groups[k] = [m.get(n, n) for n in v]
    # An alternate that upstream left out of a side's kerning group (the R's
    # left side is the same stem as B's, the $'s left side the S's) takes the
    # default glyph's group for that side, so its spacing keeps its kerning.
    for a, b in pairs:
        for pre, member in side.items():
            if b not in member and a in member and a not in font.groups[member[a]]:
                font.groups[member[a]].append(a)
    keep = []   # glyph-level pairs of the default that its alternate had no own value for
    for a, b in pairs:
        keep += [((a, r), v) for (l, r), v in font.kerning.items() if l == a and (b, r) not in font.kerning]
        keep += [((l, a), v) for (l, r), v in font.kerning.items() if r == a and (l, b) not in font.kerning]
    for (l, r), v in list(font.kerning.items()):
        nl, nr = m.get(l, l), m.get(r, r)
        if (nl, nr) != (l, r):
            del font.kerning[(l, r)]
            font.kerning[(nl, nr)] = v
    for (l, r), v in keep:
        font.kerning[(m.get(l, l) if l not in m else l, m.get(r, r) if r not in m else r)] = v
    t = font.features.text
    for ss in DROP_FEATURES:
        t = re.sub(r"feature %s \{.*?\} %s;\n?" % (ss, ss), "", t, flags=re.S)
        t = re.sub(r"^\s*feature %s;\n" % ss, "", t, flags=re.M)
    if m:
        pat = re.compile(r"(?<![\w.@])(%s)(?![\w.])" % "|".join(re.escape(n) for n in sorted(m, key=len, reverse=True)))
        t = pat.sub(lambda x: m[x.group(1)], t)
    font.features.text = t
    return len(pairs)


# --- the tile ----------------------------------------------------------------------
# Instrument's dots are sharp squares. Plissé's dot is a small tile of stone with
# bent corners: the same corner law as the bowls, at the scale of a dot.
TILE_K = 0.70


def _shear(font):
    """Horizontal shift per unit of height for italic masters."""
    a = font.info.italicAngle or 0
    return math.tan(math.radians(-a))


def _is_dot(contour, shear=0.0):
    pts = contour.points
    if len(pts) != 4 or any(p.type != "line" for p in pts):
        return None
    un = [(p.x - p.y * shear, p.y) for p in pts]
    xs = sorted({round(x, 0) for x, _ in un})
    ys = sorted({round(y, 0) for _, y in un})
    if len(xs) != 2 or len(ys) != 2:
        return None
    w, h = xs[1] - xs[0], ys[1] - ys[0]
    if not (50 <= w <= 260 and 50 <= h <= 260 and 0.72 <= w / h <= 1.38):
        return None
    return xs[0], ys[0], xs[1], ys[1]


def dot_candidates(font):
    """(glyph, contour index) pairs that are dots in this master."""
    sh = _shear(font)
    out = set()
    for name in [n for n in font.keys() if _has_dots(n)]:
        if name in font:
            for i, c in enumerate(font[name].contours):
                if _is_dot(c, sh):
                    out.add((name, i))
    return out


def _area(pts):
    a = 0
    for i in range(len(pts)):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[i]
        a += x0 * y1 - x1 * y0
    return a / 2


DOT_GLYPHS = {"period", "colon", "semicolon", "ellipsis", "exclam", "exclamdown", "question", "questiondown",
              "periodcentered", "dotaccent", "dotaccentcomb", "dotaccentcomb.case", "dotbelowcomb",
              "dieresiscomb", "dieresiscomb.case", "dieresistonos", "divide", "twodotenleader", "bullet"}


def _has_dots(name):
    """Dot glyphs, and ligatures built from i or j (f_i, f_f_i): their dot is
    the same tile."""
    base = name.split(".")[0]
    return name in DOT_GLYPHS or ("_" in base and any(p in ("i", "j") for p in base.split("_")))


def tile(glyph, without, allowed=None, shear=0.0):
    if "tile" in without or not _has_dots(glyph.name):
        return 0
    n = 0
    for idx, c in enumerate(glyph.contours):
        if allowed is not None and (glyph.name, idx) not in allowed:
            continue
        box = _is_dot(c, shear)
        if not box:
            continue
        x0, y0, x1, y1 = box
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        k = TILE_K
        top, right, bot, left = (cx, y1), (x1, cy), (cx, y0), (x0, cy)

        def P(x, y, t=None):
            return Point(x + y * shear, y, t, t is not None)

        def q(a, corner, b):
            return [P(a[0] + (corner[0] - a[0]) * k, a[1] + (corner[1] - a[1]) * k),
                    P(b[0] + (corner[0] - b[0]) * k, b[1] + (corner[1] - b[1]) * k),
                    P(b[0], b[1], "curve")]
        cw = _area([(p.x, p.y) for p in c.points]) < 0
        if cw:
            new = [P(*top, "curve")] + q(top, (x1, y1), right) + q(right, (x1, y0), bot) + q(bot, (x0, y0), left) + q(left, (x0, y1), top)[:-1]
        else:
            new = [P(*top, "curve")] + q(top, (x0, y1), left) + q(left, (x0, y0), bot) + q(bot, (x1, y0), right) + q(right, (x1, y1), top)[:-1]
        c.points = new
        n += 1
    return n


# --- the one ---------------------------------------------------------------------
# In tabular figures every figure gets the same width, and a bare 1 is left
# standing in a hole (Plissé 1.000: "11" carried 175 units more white than an
# average pair of figures). The tabular 1 is therefore drawn the way the
# best tabular sets draw it: Instrument's footed 1, its flag lengthened and its
# foot widened, set where the white on its two sides matches the other figures.
# Measured over every pair of tabular figures (area of white between the
# shapes, per band of the figure height): "11" +14, "81" -2, "18" +1 units
# against the median pair, where Mona Sans has +52/+19 and Inter +175/+77.
# Proportional figures (the default) keep the plain 1 of Diatype.
import os as _os
ONE_FLAG, ONE_FOOT, ONE_SHIFT = (float(v) for v in
                                 _os.environ.get("PLISSE_ONE", "1.3,460,25").split(","))


def tabular_one(font, without, base=None):
    """Rebuild one.tf from upstream's footed tabular 1 (`base` = the
    unedited master it comes from, whose one.tf still has the foot)."""
    if "forms" in without or "one.tf" not in font:
        return 0
    src = (base or font)["one.tf"]
    if len(src.contours) != 2:
        return 0
    stem, foot = src.contours
    pts = [(p.x, p.y, p.type, p.smooth) for p in stem.points]
    sx0, sx1 = pts[0][0], pts[1][0]                 # the stem's left and right edge
    stem_c = (sx0 + sx1) / 2
    fy0, fy1 = min(p.y for p in foot.points), max(p.y for p in foot.points)
    dx = src.width / 2 + ONE_SHIFT - stem_c
    g = font["one.tf"]
    g.clearContours()
    g.clearComponents()
    g.width = src.width
    pen = g.getPointPen()
    pen.beginPath()
    for x, y, typ, smooth in pts:
        if x < sx0 - 0.5:                            # the flag: lengthened away from the stem
            x = sx0 - (sx0 - x) * ONE_FLAG
        pen.addPoint((x + dx, y), typ, smooth)
    pen.endPath()
    pen.beginPath()
    for x, y in ((stem_c - ONE_FOOT / 2, fy0), (stem_c + ONE_FOOT / 2, fy0),
                 (stem_c + ONE_FOOT / 2, fy1), (stem_c - ONE_FOOT / 2, fy1)):
        pen.addPoint((x + dx, y), "line")
    pen.endPath()
    return 1


# --- the kreska -------------------------------------------------------------------
# Polish reads its acute as a kreska: steeper and more compact than the
# Western acute. Plissé's acute stands at 62° (upstream 50°), keeps its
# stroke weight and taper, and keeps its place right of the anchor. The
# grave of Murèlle's è is its mirror, so the two accents rhyme; the double
# acute of ő ű takes the same angle.
KRESKA_ANGLE = 62.0
KRESKA_GLYPHS = ("acutecomb", "gravecomb", "hungarumlautcomb")


def kreska(font, without):
    if "kreska" in without:
        return 0
    sh = _shear(font)
    n = 0
    for name in KRESKA_GLYPHS:
        if name not in font:
            continue
        for c in font[name].contours:
            pts = c.points
            if len(pts) != 4 or any(p.type != "line" for p in pts):
                continue
            un = [(p.x - p.y * sh, p.y) for p in pts]
            y0, y1 = min(y for _, y in un), max(y for _, y in un)
            bot = sorted(i for i in range(4) if abs(un[i][1] - y0) < 1)
            top = sorted(i for i in range(4) if abs(un[i][1] - y1) < 1)
            if len(bot) != 2 or len(top) != 2:
                continue
            bx = [un[i][0] for i in bot]
            tx = [un[i][0] for i in top]
            bc, tc = sum(bx) / 2, sum(tx) / 2
            h = y1 - y0
            old = math.atan2(h, abs(tc - bc))
            new = math.radians(KRESKA_ANGLE)
            if old >= new:
                continue
            k = math.sin(old) / math.sin(new)          # same stroke weight across the stroke
            mid = (bc + tc) / 2
            dx = math.copysign(h / math.tan(new), tc - bc)
            nbc, ntc = mid - dx / 2, mid + dx / 2
            for i in bot:
                x = nbc + (un[i][0] - bc) * k
                pts[i].x, pts[i].y = x + un[i][1] * sh, un[i][1]
            for i in top:
                x = ntc + (un[i][0] - tc) * k
                pts[i].x, pts[i].y = x + un[i][1] * sh, un[i][1]
            n += 1
    return n


# --- the tile zero -----------------------------------------------------------------
# An optional zero (feature "zero") for order numbers and codes: a stone tile
# set in the counter, so 0 and O never meet. Same tile as the period, 70 % of
# its size.
ZERO_TILE = 0.70


def tile_zero(font, without):
    if "tile" in without or "period" not in font:
        return 0
    from fontTools.pens.boundsPen import BoundsPen
    dot = font["period"].contours[0]
    dx0 = [p.x for p in dot.points]
    dy0 = [p.y for p in dot.points]
    dcx, dcy = (min(dx0) + max(dx0)) / 2, (min(dy0) + max(dy0)) / 2
    made = []
    for base in ("zero", "zero.tf"):
        if base not in font:
            continue
        src = font[base]
        name = base + ".zero"
        g = font.newGlyph(name)
        g.width = src.width
        pen = g.getPen()
        src.draw(pen)
        bp = BoundsPen(font)
        src.draw(bp)
        x0, y0, x1, y1 = bp.bounds
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        from ufoLib2.objects import Contour
        pts = [Point(cx + (p.x - dcx) * ZERO_TILE, cy + (p.y - dcy) * ZERO_TILE, p.type, p.smooth)
               for p in dot.points]
        g.contours.append(Contour(points=pts))
        made.append((base, name))
        # the tiled zero kerns exactly like its zero
        for grp, members in font.groups.items():
            if grp.startswith(("public.kern1.", "public.kern2.")) and base in members:
                members.append(name)
        for (l, r), v in list(font.kerning.items()):
            if l == base:
                font.kerning[(name, r)] = v
            if r == base:
                font.kerning[(l, name)] = v
    if made:
        rules = "".join(f"  sub {a} by {b};\n" for a, b in made)
        font.features.text += "\nfeature zero {\n" + rules + "} zero;\n"
    return len(made)


# --- the extras --------------------------------------------------------------------
# Characters a stone price list needs and Instrument Sans does not have:
# m² and m³, ¹, ½ ¼ ¾, ± ≤ ≥ ≠, ′ ″ and the spaces numbers are set with.
# Small figures are drawn from Plissé's own figures, taken from a heavier
# point between the two masters before they are scaled down, so their strokes
# keep the weight of the text around them.
SMALL = 0.62                      # small figure size, share of the cap height
SMALL_WEIGHT = {"Regular": 0.55, "Bold": 1.35}   # where between the masters they are drawn from
DIGIT_NAMES = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")


def _outline(font, name):
    """Point lists of a glyph, components drawn out."""
    from fontTools.pens.pointPen import SegmentToPointPen
    from fontTools.pens.recordingPen import DecomposingRecordingPen
    rec = DecomposingRecordingPen(font)
    font[name].draw(rec)
    from fontTools.pens.recordingPen import RecordingPointPen
    rp = RecordingPointPen()
    rec.replay(SegmentToPointPen(rp))
    return rp.value


def _blend(a, b, t):
    """Interpolate two recorded point-pen outlines of the same structure."""
    out = []
    for (op, args, kw), (op2, args2, kw2) in zip(a, b):
        assert op == op2
        if op == "addPoint":
            (x, y), (x2, y2) = args[0], args2[0]
            out.append((op, ((x + (x2 - x) * t, y + (y2 - y) * t),) + tuple(args[1:]), kw))
        else:
            out.append((op, args, kw))
    return out


def _draw(glyph, rec, transform=(1, 0, 0, 1, 0, 0)):
    from fontTools.pens.transformPen import TransformPointPen
    pen = TransformPointPen(glyph.getPointPen(), transform)
    for op, args, kw in rec:
        getattr(pen, op)(*args, **kw)


def _bounds(rec):
    xs = [a[0][0] for op, a, kw in rec if op == "addPoint"]
    ys = [a[0][1] for op, a, kw in rec if op == "addPoint"]
    return min(xs), min(ys), max(xs), max(ys)


def _rect_contour(glyph, pts):
    pen = glyph.getPointPen()
    pen.beginPath()
    for x, y in pts:
        pen.addPoint((x, y), "line")
    pen.endPath()


def extras(fonts, without=()):
    """fonts: {"Regular": font, "Bold": font}. Adds the same glyphs, with the
    same structure, to both masters."""
    if "extras" in without:
        return 0
    reg, bold = fonts["Regular"], fonts["Bold"]
    made = 0
    for style, font in fonts.items():
        cap = font.info.capHeight
        t = SMALL_WEIGHT[style]
        stroke = _bounds(_outline(font, "minus"))
        stroke = stroke[3] - stroke[1]
        side = 22 if style == "Regular" else 26
        small = {}
        # small figures: superior (top on the cap height) and inferior (on the baseline)
        for d in DIGIT_NAMES:
            rec = _blend(_outline(reg, d), _outline(bold, d), t)
            w = reg[d].width + (bold[d].width - reg[d].width) * t
            x0, _, x1, _ = _bounds(rec)
            adv = round((x1 - x0) * SMALL + 2 * side)
            for kind, dy in (("sups", cap * (1 - SMALL)), ("dnom", 0)):
                name = f"{d}.{kind}"
                g = font.newGlyph(name)
                g.width = adv
                _draw(g, rec, (SMALL, 0, 0, SMALL, side - x0 * SMALL, dy))
                small[name] = g
        for cp, d in ((0x00B9, "one"), (0x00B2, "two"), (0x00B3, "three")):
            name = {"one": "onesuperior", "two": "twosuperior", "three": "threesuperior"}[d]
            g = font.newGlyph(name)
            g.width = small[f"{d}.sups"].width
            g.unicodes = [cp]
            g.components.append(_comp(f"{d}.sups"))
        # fraction slash: from the baseline to the cap height, leaning like the slash
        fs = font.newGlyph("fraction")
        fs.unicodes = [0x2044]
        lean = 0.42 * cap
        th = stroke * 0.95
        _rect_contour(fs, [(0, 0), (th * 1.1, 0), (th * 1.1 + lean, cap), (lean, cap)])
        fs.width = round(th * 1.1 + lean)
        fw = fs.width
        # vulgar fractions: numerator, slash, denominator, set so that nothing touches
        gap = stroke * 1.1
        for cp, name, n, dd in ((0x00BD, "onehalf", "one", "two"), (0x00BC, "onequarter", "one", "four"),
                                (0x00BE, "threequarters", "three", "four")):
            g = font.newGlyph(name)
            g.unicodes = [cp]
            num, den = small[f"{n}.sups"], small[f"{dd}.dnom"]
            nb = _bounds(_outline(font, num.name))
            db = _bounds(_outline(font, den.name))
            # slash x at height y: s + y * lean / cap (left edge)
            k = lean / cap
            s = nb[2] + gap - nb[1] * k                  # left edge clears the numerator at its lowest point
            dx = s + db[3] * k + th * 1.1 + gap - db[0]  # denominator clears the slash at its highest point
            g.components.append(_comp(num.name))
            g.components.append(_comp("fraction", s))
            g.components.append(_comp(den.name, dx))
            g.width = round(dx + den.width)
        # ± ≤ ≥ : the operator raised, a minus as the bar on the baseline
        for cp, name, top in ((0x00B1, "plusminus", "plus"), (0x2264, "lessequal", "less"),
                              (0x2265, "greaterequal", "greater")):
            g = font.newGlyph(name)
            g.unicodes = [cp]
            tb = _bounds(_outline(font, top))
            mb = _bounds(_outline(font, "minus"))
            g.components.append(_comp("minus", 0, -mb[1]))
            g.components.append(_comp(top, 0, stroke + stroke * 1.25 - tb[1]))
            g.width = font[top].width
        # ≠ : equal crossed by a stroke as heavy as the bars
        g = font.newGlyph("notequal")
        g.unicodes = [0x2260]
        g.components.append(_comp("equal"))
        eb = _bounds(_outline(font, "equal"))
        cx, cy = (eb[0] + eb[2]) / 2, (eb[1] + eb[3]) / 2
        h = (eb[3] - eb[1]) + 2 * stroke * 1.6
        lx = h * 0.36
        w2 = stroke * 0.55
        _rect_contour(g, [(cx - lx / 2 - w2, cy - h / 2), (cx - lx / 2 + w2, cy - h / 2),
                          (cx + lx / 2 + w2, cy + h / 2), (cx + lx / 2 - w2, cy + h / 2)])
        g.width = font["equal"].width
        # ′ ″ : the straight quote, leaned like the slash
        q = _outline(font, "quotesingle")
        qb = _bounds(q)
        shear = 0.28
        for cp, name, n in ((0x2032, "minute", 1), (0x2033, "second", 2)):
            g = font.newGlyph(name)
            g.unicodes = [cp]
            step = (qb[2] - qb[0]) * 1.15
            for i in range(n):
                _draw(g, q, (1, 0, shear, 1, -qb[1] * shear + i * step, 0))
            g.width = round(font["quotesingle"].width + (n - 1) * step + (qb[3] - qb[1]) * shear * 0.5)
        # spaces
        space = font["space"].width
        for cp, name, w in ((0x2009, "thinspace", round(space * 0.6)), (0x202F, "narrownbspace", round(space * 0.6)),
                            (0x200A, "hairspace", round(space * 0.3)), (0x2008, "punctuationspace", font["period"].width),
                            (0x2007, "figurespace", font["zero.tf"].width)):
            g = font.newGlyph(name)
            g.unicodes = [cp]
            g.width = w
        made = len(small) + 16
    return made


def _comp(base, dx=0, dy=0):
    from ufoLib2.objects import Component
    return Component(baseGlyph=base, transformation=(1, 0, 0, 1, dx, dy))


# --- measured kerning ------------------------------------------------------------
# Pairs the new forms set tighter than upstream, opened by the amount the
# optical pair check (check.py, 10) measured against Instrument Sans: the
# R's leg now drops almost straight, so the slash comes in under it.
KERN_FIX = {("R", "slash"): {"Regular": 17, "Bold": 26}}


def kern_fix(font, style, without):
    if "forms" in without:
        return 0
    k1 = {n: g for g, ms in font.groups.items() if g.startswith("public.kern1.") for n in ms}
    k2 = {n: g for g, ms in font.groups.items() if g.startswith("public.kern2.") for n in ms}
    for (l, r), vals in KERN_FIX.items():
        L, R = k1.get(l, l), k2.get(r, r)
        font.kerning[(L, R)] = font.kerning.get((L, R), 0) + vals[style]
    return len(KERN_FIX)


# --- the guard -------------------------------------------------------------------
# Setting the lowercase closer must never make two letters touch. Every pair
# of the Polish and Latin alphabet, figures and punctuation is measured
# (outlines and kerning) before and after; a pair the spacing pushed under
# GUARD_GAP gets its old gap back (at most GUARD_GAP), and no pair may come
# closer than GUARD_MIN, not even where upstream had it so. The same pairs are written to both masters, each
# with its own value, so the weights in between interpolate cleanly.
GUARD_GAP = 25
GUARD_MIN = 8
GUARD_CHARS = ("abcdefghijklmnopqrstuvwxyząćęłńóśźżèéàüöä"
               "ABCDEFGHIJKLMNOPQRSTUVWXYZĄĆĘŁŃÓŚŹŻ0123456789.,:;!?()-'\"/&€%²³±×")
_STEP = 4


def _profile(font, name, sh):
    from fontTools.pens.basePen import BasePen
    segs = []

    class Flat(BasePen):
        def _moveTo(s, p): s.c = s.s = p
        def _lineTo(s, p): segs.append((s.c, p)); s.c = p
        def _curveToOne(s, a, b, c):
            p0 = s.c
            for i in range(1, 9):
                u = i / 8; m = 1 - u
                s._lineTo((m**3*p0[0]+3*m*m*u*a[0]+3*m*u*u*b[0]+u**3*c[0], m**3*p0[1]+3*m*m*u*a[1]+3*m*u*u*b[1]+u**3*c[1]))
        def _qCurveToOne(s, a, b):
            p0 = s.c
            for i in range(1, 7):
                u = i / 6; m = 1 - u
                s._lineTo((m*m*p0[0]+2*m*u*a[0]+u*u*b[0], m*m*p0[1]+2*m*u*a[1]+u*u*b[1]))
        def _closePath(s):
            if s.c != s.s: segs.append((s.c, s.s))
    font[name].draw(Flat(font))
    prof = {}
    for (x0, y0), (x1, y1) in segs:
        if y0 == y1:
            continue
        lo, hi = sorted((y0, y1))
        for yb in range(math.ceil(lo / _STEP), math.floor(hi / _STEP) + 1):
            y = yb * _STEP
            if lo <= y < hi:
                x = x0 + (y - y0) * (x1 - x0) / (y1 - y0) - y * sh
                a, b = prof.get(yb, (1e9, -1e9))
                prof[yb] = (min(a, x), max(b, x))
    return prof


def _kern_value(font, l, r, g1, g2):
    k = font.kerning
    L, R = g1.get(l), g2.get(r)
    for pair in ((l, r), (l, R), (L, r), (L, R)):
        if None not in pair and pair in k:
            return k[pair]
    return 0


def pair_gaps(font):
    """{(left, right): narrowest horizontal gap, in units, kerning included}."""
    cmap = {u: g.name for g in font for u in g.unicodes}
    names = [cmap[ord(c)] for c in GUARD_CHARS if ord(c) in cmap]
    g1 = {n: grp for grp, ms in font.groups.items() if grp.startswith("public.kern1.") for n in ms}
    g2 = {n: grp for grp, ms in font.groups.items() if grp.startswith("public.kern2.") for n in ms}
    sh = _shear(font)
    prof = {n: _profile(font, n, sh) for n in names}
    out = {}
    for l in names:
        for r in names:
            kv = _kern_value(font, l, r, g1, g2)
            pl, pr = prof[l], prof[r]
            out[(l, r)] = (min((font[l].width + kv + pr[y][0] - pl[y][1] for y in set(pl) & set(pr)), default=1e9), kv)
    return out


PRE = {}   # id(font) -> pair gaps measured before the spacing edit


def guard_needs(font):
    """{(left, right): kerning that gives the pair back the gap it had before
    the lowercase was set closer (at most GUARD_GAP), and opens any pair that
    touches, upstream included, to GUARD_MIN."""
    pre = PRE.get(id(font), {})
    out = {}
    for pair, (gap, kv) in pair_gaps(font).items():
        before = pre.get(pair, (gap, kv))[0]
        target = min(GUARD_GAP, max(before, GUARD_MIN))
        if gap < target - 0.5:
            out[pair] = round(kv + target - gap)
    return out


def guard(fonts):
    """Open every too-tight pair in all masters; returns the pairs."""
    needs = [guard_needs(f) for f in fonts]
    pairs = set().union(*needs)
    for f, need in zip(fonts, needs):
        g1 = {n: grp for grp, ms in f.groups.items() if grp.startswith("public.kern1.") for n in ms}
        g2 = {n: grp for grp, ms in f.groups.items() if grp.startswith("public.kern2.") for n in ms}
        for l, r in pairs:
            f.kerning[(l, r)] = need.get((l, r), _kern_value(f, l, r, g1, g2))
        f.lib["plisse.stats"]["guard"] = len(pairs)
    return pairs


# --- names -----------------------------------------------------------------------

def rename(font, style):
    from build import FAMILY, FILE, VERSION
    i = font.info
    sty = style
    i.familyName = FAMILY
    i.styleName = sty
    i.styleMapFamilyName = FAMILY
    i.styleMapStyleName = {"Regular": "regular", "Bold": "bold"}.get(sty, "regular")
    i.versionMajor, i.versionMinor = VERSION
    i.copyright = ("Copyright 2026 The Plissé Project Authors. Based on Instrument Sans, "
                   "Copyright 2022 The Instrument Sans Project Authors (https://github.com/Instrument/instrument-sans)")
    i.trademark = None
    i.openTypeNameDesigner = "Plissé: for Murèlle & Lamelio. Instrument Sans: Rodrigo Fuenzalida, Jordan Egstad"
    i.openTypeNameDesignerURL = None
    i.openTypeNameManufacturer = "Plissé Project"
    i.openTypeNameManufacturerURL = None
    i.openTypeNameDescription = ("Plissé: a warm, precise grotesk for Murèlle and Lamelio. A thin sheet "
                                 "folded into an even vertical rhythm: round as stone that bends, even as a "
                                 "wall of lamellae; its dots are small tiles of stone.")
    i.openTypeNameLicense = ("This Font Software is licensed under the SIL Open Font License, Version 1.1. "
                             "This license is available with a FAQ at: https://openfontlicense.org")
    i.openTypeNameLicenseURL = "https://openfontlicense.org"
    i.openTypeOS2VendorID = "PLSE"
    i.openTypeNameUniqueID = None
    i.openTypeNameVersion = None
    i.openTypeNamePreferredFamilyName = None
    i.openTypeNamePreferredSubfamilyName = None
    i.postscriptFontName = f"{FILE}-{sty.replace(' ', '')}"
    i.postscriptFullName = f"{FAMILY} {sty}"
    # drop upstream naming leftovers stored in the lib
    for k in [k for k in font.lib if "name" in k.lower() and "glyph" not in k.lower()]:
        del font.lib[k]


def features(font):
    """Text ligatures only. Upstream turns '->', '<-' and 'www' into single
    glyphs by default, which rewrites what partners type into forms and
    addresses; those move to the optional dlig feature."""
    t = font.features.text
    for pair in ("sub hyphen greater by hyphen_greater.liga;\n", "sub less hyphen by less_hyphen.liga;\n",
                 "sub w w w by w_w_w.liga;\n"):
        if pair in t:
            t = t.replace(pair, "")
            t += "\nfeature dlig {\n" + pair + "} dlig;\n"
    font.features.text = t


# --- spacing ---------------------------------------------------------------------------
# Lowercase is set a little closer, measured against ABC Diatype: at width 97
# its lowercase alphabet runs about 4 % shorter for the same cap height.
# Figures already match and stay as drawn.
TIGHTEN = {"lower": 9, "figure": 0}


def _category(name, font):
    import unicodedata
    g = font[name]
    base = name.split(".")[0]
    cps = list(g.unicodes)
    if not cps and base in font:
        cps = list(font[base].unicodes)
    if not cps and "_" in base:                   # ligatures like f_f_i
        parts = base.split("_")
        if all(p in font and font[p].unicodes and unicodedata.category(chr(font[p].unicodes[0])) == "Ll" for p in parts):
            return "lower"
    for cp in cps:
        cat = unicodedata.category(chr(cp))
        if cat == "Ll":
            return "lower"
        if cat == "Nd":
            return "figure"
    if base in ("fi", "fl", "dotlessi", "dotlessj", "idotless", "jdotless"):
        return "lower"
    return None


def _decompose(font, name):
    from fontTools.pens.recordingPen import DecomposingRecordingPen
    from fontTools.pens.pointPen import SegmentToPointPen
    g = font[name]
    if not g.components:
        return
    rec = DecomposingRecordingPen(font)
    g.draw(rec)
    g.clearContours()
    g.clearComponents()
    rec.replay(g.getPen())


def tighten(font, without):
    if "space" in without:
        return 0
    cats = {n: _category(n, font) for n in font.keys()}
    targets = {n for n, c in cats.items() if c}
    # anything built from a target is drawn out first, so moving the target
    # cannot drag an accent or a ligature part out of place
    for g in list(font):
        if g.components and (g.name in targets or any(c.baseGlyph in targets for c in g.components)):
            _decompose(font, g.name)
    n = 0
    for name in targets:
        g = font[name]
        if g.width <= 0:
            continue
        d = TIGHTEN[cats[name]]
        if not d:
            continue
        g.move((-d, 0))
        for a in g.anchors:
            a.x += 0          # anchors move with g.move
        g.width = max(0, g.width - 2 * d)
        n += 1
    return n


TABULAR_BASE = {}   # id(font) -> unedited master (set by build.py)


def apply(font, style, without=(), dots=None):
    features(font)
    q_tail(font, without)
    stats = {"forms": forms(font, without), "kreska": kreska(font, without), "tile": 0}
    tabular_one(font, without, base=TABULAR_BASE.get(id(font)))
    sh = _shear(font)
    for g in font:
        stats["tile"] += tile(g, without, dots, sh)
    stats["zero"] = tile_zero(font, without)
    kern_fix(font, style, without)
    if "space" not in without:
        PRE[id(font)] = pair_gaps(font)
    stats["tight"] = tighten(font, without)
    rename(font, style)
    font.lib["plisse.stats"] = stats
    return stats
