"""Sea chart background in the style of an old engraved map (Rubrik „Karte“), rendered with Blender from karte.json.

Runs inside Blender, no other packages (Blender ships numpy):
    blender -b --factory-startup -P scripts/render-relief.py -- [saves/<welt>/data/journal] [--px 1400] [--fein PFAD]

Height source: the fine grid of Spielmonitor revision 17 (../Spielmonitor/history/gelaende/<world_id>.json, world_id from
data/monitor-sources.json, or --fein) when it covers the same map as karte.json, else the coarse grid in karte.json.
The fine grid stays local; only the image and the lines are published.

Reads karte.json (block `gelaende`) and writes next to it:
- relief.webp: aged parchment (Blender noise textures), land with a hand-coloured coastal band and a faint hillshade
  (Blender, light from the north-west), the sea a shade darker,
- relief.json: where the image sits, which height grid it came from (sha256 of `hoehen`), and in chart units the coast,
  the 5-m shoal line, water lines along the coast, mountain marks where the ground is high, wave marks in open water and
  the place of the compass rose, so the page draws them as vector ink over the image.

The grid holds heights at cell centres a few hundred metres apart. Between them the surface is reconstructed (Catmull-Rom,
then a light Gaussian): coast, shoals and mountain marks follow measured heights, their shapes between measurements are
smoothed. Parchment, wave marks, rose and rhumb lines are ornament; relief.json says both.
Without `gelaende` nothing is written. The page uses the relief only while its sha256 matches karte.json.
"""
import hashlib
import json
import math
import os
import re
import sys
import time

import bpy
import numpy as np
from mathutils import Vector

ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX_LAND, EX_SEA = 3.0, 1.5        # vertical exaggeration of the hillshade
SUN_AZIMUTH, SUN_ELEVATION = 315.0, 45.0   # light from the north-west, as on printed maps
SMOOTH_CELLS = 0.35               # Gaussian sigma in grid cells: rounds single-cell peaks into hills
SIMPLIFY_M = 6.0                  # Douglas-Peucker tolerance for the vector lines
WATER_LINES_M = (70, 150, 250, 380)   # distance of the engraved water lines from the coast
# Parchment and ink (sRGB). Paper light/dark by the stain noise, blotches, burnt edge; coastal band on land; sea tint.
PAPER = {'hell': '#f2dca5', 'dunkel': '#d9ad69', 'fleck': '#bd8648', 'rand': '#7a4520', 'kueste': '#b9793c', 'meer': '#c79c5e'}
SHADE_LAND = 0.3                  # the hillshade only hints at the ground, the mountain marks carry it


def options():
    folder, px, fine = os.path.join(ROOT, 'saves', 'archipel-des-alizes', 'data', 'journal'), 1400, None
    rest = list(ARGS)
    while rest:
        a = rest.pop(0)
        if a == '--px': px = int(rest.pop(0))
        elif a == '--fein': fine = os.path.abspath(rest.pop(0))
        else: folder = os.path.abspath(a)
    return folder, px, fine


def grid_sha(heights):
    return hashlib.sha256(json.dumps(heights, separators=(',', ':')).encode()).hexdigest()


def fine_sha(F):
    # The fine grid counts with its frame and cell, so a grid rejected for another frame is not mistaken for a known one.
    return grid_sha([F.get(k) for k in ('min_x', 'min_y', 'max_x', 'max_y', 'cell_m', 'height_reference', 'heights')])


