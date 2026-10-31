"""Bildanteil im Ego-Bild (Messung für Motiongen REF 0.35 „Backblast“, Tabelle F): bedeckte Pixel von Waffe + Händen/Armen in % der
Bildfläche, dazu Box [xmin, ymin, xmax, ymax] in % B/H (Ursprung oben links, 100 = vom Bildrand abgeschnitten). Nur Messung.

  blender -b --factory-startup -P <abs>/tools/bildanteil.py -- [--weapons pilot.w01_auto_rifle_v21,…] [--poses hip,ads]
                                                               [--out <datei.json>] [--png <ordner>]

Je spielbarer Waffe (tools/export_unity.WEAPONS, ohne --weapons alle 16) und Haltung das Ego-Standbild wie `tools/ego_build.py --stills`
(`still_action`: Hände wie in der Aktion idle_hip bzw. am Ende von aim_in, Bogen mit eigener Zielhaltung, Portalkanone nur Hüfte),
ohne Mündungsfeuer und Hülsen, im Zielen mit den Ausblendungen `ads_hide` wie in `evaluate`. Aus derselben Szene und Pose eine
Workbench-Maske (flach, ohne Kantenglättung, Alpha) bei 1920 × 1080 (16:9, Bildwinkel `ego.CAMERA`, 75° horizontal).
Glasteile (Materialrolle `glass*`, Visierfenster, Kernglas) und Absehen (`reticle_*`, `sight_line`) werden für die Maske ausgeblendet:
durch sie sieht man hindurch. Zum Vergleich steht `pct_mit_glas` (Glas eingeblendet) daneben. Ausgabe JSON je Waffe/Haltung
(`pct`, `box`, `px`, `pct_mit_glas`, `ausgeblendet`) und je Maske ein PNG (weiß = bedeckt) in --png; die Zählung geschieht an der
Maske in voller Auflösung, nie an einer verkleinerten.
"""
import importlib
import json
import os
import sys

import bpy
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools import ego_build as EB  # noqa: E402
from tools.export_unity import WEAPONS  # noqa: E402

RES = (1920, 1080)
SEE_THROUGH = ('glass', 'reticle_', 'sight_line')       # Rollen (Anfang des Namens), durch die man hindurchsieht


def args():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []

    def val(k):
        return a[a.index(k) + 1] if k in a else None
    return dict(weapons=(val('--weapons').split(',') if val('--weapons') else WEAPONS),
                poses=(val('--poses') or 'hip,ads').split(','), out=val('--out'), png=val('--png'))


def mask_now():
    """Workbench-Renderung der aktuellen Szene: Alpha > 0,5 = bedeckt (bool-Feld, Zeile 0 oben)."""
    scn = bpy.context.scene
    path = os.path.join(bpy.app.tempdir, 'bildanteil_mask.png')
    scn.render.filepath = path
    bpy.ops.render.render(write_still=True)
    im = bpy.data.images.load(path)
    w, h = im.size
    px = np.empty(w * h * 4, dtype=np.float32)
    im.pixels.foreach_get(px)
    bpy.data.images.remove(im)
    return px.reshape(h, w, 4)[::-1][..., 3] > 0.5


def save_mask(mask, path):
    h, w = mask.shape
    g = mask.astype(np.float32)
    rgba = np.stack([g, g, g, np.ones_like(g)], axis=-1)
    im = bpy.data.images.new('bildanteil', w, h, alpha=True)
    im.colorspace_settings.name = 'Non-Color'
    im.pixels.foreach_set(np.ascontiguousarray(rgba[::-1]).ravel())
    im.filepath_raw = path
    im.file_format = 'PNG'
    im.save()
    bpy.data.images.remove(im)


def measure(mask):
    h, w = mask.shape
    n = int(mask.sum())
    if not n:
        return dict(px=0, pct=0.0, box=None)
    cols = np.flatnonzero(mask.any(axis=0))
    rows = np.flatnonzero(mask.any(axis=1))
    box = [cols[0] / w * 100, rows[0] / h * 100, (cols[-1] + 1) / w * 100, (rows[-1] + 1) / h * 100]
    return dict(px=n, pct=round(n / (w * h) * 100, 2), box=[round(float(v), 1) for v in box])


def see_through(sc):
    """Objekte der Szene (Waffe), deren Materialrolle Glas oder Absehen ist."""
    out = []
    for pid, ob in sc.objs.items():
        role = ob.data.materials[0].get('basic_role', '') if ob.data.materials else ''
        if role.startswith(SEE_THROUGH):
            out.append((pid, role, ob))
    return out


def main():
    o = args()
    res, scn = {}, bpy.context.scene
    for m in o['weapons']:
        W = importlib.import_module(f'basic.{m}')
        wid = f"{W.META['id']}-{W.META['variant']}"
        sc = EB.Scene(W, dict(gpu=False, samples=1, fx=False))
        scn = bpy.context.scene
        scn.camera = sc.cam
        scn.render.engine = 'BLENDER_WORKBENCH'
        scn.render.film_transparent = True
        scn.render.resolution_x, scn.render.resolution_y = RES
        scn.render.resolution_percentage = 100
        scn.display.shading.light = 'FLAT'
        scn.display.shading.color_type = 'SINGLE'
        scn.display.render_aa = 'OFF'
        scn.render.image_settings.file_format = 'PNG'
        scn.render.image_settings.color_mode = 'RGBA'
        res[wid] = dict(typ=W.META['type'], poses={})
        for pose in o['poses']:
            if pose not in sc.P['poses']:
                res[wid]['poses'][pose] = None            # Haltung gibt es für diese Klasse nicht (Portalkanone: kein ads)
                print(f'[bildanteil] {wid} {pose}: keine Haltung', flush=True)
                continue
            rep = {}
            EB.evaluate(sc, EB.still_action(sc.P, pose), 0, rep, {})
            bpy.context.view_layer.update()
            st = see_through(sc)
            h0 = [ob.hide_render for _, _, ob in st]     # Zustand aus evaluate (ads_hide); Richter 0.35: Glas im Zielen nicht einblenden
            with_glass = measure(mask_now())
            for _, _, ob in st:
                ob.hide_render = True
            mask = mask_now()
            for (_, _, ob), h in zip(st, h0):
                ob.hide_render = h
            r = measure(mask)
            r.update(pct_mit_glas=with_glass['pct'], ausgeblendet=sorted(f'{pid}:{role}' for pid, role, _ in st),
                     ads_hide_aktiv=bool(rep.get('ads_hidden')))
            res[wid]['poses'][pose] = r
            if o['png']:
                os.makedirs(o['png'], exist_ok=True)
                save_mask(mask, os.path.join(o['png'], f'{wid}_{pose}.png'))
            print(f"[bildanteil] {wid} {pose}: {r['pct']} % Box {r['box']} (mit Glas {r['pct_mit_glas']} %)", flush=True)
    if o['out']:
        os.makedirs(os.path.dirname(os.path.abspath(o['out'])), exist_ok=True)
        json.dump(dict(auflösung=list(RES), bildwinkel_h_deg=EB.EG.CAMERA['h_fov_deg'], weapons=res),
                  open(o['out'], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
