"""Prüft den Sitz des Zielfernrohrs am gebauten Netz (Entscheidungsliste 1.1, 1b; seit 0.21 „Ironsight“ Konzept A: Sattel hinter dem
Auge, Fuß unter dem Objektiv): läuft in Blender, ohne Szene und ohne Render.

  blender -b --factory-startup -P tools/test_sight_seat.py [-- --json <datei>]

Für jede Familienwaffe mit Zielfernrohr (`Socket_Eye.sight_type` `scope` oder – seit 0.25, Z3 – `fullscreen`) wird das Modell mit Fasen und Durchbrüchen gebaut und
mit senkrechten Strahlen in der Mittelebene (x = 0, alle 0,5 mm entlang des Mittelrohrs) vermessen – keine Hülle, sondern die
tatsächliche Kontur:
- Spalt = Unterkante des Zielfernrohrs (`scope_tube`, `scope_eyepiece`) − Oberkante des Trägers darunter (Baugruppe `receiver` und
  Rohrsattel `scope_mount_r`): nirgends < −0,2 mm (kein Eindringen), auf mindestens 25 mm Länge ≤ 1 mm (das Rohr liegt auf).
  Bewusst geändert in 0.21 (Konzept A): vorher Rohr allein auf dem Gehäuse über 30 mm; hinter dem Augenpunkt liegen nur Okularende bis
  Auge (30 mm), dort trägt eine 26 mm lange Wiege auf dem Buckel. Gehäuse allein: das Zielfernrohr dringt nirgends ein.
- Visierhöhe = `Socket_Eye` über der Laufachse (`Socket_Muzzle`): 66 ± 4 mm (Visier-Standard).
- Visier über Gehäuse = höchster Punkt der Baugruppe `sight` − Gehäuseoberkante unter dem Rohr, geteilt durch die Modelllänge L:
  0,02–0,04 L (Destiny-Scouts); Scharfschütze (Vollbild, 0.25) 0,05–0,11 L (Destiny-Sniper, Motiongen proportionen › 2), gemessen
  über dem Gehäuse ohne Visierträger (Schienen, Sattelblock) wie das Destiny-Maß; über dem Träger steht in `sight_over_mount_L`.
- Kollision: die Optikteile (alle `sight`-Teile außer Sattel, Klemmfuß, Spannband und Klemmhebel) überschneiden kein Gehäuseteil
  (BVH-Überlappung).
- Sattel hinter dem Auge (Konzept A, 0.21): der Rohrsattel endet vorn spätestens am Augenpunkt (`Socket_Eye`).
- Zielbild frei (0.21, ersetzt „höchstens 1,5 mm über der Rohrunterkante“ von 0.19): Strahlen vom Augenpunkt (75°, 16:9) durch das
  untere Bilddrittel treffen kein Teil ohne `ads_hide` zwischen Auge und Objektivbeginn (je 0,5 mm Abstand zu Auge und Objektivkante) – dort stand 0.19 der Sattel mit Schiene.
  Bewusst geändertes Verhalten: 0.19 erlaubte einen flachen Sattel vor dem Auge.

Pinvisier B1 am Bogen (`sight_type` `pins`, 0.29): Strahlen vom Augenpunkt durch die lichte Ringöffnung (Raster 24 × 24, innerhalb r − 0,5)
treffen bis zur Ringebene kein Teil außer Pins und Pinschiene (der Fensterbogen des Mittelstücks liegt neben dem Sichtkegel); die Optik
(Ring, Pins, Sockel) überschneidet kein Teil des Bogens außer ihrem Träger (Schiene, Visierträger).
"""
import glob
import importlib
import json
import math
import os
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic import kit  # noqa: E402
from basic.reticles import SIGHT  # noqa: E402

