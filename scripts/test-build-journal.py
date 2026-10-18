"""Journal build from synthetic monitor sessions: vehicle models (Spielmonitor revision 15), the player's notebook,
the sea chart from measured positions (revision 16) and the kinds of vehicle, air lines included.

Usage: python scripts/test-build-journal.py
Builds into a temporary folder and never touches the published journal or the real publish cache.
Runs validate-journal.mjs on each result when Node.js is available. Only uses the Python standard library.
"""
import importlib.util
import json
import lzma
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_journal', ROOT/'scripts/build-journal.py')
journal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(journal)
SAVE = 'archipel-des-alizes'
WORLD = json.loads((ROOT/'data/monitor-sources.json').read_text(encoding='utf-8'))['saves'][SAVE]['world']['world_id']
REDAKTION = {'schema_version':1, 'items':[{'id':'test-einordnung', 'typ':'einordnung', 'art':'einordnung', 'date':'1912-01', 'rubrik':'Fuhrpark',
             'titel':'Testbeitrag', 'body':['Nur für den Test.'], 'grounding':'Einordnung der Redaktion zur Datengrundlage; keine Fiktion, nur Test.'}]}


def model(mid, name, vehicles, parts=None, bought=None, file=True):
    m = {'model_id':mid, 'name':name, 'vehicles':vehicles, 'parts':parts or vehicles, 'first_parts':vehicles, 'available_from':1900}
    if file:
        m['model_file'] = f'vehicle/test/m{mid}.mdl'
    if bought:
        m['purchase_first_game_time'] = m['purchase_last_game_time'] = 1
        m['purchase_first_game_date'] = m['purchase_last_game_date'] = {'year':bought[0], 'month':bought[1], 'day':bought[2]}
    return m


def detail(day, t, models=None, complete=True, revision=15):
    """One detail measurement; models maps line id to its vehicle_models list (None: before revision 15)."""
    lines = [{'id':1, 'name':'Bus Passagiere-Val-Roc-LO-1', 'carrier':'ROAD', 'vehicles':4, 'places':['Valmorin', 'Roc']},
             {'id':2, 'name':'TC Holz-Val-Sar-RE-1', 'carrier':'RAIL', 'vehicles':2, 'places':['Valmorin', 'Sarrians']},
             {'id':3, 'name':'RC Fisch-Roc-LO-2', 'carrier':'ROAD', 'vehicles':3, 'places':['Roc']}]
    for line in lines:
        if models is not None:
            line['vehicle_models'] = models.get(line['id'], [])
            line['vehicle_models_complete'] = complete if line['id'] == 1 else True
    d = {'year':1912, 'month':day[0], 'day':day[1]}
    return {'version':1, 'mod_revision':revision, 'world_id':WORLD, 'sample_mode':'detail', 'game_time':t, 'game_date':d,
            'recorded_at':f'2026-10-13T08:{t % 60:02}:00+02:00', 'money':1000000, 'vehicle_count':9, 'line_count':3,
            'lines':lines, 'industries':[], 'towns':[{'id':10, 'name':'Valmorin', 'housing_occupied':500, 'housing_capacity':600}],
            'towns_game_date':d, 'towns_recorded_at':'2026-10-13T08:00:00+02:00', 'errors':[]}


BASE = {1:[model(11, 'Stadtbus A', 4, bought=(1905, 3, 1))], 2:[model(21, 'Dampflok B', 2, bought=(1907, 1, 1)), model(22, 'Wagen C', 2, 10)],
        3:[model(31, 'Lastwagen D', 3, bought=(1909, 5, 1))]}


