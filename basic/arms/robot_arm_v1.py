"""BASIC-Roboterarm v1 (Vorstufe, 24.10.2026: wirkte drahtig – Rohr plus Brett). Nur zum Vergleich; aktuell ist robot_arm.py (v2).

Getrennt von Toolgen (Entscheidung des Nutzers 24.10.2026: „so wie die Waffen, möglichst separat halten“). Maße sind **Startwerte
aus Toolgen** `data/ego_arms.json` (Rig-Version 2) und `data/viewmodels.json › arm` – übernommen mit Quelle, nicht verlinkt.

Segmentrahmen (mm, rechtshändig): Ursprung im Gelenk am Segmentanfang, +Z entlang des Segments, +Y Außen-/Rückseite
(Panzerseite, Handrücken), −Y Innen-/Handflächenseite, +X Daumenseite der rechten Hand (linke Hand: Daumen auf −X).
Jedes Teil: (id, de, Segment, Form, Rolle, Parameter). Formen: box (dx, dy, dz, Mitte), cyl (Achse, r, Länge, Mitte).
"""

SOURCE = 'Toolgen data/ego_arms.json (rig v2) und data/viewmodels.json › arm, gelesen 24.10.2026; Werte als Startwerte übernommen'

HAND_SCALE = 0.65 * 1.4          # viewmodels.arm.hand_scale × ego_arms.rig.scale (Handeinheiten → Meter im Bild)
UPPER_MM, FORE_MM = 320.0, 300.0  # viewmodels.arm.upper_length_m / forearm_length_m
# Kameraraum (Blender: rechts −X, vorn −Y, oben +Z). L = Toolgen-Startwert (weit vorn, damit die Stützhand den Handschutz erreicht);
# R entworfen (Toolgen-Wert −0,10/−0,30/−0,40 knickte den Arm an der BASIC-Hüfte zu stark)
SHOULDER = {'R': (-0.20, -0.05, -0.45), 'L': (0.06, -0.48, -0.48)}
ELBOW_POLE = (-0.5, 0.2, -1.0)   # rechter Ellbogen nach unten außen (links gespiegelt); Toolgen-Start (0,2/0/−1)
WRIST_LIMIT_DEG = 55        # Toolgen ego_arms.limits_degrees.wrist_limit
WRIST_TARGET_DEG = 45       # Toolgen wrist_target
FOREARM_PREF = (-0.30, 0.55, -0.78)   # Handgelenk → Ellbogen, rechter Arm (links gespiegelt): hinten, unten, außen (E)

_s = HAND_SCALE * 1000            # Handeinheiten (m) → mm im Bild
PALM_START, PALM_LEN = 0.014 * _s, 0.082 * _s
PALM_W, PALM_T = 0.086 * _s, 0.042 * _s
KNUCKLE_Z = 0.096 * _s
FINGER_X = [0.028 * _s, 0.0, -0.028 * _s]
FINGER_LINKS = [0.034 * _s, 0.027 * _s, 0.022 * _s]
FINGER_W, FINGER_D = 0.019 * _s, 0.020 * _s
THUMB_BASE = (0.046 * _s, 0.002 * _s, 0.030 * _s)
THUMB_DIR = (0.55, -0.35, 0.75)
THUMB_LINKS = [0.036 * _s, 0.028 * _s, 0.022 * _s]

# Fingerstellungen (Grad je Glied; Daumen: Beugung, Abspreizung, Spitze). Startwerte aus ego_arms.finger_poses, wo fest
# angegeben (open, regrip); Werte für wrap-Posen hier am Griff der Pilotwaffe eingestellt (entworfen).
FINGER_POSES = {
    'open':     dict(f=[[4, 4, 3]] * 3, t=[6, 34, 4]),
    'relaxed':  dict(f=[[18, 22, 14]] * 3, t=[12, 30, 8]),
    'grip':     dict(f=[[62, 74, 48]] * 3, t=[38, 12, 30]),
    'trigger':  dict(f=[[20, 30, 18], [62, 74, 48], [64, 76, 50]], t=[38, 12, 30]),
    'underhand': dict(f=[[52, 66, 44]] * 3, t=[20, 10, 16]),
    'mag_hold': dict(f=[[36, 46, 30]] * 3, t=[30, 24, 20]),
    'pinch':    dict(f=[[46, 56, 36], [70, 80, 56], [74, 82, 58]], t=[46, 18, 34]),
}


