# Epochen: Die Zeitung altert mit dem Spiel

**Konzept, abgestimmt, noch nicht umgesetzt.** Mit dem Spieler besprochen am 18.10.2026. Ziel ist, dass „Le Journal des Alizés“ so aussieht wie eine Zeitung ihrer Zeit: um 1905 anders als in den 1920ern, den 1940ern oder als Website der 1990er. Das Spiel soll bis 2050 oder länger laufen.

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

## In dieser Welt (Stand Spiel 13.10.1921)

Mit den Vorschlägen oben wäre die Zeitung schon durch die ersten Wechsel gegangen:

| Stufe | Wechsel | Anlass (gemessen) |
|---|---|---|
| 1 Kutschenzeit | bis November 1918 | – |
| 2 Schlichtere Überschriften | Dezember 1918 | Kasse erstmals über 1 Milliarde (13.12.1918) |
| 3 Erste Fotos | Januar 1919 | Daimler Decksitzwagen, Baujahr laut Spiel ab 1919, erstmals im Betrieb 06.01.1919 |
| 4 Ende der Kutschenzeit | Juni 1920 | erstes Flugzeug (Junkers F 13 Herta) am 14.06.1920, Flughäfen Port des Alizés und Sin-le-Noble |
| 5 Rundfunkzeit | noch offen | größte Stadt Bourg-l’Écorce mit 3.828 Einwohnern (Oktober 1921), 4.000 fehlen noch |

Die Zeitung nimmt im Juni 1920 Abschied von der Kutschenzeit, die Kutschen selbst aber noch nicht: Laut Fuhrpark fahren im Oktober 1921 weiter **drei Postkutschen** (gekauft 1900) auf der Buslinie in Anse Dorée. Das ist Stoff für eine Geschichte, oder eine Entscheidung im Spiel.

## Offene Fragen

- Wie viele Stufen vorab bauen? Vorschlag: Mechanik, Zustand `krisenpapier` und Stufen 1 bis 5 jetzt, jede weitere Stufe kurz bevor das Spiel sie erreichen kann.

Geklärt am 18.10.2026: Auslöser der Stufen 6, 9, 11, 13 und 14 (Technik-Jahrgänge), Krise als Zustand, Namen je Stufe, Schalter „im heutigen Stil lesen“ kommt, nur das Journal verändert sich.

## Umsetzung in Schritten (wenn freigegeben)

1. Regeldatei `data/epochen.json`, Auswertung in `build-journal.py`, `zeitleiste.json` mit Stufen und Zuständen, Validator und Tests (frühestens, spätestens, Auslöser vor „frühestens“, Zustand beginnt und endet, Rücksprung ändert nichts).
2. Anzeige-Gerüst in `journal.js`, Stile für die Stufen 1 bis 4 und das Krisenpapier, Name je Stufe, lokale Schriften, Notiz „In eigener Sache“, Schalter „im heutigen Stil lesen“.
3. Rubriken-Gerüst (Rubrik erscheint ab ihrem Monat) und die Rundfunkzeit (Stufe 5).
4. Jede spätere Stufe kurz bevor das Spiel sie erreicht.
