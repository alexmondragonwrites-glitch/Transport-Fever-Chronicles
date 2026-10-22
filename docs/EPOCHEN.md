# Epochen: Die Zeitung altert mit dem Spiel

**Konzept abgestimmt, teilweise umgesetzt (18.10.2026):** Mechanik, Zustand `krisenpapier` und die Stufen 1 bis 5 sind gebaut (siehe „Umsetzung“). Die Stufen 6 bis 14 kommen jeweils kurz bevor das Spiel sie erreichen kann. Mit dem Spieler besprochen am 18.10.2026. Ziel ist, dass „Le Journal des Alizés“ so aussieht wie eine Zeitung ihrer Zeit: um 1905 anders als in den 1920ern, den 1940ern oder als Website der 1990er. Das Spiel soll bis 2050 oder länger laufen.

## Festgelegt

1. **Gang durchs Archiv:** Jede Ausgabe erscheint im Stil ihres Spielmonats. Wer zurückblättert, sieht die alten Ausgaben im alten Gewand.
2. **Schleichende Übergänge:** Es gibt keine festen Epochen-Blöcke, sondern einzelne **Merkmale** (Überschriftenschrift, Zeitungskopf, Bilder, Papier …), die zu unterschiedlichen Zeitpunkten wechseln. So verändert sich die Zeitung allmählich.
3. **Neue Rubriken mit Inhalt:** Rubriken wie Radio- oder Fernsehprogramm erscheinen erst, wenn ihre Zeit gekommen ist. Jede wird entweder **aus Messdaten** gefüllt (Belegt) oder **von Hand** (Fiktion), gekennzeichnet wie bisher.
4. **Ereignisse lösen aus, nicht der Kalender:** Jedes Merkmal wechselt, wenn in der Welt ein bestimmtes Ereignis eintritt. Ein frühestes und ein spätestes Jahr rahmen das ein (siehe Mechanik).
5. **Der Flughafen beendet die Kutschenzeit:** Mit dem ersten Flugzeug der Société wechselt die Zeitung endgültig vom Stil der Kutschenzeit in die Moderne der 1920er (Spielerwunsch).
6. **Offenes Ende:** Nach der letzten Stufe (News-App) ändert sich nichts mehr. Sie bleibt bis 2050 und darüber hinaus.
7. **Die Technik treibt die Zeitung:** Ab den 1930ern lösen **Technik-Jahrgänge** die Stufen aus, also das erste neue Fahrzeugmodell der Société mit einem bestimmten Baujahr laut Spiel. Die Zeitung modernisiert sich so mit dem Fuhrpark (Spielerentscheidung 18.10.2026).
8. **Krise ist ein Zustand, keine Epoche:** Der Spieler weiß nicht, ob es je eine Krise gibt. Deshalb kommt der Look der 30er/40er über die Technik. Das graue **Krisenpapier** erscheint nur, solange die Kasse wirklich eingebrochen ist, und verschwindet wieder (siehe „Zustände“). Ohne Krise wird die Zeitung nie grau.
9. **Der Name darf sich ändern:** Mit den Stufen darf die Zeitung umbenannt werden. „Alizés“ bleibt im Namen immer erkennbar (siehe „Namen“).
10. **Schalter „im heutigen Stil lesen“:** Alte Ausgaben lassen sich auch im aktuellen Stil und mit dem aktuellen Namen lesen.

11. **Nur das Journal verändert sich**, nicht die übrige Chronicles-Seite (bestätigt 18.10.2026).

## Was immer gleich bleibt

- Die Kennzeichnung **Belegt / Spielervorgabe / Einordnung / Fiktion** und der „Bezug“ jedes Beitrags.
- Die Bedienung: Ausgaben blättern, Rubriken, Links zwischen Geschichte, Person, Ortsakte und Karte.
- Lesbarkeit auf dem Handy und ausreichender Kontrast. Ein Krisenjahr-Layout darf nach grauem Papier *aussehen*, muss aber gut lesbar bleiben.
- Alle Daten (Meldungen, Menschen, Städte, Fuhrpark, Karte). Es ändert sich nur, wie sie gezeigt werden.

