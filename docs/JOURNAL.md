# Le Journal des Alizés

Die Zeitung `saves/archipel-des-alizes/journal.html` ist die Startseite der Welt. Sie erscheint in monatlichen Ausgaben: Jeder Spielmonat mit Meldungen, Notizen oder Geschichten ist eine eigene Ausgabe. Belegtes, Spielervorgaben und Erfundenes bleiben überall gekennzeichnet.

| Rubrik | Inhalt | Quelle |
|---|---|---|
| Titelseite | Leitartikel der Ausgabe, Meldungen, Notizen des Direktors, Zahlen, Réclame, Gesichter des Monats, „Stoff für Geschichten“ | alles unten |
| Meldungen | Ereignisse aus den Messbüchern, filterbar nach Rubrik, Jahr und Suche | `meldungen.json` (automatisch) |
| Menschen | Beobachtungsgruppe des Monitors mit Verkehrsmitteln je Jahr, Arbeitsplatz, Zufriedenheitsrohwert und Lebensmomenten | `menschen.json` (automatisch) |
| Städte | Ortsakten aller Städte mit Einwohnerverlauf, Waren, Linien und Betrieben | `staedte.json` (automatisch) |
| Karte | Seekarte des Archipels: Städte nach Einwohnern, Linien nach Art, Betriebe nach Status, Zeitreise, Waren unterwegs (ab Monitor-Revision 16) | `karte.json` (automatisch, nur mit Positionsdaten) |
| Fuhrpark | Fahrzeuge je Art, Modelle je Art (ab Monitor-Revision 15), Premieren, größte Flotten, Kasse | `fuhrpark.json` (automatisch) |
| Geschichten | Artikel, Gespräche, Porträts, Réclame, „Am Tresen“ | `redaktion.json` (von Hand), `gazette.json` |
| Notizbuch | „Aus dem Notizbuch des Direktors“: Absichten und Erklärungen des Spielers, nach Monaten | `notizen.json` (aus dem Spielmonitor) |

Alle Dateien liegen in `saves/archipel-des-alizes/data/journal/`.

## Automatische Daten

`scripts/build-journal.py` liest die Detailmessungen aus `../Spielmonitor/sessions/*/daten.jsonl` (archivierte Sitzungen: `daten.jsonl.xz`, gleiche Bytes) und schreibt die vier automatischen Dateien, dazu `notizen.json` aus dem Notizbuch (siehe unten). Es läuft bei jedem Upload über `WEBSITE_AKTUALISIEREN.bat` bzw. `publish-monitor.py` mit. Neue Ereignisse erscheinen also ohne weiteres Zutun in der nächsten Ausgabe.

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
- **Fahrzeugarten:** Sie stammen aus dem Linienpräfix (Bus, RC = Lkw, Tram, TP = Personenzug, TC = Güterzug, WP = Passagierschiff, WC = Frachtschiff, AP = Flugzeug, AC = Frachtflugzeug) bzw. dem Verkehrsträger (ROAD = Bus, TRAM = Straßenbahn, RAIL = Personenzug, WATER = Frachtschiff, AIR = Flugzeug). Ohne beides bleibt die Art „unbekannt“, etwa bei vorläufigen Linien („Linie 1“); sie bekommt nie eine Premiere. Eine **Premiere** braucht ein Fahrzeug: Wird eine Linie einer neuen Art ohne Fahrzeug angelegt (die erste Fluglinie am 10.06.1920, der Verkehrsträger fehlt dann noch), ist sie zunächst nur „Neue Linie“; die Premiere folgt mit der ersten Messung, in der ein Fahrzeug dieser Art fährt (Flugzeug: 14.06.1920). Das gilt auch für die Premierenliste in `fuhrpark.json`.
- **Fahrzeugmodelle:** Ab Spielmonitor-Revision 15 tragen Detailmessungen je Linie `vehicle_models` (Spielname, Ressourcendatei, Fahrzeuge, Teile, Kaufdaten). Kennung ist die Ressourcendatei, sonst `id:<Modell-ID>`. Die erste Messung mit Modelldaten ist der Ausgangsbestand: Ihre Modelle gelten als „bei Beginn der Modellerfassung“ vorhanden und werden nicht gemeldet. Jedes später erstmals gesehene Modell wird einmal als „Neues Fahrzeugmodell“ gemeldet, mit Linie, Fahrzeug-/Teilezahl und erstem Kaufdatum laut Spiel. War der Ausgangsbestand unvollständig, zählt nur ein Kauf nach ihm als neu. Die Art eines Modells ist die Art der Linie, auf der es fährt; Fahrzeuge im Depot ohne Linie sind nicht erfasst. Ohne Modelldaten bleibt `fuhrpark.json` wie bisher (kein Feld `modelle`, Hinweis „bisher nicht“).
- **Beobachtungsgruppe:** Die Namen sind deterministisch aus der Personen-ID erfunden und stets als erfunden markiert. Wohnort, Verkehrsmittel, Arbeitsplatz und Zufriedenheitsrohwert (Skala nicht validiert) sind gemessen.
- **Cache:** Er liegt in `.publish-cache/journal/` und wird bei jeder Änderung am Script verworfen.

