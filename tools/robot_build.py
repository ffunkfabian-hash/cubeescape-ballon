"""BASIC-Roboter (basic/robot): Aufbau, Prüfung, Standbilder, Explosionsansicht, Einzelblätter je Baugruppe.

  blender -b --factory-startup -P tools/robot_build.py -- [--check] [--spec] [--dry] [--only hero,nah,seite,explode,parts]
                                                          [--gpu] [--samples N] [--res 1000] [--preview] [--tag T]

--check   nur aufbauen (Grundhaltung idle, ohne Waffe) und prüfen: Kind- und Elternbaugruppe berühren sich am Anschluss jedes Ankers
          (Umkreis ANCHOR_R_MM), Messwerte gleich data/robot.spec.json; Ausgabe „robot_check: …“, Exit 1 bei Fehler. Keine Bilder.
--dry     Haltung ready aufbauen (IK an die Waffe), nichts rendern oder schreiben.
--spec    zusätzlich data/robot.spec.json schreiben (gemessene Maße, Teile, Dreiecke je Baugruppe, Ankerabstände).
--preview Workbench statt Cycles (Formskizze, schnell, kein schwerer Lauf).
Renderings (Cycles) nur mit ~/Claude/cubeescape-nexogen/ce lock gpu -- … und --gpu.
Alle Bilder auf dem grauen Standardhintergrund der Waffen (--bg mid), ohne Bloom; kein Hangar (Nutzer 24.10.2026).
Ausgabe: <OUT>/robot/{hero,nah,seite}.png (Haltung ready), explode.png, asm_<baugruppe>.png (Haltung idle), robot.blend;
Kontaktbogen <OUT>/robot/contact_assemblies.png.
"""
import importlib
import json
import math
import os
import subprocess
import sys

import bmesh
import bpy
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic import kit  # noqa: E402
from basic import robot as RB  # noqa: E402
from basic.robot import arms as RARM  # noqa: E402
import tools.blender_build as BB  # noqa: E402
import tools.ego_build as EB  # noqa: E402
from tools.paths import OUT  # noqa: E402

MM = 0.001
GAP_TOL_MM = 1.0
# Umkreis des Anschlusses um die Ankerlage (entworfen): größer als der halbe Gelenkdurchmesser (Hals-/Taillenring ≤ 66 mm, Hüftgelenk
# 46 mm, Oberarm-Halbbreite 60 mm), kleiner als der Abstand Hals–Schulterpanzer (~150 mm), damit ein Kontakt dort nicht zählt
ANCHOR_R_MM = 140.0
AMBIENT = 0.35           # Anteil des Umgebungslichts von --bg mid (Roboter: mehr Schatten, Zielbild)
SPEC = os.path.join(ROOT, 'data', 'robot.spec.json')
ALL_VIEWS = ('hero', 'nah', 'seite', 'explode', 'parts')


FLAGS = {'--gpu', '--check', '--spec', '--preview', '--dry'}
VALUED = {'--samples', '--res', '--only', '--tag'}


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    i = 0
    while i < len(a):           # unbekannte Schalter ablehnen, statt still alles zu rendern
        if a[i] in VALUED:
            i += 2
        elif a[i] in FLAGS:
            i += 1
        else:
            sys.exit(f'robot_build: unbekanntes Argument {a[i]} (erlaubt: {sorted(FLAGS | VALUED)})')
    o = dict(gpu='--gpu' in a, check='--check' in a, spec='--spec' in a, preview='--preview' in a, dry='--dry' in a,
             samples=96, res=1000, only=set(ALL_VIEWS), tag='')
    for k in ('samples', 'res'):
        if f'--{k}' in a:
            o[k] = int(a[a.index(f'--{k}') + 1])
    if '--only' in a:
        o['only'] = set(a[a.index('--only') + 1].split(','))
        if o['only'] - set(ALL_VIEWS):
            sys.exit(f"robot_build: unbekannte Ansicht {sorted(o['only'] - set(ALL_VIEWS))}")
    if '--tag' in a:
        o['tag'] = a[a.index('--tag') + 1]
    return o


