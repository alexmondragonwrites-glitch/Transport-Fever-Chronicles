"""Build the fact data of „Le Journal des Alizés“ from the local Spielmonitor sessions.

Usage: python scripts/build-journal.py [--monitor PATH] [--save ID] [--out DIR] [--notebook FILE]

Writes saves/<save>/data/journal/{meldungen,menschen,staedte,fuhrpark,notizen}.json, only when the content changed,
karte.json once the monitor measures positions (Spielmonitor revision 16, see journal_karte.py) and zeitleiste.json,
the look of every edition, from the rules in data/epochen.json and saves/<save>/data/epochen.json (see journal_epochen.py).
Everything here is derived from detail measurements of the configured world on the canonical timeline:
after a game-time rollback the replayed course replaces the abandoned branch, as in build-decade.mjs.
Names of the observed residents are invented by the editors and marked as such; all other values are measured.
notizen.json carries the player's own notes from the Spielmonitor notebook: statements of intent, not measurements.
Editorial texts (articles, interviews, portraits, advertisements) live in redaktion.json and are written by hand.
Only uses the Python standard library.
"""
import argparse
import collections
import datetime
import hashlib
import json
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import journal_epochen  # noqa: E402  the look of each edition from the rules and the canonical course
import journal_karte  # noqa: E402  sea chart from the monitor's positions
import monitor_files  # noqa: E402  daten.jsonl or its lossless archive daten.jsonl.xz

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT/'.publish-cache/journal'

# Line names follow "<Typ> <Waren>-<Orte>-<Kategorie>-<Nr>", e.g. "TP Passagiere-PordesAli-Bou-RE-1".
KINDS = {'Bus':('bus','Bus','ROAD'), 'RC':('lkw','Lastwagen','ROAD'), 'Tram':('tram','Straßenbahn','TRAM'),
         'TP':('personenzug','Personenzug','RAIL'), 'TC':('gueterzug','Güterzug','RAIL'),
         'WP':('passagierschiff','Passagierschiff','WATER'), 'WC':('frachtschiff','Frachtschiff','WATER'),
         'AP':('flugzeug','Flugzeug','AIR'), 'AC':('frachtflugzeug','Frachtflugzeug','AIR')}
CARRIER_KIND = {'ROAD':'bus', 'TRAM':'tram', 'RAIL':'personenzug', 'WATER':'frachtschiff', 'AIR':'flugzeug'}
KIND_LABEL = {v[0]:v[1] for v in KINDS.values()} | {'unbekannt':'Unbekannt'}
LINE_LABEL = {'bus':'Buslinie', 'lkw':'Lkw-Linie', 'tram':'Straßenbahnlinie', 'personenzug':'Personenzuglinie',
              'gueterzug':'Güterzuglinie', 'passagierschiff':'Passagierschifflinie', 'frachtschiff':'Frachtschifflinie',
              'flugzeug':'Fluglinie', 'frachtflugzeug':'Luftfrachtlinie', 'unbekannt':'Linie'}
ARTICLE = {'tram':'eine'}
TOWN_STEPS = (100, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 4000, 5000)
FIRST = ['Adélaïde','Amélie','Angèle','Augustine','Berthe','Céleste','Clémence','Delphine','Eugénie','Fernande','Germaine',
         'Henriette','Joséphine','Justine','Léontine','Lucienne','Marceline','Noémie','Pélagie','Philomène','Rosalie','Séraphine',
         'Solange','Victorine','Zélie','Adolphe','Alcide','Alphonse','Anatole','Aristide','Augustin','Bazile','Célestin','Clovis',
         'Désiré','Edmond','Émile','Fernand','Florentin','Gaston','Hippolyte','Isidore','Jules','Léandre','Lucien','Marius',
         'Narcisse','Octave','Prosper','Siméon','Théodore','Ulysse','Zéphir']
LAST = ['Alexandre','Baptiste','Bellance','Bonheur','Calixte','Charlery','Clément','Dacalor','Désir','Édouard','Fortuné',
        'Gaspard','Hilaire','Jean-Louis','Joseph','Laurent','Lubin','Marie-Sainte','Modeste','Nicolas','Petit-Frère','Philogène',
        'Rosemond','Saint-Cyr','Sainte-Rose','Séverin','Thélus','Valère','Zébina']
MODES = {'zu Fuß':'fuss', 'Auto':'auto', 'ÖV':'oev'}


def date(d):
    return f"{d['year']:04}-{d['month']:02}-{d['day']:02}" if d else None


def de(d):
    return f"{d[8:10]}.{d[5:7]}.{d[:4]}" if d else ''


