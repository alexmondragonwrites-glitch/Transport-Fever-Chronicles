# Monitoransicht – Archipel

Die Standardansicht zeigt den Spielemonitor-Export vom 11.10.2026, 18:00:52 (Europe/Berlin). Das frühere redaktionelle Archiv mit Weltatlas, Geschichten und März-1910-Tabellen bleibt über `?view=archive` erreichbar. Diese Quellen werden nicht still vermischt.

## Reproduzierbarer Import

```text
python scripts/import-monitor.py /absoluter/pfad/zum/Export/Pakete
node --check assets/monitor.js
node scripts/validate-monitor.mjs
node scripts/validate-data.mjs
```

Der Import prüft SHA256 und die Weltkennung jedes Sitzungspakets. Er schreibt `saves/archipel-des-alizes/data/monitor-20261011/`. Das kleine `index.json` nennt Quellen, Summen und Abschnittsdateien. Das Manifest referenziert es über `monitor`. Die Website lädt zunächst nur den neuesten Abschnitt; andere werden auf Auswahl geladen. Kein Abruf der 1,51-GB-Originaldatei im Browser.

## Bedeutung und Grenzen

- Alle 2.864 Originalmessungen bestimmen Endstände und Zählungen. Die 504 Detailmessungen liefern Linien- und Flottenverläufe. Keine künstlich hochgerechneten Zwischenwerte.
- Jeder Sitzungswechsel bildet eine Vergleichsgrenze. Zusätzlich erzeugt jeder Spielzeit-Rücksprung einen neuen Abschnitt. Wiederverwendete Sequenzen/Spielzeiten verschiedener Sitzungen werden nicht dedupliziert.
- Städte: letzter tatsächlich erfasster Stadtstand je Spielmonat und Abschnitt, jeweils mit Messzeit und Spieldatum. `housing_occupied` ist Wohnbelegung, `housing_capacity` (alternativ `population`) ist Wohnkapazität. Keine Gleichsetzung dieser Werte.
- Linien: `used`/`capacity` sind Momentbelegung; `waiting_count` und Haltewerte haben einen eigenen Zeitpunkt. `balance_year` ist eine rollierende API-Betriebsbilanz der aktuell zugeordneten Fahrzeuge, ohne Investitionen. Keine Summe über Messpunkte.
- Fehler aus der letzten Detailaufnahme bleiben sichtbar, auch wenn spätere Basismessungen fehlerfrei sind. Das Limit von 20 gemeldeten Fehlern kann weitere Fehler verdecken. Keine automatische Handlungsempfehlung aus diesen Ständen.
- Graphen verwenden tatsächliche Spielzeit auf der X-Achse. Aufzeichnungslücken über 90 Sekunden, nicht fortschreitende Spielzeit und fehlende Zahlen unterbrechen Verbindungen. Unbekannt bleibt `–`, echte Nullwerte bleiben Null.
- Produktionsstatus, Produktionsjahreswerte, Stadtversorgung und Logistik besitzen teilweise verschiedene Cachezeitpunkte. Die Oberfläche nennt sie in den jeweiligen Details.
- Stations- und Bordwarenstichproben sind begrenzt. Keine behaupteten Lieferketten oder Lieferzeiten aus dem Verschwinden einzelner Objekte. Unvalidierte Qualitäts-/Fahrzeitskalen werden nicht zu Prozentwerten oder Umlaufzeiten umgedeutet.
- DB-Monatsverläufe können durch wiederholte Spielzeitstände überschrieben worden sein. Die Website leitet ihre Verläufe deshalb aus sitzungsgetrennten Originalmessungen ab. Vollständige DB-Zeilen, Chroniken, weitere Rohfelder und Fehlerlisten bleiben in den Release-Paketen erhalten.

## Oberfläche

Überblick, alle 50 Städte mit Suche/Sortierung/Ortsakte, alle Linien mit Träger- und Belegungsfilter/Detailverlauf, Industriebetriebe mit Produktionsfilter, Stationen und ein Herkunftsregister. Die 11 Aufzeichnungsstände lassen sich weltweit umschalten. Frühere Weltatlas- und Erzähltexte sind weiter als datiertes Archiv zugänglich.
