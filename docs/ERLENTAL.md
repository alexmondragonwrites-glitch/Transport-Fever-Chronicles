# Erlental – Chronik ab 1900

Dritte Welt im Archiv, angelegt am 27.10.2026. Eigenständiger TF3-Spielstand, Startjahr 1900, getrennt vom Archipel des Alizés und von der archivierten Falkenmark: Orte, Unternehmen und Ereignisse von dort werden nicht übernommen, Vergleiche zwischen den Welten nur auf ausdrückliche Bitte des Spielers. Wer gerade woran schreibt, wie weit erzählt ist und welche Messwerte bereitliegen: `werkstatt/erlental/STAND.md` und `werkstatt/AUFGABEN.md`.

Der Name der Welt ist „Erlental“, ohne Artikel („in Erlental“, „eine Karte Erlentals“), so wie in der Gründungsgeschichte des Spielers. Der Spieler nannte sie zuerst „Erlenmark“ und hat das am selben Morgen richtiggestellt; „Erlenmark.sav“ ist eine Kopie desselben Starts. „Chronik ab 1900“ ist ein Arbeitstitel.

## Wo was liegt

| Datei | Inhalt |
|---|---|
| `saves/erlental/chronik.html` | Die Chronik von Staffel 1 (1900 bis 1909, Kapitel I bis XI, abgeschlossen): Prolog, Steckbrief, Register, Kapitel, Orte, Unternehmen, Auswertungen, offene Fragen, Quellen, Korrekturen. Handgeschrieben. |
| `saves/erlental/staffel-2.html` | Die Chronik von Staffel 2 (1910 bis 1919, Kapitel ab I, seit 2.11.2026): Rückblick, Steckbrief, Register (`data-season="2"`), Kapitel, Orte, Unternehmen, Auswertungen, offene Fragen, Quellen, Korrekturen. Handgeschrieben. |
| `saves/erlental/netzplan/JJJJ.html` | Netzplan am Ende eines Spieljahres, ab Staffel 2 (seit 2.11.2026): eigene Seite mit der Übersichtskarte aller Personenlinien und den Stadtplänen der Orte mit Straßenbahn; das Kapitel des Jahres lädt sie nach. Erzeugt von `scripts/erlental-netzplan.py JJJJ`, nicht von Hand ändern. |
| `saves/erlental/data/events.json` | Ereignisregister, einzige Quelle. `chronik.html`, `staffel-2.html` und die Datenansicht lesen es. Append-only. Neue Einträge tragen die Staffel im Feld `season`; Einträge ohne Feld gehören zu Staffel 1. |
| `saves/erlental/data/meta.json` | Kurzbeschreibung, Status, Monitor-Weltname und Weltkennung. |
| `saves/erlental/data/manifest.json` | `latestReport: staffel-2.html` (die Weltseite leitet auf die laufende Staffel weiter; seit 2.11.2026 Staffel 2), `monitor_data` für die Messdaten. |
| `saves/erlental/data/monitor/` | Messdaten aus dem Spielmonitor, geschrieben von `publish-monitor.py`. Nicht von Hand ändern. |
| `saves/erlental/images/` | Bilder der Chronik. `arenswiel-gruendung-1900.png` ist das Original des Gründungsbilds (bleibt unverändert), `arenswiel-gruendung-1900-web.jpg` die Fassung für Kapitel I („Tafel I“), `arenswiel-gruendung-1900-ausschnitt.jpg` der Ausschnitt mit Arenswiel und Haus Weitblick für Titelblatt und Portalkarte. KI-Bilder als solche kennzeichnen, mit Vorlage. |
| `saves/erlental/karte/` | 3D-Karte (Q7): gebaute Seite mit je Kapitel einem Kartenstand unter `karte/staende/<Spieltag>/`. Erzeugt in `E:\KI-Projekte\Erlental-Karte` (lokal; Spielmodelle bleiben dort), gebaut mit `veroeffentlichen.py`. Nicht von Hand ändern. Gleiche Kacheln liegen nur einmal beim neuesten Stand; `kacheln.json` nennt unter `herkunft`, wo. Verweise aus der Chronik: `karte/#kapitel-N` (Staffel 1), ab Staffel 2 `karte/#staffel-N-kapitel-M`. |
| `werkstatt/erlental/fakten/JJJJ.md` | Faktenblatt je Spieljahr aus dem Spielmonitor, erzeugt von `scripts/erlental-fakten.py`. Nicht von Hand ändern. |
| `werkstatt/erlental/gruendung-1900.md` | Wortlaut der Gründungsgeschichte, wie der Spieler sie geliefert hat. Die Chronik übernimmt ihn unverändert. |
| `assets/erlental.css`, `assets/erlental-zierleiste.svg`, `assets/erlental-ecke.svg`, `assets/fonts/eb-garamond*.woff2`, `assets/fonts/cormorant*.woff2` | Eigenes Erscheinungsbild „Firmenschrift der EWV“, unabhängig von `styles.css` und `falkenmark.css`, mit Ornamenten und Schriften. Die Portalkarte hat passende Regeln in `styles.css` (`.world-card[data-world="erlental"]`). |

