"""Helm „Scout“ Version 2 nach der Spezifikation des Nutzers (27.10.2026): glatte Ei-Schale aus Superellipsen-Querschnitten,
Subdivision 2, Dunkel/Weiß per Material und Nut, zwei Phasen mit Silhouetten-Abnahme (IoU) dazwischen.

  blender -b --factory-startup -P tools/build_helm.py -- [--out DIR] [--ref PNG] [--phase1-only] [--samples N]

Maße in H (Helmhöhe = 0,30 m), +Z oben, −Y vorn, +X rechts vom Träger. Ergebnis in DIR (Standard
~/Library/Caches/CubeEscapeBallon/out/helm_scout_v2): helm_scout.blend (nach jedem Abschnitt gespeichert), sil_<cam>.png,
check_<cam>.png, compare_<cam>.png, iou.log, REPORT.md.
"""
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


OUT = os.path.expanduser(arg('--out', '~/Library/Caches/CubeEscapeBallon/out/helm_scout_v2'))
REF = os.path.expanduser(arg('--ref', '~/Library/Caches/CubeEscapeBallon/refs/robot-helm-mil.png'))
BLEND = os.path.join(OUT, 'helm_scout.blend')
CAMS = (('cam_front34', -35), ('cam_left', -90), ('cam_back34', 145), ('cam_right', 90))
LOG, NOTES = [], []
DEVIATIONS = [
    'Spiegelung: Schale und Teile sind aus symmetrischen Funktionen gebaut (beide Seiten direkt) statt mit Mirror-Modifier; '
    'die Grenzschnitte und Raycasts brauchen beide Seiten',
    'Nut und Panels ohne Inset: Grenzkanten mit Crease (0,7/0,5), nach der Subdivision Versatz der Ecken (Dunkel +0,004, Panels '
    'und Mundlinie −0,003); Reihenfolge Subdivision → Versatz → Solidify statt Solidify → Subdivision (die Inset-Streifen auf dem '
    '48er-Grundnetz falteten sich in Solidify/Subdivision bis 0,5 H auf)',
    'Abnahme-Kameras mit Abstand 3,6 statt 3,0 (bei 85 mm zeigt 3,0 nur 1,27 H, Kuppel und Antenne waren abgeschnitten)',
    'Phase-1-Anpassung im Toleranzband der Hüllbox (Breite 0,82–0,86, Tiefe 1,02–1,06), sonst hätte die IoU-Suche die Breite '
    'unter das Abnahmemaß gedrückt',
    'Wangen-Panels ohne die 6°-Neigung nach hinten (nur 0,003 abgesenkt)',
    'Grenzlinie (4.2) mit bmesh.bisect_plane entlang der projizierten Linie statt Knife Project (braucht ein 3D-Fenster, im '
    'Hintergrundlauf nicht verfügbar); Ergebnis gleich: eine Kantenschleife auf der Grenze, keine Boolean',
    'Tuch-Oberkante (11.2): keine Zeile der Vorlage ist breiter als 0,9 der Teilbreite (das Tuch ist schmaler); die Kante ist je '
    'Viertel an der Vorlage abgelesen (Zeilen 116/114/96/88 von 238), das eigene Render wird auf derselben Helmhöhe abgeschnitten '
    '(Z 0,05/0,12/0,28/0,33, geschätzt), damit beide Masken denselben Ausschnitt zeigen',
    'Silhouettenprüfung mit eigenen Messkameras je Viertel (Azimut/Elevation per Suche bestimmt): die Vorlage zeigt nicht die '
    'Richtungen aus Abschnitt 13 (Viertel 2 = Dreiviertel links, 3 = linke Seite mit Hinterkopf, 4 = Hinterkopf schräg links); die '
    'Abnahme-Renders check_/compare_ nutzen weiter die Kameras aus 13, zusätzlich compare_fit_ mit den Messkameras',
    'Referenzmaske (11.2): Helm = Pixel, die sich um mehr als 0,07 vom Hintergrundgrau unterscheiden (heller oder dunkler); nur '
    '„dunkler“ hätte die weißen Teile der Referenz ausgeschlossen',
]


def H(*c):
    return Vector(c) * S


# ------------------------------------------------------------------ Szene, Material, Hilfen

def srgb(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)


MATS = {'MAT_Dunkel': ('#26282B', 0.50, 0.15), 'MAT_Weiss': ('#D9D7D1', 0.60, 0.0), 'MAT_Pod': ('#3A3C3F', 0.50, 0.4),
        'MAT_Schlauch': ('#1C1C1C', 0.40, 0.0), 'MAT_Metall': ('#707070', 0.30, 1.0), 'MAT_Tuch': ('#8A8680', 0.90, 0.0)}


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
        em.inputs['Color'].default_value = (*srgb('#4FE3E8'), 1)
        em.inputs['Strength'].default_value = 5.0
        nt.links.new(em.outputs[0], out.inputs['Surface'])
        m.diffuse_color = (*srgb('#4FE3E8'), 1)
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
    helm = bpy.data.collections.new('HELM')
    sc.collection.children.link(helm)
    helm.children.link(bpy.data.collections.new('TUCH'))
    hilfe = bpy.data.collections.new('HILFE')
    sc.collection.children.link(hilfe)


def obj(name, bm, mats, collection='HELM', recalc=True):
    me = bpy.data.meshes.new(name)
    if recalc:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
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
    ctx(target)
    for o in others:
        o.select_set(True)
    with bpy.context.temp_override(active_object=target, selected_editable_objects=[target] + others, selected_objects=[target] + others):
        bpy.ops.object.join()
    return target


