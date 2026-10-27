"""Baugruppe Beine: Oberschenkel, Knie mit Medaillon und Kniekappe, Schienbein mit dunkler Lage und zwei Bolzen, Stiefel – je Seite.
Segmente thigh/shin/foot (Ursprung Socket_Hip, Knie, Knöchel); Teile im Rahmen der rechten Seite (+X außen, +Y vorn), die linke
ist an X gespiegelt. Fuß: +Z nach vorn, +Y nach oben, Boden bei y = −FOOT_H.

0.23 „Gauntlet“: Formsprache von Arm v3 (siehe upper_body.py). Das Bein wiederholt den Unterarm: Graphitkörper, ruhige Schale mit
Pfeilschnitt zum nächsten Gelenk, zweite dunkle Lage mit zwei Bolzen am Schienbein (wie am Handgelenk), Medaillon am Knie (wie am
Ellbogen). Runde 2 („lang und schlaksig“, Q-D2-PARADE): Oberschenkel und Schienbein gleich lang (≈ 400 mm statt 339/574), kräftiger,
Glieder gewölbt statt kastig (kleine Fasen), Stiefel mit Schaft, Zehen- und Fersenkappe.
"""
from .shapes import loft, wrap, tab, arrow, two_bolts, medallion, sec

SEGMENTS = ['thigh', 'shin', 'foot']
# Gelenkpunkte (mm, Welt) je Seite: Hüfte, Knie, Knöchel, Zehenpunkt; Stand breit und entspannt, Füße leicht auswärts, Standbein
# links (aus 0.5). Zehenpunkt auf Knöchelhöhe, damit der Fußrahmen waagerecht liegt (Sohle eben auf dem Boden).
FOOT_H = 112
# Runde 3 („steif“): Standbein links fast gestreckt, rechtes Spielbein mit lockerem Knie nach vorn außen, Fuß weiter vorn
JOINTS = {'R': ((-116, 0, 910), (-150, -62, 514), (-176, -28, FOOT_H), (-226, -192, FOOT_H)),
          'L': ((116, 0, 910), (136, -6, 508), (172, 22, FOOT_H), (214, -150, FOOT_H))}

THIGH = tab([(-10, 66, 74, 0), (130, 86, 94, 0), (300, 72, 80, 0), (400, 58, 64, 0)], ch=12)   # oben schmal unter dem Becken (Runde 4)
SHIN = tab([(30, 66, 70, 0), (140, 74, 82, -6), (300, 60, 66, -2), (396, 56, 58, 0)], ch=16)
FOOT = tab([(-100, 58, 40, -68), (-30, 64, 52, -58), (70, 66, 44, -66), (160, 60, 30, -80), (218, 50, 20, -90)], ch=14)


def parts():
    P = [loft('thigh_core', 'Oberschenkel', 'thigh', 'graphite', [THIGH(z) for z in (-10, 110, 300, 400)]),
         wrap('thigh_shell', 'Oberschenkelschale', 'thigh', 'shell',
              [THIGH(50, 2.0, a0=-60, a1=60), THIGH(110, 2.0), THIGH(250, 2.0)]
              + arrow(THIGH, 320, 370, -72, 72, 2.0, tip=5), -72, 72, 8)]
    # Knie: Gelenk und Medaillon quer durch (wie der Ellbogen), Kniekappe mit Pfeil nach oben
    P += [('knee', 'Kniegelenk', 'shin', 'cyl', 'dark_metal', dict(axis='x', r=54, len=132, c=(0, 0, 0)))]
    P += medallion('knee_med', 'shin', (0, 0, 0), 44, 146)
    P += [wrap('knee_cap', 'Kniekappe', 'shin', 'shell',
               [sec(-52, 52, 60, n=2.4, a0=-6, a1=6), sec(-18, 58, 66, n=2.4), sec(34, 60, 68, n=2.4), sec(74, 56, 64, n=2.4)], -60, 60, 9)]
    # Schienbein: Körper, Schale mit Pfeil zum Stiefel, dunkle Lage mit zwei Bolzen, Wadenplatte hinten
    P += [loft('shin_core', 'Schienbein', 'shin', 'graphite', [SHIN(z) for z in (30, 140, 300, 396)]),
          wrap('shin_shell', 'Schienbeinschale', 'shin', 'shell',
               [SHIN(84, 2.0, a0=-48, a1=48), SHIN(130, 2.0), SHIN(230, 2.0)]
               + arrow(SHIN, 268, 318, -70, 70, 2.0, tip=5), -70, 70, 8),
          wrap('shin_plate', 'Schienbeinlage', 'shin', 'anodized',
               arrow(SHIN, 196, 166, -18, 18, 10.0, tip=1.5)[::-1] + [SHIN(z, 10.0) for z in (226, 256)], -18, 18, 2.5, steps=8),
          wrap('calf', 'Wadenplatte', 'shin', 'shell', [SHIN(z, 2.0) for z in (90, 170, 250)], 138, 222, 7),
          # Stiefelschaft: Cremeschale rund um den unteren Schienbeinteil (vorn offen unter dem Pfeil)
          wrap('boot_cuff', 'Stiefelschaft', 'shin', 'shell', [SHIN(z, 3.0) for z in (326, 360, 392)], 40, 320, 8)]
    P += two_bolts('shin', 'shin', SHIN, 240, 13.5, dx=11, r=3.6)
    # Stiefel: Knöchel mit Medaillon, Graphitkörper, Zehenkappe mit Pfeil zum Knöchel, Fersenkappe, Gummisohle
    P += [('ankle', 'Knöchel', 'foot', 'cyl', 'dark_metal', dict(axis='x', r=38, len=120, c=(0, 0, 0)))]
    P += medallion('ankle_med', 'foot', (0, 0, 0), 30, 130)
    P += [loft('foot_core', 'Fuß', 'foot', 'graphite', [FOOT(z) for z in (-100, -30, 70, 160, 218)]),
          wrap('toe_cap', 'Zehenkappe', 'foot', 'shell',
               arrow(FOOT, 76, 36, -80, 80, 2.0, tip=5)[::-1] + [FOOT(z, 2.0) for z in (160, 220)], -80, 80, 7),
          wrap('heel_cap', 'Fersenkappe', 'foot', 'shell', [FOOT(z, 2.0) for z in (-104, -70, -40)], 70, 290, 7),
          loft('sole', 'Sohle', 'foot', 'rubber', [sec(-106, 60, 5, -FOOT_H + 5, n=4), sec(226, 52, 5, -FOOT_H + 5, n=4)], sub=1)]
    return P
