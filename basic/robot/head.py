"""Baugruppe Kopf: Hals mit zwei kleinen Hydrauliken, Kopfkern, kantiger Helm, schwarze Gesichtsplatte mit schmalem cyanblauem
Visier, Mittelkamm, Ohrmedaillons. Segment head (Ursprung Socket_Neck).

0.5 nach Zielbild: Kopf etwa 10 % größer, Helm mit präzisen Fasen statt runder Haube, Gesicht als eigene schwarze Platte.
"""
from .shapes import rsection, rsection_top, medallion, piston

SEGMENTS = ['head']
FACE = ((112, 172, 124), (214, 182, 128))     # Gesichtsplatte: (z, Breite, Vorderkante y1)


def parts():
    # Hals: Graphitkern mit drei Wirbelringen (sichtbare Mechanik statt eines Zylinders)
    P = [('neck', 'Hals', 'head', 'cyl', 'graphite', dict(axis='z', r=32, len=104, c=(0, -4, 34)))]
    P += [(f'neck_ring_{k}', 'Halsring', 'head', 'cyl', 'dark_metal', dict(axis='z', r=44 - 3 * k, len=16, c=(0, -4, z)))
          for k, z in enumerate((2, 30, 58))]
    P += [
         ('head_core', 'Kopfkern', 'head', 'hull', 'graphite',
          dict(pts=rsection(160, -104, 90, 40, 62, n=2) + rsection(190, -118, 88, 48, 166, n=2) + rsection(164, -106, 78, 44, 272, n=2))),
         # Helm in zwei Segmenten (Fuge 6 mm bei z 226–232, der dunkle Kern zeigt sich darin): Band und Kappe
         ('helmet', 'Helmband', 'head', 'hull', 'shell',
          dict(pts=rsection(206, -128, 62, 40, 138, n=1) + rsection(206, -128, 90, 46, 226, n=1, bulge=4))),
         ('helmet_cap', 'Helmkappe', 'head', 'hull', 'shell',
          dict(pts=rsection(204, -127, 92, 45, 232, n=1, bulge=4) + rsection(172, -112, 92, 42, 292, n=1)
               + rsection(112, -80, 54, 30, 324, n=1))),
         ('faceplate', 'Gesichtsplatte', 'head', 'hull', 'graphite',
          dict(pts=sum((rsection_top(w, 60, y1, 24, z, n=1) for z, w, y1 in FACE), []))),
         ('eye_line', 'Visier', 'head', 'hull', 'energy',
          dict(pts=[(x, y, z) for x in (-58, 58) for y in (124.5, 131) for z in (178, 185)])),
         ('crest', 'Mittelkamm', 'head', 'hull', 'dark_metal',
          dict(pts=[(x, y, z) for x in (-5, 5) for y, z in ((94, 236), (90, 292), (50, 322), (-70, 322), (100, 236), (97, 296), (56, 330), (-70, 330))]))]
    P += medallion('ear', 'head', (0, -10, 186), 32, 214)
    for side, sx in (('r', -1), ('l', 1)):
        P += piston(f'neck_piston_{side}', 'Halshydraulik', 'head', (sx * 34, -40, -10), (sx * 46, -58, 92), r=7)
    return P