## Erscheinungsbild: „Firmenschrift der EWV“

Seit 27.10.2026 auf Wunsch des Spielers ein eigenes Design, klar unterschieden von Falkenmark (Heimatkalender) und Archipel (Tropenplakat). Leitbild: Festschrift einer Verkehrsgesellschaft um 1900, Historismus mit ersten Jugendstil-Zügen. Den Ton gibt das Gründungsbild vor.

- **Farben** (Variablen in `assets/erlental.css`):
  - Chamois-Papier (`--et-paper`, heller `--et-paper-2`, getönt `--et-paper-3`) und Druckbraun (`--et-ink`).
  - Bronze für Linien, Rahmen und Ornamente (`--et-bronze`).
  - Waldgrün für Kopf- und Fußleiste (`--et-wald`).
  - Seeblau für Belegt (`--et-see`), Felsocker für Abgeleitet (`--et-ocker`), Siegelrot für Szenen, Initialen und Schlüsselereignisse (`--et-siegel`).
  - Im Dunkelmodus (`prefers-color-scheme: dark`) dunkles Papier mit Elfenbeinschrift. Waldgrüner Text und Linien laufen dann über `--et-firma` und `--et-linie` und werden heller.
- **Schriften**, lokal unter SIL OFL: EB Garamond für den Text (Mediävalziffern, Kapitälchen über `font-variant-caps: all-small-caps`) und Cormorant für Titel und Kennzahlen. In Tabellen, Jahresleiste und Kennzahlen stehen Versalziffern mit fester Breite.
  - Beschnitten mit fontTools auf Latein und Satzzeichen, alle OpenType-Features außer `locl`. EB Garamond tauscht für Deutsch sonst Ä, Ö, Ü gegen Formen mit eingesenkten Punkten, und dafür fehlen Kapitälchen.
  - Neu beschneiden: Feature-Liste aus der Originaldatei ohne `locl` an `--layout-features` übergeben.
- **Ornamente** als SVG-Masken, eingefärbt per Stylesheet:
  - `erlental-zierleiste.svg` (Erlenzweig mit Blättern, Zapfen und Kätzchen) unter jeder Abschnittsüberschrift und auf dem Titelblatt;
  - `erlental-ecke.svg` (Eckstück) an Frontispiz und Szenen;
  - das Blatt-Ornament ❦ als Abschluss jedes Abschnitts.