def dumps(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'), allow_nan=False)+'\n'


def line_kind(name, carrier):
    prefix = name.split(' ', 1)[0]
    if prefix in KINDS:
        return KINDS[prefix][0]
    return CARRIER_KIND.get(carrier, 'unbekannt')


def line_goods(name):
    head = name.split('-', 1)[0]
    # The game shortens long lists to "Fisch,Holz,+1"; the counter is not a good.
    return [g for g in head.split(' ', 1)[1].split(',') if g and not g.startswith('+')] if ' ' in head else []


def model_key(m):
    # The resource file stays the same across game sessions; the numeric model ID is only a fallback.
    return m.get('model_file') or f"id:{m.get('model_id')}"


def compact_models(line):
    """[complete, [[key, name, vehicles, parts, first purchase, last purchase, available from, carrier], …]] or None before revision 15."""
    models = line.get('vehicle_models')
    if models is None:
        return None
    return [bool(line.get('vehicle_models_complete')),
            [[model_key(m), m.get('name'), m.get('vehicles') or 0, m.get('parts') or 0, date(m.get('purchase_first_game_date')),
              date(m.get('purchase_last_game_date')), m.get('available_from'), m.get('carrier')] for m in (models or [])]]


def mixed(line):
    """Vehicles of more than one carrier on a compact line, e.g. buses and trams. The monitor reports a line's carrier only
    when all its vehicles share one, and the game then names the line after either kind. Vehicle models (revision 15 on)
    carry their own carrier: exactly one there means the line's carrier was just not read."""
    if line[2] is not None or not line[3]:
        return False
    models = line[5][1] if len(line) > 5 and line[5] else []
    return len({m[7] for m in models if len(m) > 7 and m[7]}) != 1


def joined(parts):
    return ' und '.join([', '.join(parts[:-1]), parts[-1]]) if len(parts) > 2 else ' und '.join(parts)


def compact(row):
    lines = [[l['id'], l['name'], l.get('carrier'), l.get('vehicles'), l.get('places'), compact_models(l)] for l in row.get('lines', [])]
    inds = [[i['id'], i['name'], i.get('level')] for i in row.get('industries', [])]
    towns = [[t['id'], t['name'], t.get('housing_occupied')] for t in row.get('towns', [])]
    people = [[p['id'], p.get('home_town_id'), p.get('home_town_name'), MODES.get(p.get('last_move_mode')), p.get('state'),
               p.get('happiness_raw'), p.get('work_id'), p.get('line_id')] for p in (row.get('people') or {}).get('rows', [])]
    # Landmarks (revision 14 on) and noise/pollution per town feed only the epoch triggers of journal_epochen.py.
    marks = row.get('landmarks')
    lm = [[m.get('id'), m.get('name'), bool(m.get('completed'))] for m in marks if isinstance(m, dict)] if isinstance(marks, list) else None
    env = [[t['id'], t.get('noise_db'), t.get('pollution_db')] for t in row.get('towns', [])]
    return {'t':row.get('game_time'), 'd':date(row.get('game_date')), 'r':row['recorded_at'], 'money':row.get('money'),
            'vc':row.get('vehicle_count'), 'lc':row.get('line_count'), 'lines':lines, 'inds':inds,
            'towns':towns, 'td':date(row.get('towns_game_date')), 'people':people,
            'lm':lm, 'lmd':date(row.get('landmarks_game_date')), 'env':env}


def session_rows(path, world_id, cache_dir=CACHE):
    """Compact detail rows of one session plus its newest positions, cached by file size, mtime and the scripts' version."""
    stat = path.stat()
    key = {'size':stat.st_size, 'mtime_ns':stat.st_mtime_ns,
           'script':hashlib.sha256(Path(__file__).read_bytes()+Path(journal_karte.__file__).read_bytes()).hexdigest()}
    cache = cache_dir/(path.parent.name+'.json')
    try:
        cached = json.loads(cache.read_text(encoding='utf-8'))
        if cached['key'] == key:
            return cached['rows'], cached['last_towns'], cached['karte']
    except (OSError, ValueError, KeyError):
        pass
    rows, last_towns, chart = [], None, {}
    needle = world_id.encode()
    with monitor_files.open_data(path) as stream:
        remaining = monitor_files.size(path)
        while remaining:
            raw = stream.readline(remaining)
            remaining -= len(raw)
            if not raw.endswith(b'\n') or needle not in raw or b'"detail"' not in raw:
                continue
            try:
                row = json.loads(raw.decode('utf-8-sig'))
            except (ValueError, UnicodeError):
                continue
            if row.get('world_id') != world_id or row.get('sample_mode') != 'detail':
                continue
            rows.append(compact(row))
            journal_karte.collect(chart, row)
            if row.get('towns'):
                last_towns = {'d':date(row.get('towns_game_date')), 'r':row.get('towns_recorded_at'), 'towns':row['towns'],
                              'lines':[{k:l.get(k) for k in ('id','name','places','vehicles')} for l in row.get('lines', [])],
                              'industries':[{k:i.get(k) for k in ('id','name','level','producing','production_year','shipped_year')} for i in row.get('industries', [])],
                              'karte':journal_karte.latest(row)}
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({'key':key, 'rows':rows, 'last_towns':last_towns, 'karte':chart}, ensure_ascii=False), encoding='utf-8')
    return rows, last_towns, chart


def canonical(sessions):
    """One monotonic course of detail rows; a rollback drops the abandoned branch after the reloaded point."""
    rows, jumps = [], []
    for name, session in sessions:
        for row in session:
            if rows and row['t'] is not None and rows[-1]['t'] is not None and row['t'] < rows[-1]['t']:
                dropped = [r for r in rows if r['t'] > row['t']]
                rows = [r for r in rows if r['t'] <= row['t']]
                jumps.append({'session':name, 'date':row['d'], 'game_time':row['t'], 'recorded_at':row['r'],
                              'dropped_from':dropped[0]['d'] if dropped else None, 'dropped_to':dropped[-1]['d'] if dropped else None})
            row['session'] = name
            rows.append(row)
    return rows, jumps


