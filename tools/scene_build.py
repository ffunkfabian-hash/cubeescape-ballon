"""Hintergrundszenen bauen und backen (0.9 „Parcours“), Format `ballon-scene/2` (docs/szenen-format.md).

  BALLON_BAKE_GPU=1 ce lock gpu -- blender -b --factory-startup -P <abs>/tools/scene_build.py -- hangar
        → unity/Assets/Ballon/Generated/Scenes/hangar/{hangar.fbx, hangar_<licht>_<zone>.png, scene_hangar.json}
          ~/Library/Caches/CubeEscapeBallon/unity/scenes/hangar_<licht>_ref.png (Vergleichsrender vom Startpunkt), …_atlas_view.png,
          hangar_plan.png (Draufsicht mit Strecke), hangar_albedo_<zone>.png, decals/, hangar_build.{blend,json} (nicht im Repo)
  python3 tools/scene_build.py --check   → jede Szene in basic/scenes/ hat aktuelle Dateien (ohne Blender, Teil von ./check)

Ablauf in Blender: Bauteile aus `basic/scenes/<name>.py` je Gruppe zu einem Netz (Weltlage im Netz, Objekte im Ursprung), jedes
Bauteil gefast (bmesh.ops.bevel), Trapezblech als Profil; Bildmasken (Markierungen, Flecken, Schilder) aus DECALS gerastert;
Umgebungsmaterialien mit Kantenabrieb (Bevel-Knoten), Schmutz (AO), Laufspuren, Mustern im Weltraum; Lightmap-UVs je Zone
(Smart UV, gleiche Texeldichte, gepackt); je Zone einmal die Grundfarbe backen (teure Knoten nur hier), danach je Lichtszene
und Zone das diffuse Licht (direkt + indirekt, mal Grundfarbe, dazu Leuchtflächen; ohne Glanz) aus einer zusammengefügten Kopie;
Panorama am Startpunkt misst das Umgebungslicht; Vergleichsrender und Atlasansicht je Lichtszene; FBX wie tools/export_unity.py.
Testläufe: BALLON_SCENE_TEST=1 (Atlanten ¼, wenige Samples), BALLON_SCENE_LIGHTS=tag,nacht → Ausgabe nur in den Cache.
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

FORMAT = 'ballon-scene/2'
DST = os.path.join(ROOT, 'unity', 'Assets', 'Ballon', 'Generated', 'Scenes')
CACHE = os.path.expanduser('~/Library/Caches/CubeEscapeBallon/unity/scenes')


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
        if p['mesh'] and p['group'] not in out:
            out.append(p['group'])
    return out


def zone_groups(S, z):
    g = groups(S)
    return [x for x in z['groups'] if x in g]


def atlas_name(S, L, z):
    return f"{S.META['name']}_{L['name']}_{z['name']}.png"


def light_json(lt):
    return dict(name=lt['name'], kind=lt['kind'], pos=r6(lt['pos']), dir=r6(lt['dir']), power_w=r6(lt['power_w']), size_m=r6(lt['size_m']),
                angle_deg=r6(lt.get('angle_deg', 90.0) if lt['kind'] == 'spot' else 0.0), color=lt['color'])


def data(S):
    """Szenendatei ohne Blender; gemessene Felder (zones[].texel_m, lightings[].ambient) bleiben None."""
    name = S.META['name']
    cols = []
    for p in S.PARTS:
        if not p['collide']:
            continue
        lo, hi = SC.bounds(p)
        cols.append(dict(name=p['id'], center=r6([(a + b) / 2 for a, b in zip(lo, hi)]), size=r6([b - a for a, b in zip(lo, hi)])))
    sp = S.SPAWN['pos']
    R = S.REFERENCE
    C = S.COURSE
    _, st = SC.course_check(S)
    box_ = lambda b: dict(center=r6(b['center']), size=r6(b['size']))    # noqa: E731
    return dict(
        format=FORMAT, name=name, de=S.META['de'], fbx=f'{name}.fbx',
        zones=[dict(name=z['name'], objects=zone_groups(S, z), size=int(z['size']), texel_m=None) for z in S.ZONES],
        objects=groups(S), colliders=cols,
        spawn=dict(pos=r6(sp), yaw_deg=r6(S.SPAWN['yaw_deg'])),
        lightings=[dict(name=L['name'], de=L['de'], atlases={z['name']: atlas_name(S, L, z) for z in S.ZONES}, scale=r6(L['scale']),
                        sky=dict(color=L['sky']['color'], strength=r6(L['sky']['strength'])), ambient=None,
                        lights=[light_json(lt) for lt in L['lights']],
                        reference=dict(png=f"{name}_{L['name']}_ref.png", camera_pos=r6((sp[0], sp[1], sp[2] + R['eye_m'])),
                                       yaw_deg=r6(S.SPAWN['yaw_deg']), pitch_deg=0.0, h_fov_deg=r6(R['h_fov_deg'])))
                   for L in S.LIGHTINGS],
        course=dict(start=box_(C['start']), finish=box_(C['finish']),
                    checkpoints=[dict(name=c['name'], center=r6(c['center']), size=r6(c['size'])) for c in C['checkpoints']],
                    targets=[dict(name=t['name'], pos=r6(t['pos']), normal=r6(t['normal']), radius=r6(t['radius'])) for t in C['targets']],
                    route=[r6(r[:3]) for r in C['route']],
                    par_time_s=r6(SC.par_time(S, st)[1])),
        targets=[],
        sources=sources(name))


def strip_measured(d):
    d = json.loads(json.dumps(d, ensure_ascii=False))
    for z in d.get('zones', []):
        z.pop('texel_m', None)
    for L in d.get('lightings', []):
        L.pop('ambient', None)
    return d


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
        if cur.get('format') != FORMAT:
            bad.append(f'{name}: Format {cur.get("format")} statt {FORMAT}: Szene neu bauen')
            continue
        new, old = strip_measured(data(S)), strip_measured(cur)
        diff = [k for k in new if old.get(k) != new[k]]
        if diff:
            bad.append(f'{name}: scene_{name}.json veraltet ({", ".join(diff)}): Szene neu bauen')
        for L in cur.get('lightings', []):
            if not L.get('ambient'):
                bad.append(f'{name}/{L["name"]}: ambient fehlt')
        for z in cur.get('zones', []):
            if not z.get('texel_m'):
                bad.append(f'{name}/{z["name"]}: texel_m fehlt')
        files = [cur.get('fbx')] + [f for L in cur.get('lightings', []) for f in L.get('atlases', {}).values()]
        for f in files:
            if not f or not os.path.exists(os.path.join(d, f)):
                bad.append(f'{name}: {f} fehlt')
    if bad:
        print(' | '.join(bad))
        return 1
    print(f'szenen: {", ".join(scene_names())} aktuell')
    return 0


# ------------------------------------------------------------------ Blender-Teil
T_LOG = {}


def log(msg, t0=None, key=None):
    if key and t0 is not None:
        T_LOG[key] = round(time.time() - t0, 1)
    print(f'[scene_build] {msg}' + (f' ({time.time() - t0:.1f} s)' if t0 is not None else ''), flush=True)


def hex_lin(h):
    from basic.kit import hex_rgba
    return hex_rgba(h)


def hex_srgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


# ---------------------------------------------------------- Bildmasken (numpy)
def _vnoise(h, w, cell, rng):
    """Wertrauschen (glatt) h × w, Zellgröße in Pixeln."""
    import numpy as np
    cell = max(1.0, cell)
    gh, gw = int(h / cell) + 3, int(w / cell) + 3
    G = rng.random((gh, gw)).astype(np.float32)
    ys, xs = np.arange(h) / cell, np.arange(w) / cell
    iy, ix = ys.astype(int), xs.astype(int)
    ty, tx = ys - iy, xs - ix
    ty, tx = ty * ty * (3 - 2 * ty), tx * tx * (3 - 2 * tx)
    a = G[iy][:, ix] * (1 - tx) + G[iy][:, ix + 1] * tx
    b = G[iy + 1][:, ix] * (1 - tx) + G[iy + 1][:, ix + 1] * tx
    return (a * (1 - ty)[:, None] + b * ty[:, None]).astype(np.float32)


class Sheet:
    """Rasterbild eines DECALS-Blatts (u nach rechts, v nach oben, Zeile 0 = unten wie Blender)."""

    def __init__(self, D):
        import numpy as np
        self.np = np
        self.px = D['px_m']
        W, H = D['size']
        self.w, self.h = max(2, round(W / self.px)), max(2, round(H / self.px))
        self.rgb = np.zeros((self.h, self.w, 3), np.float32)
        self.A = np.zeros((self.h, self.w), np.float32)
        if D.get('bg'):
            self.rgb[:] = hex_srgb(D['bg'])
            self.A[:] = 1.0
        for it in D['items']:
            getattr(self, 'd_' + it['kind'])(it)

    def win(self, u0, v0, u1, v1, pad=0.0):
        px = self.px
        x0, x1 = max(0, int(math.floor((u0 - pad) / px))), min(self.w, int(math.ceil((u1 + pad) / px)) + 1)
        y0, y1 = max(0, int(math.floor((v0 - pad) / px))), min(self.h, int(math.ceil((v1 + pad) / px)) + 1)
        if x1 <= x0 or y1 <= y0:
            return None
        np = self.np
        U = (np.arange(x0, x1) + 0.5) * px
        V = (np.arange(y0, y1) + 0.5) * px
        return x0, x1, y0, y1, U, V

    def over(self, w, cov, color):
        x0, x1, y0, y1 = w[:4]
        np = self.np
        c = np.asarray(color, np.float32)
        A = self.A[y0:y1, x0:x1]
        rgb = self.rgb[y0:y1, x0:x1]
        out = cov + A * (1 - cov)
        num = (c if c.ndim == 3 else c[None, None, :]) * cov[..., None] + rgb * (A * (1 - cov))[..., None]
        self.rgb[y0:y1, x0:x1] = np.where(out[..., None] > 1e-6, num / np.maximum(out, 1e-6)[..., None], rgb)
        self.A[y0:y1, x0:x1] = out

    def _box_cov(self, U, V, a, b):
        np = self.np
        px = self.px
        cu = np.clip((np.minimum(b[0], U + px / 2) - np.maximum(a[0], U - px / 2)) / px, 0, 1)
        cv = np.clip((np.minimum(b[1], V + px / 2) - np.maximum(a[1], V - px / 2)) / px, 0, 1)
        return cv[:, None] * cu[None, :]

    def _seg_cov(self, U, V, segs, hw):
        np = self.np
        X, Y = np.meshgrid(U, V)
        d = np.full(X.shape, 1e9, np.float32)
        for (ax, ay), (bx, by) in segs:
            dx, dy = bx - ax, by - ay
            L2 = dx * dx + dy * dy
            t = np.clip(((X - ax) * dx + (Y - ay) * dy) / L2, 0, 1) if L2 > 1e-12 else 0.0
            d = np.minimum(d, np.hypot(X - (ax + t * dx), Y - (ay + t * dy)))
        return np.clip((hw - d) / self.px + 0.5, 0, 1)

    def _segs_bbox(self, segs, pad):
        us = [p[0] for s in segs for p in s]
        vs = [p[1] for s in segs for p in s]
        return self.win(min(us), min(vs), max(us), max(vs), pad)

    def d_rect(self, it):
        w = self.win(*it['a'], *it['b'])
        if w:
            self.over(w, self._box_cov(w[4], w[5], it['a'], it['b']) * it.get('alpha', 1.0), hex_srgb(it['color']))

    def d_frame(self, it):
        (u0, v0), (u1, v1), t = it['a'], it['b'], it['w']
        w = self.win(u0, v0, u1, v1)
        if not w:
            return
        np = self.np
        c = np.zeros((len(w[5]), len(w[4])), np.float32)
        for a, b in (((u0, v0), (u1, v0 + t)), ((u0, v1 - t), (u1, v1)), ((u0, v0), (u0 + t, v1)), ((u1 - t, v0), (u1, v1))):
            c = np.maximum(c, self._box_cov(w[4], w[5], a, b))
        self.over(w, c, hex_srgb(it['color']))

    def _ss(self, U, V, fn):
        """Mittel über 3 × 3 Unterabtastungen einer Funktion fn(X, Y) → 0/1."""
        np = self.np
        acc = 0.0
        for oy in (-1 / 3, 0, 1 / 3):
            for ox in (-1 / 3, 0, 1 / 3):
                X, Y = np.meshgrid(U + ox * self.px, V + oy * self.px)
                acc = acc + fn(X, Y).astype(np.float32)
        return acc / 9.0

    def d_hatch(self, it):
        w = self.win(*it['a'], *it['b'])
        if not w:
            return
        np = self.np
        k = math.sqrt(2) * 2 * it['stripe_m']
        f = self._ss(w[4], w[5], lambda X, Y: ((X + Y) / k) % 1.0 < 0.5)
        c1, c2 = np.array(hex_srgb(it['c1']), np.float32), np.array(hex_srgb(it['c2']), np.float32)
        col = c1[None, None, :] * f[..., None] + c2[None, None, :] * (1 - f[..., None])
        self.over(w, self._box_cov(w[4], w[5], it['a'], it['b']), col)

    def d_checker(self, it):
        w = self.win(*it['a'], *it['b'])
        if not w:
            return
        np = self.np
        c, (u0, v0) = it['cell'], it['a']
        f = self._ss(w[4], w[5], lambda X, Y: (np.floor((X - u0) / c) + np.floor((Y - v0) / c)) % 2 < 0.5)
        c1, c2 = np.array(hex_srgb(it['c1']), np.float32), np.array(hex_srgb(it['c2']), np.float32)
        col = c1[None, None, :] * f[..., None] + c2[None, None, :] * (1 - f[..., None])
        self.over(w, self._box_cov(w[4], w[5], it['a'], it['b']), col)

    def _lines(self, lines, hw, color, alpha=1.0):
        segs = [(a, b) for ln in lines for a, b in zip(ln, ln[1:])]
        if not segs:
            return
        w = self._segs_bbox(segs, hw + 2 * self.px)
        if w:
            self.over(w, self._seg_cov(w[4], w[5], segs, hw) * alpha, hex_srgb(color))

    def d_text(self, it):
        self._lines(SC.text_strokes(it['s'], it['h'], it['at'][0], it['at'][1], it.get('align', 'left')), it['w'] * it['h'] / 2, it['color'])

    def d_line(self, it):
        self._lines([it['pts']], it['w'] / 2, it['color'], it.get('alpha', 1.0))

    def d_ring(self, it):
        (cu, cv), r, hw = it['c'], it['r'], it['w'] / 2
        w = self.win(cu - r, cv - r, cu + r, cv + r, hw + 2 * self.px)
        if w:
            np = self.np
            X, Y = np.meshgrid(w[4], w[5])
            d = np.abs(np.hypot(X - cu, Y - cv) - r)
            self.over(w, np.clip((hw - d) / self.px + 0.5, 0, 1), hex_srgb(it['color']))

    def d_disc(self, it):
        (cu, cv), r = it['c'], it['r']
        w = self.win(cu - r, cv - r, cu + r, cv + r, 2 * self.px)
        if w:
            np = self.np
            X, Y = np.meshgrid(w[4], w[5])
            self.over(w, np.clip((r - np.hypot(X - cu, Y - cv)) / self.px + 0.5, 0, 1) * it.get('alpha', 1.0), hex_srgb(it['color']))

    def d_poly(self, it):
        pts = it['pts']
        us, vs = [p[0] for p in pts], [p[1] for p in pts]
        w = self.win(min(us), min(vs), max(us), max(vs), self.px)
        if not w:
            return
        np = self.np

        def inside(X, Y):
            m = np.zeros(X.shape, bool)
            for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):
                c = ((ay > Y) != (by > Y)) & (X < (bx - ax) * (Y - ay) / ((by - ay) + 1e-12) + ax)
                m ^= c
            return m
        self.over(w, self._ss(w[4], w[5], inside), hex_srgb(it['color']))

    def d_stain(self, it):
        (cu, cv), r = it['c'], it['r']
        w = self.win(cu - 1.6 * r, cv - 1.6 * r, cu + 1.6 * r, cv + 1.6 * r)
        if not w:
            return
        np = self.np
        rng = np.random.default_rng(it.get('seed', 0))
        h_, w_ = len(w[5]), len(w[4])
        n1 = _vnoise(h_, w_, r / 2.5 / self.px, rng)
        n2 = _vnoise(h_, w_, r / 8 / self.px, rng)
        X, Y = np.meshgrid(w[4], w[5])
        d = np.hypot(X - cu, Y - cv) / (r * (0.75 + 0.5 * n1))
        m = np.clip((1.0 - d) / 0.6, 0, 1)
        m = m * m * (3 - 2 * m)
        rim = np.clip(1.0 - np.abs(d - 0.82) / 0.12, 0, 1) * 0.35        # Ölflecken: dunklerer Rand
        self.over(w, np.clip(m * (0.75 + 0.25 * n2) + rim * (d < 1.0), 0, 1) * it['alpha'], hex_srgb(it['color']))

    def d_track(self, it):
        np = self.np
        pts, g = it['pts'], it['gap'] / 2
        for side in (-1, 1):
            off = []
            for i, p in enumerate(pts):
                a, b = pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)]
                dx, dy = b[0] - a[0], b[1] - a[1]
                L = math.hypot(dx, dy) or 1.0
                off.append((p[0] - dy / L * g * side, p[1] + dx / L * g * side))
            segs = list(zip(off, off[1:]))
            w = self._segs_bbox(segs, it['w'] + 2 * self.px)
            if not w:
                continue
            rng = np.random.default_rng(it.get('seed', 0) + side)
            n = _vnoise(len(w[5]), len(w[4]), 0.5 / self.px, rng)
            cov = self._seg_cov(w[4], w[5], segs, it['w'] / 2) * np.clip((n - 0.2) / 0.5, 0, 1)
            self.over(w, cov * it['alpha'], hex_srgb(it['color']))


def decal_images(S, out_dir):
    """Alle Blätter rastern, als PNG speichern (Cache) und als Blender-Bilder laden."""
    import bpy
    import numpy as np
    t0 = time.time()
    os.makedirs(out_dir, exist_ok=True)
    ims = {}
    for nm, D in S.DECALS.items():
        sh = Sheet(D)
        px = np.concatenate([sh.rgb, sh.A[..., None]], axis=2).astype(np.float32)
        im = bpy.data.images.new(f'DECAL_{nm}', sh.w, sh.h, alpha=True)
        im.colorspace_settings.name = 'sRGB'
        im.pixels.foreach_set(px.ravel())
        p = os.path.join(out_dir, f'{nm}.png')
        im.filepath_raw = p
        im.file_format = 'PNG'
        im.save()
        ims[nm] = im
    log(f'Bildmasken: {len(ims)} Blätter gerastert', t0, 'decals')
    return ims


# ---------------------------------------------------------- Materialien
class NB:
    """Kleine Hilfe für Knotenbäume: Eingänge sind Zahlen, Tupel oder Ausgänge."""

    def __init__(self, nt):
        self.N, self.L = nt.nodes, nt.links

    def _in(self, sock, v):
        if v is None:
            return
        if isinstance(v, (int, float)) or isinstance(v, tuple):
            sock.default_value = v
        else:
            self.L.new(v, sock)

    def m(self, op, a, b=None, c=None):
        n = self.N.new('ShaderNodeMath')
        n.operation = op
        for i, v in enumerate((a, b, c)):
            self._in(n.inputs[i], v)
        return n.outputs[0]

    def v(self, op, a, b, out=0):
        n = self.N.new('ShaderNodeVectorMath')
        n.operation = op
        self._in(n.inputs[0], a)
        self._in(n.inputs[1], b)
        return n.outputs[out]

    def mr(self, v, f0, f1, t0, t1):
        n = self.N.new('ShaderNodeMapRange')
        n.inputs['From Min'].default_value = f0
        n.inputs['From Max'].default_value = f1
        n.inputs['To Min'].default_value = t0
        n.inputs['To Max'].default_value = t1
        self._in(n.inputs['Value'], v)
        return n.outputs['Result']

    def mix(self, fac, a, b, blend='MIX'):
        n = self.N.new('ShaderNodeMix')
        n.data_type = 'RGBA'
        n.blend_type = blend
        self._in(n.inputs[0], fac)
        self._in(n.inputs[6], a)
        self._in(n.inputs[7], b)
        return n.outputs[2]

    def noise(self, vec, scale, detail=2.0, rough=0.5):
        n = self.N.new('ShaderNodeTexNoise')
        n.inputs['Scale'].default_value = scale
        n.inputs['Detail'].default_value = detail
        n.inputs['Roughness'].default_value = rough
        self._in(n.inputs['Vector'], vec)
        return n.outputs['Fac']

    def sep(self, vec):
        n = self.N.new('ShaderNodeSeparateXYZ')
        self._in(n.inputs[0], vec)
        return n.outputs

    def scaled(self, vec, s):
        n = self.N.new('ShaderNodeMapping')
        n.inputs['Scale'].default_value = s
        self._in(n.inputs['Vector'], vec)
        return n.outputs['Vector']


def material_full(role, R, decals, S):
    """Grundfarbe für das Albedo-Backen: Muster, Bildmaske, Kantenabrieb (Bevel), Schmutz (AO), Spritzschmutz, Laufspuren."""
    import bpy
    m = bpy.data.materials.new(f'ENV_{role}')
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    B = NB(nt)
    b.inputs['Roughness'].default_value = R['rough']
    b.inputs['Metallic'].default_value = 0.0
    b.inputs['Specular IOR Level'].default_value = R.get('spec', 0.5)
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    pos = geo.outputs['Position']
    col = hex_lin(R['color'])
    pat = R.get('pattern')
    if pat == 'stripes':
        x, y, z = B.sep(pos)[:3]
        ph = B.m('FRACT', B.m('DIVIDE', B.m('ADD', B.m('ADD', x, y), z), math.sqrt(2) * 2 * R['stripe_m']))
        col = B.mix(B.m('LESS_THAN', ph, 0.5), hex_lin(R['color2']), col)
    elif pat == 'grid':
        x, y, z = B.sep(pos)[:3]
        c = R['cell_m']
        bx = B.m('LESS_THAN', B.m('FRACT', B.m('DIVIDE', x, c)), 0.3)
        by = B.m('LESS_THAN', B.m('FRACT', B.m('DIVIDE', y, c)), 0.3)
        col = B.mix(B.m('MAXIMUM', bx, by), hex_lin(R['color2']), col)
    if R.get('vary'):
        f = B.noise(pos, 1.0 / R.get('vary_m', 2.0), 4.0, 0.55)
        col = B.mix(1.0, col, B.mr(f, 0.3, 0.7, 1.0 - R['vary'], 1.0 + R['vary'] * 0.5), 'MULTIPLY')
        b_r = B.mr(f, 0.0, 1.0, R['rough'] * 0.85, min(1.0, R['rough'] * 1.12))
        nt.links.new(b_r, b.inputs['Roughness'])
    if pat == 'joints':
        x, y = B.sep(pos)[:2]
        J = R.get('joint_m', 6.0)
        ds = [B.m('MULTIPLY', B.m('ABSOLUTE', B.m('SUBTRACT', B.m('FRACT', B.m('ADD', B.m('DIVIDE', o, J), 0.5)), 0.5)), J) for o in (x, y)]
        d = B.m('MINIMUM', ds[0], ds[1])
        sp = B.mr(B.noise(pos, 3.0, 2.0), 0.3, 0.7, 0.7, 1.4)                     # Kantenausbrüche: Fugenbreite schwankt
        col = B.mix(1.0, col, B.mr(B.m('DIVIDE', d, sp), 0.006, 0.022, 0.42, 1.0), 'MULTIPLY')
    if pat == 'vjoints':
        x, y = B.sep(pos)[:2]
        J = R['panel_m']
        d = B.m('MULTIPLY', B.m('ABSOLUTE', B.m('SUBTRACT', B.m('FRACT', B.m('ADD', B.m('DIVIDE', B.m('ADD', x, y), J), 0.5)), 0.5)), J)
        col = B.mix(1.0, col, B.mr(d, 0.005, 0.016, 0.45, 1.0), 'MULTIPLY')
    if R.get('mottle'):                      # großflächige Verschmutzung (Wolken, Maßstab mottle_m)
        f = B.noise(pos, 1.0 / R.get('mottle_m', 8.0), 3.0, 0.5)
        col = B.mix(1.0, col, B.mr(f, 0.38, 0.72, 1.0, 1.0 - R['mottle']), 'MULTIPLY')
    if R.get('streaks'):                     # Laufspuren: senkrecht gestrecktes Rauschen
        f = B.noise(B.scaled(pos, (7.0, 7.0, 0.35)), 1.0, 3.0, 0.6)
        col = B.mix(1.0, col, B.mr(f, 0.55, 0.78, 1.0, 1.0 - R['streaks']), 'MULTIPLY')
    dn = R.get('decal')
    if dn:
        D = S.DECALS[dn]
        o, U, V = D['origin'], D['u'], D['v']
        Nn = (U[1] * V[2] - U[2] * V[1], U[2] * V[0] - U[0] * V[2], U[0] * V[1] - U[1] * V[0])
        dv = B.v('SUBTRACT', pos, tuple(float(x) for x in o))
        uu = B.m('DIVIDE', B.v('DOT_PRODUCT', dv, tuple(float(x) for x in U), 1), D['size'][0])
        vv = B.m('DIVIDE', B.v('DOT_PRODUCT', dv, tuple(float(x) for x in V), 1), D['size'][1])
        ww = B.m('LESS_THAN', B.m('ABSOLUTE', B.v('DOT_PRODUCT', dv, tuple(float(x) for x in Nn), 1)), D.get('depth', 0.05))
        cx = nt.nodes.new('ShaderNodeCombineXYZ')
        nt.links.new(uu, cx.inputs[0])
        nt.links.new(vv, cx.inputs[1])
        tx = nt.nodes.new('ShaderNodeTexImage')
        tx.image = decals[dn]
        tx.extension = 'CLIP'
        tx.interpolation = 'Linear'
        nt.links.new(cx.outputs[0], tx.inputs['Vector'])
        col = B.mix(B.m('MULTIPLY', tx.outputs['Alpha'], ww), col, tx.outputs['Color'])
    if R.get('wear'):                        # Kantenabrieb: Abweichung echte ↔ gerundete Normale, gebrochen durch Rauschen
        bev = nt.nodes.new('ShaderNodeBevel')
        bev.samples = 8
        bev.inputs['Radius'].default_value = R.get('wear_r', 0.05)        # größer als die Fase (≤ 2 cm), sonst keine Kante
        dot = B.v('DOT_PRODUCT', bev.outputs['Normal'], geo.outputs['Normal'], 1)
        edge = B.mr(dot, 0.92, 0.995, 1.0, 0.0)
        brk = B.noise(pos, 7.0, 8.0, 0.62)
        mask = B.mr(B.m('MULTIPLY', edge, brk), 0.22, 0.36, 0.0, R['wear'])
        col = B.mix(mask, col, hex_lin(R.get('wear_color', '#9EA3A9')))
    if R.get('grime'):                       # Schmutz in Ecken und Vertiefungen (AO)
        ao = nt.nodes.new('ShaderNodeAmbientOcclusion')
        ao.samples = 8
        ao.inputs['Distance'].default_value = R.get('grime_d', 0.35)
        g = B.mr(ao.outputs['AO'], 0.35, 0.92, R['grime'], 0.0)
        g = B.m('MULTIPLY', g, B.mr(B.noise(pos, 1.3, 3.0), 0.3, 0.7, 0.55, 1.25))
        col = B.mix(B.m('MINIMUM', g, 0.9), col, hex_lin('#3B3329'))
    if R.get('foot'):                        # Spritzschmutz am Fuß
        z = B.sep(pos)[2]
        g = B.m('MULTIPLY', B.mr(z, 0.0, R['foot'], 0.35, 0.0), B.mr(B.noise(pos, 4.0, 4.0), 0.3, 0.7, 0.4, 1.3))
        col = B.mix(g, col, hex_lin('#3E372E'))
    if isinstance(col, tuple):
        b.inputs['Base Color'].default_value = col
    else:
        nt.links.new(col, b.inputs['Base Color'])
    m.diffuse_color = hex_lin(R['color'])
    m['scene_role'] = role
    return m


def material_light(role, R, zone, albedo):
    """Lichtszenen: Grundfarbe aus dem Albedo-Atlas der Zone (UV), Leuchten = Albedo × Stärke der Lichtszene."""
    import bpy
    m = bpy.data.materials.new(f'L_{zone}_{role}')
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = R['rough']
    b.inputs['Metallic'].default_value = 0.0
    b.inputs['Specular IOR Level'].default_value = R.get('spec', 0.5)
    uv = nt.nodes.new('ShaderNodeUVMap')
    uv.uv_map = 'UVMap'
    tx = nt.nodes.new('ShaderNodeTexImage')
    tx.image = albedo
    tx.interpolation = 'Linear'
    tx.name = 'ALBEDO'
    nt.links.new(uv.outputs['UV'], tx.inputs['Vector'])
    nt.links.new(tx.outputs['Color'], b.inputs['Base Color'])
    nt.links.new(tx.outputs['Color'], b.inputs['Emission Color'])
    b.inputs['Emission Strength'].default_value = 0.0
    m['scene_role'] = role
    return m


# ---------------------------------------------------------- Geometrie
def _box_faces(a, b, skip):
    (x0, y0, z0), (x1, y1, z1) = a, b
    V = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    F = {'-z': (0, 3, 2, 1), '+z': (4, 5, 6, 7), '-y': (0, 1, 5, 4), '+y': (2, 3, 7, 6), '-x': (3, 0, 4, 7), '+x': (1, 2, 6, 5)}
    sk = set(skip)
    if abs(z0) < 1e-4:                     # Unterseite auf dem Boden: unsichtbar
        sk.add('-z')
    return V, [f for k, f in F.items() if k not in sk]


def part_mesh(p):
    """Bauteil als (Ecken, Flächen, glatt je Fläche) in Weltlage, gefast."""
    import bmesh
    from mathutils import Vector
    s = p['shape']
    smooth_axis = None
    if s == 'corr':
        prof = SC.corr_profile(p['u0'], p['u1'], p['prof'])
        n, u, v = SC.AX[p['n']], SC.AX[p['u']], SC.AX[p['v']]
        V = []
        for uu, dd in prof:
            for vv in (p['v0'], p['v1']):
                q = [0.0] * 3
                q[n] = p['at'] - p['side'] * dd
                q[u] = uu
                q[v] = vv
                V.append(tuple(q))
        F = []
        for i in range(len(prof) - 1):
            f = (2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1)
            pa, pb, pc = (Vector(V[k]) for k in f[:3])
            nrm = (pb - pa).cross(pc - pa)
            if nrm[n] * p['side'] < 0:
                f = tuple(reversed(f))
            F.append(f)
        return V, F, [False] * len(F)
    if s == 'box':
        V, F = _box_faces(p['a'], p['b'], p['skip'])
        cen = Vector([(x + y) / 2 for x, y in zip(p['a'], p['b'])])
    elif s == 'beam':
        V = SC.beam_frame(p['a'], p['b'], p['w'], p['h'])
        F = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        if not p.get('ends', True):
            F = F[2:]
        cen = Vector([(x + y) / 2 for x, y in zip(p['a'], p['b'])])
    elif s == 'cyl':
        i = SC.AX[p['axis']]
        j, k = [q for q in range(3) if q != i]
        n = p['segs']
        V = []
        for e in (-0.5, 0.5):
            for t in range(n):
                a = 2 * math.pi * (t + 0.5) / n
                q = list(p['c'])
                q[i] += e * p['l']
                q[j] += p['r'] * math.cos(a)
                q[k] += p['r'] * math.sin(a)
                V.append(tuple(q))
        F = [(t, (t + 1) % n, n + (t + 1) % n, n + t) for t in range(n)]
        cp = p.get('caps', 'both')
        if p['axis'] == 'z' and abs(p['c'][2] - p['l'] / 2) < 1e-4:          # steht auf dem Boden
            cp = {'both': 'top', 'bottom': 'none'}.get(cp, cp)
        if cp in ('both', 'bottom'):
            F.append(tuple(range(n)))
        if cp in ('both', 'top'):
            F.append(tuple(range(2 * n - 1, n - 1, -1)))
        cen = Vector(p['c'])
        smooth_axis = i
    else:
        raise ValueError(s)
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in V]
    for f in F:
        face = bm.faces.new([vs[q] for q in f])
        face.normal_update()
        if face.normal.dot(face.calc_center_median() - cen) < 0:
            face.normal_flip()
    bm.normal_update()
    w = SC.bevel_of(p)
    if w > 0:
        edges = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0.0) > math.radians(40)]
        if edges:
            bmesh.ops.bevel(bm, geom=edges, offset=w, offset_type='OFFSET', segments=1, profile=0.5, affect='EDGES', clamp_overlap=True)
    bm.normal_update()
    V = [tuple(v.co) for v in bm.verts]
    idx = {v: i for i, v in enumerate(bm.verts)}
    F, SM = [], []
    for f in bm.faces:
        F.append(tuple(idx[v] for v in f.verts))
        SM.append(smooth_axis is not None and abs(f.normal[smooth_axis]) < 0.2 and len(f.verts) == 4)
    bm.free()
    return V, F, SM


def build(S, mats):
    import bpy
    t0 = time.time()
    objs = []
    for g in groups(S):
        parts = [p for p in S.PARTS if p['mesh'] and p['group'] == g]
        roles = []
        for p in parts:
            if p['mat'] not in roles:
                roles.append(p['mat'])
        V, F, MI, SM = [], [], [], []
        for p in parts:
            v, f, sm = part_mesh(p)
            o = len(V)
            V += v
            F += [tuple(q + o for q in face) for face in f]
            MI += [roles.index(p['mat'])] * len(f)
            SM += sm
        me = bpy.data.meshes.new(g)
        me.from_pydata(V, [], F)
        me.polygons.foreach_set('material_index', MI)
        me.polygons.foreach_set('use_smooth', SM)
        me.update()
        for r in roles:
            me.materials.append(mats[r])
        ob = bpy.data.objects.new(g, me)
        bpy.context.scene.collection.objects.link(ob)
        objs.append(ob)
    tris = sum(len(f.vertices) - 2 for o in objs for f in o.data.polygons)
    log(f'gebaut: {len(objs)} Objekte, {sum(1 for p in S.PARTS if p["mesh"])} Bauteile, {tris} Dreiecke', t0, 'build')
    return objs, tris


def set_lighting(S, L):
    """Lichter und Himmel einer Lichtszene setzen, Leuchtstärken in die Lichtmaterialien schreiben."""
    import bpy
    from mathutils import Vector
    sc = bpy.context.scene
    for o in list(sc.objects):
        if o.type == 'LIGHT':
            bpy.data.objects.remove(o)
    for lt in L['lights']:
        k = lt['kind']
        if k == 'area':
            ld = bpy.data.lights.new(lt['name'], 'AREA')
            ld.size = lt['size_m']
        elif k == 'sun':
            ld = bpy.data.lights.new(lt['name'], 'SUN')
            ld.angle = math.radians(lt.get('blender_angle_deg', 1.0))
        elif k == 'spot':
            ld = bpy.data.lights.new(lt['name'], 'SPOT')
            ld.shadow_soft_size = lt['size_m']
            ld.spot_size = math.radians(lt.get('angle_deg', 90.0))
        else:
            ld = bpy.data.lights.new(lt['name'], 'POINT')
            ld.shadow_soft_size = lt['size_m']
        ld.energy = lt['power_w']
        ld.color = hex_lin(lt['color'])[:3]
        lo = bpy.data.objects.new(lt['name'], ld)
        lo.location = lt['pos']
        lo.rotation_euler = Vector(lt['dir']).to_track_quat('-Z', 'Y').to_euler()
        lo.visible_camera = False
        sc.collection.objects.link(lo)
    w = sc.world or bpy.data.worlds.new('Sky')
    w.use_nodes = True
    bg = w.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = hex_lin(L['sky']['color'])
    bg.inputs['Strength'].default_value = L['sky']['strength']
    sc.world = w
    em = L.get('emit', {})
    for m in bpy.data.materials:
        if m.name.startswith('L_') and 'scene_role' in m:
            m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = em.get(m['scene_role'], 0.0)


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


def unwrap(objs, size, pack_px, zone):
    """Lightmap-UVs einer Zone: Smart UV, Inseln auf gleiche Texeldichte, gepackt (Abstand pack_px Texel)."""
    import bpy
    t0 = time.time()
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for ob in objs:
        if not ob.data.uv_layers:
            ob.data.uv_layers.new(name='UVMap')
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    ang = float(os.environ.get('BALLON_SCENE_UV_ANGLE', '66'))
    bpy.ops.uv.smart_project(angle_limit=math.radians(ang), island_margin=0.0, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
    bpy.ops.uv.average_islands_scale()
    bpy.ops.uv.pack_islands(rotate=True, margin_method='FRACTION', margin=pack_px / size, shape_method='AABB')
    bpy.ops.object.mode_set(mode='OBJECT')
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
    log(f'Zone {zone}: {len(objs)} Objekte, {a3:.0f} m², Atlas {size}² belegt {auv * 100:.1f} %, {dens:.1f} Texel/m '
        f'({100 / dens:.2f} cm je Texel)', t0, f'uv_{zone}')
    return dict(area_m2=a3, uv_fill=auv, texel_per_m=dens)


def _bake_zones(zobjs, sizes, samples, kind, margin, tag):
    """Backt alle Zonen in einem Aufruf (eine Szenenübergabe an Cycles statt einer je Zone): je Zone eine zusammengefügte
    Kopie mit eigenen Zonenmaterialien und eigenem Zielbild, die Originale aus dem Render. Gibt ({Zone: Bild}, Sekunden)."""
    import bpy
    from tools import bake_unity as BK
    ims, added, copies, joins = {}, [], [], []
    for zn, objs in zobjs.items():
        work, joined = BK._joined(objs, join_all=True)
        j = work[0]
        if joined is not None:
            joins.append(joined)
            for o in objs:
                o.hide_render = True
        j.hide_render = False
        copies.append(j)
        im = BK._image(f'BAKE_{tag}_{zn}', sizes[zn], srgb=False)
        im.colorspace_settings.name = 'Linear Rec.709'
        ims[zn] = im
        for m in {s.material for s in j.material_slots if s.material}:
            tex = m.node_tree.nodes.new('ShaderNodeTexImage')
            tex.image = im
            m.node_tree.nodes.active = tex
            added.append((m, tex))
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for j in copies:
        j.select_set(True)
    bpy.context.view_layer.objects.active = copies[0]
    sc = bpy.context.scene
    sc.cycles.samples = samples
    rb = sc.render.bake
    rb.margin = margin
    rb.margin_type = 'EXTEND'
    rb.use_clear = True
    t1 = time.time()
    if kind == 'albedo':
        bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, margin=margin, use_clear=True)
    elif kind == 'normal':
        bpy.ops.object.bake(type='NORMAL', normal_space='OBJECT', margin=margin, use_clear=True)   # Objektraum = Welt (Objekte im Ursprung)
    else:
        bpy.ops.object.bake(type='COMBINED', pass_filter={'EMIT', 'DIRECT', 'INDIRECT', 'DIFFUSE'}, margin=margin, use_clear=True)
    tb = time.time() - t1
    for m, tex in added:
        m.node_tree.nodes.remove(tex)
    for j in joins:
        bpy.data.objects.remove(j)
    for objs in zobjs.values():
        for o in objs:
            o.hide_render = False
    return ims, tb


class Denoiser:
    """OIDN über den Kompositor (eigene leere Szene): Atlas mit Albedo- und Normalen-Führung entrauschen."""

    def __init__(self, cache):
        import bpy
        self.path = os.path.join(cache, '_denoise.exr')
        sc = bpy.data.scenes.new('Denoise')
        sc.render.engine = 'CYCLES'
        sc.cycles.samples = 1
        sc.cycles.device = 'CPU'
        sc.render.resolution_percentage = 100
        sc.view_settings.view_transform = 'Standard'
        sc.view_settings.look = 'None'
        sc.render.image_settings.file_format = 'OPEN_EXR'
        sc.render.image_settings.color_depth = '32'
        sc.render.filepath = self.path
        sc.world = bpy.data.worlds.new('DenoiseWorld')
        ng = bpy.data.node_groups.new('BALLON_Denoise', 'CompositorNodeTree')
        ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
        N = ng.nodes
        self.src, self.alb, self.nrm = (N.new('CompositorNodeImage') for _ in range(3))
        d = N.new('CompositorNodeDenoise')
        d.inputs['HDR'].default_value = True
        out = N.new('NodeGroupOutput')
        ng.links.new(self.src.outputs['Image'], d.inputs['Image'])
        ng.links.new(self.alb.outputs['Image'], d.inputs['Albedo'])
        ng.links.new(self.nrm.outputs['Image'], d.inputs['Normal'])
        ng.links.new(d.outputs[0], out.inputs[0])
        sc.compositing_node_group = ng
        self.sc = sc

    def __call__(self, im, albedo, normal, size):
        import bpy
        import numpy as np
        self.src.image, self.alb.image, self.nrm.image = im, albedo, normal
        self.sc.render.resolution_x = self.sc.render.resolution_y = size
        bpy.ops.render.render(write_still=True, scene=self.sc.name)
        r = bpy.data.images.load(self.path, check_existing=False)
        px = np.empty(size * size * 4, np.float32)
        r.pixels.foreach_get(px)
        bpy.data.images.remove(r)
        im.pixels.foreach_set(px)
        return im


def _save_srgb(im, size, path, k=1.0, dither=True):
    """Float-Bild (linear) → sRGB 8 bit PNG (Wert / k, Dreiecks-Dither). Gibt (Höchstwert, Anteil über k) zurück."""
    import bpy
    import numpy as np
    px = np.empty(size * size * 4, np.float32)
    im.pixels.foreach_get(px)
    rgb = px.reshape(-1, 4)[:, :3]
    vmax = float(rgb.max())
    clip = float((rgb.max(axis=1) > k).mean())
    lin = np.clip(rgb / k, 0.0, 1.0)
    s = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * np.power(lin, 1 / 2.4) - 0.055)
    if dither:
        rng = np.random.default_rng(1)
        s = s + (rng.random(s.shape, dtype=np.float32) - rng.random(s.shape, dtype=np.float32)) / 255.0
    s = np.clip(np.round(s * 255.0) / 255.0, 0.0, 1.0)
    out = np.ones((size * size, 4), np.float32)
    out[:, :3] = s
    ob = bpy.data.images.new(os.path.basename(path)[:-4], size, size, alpha=False)
    ob.colorspace_settings.name = 'sRGB'
    ob.pixels.foreach_set(out.ravel())
    ob.filepath_raw = path
    ob.file_format = 'PNG'
    ob.save()
    bpy.data.images.remove(ob)
    return vmax, clip


def measure_ambient(S, out_dir, tag):
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
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 256, 128, 100
    sc.cycles.samples = 64
    sc.cycles.use_denoising = False
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = 'OPEN_EXR'
    sc.render.image_settings.color_depth = '32'
    p = os.path.join(out_dir, f"{S.META['name']}_{tag}_pano.exr")
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
    bpy.data.objects.remove(cam)
    mx = float(max(avg))
    c = [float(x) / mx for x in avg]
    srgb = ['%02X' % round(255 * (12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055)) for v in c]
    log(f'Umgebungslicht {tag}: linear {avg.round(4).tolist()}', t0)
    return dict(color='#' + ''.join(srgb), strength=r6(round(mx, 4)))


def render_view(S, path, samples, denoise=True, view=None):
    """Bild vom Startpunkt: Augenhöhe, 75° horizontal, Blick nach −Y, AgX mit Look (wie `reference` in der Szenendatei);
    `view` (Sichtungsansicht aus S.VIEWS): eigene Lage, Gierwinkel (0 = −Y, 90 = +X), Nickwinkel, Bildwinkel, Auflösung."""
    import bpy
    from mathutils import Euler
    sc = bpy.context.scene
    R = S.REFERENCE
    cd = bpy.data.cameras.new('Ref')
    cd.sensor_fit = 'HORIZONTAL'
    cd.angle = math.radians(view.get('fov', R['h_fov_deg']) if view else R['h_fov_deg'])
    cd.clip_start = 0.05
    cd.clip_end = 500
    cam = bpy.data.objects.new('Ref', cd)
    sc.collection.objects.link(cam)
    sp = S.SPAWN['pos']
    cam.location = (sp[0], sp[1], sp[2] + R['eye_m'])
    cam.rotation_euler = Euler((math.radians(90), 0, math.radians(180 + S.SPAWN['yaw_deg'])))   # Blick −Y (LESSONS)
    if view:
        cam.location = view['pos']
        cam.rotation_euler = Euler((math.radians(90 + view.get('pitch', 0.0)), 0, math.radians(180 + view['yaw'])))
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = view.get('res', (1280, 720)) if view else R['res']
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


def swap_materials(objs, fn):
    """Alle Materialplätze der Objekte über fn(Objekt, Material) ersetzen; gibt die alte Belegung zurück."""
    old = {}
    for o in objs:
        old[o.name] = list(o.data.materials)
        for i, m in enumerate(o.data.materials):
            o.data.materials[i] = fn(o, m)
    return old


def restore_materials(objs, old):
    for o in objs:
        for i, m in enumerate(old[o.name]):
            o.data.materials[i] = m


def atlas_view(S, objs, zone_of, atlases, scale, path, views=()):
    """Wie Unity: Umgebung unbeleuchtet mit den Atlanten (Emission = Atlas × scale), Himmel als Hintergrund; gleiche Kamera.
    Dazu die Sichtungsansichten `views` als <path ohne _atlas_view.png>_<ansicht>.png."""
    import bpy
    vm = {}
    for zn, f in atlases.items():
        m = bpy.data.materials.new(f'V_{zn}')
        m.use_nodes = True
        N = m.node_tree.nodes
        for n in list(N):
            if n.type != 'OUTPUT_MATERIAL':
                N.remove(n)
        uv = N.new('ShaderNodeUVMap')
        uv.uv_map = 'UVMap'
        tex = N.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(f, check_existing=False)
        tex.image.colorspace_settings.name = 'sRGB'
        em = N.new('ShaderNodeEmission')
        em.inputs['Strength'].default_value = float(scale)
        m.node_tree.links.new(uv.outputs['UV'], tex.inputs['Vector'])
        m.node_tree.links.new(tex.outputs['Color'], em.inputs['Color'])
        out = next(n for n in N if n.type == 'OUTPUT_MATERIAL')
        m.node_tree.links.new(em.outputs['Emission'], out.inputs['Surface'])
        vm[zn] = m
    old = swap_materials(objs, lambda o, m: vm[zone_of[o.name]])
    render_view(S, path, 16, denoise=False)
    for v in views:
        render_view(S, path.replace('_atlas_view.png', f"_{v['name']}.png"), 16, denoise=False, view=v)
    restore_materials(objs, old)
    for m in vm.values():
        im = m.node_tree.nodes['Image Texture'].image if 'Image Texture' in m.node_tree.nodes else None
        bpy.data.materials.remove(m)
        if im:
            bpy.data.images.remove(im)
    return path


def image_diff(a, b):
    import bpy
    import numpy as np
    ims = [bpy.data.images.load(p, check_existing=False) for p in (a, b)]
    px = []
    for im in ims:
        v = np.empty(im.size[0] * im.size[1] * 4, np.float32)
        im.pixels.foreach_get(v)
        px.append(v.reshape(-1, 4)[:, :3])
        bpy.data.images.remove(im)
    return float(np.abs(px[0] - px[1]).mean() * 255)


def plan_view(S, objs, hide, path):
    """Draufsicht (orthografisch, ohne Dach) mit Strecke, Toren, Kontrollpunkten, Zielen und Startpunkt als Skizze."""
    import bpy
    import numpy as np
    sc = bpy.context.scene
    for o in objs:
        if o.name in hide:
            o.hide_render = True
    x0, x1, y0, y1 = -21.0, 21.0, -53.0, 31.0
    W, Hh = 840, 1680
    cd = bpy.data.cameras.new('Plan')
    cd.type = 'ORTHO'
    cd.ortho_scale = y1 - y0
    cd.sensor_fit = 'VERTICAL'
    cd.clip_end = 200
    cam = bpy.data.objects.new('Plan', cd)
    cam.location = ((x0 + x1) / 2, (y0 + y1) / 2, 60.0)
    sc.collection.objects.link(cam)
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = W, Hh, 100
    sc.cycles.samples = 32
    sc.cycles.use_denoising = True
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGB'
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    bpy.data.objects.remove(cam)
    for o in objs:
        o.hide_render = False
    im = bpy.data.images.load(path, check_existing=False)
    px = np.empty(W * Hh * 4, np.float32)
    im.pixels.foreach_get(px)
    img = px.reshape(Hh, W, 4)[..., :3].copy()
    bpy.data.images.remove(im)
    k = W / (x1 - x0)
    C = S.COURSE
    items = []

    def P(x, y):
        return ((x - x0) * k, (y - y0) * k)
    rt = [P(r[0], r[1]) for r in C['route']]
    items.append(dict(kind='line', pts=rt, w=4.0, color='#E8322A', alpha=0.95))
    for b, col in ((C['start'], '#3BD16F'), (C['finish'], '#3BD16F')):
        (cx, cy, _), (sx, sy, _) = b['center'], b['size']
        items.append(dict(kind='frame', a=P(cx - sx / 2, cy - sy / 2 - 0.3), b=P(cx + sx / 2, cy + sy / 2 + 0.3), w=4.0, color=col))
    for i, c in enumerate(C['checkpoints'], 1):
        (cx, cy, _), (sx, sy, _) = c['center'], c['size']
        items.append(dict(kind='frame', a=P(cx - sx / 2, cy - sy / 2), b=P(cx + sx / 2, cy + sy / 2), w=3.0, color='#36C8F0'))
        u, v = P(cx + sx / 2 + 0.4, cy - 0.6)
        items.append(dict(kind='text', at=(u, v), h=22.0, s=str(i), color='#36C8F0', w=0.16, align='left'))
    for t in C['targets']:
        u, v = P(t['pos'][0], t['pos'][1])
        items.append(dict(kind='disc', c=(u, v), r=7.0, color='#F03CC8'))
        items.append(dict(kind='text', at=(u + 9, v + 4), h=14.0, s=t['name'], color='#F03CC8', w=0.14, align='left'))
    u, v = P(*S.SPAWN['pos'][:2])
    items.append(dict(kind='disc', c=(u, v), r=8.0, color='#FFFFFF'))
    sh = Sheet(dict(size=(W, Hh), px_m=1.0, items=items))
    out = img * (1 - sh.A[..., None]) + sh.rgb * sh.A[..., None]
    o = bpy.data.images.new('plan_out', W, Hh, alpha=False)
    o.colorspace_settings.name = 'sRGB'
    buf = np.ones((Hh, W, 4), np.float32)
    buf[..., :3] = out
    o.pixels.foreach_set(buf.ravel())
    o.filepath_raw = path
    o.file_format = 'PNG'
    o.save()
    bpy.data.images.remove(o)
    return path


def export_fbx(objs, zone_of, name, path):
    import bpy
    zm = {}
    for o in objs:
        z = zone_of[o.name]
        if z not in zm:
            zm[z] = bpy.data.materials.new(f'{name}_{z}')     # ein Material je Zone: Unity zeigt den Zonenatlas unbeleuchtet
        me = o.data
        me.materials.clear()
        me.materials.append(zm[z])
        me.polygons.foreach_set('material_index', [0] * len(me.polygons))
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'MESH'}, use_mesh_modifiers=True,
                             mesh_smooth_type='OFF', use_custom_props=False, add_leaf_bones=False, bake_anim=False,
                             apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL', bake_space_transform=True,
                             axis_forward='-Z', axis_up='Y', path_mode='STRIP', embed_textures=False)


def blender_main():
    import bpy
    import numpy as np
    T0 = time.time()
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    name = argv[0] if argv else 'hangar'
    gpu = '--gpu' in argv or os.environ.get('BALLON_BAKE_GPU') == '1'
    S = load(name)
    err = SC.validate(S)
    if err:
        raise SystemExit('[scene_build] Szene fehlerhaft: ' + '; '.join(err))
    test = os.environ.get('BALLON_SCENE_TEST') == '1'
    only = [x for x in os.environ.get('BALLON_SCENE_LIGHTS', '').split(',') if x]
    LIGHTS = [L for L in S.LIGHTINGS if not only or L['name'] in only]
    test = test or bool(only)
    B = S.BAKE
    smp = int(os.environ.get('BALLON_SCENE_SAMPLES', 32 if test else B['samples']))
    dn_on = os.environ.get('BALLON_SCENE_DENOISE', '1' if B.get('denoise', True) else '0') == '1'
    asmp = int(os.environ.get('BALLON_SCENE_ASAMPLES', 8 if test else B['albedo_samples']))
    rsmp = 64 if test else S.REFERENCE['samples']
    div = int(os.environ.get('BALLON_SCENE_DIV', '2')) if test else 1       # Testlauf: Atlanten kleiner (Standard ½)
    sizes = {z['name']: z['size'] // div for z in S.ZONES}
    out = os.path.join(CACHE, 'test') if test else os.path.join(DST, name)
    cache = os.path.join(CACHE, 'test') if test else CACHE
    os.makedirs(out, exist_ok=True)
    os.makedirs(cache, exist_ok=True)
    log(f'Szene {name}: {len(S.ZONES)} Zonen {sizes}, {len(LIGHTS)} Lichtszenen, {smp} Samples (Grundfarbe {asmp}), Ausgabe {out}'
        + (' (Testlauf)' if test else ''))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    decals = decal_images(S, os.path.join(cache, 'decals'))
    t0 = time.time()
    mats = {r: material_full(r, R, decals, S) for r, R in S.ROLES.items()}
    log(f'{len(mats)} Materialrollen', t0)
    objs, tris = build(S, mats)
    zone_of = {o.name: z['name'] for z in S.ZONES for o in objs if o.name in z['groups']}
    zobjs = {z['name']: [o for o in objs if zone_of[o.name] == z['name']] for z in S.ZONES}
    zm = {}
    for o in objs:                         # Materialkopien je Zone: jede Zone backt in ihr eigenes Bild (ein Backaufruf)
        for i, m in enumerate(o.data.materials):
            key = (zone_of[o.name], m.name)
            if key not in zm:
                zm[key] = m.copy()
                zm[key].name = f'{m.name}_{key[0]}'
            o.data.materials[i] = zm[key]
    setup_cycles(gpu, smp, B)
    uvs = {zn: unwrap(zo, sizes[zn], B['pack_margin_px'], zn) for zn, zo in zobjs.items()}
    if os.environ.get('BALLON_SCENE_UVONLY') == '1':
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(cache, f'{name}_uv.blend'))
        log(f'nur UV: {tris} Dreiecke', T0)
        return
    # Grundfarbe je Zone (Abrieb, Schmutz, Masken; teure Knoten nur hier), danach Lichtmaterialien mit dem Albedo-Atlas
    set_lighting(S, LIGHTS[0])
    albedo = {}
    t0 = time.time()
    ims, tb = _bake_zones(zobjs, sizes, asmp, 'albedo', B['margin_px'], 'albedo')
    for zn, im in ims.items():
        p = os.path.join(cache, f'{name}_albedo_{zn}.png')
        _save_srgb(im, sizes[zn], p, 1.0, dither=False)
        bpy.data.images.remove(im)
        albedo[zn] = bpy.data.images.load(p, check_existing=False)
        albedo[zn].colorspace_settings.name = 'sRGB'
    log(f'Grundfarbe aller Zonen ({asmp} Samples): {tb:.1f} s', t0, 'albedo')
    t0 = time.time()                       # Normalen (Welt) als Führung für das Entrauschen
    normal, tb = _bake_zones(zobjs, sizes, 1, 'normal', B['margin_px'], 'normal')
    for zn, im in normal.items():
        px = np.empty(sizes[zn] ** 2 * 4, np.float32)
        im.pixels.foreach_get(px)
        px = px.reshape(-1, 4)
        px[:, :3] = px[:, :3] * 2.0 - 1.0
        im.pixels.foreach_set(px.ravel())
    log(f'Normalen: {tb:.1f} s', t0, 'normal')
    denoise = Denoiser(cache) if dn_on else None
    lmat = {}
    for o in objs:
        zn = zone_of[o.name]
        for i, m in enumerate(o.data.materials):
            r = m['scene_role']
            if (zn, r) not in lmat:
                lmat[(zn, r)] = material_light(r, S.ROLES[r], zn, albedo[zn])
            o.data.materials[i] = lmat[(zn, r)]
    stats = dict(triangles=tris, objects=len(objs), parts=sum(1 for p in S.PARTS if p['mesh']), zones={}, lightings={}, times=T_LOG)
    for zn, u in uvs.items():
        stats['zones'][zn] = dict(size=sizes[zn], area_m2=round(u['area_m2'], 1), uv_fill=round(u['uv_fill'], 3),
                                  texel_m=round(1.0 / u['texel_per_m'], 4),
                                  triangles=sum(len(f.vertices) - 2 for o in zobjs[zn] for f in o.data.polygons))
    D = data(S)
    D['lightings'] = [x for x in D['lightings'] if x['name'] in [L['name'] for L in LIGHTS]]
    for z in D['zones']:
        z['texel_m'] = stats['zones'][z['name']]['texel_m']
    for L, DL in zip(LIGHTS, D['lightings']):
        TL = time.time()
        set_lighting(S, L)
        DL['ambient'] = measure_ambient(S, cache, L['name'])
        setup_cycles(gpu, smp, B)
        files = {}
        st = dict(vmax={}, clip={})
        t0 = time.time()
        log(f'Backen {L["name"]}: alle Zonen mit {smp} Samples …')
        ims, tb = _bake_zones(zobjs, sizes, smp, 'light', B['margin_px'], L['name'])
        st['bake_s'] = round(tb, 1)
        log(f'gebacken {L["name"]}: {tb / 60:.2f} min', t0)
        for zn, im in ims.items():
            t0 = time.time()
            if denoise:
                t1 = time.time()
                denoise(im, albedo[zn], normal[zn], sizes[zn])
                st.setdefault('denoise_s', {})[zn] = round(time.time() - t1, 1)
            f = os.path.join(out, atlas_name(S, L, next(z for z in S.ZONES if z['name'] == zn)))
            vmax, clip = _save_srgb(im, sizes[zn], f, L['scale'])
            bpy.data.images.remove(im)
            files[zn] = f
            st['vmax'][zn], st['clip'][zn] = round(vmax, 3), round(clip * 100, 3)
            log(f'Atlas {L["name"]}/{zn}: max {vmax:.2f}, {clip * 100:.2f} % über Skala {L["scale"]:g}', t0)
        ref = os.path.join(cache, f'{name}_{L["name"]}_ref.png')
        t0 = time.time()
        render_view(S, ref, rsmp)
        st['ref_s'] = round(time.time() - t0, 1)
        log(f'Vergleichsrender {ref}', t0)
        t0 = time.time()
        av = atlas_view(S, objs, zone_of, files, L['scale'], ref.replace('_ref.png', '_atlas_view.png'), getattr(S, 'VIEWS', ()))
        st['views_s'] = round(time.time() - t0, 1)
        st['diff_255'] = round(image_diff(ref, av), 2)
        log(f'Atlasansicht {av}: mittlere Abweichung zum Vergleichsrender {st["diff_255"]:.1f}/255')
        if L['name'] == LIGHTS[0]['name']:
            t0 = time.time()
            hide = [g for z in S.ZONES if z['name'] == 'fern' for g in z['groups'] if g not in ('Vorfeld', 'Schutzwall')]
            pv = plan_view(S, objs, hide, os.path.join(cache, f'{name}_plan.png'))
            log(f'Skizze {pv}', t0, 'plan')
        st['total_s'] = round(time.time() - TL, 1)
        stats['lightings'][L['name']] = st
        log(f'Lichtszene {L["name"]} fertig: {st["total_s"] / 60:.1f} min', TL)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(cache, f'{name}_build.blend'))
    export_fbx(objs, zone_of, name, os.path.join(out, f'{name}.fbx'))
    write_json(os.path.join(out, f'scene_{name}.json'), D)
    stats['total_s'] = round(time.time() - T0, 1)
    write_json(os.path.join(cache, f'{name}_build.json'), stats)
    log(f'fertig: {len(objs)} Objekte, {tris} Dreiecke, {len(D["colliders"])} Kollisionsquader, '
        + ', '.join(f'{zn} {s["texel_m"] * 100:.2f} cm' for zn, s in stats['zones'].items()), T0)


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
