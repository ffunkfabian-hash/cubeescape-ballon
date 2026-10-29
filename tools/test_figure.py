"""Posensatz-Prüfung am Netz für Figuren (F3/F4/F6, BALLON 0.30 „Rulebook“; Vertrag basic/figures/__init__.py).

  /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P tools/test_figure.py     (ohne Szene, ~2 s; in ./check)

Je Figur: Teile starr an ihrem Knochen bauen, Grundhaltung und jede Pose aus POSES per Vorwärtskinematik stellen und je Teilpaar
verschiedener Knochen (ohne CONTACT_OK) prüfen: Durchdringung (BVH-Überlappung der Flächen oder ein Teil ganz im anderen) in jeder
Pose, Abstand ≥ rules.PLATE_GAP_MM in der Grundhaltung (kleinster Abstand der Eckpunkte zur Gegenfläche, in beide Richtungen; reicht
für Platten und Kästen, nicht für Kanten, die an einer Fläche ohne Eckpunkt vorbeistreifen). Budget (Dreiecke, Knochen) als Warnung.
Zuerst ein Selbsttest am Prüfkörper: die richtige Fassung muss grün sein, jede gezielt falsche Fassung (Fuge 0,5 mm, Arm schwenkt in
den Rumpf, Teil im Rumpf versteckt) rot. Ausgabe endet mit „Figuren geprüft“; bei Fehlern Zeilen mit „FEHLER“, Exit 1.
"""
import math
import os
import sys
import types

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools import rules  # noqa: E402

MM = 0.001


def piece_mesh(pc):
    """Netz eines Teils in Weltlage der Grundhaltung (m): 'box' (d, c) und 'hull' (pts) hier, sonst tools/ego_build.piece_mesh."""
    k, p = pc['kind'], pc['p']
    if k not in ('box', 'hull'):
        from tools import ego_build
        ob = ego_build.piece_mesh(pc['id'], k, p)
        bm = bmesh.new()
        bm.from_mesh(ob.data)
    else:
        bm = bmesh.new()
        if k == 'box':
            bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=Vector(p['d']) * MM, verts=bm.verts)
        else:
            for q in p['pts']:
                bm.verts.new(Vector(q) * MM)
            bmesh.ops.convex_hull(bm, input=bm.verts)
        if 'c' in p:
            bmesh.ops.translate(bm, vec=Vector(p['c']) * MM, verts=bm.verts)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    verts = [v.co.copy() for v in bm.verts]
    tris = [[v.index for v in f.verts] for f in bm.faces]
    bm.free()
    return verts, tris


def bone_mats(F, pose):
    """Weltmatrix je Knochen (Bewegung gegenüber der Grundhaltung): Eltern zuerst, Drehung um den eigenen Kopf in Weltachsen."""
    R = {}

    def get(b):
        if b in R:
            return R[b]
        B = F.BONES[b]
        par = get(B['parent']) if B.get('parent') else Matrix.Identity(4)
        h = Vector(B['head']) * MM
        rx, ry, rz = (math.radians(a) for a in pose.get(b, (0, 0, 0)))
        rot = (Matrix.Rotation(rz, 4, 'Z') @ Matrix.Rotation(ry, 4, 'Y') @ Matrix.Rotation(rx, 4, 'X'))
        hw = par @ h                                   # Kopf bewegt sich mit dem Elternknochen
        R[b] = Matrix.Translation(hw) @ (par.to_3x3().to_4x4() @ rot @ par.to_3x3().to_4x4().inverted()) @ \
            Matrix.Translation(-hw) @ par
        return R[b]
    for b in F.BONES:
        get(b)
    return R


def inside(tree, p):
    """Punkt p in der geschlossenen Fläche von tree (Normale am nächsten Punkt zeigt von p weg)."""
    loc, nrm, _, _ = tree.find_nearest(p)
    return loc is not None and (loc - p).dot(nrm) > 0


def check_figure(F):
    """(Fehler, Hinweise, Kennzahlen) einer Figur nach dem Vertrag."""
    err = list(rules.figure_meta_problems(F))
    pcs = F.pieces()
    for pc in pcs:
        if pc['bone'] not in F.BONES:
            err.append(f"{pc['id']}: Knochen {pc['bone']} fehlt in BONES")
    if err:
        return err, [], {}
    mesh = {pc['id']: piece_mesh(pc) for pc in pcs}
    bone = {pc['id']: pc['bone'] for pc in pcs}
    ok = set(getattr(F, 'CONTACT_OK', set()))
    pairs = [(a, b) for i, a in enumerate(mesh) for b in list(mesh)[i + 1:]
             if bone[a] != bone[b] and frozenset((bone[a], bone[b])) not in ok]
    for name, pose in [('rest', {})] + list(F.POSES.items()):
        M = bone_mats(F, pose)
        T, V = {}, {}
        for pid, (vs, ts) in mesh.items():
            V[pid] = [M[bone[pid]] @ v for v in vs]
            T[pid] = BVHTree.FromPolygons(V[pid], ts)
        for a, b in pairs:
            if T[a].overlap(T[b]) or inside(T[b], V[a][0]) or inside(T[a], V[b][0]):
                err.append(f'Pose {name}: {a} ({bone[a]}) durchdringt {b} ({bone[b]})')
            elif name == 'rest':
                gap = min(min((T[b].find_nearest(p)[3] for p in V[a]), default=1), min((T[a].find_nearest(p)[3] for p in V[b]), default=1))
                if gap < rules.PLATE_GAP_MM * MM:
                    err.append(f'Grundhaltung: Abstand {a} ↔ {b} {gap / MM:.2f} mm < {rules.PLATE_GAP_MM} mm (F3)')
    tris = sum(len(ts) for _, ts in mesh.values())
    stats = dict(triangles=tris, bones=len(F.BONES), poses=len(F.POSES), pairs=len(pairs))
    return err, rules.figure_budget_notes(F.META.get('id', '?'), tris, len(F.BONES)), stats


