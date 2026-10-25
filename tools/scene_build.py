"""Hintergrundszenen bauen und backen (0.8 „Hangar“), Format `ballon-scene/1` (docs/szenen-format.md).

  BALLON_BAKE_GPU=1 ce lock gpu -- blender -b --factory-startup -P <abs>/tools/scene_build.py -- hangar
        → unity/Assets/Ballon/Generated/Scenes/hangar/{hangar.fbx, hangar_light.png, scene_hangar.json}
          ~/Library/Caches/CubeEscapeBallon/unity/scenes/hangar_ref.png (Vergleichsrender vom Startpunkt, nicht im Repo)
  python3 tools/scene_build.py --check   → jede Szene in basic/scenes/ hat aktuelle Dateien (ohne Blender, Teil von ./check)

Ablauf in Blender: Bauteile aus `basic/scenes/<name>.py` je Gruppe zu einem Netz (Weltlage im Netz, Objekte im Ursprung),
Umgebungsmaterialien (Principled, Rauschen und Muster im Weltraum), Lichter und Himmel; gemeinsame Lightmap-UVs (Smart UV,
gleiche Texeldichte, gepackt); eine zusammengefügte Kopie backt das diffuse Licht (direkt + indirekt, mal Farbe, dazu die
Leuchtflächen; ohne Glanz) in einen Atlas; Panorama am Startpunkt misst das Umgebungslicht (`ambient`); Vergleichsrender;
FBX wie tools/export_unity.py. Testläufe: BALLON_SCENE_SIZE / BALLON_SCENE_SAMPLES setzen → Ausgabe nur in den Cache.
"""
import hashlib
import importlib
import json
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic import scenes as SC  # noqa: E402

FORMAT = 'ballon-scene/1'
DST = os.path.join(ROOT, 'unity', 'Assets', 'Ballon', 'Generated', 'Scenes')
CACHE = os.path.expanduser('~/Library/Caches/CubeEscapeBallon/unity/scenes')
MEASURED = ('ambient',)            # in Blender gemessen; --check vergleicht nur die übrigen Felder


def r6(v):
    if isinstance(v, (list, tuple)):
        return [r6(x) for x in v]
    return round(float(v), 6) + 0.0


def scene_names():
    d = os.path.join(ROOT, 'basic', 'scenes')
    return sorted(f[:-3] for f in os.listdir(d) if f.endswith('.py') and not f.startswith('_'))


def load(name):
    return importlib.import_module(f'basic.scenes.{name}')


def sources(name):
    files = ['basic/scenes/__init__.py', f'basic/scenes/{name}.py', 'tools/scene_build.py']
    return [dict(path=p, sha256=hashlib.sha256(open(os.path.join(ROOT, p), 'rb').read()).hexdigest()) for p in files]


def groups(S):
    out = []
    for p in S.PARTS:
        if p['group'] not in out:
            out.append(p['group'])
    return out


def data(S):
    """Szenendatei ohne Blender (alles außer den gemessenen Feldern MEASURED)."""
    name = S.META['name']
    cols = []
    for p in S.PARTS:
        if not p['collide']:
            continue
        lo, hi = SC.bounds(p)
        cols.append(dict(name=p['id'], center=r6([(a + b) / 2 for a, b in zip(lo, hi)]), size=r6([b - a for a, b in zip(lo, hi)])))
    lights = [dict(name=L['name'], kind=L['kind'], pos=r6(L['pos']), dir=r6(L['dir']), power_w=r6(L['power_w']), size_m=r6(L['size_m']),
                   color=L['color']) for L in S.LIGHTS]
    sp = S.SPAWN['pos']
    R = S.REFERENCE
    return dict(
        format=FORMAT, name=name, de=S.META['de'], fbx=f'{name}.fbx',
        light_atlas=dict(file=f'{name}_light.png', size=S.BAKE['size'], scale=r6(S.BAKE.get('scale', 1.0)),
                         de='Diffuses Cycles-Licht (direkt + indirekt) mal Farbe, dazu Leuchtflächen, ohne Glanz; gespeichert '
                            'Licht / scale als sRGB 8 bit, Unity multipliziert mit scale; Umgebung in Unity unbeleuchtet'),
        objects=groups(S), colliders=cols,
        spawn=dict(pos=r6(sp), yaw_deg=r6(S.SPAWN['yaw_deg'])),
        sky=dict(color=S.SKY['color'], strength=r6(S.SKY['strength'])),
        ambient=None,
        lights=lights,
        targets=[dict(pos=r6(t['pos']), distance=r6(t['distance'])) for t in S.TARGETS],
        reference=dict(png=f'{name}_ref.png', camera_pos=r6((sp[0], sp[1], sp[2] + R['eye_m'])), yaw_deg=r6(S.SPAWN['yaw_deg']),
                       pitch_deg=0.0, h_fov_deg=r6(R['h_fov_deg']), view=R['view'], look=R['look']),
        sources=sources(name))


