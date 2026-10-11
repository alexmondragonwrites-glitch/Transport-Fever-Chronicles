"""Import a verified split monitor export without merging sessions or game-time branches.

Usage: python scripts/import-monitor.py PATH/TO/Pakete
Only uses the Python standard library. Original packages remain untouched.
"""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WORLD_ID = 'tf3-2026-10-9-1791530983-207911368-2'
OUT = ROOT / 'saves/archipel-des-alizes/data/monitor-20261011'


def pick(row, names):
    return {k: row[k] for k in names.split() if k in row}


def date(row):
    if not row or not all(k in row for k in ('year', 'month', 'day')):
        return None
    return f"{row['year']:04}-{row['month']:02}-{row['day']:02}"


def write(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, separators=(',', ':'), allow_nan=False)+'\n', encoding='utf-8')


def snapshot(row):
    result = pick(row, 'recorded_at sequence mod_revision game_time game_date money vehicle_count line_count industry_count towns towns_game_time towns_game_date towns_recorded_at no_path_count no_path_scope')
    result['lines'] = []
    for line in row.get('lines', []):
        item = pick(line, 'id name carrier vehicles used capacity stops station_names station_group_ids cargo path_problem balance_year balance_recorded_at balance_start_game_time balance_end_game_time balance_start_game_date balance_end_game_date')
        item['timing'] = pick(line.get('timing') or {}, 'recorded_at waiting_count headway_seconds waiting_by_stop quality_by_cargo sample_limit cargo_sample_count')
        result['lines'].append(item)
    result['industries'] = row.get('industries', [])
    logistics = row.get('logistics') or {}
    result['logistics'] = pick(logistics, 'recorded_at game_time scope truncated cargo_truncated cargo_limit station_limit')
    result['logistics']['stations'] = [pick(s, 'id group_id name usage catchment_complete catchable_count') for s in logistics.get('stations', [])]
    result['logistics']['cargo_sample_count'] = len(logistics.get('cargo', []))
    people = row.get('people') or {}
    result['people_sample'] = {'count':len(people.get('rows', [])), 'limit':people.get('limit'), 'game_time':people.get('game_time')}
    return result


def main(folder):
    index = json.loads((folder/'PAKETE.json').read_text(encoding='utf-8'))
    template = index['template']
    assert template['world']['world_id'] == WORLD_ID
    OUT.mkdir(parents=True, exist_ok=True)
    segments = []
    counts = {'measurements':0, 'details':0, 'error_measurements':0}
    previous_game_time = None
    for session_index, session in enumerate(template['sessions']):
        partfiles = [p for p in index['parts'] if p['target'] == ['sessions', session_index, 'measurements']]
        segment = None
        number = 0
        city_history = {}
        last_town_time = None
        last_detail = None

        def finish():
            if segment is None:
                return
            segment['cities_history'] = {}
            for (town, month), entry in city_history.items():
                segment['cities_history'].setdefault(str(town), []).append(entry)
            for entries in segment['cities_history'].values():
                entries.sort(key=lambda x:x['game_time'])
            segment['detail_quality'] = {'recorded_at':last_detail['recorded_at'] if last_detail else None,
                                         'errors':last_detail.get('errors', []) if last_detail else None}
            filename = segment['id']+'.json'
            write(OUT/filename, segment)
            segments.append({k:segment[k] for k in ('id','session','started_at','ended_at','first_game_date','last_game_date','measurement_count','detail_count','error_measurements','rollback_before') } | {'file':'monitor-20261011/'+filename})

        for part in partfiles:
            path = folder/part['file']
            with path.open('rb') as f:
                assert hashlib.file_digest(f,'sha256').hexdigest() == part['sha256'], path
            with zipfile.ZipFile(path) as z:
                fragment = json.loads(z.read(part['json_file']))
            assert len(fragment['records']) == part['record_count']
            for row in fragment['records']:
                assert row['world_id'] == WORLD_ID
                game_time = row.get('game_time')
                rollback = previous_game_time is not None and game_time is not None and game_time < previous_game_time
                if segment is None or rollback:
                    finish()
                    number += 1
                    city_history, last_town_time, last_detail = {}, None, None
                    segment = {'id':session['session']+'-'+str(number), 'session':session['session'],
                               'started_at':row['recorded_at'], 'first_game_date':date(row.get('game_date')),
                               'measurement_count':0, 'detail_count':0, 'error_measurements':0,
                               'rollback_before':rollback, 'line_history':{}, 'world_history':[]}
                counts['measurements'] += 1
                segment['measurement_count'] += 1
                segment['ended_at'] = row['recorded_at']
                segment['last_game_date'] = date(row.get('game_date'))
                segment['snapshot'] = snapshot(row)
                previous_game_time = game_time
                if row.get('errors'):
                    segment['error_measurements'] += 1
                    counts['error_measurements'] += 1
                if row.get('sample_mode') == 'detail':
                    last_detail = row
                    counts['details'] += 1
                    segment['detail_count'] += 1
                    segment['world_history'].append({'recorded_at':row['recorded_at'], 'game_time':game_time,
                        'game_date':date(row.get('game_date')), 'money':row.get('money'),
                        'vehicles':row.get('vehicle_count'), 'lines':row.get('line_count'), 'errors':len(row.get('errors', []))})
                    for line in row.get('lines', []):
                        timing = line.get('timing') or {}
                        segment['line_history'].setdefault(str(line['id']), []).append({
                            'recorded_at':row['recorded_at'], 'game_time':game_time, 'game_date':date(row.get('game_date')),
                            'used':line.get('used'), 'capacity':line.get('capacity'), 'vehicles':line.get('vehicles'),
                            'balance_year':line.get('balance_year'), 'balance_recorded_at':line.get('balance_recorded_at'),
                            'waiting':timing.get('waiting_count'), 'timing_recorded_at':timing.get('recorded_at')})
                town_time = row.get('towns_recorded_at')
                gd = date(row.get('towns_game_date'))
                if town_time and gd and town_time != last_town_time:
                    for town in row.get('towns', []):
                        city_history[(town['id'],gd[:7])] = {
                            'date':gd, 'recorded_at':town_time, 'game_time':row.get('towns_game_time'),
                            'housing_occupied':town.get('housing_occupied'),
                            'housing_capacity':town.get('housing_capacity',town.get('population')),
                            'demand':town.get('demand'), 'supplied':town.get('supplied')}
                    last_town_time = town_time
        finish()
    assert counts['measurements'] == template['manifest']['measurement_count']
    output = {'schema_version':1, 'world':template['world'], 'exported_at':template['manifest']['created_at'],
              'source_sha256':index['source_sha256'], 'counts':counts, 'session_count':len(template['sessions']),
              'latest':segments[-1]['id'], 'segments':segments,
              'release_url':'https://github.com/alexmondragonwrites-glitch/Transport-Fever-Chronicles/releases/tag/archipel-export-2026-10-11',
              'history_policy':'Städte: letzter erfasster Stand je Spielmonat und Sitzungsabschnitt. Linien: Detailmessungen. Keine Interpolation zwischen Sitzungen, Rücksprüngen oder Aufzeichnungslücken.',
              'source_database_rows':template['manifest']['database_rows']}
    write(OUT/'index.json', output)
    print(json.dumps({'segments':len(segments), **counts, 'bytes':sum(p.stat().st_size for p in OUT.glob('*.json'))}))


if __name__ == '__main__':
    main(Path(sys.argv[1]).resolve())
