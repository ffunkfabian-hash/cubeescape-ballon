"""Baugruppe Unterkörper: Becken, Gürtelring, Lendenplatte mit Pfeilschnitt, Hüftplatten, Hüftachse mit Medaillon. Segment pelvis
(Ursprung 170 mm unter Socket_Waist, +Z nach oben, +Y vorn, +X rechte Körperseite).

0.23 „Gauntlet“: Formsprache von Arm v3 (siehe upper_body.py); die Lendenplatte wiederholt den Pfeilschnitt der Brust. Runde 2
(Q-D2-PARADE): breiteres Becken, längere Lendenplatte, Hüftplatten decken den Oberschenkelansatz.
"""
from .shapes import loft, wrap, ring, tab, arrow, sec

SEGMENTS = ['pelvis']
HIP_Z = 40          # Hüftgelenk über dem Segmentursprung (= Socket_Hip)
HIP_X = 116

PELVIS = tab([(-24, 140, 88, -4), (60, 150, 94, -4), (140, 116, 76, -4), (196, 86, 66, -4)], ch=38)


def parts():
    P = [loft('pelvis_core', 'Becken', 'pelvis', 'graphite', [PELVIS(z) for z in (-24, 60, 140, 196)]),
         ring('belt', 'Gürtelring', 'pelvis', 'dark_metal', 128, 154, 120, 82, 8, n=2.8),
         # Lendenplatte: Cremeschale vorn, läuft nach unten im Pfeilschnitt aus
         wrap('tasset', 'Lendenplatte', 'pelvis', 'shell',
              arrow(PELVIS, 20, -90, -38, 38, 2.0, tip=5)[::-1] + [PELVIS(118, 2.0, a0=-42, a1=42)], -38, 38, 8)]
    for side, sx in (('r', 1), ('l', -1)):
        # Runde 4 („Hüfte und Beine passen nicht“): Beintasche hängt vom Gürtel außen über den Oberschenkelansatz und weitet sich
        # nach unten (statt einer kleinen Hüftplatte neben dem Bein); Hüftgelenk liegt darunter
        P += [wrap(f'tasset_side_{side}', 'Beintasche', 'pelvis', 'shell',
                   [sec(-120, 212, 104, -4, ch=30), sec(-10, 178, 100, -4, ch=36), sec(116, 156, 98, -4, ch=36)],
                   sx * 90 - 26, sx * 90 + 26, 8),
              (f'hip_joint_{side}', 'Hüftgelenk', 'pelvis', 'cyl', 'dark_metal', dict(axis='x', r=46, len=84, c=(sx * HIP_X, 0, HIP_Z)))]
    return P