def fine_grid(folder, G, path=None):
    """(grid, rejected): the fine grid of this world in the shape of karte.json's `gelaende`, or why it was not used."""
    if path is None:
        save = os.path.basename(os.path.dirname(os.path.dirname(folder)))
        try:
            with open(os.path.join(ROOT, 'data', 'monitor-sources.json'), encoding='utf-8') as f:
                world = json.load(f)['saves'][save]['world']['world_id']
        except (OSError, ValueError, KeyError, TypeError):
            return None, None
        path = os.path.join(os.path.dirname(ROOT), 'Spielmonitor', 'history', 'gelaende', re.sub(r'[^A-Za-z0-9_.-]', '_', world) + '.json')
    if not os.path.exists(path):
        return None, None
    with open(path, encoding='utf-8') as f:
        F = json.load(f)
    H, sha = F.get('heights'), fine_sha(F)
    num = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
    problems = [text for text, bad in (
        ('unvollständig', not F.get('complete') or F.get('row_order') != 'min_y_first' or not isinstance(H, list)
         or len(H) != F.get('rows_total') or any(not isinstance(r, list) or len(r) != F.get('cols') for r in H)),
        ('andere Kartengrenze', not all(num(F.get(k)) and abs(F[k] - G[k]) < 1 for k in ('min_x', 'min_y', 'max_x', 'max_y'))),
        ('anderer Höhenbezug', (F.get('height_reference') == 'water_level') != (G.get('bezug') == 'wasserspiegel')),
    ) if bad]
    if problems:
        return None, {'sha256': sha, 'grund': ', '.join(problems)}
    d = F.get('game_date')
    stand = f"{d['year']:04}-{d['month']:02}-{d['day']:02}" if isinstance(d, dict) and d.get('year') else None
    return {'hoehen': H, 'zelle_m': F['cell_m'], 'min_x': F['min_x'], 'min_y': F['min_y'], 'stand': stand,
            'aufgenommen': F.get('recorded_at'), 'sha256': sha}, None


def blur(A, s):
    """Separable Gaussian with sigma s in grid steps, edges repeated."""
    r = max(1, int(3 * s))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / s) ** 2); k /= k.sum()
    for axis in (0, 1):
        P = np.pad(A, [(r, r) if a == axis else (0, 0) for a in (0, 1)], mode='edge')
        n = A.shape[axis]
        A = sum(w * (P[i:i + n] if axis == 0 else P[:, i:i + n]) for i, w in enumerate(k))
    return A


def catmull(p0, p1, p2, p3, t):
    return 0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (3 * p1 - p0 - 3 * p2 + p3) * t ** 3)


def surface(G, xs, ys):
    """Heights on the grid xs × ys (world metres): Catmull-Rom through the cell centres, then a Gaussian of SMOOTH_CELLS."""
    H = np.array(G['hoehen'], dtype=np.float64)
    rows, cols, cell = H.shape[0], H.shape[1], G['zelle_m']
    X, Y = np.meshgrid(xs, ys)
    u, v = (X - G['min_x']) / cell - 0.5, (Y - G['min_y']) / cell - 0.5
    iu, iv = np.floor(u).astype(int), np.floor(v).astype(int)
    tu, tv = u - iu, v - iv
    g = lambda j, i: H[np.clip(j, 0, rows - 1), np.clip(i, 0, cols - 1)]
    Z = catmull(*[catmull(g(iv + k, iu - 1), g(iv + k, iu), g(iv + k, iu + 1), g(iv + k, iu + 2), tu) for k in (-1, 0, 1, 2)], tv)
    return blur(Z, SMOOTH_CELLS * cell / (xs[1] - xs[0]))


def shift(A, oj, oi):
    """A moved so that result[j, i] = A[j+oj, i+oi]; NaN where that lies outside."""
    ny, nx = A.shape
    R = np.full_like(A, np.nan)
    if abs(oj) >= ny or abs(oi) >= nx: return R
    R[max(0, -oj):ny - max(0, oj), max(0, -oi):nx - max(0, oi)] = A[max(0, oj):ny + min(0, oj), max(0, oi):nx + min(0, oi)]
    return R