# ------------------------------------------------------------------ Aufbau

def _mirror(kind, p, sx):
    p = dict(p)
    if 'c' in p:
        p['c'] = [sx * p['c'][0], p['c'][1], p['c'][2]]
    if kind == 'hull':
        p['pts'] = [(sx * x, y, z) for x, y, z in p['pts']]
    if kind == 'hulls':
        p['parts'] = [[(sx * x, y, z) for x, y, z in pts] for pts in p['parts']]
    if kind == 'plate':
        p['phi'] = sx * p.get('phi', 0.0)
        p['u'] = sx * p.get('u', 0.0)
    return p


def _hulls(name, p):
    """Mehrere konvexe Hüllen als ein Objekt (Form hulls, z. B. Kabel)."""
    bm = bmesh.new()
    for pts in p['parts']:
        b2 = bmesh.new()
        EB.hull_verts(b2, pts)
        tmp = bpy.data.meshes.new('tmp')
        b2.to_mesh(tmp)
        b2.free()
        bm.from_mesh(tmp)
        bpy.data.meshes.remove(tmp)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _piece(name, kind, p, role, asm, pid, side, parent):
    ob = _hulls(name, p) if kind == 'hulls' else EB.piece_mesh(name, kind, p)
    if kind in ('hull', 'hulls'):          # gerundete Querschnitte glatt, echte Kanten (Fasen, Pfeilschnitte) bleiben scharf
        for f in ob.data.polygons:
            f.use_smooth = True
        ob.data.set_sharp_from_angle(angle=math.radians(p.get('sharp', 40)))
    ob.data.materials.append(kit.material(role))
    if p.get('bevel'):
        kit.add_bevel(ob, p['bevel'])
    else:
        kit.add_bevel(ob, {'cyl': 0.8, 'hull': 2.0, 'hulls': 1.0, 'prism': 1.6, 'plate': 1.0, 'box': 1.0}.get(kind, 1.0))
    ob.parent = parent
    ob.matrix_parent_inverse = Matrix.Identity(4)
    ob['asm'], ob['part'], ob['side'] = asm, pid, side
    return ob


def _empty(name, asm, side):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.02
    bpy.context.scene.collection.objects.link(e)
    e['asm'], e['side'] = asm, side
    return e


def build_body():
    """Kopf, Oberkörper, Unterkörper, Beine in der Grundhaltung. Rückgabe: (Segment-Empties, Teile)."""
    segs, obs = {}, {}
    plist = [(asm, p) for asm, p in RB.parts() if asm != 'arms']
    for name, A, B, hint, side in RB.segments():
        A, B = Vector(A) * MM, Vector(B) * MM
        kind_of = name.split('_')[0]
        asm = RB.asm_of_segment(kind_of)
        e = _empty(f'SEG_{name}', asm, side)
        e.matrix_world = EB.mat(EB.frame_from(B - A, Vector(hint)), A)
        segs[name] = e
        sx = -1 if side == 'L' else 1
        for a, (pid, de, seg, kind, role, p) in plist:
            if seg == kind_of:
                ob = _piece(f'{name}_{pid}' if side != 'C' else pid, kind, _mirror(kind, p, sx), role, a, pid, side, e)
                obs[ob.name] = ob
    return segs, obs


def build_arms():
    """Arme je Seite aus basic/robot/arms.py (gekoppelt an den Ego-Arm). Rückgabe: ({Seite: Segment-Empties}, Teile)."""
    segs, obs = {}, {}
    for side in ('R', 'L'):
        sx = 1 if side == 'R' else -1
        S = {s: _empty(f'ARM_{side}_{s}', 'arms', side) for s in RARM.SEGMENTS}
        for pid, de, seg, kind, role, p in RARM.parts():
            ob = _piece(f'arm_{side}_{pid}', kind, _mirror(kind, p, sx), role, 'arms', pid, side, S[seg])
            obs[ob.name] = ob
        segs[side] = S
    return segs, obs


