"""Tegner forsidens Gudhjem-tegning (design/forside-tegning-v3.svg).
Set fra havet, spejlvendt efter Jannies ønske: Grevens Dal til venstre på klipperne, kirken på bakken,
Førder og Therns i Brøddegade, Skt. Jørgens Gaard ved havnen og røgeriet til højre ved vandet."""

def house(x, base, w, h, wall, roof, wins=2):
    o = [f'<rect x="{x}" y="{base-h}" width="{w}" height="{h}" fill="{wall}"/>',
         f'<path d="M{x-5} {base-h+2} L{x+w/2} {base-h-h*0.55} L{x+w+5} {base-h+2}Z" fill="{roof}"/>']
    for i in range(wins):
        wx = x + (i+1)*w/(wins+1) - 5
        o.append(f'<rect x="{wx:.0f}" y="{base-h+h*0.35:.0f}" width="10" height="12" fill="#3f6670"/>')
    return "".join(o)

W = "#f6f3ec"; ROOF = "#b4533a"; WIN = "#3f6670"
o = ['<svg xmlns="http://www.w3.org/2000/svg" class="town v3" viewBox="0 0 1200 380" preserveAspectRatio="xMidYMax meet" role="img" aria-label="Tegning af Gudhjem set fra havet: Klippens hvide hotel på klipperne ved Grevens Dal, kirken på bakken, Førder og Therns i Brøddegade, den røde Skt. Jørgens Gaard ved havnen og røgeriets skorstene">',
     '<circle cx="110" cy="78" r="42" fill="#f2c46b" opacity=".75"/>',
     # landskab, huse og havn tegnes i den oprindelige retning og spejles
     '<g transform="translate(1200 0) scale(-1 1)">',
     '<path d="M0 230 C140 205 270 175 400 160 C500 148 560 112 630 108 C710 104 770 140 860 140 C960 140 1060 150 1200 175 L1200 380 L0 380Z" fill="#c3cfc0"/>',
     '<path d="M0 290 C120 280 220 272 330 262 C440 252 520 258 570 284 L740 286 C800 250 860 214 940 206 C1040 198 1120 204 1200 220 L1200 380 L0 380Z" fill="#9fb09b"/>',
     '<path d="M740 286 C800 250 860 214 940 206 C1040 198 1120 204 1200 220 L1200 318 C1100 324 980 316 880 322 C820 326 770 318 740 306Z" fill="#a8998e"/>',
     '<g stroke="#8a7b70" stroke-width="3" fill="none" stroke-linecap="round" opacity=".7"><path d="M820 262 l18 26 l-6 22"/><path d="M930 230 l-10 34 l16 36"/><path d="M1040 222 l12 40 l-8 40"/><path d="M1140 228 l-14 30 l10 44"/></g>']
o.append('<g opacity=".95">')
for x, b, w, h, wall, roof, n in [(470,250,52,38,W,"#e37b5b",1),(530,236,48,36,"#f2dfa8","#e37b5b",1),(690,200,54,38,W,"#e37b5b",2),(750,214,46,34,"#f2dfa8","#e37b5b",1),(560,186,46,34,W,"#e37b5b",1),(420,212,44,32,"#f2dfa8","#e37b5b",1),(330,236,40,30,W,"#e37b5b",1)]:
    o.append(house(x, b, w, h, wall, roof, n))
o.append('</g>')
o.append('<path d="M0 312 C200 304 400 318 600 308 C800 298 1000 314 1200 306 L1200 380 L0 380Z" fill="#c6d8d9"/>')
o.append('<g fill="#8e9f8b"><rect x="560" y="290" width="12" height="40"/><rect x="560" y="326" width="190" height="10"/><rect x="738" y="296" width="12" height="40"/></g>')
o.append('<g fill="none" stroke="#3f6670" stroke-width="3" stroke-linecap="round" opacity=".55"><path d="M60 344 q14 -8 28 0 t28 0"/><path d="M330 356 q14 -8 28 0 t28 0"/><path d="M860 350 q14 -8 28 0 t28 0"/><path d="M1070 362 q14 -8 28 0 t28 0"/></g>')
o.append('</g>')
# både i havnen (tegnes efter spejlingen, så sejlet vender rigtigt)
o.append('<g transform="translate(540 306)"><path d="M0 10 L56 10 L47 22 L8 22Z" fill="#b4533a"/><rect x="26" y="-14" width="4" height="24" fill="#302f2f"/><path d="M30 -12 L47 6 L30 6Z" fill="#f6f3ec"/></g>')
o.append('<g transform="translate(488 312)"><path d="M0 8 L40 8 L34 18 L6 18Z" fill="#3f6670"/><rect x="14" y="-6" width="10" height="14" fill="#f6f3ec"/></g>')

# Kirken – grå, øverst på bakken
o.append('<g transform="translate(526 112)"><rect x="0" y="34" width="74" height="40" fill="#bfc3bf"/><rect x="-16" y="4" width="28" height="70" fill="#bfc3bf"/><path d="M-20 6 L-2 -22 L16 6Z" fill="#4c5553"/><path d="M-5 36 L37 12 L79 36Z" fill="#8f9592"/><rect x="-7" y="24" width="10" height="14" rx="5" fill="#6f7674"/><rect x="30" y="50" width="12" height="24" rx="6" fill="#6f7674"/></g>')

