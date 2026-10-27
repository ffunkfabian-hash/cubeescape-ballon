"""Helm „Scout“: Hard-Surface-Nachbau nach der Spezifikation des Nutzers (27.10.2026), Blender ≥ 4.x, nur Bordmittel.

  blender -b --factory-startup -P tools/helm_scout.py -- [--out DIR] [--ref PNG] [--no-cloth] [--no-render] [--samples N]

Alle Maße der Spezifikation sind in H (Helmhöhe = 0,30 m) angegeben und werden hier mit S = 0,30 in Meter umgerechnet. Koordinaten:
+Z oben, −Y vorn, +X rechts vom Träger, Z = 0 Kinnunterkante, Y = 0 Ohrachse. Ergebnis in DIR (Standard
~/Library/Caches/CubeEscapeBallon/out/helm_scout): helm_scout.blend (nach jedem Abschnitt A–H gespeichert), check_<cam>.png,
compare_<cam>.png (Render neben dem passenden Viertel von ref_helm.png), REPORT.md (Abnahme J, Hüllmaße Ist/Soll, Abweichungen).

Abweichungen vom vorgegebenen Vorgehen stehen in DEVIATIONS und landen im Bericht.
"""
import math
import os
import subprocess
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

S = 0.30
ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []


def arg(name, default=None):
    return ARGS[ARGS.index(name) + 1] if name in ARGS else default


OUT = os.path.expanduser(arg('--out', '~/Library/Caches/CubeEscapeBallon/out/helm_scout'))
REF = os.path.expanduser(arg('--ref', '~/Library/Caches/CubeEscapeBallon/refs/robot-helm-mil.png'))
BLEND = os.path.join(OUT, 'helm_scout.blend')
DEVIATIONS = [
    'Grundkörper als konvexe Hülle dichter Querschnitte (A1–A3) statt UV-Sphere + Lattice + Bisect + Make Planar: die Hülle liefert '
    'ebene Facetten direkt (A4) und trifft die Profilpunkte exakt; koplanare Dreiecke mit Limited Dissolve (1,5°) zu N-Gons zusammengefasst',
    'Symmetrie direkt konstruiert (beide Seiten aus denselben Funktionen) statt Mirror-Modifier: Booleans, Raycasts und Shrinkwrap brauchen '
    'beide Seiten; Paare werden in J3 geprüft',
    'Shrinkwrap von Pod-Sockel und Block-Grundplatte per Raycast auf die Haube (gleiche Wirkung wie der Modifier, ohne Zusatzobjekt)',
    'Kabel an Stecker (E3) und Kurzkabel der Box2 (E4) sind in Hierarchie nicht benannt; sie sind in Helm_Pod_Stecker_* bzw. '
    'Helm_Pod_Box2_R eingefügt (join), damit J1 keine zusätzlichen Objekte findet',
    'Rastelemente (D) sind Teil von Helm_Kinnteil (zweites Material MAT_Metall), da sie in der Hierarchie nicht als Objekt stehen',
    'Riffelung der Schläuche über ein Taper-Objekt (Radius 1,0/0,8 alle 0,012 H) statt Torus-Array; Taper- und Hilfsobjekte liegen in der '
    'ausgeblendeten Collection HELM_HILFE',
    'Sensorfenster (C4, G2.4) als Quader ohne Eckradius R 0,004 (= 1,2 mm): der gerundete Schneidkörper ließ den exakten Boolean '
    'auf der Haube von 1 157 auf 16 142 Flächen anwachsen und blieb beim zweiten Fenster hängen',
    'Visier: Plattendicke 0,026 (nicht vorgegeben; 0,022 ließ die Leuchtschlitze zerfallen, 0,03 ergab Tiefe +8,6 %); ohne Bevel-Modifier, '
    'weil er auf den Boolean-Resten der Schlitze 0,03 H über die Oberkante schoss',
    'Exakte Booleans mit use_self; Haube/Kinnteil vor den Schnitten trianguliert, danach Reparatur (Doppelflächen, Splitter, Kleinstlöcher) '
    'und Limited Dissolve 0,5° zurück zu ebenen Flächen; Nut N3 endet 6 % vor der Sockelkante (dort blieb sonst ein Boolean-Loch)',
    'Schläuche: P2 liegt bei X ±0,17 (Schlaucheintritt an der Block-Grundplatte, die nur 0,30 breit ist) statt X ±0,45; P0/P1 wie vorgegeben',
]
NOTES = ['Helm_Rueckenplatte steht in der Hierarchie, ist nach M8 aber kein eigenes Objekt: nur als umlaufende Nut auf der Haube (F4)',
         'K Vergleich, drei Iterationen: (1) Kameraabstand korrigiert, (2) Unterseite des Hinterkopfs war beim Öffnen des Halses mitgelöscht, '
         '(3) Non-Manifold-Reste der Booleans repariert. Die Gesamtform weicht sichtbar von der Referenz ab (Dachfacetten statt runder '
         'Kuppel, hohes kastiges Kinnteil statt schmalem Kieferband): die Spezifikationsmaße A1–A3 und B sind maßgeblich, eine Korrektur '
         'würde sie verletzen']


def H(*c):
    return Vector(c) * S


# ------------------------------------------------------------------ Szene, Material, Hilfen

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.scale_length = 1.0
    root = sc.collection
    for nm in ('HELM', 'HELM_HILFE'):
        c = bpy.data.collections.new(nm)
        root.children.link(c)
    tuch = bpy.data.collections.new('TUCH')
    bpy.data.collections['HELM'].children.link(tuch)


def coll(name):
    return bpy.data.collections[name]


def srgb(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)


MATS = {'MAT_Haube': ('#2A2C2E', 0.55, 0.2), 'MAT_Kinn': ('#D8D6D0', 0.65, 0.0), 'MAT_Visier': ('#1E1F21', 0.45, 0.4),
        'MAT_Pod': ('#3A3C3E', 0.50, 0.5), 'MAT_Gummi': ('#1A1A1A', 0.35, 0.0), 'MAT_Metall': ('#6E6E6E', 0.30, 1.0),
        'MAT_Tuch': ('#8C8780', 0.90, 0.0)}


def mat(name):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    if name == 'MAT_Emission':
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        out = nt.nodes.new('ShaderNodeOutputMaterial')
        em = nt.nodes.new('ShaderNodeEmission')
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


def obj(name, bm, mats, collection='HELM'):
    me = bpy.data.meshes.new(name)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    coll(collection).objects.link(ob)
    for m in mats:
        ob.data.materials.append(mat(m) if isinstance(m, str) else m)
    return ob


def ctx(ob):
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)


def apply_mod(ob, name):
    ctx(ob)
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        bpy.ops.object.modifier_apply(modifier=name)


def boolean(ob, cutter, op='DIFFERENCE', keep=False, self_=True):
    import time
    t0 = time.time()
    m = ob.modifiers.new('BOOL', 'BOOLEAN')
    m.operation, m.solver, m.object = op, 'EXACT', cutter
    m.use_self = self_
    m.use_hole_tolerant = True
    m.material_mode = 'TRANSFER'
    print(f'[scout] Boolean {op} {ob.name} − {cutter.name} ({len(ob.data.polygons)}/{len(cutter.data.polygons)} Flächen) …', flush=True)
    apply_mod(ob, m.name)
    nm0 = nonmanifold(ob)
    cleanup(ob, 0.0001)
    print(f'[scout]   {time.time() - t0:.1f} s → {len(ob.data.polygons)} Flächen, Non-Manifold {nm0} roh, {nonmanifold(ob)} bereinigt', flush=True)
    if not keep:
        bpy.data.objects.remove(cutter, do_unlink=True)


