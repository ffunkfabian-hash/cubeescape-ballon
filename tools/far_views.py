"""Ansicht `far` (A7, BALLON 0.30 „Rulebook“; Regel docs/stilhandbuch.md › 2 und › 7): Hauptansicht in 3 m und 5 m Abstand.

  ~/Claude/cubeescape-nexogen/ce lock gpu -- /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup \
      -P <repo>/tools/far_views.py -- [--gpu] [--samples 64] [BASIC-07-v2.1 …]

Je Waffe der Stil-v2.1-Familie (ohne Argumente alle): AAA-Material, grauer Grund wie die Ansichten (tools/blender_build.setup_render,
bg mid), Kamera aus der Hauptrichtung (W.HERO bzw. VIEWS['hero']) auf die Waffenmitte, Abstand 3 m und 5 m bei **gleicher Brennweite**
= Bezugsbildwinkel 75° waagrecht (ego.CAMERA, Visier-Standard 3; so groß, wie ein Spieler die Waffe in der Welt sieht). Bild 1920 × 1080,
gerendert und gespeichert wird nur der mittlere Ausschnitt 640 × 360 in echten Pixeln (keine Vergrößerung). Ausgabe
<OUT>/<Waffe>/views/far_3m.png, far_5m.png und Einträge in views.json (für tools/make_sheets.py); Kontaktbogen mit
tools/rules_evidence.py --far.
"""
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic import kit  # noqa: E402
from basic.arms import ego as EG  # noqa: E402
from tools import blender_build as BB  # noqa: E402
from tools import rules  # noqa: E402
from tools.paths import OUT  # noqa: E402

RES, CROP = (1920, 1080), (640, 360)
DIST_M = (3.0, 5.0)


def main():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    gpu = '--gpu' in a
    samples = int(a[a.index('--samples') + 1]) if '--samples' in a else 64
    want = [x for x in a if x.startswith('BASIC-')]
    for wid, W in rules.family():
        if want and wid not in want:
            continue
        kit.reset_scene()
        root, objs, anchors = kit.build(W)
        bpy.context.view_layer.update()
        BB.setup_render(RES[0], samples, gpu=gpu, aaa=True, bloom=False, bg='mid')
        kit.set_mode(objs, 'aaa')
        sc = bpy.context.scene
        sc.render.use_border = sc.render.use_crop_to_border = True
        sc.render.border_min_x, sc.render.border_max_x = 0.5 - CROP[0] / RES[0] / 2, 0.5 + CROP[0] / RES[0] / 2
        sc.render.border_min_y, sc.render.border_max_y = 0.5 - CROP[1] / RES[1] / 2, 0.5 + CROP[1] / RES[1] / 2
        cd = bpy.data.cameras.new('Far')
        cd.sensor_fit = 'HORIZONTAL'
        cd.sensor_width = 36
        cd.lens = 18 / math.tan(math.radians(EG.CAMERA['h_fov_deg'] / 2))
        cd.clip_end = 50
        cam = bpy.data.objects.new('Far', cd)
        sc.collection.objects.link(cam)
        sc.camera = cam
        pts = BB.bbox_pts(list(objs.values()))
        cen = sum(pts, Vector()) / len(pts)
        d = Vector(W.HERO if hasattr(W, 'HERO') else BB.VIEWS['hero'][0]).normalized()
        vp = os.path.join(OUT, wid, 'views', 'views.json')
        V = json.load(open(vp, encoding='utf-8')) if os.path.exists(vp) else dict(resolution=list(RES), views={})
        for dist in DIST_M:
            cam.matrix_world = Matrix.Translation(cen + d * dist) @ (-d).to_track_quat('-Z', 'Y').to_matrix().to_4x4()
            name = f'far_{dist:.0f}m'
            p = os.path.join(OUT, wid, 'views', f'{name}.png')
            os.makedirs(os.path.dirname(p), exist_ok=True)
            sc.render.filepath = p
            bpy.ops.render.render(write_still=True)
            V['views'][name] = dict(resolution=list(CROP), distance_m=dist, lens_mm=round(cd.lens, 2), h_fov_deg=EG.CAMERA['h_fov_deg'],
                                    frame=list(RES), note='Ausschnitt 640 × 360 aus 1920 × 1080 in echten Pixeln, Hauptrichtung')
            print(f'[far] {wid}: {name} → {p}')
        json.dump(V, open(vp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
