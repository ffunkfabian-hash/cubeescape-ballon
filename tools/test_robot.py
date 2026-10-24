"""Regressionstest der Roboterprüfung (Blender, ~3 s): die Ankerprüfung und der Spec-Vergleich müssen Fehler finden.

  blender -b --factory-startup -P tools/test_robot.py      → Ausgabe „test_robot: … geprüft“, Exit 1 bei Fehler

Fälle: (1) Kopf 130 mm angehoben → Lücke am Hals; (2) Kopf an die rechte Schulter versetzt (berührt den Schulterpanzer, Hals offen)
→ Lücke am Hals trotz Kontakt an anderer Stelle; (3) Oberschenkel 20 % dicker bei gleichen Teile-IDs → Spec veraltet;
(4) Grundstand → alles in Ordnung; (5) --dry rendert und schreibt nichts; (6, 7) unbekanntes Argument bzw. unbekannte Ansicht
(z. B. hangar) brechen ab.
"""
import os
import subprocess
import sys

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic import kit  # noqa: E402
from basic import robot as RB  # noqa: E402
from basic.robot import legs  # noqa: E402
import tools.robot_build as RBB  # noqa: E402

err = []


def run(name, expect_gap, expect_drift):
    kit.reset_scene()
    F = RBB.build('idle', mode='color')
    gaps = RBB.anchor_gaps(F['obs'])
    gap = gaps['Socket_Neck'] > RBB.GAP_TOL_MM
    drift = bool(RBB.spec_drift(F['obs'], gaps))
    if gap != expect_gap or drift != expect_drift:
        err.append(f'{name}: Lücke {gap} (erwartet {expect_gap}), Spec veraltet {drift} (erwartet {expect_drift})')


seg0, parts0 = RB.segments, legs.parts
run('Grundstand', False, False)
RB.segments = lambda: [(n, A, B, h, s) if n != 'head' else (n, (A[0], A[1], A[2] + 130), (B[0], B[1], B[2] + 130), h, s)
                       for n, A, B, h, s in seg0()]
run('Kopf angehoben', True, True)
RB.segments = lambda: [(n, A, B, h, s) if n != 'head' else (n, (-330, 0, 1420), (-330, 0, 1740), h, s) for n, A, B, h, s in seg0()]
run('Kopf an der Schulter', True, True)
RB.segments = seg0
legs.parts = lambda: [(p[0], p[1], p[2], p[3], p[4], dict(p[5], pts=[(x * 1.2, y * 1.2, z) for x, y, z in p[5]['pts']]))
                      if p[0] == 'thigh_body' else p for p in parts0()]
run('Oberschenkel dicker', False, True)
legs.parts = parts0


def cli(argv):
    r = subprocess.run([bpy.app.binary_path, '-b', '--factory-startup', '-P', os.path.join(ROOT, 'tools', 'robot_build.py'), '--', *argv],
                       capture_output=True, text=True)
    return r.returncode, r.stdout


# (5) --dry baut ready ohne Rendern und ohne Dateien; (6) unbekannte Argumente und Ansichten brechen ab, statt alles zu rendern
out = os.path.join(RBB.OUT, 'robot')
before = {f: os.path.getmtime(os.path.join(out, f)) for f in os.listdir(out)} if os.path.isdir(out) else {}
rc, so = cli(['--dry'])
after = {f: os.path.getmtime(os.path.join(out, f)) for f in os.listdir(out)} if os.path.isdir(out) else {}
if rc or 'dry: Aufbau ready ohne Rendern' not in so or 'geschrieben' in so or before != after:
    err.append('--dry rendert oder schreibt')
for argv in (['--bogus'], ['--only', 'hangar']):
    rc, so = cli(argv)
    if rc == 0 or 'geschrieben' in so:
        err.append(f'{argv} nicht abgelehnt')
print('test_robot: ' + ('; '.join(err) if err else '7 Fälle geprüft'))
sys.exit(1 if err else 0)