def coast_distance(Z, dx, dy):
    """Signed distance to the coast in metres (sea positive): jump flooding from the coast crossings between grid points."""
    ny, nx = Z.shape
    best = np.full((ny, nx), np.inf); sx = np.full((ny, nx), np.nan); sy = np.full((ny, nx), np.nan)
    J, I = np.mgrid[0:ny, 0:nx].astype(np.float64)
    land = Z >= 0
    for axis in (0, 1):
        a, b = (Z[:-1], Z[1:]) if axis == 0 else (Z[:, :-1], Z[:, 1:])
        m = (a >= 0) != (b >= 0)
        jj, ii = np.nonzero(m)
        t = a[jj, ii] / (a[jj, ii] - b[jj, ii])
        cy, cx = (jj + t, ii.astype(float)) if axis == 0 else (jj.astype(float), ii + t)
        for tj, ti in ((jj, ii), (jj + (axis == 0), ii + (axis == 1))):
            d = ((cx - ti) * dx) ** 2 + ((cy - tj) * dy) ** 2
            better = d < best[tj, ti]
            best[tj[better], ti[better]] = d[better]; sx[tj[better], ti[better]] = cx[better]; sy[tj[better], ti[better]] = cy[better]
    step = 1 << int(math.log2(max(ny, nx)))
    while step >= 1:
        for oj in (-step, 0, step):
            for oi in (-step, 0, step):
                if not oj and not oi: continue
                csx, csy = shift(sx, oj, oi), shift(sy, oj, oi)
                d = ((csx - I) * dx) ** 2 + ((csy - J) * dy) ** 2
                better = d < best
                best = np.where(better, d, best); sx = np.where(better, csx, sx); sy = np.where(better, csy, sy)
        step //= 2
    dist = np.sqrt(best)
    return np.where(land, -dist, dist)


# --- vector lines: marching squares with whole edges as keys, so segments join into polylines without rounding ----
CASES = {1: [('l', 'b')], 2: [('b', 'r')], 3: [('l', 'r')], 4: [('r', 't')], 6: [('b', 't')], 7: [('l', 't')], 8: [('t', 'l')],
         9: [('b', 't')], 11: [('r', 't')], 12: [('l', 'r')], 13: [('b', 'r')], 14: [('l', 'b')]}


def contour(F, xs, ys, T, tol=SIMPLIFY_M):
    """Polylines of F == T. F is padded by the caller, so lines along the frame close outside it."""
    ny, nx = F.shape
    inside = F >= T
    a, b, c, d = inside[:-1, :-1], inside[:-1, 1:], inside[1:, 1:], inside[1:, :-1]
    case = a * 1 + b * 2 + c * 4 + d * 8
    centre = (F[:-1, :-1] + F[:-1, 1:] + F[1:, 1:] + F[1:, :-1]) / 4 >= T
    NH = ny * (nx - 1)
    edge = {'b': lambda j, i: j * (nx - 1) + i, 't': lambda j, i: (j + 1) * (nx - 1) + i,
            'l': lambda j, i: NH + j * nx + i, 'r': lambda j, i: NH + j * nx + i + 1}
    segs = []
    for cs in range(1, 15):
        js, iz = np.nonzero(case == cs)
        if not len(js): continue
        if cs in (5, 10):
            # Saddles: the cell centre decides whether the two inside corners connect.
            for j, i, cen in zip(js, iz, centre[js, iz]):
                pairs = ([('b', 'r'), ('t', 'l')] if cen else [('l', 'b'), ('r', 't')]) if cs == 5 else \
                        ([('l', 'b'), ('r', 't')] if cen else [('b', 'r'), ('t', 'l')])
                segs += [(edge[p](j, i), edge[q](j, i)) for p, q in pairs]
            continue
        for p, q in CASES[cs]:
            segs += list(zip(edge[p](js, iz).tolist(), edge[q](js, iz).tolist()))

    def point(e):
        if e < NH:
            j, i = divmod(e, nx - 1); f0, f1 = F[j, i], F[j, i + 1]
            return xs[i] + (T - f0) / (f1 - f0) * (xs[i + 1] - xs[i]), ys[j]
        j, i = divmod(e - NH, nx); f0, f1 = F[j, i], F[j + 1, i]
        return xs[i], ys[j] + (T - f0) / (f1 - f0) * (ys[j + 1] - ys[j])

    nbr = {}
    for p, q in segs:
        nbr.setdefault(p, []).append(q); nbr.setdefault(q, []).append(p)
    seen, lines = set(), []
    starts = [e for e, n in nbr.items() if len(n) == 1] + list(nbr)
    for s in starts:
        if s in seen: continue
        chain, prev, cur = [s], None, s
        seen.add(s)
        while True:
            nxt = [n for n in nbr[cur] if n != prev and n not in seen]
            if not nxt:
                closed = len(chain) > 2 and s in nbr[cur]
                break
            prev, cur = cur, nxt[0]
            seen.add(cur); chain.append(cur)
        pts = np.array([point(e) for e in chain])
        if closed: pts = np.vstack([pts, pts[:1]])
        lines.append((simplify(pts, tol), closed))
    return lines