- **Titelblatt:** Frontispiz links (Ausschnitt aus dem Gründungsbild, gerahmt, mit Eckstücken), Titel rechts. Darunter Zierleiste, Firmenname in Kapitälchen und „Arenswiel · Haus Weitblick · Gegründet 1900“. Das ganze Gründungsbild steht als „Tafel I“ in Kapitel I.
- **Textarten:**
  - Belegt als „Bericht“: helles Papier, Doppellinie in Seeblau, Quellenvermerk kursiv.
  - Abgeleitet als „Erläuterung“: Doppelrandlinie in Ocker, ohne Kasten.
  - Literarische Szene als „Erzählung“: getöntes Papier, Rahmen mit Eckstücken, Blocksatz und Schmuckinitiale in Siegelrot.
  - Die Etiketten „Belegt“, „Abgeleitet“, „Literarische Szene“ bleiben.

Die Klassen tragen das Kürzel `et-`; die Bausteine (Kapitel, Übersicht, Zeitachse, Linien-Schemata, Jahresauswahl) heißen wie bei der Falkenmark, sehen aber eigenständig aus. Änderungen an `erlental.css` wirken nur hier.

## Staffeln

Wunsch des Spielers vom 1.11.2026: Erlental wird in Staffeln zu je zehn Spieljahren erzählt, für Chronik und Karte. Staffel 1 umfasst 1900 bis 1909, Staffel 2 1910 bis 1919, Staffel 3 1920 bis 1929 und so weiter. Für Staffel 2 hat der Spieler eine eigene Seite mit Kapiteln ab I gewählt.

- Jede Staffel hat eine eigene Seite. Staffel 1 ist `chronik.html` mit Kapitel I bis XI; Kapitel XI reicht mit dem Jubiläum bis 30.1.1910. Staffel 2 steht seit dem 2.11.2026 in `saves/erlental/staffel-2.html`, Staffel 3 kommt nach `staffel-3.html`. Fußzeile und Skripte (Register, Kapitelnavigation, Jahresauswahl) sind auf allen Staffelseiten gleich, ab Staffel 2 kommt das Skript für den Netzplan dazu; Änderungen daran auf allen nachziehen.
- Die Kapitel zählen in jeder Staffel ab I, die Anker heißen auf jeder Seite `#kapitel-N`. Außerhalb der eigenen Seite immer mit Staffel nennen: „Staffel 2 · Kapitel I“.
- Das letzte Kapitel einer Staffel darf in den Januar des Folgejahres reichen, so wie Kapitel XI mit dem Jubiläum. Die neue Staffel beginnt mit dem 1. Januar ihres ersten Jahres und nimmt diese Wochen als Rückbezug.
- Eine neue Staffelseite entsteht mit ihrem ersten Kapitel, im Aufbau von `chronik.html`: Titelblatt mit „Staffel N: Jahre“, Prolog als Rückblick auf die vorige Staffel, Steckbrief, Register, Kapitel, Orte, Unternehmen, Auswertungen, offene Fragen, Quellen, Korrekturen. Orte, Unternehmen und offene Fragen setzen den Stand der vorigen Staffel fort; deren Seite bleibt auf ihrem Schlussstand. Die Quellennummern laufen über alle Staffeln weiter, die nächste freie steht in `werkstatt/erlental/STAND.md`.
- Register: `data/events.json` bleibt eine Datei für alle Staffeln. Neue Einträge tragen `"season": N`, Einträge ohne Feld gehören zu Staffel 1. Jede Staffelseite zeigt ihre Einträge über `data-season` an `#register-rows`.
- Mit dem ersten Kapitel einer neuen Staffel außerdem: `data/manifest.json` (`latestReport`) auf die neue Seite stellen; auf der vorigen Seite „Staffel N ab …“ im Titelblatt und den Hinweis am Schluss ihres letzten Kapitels zu Links machen; `meta.json` und `data/worlds.json` nachziehen, wo sie die Staffel nennen.
- Karte: Die Kartenstände stehen nach Staffeln gruppiert in `Erlental-Karte/zeitleiste.json` (Regel dort und im `LIESMICH`). Staffel 1 behält `kapitel-1` bis `kapitel-11`. Kapitel späterer Staffeln heißen auf der Karte `staffel-N-kapitel-M`: Die Kartenzeile im Kapitelkopf verweist auf `karte/#staffel-2-kapitel-1`, die Karte zurück auf `staffel-2.html#kapitel-1`. Alle Staffeln teilen einen Kartenzeitstrahl (Entscheidung des Spielers vom 1.11.2026): Wald und Geländescan bleiben die von Staffel 1, und das erste Kapitel von Staffel 2 wird wie jedes neue Kapitel nur an seinen Änderungen gegen Kapitel XI gebacken.