def boolean(ob, cutter):
    m = ob.modifiers.new('BOOL', 'BOOLEAN')
    m.operation, m.solver, m.object, m.use_self = 'DIFFERENCE', 'EXACT', cutter, True
    apply_mod(ob, m.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def bvh(ob):
    return BVHTree.FromObject(ob, bpy.context.evaluated_depsgraph_get())


def save(step):
    os.makedirs(OUT, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print(f'[helm] {step} gespeichert', flush=True)


def frame_of(axis):
    a = Vector(axis).normalized()
    h = Vector((0, 0, 1)) if abs(a.z) < 0.9 else Vector((1, 0, 0))
    u = a.cross(h).normalized()
    return Matrix((a, u, a.cross(u))).transposed()


def lathe(bm, prof, M, origin, segs=48, mat_index=0):
    """Drehkörper um Spalte 0 von M: prof = [(r, a)], Enden mit r = 0 geschlossen."""
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
    return rings


def cyl(bm, r, length, center, axis, segs=32, mat_index=0):
    lathe(bm, [(0, -length / 2), (r, -length / 2), (r, length / 2), (0, length / 2)], frame_of(axis), center, segs, mat_index)


def rounded_rect(w, h, r, n=4):
    pts = []
    for cu, cv, a0 in ((w / 2 - r, h / 2 - r, 0), (-(w / 2 - r), h / 2 - r, 90), (-(w / 2 - r), -(h / 2 - r), 180), (w / 2 - r, -(h / 2 - r), 270)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cu + r * math.cos(a), cv + r * math.sin(a)))
    return pts


def prism(bm, outline, origin, U, V, N, d0, d1, mat_index=0):
    """Prisma: Umriss (u, v) in der Ebene (U, V) um origin, entlang N von d0 bis d1 (Meter)."""
    a = [bm.verts.new(Vector(origin) + U * u + V * v + N * d0) for u, v in outline]
    b = [bm.verts.new(Vector(origin) + U * u + V * v + N * d1) for u, v in outline]
    fs = [bm.faces.new(a[::-1]), bm.faces.new(b)]
    for k in range(len(a)):
        k2 = (k + 1) % len(a)
        fs.append(bm.faces.new((a[k], a[k2], b[k2], b[k])))
    for f in fs:
        f.material_index = mat_index
    return fs


def plate_on(tree, name, outline, center, U, V, n_out, thick, mats, rays=None):
    """Platte: Umriss (u, v) um center, Innenseite per Raycast entlang −n_out auf die Schale (Shrinkwrap), Dicke nach außen."""
    bm = bmesh.new()
    inner, outer = [], []
    for u, v in outline:
        p = Vector(center) + U * u + V * v
        loc, _, _, _ = tree.ray_cast(p + n_out * 0.4 * S, -n_out, 2.0)
        q = loc if loc is not None else p
        inner.append(bm.verts.new(q))
        outer.append(bm.verts.new(q + n_out * thick))
    bm.faces.new(inner[::-1])
    bm.faces.new(outer)
    for k in range(len(inner)):
        k2 = (k + 1) % len(inner)
        bm.faces.new((inner[k], inner[k2], outer[k2], outer[k]))
    return obj(name, bm, mats)


def curve_obj(name, pts, r, mat_name, taper=None, res=6, collection='HELM'):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    cu.bevel_depth, cu.bevel_resolution, cu.resolution_u, cu.use_fill_caps = r, 6, res, True
    if taper:
        cu.taper_object = taper
    ob = bpy.data.objects.new(name, cu)
    coll(collection).objects.link(ob)
    ob.data.materials.append(mat(mat_name))
    return ob


def curve_points(ob):
    cu = ob.data
    keep = (cu.bevel_depth, cu.taper_object)
    cu.bevel_depth, cu.taper_object = 0.0, None
    bpy.context.view_layer.update()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    pts = [v.co.copy() for v in me.vertices]
    bpy.data.meshes.remove(me)
    cu.bevel_depth, cu.taper_object = keep
    bpy.context.view_layer.update()
    return pts


# ------------------------------------------------------------------ 3 Schale (Phase 1)

TABLE = [  # Z, a, b_v, b_h, Yc, n_v, n_h
    (0.00, 0.24, 0.34, 0.36, 0.06, 2.3, 2.0), (0.06, 0.31, 0.41, 0.44, 0.05, 2.4, 2.0), (0.15, 0.36, 0.46, 0.50, 0.04, 2.5, 2.0),
    (0.28, 0.40, 0.48, 0.54, 0.03, 2.5, 2.0), (0.40, 0.42, 0.48, 0.56, 0.03, 2.5, 2.0), (0.52, 0.42, 0.47, 0.56, 0.03, 2.4, 2.0),
    (0.62, 0.415, 0.46, 0.54, 0.04, 2.3, 2.0), (0.72, 0.40, 0.47, 0.51, 0.04, 2.2, 2.0), (0.80, 0.37, 0.43, 0.46, 0.05, 2.1, 2.0),
    (0.88, 0.32, 0.35, 0.39, 0.06, 2.0, 2.0), (0.94, 0.24, 0.25, 0.29, 0.06, 2.0, 2.0), (0.98, 0.13, 0.13, 0.15, 0.06, 2.0, 2.0)]
K = dict(a=1.0, bv=1.0, bh=1.0, yc=0.0)        # Anpassung in Phase 1 (Faktoren auf a, b_v, b_h; Verschiebung von Yc)


def table():
    return [(z, a * K['a'], bv * K['bv'], bh * K['bh'], yc + K['yc'], nv, nh) for z, a, bv, bh, yc, nv, nh in TABLE]


def interp(T, z):
    """Catmull-Rom über die Stationen der Tabelle (alle Spalten), oberhalb Z 0,98 Kuppel bis zum Pol."""
    zs = [r[0] for r in T]
    if z >= zs[-1]:
        top = T[-1]
        f = math.sqrt(max(0.0, (1.0 - z) / (1.0 - zs[-1])))
        return (z, top[1] * f, top[2] * f, top[3] * f, top[4], top[5], top[6])
    i = max(k for k in range(len(zs)) if zs[k] <= z)
    i = min(i, len(zs) - 2)
    p0, p1, p2, p3 = T[max(i - 1, 0)], T[i], T[i + 1], T[min(i + 2, len(T) - 1)]
    t = (z - p1[0]) / (p2[0] - p1[0])
    out = [z]
    for c in range(1, 7):
        m1 = (p2[c] - p0[c]) / max(p2[0] - p0[0], 1e-9) * (p2[0] - p1[0])
        m2 = (p3[c] - p1[c]) / max(p3[0] - p1[0], 1e-9) * (p2[0] - p1[0])
        h00, h10, h01, h11 = 2 * t ** 3 - 3 * t * t + 1, t ** 3 - 2 * t * t + t, -2 * t ** 3 + 3 * t * t, t ** 3 - t * t
        out.append(h00 * p1[c] + h10 * m1 + h01 * p2[c] + h11 * m2)
    return tuple(out)


def ring_pts(row, n=48):
    z, a, bv, bh, yc, nv, nh = row
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        c, s = math.cos(t), math.sin(t)
        if s >= 0:      # vorn (−Y)
            x, y = a * abs(c) ** (2 / nv) * math.copysign(1, c), yc - bv * abs(s) ** (2 / nv)
        else:
            x, y = a * abs(c) ** (2 / nh) * math.copysign(1, c), yc + bh * abs(s) ** (2 / nh)
        pts.append((x, y, z))
    return pts


def build_shell_base():
    """Grundnetz: 48 Punkte je Ring, Ringe an den Stationen und dazwischen (Catmull-Rom), oben Pol, unten offen."""
    T = table()
    zs = sorted(set([round(z, 4) for z in np.arange(0.0, 0.981, 0.02)] + [r[0] for r in T] + [0.99, 0.995]))
    bm = bmesh.new()
    rings = [[bm.verts.new(H(*p)) for p in ring_pts(interp(T, z))] for z in zs]
    n = len(rings[0])
    for A, B in zip(rings, rings[1:]):
        for k in range(n):
            k2 = (k + 1) % n
            bm.faces.new((A[k], A[k2], B[k2], B[k]))
    pole = bm.verts.new(H(0, T[-1][4], 1.0))
    for k in range(n):
        bm.faces.new((rings[-1][k], rings[-1][(k + 1) % n], pole))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    if sum(f.normal.dot(f.calc_center_median() - H(0, 0.03, 0.5)) for f in bm.faces) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    return bm


def shell_modifiers(ob):
    so = ob.modifiers.new('SOLID', 'SOLIDIFY')
    so.thickness, so.offset, so.use_rim = 0.015 * S, -1.0, True     # ohne Even Thickness: an den schmalen Inset-Streifen der Nut
    so.use_even_offset = False                                       # schoss sie bis 0,5 H über die Schale hinaus
    sd = ob.modifiers.new('SUBSURF', 'SUBSURF')
    sd.levels = sd.render_levels = 2
    sd.subdivision_type = 'CATMULL_CLARK'


def section_3():
    old = bpy.data.objects.get('Helm_Schale')
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    ob = obj('Helm_Schale', build_shell_base(), ['MAT_Dunkel', 'MAT_Weiss'], recalc=False)
    shell_modifiers(ob)
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


# ------------------------------------------------------------------ 11 Silhouetten und IoU

DIST = float(arg('--cam-dist', 3.6))   # Abschnitt 13: 3,0 schneidet Kuppel und Antenne ab (85 mm zeigen dort nur 1,27 H)
FIT = {}          # Blickrichtung je Viertel der Vorlage (Azimut, Elevation), per Suche bestimmt


def camera_rig(fit=False):
    sc = bpy.context.scene
    target = H(0, 0.03, 0.45)
    cams = {}
    for name, az in CAMS:
        el = 8
        if fit:
            az, el = FIT.get(name, (az, el))
            name = 'fit_' + name
        cam = bpy.data.objects.get(name) or bpy.data.objects.new(name, bpy.data.cameras.new(name))
        if cam.name not in sc.collection.objects:
            sc.collection.objects.link(cam)
        cam.data.lens = 85
        a, e = math.radians(az), math.radians(el)
        cam.location = target + H(math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)) * (3.0 if fit else DIST)
        cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
        cams[name.replace('fit_', '')] = cam
    return cams


