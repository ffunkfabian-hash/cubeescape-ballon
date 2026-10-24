"""Baut eine BASIC-Waffe in Blender, schreibt Modell, Spec und Ansichten.

  blender -b --factory-startup -P tools/blender_build.py -- w01_auto_rifle [--views] [--motion] [--samples 24]

Ausgabe (außerhalb des Repos, siehe tools/paths.py): <OUT>/<id>/
  <id>.blend, <id>.glb       Modell (Hierarchie Waffe → Baugruppe → Bauteil, Anker als Empties)
  <id>.spec.json             Maße, Bauteile, Anker, Bewegungen – gemessen am gebauten Modell
  views/*.png + views.json   Ansichten (transparent) und projizierte Beschriftungspunkte
  motion/<aktion>/####.png   Bildfolgen der Mechanik (--motion)
Der Rahmen ist der Formgen-/Toolgen-Rahmen: Meter, vorn −Y, oben +Z, links +X, Ursprung Socket_Hand.
"""
import importlib
import json
import math
import os
import sys

import bpy
from mathutils import Vector, Matrix, Euler
from bpy_extras.object_utils import world_to_camera_view

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic import kit  # noqa: E402
from tools.paths import OUT  # noqa: E402

# Autorenachse → (Blender-Index, Vorzeichen). Drehsinn siehe basic/kit.py: 'x' positiv = gegen den Uhrzeigersinn in der
# Seitenansicht (vorn rechts, oben oben; wie common.rot) = Blender −X; 'f' und 'u' Rechte-Hand-Regel um vorn (−Y) bzw. oben (+Z)
VDIR = 'views'
AXIS = {'x': (0, -1.0), 'f': (1, -1.0), 'u': (2, 1.0)}

# Explosionsversatz je Baugruppe (mm, f/u/x) – grafische Auseinanderziehung, kein Demontageweg
EXPLODE = {'sight': (0, 95, 0), 'ammo': (25, -120, 0), 'stock': (-90, 0, 0), 'barrel': (110, 0, 0),
           'support': (55, 0, 0), 'grip_controls': (-10, -70, 0), 'mechanism': (0, 0, 70), 'receiver': (0, 0, 0)}


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    o = dict(weapon=a[0], views='--views' in a, motion='--motion' in a, samples=24, res=1600, only=None, gpu='--gpu' in a,
             aaa='--aaa' in a, skins=[], bloom='--bloom' in a, bg='mid', tag='')
    if '--bg' in a:
        o['bg'] = a[a.index('--bg') + 1]
    if '--tag' in a:
        o['tag'] = a[a.index('--tag') + 1]
    if '--skins' in a:
        o['skins'] = a[a.index('--skins') + 1].split(',')
    if '--only' in a:
        o['only'] = set(a[a.index('--only') + 1].split(','))
    if '--samples' in a:
        o['samples'] = int(a[a.index('--samples') + 1])
    if '--res' in a:
        o['res'] = int(a[a.index('--res') + 1])
    return o


# ------------------------------------------------------------------ Bewegung

def move_matrix(ob, mv, t):
    """Weltmatrix eines Teils bei Anteil t (0..1) seiner eigenen Bewegung, ausgehend von der Ruhelage ob['rest']."""
    rest = Matrix(ob['rest'])
    k = mv['kind']
    if k == 'translate':
        return Matrix.Translation(kit.to_xyz(*mv['vector_mm']) * t) @ rest
    if k == 'rotate':
        i, s = AXIS[mv['axis']]
        a0, a1 = mv['range_deg']
        ax = Vector((0, 0, 0))
        ax[i] = 1
        piv = rest.translation.copy()
        return Matrix.Translation(piv) @ Matrix.Rotation(math.radians(a0 + (a1 - a0) * t) * s, 4, ax) @ \
            Matrix.Translation(-piv) @ rest
    if k == 'segment':   # Sehnenhälfte: ein Ende fest an der Wurfarmspitze, das andere folgt dem Nockpunkt
        tip, nock = kit.to_xyz(*mv['tip']), kit.to_xyz(*mv['nock'])
        d0 = nock - tip
        d1 = d0 + kit.to_xyz(*mv['vector_mm']) * t
        n = d0.normalized()
        kf = d1.length / d0.length
        S = Matrix.Identity(3) + (kf - 1) * Matrix([[n[i] * n[j] for j in range(3)] for i in range(3)])
        R = d0.rotation_difference(d1).to_matrix()
        return Matrix.Translation(tip) @ (R @ S).to_4x4() @ Matrix.Translation(-tip) @ rest
    if k == 'glow':
        return rest
    raise KeyError(k)


