#!/usr/bin/env python3
"""Plissé 2 release checks. Every check prints PASS or FAIL; exit 1 on any FAIL.

    python3 plisse/src/check.py
"""
import itertools
import statistics
import subprocess
import sys
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import build as B  # noqa: E402

VF = ROOT / "fonts" / "variable" / "Plisse[opsz,wght].ttf"
STATICS = {s: ROOT / "fonts" / "ttf" / f"Plisse-{s}.ttf" for s, _ in B.WEIGHTS}
FAILS = []
UPM_SCALE = 2048 / 1000


def check(ok, what, detail=""):
    print(("PASS " if ok else "FAIL ") + what + (f"  [{detail}]" if detail else ""))
    if not ok:
        FAILS.append(what)


vf = TTFont(VF)
up = B.pin()                     # Allo as released, ROND 30, wght 400–700: the reference
TAGS = [a.axisTag for a in vf["fvar"].axes]


def norm(font, user):
    """User coordinates -> normalized (with avar), as fontTools and HarfBuzz use them."""
    from fontTools.varLib.models import normalizeLocation
    axes = {a.axisTag: (a.minValue, a.defaultValue, a.maxValue) for a in font["fvar"].axes}
    loc = normalizeLocation(user, axes)
    if "avar" in font:
        from fontTools.varLib.models import piecewiseLinearMap
        for t, seg in font["avar"].segments.items():
            if t in loc:
                loc[t] = piecewiseLinearMap(loc[t], seg)
    return loc


GRID = [{"opsz": o, "wght": w} for o, w in itertools.product((9, 14, 20, 26, 32), (400, 500, 600, 700))]

# 1 — valid files ------------------------------------------------------------------------------
for p in [VF, *STATICS.values()]:
    r = subprocess.run([sys.executable, "-m", "ots", str(p)], capture_output=True, text=True)
    check(r.returncode == 0, f"OTS {p.name}", r.stdout.strip()[-60:])
for p in sorted((ROOT / "fonts" / "web").glob("*.woff2")):
    check(TTFont(p).flavor == "woff2", f"WOFF2 opens {p.name}")

# 2 — names ----------------------------------------------------------------------------------------
VER = f"Version {B.VERSION[0]}.{B.VERSION[1]:03d}"
for s, p in STATICS.items():
    t = TTFont(p)
    n = t["name"]
    legacy = s in ("Regular", "Bold")
    want = {1: "Plissé" if legacy else f"Plissé {s}", 2: s if legacy else "Regular", 4: f"Plissé {s}", 6: f"Plisse-{s}"}
    got = {k: n.getDebugName(k) for k in want}
    check(got == want, f"names {p.name}", str(got))
    check(n.getDebugName(5) == VER and t["OS/2"].achVendID == "PLSE" and t["OS/2"].usWeightClass == dict(B.WEIGHTS)[s],
          f"version, vendor, weight class {p.name}")
    check("fpgm" in t, f"hinted {p.name}")
ids = {1, 2, 3, 4, 6, 16, 17, 25} | {i.subfamilyNameID for i in vf["fvar"].instances}
stale = [r.toUnicode() for r in vf["name"].names if r.nameID in ids and "Allo" in r.toUnicode()]
check(not stale, "no upstream family name in names or instances", "; ".join(stale[:3]))
check("Allo" in vf["name"].getDebugName(0) and "Inter" in vf["name"].getDebugName(0), "upstream credited in copyright")
ax = {a.axisTag: (a.minValue, a.defaultValue, a.maxValue) for a in vf["fvar"].axes}
check(ax == {"opsz": (9, 14, 32), "wght": (400, 400, 700)}, "axes opsz 9–32, wght 400–700, no ROND", str(ax))
check([a.AxisTag for a in vf["STAT"].table.DesignAxisRecord.Axis] == ["opsz", "wght"], "STAT axes opsz, wght")

