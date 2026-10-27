"""Helm „Scout“, Fassung „näher an der Referenz“ (Nutzer 27.10.2026: „Kannst du versuchen näher an die referenz zu kommen? … Die
Augen sehen sehr traurig aus“). Baut auf tools/helm_scout.py auf (gleiche Bausteine, Namen und Materialien) und weicht bewusst von
den Zahlen der Spezifikation ab, wo die Referenz (ref_helm.png, Konzeptblatt mit vier Ansichten) anders aussieht.

  blender -b --factory-startup -P tools/helm_scout_ref.py -- [--out DIR] [--no-render] [--samples N]

Unterschiede zur Spezifikationsfassung (stehen auch im Bericht):
  Kuppel rund statt Dachfacetten (dichte Querschnitte, glatt schattiert)
  Aufteilung wie in der Referenz: dunkel = Kuppel + durchgehende Gesichtsmaske, hell = Seiten-/Hinterkopfgehäuse unter dem
    Haubenrand (Z < 0,62 hinter der Maskenkante) + schmales Kieferband vorn (Z < 0,09); das Gehäuse sitzt 0,02 zurück, der
    Haubenrand steht hinten als Überstand
  Augen: kürzer, außen höher (14°, „streng“ statt traurig), breiter Steg
  Gesicht unter den Augen: Wangenplatten (je zwei mit schräger Fuge) und schwarzes Trapez mit erhabenen Leisten und Vertiefung
  Seiten: ovale Hörmuscheln mit Halterung zum Haubenrand, lange dünne Antenne auf der rechten, kurzer dicker Stab auf der linken
  Kabel geriffelt: von den Hörmuscheln nach unten und hinten um den Nacken, zweites Kabel zum Hinterkopfmodul
  Hinterkopf: flaches querrechteckiges Modul unter dem Haubenrand mit Feldern und Vertiefung; keine Panel-Nuten, keine Dachteile
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import helm_scout as HS  # noqa: E402
from helm_scout import H, S, arc, bvh, hit, obj, join, boolean, add_box, lathe, frame_of, cyl, rounded_rect, curve_obj  # noqa: E402
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

HS.OUT = os.path.expanduser(HS.arg('--out', '~/Library/Caches/CubeEscapeBallon/out/helm_scout_ref'))
HS.BLEND = os.path.join(HS.OUT, 'helm_scout.blend')

# Profile (H): runde Kuppel, Braue am weitesten vorn, Maske zum Kinn zurück, Hinterkopf rund und kompakt
HS.FRONT = arc((0.02, 1.00), (-0.40, 0.80), 0.62, 16, 1) + [(-0.46, 0.64), (-0.45, 0.50), (-0.43, 0.30), (-0.37, 0.08), (-0.34, 0.00)]
HS.BACK = arc((0.02, 1.00), (0.44, 0.78), 0.55, 16, 1) + [(0.48, 0.62), (0.48, 0.45), (0.45, 0.28), (0.40, 0.10), (0.32, 0.00), (-0.34, 0.00)]
HS.WIDTH = [(0.0, 0.58), (0.12, 0.62), (0.28, 0.72), (0.45, 0.80), (0.62, 0.84), (0.75, 0.83), (0.85, 0.79), (0.92, 0.72), (0.97, 0.58),
            (0.99, 0.40), (1.0, 0.16)]
# ebene Front nur an der Maske (bis zur Braue Z 0,66); darüber rundet die Kuppel auch in der Draufsicht (Runde 2: flache Stirnebene)
HS.FRONTW = [(0.0, 0.40), (0.12, 0.44), (0.40, 0.62), (0.66, 0.60), (0.70, 0.30), (0.76, 0.06), (1.0, 0.04)]
HS.VIS = dict(top=0.645, bot=0.40, wt=0.62, wb=0.56, cham=0.05, tilt=10, ahead=0.012, depth=0.03)
EYE = dict(len=0.16, h=0.045, x=0.13, z=0.535, rise=14)      # außen höher
SPLIT = dict(mask_y=-0.27, rim=0.62, jaw=0.09)
POD = dict(y=-0.02, z=0.42, w=0.24, h=0.33, cup_y=0.88, cup_z=1.28, R=0.12, t=0.10)
HS.DEVIATIONS = [
    'Fassung „näher an der Referenz“ (Nutzerwunsch): Zahlen der Spezifikation A–G bewusst verlassen, wo die Referenz anders aussieht; '
    'die Spezifikationsfassung bleibt mit tools/helm_scout.py reproduzierbar',
    'Kuppel rund (Querschnitte alle 0,01 H, glatt schattiert, Kanten erst ab 30° hart) statt Dachfacetten',
    'Aufteilung: Helm_Haube = Kuppel + Gesichtsmaske, Helm_Kinnteil = helles Gehäuse an Seiten und Hinterkopf unter dem Haubenrand '
    f"(Z < {SPLIT['rim']}, hinter Y {SPLIT['mask_y']}) und Kieferband vorn (Z < {SPLIT['jaw']})",
    f"Augen {EYE['len']} × {EYE['h']}, Mitte X ±{EYE['x']} / Z {EYE['z']}, außen {EYE['rise']}° höher (C2: außen 6° tiefer wirkte traurig)",
    'Helm_Visier enthält die ganze Gesichtsmaske: Augenplatte mit Rahmen, Wangenplatten (je zwei mit Fuge) und schwarzes Trapez',
    'Helm_Pod_*: ovale Hörmuscheln (0,19 × 0,28) auf einer Sockelplatte am Gehäuse; Helm_Pod_Kasten_* ist die Halterung zum Haubenrand',
    'Antennen auf den Hörmuscheln: Helm_Antenne lang und dünn rechts (+X), Helm_Antenne_Kurz links (zusätzliches Objekt)',
    'Schläuche als geriffelte Kabel: *1 von der Hörmuschel nach unten und hinten um den Nacken, *2 zum Hinterkopfmodul',
    'Helm_Block_Hinten flach und querrechteckig (0,30 × 0,14 × 0,05) statt Grundplatte mit Zylinder',
    'Keine Panel-Nuten, Sensorfenster, Lüftungsrippe oder Nackenlasche (in der Referenz nicht sichtbar)',
]
HS.NOTES = ['K Vergleich mit der Referenz, drei Runden: (1) Aufteilung, Augen, Gesicht, Hörmuscheln, Kabel, Hinterkopfmodul; '
            '(2) Kuppel oben breiter, Hörmuscheln größer; (3) Querschnitte der Kuppel als Superellipsen (Giebel weg). Unterhalb Z 0,60 '
            'bleibt der Querschnitt der Spezifikationsfassung, weil das Kinnteil mit Superellipsen beim Aushöhlen brach',
            'Verbleibende Abweichungen zur Referenz: Kuppel etwas kantiger und höher, Hörmuscheln kleiner und ohne Bügel über den '
            'Kopf, Kabel geriffelt statt eng gewendelt, Kieferband schmaler, keine Gebrauchsspuren; Tuch weggelassen (Nutzerwunsch)']


def ref_section(z):
    """Querschnitt (Runde 3): zwei Viertel-Superellipsen statt Front + 45°-Ecke. Vorn an der Maske flach mit Knick zu den Schläfen
    (n 4,5 bis Z 0,66), darüber rund (n 2,2 ab Z 0,74), hinten breit gerundet (n 3,0); breiteste Stelle bei 45 % der Tiefe."""
    if z < 0.60:                   # unten wie bisher (mit Superellipsen brach das Kinnteil beim Aushöhlen)
        return _section0(z)
    yf, yb = HS.interp_z(HS.FRONT, z), HS.interp_z(HS.BACK, z)
    W = HS.lerp_tab(HS.WIDTH, z) / 2
    if yb - yf < 1e-4:
        return [(x, yf) for x in (-W, W)]
    ym = yf + 0.45 * (yb - yf)
    u = min(1.0, max(0.0, (z - 0.66) / 0.08))
    nf, nb = 4.5 + (2.2 - 4.5) * u, 3.0
    pts = []
    for k in range(25):
        t = math.radians(90 * k / 24)
        s_, c_ = math.sin(t), math.cos(t)
        for sx in (-1, 1):
            pts.append((sx * W * s_ ** (2 / nf), ym - (ym - yf) * c_ ** (2 / nf)))
            pts.append((sx * W * c_ ** (2 / nb), ym + (yb - ym) * s_ ** (2 / nb)))
    return pts


_section0 = HS.section
HS.section = ref_section


def split_cutter():
    bm = bmesh.new()
    m, r, j = SPLIT['mask_y'], SPLIT['rim'], SPLIT['jaw']
    yz = [(-0.8, -0.2), (1.0, -0.2), (1.0, r), (m, r), (m, j), (-0.8, j)]
    HS.prism(bm, [(y * S, z * S) for y, z in yz], 1.2 * S, H(-0.6, 0, 0), Vector((0, 1, 0)), Vector((0, 0, 1)), Vector((1, 0, 0)))
    return obj('CUT_SPLIT', bm, ['MAT_Kinn'], 'HELM_HILFE')


def section_A_B():
    HS.split_cutter = split_cutter
    hau, kin = HS.section_A_B()
    return hau, kin


def th(z):
    """Halbe Breite des Gesichtstrapezes (oben 0,05 bei Z 0,39, unten 0,10 bei Z 0,12)."""
    return 0.10 - 0.05 * (min(max(z, 0.12), 0.39) - 0.12) / 0.27


def face_plate(tree, name, pts, thick, mat_name):
    return HS.plate_on_surface(tree, name, [(x * S, z * S) for x, z in pts], H(0, -0.47, 0), Vector((1, 0, 0)), Vector((0, 0, 1)),
                               Vector((0, -1, 0)), thick * S, [mat_name])


def section_C(hau):
    vis = HS.build_visor()
    boolean(hau, HS.visor_cutter(), 'DIFFERENCE')
    slots = []
    for side, sx in (('L', -1), ('R', 1)):
        x, z = sx * EYE['x'], EYE['z']
        ys = HS.visor_y(x, z, 0.015)
        R = Matrix.Rotation(math.radians(sx * HS.VIS['tilt']), 3, 'Z') @ Matrix.Rotation(math.radians(-sx * EYE['rise']), 3, 'Y')
        bm = bmesh.new()
        add_box(bm, H(x, ys - 0.006, z), H(EYE['len'], 0.02, EYE['h']), R)
        boolean(vis, obj('CUT_SLOT', bm, ['MAT_Visier'], 'HELM_HILFE'), 'DIFFERENCE')
        bm = bmesh.new()
        geo = add_box(bm, H(x, ys + 0.006, z), H(EYE['len'] - 0.002, 0.004, EYE['h'] - 0.002), R)
        for f in {f for v in geo for f in v.link_faces}:
            f.material_index = 1 if (R.transposed() @ f.normal).y < -0.9 else 0
        slots.append(obj(f'Helm_Leuchtschlitz_{side}', bm, ['MAT_Visier', 'MAT_Emission']))
    # Gesicht unter den Augen: Trapez (schwarz) mit erhabenen Leisten und Vertiefung, Wangenplatten mit schräger Fuge
    tree = bvh(hau)
    parts = [face_plate(tree, 'F_TRAP', [(-0.10, 0.12), (0.10, 0.12), (0.05, 0.39), (-0.05, 0.39)], 0.010, 'MAT_Visier')]
    ytop = min(v.co.y for v in parts[0].data.vertices if v.co.z > 0.33 * S)
    bm = bmesh.new()
    add_box(bm, (0, ytop, 0.345 * S), H(0.04, 0.012, 0.03))
    boolean(parts[0], obj('CUT_TRAP', bm, ['MAT_Visier'], 'HELM_HILFE'), 'DIFFERENCE')
    for sx in (-1, 1):
        def m(pts, sx=sx):
            q = [(sx * x, z) for x, z in pts]
            return q if sx > 0 else q[::-1]
        parts.append(face_plate(tree, 'F_LEISTE', m([(th(0.12) - 0.022, 0.12), (th(0.12), 0.12), (th(0.39), 0.39), (th(0.39) - 0.02, 0.39)]),
                                0.018, 'MAT_Visier'))
        parts.append(face_plate(tree, 'F_WANGE_O', m([(th(0.39) + 0.012, 0.39), (0.27, 0.39), (0.265, 0.318), (th(0.215) + 0.012, 0.215)]),
                                0.012, 'MAT_Haube'))
        parts.append(face_plate(tree, 'F_WANGE_U', m([(th(0.20) + 0.012, 0.20), (0.262, 0.302), (0.24, 0.16), (0.21, 0.125),
                                                      (th(0.125) + 0.012, 0.125)]), 0.012, 'MAT_Haube'))
    join(vis, parts)
    HS.cleanup(vis)
    HS.save('C')
    return vis, slots


def section_D(kin):
    tree = bvh(kin)
    bm = bmesh.new()                                  # Lüftungsschlitze im Kieferband
    for gx in (-0.10, 0.10):
        for k in (-1, 0, 1):
            loc, nor = hit(tree, H(gx + k * 0.025, -1.0, 0.045), (0, 1, 0))
            if loc is not None:
                add_box(bm, loc, H(0.012, 0.02, 0.035))
    boolean(kin, obj('CUT_VENT', bm, ['MAT_Kinn'], 'HELM_HILFE'), 'DIFFERENCE')
    tree = bvh(kin)
    rast, spots = [], []
    for sx in (-1, 1):                                # rundes Rastelement mit Schraube am Gehäuse
        loc, nor = hit(tree, H(sx * 1.0, -0.16, 0.24), (-sx, 0, 0))
        bm = bmesh.new()
        lathe(bm, [(0, -0.002 * S), (0.025 * S, -0.002 * S), (0.025 * S, 0.005 * S), (0.022 * S, 0.008 * S), (0, 0.008 * S)],
              frame_of(nor), loc, 32)
        rast.append(obj('RAST', bm, ['MAT_Metall']))
        spots.append((loc + nor * 0.008 * S, nor, 1.0))
    join(kin, rast)
    HS.cleanup(kin)
    HS.save('D')
    return spots


def section_E(hau, kin):
    tree = bvh(kin)
    spots, cups = [], {}
    for side, sx in (('L', -1), ('R', 1)):
        ax = Vector((sx, 0, 0))
        base = HS.plate_on_surface(tree, f'Helm_Pod_{side}', rounded_rect(POD['w'] * S, POD['h'] * S, 0.03 * S, 6), H(sx * 0.40, POD['y'], POD['z']),
                                   Vector((0, 1, 0)), Vector((0, 0, 1)), ax, 0.015 * S, ['MAT_Pod'])
        bx = max(v.co.x * sx for v in base.data.vertices) / S
        R, f, t = POD['R'], 0.012, POD['t']
        x0, x1 = bx - 0.005, bx + t

        def dome(r):
            return x1 + 0.008 * (1 - (r / (R - f)) ** 2)
        prof = [(0, x0), (R, x0), (R, x1 - f), (R - f, x1), (0.083, dome(0.083)), (0.083, dome(0.083) - 0.003),
                (0.077, dome(0.077) - 0.003), (0.077, dome(0.077)), (0, x1 + 0.008)]
        bm = bmesh.new()
        lathe(bm, [(r * S, a * S) for r, a in prof], Matrix(((sx, 0, 0), (0, 1, 0), (0, 0, 1))), H(0, POD['y'], POD['z']), 48)
        c0 = H(0, POD['y'], POD['z'])
        for v in bm.verts:                            # oval: schmaler in Y, höher in Z
            v.co.y = c0.y + (v.co.y - c0.y) * POD['cup_y']
            v.co.z = c0.z + (v.co.z - c0.z) * POD['cup_z']
        join(base, [obj('CUP', bm, ['MAT_Pod'])])
        HS.cleanup(base)
        cups[sx] = (bx, x1)
        hz = R * POD['cup_z']
        for dy in (-0.08, 0.08):
            for dz in (-0.12, 0.12):
                spots.append((H(sx * bx, POD['y'] + dy, POD['z'] + dz), ax, 1.0))
        # Halterung: senkrechter Bügel von der Hörmuschel zum Haubenrand, oben eingehakt
        bm = bmesh.new()
        z0, z1 = POD['z'] + hz * 0.6, SPLIT['rim'] + 0.035
        add_box(bm, H(sx * (bx + 0.012), POD['y'], (z0 + z1) / 2), H(0.022, 0.05, z1 - z0))
        add_box(bm, H(sx * (bx - 0.005), POD['y'], z1 - 0.008), H(0.04, 0.05, 0.022))
        obj(f'Helm_Pod_Kasten_{side}', bm, ['MAT_Pod'])
        # Stecker vorn an der Hörmuschel, Kabel zum Gehäuse vorn unten
        yfront = POD['y'] - R * POD['cup_y']
        bm = bmesh.new()
        cyl(bm, 0.0125 * S, 0.03 * S, H(sx * (bx + t / 2), yfront - 0.01, POD['z'] - 0.03), (0, 1, 0), 24)
        st = obj(f'Helm_Pod_Stecker_{side}', bm, ['MAT_Metall', 'MAT_Gummi'])
        end, _ = hit(bvh(kin), H(sx * 1.0, -0.22, 0.14), (-sx, 0, 0))
        p0 = H(sx * (bx + t / 2), yfront - 0.025, POD['z'] - 0.03)
        cab = curve_obj('KABEL', [p0, (p0 + end) / 2 + H(sx * 0.03, -0.03, 0), end], 0.005 * S, 'MAT_Gummi', 'HELM')
        join(st, [HS.to_mesh(cab)])
    # rechts: Kabelverteiler auf der Sockelplatte mit Kurzkabel zur Halterung
    bx, x1 = cups[1]
    bm = bmesh.new()
    add_box(bm, H(bx + 0.015, POD['y'] + 0.085, POD['z'] + 0.12), H(0.03, 0.03, 0.05))
    box2 = obj('Helm_Pod_Box2_R', bm, ['MAT_Pod', 'MAT_Gummi'])
    bv = box2.modifiers.new('BEVEL', 'BEVEL')
    bv.width, bv.segments = 0.003 * S, 2
    kab = curve_obj('KABEL2', [H(bx + 0.02, POD['y'] + 0.07, POD['z'] + 0.145), H(bx + 0.03, POD['y'] + 0.02, POD['z'] + 0.19)],
                    0.004 * S, 'MAT_Gummi', 'HELM')
    join(box2, [HS.to_mesh(kab)])
    # Antennen auf den Hörmuscheln: rechts lang und dünn bis 5 % über den Scheitel, links kurz, dick, nach außen geneigt mit Endkappe
    top = POD['z'] + POD['R'] * POD['cup_z']
    for side, sx in (('R', 1), ('L', -1)):
        bxs, x1s = cups[sx]
        foot = H(sx * (bxs + x1s) / 2, POD['y'] - 0.05, top - 0.01)
        bm = bmesh.new()
        lathe(bm, [(0, 0), (0.016 * S, 0), (0.016 * S, 0.02 * S), (0.008 * S, 0.034 * S), (0, 0.034 * S)], frame_of((0, 0, 1)), foot, 24)
        a0 = foot + Vector((0, 0, 0.03 * S))
        if sx > 0:
            tip = H(sx * (bxs + x1s) / 2 + 0.02, POD['y'] - 0.06, 1.05)
            d = (tip - a0).normalized()
            cyl(bm, 0.004 * S, (tip - a0).length, (a0 + tip) / 2, d, 12)
            sph = bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.006 * S)
            for v in sph['verts']:
                v.co += tip
            obj('Helm_Antenne', bm, ['MAT_Pod'])
        else:
            tl = math.radians(12)
            d = Vector((-math.sin(tl), 0, math.cos(tl)))
            b1 = a0 + d * 0.19 * S
            cyl(bm, 0.015 * S, 0.19 * S, (a0 + b1) / 2, d, 20)
            cyl(bm, 0.0225 * S, 0.035 * S, b1 - d * 0.012 * S, d, 24, mat_index=1)
            obj('Helm_Antenne_Kurz', bm, ['MAT_Pod', 'MAT_Gummi'])
    HS.save('E')
    return cups, spots


def away(tree, p, gap):
    """Punkt p mindestens gap (m) vor der Oberfläche halten."""
    loc, nor, _, d = tree.find_nearest(p)
    if loc is not None and d < gap:
        return loc + nor * gap
    return p


def section_F(kin, cups):
    tree = bvh(kin)
    blk = HS.plate_on_surface(tree, 'Helm_Block_Hinten', rounded_rect(0.30 * S, 0.14 * S, 0.015 * S, 4), H(0, 0.50, 0.52),
                              Vector((1, 0, 0)), Vector((0, 0, 1)), Vector((0, 1, 0)), 0.05 * S, ['MAT_Pod', 'MAT_Visier'])
    yb = max(v.co.y for v in blk.data.vertices) / S
    bm = bmesh.new()
    for sx in (-1, 1):
        add_box(bm, H(sx * 0.07, yb + 0.004, 0.525), H(0.11, 0.008, 0.08), mat_index=1)
    add_box(bm, H(0, yb + 0.002, 0.525), H(0.025, 0.006, 0.08), mat_index=0)
    inl = {}
    for sx in (-1, 1):
        y_in = (min(v.co.y for v in blk.data.vertices if v.co.x * sx > 0.12 * S) / S + yb) / 2
        inl[sx] = H(sx * 0.17, y_in, 0.50)
        cyl(bm, 0.017 * S, 0.035 * S, H(sx * 0.16, y_in, 0.50), (1, 0, 0), 20)
    join(blk, [obj('BLOCK_TEILE', bm, ['MAT_Pod', 'MAT_Visier'])])
    HS.cleanup(blk)
    spots = [(H(sx * 0.12, yb, 0.575), Vector((0, 1, 0)), 1.25) for sx in (-1, 1)]
    taper = HS.rib_taper()
    gap = 0.03 * S
    for side, sx in (('L', -1), ('R', 1)):
        bx, x1 = cups[sx]
        xm = sx * (bx + x1) / 2
        zb = POD['z'] - POD['R'] * POD['cup_z']
        paths = {'1': [H(xm, POD['y'], zb + 0.01), away(tree, H(sx * 0.40, 0.22, 0.15), gap), away(tree, H(sx * 0.10, 0.46, 0.12), gap)],
                 '2': [H(xm, POD['y'] + 0.08, POD['z'] + 0.02), away(tree, H(sx * 0.33, 0.36, 0.52), gap), inl[sx]]}
        for k, pts in paths.items():
            cu = curve_obj(f'Helm_Schlauch_{side}{k}', pts, 0.013 * S, 'MAT_Gummi', 'HELM', taper=taper, res=256)
            P = HS.curve_points(cu)
            for end, (a, b) in (('a', (P[0], P[3])), ('b', (P[-1], P[-4]))):
                bm = bmesh.new()
                d = (a - b).normalized()
                cyl(bm, 0.018 * S, 0.035 * S, a - d * 0.008 * S, d, 24)
                obj(f'Helm_Huelse_{side}{k}{end}', bm, ['MAT_Metall'])
    HS.save('F')
    return spots


def main():
    os.makedirs(HS.OUT, exist_ok=True)
    HS.reset()
    hau, kin = section_A_B()
    vis, slots = section_C(hau)
    s1 = section_D(kin)
    cups, s2 = section_E(hau, kin)
    s3 = section_F(kin, cups)
    HS.place_screws(s1 + s2 + s3)
    for m in ('MASSE', 'CUT_SPLIT'):
        if m in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[m], do_unlink=True)
    HS.NAMES = [n for n in HS.NAMES if not n.startswith('Tuch_')] + ['Helm_Antenne_Kurz']
    HS.SOLL = {}                                       # Hüllmaße der Spezifikation gelten für diese Fassung nicht
    HS.finish()
    rows, errs, ant = HS.check()
    if '--no-render' not in HS.ARGS:
        HS.compare(HS.cameras_and_render(int(HS.arg('--samples', 48))))
    HS.report(rows, errs, ant)
    print('[scout-ref] fertig:', 'J erfüllt' if not errs else f'{len(errs)} offene Punkte', flush=True)


main()