Von Hand: `python scripts/build-journal.py [--monitor PFAD] [--out ORDNER] [--notebook DATEI]` (`--out` schreibt woandershin, z. B. für Tests; `--notebook` liest ein anderes Notizbuch).

## Seekarte „Carte marine de l’Archipel“

Die Rubrik „Karte“ (hinter „Städte“) zeichnet den Archipel als SVG-Seekarte im Papier-Design: Städte als Kreise nach Einwohnern, Linien in der Farbe ihrer Art (Schiffslinien gestrichelt, Fluglinien gepunktet), Betriebe als Rauten nach Status (produziert, steht still, wird geprüft), Halte, Wahrzeichen und auf Wunsch „Waren unterwegs“. Klick auf ein Objekt zeigt Einzelheiten (Haltefolge einer Linie, Linien an einem Halt, Erzeugnisse eines Betriebs, Link zur Ortsakte); die Ortsakte verlinkt zurück („Auf der Seekarte zeigen“, `#karte/town-<id>`). Zoom über Knöpfe oder Doppelklick, Verschieben per Ziehen im vergrößerten Zustand.

- **Quelle:** `karte.json`, geschrieben von `build-journal.py` mit `scripts/journal_karte.py`, sobald Detailmessungen den Block `geo` tragen (Spielmonitor-Revision 16, `Spielmonitor/CHANGELOG_MOD16.md`). Ohne Positionsdaten entsteht keine Datei, die Rubrik fehlt und alle anderen Dateien bleiben byte-identisch (Test).
- **Positionen:** Mittelpunkt der Begrenzungsbox wie in den Stadt- und Industriefenstern des Spiels, in Weltmetern. Je Objekt gilt die neueste Messung; ältere Sitzungen füllen nur Objekte auf, die der neueste Stand nicht kennt. `fehlend` zählt Orte, Betriebe, Halte und Wahrzeichen ohne Position.
- **Linien:** Luftlinie zwischen den Halten in Haltefolge (`station_group_ids` jeder Detailmessung), als Rundkurs geschlossen. Kein Gleis- oder Straßenverlauf.
- **Küsten und Tiefen:** grobes Höhenraster `terrain` (etwa stündlich gemessen) relativ zum Wasserspiegel; die Seite zieht daraus Küstenlinie (0 m), Flachwasser bis 5 m, Isobathe 20 m und Höhenlinien. Fehlt das Raster, bleibt die Karte offenes Meer mit Symbolen.
- **Zeitreise:** Einwohner je Spielmonat aus `staedte.json`; Linien und Betriebe erscheinen ab ihrer ersten Meldung (`linie`/`premiere` bzw. `industrie`). Eingestellte Linien und geschlossene Betriebe fehlen, weil die Karte nur den letzten Stand verortet. Ein gestrichelter Ring zeigt die heutige Größe.
- **Waren unterwegs:** Stichprobe der Ladung an Bord aus der letzten Detailmessung (`logistics.cargo`, höchstens 240 Stücke): vom erzeugenden Betrieb zum Halt, an dem sie das Fahrzeug verlässt, mit der Linienkette der Reise. Nur beim heutigen Stand sichtbar, keine vollständige Verkehrsstatistik.
- **Nordrichtung:** „Welt-y wächst nach Norden“ (`y_nach_oben` in `karte.json`), vom Spieler am 14.10.2026 mit der Spielkarte abgeglichen (`nord_geprueft: true`); Kompass und Fußnote sagen das. Für eine neue Welt erneut prüfen und in `journal_karte.py` umstellen (`Y_NACH_OBEN`, `NORD_GEPRUEFT`); ohne Abgleich nennt die Seite die Nordrichtung eine Annahme.
- **Gestaltung:** Illustrierte Kartenbeilage (Pergamentrahmen, Kartusche, Kompass, gedeckte Stichfarben je Linienart). Die Rahmenbreite richtet sich nach der Fensterhöhe, damit der ganze Archipel auf einen Bildschirm passt; Kopf und Fuß des Rahmens passen sich per Container-Query an seine Breite an. Die Kopfzeile trägt wie jede gemessene Rubrik „Belegt“.

