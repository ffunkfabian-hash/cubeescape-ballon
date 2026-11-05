"""Backen der AAA-Materialien für Unity (0.7 „Truecolor“); wird von tools/export_unity.py in Blender aufgerufen.

Die generierten Teile haben keine UVs. Je FBX entsteht ein gemeinsamer Atlas (alle Objekte zusammen abgewickelt und gepackt),
in den aus `kit.aaa_nodes` gebacken wird:
  albedo (sRGB)       Diffusfarbe = Grundfarbe · (1 − Metall), mit Kantenabrieb, Schmutz und Muster (Emission-Trick, EMIT)
  spec   (sRGB+A)     Spiegelfarbe F0 = Mix(0,08 · Specular IOR Level, Grundfarbe, Metall), A Glätte = 1 − Rauheit
                      (Unity URP Lit im Spezular-Modus: _SpecGlossMap; trifft Blenders geringe Spiegelung von Graphit/Gummi)
  normal (linear)     Mikrorelief im Tangentenraum (NORMAL, OpenGL wie Unity)
  ao     (linear)     Umgebungsverdeckung (AO), für _OcclusionMap
Glas, Absehen und Leuchtteile (Rollen mit emit oder alpha) werden nicht gebacken (eigene Materialien in Unity). Dazu `agx_lut`: die Blender-Ansicht AgX samt Look
als 3D-LUT (34³ als Streifen 1156 × 34) hinter einer log2-Formung, damit Unity dieselbe Tonwertabbildung benutzt.
"""
import math
import os

import bpy
import numpy as np

def _skip_roles():
    """Leuchtende und durchsichtige Rollen (Energie, Absehen, Gläser) nicht backen: Unity nimmt ihr eigenes Material."""
    from basic import kit
    return {k for k, v in kit.MATERIALS.items() if v.get('emit') or v.get('alpha') is not None}


SKIP_ROLES = _skip_roles()
LUT_N = 34                          # 33 Schritte: Mittelgrau (10 von 16,5 Blenden) liegt genau auf Gitterpunkt 20
LUT_EV = (-10.0, 6.5)               # Blenden um Mittelgrau 0,18 wie AgX (absolut log2 −12,47 … +4,03, also 1,8·10⁻⁴ … 16,3)


def role_of(ob):
    m = ob.data.materials[0] if ob.data.materials else None
    return m.get('basic_role') if m else None


def bakeable(ob):
    return ob.type == 'MESH' and role_of(ob) not in SKIP_ROLES and len(ob.data.polygons) > 0


def apply_modifiers(obs):
    """Modifikatoren anwenden (Bevel mit harden_normals; seit 0.32 ohne Weighted Normal, A6), damit UVs und Backen auf dem endgültigen Netz liegen."""
    dg = bpy.context.evaluated_depsgraph_get()
    for ob in obs:
        if not ob.modifiers:
            continue
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        old = ob.data
        ob.modifiers.clear()
        ob.data = me
        if old.users == 0:
            bpy.data.meshes.remove(old)


def unwrap(obs, margin=0.004):
    """Alle Objekte gemeinsam abwickeln und in einen Atlas packen (Inseln im Verhältnis ihrer 3D-Größe)."""
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for ob in obs:
        if ob.data.users > 1:                  # geteilte Netze trennen, sonst überlagern sich die Inseln
            ob.data = ob.data.copy()
        if not ob.data.uv_layers:
            ob.data.uv_layers.new(name='UVMap')
        ob.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=margin, area_weight=0.0, correct_aspect=True,
                             scale_to_bounds=False)
    bpy.ops.uv.average_islands_scale()
    bpy.ops.uv.pack_islands(rotate=True, margin=margin)
    bpy.ops.object.mode_set(mode='OBJECT')


def _image(name, size, srgb, alpha=False):
    im = bpy.data.images.get(name)
    if im:
        bpy.data.images.remove(im)
    im = bpy.data.images.new(name, size, size, alpha=alpha, float_buffer=not srgb)
    im.colorspace_settings.name = 'sRGB' if srgb else 'Non-Color'
    return im


def _mats(obs):
    return {ob.data.materials[0] for ob in obs}