## Mechanik

### Merkmale

| Merkmal | Beispiele für Stufen |
|---|---|
| `ueberschrift` | Didone mit Zierlinien → schlichte Antiqua → geometrische Art-déco-Schrift → fette Grotesk → moderne Grotesk → Web-Schrift |
| `kopf` | Zeitungskopf mit Doppellinien → Art déco mit Goldakzent → Schlagzeilenbalken → rote Fahne → Website-Kopf → App-Leiste |
| `bilder` | Kupferstich → Rasterfoto schwarzweiß → Farbe → digitale Fotos |
| `papier` | warmes Papier → helles Papier → dünnes graues Papier → Weiß → Bildschirm |
| `akzent` | Rot der Initialen → Gold → Schwarz → Signalrot → Linkblau → Systemfarbe |
| `spalten` | dichte Spalten → weniger, breitere Spalten → Raster mit Weißraum → einspaltig (App) |
| `preis` | „10 centimes“ steigt in Stufen, später „gratis online“ |
| `medium` | Papier → Website → App (ändert Kopf, Navigation und Wortwahl der Rubriken) |
| `name` | Name im Zeitungskopf, z. B. „Le Journal des Alizés“ → „Alizés-Soir“ → „alizes-journal.fr“ (Vorschläge unter „Namen“) |
| `sprache` | Regel für Redaktionsbeiträge: förmlich-ausführlich → knapp-zugespitzt → Online-Ton. Steht in `JOURNAL.md` für die Geschichten, nicht im Code. |

### Frühestens, Auslöser, spätestens

Jede Stufe eines Merkmals hat drei Angaben:

- **frühestens** (Jahr): Vorher wechselt nichts, egal was im Spiel geschieht. Es gibt also kein Fernsehprogramm 1925.
- **Auslöser**: ein messbares Ereignis der Welt. Tritt es nach „frühestens“ ein, wechselt die Stufe in diesem Monat.
- **spätestens** (Jahr): Tritt das Ereignis nie ein, wechselt die Stufe trotzdem. Die Zeitung bleibt nicht in einer Zeit stecken.

Tritt das Ereignis schon *vor* „frühestens“ ein, wechselt die Stufe im ersten Monat von „frühestens“. Der Anlass wird dann trotzdem genannt.

### Auslöser-Arten

Alle stammen aus Daten, die `build-journal.py` heute schon hat:

| Art | Bedeutung | Quelle |
|---|---|---|
| `premiere` | erste Linie einer Fahrzeugart mit Fahrzeug (z. B. Flugzeug) | `meldungen.json` |
| `modell` | erstes neues Fahrzeugmodell mit Baujahr laut Spiel ab einem Jahr | `meldungen.json` (`modell`), `fuhrpark.json` |
| `stadt` | eine (bestimmte oder beliebige) Stadt erreicht eine Einwohnerzahl | `meldungen.json` (`stadt`), `staedte.json` |
| `netz` | Netz erreicht Fahrzeug- oder Linienzahl | `meldungen.json` (`netz`) |
| `kasse` | Kassenstand über einer Schwelle | Detailmessungen (`money`) |
| `wahrzeichen` | ein Wahrzeichen ist fertig | Detailmessungen (`landmarks`) |
| `umwelt` | eine Stadt überschreitet einen Lärm- oder Verschmutzungswert | Detailmessungen (`noise_db`, `pollution_db`) |
| `meldung` | allgemein: erste Meldung eines Typs mit Textmuster | `meldungen.json` |

### Zustände (umkehrbar)

Neben den Stufen, die nur vorwärts gehen, gibt es **Zustände**, die kommen und wieder gehen. Sie überlagern die gerade gültigen Stufen, ersetzen sie aber nicht.

