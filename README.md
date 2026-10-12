# 🚂 Transport Fever Chronicles

**Ein lebendiger Atlas für mehrere Transport-Fever-3-Spielstände.** Nicht nur ein Dashboard, sondern ein historisches Archiv für Städte, Inseln, Eisenbahnen, Industrieketten und die Geschichten, die sich aus einer Spielwelt ergeben.

## Erste Welt: Archipel des Alizés · 1900–1911

Ein tropisches französisch geprägtes Archipel. Die *Société des Routes et des Rails* verbindet fünf Hauptinselstädte mit den Außeninseln Roche-Noire und Montfougère.

### Aktuell: Weihnachtsbericht vom 24. Dezember 1911

**Quelle:** TF3-Mod, Messung 12. Oktober 2026 um 06:57:34 (MESZ). Der Weihnachtsbericht dokumentiert:

- **50 Städte** und **16.245 Einwohner** (April 1911: 15.837; +408)
- **95 Linien** mit **582 zugeordneten Fahrzeugen**, 5.919 belegten von 11.626 Kapazitätseinheiten (gemischte Messgröße)
- **108 Industriebetriebe**: 78 aktiv, 30 im Export als gestoppt markiert
- Erstmals **Produktion, Versand und Zulieferung pro Jahr für alle 108 Industrien** mit Input-/Output-Rezepten
- **95 Linien** mit Takt, wartenden Fahrgästen, Wartezeit und Warenalter
- Neue Industrien wie Péronne Fahrzeugfabrik sowie neue Bus- und Verkehrsangebote rund um Roche-Noire

**[Weihnachtsbericht 1911 mit interaktiven Filtern öffnen](saves/archipel-des-alizes/weihnachten-1911.html)**

**Historische Stände bleiben getrennt:**

- [Wirtschaftsbericht April 1911](saves/archipel-des-alizes/1911.html): 85 Linien, Jahresbilanzen und 61.164.100 Kontostand. **Die Finanzwerte sind nicht Dezemberwerte.**
- [Langzeitmonitor mit Sitzungsverläufen](saves/archipel-des-alizes/index.html?view=monitor#overview): laufend aus dem Spielemonitor hochgeladen (`WEBSITE_AKTUALISIEREN.bat` im Spielmonitor bzw. `python scripts/publish-monitor.py`). Hochgeladen werden nur Dateien, deren Ansicht sich geändert hat. Das Dossier „Zehn Jahre Archipel“ bleibt auf dem eingefrorenen Monitorstand vom 11.10.2026 (`data/monitor-20261011/`).
- [Weltatlas und Archiv vom März 1910](saves/archipel-des-alizes/index.html?view=archive#atlas) mit älteren Bedarfs- und Industrie-Snapshots.

Die Daten stehen datiert in `saves/archipel-des-alizes/data/`; die Zuordnung der Snapshot-Dateien erfolgt ausschließlich über `manifest.json`.

### Historisches Dossier „Zehn Jahre Archipel“

Die illustrierte Langform-Seite über die Jahre 1900 bis 1910 bleibt unter [Sonderausgabe](saves/archipel-des-alizes/jahrzehnt.html) erhalten. Sie trennt belegte Messwerte, Rekonstruktion, Fiktion und redaktionelle Einordnung. Die vom Monitor abgeleiteten historischen Kennzahlen werden mit `node scripts/build-decade.mjs --check` geprüft.

### Zum Archiv

- **Repository:** https://github.com/alexmondragonwrites-glitch/Transport-Fever-Chronicles
- **GitHub Pages:** https://alexmondragonwrites-glitch.github.io/Transport-Fever-Chronicles/
- **Aktueller Bericht:** https://alexmondragonwrites-glitch.github.io/Transport-Fever-Chronicles/saves/archipel-des-alizes/weihnachten-1911.html

## Methodik und Datenqualität

Der Export vom **24. Dezember 1911** unterscheidet **Jahresproduktion**, **Jahresversand**, **Jahreszulieferung** und den aktuellen Status einer Industrie. Darum können Betriebe aktuell auf „gestoppt“ stehen, obwohl das laufende Spieljahr bereits positive Produktions- oder Versandmengen hatte. Ein positiver Produktionswert bei Versand 0 beweist nicht, dass alle Güter verderben oder ungenutzt bleiben.

Warenalter ist **keine abgeschlossene Transportzeit**. Belegung ist eine Momentaufnahme, aus der sich weder ein gesicherter Dauerengpass noch die Jahresrentabilität einer Linie ableiten lässt. Summierte Belegungen mehrerer Verkehrsträger mischen Personen- und Frachteinheiten und sind nur als technische Gesamtgröße zu interpretieren. Die Jahres-Betriebsbilanzen stammen **ausschließlich aus dem April-1911-Export**. Der Dezemberstand enthält keine neue Kontostands- oder Jahresbilanzangabe.

Die historische Unstimmigkeit aus April 1911 (487 Fahrzeuge in der Übersicht, aber 465 in den 85 Einzellinien) wird weiterhin als offener Prüfpunkt behandelt und nicht rückwirkend verändert.

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
