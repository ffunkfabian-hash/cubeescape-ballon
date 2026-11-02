"""Arm-Paket `ballon-arms/1` (0.40 „Brace“): neu erzeugt = bytegleich, Reimport erhält Teile, Hierarchie, Anker und Ruhelage.

  blender -b --factory-startup -P tools/test_arm_package.py

1. Bezug: die Szene, aus der export_arms die Dateien schreibt (export_arms.build), mit dem Welt-Hüllquader jedes Teilnetzes (nach den
   Fasen).
2. arms.glb und arms.fbx aus packages/ego-arms/ einlesen: jeder erwartete Knoten (Wurzel, Segment, Teil, Anker je Seite) ist da, kein
   fremder; Eltern wie im Manifest; Wurzeln, Segmente und Anker sind Leerknoten, Teile Netze mit ihrer Rolle als Material; Weltlage und
   Weltdrehung der Wurzeln, Segmentursprünge und Anker wie im Manifest (≤ TOL_MM, ≤ TOL_DEG, Maßstab 1); Hüllquader jedes Teils wie
   im Bezug (≤ TOL_MM); Dreiecke je Segment wie im Manifest; UVs je Teil wie im Bezug (Fläche und Schwerpunkt im UV-Raum, unabhängig
   von Eckenteilung und Reihenfolge); Grundfarbe-Textur am Material (GLB: dazu ORM und Normale, eingebettet).
   Bezug der UVs ist das Unity-arms.fbx (darauf ist der Atlas gebacken), über export_arms.build übernommen.
3. Paket neu in einen Temp-Ordner erzeugen (tools/export_arms.export_files): arms.glb bytegleich, Dreiecke und Netzmaße wie im
   Manifest.
Gegenprobe: falscher Elternknoten, um 1 mm verschobene Hand, um 1° verdrehter Griffpunkt, ein um 1 mm verschobenes Netz und um 0,001
verschobene UVs müssen gemeldet werden.
"""
import copy
import json
import math
import os
import sys
import tempfile

import bpy
from mathutils import Quaternion, Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic import kit  # noqa: E402
import tools.export_arms as XA  # noqa: E402

TOL_MM = 0.05
TOL_DEG = 0.01


def expected(M):
    """{Knoten: (Eltern, Art, Rolle oder None, Weltlage m oder None, Weltdrehung wxyz oder None)} für beide Seiten aus dem Manifest."""
    E = {}
    for s in XA.SIDES:
        r = M['rest_pose']['roots'][s]
        E[f'{s}_arm'] = (None, 'EMPTY', None, r['at_m'], r['rot_wxyz'])
        for g in M['segments']:
            E[f"{s}_{g['id']}"] = (f"{s}_{g['parent']}", 'EMPTY', None, g['rest'][s]['world_m'], g['rest'][s]['world_wxyz'])
        for p in M['parts']:
            E[f"{s}_{p['id']}"] = (f"{s}_{p['segment']}", 'MESH', p['role'], None, None)
        for a in M['anchors']:
            E[a['node'][s]] = (f"{s}_{a['segment']}", 'EMPTY', None, a['world_m'][s], a['world_wxyz'][s])
    return E


def bbox(o, dg):
    """Welt-Hüllquader des ausgewerteten Netzes (min, max)."""
    me = o.evaluated_get(dg).to_mesh()
    P = [o.matrix_world @ v.co for v in me.vertices]
    o.evaluated_get(dg).to_mesh_clear()
    return [Vector([min(p[i] for p in P) for i in range(3)]), Vector([max(p[i] for p in P) for i in range(3)])]


