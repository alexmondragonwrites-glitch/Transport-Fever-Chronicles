# Erlental – Chronik ab 1900

Dritte Welt im Archiv, angelegt am 27.10.2026. Eigenständiger TF3-Spielstand, Startjahr 1900, getrennt vom Archipel des Alizés und von der archivierten Falkenmark: Orte, Unternehmen und Ereignisse von dort werden nicht übernommen, Vergleiche zwischen den Welten nur auf ausdrückliche Bitte des Spielers. Wer gerade woran schreibt, wie weit erzählt ist und welche Messwerte bereitliegen: `werkstatt/erlental/STAND.md` und `werkstatt/AUFGABEN.md`.

Der Name der Welt ist „Erlental“, ohne Artikel („in Erlental“, „eine Karte Erlentals“), so wie in der Gründungsgeschichte des Spielers. Der Spieler nannte sie zuerst „Erlenmark“ und hat das am selben Morgen richtiggestellt; „Erlenmark.sav“ ist eine Kopie desselben Starts. „Chronik ab 1900“ ist ein Arbeitstitel.

## Wo was liegt

| Datei | Inhalt |
|---|---|
| `saves/erlental/chronik.html` | Die Chronik: Prolog, Steckbrief, Register, Kapitel, Orte, Unternehmen, Auswertungen, offene Fragen, Quellen, Korrekturen. Handgeschrieben. |
| `saves/erlental/data/events.json` | Ereignisregister, einzige Quelle. `chronik.html` und die Datenansicht lesen es. Append-only. |
| `saves/erlental/data/meta.json` | Kurzbeschreibung, Status, Monitor-Weltname und Weltkennung. |
| `saves/erlental/data/manifest.json` | `latestReport: chronik.html` (die Weltseite leitet dorthin weiter), `monitor_data` für die Messdaten. |
| `saves/erlental/data/monitor/` | Messdaten aus dem Spielmonitor, geschrieben von `publish-monitor.py`. Nicht von Hand ändern. |
| `saves/erlental/images/` | Bilder der Chronik. `arenswiel-gruendung-1900.png` ist das Original des Gründungsbilds (bleibt unverändert), `arenswiel-gruendung-1900-web.jpg` die Fassung für Kapitel I („Tafel I“), `arenswiel-gruendung-1900-ausschnitt.jpg` der Ausschnitt mit Arenswiel und Haus Weitblick für Titelblatt und Portalkarte. KI-Bilder als solche kennzeichnen, mit Vorlage. |
| `saves/erlental/karte/` | 3D-Karte (Q7): gebaute Seite mit je Kapitel einem Kartenstand unter `karte/staende/<Spieltag>/`. Erzeugt in `E:\KI-Projekte\Erlental-Karte` (lokal; Spielmodelle bleiben dort), gebaut mit `veroeffentlichen.py`. Nicht von Hand ändern. Gleiche Kacheln liegen nur einmal beim neuesten Stand; `kacheln.json` nennt unter `herkunft`, wo. Verweise aus der Chronik: `karte/#kapitel-N`. |
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

## Kapitel anlegen

Jedes Kapitel ist ein `<article class="et-chapter" id="kapitel-N" data-year="JJJJ">` in `#kapitel` und bekommt einen Eintrag in der Kapitelnavigation (`.et-chapnav`). Reicht ein Kapitel über einen Jahreswechsel, stehen beide Jahre im Attribut (`data-year="1901 1902"`). Jede Jahresbilanz unter VII steht in `<div class="et-yearblock" data-year="JJJJ">`.

**Jahresauswahl:** Die Leiste `#jahre` erscheint von selbst, sobald es ein Kapitel gibt, und baut sich aus den `data-year`-Attributen (Jahrzehnt wählen, dann das Jahr). Adresse `#jahr-1901`, alles: `#jahr-alle`.

Aufbau eines Kapitels (Muster: Kapitel I):

1. Kopf: `<header class="et-chapter-head"><h3><span class="et-chapter-no">Kapitel N</span> Titel</h3><p class="et-chapter-period">Zeitraum</p></header>`. Kapitel haben einen Stichtag (Messung mit Spieldatum und Aufnahmezeit), weil der Spieler beim Schreiben weiterspielt.
2. Optional ein Bild (`figure.et-founding`), bei KI-Bildern so gekennzeichnet, mit Link auf das Original.
3. Übersicht `.et-overview`: Kennzahlen (`.et-stat`, `--neg` für Verluste), Zeitachse (`ol.et-timeline`, Schlüsselereignis mit `is-key`) und Linien-Schemata (`figure.et-route` mit `et-stop`, `et-leg`, `et-leg--assumed` für abgeleitete Verläufe, `et-leg--ware` für mögliche Warenwege ohne Linie, `et-stop--ring` für Linien im Ort). Nur Zahlen und Daten, die wörtlich im Text oder im Register stehen.
4. Textblöcke: `div.et-block.et-block--belegt` (Quelle als letzter Absatz `p.et-source`), `div.et-block.et-block--abgeleitet`, `div.et-scene` mit den Varianten `et-scene--dialog`, `et-scene--eintraege`, `et-scene--telegramm`, `et-scene--karte` (Speisekarte, Aushang: mittig gesetzt, Zwischentitel `p.et-karte-zeit`), `et-scene--lied` (Strophen als Absätze mit `<br>`, Kehrreim `p.et-kehrreim`), `p.et-randnotiz`, dazu `p.et-scene-note` (Vorbemerkung vor dem Titel) und `span.et-scene-sub` (Untertitel im `h3`).
5. Quellen als Badge: `<a class="et-q" href="#q4" data-tip="…" aria-label="Quelle Q4: …">Q4</a>`; die Quellenliste hat die Anker `#q1`, `#q2` … Die nächste freie Nummer steht in `werkstatt/erlental/STAND.md`.
6. Karte: Im Kopf unter dem Zeitraum `<p class="et-chapter-map"><a href="karte/#kapitel-N">Kapitel N auf der 3D-Karte</a> · Bilder vom …</p>`. Dafür das Kapitel in `Erlental-Karte/zeitleiste.json` eintragen (Stichtag, Kartenexport vom Jahreswechsel), dann in `E:\KI-Projekte\Erlental-Karte` nacheinander `karte_backen.py alle kapitel-N`, `karte_daten.py` und `veroeffentlichen.py` (Codex-Python). Ein neues Kapitel backt nur seine Änderungen gegen das letzte, etwa eine halbe bis eine Stunde.

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
