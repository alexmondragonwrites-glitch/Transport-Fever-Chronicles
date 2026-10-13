"""Sea chart of the archipelago for „Le Journal des Alizés“: data/journal/karte.json from Spielmonitor positions.

Positions exist from Spielmonitor mod revision 16 on. A detail measurement carries `geo` every ten real minutes
(centre of the game's bounding volume, as the game's own town and industry windows use it) and `terrain`, a coarse
height grid, about once an hour. Without positions build-journal.py writes no karte.json and the journal stays as before.
The stop order of a line is `station_group_ids`, measured in every detail row; lines are drawn as straight legs
between their stops, not along tracks or roads. Only uses the Python standard library.
"""
import collections

# Assumption until compared with the game's map: world y grows to the north, so it is drawn upwards.
Y_NACH_OBEN = True
NORD_GEPRUEFT = False  # set True once a live chart has been compared with the game's map
GEO_LISTS = ('towns', 'industries', 'station_groups', 'landmarks')


def _date(d):
    return f"{d['year']:04}-{d['month']:02}-{d['day']:02}" if isinstance(d, dict) and d.get('year') else None


def _number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def collect(found, row):
    """Keep the newest positions and the newest complete height grid of one session (rows in recording order)."""
    geo = row.get('geo')
    if isinstance(geo, dict):
        found['geo'] = {'d':_date(geo.get('game_date')) or _date(row.get('game_date')),
                        'r':row.get('geo_recorded_at') or row.get('recorded_at'), 'geo':geo}
    terrain = row.get('terrain')
    if isinstance(terrain, dict) and terrain.get('complete') and terrain.get('heights'):
        found['terrain'] = {'d':_date(row.get('game_date')), 'r':row.get('recorded_at'), 'terrain':terrain}


def latest(row):
    """What the chart needs from the newest detail row beyond build-journal's town summary: stop order, goods, flows."""
    lines = [{'id':l['id'], 'carrier':l.get('carrier'), 'halte':l.get('station_group_ids') or [],
              'haltnamen':l.get('station_names') or [],
              'waren':[c.get('name') for c in (l.get('cargo') or []) if isinstance(c, dict) and not c.get('passenger') and c.get('name')]}
             for l in row.get('lines', [])]
    names = lambda items: [c.get('name') for c in (items or []) if isinstance(c, dict) and c.get('name')]
    industries = [{'id':i['id'], 'rohstoffe':names(i.get('inputs')), 'erzeugnisse':names(i.get('outputs'))} for i in row.get('industries', [])]
    landmarks = [{'id':m['id'], 'name':m.get('name'), 'fertig':m.get('completed'), 'stufe':m.get('level'), 'stufen':m.get('max_level'),
                  'stadt':m.get('town_name')} for m in (row.get('landmarks') or []) if isinstance(m, dict)]
    return {'lines':lines, 'industries':industries, 'landmarks':landmarks, 'warenwege':flows(row)}


def flows(row):
    """Goods on board at the moment of the measurement: source industry, drop-off point and the lines of the journey.
    While on board the cargo's target is the station group where it leaves the vehicle (checked against live data),
    rarely a town or industry. A bounded sample of the monitor (logistics.cargo), not the full traffic."""
    log = row.get('logistics')
    if not isinstance(log, dict):
        return None
    owners = {}
    for station in log.get('stations') or []:
        for c in station.get('catchables') or []:
            if isinstance(c, dict) and c.get('industry_id') is not None:
                owners[c['id']] = c['industry_id']
    groups = {g for l in row.get('lines', []) for g in (l.get('station_group_ids') or [])}
    cargo_names = {c['id']:c['name'] for l in row.get('lines', []) for c in (l.get('cargo') or []) if isinstance(c, dict) and 'id' in c}
    count, chains, items = collections.Counter(), {}, log.get('cargo') or []
    for item in items:
        source, target = item.get('source_industry_id'), item.get('target_id')
        town = item.get('target_town_id')
        industry = owners.get(target) if town is None else None
        stop = target if town is None and industry is None and target in groups else None
        if source is None or (town is None and industry is None and stop is None):
            continue
        key = (source, town, industry, stop, item.get('cargo_id'))
        count[key] += 1
        if key not in chains:
            hops = [h.get('line_id') for h in item.get('hops') or [] if isinstance(h, dict)]
            chains[key] = [l for i, l in enumerate(hops) if l is not None and (i == 0 or l != hops[i-1])]
    ways = [{'von':s, 'stadt':t, 'betrieb':i, 'halt':h, 'ware':cargo_names.get(c) or f'Ware {c}', 'anzahl':n, 'linien':chains[(s, t, i, h, c)]}
            for (s, t, i, h, c), n in sorted(count.items(), key=lambda e:(-e[1], str(e[0])))]
    return {'stand':_date(row.get('game_date')), 'stichprobe':len(items), 'gekappt':bool(log.get('cargo_truncated') or log.get('truncated')), 'wege':ways}


def _grid(found):
    """Newest complete height grid whose shape matches its declared size, else None."""
    for f in reversed(found):
        t = (f.get('terrain') or {}).get('terrain')
        if not t:
            continue
        heights, cols, rows = t.get('heights'), t.get('cols'), t.get('rows')
        if not (isinstance(heights, list) and len(heights) == rows and all(isinstance(r, list) and len(r) == cols for r in heights)):
            continue
        if not all(_number(t.get(k)) for k in ('min_x', 'min_y', 'max_x', 'max_y', 'cell_m')):
            continue
        return {'stand':f['terrain']['d'], 'min_x':t['min_x'], 'min_y':t['min_y'], 'max_x':t['max_x'], 'max_y':t['max_y'],
                'zelle_m':t['cell_m'], 'spalten':cols, 'zeilen':rows,
                'bezug':'wasserspiegel' if t.get('height_reference') == 'water_level' else 'absolut', 'hoehen':heights}
    return None


