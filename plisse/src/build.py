#!/usr/bin/env python3
"""Plissé 2 — the typeface of Murèlle and Lamelio, built on Allo.

    python3 plisse/src/build.py        # fonts/variable, fonts/ttf, fonts/web
    python3 plisse/src/check.py        # release checks

Allo (Josh Puckett, OFL; from Inter) is taken as released and changed only in
ways that cannot break it: an axis pinned, a range narrowed, one figure redrawn
from its own masters, one feature pointed at another of Allo's own glyphs,
kerning added where letters touch, new names. Nothing else is redrawn.

  1. ROND pinned at 30: corners eased like the honed edge of a stone sheet,
     neither cut sharp (0) nor cast round (100). Allo has masters at 30.
  2. wght narrowed to 400–700, opsz kept (9–32): the font follows its size,
     open at 12 px in a table, close and precise in a headline.
  3. Tabular 1: Allo's footed 1, its foot widened and the figure placed so
     the white on its two sides matches the other tabular figures; the foot
     and position are measured and chosen in each of its 12 masters.
  4. The zero feature gives the 0 with a dot (Allo's cv05): a stone tile in
     the counter, for order numbers and codes.
  5. Kerning wherever two letters touch (Polish ł, ą/ę + j, T + è ...),
     variable along opsz and wght, added to Allo's own.
  6. Names: Plissé; Allo and Inter credited as the licence requires.
"""
import io
import itertools
import math
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

import uharfbuzz as hb
from fontTools.otlLib import builder as otl
from fontTools.pens.basePen import BasePen
from fontTools.pens.recordingPen import DecomposingRecordingPointPen
from fontTools.pens.ttGlyphPen import TTGlyphPointPen
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import otTables as ot
from fontTools.ttLib.tables.TupleVariation import TupleVariation
from fontTools.varLib import instancer
from fontTools.varLib.models import VariationModel
from fontTools.varLib.varStore import OnlineVarStoreBuilder

ROOT = Path(__file__).resolve().parent.parent
UPSTREAM = ROOT / "sources" / "upstream" / "AlloVariable.ttf"
FONTS = ROOT / "fonts"
BUILD = ROOT / "build"

FAMILY = "Plissé"      # what font menus show
FILE = "Plisse"        # ASCII: files, PostScript names, CSS family
VERSION = (2, 0)
VENDOR = "PLSE"

ROND = 30
WGHT = (400, 700)
STATIC_OPSZ = 14       # the static TTFs are the Text design
WEIGHTS = [("Regular", 400), ("Medium", 500), ("SemiBold", 600), ("Bold", 700)]

TOUCH = 32             # no two glyphs closer than this (units of 2048, ~1.6 % em): Allo's own
                       # tightest designed pairs (2nd percentile at Display Bold)
GUARD_CHARS = ("abcdefghijklmnopqrstuvwxyząćęłńóśźżèéàüöäß"
               "ABCDEFGHIJKLMNOPQRSTUVWXYZĄĆĘŁŃÓŚŹŻÈÉ0123456789.,:;!?¡¿()[]{}-–—'\"‘’“”„«»/\\&@#€$%²³°*")


# --- geometry helpers -------------------------------------------------------------------------
def glyph_points(font, name, loc):
    """Contours as [[x, y, segmentType], ...] at a normalized location, components drawn out."""
    gs = font.getGlyphSet(location=loc, normalized=True)
    rec = DecomposingRecordingPointPen(gs)
    gs[name].drawPoints(rec)
    contours, cur = [], None
    for op, args, kw in rec.value:
        if op == "beginPath":
            cur = []
        elif op == "addPoint":
            typ = args[1] if len(args) > 1 else kw.get("segmentType")
            cur.append([args[0][0], args[0][1], typ])
        elif op == "endPath":
            contours.append(cur)
    return contours, gs[name].width


def master_grid(font, names):
    """The product of every peak each axis takes in these glyphs' variations."""
    tags = [a.axisTag for a in font["fvar"].axes]
    peaks = {t: {0.0} for t in tags}
    for n in names:
        for v in font["gvar"].variations.get(n, []):
            for t, (lo, pk, hi) in v.axes.items():
                peaks[t].add(round(pk, 6))
    return tags, [dict(zip(tags, c)) for c in itertools.product(*(sorted(peaks[t]) for t in tags))]


