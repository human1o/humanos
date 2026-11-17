#!/usr/bin/env python3
"""Write plisse/specimen.html: a self-contained specimen (fonts embedded).

Comparison fonts are built from upstream on the fly and subset to the text
they show: Allo itself (ROND 30) and Allo at roundness 0 and 100."""
import base64
import io
import re
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import build as B  # noqa: E402


def b64(data):
    return base64.b64encode(data).decode()


def woff2_bytes(font, text=None):
    if text:
        opts = subset.Options()
        opts.layout_features = ["*"]
        opts.flavor = "woff2"
        opts.notdef_outline = True
        sub = subset.Subsetter(opts)
        sub.populate(text=text)
        sub.subset(font)
    font.flavor = "woff2"
    buf = io.BytesIO()
    font.save(buf)
    return buf.getvalue()


def glyph_count():
    return len(TTFont(ROOT / "fonts" / "ttf" / "Plisse-Regular.ttf").getBestCmap())


CSS = r'''/* Layout: one quiet column on warm white, like a showroom wall; the letters are the only image. */
__FACES__
:root{
  --wall:#f5f5f3; --panel:#ffffff; --ink:#222220; --muted:#6b6a66; --rule:#dcdcd8; --stone:#a88e68; --dark:#0e0e0d; --on-dark:#ffffff;
  --font:"Plisse",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
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
.pillars{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px;background:var(--rule);border:1px solid var(--rule);border-radius:14px;overflow:hidden}
@media (max-width:820px){.pillars{grid-template-columns:1fr}}
.pillars > div{background:var(--panel);padding:22px 22px 24px;display:flex;flex-direction:column;gap:8px;min-width:0}
.pillars b{font-size:22px;font-weight:500;letter-spacing:-.01em;line-height:1.2}
.pillars p{color:var(--muted);font-size:15px}
code{font-family:inherit;font-feature-settings:"zero";background:var(--wall);border:1px solid var(--rule);border-radius:6px;padding:0 5px;font-size:.92em}
.app{display:grid;grid-template-columns:200px minmax(0,1fr);border:1px solid var(--rule);border-radius:16px;overflow:hidden;background:var(--panel);font-size:14px}
@media (max-width:760px){.app{grid-template-columns:1fr}.app nav{flex-direction:row;flex-wrap:wrap;border-right:0;border-bottom:1px solid var(--rule)}}
.app nav{display:flex;flex-direction:column;gap:2px;padding:18px 12px;border-right:1px solid var(--rule);background:var(--wall)}
.app nav b{font-size:17px;font-weight:600;letter-spacing:-.01em;padding:4px 10px 14px}
.app nav span{padding:7px 10px;border-radius:8px;color:var(--muted)}
.app nav span.on{background:var(--panel);color:var(--ink);font-weight:500;box-shadow:0 0 0 1px var(--rule)}
.appmain{padding:20px 22px 22px;display:flex;flex-direction:column;gap:18px;min-width:0}
.apphead{display:flex;justify-content:space-between;align-items:flex-end;gap:12px;flex-wrap:wrap}
.apphead h5{font-size:26px;font-weight:500;letter-spacing:-.02em;margin:4px 0 0}
.search{font-size:13px;color:var(--muted);border:1px solid var(--rule);border-radius:10px;padding:8px 12px;min-width:min(260px,100%)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.kpis div{border:1px solid var(--rule);border-radius:12px;padding:12px 14px;display:flex;flex-direction:column;gap:4px}
.kpis span{font-size:12px;color:var(--muted)}
.kpis b{font-size:22px;font-weight:600;letter-spacing:-.01em;font-variant-numeric:tabular-nums}
.orders{width:100%;border-collapse:collapse;font-size:13px}
.orders th{font-size:12px;font-weight:500;color:var(--muted);text-align:left;padding:8px 8px 8px 0;border-bottom:1px solid var(--rule)}
.orders td{padding:10px 8px 10px 0;border-bottom:1px solid var(--rule)}
.orders td:last-child,.orders th:last-child{text-align:right;padding-right:0;font-variant-numeric:tabular-nums}
.orders .code{font-feature-settings:"zero";font-weight:500}
.st{display:inline-block;font-size:12px;border-radius:999px;padding:2px 9px;background:var(--wall);border:1px solid var(--rule);white-space:nowrap}
.st.ok{background:var(--dark);color:var(--on-dark);border-color:var(--dark)}
.st.wait{color:var(--stone);border-color:var(--stone)}
@media (max-width:560px){.orders td:nth-child(2),.orders th:nth-child(2){display:none}}
footer{color:var(--muted);font-size:14px;border-top:1px solid var(--rule);padding-top:20px}
footer p{max-width:80ch}
footer a{color:inherit}
.vs3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border:1px solid var(--rule);border-radius:14px;overflow:hidden;background:var(--panel)}
.vs3 > div{padding:18px 18px 16px;display:flex;flex-direction:column;gap:8px;min-width:0}
.vs3 > div + div{border-left:1px solid var(--rule)}
.vs3 .big{font-size:clamp(64px,11vw,150px);line-height:1;letter-spacing:-.02em;white-space:nowrap;overflow:hidden;font-weight:700}
.vs3 small{font-size:12px;color:var(--muted)}
.vs3 .on small{color:var(--stone);font-weight:600}
@media (max-width:640px){.vs3{grid-template-columns:1fr}.vs3 > div + div{border-left:0;border-top:1px solid var(--rule)}}
.sizes{display:flex;flex-direction:column;gap:6px}
.sizes .row{display:grid;grid-template-columns:64px minmax(0,1fr);gap:12px;align-items:baseline}
.sizes .row small{font-size:12px;color:var(--muted)}
.sizes .row div{white-space:nowrap;overflow:hidden;text-overflow:clip}
.alts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px;background:var(--rule);border:1px solid var(--rule);border-radius:14px;overflow:hidden}
.alts > div{background:var(--panel);padding:16px 18px;display:flex;flex-direction:column;gap:6px;min-width:0}
.alts b{font-size:40px;font-weight:400;line-height:1.1}
.alts span{font-size:12px;color:var(--muted)}
.alts code{font-size:12px}
@media (max-width:640px){.alts{grid-template-columns:repeat(2,minmax(0,1fr))}}
'''

