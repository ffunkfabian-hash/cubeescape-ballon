"""Ego-Szene: Pilotwaffe + BASIC-Roboterarme, Haltungen und Aktionen aus basic/arms/ego.py, gerendert aus der Ego-Kamera.

  blender -b --factory-startup -P tools/ego_build.py -- [--stills] [--actions a,b|all] [--gpu] [--samples N] [--frames a-b] [--weapon pilot.w01_auto_rifle_v21]

Ausgabe: <OUT>/<Waffe>/ego/stills/<haltung>_{ego,out}.png, ego/<aktion>/####.png, ego/ego.json (aufgelöste Haltungen, Marker,
Gelenkprüfung). Arme sind starre Segmente; Ellbogen per analytischer Zwei-Knochen-IK mit Pol, Hand aus dem Griff (Handfläche auf der
Oberfläche, Fingerrichtung), Finger aus Stellungen. Alles getrennt von Toolgen/Cube Escape.
"""
import importlib
import json
import math
import os
import sys

import bpy
import bmesh
from mathutils import Vector, Matrix, Quaternion

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic import kit  # noqa: E402
from basic.arms import robot_arm as RA, ego as EG  # noqa: E402
from basic.arms import forms as FM  # noqa: E402
import tools.blender_build as BB  # noqa: E402
from tools.paths import OUT  # noqa: E402

MM = 0.001


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    o = dict(stills='--stills' in a, actions=[], gpu='--gpu' in a, samples=32, weapon='pilot.w01_auto_rifle_v21')
    if '--actions' in a:
        v = a[a.index('--actions') + 1]
        o['actions'] = list(EG.ACTIONS) if v == 'all' else v.split(',')
    if '--samples' in a:
        o['samples'] = int(a[a.index('--samples') + 1])
    if '--weapon' in a:
        o['weapon'] = a[a.index('--weapon') + 1]
    o['frames'] = tuple(int(x) for x in a[a.index('--frames') + 1].split('-')) if '--frames' in a else None   # Vorschau: nur Bilder a–b schreiben
    o['rig'] = a[a.index('--rig') + 1] if '--rig' in a else None          # Formstudie statt Arm v3 (0.23): basic.arms.<rig>
    o['poses'] = a[a.index('--poses') + 1].split(',') if '--poses' in a else None
    return o


# ------------------------------------------------------------------ Hilfen
def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def vdir(fux):
    """Richtung im Autorenmaß (f, u, x) → Blender-Vektor (ohne Längenänderung)."""
    return Vector((fux[2], -fux[0], fux[1]))


def frame_from(z, y_hint):
    z = z.normalized()
    y = (y_hint - z * y_hint.dot(z)).normalized()
    x = y.cross(z)
    return Matrix((x, y, z)).transposed()


def mat(rot3, loc):
    m = rot3.to_4x4()
    m.translation = loc
    return m


# ------------------------------------------------------------------ Arm bauen
def plate_verts(bm, p):
    """Facettenplatte (robot_arm.plate): verjüngte Grundfläche im Abstand r(z) von der Segmentachse, Dicke t, Walmdach mit Grat
    (Höhe ridge, an den Enden um hip eingezogen); Lage um die Achse über phi (0 = +Y), seitlich um u verschoben. Konvexe Hülle."""
    z0, z1 = p['z']
    w0, w1 = p['w']
    r0, r1 = p['r']
    h0, h1 = p['hip']
    t, rg, u = p['t'], p['ridge'], p.get('u', 0.0)

    def r(z):
        return r0 + (r1 - r0) * (z - z0) / (z1 - z0)
    pts = []
    for z, w in ((z0, w0), (z1, w1)):
        for s in (-1, 1):
            pts += [(u + s * w / 2, r(z), z), (u + s * w / 2, r(z) + t, z)]
    if rg > 0:
        for z in (z0 + h0, z1 - h1):
            pts.append((u, r(z) + t + rg, z))
    ph = math.radians(p.get('phi', 0.0))
    c, s_ = math.cos(ph), math.sin(ph)
    hull_verts(bm, [(x * c - n * s_, x * s_ + n * c, z) for x, n, z in pts])   # u → X, n → Y, um Z gedreht (phi: +Y → −X)


def hull_verts(bm, pts):
    """Konvexe Hülle aus Punkten in mm (Formen hull und plate)."""
    for x, y, z in pts:
        bm.verts.new((MM * x, MM * y, MM * z))
    res = bmesh.ops.convex_hull(bm, input=bm.verts[:])
    drop = {g for g in res['geom_interior'] + res['geom_unused'] if isinstance(g, bmesh.types.BMVert)}
    if drop:
        bmesh.ops.delete(bm, geom=list(drop), context='VERTS')
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])


FORMS = {'loft': lambda p: FM.loft(p['secs'], p.get('ring', 56), p.get('sub', 6)),
         'wrap': lambda p: FM.wrap(p['secs'], p['a0'], p['a1'], p['t'], p.get('steps'), p.get('sub', 6)),
         'tube': lambda p: FM.tube(p['path'], p['r'], p.get('segs', 14))}


def form_mesh(name, kind, p, sx):
    """Formen aus basic/arms/forms.py (0.23): weich schattiert, Kanten ab 35° scharf, Fugen per cuts (Quader im Segmentrahmen),
    linke Seite an X gespiegelt."""
    V, F = FORMS[kind](p)
    me = bpy.data.meshes.new(name)
    me.from_pydata([(MM * x, MM * y, MM * z) for x, y, z in V], [], F)
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if p.get('cuts'):
        _cut_boxes(ob, p['cuts'])
    if sx < 0:
        ob.data.transform(Matrix.Scale(-1, 4, (1, 0, 0)))
        ob.data.flip_normals()
    ob.data.shade_smooth()
    ob.data.set_sharp_from_angle(angle=math.radians(p.get('sharp', 35)))
    return ob


