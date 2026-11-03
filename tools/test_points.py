"""Weltpunkte mit Teilbezug (0.41 „Intake“, basic/variant.py): Auswurf und Griffkontakte wandern beim Dehnen mit (ohne Blender, ./check).

1. Jede Spielwaffe (export_unity.WEAPONS) nennt alle Weltpunkte in POINTS, jeder mit einem vorhandenen Teil; resolve(W) ist W selbst
   (BALLONs eigene Daten bleiben unverändert).
2. Dehnen wie ein Generator (Regel von Formgen v2 `_stretch`, hier an den Netzgrenzen aus data/specs): ein Schnitt quer zur Laufachse, Teile
   ganz davor bleiben, Teile ganz dahinter wandern um delta, gekreuzte Teile werden gedehnt; Anker und Weltpunkte folgen ihrem Teil (bei
   gedehnten Teilen nur hinter dem Schnitt). Je Waffe zwei Schnitte (im Gehäuse, im Vorderbau). Erwartet: weapon_entry der Variante
   (basic/variant.as_module) hat Auswurf und Griffkontakte genau dort, wo die Regel sie hinlegt.
3. Gegenprobe: dieselbe Variante mit den alten Modulfeldern (ohne POINTS) – Auswurf und Griffe bleiben an der alten Stelle; der Test
   meldet das als Fehler (muss rot sein, sonst prüft 2 nichts).
"""
import copy
import importlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic import variant as VA  # noqa: E402
from basic.arms import ego as EG  # noqa: E402
from tools import export_unity as EU  # noqa: E402

DELTA = 30.0      # mm nach vorn


def f_range(spec):
    """Teil → (f min, f max) mm aus den Netzgrenzen (Blender: vorn −Y)."""
    return {p['id']: (-p['bounds_m']['max'][1] * 1000, -p['bounds_m']['min'][1] * 1000) for p in spec['parts']}


def stretch(W, rng, at, delta, points=True):
    """Datensatz einer gedehnten Variante: nur Anker und (mit points) Weltpunkte, Regel wie Formgen `_stretch`."""
    far = {k for k, (lo, hi) in rng.items() if lo >= at}
    cross = {k for k, (lo, hi) in rng.items() if lo < at < hi}

    def move(d):
        out = {}
        for n, a in d.items():
            a = copy.deepcopy(a)
            if a.get('part') in far or (a.get('part') in cross and a['at'][0] > at):
                a['at'] = (a['at'][0] + delta,) + tuple(a['at'][1:])
            out[n] = a
        return out
    data = dict(ANCHORS=move(W.ANCHORS))
    if points:
        data['POINTS'] = move(W.POINTS)
    return data


def expect(W, data):
    """Erwartete Lagen (Blender, m) der Weltpunkte nach dem Dehnen: aus den bewegten Punkten des Datensatzes."""
    P = data.get('POINTS', W.POINTS)
    return {n: EU.xyz(*p['at']) for n, p in P.items()}


def measured(e):
    """Lagen der Weltpunkte im Eintrag (weapon_entry): Auswurf, Gurtglied, Griffkontakte."""
    m = {}
    ej = e['weapon']['eject']
    if ej['enabled']:
        m[VA.EJECT_POINT] = ej['pos']
        if ej['links']['enabled']:
            m[VA.LINKS_POINT] = ej['links']['pos']
    for g in e['grips']:
        m[VA.GRIP_PREFIX + g['name']] = g['contact']
    return m


def cuts(rng, W):
    """Zwei Schnitte: 40 mm vor Socket_Hand (Gehäuse, Auswurf) und Mitte Socket_Hand – Socket_SupportHand (Vorderbau)."""
    sup = W.ANCHORS.get('Socket_SupportHand', W.ANCHORS.get('Socket_Muzzle', {'at': (200, 0, 0)}))['at'][0]
    return [40.0, max(60.0, sup / 2)]


def main():
    bad, moved, red = [], 0, 0
    for m in EU.WEAPONS:
        W = importlib.import_module(f'basic.{m}')
        wid = EG.weapon_id(W)
        bad += [f'{wid}: {b}' for b in VA.problems(W)]
        if VA.resolve(W) is not W:
            bad.append(f'{wid}: resolve ändert BALLONs eigene Daten')
        spec = json.load(open(os.path.join(ROOT, 'data', 'specs', f'{wid}.spec.json'), encoding='utf-8'))
        rng = f_range(spec)
        base = measured(EU.weapon_entry(W))
        for at in cuts(rng, W):
            data = stretch(W, rng, at, DELTA)
            want = expect(W, data)
            got = measured(EU.weapon_entry(VA.as_module(data, W, name=f'basic.variant.test_{wid}')))
            for n in want:
                if n not in got or max(abs(a - b) for a, b in zip(got[n], want[n])) > 1e-6:
                    bad.append(f'{wid} Schnitt f={at:.0f}: {n} bei {got.get(n)} statt {want[n]}')
                elif got[n] != base[n]:
                    moved += 1
            # Gegenprobe: alte Modulfelder (ohne POINTS), Anker gedehnt – die Punkte bleiben stehen
            old = types_without_points(W)
            got_old = measured(EU.weapon_entry(VA.as_module(stretch(W, rng, at, DELTA, points=False), old,
                                                             name=f'basic.variant.old_{wid}')))
            red += sum(1 for n in want if got_old.get(n) != want[n])
    if moved == 0:
        bad.append('kein Weltpunkt ist beim Dehnen gewandert (Schnitte prüfen nichts)')
    if red != moved:
        bad.append(f'Gegenprobe: mit alten Modulfeldern stehen {red} statt {moved} Punkte falsch (muss rot sein)')
    for b in bad:
        print('FEHLER', b)
    print(f'Weltpunkte geprüft: {len(EU.WEAPONS)} Waffen, {moved} Punkte mitgewandert, Gegenprobe ohne POINTS {red} falsch (rot)'
          if not bad else f'{len(bad)} Fehler')
    return 1 if bad else 0


def types_without_points(W):
    """Kopie des Moduls ohne POINTS (Stand bis 0.40: Auswurf und Griffe nur als Modulfelder in Autorenmaß)."""
    import types
    old = types.ModuleType(W.__name__ + '_ohne_points')
    old.__dict__.update({k: v for k, v in vars(W).items() if k != 'POINTS' and not k.startswith('__')})
    old.__file__ = W.__file__
    return old


if __name__ == '__main__':
    sys.exit(main())