def uvsig(o, dg):
    """UV-Fläche und flächengewichteter UV-Schwerpunkt über die Dreiecke (unabhängig von Eckenteilung und Schleifenreihenfolge)."""
    me = o.evaluated_get(dg).to_mesh()
    me.calc_loop_triangles()
    uv = me.uv_layers.active.data if me.uv_layers else None
    A = cx = cy = 0.0
    for t in me.loop_triangles if uv else ():
        (ax, ay), (bx, by), (qx, qy) = (uv[i].uv for i in t.loops)
        a = abs((bx - ax) * (qy - ay) - (qx - ax) * (by - ay)) / 2
        A, cx, cy = A + a, cx + a * (ax + bx + qx) / 3, cy + a * (ay + by + qy) / 3
    o.evaluated_get(dg).to_mesh_clear()
    return (A, cx / A, cy / A) if A > 0 else (0.0, 0.0, 0.0)


def reference():
    """Hüllquader und UV-Kennung je Teil in der Szene, aus der export_arms die Dateien schreibt."""
    arms = XA.build()
    dg = bpy.context.evaluated_depsgraph_get()
    return {o.name: (bbox(o, dg), uvsig(o, dg)) for side in arms.values() for o in side[2].values()}


def problems(E, M, REF, label):
    bad = []
    obs = {o.name: o for o in bpy.data.objects}
    bad += [f'{label}: fehlt {n}' for n in E if n not in obs]
    bad += [f'{label}: fremder Knoten {n}' for n in obs if n not in E]
    dg = bpy.context.evaluated_depsgraph_get()
    tri = {s: {g['id']: 0 for g in M['segments']} for s in XA.SIDES}
    for n, (par, kind, role, at, q) in E.items():
        o = obs.get(n)
        if o is None:
            continue
        if (o.parent.name if o.parent else None) != par:
            bad.append(f"{label}: {n} hängt an {o.parent.name if o.parent else '–'} statt {par or '–'}")
        if o.type != kind:
            bad.append(f'{label}: {n} ist {o.type} statt {kind}')
            continue
        sc = o.matrix_world.to_scale()
        if max(abs(c - 1.0) for c in sc) > 1e-4:
            bad.append(f'{label}: {n} hat Weltmaßstab {tuple(round(c, 5) for c in sc)} statt 1')
        if kind == 'MESH':
            mat = o.data.materials[0].name.split('.')[0] if o.data.materials else None
            if mat != role:
                bad.append(f'{label}: {n} trägt Material {mat} statt {role}')
            me = o.evaluated_get(dg).to_mesh()
            me.calc_loop_triangles()
            tri[n[0]][par[2:]] += len(me.loop_triangles)
            o.evaluated_get(dg).to_mesh_clear()
            d = max((a - b).length for a, b in zip(bbox(o, dg), REF[n][0])) * 1000
            if d > TOL_MM:
                bad.append(f'{label}: Netz {n} liegt {d:.3f} mm neben dem Bezug')
            su, ru = uvsig(o, dg), REF[n][1]
            if abs(su[0] - ru[0]) > 1e-6 + 1e-3 * ru[0] or max(abs(su[1] - ru[1]), abs(su[2] - ru[2])) > 2e-5:
                bad.append(f'{label}: UVs von {n} weichen vom Bezug ab (Fläche {su[0]:.3e}/{ru[0]:.3e})')
            texs = [nd.image.name for nd in (o.data.materials[0].node_tree.nodes if o.data.materials and o.data.materials[0].node_tree
                                             else []) if nd.type == 'TEX_IMAGE' and nd.image]
            if not texs:
                bad.append(f'{label}: {n} trägt keine Textur')
            continue
        d = (o.matrix_world.translation - Vector(at)).length * 1000
        if d > TOL_MM:
            bad.append(f'{label}: {n} liegt {d:.3f} mm neben der Ruhelage')
        ang = math.degrees(o.matrix_world.to_3x3().normalized().to_quaternion().rotation_difference(Quaternion(q)).angle)
        if ang > TOL_DEG:
            bad.append(f'{label}: {n} ist um {ang:.3f}° gegen die Ruhelage verdreht')
    for s in XA.SIDES:
        for g in M['segments']:
            if tri[s][g['id']] != g['triangles'][s]:
                bad.append(f"{label}: {s}_{g['id']} {tri[s][g['id']]} Dreiecke statt {g['triangles'][s]}")
    return bad


