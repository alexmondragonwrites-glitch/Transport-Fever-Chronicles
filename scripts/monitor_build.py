"""Shared builder for the compact website monitor view.

Used by import-monitor.py (verified release packages) and publish-monitor.py
(live Spielmonitor session files). The output contains no wall-clock values:
identical measurements produce byte-identical files, so git only sees the
segments whose website view actually changed.
"""
import json


def pick(row, names):
    return {k: row[k] for k in names.split() if k in row}


def date(row):
    if not row or not all(k in row for k in ('year', 'month', 'day')):
        return None
    return f"{row['year']:04}-{row['month']:02}-{row['day']:02}"


def dumps(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'), allow_nan=False)+'\n'


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


SEGMENT_KEYS = ('id', 'session', 'started_at', 'ended_at', 'first_game_date', 'last_game_date',
                'measurement_count', 'detail_count', 'error_measurements', 'rollback_before')


class MonitorBuilder:
    """Splits measurements into sessions and game-time branches without merging them."""

    def __init__(self, world_id, folder):
        self.world_id = world_id
        self.folder = folder            # path prefix used in index.json, e.g. 'monitor'
        self.files = {}                 # filename -> content (str) or None for an unchanged cached file
        self.segments = []
        self.counts = {'measurements':0, 'details':0, 'error_measurements':0}
        self.session_count = 0
        self.previous_game_time = None
        self.last_recorded_at = None

    def add_session(self, session, rows):
        """Consume one session's rows in recorded order. Returns a cache record for reuse."""
        start_counts = dict(self.counts)
        start_segments = len(self.segments)
        segment = None
        number = 0
        city_history, last_town_time, last_detail = {}, None, None

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
            # Line histories are the bulk of a segment; the website loads them only when a line is opened.
            filename, lines_name = segment['id']+'.json', segment['id']+'-lines.json'
            self.files[lines_name] = dumps({'id':segment['id'], 'line_history':segment.pop('line_history')})
            self.files[filename] = dumps(segment)
            self.segments.append({k:segment[k] for k in SEGMENT_KEYS} | {'file':self.folder+'/'+filename,
                                                                        'lines_file':self.folder+'/'+lines_name})

        for row in rows:
            if row.get('world_id') != self.world_id:
                raise ValueError('Unexpected world in session '+session)
            game_time = row.get('game_time')
            rollback = self.previous_game_time is not None and game_time is not None and game_time < self.previous_game_time
            if segment is None or rollback:
                finish()
                number += 1
                city_history, last_town_time, last_detail = {}, None, None
                segment = {'id':session+'-'+str(number), 'session':session,
                           'started_at':row['recorded_at'], 'first_game_date':date(row.get('game_date')),
                           'measurement_count':0, 'detail_count':0, 'error_measurements':0,
                           'rollback_before':rollback, 'line_history':{}, 'world_history':[]}
            self.counts['measurements'] += 1
            segment['measurement_count'] += 1
            segment['ended_at'] = row['recorded_at']
            segment['last_game_date'] = date(row.get('game_date'))
            segment['snapshot'] = snapshot(row)
            self.previous_game_time = game_time
            if row.get('errors'):
                segment['error_measurements'] += 1
                self.counts['error_measurements'] += 1
            if row.get('sample_mode') == 'detail':
                last_detail = row
                self.counts['details'] += 1
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
        if segment is None:
            return None
        self.session_count += 1
        self.last_recorded_at = segment['ended_at']
        return {'segments':self.segments[start_segments:],
                'counts':{k:self.counts[k]-start_counts[k] for k in self.counts},
                'last_game_time':self.previous_game_time, 'last_recorded_at':self.last_recorded_at}

    def reuse_session(self, record):
        """Add a session whose files are already current, from a cache record of add_session."""
        for entry in record['segments']:
            self.segments.append(entry)
            for key in ('file', 'lines_file'):
                self.files[entry[key].split('/', 1)[1]] = None
        for k, v in record['counts'].items():
            self.counts[k] += v
        self.session_count += 1
        self.previous_game_time = record['last_game_time']
        self.last_recorded_at = record['last_recorded_at']

    def index(self, world, **extra):
        return {'schema_version':1, 'world':world, 'exported_at':self.last_recorded_at,
                'counts':self.counts, 'session_count':self.session_count,
                'latest':self.segments[-1]['id'], 'segments':self.segments,
                'history_policy':'Städte: letzter erfasster Stand je Spielmonat und Sitzungsabschnitt. Linien: Detailmessungen. Keine Interpolation zwischen Sitzungen, Rücksprüngen oder Aufzeichnungslücken.'} | extra

    def write(self, out, index):
        """Write changed files only and remove segments that no longer exist. Returns changed names."""
        out.mkdir(parents=True, exist_ok=True)
        wanted = dict(self.files) | {'index.json':dumps(index)}
        changed = []
        for name, content in wanted.items():
            path = out/name
            if content is None:
                if not path.exists():
                    raise FileNotFoundError(f'{path} fehlt, Cache ist veraltet')
                continue
            if path.exists() and path.read_text(encoding='utf-8') == content:
                continue
            path.write_text(content, encoding='utf-8')
            changed.append(name)
        for path in sorted(out.glob('*.json')):
            if path.name not in wanted:
                path.unlink()
                changed.append(path.name+' (entfernt)')
        return changed