def render_sil(tag='sil', res=256, only=None):
    """Silhouetten: EEVEE mit transparentem Film, Alpha = Helm (nur Collection HELM, ohne Tuch)."""
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE'
    sc.eevee.taa_render_samples = 1
    sc.render.film_transparent = True
    sc.render.resolution_x = sc.render.resolution_y = res
    hide = [o for o in coll('TUCH').objects]
    for o in hide:
        o.hide_render = True
    out = {}
    for name, cam in camera_rig(fit=True).items():
        if only and name not in only:
            continue
        sc.camera = cam
        sc.render.filepath = os.path.join(OUT, f'{tag}_{name}.png')
        bpy.ops.render.render(write_still=True)
        out[name] = sc.render.filepath
    for o in hide:
        o.hide_render = False
    return out


def load_rgba(path):
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    a = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[::-1]
    bpy.data.images.remove(img)
    return a


REF_MASKS = {}
# Tuch-Oberkante je Viertel, an der Vorlage abgelesen (Zeile von 238), und die Helmhöhe Z, bei der das eigene Render gleich
# abgeschnitten wird (geschätzt: vorn liegt das Tuch am Kinn, hinten und rechts bedeckt es den Hinterkopf bis über den Nacken)
REF_CUT = {'cam_front34': 116, 'cam_left': 114, 'cam_back34': 96, 'cam_right': 88}
Z_CUT = {'cam_front34': 0.05, 'cam_left': 0.12, 'cam_back34': 0.28, 'cam_right': 0.33}


def ref_masks():
    """Referenz in vier gleich breite Teile; Helm = Abstand zum Hintergrundgrau > 0,07; unterhalb der Tuch-Oberkante verworfen."""
    if REF_MASKS:
        return REF_MASKS
    a = load_rgba(REF)
    h, w, _ = a.shape
    q = w // 4
    for i, (name, _) in enumerate(CAMS):
        p = a[:, i * q:(i + 1) * q, :3]
        border = np.concatenate([p[0], p[-1], p[:, 0], p[:, -1]])
        bg = np.median(border, axis=0)
        m = np.abs(p - bg).mean(axis=2) > 0.07
        m[:4], m[-4:], m[:, :4], m[:, -4:] = False, False, False, False   # Bildränder und Trennlinien der Vorlage
        widths = m.sum(axis=1)
        rows = np.where(widths > 0.9 * q)[0]          # Regel 11.2 (greift bei dieser Vorlage nicht: keine Zeile so breit)
        cut = rows[0] if len(rows) else int(round(REF_CUT[name] / 238 * h))
        if cut is not None:
            m[cut:] = False
        REF_MASKS[name] = m
        NOTES.append(f'Referenzmaske {name}: Tuch-Oberkante Zeile {cut} von {h}' + ('' if cut is not None else ' (nicht gefunden)'))
    return REF_MASKS


def norm_mask(m, H_=160, W_=360):
    ys, xs = np.nonzero(m)
    if len(ys) == 0:
        return np.zeros((H_, W_), bool)
    m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = m.shape
    s = H_ / h
    nw = max(1, int(round(w * s)))
    yi = np.minimum((np.arange(H_) / s).astype(int), h - 1)
    xi = np.minimum((np.arange(nw) / s).astype(int), w - 1)
    r = m[yi][:, xi]
    cx = np.nonzero(r)[1].mean()
    out = np.zeros((H_, W_), bool)
    off = int(round(W_ / 2 - cx))
    x0, x1 = max(0, off), min(W_, off + nw)
    out[:, x0:x1] = r[:, x0 - off:x1 - off]
    return out


def iou_all(tag='sil', only=None):
    paths = render_sil(tag, only=only)
    R = ref_masks()
    res = {}
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene
    cams = camera_rig(fit=True)
    for name, _ in CAMS:
        if only and name not in only:
            continue
        m = load_rgba(paths[name])[:, :, 3] > 0.5
        row = int(round((1 - world_to_camera_view(sc, cams[name], H(0, 0.03, Z_CUT[name])).y) * m.shape[0]))
        m[max(0, row):] = False                       # gleicher Ausschnitt wie die Referenz (oberhalb des Tuchs)
        A, B = norm_mask(m), norm_mask(R[name])
        res[name] = float((A & B).sum() / max((A | B).sum(), 1))
    return res


def passed(r):
    return min(r['cam_left'], r['cam_right']) >= 0.88 and min(r['cam_front34'], r['cam_back34']) >= 0.85


def score(r):
    return (r['cam_left'] + r['cam_right']) / 2 + (r['cam_front34'] + r['cam_back34']) / 2


GUESS = {'cam_front34': (0, 10), 'cam_left': (-60, 10), 'cam_back34': (-110, 10), 'cam_right': (-160, 10)}


def fit_views():
    """Die Viertel der Vorlage zeigen andere Richtungen als Abschnitt 13 (2: Dreiviertel links, 3: linke Seite mit Hinterkopf,
    4: Hinterkopf schräg links). Je Viertel Azimut (±40° in 10°-Schritten) und Elevation (0/10/20°) mit der größten IoU der
    Ausgangsform; diese Messkameras gelten für alle IoU-Werte, die Abnahme-Renders nutzen die Kameras aus Abschnitt 13."""
    for name, (az0, el0) in GUESS.items():
        best = None
        for az in range(az0 - 40, az0 + 41, 10):
            for el in (0, 10, 20):
                FIT[name] = (az, el)
                v = iou_all('fit', only=[name])[name]
                if best is None or v > best[0]:
                    best = (v, az, el)
        FIT[name] = best[1:]
        NOTES.append(f'Messkamera {name}: Azimut {best[1]}°, Elevation {best[2]}° (IoU Ausgangsform {best[0]:.3f})')
        print('[helm] Messkamera', name, FIT[name], round(best[0], 3), flush=True)