def simplify(pts, tol):
    if len(pts) < 3: return pts
    keep = np.zeros(len(pts), bool); keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1: continue
        p, q = pts[i], pts[j]
        seg = pts[i + 1:j] - p
        dq = q - p
        n = math.hypot(*dq)
        dist = np.abs(seg[:, 0] * dq[1] - seg[:, 1] * dq[0]) / n if n else np.hypot(seg[:, 0], seg[:, 1])
        k = int(np.argmax(dist))
        if dist[k] > tol:
            keep[i + 1 + k] = True; stack += [(i, i + 1 + k), (i + 1 + k, j)]
    return pts[keep]


def svg_path(lines, up, min_points=3):
    out = []
    for pts, closed in lines:
        if len(pts) < min_points: continue
        xy = [(round(x), round(-y if up else y)) for x, y in pts]
        if closed: xy = xy[:-1]
        out.append('M' + 'L'.join(f'{x} {y}' for x, y in xy) + ('Z' if closed else ''))
    return ''.join(out)


def rgb(c): return np.array([int(c[i:i + 2], 16) / 255 for i in (1, 3, 5)])
def mix(a, b, t): return a + (b - a) * t[..., None]
def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def scene_setup(xs, ys, px_w, px_h):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    cam = bpy.data.objects.new('camera', bpy.data.cameras.new('camera'))
    cam.data.type, cam.data.clip_end = 'ORTHO', 100
    cam.data.ortho_scale = max(xs[-1] - xs[0], ys[-1] - ys[0]) / 1000
    cam.location = ((xs[0] + xs[-1]) / 2000, (ys[0] + ys[-1]) / 2000, 20)
    sc.collection.objects.link(cam)
    sc.camera = cam
    sc.render.engine = 'CYCLES'
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = px_w, px_h, 100
    sc.view_settings.view_transform = 'Standard'
    sc.render.image_settings.file_format, sc.render.image_settings.color_depth = 'OPEN_EXR', '32'
    sc.world = bpy.data.worlds.new('sky')
    sc.world.use_nodes = True
    return sc


def material(name, build):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        if n.bl_idname != 'ShaderNodeOutputMaterial': nt.nodes.remove(n)
    nt.links.new(build(nt), next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeOutputMaterial').inputs['Surface'])
    return mat


def render(sc, path, px_w, px_h, channels):
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(path)
    px = np.empty(px_w * px_h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    bpy.data.images.remove(img)
    return px.reshape(px_h, px_w, 4)[..., channels].astype(np.float64)   # rows from min_y upwards


def render_shade(sc, Z, xs, ys, px_w, px_h, path):
    """Hillshade of the exaggerated surface: white diffuse terrain, sun from the north-west plus a pale sky."""
    X, Y = np.meshgrid(xs / 1000, ys / 1000)
    verts = np.stack([X, Y, np.where(Z < 0, Z * EX_SEA, Z * EX_LAND) / 1000], -1).reshape(-1, 3)
    ny, nx = Z.shape
    idx = np.arange(nx * ny).reshape(ny, nx)
    quads = np.stack([idx[:-1, :-1], idx[:-1, 1:], idx[1:, 1:], idx[1:, :-1]], -1).reshape(-1, 4)
    me = bpy.data.meshes.new('relief')
    me.from_pydata(verts.tolist(), [], quads.tolist())
    me.shade_smooth()

    def diffuse(nt):
        n = nt.nodes.new('ShaderNodeBsdfDiffuse')
        n.inputs['Color'].default_value = (0.8, 0.8, 0.8, 1)
        return n.outputs[0]
    me.materials.append(material('relief', diffuse))
    terrain = bpy.data.objects.new('relief', me)
    sc.collection.objects.link(terrain)
    sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN'))
    sun.data.energy, sun.data.angle = 3.0, math.radians(10)
    az, el = math.radians(SUN_AZIMUTH), math.radians(SUN_ELEVATION)
    sun.rotation_mode = 'QUATERNION'
    sun.rotation_quaternion = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el))).to_track_quat('Z', 'Y')
    sc.collection.objects.link(sun)
    bg = next(n for n in sc.world.node_tree.nodes if n.bl_idname == 'ShaderNodeBackground')
    bg.inputs['Color'].default_value, bg.inputs['Strength'].default_value = (1, 1, 1, 1), 0.35
    sc.cycles.samples, sc.cycles.use_denoising, sc.cycles.max_bounces = 48, True, 2
    shade = render(sc, path, px_w, px_h, 0)
    terrain.hide_render = sun.hide_render = True
    return shade