# Grevens Dal – Klippens hvide hotel på klipperne: højt hvidt hus med stejlt rødt tag og gavl, røde vinduer, rød træudbygning (Café Plateau) og flag
o.append('<g transform="translate(176 204)">'
         # hovedhus
         '<rect x="40" y="-74" width="86" height="74" fill="#ffffff"/>'
         '<path d="M34 -72 L83 -128 L132 -72Z" fill="#b4533a"/>'
         # frontgavl
         '<rect x="62" y="-96" width="42" height="40" fill="#ffffff"/><path d="M57 -94 L83 -124 L109 -94Z" fill="#b4533a"/>'
         '<g fill="#3f6670" stroke="#9a3b2b" stroke-width="3"><rect x="75" y="-88" width="16" height="16"/><rect x="50" y="-54" width="14" height="18"/><rect x="102" y="-54" width="14" height="18"/></g><rect x="74" y="-40" width="18" height="40" fill="#9a3b2b"/>'
         # rød træudbygning med hvide vinduer (caféen)
         '<rect x="-6" y="-34" width="70" height="34" fill="#a9442f"/><path d="M-10 -34 L68 -34 L64 -42 L-6 -42Z" fill="#7d3022"/>'
         '<g fill="#fff"><rect x="2" y="-26" width="12" height="14"/><rect x="20" y="-26" width="12" height="14"/><rect x="38" y="-26" width="12" height="14"/></g>'
         '<rect x="-6" y="-2" width="150" height="6" fill="#7a5c45"/>'
         # flagstang med Dannebrog
         '<rect x="140" y="-130" width="3" height="130" fill="#f6f3ec"/>'
         '<g transform="translate(143 -128)"><rect width="34" height="24" fill="#c8102e"/><rect x="10" width="5" height="24" fill="#fff"/><rect y="9.5" width="34" height="5" fill="#fff"/></g>'
         '</g>')

# Førder – gult hus i Brøddegade
o.append('<g transform="translate(684 158)"><rect x="0" y="0" width="64" height="44" fill="#f2dfa8"/><path d="M-5 2 L32 -22 L69 2Z" fill="#b4533a"/>'
         '<path d="M-4 14 L68 14 L64 26 L0 26Z" fill="#e37b5b"/><g fill="#fff"><path d="M8 14 L16 14 L14 26 L6 26Z"/><path d="M26 14 L34 14 L33 26 L25 26Z"/><path d="M44 14 L52 14 L52 26 L44 26Z"/></g>'
         f'<rect x="24" y="28" width="16" height="16" fill="{WIN}"/></g>')

# Therns – hvidt hus i to etager
o.append('<g transform="translate(766 168)"><rect x="0" y="0" width="74" height="60" fill="#ffffff"/><path d="M-6 2 L37 -30 L80 2Z" fill="#b4533a"/>'
         f'<g fill="{WIN}"><rect x="12" y="12" width="12" height="13"/><rect x="50" y="12" width="12" height="13"/><rect x="12" y="36" width="12" height="13"/><rect x="50" y="36" width="12" height="13"/></g>'
         '<rect x="31" y="36" width="12" height="24" fill="#7a5c45"/></g>')

# Skt. Jørgens Gaard – rød gård med sort bindingsværk ved havnen
o.append('<g transform="translate(864 228)"><rect x="0" y="0" width="140" height="46" fill="#a9442f"/><path d="M-6 2 L14 -26 L126 -26 L146 2Z" fill="#5a5f5d"/>'
         '<g stroke="#1f1f1f" stroke-width="4"><line x1="0" y1="22" x2="140" y2="22"/><line x1="28" y1="0" x2="28" y2="46"/><line x1="56" y1="0" x2="56" y2="46"/><line x1="84" y1="0" x2="84" y2="46"/><line x1="112" y1="0" x2="112" y2="46"/><line x1="0" y1="0" x2="140" y2="0"/></g>'
         '<g fill="#fff"><rect x="62" y="26" width="16" height="20"/><rect x="8" y="5" width="12" height="12"/><rect x="36" y="5" width="12" height="12"/><rect x="92" y="5" width="12" height="12"/><rect x="120" y="5" width="12" height="12"/></g></g>')

# Røgeriet – tre hvide skorstene ved vandet
o.append('<g transform="translate(1038 214)" fill="#f6f3ec"><path d="M0 70 L8 0 L22 0 L30 70Z"/><path d="M36 70 L44 6 L58 6 L66 70Z"/><path d="M72 70 L80 12 L94 12 L102 70Z"/><rect x="-10" y="64" width="122" height="34"/><path d="M87 10 C80 -8 104 -14 96 -32" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" opacity=".85"/></g>')
o.append('</svg>')
open("design/forside-tegning-v3.svg", "w", encoding="utf-8").write("\n".join(o) + "\n")
print("ok")
