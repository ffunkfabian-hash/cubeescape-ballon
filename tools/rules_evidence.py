"""Belege der Regelprüfungen aus 0.30 „Rulebook“ (ohne Blender; Bilder mit ImageMagick).

  python3 tools/rules_evidence.py [--far]

Ausgabe <EVIDENCE>/rulebook/: silhouettes_side.png und silhouettes_ego.png (Masken aus data/silhouettes.json, gleiche Länge),
iou_side.md und iou_ego.md (Matrix, Fett ≥ Grenze), budget.md (Dreiecke je Waffe gegen Ziel und Grenze), clear_zone.md
(data/ego_clear.json); mit --far zusätzlich far_contact.png (Ansicht far aus tools/far_views.py, je Waffe 3 m und 5 m).
"""
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools import rules  # noqa: E402
from tools.paths import EVIDENCE, OUT  # noqa: E402

DST = os.path.join(EVIDENCE, 'rulebook')


def pbm(mask, path):
    with open(path, 'w') as fh:
        fh.write(f"P1\n{mask['w']} {mask['h']}\n")
        for r in mask['rows']:
            line = ['0'] * mask['w']
            for s, e in zip(r[::2], r[1::2]):
                line[s:e] = ['1'] * (e - s)
            fh.write(' '.join(line) + '\n')


def mosaic(data, view):
    tmp = os.path.join(DST, '_tiles')
    os.makedirs(tmp, exist_ok=True)
    args = []
    for wid, e in data['weapons'].items():
        p = os.path.join(tmp, f'{wid}_{view}.pbm')
        pbm(e[view], p)
        subprocess.run(['magick', p, '-depth', '8', '-type', 'Grayscale', p[:-4] + '.png'], check=True)
        args += ['-label', f"{wid}  {e['mm_per_px'][view]:.2f} mm/px", p[:-4] + '.png']
    out = os.path.join(DST, f'silhouettes_{view}.png')
    subprocess.run(['magick', 'montage', *args, '-tile', '4x', '-geometry', '+16+12', '-background', '#F2F1EE',
                    '-pointsize', '14', out], check=True)
    return out


def matrix_md(data, view):
    M = rules.iou_matrix(data, view)
    ids = list(data['weapons'])
    sh = [i.replace('BASIC-', '').replace('-v2.1', '') for i in ids]
    lines = [f"| {view} | " + ' | '.join(sh) + ' |', '|---' * (len(ids) + 1) + '|']
    for a, s in zip(ids, sh):
        cells = []
        for b in ids:
            v = M.get((a, b), M.get((b, a)))
            cells.append('–' if v is None else (f'**{v:.2f}**' if v >= rules.IOU_LIMIT else f'{v:.2f}'))
        lines.append(f'| {s} | ' + ' | '.join(cells) + ' |')
    top = sorted(M.items(), key=lambda kv: -kv[1])[:5]
    lines += ['', 'Höchste Paare: ' + ', '.join(f'{a} ↔ {b} {v:.3f}' for (a, b), v in top)]
    return '\n'.join(lines) + '\n'


def budget_md():
    rows = ['| Waffe | Dreiecke | Stand |', '|---|---:|---|']
    for wid, _ in rules.family():
        t = json.load(open(os.path.join(ROOT, 'data', 'specs', f'{wid}.spec.json'), encoding='utf-8'))['counts']['triangles']
        st = 'über Grenze' if t > rules.TRI_LIMIT else 'über Ziel' if t > rules.TRI_TARGET else 'im Ziel'
        rows.append(f'| {wid} | {t:,} | {st} |'.replace(',', ' '))
    return '\n'.join(rows) + '\n'


def clear_md():
    p = os.path.join(ROOT, 'data', 'ego_clear.json')
    if not os.path.exists(p):
        return 'data/ego_clear.json fehlt\n'
    D = json.load(open(p, encoding='utf-8'))
    rows = ['| Waffe | belegte Zonenpixel | Anteil der Zone | oberster Punkt in den Zonenspalten (H von oben; Zone bis 66,7 %) | Bild |', '|---|---:|---:|---:|---|']
    for wid, e in D['weapons'].items():
        rows.append(f"| {wid} | {e['zone_px']} | {e['zone_share'] * 100:.2f} % | "
                    f"{'–' if e['top_y'] is None else format(e['top_y'] * 100, '.1f') + ' %'} | {e.get('evidence', '')} |")
    return '\n'.join(rows) + '\n'


def far_contact():
    tiles = []
    for wid, _ in rules.family():
        for d in ('3m', '5m'):
            p = os.path.join(OUT, wid, 'views', f'far_{d}.png')
            if os.path.exists(p):
                tiles += ['-label', f'{wid} · {d}', p]
    out = os.path.join(DST, 'far_contact.png')
    subprocess.run(['magick', 'montage', *tiles, '-tile', '4x', '-geometry', '+8+8', '-background', '#F2F1EE', '-pointsize', '14',
                    out], check=True)
    return out


def main(argv):
    os.makedirs(DST, exist_ok=True)
    data = json.load(open(os.path.join(ROOT, 'data', 'silhouettes.json'), encoding='utf-8'))
    for v in ('side', 'ego'):
        print(mosaic(data, v))
        open(os.path.join(DST, f'iou_{v}.md'), 'w', encoding='utf-8').write(matrix_md(data, v))
    open(os.path.join(DST, 'budget.md'), 'w', encoding='utf-8').write(budget_md())
    open(os.path.join(DST, 'clear_zone.md'), 'w', encoding='utf-8').write(clear_md())
    if '--far' in argv:
        print(far_contact())
    for f in sorted(glob.glob(os.path.join(DST, '*.md'))):
        print(f)


if __name__ == '__main__':
    main(sys.argv[1:])