| Zustand | Beginnt | Endet | Wirkung |
|---|---|---|---|
| `krisenpapier` | Kassenstand fällt binnen 12 Spielmonaten um mindestens 20 % (frühestens 1925) | Kasse erreicht wieder den Stand vor dem Einbruch, oder 12 Monate durchgehend Wachstum | dünnes graues Papier, weniger Spalten, Rubrik „Bekanntmachungen“ |

Auch ein Zustand bekommt beim Beginn eine Notiz „In eigener Sache“ mit dem belegten Anlass, etwa „Wegen der angespannten Lage der Société erscheint diese Ausgabe auf einfacherem Papier.“ Weitere Zustände sind denkbar, etwa ein Festtagskopf, wenn ein Wahrzeichen fertig wird.

### Wo die Regeln stehen

- `data/epochen.json`: Vorlage für alle Welten mit Merkmalen, Stufen und Auslöser-Vorschlägen.
- Optional `saves/<welt>/data/epochen.json`: überschreibt einzelne Stufen für eine Welt, etwa „Radio erst mit der ersten Straßenbahn in Roquemer“.
- **Keine Ortsnamen, Linien oder Jahre im Code** (siehe Regel „keine Hardcodes“). Was für diese Welt gilt, steht nur in ihrer Datei.

### Berechnung

`build-journal.py` wertet die Regeln auf dem **kanonischen Spielverlauf** aus und schreibt `zeitleiste.json`: für jedes Merkmal jede erreichte Stufe mit Monat und Anlass (Meldungs-ID oder Messwert) bzw. „spätestens erreicht“. Rücksprünge und geladene Spielstände verändern die Zeitleiste nicht. Dieselben Messungen ergeben immer dieselbe Zeitleiste (Test).

### Anzeige

- `journal.js` bestimmt für den Monat der angezeigten Ausgabe die gültige Stufe jedes Merkmals und setzt sie als Attribute am Journal (`data-kopf="artdeco"` usw.). Die Stile liegen je Merkmal und Stufe in `assets/epochen/`.
- Optionaler Schalter **„im heutigen Stil lesen“** für alte Ausgaben, als Komfort im Browser gespeichert.
- Rubriken erscheinen in der Navigation erst ab ihrem Monat. Ältere Ausgaben zeigen sie nicht.
- Schriften liegen möglichst **lokal** im Repository statt bei Google Fonts. Das ist schneller und schont die Privatsphäre der Leser.

### „In eigener Sache“

Die erste Ausgabe nach einem sichtbaren Wechsel trägt automatisch eine kurze Notiz mit dem **belegten Anlass**, etwa „Seit am 14. Juni 1920 das erste Flugzeug der Société abhob, erscheint diese Zeitung in neuem Gewand.“ Ausführlichere Stücke, in denen Figuren auf das neue Layout reagieren, kommen von Hand in `redaktion.json` (Fiktion, mit Bezug).

## Umsetzung (Stand 18.10.2026)

| Teil | Datei |
|---|---|
| Regeln, Vorlage für alle Welten | `data/epochen.json` (Stufen 1–5, Merkmale, Rubrik Radioprogramm, Zustand Krisenpapier) |
| Regeln dieser Welt | `saves/archipel-des-alizes/data/epochen.json` (Name, Kopfzeile, Preis, Name der Gesellschaft; Ortsnamen und Namen nur hier) |
| Auswertung | `scripts/journal_epochen.py`, aufgerufen von `build-journal.py` auf dem kanonischen Verlauf |
| Ergebnis | `saves/<welt>/data/journal/zeitleiste.json` (ohne Vorlage keine Datei, alle anderen Dateien byte-identisch) |
| Anzeige | `assets/journal-epochen.js` (gültige Stufe je Ausgabe, „In eigener Sache“), Stile je Merkmal in `assets/epochen/*.css` |
| Rubrik Radioprogramm | `saves/<welt>/data/journal/radioprogramm.json`, von Hand (Fiktion), Struktur unten |
| Prüfung | `validate-journal.mjs` (Zeitleiste, Programme), `test-build-journal.py` (11 Epochen-Tests) |

