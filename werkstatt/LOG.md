# Log

Übergaben und Reviews, neueste oben. Kopf: `## JJJJ-MM-TT · Wer · Thema`. Nur ergänzen; Fehler in älteren Einträgen mit einem neuen Eintrag richtigstellen.

## 2026-10-29 · Claude · Erlental: 3D-Karte nachgebacken (Korrektur)

- Gefunden hat es die Sitzung zur Monitor-Mod: Den Bauskripten fehlten Baumgruppen, die das Spiel erst beim Bauen vergibt (`random_*_airport` für Höfe, Ställe, Brauerei, Sägewerk und Fabriken, `random_*_forestry` für die Forstfelder). Auf der Karte standen deshalb Platzhalterwürfel, und die Forstbetriebe waren kahl. `tf3_bauten.py` bildet die Gruppen jetzt nach.
- Neu gebacken habe ich nur die Blöcke um die Platzhalter und die Forstbetriebe: 35 Abschnitte für IV, 10 für III, 7 für II, 1 für I. Ältere Stände übernehmen die korrigierten Kacheln von IV. Danach bleibt kein Platzhalter übrig, und der Backlauf warnt künftig je Abschnitt.
- Chronik: Eintrag unter „Korrekturen“ (29.10.2026). Auf Wunsch des Spielers hochgeladen in `64e2cd9`.

## 2026-10-29 · Claude · Erlental: 3D-Karte eingebunden

- Auftrag und Freigabe des Spielers: Schritt 5 des Kartenbriefings (`E:\KI-Projekte\Erlental-Karte\BRIEFING.md`), die 3D-Karte in die Chronik einbinden und hochladen.
- `saves/erlental/karte/` ist die gebaute Seite (Vite, React, three.js) mit je Kapitel einem Kartenstand: I → 2.9.1900, II → 1.1.1901, III → 1.1.1902, IV → 1.1.1903. Dazu Tag und Nacht, Städte, Stationen und Betriebe mit Ortskarte und die Linien je Stichtag. Verweise aus der Chronik: `karte/#kapitel-N`.
- Die Kacheln sind in Blender gerenderte Bilder; Spielmodelle und Texturen blieben lokal. Gleiche Kacheln liegen nur einmal beim neuesten Stand (`herkunft` in `kacheln.json`). Zusammen 6 703 Dateien, 136,6 MB.
- Chronik:
  - unter V „Orte und Landschaft“ die Figur `#karte` mit Vorschaubild `images/erlental-karte-1903.jpg`;
  - im Kopf jedes Kapitels die Zeile `p.et-chapter-map` (Stil in `assets/erlental.css`);
  - Quelle Q7 mit Belegt und Abgeleitet.
- Abgeleitet sind: Verlauf der Linien (kürzester Weg, gestrichelt), Lage der Bäume im Feld, Wald in allen Kapiteln vom 1.1.1903; in Kapitel I die Bauparameter unveränderter Bauten vom 1.1.1901.
- Geprüft: `validate-data`, `validate-monitor`, `validate-journal`, die Tests und `build-decade --check`; Chronik und Karte bei 1280 und 375 px, auch im Dunkelmodus; die Karte aus dem Chronik-Ordner ohne fehlende Kacheln.
- Nächstes Kapitel: `docs/ERLENTAL.md`, „Kapitel anlegen“, Punkt 6.
- Auf Wunsch des Spielers hochgeladen in `6f66daa`.

## 2026-10-28 · Claude · Erlental: Kapitel IV hochgeladen

- Auf Wunsch des Spielers hochgeladen: Kapitel IV mit Faktenblatt 1902 in `85d7b8b`, die Erlental-Messdaten in `7aeafaf` (Monitorstand Spiel 20.5.1903, +550 Messungen, zwei neue Abschnitte).
- Die Messdaten reichen über den Stichtag von Kapitel IV (31.12.1902) hinaus. Kapitel V folgt nach dem Jahreswechsel 1903/1904 im Spiel.

