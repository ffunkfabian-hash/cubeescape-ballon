"""Skins aus Masken zusammensetzen (0.42 „Quickslot“, Entscheid 247 A): Farb- und Glanzkarte je Skin entstehen lokal aus dem Standard-Atlas
und den Skin-Masken (tools/skin_masks.py) mit der Mischkette von kit.aaa_nodes – nicht im Repo (.gitignore), sondern bei
`python3 tools/unity_run.py setup` vor dem Unity-Import. Läuft mit Blenders Python (numpy, OpenImageIO), ohne bpy und ohne GPU.

  <Blender>/Contents/Resources/<v>/python/bin/python3.x tools/skin_compose.py [--force] [--compare <Ordner mit gebackenen Skins>] [ID …]

Je Texel einer Rolle, die der Skin ändert (Farbe der Skin-Rolle, Tarnmuster, Abrieb-/Schmutzstärke, Metall-Gehäuse):
  Grundfarbe B = mix(mix(mix(C, W, m), D, g), S, s)   (W #9EA3A9 Abrieb, D #3B3329 Schmutz, S #A7ACB2 Kratzer – kit.aaa_nodes)
  Metall μ = mix(metal, 1, m), diffus = B·(1 − μ), spiegelnd = mix(0,08·spec, B, μ), Rauheit = mix(r, 0,28, m)
als Erwartungswert über die Samples des Bakes: m rauscht (Bevel), darum E[m] und E[m²] aus den Masken; g und s gehen linear ein
(E[(1 − m)²] = 1 − 2·E[m] + E[m²], E[m(1 − m)] = E[m] − E[m²]). Ausgabe = Standard-Atlas + (Modell Skin − Modell Standard): der Standard
bleibt bitgleich, das Rauschen des Bakes bleibt erhalten. Die Rauheit r ohne Abrieb kommt aus dem Glanzkanal des Standards. Ablage wie gebackene Skins
(export_unity.store_texture: JPG 92 % 4:4:4, Glanz 2048² in linearem Licht verkleinert).
"""
import json
import os
import subprocess
import sys
import time

import numpy as np
import OpenImageIO as oiio

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools import export_unity as EU  # noqa: E402

MIX = {'m': '#9EA3A9', 'g': '#3B3329', 's': '#A7ACB2'}     # Abrieb, Schmutz, Kratzer (kit.aaa_nodes; skin_masks.chain prüft sie)
WEAR_ROUGH, WEAR_METAL, F0_SCALE = 0.28, 1.0, 0.08          # kit.aaa_nodes (mr, mm), bake_unity._channel
PATTERN_STEPS = (0.47, 0.58)                                # kit.aaa_nodes: Tarnmuster-Rampe (konstant)
SHELL_METAL = dict(metal=0.85, rough=0.32)                   # kit.aaa_nodes: metal_shell (Eloxal)
VERSION = 3                                                  # Stempel im Ordner: neue Rechenregel → neu zusammensetzen


def lin(c):
    c = np.asarray(c, np.float32)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def srgb(c):
    c = np.clip(c, 0.0, 1.0)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def hexlin(h):
    h = h.lstrip('#')
    return lin([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])


def read(path, size=None, nearest=False):
    """Bild als float 0–1 (H, W, C), Alpha unvormultipliziert (Glanz im Alpha); size: auf size² bringen (bilinear, Rolle: nächster Texel)."""
    cfg = oiio.ImageSpec()
    cfg.attribute('oiio:UnassociatedAlpha', 1)
    buf = oiio.ImageBuf(path, 0, 0, cfg)
    if size and buf.spec().width != size:
        roi = oiio.ROI(0, size, 0, size, 0, 1, 0, buf.nchannels)
        buf = oiio.ImageBufAlgo.resample(buf, interpolate=not nearest, roi=roi)
    return buf.get_pixels(oiio.FLOAT)


def write(path, arr):
    h, w, c = arr.shape
    out = oiio.ImageOutput.create(path)
    spec = oiio.ImageSpec(w, h, c, oiio.UINT8)
    spec.attribute('png:compressionLevel', 1)
    spec.attribute('oiio:UnassociatedAlpha', 1)                 # Glanz im Alpha: Farbe nicht teilen
    out.open(path, spec)
    out.write_image(np.clip(np.rint(arr * 255), 0, 255).astype(np.uint8))
    out.close()


def tables(roles, D):
    """Je Rollenindex (0 = leer): Grundfarbe (linear), Metall, Rauheit, Spiegelstärke, Gruppe (skin_as), WEAR, GRIME."""
    R = {r['role']: r for r in D['roles']}
    mats = EU.kit_literal('MATERIALS')
    wear, grime = EU.kit_literal('WEAR'), EU.kit_literal('GRIME')
    t = []
    for r in roles:
        g = R[r].get('skin_as') or mats.get(r, {}).get('skin_as', r)
        # Rollen aus Modulen (metal_roles.RING_ROLES) setzen kit.WEAR/GRIME erst beim Import wie ihre Skin-Gruppe (setdefault)
        t.append(dict(name=r, C=hexlin(R[r].get('aaa_color', R[r]['color'])), metal=R[r]['metal'], rough=R[r]['rough'],
                      spec=R[r].get('spec', 0.5), group=g, wear=wear.get(r, wear.get(g)), grime=grime.get(r, grime.get(g))))
    return [None] + t


