# Falkenmark – Chronik eines Landes im Wandel

Zweite Welt im Archiv, angelegt am 24.10.2026. Wer gerade woran schreibt, wie weit erzählt ist und welche Messwerte bereitliegen: `werkstatt/` (Abstimmung zwischen Claude und Codex, siehe `werkstatt/README.md`). Eigenständiger TF3-Spielstand, Startjahr 1900, getrennt vom Archipel des Alizés: Orte, Unternehmen und Ereignisse von dort werden nicht übernommen.

## Wo was liegt

| Datei | Inhalt |
|---|---|
| `saves/falkenmark/chronik.html` | Die Chronik: Prolog, Steckbrief, Kapitel, Orte, Unternehmen, Auswertungen, offene Fragen, Quellen, Korrekturen. Handgeschrieben. |
| `saves/falkenmark/data/events.json` | Ereignisregister, einzige Quelle. `chronik.html` und die Datenansicht lesen es. |
| `saves/falkenmark/data/meta.json` | Kurzbeschreibung, Status, Monitor-Weltname. |
| `saves/falkenmark/data/manifest.json` | `latestReport: chronik.html`: Die Weltseite leitet dorthin weiter. |
| `saves/falkenmark/images/` | Bilder der Chronik, z. B. die KI-Ansicht „Falkenried · 1900“ nach einer Spielaufnahme. |
| `assets/falkenmark.css`, `assets/affiche-falkenmark.svg` | Eigenes Erscheinungsbild, unabhängig von `styles.css`: Leinenpapier mit Höhenlinien, Waldgrün, Schiefer, Ziegelrot, Grenzlinie (Strich-Punkt) statt Madras-Band, Source Serif 4 und Jost statt Playfair. Dazu das Zierbild (keine Karte). Die Falkenmark-Karte auf dem Portal hat passende Regeln in `styles.css` (`.world-card[data-world="falkenmark"]`). |

Die allgemeine Datenansicht (`index.html?view=archive`) ist noch auf das Archipel zugeschnitten (Wörter wie „Inseln“ im Atlas). Einstieg für die Falkenmark ist `chronik.html`.

## Kapitel anlegen

Jedes Kapitel ist ein `<article class="fm-chapter" id="kapitel-N" data-year="JJJJ">` in `#kapitel` und bekommt einen Eintrag in der Kapitelnavigation (`.fm-chapnav`). Reicht ein Kapitel über einen Jahreswechsel, stehen beide Jahre im Attribut (`data-year="1901 1902"`). Jede Jahresbilanz unter VII steht in `<div class="fm-yearblock" data-year="JJJJ">`.

**Jahresauswahl:** Die mitlaufende Leiste `#jahre` baut sich aus diesen Attributen selbst (Jahrzehnt wählen, dann das Jahr; Jahre ohne Kapitel ausgegraut). Ein Jahr zeigt nur dessen Kapitel, Registereinträge (Jahr aus `date` in `events.json`) und Jahresbilanz; Adresse `#jahr-1901`, alles: `#jahr-alle`. Ein Sprung zu einem ausgeblendeten Kapitel wählt dessen Jahr. Prolog, Steckbrief, Orte, Unternehmen, offene Fragen und Quellen bleiben jahresübergreifend. Wird die Seite irgendwann zu lang, lässt sie sich nach Jahrzehnten auf mehrere Seiten teilen; die Leiste bleibt dieselbe.

Aufbau eines Kapitels:

1. Kopf: `<h3><span class="fm-chapter-no">Kapitel N</span> Titel</h3>` und `<p class="fm-chapter-period">` mit dem Zeitraum.
2. Optional ein Bild (`figure.fm-founding`), bei KI-Bildern so gekennzeichnet.
3. Übersicht `.fm-overview`: Kennzahlen (`.fm-stat`, `--neg` für Verluste), Zeitachse (`ol.fm-timeline`, Schlüsselereignis mit `is-key`) und Linien-Schemata (`figure.fm-route`: `fm-stop`, `fm-leg`, `fm-leg--assumed` für nicht gemessene Verläufe, `fm-stop--ring` für Linien im Ort). Nur Zahlen und Daten, die wörtlich im Text oder im Register stehen.
4. Textblöcke: `div.fm-block.fm-block--belegt` (Dokumentkasten, Quelle als letzter Absatz `p.fm-source`), `div.fm-block.fm-block--abgeleitet` (Kommentar mit Akzentbalken), `div.fm-scene` (Pergament, Initiale, eingerückte Folgeabsätze).
5. Quellen als Badge: `<a class="fm-q" href="#q4" data-tip="…" aria-label="Quelle Q4: …">Q4</a>`; die Quellenliste hat die Anker `#q1`, `#q2` … (`li id="qN"`). Die nächste freie Nummer steht in `werkstatt/falkenmark/STAND.md`.

