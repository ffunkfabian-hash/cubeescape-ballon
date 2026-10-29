"""Leuchtteile (`move.kind glow`) sitzen in der Ego-Szene an der Waffe (0.32 „Softgrip“, Patch aus 0.30 Vorschlag 6).

  blender -b --factory-startup -P tools/test_ego_glow.py

`ego_build.Scene.set_weapon` setzte Leuchtteile nach der Waffenmatrix über `blender_build.apply_move` zurück in die Ruhelage: die
Salvenanzeigen von BASIC-02 schwebten in Blender-Ego-Bildern oben im Bild. Geprüft wird je spielbarer Waffe mit Leuchtteilen (heute nur
BASIC-02; Ego-Profile gibt es nur für tools/export_unity.WEAPONS) die Lage relativ zur Waffe bzw. zum Elternteil bei gedrehter,
verschobener Waffe, an und aus; Gegenprobe: das alte Verhalten (apply_move nach set_weapon) muss gemeldet werden.
"""
import importlib
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools import ego_build as EB  # noqa: E402
import tools.blender_build as BB  # noqa: E402
from tools.export_unity import WEAPONS  # noqa: E402

TOL_MM = 0.01
R = Matrix.Rotation(math.radians(25), 3, 'X') @ Matrix.Rotation(math.radians(-40), 3, 'Z')
POS = Vector((0.12, -0.35, -0.21))


def glow_parts(W):
    return [p for p in W.PARTS if p.get('move', {}).get('kind') == 'glow']


def off_mm(sc, p):
    """Abstand (mm) der Lage des Teils von seiner Ruhelage relativ zur Waffe bzw. zum Elternteil."""
    ob = sc.objs[p['id']]
    par = sc.objs.get(p.get('parent_part'))
    base = par.matrix_world @ Matrix(par['rest']).inverted() if par is not None else sc.root.matrix_world
    return ((base @ Matrix(ob['rest'])).translation - ob.matrix_world.translation).length * 1000


bad, n = [], 0
for mod in WEAPONS:
    W = importlib.import_module(f'basic.{mod}')
    if not glow_parts(W):
        continue
    sc = EB.Scene(W, dict(gpu=False, samples=1, fx=False))
    G = glow_parts(W)
    for t in (0.0, 1.0):
        sc.set_weapon(R, POS, {p['id']: t for p in G}, {})
        for p in G:
            n += 1
            d = off_mm(sc, p)
            if d > TOL_MM:
                bad.append(f"{W.META['id']}/{p['id']} (t {t:g}): {d:.1f} mm neben der Waffe")
    p = G[0]                                       # Gegenprobe: alter Ablauf setzt die Lage ohne Waffenmatrix
    BB.apply_move(sc.objs[p['id']], p['move'], 1.0)
    bpy.context.view_layer.update()
    if off_mm(sc, p) < 1.0:
        bad.append(f"{W.META['id']}/{p['id']}: Gegenprobe (apply_move nach set_weapon) nicht erkannt")
if n == 0:
    bad.append('keine spielbare Waffe mit Leuchtteilen gefunden')
print(f'[test_ego_glow] {n} Leuchtteil-Lagen geprüft')
for b in bad:
    print('[test_ego_glow] FEHLER', b)
sys.exit(1 if bad else 0)
