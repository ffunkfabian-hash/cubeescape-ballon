"""MP4-Clips aus den Bildfolgen der Mechanik (ffmpeg), 854×480, ein Clip je Aktion.

  python3 tools/make_clips.py [BASIC-01 …]
Ausgabe: <EVIDENCE>/clips/<id>_<aktion>.mp4 – dieselben Frames wie Blätter und Kontaktbögen (<OUT>/<id>/motion/).
Einblendung: Waffen-ID, Aktion, Bild/Zeit (30 fps) und Ereignisse am jeweiligen Bild.
"""
import glob
import importlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools.paths import OUT, EVIDENCE  # noqa: E402

FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
BG_HEX = '#F2F1EE'


def weapon(wid):
    for f in glob.glob(os.path.join(ROOT, 'basic', 'weapons', 'w*.py')):
        W = importlib.import_module('basic.weapons.' + os.path.basename(f)[:-3])
        if W.META['id'] == wid:
            return W


def main(argv):
    ids = argv or sorted(os.path.basename(d) for d in glob.glob(os.path.join(OUT, 'BASIC-*')))
    dst = os.path.join(EVIDENCE, 'clips')
    os.makedirs(dst, exist_ok=True)
    made = []
    for wid in ids:
        W = weapon(wid)
        for act, A in W.ACTIONS.items():
            src = os.path.join(OUT, wid, 'motion', act)
            frames = sorted(glob.glob(os.path.join(src, '*.png')))
            if not frames:
                continue
            step = A.get('step', 2)
            fps = 30 / step
            ev = A.get('events', [])
            out = os.path.join(dst, f'{wid}_{act}.mp4')
            tmp = os.path.join(src, '_lab')
            os.makedirs(tmp, exist_ok=True)
            for i, p in enumerate(frames):   # Beschriftung mit ImageMagick (ffmpeg hier ohne drawtext)
                n = int(os.path.basename(p)[:4])
                cur = [name for fr, name in ev if fr <= n < fr + max(4, 8)]
                cmd = ['magick', p, '-background', BG_HEX, '-flatten', '-font', FONT, '-fill', '#1F2328', '-pointsize', '20',
                       '-annotate', '+18+34', f'{wid} · {act}', '-fill', '#4A4E55', '-pointsize', '16',
                       '-annotate', '+18+60', f'Bild {n} · {n * 1000 / 30:.0f} ms · 30 fps']
                if cur:
                    cmd += ['-fill', '#C4520F', '-pointsize', '20', '-gravity', 'NorthEast', '-annotate', '+18+34', '> ' + cur[-1]]
                subprocess.run(cmd + [os.path.join(tmp, f'{i:04d}.png')], check=True)
            r = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', f'{fps:g}', '-i', os.path.join(tmp, '%04d.png'),
                                '-vf', 'format=yuv420p', '-c:v', 'libx264', '-crf', '24', '-movflags', '+faststart', out],
                               capture_output=True, text=True)
            for q in glob.glob(os.path.join(tmp, '*.png')):
                os.remove(q)
            os.rmdir(tmp)
            if r.returncode:
                print('Fehler', wid, act, r.stderr[-400:])
                continue
            made.append(out)
    meta = {os.path.basename(m): os.path.getsize(m) for m in made}
    json.dump(meta, open(os.path.join(dst, 'clips.json'), 'w'), indent=1)
    print(f'{len(made)} Clips in {dst}')


if __name__ == '__main__':
    main(sys.argv[1:])
