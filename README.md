# 🚂 Transport Fever Chronicles

**Ein lebendiger Atlas für mehrere Transport-Fever-3-Spielstände.** Nicht nur ein Dashboard, sondern ein historisches Archiv für Städte, Inseln, Eisenbahnen, Industrieketten und die Geschichten, die sich aus einer Spielwelt ergeben.

## Erste Welt: Archipel des Alizés · 1900–1911

Ein tropisches französisch geprägtes Archipel. Die *Société des Routes et des Rails* verbindet fünf Hauptinselstädte mit den Außeninseln Roche-Noire und Montfougère.

### Aktuell: Wirtschaftsbericht April 1911

**Spieldatum:** 13. April 1911. **Messung:** 11. Oktober 2026, 19:19:55 (MESZ). Der aktuelle Bericht enthält:

- **50 Städte** mit Bevölkerungsentwicklung ab 1904 und **15.837 Einwohnern**
- **85 Linien** mit **465 einzeln zugeordneten Fahrzeugen**; die Weltübersicht nennt **487** (22 Differenz, Ursache unbekannt)
- **42,90 Mio.** addierte Linien-Betriebsbilanz des letzten Spieljahres (keine bestätigte Bilanz des Gesamtunternehmens)
- **Alle 85 Linien mit Takt, aktuellen Wartezeiten, Warenalter und Zeiten seit Abholung**
- **104 Industrieeinträge laut Weltübersicht**, davon **28 explizite Stillstandsbeobachtungen**; übrige aktuelle Zustände fehlen
- **61.164.100** Kontostand in der Spielwährung

**Direkt zum aktuellen Bericht:** [Wirtschaftsbericht April 1911](saves/archipel-des-alizes/1911.html)

Die Spielstand-Startseite führt nun zum neuesten Bericht. [Der Langzeitmonitor](saves/archipel-des-alizes/index.html?view=monitor#overview) zeigt frühere Messsitzungen bis Juli 1910, inklusive Rücksprünge und Aufzeichnungslücken. [Der archivierte Weltatlas](saves/archipel-des-alizes/index.html?view=archive#atlas) hält die redaktionelle Momentaufnahme vom März 1910 fest.

### Historisches Dossier „Zehn Jahre Archipel“

Die illustrierte Langform-Seite über die Jahre 1900 bis 1910 bleibt unter [Sonderausgabe](saves/archipel-des-alizes/jahrzehnt.html) erhalten. Sie trennt belegte Messwerte, Rekonstruktion, Fiktion und redaktionelle Einordnung. Die vom Monitor abgeleiteten historischen Kennzahlen werden mit `node scripts/build-decade.mjs --check` geprüft.

### Zum Archiv

- **Repository:** https://github.com/alexmondragonwrites-glitch/Transport-Fever-Chronicles
- **GitHub Pages:** https://alexmondragonwrites-glitch.github.io/Transport-Fever-Chronicles/
- **Aktueller Bericht:** https://alexmondragonwrites-glitch.github.io/Transport-Fever-Chronicles/saves/archipel-des-alizes/1911.html

## Methodik

Ein Bericht zu **1911** ist nicht dieselbe Datenbasis wie der ältere **1910er Monitor**: Die Bilanzsummen beziehen sich auf das letzte Spieljahr, Belegungen auf eine Momentaufnahme. Warenalter ist **keine abgeschlossene Transportzeit**. Die 28 gestoppten Industrien sind eine **unvollständige Auswahl**, keine Aussage über den Status aller 104 Betriebe. Datenunterschiede werden nicht durch Schätzung ausgeglichen.

## Funktionen

- Weltportal mit eigener URL pro Spielstand und Erweiterung über `data/worlds.json`
- Stadtregister mit Zeitreihen und Warenbedarf
- Filterbare Linienliste für Verkehrsträger und Belegung
- Industrieregister mit Aktivitätsstatus und Stufe
- Datierte Chronik mit Unterscheidung zwischen Fakten, Rekonstruktion und Fiktion
- Historische Snapshots, aktiver Stand durch Save-Manifest
- Node.js-Importer für Watcher-TSV-Exporte (Linien und Industrien)
- Automatische Validierung bei GitHub-Push und Pull Request

## Lokal ausführen

```bash
python -m http.server 8000
```

Dann http://localhost:8000 öffnen. Die statische Website benötigt keine Installation, kein Build-System und keine externen Pakete.

Daten und JavaScript prüfen:

```bash
node --check assets/app.js
node scripts/validate-data.mjs
```

## Neue Welt anlegen

```bash
node scripts/new-save.mjs --id neue-welt --name "Neue Welt" --year 1900
```

Danach ist sie als leeres, funktionierendes Save im Portal registriert. Detaillierte Anleitung: [Watcher-Import](docs/WATCHER.md) · [Architektur](docs/ARCHITECTURE.md).

## Projektprinzip

**Das Spiel ist die Quelle, die Chronik die Interpretation.** Nur tatsächlich beobachtete Werte sind als Fakten gekennzeichnet. Zeitungsartikel und gesellschaftliche Erzählungen sind ausdrücklich fiktional. Es werden keine exakten geografischen Koordinaten behauptet, solange sie nicht exportiert wurden.

Nicht offiziell mit dem Spieleentwickler verbunden.
