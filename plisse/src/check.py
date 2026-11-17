#!/usr/bin/env python3
"""Plissé release checks. Every check prints PASS or FAIL; exit code 1 on any FAIL.

    python3 plisse/src/check.py
"""
import io
import math
import subprocess
import sys
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import edits  # noqa: E402

VF = ROOT / "fonts" / "variable" / "Plisse[wght].ttf"
STATICS = {s: ROOT / "fonts" / "ttf" / f"Plisse-{s}.ttf" for s in ("Regular", "Medium", "SemiBold", "Bold")}
WEIGHT = {"Regular": 400, "Medium": 500, "SemiBold": 600, "Bold": 700}
FAILS = []


def check(ok, what, detail=""):
    print(("PASS " if ok else "FAIL ") + what + (f"  [{detail}]" if detail else ""))
    if not ok:
        FAILS.append(what)


def hbfont(tt):
    buf = io.BytesIO()
    tt.save(buf)
    return hb.Font(hb.Face(buf.getvalue()))


def shape(font, text, feats=None):
    b = hb.Buffer()
    b.add_str(text)
    b.guess_segment_properties()
    hb.shape(font, b, feats or {})
    return [(font.glyph_to_string(i.codepoint), p.x_advance, p.x_offset, p.y_offset)
            for i, p in zip(b.glyph_infos, b.glyph_positions)]


def instances():
    for s, w in WEIGHT.items():
        yield s, instancer.instantiateVariableFont(TTFont(VF), {"wght": w})


# 1 — files are valid OpenType (the browser sanitiser) -------------------------------
for p in [VF, *STATICS.values()]:
    r = subprocess.run([sys.executable, "-m", "ots", str(p)], capture_output=True, text=True)
    check(r.returncode == 0, f"OTS {p.name}", r.stdout.strip()[-80:])
for p in sorted((ROOT / "fonts" / "web").glob("*.woff2")):
    check(TTFont(p).flavor == "woff2", f"WOFF2 opens {p.name}")

# 2 — names -------------------------------------------------------------------------------
for s, p in STATICS.items():
    n = TTFont(p)["name"]
    want = {1: "Plissé" if s in ("Regular", "Bold") else f"Plissé {s}",
            2: s if s in ("Regular", "Bold") else "Regular",
            4: f"Plissé {s}", 6: f"Plisse-{s}"}
    got = {k: n.getDebugName(k) for k in want}
    check(got == want, f"names {p.name}", str(got))
    allnames = " ".join(str(r) for r in n.names)
    check("Lamina" not in allnames and "Italic" not in allnames, f"no stale names {p.name}")
    check(n.getDebugName(5).startswith("Version 1.002"), f"version {p.name}", n.getDebugName(5))
    os2 = TTFont(p)["OS/2"]
    check(os2.usWeightClass == WEIGHT[s] and os2.achVendID == "PLSE" and not (os2.fsSelection & 1),
          f"OS/2 {p.name}", f"{os2.usWeightClass} {os2.achVendID} {hex(os2.fsSelection)}")
    check("fpgm" in TTFont(p), f"hinted {p.name}")
vf = TTFont(VF)
check([a.axisTag for a in vf["fvar"].axes] == ["wght"] and
      (vf["fvar"].axes[0].minValue, vf["fvar"].axes[0].maxValue) == (400, 700), "VF axis wght 400–700")
check([a.AxisTag for a in vf["STAT"].table.DesignAxisRecord.Axis] == ["wght"], "STAT has only wght")

# 3 — vertical metrics cover every glyph (no clipping on Windows) ----------------------------
for s, tt in instances():
    gs = tt.getGlyphSet()
    top = bot = 0
    for g in tt.getGlyphOrder():
        b = BoundsPen(gs)
        gs[g].draw(b)
        if b.bounds:
            top, bot = max(top, b.bounds[3]), min(bot, b.bounds[1])
    os2 = tt["OS/2"]
    check(os2.usWinAscent >= top and os2.usWinDescent >= -bot, f"win metrics cover glyphs {s}",
          f"ink {bot:.0f}..{top:.0f}, win -{os2.usWinDescent}..{os2.usWinAscent}")

