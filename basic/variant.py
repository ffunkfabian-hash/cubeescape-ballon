"""Varianten fremder Generatoren (0.41 „Intake“): Weltpunkte mit Teilbezug und Waffen aus einem Datensatz.

Weltpunkte (POINTS) sind alle Punkte im Waffenrahmen außer den Ankern: Hülsenauswurf (EJECT at), Gurtgliederauswurf (EJECT links at)
und die Handkontakte der Ego-Griffe (EGO_GRIPS bzw. ego.GRIPS contact). Sie stehen in derselben Form wie ANCHORS – dict(at=(f, u, x) mm,
part=Teil-ID) –, damit ein Generator, der Teile dehnt, staucht oder tauscht, sie nach derselben Regel mitnimmt wie die Anker (Formgen
v2: Teil verschoben → Punkt verschoben; Teil gedehnt → Punkt hinter dem Schnitt verschoben). Der Teilbezug sagt nur, an welchem Teil der
Punkt sitzt; die Bewegung im Spiel steuern weiter die Felder selbst (Griff 'part': folgt dem Teil, EJECT 'part': Start im Teil).

Ein Waffenmodul nennt seine Weltpunkte mit `POINTS = collect(EJECT, EGO_GRIPS, dict(eject=…, grip=…, support=…))`: die Werte bleiben in den
Feldern, `collect` ergänzt nur den Teilbezug (Griffe mit eigenem 'part' brauchen keinen). `resolve(W)` schreibt die Punkte zurück in Kopien
der Felder; bei BALLONs eigenen Waffen ändert das nichts (Test tools/test_points.py), bei einer Variante übernimmt es die verschobenen
Punkte. `as_module(data, base)` macht aus einem Datensatz (META, PARTS, ASSEMBLIES, ANCHORS, POINTS, ACTIONS …) ein Waffenmodul; alle
übrigen Felder kommen vom Grundmodul (wie formgen/blender/asset_build.py bis Formgen 0.6).
"""
import copy
import importlib
import types

# Name eines Weltpunkts → Feld im Waffenmodul
EJECT_POINT = 'eject'                 # EJECT['at']
LINKS_POINT = 'eject.links'           # EJECT['links']['at']
GRIP_PREFIX = 'grip.'                 # 'grip.<Griff>' → EGO_GRIPS[<Griff>]['contact']
DATA_FIELDS = ('META', 'PARTS', 'ASSEMBLIES', 'ANCHORS', 'POINTS', 'ACTIONS')


def _grips(grips):
    if grips is None:                 # Pilotwaffe ohne EGO_GRIPS: Griffe aus ego.GRIPS
        from basic.arms import ego
        return ego.GRIPS
    return grips


def collect(eject, grips, parts):
    """Weltpunkte eines Moduls aus EJECT und EGO_GRIPS (None = ego.GRIPS) mit Teilbezug. parts: {'eject' | 'links' | <Griff>: Teil-ID};
    ein Griff (und EJECT) mit eigenem 'part' nimmt dieses Teil. Fehlt ein Teilbezug, bricht das Modul beim Import ab (keine stillen Punkte)."""
    pts = {}

    def put(name, at, part):
        if not part:
            raise KeyError(f'Weltpunkt {name} ohne Teilbezug (POINTS = collect(…, {{…}}))')
        pts[name] = dict(at=tuple(at), part=part)
    if eject:
        put(EJECT_POINT, eject['at'], parts.get('eject') or eject.get('part'))
        if eject.get('links'):
            put(LINKS_POINT, eject['links']['at'], parts.get('links'))
    for k, G in _grips(grips).items():
        put(GRIP_PREFIX + k, G['contact'], G.get('part') or parts.get(k))
    unknown = sorted(set(parts) - {'eject', 'links'} - set(_grips(grips)))
    if unknown:
        raise KeyError(f'Teilbezug für unbekannte Weltpunkte {unknown}')
    return pts


def expected(W):
    """Namen der Weltpunkte, die das Modul W nach seinen Feldern haben muss."""
    E = getattr(W, 'EJECT', None)
    names = [EJECT_POINT] if E else []
    if E and E.get('links'):
        names.append(LINKS_POINT)
    return names + [GRIP_PREFIX + k for k in _grips(getattr(W, 'EGO_GRIPS', None))]


