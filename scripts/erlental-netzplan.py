"""Netzplan von Erlental am Ende eines Spieljahres, gezeichnet im Stil der Zeit.

Usage: python scripts/erlental-netzplan.py JAHR [--monitor PFAD] [--out saves/erlental/netzplan]

Schreibt saves/erlental/netzplan/JAHR.html: eine eigene Seite mit der Übersichtskarte aller Personenlinien und je Ort
mit Straßenbahn einem Stadtplan mit Haltestellen und Liniennummern. Die Chronikseite lädt den Plan (das Element .np)
in einen Kasten <div class="np-laden" data-netzplan="netzplan/JAHR.html"> nach, sobald man in seine Nähe scrollt.

Quellen, alle auf dem Rechner des Spielers (Q4 der Chronik):
- Linien, Halte und Fahrzeuge aus der letzten Messung des Jahres (Spielmonitor, sessions),
- die Lage der Haltestellen und Orte aus den geo-Angaben der Messungen,
- der Verlauf jeder Linie über Straßen und Gleise, Straßen und Gebäude aus dem Kartenexport des Kapitels
  (Erlental-Karte/zeitleiste.json nennt ihn; steht das Kapitel dort noch nicht, der erste vollständige Export
  vom Januar des Folgejahres aus der Kartenhistorie des Monitors),
- Wasserflächen aus dem Geländescan, mit dem auch die 3D-Karte gebacken ist (zeitleiste.json, Feld gelaende).
Gezeichnet werden nur gemessene Personenlinien; Gleise ohne Personenzug erscheinen als Güterbahn ohne Namen.
Dampfer fahren im Spiel frei über das Wasser; gezeichnet ist der kürzeste Kurs zwischen den Anlegern.

Stil: STILE hält je Epoche Titel und Wortlaut, erlental.css (Abschnitt Netzplan) Schrift, Farben und Zeichen. Bis 1919
gilt der Stil der Kaiserzeit. Der Plan wird mit den Jahren moderner (Vorgabe des Spielers vom 2.11.2026); der nächste
Stil kommt zu Beginn von Staffel 3 dazu.
Nur Python-Standardbibliothek.
"""
import argparse
import heapq
import html
import importlib.util
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('erlental_fakten', ROOT/'scripts/erlental-fakten.py')
FAKTEN = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FAKTEN)
WORLD_ID = FAKTEN.WORLD_ID
ZEITLEISTE = ROOT.parent/'Erlental-Karte/zeitleiste.json'

MONATE = ('Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober',
          'November', 'Dezember')
# Zeichenreihenfolge von unten nach oben; die Legende folgt ihr rückwärts.
ARTEN = {
    'dampfer': 'Dampfer',
    'postkutsche': 'Postkutsche',
    'omnibus': 'Omnibus',
    'pferdebahn': 'Pferdebahn',
    'tram': 'Elektrische Straßenbahn',
    'bahn': 'Personenzug',
}
PFERDE = ('pferd', 'kutsche')
STILE = {
    'kaiserzeit': {
        'von': 1900, 'bis': 1919,
        'kopf': 'Übersicht der Personenlinien',
        'legende': 'Zeichen-Erklärung',
        'staedte': 'Die Orte mit Straßenbahn',
    },
}

KARTE_PX = 760     # Breite der Übersichtskarte, so breit wie die Textspalte der Chronik
BAND = 112         # Band unter der Karte für Kopf, Maßstab und Zeichen-Erklärung
STADT_PX = 372     # Breite eines Stadtplans; zwei passen nebeneinander
RAND = 12          # Abstand der Karte vom Rahmen


def stil(jahr):
    for name, s in STILE.items():
        if s['von'] <= jahr <= s['bis']:
            return name, s
    sys.exit(f'Für {jahr} gibt es noch keinen Stil des Netzplans. Er wird mit jeder Staffel moderner: '
             'den Stil vor dem ersten Kapitel der Staffel in STILE und erlental.css festlegen.')


def datum(d):
    return f'{d[2]}. {MONATE[d[1] - 1]} {d[0]}'


def zahl(v):
    return f'{v:,}'.replace(',', '.')


# ---------------------------------------------------------------- Daten

def kapitel_export(jahr, monitor):
    """Kartenexport und Chronikseite des Kapitels, das mit diesem Jahr endet (Erlental-Karte/zeitleiste.json).
    Ab Staffel 2 hat jedes Jahr ein Kapitel. Ist dessen Kartenstand noch nicht eingetragen, gilt der erste vollständige
    Export vom Januar des Folgejahres aus der Kartenhistorie des Monitors; so entsteht der Plan vor dem Backen der Karte."""
    z = json.loads(ZEITLEISTE.read_text(encoding='utf-8'))
    ordner = Path(monitor)/'history/karte'/WORLD_ID
    kap = [k for k in z['kapitel'] if k.get('stichtag', '').startswith(f'{jahr}-')]
    if kap:
        k = max(kap, key=lambda k: k['stichtag'])
        staffel = next((s for s in z.get('staffeln', []) if k['id'] in s.get('kapitel', [])), {})
        export = json.loads((ordner/k['export']).read_text(encoding='utf-8'))
    else:
        staffel = next((s for s in z.get('staffeln', []) if s.get('chronik')
                        and int(s['zeitraum'][:4]) <= jahr <= int(s['zeitraum'][-4:])), None)
        export = staffel and jahreswechsel(ordner, jahr + 1)
        if not export:
            sys.exit(f'Kein Kapitel mit Stichtag im Jahr {jahr} in {ZEITLEISTE} und kein vollständiger Kartenexport '
                     f'vom Januar {jahr + 1} in {ordner}.')
        k = {'titel': f'Kapitel {roemisch(jahr - int(staffel["zeitraum"][:4]) + 1)}'}
        print(f'Kartenstand für {jahr} noch nicht in der Zeitleiste: Export {export["scan_id"]} '
              f'vom {datum(tuple(export["game_date"][x] for x in ("year", "month", "day")))}.')
    seite = (staffel.get('chronik') or z.get('chronik') or '../chronik.html').removeprefix('../')
    gelaende = ZEITLEISTE.parent/z['gelaende']
    return k, seite, staffel.get('titel', ''), export, gelaende


def jahreswechsel(ordner, jahr):
    """Erster vollständiger Kartenexport vom Januar dieses Jahres. Spieldatum und Vollständigkeit stehen im Kopf der Datei."""
    for pfad in sorted(ordner.glob('*.json')):
        with pfad.open(encoding='utf-8') as f:
            kopf = f.read(2000)
        m = re.search(r'"game_date":(\{[^}]*\})', kopf)
        tag = m and json.loads(m.group(1))
        if tag and tag['year'] == jahr and tag['month'] == 1:
            export = json.loads(pfad.read_text(encoding='utf-8'))
            if export.get('complete'):
                return export
    return None