## Notizbuch des Direktors

Der Spieler, Direktor der Société, notiert beim Spielen im Spielmonitor kurze Absichten und Erklärungen (Zeile „Notizbuch“, Strg+N; Bedienung in `Spielmonitor/README.md`). Beispiel: „Lärmschutzwände in Valmorin gebaut, dafür Häuser abgerissen“. Bisher kamen solche Erklärungen per Chat, jetzt stehen sie mit Spieldatum im Notizbuch.

- **Quelle:** `Spielmonitor/history/notizbuch.jsonl`. `build-journal.py` übernimmt Notizen mit der `world_id` dieser Welt und gültigem Spieldatum, die im Monitor für die Zeitung freigegeben sind (`public` nicht `false`), unverändert nach `notizen.json`: `id`, `date` (Spieldatum der letzten Messung beim Schreiben), `game_time`, `text`. Reihenfolge nach Spielzeit. Die Datei hat keinen Messstand und ändert sich nur, wenn sich Notizen ändern; der Upload-Commit sagt dann „Notizbuch aktualisiert“.
- **Anzeige:** Auf der Titelseite ihres Monats im Kasten „Aus dem Notizbuch des Direktors“, unter „Notizbuch“ alle Notizen nach Monaten. Die ersten zwei Notizen einer Ausgabe erscheinen auch als Frage unter „Stoff für Geschichten“.
- **Status:** Notizen sind **Spielervorgabe**, kein Messwert. Der Monitor misst weder Absicht noch Ursache. Eine Notiz erklärt, was der Spieler wollte oder tat; ob die Daten dazu passen, sagt erst der Abgleich mit den Messungen.
- **Bearbeiten und Löschen** nur im Monitor. Nach dem nächsten Upload ist die Zeitung auf dem Stand des Notizbuchs. Wird ein früherer Spielstand geladen, bleiben Notizen stehen; Rücksprünge erwähnt die Zeitung weiterhin nicht.

**Zitieren in Redaktionsbeiträgen:** `refs.notizen` mit den IDs aus `notizen.json` und im `grounding` ausdrücklich „Spielervorgabe“ nennen, etwa „Spielervorgabe (Notizbuch des Direktors, 5. April 1913): …“. Der Beitrag zeigt die zitierte Notiz dann unter dem Datenbezug, die Notiz verlinkt zurück auf den Beitrag. Der Validator verlangt „Spielervorgabe“ im `grounding`. Fehlt eine zitierte Notiz, weil der Spieler sie gelöscht oder nicht freigegeben hat, gibt er nur einen Hinweis aus und blockiert keinen Upload.

## Geschichten schreiben

Neue Beiträge kommen als Eintrag in `redaktion.json` hinzu. Pflicht für jeden Beitrag:

