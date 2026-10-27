# Werkstatt – gemeinsamer Arbeitsbereich für Claude und Codex

Hier stimmen sich die KI-Sitzungen ab, die an den Chroniken arbeiten (Claude Code, Codex, weitere). Die Chroniken selbst liegen unter `saves/<welt>/`. Die Werkstatt hält fest, wer gerade woran arbeitet, wie weit eine Welt erzählt ist und welche Messwerte dafür bereitliegen.

**Öffentlich:** Das Repo ist öffentlich und wird als GitHub Pages ausgeliefert. Alles in `werkstatt/` ist im Netz lesbar. Keine Zugangsdaten, Schlüssel oder privaten Dateien ablegen.

## Was wo liegt

| Datei | Zweck | Wer schreibt |
|---|---|---|
| `AUFGABEN.md` | Tafel mit In Arbeit, Zur Prüfung, Offen, Erledigt. Wer etwas anfängt, trägt sich zuerst hier ein. | alle Sitzungen |
| `LOG.md` | Übergaben und Reviews, neueste oben. Nur ergänzen, nichts umschreiben. | alle Sitzungen |
| `eingang/` | Screenshots, Notizen und Wünsche des Spielers, die noch niemand verarbeitet hat. | Spieler; Sitzungen räumen auf |
| `falkenmark/STAND.md` | Wie weit die Falkenmark erzählt ist, nächste freie Quellennummer, Bilder, Datenstand, Fallstricke. | wer ein Kapitel abschließt |
| `falkenmark/fakten/JJJJ.md` | Faktenblatt je Spieljahr aus dem Spielmonitor. Erzeugt von `scripts/falkenmark-fakten.py`, nicht von Hand ändern. | Skript |
| `erlenmark/STAND.md` | Dasselbe für die Erlenmark (seit 27.10.2026): Erzähltes, nächste freie Quellennummer, Daten, Spielstand, Namen, Szenen. | wer ein Kapitel abschließt |

Die Regeln der Falkenmark-Chronik stehen in `docs/FALKENMARK.md`, die der Erlenmark in `docs/ERLENMARK.md`, das Journal des Archipels in `docs/JOURNAL.md`. Bekommt das Archipel hier einen eigenen Ordner, dann `werkstatt/archipel/` nach demselben Muster.

## Ablauf einer Sitzung

1. **Aktualisieren:** `git fetch origin` und `git merge --ff-only origin/main`. Andere Sitzungen schieben parallel.
2. **Lesen:** `AUFGABEN.md`, die obersten Einträge in `LOG.md`, den `STAND.md` der Welt; `eingang/` ansehen.
3. **Eintragen:** Aufgabe unter „In Arbeit“ mit Wer, Datum und Dateien. Solange dort jemand für eine Datei eingetragen ist, ändert niemand sonst sie. `chronik.html` und `data/events.json` einer Welt gelten zusammen als eine Einheit. Arbeiten beide Sitzungen im selben Ordner (`E:\KI-Projekte\Transport-Fever-Chronicles`), sieht die andere den Eintrag sofort, sonst erst nach dem Hochladen.
4. **Arbeiten** nach den Regeln der Welt.
5. **Prüfen:** mindestens `node scripts/validate-data.mjs`; bei Monitordaten zusätzlich `node scripts/validate-monitor.mjs`.
6. **Abschließen:** Aufgabe nach „Erledigt“ (mit Commit, sobald es einen gibt) oder nach „Zur Prüfung“, `STAND.md` nachziehen, Übergabe oben in `LOG.md`.
7. **Hochladen nur mit Freigabe des Spielers.** Vor dem Push erneut `git fetch`; ist `origin/main` weiter, zusammenführen. Kein `--force`, keine fremden Commits umschreiben.

## Regeln für alle

- **Wortlaut:** Veröffentlichte Kapitel nicht umschreiben. Ausnahme: ein Fehler. Dann knapp korrigieren und unter „Korrekturen“ in der Chronik mit Datum und Grund vermerken.
- **Register:** `data/events.json` ist append-only. Einträge nicht löschen; Fehler bekommen ein Feld `correction` mit `date` und `note`.
- **Zahlen** nur aus Messungen, Faktenblättern, Screenshots oder Angaben des Spielers. Fehlt etwas, bleibt es offen und kommt unter „Offen und unbestätigt“.
- **Werte „pro Jahr“** aus dem Spiel (Produktion, Versand, Linienbilanz) gelten für ein Wirtschaftsjahr des Spiels, nicht für das Kalenderjahr. In beiden Welten läuft der Kalender langsamer (rund 16.000 Spielzeit-Einheiten je Tag); ein Wirtschaftsjahr sind dort rund 91 Kalendertage. Die Finanztabelle dagegen rechnet nach Kalenderquartalen.
- **Textarten:** Belegt, Abgeleitet und Literarische Szene getrennt halten. Erfundene Personen und Zitate nur in Szenen mit Etikett.
- **Namen** von Orten, Firmen und Landschaften erst nach Bestätigung des Spielers.
- **Quellen:** Nummern (Q1, Q2, …) vergibt, wer ein Kapitel schreibt. Die nächste freie Nummer steht im `STAND.md` der Welt; wer eine vergibt, zählt dort sofort weiter.
- **Bilder** unter `saves/<welt>/images/`. KI-Bilder als solche kennzeichnen, mit Vorlage (z. B. „KI-Bild nach einem Screenshot im Spiel“).
- **Keine Zukunft:** Keine Sitzung plant, was in der Welt passieren wird. Der Spieler spielt, die Chronik folgt.
- **Welten getrennt:** Nichts aus dem Archipel in die Falkenmark übernehmen und umgekehrt.

## Wer was kann

- **Claude** (Claude Code auf dem Rechner des Spielers) kommt an den Spielmonitor (`E:\KI-Projekte\Spielmonitor`): erzeugt Faktenblätter, lädt Messdaten hoch (`WEBSITE_AKTUALISIEREN.bat`), schreibt Kapitel.
- **Codex** hat in der Regel nur dieses Repo. Prüft Kapitel gegen Faktenblätter und Register (Zahlen, Daten, Textarten, Regeln), schreibt auf Absprache auch Kapitel. Messdaten erzeugt Codex nicht selbst; fehlt ein Faktenblatt, kommt das als Aufgabe für Claude auf die Tafel.

Faktenblatt erzeugen (nur wo der Spielmonitor liegt):

```bash
py -3 scripts/falkenmark-fakten.py 1902
```

## Review-Format

Wer prüft, schreibt in `LOG.md` einen Eintrag „Review“ mit Fundstellen: Datei, Abschnitt, was steht, was die Quelle sagt, Vorschlag. Ändern darf die Sitzung, die die Datei unter „In Arbeit“ hält, oder nach Absprache die prüfende.
