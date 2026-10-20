"""Publish the current Spielmonitor state to the website, uploading only changed views.

Usage: python scripts/publish-monitor.py [--monitor PATH] [--save ID] [--yes] [--no-push]

Reads the local session files (sessions/*/daten.jsonl, archived ones as daten.jsonl.xz) of the configured world,
builds the compact website view and writes only files whose content changed.
Finished sessions stay byte-identical, so a commit normally contains the active
session's segment and index.json. Nothing is committed without confirmation
(or --yes); with no visible change nothing is committed at all.
Only uses the Python standard library; git and node must be on PATH.
"""
import argparse
import glob
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from monitor_build import MonitorBuilder
import monitor_files

journal = importlib.import_module('build-journal')

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT/'.publish-cache/monitor.json'
BRANCH = 'main'


def git(*args, check=True):
    result = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    if check and result.returncode:
        raise SystemExit(f'git {" ".join(args)} fehlgeschlagen:\n{result.stderr.strip()}')
    return result


def session_rows(path, size, world_id, stats):
    """Rows of one world up to the captured size; an unfinished last line is left for the next run."""
    needle = world_id.encode()
    with monitor_files.open_data(path) as stream:
        remaining = size
        while remaining:
            raw = stream.readline(remaining)
            remaining -= len(raw)
            if not raw.endswith(b'\n') or needle not in raw:
                continue
            try:
                row = json.loads(raw.decode('utf-8-sig'))
            except (ValueError, UnicodeError):
                stats['unreadable'] += 1
                continue
            if isinstance(row, dict) and row.get('world_id') == world_id:
                yield row


def build(monitor, save, config, use_cache=True):
    world_id = config['world']['world_id']
    builder = MonitorBuilder(world_id, config['folder'])
    try:
        cache = json.loads(CACHE.read_text(encoding='utf-8')) if use_cache else {}
    except (OSError, ValueError):
        cache = {}
    # Any change to the builder or target folder invalidates all cached sessions.
    identity = {'world_id':world_id, 'folder':config['folder'],
                'builder':hashlib.sha256((ROOT/'scripts/monitor_build.py').read_bytes()).hexdigest()}
    if cache.get('identity') != identity:
        cache = {'identity':identity, 'sessions':{}}
    stats = {'unreadable':0, 'parsed_sessions':0}
    sessions = {}
    for path in monitor_files.data_paths(monitor/'sessions'):
        name = path.parent.name
        stat = path.stat()
        # Archiving a session changes its file, so it is read once more and yields the same record.
        key = {'size':stat.st_size, 'mtime_ns':stat.st_mtime_ns, 'previous_game_time':builder.previous_game_time}
        cached = cache['sessions'].get(name)
        if cached and cached['key'] == key:
            if cached['record']:
                builder.reuse_session(cached['record'])
        else:
            stats['parsed_sessions'] += 1
            record = builder.add_session(name, session_rows(path, monitor_files.size(path), world_id, stats))
            cached = {'key':key, 'record':record}
        sessions[name] = cached
    if not builder.segments:
        raise SystemExit(f'Keine Messungen für {world_id} in {monitor/"sessions"} gefunden.')
    cache['sessions'] = sessions
    index = builder.index(config['world'], source='spielmonitor', archive=config['archive'])
    out = ROOT/'saves'/save/'data'/config['folder']
    changed = builder.write(out, index)
    CACHE.parent.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps(cache), encoding='utf-8')
    return builder, index, changed, stats


def point_manifest(save, folder):
    path = ROOT/'saves'/save/'data/manifest.json'
    manifest = json.loads(path.read_text(encoding='utf-8'))
    target = folder+'/index.json'
    if manifest.get('monitor') != target:
        manifest['monitor'] = target
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return path


def published_index(save, folder):
    result = git('show', f'HEAD:saves/{save}/data/{folder}/index.json', check=False)
    return json.loads(result.stdout) if result.returncode == 0 else None


def grid_sha(heights):
    return hashlib.sha256(json.dumps(heights, separators=(',', ':')).encode()).hexdigest()


def fine_sha(F):
    # The fine grid counts with its frame and cell, so a grid rejected for another frame is not mistaken for a known one.
    return grid_sha([F.get(k) for k in ('min_x', 'min_y', 'max_x', 'max_y', 'cell_m', 'height_reference', 'heights')])