# ------------------------------------------------------------------ Prüfkörper
def probe(variant='ok'):
    """Prüfkörper aus Kästen: Becken, Rumpf, rechter Arm, rechtes Bein, je 10 mm Fuge. Varianten: 'ok', 'gap05' (Becken 0,5 mm unter
    dem Rumpf), 'swing' (Arm vor der Brust schwenkt 40° in den Rumpf), 'hidden' (Kasten des Arms steckt ganz im Rumpf)."""
    from basic.arms import robot_arm
    B = dict(pelvis=dict(parent=None, head=(0, 0, 900)), torso=dict(parent='pelvis', head=(0, 0, 1000)),
             arm_R=dict(parent='torso', head=(-210, 0, 1400)), leg_R=dict(parent='pelvis', head=(-100, 0, 900)))
    P = dict(arm_up={'arm_R': (0, 180, 0)}, arm_cross={'arm_R': (-90, 0, 0)}, deep_squat={'leg_R': (-100, 0, 0)},
             lunge={'leg_R': (-45, 0, 0)}, twist_l45={'torso': (0, 0, 45)}, twist_r45={'torso': (0, 0, -45)})
    pel_h = 100
    if variant == 'gap05':
        pel_h = 109.5                                   # Oberkante 999,5: 0,5 mm Fuge zum Rumpf
    if variant == 'swing':
        P['arm_cross'] = {'arm_R': (0, -40, 0)}         # Unterarmende schwenkt zur Mitte (x −40 mm): mitten im Rumpf
    pieces = [dict(id='torso_shell', bone='torso', kind='box', p=dict(d=(300, 200, 400), c=(0, 0, 1200))),
              dict(id='pelvis_block', bone='pelvis', kind='box', p=dict(d=(60, 180, pel_h), c=(0, 0, 890 + pel_h / 2))),
              dict(id='arm_shell', bone='arm_R', kind='box', p=dict(d=(80, 80, 500), c=(-210, 0, 1150))),
              dict(id='leg_shell', bone='leg_R', kind='box', p=dict(d=(120, 120, 860), c=(-100, 0, 450)))]
    if variant == 'hidden':
        pieces.append(dict(id='arm_implant', bone='arm_R', kind='box', p=dict(d=(20, 20, 20), c=(-100, 0, 1200))))
    return types.SimpleNamespace(__name__=f'probe_{variant}', META=dict(id=f'PROBE-{variant}', role='player', form='square_circle'),
                                 BONES=B, POSES=P, pieces=lambda: pieces, CONTACT_OK=set(), HAND=robot_arm,
                                 HEIGHT_MM=1600, HEAD_MM=1600 / 7.5)


def self_test():
    bad = []
    e, _, st = check_figure(probe('ok'))
    if e:
        bad.append('Prüfkörper ok meldet Fehler: ' + ' | '.join(e))
    for v, want in (('gap05', 'Abstand torso_shell ↔ pelvis_block'), ('swing', 'Pose arm_cross: torso_shell (torso) durchdringt arm_shell'),
                    ('hidden', 'Pose rest: torso_shell (torso) durchdringt arm_implant')):
        e, _, _ = check_figure(probe(v))
        if not any(want in x for x in e):
            bad.append(f'Prüfkörper {v} nicht erkannt (erwartet „{want}“): {e}')
    return bad, st


def main():
    bad, st = self_test()
    print(f"[test_figure] Selbsttest Prüfkörper: {st.get('pairs', 0)} Teilpaare × {st.get('poses', 0) + 1} Haltungen, "
          f"falsche Fassungen gap05/swing/hidden {'erkannt' if not bad else 'NICHT erkannt'}")
    n = 0
    for F in rules.figure_modules():
        e, notes, s = check_figure(F)
        n += 1
        bad += [f"{F.META.get('id')}: {x}" for x in e]
        for x in notes:
            print(f'[test_figure] {x}')
        print(f"[test_figure] {F.META.get('id')}: {s}")
    for b in bad:
        print(f'[test_figure] FEHLER {b}')
    print(f'[test_figure] {n} Figuren geprüft (Posensatz {", ".join(rules.POSES)})')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
