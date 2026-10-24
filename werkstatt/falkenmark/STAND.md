# Falkenmark · Stand der Chronik

Zuletzt nachgezogen: 24.10.2026, Claude.

## Erzählt

| Kapitel | Titel | Zeitraum | `data-year` |
|---|---|---|---|
| I | Die Anfänge | 1. Januar bis 1. Juli 1900 | 1900 |
| II | Über das Wasser | Juli bis Dezember 1900 | 1900 |
| III | Treibstoff für Lindendorf | Januar bis Juni 1901 | 1901 |
| IV | Das zweite Öl | Juli bis Dezember 1901 | 1901 |

- Erzählt bis **31.12.1901**. Jahresbilanzen unter VII für 1900 und 1901.
- Register `saves/falkenmark/data/events.json`: 33 Einträge, letzter `jahresende-1901`.
- **Nächste freie Quelle: Q7.** Vergeben: Q1 Einstellungsseite, Q2 Angaben des Spielers, Q3 Spielprotokoll, Q4 Spielmonitor, Q5 Bestätigung „Falkenried“ mit Screenshot (Vorlage des KI-Bildes in Kapitel I), Q6 Screenshot Lindendorf (Vorlage des Bildes in Kapitel III).

## Daten

- Spielmonitor lokal: Messungen bis **30.1.1902** (Sitzung `20261024_093700_921135`).
- Im Repo (`saves/falkenmark/data/monitor/`): Export vom 24.10.2026, 08:15, 382 Messungen. Neuere Messungen kommen erst mit `WEBSITE_AKTUALISIEREN.bat` dazu.
- Faktenblätter: `fakten/1900.md`, `fakten/1901.md`, `fakten/1902.md` (nur Januar 1902).
- Für Kapitel V liegen bereit: zwei neue Linien am 4.1.1902 in Falkenried, ein Kanadischer Kutter (`WC Passagiere,Werkzeuge,Fisch-Fal-LO-1`) und vier Pferdefuhrwerke (`RC Fisch,Ziegel-Fal-LO-1`), beide mit zwei Halten in Falkenried; neu gemessen die Hinteralmhafen Ölplattform Süd. Mehr erst, wenn der Spieler weitergespielt hat.

## Namen

Bestätigt vom Spieler: Falkenried (vorher Ostheim, vom Spieler umbenannt), Falkenrieder Transportgesellschaft · FTG mit Sitz in Falkenried, das Haus am Ende der Allee ist der Firmensitz. Die übrigen Orts- und Betriebsnamen stammen aus dem Spiel (Mod Organic Towns). Flüsse, Seen und Höhenzüge haben noch keine Namen.

## Bilder

| Datei | Kapitel | Art |
|---|---|---|
| `saves/falkenmark/images/falkenried-gruendung-1900.jpg` | I | KI-Bild nach einem Screenshot im Spiel (Q5) |
| `saves/falkenmark/images/lindendorf-um-1901.jpg` | III | Bild nach einem Screenshot, Datierung vom Spieler auf 1901 geschätzt (Q6) |

## Fallstricke

- Werte „pro Jahr“ (Produktion, Versand, Linienbilanz) umfassen ein Wirtschaftsjahr des Spiels, hier rund 91 Kalendertage, also etwa ein Quartal. Die Faktenblätter nennen jeweils den Zeitraum. Korrigiert am 24.10.2026.
- Finanztabelle: Kalenderquartale, echte Jahressummen.
- Einwohner = belegte Wohnungen (`housing_occupied`). In der Falkenmark bisher immer gleich der Wohnkapazität.
- Leere Mehrzweck-Fuhrwerke meldet der Monitor mit dem Laderaum der ersten Ware (oft Getreide). Das ist keine Fehleinstellung.
- Die Personen-Stichprobe des Monitors ist für die Falkenmark unplausibel; nicht verwenden.
- Rücksprünge der Spielzeit (Neuladen) stehen im Faktenblatt. Geladene Stände sind kein Erzählstoff.
- Verläufe von Strecken sind nicht gemessen, nur Halte. Aus der Kartenvorschau keine Richtungen oder Verbindungen ableiten.
