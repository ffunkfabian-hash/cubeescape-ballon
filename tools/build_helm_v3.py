"""Helm „Scout v3“ nach der Spezifikation des Nutzers (27.10.2026): Hard-Surface, weiße zylindrische Schale mit Kragen, dunkle Kappe
mit Krempe/Visierkante, facettierte dunkle Gesichtsmaske, runde Pods mit Bügel, Spiralkabel zur Rückbox, Antenne rechts.

  blender -b --factory-startup -P tools/build_helm_v3.py -- [--out DIR] [--phase1-only] [--reuse-phase1] [--samples N]

Maße in H (Helmhöhe = 0,30 m), +Z oben, −Y vorn, +X rechts vom Träger, Z = 0 Unterkante Schale/Kinnleiste, Z = 1 Kappenscheitel.
Zwei Phasen: Grundmassen → Silhouetten-IoU gegen ref_helm_v3.png (Stop-Kriterium, höchstens 8 Iterationen) → Details.
Ergebnis in DIR (Standard ~/Library/Caches/CubeEscapeBallon/out/helm_v3): helm_v3.blend, sil_*.png, check_*.png, compare_*.png,
iou.log, phase1.json, REPORT.md.
"""
import json
import math
import os
import subprocess
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

S = 0.30
ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []


def arg(name, default=None):
    return ARGS[ARGS.index(name) + 1] if name in ARGS else default


OUT = os.path.expanduser(arg('--out', '~/Library/Caches/CubeEscapeBallon/out/helm_v3'))
REF = os.path.expanduser(arg('--ref', '~/Library/Caches/CubeEscapeBallon/refs/robot-helm-v3.png'))
REFB = os.path.expanduser('~/Library/Caches/CubeEscapeBallon/refs/robot-helm-v3b.png')
BLEND = os.path.join(OUT, 'helm_v3.blend')
CAMS = (('cam_front', 0), ('cam_right', 90), ('cam_back', 180), ('cam_left', -90))
LOG, NOTES = [], []
DEVIATIONS = [
    'Beide Seiten direkt aus symmetrischen Funktionen gebaut statt Mirror-Modifier (Raycasts/Booleans brauchen beide Seiten); Paare in '
    'Abnahme 5 geprüft',
    'Referenzmaske: Helm = Pixel, deren Luminanz sich um mehr als 12/255 vom Hintergrund unterscheidet (heller oder dunkler); '
    '„dunkler als Hintergrund − 12“ hätte die weiße Schale ausgeschlossen',
    'Hüllbox (Abnahme 2) gemessen an den Grundmassen Schale, Kappe, Maske, Kinnleiste: die Pods reichen allein bis X ±0,45, die Bügel '
    'bis ±0,50, damit wäre 0,80 ± 0,02 nicht erreichbar',
    'Tuch-Oberkante an der Vorlage abgelesen (Zeilen 340/320/318/305 von 500), eigenes Render auf Z 0,155/0,19/0,22/0,23 '
    'abgeschnitten; Löcher der Referenzmaske vom Rand her gefüllt (graue Helmteile haben fast die Hintergrundfarbe)',
    'Phase-1-Anpassung im Toleranzband der Hüllbox (Breite 0,78–0,82, Scheitel 0,99–1,01); die IoU-Suche hätte die Schale sonst '
    'auf 0,84 Breite und 1,02 Höhe gezogen',
    'Maskenplatten und Kinnleiste eben trianguliert (triangle_fill), zweimal unterteilt und Punkt für Punkt auf die Schale projiziert '
    '(statt eines großen N-Gons: dessen lange Dreiecke knickten auf der Wölbung, die Platten wirkten durchsichtig)',
    'Dunkle Unterlage unter der Maske (Teil von Maske_Stirn): sonst schien die weiße Schale durch die 0,006-Fugen und an den '
    'schrägen Plattenrändern und ließ die Wangen wie leere Rahmen wirken',
    'Wangen-Nut Z 0,36 als Spalt zwischen zwei Platten statt Boolean (die Quaderkette erzeugte Non-Manifold-Kanten); Bevel der '
    'Maskenplatten ohne Harden Normals (Streifen auf den langen Dreiecken)',
    'Krempenüberstand an Seiten und Rücken geprüft; vorn ist die Krempe laut 4.2 um 0,025 verlängert (Visierkante)',
    'Referenzbild liegt in 2000 × 500 vor (Viertel 500 × 500 statt 720 × 720); Opening-Kern auf 6 px skaliert (9 × 500/720)',
]


def H(*c):
    return Vector(c) * S


# ------------------------------------------------------------------ Szene, Material, Hilfen

def srgb(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)


MATS = {'MAT_Dunkel': ('#26282B', 0.55, 0.10), 'MAT_Weiss': ('#D7D5CF', 0.65, 0.0), 'MAT_Pod': ('#5A574D', 0.60, 0.2),
        'MAT_Kabel': ('#1C1C1C', 0.45, 0.0), 'MAT_Metall': ('#6E6E6E', 0.30, 1.0)}


def mat(name):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    if name == 'MAT_Leucht':
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        out, em = nt.nodes.new('ShaderNodeOutputMaterial'), nt.nodes.new('ShaderNodeEmission')
        em.inputs['Color'].default_value = (*srgb('#7FE6E0'), 1)
        em.inputs['Strength'].default_value = 4.0
        nt.links.new(em.outputs[0], out.inputs['Surface'])
        m.diffuse_color = (*srgb('#7FE6E0'), 1)
        return m
    col, rough, metal = MATS[name]
    b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*srgb(col), 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    m.diffuse_color = (*srgb(col), 1)
    return m


def coll(name):
    return bpy.data.collections[name]


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system, sc.unit_settings.scale_length = 'METRIC', 1.0
    for n in ('HELM_V3', 'HILFE'):
        sc.collection.children.link(bpy.data.collections.new(n))


def obj(name, bm, mats, collection='HELM_V3', recalc=True):
    me = bpy.data.meshes.new(name)
    if recalc:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    ob = bpy.data.objects.new(name, me)
    coll(collection).objects.link(ob)
    for m in mats:
        ob.data.materials.append(mat(m))
    return ob


def ctx(ob):
    for o in list(bpy.context.view_layer.objects):
        if o is not None:
            o.select_set(False)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)


def apply_mod(ob, name):
    ctx(ob)
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        bpy.ops.object.modifier_apply(modifier=name)


def join(target, others):
    others = [o for o in others if o is not None]
    if not others:
        return target
    ctx(target)
    for o in others:
        o.select_set(True)
    with bpy.context.temp_override(active_object=target, selected_editable_objects=[target] + others, selected_objects=[target] + others):
        bpy.ops.object.join()
    return target


def boolean(ob, cutter):
    m = ob.modifiers.new('BOOL', 'BOOLEAN')
    m.operation, m.solver, m.object, m.use_self = 'DIFFERENCE', 'EXACT', cutter, True
    m.material_mode = 'INDEX'
    if len(ob.modifiers) > 1:                         # vor vorhandene Bevel-Modifier ziehen, damit nur der Schnitt angewendet wird
        ob.modifiers.move(len(ob.modifiers) - 1, 0)
    apply_mod(ob, m.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def bevel(ob, w=0.006, seg=2, harden=True):
    m = ob.modifiers.new('BEVEL', 'BEVEL')
    m.width, m.segments, m.limit_method, m.angle_limit, m.harden_normals = w * S, seg, 'ANGLE', math.radians(30), harden
    m.use_clamp_overlap = True


def smooth(ob, deg=35):
    ob.data.shade_smooth()
    ob.data.set_sharp_from_angle(angle=math.radians(deg))


def bvh(obs):
    obs = obs if isinstance(obs, (list, tuple)) else [obs]
    dg = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()
    for o in obs:
        e = o.evaluated_get(dg)
        me = e.to_mesh()
        b2 = bmesh.new()
        b2.from_mesh(me)
        b2.transform(o.matrix_world)
        tmp = bpy.data.meshes.new('tmp')
        b2.to_mesh(tmp)
        b2.free()
        bm.from_mesh(tmp)
        bpy.data.meshes.remove(tmp)
        e.to_mesh_clear()
    t = BVHTree.FromBMesh(bm)
    bm.free()
    return t


def save(step):
    os.makedirs(OUT, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print(f'[v3] {step} gespeichert', flush=True)


def frame_of(axis):
    a = Vector(axis).normalized()
    h = Vector((0, 0, 1)) if abs(a.z) < 0.9 else Vector((1, 0, 0))
    u = a.cross(h).normalized()
    return Matrix((a, u, a.cross(u))).transposed()


def lathe(bm, prof, M, origin, segs=40, mat_index=0):
    ax, u, w = M.col[0], M.col[1], M.col[2]
    rings = []
    for r, a in prof:
        if r <= 1e-9:
            rings.append([bm.verts.new(Vector(origin) + ax * a)])
        else:
            rings.append([bm.verts.new(Vector(origin) + ax * a + (u * math.cos(t) + w * math.sin(t)) * r)
                          for t in (2 * math.pi * k / segs for k in range(segs))])
    for A, B in zip(rings, rings[1:]):
        for k in range(segs):
            k2 = (k + 1) % segs
            if len(A) == 1 and len(B) == 1:
                continue
            f = bm.faces.new((A[0], B[k2], B[k]) if len(A) == 1 else (A[k], A[k2], B[0]) if len(B) == 1 else (A[k], A[k2], B[k2], B[k]))
            f.material_index = mat_index


def cyl(bm, r, length, center, axis, segs=32, mat_index=0):
    lathe(bm, [(0, -length / 2), (r, -length / 2), (r, length / 2), (0, length / 2)], frame_of(axis), center, segs, mat_index)


def add_box(bm, center, size, R=None):
    R = R or Matrix.Identity(3)
    for v in bmesh.ops.create_cube(bm, size=1.0)['verts']:
        v.co = R @ Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2])) + Vector(center)


