# Le Journal des Alizés

Die Zeitung `saves/archipel-des-alizes/journal.html` ist die Startseite der Welt. Sie erscheint in monatlichen Ausgaben: Jeder Spielmonat mit Meldungen oder Geschichten ist eine eigene Ausgabe. Belegtes und Erfundenes bleiben überall gekennzeichnet.

| Rubrik | Inhalt | Quelle |
|---|---|---|
| Titelseite | Leitartikel der Ausgabe, Meldungen, Zahlen, Réclame, Gesichter des Monats, „Stoff für Geschichten“ | alles unten |
| Meldungen | Ereignisse aus den Messbüchern, filterbar nach Rubrik, Jahr und Suche | `meldungen.json` (automatisch) |
| Menschen | Beobachtungsgruppe des Monitors mit Verkehrsmitteln je Jahr, Arbeitsplatz, Zufriedenheitsrohwert und Lebensmomenten | `menschen.json` (automatisch) |
| Städte | Ortsakten aller Städte mit Einwohnerverlauf, Waren, Linien und Betrieben | `staedte.json` (automatisch) |
| Fuhrpark | Fahrzeuge je Art, Modelle je Art (ab Monitor-Revision 15), Premieren, größte Flotten, Kasse | `fuhrpark.json` (automatisch) |
| Geschichten | Artikel, Gespräche, Porträts, Réclame, „Am Tresen“ | `redaktion.json` (von Hand), `gazette.json` |

Alle Dateien liegen in `saves/archipel-des-alizes/data/journal/`.

## Automatische Daten

`scripts/build-journal.py` liest die Detailmessungen aus `../Spielmonitor/sessions/*/daten.jsonl` und schreibt die vier automatischen Dateien. Es läuft bei jedem Upload über `WEBSITE_AKTUALISIEREN.bat` bzw. `publish-monitor.py` mit. Neue Ereignisse erscheinen also ohne weiteres Zutun in der nächsten Ausgabe.

Regeln:

- **Kanonischer Verlauf:** Nach einem Spielzeit-Rücksprung gilt der neu gespielte Verlauf, Messungen der verworfenen Zeitlinie zählen nicht. Der Rücksprung selbst wird in der Zeitung nicht erwähnt (Wunsch des Spielers); er bleibt im Monitor sichtbar.
- **Erkannte Ereignisse:**
  - neue, geänderte und eingestellte Linien
  - Premieren je Fahrzeugart
  - neue Fahrzeugmodelle (`modell`, ab Monitor-Revision 15)
  - Flottenänderungen ab ±3 Fahrzeugen
  - Neugründungen, Schließungen und Ausbaustufen von Betrieben
  - Einwohnerschwellen und Umbenennungen von Städten
  - Netz-Meilensteine (je 10 Linien, je 50 Fahrzeuge)
- **Bestätigung:** Schließungen brauchen drei aufeinanderfolgende Messungen ohne das Objekt, Einwohnerschwellen zwei Stadtstände.
- **Unscharfe Zeitpunkte:** Liegt vor einer Meldung eine Aufzeichnungslücke von mehr als 31 Tagen, nennt sie den Zeitraum (`fruehestens`) statt eines Tages.
- **Fahrzeugarten:** Sie stammen aus dem Linienpräfix (Bus, RC = Lkw, Tram, TP = Personenzug, TC = Güterzug, WP = Passagierschiff, WC = Frachtschiff) bzw. dem Verkehrsträger.
- **Fahrzeugmodelle:** Ab Spielmonitor-Revision 15 tragen Detailmessungen je Linie `vehicle_models` (Spielname, Ressourcendatei, Fahrzeuge, Teile, Kaufdaten). Kennung ist die Ressourcendatei, sonst `id:<Modell-ID>`. Die erste Messung mit Modelldaten ist der Ausgangsbestand: Ihre Modelle gelten als „bei Beginn der Modellerfassung“ vorhanden und werden nicht gemeldet. Jedes später erstmals gesehene Modell wird einmal als „Neues Fahrzeugmodell“ gemeldet, mit Linie, Fahrzeug-/Teilezahl und erstem Kaufdatum laut Spiel. War der Ausgangsbestand unvollständig, zählt nur ein Kauf nach ihm als neu. Die Art eines Modells ist die Art der Linie, auf der es fährt; Fahrzeuge im Depot ohne Linie sind nicht erfasst. Ohne Modelldaten bleibt `fuhrpark.json` wie bisher (kein Feld `modelle`, Hinweis „bisher nicht“).
- **Beobachtungsgruppe:** Die Namen sind deterministisch aus der Personen-ID erfunden und stets als erfunden markiert. Wohnort, Verkehrsmittel, Arbeitsplatz und Zufriedenheitsrohwert (Skala nicht validiert) sind gemessen.
- **Cache:** Er liegt in `.publish-cache/journal/` und wird bei jeder Änderung am Script verworfen.