def _source(nt, b, name):
    """Was am Eingang `name` des Principled BSDF hängt: (Ausgangssocket, None) oder (None, Standardwert)."""
    inp = b.inputs[name]
    if inp.is_linked:
        return inp.links[0].from_socket, None
    v = inp.default_value
    return None, (tuple(v) if hasattr(v, '__len__') else (v, v, v, 1.0))


def _link_or_set(N, L, b, name, target, gray=False):
    sock, val = _source(None, b, name)
    if sock is not None:
        L.new(sock, target)
    else:
        target.default_value = (val[0], val[0], val[0], 1.0) if gray else val


def _channel(N, L, b, channel, target):
    """Kanal für den Emission-Trick an `target` hängen; gibt Hilfsknoten zum Aufräumen zurück. Spezular-Modell wie Unity URP:
    diffuse = Grundfarbe · (1 − Metall), spec = Mix(F0 Dielektrikum = 0,08 · Specular IOR Level, Grundfarbe, Metall)."""
    if channel in ('rough', 'metal'):
        _link_or_set(N, L, b, {'rough': 'Roughness', 'metal': 'Metallic'}[channel], target, gray=True)
        return []
    mix = N.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.blend_type = 'MIX'
    fac, a_in, b_in, res = mix.inputs[0], mix.inputs[6], mix.inputs[7], mix.outputs[2]
    sm, vm = _source(None, b, 'Metallic')
    if sm is not None:
        L.new(sm, fac)
    else:
        fac.default_value = vm[0]
    extra = [mix]
    if channel == 'diffuse':
        _link_or_set(N, L, b, 'Base Color', a_in)
        b_in.default_value = (0.0, 0.0, 0.0, 1.0)
    else:   # spec
        ss, vs = _source(None, b, 'Specular IOR Level')
        if ss is not None:
            mul = N.new('ShaderNodeMath')
            mul.operation = 'MULTIPLY'
            mul.inputs[1].default_value = 0.08
            L.new(ss, mul.inputs[0])
            L.new(mul.outputs[0], a_in)
            extra.append(mul)
        else:
            f0 = 0.08 * vs[0]
            a_in.default_value = (f0, f0, f0, 1.0)
        _link_or_set(N, L, b, 'Base Color', b_in)
    L.new(res, target)
    return extra


CO_ATTR, PART_ATTR = 'ballon_co', 'ballon_part'         # zusammengefügte Kopie: Objektkoordinaten und Teil je Punkt (_joined)


def _object_coords(mats):
    """Muster aus `Texture Coordinate › Object` auf CO_ATTR umhängen: in der zusammengefügten Kopie ist der Objektraum der Waffenraum, die Muster
    verschobener Teile lägen sonst anders als im Render. Gibt den Rückweg zurück (restore_coords)."""
    undo = []
    for m in mats:
        nt = m.node_tree
        for tc in [n for n in nt.nodes if n.type == 'TEX_COORD']:
            links = list(tc.outputs['Object'].links)
            if not links:
                continue
            at = nt.nodes.new('ShaderNodeAttribute')
            at.attribute_type = 'GEOMETRY'
            at.attribute_name = CO_ATTR
            ends = [l.to_socket for l in links]
            for e in ends:
                nt.links.new(at.outputs['Vector'], e)
            undo.append((nt, at, tc, ends))
    return undo


def restore_coords(undo):
    for nt, at, tc, ends in undo:
        for e in ends:
            nt.links.new(tc.outputs['Object'], e)
        nt.nodes.remove(at)


def _bake(obs, mats, image, kind, samples, channel=None, margin=8):
    """Backt `kind` (EMIT mit Kanal albedo/rough/metal, NORMAL, AO) für alle Objekte in `image`."""
    undo = []
    for m in mats:
        nt = m.node_tree
        N, L = nt.nodes, nt.links
        tex = N.new('ShaderNodeTexImage')
        tex.image = image
        N.active = tex
        undo.append((m, tex, None))
        if kind == 'EMIT':
            b = N['Principled BSDF']
            out = next(n for n in N if n.type == 'OUTPUT_MATERIAL' and n.is_active_output)
            old = out.inputs['Surface'].links[0].from_socket if out.inputs['Surface'].is_linked else None
            em = N.new('ShaderNodeEmission')
            extra = _channel(N, L, b, channel, em.inputs['Color'])
            L.new(em.outputs['Emission'], out.inputs['Surface'])
            undo[-1] = (m, tex, (em, out, old, extra))
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for ob in obs:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    sc = bpy.context.scene
    sc.cycles.samples = samples
    sc.render.bake.margin = margin
    sc.render.bake.use_clear = True
    kw = dict(type=kind, margin=margin, use_clear=True)
    if kind == 'NORMAL':
        kw.update(normal_space='TANGENT', normal_r='POS_X', normal_g='POS_Y', normal_b='POS_Z')
    import time
    t0 = time.time()
    bpy.ops.object.bake(**kw)
    print(f'[bake_unity] {image.name} {kind} {channel or ""}: {time.time() - t0:.0f} s', flush=True)
    for m, tex, em in undo:
        nt = m.node_tree
        if em:
            e, out, old, extra = em
            for x in extra:
                nt.nodes.remove(x)
            nt.nodes.remove(e)
            if old is not None:
                nt.links.new(old, out.inputs['Surface'])
        nt.nodes.remove(tex)


