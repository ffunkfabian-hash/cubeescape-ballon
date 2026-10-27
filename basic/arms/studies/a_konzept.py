"""Formstudie A „Konzept“ (0.23): Elfenbeinplatten über schwarzer Mechanik wie im Zielbild robot-concept.png.

Schlanke Glieder; der Graphitkörper bleibt an Unterseite, Fugen und Gelenken sichtbar. Unterarm mit zwei getrennten Platten
(hinten größer, vorn verjüngt), dunkle zweite Lage mit zwei Bolzen, ein Hydraulikkolben an der Daumenseite, offenes Handgelenk
mit Drehring. Hand dunkel mit einer Rückenplatte; Finger mit Platten auf Grund- und Mittelglied, Spitzen dunkel.
"""
from basic.arms.studies import (skeleton, bulk, loft, wrap, tube, cyl, box, tab, digits, sec,
                                PALM_W, PALM_T, KNUCKLE_Z, FINGER_X, FINGER_W, FINGER_D, THUMB_BASE)

skeleton(globals())
STUDY = dict(id='a_konzept', de='A „Konzept“', idea='Elfenbeinplatten über sichtbarer schwarzer Mechanik, schlank, offene Gelenke')

UPPER = tab([(10, 40, 38, 0), (160, 42, 40, 0), (300, 35, 33, 0)])
CORE = tab([(-6, 30, 30, 0), (20, 36, 35, 0), (100, 40, 38, 0), (210, 31, 29, 0), (290, 25, 23, 0)])
PLATE_A = tab([(22, 37.5, 36.5, 0), (100, 41.5, 39.5, 0), (148, 39, 37, 0)])
PLATE_B = tab([(154, 38, 36, 0), (210, 33, 31, 0), (254, 28.5, 26.5, 0)])
PALM = tab([(8, 34, 19, 0), (30, 45, 22.9, 0), (72, 47, 22.9, 0), (92, 45.5, 20, 0)])