def cleanup(ob, dist=0.0005, tri=False):
    """Merge by Distance (0,0005 H), entartete Kanten/Flächen auflösen, Normalen neu; tri: vorher triangulieren (exakte Booleans
    auf fast-ebenen N-Gons zerrissen die Haube: 207 000 Flächen, Ecken bis 32 H entfernt)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist * S)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=bm.edges)
    if tri:
        bmesh.ops.triangulate(bm, faces=bm.faces, quad_method='BEAUTY', ngon_method='BEAUTY')
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()


def nonmanifold(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    n = sum(1 for e in bm.edges if not e.is_manifold)
    bm.free()
    return n


def join(target, others):
    ctx(target)
    for o in others:
        o.select_set(True)
    with bpy.context.temp_override(active_object=target, selected_editable_objects=[target] + others,
                                   selected_objects=[target] + others):
        bpy.ops.object.join()
    return target


def bvh(ob):
    return BVHTree.FromObject(ob, bpy.context.evaluated_depsgraph_get())


def hit(tree, origin, direction):
    loc, nor, _, _ = tree.ray_cast(origin, Vector(direction).normalized(), 10.0)
    return loc, nor


def save(step):
    os.makedirs(OUT, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print(f'[scout] {step} gespeichert', flush=True)


# ------------------------------------------------------------------ Grundformen (bmesh, Maße in Metern)

def add_box(bm, center, size, R=None, mat_index=0):
    R = R or Matrix.Identity(3)
    geo = bmesh.ops.create_cube(bm, size=1.0)['verts']
    for v in geo:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
        v.co = R @ v.co + Vector(center)
    for f in {f for v in geo for f in v.link_faces}:
        f.material_index = mat_index
    return geo


def lathe(bm, prof, axis_m, origin, segs=48, mat_index=0, cap=True):
    """Drehkörper: prof = [(r, a)] entlang der lokalen Achse a (Achse = Spalte 0 von axis_m), r radial; Enden mit r = 0 schließen."""
    ax, u, w = axis_m.col[0], axis_m.col[1], axis_m.col[2]
    rings = []
    for r, a in prof:
        if r <= 1e-9:
            rings.append([bm.verts.new(Vector(origin) + ax * a)])
            continue
        rings.append([bm.verts.new(Vector(origin) + ax * a + (u * math.cos(t) + w * math.sin(t)) * r)
                      for t in (2 * math.pi * k / segs for k in range(segs))])
    for A, B in zip(rings, rings[1:]):
        if len(A) == 1 and len(B) == 1:
            continue
        for k in range(segs):
            k2 = (k + 1) % segs
            if len(A) == 1:
                f = bm.faces.new((A[0], B[k2], B[k]))
            elif len(B) == 1:
                f = bm.faces.new((A[k], A[k2], B[0]))
            else:
                f = bm.faces.new((A[k], A[k2], B[k2], B[k]))
            f.material_index = mat_index
    if cap:
        for ring, flip in ((rings[0], True), (rings[-1], False)):
            if len(ring) > 1:
                f = bm.faces.new(ring[::-1] if flip else ring)
                f.material_index = mat_index
    return rings


def frame_of(axis):
    a = Vector(axis).normalized()
    h = Vector((0, 0, 1)) if abs(a.z) < 0.9 else Vector((1, 0, 0))
    u = a.cross(h).normalized()
    w = a.cross(u)
    return Matrix((a, u, w)).transposed()


def cyl(bm, r, length, center, axis, segs=32, mat_index=0):
    M = frame_of(axis)
    return lathe(bm, [(0, -length / 2), (r, -length / 2), (r, length / 2), (0, length / 2)], M, Vector(center) - 0 * M.col[0],
                 segs, mat_index, cap=False)


def rounded_rect(w, h, r, n=6):
    """Umriss (u, v) eines Rechtecks w × h mit Eckradius r, gegen den Uhrzeigersinn."""
    pts = []
    for cu, cv, a0 in ((w / 2 - r, h / 2 - r, 0), (-(w / 2 - r), h / 2 - r, 90), (-(w / 2 - r), -(h / 2 - r), 180), (w / 2 - r, -(h / 2 - r), 270)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cu + r * math.cos(a), cv + r * math.sin(a)))
    return pts


def prism(bm, outline, depth, origin, U, V, N, mat_index=0):
    """Prisma: Umriss in der Ebene (U, V) bei origin, Tiefe entlang N (beide Richtungen symmetrisch: 0 … depth)."""
    a = [bm.verts.new(Vector(origin) + U * u + V * v) for u, v in outline]
    b = [bm.verts.new(Vector(origin) + U * u + V * v + N * depth) for u, v in outline]
    n = len(outline)
    faces = [bm.faces.new(a[::-1]), bm.faces.new(b)]
    for k in range(n):
        k2 = (k + 1) % n
        faces.append(bm.faces.new((a[k], a[k2], b[k2], b[k])))
    for f in faces:
        f.material_index = mat_index
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return a, b


# ------------------------------------------------------------------ A Grundkörper

def arc(p0, p1, R, n, inner):
    """Kreisbogen von p0 nach p1 (y, z) mit Radius R; inner = Richtung des Mittelpunkts (+1/−1 um die Sehne)."""
    p0, p1 = Vector(p0), Vector(p1)
    m = (p0 + p1) / 2
    d = (p1 - p0)
    L = d.length
    h = math.sqrt(max(R * R - (L / 2) ** 2, 0))
    perp = Vector((d.y, -d.x)).normalized() * inner
    c = m + perp * h
    a0, a1 = math.atan2(p0.y - c.y, p0.x - c.x), math.atan2(p1.y - c.y, p1.x - c.x)
    da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
    return [(c.x + R * math.cos(a0 + da * t / n), c.y + R * math.sin(a0 + da * t / n)) for t in range(n + 1)]


# A1 Seitenprofil (Y, Z)
FRONT = arc((0.05, 1.00), (-0.42, 0.78), 0.55, 12, 1) + [(-0.47, 0.60), (-0.48, 0.28), (-0.38, 0.00)]
BACK = [(0.05, 1.00), (0.30, 0.92)] + arc((0.30, 0.92), (0.55, 0.45), 0.45, 12, 1)[1:] + [(0.40, 0.18), (0.15, 0.05), (-0.38, 0.00)]


def interp_z(chain, z):
    P = sorted(chain, key=lambda p: p[1])
    if z <= P[0][1]:
        return P[0][0]
    for (y0, z0), (y1, z1) in zip(P, P[1:]):
        if z0 <= z <= z1:
            return y0 + (y1 - y0) * (z - z0) / max(z1 - z0, 1e-9)
    return P[-1][0]


def lerp_tab(tab, z):
    for (z0, v0), (z1, v1) in zip(tab, tab[1:]):
        if z0 <= z <= z1:
            return v0 + (v1 - v0) * (z - z0) / (z1 - z0)
    return tab[0][1] if z < tab[0][0] else tab[-1][1]


# A2 Frontprofil (volle Breite) und Breite der ebenen Front (A3: 0,60 an der Stirnkante)
WIDTH = [(0.0, 0.64), (0.08, 0.66), (0.30, 0.78), (0.55, 0.85), (0.78, 0.78), (0.92, 0.62), (1.0, 0.56)]
FRONTW = [(0.0, 0.46), (0.28, 0.56), (0.60, 0.64), (0.78, 0.60), (0.92, 0.40), (1.0, 0.30)]


def section(z):
    """Querschnitt (x, y) bei z, beide Seiten (A3: Frontecken ≈ R 0,08 als 45°-Eckfläche, breiteste Stelle Y +0,10, hinten rund
    R ≈ 0,40 mit leichtem Mittelgrat); im Kinnbereich Front gewölbt (D: Radius 0,6)."""
    yf, yb = interp_z(FRONT, z), interp_z(BACK, z)
    if yb - yf < 1e-4:
        W = lerp_tab(WIDTH, z) / 2
        return [(x, yf) for x in (-W, W)]
    W = lerp_tab(WIDTH, z) / 2
    fw = min(lerp_tab(FRONTW, z) / 2, W - 0.02)
    pts = []
    for k in range(7):                                 # Front (im Kinnbereich mit Radius 0,6 gewölbt)
        x = -fw + 2 * fw * k / 6
        bulge = (0.6 - math.sqrt(0.36 - x * x)) if z < 0.33 else 0.0
        pts.append((x, yf + bulge))
    yc = min(yf + (W - fw) + 0.02, max(0.10, yf + 0.02))   # Ende der 45°-Eckfläche
    ym = max(0.10, yc)
    for sx in (-1, 1):
        pts += [(sx * (fw + 0.6 * (W - fw)), yf + 0.6 * (W - fw)), (sx * (W - 0.004), yc), (sx * W, ym)]
        rb = max(yb - ym, 0.0)
        for k in range(1, 10):                         # hinten rund
            t = math.pi / 2 * k / 10
            pts.append((sx * W * math.cos(t), ym + rb * math.sin(t)))
    pts.append((0.0, yb + 0.006))                      # leichter Mittelgrat hinten
    return pts


def build_mass():
    bm = bmesh.new()
    zs = sorted({round(z / 100, 3) for z in range(0, 101, 2)} | {p[1] for p in FRONT + BACK})
    for z in zs:
        for x, y in section(z):
            bm.verts.new(H(x, y, z))
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.0005 * S)
    res = bmesh.ops.convex_hull(bm, input=list(bm.verts))
    bmesh.ops.delete(bm, geom=list({g for g in res['geom_interior'] + res['geom_unused'] if isinstance(g, bmesh.types.BMVert)}), context='VERTS')
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.5), verts=list(bm.verts), edges=list(bm.edges))
    nm = sum(1 for e in bm.edges if not e.is_manifold)
    print(f'[scout] Masse: {len(bm.verts)} Ecken, {len(bm.faces)} Flächen, {nm} Non-Manifold-Kanten', flush=True)
    return obj('MASSE', bm, ['MAT_Haube'], 'HELM_HILFE')


def z_split(y):
    """B Trennlinie (Seitenansicht)."""
    return lerp_tab([(-1.0, 0.28), (-0.40, 0.28), (-0.10, 0.32), (0.20, 0.40), (0.35, 0.38), (1.0, 0.38)], y)


def split_cutter():
    """Raum unterhalb der Trennlinie bis Y +0,375 (Kinnteil), als Prisma über die ganze Breite."""
    bm = bmesh.new()
    yz = [(-0.8, -0.2), (0.375, -0.2), (0.375, 0.38), (0.35, 0.38), (0.20, 0.40), (-0.10, 0.32), (-0.40, 0.28), (-0.8, 0.28)]
    prism(bm, [(y * S, z * S) for y, z in yz], 1.2 * S, H(-0.6, 0, 0), Vector((0, 1, 0)), Vector((0, 0, 1)), Vector((1, 0, 0)), mat_index=0)
    return obj('CUT_SPLIT', bm, ['MAT_Kinn'], 'HELM_HILFE')


def hollow(ob, drop):
    """Öffnungen entfernen (drop(face) → True) und mit Solidify 0,015 nach innen eine Wand bilden (Rand innen)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if drop(f)], context='FACES')
    bm.to_mesh(ob.data)
    bm.free()
    m = ob.modifiers.new('SOLID', 'SOLIDIFY')
    m.thickness, m.offset, m.use_rim, m.use_even_offset = 0.015 * S, -1.0, True, True
    apply_mod(ob, m.name)


