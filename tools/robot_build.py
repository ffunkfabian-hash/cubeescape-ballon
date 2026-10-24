"""BASIC-Roboter (Spaßfigur) mit Arm v3 und Pilotwaffe in tiefer Bereitschaft – Standbilder.

  blender -b --factory-startup -P tools/robot_build.py -- [--gpu] [--samples N] [--res 1000] [--dry]

Figur aus basic/arms/robot_figure.py, Arme aus robot_arm.py (Zwei-Knochen-IK von der Schulter zum Griff aus ego.GRIPS).
Ausgabe: <OUT>/robot/{hero,nah,seite}.png, <OUT>/robot/robot.blend
"""
import importlib
import math
import os
import sys

import bpy
from mathutils import Vector, Matrix

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic import kit  # noqa: E402
from basic.arms import robot_figure as FIG  # noqa: E402
import tools.blender_build as BB  # noqa: E402
import tools.ego_build as EB  # noqa: E402
from tools.paths import OUT  # noqa: E402

MM = 0.001
WEAPON = 'pilot.w01_auto_rifle_v21'


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    o = dict(gpu='--gpu' in a, dry='--dry' in a, samples=96, res=1000)
    for k in ('samples', 'res'):
        if f'--{k}' in a:
            o[k] = int(a[a.index(f'--{k}') + 1])
    return o


def build_figure():
    parts = FIG.parts()
    obs = {}
    for name, A, B, hint, side in FIG.segments():
        A, B = Vector(A) * MM, Vector(B) * MM
        e = bpy.data.objects.new(f'FIG_{name}', None)
        bpy.context.scene.collection.objects.link(e)
        e.matrix_world = EB.mat(EB.frame_from(B - A, Vector(hint)), A)
        kind_of = name.split('_')[0]
        sx = -1 if side == 'L' else 1
        for pid, de, seg, kind, role, p in parts:
            if seg != kind_of:
                continue
            p = dict(p)
            if 'c' in p:
                p['c'] = [sx * p['c'][0], p['c'][1], p['c'][2]]
            if kind == 'hull':
                p['pts'] = [(sx * x, y, z) for x, y, z in p['pts']]
            ob = EB.piece_mesh(f'{name}_{pid}', kind, p)
            if kind == 'hull':          # v2: gerundete Querschnitte glatt, echte Kanten bleiben scharf
                for f in ob.data.polygons:
                    f.use_smooth = True
                ob.data.set_sharp_from_angle(angle=math.radians(40))
            ob.data.materials.append(kit.material(role))
            kit.add_bevel(ob, p.get('bevel', {'cyl': 0.8, 'hull': 2.0}.get(kind, 1.0)))
            ob.parent = e
            ob.matrix_parent_inverse = Matrix.Identity(4)
            obs[ob.name] = ob
    return obs


def two_bone(S, Wp, a, b, pole):
    d = Wp - S
    L = min(d.length, a + b - 1e-4)
    if d.length > a + b:
        print(f'Warnung: Griff {d.length:.3f} m außer Reichweite ({a + b:.3f} m)')
    x = (a * a - b * b + L * L) / (2 * L)
    h = math.sqrt(max(a * a - x * x, 0.0))
    u = d.normalized()
    pv = pole - u * pole.dot(u)
    return S + u * x + pv.normalized() * h


def pose_arms(WM):
    RA = EB.RA
    pw = (lambda pid: WM)
    for side, grip, S, pole, out in (('R', 'grip', Vector((-0.245, 0.0, 1.43)), Vector((-0.6, 0.5, -0.5)), Vector((-1, 0, 0))),
                                     ('L', 'support', Vector((0.245, 0.0, 1.43)), Vector((0.7, 0.2, -0.6)), Vector((1, 0, 0)))):
        segs, pieces = EB.build_arm(side)
        kit.set_mode(pieces, 'aaa')
        H, fp = EB.grip_hand(grip, pw)
        EB.solve_arm(side, segs, H, RA.FINGER_POSES[fp], {})
        Wp = H.translation
        E = two_bone(S, Wp, RA.UPPER_MM * MM, RA.FORE_MM * MM, pole)
        segs['upper'].matrix_world = EB.mat(EB.frame_from(E - S, out), S)
        segs['fore'].matrix_world = EB.mat(EB.frame_from(Wp - E, H.to_3x3().col[1]), E)
        bend = math.degrees((Wp - E).angle(H.to_3x3().col[2]))
        print(f'{side}: Ellbogen {E.x:+.3f} {E.y:+.3f} {E.z:+.3f}, Handgelenk {bend:.0f}°')


def lights():
    for nm, loc, en, size in (('Key', (-2.6, -3.0, 3.4), 900, 3.0), ('Fill', (3.0, -1.8, 1.6), 260, 3.0),
                              ('Rim', (1.0, 3.2, 3.0), 600, 2.5)):
        o = bpy.data.objects[nm]
        o.location = loc
        o.data.energy = en
        o.data.size = size
        o.rotation_euler = (Vector((0, 0, 1.0)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0))
    fl = bpy.context.active_object
    m = bpy.data.materials.new('Boden')
    m.use_nodes = True
    bsdf = m.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (0.09, 0.10, 0.115, 1)
    bsdf.inputs['Roughness'].default_value = 0.85
    fl.data.materials.append(m)


def main():
    o = args()
    kit.reset_scene()
    BB.setup_render(o['res'], o['samples'], aspect=(4, 5), gpu=o['gpu'], aaa=True, bloom=False, bg='mid')
    lights()
    obs = build_figure()
    kit.set_mode(obs, 'aaa')
    W = importlib.import_module(f'basic.{WEAPON}')
    root, wobs, _ = kit.build(W)
    kit.set_mode(wobs, 'aaa')
    # Waffe tief vor dem Körper: Griff vorn an der rechten Hüfte, Mündung nach vorn links unten
    WM = Matrix.Translation((-0.15, -0.20, 1.08)) @ Matrix.Rotation(math.radians(38), 4, 'Z') @ Matrix.Rotation(math.radians(22), 4, 'X')
    root.matrix_world = WM
    bpy.context.view_layer.update()
    pose_arms(WM)
    bpy.context.view_layer.update()
    if o['dry']:                # nur Aufbau und IK prüfen, kein Rendern
        return
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam'))
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    out = os.path.join(OUT, 'robot')
    os.makedirs(out, exist_ok=True)
    for name, pos, at, lens in (('hero', (-1.75, -3.6, 1.05), (0.02, 0, 0.93), 55),
                                ('nah', (-1.15, -1.9, 1.55), (0.0, -0.12, 1.30), 50),
                                ('seite', (-3.8, -1.2, 1.1), (0, 0, 0.93), 60)):
        pos, at = Vector(pos), Vector(at)
        cam.data.lens = lens
        cam.matrix_world = EB.mat((at - pos).normalized().to_track_quat('-Z', 'Y').to_matrix(), pos)
        bpy.context.scene.render.filepath = os.path.join(out, f'{name}.png')
        bpy.ops.render.render(write_still=True)
        print('geschrieben', bpy.context.scene.render.filepath)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, 'robot.blend'))


if __name__ == '__main__':
    main()
