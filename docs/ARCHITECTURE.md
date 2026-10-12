# Transport Fever Chronicles · Architektur

## Ziel und Prinzipien

Ein Repository für beliebig viele Transport-Fever-3-Spielstände. Jeder Save hat ein eigenes Verzeichnis, ein eigenes Zeitmodell und eine unverwechselbare Kennung. Das Portal wird statisch über GitHub Pages ausgeliefert und benötigt weder Framework noch Backend.

Das Projekt überträgt bewährte Grundsätze des Finn-Harps-FM-Wikis auf einen Spielstands-Atlas:

1. **Daten vor Deutung**: belegte Ingame-Werte, Hypothesen und fiktive Zeitungsartikel sind sichtbar voneinander getrennt.
2. **Archiv statt Überschreiben**: frühere Exportstände bleiben als eigenständige JSON-Dateien erhalten.
3. **Manifest statt fester Verweise**: der jeweils aktuelle Stand wird pro Welt in `manifest.json` bestimmt.
4. **Save-Isolation**: gleiche Städtenamen in verschiedenen Saves kollidieren nicht.
5. **Kein falscher Kartenanspruch**: eine geografische Karte erscheint erst, wenn für die Welt echte Spielkoordinaten oder validierte Bildbezüge vorliegen.
6. **Reproduzierbarkeit**: Datenprüfer und GitHub Actions überwachen Referenzen und Kennzahlen.
7. **Ressourcenschonung**: reines HTML/CSS/JavaScript, keine externe Bibliothek, responsiv und ohne Tracking.

## Repository

```text
/
├── index.html                      # Weltportal
├── assets/
│   ├── app.js                      # Gesamtes Frontend, Datenzugriff, Filter und Charts
│   ├── styles.css                  # Gemeinsames Design (Farbvariablen, Komponenten)
│   ├── affiche-alizes.svg, rivage.svg  # Reiseplakat und Küstenband
│   └── fonts/                      # Playfair Display, Source Serif 4 (OFL, lokal)
├── data/
│   └── worlds.json                 # Weltregister
├── saves/
│   └── archipel-des-alizes/
│       ├── index.html              # Eigene Seite und URL der Welt
│       └── data/
│           ├── meta.json           # Name, Datum, Gesellschaft, Beschreibung
│           ├── manifest.json       # aktuelle Datenstände und Snapshot-Historie
│           ├── cities.json         # Historie der Stadtgrößen
│           ├── lines-1910-03.json
│           ├── industries-1910-03.json
│           ├── demand-1910-03.json
│           └── events.json         # Ereignisarchiv
├── scripts/
│   ├── import-watcher.mjs          # TSV-Import und Snapshot-Pflege
│   ├── new-save.mjs                # Neues Save-Gerüst und Registereintrag
│   └── validate-data.mjs           # Qualitätsregeln
├── .github/workflows/validate.yml
└── docs/
    ├── ARCHITECTURE.md
    └── WATCHER.md
```

## Datenmodell und wichtige Unterscheidungen

* Das Weltregister liefert IDs, Pfade und Labels; es enthält keine langen historischen Daten.
* `cities.json` enthält mehrere Datumswerte pro Stadt (`YYYY-MM`), nicht nur den aktuellen Stand.
* `lines-*.json` enthält `occupied` und `capacity` als **Momentaufnahme**. Ohne transportierte Menge und Gewinn pro Jahr darf aus der Belegung keine Wirtschaftlichkeit abgeleitet werden.
* `industries-*.json` enthält `tier`, `status` und optionale Hinweise. Im derzeitigen Export trägt die Spalte „Produktion“ den **Aktivitätsstatus**, nicht eine Produktionsmenge.
* `demand-*.json`: `missing` und `need` sind Bedarfswerte; `supplied = need - missing`. Nur die aktuell sieben dokumentierten Städte sind im Demand-Datensatz enthalten.
* `events.json`: `kind` ist `fakt`, `rekonstruktion` oder `fiktion`. Näherungsdaten bleiben ungenau und erhalten `precision`. Ältere Ereignisse werden nachträglich korrigiert, aber nicht still gelöscht.

## Erweiterung und Versionierung

Neue Exporte werden zu `lines-YYYY-MM-DD.json` / `industries-YYYY-MM-DD.json` geschrieben. Das Manifest wird auf den jüngsten Stand gesetzt und ältere Dateien bleiben vorhanden. Importierte Dateien werden bei gleichem Datum und Typ nicht ungefragt überschrieben. Das Feld `snapshots` bildet die Archivhistorie ab.

`new-save.mjs` legt eine Welt mit leeren, formal gültigen Datendomänen und Registereintrag an. Die UI behandelt noch leere Welten ohne Programmfehler.

Künftige Verbesserungen:
- Exakte Infrastrukturkoordinaten und Karten aus TF3
- Jahresdurchsatz und Betriebsbilanz pro Linie
- Richtungsspezifische Belegung und Fahrzeugklassen
- Produktionsrate, Lagerbestand, Engpassgrund pro Industriebetrieb
- Güteralter, Liegezeiten und Verlust durch Zeitlimits
- Automatische watcher-kompatible JSON-Exporte
- Querverlinkte Zeitungsartikel und Stadtchroniken
- Snapshotauswahl und Vergleich von Ingame-Zeitpunkten im Browser

## Entwicklung

Einfach `python -m http.server 8000` im Projektroot starten und `http://localhost:8000` öffnen. Direkte `file://`-Zugriffe sind wegen `fetch` nicht vorgesehen.

Syntax prüfen: `node --check assets/app.js`.
Daten prüfen: `node scripts/validate-data.mjs`.
CI läuft bei Pushes auf `main` und Pull Requests.

## Gestaltung

Leitbild „Compagnie des Antilles, um 1905“: Papiergrund, Didot-Überschriften (Playfair Display), Lesetext in Source Serif 4, Reiseplakat und Küstenband als SVG, Madras-Karo als Band unter Kopf- und über Fußleiste. Alle Farben stehen als Variablen in `assets/styles.css`; Kopf-/Fußleiste und der Dossierkopf setzen sie lokal auf Nachtfarben um. Die bisherigen Variablennamen (`--gold`, `--mint`, `--red`, `--blue`) bleiben und bezeichnen die Druckfarben auf Papier. Ältere Scripts zeichnen Diagramme mit festen Farben der früheren Nachtpalette; ein Block am Ende von `styles.css` ordnet diese Werte per Attributselektor den neuen Diagrammfarben zu. Neue Diagramme sollten die Variablen direkt nutzen (CSS-Klassen oder `style="stroke:var(--series-1)"`; in SVG-Attributen wie `stroke="…"` wirken CSS-Variablen nicht). Schriften werden lokal ausgeliefert, damit keine Anfragen an fremde Server gehen. Kontrast nach WCAG AA wurde für alle Seiten und Reiter geprüft.