class Flat(BasePen):
    def __init__(self, gs, step=8):
        super().__init__(gs)
        self.segs, self.step = [], step

    def _moveTo(self, p):
        self.c = self.s = p

    def _lineTo(self, p):
        self.segs.append((self.c, p))
        self.c = p

    def _curveToOne(self, a, b, c):
        p0 = self.c
        for i in range(1, 9):
            t = i / 8
            m = 1 - t
            self._lineTo((m**3*p0[0]+3*m*m*t*a[0]+3*m*t*t*b[0]+t**3*c[0], m**3*p0[1]+3*m*m*t*a[1]+3*m*t*t*b[1]+t**3*c[1]))

    def _qCurveToOne(self, a, b):
        p0 = self.c
        for i in range(1, 7):
            t = i / 6
            m = 1 - t
            self._lineTo((m*m*p0[0]+2*m*t*a[0]+t*t*b[0], m*m*p0[1]+2*m*t*a[1]+t*t*b[1]))

    def _closePath(self):
        if self.c != self.s:
            self.segs.append((self.c, self.s))

    def profile(self):
        prof = {}
        st = self.step
        for (x0, y0), (x1, y1) in self.segs:
            if y0 == y1:
                continue
            lo, hi = sorted((y0, y1))
            for yb in range(math.ceil(lo / st), math.floor(hi / st) + 1):
                y = yb * st
                if lo <= y < hi:
                    x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                    a, b = prof.get(yb, (1e9, -1e9))
                    prof[yb] = (min(a, x), max(b, x))
        return prof


def profile(gs, name):
    pen = Flat(gs)
    gs[name].draw(pen)
    return pen.profile()


def hb_font(font, loc=None, tags=None):
    buf = io.BytesIO()
    font.save(buf)
    f = hb.Font(hb.Face(buf.getvalue()))
    if loc is not None:
        f.set_var_coords_normalized([loc[t] for t in tags])
    return f


def shape(f, text, feats=None):
    b = hb.Buffer()
    b.add_str(text)
    b.guess_segment_properties()
    hb.shape(f, b, feats or {})
    return [(f.glyph_to_string(i.codepoint), p.x_advance, p.x_offset) for i, p in zip(b.glyph_infos, b.glyph_positions)]


# --- 1, 2: pin -----------------------------------------------------------------------------------
def pin():
    f = instancer.instantiateVariableFont(TTFont(UPSTREAM), {"ROND": ROND, "wght": WGHT})
    buf = io.BytesIO()
    f.save(buf)                       # reload: a fully compiled font, every table consistent
    buf.seek(0)
    return TTFont(buf)


def stat(font):
    """STAT for the two axes left: optical size and weight."""
    from fontTools.otlLib.builder import buildStatTable
    buildStatTable(font, [
        dict(tag="opsz", name="Optical size", values=[
            dict(value=9, name="Small", rangeMinValue=9, rangeMaxValue=11),
            dict(value=14, name="Text", flags=0x2, rangeMinValue=11, rangeMaxValue=20),
            dict(value=32, name="Display", rangeMinValue=20, rangeMaxValue=32)]),
        dict(tag="wght", name="Weight", values=[
            dict(value=w, name=s, **({"flags": 0x2, "linkedValue": 700} if w == 400 else {}))
            for s, w in WEIGHTS]),
    ], elidedFallbackName="Regular")


# --- 3: the tabular 1 --------------------------------------------------------------------------
def edit_one(contours, foot_l, foot_r, shift):
    pts = contours[0]
    top = max(p[1] for p in pts)
    foot_top = max(p[1] for p in pts if p[1] < top * 0.2)
    edge = sorted(p[0] for p in pts if abs(p[1] - foot_top) < 0.5)
    stem_l, stem_r = edge[1], edge[-2]
    for p in pts:
        if p[1] <= foot_top + 0.5:
            if p[0] < stem_l - 1:
                p[0] -= foot_l
            elif p[0] > stem_r + 1:
                p[0] += foot_r
    for c in contours:
        for p in c:
            p[0] += shift
    return contours


