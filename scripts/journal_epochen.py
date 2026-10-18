"""Epochs of „Le Journal des Alizés“: data/journal/zeitleiste.json, the look of every edition from events of the world.

Rules: data/epochen.json is the template for all worlds; saves/<save>/data/epochen.json may override single stages,
features, sections and states for one world. Place names, lines and years live only in these files, never here.
A stage (Stufe) changes the month its trigger (ausloeser) happens, not before January of `fruehestens` and at the
latest in January of `spaetestens`; stages follow each other in their order. Features (Merkmale) such as the headline
type or the masthead take a value per stage or with a trigger of their own, so the paper changes bit by bit.
A state (Zustand) such as `krisenpapier` comes and goes with the cash of the Société and overlays the stages.

zeitleiste() evaluates the rules on the canonical course of build-journal.py (detail rows after rollbacks, events of
meldungen.json): same measurements, same timeline. Each reached step names its occasion, a measured event (ID) or
value, or says that it came at the latest year the rules allow. Without a template file nothing is written.
Only uses the Python standard library.
"""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MONATE = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
SLUG = re.compile(r'[a-z][a-z0-9-]*')
TRIGGERS = {  # trigger kind: (required numeric/text parameters, optional parameters)
    'premiere':({'fahrzeugart'}, set()), 'modell':({'baujahr_ab'}, {'fahrzeugart'}), 'stadt':({'einwohner_ab'}, {'stadt'}),
    'netz':(set(), {'fahrzeuge_ab', 'linien_ab'}), 'kasse':({'ab'}, set()), 'wahrzeichen':(set(), {'id'}),
    'umwelt':(set(), {'laerm_ab', 'verschmutzung_ab', 'stadt'}), 'meldung':({'typ'}, {'muster'})}
FORMS = {'programm'}


class RulesError(SystemExit):
    pass


def lang(day):
    """13. Dezember 1918"""
    return f"{int(day[8:10])}. {MONATE[int(day[5:7])-1]} {day[:4]}" if day else ''


def month_name(month):
    return f"{MONATE[int(month[5:7])-1]} {month[:4]}"


def number(v, digits=0):
    text = f"{v:,.{digits}f}"
    return text.replace(',', ' ').replace('.', ',').replace(' ', '.')


def mio(v):
    x = v/1e6
    return number(x, 0 if x == int(x) or abs(x) >= 10000 else 1)


def jan(year):
    return f"{int(year):04}-01"


def months_apart(a, b):
    return (int(b[:4])*12+int(b[5:7]))-(int(a[:4])*12+int(a[5:7]))


# Rules -------------------------------------------------------------------------------------------------------------

def _read(path):
    try:
        rules = json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        raise RulesError(f'{path}: Regeldatei nicht lesbar ({error})')
    if not isinstance(rules, dict) or rules.get('schema_version') != 1:
        raise RulesError(f'{path}: schema_version 1 erwartet')
    return rules


def _shown(path):
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return Path(path).name


def merge(base, over):
    """World overrides: stages by number and features, sections and states by key, field by field; null removes a key."""
    out = {k:v for k, v in base.items()}
    stages = {s.get('nr'):dict(s) for s in base.get('stufen', [])}
    for s in over.get('stufen', []):
        stages[s.get('nr')] = {**stages.get(s.get('nr'), {}), **s}
    out['stufen'] = sorted(stages.values(), key=lambda s:s.get('nr') if isinstance(s.get('nr'), int) else -1)
    for part in ('merkmale', 'rubriken', 'zustaende'):
        merged = {k:dict(v) for k, v in base.get(part, {}).items()}
        for key, value in over.get(part, {}).items():
            if value is None:
                merged.pop(key, None)
            else:
                merged[key] = {**merged.get(key, {}), **value}
        out[part] = merged
    return out


def load(template, world=None):
    """(rules, sources) or None without a template. A broken rules file stops the build with a clear message."""
    if not template or not Path(template).exists():
        return None
    rules, sources = _read(template), {'vorlage':_shown(template)}
    if world and Path(world).exists():
        rules = merge(rules, _read(world))
        sources['welt'] = _shown(world)
    check(rules)
    return rules, sources


def _year(value, where):
    if value is not None and not (isinstance(value, int) and 1800 <= value <= 2300):
        raise RulesError(f'epochen.json: {where}: Jahr erwartet, nicht {value!r}')