def section_A_B():
    mass = build_mass()
    kin = mass.copy()
    kin.data = mass.data.copy()
    coll('HELM').objects.link(kin)
    kin.name = 'Helm_Kinnteil'
    hau = mass
    coll('HELM').objects.link(hau)
    coll('HELM_HILFE').objects.unlink(hau)
    hau.name = 'Helm_Haube'
    save('A')
    cut = split_cutter()
    boolean(hau, cut, 'DIFFERENCE', keep=True)
    boolean(kin, cut, 'INTERSECT')
    for ob, m in ((hau, 'MAT_Haube'), (kin, 'MAT_Kinn')):
        cleanup(ob)
    # Kinnteil 0,02 entlang der Normalen nach innen (Shrink/Fatten), Unterkante: Lippe 0,03 unter 45° (Fase der Kinnkante)
    bm = bmesh.new()
    bm.from_mesh(kin.data)
    bottom = [e for e in bm.edges if all(v.co.z < 0.004 * S for v in e.verts) and e.calc_length() > 0.01 * S
              and all(v.co.y < -0.30 * S for v in e.verts)]
    if bottom:
        bmesh.ops.bevel(bm, geom=bottom, offset=0.03 * S, segments=1, affect='EDGES', profile=0.5)
    bm.normal_update()
    for v in bm.verts:
        v.co -= v.normal * 0.02 * S
    bm.to_mesh(kin.data)
    bm.free()
    # Hohl: Haube ohne Schnittfläche (Material vom Trenner, Index 1) und ohne Unterseite hinten; Kinnteil ohne Deckel und Halsöffnung
    def drop_h(f):
        c = f.calc_center_median()
        return f.material_index == 1 or (f.normal.z < -0.95 and c.y > 0.30 * S and c.z < 0.30 * S)

    def drop_k(f):
        c = f.calc_center_median()
        return f.material_index == 1 or (f.normal.z < -0.3 and c.y > -0.30 * S)
    # Kinnteil: nach dem Schrumpfen ist der Index des Deckels unverändert (Trenner-Material = Index 1)
    hollow(hau, drop_h)
    hollow(kin, drop_k)
    for ob, m in ((hau, 'MAT_Haube'), (kin, 'MAT_Kinn')):
        ob.data.materials.clear()
        ob.data.materials.append(mat(m))
        for p in ob.data.polygons:
            p.material_index = 0
        cleanup(ob, tri=True)
        print(f'[scout] {ob.name} hohl: {len(ob.data.polygons)} Flächen, {nonmanifold(ob)} Non-Manifold', flush=True)
    save('B')
    return hau, kin


# ------------------------------------------------------------------ C Visier, Leuchtschlitze, Zwischenband, Stirn

VIS = dict(top=0.60, bot=0.28, wt=0.66, wb=0.54, cham=0.05, tilt=12, ahead=0.045, depth=0.026)   # Plattendicke nicht vorgegeben


def visor_outline():
    """Trapez (x, z) mit Fasen an den oberen Ecken."""
    t, b, wt, wb, c = VIS['top'], VIS['bot'], VIS['wt'] / 2, VIS['wb'] / 2, VIS['cham']
    return [(-wb, b), (wb, b), (wt, t - c), (wt - c, t), (-(wt - c), t), (-wt, t - c)]


def visor_y(x, z, extra=0.0):
    """Vorderfläche des Visiers: Mittelgrat bei X = 0 vorn, Hälften 12° zurück."""
    return interp_z(FRONT, z) - VIS['ahead'] + abs(x) * math.tan(math.radians(VIS['tilt'])) + extra