def _cut_boxes(ob, cuts):
    """Fugen und Durchbrüche: Quader dict(c=(x, y, z), d=(dx, dy, dz), rz=Grad um Z, rx=Grad um X) in mm, Exact-Boolean."""
    bm = bmesh.new()
    for c in cuts:
        geo = bmesh.ops.create_cube(bm, size=1.0)['verts']
        bmesh.ops.scale(bm, vec=Vector(c['d']) * MM, verts=geo)
        R = Matrix.Rotation(math.radians(c.get('rz', 0)), 3, 'Z') @ Matrix.Rotation(math.radians(c.get('rx', 0)), 3, 'X')
        bmesh.ops.rotate(bm, verts=geo, cent=(0, 0, 0), matrix=R)
        bmesh.ops.translate(bm, vec=Vector(c['c']) * MM, verts=geo)
    me = bpy.data.meshes.new(ob.name + '_cut')
    bm.to_mesh(me)
    bm.free()
    cut = bpy.data.objects.new(ob.name + '_cut', me)
    bpy.context.scene.collection.objects.link(cut)
    mod = ob.modifiers.new('BASIC_Cut', 'BOOLEAN')
    mod.operation, mod.solver, mod.use_self, mod.object = 'DIFFERENCE', 'EXACT', True, cut
    bpy.context.view_layer.update()
    res = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    ob.modifiers.remove(mod)
    if len(res.vertices) < 8:
        raise RuntimeError(f'Fuge an {ob.name} ergibt ein leeres Netz')
    res.materials.clear()                  # leerer Platz vom Schneidkörper; die Rolle hängt build_arm danach an
    old = ob.data
    ob.data = res
    bpy.data.meshes.remove(old)
    bpy.data.objects.remove(cut)


def piece_mesh(name, kind, p):
    bm = bmesh.new()
    if kind == 'box':
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=Vector(p['d']) * MM, verts=bm.verts)
    elif kind == 'plate':
        plate_verts(bm, p)
    elif kind == 'hull':
        hull_verts(bm, p['pts'])
    elif kind == 'prism':       # Achteck, Fläche nach +Y, verjüngt von r0 (Anfang) zu r1 (Ende)
        bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=p['r0'] * MM, radius2=p['r1'] * MM, depth=p['len'] * MM)
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(22.5), 3, 'Z'))
    else:
        bmesh.ops.create_cone(bm, cap_ends=True, segments=20, radius1=p['r'] * MM, radius2=p['r'] * MM, depth=p['len'] * MM)
        if p['axis'] == 'x':
            bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, 'Y'))
        elif p['axis'] == 'y':
            bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, 'X'))
    if 'c' in p:
        bmesh.ops.translate(bm, vec=Vector(p['c']) * MM, verts=bm.verts)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if kind == 'cyl':
        for f in me.polygons:
            f.use_smooth = True
    return ob


def build_arm(side):
    sx = 1 if side == 'R' else -1
    segs = {}
    for s in RA.SEGMENTS:
        e = bpy.data.objects.new(f'{side}_{s}', None)
        e.empty_display_size = 0.01
        bpy.context.scene.collection.objects.link(e)
        segs[s] = e
    pieces = {}
    for pid, de, seg, kind, role, p in RA.parts():
        p = dict(p)
        if 'c' in p:
            c = list(p['c'])
            c[0] *= sx
            p['c'] = c
        if kind == 'hull':
            p['pts'] = [(sx * x, y, z) for x, y, z in p['pts']]
        if kind == 'plate':        # Spiegeln an X: Winkel und Seitenversatz umkehren
            p['phi'] = sx * p.get('phi', 0.0)
            p['u'] = sx * p.get('u', 0.0)
        ob = form_mesh(f'{side}_{pid}', kind, p, sx) if kind in FORMS else piece_mesh(f'{side}_{pid}', kind, p)
        ob.data.materials.append(kit.material(role))
        if p.get('bevel') is not None:
            kit.add_bevel(ob, p['bevel'])
        elif kind in ('cyl', 'prism', 'plate', 'hull', 'loft', 'wrap'):
            kit.add_bevel(ob, {'cyl': 0.8, 'prism': 1.6, 'plate': 1.0, 'hull': 1.6, 'loft': 1.2, 'wrap': 0.9}[kind])
        ob.parent = segs[seg]
        pieces[f'{side}_{pid}'] = ob
    return segs, pieces


# ------------------------------------------------------------------ Waffe positionieren
def pose_matrix(W, name, off=None):
    P = EG.profile(W)['poses'][name]                      # Haltungen der Klasse (0.18, ego.CLASSES)
    if 'eye' in P:
        d = Vector(P['aim_dir']).normalized()
    else:
        d = (Vector(P['aim']) - Vector(P['pos'])).normalized()
    up = Vector((0, 0, 1))
    u = (up - d * up.dot(d)).normalized()
    left = (-d).cross(u)                      # lokale +X (links) = (+Y lokal) × (+Z lokal), +Y lokal = −d
    R = Matrix((left, -d, u)).transposed()
    off = off or {}
    roll = P.get('roll', 0) + off.get('roll', 0)
    R = Matrix.Rotation(math.radians(-roll), 3, d) @ R
    # pitch positiv = Mündung hoch, yaw positiv = Mündung nach links
    R = R @ Matrix.Rotation(math.radians(-off.get('pitch', 0)), 3, 'X') @ Matrix.Rotation(math.radians(off.get('yaw', 0)), 3, 'Z')
    if 'eye' in P:
        eye_local = kit.to_xyz(*W.ANCHORS['Socket_Eye']['at'])
        pos = Vector(P['eye']) - R @ eye_local
    else:
        pos = Vector(P['pos'])
    pos = pos + Vector((-off.get('right', 0), off.get('back', 0), off.get('up', 0)))
    return R, pos


