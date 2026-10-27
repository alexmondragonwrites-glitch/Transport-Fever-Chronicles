"""Faktenblatt von Erlental aus synthetischen Monitor-Sitzungen: Umbenennungen von Ort, Betrieb und Halt,
Orte unter ihrem Namen am Jahresende, Halte mit Stationsnamen, eine Linie, die im Lauf des Jahres verschwindet,
und ein Neuladen, dessen verworfener Abschnitt nicht zählt.

Usage: python scripts/test-erlental-fakten.py
Schreibt nur in einen temporären Ordner. Nur Python-Standardbibliothek.
"""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('erlental_fakten', ROOT/'scripts/erlental-fakten.py')
fakten = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fakten)


def town(name, people):
    return {'id': 1, 'name': name, 'housing_occupied': people, 'population': people,
            'supply_districts': [{'goods': [{'name': 'Fisch', 'supplied': 0, 'demand': 10}]}]}


def line(lid=7, name='RC Fisch-Are-LO-1'):
    return {'id': lid, 'name': name, 'carrier': 'ROAD', 'vehicles': 2, 'places': ['Arenswiel', 'Arenswiel'],
            'station_names': ['Arenswiel Hafen', 'Arenswiel Mitte'], 'balance_year': -500,
            'balance_start_game_time': 0, 'balance_end_game_time': 64000,
            'vehicle_models': [{'name': 'Pferdefuhrwerk', 'vehicles': 2, 'purchase_first_game_date': {'year': 1900, 'month': 1, 'day': 5}}]}


def row(d, t, mode, place, people, works=None, lines=(), finance=False):
    r = {'world_id': fakten.WORLD_ID, 'game_date': {'year': 1900, 'month': 1, 'day': d}, 'game_time': t, 'sample_mode': mode,
         'towns': [town(place, people)], 'money': 1000, 'line_count': len(lines), 'vehicle_count': 2 * len(lines)}
    if works:
        r['industries'] = [{'id': 10, 'name': works, 'outputs': [{'name': 'Fisch'}], 'inputs': [], 'level': 1,
                            'production_year': 0, 'shipped_year': 0}]
        r['logistics'] = {'stations': [{'id': 100, 'name': works}]}
        r['lines'] = list(lines)
    if finance:
        r['finance'] = {'game_date': {'year': 1900, 'month': 1, 'day': d}, 'periods': ['1/00 - 3/00'], 'rows': [],
                        'total': [-500], 'loan_borrowing': [0], 'loan_repayment': [0], 'interest': [0],
                        'balance': [1000], 'loan': [0], 'loan_now': 0}
    return r


BUS = line(8, 'Bus Passagiere-Sil-LO-1')
ROWS = [
    row(1, 0, 'detail', 'Selters', 100, 'Mettmann Fischzucht'),
    row(3, 32000, 'basic', 'Arenswiel', 100),
    row(5, 64000, 'detail', 'Arenswiel', 120, 'Seegut Tiefenborn', [line(), BUS]),
    row(7, 96000, 'detail', 'Falschname', 125, 'Seegut Tiefenborn', [line(), BUS]),  # danach neu geladen: verworfen
    row(6, 80000, 'detail', 'Arenswiel', 120, 'Seegut Tiefenborn', [line(), BUS]),
    row(9, 128000, 'detail', 'Arenswiel', 130, 'Seegut Tiefenborn', finance=True),  # ohne den Bus
    row(10, 144000, 'basic', 'Arenswiel', 130, 'Seegut Tiefenborn', [BUS]),  # die Grundmessung danach hat ihn wieder
]


class ErlentalFakten(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)/'sessions'/'20261027_000000_000000'
            folder.mkdir(parents=True)
            (folder/'daten.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in ROWS), encoding='utf-8')
            cls.text = fakten.sheet(1900, tmp)

    def test_renames_with_first_measurement(self):
        self.assertIn('- 3.1.1900 Ort: Selters → Arenswiel', self.text)
        self.assertIn('- 5.1.1900 Betrieb: Mettmann Fischzucht → Seegut Tiefenborn', self.text)
        self.assertIn('- 5.1.1900 Halt: Mettmann Fischzucht → Seegut Tiefenborn', self.text)

    def test_towns_under_their_name_at_year_end(self):
        self.assertIn('- Arenswiel (vorher Selters): 100 → 130 (+30)', self.text)

    def test_line_with_station_names_and_its_end(self):
        self.assertIn('Halte: Arenswiel Hafen, Arenswiel Mitte; Kaufdatum laut Monitor: 5.1.1900', self.text)
        self.assertIn('- **nicht mehr gemessen:** RC Fisch-Are-LO-1 (zuletzt 6.1.1900)', self.text)

    def test_line_left_out_by_one_detail_measurement_runs_on(self):
        self.assertNotIn('nicht mehr gemessen:** Bus Passagiere-Sil-LO-1', self.text)

    def test_discarded_section_after_reload(self):
        self.assertIn('Rücksprünge der Spielzeit (Neuladen) im Jahr: 1; 1 Messungen aus verworfenen Abschnitten', self.text)
        self.assertNotIn('Falschname', self.text)

    def test_economic_year_in_days(self):
        self.assertIn('sind das etwa 4 Kalendertage', self.text)


if __name__ == '__main__':
    unittest.main()
