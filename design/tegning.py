"""Tegner forsidens Gudhjem-tegning (design/forside-tegning-v4.svg), set fra havet.
Fra venstre: Klippen/Grevens Dal på klipperne med kirken bagved, mange huse op ad bakken, Therns og Førder,
flere huse, Skt. Jørgens Gaard (trelænget, åben mod vandet) og røgeriets gule skorstene. Christiansøbåden på vandet."""

WIN = "#3f6670"; RED = "#a9442f"; TIMBER = "#1f1f1f"

def house(x, base, w, h, wall, roof, wins=2, door=False):
    o = [f'<rect x="{x}" y="{base-h}" width="{w}" height="{h}" fill="{wall}"/>',
         f'<path d="M{x-5} {base-h+2} L{x+w/2} {base-h-h*0.55:.0f} L{x+w+5} {base-h+2}Z" fill="{roof}"/>']
    for i in range(wins):
        wx = x + (i+1)*w/(wins+1) - 5
        o.append(f'<rect x="{wx:.0f}" y="{base-h+h*0.3:.0f}" width="10" height="11" fill="{WIN}"/>')
    if door:
        o.append(f'<rect x="{x+w/2-5:.0f}" y="{base-16}" width="10" height="16" fill="#7a5c45"/>')
    return "".join(o)

o = ['<svg xmlns="http://www.w3.org/2000/svg" class="town v4" viewBox="0 0 1200 380" preserveAspectRatio="xMidYMax meet" role="img" aria-label="Tegning af Gudhjem set fra havet: Klippens hvide hotel på klipperne ved Grevens Dal med kirken bagved, husene op ad bakken, Therns, Skt. Jørgens Gaard ved havnen, røgeriets gule skorstene og Christiansøbåden">',
     '<circle cx="1100" cy="70" r="40" fill="#f2c46b" opacity=".75"/>',
     # landskab og havn (oprindelig tegning spejlet: klipperne til venstre)
     '<g transform="translate(1200 0) scale(-1 1)">',
     '<path d="M0 230 C140 205 270 175 400 160 C500 148 560 112 630 108 C710 104 770 140 860 140 C960 140 1060 150 1200 175 L1200 380 L0 380Z" fill="#c3cfc0"/>',
     '<path d="M0 290 C120 280 220 272 330 262 C440 252 520 258 570 284 L740 286 C800 250 860 214 940 206 C1040 198 1120 204 1200 220 L1200 380 L0 380Z" fill="#9fb09b"/>',
     '<path d="M740 286 C800 250 860 214 940 206 C1040 198 1120 204 1200 220 L1200 318 C1100 324 980 316 880 322 C820 326 770 318 740 306Z" fill="#a8998e"/>',
     '<g stroke="#8a7b70" stroke-width="3" fill="none" stroke-linecap="round" opacity=".7"><path d="M820 262 l18 26 l-6 22"/><path d="M930 230 l-10 34 l16 36"/><path d="M1040 222 l12 40 l-8 40"/><path d="M1140 228 l-14 30 l10 44"/></g>',
     '</g>']

# Gudhjem Mølle – hvid hollandsk mølle bagved, mellem Grevens Dal og kirken
o.append('<g transform="translate(298 160) scale(.72)">'
         '<path d="M-20 0 L-13 -66 L13 -66 L20 0Z" fill="#ffffff"/>'
         '<rect x="-24" y="-30" width="48" height="4" fill="#5a5f5d"/>'
         '<path d="M-15 -66 C-15 -84 15 -84 15 -66Z" fill="#4c5553"/>'
         '<g transform="translate(0 -72) rotate(20)" fill="#f6f3ec" stroke="#6f7674" stroke-width="2">'
         '<rect x="-3" y="-58" width="6" height="116" fill="#6f7674" stroke="none"/><rect x="-58" y="-3" width="116" height="6" fill="#6f7674" stroke="none"/>'
         '<rect x="3" y="-56" width="12" height="44"/><rect x="-15" y="12" width="12" height="44"/><rect x="12" y="3" width="44" height="12"/><rect x="-56" y="-15" width="44" height="12"/></g>'
         '<circle cx="0" cy="-72" r="4" fill="#4c5553"/>'
         '<rect x="-5" y="-16" width="10" height="16" fill="#7a5c45"/><rect x="-4" y="-50" width="8" height="10" fill="#3f6670"/>'
         '</g>')

# Kirken – grå, bagved og til højre for Grevens Dal, højt på bakken
o.append('<g transform="translate(346 108)"><rect x="0" y="30" width="70" height="38" fill="#bfc3bf"/><rect x="-14" y="2" width="26" height="66" fill="#bfc3bf"/>'
         '<path d="M-18 4 L-1 -22 L16 4Z" fill="#4c5553"/><path d="M-5 32 L35 10 L75 32Z" fill="#8f9592"/>'
         '<rect x="-6" y="20" width="10" height="13" rx="5" fill="#6f7674"/><rect x="29" y="46" width="11" height="22" rx="5.5" fill="#6f7674"/></g>')

