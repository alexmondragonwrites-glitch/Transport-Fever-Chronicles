# Epochen: Die Zeitung altert mit dem Spiel

**Konzept, noch nicht umgesetzt.** Mit dem Spieler besprochen am 18.10.2026. Ziel ist, dass „Le Journal des Alizés“ so aussieht wie eine Zeitung ihrer Zeit: um 1905 anders als in den 1920ern, den 1940ern oder als Website der 1990er. Das Spiel soll bis 2050 oder länger laufen.

## Festgelegt

1. **Gang durchs Archiv:** Jede Ausgabe erscheint im Stil ihres Spielmonats. Wer zurückblättert, sieht die alten Ausgaben im alten Gewand.
2. **Schleichende Übergänge:** Es gibt keine festen Epochen-Blöcke, sondern einzelne **Merkmale** (Überschriftenschrift, Zeitungskopf, Bilder, Papier …), die zu unterschiedlichen Zeitpunkten wechseln. So verändert sich die Zeitung allmählich.
3. **Neue Rubriken mit Inhalt:** Rubriken wie Radio- oder Fernsehprogramm erscheinen erst, wenn ihre Zeit gekommen ist. Jede wird entweder **aus Messdaten** gefüllt (Belegt) oder **von Hand** (Fiktion), gekennzeichnet wie bisher.
4. **Ereignisse lösen aus, nicht der Kalender:** Jedes Merkmal wechselt, wenn in der Welt ein bestimmtes Ereignis eintritt. Ein frühestes und ein spätestes Jahr rahmen das ein (siehe Mechanik).
5. **Der Flughafen beendet die Kutschenzeit:** Mit dem ersten Flugzeug der Société wechselt die Zeitung endgültig vom Stil der Kutschenzeit in die Moderne der 1920er (Spielerwunsch).
6. **Offenes Ende:** Nach der letzten Stufe (News-App) ändert sich nichts mehr. Sie bleibt bis 2050 und darüber hinaus.

Vorschlag, noch nicht bestätigt: Nur das Journal verändert sich, nicht die übrige Chronicles-Seite. Der Name „Le Journal des Alizés“ bleibt.

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
| 6 | Krisenjahre | fette Grotesk-Schlagzeilen, graues Papier, weniger Seiten | Bekanntmachungen (gemischt) | 1932 · Auslöser offen (Vorschlag: Kasse sinkt binnen 12 Monaten deutlich) · 1938 |
| 7 | Nachkriegsmoderne | moderne Grotesk, Weißraum, erste Farbe | – | 1948 · erstes Modell mit Baujahr ab 1950 · 1955 |
| 8 | Fernsehzeit | wie 7 | Fernsehprogramm, Autoseite (Fiktion) | 1950 · eine Stadt erreicht 10.000 · 1958 |
| 9 | Offset in Farbe | kräftige Farbflächen, Infografiken | – | 1968 · Auslöser offen (Vorschlag: Netz erreicht 1.500 Fahrzeuge) · 1975 |
| 10 | Umweltbewusstsein | wie 9 | Umwelt (aus Messdaten: Lärm, Verschmutzung) | 1965 · eine Stadt über 80 dB · 1975 |
| 11 | Verkehrsfunk | wie 9 | Verkehrsfunk (aus Messdaten: Wartende, Wegprobleme) | 1970 · Auslöser offen · 1980 |
| 12 | Die Zeitung wird Website | Netscape-Look, Linkblau, Besucherzähler | Gästebuch, Online-Umfrage (Fiktion) | 1993 · Netz erreicht 2.000 Fahrzeuge · 2000 |
| 13 | Nachrichtenportal | Portal mit Teasern | Liveticker (aus Meldungen) | 2004 · Auslöser offen · 2010 |
| 14 | News-App (Endstufe) | einspaltig, App-Leiste, Push-Meldungen | Wirtschaft (aus Messdaten: Kasse, Produktion) | 2018 · Auslöser offen · 2025, bleibt bis 2050+ |

Der Look der Krisenjahre (6) braucht keine Kriegsthemen. Er zeigt nur, wie Zeitungen damals aussahen. Was in der Welt geschieht, bestimmt der Spieler.

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

- Bestätigen: nur das Journal verändert sich, der Name bleibt?
- Auslöser für die Stufen 6, 9, 11, 13 und 14.
- Schalter „im heutigen Stil lesen“: ja oder nein?
- Wie viele Stufen vorab bauen? Vorschlag: Mechanik und Stufen 1 bis 5 jetzt, jede weitere Stufe kurz bevor das Spiel sie erreichen kann.

## Umsetzung in Schritten (wenn freigegeben)

1. Regeldatei `data/epochen.json`, Auswertung in `build-journal.py`, `zeitleiste.json`, Validator und Tests (frühestens, spätestens, Auslöser vor „frühestens“, Rücksprung ändert nichts).
2. Anzeige-Gerüst in `journal.js`, Stile für die Stufen 1 bis 4, lokale Schriften, Notiz „In eigener Sache“, Schalter „im heutigen Stil lesen“.
3. Rubriken-Gerüst (Rubrik erscheint ab ihrem Monat) und die Rundfunkzeit (Stufe 5).
4. Jede spätere Stufe kurz bevor das Spiel sie erreicht.
