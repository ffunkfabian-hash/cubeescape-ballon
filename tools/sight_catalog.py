"""Katalogblatt Visier-Baukasten (basic/pilot/optics/sight_kit.py): je Visier Blick beim Zielen und Nahansicht, dazu Größen S/M/L.

  blender -b --factory-startup -P tools/sight_catalog.py -- [--gpu] [--samples N] [--only holo_rr,scope_ring]
                                                                      → <OUT>/sight_catalog/<id>_<größe>_{ziel,nah}.png
  python3 tools/sight_catalog.py --sheet                              → <EVIDENCE>/sight_catalog.png, sight_catalog_sizes.png

Baukasten seit 0.21 Produktionsform (basic/common.py, Form `xprof` und Rolle `sight_anod` in kit.py).
Zielbild wie tools/sight_options.py (Augenpunkt, 75°, `ads_hide` aus, gezeichnetes Absehen in Hüftform der Klasse). Kimme/Korn
ohne gezeichnetes Absehen (die Leuchtklammern sind das Absehen); das Scharfschützen-ZF zeigt im Zielen das Vollbild (Art A): Waffe
aus, Kreis 82 % der Bildhöhe, außen schwarz, Hüftform in der Mitte.
"""
import math
import os
import subprocess
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools.paths import OUT, EVIDENCE  # noqa: E402
from tools.sight_options import HFOV, RES, FONT, drawn_reticle, ground  # noqa: E402

DST = os.path.join(OUT, 'sight_catalog')
FULLSCREEN = 0.82          # Kreis im Vollbild als Anteil der Bildhöhe (Destiny 80–83 %, Motiongen visiere.md › 7)


def duplex(cx, cy, r):
    """Duplex-Absehen (Kritik Z3): außen kräftige Balken 1,2 % Bildhöhe bis zur Lücke 12 % H um die Mitte, innen feine Linien 0,15 % H."""
    H = RES[1]
    g, wo, wi = 0.12 * H, max(2, 0.012 * H), max(1, 0.0015 * H * 2)
    a = ['-stroke', 'none', '-fill', '#121417']
    for x0, y0, x1, y1 in ((cx - r, cy - wo / 2, cx - g, cy + wo / 2), (cx + g, cy - wo / 2, cx + r, cy + wo / 2),
                           (cx - wo / 2, cy + g, cx + wo / 2, cy + r), (cx - wo / 2, cy - r, cx + wo / 2, cy - g)):
        a += ['-draw', f'rectangle {x0:.1f},{y0:.1f} {x1:.1f},{y1:.1f}']
    a += ['-draw', f'rectangle {cx - g:.1f},{cy - wi / 2:.1f} {cx + g:.1f},{cy + wi / 2:.1f}',
          '-draw', f'rectangle {cx - wi / 2:.1f},{cy - g:.1f} {cx + wi / 2:.1f},{cy + g:.1f}']
    return a


def kits():
    """Baukasten-Module: sight_kit und, falls vorhanden, sight_kit_more (weitere Varianten). Liefert {id: (Modul, Eintrag)}."""
    import importlib
    out = {}
    for name in ('sight_kit', 'sight_kit_more'):
        try:
            M = importlib.import_module(f'basic.pilot.optics.{name}')
        except ModuleNotFoundError:
            continue
        out.update({k: (M, v) for k, v in M.KIT.items()})
    return out


def jobs():
    out = []
    for k, (M, _) in kits().items():
        out.append((k, 'M'))
        out += [(k, s) for s in ('S', 'L') if k in getattr(M, 'SIZED', ())]
    return out