def rounded_rect(w, h, r, n=3):
    pts = []
    for cu, cv, a0 in ((w / 2 - r, h / 2 - r, 0), (-(w / 2 - r), h / 2 - r, 90), (-(w / 2 - r), -(h / 2 - r), 180), (w / 2 - r, -(h / 2 - r), 270)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cu + r * math.cos(a), cv + r * math.sin(a)))
    return pts


def densify(poly, step=0.02):
    out = []
    for (u0, v0), (u1, v1) in zip(poly, poly[1:] + poly[:1]):
        n = max(1, int(math.hypot(u1 - u0, v1 - v0) / step))
        out += [(u0 + (u1 - u0) * k / n, v0 + (v1 - v0) * k / n) for k in range(n)]
    return out


def prism(bm, outline, origin, U, V, N, d0, d1):
    a = [bm.verts.new(Vector(origin) + U * u + V * v + N * d0) for u, v in outline]
    b = [bm.verts.new(Vector(origin) + U * u + V * v + N * d1) for u, v in outline]
    bm.faces.new(a[::-1])
    bm.faces.new(b)
    for k in range(len(a)):
        k2 = (k + 1) % len(a)
        bm.faces.new((a[k], a[k2], b[k2], b[k]))


def shell_plate(tree, outline_h, center, U, V, n_out, off_in, off_out, extra=None):
    """Platte auf der Schale: Umriss (u, v) in H, je Punkt Raycast entlang −n_out, Innen-/Außenseite im Abstand off_in/off_out (H);
    extra(u, v) → zusätzlicher Versatz nach außen (H, z. B. Dachknick). Rückgabe bmesh."""
    bm = bmesh.new()
    inner, outer = [], []
    for u, v in outline_h:
        p = Vector(center) + U * u * S + V * v * S
        loc, _, _, _ = tree.ray_cast(p + n_out * 0.6 * S, -n_out, 2.0)
        q = loc if loc is not None else p
        e = extra(u, v) if extra else 0.0
        inner.append(bm.verts.new(q + n_out * (off_in + e) * S))
        outer.append(bm.verts.new(q + n_out * (off_out + e) * S))
    bm.faces.new(inner[::-1])
    bm.faces.new(outer)
    for k in range(len(inner)):
        k2 = (k + 1) % len(inner)
        bm.faces.new((inner[k], inner[k2], outer[k2], outer[k]))
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    return bm


def plate_mesh(tree, outline_h, center, U, V, n_out, off_in, off_out, extra=None, sub=2):
    """Platte auf der Schale, sauber vernetzt: Umriss eben triangulieren (triangle_fill), zweimal unterteilen, jeden Punkt per Raycast
    entlang −n_out auf die Schale legen (Innenseite off_in + extra), dann Dicke nach außen bis off_out (bmesh.solidify)."""
    bm = bmesh.new()
    vs = [bm.verts.new((u, v, 0.0)) for u, v in outline_h]
    es = [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs))]
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=es, normal=(0, 0, 1))
    for _ in range(sub):
        bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=1, use_grid_fill=True)
    for v in bm.verts:
        u, w = v.co.x, v.co.y
        p = Vector(center) + U * u * S + V * w * S
        loc, _, _, _ = tree.ray_cast(p + n_out * 0.6 * S, -n_out, 2.0)
        q = loc if loc is not None else p
        v.co = q + n_out * (off_in + (extra(u, w) if extra else 0.0)) * S
    bm.normal_update()
    if sum(f.normal.dot(n_out) for f in bm.faces) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    bm.normal_update()
    bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=(off_out - off_in) * S)   # extrudiert entlang der Normalen (nach außen)
    return bm


def curve_obj(name, splines, r, mat_name, res=12, collection='HELM_V3'):
    """splines: Liste von ('BEZIER'|'POLY', Punkte)."""
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    for kind, pts in splines:
        sp = cu.splines.new(kind)
        if kind == 'BEZIER':
            sp.bezier_points.add(len(pts) - 1)
            for bp, p in zip(sp.bezier_points, pts):
                bp.co = p
                bp.handle_left_type = bp.handle_right_type = 'AUTO'
        else:
            sp.points.add(len(pts) - 1)
            for pp, p in zip(sp.points, pts):
                pp.co = (p.x, p.y, p.z, 1)
    cu.bevel_depth, cu.bevel_resolution, cu.resolution_u, cu.use_fill_caps = r, 4, res, True
    ob = bpy.data.objects.new(name, cu)
    coll(collection).objects.link(ob)
    ob.data.materials.append(mat(mat_name))
    return ob


def eval_points(ob):
    cu = ob.data
    keep = cu.bevel_depth
    cu.bevel_depth = 0.0
    bpy.context.view_layer.update()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    pts = [v.co.copy() for v in me.vertices]
    bpy.data.meshes.remove(me)
    cu.bevel_depth = keep
    bpy.context.view_layer.update()
    return pts


# ------------------------------------------------------------------ 3 Schale

SHELL = [  # Z, a, b_v, b_h, n_v, n_h
    (0.00, 0.33, 0.38, 0.46, 3.0, 2.2), (0.30, 0.34, 0.39, 0.47, 3.0, 2.2), (0.31, 0.37, 0.44, 0.52, 3.0, 2.2),
    (0.55, 0.38, 0.46, 0.54, 3.0, 2.2), (0.72, 0.38, 0.45, 0.53, 2.8, 2.2), (0.80, 0.36, 0.42, 0.50, 2.6, 2.2)]
K = dict(a=1.0, bv=1.0, bh=1.0, cap_c=0.28)      # Phase-1-Anpassung (Faktoren auf a, b_v, b_h; Kuppelhöhe)


def shell_row(z):
    T = [(r[0], r[1] * K['a'], r[2] * K['bv'], r[3] * K['bh'], r[4], r[5]) for r in SHELL]
    for r0, r1 in zip(T, T[1:]):
        if r0[0] <= z <= r1[0]:
            u = (z - r0[0]) / (r1[0] - r0[0])
            return tuple(r0[i] + (r1[i] - r0[i]) * u for i in range(6))
    return T[0] if z < T[0][0] else T[-1]


def ring(row, n=64, grow=0.0):
    z, a, bv, bh, nv, nh = row
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        c, s = math.cos(t), math.sin(t)
        nn, b = (nv, bv) if s >= 0 else (nh, bh)
        x = (a + grow) * abs(c) ** (2 / nn) * math.copysign(1, c)
        y = -(b + grow) * abs(s) ** (2 / nn) if s >= 0 else (b + grow) * abs(s) ** (2 / nn)
        pts.append((x, y, z))
    return pts