## Netzplan

Wunsch des Spielers vom 2.11.2026: Weil das Netz wächst, bekommt ab Staffel 2 jedes Kapitel einen Netzplan zum Zurechtfinden, im Stil der Zeit und mit den Jahren moderner. `scripts/erlental-netzplan.py JJJJ` zeichnet ihn aus der letzten Messung des Jahres (Linien, Halte, Fahrzeugmodelle), den geo-Lagen der Haltestellen und Orte, dem Kartenexport des Kapitels (Verlauf jeder Linie über ihre Kanten, Straßen, Gleise, Gebäude) und dem Geländescan der 3D-Karte (Gewässer). Den Export nennt der Kartenstand in `Erlental-Karte/zeitleiste.json`; steht das Kapitel dort noch nicht, nimmt das Skript den ersten vollständigen Export vom Januar des Folgejahres aus der Kartenhistorie des Monitors. So entsteht der Plan auch vor dem Backen der Karte (Kapitel II, 1911). Läuft nur auf dem Rechner des Spielers, braucht etwa eine Minute und erzeugt rund 80 bis 110 KB.

- Übersichtskarte: alle Personenlinien; die übrigen Gleise als Güterbahn; Orte mit Linien und Orte ab 300 Einwohnern mit Namen; Anleger der Dampfer außerhalb der Orte. Kopf, Maßstab und Zeichen-Erklärung stehen im Band unter der Karte, damit das Netz frei bleibt. Auf dem Handy lässt sich die Karte seitlich schieben.
- Stadtpläne: je Ort mit Straßenbahn, mit Straßen, Ortslage, Haltestellen, Bahnhöfen und Liniennummern am ersten Halt. Der Ausschnitt umfasst die Halte der Ortslinien bis 1 km um die Ortsmitte und die Bahnhöfe der Personenzüge bis 1,5 km; Linien, die weiter hinausführen, laufen über den Rand. Eine Linie gehört zu dem Ort, der dem Mittel ihrer Halte am nächsten liegt. Die Nummern stammen aus den Linienkennungen des Spiels (`…-LO-3`) und gelten je Verkehrsmittel: Kreise für Straßenbahnen, Quadrate für Omnibusse und Postkutschen.
- Arten nach Fracht und Fahrzeugmodell: Personenlinien sind Linien, deren Fracht nur aus Fahrgästen besteht (es zählt allein die Fracht, auch bei Namen wie „RC Passagiere,Gemüse-Sil-LO-2“). Pferdetram ergibt Pferdebahn, Postkutsche ergibt Postkutsche, sonst Straßenbahn oder Omnibus. Für Dampfer liefert der Export nur die Anleger; das Skript zeichnet den kürzesten Kurs über das Wasser und nennt das im Nachweis unter dem Plan.
- Stil je Epoche: Titel und Wortlaut in `STILE` im Skript, Schrift, Farben und Zeichen im Abschnitt Netzplan von `assets/erlental.css` (Klasse `np--<stil>`). Bis 1919 gilt „Kaiserzeit“: Papier, Garamond und Cormorant, die Bahn im schwarz-weißen Bahnzeichen, Straßenbahnen rot, Uferlinien wie im Stich. Den Stil der nächsten Staffel mit dem Spieler festlegen, bevor ihr erstes Kapitel entsteht. Vorschläge: 1920er sachlich mit Grotesk (Jost liegt bei den Schriften) und farbigen Liniennummern, 1930er mit den ersten schematischen Linienplänen, danach Bundesbahn-Art, zuletzt ein heutiger Liniennetzplan.

