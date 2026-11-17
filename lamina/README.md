# Lamina

The typeface of Murèlle and Lamelio: a slender grotesk on the rhythm of the
lamella. Built on [Zalando Sans](https://github.com/zalando/sans) (Jakob
Ekelund, KH Type, Zalando; SIL OFL 1.1), released in 2025.

**Why this base.** Zalando Sans already has what we like in ABC Diatype:
spurless stems in a, u, d, q, a spurless G, a J without a top bar, flat
horizontal terminals and careful Polish diacritics. It also has width and
weight axes and a true italic.

**What Lamina changes** (each change is a rule applied to every glyph, in both
masters, so all weights and the italic inherit it):

1. **Slenderness.** The whole family is set at width 86 of the upstream width
   axis: narrower letters, tighter text, a compact colour close to Diatype.
2. **Lamella rhythm (flanks).** Where a curve turns vertical its handles are
   lengthened, so bowls (o d b p e c O G D, figures) stand on straighter sides,
   like a sheet of stone wrapped around a column.
3. **Tiles.** Every dot (i j ż ö . ! ? : ÷) is a small stone tile with bent
   corners instead of a sharp square.
4. **Tabular figures change only the figures.** Upstream `tnum` also swapped the
   word space for a figure-wide space, which spread words apart in tables.
5. **Names.** New family name; the upstream Reserved Font Name is not used.

| | |
| --- | --- |
| Weights | 400–700 variable; static Regular, Medium, SemiBold, Bold |
| Styles | upright and italic |
| Characters | 549 (Latin incl. full Polish, Vietnamese) |
| Files | `fonts/web` (WOFF2 + `lamina.css`), `fonts/ttf` (hinted), `fonts/variable` |
| Licence | SIL Open Font License 1.1 — see `OFL.txt` |

## Use

```css
@import url("lamina/fonts/web/lamina.css");
body { font-family: var(--font-lamina); }
td.price { font-variant-numeric: tabular-nums; }
```

## Build

```sh
pip install fontmake fonttools ufoLib2 skia-pathops brotli ttfautohint-py
python3 lamina/src/build.py --italic     # fonts/variable, fonts/ttf, fonts/web
python3 lamina/src/specimen.py           # specimen.html (needs the control fonts, see below)
```

- `sources/upstream/` — Zalando Sans source (`.glyphs`) and its licence
- `src/build.py` — interpolates the two masters at width 86, applies the edits, compiles
- `src/edits.py` — the Lamina rules: flank, tile, features, names
- `src/release.py` — variable font, statics, hinting, WOFF2, CSS
- `LAMINA_WITHOUT=flank|tile python3 lamina/src/build.py --out build/control/<name>.ttf`
  builds a control font with one rule switched off (used by the specimen)