def place_text(places):
    places = [p for p in (places or []) if p]
    unique = list(dict.fromkeys(places))
    if not unique:
        return ''
    if len(unique) == 1:
        return 'in '+unique[0]
    return 'zwischen '+joined(unique)


def detect(rows, jumps, latest_places):
    events = []

    # After a recording gap of more than a month the change happened somewhere inside the gap.
    for before, row in zip(rows, rows[1:]):
        if (datetime.date.fromisoformat(row['d'])-datetime.date.fromisoformat(before['d'])).days > 31:
            row['gap_from'] = before['d']

    def add(kind, row, title, text, refs=None, values=None, key=None):
        event = {'id':f"{kind}-{key or ''}-{row['t']}".replace('--', '-'), 'typ':kind, 'date':row['d'], 'game_time':row['t'],
                 'recorded_at':row['r'], 'titel':title, 'text':text, 'refs':refs or {}, 'werte':values or {}}
        if row.get('gap_from'):
            event['fruehestens'] = row['gap_from']
            event['text'] += f" Zeitpunkt unscharf: zwischen {de(row['gap_from'])} und {de(row['d'])} lag eine Aufzeichnungslücke."
        events.append(event)

    first = rows[0]
    add('aufzeichnung', first, 'Erste Netzaufnahme',
        f"Die erste Detailmessung verzeichnet {first['lc']} Linien mit {first['vc']} Fahrzeugen, "
        f"{len(first['inds'])} Industriebetriebe und {len(first['towns'])} Orte.",
        values={'linien':first['lc'], 'fahrzeuge':first['vc'], 'betriebe':len(first['inds']), 'orte':len(first['towns'])}, key='start')
    # Reloaded save states are a playing technique, not world history: the player does not want them in the newspaper.
    # The canonical course above still drops the abandoned branch; it is just not announced.

    lines, line_vehicles, line_missing, gone_since = {}, {}, collections.Counter(), {}
    # While a line runs vehicles of several kinds its measured name flips between them. Name changes count only when the
    # line runs one kind again, against the name it had then (named); the mix itself is news once, after three measurements.
    named, mixing, mixed_told = {}, {}, set()
    kinds_seen = set()
    inds, ind_missing = {}, collections.Counter()
    towns, town_steps, town_pending = {}, {}, {}
    last_lc, last_vc = first['lc'], first['vc']
    for l in first['lines']:
        lines[l[0]] = named[l[0]] = l
        line_vehicles[l[0]] = l[3]
        if mixed(l):
            mixing[l[0]] = {'row':first, 'line':l, 'names':[l[1]], 'runs':1}
        if l[3]:
            kinds_seen.add(line_kind(l[1], l[2]))
    for i in first['inds']:
        inds[i[0]] = i
    for t in first['towns']:
        towns[t[0]] = t
        town_steps[t[0]] = max([s for s in TOWN_STEPS if (t[2] or 0) >= s], default=0)

    for idx in range(1, len(rows)):
        prev, row, nxt = rows[idx-1], rows[idx], rows[idx+1] if idx+1 < len(rows) else None
        # Lines: a partially failed measurement must not look like a mass closure.
        if row['lines'] and len(row['lines']) >= 0.6*len(lines):
            current = {l[0]:l for l in row['lines']}
            for lid, l in current.items():
                kind = line_kind(l[1], l[2])
                places = l[4] or latest_places.get(lid)
                if lid not in lines:
                    add('linie', row, f"Neue Linie: {l[1]}",
                        f"{LINE_LABEL[kind]} {place_text(places)}, erstmals erfasst mit {l[3]} Fahrzeug{'en' if l[3] != 1 else ''}.".replace('  ', ' ').replace(' ,', ','),
                        {'line':lid}, {'art':kind, 'fahrzeuge':l[3]}, key=lid)
                    line_vehicles[lid] = l[3]
                    named[lid] = l
                elif l[1] != named[lid][1] and not mixed(l):
                    old = named[lid][1]
                    old_kind = line_kind(old, named[lid][2])
                    gained = [g for g in line_goods(l[1]) if g not in line_goods(old)]
                    lost = [g for g in line_goods(old) if g not in line_goods(l[1])]
                    if not line_goods(old):
                        title, text = 'Linie eingerichtet', f"Aus der vorläufigen Linie „{old}“ wird „{l[1]}“."
                    elif old_kind != kind and kind != 'unbekannt':
                        text = f"Die Linie „{old}“ wird als {KIND_LABEL[kind]} weitergeführt und heißt jetzt „{l[1]}“."
                        if kind not in kinds_seen and l[3]:
                            add('premiere', row, f"Premiere: {KIND_LABEL[kind]}", text, {'line':lid}, {'art':kind}, key=kind)
                            kinds_seen.add(kind)
                        title = f"Umstellung auf {KIND_LABEL[kind]}"
                    elif gained or lost:
                        parts = ([f"befördert jetzt auch {', '.join(gained)}"] if gained else [])+([f"nicht mehr {', '.join(lost)}"] if lost else [])
                        title = ' · '.join(([f"Neue Ware: {', '.join(gained)}"] if gained else [])+([f"Ware entfällt: {', '.join(lost)}"] if lost else []))
                        text = f"„{old}“ {' und '.join(parts)}; neuer Name „{l[1]}“."
                    else:
                        title, text = 'Linie neu geführt', f"„{old}“ heißt jetzt „{l[1]}“."
                    if mixing.get(lid, {}).get('runs', 0) >= 3:
                        text += f" Seit {de(mixing[lid]['row']['d'])} fuhren auf ihr Fahrzeuge verschiedener Art gemeinsam, jetzt nur noch eine."
                    add('linie-neu-gefuehrt', row, title, text, {'line':lid}, {'alt':old, 'neu':l[1], 'neue_waren':gained, 'entfallene_waren':lost}, key=lid)
                if mixed(l):
                    mix = mixing.setdefault(lid, {'row':row, 'line':l, 'names':[], 'runs':0})
                    mix['runs'] += 1
                    if l[1] not in mix['names']:
                        mix['names'].append(l[1])
                    if mix['runs'] == 3 and lid not in mixed_told:
                        mixed_told.add(lid)
                        first_mixed = mix['line']
                        models = [m for m in (first_mixed[5][1] if len(first_mixed) > 5 and first_mixed[5] else []) if m[2]]
                        fleet_text = (joined([f"{m[2]} {model_name(m[0], m[1])}" for m in models]) if models
                                      else f"{first_mixed[3]} Fahrzeug{'e' if first_mixed[3] != 1 else ''}")
                        names = list(dict.fromkeys([named[lid][1]]+mix['names']))
                        text = (f"Auf der Linie „{named[lid][1]}“ {place_text(first_mixed[4] or latest_places.get(lid))} fahren Fahrzeuge "
                                f"verschiedener Art gemeinsam: {fleet_text}.").replace('  ', ' ')
                        if len(names) > 1:
                            text += f" Die Messungen führen sie deshalb abwechselnd als {joined([f'„{n}“' for n in names])}."
                        add('linie-neu-gefuehrt', mix['row'], f"Gemischter Betrieb: {named[lid][1]}", text, {'line':lid},
                            {'gemischt':True, 'namen':names, 'fahrzeuge':first_mixed[3],
                             'modelle':[{'modell':model_name(m[0], m[1]), 'fahrzeuge':m[2], 'verkehrstraeger':m[7]} for m in models]},
                            key=f"{lid}-gemischt")
                else:
                    mixing.pop(lid, None)
                    named[lid] = l
                # A premiere needs a vehicle: a line set up before its first purchase waits for it.
                if kind not in kinds_seen and kind != 'unbekannt' and l[3]:
                    add('premiere', row, f"Premiere: {KIND_LABEL[kind]}",
                        f"Mit „{l[1]}“ fährt erstmals {ARTICLE.get(kind, 'ein')} {KIND_LABEL[kind]} der Gesellschaft {place_text(places)}.".replace('  ', ' ').replace(' .', '.'),
                        {'line':lid}, {'art':kind, 'fahrzeuge':l[3]}, key=kind)
                    kinds_seen.add(kind)
                line_missing[lid] = 0
                gone_since.pop(('line', lid), None)
                if lid in line_vehicles and l[3] is not None and line_vehicles[lid] is not None:
                    confirmed = nxt is None or any(x[0] == lid and x[3] is not None and abs(x[3]-line_vehicles[lid]) >= 3 for x in nxt['lines'])
                    if abs(l[3]-line_vehicles[lid]) >= 3 and confirmed:
                        up = l[3] > line_vehicles[lid]
                        add('flotte', row, f"{'Verstärkt' if up else 'Ausgedünnt'}: {l[1]}",
                            f"Statt {line_vehicles[lid]} fahren jetzt {l[3]} Fahrzeuge.", {'line':lid},
                            {'vorher':line_vehicles[lid], 'nachher':l[3]}, key=lid)
                        line_vehicles[lid] = l[3]
                lines[lid] = l
            for lid in list(lines):
                if lid not in current:
                    line_missing[lid] += 1
                    gone_since.setdefault(('line', lid), row)
                    if line_missing[lid] == 3:
                        add('linie-ende', gone_since.pop(('line', lid)), f"Eingestellt: {named[lid][1]}",
                            f"Die Linie fehlt ab dieser Messung dauerhaft im Netz; zuletzt mit {lines[lid][3]} Fahrzeugen.",
                            {'line':lid}, key=lid)
                        del lines[lid], named[lid]
                        mixing.pop(lid, None)
                        mixed_told.discard(lid)
        # Industries
        if row['inds'] and len(row['inds']) >= 0.6*len(inds):
            current = {i[0]:i for i in row['inds']}
            for iid, i in current.items():
                if iid not in inds:
                    add('industrie', row, f"Neugründung: {i[1]}", f"Ein neuer Betrieb erscheint im Industrieregister (Stufe {i[2]}).",
                        {'industry':iid}, {'stufe':i[2]}, key=iid)
                elif i[2] != inds[iid][2] and i[2] is not None and inds[iid][2] is not None:
                    add('ausbau', row, f"{'Ausbau' if i[2] > inds[iid][2] else 'Rückbau'}: {i[1]}",
                        f"Die Betriebsstufe ändert sich von {inds[iid][2]} auf {i[2]}.", {'industry':iid},
                        {'vorher':inds[iid][2], 'nachher':i[2]}, key=iid)
                ind_missing[iid] = 0
                gone_since.pop(('industry', iid), None)
                inds[iid] = i
            for iid in list(inds):
                if iid not in current:
                    ind_missing[iid] += 1
                    gone_since.setdefault(('industry', iid), row)
                    if ind_missing[iid] == 3:
                        add('industrie-ende', gone_since.pop(('industry', iid)), f"Geschlossen: {inds[iid][1]}", 'Der Betrieb fehlt ab dieser Messung dauerhaft im Industrieregister.',
                            {'industry':iid}, key=iid)
                        del inds[iid]
        # Towns: milestones need two consecutive town updates above the threshold.
        if row['towns'] and row['td'] != prev['td']:
            for t in row['towns']:
                if t[0] not in towns:
                    towns[t[0]] = t
                    town_steps[t[0]] = max([s for s in TOWN_STEPS if (t[2] or 0) >= s], default=0)
                    continue
                if t[1] != towns[t[0]][1]:
                    add('umbenennung', row, f"Aus {towns[t[0]][1]} wird {t[1]}", f"Der Ort heißt in den Messungen ab {de(row['td'])} {t[1]}.",
                        {'town':t[0]}, {'alt':towns[t[0]][1], 'neu':t[1]}, key=t[0])
                step = max([s for s in TOWN_STEPS if (t[2] or 0) >= s], default=0)
                if step > town_steps.get(t[0], 0):
                    if town_pending.get(t[0]) == step:
                        add('stadt', row, f"{t[1]} zählt {step:,} Einwohner".replace(',', '.'),
                            f"Belegter Wohnraum am {de(row['td'])}: {t[2]:,}.".replace(',', '.'), {'town':t[0]}, {'schwelle':step, 'wert':t[2]}, key=t[0])
                        town_steps[t[0]] = step
                    else:
                        town_pending[t[0]] = step
                else:
                    town_pending.pop(t[0], None)
                towns[t[0]] = t
        # Network milestones
        for value, last, unit, steps in ((row['lc'], last_lc, 'Linien', 10), (row['vc'], last_vc, 'Fahrzeuge', 50)):
            if value is not None and last is not None and value // steps > last // steps and value >= 50:
                mark = value//steps*steps
                add('netz', row, f"Das Netz zählt {mark} {unit}", f"Gemessen: {value} {unit} am {de(row['d'])}.", values={'wert':value}, key=f"{unit}-{mark}")
        last_lc = row['lc'] if row['lc'] is not None else last_lc
        last_vc = row['vc'] if row['vc'] is not None else last_vc
    detect_models(rows, add)
    events.sort(key=lambda e:(e['game_time'] or 0, e['id']))
    return events


