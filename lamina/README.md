# Lamina

The typeface of Murèlle and Lamelio. *Lamina* is Latin for a thin plate; *lamella*
is its diminutive. Both brands grow out of that word, and so does the typeface.

**The idea.** Every letter stands on the rhythm of the lamella. Where a stroke
turns, it bends like stone; where it ends, it is cut like a slab.

1. **Lamella rhythm.** Round letters have straight flanks. The bowls of o, d, b,
   p, q, c and e stand on vertical sides, with the same light between them as in
   n, u and h, so text pulses evenly like a wall of lamellae.
2. **Bend, don't break.** Every stroke that turns follows one curve law: the
   foot of t, the hook of f, the tails of j, y and g, the flag of 1, the ogonek.
3. **Square cuts.** Every terminal is cut horizontally or vertically, like a sawn
   slab: c, e, a, s, C, G, the apexes of A, V, W, the bar of ł.

| | |
| --- | --- |
| Weights | Regular 400, Medium 500, SemiBold 600, Bold 700 |
| Characters | 337: Western and Central European Latin incl. full Polish and è |
| Features | kerning, tabular figures `tnum`, case punctuation `case` |
| Files | `fonts/web` (WOFF2 + `lamina.css`), `fonts/ttf` (hinted for Windows) |
| Licence | SIL Open Font License 1.1 (commercial use allowed) |

Every outline is drawn from scratch by the code in `src/`; no existing typeface
is used as a base.

## Use

```css
@import url("lamina/fonts/web/lamina.css");
body { font-family: var(--font-lamina); }
td.price { font-variant-numeric: tabular-nums; }
```

## Build

```sh
pip install fonttools skia-pathops brotli ttfautohint-py
python3 lamina/src/build.py --release     # fonts/ttf, fonts/web
python3 lamina/src/specimen.py            # specimen.html
```

- `src/params.py` — metrics, weights, the rhythm (counters), spacing
- `src/geom.py`, `src/fit.py` — skeletons, stroke expansion, boolean cuts
- `src/parts.py` — the shared oval, arch, bend hooks, dot
- `src/lower.py`, `upper.py`, `figures.py`, `punct.py`, `marks.py`, `accented.py` — the glyphs
- `src/kerning.py` — kerning measured from the outlines
- `LAMINA_WITHOUT=flank|bend|cut` builds a control font with one principle off (used by the specimen)