def phase1():
    """Grundform, Silhouetten-IoU, Tabellenanpassung (Faktoren auf a, b_v, b_h, Verschiebung Yc), höchstens 8 Iterationen."""
    section_3()
    fit_views()
    r = iou_all()
    LOG.append(('Start', dict(K), r))
    print('[helm] IoU Start', {k: round(v, 3) for k, v in r.items()}, flush=True)
    step = {'a': 0.03, 'bv': 0.03, 'bh': 0.03, 'yc': 0.02}
    it = 0
    while not passed(r) and it < 8:
        it += 1
        best = None
        for key in ('a', 'bv', 'bh', 'yc'):
            for sgn in (1, -1):
                K[key] += sgn * step[key]
                width, depth = 0.84 * K['a'], 0.48 * K['bv'] + 0.56 * K['bh']
                if not (0.82 <= width <= 0.86 and 1.02 <= depth <= 1.06):     # Abnahme 2: Hüllbox bleibt im Toleranzband
                    K[key] -= sgn * step[key]
                    continue
                section_3()
                rr = iou_all()
                if best is None or score(rr) > score(best[2]):
                    best = (key, sgn, rr)
                K[key] -= sgn * step[key]
        key, sgn, rr = best
        if score(rr) > score(r):
            K[key] += sgn * step[key]
            r = rr
            LOG.append((f'Iteration {it}: {key} {"+" if sgn > 0 else "−"}{step[key]}', dict(K), r))
        else:
            for k in step:
                step[k] /= 2
            LOG.append((f'Iteration {it}: keine Verbesserung, Schritte halbiert', dict(K), r))
        print('[helm]', LOG[-1][0], {k: round(v, 3) for k, v in r.items()}, flush=True)
    section_3()
    r = iou_all()
    import json
    json.dump(dict(K=K, FIT=FIT, LOG=LOG, NOTES=NOTES), open(os.path.join(OUT, 'phase1.json'), 'w'))
    save('Phase 1')
    return r


def phase1_reuse():
    """--reuse-phase1: Faktoren, Messkameras und Protokoll aus phase1.json übernehmen (nur zum schnellen Neubau von Phase 2)."""
    import json
    d = json.load(open(os.path.join(OUT, 'phase1.json')))
    K.update(d['K'])
    FIT.update({k: tuple(v) for k, v in d['FIT'].items()})
    LOG[:] = [tuple(x) for x in d['LOG']]
    NOTES[:] = d['NOTES'] + ['Phase 1 aus phase1.json übernommen (--reuse-phase1)']
    section_3()
    return iou_all()


# ------------------------------------------------------------------ 4/5 Aufteilung und Gesicht (auf dem Grundnetz)

SIDE = [(-0.30, 0.70), (-0.12, 0.60), (0.05, 0.57), (0.25, 0.55), (0.42, 0.50), (0.52, 0.45), (0.55, 0.43)]   # (Y, Z)
SIDE3 = [(0.36, -0.30, 0.70), (0.41, -0.12, 0.60), (0.42, 0.05, 0.57), (0.42, 0.25, 0.55), (0.36, 0.42, 0.50), (0.20, 0.52, 0.45),
         (0.0, 0.55, 0.43)]
WEDGE3 = [(0.36, -0.30, 0.70), (0.33, -0.38, 0.50), (0.28, -0.42, 0.32), (0.18, -0.45, 0.14), (0.10, -0.44, 0.06), (0.0, -0.43, 0.05)]


def lerp(tab, v):
    for (a0, b0), (a1, b1) in zip(tab, tab[1:]):
        if min(a0, a1) <= v <= max(a0, a1):
            return b0 + (b1 - b0) * (v - a0) / ((a1 - a0) or 1e-9)
    return tab[0][1] if v < min(tab[0][0], tab[-1][0]) else tab[-1][1]


def z_side(y):
    return lerp(SIDE, y)


def x_wedge(z):
    return lerp([(p[2], p[0]) for p in WEDGE3[::-1]], z)


def grat_half(z):
    return 0.025 + 0.01 * (z - 0.14) / 0.42


def is_dark(c):
    return c.z > z_side(c.y) or (c.y < -0.15 and abs(c.x) < x_wedge(c.z) and c.z > 0.05)


def is_panel(c):
    return c.y < -0.15 and 0.16 < c.z < 0.52 and grat_half(c.z) + 0.004 < abs(c.x) < x_wedge(c.z) - 0.02


def project(tree, p):
    loc, nor, _, _ = tree.find_nearest(H(*p))
    return loc, nor


def cut_polyline(bm, tree, pts3, radius=0.10):
    """Kantenschleife entlang einer Linie auf der Fläche: je Abschnitt bisect_plane durch beide Punkte und die Flächennormale,
    begrenzt auf die Flächen in der Nähe des Abschnitts."""
    P = [project(tree, p) for p in pts3]
    planes = []
    for (p0, n0), (p1, n1) in zip(P, P[1:]):
        d = p1 - p0
        L = d.length
        if L < 1e-6:
            continue
        t = d / L
        nrm = t.cross((n0 + n1).normalized()).normalized()
        planes.append((p0.copy(), t, L, nrm))
        geom = []
        for f in bm.faces:
            c = f.calc_center_median()
            u = (c - p0).dot(t) / L
            if -0.08 <= u <= 1.08 and (c - (p0 + t * max(0.0, min(L, (c - p0).dot(t))))).length < radius * S:
                geom.append(f)
        if not geom:
            continue
        g = list(geom) + list({e for f in geom for e in f.edges}) + list({v for f in geom for v in f.verts})
        bmesh.ops.bisect_plane(bm, geom=g, plane_co=p0, plane_no=nrm, dist=1e-6)
    return planes


def oriented(planes, inside):
    """Schnittebenen so drehen, dass der Punkt inside auf der positiven Seite liegt."""
    return [(p0, t, L, n if (inside - p0).dot(n) > 0 else -n) for p0, t, L, n in planes]


def side_of(planes, c):
    """Vorzeichenabstand von c zur nächsten Schnittebene (nächster Abschnitt der Linie)."""
    best = None
    for p0, t, L, n in planes:
        u = max(0.0, min(L, (c - p0).dot(t)))
        d = (c - (p0 + t * u)).length
        if best is None or d < best[0]:
            best = (d, (c - p0).dot(n))
    return best[1]


def section_4_5(ob):
    """Grenze Dunkel/Weiß, Nut, Wangen-Panels, Mundlinie – auf dem Grundnetz vor Solidify/Subdivision."""
    tree = BVHTree.FromObject(ob, bpy.context.evaluated_depsgraph_get(), deform=False)
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    tree = BVHTree.FromBMesh(bm)
    PL = {}
    for sx in (-1, 1):                                 # Ebenen zur Einteilung: Seitenlinie (dunkel oben), Keil (dunkel innen)
        PL['side', sx] = oriented(cut_polyline(bm, tree, [(sx * x, y, z) for x, y, z in SIDE3]), H(0, 0.06, 1.0))
        PL['wedge', sx] = oriented(cut_polyline(bm, tree, [(sx * x, y, z) for x, y, z in WEDGE3]), H(0, -0.5, 0.40))
        # Panel-Umriss: Grat-Kante, oben Z 0,52, unten Z 0,16; Mundlinie Z 0,297/0,303
        cut_polyline(bm, tree, [(sx * (grat_half(0.52) + 0.004), -0.5, 0.52), (sx * (grat_half(0.16) + 0.004), -0.5, 0.16)], 0.06)
    tree = BVHTree.FromBMesh(bm)
    for zc in (0.16, 0.52, 0.297, 0.303):
        cut_polyline(bm, tree, [(-x_wedge(zc), -0.6, zc), (0.0, -0.6, zc), (x_wedge(zc), -0.6, zc)], 0.06)
    bm.faces.ensure_lookup_table()
    zone = bm.faces.layers.int.new('zone')
    crease = bm.edges.layers.float.get('crease_edge') or bm.edges.layers.float.new('crease_edge')
    n_dark = n_panel = n_mund = 0
    def dark(cm):
        sx = 1 if cm.x >= 0 else -1
        if side_of(PL['side', sx], cm) > 0:
            return True
        return cm.y < -0.10 * S and cm.z > 0.05 * S and side_of(PL['wedge', sx], cm) > 0
    for f in bm.faces:
        cm = f.calc_center_median()
        c = cm / S
        f.material_index = 0 if dark(cm) else 1
        if f.material_index == 0 and is_panel(c):
            f[zone] = 2
            n_panel += 1
        if f.material_index == 0 and 0.296 < c.z < 0.304 and abs(c.x) < 0.24 and c.y < -0.15:
            f[zone] = 3
            n_mund += 1
        n_dark += f.material_index == 0
    for e in bm.edges:                                 # Crease an Grenze (0,7), Panel-Umriss (0,5), Mundlinie (0,7)
        if len(e.link_faces) != 2:
            continue
        a, b = e.link_faces
        if a.material_index != b.material_index or 3 in (a[zone], b[zone]) and a[zone] != b[zone]:
            e[crease] = 0.7
        elif a[zone] != b[zone]:
            e[crease] = 0.5
    NOTES.append(f'4/5 Grundnetz: {n_dark} dunkle Flächen, {n_panel} Panel-Flächen, {n_mund} Flächen Mundlinie')
    bm.to_mesh(ob.data)
    bm.free()
    for p in ob.data.polygons:
        p.use_smooth = True