def curve(ts, vs, f):
    """Monotone kubische Hermite-Kurve durch Schlüsselwerte (Listen gleicher Länge) – EG.INTERP. Tangente je Komponente aus den
    Nachbarsteigungen, 0 an Halt- und Umkehrpunkten und an den Enden (kein Überschwingen); ohne Tangenten entspricht sie ease()."""
    n = len(ts)
    if f <= ts[0]:
        return list(vs[0])
    if f >= ts[-1]:
        return list(vs[-1])
    i = max(k for k in range(n - 1) if ts[k] <= f)

    def tan(k):
        if k == 0 or k == n - 1:
            return [0.0] * len(vs[k])
        h0, h1 = ts[k] - ts[k - 1], ts[k + 1] - ts[k]
        out = []
        for a, b, c in zip(vs[k - 1], vs[k], vs[k + 1]):
            d0 = (b - a) / h0 if h0 > 0 else 0.0
            d1 = (c - b) / h1 if h1 > 0 else 0.0
            if d0 * d1 <= 0:
                out.append(0.0)
            else:
                m = (d0 + d1) / 2
                lim = 3 * min(abs(d0), abs(d1))
                out.append(max(-lim, min(lim, m)))
        return out
    h = ts[i + 1] - ts[i]
    if h <= 0:
        return list(vs[i + 1])
    s = (f - ts[i]) / h
    h00, h10, h01, h11 = 2 * s ** 3 - 3 * s ** 2 + 1, s ** 3 - 2 * s ** 2 + s, -2 * s ** 3 + 3 * s ** 2, s ** 3 - s ** 2
    m0, m1 = tan(i), tan(i + 1)
    return [h00 * a + h10 * h * ma + h01 * b + h11 * h * mb for a, b, ma, mb in zip(vs[i], vs[i + 1], m0, m1)]


def mats_curve(ts, Ms, f):
    """Kurve durch (Rotation, Position)-Schlüssel: Quaternionen auf eine Halbkugel gelegt, komponentenweise, normiert."""
    vs, qp = [], None
    for R, p in Ms:
        q = R.to_quaternion()
        if qp is not None and q.dot(qp) < 0:
            q.negate()
        qp = q
        vs.append([p.x, p.y, p.z, q.w, q.x, q.y, q.z])
    v = curve(ts, vs, f)
    q = Quaternion(v[3:]).normalized()
    return q.to_matrix(), Vector(v[:3])


def weapon_at(W, keys, f):
    def ev(k):
        return pose_matrix(W, k) if isinstance(k, str) else pose_matrix(W, k[0], k[1])
    return mats_curve([k[0] for k in keys], [ev(k[1]) for k in keys], f)


def spring_step(x, v, target, w, zeta, dt, sub=4):
    """Gedämpfte Feder (Vektor x folgt target), halbimplizit in Unterschritten."""
    h = dt / sub
    for _ in range(sub):
        a = (target - x) * (w * w) - v * (2 * zeta * w)
        v = v + a * h
        x = x + v * h
    return x, v


def secondary(R, pos, f, state, aim=False):
    """EG.SECONDARY: Die Waffe folgt ihrer Kurve träge (Position und Drehung als Federn), dadurch Nachschwingen nach Bewegungen.
    aim: Aktion endet im Zielen, dann kritisch gedämpft (aim_zeta), damit das Visier nicht über die Mitte schwingt."""
    S = EG.SECONDARY
    w = 2 * math.pi * (S['aim_freq_hz'] if aim else S['freq_hz'])
    z, dt = S['aim_zeta'] if aim else S['zeta'], 1.0 / EG.FPS
    q_t = R.to_quaternion()
    if 'sec' not in state:
        state['sec'] = dict(p=pos.copy(), v=Vector(), q=q_t.copy(), av=Vector(), f=f)
        return R, pos
    st = state['sec']
    steps = max(1, int(round(f - st['f'])))
    for _ in range(steps):
        st['p'], st['v'] = spring_step(st['p'], st['v'], pos, w, z, dt)
        for _k in range(4):
            dq = q_t @ st['q'].inverted()
            if dq.w < 0:
                dq.negate()
            err = Vector(dq.axis) * dq.angle if dq.angle > 1e-9 else Vector()
            h = dt / 4
            st['av'] = st['av'] + (err * (w * w) - st['av'] * (2 * z * w)) * h
            ang = st['av'].length * h
            if ang > 1e-12:
                st['q'] = Quaternion(st['av'].normalized(), ang) @ st['q']
    st['f'] = f
    return st['q'].to_matrix(), st['p'].copy()


# ------------------------------------------------------------------ Hände
PALM_CENTER = Vector((0, -RA.PALM_T / 2, RA.PALM_START + RA.PALM_LEN / 2)) * MM


def use_rig(name):
    """Anderes Arm-Rig laden (Formstudien 0.23, basic.arms.<name>); Skelett und Handfläche bestimmen die Griffe."""
    global RA, PALM_CENTER
    RA = importlib.import_module(f'basic.arms.{name}')
    PALM_CENTER = Vector((0, -RA.PALM_T / 2, RA.PALM_START + RA.PALM_LEN / 2)) * MM


GRIPS = EG.GRIPS          # Griffe der Waffe in der Szene (Scene setzt sie aus ego.profile, 0.18); ohne Szene die der Pilotwaffe


def grip_hand(gname, part_world, offset=None):
    G = GRIPS[gname]
    M = part_world(G.get('part'))
    c = M @ kit.to_xyz(*G['contact'])
    if offset:
        c = c + M.to_3x3() @ vdir(offset) * MM
    palm = (M.to_3x3() @ vdir(G['palm'])).normalized()
    fing = (M.to_3x3() @ vdir(G['fingers'])).normalized()
    R = frame_from(fing, -palm)
    return mat(R, c - R @ PALM_CENTER), G['fingers_pose']


def hand_target(key, part_world, cam_rot=None):
    if isinstance(key, str):
        return grip_hand(key, part_world)
    if key[0] == 'cam':
        H, fp = grip_hand('support', part_world)
        return mat(H.to_3x3(), Vector(key[1]) - H.to_3x3() @ PALM_CENTER), 'relaxed'
    return grip_hand(key[0], part_world, key[1])


def blend_hand(keys, f, part_world):
    return mat(*mats_curve([k[0] for k in keys], [(lambda H: (H.to_3x3(), H.translation))(hand_target(k[1], part_world)[0])
                                                  for k in keys], f))