# Mange huse op ad bakken (bagerste række først)
o.append('<g>')
back = [(420,170,46,32,"#f6f3ec","#e37b5b",1),(500,160,50,34,"#f2dfa8","#b4533a",2),(584,156,46,32,"#efe3c8","#e37b5b",1),(668,164,46,32,"#f6f3ec","#b4533a",1)]
mid = [(444,206,50,34,"#f2dfa8","#e37b5b",2),(536,200,46,32,"#f6f3ec","#b4533a",1)]
front = [(476,242,48,32,"#f6f3ec","#e37b5b",1),(566,240,46,30,"#efe3c8","#e37b5b",1)]
for row in (back, mid, front):
    for x,b,w,h,wall,roof,n in row:
        o.append(house(x,b,w,h,wall,roof,n))
o.append('</g>')

# Therns – hvidt hus i to etager i Brøddegade, med Førder (gult) lige ved siden af
o.append('<g transform="translate(616 168)"><rect x="0" y="0" width="152" height="62" fill="#ffffff"/><path d="M-6 2 L22 -30 L130 -30 L158 2Z" fill="#b4533a"/>'
         f'<g fill="{WIN}"><rect x="14" y="12" width="12" height="13"/><rect x="44" y="12" width="12" height="13"/><rect x="96" y="12" width="12" height="13"/><rect x="126" y="12" width="12" height="13"/>'
         '<rect x="14" y="38" width="12" height="13"/><rect x="44" y="38" width="12" height="13"/><rect x="96" y="38" width="12" height="13"/><rect x="126" y="38" width="12" height="13"/><rect x="70" y="12" width="12" height="13"/></g>'
         '<rect x="70" y="38" width="12" height="24" fill="#7a5c45"/></g>')
o.append('<g transform="translate(776 186)"><rect x="0" y="0" width="56" height="44" fill="#f2dfa8"/><path d="M-5 2 L28 -22 L61 2Z" fill="#b4533a"/>'
         '<path d="M-3 14 L59 14 L56 25 L0 25Z" fill="#e37b5b"/><g fill="#fff"><path d="M8 14 L15 14 L14 25 L7 25Z"/><path d="M24 14 L31 14 L31 25 L24 25Z"/><path d="M40 14 L47 14 L48 25 L41 25Z"/></g>'
         f'<rect x="20" y="28" width="14" height="16" fill="{WIN}"/></g>')

# Lidt flere huse
o.append('<g>')
for x,b,w,h,wall,roof,n in [(800,160,44,30,"#efe3c8","#b4533a",1),(852,196,46,32,"#f6f3ec","#e37b5b",1)]:
    o.append(house(x,b,w,h,wall,roof,n))
o.append('</g>')

# Skt. Jørgens Gaard – trelænget rød gård med sort bindingsværk, åben ud mod vandet (Jylkat i gården)
sjg = ['<g transform="translate(884 236)">',
       # bagerste længe
       f'<rect x="0" y="-8" width="190" height="34" fill="{RED}"/><path d="M-4 -6 L12 -30 L178 -30 L194 -6Z" fill="#5a5f5d"/>',
       f'<g stroke="{TIMBER}" stroke-width="3"><line x1="0" y1="-8" x2="190" y2="-8"/><line x1="0" y1="9" x2="190" y2="9"/>' + "".join(f'<line x1="{x}" y1="-8" x2="{x}" y2="26"/>' for x in range(70, 130, 20)) + '</g>',
       '<g fill="#fff"><rect x="76" y="-3" width="9" height="9"/><rect x="96" y="-3" width="9" height="9"/><rect x="116" y="-3" width="9" height="9"/></g>',
       # gården mellem længerne
       '<rect x="56" y="26" width="78" height="22" fill="#cdbf9f"/>',
       '<g transform="translate(78 30)"><rect x="9" y="-14" width="2" height="18" fill="#302f2f"/><path d="M-4 -14 L10 -24 L24 -14Z" fill="#e37b5b"/><rect x="0" y="2" width="20" height="4" fill="#7a5c45"/></g>',
       '<g transform="translate(108 32)"><rect x="9" y="-14" width="2" height="16" fill="#302f2f"/><path d="M-4 -14 L10 -24 L24 -14Z" fill="#f6f3ec"/><rect x="0" y="0" width="20" height="4" fill="#7a5c45"/></g>']
for gx in (0, 134):  # de to sidelænger med gavlen mod vandet
    sjg.append(f'<rect x="{gx}" y="2" width="56" height="46" fill="{RED}"/><path d="M{gx-4} 4 L{gx+28} -30 L{gx+60} 4Z" fill="#474b4a"/><path d="M{gx+8} 0 L{gx+28} -20 L{gx+48} 0Z" fill="{RED}" stroke="{TIMBER}" stroke-width="3"/>'
               f'<g stroke="{TIMBER}" stroke-width="3" fill="none"><rect x="{gx}" y="2" width="56" height="46"/><line x1="{gx}" y1="24" x2="{gx+56}" y2="24"/><line x1="{gx+28}" y1="2" x2="{gx+28}" y2="48"/><line x1="{gx+14}" y1="2" x2="{gx+14}" y2="24"/><line x1="{gx+42}" y1="2" x2="{gx+42}" y2="24"/></g>'
               f'<g fill="#fff"><rect x="{gx+8}" y="30" width="10" height="11"/><rect x="{gx+38}" y="30" width="10" height="11"/></g>')