def build_visor():
    bm = bmesh.new()
    ol = visor_outline()
    # Umriss mit Punkt auf X = 0 oben und unten, damit der Grat eine Kante ist
    pts = [ol[0], (0.0, ol[0][1]), ol[1], ol[2], ol[3], (0.0, ol[3][1]), ol[4], ol[5]]
    front = [bm.verts.new(H(x, visor_y(x, z), z)) for x, z in pts]
    back = [bm.verts.new(H(x, visor_y(x, z, VIS['depth']), z)) for x, z in pts]
    n = len(pts)
    fr = bm.faces.new([front[i] for i in (0, 1, 5, 6, 7)][::-1])
    fl = bm.faces.new([front[i] for i in (1, 2, 3, 4, 5)][::-1])
    bm.faces.new([back[i] for i in (0, 1, 5, 6, 7)])
    bm.faces.new([back[i] for i in (1, 2, 3, 4, 5)])
    for k in range(n):
        k2 = (k + 1) % n
        bm.faces.new((front[k], front[k2], back[k2], back[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # Rahmen: Inset 0,02, Innenfläche 0,015 zurück (Rahmen 0,015 erhaben)
    ins = bmesh.ops.inset_region(bm, faces=[fr, fl], thickness=0.02 * S, depth=0.0)
    for f in (fr, fl):
        for v in f.verts:
            v.co.y += 0.015 * S
    vis = obj('Helm_Visier', bm, ['MAT_Visier'])
    cleanup(vis)
    print(f'[scout] Visier: {nonmanifold(vis)} Non-Manifold', flush=True)
    return vis


def visor_cutter():
    bm = bmesh.new()
    ol = visor_outline()
    a = [bm.verts.new(H(x, interp_z(FRONT, z) - 0.10, z)) for x, z in ol]
    b = [bm.verts.new(H(x, visor_y(x, z, VIS['depth']) - 0.002, z)) for x, z in ol]
    bm.faces.new(a)
    bm.faces.new(b[::-1])
    for k in range(len(a)):
        k2 = (k + 1) % len(a)
        bm.faces.new((a[k], a[k2], b[k2], b[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj('CUT_VIS', bm, ['MAT_Visier'], 'HELM_HILFE')


def groove_cutter(name, pts, normals, width, depth, mat_name):
    """Nut entlang einer Folge von Oberflächenpunkten: je Abschnitt ein Quader (Breite × Tiefe), Normalen = Oberflächennormalen."""
    bm = bmesh.new()
    for (p, n), (q, m) in zip(zip(pts, normals), zip(pts[1:], normals[1:])):
        d = (q - p)
        L = d.length
        if L < 1e-6:
            continue
        t = d / L
        nn = ((n + m) / 2).normalized()
        nn = (nn - t * nn.dot(t)).normalized()
        b = t.cross(nn)
        R = Matrix((t, b, nn)).transposed()
        add_box(bm, (p + q) / 2, (L + width, width, 2 * depth), R)
    return obj(name, bm, [mat_name], 'HELM_HILFE')


def surface_path(tree, pts, inward):
    """Punkte (H) auf die Oberfläche projizieren: Strahl von außen (pts − inward·0,5) in Richtung inward."""
    P, N = [], []
    for p, d in zip(pts, inward):
        o = H(*p) - Vector(d).normalized() * 0.5 * S
        loc, nor = hit(tree, o, d)
        if loc is not None:
            P.append(loc)
            N.append(nor)
    return P, N


def section_C(hau, kin):
    vis = build_visor()
    boolean(hau, visor_cutter(), 'DIFFERENCE')
    # C2 Leuchtschlitze: 0,22 × 0,035, Zentrum X ±0,16 / Z 0,43, 6° gedreht (außen tiefer), 0,004 eingelassen
    slots = []
    for side, sx in (('L', -1), ('R', 1)):
        x, z = sx * 0.16, 0.43
        ys = visor_y(x, z, 0.015)                    # Innenfläche des Visiers (hinter dem Rahmen)
        Rz = Matrix.Rotation(math.radians(sx * VIS['tilt']), 3, 'Z')
        Ry = Matrix.Rotation(math.radians(sx * 6), 3, 'Y')
        R = Rz @ Ry
        bm = bmesh.new()
        add_box(bm, H(x, ys - 0.006, z), H(0.22, 0.02, 0.035), R)
        boolean(vis, obj('CUT_SLOT', bm, ['MAT_Visier'], 'HELM_HILFE'), 'DIFFERENCE')
        bm = bmesh.new()
        geo = add_box(bm, H(x, ys + 0.004 + 0.002, z), H(0.218, 0.004, 0.033), R)
        for f in {f for v in geo for f in v.link_faces}:
            f.material_index = 1 if (R.transposed() @ f.normal).y < -0.9 else 0
        sl = obj(f'Helm_Leuchtschlitz_{side}', bm, ['MAT_Visier', 'MAT_Emission'])
        slots.append(sl)
    save('C1-C2')
    # C3 Zwischenband: Nut Z 0,28–0,34 über die ganze Frontbreite, 0,01 zurückgesetzt
    bm = bmesh.new()
    add_box(bm, H(0, interp_z(FRONT, 0.31) - 0.10 + 0.01, 0.31), H(0.95, 0.20, 0.06))
    boolean(hau, obj('CUT_BAND', bm, ['MAT_Haube'], 'HELM_HILFE'), 'DIFFERENCE')
    # C4 Mittelsicke 0,03 × 0,004 von Z 0,62 über die Stirnkante bis Y 0 auf dem Dach; Sensorfenster X ±0,20 / Z 0,70
    tree = bvh(hau)
    prof = sorted([(y, z) for y, z in FRONT if z > 0.62 and y <= 0.0] + [(0.0, 0.998)], key=lambda p: p[1])
    pts = [(0.0, interp_z(FRONT, 0.62), 0.62), (0.0, interp_z(FRONT, 0.70), 0.70)] + [(0.0, y, z) for y, z in prof]
    P, N = surface_path(tree, pts, [_inward(p) for p in pts])
    boolean(hau, groove_cutter('CUT_SICKE', P, N, 0.03 * S, 0.004 * S, 'MAT_Haube'), 'DIFFERENCE', self_=True)
    tree = bvh(hau)
    bm = bmesh.new()
    for sx in (-1, 1):                               # beide Fenster in einem Schnitt, als Quader (Eckradius entfällt, Bericht)
        loc, nor = hit(tree, H(sx * 0.20, -1.0, 0.70), (0, 1, 0))
        add_box(bm, loc, H(0.06, 0.008, 0.03))
    boolean(hau, obj('CUT_SENS', bm, ['MAT_Visier'], 'HELM_HILFE'), 'DIFFERENCE')
    cleanup(hau)
    cleanup(vis)
    save('C')
    return vis, slots


def _inward(p):
    """Strahlrichtung zur Oberfläche für Punkte auf der Mittellinie vorn/oben: senkrecht zum Profil, nach innen."""
    y, z = p[1], p[2]
    if z < 0.78:
        return (0, 1, 0)
    c = Vector((0.0206, 0.4506))                     # Mittelpunkt des Scheitelbogens (A1)
    d = (c - Vector((y, z))).normalized()
    return (0, d.x, d.y)


# ------------------------------------------------------------------ D Kinnteil

def section_D(kin):
    tree = bvh(kin)
    # Lüftungsschlitze: 2 Gruppen à 3, Gruppenzentrum X ±0,10, 0,015 breit, Z 0,10–0,22, Abstand 0,025, Tiefe 0,01
    bm = bmesh.new()
    for gx in (-0.10, 0.10):
        for k in (-1, 0, 1):
            x = gx + k * 0.025
            loc, nor = hit(tree, H(x, -1.0, 0.16), (0, 1, 0))
            add_box(bm, loc, H(0.015, 0.02, 0.12))
    boolean(kin, obj('CUT_VENT', bm, ['MAT_Kinn'], 'HELM_HILFE'), 'DIFFERENCE')
    # Mittelrippe 0,04 breit, 0,006 erhaben, Z 0,06–0,26
    tree = bvh(kin)
    bm = bmesh.new()
    zs = [0.06 + 0.02 * k for k in range(11)]
    pts = [hit(tree, H(0, -1.0, z), (0, 1, 0))[0] for z in zs]
    for p, q in zip(pts, pts[1:]):
        d = (q - p)
        t = d.normalized()
        nn = Vector((0, -1, 0))
        nn = (nn - t * nn.dot(t)).normalized()
        R = Matrix((t, t.cross(nn), nn)).transposed()
        add_box(bm, (p + q) / 2 + nn * 0.0015 * S, (d.length + 0.002 * S, 0.04 * S, 0.009 * S), R)
    boolean(kin, obj('RIPPE', bm, ['MAT_Kinn'], 'HELM_HILFE'), 'UNION', self_=True)
    # Rastelement je Seite: Zylinder Ø 0,05, 0,008 erhaben, Fase 0,003, bei Y −0,10 / Z 0,25 (MAT_Metall, Teil des Kinnteils)
    tree = bvh(kin)
    rast = []
    for sx in (-1, 1):
        loc, nor = hit(tree, H(sx * 1.0, -0.10, 0.25), (-sx, 0, 0))
        bm = bmesh.new()
        M = frame_of(nor)
        lathe(bm, [(0, -0.002 * S), (0.025 * S, -0.002 * S), (0.025 * S, 0.005 * S), (0.022 * S, 0.008 * S), (0, 0.008 * S)], M, loc, 32)
        o = obj('RAST', bm, ['MAT_Metall'], 'HELM_HILFE')
        rast.append((o, loc + nor * 0.008 * S, nor))
    # Nackenlasche: 0,30 breit bis Z 0,38, Oberkante R 0,05, am hinteren Ende des Kinnteils
    bm = bmesh.new()
    ol = []
    for u, v in rounded_rect(0.30 * S, 0.24 * S, 0.05 * S, 6):
        ol.append((u, v))
    prism(bm, ol, 0.015 * S, H(0, 0.345, 0.26), Vector((1, 0, 0)), Vector((0, 0, 1)), Vector((0, 1, 0)))
    lasche = obj('LASCHE', bm, ['MAT_Kinn'], 'HELM_HILFE')
    boolean(kin, lasche, 'UNION')
    for o, _, _ in rast:
        coll('HELM').objects.link(o)
        coll('HELM_HILFE').objects.unlink(o)
    join(kin, [o for o, _, _ in rast])
    cleanup(kin)
    NOTES.append('D Nackenlasche: als Platte 0,30 × 0,24 am hinteren Ende des Kinnteils (Y +0,345–0,36, Oberkante Z 0,38) gesetzt; die '
                 'Spezifikation nennt keine Lage in Y, und die Hüllmaße begrenzen das Kinnteil auf Y ≤ +0,375')
    save('D')
    return [(p, n, 1.0) for _, p, n in rast]


# ------------------------------------------------------------------ E Pods

def plate_on_surface(tree, name, outline, center, U, V, n_out, thick, mats, mat_index=0):
    """Platte mit Umriss (u, v), Innenseite per Raycast entlang −n_out auf die Haube projiziert (Shrinkwrap), Dicke nach außen."""
    bm = bmesh.new()
    inner, outer = [], []
    for u, v in outline:
        p = Vector(center) + U * u + V * v
        loc, nor = hit(tree, p + n_out * 0.3 * S, -n_out)
        q = loc if loc is not None else p
        inner.append(bm.verts.new(q))
        outer.append(bm.verts.new(q + n_out * thick))
    n = len(outline)
    faces = [bm.faces.new(inner[::-1]), bm.faces.new(outer)]
    for k in range(n):
        k2 = (k + 1) % n
        faces.append(bm.faces.new((inner[k], inner[k2], outer[k2], outer[k])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    for f in faces:
        f.material_index = mat_index
    return obj(name, bm, mats)


def section_E(hau, kin):
    tree = bvh(hau)
    screws = []
    pods = {}
    for side, sx in (('L', -1), ('R', 1)):
        ax = Vector((sx, 0, 0))
        # Sockelplatte 0,26 × 0,26 × 0,015, R 0,03, an die Schläfe (Shrinkwrap)
        base = plate_on_surface(tree, f'Helm_Pod_{side}', rounded_rect(0.26 * S, 0.26 * S, 0.03 * S, 6), H(sx * 0.42, 0, 0.50),
                                Vector((0, 1, 0)), Vector((0, 0, 1)), ax, 0.015 * S, ['MAT_Pod'])
        bx = max(v.co.x * sx for v in base.data.vertices) / S       # Außenseite der Sockelplatte (H)
        # Zylinder Ø 0,22, Dicke 0,10, Außenfläche konvex (+0,01), Fase 0,015, Rille r 0,08 (0,006 × 0,003); 48 Segmente
        x0, x1, R, f = 0.47 - 0.05, 0.47 + 0.05, 0.11, 0.015

        def dome(r):
            return x1 + 0.01 * (1 - (r / (R - f)) ** 2)
        prof = [(0, x0), (R, x0), (R, x1 - f), (R - f, x1), (0.083, dome(0.083)), (0.083, dome(0.083) - 0.003),
                (0.077, dome(0.077) - 0.003), (0.077, dome(0.077)), (0, x1 + 0.01)]
        prof = [(r * S, a * S) for r, a in prof]
        bm = bmesh.new()
        M = Matrix(((sx, 0, 0), (0, 1, 0), (0, 0, 1)))
        lathe(bm, [(r, a) for r, a in prof], M, H(0, 0, 0.50), 48)
        c = obj('POD_CYL', bm, ['MAT_Pod'], 'HELM')
        join(base, [c])
        cleanup(base)
        pods[side] = base
        # 4 Schrauben Ø 0,012 an den Sockelecken
        for dy in (-0.10, 0.10):
            for dz in (-0.10, 0.10):
                screws.append((H(sx * bx, dy, 0.50 + dz), ax, 1.0))
        # E2 Kasten oben (12 Uhr), E3 Stecker vorn (9 Uhr) mit Kabel zum Kinnteil
        bm = bmesh.new()
        add_box(bm, H(sx * 0.47, 0, 0.61 + 0.02), H(0.06, 0.05, 0.04))
        obj(f'Helm_Pod_Kasten_{side}', bm, ['MAT_Pod'])
        bm = bmesh.new()
        cyl(bm, 0.0125 * S, 0.03 * S, H(sx * 0.47, -0.11 - 0.015, 0.50), (0, 1, 0), 24)
        st = obj(f'Helm_Pod_Stecker_{side}', bm, ['MAT_Metall', 'MAT_Gummi'])
        ktree = bvh(kin)
        end, _ = hit(ktree, H(sx * 1.0, -0.15, 0.30), (-sx, 0, 0))
        p0 = H(sx * 0.47, -0.14, 0.50)
        cab = curve_obj('KABEL', [p0, (p0 + end) / 2 + H(sx * 0.03, -0.03, -0.02), end], 0.005 * S, 'MAT_Gummi', 'HELM')
        NOTES.append(f'E3 Kabel {side}: Länge {curve_len(cab) / S:.3f} H (Soll ≈ 0,12); der Endpunkt am Kinnteil (Y −0,15 / Z 0,30) liegt '
                     f'{(end - p0).length / S:.3f} H vom Stecker entfernt')
        join(st, [to_mesh(cab)])
    # E4 Kabelverteiler nur rechts: 0,05 × 0,03 × 0,03 auf der Sockelplatte bei Y +0,09 / Z 0,60, Kurzkabel Ø 0,008 in den Kasten
    bx = max(v.co.x for v in pods['R'].data.vertices if abs(v.co.y - 0.09 * S) < 0.03 * S and abs(v.co.z - 0.60 * S) < 0.03 * S) / S
    bm = bmesh.new()
    add_box(bm, H(bx + 0.015, 0.09, 0.60), H(0.03, 0.05, 0.03))
    box2 = obj('Helm_Pod_Box2_R', bm, ['MAT_Pod', 'MAT_Gummi'])
    bv = box2.modifiers.new('BEVEL', 'BEVEL')
    bv.width, bv.segments = 0.003 * S, 2
    k0 = H(bx + 0.015, 0.09 - 0.02, 0.615)
    k1 = H(0.47, -0.025, 0.63)
    kab = curve_obj('KABEL2', [k0, k1], 0.004 * S, 'MAT_Gummi', 'HELM')
    NOTES.append(f'E4 Kurzkabel: Länge {curve_len(kab) / S:.3f} H (Soll 0,06)')
    join(box2, [to_mesh(kab)])
    save('E')
    return pods, screws


def curve_obj(name, pts, r, mat_name, collection, taper=None, res=12):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    cu.bevel_depth = r
    cu.bevel_resolution = 4
    cu.resolution_u = res
    cu.use_fill_caps = True
    if taper:
        cu.taper_object = taper
    ob = bpy.data.objects.new(name, cu)
    coll(collection).objects.link(ob)
    ob.data.materials.append(mat(mat_name))
    return ob


def curve_points(ob, n=None):
    """Mittellinie der Kurve (ausgewertet ohne Bevel und Taper), Punkte in Reihenfolge."""
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


def curve_len(ob):
    pts = curve_points(ob)
    return sum((b - a).length for a, b in zip(pts, pts[1:]))


def to_mesh(curve_ob):
    me = bpy.data.meshes.new_from_object(curve_ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    ob = bpy.data.objects.new(curve_ob.name + '_mesh', me)
    for c in curve_ob.users_collection:
        c.objects.link(ob)
    bpy.data.objects.remove(curve_ob, do_unlink=True)
    return ob


# ------------------------------------------------------------------ F Schläuche, Hülsen, hinterer Block

def rib_taper():
    """Taper-Kurve: Radiusfaktor 1,0/0,8 (Tiefe 0,003 bei Radius 0,015) alle 0,012 H entlang der Schlauchlänge (≈ 0,62 H)."""
    cu = bpy.data.curves.new('TAPER_RIPPEN', 'CURVE')
    sp = cu.splines.new('POLY')
    n_rib = int(0.62 / 0.012)
    m = n_rib * 8
    sp.points.add(m)
    for i in range(m + 1):
        u = i / m
        sp.points[i].co = (u, 0.9 + 0.1 * math.cos(2 * math.pi * n_rib * u), 0, 1)
    ob = bpy.data.objects.new('TAPER_RIPPEN', cu)
    coll('HELM_HILFE').objects.link(ob)
    return ob


def section_F(hau):
    tree = bvh(hau)
    # F3 Block: Grundplatte 0,30 × 0,22 × 0,04 an den Hinterkopf (Shrinkwrap), Zylinder Ø 0,12 × 0,08 (Achse Y, mit Deckel),
    # Schlaucheintritte Ø 0,04 links/rechts, 2 Schrauben Ø 0,015 an der Oberkante
    blk = plate_on_surface(tree, 'Helm_Block_Hinten', rounded_rect(0.30 * S, 0.22 * S, 0.02 * S, 4), H(0, 0.50, 0.45),
                           Vector((1, 0, 0)), Vector((0, 0, 1)), Vector((0, 1, 0)), 0.04 * S, ['MAT_Pod'])
    yb = max(v.co.y for v in blk.data.vertices) / S
    bm = bmesh.new()
    cyl(bm, 0.06 * S, 0.08 * S, H(0, yb + 0.04 - 0.002, 0.45), (0, 1, 0), 40)
    inl = {}
    for sx in (-1, 1):
        y_in = (min(v.co.y for v in blk.data.vertices if v.co.x * sx > 0.13 * S) / S + yb) / 2
        inl[sx] = (sx * 0.17, y_in, 0.52)
        cyl(bm, 0.02 * S, 0.04 * S, H(sx * 0.16, y_in, 0.52), (1, 0, 0), 24)
    c = obj('BLOCK_TEILE', bm, ['MAT_Pod'])
    join(blk, [c])
    cleanup(blk)
    screws = [(H(sx * 0.10, yb, 0.54), Vector((0, 1, 0)), 1.25) for sx in (-1, 1)]
    # F1 Schläuche: P0 (Y 0 / Z 0,62) am Kasten, P1 (Y +0,25 / Z 0,72), P2 am Block; zweiter Schlauch 0,04 versetzt (X +0,02 außen)
    taper = rib_taper()
    huelsen = []
    for side, sx in (('L', -1), ('R', 1)):
        for k, off in (('1', Vector((0, 0, 0))), ('2', Vector((sx * 0.02, 0, -0.035)))):
            p0 = H(sx * 0.45, 0.0, 0.62) + off * S
            p1 = H(sx * 0.45, 0.25, 0.72) + off * S
            p2 = H(*inl[sx]) + Vector((sx * 0.02, 0, -0.035 if k == '2' else 0)) * S
            cu = curve_obj(f'Helm_Schlauch_{side}{k}', [p0, p1, p2], 0.015 * S, 'MAT_Gummi', 'HELM', taper=taper, res=256)
            pts = curve_points(cu)
            apex = min(pts, key=lambda p: (p - p1).length)
            free = tree.find_nearest(apex)[3] / S - 0.015
            low = min(tree.find_nearest(p)[3] for p in pts[len(pts) // 4: 3 * len(pts) // 4]) / S - 0.015
            NOTES.append(f'F1 Helm_Schlauch_{side}{k}: Länge {sum((b - a).length for a, b in zip(pts, pts[1:])) / S:.3f} H, '
                         f'Abstand Mantel–Haube am Scheitel P1 {free:.3f} H (Soll ≥ 0,04), kleinster im Mittelteil {low:.3f} H')
            for end, (a, b) in (('a', (pts[0], pts[3])), ('b', (pts[-1], pts[-4]))):
                bm = bmesh.new()
                d = (a - b).normalized()
                cyl(bm, 0.02 * S, 0.04 * S, a - d * 0.01 * S, d, 24)
                huelsen.append(obj(f'Helm_Huelse_{side}{k}{end}', bm, ['MAT_Metall']))
    save('F')
    return screws


# ------------------------------------------------------------------ G Antenne, Panel-Nuten

def section_G(hau):
    tree = bvh(hau)
    foot, nor = hit(tree, H(0.06, 0.12, 1.5), (0, 0, -1))
    bm = bmesh.new()
    lathe(bm, [(0, 0), (0.015 * S, 0), (0.015 * S, 0.02 * S), (0.006 * S, 0.035 * S), (0, 0.035 * S)], frame_of((0, 0, 1)), foot, 24)
    d = Vector((math.tan(math.radians(5)), math.tan(math.radians(15)), 1)).normalized()
    a0 = foot + Vector((0, 0, 0.035 * S))
    cyl(bm, 0.003 * S, 0.24 * S, a0 + d * 0.12 * S, d, 12)
    tip = a0 + d * 0.24 * S
    sph = bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.004 * S)
    for v in sph['verts']:
        v.co += tip
    obj('Helm_Antenne', bm, ['MAT_Pod'])
    # G2 Nuten 0,006 × 0,003: Dachmitte bis Y +0,30, Quernaht Y +0,30, Schrägnähte Stirnecke → Pod-Sockel, Rückenplatte (F4)
    cuts = []

    def path(name, pts, dirs):
        P, N = surface_path(tree, pts, dirs)
        if len(P) >= 2:
            cuts.append(groove_cutter(name, P, N, 0.006 * S, 0.003 * S, 'MAT_Haube'))
    ys = [k / 20 * 0.30 for k in range(21)]
    path('N1', [(0, y, 1.2) for y in ys], [(0, 0, -1)] * len(ys))
    xs = [-0.42 + k * 0.84 / 30 for k in range(31)]
    path('N2', [(x, 0.30, 1.2 if abs(x) < 0.30 else 0.85) for x in xs], [(0, 0, -1) if abs(x) < 0.30 else (-math.copysign(1, x), 0, -0.4) for x in xs])
    for sx in (-1, 1):
        a, b = Vector((sx * 0.30, -0.38, 0.78)), Vector((sx * 0.43, -0.13, 0.63))
        pts = [tuple(a + (b - a) * (0.94 * k / 12)) for k in range(13)]     # endet knapp vor der Sockelkante (Boolean-Rest)
        path(f'N3{sx}', pts, [(-sx, 0.4, -0.2)] * len(pts))
    # F4 Rückenplatte: umlaufende Nut Z 0,60–0,80, seitlich X ±0,25 (Oberkante läuft in die Quernaht über)
    loop = [(-0.25, 0.60), (0.25, 0.60), (0.25, 0.80), (-0.25, 0.80), (-0.25, 0.60)]
    pts = []
    for (x0, z0), (x1, z1) in zip(loop, loop[1:]):
        for k in range(10):
            pts.append((x0 + (x1 - x0) * k / 10, 1.0, z0 + (z1 - z0) * k / 10))
    pts.append((loop[-1][0], 1.0, loop[-1][1]))
    path('N4', pts, [(0, -1, 0)] * len(pts))
    join(cuts[0], cuts[1:])                           # alle Nuten in einem Schnitt
    boolean(hau, cuts[0], 'DIFFERENCE')
    # G2.4 Dachsensor nur rechts: 0,06 (Y) × 0,03 (X), Tiefe 0,004, X +0,15 / Y −0,15 / Z 0,95
    tree = bvh(hau)
    loc, nor = hit(tree, H(0.15, -0.15, 1.5), (0, 0, -1))
    bm = bmesh.new()
    t = Vector((0, 1, 0))
    t = (t - nor * t.dot(nor)).normalized()
    add_box(bm, loc, (0.03 * S, 0.06 * S, 0.008 * S), Matrix((t.cross(nor), t, nor)).transposed())
    boolean(hau, obj('CUT_DACH', bm, ['MAT_Visier'], 'HELM_HILFE'), 'DIFFERENCE')
    cleanup(hau)
    save('G')


def place_screws(spots):
    bm = bmesh.new()
    lathe(bm, [(0, -0.002 * S), (0.006 * S, -0.002 * S), (0.006 * S, 0.002 * S), (0.004 * S, 0.004 * S), (0, 0.004 * S)],
          frame_of((0, 0, 1)), Vector((0, 0, 0)), 16)
    me = bpy.data.meshes.new('Schraube')
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat('MAT_Metall'))
    for i, (p, n, sc) in enumerate(spots):
        ob = bpy.data.objects.new(f'Helm_Schraube_{i + 1:02d}', me)
        R = frame_of(n)
        R = Matrix((R.col[1], R.col[2], R.col[0])).transposed()      # lokale Z = Normale
        ob.matrix_world = Matrix.Translation(p) @ R.to_4x4() @ Matrix.Scale(sc, 4)
        coll('HELM').objects.link(ob)


# ------------------------------------------------------------------ H Tuch

def cloth_mod(ob, pin):
    vg = ob.vertex_groups.new(name='pin')
    vg.add([v.index for v in ob.data.vertices if pin(v.co)], 1.0, 'REPLACE')
    m = ob.modifiers.new('Cloth', 'CLOTH')
    st = m.settings
    st.quality = 10
    st.mass = 0.3
    st.tension_stiffness = st.compression_stiffness = 15
    st.shear_stiffness = 15
    st.bending_stiffness = 0.5
    st.air_damping = 1.0
    st.vertex_group_mass = 'pin'
    m.collision_settings.use_self_collision = True
    m.point_cache.frame_start, m.point_cache.frame_end = 1, 60
    return m


def grid(name, w, h, nu, nv, M):
    bm = bmesh.new()
    V = [[bm.verts.new(M @ Vector(((i / nu - 0.5) * w, 0, -j / nv * h))) for i in range(nu + 1)] for j in range(nv + 1)]
    for j in range(nv):
        for i in range(nu):
            bm.faces.new((V[j][i], V[j][i + 1], V[j + 1][i + 1], V[j + 1][i]))
    return obj(name, bm, ['MAT_Tuch'], 'TUCH')


def section_H():
    sc = bpy.context.scene
    # Kollision: alle Helmteile und eine unsichtbare Schulterkugel r 0,70 bei Z −0,95
    for ob in coll('HELM').objects:
        if ob.type == 'MESH':
            ob.modifiers.new('Collision', 'COLLISION')
    bm = bmesh.new()
    sph = bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=0.70 * S)
    for v in sph['verts']:
        v.co += H(0, 0, -0.95)
    kugel = obj('Schulterkugel', bm, ['MAT_Tuch'], 'HELM_HILFE')
    kugel.modifiers.new('Collision', 'COLLISION')
    kugel.hide_render = True
    # H1 Wicklung: Zylinder 24 Segmente, r 0,55, Z −0,50 … −0,05, Pin oberer Rand
    bm = bmesh.new()
    rings = []
    for j in range(13):
        z = -0.05 - 0.45 * j / 12
        rings.append([bm.verts.new(H(0.55 * math.cos(2 * math.pi * k / 24), 0.55 * math.sin(2 * math.pi * k / 24), z)) for k in range(24)])
    for A, B in zip(rings, rings[1:]):
        for k in range(24):
            bm.faces.new((A[k], A[(k + 1) % 24], B[(k + 1) % 24], B[k]))
    w = obj('Tuch_Wicklung', bm, ['MAT_Tuch'], 'TUCH')
    cloth_mod(w, lambda c: c.z > -0.06 * S)
    # H2 Schulter: Kreisfläche r 0,72 bei Z −0,50, Pin am Innenrand r 0,55
    bm = bmesh.new()
    rings = []
    for j in range(7):
        r = 0.55 + (0.72 - 0.55) * j / 6
        rings.append([bm.verts.new(H(r * math.cos(2 * math.pi * k / 48), r * math.sin(2 * math.pi * k / 48), -0.50)) for k in range(48)])
    for A, B in zip(rings, rings[1:]):
        for k in range(48):
            bm.faces.new((A[k], A[(k + 1) % 48], B[(k + 1) % 48], B[k]))
    sch = obj('Tuch_Schulter', bm, ['MAT_Tuch'], 'TUCH')
    cloth_mod(sch, lambda c: Vector((c.x, c.y)).length < 0.56 * S)
    # H3/H4 Zipfel: Pin an der Oberkante, diagonal zur angegebenen Spitze ausgerichtet
    for name, top, tipp, w_, h_ in (('Tuch_Zipfel_Vorn', (0.25, -0.58, -0.30), (-0.20, -0.62, -0.90), 0.25, 0.60),
                                    ('Tuch_Zipfel_Hinten', (0.15, 0.45, -0.30), (0.10, 0.45, -1.00), 0.25, 0.70)):
        t, p = H(*top), H(*tipp)
        down = (p - t).normalized()
        side = Vector((0, 1, 0)).cross(down).normalized() if abs(down.y) < 0.9 else Vector((1, 0, 0))
        nrm = side.cross(down)
        M = Matrix((side, -nrm, -down)).transposed()
        M4 = Matrix.Translation(t) @ M.to_4x4() @ Matrix.Scale(S, 4)
        g = grid(name, w_, (p - t).length / S, 8, 20, M4)
        cloth_mod(g, lambda c, t=t: (c - t).length < 0.14 * S and c.z > t.z - 0.02 * S)
    sc.frame_start, sc.frame_end = 1, 60
    for f in range(1, 61):
        sc.frame_set(f)
    for ob in list(coll('TUCH').objects):
        apply_mod(ob, 'Cloth')
        ob.vertex_groups.clear()
        m = ob.modifiers.new('SOLID', 'SOLIDIFY')
        m.thickness = 0.006 * S
        apply_mod(ob, m.name)
    for ob in coll('HELM').objects:
        for m in list(ob.modifiers):
            if m.type == 'COLLISION':
                ob.modifiers.remove(m)
    NOTES.append('H Tuch: Simulation 60 Bilder ohne Feinabstimmung; „3 sichtbare Lagen“ der Wicklung und die Faltenzahl der Schulter '
                 'sind nicht gezielt gesteuert, sondern Ergebnis der Simulation')
    save('H')


# ------------------------------------------------------------------ Abschluss: Bevel, Prüfung, Renders, Bericht

SOLL = {'Helm_Haube+Helm_Kinnteil': ((0.85, 1.00, 1.03), (0, 0.03, 0.50)), 'Helm_Haube': ((0.85, 0.62, 1.03), (0, 0.03, 0.69)),
        'Helm_Kinnteil': ((0.80, 0.40, 0.85), (0, -0.05, 0.20)), 'Helm_Visier': ((0.66, 0.32, 0.10), (0, -0.47, 0.44)),
        'Helm_Pod_L': ((0.10, 0.22, 0.22), (-0.47, 0, 0.50)), 'Helm_Pod_R': ((0.10, 0.22, 0.22), (0.47, 0, 0.50)),
        'Helm_Block_Hinten': ((0.30, 0.22, 0.12), (0, 0.52, 0.45)), 'Helm_Antenne': ((0.03, 0.26, 0.03), (0.06, 0.12, None)),
        'TUCH': ((1.45, 0.95, 1.30), (0, 0.05, -0.30))}
WHY = {  # Begründungen für Hüllmaße außerhalb ±5 % (Widersprüche innerhalb der Spezifikation)
    'Helm_Haube': 'B legt die Trennlinie vorn auf Z 0,28; die Haube reicht damit vorn bis 0,28 und ist 0,72 statt 0,62 hoch '
                  '(Haube + Kinnteil zusammen stimmen)',
    'Helm_Kinnteil': 'B verlangt 0,02 Schrumpfen entlang der Normalen; das senkt die Oberkante und hebt die Unterkante um je ≈ 0,014',
    'Helm_Pod_L': 'die Soll-Hülle entspricht dem Zylinder allein (Ø 0,22, Dicke 0,10); E1 verlangt die Sockelplatte 0,26 × 0,26 im selben '
                  'Objekt (join), die auf der Schläfe bei X ≈ 0,40 aufliegt',
    'Helm_Pod_R': 'wie Helm_Pod_L',
    'Helm_Block_Hinten': 'F3: Schlaucheintritte Ø 0,04 seitlich (X bis ±0,18) und Grundplatte per Shrinkwrap am gewölbten Hinterkopf '
                         '(Y bis +0,55) plus Zylinder 0,08 nach hinten; die Soll-Mitte Y +0,52 läge zur Hälfte im Hinterkopf (A1: Y +0,55)',
    'Helm_Antenne': 'G1: Stab 0,24 mit 15° nach hinten und 5° nach außen geneigt ergibt allein 0,062 Tiefe und 0,021 Breite; die Soll-Hülle '
                    '0,03 × 0,03 passt nur zu einem senkrechten Stab',
}
NAMES = (['Helm_Haube', 'Helm_Kinnteil', 'Helm_Visier', 'Helm_Leuchtschlitz_L', 'Helm_Leuchtschlitz_R', 'Helm_Pod_L', 'Helm_Pod_R',
          'Helm_Pod_Kasten_L', 'Helm_Pod_Kasten_R', 'Helm_Pod_Stecker_L', 'Helm_Pod_Stecker_R', 'Helm_Pod_Box2_R', 'Helm_Schlauch_L1',
          'Helm_Schlauch_L2', 'Helm_Schlauch_R1', 'Helm_Schlauch_R2', 'Helm_Block_Hinten', 'Helm_Antenne', 'Tuch_Wicklung',
          'Tuch_Schulter', 'Tuch_Zipfel_Vorn', 'Tuch_Zipfel_Hinten'])


def bounds(obs):
    dg = bpy.context.evaluated_depsgraph_get()
    lo, hi = Vector((1e9,) * 3), Vector((-1e9,) * 3)
    for ob in obs:
        e = ob.evaluated_get(dg)
        for c in e.bound_box:
            w = e.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, w))
            hi = Vector(map(max, hi, w))
    return (hi - lo) / S, (hi + lo) / 2 / S, lo / S


def repair(ob):
    """Reste exakter Booleans: doppelte Flächen (Kanten mit 3–4 Flächen), lose Geometrie, Kleinstlöcher (Kanten mit 1 Fläche)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    seen, dup = set(), []
    for f in bm.faces:
        k = frozenset(v.index for v in f.verts)
        if k in seen:
            dup.append(f)
        seen.add(k)
    bmesh.ops.delete(bm, geom=dup, context='FACES')
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0002 * S)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-5, edges=bm.edges)
    loose = [e for e in bm.edges if not e.link_faces]
    bmesh.ops.delete(bm, geom=loose, context='EDGES')
    # Flächen an Kanten mit mehr als zwei Flächen: kleinste (Splitter) entfernen, dann Löcher schließen
    for _ in range(3):
        over = [e for e in bm.edges if len(e.link_faces) > 2]
        if not over:
            break
        kill = {min(e.link_faces, key=lambda f: f.calc_area()) for e in over}
        bmesh.ops.delete(bm, geom=list(kill), context='FACES')
    bnd = [e for e in bm.edges if e.is_boundary]
    if bnd:
        bmesh.ops.holes_fill(bm, edges=bnd, sides=0)
    for _ in range(4):             # Splitterflächen < 1e-7 m²: kürzeste Kante zusammenziehen
        tiny = [f for f in bm.faces if f.is_valid and f.calc_area() < 1e-7]
        if not tiny:
            break
        edges = list({min(f.edges, key=lambda e: e.calc_length()) for f in tiny})
        bmesh.ops.collapse(bm, edges=[e for e in edges if e.is_valid], uvs=False)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()


def planar(ob):
    """Nach allen Schnitten: koplanare Dreiecke wieder zu ebenen Flächen zusammenfassen (Limited Dissolve 0,5°, gleiche Materialien)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.5), verts=list(bm.verts), edges=list(bm.edges),
                             delimit={'MATERIAL'})
    bm.to_mesh(ob.data)
    bm.free()


def finish():
    for n in ('Helm_Haube', 'Helm_Kinnteil', 'Helm_Visier'):
        a = nonmanifold(bpy.data.objects[n])
        repair(bpy.data.objects[n])
        if n != 'Helm_Visier':     # am Visier erzeugte Limited Dissolve konkave N-Gons, an denen der Bevel bis Z 0,63 überschoss
            planar(bpy.data.objects[n])
            repair(bpy.data.objects[n])
        print(f'[scout] {n} eben: Non-Manifold {a} → {nonmanifold(bpy.data.objects[n])}', flush=True)
    # Hilfsobjekte (Schneidkörper, Taper) erst jetzt ausblenden: ausgeblendete Objekte wertet der Depsgraph nicht aus,
    # dann liefern Booleans mit ihnen leere Netze
    bpy.context.view_layer.layer_collection.children['HELM_HILFE'].hide_viewport = True
    coll('HELM_HILFE').hide_render = True
    for name, w in (('Helm_Haube', 0.006), ('Helm_Kinnteil', 0.003)):     # Visier ohne Bevel: auf den Boolean-Resten schoss er 0,03 H über
        m = bpy.data.objects[name].modifiers.new('BEVEL', 'BEVEL')
        m.width, m.segments, m.limit_method, m.angle_limit = w * S, 2, 'ANGLE', math.radians(30)
        m.harden_normals = True
        m.use_clamp_overlap = True
    for ob in coll('HELM').all_objects:
        if ob.type == 'MESH':
            ob.data.shade_smooth()
            ob.data.set_sharp_from_angle(angle=math.radians(30))
    save('Abschluss')


def check():
    rows, errs = [], []
    allobs = {o.name: o for o in coll('HELM').all_objects}
    tuch = bool(coll('TUCH').objects)
    for n in [n for n in NAMES if tuch or not n.startswith('Tuch_')]:
        if n not in allobs:
            errs.append(f'J1 fehlt: {n}')
    extra = [n for n, o in allobs.items() if not (n in NAMES or n.startswith(('Helm_Schraube_', 'Helm_Huelse_')))]
    if extra:
        errs.append(f'J1 zusätzliche Objekte: {extra}')
    for key, (dim, cen) in SOLL.items():
        if key == 'TUCH' and not tuch:
            continue
        obs = ([allobs['Helm_Haube'], allobs['Helm_Kinnteil']] if '+' in key else
               list(coll('TUCH').objects) if key == 'TUCH' else [allobs[key]])
        d, c, lo = bounds(obs)
        dev = [(d.x - dim[0]) / dim[0] * 100, (d.y - dim[2]) / dim[2] * 100, (d.z - dim[1]) / dim[1] * 100]
        cz = cen[2] if cen[2] is not None else None
        rows.append((key, dim, (d.x, d.z, d.y), (cen[0], cen[1], cz), (c.x, c.y, c.z if cz is not None else lo.z), (dev[0], dev[2], dev[1])))
        over = [f'{ax} {v:+.1f} %' for ax, v in zip(('B', 'T', 'H'), dev) if abs(v) > 5]
        if over:
            errs.append(f'J2 {key}: {", ".join(over)} – {WHY.get(key, "ohne Begründung")}')
    for a, b in (('Helm_Pod_L', 'Helm_Pod_R'), ('Helm_Leuchtschlitz_L', 'Helm_Leuchtschlitz_R'), ('Helm_Pod_Kasten_L', 'Helm_Pod_Kasten_R'),
                 ('Helm_Pod_Stecker_L', 'Helm_Pod_Stecker_R'), ('Helm_Schlauch_L1', 'Helm_Schlauch_R1'), ('Helm_Schlauch_L2', 'Helm_Schlauch_R2')):
        da, ca, _ = bounds([allobs[a]])
        db, cb, _ = bounds([allobs[b]])
        if abs(abs(ca.x) - abs(cb.x)) > 0.005 or (da - db).length > 0.005:
            errs.append(f'J3 {a}/{b}: Zentrum x {ca.x:.4f}/{cb.x:.4f}, Maße {tuple(round(v, 4) for v in da)}/{tuple(round(v, 4) for v in db)}')
    for n in ('Helm_Haube', 'Helm_Kinnteil', 'Helm_Visier'):
        bm = bmesh.new()
        bm.from_mesh(allobs[n].data)
        nm = sum(1 for e in bm.edges if not e.is_manifold)
        small = sum(1 for f in bm.faces if f.calc_area() < 1e-7)
        bm.free()
        if nm or small:
            errs.append(f'J4 {n}: {nm} Non-Manifold-Kanten, {small} Flächen < 1e-7')
    for n in ('Helm_Leuchtschlitz_L', 'Helm_Leuchtschlitz_R'):
        if 'MAT_Emission' not in [m.name for m in allobs[n].data.materials]:
            errs.append(f'J5 {n} ohne MAT_Emission')
    for n, o in allobs.items():
        if o.type in ('MESH', 'CURVE') and (not o.data.materials or any(m is None or m.name not in list(MATS) + ['MAT_Emission'] for m in o.data.materials)):
            errs.append(f'J5 {n}: Material fehlt oder nicht aus Tabelle I')
    if 'Helm_Pod_Box2_L' in allobs:
        errs.append('J6 Box2 links vorhanden')
    ant = bounds([allobs['Helm_Antenne']])[2]
    for n, o in allobs.items():
        for m in o.modifiers:
            if m.type not in ('BEVEL', 'MIRROR'):
                errs.append(f'J7 {n}: Modifier {m.type} nicht angewendet')
    return rows, errs, ant


def cameras_and_render(samples):
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE'
    try:
        sc.eevee.taa_render_samples = samples
    except AttributeError:
        pass
    sc.render.resolution_x = sc.render.resolution_y = 1024
    sc.render.film_transparent = False
    world = bpy.data.worlds.new('Grau')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (*srgb('#7A7D82'), 1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
    sc.world = world
    sc.view_settings.view_transform = 'Standard'
    li = bpy.data.objects.new('Licht', bpy.data.lights.new('Licht', 'AREA'))
    li.data.energy, li.data.size = 220, 0.8
    li.location = H(0, -2.6, 3.4)
    li.rotation_euler = (H(0, 0, 0.5) - li.location).to_track_quat('-Z', 'Y').to_euler()
    sc.collection.objects.link(li)
    dist, tz = float(arg('--cam-dist', 3.8)), float(arg('--cam-z', 0.5))
    target = H(0, 0, tz)
    DEVIATIONS.append(f'K Kameras: Abstand {dist} H statt 2,2 H und Ziel Z {tz} statt 0,35 – mit 85 mm und 2,2 H (0,66 m) zeigt das Bild '
                      'nur ≈ 0,93 H, der Helm ist mit Antenne 1,26 H hoch; ohne Tuch liegt die Helmmitte bei Z 0,5')
    out = {}
    for name, az, el in (('cam_front34', -35, 5), ('cam_left', -90, 0), ('cam_back34', 145, 0), ('cam_right', 90, 0)):
        cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
        cam.data.lens = 85
        a, e = math.radians(az), math.radians(el)
        cam.location = target + H(math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)) * dist
        cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
        sc.collection.objects.link(cam)
        sc.camera = cam
        sc.render.filepath = os.path.join(OUT, f'check_{name}.png')
        bpy.ops.render.render(write_still=True)
        out[name] = sc.render.filepath
        print('[scout] geschrieben', sc.render.filepath, flush=True)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    return out


def compare(renders):
    """ref_helm.png in vier gleich breite Teile schneiden und je neben das passende Render legen."""
    ref = os.path.join(OUT, 'ref_helm.png')
    if os.path.exists(REF):
        subprocess.run(['cp', REF, ref], check=True)
    if not os.path.exists(ref):
        NOTES.append('K ref_helm.png fehlt: kein Vergleich')
        return
    w = int(subprocess.run(['magick', 'identify', '-format', '%w', ref], capture_output=True, text=True).stdout)
    for i, name in enumerate(('cam_front34', 'cam_left', 'cam_back34', 'cam_right')):
        part = os.path.join(OUT, f'ref_{i}.png')
        subprocess.run(['magick', ref, '-crop', f'{w // 4}x+{i * (w // 4)}+0', '+repage', '-resize', 'x1024', part], check=True)
        subprocess.run(['magick', part, renders[name], '-resize', 'x1024', '+append', os.path.join(OUT, f'compare_{name}.png')], check=True)


def report(rows, errs, ant):
    L = ['# Helm „Scout“ – Bericht', '', f'- Datei: `{BLEND}`', f'- Renders: `check_<cam>.png`, Vergleich `compare_<cam>.png` in `{OUT}`',
         f'- Abnahme J: {"alle Kriterien erfüllt" if not errs else f"{len(errs)} offene Punkte"}', '',
         '## Hüllmaße (H; Breite X, Höhe Z, Tiefe Y)', '',
         '| Objekt | Soll B × H × T | Ist B × H × T | Abw. % (B/H/T) | Soll Zentrum X/Y/Z | Ist Zentrum X/Y/Z |', '|---|---|---|---|---|---|']
    for key, dim, ist, cs, ci, dev in rows:
        f = ' / '.join
        L.append(f'| {key} | {f(f"{v:.2f}" for v in dim[:1] + (dim[1], dim[2]))} | {f(f"{v:.3f}" for v in ist)} | '
                 f'{f(f"{v:+.1f}" for v in dev)} | {f("–" if v is None else f"{v:.2f}" for v in cs)} | {f(f"{v:.3f}" for v in ci)} |')
    L += ['', f'Antenne: Fuß Z (Ist) {ant.z:.3f} H', '', '## Abnahme J – offene Punkte', '']
    L += [f'- {e}' for e in errs] or ['- keine']
    L += ['', '## Messungen und Hinweise', ''] + [f'- {n}' for n in NOTES]
    L += ['', '## Abweichungen vom vorgegebenen Vorgehen', ''] + [f'- {d}' for d in DEVIATIONS]
    L += ['', '## Objekte', '', '| Objekt | Typ | Materialien |', '|---|---|---|']
    for o in sorted(coll('HELM').all_objects, key=lambda o: o.name):
        L.append(f'| {o.name} | {o.type} | {", ".join(m.name for m in o.data.materials if m)} |')
    open(os.path.join(OUT, 'REPORT.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('[scout] Bericht', os.path.join(OUT, 'REPORT.md'), flush=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    reset()
    hau, kin = section_A_B()
    vis, slots = section_C(hau, kin)
    screws = section_D(kin)
    pods, s2 = section_E(hau, kin)
    s3 = section_F(hau)
    section_G(hau)
    place_screws(screws + s2 + s3)
    if '--cloth' in ARGS:          # Nutzer 27.10.2026: „Lass das Tuch bitte (erstmal) weg“
        section_H()
    else:
        NOTES.append('H Tuch auf Wunsch des Nutzers vorerst weggelassen („Lass das Tuch bitte (erstmal) weg“); --cloth baut es')
    for m in ('MASSE', 'CUT_SPLIT'):
        if m in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[m], do_unlink=True)
    finish()
    rows, errs, ant = check()
    if '--no-render' not in ARGS:
        renders = cameras_and_render(int(arg('--samples', 32)))
        compare(renders)
    report(rows, errs, ant)
    print('[scout] fertig:', 'J erfüllt' if not errs else f'{len(errs)} offene Punkte', flush=True)


if __name__ == '__main__':
    main()