def model_rows(rows):
    """Detail rows that carry vehicle models (Spielmonitor revision 15 or later)."""
    return [r for r in rows if any(len(l) > 5 and l[5] is not None for l in r['lines'])]


def model_name(key, name):
    return name or key.rsplit('/', 1)[-1].removesuffix('.mdl')


def detect_models(rows, add):
    """A model is news when it appears after the first measurement with model data.
    That first measurement is the baseline: its models were already there when the recording began."""
    known, base = set(), None
    for row in model_rows(rows):
        captured = [l for l in row['lines'] if len(l) > 5 and l[5] is not None]
        if base is None:
            base = {'d':row['d'], 'complete':len(captured) == len(row['lines']) and all(l[5][0] for l in captured)}
            known.update(m[0] for l in captured for m in l[5][1])
            continue
        new = collections.defaultdict(list)
        for l in captured:
            for m in l[5][1]:
                if m[0] not in known:
                    new[m[0]].append((l, m))
        for key, uses in new.items():
            known.add(key)
            name = model_name(key, next((m[1] for _, m in uses if m[1]), None))
            bought = min((m[4] for _, m in uses if m[4]), default=None)
            # An incomplete baseline may have missed older vehicles: only a purchase after it proves a newcomer.
            if not base['complete'] and (bought is None or bought < base['d']):
                continue
            vehicles, parts = sum(m[2] for _, m in uses), sum(m[3] for _, m in uses)
            line = max(uses, key=lambda u:u[1][2])[0]
            kind = line_kind(line[1], line[2])
            where = (f"auf der {LINE_LABEL[kind]} „{line[1]}“ {place_text(line[4])}".rstrip() if len(uses) == 1
                     else f"auf {len(uses)} Linien, darunter „{line[1]}“")
            text = (f"„{name}“ ist erstmals im Linienbetrieb der Gesellschaft: {vehicles} Fahrzeug{'e' if vehicles != 1 else ''}"
                    + (f" mit {parts} Einheiten dieses Modells" if parts != vehicles else '') + f" {where}.")
            if bought:
                text += f" Erstes Exemplar laut Spiel gekauft am {de(bought)}."
            add('modell', row, f"Neues Fahrzeugmodell: {name}", text, {'line':line[0], 'lines':[l[0] for l, _ in uses]},
                {'art':kind, 'modell':name, 'datei':key, 'fahrzeuge':vehicles, 'einheiten':parts, 'gekauft':bought},
                key=re.sub(r'[^A-Za-z0-9]+', '-', key).strip('-'))