def validate(out):
    """validate-journal.mjs on a built folder; None without Node.js."""
    node = shutil.which('node')
    return node and subprocess.run([node, 'scripts/validate-journal.mjs', str(out)], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')


def with_models(extra):
    out = {k:list(v) for k, v in BASE.items()}
    for line, models in extra.items():
        out[line] = out[line]+models
    return out


class JournalCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='journal-test-'))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def build(self, sessions, notebook=None, redaktion=REDAKTION):
        monitor = self.tmp/'monitor'
        for name, rows in sessions.items():
            folder = monitor/'sessions'/name
            folder.mkdir(parents=True)
            (folder/'daten.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in rows), encoding='utf-8')
        if notebook is not None:
            (monitor/'history').mkdir()
            (monitor/'history/notizbuch.jsonl').write_text(notebook, encoding='utf-8')
        out = self.out = self.tmp/'out'
        out.mkdir()
        (out/'redaktion.json').write_text(json.dumps(redaktion, ensure_ascii=False), encoding='utf-8')
        self.changed = journal.build(monitor, SAVE, out, self.tmp/'cache')[0]
        self.validation = validate(out)
        if self.validation:
            self.assertEqual(self.validation.returncode, 0, self.validation.stderr or self.validation.stdout)
        return [json.loads((out/f'{n}.json').read_text(encoding='utf-8')) for n in ('meldungen', 'fuhrpark')]


class JournalModelTests(JournalCase):
    def test_old_recordings_without_models_keep_previous_fleet(self):
        meld, fleet = self.build({'a_alt':[detail((1, 1), 100, revision=14), detail((1, 20), 200, revision=14)]})
        self.assertNotIn('modelle', fleet)
        self.assertIn('bisher nicht', fleet['hinweis'])
        self.assertFalse([e for e in meld['meldungen'] if e['typ'] == 'modell'])
        self.assertTrue(all('modelle' not in v for v in fleet['verlauf']))

    def test_new_model_is_reported_once_and_baseline_models_are_not_news(self):
        new_bus = model(12, 'Stadtbus Neu', 2, bought=(1912, 2, 10))
        wagon = model(23, 'Kühlwagen', 1, 4)
        meld, fleet = self.build({
            'a_alt':[detail((1, 1), 100, revision=14)],
            'b_neu':[detail((2, 1), 200, BASE), detail((2, 5), 300, BASE), detail((2, 15), 400, with_models({1:[new_bus], 2:[wagon]})),
                     detail((3, 1), 500, with_models({1:[new_bus], 2:[wagon]}))]})
        events = [e for e in meld['meldungen'] if e['typ'] == 'modell']
        self.assertEqual(sorted(e['werte']['modell'] for e in events), ['Kühlwagen', 'Stadtbus Neu'])
        bus = next(e for e in events if e['werte']['modell'] == 'Stadtbus Neu')
        self.assertEqual((bus['date'], bus['titel']), ('1912-02-15', 'Neues Fahrzeugmodell: Stadtbus Neu'))
        self.assertEqual(bus['werte']['art'], 'bus')
        self.assertIn('Buslinie „Bus Passagiere-Val-Roc-LO-1“ zwischen Valmorin und Roc', bus['text'])
        self.assertIn('gekauft am 10.02.1912', bus['text'])
        wagons = next(e for e in events if e['werte']['modell'] == 'Kühlwagen')
        self.assertIn('1 Fahrzeug mit 4 Einheiten', wagons['text'])
        self.assertEqual(wagons['werte']['art'], 'gueterzug')
        models = fleet['modelle']
        self.assertEqual((models['erfasst_seit'], models['stand'], models['anzahl']), ('1912-02-01', '1912-03-01', 6))
        self.assertTrue(models['vollstaendig'])
        self.assertIn('seit 01.02.1912', fleet['hinweis'])
        kinds = {k['art']:k['modelle'] for k in models['je_art']}
        self.assertEqual([m['modell'] for m in kinds['bus']], ['Stadtbus A', 'Stadtbus Neu'])
        self.assertTrue(kinds['bus'][0]['seit_beginn'])
        self.assertEqual((kinds['bus'][1]['erstmals'], kinds['bus'][1]['seit_beginn']), ('1912-02-15', False))
        train = {m['modell']:m for m in kinds['gueterzug']}
        self.assertEqual((train['Wagen C']['fahrzeuge'], train['Wagen C']['einheiten']), (2, 10))
        self.assertEqual(train['Dampflok B']['kauf_erstes'], '1907-01-01')
        months = {v['monat']:v for v in fleet['verlauf']}
        self.assertNotIn('modelle', months['1912-01'])
        self.assertEqual((months['1912-02']['modelle'], months['1912-03']['modelle']), (6, 6))

    def test_incomplete_baseline_needs_a_later_purchase_and_names_fall_back_to_file(self):
        missed = model(13, 'Alter Bus', 1, bought=(1904, 1, 1))
        bought = model(14, None, 1, bought=(1912, 2, 20))
        meld, fleet = self.build({'b_neu':[detail((2, 1), 200, BASE, complete=False),
                                           detail((2, 25), 300, with_models({1:[missed, bought]}))]})
        events = [e for e in meld['meldungen'] if e['typ'] == 'modell']
        self.assertEqual([e['werte']['modell'] for e in events], ['m14'])
        self.assertTrue(fleet['modelle']['vollstaendig'])
        bus = {m['modell']:m for k in fleet['modelle']['je_art'] if k['art'] == 'bus' for m in k['modelle']}
        self.assertEqual((bus['Alter Bus']['erstmals'], bus['m14']['erstmals']), ('1912-02-25', '1912-02-25'))

    def test_model_without_file_uses_id_key_and_empty_model_lists_are_valid(self):
        nameless = model(41, 'Ohne Datei', 1, file=False)
        meld, fleet = self.build({'b_neu':[detail((2, 1), 200, {}), detail((2, 9), 300, {3:[nameless]})]})
        events = [e for e in meld['meldungen'] if e['typ'] == 'modell']
        self.assertEqual([e['werte']['datei'] for e in events], ['id:41'])
        self.assertEqual(fleet['modelle']['anzahl'], 1)


class JournalNotebookTests(JournalCase):
    """The player's notes from history/notizbuch.jsonl (Spielmonitor notebook)."""
    def note(self, nid, day, t, text, **extra):
        return {'id':nid, 'recorded_at':f'2026-10-13T08:{t % 60:02}:30+02:00', 'world_id':WORLD, 'world_name':'Archipel',
                'game_time':t, 'game_date':day, 'measured_at':'2026-10-13T08:00:00+02:00', 'source':'Live-Messung', 'text':text, 'public':True} | extra

    def notes(self):
        return json.loads((self.out/'notizen.json').read_text(encoding='utf-8'))

    def test_without_notebook_the_list_is_empty_and_labelled(self):
        self.build({'a':[detail((1, 1), 100)]})
        notes = self.notes()
        self.assertEqual(notes['notizen'], [])
        self.assertIn('Spielervorgabe', notes['hinweis'])
        self.assertNotIn('stand', notes)

    def test_only_released_notes_of_this_world_in_game_order(self):
        rows = [self.note('n2', '1912-02-05', 300, '  Lärmschutzwände in Valmorin gebaut, dafür Häuser abgerissen \n'),
                self.note('n1', '1912-02-01', 200, 'Straßenbahn statt Omnibus', edited_at='2026-10-13T09:00:00+02:00'),
                self.note('privat', '1912-02-02', 250, 'Nur für mich', public=False),
                self.note('fremd', '1912-02-02', 250, 'Andere Karte', world_id='andere-welt'),
                self.note('ohne-datum', None, 250, 'Kein Spieldatum'),
                self.note('leer', '1912-02-02', 250, '   ')]
        notebook = ''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in rows)+'kein JSON\n'
        self.build({'a':[detail((2, 1), 200), detail((2, 9), 300)]}, notebook)
        notes = self.notes()['notizen']
        self.assertEqual([n['id'] for n in notes], ['n1', 'n2'])
        self.assertEqual(notes[1], {'id':'n2', 'date':'1912-02-05', 'game_time':300, 'text':'Lärmschutzwände in Valmorin gebaut, dafür Häuser abgerissen'})
        self.assertIn('notizen.json', self.changed)
        # Unchanged notes leave the file untouched on the next build.
        self.assertNotIn('notizen.json', journal.build(self.tmp/'monitor', SAVE, self.out, self.tmp/'cache')[0])

    def test_stories_cite_notes_as_player_statements(self):
        notebook = json.dumps(self.note('n1', '1912-02-01', 200, 'Lärmschutzwände gebaut'), ensure_ascii=False)+'\n'
        story = {'id':'zitat', 'typ':'artikel', 'art':'fiktion', 'date':'1912-02', 'rubrik':'Valmorin', 'titel':'Mauern', 'body':['Text.'],
                 'grounding':'Spielervorgabe (Notizbuch des Direktors, 1. Februar 1912): Wände gebaut. Erfunden sind alle Personen.',
                 'refs':{'notizen':['n1', 'geloescht']}}
        self.build({'a':[detail((2, 1), 200)]}, notebook, {'schema_version':1, 'items':[story]})
        if not self.validation:
            self.skipTest('Node.js fehlt')
        self.assertIn('Notiz geloescht aus zitat fehlt', self.validation.stderr)
        unlabelled = {**story, 'grounding':'Laut Notiz wurden Wände gebaut. Erfunden sind alle Personen und Gespräche hier.'}
        (self.out/'redaktion.json').write_text(json.dumps({'schema_version':1, 'items':[unlabelled]}, ensure_ascii=False), encoding='utf-8')
        result = validate(self.out)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Spielervorgabe', result.stderr)