def chart(found, last, stand, line_kind, line_goods):
    """karte.json content, or None when no session carries positions yet."""
    geos = [f['geo'] for f in found if f.get('geo')]
    if not geos:
        return None
    pos = {k:{} for k in GEO_LISTS}
    for g in geos:  # sessions in recording order: the newest measurement of an object wins
        for kind in GEO_LISTS:
            items = g['geo'].get(kind)
            for p in items if isinstance(items, list) else []:
                if isinstance(p, dict) and _number(p.get('x')) and _number(p.get('y')):
                    pos[kind][p['id']] = p
    newest = geos[-1]
    extra = last.get('karte') or {'lines':[], 'industries':[], 'landmarks':[], 'warenwege':None}
    missing = collections.Counter()

    def at(kind, oid):
        p = pos[kind].get(oid)
        if not p:
            missing[kind] += 1
        return p

    towns = []
    for t in last['towns']:
        p = at('towns', t['id'])
        if p:
            area = [p[k] for k in ('min_x', 'min_y', 'max_x', 'max_y')] if all(_number(p.get(k)) for k in ('min_x', 'min_y', 'max_x', 'max_y')) else None
            towns.append({'id':t['id'], 'name':t['name'], 'x':p['x'], 'y':p['y'], 'ausdehnung':area, 'einwohner':t.get('housing_occupied')})
    goods = {i['id']:i for i in extra['industries']}
    industries = []
    for i in last['industries']:
        p = at('industries', i['id'])
        if p:
            state = 'aktiv' if i.get('producing') is True else 'gestoppt' if i.get('producing') is False else 'ungeprueft'
            industries.append({'id':i['id'], 'name':i['name'], 'x':p['x'], 'y':p['y'], 'stufe':i.get('level'), 'status':state,
                               'produktion_jahr':i.get('production_year'), 'versand_jahr':i.get('shipped_year'),
                               'rohstoffe':goods.get(i['id'], {}).get('rohstoffe', []), 'erzeugnisse':goods.get(i['id'], {}).get('erzeugnisse', [])})
    by_line = {l['id']:l for l in extra['lines']}
    lines, stop_names = [], {}
    for l in last['lines']:
        e = by_line.get(l['id'], {})
        for gid, name in zip(e.get('halte', []), e.get('haltnamen', [])):
            stop_names.setdefault(gid, name)
        lines.append({'id':l['id'], 'name':l['name'], 'art':line_kind(l['name'], e.get('carrier')), 'fahrzeuge':l.get('vehicles'),
                      'halte':e.get('halte', []), 'waren':e.get('waren') or line_goods(l['name'])})
    stations = []
    for gid in sorted({g for l in lines for g in l['halte']}):
        p = at('station_groups', gid)
        if p:
            stations.append({'id':gid, 'name':p.get('name') or stop_names.get(gid) or f'Halt {gid}', 'x':p['x'], 'y':p['y']})
    landmarks = []
    for m in extra['landmarks']:
        p = at('landmarks', m['id'])
        if p:
            landmarks.append(m | {'x':p['x'], 'y':p['y']})
    bounds = newest['geo'].get('map') if isinstance(newest['geo'].get('map'), dict) else {}
    if not all(_number(bounds.get(k)) for k in ('min_x', 'min_y', 'max_x', 'max_y')):
        # Without the terrain box the chart frames everything it knows, with a margin.
        xs = [p['x'] for kind in GEO_LISTS for p in pos[kind].values()]
        ys = [p['y'] for kind in GEO_LISTS for p in pos[kind].values()]
        pad = max(max(xs)-min(xs), max(ys)-min(ys), 1000)*0.06
        bounds = {'min_x':min(xs)-pad, 'min_y':min(ys)-pad, 'max_x':max(xs)+pad, 'max_y':max(ys)+pad}
    return {'schema_version':1,
            'stand':{'date':stand['date'], 'positionen':newest['d'], 'positionen_erfasst':newest['r'],
                     'vollstaendig':bool(newest['geo'].get('complete')) and not missing},
            'hinweis':('Positionen misst der Spielmonitor seit Revision 16 alle zehn Minuten Echtzeit: Mittelpunkt der Begrenzungsbox '
                       'wie in den Stadt- und Industriefenstern des Spiels. Linien sind als Luftlinie zwischen ihren Halten in Haltefolge '
                       'gezeichnet, nicht als Gleis- oder Straßenverlauf. Küsten und Tiefen stammen aus einem groben Höhenraster.'),
            'y_nach_oben':Y_NACH_OBEN, 'nord_geprueft':NORD_GEPRUEFT,
            'grenze':{k:bounds[k] for k in ('min_x', 'min_y', 'max_x', 'max_y')},
            'gelaende':_grid(found),
            'staedte':sorted(towns, key=lambda t:t['id']), 'betriebe':sorted(industries, key=lambda i:i['id']),
            'stationen':stations, 'linien':sorted(lines, key=lambda l:l['id']), 'wahrzeichen':sorted(landmarks, key=lambda m:m['id']),
            'warenwege':extra.get('warenwege'),
            'fehlend':{'staedte':missing['towns'], 'betriebe':missing['industries'], 'stationen':missing['station_groups'],
                       'wahrzeichen':missing['landmarks']}}
