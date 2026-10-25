# Aufgaben

Format: `- [Welt] Aufgabe · Dateien · Wer · seit/erledigt am`. Wer etwas anfängt, schiebt es nach „In Arbeit“ und trägt sich ein. Regeln: `werkstatt/README.md`.

## In Arbeit

- *(nichts)*

## Zur Prüfung

- [Falkenmark] Korrektur „Werte pro Jahr“: Kapitel I, II, IV, Jahresbilanzen 1900/1901 und drei Registereinträge nennen jetzt den Zeitraum (ein Wirtschaftsjahr, rund 91 Tage) · `saves/falkenmark/chronik.html`, `saves/falkenmark/data/events.json` · Claude, 24.10.2026 · Bitte gegen `werkstatt/falkenmark/fakten/1900.md` und `1901.md` prüfen.
- [Falkenmark] Jahresauswahl `#jahre` (Kapitel, Register und Jahresbilanz nach Jahr filtern) · `saves/falkenmark/chronik.html`, `assets/falkenmark.css` · Claude, 24.10.2026

## Offen

- [Falkenmark] Kapitel V ab Januar 1902, sobald der Spieler weitergespielt hat. Ausgangslage in `werkstatt/falkenmark/STAND.md`.
- [Falkenmark] Neue Messdaten hochladen (`WEBSITE_AKTUALISIEREN.bat --save falkenmark`); im Repo liegen sie nur bis zum Export vom 24.10.2026, 08:15 · Claude, nur mit Freigabe des Spielers
- [Falkenmark] Subventionen: Wofür wurden sie gezahlt? Braucht Angaben des Spielers oder eine neue Messgröße.
- [Falkenmark] Linienbilanzen für ein ganzes Kalenderjahr ableiten, aus vier aufeinanderfolgenden Wirtschaftsjahren. Nur als „Abgeleitet“, mit Hinweis auf Fahrzeugwechsel.
- [Falkenmark] Eigene Monitor-Ansicht; die Archipel-Seite ist bewusst nicht eingebunden.
- [Archipel] Prüfen, ob Journal und Auswertungen Werte „pro Jahr“ als Kalenderjahr ausgeben. Das Archipel läuft ebenfalls mit rund 16.000 Spielzeit-Einheiten je Tag.
- [Spielmonitor] Kalendertempo (Millisekunden je Tag) mit messen; `balance_start_game_date` und `balance_end_game_date` kommen derzeit als `null`.

## Erledigt

- [Falkenmark] Karte der Verkehrswege 1902 und Reliefmodell unter V (`#karte`), Quelle Q7 · Claude, 25.10.2026 · `67ab3ee`
- [Werkstatt] Arbeitsbereich angelegt: README, Aufgaben, Log, Eingang, Falkenmark-Stand, Faktenblätter, `AGENTS.md`/`CLAUDE.md` · Claude, 24.10.2026
- [Falkenmark] Das Jahr 1901, Kapitel III und IV · Claude, 24.10.2026 · `1e6ae35`
- [Falkenmark] Lindendorf-Bild für Kapitel III · `fed1c65`
- [Falkenmark] Kapitel neu gestaltet (Textarten, Übersichten, Navigation) · Claude, 24.10.2026 · `76d80ea`
- [Falkenmark] Upload aus dem Spielmonitor für mehrere Welten, erste Messdaten · Claude, 24.10.2026 · `ee56786`
- [Falkenmark] Das Jahr 1900, Kapitel I und II · Claude, 24.10.2026 · `f018e3b`