def charted(day, t, geo=None, terrain=None, logistics=None):
    """Revision-16 detail row with stop order, cargo and industries; positions and height grid only when given."""
    row = detail(day, t, BASE, revision=16)
    stops = {1:[701, 702], 2:[701, 703], 3:[702]}
    for line in row['lines']:
        line['station_group_ids'] = stops[line['id']]
        line['station_names'] = [f'Halt {g}' for g in stops[line['id']]]
        line['cargo'] = ([{'id':0, 'name':'Passagiere', 'passenger':True}] if line['id'] == 1
                         else [{'id':7, 'name':'Holz' if line['id'] == 2 else 'Fisch', 'passenger':False}, {'id':8, 'name':'Bretter', 'passenger':False}])
    row['towns'].append({'id':11, 'name':'Roc', 'housing_occupied':200, 'housing_capacity':260})
    row['industries'] = [{'id':401, 'name':'Valmorin Sägewerk', 'level':2, 'producing':True, 'production_year':80, 'shipped_year':60,
                          'inputs':[{'id':7, 'name':'Holz'}], 'outputs':[{'id':8, 'name':'Bretter'}]},
                         {'id':402, 'name':'Roc Fischerei', 'level':1, 'producing':False, 'inputs':[], 'outputs':[]}]
    if geo is not None:
        row['geo'], row['geo_recorded_at'] = geo, row['recorded_at']
    if terrain is not None:
        row['terrain'] = terrain
    if logistics is not None:
        row['logistics'] = logistics
    return row