def two_bone(S, Wp, a, b, pole):
    d = Wp - S
    L = min(d.length, a + b - 1e-4)
    if d.length > a + b:
        print(f'Warnung: Griff {d.length:.3f} m außer Reichweite ({a + b:.3f} m)')
    x = (a * a - b * b + L * L) / (2 * L)
    h = math.sqrt(max(a * a - x * x, 0.0))
    u = d.normalized()
    pv = pole - u * pole.dot(u)
    return S + u * x + pv.normalized() * h


def pose_arms(asegs, pose, part_world=None):
    """Arme in Haltung pose setzen: ready (IK an die Waffengriffe) oder idle (hängend, Richtungen je Glied)."""
    P = RB.POSES[pose]
    a, b = RARM.UPPER_MM * MM, RARM.FORE_MM * MM
    for side, segs in asegs.items():
        sx = -1 if side == 'R' else 1                 # Weltseite (rechts −X)
        S = Vector(RB.SHOULDER[side]) * MM
        out = Vector((sx, 0, 0))
        if P['weapon']:
            h = P['hands'][side]
            H, fp = EB.grip_hand(h['grip'], part_world)
            EB.solve_arm(side, segs, H, RARM.FINGER_POSES[fp], {})
            Wp = H.translation
            E = two_bone(S, Wp, a, b, Vector(h['pole']))
        else:
            ud = Vector((sx * -P['upper'][0], P['upper'][1], P['upper'][2])).normalized()
            fd = Vector((sx * -P['fore'][0], P['fore'][1], P['fore'][2])).normalized()
            E = S + ud * a
            Wp = E + fd * b
            H = EB.mat(EB.frame_from(fd, out), Wp)      # Handrücken nach außen, Daumen nach vorn
            EB.solve_arm(side, segs, H, RARM.FINGER_POSES[P['fingers']], {})
        segs['upper'].matrix_world = EB.mat(EB.frame_from(E - S, out), S)
        segs['fore'].matrix_world = EB.mat(EB.frame_from(Wp - E, H.to_3x3().col[1]), E)
        bend = math.degrees((Wp - E).angle(H.to_3x3().col[2]))
        print(f'[robot] {pose} {side}: Ellbogen {E.x:+.3f} {E.y:+.3f} {E.z:+.3f}, Handgelenk {bend:.0f}°')


def build(pose, mode='aaa'):
    """Ganze Figur in Haltung pose; mit Waffe bei ready. Rückgabe: dict mit segs, obs (alle Roboterteile), weapon-Objekten."""
    segs, obs = build_body()
    asegs, aobs = build_arms()
    obs.update(aobs)
    wobs = {}
    P = RB.POSES[pose]
    WM = None
    if P['weapon']:
        W = importlib.import_module(f"basic.{P['weapon']}")
        root, wobs, _ = kit.build(W)
        WM = (Matrix.Translation(Vector(P['pos']) * MM) @ Matrix.Rotation(math.radians(P['rot_z']), 4, 'Z')
              @ Matrix.Rotation(math.radians(P['rot_x']), 4, 'X'))
        root.matrix_world = WM
        bpy.context.view_layer.update()
    pose_arms(asegs, pose, (lambda pid: WM))
    bpy.context.view_layer.update()
    if mode != 'color':
        kit.set_mode(obs, mode)
        if wobs:
            kit.set_mode(wobs, mode)
    return dict(segs=segs, asegs=asegs, obs=obs, wobs=wobs)


# ------------------------------------------------------------------ Prüfung

