# Lamina

The typeface of Murèlle and Lamelio: a warm, precise grotesk in the
temperature of ABC Diatype. Built on
[Hanken Grotesk](https://github.com/marcologous/hanken-grotesk)
(Alfredo Marco Pradil, Hanken Design Co.; SIL OFL 1.1).

**Why this base.** Over fifty open grotesks were set on the same sheet as the
ABC Diatype specimen and measured. Hanken Grotesk came closest in both shape
(G with spur and bar, straight-legged R, angled t, straight-tailed y,
single-storey g, flagged 1 without a foot, closed 4, round O) and proportion
(capitals within 2 %).

**What Lamina changes** (each change is a rule applied to every glyph, in both
masters and in the italic):

1. **Diatype proportions.** Lowercase and figures are set closer (12 and 14
   units per side), so the lowercase alphabet and the figures run the same
   length as in Diatype for the same cap height — measured within 1–2 % on
   every line of the Diatype sheet. Capitals stay as they are.
2. **Tiles.** Every dot (i j ż ö . … ! ? : • ÷) is a small stone tile with
   bent corners instead of a sharp square.
3. **Flank.** Curves that turn vertical get slightly longer handles: a quiet
   precision in the rounds, not a squaring.
4. **No surprise ligatures.** Upstream turns `->` and `<-` into arrows by
   default; Lamina moves them to the optional `dlig` feature, so what people
   type in forms stays what they typed.
5. **Names.** New family name, attribution kept as the licence requires.

| | |
| --- | --- |
| Weights | 400–700 variable; static Regular, Medium, SemiBold, Bold |
| Styles | upright and italic |
| Figures | tabular by default (`pnum` for proportional) |
| Characters | 617 (Latin incl. full Polish, Vietnamese, Greek basics) |
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
LAMINA_WITHOUT=tile python3 lamina/src/build.py --out lamina/build/control/notile.ttf
LAMINA_WITHOUT=flank,tile,space python3 lamina/src/build.py --out lamina/build/control/hanken.ttf
python3 lamina/src/specimen.py           # specimen.html (uses the two control fonts as woff2)
```

- `sources/upstream/` — Hanken Grotesk sources (`.glyphs`, upright and italic) and licence
- `src/build.py` — interpolates the 400 and 700 masters, applies the edits, compiles
- `src/edits.py` — the Lamina rules: spacing, tiles, flank, features, names
- `src/release.py` — variable font, statics, hinting, WOFF2, CSS