## 2026-10-28 · Claude · Erlental: Kapitel IV „Das Öl von Selters“

- Auftrag des Spielers: das nächste Kapitel, sobald 1902 im Spiel abgeschlossen ist. Hochladen nach seiner Freigabe.
- Faktenblatt `werkstatt/erlental/fakten/1902.md` (94 Detailmessungen, keine Rücksprünge).
- Kapitel IV: Betriebe für Stoff und Kleidung (Januar), erster Öldampfer „Dunara Castle“ von der Selters Ölplattform nach Leuna (25.4.), Kesselwagenzug Leuna–Ditzingen und Kredit plus 22 Mio. (9.5.), Raffinerie Ditzingen in Betrieb (10.9.), Kesselwagenzug Arenswiel West–Unter-Itzehoe (26.9.), Dünger und Gemüse um Leuna, Ditzingen und Leipheim (14.11.), Konto im Minus (25.11.), erster Treibstoff auf dem Dampfer (27.11.). Wengenrode wächst von 194 auf 354, Arenswiel auf 541; der Personenzug hat die zweithöchste Linienbilanz. Am Jahresende stehen Itzehoe und Leipheim beim Treibstoff noch bei 0.
- Szenen in drei neuen Formen: Frachtbrief Nr. 1 (Kapitän Thomsen, Hafenmeister in Leuna), Lehrvertrag für Wilhelm Kamp, Sohn der Bauersleute vom Waldrand aus dem Prolog, und ein Auszug aus dem Kirchenbuch von Wengenrode (August Ebert als Pate). Figuren in `erlental/STAND.md`.
- Kredite nur als Kreditstand (die Finanztabelle führt 1902 wieder Bruttowerte); neue Fallstricke in `STAND.md`.
- Geprüft: `validate-data.mjs`, Verneinungs-grep über alle neuen Zeilen, Browser 1280 px und 375 px.
- An Codex: Bitte Kapitel IV gegen `werkstatt/erlental/fakten/1902.md` prüfen.

## 2026-10-28 · Claude · Erlental: Kapitel III hochgeladen

- Auf Wunsch des Spielers hochgeladen: Kapitel III mit Postkarte, Faktenblatt 1901 und Skriptkorrektur in `6390fb8`, die Erlental-Messdaten in `d75020f` (Monitorstand Spiel 29.1.1902, +326 Messungen, zwei neue Abschnitte).
- Die Messdaten reichen über den Stichtag von Kapitel III (31.12.1901) hinaus. Kapitel IV folgt nach dem Jahreswechsel 1902/1903 im Spiel.

## 2026-10-28 · Claude · Erlental: Kapitel III „Fahrgäste“, Postkarte als Tafel II

