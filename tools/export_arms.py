"""Arm-Paket „ballon-arms/1“ (0.40 „Brace“): die Ego-Arme aus basic/arms/robot_arm.py (Rig v3) als eigenständiges Paket für Abnehmer
außerhalb von BALLON (Cube Escape, Critic/Roboter). Quelle bleibt robot_arm.py; das Paket entsteht nur hier, nie von Hand.

  ce lock blender -- blender -b --factory-startup -P <abs>/tools/export_arms.py   → packages/ego-arms/
        arms.glb, arms.fbx (Wurzel R_arm/L_arm → Segmentkette → Teile, Anker als Leerknoten), manifest.json, README.md, contact.jpg
  python3 tools/export_arms.py --check   → manifest.json und README.md passen zu robot_arm.py, ego.py, kit.py (ohne Blender, ./check)

Ruhelage des Pakets: beide Arme gestreckt nach vorn (Blender −Y), Handrücken oben, Finger gestreckt, Daumen in seiner Grundrichtung.
Die Kette rechnet Finger und Daumen mit denselben Formeln wie tools/ego_build.solve_arm, nur ohne Löser: Abnehmer setzen die Gelenke
selbst. Die Netze baut tools/ego_build.build_arm (dieselben Teile wie arms.fbx im Unity-Ordner); dieser Export ändert dort nichts.
"""
import hashlib
import json
import math
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic.arms import robot_arm as RA, ego as EG  # noqa: E402
from tools.export_unity import kit_materials, _rounded  # noqa: E402

FORMAT = 'ballon-arms/1'
SET = 'ego'                          # Arm-Set dieses Pakets; weitere Sets (Nutzerentscheid 143 offen) bekommen eigene Ordner
DST = os.path.join(ROOT, 'packages', 'ego-arms')
MM = 0.001
SIDES = ('R', 'L')
ROOT_AT = {'R': (-0.20, 0.0, 0.0), 'L': (0.20, 0.0, 0.0)}    # Schulterwurzeln in der Ruhelage (Paketraum, nicht der Ego-Kameraraum)
ROOT_ROT = (math.sqrt(0.5), math.sqrt(0.5), 0.0, 0.0)        # +90° um X: Segment +Z → vorn (−Y), Segment +Y (Panzerseite) → oben (+Z)
FORM_SRC = ['basic/arms/robot_arm.py', 'basic/arms/forms.py', 'tools/export_arms.py']   # geändert → Paket neu erzeugen (--check)
BUILD_SRC = ['tools/ego_build.py', 'basic/kit.py']   # bauen die Netze mit (build_arm, Fasen); geändert → Hinweis, test_arm_package entscheidet
FINGER_DE = ['Zeigefinger', 'Mittelfinger', 'Ringfinger', 'kleiner Finger']
TOOLGEN_NODES = ['UpperArm_*', 'LowerArm_*', 'Hand_*', 'Fingers_*_0..2', 'Thumb_*', 'Wrist_*', 'GripContact_*']   # Cube Escape FIRST_PERSON_EQUIPMENT.md › 11
ANCHORS = [
    ('Socket_Palm', 'hand', lambda s: (0.0, -RA.PALM_T / 2, RA.PALM_START + RA.PALM_LEN / 2),
     'Griffpunkt: Mitte der Handfläche auf ihrer Oberfläche; +Z Fingerrichtung, −Y zeigt in den Griff (ego_build.PALM_CENTER)'),
    ('Socket_IndexTip', 'f0_2', lambda s: (0.0, 0.0, RA.FINGER_LINKS[2] * RA.FINGER_SCALE[0]),
     'Spitze des Zeigefingers (Abzugsfinger), Ende des dritten Glieds'),
    ('Socket_ThumbTip', 't_2', lambda s: (0.0, 0.0, RA.THUMB_LINKS[2]), 'Daumenspitze, Ende des dritten Daumenglieds'),
]


# ------------------------------------------------------------------ Rechnen ohne Blender (Manifest, --check)
def _norm(v):
    L = math.sqrt(sum(c * c for c in v))
    return tuple(c / L for c in v)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def frame_from(z, y_hint):
    """Wie tools/ego_build.frame_from: Spalten x, y, z (Zeilenliste der 3×3-Matrix)."""
    z = _norm(z)
    d = sum(a * b for a, b in zip(y_hint, z))
    y = _norm(tuple(a - b * d for a, b in zip(y_hint, z)))
    x = _cross(y, z)
    return [[x[i], y[i], z[i]] for i in range(3)]


