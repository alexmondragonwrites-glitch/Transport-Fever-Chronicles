# Log

Übergaben und Reviews, neueste oben. Kopf: `## JJJJ-MM-TT · Wer · Thema`. Nur ergänzen; Fehler in älteren Einträgen mit einem neuen Eintrag richtigstellen.

## 2026-10-25 · Claude · Karte der Falkenmark auf der Website

- Neu unter V „Orte und Landschaft“ (`#karte`, Link „Karte“ in der Kopfleiste): Karte der Verkehrswege im Stil farbiger Atlaskarten um 1900, Stand 29.12.1902, und ein Reliefmodell. Bilder `saves/falkenmark/images/falkenmark-1902-karte.jpg` (A2, 300 dpi, 4,2 MB), `-karte-web.jpg`, `-reliefmodell.jpg`. Neue Quelle Q7 (Messung 29.12.1902 und Feinscan des Geländes); nächste freie Nummer Q8.
- Textarten in der Bildunterschrift: belegt sind Lage, Einwohner, Betriebe, Halte, Linien, Fahrzeuge und Höhen; abgeleitet ist der Verlauf der Linien zwischen den Halten (Weg über das Gelände). Keine Namen für Flüsse, Seen, Höhenzüge. Hinweis, dass die Chronik bis Ende 1901 erzählt ist.
- Erzeugt außerhalb des Repos mit `E:\KI-Projekte\Falkenmark-Karte\KARTE_RECHNEN.bat` (Python, Blender); der letzte Schritt `karte_web.py` schreibt die drei Bilder hierher. Nach einem neuen Lauf nur committen und hochladen.
- Geprüft: `validate-data.mjs`, Browser 1280 px und 375 px ohne Überlauf, Bilder laden, keine Konsolenfehler. Auf Wunsch des Spielers hochgeladen.

## 2026-10-24 · Claude · Werkstatt angelegt, Werte „pro Jahr“ korrigiert

- Werkstatt eingerichtet: `README.md` (Ablauf, Regeln, Rollen), `AUFGABEN.md`, dieses Log, `eingang/`, `falkenmark/STAND.md`, Faktenblätter 1900 bis Januar 1902 (`scripts/falkenmark-fakten.py`). Im Repo-Wurzelverzeichnis `AGENTS.md` (Codex) und `CLAUDE.md` (Claude) mit Verweis hierher.
- Fehler gefunden: Die Werte „pro Jahr“ aus dem Spiel (Produktion, Versand, Linienbilanz) umfassen ein Wirtschaftsjahr des Spiels, `getDefaultYearDuration` = 1.461.000 Spielzeit-Einheiten. Die Falkenmark läuft mit rund 16.000 Einheiten je Kalendertag, ein Wirtschaftsjahr sind also rund 91 Tage. Belegt durch das Bilanzfenster an jeder Linie (`balance_start_game_time`) und eine Lehmgrube ohne Abholung, deren Wert „pro Jahr“ etwa 91 Tage steigt und dann stehen bleibt. Die Finanztabelle rechnet nach Kalenderquartalen und ist nicht betroffen.
- Korrigiert in `chronik.html`: Quellenabsatz Kapitel I, je ein Satz in Kapitel II und IV, Karten der Jahresbilanzen 1900 und 1901, neuer Eintrag unter „Korrekturen“. In `events.json` drei Einträge mit `correction` (Wortlaut stehen gelassen). Zahlen unverändert.
- Jahresauswahl `#jahre` gebaut (Kapitel, Register, Jahresbilanz nach Jahr). Beides liegt unter „Zur Prüfung“.
- Auf Wunsch des Spielers am 24.10.2026 zusammen hochgeladen (Werkstatt, Korrektur, Jahresauswahl).
- Offen fürs Archipel: dieselbe Frage. Es läuft ebenfalls mit rund 16.000 Einheiten je Tag.
