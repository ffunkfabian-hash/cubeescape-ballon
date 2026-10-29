"""Formstudien für die Ego-Arme (0.23 „Gauntlet“): drei Richtungen auf dem Skelett von Arm v3.

Jede Studie übernimmt Längen, Handfläche, Fingerlagen und Fingerstellungen aus `basic/arms/robot_arm.py`, damit Griffe und
Aktionen unverändert passen; neu ist nur `parts()` mit den Formen aus `basic/arms/forms.py`. Rendern:

  blender -b --factory-startup -P tools/arm_preview.py -- --rig studies.<name> --tag <name> [--gpu]
  blender -b --factory-startup -P tools/ego_build.py -- --rig studies.<name> --stills --poses hip,inspect_l [--gpu]
"""
from basic.arms import robot_arm as V3
from basic.arms.forms import sec

PALM_W, PALM_T, PALM_START, PALM_LEN = V3.PALM_W, V3.PALM_T, V3.PALM_START, V3.PALM_LEN
KNUCKLE_Z, FINGER_X, FINGER_W, FINGER_D = V3.KNUCKLE_Z, V3.FINGER_X, V3.FINGER_W, V3.FINGER_D
FINGER_LINKS, FINGER_SCALE, THUMB_BASE, THUMB_LINKS = V3.FINGER_LINKS, V3.FINGER_SCALE, V3.THUMB_BASE, V3.THUMB_LINKS


def skeleton(ns):
    """Skelett von Arm v3 in den Namensraum einer Studie übernehmen (alles außer parts)."""
    for k in dir(V3):
        if k.isupper() and k not in ns:
            ns[k] = getattr(V3, k)


def loft(pid, de, seg, role, secs, **kw):
    return (pid, de, seg, 'loft', role, dict(secs=secs, **kw))


def wrap(pid, de, seg, role, secs, a0, a1, t, **kw):
    return (pid, de, seg, 'wrap', role, dict(secs=secs, a0=a0, a1=a1, t=t, **kw))


def tube(pid, de, seg, role, path, r, **kw):
    return (pid, de, seg, 'tube', role, dict(path=path, r=r, **kw))


def cyl(pid, de, seg, role, axis, r, ln, c, **kw):
    return (pid, de, seg, 'cyl', role, dict(axis=axis, r=r, len=ln, c=c, **kw))


def box(pid, de, seg, role, d, c, bevel=3, **kw):
    return (pid, de, seg, 'box', role, dict(d=d, c=c, bevel=bevel, **kw))


def tab(table):
    """Querschnitt aus einer Tabelle [(z, a, b, y) …] linear abgreifen: f(z, grow=0, **extra) → sec."""
    pairs = list(zip(table, table[1:]))

    def f(z, grow=0.0, n=2.6, **extra):
        (z0, a0, b0, y0), (z1, a1, b1, y1) = next((p for p in pairs if z <= p[1][0]), pairs[-1])
        u = max(0.0, min(1.0, (z - z0) / (z1 - z0)))
        return sec(z, a0 + (a1 - a0) * u + grow, b0 + (b1 - b0) * u + grow, y0 + (y1 - y0) * u, n=n, **extra)
    return f


def bulk(P, k, segs=('upper', 'fore')):
    """Querschnitt von Ober- und Unterarm um k vergrößern (wie Arm v3 ARM_BULK): Querschnitte, Leitungen, Mittelpunkte und
    Radien quer zum Glied; Längen in z und Plattendicken bleiben. In der Ego-Kamera trägt der Unterarm das Bild."""
    out = []
    for pid, de, seg, kind, role, p in P:
        if seg in segs:
            p = dict(p)
            if 'secs' in p:
                p['secs'] = [dict(s, a=s['a'] * k, b=s['b'] * k, x=s['x'] * k, y=s['y'] * k) for s in p['secs']]
            if 'path' in p:
                p['path'] = [(x * k, y * k, z) for x, y, z in p['path']]
            if 'c' in p:
                p['c'] = (p['c'][0] * k, p['c'][1] * k, p['c'][2])
            if 'cuts' in p:
                p['cuts'] = [dict(c, c=(c['c'][0] * k, c['c'][1] * k, c['c'][2])) for c in p['cuts']]
            if kind == 'cyl':
                p['r'] = p['r'] * (k if p['axis'] != 'y' else 1)
                p['len'] = p['len'] * (k if p['axis'] != 'z' else 1)
        out.append((pid, de, seg, kind, role, p))
    return out


def link_len(i, j):
    return FINGER_LINKS[j] * FINGER_SCALE[i]


def digits():
    """Alle Fingerglieder als (Segment, Länge, ist_Spitze, ist_Daumen)."""
    out = [(f'f{i}_{j}', link_len(i, j), j == len(FINGER_LINKS) - 1, False)
           for i in range(len(FINGER_X)) for j in range(len(FINGER_LINKS))]
    out += [(f't_{j}', L, j == len(THUMB_LINKS) - 1, True) for j, L in enumerate(THUMB_LINKS)]
    return out
