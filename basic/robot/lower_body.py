"""Baugruppe Unterkörper: Becken, Hüftgelenke, Gürtel mit Schnalle, Lendenplatte. Segment pelvis (Ursprung 150 mm unter Socket_Waist).

0.5: schmaler (Becken 210 statt 240 mm), Lendenplatte kürzer, sichtbare dunkle Hüftgelenke statt eines Blocks (Nutzer: „klotzig“).
"""
from .shapes import rsection, rsection_top, medallion

SEGMENTS = ['pelvis']
HIP_Z = 40          # Hüftgelenk über dem Segmentursprung (= Socket_Hip)


def parts():
    P = [('pelvis_core', 'Becken', 'pelvis', 'hull', 'graphite',
          dict(pts=rsection(210, -78, 74, 40, -10) + rsection(200, -74, 70, 38, 100) + rsection(186, -70, 64, 34, 156))),
         ('belt', 'Gürtel', 'pelvis', 'hull', 'graphite',
          dict(pts=rsection(226, -86, 84, 44, 98, bulge=3) + rsection(222, -84, 82, 42, 132, bulge=3))),
         ('buckle', 'Gürtelschnalle', 'pelvis', 'hull', 'shell',
          dict(pts=rsection_top(60, 80, 96, 6, 100, n=1) + rsection_top(56, 80, 96, 6, 130, n=1))),
         ('tasset', 'Lendenplatte', 'pelvis', 'hull', 'shell',
          dict(pts=rsection_top(96, 66, 88, 10, 94, n=1) + rsection_top(76, 62, 84, 10, -60, n=1))),
         ('tasset_edge', 'Lendenplattenkante', 'pelvis', 'hull', 'dark_metal',
          dict(pts=rsection_top(78, 61, 86, 8, -50, n=1) + rsection_top(74, 60, 86, 8, -64, n=1)))]
    for side, sx in (('r', -1), ('l', 1)):
        # Hüftachse durch den Oberschenkel bis außen, dort Medaillon wie am Knie (Zielbild: sichtbare Gelenke)
        P.append((f'hip_joint_{side}', 'Hüftgelenk', 'pelvis', 'cyl', 'dark_metal', dict(axis='x', r=40, len=150, c=(sx * 112, 0, HIP_Z))))
        P += medallion(f'hip_med_{side}', 'pelvis', (sx * 190, 0, HIP_Z), 34, 10)
    return P
