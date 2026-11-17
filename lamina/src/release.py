"""Lamina — release build: four weights, hinted TTF, WOFF2, CSS, licence."""
import shutil
from pathlib import Path

from fontTools.ttLib import TTFont

import build
import params

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "fonts"

CSS = """/* Lamina — Regular 400, Medium 500, SemiBold 600, Bold 700. Paths are relative to this file. */
{faces}
:root {{
  --font-lamina: "Lamina", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}

/* Prices and tables: tabular figures keep the columns straight. */
.lamina-tabular {{ font-variant-numeric: tabular-nums; }}
/* All-caps labels: punctuation lifted to the capitals. */
.lamina-caps {{ font-feature-settings: "case"; letter-spacing: 0.04em; text-transform: uppercase; }}
"""

FACE = """@font-face {{
  font-family: "Lamina";
  src: url("Lamina-{style}.woff2") format("woff2");
  font-weight: {weight};
  font-style: normal;
  font-display: swap;
}}"""


def autohint(src, dst):
    from ttfautohint import ttfautohint
    ttfautohint(in_file=str(src), out_file=str(dst), no_info=True)


def run():
    raw = ROOT / "build" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    for d in ("ttf", "web"):
        if (OUT / d).exists():
            shutil.rmtree(OUT / d)
        (OUT / d).mkdir(parents=True)
    faces = []
    for style, (weight, _) in params.WEIGHTS.items():
        r = raw / f"Lamina-{style}.ttf"
        build.build_font(style, str(r))
        t = OUT / "ttf" / f"Lamina-{style}.ttf"
        autohint(r, t)
        f = TTFont(t)
        f.flavor = "woff2"
        f.save(OUT / "web" / f"Lamina-{style}.woff2")
        faces.append(FACE.format(style=style, weight=weight))
        print(style, t.stat().st_size, (OUT / "web" / f"Lamina-{style}.woff2").stat().st_size)
    (OUT / "web" / "lamina.css").write_text(CSS.format(faces="\n".join(faces)))
    shutil.copy(ROOT / "OFL.txt", OUT / "web" / "OFL.txt")
    shutil.copy(ROOT / "OFL.txt", OUT / "ttf" / "OFL.txt")