def roemisch(n):
    zeichen = ''
    for wert, z in ((10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')):
        while n >= wert:
            zeichen += z
            n -= wert
    return zeichen


def messungen(monitor, jahr):
    rows = FAKTEN.canonical(list(FAKTEN.rows_of(monitor)))
    ende = (jahr, 12, 31)
    letzte = None
    stationen, orte = {}, {}
    for r in rows:
        tag = FAKTEN.day(r)
        if tag[0] == jahr and r.get('lines'):
            letzte = r
        # Lagen ändern sich nicht; spätere Messungen ergänzen Stationen, die erst kurz vor Jahresende entstanden.
        if tag <= (jahr + 1, 3, 31):
            g = r.get('geo') or {}
            for s in g.get('station_groups') or []:
                stationen[s['id']] = (s['x'], s['y'])
            for t in g.get('towns') or []:
                orte[t['id']] = (t['x'], t['y'])
    if not letzte or FAKTEN.day(letzte) > ende:
        sys.exit(f'Keine Messung mit Linien im Jahr {jahr}.')
    return letzte, stationen, orte


def art(line):
    cargo = line.get('cargo') or []
    if not cargo or not all(c.get('passenger') for c in cargo):
        return None
    models = line.get('vehicle_models') or []
    pferd = sum(m.get('vehicles') or 0 for m in models if any(w in (m.get('name') or '').lower() for w in PFERDE))
    alle = sum(m.get('vehicles') or 0 for m in models)
    pferd = alle and pferd * 2 > alle
    return {'RAIL': 'bahn', 'TRAM': 'pferdebahn' if pferd else 'tram',
            'ROAD': 'postkutsche' if pferd else 'omnibus', 'WATER': 'dampfer'}.get(line.get('carrier'))


def nummer(name):
    m = re.search(r'-(LO|IC|RE)-(\d+)$', name or '')
    return (m.group(1), int(m.group(2))) if m else (None, None)


# ---------------------------------------------------------------- Geometrie

def kurve(e):
    """Punkte einer Kante: im Spiel eine Hermite-Kurve aus p0, t0, p1, t1, hier als Bézier abgetastet."""
    x0, y0 = e['p0'][:2]
    x1, y1 = e['p1'][:2]
    a = (x0 + e['t0'][0] / 3, y0 + e['t0'][1] / 3)
    b = (x1 - e['t1'][0] / 3, y1 - e['t1'][1] / 3)
    laenge = math.hypot(x1 - x0, y1 - y0)
    n = max(1, min(16, int(laenge / 12)))
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        pts.append((u * u * u * x0 + 3 * u * u * t * a[0] + 3 * u * t * t * b[0] + t * t * t * x1,
                    u * u * u * y0 + 3 * u * u * t * a[1] + 3 * u * t * t * b[1] + t * t * t * y1))
    return pts


def zuege(kanten):
    """Kanten zu möglichst langen Linienzügen verbinden (über Knoten mit genau zwei Kanten)."""
    nachbarn = defaultdict(list)
    for e in kanten:
        nachbarn[e['n0']].append(e)
        nachbarn[e['n1']].append(e)
    benutzt, out = set(), []

    def gehe(knoten, e):
        pts = []
        while True:
            benutzt.add(e['id'])
            seg = kurve(e) if e['n0'] == knoten else kurve(e)[::-1]
            pts.extend(seg if not pts else seg[1:])
            knoten = e['n1'] if e['n0'] == knoten else e['n0']
            weiter = [f for f in nachbarn[knoten] if f['id'] not in benutzt]
            if len(nachbarn[knoten]) != 2 or not weiter:
                return pts
            e = weiter[0]

    for k, es in nachbarn.items():
        if len(es) != 2:
            for e in es:
                if e['id'] not in benutzt:
                    out.append(gehe(k, e))
    for e in kanten:
        if e['id'] not in benutzt:
            out.append(gehe(e['n0'], e))
    return out


def vereinfachen(pts, tol):
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stapel = [(0, len(pts) - 1)]
    while stapel:
        a, b = stapel.pop()
        (ax, ay), (bx, by) = pts[a], pts[b]
        dx, dy = bx - ax, by - ay
        lang = math.hypot(dx, dy)
        best, idx = -1.0, -1
        for i in range(a + 1, b):
            px, py = pts[i]
            d = abs(dy * px - dx * py + bx * ay - by * ax) / lang if lang else math.hypot(px - ax, py - ay)
            if d > best:
                best, idx = d, i
        if best > tol:
            keep[idx] = True
            stapel += [(a, idx), (idx, b)]
    return [p for p, k in zip(pts, keep) if k]


def chaikin(ring, n=1):
    for _ in range(n):
        out = []
        for i in range(len(ring)):
            (ax, ay), (bx, by) = ring[i], ring[(i + 1) % len(ring)]
            out += [(0.75 * ax + 0.25 * bx, 0.75 * ay + 0.25 * by), (0.25 * ax + 0.75 * bx, 0.25 * ay + 0.75 * by)]
        ring = out
    return ring


def flaeche(ring):
    return abs(sum(ax * by - bx * ay for (ax, ay), (bx, by) in zip(ring, ring[1:] + ring[:1]))) / 2


def konturen(wert, zeilen, spalten, x0, y0, zelle):
    """Ränder der Flächen mit wert(z, s) > 0 als geschlossene Ringe in Weltkoordinaten (Marching Squares).
    Zeile z liegt bei y0 + z * zelle (von Süden nach Norden), Spalte s bei x0 + s * zelle. Außerhalb des Gitters gilt
    alles als außen, so schließen sich alle Ringe."""
    def f(z, s):
        if 0 <= z < zeilen and 0 <= s < spalten:
            return wert(z, s)
        return -1.0

    punkte, nachbarn = {}, defaultdict(list)

    def kante(art_, z, s):
        key = (art_, z, s)
        if key not in punkte:
            if art_ == 'h':   # zwischen (z, s) und (z, s + 1)
                a, b = f(z, s), f(z, s + 1)
                t = a / (a - b)
                punkte[key] = (x0 + (s + t) * zelle, y0 + z * zelle)
            else:             # zwischen (z, s) und (z + 1, s)
                a, b = f(z, s), f(z + 1, s)
                t = a / (a - b)
                punkte[key] = (x0 + s * zelle, y0 + (z + t) * zelle)
        return key

    for z in range(-1, zeilen):
        for s in range(-1, spalten):
            v00, v10, v11, v01 = f(z, s), f(z, s + 1), f(z + 1, s + 1), f(z + 1, s)
            fall = (v00 > 0) | (v10 > 0) << 1 | (v11 > 0) << 2 | (v01 > 0) << 3
            if fall in (0, 15):
                continue
            unten, rechts = ('h', z, s), ('v', z, s + 1)
            oben, links = ('h', z + 1, s), ('v', z, s)
            mitte = (v00 + v10 + v11 + v01) > 0
            paare = {
                1: [(links, unten)], 2: [(unten, rechts)], 3: [(links, rechts)], 4: [(rechts, oben)],
                5: [(links, oben), (unten, rechts)] if mitte else [(links, unten), (rechts, oben)],
                6: [(unten, oben)], 7: [(links, oben)], 8: [(oben, links)], 9: [(unten, oben)],
                10: [(links, unten), (rechts, oben)] if mitte else [(unten, rechts), (oben, links)],
                11: [(rechts, oben)], 12: [(links, rechts)], 13: [(unten, rechts)], 14: [(links, unten)],
            }[fall]
            for a, b in paare:
                ka, kb = kante(*a), kante(*b)
                nachbarn[ka].append(kb)
                nachbarn[kb].append(ka)

    ringe, besucht = [], set()
    for start in list(nachbarn):
        if start in besucht:
            continue
        ring, vorher, jetzt = [], None, start
        while jetzt not in besucht:
            besucht.add(jetzt)
            ring.append(punkte[jetzt])
            nb = nachbarn[jetzt]
            weiter = nb[0] if nb[0] != vorher or len(nb) == 1 else nb[1]
            vorher, jetzt = jetzt, weiter
        if len(ring) > 2:
            ringe.append(ring)
    return ringe


class Gelaende:
    def __init__(self, pfad):
        g = json.loads(Path(pfad).read_text(encoding='utf-8'))
        assert g.get('row_order') == 'min_y_first', g.get('row_order')
        self.h, self.zelle = g['heights'], g['cell_m']
        self.x0, self.y0 = g['min_x'], g['min_y']
        self.zeilen, self.spalten = len(self.h), len(self.h[0])
        self.wasserstand = g.get('water_level', 0)

    def wasser(self, z, s):
        return self.wasserstand - self.h[z][s]

    def ufer(self, box):
        """Wasserflächen in einem Weltausschnitt (x0, y0, x1, y1), etwas größer gerechnet als gezeigt."""
        bx0, by0, bx1, by1 = box
        s0 = max(0, int((bx0 - self.x0) / self.zelle) - 2)
        s1 = min(self.spalten, int((bx1 - self.x0) / self.zelle) + 3)
        z0 = max(0, int((by0 - self.y0) / self.zelle) - 2)
        z1 = min(self.zeilen, int((by1 - self.y0) / self.zelle) + 3)
        ringe = konturen(lambda z, s: self.wasser(z0 + z, s0 + s), z1 - z0, s1 - s0,
                         self.x0 + s0 * self.zelle, self.y0 + z0 * self.zelle, self.zelle)
        return [chaikin(r, 2) for r in ringe if flaeche(r) > 3 * self.zelle ** 2]

    def kurs(self, a, b):
        """Kürzester Weg über Wasser zwischen zwei Anlegern (A* auf dem Geländegitter)."""
        def zelle_von(p):
            s = round((p[0] - self.x0) / self.zelle)
            z = round((p[1] - self.y0) / self.zelle)
            best = None
            for r in range(0, 8):
                for dz in range(-r, r + 1):
                    for ds in range(-r, r + 1):
                        zz, ss = z + dz, s + ds
                        if 0 <= zz < self.zeilen and 0 <= ss < self.spalten and self.wasser(zz, ss) > 0.5:
                            d = dz * dz + ds * ds
                            if best is None or d < best[0]:
                                best = (d, (zz, ss))
                if best:
                    return best[1]
            return None

        start, ziel = zelle_von(a), zelle_von(b)
        if not start or not ziel:
            return [a, b]
        offen = [(0.0, start)]
        kosten, von = {start: 0.0}, {start: None}
        while offen:
            _, jetzt = heapq.heappop(offen)
            if jetzt == ziel:
                break
            for dz in (-1, 0, 1):
                for ds in (-1, 0, 1):
                    if not dz and not ds:
                        continue
                    n = (jetzt[0] + dz, jetzt[1] + ds)
                    if not (0 <= n[0] < self.zeilen and 0 <= n[1] < self.spalten) or self.wasser(*n) <= 0.5:
                        continue
                    k = kosten[jetzt] + math.hypot(dz, ds)
                    if k < kosten.get(n, 1e18):
                        kosten[n], von[n] = k, jetzt
                        heapq.heappush(offen, (k + math.hypot(n[0] - ziel[0], n[1] - ziel[1]), n))
        if ziel not in von:
            return [a, b]
        weg, z = [], ziel
        while z:
            weg.append((self.x0 + z[1] * self.zelle, self.y0 + z[0] * self.zelle))
            z = von[z]
        weg = vereinfachen([b] + weg + [a], self.zelle * 0.7)[::-1]
        return chaikin(weg, 3)[1:-1] if len(weg) > 2 else weg


def ortslagen(bauten, box, zelle):
    """Bebaute Flächen aus den Gebäuden des Kartenexports, als geglättete Ringe."""
    bx0, by0, bx1, by1 = box
    spalten, zeilen = int((bx1 - bx0) / zelle) + 2, int((by1 - by0) / zelle) + 2
    gitter = [[0] * spalten for _ in range(zeilen)]
    for b in bauten:
        if b.get('town') is None or not b.get('bb'):
            continue
        x0, y0, _, x1, y1, _ = b['bb']
        if x1 < bx0 or x0 > bx1 or y1 < by0 or y0 > by1:
            continue
        for z in range(max(0, int((y0 - by0) / zelle)), min(zeilen, int((y1 - by0) / zelle) + 1)):
            for s in range(max(0, int((x0 - bx0) / zelle)), min(spalten, int((x1 - bx0) / zelle) + 1)):
                gitter[z][s] = 1
    # schließen: erst ausdehnen, dann zurücknehmen, damit Lücken zwischen Häusern zu einer Ortslage werden
    def schritt(g, ausdehnen):
        out = [[0] * spalten for _ in range(zeilen)]
        for z in range(zeilen):
            for s in range(spalten):
                feld = [g[zz][ss] for zz in (z - 1, z, z + 1) for ss in (s - 1, s, s + 1)
                        if 0 <= zz < zeilen and 0 <= ss < spalten]
                out[z][s] = int(any(feld)) if ausdehnen else int(all(feld) and len(feld) == 9)
        return out
    gitter = schritt(schritt(gitter, True), False)
    ringe = konturen(lambda z, s: 1.0 if gitter[z][s] else -1.0, zeilen, spalten, bx0 + zelle / 2, by0 + zelle / 2, zelle)
    return [chaikin(r, 2) for r in ringe if flaeche(r) > 4 * zelle ** 2]


# ---------------------------------------------------------------- Zeichnen

def f1(v):
    s = f'{v:.1f}'
    return s[:-2] if s.endswith('.0') else s


class Ansicht:
    def __init__(self, box, breite, rand=RAND):
        self.x0, self.y0, self.x1, self.y1 = box
        self.s = (breite - 2 * rand) / (self.x1 - self.x0)
        self.rand, self.breite = rand, breite
        self.hoehe = round(2 * rand + (self.y1 - self.y0) * self.s)
        self.spuren = []   # gezeichnete Linien in Bildpunkten; Beschriftungen weichen ihnen aus

    def px(self, p):
        return (self.rand + (p[0] - self.x0) * self.s, self.rand + (self.y1 - p[1]) * self.s)

    def innen(self, p, mehr=0):
        x, y = p
        return -mehr <= x <= self.breite + mehr and -mehr <= y <= self.hoehe + mehr

    def linien(self, zuege, tol=0.35, mehr=24, merken=False):
        """Linienzüge in Bildpunkten, auf den Ausschnitt zugeschnitten und vereinfacht, als SVG-Pfad."""
        teile = []
        for pts in zuege:
            pts = [self.px(p) for p in pts]
            lauf = []
            for i, p in enumerate(pts):
                nah = self.innen(p, mehr) or (i and self.innen(pts[i - 1], mehr)) or \
                    (i + 1 < len(pts) and self.innen(pts[i + 1], mehr))
                if nah:
                    lauf.append(p)
                else:
                    if len(lauf) > 1:
                        teile.append(lauf)
                    lauf = []
            if len(lauf) > 1:
                teile.append(lauf)
        teile = [vereinfachen(t, tol) for t in teile]
        if merken:
            self.spuren += teile
        return ''.join('M' + ' '.join(f'{f1(x)},{f1(y)}' for x, y in t) for t in teile)

    def hindernisse(self, platz, abstand=5, halb=1.6):
        for lauf in self.spuren:
            for (ax, ay), (bx, by) in zip(lauf, lauf[1:]):
                n = max(1, int(math.hypot(bx - ax, by - ay) / abstand))
                for i in range(n + 1):
                    x, y = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
                    platz.nimm((x - halb, y - halb, x + halb, y + halb))

    def ringe(self, ringe, tol=0.35, mehr=24):
        box = (-mehr, -mehr, self.breite + mehr, self.hoehe + mehr)
        teile = []
        for r in ringe:
            r = beschneiden([self.px(p) for p in r], box)
            if len(r) < 3:
                continue
            r = vereinfachen(r + r[:1], tol)[:-1]
            if len(r) > 2:
                teile.append('M' + ' '.join(f'{f1(x)},{f1(y)}' for x, y in r) + 'Z')
        return ''.join(teile)


def beschneiden(ring, box):
    """Vieleck auf ein Rechteck zuschneiden (Sutherland-Hodgman)."""
    x0, y0, x1, y1 = box
    seiten = (
        (lambda p: p[0] >= x0, lambda a, b: (x0, a[1] + (b[1] - a[1]) * (x0 - a[0]) / (b[0] - a[0]))),
        (lambda p: p[0] <= x1, lambda a, b: (x1, a[1] + (b[1] - a[1]) * (x1 - a[0]) / (b[0] - a[0]))),
        (lambda p: p[1] >= y0, lambda a, b: (a[0] + (b[0] - a[0]) * (y0 - a[1]) / (b[1] - a[1]), y0)),
        (lambda p: p[1] <= y1, lambda a, b: (a[0] + (b[0] - a[0]) * (y1 - a[1]) / (b[1] - a[1]), y1)),
    )
    for innen, schnitt in seiten:
        if not ring:
            break
        out = []
        for i, jetzt in enumerate(ring):
            vorher = ring[i - 1]
            if innen(jetzt):
                if not innen(vorher):
                    out.append(schnitt(vorher, jetzt))
                out.append(jetzt)
            elif innen(vorher):
                out.append(schnitt(vorher, jetzt))
        ring = out
    return ring


class Platz:
    """Freie Plätze für Beschriftungen: einfache Belegung von Rechtecken."""
    def __init__(self, breite, hoehe):
        self.boxen, self.breite, self.hoehe = [], breite, hoehe

    def frei(self, b, luft=1.5):
        if b[0] < 3 or b[1] < 3 or b[2] > self.breite - 3 or b[3] > self.hoehe - 3:
            return False
        return all(b[2] + luft < o[0] or o[2] + luft < b[0] or b[3] + luft < o[1] or o[3] + luft < b[1]
                   for o in self.boxen)

    def nimm(self, b):
        self.boxen.append(b)

    def ueberdeckung(self, b):
        aussen = max(0, 3 - b[0]) + max(0, 3 - b[1]) + max(0, b[2] - self.breite + 3) + max(0, b[3] - self.hoehe + 3)
        return aussen * 1000 + sum(max(0, min(b[2], o[2]) - max(b[0], o[0])) * max(0, min(b[3], o[3]) - max(b[1], o[1]))
                                   for o in self.boxen)


def textbreite(text, groesse, faktor=0.47):
    return len(text) * groesse * faktor


def beschriften(platz, x, y, r, text, groesse, klasse, faktor=0.47, pflicht=False):
    """Beschriftung neben einen Punkt setzen: rechts, links, oben, unten, schräg, dann etwas weiter weg. Findet sich
    kein freier Platz, bekommt eine Pflichtbeschriftung den Platz mit der kleinsten Überdeckung."""
    w, h = textbreite(text, groesse, faktor), groesse
    kandidaten = []
    for d in (0, 6, 12):
        s = d * 0.7
        kandidaten += [
            (x + r + 3 + d, y + h * 0.33, 'start'), (x - r - 3 - d, y + h * 0.33, 'end'),
            (x, y - r - 3 - d, 'middle'), (x, y + r + h * 0.8 + d, 'middle'),
            (x + r + 1 + s, y - r - 1 - s, 'start'), (x + r + 1 + s, y + r + h * 0.75 + s, 'start'),
            (x - r - 1 - s, y - r - 1 - s, 'end'), (x - r - 1 - s, y + r + h * 0.75 + s, 'end'),
        ]

    def box(k):
        tx, ty, anker = k
        bx0 = tx if anker == 'start' else tx - w if anker == 'end' else tx - w / 2
        return (bx0, ty - h * 0.78, bx0 + w, ty + h * 0.22)

    wahl = next((k for k in kandidaten if platz.frei(box(k))), None)
    if wahl is None:
        if not pflicht:
            return ''
        wahl = min(kandidaten, key=lambda k: platz.ueberdeckung(box(k)))
    platz.nimm(box(wahl))
    tx, ty, anker = wahl
    return f'<text class="{klasse}" x="{f1(tx)}" y="{f1(ty)}" text-anchor="{anker}">{html.escape(text)}</text>'


def massstab(x, y, ansicht, meter, schritte, einheit, beschrift):
    """Maßstabsleiste mit abwechselnd gefüllten Feldern."""
    teil = meter / schritte * ansicht.s
    out = [f'<g class="np-massstab" transform="translate({f1(x)},{f1(y)})">']
    for i in range(schritte):
        out.append(f'<rect x="{f1(i * teil)}" y="0" width="{f1(teil)}" height="4" class="{"np-voll" if i % 2 == 0 else "np-leer"}"/>')
    for i in range(schritte + 1):
        out.append(f'<text x="{f1(i * teil)}" y="15" text-anchor="middle">{beschrift(meter / schritte * i)}</text>')
    out.append(f'<text x="{f1(schritte * teil + 6)}" y="5" class="np-einheit">{einheit}</text></g>')
    return ''.join(out)


# ---------------------------------------------------------------- Plan

class Plan:
    def __init__(self, jahr, monitor):
        self.jahr = jahr
        self.stilname, self.stil = stil(jahr)
        self.kapitel, self.seite, self.staffel, export, gelaende = kapitel_export(jahr, monitor)
        row, self.lage, self.ortlage = messungen(monitor, jahr)
        self.tag = FAKTEN.day(row)
        self.export_tag = tuple(export['game_date'][k] for k in ('year', 'month', 'day'))
        self.kanten = {e['id']: e for e in export['kanten']}
        self.bauten = export['bauten']
        export_linien = {l['line']: l for l in export['linien']}
        self.gelaende = Gelaende(gelaende)
        self.orte = {t['id']: {'name': t['name'], 'einwohner': FAKTEN.residents(t),
                               'lage': self.ortlage.get(t['id'])} for t in row.get('towns') or []}
        self.linien = []
        for l in row['lines']:
            a = art(l)
            if not a:
                continue
            ids = l.get('station_group_ids') or []
            namen = l.get('station_names') or []
            halte = [(i, n, self.lage[i]) for i, n in zip(ids, namen) if i in self.lage]
            ex = export_linien.get(l['id'])
            kanten = [self.kanten[i] for i in (ex or {}).get('edges', []) if i in self.kanten]
            typ, nr = nummer(l.get('name'))
            self.linien.append({'id': l['id'], 'name': l['name'], 'art': a, 'typ': typ, 'nr': nr, 'halte': halte,
                                'kanten': kanten, 'fahrzeuge': l.get('vehicles') or 0, 'im_export': bool(ex)})
        for l in self.linien:
            l['ort'] = self.naechster_ort(l['halte'])
        bahn = {e['id'] for l in self.linien if l['art'] == 'bahn' for e in l['kanten']}
        self.gueterbahn = [e for e in export['kanten'] if e.get('rt') == 'track' and e['id'] not in bahn]
        self.strassen = [e for e in export['kanten'] if e.get('rt') == 'street']
        self.kurse = {}
        for l in self.linien:
            if l['art'] == 'dampfer':
                l['kurs'] = []
                for (_, _, a), (_, _, b) in zip(l['halte'], l['halte'][1:]):
                    key = tuple(sorted((a, b)))
                    if key not in self.kurse:
                        self.kurse[key] = self.gelaende.kurs(a, b)
                    l['kurs'].append(self.kurse[key])

    def naechster_ort(self, halte):
        if not halte:
            return None
        mx = sum(p[0] for _, _, p in halte) / len(halte)
        my = sum(p[1] for _, _, p in halte) / len(halte)
        kandidaten = [(math.hypot(o['lage'][0] - mx, o['lage'][1] - my), oid) for oid, o in self.orte.items() if o['lage']]
        return min(kandidaten)[1] if kandidaten else None

    def netz(self, arten):
        """Alle Kanten der Linien dieser Arten, jede einmal, als Linienzüge."""
        kanten = {}
        for l in self.linien:
            if l['art'] in arten:
                for e in l['kanten']:
                    kanten[e['id']] = e
        return zuege(list(kanten.values()))

    def kennung(self, teil):
        return f'np{self.jahr}-{teil}'

    # ------------------------------------------------------------ Übersichtskarte

    def ausschnitt(self):
        pts = [p for l in self.linien for _, _, p in l['halte']]
        pts += [e['p0'][:2] for l in self.linien for e in l['kanten']]
        x0, x1 = min(p[0] for p in pts) - 900, max(p[0] for p in pts) + 900
        y0, y1 = min(p[1] for p in pts) - 900, max(p[1] for p in pts) + 700
        g = self.gelaende
        x0, x1 = max(x0, g.x0), min(x1, g.x0 + g.spalten * g.zelle)
        y0, y1 = max(y0, g.y0), min(y1, g.y0 + g.zeilen * g.zelle)
        return (x0, y0, x1, y1)

    def karte(self):
        box = self.ausschnitt()
        v = Ansicht(box, KARTE_PX)
        k = self.kennung
        teile = []
        defs = []
        # Gewässer mit Uferlinien im Stich alter Karten
        wasser = v.ringe(self.gelaende.ufer(box), tol=0.5)
        if wasser:
            defs.append(f'<path id="{k("ufer")}" d="{wasser}"/>')
            defs.append(f'<clipPath id="{k("see")}"><use href="#{k("ufer")}"/></clipPath>')
            teile.append(f'<use href="#{k("ufer")}" class="np-wasser"/>')
            teile.append(f'<g clip-path="url(#{k("see")})">' + ''.join(
                f'<use href="#{k("ufer")}" class="np-welle" style="stroke-width:{w}px"/>'
                f'<use href="#{k("ufer")}" class="np-welle-papier" style="stroke-width:{w - 0.9}px"/>'
                for w in (22, 15, 9)) + '</g>')
            teile.append(f'<use href="#{k("ufer")}" class="np-ufer"/>')
        orte = v.ringe(ortslagen(self.bauten, box, 40), tol=0.4)
        if orte:
            teile.append(f'<path class="np-ortslage" d="{orte}"/>')
        teile.append(f'<path class="np-gueterbahn" d="{v.linien(zuege(self.gueterbahn), 0.4)}"/>')
        teile += self.linienzeichen(v, tol=0.35)
        platz = Platz(v.breite, v.hoehe)
        v.hindernisse(platz)
        punkte = []
        # Bahnhöfe des Personenzugs
        bahnhoefe = {}
        for l in self.linien:
            if l['art'] == 'bahn':
                for _, n, p in l['halte']:
                    bahnhoefe[n] = p
        for n, p in bahnhoefe.items():
            x, y = v.px(p)
            punkte.append(f'<circle class="np-bahnhof" cx="{f1(x)}" cy="{f1(y)}" r="3.6"/>')
            platz.nimm((x - 4, y - 4, x + 4, y + 4))
        # Ortsnamen: Orte mit Linien zuerst und mindestens mittelgroß, sonst nach Einwohnern
        namen = []
        bedient = {l['ort'] for l in self.linien if l['ort']}
        for oid, o in sorted(self.orte.items(), key=lambda kv: (kv[0] not in bedient, -kv[1]['einwohner'])):
            if not o['lage']:
                continue
            x, y = v.px(o['lage'])
            if not (RAND < x < v.breite - RAND and RAND < y < v.hoehe - RAND):
                continue
            e = o['einwohner']
            if e >= 800:
                groesse, klasse = 15, 'np-ort np-ort--gross'
            elif e >= 300 or oid in bedient:
                groesse, klasse = 12.5, 'np-ort'
            else:
                groesse, klasse = 10.5, 'np-ort np-ort--klein'
            punkte.append(f'<circle class="np-ortszeichen" cx="{f1(x)}" cy="{f1(y)}" r="2.2"/>')
            namen.append(beschriften(platz, x, y, 3, o['name'], groesse, klasse, faktor=0.6 if groesse > 11 else 0.46,
                                     pflicht=oid in bedient or e >= 300))
        # Anleger der Dampfer außerhalb der Orte
        for key in sorted({(n, p) for l in self.linien if l['art'] == 'dampfer' for _, n, p in l['halte']}):
            n, p = key
            if any(o['lage'] and math.hypot(o['lage'][0] - p[0], o['lage'][1] - p[1]) < 900 for o in self.orte.values()):
                continue
            x, y = v.px(p)
            punkte.append(f'<circle class="np-anleger" cx="{f1(x)}" cy="{f1(y)}" r="2.4"/>')
            namen.append(beschriften(platz, x, y, 3, n, 10, 'np-anleger-name', faktor=0.45))
        teile += punkte + namen
        # Kopf, Maßstab und Zeichen-Erklärung im Band unter der Karte, damit nichts vom Netz verdeckt wird
        hoehe = v.hoehe + BAND
        rahmen = (f'<rect class="np-rahmen" x="2" y="2" width="{v.breite - 4}" height="{hoehe - 4}"/>'
                  f'<rect class="np-rahmen-innen" x="6" y="6" width="{v.breite - 12}" height="{hoehe - 12}"/>')
        defs.append(f'<clipPath id="{k("feld")}"><rect x="6" y="6" width="{v.breite - 12}" height="{v.hoehe - 6}"/></clipPath>')
        titel = f'Erlental, {self.stil["kopf"]}, Stand vom {datum(self.tag)}'
        beschreibung = self.beschreibung()
        return (f'<svg class="np-karte" viewBox="0 0 {v.breite} {hoehe}" width="{v.breite}" height="{hoehe}" role="img" '
                f'aria-labelledby="{k("t")} {k("d")}"><title id="{k("t")}">{html.escape(titel)}</title>'
                f'<desc id="{k("d")}">{html.escape(beschreibung)}</desc><defs>{"".join(defs)}</defs>'
                f'<rect class="np-papier" width="{v.breite}" height="{hoehe}"/>'
                f'<g clip-path="url(#{k("feld")})">{"".join(teile)}</g>{self.band(v)}{rahmen}</svg>')

    def linienzeichen(self, v, tol):
        """Linien aller Arten in Zeichenreihenfolge; der Personenzug im schwarz-weißen Bahnzeichen."""
        out = []
        for a in ARTEN:
            if a == 'dampfer':
                kurse = [k for l in self.linien if l['art'] == a for k in l['kurs']]
                if kurse:
                    out.append(f'<path class="np-dampfer" d="{v.linien(kurse, tol, merken=True)}"/>')
                continue
            netz = self.netz({a})
            if not netz:
                continue
            d = v.linien(netz, tol, merken=True)
            if a == 'bahn':
                out.append(f'<path class="np-bahn" d="{d}"/><path class="np-bahn-weiss" d="{d}"/>')
            else:
                out.append(f'<path class="np-{a}" d="{d}"/>')
        return out

    def legende_eintraege(self):
        da = {l['art'] for l in self.linien}
        eintraege = [(a, ARTEN[a]) for a in reversed(list(ARTEN)) if a in da]
        eintraege += [('gueterbahn', 'Güterbahn'), ('bahnhof', 'Bahnhof'), ('halt', 'Haltestelle'),
                      ('nr', 'Liniennummer'), ('ortslage', 'Ortslage')]
        return eintraege

    def band(self, v):
        """Kopf mit Maßstab links, Zeichen-Erklärung in drei Spalten rechts."""
        y0 = v.hoehe
        m = 136
        km = 5 if v.s * 5000 < 230 else 2
        lang = km * 1000 * v.s
        out = [f'<path class="np-trenner" d="M6,{y0}H{v.breite - 6}M6,{y0 + 3}H{v.breite - 6}"/>',
               f'<g class="np-kopf"><text class="np-kopf-ober" x="{m}" y="{y0 + 25}" text-anchor="middle">{html.escape(self.stil["kopf"])}</text>'
               f'<text class="np-kopf-titel" x="{m}" y="{y0 + 53}" text-anchor="middle">Erlental</text>'
               f'<text class="np-kopf-stand" x="{m}" y="{y0 + 71}" text-anchor="middle">Stand vom {datum(self.tag)}</text></g>',
               massstab(m - lang / 2, y0 + 82, v, km * 1000, km, 'km', lambda x: f'{x / 1000:g}'),
               f'<path class="np-trenner" d="M272,{y0 + 14}V{y0 + BAND - 14}"/>',
               f'<g class="np-legende"><text class="np-legende-kopf" x="288" y="{y0 + 24}">{self.stil["legende"]}</text>']
        eintraege = self.legende_eintraege()
        zeilen = math.ceil(len(eintraege) / 3)
        for i, (a, text) in enumerate(eintraege):
            x0 = 288 + (i // zeilen) * 158
            yy = y0 + 43 + (i % zeilen) * 17
            x1 = x0 + 28
            mx = (x0 + x1) / 2
            strich = f'M{f1(x0)},{f1(yy)}H{f1(x1)}'
            if a == 'bahn':
                z = f'<path class="np-bahn" d="{strich}"/><path class="np-bahn-weiss" d="{strich}"/>'
            elif a == 'bahnhof':
                z = f'<circle class="np-bahnhof" cx="{f1(mx)}" cy="{f1(yy)}" r="3.6"/>'
            elif a == 'halt':
                z = f'<circle class="np-halt" cx="{f1(mx)}" cy="{f1(yy)}" r="3.3"/>'
            elif a == 'nr':
                z = (f'<g class="np-nr np-nr--tram"><circle cx="{f1(x0 + 6)}" cy="{f1(yy)}" r="6"/><text x="{f1(x0 + 6)}" y="{f1(yy + 3.3)}" text-anchor="middle">1</text></g>'
                     f'<g class="np-nr np-nr--bus"><rect x="{f1(x1 - 11.5)}" y="{f1(yy - 5.5)}" width="11" height="11" rx="1.5"/><text x="{f1(x1 - 6)}" y="{f1(yy + 3.3)}" text-anchor="middle">3</text></g>')
            elif a == 'ortslage':
                z = f'<rect class="np-ortslage" x="{f1(x0 + 3)}" y="{f1(yy - 5)}" width="22" height="10" rx="3"/>'
            else:
                z = f'<path class="np-{a}" d="{strich}"/>'
            out.append(z + f'<text x="{f1(x1 + 7)}" y="{f1(yy + 3.8)}">{html.escape(text)}</text>')
        out.append('</g>')
        return ''.join(out)

    def beschreibung(self):
        teile = []
        bahn = [l for l in self.linien if l['art'] == 'bahn']
        for l in bahn:
            halte = list(dict.fromkeys(n for _, n, _ in l['halte']))
            teile.append('Personenzug über ' + ', '.join(halte))
        staedte = sorted({self.orte[l['ort']]['name'] for l in self.linien if l['art'] in ('tram', 'pferdebahn') and l['ort']})
        if staedte:
            teile.append('Straßenbahnen in ' + ', '.join(staedte))
        for a, wort in (('omnibus', 'Omnibuslinien'), ('postkutsche', 'Postkutschenlinien'), ('dampfer', 'Dampferlinien')):
            n = sum(1 for l in self.linien if l['art'] == a)
            if n:
                teile.append(f'{n} {wort}')
        return '. '.join(teile) + '.'

    # ------------------------------------------------------------ Stadtpläne

    def staedte(self):
        orte = defaultdict(list)
        for l in self.linien:
            if l['art'] in ('tram', 'pferdebahn') and l['ort']:
                orte[l['ort']].append(l)
        return sorted(orte, key=lambda oid: -self.orte[oid]['einwohner'])

    def stadtplan(self, oid):
        ort = self.orte[oid]
        mx, my = ort['lage']
        nah = lambda p, r: math.hypot(p[0] - mx, p[1] - my) < r  # noqa: E731
        # Halte der Ortslinien bis 1 km um die Ortsmitte; weiter draußen (Silberweide 1911: Kirchgasse, Mettmann Bauernhof)
        # liefe die Straßenbahn klein in einer Ecke. Solche Linien laufen über den Rand hinaus.
        pts = [p for l in self.linien if l['ort'] == oid and l['typ'] == 'LO' and l['art'] != 'dampfer'
               for _, _, p in l['halte'] if nah(p, 1000)]
        pts += [p for l in self.linien if l['art'] == 'bahn' for _, _, p in l['halte'] if nah(p, 1500)]
        x0, x1 = min(p[0] for p in pts) - 170, max(p[0] for p in pts) + 170
        y0, y1 = min(p[1] for p in pts) - 150, max(p[1] for p in pts) + 150
        # Mindestgröße und Seitenverhältnis 4:3
        w, h = max(x1 - x0, 900), max(y1 - y0, 675)
        if w / h > 4 / 3:
            h = w * 3 / 4
        else:
            w = h * 4 / 3
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
        v = Ansicht(box, STADT_PX, rand=0)
        k = lambda t: self.kennung(f'{oid}-{t}')  # noqa: E731
        teile, defs = [], []
        wasser = v.ringe(self.gelaende.ufer(box), tol=0.4)
        if wasser:
            defs.append(f'<path id="{k("ufer")}" d="{wasser}"/>')
            defs.append(f'<clipPath id="{k("see")}"><use href="#{k("ufer")}"/></clipPath>')
            teile.append(f'<use href="#{k("ufer")}" class="np-wasser"/>')
            teile.append(f'<g clip-path="url(#{k("see")})">' + ''.join(
                f'<use href="#{k("ufer")}" class="np-welle" style="stroke-width:{w_}px"/>'
                f'<use href="#{k("ufer")}" class="np-welle-papier" style="stroke-width:{w_ - 0.9}px"/>'
                for w_ in (16, 10)) + '</g>')
            teile.append(f'<use href="#{k("ufer")}" class="np-ufer"/>')
        orte = v.ringe(ortslagen(self.bauten, box, 16), tol=0.5)
        if orte:
            teile.append(f'<path class="np-ortslage" d="{orte}"/>')
        nahe = lambda e: any(box[0] - 300 < p[0] < box[2] + 300 and box[1] - 300 < p[1] < box[3] + 300  # noqa: E731
                             for p in (e['p0'], e['p1']))
        strassen = [e for e in self.strassen if nahe(e)]
        teile.append(f'<path class="np-strasse" d="{v.linien(zuege(strassen), 0.3)}"/>')
        teile.append(f'<path class="np-gueterbahn" d="{v.linien(zuege([e for e in self.gueterbahn if nahe(e)]), 0.3)}"/>')
        teile += self.linienzeichen(v, tol=0.3)
        platz = Platz(v.breite, v.hoehe)
        v.hindernisse(platz)
        titel_w = textbreite(ort['name'], 16, 0.8) + 22
        platz.nimm((0, 0, titel_w + 8, 30))
        platz.nimm((v.breite - 190, v.hoehe - 30, v.breite, v.hoehe))
        # Haltestellen: alle Halte der gezeigten Linien im Ausschnitt
        halte = {}
        for l in self.linien:
            for gid, n, p in l['halte']:
                x, y = v.px(p)
                if 6 < x < v.breite - 6 and 6 < y < v.hoehe - 6:
                    eintrag = halte.setdefault(gid, {'name': n, 'xy': (x, y), 'arten': set()})
                    eintrag['arten'].add(l['art'])
        zeichen, namen = [], []
        for gid, h in halte.items():
            x, y = h['xy']
            if 'bahn' in h['arten']:
                zeichen.append(f'<rect class="np-bahnhof" x="{f1(x - 5)}" y="{f1(y - 3.2)}" width="10" height="6.4" rx="1"/>')
            else:
                zeichen.append(f'<circle class="np-halt" cx="{f1(x)}" cy="{f1(y)}" r="3.3"/>')
            platz.nimm((x - 5, y - 5, x + 5, y + 5))
        # Liniennummern am ersten Halt jeder Linie des Ortes
        marken = []
        an_halt = defaultdict(list)
        for l in sorted(self.linien, key=lambda l: (l['art'], l['nr'] or 0)):
            if l['ort'] != oid or l['typ'] != 'LO' or not l['halte'] or l['art'] == 'dampfer':
                continue
            gid = l['halte'][0][0]
            if gid in halte:
                an_halt[gid].append(l)
        for gid, ls in an_halt.items():
            x, y = halte[gid]['xy']
            for i, l in enumerate(ls):
                bx, by = x + 8 + i * 13, y - 10
                kl = 'np-nr np-nr--tram' if l['art'] in ('tram', 'pferdebahn') else 'np-nr np-nr--bus'
                form = (f'<circle cx="{f1(bx)}" cy="{f1(by)}" r="6"/>' if 'tram' in kl
                        else f'<rect x="{f1(bx - 5.5)}" y="{f1(by - 5.5)}" width="11" height="11" rx="1.5"/>')
                marken.append(f'<g class="{kl}">{form}<text x="{f1(bx)}" y="{f1(by + 3.3)}" text-anchor="middle">{l["nr"]}</text></g>')
                platz.nimm((bx - 6.5, by - 6.5, bx + 6.5, by + 6.5))
        kurz = ort['name'] + ' '
        for gid, h in sorted(halte.items(), key=lambda kv: ('bahn' not in kv[1]['arten'], kv[1]['xy'][1])):
            x, y = h['xy']
            n = h['name']
            if n.startswith(kurz) and len(n) > len(kurz) + 2:
                n = n[len(kurz):]
            kl = 'np-halt-name np-halt-name--bahn' if 'bahn' in h['arten'] else 'np-halt-name'
            namen.append(beschriften(platz, x, y, 4, n, 10.5, kl, faktor=0.44, pflicht=True))
        teile += zeichen + marken + namen
        teile.append(f'<g class="np-stadt-kopf"><rect class="np-kasten" x="-1" y="-1" width="{f1(titel_w)}" height="27"/>'
                     f'<text class="np-stadt-name" x="11" y="18.5">{html.escape(ort["name"])}</text></g>')
        meter = 500 if v.s * 500 < v.breite / 3 else 250
        teile.append(massstab(v.breite - meter * v.s - 26, v.hoehe - 22, v, meter, 2, 'm', lambda m: f'{m:g}'))
        defs.append(f'<clipPath id="{k("feld")}"><rect width="{v.breite}" height="{v.hoehe}"/></clipPath>')
        linien = [l for l in self.linien if l['ort'] == oid and l['typ'] == 'LO' and l['art'] in ('tram', 'pferdebahn')]
        wort = 'Pferdebahn' if all(l['art'] == 'pferdebahn' for l in linien) else 'Straßenbahn'
        nummern = sorted(l['nr'] for l in linien)
        titel = f'Stadtplan {ort["name"]}: {wort}, Linie{"n" if len(nummern) > 1 else ""} {", ".join(map(str, nummern))}'
        return (f'<figure class="np-stadt"><svg viewBox="0 0 {v.breite} {v.hoehe}" width="{v.breite}" height="{v.hoehe}" role="img" '
                f'aria-label="{html.escape(titel)}"><defs>{"".join(defs)}</defs>'
                f'<rect class="np-papier" width="{v.breite}" height="{v.hoehe}"/><g clip-path="url(#{k("feld")})">{"".join(teile)}</g>'
                f'<rect class="np-rahmen-stadt" x=".5" y=".5" width="{v.breite - 1}" height="{v.hoehe - 1}"/></svg></figure>')

    # ------------------------------------------------------------ Seite

    def html(self):
        staedte = self.staedte()
        namen = [self.orte[o]['name'] for o in staedte]
        liste = ', '.join(namen[:-1]) + ' und ' + namen[-1] if len(namen) > 1 else ''.join(namen)
        kap = self.kapitel['titel'].split(' · ')[0] if ' · ' in self.kapitel['titel'] else self.kapitel['titel']
        np = (f'<div class="np np--{self.stilname}" data-jahr="{self.jahr}">'
              f'<div class="np-scroll">{self.karte()}</div>'
              f'<details class="np-staedte" open><summary>{html.escape(self.stil["staedte"])}: {html.escape(liste)}</summary>'
              f'<div class="np-raster">{"".join(self.stadtplan(o) for o in staedte)}</div></details>'
              f'<p class="np-nachweis">Gezeichnet nach der Messung vom {datum(self.tag)} und dem Kartenexport vom '
              f'{datum(self.export_tag)}: Linien, Halte und Fahrzeuge laut Messung, Verlauf über Straßen und Gleise, Ortslagen '
              f'aus den Gebäuden, Gewässer aus dem Geländescan. Dampfer fahren frei über das Wasser; gezeichnet ist der kürzeste '
              f'Kurs zwischen den Anlegern. Liniennummern wie im Spiel; Kreise für Straßenbahnen, Quadrate für Omnibusse und '
              f'Postkutschen.</p></div>')
        zurueck = f'../{self.seite}#netzplan-{self.jahr}'
        return ('<!doctype html>\n<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                f'<title>Erlental · Netzplan {self.jahr}</title>'
                '<link rel="stylesheet" href="../../../assets/erlental.css?v=20261102-netzplan"></head>\n'
                f'<body class="et np-seite"><main class="shell np-seite-inhalt"><p class="np-zurueck"><a href="{zurueck}">'
                f'{html.escape(self.staffel or "Chronik")}, {html.escape(kap)}</a></p>\n{np}\n</main></body></html>\n')


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('jahr', type=int)
    p.add_argument('--monitor', default=str(ROOT.parent/'Spielmonitor'))
    p.add_argument('--out', default=str(ROOT/'saves/erlental/netzplan'))
    a = p.parse_args()
    plan = Plan(a.jahr, a.monitor)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    ziel = out/f'{a.jahr}.html'
    text = plan.html()
    ziel.write_text(text, encoding='utf-8', newline='\n')
    print(f'{ziel.relative_to(ROOT) if ziel.is_relative_to(ROOT) else ziel}: {len(text.encode()) // 1024} KB, '
          f'Stil {plan.stilname}, Messung {datum(plan.tag)}, '
          f'Export {datum(plan.export_tag)}')
    for l in sorted(plan.linien, key=lambda l: (list(ARTEN).index(l['art']), l['name'])):
        ort = plan.orte.get(l['ort'], {}).get('name')
        print(f"  {ARTEN[l['art']]:26s} {l['name']:34s} {ort or '-':14s} Halte {len(l['halte'])} Kanten {len(l['kanten'])}"
              f"{'' if l['im_export'] or l['art'] == 'dampfer' else ' (nicht im Export)'}")
    print('  Stadtpläne:', ', '.join(plan.orte[o]['name'] for o in plan.staedte()))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()
