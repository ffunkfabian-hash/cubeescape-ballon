"""Gegenproben für basic/loadout.py (0.42 „Quickslot“): Kategorien, Leiste und Standard-Skins als Daten – ohne Blender, Teil von ./check.

Geprüft: der echte Block deckt jede Klasse der Spielwaffen und der Formgen-Varianten ab, die Leiste hat neun bekannte Klassen, jeder
Standard-Skin steht in kit.SKINS und ist kein heller Skin; hud_data lehnt fehlende und doppelte Klassen, unbekannte Skins und eine
falsche Leistenlänge ab (Gegenproben). Ausgabe „Leistendaten geprüft“ bei Erfolg.
"""
import copy
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic import loadout as LO  # noqa: E402
from tools import export_unity as EU  # noqa: E402

bad = []
skins = EU.kit_literal('SKINS')
D = EU.data()
classes = [e['profile']['type'] for e in D['weapons']]
hud = D['hud']
cat = {k: c['id'] for c in hud['categories'] for k in c['classes']}
for k in classes:
    if k not in cat:
        bad.append(f'Klasse {k} ohne Kategorie')
for k in set(classes):
    s = LO.DEFAULT_SKIN.get(k)
    if s is None or s not in skins or s in ('standard', 'polar', 'gebraucht'):
        bad.append(f'Klasse {k}: Standard-Skin {s} nicht farbig')
if len(hud['hotbar']) != 9 or any(k not in classes for k in hud['hotbar']):
    bad.append(f'Leiste {hud["hotbar"]}: neun Klassen der Spielwaffen')


def rejects(what, **patch):
    saved = {k: copy.deepcopy(getattr(LO, k)) for k in patch}
    try:
        for k, v in patch.items():
            setattr(LO, k, v)
        LO.hud_data(classes, skins)
        bad.append(f'Gegenprobe {what}: nicht abgelehnt')
    except ValueError:
        pass
    finally:
        for k, v in saved.items():
            setattr(LO, k, v)


cats = copy.deepcopy(LO.CATEGORIES)
rejects('Klasse ohne Kategorie', CATEGORIES=[dict(c, classes=[k for k in c['classes'] if k != 'shotgun']) for c in cats])
rejects('Klasse doppelt', CATEGORIES=cats[:-1] + [dict(cats[-1], classes=cats[-1]['classes'] + ['auto_rifle'])])
rejects('unbekannter Skin', DEFAULT_SKIN=dict(LO.DEFAULT_SKIN, auto_rifle='lila'))
rejects('Leiste mit acht Plätzen', HOTBAR=LO.HOTBAR[:8])
rejects('Leiste mit unbekannter Klasse', HOTBAR=LO.HOTBAR[:8] + ['laser'])
for b in bad:
    print('FEHLER', b)
if not bad:
    print(f'Leistendaten geprüft: {len(set(classes))} Klassen in {len(hud["categories"])} Kategorien, Leiste {", ".join(hud["hotbar"])}, '
          '5 Gegenproben abgelehnt')
sys.exit(1 if bad else 0)
