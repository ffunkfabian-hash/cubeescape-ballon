"""Visierbild-Beispiele zum Visier-Standard v2: Blick beim Zielen (nur Waffe, ohne Arme) je Waffe mit drei Augenabständen.

  blender -b --factory-startup -P tools/sight_examples.py -- [--gpu] [--samples N] [--only BASIC-03]   → <OUT>/sight_examples/<waffe>_<abstand>_<zoom>.png
  python3 tools/sight_examples.py --sheet                                          → <EVIDENCE>/sight_examples.png

Kamera im Augenpunkt (Socket_Eye, um den Unterschied zum Standardabstand entlang der Visierlinie verschoben), Blick nach vorn,
Grundbildwinkel 75° horizontal (ego.CAMERA); das Waffenmodell wird nicht vergrößert (Viewmodel-Zoom 1,0), Teile mit `ads_hide`
sind ausgeblendet. Beschriftung: Anteil der Visieröffnung an der Bildbreite und Zielbereich aus reticles.SIGHT. Die Scout-Zeile
zeigt rechts ein Destiny-Vergleichsbild (Q-D2-ADS), falls vorhanden.
"""
import importlib
import math
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic import reticles as RT  # noqa: E402
from tools.paths import OUT, EVIDENCE  # noqa: E402

DST = os.path.join(OUT, 'sight_examples')
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
HFOV = 75.0
# (Modul, Visiertyp, Fensterbreite mm, Augenabstände mm, Zoomwerte)
CASES = [('pilot.w01_auto_rifle_v21', 'reflex', 26, (70, 90, 110), (1.0,)),
         ('pilot.w02_pulse_rifle_v21', 'reflex', 27, (70, 90, 110), (1.0,)),
         ('pilot.w03_scout_rifle_v21', 'scope', 2 * 16.5, (70, 90, 110), (1.0,))]
REF = os.path.expanduser('~/Library/Caches/CubeEscapeBallon/refs/video/scout_frames/f_520.png')


def share(ww, relief, zoom):
    """Anteil des Fensters (Breite ww mm, Abstand relief mm) an der Bildbreite bei Zoom."""
    return ww / (2 * relief * math.tan(math.radians(HFOV / 2)) / zoom)


def render(o, only=None):
    import bpy
    from mathutils import Vector, Matrix
    from basic import kit
    import tools.blender_build as BB
    os.makedirs(DST, exist_ok=True)
    for mod, typ, ww, reliefs, zooms in CASES:
        W = importlib.import_module(f'basic.{mod}')
        if only and W.META['id'] not in only:
            continue
        kit.reset_scene()
        root, objs, anc = kit.build(W)
        BB.setup_render(960, o['samples'], gpu=o['gpu'], aaa=True, bloom=False, bg='mid')
        kit.set_mode(objs, 'aaa')
        cam = bpy.data.objects.new('Eye', bpy.data.cameras.new('Eye'))
        cam.data.sensor_fit = 'HORIZONTAL'
        cam.data.sensor_width = 36
        cam.data.clip_start = 0.005
        bpy.context.scene.collection.objects.link(cam)
        bpy.context.scene.camera = cam
        bpy.context.view_layer.update()
        eye0 = anc['Socket_Eye'].matrix_world.translation.copy()
        for p in W.PARTS:                                   # Visier-Standard: beim Zielen ausgeblendete Teile
            if p.get('ads_hide') and p['id'] in objs:
                objs[p['id']].hide_render = True
        std = RT.SIGHT['types'][typ]['eye_relief_mm']
        for rel in reliefs:
            eye = eye0 + Vector((0, (rel - std) / 1000.0, 0))          # weiter weg = nach hinten (+Y)
            cam.matrix_world = Matrix.Translation(eye) @ Vector((0, -1, 0)).to_track_quat('-Z', 'Y').to_matrix().to_4x4()
            for z in zooms:
                fov = 2 * math.atan(math.tan(math.radians(HFOV / 2)) / z)
                cam.data.lens = 18 / math.tan(fov / 2)
                bpy.context.scene.render.filepath = os.path.join(DST, f"{W.META['id']}_{rel}_{z}.png")
                bpy.ops.render.render(write_still=True)
                print('geschrieben', W.META['id'], rel, z)


def sheet():
    rows = []
    for mod, typ, ww, reliefs, zooms in CASES:
        W = importlib.import_module(f'basic.{mod}')
        tiles = []
        for rel in reliefs:
            for z in zooms:
                std = '  (Standard)' if rel == RT.SIGHT['types'][typ]['eye_relief_mm'] else ''
                lo, hi = RT.SIGHT['types'][typ]['target_share']
                tiles += ['-label', f"Augenabstand {rel} mm{std} · Öffnung {share(ww, rel, z) * 100:.0f} %% der Bildbreite "
                                    f"(Ziel {lo * 100:.0f}–{hi * 100:.0f} %%)", os.path.join(DST, f"{W.META['id']}_{rel}_{z}.png")]
        if typ == 'scope' and os.path.exists(REF):
            tiles += ['-label', 'Destiny 2 · Scout im Zielen (Video 1ERmScNiOk4, 8:40)', REF]
        out = os.path.join(DST, f"_rows_{W.META['id']}.png")
        subprocess.run(['magick', 'montage', *tiles, '-tile', 'x1', '-geometry', '560x315+5+5', '-pointsize', '15',
                        '-font', FONT, '-background', '#4C525A', '-fill', '#ECEFF2',
                        '-title', f"{W.META['id']} {W.META['type_de']} · {RT.SIGHT['types'][typ]['de']}", out], check=True)
        rows.append(out)
    out = os.path.join(EVIDENCE, 'sight_examples.png')
    subprocess.run(['magick', *rows, '-background', '#4C525A', '-append', out], check=True)
    print(out)


if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    if '--sheet' in a:
        sheet()
    else:
        render(dict(gpu='--gpu' in a, samples=int(a[a.index('--samples') + 1]) if '--samples' in a else 48),
               only=a[a.index('--only') + 1].split(',') if '--only' in a else None)