def find_blender():
    """Blender for the sea chart relief: environment variable BLENDER, PATH, or the usual install folders."""
    drives = os.listdrives() if hasattr(os, 'listdrives') else []
    found = [os.environ.get('BLENDER'), shutil.which('blender')]
    found += sorted(glob.glob('C:/Program Files/Blender Foundation/Blender*/blender.exe'), reverse=True)
    for drive in drives:
        found += sorted(glob.glob(os.path.join(drive, 'Blender*', 'blender.exe')), reverse=True)
        found += glob.glob(os.path.join(drive, 'SteamLibrary', 'steamapps', 'common', 'Blender', 'blender.exe'))
    found += glob.glob('C:/Program Files (x86)/Steam/steamapps/common/Blender/blender.exe')
    return next((f for f in found if f and os.path.isfile(f)), None)


def refresh_relief(save, config, monitor):
    """Render the old-chart relief again when the coarse grid in karte.json or the monitor's fine grid has changed."""
    folder = ROOT/'saves'/save/'data/journal'
    try:
        grid = json.loads((folder/'karte.json').read_text(encoding='utf-8')).get('gelaende')
    except (OSError, ValueError):
        return
    if not grid:
        return
    try:
        relief = json.loads((folder/'relief.json').read_text(encoding='utf-8'))
    except (OSError, ValueError):
        relief = {}
    fine_path = monitor/'history'/'gelaende'/(re.sub(r'[^A-Za-z0-9_.-]', '_', config['world']['world_id'])+'.json')
    fine_hash = None
    if fine_path.exists():
        try:
            fine_hash = fine_sha(json.loads(fine_path.read_text(encoding='utf-8')))
        except (OSError, ValueError):
            pass
    known_fine = {(relief.get('fein') or {}).get('sha256'), (relief.get('fein_abgelehnt') or {}).get('sha256')}
    if relief.get('gelaende_sha256') == grid_sha(grid['hoehen']) and (fine_hash is None or fine_hash in known_fine):
        return
    blender = find_blender()
    if not blender:
        print('Relief: Höhenraster neu, aber Blender nicht gefunden (Umgebungsvariable BLENDER setzen). '
              'Die Karte zeichnet die Küste bis dahin aus dem groben Raster.')
        return
    print('Relief: Höhenraster neu, rechne die Seekarte mit Blender (etwa eine halbe Minute) …')
    command = [blender, '-b', '--factory-startup', '-noaudio', '--python-exit-code', '1', '-P', str(ROOT/'scripts/render-relief.py'),
               '--', str(folder)] + (['--fein', str(fine_path)] if fine_hash else [])
    try:
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=900)
    except (OSError, subprocess.TimeoutExpired) as error:
        print(f'Relief: Blender nicht ausführbar ({error}); die Karte bleibt beim bisherigen Stand.')
        return
    lines = [l for l in result.stdout.splitlines() if l.startswith('render-relief:')]
    if result.returncode or not lines:
        print('Relief: Blender fehlgeschlagen, die Karte bleibt beim bisherigen Stand.', (result.stderr or result.stdout)[-1500:], sep='\n')
        return
    for line in lines:
        print('Relief:', line.split(':', 1)[1].strip())