def _bvh(obs, center, radius):
    """BVH aus den Flächen der Objekte, die mindestens eine Ecke im Umkreis radius (m) um center haben."""
    dg = bpy.context.evaluated_depsgraph_get()
    verts, polys = [], []
    for ob in obs:
        e = ob.evaluated_get(dg)
        me = e.to_mesh()
        off = len(verts)
        W = [e.matrix_world @ v.co for v in me.vertices]
        verts += W
        polys += [[off + i for i in p.vertices] for p in me.polygons if any((W[i] - center).length <= radius for i in p.vertices)]
        e.to_mesh_clear()
    used = sorted({i for p in polys for i in p})
    return (BVHTree.FromPolygons(verts, polys) if polys else None), [verts[i] for i in used]


def anchor_gaps(obs):
    """Abstand (mm) zwischen Eltern- und Kindbaugruppe am Anschluss je Anker; 0 = Überschneidung. Geprüft wird nur Geometrie im
    Umkreis ANCHOR_R_MM um die Ankerlage – ein Kontakt an anderer Stelle verdeckt keinen offenen Anschluss. Seitenanker prüfen nur
    die Teile ihrer Seite; keine Geometrie im Umkreis = unendlich."""
    res = {}
    for k, A in RB.ANCHORS.items():
        c, r = Vector(A['pos']) * MM, ANCHOR_R_MM * MM
        par = [o for o in obs.values() if o['asm'] == A['parent']]
        chi = [o for o in obs.values() if o['asm'] == A['child'] and (not A.get('side') or o['side'] == A['side'])]
        tp, _ = _bvh(par, c, r)
        tc, vc = _bvh(chi, c, r)
        if tp is None or tc is None:
            res[k] = float('inf')
        elif tp.overlap(tc):
            res[k] = 0.0
        else:
            res[k] = min(tp.find_nearest(v)[3] for v in vc) / MM
    return res


def spec_drift(obs, gaps):
    """Abweichungen der gemessenen Werte von data/robot.spec.json (Geometrie geändert, Spec nicht neu geschrieben)."""
    if not os.path.exists(SPEC):
        return ['Spec fehlt']
    S = json.load(open(SPEC, encoding='utf-8'))
    out = []
    if S.get('measured') != measure(obs):
        out.append('Messwerte')
    if S.get('anchor_gap_mm') != {k: round(v, 2) for k, v in gaps.items()}:
        out.append('Ankerabstände')
    return out


def measure(obs):
    lo, hi = kit.world_bounds(list(obs.values()))
    per = {}
    for a in RB.ASSEMBLIES:
        sel = [o for o in obs.values() if o['asm'] == a['id']]
        alo, ahi = kit.world_bounds(sel)
        per[a['id']] = dict(objects=len(sel), parts=len(a['module'].parts()), triangles=sum(kit.eval_tris(o) for o in sel),
                            size_mm=[round((ahi[i] - alo[i]) / MM) for i in range(3)])
    return dict(height_mm=round((hi.z - lo.z) / MM), width_mm=round((hi.x - lo.x) / MM), depth_mm=round((hi.y - lo.y) / MM),
                assemblies=per)