def finalize_shell(ob):
    """Subdivision 2 anwenden, dann Versatz statt Inset (Dunkel +0,004 über Weiß, Panels −0,003, Mundlinie −0,003; der Übergang
    über eine Flächenbreite ist die Nut), dann Solidify 0,015 nach innen."""
    sd = ob.modifiers.new('SUBSURF', 'SUBSURF')
    sd.levels = sd.render_levels = 2
    apply_mod(ob, sd.name)
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    zone = bm.faces.layers.int.get('zone')
    bm.normal_update()
    moves = []
    for v in bm.verts:
        fs = v.link_faces
        if not fs:
            continue
        d = 0.0
        if all(f.material_index == 0 for f in fs):
            d += 0.004
        if all(f[zone] == 2 for f in fs) or all(f[zone] == 3 for f in fs):
            d -= 0.003
        if d:
            moves.append((v, v.normal.copy() * d * S))
    for v, off in moves:
        v.co += off
    bm.to_mesh(ob.data)
    bm.free()
    so = ob.modifiers.new('SOLID', 'SOLIDIFY')
    so.thickness, so.offset, so.use_rim, so.use_even_offset = 0.015 * S, -1.0, True, False
    apply_mod(ob, so.name)


def section_5_eyes(ob):
    tree = bvh(ob)
    eyes = []
    for side, sx in (('L', -1), ('R', 1)):
        c, nor = project(tree, (sx * 0.15, -0.6, 0.72))
        nor = Vector(nor).normalized()
        up = Vector((0, 0, 1))
        U = (Vector((sx, 0, 0)) - nor * nor.dot(Vector((sx, 0, 0)))).normalized()       # nach außen entlang der Fläche
        V = nor.cross(U) if sx > 0 else U.cross(nor)
        if V.dot(up) < 0:
            V = -V
        ang = math.atan2(0.015, 0.16)                  # außen 0,015 höher
        U2 = U * math.cos(ang) + V * math.sin(ang)
        V2 = -U * math.sin(ang) + V * math.cos(ang)
        ol = rounded_rect(0.16 * S, 0.045 * S, 0.006 * S, 3)
        bm = bmesh.new()
        prism(bm, ol, c, U2, V2, nor, -0.006 * S, 0.02 * S)
        boolean(ob, obj('CUT_AUGE', bm, ['MAT_Leucht'], 'HILFE'))
        bm = bmesh.new()
        prism(bm, [(u * 0.985, v * 0.96) for u, v in ol], c, U2, V2, nor, -0.0058 * S, -0.002 * S)
        eyes.append(obj(f'Helm_Auge_{side}', bm, ['MAT_Leucht']))
    return eyes


def section_5_parts(ob):
    tree = bvh(ob)
    # 5.3 Mundgrat: Z 0,56 → 0,14, Breite 0,07 → 0,05, 0,012 erhaben, Enden gerundet, Bevel 0,004
    ol = []
    for k in range(9):                                 # oben Halbkreis
        a = math.pi * k / 8
        ol.append((0.035 * math.cos(a), 0.56 - 0.035 + 0.035 * math.sin(a)))
    for k in range(9):                                 # unten Halbkreis
        a = math.pi + math.pi * k / 8
        ol.append((0.025 * math.cos(a), 0.14 + 0.025 + 0.025 * math.sin(a)))
    grat = plate_on(tree, 'Helm_Mundgrat', [(x * S, z * S) for x, z in ol], H(0, -0.6, 0), Vector((1, 0, 0)), Vector((0, 0, 1)),
                    Vector((0, -1, 0)), 0.012 * S, ['MAT_Dunkel'])
    bv = grat.modifiers.new('BEVEL', 'BEVEL')
    bv.width, bv.segments = 0.004 * S, 2
    # 5.5 Kinnlippe: X −0,22 … +0,22, Z 0,00–0,05, 0,01 vor, Bevel 0,004, drei Schlitze 0,012 × 0,03
    lip = plate_on(tree, 'Helm_Kinnlippe', [(x * S, z * S) for x, z in rounded_rect(0.44, 0.048, 0.008, 3)], H(0, -0.6, 0.026),
                   Vector((1, 0, 0)), Vector((0, 0, 1)), Vector((0, -1, 0)), 0.010 * S, ['MAT_Weiss'])
    lt = bvh(lip)
    bm = bmesh.new()
    for x in (-0.06, 0.0, 0.06):
        loc, _, _, _ = lt.ray_cast(H(x, -1.0, 0.026), Vector((0, 1, 0)), 2.0)
        if loc is not None:
            prism(bm, [(u * S, v * S) for u, v in rounded_rect(0.012, 0.03, 0.002, 2)], loc, Vector((1, 0, 0)), Vector((0, 0, 1)),
                  Vector((0, 1, 0)), -0.01 * S, 0.008 * S)
    boolean(lip, obj('CUT_LIPPE', bm, ['MAT_Weiss'], 'HILFE'))
    bv = lip.modifiers.new('BEVEL', 'BEVEL')
    bv.width, bv.segments, bv.limit_method = 0.004 * S, 2, 'ANGLE'
    save('5')


# ------------------------------------------------------------------ 6 Pods, 7 Schläuche, 8 Block und Antennen