# 3 — nothing redrawn but the tabular 1 -------------------------------------------------------------
CHANGED = {"one.foot.tf"}
diff = set()
for user in ({"opsz": 9, "wght": 400}, {"opsz": 14, "wght": 400}, {"opsz": 32, "wght": 700}, {"opsz": 20, "wght": 550}):
    gs_p = vf.getGlyphSet(location=user)
    gs_u = up.getGlyphSet(location=user)
    for g in vf.getGlyphOrder():
        a, b = DecomposingRecordingPen(gs_p), DecomposingRecordingPen(gs_u)
        gs_p[g].draw(a)
        gs_u[g].draw(b)
        ra = [(op, tuple((round(x), round(y)) for x, y in args)) for op, args in a.value]
        rb = [(op, tuple((round(x), round(y)) for x, y in args)) for op, args in b.value]
        if ra != rb or round(gs_p[g].width) != round(gs_u[g].width):
            diff.add(g)
check(diff == CHANGED, "every glyph identical to Allo (ROND 30) except the tabular 1", ", ".join(sorted(diff - CHANGED)[:8]))

# 4 — metrics ---------------------------------------------------------------------------------------
top = bot = 0
for user in GRID:
    gs = vf.getGlyphSet(location=user)
    for g in vf.getGlyphOrder():
        b = BoundsPen(gs)
        gs[g].draw(b)
        if b.bounds:
            top, bot = max(top, b.bounds[3]), min(bot, b.bounds[1])
os2 = vf["OS/2"]
check(os2.usWinAscent >= top and os2.usWinDescent >= -bot, "win metrics cover every glyph at every size and weight",
      f"ink {bot:.0f}..{top:.0f}, win -{os2.usWinDescent}..{os2.usWinAscent}")

# 5 — characters -------------------------------------------------------------------------------------
NEED = ("aąbcćdeęfghijklłmnńoóprsśtuwyzźżAĄBCĆDEĘFGHIJKLŁMNŃOÓPRSŚTUWYZŹŻqvxQVXèéàçöüäßÈÉ"
        "0123456789.,:;!?¡¿…-–—'\"‘’‚“”„«»‹›()[]{}/\\|@#&*%‰+−±×÷=<>≤≥≠~^_°′″€$£¢¥"
        "→←↑↓↗↘·•©®™§¶¹²³½¼¾⁄✓")
cmap = vf.getBestCmap()
miss = [c for c in NEED if ord(c) not in cmap]
check(not miss, "characters a Polish stone price list needs", "".join(miss))
for cp in (0x00A0, 0x202F, 0x2009, 0x2007):
    check(cp in cmap, f"space U+{cp:04X}")

# 6 — features ----------------------------------------------------------------------------------------
F = B.hb_font(vf)
t = B.shape(F, "0123456789", {"tnum": True})
check(len({a for _, a, _ in t}) == 1, "tnum: one width for every figure")
check(len({a for _, a, _ in B.shape(F, "0123456789")}) > 1, "default figures proportional")
z = [g for g, *_ in B.shape(F, "0", {"zero": True}) + B.shape(F, "0", {"zero": True, "tnum": True})]
check(z == ["zero.dot", "zero.tf.dot"], "zero feature: the 0 with a stone tile, also in tables", str(z))
check([g for g, *_ in B.shape(F, "1", {"tnum": True})] == ["one.foot.tf"], "tabular 1 is the redrawn footed 1")
for tag, ch, alt in (("ss01", "a", "a.1"), ("cv03", "l", "l.ss02"), ("ss03", "6", "six.ss01")):
    check([g for g, *_ in B.shape(F, ch, {tag: True})] == [alt], f"Allo alternate {tag} kept")

# 7 — figures evenly spaced, the tabular 1 included -------------------------------------------------------
LIMIT = 60 * UPM_SCALE


def optical(font, user, feats):
    loc = norm(font, user)
    gs = font.getGlyphSet(location=user)
    hf = B.hb_font(font, loc, TAGS)
    cap = font["OS/2"].sCapHeight
    depth = 0.12 * cap
    cache = {}

    def sides(n):
        if n not in cache:
            prof = B.profile(gs, n)
            b = BoundsPen(gs)
            gs[n].draw(b)
            x0, _, x1, _ = b.bounds
            adv = gs[n].width
            L, R = [], []
            for yb in range(0, int(cap / 8) + 1):
                l, r = prof.get(yb, (x1, x0))
                L.append(min(l, x0 + depth))
                R.append(min(adv - r, adv - x1 + depth))
            cache[n] = (L, R)
        return cache[n]
    out = {}
    for a in "0123456789":
        for b in "0123456789":
            (n1, adv, _), (n2, _, dx) = B.shape(hf, a + b, feats)
            kern = adv - gs[n1].width + dx
            R, L = sides(n1)[1], sides(n2)[0]
            out[a + b] = statistics.mean(r + l for r, l in zip(R, L)) + kern
    return out