### Regeldatei

- `stufen`: Liste mit `nr`, `name`, optional `notiz` (Text für „In eigener Sache“), dazu `fruehestens`, `spaetestens` (Jahre) und `ausloeser`. Die erste Stufe gilt ab Beginn der Aufzeichnung und hat keinen Auslöser.
- `merkmale`: je Merkmal `bezeichnung` und `stufen` [{`wert`}, {`wert`, `stufe`: 2}, …]. Der erste Wert gilt von Anfang an, jeder weitere wechselt mit einer Stufe oder mit eigenem `fruehestens`/`ausloeser`/`spaetestens` (dann schleichend unabhängig von den Stufen). Stilmerkmale haben Werte aus Kleinbuchstaben (`didone`, `artdeco` …) und werden zu data-Attributen; Textmerkmale (`"text": true`, z. B. `name`, `kopfzeile`, `preis`) stehen im Zeitungskopf. Beim Namen sagt `vormals_ausgaben`, wie viele Ausgaben der alte Name klein darunter steht.
- `rubriken`: je Rubrik `titel`, `stufe` (oder eigener Auslöser), `form` (bisher `programm`), `fuellung` (`fiktion` oder `messdaten`), `datei`.
- `zustaende`: bisher `krisenpapier` mit `fruehestens`, `beginn` {`art`: `kasse_einbruch`, `rueckgang_prozent`, `binnen_monaten`}, `ende` {`wachstum_monate`}, `notiz_beginn`, `notiz_ende`.
- Die Datei einer Welt überschreibt Stufen nach `nr` und Merkmale, Rubriken und Zustände nach Namen, Feld für Feld; `null` entfernt einen Eintrag. Beispiel „Radio erst mit der ersten Straßenbahn in Roquemer“: `{"schema_version": 1, "stufen": [{"nr": 5, "ausloeser": {"art": "meldung", "typ": "premiere", "muster": "Straßenbahn.*Roquemer"}}]}`.
- Eine fehlerhafte Regeldatei (unbekannte Auslöser-Art, frühestens nach spätestens, Stufen außer der Reihe …) bricht den Bau mit einer Meldung ab.

Textmerkmale, die zur Welt gehören und nicht zum Stil, tragen `"stil": false` (bisher `firma`, der Name der Gesellschaft): Sie folgen immer dem Monat der Ausgabe, auch im heutigen Stil, und zählen nicht als Stilunterschied für den Schalter.

Auslöser und ihre Angaben: `premiere` {`fahrzeugart`}, `modell` {`baujahr_ab`, optional `fahrzeugart`}, `stadt` {`einwohner_ab`, optional `stadt` = Orts-ID}, `netz` {`fahrzeuge_ab` oder `linien_ab`}, `kasse` {`ab`}, `wahrzeichen` {optional `id`}, `umwelt` {`laerm_ab` oder `verschmutzung_ab`, optional `stadt`}, `meldung` {`typ`, optional `muster` als regulärer Ausdruck über Titel und Text}, `vorgabe` {`monat` wie `1921-10`, optional `quelle`}: eine Spielervorgabe für einen festen Monat, etwa eine Umbenennung, die der Monitor nicht misst. Ihr Anlass hat keinen Tag, sagt „Spielervorgabe … kein Messwert“ und trägt in der Notiz das Etikett „Spielervorgabe“; ein Monat nach dem letzten Messstand bleibt offen. Einwohner- und Umweltschwellen brauchen wie die Meilensteine der Meldungen zwei Stadtstände nacheinander. Eine Premiere zählt auch, wenn die Fahrzeugart schon bei Beginn der Aufzeichnung fuhr; ein Modell auch, wenn es schon im Ausgangsbestand der Modellerfassung war.