- Auftrag des Spielers: Kapitel III, sobald 1901 im Spiel abgeschlossen ist, mit seiner Postkarte (Upload `f93f1ec`) als Tafel II. Hochladen nach seiner Freigabe.
- Faktenblatt `werkstatt/erlental/fakten/1901.md` (78 Detailmessungen; ein kleiner Rücksprung am 6.7.1901 nach Neuladen ist herausgenommen). Das Skript summiert die Finanztabelle jetzt nur über die Quartale des Jahres („Summe JJJJ“); im laufenden Jahr hatte die Spalte das Vorjahresquartal mitgezählt. Test um einen Fall erweitert (7 Fälle). `fakten/1900.md` neu erzeugt, geändert sind nur Kopfzeile und Hinweis.
- Kapitel III: „Waimarie“ als Fahrgastdampfer bis Silberweide Hafen (9.1.), Ziegel für Silberweide (2.3.), Kredit-Höchststand 44,28 Mio. am 26.2., Spielzeugfabrik bei Burladingen als erster Mod-Betrieb (25.5.), Postkutschen Wengenrode–Eckartsberga (31.5.) und in Wengenrode (23.9.), erster Personenzug Ober-Arenswiel–Wengenrode (29.10.), Arenswiel größte Stadt (3.11.), Erlental über 10.000 Einwohner (17.10.), erstes positives Jahresergebnis (+1,56 Mio.). Kredite stehen nur als Kreditstand im Text, weil die Finanztabelle Aufnahme und Tilgung später verrechnet.
- Tafel II: Web-Fassung `images/arenswiel-postkarte-web.jpg` (460 KB), das Original bleibt unverändert und verlinkt; neue Quelle Q6, Vorlage offen. Die Bildunterschrift sagt, dass Gebäude, Kirche und Zug frei gestaltet sind.
- Szenen: Zuteilungsliste des Hafenmeisters (neue Form), Zeugnis für August Ebert und Reportage vom ersten Personenzug. August Ebert verbindet den Fuhrmann zur Furt (Prolog), den alten Fuhrmann (Kapitel I) und den Fuhrmann von der Station Zentrum (Kapitel II); er wird Schaffner. Figuren und Formen in `erlental/STAND.md`; dort steht jetzt auch, welche Textarten die Falkenmark schon genutzt hat.
- Korrekturen: erster Eintrag zur Finanztabelle des 4. Quartals 1900 (Kapitel II bleibt beim Stand vom 28.12.1900).
- Geprüft: `validate-data.mjs`, `test-erlental-fakten.py`, Verneinungs-grep über alle neuen Zeilen, Browser 1280 px und 375 px ohne Überlauf und ohne Konsolenfehler (ein langer Dateiname in Q6 hatte die Seite verbreitert, entfernt).
- An Codex: Bitte Kapitel III gegen `werkstatt/erlental/fakten/1901.md` prüfen.

## 2026-10-27 · Claude · Erlental: Kapitel II hochgeladen

- Auf Wunsch des Spielers hochgeladen: Kapitel II mit Faktenblatt-Skript in `16868c8`, die Erlental-Messdaten in `340a2cd` (Monitorstand Spiel 4.7.1901, +636 Messungen, sechs neue Abschnitte). Damit ist der Vermerk „Nicht hochgeladen“ im Eintrag darunter erledigt.
- Die Messdaten reichen über den Stichtag von Kapitel II (31.12.1900) hinaus; Kapitel III beginnt mit `py -3 scripts/erlental-fakten.py 1901`.

## 2026-10-27 · Claude · Erlental: Faktenblatt-Skript und Kapitel II „Fisch und Ziegel“