sjg.append('</g>')
o.append("".join(sjg))

# Røgeriet – gule skorstene ved vandet
o.append('<g transform="translate(1092 220)" fill="#efc95a"><path d="M0 64 L7 0 L19 0 L26 64Z"/><path d="M30 64 L37 6 L49 6 L56 64Z"/><path d="M60 64 L67 12 L79 12 L86 64Z"/>'
         '<rect x="-8" y="60" width="104" height="30" fill="#f6efd8"/><path d="M13 -2 C6 -20 30 -26 22 -44" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" opacity=".85"/></g>')

# Grevens Dal – Klippens hvide hotel på klipperne (vendt: caféudbygningen til højre, flaget til venstre)
o.append('<g transform="translate(160 204)">'
         '<rect x="10" y="-74" width="86" height="74" fill="#ffffff"/><path d="M4 -72 L53 -128 L102 -72Z" fill="#b4533a"/>'
         '<rect x="32" y="-96" width="42" height="40" fill="#ffffff"/><path d="M27 -94 L53 -124 L79 -94Z" fill="#b4533a"/>'
         '<g fill="#3f6670" stroke="#9a3b2b" stroke-width="3"><rect x="45" y="-88" width="16" height="16"/><rect x="20" y="-54" width="14" height="18"/><rect x="72" y="-54" width="14" height="18"/></g>'
         '<rect x="44" y="-40" width="18" height="40" fill="#9a3b2b"/>'
         f'<rect x="92" y="-34" width="70" height="34" fill="{RED}"/><path d="M88 -34 L166 -34 L162 -42 L92 -42Z" fill="#7d3022"/>'
         '<g fill="#fff"><rect x="100" y="-26" width="12" height="14"/><rect x="118" y="-26" width="12" height="14"/><rect x="136" y="-26" width="12" height="14"/></g>'
         '<rect x="-24" y="-2" width="190" height="6" fill="#7a5c45"/>'
         '<rect x="-18" y="-130" width="3" height="130" fill="#f6f3ec"/>'
         '<g transform="translate(-15 -128)"><rect width="34" height="24" fill="#c8102e"/><rect x="10" width="5" height="24" fill="#fff"/><rect y="9.5" width="34" height="5" fill="#fff"/></g>'
         '</g>')

# Havet, havnen og bådene
o.append('<path d="M0 306 C200 314 400 300 600 308 C800 318 1000 304 1200 312 L1200 380 L0 380Z" fill="#c6d8d9"/>')
o.append('<g fill="#8e9f8b"><rect x="450" y="296" width="12" height="40"/><rect x="450" y="326" width="190" height="10"/><rect x="628" y="290" width="12" height="40"/></g>')
o.append('<g transform="translate(540 306)"><path d="M0 10 L56 10 L47 22 L8 22Z" fill="#b4533a"/><rect x="26" y="-14" width="4" height="24" fill="#302f2f"/><path d="M30 -12 L47 6 L30 6Z" fill="#f6f3ec"/></g>')
o.append('<g transform="translate(488 312)"><path d="M0 8 L40 8 L34 18 L6 18Z" fill="#3f6670"/><rect x="14" y="-6" width="10" height="14" fill="#f6f3ec"/></g>')
# Christiansøbåden på vej ud
o.append('<g transform="translate(760 318)"><path d="M0 18 L120 18 L108 36 L10 36Z" fill="#f6f3ec"/><rect x="0" y="26" width="116" height="5" fill="#2c4f6b"/>'
         '<rect x="22" y="2" width="70" height="16" fill="#f6f3ec"/><g fill="#3f6670"><rect x="30" y="7" width="8" height="6"/><rect x="44" y="7" width="8" height="6"/><rect x="58" y="7" width="8" height="6"/><rect x="72" y="7" width="8" height="6"/></g>'
         '<rect x="56" y="-10" width="10" height="12" fill="#2c4f6b"/><path d="M128 30 q12 -6 24 0 t24 0" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".8"/></g>')
o.append('<g fill="none" stroke="#3f6670" stroke-width="3" stroke-linecap="round" opacity=".55"><path d="M60 344 q14 -8 28 0 t28 0"/><path d="M330 356 q14 -8 28 0 t28 0"/><path d="M960 356 q14 -8 28 0 t28 0"/><path d="M1090 346 q14 -8 28 0 t28 0"/></g>')
o.append('</svg>')
open("design/forside-tegning-v4.svg", "w", encoding="utf-8").write("\n".join(o) + "\n")
print("ok")