### Wann eine Stufe erreicht ist

- **Auslöser** im Monat des Ereignisses (`grund: ausloeser`), frühestens im **Januar** von `fruehestens` (`grund: fruehestens`, der frühere Anlass wird genannt), spätestens im **Januar** von `spaetestens` (`grund: spaetestens`, ohne Anlass).
- Stufen folgen ihrer Reihenfolge: Eine Stufe kommt nie vor der vorigen (`grund: vorgaenger`, gleicher Monat). Was schon bei Beginn der Aufzeichnung galt, hat `grund: beginn` und wird nicht angekündigt.
- Monate nach dem letzten Messstand bleiben offen (`monat: null`, `grund: offen`). Rücksprünge ändern nichts, weil nur der kanonische Verlauf zählt; dieselben Messungen ergeben dieselbe Datei (Tests).
- **Krisenpapier** rechnet mit dem Kassenstand der letzten Detailmessung jedes Spielmonats (wie die Kassenkurve im Fuhrpark): Beginn, wenn dieser Stand höchstens 80 % des höchsten Stands der zwölf Monate davor beträgt (frühestens 1925); Ende im ersten Monat, in dem die Kasse diesen Höchststand wieder erreicht oder zwölf Monate in Folge gewachsen ist (eine Lücke in der Aufzeichnung unterbricht die Folge). Das Krisenpapier gilt vom Beginn bis vor das Ende und kann später wiederkommen.

### Anzeige

- `journal.js` setzt am Journal `data-ueberschrift`, `data-kopf`, `data-bilder`, `data-papier`, `data-akzent`, `data-stufe` und während eines Zustands `data-zustand="krisenpapier"`. Topbar, Fußleiste und alle anderen Seiten der Chronicles bleiben unverändert; der Titel des Browserfensters folgt dem Namen der Ausgabe.
- Stufe 1 ist das bisherige Design (im Browser verglichen: gleiche berechnete Stile). Stufe 2: Überschriften in Source Serif 4 statt Playfair, einfache statt doppelte Linien. Stufe 3: Kopfzeile „Quotidien illustré de l’Archipel“, Fotos mit schwarzer Haarlinie, weißem Rand und „Photo.“ (die Bilder selbst bleiben unverfärbt). Stufe 4: Art-déco-Kopf mit Strahlenfächer und goldenen Doppellinien, Versaltitel und Überschriften in geometrischer Grotesk, Gold statt Rot als Akzent (das Etikett „Fiktion“ bleibt rot), Name „Journal des Alizés“, sechs Ausgaben lang „vormals Le Journal des Alizés“. Stufe 5: wie 4, dazu die Rubrik „Radioprogramm“.
- **Krisenpapier:** graues, leicht faseriges Papier, nur eine Druckfarbe, Artikel einspaltig, weniger Spalten in Meldungen und Geschichten, auf der Titelseite der Kasten „Bekanntmachungen“ mit Schließungen, eingestellten Linien und Ausdünnungen des Monats (Belegt). Alle Texte behalten mindestens 4,5 : 1 Kontrast.
- **In eigener Sache:** In der ersten Ausgabe ab dem Monat eines sichtbaren Wechsels steht oben auf der Titelseite die `notiz` der Stufe, ein Satz zum neuen Namen und zu neuen Rubriken sowie die Begründung mit dem belegten Anlass (Etikett „Belegt“) oder dem Hinweis auf „spätestens“ (Etikett „Einordnung“). Beginn und Ende des Krisenpapiers bekommen ebenfalls eine Notiz.
- **Schalter „Im heutigen Stil lesen“** unter der Datumszeile, nur bei Ausgaben, die anders aussehen als die neueste. Er zeigt Stil, Name und Kopfzeile der neuesten Ausgabe (Zustände wie das Krisenpapier gehören zu ihrer Ausgabe und bleiben weg), nennt den Originalnamen und die Stufe und blendet die Notiz aus. Gemerkt wird er nur als Komfort im Browser (`localStorage`); ohne Speicher startet die Seite im Stil der Zeit.
- **Name der Gesellschaft:** Unter der Unterzeile steht „Nach den Messbüchern der …“ mit dem Namen im Monat der Ausgabe, nach einer Umbenennung sechs Ausgaben lang „vormals …“ darunter. Ältere Ausgaben behalten den alten Namen, auch im heutigen Stil. Die Monitorseite (`assets/monitor.js`) zeigt im Siegel den neuesten Namen aus `zeitleiste.json`; ohne Datei kein Name statt eines festen.
- **Rubriken** erscheinen in der Navigation hinter „Geschichten“ erst ab ihrem Monat. Das Radioprogramm zeigt das Programm der Ausgabe, sonst das jüngste davor, dazu frühere Programme; auf der Titelseite steht ein Kasten mit den ersten Sendungen, wenn es für den Monat ein Programm gibt.
- **Schriften:** Playfair Display, Source Serif 4 und Jost liegen lokal im Repository; die Seite fragt keinen fremden Server an. Die geometrische Schrift der Stufe 4 ist Jost (SIL Open Font License, `assets/fonts/OFL-Jost.txt`): variable Datei `assets/fonts/jost.woff2` (Stärken 100 bis 900, nur Latin, 26 KB, aus `@fontsource-variable/jost` 5.3.0), eingebunden per `@font-face` in `journal.css` und an erster Stelle der Schriftliste `--j-geo`. Der Browser lädt sie nur für Ausgaben ab Stufe 4; frühere Ausgaben brauchen sie nicht. Fehlt die Datei, greifen Futura, Century Gothic, Avenir …, sonst die Grotesk des Geräts. Eine Kursive gibt es nicht, Stufe 4 braucht keine.

