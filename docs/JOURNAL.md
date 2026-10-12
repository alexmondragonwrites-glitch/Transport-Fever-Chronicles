# Le Journal des Alizés

Die Zeitung `saves/archipel-des-alizes/journal.html` ist die Startseite der Welt. Sie erscheint in monatlichen Ausgaben: Jeder Spielmonat mit Meldungen oder Geschichten ist eine eigene Ausgabe. Belegtes und Erfundenes bleiben überall gekennzeichnet.

| Rubrik | Inhalt | Quelle |
|---|---|---|
| Titelseite | Leitartikel der Ausgabe, Meldungen, Zahlen, Réclame, Gesichter des Monats, „Stoff für Geschichten“ | alles unten |
| Meldungen | Ereignisse aus den Messbüchern, filterbar nach Rubrik, Jahr und Suche | `meldungen.json` (automatisch) |
| Menschen | Beobachtungsgruppe des Monitors mit Verkehrsmitteln je Jahr, Arbeitsplatz, Zufriedenheitsrohwert und Lebensmomenten | `menschen.json` (automatisch) |
| Städte | Ortsakten aller Städte mit Einwohnerverlauf, Waren, Linien und Betrieben | `staedte.json` (automatisch) |
| Fuhrpark | Fahrzeuge je Art, Premieren, größte Flotten, Kasse | `fuhrpark.json` (automatisch) |
| Geschichten | Artikel, Gespräche, Porträts, Réclame, „Am Tresen“ | `redaktion.json` (von Hand), `gazette.json` |

Alle Dateien liegen in `saves/archipel-des-alizes/data/journal/`.

## Automatische Daten

`scripts/build-journal.py` liest die Detailmessungen aus `../Spielmonitor/sessions/*/daten.jsonl` und schreibt die vier automatischen Dateien. Es läuft bei jedem Upload über `WEBSITE_AKTUALISIEREN.bat` bzw. `publish-monitor.py` mit. Neue Ereignisse erscheinen also ohne weiteres Zutun in der nächsten Ausgabe.

Regeln:

- **Kanonischer Verlauf:** Nach einem Spielzeit-Rücksprung gilt der neu gespielte Verlauf, Messungen der verworfenen Zeitlinie zählen nicht. Der Rücksprung selbst erscheint als Meldung.
- **Erkannte Ereignisse:**
  - neue, geänderte und eingestellte Linien
  - Premieren je Fahrzeugart
  - Flottenänderungen ab ±3 Fahrzeugen
  - Neugründungen, Schließungen und Ausbaustufen von Betrieben
  - Einwohnerschwellen und Umbenennungen von Städten
  - Netz-Meilensteine (je 10 Linien, je 50 Fahrzeuge)
- **Bestätigung:** Schließungen brauchen drei aufeinanderfolgende Messungen ohne das Objekt, Einwohnerschwellen zwei Stadtstände.
- **Unscharfe Zeitpunkte:** Liegt vor einer Meldung eine Aufzeichnungslücke von mehr als 31 Tagen, nennt sie den Zeitraum (`fruehestens`) statt eines Tages.
- **Fahrzeugarten:** Sie stammen aus dem Linienpräfix (Bus, RC = Lkw, Tram, TP = Personenzug, TC = Güterzug, WP = Passagierschiff, WC = Frachtschiff) bzw. dem Verkehrsträger. Modellnamen erfasst der Monitor noch nicht.
- **Beobachtungsgruppe:** Die Namen sind deterministisch aus der Personen-ID erfunden und stets als erfunden markiert. Wohnort, Verkehrsmittel, Arbeitsplatz und Zufriedenheitsrohwert (Skala nicht validiert) sind gemessen.
- **Cache:** Er liegt in `.publish-cache/journal/` und wird bei jeder Änderung am Script verworfen.

Von Hand: `python scripts/build-journal.py [--monitor PFAD]`.

## Geschichten schreiben

Neue Beiträge kommen als Eintrag in `redaktion.json` hinzu. Pflicht für jeden Beitrag:

- `id` (eindeutig), `typ` (`artikel`, `interview`, `portraet`, `anzeige`, `einordnung`), `art` (`fiktion` oder `einordnung`), `date` als Spielmonat `JJJJ-MM`, `rubrik`, `titel`, optional `teaser`.
- Inhalt je Typ: `body` (Liste von Absätzen); Interviews `partner` {`name`, `rolle`, optional `person`} und `fragen` [{`frage`, `antwort`}]; Anzeigen `anzeige` {`kopf`, `zeilen`, `fuss`}.
- `grounding`: welche Werte gemessen sind und **was erfunden ist** (Fiktion muss „erfunden“ enthalten). Nur behaupten, was die Daten hergeben; Ursachen, Einheiten und Antriebsarten sind meist nicht gemessen.
- `refs`: `personen` und `staedte` (IDs aus `menschen.json` und `staedte.json`), dazu `linien` und `betriebe`. Verweise erzeugen Links zwischen Geschichte, Person und Ortsakte.
- `lead: true` macht einen Artikel zum Aufmacher seiner Ausgabe (höchstens einer je Monat). Ohne Aufmacher baut die Titelseite ihren Kopf aus der wichtigsten Meldung.

Ideen liefert die Zeitung selbst. Der Kasten „Stoff für Geschichten“ auf jeder Titelseite und „Noch unerzählt“ unter Geschichten leiten offene Fragen aus den Meldungen ab. Wiederkehrende Figuren: Wirt Mathurin vom „Au Quai des Collines“ (Valmorin), der alte Anselme, Lucie vom Bahnhof; aus der Beobachtungsgruppe Marceline Clément (84185), Isidore Lubin (54586), Edmond Philogène (144145).

Prüfen: `node scripts/validate-journal.mjs` (läuft auch in CI und vor jedem Upload).
