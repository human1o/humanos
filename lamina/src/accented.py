"""Lamina — accented letters (composites) and the extra drawn letters."""
import math

from geom import Skel, poly, rect, stroked
from params import ASC, CAP, DESC, OS, OSC, XH
from parts import lc_oval, oval
from registry import G, glyph


def mix(a, b, w):
    return a + (b - a) * w


# --- drawn extras ---------------------------------------------------------------------

def _stroke_bar(x0, x1, yc, rise, t):
    """A slanted bar with vertical cuts at both ends (ł, Ł): its edges
    run parallel, its ends are cut like a sawn slat."""
    return poly((x0, yc - rise / 2 - t / 2), (x1, yc + rise / 2 - t / 2), (x1, yc + rise / 2 + t / 2), (x0, yc - rise / 2 + t / 2))


@glyph("lslash", 0x142)
def lslash(p):
    from lower import l_
    V = p.V
    sh = l_(p).shape
    reach = mix(96, 100, p.w)
    bar = _stroke_bar(-reach + V / 2, V / 2 + reach, ASC * 0.50, mix(120, 130, p.w), p.H * 1.02)
    return G(sh | bar, 22, 22)


@glyph("Lslash", 0x141)
def Lslash(p):
    from upper import L_
    V = p.VC
    sh = L_(p).shape
    reach = mix(118, 124, p.w)
    bar = _stroke_bar(V / 2 - reach, V / 2 + reach, CAP * 0.47, mix(140, 150, p.w), p.HC * 1.02)
    return G(sh | bar, 26, 30)


@glyph("dcroat", 0x111)
def dcroat(p):
    from lower import d_
    sh = d_(p).shape
    b = sh.bounds()
    V, H = p.V, p.H
    xs = b[2] - V
    y = ASC - mix(118, 126, p.w)
    return G(sh | rect(xs - mix(96, 104, p.w), y - H, b[2] + mix(60, 56, p.w), y), "R", 24)


@glyph("Dcroat", 0x110, aliases=(0xD0,))
def Dcroat(p):
    from upper import D_
    sh = D_(p).shape
    V, H = p.VC, p.HC
    y = CAP / 2
    return G(sh | rect(-mix(96, 100, p.w), y - H / 2, V + mix(120, 110, p.w), y + H / 2), 26, "RC")


@glyph("oslash", 0xF8)
def oslash(p):
    from lower import o_
    sh = o_(p).shape
    b = sh.bounds()
    t = p.V * 0.92
    d = _cut_diag(b[0] - 4, -56, b[2] + 4, XH + 56, t)
    return G(sh | d, "R", "R")


@glyph("Oslash", 0xD8)
def Oslash(p):
    from upper import O_
    sh = O_(p).shape
    b = sh.bounds()
    t = p.VC * 0.92
    d = _cut_diag(b[0] - 4, -64, b[2] + 4, CAP + 64, t)
    return G(sh | d, "RC", "RC")


def _cut_diag(x0, y0, x1, y1, t):
    from parts import diag
    wh = t * math.hypot(x1 - x0, y1 - y0) / (y1 - y0)
    return diag(x1 - wh / 2, y1, x0 + wh / 2, y0, t)


def _arch_e(p):
    """The e, trimmed to the centre of its left flank, so that it grows out
    of a stem like the arch of n."""
    from lower import e_
    sh = e_(p).shape
    return sh & rect(p.V / 2, -500, 2000, 2000)


@glyph("ae", 0xE6)
def ae(p):
    from lower import a_
    a = a_(p).shape
    b = a.bounds()
    xr = b[2] - p.V / 2               # a's stem centre
    e = _arch_e(p).move(xr - p.V / 2)
    return G(a | e, 34, 34)


@glyph("oe", 0x153)
def oe(p):
    from lower import o_
    o = o_(p).shape
    b = o.bounds()
    xr = b[2] - p.V / 2
    e = _arch_e(p).move(xr - p.V / 2)
    return G(o | e, "R", 34)