Von Hand: `python scripts/build-journal.py [--monitor PFAD] [--out ORDNER]` (`--out` schreibt woandershin, z. B. für Tests).

## Geschichten schreiben

Neue Beiträge kommen als Eintrag in `redaktion.json` hinzu. Pflicht für jeden Beitrag:

- `id` (eindeutig), `typ` (`artikel`, `interview`, `portraet`, `anzeige`, `einordnung`), `art` (`fiktion` oder `einordnung`), `date` als Spielmonat `JJJJ-MM`, `rubrik`, `titel`, optional `teaser`.
- Inhalt je Typ: `body` (Liste von Absätzen); Interviews `partner` {`name`, `rolle`, optional `person`} und `fragen` [{`frage`, `antwort`}]; Anzeigen `anzeige` {`kopf`, `zeilen`, `fuss`}.
- `grounding`: welche Werte gemessen sind und **was erfunden ist** (Fiktion muss „erfunden“ enthalten). Nur behaupten, was die Daten hergeben; Ursachen, Einheiten und Antriebsarten sind meist nicht gemessen.
- `refs`: `personen` und `staedte` (IDs aus `menschen.json` und `staedte.json`), dazu `linien` und `betriebe`. Verweise erzeugen Links zwischen Geschichte, Person und Ortsakte.
- **Kein Stoff für Geschichten:** das Laden früherer Spielstände, Spielzeit-Rücksprünge und verworfene Zeitlinien (Wunsch des Spielers). Sie erscheinen auch nicht als Meldung; sichtbar bleiben sie nur im Monitor.
- `lead: true` macht einen Artikel zum Aufmacher seiner Ausgabe (höchstens einer je Monat). Ohne Aufmacher baut die Titelseite ihren Kopf aus der wichtigsten Meldung.

Ideen liefert die Zeitung selbst. Der Kasten „Stoff für Geschichten“ auf jeder Titelseite und „Noch unerzählt“ unter Geschichten leiten offene Fragen aus den Meldungen ab. Wiederkehrende Figuren: Wirt Mathurin vom „Au Quai des Collines“ (Valmorin), der alte Anselme, Lucie vom Bahnhof; aus der Beobachtungsgruppe Marceline Clément (84185), Isidore Lubin (54586), Edmond Philogène (144145).

Prüfen: `node scripts/validate-journal.mjs [ORDNER]` (läuft auch in CI und vor jedem Upload). `python scripts/test-build-journal.py` baut synthetische Messungen mit und ohne Modelldaten in einen Temp-Ordner und prüft Meldungen, Fuhrpark und Validator (CI).

## Bildreportagen

Optionales Feld `image` pro Redaktionsbeitrag: `{src, alt, caption, source}`. `src` verweist relativ zur Zeitung auf `../../assets/photos/<name>.webp`. Nur lokale WebP-Dateien in diesem Verzeichnis werden eingebunden. Vorschau und Vollartikel zeigen das vollständige Bild; Anklicken öffnet die Großansicht. `alt` beschreibt das Motiv, `caption` nennt die Bearbeitung und `source` die ursprüngliche Aufnahme. Fotos werden erst nach Freigabe des Spielers veröffentlicht; das redaktionelle Ausgabedatum ist nicht automatisch das Aufnahmedatum im Spiel.