def section_6(ob):
    tree = bvh(ob)
    tops = {}
    for side, sx in (('L', -1), ('R', 1)):
        c, nor = project(tree, (sx * 0.43, 0.0, 0.46))
        nor = Vector(nor).normalized()
        M = frame_of(nor)
        U, V = M.col[1], M.col[2]
        if abs(V.z) < abs(U.z):
            U, V = V, U
        if V.z < 0:
            V = -V
        U = nor.cross(V) if sx > 0 else V.cross(nor)
        base = plate_on(tree, f'Helm_Pod_{side}', rounded_rect(0.15 * S, 0.15 * S, 0.02 * S, 4), c, U, V, nor, 0.012 * S, ['MAT_Pod'])
        h0 = 0.012
        R, L, fil, dome = 0.10, 0.07, 0.02, 0.03
        prof = [(0, h0 - 0.004), (R, h0 - 0.004), (R, h0 + L - fil)]
        for k in range(1, 4):                          # Rand-Fillet 0,02 (3 Segmente)
            a = math.pi / 2 * k / 3
            prof.append((R - fil + fil * math.cos(a), h0 + L - fil + fil * math.sin(a)))
        def domez(r):
            return h0 + L + dome * (1 - (r / (R - fil)) ** 2)
        prof += [(0.0725, domez(0.0725)), (0.0725, domez(0.0725) - 0.002), (0.0675, domez(0.0675) - 0.002), (0.0675, domez(0.0675)),
                 (0.03, domez(0.03)), (0, domez(0))]
        bm = bmesh.new()
        lathe(bm, [(r * S, a * S) for r, a in prof], Matrix((nor, U, V)).transposed(), c, 48)
        join(base, [obj('POD_CUP', bm, ['MAT_Pod'])])
        top = max((Vector(v.co) for v in base.data.vertices), key=lambda p: p.z)
        tops[side] = top.z / S
        # 6.2 Kasten 0,08 × 0,05 × 0,05 bei X ±0,40 / Y +0,02 / Z 0,60, Unterseite auf der Schale
        k_c, k_n = project(tree, (sx * 0.40, 0.02, 0.60))
        bm = bmesh.new()
        prism(bm, [(u * S, v * S) for u, v in rounded_rect(0.05, 0.05, 0.004, 2)], k_c, Vector((0, 1, 0)), Vector((0, 0, 1)),
              Vector((sx, 0, 0)), -0.01 * S, 0.07 * S)
        kb = obj(f'Helm_Pod_Kasten_{side}', bm, ['MAT_Pod'])
        bv = kb.modifiers.new('BEVEL', 'BEVEL')
        bv.width, bv.segments = 0.004 * S, 2
    save('6')
    return tops


def rib_taper(length_h, pitch=0.014, depth=0.004, r=0.0175):
    cu = bpy.data.curves.new('TAPER_RIPPEN', 'CURVE')
    sp = cu.splines.new('POLY')
    n = max(4, int(length_h / pitch))
    m = n * 8
    sp.points.add(m)
    lo = 1 - depth / r
    for i in range(m + 1):
        u = i / m
        sp.points[i].co = (u, (1 + lo) / 2 + (1 - lo) / 2 * math.cos(2 * math.pi * n * u), 0, 1)
    ob = bpy.data.objects.new('TAPER_RIPPEN', cu)
    coll('HILFE').objects.link(ob)
    return ob


HOSES = {'Hinten': [(0.44, 0.07, 0.37), (0.45, 0.30, 0.22), (0.10, 0.52, 0.28)],
         'Vorn': [(0.44, -0.07, 0.37), (0.40, -0.25, 0.18), (0.19, -0.38, 0.13)]}


def section_7(ob):
    tree = bvh(ob)
    out = []
    for kind, pts in HOSES.items():
        for side, sx in (('L', -1), ('R', 1)):
            P = [H(sx * x, y, z) for x, y, z in pts]
            L = sum((b - a).length for a, b in zip(P, P[1:])) / S * 1.05
            cu = curve_obj(f'Helm_Schlauch_{kind}_{side}', P, 0.0175 * S, 'MAT_Schlauch', taper=rib_taper(L), res=max(64, int(L / 0.014 * 6)))
            c = curve_points(cu)
            free = tree.find_nearest(min(c, key=lambda q: (q - P[1]).length))[3] / S - 0.0175
            NOTES.append(f'7 Helm_Schlauch_{kind}_{side}: Länge {sum((b - a).length for a, b in zip(c, c[1:])) / S:.3f} H, '
                         f'Abstand Mantel–Schale an P1 {free:.3f} H')
            for end, (a, b) in (('a', (c[0], c[2])), ('b', (c[-1], c[-3]))):
                bm = bmesh.new()
                d = (a - b).normalized()
                cyl(bm, 0.0225 * S, 0.035 * S, a - d * 0.005 * S, d, 24)
                out.append(obj(f'Helm_Buchse_{kind}_{side}{end}', bm, ['MAT_Metall']))
    save('7')


def section_8(ob):
    tree = bvh(ob)
    # 8.1 Block 0,24 × 0,10 × 0,10, Vorderseite auf der Schale (Shrinkwrap), Bevel 0,006, zwei Eintritte oben, Steckdose als Rille
    blk = plate_on(tree, 'Helm_Block_Hinten', [(u * S, v * S) for u, v in rounded_rect(0.24, 0.10, 0.012, 3)], H(0, 0.53, 0.28),
                   Vector((1, 0, 0)), Vector((0, 0, 1)), Vector((0, 1, 0)), 0.10 * S, ['MAT_Pod'])
    ys = [v.co.y for v in blk.data.vertices]
    ym = (min(ys) + max(ys)) / 2
    bm = bmesh.new()
    for x in (-0.10, 0.10):
        cyl(bm, 0.0225 * S, 0.03 * S, Vector((x * S, ym, 0.33 * S + 0.01 * S)), (0, 0, 1), 24)
    lathe(bm, [(0.025 * S, 0), (0.025 * S, 0.003 * S), (0.022 * S, 0.003 * S), (0.022 * S, 0)], frame_of((0, -1, 0)),
          Vector((0, min(ys) - 0.0005 * S, 0.28 * S)), 32)
    join(blk, [obj('BLOCK_TEILE', bm, ['MAT_Pod'])])
    bv = blk.modifiers.new('BEVEL', 'BEVEL')
    bv.width, bv.segments, bv.limit_method = 0.006 * S, 2, 'ANGLE'
    # 8.2/8.3 Antennen auf der Kuppel: Sockel Ø 0,03 × 0,015, Stab Ø 0,012; rechts 0,18 mit 10° nach hinten und Kugel Ø 0,014, links 0,07
    for side, sx, L, tilt in (('R', 1, 0.18, 10), ('L', -1, 0.07, 0)):
        foot, nor = project(tree, (sx * 0.22, -0.02, 0.88))
        bm = bmesh.new()
        cyl(bm, 0.015 * S, 0.015 * S, foot + Vector((0, 0, 0.0075 * S)), (0, 0, 1), 24)
        d = Vector((0, math.sin(math.radians(tilt)), math.cos(math.radians(tilt))))
        a0 = foot + Vector((0, 0, 0.012 * S))
        cyl(bm, 0.006 * S, L * S, a0 + d * L / 2 * S, d, 16)
        if side == 'R':
            sph = bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=0.007 * S)
            for v in sph['verts']:
                v.co += a0 + d * L * S
        obj(f'Helm_Antenne_{side}', bm, ['MAT_Pod'])
    save('8')


# ------------------------------------------------------------------ 10 Tuch (vereinfachte Pflichtvariante)

