"""Bildlage der Ego-Haltungen ohne Blender (0.35 „Stance“): Anker und Fluchtpunkt der Laufachse in % B/H (Ursprung oben links).

  python3 tools/bildlage.py [Klasse|Modul …] [--poses hip,sprint] [--json]

Rechnet wie `tools/ego_build.pose_matrix` (Lage von Socket_Hand, Zielpunkt, Rollen) und projiziert mit der Ego-Kamera (`ego.CAMERA`,
75° horizontal, 16:9; Blick −Y, oben +Z, rechts −X). Der Fluchtpunkt ist das Bild der Laufrichtung (Autorenmaß +f) – so misst Motiongen
REF 0.35 „Backblast“ die Laufneigung (Tabelle C): wohin die Waffe im Bild zeigt. Nur Messung, ändert keine Werte.
"""
import importlib
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic.arms import ego as EG  # noqa: E402

MODULES = ['w01_auto_rifle', 'w06_submachine_gun', 'w03_scout_rifle', 'w02_pulse_rifle', 't01_portal_cannon', 'w04_hand_cannon',
           'w05_sidearm', 'w09_sniper_rifle', 'w12_trace_rifle', 'w15_machine_gun', 'w08_shotgun', 'w10_fusion_rifle',
           'w11_linear_fusion_rifle', 'w07_combat_bow', 'w13_grenade_launcher', 'w14_rocket_launcher']
ANCHORS = ('Socket_Muzzle', 'Socket_Sight', 'Socket_Reticle', 'Socket_Hand', 'Socket_SupportHand')
TX = math.tan(math.radians(EG.CAMERA['h_fov_deg'] / 2))
TY = TX * EG.CAMERA['aspect'][1] / EG.CAMERA['aspect'][0]


def _sub(a, b):
    return [x - y for x, y in zip(a, b)]


def _norm(v):
    n = math.sqrt(sum(x * x for x in v))
    return [x / n for x in v]


def _cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def _rot(axis, deg, v):
    """v um die Einheitsachse axis um deg drehen (Rodrigues, rechtshändig wie mathutils Matrix.Rotation)."""
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    d = sum(a * b for a, b in zip(axis, v))
    cr = _cross(axis, v)
    return [v[i] * c + cr[i] * s + axis[i] * d * (1 - c) for i in range(3)]


def frame(W, P):
    """Basis (links, vorn, oben) der Waffe im Kameraraum und Lage von Socket_Hand wie ego_build.pose_matrix (ohne Versatz)."""
    d = _norm(P['aim_dir']) if 'eye' in P else _norm(_sub(P['aim'], P['pos']))
    up = [0, 0, 1]
    k = sum(a * b for a, b in zip(up, d))
    u = _norm([up[i] - d[i] * k for i in range(3)])
    left = _cross([-x for x in d], u)
    cols = [_rot(d, -P.get('roll', 0), c) for c in (left, [-x for x in d], u)]   # Spalten: lokale +X, +Y, +Z
    if 'eye' in P:
        e = W.ANCHORS['Socket_Eye']['at']
        el = [e[2] / 1000, -e[0] / 1000, e[1] / 1000]
        pos = [P['eye'][i] - sum(cols[j][i] * el[j] for j in range(3)) for i in range(3)]
    else:
        pos = list(P['pos'])
    return cols, pos


def world(cols, pos, fux):
    f, u, x = fux
    loc = [x / 1000, -f / 1000, u / 1000]                 # kit.to_xyz
    return [pos[i] + sum(cols[j][i] * loc[j] for j in range(3)) for i in range(3)]


def pct(p):
    depth = -p[1]
    return [round(50 + 50 * (-p[0] / depth) / TX, 1), round(50 - 50 * (p[2] / depth) / TY, 1)]


def measure(W, pose):
    P = EG.profile(W)['poses'][pose]
    cols, pos = frame(W, P)
    r = {a: pct(world(cols, pos, W.ANCHORS[a]['at'])) for a in ANCHORS if a in W.ANCHORS}
    fwd = [-c for c in cols[1]]                           # Laufrichtung = Autorenmaß +f = lokale −Y
    r['flucht'] = pct(fwd) if fwd[1] < 0 else None        # None: Lauf zeigt nicht nach vorn
    return r


def ray(xy):
    """Blickstrahl (Tiefe 1) durch den Bildpunkt xy in %."""
    return [-(xy[0] - 50) / 50 * TX, -1.0, (50 - xy[1]) / 50 * TY]


def fit(W, pose, muzzle, flucht, roll=None, depth=None):
    """Haltung (pos, aim, roll) rückwärts: Mündung bei `muzzle` %, Laufrichtung zum Fluchtpunkt `flucht` %; Tiefe der Mündung und Rollen
    wie die heutige Haltung, wenn nicht angegeben (Rollen um die Laufachse ändert den Fluchtpunkt nicht)."""
    P = dict(EG.profile(W)['poses'][pose])
    cols, pos = frame(W, P)
    m_now = world(cols, pos, W.ANCHORS['Socket_Muzzle']['at'])
    depth = depth or -m_now[1]
    d = _norm(ray(flucht))
    Q = dict(pos=(0, 0, 0), aim=tuple(d), roll=P.get('roll', 0) if roll is None else roll)
    cols, _ = frame(W, Q)
    mw = [c * depth for c in ray(muzzle)]
    hand = [mw[i] - (world(cols, [0, 0, 0], W.ANCHORS['Socket_Muzzle']['at'])[i]) for i in range(3)]
    aim = [hand[i] + 3.0 * d[i] for i in range(3)]
    return dict(pos=tuple(round(v, 3) for v in hand), aim=tuple(round(v, 3) for v in aim), roll=Q['roll'])


def main():
    a = sys.argv[1:]
    if '--fit' in a:          # --fit <modul> <pose> mx my fx fy [roll] [tiefe]
        i = a.index('--fit')
        W = importlib.import_module(f'basic.pilot.{a[i + 1]}_v21')
        v = [float(x) for x in a[i + 3:]]
        print(fit(W, a[i + 2], v[0:2], v[2:4], *(v[4:6])))
        return
    poses = a[a.index('--poses') + 1].split(',') if '--poses' in a else ['hip']
    names = [x for x in a if not x.startswith('--') and (not a.index(x) or a[a.index(x) - 1] != '--poses')]
    mods = [m for m in MODULES if not names or any(n in m for n in names)]
    out = {}
    for m in mods:
        W = importlib.import_module(f'basic.pilot.{m}_v21')
        t = W.META['type']
        for pose in poses:
            if pose not in EG.profile(W)['poses']:
                continue
            r = out.setdefault(t, {})[pose] = measure(W, pose)
            if '--json' not in a:
                s = '  '.join(f"{k.replace('Socket_', '')} {v[0]:.1f}/{v[1]:.1f}" for k, v in r.items() if v)
                print(f'{t:20s} {pose:7s} {s}')
    if '--json' in a:
        print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
