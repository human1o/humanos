#!/usr/bin/env python3
"""Write lamina/specimen.html: a self-contained specimen (fonts embedded)."""
import base64
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent


def b64(path):
    return base64.b64encode(Path(path).read_bytes()).decode()


def word_paths(font_path, word, scale=1.0):
    f = TTFont(font_path)
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    x, out = 0, []
    for ch in word:
        g = gs[cmap[ord(ch)]]
        pen = SVGPathPen(gs)
        g.draw(TransformPen(pen, (1, 0, 0, 1, x, 0)))
        out.append(pen.getCommands())
        x += g.width
    return out, x


def glyph_count():
    return len(TTFont(ROOT / "fonts" / "ttf" / "Lamina-Regular.ttf").getBestCmap())


PAGE = r'''<meta charset="utf-8">
<title>Lamina</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
/* Layout: one quiet column on warm white, like a showroom wall; the letters are the only image. */
@font-face{font-family:"Lamina";src:url(data:font/woff2;base64,__VF__) format("woff2");font-weight:400 700;font-style:normal;font-display:block}
@font-face{font-family:"Lamina";src:url(data:font/woff2;base64,__VFI__) format("woff2");font-weight:400 700;font-style:italic;font-display:block}
@font-face{font-family:"NoTile";src:url(data:font/woff2;base64,__NT__) format("woff2");font-weight:400 700;font-display:block}
@font-face{font-family:"Upstream";src:url(data:font/woff2;base64,__UP__) format("woff2");font-weight:400 700;font-display:block}
@font-face{font-family:"NoForms";src:url(data:font/woff2;base64,__NF__) format("woff2");font-weight:400 700;font-display:block}
:root{
  --wall:#f5f5f3; --panel:#ffffff; --ink:#222220; --muted:#6b6a66; --rule:#dcdcd8; --stone:#a88e68; --dark:#0e0e0d; --on-dark:#ffffff;
  --font:"Lamina",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--wall:#141413;--panel:#1b1b19;--ink:#ecebe7;--muted:#9c9a94;--rule:#32312e;--stone:#c9ab7e;--dark:#ecebe7;--on-dark:#141413;color-scheme:dark}}
:root[data-theme="dark"]{--wall:#141413;--panel:#1b1b19;--ink:#ecebe7;--muted:#9c9a94;--rule:#32312e;--stone:#c9ab7e;--dark:#ecebe7;--on-dark:#141413;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--wall);color:var(--ink);font-family:var(--font);font-size:16px;line-height:1.5;-webkit-font-smoothing:antialiased;
  padding-left:max(20px,env(safe-area-inset-left,0px));padding-right:max(20px,env(safe-area-inset-right,0px));padding-block:0 120px}
main{max-width:1120px;margin:0 auto;display:flex;flex-direction:column;gap:104px}
.label{font-size:12px;font-weight:600;letter-spacing:.07em;text-transform:uppercase;color:var(--muted)}
h2{font-size:clamp(28px,3.6vw,44px);font-weight:400;letter-spacing:-.02em;line-height:1.06;margin:10px 0 0;text-wrap:balance}
p{margin:0;max-width:62ch}
section{display:flex;flex-direction:column;gap:30px}
.head{display:flex;flex-direction:column;gap:8px}
.lede{color:var(--muted)}
.hero{padding-top:clamp(48px,9vw,120px);gap:26px}
.mark{font-size:clamp(110px,27vw,340px);line-height:.82;letter-spacing:-.045em;margin:0 0 0 -.03em;font-weight:400}
.idea{font-size:clamp(20px,2.4vw,28px);line-height:1.3;max-width:36ch}
.meta{display:flex;flex-wrap:wrap;gap:8px 28px;color:var(--muted);font-size:14px}
.names{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1px;background:var(--rule);border:1px solid var(--rule);border-radius:14px;overflow:hidden}
.names div{background:var(--panel);padding:22px 22px 18px;display:flex;flex-direction:column;gap:6px;min-width:0}
.names b{font-size:clamp(42px,7.8vw,96px);line-height:1.04;letter-spacing:-.025em;white-space:nowrap}
.names span{font-size:12px;color:var(--muted)}
@media (max-width:640px){.names{grid-template-columns:1fr}}
.law{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:24px 48px;align-items:start}
@media (max-width:820px){.law{grid-template-columns:1fr}}
.law h3{font-size:24px;font-weight:500;letter-spacing:-.01em;margin:6px 0 10px}
.law p{color:var(--muted)}
.law p strong{color:var(--ink);font-weight:500}
.n{font-size:13px;color:var(--stone);font-weight:600}
.vs{display:grid;grid-template-columns:1fr 1fr;border:1px solid var(--rule);border-radius:14px;overflow:hidden;background:var(--panel)}
.vs > div{padding:18px 18px 16px;display:flex;flex-direction:column;gap:8px;min-width:0}
.vs > div + div{border-left:1px solid var(--rule)}
.vs .big{font-size:clamp(56px,10vw,124px);line-height:1.06;letter-spacing:-.015em;white-space:nowrap;overflow:hidden}
.vs .line{font-size:clamp(16px,1.9vw,21px);line-height:1.35}
.vs small{font-size:12px;color:var(--muted)}
.vs .off{color:var(--muted)}
@media (max-width:560px){.vs{grid-template-columns:1fr}.vs > div + div{border-left:0;border-top:1px solid var(--rule)}}
.overlay{border:1px solid var(--rule);border-radius:14px;background:var(--panel);padding:20px 18px 12px}
.overlay svg{width:100%;height:auto;display:block}
.overlay .ink path{fill:var(--ink)}
.overlay .ghost path{fill:none;stroke:var(--stone);stroke-width:5}
.overlay small{display:block;font-size:12px;color:var(--muted);margin-top:8px}
.set{display:flex;flex-direction:column;gap:8px}
.set div{font-size:clamp(30px,5.4vw,64px);line-height:1.14;overflow-wrap:anywhere}
.set .sm{font-size:clamp(22px,3.4vw,40px)}
.figs{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px}
.figs > div{border:1px solid var(--rule);border-radius:14px;background:var(--panel);padding:18px 20px;display:flex;flex-direction:column;gap:10px;min-width:0}
.figs .col{font-size:22px;line-height:1.45;font-variant-numeric:tabular-nums;text-align:right}
.figs .prop{font-size:22px;line-height:1.45;text-align:right;font-variant-numeric:proportional-nums}
.figs .giant{font-size:clamp(72px,10vw,120px);line-height:1;letter-spacing:-.02em}
.para{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:36px 48px}
.para > div{display:flex;flex-direction:column;gap:8px;min-width:0}
.para small{font-size:12px;color:var(--muted)}
.shop{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);border:1px solid var(--rule);border-radius:16px;overflow:hidden;background:var(--panel)}
@media (max-width:760px){.shop{grid-template-columns:1fr}}
.slab{min-height:360px;background:radial-gradient(120% 90% at 20% 15%,rgba(255,255,255,.55),transparent 60%),repeating-linear-gradient(97deg,rgba(120,96,64,.06) 0 3px,transparent 3px 11px),repeating-linear-gradient(83deg,rgba(120,96,64,.05) 0 2px,transparent 2px 17px),linear-gradient(160deg,#e9dfcf,#d9cab3 55%,#cbb89c);position:relative}
.slab span{position:absolute;left:18px;bottom:16px;font-size:12px;color:#5b4a33;letter-spacing:.06em;text-transform:uppercase;font-weight:600}
.card{padding:26px 26px 24px;display:flex;flex-direction:column;gap:18px;min-width:0}
.card h4{font-size:clamp(30px,3.6vw,40px);font-weight:500;letter-spacing:-.02em;line-height:1.04;margin:2px 0 0}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chips span{font-size:13px;border:1px solid var(--rule);border-radius:999px;padding:5px 11px}
.chips span.on{background:var(--dark);color:var(--on-dark);border-color:var(--dark)}
.prices{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}
.prices td,.prices th{padding:8px 0;border-bottom:1px solid var(--rule);font-size:14px;text-align:left}
.prices th{font-size:12px;font-weight:500;color:var(--muted)}
.prices td:last-child,.prices th:last-child{text-align:right}
.total{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap}
.total b{font-size:36px;font-weight:600;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.btns{display:flex;gap:10px;flex-wrap:wrap}
.btn{font-size:15px;font-weight:500;border-radius:11px;padding:11px 18px;border:1px solid var(--dark);background:var(--dark);color:var(--on-dark)}
.btn.ghost{background:transparent;color:var(--ink);border-color:var(--rule)}
.italic{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1px;background:var(--rule);border:1px solid var(--rule);border-radius:14px;overflow:hidden}
.italic div{background:var(--panel);padding:20px 20px 18px;font-style:italic;font-size:clamp(34px,4.6vw,56px);line-height:1.06;letter-spacing:-.02em;min-width:0}
.italic small{display:block;font-style:normal;font-size:12px;color:var(--muted);letter-spacing:0;margin-top:8px}
.tester{border:1px solid var(--rule);border-radius:14px;background:var(--panel);overflow:hidden}
.controls{display:flex;flex-wrap:wrap;gap:14px 26px;align-items:center;padding:14px 18px;border-bottom:1px solid var(--rule);font-size:13px;color:var(--muted)}
.controls label{display:flex;align-items:center;gap:10px}
.controls output{color:var(--ink);font-variant-numeric:tabular-nums;min-width:3ch}
.seg{display:flex;gap:6px;flex-wrap:wrap}
.seg button{font:inherit;font-size:13px;border:1px solid var(--rule);background:transparent;color:var(--ink);border-radius:999px;padding:5px 12px;cursor:pointer}
.seg button[aria-pressed=true]{background:var(--dark);color:var(--on-dark);border-color:var(--dark)}
input[type=range]{accent-color:var(--ink);width:150px}
button:focus-visible,input:focus-visible,[contenteditable]:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
#sample{padding:24px 18px 30px;font-size:64px;line-height:1.08;letter-spacing:-.02em;overflow-wrap:anywhere;min-height:2.3em}
.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1px;background:var(--rule);border:1px solid var(--rule);border-radius:14px;overflow:hidden}
.facts div{background:var(--panel);padding:16px 18px;display:flex;flex-direction:column;gap:4px}
.facts b{font-size:22px;font-weight:500}
.facts span{font-size:13px;color:var(--muted)}
footer{color:var(--muted);font-size:14px;border-top:1px solid var(--rule);padding-top:20px}
footer p{max-width:80ch}
footer a{color:inherit}
</style>

<main>
<section class="hero">
  <span class="label">Krój pisma Murèlle i Lamelio</span>
  <h1 class="mark">Lamina</h1>
  <p class="idea">Ciepły, precyzyjny grotesk w temperaturze ABC Diatype: brzuśce okrągłe jak arkusz kamienia owinięty wokół słupa, rytm równy jak ściana z lamel. Kropki są małymi płytkami kamienia.</p>
  <div class="meta"><span>400–700, font zmienny</span><span>prosty i kursywa</span><span>__COUNT__ znaków</span><span>pełna polszczyzna</span><span>licencja OFL</span></div>
  <div class="names">
    <div><b style="font-weight:400">Murèlle</b><span>400 Regular</span></div>
    <div><b style="font-weight:500">Lamelio</b><span>500 Medium</span></div>
    <div><b style="font-weight:600;font-style:italic">Murèlle</b><span>600 SemiBold Italic</span></div>
    <div><b style="font-weight:700">Lamelio</b><span>700 Bold</span></div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Skąd się wziął</span>
  <h2>Zbudowany na Instrument Sans, najokrąglejszym bliskim Diatype otwartym kroju</h2></div>
  <p class="lede">Zestawiliśmy z planszą Diatype ponad dziewięćdziesiąt otwartych grotesków, litera przy literze, w tych samych proporcjach, i zmierzyliśmy, jak bardzo każde O, e, s, 0 i 8 wypełnia swój prostokąt. Najbliżej był Instrument Sans (Rodrigo Fuenzalida, Jordan Egstad, licencja OFL): okrągłe brzuśce, poziomo cięte końcówki e, c, s, jednopiętrowe g, y z prostym ogonem, okrągłe 6 i 9. Lamina bierze go w szerokości 97 i grubości 430, czyli z tym samym pniem i tą samą szerokością co Diatype, a potem dokłada trzy zasady.</p>
</section>

<section>
  <div class="head"><span class="label">Ta sama plansza co Diatype</span><h2>Postaw obok swojej grafiki</h2></div>
  <div style="background:#6ba808;color:#fff;border-radius:14px;padding:22px 20px 26px;display:flex;flex-direction:column;align-items:center;gap:18px;overflow:hidden">
    <div style="font-size:12px">Lamina</div>
    <div style="font-size:clamp(26px,5.6vw,64px);line-height:1.02;text-align:center;letter-spacing:-.005em">Lamina Regular<br>EFGHIJKLMN<br>OPQRSTUVWXYZ<br>äbcdefghijklmnöpqrstu<br>vwxyz 0123456789<br>.,:;…!¡?¿‹›«»()[]{}\/|#%<br>$€£¢&amp;&lt;&gt;@©®•™°*</div>
  </div>
</section>

<section>
  <div class="law">
    <div><span class="n">Zasada 1</span><h3>Proporcje Diatype</h3>
      <p><strong>Szerokość, grubość i odstępy wzięte z Diatype, nie z bazy.</strong> Pień Regular ma tę samą grubość co w Diatype, litery są o 3 % węższe niż w Instrument Sans, a małe litery stoją ciaśniej, żeby alfabet miał tę samą długość co na planszy Diatype przy tej samej wysokości wersalików. Po prawej Instrument Sans bez zmian.</p></div>
    <div></div>
  </div>
  <div class="vs">
    <div><small>Lamina</small><div class="big">kamień</div><div class="line">Zamówienia partnerów przyjęte w tym tygodniu: 12 480,00 zł</div></div>
    <div><small>Baza bez zmian</small><div class="big off" style="font-family:Upstream">kamień</div><div class="line off" style="font-family:Upstream">Zamówienia partnerów przyjęte w tym tygodniu: 12 480,00 zł</div></div>
  </div>
</section>

<section>
  <div class="law">
    <div><span class="n">Zasada 2</span><h3>Kropka jak płytka</h3>
      <p><strong>Każda kropka to mała płytka kamienia z giętymi rogami.</strong> Arkusz kamienia nie ma ostrych krawędzi, więc kropka też nie: i, j, ż, ö, kropka, wielokropek, wykrzyknik, pytajnik, dwukropek, punktor, także w kursywie. W bazie kropki są ostrymi kwadratami.</p></div>
    <div></div>
  </div>
  <div class="vs">
    <div><small>Z zasadą</small><div class="big">żij!?</div><div class="line">Zażółć gęślą jaźń. Tak, tak!</div></div>
    <div><small>Bez zasady</small><div class="big off" style="font-family:NoTile">żij!?</div><div class="line off" style="font-family:NoTile">Zażółć gęślą jaźń. Tak, tak!</div></div>
  </div>
</section>

<section>
  <div class="law">
    <div><span class="n">Zasada 3</span><h3>Formy, które się gną</h3>
      <p><strong>Tam, gdzie baza ma dwie formy, Lamina wybiera tę bliższą Diatype i ją dociąga.</strong> R ma nogę wychodzącą z brzuśca i opadającą prawie pionowo. Ogonek Q zaczyna się w środku litery i kończy pod jej prawym bokiem; narysowaliśmy go od nowa według pomiaru z Diatype. Dolar i cent mają kreskę przeprowadzoną przez całą literę. Po prawej formy z bazy.</p></div>
    <div></div>
  </div>
  <div class="vs">
    <div><small>Z zasadą</small><div class="big">QR$¢</div><div class="line">Quarzite Rosso, Rivestimento</div></div>
    <div><small>Bez zasady</small><div class="big off" style="font-family:NoForms">QR$¢</div><div class="line off" style="font-family:NoForms">Quarzite Rosso, Rivestimento</div></div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Alfabet i cyfry</span><h2>Pełny zestaw w jednej temperaturze</h2></div>
  <div class="set">
    <div>ABCDEFGHIJKLMNOPQRSTUVWXYZ</div>
    <div>abcdefghijklmnopqrstuvwxyz</div>
    <div>0123456789</div>
    <div class="sm">ĄĆĘŁŃÓŚŹŻ ąćęłńóśźż è ß æ œ ø</div>
    <div class="sm">&amp; @ € $ % “ ” „ ” « » ( ) [ ] { } / → ↗ ± × ÷ ≤ ≥ ½</div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Cyfry</span><h2>Cyfry jak litery najwyższej wagi</h2>
  <p class="lede">Cyfry mają jeden rysunek. Domyślnie są tabelaryczne, więc ceny w kolumnie stoją jedna pod drugą bez żadnego CSS; w tekście ciągłym można przełączyć je na proporcjonalne.</p></div>
  <div class="figs">
    <div><span class="label">Domyślne, tabelaryczne</span><div class="col">12 480,00 zł<br>9 315,60 zł<br>1 111,10 zł<br>407,90 zł</div></div>
    <div><span class="label">Proporcjonalne</span><div class="prop">12 480,00 zł<br>9 315,60 zł<br>1 111,10 zł<br>407,90 zł</div></div>
    <div><span class="label">Jeden rysunek</span><div class="giant">2026</div></div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Akapit</span><h2>Tekst, który czyta się bez zmęczenia</h2></div>
  <div class="para">
    <div><small>16 px · 400</small><p style="font-size:16px;line-height:1.55">Murèlle to cienkie arkusze prawdziwego kamienia: trawertynu, wapienia, łupka. Są tak elastyczne, że owijają łuk, słup i narożnik ściany. Kamień, który się nie łamie, tylko gnie. Lamelio to ściany z lamel: pionowy rytm, ta sama szerokość, ten sam odstęp, a resztę robi światło. <i>Żadnego blichtru, tylko ciepła biel, faktura i światło.</i></p></div>
    <div><small>13 px · 400 i 600</small><p style="font-size:13px;line-height:1.55">Zamówienie <b style="font-weight:600">MU-2026-01184</b> zostało przyjęte. Flexible Stone, Travertino Avorio, format 1200 × 600 mm, 48 szt. Dostawa w czwartek, 19 listopada, na adres: ul. Źródlana 7, 50-541 Wrocław. Gwarancja jakości obejmuje każdą płytę; łączenia wykonujemy bez fug.</p>
      <small style="margin-top:14px">12 px · 600, wersaliki</small><p class="label" style="font-size:12px;color:var(--ink)">Panel partnera · Zamówienia (3) · Konfigurator ściany</p></div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Kursywa</span><h2>Prawdziwa kursywa w każdej grubości</h2></div>
  <div class="italic">
    <div style="font-weight:400">Kamień, który się nie łamie<small>Italic 400</small></div>
    <div style="font-weight:700">tylko gnie.<small>Bold Italic 700</small></div>
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
      <label for="wt">Grubość <input id="wt" type="range" min="400" max="700" value="400" step="1"><output id="wto">400</output></label>
      <label for="sz">Rozmiar <input id="sz" type="range" min="12" max="160" value="64"><output id="szo">64</output></label>
      <div class="seg"><button id="it" aria-pressed="false">Kursywa</button><button id="tn" aria-pressed="false">Cyfry proporcjonalne</button></div>
    </div>
    <div id="sample" contenteditable="true" spellcheck="false" aria-label="Tekst próbny">Zażółć gęślą jaźń. Murèlle 12 480,00 zł</div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Pliki</span><h2>Gotowe do sieci i do instalacji</h2></div>
  <div class="facts">
    <div><b>400–700</b><span>font zmienny oraz 4 grubości statyczne</span></div>
    <div><b>Prosty i kursywa</b><span>8 plików TTF z hintingiem dla Windows</span></div>
    <div><b>__COUNT__ znaków</b><span>łacina europejska, w tym pełna polszczyzna</span></div>
    <div><b>OFL 1.1</b><span>wolno używać komercyjnie</span></div>
  </div>
</section>

<footer><p>Lamina 4.000. Na bazie <a href="https://github.com/Instrument/instrument-sans">Instrument Sans</a> (Rodrigo Fuenzalida, Jordan Egstad, licencja SIL Open Font License 1.1). Lamina ustawia szerokość i grubość według Diatype, zagęszcza małe litery, zamienia kropki na płytki, rysuje nowy ogonek Q, wybiera formy R, $ i ¢, ustawia cyfry tabelaryczne jako domyślne, przenosi strzałki „-&gt;” i „www” z domyślnych ligatur do opcjonalnych i nadaje nowe nazwy.</p></footer>
</main>

<script>
(function(){
  var s=document.getElementById('sample'),sz=document.getElementById('sz'),so=document.getElementById('szo'),wt=document.getElementById('wt'),wto=document.getElementById('wto'),it=document.getElementById('it'),tn=document.getElementById('tn');
  var ital=false,tab=false;
  function apply(){
    var max=Math.max(12,(s.clientWidth-36)/3.2);
    s.style.fontSize=Math.min(+sz.value,max)+'px';so.textContent=sz.value;
    s.style.fontWeight=wt.value;wto.textContent=wt.value;
    s.style.fontStyle=ital?'italic':'normal';s.style.fontVariantNumeric=tab?'proportional-nums':'normal';
  }
  it.addEventListener('click',function(){ital=!ital;it.setAttribute('aria-pressed',String(ital));apply();});
  tn.addEventListener('click',function(){tab=!tab;tn.setAttribute('aria-pressed',String(tab));apply();});
  sz.addEventListener('input',apply);wt.addEventListener('input',apply);window.addEventListener('resize',apply);apply();
})();
</script>
'''


def nbsp(page):
    """Amounts never break: 12 480,00 zł, 1200 × 600 mm (only inside <main>)."""
    import re
    a, b = page.index("<main>"), page.index("</main>")
    body = page[a:b]
    body = re.sub(r"(\d) (?=\d{3}\b)", "\\1\u00a0", body)
    body = re.sub(r"(\d) (?=(zł|mm|szt|m²|×))", "\\1\u00a0", body)
    body = re.sub(r"× (?=\d)", "×\u00a0", body)
    return page[:a] + body + page[b:]


def main():
    web = ROOT / "fonts" / "web"
    ctl = ROOT / "build" / "control"
    html = (nbsp(PAGE).replace("__VF__", b64(web / "Lamina[wght].woff2"))
            .replace("__VFI__", b64(web / "Lamina-Italic[wght].woff2"))
            .replace("__NT__", b64(ctl / "notile.woff2"))
            .replace("__UP__", b64(ctl / "upstream.woff2"))
            .replace("__NF__", b64(ctl / "noforms.woff2"))
            .replace("__COUNT__", str(glyph_count())))
    out = ROOT / "specimen.html"
    out.write_text(html)
    print(out, out.stat().st_size)


if __name__ == "__main__":
    main()