def quat(M):
    """3×3-Drehmatrix → Quaternion (w, x, y, z) mit w ≥ 0."""
    t = M[0][0] + M[1][1] + M[2][2]
    if t > 0:
        s = math.sqrt(t + 1.0) * 2
        q = (0.25 * s, (M[2][1] - M[1][2]) / s, (M[0][2] - M[2][0]) / s, (M[1][0] - M[0][1]) / s)
    elif M[0][0] > M[1][1] and M[0][0] > M[2][2]:
        s = math.sqrt(1.0 + M[0][0] - M[1][1] - M[2][2]) * 2
        q = ((M[2][1] - M[1][2]) / s, 0.25 * s, (M[0][1] + M[1][0]) / s, (M[0][2] + M[2][0]) / s)
    elif M[1][1] > M[2][2]:
        s = math.sqrt(1.0 + M[1][1] - M[0][0] - M[2][2]) * 2
        q = ((M[0][2] - M[2][0]) / s, (M[0][1] + M[1][0]) / s, 0.25 * s, (M[1][2] + M[2][1]) / s)
    else:
        s = math.sqrt(1.0 + M[2][2] - M[0][0] - M[1][1]) * 2
        q = ((M[1][0] - M[0][1]) / s, (M[0][2] + M[2][0]) / s, (M[1][2] + M[2][1]) / s, 0.25 * s)
    return tuple(-c for c in q) if q[0] < 0 else q