## Kapitel anlegen

Jedes Kapitel ist ein `<article class="et-chapter" id="kapitel-N" data-year="JJJJ">` in `#kapitel` auf der Seite seiner Staffel und bekommt einen Eintrag in der Kapitelnavigation (`.et-chapnav`). Reicht ein Kapitel über einen Jahreswechsel, stehen beide Jahre im Attribut (`data-year="1901 1902"`). Jede Jahresbilanz unter VII steht in `<div class="et-yearblock" data-year="JJJJ">`.

**Jahresauswahl:** Die Leiste `#jahre` erscheint von selbst, sobald es ein Kapitel gibt, und baut sich aus den `data-year`-Attributen (Jahrzehnt wählen, dann das Jahr). Adresse `#jahr-1901`, alles: `#jahr-alle`. Register und Netzplan laden nach dem ersten Sprung; damit Adressen wie `#kapitel` oder `#netzplan-1910` trotzdem ankommen, fasst die Seite danach noch einmal nach (`et:register`, `et:netzplan`), höchstens acht Sekunden lang und bis jemand selbst scrollt, tippt oder klickt.

Aufbau eines Kapitels (Muster: Kapitel I):

1. Kopf: `<header class="et-chapter-head"><h3><span class="et-chapter-no">Kapitel N</span> Titel</h3><p class="et-chapter-period">Zeitraum</p></header>`. Kapitel haben einen Stichtag (Messung mit Spieldatum und Aufnahmezeit), weil der Spieler beim Schreiben weiterspielt.
2. Optional ein Bild (`figure.et-founding`), bei KI-Bildern so gekennzeichnet, mit Link auf das Original.
3. Übersicht `.et-overview`: Kennzahlen (`.et-stat`, `--neg` für Verluste), Zeitachse (`ol.et-timeline`, Schlüsselereignis mit `is-key`) und Linien-Schemata (`figure.et-route` mit `et-stop`, `et-leg`, `et-leg--assumed` für abgeleitete Verläufe, `et-leg--ware` für mögliche Warenwege ohne Linie, `et-stop--ring` für Linien im Ort). Nur Zahlen und Daten, die wörtlich im Text oder im Register stehen.
4. Textblöcke: `div.et-block.et-block--belegt` (Quelle als letzter Absatz `p.et-source`), `div.et-block.et-block--abgeleitet`, `div.et-scene` mit den Varianten `et-scene--dialog`, `et-scene--eintraege`, `et-scene--telegramm`, `et-scene--karte` (Speisekarte, Aushang: mittig gesetzt, Zwischentitel `p.et-karte-zeit`), `et-scene--lied` (Strophen als Absätze mit `<br>`, Kehrreim `p.et-kehrreim`), `p.et-randnotiz`, dazu `p.et-scene-note` (Vorbemerkung vor dem Titel) und `span.et-scene-sub` (Untertitel im `h3`).
5. Quellen als Badge: `<a class="et-q" href="#q4" data-tip="…" aria-label="Quelle Q4: …">Q4</a>`; die Quellenliste hat die Anker `#q1`, `#q2` … Die nächste freie Nummer steht in `werkstatt/erlental/STAND.md`.
6. Karte: Im Kopf unter dem Zeitraum `<p class="et-chapter-map"><a href="karte/#kapitel-N">Kapitel N auf der 3D-Karte</a> · Bilder vom …</p>`; auf Seiten ab Staffel 2 heißt der Verweis `karte/#staffel-N-kapitel-M`. Dafür das Kapitel in `Erlental-Karte/zeitleiste.json` eintragen (Stichtag, Kartenexport vom Jahreswechsel), dann in `E:\KI-Projekte\Erlental-Karte` nacheinander `karte_backen.py alle kapitel-N`, `karte_backen.py pruefen kapitel-N` (meldet schwarz gerendertes Gelände), `karte_daten.py` und `veroeffentlichen.py` (Codex-Python). Ein neues Kapitel backt nur seine Änderungen gegen das letzte, etwa eine halbe bis eine Stunde. Vorher den Export selbst prüfen (`complete`, Zahl der Bauten und Kanten). Ist der vom Jahreswechsel unvollständig, den letzten vollständigen davor nehmen und in der Kartenzeile nennen: „Bilder vom …, dem letzten vollständigen Kartenexport des Jahres“ (so in Kapitel VII).
7. Netzplan (ab Staffel 2): `py -3 scripts/erlental-netzplan.py JJJJ` ausführen, mit oder vor dem Kartenstand (siehe „Netzplan“); es schreibt `saves/erlental/netzplan/JJJJ.html`. Im Kapitel nach der Übersicht `<figure class="et-netzplan" id="netzplan-JJJJ">` mit dem Kasten `<div class="np-laden" data-netzplan="netzplan/JJJJ.html">` und der Bildunterschrift mit Q4 (Muster: Staffel 2 · Kapitel I), in der Kartenzeile `· <a href="#netzplan-JJJJ">Netzplan Ende JJJJ</a>`. Der Eintrag „Netzplan Ende JJJJ“ im Inhaltsverzeichnis (`a.et-toc-sub` unter IV · Kapitel) zeigt immer auf das neueste Jahr.