def write_spec(obs, gaps):
    m = measure(obs)
    spec = dict(format='cubeescape-ballon/robot-spec', format_version=1, id=RB.META['id'], version=RB.META['version'],
                pose='idle', measured=m, anchor_gap_mm={k: round(v, 2) for k, v in gaps.items()},
                parts={a['id']: [p[0] for p in a['module'].parts()] for a in RB.ASSEMBLIES})
    json.dump(spec, open(SPEC, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    open(SPEC, 'a').write('\n')
    print('[robot] geschrieben', SPEC)


# ------------------------------------------------------------------ Bild

def floor():
    """Boden als Schattenfänger: Schatten auf dem grauen Hintergrund, keine Horizontkante."""
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
    fl = bpy.context.active_object
    fl.name = 'Boden'
    fl.is_shadow_catcher = True
    return fl


def lights():
    # wie im Zielbild: großflächiges warmweißes Hauptlicht, kühles Kantenlicht von hinten rechts, wenig Fülllicht
    for nm, loc, en, size, col in (('Key', (-3.6, -1.4, 3.2), 560, 1.6, '#FFDDB8'), ('Fill', (2.6, -2.8, 1.4), 45, 3.0, '#D2DEEC'),
                                   ('Rim', (1.8, 2.8, 2.6), 950, 1.8, '#A9D3FF')):
        o = bpy.data.objects.get(nm)
        if o is None:
            o = bpy.data.objects.new(nm, bpy.data.lights.new(nm, 'AREA'))
            bpy.context.scene.collection.objects.link(o)
        o.location = loc
        o.data.energy = en
        o.data.size = size
        o.data.color = kit.hex_rgba(col)[:3]
        o.rotation_euler = (Vector((0, 0, 1.0)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()


def camera_persp(cam, pos, at, lens):
    pos, at = Vector(pos), Vector(at)
    cam.data.type = 'PERSP'
    cam.data.lens = lens
    cam.data.clip_end = 100
    cam.matrix_world = EB.mat((at - pos).normalized().to_track_quat('-Z', 'Y').to_matrix(), pos)


def fit(cam, d, up, pts, margin=1.10):
    """Orthografische Kamera wie blender_build.aim, Maßstab auch für Hochformat richtig (ortho_scale gilt für die längere Bildseite)."""
    BB.aim(cam, d, up, pts, margin)
    inv = cam.matrix_world.inverted()
    loc = [inv @ p for p in pts]
    w = max(p.x for p in loc) - min(p.x for p in loc)
    h = max(p.y for p in loc) - min(p.y for p in loc)
    r = bpy.context.scene.render
    asp = r.resolution_x / r.resolution_y
    cam.data.ortho_scale = (max(w, h * asp) if asp >= 1 else max(w / asp, h)) * margin


def explode(F):
    for name, e in list(F['segs'].items()) + [(f'{s}_{k}', e) for s, S in F['asegs'].items() for k, e in S.items()]:
        off = Vector(RB.EXPLODE[e['asm']]) * MM
        if e['side'] == 'R':
            off.x = -off.x
        e.matrix_world.translation += off
    bpy.context.view_layer.update()


def render_to(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print('[robot] geschrieben', path)


def setup(o, aspect=(4, 5)):
    kit.reset_scene()
    kit.SKINS[RB.SKIN['name']] = {k: v for k, v in RB.SKIN.items() if k != 'name'}
    kit.SKIN['name'] = RB.SKIN['name']
    BB.setup_render(o['res'], o['samples'], aspect=aspect, gpu=o['gpu'], aaa=True, bloom=False, bg='mid')
    for n in bpy.context.scene.world.node_tree.nodes:   # Umgebungslicht dämpfen (mehr Form im Elfenbein), Hintergrund bleibt
        if n.type == 'BACKGROUND' and not n.inputs['Color'].links:
            n.inputs['Strength'].default_value *= AMBIENT
    if o['preview']:
        sc = bpy.context.scene
        sc.render.engine = 'BLENDER_WORKBENCH'
        sc.display.shading.light = 'STUDIO'
        sc.display.shading.color_type = 'MATERIAL'
        sc.display.shading.show_cavity = True
        sc.display.shading.show_shadows = True
        sc.view_settings.view_transform = 'Standard'


def contact_sheet(out, tag):
    """Kontaktbogen der fünf Baugruppen einzeln (ImageMagick), Beschriftung mit Teilezahl."""
    tiles = []
    for a in RB.ASSEMBLIES:
        png = os.path.join(out, f'asm_{a["id"]}{tag}.png')
        if os.path.exists(png):
            n = len(a['module'].parts())
            tiles += ['-label', f"{a['de']} ({a['id']}) · {n} Teile", png]
    exp = os.path.join(out, f'explode{tag}.png')
    if os.path.exists(exp):
        tiles += ['-label', 'Explosionsansicht entlang der Anker', exp]
    res = os.path.join(out, f'contact_assemblies{tag}.png')
    subprocess.run(['magick', 'montage', *tiles, '-tile', '3x', '-geometry', '480x600+10+10', '-background', '#5A6068',
                    '-fill', '#F2F1EE', '-font', 'Helvetica', '-pointsize', '18',
                    '-title', 'BASIC-Roboter 0.5 · fünf Baugruppen', res], check=True)
    print('[robot] geschrieben', res)


def main():
    o = args()
    out = os.path.join(OUT, 'robot')
    os.makedirs(out, exist_ok=True)
    tag = o['tag'] and f"_{o['tag']}"
    if o['check'] or o['spec']:
        kit.reset_scene()
        F = build('idle', mode='color')
        gaps = anchor_gaps(F['obs'])
        bad = {k: v for k, v in gaps.items() if v > GAP_TOL_MM}
        if o['spec']:
            write_spec(F['obs'], gaps)
        drift = spec_drift(F['obs'], gaps)
        msg = []
        if bad:
            msg.append('Lücke an ' + ', '.join(f'{k} {v:.1f} mm' for k, v in bad.items()))
        if drift:
            msg.append('Spec veraltet (' + ', '.join(drift) + '): tools/robot_build.py --spec')
        print('robot_check: ' + ('; '.join(msg) if msg else f'{len(gaps)} Anker ohne Lücke, Spec aktuell'))
        if o['check']:
            sys.exit(1 if msg else 0)
        return
    if o['dry']:                # nur Aufbau und IK der Haltung ready prüfen, kein Rendern, nichts schreiben
        kit.reset_scene()
        build('ready', mode='color')
        print('[robot] dry: Aufbau ready ohne Rendern')
        return
    mode = 'color' if o['preview'] else 'aaa'
    cam = None
    # Haltung ready mit Waffe: Hero, Nah, Seite (grauer Hintergrund, Schattenfänger statt Horizont)
    if o['only'] & {'hero', 'nah', 'seite'}:
        setup(o, aspect=(2, 3))         # Hochformat wie das Zielbild
        lights()
        floor()
        build('ready', mode)
        cam = BB.camera()
        for name, pos, at, lens in (('hero', (-1.9, -3.4, 0.62), (0.0, 0.0, 0.98), 60),     # wie Zielbild: niedrig, Dreiviertel
                                    ('nah', (-1.15, -1.9, 1.55), (0.0, -0.12, 1.36), 50),
                                    ('seite', (-3.8, -1.2, 1.0), (0, 0, 0.98), 60)):
            if name in o['only']:
                camera_persp(cam, pos, at, lens)
                render_to(os.path.join(out, f'{name}{tag}.png'))
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, f'robot{tag}.blend'))
    # Haltung idle ohne Waffe: Explosionsansicht und Einzelblätter je Baugruppe (orthografisch, Dreiviertel von vorn rechts)
    if o['only'] & {'explode', 'parts'}:
        setup(o)
        lights()
        F = build('idle', mode)
        cam = BB.camera()
        d, up = (-0.62, -0.74, 0.18), (0, 0, 1)
        if 'parts' in o['only']:
            for a in RB.ASSEMBLIES:
                keep = [ob for ob in F['obs'].values() if ob['asm'] == a['id']]
                for ob in F['obs'].values():
                    ob.hide_render = ob['asm'] != a['id']
                fit(cam, d, up, BB.bbox_pts(keep), margin=1.12)
                render_to(os.path.join(out, f'asm_{a["id"]}{tag}.png'))
            for ob in F['obs'].values():
                ob.hide_render = False
        if 'explode' in o['only']:
            explode(F)
            fit(cam, d, up, BB.bbox_pts(list(F['obs'].values())), margin=1.05)
            render_to(os.path.join(out, f'explode{tag}.png'))
        contact_sheet(out, tag)


if __name__ == '__main__':
    main()
