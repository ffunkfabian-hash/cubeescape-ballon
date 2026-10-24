"""Baugruppe Oberkörper: Rumpf (V-Silhouette), trapezförmige Brustplatte mit einem runden Sensor, Bauchbänder, Kragen, Taillengelenk,
Rückenmodul, Schulterpanzer mit Medaillon. Segment torso (Ursprung Socket_Waist, +Z nach oben, +Y vorn).

0.5 nach Nutzerkritik („viel zu kantig“ = klotzig) und Zielbild: schmale Taille (180 mm), Brust 330 statt 376 mm, Brustplatte als
Trapez mit präzisen Fasen statt runder Schale, kleinere Schulterkuppeln, dunkles Taillengelenk sichtbar.
"""
from .shapes import rsection, rsection_top, dome, medallion

SEGMENTS = ['torso']
# Brustplatte: (z, Breite, Vorderkante y1) – Trapez, unten schmal
CHEST = ((146, 196, 104), (296, 336, 122), (352, 292, 108))
BULGE = 6


def chest_front(z):
    """Vorderfläche der Brustplatte in der Mitte (mm, y) bei z – für Sensor und Akzentlinie."""
    for (z0, _, y0), (z1, _, y1) in zip(CHEST, CHEST[1:]):
        if z0 <= z <= z1:
            return y0 + (y1 - y0) * (z - z0) / (z1 - z0) + BULGE
    raise ValueError(z)


def parts():
    # Taillengelenk: Graphitkern mit Wirbelringen (sichtbare Mechanik in der schmalen Taille)
    P = [('waist_joint', 'Taillengelenk', 'torso', 'cyl', 'graphite', dict(axis='z', r=50, len=80, c=(0, -4, 6)))]
    P += [(f'waist_ring_{k}', 'Taillenring', 'torso', 'cyl', 'dark_metal', dict(axis='z', r=66 - 4 * k, len=14, c=(0, -4, z)))
          for k, z in enumerate((-22, 4, 30))]
    P += [
         ('torso_core', 'Rumpf', 'torso', 'hull', 'graphite',
          dict(pts=rsection(180, -70, 64, 40, 20) + rsection(262, -92, 92, 50, 150, bulge=4) + rsection(330, -100, 106, 56, 282, bulge=4)
               + rsection(272, -88, 80, 46, 370))),
         ('chest', 'Brustplatte', 'torso', 'hull', 'shell',
          dict(pts=sum((rsection_top(w, 14, y1, 22, z, n=1, bulge=BULGE) for z, w, y1 in CHEST), []))),
         ('chest_line', 'Mittelfuge', 'torso', 'hull', 'anodized',
          dict(pts=[(x, chest_front(z) + dy, z) for x in (-1.8, 1.8) for z in (172, 246) for dy in (-1.2, 1.0)])),
         ('collar', 'Kragen', 'torso', 'hull', 'graphite', dict(pts=rsection(204, -80, 70, 40, 346) + rsection(150, -60, 54, 34, 398)))]
    P += medallion('chest_core', 'torso', (0, round(chest_front(286) + 1), 286), 28, 10, axis='y')
    # Schrauben an den Ecken der Brustplatte (Vorderfläche außerhalb der Mittelwölbung, + 1 mm)
    for k, (x, z, y) in enumerate(((-118, 330, 115.5), (118, 330, 115.5), (-78, 172, 108.5), (78, 172, 108.5))):
        P.append((f'chest_bolt_{k}', 'Schraube', 'torso', 'cyl', 'trim', dict(axis='y', r=4.2, len=4, c=(x, y, z))))
    # Flankenplatten unter den Armen (hell, mit Fase), liegen 3 mm auf dem Rumpf
    for side, sx in (('r', -1), ('l', 1)):
        P.append((f'flank_{side}', 'Flankenplatte', 'torso', 'hull', 'shell',
                  dict(pts=[(sx * x, y, z) for z, xo, y0, y1 in ((120, 126, -50, 70), (250, 166, -60, 84))
                            for x, ys in ((xo - 22, (y0 - 6, y1 + 6)), (xo + 6, (y0 + 10, y1 - 10))) for y in ys])))
    for k, z in enumerate((40, 82, 124)):
        y1 = 64 + 28 * z / 150 + 10
        P.append((f'abs_{k}', 'Bauchband', 'torso', 'hull', 'graphite',
                  dict(pts=rsection_top(150 + 14 * k, 26, y1, 20, z - 14, n=2) + rsection_top(154 + 14 * k, 26, y1 + 2, 20, z + 14, n=2))))
    P += [('pack', 'Rückenmodul', 'torso', 'hull', 'graphite',
           dict(pts=rsection(210, -156, -80, 34, 140) + rsection(232, -166, -80, 38, 330))),
          ('pack_plate', 'Rückenplatte', 'torso', 'hull', 'shell',
           dict(pts=rsection(172, -176, -160, 8, 180, n=1) + rsection(194, -180, -164, 8, 318, n=1)))]
    for side, sx in (('r', -1), ('l', 1)):
        P += [(f'pauldron_{side}', 'Schulterpanzer', 'torso', 'hull', 'shell',
               dict(pts=dome(sx, (4, 350), [(150, 188, 152, 58), (228, 212, 176, 74), (294, 170, 134, 56), (320, 102, 76, 34)]))),
              (f'pauldron_rim_{side}', 'Schulterrand', 'torso', 'hull', 'graphite',
               dict(pts=dome(sx, (4, 343), [(140, 204, 168, 62), (164, 206, 170, 62)])))]
        P += medallion(f'shoulder_{side}', 'torso', (sx * 322, 4, 350), 34, 10)
    return P
