"""Bewegungs-Kontaktbögen: je Aktion eine Zeile (Start, Ereignisbilder, Ende) aus denselben Frames wie die Clips.

  python3 tools/motion_sheet.py [BASIC-01 …]   → <EVIDENCE>/motion_<id>.png
Grundlage der Sichtung in data/review.json.
"""
import glob
import importlib
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools.paths import OUT, EVIDENCE  # noqa: E402


def main(argv):
    mods = {}
    for f in glob.glob(os.path.join(ROOT, 'basic', 'weapons', 'w*.py')):
        W = importlib.import_module('basic.weapons.' + os.path.basename(f)[:-3])
        mods[W.META['id']] = W
    ids = argv or sorted(mods)
    tmp = os.path.join(EVIDENCE, '_motion_tiles')
    os.makedirs(tmp, exist_ok=True)
    for wid in ids:
        W = mods[wid]
        rows = []
        for act, A in W.ACTIONS.items():
            frames = sorted(glob.glob(os.path.join(OUT, wid, 'motion', act, '*.png')))
            if not frames:
                continue
            nums = [int(os.path.basename(p)[:4]) for p in frames]
            names = {f: n for f, n in A.get('events', [])}
            keys = sorted({0, A['frames'], *names})
            tiles = []
            for k in keys:
                i = min(range(len(nums)), key=lambda j: abs(nums[j] - k))
                out = os.path.join(tmp, f'{wid}_{act}_{k:04d}.png')
                subprocess.run(['magick', frames[i], '-background', '#F2F1EE', '-flatten', '-resize', '300x', out], check=True)
                tiles += ['-label', f"{act} · Bild {nums[i]} · {names.get(k, 'Start' if k == 0 else 'Ende')}", out]
            row = os.path.join(tmp, f'{wid}_{act}_row.png')
            subprocess.run(['magick', 'montage', *tiles[:24], '-tile', 'x1', '-geometry', '+3+3', '-pointsize', '11',
                            '-background', '#F2F1EE', row], check=True)
            rows.append(row)
        res = os.path.join(EVIDENCE, f'motion_{wid}.png')
        subprocess.run(['magick', *rows, '-background', '#F2F1EE', '-gravity', 'west', '-append', res], check=True)
        print(res)


if __name__ == '__main__':
    main(sys.argv[1:])
