# Monitoransicht – Archipel

Der Langzeitmonitor unter `saves/archipel-des-alizes/index.html?view=monitor` zeigt den zuletzt hochgeladenen Spielemonitor-Stand. Ohne Parameter leitet die Seite auf den aktuellen Bericht (`latestReport`) weiter; das redaktionelle Archiv mit Weltatlas und März-1910-Tabellen bleibt über `?view=archive` erreichbar. Diese Quellen werden nicht still vermischt.

**Zwei Monitorordner:** `data/monitor/` (Manifest `monitor`) wird laufend aktualisiert. `data/monitor-20261011/` (Manifest `monitor_archive`) ist der eingefrorene Stand des Release-Exports vom 11.10.2026 im ursprünglichen Format; auf ihm beruhen die Fakten des Dossiers „Zehn Jahre Archipel“ (`scripts/build-decade.mjs`). Diesen Ordner nicht neu erzeugen oder überschreiben; `validate-monitor.mjs` prüft seine Eckwerte.

## Aktuellen Stand hochladen

Im Spielmonitor-Ordner `WEBSITE_AKTUALISIEREN.bat` doppelklicken, oder:

```text
python scripts/publish-monitor.py            # zeigt Änderungen, fragt vor dem Upload
python scripts/publish-monitor.py --no-push  # nur lokal erzeugen, nichts committen
python scripts/publish-monitor.py --yes      # ohne Rückfrage (z. B. für geplante Aufgaben)
```

Das Script liest `../Spielmonitor/sessions/*/daten.jsonl` (anderer Ort: `--monitor PFAD`), nimmt nur Messungen der in `data/monitor-sources.json` eingetragenen `world_id` und erzeugt daraus `saves/archipel-des-alizes/data/monitor/`. Die Ausgabe enthält keine Uhrzeit des Exports, sondern nur Messwerte: Abgeschlossene Sitzungen bleiben byte-identisch und werden nie erneut hochgeladen. Ein Upload enthält deshalb normalerweise nur den Abschnitt der laufenden Sitzung und `index.json`. Ohne neue Messungen entsteht kein Commit.

Ablauf: GitHub-Stand nachziehen (nur Fast-Forward), geänderte Dateien schreiben, `validate-monitor.mjs` und `validate-data.mjs` ausführen, Änderungen anzeigen, nach Bestätigung committen und pushen. Schlägt eine Prüfung fehl, wird nichts committet. Eine noch nicht vollständig geschriebene letzte Zeile der laufenden Sitzung bleibt für den nächsten Lauf stehen. Bereits gelesene, unveränderte Sitzungsdateien merkt sich `.publish-cache/` (nicht im Repository); Änderungen an `monitor_build.py` verwerfen diesen Cache automatisch.

Neue Rohdaten bleiben lokal im Spielmonitor. Das Rohdaten-Archiv auf GitHub (Release) ist der vollständige Export vom 11.10.2026 und wird nicht automatisch erweitert.

## Reproduzierbarer Import aus dem Release-Archiv

```text
python scripts/import-monitor.py /absoluter/pfad/zum/Export/Pakete
node --check assets/monitor.js
node scripts/validate-monitor.mjs
node scripts/validate-data.mjs
```

Der Import prüft SHA256 und die Weltkennung jedes Sitzungspakets und schreibt denselben Ordner `monitor/` mit dem Stand des Archivs. Beide Wege nutzen `scripts/monitor_build.py`; für dieselben Messungen entstehen identische Abschnittsdateien. Das kleine `index.json` nennt Quellen, Summen und Abschnittsdateien. Das Manifest referenziert es über `monitor`. Je Abschnitt gibt es `<id>.json` (Stand, Städte, Flotte, Qualität) und `<id>-lines.json` (Linienverläufe, der größte Teil). Die Website lädt zunächst nur den neuesten Abschnitt ohne Linienverläufe; diese kommen erst beim Reiter „Verkehr“, andere Abschnitte erst auf Auswahl.

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
