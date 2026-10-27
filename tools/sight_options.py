"""Optionsblatt Visier-Konzept: Holo (BASIC-01 v2.1) und Zielfernrohr (BASIC-03 v2.1) je Konzept – Blick beim Zielen und Seitenansicht.

  blender -b --factory-startup -P tools/sight_options.py -- [--gpu] [--samples N] [--only jetzt,hals] [--weapons holo,scope,pulse,mp]
                                                                      → <OUT>/sight_options/<option>_<waffe>_{ziel,seite}.png
  python3 tools/sight_options.py --sheet                              → <EVIDENCE>/sight_options.png

Optionen: „jetzt“ (Stand 0.20, Modell-Absehen) und die Konzepte aus basic/pilot/optics/sight_concepts.py (docs/visier-konzept.md).
Zielbild wie tools/sight_examples.py: Kamera im Augenpunkt (Visier-Standard, 90 mm), 75° horizontal, `ads_hide`-Teile aus, ohne
Weltzoom (Modell und Öffnung wie im Spiel, nur die Welt wäre vergrößert). Konzepte zeigen das Absehen gezeichnet: flach in der
Glasebene, Hüftform der Klasse in Hüftgröße (reticles.hip, wie Unity seit 0.20), Linien mindestens 1,6 px. Eine Bodenebene mit
Raster zeigt, was unter dem Ring von der Welt bleibt. Belege: Destiny-Bilder aus dem Scout-Video (Q-D2-ADS), falls vorhanden.
Die Kastenoptiken von 24.10.2026 (basic/pilot/optics/scout_optics.py) sind nicht mehr Teil des Blatts.
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
REFS = [os.path.expanduser(f'~/Library/Caches/CubeEscapeBallon/refs/video/scout_frames/{n}.png') for n in ('f_230', 'f_450')]
HFOV = 75.0
RES = (1280, 720)
WEAPONS = [('holo', 'pilot.w01_auto_rifle_v21', 'auto_rifle'), ('scope', 'pilot.w03_scout_rifle_v21', 'scout_rifle'),
           ('pulse', 'pilot.w02_pulse_rifle_v21', 'pulse_rifle'), ('mp', 'pilot.w06_submachine_gun_v21', 'submachine_gun')]
CONCEPT_WEAPONS = ('holo', 'scope')        # Konzepte A/B/C gibt es nur für Holo und Zielfernrohr; Impuls und MP nur „jetzt“ (0.21)


def options():
    from basic.pilot.optics import sight_concepts as C
    return [('jetzt', '0.20 jetzt', 'Stand 0.20 „Spotter“: Rohrsattel und Schiene vor dem Auge, Ringwulst, Absehen als Modellteil')] \
        + C.CONCEPTS


def weapon(opt, w):
    if opt == 'jetzt':
        return importlib.import_module(f'basic.{dict((a, b) for a, b, _ in WEAPONS)[w]}')
    from basic.pilot.optics import sight_concepts as C
    return C.variant(opt, w)


def drawn_reticle(wtype, center, dist_mm, px_mm):
    """Gezeichnetes Absehen: Hüftform flach in der Ebene quer zur Blickrichtung (−Y) durch `center`, Größe als Anteil der Bildhöhe."""
    import bmesh
    import bpy
    from mathutils import Vector
    from basic import kit, reticles as RT
    h = RT.hip(wtype)
    k = RT.WEIGHTS[RT.HIP['weight']][1]
    tan_v = math.tan(math.radians(HFOV / 2)) * RES[1] / RES[0]
    s = h['share_h'] * 2 * dist_mm * tan_v / h['extent_mm']
    lw = max(RT.LINE_R * k * s, 0.8 * px_mm)              # halbe Linienbreite, mindestens 1,6 px
    bm = bmesh.new()

    def P(x, u):
        return center + Vector((x * kit.MM, 0, u * kit.MM))

    def poly(pts):
        bm.faces.new([bm.verts.new(P(*q)) for q in pts])

    for q in RT.prims_at(h['kind'], 0.0, True):
        if q['t'] == 'line':
            (ax, au), (bx, bu) = [(c[0] * s, c[1] * s) for c in (q['a'], q['b'])]
            L = math.hypot(bx - ax, bu - au) or 1.0
            nx, nu = -(bu - au) / L * lw, (bx - ax) / L * lw
            poly([(ax + nx, au + nu), (ax - nx, au - nu), (bx - nx, bu - nu), (bx + nx, bu + nu)])
        else:
            n = 64 if q['t'] == 'ring' else 24
            ro = (q['ri'] + (q['r'] - q['ri']) * k) * s if q['t'] == 'ring' else q['r'] * s * (0.5 + 0.5 * k)
            ro = max(ro, lw * 1.2)
            ri = q['ri'] * s if q['t'] == 'ring' else 0.0
            if q['t'] == 'ring':
                ri = min(ri, ro - 2 * lw)
            for i in range(n):
                a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
                c0, c1 = (math.cos(a0), math.sin(a0)), (math.cos(a1), math.sin(a1))
                if ri > 0:
                    poly([(c0[0] * ri, c0[1] * ri), (c0[0] * ro, c0[1] * ro), (c1[0] * ro, c1[1] * ro), (c1[0] * ri, c1[1] * ri)])
                else:
                    poly([(0, 0), (c0[0] * ro, c0[1] * ro), (c1[0] * ro, c1[1] * ro)])
    me = bpy.data.meshes.new('drawn_reticle')
    bm.to_mesh(me)
    ob = bpy.data.objects.new('drawn_reticle', me)
    ob.data.materials.append(kit.material('reticle_cyan'))
    ob.visible_shadow = False
    bpy.context.scene.collection.objects.link(ob)
    return ob


def ground(z):
    """Bodenebene mit grobem Raster (2 m), damit Glas und Unterseite gegen eine Welt stehen."""
    import bpy
    me = bpy.data.meshes.new('Ground')
    S = 200
    me.from_pydata([(-S, -S, z), (S, -S, z), (S, S, z), (-S, S, z)], [], [(0, 1, 2, 3)])
    ob = bpy.data.objects.new('Ground', me)
    m = bpy.data.materials.new('Ground')
    m.use_nodes = True
    nt = m.node_tree
    ch = nt.nodes.new('ShaderNodeTexChecker')
    ch.inputs['Scale'].default_value = S
    ch.inputs['Color1'].default_value = (0.42, 0.40, 0.37, 1)
    ch.inputs['Color2'].default_value = (0.33, 0.32, 0.30, 1)
    nt.links.new(ch.outputs['Color'], nt.nodes['Principled BSDF'].inputs['Base Color'])
    me.uv_layers.new()
    for i, uv in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
        me.uv_layers[0].data[i].uv = uv
    me.materials.append(m)
    bpy.context.scene.collection.objects.link(ob)


def render(o, only=None, weapons=None):
    import bpy
    from mathutils import Vector, Matrix
    from basic import kit
    import tools.blender_build as BB
    os.makedirs(DST, exist_ok=True)
    # Entwurfsrolle der Konzepte: dunkel, ohne Kantenabrieb (WEAR färbt dünne Teile sonst ganz hell, siehe sight_concepts)
    kit.MATERIALS.setdefault('sight_dark', dict(color='#26282C', rough=0.5, metal=0.0, spec=0.35, aaa_color='#18191C',
                                                de='Visier dunkel (Entwurf, ohne Abrieb)'))
    for opt, _, _ in options():
        if only and opt not in only:
            continue
        for w, _, wtype in WEAPONS:
            if (weapons and w not in weapons) or (opt != 'jetzt' and w not in CONCEPT_WEAPONS):
                continue
            W = weapon(opt, w)
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
            front = anc['Socket_Objective' if 'Socket_Objective' in anc else 'Socket_Reticle'].matrix_world.translation.copy()
            ground(eye.z - 1.55)
            # Seitenansicht: links, leicht von oben und vorn, auf Visier und Sitz
            at = (eye + front) / 2 + Vector((0, -0.02, -0.022))
            pos = at + Vector((0.34, -0.10, 0.07))
            cam.data.lens = 70
            cam.matrix_world = Matrix.Translation(pos) @ (at - pos).to_track_quat('-Z', 'Y').to_matrix().to_4x4()
            bpy.context.scene.render.filepath = os.path.join(DST, f'{opt}_{w}_seite.png')
            bpy.ops.render.render(write_still=True)
            # Zielbild (Augenpunkt, 75°, ads_hide aus)
            for p in W.PARTS:
                if p.get('ads_hide') and p['id'] in objs:
                    objs[p['id']].hide_render = True
            if opt != 'jetzt':
                d = (ret - eye).length / kit.MM
                px = 2 * d * math.tan(math.radians(HFOV / 2)) / RES[0]
                drawn_reticle(wtype, ret + Vector((0, 0.0004, 0)), d - 0.4, px)
            cam.data.lens = 18 / math.tan(math.radians(HFOV / 2))
            cam.matrix_world = Matrix.Translation(eye) @ Vector((0, -1, 0)).to_track_quat('-Z', 'Y').to_matrix().to_4x4()
            bpy.context.scene.render.filepath = os.path.join(DST, f'{opt}_{w}_ziel.png')
            bpy.ops.render.render(write_still=True)
            print('geschrieben', opt, w, flush=True)


def sheet():
    rows = []
    T = dict(geometry='620x349+4+4', bg='#4C525A', fg='#ECEFF2')
    for opt, name, de in options():
        tiles = []
        for w, lab in (('holo', 'Holo · im Zielen'), ('scope', 'Zielfernrohr · im Zielen'), ('holo', 'Holo · Seite'),
                       ('scope', 'Zielfernrohr · Seite')):
            view = 'ziel' if 'Zielen' in lab else 'seite'
            tiles += ['-label', lab, os.path.join(DST, f'{opt}_{w}_{view}.png')]
        out = os.path.join(DST, f'_row_{opt}.png')
        subprocess.run(['magick', 'montage', *tiles, '-tile', '4x1', '-geometry', T['geometry'], '-pointsize', '15', '-font', FONT,
                        '-background', T['bg'], '-fill', T['fg'], '-title', f'{name} – {de}', out], check=True)
        rows.append(out)
    refs = [r for r in REFS if os.path.exists(r)]
    if refs:
        out = os.path.join(DST, '_row_ref.png')
        tiles = []
        for r in refs:
            tiles += ['-label', f'Destiny 2 · Scout im Zielen ({os.path.basename(r)})', r]
        subprocess.run(['magick', 'montage', *tiles, '-tile', f'{len(refs)}x1', '-geometry', T['geometry'], '-pointsize', '15',
                        '-font', FONT, '-background', T['bg'], '-fill', T['fg'],
                        '-title', 'Referenz – Destiny 2, Video 1ERmScNiOk4 (Q-D2-ADS)', out], check=True)
        rows.insert(0, out)
    out = os.path.join(EVIDENCE, 'sight_options.png')
    subprocess.run(['magick', *rows, '+repage', '-background', T['bg'], '-gravity', 'west', '-append', '-depth', '8', out], check=True)
    print(out)


if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    if '--sheet' in a:
        sheet()
    else:
        render(dict(gpu='--gpu' in a, samples=int(a[a.index('--samples') + 1]) if '--samples' in a else 48),
               only=a[a.index('--only') + 1].split(',') if '--only' in a else None,
               weapons=a[a.index('--weapons') + 1].split(',') if '--weapons' in a else None)