- `id` (eindeutig), `typ` (`artikel`, `interview`, `portraet`, `anzeige`, `einordnung`), `art` (`fiktion` oder `einordnung`), `date` als Spielmonat `JJJJ-MM`, `rubrik`, `titel`, optional `teaser`.
- Inhalt je Typ: `body` (Liste von Absätzen); Interviews `partner` {`name`, `rolle`, optional `person`} und `fragen` [{`frage`, `antwort`}]; Anzeigen `anzeige` {`kopf`, `zeilen`, `fuss`}.
- `grounding`: welche Werte gemessen sind und **was erfunden ist** (Fiktion muss „erfunden“ enthalten). Nur behaupten, was die Daten hergeben; Ursachen, Einheiten und Antriebsarten sind meist nicht gemessen.
- `refs`: `personen` und `staedte` (IDs aus `menschen.json` und `staedte.json`), dazu `linien` und `betriebe`, optional `notizen` (IDs aus `notizen.json`, siehe „Notizbuch des Direktors“). Verweise erzeugen Links zwischen Geschichte, Person, Ortsakte und Notiz.
- **Kein Stoff für Geschichten:** das Laden früherer Spielstände, Spielzeit-Rücksprünge und verworfene Zeitlinien (Wunsch des Spielers). Sie erscheinen auch nicht als Meldung; sichtbar bleiben sie nur im Monitor.
- `lead: true` macht einen Artikel zum Aufmacher seiner Ausgabe (höchstens einer je Monat). Ohne Aufmacher baut die Titelseite ihren Kopf aus der wichtigsten Meldung.

**Alltag, Orte, Figuren (Wunsch des Spielers, Oktober 2026):**

- **Fortsetzen statt neu erfinden:** Wiederkehrende Figuren, Wirtshäuser, Ortsrivalitäten und kleine Fortsetzungen weiterführen (Kleiderwette in Valmorin, Honorines Wettbuch …). Menschen erinnern sich, erzählen dasselbe Ereignis unterschiedlich und kommen auf frühere Stücke zurück.
- **Eigene Alltagsanlässe:** Neben Geschichten aus Fahrzeugen, Waren und Lieferproblemen gelegentlich ein Anlass aus dem Leben: ein Sonntag am Meer, ein Markttag, ein Familienbesuch, ein Nachbarschaftsstreit, ein Fest, ein Abend nach der Arbeit. Verkehr und Wirtschaft laufen dann im Hintergrund mit.
- **Orte mit Charakter:** konkrete Szenen zeigen, wie man dort wohnt, miteinander umgeht, sich erholt und die Umgebung wahrnimmt. Fortschritt wird unterschiedlich erlebt, als Hoffnung, Erleichterung, Überforderung oder als Gefühl, übersehen zu werden. Kein Ort und keine Figur bekommt nur eine feste Eigenschaft.
- **Ziel:** Leser sollen sich vorstellen können, wie sich ein gewöhnlicher Tag dort anfühlt, und wissen wollen, was aus den Menschen wird.

**Unmittelbar erzählen, sauber trennen:**

- **Keine Fiktions-Metasprache im Text:** Formeln wie „in unserer erfundenen Szene“, „unser fiktiver Gesprächspartner“, „(erfundene Figur)“ oder „in unserer Erzählung“ gehören nicht in `titel`, `teaser`, `body`, `partner`, `fragen` oder `anzeige`. Die Kennzeichnung steht nur am Beitrag (`art: fiktion`, Etikett „Fiktion“) und im `grounding`, das weiter genau nennt, was erfunden ist. Die Stimme der Zeitung bleibt erlaubt, wo sie Gemessenes von Vermutetem trennt („Was er arbeitet, verraten die Bücher nicht. Die Redaktion stellt sich vor …“, „Nachbemerkung der Redaktion“). Der Validator gibt für solche Formeln in Fiktion einen Hinweis aus.
- **Erfundenes ist nie Beleg:** Ereignisse, Figuren, Gespräche und Zahlen aus früheren Geschichten werden später nicht als Spieldaten behandelt, im `grounding` nicht als gemessen geführt und nie als Ursache eines Messwerts genannt. Rückbezüge greifen die Erzählung auf (eine Figur erinnert sich an die Wette), Fakten kommen weiter nur aus den Messungen.