Schriften bleiben lokal (Source Serif 4, Jost) bzw. Systemschrift für Zahlen (`--fm-mono`); keine Google Fonts, kein Playfair (Archipel).

## Ereignisse eintragen

Jeder Eintrag in `events.json` braucht `id`, `date` (`JJJJ`, `JJJJ-MM` oder `JJJJ-MM-TT`, Spielzeit), `kind`, `category`, `title`, `description`, `source`. Zusätzlich hier:

- `game_time_label`: Spielzeit in Worten, wenn `date` allein missverständlich ist (z. B. „Startjahr 1900, vor Spielbeginn“).
- `recorded`: reales Datum des Screenshots oder Exports (`JJJJ-MM-TT`), `recorded_note` für Einschränkungen.
- `kind`: `fakt` = Belegt, `rekonstruktion` = Abgeleitet, `fiktion` = Literarische Szene.

Einträge nicht löschen. Falsche Angaben werden korrigiert und im Abschnitt „Korrekturen“ von `chronik.html` mit Datum und Grund vermerkt.

## Regeln aus dem Auftrag des Spielers

1. Belegtes, Abgeleitetes und Erfundenes trennen.
2. Keine Einwohnerzahlen, Finanzwerte, Produktionsmengen, Eröffnungsdaten oder Verbindungen erfinden. Fehlendes bleibt offen.
3. Fiktive Personen und Zitate nur in Passagen mit dem Etikett „Literarische Szene“.
4. Spieljahr und reales Aufnahmedatum immer getrennt.
5. Orts- und Unternehmensnamen erst nach Bestätigung des Spielers verbindlich.
6. Aus der kleinen Kartenvorschau keine Himmelsrichtungen, Fließrichtungen oder Verbindungen ableiten.
7. Widersprüche benennen und nachvollziehbar korrigieren.

Werte „pro Jahr“ aus dem Spiel (Produktion, Versand, Linienbilanz) umfassen ein Wirtschaftsjahr des Spiels, nicht das Kalenderjahr. Die Falkenmark läuft mit rund 16.000 Spielzeit-Einheiten je Kalendertag, ein Wirtschaftsjahr sind also rund 91 Tage. In der Chronik steht deshalb immer der Zeitraum dabei (Korrektur vom 24.10.2026). Die Finanztabelle rechnet nach Kalenderquartalen.

Politische Einordnung bleibt offen; reale historische Ereignisse gehören nicht automatisch zur Welt. Ton: ruhige Regionalgeschichte mit gelegentlichen Reportagen, kein Werbeton, auch Umwege und stillstehende Orte erzählen. Die Zukunft wird nicht vorweggenommen.

## Spielmonitor

Im Spielmonitor heißt die Welt „Falkenmark – 1900“ (angelegt und vorgewählt am 24.10.2026), Weltkennung `tf3-2026-10-24-1792815641-1925542896-2`, Spielstand `Falkenmark.sav`, Zufallswert `OKij0PeQLm`. Der Screenshot der Einstellungsseite zeigt eine früher erzeugte Karte, nicht diese Welt (Korrektur vom 24.10.2026 in `chronik.html`). Voraussetzungen: Mod „Spielmonitor – Live-Daten und Chronik“ im Spielstand aktiv, Monitor vor dem Laden mit dieser Welt gestartet, Spielstand nach dem ersten Laden gespeichert.

`WEBSITE_AKTUALISIEREN.bat` lädt die Falkenmark mit hoch (Eintrag in `data/monitor-sources.json`, ohne Zeitung). Ihre Messdaten liegen unter `saves/falkenmark/data/monitor/` und stehen im Manifest als `monitor_data`; die Archipel-Monitorseite wird für die Falkenmark bewusst nicht eingebunden. Die Chronik selbst (`chronik.html`, `events.json`) schreibt das Skript nicht, sie bleibt Handarbeit. Einzeln: `WEBSITE_AKTUALISIEREN.bat --save falkenmark`.