def _check_timing(spec, where, need_trigger=True):
    for key in ('fruehestens', 'spaetestens'):
        _year(spec.get(key), f'{where}.{key}')
    if spec.get('fruehestens') and spec.get('spaetestens') and spec['fruehestens'] > spec['spaetestens']:
        raise RulesError(f'epochen.json: {where}: fruehestens liegt nach spaetestens')
    trigger = spec.get('ausloeser')
    if trigger is None:
        if need_trigger and not spec.get('spaetestens'):
            raise RulesError(f'epochen.json: {where}: Auslöser oder spaetestens fehlt')
        return
    kind = trigger.get('art') if isinstance(trigger, dict) else None
    if kind not in TRIGGERS:
        raise RulesError(f'epochen.json: {where}: unbekannte Auslöser-Art {kind!r} (bekannt: {", ".join(sorted(TRIGGERS))})')
    required, optional = TRIGGERS[kind]
    unknown = set(trigger)-required-optional-{'art'}
    if required-set(trigger) or unknown:
        raise RulesError(f'epochen.json: {where}: Auslöser {kind} braucht {sorted(required)}, erlaubt {sorted(optional)}')
    if kind == 'netz' and len({'fahrzeuge_ab', 'linien_ab'} & set(trigger)) != 1:
        raise RulesError(f'epochen.json: {where}: netz braucht fahrzeuge_ab oder linien_ab')
    if kind == 'umwelt' and len({'laerm_ab', 'verschmutzung_ab'} & set(trigger)) != 1:
        raise RulesError(f'epochen.json: {where}: umwelt braucht laerm_ab oder verschmutzung_ab')
    for key in set(trigger)-{'art', 'fahrzeugart', 'typ', 'muster'}:
        if not isinstance(trigger[key], (int, float)) or isinstance(trigger[key], bool):
            raise RulesError(f'epochen.json: {where}: {key} muss eine Zahl sein')
    if 'muster' in trigger:
        try:
            re.compile(trigger['muster'])
        except (re.error, TypeError) as error:
            raise RulesError(f'epochen.json: {where}: muster ungültig ({error})')