def blend_fingers(keys, f):
    def flat(n):
        P = EG.FINGER_POSES[n]
        return [x for fi in P['f'] for x in fi] + list(P['t'])
    v = curve([k[0] for k in keys], [flat(k[1]) for k in keys], f)
    nf, nl = len(RA.FINGER_X), len(RA.FINGER_LINKS)
    return dict(f=[v[i * nl:(i + 1) * nl] for i in range(nf)], t=v[nf * nl:])


def solve_arm(side, segs, H, fp, report):
    """Viewmodel-Konvention (wie Toolgen arm_pose.forearm): Der Unterarm folgt der Hand, gemischt mit einer bevorzugten Richtung
    nach hinten unten außen, Knick am Handgelenk höchstens RA.WRIST_TARGET_DEG; der Oberarm zeigt zur Schulter, die Schulter folgt
    (liegt außerhalb des Bildes)."""
    sx = 1 if side == 'R' else -1
    Wp = H.translation
    a, b = RA.UPPER_MM * MM, RA.FORE_MM * MM
    back = -H.to_3x3().col[2].normalized()
    pref = Vector((sx * RA.FOREARM_PREF[0], RA.FOREARM_PREF[1], RA.FOREARM_PREF[2])).normalized()
    fdir = (back * 0.55 + pref * 0.45).normalized()
    lim = math.radians(RA.WRIST_TARGET_DEG)
    if fdir.angle(back) > lim:
        fdir = back.slerp(pref, lim / max(1e-6, back.angle(pref))) if back.angle(pref) > 1e-6 else back
    E = Wp + fdir * b
    S0 = Vector(RA.SHOULDER[side])
    S = E + (S0 - E).normalized() * a
    # Drehgelenk in der Stulpe (v2): Ober- und Unterarm zeigen ihre Panzerseite (+Y) zur Kamera (Ursprung), die Hand dreht frei
    hy = H.to_3x3().col[1]
    view = -(E + Wp) / 2
    hint = view.normalized() if view.length > 1e-6 else hy
    segs['upper'].matrix_world = mat(frame_from(E - S, hint), S)
    segs['fore'].matrix_world = mat(frame_from(Wp - E, hint), E)
    segs['hand'].matrix_world = H
    bend = math.degrees((Wp - E).normalized().angle(H.to_3x3().col[2]))
    report['wrist_max_deg'] = max(report.get('wrist_max_deg', 0), bend)
    if (S - S0).length > 0.25:      # Schulter weiter als 25 cm vom Ankerpunkt: Haltung prüfen
        report['overreach'] = report.get('overreach', 0) + 1
    # Finger
    scale = getattr(RA, 'FINGER_SCALE', [1.0] * len(RA.FINGER_X))
    for i in range(len(RA.FINGER_X)):
        M = H @ Matrix.Translation(Vector((sx * RA.FINGER_X[i], 0, RA.KNUCKLE_Z)) * MM)
        for j, L0 in enumerate(RA.FINGER_LINKS):
            Lk = L0 * scale[i]
            M = M @ Matrix.Rotation(math.radians(fp['f'][i][j]), 4, 'X')
            segs[f'f{i}_{j}'].matrix_world = M
            M = M @ Matrix.Translation((0, 0, Lk * MM))
    tb = Vector((sx * RA.THUMB_BASE[0], RA.THUMB_BASE[1], RA.THUMB_BASE[2])) * MM
    td = Vector((sx * RA.THUMB_DIR[0], RA.THUMB_DIR[1], RA.THUMB_DIR[2]))
    flex, out, tip = fp['t']
    T = H @ mat(frame_from(td, Vector((0, 1, 0))), tb) @ Matrix.Rotation(math.radians(-sx * (out - 30)), 4, 'Y')
    for j, Lk in enumerate(RA.THUMB_LINKS):
        T = T @ Matrix.Rotation(math.radians([flex, tip * 0.6, tip][j]), 4, 'X')
        segs[f't_{j}'].matrix_world = T
        T = T @ Matrix.Translation((0, 0, Lk * MM))


# ------------------------------------------------------------------ Mündungsfeuer und Hülsen (0.16, Entscheidungsliste 5.3 A / 5.4 A)
def fx_mesh(name, V, faces, mats):
    me = bpy.data.meshes.new(name)
    me.from_pydata([vdir(v) * MM for v in V], [], [f for f, _ in faces])
    for m in mats:
        me.materials.append(m)
    for poly, (_, k) in zip(me.polygons, faces):
        poly.material_index = k
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.hide_render = True
    return ob


def emit_material(role):
    """Reine Emission wie kit.aaa_nodes bei emit_only (Stärke emit · 1,6, Grundfarbe schwarz); Unity: BallonSetup aus ego.json › roles."""
    d = EG.FLASH['roles'][role]
    m = bpy.data.materials.new(f'MT_{role}')
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0, 0, 0, 1)
    b.inputs['Specular IOR Level'].default_value = 0.0
    b.inputs['Emission Color'].default_value = kit.hex_rgba(d['color'])
    b.inputs['Emission Strength'].default_value = d['emit'] * 1.6
    return m


def build_fx(W):
    V, core, flame = EG.flash_mesh()
    fl = fx_mesh('FX_flash', V, [(t, 0) for t in core] + [(t, 1) for t in flame],
                 [emit_material(EG.FLASH['core']['role']), emit_material(EG.FLASH['tongues']['role'])])
    fl.visible_shadow = False                     # Leuchtkörper ohne Schatten (Unity: ShadowCastingMode.Off)
    shells = []
    E = getattr(W, 'EJECT', None)
    if E:
        CV, CF = EG.case_mesh(E['case'])
        brass = kit.material(EG.EJECT['role'], 'aaa')
        for k in range(EG.EJECT['max_live']):
            shells.append(fx_mesh(f'FX_shell_{k}', CV, [(t, 0) for t in CF], [brass]))
    links = []
    if E and E.get('links'):                      # Gurtglieder (0.34): eigene Form, eigener Pool, mit jeder Hülse
        LV, LF = EG.case_mesh(E['links']['case'])
        dark = kit.material('dark_metal', 'aaa')
        for k in range(EG.EJECT['max_live']):
            links.append(fx_mesh(f'FX_link_{k}', LV, [(t, 0) for t in LF], [dark]))
    return dict(flash=fl, shells=shells, links=links)