def fictional_name(pid):
    h = int(hashlib.sha256(f'alizes-{pid}'.encode()).hexdigest(), 16)
    return f"{FIRST[h % len(FIRST)]} {LAST[(h // len(FIRST)) % len(LAST)]}"


def people(rows, town_names, line_names):
    persons = {}
    cohort = collections.defaultdict(lambda:collections.Counter())
    for row in rows:
        year = row['d'][:4]
        for pid, town_id, town, mode, state, happy, work, line in row['people']:
            p = persons.setdefault(pid, {'id':pid, 'name':fictional_name(pid), 'first':row['d'], 'years':{}, 'moments':[],
                                         '_mode':None, '_work':None, '_town':town_id})
            p['last'] = row['d']
            y = p['years'].setdefault(year, {'fuss':0, 'auto':0, 'oev':0, 'messungen':0, 'arbeit':0, '_h':[]})
            y['messungen'] += 1
            if mode:
                y[mode] += 1
                cohort[year][mode] += 1
            if work not in (None, -1):
                y['arbeit'] += 1
            if happy is not None:
                y['_h'].append(happy)
            if mode == 'oev' and not any(m['typ'] == 'erste-oev-fahrt' for m in p['moments']):
                p['moments'].append({'typ':'erste-oev-fahrt', 'date':row['d'], 'text':'Erste beobachtete Fahrt mit dem öffentlichen Verkehr'
                                     + (f" (Linie „{line_names[line]}“)" if line in line_names else '')})
            if mode == 'auto' and not any(m['typ'] == 'erstes-auto' for m in p['moments']):
                p['moments'].append({'typ':'erstes-auto', 'date':row['d'], 'text':'Erster beobachteter Weg mit dem Auto'})
            employed = work not in (None, -1)
            if p['_work'] is not None and employed != p['_work']:
                p['moments'].append({'typ':'arbeit' if employed else 'ohne-arbeit', 'date':row['d'],
                                     'text':'Hat wieder einen Arbeitsplatz' if employed else 'Kein Arbeitsplatz mehr erfasst'})
            known = town_id in town_names or town
            if p['_town'] != town_id and known:
                p['moments'].append({'typ':'umzug', 'date':row['d'], 'text':f"Neuer Wohnort: {town_names.get(town_id, town)}"})
            p['_work'] = employed
            if known:
                p['_town'] = town_id
                p['home_town_id'], p['home_town'] = town_id, town_names.get(town_id, town)
            p['latest'] = {'date':row['d'], 'modus':mode, 'zustand':state, 'zufriedenheit':happy, 'arbeit':employed,
                           'linie':line_names.get(line) if line not in (None, -1) else None}
    end = rows[-1]['d']
    for p in persons.values():
        p['ausgeschieden'] = p['last'] != end
        if p['ausgeschieden']:
            p['moments'].append({'typ':'ausgeschieden', 'date':p['last'], 'text':'Letzte Messung: danach nicht mehr in der Beobachtungsgruppe'})
        for y in p['years'].values():
            h = y.pop('_h')
            y['zufriedenheit'] = round(sum(h)/len(h), 3) if h else None
        for k in ('_mode', '_work', '_town'):
            p.pop(k)
        # Job changes flicker between trips; keep only the first and last two to stay readable.
        jobs = [m for m in p['moments'] if m['typ'] in ('arbeit', 'ohne-arbeit')]
        if len(jobs) > 4:
            p['moments'] = [m for m in p['moments'] if m not in jobs[2:-2]]
            p['arbeitswechsel'] = len(jobs)
    return sorted(persons.values(), key=lambda p:(p['home_town'] or '', p['name'])), {y:dict(c) for y, c in sorted(cohort.items())}


