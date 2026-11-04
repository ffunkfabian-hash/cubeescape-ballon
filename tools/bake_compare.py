"""Atlas zweier Bakes vergleichen (0.43 „Kiln“): je Karte mittlere Abweichung, PSNR und SSIM auf den Inseln (Atlas-Texel ohne leeren Rand).

  <Blender-Python> tools/bake_compare.py <Ordner Referenz> <Ordner Kandidat> <Name Referenz> <Name Kandidat> [--json Datei]

Beide Ordner enthalten <Name>_albedo.jpg, _spec.png, _normal.png, _ao.png. Unterschiedliche Kantenlängen: die größere Karte wird als Kastenmittel auf die
kleinere gebracht. Die Inseln liest das Werkzeug aus der AO-Karte der Referenz (Rand: 0), um die Füllung eingeengt. Python von Blender, weil es numpy und OpenImageIO mitbringt.
"""
import json
import os
import sys

import numpy as np
import OpenImageIO as oiio

ERODE = 6                                          # Texel bei 2048²: Füllung der Referenz (8 bei 4096² = 4) und Übergang
KINDS = (('albedo', 'jpg'), ('spec', 'png'), ('normal', 'png'), ('ao', 'png'))


def read(path):
    i = oiio.ImageInput.open(path)
    if i is None:
        raise FileNotFoundError(path)
    px = i.read_image('float')
    i.close()
    return px


def erode(m, r):
    """Maske um r Texel einengen: der Rand der Inseln ist Füllung (bake margin in Texeln, 2048² doppelt so breit wie 4096²), kein Inhalt."""
    for _ in range(r):
        e = m.copy()
        e[1:] &= m[:-1]
        e[:-1] &= m[1:]
        e[:, 1:] &= m[:, :-1]
        e[:, :-1] &= m[:, 1:]
        m = e
    return m


def box(a, n):
    k = a.shape[0] // n
    return a.reshape(n, k, n, k, -1).mean(axis=(1, 3)) if k > 1 else a


def ssim(x, y, w=8):
    """Mittleres SSIM je w×w-Block (Grauwert), Blöcke mit Atlas-Inhalt."""
    h = (x.shape[0] // w) * w
    bx = x[:h, :h].reshape(h // w, w, h // w, w).transpose(0, 2, 1, 3).reshape(-1, w * w)
    by = y[:h, :h].reshape(h // w, w, h // w, w).transpose(0, 2, 1, 3).reshape(-1, w * w)
    mx, my = bx.mean(1), by.mean(1)
    vx, vy = bx.var(1), by.var(1)
    cov = ((bx - mx[:, None]) * (by - my[:, None])).mean(1)
    c1, c2 = 0.01 ** 2, 0.03 ** 2
    return (2 * mx * my + c1) * (2 * cov + c2) / ((mx * mx + my * my + c1) * (vx + vy + c2))


def compare(a, b, mask):
    n = min(a.shape[0], b.shape[0], mask.shape[0])
    a, b, m = box(a, n), box(b, n), erode(box(mask, n)[..., 0] > 0.5, round(ERODE * n / 2048))
    d = np.abs(a - b)[m]
    mse = float((d ** 2).mean())
    ga, gb = a[..., :3].mean(-1) if a.shape[-1] >= 3 else a[..., 0], b[..., :3].mean(-1) if b.shape[-1] >= 3 else b[..., 0]
    s = ssim(ga, gb)
    w = 8
    h = (n // w) * w
    mb = m[:h, :h].reshape(h // w, w, h // w, w).mean((1, 3)).ravel() > 0.9
    return dict(n=n, mean=round(float(d.mean()) * 255, 2), p999=round(float(np.quantile(d, 0.999)) * 255, 1),
                psnr=round(10 * np.log10(1 / max(mse, 1e-12)), 2), ssim=round(float(s[mb].mean()), 4), ssim_p1=round(float(np.quantile(s[mb], 0.01)), 3))


def run(ref_dir, new_dir, ref_name, new_name):
    ao = read(os.path.join(ref_dir, f'{ref_name}_ao.png'))
    mask = (ao[..., :1] > 0.003).astype(np.float32)
    out = {}
    for k, ext in KINDS:
        a, b = read(os.path.join(ref_dir, f'{ref_name}_{k}.{ext}')), read(os.path.join(new_dir, f'{new_name}_{k}.{ext}'))
        if k == 'spec':
            out['spec_rgb'] = compare(a[..., :3], b[..., :3], mask)
            out['gloss'] = compare(a[..., 3:4], b[..., 3:4], mask)
        else:
            out[k] = compare(a, b, mask)
    return out


if __name__ == '__main__':
    res = run(*sys.argv[1:5])
    for k, v in res.items():
        print(f"{k:9s} {v['n']}²  mittel {v['mean']:6.2f}/255  p99,9 {v['p999']:6.1f}  PSNR {v['psnr']:6.2f} dB  SSIM {v['ssim']:.4f}  (1%-Block {v['ssim_p1']:.3f})")
    if '--json' in sys.argv:
        json.dump(res, open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=1)
    if '--limits' in sys.argv:                          # Grenzwerte je Karte (data/bake_settings.json › limits); --limits <Datei> <Schlüssel>
        i = sys.argv.index('--limits')
        L = json.load(open(sys.argv[i + 1], encoding='utf-8'))['limits'][sys.argv[i + 2]]
        over = [f"{k}: SSIM {res[k]['ssim']} < {v['ssim']}" for k, v in L.items() if res[k]['ssim'] < v['ssim']] + \
               [f"{k}: Abweichung {res[k]['mean']} > {v['mean']}" for k, v in L.items() if res[k]['mean'] > v['mean']]
        print('Grenzwerte ' + ('überschritten: ' + '; '.join(over) if over else 'eingehalten'))
        sys.exit(1 if over else 0)
