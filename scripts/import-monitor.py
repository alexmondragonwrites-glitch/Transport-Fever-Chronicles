"""Import a verified split monitor export without merging sessions or game-time branches.

Usage: python scripts/import-monitor.py PATH/TO/Pakete [--save archipel-des-alizes]
Only uses the Python standard library. Original packages remain untouched.
For regular updates from the local Spielmonitor use publish-monitor.py instead.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from monitor_build import MonitorBuilder

ROOT = Path(__file__).resolve().parents[1]


def package_rows(folder, index, session_index, world_id):
    for part in [p for p in index['parts'] if p['target'] == ['sessions', session_index, 'measurements']]:
        path = folder/part['file']
        with path.open('rb') as f:
            assert hashlib.file_digest(f,'sha256').hexdigest() == part['sha256'], path
        with zipfile.ZipFile(path) as z:
            fragment = json.loads(z.read(part['json_file']))
        assert len(fragment['records']) == part['record_count']
        for row in fragment['records']:
            assert row['world_id'] == world_id
            yield row


def main(folder, save):
    config = json.loads((ROOT/'data/monitor-sources.json').read_text(encoding='utf-8'))['saves'][save]
    world_id = config['world']['world_id']
    index = json.loads((folder/'PAKETE.json').read_text(encoding='utf-8'))
    template = index['template']
    assert template['world']['world_id'] == world_id
    builder = MonitorBuilder(world_id, config['folder'])
    for session_index, session in enumerate(template['sessions']):
        builder.add_session(session['session'], package_rows(folder, index, session_index, world_id))
    assert builder.counts['measurements'] == template['manifest']['measurement_count']
    output = builder.index(template['world'], source='packages', exported_at=template['manifest']['created_at'],
                           archive=config['archive'], source_database_rows=template['manifest']['database_rows'])
    out = ROOT/'saves'/save/'data'/config['folder']
    changed = builder.write(out, output)
    print(json.dumps({'segments':len(builder.segments), **builder.counts, 'changed':changed,
                      'bytes':sum(p.stat().st_size for p in out.glob('*.json'))}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folder')
    parser.add_argument('--save', default='archipel-des-alizes')
    args = parser.parse_args()
    main(Path(args.folder).resolve(), args.save)
