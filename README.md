# 🚂 Transport Fever Chronicles

**Ein lebendiger Atlas für mehrere Transport-Fever-3-Spielstände.** Nicht nur ein Dashboard, sondern ein historisches Archiv für Städte, Inseln, Eisenbahnen, Industrieketten und die Geschichten, die sich aus einer Spielwelt ergeben.

## Erste Welt: Archipel des Alizés · 1900–1910

Ein tropisches französisch geprägtes Archipel. Die *Société des Routes et des Rails* verbindet fünf schnell wachsende Hauptinselstädte mit den jungen Handelsinseln Roche-Noire und Montfougère.

**Datenstand:** Spieljahr **13. März 1910**, dokumentiert am **11. Oktober 2026**. Der erste Import umfasst sieben Stadtgeschichten ab 1904, **80 Linien**, **448 Fahrzeuge**, **103 Industriebetriebe** und **27 Warenbedarfsposten** für sieben Städte. Die Zahlen sind Messungen und keine Wirtschaftsprognosen.

### Neu: vollständiger Monitorstand

Die Weltseite zeigt jetzt standardmäßig den Monitorstand bis **11. Juli 1910**: **50 Städte, 82 Linien, 474 Fahrzeuge und 105 Industriebetriebe**. Stadtwerte besitzen einen eigenen Detailstand (8. Juli 1910). Elf Aufzeichnungsstände sind auswählbar; Stadt- und Linienverläufe bleiben nach Sitzungen getrennt. Bekannte Aufnahmefehler werden angezeigt.

Das bisherige redaktionelle Archiv mit Weltatlas und Geschichten bleibt über „Chronik & Weltatlas · März 1910“ erreichbar. [Import, Quellen und Messgrenzen](docs/MONITOR.md).

### Zum Archiv

- **Repository:** https://github.com/alexmondragonwrites-glitch/Transport-Fever-Chronicles
- **Vorgesehene GitHub-Pages-URL:** https://alexmondragonwrites-glitch.github.io/Transport-Fever-Chronicles/
- **Erste Welt:** https://alexmondragonwrites-glitch.github.io/Transport-Fever-Chronicles/saves/archipel-des-alizes/

Die Pages-Links funktionieren, sobald GitHub Pages für das Repository in **Settings → Pages → Deploy from a branch → main / (root)** aktiviert wurde.

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
