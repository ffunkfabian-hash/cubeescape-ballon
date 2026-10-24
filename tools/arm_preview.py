"""Arm-Vorschau ohne Waffe: rechter BASIC-Roboterarm in einer Schauhaltung, Seitenansicht und Hand-Nahansichten.

  blender -b --factory-startup -P tools/arm_preview.py -- [--rig v1|v2] [--k 1.0] [--tag aktuell] [--gpu] [--samples N]

--k skaliert den Querschnitt von Ober- und Unterarm (nur Vorschau, ändert basic/arms nicht). Ausgabe:
<OUT>/arms/preview/<tag>_{seite,hand_offen,hand_faust,schraeg}.png
"""
import math
import os
import sys

import bpy
from mathutils import Vector, Matrix

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic import kit  # noqa: E402
import tools.blender_build as BB  # noqa: E402
import tools.ego_build as EB  # noqa: E402
from tools.paths import OUT  # noqa: E402

MM = 0.001


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    o = dict(rig='v2', k=1.0, tag='v2', gpu='--gpu' in a, samples=64)
    for i, v in enumerate(a):
        if v == '--k':
            o['k'] = float(a[i + 1])
        if v == '--rig':
            o['rig'] = a[i + 1]
        if v == '--tag':
            o['tag'] = a[i + 1]
        if v == '--samples':
            o['samples'] = int(a[i + 1])
    return o


def look(cam, pos, at, lens):
    cam.data.lens = lens
    cam.matrix_world = EB.mat((at - pos).normalized().to_track_quat('-Z', 'Y').to_matrix(), pos)


def main():
    o = args()
    if o['rig'] == 'v1':
        from basic.arms import robot_arm_v1
        EB.RA = robot_arm_v1
    kit.reset_scene()
    segs, pieces = EB.build_arm('R')
    if o['k'] != 1.0:               # Querschnitt (Segment-X/Y) von Ober- und Unterarm skalieren
        for ob in pieces.values():
            if ob.parent and ob.parent.name in ('R_upper', 'R_fore'):
                for v in ob.data.vertices:
                    v.co.x *= o['k']
                    v.co.y *= o['k']
    BB.setup_render(1200, o['samples'], gpu=o['gpu'], aaa=True, bloom=False, bg='mid')
    kit.set_mode(pieces, 'aaa')
    # Schauhaltung: Oberarm schräg nach vorn unten, Unterarm waagerecht nach vorn (−Y), Handrücken oben
    S = Vector((0, 0.62, 0.18))
    E = S + Vector((0, -0.6, -0.8)) * EB.RA.UPPER_MM * MM
    W = E + Vector((0, -1, 0)) * EB.RA.FORE_MM * MM
    up = Vector((0, 0, 1))
    H = EB.mat(EB.frame_from(Vector((0, -1, 0)), up), W)
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam'))
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    out = os.path.join(OUT, 'arms', 'preview')
    os.makedirs(out, exist_ok=True)
    hand_c = W + Vector((0, -0.09, 0))
    shots = [('seite', 'relaxed', Vector((-1.45, 0.22, 0.12)), (W + E) / 2 + Vector((0, 0.04, 0.02)), 50),
             ('hand_offen', 'open', Vector((-0.42, -0.30, 0.30)), hand_c, 60),
             ('hand_faust', 'grip', Vector((-0.40, -0.34, -0.12)), hand_c, 60),
             ('schraeg', 'relaxed', Vector((-0.62, -0.30, 0.42)), (W + E) / 2 + Vector((0, -0.04, -0.01)), 40)]
    for name, fp, pos, at, lens in shots:
        EB.solve_arm('R', segs, H, EB.RA.FINGER_POSES[fp], {})
        segs['upper'].matrix_world = EB.mat(EB.frame_from(E - S, Vector((0, 1, 0.3))), S)
        segs['fore'].matrix_world = EB.mat(EB.frame_from(W - E, up), E)
        bpy.context.view_layer.update()
        look(cam, pos, at, lens)
        bpy.context.scene.render.filepath = os.path.join(out, f"{o['tag']}_{name}.png")
        bpy.ops.render.render(write_still=True)
        print('geschrieben', bpy.context.scene.render.filepath)


if __name__ == '__main__':
    main()
