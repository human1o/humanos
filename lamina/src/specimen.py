#!/usr/bin/env python3
"""Write lamina/specimen.html: a self-contained specimen (fonts embedded)."""
import base64
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from fontTools.pens.recordingPen import RecordingPen  # noqa: E402
from fontTools.pens.svgPathPen import SVGPathPen  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402


def b64(path):
    return base64.b64encode(Path(path).read_bytes()).decode()


def rhythm_svg(word="minimum", style="Regular"):
    """The word drawn from the outlines, with a guide on every straight
    vertical edge: the lamellae made visible."""
    f = TTFont(ROOT / "fonts" / "ttf" / f"Lamina-{style}.ttf")
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    x = 0
    paths, edges = [], []
    for ch in word:
        name = cmap[ord(ch)]
        g = gs[name]
        pen = SVGPathPen(gs)
        from fontTools.pens.transformPen import TransformPen
        g.draw(TransformPen(pen, (1, 0, 0, 1, x, 0)))
        paths.append(pen.getCommands())
        rec = RecordingPen()
        g.draw(TransformPen(rec, (1, 0, 0, 1, x, 0)))
        cur = None
        for op, args in rec.value:
            if op == "moveTo":
                cur = args[0]
            elif op == "lineTo":
                a, b = cur, args[0]
                if abs(a[0] - b[0]) < 1 and abs(a[1] - b[1]) > 150:
                    edges.append(round(a[0]))
                cur = b
            elif op in ("curveTo", "qCurveTo"):
                cur = args[-1]
        x += g.width
    edges = sorted(set(edges))
    W = x
    lines = "".join(f'<line x1="{e}" x2="{e}" y1="-60" y2="590" class="lam"/>' for e in edges)
    body = "".join(f'<path d="{d}"/>' for d in paths)
    return (f'<svg viewBox="-20 -620 {W + 40} 700" role="img" aria-label="{word}: proste krawędzie liter w równym rytmie">'
            f'<g transform="scale(1,-1)">{lines}<g class="ink">{body}</g></g></svg>')


def glyph_count():
    f = TTFont(ROOT / "fonts" / "ttf" / "Lamina-Regular.ttf")
    return len(f.getBestCmap())