def eject_data(W):
    """(Lage im Waffenrahmen, Geschwindigkeit im Waffenrahmen, Drehachse) aus W.EJECT und EG.EJECT oder None (Waffe ohne Auswurf)."""
    E = getattr(W, 'EJECT', None)
    if not E:
        return None
    return vdir(E['at']) * MM, vdir(E['dir']).normalized() * EG.EJECT['speed_mps'] * E.get('speed_k', 1.0), \
        vdir(EG.EJECT['spin_axis']).normalized()


def link_data(W):
    """Wie eject_data für das Gurtglied (EJECT links, 0.34) oder None."""
    E = getattr(W, 'EJECT', None)
    L = E.get('links') if E else None
    if not L:
        return None
    return vdir(L['at']) * MM, vdir(L['dir']).normalized() * EG.EJECT['speed_mps'], vdir(EG.EJECT['spin_axis']).normalized()


def shell_matrix(W0, ej, t):
    """Hülse t Sekunden nach dem Schuss: Start im Auswurffenster der Waffe im Schussbild (W0), gerade Bahn plus Schwerkraft nach unten im
    Kameraraum, Drehung um spin_axis der Waffe. Gleiche Formel in Unity (EgoSolver.ShellMatrix)."""
    p0, v, ax = ej
    R0 = W0.to_3x3()
    p = W0 @ p0 + (R0 @ v) * t + Vector((0, 0, -0.5 * EG.EJECT['gravity_mps2'] * t * t))
    return mat(R0 @ Matrix.Rotation(math.radians(EG.EJECT['spin_dps'] * t), 3, ax), p)


def fx_eval(sc, A, f, state):
    """Blitz (sichtbar für FLASH.dur_s ab dem Schussbild, gedreht nach flash_roll) und Hülsen (ab dem Schussbild + delay_frames für
    life_s, höchstens max_live gleichzeitig) im Bild f; Ergebnis in sc.fx_now, Objekte (falls gebaut) werden gesetzt."""
    fire = A.get('fire', [])
    now = dict(flash=None, shells={}, links={})
    i = EG.flash_visible(fire, f) if sc.P['gameplay'].get('muzzle_flash', True) else None   # Werkzeug (0.22): ohne Mündungsfeuer
    if i is not None:
        mz = vdir(sc.W.ANCHORS['Socket_Muzzle']['at']) * MM
        now['flash'] = sc.WM @ Matrix.Translation(mz) @ Matrix.Rotation(math.radians(EG.flash_roll(i)), 4, 'Y') @ \
            Matrix.Scale(sc.P['gameplay'].get('flash_scale', 1.0), 4)            # Blitzmaßstab je Klasse (0.33 P4, Werfer)
    ej = eject_data(sc.W)
    if ej and fire and sc.W.EJECT.get('on') != 'reload':   # Trommel (0.33 P4, EJECT on='reload'): Hülsen nur beim Nachladen (Unity: Marker Eject)
        W0s = state.setdefault('shot_wm', {})
        for k, s in enumerate(fire):
            if s <= f and k not in W0s:
                W0s[k] = sc.WM.copy()                # Waffe im Schussbild (nach dem Rückstoß dieses Bilds)
        live = [k for k, s in enumerate(fire) if 0 <= (f - s) / EG.FPS - EG.EJECT['delay_frames'] / EG.FPS < EG.EJECT['life_s']]
        lk = link_data(sc.W)
        for k in live[-EG.EJECT['max_live']:]:
            now['shells'][k] = shell_matrix(W0s[k], ej, (f - fire[k] - EG.EJECT['delay_frames']) / EG.FPS)
            if lk:
                now['links'][k] = shell_matrix(W0s[k], lk, (f - fire[k] - EG.EJECT['delay_frames']) / EG.FPS)
    sc.fx_now = now
    if sc.fx:
        ob = sc.fx['flash']
        ob.hide_render = now['flash'] is None
        if now['flash'] is not None:
            ob.matrix_world = now['flash']
        n = len(sc.fx['shells'])
        for slot, sh in enumerate(sc.fx['shells']):
            k = next((k for k in now['shells'] if k % n == slot), None)
            sh.hide_render = k is None
            if k is not None:
                sh.matrix_world = now['shells'][k]
        for slot, lo in enumerate(sc.fx.get('links', ())):
            k = next((k for k in now['links'] if k % n == slot), None)
            lo.hide_render = k is None
            if k is not None:
                lo.matrix_world = now['links'][k]