def problems(W):
    """Fehlerliste: fehlende oder überzählige Weltpunkte, Teilbezug auf ein fehlendes Teil, Punkte abweichend von den Feldern."""
    P = getattr(W, 'POINTS', None)
    if P is None:
        return ['ohne POINTS (Weltpunkte mit Teilbezug, basic/variant.collect)']
    ids = {p['id'] for p in W.PARTS}
    want = expected(W)
    bad = [f'Weltpunkt {n} fehlt in POINTS' for n in want if n not in P]
    bad += [f'POINTS {n}: kein Feld dazu' for n in P if n not in want]
    bad += [f"POINTS {n}: Teil {v.get('part')} fehlt" for n, v in P.items() if v.get('part') not in ids]
    if not bad:
        R = resolve(W)
        if getattr(R, 'EJECT', None) != getattr(W, 'EJECT', None) or _grips(getattr(R, 'EGO_GRIPS', None)) != _grips(getattr(W, 'EGO_GRIPS', None)):
            bad.append('POINTS weichen von EJECT/EGO_GRIPS ab')
    return bad


def _same(a, b):
    return tuple(float(x) for x in a) == tuple(float(x) for x in b)


def resolve(W):
    """W mit den Weltpunkten aus W.POINTS in EJECT und EGO_GRIPS (Kopien). Ohne POINTS oder ohne Abweichung: W selbst."""
    P = getattr(W, 'POINTS', None)
    if not P:
        return W
    E = getattr(W, 'EJECT', None)
    G = _grips(getattr(W, 'EGO_GRIPS', None))
    moved = (E and EJECT_POINT in P and not _same(P[EJECT_POINT]['at'], E['at'])) or \
        (E and E.get('links') and LINKS_POINT in P and not _same(P[LINKS_POINT]['at'], E['links']['at'])) or \
        any(GRIP_PREFIX + k in P and not _same(P[GRIP_PREFIX + k]['at'], g['contact']) for k, g in G.items())
    if not moved:
        return W
    R = types.ModuleType(W.__name__)
    R.__dict__.update({k: v for k, v in vars(W).items() if k not in ('__name__',)})
    if E:
        E = copy.deepcopy(E)
        if EJECT_POINT in P:
            E['at'] = tuple(P[EJECT_POINT]['at'])
        if E.get('links') and LINKS_POINT in P:
            E['links']['at'] = tuple(P[LINKS_POINT]['at'])
        R.EJECT = E
    G = copy.deepcopy(G)
    for k, g in G.items():
        if GRIP_PREFIX + k in P:
            g['contact'] = tuple(P[GRIP_PREFIX + k]['at'])
    R.EGO_GRIPS = G
    return R


def as_module(data, base=None, name=None):
    """Waffenmodul aus einem Datensatz `data` (dict mit DATA_FIELDS und weiteren Modulfeldern) über dem Grundmodul `base` (Modul oder
    Modulname wie 'pilot.w01_auto_rifle_v21' bzw. 'basic.pilot.w01_auto_rifle_v21'). Ein Modul wird unverändert zurückgegeben. Felder,
    die der Datensatz nicht nennt, kommen vom Grundmodul (EJECT, EGO_GRIPS, EGO_LIVE, Rollenmodule …); nennt er POINTS, gelten deren
    Lagen (resolve). Ohne Grundmodul muss der Datensatz alle Felder tragen."""
    if isinstance(data, types.ModuleType):
        return data
    if isinstance(base, str):
        base = importlib.import_module(base if base.startswith('basic.') else f'basic.{base}')
    meta = data.get('META') or getattr(base, 'META', {})
    W = types.ModuleType(name or f"basic.variant.{meta.get('id', 'weapon')}")
    if base is not None:
        W.__dict__.update({k: v for k, v in vars(base).items() if not k.startswith('__')})
        W.__file__ = base.__file__
        W.BASE = base
    for k, v in data.items():
        setattr(W, k, copy.deepcopy(v))
    missing = [k for k in ('META', 'PARTS', 'ASSEMBLIES', 'ANCHORS') if not hasattr(W, k)]
    if missing:
        raise KeyError(f'Datensatz ohne {missing} und ohne Grundmodul')
    return resolve(W)