def write_json(path, obj):
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
        fh.write('\n')


def check():
    bad = []
    for name in scene_names():
        S = load(name)
        e = SC.validate(S)
        if e:
            bad.append(f'{name}: ' + '; '.join(e[:3]))
            continue
        d = os.path.join(DST, name)
        p = os.path.join(d, f'scene_{name}.json')
        if not os.path.exists(p):
            bad.append(f'{name}: scene_{name}.json fehlt (tools/scene_build.py in Blender ausführen)')
            continue
        cur = json.load(open(p, encoding='utf-8'))
        new = json.loads(json.dumps(data(S), ensure_ascii=False))
        diff = [k for k in new if k not in MEASURED and cur.get(k) != new[k]]
        if diff:
            bad.append(f'{name}: scene_{name}.json veraltet ({", ".join(diff)}): Szene neu bauen')
        if not cur.get('ambient'):
            bad.append(f'{name}: ambient fehlt')
        for f in (cur.get('fbx'), cur.get('light_atlas', {}).get('file')):
            if not f or not os.path.exists(os.path.join(d, f)):
                bad.append(f'{name}: {f} fehlt')
    if bad:
        print(' | '.join(bad))
        return 1
    print(f'szenen: {", ".join(scene_names())} aktuell')
    return 0


# ------------------------------------------------------------------ Blender-Teil
def log(msg, t0=None):
    print(f'[scene_build] {msg}' + (f' ({time.time() - t0:.1f} s)' if t0 is not None else ''), flush=True)