def _joined(obs, join_all=True):
    """Alle Teile als eine Kopie zusammenfügen: Cycles backt je Objekt über den ganzen Atlas, eine Kopie statt 60 Teilen spart ein
    Vielfaches. Bis 0.42 blieben verschobene Teile (Drehpunkte) einzeln, weil ihr Objektraum die Rauschmuster trägt; seit 0.43 trägt das
    Attribut CO_ATTR je Punkt die alten Objektkoordinaten (_object_coords hängt die Muster beim Backen darauf um), PART_ATTR den Index des
    Teils. join_all=False backt wie bis 0.42 (Vergleich)."""
    from mathutils import Matrix
    same = list(obs) if join_all else [o for o in obs if o.matrix_world == Matrix.Identity(4)]
    rest = [o for o in obs if o not in same]
    if len(same) < 2:
        return obs, None
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    j = _join_copies(same)
    for o in same:          # Originale liegen deckungsgleich unter der Kopie: AO sähe sie als Verdeckung (gemessen 0,43 statt 0,64)
        o.hide_render = True
    j['ballon_hidden'] = [o.name for o in same]
    return [j] + rest, j


def _join_copies(same):
    """Kopien von `same` (Lage ins Netz, CO_ATTR, PART_ATTR) zu einem Objekt zusammenfügen."""
    from mathutils import Matrix
    cps = []
    for i, o in enumerate(same):
        c = o.copy()
        c.data = o.data.copy()
        mw = o.matrix_world.copy()
        c.parent = None
        bpy.context.scene.collection.objects.link(c)
        n = len(c.data.vertices)
        co = np.empty(n * 3, np.float32)
        c.data.vertices.foreach_get('co', co)
        c.data.attributes.new(CO_ATTR, 'FLOAT_VECTOR', 'POINT').data.foreach_set('vector', co)
        c.data.attributes.new(PART_ATTR, 'INT', 'POINT').data.foreach_set('value', np.full(n, i, np.int32))
        c.data.transform(mw)                  # Lage ins Netz (Drehpunkte, auseinandergelegte Armsegmente)
        c.matrix_world = Matrix.Identity(4)
        c.select_set(True)
        cps.append(c)
    bpy.context.view_layer.objects.active = cps[0]
    bpy.ops.object.join()
    return bpy.context.view_layer.objects.active


def joined_without(obs, ads):
    """0.44.1: Kopie aller Teile ohne die `ads_hide`-Teile (Namen in `ads`), unsichtbar für den Lichtweg. Im Zielen fehlen diese Teile,
    Flächen dahinter (Stirnfläche des Startrohrs hinter dem Kegel, BASIC-14) dürfen beim Backen nicht von ihnen verdeckt sein (AO, Schmutz).
    None, wenn kein Teil betroffen ist. Aufrufer nach _joined(obs); entfernen mit drop_view."""
    keep = [o for o in obs if o.name not in ads]
    if len(keep) == len(obs) or len(keep) < 2:
        return None
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    a = _join_copies(keep)
    a.hide_render = True
    return a


def drop_view(a):
    if a is not None:
        bpy.data.objects.remove(a)


