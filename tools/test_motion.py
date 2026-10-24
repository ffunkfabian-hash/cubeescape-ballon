"""Prüft den Drehsinn aller beweglichen Teile mit `move.expect` (läuft in Blender, ohne Szene und ohne Render).

  blender -b --factory-startup -P tools/test_motion.py
expect = (Punkt (f,u,x) mm, Richtung (f,u,x)): Bei voller Bewegung (t = 1) muss sich der Punkt in diese Richtung bewegen
(Skalarprodukt > 30 % der Verschiebung). Fängt vertauschte Vorzeichen (Abzug nach vorn, Deckel ins Gehäuse).
"""
import glob
import importlib
import os
import sys

from mathutils import Matrix

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic import kit  # noqa: E402
import tools.blender_build as B  # noqa: E402

bad, n = [], 0
for f in sorted(glob.glob(os.path.join(ROOT, 'basic', 'weapons', 'w*.py'))):
    W = importlib.import_module('basic.weapons.' + os.path.basename(f)[:-3])
    for p in W.PARTS:
        mv = p.get('move')
        if not mv or 'expect' not in mv:
            continue
        n += 1
        ob = {'rest': Matrix.Translation(kit.to_xyz(*mv['pivot']))}
        pt, d = mv['expect']
        p0 = kit.to_xyz(*pt)
        M = B.move_matrix(ob, mv, 1.0)
        delta = M @ Matrix.Translation(kit.to_xyz(*mv['pivot'])).inverted() @ p0 - p0
        dv = kit.to_xyz(*d).normalized()
        if delta.length < 1e-4 or delta.normalized().dot(dv) < 0.3:
            fux = (round(-delta.y * 1000), round(delta.z * 1000), round(delta.x * 1000))
            bad.append(f"{W.META['id']}/{p['id']}: bewegt sich (f,u,x) {fux} mm statt Richtung {d}")
print(f'[test_motion] {n} Bewegungen geprüft')
for b in bad:
    print('[test_motion] FEHLER', b)
sys.exit(1 if bad else 0)