def material(role, R):
    """Umgebungsmaterial: Principled, Helligkeitsrauschen (vary), Fugen oder Warnstreifen im Weltraum."""
    import bpy
    from basic.kit import hex_rgba
    m = bpy.data.materials.new(f'ENV_{role}')
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N['Principled BSDF']
    b.inputs['Roughness'].default_value = R['rough']
    b.inputs['Metallic'].default_value = 0.0
    b.inputs['Specular IOR Level'].default_value = R.get('spec', 0.5)
    geo = N.new('ShaderNodeNewGeometry')
    pos = geo.outputs['Position']

    def math_node(op, a, bval=None, c=None):
        n = N.new('ShaderNodeMath')
        n.operation = op
        for i, v in enumerate((a, bval, c)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]

    def mul_color(col, fac):
        mx = N.new('ShaderNodeMix')
        mx.data_type = 'RGBA'
        mx.blend_type = 'MULTIPLY'
        mx.inputs[0].default_value = 1.0
        if isinstance(col, tuple):
            mx.inputs[6].default_value = col
        else:
            L.new(col, mx.inputs[6])
        L.new(fac, mx.inputs[7])
        return mx.outputs[2]

    col = hex_rgba(R['color'])
    if R.get('pattern') == 'stripes':       # 45°-Streifen: Phase (x + y + z) / (√2 · 2 · Breite)
        sep = N.new('ShaderNodeSeparateXYZ')
        L.new(pos, sep.inputs[0])
        s = math_node('ADD', math_node('ADD', sep.outputs[0], sep.outputs[1]), sep.outputs[2])
        ph = math_node('FRACT', math_node('DIVIDE', s, math.sqrt(2) * 2 * R['stripe_m']))
        fac = math_node('LESS_THAN', ph, 0.5)
        mx = N.new('ShaderNodeMix')
        mx.data_type = 'RGBA'
        mx.inputs[6].default_value = hex_rgba(R['color2'])
        mx.inputs[7].default_value = col
        L.new(fac, mx.inputs[0])
        col = mx.outputs[2]
    if R.get('vary'):
        no = N.new('ShaderNodeTexNoise')
        no.inputs['Scale'].default_value = 1.0 / R['vary_m']
        no.inputs['Detail'].default_value = 4.0
        no.inputs['Roughness'].default_value = 0.55
        L.new(pos, no.inputs['Vector'])
        mr = N.new('ShaderNodeMapRange')
        mr.inputs['From Min'].default_value = 0.3
        mr.inputs['From Max'].default_value = 0.7
        mr.inputs['To Min'].default_value = 1.0 - R['vary']
        mr.inputs['To Max'].default_value = 1.0 + R['vary'] * 0.5
        L.new(no.outputs['Fac'], mr.inputs['Value'])
        col = mul_color(col, mr.outputs['Result'])
        rr = N.new('ShaderNodeMapRange')
        rr.inputs['To Min'].default_value = R['rough'] * 0.85
        rr.inputs['To Max'].default_value = min(1.0, R['rough'] * 1.12)
        L.new(no.outputs['Fac'], rr.inputs['Value'])
        L.new(rr.outputs['Result'], b.inputs['Roughness'])
    if R.get('pattern') == 'joints':        # Fugen alle 6 m, 2 cm dunkel
        sep = N.new('ShaderNodeSeparateXYZ')
        L.new(pos, sep.inputs[0])
        ds = []
        for o in (sep.outputs[0], sep.outputs[1]):
            f = math_node('FRACT', math_node('ADD', math_node('DIVIDE', o, 6.0), 0.5))
            ds.append(math_node('MULTIPLY', math_node('ABSOLUTE', math_node('SUBTRACT', f, 0.5)), 6.0))
        d = math_node('MINIMUM', ds[0], ds[1])
        mr = N.new('ShaderNodeMapRange')
        mr.inputs['From Min'].default_value = 0.008
        mr.inputs['From Max'].default_value = 0.025
        mr.inputs['To Min'].default_value = 0.5
        mr.inputs['To Max'].default_value = 1.0
        L.new(d, mr.inputs['Value'])
        col = mul_color(col, mr.outputs['Result'])
    if R.get('ribs'):                       # Trapezprofil als Relief: h = Rampe(|fract(u/T) − ½|·2), Flanken 30 %
        ax, per, depth = R['ribs']
        sep = N.new('ShaderNodeSeparateXYZ')
        L.new(pos, sep.inputs[0])
        u = math_node('ADD', sep.outputs[0], sep.outputs[1]) if ax == 'xy' else sep.outputs[0]
        tri = math_node('MULTIPLY', math_node('ABSOLUTE', math_node('SUBTRACT', math_node('FRACT', math_node('DIVIDE', u, per)), 0.5)), 2.0)
        mr = N.new('ShaderNodeMapRange')
        mr.inputs['From Min'].default_value = 0.35
        mr.inputs['From Max'].default_value = 0.65
        L.new(tri, mr.inputs['Value'])
        bu = N.new('ShaderNodeBump')
        bu.inputs['Distance'].default_value = depth
        bu.inputs['Strength'].default_value = 1.0
        L.new(mr.outputs['Result'], bu.inputs['Height'])
        L.new(bu.outputs['Normal'], b.inputs['Normal'])
    if isinstance(col, tuple):
        b.inputs['Base Color'].default_value = col
    else:
        L.new(col, b.inputs['Base Color'])
    if R.get('emit'):
        b.inputs['Emission Color'].default_value = hex_rgba(R['color'])
        b.inputs['Emission Strength'].default_value = R['emit']
    m.diffuse_color = hex_rgba(R['color'])
    m['scene_role'] = role
    return m


