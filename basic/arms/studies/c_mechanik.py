"""Formstudie C „Mechanik“ (0.23): Exoskelett mit sichtbarer Funktion, nur ein kleines Elfenbeinschild je Glied.

Unterarm aus zwei Graphitschienen mit offenem Raum dazwischen, darin ein Stellzylinder mit blanker Kolbenstange zum Handgelenk;
Handgelenkkragen verbindet die Schienen; ein Schlauch an der Außenseite; Schild oben mit zwei Lüftungsschlitzen. Großes offenes
Ellbogenlager. Hand mit dunklem Rahmen, kleinem Schild, Einzelknöcheln; schlanke Finger mit Gelenkscheiben, ohne Platten.
"""
from basic.arms.studies import (skeleton, bulk, loft, wrap, tube, cyl, box, tab, digits, sec,
                                KNUCKLE_Z, FINGER_X, FINGER_W, FINGER_D, THUMB_BASE)

skeleton(globals())
STUDY = dict(id='c_mechanik', de='C „Mechanik“', idea='Exoskelett: Schienen, Stellzylinder, Schlauch, kleines Schild')

PALM = tab([(8, 33, 18, 0), (30, 44, 21.5, 0), (72, 46, 21.5, 0), (92, 44.5, 19, 0)])
GUARD = tab([(40, 28, 33, 2), (130, 30, 34, 2), (205, 24, 28, 2)])


def parts():
    P = []
    P += [loft('upper_core', 'Oberarmkörper', 'upper', 'graphite', [sec(10, 36, 34), sec(170, 37, 35), sec(326, 26, 25)]),
          wrap('upper_guard', 'Oberarmschild', 'upper', 'shell', [sec(z, 37.5, 35.5) for z in (70, 160, 250)], -55, 55, 5)]
    # Ellbogen: offenes Lager
    P += [cyl('elbow', 'Ellbogenlager', 'fore', 'dark_metal', 'x', 34, 96, (0, 0, 0)),
          cyl('elbow_ring', 'Lagerring', 'fore', 'trim', 'x', 26, 100, (0, 0, 0)),
          cyl('elbow_hub', 'Lagernabe', 'fore', 'graphite', 'x', 15, 104, (0, 0, 0))]
    # Unterarm: zwei Schienen, Stellzylinder mit Kolbenstange, Kragen, Schild mit Schlitzen, Schlauch
    for side, sx in (('r', -1), ('l', 1)):
        P += [loft(f'rail_{side}', 'Schiene', 'fore', 'graphite',
                   [sec(-8, 10, 27, x=sx * 27, n=3.2), sec(120, 10.5, 29, x=sx * 27, n=3.2), sec(268, 8.5, 21, x=sx * 19, n=3.2)])]
    P += [loft('actuator', 'Stellzylinder', 'fore', 'dark_metal', [sec(24, 17, 17, n=2), sec(178, 17, 17, n=2), sec(186, 13, 13, n=2)],
               ring=32),
          tube('actuator_rod', 'Kolbenstange', 'fore', 'trim', [(0, 0, 180), (0, 0, 268)], 7.5),
          wrap('collar', 'Handgelenkkragen', 'fore', 'dark_metal', [sec(258, 27, 23, n=3), sec(292, 25, 21.5, n=3)], -180, 180, 6),
          wrap('guard', 'Unterarmschild', 'fore', 'shell', [GUARD(z) for z in (40, 130, 205)], -48, 48, 5,
               cuts=[dict(c=(0, 40, z), d=(34, 14, 6)) for z in (96, 112)]),
          tube('hose', 'Schlauch', 'fore', 'rubber', [(-30, 18, 24), (-37, 22, 120), (-30, 14, 220), (-20, 6, 262)], 4.2)]
    # Hand: dunkler Rahmen, kleines Schild, Einzelknöchel
    P += [loft('wrist_block', 'Kardanblock', 'hand', 'dark_metal', [sec(-16, 17, 15), sec(14, 19, 17)]),
          cyl('wrist_pin', 'Kardanbolzen', 'hand', 'trim', 'x', 7, 44, (0, 0, 0)),
          loft('palm', 'Handfläche', 'hand', 'graphite', [PALM(z, n=3.4) for z in (8, 30, 72, 92)]),
          wrap('back_frame', 'Handrückenrahmen', 'hand', 'dark_metal', [PALM(z, 0.8, n=3.4) for z in (14, 46, 82)], -58, 58, 3.5),
          wrap('back_shield', 'Handrückenschild', 'hand', 'shell', [PALM(z, 4.4, n=3.4) for z in (28, 50, 72)], -38, 38, 3),
          box('thumb_mount', 'Daumensockel', 'hand', 'graphite', (20, 28, 32), (THUMB_BASE[0] - 7, THUMB_BASE[1], THUMB_BASE[2]), 5)]
    P += [cyl(f'knuckle_{i}', 'Knöchel', 'hand', 'dark_metal', 'x', 8.5, FINGER_W - 1, (x, 2, KNUCKLE_Z - 3)) for i, x in enumerate(FINGER_X)]
    # Finger: schlanke Kerne mit Gelenkscheiben (blanker Ring), keine Platten
    for seg, L, tip, thumb in digits():
        w, d = FINGER_W + (2 if thumb else 0), FINGER_D + (1 if thumb else 0)
        a, b = w / 2 - 3.0, d / 2 - 2.4
        core = [sec(1, a, b, n=3.2), sec(L - 1, a - 0.6, b - 0.8, n=3.2)] if not tip else \
               [sec(1, a, b, n=3.2), sec(L - 6, a - 0.6, b - 0.8, n=3.2), sec(L + 1, a - 2.6, b - 3.6, n=2.4)]
        P += [loft(f'{seg}_core', 'Fingerglied', seg, 'graphite', core, ring=24, sub=3),
              cyl(f'{seg}_joint', 'Fingergelenk', seg, 'dark_metal', 'x', 6.4, w - 2, (0, 0, 0)),
              cyl(f'{seg}_cap', 'Gelenkscheibe', seg, 'trim', 'x', 3.6, w, (0, 0, 0))]
    return bulk(P, 1.18)