BODY = r'''
<main>
<section class="hero">
  <span class="label">Krój pisma Murèlle i Lamelio</span>
  <h1 class="mark">Plissé</h1>
  <p class="idea">Cienki arkusz złożony w równy, pionowy rytm. Krawędzie ma łagodne jak szlifowany kamień, a odstępy dopasowuje do rozmiaru, jak ściana lamel do światła.</p>
  <div class="meta"><span>400–700</span><span>wielkość optyczna 9–32, sama się ustawia</span><span>__COUNT__ znaków</span><span>pełna polszczyzna</span><span>licencja OFL</span></div>
  <div class="names">
    <div><b style="font-weight:400">Murèlle</b><span>400 Regular</span></div>
    <div><b style="font-weight:500">Lamelio</b><span>500 Medium</span></div>
    <div><b style="font-weight:600">Murèlle</b><span>600 SemiBold</span></div>
    <div><b style="font-weight:700">Lamelio</b><span>700 Bold</span></div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Filozofia</span>
  <h2>Plisa: arkusz, który się gnie, złożony w równy rytm</h2></div>
  <p class="lede">Plisa to cienki materiał złożony w pionowe fałdy tej samej szerokości. Murèlle to arkusz kamienia, który owija słup. Lamelio to ściana z lamel w równych odstępach. Plissé bierze z obu tylko to, co widać w literach, i nie dodaje niczego więcej.</p>
  <div class="pillars">
    <div><span class="n">Krawędź</span><b>Szlifowana, nie ostra i nie odlana</b><p>Narożniki są złagodzone tak jak krawędź arkusza kamienia: wyraźnie, ale bez zaokrąglania na siłę. To jedno ustawienie, takie samo w każdej literze.</p></div>
    <div><span class="n">Rytm</span><b>Odstępy idą za rozmiarem</b><p>W tabeli przy 12 px litery mają więcej powietrza, w nagłówku przy 64 px stoją ciaśniej i precyzyjniej. Przeglądarka dobiera to sama.</p></div>
    <div><span class="n">Płytka</span><b>Kamień w zerze</b><p>W numerach zamówień zero ma w środku małą płytkę, więc 0 nigdy nie myli się z O. Cyfry w tabeli stoją równo, łącznie z jedynką.</p></div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Skąd się wziął</span>
  <h2>Zbudowany na Allo, bez przerysowywania</h2></div>
  <p class="lede">Podstawą jest Allo Josha Pucketta (licencja OFL), wyrosły z Inter Rasmusa Anderssona: krój zrobiony do ekranów, z wielkością optyczną, cyframi tabelarycznymi, ułamkami i pełną łaciną. Plissé bierze go w wersji 1.0.1 i zmienia tylko to, czego nie da się zepsuć: ustawia oś zaokrąglenia, zawęża grubości, kieruje funkcję zero na inną z jego własnych cyfr, dokłada kerning tam, gdzie litery się stykały, i poprawia jedną cyfrę. Test w repozytorium porównuje każdą literę z Allo w czterech rozmiarach i grubościach: poza tabelaryczną jedynką wszystkie są identyczne.</p>
</section>

<section>
  <div class="law">
    <div><span class="n">Zasada 1</span><h3>Krawędź szlifowanego kamienia</h3>
      <p><strong>Zaokrąglenie ustawione na 30 ze 100.</strong> Przy 0 krój jest cięty ostro i robi się chłodny, przy 100 wygląda na odlany. 30 to krawędź arkusza po szlifie: przy dużym rozmiarze widać miękkość, przy małym zostaje precyzja. Allo ma przy 30 własne wzorce rysunku, więc to ustawienie zaprojektowane, a nie wyliczone.</p></div>
    <div></div>
  </div>
  <div class="vs3">
    <div><small>Ostra, 0</small><div class="big" style="font-family:Rond0">tRk.ł1</div></div>
    <div class="on"><small>Plissé, 30</small><div class="big">tRk.ł1</div></div>
    <div><small>Odlana, 100</small><div class="big" style="font-family:Rond100">tRk.ł1</div></div>
  </div>
</section>

<section>
  <div class="law">
    <div><span class="n">Zasada 2</span><h3>Rozmiar ustawia rytm</h3>
      <p><strong>Wielkość optyczna działa sama.</strong> Przy 12 px litery stoją luźniej i łatwiej je przeczytać w tabeli, przy 64 px ściślej, jak lamele ustawione do światła. Nie trzeba niczego włączać: przeglądarka robi to z rozmiaru tekstu. Po prawej ten sam tekst z jednym rysunkiem w każdym rozmiarze.</p></div>
    <div></div>
  </div>
  <div class="vs">
    <div><small>Plissé, rozmiar ustawia odstępy</small><div class="sizes">
      <div class="row"><small>12 px</small><div style="font-size:12px">Travertino Avorio · 1200 × 600 mm · 389,00 zł/m²</div></div>
      <div class="row"><small>16 px</small><div style="font-size:16px">Travertino Avorio · 1200 × 600 mm</div></div>
      <div class="row"><small>64 px</small><div style="font-size:64px;line-height:1.05;letter-spacing:-.01em">Lamelio</div></div></div></div>
    <div><small>Bez tego, jeden rysunek</small><div class="sizes off" style="font-optical-sizing:none">
      <div class="row"><small>12 px</small><div style="font-size:12px">Travertino Avorio · 1200 × 600 mm · 389,00 zł/m²</div></div>
      <div class="row"><small>16 px</small><div style="font-size:16px">Travertino Avorio · 1200 × 600 mm</div></div>
      <div class="row"><small>64 px</small><div style="font-size:64px;line-height:1.05;letter-spacing:-.01em">Lamelio</div></div></div></div>
  </div>
</section>

<section>
  <div class="law">
    <div><span class="n">Zasada 3</span><h3>Płytka w zerze</h3>
      <p><strong>Funkcja <code>zero</code> daje zero z kamienną płytką w środku,</strong> zamiast przekreślenia, które Allo ma pod tą funkcją. Przekreślone zero wygląda technicznie, a płytka pasuje do kroju. Włącza się ją na numerach zamówień, faktur i SKU, a w zwykłym tekście zero zostaje czyste.</p></div>
    <div></div>
  </div>
  <div class="vs">
    <div><small>Plissé, funkcja zero</small><div class="big" style="font-feature-settings:'zero';font-size:clamp(30px,4.6vw,64px)">MU-2026-01184</div><div class="line" style="font-feature-settings:'zero'">Kod O0O0 · Faktura FV/2026/0118</div></div>
    <div><small>Allo, funkcja zero</small><div class="big off" style="font-family:Allo;font-feature-settings:'zero';font-size:clamp(30px,4.6vw,64px)">MU-2026-01184</div><div class="line off" style="font-family:Allo;font-feature-settings:'zero'">Kod O0O0 · Faktura FV/2026/0118</div></div>
  </div>
</section>

<section>
  <div class="law">
    <div><span class="n">Zasada 4</span><h3>Jedynka nie stoi w dziurze</h3>
      <p><strong>W tabeli każda cyfra ma tę samą szerokość, więc wąska jedynka zostawia puste miejsce.</strong> Allo daje jej stopkę, ale „11” wciąż ma o 68 jednostek na 1000 więcej światła niż typowa para cyfr. W każdym z 12 wzorców Plissé poszerza stopkę i ustawia jedynkę według pomiaru białego pola. Wynik: „11” +5, „81” −7, w nagłówku najwyżej +13.</p></div>
    <div></div>
  </div>
  <div class="vs">
    <div><small>Plissé, cyfry tabelaryczne</small><div class="big" style="font-variant-numeric:tabular-nums;font-size:clamp(44px,7vw,92px)">12.11 · 1 111</div><div class="line" style="font-variant-numeric:tabular-nums">167,81 zł · 11 111,10 zł · 12.11.2026</div></div>
    <div><small>Allo, cyfry tabelaryczne</small><div class="big off" style="font-family:Allo;font-variant-numeric:tabular-nums;font-size:clamp(44px,7vw,92px)">12.11 · 1 111</div><div class="line off" style="font-family:Allo;font-variant-numeric:tabular-nums">167,81 zł · 11 111,10 zł · 12.11.2026</div></div>
  </div>
</section>

<section>
  <div class="law">
    <div><span class="n">Zasada 5</span><h3>Polskie litery w nagłówku się nie stykają</h3>
      <p><strong>W dużym rozmiarze i grubym kroju ł w Allo wchodziło na sąsiednie litery:</strong> „światło”, „zmarł”, „cło”, a także „Ąj” i „Tè”. Plissé mierzy każdą parę z 9 tysięcy w 12 wzorcach i dokłada kerning tylko tam, gdzie litery się stykały. Kerning zmienia się z rozmiarem i grubością, a żadna para nie stoi ciaśniej niż w Allo.</p></div>
    <div></div>
  </div>
  <div class="vs">
    <div><small>Plissé, 700</small><div class="big" style="font-weight:700;font-size:clamp(44px,7vw,92px)">światło zmarł</div><div class="line" style="font-weight:700;font-size:clamp(28px,4vw,48px)">Cło · Ąj · Tè · łf</div></div>
    <div><small>Allo, 700</small><div class="big off" style="font-family:Allo;font-weight:700;font-size:clamp(44px,7vw,92px)">światło zmarł</div><div class="line off" style="font-family:Allo;font-weight:700;font-size:clamp(28px,4vw,48px)">Cło · Ąj · Tè · łf</div></div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Alfabet i cyfry</span><h2>Pełny zestaw w jednej temperaturze</h2></div>
  <div class="set">
    <div>ABCDEFGHIJKLMNOPQRSTUVWXYZ</div>
    <div>abcdefghijklmnopqrstuvwxyz</div>
    <div>0123456789</div>
    <div class="sm">ĄĆĘŁŃÓŚŹŻ ąćęłńóśźż è é ß æ œ ø</div>
    <div class="sm">&amp; @ € $ % “ ” „ ” « » ( ) [ ] { } / → ↗ ✓ ± × ÷ ≤ ≥ ≠ ½ ¼ ¾ m² m³ 5′3″</div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Alternatywy</span><h2>Wszystko, co Allo ma w zanadrzu, zostaje</h2>
  <p class="lede">Domyślnie Plissé ma dwupiętrowe a, prostą pionową l jak lamelę i zamknięte cyfry. Alternatywy Allo działają dalej i włącza się je w CSS przez <code>font-feature-settings</code>.</p></div>
  <div class="alts">
    <div><b style="font-feature-settings:'ss01'">aąá</b><span><code>ss01</code> jednopiętrowe a</span></div>
    <div><b style="font-feature-settings:'ss02'">Il1 0</b><span><code>ss02</code> rozróżnienie I, l, 1, 0</span></div>
    <div><b style="font-feature-settings:'ss03'">469</b><span><code>ss03</code> otwarte 4, 6, 9</span></div>
    <div><b style="font-feature-settings:'cv03'">lł</b><span><code>cv03</code> l z ogonkiem</span></div>
    <div><b style="font-feature-settings:'liga'">ft tt ff</b><span><code>liga</code> wspólna poprzeczka, domyślnie</span></div>
    <div><b style="font-feature-settings:'frac'">1/2 3/4</b><span><code>frac</code> ułamki</span></div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Cyfry</span><h2>Cyfry jak litery najwyższej wagi</h2>
  <p class="lede">W tekście i nagłówkach cyfry są proporcjonalne. W tabelach i cennikach włącza się cyfry tabelaryczne (<code>font-variant-numeric: tabular-nums</code>): tam jedynka ma stopkę, a białe pole wokół niej jest takie jak przy innych cyfrach.</p></div>
  <div class="figs">
    <div><span class="label">Tabelaryczne, w cenniku</span><div class="col">12 480,00 zł<br>9 315,60 zł<br>1 111,10 zł<br>407,90 zł</div></div>
    <div><span class="label">Domyślne, w tekście</span><div class="prop">12 480,00 zł<br>9 315,60 zł<br>1 111,10 zł<br>407,90 zł</div></div>
    <div><span class="label">Jeden rysunek</span><div class="giant">2026</div></div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Akapit</span><h2>Tekst, który czyta się bez zmęczenia</h2></div>
  <div class="para">
    <div><small>16 px · 400</small><p style="font-size:16px;line-height:1.55">Murèlle to cienkie arkusze prawdziwego kamienia: trawertynu, wapienia, łupka. Są tak elastyczne, że owijają łuk, słup i narożnik ściany. Kamień, który się nie łamie, tylko gnie. Lamelio to ściany z lamel: pionowy rytm, ta sama szerokość, ten sam odstęp, a resztę robi światło. Żadnego blichtru, tylko ciepła biel, faktura i światło.</p></div>
    <div><small>13 px · 400 i 600</small><p style="font-size:13px;line-height:1.55">Zamówienie <b style="font-weight:600;font-feature-settings:'zero'">MU-2026-01184</b> zostało przyjęte. Flexible Stone, Travertino Avorio, format 1200 × 600 mm, 48 szt. Dostawa w czwartek, 19 listopada, na adres: ul. Źródlana 7, 50-541 Wrocław. Gwarancja jakości obejmuje każdą płytę; łączenia wykonujemy bez fug.</p>
      <small style="margin-top:14px">12 px · 600, wersaliki</small><p class="label" style="font-size:12px;color:var(--ink)">Panel partnera · Zamówienia (3) · Konfigurator ściany</p></div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Interfejs</span><h2>Plissé w panelu partnera</h2><p class="lede">Przykładowe dane. Tekst ma 13–14 px, etykiety 12 px, kwoty mają cyfry tabelaryczne, numery zamówień zero z płytką.</p></div>
  <div class="app">
    <nav><b>Murèlle</b><span class="on">Zamówienia</span><span>Produkty</span><span>Konfigurator ściany</span><span>Faktury</span><span>Ustawienia</span></nav>
    <div class="appmain">
      <div class="apphead"><div><span class="label">Panel partnera</span><h5>Zamówienia</h5></div><div class="search">Szukaj zamówienia, produktu…</div></div>
      <div class="kpis"><div><span>Wartość w listopadzie</span><b>48 912,40 zł</b></div><div><span>Zamówienia otwarte</span><b>7</b></div><div><span>Rabat partnerski</span><b>12%</b></div></div>
      <table class="orders">
        <tr><th>Zamówienie</th><th>Produkt</th><th>Status</th><th>Wartość</th></tr>
        <tr><td class="code">MU-2026-01184</td><td>Travertino Avorio, 48 szt.</td><td><span class="st ok">Wysłane</span></td><td>12 407,04 zł</td></tr>
        <tr><td class="code">MU-2026-01179</td><td>Ardesia Nera, 20 szt.</td><td><span class="st">W realizacji</span></td><td>6 180,00 zł</td></tr>
        <tr><td class="code">LA-2026-00412</td><td>Lamelio Dąb, 36 lameli</td><td><span class="st">W realizacji</span></td><td>9 315,60 zł</td></tr>
        <tr><td class="code">MU-2026-01160</td><td>Quarzite Rosso, 12 szt.</td><td><span class="st wait">Czeka na płatność</span></td><td>3 708,90 zł</td></tr>
      </table>
    </div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Karta produktu</span><h2>Plissé w sklepie</h2><p class="lede">Przykładowe dane, żeby pokazać krój w panelu B2B.</p></div>
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
      <div class="seg"><button id="tn" aria-pressed="false">Cyfry tabelaryczne</button><button id="zr" aria-pressed="false">Zero z płytką</button></div>
    </div>
    <div id="sample" contenteditable="true" spellcheck="false" aria-label="Tekst próbny">Zażółć gęślą jaźń. Plissé 12 480,00 zł</div>
  </div>
</section>

<section>
  <div class="head"><span class="label">Pliki</span><h2>Gotowe do sieci i do instalacji</h2></div>
  <div class="facts">
    <div><b>1 plik do sieci</b><span>font zmienny: grubość 400–700 i wielkość optyczna 9–32, ok. 190 kB</span></div>
    <div><b>4 pliki TTF</b><span>Regular, Medium, SemiBold, Bold, z hintingiem dla Windows</span></div>
    <div><b>__COUNT__ znaków</b><span>łacina europejska i wietnamska, pełna polszczyzna</span></div>
    <div><b>OFL 1.1</b><span>wolno używać komercyjnie</span></div>
  </div>
</section>

<footer><p>Plissé __VER__, krój pisma Murèlle i Lamelio. Na bazie <a href="https://github.com/joshpuckett/allo">Allo</a> 1.0.1 Josha Pucketta, który wyrósł z <a href="https://github.com/rsms/inter">Inter</a> Rasmusa Anderssona (oba na licencji SIL Open Font License 1.1). Plissé ustawia zaokrąglenie na 30, zawęża grubości do 400–700, poszerza stopkę tabelarycznej jedynki i ustawia ją według pomiaru, kieruje funkcję zero na zero z płytką, dokłada zmienny kerning tam, gdzie litery się stykały, poprawia metryki Windows tak, by żaden akcent nie był przycinany, i nadaje nowe nazwy.</p></footer>
</main>

<script>
(function(){
  var s=document.getElementById('sample'),sz=document.getElementById('sz'),so=document.getElementById('szo'),wt=document.getElementById('wt'),wto=document.getElementById('wto'),tn=document.getElementById('tn'),zr=document.getElementById('zr');
  var tab=false,zero=false;
  function apply(){
    var max=Math.max(12,(s.clientWidth-36)/3.2);
    s.style.fontSize=Math.min(+sz.value,max)+'px';so.textContent=sz.value;
    s.style.fontWeight=wt.value;wto.textContent=wt.value;
    s.style.fontVariantNumeric=tab?'tabular-nums':'normal';
    s.style.fontFeatureSettings=zero?'"zero"':'normal';
  }
  tn.addEventListener('click',function(){tab=!tab;tn.setAttribute('aria-pressed',String(tab));apply();});
  zr.addEventListener('click',function(){zero=!zero;zr.setAttribute('aria-pressed',String(zero));apply();});
  sz.addEventListener('input',apply);wt.addEventListener('input',apply);window.addEventListener('resize',apply);apply();
})();
</script>
'''