Ideen liefert die Zeitung selbst. Der Kasten „Stoff für Geschichten“ auf jeder Titelseite und „Noch unerzählt“ unter Geschichten leiten offene Fragen aus den Meldungen ab.

**Orte und Figuren (Stand Oktober 1921; erfunden, soweit nicht aus der Beobachtungsgruppe):**

- Valmorin: „Au Quai des Collines“ mit Wirt Mathurin und seiner Frau (gewann 1913 die Kleiderwette), der alte Anselme (setzt aus Prinzip auf „nie“, 1921 kurz „vielleicht“), Lucie vom Bahnhof (zählt Hemden seit 1910, setzt „Weihnachten, für Isidore“), Maurermeister Barnabé Lacroix; Kreidefragen an der Lärmschutzwand, zuletzt „Wann Stufe zwei?“ zur Burg des weißen Reihers.
- Port des Alizés: Honorine („Chez Honorine“, Wettbuch, Ratgeber), Lokführer Hippolyte (Rosemond), Inspecteur Lebrun, Automobil-Club des Alizés (sein Herr hat die Flugwette im Juli 1921 bezahlt), Familie Bonnaire.
- Anse Dorée: Madame Rosalie (Ansichtskarten, „Auf meinen Karten schon“), Pension „Les Jardins“ am Bahnhof mit Wirtin und Gästebuch, die letzten Postkutschen zum Domaine des Alizés.
- Vauclaire: Marthe (1921 siebzehn), ihr Bruder Paul (neun, Brettpferd vom Großvater, will Spielzeug nur „mit der Société“), der Großvater (sagt weiter „Sarrians“), Léonie Saint-Cyr mit ihrem Haushaltsbuch. Sin-le-Noble: Tante Clémentine (Rue des Jardins), „Café du Sablier“.
- Roquemer: Madame Odile (Fischhändlerin, Rue des Dames), der Stadtschreiber (Urkunde 1918, Meldescheine 1921), der Briefträger (Adressbuch 1919).
- Garches: der Pfarrer (Predigt 1920) und seine Haushälterin Mademoiselle Eulalie (Rezept 1921). Roche-Noire: der Wirt vom „Le Puits“. Fähre nach Montfougère: Kapitän und Fischer. Kartograf Aristide Vauquelin.
- Aus der Beobachtungsgruppe (Namen von der Redaktion vergeben; Wege, Wohnorte und Arbeitsplätze gemessen): Isidore Valère (45714, Garches bis April 1920, dann Fontenay-aux-Roses, jeder Weg zu Fuß) und Marceline Philogène (126758, Lamballe-Armor bis Januar 1920, dann La Mulatière) sind die letzten von 1904 und schreiben sich seit 1921 Briefe („Briefwechsel“). Augustin Valère (35081, Roquemer, seit März 1921, nicht verwandt), Delphine Gaspard (35840, Valmorin), Fernand Saint-Cyr (35558), Clovis Calixte (36283) und Amélie Modeste (35243, alle Vauclaire), Célestin Hilaire (94977) und Lucienne Sainte-Rose (36242, beide Anse Dorée), Narcisse Petit-Frère (35326, Garches). Nicht mehr dabei: Isidore Lubin (54586, seit April 1913), Marceline Clément (84185, seit 28.12.1918, „Poesiealbum“), Edmond Philogène (144145) und Désiré Séverin (90377, beide 1920, „Rede“). Zwischen 01.01. und 03.06.1920 sind 67 der seit 1904 Beobachteten ausgeschieden; die Neuen wohnen meist in angeschlossenen Orten, daher steigt der Anteil der Wege mit der Société ab 1920 durch die neue Besetzung, nicht durch Umsteigen. Gleiche Nachnamen sind Zufall der Namensvergabe.

**Offene Fäden (Stand Oktober 1921):**

