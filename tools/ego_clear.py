"""Freihaltezone im Hüftbild (A4, BALLON 0.30 „Rulebook“; Regel docs/stilhandbuch.md › 2): Maske von Waffe und Armen im Ego-Still.

  ~/Claude/cubeescape-nexogen/ce lock gpu -- /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup \
      -P <repo>/tools/ego_clear.py -- [--gpu] [--samples 32] [pilot.w01_auto_rifle_v21 …]

Je spielbarer Waffe (tools/export_unity.WEAPONS, ohne Argumente alle) die Ego-Szene aus tools/ego_build.py in der Haltung `hip`
(Hände wie ego_build --stills, ohne Mündungsfeuer und Hülsen): ein Cycles-Still und aus derselben Szene und Pose eine
Workbench-Maske (Alpha, Waffe und Arme). Zone nach tools/rules.ZONE (±10 % B um die Absehen-Spalte = Bildmitte, obere zwei Drittel).
Ausgabe: data/ego_clear.json (Zahlen, Quellen-SHA), Beleg <EVIDENCE>/rulebook/clear_<Waffe>.png (Still, Maske getönt, Zone cyan,
Verletzung rot). ./check wertet die Zahlen aus (Warnung, kein Fehler).
"""
import importlib
import json
import os
import sys

import bpy
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools import rules  # noqa: E402
from tools import ego_build as EB  # noqa: E402
from tools.export_unity import WEAPONS  # noqa: E402
from tools.paths import EVIDENCE  # noqa: E402

DST = os.path.join(ROOT, 'data', 'ego_clear.json')
RES = (1600, 900)


def load_png(path):
    im = bpy.data.images.load(path)
    w, h = im.size
    px = np.empty(w * h * 4, dtype=np.float32)
    im.pixels.foreach_get(px)
    bpy.data.images.remove(im)
    return px.reshape(h, w, 4)[::-1]          # Zeile 0 oben


def save_png(arr, path):
    h, w = arr.shape[:2]
    im = bpy.data.images.new('clear', w, h, alpha=True)
    im.pixels.foreach_set(np.ascontiguousarray(arr[::-1]).ravel().astype(np.float32))
    im.filepath_raw = path
    im.file_format = 'PNG'
    im.save()
    bpy.data.images.remove(im)


def measure(mask):
    h, w = mask.shape
    x0, x1, y0, y1 = rules.zone_px(w, h)
    z = mask[y0:y1, x0:x1]
    band = np.flatnonzero(mask[:, x0:x1].any(axis=1))          # Zeilen mit Waffe/Arm in den Zonenspalten (ganze Bildhöhe)
    cols = np.flatnonzero(z.any(axis=0))
    return dict(zone_px=int(z.sum()), zone_share=round(float(z.mean()), 5),
                top_y=round(float(band[0] / h), 4) if len(band) else None,
                cols=[round((x0 + int(cols[0])) / w, 4), round((x0 + int(cols[-1]) + 1) / w, 4)] if len(cols) else None,
                zone=dict(x=[round(x0 / w, 4), round(x1 / w, 4)], y=[round(y0 / h, 4), round(y1 / h, 4)]))


def overlay(still, mask, path):
    h, w = mask.shape
    x0, x1, y0, y1 = rules.zone_px(w, h)
    img = still[..., :3].copy()
    tint = np.array([0.85, 0.2, 0.85])
    img[mask] = img[mask] * 0.55 + tint * 0.45
    hit = np.zeros_like(mask)
    hit[y0:y1, x0:x1] = mask[y0:y1, x0:x1]
    img[hit] = [0.95, 0.1, 0.1]
    cyan = [0.1, 0.9, 0.95]
    for t in range(3):
        img[y0:y1, x0 + t] = img[y0:y1, x1 - 1 - t] = cyan
        img[y0 + t, x0:x1] = img[y1 - 1 - t, x0:x1] = cyan
    save_png(np.concatenate([img, np.ones((h, w, 1))], axis=-1), path)


def main():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    gpu = '--gpu' in a
    samples = int(a[a.index('--samples') + 1]) if '--samples' in a else 32
    want = [x for x in a if x.startswith(('pilot.', 'weapons.'))] or WEAPONS
    data = json.load(open(DST, encoding='utf-8')) if os.path.exists(DST) else {}
    out = dict(data.get('weapons', {}))
    ev = os.path.join(EVIDENCE, 'rulebook')
    os.makedirs(ev, exist_ok=True)
    for m in want:
        W = importlib.import_module(f'basic.{m}')
        wid = f"{W.META['id']}-{W.META['variant']}"
        sc = EB.Scene(W, dict(gpu=gpu, samples=samples, fx=False))
        EB.evaluate(sc, dict(weapon=[(0, 'hip')], L=[(0, 'support')], R=[(0, 'grip')]), 0, {}, {})
        # Leuchtteile (move.kind glow) sitzen seit 0.32 in ego_build.set_weapon an der Waffe (vorher schwebten die Salvenanzeigen von
        # BASIC-02 oben im Bild; Prüfung tools/test_ego_glow.py)
        scn = bpy.context.scene
        scn.camera = sc.cam
        scn.render.resolution_x, scn.render.resolution_y = RES
        scn.render.resolution_percentage = 100
        scn.cycles.samples = samples
        still_p = os.path.join(ev, f'_still_{wid}.png')
        scn.render.filepath = still_p
        bpy.ops.render.render(write_still=True)
        scn.render.engine = 'BLENDER_WORKBENCH'                 # Maske aus derselben Szene und Pose: nur Deckung (Alpha)
        scn.render.film_transparent = True
        scn.display.shading.light = 'FLAT'
        scn.display.shading.color_type = 'SINGLE'
        scn.display.render_aa = 'OFF'
        mask_p = os.path.join(ev, f'_mask_{wid}.png')
        scn.render.filepath = mask_p
        bpy.ops.render.render(write_still=True)
        mask = load_png(mask_p)[..., 3] > 0.5
        r = measure(mask)
        ev_p = os.path.join(ev, f'clear_{wid}.png')
        overlay(load_png(still_p), mask, ev_p)
        out[wid] = dict(r, sources_sha256=rules.sha_files(rules.clear_sources(W)), pose='hip', resolution=list(RES),
                        evidence=os.path.relpath(ev_p, os.path.expanduser('~')).join(('~/', '')))
        print(f"[ego_clear] {wid}: Zone {r['zone_px']} px ({r['zone_share'] * 100:.2f} %), oberster Punkt in den Zonenspalten "
              f"{'–' if r['top_y'] is None else format(r['top_y'] * 100, '.1f') + ' % H'} → {ev_p}")
    data = dict(format='cubeescape-ballon/ego-clear', format_version=1, generated_by='tools/ego_clear.py',
                de='Freihaltezone im Hüftbild (A4): belegte Pixel von Waffe und Armen in der Zone (±10 % B um die Bildmitte, obere zwei '
                   'Drittel) bei 1600 × 900; top_y = oberster belegter Punkt in den Zonenspalten (Anteil H von oben), cols = belegte '
                   'Spalten in der Zone (Anteil B). Aktuell, solange sources_sha256 (tools/rules.clear_sources) stimmt.',
                weapons=dict(sorted(out.items())))
    with open(DST, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
        fh.write('\n')


if __name__ == '__main__':
    main()
