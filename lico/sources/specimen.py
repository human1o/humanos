#!/usr/bin/env python3
"""Write lico/specimen.html — a self-contained page (font embedded)."""
import base64
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
woff = (ROOT / "fonts/web/Lico-Variable.woff2").read_bytes()
cmap = TTFont(ROOT / "fonts/variable/Lico[wght].ttf").getBestCmap()
chars = "".join(
    f"<span>&#{c};</span>" for c in sorted(cmap)
    if c > 32 and c != 0xA0 and not 0x300 <= c < 0x370)

HTML = r'''<title>Lico Specimen</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
/* Layout: one quiet column on warm white; the letters are the only image. */
@font-face{font-family:"Lico";src:url(data:font/woff2;base64,__FONT__) format("woff2");font-weight:300 900;font-style:normal;font-display:block}
:root{
  --canvas:#f5f5f3;--panel:#ffffff;--ink:#222220;--muted:#686865;--rule:#dcdcd8;--dark:#0e0e0d;--on-dark:#ffffff;--bend:#b9783a;
  --font:"Lico",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--canvas:#141413;--panel:#1c1c1a;--ink:#ecece8;--muted:#9a9a95;--rule:#333330;--dark:#ecece8;--on-dark:#141413;--bend:#d9a066;color-scheme:dark}}
:root[data-theme="dark"]{--canvas:#141413;--panel:#1c1c1a;--ink:#ecece8;--muted:#9a9a95;--rule:#333330;--dark:#ecece8;--on-dark:#141413;--bend:#d9a066;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--canvas);color:var(--ink);font-family:var(--font);font-size:16px;line-height:1.5;-webkit-font-smoothing:antialiased;
  padding-left:max(20px,env(safe-area-inset-left,0px));padding-right:max(20px,env(safe-area-inset-right,0px));padding-block:0 96px}
main{max-width:1080px;margin:0 auto;display:flex;flex-direction:column;gap:88px}
.label{font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);font-feature-settings:"case"}
h2{font-size:clamp(26px,3.4vw,38px);font-weight:400;letter-spacing:-.02em;line-height:1.1;margin:8px 0 0;text-wrap:balance}
p{margin:0;max-width:62ch}
.lede{color:var(--muted)}
section{display:flex;flex-direction:column;gap:28px}
.head{display:flex;flex-direction:column;gap:6px}

.hero{padding-top:clamp(40px,8vw,96px);gap:20px}
.word{font-size:clamp(96px,27vw,340px);font-weight:400;letter-spacing:-.045em;line-height:.86;margin:0 0 0 -.04em}
.hero p{font-size:clamp(18px,2.1vw,24px);font-weight:300;line-height:1.35;max-width:36ch}
.meta{display:flex;flex-wrap:wrap;gap:8px 28px;color:var(--muted);font-size:14px}

.bend{display:grid;grid-template-columns:repeat(6,1fr);border:1px solid var(--rule);border-radius:12px;background:var(--panel);overflow:hidden}
.bend div{display:flex;flex-direction:column;align-items:center;gap:4px;padding:18px 4px 14px;border-left:1px solid var(--rule);min-width:0}
.bend div:first-child{border-left:0}
.bend b{font-weight:400;font-size:clamp(64px,13vw,168px);line-height:1.25}
.bend span{font-size:12px;color:var(--muted);text-align:center}
@media (max-width:640px){.bend{grid-template-columns:repeat(3,1fr)}.bend div:nth-child(4){border-left:0}.bend div:nth-child(n+4){border-top:1px solid var(--rule)}}
.pair{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px 48px}
.pair p{color:var(--muted)}
.pair strong{color:var(--ink);font-weight:600}

.tester{border:1px solid var(--rule);border-radius:12px;background:var(--panel);overflow:hidden}
.controls{display:flex;flex-wrap:wrap;gap:14px 28px;align-items:center;padding:14px 20px;border-bottom:1px solid var(--rule);font-size:13px;color:var(--muted)}
.controls label{display:flex;align-items:center;gap:10px}
.controls output{font-variant-numeric:tabular-nums;color:var(--ink);min-width:3ch}
input[type=range]{accent-color:var(--ink);width:150px}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chips button{font:inherit;font-size:13px;color:var(--ink);background:transparent;border:1px solid var(--rule);border-radius:999px;padding:5px 12px;cursor:pointer}
.chips button[aria-pressed=true]{background:var(--dark);color:var(--on-dark);border-color:var(--dark)}
button:focus-visible,input:focus-visible,[contenteditable]:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
#sample{padding:28px 20px 34px;font-size:72px;font-weight:400;line-height:1.08;letter-spacing:-.02em;outline-offset:-2px;overflow-wrap:anywhere;min-height:2.2em}

.weights{display:flex;flex-direction:column}
.weights div{display:flex;align-items:baseline;gap:20px;padding:10px 0;border-top:1px solid var(--rule);min-width:0}
.weights div:last-child{border-bottom:1px solid var(--rule)}
.weights small{flex:0 0 108px;font-size:13px;color:var(--muted);font-variant-numeric:tabular-nums}
.weights span{font-size:clamp(24px,4.6vw,46px);letter-spacing:-.015em;line-height:1.15;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}
@media (max-width:520px){.weights small{flex-basis:76px}}

.ui{border:1px solid var(--rule);border-radius:12px;background:var(--panel);padding:24px;display:flex;flex-direction:column;gap:18px;font-size:14px}
.ui h3{font-size:clamp(28px,4.4vw,44px);font-weight:400;letter-spacing:-.02em;line-height:1.1;margin:4px 0 0}
.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;min-width:640px;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:9px 12px 9px 0;border-bottom:1px solid var(--rule);font-size:13px;white-space:nowrap}
th{font-weight:500;color:var(--muted);font-size:12px}
td.code{font-feature-settings:"tnum","ss02","ss03","zero"}
.row{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.btn{background:var(--dark);color:var(--on-dark);border-radius:10px;padding:9px 16px;font-weight:500}
.btn.ghost{background:transparent;color:var(--ink);border:1px solid var(--rule)}
.sizes{display:flex;flex-direction:column;gap:10px}
.sizes p{max-width:none;display:flex;gap:16px;align-items:baseline}
.sizes small{flex:0 0 34px;font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}

.feat{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1px;background:var(--rule);border:1px solid var(--rule);border-radius:12px;overflow:hidden}
.feat div{background:var(--panel);padding:16px 18px;display:flex;flex-direction:column;gap:2px}
.feat b{font-weight:400;font-size:34px;line-height:1.25;white-space:nowrap}
.feat b i{font-style:normal;color:var(--muted)}
.feat span{font-size:13px;color:var(--muted)}
.feat code{font-family:var(--font);color:var(--ink)}

.set{display:grid;grid-template-columns:repeat(auto-fill,minmax(44px,1fr));border-top:1px solid var(--rule);border-left:1px solid var(--rule)}
.set span{font-size:22px;line-height:44px;text-align:center;border-right:1px solid var(--rule);border-bottom:1px solid var(--rule);overflow:hidden}
footer{color:var(--muted);font-size:14px;border-top:1px solid var(--rule);padding-top:20px}
footer p{max-width:72ch}
</style>

<main>
<section class="hero">
  <span class="label">Krój pisma Murèlle i Lamelio</span>
  <h1 class="word">Lico</h1>
  <p>Lico to widoczna strona muru. Cichy grotesk z jednym gestem: każda kreska, która skręca, skręca tym samym zgięciem.</p>
  <div class="meta"><span>7 odmian, 300–900</span><span>font zmienny</span><span>502 znaki</span><span>pełna polszczyzna</span><span>licencja OFL</span></div>
</section>

<section>
  <div class="head"><span class="label">Zasada</span><h2>Płaski kamień, który się zgina</h2></div>
  <div class="bend">
    <div><b>t</b><span>stopa i łuk poprzeczki</span></div>
    <div><b>f</b><span>hak</span></div>
    <div><b>j</b><span>ogon</span></div>
    <div><b>y</b><span>ogon</span></div>
    <div><b>g</b><span>ogon</span></div>
    <div><b>Q</b><span>ogon</span></div>
  </div>
  <div class="pair">
    <p><strong>Jedno zgięcie.</strong> Stopa t, hak f, ogony j, y, g i Q zawijają tym samym łukiem o jednym promieniu, tak jak arkusz Flexible Stone owija narożnik. W t poprzeczka dodatkowo wygina się w górę i przechodzi w trzon.</p>
    <p><strong>Reszta stoi.</strong> Litery l oraz I to proste lamele. Litera a staje płasko na linii, bez ogonka. Zakończenia są cięte poziomo. Nic nie zdobi, więc zgięcie widać.</p>
  </div>
</section>

<section>
  <div class="head"><span class="label">Wypróbuj</span><h2>Wpisz własny tekst</h2></div>
  <div class="tester">
    <div class="controls">
      <label for="w">Grubość <input id="w" type="range" min="300" max="900" value="400" step="1"><output id="wo">400</output></label>
      <label for="s">Rozmiar <input id="s" type="range" min="14" max="160" value="72" step="1"><output id="so">72</output></label>
      <div class="chips" role="group" aria-label="Warianty znaków">
        <button id="f-ss01" aria-pressed="false" data-f="ss01">g dwupiętrowe</button>
        <button id="f-ss02" aria-pressed="false" data-f="ss02">l zgięte</button>
        <button id="f-ss03" aria-pressed="false" data-f="ss03">I z szeryfami</button>
        <button id="f-zero" aria-pressed="false" data-f="zero">0 przekreślone</button>
        <button id="f-tnum" aria-pressed="false" data-f="tnum">cyfry tabelaryczne</button>
      </div>
    </div>
    <div id="sample" contenteditable="true" spellcheck="false" aria-label="Tekst próbny">Ściana jest bohaterem. Quality fittings, lightly glazed.</div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Odmiany</span><h2>Od Light do Black</h2></div>
  <div class="weights">
    <div><small>Light 300</small><span style="font-weight:300">Światło jest jedynym ornamentem</span></div>
    <div><small>Regular 400</small><span style="font-weight:400">Okładziny do każdej ściany</span></div>
    <div><small>Medium 500</small><span style="font-weight:500">Zamówienia przyjęte w tym tygodniu</span></div>
    <div><small>SemiBold 600</small><span style="font-weight:600">Lamele: wysokie, wąskie, powtarzane</span></div>
    <div><small>Bold 700</small><span style="font-weight:700">Rzeczy mają ciężar</span></div>
    <div><small>ExtraBold 800</small><span style="font-weight:800">Travertino Avorio 1200 × 600</span></div>
    <div><small>Black 900</small><span style="font-weight:900">Cisza</span></div>
  </div>
</section>

<section>
  <div class="head"><span class="label">W interfejsie</span><h2>Panel partnera</h2><p class="lede">Przykładowe dane, żeby pokazać krój w pracy.</p></div>
  <div class="ui">
    <div><span class="label">Zamówienia</span><h3>Dzień dobry, Agnieszko</h3></div>
    <p style="color:var(--muted)">Twoje zamówienie jest w drodze. Dostawa w czwartek, 19 listopada.</p>
    <div class="scroll"><table>
      <tr><th>Numer</th><th>Produkt</th><th>Format</th><th>Ilość</th><th>Wartość</th><th>Status</th></tr>
      <tr><td class="code">MU-2026-01184</td><td>Flexible Stone, Travertino Avorio</td><td>1200 × 600 mm</td><td>48 szt.</td><td>12 480,00 zł</td><td>✓ Przyjęte</td></tr>
      <tr><td class="code">MU-2026-01177</td><td>Lamelio Asti, dąb żłobiony</td><td>2700 × 122 mm</td><td>120 szt.</td><td>9 315,60 zł</td><td>→ W produkcji</td></tr>
      <tr><td class="code">LA-2026-0I1l0</td><td>Flexible Stone, Grigio Łupek</td><td>2400 × 1200 mm</td><td>6 szt.</td><td>4 071,90 zł</td><td>↗ Wysłane</td></tr>
    </table></div>
    <div class="row"><span class="btn">Dodaj do koszyka</span><span class="btn ghost">Konfigurator ściany</span></div>
    <div class="sizes">
      <p style="font-size:16px"><small>16</small><span>Partnerzy otrzymują właściwe okładziny do każdej wykańczanej ściany.</span></p>
      <p style="font-size:14px"><small>14</small><span>Partnerzy otrzymują właściwe okładziny do każdej wykańczanej ściany.</span></p>
      <p style="font-size:13px"><small>13</small><span>Partnerzy otrzymują właściwe okładziny do każdej wykańczanej ściany.</span></p>
      <p style="font-size:12px"><small>12</small><span>Partnerzy otrzymują właściwe okładziny do każdej wykańczanej ściany.</span></p>
      <p style="font-size:11px"><small>11</small><span>Partnerzy otrzymują właściwe okładziny do każdej wykańczanej ściany.</span></p>
    </div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Funkcje OpenType</span><h2>Szczegóły na życzenie</h2></div>
  <div class="feat">
    <div><b><i>g </i><span style="font-feature-settings:'ss01';font-size:inherit;color:inherit">g</span></b><span><code>ss01</code> g dwupiętrowe</span></div>
    <div><b><i>Illinois </i><span style="font-feature-settings:'ss02','ss03';font-size:inherit;color:inherit">Illinois</span></b><span><code>ss02</code> <code>ss03</code> rozróżnienie I, l, 1 w kodach</span></div>
    <div><b><i>1001 </i><span style="font-feature-settings:'zero';font-size:inherit;color:inherit">1001</span></b><span><code>zero</code> zero przekreślone</span></div>
    <div><b style="font-feature-settings:'tnum'">1 111,10<br>9 480,00</b><span><code>tnum</code> cyfry tabelaryczne</span></div>
    <div><b><i>(A-B) </i><span style="font-feature-settings:'case';font-size:inherit;color:inherit">(A-B)</span></b><span><code>case</code> interpunkcja do wersalików</span></div>
    <div><b style="font-feature-settings:'frac'">1/2 3/4 m<span style="font-feature-settings:'sups';font-size:inherit;color:inherit">2</span></b><span><code>frac</code> <code>sups</code> ułamki i indeksy</span></div>
  </div>
  <div class="feat">
    <div><b>ąćęłńóśźż</b><span>polskie znaki</span></div>
    <div><b>ĄĆĘŁŃÓŚŹŻ</b><span>wersaliki</span></div>
    <div><b>→ ↗ ✓ ● ▲ ▼</b><span>symbole interfejsu</span></div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Zestaw znaków</span><h2>502 znaki</h2></div>
  <div class="set">__CHARS__</div>
</section>

<footer><p>Lico powstało na bazie kroju Schibsted Grotesk (Bakken &amp; Bæck, Henrik Kongsvoll), udostępnionego na licencji SIL Open Font License 1.1. Przerysowane zostały t, f, j, l, y, g, a, I, J, ogon Q oraz wszystkie litery z akcentami i ligatury, które z nich powstają. Odmiana Light, zgięte l i symbole interfejsu są nowe.</p></footer>
</main>

<script>
(function(){
  var sample=document.getElementById('sample'),w=document.getElementById('w'),s=document.getElementById('s');
  var feats={};
  function apply(){
    sample.style.fontWeight=w.value;document.getElementById('wo').textContent=w.value;
    var size=Math.min(+s.value,Math.max(14,(sample.clientWidth-40)/3.2));
    sample.style.fontSize=size+'px';document.getElementById('so').textContent=s.value;
    var on=Object.keys(feats).filter(function(k){return feats[k]});
    sample.style.fontFeatureSettings=on.length?on.map(function(k){return '"'+k+'"'}).join(','):'normal';
  }
  w.addEventListener('input',apply);s.addEventListener('input',apply);window.addEventListener('resize',apply);
  Array.prototype.forEach.call(document.querySelectorAll('.chips button'),function(b){
    b.addEventListener('click',function(){var k=b.dataset.f;feats[k]=!feats[k];b.setAttribute('aria-pressed',String(!!feats[k]));apply();});
  });
  apply();
})();
</script>
'''

out = ROOT / "specimen.html"
out.write_text(HTML.replace("__FONT__", base64.b64encode(woff).decode()).replace("__CHARS__", chars))
print(out, out.stat().st_size)