def island_mask(o, size, name, margin):
    """Boolesches size²-Feld: UV-Inseln von o (weißer Emissionsdurchgang), margin Pixel Rand."""
    from tools import skin_masks as SM
    img = _image(name, size, False)
    ms = {s.material for s in o.material_slots if s.material}
    SM.bake_rgb([o], ms, img, {x: (1.0, 1.0, 1.0) for x in ms}, 1, margin)
    q = np.empty(size * size * 4, np.float32)
    img.pixels.foreach_get(q)
    bpy.data.images.remove(img)
    return q[0::4] > 0.5


def bake_views(run, image, tmp, a):
    """run(obs, image) backt in image. Mit `a` (joined_without): zweiter Durchgang ohne ads_hide-Teile als Verdecker, übernommen wird er
    auf den Inseln der übrigen Teile (Maske aus einem weißen Emissionsdurchgang, gleicher Rand), sonst der Durchgang mit allem."""
    run([tmp], image)
    if a is None:
        return
    size = image.size[0]
    im2 = _image(image.name + '_noads', size, False)
    tmp.hide_render, a.hide_render = True, False
    try:
        run([a], im2)
        keep_m = island_mask(a, size, image.name + '_noadsmask', 8)       # übrige Teile samt Bake-Rand
        keep_0 = island_mask(a, size, image.name + '_noadsk0', 0)
        tmp.hide_render, a.hide_render = False, True
        all_0 = island_mask(tmp, size, image.name + '_noadsa0', 0)
    finally:
        tmp.hide_render, a.hide_render = False, True
    ads_0 = all_0 & ~keep_0                                     # Inseln der ads_hide-Teile: nie überschreiben (Rand der anderen reicht nicht hinein)
    mask = (keep_m & ~ads_0).astype(np.float32)
    n = size * size * 4
    p1, p2 = (np.empty(n, np.float32) for _ in range(2))
    image.pixels.foreach_get(p1)
    im2.pixels.foreach_get(p2)
    m = np.repeat(mask, 4)
    m[3::4] = 1.0
    p2[3::4] = p1[3::4]
    image.pixels.foreach_set(p1 * (1.0 - m) + p2 * m)
    bpy.data.images.remove(im2)


# Bake-Einstellungen (0.43 „Kiln“, Messung und Grenzwerte: docs/versions/0.43-kiln.md). size von bake_atlas gilt für Albedo, normal_size ist die Untergrenze der
# Normalen (2048² wirkt beim Zielen fleckig, Albedo nicht), data_size gilt für Spec, Glätte und AO (TEXTURE_STORE legt sie ohnehin in 2048² ab). rand_samples: Abrieb (Bevel) und Schmutz (AO-Knoten) sind Zufallsverfahren, sie werden
# einmal in eine Maske gebacken (_freeze); danach sind Albedo, Spec und Glätte ohne Lichtweg und ohne Rauschen, emit_samples glättet nur noch die
# feinen Muster. 0 = Zufallsknoten in jedem Durchgang wie bis 0.42 (plain_samples). AO in 2048² rauscht bei gleichen Samples sichtbar mehr als die aus 4096²
# verkleinerte Karte bis 0.42, darum OIDN (ao_denoise).
SETTINGS = dict(data_size=2048, normal_size=4096, rand_samples=64, emit_samples=16, plain_samples=64, normal_samples=4, ao_samples=32, ao_denoise=True)


def _freeze(obs, mats, size, name, samples, tmp=None, noads=None):
    """Abrieb- und Schmutzmaske je Material einmal backen und in den Materialien an Stelle der Zufallsknoten einsetzen. Gibt (Bild, Rückweg)."""
    from tools import skin_masks as SM
    chains = {m: SM.chain(m) for m in mats}
    if not any('m' in c or 'g' in c for c in chains.values()):
        return None, []
    im = _image(f'{name}_rand', size, False)
    vals = {m: (c.get('m', 0.0), c.get('g', 0.0), 0.0) for m, c in chains.items()}
    if noads is None:
        SM.bake_rgb(obs, mats, im, vals, samples)
    else:
        bake_views(lambda o, i: SM.bake_rgb(o, mats, i, vals, samples), im, tmp, noads)
    undo = []
    for m, c in chains.items():
        keys = [k for k in ('m', 'g') if k in c]
        if not keys:
            continue
        nt = m.node_tree
        tex = nt.nodes.new('ShaderNodeTexImage')
        tex.image = im
        tex.interpolation = 'Closest'
        sep = nt.nodes.new('ShaderNodeSeparateColor')
        nt.links.new(tex.outputs['Color'], sep.inputs[0])
        back = []
        for i, k in enumerate(('m', 'g')):
            if k in c:
                ends = [l.to_socket for l in c[k].links]
                for e in ends:
                    nt.links.new(sep.outputs[i], e)
                back.append((c[k], ends))
        undo.append((nt, tex, sep, back))
    return im, undo


