# Gesamtexport – Archipel des Alizés – 1900

`MEINE_SPIELWELT.json` enthält ausschließlich die protokollierte Welt **Archipel des Alizés – 1900**, Kennung `tf3-2026-10-9-1791530983-207911368-2`. Der Dateiname stammt aus dem bestehenden Weltexporter.

## Struktur der JSON-Datei

- `world`: Weltname und eindeutige Weltkennung.
- `database`: Gespeicherte Monitor-Tabellen mit `identity_basis`, `row_count` und `rows`. Enthält unter anderem Stadtverläufe, Linienverläufe, den gespeicherten Snapshot, Markierungen und erfasste Linienwechsel, soweit vorhanden. JSON-Datenspalten sind als Objekte eingebettet.
- `sessions`: Alle zugeordneten Aufzeichnungssitzungen. Jede enthält Sitzungskennung, Quelldatei, vollständige Originalmessungen in `measurements`, SHA256 und erfasste Quellgröße. Zugeordnete Chroniken stehen in `chronicle_markdown`.
- `manifest`: Exportzeit, Umfang, Zählungen, Quellenabgrenzung und Hinweise zur Konsistenz.

`INHALT.json` ist das kleine, lesbar eingerückte Inhaltsverzeichnis mit Messungszahlen, Tabellenzahlen, Dateigröße und SHA256 der großen JSON-Datei. `MEINE_SPIELWELT.zip` enthält dieselbe JSON-Datei und das Inhaltsverzeichnis komprimiert.

## Daten richtig einordnen

Alle tatsächlich gespeicherten Messfelder bleiben erhalten, einschließlich Fehlerlisten, Cache-Zeitpunkten und fehlender Werte. Die große JSON-Datei ist platzsparend serialisiert; ihre Objekte und Arrays sind vollständig strukturiert.

Bekannter Aufnahmefehler von Revision 13: Die Kalendergrenzen `balance_start_game_date` / `balance_end_game_date` konnten teilweise nicht serialisiert werden. Fehlende Kalenderwerte werden nicht ergänzt. Qualitäts- und Fahrzeitwerte sind teilweise ungeprüfte API-Rohwerte.

Am 11.10.2026 wurde an der Grenze zur Sitzung `20261011_135432_045539` ein Rücksprung der Spielzeit beobachtet. Sitzungen bleiben deshalb getrennt. Wiederverwendete Sequenzen/Spielzeiten nicht global deduplizieren oder zu einer ununterbrochenen Entwicklung zusammenführen. Datenbankverläufe sind zusätzlich gespeicherte Darstellungen und keine zusätzlichen unabhängigen Messungen.

Der Export ist eine Bestandsaufnahme: SQLite wurde konsistent nur lesend in den Arbeitsspeicher gesichert; Sitzungsdateien wurden bis zu festgehaltenen Dateigrößen eingelesen. Währenddessen später eingehende Messungen gehören nicht zu diesem Export. Über alle Dateien hinweg besteht kein atomarer Aufnahmezeitpunkt.

Dies ist ein Export der Monitoraufzeichnungen, keine Spielstanddatei. Andere Welten, Messungen ohne passende Weltkennung, fremde Berichte, frühere Exporte, Quellcode und externe Steam-Dateien sind ausgeschlossen.


## Download-Status

Die große Exportdatei ist noch nicht hochgeladen. JSON und ZIP liegen bisher lokal vor. Der Upload als Release-Anhang steht aus.