def towns_data(rows, last, lines_now, industries_now):
    names, series, former = {}, collections.defaultdict(dict), collections.defaultdict(list)
    for row in rows:
        if not row['towns']:
            continue
        for tid, name, housing in row['towns']:
            if tid in names and names[tid] != name:
                former[tid].append({'name':names[tid], 'bis':row['td']})
            names[tid] = name
            if housing is not None and row['td']:
                series[tid][row['td'][:7]] = housing
    out = []
    for t in last['towns']:
        tid = t['id']
        months = sorted(series[tid].items())
        served = [{'id':l['id'], 'name':l['name'], 'fahrzeuge':l.get('vehicles')} for l in lines_now if t['name'] in (l.get('places') or [])]
        local = [{'id':i['id'], 'name':i['name'], 'stufe':i.get('level'), 'aktiv':i.get('producing'), 'produktion_jahr':i.get('production_year')}
                 for i in industries_now if i['name'].startswith(t['name']+' ')]
        goods = []
        for district in t.get('supply_districts') or []:
            for g in district.get('goods') or []:
                goods.append({'bereich':district.get('name'), 'ware':g.get('name'), 'bedarf':g.get('demand'), 'gedeckt':g.get('supplied')})
        out.append({'id':tid, 'name':t['name'], 'frueher':former.get(tid, []),
                    'verlauf':[{'monat':m, 'einwohner':v} for m, v in months],
                    'erste_messung':months[0][0] if months else None, 'einwohner':t.get('housing_occupied'),
                    'wohnkapazitaet':t.get('housing_capacity'), 'arbeitsplaetze':(t.get('jobs_private') or 0)+(t.get('jobs_public') or 0),
                    'geschaefte':(t.get('shops_private') or 0)+(t.get('shops_public') or 0), 'flaeche_km2':t.get('area_square_km'),
                    'laerm_db':t.get('noise_db'), 'verschmutzung_roh':t.get('pollution_db'), 'netzanteil_prozent':t.get('line_usage_percent'),
                    'bedarf':t.get('demand'), 'gedeckt':t.get('supplied'), 'waren':goods, 'linien':served, 'betriebe':local})
    return sorted(out, key=lambda t:-(t['einwohner'] or 0))