def geo(towns, day=(2, 1), **extra):
    return {'game_date':{'year':1912, 'month':day[0], 'day':day[1]}, 'complete':True, 'positions_missing':0,
            'map':{'min_x':-2000, 'min_y':-1000, 'max_x':2000, 'max_y':1000, 'water_level':0}, 'towns':towns,
            'industries':[{'id':401, 'x':300, 'y':250, 'source':'bounding_volume'}],
            'station_groups':[{'id':701, 'x':120, 'y':210, 'name':'Valmorin Bahnhof', 'source':'bounding_volume'},
                              {'id':702, 'x':900, 'y':-300, 'name':'Roc Hafen', 'source':'stations', 'stations':2}],
            'landmarks':{}} | extra  # {}: an empty Lua table


TERRAIN = {'complete':True, 'min_x':-2000, 'min_y':-1000, 'max_x':2000, 'max_y':1000, 'cell_m':1000, 'cols':4, 'rows':2,
           'water_level':0, 'height_reference':'water_level', 'row_order':'min_y_first', 'heights':[[-20, -3, 5, 40], [-8, 2, 12, 90]]}
# While on board, the cargo's target is the stop where it leaves the vehicle (as measured live).
LOGISTICS = {'cargo_truncated':False, 'stations':[], 'cargo':[{'source_industry_id':401, 'target_id':702, 'cargo_id':8,
             'hops':[{'line_id':2}, {'line_id':2}, {'line_id':1}]}]*3 + [{'source_industry_id':401, 'target_id':999, 'cargo_id':8}]}