# ------------------------------------------------------------------ Szene
class Scene:
    def __init__(self, W, o):
        global GRIPS
        kit.reset_scene()
        self.W = W
        self.P = EG.profile(W)                                  # Ego-Profil der Waffe: Haltungen, Aktionen, Griffe, Live-Teile (0.18)
        GRIPS = self.P['grips']
        self.root, self.objs, self.anchors = kit.build(W)
        bpy.context.view_layer.update()
        for ob in self.objs.values():
            ob['rest'] = [list(r) for r in ob.matrix_world]
        self.byid = {p['id']: p for p in W.PARTS}
        self.arms = {s: build_arm(s) for s in ('R', 'L')}
        self.fx = build_fx(W) if o.get('fx', True) else None      # Mündungsfeuer und Hülsen (0.16); der Export braucht nur die Matrizen
        self.fx_now = dict(flash=None, shells={}, links={})
        BB.setup_render(854, o['samples'], gpu=o['gpu'], aaa=True, bloom=False, bg='mid')
        kit.set_mode(self.objs, 'aaa')
        for s in ('R', 'L'):
            kit.set_mode(self.arms[s][1], 'aaa')
        c = bpy.data.cameras.new('Ego')
        c.sensor_fit = 'HORIZONTAL'
        c.sensor_width = 36
        c.lens = 18 / math.tan(math.radians(EG.CAMERA['h_fov_deg'] / 2))
        c.clip_start = EG.CAMERA['near_m']
        self.cam = bpy.data.objects.new('Ego', c)
        bpy.context.scene.collection.objects.link(self.cam)
        self.cam_base = Matrix.Rotation(math.pi, 4, 'Z') @ Matrix.Rotation(math.pi / 2, 4, 'X')   # Blick −Y, oben +Z
        self.cam.matrix_world = self.cam_base
        o2 = bpy.data.cameras.new('Out')
        o2.lens = 40
        self.out_cam = bpy.data.objects.new('Out', o2)
        bpy.context.scene.collection.objects.link(self.out_cam)
        look = Vector((-0.12, -0.42, -0.25))
        posn = Vector((-1.05, 0.05, 0.10))
        self.out_cam.matrix_world = mat((look - posn).normalized().to_track_quat('-Z', 'Y').to_matrix(), posn)
        bpy.context.scene.camera = self.cam
        self.WM = Matrix.Identity(4)

    def part_world(self, pid):
        if pid is None:
            return self.WM
        ob = self.objs[pid]
        return ob.matrix_world @ Matrix(ob['rest']).inverted()   # Bewegung des Teils relativ zur Ruhelage, mal Waffe

    def set_weapon(self, R, pos, mech, report, carry=None, drop=None):
        self.WM = mat(R, pos)
        self.root.matrix_world = self.WM
        bpy.context.view_layer.update()
        order = sorted([p for p in self.W.PARTS if p.get('move')], key=lambda p: 1 if p.get('parent_part') else 0)
        for p in order:
            ob = self.objs[p['id']]
            t = mech.get(p['id'], 0.0)
            Ml = BB.move_matrix(ob, p['move'], t)
            if p.get('parent_part'):
                par = self.objs[p['parent_part']]
                ob.matrix_world = par.matrix_world @ Matrix(par['rest']).inverted() @ Ml
            else:
                ob.matrix_world = self.WM @ Ml
            if p['move']['kind'] == 'glow':        # nur das Leuchten: apply_move setzt die Lage ohne Waffenmatrix (0.30 Vorschlag 6)
                M = ob.matrix_world.copy()
                BB.apply_move(ob, p['move'], t)
                ob.matrix_world = M
        mag = self.objs.get(self.P['mag'])        # Bauteil des Griffs 'mag' (Magazin, Energiezelle; 0.33)
        if mag is not None and carry is not None:
            mag.matrix_world = carry
        if mag is not None and drop is not None:
            mag.matrix_world = drop
        bpy.context.view_layer.update()

    def hands(self, Hs, fps, report):
        for s in ('R', 'L'):
            solve_arm(s, self.arms[s][0], Hs[s], fps[s], report)
        bpy.context.view_layer.update()


def still_action(P, name):
    """Standbild einer Haltung (Stills, Export-Referenz; Unity EgoSolver.StillAction): Hände wie in Ruhe (idle_hip), im Zielen wie am Ende
    von aim_in (0.33 P4: Bogen mit Bogenhand links, Zughand im ungespannten Zielen unter dem Bild), inspect_r mit der Hand unter dem Bild
    wie in der Aktion inspect, reload mit der Hand am Magazin."""
    I = P['actions']['aim_in' if name == 'ads' else 'idle_hip']
    A = dict(L=I.get('L', [(0, 'support')])[-1:], R=I.get('R', [(0, 'grip')])[-1:], fL=I['fL'][-1:], fR=I.get('fR', [(0, 'trigger')])[-1:])
    A = {k: [(0, v[0][1])] for k, v in A.items()}
    A['weapon'] = [(0, name)]
    if name == 'inspect_r':
        for ch in ('L', 'R'):
            cam = [k for k in P['actions']['inspect'].get(ch, []) if isinstance(k[1], tuple) and k[1][0] == 'cam']
            if cam:
                A[ch] = [(0, cam[0][1])]
    if name == 'reload':
        A.update(L=[(0, 'mag')], fL=[(0, 'mag_hold')])
    return A