def _box_faces(a, b, skip):
    (x0, y0, z0), (x1, y1, z1) = a, b
    V = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    F = {'-z': (0, 3, 2, 1), '+z': (4, 5, 6, 7), '-y': (0, 1, 5, 4), '+y': (2, 3, 7, 6), '-x': (3, 0, 4, 7), '+x': (1, 2, 6, 5)}
    sk = set(skip)
    if abs(z0) < 1e-4:                     # Unterseite auf dem Boden: unsichtbar
        sk.add('-z')
    return V, [f for k, f in F.items() if k not in sk]


def add_part(bm, p, mi):
    """Bauteil als Flächen ins bmesh (Weltlage), Normalen nach außen."""
    from mathutils import Vector
    s = p['shape']
    smooth = False
    if s == 'box':
        V, F = _box_faces(p['a'], p['b'], p['skip'])
        cen = Vector([(x + y) / 2 for x, y in zip(p['a'], p['b'])])
    elif s == 'beam':
        V = SC.beam_frame(p['a'], p['b'], p['w'], p['h'])
        F = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        cen = Vector([(x + y) / 2 for x, y in zip(p['a'], p['b'])])
    elif s == 'cyl':
        i = SC.AX[p['axis']]
        j, k = [q for q in range(3) if q != i]
        n = p['segs']
        V = []
        for e in (-0.5, 0.5):
            for t in range(n):
                a = 2 * math.pi * (t + 0.5) / n
                v = list(p['c'])
                v[i] += e * p['l']
                v[j] += p['r'] * math.cos(a)
                v[k] += p['r'] * math.sin(a)
                V.append(tuple(v))
        F = [(t, (t + 1) % n, n + (t + 1) % n, n + t) for t in range(n)]
        caps = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))]
        if p['axis'] == 'z' and abs(p['c'][2] - p['l'] / 2) < 1e-4:
            caps = caps[1:]
        F += caps
        cen = Vector(p['c'])
        smooth = True
    else:
        raise ValueError(s)
    vs = [bm.verts.new(v) for v in V]
    for f in F:
        face = bm.faces.new([vs[q] for q in f])
        face.material_index = mi
        face.normal_update()
        if face.normal.dot(face.calc_center_median() - cen) < 0:
            face.normal_flip()
        face.smooth = smooth and len(f) == 4
    return len(F)


def build(S):
    import bpy
    import bmesh
    from basic.kit import hex_rgba
    t0 = time.time()
    mats = {r: material(r, R) for r, R in S.ROLES.items()}
    objs = []
    for g in groups(S):
        parts = [p for p in S.PARTS if p['group'] == g]
        roles = []
        for p in parts:
            if p['mat'] not in roles:
                roles.append(p['mat'])
        bm = bmesh.new()
        for p in parts:
            add_part(bm, p, roles.index(p['mat']))
        me = bpy.data.meshes.new(g)
        bm.to_mesh(me)
        bm.free()
        for r in roles:
            me.materials.append(mats[r])
        ob = bpy.data.objects.new(g, me)
        bpy.context.scene.collection.objects.link(ob)
        objs.append(ob)
    sc = bpy.context.scene
    for L in S.LIGHTS:
        if L['kind'] == 'area':
            ld = bpy.data.lights.new(L['name'], 'AREA')
            ld.size = L['size_m']
        elif L['kind'] == 'sun':
            ld = bpy.data.lights.new(L['name'], 'SUN')
            ld.angle = math.radians(L.get('angle_deg', 1.0))
        elif L['kind'] == 'spot':
            ld = bpy.data.lights.new(L['name'], 'SPOT')
            ld.shadow_soft_size = L['size_m']
        else:
            ld = bpy.data.lights.new(L['name'], 'POINT')
            ld.shadow_soft_size = L['size_m']
        ld.energy = L['power_w']
        ld.color = hex_rgba(L['color'])[:3]
        lo = bpy.data.objects.new(L['name'], ld)
        lo.location = L['pos']
        from mathutils import Vector
        lo.rotation_euler = Vector(L['dir']).to_track_quat('-Z', 'Y').to_euler()
        lo.visible_camera = False                # Leuchtfläche zeigt das Netz (lamp), nicht die Lichtquelle
        sc.collection.objects.link(lo)
    w = bpy.data.worlds.new('Sky')
    w.use_nodes = True
    bg = w.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = hex_rgba(S.SKY['color'])
    bg.inputs['Strength'].default_value = S.SKY['strength']
    sc.world = w
    tris = sum(len(f.vertices) - 2 for o in objs for f in o.data.polygons)
    log(f'gebaut: {len(objs)} Objekte, {len(S.PARTS)} Bauteile, {tris} Dreiecke, {len(S.LIGHTS)} Lichter', t0)
    return objs, tris