def _sides(contours, adv, cap):
    gs_like = None
    pen = Flat(gs_like)
    for c in contours:
        _draw_points(pen, c)
    prof = pen.profile()
    xs = [p[0] for c in contours for p in c]
    x0, x1 = min(xs), max(xs)
    depth = 0.12 * cap
    L, R = [], []
    for yb in range(0, int(cap / 8) + 1):
        l, r = prof.get(yb, (x1, x0))
        L.append(min(l, x0 + depth))
        R.append(min(adv - r, adv - x1 + depth))
    return L, R


def _draw_points(pen, contour):
    """Draw one TrueType contour ([x, y, type]) on a segment pen."""
    from fontTools.pens.pointPen import PointToSegmentPen
    pp = PointToSegmentPen(pen)
    pp.beginPath()
    for x, y, typ in contour:
        pp.addPoint((x, y), typ)
    pp.endPath()


DIGITS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
ONE_MIN_SIDE = 52      # the foot keeps at least this much of the cell free (units of 2048)


def fit_one(font, loc, contours, adv):
    """Foot and position of the tabular 1 at one master, chosen so that the
    white between it and every other tabular figure matches the median pair."""
    cap = font["OS/2"].sCapHeight
    S = {}
    for d in DIGITS:
        if d != "one":
            c, a = glyph_points(font, d + ".tf", loc)
            S[d] = _sides(c, a, cap)
    pair = {(a, b): statistics.mean(r + l for r, l in zip(S[a][1], S[b][0]))
            for a in S for b in S}
    med = statistics.median(pair.values())
    best = None
    for fl, fr, sh in itertools.product(range(0, 161, 20), range(0, 121, 20), range(-40, 81, 10)):
        c = edit_one([[list(p) for p in cc] for cc in contours], fl, fr, sh)
        xs = [p[0] for p in c[0]]
        if min(xs) < ONE_MIN_SIDE or adv - max(xs) < ONE_MIN_SIDE:
            continue
        L1, R1 = _sides(c, adv, cap)
        devs = [statistics.mean(r + l for r, l in zip(R1, L1)) - med]
        for d in S:
            devs.append(statistics.mean(r + l for r, l in zip(S[d][1], L1)) - med)
            devs.append(statistics.mean(r + l for r, l in zip(R1, S[d][0])) - med)
        cost = sum(v * v for v in devs) + 0.5 * (fl * fl + fr * fr)   # the least change that works
        if best is None or cost < best[0]:
            best = (cost, fl, fr, sh, c)
    return best


def tabular_one(font, name="one.foot.tf"):
    """Redraw `name` in each of its masters and rebuild its variations, the
    way a variable font is compiled from masters."""
    tags, locs = master_grid(font, [name] + [c.glyphName for c in font["glyf"][name].components]
                             if font["glyf"][name].isComposite() else [name])
    masters = []
    fits = []
    for loc in locs:
        contours, adv = glyph_points(font, name, loc)
        cost, fl, fr, sh, contours = fit_one(font, loc, contours, adv)
        fits.append((loc, fl, fr, sh))
        masters.append((contours, adv))
    font.lib_one = fits
    base_i = next(i for i, l in enumerate(locs) if all(v == 0 for v in l.values()))
    contours0, adv0 = masters[base_i]
    pen = TTGlyphPointPen(None)
    for c in contours0:
        pen.beginPath()
        for x, y, typ in c:
            pen.addPoint((round(x), round(y)), typ)
        pen.endPath()
    glyph = pen.glyph()
    font["glyf"][name] = glyph
    glyph.recalcBounds(font["glyf"])
    lsb = glyph.xMin
    font["hmtx"][name] = (font["hmtx"][name][0], lsb)

    def flat(contours, adv):
        pts = [(x, y) for c in contours for x, y, _ in c]
        return pts + [(0, 0), (adv, 0), (0, 0), (0, 0)]   # + phantom points
    model = VariationModel(locs, axisOrder=tags)
    vals = [flat(c, a) for c, a in masters]
    n = len(vals[0])
    columns = []
    for i in range(n):
        xs = model.getDeltas([v[i][0] for v in vals])
        ys = model.getDeltas([v[i][1] for v in vals])
        columns.append(list(zip(xs, ys)))
    tvs = []
    for k, support in enumerate(model.supports):
        if not support:
            continue
        coords = [(round(columns[i][k][0]), round(columns[i][k][1])) for i in range(n)]
        if any(c != (0, 0) for c in coords):
            tvs.append(TupleVariation({t: support[t] for t in support}, coords))
    font["gvar"].variations[name] = tvs
    return len(locs)


