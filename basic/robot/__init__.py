"""BASIC-Roboter: eigenständiges Modell für die Außenansicht zu den Ego-Armen, zerlegt in fünf Baugruppen.

Nutzerwunsch 24.10.2026: „Wichtig ist das der Roboter seperat gehalten wird! Er soll auch in Bauteile ‚zerlegt‘ werden. Kopf, Arme,
Ober & Unterkörper, Beine“. Getrennt von Waffen (basic/weapons) und Ego-Animation (basic/arms/ego.py); nur die Arme lesen den
Ego-Arm (gekoppelt, siehe arms.py). 0.23 „Gauntlet“ (Nutzer 27.10.2026: „Aber ich wünsche mir ja von dir das du einen passenden
Roboter zu den Ego-Ansichten baust“ – „Der Roboter soll den Stilanforderungen von Ego v3 und Waffen entsprechen“): Körper neu in der
Formsprache von Arm v3 (Formen loft/wrap aus basic/arms/forms.py); Struktur, Anker und Prüfung aus 0.5.

Welt (mm): Figur steht auf z = 0, schaut nach −Y, rechte Körperseite bei −X. Segmente: (name, A, B, hint, Seite) – Rahmen +Z von A
nach B, +Y = hint (Vorder-/Panzerseite); Seite 'R'/'L' spiegelt die Teile an X ('C' Mitte). Teile: (id, de, segment-typ, form,
rolle, params) wie basic/arms/robot_arm.py. Gebaut, gerendert und geprüft von tools/robot_build.py.
"""
from . import head, arms, upper_body, lower_body, legs

META = dict(id='BASIC-ROBOT', name_de='BASIC-Roboter', version='0.23', status='Entwurf (Außenansicht zu den Ego-Armen v3, nicht exportiert)')

ASSEMBLIES = [
    dict(id='head', de='Kopf', en='Head', module=head),
    dict(id='arms', de='Arme', en='Arms', module=arms),
    dict(id='upper_body', de='Oberkörper', en='Upper body', module=upper_body),
    dict(id='lower_body', de='Unterkörper', en='Lower body', module=lower_body),
    dict(id='legs', de='Beine', en='Legs', module=legs),
]

# 0.23 nach Nutzerkritik („lang und schlaksig … irgendwie klotzig“, Referenz Q-D2-PARADE, nur Prinzipien): kompakt-heroisch statt
# langbeinig – Hüfte bei der halben Höhe (910 statt 1000 mm), Oberschenkel und Schienbein gleich lang, kurzer Hals (Helm sitzt im Kragen),
# Schultern tiefer und breiter (±250 mm bei 1400 statt ±235 bei 1440)
# Runde 3 („klotzig und steif“): Haltung statt Strammstehen – Rumpf 4° vorgeneigt und 9° zur Mündung gedreht, Kopf weiter zur
# Mündung (20°) und leicht gesenkt; Standbein links, rechtes Knie locker (legs.JOINTS). Die Schultern folgen dem Rumpfrahmen.
WAIST = (0, 0, 1040)
NECK = (0, -28, 1439)
PELVIS = (0, 0, 870)          # Ursprung des Beckensegments
HEAD_H = 260
TORSO_HINT = (0.16, -1, 0)    # Vorderseite des Rumpfs (+Y lokal); x > 0 dreht zur Mündung (links vorn)
HEAD_HINT = (0.36, -1, 0)
HEAD_TOP = (0, NECK[1] - 22, NECK[2] + HEAD_H)
SHOULDER_LOCAL = (250, 0, 360)   # Socket_Shoulder im Rumpfrahmen (upper_body.SHOULDER_X/Z)


def _frame(A, B, hint):
    """Segmentrahmen wie tools/ego_build.frame_from: z von A nach B, y = hint senkrecht dazu, x = y × z (Spalten x, y, z)."""
    z = [b - a for a, b in zip(A, B)]
    L = sum(v * v for v in z) ** 0.5
    z = [v / L for v in z]
    d = sum(h * v for h, v in zip(hint, z))
    y = [h - d * v for h, v in zip(hint, z)]
    L = sum(v * v for v in y) ** 0.5
    y = [v / L for v in y]
    x = [y[1] * z[2] - y[2] * z[1], y[2] * z[0] - y[0] * z[2], y[0] * z[1] - y[1] * z[0]]
    return x, y, z


def _torso_point(local):
    x, y, z = _frame(WAIST, NECK, TORSO_HINT)
    return tuple(round(WAIST[i] + local[0] * x[i] + local[1] * y[i] + local[2] * z[i], 3) for i in range(3))


SHOULDER = {'R': _torso_point(SHOULDER_LOCAL), 'L': _torso_point((-SHOULDER_LOCAL[0],) + SHOULDER_LOCAL[1:])}

# Anker zwischen den Baugruppen (Welt, mm, Grundhaltung): Elternbaugruppe → Kindbaugruppe
ANCHORS = {
    'Socket_Neck': dict(pos=NECK, parent='upper_body', child='head', de='Hals'),
    'Socket_Shoulder_R': dict(pos=SHOULDER['R'], parent='upper_body', child='arms', side='R', de='Schulter rechts'),
    'Socket_Shoulder_L': dict(pos=SHOULDER['L'], parent='upper_body', child='arms', side='L', de='Schulter links'),
    'Socket_Waist': dict(pos=WAIST, parent='upper_body', child='lower_body', de='Taille'),
    'Socket_Hip_R': dict(pos=legs.JOINTS['R'][0], parent='lower_body', child='legs', side='R', de='Hüfte rechts'),
    'Socket_Hip_L': dict(pos=legs.JOINTS['L'][0], parent='lower_body', child='legs', side='L', de='Hüfte links'),
}