def render(o, only=None):
    import bpy
    from mathutils import Vector, Matrix
    from basic import kit
    import tools.blender_build as BB
    os.makedirs(DST, exist_ok=True)
    for kid, size in jobs():
        if only and kid not in only:
            continue
        W = kits()[kid][0].weapon(kid, size)
        kit.reset_scene()
        root, objs, anc = kit.build(W)
        BB.setup_render(RES[0], o['samples'], gpu=o['gpu'], aaa=True, bloom=False, bg='mid')
        kit.set_mode(objs, 'aaa')
        cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam'))
        cam.data.sensor_fit = 'HORIZONTAL'
        cam.data.sensor_width = 36
        cam.data.clip_start = 0.005
        bpy.context.scene.collection.objects.link(cam)
        bpy.context.scene.camera = cam
        bpy.context.view_layer.update()
        eye = anc['Socket_Eye'].matrix_world.translation.copy()
        ret = anc['Socket_Reticle'].matrix_world.translation.copy()
        ground(eye.z - 1.55)
        if size == 'M':      # Nahansicht schräg von links vorn oben auf das Visier
            iron = W.ANCHORS['Socket_Eye']['sight_type'] == 'iron'     # Kimme/Korn: Nahansicht nur auf die Kimme
            sight = [ob for p, ob in ((p, objs[p['id']]) for p in W.PARTS) if p['asm'] == 'sight' and not p.get('ads_hide')
                     and not (iron and p['id'].startswith(('sight_front', 'sight_glass')))]
            pts = [ob.matrix_world @ Vector(c) for ob in sight for c in ob.bound_box]
            lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
            hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
            at = (lo + hi) / 2
            size_m = max((hi - lo).length, 0.06)
            pos = at + Vector((1.0, -0.75, 0.55)).normalized() * size_m * 2.6
            cam.data.lens = 50
            cam.matrix_world = Matrix.Translation(pos) @ (at - pos).to_track_quat('-Z', 'Y').to_matrix().to_4x4()
            bpy.context.scene.render.filepath = os.path.join(DST, f'{kid}_{size}_nah.png')
            bpy.ops.render.render(write_still=True)
        for p in W.PARTS:      # ads_hide aus; Modell-Absehen aus, das Absehen wird gezeichnet
            if (p.get('ads_hide') or p['id'] == 'sight_reticle') and p['id'] in objs:
                objs[p['id']].hide_render = True
        typ = W.ANCHORS['Socket_Eye']['sight_type']
        d = (ret - eye).length / kit.MM
        px = 2 * d * math.tan(math.radians(HFOV / 2)) / RES[0]
        if typ == 'fullscreen':      # Waffe aus, Absehen 200 mm vor dem Auge
            for ob in objs.values():
                ob.hide_render = True
            d = 200.0
            px = 2 * d * math.tan(math.radians(HFOV / 2)) / RES[0]
        elif typ != 'iron':
            drawn_reticle(W.META['type'], ret + Vector((0, 0.0004, 0)), d - 0.4, px)
        cam.data.lens = 18 / math.tan(math.radians(HFOV / 2))
        cam.matrix_world = Matrix.Translation(eye) @ Vector((0, -1, 0)).to_track_quat('-Z', 'Y').to_matrix().to_4x4()
        f = os.path.join(DST, f'{kid}_{size}_ziel.png')
        bpy.context.scene.render.filepath = f
        bpy.ops.render.render(write_still=True)
        if typ == 'fullscreen':
            r = FULLSCREEN * RES[1] / 2
            cx, cy = RES[0] / 2, RES[1] / 2
            subprocess.run(['magick', f, '-background', '#4C525A', '-flatten', '(', '-size', f'{RES[0]}x{RES[1]}', 'xc:black', '-fill',
                            'white', '-draw', f'circle {cx},{cy} {cx + r},{cy}', '-blur', '0x1.2', ')', '-compose', 'multiply',
                            '-composite', '-fill', 'none', '-stroke', '#3A3F46', '-strokewidth', '3', '-draw',
                            f'circle {cx},{cy} {cx + r},{cy}', *duplex(cx, cy, r), f], check=True)
        print('geschrieben', kid, size, flush=True)


def sheet():
    K = types.SimpleNamespace(KIT={k: v for k, (M, v) in kits().items()},
                              SIZED=[k for k, (M, v) in kits().items() if k in getattr(M, 'SIZED', ())])
    T = ['-geometry', '560x315+4+4', '-pointsize', '15', '-font', FONT, '-background', '#4C525A', '-fill', '#ECEFF2']
    tiles = []
    built = ('holo_ref', 'holo_pille', 'holo_kasten', 'scope_tropfen')      # 0.21: gebaut in basic/common.py
    for kid, (_, name, wtype, use, feat) in K.KIT.items():
        tiles += ['-label', f'{name} · {use}' + (' · GEBAUT' if kid in built else ''), os.path.join(DST, f'{kid}_M_ziel.png'),
                  '-label', feat, os.path.join(DST, f'{kid}_M_nah.png')]
    out = os.path.join(EVIDENCE, 'sight_catalog.png')
    subprocess.run(['magick', 'montage', *tiles, '-tile', '4x', *T, '-title', 'BALLON Visier-Baukasten v3 (0.21) – Größe M; gebaut: H0, H2, H4, Z1',
                    '-depth', '8', out], check=True)
    tiles = []
    for kid in K.SIZED:
        for s in ('S', 'M', 'L'):
            tiles += ['-label', f'{K.KIT[kid][1]} · {s}', os.path.join(DST, f'{kid}_{s}_ziel.png')]
    out2 = os.path.join(EVIDENCE, 'sight_catalog_sizes.png')
    subprocess.run(['magick', 'montage', *tiles, '-tile', '3x', *T, '-title', 'Größen S / M / L im Zielen (90 mm, 75°)',
                    '-depth', '8', out2], check=True)
    print(out, out2)


if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    if '--sheet' in a:
        sheet()
    else:
        render(dict(gpu='--gpu' in a, samples=int(a[a.index('--samples') + 1]) if '--samples' in a else 48),
               only=a[a.index('--only') + 1].split(',') if '--only' in a else None)
