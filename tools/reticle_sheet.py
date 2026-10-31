"""Absehen-Katalog (basic/reticles.py): Formen (Cyan, normal), Farben (am Ring mit Punkt) und Linienstärken (am Fadenkreuz)
im Familienvisier (reflex_sight_v21), Blick durch das Glas; dazu ein Clip, wie Absehen beim Dauerfeuer aufgehen.

  blender -b --factory-startup -P tools/reticle_sheet.py -- [--gpu] [--samples N] [--spread]

Ausgabe: <OUT>/reticles/{kind,color,weight}_<id>.png; mit --spread <OUT>/reticles/spread/<kind>/####.png und
<EVIDENCE>/clips/reticle_spread.mp4 (Spreizung aus reticles.simulate, Profil 'auto', 10 Schuss mit 600/min); Katalogblatt mit `python3 tools/reticle_sheet.py --sheet` (ImageMagick, ohne Blender)
→ <EVIDENCE>/reticles.png; Hüftformen (0.13) mit `python3 tools/reticle_sheet.py --hip` → <EVIDENCE>/hip_reticles.png (SVG, ohne Blender)
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic import common as C, reticles as RT  # noqa: E402
from tools.paths import OUT, EVIDENCE  # noqa: E402

DST = os.path.join(OUT, 'reticles')
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'


CATALOG = [k for k in RT.RETICLES if k not in RT.HUD_ONLY]     # HUD-Formen der Sonderklassen stehen im Hüftblatt (HIP_SHEET)
VARIANTS = ([('kind', k, dict(reticle_kind=k), f"{RT.RETICLES[k]['de']} · {k}") for k in CATALOG]
            + [('color', f'{k}_{c}', dict(reticle_kind=k, reticle_color=c), f"{RT.RETICLES[k]['de']} · {d[0]}")
               for c, d in RT.COLORS.items() for k in CATALOG]
            + [('weight', w, dict(reticle_kind='cross', reticle_weight=w), f"Fadenkreuz {de} · {w}")
               for w, (de, _) in RT.WEIGHTS.items()]
            + [('glass', g, dict(reticle_kind='ring_dot', glass=g), f"Glas {de} · {g}") for g, (de, _) in RT.GLASS.items()])


def sheet():
    rows = []
    for grp, title in (('kind', 'Formen (Cyan, normal)'), ('color', 'Farben: jede Form in jeder Farbe'),
                       ('weight', 'Linienstärken (Fadenkreuz)'), ('glass', 'Glasvarianten (dezent; Ring mit Punkt)')):
        tiles = []
        for g, i, _, lab in VARIANTS:
            p = os.path.join(DST, f'{g}_{i}.png')
            if g == grp and os.path.exists(p):
                tiles += ['-label', lab, p]
        out = os.path.join(DST, f'_row_{grp}.png')
        subprocess.run(['magick', 'montage', *tiles, '-tile', f'{len(CATALOG)}x' if grp == 'color' else 'x1', '-geometry', '360x203+5+5', '-pointsize', '16', '-font', FONT,
                        '-background', '#4C525A', '-fill', '#ECEFF2', '-title', title, out], check=True)
        rows.append(out)
    out = os.path.join(EVIDENCE, 'reticles.png')
    subprocess.run(['magick', *rows, '-background', '#4C525A', '-gravity', 'west', '-append', out], check=True)
    print(out)


SPREAD_KINDS = ['ring_dot', 'cross', 'circle_cross', 'corners']
SHOTS = [0.2 + 0.1 * i for i in range(10)]


def build_sight(kw):
    import types
    import bpy
    from mathutils import Vector, Matrix
    from basic import kit
    kit.reset_scene()
    parts, anchors = C.reflex_sight_v21(0, 0, ww=34, wh=26, **kw)
    W = types.SimpleNamespace(META=dict(id='RETICLE', name='r'), ASSEMBLIES=C.assemblies('sight'), PARTS=parts, ANCHORS=anchors,
                              ACTIONS={})
    root, objs, anc = kit.build(W)
    return objs, anc, bpy, Vector, Matrix, kit


def spread_clip(o):
    import tools.blender_build as BB
    vals = RT.simulate('auto', SHOTS, 1.6)
    for k in SPREAD_KINDS:
        d = os.path.join(DST, 'spread', k)
        os.makedirs(d, exist_ok=True)
        for i, s in enumerate(vals):
            objs, anc, bpy, Vector, Matrix, kit = build_sight(dict(reticle_kind=k))
            # Absehen mit Spreizung s ersetzt das Ruhe-Absehen (gleiche Lage)
            BB.setup_render(480, o['samples'], gpu=o['gpu'], aaa=True, bloom=False, bg='mid')
            kit.set_mode(objs, 'aaa')
            ob = objs['sight_reticle']
            new = kit.build_shape('sight_reticle_s', dict(C.reticle(43.0, 8 + 13 + 8.5, k, spread=s), shape='multi'))
            new.data.materials.append(ob.data.materials[0])
            new.matrix_world = ob.matrix_world
            bpy.data.objects.remove(ob)
            cam = bpy.data.objects.new('Eye', bpy.data.cameras.new('Eye'))
            cam.data.lens = 70
            cam.data.clip_start = 0.005
            bpy.context.scene.collection.objects.link(cam)
            bpy.context.view_layer.update()
            eye = anc['Socket_Eye'].matrix_world.translation + Vector((0, 0.11, 0))
            cam.matrix_world = Matrix.Translation(eye) @ Vector((0, -1, 0)).to_track_quat('-Z', 'Y').to_matrix().to_4x4()
            bpy.context.scene.camera = cam
            bpy.context.scene.render.filepath = os.path.join(d, f'{i:04d}.png')
            bpy.ops.render.render(write_still=True)
        print('geschrieben Spreizung', k, len(vals))


def spread_video():
    vals = RT.simulate('auto', SHOTS, 1.6)
    tmp = os.path.join(DST, 'spread', '_grid')
    os.makedirs(tmp, exist_ok=True)
    for i, s in enumerate(vals):
        tiles = []
        for k in SPREAD_KINDS:
            tiles += ['-label', f"{RT.RETICLES[k]['de']}", os.path.join(DST, 'spread', k, f'{i:04d}.png')]
        shot = any(abs(i / 30 - t) < 0.5 / 30 for t in SHOTS)
        subprocess.run(['magick', 'montage', *tiles, '-tile', '4x1', '-geometry', '+4+4', '-pointsize', '15', '-font', FONT,
                        '-background', '#4C525A', '-fill', '#ECEFF2',
                        '-title', f"Aufgehen beim Dauerfeuer · Spreizung {s:.1f} mm{'  · Schuss' if shot else ''}",
                        os.path.join(tmp, f'{i:04d}.png')], check=True)
    os.makedirs(os.path.join(EVIDENCE, 'clips'), exist_ok=True)
    out = os.path.join(EVIDENCE, 'clips', 'reticle_spread.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '30', '-i', os.path.join(tmp, '%04d.png'),
                    '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2,format=yuv420p', '-c:v', 'libx264', '-crf', '22', out], check=True)
    print(out)


HIP_SHEET = [('auto_rifle', False), ('pulse_rifle', False), ('submachine_gun', False), ('hand_cannon', False), ('sniper_rifle', False),
             ('auto_rifle', True), ('combat_bow', False), ('fusion_rifle', False), ('linear_fusion_rifle', False),   # 0.33: Sonderklassen
             ('grenade_launcher', False)]


def hip_svg(kind, share_h, extent, spread, h=1080, size=200):
    """Hüftform als SVG in Bildpunkten einer Bildhöhe h, 1:1 wie Unity (HipReticle.Mask): Außenmaß share_h · h, Linie LINE_R · fein,
    Ringdicke · fein (innen fest), Punkt · (0,5 + 0,5 · fein), Linien mindestens 2 · min_line_px; Hintergrund wie der Unity-Parcours."""
    w, mp, k, c = RT.WEIGHTS[RT.HIP['weight']][1], RT.HIP['min_line_px'], share_h * h / extent, size / 2
    col, op = RT.COLORS[RT.HIP['color']][1], RT.SETTINGS['opacity']['default']
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"><rect width="100%" height="100%" fill="#9EA8B3"/>',
           f'<g fill="none" stroke="{col}" stroke-linecap="round" opacity="{op}">']
    for q in RT.prims_at(kind, spread):
        if q['t'] == 'line':
            (ax, au), (bx, bu) = q['a'], q['b']
            out.append(f'<line x1="{c - ax * k:.2f}" y1="{c - au * k:.2f}" x2="{c - bx * k:.2f}" y2="{c - bu * k:.2f}" '
                       f'stroke-width="{2 * max(RT.LINE_R * w * k, mp):.2f}"/>')
        elif q['t'] == 'ring':
            inner = q['ri'] * k
            outer = inner + max((q['r'] - q['ri']) * w * k, 2 * mp)
            out.append(f'<circle cx="{c}" cy="{c}" r="{(inner + outer) / 2:.2f}" stroke-width="{outer - inner:.2f}"/>')
        else:
            out.append(f'<circle cx="{c}" cy="{c}" r="{max(q["r"] * (0.5 + 0.5 * w) * k, mp):.2f}" fill="{col}" stroke="none"/>')
    return '\n'.join(out + ['</g></svg>'])


def hip_sheet():
    """Bogen der Hüftformen (Entscheidungsliste 4.2 A): je Typ Ruhe, nach 3 Schuss (720/min) und Maximum, 1:1 bei 1080 px Bildhöhe
    (Ausschnitt 200 × 200 px), darunter 3-fach vergrößert."""
    d = os.path.join(DST, 'hip')
    os.makedirs(d, exist_ok=True)
    rows = []
    for t, sprint in HIP_SHEET:
        H = RT.hud_hip(t)   # 0.33: HUD-Hüftzeichen (Sonderklassen nach Glidepath)
        kind, share = (H['sprint']['kind'], H['sprint']['share_h']) if sprint else (H['kind'], H['share_h'])
        S = RT.SPREAD[H['spread']]
        three = RT.simulate(H['spread'], [i * 60 / 720 for i in range(3)], 3 * 60 / 720)[-1]
        tiles = []
        states = (('Sprint, geht nicht auf', 0.0),) if sprint else (('Ruhe', S['base']), ('3 Schuss', three), ('Maximum', S['max']))
        for lab, sp in states:
            svg = os.path.join(d, f"{t}{'_sprint' if sprint else ''}_{lab.split(',')[0].replace(' ', '')}.svg")
            open(svg, 'w', encoding='utf-8').write(hip_svg(kind, share, RT.extent_mm(kind, RT.WEIGHTS[RT.HIP['weight']][1]), sp))
            png = svg[:-4] + '.png'
            subprocess.run(['magick', '-density', '96', svg, png], check=True)
            big = svg[:-4] + '_x3.png'
            subprocess.run(['magick', png, '-gravity', 'center', '-crop', '100x100+0+0', '+repage', '-filter', 'point', '-resize', '300%', big],
                           check=True)
            tiles += ['-label', f'{lab} · {sp:.1f} mm', png, '-label', '× 3 (Mitte)', big]
        out = os.path.join(d, f"_row_{t}{'_sprint' if sprint else ''}.png")
        name = f"{t}{' · Sprint' if sprint else ''} · `{kind}` {share * 100:.1f} %% H · {(H['status'] if not sprint else 'gemessen (Glidepath, 1,5 % H)').replace('%', '%%')}"
        subprocess.run(['magick', 'montage', *tiles, '-tile', '6x1', '-geometry', '+4+4', '-pointsize', '14', '-font', FONT,
                        '-background', '#4C525A', '-fill', '#ECEFF2', '-title', name, out], check=True)
        rows.append(out)
    out = os.path.join(EVIDENCE, 'hip_reticles.png')
    subprocess.run(['magick', *rows, '-background', '#4C525A', '-gravity', 'west', '-append', out], check=True)
    print(out)


def render(o):
    import types
    import bpy
    from mathutils import Vector, Matrix
    from basic import kit
    import tools.blender_build as BB
    os.makedirs(DST, exist_ok=True)
    for grp, i, kw, _ in VARIANTS:
        kit.reset_scene()
        parts, anchors = C.reflex_sight_v21(0, 0, ww=34, wh=26, **kw)
        W = types.SimpleNamespace(META=dict(id='RETICLE', name=i), ASSEMBLIES=C.assemblies('sight'), PARTS=parts,
                                  ANCHORS=anchors, ACTIONS={})
        root, objs, anc = kit.build(W)
        BB.setup_render(960, o['samples'], gpu=o['gpu'], aaa=True, bloom=False, bg='mid')
        kit.set_mode(objs, 'aaa')
        cam = bpy.data.objects.new('Eye', bpy.data.cameras.new('Eye'))
        cam.data.lens = 70
        cam.data.clip_start = 0.005
        bpy.context.scene.collection.objects.link(cam)
        bpy.context.view_layer.update()
        eye = anc['Socket_Eye'].matrix_world.translation + Vector((0, 0.11, 0))
        cam.matrix_world = Matrix.Translation(eye) @ Vector((0, -1, 0)).to_track_quat('-Z', 'Y').to_matrix().to_4x4()
        bpy.context.scene.camera = cam
        bpy.context.scene.render.filepath = os.path.join(DST, f'{grp}_{i}.png')
        bpy.ops.render.render(write_still=True)
        print('geschrieben', grp, i)


if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    if '--sheet' in a:
        sheet()
    elif '--hip' in a:
        hip_sheet()
    elif '--video' in a:
        spread_video()
    elif '--spread' in a:
        spread_clip(dict(gpu='--gpu' in a, samples=int(a[a.index('--samples') + 1]) if '--samples' in a else 48))
    else:
        render(dict(gpu='--gpu' in a, samples=int(a[a.index('--samples') + 1]) if '--samples' in a else 64))
