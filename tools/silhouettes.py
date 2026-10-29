"""Schwarze Silhouetten der Stil-v2.1-Familie am gebauten Netz (A1, BALLON 0.30 „Rulebook“; Regel docs/stilhandbuch.md › 2).

  ~/Claude/cubeescape-nexogen/ce lock blender -- /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup \
      -P <repo>/tools/silhouettes.py [-- BASIC-07-v2.1 …]

Baut jede Waffe (kit.build, Ruhelage, alle Teile) und rastert ihre Dreiecke ohne Rendern auf zwei Ebenen: `side` (Seitenansicht, f
nach rechts, u nach oben) und `ego` (Blickrichtung der Ansicht `ego` aus tools/blender_build.VIEWS, links hinten oben). Jede Maske ist
auf COLS Spalten Länge normiert (A-R1: „auf gleiche Länge normiert“), Pixelmitte innerhalb eines Dreiecks = belegt, danach Fugen ≤ 2 px geschlossen. Ausgabe
data/silhouettes.json (lauflängenkodiert, mit parts_sha256 und Dreieckszahl als Aktualitätsschlüssel); ./check rechnet daraus die
paarweise IoU (tools/rules.py). Ohne Argumente alle Waffen, sonst nur die genannten (übrige Einträge bleiben).
"""
import json
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic import kit  # noqa: E402
from tools import rules  # noqa: E402
from tools.blender_build import VIEWS  # noqa: E402
from tools.export_unity import parts_sha  # noqa: E402

COLS = 320
DST = os.path.join(ROOT, 'data', 'silhouettes.json')


def basis(view):
    """Bildachsen (rechts, oben) einer Ansicht: wie blender_build.aim (z = Blick zur Kamera, x = oben × z)."""
    d, up = (Vector(v).normalized() for v in VIEWS[view])
    x = up.cross(d).normalized()
    return x, d.cross(x)


def triangles(objs):
    """Alle Dreiecke (n, 3, 3) der ausgewerteten Netze in Weltkoordinaten (m)."""
    dg = bpy.context.evaluated_depsgraph_get()
    out = []
    for ob in objs:
        e = ob.evaluated_get(dg)
        me = e.to_mesh()
        me.calc_loop_triangles()
        co = np.empty(len(me.vertices) * 3)
        me.vertices.foreach_get('co', co)
        co = co.reshape(-1, 3)
        M = np.array(e.matrix_world)
        co = co @ M[:3, :3].T + M[:3, 3]
        tri = np.empty(len(me.loop_triangles) * 3, dtype=np.int64)
        me.loop_triangles.foreach_get('vertices', tri)
        out.append(co[tri.reshape(-1, 3)])
        e.to_mesh_clear()
    return np.concatenate(out)


def raster(T, ax, ay, cols=COLS, frame=None):
    """Projektion auf (ax, ay), auf cols Spalten Länge normiert; Zeile 0 oben. Gibt (Maske bool[h, w], mm je Pixel).
    frame = (lo, hi) erzwingt einen Bildausschnitt (Fehlersuche an Einzelteilen)."""
    P = np.stack([T @ np.array(ax), T @ np.array(ay)], axis=-1)          # (n, 3, 2)
    lo, hi = frame or (P.reshape(-1, 2).min(0), P.reshape(-1, 2).max(0))
    s = (hi[0] - lo[0]) / cols
    h = int(math.ceil((hi[1] - lo[1]) / s))
    X = (P[..., 0] - lo[0]) / s
    Y = (hi[1] - P[..., 1]) / s                                          # oben = Zeile 0
    m = np.zeros((h, cols), dtype=bool)
    for (x0, x1, x2), (y0, y1, y2) in zip(X, Y):
        i0, i1 = int(math.ceil(min(x0, x1, x2) - 0.5)), int(math.floor(max(x0, x1, x2) - 0.5))
        j0, j1 = int(math.ceil(min(y0, y1, y2) - 0.5)), int(math.floor(max(y0, y1, y2) - 0.5))
        i0, j0, i1, j1 = max(i0, 0), max(j0, 0), min(i1, cols - 1), min(j1, h - 1)
        if i1 < i0 or j1 < j0:
            continue
        d = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        if abs(d) < 1e-12:
            continue
        gx, gy = np.meshgrid(np.arange(i0, i1 + 1) + 0.5, np.arange(j0, j1 + 1) + 0.5)
        a = ((x1 - gx) * (y2 - gy) - (x2 - gx) * (y1 - gy)) / d
        b = ((x2 - gx) * (y0 - gy) - (x0 - gx) * (y2 - gy)) / d
        inside = (a >= -1e-9) & (b >= -1e-9) & (1 - a - b >= -1e-9)
        m[j0:j1 + 1, i0:i1 + 1] |= inside
    return m, s * 1000