MOUNTS = ('rail', 'rail_front', 'saddle_block')     # Visierträger auf dem Gehäuse (für „Visier über Gehäuse“ beim Vollbild)
CLAMP = ('scope_mount_r', 'scope_mount_f', 'sight_clamp', 'scope_strap')      # dürfen das Gehäuse berühren (Klemmung)
HFOV, ASPECT, GRID = 75.0, 9 / 16, (48, 16)
GAP_MAX, GAP_MIN, CONTACT_MM = 1.0, -0.2, 25.0
BAND = (0.02, 0.04)
BAND_TYPE = {'scope': BAND, 'fullscreen': (0.05, 0.11)}   # Scharfschütze (0.25): Destiny 0,05–0,11 L (Motiongen proportionen › 2)


def tree(obs):
    dg = bpy.context.evaluated_depsgraph_get()
    verts, polys = [], []
    for ob in obs:
        e = ob.evaluated_get(dg)
        me = e.to_mesh()
        k = len(verts)
        verts += [e.matrix_world @ v.co for v in me.vertices]
        polys += [[k + i for i in p.vertices] for p in me.polygons]
        e.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys), verts


def hit_z(t, f, down):
    """Erste Trefferhöhe (mm) eines senkrechten Strahls bei x = 0, Längslage f (mm); down: von oben, sonst von unten."""
    y = -f / 1000
    o, d = (Vector((0, y, 1.0)), Vector((0, 0, -1))) if down else (Vector((0, y, -1.0)), Vector((0, 0, 1)))
    loc = t.ray_cast(o, d)[0]
    return None if loc is None else loc.z * 1000


def measure(W):
    kit.reset_scene()
    _, objs, anc = kit.build(W)
    bpy.context.view_layer.update()
    by_asm = {}
    for p in W.PARTS:
        by_asm.setdefault(p['asm'], []).append(objs[p['id']])
    house, _ = tree(by_asm['receiver'])
    support, _ = tree(by_asm['receiver'] + [objs['scope_mount_r']])
    tube_p = next(p for p in W.PARTS if p['id'] == 'scope_tube')
    eye_p = next(p for p in W.PARTS if p['id'] == 'scope_eyepiece')
    tube, _ = tree([objs['scope_tube'], objs['scope_eyepiece']])
    _, sight_v = tree(by_asm['sight'])
    _, all_v = tree(list(objs.values()))
    fs = W.ANCHORS['Socket_Eye']['sight_type'] == 'fullscreen'
    a0, a1 = min(eye_p['a0'], tube_p['a0']) + 0.5, max(tube_p['a0'], tube_p['a1'])
    rows = []
    f = a0
    while f <= a1 + 1e-9:
        zt, zh, zs = hit_z(tube, f, down=False), hit_z(house, f, down=True), hit_z(support, f, down=True)
        if zt is not None and zh is not None:
            rows.append((round(f, 2), zt, zh, zt - zs, zt - zh))
        f += 0.5
    gaps = [r[3] for r in rows]
    contact = 0.5 * sum(1 for g in gaps if GAP_MIN <= g <= GAP_MAX)
    gap_house = min(r[4] for r in rows)
    house_top = max(r[2] for r in rows)
    # Vollbild (0.25): Destiny misst die Optik über dem Gehäuse, nicht über dem Visierträger – Schienen und Sattelblock zählen dort nicht
    body = [objs[p['id']] for p in W.PARTS if p['asm'] == 'receiver' and p['id'] not in MOUNTS]
    bt, _ = tree(body)
    body_top = max(z for z in (hit_z(bt, r[0], down=True) for r in rows) if z is not None)
    sight_top = max(v.z for v in sight_v) * 1000
    L = (max(v.y for v in all_v) - min(v.y for v in all_v)) * 1000
    eye = anc['Socket_Eye'].matrix_world.translation.z * 1000
    bore = anc['Socket_Muzzle'].matrix_world.translation.z * 1000
    optic, _ = tree([objs[p['id']] for p in W.PARTS if p['asm'] == 'sight' and p['id'] not in CLAMP])
    overlaps = optic.overlap(house)
    obj_f = next(p for p in W.PARTS if p['id'] == 'scope_objective')['a0']
    eye_f = W.ANCHORS['Socket_Eye']['at'][0]
    _, sv = tree([objs['scope_mount_r']])
    saddle_front = max(-v.y * 1000 for v in sv)
    vis, _ = tree([objs[p['id']] for p in W.PARTS if not p.get('ads_hide')])
    e = anc['Socket_Eye'].matrix_world.translation
    th = math.tan(math.radians(HFOV / 2))
    hits = []
    for i in range(GRID[0]):                 # unteres Bilddrittel: Höhe −tan_v … −tan_v/3
        for j in range(GRID[1]):
            tx = th * (-1 + (2 * i + 1) / GRID[0])
            ty = -th * ASPECT * (1 / 3 + (2 / 3) * (j + 0.5) / GRID[1])
            loc = vis.ray_cast(e, Vector((tx, -1.0, ty)).normalized())[0]
            if loc is not None and eye_f + 0.5 < -loc.y * 1000 < obj_f - 0.5:     # 0.25: Objektivhinterkante selbst zählt nicht
                hits.append(round(-loc.y * 1000, 1))
    return dict(weapon=f"{W.META['id']}-{W.META['variant']}", sight_type=W.ANCHORS['Socket_Eye']['sight_type'], tube_f=[a0, a1], tube_bottom_mm=round(min(r[1] for r in rows), 2),
                gap_min_mm=round(min(gaps), 2), gap_max_mm=round(max(gaps), 2), contact_mm=contact, gap_house_min_mm=round(gap_house, 2),
                house_top_mm=round(house_top, 2), sight_top_mm=round(sight_top, 2), length_mm=round(L, 1),
                sight_over_house_mm=round(sight_top - (body_top if fs else house_top), 2),
                sight_over_house_L=round((sight_top - (body_top if fs else house_top)) / L, 4),
                sight_over_mount_L=round((sight_top - house_top) / L, 4),
                sight_height_mm=round(eye - bore, 2), optic_overlaps=len(overlaps), eye_f=eye_f, objective_f=round(obj_f, 2),
                saddle_front_f=round(saddle_front, 2), ads_lower_third_hits=len(hits), ads_hit_f=[min(hits), max(hits)] if hits else None)


