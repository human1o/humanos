"""python3 src/debug.py out.png w glyph [glyph...] — outline with points."""
import sys, subprocess, os
sys.path.insert(0, os.path.dirname(__file__))
import build, params
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import RecordingPen
build.load_modules()
out, w = sys.argv[1], float(sys.argv[2])
names = sys.argv[3:]
p = params.P(w)
gl = build.draw_all(p, only=set(names))
html = '<body style="margin:6px;background:#fff">'
for n in names:
    g = gl[n]
    pen = SVGPathPen(None); g["shape"].path.draw(pen)
    rec = RecordingPen(); g["shape"].path.draw(rec)
    pts = []
    for op, args in rec.value:
        for i, a in enumerate(args):
            on = i == len(args) - 1
            pts.append(f'<circle cx="{a[0]:.0f}" cy="{a[1]:.0f}" r="{7 if on else 4}" fill="{"#d00" if on else "#08c"}"/>')
    W = g["advance"]
    html += (f'<svg width="{(W+100)*0.42}" height="{1100*0.42}" viewBox="-50 -800 {W+100} 1100"><g transform="scale(1,-1)">'
             f'<line x1="-50" x2="{W+50}" y1="0" y2="0" stroke="#f99"/><line x1="-50" x2="{W+50}" y1="526" y2="526" stroke="#9cf"/>'
             f'<line x1="-50" x2="{W+50}" y1="700" y2="700" stroke="#9cf"/>'
             f'<path d="{pen.getCommands()}" fill="rgba(0,0,0,.15)" stroke="#000" stroke-width="2"/>{"".join(pts)}</g></svg>')
open('/tmp/dbg.html', 'w').write(html)
subprocess.run(['node', '-e', f"const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1600,height:300}}}});await p.goto('file:///tmp/dbg.html');await p.screenshot({{path:'{out}',fullPage:true}});await b.close()}})()"], check=True)