def evaluate(sc, A, f, report, state):
    W = sc.W
    R, pos = weapon_at(W, A['weapon'], f)
    R, pos = secondary(R, pos, f, state, EG.ends_in_ads(A))
    # Zielfernrohr (0.20, EG.ADS_HIDE): Teile mit ads_hide aus, solange der Augenpunkt der Grundhaltung nah an der Kamera liegt
    eye = pos + R @ kit.to_xyz(*W.ANCHORS['Socket_Eye']['at']) if 'Socket_Eye' in W.ANCHORS else None
    ads_eye = Vector(sc.P['poses'].get('ads', {}).get('eye', (0, 0, 0)))   # 0.33 P4: Ziellage des Augenpunkts (Bogen: hinter der Kamera)
    hidden = eye is not None and (eye - ads_eye).length < EG.ADS_HIDE['eye_m']
    for p in W.PARTS:
        if (p.get('ads_hide') or p['id'] in sc.P['ads_hide']) and p['id'] in sc.objs:
            sc.objs[p['id']].hide_render = hidden
    if sc.P['gameplay'].get('ads_hide_arms'):    # 0.35 (Nutzerentscheid 193 B, ego.ADS_STRIP): im Zielen auch die Arme aus
        for s in ('R', 'L'):
            for ob in sc.arms[s][1].values():
                ob.hide_render = hidden
    report['ads_hidden'] = sc.ads_hidden = hidden
    off_pos, off_rot = Vector(), Matrix.Identity(3)
    cam_pitch = 0.0
    Bz = EG.BREATHE_ALL                      # dezentes Atmen in jeder Aktion (Echtzeit, unabhängig vom Ablauftempo)
    ph_b = 2 * math.pi * f / (Bz['period_s'] * EG.FPS)
    off_pos.z += Bz['up_m'] * math.sin(ph_b)
    off_rot = Matrix.Rotation(math.radians(-Bz['pitch_deg'] * math.sin(ph_b + 0.8)), 3, 'X')
    if A.get('breathe'):
        off_pos.z += 0.0015 * math.sin(2 * math.pi * f / 60)
        off_rot = Matrix.Rotation(math.radians(-0.25 * math.sin(2 * math.pi * f / 60 + 1)), 3, 'X')
    if A.get('bob'):
        B = A['bob']
        if B['start'] <= f <= B['end']:
            w = min(1.0, (f - B['start']) / 4, (B['end'] - f) / 4)
            ph = 2 * math.pi * (f - B['start']) / B['period']
            up = -math.cos(2 * ph) if B.get('shape') == 'u' else math.sin(2 * ph)   # u: oben an den Seitenumkehren (Destiny-Sprint)
            off_pos += Vector((B['amp'][0] * math.sin(ph) * w, 0, B['amp'][1] * up * w))
            off_rot = off_rot @ Matrix.Rotation(math.radians(B['roll'] * math.sin(ph) * w), 3, 'Y')
    mech = {}
    for pid, keys in A.get('mech', {}).items():
        mech[pid] = BB.value_at(keys, f)
    shots = [s for s in A.get('fire', []) if s <= f]
    still, rec_pos, rec_deg = 0.0, Vector(), 0.0     # 0.36: Stützhand (support_still) nur mit Rückstoß
    if A.get('fire'):                        # EG.RECOIL: Impuls je Schuss in gedämpfte Federn (Waffe zurück/hoch, Kamera getrennt)
        k, Rc, dt = A.get('kick', 1.0), sc.P['recoil'], 1.0 / EG.FPS   # 0.35: Rückstoßsatz der Klasse (ego.profile)
        # Zielen (5.1 A): kleiner Modellkick, kein Hochziehen, der Kamera-Ruck geht nur in die Welt (hier ohne Welt: Kamera steht)
        kb, kp, kc, kl = (Rc['ads_back'], Rc['ads_pitch'], 0.0, 0.0) if EG.ends_in_ads(A) else (1.0, 1.0, 1.0, 1.0)
        rc = state.setdefault('rec', dict(x=Vector(), v=Vector(), cx=Vector(), cv=Vector(), f=f - 1))
        for fr in range(int(rc['f']) + 1, int(f) + 1):
            for s in A['fire']:
                if fr - 1 < s <= fr:
                    rc['v'] += Vector((Rc['back_mps'] * k * kb, Rc['pitch_dps'] * k * kp, 0))
                    rc['cv'] += Vector((Rc['cam_dps'] * k * kc, 0, 0))
            rc['x'], rc['v'] = spring_step(rc['x'], rc['v'], Vector(), 2 * math.pi * Rc['freq_hz'], Rc['zeta'], dt)
            rc['cx'], rc['cv'] = spring_step(rc['cx'], rc['cv'], Vector(), 2 * math.pi * Rc['cam_freq_hz'], Rc['cam_zeta'], dt)
        rc['f'] = f
        climb = Rc['climb_deg'] * k * kl * len(shots) * math.exp(-max(0, f - A['fire'][-1]) / 8)
        cam_pitch = rc['cx'].x
        rec_pos, rec_deg = R @ Vector((0, rc['x'].x, 0)), -(rc['x'].y + climb)
        off_pos += rec_pos
        off_rot = off_rot @ Matrix.Rotation(math.radians(rec_deg), 3, 'X')   # Mündung steigt
        still = 0.0 if EG.ends_in_ads(A) else Rc.get('support_still', 0.0)   # 0.36: Stützhand folgt dem Kick nicht (Hüfte)
        live = sc.P['live']                  # Live-Teile der Waffe (ego.LIVE bzw. Modul-Feld EGO_LIVE)
        G = sc.P['gameplay']
        charge_f = G['charge_s'] * EG.FPS if sc.P['fire_mode'] in EG.CHARGE_MODES else 0.0   # Ladewaffe (0.33): Abzug ab dem Aufladen
        trig = 1.0 if EG.trigger_on(A['fire'], f, sc.P['fire_mode'] in EG.SEMI_MODES, lead=charge_f) else 0.0   # je Schuss
        if live.get('trigger'):              # Bogen (0.33 P4): ohne Abzug
            mech[live['trigger']] = trig
        for g in live.get('glow', ()):       # Dauerstrahl (0.33): Leuchtteile an, solange der Abzug zieht; Ladewaffe: mit der Ladung
            mech[g] = EG.charge_level(A['fire'], f, charge_f, G.get('burst_shots') or 1, G['charge_fade_s'] * EG.FPS) if charge_f \
                else trig
        if live.get('bolt'):                 # Werkzeug (0.22): ohne Verschluss und Auswurfklappe
            mech[live['bolt']] = 1.0 if shots and f - shots[-1] < 1.5 else 0.0
        if live.get('port'):
            mech[live['port']] = 1.0 if shots else 0.0
        for q in live.get('index', ()):      # Schrittteile (0.34): Trommel eine Kammer, Gurt eine Gliedteilung je Schuss
            mech[q] = EG.index_level(A['fire'], f, EG.index_frames(G['rpm']))
    for q in sc.P['live'].get('fill', ()):  # Zählzellen (0.34): in den Clips voller Kasten (Füllstand nur im Spiel, Unity)
        mech.setdefault(q, 1.0)
    R2 = R @ off_rot
    pos2 = pos + off_pos
    # Magazin: fallen (leer) oder in der linken Hand
    carry = drop = None
    sc.set_weapon(R2, pos2, mech, report)
    pw = sc.part_world
    Lkeys = A.get('L', [(0, 'support')])
    Rkeys = A.get('R', [(0, 'grip')])
    HL = blend_hand(Lkeys, f, pw)
    HR = blend_hand(Rkeys, f, pw)
    if still > 0:                            # 0.36: linke Hand an der Waffe ohne Rückstoß (Unity EgoController.SupportStill)
        WM = Matrix.Translation(pos2) @ R2.to_4x4()
        WN = Matrix.Translation(pos2 - rec_pos) @ (R2 @ Matrix.Rotation(math.radians(-rec_deg), 3, 'X')).to_4x4()
        HS = WN @ WM.inverted() @ HL
        HL = Matrix.Translation(HL.translation.lerp(HS.translation, still)) @ \
            HL.to_quaternion().slerp(HS.to_quaternion(), still).to_matrix().to_4x4()
    if A.get('drop') and A['drop'][0] <= f < A['carry'][0][0]:
        t = (f - A['drop'][0]) / FPS_F
        mag0 = sc.WM @ Matrix(sc.objs[sc.P['mag']]['rest'])
        drop = Matrix.Translation(Vector((0.02 * t, -0.05 * t, -0.5 * 9.81 * t * t - 0.3 * t))) @ mag0 @ \
            Matrix.Rotation(math.radians(-140 * t), 4, 'X')
        if f >= A['drop'][1]:
            drop = Matrix.Translation(Vector((0, 0, -5))) @ mag0
    for c0, c1 in A.get('carry', []):
        if c0 <= f <= c1:
            if 'rel' not in state:
                Hm, _ = grip_hand('mag', lambda pid: sc.WM if pid is None else sc.WM)
                state['rel'] = Hm.inverted() @ (sc.WM @ Matrix(sc.objs[sc.P['mag']]['rest']))
            carry = HL @ state['rel']
    if carry is not None or drop is not None:
        sc.set_weapon(R2, pos2, mech, report, carry=carry, drop=drop)
    # Standbilder ohne fL: Fingerstellung des Stützgriffs (Pilotwaffe underhand, MP foregrip)
    fps = {'L': blend_fingers(A.get('fL', [(0, GRIPS['support']['fingers_pose'])]), f), 'R': blend_fingers(A.get('fR', [(0, 'trigger')]), f)}
    sc.hands({'L': HL, 'R': HR}, fps, report)
    sc.cam.matrix_world = sc.cam_base @ Matrix.Rotation(math.radians(cam_pitch), 4, 'X')
    fx_eval(sc, A, f, state)
    # Visier-Standard v2: das Waffenmodell wird beim Zielen nicht vergrößert (reticles.SIGHT['viewmodel_zoom'] = 1,0); nur die Welt zoomt
    # (in Unity), hier gibt es keine Welt – die Ego-Kamera bleibt beim Grundbildwinkel.