# Armhaltungen. ready (nach Zielbild): Pilotwaffe diagonal vor dem Körper, Griff rechts vor dem Bauch, Mündung vorn links gesenkt, Hände an den Griffen
# aus basic/arms/ego.GRIPS, Zwei-Knochen-IK mit Ellbogen-Pol. idle: ohne Waffe, Arme hängen leicht gebeugt (Richtungen je Glied).
POSES = {
    'ready': dict(weapon='pilot.w01_auto_rifle_v21', pos=(-120, -250, 1150), rot_z=34, rot_x=24,
                  hands={'R': dict(grip='grip', pole=(-0.6, 0.5, -0.5)), 'L': dict(grip='support', pole=(0.7, 0.2, -0.6))}),
    'idle': dict(weapon=None, upper=(-0.16, 0.02, -1.0), fore=(-0.03, -0.30, -1.0), fingers='relaxed'),
}

# Material (0.23): Standard-Skin der Waffen und Ego-Arme – der Roboter soll zu Arm v3 und den Waffen passen (Nutzer 27.10.2026);
# der wärmere, gebrauchte Skin „einsatz“ aus 0.5 (Zielbild) entfällt
SKIN = dict(name='standard', de='Standard', kind='Farbe', roles={})

# Explosionsansicht (mm, Welt): grafische Auseinanderziehung entlang der Anker, Oberkörper bleibt stehen
EXPLODE = {'head': (0, 0, 260), 'upper_body': (0, 0, 0), 'arms': (300, 0, 40), 'lower_body': (0, 0, -170), 'legs': (90, 0, -360)}


def asm_of_segment(kind):
    """Baugruppe zu einem Segmenttyp (head, torso, …, upper, fore, hand, f0_0, …)."""
    for a in ASSEMBLIES:
        if kind in a['module'].SEGMENTS:
            return a['id']
    return None


def segments():
    """Rumpfsegmente in der Grundhaltung (die Arme setzt tools/robot_build.py je Haltung)."""
    S = [('pelvis', PELVIS, WAIST, (0, -1, 0), 'C'),
         ('torso', WAIST, NECK, TORSO_HINT, 'C'),
         ('head', NECK, HEAD_TOP, HEAD_HINT, 'C')]
    for side, (hip, knee, ankle, toe) in legs.JOINTS.items():
        S += [(f'thigh_{side}', hip, knee, (0, -1, 0), side),
              (f'shin_{side}', knee, ankle, (0, -1, 0), side),
              (f'foot_{side}', ankle, toe, (0, 0, 1), side)]
    return S


def parts():
    """Alle Teile mit Baugruppe: Liste von (asm, (id, de, segment, form, rolle, params))."""
    return [(a['id'], p) for a in ASSEMBLIES for p in a['module'].parts()]


def validate():
    """Konsistenz ohne Blender (für ./check): Teile je Baugruppe, Zuordnung eindeutig, Anker passen zu Segmenten und Baugruppen."""
    err = []
    ids = {a['id'] for a in ASSEMBLIES}
    seg_owner = {}
    for a in ASSEMBLIES:
        for s in a['module'].SEGMENTS:
            if s in seg_owner:
                err.append(f"Segment {s} in {seg_owner[s]} und {a['id']}")
            seg_owner[s] = a['id']
    seen = {}
    for a in ASSEMBLIES:
        P = a['module'].parts()
        if not P:
            err.append(f"Baugruppe {a['id']} ohne Teile")
        for pid, de, seg, kind, role, p in P:
            if pid in seen:
                err.append(f"Teil {pid} in {seen[pid]} und {a['id']}")
            seen[pid] = a['id']
            if seg_owner.get(seg) != a['id']:
                err.append(f"Teil {pid}: Segment {seg} gehört nicht zu {a['id']}")
            if not de or kind not in ('hull', 'hulls', 'cyl', 'box', 'plate', 'prism', 'loft', 'wrap', 'tube'):
                err.append(f'Teil {pid}: Bezeichnung oder Form fehlt')
    segs = {s[0]: s for s in segments()}
    joint = {'Socket_Neck': [segs['head'][1], segs['torso'][2]], 'Socket_Waist': [segs['torso'][1], segs['pelvis'][2]],
             'Socket_Hip_R': [segs['thigh_R'][1]], 'Socket_Hip_L': [segs['thigh_L'][1]],
             'Socket_Shoulder_R': [SHOULDER['R']], 'Socket_Shoulder_L': [SHOULDER['L']]}
    for k, A in ANCHORS.items():
        if not k.startswith('Socket_'):
            err.append(f'Anker {k}: Name ohne Socket_')
        if A['parent'] not in ids or A['child'] not in ids or A['parent'] == A['child']:
            err.append(f'Anker {k}: Baugruppen {A["parent"]} → {A["child"]} ungültig')
        for q in joint.get(k, [None]):
            if q is None or tuple(q) != tuple(A['pos']):
                err.append(f'Anker {k}: Lage {A["pos"]} passt nicht zum Gelenk {q}')
    reach, todo = {'upper_body'}, True
    while todo:
        todo = False
        for A in ANCHORS.values():
            if A['parent'] in reach and A['child'] not in reach:
                reach.add(A['child'])
                todo = True
    if reach != ids:
        err.append(f'Baugruppen ohne Anker: {sorted(ids - reach)}')
    if set(EXPLODE) != ids:
        err.append('EXPLODE deckt nicht alle Baugruppen ab')
    return err