def check(rules):
    stages = rules.get('stufen') or []
    numbers = [s.get('nr') for s in stages]
    if not stages or not all(isinstance(n, int) and n >= 1 for n in numbers) or numbers != sorted(set(numbers)):
        raise RulesError('epochen.json: stufen brauchen eindeutige, aufsteigende Nummern ab 1')
    if stages[0].get('ausloeser') or stages[0].get('spaetestens'):
        raise RulesError('epochen.json: die erste Stufe gilt ab Beginn der Aufzeichnung und hat keinen Auslöser')
    for s in stages:
        if not isinstance(s.get('name'), str) or not s['name'].strip():
            raise RulesError(f"epochen.json: Stufe {s['nr']} ohne Namen")
        if s is not stages[0]:
            _check_timing(s, f"Stufe {s['nr']}")
    known = set(numbers)

    def steps_of(where, steps, text):
        if not isinstance(steps, list) or not steps:
            raise RulesError(f'epochen.json: {where}: stufen fehlen')
        last = 0
        for i, step in enumerate(steps):
            value = step.get('wert')
            if not isinstance(value, str) or not value or (not text and not SLUG.fullmatch(value)):
                raise RulesError(f'epochen.json: {where}[{i}]: wert {value!r} ungültig' + ('' if text else ' (Kleinbuchstaben, Ziffern, Bindestrich)'))
            if i == 0:
                if {'stufe', 'ausloeser', 'spaetestens', 'fruehestens'} & set(step):
                    raise RulesError(f'epochen.json: {where}: der erste Wert gilt von Anfang an')
                continue
            if 'stufe' in step:
                if step['stufe'] not in known:
                    raise RulesError(f"epochen.json: {where}[{i}]: Stufe {step['stufe']} gibt es nicht")
                if step['stufe'] < last:
                    raise RulesError(f'epochen.json: {where}: Stufen müssen in Reihenfolge stehen')
                last = step['stufe']
            else:
                _check_timing(step, f'{where}[{i}]')
            if 'vormals_ausgaben' in step and not (isinstance(step['vormals_ausgaben'], int) and 0 <= step['vormals_ausgaben'] <= 60):
                raise RulesError(f'epochen.json: {where}[{i}]: vormals_ausgaben 0 bis 60')

    for key, feature in (rules.get('merkmale') or {}).items():
        if not SLUG.fullmatch(key):
            raise RulesError(f'epochen.json: Merkmal {key!r}: Name aus Kleinbuchstaben')
        steps_of(f'merkmale.{key}', feature.get('stufen'), bool(feature.get('text')))
    for key, section in (rules.get('rubriken') or {}).items():
        if not SLUG.fullmatch(key) or not isinstance(section.get('titel'), str) or section.get('form') not in FORMS:
            raise RulesError(f'epochen.json: Rubrik {key!r} braucht titel und form ({", ".join(sorted(FORMS))})')
        if section.get('fuellung') not in ('fiktion', 'messdaten'):
            raise RulesError(f'epochen.json: Rubrik {key}: fuellung fiktion oder messdaten')
        if not re.fullmatch(r'[a-z0-9-]+\.json', str(section.get('datei', ''))):
            raise RulesError(f'epochen.json: Rubrik {key}: datei wie radioprogramm.json')
        if 'stufe' in section:
            if section['stufe'] not in known:
                raise RulesError(f"epochen.json: Rubrik {key}: Stufe {section['stufe']} gibt es nicht")
        else:
            _check_timing(section, f'Rubrik {key}')
    for key, state in (rules.get('zustaende') or {}).items():
        begin, end = state.get('beginn') or {}, state.get('ende') or {}
        if not SLUG.fullmatch(key) or begin.get('art') != 'kasse_einbruch':
            raise RulesError(f'epochen.json: Zustand {key!r}: beginn.art kasse_einbruch erwartet')
        _year(state.get('fruehestens'), f'Zustand {key}.fruehestens')
        pct, within, growth = begin.get('rueckgang_prozent'), begin.get('binnen_monaten'), end.get('wachstum_monate')
        if not (isinstance(pct, (int, float)) and 0 < pct < 100 and isinstance(within, int) and within >= 1 and isinstance(growth, int) and growth >= 1):
            raise RulesError(f'epochen.json: Zustand {key}: rueckgang_prozent (0–100), binnen_monaten und ende.wachstum_monate (ab 1) nötig')


# Facts of the canonical course -------------------------------------------------------------------------------------

def _from_event(e, art):
    return {'art':art, 'date':e['date'], 'meldung':e['id'], 'text':f"Am {lang(e['date'])} verzeichnen die Messbücher: {e['text']}"}


def _town_updates(rows):
    """Rows with a new town measurement, in course order."""
    last = None
    for r in rows:
        if r['towns'] and r['td'] and r['td'] != last:
            last = r['td']
            yield r