# 4 — characters a Polish B2B panel uses ------------------------------------------------------
NEED = ("aąbcćdeęfghijklłmnńoóprsśtuwyzźżAĄBCĆDEĘFGHIJKLŁMNŃOÓPRSŚTUWYZŹŻqvxQVXèéàçöüäßÈÉ"
        "0123456789.,:;!?¡¿…-–—'\"‘’‚“”„«»‹›()[]{}/\\|@#&*%‰+−±×÷=<>≤≥≠~^_°′″€$£¢¥zł"
        "→←↑↓↗↘·•©®™§¶¹²³½¼¾⁄")
cmap = vf.getBestCmap()
miss = [c for c in NEED if ord(c) not in cmap]
check(not miss, "characters present", "".join(miss))
for cp, label in ((0x00A0, "no-break space"), (0x202F, "narrow no-break space"), (0x2009, "thin space"),
                  (0x2007, "figure space")):
    check(cp in cmap, f"{label} U+{cp:04X}")
if 0x00A0 in cmap:
    check(vf["hmtx"][cmap[0xA0]][0] == vf["hmtx"][cmap[0x20]][0], "no-break space as wide as space")

# 5 — no sharp square dot left anywhere --------------------------------------------------------
import ufoLib2  # noqa: E402
for m in ("Regular", "Bold"):
    f = ufoLib2.Font.open(ROOT / "build" / "masters" / f"Plisse-{m}.ufo")
    reach = set()
    left = sorted({g.name for g in f for c in g.contours if edits._is_dot(c)})
    # glyphs that text can reach: cmap + every GSUB output in the final font
    gsub_out = set()
    for lk in vf["GSUB"].table.LookupList.Lookup:
        for st in lk.SubTable:
            st = getattr(st, "ExtSubTable", st)
            for attr in ("mapping", "alternates", "ligatures"):
                d = getattr(st, attr, None)
                if not d:
                    continue
                for v in d.values():
                    if isinstance(v, str):
                        gsub_out.add(v)
                    elif isinstance(v, list):
                        for x in v:
                            gsub_out.add(x if isinstance(x, str) else x.LigGlyph)
    reach = set(cmap.values()) | gsub_out
    bad = [n for n in left if n in reach]
    check(not bad, f"every reachable dot is a tile ({m})", ",".join(bad))

# 6 — features --------------------------------------------------------------------------------------
F = hbfont(vf)
check([g for g, *_ in shape(F, "fi")] == ["f_i"], "fi ligature")
check([g for g, *_ in shape(F, "->")] == ["hyphen", "greater"], "-> stays as typed")
check([g for g, *_ in shape(F, "www")] == ["w", "w", "w"], "www stays as typed")
check(len(shape(F, "->", {"dlig": True})) == 1, "-> arrow only with dlig")
d = shape(F, "0123456789")
t = shape(F, "0123456789", {"tnum": True})
check(len({a for _, a, *_ in t}) == 1, "tnum: all figures one width", str({a for _, a, *_ in t}))
check(len({a for _, a, *_ in d}) > 1, "default figures proportional")
z = shape(F, "0", {"zero": True}) + shape(F, "0", {"zero": True, "tnum": True})
check([g for g, *_ in z] == ["zero.zero", "zero.tf.zero"], "zero feature, also with tnum", str(z))
check(shape(F, "0", {"zero": True})[0][1] == shape(F, "0")[0][1], "tiled zero keeps its width")
tf = [n for n in vf.getGlyphOrder() if n.endswith(".tf") or ".tf." in n]
fig = [n for n in tf if n.split(".")[0] in edits.DIGIT_NAMES]
check(len({vf["hmtx"][n][0] for n in fig}) == 1, "tabular figure glyphs share one width",
      str(sorted({vf['hmtx'][n][0] for n in fig})))

# 7 — figures are evenly spaced: no figure (the 1 above all) stands in a hole ----------------------
# Optical spacing: mean white between two figures per band of the cap height,
# each side's depth clamped at 12 % of the cap height. A pair with a 1 may not
# carry more than ONE_LIMIT units of white more (or less) than the median pair,
# and pairs with a 1 may not spread wider than pairs without it.
import statistics  # noqa: E402
ONE_LIMIT = 60


