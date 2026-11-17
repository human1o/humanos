# Lamina

The typeface of Murèlle and Lamelio: a warm, precise grotesk in the
temperature of ABC Diatype. Built on
[Instrument Sans](https://github.com/Instrument/instrument-sans)
(Rodrigo Fuenzalida, Jordan Egstad; SIL OFL 1.1).

**The idea.** Rounds as round as a sheet of stone wrapped around a column,
a rhythm as even as a wall of lamellae. The dots are small tiles of stone.

**Why this base.** Over ninety open grotesks were set on the same sheet as
the ABC Diatype specimen, letter beside letter, and measured: how much each
O, e, s, 0 and 8 fills its box, how long each line runs for the same cap
height. Instrument Sans came closest in roundness (round bowls, horizontally
cut terminals on e c s, single-storey g, straight-tailed y, round 6 and 9).

**What Lamina changes** (each change is a rule, applied the same way to both
masters and to the italic):

1. **Diatype proportions.** Lamina's masters are Instrument Sans at width 97
   and weight 430 (Regular) and 700 (Bold): the stem and set width of
   Diatype. Lowercase is set 9 units per side closer, so the lowercase
   alphabet runs the same length as on the Diatype sheet.
2. **Tiles.** Every dot (i j ż ö . … ! ? : • ÷) is a small stone tile with
   bent corners instead of a sharp square. Upstream's round-dot set (ss01)
   is removed: it argues against the tile.
3. **Forms.** The R whose leg leaves the bowl and drops nearly straight
   (upstream ss05) and $ ¢ with the full stroke (ss12) become the default.
   Q gets a new tail, measured on Diatype: it starts inside the counter (59 %
   of the bowl's width, 30 % of the cap height) and ends under the right
   flank just below the baseline.
4. **Tabular figures by default.** Prices and tables line up with no CSS;
   `pnum` gives proportional figures.
5. **No surprise ligatures.** `->`, `<-` and `www` move from `liga` to the
   optional `dlig`, so what people type in forms stays what they typed.
6. **Names.** New family name, attribution kept as the licence requires.

| | |
| --- | --- |
| Weights | 400–700 variable; static Regular, Medium, SemiBold, Bold |
| Styles | upright and italic |
| Figures | tabular by default (`pnum` for proportional) |
| Characters | 343 (Latin incl. full Polish and è) |
| Files | `fonts/web` (WOFF2 + `lamina.css`), `fonts/ttf` (hinted), `fonts/variable` |
| Licence | SIL Open Font License 1.1 — see `OFL.txt` |

## Use

```css
@import url("lamina/fonts/web/lamina.css");
body { font-family: var(--font-lamina); }
```

## Build

```sh
pip install fontmake fonttools ufoLib2 skia-pathops brotli ttfautohint-py
python3 lamina/src/build.py --italic     # fonts/variable, fonts/ttf, fonts/web
# control fonts for the specimen's "with / without" comparisons
LAMINA_WITHOUT=tile  python3 lamina/src/build.py --out lamina/build/control/notile.ttf
LAMINA_WITHOUT=forms python3 lamina/src/build.py --out lamina/build/control/noforms.ttf
fontmake -g lamina/sources/upstream/InstrumentSans.glyphs -o variable --output-path lamina/build/control/upstream-full.ttf
python3 -c "from fontTools.ttLib import TTFont as T; from fontTools.varLib.instancer import instantiateVariableFont as I
for n in ('notile','noforms'): f=T(f'lamina/build/control/{n}.ttf'); f.flavor='woff2'; f.save(f'lamina/build/control/{n}.woff2')
f=I(T('lamina/build/control/upstream-full.ttf'),{'wdth':100}); f.flavor='woff2'; f.save('lamina/build/control/upstream.woff2')"
python3 lamina/src/specimen.py           # specimen.html, fonts embedded
```

- `sources/upstream/` — Instrument Sans sources (`.glyphs`, upright and italic), licence and authors
- `src/build.py` — interpolates the two masters, applies the edits, compiles
- `src/edits.py` — the Lamina rules: forms, Q tail, tiles, spacing, features, names
- `src/release.py` — variable font, statics, hinting, WOFF2, CSS