def parts():
    P = []
    # Oberarm: Graphitkörper, eine Platte
    P += [loft('upper_core', 'Oberarmkörper', 'upper', 'graphite', [UPPER(z, n=2.4) for z in (10, 160, 300)] + [sec(326, 28, 27, n=2.2)]),
          wrap('upper_plate', 'Oberarmplatte', 'upper', 'shell', [UPPER(z, 1.5) for z in (40, 150, 262)], -115, 115, 5)]
    # Ellbogen: Medaillon (Scheibe, blanker Ring, Nabe)
    P += [cyl('elbow', 'Ellbogengelenk', 'fore', 'dark_metal', 'x', 31, 76, (0, 0, 0)),
          cyl('elbow_disc', 'Ellbogenscheibe', 'fore', 'graphite', 'x', 28, 82, (0, 0, 0)),
          cyl('elbow_ring', 'Ellbogenring', 'fore', 'trim', 'x', 21, 85, (0, 0, 0)),
          cyl('elbow_hub', 'Ellbogennabe', 'fore', 'dark_metal', 'x', 12, 88, (0, 0, 0))]
    # Unterarm: Körper, zwei Platten mit Fuge, dunkle Lage mit Bolzen, Kolben, Drehring am Handgelenk
    top_b = lambda z: PLATE_B(z)['b'] + 4.5          # Oberkante der vorderen Platte
    P += [loft('fore_core', 'Unterarmkörper', 'fore', 'graphite', [CORE(z, n=2.5) for z in (-6, 20, 100, 210, 290)]),
          wrap('fore_plate_a', 'Unterarmplatte hinten', 'fore', 'shell', [PLATE_A(z) for z in (22, 60, 100, 148)], -84, 84, 5.5),
          cyl('plate_screw_a', 'Schraube', 'fore', 'trim', 'y', 2.6, 3, (-16, PLATE_A(136)['b'] + 5.6, 136)),
          cyl('plate_screw_b', 'Schraube', 'fore', 'trim', 'y', 2.6, 3, (16, PLATE_A(136)['b'] + 5.6, 136)),
          wrap('fore_plate_b', 'Unterarmplatte vorn', 'fore', 'shell',
               [PLATE_B(154), PLATE_B(210), PLATE_B(254, a0=-58, a1=58)], -84, 84, 4.5),
          wrap('fore_inset', 'Handgelenkplatte', 'fore', 'anodized', [PLATE_B(z, 4.6) for z in (168, 200, 238)], -24, 24, 1.8,
               steps=8),
          cyl('fore_bolt_a', 'Bolzen', 'fore', 'trim', 'y', 3.2, 3, (-11, top_b(224) + 1.6, 224)),
          cyl('fore_bolt_b', 'Bolzen', 'fore', 'trim', 'y', 3.2, 3, (11, top_b(224) + 1.6, 224)),
          tube('piston', 'Hydraulikzylinder', 'fore', 'dark_metal', [(38, 4, 40), (34, 3, 170)], 6.5),
          tube('piston_rod', 'Kolbenstange', 'fore', 'trim', [(34.4, 3.1, 164), (26, 2, 262)], 3.0),
          cyl('piston_mount', 'Kolbenlager', 'fore', 'dark_metal', 'x', 7.5, 10, (35, 4, 40)),
          wrap('wrist_ring', 'Drehring', 'fore', 'dark_metal', [sec(262, 24, 22.5, n=2.3), sec(298, 23, 21.5, n=2.3)], -180, 180, 5),
          wrap('wrist_ring_trim', 'Drehring Kante', 'fore', 'trim', [sec(266, 24.3, 22.8, n=2.3), sec(269, 24.3, 22.8, n=2.3)],
               -180, 180, 5.4, sub=1)]
    # Hand: Kardan, dunkle Handfläche, eine Rückenplatte, Knöchelwelle, Daumensockel
    P += [loft('wrist_block', 'Kardanblock', 'hand', 'dark_metal', [sec(-16, 17, 15, n=2.4), sec(14, 19, 17, n=2.4)]),
          cyl('wrist_pin', 'Kardanbolzen', 'hand', 'trim', 'x', 7, 44, (0, 0, 0)),
          loft('palm', 'Handfläche', 'hand', 'graphite', [PALM(z, n=3.4) for z in (8, 30, 72, 92)]),
          wrap('back_plate', 'Handrückenplatte', 'hand', 'shell',
               [PALM(20, 1.0, n=3.4, a0=-46, a1=46), PALM(46, 1.0, n=3.4), PALM(82, 1.0, n=3.4)], -62, 62, 4.5),
          cyl('knuckles', 'Knöchelwelle', 'hand', 'dark_metal', 'x', 8.5, PALM_W - 6, (0, 3, KNUCKLE_Z - 3)),
          box('thumb_mount', 'Daumensockel', 'hand', 'graphite', (22, 30, 34), (THUMB_BASE[0] - 7, THUMB_BASE[1], THUMB_BASE[2]), 6)]
    # Finger: dunkler Kern, Gelenk; Platten auf Grund- und Mittelglied, Spitze dunkel gerundet
    for seg, L, tip, thumb in digits():
        w, d = FINGER_W + (2 if thumb else 0), FINGER_D + (1 if thumb else 0)
        a, b = w / 2 - 2.2, d / 2 - 2.2
        core = [sec(2, a, b, n=3), sec(L - 2, a - 0.4, b - 0.6, n=3)] if not tip else \
               [sec(2, a, b, n=3), sec(L - 7, a - 0.4, b - 0.6, n=3), sec(L, a - 2.6, b - 3.6, n=2.4)]
        P += [loft(f'{seg}_core', 'Fingerglied', seg, 'graphite', core, ring=24, sub=3),
              cyl(f'{seg}_joint', 'Fingergelenk', seg, 'dark_metal', 'x', 6, w - 1, (0, 0, 0))]
        if not tip:
            P += [wrap(f'{seg}_plate', 'Fingerplatte', seg, 'shell',
                       [sec(4, a + 0.6, b + 0.6, n=3, a0=-55, a1=55), sec(L - 3, a + 0.2, b, n=3)], -72, 72, 2.6, sub=3, steps=12)]
    return bulk(P, 1.2)