def compose_one(e, D, tex_dir, skins_def, force=False):
    """Alle Skins einer Waffe; gibt {Skin: (Albedo, Glanz)} der geschriebenen Dateien zurück."""
    T = e['textures']
    M = T.get('skin_masks')
    if not M:
        return {}
    todo = [s for s in T['skins'] if s['name'] != 'standard']
    stamp = os.path.join(tex_dir, f".skin_compose_{e['atlas']}.json")
    srcs = [T['weapon']['albedo'], T['weapon']['spec'], M['a'], M['b'], M['c'], M['p']]
    tab = tables(M['roles'], D)
    key = dict(version=VERSION, src={f: os.path.getmtime(os.path.join(tex_dir, f)) for f in srcs},   # alle Eingaben (Richter 0.42):
               skins={s['name']: skins_def[s['name']] for s in todo}, masks=M,                       # Bilder, Skins, Masken-Eintrag,
               roles=[{k: (v.tolist() if hasattr(v, 'tolist') else v) for k, v in r.items()} for r in tab[1:]])   # Rollenwerte

    if not force and os.path.exists(stamp) and json.load(open(stamp)) == json.loads(json.dumps(key)) and \
            all(os.path.exists(os.path.join(tex_dir, s[k])) for s in todo for k in ('albedo', 'spec')):
        return {}
    S = T['weapon']['size']
    t0 = time.time()
    alb = lin(read(os.path.join(tex_dir, T['weapon']['albedo']))[..., :3])
    sp = read(os.path.join(tex_dir, T['weapon']['spec']), S)
    spec_std, smooth_std = lin(sp[..., :3]), sp[..., 3]
    a = read(os.path.join(tex_dir, M['a']), S)
    b = read(os.path.join(tex_dir, M['b']), S)
    c = read(os.path.join(tex_dir, M['c']), S)
    role = np.rint(read(os.path.join(tex_dir, M['c']), S, nearest=True)[..., 2] * 255).astype(np.int32)
    pat = read(os.path.join(tex_dir, M['p']), S)[..., 0]
    wear_m = {'standard': (a[..., 0], a[..., 1]), 'nacht': (b[..., 0], b[..., 1]), 'gebraucht': (c[..., 0], c[..., 1])}
    g0, s = a[..., 2], b[..., 2]
    m0 = wear_m['standard'][0]
    lut = lambda f, d=0.0: np.array([d] + [f(r) for r in tab[1:]], np.float32)[role]   # noqa: E731
    C0 = np.array([np.zeros(3, np.float32)] + [r['C'] for r in tab[1:]], np.float32)[role]
    metal0, rough0, f0 = lut(lambda r: r['metal']), lut(lambda r: r['rough']), lut(lambda r: F0_SCALE * r['spec'])
    wear_r, grime_r = lut(lambda r: r['wear'] or 0.0), lut(lambda r: r['grime'] or 0.0)
    W, Dc, Sc = (hexlin(MIX[k]) for k in 'mgs')

    def model(C, mk, g, metal_r):
        """Erwartete Diffus- und Spiegelfarbe; mk = (E[m], E[m²])."""
        k1, k2 = mk
        x = lambda v: v[..., None]                            # noqa: E731
        u = (1 - g) * (1 - s)
        EB = C * x((1 - k1) * u) + W * x(k1 * u) + Dc * x(g * (1 - s)) + Sc * x(s)                       # E[B]
        EBm = C * x((k1 - k2) * u) + W * x(k2 * u) + Dc * x(g * (1 - s) * k1) + Sc * x(s * k1)           # E[B·m]
        diff = x(1 - metal_r) * (EB - EBm)                                                          # E[B·(1 − μ)], 1 − μ = (1 − metal)(1 − m)
        spec = f0[..., None] * x((1 - metal_r) * (1 - k1)) + x(metal_r) * EB + x(1 - metal_r) * EBm   # E[F0(1 − μ) + B·μ]
        return diff, spec

    d0, sp0 = model(C0, wear_m['standard'], g0, metal0)
    rough_std = 1 - smooth_std
    rv = np.where(m0 < 0.99, (rough_std - WEAR_ROUGH * m0) / np.maximum(1 - m0, 1e-3), rough0)
    out = {}
    for sk in todo:
        K = skins_def[sk['name']]
        groups = set(K.get('roles', {}))
        wk, gk = K.get('wear', 1.0), K.get('grime', 1.0)
        over = np.array([np.zeros(3, np.float32)] + [hexlin(K['roles'][r['group']]) if r['group'] in groups else r['C'] for r in tab[1:]],
                        np.float32)
        C = over[role]                                        # Skin-Rolle (Gruppe skin_as) statt Standardfarbe
        shell = np.array([False] + [r['group'] == 'shell' for r in tab[1:]])[role]
        recolor = np.array([False] + [r['group'] in groups for r in tab[1:]])[role]
        if K.get('pattern'):
            p = [hexlin(h) for h in K['pattern']]
            pc = np.where((pat < PATTERN_STEPS[0])[..., None], p[0], np.where((pat < PATTERN_STEPS[1])[..., None], p[1], p[2]))
            C[shell] = pc[shell]
        if sk['name'] in wear_m:
            mk = wear_m[sk['name']]
        elif wk != 1.0:                                       # Abrieb linear in der Stärke (MapRange To Max = min(1, WEAR · wear))
            w0, w1 = np.minimum(1, wear_r), np.minimum(1, wear_r * wk)
            q = np.where(w0 > 0, w1 / np.maximum(w0, 1e-6), 0)
            mk = (wear_m['standard'][0] * q, wear_m['standard'][1] * q * q)
        else:
            mk = wear_m['standard']
        m = mk[0]
        g = np.where(grime_r > 0, g0 * np.minimum(0.9, grime_r * gk) / np.maximum(np.minimum(0.9, grime_r), 1e-6), 0) if gk != 1.0 else g0
        metal_r, rv_k = metal0, rv
        if K.get('metal_shell'):
            metal_r = np.where(shell, SHELL_METAL['metal'], metal0)
            rv_k = np.where(shell, rv * SHELL_METAL['rough'] / np.maximum(rough0, 1e-3), rv)
        d1, sp1 = model(C, mk, g, metal_r)
        hit = (role > 0) & (recolor | (K.get('pattern') is not None) & shell | bool(K.get('metal_shell')) & shell
                            | ((wk != 1.0) & (wear_r > 0)) | ((gk != 1.0) & (grime_r > 0)))
        h3 = hit[..., None]
        al = np.where(h3, alb + d1 - d0, alb)
        spc = np.where(h3, spec_std + sp1 - sp0, spec_std)
        sm = np.where(hit, 1 - (rv_k + (WEAR_ROUGH - rv_k) * m), smooth_std)
        pa = os.path.join(tex_dir, sk['albedo'].rsplit('.', 1)[0] + '.png')
        ps = os.path.join(tex_dir, sk['spec'])
        write(pa, srgb(al))
        write(ps, np.concatenate([srgb(spc), sm[..., None]], -1))
        out[sk['name']] = (EU.store_texture(tex_dir, os.path.basename(pa), 'albedo'), EU.store_texture(tex_dir, os.path.basename(ps), 'spec'))
    json.dump(json.loads(json.dumps(key)), open(stamp, 'w'))
    print(f"[skin_compose] {e['id']}: {len(out)} Skins in {time.time() - t0:.0f} s", flush=True)
    return out


