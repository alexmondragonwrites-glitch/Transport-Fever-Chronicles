# Aufgaben

Format: `- [Welt] Aufgabe · Dateien · Wer · seit/erledigt am`. Wer etwas anfängt, schiebt es nach „In Arbeit“ und trägt sich ein. Regeln: `werkstatt/README.md`.

**Falkenmark archiviert am 26.10.2026.** Die Welt wird beendet, die Chronik ist abgeschlossen. Neue Kapitel und Uploads entfallen; Prüfungen des veröffentlichten Stands und Korrekturen bleiben möglich. Archiv: `E:\KI-Projekte\_archiv\falkenmark-2026-10-26\`.

## In Arbeit

- *(nichts)*

## Zur Prüfung

- [Falkenmark] Kapitel VIII „Das dritte Öl“, IX „Lindendorf vorn“, X „Getreide für Hintereichdorf“ (27.6.1903 bis 31.12.1904), 18 Registereinträge, Jahresbilanzen 1903 und 1904, Ortsverzeichnis (neu: Hohenstedt, Hochloh), Unternehmen, offene Fragen, Q9 (Gebäude-Mod, Stadtentwicklung Lindendorf), Hinweis „Zur Stadtentwicklung 1903 und 1904“ · `saves/falkenmark/chronik.html`, `saves/falkenmark/data/events.json`, `assets/falkenmark.css` (Kapitelleiste umbricht auf breiten Bildschirmen, `fm-scene--telegramm`) · Claude, 25.10.2026 abends, mit dem Archiv-Vermerk am 26.10.2026 hochgeladen · Bitte gegen `werkstatt/falkenmark/fakten/1903.md` und `1904.md` prüfen.
- [Falkenmark] `scripts/falkenmark-fakten.py` nimmt Messungen aus verworfenen Abschnitten (Rücksprung der Spielzeit nach Neuladen) heraus; Faktenblätter 1900 bis 1904 neu erzeugt (1900 bis 1902 inhaltlich gleich) · Claude, 25.10.2026 abends
- [Falkenmark] Kapitel V „Die Bahn nach Lindendorf“, VI „Bis Birkreuth“ und VII „Vier Fabriken“ (Januar 1902 bis 26.6.1903), 24 Registereinträge, Jahresbilanz 1902, Orte (neu: Hinteralmhafen, Langstein, Steinbach im Tal), Unternehmen, offene Fragen, Q8, Korrektur „Gemüselinie“ im Ortsverzeichnis · `saves/falkenmark/chronik.html`, `saves/falkenmark/data/events.json`, `assets/falkenmark.css` · Claude, 25.10.2026 · `df5c2e8`, auf Wunsch des Spielers hochgeladen · Bitte gegen `werkstatt/falkenmark/fakten/1902.md` und `1903.md` prüfen; einzelne Daten stammen aus Grundmessungen und liegen bis zu drei Tage vor dem Faktenblatt (siehe `STAND.md`, Fallstricke).
- [Falkenmark] Korrektur „Werte pro Jahr“: Kapitel I, II, IV, Jahresbilanzen 1900/1901 und drei Registereinträge nennen jetzt den Zeitraum (ein Wirtschaftsjahr, rund 91 Tage) · `saves/falkenmark/chronik.html`, `saves/falkenmark/data/events.json` · Claude, 24.10.2026 · Bitte gegen `werkstatt/falkenmark/fakten/1900.md` und `1901.md` prüfen.
- [Falkenmark] Jahresauswahl `#jahre` (Kapitel, Register und Jahresbilanz nach Jahr filtern) · `saves/falkenmark/chronik.html`, `assets/falkenmark.css` · Claude, 24.10.2026

## Offen

- [Archipel] Prüfen, ob Journal und Auswertungen Werte „pro Jahr“ als Kalenderjahr ausgeben. Das Archipel läuft ebenfalls mit rund 16.000 Spielzeit-Einheiten je Tag.
- [Spielmonitor] Kalendertempo (Millisekunden je Tag) mit messen; `balance_start_game_date` und `balance_end_game_date` kommen derzeit als `null`.

## Erledigt

- [Falkenmark] Welt archiviert: Chronik mit Kapitel VIII bis X und Archiv-Vermerk, Portal-Status „Archiviert“, letzte Messdaten bis Spiel 24.10.1905, `closed` in `data/monitor-sources.json`; lokales Archiv mit Spielstand, gepackten Spielmonitor-Sitzungen und Kartenprojekt · Claude, 26.10.2026. Damit entfallen die offenen Falkenmark-Aufgaben: Kapitel XI, weitere Messdaten, Schulen und Gebäude, Zweck der Subventionen, Kalenderjahres-Bilanzen, eigene Monitor-Ansicht.
- [Falkenmark] Messdaten bis Spiel 27.6.1903 hochgeladen (+114 Messungen) · Claude, 25.10.2026 · `60fd9a8`
- [Falkenmark] Karte der Verkehrswege 1902 und Reliefmodell unter V (`#karte`), Quelle Q7 · Claude, 25.10.2026 · `67ab3ee`
- [Werkstatt] Arbeitsbereich angelegt: README, Aufgaben, Log, Eingang, Falkenmark-Stand, Faktenblätter, `AGENTS.md`/`CLAUDE.md` · Claude, 24.10.2026
- [Falkenmark] Das Jahr 1901, Kapitel III und IV · Claude, 24.10.2026 · `1e6ae35`
- [Falkenmark] Lindendorf-Bild für Kapitel III · `fed1c65`
- [Falkenmark] Kapitel neu gestaltet (Textarten, Übersichten, Navigation) · Claude, 24.10.2026 · `76d80ea`
- [Falkenmark] Upload aus dem Spielmonitor für mehrere Welten, erste Messdaten · Claude, 24.10.2026 · `ee56786`
- [Falkenmark] Das Jahr 1900, Kapitel I und II · Claude, 24.10.2026 · `f018e3b`