def close(m, r=1):
    """Morphologisches Schließen mit Radius r px (3 × 3 je Schritt): Fugen ≤ 2 r px zwischen Teilen, die sich nur berühren, zählen
    zur Silhouette (Lesbarkeit auf Distanz); größere Öffnungen (Abzugsbügel, Durchbrüche) bleiben."""
    def grow(a, op):
        p = np.pad(a, 1, constant_values=(op is np.logical_and))
        out = p[1:-1, 1:-1].copy()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                out = op(out, p[1 + dy:p.shape[0] - 1 + dy, 1 + dx:p.shape[1] - 1 + dx])
        return out
    for _ in range(r):
        m = grow(m, np.logical_or)
    for _ in range(r):
        m = grow(m, np.logical_and)
    return m


def rle(m):
    out = []
    for r in m:
        d = np.diff(np.concatenate([[0], r.astype(np.int8), [0]]))
        out.append([int(v) for v in np.column_stack([np.flatnonzero(d == 1), np.flatnonzero(d == -1)]).ravel()])
    return dict(w=int(m.shape[1]), h=int(m.shape[0]), rows=out)


def main():
    want = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    data = json.load(open(DST, encoding='utf-8')) if os.path.exists(DST) else {}
    old = data.get('weapons', {})
    W_ = {}
    for wid, W in rules.family():
        if want and wid not in want:
            W_[wid] = old.get(wid)
            continue
        kit.reset_scene()
        root, objs, anchors = kit.build(W)
        bpy.context.view_layer.update()
        T = triangles(objs.values())
        side, s_mm = raster(T, (0, -1, 0), (0, 0, 1))              # f = −Y nach rechts, u = Z nach oben
        ex, ey = basis('ego')
        ego, e_mm = raster(T, tuple(ex), tuple(ey))
        W_[wid] = dict(parts_sha256=parts_sha(W), triangles=int(len(T)), mm_per_px=dict(side=round(s_mm, 3), ego=round(e_mm, 3)),
                       side=rle(close(side)), ego=rle(close(ego)))
        print(f'[silhouettes] {wid}: {len(T)} Dreiecke, Seite {side.shape[1]}×{side.shape[0]} ({s_mm:.2f} mm/px), '
              f'Ego {ego.shape[1]}×{ego.shape[0]}')
    data = dict(format='cubeescape-ballon/silhouettes', format_version=1, generated_by='tools/silhouettes.py', columns=COLS,
                de='Schwarze Silhouetten je Waffe der Stil-v2.1-Familie, auf gleiche Länge normiert (A1, Stilhandbuch › 2); rows = '
                   'je Bildzeile von oben [Beginn, Ende, …] belegter Spalten. side: Seitenansicht (Mündung rechts); ego: Ansicht ego '
                   '(von links hinten oben). Aktuell, solange parts_sha256 (tools/export_unity.parts_sha) und die Dreieckszahl des '
                   'Specs stimmen.',
                weapons={k: v for k, v in W_.items() if v is not None})
    with open(DST, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, ensure_ascii=False, separators=(',', ':'))
        fh.write('\n')
    print(f'[silhouettes] {len(data["weapons"])} Waffen → {DST}')


if __name__ == '__main__':
    main()
