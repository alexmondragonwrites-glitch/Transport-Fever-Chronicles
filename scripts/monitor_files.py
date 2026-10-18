"""Raw Spielmonitor session files: daten.jsonl while recording, daten.jsonl.xz once archived.

The Spielmonitor (archivieren.py) packs finished sessions losslessly with xz and keeps the original
size and SHA-256 in archiv.json next to it. Both kinds read as exactly the original bytes, so the
builders here see the same lines as before. Same rules as Spielmonitor/sitzungsdaten.py.
Only uses the Python standard library.
"""
import json
import lzma
from pathlib import Path

PLAIN = 'daten.jsonl'
ARCHIVE = 'daten.jsonl.xz'
MANIFEST = 'archiv.json'


def data_paths(sessions):
    """Raw data file of every session folder in folder order; while both exist the original wins."""
    sessions = Path(sessions)
    if not sessions.is_dir():
        return []
    found = []
    for folder in sorted(f for f in sessions.iterdir() if f.is_dir()):
        for name in (PLAIN, ARCHIVE):
            if (folder/name).is_file():
                found.append(folder/name)
                break
    return found


def is_archive(path):
    return Path(path).name == ARCHIVE


def size(path):
    """Bytes of the original data; for an archive as recorded when it was checked."""
    path = Path(path)
    if not is_archive(path):
        return path.stat().st_size
    try:
        return json.loads((path.parent/MANIFEST).read_text(encoding='utf-8'))['bytes']
    except (OSError, ValueError, KeyError):
        with lzma.open(path, 'rb') as stream:
            return sum(len(chunk) for chunk in iter(lambda: stream.read(1 << 20), b''))


def open_data(path):
    """Binary stream with exactly the original bytes."""
    path = Path(path)
    return lzma.open(path, 'rb') if is_archive(path) else path.open('rb')
