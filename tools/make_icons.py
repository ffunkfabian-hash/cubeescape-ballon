"""Waffensymbole für HUD und Waffenmenü (0.33 „Armory“, Ziel 2) aus den Silhouetten (data/silhouettes.json › side) per ImageMagick.

Je Waffe aus tools/export_unity.WEAPONS ein weißes PNG mit Alphakanal (Silhouette der Seitenansicht, Mündung rechts, auf gleiche Länge
normiert wie A1), knapp beschnitten mit 4 px Rand, nach unity/Assets/Ballon/Generated/Icons/<id>.png. Unity färbt es im HUD ein
(EgoPlayer.OnGUI). Die Herkunft je Symbol steht in Icons/icons.json (Hash der Silhouettenzeilen); --check meldet fehlende oder veraltete
Symbole, ohne zu schreiben.

    python3 tools/make_icons.py            # erzeugen
    python3 tools/make_icons.py --check    # nur prüfen (./check)
"""
import hashlib
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic.arms import ego as EG  # noqa: E402
from tools import export_unity as EX  # noqa: E402

SIL = os.path.join(ROOT, 'data', 'silhouettes.json')
OUT = os.path.join(ROOT, 'unity', 'Assets', 'Ballon', 'Generated', 'Icons')
BORDER = 4


def weapon_ids():
    return [EG.weapon_id(importlib.import_module(f'basic.{m}')) for m in EX.WEAPONS]


def rows_sha(side):
    return hashlib.sha256(json.dumps(side, sort_keys=True).encode()).hexdigest()


def pbm(side):
    """Silhouette als PBM (P1): 1 = belegt; rows je Bildzeile [Beginn, Ende, …] belegter Spalten (Ende einschließlich)."""
    w, h = side['w'], side['h']
    lines = [f'P1\n{w} {h}']
    for r in side['rows']:
        px = [0] * w
        for a, b in zip(r[::2], r[1::2]):
            for x in range(a, min(b, w - 1) + 1):
                px[x] = 1
        lines.append(' '.join(map(str, px)))
    return '\n'.join(lines) + '\n'


def render(side, dst, magick):
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, 'sil.pbm')
        open(src, 'w').write(pbm(side))
        # belegt (schwarz) → weiß und deckend, frei → durchsichtig; beschneiden, Rand
        subprocess.run([magick, src, '-negate', '-alpha', 'copy', '-fill', 'white', '-colorize', '100', '-trim', '+repage',
                        '-bordercolor', 'none', '-border', str(BORDER), '-define', 'png:color-type=6', dst], check=True)


def main():
    check = '--check' in sys.argv
    sil = json.load(open(SIL, encoding='utf-8'))['weapons']
    meta_path = os.path.join(OUT, 'icons.json')
    meta = json.load(open(meta_path, encoding='utf-8')) if os.path.exists(meta_path) else {}
    want, err = {}, []
    for wid in weapon_ids():
        if wid not in sil:
            err.append(f'{wid}: keine Silhouette in data/silhouettes.json (tools/silhouettes.py)')
            continue
        side = sil[wid]['side']
        side = json.loads(side) if isinstance(side, str) else side
        want[wid] = dict(file=f'{wid}.png', rows_sha256=rows_sha(side), w=side['w'], h=side['h'])
        if check and (meta.get('icons', {}).get(wid, {}).get('rows_sha256') != want[wid]['rows_sha256']
                      or not os.path.exists(os.path.join(OUT, f'{wid}.png'))):
            err.append(f'{wid}: Symbol fehlt oder ist veraltet (python3 tools/make_icons.py)')
    if check:
        extra = set(meta.get('icons', {})) - set(want)
        err += [f'{w}: Symbol ohne Waffe in export_unity.WEAPONS' for w in sorted(extra)]
        print('\n'.join(err) if err else f'Symbole: {len(want)} aktuell')
        return 1 if err else 0
    if err:
        print('\n'.join(err))
        return 1
    magick = shutil.which('magick') or shutil.which('convert')
    if not magick:
        print('ImageMagick fehlt (magick)')
        return 1
    os.makedirs(OUT, exist_ok=True)
    for wid, m in want.items():
        side = sil[wid]['side']
        render(json.loads(side) if isinstance(side, str) else side, os.path.join(OUT, m['file']), magick)
    json.dump(dict(format='ballon-icons/1', de='Waffensymbole (weiß, Alpha) aus data/silhouettes.json › side, tools/make_icons.py; '
                                          'Reihenfolge wie export_unity.WEAPONS',
                   order=list(want), icons=want), open(meta_path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f'Symbole: {len(want)} nach {os.path.relpath(OUT, ROOT)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