def section_3():
    zs = [0.0, 0.10, 0.20, 0.28, 0.30, 0.31, 0.33, 0.40, 0.48, 0.55, 0.62, 0.68, 0.72, 0.76, 0.80]
    bm = bmesh.new()
    rings = [[bm.verts.new(H(*p)) for p in ring(shell_row(z))] for z in zs]
    for A, B in zip(rings, rings[1:]):
        for k in range(64):
            bm.faces.new((A[k], A[(k + 1) % 64], B[(k + 1) % 64], B[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    if sum(f.normal.dot(f.calc_center_median() - H(0, 0, f.calc_center_median().z / S)) for f in bm.faces) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    ob = obj('Schale', bm, ['MAT_Weiss'], recalc=False)
    so = ob.modifiers.new('SOLID', 'SOLIDIFY')
    so.thickness, so.offset, so.use_rim = 0.015 * S, -1.0, True
    apply_mod(ob, so.name)
    smooth(ob, 30)
    return ob


# ------------------------------------------------------------------ 4 Kappe

def section_4(with_lugs=False):
    a, b, c, yc, zc = 0.40 * K['a'], 0.52, K['cap_c'], 0.02, 0.72
    bm = bmesh.new()
    zs = [0.76 + (zc + c - 0.76) * k / 14 for k in range(14)]
    rings = []
    for z in zs:
        s = math.sqrt(max(0.0, 1 - ((z - zc) / c) ** 2))
        row = (z, a * s, b * s, b * s, 3.2, 2.0)      # vorn fast gerade Stirnfläche (n 3,2), hinten rund
        rings.append([bm.verts.new(H(x, y + yc, zz)) for x, y, zz in ring(row, 48)])
    for A, B in zip(rings, rings[1:]):
        for k in range(48):
            bm.faces.new((A[k], A[(k + 1) % 48], B[(k + 1) % 48], B[k]))
    pole = bm.verts.new(H(0, yc, zc + c))
    for k in range(48):
        bm.faces.new((rings[-1][k], rings[-1][(k + 1) % 48], pole))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    if sum(f.normal.dot(f.calc_center_median() - H(0, yc, zc)) for f in bm.faces) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    cap = obj('Kappe', bm, ['MAT_Dunkel'], recalc=False)
    sd = cap.modifiers.new('SUB', 'SUBSURF')
    sd.levels = 2
    apply_mod(cap, sd.name)
    so = cap.modifiers.new('SOLID', 'SOLIDIFY')
    so.thickness, so.offset, so.use_rim = 0.015 * S, -1.0, True
    apply_mod(cap, so.name)
    smooth(cap, 40)
    # Krempe: Band 0,06 hoch (Z 0,70–0,76), 0,02 über der Schale; vorn 0,025 länger und vorn unten bei Z 0,69 (Schirm); hinten
    # Z 0,72–0,84 (dunkler „Hut“ über der weißen Schale)
    n = 64
    bm = bmesh.new()
    loops = []
    for zb_, zt_, g in ((None, None, 0.0), (None, None, 0.02), (None, None, 0.02), (None, None, 0.0)):
        loops.append([])
    base = ring(shell_row(0.73), n)
    for k, (x, y, _) in enumerate(base):
        front = y < -0.28 and abs(x) < 0.36
        back = y > 0.30
        zb = 0.69 if front else (0.72 if back else 0.70)
        zt = 0.84 if back else 0.76
        L = math.hypot(x, y) or 1.0
        nx, ny = x / L, y / L
        out = 0.02 + (0.025 if front else 0.0)
        pts = [(x, y, zb), (x + nx * out, y + ny * out, zb), (x + nx * out, y + ny * out, zt), (x, y, zt)]
        for i, p in enumerate(pts):
            loops[i].append(bm.verts.new(H(*p)))
    for A, B in zip(loops, loops[1:] + loops[:1]):
        for k in range(n):
            bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]))
    kr = obj('KREMPE', bm, ['MAT_Dunkel'])
    join(cap, [kr])
    bevel(cap, 0.003)
    if with_lugs:
        t = bvh(cap)
        for side, sx in (('L', -1), ('R', 1)):
            loc, _, _, _ = t.ray_cast(H(sx * 0.20, -0.05, 1.3), Vector((0, 0, -1)), 2.0)
            bm = bmesh.new()
            add_box(bm, loc + H(0, 0, 0.008), H(0.04, 0.03, 0.02))
            lug = obj(f'Lug_{side}', bm, ['MAT_Pod'])
            bevel(lug, 0.003)
    return cap


# ------------------------------------------------------------------ 5/6 Maske und Kinnleiste

def nh(z):
    """Halbe Breite des Nasenmoduls (oben 0,06 bei Z 0,46, unten 0,11 bei Z 0,20)."""
    return 0.06 + 0.05 * (0.46 - min(max(z, 0.20), 0.46)) / 0.26


def ridge(u, v):
    """Dachknick 6°: X = 0 vorderste Linie, nach außen um |x|·tan 6° zurück (bezogen auf die Stirnbreite 0,36)."""
    return (0.36 - min(abs(u), 0.36)) * math.tan(math.radians(6)) * 0.5


STIRN = [(-0.36, 0.70), (0.36, 0.70), (0.32, 0.46), (0.07, 0.46), (0.0, 0.40), (-0.07, 0.46), (-0.32, 0.46)]
MASK_ALL = [(-0.36, 0.70), (0.36, 0.70), (0.33, 0.46), (0.27, 0.22), (0.11, 0.20), (-0.11, 0.20), (-0.27, 0.22), (-0.33, 0.46)]


def front_plate(tree, name, poly, off_in, off_out, mats, step=0.02, ridged=True):
    bm = plate_mesh(tree, densify(poly, 0.03), H(0, -0.8, 0), Vector((1, 0, 0)), Vector((0, 0, 1)), Vector((0, -1, 0)), off_in, off_out,
                    ridge if ridged else None)
    ob = obj(name, bm, mats)
    smooth(ob, 30)                                     # glatt mit harten Kanten ab 30° (flach schattiert gab Streifen auf den Dreiecken)
    return ob


def kinnleiste(tree):
    poly = [(-0.30, 0.06), (0.30, 0.06), (0.34, 0.10), (0.34, 0.20), (-0.34, 0.20), (-0.34, 0.10)]     # Ecken Fase 0,04
    kl = front_plate(tree, 'Kinnleiste', poly, 0.010, 0.025, ['MAT_Weiss'], ridged=False)
    parts = [obj('LIPPE', plate_mesh(tree, densify([(-0.28, 0.06), (0.28, 0.06), (0.28, 0.08), (-0.28, 0.08)], 0.04), H(0, -0.8, 0),
                                      Vector((1, 0, 0)), Vector((0, 0, 1)), Vector((0, -1, 0)), 0.020, 0.040), ['MAT_Weiss'])]
    for sx in (-1, 1):                                 # seitlicher Steg bis Y +0,05, Höhe 0,06
        parts.append(obj(f'STEG_{sx}', plate_mesh(tree, densify([(-0.30, 0.06), (0.05, 0.06), (0.05, 0.12), (-0.30, 0.12)], 0.04),
                                             H(sx * 0.8, 0, 0), Vector((0, 1, 0)), Vector((0, 0, 1)), Vector((sx, 0, 0)), 0.010, 0.025),
                         ['MAT_Weiss']))
    join(kl, parts)
    bevel(kl, 0.004)
    return kl


def phase1_masses():
    for n in [o.name for o in coll('HELM_V3').objects]:
        bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)
    sh = section_3()
    section_4()
    tree = bvh(sh)
    m = front_plate(tree, 'MASKE_P1', MASK_ALL, 0.008, 0.020, ['MAT_Dunkel'])
    kinnleiste(tree)
    return sh


# ------------------------------------------------------------------ 13 Silhouetten und IoU

def camera_rig():
    sc = bpy.context.scene
    target = H(0, 0, 0.50)
    cams = {}
    for name, az in CAMS:
        cam = bpy.data.objects.get(name) or bpy.data.objects.new(name, bpy.data.cameras.new(name))
        if cam.name not in sc.collection.objects:
            sc.collection.objects.link(cam)
        cam.data.lens = 85
        a = math.radians(az)
        cam.location = target + H(math.sin(a), -math.cos(a), 0) * 3.2
        cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
        cams[name] = cam
    return cams


def render_sil(tag, res=256):
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE'
    sc.eevee.taa_render_samples = 1
    sc.render.film_transparent = True
    sc.render.resolution_x = sc.render.resolution_y = res
    out = {}
    for name, cam in camera_rig().items():
        sc.camera = cam
        sc.render.filepath = os.path.join(OUT, f'{tag}_{name}.png')
        bpy.ops.render.render(write_still=True)
        out[name] = sc.render.filepath
    return out


def load_rgba(path):
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    a = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[::-1]
    bpy.data.images.remove(img)
    return a