@glyph("AE", 0xC6)
def AE(p):
    from upper import E_, h_width, tdiag
    V, Hh = p.VC, p.HC
    t = tdiag(p)
    W0 = h_width(p) * 0.74
    e = E_(p).shape.move(W0)
    wh = t * math.hypot(W0, CAP) / CAP
    d = poly((0, 0), (wh, 0), (W0 + V * 0.6, CAP), (W0 + V * 0.6 - wh, CAP))
    bar = CAP * 0.28
    xbar = W0 * (bar / CAP) + wh * 0.5
    sh = e | (d & rect(0, 0, W0 + V, CAP)) | rect(xbar, bar - Hh / 2, W0 + V, bar + Hh / 2)
    return G(sh, 6, 40)


@glyph("OE", 0x152)
def OE(p):
    from upper import E_, cap_oval, o_cap_width
    W = o_cap_width(p)
    cut = W * 0.62
    o = cap_oval(p, 0, W) & rect(-10, -100, cut, 1000)
    e = E_(p).shape.move(cut - p.VC / 2)
    return G(o | e, "RC", 40)


@glyph("germandbls", 0xDF)
def germandbls(p):
    V, H = p.V, p.H
    W = mix(470, 520, p.w)
    xs = V / 2
    xr = W - V / 2
    yt = ASC + OS - H / 2
    mid = XH * 0.70
    r_u = mix(140, 144, p.w)
    xr_u = xr - 30
    s1 = Skel(xs, 0).L(xs, yt - r_u).bend((xs, yt), ((xs + xr_u) / 2, yt), k=0.62)
    s1.bend((xr_u, yt), (xr_u, yt - r_u * 0.95)).L(xr_u, mid + r_u * 0.7)
    s1.bend((xr_u, mid), (xr_u - r_u * 0.8, mid)).L(V * 0.5, mid)
    up = stroked(s1, p.nib())
    yb = -OS + H / 2
    r_l = (mid - yb) * 0.46
    s2 = Skel(V * 0.5, mid).L(xr - r_l * 1.05, mid).bend((xr, mid), (xr, mid - r_l)).L(xr, yb + r_l)
    s2.bend((xr, yb), (xr - r_l * 1.05, yb)).L(V + mix(70, 80, p.w), yb)
    lo = stroked(s2, p.nib())
    return G(up | lo, "S", "R")


@glyph("eth", 0xF0)
def eth(p):
    V, H = p.V, p.H
    from lower import o_width
    W = o_width(p)
    ring = lc_oval(p, 0, W)
    xr = W - V / 2
    yt = ASC - H / 2
    r = mix(150, 156, p.w)
    s = Skel(xr, XH * 0.5).L(xr, yt - r).bend((xr, yt), (xr - r, yt)).L(xr - r - mix(70, 60, p.w), yt)
    hook = stroked(s, p.nib())
    bar = _stroke_bar(xr - 150, xr + 70, ASC - 230, 90, H)
    return G(ring | hook | bar, "R", "R")


@glyph("thorn", 0xFE)
def thorn(p):
    from lower import bowl_with_stem
    sh = bowl_with_stem(p, "left", ASC, DESC)
    return G(sh, "S", "R")


@glyph("Thorn", 0xDE)
def Thorn(p):
    from upper import cap_bowl
    V, Hh = p.VC, p.HC
    W = p.CC * 0.86 + 2 * V
    bowl = cap_bowl(p, V / 2, W, CAP * 0.82, CAP * 0.20)
    return G(rect(0, 0, V, CAP) | bowl, "SC", "RC")


@glyph("mu", 0xB5)
def mu(p):
    from lower import u_
    sh = u_(p).shape
    b = sh.bounds()
    return G(sh | rect(b[0], DESC, b[0] + p.V, XH * 0.5), "S", "S")


# --- composites ------------------------------------------------------------------------

LC = {
    # base -> list of (suffix-name, unicode, marks)
}

COMPOSITES = []


def comp(name, uni, base, *marks):
    COMPOSITES.append((name, uni, base, list(marks)))


