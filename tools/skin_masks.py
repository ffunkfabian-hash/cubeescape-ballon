"""Skin-Masken je Waffe (0.42 „Quickslot“, Entscheid 247 A): statt voller Farb- und Glanzkarten je Skin (≈ 4 MB je Skin und Waffe) backt
Blender einmal je Waffe die Werte, aus denen kit.aaa_nodes die Grundfarbe mischt; tools/skin_compose.py setzt daraus jeden Skin auf dem
Standard-Atlas zusammen (lokal bei `unity_run.py setup`, nicht im Repo).

  BALLON_BAKE_GPU=1 ce lock gpu -- blender -b --factory-startup -P <abs>/tools/skin_masks.py [-- BASIC-09-v2.1 …]

Mischkette je Rolle (kit.aaa_nodes): Grundfarbe C (Skin-Rolle bzw. Tarnmuster) → Abrieb mix(C, #9EA3A9, m) → Schmutz mix(·, #3B3329, g)
→ Kratzer mix(·, #A7ACB2, s); Metall mix(metal, 1, m), Rauheit mix(r, 0,28, m). Die Abriebmaske m (Bevel, 8 Samples) rauscht je Sample,
und die Diffusfarbe hängt quadratisch von m ab (Grundfarbe · (1 − Metall)): der Atlas mittelt das Produkt. Gebacken werden darum E[m] und
E[m²] je Abriebstufe (Emission, 64 Samples wie der Atlas); g (AO, unabhängige Samples) und s (Noise, ohne Zufall) gehen linear ein. Drei PNG
(8 bit, linear, ohne Alpha – OpenImageIO behandelt Alpha als vormultipliziert) und das Tarnmuster:
  <atlas>_skinmask_a.png  E[m], E[m²] (Standard-Abrieb), E[g] (Standard-Schmutz)                        MASK_SIZE²
  <atlas>_skinmask_b.png  E[m], E[m²] (Nachtschicht: wear 1,4), s (Kratzer)                             MASK_SIZE²
  <atlas>_skinmask_c.png  E[m], E[m²] (Gebraucht: wear 3,2, Radius ×1,75), Rolle (Index/255, 0 = leer)   MASK_SIZE²
  <atlas>_skinmask_p.png  Tarnmuster (Noise-Wert, nur Gehäuse; großflächig)                              PATTERN_SIZE²
Polar (wear 0,6: k·m, k²·m²) und der Schmutz von Gebraucht (grime 2,2) sind linear in der Stärke (MapRange To Max/To Min).

UVs: aus dem FBX der Waffe übernommen (Teil für Teil, gleiche Schleifen), nicht neu abgewickelt – sieben Atlanten stammen aus älteren
Blender-Ständen. Prüfung vor dem Schreiben: Standard-Diffusfarbe in 512² backen und mit dem vorhandenen Atlas vergleichen (Inselinneres,
mittlere Abweichung ≤ 0,03, sonst Abbruch; verschobene UVs ergäben ein Vielfaches). Arme beim Backen wie beim Atlas der Waffe (export_unity.atlas_with_arms: vor 0.41 gebacken = mit Armen).
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
STATES = ('standard', 'nacht', 'gebraucht', 'tarnung')     # Material-Stände, in denen gebacken wird
MASK_SIZE = int(os.environ.get('BALLON_SKINMASK_SIZE', '2048'))   # Abrieb und Kratzer: 2048² reicht (Vergleich im Bericht 0.42)
PATTERN_SIZE = 2048                                               # harte Mustergrenzen: 1024² verschob sie sichtbar
CHECK_MAE = float(os.environ.get('BALLON_SKINMASK_MAE', '0.03'))


def chain(m):
    """Sockets der Mischkette im Material m (kit.aaa_nodes): {'m','g','s','pattern'} → Ausgangssocket (fehlt = Wert 0)."""
    from basic import kit
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    col = {'#9EA3A9': 'm', '#3B3329': 'g', '#A7ACB2': 's'}
    ref = {k: kit.hex_rgba(h) for h, k in col.items()}
    out = {}
    inp = b.inputs['Base Color']
    while inp.is_linked:
        n = inp.links[0].from_node
        if n.bl_idname == 'ShaderNodeMix' and n.data_type == 'RGBA':
            bv = tuple(n.inputs['B'].default_value)
            key = next((k for k, v in ref.items() if max(abs(a - c) for a, c in zip(bv, v)) < 1e-4), None)
            if key is None:
                raise RuntimeError(f'{m.name}: unbekannte Mischung {bv}')
            if n.inputs['Factor'].is_linked:
                out[key] = n.inputs['Factor'].links[0].from_socket
            inp = n.inputs['A']
        elif n.bl_idname == 'ShaderNodeValToRGB':              # Tarnmuster: Rampe über Noise
            out['pattern'] = n.inputs['Fac'].links[0].from_socket
            break
        else:
            raise RuntimeError(f'{m.name}: unerwarteter Knoten {n.bl_idname} vor der Grundfarbe')
    return out


def bake_rgb(obs, mats, image, values, samples=64, margin=8):
    """Emission (R, G, B) = values[material] (je Eintrag Socket oder Zahl) in image backen."""
    import bpy
    undo = []
    for m in mats:
        N, L = m.node_tree.nodes, m.node_tree.links
        tex = N.new('ShaderNodeTexImage')
        tex.image = image
        N.active = tex
        out = next(n for n in N if n.type == 'OUTPUT_MATERIAL' and n.is_active_output)
        old = out.inputs['Surface'].links[0].from_socket if out.inputs['Surface'].is_linked else None
        cc = N.new('ShaderNodeCombineColor')
        extra = []
        for i, v in enumerate(values[m]):
            if isinstance(v, (int, float)):
                cc.inputs[i].default_value = float(v)
            elif isinstance(v, tuple):                     # ('sq', Socket): Quadrat je Sample (E[m²])
                sq = N.new('ShaderNodeMath')
                sq.operation = 'MULTIPLY'
                L.new(v[1], sq.inputs[0])
                L.new(v[1], sq.inputs[1])
                L.new(sq.outputs[0], cc.inputs[i])
                extra.append(sq)
            else:
                L.new(v, cc.inputs[i])
        em = N.new('ShaderNodeEmission')
        L.new(cc.outputs['Color'], em.inputs['Color'])
        L.new(em.outputs['Emission'], out.inputs['Surface'])
        undo.append((m, tex, cc, em, out, old, extra))
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for ob in obs:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    sc = bpy.context.scene
    sc.cycles.samples = samples
    t0 = time.time()
    bpy.ops.object.bake(type='EMIT', margin=margin, use_clear=True)
    print(f'[skin_masks] {image.name}: {time.time() - t0:.0f} s', flush=True)
    for m, tex, cc, em, out, old, extra in undo:
        nt = m.node_tree
        for n in [tex, cc, em] + extra:
            nt.nodes.remove(n)
        if old is not None:
            nt.links.new(old, out.inputs['Surface'])


def copy_uvs(bake, fbx):
    """UVs der Teile aus dem FBX übernehmen (gleicher Name, gleiche Schleifenzahl); gibt die Zahl der Teile zurück."""
    import bpy
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=fbx)
    new = [o for o in bpy.data.objects if o not in before]
    src = {o.name.split('.')[0]: o for o in new if o.type == 'MESH'}
    n = 0
    for ob in bake:
        f = src.get(ob.name)
        if f is None or len(f.data.loops) != len(ob.data.loops) or not f.data.uv_layers:
            raise RuntimeError(f'{ob.name}: kein passendes Netz im FBX ({fbx})')
        if not ob.data.uv_layers:
            ob.data.uv_layers.new(name='UVMap')
        import numpy as np
        a = np.empty(len(f.data.loops) * 2, np.float32)
        f.data.uv_layers.active.data.foreach_get('uv', a)
        ob.data.uv_layers.active.data.foreach_set('uv', a)
        n += 1
    for o in new:
        bpy.data.objects.remove(o, do_unlink=True)
    return n


def check_alignment(obs, mats, albedo_path, size=512):
    """Standard-Diffusfarbe klein backen und mit dem vorhandenen Atlas vergleichen (sRGB 0–1, nur belegte Texel)."""
    import bpy
    import numpy as np
    from tools import bake_unity as BK
    im = BK._image('_skinmask_check', size, True)
    BK._bake(obs, mats, im, 'EMIT', 16, 'diffuse')
    a = np.empty(size * size * 4, np.float32)
    im.pixels.foreach_get(a)
    ref = bpy.data.images.load(albedo_path)
    ref.scale(size, size)
    r = np.empty(size * size * 4, np.float32)
    ref.pixels.foreach_get(r)
    dbg = os.environ.get('BALLON_SKINMASK_DEBUG')            # Ordner: Prüfbild und Atlas klein nebeneinander (Sichtprüfung)
    if dbg:
        _w = write_png
        os.makedirs(dbg, exist_ok=True)
        name = os.path.basename(albedo_path).split('.')[0]
        _w(os.path.join(dbg, f'{name}_bake.png'), a.reshape(size, size, 4)[::-1, :, :3])
        _w(os.path.join(dbg, f'{name}_atlas.png'), r.reshape(size, size, 4)[::-1, :, :3])
    a, r = a.reshape(-1, 4)[:, :3], r.reshape(-1, 4)[:, :3]
    used = (r.max(axis=1) > 0.02).reshape(size, size)
    for ax in (0, 1):                                         # nur Inselinneres: Ränder mischen beim Verkleinern mit dem Spalt
        for d in (-2, -1, 1, 2):
            used = used & np.roll(used, d, axis=ax)
    used = used.reshape(-1)
    mae = float(np.abs(a[used] - r[used]).mean())
    bpy.data.images.remove(im)
    bpy.data.images.remove(ref)
    return mae


def masks_for(module, e, tex_dir, gpu, arms):
    """Masken einer Waffe backen; gibt den Eintrag textures.skin_masks zurück."""
    import bpy
    import importlib
    import numpy as np
    from basic import kit
    from tools import ego_build as EB, bake_unity as BK, export_unity as EU
    W = importlib.import_module(f'basic.{module}')
    sc = EB.Scene(W, dict(stills=False, actions=[], gpu=False, samples=1, weapon=module, fx=False))
    EU.rest_pose(sc)
    root = sc.root
    wobs = [root] + list(root.children_recursive)
    meshes = [o for o in wobs if o.type == 'MESH']
    BK.apply_modifiers(meshes)
    BK.SKIP_ROLES |= BK._skip_roles()
    bake = [o for o in meshes if BK.bakeable(o)]
    n = copy_uvs(bake, os.path.join(EU.DST, e['weapon']['fbx']))
    hidden = [] if arms else [o for o in bpy.context.scene.objects if o.type == 'MESH' and o not in wobs and not o.hide_render]
    for o in hidden:
        o.hide_render = True
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    if gpu:
        pr = bpy.context.preferences.addons['cycles'].preferences
        pr.compute_device_type = 'METAL'
        pr.get_devices()
        for d in pr.devices:
            d.use = d.type == 'METAL'
        s.cycles.device = 'GPU'
    s.cycles.use_denoising = False
    if s.world:
        s.world.light_settings.distance = 0.03
    size = e['textures']['weapon']['size']
    atlas = e['atlas']
    albedo = os.path.join(tex_dir, e['textures']['weapon']['albedo'])
    roles = sorted({BK.role_of(o) for o in bake})
    idx = {r: (i + 1) / 255.0 for i, r in enumerate(roles)}
    planes = {}
    tmp = None
    ads = {sc.objs[p['id']].name for p in e['weapon']['parts'] if p['ads_hide'] and p['id'] in sc.objs}
    try:
        for state in STATES:
            kit.SKIN['name'] = state
            kit.set_mode(sc.objs, 'aaa')
            noads = BK.joined_without(bake, ads)           # 0.44.1: ads_hide-Teile verdecken nichts (wie bake_atlas)
            obs, tmp = BK._joined(bake)                    # je Stand neu: die Kopie übernimmt die Materialien beim Zusammenfügen
            mats = {sl.material for o in obs for sl in o.material_slots if sl.material}
            if state == 'standard':
                mae = check_alignment(obs, mats, albedo)
                print(f'[skin_masks] {e["id"]}: {n} Teile mit FBX-UVs, Deckung mit dem Atlas {mae:.4f} (≤ {CHECK_MAE})', flush=True)
                if mae > CHECK_MAE:
                    raise RuntimeError(f'{e["id"]}: Masken lägen nicht auf dem Atlas (Abweichung {mae:.3f})')
            ch = {m: chain(m) for m in mats}
            role = {m: idx[m['basic_role']] for m in mats}
            mm = lambda m: ch[m].get('m', 0.0)                                       # noqa: E731
            sq = lambda m: ('sq', ch[m]['m']) if 'm' in ch[m] else 0.0                 # noqa: E731
            pick = {'standard': lambda m: (mm(m), sq(m), ch[m].get('g', 0.0)),
                    'nacht': lambda m: (mm(m), sq(m), 0.0),
                    'gebraucht': lambda m: (mm(m), sq(m), role[m]),                    # B: Rolle (konstant je Material)
                    'tarnung': lambda m: (ch[m].get('pattern', 0.0), ch[m].get('s', 0.0), 0.0)}[state]
            im = BK._image(f'{atlas}_skinmask_{state}', size, False)
            vals = {m: pick(m) for m in mats}
            if noads is None:
                bake_rgb(obs, mats, im, vals)
            else:
                BK.bake_views(lambda o, i: bake_rgb(o, mats, i, vals), im, tmp, noads)
            BK.drop_view(noads)
            px = np.empty(size * size * 4, np.float32)
            im.pixels.foreach_get(px)
            planes[state] = px.reshape(size, size, 4)[::-1]          # Blender: Zeile 0 unten → Bild oben
            bpy.data.images.remove(im)
            unjoin(tmp)
            tmp = None
    finally:
        kit.SKIN['name'] = 'standard'
        kit.set_mode(sc.objs, 'aaa')
        for o in hidden:
            o.hide_render = False
        unjoin(tmp)
    st, na, ge, ta = (planes[k] for k in STATES)
    a = st[..., :3]
    b = np.stack([na[..., 0], na[..., 1], ta[..., 1]], -1)
    c = ge[..., :3]
    files = {}
    for key, arr, n in (('a', a, MASK_SIZE), ('b', b, MASK_SIZE), ('c', c, MASK_SIZE), ('p', ta[..., :1], PATTERN_SIZE)):
        name = f'{atlas}_skinmask_{key}.png'
        f = size // n
        if key == 'c' and f > 1:                           # Rolle: nächster Texel (Mittelwert mischte Indizes an Inselrändern)
            arr = np.concatenate([arr[:, :, :2].reshape(n, f, n, f, 2).mean((1, 3)), arr[f // 2::f, f // 2::f, 2:]], -1)
        elif f > 1:
            arr = arr.reshape(n, f, n, f, arr.shape[-1]).mean((1, 3))
        write_png(os.path.join(tex_dir, name), arr)
        files[key] = name
    return dict(files, roles=roles, size=MASK_SIZE, pattern_size=PATTERN_SIZE, arms=bool(arms),
                de='Skin-Masken (tools/skin_masks.py): a = E[m], E[m²] Standard, E[g]; b = E[m], E[m²] Nachtschicht, Kratzer s; '
                   'c = E[m], E[m²] Gebraucht, Rolle (Index/255 in roles, 0 = leer); p = Tarnmuster')


def unjoin(tmp):
    """Zusammengefügte Bake-Kopie entfernen und die Originale wieder rendern (wie bake_unity.bake_atlas beim Aufräumen)."""
    import bpy
    if tmp is None:
        return
    for nm in tmp.get('ballon_hidden', []):
        if nm in bpy.data.objects:
            bpy.data.objects[nm].hide_render = False
    bpy.data.objects.remove(tmp)


def write_png(path, arr):
    """Lineare Werte 0–1 als 8-bit-PNG (OpenImageIO, ohne Farbraumumrechnung)."""
    import numpy as np
    import OpenImageIO as oiio
    h, w, c = arr.shape
    out = oiio.ImageOutput.create(path)
    spec = oiio.ImageSpec(w, h, c, oiio.UINT8)
    spec.attribute('oiio:ColorSpace', 'Linear')
    spec.attribute('png:compressionLevel', 9)
    out.open(path, spec)
    out.write_image(np.clip(np.rint(arr * 255), 0, 255).astype(np.uint8))
    out.close()


def main():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    gpu = os.environ.get('BALLON_BAKE_GPU') == '1'
    from tools import export_unity as EU
    p = os.path.join(EU.DST, 'ego.json')
    D = json.load(open(p, encoding='utf-8'))
    tex_dir = os.path.join(EU.DST, 'Textures')
    want = [x for x in a if not x.startswith('-')]
    for m, e in zip(EU.WEAPONS, D['weapons']):
        if want and e['id'] not in want:
            continue
        e['textures']['skin_masks'] = masks_for(m, e, tex_dir, gpu, arms=EU.atlas_with_arms(e))
        EU.write_json(p, D)                                   # nach jeder Waffe: ein Abbruch verliert nur die laufende
        print(f'[skin_masks] {e["id"]}: {e["textures"]["skin_masks"]["a"]}, {e["textures"]["skin_masks"]["b"]}', flush=True)


if __name__ == '__main__':
    main()