## Ereignisse eintragen

Jeder Eintrag in `events.json` braucht `id`, `date` (`JJJJ`, `JJJJ-MM` oder `JJJJ-MM-TT`, Spielzeit), `kind`, `category`, `title`, `description`, `source`. Dazu nach Bedarf `game_time_label` (Spielzeit in Worten), `recorded` (reales Datum der Aufnahme, `JJJJ-MM-TT`) und `recorded_note`. `kind`: `fakt` = Belegt, `rekonstruktion` = Abgeleitet, `fiktion` = Literarische Szene. Einträge nicht löschen; Fehler bekommen ein Feld `correction` mit `date` und `note` und einen Eintrag unter „Korrekturen“ in der Chronik. Erfundenes aus Szenen (Beratungen, Wirt, Fuhrmann, Büroausstattung) gehört nicht ins Register.

## Regeln aus dem Auftrag des Spielers

Es gelten dieselben Regeln wie für die Falkenmark (`docs/FALKENMARK.md`, Abschnitt „Regeln aus dem Auftrag des Spielers“):

1. Belegtes, Abgeleitetes und Erfundenes trennen.
2. Keine Einwohnerzahlen, Finanzwerte, Produktionsmengen, Eröffnungsdaten oder Verbindungen erfinden. Fehlendes bleibt offen.
3. Fiktive Personen und Zitate nur in Passagen mit dem Etikett „Literarische Szene“.
4. Spieljahr und reales Aufnahmedatum immer getrennt. Für die Gründung der Gesellschaft gilt das Jahr 1900; einen gemessenen Gründungstag gibt es nicht.
5. Orts- und Unternehmensnamen erst nach Bestätigung des Spielers verbindlich. Namen, die der Spieler im Spiel selbst vergibt (Arenswiel, Seegut Tiefenborn), gelten als bestätigt.
6. Aus der kleinen Kartenvorschau keine Himmelsrichtungen, Fließrichtungen oder Verbindungen ableiten. Entfernungen aus den Monitor-Positionen als Luftlinie angeben.
7. Widersprüche benennen und nachvollziehbar korrigieren.

