"""Arm-Paket `ballon-arms/1` (0.40 „Brace“): neu erzeugt = bytegleich, Reimport erhält Teile, Hierarchie, Anker und Ruhelage.

  blender -b --factory-startup -P tools/test_arm_package.py

1. arms.glb und arms.fbx aus packages/ego-arms/ einlesen: jeder erwartete Knoten (Wurzel, Segment, Teil, Anker je Seite) ist da, kein
   fremder; Eltern wie im Manifest; Wurzeln, Segmente und Anker sind Leerknoten, Teile Netze mit ihrer Rolle als Material; Dreiecke je
   Segment wie im Manifest; Weltlage der Wurzeln, Segmentursprünge und Anker wie manifest world_m (≤ TOL_MM).
2. Paket neu in einen Temp-Ordner erzeugen (tools/export_arms.export_files): arms.glb bytegleich, Dreiecke gleich dem Manifest.
Gegenprobe: eine Erwartung mit vertauschtem Elternknoten und um 1 mm verschobener Hand muss gemeldet werden.
"""
import copy
import json
import os
import sys
import tempfile

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic import kit  # noqa: E402
import tools.export_arms as XA  # noqa: E402

TOL_MM = 0.05


def expected(M):
    """{Knoten: (Eltern, Art, Rolle oder None, Weltlage m oder None)} für beide Seiten aus dem Manifest."""
    E = {}
    for s in XA.SIDES:
        E[f'{s}_arm'] = (None, 'EMPTY', None, M['rest_pose']['roots'][s]['at_m'])
        for g in M['segments']:
            E[f"{s}_{g['id']}"] = (f"{s}_{g['parent']}", 'EMPTY', None, g['rest'][s]['world_m'])
        for p in M['parts']:
            E[f"{s}_{p['id']}"] = (f"{s}_{p['segment']}", 'MESH', p['role'], None)
        for a in M['anchors']:
            E[a['node'][s]] = (f"{s}_{a['segment']}", 'EMPTY', None, a['world_m'][s])
    return E


def problems(E, M, label):
    bad = []
    obs = {o.name: o for o in bpy.data.objects}
    bad += [f'{label}: fehlt {n}' for n in E if n not in obs]
    bad += [f'{label}: fremder Knoten {n}' for n in obs if n not in E]
    dg = bpy.context.evaluated_depsgraph_get()
    tri = {s: {g['id']: 0 for g in M['segments']} for s in XA.SIDES}
    for n, (par, kind, role, at) in E.items():
        o = obs.get(n)
        if o is None:
            continue
        if (o.parent.name if o.parent else None) != par:
            bad.append(f"{label}: {n} hängt an {o.parent.name if o.parent else '–'} statt {par or '–'}")
        if o.type != kind:
            bad.append(f'{label}: {n} ist {o.type} statt {kind}')
        if role is not None and o.type == 'MESH':
            mat = o.data.materials[0].name.split('.')[0] if o.data.materials else None
            if mat != role:
                bad.append(f'{label}: {n} trägt Material {mat} statt {role}')
            me = o.evaluated_get(dg).to_mesh()
            me.calc_loop_triangles()
            tri[n[0]][par[2:]] += len(me.loop_triangles)
            o.evaluated_get(dg).to_mesh_clear()
        if at is not None:
            d = (o.matrix_world.translation - type(o.matrix_world.translation)(at)).length * 1000
            if d > TOL_MM:
                bad.append(f'{label}: {n} liegt {d:.3f} mm neben der Ruhelage')
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
bad = []
for kind in ('glb', 'fbx'):
    load(kind)
    bad += problems(E, M, kind)
# Gegenprobe: falscher Elternknoten und verschobene Hand müssen auffallen
E2 = copy.deepcopy(E)
E2['R_hand'] = ('R_upper', 'EMPTY', None, [E['R_hand'][3][0], E['R_hand'][3][1] + 0.001, E['R_hand'][3][2]])
G = problems(E2, M, 'gegenprobe')
if not any('R_hand hängt an' in b for b in G) or not any('R_hand liegt' in b for b in G):
    bad.append('Gegenprobe (Elternknoten, Lage) nicht erkannt')
# neu erzeugen: GLB bytegleich, Dreiecke wie im Manifest
tmp = tempfile.mkdtemp(prefix='ballon_arms_test_')
meas = XA.export_files(tmp)
same = open(os.path.join(tmp, 'arms.glb'), 'rb').read() == open(os.path.join(XA.DST, 'arms.glb'), 'rb').read()
if not same:
    bad.append(f"arms.glb neu erzeugt nicht bytegleich ({meas['glb']['bytes']} B, SHA {meas['glb']['sha256'][:12]} statt "
               f"{M['files']['glb']['sha256'][:12]}): Paket neu erzeugen")
if meas['triangles'] != XA.measured_from(M)['triangles']:
    bad.append('Dreiecke beim Neuerzeugen weichen vom Manifest ab')
n = len(E)
print(f"[test_arm_package] {n} Knoten je Datei (GLB, FBX), GLB {'bytegleich' if same else 'abweichend'}: Arm-Paket geprüft")
for b in bad[:20]:
    print('[test_arm_package] FEHLER', b)
sys.exit(1 if bad else 0)