def check(m):
    bad = []
    if min(m['gap_min_mm'], m['gap_house_min_mm']) < GAP_MIN:
        bad.append(f"Rohr dringt in Gehäuse oder Sattel ein (Spalt min {m['gap_min_mm']} / {m['gap_house_min_mm']} mm)")
    if m['contact_mm'] < CONTACT_MM:
        bad.append(f"Rohr liegt nicht auf: Spalt ≤ {GAP_MAX:g} mm nur auf {m['contact_mm']:g} mm (min {m['gap_min_mm']} mm), "
                   f"Soll ≥ {CONTACT_MM:g} mm")
    h, tol = SIGHT['height_mm'], SIGHT['height_tol_mm']
    if abs(m['sight_height_mm'] - h) > tol:
        bad.append(f"Visierhöhe {m['sight_height_mm']} mm außerhalb {h:g} ± {tol:g} mm")
    b = BAND_TYPE[m['sight_type']]
    if not b[0] <= m['sight_over_house_L'] <= b[1]:
        bad.append(f"Visier über Gehäuse {m['sight_over_house_L']:.3f} L ({m['sight_over_house_mm']} mm) außerhalb "
                   f"{b[0]:.2f}–{b[1]:.2f} L")
    if m['saddle_front_f'] > m['eye_f'] + 1e-6:
        bad.append(f"Rohrsattel reicht bis f {m['saddle_front_f']} vor den Augenpunkt f {m['eye_f']} (Konzept A: hinter dem Auge)")
    if m['ads_lower_third_hits']:
        bad.append(f"im Zielbild unteres Drittel: {m['ads_lower_third_hits']} Strahlen treffen Teile zwischen Auge und Objektiv "
                   f"(f {m['ads_hit_f'][0]}–{m['ads_hit_f'][1]}; Sattel/Schiene vor dem Auge?)")
    if m['optic_overlaps']:
        bad.append(f"Optik überschneidet das Gehäuse ({m['optic_overlaps']} Dreieckspaare)")
    return bad