- Spielzeug: Sin-le-Noble seit 01.11.1920 versorgt (Februar 1921 33 von 94, Oktober 55 von 106); Vauclaire (152), Roquemer (269) und Roche-Noire (206) weiter 0, keine Linie mit Toys hält dort. Kette Tournus – Schiff Sin–Tou (Toys ab 17.04.1920) – Lastwagen in Sin-le-Noble; Cassis Toy Factory und Cassis Sägewerk ohne Produktion.
- Wettbuch von Chez Honorine: offen sind Wette 4 (Honorine fliegt erst, wenn das erste Spielzeug in Vauclaire ankommt) und die Dauerwette Rum in Bourg.
- Rum: Port des Alizés 102 (Februar 1921), 58 (Juni), 89 von 251 (Oktober); Bourg-l’Écorce (456) und Pointe des Pêcheurs (209) weiter 0.
- Valmorin: Burg des weißen Reihers seit 23.03.1921 auf Stufe 1 von 4, bis Oktober unverändert; in derselben Woche Stein auf drei Linien (Lkw am Steinbruch Port, zwei Güterzüge, einer bis Valmorin Ost), Zweck nicht gemessen. Werkzeuge 0 von rund 157, obwohl die Raddampfer aus Rambervillers zeitweise über 200 an Bord haben. Kleidung 15 (Februar 1921) bis 55 (August), Oktober 45 von 145. 1.500 Einwohner seit 28.04.1921, an der Wand nicht angeschrieben.
- Garches: weiter 399 und 0 % Netz. Fleisch-Lkw RC Passagiere,Fleisch-Gar-LO-1 seit 10.08.1921, erstes Fleisch im Laden am 02.10.1921 (12 von 129, die erste je in Garches gedeckte Ware); Wolle (45 im Jahr) ohne Linie, Bretter 0 von 128; Viehzuchtbetrieb Nord seit 10.08.1921 fort.
- Vauclaire: in der Beobachtungsgruppe 1921 viele ohne Arbeit (Clovis Calixte seit 09.01.1921, im Oktober weiter ohne); Bretter seit 02.09.1921 1 von 140, Maschinen 0 von 70; Dünger-Lkw zum Sarrians Bauernhof seit 04.07.1921.
- Anse Dorée: Zucker 0 von 351 in jeder Messung 1921, Kleidung rund 25 von 175, während vom Bahnhof Anse Dorée Kleidung nach Valmorin fährt.
- Valombre wächst (621 im Oktober 1921), Konserven seit Mai und Werkzeuge seit Oktober 0, Netzanteil 57 % → 45 %. Roquemer 818 im Oktober 1921.
- Flugzeug: 8 Junkers F 13 seit 02.04.1921, bis 26 von 32 Plätzen (07.07.1921).
- Noch unerzählt: Nyons bekommt am 17.05.1921 seinen ersten Bus (zum Holzfällerlager, Netzanteil 3 %); Péronne (Eisenerz geschlossen 06.03., Kohle 06.04., Holzfäller 19.08.1921; Germaine Nicolas erstes Auto 06.10.1921); Lardy (Eisenerzbergwerk 21.05., Stahlwerk Nord 04.07.1921, Fahrzeugfabrik still); Port des Alizés (Möbelfabrik 17.02.1921, Bauernhof geschlossen 07.07. und neu 06.10.1921); Schiff Pointe – Garches mit Konserven und Möbeln (28.04.1921); 1.100 Fahrzeuge und 200 Linien (17.05.1921).

