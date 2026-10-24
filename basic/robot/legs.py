"""Baugruppe Beine: Oberschenkel, Knie mit Medaillon, Schienbein mit Wadenhydraulik, Fuß – je Seite. Segmente thigh/shin/foot
(Ursprung Socket_Hip, Knie, Knöchel); Teile im Rahmen der rechten Seite (+X zur Körpermitte), die linke ist an X gespiegelt.

0.5 nach Nutzerkritik („klotzig“) und Zielbild: Hüfte 1000 statt 960 mm (lange Beine), Knie hoch (lange Schienbeine), Oberschenkel
verjüngt sich von 156 auf 100 mm,
Schalen mit Fasen und leicht gewölbter Front, Wade mit Wölbung nach hinten, schmalere Füße.
"""
from .shapes import rsection, rsection_top, medallion, bolts, piston

SEGMENTS = ['thigh', 'shin', 'foot']
# Gelenkpunkte (mm, Welt) je Seite: Hüfte, Knie, Knöchel, Zehenspitze 
# Stand nach Zielbild: breiter und entspannt, Füße leicht auswärts, Standbein links
JOINTS = {'R': ((-110, 0, 1000), (-140, -34, 664), (-176, 6, 92), (-214, -176, 30)),
          'L': ((110, 0, 1000), (146, -6, 660), (188, 30, 92), (250, -146, 30))}
# Knie wie im Zielbild bei ~36 % der Höhe (vorher 30 %): Teile entlang der Glieder gestreckt bzw. gestaucht (Entwurf für 455 mm)
LEN_K = {'thigh': 0.74, 'shin': 1.26}


def parts():
    P = [('thigh_body', 'Oberschenkel', 'thigh', 'hull', 'graphite',
          dict(pts=rsection(150, -76, 72, 44, 10, bulge=4) + rsection(156, -80, 80, 48, 150, bulge=6) + rsection(120, -62, 62, 38, 320)
               + rsection(100, -54, 54, 34, 440))),
         # Oberschenkelschale wie im Zielbild als eine lange Platte von der Schritthöhe bis über das Knie; darüber und außen bleibt die
         # dunkle Mechanik sichtbar
         ('thigh_shell', 'Oberschenkelschale', 'thigh', 'hull', 'shell',
          dict(pts=rsection_top(150, -4, 92, 34, 150, n=1, bulge=6) + rsection_top(146, -4, 91, 34, 200, n=1, bulge=6)
               + rsection_top(130, -3, 82, 30, 300, n=1, bulge=4) + rsection_top(112, -2, 70, 28, 404, n=1)))]
    P += bolts('thigh', 89, 230, dx=34, r=4.0)
    P += piston('thigh_piston', 'Oberschenkelhydraulik', 'thigh', (-70, -66, 70), (-58, -52, 400), r=8)
    P += piston('thigh_piston_in', 'Oberschenkelhydraulik innen', 'thigh', (70, -40, 80), (56, -30, 390), r=7)
    P += [('knee', 'Kniegelenk', 'shin', 'cyl', 'dark_metal', dict(axis='x', r=48, len=120, c=(0, 0, 0))),
          ('knee_cap', 'Kniekappe', 'shin', 'hull', 'shell',
           dict(pts=rsection_top(104, 22, 82, 30, -48, n=1) + rsection_top(116, 22, 94, 34, 28, n=1)
                + rsection_top(84, 14, 72, 26, 78, z_top=100, n=1)))]
    P += medallion('knee_med', 'shin', (0, 0, 0), 40, 126)
    P += [('shin_body', 'Schienbein', 'shin', 'hull', 'graphite',
           dict(pts=rsection(104, -60, 52, 34, 40) + rsection(124, -78, 62, 40, 160, bulge=6) + rsection(96, -64, 50, 30, 280)
                + rsection(78, -44, 40, 26, 410))),
          # Schienbeinplatte endet wie im Zielbild deutlich über dem Fuß: darunter ein langer dunkler Knöchelbereich
          ('shin_shell', 'Schienbeinschale', 'shin', 'hull', 'shell',
           dict(pts=rsection_top(118, -6, 78, 30, 110, n=1) + rsection_top(130, -8, 86, 34, 180, n=1, bulge=5)
                + rsection_top(96, -5, 62, 24, 362, n=1))),
          ('shin_plate', 'Schienbeinplatte', 'shin', 'hull', 'anodized',
           dict(pts=[(x, y, z) for z, w, yt in ((246, 50, 80), (344, 40, 66)) for x in (-w / 2, w / 2) for y in (yt - 3, yt + 6)]
                + [(0, y, 216) for y in (84, 93)]))]
    P += bolts('shin', 77, 322, dx=12)
    P += piston('calf_piston', 'Wadenhydraulik', 'shin', (-64, -30, 60), (-50, -24, 330), r=9)
    P += piston('heel_piston', 'Fersenhydraulik', 'shin', (0, -68, 262), (0, -50, 420), r=9)
    # Fuß (Rahmen: +Z nach vorn, +Y nach oben, Ursprung Knöchel)
    P += medallion('ankle_med', 'foot', (0, 0, 0), 34, 104)
    P += [('ankle', 'Knöchel', 'foot', 'cyl', 'dark_metal', dict(axis='x', r=32, len=96, c=(0, 0, 0))),
          ('foot_body', 'Fuß', 'foot', 'hull', 'graphite',
           dict(pts=rsection(100, -88, 24, 26, -66) + rsection(110, -88, 22, 30, 116) + rsection(94, -88, -8, 26, 194))),
          ('toe_cap', 'Zehenkappe', 'foot', 'hull', 'shell',
           dict(pts=rsection_top(112, -60, 28, 22, 80, n=2) + rsection_top(98, -84, -14, 20, 204, n=2))),
          ('ankle_guard', 'Knöchelschutz', 'foot', 'hull', 'shell',
           dict(pts=rsection(98, -12, 44, 14, -4, n=1) + rsection(90, -22, 32, 12, 74, n=1))),
          ('heel', 'Fersenplatte', 'foot', 'hull', 'shell',
           dict(pts=rsection(104, -84, 10, 22, -80, n=2) + rsection(106, -84, 16, 22, -40, n=2))),
          ('sole', 'Sohle', 'foot', 'hull', 'rubber', dict(pts=rsection(110, -96, -84, 5, -78) + rsection(104, -96, -84, 5, 198)))]
    return [_stretch(p) for p in P]


def _stretch(p):
    """Längen (z) der Teile auf Oberschenkel und Schienbein mit LEN_K anpassen; Gelenke am Ursprung (Knie) bleiben rund."""
    pid, de, seg, kind, role, q = p
    k = LEN_K.get(seg, 1.0)
    if k == 1.0:
        return p
    q = dict(q)
    if 'pts' in q:
        q['pts'] = [(x, y, z * k if z > 0 else z) for x, y, z in q['pts']]
    if 'c' in q and q['c'][2] > 0:
        q['c'] = (q['c'][0], q['c'][1], q['c'][2] * k)
    return (pid, de, seg, kind, role, q)