def _thaw(im, undo):
    for nt, tex, sep, back in undo:
        for src, ends in back:
            for e in ends:
                nt.links.new(src, e)
        nt.nodes.remove(tex)
        nt.nodes.remove(sep)
    if im:
        bpy.data.images.remove(im)


def _denoise(im, size, out_dir):
    """OIDN über den Kompositor (scene_build.Denoiser, ohne Führung: eine AO-Karte hat keine eigene Albedo). Atlasränder bleiben durch den Rand der Inseln
    getrennt."""
    import time
    from tools.scene_build import Denoiser
    t0 = time.time()
    d = Denoiser(out_dir)
    d.src.image = im
    tree = d.sc.compositing_node_group
    for n in (d.alb, d.nrm):
        tree.nodes.remove(n)
    d.alb = d.nrm = None
    d.sc.render.resolution_x = d.sc.render.resolution_y = size
    bpy.ops.render.render(write_still=True, scene=d.sc.name)
    r = bpy.data.images.load(d.path, check_existing=False)
    px = np.empty(size * size * 4, np.float32)
    r.pixels.foreach_get(px)
    bpy.data.images.remove(r)
    im.pixels.foreach_set(px)
    os.remove(d.path)
    bpy.data.node_groups.remove(tree)
    bpy.data.scenes.remove(d.sc)
    print(f'[bake_unity] {im.name} OIDN: {time.time() - t0:.1f} s', flush=True)


def bake_atlas(obs, name, size, out_dir, gpu=False, samples=None, join_all=True, color_only=False, settings=None, ads=()):
    """Backt den Atlas `name` für `obs` und schreibt <name>_albedo/_spec/_normal/_ao.png nach out_dir. size: Albedo (Schalter 2048/4096),
    settings: Abweichungen von SETTINGS, samples: rand_samples (Aufrufer von früher: der Kantenabrieb krisselt bei 12),
    ads: Namen der ads_hide-Teile (0.44.1: AO und Schmutz der übrigen Flächen ohne sie als Verdecker, joined_without)."""
    S = dict(SETTINGS, **(settings or {}))
    if samples:
        S['rand_samples'] = samples
    data = min(size, S['data_size'])
    nsize = max(size, S['normal_size'])                          # Normale nie unter normal_size: bei 2048² wird Relief nah am Auge beim Zielen fleckig
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    if gpu:
        pr = bpy.context.preferences.addons['cycles'].preferences
        pr.compute_device_type = 'METAL'
        pr.get_devices()
        for d in pr.devices:
            d.use = d.type == 'METAL'
        sc.cycles.device = 'GPU'
        print('[bake_unity] GPU:', [d.name for d in pr.devices if d.use], flush=True)
    sc.cycles.use_denoising = False
    if sc.world:
        sc.world.light_settings.distance = 0.03          # AO-Reichweite 3 cm (Viewmodel-Maßstab)
    noads = joined_without(obs, set(ads)) if ads and join_all else None
    obs, tmp = _joined(obs, join_all)
    if tmp is None:
        drop_view(noads)
        noads = None
    mats = {s.material for o in obs for s in o.material_slots if s.material}
    coords = _object_coords(mats) if tmp is not None and join_all else []
    res = {}
    import time
    t0 = time.time()
    rand, frozen = _freeze(obs, mats, size, name, S['rand_samples'], tmp, noads) if S['rand_samples'] else (None, [])
    emit = S['emit_samples'] if rand else S['plain_samples']
    al = _image(f'{name}_albedo', size, True)                  # Diffusfarbe (Spezular-Modell), sRGB
    _bake(obs, mats, al, 'EMIT', emit, 'diffuse')
    sp = _image(f'{name}_spec', data, True, alpha=True)          # Spiegelfarbe F0 (sRGB), Alpha = Glätte
    _bake(obs, mats, sp, 'EMIT', emit, 'spec')
    ro = _image(f'{name}_rough', data, False)
    _bake(obs, mats, ro, 'EMIT', emit, 'rough')
    _thaw(rand, frozen)
    if not color_only:                                           # Skins: Normale und AO sind für alle gleich (gleiche Form, gleiche UVs)
        nm = _image(f'{name}_normal', nsize, False)
        _bake(obs, mats, nm, 'NORMAL', S['normal_samples'])
        ao = _image(f'{name}_ao', data, False)
        if noads is None:
            _bake(obs, mats, ao, 'AO', S['ao_samples'])
        else:
            bake_views(lambda o, im: _bake(o, mats, im, 'AO', S['ao_samples']), ao, tmp, noads)
        if S['ao_denoise']:
            _denoise(ao, data, out_dir)
    n = data * data * 4
    r, px = np.empty(n, np.float32), np.empty(n, np.float32)
    ro.pixels.foreach_get(r)
    sp.pixels.foreach_get(px)
    px[3::4] = 1.0 - r[0::4]                                     # Alpha ist nie gammakodiert
    sp.pixels.foreach_set(px)
    for im, key in ((al, 'albedo'), (sp, 'spec')) + (() if color_only else ((nm, 'normal'), (ao, 'ao'))):
        path = os.path.join(out_dir, f'{name}_{key}.png')
        im.filepath_raw = path
        im.file_format = 'PNG'
        if key in ('albedo', 'spec'):
            im.save()
        else:                                            # lineare Daten unverändert (16 bit; Non-Color kennt keine Ansichtstransformation, tools/test_bake_settings)
            sc.render.image_settings.file_format = 'PNG'
            sc.render.image_settings.color_depth = '16'
            sc.render.image_settings.color_mode = 'RGB'
            im.save_render(path, scene=sc)
        res[key] = os.path.basename(path)
    bpy.data.images.remove(ro)
    restore_coords(coords)
    drop_view(noads)
    if tmp is not None:
        for nm in tmp.get('ballon_hidden', []):
            if nm in bpy.data.objects:
                bpy.data.objects[nm].hide_render = False
        bpy.data.objects.remove(tmp)
    print(f'[bake_unity] {name}: {len(obs)} Backobjekte, {size}² (Normale {nsize}², Daten {data}²), {time.time() - t0:.0f} s', flush=True)
    return res


