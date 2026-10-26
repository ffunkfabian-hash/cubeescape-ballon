"""Messung Bildlage im Ego-Bild (Patch „messen“, Entscheidungsliste 2.1): projiziert Anker und Waffenkontur der Pose in Prozent
von Bildbreite/-höhe (Ursprung oben links), ohne Rendern. Nur Messung, ändert keine Werte.

  blender -b --factory-startup -P tools/messen.py -- [--poses hip,ads] [--out <datei.json>]

Der Bildwinkel ist der des Ego-Bilds (`ego.CAMERA`, 75° horizontal, 16:9) wie in den Ego-Stills von `tools/ego_build.py`.
Liefert je Pose: Mündung (Socket_Muzzle), Visier hinten/Absehen (Socket_Sight/Socket_Reticle), Waffenkontur (Eckpunkte der
ausgewerteten Waffennetze, ohne Arme) als unbeschnittene Ausdehnung in %.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import bpy  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402
import tools.ego_build as E  # noqa: E402
import importlib  # noqa: E402


def pct(scene, cam, co):
    v = world_to_camera_view(scene, cam, co)          # x, y in 0…1 (y von unten), z = Tiefe
    return [round(v.x * 100, 2), round((1 - v.y) * 100, 2), round(v.z, 3)]


def main():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    poses = (a[a.index('--poses') + 1] if '--poses' in a else 'hip,ads').split(',')
    out = a[a.index('--out') + 1] if '--out' in a else None
    o = dict(stills=False, actions=[], gpu=False, samples=8, weapon='pilot.w01_auto_rifle_v21')
    W = importlib.import_module(f'basic.{o["weapon"]}')
    sc = E.Scene(W, o)
    scn = bpy.context.scene
    scn.render.resolution_x, scn.render.resolution_y = 1600, 900
    res = {}
    dg = bpy.context.evaluated_depsgraph_get()
    for name in poses:
        A = dict(weapon=[(0, name)], L=[(0, 'support')], R=[(0, 'grip')])
        E.evaluate(sc, A, 0, {}, {})
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        r = {}
        for an in ('Socket_Muzzle', 'Socket_Sight', 'Socket_Reticle', 'Socket_Eye'):
            if an in sc.anchors:
                r[an] = pct(scn, sc.cam, sc.anchors[an].matrix_world.translation)
        xs, ys = [], []
        for ob in sc.objs.values():
            if ob.type != 'MESH' or ob.hide_render:
                continue
            ev = ob.evaluated_get(dg)
            me = ev.to_mesh()
            mw = ev.matrix_world
            for v in me.vertices:
                p = pct(scn, sc.cam, mw @ v.co)
                if p[2] > 0:                           # vor der Kamera
                    xs.append(p[0])
                    ys.append(p[1])
            ev.to_mesh_clear()
        r['kontur'] = dict(x_min=min(xs), x_max=max(xs), y_min=min(ys), y_max=max(ys))
        res[name] = r
        print('[messen]', name, json.dumps(r))
    if out:
        json.dump(res, open(out, 'w', encoding='utf-8'), indent=1)


if __name__ == '__main__':
    main()
