# Erlenmark – Chronik ab 1900

Dritte Welt im Archiv, angelegt am 27.10.2026. Eigenständiger TF3-Spielstand, Startjahr 1900, getrennt vom Archipel des Alizés und von der archivierten Falkenmark: Orte, Unternehmen und Ereignisse von dort werden nicht übernommen, Vergleiche zwischen den Welten nur auf ausdrückliche Bitte des Spielers. Wer gerade woran schreibt, wie weit erzählt ist und welche Messwerte bereitliegen: `werkstatt/erlenmark/STAND.md` und `werkstatt/AUFGABEN.md`.

„Chronik ab 1900“ ist ein Arbeitstitel; einen eigenen Titel legt der Spieler fest.

## Wo was liegt

| Datei | Inhalt |
|---|---|
| `saves/erlenmark/chronik.html` | Die Chronik: Prolog, Steckbrief, Register, Kapitel, Orte, Unternehmen, Auswertungen, offene Fragen, Quellen, Korrekturen. Handgeschrieben. |
| `saves/erlenmark/data/events.json` | Ereignisregister, einzige Quelle. `chronik.html` und die Datenansicht lesen es. Append-only. |
| `saves/erlenmark/data/meta.json` | Kurzbeschreibung, Status, Monitor-Weltname und Weltkennung. |
| `saves/erlenmark/data/manifest.json` | `latestReport: chronik.html` (die Weltseite leitet dorthin weiter), `monitor_data` für die Messdaten. |
| `saves/erlenmark/data/monitor/` | Messdaten aus dem Spielmonitor, geschrieben von `publish-monitor.py`. Nicht von Hand ändern. |
| `saves/erlenmark/images/` | Bilder der Chronik (noch leer). KI-Bilder als solche kennzeichnen, mit Vorlage. |
| `assets/erlenmark.css`, `assets/affiche-erlenmark.svg` | Eigenes Erscheinungsbild, unabhängig von `styles.css` und `falkenmark.css`. Dazu das Zierbild (keine Karte). Die Portalkarte hat passende Regeln in `styles.css` (`.world-card[data-world="erlenmark"]`). |

## Erscheinungsbild

Leitbild: Messtischblatt und Wiesenland um 1900. Büttenpapier mit Sumpfsignaturen und Wasserschraffur, Flussblau (`--em-water`, Kopfleiste `--em-deep`), Erlenrot wie frisch geschnittenes Erlenholz (`--em-alder`, Akzent), Ried (`--em-reed`), Kätzchengelb (`--em-ochre`, Abgeleitet), Schlehenviolett (`--em-slate`, Szenen). Grenzlinie als Kreisgrenze: Strich, Punkt, Punkt. Schriften lokal wie im übrigen Archiv: Source Serif 4 und Jost, Zahlen in der Systemschrift (`--em-mono`); keine Google Fonts, kein Playfair (Archipel).

Das Seitengerüst entspricht der Falkenmark, die Klassen tragen das Kürzel `em-` statt `fm-`. Änderungen an einer der beiden Dateien wirken nur in ihrer Welt.

## Kapitel anlegen

Jedes Kapitel ist ein `<article class="em-chapter" id="kapitel-N" data-year="JJJJ">` in `#kapitel`. Mit dem ersten Kapitel kommt die Kapitelnavigation dazu: `<nav class="em-chapnav" aria-label="Kapitel">` mit einem Link je Kapitel (`<a href="#kapitel-1"><span>Kapitel I</span> Titel</a>`), direkt unter dem einleitenden Absatz; der Satz „Das erste Kapitel folgt …“ fällt dann weg. Reicht ein Kapitel über einen Jahreswechsel, stehen beide Jahre im Attribut (`data-year="1901 1902"`). Jede Jahresbilanz unter VII steht in `<div class="em-yearblock" data-year="JJJJ">`.

**Jahresauswahl:** Die Leiste `#jahre` erscheint von selbst, sobald es ein Kapitel gibt, und baut sich aus den `data-year`-Attributen (Jahrzehnt wählen, dann das Jahr). Adresse `#jahr-1901`, alles: `#jahr-alle`.

Aufbau eines Kapitels:

1. Kopf: `<div class="em-chapter-head"><h3><span class="em-chapter-no">Kapitel N</span> Titel</h3><p class="em-chapter-period">Zeitraum</p></div>`.
2. Optional ein Bild (`figure.em-founding`), bei KI-Bildern so gekennzeichnet.
3. Übersicht `.em-overview`: Kennzahlen (`.em-stat`, `--neg` für Verluste), Zeitachse (`ol.em-timeline`, Schlüsselereignis mit `is-key`) und Linien-Schemata (`figure.em-route` mit `em-stop`, `em-leg`, `em-leg--assumed` für abgeleitete Verläufe, `em-leg--ware` für mögliche Warenwege ohne Linie, `em-stop--ring` für Linien im Ort). Nur Zahlen und Daten, die wörtlich im Text oder im Register stehen.
4. Textblöcke: `div.em-block.em-block--belegt` (Quelle als letzter Absatz `p.em-source`), `div.em-block.em-block--abgeleitet`, `div.em-scene` mit den Varianten `em-scene--dialog`, `em-scene--eintraege`, `em-scene--telegramm` und `p.em-randnotiz`.
5. Quellen als Badge: `<a class="em-q" href="#q4" data-tip="…" aria-label="Quelle Q4: …">Q4</a>`; die Quellenliste hat die Anker `#q1`, `#q2` … Die nächste freie Nummer steht in `werkstatt/erlenmark/STAND.md`.