for user in [{"opsz": o, "wght": w} for o, w in itertools.product((9, 14, 32), (400, 700))]:
    for label, feats in (("tabular", {"tnum": True}), ("text", {})):
        o = optical(vf, user, feats)
        rest = [v for k, v in o.items() if "1" not in k]
        ones = [v for k, v in o.items() if "1" in k]
        med = statistics.median(rest)
        worst = max((abs(v - med), k) for k, v in o.items() if "1" in k)
        check(worst[0] <= LIMIT and statistics.pstdev(ones) <= statistics.pstdev(rest) * 1.1 + 4,
              f"figure 1 evenly spaced, {label}, opsz {user['opsz']} wght {user['wght']}",
              f"worst {worst[1]} {worst[0]/UPM_SCALE:+.0f}/1000, '11' {(o['11']-med)/UPM_SCALE:+.0f}, "
              f"'81' {(o['81']-med)/UPM_SCALE:+.0f}")

# 8 — no two letters touch, at masters and between them -----------------------------------------------------
for user in GRID:
    need = B.touching(vf, TAGS, norm(vf, user))
    worst = max(need.items(), key=lambda kv: kv[1]) if need else None
    # interpolation between masters may lose a few units; never a touch
    check(not need or worst[1] <= B.TOUCH - 4, f"no pair touches, opsz {user['opsz']} wght {user['wght']}",
          f"{len(need)} under {B.TOUCH} units" + (f", worst {worst[0]} gap {B.TOUCH - worst[1]:.0f}" if worst else ""))

# 9 — kerning only ever opened, and only where Allo let letters touch -------------------------------------------
for user in ({"opsz": 14, "wght": 400}, {"opsz": 32, "wght": 700}):
    lp, lu = norm(vf, user), norm(up, user)
    hp, hu = B.hb_font(vf, lp, TAGS), B.hb_font(up, lu, TAGS)
    chars = B.GUARD_CHARS
    tighter, opened = [], 0
    for a, b in itertools.product(chars, chars):
        sp, su = B.shape(hp, a + b), B.shape(hu, a + b)
        if len(sp) != 2 or len(su) != 2:
            continue
        d = (sp[0][1] + sp[1][2]) - (su[0][1] + su[1][2])
        if d < 0:
            tighter.append(a + b)
        elif d > 0:
            opened += 1
    check(not tighter, f"no pair tighter than Allo, opsz {user['opsz']} wght {user['wght']}",
          f"{opened} pairs opened; tighter: {' '.join(tighter[:8])}")

# 10 — combining accents land where the precomposed letters have them -------------------------------------------
PAIRS = {"ą": "ą", "ć": "ć", "ę": "ę", "ń": "ń", "ó": "ó", "ś": "ś",
         "ź": "ź", "ż": "ż", "è": "è", "é": "é", "Ó": "Ó", "Ż": "Ż",
         "Ą": "Ą", "Ę": "Ę", "Ś": "Ś"}
for user in ({"opsz": 14, "wght": 400}, {"opsz": 32, "wght": 700}):
    gs = vf.getGlyphSet(location=user)
    hf = B.hb_font(vf, norm(vf, user), TAGS)

    def ink(text):
        x, box = 0, None
        for g, adv, dx in B.shape(hf, text):
            b = BoundsPen(gs)
            gs[g].draw(b)
            if b.bounds:
                bb = (b.bounds[0] + x + dx, b.bounds[1], b.bounds[2] + x + dx, b.bounds[3])
                box = bb if box is None else (min(box[0], bb[0]), min(box[1], bb[1]), max(box[2], bb[2]), max(box[3], bb[3]))
            x += adv
        return box
    worst = max((max(abs(a - b) for a, b in zip(ink(pre), ink(nfd))), pre) for pre, nfd in PAIRS.items())
    check(worst[0] <= 6, f"NFD accents match precomposed, opsz {user['opsz']} wght {user['wght']}",
          f"worst {worst[1]} {worst[0]:.0f} units")

print()
print(f"{len(FAILS)} FAIL" if FAILS else "ALL PASS")
sys.exit(1 if FAILS else 0)