Schreibweise (Wunsch des Spielers vom 25.10.2026, gilt für alle Chroniken): Formen variieren, natürlich klingen, Verneinungsfiguren meiden („nicht X, sondern Y“, „kein …“, „niemand …“) und keine KI-Phrasen. Was fehlt, positiv sagen: „fehlt“, „bleibt offen“, „steht still“. Neue Abschnitte mit `grep -n -w -E "nicht|kein|keine|nie|niemand|nichts|sondern|ohne"` prüfen. Texte, die der Spieler selbst liefert (wie die Gründungsgeschichte), stehen im Wortlaut. Formen und wiederkehrende Figuren in `werkstatt/erlental/STAND.md` nachhalten.

Ton: ruhige Regionalgeschichte mit gelegentlichen Reportagen, kein Werbeton, auch Umwege und stillstehende Orte erzählen. Die Zukunft wird nicht vorweggenommen.

## Erfahrungen aus der Falkenmark

- **Einstellungsseite und gespeicherte Welt:** Maßgeblich ist die Welt, die das Spielprotokoll beim Start und Speichern nennt. Bei Erlental stimmen Zufallswert (SpWJDQtUdp), Größe und Mod-Zahl der Einstellungsseite mit dem Protokoll überein.
- **Neuladen:** Lädt der Spieler einen älteren Stand, springt die Spielzeit zurück; die Messungen dahinter gehören zu einem verworfenen Abschnitt und werden nicht erzählt.
- **Werte „pro Jahr“** (Produktion, Versand, Linienbilanz) gelten für ein Wirtschaftsjahr des Spiels. In Erlental sind das rund 92 Kalendertage (gemessen Ende 1900 an den Bilanzzeiträumen der Linien, 91,6 Tage). Solche Werte mit ihrem Zeitraum nennen und nie als Kalenderjahr ausgeben.
- **Mods des Spielers** (Bauten, gesetzte Betriebe) als Hinweis mit Quelle nennen, als Ereignis der erzählten Welt nur, wenn der Spieler es so will. Die Mod-Auswahl von Erlental ist laut Spieler gewollt (Organic Towns deinstalliert, eigene Mods ausgeschaltet).

## Spielmonitor

Im Spielmonitor heißt die Welt „Erlental – 1900“ (am 27.10.2026 angelegt und vorgewählt, zuerst unter „Erlenmark – 1900“, am selben Morgen umbenannt), Weltkennung `tf3-2026-10-27-1793075833-1414195950-2`. Der Monitor lief beim ersten Laden, die erste Messung mit Positionen und Höhenraster steht deshalb in der Sitzung `20261027_053713_859866`; eine Kopie liegt in `Spielmonitor/exports/erlental-start-1900-01-01-geo.json`, das Spielprotokoll des Starts in `exports/tf3-spielprotokoll-2026-10-27-erlental.txt`. Weitergespielt wird `Erlental.sav`; `Erlenmark.sav` ist eine Kopie desselben Starts mit derselben Weltkennung. Wer beide abwechselnd lädt, erzeugt Rücksprünge (verworfene Abschnitte).

`WEBSITE_AKTUALISIEREN.bat` lädt Erlental mit hoch (Eintrag in `data/monitor-sources.json`, ohne Zeitung, `manifest_key: monitor_data`). Die Chronik selbst bleibt Handarbeit. Einzeln: `WEBSITE_AKTUALISIEREN.bat --save erlental`. Hochladen nur mit Freigabe des Spielers.

Faktenblätter: `py -3 scripts/erlental-fakten.py JAHR` schreibt `werkstatt/erlental/fakten/JAHR.md`, aufgebaut wie bei der Falkenmark, dazu Umbenennungen im Spiel, Stationsnamen der Halte und Linien, die im Lauf des Jahres verschwinden. Test: `py -3 scripts/test-erlental-fakten.py`. Kapitel I ist direkt aus den Sitzungsdaten geschrieben, Kapitel II nach dem Faktenblatt 1900; Daten nennt die Chronik nach der frühesten Messung, auch aus Grundmessungen.
