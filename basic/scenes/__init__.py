"""Hintergrundszenen (0.9 „Parcours“): Szenen als Python-Daten, gebaut und gebacken von tools/scene_build.py.

Ein Szenenmodul `basic/scenes/<name>.py` beschreibt: META, ROLES (eigene Umgebungs-Materialrollen, `kit.MATERIALS` bleibt
unberührt), DECALS (Bildmasken: Markierungen, Flecken, Schilder), PARTS (Bauteile), ZONES (Atlanten), LIGHTINGS (Lichtszenen),
SPAWN, COURSE (Parcours), REFERENCE, BAKE. Dieses Modul braucht kein `bpy` und kein numpy (auch `./check` liest es).

Rahmen: Blender-Welt in Metern, Z oben, der Spieler blickt beim Start nach −Y (docs/szenen-format.md).

Bauteil-Formen (alle Maße in Metern, Weltlage; ein Bauteil ist ein Netzstück, `group` ist das FBX-Objekt, in das es geht):
  box    achsparalleler Quader `a`..`b` (Ecken); `skip` lässt unsichtbare Seiten weg ('+x', '-x', '+y', '-y', '+z', '-z'),
         die Unterseite auf dem Boden (z0 = 0) fällt immer weg
  cyl    Zylinder entlang `axis` ('x', 'y', 'z'), Mitte `c`, Radius `r`, Länge `l`, `segs` Seiten (glatt schattiert)
  beam   Vierkant von Punkt `a` nach `b`, Querschnitt `w` (waagerecht quer) × `h`; für Schrägen (Fachwerk, Treppenwangen)
  corr   Trapezblech als echte Geometrie: sichtbare Seite `side` (±1) entlang Achse `n`, Vorderfläche (Hochsicke) bei `at`,
         Profil entlang `u` (Teilung, Tiefe, Sicke, Flanke in `prof`), gerade entlang der dritten Achse `v`; einseitig
  solid  nur Kollisionsquader (kein Netz), z. B. als Ersatz für viele kleine sichtbare Teile
`bev` ist die Fasenbreite (m) aller Kanten über 30°; ohne Angabe nach Größe (`bevel_of`), 0 = scharf.
`collide` (Standard: box/cyl/corr ja, beam nein) legt fest, ob das Bauteil einen achsparallelen Kollisionsquader bekommt.
"""
import math

FACES = ('+x', '-x', '+y', '-y', '+z', '-z')
AX = {'x': 0, 'y': 1, 'z': 2}

# Spielerwerte aus unity/Assets/Ballon/Runtime/EgoPlayer.cs › MoveTuning (Prüfung des Parcours)
PLAYER = dict(height=1.8, crouch_height=1.15, radius=0.32, step=0.35, jump_speed=5.0, gravity=16.0, eye=1.62, crouch_eye=1.0,
              walk=4.2, sprint=6.8, crouch=2.4)
PLAYER['jump_h'] = PLAYER['jump_speed'] ** 2 / (2 * PLAYER['gravity'])          # 0,78 m
LIMITS = dict(passage_m=0.7, duck_lo=1.2, duck_hi=1.6, jump_step=0.75, stair_step=0.35)


def _part(pid, de, group, mat, shape, collide, bev, **kw):
    p = dict(id=pid, de=de, group=group, mat=mat, shape=shape, collide=collide, bev=bev, mesh=True)
    p.update(kw)
    return p


def box(pid, de, group, mat, a, b, skip=(), collide=True, bev=None):
    a, b = tuple(float(min(x, y)) for x, y in zip(a, b)), tuple(float(max(x, y)) for x, y in zip(a, b))
    return _part(pid, de, group, mat, 'box', collide, bev, a=a, b=b, skip=tuple(skip))


def cyl(pid, de, group, mat, axis, c, r, l, segs=16, collide=True, bev=None, caps='both'):
    """`caps`: 'both', 'top' (nur +Achse), 'bottom', 'none' – verdeckte Deckel weglassen (sparen Atlasplatz)."""
    return _part(pid, de, group, mat, 'cyl', collide, bev, axis=axis, c=tuple(float(x) for x in c), r=float(r), l=float(l), segs=segs,
                 caps=caps)


