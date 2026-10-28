"""Faktenblatt eines Spieljahres von Erlental aus den Spielmonitor-Sitzungen.

Usage: python scripts/erlental-fakten.py JAHR [--monitor PFAD] [--out werkstatt/erlental/fakten]

Schreibt werkstatt/erlental/fakten/JAHR.md: Namen, Linien, Fahrzeuge, Betriebe, Versorgung, Einwohner und Finanzen,
jeweils mit Spieldatum. Nur gemessene Werte, keine Deutung. Aufbau wie scripts/falkenmark-fakten.py, dazu: Umbenennungen
im Spiel (Orte, Betriebe, Halte), Halte der Linien mit Stationsnamen, Linien, die im Lauf des Jahres wieder verschwinden,
und Orte unter ihrem Namen am Ende des Jahres. Läuft nur dort, wo der Spielmonitor liegt (Rechner des Spielers); Codex und
andere Sitzungen ohne Monitor schreiben Kapitel anhand dieser Blätter.
Nur Python-Standardbibliothek.
"""
import argparse
import json
import math
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import monitor_files  # noqa: E402  (liest daten.jsonl und archivierte daten.jsonl.xz)

WORLD_ID = json.loads((ROOT/'data/monitor-sources.json').read_text(encoding='utf-8'))['saves']['erlental']['world']['world_id']


def rows_of(monitor):
    """Alle Messungen von Erlental in Aufzeichnungsreihenfolge."""
    needle = WORLD_ID.encode()
    for path in monitor_files.data_paths(Path(monitor)/'sessions'):
        with monitor_files.open_data(path) as stream:
            for raw in stream:
                if needle not in raw:
                    continue
                try:
                    row = json.loads(raw.decode('utf-8-sig'))
                except ValueError:
                    continue
                if row.get('world_id') == WORLD_ID and row.get('game_date'):
                    row['_session'] = path.parent.name
                    yield row


def canonical(rows):
    """Nur der gültige Spielverlauf: Nach einem Neuladen (Spielzeit springt zurück) fallen die Messungen weg,
    die hinter dem geladenen Stand lagen. Sie gehören zu einem verworfenen Abschnitt."""
    kept = []
    for r in rows:
        t = r.get('game_time')
        if isinstance(t, (int, float)):
            while kept and isinstance(kept[-1].get('game_time'), (int, float)) and kept[-1]['game_time'] > t:
                kept.pop()
        kept.append(r)
    return kept


def day(r):
    d = r['game_date']
    return d['year'], d['month'], d['day']


def de(t):
    return f'{t[2]}.{t[1]}.{t[0]}'


def n(x):
    return f'{x:,}'.replace(',', '.') if isinstance(x, int) else str(x)


def residents(town):
    return town.get('housing_occupied', town['population'])


def models(line):
    return ', '.join(f"{m['vehicles']} × {m['name']}" for m in line.get('vehicle_models', [])) or '–'


def stops(line):
    """Halte einer Linie mit Stationsnamen, ersatzweise mit den Orten der Halte."""
    return ', '.join(line.get('station_names') or line.get('places') or []) or '–'


def pace(rows):
    """Spielzeit je Kalendertag, gemessen von der ersten bis zur letzten Messung."""
    timed = sorted((x['game_time'], day(x)) for x in rows if isinstance(x.get('game_time'), (int, float)))
    days = (date(*timed[-1][1]) - date(*timed[0][1])).days
    return (timed[-1][0] - timed[0][0]) / days if days else float('nan')


def econ_year(rows):
    """Länge des Wirtschaftsjahres in Spielzeit: das längste Bilanzfenster einer Linie (ungekürzt nach dem ersten Jahr)."""
    return max((l['balance_end_game_time'] - l['balance_start_game_time'] for r in rows for l in r.get('lines') or []
                if isinstance(l.get('balance_start_game_time'), (int, float)) and isinstance(l.get('balance_end_game_time'), (int, float))),
               default=float('nan'))