def render_paper(sc, xs, ys, px_w, px_h, path):
    """Parchment structure from three Blender noise textures: large stains, blotches and fibres (R, G, B)."""
    x0, x1, y0, y1 = xs[0] / 1000, xs[-1] / 1000, ys[0] / 1000, ys[-1] / 1000
    me = bpy.data.meshes.new('paper')
    me.from_pydata([(x0, y0, 5), (x1, y0, 5), (x1, y1, 5), (x0, y1, 5)], [], [(0, 1, 2, 3)])

    def noise_layers(nt):
        coords = nt.nodes.new('ShaderNodeTexCoord')
        rgb_node = nt.nodes.new('ShaderNodeCombineColor')
        for channel, (scale, detail, rough) in enumerate(((0.35, 6, 0.62), (1.6, 5, 0.55), (28, 3, 0.5))):
            n = nt.nodes.new('ShaderNodeTexNoise')
            n.inputs['Scale'].default_value, n.inputs['Detail'].default_value, n.inputs['Roughness'].default_value = scale, detail, rough
            nt.links.new(coords.outputs['Object'], n.inputs['Vector'])
            nt.links.new(n.outputs['Fac'], rgb_node.inputs[channel])
        emit = nt.nodes.new('ShaderNodeEmission')
        nt.links.new(rgb_node.outputs[0], emit.inputs['Color'])
        return emit.outputs[0]
    me.materials.append(material('paper', noise_layers))
    sc.collection.objects.link(bpy.data.objects.new('paper', me))
    next(n for n in sc.world.node_tree.nodes if n.bl_idname == 'ShaderNodeBackground').inputs['Strength'].default_value = 0
    sc.cycles.samples, sc.cycles.use_denoising = 4, False
    return render(sc, path, px_w, px_h, slice(0, 3))


def scatter(x0, y0, x1, y1, spacing, seed):
    """Points on a jittered grid, the same for the same frame and seed."""
    rng = np.random.default_rng(seed)
    gx, gy = np.meshgrid(np.arange(x0 + spacing / 2, x1, spacing), np.arange(y0 + spacing / 2, y1, spacing))
    jx, jy = rng.uniform(-0.38, 0.38, gx.shape) * spacing, rng.uniform(-0.38, 0.38, gx.shape) * spacing
    return (gx + jx).ravel(), (gy + jy).ravel()