def _build_table():
    top = [("grave", "gravecomb"), ("acute", "acutecomb"), ("circumflex", "circumflexcomb"),
           ("tilde", "tildecomb"), ("dieresis", "dieresiscomb"), ("ring", "ringcomb"),
           ("macron", "macroncomb"), ("breve", "brevecomb"), ("caron", "caroncomb"),
           ("dotaccent", "dotaccentcomb"), ("hungarumlaut", "hungarumlautcomb")]
    import unicodedata
    def u(ch):
        return ord(ch)
    table = {
        "a": "àáâãäåāă", "e": "èéêëēėě", "i": "ìíîïī", "o": "òóôõöōő", "u": "ùúûüūůű",
        "y": "ýÿ", "n": "ñńň", "c": "ćčċ", "s": "śš", "z": "źžż", "r": "ŕř", "g": "ğġ",
        "A": "ÀÁÂÃÄÅĀĂ", "E": "ÈÉÊËĒĖĚ", "I": "ÌÍÎÏĪİ", "O": "ÒÓÔÕÖŌŐ", "U": "ÙÚÛÜŪŮŰ",
        "Y": "ÝŸ", "N": "ÑŃŇ", "C": "ĆČĊ", "S": "ŚŠ", "Z": "ŹŽŻ", "R": "ŔŘ", "G": "ĞĠ",
        "D": "Ď", "T": "Ť", "L": "Ĺ", "l": "ĺ",
    }
    for base, chars in table.items():
        for ch in chars:
            dec = unicodedata.decomposition(ch).split()
            mark_cp = int(dec[1], 16)
            mark = {0x300: "gravecomb", 0x301: "acutecomb", 0x302: "circumflexcomb", 0x303: "tildecomb",
                    0x308: "dieresiscomb", 0x30A: "ringcomb", 0x304: "macroncomb", 0x306: "brevecomb",
                    0x30C: "caroncomb", 0x307: "dotaccentcomb", 0x30B: "hungarumlautcomb"}[mark_cp]
            b = base
            if base == "i":
                b = "dotlessi"
            name = unicodedata.name(ch)
            gname = _agl(ch)
            if base.isupper():
                comp(gname, ord(ch), b, (mark + ".case", "top"))
            elif base == "l":
                comp(gname, ord(ch), b, (mark, "top_asc"))
            else:
                comp(gname, ord(ch), b, (mark, "top"))
    # caron as apostrophe
    comp("dcaron", 0x10F, "d", ("caroncomb.alt", "alt"))
    comp("lcaron", 0x13E, "l", ("caroncomb.alt", "alt"))
    comp("tcaron", 0x165, "t", ("caroncomb.alt", "alt"))
    comp("Lcaron", 0x13D, "L", ("caroncomb.alt", "altcap"))
    # ogonek
    for b, ch in (("a", "ą"), ("e", "ę"), ("i", "į"), ("u", "ų"), ("A", "Ą"), ("E", "Ę"), ("I", "Į"), ("U", "Ų")):
        comp(_agl(ch), ord(ch), b, ("ogonekcomb", "ogonek"))
    # cedilla
    for b, ch in (("c", "ç"), ("C", "Ç"), ("s", "ş"), ("S", "Ş"), ("t", "ţ"), ("T", "Ţ")):
        comp(_agl(ch), ord(ch), b, ("cedillacomb", "bottom"))
    # comma below
    for b, ch in (("s", "ș"), ("S", "Ș"), ("t", "ț"), ("T", "Ț"), ("k", "ķ"), ("K", "Ķ"),
                  ("l", "ļ"), ("L", "Ļ"), ("n", "ņ"), ("N", "Ņ"), ("r", "ŗ"), ("R", "Ŗ"), ("G", "Ģ")):
        comp(_agl(ch), ord(ch), b, ("commaaccentcomb", "bottom"))
    comp("gcommaaccent", 0x123, "g", ("commaturnedabovecomb", "top"))
    comp("iogonek.dot", None, "i")  # placeholder never used


def _agl(ch):
    from fontTools.agl import UV2AGL
    cp = ord(ch)
    return UV2AGL.get(cp, "uni%04X" % cp)


_build_table()
COMPOSITES[:] = [c for c in COMPOSITES if c[0] != "iogonek.dot"]
# į keeps its dot: build it on i, not on the dotless form