def window(rows, r):
    """Zeitraum der Werte „pro Jahr“ (Linienbilanz, Produktion, Versand) zur Messung r.

    Das Spiel zählt ein Wirtschaftsjahr (getDefaultYearDuration), nicht das Kalenderjahr; läuft der Kalender langsamer,
    ist es kürzer als zwölf Monate. Der Beginn steht als balance_start_game_time an jeder Linie und wird hier über die
    Messung mit der nächstliegenden Spielzeit in ein Datum übersetzt."""
    starts = [l['balance_start_game_time'] for l in r['lines'] if isinstance(l.get('balance_start_game_time'), (int, float))]
    timed = [(x['game_time'], day(x)) for x in rows if isinstance(x.get('game_time'), (int, float))]
    if not starts or not timed:
        return 'unbekannt'
    begin = max(starts)
    if begin <= min(t for t, _ in timed):
        return f'seit Spielbeginn {de(min(timed)[1])}'
    since = min(timed, key=lambda p: abs(p[0] - begin))[1]
    days = (date(*day(r)) - date(*since)).days
    return f'{de(since)} bis {de(day(r))}, {days} Kalendertage = ein Wirtschaftsjahr des Spiels'


def renamed(rows, year):
    """Umbenennungen im Jahr, über die Kennung verfolgt: (erste Messung mit dem neuen Namen, Art, alter Name, neuer Name).
    Nimmt alle Messungen, auch die Grundmessungen zwischen den Detailmessungen."""
    kinds = (('Ort', lambda r: r.get('towns')), ('Betrieb', lambda r: r.get('industries')),
             ('Halt', lambda r: (r.get('logistics') or {}).get('stations')))
    found = []
    for label, items in kinds:
        names = {}
        for r in rows:
            for item in items(r) or []:
                before = names.get(item['id'])
                if before and before != item['name'] and day(r)[0] == year:
                    found.append((day(r), label, before, item['name']))
                names[item['id']] = item['name']
    return sorted(found)