def compare(e, tex_dir, ref_dir):
    """Zusammengesetzte Skins gegen gebackene (ref_dir, gleiche Dateinamen): mittlere Abweichung (0–255) und PSNR je Karte, nur Atlas-Texel."""
    T = e['textures']
    role = read(os.path.join(tex_dir, T['skin_masks']['c']), 1024, nearest=True)[..., 2] > 0    # Rolle (Richter 0.42: nicht Maske b)
    res = {}
    for sk in T['skins']:
        if sk['name'] == 'standard':
            continue
        r = {}
        for k, size in (('albedo', 1024), ('spec', 1024)):
            ref = os.path.join(ref_dir, sk[k])
            if not os.path.exists(ref):
                continue
            x, y = read(os.path.join(tex_dir, sk[k]), size) * 255, read(ref, size) * 255
            dd = np.abs(x - y)[role]
            mse = float((dd ** 2).mean())
            r[k] = dict(mae=round(float(dd.mean()), 2), p99=round(float(np.percentile(dd, 99)), 1),
                        psnr=round(10 * np.log10(255 ** 2 / max(mse, 1e-9)), 1))
        res[sk['name']] = r
    return res


def main():
    a = sys.argv[1:]
    force = '--force' in a
    ref = a[a.index('--compare') + 1] if '--compare' in a else None
    want = [x for x in a if not x.startswith('--') and x != ref]
    D = json.load(open(os.path.join(EU.DST, 'ego.json'), encoding='utf-8'))
    skins_def = EU.kit_literal('SKINS')
    tex_dir = os.path.join(EU.DST, 'Textures')
    report = {}
    for e in D['weapons']:
        if 'origin' in e or (want and e['id'] not in want) or not e['textures'].get('skin_masks'):
            continue
        compose_one(e, D, tex_dir, skins_def, force)
        if ref:
            report[e['id']] = compare(e, tex_dir, ref)
            print(e['id'], json.dumps(report[e['id']]), flush=True)
    if ref:
        json.dump(report, open(os.path.join(ref, 'vergleich.json'), 'w'), indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main())