# --- 4: the zero feature points at the dotted zero ------------------------------------------------
def zero_dot(font):
    gsub = font["GSUB"].table
    idx = {li for fr in gsub.FeatureList.FeatureRecord if fr.FeatureTag == "zero" for li in fr.Feature.LookupListIndex}
    for li in idx:
        for st in gsub.LookupList.Lookup[li].SubTable:
            st = getattr(st, "ExtSubTable", st)
            st.mapping = {"zero": "zero.dot", "zero.tf": "zero.tf.dot"}
    return len(idx)


# --- 5: kerning wherever two glyphs touch ----------------------------------------------------------
def touching(font, tags, loc, chars=GUARD_CHARS):
    """{(left, right): units needed to open the pair to TOUCH} at one location."""
    gs = font.getGlyphSet(location=loc, normalized=True)
    hf = hb_font(font, loc, tags)
    cmap = font.getBestCmap()
    names = [cmap[ord(c)] for c in chars if ord(c) in cmap]
    bbox, prof = {}, {}
    from fontTools.pens.boundsPen import BoundsPen
    for n in set(names):
        b = BoundsPen(gs)
        gs[n].draw(b)
        bbox[n] = b.bounds
    need = {}
    for a, b in itertools.product(chars, chars):
        sh = shape(hf, a + b)
        if len(sh) != 2:
            continue
        (g1, adv, _), (g2, _, dx) = sh
        if g1 not in bbox:
            bbox[g1] = None
        b1, b2 = bbox.get(g1), bbox.get(g2)
        if not b1 or not b2:
            continue
        if adv + dx + b2[0] - b1[2] >= TOUCH:   # boxes alone keep them apart
            continue
        for g in (g1, g2):
            if g not in prof:
                prof[g] = profile(gs, g)
        p1, p2 = prof[g1], prof[g2]
        gap = min((adv + dx + p2[y][0] - p1[y][1] for y in set(p1) & set(p2)), default=1e9)
        if gap < TOUCH:
            need[(g1, g2)] = TOUCH - gap
    return need


def guard(font):
    """Add one kerning lookup, variable along the font's axes, that opens
    every touching pair to TOUCH at every master and nowhere else."""
    names = [n for n in font.getGlyphOrder()]
    tags, locs = master_grid(font, names)
    # the kerning is checked and set also halfway between the glyph masters,
    # where interpolated outlines can come closer than at either master
    axis_vals = {t: sorted({l[t] for l in locs}) for t in tags}
    for t_ in tags:
        v = axis_vals[t_]
        axis_vals[t_] = sorted(set(v) | {round((a + b) / 2, 6) for a, b in zip(v, v[1:])})
    locs = [dict(zip(tags, c)) for c in itertools.product(*(axis_vals[t_] for t_ in tags))]
    per = [touching(font, tags, loc) for loc in locs]
    pairs = sorted(set().union(*per))
    if not pairs:
        return 0
    model = VariationModel(locs, axisOrder=tags)
    vb = OnlineVarStoreBuilder(tags)
    vb.setModel(model)
    entries = {}
    for pr in pairs:
        vals = [math.ceil(p.get(pr, 0)) for p in per]
        base, var_idx = vb.storeMasters(vals)
        entries[pr] = (base, var_idx)
    new = vb.finish()
    # merge the new variation data into the font's own store
    store = font["GDEF"].table.VarStore
    reg0 = len(store.VarRegionList.Region)
    store.VarRegionList.Region.extend(new.VarRegionList.Region)
    store.VarRegionList.RegionCount = len(store.VarRegionList.Region)
    major0 = len(store.VarData)
    for vd in new.VarData:
        vd.VarRegionIndex = [i + reg0 for i in vd.VarRegionIndex]
        vd.VarRegionCount = len(vd.VarRegionIndex)
        store.VarData.append(vd)
    store.VarDataCount = len(store.VarData)
    values = {}
    for pr, (base, var_idx) in entries.items():
        v = otl.buildValue({"XAdvance": base})
        if var_idx is not None and var_idx != 0xFFFFFFFF:
            dev = ot.Device()
            dev.StartSize = (var_idx >> 16) + major0
            dev.EndSize = var_idx & 0xFFFF
            dev.DeltaFormat = 0x8000
            v.XAdvDevice = dev
        values[pr] = (v, None)
    subtables = otl.buildPairPosGlyphs(values, font.getReverseGlyphMap())
    lookup = otl.buildLookup(subtables, flags=0)
    gpos = font["GPOS"].table
    gpos.LookupList.Lookup.append(lookup)
    gpos.LookupList.LookupCount = len(gpos.LookupList.Lookup)
    li = len(gpos.LookupList.Lookup) - 1
    for fr in gpos.FeatureList.FeatureRecord:
        if fr.FeatureTag == "kern":
            fr.Feature.LookupListIndex.append(li)
            fr.Feature.LookupCount = len(fr.Feature.LookupListIndex)
    return len(pairs)