def setup_cycles(gpu, samples, B):
    import bpy
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    if gpu:
        pr = bpy.context.preferences.addons['cycles'].preferences
        pr.compute_device_type = 'METAL'
        pr.get_devices()
        for d in pr.devices:
            d.use = d.type == 'METAL'
        sc.cycles.device = 'GPU'
        log(f"GPU: {[d.name for d in pr.devices if d.use]}")
    else:
        log('CPU (ohne BALLON_BAKE_GPU=1)')
    c = sc.cycles
    c.samples = samples
    c.max_bounces = B['bounces']
    c.diffuse_bounces = B['bounces']
    c.glossy_bounces = 2
    c.transmission_bounces = 0
    c.transparent_max_bounces = 2
    c.caustics_reflective = False
    c.caustics_refractive = False
    c.sample_clamp_indirect = B['clamp_indirect']
    c.use_light_tree = True
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'


def unwrap(objs, size, pack_px):
    """Gemeinsame Lightmap-UVs: Smart UV, Inseln auf gleiche Texeldichte, gepackt (Abstand pack_px Texel)."""
    import bpy
    t0 = time.time()
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for ob in objs:
        ob.data.uv_layers.new(name='UVMap')
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(50), island_margin=0.0, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
    log('Smart UV', t0)
    bpy.ops.uv.average_islands_scale()
    bpy.ops.uv.pack_islands(rotate=True, margin_method='FRACTION', margin=pack_px / size, shape_method='AABB')
    bpy.ops.object.mode_set(mode='OBJECT')
    log('UV gepackt', t0)
    a3 = auv = 0.0
    for ob in objs:
        me = ob.data
        uv = me.uv_layers.active.data
        for f in me.polygons:
            a3 += f.area
            pts = [uv[li].uv for li in f.loop_indices]
            s = 0.0
            for i in range(len(pts)):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % len(pts)]
                s += x0 * y1 - x1 * y0
            auv += abs(s) / 2
    dens = math.sqrt(auv * size * size / a3)
    log(f'Lightmap: {a3:.0f} m² Fläche, Atlas belegt {auv * 100:.1f} %, {dens:.1f} Texel/m ({100 / dens:.1f} cm je Texel)')
    return dict(area_m2=a3, uv_fill=auv, texel_per_m=dens)