### Radioprogramm schreiben

`radioprogramm.json`: `schema_version` 1, `hinweis` (muss „erfunden“ enthalten), `programme` mit je `id`, `date` (Spielmonat, nicht vor dem Monat der Rubrik), `art: "fiktion"`, optional `sender`, `titel`, `grounding` (was erfunden ist, mindestens 40 Zeichen), `tage` [{`tag`, `sendungen` [{`zeit` wie „20.30“, `titel`, optional `text`}]}], optional `refs` {`personen`, `staedte`}. Für Programme gelten dieselben Schreibregeln wie für Geschichten (`JOURNAL.md`).

### Eine weitere Stufe bauen

1. Stufe in `data/epochen.json` eintragen (Nummer, Name, Notiz, frühestens, Auslöser, spätestens) und die Merkmale mit `"stufe": n` ergänzen; Ortsbezüge nur in der Datei der Welt.
2. Für neue Werte eine Regel `.j[data-merkmal=wert]` in `assets/epochen/<merkmal>.css`; für neue Rubrikformen `journal.js` erweitern.
3. Versionsparameter der geänderten Dateien in `journal.html` erhöhen (sonst liefert der Browser-Cache alte Dateien).
4. `python scripts/test-build-journal.py`, `node scripts/validate-journal.mjs`, Browser-Vorschau der betroffenen Monate, Desktop und 375 px.

## Stufen bis 2050 (Entwurf zum Diskutieren)