FPS_F = float(EG.FPS)


def main():
    o = args()
    W = importlib.import_module(f'basic.{o["weapon"]}')
    wid = W.META['id'] + (f"-{W.META['variant']}" if W.META.get('variant') else '')
    out = os.path.join(OUT, wid, 'ego')
    if o['rig']:                                   # Formstudie (0.23): eigenes Rig, eigener Ordner, Ego-Daten bleiben unberührt
        use_rig(o['rig'])
        out = os.path.join(OUT, 'arms', 'studies', o['rig'].split('.')[-1], wid)
    os.makedirs(os.path.join(out, 'stills'), exist_ok=True)
    sc = Scene(W, o)
    if o['actions'] == list(EG.ACTIONS):          # 'all': Aktionen der Klasse (Werkzeug ohne Zielen/Nachladen, mit fire_a/fire_b; 0.22)
        o['actions'] = list(sc.P['actions'])
    meta = dict(weapon=wid, camera=EG.CAMERA, fps=EG.FPS, poses={}, actions={}, source=RA.SOURCE)
    scn = bpy.context.scene
    if o['stills']:
        scn.render.resolution_x, scn.render.resolution_y = 1600, 900
        scn.cycles.samples = max(96, o['samples'])
        for name in [k for k in ('hip', 'ads', 'sprint', 'lowered', 'reload', 'inspect_l', 'inspect_r', 'crouch')
                     if k in sc.P['poses'] and (not o['poses'] or k in o['poses'])]:
            rep = {}
            A = still_action(sc.P, name)
            evaluate(sc, A, 0, rep, {})
            for camname, cam in (('ego', sc.cam), ('out', sc.out_cam)):
                scn.camera = cam
                scn.render.filepath = os.path.join(out, 'stills', f'{name}_{camname}.png')
                bpy.ops.render.render(write_still=True)
            scn.camera = sc.cam
            R, pos = pose_matrix(W, name)
            meta['poses'][name] = dict(socket_hand_m=[round(v, 4) for v in pos], src=sc.P['poses'][name]['src'],
                                       wrist_bend_max_deg=round(rep.get('wrist_max_deg', 0), 1), overreach=rep.get('overreach', 0))
    scn.render.resolution_x, scn.render.resolution_y = 854, 480
    scn.cycles.samples = o['samples']
    for name in o['actions']:
        A = sc.P['actions'][name]
        d = os.path.join(out, name)
        os.makedirs(d, exist_ok=True)
        rep, state = {}, {}
        for f in range(0, A['frames'] + 1, A.get('step', 1)):
            evaluate(sc, A, f, rep, state)                     # lückenlos auswerten (Federn, Hülsen), gerendert wird ggf. nur ein Ausschnitt
            if o.get('frames') and not o['frames'][0] <= f <= o['frames'][1]:
                continue
            scn.render.filepath = os.path.join(d, f'{f:04d}.png')
            bpy.ops.render.render(write_still=True)
        meta['actions'][name] = dict(de=A['de'], frames=A['frames'], step=A.get('step', 1), events=A.get('events', []),
                                     src=A['src'], wrist_bend_max_deg=round(rep.get('wrist_max_deg', 0), 1),
                                     overreach_frames=rep.get('overreach', 0))
        print(f"[ego] {name}: {A['frames']} Bilder, Handgelenk max {rep.get('wrist_max_deg', 0):.0f}°")
    if o['rig']:
        json.dump(meta, open(os.path.join(out, 'study.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        return
    mp = os.path.join(out, 'ego.json')
    if os.path.exists(mp):
        old = json.load(open(mp, encoding='utf-8'))
        old['poses'].update(meta['poses'])
        old['actions'].update(meta['actions'])
        meta = dict(old, **{k: v for k, v in meta.items() if k not in ('poses', 'actions')}, poses=old['poses'], actions=old['actions'])
    json.dump(meta, open(mp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, f'{wid}_ego.blend'))


if __name__ == '__main__':
    main()