def nbsp(page):
    """Amounts never break: 12 480,00 zł, 1200 × 600 mm (only inside <main>)."""
    a, b = page.index("<main>"), page.index("</main>")
    body = page[a:b]
    body = re.sub(r"(\d) (?=\d{3}\b)", "\\1\u00a0", body)
    body = re.sub(r"(\d) (?=(zł|mm|szt|m²|×))", "\\1\u00a0", body)
    body = re.sub(r"× (?=\d)", "×\u00a0", body)
    return page[:a] + body + page[b:]


def main():
    up = TTFont(B.UPSTREAM)
    allo = woff2_bytes(B.pin(), "MU-2026-01184 Kod O0O0 Faktura FV/2026/0118 12.11 · 1 111 167,81 zł 11 111,10 12.11.2026 światło zmarł Cło · Ąj · Tè · łf")
    rond = {}
    for r in (0, 100):
        f = instancer.instantiateVariableFont(TTFont(B.UPSTREAM), {"ROND": r, "wght": (400, 700)})
        rond[r] = woff2_bytes(f, "tRk.ł1")
    vf = (ROOT / "fonts" / "web" / "Plisse[opsz,wght].woff2").read_bytes()
    faces = "\n".join([
        f'@font-face{{font-family:"Plisse";src:url(data:font/woff2;base64,{b64(vf)}) format("woff2");font-weight:400 700;font-style:normal;font-display:block}}',
        f'@font-face{{font-family:"Allo";src:url(data:font/woff2;base64,{b64(allo)}) format("woff2");font-weight:400 700;font-display:block}}',
        f'@font-face{{font-family:"Rond0";src:url(data:font/woff2;base64,{b64(rond[0])}) format("woff2");font-weight:400 700;font-display:block}}',
        f'@font-face{{font-family:"Rond100";src:url(data:font/woff2;base64,{b64(rond[100])}) format("woff2");font-weight:400 700;font-display:block}}',
    ])
    ver = f"{B.VERSION[0]}.{B.VERSION[1]:03d}"
    page = ('<meta charset="utf-8">\n<title>Plissé</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<style>\n'
            + CSS.replace("__FACES__", faces) + "</style>\n" + BODY)
    page = nbsp(page).replace("__COUNT__", str(glyph_count())).replace("__VER__", ver)
    out = ROOT / "specimen.html"
    out.write_text(page)
    print(out, out.stat().st_size)


if __name__ == "__main__":
    main()