def parts():
    """Teile je Segment: (id, de, segment, form, rolle, params). Maße in mm im Segmentrahmen."""
    P = []
    # Oberarm (meist außerhalb des Bildes): Kern, Panzerplatte
    P += [('upper_core', 'Oberarmkern', 'upper', 'cyl', 'graphite', dict(axis='z', r=30, len=290, c=(0, 0, 165))),
          ('upper_plate', 'Oberarmpanzer', 'upper', 'box', 'shell', dict(d=(62, 18, 210), c=(0, 27, 170), bevel=7))]
    # Ellbogen am Anfang des Unterarms
    P += [('elbow', 'Ellbogengelenk', 'fore', 'cyl', 'dark_metal', dict(axis='x', r=27, len=74, c=(0, 0, 0))),
          ('elbow_ring', 'Ellbogenring', 'fore', 'cyl', 'trim', dict(axis='x', r=20, len=80, c=(0, 0, 0)))]
    # Unterarm: Kern, Panzer, Servo unten, Manschette, Gabel zum Handgelenk (Toolgen: core_radius 29,5, cuff 42,5, servo 26×74)
    P += [('fore_core', 'Unterarmkern', 'fore', 'cyl', 'graphite', dict(axis='z', r=29.5, len=262, c=(0, 0, 150))),
          ('fore_plate', 'Unterarmpanzer', 'fore', 'box', 'shell', dict(d=(68, 18, 196), c=(0, 27, 150), bevel=7)),
          ('fore_plate_rear', 'Panzerstufe', 'fore', 'box', 'shell', dict(d=(58, 10, 60), c=(0, 37, 112), bevel=4)),
          ('fore_inset', 'Akzentstreifen', 'fore', 'box', 'accent', dict(d=(5, 1.2, 110), c=(24, 36.4, 160), bevel=0.4)),
          ('fore_servo', 'Unterarmservo', 'fore', 'cyl', 'dark_metal', dict(axis='z', r=17, len=74, c=(0, -24, 150))),
          ('fore_cuff', 'Manschette', 'fore', 'cyl', 'dark_metal', dict(axis='z', r=42.5, len=20, c=(0, 0, 262))),
          ('fore_cuff_trim', 'Manschettenkante', 'fore', 'cyl', 'trim', dict(axis='z', r=43.5, len=3, c=(0, 0, 273))),
          ('fore_fork_a', 'Gelenkgabel', 'fore', 'box', 'dark_metal', dict(d=(8, 26, 30), c=(15, 0, 288), bevel=2)),
          ('fore_fork_b', 'Gelenkgabel', 'fore', 'box', 'dark_metal', dict(d=(8, 26, 30), c=(-15, 0, 288), bevel=2))]
    # Hand: Kardanblock am Ursprung (Handgelenk), Handfläche, Handrückenplatte, Knöchelleiste, Daumensockel
    P += [('wrist_block', 'Kardanblock', 'hand', 'box', 'dark_metal', dict(d=(16, 16, 16), c=(0, 0, 0), bevel=2)),
          ('wrist_pin', 'Kardanbolzen', 'hand', 'cyl', 'trim', dict(axis='x', r=6.5, len=34, c=(0, 0, 0))),
          ('palm', 'Handfläche', 'hand', 'box', 'graphite',
           dict(d=(PALM_W, PALM_T, PALM_LEN), c=(0, 0, PALM_START + PALM_LEN / 2), bevel=6)),
          ('back_plate', 'Handrückenplatte', 'hand', 'box', 'shell',
           dict(d=(PALM_W - 8, 9, PALM_LEN - 12), c=(0, PALM_T / 2 + 3, PALM_START + PALM_LEN / 2 + 2), bevel=4)),
          ('back_inset', 'Handrückenakzent', 'hand', 'box', 'accent',
           dict(d=(PALM_W - 40, 1.0, 8), c=(0, PALM_T / 2 + 7.8, PALM_START + 16), bevel=0.3)),
          ('knuckles', 'Knöchelleiste', 'hand', 'cyl', 'dark_metal', dict(axis='x', r=9, len=PALM_W - 4, c=(0, 2, KNUCKLE_Z - 4))),
          ('thumb_mount', 'Daumensockel', 'hand', 'box', 'graphite',
           dict(d=(18, 26, 30), c=(THUMB_BASE[0] - 6, THUMB_BASE[1], THUMB_BASE[2]), bevel=4))]
    # Finger: je Glied Kern, Rückenplatte, Gelenk (drei Greiffinger)
    for i in range(3):
        for j, L in enumerate(FINGER_LINKS):
            seg = f'f{i}_{j}'
            P += [(f'{seg}_core', f'Finger {i + 1} Glied {j + 1}', seg, 'box', 'graphite',
                   dict(d=(FINGER_W - 2, FINGER_D - 2, L - 4), c=(0, 0, L / 2), bevel=2.5)),
                  (f'{seg}_plate', f'Finger {i + 1} Glied {j + 1} Platte', seg, 'box', 'shell',
                   dict(d=(FINGER_W - 4, 4, L - 8), c=(0, FINGER_D / 2 + 1, L / 2 + 1), bevel=1.5)),
                  (f'{seg}_joint', f'Finger {i + 1} Gelenk {j + 1}', seg, 'cyl', 'dark_metal',
                   dict(axis='x', r=6.2, len=FINGER_W, c=(0, 0, 0)))]
    for j, L in enumerate(THUMB_LINKS):
        seg = f't_{j}'
        P += [(f'{seg}_core', f'Daumen Glied {j + 1}', seg, 'box', 'graphite',
               dict(d=(FINGER_W, FINGER_D, L - 4), c=(0, 0, L / 2), bevel=2.5)),
              (f'{seg}_plate', f'Daumen Glied {j + 1} Platte', seg, 'box', 'shell',
               dict(d=(FINGER_W - 4, 4, L - 8), c=(0, FINGER_D / 2 + 1, L / 2 + 1), bevel=1.5)),
              (f'{seg}_joint', f'Daumengelenk {j + 1}', seg, 'cyl', 'dark_metal', dict(axis='x', r=6.6, len=FINGER_W + 2, c=(0, 0, 0)))]
    return P


SEGMENTS = (['upper', 'fore', 'hand'] + [f'f{i}_{j}' for i in range(3) for j in range(3)] + [f't_{j}' for j in range(3)])