class JournalChartTests(JournalCase):
    def build_into(self, name, sessions):
        monitor = self.tmp/name/'monitor'
        for session, rows in sessions.items():
            folder = monitor/'sessions'/session
            folder.mkdir(parents=True)
            (folder/'daten.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in rows), encoding='utf-8')
        out = self.tmp/name/'out'
        out.mkdir()
        (out/'redaktion.json').write_text(json.dumps(REDAKTION, ensure_ascii=False), encoding='utf-8')
        journal.build(monitor, SAVE, out, self.tmp/name/'cache')
        result = validate(out)
        if result:
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        return out

    def test_without_positions_there_is_no_chart_and_the_other_files_stay_identical(self):
        plain = self.build_into('ohne', {'a':[charted((1, 1), 100), charted((2, 1), 200)]})
        placed = self.build_into('mit', {'a':[charted((1, 1), 100), charted((2, 1), 200, geo([{'id':10, 'x':1, 'y':2}]), TERRAIN, LOGISTICS)]})
        self.assertFalse((plain/'karte.json').exists())
        self.assertTrue((placed/'karte.json').exists())
        for name in ('meldungen', 'menschen', 'staedte', 'fuhrpark', 'notizen'):
            self.assertEqual((plain/f'{name}.json').read_bytes(), (placed/f'{name}.json').read_bytes(), name)

    def test_chart_places_towns_stops_and_industries_and_counts_what_is_missing(self):
        old = geo([{'id':10, 'x':5, 'y':5}, {'id':11, 'x':880, 'y':-280}], day=(1, 1))
        new = geo([{'id':10, 'x':100, 'y':200, 'min_x':0, 'min_y':100, 'max_x':200, 'max_y':300}], complete=False, positions_missing=1)
        self.build({'a':[charted((1, 1), 100, old)], 'b':[charted((2, 1), 200, new, TERRAIN, LOGISTICS)]})
        chart = json.loads((self.out/'karte.json').read_text(encoding='utf-8'))
        self.assertEqual((chart['stand']['positionen'], chart['stand']['vollstaendig']), ('1912-02-01', False))
        towns = {t['id']:t for t in chart['staedte']}
        # The newest measurement of an object wins; older positions fill in what the newest one lacks.
        self.assertEqual((towns[10]['x'], towns[10]['y'], towns[10]['ausdehnung'], towns[10]['einwohner']), (100, 200, [0, 100, 200, 300], 500))
        self.assertEqual((towns[11]['x'], towns[11]['ausdehnung']), (880, None))
        self.assertEqual([(i['id'], i['status'], i['erzeugnisse'], i['rohstoffe']) for i in chart['betriebe']], [(401, 'aktiv', ['Bretter'], ['Holz'])])
        self.assertEqual([(s['id'], s['name']) for s in chart['stationen']], [(701, 'Valmorin Bahnhof'), (702, 'Roc Hafen')])
        self.assertEqual(chart['fehlend'], {'staedte':0, 'betriebe':1, 'stationen':1, 'wahrzeichen':0})
        lines = {l['id']:l for l in chart['linien']}
        self.assertEqual((lines[2]['art'], lines[2]['halte'], lines[2]['waren']), ('gueterzug', [701, 703], ['Holz', 'Bretter']))
        self.assertEqual((lines[1]['art'], lines[1]['waren']), ('bus', ['Passagiere']))  # no goods measured: from the name
        self.assertEqual((chart['gelaende']['spalten'], chart['gelaende']['zeilen'], chart['gelaende']['bezug']), (4, 2, 'wasserspiegel'))
        ways = chart['warenwege']
        self.assertEqual((ways['stichprobe'], ways['stand']), (4, '1912-02-01'))
        self.assertEqual(ways['wege'], [{'von':401, 'stadt':None, 'betrieb':None, 'halt':702, 'ware':'Bretter', 'anzahl':3, 'linien':[2, 1]}])
        self.assertEqual(chart['grenze'], {'min_x':-2000, 'min_y':-1000, 'max_x':2000, 'max_y':1000})
        self.assertIn('karte.json', self.changed)

    def test_archived_sessions_build_the_same_journal(self):
        sessions = {'a':[charted((1, 1), 100), charted((2, 1), 200, geo([{'id':10, 'x':1, 'y':2}]), TERRAIN, LOGISTICS)],
                    'b':[charted((3, 1), 300)]}
        plain = self.build_into('offen', sessions)
        # The Spielmonitor packs finished sessions as daten.jsonl.xz with archiv.json; the bytes stay the same.
        archived = self.tmp/'archiviert'/'monitor'/'sessions'
        for name, rows in sessions.items():
            raw = ''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in rows).encode('utf-8')
            (archived/name).mkdir(parents=True)
            with lzma.open(archived/name/'daten.jsonl.xz', 'wb') as stream:
                stream.write(raw)
            if name == 'a':
                (archived/name/'archiv.json').write_text(json.dumps({'bytes':len(raw)}), encoding='utf-8')
        out = self.tmp/'archiviert'/'out'
        out.mkdir()
        (out/'redaktion.json').write_text(json.dumps(REDAKTION, ensure_ascii=False), encoding='utf-8')
        journal.build(archived.parent, SAVE, out, self.tmp/'archiviert'/'cache')
        for name in ('meldungen', 'menschen', 'staedte', 'fuhrpark', 'notizen', 'karte'):
            self.assertEqual((plain/f'{name}.json').read_bytes(), (out/f'{name}.json').read_bytes(), name)

    def test_misshaped_height_grid_is_left_out(self):
        broken = TERRAIN | {'rows':3}
        self.build({'a':[charted((2, 1), 200, geo([{'id':10, 'x':1, 'y':2}]), broken)]})
        chart = json.loads((self.out/'karte.json').read_text(encoding='utf-8'))
        self.assertIsNone(chart['gelaende'])
        self.assertEqual(chart['fehlend']['staedte'], 1)


