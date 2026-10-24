"""Optionsblatt Visier-Designsprache: dieselbe Waffe mit verschiedenen Optiken – Nahansicht schräg vorn und Blick beim Zielen.

  blender -b --factory-startup -P tools/sight_options.py -- [--gpu] [--samples N]   → <OUT>/sight_options/<option>_{nah,ziel}.png
  python3 tools/sight_options.py --sheet                                           → <EVIDENCE>/sight_options.png

Optionen (Scout v2.1): Rohr (common.scope_v21), Prisma-Kasten und Flachkasten (common.box_scope_v21, basic/pilot/optics).
Zielbild wie tools/sight_examples.py: Kamera im Augenpunkt (Visier-Standard), 75° horizontal, `ads_hide`-Teile aus.
"""
import importlib
import math
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools.paths import OUT, EVIDENCE  # noqa: E402

DST = os.path.join(OUT, 'sight_options')
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
REF = os.path.expanduser('~/Library/Caches/CubeEscapeBallon/refs/video/scout_frames/f_520.png')
OPTIONS = [('rohr', 'Rohr mit Ringen (jetzt)'), ('prism', 'Prisma-Kasten (Bild 1)'), ('flat', 'Flachkasten (Bild 2)')]


def weapon(opt):
    if opt == 'rohr':
        return importlib.import_module('basic.pilot.w03_scout_rifle_v21')
    from basic.pilot.optics import scout_optics
    return scout_optics.variant(opt)


def render(o):
    import bpy
    from mathutils import Vector, Matrix
    from basic import kit
    import tools.blender_build as BB
    os.makedirs(DST, exist_ok=True)
    for opt, _ in OPTIONS:
        W = weapon(opt)
        kit.reset_scene()
        root, objs, anc = kit.build(W)
        BB.setup_render(960, o['samples'], gpu=o['gpu'], aaa=True, bloom=False, bg='mid')
        kit.set_mode(objs, 'aaa')
        cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam'))
        cam.data.sensor_fit = 'HORIZONTAL'
        cam.data.sensor_width = 36
        cam.data.clip_start = 0.005
        bpy.context.scene.collection.objects.link(cam)
        bpy.context.scene.camera = cam
        bpy.context.view_layer.update()
        eye = anc['Socket_Eye'].matrix_world.translation.copy()
        obj = anc['Socket_Objective'].matrix_world.translation.copy()
        # Nahansicht: schräg von vorn rechts oben auf Optik und Gehäuseoberseite
        at = (eye + obj) / 2 + Vector((0, 0, -0.01))
        pos = at + Vector((-0.30, -0.30, 0.16))
        cam.data.lens = 60
        cam.matrix_world = Matrix.Translation(pos) @ (at - pos).to_track_quat('-Z', 'Y').to_matrix().to_4x4()
        bpy.context.scene.render.filepath = os.path.join(DST, f'{opt}_nah.png')
        bpy.ops.render.render(write_still=True)
        # Zielbild
        for p in W.PARTS:
            if p.get('ads_hide') and p['id'] in objs:
                objs[p['id']].hide_render = True
        cam.data.lens = 18 / math.tan(math.radians(37.5))
        cam.matrix_world = Matrix.Translation(eye) @ Vector((0, -1, 0)).to_track_quat('-Z', 'Y').to_matrix().to_4x4()
        bpy.context.scene.render.filepath = os.path.join(DST, f'{opt}_ziel.png')
        bpy.ops.render.render(write_still=True)
        print('geschrieben', opt)


def sheet():
    tiles = []
    for opt, de in OPTIONS:
        tiles += ['-label', f'{de} · nah', os.path.join(DST, f'{opt}_nah.png'),
                  '-label', f'{de} · im Zielen (90 mm)', os.path.join(DST, f'{opt}_ziel.png')]
    rows = os.path.join(DST, '_grid.png')
    subprocess.run(['magick', 'montage', *tiles, '-tile', '2x', '-geometry', '640x360+5+5', '-pointsize', '16', '-font', FONT,
                    '-background', '#4C525A', '-fill', '#ECEFF2', '-title', 'Scout v2.1 · Optik-Designsprache', rows], check=True)
    out = os.path.join(EVIDENCE, 'sight_options.png')
    if os.path.exists(REF):
        ref = os.path.join(DST, '_ref.png')
        subprocess.run(['magick', REF, '-resize', '640x', '-gravity', 'south', '-background', '#4C525A', '-fill', '#ECEFF2',
                        '-font', FONT, '-pointsize', '16', '-splice', '0x26', '-annotate', '+0+4', 'Destiny 2 · Scout im Zielen', ref],
                       check=True)
        subprocess.run(['magick', rows, ref, '-background', '#4C525A', '-gravity', 'north', '+append', out], check=True)
    else:
        subprocess.run(['cp', rows, out], check=True)
    print(out)


if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    if '--sheet' in a:
        sheet()
    else:
        render(dict(gpu='--gpu' in a, samples=int(a[a.index('--samples') + 1]) if '--samples' in a else 48))