def measure_ambient(S, out_dir, gpu):
    """Mittlere Radianz der Umgebung am Startpunkt (Augenhöhe): Panorama 256 × 128, raumwinkelgewichtet."""
    import bpy
    import numpy as np
    from mathutils import Euler
    t0 = time.time()
    sc = bpy.context.scene
    cd = bpy.data.cameras.new('Pano')
    cd.type = 'PANO'
    cd.panorama_type = 'EQUIRECTANGULAR'
    cam = bpy.data.objects.new('Pano', cd)
    sc.collection.objects.link(cam)
    sp = S.SPAWN['pos']
    cam.location = (sp[0], sp[1], sp[2] + S.REFERENCE['eye_m'])
    cam.rotation_euler = Euler((math.radians(90), 0, math.radians(180)))
    sc.camera = cam
    old = (sc.render.resolution_x, sc.render.resolution_y, sc.cycles.samples)
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 256, 128, 100
    sc.cycles.samples = 64
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = 'OPEN_EXR'
    sc.render.image_settings.color_depth = '32'
    p = os.path.join(out_dir, f"{S.META['name']}_pano.exr")
    sc.render.filepath = p
    bpy.ops.render.render(write_still=True)
    im = bpy.data.images.load(p)
    w, h = im.size
    px = np.empty(w * h * 4, np.float32)
    im.pixels.foreach_get(px)
    px = px.reshape(h, w, 4)[..., :3]
    lat = (np.arange(h) + 0.5) / h * math.pi - math.pi / 2
    wt = np.cos(lat)[:, None, None]
    avg = (px * wt).sum(axis=(0, 1)) / (wt.sum() * w)
    bpy.data.images.remove(im)
    sc.render.resolution_x, sc.render.resolution_y, sc.cycles.samples = old
    bpy.data.objects.remove(cam)
    mx = float(max(avg))
    c = [float(x) / mx for x in avg]
    srgb = ['%02X' % round(255 * (12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055)) for v in c]
    log(f'Umgebungslicht am Startpunkt: linear {avg.round(4).tolist()}', t0)
    return dict(color='#' + ''.join(srgb), strength=r6(round(mx, 4)))     # Farbe (Maximum 1) × Stärke = mittlere Radianz


def bake(objs, S, size, samples, out_path):
    """Eine zusammengefügte Kopie backt COMBINED mit Filter Emission + Diffus (direkt, indirekt) in einen Float-Atlas,
    danach sRGB 8 bit mit Dither. Gibt Kennzahlen zurück."""
    import bpy
    import numpy as np
    from tools import bake_unity as BK
    t0 = time.time()
    work, joined = BK._joined(objs, join_all=True)
    j = work[0]
    for o in objs:                 # Originale liegen deckungsgleich unter der Kopie: aus dem Backen nehmen, sonst Schatten auf alles
        o.hide_render = True
    log(f'Backobjekt zusammengefügt: {len(j.data.polygons)} Flächen', t0)
    im = BK._image(f"{S.META['name']}_light_f", size, srgb=False)
    im.colorspace_settings.name = 'Linear Rec.709'
    mats = {s.material for s in j.material_slots if s.material}
    added = []
    for m in mats:
        tex = m.node_tree.nodes.new('ShaderNodeTexImage')
        tex.image = im
        m.node_tree.nodes.active = tex
        added.append((m, tex))
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    j.select_set(True)
    bpy.context.view_layer.objects.active = j
    sc = bpy.context.scene
    sc.cycles.samples = samples
    rb = sc.render.bake
    rb.margin = S.BAKE['margin_px']
    rb.margin_type = 'EXTEND'
    rb.use_clear = True
    t1 = time.time()
    log(f'Backen {size}² mit {samples} Samples …')
    bpy.ops.object.bake(type='COMBINED', pass_filter={'EMIT', 'DIRECT', 'INDIRECT', 'DIFFUSE'}, margin=S.BAKE['margin_px'],
                        use_clear=True)
    tb = time.time() - t1
    log(f'gebacken: {tb / 60:.1f} min', t1)
    for m, tex in added:
        m.node_tree.nodes.remove(tex)
    n = size * size * 4
    px = np.empty(n, np.float32)
    im.pixels.foreach_get(px)
    rgb = px.reshape(-1, 4)[:, :3]
    clip = float((rgb.max(axis=1) > 1.0).mean())
    vmax = float(rgb.max())
    k = float(S.BAKE.get('scale', 1.0))
    clip = float((rgb.max(axis=1) > k).mean())           # über k wird abgeschnitten
    lin = np.clip(rgb / k, 0.0, 1.0)
    s = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * np.power(lin, 1 / 2.4) - 0.055)
    rng = np.random.default_rng(1)
    s = s + (rng.random(s.shape, dtype=np.float32) - rng.random(s.shape, dtype=np.float32)) / 255.0   # Dreiecks-Dither ±1 LSB
    s = np.clip(np.round(s * 255.0) / 255.0, 0.0, 1.0)
    out = np.ones((size * size, 4), np.float32)
    out[:, :3] = s
    ob = bpy.data.images.new(f"{S.META['name']}_light", size, size, alpha=False)
    ob.colorspace_settings.name = 'sRGB'
    ob.pixels.foreach_set(out.ravel())
    ob.filepath_raw = out_path
    ob.file_format = 'PNG'
    ob.save()
    bpy.data.images.remove(im)
    if joined is not None:
        bpy.data.objects.remove(joined)
    for o in objs:
        o.hide_render = False
    log(f'Atlas {os.path.basename(out_path)}: max {vmax:.2f}, Skala {k:g}, {clip * 100:.2f} % der Texel über {k:g}', t0)
    return dict(bake_s=tb, clip=clip, vmax=vmax)


