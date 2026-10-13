"""Journal build from synthetic monitor sessions: vehicle models (Spielmonitor revision 15) and the player's notebook.

Usage: python scripts/test-build-journal.py
Builds into a temporary folder and never touches the published journal or the real publish cache.
Runs validate-journal.mjs on each result when Node.js is available. Only uses the Python standard library.
"""
import importlib.util
import json
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


if __name__ == '__main__':
    unittest.main()
