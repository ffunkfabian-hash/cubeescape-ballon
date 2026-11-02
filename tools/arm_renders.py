"""Drei Renders der Ego-Arme (0.40 „Brace“): Spielbild, Arme allein im Studio, Aufbauansicht mit Segment-IDs.

  ce lock gpu -- blender -b --factory-startup -P <abs>/tools/arm_renders.py -- [--gpu] [--samples N] [--only a,b,c]
  python3 tools/arm_renders.py --annotate        → nur Beschriftung, 960er und docs/bilder neu (ohne Blender)

  a) Ego-Ansicht: BASIC-01 (Automatik) in der Hüfthaltung mit beiden Armen, Kamera wie im Spiel (ego.CAMERA, 75°); Hände wie im
     Standbild der Haltung (ego_build.still_action).
  b) Dieselbe Haltung ohne Waffe, 3/4 von vorn oben: Griffhand rechts (trigger), Stützhand links (underhand).
  c) Rechter Arm in der Ruhelage des Arm-Pakets (tools/export_arms.build), Segmente entlang der Kette auseinandergezogen; Ellbogen- und
     Kardanteile (gehören zu fore bzw. hand) sitzen in ihrer Lücke. Beschriftung mit den IDs aus robot_arm.SEGMENTS.
Ausgabe: <CACHE>/0.40/belege/renders/{a_spielbild,b_studio,c_aufbau}.png (1920×1080) und *_960.jpg; verkleinerte JPEGs (≤ 400 KB)
nach docs/bilder/ego-arme-{spielbild,studio,aufbau}.jpg.
"""
import json
import math
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic.arms import robot_arm as RA  # noqa: E402

OUT = os.path.expanduser('~/Library/Caches/CubeEscapeBallon/0.40/belege/renders')
DOCS = os.path.join(ROOT, 'docs', 'bilder')
NAMES = {'a': 'spielbild', 'b': 'studio', 'c': 'aufbau'}
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
FONT_B = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
DOC_MAX = 400 * 1024
MM = 0.001
# Aufbauansicht: Lücken entlang der Kette (m) und seitliche Spreizung der Finger (Anteil der Fingerteilung)
GAP = dict(fore=0.14, hand=0.085, finger0=0.032, link=0.016, thumb0=0.036, spread=0.6, elbow=-0.07, wrist=-0.042)
ELBOW = ('elbow', 'elbow_disc', 'elbow_ring', 'elbow_hub')
WRIST = ('wrist_block', 'wrist_pin')
FINGER_DE = ['Zeigefinger', 'Mittelfinger', 'Ringfinger', 'kleiner Finger']
B_DIR = (-0.55, -0.80, 0.75)         # b) vom Motiv zur Kamera: rechts (−X), vorn (−Y), oben
C_DIR = (-0.62, 0.10, 0.78)          # c) von der rechten Seite und oben auf den gestreckten Arm (Kette läuft nach −Y = im Bild nach rechts)
C_ROLL = -55                         # c) Arm zur Ansicht um seine Längsachse gerollt: Daumenseite nach oben, Handrücken zur Kamera
LEAD = 120                           # c) Länge der Hinweislinien über/unter dem Arm (px)
C_SHIFT = 0.085                      # c) Linsenversatz: Arm links, rechts Platz für die Finger-Etiketten


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    o = dict(gpu='--gpu' in a, samples=192, only='abc')
    if '--samples' in a:
        o['samples'] = int(a[a.index('--samples') + 1])
    if '--only' in a:
        o['only'] = a[a.index('--only') + 1].replace(',', '')
    return o


