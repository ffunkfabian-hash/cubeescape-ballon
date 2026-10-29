"""Tests der Regelprüfungen aus 0.30 „Rulebook“ (tools/rules.py) ohne Blender: jede Prüfung grün am richtigen und rot an einem
gezielt falschen Beispiel. In ./check (auch im PR-Check auf Linux). Ausgabe endet mit „Regeln geprüft“, Fehlerzeilen mit „FEHLER“.

  python3 tools/test_rules.py
"""
import copy
import inspect
import json
import os
import sys
import tempfile
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools import rules  # noqa: E402

bad = []


def expect(cond, msg):
    if not cond:
        bad.append(msg)


def mask(rows_bits, w=8):
    return dict(w=w, h=len(rows_bits), rows=[[s, e] for s, e in rows_bits])


# A1 Silhouetten: IoU am Kleinbeispiel, dann am Repo-Stand mit einer gezielt kopierten Maske
a = mask([(0, 8), (2, 6)])
expect(abs(rules.best_iou(a, a)[0] - 1) < 1e-12, 'IoU gleicher Masken ≠ 1')
b = mask([(0, 0), (0, 8), (2, 6)])                  # dieselbe Form eine Zeile tiefer: Verschiebung muss sie finden
expect(rules.best_iou(a, b) == (1.0, -1), f'IoU über Verschiebung nicht gefunden: {rules.best_iou(a, b)}')
expect(rules.best_iou(mask([(0, 4)]), mask([(4, 8)]))[0] == 0, 'IoU getrennter Masken ≠ 0')
expect(abs(rules.best_iou(mask([(0, 4)]), mask([(2, 6)]))[0] - 2 / 6) < 1e-12, 'IoU Teilüberdeckung ≠ 2/6 (Nenner)')   # Richter 0.30
fam = rules.family()
specs = {w: json.load(open(os.path.join(ROOT, 'data', 'specs', f'{w}.spec.json'), encoding='utf-8')) for w, _ in fam}
data = json.load(open(os.path.join(ROOT, 'data', 'silhouettes.json'), encoding='utf-8'))
expect(rules.silhouette_problems(data, fam, specs) == [], 'Repo-Stand: Silhouetten melden Fehler (./check zeigt sie)')
d2 = copy.deepcopy(data)
d2['weapons']['BASIC-12-v2.1']['side'] = d2['weapons']['BASIC-02-v2.1']['side']
p = rules.silhouette_problems(d2, fam, specs)
expect(len(p) == 1 and 'BASIC-02-v2.1 ↔ BASIC-12-v2.1: IoU 1.000' in p[0], f'gleiche Silhouetten 02/12 nicht gemeldet: {p}')
d3 = copy.deepcopy(data)
d3['weapons']['BASIC-07-v2.1']['triangles'] += 1
expect(any('BASIC-07-v2.1: Silhouette veraltet' in x for x in rules.silhouette_problems(d3, fam, specs)), 'veraltete Silhouette nicht gemeldet')
d4 = copy.deepcopy(data)
del d4['weapons']['BASIC-T01-v2.1']
expect(any('BASIC-T01-v2.1: Silhouette fehlt' in x for x in rules.silhouette_problems(d4, fam, specs)), 'fehlende Silhouette nicht gemeldet')

# A2 Dreiecksbudget
n = rules.budget_notes({'X': dict(counts=dict(triangles=55000)), 'Y': dict(counts=dict(triangles=25000)),
                        'Z': dict(counts=dict(triangles=15000))})
expect(len(n) == 2 and n[0].startswith('Warnung Budget X') and n[1].startswith('Hinweis Budget Y'), f'Budget falsch: {n}')

# A4 Freihaltezone
expect(rules.zone_px(1600, 900) == (640, 960, 0, 600), f'Zone 1600 × 900: {rules.zone_px(1600, 900)}')
from tools.export_unity import WEAPONS  # noqa: E402
import importlib  # noqa: E402
m = importlib.import_module(f'basic.{WEAPONS[0]}')
sha = rules.sha_files(rules.clear_sources(m))
ok = dict(zone_px=0, zone_share=0, top_y=0.7, cols=None, sources_sha256=sha)
expect(rules.clear_zone_notes(dict(weapons={'W': ok}), [('W', m)]) == [], 'freie Zone meldet etwas')
hit = dict(ok, zone_px=12, zone_share=0.0001, top_y=0.5, cols=[0.55, 0.6])
n = rules.clear_zone_notes(dict(weapons={'W': hit}), [('W', m)])
expect(len(n) == 1 and n[0].startswith('Warnung Freihaltezone W: 12 px'), f'belegte Zone nicht gemeldet: {n}')
# A4 gelockert: nur das vordere Ende in der unteren äußeren Ecke → keine Meldung; links davon oder höher → Warnung
front = dict(ok, zone_px=1500, zone_share=0.008, top_y=0.61, cols=[0.57, 0.6])
expect(rules.clear_zone_notes(dict(weapons={'W': front}), [('W', m)]) == [], 'Mündung in der erlaubten Ecke gemeldet')
n = rules.clear_zone_notes(dict(weapons={'W': dict(front, cols=[0.50, 0.6])}), [('W', m)])
expect(len(n) == 1 and n[0].startswith('Warnung Freihaltezone'), f'Teil links der Ecke nicht gemeldet: {n}')
n = rules.clear_zone_notes(dict(weapons={'W': dict(ok, sources_sha256='0')}), [('W', m)])
expect(len(n) == 1 and 'veraltet' in n[0], f'veraltete Zonenmessung nicht gemeldet: {n}')
n = rules.clear_zone_notes(dict(weapons={'W': dict(hit, sources_sha256='0')}), [('W', m)])
expect(len(n) == 2 and n[1].startswith('Hinweis Freihaltezone (Stand vorher) W'), f'alte Verletzung nicht als Stand vorher: {n}')
expect('nicht gemessen' in rules.clear_zone_notes({}, [('W', m)])[0], 'fehlende Zonenmessung nicht gemeldet')