# --- 6: names ---------------------------------------------------------------------------------------
def rename(font):
    name = font["name"]
    ver = f"{VERSION[0]}.{VERSION[1]:03d}"
    texts = {
        0: ("Copyright 2026 The Plissé Project Authors. Based on Allo, Copyright 2026 Josh Puckett "
            "(https://joshpuckett.me), which began from Inter, Copyright (c) 2016 The Inter Project "
            "Authors (https://github.com/rsms/inter)."),
        1: FAMILY, 2: "Regular", 3: f"{ver};{VENDOR};{FILE}-Regular", 4: f"{FAMILY} Regular",
        5: f"Version {ver}", 6: f"{FILE}-Regular",
        8: "Plissé Project",
        9: "Plissé: for Murèlle & Lamelio. Allo: Josh Puckett. Inter: Rasmus Andersson.",
        10: ("Plissé: a warm, precise grotesk for Murèlle and Lamelio. A thin sheet folded into an even "
             "vertical rhythm: its corners eased like honed stone, its size followed by its spacing."),
        13: ("This Font Software is licensed under the SIL Open Font License, Version 1.1. "
             "This license is available with a FAQ at: https://openfontlicense.org"),
        14: "https://openfontlicense.org",
        25: FILE,
    }
    for nid in (7, 11, 12, 16, 17, 18, 21, 22):
        name.removeNames(nameID=nid)
    for nid, text in texts.items():
        name.removeNames(nameID=nid)
        name.setName(text, nid, 3, 1, 0x409)
    # any other record still carrying the upstream family name
    for rec in name.names:
        s = rec.toUnicode()
        if "Allo" in s and rec.nameID not in texts:
            rec.string = s.replace("Allo Variable", FAMILY).replace("Allo", FAMILY)
    font["OS/2"].achVendID = VENDOR
    font["head"].fontRevision = VERSION[0] + VERSION[1] / 1000


def win_metrics(font):
    """usWin* cover the highest and lowest ink at every size and weight, so
    Windows never clips a stacked accent. Line spacing is unchanged: the font
    sets USE_TYPO_METRICS, and browsers and Windows space lines by typo."""
    from fontTools.pens.boundsPen import BoundsPen
    tags = [a.axisTag for a in font["fvar"].axes]
    top = bot = 0
    for combo in itertools.product(*((a.minValue, a.defaultValue, a.maxValue) for a in font["fvar"].axes)):
        gs = font.getGlyphSet(location=dict(zip(tags, combo)))
        for g in font.getGlyphOrder():
            b = BoundsPen(gs)
            gs[g].draw(b)
            if b.bounds:
                top, bot = max(top, b.bounds[3]), min(bot, b.bounds[1])
    os2 = font["OS/2"]
    os2.usWinAscent = max(os2.usWinAscent, math.ceil(top))
    os2.usWinDescent = max(os2.usWinDescent, math.ceil(-bot))
    assert os2.fsSelection & 0x80


def overlap_flags(font):
    glyf = font["glyf"]
    for n in font.getGlyphOrder():
        g = glyf[n]
        if g.isComposite():
            g.components[0].flags |= 0x0400
        elif g.numberOfContours > 0:
            g.flags[0] |= 0x40


def woff2(src, dst):
    f = TTFont(src)
    f.flavor = "woff2"
    f.save(dst)


