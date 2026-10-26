"""Prüft den Sitz des Zielfernrohrs am gebauten Netz (Entscheidungsliste 1.1 A, 1b): läuft in Blender, ohne Szene und ohne Render.

  blender -b --factory-startup -P tools/test_sight_seat.py [-- --json <datei>]

Für jede Familienwaffe mit Zielfernrohr (`Socket_Eye.sight_type == 'scope'`) wird das Modell mit Fasen und Durchbrüchen gebaut und
mit senkrechten Strahlen in der Mittelebene (x = 0, alle 0,5 mm entlang des Mittelrohrs) vermessen – keine Hülle, sondern die
tatsächliche Kontur:
- Spalt = Unterkante `scope_tube` − Oberkante der Baugruppe `receiver` darunter: nirgends < −0,2 mm (kein Eindringen), auf
  mindestens 30 mm Länge ≤ 1 mm (das Rohr liegt auf).
- Visierhöhe = `Socket_Eye` über der Laufachse (`Socket_Muzzle`): 66 ± 4 mm (Visier-Standard).
- Visier über Gehäuse = höchster Punkt der Baugruppe `sight` − Gehäuseoberkante unter dem Rohr, geteilt durch die Modelllänge L:
  0,02–0,04 L (Destiny-Scouts).
- Kollision: die Optikteile (alle `sight`-Teile außer Sattel, Spannband und Klemmhebel) überschneiden kein Gehäuseteil (BVH-Überlappung).
- Im Zielen frei: `sight`-Teile ohne `ads_hide` reichen zwischen Auge und Objektivbeginn höchstens 1,5 mm über die Rohrunterkante
  (sonst stehen sie nah am Auge groß im Zielbild, z. B. ein Ring um das Rohr).
"""
import glob
import importlib
import json
import os
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic import kit  # noqa: E402
from basic.reticles import SIGHT  # noqa: E402

CLAMP = ('scope_mount_r', 'sight_clamp', 'scope_strap')      # dürfen das Gehäuse berühren (Klemmung)
ADS_TOL = 1.5
GAP_MAX, GAP_MIN, CONTACT_MM = 1.0, -0.2, 30.0
BAND = (0.02, 0.04)


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
    tube_p = next(p for p in W.PARTS if p['id'] == 'scope_tube')
    tube, _ = tree([objs['scope_tube']])
    _, sight_v = tree(by_asm['sight'])
    _, all_v = tree(list(objs.values()))
    a0, a1 = sorted((tube_p['a0'], tube_p['a1']))
    rows = []
    f = a0
    while f <= a1 + 1e-9:
        zt, zh = hit_z(tube, f, down=False), hit_z(house, f, down=True)
        if zt is not None and zh is not None:
            rows.append((round(f, 2), zt, zh, zt - zh))
        f += 0.5
    gaps = [r[3] for r in rows]
    contact = 0.5 * sum(1 for g in gaps if GAP_MIN <= g <= GAP_MAX)
    house_top = max(r[2] for r in rows)
    sight_top = max(v.z for v in sight_v) * 1000
    L = (max(v.y for v in all_v) - min(v.y for v in all_v)) * 1000
    eye = anc['Socket_Eye'].matrix_world.translation.z * 1000
    bore = anc['Socket_Muzzle'].matrix_world.translation.z * 1000
    optic, _ = tree([objs[p['id']] for p in W.PARTS if p['asm'] == 'sight' and p['id'] not in CLAMP])
    hits = optic.overlap(house)
    obj_f = next(p for p in W.PARTS if p['id'] == 'scope_objective')['a0']
    _, vis = tree([objs[p['id']] for p in W.PARTS if p['asm'] == 'sight' and not p.get('ads_hide')])
    near = [v.z * 1000 for v in vis if -v.y * 1000 < obj_f - 0.5]   # Objektiv selbst ausgenommen
    return dict(weapon=f"{W.META['id']}-{W.META['variant']}", tube_f=[a0, a1], tube_bottom_mm=round(min(r[1] for r in rows), 2),
                gap_min_mm=round(min(gaps), 2), gap_max_mm=round(max(gaps), 2), contact_mm=contact,
                house_top_mm=round(house_top, 2), sight_top_mm=round(sight_top, 2), length_mm=round(L, 1),
                sight_over_house_mm=round(sight_top - house_top, 2), sight_over_house_L=round((sight_top - house_top) / L, 4),
                sight_height_mm=round(eye - bore, 2), optic_overlaps=len(hits),
                ads_visible_top_mm=round(max(near), 2) if near else None)


def check(m):
    bad = []
    if m['gap_min_mm'] < GAP_MIN:
        bad.append(f"Rohr dringt ins Gehäuse ein (Spalt min {m['gap_min_mm']} mm)")
    if m['contact_mm'] < CONTACT_MM:
        bad.append(f"Rohr liegt nicht auf: Spalt ≤ {GAP_MAX:g} mm nur auf {m['contact_mm']:g} mm (min {m['gap_min_mm']} mm), "
                   f"Soll ≥ {CONTACT_MM:g} mm")
    h, tol = SIGHT['height_mm'], SIGHT['height_tol_mm']
    if abs(m['sight_height_mm'] - h) > tol:
        bad.append(f"Visierhöhe {m['sight_height_mm']} mm außerhalb {h:g} ± {tol:g} mm")
    if not BAND[0] <= m['sight_over_house_L'] <= BAND[1]:
        bad.append(f"Visier über Gehäuse {m['sight_over_house_L']:.3f} L ({m['sight_over_house_mm']} mm) außerhalb "
                   f"{BAND[0]:.2f}–{BAND[1]:.2f} L")
    if m['ads_visible_top_mm'] is not None and m['ads_visible_top_mm'] > m['tube_bottom_mm'] + ADS_TOL:
        bad.append(f"im Zielen sichtbares Visierteil bis u {m['ads_visible_top_mm']} mm, über der Rohrunterkante "
                   f"{m['tube_bottom_mm']} + {ADS_TOL:g} mm (ads_hide fehlt?)")
    if m['optic_overlaps']:
        bad.append(f"Optik überschneidet das Gehäuse ({m['optic_overlaps']} Dreieckspaare)")
    return bad


def main():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    res, bad = [], []
    for f in sorted(glob.glob(os.path.join(ROOT, 'basic', 'pilot', 'w*_v21.py'))):
        W = importlib.import_module(os.path.relpath(f, ROOT)[:-3].replace(os.sep, '.'))
        if W.ANCHORS.get('Socket_Eye', {}).get('sight_type') != 'scope':
            continue
        m = measure(W)
        res.append(m)
        print('[test_sight_seat]', json.dumps(m, ensure_ascii=False))
        bad += [f"{m['weapon']}: {b}" for b in check(m)]
    if '--json' in a:
        json.dump(res, open(a[a.index('--json') + 1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'[test_sight_seat] {len(res)} Zielfernrohre geprüft')
    for b in bad:
        print('[test_sight_seat] FEHLER', b)
    sys.exit(1 if bad or not res else 0)


main()