def beam(pid, de, group, mat, a, b, w, h, collide=False, bev=None, ends=True):
    """`ends=False`: Stirnflächen weglassen (stecken in Gurten oder Wänden)."""
    return _part(pid, de, group, mat, 'beam', collide, bev, a=tuple(float(x) for x in a), b=tuple(float(x) for x in b),
                 w=float(w), h=float(h), ends=ends)


def corr(pid, de, group, mat, n, side, at, u, u0, u1, v0, v1, prof, collide=True):
    """Trapezblech: Vorderfläche bei `at` (Achse n), sichtbar nach `side`, Rücken `prof['depth']` dahinter."""
    v = [k for k in 'xyz' if k not in (n, u)][0]
    return _part(pid, de, group, mat, 'corr', collide, 0.0, n=n, side=int(side), at=float(at), u=u, v=v,
                 u0=float(min(u0, u1)), u1=float(max(u0, u1)), v0=float(min(v0, v1)), v1=float(max(v0, v1)), prof=dict(prof))


def solid(pid, de, a, b, surface=''):
    """Nur Kollisionsquader (kein Netz). `surface` (0.39): Untergrund für Einschläge (ego.IMPACT_SURFACES), sonst keiner."""
    p = box(pid, de, '-', '-', a, b)
    p['mesh'] = False
    if surface:
        p['surface'] = surface
    return p


def surface_of(S, p):
    """Untergrund eines Teils für Einschläge (0.39 „Scatter“): am Teil angegeben (Kollisionsquader), sonst aus seiner Materialrolle
    (S.SURFACES: Art → Rollen); '' = keiner (der Einschlag gilt unverändert)."""
    if p.get('surface'):
        return p['surface']
    return next((k for k, roles in getattr(S, 'SURFACES', {}).items() if p['mat'] in roles), '')


def bevel_of(p):
    """Fasenbreite in m: angegeben oder nach der kleinsten Abmessung (≈ 15 %, 5–20 mm, unter 4 cm keine)."""
    if p.get('bev') is not None:
        return p['bev']
    s = p['shape']
    if s == 'box':
        d = min(y - x for x, y in zip(p['a'], p['b']))
    elif s == 'beam':
        d = min(p['w'], p['h'])
    else:                         # Zylinder glatt schattiert, ohne Fase (Fasenringe zerfallen im Atlas in viele Bogeninseln)
        return 0.0
    if d < 0.04:
        return 0.0
    return round(min(0.02, max(0.005, 0.15 * d)), 4)


def corr_profile(u0, u1, prof):
    """Knickpunkte (u, Rücksprung) des Trapezprofils zwischen u0 und u1; Phase im Weltraum (Nachbarfelder passen)."""
    T, D, c, f = prof['period'], prof['depth'], prof['crest'], prof['flank']
    b = T - c - 2 * f
    keys = [(0.0, D), (b, D), (b + f, 0.0), (b + f + c, 0.0), (T, D)]      # Tiefsicke, Flanke, Hochsicke, Flanke

    def depth_at(u):
        t = u - math.floor(u / T) * T
        for (ta, da), (tb, db) in zip(keys, keys[1:]):
            if ta <= t <= tb:
                return da if tb == ta else da + (db - da) * (t - ta) / (tb - ta)
        return D
    pts = [u0]
    k0 = math.floor(u0 / T)
    k = k0
    while True:
        base = k * T
        for t, _ in keys:
            u = base + t
            if u0 + 1e-6 < u < u1 - 1e-6:
                pts.append(u)
        if base > u1:
            break
        k += 1
    pts.append(u1)
    pts = sorted(set(round(x, 6) for x in pts))
    return [(u, depth_at(u)) for u in pts]


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
    if s == 'corr':
        lo, hi = [0.0] * 3, [0.0] * 3
        n, u, v = AX[p['n']], AX[p['u']], AX[p['v']]
        back = p['at'] - p['side'] * p['prof']['depth']
        lo[n], hi[n] = min(p['at'], back), max(p['at'], back)
        lo[u], hi[u] = p['u0'], p['u1']
        lo[v], hi[v] = p['v0'], p['v1']
        return tuple(lo), tuple(hi)
    raise ValueError(f'Form {s} unbekannt')