def fleet(rows, latest_lines):
    months = {}
    premieres = {}
    for row in rows:
        if not row['lines']:
            continue
        by = collections.Counter()
        count = collections.Counter()
        for lid, name, carrier, vehicles, places, *_ in row['lines']:
            kind = line_kind(name, carrier)
            by[kind] += vehicles or 0
            count[kind] += 1
            if kind != 'unbekannt' and vehicles:
                premieres.setdefault(kind, {'art':kind, 'bezeichnung':KIND_LABEL[kind], 'date':row['d'], 'linie':name, 'line':lid})
        months[row['d'][:7]] = {'monat':row['d'][:7], 'fahrzeuge':dict(by), 'linien':dict(count), 'gesamt_fahrzeuge':row['vc'],
                                'gesamt_linien':row['lc'], 'kasse':row['money']}
        captured = {m[0] for l in row['lines'] if len(l) > 5 and l[5] is not None for m in l[5][1]}
        if captured:
            months[row['d'][:7]]['modelle'] = len(captured)
    first_date = rows[0]['d']
    out = {'arten':[{'art':k, 'bezeichnung':v} for k, v in KIND_LABEL.items()],
           'premieren':sorted([p | {'seit_beginn':p['date'] == first_date} for p in premieres.values()], key=lambda p:p['date']),
           'verlauf':list(months.values()),
           'groesste':[{'id':l['id'], 'name':l['name'], 'art':line_kind(l['name'], None), 'fahrzeuge':l.get('vehicles'), 'orte':l.get('places') or []}
                       for l in sorted(latest_lines, key=lambda l:-(l.get('vehicles') or 0))[:12]],
           'hinweis':'Fahrzeugmodelle (Typenbezeichnungen) erfasst der Monitor bisher nicht; die Arten stammen aus dem Linienpräfix bzw. Verkehrsträger.'}
    models = fleet_models(rows)
    if models:
        out['modelle'] = models
        out['hinweis'] = (f"Arten aus dem Linienpräfix bzw. Verkehrsträger. Fahrzeugmodelle (Typenbezeichnung laut Spiel, je Fahrzeugteil) "
                          f"erfasst der Monitor seit {de(models['erfasst_seit'])}; frühere Modelle und Wechsel sind nicht belegt.")
    return out


def fleet_models(rows):
    """Models per kind in the latest measurement with model data; None for recordings before revision 15."""
    found = model_rows(rows)
    if not found:
        return None
    first, last = found[0], found[-1]
    first_seen = {}
    for row in found:
        for l in row['lines']:
            for m in (l[5][1] if len(l) > 5 and l[5] is not None else []):
                first_seen.setdefault(m[0], row['d'])
    kinds = collections.defaultdict(dict)
    captured = [l for l in last['lines'] if len(l) > 5 and l[5] is not None]
    for l in captured:
        kind = line_kind(l[1], l[2])
        for key, name, vehicles, parts, bought_first, bought_last, available, *_ in l[5][1]:
            e = kinds[kind].setdefault(key, {'modell':model_name(key, name), 'datei':key, 'fahrzeuge':0, 'einheiten':0, 'linien':0,
                                             'kauf_erstes':None, 'kauf_letztes':None, 'verfuegbar_ab':available,
                                             'erstmals':first_seen[key], 'seit_beginn':first_seen[key] == first['d']})
            e['fahrzeuge'] += vehicles
            e['einheiten'] += parts
            e['linien'] += 1
            e['kauf_erstes'] = min([d for d in (e['kauf_erstes'], bought_first) if d], default=None)
            e['kauf_letztes'] = max([d for d in (e['kauf_letztes'], bought_last) if d], default=None)
    order = list(KIND_LABEL)
    return {'stand':last['d'], 'erfasst_seit':first['d'], 'anzahl':len({k for models in kinds.values() for k in models}),
            'vollstaendig':len(captured) == len(last['lines']) and all(l[5][0] for l in captured),
            'je_art':[{'art':k, 'bezeichnung':KIND_LABEL[k], 'modelle':sorted(kinds[k].values(), key=lambda e:(-e['fahrzeuge'], e['modell']))}
                      for k in sorted(kinds, key=order.index)]}


