# Log

Übergaben und Reviews, neueste oben. Kopf: `## JJJJ-MM-TT · Wer · Thema`. Nur ergänzen; Fehler in älteren Einträgen mit einem neuen Eintrag richtigstellen.

## 2026-10-26 · Claude · Falkenmark archiviert

- Wunsch des Spielers: Die Falkenmark wird beendet, weil sie nach Einschätzung des Spielers anders lief als geplant; alles Vorhandene wird archiviert. Die Chronik bleibt als abgeschlossene Chronik online.
- Website: Kapitel VIII bis X (vom 25.10. abends) gehen mit hoch, dazu ein Archiv-Vermerk am Anfang der Chronik (`#archiv`), Kopfzeile „Archiviert · erzählt 1900 bis 1904“, Portal-Status „Archiviert · gespielt 1900–1905“ (`data/worlds.json`), `meta.json` mit Endstand. Letzter Monitor-Upload bis Spiel 24.10.1905; danach steht die Welt in `data/monitor-sources.json` als `closed`, und `publish-monitor.py` überspringt sie ohne ausdrückliches `--save falkenmark`.
- Lokal: `E:\KI-Projekte\_archiv\falkenmark-2026-10-26\` mit `spielstand/` (Kopie von `Falkenmark.sav`, Stand 25.10.2026 18:43; die Spielstände im Spielordner bleiben), `spielmonitor/` (22 Sitzungen und Geländescan als tar.xz, 8,9 MB, die Originale bleiben im Spielmonitor), `karte/` (das Kartenprojekt, vorher `E:\KI-Projekte\Falkenmark-Karte`), `chronik-website.zip` und `README.md`.
- Werkstatt: offene Falkenmark-Aufgaben entfallen; die Prüfaufträge für veröffentlichte Kapitel bleiben, Korrekturen sind weiter möglich.

## 2026-10-25 · Claude · Falkenmark Kapitel VIII bis X (27.6.1903 bis 31.12.1904)

- Drei neue Kapitel: VIII „Das dritte Öl“ (Ölplattform bei Falkenried angeschlossen, Dünger von der Raffinerie zum Kornhausen Bauernhof, fünf Personenzüge, letzte Subvention 27.7.1903), IX „Lindendorf vorn“ (zwei Plus-Quartale aus dem laufenden Geschäft, Lindendorf seit 24.6.1904 größter Ort, Falkenried verlangt Werkzeuge), X „Getreide für Hintereichdorf“ (Maschinenkette für Lindendorf, Güterzug zur Lebensmittelfabrik ab 18.10., Fabrik arbeitet ab 30.11.1904, Falkenried wartet auf die ersten Lebensmittel). Sechs Szenen in neuen Formen: Fundbuch, Postkarte, Leserbriefe „Eingesandt“, Tagebuch des Buchhalters, Telegramme, Unterredung mit dem Bürgermeister; wiederkehrende Figuren in `falkenmark/STAND.md`.
- Neuladen: Der Spieler hat den Spielstand für Mod-Tests mehrfach neu geladen. Auswertung und Faktenblätter nehmen die verworfenen Abschnitte heraus (`scripts/falkenmark-fakten.py`, Funktion `canonical`); 1900 bis 1902 bleiben inhaltlich gleich.
- Technischer Hinweis in Kapitel X mit neuer Quelle Q9: Gebäude-Mod des Spielers seit Ende Juni 1903 (Spielzeit), Stadtentwicklung in Lindendorf vom 15.7. bis Ende September 1904 abgeschaltet (Organic Towns) und wieder eingeschaltet. Schulen sind unbelegt und bleiben vorerst draußen.
- Register +18 (75), Jahresbilanzen 1903 und 1904, Ortsverzeichnis (+Hohenstedt, Hochloh), Unternehmen, offene Fragen. CSS: Kapitelleiste umbricht ab 901 px Breite (zehn Kapitel waren hinter einer unsichtbaren Scrollleiste), `fm-scene--telegramm`.
- Geprüft: `validate-data.mjs`, grep der neuen Kapitel ohne Treffer bei nicht/kein/nie/niemand/nichts/sondern/ohne, Browser 1280 und 375 px ohne Überlauf, Jahresauswahl 1903/1904, keine Konsolenfehler. Noch nicht committet.

## 2026-10-25 · Claude · Falkenmark Kapitel V bis VII (1902 bis Juni 1903)

- Drei neue Kapitel: V „Die Bahn nach Lindendorf“ (Januar bis Juni 1902: Fisch für Falkenried, erster Personenzug Falkenried–Lindendorf am 30.3., Raddampfer zur Fischzucht), VI „Bis Birkreuth“ (Juli bis Dezember 1902: Lindendorf wird zweitgrößter Ort, neue Wünsche Lebensmittel und Kleidung, Zug bis Birkreuth am 15.12.), VII „Vier Fabriken“ (Januar bis 26.6.1903: Textilfabrik, Chemiefabrik, Lebensmittelfabrik, Weberei, alle still). Sechs Szenen in neuen Formen: Schulaufsatz, Kleinanzeigen, Gemeinderatsprotokoll, Erzählung, Reportage, Ansprache; wiederkehrende Figuren und Formen stehen jetzt in `falkenmark/STAND.md`.
- Wunsch des Spielers für alle Szenen: variieren, natürlich, ohne Verneinungsfiguren und KI-Phrasen. Kapitel V bis VII ohne Treffer bei grep auf nicht/kein/nie/niemand/nichts/sondern/ohne.
- Register +24 (33 → 57, darunter der Nachtrag „Falkenried größter Ort seit 7.7.1901“), Jahresbilanz 1902, Ortsverzeichnis (drei neue Orte), Unternehmen, offene Fragen, Q8 (Lebensmittelfabrik auf Wunsch des Spielers über einen Mod gesetzt, als Hinweis „Zur Lebensmittelfabrik“ in VII). Korrektur im Ortsverzeichnis: Falkenried war als Ziel der Gemüselinie geführt, das Gemüse geht aber nach Lindendorf.
- Technik: `fm-scene--eintraege` (Szenen aus Einträgen, ohne Initiale), `fm-randnotiz` (Randbemerkung), `fm-leg--ware` (möglicher Warenweg, Hinweis „Luftlinie“); Jahresauswahl nennt die Jahresbilanz nur, wenn es eine gibt. Faktenblätter 1902 und 1903 neu erzeugt.
- Daten: Spielmonitor lokal bis 26.6.1903, lückenlos; das Spiel wurde danach beendet. Kapitel VIII beginnt am 27.6.1903. Im Repo liegen Messdaten bis 19.4.1903, Upload nur mit Freigabe.
- Geprüft: `validate-data.mjs`, Browser 1024 px und 375 px ohne Überlauf, Register lädt (57), Jahresauswahl 1902/1903, keine Konsolenfehler.
- Auf Wunsch des Spielers committet (`df5c2e8`) und mit den Messdaten hochgeladen (`60fd9a8`, Spiel bis 27.6.1903: drei Messungen vom 27.6. aus einem kurzen Spielstart um 08:51 Uhr kamen mit; erzählt ist bis 26.6.).

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
