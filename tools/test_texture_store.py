"""Prüfung der Texturablage (0.20, Entscheidung 97 A; Richter 0.20 Nr. 4): store_texture legt eine gebackene Datei nach der Regel ab
(Endung, Kantenlänge, 8 bit, AO ein Kanal), texture_problems erkennt falsche Endung, Kantenlänge, Bittiefe und eine überschrittene
Grenze. Kleine Testbilder (64²/32² statt 4096²/2048²) in einem Temp-Ordner, nur `magick`; läuft in ./check."""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import tools.export_unity as XU  # noqa: E402


def make(path, size, depth=8, alpha=False):
    subprocess.run(['magick', '-size', f'{size}x{size}', 'plasma:', '-depth', str(depth)] + (['-alpha', 'on'] if alpha else []) + [path],
                   check=True, capture_output=True)


def main():
    err = []
    store = json.loads(json.dumps(XU.TEXTURE_STORE))
    for k, v in (('albedo', 64), ('spec', 32), ('normal', 64), ('ao', 32)):
        store[k]['size'] = v
    old = XU.TEXTURE_STORE
    XU.TEXTURE_STORE = store
    try:
        with tempfile.TemporaryDirectory() as d:
            make(os.path.join(d, 'w_albedo.png'), 64)
            make(os.path.join(d, 'w_spec.png'), 64, alpha=True)
            make(os.path.join(d, 'w_normal.png'), 64, depth=16)
            make(os.path.join(d, 'w_ao.png'), 64, depth=16)
            make(os.path.join(d, 'w_x_albedo.png'), 64)
            make(os.path.join(d, 'w_x_spec.png'), 64, alpha=True)
            tex = dict(weapon=dict(albedo='w_albedo.png', spec='w_spec.png', normal='w_normal.png', ao='w_ao.png'),
                       skins=[dict(name='x', albedo='w_x_albedo.png', spec='w_x_spec.png')])
            D = dict(weapons=[dict(id='T', textures=tex)])
            if not XU.texture_problems(D, d, store):
                err.append('ungeordnete Dateien nicht erkannt')
            T = XU.store_textures(tex, d)
            D['weapons'][0]['textures'] = T
            bad = XU.texture_problems(D, d, store)
            if bad:
                err.append('nach der Ablage: ' + '; '.join(bad))
            if os.path.exists(os.path.join(d, 'w_albedo.png')) or not T['weapon']['albedo'].endswith('.jpg'):
                err.append('albedo nicht als JPG abgelegt')
            if T != XU.store_textures(T, d):
                err.append('zweite Ablage ändert etwas (nicht wiederholbar)')
            make(os.path.join(d, 'w_spec.png'), 64, alpha=True)        # falsche Kantenlänge
            if not any('w_spec.png' in b for b in XU.texture_problems(D, d, store)):
                err.append('falsche Kantenlänge spec nicht erkannt')
            XU.store_texture(d, 'w_spec.png', 'spec')
            make(os.path.join(d, 'w_x_spec.png'), 32, depth=16, alpha=True)   # Skin mit 16 bit
            if not any('w_x_spec.png' in b for b in XU.texture_problems(D, d, store)):
                err.append('Skin mit 16 bit nicht erkannt')
            XU.store_texture(d, 'w_x_spec.png', 'spec')
            store['limit_mb'] = 1e-6
            if not any('MB >' in b for b in XU.texture_problems(D, d, store)):
                err.append('Grenze nicht erkannt')
    finally:
        XU.TEXTURE_STORE = old
    print('\n'.join(err) if err else 'test_texture_store: Ablage und Prüfung in Ordnung')
    return 1 if err else 0


if __name__ == '__main__':
    sys.exit(main())