def apply_move(ob, mv, t, parent=None):
    M = move_matrix(ob, mv, t)
    if parent is not None:
        M = parent.matrix_world @ Matrix(parent['rest']).inverted() @ M
    ob.matrix_world = M
    if mv['kind'] == 'glow':   # aus = Graphit ohne Leuchten, an = Energie-Cyan mit voller Leuchtstärke
        n = ob.data.materials[0].node_tree.nodes['Principled BSDF']
        k = max(0.0, min(1.0, t))
        off, on = kit.hex_rgba(kit.MATERIALS['graphite']['color']), kit.hex_rgba(kit.MATERIALS['energy']['color'])
        n.inputs['Base Color'].default_value = [off[i] + (on[i] - off[i]) * k for i in range(4)]
        n.inputs['Emission Color'].default_value = on
        n.inputs['Emission Strength'].default_value = mv.get('max', 4.0) * k


def ease(a, b, x):
    x = max(0.0, min(1.0, (x - a) / (b - a))) if b > a else 1.0
    return x * x * (3 - 2 * x)


def value_at(keys, fr):
    if fr <= keys[0][0]:
        return keys[0][1]
    for (f0, v0), (f1, v1) in zip(keys, keys[1:]):
        if f0 <= fr <= f1:
            return v0 + (v1 - v0) * ease(f0, f1, fr)
    return keys[-1][1]


# ------------------------------------------------------------------ Messen

def mesh_stats(ob):
    import bmesh
    dg = bpy.context.evaluated_depsgraph_get()
    e = ob.evaluated_get(dg)
    me = e.to_mesh()
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.transform(e.matrix_world)
    tris = sum(len(f.verts) - 2 for f in bm.faces)
    vol = abs(bm.calc_volume(signed=False))
    lo = [min(v.co[i] for v in bm.verts) for i in range(3)]
    hi = [max(v.co[i] for v in bm.verts) for i in range(3)]
    cen = Vector((0, 0, 0))
    for v in bm.verts:
        cen += v.co
    cen /= max(1, len(bm.verts))
    bm.free()
    e.to_mesh_clear()
    return dict(tris=tris, volume_m3=vol, lo=lo, hi=hi, center=list(cen))


def r5(v):
    return [round(float(x), 5) for x in v]