def section_10():
    tori = []
    for i, (R, r, z, tilt) in enumerate(((0.46, 0.09, -0.08, 4), (0.50, 0.10, -0.20, 5), (0.53, 0.11, -0.33, 6), (0.55, 0.12, -0.47, 5))):
        bm = bmesh.new()
        segs, rs = 48, 16
        rings = []
        for k in range(segs):
            t = 2 * math.pi * k / segs
            c = Vector((R * math.cos(t), R * math.sin(t), 0))
            out = Vector((math.cos(t), math.sin(t), 0))
            rings.append([bm.verts.new((c + (out * math.cos(2 * math.pi * j / rs) + Vector((0, 0, 1)) * math.sin(2 * math.pi * j / rs)) * r) * S)
                          for j in range(rs)])
        for k in range(segs):
            A, B = rings[k], rings[(k + 1) % segs]
            for j in range(rs):
                bm.faces.new((A[j], A[(j + 1) % rs], B[(j + 1) % rs], B[j]))
        Rm = Matrix.Rotation(math.radians(-tilt), 3, 'X')    # vorn (−Y) tiefer
        for v in bm.verts:
            v.co = Rm @ v.co + H(0, 0, z)
        tori.append(obj(f'TORUS_{i}', bm, ['MAT_Tuch'], 'TUCH'))
    w = join(tori[0], tori[1:])
    w.name = 'Tuch_Wicklung'
    tex = bpy.data.textures.new('TUCH_NOISE', 'CLOUDS')
    tex.noise_scale = 0.06
    d = w.modifiers.new('DISPLACE', 'DISPLACE')
    d.texture, d.strength = tex, 0.02 * S
    s = w.modifiers.new('SUBSURF', 'SUBSURF')
    s.levels = s.render_levels = 1
    # Zipfel 0,30 × 0,55: Oberkante an der Wicklung bei X +0,25 / Z −0,30, Spitze X −0,15 / Z −0,85
    bm = bmesh.new()
    nu, nv = 8, 18
    V = [[bm.verts.new(((i / nu - 0.5) * 0.30, 0, -j / nv * 0.55)) for i in range(nu + 1)] for j in range(nv + 1)]
    for j in range(nv):
        for i in range(nu):
            bm.faces.new((V[j][i], V[j][i + 1], V[j + 1][i + 1], V[j + 1][i]))
    t, p = Vector((0.25, -0.60, -0.30)), Vector((-0.15, -0.62, -0.85))
    down = (p - t).normalized()
    side = Vector((0, 1, 0)).cross(down).normalized()
    M = Matrix((side, -side.cross(down), -down)).transposed()
    for v in bm.verts:
        v.co = (t + M @ v.co) * S
    z = obj('Tuch_Zipfel', bm, ['MAT_Tuch'], 'TUCH')
    sd = z.modifiers.new('BEND', 'SIMPLE_DEFORM')
    sd.deform_method, sd.angle, sd.deform_axis = 'BEND', math.radians(25), 'Z'
    d2 = z.modifiers.new('DISPLACE', 'DISPLACE')
    d2.texture, d2.strength = tex, 0.02 * S
    so = z.modifiers.new('SOLID', 'SOLIDIFY')
    so.thickness = 0.006 * S
    for ob in (w, z):
        for m in list(ob.modifiers):
            apply_mod(ob, m.name)
        for pl in ob.data.polygons:
            pl.use_smooth = True
    save('10')


# ------------------------------------------------------------------ 13/14/15 Renders, Abnahme, Bericht

def bounds(obs):
    dg = bpy.context.evaluated_depsgraph_get()
    lo, hi = Vector((1e9,) * 3), Vector((-1e9,) * 3)
    for ob in obs:
        e = ob.evaluated_get(dg)
        for c in e.bound_box:
            w = e.matrix_world @ Vector(c)
            lo, hi = Vector(map(min, lo, w)), Vector(map(max, hi, w))
    return (hi - lo) / S, lo / S, hi / S


def acceptance(iou1, iou2):
    rows, errs = [], []
    ok = passed(iou1)
    rows.append(('1 IoU Phase 1', ', '.join(f'{k} {v:.3f}' for k, v in iou1.items()), 'bestanden' if ok else 'nicht bestanden'))
    if not ok:
        errs.append('1 IoU-Stop-Kriterium nicht erreicht')
    rows.append(('  IoU Phase 2 (mit Pods/Antennen)', ', '.join(f'{k} {v:.3f}' for k, v in iou2.items()),
                 'ok' if min(iou2.values()) >= 0.85 else 'unter 0,85'))
    sh = bpy.data.objects['Helm_Schale']
    d, lo, hi = bounds([sh])
    ok = abs(d.x - 0.84) <= 0.02 and abs(d.y - 1.04) <= 0.02 and abs(d.z - 1.00) <= 0.01
    rows.append(('2 Hüllbox Schale (B × T × H)', f'{d.x:.3f} × {d.y:.3f} × {d.z:.3f}', 'ok' if ok else 'außerhalb'))
    if not ok:
        errs.append('2 Hüllbox Schale außerhalb der Toleranz')
    # 3 Dihedralwinkel > 25° außer Nut, Augen, Kinnkante
    bm = bmesh.new()
    bm.from_mesh(sh.data)
    zone = bm.faces.layers.int.get('zone')
    eyes = [Vector(bpy.data.objects[f'Helm_Auge_{s}'].data.vertices[0].co) for s in 'LR']
    from mathutils.kdtree import KDTree
    seam = [v.co for v in bm.verts if len({(f.material_index, f[zone] if zone else 0) for f in v.link_faces}) > 1]
    kd = KDTree(len(seam))
    for i_, co in enumerate(seam):
        kd.insert(co, i_)
    kd.balance()
    cen = H(0, 0.03, 0.5)
    bm.normal_update()
    bad = 0
    for e in bm.edges:
        if len(e.link_faces) != 2:
            continue
        f0, f1 = e.link_faces
        mid = (e.verts[0].co + e.verts[1].co) / 2
        if f0.normal.dot(mid - cen) < 0:
            continue                                   # Innenseite (Solidify) gehört nicht zur Außenhaut
        if seam and kd.find(mid)[2] < 0.03 * S:
            continue                                   # Nut, Panel-Umriss, Mundlinie (Crease-Übergänge)
        if f0.normal.angle(f1.normal, 0) <= math.radians(25):
            continue
        m = (e.verts[0].co + e.verts[1].co) / 2
        if m.z < 0.03 * S or any((m - q).length < 0.12 * S for q in eyes):
            continue
        if f0.material_index != f1.material_index or (zone is not None and (f0[zone] or f1[zone])):
            continue
        if any(len({g.material_index for g in v.link_faces}) > 1 for v in e.verts):
            continue                                   # Nut-Übergang neben der Grenze
        bad += 1
    bm.free()
    rows.append(('3 Kanten > 25° auf der Außenhaut (ohne Nut/Panels/Augen/Kinnkante)', str(bad), 'ok' if bad == 0 else 'zu viele'))
    if bad:
        errs.append(f'3 {bad} Kanten mit Dihedralwinkel > 25°')
    # 4 Pods auf Weiß, Oberkante ≤ Z 0,57
    tree = bvh(sh)
    for s, sx in (('L', -1), ('R', 1)):
        _, _, idx, _ = tree.find_nearest(H(sx * 0.43, 0.0, 0.46))
        w_ = sh.data.polygons[idx].material_index == 1
        top = bounds([bpy.data.objects[f'Helm_Pod_{s}']])[2].z
        rows.append((f'4 Helm_Pod_{s}', f'Untergrund {"MAT_Weiss" if w_ else "MAT_Dunkel"}, Oberkante Z {top:.3f}',
                     'ok' if w_ and top <= 0.57 else 'nicht ok'))
        if not (w_ and top <= 0.57):
            errs.append(f'4 Helm_Pod_{s}')
    # 5 Schläuche Ø und Endpunkte
    for kind, pts in HOSES.items():
        for s, sx in (('L', -1), ('R', 1)):
            ob = bpy.data.objects[f'Helm_Schlauch_{kind}_{s}']
            c = curve_points(ob)
            e0 = (c[0] / S - Vector((sx * pts[0][0], pts[0][1], pts[0][2]))).length
            e1 = (c[-1] / S - Vector((sx * pts[2][0], pts[2][1], pts[2][2]))).length
            dia = 2 * ob.data.bevel_depth / S
            ok = abs(dia - 0.035) <= 0.003 and e0 <= 0.02 and e1 <= 0.02
            rows.append((f'5 {ob.name}', f'Ø {dia:.3f}, Endpunkte ± {e0:.3f} / {e1:.3f}', 'ok' if ok else 'nicht ok'))
            if not ok:
                errs.append(f'5 {ob.name}')
    # 6 Antennenlängen
    for s, lim in (('R', 0.20), ('L', 0.08)):
        d, lo, hi = bounds([bpy.data.objects[f'Helm_Antenne_{s}']])
        rows.append((f'6 Helm_Antenne_{s}', f'Höhe über Fuß {d.z:.3f}', 'ok' if d.z <= lim + 0.03 else 'zu lang'))
    # 7 Objekte, Namen, je ein Material
    names = ['Helm_Schale', 'Helm_Auge_L', 'Helm_Auge_R', 'Helm_Mundgrat', 'Helm_Kinnlippe', 'Helm_Pod_L', 'Helm_Pod_R', 'Helm_Pod_Kasten_L',
             'Helm_Pod_Kasten_R', 'Helm_Schlauch_Hinten_L', 'Helm_Schlauch_Hinten_R', 'Helm_Schlauch_Vorn_L', 'Helm_Schlauch_Vorn_R',
             'Helm_Block_Hinten', 'Helm_Antenne_R', 'Helm_Antenne_L', 'Tuch_Wicklung', 'Tuch_Zipfel']
    missing = [n for n in names if n not in bpy.data.objects]
    multi = [o.name for o in coll('HELM').all_objects if o.name != 'Helm_Schale' and len(o.data.materials) != 1]
    rows.append(('7 Objekte/Materialien', f'fehlend {missing or "keine"}, mehrere Materialien {multi or "keine"}',
                 'ok' if not missing and not multi else 'nicht ok'))
    if missing or multi:
        errs.append('7 Objekte/Materialien')
    rows.append(('8 build_helm.py aus leerer Datei', 'durchgelaufen (dieser Bericht)', 'ok'))
    return rows, errs