# ------------------------------------------------------------------ Blender
def look(cam, pos, at, lens):
    from mathutils import Vector
    cam.data.lens = lens
    cam.location = pos
    cam.rotation_euler = (Vector(at) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()


def corners(obs):
    """Weltpunkte der Hüllquader aller sichtbaren Netze."""
    from mathutils import Vector
    return [ob.matrix_world @ Vector(c) for ob in obs if ob.type == 'MESH' and not ob.hide_render for c in ob.bound_box]


def fit(cam, pts, d, lens, fill=0.84):
    """Kamera aus Richtung d (vom Motiv zur Kamera) so weit zurück, dass pts fill des Bildes füllen (zwei Näherungsschritte)."""
    import bpy
    from mathutils import Vector
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    at, d, dist = (lo + hi) / 2, Vector(d).normalized(), (hi - lo).length * 2.0
    for _ in range(3):
        look(cam, at + d * dist, at, lens)
        bpy.context.view_layer.update()
        V = [world_to_camera_view(sc, cam, p) for p in pts]
        ext = max(max(abs(v.x - 0.5) for v in V), max(abs(v.y - 0.5) for v in V)) / 0.5     # mit Linsenversatz zählt die ferne Seite
        dist *= ext / fill
    look(cam, at + d * dist, at, lens)
    bpy.context.view_layer.update()
    return at, dist


def render(path, res=(1920, 1080)):
    import bpy
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print(f'[arm_renders] {path}', flush=True)


def ego_scene(o):
    """a) und b): Ego-Szene der Automatik in der Hüfthaltung (Hände wie im Standbild)."""
    import bpy
    from mathutils import Vector
    import importlib
    import tools.ego_build as EB
    W = importlib.import_module('basic.pilot.w01_auto_rifle_v21')
    sc = EB.Scene(W, dict(gpu=o['gpu'], samples=o['samples'], fx=False))
    bpy.context.scene.cycles.samples = o['samples']
    rep = {}
    EB.evaluate(sc, EB.still_action(sc.P, 'hip'), 0, rep, {})
    elbow = {}
    for s in ('R', 'L'):           # Ellbogen: Drehachse zwischen Ober- und Unterarmrahmen gegen die Segment-X-Achse (Bericht)
        U, F = sc.arms[s][0]['upper'].matrix_world.to_3x3(), sc.arms[s][0]['fore'].matrix_world.to_3x3()
        q = (U.inverted() @ F).to_quaternion()
        ax = Vector(q.axis)
        elbow[s] = dict(bend_deg=round(q.angle * 57.29578, 1), axis_off_x_deg=round(ax.angle(Vector((1, 0, 0)) if ax.x >= 0
                                                                                              else Vector((-1, 0, 0))) * 57.29578, 1))
    meta = dict(weapon=EB.EG.weapon_id(W), pose='hip', wrist_bend_max_deg=round(rep.get('wrist_max_deg', 0), 1),
                overreach=rep.get('overreach', 0), elbow=elbow, samples=o['samples'], gpu=o['gpu'])
    if 'a' in o['only']:
        bpy.context.scene.camera = sc.cam
        render(os.path.join(OUT, 'a_spielbild.png'))
    if 'b' in o['only']:
        arm_obs = {ob for s in ('R', 'L') for d in sc.arms[s][:2] for ob in d.values()}
        for ob in bpy.data.objects:
            if ob.type == 'MESH' and ob not in arm_obs:
                ob.hide_render = True
        cam = bpy.data.objects.new('Studio', bpy.data.cameras.new('Studio'))
        bpy.context.scene.collection.objects.link(cam)
        at, dist = fit(cam, corners(arm_obs), B_DIR, 60, fill=0.86)
        bpy.context.scene.camera = cam
        render(os.path.join(OUT, 'b_studio.png'))
        meta['b_camera'] = dict(at=[round(v, 4) for v in at], dist_m=round(dist, 3), dir=B_DIR, lens=60)
    return meta


def explode_scene(o):
    """c): rechter Arm in der Paket-Ruhelage, entlang der Kette auseinandergezogen; Bildpunkte der Beschriftung."""
    import bpy
    from mathutils import Matrix, Vector
    from bpy_extras.object_utils import world_to_camera_view
    from basic import kit
    import tools.blender_build as BB
    import tools.export_arms as XA
    arms = XA.build(materials=False)
    BB.setup_render(1920, o['samples'], gpu=o['gpu'], aaa=True, bloom=False, bg='mid')
    bpy.context.scene.cycles.samples = o['samples']
    root, segs, pieces, anchors = arms['R']
    kit.set_mode(pieces, 'aaa')
    for ob in arms['L'][2].values():
        ob.hide_render = True
    C = XA.chain('R')
    for seg, (par, at, q) in C.items():
        if seg == 'upper':
            continue
        if seg in ('fore', 'hand'):
            extra = Vector((0, 0, GAP[seg]))
        elif seg.startswith('f') and seg.endswith('_0'):
            extra = Vector((RA.FINGER_X[int(seg[1])] * GAP['spread'] * MM, 0, GAP['finger0']))
        elif seg == 't_0':
            extra = Vector(RA.THUMB_DIR).normalized() * GAP['thumb0']
        else:
            extra = Vector((0, 0, GAP['link']))
        segs[seg].matrix_basis = Matrix.Translation(Vector(at) + extra) @ segs[seg].matrix_basis.to_3x3().to_4x4()
    for pid in ELBOW:
        pieces[f'R_{pid}'].matrix_basis = Matrix.Translation((0, 0, GAP['elbow']))
    for pid in WRIST:
        pieces[f'R_{pid}'].matrix_basis = Matrix.Translation((0, 0, GAP['wrist']))
    # zur Ansicht gerollt und so verschoben, dass der Arm um den Zielpunkt der Studiolichter liegt (blender_build.setup_render)
    root.matrix_world = Matrix.Translation((0, 0.45, 0)) @ Matrix.Rotation(math.radians(C_ROLL), 4, 'Y') @ \
        Matrix.Rotation(math.radians(90), 4, 'X')
    bpy.context.view_layer.update()
    r0 = root.matrix_world.translation.copy()
    cam = bpy.data.objects.new('Aufbau', bpy.data.cameras.new('Aufbau'))
    bpy.context.scene.collection.objects.link(cam)
    cam.data.shift_x, cam.data.shift_y = C_SHIFT, -0.025
    fit(cam, corners(pieces.values()), C_DIR, 50, fill=0.95)
    bpy.context.scene.camera = cam
    sc = bpy.context.scene

    def px(p):
        v = world_to_camera_view(sc, cam, p)
        return [round(v.x * 1920, 1), round((1 - v.y) * 1080, 1)]

    def mid_of(seg, k=0.5, length=None):
        L = length if length is not None else XA.length_m(seg)
        return px(segs[seg].matrix_world @ Vector((0, 0, L * k)))
    pts = [dict(de='Schulter', ids='R_arm (Wurzel)', at=px(r0), side='above'),
           dict(de='Oberarm', ids='upper', at=mid_of('upper', 0.45), side='below'),
           dict(de='Ellbogen', ids='elbow* in fore', at=px(pieces['R_elbow'].matrix_world.translation), side='above'),
           dict(de='Unterarm', ids='fore', at=mid_of('fore', 0.5), side='below'),
           dict(de='Handgelenk', ids='wrist_* in hand', at=px(pieces['R_wrist_block'].matrix_world.translation), side='above'),
           dict(de='Hand', ids='hand', at=mid_of('hand', 0.55), side='below')]
    for i in range(4):
        pts.append(dict(de=FINGER_DE[i], ids=f'f{i}_0 · f{i}_1 · f{i}_2', at=mid_of(f'f{i}_1', 0.5), side='right'))
    pts.append(dict(de='Daumen', ids='t_0 · t_1 · t_2', at=mid_of('t_1', 0.5), side='right'))
    if 'c' in o['only']:
        render(os.path.join(OUT, 'c_aufbau_roh.png'))
    return dict(labels=pts, gap=GAP, segments=list(RA.SEGMENTS))


def blender_main():
    import bpy  # noqa: F401
    o = args()
    os.makedirs(OUT, exist_ok=True)
    meta = {}
    if 'a' in o['only'] or 'b' in o['only']:
        meta['ego'] = ego_scene(o)
    if 'c' in o['only']:
        meta['explode'] = explode_scene(o)
    mp = os.path.join(OUT, 'renders.json')
    old = json.load(open(mp, encoding='utf-8')) if os.path.exists(mp) else {}
    old.update(meta)
    json.dump(old, open(mp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    annotate()


# ------------------------------------------------------------------ Beschriftung und Ablage (ImageMagick, ohne Blender)
def _label(de, ids):
    """Etikett als Bilddatei-Argumente: (Breite, Höhe, magick-Teilbefehl)."""
    sub = ['(', '-background', '#F4F3F0', '-fill', '#14171A', '-font', FONT_B, '-pointsize', '27', f'label:{de}',
           '-fill', '#8A3F0E', '-font', FONT, '-pointsize', '24', f'label:{ids}', '-gravity', 'West', '-append',
           '-bordercolor', '#F4F3F0', '-border', '12x8', ')']
    wh = subprocess.run(['magick', *sub[1:-1], '-format', '%w %h', 'info:'], capture_output=True, text=True, check=True).stdout
    w, h = (int(v) for v in wh.split())
    return w, h, sub


def annotate():
    meta = json.load(open(os.path.join(OUT, 'renders.json'), encoding='utf-8'))
    raw = os.path.join(OUT, 'c_aufbau_roh.png')
    if 'explode' in meta and os.path.exists(raw):
        cmd = ['magick', raw]
        draws, comps = [], []
        right = sorted([p for p in meta['explode']['labels'] if p['side'] == 'right'], key=lambda p: p['at'][1])
        boxes = [_label(p['de'], p['ids']) for p in right]
        col_x = max(p['at'][0] for p in right) + 90
        total = sum(h for _w, h, _s in boxes) + 14 * (len(boxes) - 1)       # Spalte rechts, mittig um die Finger gestapelt
        y = max(60, min(1080 - total - 20, sum(p['at'][1] for p in right) / len(right) - total / 2))
        for p, (w, h, sub) in zip(right, boxes):
            x = min(col_x, 1920 - w - 20)
            ax, ay = p['at']
            draws += [f'line {ax},{ay} {x},{y + h / 2}', f'circle {ax},{ay} {ax + 5},{ay}']
            comps += [*sub, '-gravity', 'NorthWest', '-geometry', f'+{int(x)}+{int(y)}', '-composite']
            y += h + 14
        for p in meta['explode']['labels']:
            if p['side'] == 'right':
                continue
            w, h, sub = _label(p['de'], p['ids'])
            ax, ay = p['at']
            y = ay - LEAD - h if p['side'] == 'above' else ay + LEAD
            x = max(20, min(1920 - w - 20, ax - w / 2))
            ly = y + h if p['side'] == 'above' else y
            draws += [f'line {ax},{ay} {ax},{ly}', f'circle {ax},{ay} {ax + 5},{ay}']
            comps += [*sub, '-gravity', 'NorthWest', '-geometry', f'+{int(x)}+{int(y)}', '-composite']
        title = (f'Ego-Arm rechts · Rig v{RA.RIG_VERSION} · ballon-arms/1 · Segmente entlang der Kette auseinandergezogen '
                 f'(IDs aus robot_arm.SEGMENTS)')
        cmd += ['-stroke', '#F4F3F0', '-strokewidth', '3', '-fill', '#F4F3F0'] + sum((['-draw', d] for d in draws), [])
        cmd += ['-stroke', 'none'] + comps
        cmd += ['-fill', '#F4F3F0', '-font', FONT, '-pointsize', '26', '-gravity', 'NorthWest', '-annotate', '+28+22', title,
                os.path.join(OUT, 'c_aufbau.png')]
        subprocess.run(cmd, check=True)
    os.makedirs(DOCS, exist_ok=True)
    for k, n in NAMES.items():
        src = os.path.join(OUT, f'{k}_{n}.png')
        if not os.path.exists(src):
            continue
        subprocess.run(['magick', src, '-resize', '960x', '-quality', '90', os.path.join(OUT, f'{k}_{n}_960.jpg')], check=True)
        dst = os.path.join(DOCS, f'ego-arme-{n}.jpg')
        for width, q in ((1600, 84), (1280, 84), (1280, 76), (960, 82)):
            subprocess.run(['magick', src, '-resize', f'{width}x', '-strip', '-sampling-factor', '4:2:0', '-quality', str(q), dst],
                           check=True)
            if os.path.getsize(dst) <= DOC_MAX:
                break
        print(f'[arm_renders] {dst}: {os.path.getsize(dst) // 1024} KB', flush=True)


if __name__ == '__main__':
    if '--annotate' in sys.argv and '--' not in sys.argv:
        annotate()
    else:
        blender_main()