def load(kind):
    kit.reset_scene()
    path = os.path.join(XA.DST, f'arms.{kind}')
    if kind == 'glb':
        bpy.ops.import_scene.gltf(filepath=path)
    else:
        bpy.ops.import_scene.fbx(filepath=path)
    bpy.context.view_layer.update()


M = json.load(open(os.path.join(XA.DST, 'manifest.json'), encoding='utf-8'))
E = expected(M)
REF = reference()
bad = []
for kind in ('glb', 'fbx'):
    load(kind)
    bad += problems(E, M, REF, kind)
    imgs = {i.name for i in bpy.data.images if i.size[0]}
    if kind == 'glb' and len(imgs) != 3:                  # Grundfarbe, ORM, Normale eingebettet
        bad.append(f'glb: {len(imgs)} Texturen statt 3 ({sorted(imgs)})')
    if kind == 'fbx' and not any(os.path.basename(i.filepath) == 'arms_basecolor.png' for i in bpy.data.images if i.size[0]):
        bad.append('fbx: Grundfarbe-Textur (textures/arms_basecolor.png) nicht gefunden')
# Gegenprobe am zuletzt geladenen FBX: falscher Elternknoten, verschobene Hand, verdrehter Griffpunkt, verschobenes Netz
E2 = copy.deepcopy(E)
h = E['R_hand']
E2['R_hand'] = ('R_upper', h[1], h[2], [h[3][0], h[3][1] + 0.001, h[3][2]], h[4])
p = E['R_Socket_Palm']
E2['R_Socket_Palm'] = p[:4] + (list(Quaternion((1, 0, 0), math.radians(1.0)) @ Quaternion(p[4])),)
REF2 = dict(REF, R_palm=([c + Vector((0, 0, 0.001)) for c in REF['R_palm'][0]], REF['R_palm'][1]),
            R_back_plate=(REF['R_back_plate'][0], (REF['R_back_plate'][1][0], REF['R_back_plate'][1][1] + 0.001, REF['R_back_plate'][1][2])))
G = problems(E2, M, REF2, 'gegenprobe')
KEYS = ('R_hand hängt an', 'R_hand liegt', 'R_Socket_Palm ist um', 'Netz R_palm liegt', 'UVs von R_back_plate')
hit = [k for k in KEYS if any(k in b for b in G)]
bad += [f'Gegenprobe nicht erkannt: {k}' for k in KEYS if k not in hit]
# neu erzeugen: GLB bytegleich, Dreiecke wie im Manifest
tmp = tempfile.mkdtemp(prefix='ballon_arms_test_')
meas = XA.export_files(tmp)
same = open(os.path.join(tmp, 'arms.glb'), 'rb').read() == open(os.path.join(XA.DST, 'arms.glb'), 'rb').read()
if not same:
    bad.append(f"arms.glb neu erzeugt nicht bytegleich ({meas['glb']['bytes']} B, SHA {meas['glb']['sha256'][:12]} statt "
               f"{M['files']['glb']['sha256'][:12]}): Paket neu erzeugen")
ref = XA.measured_from(M)
for k, de in (('triangles', 'Dreiecke'), ('bounds', 'Netzmaße')):
    if meas[k] != ref[k]:
        bad.append(f'{de} beim Neuerzeugen weichen vom Manifest ab')
print(f"[test_arm_package] {len(E)} Knoten je Datei (GLB, FBX), {len(REF)} Netze und UV-Sätze gegen den Bezug, Gegenprobe {len(hit)}/{len(KEYS)}, "
      f"GLB {'bytegleich' if same else 'abweichend'}: Arm-Paket geprüft")
for b in bad[:20]:
    print('[test_arm_package] FEHLER', b)
sys.exit(1 if bad else 0)