def box_sum(m, k):
    p = k // 2
    c = np.pad(m.astype(np.int32), p).cumsum(0).cumsum(1)
    c = np.pad(c, ((1, 0), (1, 0)))
    return c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]


def opening(m, k):
    er = box_sum(m, k) == k * k
    return box_sum(er, k) > 0


REFM = {}
# Tuch-Oberkante je Ansicht an der Vorlage abgelesen (Zeile von 500; die 0,85-Breitenregel greift erst bei 398–484, weil das Tuch
# schmaler ist) und die Helmhöhe, auf der das eigene Render gleich abgeschnitten wird (geschätzt aus Kappenscheitel/Kinnleiste)
REF_CUT = {'cam_front': 340, 'cam_right': 320, 'cam_back': 318, 'cam_left': 305}
Z_CUT = {'cam_front': 0.155, 'cam_right': 0.19, 'cam_back': 0.22, 'cam_left': 0.23}


def fill_holes(m):
    """Alles, was nicht vom Bildrand aus durch Hintergrund erreichbar ist, zählt zum Helm (graue Helmteile ≈ Hintergrundfarbe)."""
    free = ~m
    bg = np.zeros_like(m)
    bg[0, :], bg[-1, :], bg[:, 0], bg[:, -1] = free[0, :], free[-1, :], free[:, 0], free[:, -1]
    while True:
        nb = bg.copy()
        nb[1:] |= bg[:-1]
        nb[:-1] |= bg[1:]
        nb[:, 1:] |= bg[:, :-1]
        nb[:, :-1] |= bg[:, 1:]
        nb &= free
        if (nb == bg).all():
            return ~bg
        bg = nb


def ref_masks(open_k):
    key = open_k
    if key in REFM:
        return REFM[key]
    a = load_rgba(REF)
    h, w, _ = a.shape
    q = w // 4
    res = {}
    for i, (name, _) in enumerate(CAMS):
        p = a[:, i * q:(i + 1) * q, :3]
        lum = p @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        bg = np.median(lum[:20])
        m = np.abs(lum - bg) > 12 / 255
        m[:3], m[-3:], m[:, :3], m[:, -3:] = False, False, False, False
        rows = np.where(m.sum(axis=1) > 0.85 * q)[0]
        cut = min(rows[0] if len(rows) else h, int(round(REF_CUT[name] / 500 * h)))
        m[cut:] = False
        m = fill_holes(m)
        if open_k:
            m = opening(m, open_k)
        res[name] = m
        if open_k and not any(f'Tuch-Oberkante {name}' in n_ for n_ in NOTES):
            NOTES.append(f'Tuch-Oberkante {name}: Zeile {cut} von {h}')
    REFM[key] = res
    return res


def norm_mask(m, H_=180, W_=360):
    ys, xs = np.nonzero(m)
    if len(ys) == 0:
        return np.zeros((H_, W_), bool)
    m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = m.shape
    s = H_ / h
    nw = max(1, int(round(w * s)))
    r = m[np.minimum((np.arange(H_) / s).astype(int), h - 1)][:, np.minimum((np.arange(nw) / s).astype(int), w - 1)]
    out = np.zeros((H_, W_), bool)
    off = int(round(W_ / 2 - np.nonzero(r)[1].mean()))
    x0, x1 = max(0, off), min(W_, off + nw)
    out[:, x0:x1] = r[:, x0 - off:x1 - off]
    return out


def iou_all(tag='sil', open_k=6):
    paths = render_sil(tag)
    R = ref_masks(open_k)
    res = {}
    from bpy_extras.object_utils import world_to_camera_view
    cams = camera_rig()
    for name, _ in CAMS:
        m = load_rgba(paths[name])[:, :, 3] > 0.5
        row = int(round((1 - world_to_camera_view(bpy.context.scene, cams[name], H(0, 0, Z_CUT[name])).y) * m.shape[0]))
        m[max(0, row):] = False
        A, B = norm_mask(m), norm_mask(R[name])
        res[name] = float((A & B).sum() / max((A | B).sum(), 1))
    return res


def passed(r):
    return min(r['cam_front'], r['cam_back']) >= 0.90 and min(r['cam_left'], r['cam_right']) >= 0.88


def score(r):
    return sum(r.values())


def phase1():
    phase1_masses()
    r = iou_all()
    LOG.append(('Start', dict(K), r))
    print('[v3] IoU Start', {k: round(v, 3) for k, v in r.items()}, flush=True)
    step = {'a': 0.02, 'bv': 0.02, 'bh': 0.02, 'cap_c': 0.02}
    it = 0
    while not passed(r) and it < 8:
        it += 1
        best = None
        for key in step:
            for sgn in (1, -1):
                K[key] += sgn * step[key]
                if not (0.78 <= 2 * (0.38 * K['a'] + 0.02) <= 0.82 and 0.99 <= 0.72 + K['cap_c'] <= 1.01):
                    K[key] -= sgn * step[key]                  # Abnahme 2: Breite und Scheitel bleiben im Toleranzband
                    continue
                phase1_masses()
                rr = iou_all()
                if best is None or score(rr) > score(best[2]):
                    best = (key, sgn, rr)
                K[key] -= sgn * step[key]
        key, sgn, rr = best
        if score(rr) > score(r):
            K[key] += sgn * step[key]
            r = rr
            LOG.append((f'Iteration {it}: {key} {"+" if sgn > 0 else "−"}{step[key]:.3f}', dict(K), r))
        else:
            for k in step:
                step[k] /= 2
            LOG.append((f'Iteration {it}: keine Verbesserung, Schritte halbiert', dict(K), r))
        print('[v3]', LOG[-1][0], {k: round(v, 3) for k, v in r.items()}, flush=True)
    phase1_masses()
    r = iou_all()
    json.dump(dict(K=K, LOG=LOG, NOTES=NOTES), open(os.path.join(OUT, 'phase1.json'), 'w'))
    save('Phase 1')
    return r


# ------------------------------------------------------------------ Phase 2

def groove_path(tree, pts_h, inward, width=0.006, depth=0.003):
    """Nut als Kette dünner Quader entlang projizierter Punkte (Raycast entlang inward)."""
    P, N = [], []
    for p, d in zip(pts_h, inward):
        d = Vector(d).normalized()
        loc, nor, _, _ = tree.ray_cast(H(*p) - d * 0.6 * S, d, 2.0)
        if loc is not None:
            P.append(loc)
            N.append(nor)
    bm = bmesh.new()
    for (p, n), (q, m) in zip(zip(P, N), zip(P[1:], N[1:])):
        dd = q - p
        L = dd.length
        if L < 1e-6:
            continue
        t = dd / L
        nn = ((n + m) / 2)
        nn = (nn - t * nn.dot(t)).normalized()
        add_box(bm, (p + q) / 2, (L + width * S, width * S, 2 * depth * S), Matrix((t, t.cross(nn), nn)).transposed())
    return bm