def optical(tt, feats):
    gs = tt.getGlyphSet()
    Fi = hbfont(tt)
    cap = tt["OS/2"].sCapHeight
    depth = 0.12 * cap

    class G:
        def __getitem__(self, k):
            return gs[k]
    cache = {}

    def sides(n):
        if n not in cache:
            prof = edits._profile(G(), n, 0)
            b = BoundsPen(gs)
            gs[n].draw(b)
            x0, _, x1, _ = b.bounds
            adv = tt["hmtx"][n][0]
            L, R = [], []
            for yb in range(0, int(cap / edits._STEP) + 1):
                l, r = prof.get(yb, (x1, x0))
                L.append(min(l, x0 + depth))
                R.append(min(adv - r, adv - x1 + depth))
            cache[n] = (L, R)
        return cache[n]
    out = {}
    for a in "0123456789":
        for b in "0123456789":
            sh = shape(Fi, a + b, feats)
            (n1, adv, _, _), (n2, _, dx, _) = sh
            kern = adv - tt["hmtx"][n1][0] + dx
            R, L = sides(n1)[1], sides(n2)[0]
            out[a + b] = statistics.mean(r + l for r, l in zip(R, L)) + kern
    return out


for s, tt in instances():
    for label, feats in (("tabular", {"tnum": True}), ("text", {})):
        o = optical(tt, feats)
        rest = [v for k, v in o.items() if "1" not in k]
        ones = [v for k, v in o.items() if "1" in k]
        med = statistics.median(rest)
        worst = max(((abs(v - med), k) for k, v in o.items() if "1" in k))
        check(worst[0] <= ONE_LIMIT and statistics.pstdev(ones) <= statistics.pstdev(rest) * 1.1 + 2,
              f"figure 1 evenly spaced, {label} ({s})",
              f"worst {worst[1]} {worst[0]:+.0f}, '11' {o['11'] - med:+.0f}, '81' {o['81'] - med:+.0f}; "
              f"spread with 1 {statistics.pstdev(ones):.0f} vs without {statistics.pstdev(rest):.0f}")

# 8 — combining accents land where the precomposed letters have them --------------------------------
PAIRS = {"ą": "ą", "ć": "ć", "ę": "ę", "ń": "ń", "ó": "ó", "ś": "ś",
         "ź": "ź", "ż": "ż", "è": "è", "é": "é", "Ó": "Ó", "Ż": "Ż",
         "Ą": "Ą", "Ę": "Ę", "Ś": "Ś"}
for s, tt in instances():
    Fi = hbfont(tt)
    gs = tt.getGlyphSet()

    def ink(text):
        x = 0
        box = None
        for g, adv, dx, dy in shape(Fi, text):
            b = BoundsPen(gs)
            gs[g].draw(b)
            if b.bounds:
                bb = (b.bounds[0] + x + dx, b.bounds[1] + dy, b.bounds[2] + x + dx, b.bounds[3] + dy)
                box = bb if box is None else (min(box[0], bb[0]), min(box[1], bb[1]),
                                              max(box[2], bb[2]), max(box[3], bb[3]))
            x += adv
        return box
    worst = max((max(abs(a - b) for a, b in zip(ink(pre), ink(nfd))), pre) for pre, nfd in PAIRS.items())
    check(worst[0] <= 3, f"NFD accents match precomposed ({s})", f"worst {worst[1]} {worst[0]:.0f} units")