| # | Stufe | Aussehen | Neue Rubriken (Füllung) | frühestens · Auslöser · spätestens |
|---|---|---|---|---|
| 1 | Kutschenzeit (Start) | heutiges Design: Didone-Kopf, Stiche, Zierlinien | Schiffsmeldungen, Réclame | Beginn der Aufzeichnung |
| 2 | Schlichtere Überschriften | Antiqua ohne Zier, weniger Linien | – | 1915 · Kasse über 1 Milliarde · 1922 |
| 3 | Erste Fotos | Rasterfotos schwarzweiß | Bildreportagen häufiger | 1916 · neues Modell mit Baujahr ab 1918 · 1923 |
| 4 | **Ende der Kutschenzeit** | Art-déco-Kopf, Goldakzent, geometrische Schrift | – | 1919 · **erstes Flugzeug** · 1925 |
| 5 | Rundfunkzeit | wie 4 | Radioprogramm, Kino, Sport (Fiktion) | 1922 · eine Stadt erreicht 4.000 · 1927 |
| 6 | Dreißiger/Vierziger | fette Grotesk-Schlagzeilen, harte Kontraste (graues Papier nur als Zustand `krisenpapier`) | – | 1932 · erstes Modell mit Baujahr ab 1935 · 1940 |
| 7 | Nachkriegsmoderne | moderne Grotesk, Weißraum, erste Farbe | – | 1948 · erstes Modell mit Baujahr ab 1950 · 1955 |
| 8 | Fernsehzeit | wie 7 | Fernsehprogramm, Autoseite (Fiktion) | 1950 · eine Stadt erreicht 10.000 · 1958 |
| 9 | Offset in Farbe | kräftige Farbflächen, Infografiken | – | 1965 · erstes Modell mit Baujahr ab 1965 · 1975 |
| 10 | Umweltbewusstsein | wie 9 | Umwelt (aus Messdaten: Lärm, Verschmutzung) | 1965 · eine Stadt über 80 dB · 1975 |
| 11 | Verkehrsfunk | wie 9 | Verkehrsfunk (aus Messdaten: Wartende, Wegprobleme) | 1970 · erstes Modell mit Baujahr ab 1970 · 1980 |
| 12 | Die Zeitung wird Website | Netscape-Look, Linkblau, Besucherzähler | Gästebuch, Online-Umfrage (Fiktion) | 1993 · Netz erreicht 2.000 Fahrzeuge · 2000 |
| 13 | Nachrichtenportal | Portal mit Teasern | Liveticker (aus Meldungen) | 2004 · erstes Modell mit Baujahr ab 2000 · 2010 |
| 14 | News-App (Endstufe) | einspaltig, App-Leiste, Push-Meldungen | Wirtschaft (aus Messdaten: Kasse, Produktion) | 2018 · erstes Modell mit Baujahr ab 2015 · 2025, bleibt bis 2050+ |

Der Look der Dreißiger/Vierziger (6) braucht keine Kriegsthemen. Er zeigt nur, wie Zeitungen damals aussahen. Was in der Welt geschieht, bestimmt der Spieler.

„Erstes Modell mit Baujahr ab …“ heißt: Die Société setzt erstmals ein Fahrzeugmodell ein, das laut Spiel ab diesem Jahr verfügbar ist (`verfuegbar_ab` im Fuhrpark, Meldung „Neues Fahrzeugmodell“). Kauft der Spieler lange nichts Neues, greift „spätestens“.

## Namen

Vom Spieler bestätigt (18.10.2026). Der Name ist ein eigenes Merkmal und wechselt zusammen mit einer Stufe. Jeder Namenswechsel bekommt eine Notiz „In eigener Sache“, und der alte Name steht noch einige Ausgaben klein unter dem neuen („vormals Le Journal des Alizés“).

| ab Stufe | Name | Gedanke |
|---|---|---|
| 1 | Le Journal des Alizés | wie heute |
| 4 | Journal des Alizés | Art déco, kürzer und moderner, ohne Artikel |
| 7 | Alizés-Soir | Nachkriegs-Abendzeitung |
| 12 | alizes-journal.fr | Die Zeitung geht online |
| 14 | Alizés | App-Name, nur noch ein Wort |

## In dieser Welt (Stand Spiel 17.01.1924)

So steht es in `zeitleiste.json`, berechnet aus den Messungen:

