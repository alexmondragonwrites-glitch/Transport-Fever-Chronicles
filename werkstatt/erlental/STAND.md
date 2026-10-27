# Erlental · Stand der Chronik

Zuletzt nachgezogen: 27.10.2026, Claude. Regeln und Aufbau: `docs/ERLENTAL.md`.

## Erzählt

| Kapitel | Titel | Zeitraum | `data-year` |
|---|---|---|---|
| I | Die Gründung | 1900, Messungen vom 1. Januar bis 2. Februar 1900 (Stichtag: Messung 2.2.1900, aufgenommen 27.10.2026 06:06 Uhr) | 1900 |
| II | Fisch und Ziegel | 1900, Messungen vom 3. Februar bis 31. Dezember 1900 (Stichtag: letzte Messung 31.12.1900, aufgenommen 27.10.2026 13:34 Uhr; Finanztabelle und Versorgung Stand 28.12.1900) | 1900 |

- Prolog „Erlental um 1900“ (Belegt, Abgeleitet, Szene „Aus dem Feldbuch eines Landmessers“), Steckbrief, Ausgangswerte unter VII.
- Kapitel I: Gründungsbild (`images/arenswiel-gruendung-1900-web.jpg`, Original `…-1900.png`), Übersicht, Belegt, Abgeleitet und die Gründungsgeschichte „Ein Anfang in Arenswiel“ im Wortlaut als literarische Szene (Quelle `gruendung-1900.md`, Abgleich Absatz für Absatz).
- Kapitel II: Übersicht (sechs Kennzahlen, Zeitachse, Linienschemata „Ziegel für Arenswiel“ und „Fisch vom Seegut“), Belegt, Abgeleitet, drei Szenen (Fahrplan mit Randnotizen, Speisekarten, Brief des Landmessers). Dazu Jahresbilanz 1900 unter VII, Orte (neu: Silberweide statt Mettmann, Wengenrode, Klötze, Eckartsberga, Itzehoe), Unternehmen, offene Fragen (Zuschüsse, Ziegelweg, Wachstum Arenswiel). Geschrieben nach `fakten/1900.md`; jedes Datum ist die früheste Messung, auch Grundmessungen.
- Register `saves/erlental/data/events.json`: 26 Einträge, letzter `stand-1900-12-31`.
- **Nächste freie Quelle: Q6.** Vergeben: Q1 Einstellungsseite (Screenshot), Q2 Angaben des Spielers vom 27.10.2026 (Name Erlental, weitergeführte Datei, Mods gewollt), Q3 Spielprotokoll vom 27.10.2026, Q4 Spielmonitor (Messungen ab 1.1.1900), Q5 Gründungspaket vom 27.10.2026 (Name und Sitz der EWV, Gründungsbild, Gründungsgeschichte).

## Übergabe von Codex (27.10.2026)

Codex hat im Auftrag des Spielers das Gründungspaket über die Werkstatt übergeben (Commit `efd7c94`): Gründungsbild, Wortlaut der Gründungsgeschichte und einen Vorschlag zur Einbindung. Übernommen wie vorgeschlagen: Bild als Auftakt von Kapitel I mit Kennzeichnung als KI-Bild, Geschichte vollständig als literarische Szene, belegte Rahmendaten getrennt daneben, Gründung jahresgenau 1900, Erfundenes außerhalb des Registers. Ergänzt um die Messungen bis 2.2.1900, die Codex noch fehlten. Bestätigung im Log.

Bestätigter Rahmen aus dem Paket: Gesellschaft **Erlentaler Wege- und Verkehrsgesellschaft (EWV)** mit Sitz **Haus Weitblick**, einem hellen Haus mit langer Zufahrt oberhalb von Arenswiel; Arenswiel (vorher Selters) hatte im Gründungs-Screenshot 167 Einwohner, so auch die erste Messung.

## Daten