# F5 Handmaß (ein Maß für Ego und Figur), Bezug Griffbreite der Familie
from basic import common  # noqa: E402
from basic.arms import robot_arm  # noqa: E402
expect(inspect.signature(common.grip_rifle).parameters['w'].default == rules.GRIP_W_MM, 'GRIP_W_MM ≠ common.grip_rifle w')
ego = rules.hand_measure(robot_arm)
expect(rules.hand_problems(ego, ego) == [], 'gleiche Hand meldet Abweichung')
big = types.SimpleNamespace(**{k: getattr(robot_arm, k) for k in ('PALM_W', 'PALM_LEN', 'FINGER_X', 'FINGER_W', 'FINGER_LINKS',
                                                                   'FINGER_SCALE', 'THUMB_LINKS')})
big.PALM_W *= 1.12                                       # Valorant-Ansatz (F5 B, verworfen): Außenhand 12 % größer
p = rules.hand_problems(rules.hand_measure(big), ego)
expect(any(x.startswith('Handmaß palm_w') for x in p), f'vergrößerte Hand nicht gemeldet: {p}')
rigs = rules.arm_rigs()                                  # Formstudien A/B/C (0.31): ein Handmaß mit Arm v3
expect(len(rigs) >= 3, f'Armsätze nicht gefunden: {[r.__name__ for r in rigs]}')
for r in rigs:
    expect(rules.hand_problems(rules.hand_measure(r), ego) == [], f'Armsatz {r.__name__}: Handmaß weicht von Arm v3 ab')
expect(not any(x.startswith('Armsatz') for x in rules.figure_report()[0]), 'figure_report meldet Armsatz-Handmaß')
from basic.arms import forms as FM  # noqa: E402
BUILD = {'loft': lambda q: FM.loft(q['secs'], q.get('ring', 56), q.get('sub', 6)),          # wie tools/ego_build.FORMS
         'wrap': lambda q: FM.wrap(q['secs'], q['a0'], q['a1'], q['t'], q.get('steps'), q.get('sub', 6)),
         'tube': lambda q: FM.tube(q['path'], q['r'], q.get('segs', 14))}
nform = 0
for r in rigs:                                           # Formen der Armsätze: gültige Indizes, geschlossen, nach außen orientiert
    for pid, _de, _seg, kind, _role, q in r.parts():
        if kind in BUILD:
            V, F = BUILD[kind](q)
            nform += 1
            expect(V and F and all(0 <= i < len(V) for f in F for i in f), f'{r.__name__} {pid}: ungültiges Netz')
            expect(FM._volume(V, F) > 0, f'{r.__name__} {pid}: Volumen ≤ 0')
expect(nform > 30, f'zu wenige Formen in den Armsätzen geprüft: {nform}')

# F6 Budget, F1 Proportion
n = rules.figure_budget_notes('F', 40000, 120)
expect(len(n) == 2 and all(x.startswith('Warnung Figur F') for x in n), f'Figurenbudget: {n}')
expect(rules.figure_budget_notes('F', 20000, 80) == [], 'Figur im Budget meldet etwas')
expect(rules.proportion_note('F', 1600, 1600 / 7.5) == [], '7,5 Kopfhöhen meldet etwas')
expect(len(rules.proportion_note('F', 1709, 297)) == 1, '5,8 Kopfhöhen nicht gemeldet')
with tempfile.TemporaryDirectory() as tmp:
    sp = os.path.join(tmp, 'robot.spec.json')
    json.dump(dict(format='cubeescape-ballon/robot-spec', id='R', measured=dict(height_mm=1709, assemblies=dict(
        head=dict(triangles=11000, size_mm=[227, 240, 297]), legs=dict(triangles=70000)))), open(sp, 'w'))
    n = rules.robot_spec_notes(sp)
    expect(any('81000 Dreiecke' in x for x in n) and any('Knochenzahl' in x for x in n) and any('Kopfhöhen' in x for x in n),
           f'Roboter-Spec: {n}')

# F2/F3/F5/F7 Figurenvertrag
good = types.SimpleNamespace(__name__='g', META=dict(id='G', role='enemy', form='triangle', size_class='large', scale=1.8),
                             POSES={k: {} for k in rules.POSES}, HAND=robot_arm)
expect(rules.figure_meta_problems(good) == [], f'gültiger Vertrag meldet: {rules.figure_meta_problems(good)}')
wrong = types.SimpleNamespace(__name__='w', META=dict(id='W', role='enemy', form='circle', size_class='large', scale=1.2),
                              POSES={k: {} for k in rules.POSES[:-1]})
p = rules.figure_meta_problems(wrong)
expect(len(p) == 4 and any('Grundform' in x for x in p) and any('Maßstab 1.2' in x for x in p) and any('twist_r45' in x for x in p)
       and any('HAND' in x for x in p), f'falscher Vertrag: {p}')

for x in bad:
    print(f'FEHLER {x}')
print(f'test_rules: {"Fehler" if bad else "alles grün"} – Regeln geprüft (A1, A2, A4, F1, F2, F3, F5, F6, F7)')
sys.exit(1 if bad else 0)
