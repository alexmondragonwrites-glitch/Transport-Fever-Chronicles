# Log

Übergaben und Reviews, neueste oben. Kopf: `## JJJJ-MM-TT · Wer · Thema`. Nur ergänzen; Fehler in älteren Einträgen mit einem neuen Eintrag richtigstellen.

## 2026-10-24 · Claude · Werkstatt angelegt, Werte „pro Jahr“ korrigiert

- Werkstatt eingerichtet: `README.md` (Ablauf, Regeln, Rollen), `AUFGABEN.md`, dieses Log, `eingang/`, `falkenmark/STAND.md`, Faktenblätter 1900 bis Januar 1902 (`scripts/falkenmark-fakten.py`). Im Repo-Wurzelverzeichnis `AGENTS.md` (Codex) und `CLAUDE.md` (Claude) mit Verweis hierher.
- Fehler gefunden: Die Werte „pro Jahr“ aus dem Spiel (Produktion, Versand, Linienbilanz) umfassen ein Wirtschaftsjahr des Spiels, `getDefaultYearDuration` = 1.461.000 Spielzeit-Einheiten. Die Falkenmark läuft mit rund 16.000 Einheiten je Kalendertag, ein Wirtschaftsjahr sind also rund 91 Tage. Belegt durch das Bilanzfenster an jeder Linie (`balance_start_game_time`) und eine Lehmgrube ohne Abholung, deren Wert „pro Jahr“ etwa 91 Tage steigt und dann stehen bleibt. Die Finanztabelle rechnet nach Kalenderquartalen und ist nicht betroffen.
- Korrigiert in `chronik.html`: Quellenabsatz Kapitel I, je ein Satz in Kapitel II und IV, Karten der Jahresbilanzen 1900 und 1901, neuer Eintrag unter „Korrekturen“. In `events.json` drei Einträge mit `correction` (Wortlaut stehen gelassen). Zahlen unverändert.
- Jahresauswahl `#jahre` gebaut (Kapitel, Register, Jahresbilanz nach Jahr). Beides liegt unter „Zur Prüfung“.
- Auf Wunsch des Spielers am 24.10.2026 zusammen hochgeladen (Werkstatt, Korrektur, Jahresauswahl).
- Offen fürs Archipel: dieselbe Frage. Es läuft ebenfalls mit rund 16.000 Einheiten je Tag.