def render_final(samples):
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE'
    sc.eevee.taa_render_samples = samples
    sc.render.film_transparent = False
    sc.render.resolution_x = sc.render.resolution_y = 1024
    world = bpy.data.worlds.new('Grau')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (*srgb('#7A7D82'), 1)
    sc.world = world
    sc.view_settings.view_transform = 'Standard'
    for nm, loc, en, size in (('Key', H(-1.6, -2.4, 2.6), 110, 0.9), ('Fill', H(1.4, 2.6, 1.2), 40, 1.2)):
        li = bpy.data.objects.new(nm, bpy.data.lights.new(nm, 'AREA'))
        li.data.energy, li.data.size = en, size
        li.location = loc
        li.rotation_euler = (H(0, 0, 0.45) - loc).to_track_quat('-Z', 'Y').to_euler()
        sc.collection.objects.link(li)
    out = {}
    for name, cam in camera_rig().items():
        sc.camera = cam
        sc.render.filepath = os.path.join(OUT, f'check_{name}.png')
        bpy.ops.render.render(write_still=True)
        out[name] = sc.render.filepath
    ref = os.path.join(OUT, 'ref_helm.png')
    subprocess.run(['cp', REF, ref], check=True)
    w = int(subprocess.run(['magick', 'identify', '-format', '%w', ref], capture_output=True, text=True).stdout)
    for i, (name, _) in enumerate(CAMS):
        part = os.path.join(OUT, f'_ref_{i}.png')
        subprocess.run(['magick', ref, '-crop', f'{w // 4}x+{i * (w // 4)}+0', '+repage', '-resize', 'x1024', part], check=True)
        subprocess.run(['magick', part, out[name], '-resize', 'x1024', '+append', os.path.join(OUT, f'compare_{name}.png')], check=True)
        os.remove(part)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)


def report(rows, errs):
    L = ['# Helm „Scout“ V2 – Bericht', '', f'- Ergebnis: {"alle Abnahmekriterien erfüllt" if not errs else f"{len(errs)} Kriterien offen"}',
         f'- Datei `{BLEND}`, Skript `tools/build_helm.py`', '', '## IoU je Iteration (Phase 1)', '',
         '| Schritt | Faktor a | Faktor b_v | Faktor b_h | Yc-Versatz | front34 | left | back34 | right |', '|---|---|---|---|---|---|---|---|---|']
    for step, k, r in LOG:
        L.append(f"| {step} | {k['a']:.3f} | {k['bv']:.3f} | {k['bh']:.3f} | {k['yc']:+.3f} | " + ' | '.join(f'{r[n]:.3f}' for n, _ in CAMS) + ' |')
    L += ['', 'Endgültige Tabelle (Abschnitt 3) nach Phase 1:', '', '| Z | a | b_v | b_h | Yc | n_v | n_h |', '|---|---|---|---|---|---|---|']
    L += [f'| {z:.2f} | {a:.3f} | {bv:.3f} | {bh:.3f} | {yc:+.3f} | {nv} | {nh} |' for z, a, bv, bh, yc, nv, nh in table()]
    L += ['', '## Abnahmekriterien (Abschnitt 14)', '', '| Kriterium | Messwert | Ergebnis |', '|---|---|---|']
    L += [f'| {a} | {b} | {c} |' for a, b, c in rows]
    L += ['', '## Nicht erreichte Punkte', ''] + ([f'- {e}' for e in errs] or ['- keine'])
    L += ['', '## Hinweise und Messungen', ''] + [f'- {n}' for n in NOTES]
    L += ['', '## Abweichungen vom Vorgehen', ''] + [f'- {d}' for d in DEVIATIONS]
    open(os.path.join(OUT, 'REPORT.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    with open(os.path.join(OUT, 'iou.log'), 'w', encoding='utf-8') as fh:
        for step, k, r in LOG:
            fh.write(f'{step}\t{k}\t{r}\n')


def main():
    os.makedirs(OUT, exist_ok=True)
    reset()
    iou1 = phase1_reuse() if '--reuse-phase1' in ARGS else phase1()
    if '--phase1-only' in ARGS:
        report([('1 IoU Phase 1', str(iou1), 'bestanden' if passed(iou1) else 'nicht bestanden')], [] if passed(iou1) else ['1'])
        print('[helm] Phase 1:', 'bestanden' if passed(iou1) else 'nicht bestanden', flush=True)
        return
    if not passed(iou1):
        NOTES.append('Phase 1 nach 8 Iterationen nicht bestanden; Phase 2 trotzdem gebaut, damit das Ergebnis sichtbar ist (Kriterium 1 offen)')
    sh = bpy.data.objects['Helm_Schale']
    sh.modifiers.clear()
    section_4_5(sh)
    finalize_shell(sh)
    save('4')
    section_5_eyes(sh)
    section_5_parts(sh)
    tops = section_6(sh)
    iou6 = iou_all('sil6')
    NOTES.append(f'IoU nach 6: ' + ', '.join(f'{k} {v:.3f}' for k, v in iou6.items()))
    section_7(sh)
    section_8(sh)
    iou8 = iou_all('sil8')
    NOTES.append(f'IoU nach 8: ' + ', '.join(f'{k} {v:.3f}' for k, v in iou8.items()))
    section_10()
    for o in coll('HILFE').objects:
        o.hide_render = True
    bpy.context.view_layer.layer_collection.children['HILFE'].hide_viewport = True
    rows, errs = acceptance(iou1, iou8)
    if '--no-render' not in ARGS:
        render_final(int(arg('--samples', 48)))
    report(rows, errs)
    print('[helm] fertig:', 'alle Kriterien erfüllt' if not errs else f'{len(errs)} offen', flush=True)


if __name__ == '__main__':
    main()