def render_view(S, path, samples, denoise=True):
    """Bild vom Startpunkt: Augenhöhe, 75° horizontal, Blick nach −Y, AgX mit Look (wie `reference` in der Szenendatei)."""
    import bpy
    from mathutils import Euler
    sc = bpy.context.scene
    R = S.REFERENCE
    cd = bpy.data.cameras.new('Ref')
    cd.sensor_fit = 'HORIZONTAL'
    cd.angle = math.radians(R['h_fov_deg'])
    cd.clip_start = 0.05
    cd.clip_end = 500
    cam = bpy.data.objects.new('Ref', cd)
    sc.collection.objects.link(cam)
    sp = S.SPAWN['pos']
    cam.location = (sp[0], sp[1], sp[2] + R['eye_m'])
    cam.rotation_euler = Euler((math.radians(90), 0, math.radians(180 + S.SPAWN['yaw_deg'])))   # Blick −Y (LESSONS)
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = R['res']
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.cycles.samples = samples
    sc.cycles.use_denoising = denoise
    sc.view_settings.view_transform = R['view']
    sc.view_settings.look = R['look']
    sc.view_settings.exposure = 0.0
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_depth = '8'
    sc.render.image_settings.color_mode = 'RGB'
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    bpy.data.objects.remove(cam)


def atlas_view(S, objs, atlas, path):
    """Wie Unity: Umgebung unbeleuchtet mit dem Atlas (Emission = Atlasfarbe), Himmel als Hintergrund; gleiche Kamera.
    Gibt die mittlere Abweichung zum Vergleichsrender zurück (0–255, alle Kanäle)."""
    import bpy
    import numpy as np
    m = objs[0].data.materials[0]
    nt = m.node_tree
    N = nt.nodes
    for n in list(N):
        if n.type != 'OUTPUT_MATERIAL':
            N.remove(n)
    tex = N.new('ShaderNodeTexImage')
    tex.image = bpy.data.images.load(atlas)
    tex.image.colorspace_settings.name = 'sRGB'
    em = N.new('ShaderNodeEmission')
    em.inputs['Strength'].default_value = float(S.BAKE.get('scale', 1.0))   # wie Unity: Atlas mal scale
    nt.links.new(tex.outputs['Color'], em.inputs['Color'])
    out = next(n for n in N if n.type == 'OUTPUT_MATERIAL')
    nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
    render_view(S, path, 16, denoise=False)
    return path