def section_3_2(sh):
    tree = bvh(sh)
    bm = bmesh.new()
    cut = bmesh.new()

    def merge(b):
        me = bpy.data.meshes.new('t')
        b.to_mesh(me)
        b.free()
        cut.from_mesh(me)
        bpy.data.meshes.remove(me)
    # 1 Nut rundum bei Z 0,28
    pts = [(x * 1.2, y * 1.2, 0.28) for x, y, _ in ring(shell_row(0.28), 64)] + [(lambda p: (p[0] * 1.2, p[1] * 1.2, 0.28))(ring(shell_row(0.28), 64)[0])]
    merge(groove_path(tree, pts, [(-x, -y, 0) for x, y, _ in pts]))
    # 2 hinten mittig senkrecht Z 0,31–0,72
    pts = [(0, 1.0, 0.31 + 0.41 * k / 10) for k in range(11)]
    merge(groove_path(tree, pts, [(0, -1, 0)] * len(pts)))
    # 3 L-Nut je Seite
    for sx in (-1, 1):
        pts = [(sx * 1.0, 0.10, 0.70 - 0.30 * k / 8) for k in range(9)] + [(sx * 1.0, 0.10 + 0.30 * k / 8, 0.40) for k in range(1, 9)]
        merge(groove_path(tree, pts, [(-sx, 0, 0)] * len(pts)))
    # 5 hintere Fenster 0,05 × 0,04, 0,004 tief
    for sx in (-1, 1):
        d = Vector((-sx * 0.30, -0.42, 0)).normalized()
        loc, nor, _, _ = tree.ray_cast(H(sx * 0.30, 0.42, 0.45) - d * 0.6 * S, d, 2.0)
        b = bmesh.new()
        M = frame_of(nor)
        prism(b, [(u * S, v * S) for u, v in rounded_rect(0.05, 0.04, 0.004, 2)], loc, (M.col[1] if abs(M.col[1].z) < 0.5 else M.col[2]),
              Vector((0, 0, 1)), Vector(nor), -0.004 * S, 0.01 * S)
        merge(b)
    c = obj('CUT_SCHALE', cut, ['MAT_Weiss'], 'HILFE')
    boolean(sh, c)
    # 4 Leder-Panel je Seite 0,003 erhaben mit Schlitz
    panels = []
    for sx in (-1, 1):
        b = shell_plate(tree, densify(rounded_rect(0.20, 0.08, 0.01, 2), 0.02), H(sx * 0.8, -0.05, 0.36), Vector((0, 1, 0)),
                        Vector((0, 0, 1)), Vector((sx, 0, 0)), -0.002, 0.003)
        p = obj(f'PANEL_{sx}', b, ['MAT_Weiss'])
        t2 = bvh(p)
        loc, nor, _, _ = t2.ray_cast(H(sx * 1.0, -0.05, 0.36), Vector((-sx, 0, 0)), 2.0)
        b2 = bmesh.new()
        prism(b2, [(u * S, v * S) for u, v in rounded_rect(0.10, 0.015, 0.004, 2)], loc, Vector((0, 1, 0)), Vector((0, 0, 1)), Vector(nor),
              -0.004 * S, 0.01 * S)
        boolean(p, obj('CUT_P', b2, ['MAT_Weiss'], 'HILFE'))
        panels.append(p)
    join(sh, panels)
    bevel(sh, 0.004)
    spots = [(H(sx * 0.22, 1.0, z), (0, 1, 0)) for sx in (-1, 1) for z in (0.75, 0.45)] + [(H(sx * 0.10, 1.0, 0.32), (0, 1, 0)) for sx in (-1, 1)]
    return spots


def section_5(sh):
    tree = bvh(sh)
    st = front_plate(tree, 'Maske_Stirn', STIRN, 0.008, 0.020, ['MAT_Dunkel'], 0.015)
    eyes_cut = bmesh.new()
    t2 = bvh(st)
    eyes = []
    for side, sx in (('L', -1), ('R', 1)):
        xi, xo = 0.11, 0.27
        poly = [(xi, 0.555), (xo, 0.56), (xo, 0.625), (xi, 0.605)]
        poly = [(sx * x, z) for x, z in poly]
        if sx < 0:
            poly = poly[::-1]
        # Schlitz entlang −Y durch die Stirnplatte (0,008 tief), Einlage 0,002 unter der Oberfläche
        surf = [t2.ray_cast(H(x, -1.0, z), Vector((0, 1, 0)), 2.0)[0] for x, z in poly]
        bmc = bmesh.new()
        a = [bmc.verts.new(p + Vector((0, -0.02 * S, 0))) for p in surf]
        b = [bmc.verts.new(p + Vector((0, 0.008 * S, 0))) for p in surf]
        bmc.faces.new(a[::-1])
        bmc.faces.new(b)
        for k in range(4):
            bmc.faces.new((a[k], a[(k + 1) % 4], b[(k + 1) % 4], b[k]))
        boolean(st, obj('CUT_AUGE', bmc, ['MAT_Dunkel'], 'HILFE'))
        bme = bmesh.new()
        a = [bme.verts.new(p + Vector((0, 0.002 * S, 0))) for p in surf]
        b = [bme.verts.new(p + Vector((0, 0.009 * S, 0))) for p in surf]
        bme.faces.new(a[::-1])
        bme.faces.new(b)
        for k in range(4):
            bme.faces.new((a[k], a[(k + 1) % 4], b[(k + 1) % 4], b[k]))
        eyes.append(obj(f'Auge_{side}', bme, ['MAT_Leucht']))
    bevel(st, harden=False)
    spots = []
    t2 = bvh(st)
    for sx in (-1, 1):
        loc, nor, _, _ = t2.ray_cast(H(sx * 0.30, -1.0, 0.52), Vector((0, 1, 0)), 2.0)
        spots.append((loc, nor))
    # Wangen
    for side, sx in (('L', -1), ('R', 1)):
        poly = [(nh(0.454) + 0.006, 0.454), (0.33, 0.454), (0.27, 0.22), (nh(0.22) + 0.006, 0.22)]
        poly = [(sx * x, z) for x, z in poly]
        if sx < 0:
            poly = poly[::-1]
        def xo(z):
            return 0.27 + 0.06 * (z - 0.22) / 0.234
        up = [(nh(0.454) + 0.006, 0.454), (0.33, 0.454), (xo(0.363), 0.363), (nh(0.363) + 0.006, 0.363)]
        lo = [(nh(0.357) + 0.006, 0.357), (xo(0.357), 0.357), (0.27, 0.22), (nh(0.22) + 0.006, 0.22)]
        parts_ = []
        for nm_, poly in (('o', up), ('u', lo)):        # Panel-Nut Z 0,36 als Spalt 0,006 zwischen zwei Platten
            poly = [(sx * x, z) for x, z in poly]
            if sx < 0:
                poly = poly[::-1]
            parts_.append(front_plate(tree, f'W_{side}_{nm_}', poly, 0.008, 0.020, ['MAT_Dunkel'], 0.015, ridged=False))
        w = join(parts_[0], parts_[1:])
        w.name = f'Maske_Wange_{side}'
        tw = bvh(w)
        cut = bmesh.new()
        loc, nor, _, _ = tw.ray_cast(H(sx * 0.24, -1.0, 0.42), Vector((0, 1, 0)), 2.0)
        add_box(cut, loc, H(0.04, 0.008, 0.02))           # Fenster 0,04 × 0,02, 0,004 tief
        boolean(w, obj('CUT_W', cut, ['MAT_Dunkel'], 'HILFE'))
        bevel(w, harden=False)
        loc, nor, _, _ = tw.ray_cast(H(sx * 0.27, -1.0, 0.30), Vector((0, 1, 0)), 2.0)
        spots.append((loc, nor))
    # Nase: 0,010 vor den Wangen, Lüftungsschlitz, Mittelnut
    nose = front_plate(tree, 'Maske_Nase', [(-0.06, 0.46), (-0.11, 0.20), (0.11, 0.20), (0.06, 0.46)][::-1], 0.018, 0.030, ['MAT_Dunkel'],
                       0.015, ridged=False)
    tn = bvh(nose)
    cut = bmesh.new()
    loc, _, _, _ = tn.ray_cast(H(0, -1.0, 0.42), Vector((0, 1, 0)), 2.0)
    add_box(cut, loc, H(0.06, 0.012, 0.025))
    loc, _, _, _ = tn.ray_cast(H(0, -1.0, 0.31), Vector((0, 1, 0)), 2.0)
    add_box(cut, loc, H(0.004, 0.004, 0.14))           # Mittelnut Z 0,24–0,38 als ein Quader
    boolean(nose, obj('CUT_N', cut, ['MAT_Dunkel'], 'HILFE'))
    bevel(nose, harden=False)
    # dunkle Unterlage im Umriss der ganzen Maske, 0,002–0,007 vor der Schale: die Fugen zwischen Stirn, Wangen und Nase zeigen dunkel
    # statt der weißen Schale (Referenz: Maske als geschlossenes dunkles Teil mit Panel-Linien); Teil von Maske_Stirn
    under = front_plate(tree, 'UNTERLAGE', [(x * 0.99, z) for x, z in MASK_ALL[:2]] + [(0.325, 0.46), (0.27, 0.225), (0.11, 0.205),
                                                                                        (-0.11, 0.205), (-0.27, 0.225), (-0.325, 0.46)],
                        0.002, 0.007, ['MAT_Dunkel'], ridged=False)
    st = bpy.data.objects['Maske_Stirn']
    join(st, [under])
    save('5')
    return spots


