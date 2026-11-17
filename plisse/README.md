# Plissé

The typeface of Murèlle and Lamelio: a warm, precise grotesk in the
temperature of ABC Diatype, made mainly for interfaces. Built on
[Instrument Sans](https://github.com/Instrument/instrument-sans)
(Rodrigo Fuenzalida, Jordan Egstad; SIL OFL 1.1).

**The idea.** A plissé is a thin sheet folded into an even vertical rhythm.
The letters are round like stone that bends and stand evenly like the
lamellae of a wall; every dot is a small tile of stone.

Font menus show **Plissé**; files, PostScript names and the CSS family use the
ASCII spelling **Plisse**.

**Why this base.** Over ninety open grotesks were set on the same sheet as
the ABC Diatype specimen, letter beside letter, and measured: how much each
O, e, s, 0 and 8 fills its box, how long each line runs for the same cap
height. Instrument Sans came closest in roundness (round bowls, horizontally
cut terminals on e c s, single-storey g, straight-tailed y, round 6 and 9).

**What Plissé changes** (each change is a rule, applied the same way to both
masters):

1. **Diatype proportions.** Plissé's masters are Instrument Sans at width 97
   and weight 430 (Regular) and 700 (Bold): the stem and set width of
   Diatype. Lowercase is set 9 units per side closer, so the lowercase
   alphabet runs the same length as on the Diatype sheet. A guard measures
   every pair of the alphabet, figures and punctuation before and after: no
   pair the spacing tightened may fall under 25 units (it gets its old gap
   back), and no pair may come closer than 8, not even where upstream had it.
2. **Tiles.** Every dot (i j ż ö . … ! ? : • ÷) is a small stone tile with
   bent corners instead of a sharp square. Upstream's round-dot set (ss01)
   is removed: it argues against the tile. The optional `zero` feature sets
   the same tile inside the 0, for order numbers and codes.
3. **Forms.** The R whose leg leaves the bowl and drops nearly straight
   (upstream ss05) and $ ¢ with the full stroke (ss12) become the default.
   Q gets a new tail, measured on Diatype: it starts inside the counter (59 %
   of the bowl's width, 30 % of the cap height) and ends under the right
   flank just below the baseline. The 1 never stands on a foot, not even in
   the tabular figures, where it sits on the axis of the tabular 0.
4. **Polish kreska.** The acute stands at 62° instead of 50°, compact, with
   the same stroke weight; the grave of è mirrors it.
5. **Figures.** Proportional by default, as in Diatype, so a 1 never stands
   in a hole in text and headlines; tables and prices use `tnum`
   (`font-variant-numeric: tabular-nums`).
6. **What a price list needs.** Small figures for m² m³ ¹ and ½ ¼ ¾ are
   drawn from Plissé's own figures, taken from a heavier point between the
   masters before scaling so they keep the weight of the text; ± ≤ ≥ ≠, ′ ″
   and the thin, narrow no-break and figure spaces are added.
7. **No surprise ligatures.** `->`, `<-` and `www` move from `liga` to the
   optional `dlig`, so what people type in forms stays what they typed.
8. **Names.** New family name, attribution kept as the licence requires.

| | |
| --- | --- |
| Weights | 400–700 variable; static Regular, Medium, SemiBold, Bold |
| Styles | upright (no italic, by design) |
| Figures | proportional by default, `tnum` for tables and prices |
| Characters | 361 (Latin incl. full Polish and è; m² m³ ½ ¼ ¾ ± ≤ ≥ ≠ ′ ″; thin, narrow no-break and figure spaces) |
| Files | `fonts/web` (WOFF2 + `plisse.css`), `fonts/ttf` (hinted), `fonts/variable` |
| Licence | SIL Open Font License 1.1 — see `OFL.txt` |

## Use

```css
@import url("plisse/fonts/web/plisse.css");
body { font-family: var(--font-plisse); }
.order-number { font-feature-settings: "zero"; }   /* 0 with a tile */
```

## Build

```sh
pip install fontmake fonttools ufoLib2 skia-pathops brotli ttfautohint-py
python3 plisse/src/build.py              # fonts/variable, fonts/ttf, fonts/web
python3 plisse/src/check.py              # 65 release checks, exit 1 on any failure
# control fonts for the specimen's "with / without" comparisons
PLISSE_WITHOUT=tile  python3 plisse/src/build.py --out plisse/build/control/notile.ttf
PLISSE_WITHOUT=forms python3 plisse/src/build.py --out plisse/build/control/noforms.ttf
PLISSE_WITHOUT=kreska python3 plisse/src/build.py --out plisse/build/control/nokreska.ttf
fontmake -g plisse/sources/upstream/InstrumentSans.glyphs -o variable --output-path plisse/build/control/upstream-full.ttf
python3 -c "from fontTools.ttLib import TTFont as T; from fontTools.varLib.instancer import instantiateVariableFont as I
for n in ('notile','noforms','nokreska'): f=T(f'plisse/build/control/{n}.ttf'); f.flavor='woff2'; f.save(f'plisse/build/control/{n}.woff2')
f=I(T('plisse/build/control/upstream-full.ttf'),{'wdth':100}); f.flavor='woff2'; f.save('plisse/build/control/upstream.woff2')"
python3 plisse/src/specimen.py           # specimen.html, fonts embedded
```

- `sources/upstream/` — Instrument Sans sources (`.glyphs`, upright), licence and authors
- `src/build.py` — interpolates the two masters, applies the edits, compiles
- `src/edits.py` — the Plissé rules: forms, Q tail, one, kreska, tiles, tile zero, spacing, features, names
- `src/release.py` — variable font (overlap flags), statics (overlaps removed), hinting, WOFF2, CSS
- `src/check.py` — release checks: OTS, names, metrics, characters, tiles, features, figures, accents, spacing
