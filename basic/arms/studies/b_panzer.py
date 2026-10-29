"""Formstudie B „Panzer“ (0.23): geschlossener Panzerhandschuh nach den Destiny-Handschuhen (Q-D2-ARM, nur Prinzipien).

Große ruhige Cremeschale: Armschiene bis kurz vor das Handgelenk, getrennt durch eine dunkle Fuge von der aufgeweiteten Stulpe,
die über die Hand greift. Zweite Lage als dunkle Pfeilplatte mit zwei Bolzen, eine orange Akzentlinie an der Stulpe; Medaillon am
Ellbogen. Hand mit dicker Rückenschale und Knöchelschutz, Finger durchgehend gepanzert, Spitzen zugespitzt.
"""
from basic.arms.studies import (skeleton, bulk, loft, wrap, cyl, box, tab, digits, sec,
                                PALM_W, KNUCKLE_Z, FINGER_W, FINGER_D, THUMB_BASE)

skeleton(globals())
STUDY = dict(id='b_panzer', de='B „Panzer“', idea='geschlossene Cremeschale, Stulpe über der Hand, kräftige gepanzerte Faust')

UPPER = tab([(20, 44, 42, 0), (150, 50, 48, 0), (282, 45, 43, 0), (308, 37, 35, 0)])
CORE = tab([(0, 40, 40, 0), (110, 45, 43, 0), (290, 30, 28, 0)])
BRACER = tab([(16, 43, 42, 0), (110, 49.5, 47.5, 0), (228, 41, 38.5, 0)])
CUFF = tab([(236, 39.5, 37, 0), (290, 40.5, 37.5, 0), (320, 46, 42, 0)])
PALM = tab([(8, 34, 19, 0), (30, 45, 22.9, 0), (72, 47, 22.9, 0), (92, 45.5, 20, 0)])


def parts():
    P = []
    P += [loft('upper_core', 'Oberarmkörper', 'upper', 'graphite', [sec(10, 40, 38), sec(300, 36, 34), sec(328, 30, 29)]),
          loft('upper_shell', 'Oberarmschale', 'upper', 'shell', [UPPER(z, n=2.8) for z in (20, 150, 282, 308)])]
    # Ellbogen: großes Medaillon wie Arm v3
    P += [cyl('elbow', 'Ellbogengelenk', 'fore', 'dark_metal', 'x', 40, 100, (0, 0, 0)),
          cyl('elbow_disc', 'Ellbogenscheibe', 'fore', 'graphite', 'x', 36, 106, (0, 0, 0)),
          cyl('elbow_ring', 'Ellbogenring', 'fore', 'trim', 'x', 27, 110, (0, 0, 0)),
          cyl('elbow_hub', 'Ellbogennabe', 'fore', 'graphite', 'x', 19, 113, (0, 0, 0))]
    # Unterarm: Körper (nur in der Fuge und unten im Schlitz sichtbar), Armschiene, Stulpe, Pfeilplatte, Akzentlinie
    top = lambda z: BRACER(z)['b'] + 6
    P += [loft('fore_core', 'Unterarmkörper', 'fore', 'graphite', [CORE(z) for z in (0, 110, 290)] + [sec(306, 28, 26)]),
          wrap('bracer', 'Armschiene', 'fore', 'shell', [BRACER(z, n=2.8) for z in (16, 60, 110, 170, 228)], -150, 150, 6),
          wrap('cuff', 'Stulpe', 'fore', 'shell', [CUFF(z, n=2.8) for z in (236, 290, 320)], -150, 150, 5),
          wrap('arrow_plate', 'Pfeilplatte', 'fore', 'anodized',
               [BRACER(60, 6.4, n=2.8, a0=-30, a1=30), BRACER(170, 6.4, n=2.8, a0=-26, a1=26),
                BRACER(222, 6.4, n=2.8, a0=-2, a1=2)], -30, 30, 3, steps=10),
          cyl('fore_bolt_a', 'Bolzen', 'fore', 'trim', 'y', 3.6, 3, (-10, top(96) + 4.2, 96)),
          cyl('fore_bolt_b', 'Bolzen', 'fore', 'trim', 'y', 3.6, 3, (10, top(96) + 4.2, 96)),
          wrap('cuff_line', 'Akzentlinie', 'fore', 'accent', [CUFF(300, 5.1, n=2.8), CUFF(304, 5.1, n=2.8)], -150, 150, 1.0, sub=1)]
    # Hand: Kardan, Handfläche, dicke Rückenschale, Knöchelschutz, Daumensockel
    P += [loft('wrist_block', 'Kardanblock', 'hand', 'dark_metal', [sec(-16, 18, 16), sec(14, 20, 18)]),
          cyl('wrist_pin', 'Kardanbolzen', 'hand', 'trim', 'x', 7, 44, (0, 0, 0)),
          loft('palm', 'Handfläche', 'hand', 'graphite', [PALM(z, n=3.4) for z in (8, 30, 72, 92)]),
          wrap('back_shell', 'Handrückenschale', 'hand', 'shell',
               [PALM(8, 1.0, n=3.2, a0=-50, a1=50), PALM(40, 1.0, n=3.2), PALM(80, 1.0, n=3.2)], -76, 76, 7),
          wrap('knuckle_guard', 'Knöchelschutz', 'hand', 'dark_metal', [PALM(82, 1.0, n=3.2), PALM(96, 0.5, n=3.2)], -80, 80, 6.5,
               sub=2),
          box('thumb_mount', 'Daumensockel', 'hand', 'graphite', (24, 32, 36), (THUMB_BASE[0] - 7, THUMB_BASE[1], THUMB_BASE[2]), 7)]
    # Finger: schlanker Kern, Gelenk, Cremeplatte auf jedem Glied; Spitze zugespitzt
    for seg, L, tip, thumb in digits():
        w, d = FINGER_W + (2 if thumb else 0), FINGER_D + (1 if thumb else 0)
        a, b = w / 2 - 2.6, d / 2 - 2.6
        P += [loft(f'{seg}_core', 'Fingerglied', seg, 'graphite', [sec(1, a, b, n=3), sec(L - 1, a - 0.5, b - 0.5, n=3)], ring=24, sub=2),
              cyl(f'{seg}_joint', 'Fingergelenk', seg, 'dark_metal', 'x', 6.6, w + 0.5, (0, 0, 0))]
        plate = [sec(3, a + 0.8, b + 0.6, n=3, a0=-60, a1=60), sec(L - 3, a + 0.6, b + 0.4, n=3)] if not tip else \
                [sec(3, a + 0.8, b + 0.6, n=3, a0=-60, a1=60), sec(L - 6, a + 0.4, b + 0.2, n=3), sec(L + 2, a - 2.4, b - 3.0, n=2.4)]
        P += [wrap(f'{seg}_plate', 'Fingerplatte', seg, 'shell', plate, -80, 80, 3.4, sub=3, steps=14)]
    return bulk(P, 1.1)