def section_6_2(kl):
    tree = bvh(kl)
    loc, _, _, _ = tree.ray_cast(H(0, -1.0, 0.13), Vector((0, 1, 0)), 2.0)
    cut = bmesh.new()
    add_box(cut, loc, H(0.20, 0.008, 0.10))
    boolean(kl, obj('CUT_KP', cut, ['MAT_Weiss'], 'HILFE'))
    b = bmesh.new()
    add_box(b, loc + H(0, 0.004, 0), H(0.198, 0.004, 0.098))
    kp = obj('Kinn_Panel', b, ['MAT_Weiss'])
    t2 = bvh(kp)
    cut = bmesh.new()
    for dz in (-0.032, 0.0, 0.032):
        l2, _, _, _ = t2.ray_cast(H(0, -1.0, 0.13 + dz), Vector((0, 1, 0)), 2.0)
        add_box(cut, l2, H(0.12, 0.012, 0.012))
    boolean(kp, obj('CUT_KS', cut, ['MAT_Weiss'], 'HILFE'))
    bevel(kp, 0.002)
    NOTES.append('6.2 Kinn_Panel mit einem Material (MAT_Weiss), da Abnahme 7 genau ein Material je Objekt verlangt; der Schlitzboden '
                 'wirkt durch die Tiefe dunkel')


POD_C = (0.41, -0.04, 0.55)


def section_7(sh):
    tree = bvh(sh)
    spots = []
    for side, sx in (('L', -1), ('R', 1)):
        # Halteplatte 0,16 × 0,20 (Y × Z), R 0,02, Dicke 0,012, auf der Schale
        b = shell_plate(tree, densify(rounded_rect(0.16, 0.20, 0.02, 3), 0.02), H(sx * 0.8, POD_C[1], POD_C[2]), Vector((0, 1, 0)),
                        Vector((0, 0, 1)), Vector((sx, 0, 0)), 0.0, 0.012)
        pod = obj(f'Pod_{side}', b, ['MAT_Pod'])
        x0 = max(v.co.x * sx for v in pod.data.vertices) / S
        # Kapsel: Ellipsoid-Hälfte 0,10 (Y) × 0,125 (Z) × 0,06 (X), Rand-Fillet, Subdivision 2
        bm = bmesh.new()
        rings = []
        for k in range(8):
            th = math.pi / 2 * k / 8
            r, h = math.cos(th), math.sin(th)
            rings.append([bm.verts.new(H(sx * (x0 - 0.003 + 0.06 * h), POD_C[1] + 0.10 * r * math.cos(t), POD_C[2] + 0.125 * r * math.sin(t)))
                          for t in (2 * math.pi * j / 40 for j in range(40))])
        for A, B in zip(rings, rings[1:]):
            for j in range(40):
                bm.faces.new((A[j], A[(j + 1) % 40], B[(j + 1) % 40], B[j]))
        bm.faces.new(rings[0])
        pole = bm.verts.new(H(sx * (x0 - 0.003 + 0.06), POD_C[1], POD_C[2]))
        for j in range(40):
            bm.faces.new((rings[-1][j], rings[-1][(j + 1) % 40], pole))
        cap = obj('KAPSEL', bm, ['MAT_Pod'])
        sd = cap.modifiers.new('SUB', 'SUBSURF')
        sd.levels = 2
        apply_mod(cap, sd.name)
        smooth(cap, 50)
        tc = bvh(cap)
        extra = []
        # Taste Ø 0,03 (0,004 erhaben) bei Pod-Mitte +0,02 in Y; dreieckige Vertiefung 0,04 × 0,03 darunter
        loc, nor, _, _ = tc.ray_cast(H(sx * 1.0, POD_C[1] + 0.02, POD_C[2]), Vector((-sx, 0, 0)), 2.0)
        b = bmesh.new()
        cyl(b, 0.015 * S, 0.008 * S, loc, nor, 24)
        extra.append(obj('TASTE', b, ['MAT_Pod']))
        loc, nor, _, _ = tc.ray_cast(H(sx * 1.0, POD_C[1] + 0.02, POD_C[2] - 0.06), Vector((-sx, 0, 0)), 2.0)
        b = bmesh.new()
        prism(b, [(-0.02 * S, 0.015 * S), (0.02 * S, 0.015 * S), (0.0, -0.015 * S)], loc, Vector((0, 1, 0)), Vector((0, 0, 1)), Vector(nor),
              -0.003 * S, 0.01 * S)
        boolean(cap, obj('CUT_TRI', b, ['MAT_Pod'], 'HILFE'))
        # Sockel oben Ø 0,035 × 0,02 (Antennenfuß; links mit Deckel)
        top = POD_C[2] + 0.125 - 0.012
        b = bmesh.new()
        cyl(b, 0.0175 * S, 0.02 * S, H(sx * 0.43, POD_C[1], top + 0.01), (0, 0, 1), 24)
        extra.append(obj('SOCKEL', b, ['MAT_Pod']))
        join(pod, [cap] + extra)
        for dy, dz in ((-0.06, 0.08), (0.06, -0.08)):
            spots.append((H(sx * x0, POD_C[1] + dy, POD_C[2] + dz), (sx, 0, 0)))
        # Bügel Ø 0,012, Bezier 4 Punkte: Füße vorn/hinten unten, Scheitel 0,04 über dem Pod
        pts = [H(sx * 0.42, -0.15, 0.44), H(sx * 0.50, -0.13, 0.66), H(sx * 0.50, 0.05, 0.66), H(sx * 0.42, 0.07, 0.44)]
        curve_obj(f'Pod_Buegel_{side}', [('BEZIER', pts)], 0.006 * S, 'MAT_Metall', 16)
        # Stecker Ø 0,03 × 0,03, unten vorn, Achse 30° nach vorn geneigt
        b = bmesh.new()
        cyl(b, 0.015 * S, 0.03 * S, H(sx * 0.43, -0.10, 0.43), (0, -0.5, -0.866), 20)
        obj(f'Pod_Stecker_{side}', b, ['MAT_Metall'])
    # Antenne rechts: Fuß auf dem Sockel, Ø 0,014 × 0,45, 12° nach vorn, 5° nach außen, unten Hülse Ø 0,018 × 0,12
    foot = H(0.43, POD_C[1], POD_C[2] + 0.125 - 0.012 + 0.02)
    d = Vector((math.tan(math.radians(5)), -math.tan(math.radians(12)), 1)).normalized()
    b = bmesh.new()
    cyl(b, 0.007 * S, 0.45 * S, foot + d * 0.225 * S, d, 16)
    cyl(b, 0.009 * S, 0.12 * S, foot + d * 0.06 * S, d, 16)
    obj('Antenne_R', b, ['MAT_Dunkel'])
    save('7')
    return spots


CABLE = [(0.43, -0.10, 0.42), (0.47, -0.05, 0.28), (0.46, 0.30, 0.24), (0.18, 0.50, 0.60)]


def section_8():
    for side, sx in (('L', -1), ('R', 1)):
        P = [H(sx * x, y, z) for x, y, z in CABLE]
        tmp = curve_obj('TMP_KERN', [('BEZIER', P)], 0.006 * S, 'MAT_Kabel', 64, 'HILFE')
        path = eval_points(tmp)
        bpy.data.objects.remove(tmp, do_unlink=True)
        L = [0.0]
        for p, q in zip(path, path[1:]):
            L.append(L[-1] + (q - p).length)
        pitch, rad = 0.018 * S, 0.022 * S
        n = int(L[-1] / pitch * 12)
        helix = []
        nrm = None
        for i in range(n + 1):
            s_ = L[-1] * i / n
            j = min(max(k for k in range(len(L)) if L[k] <= s_), len(path) - 2)
            u = (s_ - L[j]) / max(L[j + 1] - L[j], 1e-9)
            p = path[j].lerp(path[j + 1], u)
            t = (path[j + 1] - path[j]).normalized()
            if nrm is None:
                nrm = t.cross(Vector((0, 0, 1))).normalized()
            nrm = (nrm - t * nrm.dot(t)).normalized()
            bi = t.cross(nrm)
            ang = 2 * math.pi * s_ / pitch
            helix.append(p + (nrm * math.cos(ang) + bi * math.sin(ang)) * rad)
        curve_obj(f'Kabel_{side}', [('BEZIER', P), ('POLY', helix)], 0.006 * S, 'MAT_Kabel', 24)
    save('8')