def air(row, vehicles, name, carrier, models):
    """Adds the air line 4 to a detail row; the game reports no carrier while a line has no vehicle."""
    row['lines'].append({'id':4, 'name':name, 'carrier':carrier, 'vehicles':vehicles, 'places':['Valmorin', 'Roc'],
                         'station_group_ids':[701, 702], 'vehicle_models':models, 'vehicle_models_complete':True})
    return row


class JournalKindTests(JournalCase):
    def test_air_line_premieres_with_its_first_aircraft(self):
        plane = model(51, 'Junkers F 13', 4, bought=(1912, 2, 8))
        meld, fleet = self.build({'a':[detail((1, 20), 100, BASE),
                                       air(detail((2, 1), 200, BASE), 0, 'AP Passagiere-Val-LO-1', None, []),
                                       air(detail((2, 10), 300, BASE), 4, 'AP Passagiere-Val-Roc-IC-1', 'AIR', [plane]),
                                       air(charted((3, 1), 400, geo([{'id':10, 'x':1, 'y':2}])), 4, 'AP Passagiere-Val-Roc-IC-1', 'AIR', [plane])]})
        events = meld['meldungen']
        # Set up without an aircraft on 1 February, the line is news then; the premiere waits for the first aircraft.
        premieres = [e for e in events if e['typ'] == 'premiere']
        self.assertEqual([(e['date'], e['titel'], e['werte']) for e in premieres], [('1912-02-10', 'Premiere: Flugzeug', {'art':'flugzeug', 'fahrzeuge':4})])
        self.assertIn('„AP Passagiere-Val-Roc-IC-1“ fährt erstmals ein Flugzeug der Gesellschaft zwischen Valmorin und Roc.', premieres[0]['text'])
        line = next(e for e in events if e['typ'] == 'linie')
        self.assertEqual((line['date'], line['werte']['art']), ('1912-02-01', 'flugzeug'))
        self.assertTrue(line['text'].startswith('Fluglinie zwischen Valmorin und Roc, erstmals erfasst mit 0 Fahrzeugen'))
        plane_event = next(e for e in events if e['typ'] == 'modell')
        self.assertEqual((plane_event['date'], plane_event['werte']['art']), ('1912-02-10', 'flugzeug'))
        self.assertIn('auf der Fluglinie „AP Passagiere-Val-Roc-IC-1“', plane_event['text'])
        self.assertIn({'art':'flugzeug', 'bezeichnung':'Flugzeug'}, fleet['arten'])
        first = {p['art']:p for p in fleet['premieren']}['flugzeug']
        self.assertEqual((first['date'], first['linie'], first['seit_beginn']), ('1912-02-10', 'AP Passagiere-Val-Roc-IC-1', False))
        months = {v['monat']:v for v in fleet['verlauf']}
        self.assertEqual((months['1912-02']['fahrzeuge']['flugzeug'], months['1912-02']['linien']['flugzeug']), (4, 1))
        self.assertNotIn('unbekannt', months['1912-02']['fahrzeuge'])
        self.assertEqual([m['modell'] for k in fleet['modelle']['je_art'] if k['art'] == 'flugzeug' for m in k['modelle']], ['Junkers F 13'])
        chart = json.loads((self.out/'karte.json').read_text(encoding='utf-8'))
        self.assertEqual({l['id']:l['art'] for l in chart['linien']}[4], 'flugzeug')
        # Air cargo is a kind of its own; without a known prefix the carrier alone still says aircraft.
        self.assertEqual((journal.line_kind('AC Post-Val-Roc-IC-1', 'AIR'), journal.line_kind('Linie 1', 'AIR')), ('frachtflugzeug', 'flugzeug'))


if __name__ == '__main__':
    unittest.main()