PIN_OK = ('sight_pin', 'sight_pin_1', 'sight_pin_2', 'sight_pin_blade_0', 'sight_pin_blade_1', 'sight_pin_blade_2', 'sight_pin_rail',
          'sight_pin_screws')
PIN_MOUNT = ('rail', 'sight_arm', 'sight_mount', 'sight_clamp')     # Träger: dürfen einander berühren (Klemmung)


def measure_pins(W):
    """Pinvisier B1 (0.29): freie Sicht durch den Ring am Netz und keine Überschneidung der Optik mit dem Bogen."""
    kit.reset_scene()
    _, objs, anc = kit.build(W)
    bpy.context.view_layer.update()
    e = anc['Socket_Eye'].matrix_world.translation
    fr = next(p for p in W.PARTS if p['id'] == 'sight_frame')
    hole = fr['cuts'][0]['pts']
    r, cap = max(q[0] for q in hole), -min(q[0] for q in hole)       # links rund, rechts bei −cap abgeflacht (Pinschiene)
    fp = (fr['f0'] + fr['f1']) / 2
    cx, cu = fr.get('cx', 0.0), fr['cu']
    others, _ = tree([objs[p['id']] for p in W.PARTS if p['id'] not in PIN_OK])
    hits, n = [], 0
    for i in range(24):
        for j in range(24):
            dx, du = (r - 0.5) * (-1 + (2 * i + 1) / 24), (r - 0.5) * (-1 + (2 * j + 1) / 24)
            if dx * dx + du * du > (r - 0.5) ** 2 or dx < -cap + 0.5:
                continue
            n += 1
            tgt = kit.to_xyz(fp, cu + du, cx + dx)
            d = tgt - e
            loc = others.ray_cast(e, d.normalized(), d.length)[0]
            if loc is not None:
                hits.append(round(-loc.y * 1000, 1))
    optic, _ = tree([objs[p['id']] for p in W.PARTS if p['asm'] == 'sight' and p['id'] not in PIN_MOUNT])
    rest, _ = tree([objs[p['id']] for p in W.PARTS if p['asm'] != 'sight' and p['id'] not in PIN_MOUNT])
    return dict(weapon=f"{W.META['id']}-{W.META['variant']}", sight_type='pins', rays=n, ring_hits=len(hits),
                ring_hit_f=[min(hits), max(hits)] if hits else None, optic_overlaps=len(optic.overlap(rest)))


def check_pins_mesh(m):
    bad = []
    if m['ring_hits']:
        bad.append(f"Zielbild durch den Ring: {m['ring_hits']} von {m['rays']} Strahlen treffen ein Teil (f {m['ring_hit_f'][0]}–"
                   f"{m['ring_hit_f'][1]}; Fensterbogen im Sichtkegel?)")
    if m['optic_overlaps']:
        bad.append(f"Pinvisier überschneidet den Bogen ({m['optic_overlaps']} Dreieckspaare)")
    return bad


def main():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    res, bad = [], []
    for f in sorted(glob.glob(os.path.join(ROOT, 'basic', 'pilot', 'w*_v21.py'))):
        W = importlib.import_module(os.path.relpath(f, ROOT)[:-3].replace(os.sep, '.'))
        if W.ANCHORS.get('Socket_Eye', {}).get('sight_type') == 'pins':
            m = measure_pins(W)
            res.append(m)
            print('[test_sight_seat]', json.dumps(m, ensure_ascii=False))
            bad += [f"{m['weapon']}: {b}" for b in check_pins_mesh(m)]
            continue
        if W.ANCHORS.get('Socket_Eye', {}).get('sight_type') not in BAND_TYPE:
            continue
        m = measure(W)
        res.append(m)
        print('[test_sight_seat]', json.dumps(m, ensure_ascii=False))
        bad += [f"{m['weapon']}: {b}" for b in check(m)]
    if '--json' in a:
        json.dump(res, open(a[a.index('--json') + 1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'[test_sight_seat] {len(res)} Zielfernrohre geprüft (mit Pinvisieren B1)')
    for b in bad:
        print('[test_sight_seat] FEHLER', b)
    sys.exit(1 if bad or not res else 0)


main()