def qmat(q):
    w, x, y, z = q
    return [[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
            [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
            [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]]


def _mv(M, v):
    return tuple(sum(M[i][k] * v[k] for k in range(3)) for i in range(3))


def _mm(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def parent_of(seg):
    if seg == 'upper':
        return None
    if seg in ('fore', 'hand'):
        return {'fore': 'upper', 'hand': 'fore'}[seg]
    base, j = seg.rsplit('_', 1)
    return 'hand' if j == '0' else f'{base}_{int(j) - 1}'


def chain(side):
    """Ruhelage je Segment: (Eltern, Lage im Elternrahmen in m, Drehung als Quaternion). Spiegelung links an X wie build_arm."""
    sx = 1 if side == 'R' else -1
    out = {}
    for seg in RA.SEGMENTS:
        par, q = parent_of(seg), (1.0, 0.0, 0.0, 0.0)
        if seg == 'upper':
            at = (0.0, 0.0, 0.0)
        elif seg == 'fore':
            at = (0.0, 0.0, RA.UPPER_MM * MM)
        elif seg == 'hand':
            at = (0.0, 0.0, RA.FORE_MM * MM)
        elif seg.startswith('f'):
            i, j = int(seg[1]), int(seg[3])
            at = (sx * RA.FINGER_X[i] * MM, 0.0, RA.KNUCKLE_Z * MM) if j == 0 else \
                (0.0, 0.0, RA.FINGER_LINKS[j - 1] * RA.FINGER_SCALE[i] * MM)
        else:
            j = int(seg[2])
            if j == 0:
                at = (sx * RA.THUMB_BASE[0] * MM, RA.THUMB_BASE[1] * MM, RA.THUMB_BASE[2] * MM)
                q = quat(frame_from((sx * RA.THUMB_DIR[0], RA.THUMB_DIR[1], RA.THUMB_DIR[2]), (0.0, 1.0, 0.0)))
            else:
                at = (0.0, 0.0, RA.THUMB_LINKS[j - 1] * MM)
        out[seg] = (par, at, q)
    return out


def rest_world(side):
    """Weltlage (Paketraum) jedes Segments und Ankers in der Ruhelage: {name: (Lage, 3×3)}."""
    W = {'arm': (ROOT_AT[side], qmat(ROOT_ROT))}
    for seg, (par, at, q) in chain(side).items():
        p, R = W[par or 'arm']
        W[seg] = (tuple(a + b for a, b in zip(p, _mv(R, at))), _mm(R, qmat(q)))
    sx = 1 if side == 'R' else -1
    for aid, seg, at, _de in ANCHORS:
        p, R = W[seg]
        a = at(side)
        W[aid] = (tuple(x + y for x, y in zip(p, _mv(R, (sx * a[0] * MM, a[1] * MM, a[2] * MM)))), R)
    return W


def r6(v):
    return [r6(x) for x in v] if isinstance(v, (list, tuple)) else round(float(v), 6) + 0.0     # + 0.0: kein −0.0 im Manifest


def sha(path):
    return hashlib.sha256(open(os.path.join(ROOT, path), 'rb').read()).hexdigest()


def parts_sha():
    return hashlib.sha256(json.dumps(_rounded([list(p) for p in RA.parts()]), sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def joint(seg):
    if seg == 'upper':
        return dict(name='shoulder', de='Schulter', type='ball', axes=['x', 'y', 'z'],
                    src='ego_build.solve_arm: Oberarm zeigt vom Ellbogen zur Schulter (Zwei-Glied-Lösung mit Pol), +Y Panzerseite zur Kamera')
    if seg == 'fore':
        return dict(name='elbow', de='Ellbogen', type='ball', axes=['x', 'y', 'z'], visual_axis='x',
                    src='Der Gelenkzylinder elbow* liegt auf X. solve_arm richtet Ober- und Unterarm einzeln aus (Richtung plus '
                        'Blickhinweis) und beugt dabei nicht um X: gemessen 0.40 liegt die Beugeachse nahe Segment-±Y')
    if seg == 'hand':
        return dict(name='wrist', de='Handgelenk: Kardan in der Stulpe, Hand dreht frei', type='ball', axes=['x', 'y', 'z'],
                    limits=dict(bend_target_deg=RA.WRIST_TARGET_DEG, bend_limit_deg=RA.WRIST_LIMIT_DEG),
                    src='Knick = Winkel zwischen Unterarm-Z und Hand-Z; Ziel 45° (Löser hält ihn), Grenze 55° (Toolgen wrist_limit)')
    if seg == 't_0':
        return dict(name='thumb_base', de='Daumensattel', type='saddle', axes=['y', 'x'],
                    pose='Ry(−s·(out − 30°)) · Rx(flex); s = +1 rechts, −1 links', src='ego_build.solve_arm (Daumen)')
    if seg.startswith('t_'):
        return dict(name='thumb', de='Daumengelenk', type='hinge', axes=['x'],
                    pose='Rx(0,6 · tip)' if seg == 't_1' else 'Rx(tip)', src='ego_build.solve_arm (Daumen)')
    return dict(name='finger', de='Fingergelenk', type='hinge', axes=['x'], pose='Rx(Winkel); positiv beugt zur Handfläche (−Y)',
                src='ego_build.solve_arm (Finger)')


def finger_range():
    """Genutzte Gelenkwinkel aus den Fingerposen (Grenzen legt robot_arm.py nicht fest)."""
    P = EG.FINGER_POSES.values()
    links = [[a for p in P for row in p['f'] for a in [row[j]]] for j in range(3)]
    th = [[p['t'][k] for p in P] for k in range(3)]
    return dict(finger_deg=[[min(v), max(v)] for v in links],
                thumb_deg=dict(flex=[min(th[0]), max(th[0])], out=[min(th[1]), max(th[1])], tip=[min(th[2]), max(th[2])]),
                de='kleinster und größter Winkel je Glied über alle finger_poses; keine festen Grenzen im Rig')


def segment_de(seg):
    if seg in ('upper', 'fore', 'hand'):
        return {'upper': 'Oberarm', 'fore': 'Unterarm mit Ellbogen', 'hand': 'Hand mit Kardanblock'}[seg]
    if seg.startswith('f'):
        return f'{FINGER_DE[int(seg[1])]}, Glied {int(seg[3]) + 1}'
    return f'Daumen, Glied {int(seg[2]) + 1}'


def length_m(seg):
    if seg in ('upper', 'fore'):
        return (RA.UPPER_MM if seg == 'upper' else RA.FORE_MM) * MM
    if seg == 'hand':
        return RA.KNUCKLE_Z * MM
    if seg.startswith('f'):
        return RA.FINGER_LINKS[int(seg[3])] * RA.FINGER_SCALE[int(seg[1])] * MM
    return RA.THUMB_LINKS[int(seg[2])] * MM


def manifest(measured):
    """measured: dict(triangles={R: {seg: n}, L: …}, glb=dict(sha256, bytes)) – aus Blender oder aus dem vorhandenen Manifest."""
    roles = kit_materials()
    P = RA.parts()
    used = sorted({p[4] for p in P})
    C = {s: chain(s) for s in SIDES}
    Wr = {s: rest_world(s) for s in SIDES}
    segs = []
    for seg in RA.SEGMENTS:
        par, _, _ = C['R'][seg]
        segs.append(dict(id=seg, de=segment_de(seg), parent=par or 'arm', joint=joint(seg), length_m=r6(length_m(seg)),
                         rest={s: dict(at_m=r6(C[s][seg][1]), rot_wxyz=r6(C[s][seg][2]), world_m=r6(Wr[s][seg][0])) for s in SIDES},
                         parts=[p[0] for p in P if p[2] == seg],
                         triangles={s: measured['triangles'][s][seg] for s in SIDES}))
    tri = {s: sum(measured['triangles'][s].values()) for s in SIDES}
    return dict(
        format=FORMAT, set=SET, generated_by='tools/export_arms.py', rig_version=RA.RIG_VERSION,
        de='Ego-Arme BASIC (Roboterarm v3): starre Teile je Segment, ohne Skinning; zwei Seiten R/L',
        units=dict(length='m', angle='deg', source_mm='robot_arm.py rechnet in mm, das Paket in m'),
        axes=dict(space='Blender, rechtshändig: rechts −X, vorn −Y, oben +Z (wie der Ego-Kameraraum in ego.json)',
                  segment='Ursprung im Gelenk am Segmentanfang, +Z entlang des Segments, +Y Panzerseite/Handrücken, −Y Handfläche, '
                          '+X Daumenseite der rechten Hand (links gespiegelt: Daumen auf −X)',
                  glb='glTF 2.0 (+Y oben): der Blender-Exporter rechnet (x, y, z) → (x, z, −y)',
                  fbx='Achsen forward −Z, up Y, Meter (FBX_SCALE_ALL), ohne „Apply Transform“: jeder Knoten trägt seine lokale Lage'),
        nodes=dict(root='<S>_arm', segment='<S>_<segment>', part='<S>_<teil>', anchor='<S>_<anker>', sides=list(SIDES),
                   de='S = R oder L; Teile hängen unter ihrem Segment, Segmente bilden die Kette, Anker sind Leerknoten'),
        rest_pose=dict(de='Arme gestreckt nach vorn (−Y), Handrücken oben, Finger gestreckt (alle Winkel 0), Daumen in seiner '
                          'Grundrichtung (out = 30°, flex = tip = 0); keine Ego-Haltung',
                       roots={s: dict(at_m=r6(ROOT_AT[s]), rot_wxyz=r6(ROOT_ROT)) for s in SIDES}),
        segments=segs,
        anchors=[dict(id=aid, segment=seg, de=de, at_mm_R=r6(at('R')), node={s: f'{s}_{aid}' for s in SIDES},
                      world_m={s: r6(Wr[s][aid][0]) for s in SIDES}) for aid, seg, at, de in ANCHORS],
        limits=dict(wrist_target_deg=RA.WRIST_TARGET_DEG, wrist_limit_deg=RA.WRIST_LIMIT_DEG, used=finger_range()),
        finger_poses=[dict(name=k, f=[[float(a) for a in row] for row in v['f']], t=[float(a) for a in v['t']])
                      for k, v in EG.FINGER_POSES.items()],
        finger_pose_de='f: je Finger (Zeige-, Mittel-, Ring-, kleiner Finger) drei Gliedwinkel; t: Daumen [flex, out, tip]',
        docking=dict(de='Eine Waffe beschreibt je Griff contact (Autorenmaß f vorn, u oben, x links in mm), palm (Richtung von der '
                        'Handfläche in das Bauteil), fingers (Fingerrichtung) und fingers_pose. Die Hand sitzt so, dass Socket_Palm auf '
                        'contact liegt, sein +Z entlang fingers und sein −Y entlang palm zeigt: Hand = Griffrahmen · Socket_Palm⁻¹ '
                        '(ego_build.grip_hand). Autorenmaß → Blender: (x, −f, u) / 1000.',
                     pilot=dict(weapon='BASIC-01-v2.1', grips={k: dict({kk: vv for kk, vv in g.items() if kk != 'src'}, src=g['src'])
                                                                 for k, g in EG.GRIPS.items()})),
        ego=dict(de='So hängen die Arme in BALLON (ego.json › arm): Kameraraum, Schulteranker, Pol und Vorzugsrichtung des Löser',
                 camera=dict(h_fov_deg=EG.CAMERA['h_fov_deg'], near_m=EG.CAMERA['near_m']),
                 shoulder_m={s: r6(RA.SHOULDER[s]) for s in SIDES}, elbow_pole=r6(RA.ELBOW_POLE), forearm_pref=r6(RA.FOREARM_PREF),
                 solver='tools/ego_build.solve_arm'),
        materials=[dict(role=r, color=roles[r]['color'], aaa_color=roles[r].get('aaa_color', roles[r]['color']),
                        rough=roles[r]['rough'], metal=roles[r]['metal'], spec=roles[r].get('spec', 0.5), de=roles[r]['de'])
                   for r in used],
        material_de='Netze tragen je Teil eine Rolle als Materialname; Farbe in GLB/FBX = aaa_color, keine Texturen. Der gebackene '
                    'Arm-Atlas liegt nur im Unity-Ordner (unity/Assets/Ballon/Generated/Textures/arms_{albedo,spec,normal,ao}.png)',
        parts=[dict(id=pid, de=de, segment=seg, form=kind, role=role) for pid, de, seg, kind, role, _p in P],
        triangles=dict(total=tri, de='nach den Fasen (wie exportiert), je Seite'),
        files=dict(glb=dict(path='arms.glb', **measured['glb']), fbx=dict(path='arms.fbx', de='Bytes nicht stabil (Zeitstempel im FBX)'),
                   contact='contact.jpg', readme='README.md'),
        sources=dict(files=[dict(path=p, sha256=sha(p)) for p in FORM_SRC + BUILD_SRC], parts_sha256=parts_sha(),
                     de='SHA-256 der Generatorquellen beim Export; parts_sha256 über robot_arm.parts()'),
        toolgen=dict(src=RA.SOURCE, nodes=TOOLGEN_NODES, nodes_src='Cube Escape Docs/FIRST_PERSON_EQUIPMENT.md › 11'))


def readme(M):
    """README.md des Pakets aus dem Manifest (erzeugt, nie von Hand)."""
    seg = {s['id']: s for s in M['segments']}
    L = [f"# Ego-Arme – Paket `{M['format']}`", '',
         f"Erzeugt von `{M['generated_by']}` (BALLON), nie von Hand bearbeiten. Rig-Version {M['rig_version']}, Set `{M['set']}`. "
         'Quelle der Form ist `basic/arms/robot_arm.py`; Haltungen, Griffe und Fingerposen kommen aus `basic/arms/ego.py`.', '',
         '![Aufbau der Ego-Arme](../../docs/bilder/ego-arme-aufbau.jpg)', '',
         '## Dateien', '', '| Datei | Inhalt |', '|---|---|',
         f"| `arms.glb` | beide Arme, glTF 2.0 binär, {M['triangles']['total']['R'] + M['triangles']['total']['L']} Dreiecke, "
         f"Bytes reproduzierbar (SHA-256 im Manifest) |",
         '| `arms.fbx` | dieselbe Hierarchie als FBX (ohne „Apply Transform“) |',
         '| `manifest.json` | Maschinenlesbar: Segmente, Eltern, Längen, Gelenke, Grenzen, Anker, Fingerposen, Rollen, Dreiecke, Quellhash |',
         '| `contact.jpg` | Kontaktbogen aus dem wieder eingelesenen GLB (Workbench) |', '',
         '## Aufbau', '',
         'Ein Arm besteht aus **starren Teilen**, die je an genau einem **Segment** hängen. Es gibt kein Skinning und keine Knochen. '
         'Ein Gelenk ist der Ursprung eines Segments, und bewegt wird, indem man die lokale Drehung des Segmentknotens setzt.', '',
         '```', '<S>_arm                      Wurzel = Schultergelenk (S = R oder L)',
         '└─ <S>_upper                 Oberarm',
         '   └─ <S>_fore               Unterarm, Ellbogengelenk an seinem Ursprung',
         '      └─ <S>_hand            Hand, Kardanblock an ihrem Ursprung (Handgelenk)',
         '         ├─ <S>_Socket_Palm  Griffpunkt',
         '         ├─ <S>_f0_0 → f0_1 → f0_2 → <S>_Socket_IndexTip   Zeigefinger',
         '         ├─ <S>_f1_0 → f1_1 → f1_2                        Mittelfinger',
         '         ├─ <S>_f2_0 → f2_1 → f2_2                        Ringfinger',
         '         ├─ <S>_f3_0 → f3_1 → f3_2                        kleiner Finger',
         '         └─ <S>_t_0 → t_1 → t_2 → <S>_Socket_ThumbTip     Daumen',
         '   (jeder Segmentknoten trägt seine Teile <S>_<teil> als Kinder)', '```', '',
         '| Segment | Teil des Arms | Eltern | Gelenk | Achsen | Länge (mm) | Teile | Dreiecke R |', '|---|---|---|---|---|---|---|---|']
    for s in M['segments']:
        J = s['joint']
        L.append(f"| `{s['id']}` | {s['de']} | `{s['parent']}` | {J['de']} ({J['type']}) | {', '.join(J['axes'])} | "
                 f"{s['length_m'] * 1000:.1f} | {len(s['parts'])} | {s['triangles']['R']} |")
    L += ['', '**Schulter, Ellbogen, Handgelenk** sind keine eigenen Segmente. Die Schulter ist die Wurzel `<S>_arm`. Die '
          'Ellbogenteile (`elbow`, `elbow_disc`, `elbow_ring`, `elbow_hub`) liegen im Ursprung von `fore`, der Kardanblock '
          '(`wrist_block`, `wrist_pin`) im Ursprung von `hand`.', '',
          '## Rahmen, Achsen, Ruhelage', '',
          f"- Paketraum: {M['axes']['space']}. Einheiten: Meter, Grad.",
          f"- Segmentrahmen: {M['axes']['segment']}.",
          f"- GLB: {M['axes']['glb']}. FBX: {M['axes']['fbx']}.",
          f"- Ruhelage: {M['rest_pose']['de']}. Wurzeln bei R {M['rest_pose']['roots']['R']['at_m']} m und "
          f"L {M['rest_pose']['roots']['L']['at_m']} m, gedreht +90° um X.",
          '- Die linke Seite ist an der Segment-X-Achse gespiegelt: gleiche Rahmen (rechtshändig), gespiegelte Netze, Versätze mit −x.', '',
          '## Gelenke und Grenzen', '',
          f"- Finger: Drehung um X, positiv beugt zur Handfläche. Ein Fingerglied `f<i>_<j>` = Versatz · Rx(Winkel).",
          f"- Daumen: `t_0` = Versatz · Grundrichtung · {seg['t_0']['joint']['pose']}, `t_1` = {seg['t_1']['joint']['pose']}, "
          f"`t_2` = {seg['t_2']['joint']['pose']}.",
          f"- Handgelenk: Knick (Unterarm-Z zu Hand-Z) Ziel {M['limits']['wrist_target_deg']}°, Grenze {M['limits']['wrist_limit_deg']}°. "
          'Die Hand dreht in der Stulpe frei.',
          f"- Ellbogen: {seg['fore']['joint']['src']}.",
          f"- Fingergrenzen legt das Rig nicht fest. Genutzt werden: Finger je Glied {M['limits']['used']['finger_deg']}°, Daumen "
          f"flex {M['limits']['used']['thumb_deg']['flex']}°, out {M['limits']['used']['thumb_deg']['out']}°, "
          f"tip {M['limits']['used']['thumb_deg']['tip']}°.", '',
          '## Anker', '', '| Anker | Segment | Lage R (mm, Segmentrahmen) | Bedeutung |', '|---|---|---|---|']
    for a in M['anchors']:
        L.append(f"| `<S>_{a['id']}` | `{a['segment']}` | {a['at_mm_R']} | {a['de']} |")
    L += ['', '## Wie eine Waffe andockt', '', M['docking']['de'], '',
          f"Beispiel Pilotwaffe {M['docking']['pilot']['weapon']}:", '',
          '| Griff | Teil | contact (f, u, x mm) | palm | fingers | Fingerpose |', '|---|---|---|---|---|---|']
    for k, g in M['docking']['pilot']['grips'].items():
        L.append(f"| `{k}` | {g.get('part', 'Waffe')} | {list(g['contact'])} | {list(g['palm'])} | {list(g['fingers'])} | "
                 f"`{g['fingers_pose']}` |")
    L += ['', 'Die Waffe selbst hängt über ihren `Socket_Hand` in der Haltung (ego.py `POSES`). Griffhand rechts = `grip`, Stützhand '
          'links = `support`.', '',
          '## Fingerposen', '', M['finger_pose_de'] + '.', '', '| Pose | Zeige | Mittel | Ring | klein | Daumen |', '|---|---|---|---|---|---|']
    for p in M['finger_poses']:
        L.append(f"| `{p['name']}` | " + ' | '.join(str([int(a) if a == int(a) else a for a in row]) for row in p['f']) +
                 f" | {[int(a) if a == int(a) else a for a in p['t']]} |")
    L += ['', '## Materialrollen', '', M['material_de'] + '.', '', '| Rolle | Farbe | AAA-Farbe | Rauheit | Metall | Bedeutung |',
          '|---|---|---|---|---|---|']
    for m in M['materials']:
        L.append(f"| `{m['role']}` | {m['color']} | {m['aaa_color']} | {m['rough']} | {m['metal']} | {m['de']} |")
    L += ['', '## Was ein Abnehmer braucht', '',
          '- **Alle:** `manifest.json` lesen und `format` prüfen (`ballon-arms/1`, sonst abbrechen). Dann `arms.glb` oder `arms.fbx` '
          'laden, Knoten über die Namen `<S>_<segment>` und `<S>_<anker>` finden und nie über die Reihenfolge.',
          '- **Ego-Ansicht (Cube Escape, BALLON-Unity):** Die Wurzel kommt an die Schulter im Kameraraum (`ego.shoulder_m`). Die Hand '
          'wird über `Socket_Palm` an den Griff der Waffe gelegt. Der Unterarm folgt der Hand mit dem Knick ≤ 45° (`ego_build.solve_arm`), '
          'der Oberarm zeigt zur Schulter. Die Finger kommen aus `finger_poses`. '
          'Zum Vergleich die Toolgen-Knoten in Cube Escape: ' + ', '.join(f'`{n}`' for n in M['toolgen']['nodes']) +
          f" ({M['toolgen']['nodes_src']}); eine Namenszuordnung legt dieses Paket nicht fest.",
          '- **Roboter von außen (Critic, Figur):** Die Wurzel `<S>_arm` sitzt im Schultergelenk des Rumpfs. Die Gelenkachsen und Längen '
          'stehen in `segments`. Die Hand greift über `Socket_Palm` wie oben.',
          '- **Material:** Rolle je Teil (Materialname); eigene Shader sollen die Werte aus `materials` nutzen.', '',
          '## Was ewig ist', '',
          '- Segment-IDs aus `robot_arm.SEGMENTS`: ' + ', '.join(f'`{s["id"]}`' for s in M['segments']) + '.',
          '- Anker-Namen: ' + ', '.join(f"`{a['id']}`" for a in M['anchors']) + '. Knotennamen `<S>_…` mit S = R/L, Wurzel `<S>_arm`.',
          '- Teil-IDs (englisch snake_case) und Rollennamen.',
          '- Umbenennen oder Entfernen nur mit `ballon-arms/2` und einem Migrationshinweis. Neue Felder, Teile oder Anker dürfen dazukommen.', '',
          '## Weitere Arm-Sets', '',
          'Dieses Paket beschreibt die heutigen Ego-Arme (Set `ego`). Ob es ein eigenes Arm-Set für den Roboter gibt, entscheidet der '
          'Nutzerentscheid 143 (Arm-Set Ego/Roboter), der noch offen ist. Ein weiteres Set bekäme einen eigenen Ordner '
          '`packages/<set>-arms/` im selben Format, mit eigenem `set` und denselben Segment- und Ankernamen, soweit es die Glieder gibt.', '',
          '## Prüfen', '',
          '- `python3 tools/export_arms.py --check` (in `./check`): Manifest und README passen zu `robot_arm.py`, `ego.py`, `kit.py`.',
          '- `blender -b --factory-startup -P tools/test_arm_package.py` (in `./check`, wenn Blender vorhanden ist): GLB neu erzeugt ist '
          'bytegleich, die Dreiecke stimmen, und der Reimport von GLB und FBX erhält Teile, Hierarchie, Anker und die Ruhelage.',
          '- Neu erzeugen: `ce lock blender -- blender -b --factory-startup -P <abs>/tools/export_arms.py`.', '']
    return '\n'.join(L)


def measured_from(M):
    return dict(triangles={s: {x['id']: x['triangles'][s] for x in M['segments']} for s in SIDES},
                glb={k: M['files']['glb'][k] for k in ('sha256', 'bytes')})


def check():
    p = os.path.join(DST, 'manifest.json')
    if not os.path.exists(p):
        print('packages/ego-arms/manifest.json fehlt (tools/export_arms.py in Blender ausführen)')
        return 1
    cur = json.load(open(p, encoding='utf-8'))
    new = json.loads(json.dumps(manifest(measured_from(cur)), ensure_ascii=False))
    bad = [k for k in new if k != 'sources' and cur.get(k) != new[k]]
    if cur.get('sources', {}).get('parts_sha256') != new['sources']['parts_sha256']:
        bad.append('parts_sha256')
    old = {f['path']: f['sha256'] for f in cur.get('sources', {}).get('files', [])}
    bad += [f['path'] for f in new['sources']['files'] if f['path'] in FORM_SRC and old.get(f['path']) != f['sha256']]
    note = [f['path'] for f in new['sources']['files'] if f['path'] in BUILD_SRC and old.get(f['path']) != f['sha256']]
    for f in ('arms.glb', 'arms.fbx', 'contact.jpg', 'README.md'):
        if not os.path.exists(os.path.join(DST, f)):
            bad.append(f)
    glb = os.path.join(DST, 'arms.glb')
    if os.path.exists(glb) and hashlib.sha256(open(glb, 'rb').read()).hexdigest() != cur['files']['glb']['sha256']:
        bad.append('arms.glb (SHA-256)')
    rp = os.path.join(DST, 'README.md')
    if os.path.exists(rp) and open(rp, encoding='utf-8').read() != readme(cur):
        bad.append('README.md')
    if bad:
        print('Arm-Paket veraltet (' + ', '.join(bad[:8]) + '): ce lock blender -- blender -b --factory-startup -P <abs>/tools/export_arms.py')
        return 1
    if note:
        print('Hinweis Arm-Paket: ' + ', '.join(note) + ' seit dem Export geändert – tools/test_arm_package.py prüft, ob die Netze gleich blieben')
    print(f"arm-paket: {cur['format']} aktuell ({len(cur['segments'])} Segmente, {len(cur['parts'])} Teile je Seite, "
          f"{len(cur['anchors'])} Anker, {cur['triangles']['total']['R'] + cur['triangles']['total']['L']} Dreiecke)")
    return 0


# ------------------------------------------------------------------ Blender-Teil
def build(materials=True):
    """Szene mit beiden Armen in der Ruhelage des Pakets: {Seite: (Wurzel, Segmente, Teile, Anker)}."""
    import bpy
    from mathutils import Matrix, Quaternion, Vector
    from basic import kit
    import tools.ego_build as EB
    kit.reset_scene()
    mats = {}
    out = {}
    for side in SIDES:
        sx = 1 if side == 'R' else -1
        segs, pieces = EB.build_arm(side)
        root = bpy.data.objects.new(f'{side}_arm', None)
        root.empty_display_size = 0.03
        bpy.context.scene.collection.objects.link(root)
        root.matrix_world = Matrix.Translation(ROOT_AT[side]) @ Quaternion(ROOT_ROT).to_matrix().to_4x4()
        for seg, (par, at, q) in chain(side).items():
            e = segs[seg]
            e.parent = segs[par] if par else root
            e.matrix_basis = Matrix.Translation(at) @ Quaternion(q).to_matrix().to_4x4()
        anchors = {}
        for aid, seg, at, _de in ANCHORS:
            a = at(side)
            e = bpy.data.objects.new(f'{side}_{aid}', None)
            e.empty_display_size = 0.006
            bpy.context.scene.collection.objects.link(e)
            e.parent = segs[seg]
            e.matrix_basis = Matrix.Translation(Vector((sx * a[0], a[1], a[2])) * MM)
            anchors[aid] = e
        if materials:          # einfache Rollenmaterialien (Name = Rolle, aaa_color); kit.material ist ein Knotenbaum für Cycles
            for ob in pieces.values():
                role = ob.data.materials[0]['basic_role']
                if role not in mats:
                    d = kit.MATERIALS[role]
                    m = bpy.data.materials.new(role)
                    m.use_nodes = True
                    b = m.node_tree.nodes['Principled BSDF']
                    b.inputs['Base Color'].default_value = kit.hex_rgba(d.get('aaa_color', d['color']))
                    b.inputs['Roughness'].default_value = d['rough']
                    b.inputs['Metallic'].default_value = d['metal']
                    mats[role] = m
                ob.data.materials[0] = mats[role]
        out[side] = (root, segs, pieces, anchors)
    bpy.context.view_layer.update()
    return out


def triangles(arms):
    import bpy
    dg = bpy.context.evaluated_depsgraph_get()
    T = {}
    for side, (_root, segs, pieces, _a) in arms.items():
        T[side] = {s: 0 for s in RA.SEGMENTS}
        for ob in pieces.values():
            me = ob.evaluated_get(dg).to_mesh()
            me.calc_loop_triangles()
            T[side][ob.parent.name[2:]] += len(me.loop_triangles)
            ob.evaluated_get(dg).to_mesh_clear()
    return T


def export_files(dst):
    """Baut die Szene und schreibt arms.glb und arms.fbx nach dst; gibt die Messwerte (Dreiecke, GLB) zurück."""
    import bpy
    os.makedirs(dst, exist_ok=True)
    arms = build()
    T = triangles(arms)
    glb = os.path.join(dst, 'arms.glb')
    bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', use_selection=False, export_apply=True, export_yup=True,
                              export_materials='EXPORT', export_cameras=False, export_lights=False, export_extras=False,
                              export_animations=False, export_skins=False, export_morph=False, export_texcoords=False,
                              export_tangents=False, export_attributes=False)
    bpy.ops.export_scene.fbx(filepath=os.path.join(dst, 'arms.fbx'), use_selection=False, object_types={'EMPTY', 'MESH'},
                             use_mesh_modifiers=True, mesh_smooth_type='OFF', use_custom_props=False, add_leaf_bones=False,
                             bake_anim=False, apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL', bake_space_transform=False,
                             axis_forward='-Z', axis_up='Y', path_mode='STRIP', embed_textures=False)
    body = open(glb, 'rb').read()
    return dict(triangles=T, glb=dict(sha256=hashlib.sha256(body).hexdigest(), bytes=len(body)))


SHEET = [('beide Arme, vorn oben', (-0.75, -1.55, 0.85), (0.0, -0.45, 0.0), 40),
         ('rechts, Seite', (-1.6, -0.42, 0.10), (0.0, -0.42, 0.0), 40),
         ('oben', (0.0, -0.42, 1.7), (0.0, -0.42, 0.0), 40),
         ('rechte Hand, nah', (-0.42, -0.95, 0.25), (-0.20, -0.70, 0.0), 55)]


def contact_sheet(dst):
    """Kontaktbogen aus dem wieder eingelesenen GLB (Workbench, Materialfarben), vier Ansichten 2 × 2."""
    import bpy
    import tempfile
    from basic import kit
    kit.reset_scene()
    bpy.ops.import_scene.gltf(filepath=os.path.join(dst, 'arms.glb'))
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'STUDIO'
    sc.display.shading.color_type = 'MATERIAL'
    sc.display.shading.show_cavity = True
    sc.display.render_aa = '8'
    sc.render.resolution_x, sc.render.resolution_y = 960, 540
    sc.render.film_transparent = False
    sc.world = bpy.data.worlds.new('W')
    sc.world.color = (0.55, 0.57, 0.60)
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam'))
    sc.collection.objects.link(cam)
    sc.camera = cam
    from mathutils import Vector
    tmp = tempfile.mkdtemp(prefix='ballon_arms_sheet_')
    tiles = []
    for i, (label, pos, at, lens) in enumerate(SHEET):
        cam.data.lens = lens
        cam.location = pos
        cam.rotation_euler = (Vector(at) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = os.path.join(tmp, f'{i}.png')
        bpy.ops.render.render(write_still=True)
        tiles += ['-label', label, sc.render.filepath]
    subprocess.run(['montage', '-font', '/System/Library/Fonts/Supplemental/Arial.ttf', '-pointsize', '20', *tiles,
                    '-tile', '2x2', '-geometry', '+6+6', '-background', '#E9E9E6',
                    '-title', f'{FORMAT} · Rig v{RA.RIG_VERSION} · wieder eingelesenes arms.glb', '-quality', '86',
                    os.path.join(dst, 'contact.jpg')], check=True)


def write(dst, measured):
    M = manifest(measured)
    with open(os.path.join(dst, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(M, f, ensure_ascii=False, indent=1)
        f.write('\n')
    with open(os.path.join(dst, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(readme(json.loads(json.dumps(M, ensure_ascii=False))))
    return M


def blender_main():
    measured = export_files(DST)
    M = write(DST, measured)
    contact_sheet(DST)
    print(f"[export_arms] {FORMAT}: {len(M['segments'])} Segmente, Dreiecke R {M['triangles']['total']['R']} / "
          f"L {M['triangles']['total']['L']}, GLB {measured['glb']['bytes']} B → {DST}", flush=True)


if __name__ == '__main__':
    if '--check' in sys.argv:
        sys.exit(check())
    blender_main()