def write_spec(W, objs, anchors, path):
    parts = []
    tot_tris, mass, msum = 0, 0.0, Vector((0, 0, 0))
    lo_all, hi_all = [1e9] * 3, [-1e9] * 3
    for p in W.PARTS:
        ob = objs[p['id']]
        st = mesh_stats(ob)
        tot_tris += st['tris']
        if p['mat'] != 'glass':
            mass += st['volume_m3']
            msum += Vector(st['center']) * st['volume_m3']
        lo_all = list(map(min, lo_all, st['lo']))
        hi_all = list(map(max, hi_all, st['hi']))
        mv = p.get('move')
        mvj = None
        if mv:
            mvj = dict(kind=mv['kind'], event=mv.get('event'), note=mv.get('note'),
                       pivot_m=r5(kit.to_xyz(*mv['pivot'])) if mv.get('pivot') else None)
            if mv['kind'] in ('translate', 'segment'):
                mvj['vector_m'] = r5(kit.to_xyz(*mv['vector_mm']))
                mvj['travel_mm'] = round(math.sqrt(sum(c * c for c in mv['vector_mm'])), 1)
                if mv['kind'] == 'segment':
                    mvj['tip_m'] = r5(kit.to_xyz(*mv['tip']))
                    mvj['nock_rest_m'] = r5(kit.to_xyz(*mv['nock']))
            elif mv['kind'] == 'glow':
                mvj['emission_max'] = mv.get('max', 4.0)
            else:
                i, s = AXIS[mv['axis']]
                mvj['axis_blender'] = 'XYZ'[i]
                mvj['axis_sign'] = s
                mvj['range_deg'] = list(mv['range_deg'])
        parts.append(dict(
            id=p['id'], name_de=p['de'], name_en=p['en'], assembly=p['asm'], function_de=p['func'],
            attachment_de=p['attach'], material_role=p['mat'], material_de=kit.MATERIALS[p['mat']]['de'],
            interface=p.get('iface'), parent_part=p.get('parent_part'), shape=p['shape'], bevel_mm=p.get('bevel', 1.0),
            blender_object=ob.name, origin_m=r5(ob.matrix_world.translation),
            bounds_m=dict(min=r5(st['lo']), max=r5(st['hi'])),
            size_mm=[round((st['hi'][i] - st['lo'][i]) * 1000, 1) for i in range(3)],
            triangles=st['tris'], volume_cm3=round(st['volume_m3'] * 1e6, 2), moving=mvj,
            removable=bool(p.get('removable') or (mv or {}).get('removable')),
        ))
    com = msum / mass if mass else Vector((0, 0, 0))
    an = {}
    for k, v in W.ANCHORS.items():
        an[k] = dict(position_m=r5(anchors[k].matrix_world.translation), part=v.get('part'), note=v.get('note'),
                     source='Modell (gesetzt im Entwurf)')
    an['Socket_CenterOfMass'] = dict(position_m=r5(com), part=None,
                                     note='abgeleitet: Volumenschwerpunkt, homogene Dichte, ohne Glas',
                                     source='abgeleitet aus dem Modellvolumen')
    spec = dict(
        format='cubeescape-ballon/basic-spec', format_version=1,
        generator=dict(repo='cubeescape-ballon', tool='tools/blender_build.py', blender=bpy.app.version_string),
        weapon=dict(W.META), units=dict(length='m', author_unit='mm'),
        axes=dict(forward='-Y', up='+Z', left='+X', origin='Socket_Hand', handedness='rechtshändig (Blender)'),
        assemblies=[dict(a, parts=[p['id'] for p in W.PARTS if p['asm'] == a['id']]) for a in W.ASSEMBLIES],
        parts=parts, anchors=an,
        dimensions=dict(bounds_m=dict(min=r5(lo_all), max=r5(hi_all)),
                        length_m=round(hi_all[1] - lo_all[1], 4), height_m=round(hi_all[2] - lo_all[2], 4),
                        width_m=round(hi_all[0] - lo_all[0], 4),
                        reference_length_m=W.META.get('reference_length_m'),
                        note='gemessen am gebauten Modell mit Bevel, Visier montiert, Ruhelage'),
        counts=dict(parts=len(parts), triangles=tot_tris, assemblies=len(W.ASSEMBLIES)),
        actions={k: dict(de=a['de'], frames=a['frames'], fps=30, parts=list(a['keys']), events=a.get('events', []),
                         status='Mechanik definiert; Bildfolge und Sichtung siehe data/review.json; Dauer entworfen')
                 for k, a in getattr(W, 'ACTIONS', {}).items()},
        interfaces=sorted({p['iface'] for p in W.PARTS if p.get('iface')}),
    )
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(spec, f, ensure_ascii=False, indent=1)
    return spec


# ------------------------------------------------------------------ Szene/Render

