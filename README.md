# Det sker i Gudhjem

**https://detskerigudhjem.dk** – byens kalender: film i Scala, koncerter og gudstjenester, museer, svømmehal, børneaktiviteter og spisesteder med åbent. Lavet af [Klippen Hotel](https://www.hotelklippen.com).

## Sådan virker det
- `build.py` henter data fra Klippens gæste-app (`https://therns.dk/app/gudhjem.json`) og bygger én statisk side i `site/` ud fra `template.html`.
- Data samles hver nat i Klippens app-repo (film fra Scala/bioguiden, svømmehallens kalender, KultuNaut, Gudhjem Museum, åbningstider). Klippens egne events og åbningstider for Café Plateau og Jylkat rettes også dér (`DATA.events` og `DATA.venues`).
- GitHub Actions (`.github/workflows/byg.yml`) bygger og udgiver siden hver nat, midt på dagen og ved hver ændring.
- `data.json` er sidste gode udgave af data – bruges hvis appen ikke svarer.

## Rette udseende eller tekster
Ret i `template.html` (tekster, farver, opbygning) eller `build.py` (hvad der vises). Gem → siden opdateres automatisk efter et par minutter.

## Domæne
Domænet ligger hos one.com og peger på GitHub Pages (A-records 185.199.108.153, .109.153, .110.153, .111.153 og `www` som CNAME til `jannie-spec.github.io`).