class Facts:
    def __init__(self, rows, events, kind, labels):
        self.rows, self.events, self.kind, self.labels = rows, events, kind, labels

    def event(self, pred):
        return next((e for e in self.events if pred(e)), None)

    def premiere(self, a):
        e = self.event(lambda e:e['typ'] == 'premiere' and e['werte'].get('art') == a['fahrzeugart'])
        if e:
            return _from_event(e, 'premiere')
        first = self.rows[0]
        if any(l[3] and self.kind(l[1], l[2]) == a['fahrzeugart'] for l in first['lines']):
            label = self.labels.get(a['fahrzeugart'], a['fahrzeugart'])
            return {'art':'premiere', 'date':first['d'], 'text':f"{label}: Linien mit Fahrzeugen schon bei Beginn der Aufzeichnung am {lang(first['d'])}."}
        return None

    def modell(self, a):
        base = True
        for r in self.rows:
            captured = [l for l in r['lines'] if len(l) > 5 and l[5] is not None]
            if not captured:
                continue
            for l in captured:
                if a.get('fahrzeugart') and self.kind(l[1], l[2]) != a['fahrzeugart']:
                    continue
                for m in l[5][1]:
                    year = m[6]
                    if isinstance(year, (int, float)) and not isinstance(year, bool) and year >= a['baujahr_ab']:
                        name = m[1] or m[0].rsplit('/', 1)[-1].removesuffix('.mdl')
                        e = self.event(lambda e:e['typ'] == 'modell' and e['werte'].get('datei') == m[0])
                        found = {'art':'modell', 'date':e['date'] if e else r['d'], 'wert':year}
                        if e:
                            found['meldung'] = e['id']
                        found['text'] = (f"„{name}“, laut Spiel verfügbar ab {year}, ist bei Beginn der Modellerfassung am {lang(r['d'])} schon im Linienbetrieb der Société."
                                         if base else f"Am {lang(found['date'])} ist „{name}“ erstmals im Linienbetrieb der Société, ein Modell, das laut Spiel ab {year} verfügbar ist.")
                        return found
            base = False
        return None

    def _confirmed(self, a, value_of, test):
        """First town that passes `test` in two consecutive town measurements (as the town milestones of meldungen.json)."""
        streak = {}
        for r in _town_updates(self.rows):
            names = {t[0]:t[1] for t in r['towns']}
            for tid, value in value_of(r):
                if a.get('stadt') is not None and tid != a['stadt']:
                    continue
                if isinstance(value, (int, float)) and test(value):
                    streak[tid] = streak.get(tid, 0)+1
                    if streak[tid] == 2:
                        return r, tid, names.get(tid, str(tid)), value
                else:
                    streak[tid] = 0
        return None

    def stadt(self, a):
        hit = self._confirmed(a, lambda r:[(t[0], t[2]) for t in r['towns']], lambda v:v >= a['einwohner_ab'])
        if not hit:
            return None
        r, tid, name, value = hit
        found = {'art':'stadt', 'date':r['td'], 'wert':value, 'stadt':tid,
                 'text':f"Am {lang(r['td'])} zählt {name} {number(value)} Einwohner und erreicht damit {number(a['einwohner_ab'])}."}
        e = self.event(lambda e:e['typ'] == 'stadt' and e['refs'].get('town') == tid and e['werte'].get('schwelle') == a['einwohner_ab'] and e['date'] == r['td'])
        if e:
            found['meldung'] = e['id']
        return found

    def umwelt(self, a):
        noise = 'laerm_ab' in a
        limit = a['laerm_ab'] if noise else a['verschmutzung_ab']
        hit = self._confirmed(a, lambda r:[(t[0], t[1] if noise else t[2]) for t in r.get('env') or []], lambda v:v >= limit)
        if not hit:
            return None
        r, tid, name, value = hit
        what = f"{number(value, 1)} dB Lärm (Schwelle {number(limit)} dB)" if noise else f"eine Verschmutzung (Rohwert) von {number(value)} (Schwelle {number(limit)})"
        return {'art':'umwelt', 'date':r['td'], 'wert':round(value, 3), 'stadt':tid, 'text':f"Am {lang(r['td'])} misst der Monitor in {name} {what}."}

    def netz(self, a):
        key, unit, step = ('vc', 'Fahrzeuge', 50) if 'fahrzeuge_ab' in a else ('lc', 'Linien', 10)
        limit = a.get('fahrzeuge_ab', a.get('linien_ab'))
        r = next((r for r in self.rows if r[key] is not None and r[key] >= limit), None)
        if not r:
            return None
        found = {'art':'netz', 'date':r['d'], 'wert':r[key], 'text':f"Am {lang(r['d'])} zählt das Netz {number(r[key])} {unit} (Schwelle {number(limit)})."}
        e = self.event(lambda e:e['typ'] == 'netz' and e['id'].startswith(f"netz-{unit}-{limit}-") and e['date'] == r['d']) if limit % step == 0 else None
        if e:
            found['meldung'] = e['id']
        return found

    def kasse(self, a):
        r = next((r for r in self.rows if isinstance(r['money'], (int, float)) and r['money'] >= a['ab']), None)
        return r and {'art':'kasse', 'date':r['d'], 'wert':r['money'],
                      'text':f"Am {lang(r['d'])} steht die Kasse der Société erstmals bei mindestens {mio(a['ab'])} Mio. (gemessen: {mio(r['money'])} Mio.)."}

    def wahrzeichen(self, a):
        for r in self.rows:
            for lid, name, completed, *_ in r.get('lm') or []:
                if completed and (a.get('id') is None or lid == a['id']):
                    day = r.get('lmd') or r['d']
                    return {'art':'wahrzeichen', 'date':day, 'wahrzeichen':lid, 'text':f"Am {lang(day)} verzeichnet der Monitor das Wahrzeichen „{name}“ als fertig."}
        return None

    def meldung(self, a):
        pattern = re.compile(a['muster'], re.I) if a.get('muster') else None
        e = self.event(lambda e:e['typ'] == a['typ'] and (not pattern or pattern.search(e['titel']+' '+e['text'])))
        return e and _from_event(e, 'meldung')

    def trigger(self, a):
        return getattr(self, a['art'])(a) if a else None