# ------------------------------------------------------------------ Strichschrift für Schilder und Bodenmarkierungen
# Zeichen im Raster 4 × 6 (Großbuchstaben, y nach oben), Linienzüge; Breite `w` bestimmt den Vorschub (w + 1,6).
_O = [(1, 0), (0, 1), (0, 5), (1, 6), (3, 6), (4, 5), (4, 1), (3, 0), (1, 0)]
_P = [(0, 0), (0, 6), (3, 6), (4, 5), (4, 4), (3, 3), (0, 3)]
GLYPHS = {
    'A': [[(0, 0), (2, 6), (4, 0)], [(0.75, 2.2), (3.25, 2.2)]],
    'B': [[(0, 0), (0, 6), (3, 6), (4, 5), (4, 4), (3, 3), (0, 3)], [(3, 3), (4, 2), (4, 1), (3, 0), (0, 0)]],
    'C': [[(4, 5), (3, 6), (1, 6), (0, 5), (0, 1), (1, 0), (3, 0), (4, 1)]],
    'D': [[(0, 0), (0, 6), (2.5, 6), (4, 4.5), (4, 1.5), (2.5, 0), (0, 0)]],
    'E': [[(4, 6), (0, 6), (0, 0), (4, 0)], [(0, 3), (3, 3)]],
    'F': [[(4, 6), (0, 6), (0, 0)], [(0, 3), (3, 3)]],
    'G': [[(4, 5), (3, 6), (1, 6), (0, 5), (0, 1), (1, 0), (3, 0), (4, 1), (4, 3), (2.2, 3)]],
    'H': [[(0, 0), (0, 6)], [(4, 0), (4, 6)], [(0, 3), (4, 3)]],
    'I': [[(0, 0), (0, 6)]],
    'K': [[(0, 0), (0, 6)], [(4, 6), (0, 2)], [(1.3, 3.3), (4, 0)]],
    'L': [[(0, 6), (0, 0), (4, 0)]],
    'M': [[(0, 0), (0, 6), (2, 3), (4, 6), (4, 0)]],
    'N': [[(0, 0), (0, 6), (4, 0), (4, 6)]],
    'O': [_O],
    'Ö': [_O, [(1.3, 7.4), (1.3, 7.5)], [(2.7, 7.4), (2.7, 7.5)]],
    'P': [_P],
    'R': [_P, [(2, 3), (4, 0)]],
    'S': [[(4, 5), (3, 6), (1, 6), (0, 5), (0, 4), (1, 3), (3, 3), (4, 2), (4, 1), (3, 0), (1, 0), (0, 1)]],
    'T': [[(0, 6), (4, 6)], [(2, 6), (2, 0)]],
    'U': [[(0, 6), (0, 1), (1, 0), (3, 0), (4, 1), (4, 6)]],
    'V': [[(0, 6), (2, 0), (4, 6)]],
    'W': [[(0, 6), (1, 0), (2, 4), (3, 0), (4, 6)]],
    'X': [[(0, 0), (4, 6)], [(0, 6), (4, 0)]],
    'Z': [[(0, 6), (4, 6), (0, 0), (4, 0)]],
    '0': [_O, [(0.6, 1), (3.4, 5)]],
    '1': [[(0.8, 4.8), (2, 6), (2, 0)], [(0.8, 0), (3.2, 0)]],
    '2': [[(0, 5), (1, 6), (3, 6), (4, 5), (4, 4), (0, 0), (4, 0)]],
    '3': [[(0, 5), (1, 6), (3, 6), (4, 5), (4, 4), (3, 3), (1.5, 3)], [(3, 3), (4, 2), (4, 1), (3, 0), (1, 0), (0, 1)]],
    '4': [[(3, 0), (3, 6), (0, 2), (4, 2)]],
    '5': [[(4, 6), (0, 6), (0, 3.5), (3, 3.5), (4, 2.5), (4, 1), (3, 0), (1, 0), (0, 1)]],
    '6': [[(4, 5), (3, 6), (1, 6), (0, 5), (0, 1), (1, 0), (3, 0), (4, 1), (4, 2.5), (3, 3.5), (1, 3.5), (0, 2.5)]],
    '7': [[(0, 6), (4, 6), (1.5, 0)]],
    '8': [[(1, 3), (0, 4), (0, 5), (1, 6), (3, 6), (4, 5), (4, 4), (3, 3), (1, 3), (0, 2), (0, 1), (1, 0), (3, 0), (4, 1),
           (4, 2), (3, 3)]],
    '9': [[(0, 1), (1, 0), (3, 0), (4, 1), (4, 5), (3, 6), (1, 6), (0, 5), (0, 3.5), (1, 2.5), (3, 2.5), (4, 3.5)]],
    ',': [[(0.4, 0.3), (0, -1)]],
    '.': [[(0.2, 0), (0.2, 0.1)]],
    '-': [[(0.5, 3), (3.5, 3)]],
    '>': [[(0, 3), (4, 3)], [(2.2, 5), (4.2, 3), (2.2, 1)]],        # Pfeil (Fluchtweg)
    '<': [[(0, 3), (4, 3)], [(1.8, 5), (-0.2, 3), (1.8, 1)]],
    ' ': [],
}
GLYPH_W = {'I': 0.0, ',': 0.4, '.': 0.2, ' ': 2.0, '1': 3.2}


