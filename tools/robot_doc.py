"""Erzeugt docs/roboter.md aus basic/robot (Entwurf) und data/robot.spec.json (gemessen von tools/robot_build.py --spec).

  python3 tools/robot_doc.py          → docs/roboter.md schreiben
  python3 tools/robot_doc.py --check  → nur prüfen, ob die Datei aktuell ist und die Spec zum Entwurf passt (Exit 1 bei Abweichung)
"""
import collections
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic import robot as RB  # noqa: E402

HEAD = '<!-- erzeugt von tools/robot_doc.py – nicht von Hand ändern -->\n'
DOC = os.path.join(ROOT, 'docs', 'roboter.md')
SPEC = os.path.join(ROOT, 'data', 'robot.spec.json')
FORM = {'hull': 'Hülle', 'hulls': 'Hüllenkette', 'cyl': 'Zylinder', 'box': 'Quader', 'plate': 'Facettenplatte', 'prism': 'Achtkant'}


def spec():
    return json.load(open(SPEC, encoding='utf-8')) if os.path.exists(SPEC) else None


def spec_matches(S):
    return S is not None and S.get('parts') == {a['id']: [p[0] for p in a['module'].parts()] for a in RB.ASSEMBLIES}


def render():
    S = spec()
    ok = spec_matches(S)
    M = S['measured'] if ok else None
    L = [HEAD, f"# {RB.META['name_de']} – Baugruppen und Teile\n",
         f"Eigenständiges Modell `{RB.META['id']}` (Version {RB.META['version']}, {RB.META['status']}). Quelle: `basic/robot/`; Aufbau, "
         'Bilder und Ankerprüfung: `tools/robot_build.py`. Die Arme sind an den Ego-Arm gekoppelt (`basic/arms/robot_arm.py`, '
         'Entscheidung des Nutzers 24.10.2026); Roboter-eigene Abwandlungen nur in `basic/robot/arms.py`.\n']
    if M:
        L.append(f"Gemessen in der Grundhaltung `idle` (ohne Waffe): Höhe {M['height_mm']} mm, Breite {M['width_mm']} mm, "
                 f"Tiefe {M['depth_mm']} mm.\n")
    else:
        L.append('Maße: noch nicht gemessen oder Spec veraltet (`tools/robot_build.py --spec`).\n')
    L += ['## Baugruppen\n', '| Baugruppe | ID | Segmente | Teile | Objekte im Modell | Dreiecke | Größe B × T × H (mm) |',
          '|---|---|---|---:|---:|---:|---|']
    for a in RB.ASSEMBLIES:
        m = M['assemblies'][a['id']] if M else None
        segs = ', '.join(f'`{s}`' for s in a['module'].SEGMENTS[:6]) + (' …' if len(a['module'].SEGMENTS) > 6 else '')
        L.append(f"| {a['de']} | `{a['id']}` | {segs} | {len(a['module'].parts())} | "
                 + (f"{m['objects']} | {m['triangles']} | {' × '.join(str(v) for v in m['size_mm'])} |" if m else '– | – | – |'))
    L += ['', 'Seitige Baugruppen (Arme, Beine) führen jedes Teil einmal; im Modell steht es rechts und links (Spiegelung an X).\n',
          '## Anker\n', 'Lage in der Grundhaltung (Entwurf, mm, Welt: vorn −Y, oben +Z, rechts −X). Abstand = gemessener kleinster '
          'Abstand zwischen Eltern- und Kindbaugruppe (0 = sie greifen ineinander).\n',
          '| Anker | Gelenk | Eltern → Kind | Lage (mm) | Abstand (mm) |', '|---|---|---|---|---:|']
    for k, A in RB.ANCHORS.items():
        g = S['anchor_gap_mm'].get(k) if ok else None
        L.append(f"| `{k}` | {A['de']} | `{A['parent']}` → `{A['child']}` | {tuple(A['pos'])} | {'–' if g is None else g} |")
    L += ['', '## Haltungen\n', '- `ready`: Pilotwaffe `' + RB.POSES['ready']['weapon'] + '` tief vor dem Körper, Hände an den '
          'Griffen (`basic/arms/ego.GRIPS`), Zwei-Knochen-IK – Hero-, Nah- und Seitenbild.',
          '- `idle`: ohne Waffe, Arme hängen leicht gebeugt – Grundhaltung für Prüfung, Explosionsansicht und Einzelblätter.', '',
          '## Explosionsansicht\n', 'Grafischer Versatz je Baugruppe (mm; X gilt für die linke Seite, rechts gespiegelt):\n',
          '| Baugruppe | Versatz (x, y, z) |', '|---|---|']
    L += [f"| {a['de']} | {RB.EXPLODE[a['id']]} |" for a in RB.ASSEMBLIES]
    L += ['', '## Teile je Baugruppe\n']
    for a in RB.ASSEMBLIES:
        P = a['module'].parts()
        L += [f"### {a['de']} (`{a['id']}`, {len(P)} Teile)\n", '| ID | Bezeichnung | Segment | Form | Material |', '|---|---|---|---|---|']
        L += [f'| `{pid}` | {de} | `{seg}` | {FORM.get(kind, kind)} | `{role}` |' for pid, de, seg, kind, role, p in P]
        roles = collections.Counter(p[4] for p in P)
        L += ['', 'Materialrollen: ' + ', '.join(f'`{r}` {n}' for r, n in sorted(roles.items())) + '\n']
    return '\n'.join(L).rstrip() + '\n'


def main(argv):
    text = render()
    if '--check' in argv:
        msg = []
        if not spec_matches(spec()):
            msg.append('data/robot.spec.json passt nicht zum Entwurf (tools/robot_build.py --spec)')
        if not os.path.exists(DOC) or open(DOC, encoding='utf-8').read() != text:
            msg.append('docs/roboter.md veraltet (python3 tools/robot_doc.py)')
        print('; '.join(msg))
        sys.exit(1 if msg else 0)
    open(DOC, 'w', encoding='utf-8').write(text)
    print('geschrieben', DOC)


if __name__ == '__main__':
    main(sys.argv[1:])