def section_9(sh):
    tree = bvh(sh)
    b = shell_plate(tree, densify(rounded_rect(0.30, 0.24, 0.01, 2), 0.03), H(0, 0.9, 0.66), Vector((1, 0, 0)), Vector((0, 0, 1)),
                    Vector((0, 1, 0)), 0.0, 0.10)
    b.verts.ensure_lookup_table()
    inner, outer = list(b.verts)[0::2], list(b.verts)[1::2]
    inner_max = max(v.co.y for v in inner)
    yb = inner_max + 0.10 * S                          # Rückseite eben
    for v in outer:
        v.co.y = yb
    box = obj('Rueckbox', b, ['MAT_Pod'])
    bevel(box)
    hexo = [(-0.07, 0.08), (0.07, 0.08), (0.11, 0.04), (0.11, -0.04), (0.07, -0.08), (-0.07, -0.08), (-0.11, -0.04), (-0.11, 0.04)]
    hb = bmesh.new()
    prism(hb, [(u * S, v * S) for u, v in hexo], Vector((0, yb, 0.66 * S)), Vector((-1, 0, 0)), Vector((0, 0, 1)), Vector((0, 1, 0)),
          -0.001 * S, 0.012 * S)
    hexp = obj('HEX', hb, ['MAT_Pod'])
    hi = [(-0.05, 0.05), (0.05, 0.05), (0.08, 0.02), (0.08, -0.02), (0.05, -0.05), (-0.05, -0.05), (-0.08, -0.02), (-0.08, 0.02)]
    cut = bmesh.new()
    prism(cut, [(u * S, v * S) for u, v in hi], Vector((0, yb + 0.008 * S, 0.66 * S)), Vector((-1, 0, 0)), Vector((0, 0, 1)), Vector((0, 1, 0)),
          0.0, 0.01 * S)
    for sg in (-1, 1):
        R = Matrix.Rotation(math.radians(sg * 40), 3, 'Y')
        add_box(cut, Vector((sg * 0.015 * S, yb + 0.012 * S, 0.66 * S)), (0.10 * S, 0.004 * S, 0.003 * S), R)
    boolean(hexp, obj('CUT_HEX', cut, ['MAT_Pod'], 'HILFE'))
    tp = shell_plate(tree, densify([(-0.05, 0.02), (0.05, 0.02), (0.035, -0.02), (-0.035, -0.02)], 0.02), H(0, 0.9, 0.50), Vector((1, 0, 0)),
                     Vector((0, 0, 1)), Vector((0, 1, 0)), -0.001, 0.003)
    trap = obj('TRAPEZ', tp, ['MAT_Pod'])
    join(box, [hexp, trap])
    spots = [(Vector((sx * 0.13 * S, yb, z * S)), (0, 1, 0)) for sx in (-1, 1) for z in (0.56, 0.76)]
    for side, sx in (('L', -1), ('R', 1)):
        b = bmesh.new()
        cyl(b, 0.02 * S, 0.04 * S, H(sx * 0.17, (inner_max / S + yb / S) / 2, 0.60), (1, 0, 0), 24)
        obj(f'Rueckbox_Anschluss_{side}', b, ['MAT_Metall'])
    NOTES.append(f'9.1 Rückbox: Vorderseite auf der Schale, Rückseite eben bei Y {yb / S:.3f}')
    save('9')
    return spots


def section_10(spots):
    bm = bmesh.new()
    lathe(bm, [(0, 0), (0.006 * S, 0), (0.006 * S, 0.003 * S), (0.004 * S, 0.0045 * S), (0, 0.005 * S)], frame_of((0, 0, 1)), Vector((0, 0, 0)), 16)
    me = bpy.data.meshes.new('Schraube')
    bm.to_mesh(me)
    bm.free()
    tmp = bpy.data.objects.new('TMP_S', me)
    coll('HILFE').objects.link(tmp)
    cut = bmesh.new()
    for R in (Matrix.Identity(3), Matrix.Rotation(math.pi / 2, 3, 'Z')):
        add_box(cut, Vector((0, 0, 0.005 * S)), (0.009 * S, 0.0015 * S, 0.002 * S), R)
    boolean(tmp, obj('CUT_SCHLITZ', cut, ['MAT_Metall'], 'HILFE'))
    me = tmp.data
    bpy.data.objects.remove(tmp, do_unlink=True)
    me.materials.clear()
    me.materials.append(mat('MAT_Metall'))
    targets = [o for o in coll('HELM_V3').objects if o.type == 'MESH']
    tree = bvh(targets)
    missing = [i for i, (p, n) in enumerate(spots) if p is None or n is None]
    if missing:
        NOTES.append(f'10 Schrauben: {len(missing)} Position(en) ohne Treffer übersprungen')
    spots = [(p, n) for p, n in spots if p is not None and n is not None]
    for i, (p, n) in enumerate(spots):
        n = Vector(n).normalized()
        loc, nor, _, _ = tree.ray_cast(Vector(p) + n * 0.3 * S, -n, 1.0)
        if loc is None:
            loc, nor = Vector(p), n
        ob = bpy.data.objects.new(f'Schraube_{i + 1:02d}', me)
        R = frame_of(nor)
        R = Matrix((R.col[1], R.col[2], R.col[0])).transposed()
        ob.matrix_world = Matrix.Translation(loc) @ R.to_4x4()
        coll('HELM_V3').objects.link(ob)
    save('10')


# ------------------------------------------------------------------ 15/16/17

def bounds(obs):
    dg = bpy.context.evaluated_depsgraph_get()
    lo, hi = Vector((1e9,) * 3), Vector((-1e9,) * 3)
    for ob in obs:
        e = ob.evaluated_get(dg)
        for c in e.bound_box:
            w = e.matrix_world @ Vector(c)
            lo, hi = Vector(map(min, lo, w)), Vector(map(max, hi, w))
    return (hi - lo) / S, lo / S, hi / S


NAMES = ['Schale', 'Kappe', 'Maske_Stirn', 'Auge_L', 'Auge_R', 'Maske_Wange_L', 'Maske_Wange_R', 'Maske_Nase', 'Kinnleiste', 'Kinn_Panel',
         'Pod_L', 'Pod_R', 'Pod_Buegel_L', 'Pod_Buegel_R', 'Pod_Stecker_L', 'Pod_Stecker_R', 'Kabel_L', 'Kabel_R', 'Rueckbox',
         'Rueckbox_Anschluss_L', 'Rueckbox_Anschluss_R', 'Antenne_R', 'Lug_L', 'Lug_R']