| Stufe | Wechsel | Anlass (gemessen) |
|---|---|---|
| 1 Kutschenzeit | Dezember 1904 bis November 1918 | Beginn der Aufzeichnung |
| 2 Schlichtere Überschriften | Dezember 1918 | Kasse erstmals über 1 Milliarde (13.12.1918, 1.004,1 Mio.) |
| 3 Erste Fotos | Januar 1919 | Daimler Decksitzwagen, laut Spiel ab 1919 verfügbar, erstmals im Betrieb 06.01.1919 (Meldung „Neues Fahrzeugmodell“) |
| 4 Ende der Kutschenzeit | Juni 1920 | Premiere Flugzeug am 14.06.1920 (Linie Port des Alizés – Sin-le-Noble), Name „Journal des Alizés“ |
| 5 Rundfunkzeit | November 1922 | Bourg-l’Écorce zählt am 17.11.1922 als erste Stadt 4.012 Einwohner (Meldung „Bourg-l’Écorce zählt 4.000 Einwohner“), Rubrik „Radioprogramm“ ab dieser Ausgabe |

Krisenpapier: bisher kein Fall (frühestens 1925).

Name der Gesellschaft (Merkmal `firma`, Spielervorgabe vom 19.10.2026): bis September 1921 „Société des Routes et des Rails“, ab der Ausgabe Oktober 1921 „Société des Alizés — Routes, Voyages et Commerce“ mit Notiz „In eigener Sache“ und sechs Ausgaben lang „vormals Société des Routes et des Rails“.

Die Zeitung nimmt im Juni 1920 Abschied von der Kutschenzeit, die Kutschen selbst aber noch nicht: Laut Fuhrpark fahren im Januar 1924 weiter **drei Postkutschen** (gekauft 1900) auf der Buslinie in Anse Dorée (Grande Rue – Domaine des Alizés); im August 1922 fuhr in den Geschichten ein Brautpaar damit („Tischordnung“), im November 1923 verweist die Bittschrift um Zucker auf sie. Das ist Stoff für eine Geschichte, oder eine Entscheidung im Spiel.

## Offene Fragen

- Stufe 6 (Dreißiger/Vierziger) bauen, kurz bevor das Spiel sie erreichen kann (frühestens 1932).
- Radioprogramm Monat für Monat weiterschreiben (bisher November 1922 bis Januar 1924, Sender „Radio Alizés · Sender Bourg-l’Écorce“; wiederkehrende Sendungen in `JOURNAL.md` unter „Rundfunkzeit“).

Geklärt am 18.10.2026: Auslöser der Stufen 6, 9, 11, 13 und 14 (Technik-Jahrgänge), Krise als Zustand, Namen je Stufe, Schalter „im heutigen Stil lesen“ kommt, nur das Journal verändert sich, Umfang der ersten Runde (Mechanik, Krisenpapier, Stufen 1 bis 5). Ebenfalls am 18.10.2026: Jost liegt als freie geometrische Schrift der Stufe 4 im Repository (siehe „Schriften“).

## Umsetzung in Schritten

1. Erledigt: Regeldatei `data/epochen.json`, Auswertung in `build-journal.py`, `zeitleiste.json` mit Stufen und Zuständen, Validator und Tests (frühestens, spätestens, Auslöser vor „frühestens“, Zustand beginnt und endet, Rücksprung ändert nichts, gleiche Messungen, ohne Regeldatei byte-identisch).
2. Erledigt: Anzeige-Gerüst in `journal.js`, Stile für die Stufen 1 bis 4 und das Krisenpapier, Name je Stufe, Notiz „In eigener Sache“, Schalter „im heutigen Stil lesen“, lokale geometrische Schrift (Jost).
3. Erledigt: Rubriken-Gerüst (Rubrik erscheint ab ihrem Monat) und die Rundfunkzeit (Stufe 5, Radioprogramm von Hand; in dieser Welt seit November 1922, Programme bisher November 1922 bis Januar 1924).
4. Jede spätere Stufe kurz bevor das Spiel sie erreicht.