def sheet(year, monitor):
    raw = list(rows_of(monitor))
    rows = canonical(raw)
    det = [r for r in rows if r.get('sample_mode') == 'detail']
    inyear = [r for r in det if day(r)[0] == year]
    if not inyear:
        raise SystemExit(f'Keine Detailmessungen für {year}.')
    prev = [r for r in det if day(r)[0] < year]
    start = prev[-1] if prev else inyear[0]
    end = inyear[-1]
    out = [f'# Erlental · Faktenblatt {year}', '',
           f'Automatisch erzeugt aus dem Spielmonitor (`scripts/erlental-fakten.py`). Nur Messwerte, keine Deutung.',
           f'Vergleich: {"letzte Detailmessung " + de(day(start)) if prev else "erste Detailmessung " + de(day(start))} '
           f'bis letzte Detailmessung {de(day(end))}. {len(inyear)} Detailmessungen aus den Sitzungen '
           f'{", ".join(sorted({r["_session"] for r in inyear}))}.', '']
    back = sum(1 for a, b in zip(raw, raw[1:]) if day(b)[0] == year and isinstance(a.get('game_time'), (int, float))
               and isinstance(b.get('game_time'), (int, float)) and b['game_time'] < a['game_time'])
    dropped = sum(1 for r in raw if day(r)[0] == year) - sum(1 for r in rows if day(r)[0] == year)
    out.append(f'Rücksprünge der Spielzeit (Neuladen) im Jahr: {back}; {dropped} Messungen aus verworfenen Abschnitten '
               'sind herausgenommen. Geladene Stände sind kein Erzählstoff.')

    out += ['', '## Namen', '', 'Umbenennungen im Spiel; Datum der ersten Messung mit dem neuen Namen:', '']
    out += [f'- {de(d)} {label}: {before} → {after}' for d, label, before, after in renamed(rows, year)] or ['- keine']

    out += ['', '## Linien', '']
    old = {l['id']: l for l in start['lines']} if prev else {}
    seen, events = {}, []
    for r in inyear:
        for l in r['lines']:
            sig = (l['name'], l['vehicles'], models(l))
            if l['id'] not in old and l['id'] not in seen:
                bought = sorted({json.dumps(m.get('purchase_first_game_date'), sort_keys=True) for m in l.get('vehicle_models', [])})
                events.append(f"- {de(day(r))} **neu gemessen:** {l['name']} ({l.get('carrier')}), {l['vehicles']} Fahrzeuge: {models(l)}; "
                              f"Halte: {stops(l)}; Kaufdatum laut Monitor: "
                              + ', '.join(de((d['year'], d['month'], d['day'])) for d in map(json.loads, bought) if d))
            elif l['id'] in seen and seen[l['id']] != sig:
                events.append(f"- {de(day(r))} {l['name']}: {seen[l['id']][1]} → {l['vehicles']} Fahrzeuge ({models(l)})"
                              + (f"; Name vorher {seen[l['id']][0]}" if seen[l['id']][0] != l['name'] else ''))
            seen[l['id']] = sig
    # Verschwunden ist, was in der letzten Messung des Jahres mit Linienliste fehlt, Grundmessungen eingeschlossen;
    # „zuletzt“ ist die letzte Messung mit der Linie. So zählen auch Linien, die nur zwischen zwei Detailmessungen bestanden.
    listed = [r for r in rows if day(r)[0] == year and r.get('lines') is not None]
    last = {lid: (None, l['name']) for lid, l in old.items()}
    for r in listed:
        for l in r['lines']:
            last[l['id']] = (day(r), l['name'])
    ids_end = {l['id'] for l in listed[-1]['lines']}
    events += [f"- **nicht mehr gemessen:** {name}" + (f" (zuletzt {de(d)})" if d else '')
               for lid, (d, name) in sorted(last.items(), key=lambda x: x[1][0] or (0, 0, 0)) if lid not in ids_end]
    out += events or ['- keine Änderungen']
    span = window(rows, end)
    out += ['', f'Linienbilanzen am {de(day(end))}, nur Fahrzeugbetrieb ohne Kaufpreise, Zeitraum {span}:', '',
            '| Linie | Träger | Fahrzeuge | Bilanz | Halte |', '|---|---|---|---:|---|']
    for l in sorted(end['lines'], key=lambda x: -(x.get('balance_year') or 0)):
        out.append(f"| {l['name']} | {l.get('carrier')} | {models(l)} | {n(l.get('balance_year'))} | {stops(l)} |")
    total = sum(l.get('balance_year') or 0 for l in end['lines'])
    fleet = Counter(m['name'] for l in end['lines'] for m in l.get('vehicle_models', []) for _ in range(m['vehicles']))
    out += ['', f"Summe der Linienbilanzen: {n(total)} · {end['line_count']} Linien · {end['vehicle_count']} Fahrzeuge "
            f"({', '.join(f'{v} {k}' for k, v in fleet.most_common())})"]

    out += ['', '## Betriebe', '']
    known = {i['id']: i['name'] for i in start['industries']} if prev else {i['id']: i['name'] for i in inyear[0]['industries']}
    for r in inyear:
        for i in r['industries']:
            if i['id'] not in known:
                known[i['id']] = i['name']
                out.append(f"- {de(day(r))} **neu:** {i['name']} ({', '.join(o['name'] for o in i['outputs'])}"
                           + (f" aus {', '.join(x['name'] for x in i['inputs'])}" if i['inputs'] else '') + ')')
    measured = [r for r in rows if day(r)[0] == year and r.get('industries')]
    ids = {i['id'] for i in measured[-1]['industries']}
    for k, v in known.items():
        if k not in ids:
            gone = max((day(r) for r in measured if any(i['id'] == k for i in r['industries'])), default=None)
            out.append(f"- **nicht mehr gemessen:** {v}" + (f" (zuletzt {de(gone)})" if gone else ''))
    first = {}
    for r in det:
        for i in r['industries']:
            for key in ('production_year', 'shipped_year'):
                if (i.get(key) or 0) > 0 and (i['id'], key) not in first:
                    first[(i['id'], key)] = de(day(r))
    lvl = {i['id']: i.get('level') for i in start['industries']}
    out += ['', f'Betriebe mit Versand, Werte „pro Jahr“ am {de(day(end))} (Zeitraum {span}; '
            '„ab“ = erste Messung seit Spielbeginn mit Wert über null):', '',
            '| Betrieb | Stufe | erzeugt | verschickt | Produktion ab | Versand ab |', '|---|---|---:|---:|---|---|']
    for i in sorted(end['industries'], key=lambda x: x['name']):
        if (i.get('shipped_year') or 0) > 0:
            stufe = f"{lvl.get(i['id'])} → {i.get('level')}" if lvl.get(i['id']) not in (None, i.get('level')) else str(i.get('level'))
            out.append(f"| {i['name']} | {stufe} | {n(i.get('production_year'))} | {n(i.get('shipped_year'))} | "
                       f"{first.get((i['id'], 'production_year'), '–')} | {first.get((i['id'], 'shipped_year'), '–')} |")
    out.append(f"\nAnzahl Betriebe: {len(start['industries'])} → {len(end['industries'])}. Werte „pro Jahr“ sind gleitend und sinken auch ohne Stillstand.")

    out += ['', '## Versorgung der Städte', '']
    had = {(t['id'], g['name']) for t in start['towns'] for d in t['supply_districts'] for g in d['goods'] if (g.get('supplied') or 0) > 0} if prev else set()
    for r in inyear:
        for t in r['towns']:
            for d in t['supply_districts']:
                for g in d['goods']:
                    k = (t['id'], g['name'])
                    if (g.get('supplied') or 0) > 0 and k not in had:
                        had.add(k)
                        out.append(f"- {de(day(r))} **erstmals versorgt:** {t['name']} mit {g['name']}, {g.get('supplied')} von {g['demand']}")
    out += ['', f'Stand {de(day(end))}:', '']
    for t in sorted(end['towns'], key=lambda x: x['name']):
        goods = [f"{g['name']} {g.get('supplied')} von {g['demand']}" for d in t['supply_districts'] for g in d['goods'] if (g.get('supplied') or 0) > 0]
        if goods:
            out.append(f"- {t['name']}: {', '.join(goods)}")

    out += ['', '## Einwohner', '']
    # Einwohner = belegte Wohnungen (housing_occupied); population ist im Monitor die Wohnkapazität.
    # Orte stehen unter ihrem Namen am Ende des Jahres, ein früherer Name in Klammern.
    p0 = {t['id']: (t['name'], residents(t)) for t in start['towns']}
    pe = {t['id']: (t['name'], residents(t)) for t in end['towns']}
    label = {k: pe[k][0] + (f' (vorher {v[0]})' if v[0] != pe[k][0] else '') for k, v in p0.items() if k in pe}
    changes = sorted(((pe[k][1] - v[1], label[k], v[1], pe[k][1]) for k, v in p0.items() if k in pe), key=lambda c: (-c[0], c[1]))
    out += [f"- {c[1]}: {c[2]} → {c[3]} ({'+' if c[0] > 0 else ''}{c[0]})" for c in changes if c[0]]
    out += [f"- unverändert: {sum(1 for c in changes if not c[0])} von {len(changes)} Orten",
            f"- zusammen: {n(sum(v[1] for v in p0.values()))} → {n(sum(v[1] for v in pe.values()))}"]
    big = sorted(end['towns'], key=lambda t: -residents(t))[:5]
    out.append(f"- größte Orte am {de(day(end))}: " + ', '.join(f"{t['name']} {residents(t)}" for t in big))

    out += ['', '## Finanzen', '']
    fin = [r for r in rows if day(r)[0] == year and r.get('finance')][-1]['finance']
    fd = fin.get('game_date') or {}
    periods = fin.get('periods') or []
    # Im laufenden Jahr reicht die Tabelle ins Vorjahr zurück; die Summe zählt nur die Quartale dieses Jahres.
    mine = [p.endswith(f'/{year % 100:02d}') for p in periods]
    if not any(mine):
        mine = [True] * len(periods)

    def year_sum(vals):
        return sum(v for v, m in zip(vals, mine) if m)

    out.append(f"Finanztabelle des Spiels, Stand {fd.get('day')}.{fd.get('month')}.{fd.get('year')}, Quartale {', '.join(periods)}:")
    out += ['', '| Posten | ' + ' | '.join(periods) + f' | Summe {year} |', '|---|' + '---:|' * (len(periods) + 1)]
    agg = {}
    for row in fin.get('rows', []):
        key = f"{row.get('type')} {row.get('carrier') or ''}".strip()
        agg[key] = [a + b for a, b in zip(agg.get(key, [0] * len(row['values'])), row['values'])]
    for title, key in (('Ergebnis', 'total'), ('Kredit aufgenommen', 'loan_borrowing'), ('Tilgung', 'loan_repayment'), ('Zinsen', 'interest')):
        vals = fin.get(key) or []
        out.append(f"| {title} | " + ' | '.join(n(v) for v in vals) + f" | {n(year_sum(vals))} |")
    for key, vals in agg.items():
        if any(vals):
            out.append(f"| {key} | " + ' | '.join(n(v) for v in vals) + f" | {n(year_sum(vals))} |")
    out.append(f"| Kontostand (Quartalsende) | " + ' | '.join(n(v) for v in fin.get('balance') or []) + ' | |')
    out.append(f"| Kredit (Quartalsende) | " + ' | '.join(n(v) for v in fin.get('loan') or []) + ' | |')
    months = {}
    for r in rows:
        if day(r)[0] == year:
            months[day(r)[1]] = (de(day(r)), r.get('money'), (r.get('finance') or {}).get('loan_now'))
    out += ['', 'Letzte Messung je Monat (Kontostand · Kredit):', '']
    out += [f"- {v[0]}: {n(v[1])} · {n(v[2])}" for _, v in sorted(months.items())]

    out += ['', '## Stationen', '']
    s0 = {s['name'] for s in start['logistics']['stations']} if prev else set()
    s1 = {s['name'] for s in end['logistics']['stations']}
    out.append('- neu: ' + (', '.join(sorted(s1 - s0)) or '–'))
    out.append('- weg: ' + (', '.join(sorted(s0 - s1)) or '–'))
    days = econ_year(rows) / pace(rows)
    out += ['', '## Hinweise zum Lesen', '',
            '- Leere Mehrzweck-Fuhrwerke meldet der Monitor mit dem Laderaum der ersten Warenart (oft „Getreide“); das ist keine Fehleinstellung.',
            '- Die Personen-Stichprobe des Monitors ist nicht repräsentativ; nicht für Geschichten verwenden.',
            '- „Neu gemessen“ heißt: zum ersten Mal in einer Messung gesehen. Das Kaufdatum steht dabei, wenn der Monitor es kennt. '
            'Bei Postkutschen neuer Linien ist es unzuverlässig; dann gilt die erste Messung der Linie.',
            '- Liniennamen entstehen nach einem Muster (Kürzel, Waren, Orte, Nummer) und ändern sich mit der Linie und mit Ortsnamen. '
            'Das Blatt verfolgt Linien über ihre Kennung.',
            '- Benennt der Spieler einen Ort um, behalten Betriebe und Halte dort ihren bisherigen Namen.',
            '- Werte „pro Jahr“ (Linienbilanz, Produktion, Versand) gelten für ein Wirtschaftsjahr des Spiels, nicht für das Kalenderjahr. '
            f'Bei diesem Kalendertempo (rund {n(round(pace(rows)))} Spielzeit-Einheiten je Tag) sind das etwa '
            f'{round(days) if math.isfinite(days) else "unbekannt viele"} Kalendertage. Für Aussagen über ein ganzes Jahr nicht verwenden.',
            f'- Die Finanztabelle rechnet nach Kalenderquartalen; „Summe {year}“ zählt nur die Quartale dieses Jahres. '
            'Ältere Quartale rechnet das Spiel später teils um (Kreditaufnahme und Tilgung verrechnet, der Saldo bleibt); '
            'Jahreswerte aus dem Blatt des Jahres nehmen.',
            '- Finanzwerte sind Stand der letzten Messung im Jahr, nicht zwingend der 31. Dezember.',
            '- Das Blatt kennt nur Detailmessungen; die Grundmessungen dazwischen zeigen manches einen bis drei Tage früher. '
            'Umbenennungen und „nicht mehr gemessen“ stammen aus allen Messungen des Jahres.']
    return '\n'.join(out) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('year', type=int)
    parser.add_argument('--monitor', default=str(ROOT.parent/'Spielmonitor'))
    parser.add_argument('--out', default=str(ROOT/'werkstatt/erlental/fakten'))
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    target = out/f'{args.year}.md'
    target.write_text(sheet(args.year, args.monitor), encoding='utf-8')
    print(f'Geschrieben: {target}')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()
