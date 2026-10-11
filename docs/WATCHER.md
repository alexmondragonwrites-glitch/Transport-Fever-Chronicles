# Watcher-Export und Import

## Exportanforderung an den TF3-Watcher

**Die beiden bereits unterstützten Formate sind tabulatorgetrennte Tabellen (TSV)**, so wie sie aus einer HTML-Tabelle kopiert werden können. Die Spaltenüberschriften und die Reihenfolge müssen stimmen.

### Linien & Auslastung

```tsv
Linie	Haltestellen	Fahrzeuge	Belegt	Kapazität	Auslastung
WC Passagiere,Holz,Bretter-Mon-Val-IC-1	2	3	120	120	100%
TP Passagiere-PordesAli-AnsDor-RE-1	8	10	551	960	57%
```

Aufruf:

```bash
node scripts/import-watcher.mjs --save archipel-des-alizes --kind lines --date 1910-04-01 --input export-linien.tsv
```

### Industrien

```tsv
Industrie	Stufe	Produktion
Scierie de l’Écorce	1	gestoppt · Wechsel wird geprüft
Pointe des Pêcheurs Konservenfabrik	1	aktiv
```

```bash
node scripts/import-watcher.mjs --save archipel-des-alizes --kind industries --date 1910-04-01 --input export-industrien.tsv
```

Der Importer prüft Zahlenspalten und Statuswerte, erzeugt eine neue datierte JSON-Datei und ergänzt `manifest.json`. Die frühere Datendatei bleibt unverändert. Bei einem Import mit neuerem Datum wird zusätzlich `meta.json` fortgeschrieben. Ein Export mit älterem Datum darf als Nachtrag archiviert werden, ersetzt aber nicht den neueren aktiven Stand. **Bestehende Dateien werden nicht überschrieben.**

### Was der Watcher als Nächstes zusätzlich ausgeben sollte

Empfohlene Reihenfolge:

| Datendomäne | Felder |
|---|---|
| Line metrics | stabiler Linien-Identifier, Spiel-Datum, Modus, Route und Stationen, Jahresdurchsatz nach Ware, Gewinn, Kosten, Fahrzeuge, Konfiguration |
| Direction | Auslastung je Richtung und Station, leere Rückfahrten, Haltezeit |
| Factory | stabiler Industrie-Identifier, Rezept, Eingangslager, Ausgangslager, aktuelle / max. Produktion, Statusgrund |
| Stations | Lagerbestände je Ware, wartende Einheiten, durchschnittliche Wartezeit, Verschleiß / Verderb |
| Geography | Welt-ID, Stadt- und Stationskoordinaten, Insel-ID und eindeutige Bahn-/Hafenknoten |
| Cities | Bedarf, gedeckte Menge, Bevölkerung, Lärm und Datum mit Einheiten |
| Events | Eröffnung, Umbau, Stilllegung, Investition, Quelle und exaktes Ingame-Datum |

Derzeit ist der Importer absichtlich auf die beiden vorhandenen und eindeutig parsebaren Tabellenformate begrenzt. Stadt- und Bedarfsmessungen werden bereits als JSON archiviert, aber ein automatischer TSV-Importer dafür ist noch nicht implementiert. Bitte nicht so tun, als könnten alle Exportvarianten schon direkt importiert werden.

## Neue Spielwelt

```bash
node scripts/new-save.mjs --id nordland-1920 --name "Nordland" --year 1920 --company "Nordbahn AG"
node scripts/validate-data.mjs
```

Danach den neuen Weltordner und `data/worlds.json` gemeinsam committen.