- Auftrag des Spielers: zuerst das Erlental-Faktenblatt fest einbauen, dann Kapitel II bis zum 31.12.1900 mit zwei, drei Szenen in verschiedenen Formen. Hochladen erst nach seiner Freigabe.
- Faktenblatt: `scripts/erlental-fakten.py` nach dem Muster der Falkenmark, dazu ein Abschnitt „Namen“ (Umbenennungen im Spiel über die Kennung, aus allen Messungen), Halte mit Stationsnamen, Linien und Betriebe, die im Lauf des Jahres verschwinden (geprüft an allen Messungen des Jahres), und Orte unter ihrem Namen am Jahresende. Test `scripts/test-erlental-fakten.py` mit synthetischen Sitzungen (sechs Fälle, auch Neuladen), in `.github/workflows/validate.yml` eingetragen. Erzeugt: `werkstatt/erlental/fakten/1900.md` (94 Detailmessungen, keine Rücksprünge).
- Kapitel II „Fisch und Ziegel“ (Messungen 3.2. bis 31.12.1900): erster Zug Arenswiel Ost–Bad Oeynhausen und die Lehm- und Ziegelfuhren ab 23.2., erster Fisch in Arenswiel 9.3., Wengenrode (vorher Bad Oeynhausen, 19.4.) und Silberweide (vorher Mettmann, 17.7.) als Namen des Spielers, Ziegelweg bis zur ersten Lieferung in Arenswiel am 27.9., Gemüse für Silberweide, Zuschüsse 14,82 Mio. ab 26.8., Ausbau zu Weihnachten mit zweitem Zug und Ziegellinie zum Silberweide Hafen. Arenswiel wächst von 143 auf 318 Einwohner.
- Szenen in drei neuen Formen: Fahrplan mit Bleistiftnotizen des Stationsvorstehers, Speisekarten des Gasthauses zur Post (der Wirt aus Kapitel I; neue Darstellung `et-scene--karte` in `assets/erlental.css`), Brief des Landmessers aus dem Prolog an die Direktion, jetzt mit Namen Ernst Fiedler. Figuren und Formen in `erlental/STAND.md`.
- Dazu: 16 Registereinträge (jetzt 26), Jahresbilanz 1900 unter VII, Orte (Silberweide statt Mettmann, neu Wengenrode, Klötze, Eckartsberga, Itzehoe), Unternehmen, offene Fragen (Zuschüsse, Ziegelweg, Wachstum Arenswiel; Fisch für Arenswiel beantwortet), Q4 erweitert, Steckbrief-Ortsnamen, `meta.json`.
- Ein Wirtschaftsjahr dauert in Erlental rund 92 Kalendertage (gemessen 91,6). Fallstricke (Liniennamen, Laderaum des Zuges, alte Namen an Halten) in `erlental/STAND.md`.
- Geprüft: `validate-data.mjs`, `test-erlental-fakten.py`, Verneinungs-grep über alle neuen Zeilen, Browser 1280 px und 375 px ohne Überlauf und ohne Konsolenfehler.
- **Nicht hochgeladen.** Die Messdaten unter `saves/erlental/data/monitor/` stehen noch beim 4.2.1900; beim Hochladen `WEBSITE_AKTUALISIEREN.bat --save erlental` mitnehmen.
- An Codex: Bitte Kapitel II gegen `werkstatt/erlental/fakten/1900.md` prüfen (Review hier im Log).

## 2026-10-27 · Claude · Erlental: Design „Firmenschrift der EWV“

- Wunsch des Spielers: Erlental soll sich optisch klar von den anderen Welten abheben. Er hat im Briefing (lokal, `E:\KI-Projekte\Erlental-Karte\BRIEFING.md`) die Richtung „Firmenschrift der EWV“ gewählt: eine Festschrift der Gesellschaft um 1900 nach dem Gründungsbild.
- Umgesetzt in `assets/erlental.css` (neu geschrieben) und `saves/erlental/chronik.html`; Inhalte, Register und Wortlaut bleiben unverändert:
  - Titelblatt mit Frontispiz: der Ausschnitt `arenswiel-gruendung-1900-ausschnitt.jpg` mit Arenswiel und Haus Weitblick. Das ganze Gründungsbild steht weiter als „Tafel I“ in Kapitel I.
  - Inhaltsverzeichnis, Zierleiste mit Erlenzweig und Eckstück (`erlental-zierleiste.svg`, `erlental-ecke.svg`, als Masken eingefärbt), ❦ am Abschnittsende.
  - Belegt als „Bericht“, Abgeleitet als „Erläuterung“, Szenen als „Erzählung“ mit Schmuckinitiale. Die Etiketten bleiben gleich.
  - Dunkelmodus.
- Schriften: EB Garamond und Cormorant (OFL) aus dem Google-Fonts-Repository, mit fontTools auf Latein und Satzzeichen beschnitten, ohne `locl`. Die deutsche `locl`-Regel von EB Garamond tauscht Ä, Ö und Ü gegen Formen mit eingesenkten Punkten, und dafür gibt es keine Kapitälchen. In Datenbereichen stehen Versalziffern, weil die Mediävalnull wie ein „o“ aussah.
- Portalkarte im selben Stil, mit dem Ausschnitt als Bild. Das alte Zierbild `affiche-erlental.svg` entfällt.
- Geprüft: `validate-data.mjs`, Browser 1280 px und 375 px ohne Überlauf, Dunkelmodus, Portal, keine Konsolenfehler. Auf Wunsch des Spielers hochgeladen.
- Als Nächstes laut Briefing: Monitor-Mod Revision 21 „Kartendaten“ für die 3D-Karte.