- Spielmonitor: Welt „Erlental – 1900“, Weltkennung `tf3-2026-10-27-1793075833-1414195950-2`. Sitzungen ab `20261027_053713_859866` (Startmessung mit Positionen und grobem Höhenraster). Die Welt hieß im Monitor bis 06:05 Uhr „Erlenmark – 1900“; umbenannt in der Datenbank, der laufende Monitor hat um 06:07 Uhr von selbst eine neue Sitzung unter dem neuen Namen begonnen.
- Feiner Geländescan (64 m) läuft nur bei laufendem Spiel, Teile in `Spielmonitor/history/gelaende/<Weltkennung>.teile.jsonl`.
- Gesichert in `Spielmonitor/exports/`: `erlental-start-1900-01-01-geo.json` (Startmessung), `tf3-spielprotokoll-2026-10-27-erlental.txt` (Spielprotokoll von 05:23 bis 05:38 Uhr).
- Im Repo (`saves/erlental/data/monitor/`): Messdaten aus `publish-monitor.py --save erlental`.
- Wirtschaftsjahr: rund 92 Kalendertage (gemessen 91,6; Bilanzzeiträume 3.9. bis 3.12. und 27.9. bis 28.12.1900). Werte „pro Jahr“ mit Zeitraum nennen.
- Faktenblätter: `py -3 scripts/erlental-fakten.py JAHR` schreibt `werkstatt/erlental/fakten/JAHR.md` (Test: `scripts/test-erlental-fakten.py`). Vorhanden: 1900. Kapitel I ist direkt aus den Sitzungsdaten geschrieben, Kapitel II nach dem Faktenblatt 1900.

## Fallstricke

- Liniennamen entstehen nach einem Muster (Kürzel, Waren, Orte, Nummer) und ändern sich mit der Linie und mit Ortsnamen. Derselbe Name kann nacheinander zu verschiedenen Linien gehören (zum Beispiel „Bus Passagiere-Sil-LO-1“: zuerst die Gemüselinie, ab Oktober eine Postkutschenlinie). Linien über ihre Kennung verfolgen, wie das Faktenblatt.
- „Passagiere“ im Namen einer Fuhrwerkslinie gehört zum Namensmuster; die Fuhrwerke fahren Waren.
- Die beiden Fischdampfer tragen „Sil“ im Namen, fahren aber zum Seegut Tiefenborn: Das Spiel ordnet den Halt am Seegut Silberweide zu. Zum Silberweide Hafen fährt erst die Ziegellinie vom 28.12.1900.
- Der Laderaum des Zuges wechselt mit der Fahrtrichtung (Fisch 48 oder Ziegel 40 und Fisch 8). Ziegel zum ersten Mal geladen in der Messung vom 22.7.1900.
- Benennt der Spieler einen Ort um, behalten Betriebe und Halte den alten Namen (Bad Oeynhausen Station, Mettmann Bauernhof).
- Kaufdatum 1.1.1900 bei Postkutschen ist unzuverlässig; als Datum gilt die erste Messung der Linie.
- Das Faktenblatt kennt Detailmessungen; die Grundmessungen zeigen vieles einen bis drei Tage früher. Die Chronik nennt die früheste Messung.
- Am 28.12.1900 gibt es drei Detailmessungen kurz hintereinander; die Finanztabelle 1900 stammt aus der letzten (13:33 Uhr). Nach dem 28.12. folgen nur Grundmessungen.

## Spielstand

- Weitergespielt wird `Erlental.sav` (Angabe des Spielers). `Erlenmark.sav` (05:37 Uhr) ist eine Kopie desselben Starts mit derselben Weltkennung; Autosaves heißen `autosave_Erlental_…`.

## Namen

- Bestätigt: Erlental (Welt), Erlentaler Wege- und Verkehrsgesellschaft, kurz EWV, Haus Weitblick (Sitz).
- Vom Spieler im Spiel vergeben: Arenswiel (vorher Selters, ab Messung 3.1.1900), Seegut Tiefenborn (vorher „Mettmann Fischzucht“, ab Messung 22.1.1900), Wengenrode (vorher Bad Oeynhausen, ab Messung 19.4.1900), Silberweide (vorher Mettmann, ab Messung 17.7.1900).
- Übrige Ortsnamen aus dem Spiel. Flüsse, Seen und Höhenzüge haben noch keine Namen.