# 9 — no two letters touch; spacing never tighter than upstream where it matters ----------------------
work = Path("/tmp")
for s, tt in instances():
    sys.path.insert(0, str(ROOT / "src"))
    g = edits  # noqa
    from fontTools.pens.basePen import BasePen  # noqa: F401
    Fi = hbfont(tt)
    gs = tt.getGlyphSet()
    names = {c: tt.getBestCmap().get(ord(c)) for c in edits.GUARD_CHARS}
    prof = {}

    def P(n):
        if n not in prof:
            class G:  # adapter: edits._profile wants font[name].draw
                def __getitem__(self, k):
                    return gs[k]
            prof[n] = edits._profile(G(), n, 0)
        return prof[n]
    worst = (1e9, "")
    for a in edits.GUARD_CHARS:
        for b in edits.GUARD_CHARS:
            sh = shape(Fi, a + b)
            if len(sh) != 2:
                continue
            (g1, adv, _, _), (g2, _, dx, _) = sh
            p1, p2 = P(g1), P(g2)
            gap = min((adv + dx + p2[y][0] - p1[y][1] for y in set(p1) & set(p2)), default=1e9)
            worst = min(worst, (gap, a + b))
    check(worst[0] >= edits.GUARD_MIN - 1.5, f"no pair touches ({s})", f"closest {worst[1]!r} {worst[0]:.0f} units")

# 10 — no pair is spaced worse than in Instrument Sans ------------------------------------------------
# Same optical measure over every pair of letters, figures and punctuation,
# each pair against the median of its kind (lower-lower, upper-lower, ...),
# compared with upstream at the same width and weight. A pair may not become
# more uneven than upstream by more than 25 units. Pairs with characters
# upstream does not have (² ³) cannot be compared and are left out.
UP = ROOT / "build" / "control" / "upstream-full.ttf"
if not UP.exists():
    UP.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["fontmake", "-g", str(ROOT / "sources" / "upstream" / "InstrumentSans.glyphs"), "-o", "variable",
                    "--output-path", str(UP)], check=True, capture_output=True)
PCH = "abcdefghijklmnopqrstuvwxyząćęłńóśźżèé" + "ABCDEFGHIJKLMNOPQRSTUVWXYZĄĆĘŁŃÓŚŹŻ" + "0123456789" + ".,:;!?()-/&€%$¢"


def kind(c):
    return "l" if c.islower() else "U" if c.isupper() else "d" if c.isdigit() else "p"


def pair_optical(tt):
    gs = tt.getGlyphSet()
    Fi = hbfont(tt)
    cap = tt["OS/2"].sCapHeight
    depth = 0.12 * cap

    class G:
        def __getitem__(self, k):
            return gs[k]
    cache = {}

    def sides(n):
        if n not in cache:
            prof = edits._profile(G(), n, 0)
            b = BoundsPen(gs)
            gs[n].draw(b)
            x0, _, x1, _ = b.bounds or (0, 0, 0, 0)
            adv = tt["hmtx"][n][0]
            L, R = [], []
            for yb in range(int(-0.25 * cap / edits._STEP), int(cap / edits._STEP) + 1):
                l, r = prof.get(yb, (x1, x0))
                L.append(min(l, x0 + depth))
                R.append(min(adv - r, adv - x1 + depth))
            cache[n] = (L, R)
        return cache[n]
    out = {}
    for a in PCH:
        for b in PCH:
            sh = shape(Fi, a + b)
            if len(sh) != 2:
                continue
            (n1, adv, _, _), (n2, _, dx, _) = sh
            R, L = sides(n1)[1], sides(n2)[0]
            out[a + b] = statistics.mean(r + l for r, l in zip(R, L)) + adv - tt["hmtx"][n1][0] + dx
    groups = {}
    for k, v in out.items():
        groups.setdefault(kind(k[0]) + kind(k[1]), []).append(v)
    med = {g: statistics.median(v) for g, v in groups.items()}
    return {k: v - med[kind(k[0]) + kind(k[1])] for k, v in out.items()}


for (s, tt), uw in zip(instances(), (430, 520, 610, 700)):
    P = pair_optical(tt)
    U = pair_optical(instancer.instantiateVariableFont(TTFont(UP), {"wght": uw, "wdth": 97}))
    worse = sorted(((abs(P[k]) - abs(U[k]), k) for k in P if k in U), reverse=True)
    bad = [w for w in worse if w[0] > 25]
    check(not bad, f"no pair spaced worse than upstream ({s})",
          ", ".join(f"{k!r} {d:+.0f}" for d, k in bad[:8]) or f"largest {worse[0][1]!r} {worse[0][0]:+.0f}")

print()
print(f"{len(FAILS)} FAIL" if FAILS else "ALL PASS")
sys.exit(1 if FAILS else 0)