def validate():
    for command in (['node', '--check', 'assets/monitor.js'], ['node', 'scripts/validate-monitor.mjs'], ['node', 'scripts/validate-data.mjs'],
                    ['node', 'scripts/validate-journal.mjs'], ['node', 'scripts/build-decade.mjs', '--check']):
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        if result.returncode:
            raise SystemExit(f'Prüfung {" ".join(command)} fehlgeschlagen, nichts hochgeladen:\n{result.stdout}{result.stderr}')


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--monitor', default=str(ROOT.parent/'Spielmonitor'), help='Spielmonitor-Ordner mit sessions/')
    parser.add_argument('--save', default='archipel-des-alizes')
    parser.add_argument('--yes', action='store_true', help='ohne Rückfrage committen und hochladen')
    parser.add_argument('--no-push', action='store_true', help='nur lokal aktualisieren, nichts committen')
    args = parser.parse_args()
    config = json.loads((ROOT/'data/monitor-sources.json').read_text(encoding='utf-8'))['saves'][args.save]
    folder = config['folder']
    paths = [f'saves/{args.save}/data/{folder}', f'saves/{args.save}/data/manifest.json', f'saves/{args.save}/data/journal']

    if git('diff', '--cached', '--quiet', check=False).returncode:
        raise SystemExit('Im Website-Repository sind bereits Änderungen vorgemerkt (git add). Bitte zuerst committen oder zurücknehmen.')
    if not args.no_push:
        git('fetch', '--quiet', 'origin', BRANCH)
        behind = int(git('rev-list', '--count', f'HEAD..origin/{BRANCH}').stdout)
        if behind:
            if git('merge', '--ff-only', '--quiet', f'origin/{BRANCH}', check=False).returncode:
                raise SystemExit(f'Das Repository ist {behind} Commit(s) hinter GitHub und lässt sich nicht automatisch nachziehen. Bitte manuell abgleichen.')
            print(f'{behind} neuere(n) Commit(s) von GitHub übernommen.')
    unpushed = [] if args.no_push else git('log', '--format=  %h %s', f'origin/{BRANCH}..HEAD').stdout.splitlines()

    print('Lese Spielmonitor-Sitzungen …')
    try:
        builder, index, changed, stats = build(Path(args.monitor).resolve(), args.save, config)
    except FileNotFoundError:
        builder, index, changed, stats = build(Path(args.monitor).resolve(), args.save, config, use_cache=False)
    point_manifest(args.save, folder)
    latest = index['segments'][-1]
    print(f"Stand: Spiel {latest['last_game_date']}, aufgezeichnet {index['exported_at']} · "
          f"{index['counts']['measurements']} Messungen in {len(index['segments'])} Abschnitten "
          f"({stats['parsed_sessions']} Sitzungsdatei(en) neu gelesen)")
    if stats['unreadable']:
        print(f"Hinweis: {stats['unreadable']} unlesbare Zeile(n) übersprungen.")
    print('Aktualisiere Le Journal des Alizés …')
    journal_changed, _, journal_sizes = journal.build(Path(args.monitor).resolve(), args.save)
    print(f"Journal: {journal_sizes['meldungen.json']} Meldungen, {journal_sizes['menschen.json']} Personen, "
          f"{journal_sizes['notizen.json']} Notizen aus dem Notizbuch"
          + (f" · geändert: {', '.join(journal_changed)}" if journal_changed else ' · unverändert'))
    refresh_relief(args.save, config, Path(args.monitor).resolve())

    git('add', '-A', '--', *paths)
    has_changes = git('diff', '--cached', '--quiet', check=False).returncode != 0
    if not has_changes and not unpushed:
        print('Keine Änderung an der Website-Ansicht seit dem letzten Upload – nichts zu tun.')
        return
    if has_changes:
        validate()
        previous = published_index(args.save, folder)
        new_measurements = index['counts']['measurements']-(previous['counts']['measurements'] if previous else 0)
        print('\nGeänderte Dateien:')
        print(git('diff', '--cached', '--stat=100', '--', *paths).stdout.rstrip())
        if previous:
            new_segments = [s['id'] for s in index['segments'] if s['id'] not in {p['id'] for p in previous['segments']}]
            print(f"\n+{new_measurements} Messungen seit dem letzten Upload"+(f", neue Abschnitte: {', '.join(new_segments)}" if new_segments else ''))
    if unpushed:
        print('\nNoch nicht hochgeladene lokale Commits, die mitgeschickt werden:')
        print('\n'.join(unpushed))

    if args.no_push:
        git('reset', '--quiet', '--', *paths)
        print('\n--no-push: Dateien lokal aktualisiert, nichts committet.')
        return
    if not args.yes:
        answer = input('\nJetzt committen und zu GitHub hochladen? [j/N] ').strip().lower()
        if answer not in ('j', 'ja', 'y', 'yes'):
            git('reset', '--quiet', '--', *paths)
            print('Abgebrochen. Dateien bleiben lokal aktualisiert; der nächste Lauf nimmt sie mit.')
            return
    if has_changes:
        # Staged rather than just rebuilt: an aborted earlier run may already have written the notes.
        notes = git('diff', '--cached', '--name-only', '--', f'saves/{args.save}/data/journal/notizen.json').stdout.strip()
        message = f"Monitorstand Spiel {latest['last_game_date']} (+{new_measurements} Messungen{', Notizbuch aktualisiert' if notes else ''})"
        git('commit', '--quiet', '-m', message)
        print(f'Commit: {message}')
    push = git('push', 'origin', f'HEAD:{BRANCH}', check=False)
    if push.returncode:
        raise SystemExit('Push fehlgeschlagen, der Commit bleibt lokal und wird beim nächsten Lauf mit hochgeladen:\n'+push.stderr.strip())
    print('Hochgeladen. GitHub Pages aktualisiert die Website in 1–2 Minuten.')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    try:
        main()
    except KeyboardInterrupt:
        sys.exit('Abgebrochen.')