def text_strokes(s, height, u0=0.0, v0=0.0, align='left'):
    """Strichschrift: Liste von Linienzügen [(u, v), …] in Metern, Grundlinie v0, Versalhöhe `height`."""
    k = height / 6.0
    adv = [(GLYPH_W.get(ch, 4.0) + 1.6) * k for ch in s]
    total = sum(adv) - 1.6 * k
    x = u0 - (total / 2 if align == 'center' else total if align == 'right' else 0.0)
    out = []
    for ch, a in zip(s, adv):
        for line in GLYPHS[ch]:
            out.append([(x + px * k, v0 + py * k) for px, py in line])
        x += a
    return out


# ------------------------------------------------------------------ Prüfung
def validate(S):
    """Strukturprüfung eines Szenenmoduls; gibt eine Liste von Fehlern zurück (leer = in Ordnung)."""
    err = []
    ids = [p['id'] for p in S.PARTS]
    if len(ids) != len(set(ids)):
        dup = sorted({i for i in ids if ids.count(i) > 1})
        err.append(f'doppelte Bauteil-IDs: {dup[:5]}')
    zone_of = {}
    for z in S.ZONES:
        for g in z['groups']:
            if g in zone_of:
                err.append(f'Gruppe {g} in zwei Zonen')
            zone_of[g] = z['name']
    for p in S.PARTS:
        if p['mesh']:
            for k in ('de', 'group', 'mat'):
                if not p.get(k):
                    err.append(f'{p["id"]}: Feld {k} leer')
            if p['mat'] not in S.ROLES:
                err.append(f'{p["id"]}: Rolle {p["mat"]} fehlt in ROLES')
            if p['group'] not in zone_of:
                err.append(f'{p["id"]}: Gruppe {p["group"]} in keiner Zone')
        if p['shape'] == 'box' and set(p['skip']) - set(FACES):
            err.append(f'{p["id"]}: unbekannte Seite in skip')
        lo, hi = bounds(p)
        if any(h - l <= 0 for l, h in zip(lo, hi)):
            err.append(f'{p["id"]}: leere Ausdehnung')
    for r, R in S.ROLES.items():
        if R.get('decal') and R['decal'] not in S.DECALS:
            err.append(f'Rolle {r}: Bildmaske {R["decal"]} fehlt in DECALS')
    for k, roles in getattr(S, 'SURFACES', {}).items():
        err += [f'Untergrund {k}: Rolle {r} fehlt in ROLES' for r in roles if r not in S.ROLES]
    for L in S.LIGHTINGS:
        for lt in L['lights']:
            if lt['kind'] not in ('area', 'sun', 'point', 'spot'):
                err.append(f'{L["name"]}/{lt["name"]}: Lichtart {lt["kind"]}')
        for r in L.get('emit', {}):
            if r not in S.ROLES:
                err.append(f'{L["name"]}: Leuchtrolle {r} fehlt in ROLES')
    sx, sy, sz = S.SPAWN['pos']
    for p in S.PARTS:                                  # Startpunkt frei: kein Kollisionsquader im Spielerzylinder (r 0,4, h 1,8)
        if not p['collide']:
            continue
        lo, hi = bounds(p)
        if lo[0] < sx + 0.4 and hi[0] > sx - 0.4 and lo[1] < sy + 0.4 and hi[1] > sy - 0.4 and lo[2] < sz + 1.8 and hi[2] > sz + 0.02:
            err.append(f'Startpunkt nicht frei: {p["id"]}')
    if getattr(S, 'COURSE', None):
        e, _ = course_check(S)
        err += e
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