# Timeline ----------------------------------------------------------------------------------------------------------

def reach(spec, facts, start, end, prev):
    """(month, reason, occasion) of a stage, feature step or section; month None while open.
    prev is the month the step before was reached, or None while that one is still open."""
    hit = facts.trigger(spec.get('ausloeser'))
    early, late = spec.get('fruehestens'), spec.get('spaetestens')
    month, reason = None, 'offen'
    if hit:
        month, reason = hit['date'][:7], 'ausloeser'
        if early and month < jan(early):
            month, reason = jan(early), 'fruehestens'
    if late and (month is None or month > jan(late)):
        month, reason, hit = jan(late), 'spaetestens', None
    if month is None or prev is None:
        return None, 'offen', hit
    if month < prev:
        month, reason = prev, 'beginn' if prev == start else 'vorgaenger'
    if month > end:
        return None, 'offen', hit
    return month, reason, hit


def reason_text(reason, spec, hit, before=None):
    if reason == 'ausloeser':
        return f"Anlass: {hit['text']}"
    if reason == 'fruehestens':
        return f"Anlass: {hit['text']} Vor {spec['fruehestens']} wechselt die Zeitung nicht, deshalb erst mit dieser Ausgabe."
    if reason == 'spaetestens':
        return f"Bis Ende {spec['spaetestens']-1} ist kein eigener Anlass eingetreten; die Zeitung wechselt wie vorgesehen spätestens {spec['spaetestens']}."
    if reason == 'vorgaenger':
        return (f"Anlass: {hit['text']} " if hit else '')+f"Die Zeitung wechselt nicht vor der vorigen Stufe{f' „{before}“' if before else ''}."
    return None


def _entry(base, month, reason, hit, spec, before=None):
    out = dict(base)
    out['monat' if 'nr' in base else 'ab'] = month
    out['grund'] = reason
    for key in ('fruehestens', 'spaetestens', 'ausloeser'):
        if spec.get(key) is not None:
            out[key] = spec[key]
    if hit:
        out['anlass'] = hit
    if month and reason not in ('beginn', 'offen'):
        out['begruendung'] = reason_text(reason, spec, hit, before)
    return out


def crisis(rule, rows, end):
    """Phases of a state such as krisenpapier from the monthly closing cash (last detail row of each month)."""
    series = {}
    for r in rows:
        if isinstance(r['money'], (int, float)):
            series[r['d'][:7]] = (r['money'], r['d'])
    months = sorted(m for m in series if m <= end)
    pct, within = rule['beginn']['rueckgang_prozent'], rule['beginn']['binnen_monaten']
    growth, early = rule['ende']['wachstum_monate'], rule.get('fruehestens')
    phases, active, streak = [], None, 0
    for i, m in enumerate(months):
        value, day = series[m]
        if active:
            before = months[i-1]
            streak = streak+1 if months_apart(before, m) == 1 and value > series[before][0] else 0
            done = 'erholt' if value >= active['_ref'] else 'wachstum' if streak >= growth else None
            if done:
                active['ende'] = m
                active['ende_anlass'] = {'art':'kasse_erholung' if done == 'erholt' else 'kasse_wachstum', 'date':day, 'wert':value,
                    'text':(f"Im {month_name(m)} erreicht die Kasse der Société mit {mio(value)} Mio. wieder den Stand vor dem Einbruch ({mio(active['_ref'])} Mio.)."
                            if done == 'erholt' else f"Die Kasse der Société wächst seit {streak} Monaten ohne Unterbrechung, im {month_name(m)} auf {mio(value)} Mio.")}
                active['ende_begruendung'] = 'Anlass: '+active['ende_anlass']['text']
                del active['_ref']
                active = None
            continue
        if early and m < jan(early):
            continue
        window = [k for k in months[:i] if 1 <= months_apart(k, m) <= within]
        if not window:
            continue
        peak = max(window, key=lambda k:(series[k][0], -months_apart(k, m)))
        top = series[peak][0]
        if top > 0 and value <= top*(1-pct/100):
            drop = round(100*(top-value)/top, 1)
            active = {'beginn':m, 'ende':None, '_ref':top,
                      'anlass':{'art':'kasse_einbruch', 'date':day, 'wert':value, 'hoechststand':top, 'hoechststand_monat':peak, 'rueckgang_prozent':drop,
                                'text':f"Die Kasse der Société fällt von {mio(top)} Mio. ({month_name(peak)}) auf {mio(value)} Mio. ({month_name(m)}), ein Rückgang um {number(drop, 1)} %."}}
            active['begruendung'] = 'Anlass: '+active['anlass']['text']
            phases.append(active)
            streak = 0
    for p in phases:
        p.pop('_ref', None)
    return phases


