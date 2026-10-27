# Erlenmark · Stand der Chronik

Zuletzt nachgezogen: 27.10.2026, Claude.

Neue Welt, angelegt am 27.10.2026. Regeln und Aufbau: `docs/ERLENMARK.md`.

## Erzählt

- Prolog „Die Erlenmark um 1900“ (Belegt, Abgeleitet, Szene), Steckbrief, Ausgangswerte unter VII.
- Noch kein Kapitel. Kapitel I beginnt mit der ersten Tätigkeit des Unternehmens.
- Register `saves/erlenmark/data/events.json`: 3 Einträge (`einstellungen-erlenmark`, `start-erlenmark`, `messung-erlenmark-1900-01-01`).
- **Nächste freie Quelle: Q5.** Vergeben: Q1 Einstellungsseite (Screenshot), Q2 Angaben des Spielers vom 27.10.2026, Q3 Spielprotokoll vom 27.10.2026, Q4 Spielmonitor (erste Messung 1.1.1900).

## Daten

- Spielmonitor: Welt „Erlenmark – 1900“, Weltkennung `tf3-2026-10-27-1793075833-1414195950-2`. Erste Sitzung `20261027_053713_859866` ab 05:37 Uhr mit der Startmessung (Positionen, grobes Höhenraster 427 m). Feiner Geländescan (64 m) seit dem ersten Laden in Arbeit, Teile in `Spielmonitor/history/gelaende/<Weltkennung>.teile.jsonl`; er läuft nur bei laufendem Spiel weiter.
- Gesichert in `Spielmonitor/exports/`: `erlenmark-start-1900-01-01-geo.json` (Startmessung), `tf3-spielprotokoll-2026-10-27-erlenmark.txt` (Spielprotokoll von 05:23 bis 05:38 Uhr; TF3 überschreibt das Original beim nächsten Start).
- Im Repo (`saves/erlenmark/data/monitor/`): Stand Spiel 2.1.1900, 4 Messungen, lokal mit `publish-monitor.py --save erlenmark --no-push` erzeugt; hochgeladen wird nur mit Freigabe.
- Kalendertempo und Länge eines Wirtschaftsjahres: offen, bis die erste Linie eine Bilanz hat.
- Faktenblätter: noch keine. `scripts/falkenmark-fakten.py` ist auf die Falkenmark zugeschnitten; für Kapitel I wird ein Skript für die Erlenmark gebraucht (Tafel, „Offen“).

## Spielstand

- `Erlenmark.sav` um 05:37:53 und `Erlental.sav` um 05:38:10 Uhr, beide vom selben Spielstart (Zufallswert SpWJDQtUdp). Das Autosave um 05:48 Uhr heißt `autosave_Erlental_1900-01-03.sav`: TF3 benennt Autosaves nach der zuletzt gespeicherten Datei. Welche Datei der Spieler weiterführt, ist mit ihm zu klären. Für den Monitor ist es gleich, beide haben dieselbe Weltkennung; wer beide abwechselnd lädt, erzeugt Rücksprünge (verworfene Abschnitte).

## Namen

- Bestätigt vom Spieler: „Erlenmark“ als Name der Welt.
- Ortsnamen aus dem Spiel (größte Städte zum Start: Ahaus 409, Stendal 258, Drolshagen 256, Rinteln 255). Unternehmen, Sitz, Flüsse, Seen und Höhenzüge haben noch keine Namen.

## Mods

46 aktiv (Protokoll vom 27.10.2026), darunter Spielmonitor (Rev. 20), Electronics Pack, Sugar Cane Industry, Toy Factory, Real Financial Statements. Im Spielordner installiert, in dieser Welt ausgeschaltet: Lebensmittel-Industrie, Werkerkundung, der Gebäude-Mod des Spielers (Schulen) und der Simplex 1902. Organic Towns ist seit dem 27.10.2026 deinstalliert. In der Startmessung stehen nur Betriebe des Grundspiels.

## Literarische Szenen

Formen bisher: Feldbuch eines Landmessers (Prolog, Einträge vom 27. bis 31.12.1899). Bitte abwechseln; Vorrat aus der Falkenmark-Liste: Speisekarte, Rezept, Lied, Predigt, Zeugnis, Fahrplan mit Randnotizen, Inventarliste, Wetterbuch, Brief, Aushang, Reportage und weitere. Figuren und Formen aus anderen Welten werden nicht übernommen.

Figuren (erfunden, nur in Szenen):

- Der Landmesser, Ich-Erzähler des Feldbuchs (Prolog), setzt Messpunkte an Erlen und zeichnet eine Karte, die „im Frühjahr“ fertig sein soll.
- Der Fuhrmann zur Furt, fährt die Strecke jede Woche, bei Hochwasser über die Höhe (Prolog).
- Bauer und Bäuerin am Waldrand mit den nassen Wiesen; sie fragt, ob ihr Hof auf der Karte steht (Prolog).
- Zwei Männer in der Wirtschaft, die den Holzpreis bis in die Stadt ausrechnen (Prolog).

Orte der Szenen sind namenlos (Bach, Furt, Waldrand, Wirtschaft im Ort), bis Namen aus dem Spiel oder vom Spieler kommen.

## Bilder

- Zierbild `assets/affiche-erlenmark.svg` (gezeichnet, keine Karte).
- Noch keine Bilder in `saves/erlenmark/images/`.