def image_diff(a, b):
    import bpy
    import numpy as np
    ims = [bpy.data.images.load(p) for p in (a, b)]
    px = []
    for im in ims:
        v = np.empty(im.size[0] * im.size[1] * 4, np.float32)
        im.pixels.foreach_get(v)
        px.append(v.reshape(-1, 4)[:, :3])
        bpy.data.images.remove(im)
    return float(np.abs(px[0] - px[1]).mean() * 255)


def export_fbx(objs, name, path):
    import bpy
    m = bpy.data.materials.new(f'{name}_light')      # ein Material: Unity zeigt den Atlas unbeleuchtet
    for ob in objs:
        me = ob.data
        me.materials.clear()
        me.materials.append(m)
        for f in me.polygons:
            f.material_index = 0
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'MESH'}, use_mesh_modifiers=True,
                             mesh_smooth_type='OFF', use_custom_props=False, add_leaf_bones=False, bake_anim=False,
                             apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL', bake_space_transform=True,
                             axis_forward='-Z', axis_up='Y', path_mode='STRIP', embed_textures=False)


def blender_main():
    import bpy
    T0 = time.time()
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    name = argv[0] if argv else 'hangar'
    gpu = '--gpu' in argv or os.environ.get('BALLON_BAKE_GPU') == '1'
    S = load(name)
    err = SC.validate(S)
    if err:
        raise SystemExit('[scene_build] Szene fehlerhaft: ' + '; '.join(err))
    size = int(os.environ.get('BALLON_SCENE_SIZE', S.BAKE['size']))
    samples = int(os.environ.get('BALLON_SCENE_SAMPLES', S.BAKE['samples']))
    test = size != S.BAKE['size'] or samples != S.BAKE['samples'] or os.environ.get('BALLON_SCENE_TEST') == '1'
    out = os.path.join(CACHE, 'test') if test else os.path.join(DST, name)
    os.makedirs(out, exist_ok=True)
    os.makedirs(CACHE, exist_ok=True)
    log(f'Szene {name}: Atlas {size}², {samples} Samples, Ausgabe {out}' + (' (Testlauf)' if test else ''))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    objs, tris = build(S)
    setup_cycles(gpu, samples, S.BAKE)
    uvs = unwrap(objs, size, S.BAKE['pack_margin_px'])
    amb = measure_ambient(S, CACHE, gpu)
    setup_cycles(gpu, samples, S.BAKE)
    bk = bake(objs, S, size, samples, os.path.join(out, f'{name}_light.png'))
    ref = os.path.join(CACHE, f'{name}_ref.png' if not test else f'test/{name}_ref.png')
    t0 = time.time()
    render_view(S, ref, S.REFERENCE['samples'])
    log(f'Vergleichsrender {ref}', t0)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(CACHE, f'{name}_build.blend' if not test else f'test/{name}_build.blend'))
    export_fbx(objs, name, os.path.join(out, f'{name}.fbx'))
    t0 = time.time()
    av = atlas_view(S, objs, os.path.join(out, f'{name}_light.png'), ref.replace('_ref.png', '_atlas_view.png'))
    log(f'Atlasansicht (unbeleuchtet wie Unity) {av}: mittlere Abweichung zum Vergleichsrender {image_diff(ref, av):.1f}/255', t0)
    D = data(S)
    D['ambient'] = amb
    write_json(os.path.join(out, f'scene_{name}.json'), D)
    log(f'fertig: {len(objs)} Objekte, {tris} Dreiecke, {len(D["colliders"])} Kollisionsquader, Backen {bk["bake_s"] / 60:.1f} min '
        f'({samples} Samples), {uvs["texel_per_m"]:.1f} Texel/m, Atlas {uvs["uv_fill"] * 100:.0f} % belegt, '
        f'{bk["clip"] * 100:.2f} % abgeschnitten', T0)


if __name__ == '__main__':
    try:
        import bpy  # noqa: F401
        IN_BLENDER = True
    except ImportError:
        IN_BLENDER = False
    if IN_BLENDER:
        blender_main()
    else:
        sys.exit(check() if '--check' in sys.argv else (print(__doc__) or 0))