def acceptance(iou1, iou7, iou9):
    rows, errs = [], []
    O = bpy.data.objects
    ok = passed(iou1)
    rows.append(('1 IoU Phase 1 (mit Opening)', ', '.join(f'{k} {v:.3f}' for k, v in iou1.items()), 'bestanden' if ok else 'nicht bestanden'))
    if not ok:
        errs.append('1 Stop-Kriterium Phase 1 nicht erreicht')
    for tag, r in (('nach 7', iou7), ('nach 9', iou9)):
        ok2 = min(r.values()) >= 0.86
        rows.append((f'1 IoU {tag} (ohne Opening)', ', '.join(f'{k} {v:.3f}' for k, v in r.items()), 'ok' if ok2 else 'unter 0,86'))
        if not ok2:
            errs.append(f'1 IoU {tag} unter 0,86')
    d, lo, hi = bounds([O[n] for n in ('Schale', 'Kappe', 'Maske_Stirn', 'Maske_Wange_L', 'Maske_Wange_R', 'Maske_Nase', 'Kinnleiste')])
    ok = abs(d.x - 0.80) <= 0.02 and abs(d.y - 1.06) <= 0.03 and abs(d.z - 1.00) <= 0.01
    rows.append(('2 Hüllbox Grundmassen (X × Y × Z)', f'{d.x:.3f} × {d.y:.3f} × {d.z:.3f}', 'ok' if ok else 'außerhalb'))
    if not ok:
        errs.append('2 Hüllbox')
    # 3 Kragenstufe: Außenradius seitlich knapp unter/über Z 0,30
    sh = O['Schale']
    t = bvh(sh)
    xs = []
    for z in (0.295, 0.315):
        loc, _, _, _ = t.ray_cast(H(1.0, 0.0, z), Vector((-1, 0, 0)), 2.0)
        xs.append(loc.x / S if loc else 0)
    st = xs[1] - xs[0]
    rows.append(('3 Kragenstufe (Sprung seitlich Z 0,295 → 0,315)', f'{st:.3f}', 'ok' if st > 0.02 else 'fehlt'))
    if st <= 0.02:
        errs.append('3 Kragenstufe')
    # 4 Krempe 0,02 ± 0,005 über der Schale (Stichproben seitlich und hinten-seitlich)
    tk = bvh(O['Kappe'])
    over = []
    for ang in (90, 135, 180, 225, 270):            # Seiten und Rücken (vorn ist die Krempe laut 4.2 um 0,025 länger)
        a = math.radians(ang)
        d_ = Vector((math.sin(a), -math.cos(a), 0))
        lk, _, _, _ = tk.ray_cast(H(0, 0, 0.73) + d_ * 2 * S, -d_, 3.0)
        ls, _, _, _ = t.ray_cast(H(0, 0, 0.73) + d_ * 2 * S, -d_, 3.0)
        if lk and ls:
            over.append(((lk - ls).length / S, ang))
    ok = all(abs(o - 0.02) <= 0.005 for o, _ in over)
    rows.append(('4 Krempenüberstand', ', '.join(f'{a}°: {o:.3f}' for o, a in over), 'ok' if ok else 'außerhalb'))
    if not ok:
        errs.append('4 Krempe')
    # 5 Pods gespiegelt, Antenne nur rechts 0,45 ± 0,03
    dl, lol, hil = bounds([O['Pod_L']])
    dr, lor, hir = bounds([O['Pod_R']])
    cl, cr = (lol + hil) / 2, (lor + hir) / 2
    ok = abs(abs(cl.x) - abs(cr.x)) <= 0.005 and (dl - dr).length <= 0.005
    ant = O['Antenne_R']
    La = max(v.co.length for v in ant.data.vertices) / S
    vs = [v.co for v in ant.data.vertices]
    La = max((a - b).length for a in vs[::7] for b in vs[::7]) / S
    ok2 = 'Antenne_L' not in O and abs(La - 0.45) <= 0.03
    rows.append(('5 Pods gespiegelt / Antenne', f'Zentrum x {cl.x:.3f}/{cr.x:.3f}, Maße Δ {(dl - dr).length:.4f}; Antenne_R {La:.3f}',
                 'ok' if ok and ok2 else 'nicht ok'))
    if not (ok and ok2):
        errs.append('5 Pods/Antenne')
    # 6 Kabelabstand ≥ 0,015 (Mantel zu Schale und Pods)
    tt = bvh([O['Schale'], O['Pod_L'], O['Pod_R']])
    mins = []
    for side in 'LR':
        ob = O[f'Kabel_{side}']
        pts = []
        for sp in ob.data.splines:
            if sp.type == 'POLY':
                pts = [Vector(p.co[:3]) for p in sp.points]
        dmin = min(tt.find_nearest(p)[3] for p in pts[len(pts) // 6: -len(pts) // 6]) / S - 0.006
        mins.append(dmin)
    ok = min(mins) >= 0.015
    rows.append(('6 Kabelabstand (Mittelteil, Wendel)', ', '.join(f'{m:.3f}' for m in mins), 'ok' if ok else 'zu nah'))
    if not ok:
        errs.append('6 Kabelabstand')
    missing = [n for n in NAMES if n not in O]
    multi = [o.name for o in coll('HELM_V3').objects if o.data and len(o.data.materials) != 1]
    nsc = len([o for o in coll('HELM_V3').objects if o.name.startswith('Schraube_')])
    ok = not missing and not multi and nsc >= 18
    rows.append(('7 Objekte, Materialien, Schrauben', f'fehlend {missing or "–"}, mehrere Materialien {multi or "–"}, Schrauben {nsc}',
                 'ok' if ok else 'nicht ok'))
    if not ok:
        errs.append('7 Objekte/Materialien/Schrauben')
    rows.append(('8 Lauf aus leerer Datei', 'durchgelaufen', 'ok'))
    return rows, errs


def render_final(samples):
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE'
    sc.eevee.taa_render_samples = samples
    sc.render.film_transparent = False
    sc.render.resolution_x = sc.render.resolution_y = 720
    world = bpy.data.worlds.new('Grau')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (*srgb('#8A8C90'), 1)
    sc.world = world
    sc.view_settings.view_transform = 'Standard'
    for nm, loc, en, size in (('Key', H(-1.8, -2.6, 2.4), 60, 1.0), ('Fill', H(1.6, 2.8, 1.4), 25, 1.4)):
        li = bpy.data.objects.new(nm, bpy.data.lights.new(nm, 'AREA'))
        li.data.energy, li.data.size = en, size
        li.location = loc
        li.rotation_euler = (H(0, 0, 0.5) - loc).to_track_quat('-Z', 'Y').to_euler()
        sc.collection.objects.link(li)
    out = {}
    for name, cam in camera_rig().items():
        sc.camera = cam
        sc.render.filepath = os.path.join(OUT, f'check_{name}.png')
        bpy.ops.render.render(write_still=True)
        out[name] = sc.render.filepath
    ref = os.path.join(OUT, 'ref_helm_v3.png')
    subprocess.run(['cp', REF, ref], check=True)
    w = int(subprocess.run(['magick', 'identify', '-format', '%w', ref], capture_output=True, text=True).stdout)
    for i, (name, _) in enumerate(CAMS):
        part = os.path.join(OUT, f'_ref_{i}.png')
        subprocess.run(['magick', ref, '-crop', f'{w // 4}x+{i * (w // 4)}+0', '+repage', '-resize', 'x720', part], check=True)
        subprocess.run(['magick', part, out[name], '-resize', 'x720', '+append', os.path.join(OUT, f'compare_{name}.png')], check=True)
        os.remove(part)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)


def report(rows, errs):
    L = ['# Helm „Scout v3“ – Bericht', '', f'- Ergebnis: {"alle Abnahmekriterien erfüllt" if not errs else f"{len(errs)} Kriterien offen"}',
         f'- Datei `{BLEND}`, Skript `tools/build_helm_v3.py`', '', '## IoU je Iteration (Phase 1, Referenz mit Opening)', '',
         '| Schritt | a | b_v | b_h | Kuppel c | front | right | back | left |', '|---|---|---|---|---|---|---|---|---|']
    for step, k, r in LOG:
        L.append(f"| {step} | {k['a']:.3f} | {k['bv']:.3f} | {k['bh']:.3f} | {k['cap_c']:.3f} | " + ' | '.join(f'{r[n]:.3f}' for n, _ in CAMS) + ' |')
    L += ['', '## Abnahmekriterien (Abschnitt 16)', '', '| Kriterium | Messwert | Ergebnis |', '|---|---|---|']
    L += [f'| {a} | {b} | {c} |' for a, b, c in rows]
    L += ['', '## Nicht erreichte Punkte', ''] + ([f'- {e}' for e in errs] or ['- keine'])
    L += ['', '## Hinweise', ''] + [f'- {n}' for n in NOTES]
    L += ['', '## Abweichungen vom Vorgehen', ''] + [f'- {d}' for d in DEVIATIONS]
    open(os.path.join(OUT, 'REPORT.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    with open(os.path.join(OUT, 'iou.log'), 'w', encoding='utf-8') as fh:
        for step, k, r in LOG:
            fh.write(f'{step}\t{k}\t{r}\n')


def main():
    os.makedirs(OUT, exist_ok=True)
    reset()
    if '--reuse-phase1' in ARGS:
        d = json.load(open(os.path.join(OUT, 'phase1.json')))
        K.update(d['K'])
        LOG[:] = [tuple(x) for x in d['LOG']]
        NOTES[:] = d['NOTES'] + ['Phase 1 aus phase1.json übernommen (--reuse-phase1)']
        phase1_masses()
        iou1 = iou_all()
    else:
        iou1 = phase1()
    if '--phase1-only' in ARGS:
        report([('1 IoU Phase 1', str(iou1), 'bestanden' if passed(iou1) else 'nicht bestanden')], [] if passed(iou1) else ['1'])
        return
    if not passed(iou1):
        NOTES.append('Phase 1 nach 8 Iterationen nicht bestanden; Phase 2 trotzdem gebaut (Kriterium 1 offen)')
    bpy.data.objects.remove(bpy.data.objects['MASKE_P1'], do_unlink=True)
    sh = bpy.data.objects['Schale']
    s1 = section_3_2(sh)
    section_4(with_lugs=True)
    s2 = section_5(sh)
    section_6_2(bpy.data.objects['Kinnleiste'])
    s3 = section_7(sh)
    iou7 = iou_all('sil7', open_k=0)
    section_8()
    s4 = section_9(sh)
    iou9 = iou_all('sil9', open_k=0)
    section_10(s1 + s2 + s3 + s4)
    for o in coll('HILFE').objects:
        o.hide_render = True
    rows, errs = acceptance(iou1, iou7, iou9)
    if '--no-render' not in ARGS:
        render_final(int(arg('--samples', 48)))
    report(rows, errs)
    print('[v3] fertig:', 'alle Kriterien erfüllt' if not errs else f'{len(errs)} offen', flush=True)


if __name__ == '__main__':
    main()