PAGE = r'''<title>Lamina</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
/* Layout: one quiet column on warm white, like a showroom wall; the letters are the only image. */
@font-face{font-family:"Lamina";src:url(data:font/woff2;base64,__R__) format("woff2");font-weight:400;font-display:block}
@font-face{font-family:"Lamina";src:url(data:font/woff2;base64,__M__) format("woff2");font-weight:500;font-display:block}
@font-face{font-family:"Lamina";src:url(data:font/woff2;base64,__S__) format("woff2");font-weight:600;font-display:block}
@font-face{font-family:"Lamina";src:url(data:font/woff2;base64,__B__) format("woff2");font-weight:700;font-display:block}
@font-face{font-family:"LaminaNoFlank";src:url(data:font/woff2;base64,__NF__) format("woff2");font-display:block}
@font-face{font-family:"LaminaNoBend";src:url(data:font/woff2;base64,__NB__) format("woff2");font-display:block}
@font-face{font-family:"LaminaNoCut";src:url(data:font/woff2;base64,__NC__) format("woff2");font-display:block}
:root{
  --wall:#f5f5f3; --panel:#ffffff; --ink:#222220; --muted:#6b6a66; --rule:#dcdcd8; --stone:#a88e68; --dark:#0e0e0d; --on-dark:#ffffff;
  --font:"Lamina",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--wall:#141413;--panel:#1b1b19;--ink:#ecebe7;--muted:#9c9a94;--rule:#32312e;--stone:#c9ab7e;--dark:#ecebe7;--on-dark:#141413;color-scheme:dark}}
:root[data-theme="dark"]{--wall:#141413;--panel:#1b1b19;--ink:#ecebe7;--muted:#9c9a94;--rule:#32312e;--stone:#c9ab7e;--dark:#ecebe7;--on-dark:#141413;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--wall);color:var(--ink);font-family:var(--font);font-size:16px;line-height:1.5;-webkit-font-smoothing:antialiased;
  padding-left:max(20px,env(safe-area-inset-left,0px));padding-right:max(20px,env(safe-area-inset-right,0px));padding-block:0 120px}
main{max-width:1120px;margin:0 auto;display:flex;flex-direction:column;gap:112px}
.label{font-size:12px;font-weight:600;letter-spacing:.07em;text-transform:uppercase;color:var(--muted);font-feature-settings:"case"}
h2{font-size:clamp(28px,3.6vw,42px);font-weight:400;letter-spacing:-.02em;line-height:1.08;margin:10px 0 0;text-wrap:balance}
p{margin:0;max-width:60ch}
section{display:flex;flex-direction:column;gap:32px}
.head{display:flex;flex-direction:column;gap:8px}
.lede{color:var(--muted)}

/* hero */
.hero{padding-top:clamp(48px,9vw,120px);gap:28px}
.mark{font-size:clamp(110px,26vw,330px);line-height:.82;letter-spacing:-.04em;margin:0 0 0 -.03em;font-weight:400}
.idea{font-size:clamp(20px,2.4vw,28px);line-height:1.3;max-width:34ch;font-weight:400}
.idea b{font-weight:500}
.meta{display:flex;flex-wrap:wrap;gap:8px 28px;color:var(--muted);font-size:14px}
.names{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1px;background:var(--rule);border:1px solid var(--rule);border-radius:14px;overflow:hidden}
.names div{background:var(--panel);padding:22px 22px 18px;display:flex;flex-direction:column;gap:6px;min-width:0}
.names b{font-size:clamp(40px,7.4vw,92px);line-height:1.05;letter-spacing:-.025em;white-space:nowrap}
.names span{font-size:12px;color:var(--muted)}
@media (max-width:640px){.names{grid-template-columns:1fr}}

/* principles */
.law{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:24px 48px;align-items:start}
@media (max-width:820px){.law{grid-template-columns:1fr}}
.law h3{font-size:24px;font-weight:500;letter-spacing:-.01em;margin:6px 0 10px}
.law p{color:var(--muted)}
.law p strong{color:var(--ink);font-weight:500}
.n{font-size:13px;color:var(--stone);font-weight:600;font-variant-numeric:tabular-nums}
.vs{display:grid;grid-template-columns:1fr 1fr;border:1px solid var(--rule);border-radius:14px;overflow:hidden;background:var(--panel)}
.vs > div{padding:18px 18px 16px;display:flex;flex-direction:column;gap:6px;min-width:0}
.vs > div + div{border-left:1px solid var(--rule)}
.vs .big{font-size:clamp(64px,11vw,132px);line-height:1.08;letter-spacing:-.01em;white-space:nowrap;overflow:hidden}
.vs .line{font-size:clamp(17px,2vw,22px);line-height:1.3}
.vs small{font-size:12px;color:var(--muted)}
.vs .off{color:var(--muted)}
.rhythm{border:1px solid var(--rule);border-radius:14px;background:var(--panel);padding:20px 18px 12px;overflow:hidden}
.rhythm svg{width:100%;height:auto;display:block}
.rhythm .ink path{fill:var(--ink)}
.rhythm .lam{stroke:var(--stone);stroke-width:5;opacity:.75}
.rhythm small{display:block;font-size:12px;color:var(--muted);margin-top:8px}

/* alphabet */
.set{display:flex;flex-direction:column;gap:10px}
.set div{font-size:clamp(30px,5.4vw,64px);line-height:1.14;letter-spacing:.01em;overflow-wrap:anywhere}
.set .sm{font-size:clamp(22px,3.4vw,40px);color:var(--ink)}
.figs{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px}
.figs > div{border:1px solid var(--rule);border-radius:14px;background:var(--panel);padding:18px 20px;display:flex;flex-direction:column;gap:10px;min-width:0}
.figs .col{font-size:22px;line-height:1.45;font-variant-numeric:tabular-nums;text-align:right}
.figs .prop{font-size:22px;line-height:1.45;font-variant-numeric:proportional-nums;text-align:right}
.figs .giant{font-size:clamp(72px,10vw,120px);line-height:1;letter-spacing:-.01em}

/* text */
.para{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:36px 48px}
.para > div{display:flex;flex-direction:column;gap:8px;min-width:0}
.para small{font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}

/* product card */
.shop{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:0;border:1px solid var(--rule);border-radius:16px;overflow:hidden;background:var(--panel)}
@media (max-width:760px){.shop{grid-template-columns:1fr}}
.slab{min-height:360px;background:
  radial-gradient(120% 90% at 20% 15%, rgba(255,255,255,.55), transparent 60%),
  repeating-linear-gradient(97deg, rgba(120,96,64,.06) 0 3px, transparent 3px 11px),
  repeating-linear-gradient(83deg, rgba(120,96,64,.05) 0 2px, transparent 2px 17px),
  linear-gradient(160deg,#e9dfcf,#d9cab3 55%,#cbb89c);position:relative}
.slab span{position:absolute;left:18px;bottom:16px;font-size:12px;color:#5b4a33;letter-spacing:.06em;text-transform:uppercase;font-weight:600}
.card{padding:26px 26px 24px;display:flex;flex-direction:column;gap:18px;min-width:0}
.card h4{font-size:clamp(28px,3.4vw,38px);font-weight:500;letter-spacing:-.02em;line-height:1.05;margin:2px 0 0}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chips span{font-size:13px;border:1px solid var(--rule);border-radius:999px;padding:5px 11px}
.chips span.on{background:var(--dark);color:var(--on-dark);border-color:var(--dark)}
.prices{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}
.prices td,.prices th{padding:8px 0;border-bottom:1px solid var(--rule);font-size:14px;text-align:left}
.prices th{font-size:12px;font-weight:500;color:var(--muted)}
.prices td:last-child,.prices th:last-child{text-align:right}
.total{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap}
.total b{font-size:34px;font-weight:600;letter-spacing:-.015em;font-variant-numeric:tabular-nums}
.btns{display:flex;gap:10px;flex-wrap:wrap}
.btn{font:inherit;font-size:15px;font-weight:500;border-radius:11px;padding:11px 18px;border:1px solid var(--dark);background:var(--dark);color:var(--on-dark)}
.btn.ghost{background:transparent;color:var(--ink);border-color:var(--rule)}

/* tester */
.tester{border:1px solid var(--rule);border-radius:14px;background:var(--panel);overflow:hidden}
.controls{display:flex;flex-wrap:wrap;gap:14px 26px;align-items:center;padding:14px 18px;border-bottom:1px solid var(--rule);font-size:13px;color:var(--muted)}
.controls label{display:flex;align-items:center;gap:10px}
.controls output{color:var(--ink);font-variant-numeric:tabular-nums;min-width:3ch}
.seg{display:flex;gap:6px;flex-wrap:wrap}
.seg button{font:inherit;font-size:13px;border:1px solid var(--rule);background:transparent;color:var(--ink);border-radius:999px;padding:5px 12px;cursor:pointer}
.seg button[aria-pressed=true]{background:var(--dark);color:var(--on-dark);border-color:var(--dark)}
input[type=range]{accent-color:var(--ink);width:150px}
button:focus-visible,input:focus-visible,[contenteditable]:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
#sample{padding:24px 18px 30px;font-size:64px;line-height:1.1;letter-spacing:-.015em;overflow-wrap:anywhere;min-height:2.3em}

.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1px;background:var(--rule);border:1px solid var(--rule);border-radius:14px;overflow:hidden}
.facts div{background:var(--panel);padding:16px 18px;display:flex;flex-direction:column;gap:4px}
.facts b{font-size:22px;font-weight:500;font-variant-numeric:tabular-nums}
.facts span{font-size:13px;color:var(--muted)}
footer{color:var(--muted);font-size:14px;border-top:1px solid var(--rule);padding-top:20px}
footer p{max-width:76ch}
@media (prefers-reduced-motion:no-preference){.mark{transition:font-weight .4s}}
</style>

<main>
<section class="hero">
  <span class="label">Krój pisma Murèlle i Lamelio</span>
  <h1 class="mark">Lamina</h1>
  <p class="idea"><b>Lamina</b> to po łacinie cienka płyta, a <b>lamella</b> to jej zdrobnienie. Z tego jednego słowa wyrastają obie marki i ten krój.</p>
  <div class="meta"><span>4 grubości: 400, 500, 600, 700</span><span>__COUNT__ znaków</span><span>pełna polszczyzna</span><span>cyfry tabelaryczne</span><span>narysowany od zera</span></div>
  <div class="names">
    <div><b style="font-weight:400">Murèlle</b><span>400 Regular</span></div>
    <div><b style="font-weight:500">Lamelio</b><span>500 Medium</span></div>
    <div><b style="font-weight:600">Murèlle</b><span>600 SemiBold</span></div>
    <div><b style="font-weight:700">Lamelio</b><span>700 Bold</span></div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Idea w dwóch zdaniach</span>
  <h2>Każda litera stoi na rytmie lameli. Gdzie kreska skręca, gnie się jak kamień; gdzie się kończy, jest cięta jak płyta.</h2></div>
  <p class="lede">Murèlle to kamień, który się nie łamie, tylko gnie. Lamelio to ściana z lamel: ta sama szerokość, ten sam odstęp, a resztę robi światło. Lamina bierze z obu po jednej rzeczy i niczego nie dodaje. Nie ma tu nacięć, ozdobników ani zaokrągleń dla efektu. Charakter powstaje z trzech zasad, które działają w każdym znaku.</p>
</section>

<section>
  <div class="law">
    <div><span class="n">Zasada 1</span><h3>Rytm lameli</h3>
      <p><strong>Okrągłe litery mają proste boki.</strong> Brzuśce o, d, b, p, q, c, e stoją na pionowych flankach, a światło między nimi jest takie samo jak w n, u i h. Tekst pulsuje równo, jak ściana z lamel. Bez tej zasady o jest zwykłym owalem, który wypada z rytmu i rozmywa linię.</p></div>
    <div class="rhythm">__RHYTHM__<small>Złote linie: każda prosta, pionowa krawędź w słowie „minimum”. Odstępy się powtarzają.</small></div>
  </div>
  <div class="vs">
    <div><small>Z zasadą</small><div class="big">dobro</div><div class="line">Płyta kamienia owinięta wokół słupa.</div></div>
    <div><small>Bez zasady: zwykły owal</small><div class="big off" style="font-family:LaminaNoFlank">dobro</div><div class="line off" style="font-family:LaminaNoFlank">Płyta kamienia owinięta wokół słupa.</div></div>
  </div>
</section>

<section>
  <div class="law">
    <div><span class="n">Zasada 2</span><h3>Gięcie zamiast łamania</h3>
      <p><strong>Każda kreska, która skręca, gnie się tym samym łukiem.</strong> Stopa t, hak f, ogony j, y i g, flaga 1 i ogonek ą, ę mają jedno prawo krzywej. Bez tej zasady narożniki pękają pod kątem prostym i krój robi się techniczny, jak szablon.</p></div>
    <div></div>
  </div>
  <div class="vs">
    <div><small>Z zasadą</small><div class="big">tfję1</div><div class="line">Fajny, gięty, jaśniejszy.</div></div>
    <div><small>Bez zasady: kąt prosty</small><div class="big off" style="font-family:LaminaNoBend">tfję1</div><div class="line off" style="font-family:LaminaNoBend">Fajny, gięty, jaśniejszy.</div></div>
  </div>
</section>

<section>
  <div class="law">
    <div><span class="n">Zasada 3</span><h3>Cięcie pod kątem prostym</h3>
      <p><strong>Każda końcówka jest cięta poziomo albo pionowo,</strong> jak płyta przecięta piłą: c, e, a, s, C, G, wierzchołki A, V, W, nawet kreska w ł. Daje to precyzję bez kłucia. Bez tej zasady końcówki cięte prostopadle do kreski patrzą w różne strony i litera traci spokój.</p></div>
    <div></div>
  </div>
  <div class="vs">
    <div><small>Z zasadą</small><div class="big">ceCG</div><div class="line">Cechy cennej ceramiki.</div></div>
    <div><small>Bez zasady: cięcie prostopadłe do kreski</small><div class="big off" style="font-family:LaminaNoCut">ceCG</div><div class="line off" style="font-family:LaminaNoCut">Cechy cennej ceramiki.</div></div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Alfabet i cyfry</span><h2>Każdy znak z tych samych trzech zasad</h2></div>
  <div class="set">
    <div>ABCDEFGHIJKLMNOPQRSTUVWXYZ</div>
    <div>abcdefghijklmnopqrstuvwxyz</div>
    <div>0123456789</div>
    <div class="sm">ĄĆĘŁŃÓŚŹŻ ąćęłńóśźż è ß æ œ ø</div>
    <div class="sm">&amp; @ € $ % “ ” „ ” « » ( ) [ ] { } / → ↗ ✓ ● ± × ÷ ≤ ≥</div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Cyfry</span><h2>Cyfry jak litery najwyższej wagi</h2>
  <p class="lede">Cyfry mają wysokość wersalików, własną grubość kreski i te same flanki, gięcie i cięcia. Każda ma jeden rysunek. Cyfry tabelaryczne to ten sam rysunek na równej szerokości, więc ceny w kolumnie stoją jedna pod drugą.</p></div>
  <div class="figs">
    <div><span class="label">Tabelaryczne</span><div class="col">12 480,00 zł<br>9 315,60 zł<br>1 111,10 zł<br>407,90 zł</div></div>
    <div><span class="label">Proporcjonalne</span><div class="prop">12 480,00 zł<br>9 315,60 zł<br>1 111,10 zł<br>407,90 zł</div></div>
    <div><span class="label">Jeden rysunek</span><div class="giant">2026</div></div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Akapit</span><h2>Tekst, który czyta się bez zmęczenia</h2></div>
  <div class="para">
    <div><small>16 px · 400</small><p style="font-size:16px;line-height:1.55">Murèlle to cienkie arkusze prawdziwego kamienia: trawertynu, wapienia, łupka. Są tak elastyczne, że owijają łuk, słup i narożnik ściany. Kamień, który się nie łamie, tylko gnie. Lamelio to ściany z lamel: pionowy rytm, ta sama szerokość, ten sam odstęp, a resztę robi światło. Żadnego blichtru, tylko ciepła biel, faktura i światło.</p></div>
    <div><small>13 px · 400 i 600</small><p style="font-size:13px;line-height:1.55">Zamówienie <b style="font-weight:600">MU-2026-01184</b> zostało przyjęte. Flexible Stone, Travertino Avorio, format 1200 × 600 mm, 48 szt. Dostawa w czwartek, 19 listopada, na adres: ul. Źródlana 7, 50-541 Wrocław. Gwarancja jakości obejmuje każdą płytę; łączenia wykonujemy bez fug.</p>
      <small style="margin-top:14px">12 px · 500, wersaliki z „case”</small><p class="label" style="font-size:12px;color:var(--ink)">Panel partnera · Zamówienia (3) · Konfigurator ściany</p></div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Karta produktu</span><h2>Lamina w pracy</h2><p class="lede">Przykładowe dane, żeby pokazać krój w panelu B2B.</p></div>
  <div class="shop">
    <div class="slab" role="img" aria-label="Faktura trawertynu"><span>Travertino Avorio</span></div>
    <div class="card">
      <div><span class="label">Flexible Stone · Trawertyn</span><h4>Travertino Avorio</h4></div>
      <div class="chips"><span class="on">1200 × 600 mm</span><span>2400 × 1200 mm</span><span>Grubość 1,5 mm</span></div>
      <table class="prices">
        <tr><th>Ilość</th><th>Cena za m²</th><th>Za arkusz</th></tr>
        <tr><td>1–19 szt.</td><td>389,00 zł</td><td>280,08 zł</td></tr>
        <tr><td>20–49 szt.</td><td>359,00 zł</td><td>258,48 zł</td></tr>
        <tr><td>50+ szt.</td><td>329,00 zł</td><td>236,88 zł</td></tr>
      </table>
      <div class="total"><span class="lede">48 arkuszy, 34,56 m², netto</span><b>12 407,04 zł</b></div>
      <div class="btns"><span class="btn">Dodaj do koszyka</span><span class="btn ghost">Konfigurator ściany</span></div>
    </div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Wypróbuj</span><h2>Wpisz własny tekst</h2></div>
  <div class="tester">
    <div class="controls">
      <div class="seg" role="group" aria-label="Grubość">
        <button id="w400" data-w="400" aria-pressed="true">400</button><button id="w500" data-w="500" aria-pressed="false">500</button><button id="w600" data-w="600" aria-pressed="false">600</button><button id="w700" data-w="700" aria-pressed="false">700</button>
      </div>
      <label for="sz">Rozmiar <input id="sz" type="range" min="12" max="160" value="64"><output id="szo">64</output></label>
      <div class="seg"><button id="tn" aria-pressed="false">Cyfry tabelaryczne</button></div>
    </div>
    <div id="sample" contenteditable="true" spellcheck="false" aria-label="Tekst próbny">Zażółć gęślą jaźń. Murèlle 12 480,00 zł</div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Pliki</span><h2>Gotowe do sieci i do instalacji</h2></div>
  <div class="facts">
    <div><b>4</b><span>grubości: 400, 500, 600, 700</span></div>
    <div><b>__COUNT__</b><span>znaków: łacina zachodnia i środkowoeuropejska</span></div>
    <div><b>WOFF2 + TTF</b><span>sieć i komputer, z hintingiem dla Windows</span></div>
    <div><b>OFL 1.1</b><span>wolno używać komercyjnie</span></div>
  </div>
</section>

<footer><p>Lamina 1.000. Każdy kontur został narysowany od zera przez program, który składa litery z trzech zasad, bez cudzego kroju jako bazy. Funkcje OpenType: kerning, cyfry tabelaryczne (tnum), interpunkcja do wersalików (case).</p></footer>
</main>

<script>
(function(){
  var s=document.getElementById('sample'),sz=document.getElementById('sz'),o=document.getElementById('szo'),tn=document.getElementById('tn');
  var w=400,tab=false;
  function apply(){
    var max=Math.max(12,(s.clientWidth-36)/3.4);
    s.style.fontSize=Math.min(+sz.value,max)+'px';o.textContent=sz.value;
    s.style.fontWeight=w;s.style.fontVariantNumeric=tab?'tabular-nums':'normal';
  }
  Array.prototype.forEach.call(document.querySelectorAll('[data-w]'),function(b){
    b.addEventListener('click',function(){w=+b.dataset.w;Array.prototype.forEach.call(document.querySelectorAll('[data-w]'),function(x){x.setAttribute('aria-pressed',String(x===b))});apply();});
  });
  tn.addEventListener('click',function(){tab=!tab;tn.setAttribute('aria-pressed',String(tab));apply();});
  sz.addEventListener('input',apply);window.addEventListener('resize',apply);apply();
})();
</script>
'''


def main():
    web = ROOT / "fonts" / "web"
    wo = ROOT / "build" / "without"
    html = (PAGE.replace("__R__", b64(web / "Lamina-Regular.woff2"))
            .replace("__M__", b64(web / "Lamina-Medium.woff2"))
            .replace("__S__", b64(web / "Lamina-SemiBold.woff2"))
            .replace("__B__", b64(web / "Lamina-Bold.woff2"))
            .replace("__NF__", b64(wo / "Lamina-without-flank.woff2"))
            .replace("__NB__", b64(wo / "Lamina-without-bend.woff2"))
            .replace("__NC__", b64(wo / "Lamina-without-cut.woff2"))
            .replace("__RHYTHM__", rhythm_svg())
            .replace("__COUNT__", str(glyph_count())))
    out = ROOT / "specimen.html"
    out.write_text(html)
    print(out, out.stat().st_size)


if __name__ == "__main__":
    main()
