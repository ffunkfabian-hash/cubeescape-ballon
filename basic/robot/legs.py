"""Baugruppe Beine: Oberschenkel, Knie mit Medaillon, Schienbein mit Wadenhydraulik, Fuß – je Seite. Segmente thigh/shin/foot
(Ursprung Socket_Hip, Knie, Knöchel); Teile im Rahmen der rechten Seite (+X zur Körpermitte), die linke ist an X gespiegelt.

0.5 nach Nutzerkritik („klotzig“) und Zielbild: Hüfte 1000 statt 960 mm (lange Beine), Oberschenkel verjüngt sich von 156 auf 100 mm,
Schalen mit Fasen und leicht gewölbter Front, Wade mit Wölbung nach hinten, schmalere Füße.
"""
from .shapes import rsection, rsection_top, medallion, bolts, piston

SEGMENTS = ['thigh', 'shin', 'foot']
# Gelenkpunkte (mm, Welt) je Seite: Hüfte, Knie, Knöchel, Zehenspitze (Ruhehaltung, leichtes Standbein links)
JOINTS = {'R': ((-110, 0, 1000), (-122, -30, 545), (-130, 10, 92), (-146, -190, 30)),
          'L': ((110, 0, 1000), (130, -10, 540), (148, 26, 92), (186, -160, 30))}


def parts():
    P = [('thigh_body', 'Oberschenkel', 'thigh', 'hull', 'graphite',
          dict(pts=rsection(150, -76, 72, 44, 10, bulge=4) + rsection(156, -80, 80, 48, 150, bulge=6) + rsection(120, -62, 62, 38, 320)
               + rsection(100, -54, 54, 34, 440))),
         # Oberschenkelschale in zwei Segmenten (Fuge 6 mm bei z 262–268)
         ('thigh_shell', 'Oberschenkelschale', 'thigh', 'hull', 'shell',
          dict(pts=rsection_top(158, -4, 92, 34, 50, n=1, bulge=6) + rsection_top(150, -4, 92, 34, 190, n=1, bulge=6)
               + rsection_top(137, -3, 84, 32, 262, n=1, bulge=4))),
         ('thigh_shell_low', 'Oberschenkelschale unten', 'thigh', 'hull', 'shell',
          dict(pts=rsection_top(134, -3, 83, 31, 268, n=1, bulge=4) + rsection_top(112, -2, 70, 28, 384, n=1))),
         ('thigh_side', 'Oberschenkelseitenplatte', 'thigh', 'hull', 'shell',
          dict(pts=[(x, y, z) for z, y0, y1 in ((90, -54, 30), (300, -40, 22)) for y in (y0, y1) for x in (-80, -88)]
               + [(-92, -12, 196)]))]
    P += bolts('thigh', 89, 230, dx=34, r=4.0)
    P += piston('thigh_piston', 'Oberschenkelhydraulik', 'thigh', (-70, -66, 70), (-58, -52, 400), r=8)
    P += [('knee', 'Kniegelenk', 'shin', 'cyl', 'dark_metal', dict(axis='x', r=48, len=120, c=(0, 0, 0))),
          ('knee_cap', 'Kniekappe', 'shin', 'hull', 'shell',
           dict(pts=rsection_top(104, 22, 82, 30, -48, n=1) + rsection_top(116, 22, 94, 34, 28, n=1)
                + rsection_top(84, 14, 72, 26, 78, z_top=100, n=1)))]
    P += medallion('knee_med', 'shin', (0, 0, 0), 40, 126)
    P += [('shin_body', 'Schienbein', 'shin', 'hull', 'graphite',
           dict(pts=rsection(104, -60, 52, 34, 40) + rsection(124, -78, 62, 40, 160, bulge=6) + rsection(96, -64, 50, 30, 280)
                + rsection(78, -44, 40, 26, 410))),
          ('shin_shell', 'Schienbeinschale', 'shin', 'hull', 'shell',
           dict(pts=rsection_top(118, -6, 78, 30, 110, n=1) + rsection_top(130, -8, 86, 34, 180, n=1, bulge=5)
                + rsection_top(90, -4, 58, 24, 400, n=1))),
          ('shin_plate', 'Schienbeinplatte', 'shin', 'hull', 'anodized',
           dict(pts=[(x, y, z) for z, w, yt in ((262, 50, 79), (380, 40, 62)) for x in (-w / 2, w / 2) for y in (yt - 3, yt + 6)]
                + [(0, y, 232) for y in (83, 92)]))]
    P += bolts('shin', 74, 352, dx=12)
    P += piston('calf_piston', 'Wadenhydraulik', 'shin', (-64, -30, 60), (-50, -24, 330), r=9)
    # Fuß (Rahmen: +Z nach vorn, +Y nach oben, Ursprung Knöchel)
    P += medallion('ankle_med', 'foot', (0, 0, 0), 28, 100)
    P += [('ankle', 'Knöchel', 'foot', 'cyl', 'dark_metal', dict(axis='x', r=32, len=96, c=(0, 0, 0))),
          ('foot_body', 'Fuß', 'foot', 'hull', 'graphite',
           dict(pts=rsection(100, -88, 24, 26, -66) + rsection(110, -88, 22, 30, 116) + rsection(94, -88, -8, 26, 194))),
          ('toe_cap', 'Zehenkappe', 'foot', 'hull', 'shell',
           dict(pts=rsection_top(112, -60, 28, 22, 80, n=2) + rsection_top(98, -84, -14, 20, 204, n=2))),
          ('heel', 'Fersenplatte', 'foot', 'hull', 'shell',
           dict(pts=rsection(104, -84, 10, 22, -80, n=2) + rsection(106, -84, 16, 22, -40, n=2))),
          ('sole', 'Sohle', 'foot', 'hull', 'rubber', dict(pts=rsection(110, -96, -84, 5, -78) + rsection(104, -96, -84, 5, 198)))]
    return P