def notebook(path, world_id):
    """Notes of the player for this world from the Spielmonitor notebook (history/notizbuch.jsonl).
    Only notes released for the newspaper; text and game date stay exactly as the player wrote them."""
    try:
        raw = path.read_text(encoding='utf-8-sig')
    except FileNotFoundError:
        return []
    notes = []
    for line in raw.splitlines():
        try:
            n = json.loads(line)
        except ValueError:
            continue
        if not isinstance(n, dict) or n.get('world_id') != world_id or n.get('public') is False or not n.get('id'):
            continue
        text, day = n.get('text'), n.get('game_date')
        if not isinstance(text, str) or not text.strip() or not isinstance(day, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', day):
            continue
        game_time = n.get('game_time') if isinstance(n.get('game_time'), (int, float)) else None
        notes.append({'id':str(n['id']), 'date':day, 'game_time':game_time, 'text':text.strip(), '_order':n.get('recorded_at') or ''})
    notes.sort(key=lambda n:(n['game_time'] if n['game_time'] is not None else -1, n['_order'], n['id']))
    for n in notes:
        del n['_order']
    return notes


def write(path, obj):
    content = dumps(obj)
    if path.exists() and path.read_text(encoding='utf-8') == content:
        return False
    path.write_text(content, encoding='utf-8')
    return True


def build(monitor, save, out=None, cache_dir=CACHE, notes_path=None, epochen=None):
    """epochen: (template, world file) of the epoch rules; None reads data/epochen.json and saves/<save>/data/epochen.json,
    () builds without rules (no zeitleiste.json)."""
    config = json.loads((ROOT/'data/monitor-sources.json').read_text(encoding='utf-8'))['saves'][save]
    world_id = config['world']['world_id']
    sessions, last_towns, charts = [], None, []
    for path in monitor_files.data_paths(monitor/'sessions'):
        rows, last, chart = session_rows(path, world_id, cache_dir)
        charts.append(chart)
        if rows:
            sessions.append((path.parent.name, rows))
            last_towns = last or last_towns
    rows, jumps = canonical(sessions)
    if not rows:
        raise SystemExit(f'Keine Detailmessungen für {world_id} gefunden.')
    latest_places = {l['id']:l.get('places') for l in last_towns['lines']}
    town_names = {t['id']:t['name'] for t in last_towns['towns']}
    line_names = {}
    for row in rows:
        for l in row['lines']:
            line_names[l[0]] = l[1]
    stand = {'date':rows[-1]['d'], 'recorded_at':rows[-1]['r'], 'messungen':len(rows), 'zeitspruenge':len(jumps)}
    persons, cohort = people(rows, town_names, line_names)
    out = Path(out) if out else ROOT/'saves'/save/'data/journal'
    out.mkdir(parents=True, exist_ok=True)
    files = {
        'meldungen.json':{'schema_version':1, 'stand':stand, 'quelle':'Detailmessungen des Spielmonitors, kanonischer Verlauf',
                          'meldungen':detect(rows, jumps, latest_places)},
        'menschen.json':{'schema_version':1, 'stand':stand,
                         'hinweis':'Feste, nicht repräsentative Beobachtungsgruppe des Monitors. Namen sind von der Redaktion erfunden; '
                                   'Wohnort, Verkehrsmittel, Arbeitsplatz und Zufriedenheitsrohwert (0–1, Skala nicht validiert) sind gemessen.',
                         'jahre':cohort, 'personen':persons},
        'staedte.json':{'schema_version':1, 'stand':stand | {'staedtestand':last_towns['d']}, 'staedte':towns_data(rows, last_towns, last_towns['lines'], last_towns['industries'])},
        'fuhrpark.json':{'schema_version':1, 'stand':stand} | fleet(rows, last_towns['lines']),
        # No measurement stand here: the file changes only when the notes change.
        'notizen.json':{'schema_version':1, 'quelle':'Notizbuch des Spielmonitors, für die Zeitung freigegebene Notizen dieser Welt',
                        'hinweis':'Notizen des Spielers, des Direktors der Société, beim Spielen: Absichten und Erklärungen. '
                                  'Sie gelten als Spielervorgabe, nicht als Messwert. Datum = Spieldatum der letzten Messung beim Schreiben.',
                        'notizen':notebook(Path(notes_path) if notes_path else monitor/'history/notizbuch.jsonl', world_id)},
    }
    lists = {'meldungen.json':'meldungen', 'menschen.json':'personen', 'staedte.json':'staedte', 'fuhrpark.json':'verlauf', 'notizen.json':'notizen'}
    # The sea chart exists only once the monitor measured positions; before that nothing changes here.
    chart = journal_karte.chart(charts, last_towns, stand, line_kind, line_goods)
    if chart:
        files['karte.json'], lists['karte.json'] = chart, 'staedte'
    # The epochs exist only with a rules file; without one every other file stays exactly as before.
    paths = (ROOT/'data/epochen.json', ROOT/'saves'/save/'data/epochen.json') if epochen is None else tuple(epochen)
    rules = journal_epochen.load(*paths) if paths else None
    stale = []
    if rules:
        files['zeitleiste.json'] = journal_epochen.zeitleiste(rules, rows, files['meldungen.json']['meldungen'], stand, line_kind, KIND_LABEL)
        lists['zeitleiste.json'] = 'stufen'
    elif (out/'zeitleiste.json').exists():
        # Rules removed: the journal returns to its first look, so an old timeline must not linger.
        (out/'zeitleiste.json').unlink()
        stale.append('zeitleiste.json')
    changed = [name for name, obj in files.items() if write(out/name, obj)]+stale
    return changed, stand, {k:len(files[k][key]) for k, key in lists.items()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--monitor', default=str(ROOT.parent/'Spielmonitor'))
    parser.add_argument('--save', default='archipel-des-alizes')
    parser.add_argument('--out', help='anderer Zielordner, z. B. für Tests (Standard: saves/<save>/data/journal)')
    parser.add_argument('--notebook', help='anderes Notizbuch (Standard: <monitor>/history/notizbuch.jsonl)')
    args = parser.parse_args()
    changed, stand, sizes = build(Path(args.monitor).resolve(), args.save, args.out, notes_path=args.notebook)
    print(json.dumps({'stand':stand, 'eintraege':sizes, 'geaendert':changed}, ensure_ascii=False))
