"""Kontaktbögen aus den gerenderten Ansichten (ImageMagick).

  python3 tools/contact.py hero              → Raster aller Hauptansichten
  python3 tools/contact.py side --scale      → Seitenansichten im gleichen Maßstab (mm-genau, Raster 100 mm)
Ausgabe: <EVIDENCE>/contact_<ansicht>.png
"""
import glob
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.paths import OUT, EVIDENCE  # noqa: E402

BG = '#F2F1EE'


def main(argv):
    view = argv[0] if argv else 'hero'
    scaled = '--scale' in argv
    os.makedirs(EVIDENCE, exist_ok=True)
    tiles = []
    hmax = max(json.load(open(f))['dimensions']['height_m'] for f in glob.glob(os.path.join(OUT, 'BASIC-*', 'BASIC-*.spec.json')))
    ext = f'640x{int(hmax * 400 + 40)}'
    tmp = os.path.join(EVIDENCE, '_tiles')
    os.makedirs(tmp, exist_ok=True)
    for d in sorted(glob.glob(os.path.join(OUT, 'BASIC-*'))):
        wid = os.path.basename(d)
        png = os.path.join(d, 'views', f'{view}.png')
        if not os.path.exists(png):
            continue
        spec = json.load(open(os.path.join(d, f'{wid}.spec.json')))
        meta = json.load(open(os.path.join(d, 'views', 'views.json')))
        label = f"{wid} {spec['weapon']['type_de']} · {spec['dimensions']['length_m'] * 1000:.0f} mm"
        out = os.path.join(tmp, f'{wid}_{view}.png')
        cmd = ['magick', png, '-background', BG, '-flatten']
        if scaled:
            px_per_m = meta['resolution'][0] / meta['views'][view]['ortho_scale']
            f = 400 / px_per_m          # Ziel: 400 px je Meter
            cmd += ['-resize', f'{f * 100:.3f}%', '-gravity', 'center', '-extent', ext]
        else:
            cmd += ['-resize', '600x']
        subprocess.run(cmd + [out], check=True)
        tiles += ['-label', label, out]
    res = os.path.join(EVIDENCE, f'contact_{view}{"_scaled" if scaled else ""}.png')
    title = f'BASIC · {view} · ' + ('gleicher Maßstab 400 px/m' if scaled else 'je Waffe eingepasst')
    subprocess.run(['magick', 'montage', *tiles, '-tile', '3x', '-geometry', '+12+12', '-background', BG,
                    '-font', 'Helvetica', '-pointsize', '18', '-title', title, res], check=True)
    print(res)


if __name__ == '__main__':
    main(sys.argv[1:])
