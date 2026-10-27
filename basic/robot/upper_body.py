"""Baugruppe Oberkörper: Rumpf, Brustplatte mit Pfeilschnitt, dunkle Brustlage mit zwei Bolzen, Rückenplatte, hoher Kragen, offene
Taille mit Wirbelringen, Schultergelenke mit Schulterpanzer und Medaillon. Segment torso (Ursprung Socket_Waist, +Z nach oben,
+Y vorn, +X rechte Körperseite).

0.23 „Gauntlet“ (Nutzer 27.10.2026: „Aber ich wünsche mir ja von dir das du einen passenden Roboter zu den Ego-Ansichten baust“ –
„Der Roboter soll den Stilanforderungen von Ego v3 und Waffen entsprechen“): Formsprache von Arm v3 – Graphitkörper, ruhige
Cremeschale mit Pfeilschnitt, zweite dunkle Lage mit zwei Bolzen, Medaillon, eine Akzentlinie, gefaste Querschnitte wie
robot_arm.section – und das Schlichtheitsbudget der Waffen (keine Kolben und Kabel als Zierde). Negativraum: die offene Taille.
Runde 2 („lang und schlaksig … irgendwie klotzig“, Q-D2-PARADE): breite, tiefe Brust, große gefaste Schulterpanzer, die über den
Oberarm greifen, hoher Kragen, in dem der Helm sitzt.
"""
from .shapes import loft, wrap, ring, tab, arrow, two_bolts, medallion, sec

SEGMENTS = ['torso']
SHOULDER_X, SHOULDER_Z = 250, 360          # Socket_Shoulder im Rumpfrahmen (Welt 1400 − Taille 1040)

# Rumpfkörper (z, Halbbreite a, Halbtiefe b, Mitte y): breite, tiefe Brust, Taille schmaler
# Runde 4 („Schultern und Oberkörper passen nicht“): oben Schultergürtel bis fast an die Schulter, der Panzer liegt darauf
CORE = tab([(30, 104, 78, -4), (150, 150, 104, -2), (270, 184, 116, -6), (330, 206, 110, -8), (384, 186, 98, -10), (424, 100, 78, -10)], ch=48)
CHEST_GROW = 2.0
CHEST_T = 10.0


def parts():
    P = [loft('waist_core', 'Taillenkern', 'torso', 'graphite', [sec(-40, 76, 62, n=2.2), sec(46, 84, 68, n=2.2)]),
         ring('waist_ring_a', 'Wirbelring', 'torso', 'dark_metal', -14, -2, 80, 66, 6),
         ring('waist_ring_b', 'Wirbelring', 'torso', 'dark_metal', 10, 22, 82, 68, 6),
         loft('torso_core', 'Rumpf', 'torso', 'graphite', [CORE(z) for z in (30, 150, 270, 330, 384, 424)]),
         loft('collar', 'Kragen', 'torso', 'graphite', [sec(388, 126, 92, -10, ch=34), sec(440, 98, 82, -8, ch=28),
                                                        sec(452, 88, 76, -8, ch=24)])]
    # Brustplatte: ruhige Cremeschale über der Vorderseite, Pfeilschnitt nach unten zur Taille (Motiv der Unterarmschale)
    P += [wrap('chest', 'Brustplatte', 'torso', 'shell',
               arrow(CORE, 160, 100, -66, 66, CHEST_GROW, tip=6)[::-1]
               + [CORE(z, CHEST_GROW, a0=-72, a1=72) for z in (230, 310)]
               + [CORE(380, CHEST_GROW, a0=-56, a1=56)], -66, 66, CHEST_T),
          # zweite dunkle Lage mit Pfeilschnitt und zwei Bolzen (wie die Handgelenkplatte), darunter eine Akzentlinie auf der Mitte
          # (wie die Linie auf der Unterarmschale); beide zeigen zur Taille
          wrap('chest_plate', 'Brustlage', 'torso', 'anodized',
               arrow(CORE, 282, 248, -17, 17, CHEST_GROW + CHEST_T, tip=1.5)[::-1]
               + [CORE(z, CHEST_GROW + CHEST_T) for z in (316, 350)], -17, 17, 3.0, steps=10),
          wrap('chest_line', 'Akzentlinie', 'torso', 'accent',
               [CORE(z, CHEST_GROW + CHEST_T) for z in (176, 234)], -1.1, 1.1, 1.4, steps=2)]
    P += two_bolts('chest', 'torso', CORE, 334, CHEST_GROW + CHEST_T + 3.0, dx=18)
    # Rückenplatte, Pfeilschnitt nach unten
    P += [wrap('back', 'Rückenplatte', 'torso', 'shell',
               [CORE(150, CHEST_GROW, a0=176, a1=184)] + [CORE(z, CHEST_GROW) for z in (210, 350)], 126, 234, 9)]
    # Schultern: dunkles Gelenk, großer gefaster Schulterpanzer (greift außen über den Oberarm), Medaillon außen
    for side, sx in (('r', 1), ('l', -1)):
        x = sx * SHOULDER_X
        P += [(f'shoulder_joint_{side}', 'Schultergelenk', 'torso', 'cyl', 'dark_metal',
               dict(axis='x', r=54, len=130, c=(sx * 200, -6, SHOULDER_Z))),
              loft(f'pauldron_{side}', 'Schulterpanzer', 'torso', 'shell',
                   [sec(300, 86, 92, -8, x=x + sx * 30, n=2.8), sec(350, 98, 102, -8, x=x + sx * 22, n=2.8),
                    sec(410, 92, 98, -8, x=x + sx * 4, n=2.7), sec(446, 64, 74, -8, x=x - sx * 14, n=2.5),
                    sec(460, 28, 36, -8, x=x - sx * 24, n=2.2)], sharp=50),
              wrap(f'pauldron_band_{side}', 'Schulterband', 'torso', 'graphite',
                   [sec(z, 99, 103, -8, x=x + sx * 21, n=2.8) for z in (354, 364)], -180, 180, 2.5, sub=1)]
        P += medallion(f'shoulder_{side}', 'torso', (sx * (SHOULDER_X + 118), -8, 376), 30, 16)
    return P