def setup_render(res, samples, aspect=(16, 9), gpu=False, aaa=False, bloom=False, bg='dark'):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    if gpu:   # nur mit heavy_lock --resource gpu starten
        pr = bpy.context.preferences.addons['cycles'].preferences
        pr.compute_device_type = 'METAL'
        pr.get_devices()
        for d in pr.devices:
            d.use = d.type == 'METAL'
        sc.cycles.device = 'GPU'
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.render.film_transparent = True
    sc.render.resolution_x = res
    sc.render.resolution_y = int(res * aspect[1] / aspect[0])
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    world = bpy.data.worlds.new('W')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.9, 0.9, 0.92, 1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.35
    sc.world = world
    for nm, loc, en, size in (('Key', (-1.2, -1.0, 1.6), 115, 1.6), ('Fill', (1.4, -0.6, 0.6), 35, 2.0),
                              ('Rim', (0.3, 1.6, 1.2), 70, 1.4)):
        L = bpy.data.lights.new(nm, 'AREA')
        L.energy = en
        L.size = size
        o = bpy.data.objects.new(nm, L)
        o.location = loc
        sc.collection.objects.link(o)
        o.rotation_euler = (Vector((0, -0.1, 0.1)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    if aaa:
        return setup_aaa(sc, bloom, bg)
    # Freestyle-Kontur (Illustrationsstil)
    sc.render.use_freestyle = True
    sc.render.line_thickness_mode = 'ABSOLUTE'
    sc.render.line_thickness = max(1.0, res / 600)
    vl = sc.view_layers[0]
    vl.use_freestyle = True
    fs = vl.freestyle_settings
    fs.crease_angle = math.radians(120)
    ls = fs.linesets[0] if fs.linesets else fs.linesets.new('L')
    ls.select_by_visibility = True
    ls.select_by_edge_types = True
    ls.select_silhouette = True
    ls.select_border = True
    ls.select_crease = True
    ls.select_material_boundary = True
    ls.select_external_contour = True
    if ls.linestyle is None:
        ls.linestyle = bpy.data.linestyles.new('BASIC_Line')
    ls.linestyle.color = (0.06, 0.06, 0.07)
    ls.linestyle.thickness = max(1.0, res / 600)
    return sc


# Hintergrund-Verläufe (unten → oben) und Umgebungslicht; Standard mittelgrau (Entscheidung des Nutzers 24.10.2026)
BACKDROPS = {'dark': ('#0C0E11', '#3A3F47', 0.35), 'mid': ('#4C525A', '#9EA4AC', 0.45), 'light': ('#B9BEC5', '#EEF0F2', 0.55)}


def setup_aaa(sc, bloom=False, bg='dark'):
    """Produktbild wie ein Inspektionsbildschirm: dunkler Verlauf, weiches Key, kräftiges Rim, AgX, ohne Kontur."""
    sc.render.use_freestyle = False
    sc.render.film_transparent = False
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    sc.cycles.samples = max(sc.cycles.samples, 96)
    w = sc.world
    nt = w.node_tree
    N, L = nt.nodes, nt.links
    tc = N.new('ShaderNodeTexCoord')
    sep = N.new('ShaderNodeSeparateXYZ')
    ramp = N.new('ShaderNodeValToRGB')
    lo, hi, amb_s = BACKDROPS[bg]
    ramp.color_ramp.elements[0].color = kit.hex_rgba(lo)
    ramp.color_ramp.elements[1].color = kit.hex_rgba(hi)
    ramp.color_ramp.elements[0].position = 0.05
    ramp.color_ramp.elements[1].position = 0.95
    L.new(tc.outputs['Window'], sep.inputs['Vector'])
    L.new(sep.outputs['Y'], ramp.inputs['Fac'])
    lp = N.new('ShaderNodeLightPath')
    mix = N.new('ShaderNodeMixShader')
    amb = N.new('ShaderNodeBackground')
    amb.inputs['Color'].default_value = kit.hex_rgba('#8C96A3')
    amb.inputs['Strength'].default_value = amb_s
    bg = N['Background']
    L.new(ramp.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = 1.0
    L.new(lp.outputs['Is Camera Ray'], mix.inputs['Fac'])
    L.new(amb.outputs['Background'], mix.inputs[1])
    L.new(bg.outputs['Background'], mix.inputs[2])
    L.new(mix.outputs['Shader'], N['World Output'].inputs['Surface'])
    if bloom:   # Standard: kein Glanzeffekt (Wunsch des Nutzers 24.10.2026); --bloom nur sehr dezent auf starker Emission
        try:   # Bloom nur auf Leuchtteilen, Blender-5-Compositor als Knotengruppe
            ng = bpy.data.node_groups.new('BASIC_Comp', 'CompositorNodeTree')
            ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
            rl, gl, out = ng.nodes.new('CompositorNodeRLayers'), ng.nodes.new('CompositorNodeGlare'), ng.nodes.new('NodeGroupOutput')
            gl.inputs['Type'].default_value = 'Bloom'
            gl.inputs['Threshold'].default_value = 8.0     # nur starke Emission
            gl.inputs['Strength'].default_value = 0.08
            gl.inputs['Size'].default_value = 0.25
            ng.links.new(rl.outputs['Image'], gl.inputs['Image'])
            ng.links.new(gl.outputs['Image'], out.inputs[0])
            sc.compositing_node_group = ng
        except Exception as e:   # ältere Blender-Versionen: ohne Bloom weiter
            print('[basic] Bloom nicht verfügbar:', e)
    for ob in [o for o in sc.objects if o.type == 'LIGHT']:
        bpy.data.objects.remove(ob)
    for nm, loc, en, size, colr in (('Key', (-0.9, -0.9, 1.3), 170, 1.2, '#FFF4E6'), ('Fill', (1.2, -0.5, 0.2), 40, 2.5, '#DCE6F2'),
                                    ('Rim', (0.6, 1.4, 0.9), 320, 0.9, '#E8F1FF'), ('Top', (0.0, 0.0, 1.8), 60, 3.0, '#FFFFFF')):
        Lt = bpy.data.lights.new(nm, 'AREA')
        Lt.energy = en
        Lt.size = size
        Lt.color = kit.hex_rgba(colr)[:3]
        lo = bpy.data.objects.new(nm, Lt)
        lo.location = loc
        sc.collection.objects.link(lo)
        lo.rotation_euler = (Vector((0, -0.1, 0.1)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return sc


def camera(name='Cam'):
    c = bpy.data.cameras.new(name)
    c.type = 'ORTHO'
    o = bpy.data.objects.new(name, c)
    bpy.context.scene.collection.objects.link(o)
    bpy.context.scene.camera = o
    return o


VIEWS = {   # Blickrichtung (von der Waffe zur Kamera), Hochachse
    'hero': ((-0.78, -0.50, 0.42), (0, 0, 1)),
    'side': ((-1, 0, 0), (0, 0, 1)),          # rechte Seite, Mündung rechts
    'side_left': ((1, 0, 0), (0, 0, 1)),
    'top': ((0, 0, 1), (-1, 0, 0)),
    'front': ((0, -1, 0), (0, 0, 1)),
    'rear': ((0, 1, 0.02), (0, 0, 1)),
    'ego': ((0.42, 0.86, 0.36), (0, 0, 1)),     # von links hinten oben: Seite, die im Ego-Bild sichtbar ist
}


def aim(cam, d, up, pts, margin=1.10):
    d = Vector(d).normalized()
    cen = sum(pts, Vector()) / len(pts)
    rot = d.to_track_quat('Z', 'Y')
    # Hochachse ausrichten
    m = Matrix.Identity(3)
    z = d
    x = Vector(up).cross(z).normalized() if abs(Vector(up).normalized().dot(z)) < 0.99 else Vector((1, 0, 0))
    y = z.cross(x)
    m = Matrix((x, y, z)).transposed()
    cam.matrix_world = Matrix.Translation(cen + d * 3.0) @ m.to_4x4()
    bpy.context.view_layer.update()
    inv = cam.matrix_world.inverted()
    loc = [inv @ p for p in pts]
    w = max(p.x for p in loc) - min(p.x for p in loc)
    h = max(p.y for p in loc) - min(p.y for p in loc)
    sc = bpy.context.scene
    asp = sc.render.resolution_x / sc.render.resolution_y
    cam.data.ortho_scale = max(w, h * asp) * margin
    mx = (max(p.x for p in loc) + min(p.x for p in loc)) / 2
    my = (max(p.y for p in loc) + min(p.y for p in loc)) / 2
    cam.matrix_world = cam.matrix_world @ Matrix.Translation((mx, my, 0))
    cam.data.clip_end = 10


def bbox_pts(obs):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for ob in obs:
        e = ob.evaluated_get(dg)
        pts += [e.matrix_world @ Vector(c) for c in e.bound_box]
    return pts


def project(cam, p):
    sc = bpy.context.scene
    v = world_to_camera_view(sc, cam, p)
    return [round(v.x * sc.render.resolution_x, 1), round((1 - v.y) * sc.render.resolution_y, 1)]


def render(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def labels(cam, objs, anchors, W):
    out = dict(parts={}, assemblies={}, anchors={})
    for pid, ob in objs.items():
        pts = bbox_pts([ob])
        out['parts'][pid] = project(cam, sum(pts, Vector()) / len(pts))
    for a in W.ASSEMBLIES:
        obs = [objs[p['id']] for p in W.PARTS if p['asm'] == a['id'] and p['id'] in objs]
        if obs:
            pts = bbox_pts(obs)
            out['assemblies'][a['id']] = project(cam, sum(pts, Vector()) / len(pts))
    for k, e in anchors.items():
        out['anchors'][k] = project(cam, e.matrix_world.translation)
    return out


def set_visible(objs, keep):
    for pid, ob in objs.items():
        ob.hide_render = pid not in keep


def main():
    o = args()
    W = importlib.import_module(f'basic.{o["weapon"]}' if '.' in o['weapon'] else f'basic.weapons.{o["weapon"]}')
    wid = W.META['id'] + (f"-{W.META['variant']}" if W.META.get('variant') else '')
    base_mode = 'aaa' if o['aaa'] else 'color'
    global VDIR
    VDIR = 'views' + (f"_{o['tag']}" if o['tag'] else '')   # --tag: Vergleichsläufe in eigenem Ordner
    out = os.path.join(OUT, wid)
    os.makedirs(os.path.join(out, VDIR), exist_ok=True)
    kit.reset_scene()
    root, objs, anchors = kit.build(W)
    bpy.context.view_layer.update()
    for ob in objs.values():
        ob['rest'] = [list(r) for r in ob.matrix_world]
    spec = write_spec(W, objs, anchors, os.path.join(out, f'{wid}.spec.json'))
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, f'{wid}.blend'))
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, f'{wid}.glb'), export_apply=True, export_extras=True)
    print(f'[basic] {wid}: {spec["counts"]} Länge {spec["dimensions"]["length_m"]} m')
    if not (o['views'] or o['motion']):
        return
    setup_render(o['res'], o['samples'], gpu=o['gpu'], aaa=o['aaa'], bloom=o['bloom'], bg=o['bg'])
    if o['aaa']:
        kit.set_mode(objs, 'aaa')
    cam = camera()
    allp = list(objs.values())
    meta = dict(resolution=[bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y], views={})
    sight_ids = [p['id'] for p in W.PARTS if p['asm'] == 'sight']
    if o['views']:
        base = bbox_pts(allp)
        want = (lambda v: o['only'] is None or v in o['only'])
        if hasattr(W, 'HERO'):
            VIEWS['hero'] = (W.HERO, (0, 0, 1))
        for v, (d, up) in VIEWS.items():
            if not want(v):
                continue
            aim(cam, d, up, base)
            render(os.path.join(out, VDIR, f'{v}.png'))
            meta['views'][v] = dict(labels=labels(cam, objs, anchors, W), ortho_scale=cam.data.ortho_scale)
        if o['aaa'] and want('hero_p'):   # Produktfoto: Perspektive 70 mm aus der Hauptrichtung
            pc = bpy.data.cameras.new('Persp')
            pc.lens = 70
            pc.sensor_width = 36
            po = bpy.data.objects.new('Persp', pc)
            bpy.context.scene.collection.objects.link(po)
            dvec = Vector(W.HERO if hasattr(W, 'HERO') else VIEWS['hero'][0]).normalized()
            cen = sum(base, Vector()) / len(base)
            rad = max((p - cen).length for p in base)
            dist = rad / math.tan(math.atan(18 / 70)) * 1.02
            po.matrix_world = Matrix.Translation(cen + dvec * dist) @ (-dvec).to_track_quat('-Z', 'Y').to_matrix().to_4x4()
            po.data.clip_end = 20
            bpy.context.scene.camera = po
            render(os.path.join(out, VDIR, 'hero_p.png'))
            meta['views']['hero_p'] = dict(labels=labels(po, objs, anchors, W), lens_mm=70)
            bpy.context.scene.camera = cam
        # Visierlinie: Perspektive aus Socket_Eye entlang der Laufachse (prüft freie Durchsicht)
        if 'Socket_Eye' in anchors and want('sightline'):
            pc = bpy.data.cameras.new('Eye')
            pc.lens = 50
            pc.sensor_width = 36
            pc.clip_start = 0.005
            eo = bpy.data.objects.new('Eye', pc)
            bpy.context.scene.collection.objects.link(eo)
            std = W.ANCHORS.get('Socket_Eye', {}).get('std')        # Visier-Standard: Socket_Eye ist die echte Augenposition
            eye_off = 0.0 if std else 0.09
            eye = anchors['Socket_Eye'].matrix_world.translation + Vector((0, eye_off, 0))
            eo.matrix_world = Matrix.Translation(eye) @ Vector((0, -1, 0)).to_track_quat('-Z', 'Y').to_matrix().to_4x4()
            bpy.context.scene.camera = eo
            hid = [objs[p['id']] for p in W.PARTS if p.get('ads_hide') and p['id'] in objs]   # Visier-Standard: beim Zielen aus
            for ob in hid:
                ob.hide_render = True
            render(os.path.join(out, VDIR, 'sightline.png'))
            for ob in hid:
                ob.hide_render = False
            meta['views']['sightline'] = dict(labels=labels(eo, objs, anchors, W), eye_offset_m=eye_off,
                                              note='Perspektive 50 mm, Kamera im Augenpunkt (Visier-Standard)' if std else
                                              'Perspektive 50 mm, Kamera 90 mm hinter Socket_Eye auf der Visierlinie')
            bpy.context.scene.camera = cam
        if o['only'] is not None and not o['only'] & {'clay', 'silhouette', 'exploded', 'parts'}:
            o['views'] = False
    if o['views']:
        # neutral grau und Silhouette
        kit.set_mode(objs, 'clay')
        aim(cam, *VIEWS['hero'], base)
        render(os.path.join(out, VDIR, 'clay.png'))
        meta['views']['clay'] = dict(labels=labels(cam, objs, anchors, W), ortho_scale=cam.data.ortho_scale)
        kit.set_mode(objs, 'black')
        bpy.context.scene.render.use_freestyle = False
        if o['aaa']:
            bpy.context.scene.render.film_transparent = True
        for L in [ob for ob in bpy.context.scene.objects if ob.type == 'LIGHT']:
            L.hide_render = True
        aim(cam, *VIEWS['side'], base)
        render(os.path.join(out, VDIR, 'silhouette.png'))
        meta['views']['silhouette'] = dict(ortho_scale=cam.data.ortho_scale)
        for L in [ob for ob in bpy.context.scene.objects if ob.type == 'LIGHT']:
            L.hide_render = False
        if o['aaa']:
            bpy.context.scene.render.film_transparent = False
        bpy.context.scene.render.use_freestyle = not o['aaa']
        kit.set_mode(objs, base_mode)
        # Explosionsansicht
        exp = dict(EXPLODE, **getattr(W, 'EXPLODE', {}))
        for p in W.PARTS:
            if p.get('parent_part'):
                continue
            ob = objs[p['id']]
            off = exp.get(p['id'], exp.get(p['asm'], (0, 0, 0)))
            ob.matrix_world = Matrix.Translation(kit.to_xyz(*off)) @ Matrix(ob['rest'])
        bpy.context.view_layer.update()
        aim(cam, *VIEWS['hero'], bbox_pts(allp), margin=1.16)
        render(os.path.join(out, VDIR, 'exploded.png'))
        meta['views']['exploded'] = dict(labels=labels(cam, objs, anchors, W), ortho_scale=cam.data.ortho_scale,
                                         offsets_mm={k: list(v) for k, v in exp.items()})
        for ob in allp:
            ob.matrix_world = Matrix(ob['rest'])
        bpy.context.view_layer.update()
        # Einzelteile: Magazin und Visier (identische Objekte, nur andere Teile ausgeblendet)
        groups = {'part_sight': sight_ids,
                  'part_ammo': [p['id'] for p in W.PARTS if p['asm'] == 'ammo']}
        for g, ids in groups.items():
            if not ids:
                continue
            set_visible(objs, set(ids))
            aim(cam, (-0.8, -0.45, 0.4), (0, 0, 1), bbox_pts([objs[i] for i in ids]), margin=1.25)
            bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y = 900, 700
            render(os.path.join(out, VDIR, f'{g}.png'))
            meta['views'][g] = dict(labels=labels(cam, {i: objs[i] for i in ids}, {}, W), ortho_scale=cam.data.ortho_scale,
                                    resolution=[900, 700])
            bpy.context.scene.render.resolution_x = o['res']
            bpy.context.scene.render.resolution_y = int(o['res'] * 9 / 16)
        set_visible(objs, set(objs))
    if o['motion']:
        sc = bpy.context.scene
        sc.render.resolution_x, sc.render.resolution_y = 854, 480
        sc.cycles.samples = max(8, o['samples'] // 3)
        sc.render.use_freestyle = False   # Bildfolgen ohne Kontur: Freestyle kostet je Bild mehrere Sekunden CPU
        for k, A in getattr(W, 'ACTIONS', {}).items():
            # Kamera so, dass die bewegten Teile sichtbar sind: Waffe von rechts vorn; Auswurf rechts
            moving = [objs[p] for p in A['keys']]
            aim(cam, A.get('view', (-0.85, -0.25, 0.45)), (0, 0, 1), bbox_pts(allp), margin=1.08)
            d = os.path.join(out, 'motion', k)
            os.makedirs(d, exist_ok=True)
            step = A.get('step', 2)
            byid = {x['id']: x for x in W.PARTS}
            order = sorted(A['keys'], key=lambda pid: 1 if byid[pid].get('parent_part') else 0)
            for fr in range(0, A['frames'] + 1, step):
                for pid in order:
                    p = byid[pid]
                    mv = p['move']
                    par = objs[p['parent_part']] if p.get('parent_part') else None
                    apply_move(objs[pid], mv, value_at(A['keys'][pid], fr), par)
                bpy.context.view_layer.update()
                render(os.path.join(d, f'{fr:04d}.png'))
            for ob in allp:
                ob.matrix_world = Matrix(ob['rest'])
        meta['motion_resolution'] = [854, 480]
    vj = os.path.join(out, VDIR, 'views.json')
    if os.path.exists(vj):   # zusammenführen: ein Lauf mit nur --motion oder --only behält die übrigen Ansichten
        old = json.load(open(vj, encoding='utf-8'))
        old['views'].update(meta['views'])
        meta = dict(old, **{k: v for k, v in meta.items() if k != 'views'}, views=old['views'])
    with open(vj, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    if o['aaa'] and o['skins']:   # Farb-/Texturvarianten: gleiche Form, Hauptansicht und Linke Seite je Skin
        sc = bpy.context.scene
        sc.render.resolution_x, sc.render.resolution_y = o['res'], int(o['res'] * 9 / 16)
        sc.cycles.samples = max(96, o['samples'])
        for ob in allp:
            ob.matrix_world = Matrix(ob['rest'])
        for s in o['skins']:
            kit.SKIN['name'] = s
            kit.set_mode(objs, 'aaa')
            for v in ('hero', 'side_left'):
                aim(cam, *VIEWS[v], bbox_pts(allp))
                render(os.path.join(out, VDIR, f'skin_{s}_{v}.png'))
        kit.SKIN['name'] = 'standard'


if __name__ == '__main__':
    main()