class _Grid:
    """Kollisionsquader in 2-m-Feldern (Draufsicht) für schnelle Abfragen ohne numpy."""

    def __init__(self, boxes, cell=2.0):
        self.b, self.c, self.cells = boxes, cell, {}
        for i, (lo, hi) in enumerate(boxes):
            for gx in range(math.floor(lo[0] / cell), math.floor(hi[0] / cell) + 1):
                for gy in range(math.floor(lo[1] / cell), math.floor(hi[1] / cell) + 1):
                    self.cells.setdefault((gx, gy), []).append(i)

    def near(self, x0, y0, x1, y1):
        out = set()
        c = self.c
        for gx in range(math.floor(min(x0, x1) / c), math.floor(max(x0, x1) / c) + 1):
            for gy in range(math.floor(min(y0, y1) / c), math.floor(max(y0, y1) / c) + 1):
                out.update(self.cells.get((gx, gy), ()))
        return out

    def along(self, a, b, m=0.9):
        """Quader in den Feldern entlang der Strecke a→b (je 1 m eine Stichprobe, Rand m)."""
        n = max(1, int(math.dist(a[:2], b[:2]) / 1.0))
        cand = set()
        for i in range(n + 1):
            t = i / n
            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            cand |= self.near(x - m, y - m, x + m, y + m)
        return [self.b[i] for i in cand if _hits(a, b, (self.b[i][0][0] - m, self.b[i][0][1] - m, self.b[i][0][2] - m),
                                                 (self.b[i][1][0] + m, self.b[i][1][1] + m, self.b[i][1][2] + m))]


def course_boxes(S):
    return [bounds(p) for p in S.PARTS if p['collide']]


