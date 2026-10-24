"""Baugruppe Kopf: Hals mit zwei kleinen Hydrauliken, Kopfkern, kantiger Helm, schwarze Gesichtsplatte mit schmalem cyanblauem
Visier, Mittelkamm, Ohrmedaillons. Segment head (Ursprung Socket_Neck).

0.5 nach Zielbild: Kopf etwa 10 % größer, Helm mit präzisen Fasen statt runder Haube, Gesicht als eigene schwarze Platte.
"""
from .shapes import rsection, rsection_top, medallion, piston, cable

SEGMENTS = ['head']
LIFT = 70           # Kopf über dem Hals angehoben: längerer, offener Hals wie im Zielbild
SCALE = 0.90        # Kopf kleiner wie im Zielbild (Helm ~12 % der Körperhöhe statt 18 %)
FACE = ((112, 172, 124), (214, 182, 128))     # Gesichtsplatte: (z, Breite, Vorderkante y1)


def parts():
    P = [
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
    P = [_xform(p, SCALE, LIFT) for p in P]
    # Hals: Graphitkern mit vier Wirbelringen, zwei Hydrauliken und zwei Nackenkabel (sichtbare Mechanik)
    N = [('neck', 'Hals', 'head', 'cyl', 'graphite', dict(axis='z', r=30, len=180, c=(0, -4, 70)))]
    N += [(f'neck_ring_{k}', 'Halsring', 'head', 'cyl', 'graphite' if k % 2 else 'dark_metal',
           dict(axis='z', r=42 - 2 * k, len=18, c=(0, -4, z))) for k, z in enumerate((2, 30, 58, 86, 114))]
    for side, sx in (('r', -1), ('l', 1)):
        N += piston(f'neck_piston_{side}', 'Halshydraulik', 'head', (sx * 30, -40, -10), (sx * 36, -52, 150), r=7)
        N += cable(f'neck_cable_{side}', 'Nackenkabel', 'head', [(sx * 20, -50, -6), (sx * 30, -60, 60), (sx * 22, -62, 130),
                                                                  (sx * 12, -56, 176)], r=5)
    return N + P


def _xform(p, k, dz):
    """Teil um den Segmentursprung mit k skalieren und um dz anheben."""
    pid, de, seg, kind, role, q = p
    q = dict(q)
    if 'pts' in q:
        q['pts'] = [(x * k, y * k, z * k + dz) for x, y, z in q['pts']]
    if 'c' in q:
        q['c'] = (q['c'][0] * k, q['c'][1] * k, q['c'][2] * k + dz)
    if kind == 'cyl':
        q['r'], q['len'] = q['r'] * k, q['len'] * k
    return (pid, de, seg, kind, role, q)