**Erledigt:** Valmorin 1.000, Eiffelturm, erste Möbel (Aug. 1915), Konserven Valmorin (Mai 1916), Maschinen Valmorin (Dez. 1916), erster Zucker auf Roche-Noire (23.06.1917), Roche-Noire 1.000 (18.05.1916), Nordrichtung, Rum in Port (Fall Lebrun abgeschlossen, April 1918), erste Milliarde in der Kasse (13.12.1918), Decksitzwagen statt Postbus (ab Januar 1919), Zuckermühle Montceau-les-Mines produziert (seit 11.12.1919), erstes Spielzeug (Dez. 1919, „Bauanleitung“) und erste Ankunft (Nov. 1920, „Märchen“), Melle → Valombre (Januar 1920, „Taufanzeige“), 1.000 Fahrzeuge (22.03.1920, „Inventur“), AEG-Triebwagen durch Nürnberg F ersetzt (Januar bis Mai 1920), erster Fluggast (16.09.1920, „Wettbuch“), Valombre zieht mit Garches gleich (03.09.1920, „Sportbericht“), erstes Fleisch im Garcher Stall (Dez. 1920, „Predigt“), Krokodil statt Atlantic auf der Blech-/Stahlstrecke (13.01.1921, „Steckbrief“), Roquemer 750 (24.04.1921, „Meldeschein“), Valmorin 1.500 (28.04.1921, „Einkaufszettel“), Flugwette des Automobil-Clubs (Juli 1921, „Gästebuch“), erstes Fleisch in den Läden von Garches (02.10.1921, „Rezept“). Umbenennungen: Sarrians → Vauclaire (28.11.1915, Schulaufsatz; Straßenbahnhalt und Bauernhof heißen weiter „Sarrians“), La Talaudière → Roquemer (03.01.1918, Grundsteinurkunde), Melle → Valombre (Januar 1920, Taufanzeige; Bahnhof heißt weiter „Melle Station West“, Brennerei „Melle Rum Distillery“).

**Formen abwechseln (Wunsch des Spielers):** Eine Ausgabe soll nicht aus lauter gleichen Stücken bestehen, und dieselbe Form nicht mehrmals hintereinander. Bisher genutzt: Artikel, Aufmacher, Interview/Gespräch, Porträt, Réclame, „Am Tresen“, Leserbriefe, Nachrufe, Almanach (Einordnung), Amtliche Bekanntmachung, Momentaufnahme, Unterwegs (Reise einer Ware), Bildreportage, Logbuch, Reisebericht, Versteigerung, Tagebuch, „On dit …“ (Klatsch aus mehreren Lokalen), Kleinanzeigen, Telegramm, Festprogramm, Offener Brief, Lieferschein, Ich-Erzählung eines Gegenstands („Ich, die Wand“), Glückwünsche, Schiffsmeldungen, Bühnenstück, Fragebogen (eine Stadt antwortet), Schulaufsatz, Ratgeber („Fragen Sie Honorine“), Marktbericht (Einordnung), Postkarte, Speisekarte, Fahrplan-Aushang, Kalenderblatt, Reiseführer-Eintrag, Gedicht/Ballade, Vereinsnachrichten, Kriminalfall, Vermischtes, Urkunde (Grundstein), Polizeiakte (Abschlussbericht), Sitzungsprotokoll, Poesiealbum, Fahrgastordnung, Adressbuch, Rätselecke, Wunschzettel, Bauanleitung, Taufanzeige, Inventur, Rede, Wettbuch, Sportbericht (mit Tabelle), Märchen, Predigt, Steckbrief, Umfrage, Meldeschein, Briefwechsel, Bilderbogen, Einkaufszettel, Gästebuch, Haushaltsbuch, Rezept. Neue Formen sind willkommen; `rubrik` ist frei wählbar. Familien- und Gemeindeanzeigen als `typ: artikel` anlegen, denn `typ: anzeige` erscheint als „Réclame“.

Prüfen: `node scripts/validate-journal.mjs [ORDNER]` (läuft auch in CI und vor jedem Upload). `python scripts/test-build-journal.py` baut synthetische Messungen mit und ohne Modelldaten bzw. Positionen, eine erst später bestückte Fluglinie sowie ein Test-Notizbuch in einen Temp-Ordner und prüft Meldungen, Fuhrpark, Notizen, Seekarte und Validator (CI).

## Bildreportagen

Optionales Feld `image` pro Redaktionsbeitrag: `{src, alt, caption, source}`. `src` verweist relativ zur Zeitung auf `../../assets/photos/<name>.webp`. Nur lokale WebP-Dateien in diesem Verzeichnis werden eingebunden. Vorschau und Vollartikel zeigen das vollständige Bild; Anklicken öffnet die Großansicht. `alt` beschreibt das Motiv, `caption` nennt die Bearbeitung und `source` die ursprüngliche Aufnahme. Fotos werden erst nach Freigabe des Spielers veröffentlicht; das redaktionelle Ausgabedatum ist nicht automatisch das Aufnahmedatum im Spiel.