def course_check(S):
    """Parcours begehbar? Prüft entlang `COURSE['route']` (Abschnittsart je Punkt): Durchgang ≥ 0,7 m (Quadrat 0,7 m frei bis
    Kopfhöhe), Stufen beim Gehen/Treppe ≤ 0,35 m, Sprungstufen ≤ 0,75 m, Duckstellen 1,2–1,6 m, Tore und Kontrollpunkte in
    Reihenfolge auf der Strecke, jede Zielscheibe von der Strecke sichtbar (`vis`: 'frei', 'deckung' teilverdeckt, 'oben' nur von
    erhöhten Punkten). Gibt (Fehler, Kennzahlen) zurück."""
    C = S.COURSE
    P = PLAYER
    err = []
    boxes = course_boxes(S)
    G = _Grid(boxes)
    half = LIMITS['passage_m'] / 2
    route = C['route']

    def ground(x, y, zref):
        """Höchste Oberkante unter (x, y), die von zref aus erreichbar ist (Boden 0)."""
        g = 0.0
        for i in G.near(x, y, x, y):
            lo, hi = boxes[i]
            if lo[0] <= x <= hi[0] and lo[1] <= y <= hi[1] and hi[2] <= zref + 1e-6 and hi[2] > g:
                g = hi[2]
        return g

    def blockers(x, y, z0, z1):
        out = []
        for i in G.near(x - half, y - half, x + half, y + half):
            lo, hi = boxes[i]
            if lo[0] < x + half and hi[0] > x - half and lo[1] < y + half and hi[1] > y - half and lo[2] < z1 and hi[2] > z0:
                out.append(i)
        return out

    length = dict(run=0.0, duck=0.0, stairs=0.0, jump=0.0, drop=0.0)
    counts = dict(jump=0, drop=0, duck=0, stairs=0)
    duck_min = []
    names = [p['id'] for p in S.PARTS if p['collide']]
    for k in range(len(route) - 1):
        (ax, ay, az, kind), (bx, by, bz, _) = route[k], route[k + 1]
        seg = math.dist((ax, ay, az), (bx, by, bz))
        length[kind] += seg
        if kind in counts:
            counts[kind] += 1
        for (x, y, z), lab in (((ax, ay, az), 'Anfang'), ((bx, by, bz), 'Ende')):
            g = ground(x, y, z + 0.05)
            if abs(g - z) > 0.06:
                err.append(f'Strecke {k} ({kind}): {lab} ({x:.2f}, {y:.2f}) liegt auf {z:.2f} m, Boden dort {g:.2f} m')
        n = max(2, int(math.dist((ax, ay), (bx, by)) / 0.2))
        g_prev = az
        ceil = 9.9
        slope = max(0.0, (bz - az) / max(1e-6, math.dist((ax, ay), (bx, by))))
        for i in range(n + 1):
            t = i / n
            x, y = ax + (bx - ax) * t, ay + (by - ay) * t
            if kind == 'jump':
                allow = az + LIMITS['jump_step']
            elif kind == 'drop':
                allow = max(g_prev, az) + P['step']
            else:
                allow = g_prev + P['step'] + (half * 2 * slope if kind == 'stairs' else 0.0)
            g = ground(x, y, allow)
            if kind in ('run', 'stairs', 'duck') and g - g_prev > LIMITS['stair_step'] + 1e-6:
                err.append(f'Strecke {k} ({kind}): Stufe {g - g_prev:.2f} m bei ({x:.1f}, {y:.1f})')
            if kind == 'jump' and g - az > LIMITS['jump_step'] + 1e-6:
                err.append(f'Strecke {k}: Sprungstufe {g - az:.2f} m > {LIMITS["jump_step"]} m bei ({x:.1f}, {y:.1f})')
            head = P['crouch_height'] if kind == 'duck' else P['height']
            z0 = max(allow, g + P['step']) if kind in ('jump', 'drop', 'stairs') else g + P['step']
            z0 = min(z0, g + head - 0.05)
            bl = blockers(x, y, z0 + 1e-3, g + head)
            if bl:
                err.append(f'Strecke {k} ({kind}): Durchgang bei ({x:.2f}, {y:.2f}, {g:.2f}) versperrt von {names[bl[0]]}')
                break
            if kind == 'duck':
                above = [boxes[i][0][2] - g for i in blockers(x, y, g + head, g + 3.0)]
                if above:
                    ceil = min(ceil, min(above))
            g_prev = g
        if kind == 'duck':
            duck_min.append(ceil)
            if not LIMITS['duck_lo'] <= ceil <= LIMITS['duck_hi']:
                err.append(f'Strecke {k}: Duckstelle {ceil:.2f} m hoch (Soll {LIMITS["duck_lo"]}–{LIMITS["duck_hi"]} m)')
    # Tore und Kontrollpunkte: in Reihenfolge auf der Strecke (Strecke schneidet den Auslösequader in Hüfthöhe)
    pts = [(r[0], r[1], r[2] + 1.0) for r in route]

    def first_hit(b):
        lo = tuple(c - s / 2 for c, s in zip(b['center'], b['size']))
        hi = tuple(c + s / 2 for c, s in zip(b['center'], b['size']))
        for i in range(len(pts) - 1):
            if _hits(pts[i], pts[i + 1], lo, hi):
                return i
        return None
    order = [first_hit(C['start'])] + [first_hit(c) for c in C['checkpoints']]
    if None in order:
        err.append('Start oder Kontrollpunkt liegt nicht auf der Strecke: ' + ', '.join(
            n for n, o in zip(['Start'] + [c['name'] for c in C['checkpoints']], order) if o is None))
    elif order != sorted(order):
        err.append(f'Kontrollpunkte nicht in Streckenreihenfolge: {order}')
    lo = tuple(c - s / 2 for c, s in zip(C['finish']['center'], C['finish']['size']))
    hi = tuple(c + s / 2 for c, s in zip(C['finish']['center'], C['finish']['size']))
    if not any(_hits(pts[i], pts[i + 1], lo, hi) for i in range(max(0, len(pts) - 4), len(pts) - 1)):
        err.append('Ziel liegt nicht am Ende der Strecke')
    # Treppenstufen ≤ 0,35 m (alle Bauteile mit Rolle Treppe)
    # Sichtbarkeit der Zielscheiben von Augenpunkten auf der Strecke (alle 1 m)
    eyes = []
    for k in range(len(route) - 1):
        (ax, ay, az, kind), (bx, by, bz, _) = route[k], route[k + 1]
        n = max(1, int(math.dist((ax, ay), (bx, by)) / 1.0))
        e = P['crouch_eye'] if kind == 'duck' else P['eye']
        for i in range(n):
            t = i / n
            eyes.append((ax + (bx - ax) * t, ay + (by - ay) * t, az + (bz - az) * t + e))
    vis = {}
    for t in C['targets']:
        c, nrm, r = t['pos'], t['normal'], t['radius']
        up = (0.0, 0.0, 1.0) if abs(nrm[2]) < 0.9 else (0.0, 1.0, 0.0)
        s = _norm(_cross(nrm, up))
        u = _cross(s, nrm)
        probes = [c] + [tuple(c[k] + 0.85 * r * d[k] for k in range(3)) for d in (u, tuple(-x for x in u), s, tuple(-x for x in s))]
        best_low = best_high = 0
        best_d = None
        for e in eyes:
            d = math.dist(e, c)
            if d > 45.0:
                continue
            to = tuple((e[k] - c[k]) / d for k in range(3))
            if sum(a * b for a, b in zip(to, nrm)) < 0.25:          # Scheibe zeigt vom Auge weg
                continue
            q = [tuple(pp[k] + nrm[k] * 0.03 for k in range(3)) for pp in probes]
            near = G.along(e, c)
            m = sum(1 for pp in q if not any(_hits(e, pp, lo, hi) for lo, hi in near))
            if e[2] - P['eye'] < 1.0:
                best_low = max(best_low, m)
            else:
                best_high = max(best_high, m)
            if m >= 3 and (best_d is None or d < best_d):
                best_d = d
        vis[t['name']] = dict(low=best_low, high=best_high, dist=best_d)
        want = t.get('vis', 'frei')
        if want == 'frei' and max(best_low, best_high) < 4:
            err.append(f'Ziel {t["name"]}: von der Strecke kaum sichtbar ({max(best_low, best_high)}/5 Punkte)')
        if want == 'deckung' and not (2 <= max(best_low, best_high) <= 4):
            err.append(f'Ziel {t["name"]}: soll teilverdeckt sein, sichtbar {max(best_low, best_high)}/5')
        if want == 'oben' and (best_low > 0 or best_high < 3):
            err.append(f'Ziel {t["name"]}: soll nur von oben sichtbar sein (unten {best_low}/5, oben {best_high}/5)')
    stats = dict(length=length, counts=counts, duck_clear=duck_min, vis=vis,
                 total_m=sum(length.values()))
    return err, stats


def par_time(S, stats):
    """Richtzeit: Laufen mit 85 % Sprint (Kurven), Treppe/Sprung/Herunterspringen mit Gehtempo, Ducken mit 2,4 m/s, je Sprung
    0,3 s, je Herunterspringen 0,3 s, je Ziel 1,0 s (Zielen und Treffen im Lauf); aufgerundet auf 5 s."""
    P = PLAYER
    L, n = stats['length'], stats['counts']
    t = (L['run'] / (0.85 * P['sprint']) + L['duck'] / P['crouch'] + (L['stairs'] + L['jump'] + L['drop']) / P['walk']
         + 0.3 * n['jump'] + 0.3 * n['drop'] + 1.0 * len(S.COURSE['targets']))
    return t, 5 * math.ceil(t / 5)