def main():
    t0 = time.time()
    folder, px_w, fine_path = options()
    K = json.load(open(os.path.join(folder, 'karte.json'), encoding='utf-8'))
    G = K.get('gelaende')
    if not G:
        print('render-relief: karte.json hat kein Gelaende, nichts zu tun'); return
    up = K.get('y_nach_oben', True)
    x0, y0, x1, y1 = G['min_x'], G['min_y'], G['max_x'], G['max_y']
    fine, rejected = fine_grid(folder, G, fine_path)
    if rejected: print(f"render-relief: feines Raster nicht verwendet ({rejected['grund']})")
    S = fine or G
    px_h = round(px_w * (y1 - y0) / (x1 - x0))
    # Surface on the mesh grid: two image pixels per vertex; one padded ring closes every line outside the frame.
    nx, ny = px_w // 2 + 1, px_h // 2 + 1
    xs, ys = np.linspace(x0, x1, nx), np.linspace(y0, y1, ny)
    Z = surface(S, xs, ys)
    dx, dy = xs[1] - xs[0], ys[1] - ys[0]
    xp, yp = np.concatenate([[x0 - dx], xs, [x1 + dx]]), np.concatenate([[y0 - dy], ys, [y1 + dy]])
    D = blur(coast_distance(Z, dx, dy), 1.2)
    lo, hi = float(Z.min()), float(Z.max())
    svg = lambda x, y: [round(float(x)), round(float(-y if up else y))]
    at = lambda A, x, y: A[np.clip(np.round((y - y0) / dy).astype(int), 0, ny - 1), np.clip(np.round((x - x0) / dx).astype(int), 0, nx - 1)]

    # Compass rose in the widest open water, away from the frame; wave marks in open water around it.
    margin = (np.abs(xs - (x0 + x1) / 2)[None, :] < 0.4 * (x1 - x0)) & (np.abs(ys - (y0 + y1) / 2)[:, None] < 0.42 * (y1 - y0))
    j, i = np.unravel_index(np.argmax(np.where(margin, D, -np.inf)), D.shape)
    rose_r = float(np.clip(0.75 * D[j, i], 900, 2600))
    rose = {'x': svg(xs[i], ys[j])[0], 'y': svg(xs[i], ys[j])[1], 'r': round(rose_r)}
    wx, wy = scatter(x0, y0, x1, y1, 1250, 11)
    keep = (at(D, wx, wy) > 480) & (np.hypot(wx - xs[i], wy - ys[j]) > rose_r * 1.3)
    waves = [svg(x, y) for x, y in zip(wx[keep], wy[keep])]

    # Mountain marks where the ground is high, not on the coast and not inside towns; north first so south overlaps.
    mx, my = scatter(x0, y0, x1, y1, 470, 7)
    mh = at(Z, mx, my)
    low = max(30.0, 0.16 * hi)
    keep = (mh >= low) & (-at(D, mx, my) > 180)
    for t in K.get('staedte', []):
        b = t.get('ausdehnung')
        if b: keep &= ~((mx > b[0] - 150) & (mx < b[2] + 150) & (my > b[1] - 150) & (my < b[3] + 150))
    order = np.argsort(-my[keep])
    peaks = max(110.0, 0.45 * hi)
    marks = [svg(x, y) + [round(min(820.0, 300 + 1.9 * h)), int(h >= peaks)] for x, y, h in zip(mx[keep][order], my[keep][order], mh[keep][order])]

    Zp = np.pad(Z, 1, constant_values=-1e4)
    Dp = np.pad(D, 1, constant_values=-1e4)
    paths = {'kueste': svg_path(contour(Zp, xp, yp, 0.0), up),
             'flach': svg_path(contour(Zp, xp, yp, -5.0), up, 4) if lo < -5 else '',
             'wasserlinien': [{'m': m, 'd': svg_path(contour(Dp, xp, yp, float(m), 10.0), up, 4)} for m in WATER_LINES_M]}
    print(f'surface {nx}x{ny}, lines and marks in {time.time() - t0:.1f}s')

    sc = scene_setup(xs, ys, px_w, px_h)
    tmp = bpy.app.tempdir or folder
    shade = render_shade(sc, Z, xs, ys, px_w, px_h, os.path.join(tmp, 'relief-shade.exr'))
    paper = render_paper(sc, xs, ys, px_w, px_h, os.path.join(tmp, 'relief-paper.exr'))
    print(f'renders in {time.time() - t0:.1f}s')

    # Heights at pixel centres (bilinear on the mesh grid); level ground keeps the paper as it is.
    cx = (np.arange(px_w) + 0.5) / px_w * (nx - 1)
    cy = (np.arange(px_h) + 0.5) / px_h * (ny - 1)
    i0, j0 = np.minimum(cx.astype(int), nx - 2), np.minimum(cy.astype(int), ny - 2)
    fx, fy = (cx - i0)[None, :], (cy - j0)[:, None]
    h = (Z[j0][:, i0] * (1 - fx) * (1 - fy) + Z[j0][:, i0 + 1] * fx * (1 - fy)
         + Z[j0 + 1][:, i0] * (1 - fx) * fy + Z[j0 + 1][:, i0 + 1] * fx * fy)
    gy, gx = np.gradient(np.where(h < 0, h * EX_SEA, h * EX_LAND), (y1 - y0) / px_h, (x1 - x0) / px_w)
    level = np.hypot(gx, gy) < 0.004
    flat = float(np.median(shade[level])) if level.sum() > 1000 else float(np.percentile(shade, 70))
    rel = np.clip(shade / flat, 0, 1.5)

    C = {k: rgb(v) for k, v in PAPER.items()}
    stain, blot, fibre = paper[..., 0], paper[..., 1], paper[..., 2]
    base = mix(np.broadcast_to(C['hell'], (px_h, px_w, 3)), C['dunkel'], smoothstep(0.38, 0.72, stain) * 0.85)
    base = mix(base, C['fleck'], smoothstep(0.6, 0.78, blot) * 0.4)
    base = base * (0.95 + 0.09 * fibre)[..., None]
    edge = np.minimum.outer(np.minimum(np.arange(px_h), np.arange(px_h)[::-1]), np.minimum(np.arange(px_w), np.arange(px_w)[::-1]))
    base = mix(base, C['rand'], 0.55 * np.exp(-edge / (0.05 * px_w)) * (0.6 + 0.6 * stain))
    land = h >= 0
    band = land * np.clip((1 - blur(land.astype(np.float64), 0.0035 * px_w)) * 2.4, 0, 1)
    land_col = mix(base * (1.05 + SHADE_LAND * (rel - 1))[..., None], C['kueste'], 0.6 * band)
    sea_col = mix(base, C['meer'], 0.22 + 0.1 * smoothstep(-5, -60, h)) * 0.97
    col = np.clip(np.where(land[..., None], land_col, sea_col), 0, 1)
    if not up: col = col[::-1]
    img = bpy.data.images.new('relief', px_w, px_h, alpha=False)
    img.pixels.foreach_set(np.concatenate([col, np.ones((px_h, px_w, 1))], -1).astype(np.float32).ravel())
    out_img = os.path.join(folder, 'relief.webp')
    img.filepath_raw, img.file_format = out_img, 'WEBP'
    img.save(quality=86)

    digest = grid_sha(G['hoehen'])
    smooth = round(SMOOTH_CELLS * S['zelle_m'])
    source = f'Feinscan im Abstand von {S["zelle_m"]} m' if fine else f'Abstand {S["zelle_m"]} m'
    meta = {'schema_version': 1,
            'hinweis': (f'Hintergrund im Stil einer alten Seekarte, mit Blender gerechnet. Küste, Untiefen (bis 5 m) und '
                        f'Bergzeichen folgen dem gemessenen Höhenraster ({source}, dazwischen geglättet), '
                        'die Bergzeichen stehen, wo das Land hoch ist, ihre Größe nach der Höhe. Pergament, Wellenzeichen, '
                        'Windrose und Kompasslinien sind Zierrat.'),
            'gelaende_stand': G['stand'], 'gelaende_sha256': digest,
            'bild': 'relief.webp', 'bild_px': [px_w, px_h], 'bild_version': hashlib.sha256(open(out_img, 'rb').read()).hexdigest()[:12],
            'rahmen': {'min_x': x0, 'min_y': y0, 'max_x': x1, 'max_y': y1}, 'y_nach_oben': up,
            'quelle': 'fein' if fine else 'grob', 'zelle_m': S['zelle_m'], 'glaettung_m': smooth, 'hoehen': {'min': round(lo), 'max': round(hi)},
            'licht': {'azimut': SUN_AZIMUTH, 'hoehe': SUN_ELEVATION}, 'papier': PAPER,
            **({'fein': {k: fine[k] for k in ('stand', 'aufgenommen', 'zelle_m', 'sha256')}} if fine else {}),
            **({'fein_abgelehnt': rejected} if rejected else {}),
            'pfade': paths, 'berge': marks, 'berge_ab_m': round(low), 'gipfel_ab_m': round(peaks), 'wellen': waves, 'rose': rose}
    with open(os.path.join(folder, 'relief.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(meta, f, ensure_ascii=False, separators=(',', ':'))
        f.write('\n')
    print(f'render-relief: {out_img} {px_w}x{px_h}, Raster {"fein" if fine else "grob"} {S["zelle_m"]} m, relief.json {os.path.getsize(os.path.join(folder, "relief.json")) // 1024} KB, '
          f'{len(marks)} Bergzeichen, {len(waves)} Wellen, {time.time() - t0:.1f}s')


main()