def zeitleiste(loaded, rows, events, stand, kind, labels):
    """Content of zeitleiste.json for the canonical rows and events of build-journal.py."""
    rules, sources = loaded
    facts = Facts(rows, events, kind, labels)
    start, end = rows[0]['d'][:7], rows[-1]['d'][:7]
    stages, months, names, prev = [], {}, {}, start
    for s in rules['stufen']:
        base = {'nr':s['nr'], 'name':s['name']}
        if s is rules['stufen'][0]:
            entry = base | {'monat':start, 'grund':'beginn'}
        else:
            month, reason, hit = reach(s, facts, start, end, prev)
            entry = _entry(base, month, reason, hit, s, names.get(stages[-1]['nr']) if stages else None)
            prev = month
        if s.get('notiz'):
            entry['notiz'] = s['notiz']
        stages.append(entry)
        months[s['nr']], names[s['nr']] = entry['monat'], s['name']

    def by_stage(step, base, before):
        month = months[step['stufe']]
        if month is not None and before is not None and month < before:
            month = before
        return base | {'ab':month if before is not None else None, 'stufe':step['stufe']}

    features = {}
    for key, feature in rules.get('merkmale', {}).items():
        steps, before = [], start
        for i, step in enumerate(feature['stufen']):
            base = {'wert':step['wert']}
            if 'vormals_ausgaben' in step:
                base['vormals_ausgaben'] = step['vormals_ausgaben']
            if i == 0:
                entry = base | {'ab':start}
            elif 'stufe' in step:
                entry = by_stage(step, base, before)
            else:
                month, reason, hit = reach(step, facts, start, end, before)
                entry = _entry(base, month, reason, hit, step)
                if step.get('notiz'):
                    entry['notiz'] = step['notiz']
            steps.append(entry)
            before = entry['ab']
        features[key] = {'bezeichnung':feature.get('bezeichnung') or key, **({'text':True} if feature.get('text') else {}), 'stufen':steps}

    sections = {}
    for key, section in rules.get('rubriken', {}).items():
        base = {k:section[k] for k in ('titel', 'form', 'fuellung', 'datei')}
        if 'stufe' in section:
            sections[key] = base | {'ab':months[section['stufe']], 'stufe':section['stufe']}
        else:
            month, reason, hit = reach(section, facts, start, end, start)
            sections[key] = _entry(base, month, reason, hit, section)

    states = {}
    for key, state in rules.get('zustaende', {}).items():
        states[key] = {'bezeichnung':state.get('bezeichnung') or key,
                       'regel':{'fruehestens':state.get('fruehestens'), 'beginn':state['beginn'], 'ende':state['ende']},
                       **{k:state[k] for k in ('notiz_beginn', 'notiz_ende') if state.get(k)},
                       'phasen':crisis(state, rows, end)}

    return {'schema_version':1, 'stand':stand,
            'quelle':'Regeln aus der Epochen-Vorlage und der Datei der Welt, ausgewertet auf dem kanonischen Verlauf der Detailmessungen',
            'hinweis':'Monat = erste Ausgabe im neuen Stil. grund: ausloeser (Ereignis in diesem Monat), fruehestens (Ereignis lag davor), '
                      'spaetestens (kein Ereignis bis dahin), vorgaenger (wartete auf die vorige Stufe), beginn (galt schon bei Beginn der Aufzeichnung), offen.',
            'regeln':sources, 'beginn':start, 'stufen':stages, 'merkmale':features, 'rubriken':sections, 'zustaende':states}