## Ereignisse eintragen

Jeder Eintrag in `events.json` braucht `id`, `date` (`JJJJ`, `JJJJ-MM` oder `JJJJ-MM-TT`, Spielzeit), `kind`, `category`, `title`, `description`, `source`. Dazu nach Bedarf `game_time_label` (Spielzeit in Worten), `recorded` (reales Datum der Aufnahme, `JJJJ-MM-TT`) und `recorded_note`. `kind`: `fakt` = Belegt, `rekonstruktion` = Abgeleitet, `fiktion` = Literarische Szene. Einträge nicht löschen; Fehler bekommen ein Feld `correction` mit `date` und `note` und einen Eintrag unter „Korrekturen“ in der Chronik.

## Regeln aus dem Auftrag des Spielers

Es gelten dieselben Regeln wie für die Falkenmark (`docs/FALKENMARK.md`, Abschnitt „Regeln aus dem Auftrag des Spielers“):

1. Belegtes, Abgeleitetes und Erfundenes trennen.
2. Keine Einwohnerzahlen, Finanzwerte, Produktionsmengen, Eröffnungsdaten oder Verbindungen erfinden. Fehlendes bleibt offen.
3. Fiktive Personen und Zitate nur in Passagen mit dem Etikett „Literarische Szene“.
4. Spieljahr und reales Aufnahmedatum immer getrennt.
5. Orts- und Unternehmensnamen erst nach Bestätigung des Spielers verbindlich; Ortsnamen aus dem Spiel dürfen stehen.
6. Aus der kleinen Kartenvorschau keine Himmelsrichtungen, Fließrichtungen oder Verbindungen ableiten.
7. Widersprüche benennen und nachvollziehbar korrigieren.

Schreibweise (Wunsch des Spielers vom 25.10.2026, gilt für alle Chroniken): Formen variieren, natürlich klingen, Verneinungsfiguren meiden („nicht X, sondern Y“, „kein …“, „niemand …“) und keine KI-Phrasen. Was fehlt, positiv sagen: „fehlt“, „bleibt offen“, „steht still“. Neue Abschnitte mit `grep -n -w -E "nicht|kein|keine|nie|niemand|nichts|sondern|ohne"` prüfen. Formen und wiederkehrende Figuren in `werkstatt/erlenmark/STAND.md` nachhalten.

Ton: ruhige Regionalgeschichte mit gelegentlichen Reportagen, kein Werbeton, auch Umwege und stillstehende Orte erzählen. Die Zukunft wird nicht vorweggenommen.

## Erfahrungen aus der Falkenmark

- **Einstellungsseite und gespeicherte Welt:** Maßgeblich ist die Welt, die das Spielprotokoll beim Start und Speichern nennt. Bei der Erlenmark stimmen Zufallswert (SpWJDQtUdp), Größe und Mod-Zahl der Einstellungsseite mit dem Protokoll überein.
- **Neuladen:** Lädt der Spieler einen älteren Stand, springt die Spielzeit zurück; die Messungen dahinter gehören zu einem verworfenen Abschnitt und werden nicht erzählt.
- **Werte „pro Jahr“** (Produktion, Versand, Linienbilanz) gelten für ein Wirtschaftsjahr des Spiels. Wie viele Kalendertage das in der Erlenmark sind, zeigt die erste Bilanzmessung einer Linie (`balance_start_game_time`); bis dahin keine solchen Werte als Kalenderjahr ausgeben.
- **Mods des Spielers** (Bauten, gesetzte Betriebe) als Hinweis mit Quelle nennen, als Ereignis der erzählten Welt nur, wenn der Spieler es so will.

## Spielmonitor

Im Spielmonitor heißt die Welt „Erlenmark – 1900“ (angelegt und vorgewählt am 27.10.2026), Weltkennung `tf3-2026-10-27-1793075833-1414195950-2`. Der Monitor lief beim ersten Laden, die erste Messung mit Positionen und Höhenraster steht deshalb in der Sitzung `20261027_053713_859866`; eine Kopie liegt in `Spielmonitor/exports/erlenmark-start-1900-01-01-geo.json`, das Spielprotokoll des Starts in `exports/tf3-spielprotokoll-2026-10-27-erlenmark.txt`. Spielstand: `Erlenmark.sav` (05:37 Uhr); derselbe Stand liegt auch als `Erlental.sav` vor (05:38 Uhr). Beide Dateien tragen dieselbe Weltkennung; welche weitergeführt wird, steht in `werkstatt/erlenmark/STAND.md`.

`WEBSITE_AKTUALISIEREN.bat` lädt die Erlenmark mit hoch (Eintrag in `data/monitor-sources.json`, ohne Zeitung, `manifest_key: monitor_data`). Die Chronik selbst bleibt Handarbeit. Einzeln: `WEBSITE_AKTUALISIEREN.bat --save erlenmark`. Hochladen nur mit Freigabe des Spielers.

Ein Faktenblatt-Skript wie `scripts/falkenmark-fakten.py` gibt es für die Erlenmark noch nicht; es kommt mit dem ersten Kapitel (Aufgabe auf der Tafel).
