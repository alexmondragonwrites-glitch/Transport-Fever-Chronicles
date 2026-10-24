# Transport Fever Chronicles – Hinweise für KI-Sitzungen

Statische Website (GitHub Pages) mit Chroniken zu Spielständen aus Transport Fever 3. Zwei getrennte Welten: Archipel des Alizés (`saves/archipel-des-alizes/`) und Falkenmark (`saves/falkenmark/`). Mehrere Sitzungen arbeiten parallel daran, Claude Code und Codex.

## Zuerst lesen

1. `werkstatt/README.md`: Ablauf, Regeln, wer was kann.
2. `werkstatt/AUFGABEN.md`: wer gerade woran arbeitet. Vor dem Ändern eintragen.
3. Die obersten Einträge in `werkstatt/LOG.md`.
4. Für die Falkenmark: `werkstatt/falkenmark/STAND.md` und `docs/FALKENMARK.md`. Für das Archipel: `docs/JOURNAL.md`.

## Kurzregeln

- Vor dem Arbeiten und vor jedem Push `git fetch origin`; zusammenführen statt überschreiben. Kein `--force`.
- Hochladen nur mit Freigabe des Spielers.
- Keine Zahlen erfinden. Belegt, Abgeleitet und Literarische Szene trennen. Namen erst nach Bestätigung des Spielers.
- Veröffentlichten Wortlaut nur zur Korrektur eines Fehlers ändern, mit Eintrag unter „Korrekturen“. `data/events.json` ist append-only.
- Werte „pro Jahr“ aus dem Spiel gelten für ein Wirtschaftsjahr (in beiden Welten rund 91 Kalendertage), nicht für das Kalenderjahr.
- Welten nicht vermischen.
- Öffentliches Repo: keine Zugangsdaten oder privaten Dateien.

## Prüfen

```bash
node scripts/validate-data.mjs
```

Bei Monitordaten zusätzlich `node scripts/validate-monitor.mjs`. Weitere Prüfungen laufen in `.github/workflows/validate.yml`.
