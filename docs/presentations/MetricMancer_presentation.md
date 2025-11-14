# MetricMancer

Effektiv och flexibel mätning för datadrivna beslut

______________________________________________________________________

## Vad är MetricMancer?

- Open source-verktyg för insamling, analys och visualisering av mätdata
- För utvecklare, analytiker och beslutsfattare
- Förenklar och automatiserar hanteringen av kodrelaterade metrics

______________________________________________________________________

## Varför behövs MetricMancer?

- Många har data, men saknar struktur och verktyg för analys
- Traditionella lösningar är ofta komplexa eller dyra
- MetricMancer erbjuder enkelhet, flexibilitet och öppen källkod

______________________________________________________________________

## Inspiration och metodik

- **MetricMancer är starkt inspirerat av koncepten i boken _Your Code as a Crime Scene_ av Adam Tornhill.**
- Många av KPI:erna och analysmetoderna bygger på ideér från boken kring kodforensik och förändringsanalys.

______________________________________________________________________

## Huvudfunktioner

- Insamling av metrics från flera datakällor (Git, Jira m.fl.)
- Automatiserade rapporter och dashboards
- Anpassningsbara mätningar och moduler
- Export i JSON, HTML och andra format

______________________________________________________________________

## Tekniska egenskaper

- Körs som CLI-verktyg eller Python-bibliotek
- Modulär och lätt att bygga ut
- Rapportexport (JSON, HTML, m.fl.)
- **Integration sker genom import av data från andra system – ej via eget API**
- Integrationer idag fokuserar på att hämta data (ex. Jira, Git) till MetricMancer

______________________________________________________________________

## Integrationer och API

- Stöd för att importera/exportera data (CSV, JSON)
- Kan hämta data via API från t.ex. Jira, Bitbucket
- JSON-export möjliggör vidare bearbetning i andra verktyg
- **MetricMancer exponerar inget eget API för externa anrop**
- Planerade funktioner: Utökad integration med dashboards och issue trackers

______________________________________________________________________

## Implementerade KPI:er (metrics)

- **Cyclomatic Complexity:** Mäts per funktion/metod (hur komplex koden är)
- **Code Churn:** Hur ofta filer ändras över tid (mått på instabilitet)
- **Hotspot Score:** Kombination av komplexitet och churn (identifierar riskfyllda filer)
- **Grade:** Sammanvägd bedömning (Low, Medium, High)

______________________________________________________________________

## Planerade KPI:er (metrics)

- **Code Ownership** *(nästa på tur att implementeras)*\
  Andel kodrader som ägs av respektive utvecklare (via git blame)
- Temporal Coupling (filer som ofta ändras samtidigt)
- Change Coupling (logisk koppling mellan koddelar)
- Author Churn / Knowledge Map (fördelning av kodkunskap)
- Defect Density (buggtäthet från issue trackers)
- Hotspot Evolution (hur hotspots förändras över tid)
- Complexity Trend (trend för kodkomplexitet)
- Code Age (hur gammal koden är)
- Test Coverage (testtäckning)
- Logical Coupling (samband i förändringar)

______________________________________________________________________

## Typiska användningsområden

- Övervakning av kodkvalitet och systemprestanda
- Uppföljning av affärsnyckeltal kopplat till utveckling
- Analys av leveransflöde och flaskhalsar
- Automatiserad rapportering för ledning och team

______________________________________________________________________

## Demo / Skärmbilder

*(Här kan du inkludera screenshots på rapporter, CLI-output etc.)*

______________________________________________________________________

## Kom igång

- Ladda ner från GitHub: https://github.com/CmdrPrompt/MetricMancer
- Se installationsguide och dokumentation
- Bidra eller ställ frågor via GitHub

______________________________________________________________________

## Sammanfattning

- MetricMancer gör metrics-hantering enkel och flexibel
- Integration via dataimport och export
- Främjar datadrivna beslut
- Testa redan idag!

______________________________________________________________________

## Kontakt & frågor

Namn: [Ditt namn]\
E-post: [Din e-post]\
GitHub: https://github.com/CmdrPrompt/MetricMancer
