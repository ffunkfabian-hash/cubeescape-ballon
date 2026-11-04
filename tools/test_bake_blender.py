"""Backen im Kleinen (0.43 „Kiln“, Blender, CPU, 64²): zusammengefügte Kopie trägt Objektkoordinaten und Teil, Materialien nach dem Backen unverändert, Datenkarten ohne
Ansichtstransformation, Spec und AO in data_size.

  ~/Claude/cubeescape-nexogen/ce lock blender -- blender -b --factory-startup -P <abs>/tools/test_bake_blender.py
"""
import importlib
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import bpy  # noqa: E402
import numpy as np  # noqa: E402
from basic import kit  # noqa: E402
import tools.blender_build as BB  # noqa: E402
import tools.bake_unity as BK  # noqa: E402

bad = []


def ok(c, what):
    print(('  ✓ ' if c else '  ✗ ') + what, flush=True)
    if not c:
        bad.append(what)


def links(mats):
    return {m.name: sorted((l.from_node.bl_idname, l.from_socket.name, l.to_node.bl_idname, l.to_socket.name) for l in m.node_tree.links) for m in mats}


def main():
    t = tempfile.mkdtemp(prefix='kiln-')
    os.environ['BASIC_OUT'] = t
    W = importlib.import_module('basic.pilot.w05_sidearm_v21')
    kit.reset_scene()
    root, objs, _ = kit.build(W)
    bpy.context.view_layer.update()
    BB.setup_render(854, 1, gpu=False, aaa=True, bloom=False, bg='mid')
    kit.set_mode(objs, 'aaa')
    meshes = [o for o in [root] + list(root.children_recursive) if o.type == 'MESH']
    BK.apply_modifiers(meshes)
    bake = [o for o in meshes if BK.bakeable(o)]
    BK.unwrap(bake)
    moved = [o for o in bake if max(abs(v) for v in o.matrix_world.translation) > 1e-6]
    ok(len(moved) > 0 and len(moved) < len(bake), f'Prüfwaffe hat verschobene Teile ({len(moved)} von {len(bake)})')

    # zusammengefügte Kopie
    obs, tmp = BK._joined(bake)
    ok(obs == [tmp], 'ein Backobjekt')
    me = tmp.data
    n = len(me.vertices)
    ok(n == sum(len(o.data.vertices) for o in bake), 'alle Punkte in der Kopie')
    co = np.empty(n * 3, np.float32)
    me.attributes[BK.CO_ATTR].data.foreach_get('vector', co)
    part = np.empty(n, np.int32)
    me.attributes[BK.PART_ATTR].data.foreach_get('value', part)
    co = co.reshape(-1, 3)
    pos = np.empty(n * 3, np.float32)
    me.vertices.foreach_get('co', pos)
    pos = pos.reshape(-1, 3)
    ok(len(set(part.tolist())) == len(bake), 'Teile-ID je Punkt')
    i = bake.index(moved[0])
    mine = part == i
    off = np.array(moved[0].matrix_world.translation, np.float32)
    ok(np.abs(pos[mine] - co[mine] - off).max() < 1e-5, 'verschobenes Teil: Attribut = alter Objektraum, Lage = Waffenraum')
    ok(all(o.hide_render for o in bake), 'Originale beim Backen verborgen')
    mats = {s.material for s in tmp.material_slots if s.material}
    before = links(mats)
    undo = BK._object_coords(mats)
    ok(len(undo) > 0 and links(mats) != before, 'Muster hängen am Attribut')
    BK.restore_coords(undo)
    ok(links(mats) == before, 'Rückweg Objektkoordinaten')
    for nm in tmp['ballon_hidden']:
        bpy.data.objects[nm].hide_render = False
    bpy.data.objects.remove(tmp)

    # ganzer Atlas
    allm = {o.data.materials[0] for o in bake}
    before = links(allm)
    res = BK.bake_atlas(bake, 'k', 128, t, settings=dict(data_size=64, normal_size=256, rand_samples=2, emit_samples=1, ao_samples=2))
    ok(links(allm) == before, 'Materialien nach dem Backen unverändert')
    ok(not any(o.hide_render for o in bake), 'Originale wieder sichtbar')
    ok(not any(n.startswith('k_rand') for n in bpy.data.images.keys()) and 'k_rough' not in bpy.data.images, 'keine Zwischenbilder')
    size = {}
    for k, f in res.items():
        im = bpy.data.images.load(os.path.join(t, f))
        size[k] = im.size[0]
        bpy.data.images.remove(im)
    ok(size == dict(albedo=128, spec=64, normal=256, ao=64), f'Kantenlängen {size}')

    # Datenkarten: keine Ansichtstransformation beim Speichern, auch unter AgX
    sc = bpy.context.scene
    vt, lk = sc.view_settings.view_transform, sc.view_settings.look
    sc.view_settings.view_transform, sc.view_settings.look = 'AgX', 'AgX - Medium High Contrast'
    im = BK._image('t', 16, False)
    ok(im.colorspace_settings.name == 'Non-Color', 'Datenbild Non-Color')
    px = np.tile(np.array([0.5, 0.25, 0.75, 1], np.float32), 256)
    im.pixels.foreach_set(px)
    sc.render.image_settings.file_format, sc.render.image_settings.color_depth, sc.render.image_settings.color_mode = 'PNG', '16', 'RGB'
    p = os.path.join(t, 't.png')
    im.save_render(p, scene=sc)
    r = bpy.data.images.load(p)
    r.colorspace_settings.name = 'Non-Color'
    q = np.empty(1024, np.float32)
    r.pixels.foreach_get(q)
    ok(np.abs(q[:3] - px[:3]).max() < 1e-3, f'Non-Color unter AgX unverändert ({q[:3]})')
    sc.view_settings.view_transform, sc.view_settings.look = vt, lk
    print(f'Backen im Kleinen: {len(bad)} Fehler' if bad else 'Backen im Kleinen geprüft', flush=True)
    sys.exit(1 if bad else 0)


main()
