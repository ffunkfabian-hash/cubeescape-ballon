"""Hintergrundszenen (0.8 „Hangar“): Szenen als Python-Daten, gebaut und gebacken von tools/scene_build.py.

Ein Szenenmodul `basic/scenes/<name>.py` beschreibt: META, ROLES (eigene Umgebungs-Materialrollen, `kit.MATERIALS` bleibt
unberührt), PARTS (Bauteile), LIGHTS, SKY, SPAWN, TARGETS, BAKE. Dieses Modul braucht kein `bpy` (auch `./check` liest es).

Rahmen: Blender-Welt in Metern, Z oben, der Spieler blickt beim Start nach −Y (docs/szenen-format.md).

Bauteil-Formen (alle Maße in Metern, Weltlage; ein Bauteil ist ein Netzstück, `group` ist das FBX-Objekt, in das es geht):
  box   achsparalleler Quader `a`..`b` (Ecken); `skip` lässt unsichtbare Seiten weg ('+x', '-x', '+y', '-y', '+z', '-z'),
        die Unterseite auf dem Boden (z0 = 0) fällt immer weg
  cyl   Zylinder entlang `axis` ('x', 'y', 'z'), Mitte `c`, Radius `r`, Länge `l`, `segs` Seiten (glatt schattiert)
  beam  Vierkant von Punkt `a` nach `b`, Querschnitt `w` (waagerecht quer) × `h`; für Schrägen (Fachwerk, Treppenwangen)
`collide` (Standard: box/cyl ja, beam nein) legt fest, ob das Bauteil einen achsparallelen Kollisionsquader bekommt.
"""
import math

FACES = ('+x', '-x', '+y', '-y', '+z', '-z')


def _part(pid, de, group, mat, shape, collide, **kw):
    p = dict(id=pid, de=de, group=group, mat=mat, shape=shape, collide=collide)
    p.update(kw)
    return p


def box(pid, de, group, mat, a, b, skip=(), collide=True):
    a, b = tuple(float(min(x, y)) for x, y in zip(a, b)), tuple(float(max(x, y)) for x, y in zip(a, b))
    return _part(pid, de, group, mat, 'box', collide, a=a, b=b, skip=tuple(skip))


def cyl(pid, de, group, mat, axis, c, r, l, segs=20, collide=True):
    return _part(pid, de, group, mat, 'cyl', collide, axis=axis, c=tuple(float(x) for x in c), r=float(r), l=float(l), segs=segs)


def beam(pid, de, group, mat, a, b, w, h, collide=False):
    return _part(pid, de, group, mat, 'beam', collide, a=tuple(float(x) for x in a), b=tuple(float(x) for x in b),
                 w=float(w), h=float(h))


AX = {'x': 0, 'y': 1, 'z': 2}


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _norm(a):
    n = math.sqrt(sum(x * x for x in a))
    return tuple(x / n for x in a)


def beam_frame(a, b, w, h):
    """Acht Ecken eines Vierkants von a nach b: Breite w entlang der Waagerechten quer zur Achse, Höhe h senkrecht dazu."""
    d = _sub(b, a)
    dn = _norm(d)
    s = _cross(dn, (0.0, 0.0, 1.0))
    if math.sqrt(sum(x * x for x in s)) < 1e-6:          # senkrecht: Breite entlang X
        s = (1.0, 0.0, 0.0)
    s = _norm(s)
    t = _cross(s, dn)
    pts = []
    for e in (a, b):
        for i, j in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            pts.append(tuple(e[k] + i * s[k] * w / 2 + j * t[k] * h / 2 for k in range(3)))
    return pts


def bounds(p):
    """Achsparallele Grenzen (min, max) eines Bauteils in Weltmetern, ohne Blender."""
    s = p['shape']
    if s == 'box':
        return p['a'], p['b']
    if s == 'cyl':
        i = AX[p['axis']]
        lo = [c - p['r'] for c in p['c']]
        hi = [c + p['r'] for c in p['c']]
        lo[i], hi[i] = p['c'][i] - p['l'] / 2, p['c'][i] + p['l'] / 2
        return tuple(lo), tuple(hi)
    if s == 'beam':
        pts = beam_frame(p['a'], p['b'], p['w'], p['h'])
        return tuple(min(q[k] for q in pts) for k in range(3)), tuple(max(q[k] for q in pts) for k in range(3))
    raise ValueError(f'Form {s} unbekannt')


def validate(S):
    """Strukturprüfung eines Szenenmoduls; gibt eine Liste von Fehlern zurück (leer = in Ordnung)."""
    err = []
    ids = [p['id'] for p in S.PARTS]
    if len(ids) != len(set(ids)):
        dup = sorted({i for i in ids if ids.count(i) > 1})
        err.append(f'doppelte Bauteil-IDs: {dup[:5]}')
    for p in S.PARTS:
        for k in ('de', 'group', 'mat'):
            if not p.get(k):
                err.append(f'{p["id"]}: Feld {k} leer')
        if p['mat'] not in S.ROLES:
            err.append(f'{p["id"]}: Rolle {p["mat"]} fehlt in ROLES')
        if p['shape'] == 'box' and set(p['skip']) - set(FACES):
            err.append(f'{p["id"]}: unbekannte Seite in skip')
        lo, hi = bounds(p)
        if any(h - l <= 0 for l, h in zip(lo, hi)):
            err.append(f'{p["id"]}: leere Ausdehnung')
    for L in S.LIGHTS:
        if L['kind'] not in ('area', 'sun', 'point', 'spot'):
            err.append(f'{L["name"]}: Lichtart {L["kind"]}')
    sx, sy, sz = S.SPAWN['pos']
    for p in S.PARTS:                                  # Startpunkt frei: kein Kollisionsquader im Spielerzylinder (r 0,4, h 1,8)
        if not p['collide']:
            continue
        lo, hi = bounds(p)
        if lo[0] < sx + 0.4 and hi[0] > sx - 0.4 and lo[1] < sy + 0.4 and hi[1] > sy - 0.4 and lo[2] < sz + 1.8 and hi[2] > sz + 0.02:
            err.append(f'Startpunkt nicht frei: {p["id"]}')
    for t in S.TARGETS:                                # Schussbahn frei: nichts zwischen Auge und Scheibe
        e = (sx, sy, sz + 1.62)
        for p in S.PARTS:
            if not p['collide']:
                continue
            lo, hi = bounds(p)
            if _hits(e, t['pos'], lo, hi):
                err.append(f'Schussbahn {t["distance"]} m bei x={t["pos"][0]} verdeckt von {p["id"]}')
                break
    return err


def _hits(a, b, lo, hi):
    """Schneidet die Strecke a→b den Quader (lo, hi)? (Slab-Verfahren)"""
    t0, t1 = 0.0, 1.0
    for k in range(3):
        d = b[k] - a[k]
        if abs(d) < 1e-9:
            if a[k] < lo[k] or a[k] > hi[k]:
                return False
            continue
        u, v = (lo[k] - a[k]) / d, (hi[k] - a[k]) / d
        if u > v:
            u, v = v, u
        t0, t1 = max(t0, u), min(t1, v)
        if t0 > t1:
            return False
    return t1 > 0.0 and t0 < 1.0