def agx_lut(path, view='AgX', look='AgX - Medium High Contrast'):
    """Blender-Tonwertabbildung als 2D-Streifen einer 3D-LUT: Eingang log2-geformt (LUT_EV), Ausgang Anzeige-sRGB (16 bit)."""
    n = LUT_N
    ev0, ev1 = LUT_EV
    u = np.linspace(0.0, 1.0, n, dtype=np.float32)
    lin = 0.18 * np.power(2.0, ev0 + u * (ev1 - ev0)).astype(np.float32)
    lin[0] = 0.0
    w, h = n * n, n
    px = np.zeros((h, w, 4), np.float32)
    for b in range(n):                                    # Streifen: x = r + b·n, y = g (Unity-Konvention)
        px[:, b * n:(b + 1) * n, 0] = lin[None, :]
        px[:, b * n:(b + 1) * n, 1] = lin[:, None]
        px[:, b * n:(b + 1) * n, 2] = lin[b]
    px[..., 3] = 1.0
    im = bpy.data.images.new('agx_lut', w, h, float_buffer=True)
    im.colorspace_settings.name = 'Linear Rec.709'
    im.pixels.foreach_set(px.ravel())
    sc = bpy.context.scene
    vs = sc.view_settings
    old = (vs.view_transform, vs.look, vs.exposure, vs.gamma)
    vs.view_transform, vs.look, vs.exposure, vs.gamma = view, look, 0.0, 1.0
    sc.display_settings.display_device = 'sRGB'
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_depth = '16'
    sc.render.image_settings.color_mode = 'RGB'
    im.save_render(path, scene=sc)
    vs.view_transform, vs.look, vs.exposure, vs.gamma = old
    bpy.data.images.remove(im)
    return dict(file=os.path.basename(path), size=n, ev=list(LUT_EV), mid_grey=0.18, view=view, look=look,
                de='3D-LUT als Streifen (Breite n², Höhe n), x = R + B·n, y = G; Eingang u = (log2(c/0,18) − ev0)/(ev1 − ev0)')