def statics(vf_path):
    out = []
    for style, w in WEIGHTS:
        f = instancer.instantiateVariableFont(TTFont(vf_path), {"opsz": STATIC_OPSZ, "wght": w},
                                              overlap=instancer.OverlapMode.REMOVE)
        name = f["name"]
        legacy = style in ("Regular", "Bold")
        fam = FAMILY if legacy else f"{FAMILY} {style}"
        for nid in (1, 2, 3, 4, 6, 16, 17, 25):
            name.removeNames(nameID=nid)
        name.setName(fam, 1, 3, 1, 0x409)
        name.setName(style if legacy else "Regular", 2, 3, 1, 0x409)
        name.setName(f"{VERSION[0]}.{VERSION[1]:03d};{VENDOR};{FILE}-{style}", 3, 3, 1, 0x409)
        name.setName(f"{FAMILY} {style}", 4, 3, 1, 0x409)
        name.setName(f"{FILE}-{style}", 6, 3, 1, 0x409)
        if not legacy:
            name.setName(FAMILY, 16, 3, 1, 0x409)
            name.setName(style, 17, 3, 1, 0x409)
        os2 = f["OS/2"]
        os2.usWeightClass = w
        sel = os2.fsSelection & ~0b1100001   # clear ITALIC, BOLD, REGULAR
        os2.fsSelection = sel | (0x20 if style == "Bold" else 0x40) | 0x80
        f["head"].macStyle = 1 if style == "Bold" else 0
        f["post"].isFixedPitch = 0
        raw = BUILD / f"{FILE}-{style}.ttf"
        f.save(raw)
        dst = FONTS / "ttf" / f"{FILE}-{style}.ttf"
        from ttfautohint import ttfautohint
        ttfautohint(in_file=str(raw), out_file=str(dst), no_info=True)
        woff2(dst, FONTS / "web" / f"{FILE}-{style}.woff2")
        out.append(dst)
    return out


CSS = """/* Plissé {ver}: one variable font, weight 400–700, optical size 9–32.
   The optical size follows the font size by itself (font-optical-sizing: auto).
   ?v= makes browsers fetch a new release. SIL Open Font License 1.1. */
@font-face {{
  font-family: "Plisse";
  src: url("Plisse[opsz,wght].woff2?v={ver}") format("woff2");
  font-weight: 400 700;
  font-style: normal;
  font-display: swap;
}}

:root {{
  --font-plisse: "Plisse", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}

/* Prices, tables, totals: every figure the same width, columns line up. */
.plisse-tabular {{ font-variant-numeric: tabular-nums; }}
/* Order numbers and codes: 0 with a stone tile inside, never read as O. */
.plisse-code {{ font-feature-settings: "zero"; }}
"""


def build(out=None, without=()):
    BUILD.mkdir(exist_ok=True)
    f = pin()
    stats = {}
    if "one" not in without:
        stats["one masters"] = tabular_one(f)
        stats["one fits"] = [(round(l["opsz"], 2), round(l["wght"], 2), fl, fr, sh) for l, fl, fr, sh in f.lib_one]
    if "zero" not in without:
        stats["zero"] = zero_dot(f)
    if "guard" not in without:
        stats["kerned pairs"] = guard(f)
    stat(f)
    win_metrics(f)
    rename(f)
    overlap_flags(f)
    if out:
        f.save(out)
        return out, stats
    for d in ("ttf", "web", "variable"):
        if (FONTS / d).exists():
            shutil.rmtree(FONTS / d)
        (FONTS / d).mkdir(parents=True)
    vf = FONTS / "variable" / f"{FILE}[opsz,wght].ttf"
    f.save(vf)
    woff2(vf, FONTS / "web" / f"{FILE}[opsz,wght].woff2")
    statics(vf)
    ver = f"{VERSION[0]}.{VERSION[1]:03d}"
    (FONTS / "web" / "plisse.css").write_text(CSS.format(ver=ver))
    for d in ("web", "ttf", "variable"):
        shutil.copy(ROOT / "OFL.txt", FONTS / d / "OFL.txt")
    return vf, stats


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="variable font only, to this path (control builds)")
    ap.add_argument("--without", default="", help="comma list: one, zero, guard")
    a = ap.parse_args()
    path, stats = build(a.out, set(filter(None, a.without.split(","))))
    print(path, stats)
    if not a.out:
        for p in sorted(FONTS.rglob("*")):
            if p.is_file():
                print(p.relative_to(ROOT), p.stat().st_size)
