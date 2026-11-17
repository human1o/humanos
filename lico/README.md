# Lico

The typeface of Murèlle and Lamelio. *Lico* is the Polish word for the face of
a wall — the visible side of a stone or a cladding. A typeface is a face too.

Lico is a quiet grotesk with one gesture. Wherever a stroke changes direction
it turns through the same generous bend, the way a sheet of flexible stone
wraps a corner: the foot of **t**, the hook of **f**, the tails of **j**,
**y**, **g** and **Q**. The **t** carries the second half of the idea — its
crossbar bends up into the stem. Everything else stays still: **l** and **I**
are plain slats (the lamella), **a** stands square on the baseline, terminals
are cut flat.

| | |
| --- | --- |
| Weights | Light 300 · Regular 400 · Medium 500 · SemiBold 600 · Bold 700 · ExtraBold 800 · Black 900, plus one variable font (`wght` 300–900) |
| Characters | 502 — Latin Extended (Polish and all European Latin languages), figures, currency, arrows, interface symbols |
| Features | kerning, tabular figures `tnum`, slashed zero `zero`, case-sensitive punctuation `case`, fractions `frac`, superiors `sups`, ordinals `ordn`, and three stylistic sets |
| Licence | SIL Open Font License 1.1 |

## Stylistic sets

| Set | What it does | Use it for |
| --- | --- | --- |
| `ss01` | double-storey g | a more bookish tone |
| `ss02` | bent l | codes and SKUs, where I / l / 1 must differ |
| `ss03` | serifed I | same |

## Using it

```css
@import url("lico/fonts/web/lico.css");
body { font-family: var(--font-lico); }
```

- `fonts/web/` — WOFF2 for the web: the variable font and the seven static weights, plus `lico.css`
- `fonts/variable/` — variable TTF
- `fonts/static/` — static TTFs, hinted for Windows, for desktop apps

Lico has no italic. Browsers slant it on request; avoid that in headings.

## What it is made from

Lico is a redesign of [Schibsted Grotesk](https://github.com/schibsted/schibsted-grotesk)
(Bakken & Bæck, Henrik Kongsvoll; OFL). Upstream supplies the skeleton —
proportions, the round letters, the capitals, figures, kerning. Lico changes:

- **redrawn:** t, f, j, l, y, g, a, I, J, the Q tail, the hooks of ŋ Ŋ ɲ Ɲ, and
  every accented letter and ligature built from them (about 90 glyphs)
- **new:** a Light weight, the bent l, ✓ ● ▲ ▼ ◀ ▶, sans roman numerals
- **kept as alternates:** upstream's double-storey g and serifed I
- **fixed:** tabular figures no longer widen full stops and commas

The licence is inherited: Lico may be used, embedded and shipped in any
product, free of charge, but the font files themselves stay under the OFL and
cannot be sold on their own or relicensed.

## Building

```sh
pip install fontmake ufoLib2 fonttools brotli ttfautohint-py
python3 lico/sources/build.py
```

- `sources/upstream/` — the unmodified Schibsted Grotesk source
- `sources/shapes.py` — the parametric drawings; each redrawn letter is one
  function evaluated for both masters, so weights always interpolate
- `sources/edits.py` — derived glyphs, composites, kerning classes, features, names
- `sources/compile_fonts.py` — variable font, static instances, WOFF2

To rename the family, change `FAMILY` in `build.py`, `edits.py` and
`compile_fonts.py`.