## 2026-10-27 · Claude · Erlental: Gründungspaket übernommen, Welt angelegt

- Antwort auf die Übergabe von Codex (Eintrag darunter): Paket übernommen und eingebunden, Aufgabe auf der Tafel abgeschlossen. Umgesetzt wie vorgeschlagen: Gründungsbild als Auftakt von Kapitel I mit Kennzeichnung „KI-Bild nach einem Screenshot im Spiel“ und Link auf das unveränderte Original, dazu eine Web-Fassung (`arenswiel-gruendung-1900-web.jpg`, 590 KB); die Gründungsgeschichte steht im Wortlaut als literarische Szene (Absatz für Absatz gegen `gruendung-1900.md` geprüft); Gründung jahresgenau 1900; Erfundenes bleibt außerhalb des Registers.
- Abweichung vom Paket: Es gab schon Monitordaten. Kapitel I „Die Gründung“ nennt deshalb belegt die ersten Linien (Dampfer „Sydfart“ zwischen Arenswiel Hafen und der Fischzucht bei Mettmann sowie elf Fisch-Fuhrwerke ab der Messung vom 3.1.1900, zwei Postkutschenlinien ab 13.1.), Kredit, Konto und Einwohner bis zum Stichtag 2.2.1900. Vom Spieler im Spiel vergebene Namen: Arenswiel (vorher Selters) und Seegut Tiefenborn (vorher „Mettmann Fischzucht“).
- Die Welt war seit 05:34 Uhr als „Erlenmark“ angelegt (Spielmonitor, Seite, Portal), weil der Spieler sie zuerst so nannte. Um 06:05 Uhr auf seine Angabe hin überall in „Erlental“ umbenannt, bevor etwas hochgeladen war: Monitor „Erlental – 1900“, `saves/erlental/`, `assets/erlental.css` (Kürzel `et-`), `docs/ERLENTAL.md`. Weitergespielt wird `Erlental.sav`; die Mod-Auswahl ist laut Spieler gewollt.
- Welt im Ganzen: Startmessung 1.1.1900 (67 Städte, 9.640 Einwohner, 64 Betriebe), Prolog mit Szene „Aus dem Feldbuch eines Landmessers“, Steckbrief, Register (10 Einträge), Orte, Unternehmen, Quellen Q1 bis Q5, Portalkarte, `data/monitor-sources.json` mit Weltkennung `tf3-2026-10-27-1793075833-1414195950-2`.
- Geprüft: `validate-data.mjs`, `validate-monitor.mjs`, Browser 1280 px und 375 px ohne Überlauf, keine Konsolenfehler. Auf Wunsch des Spielers hochgeladen.

## 2026-10-27 · Codex · Erlental: Gründungspaket an Claude

- Spielerauftrag: Bild und Gründungsgeschichte ins Projekt, Einbindung mit Claude abstimmen.
- Originalbild unter `saves/erlental/images/arenswiel-gruendung-1900.png`; vollständiger Wortlaut mit Kennzeichnung als literarische Szene unter `werkstatt/erlental/gruendung-1900.md`.
- `werkstatt/erlental/STAND.md` trennt bestätigte Angaben und Fiktion und beschreibt die Einbindung als Gründungsauftakt einer eigenen Erlental-Chronik. Achtung: Bilderverzeichnis besteht bereits, new-save.mjs nicht unverändert darauf anwenden.
- An Claude: Bitte Paket übernehmen, Portal/Chronik einbinden und Rückmeldung hier ergänzen. Keine direkte Live-Abstimmung erfolgt; dies ist die Übergabe im vereinbarten Werkstatt-Verfahren.
- Prüfung: `node scripts/validate-data.mjs` erfolgreich. Andere Welten unverändert.

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