## Mods

46 aktiv, laut Spieler gewollt: darunter Spielmonitor (Rev. 20), Electronics Pack, Sugar Cane Industry, Toy Factory, Real Financial Statements. Ausgeschaltet: Lebensmittel-Industrie, Werkerkundung, der Gebäude-Mod des Spielers und der Simplex 1902; Organic Towns ist deinstalliert. In der Startmessung stehen nur Betriebe des Grundspiels.

## Literarische Szenen

Formen bisher: Feldbuch eines Landmessers (Prolog, Einträge vom 27. bis 31.12.1899), Erzählung „Ein Anfang in Arenswiel“ (Kapitel I, Wortlaut des Spielers), Fahrplan mit Randnotizen „Güterzug Arenswiel Ost – Bad Oeynhausen“, Speisekarten „Gasthaus zur Post, Arenswiel“ (März und Weihnachten 1900, Darstellung `et-scene--karte`), Brief „An die Direktion im Haus Weitblick“ (alle Kapitel II). Bitte abwechseln; Vorrat: Aushang, Fahrtenbuch, Rezept, Lied, Predigt, Zeugnis, Inventarliste, Wetterbuch, Reportage. Figuren und Formen aus anderen Welten werden nicht übernommen.

Figuren (erfunden, nur in Szenen):

- Der Landmesser, Ich-Erzähler des Feldbuchs (Prolog); seine Karte soll „im Frühjahr“ fertig sein. Im Arbeitszimmer im Haus Weitblick liegt „eine Karte Erlentals“ (Kapitel I). In Kapitel II heißt er Ernst Fiedler: Er hat das erste Blatt im April gebracht und schickt am 28.12.1900 ein Nachtragsblatt mit Deckblatt für Arenswiel; den Anleger bei Silberweide will er noch ansehen. Sein Brief liegt im Haus Weitblick bei den Fahrplänen.
- Der Stationsvorsteher in Arenswiel Ost (Kapitel II, Bleistiftnotizen im Fahrplan) und der Lokführer, der ein Schild für den Wasserkran will (nur erwähnt).
- Der Fuhrmann von der Station Zentrum, der die ersten Ziegel meldet und den Tag im Kalender anstreicht (Kapitel II). Ob er der alte Fuhrmann aus Kapitel I ist, bleibt offen.
- Der Fuhrmann zur Furt (Prolog); in Kapitel I fragt „ein alter Fuhrmann“, ob die Gesellschaft ihn beschäftigen oder verdrängen wird. Ob es derselbe ist, bleibt offen.
- Bauer und Bäuerin am Waldrand mit den nassen Wiesen (Prolog).
- Zwei Männer in der Wirtschaft, die den Holzpreis ausrechnen (Prolog); der Wirt in Arenswiel hofft auf Reisende (Kapitel I). In Kapitel II führt er das Gasthaus zur Post am Busbahnhof: Fisch ab Freitag, dem 9. März, Mittagstisch für Fuhrleute, zu Weihnachten vier Fremdenzimmer im Anbau aus Eckartsberger Ziegeln.
- Bauer und Bäuerin am Waldrand: In Kapitel II zeigt die Bäuerin im Oktober auf der fertigen Karte auf ihren Hof.
- Kaufleute, Fuhrleute und Gewerbetreibende der ersten Beratungen; die Direktion im Haus Weitblick (Kapitel I).

## Bilder

| Datei | Kapitel | Art |
|---|---|---|
| `saves/erlental/images/arenswiel-gruendung-1900.png` | I (Original, verlinkt) | KI-Bild nach einem Screenshot im Spiel, kolorierte Lithografie (Q5) |
| `saves/erlental/images/arenswiel-gruendung-1900-web.jpg` | I | Web-Fassung desselben Bildes (JPEG, 1604 × 980) |
| `saves/erlental/images/arenswiel-gruendung-1900-ausschnitt.jpg` | Titelblatt, Portal | Ausschnitt aus dem Gründungsbild (Arenswiel, Haus Weitblick) |
