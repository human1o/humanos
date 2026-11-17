# Plissé

The typeface of Murèlle and Lamelio: a warm, precise grotesk made mainly for
interfaces, from 12 px tables to large headlines.

**The idea.** A plissé is a thin sheet folded into an even vertical rhythm.
Its corners are eased like honed stone, and its spacing follows its size the
way a wall of lamellae follows the light.

Font menus show **Plissé**; files, PostScript names and the CSS family use the
ASCII spelling **Plisse**.

## Built on Allo, changed only where nothing can break

Plissé 2 is [Allo](https://github.com/joshpuckett/allo) 1.0.1 by Josh Puckett
(itself begun from [Inter](https://github.com/rsms/inter) by Rasmus
Andersson), taken as released (`sources/upstream/AlloVariable.ttf`) and
changed in six ways. `src/check.py` proves the first claim: every glyph is
identical to Allo at ROND 30 in four sizes and weights, except the tabular 1.

1. **The honed edge.** The roundness axis is pinned at 30 of 100: corners
   eased like the edge of a stone sheet, neither cut sharp (0, cold) nor cast
   round (100). Allo has masters at 30, so this is a designed state.
2. **Size sets the rhythm.** Weight is narrowed to 400–700; optical size
   (9–32) is kept and follows the font size by itself
   (`font-optical-sizing: auto`, the CSS default): open at 12 px, close and
   precise in headlines.
3. **The tabular 1.** Allo's footed tabular 1, its foot widened and the figure
   placed so the white on both its sides matches the other tabular figures,
   measured and chosen in each of its 12 masters, its variations rebuilt from
   them. Optical spacing against the median pair of tabular figures, per 1000
   units: "11" +5 (Allo +68), "81" −7, at Display at most +13.
4. **The tile zero.** The `zero` feature gives Allo's dotted zero (a stone
   tile in the counter) instead of the slashed one, for order numbers and
   codes.
5. **Nothing touches.** Every pair of the Polish and Latin alphabets, figures
   and punctuation is measured at each master and halfway between them; where
   Allo let two glyphs come closer than 32 units (1.6 % em, its own tightest
   designed pairs), one added kerning lookup, variable along opsz and wght,
   opens them. In Display Bold that is ł in "światło", "zmarł", "cło", and
   Ąj, Tè. No pair is ever set tighter than in Allo.
6. **Names and metrics.** New names; Allo and Inter credited. usWin* raised to
   cover Allo's stacked accents (Windows clipped them); line spacing is
   unchanged (USE_TYPO_METRICS).

Allo's own features stay: `ss01` single-storey a, `ss02` disambiguation,
`ss03` open 4 6 9, `cv01`–`cv05`, `liga` shared crossbars (default), `frac`,
`sups`/`subs`, `case`, `calt` (`->` → →, punctuation raised beside capitals).

| | |
| --- | --- |
| Axes | `wght` 400–700, `opsz` 9–32 (automatic) |
| Static | Regular, Medium, SemiBold, Bold (Text optical size), hinted |
| Figures | proportional by default; `tnum` for tables and prices; `zero` for codes |
| Characters | 697: Latin incl. full Polish, Vietnamese; ² ³ ½ ± ≤ ≥ ≠ ✓ arrows; thin, narrow no-break, figure spaces |
| Files | `fonts/web` (WOFF2 + `plisse.css`), `fonts/ttf`, `fonts/variable` |
| Licence | SIL Open Font License 1.1 — see `OFL.txt` |

## Use

```css
@import url("plisse/fonts/web/plisse.css");
body { font-family: var(--font-plisse); font-synthesis: none; }
.price, td.amount { font-variant-numeric: tabular-nums; }
.order-number { font-feature-settings: "zero"; }
```

## Build

```sh
pip install fonttools uharfbuzz brotli skia-pathops ttfautohint-py opentype-sanitizer
python3 plisse/src/build.py      # fonts/variable, fonts/ttf, fonts/web
python3 plisse/src/check.py      # release checks, exit 1 on any failure
python3 plisse/src/specimen.py   # specimen.html, fonts embedded
```

- `sources/upstream/` — Allo 1.0.1 variable font as released, its licence, its commit
- `src/build.py` — pin, tabular 1, zero, touch guard, names, statics, WOFF2, CSS
- `src/check.py` — OTS, names, unchanged glyphs, metrics, characters, features,
  figure spacing, touching pairs, kerning never tighter than Allo, accents
