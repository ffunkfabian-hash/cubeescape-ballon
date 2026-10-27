"""Baugruppe Kopf: kurzer Hals mit Wirbelring, runder Helm, dunkle Gesichtsplatte, cyanblaue Augenlinie, Helmfuge, Medaillon an den
Schläfen. Segment head (Ursprung Socket_Neck, +Z nach oben, +Y vorn, +X rechte Körperseite).

0.23 „Gauntlet“: Formsprache von Arm v3 (siehe upper_body.py). Die Augenlinie ist der eine Blickfang der Figur (Stilhandbuch § 2,
„Ein Blickfang“); sonst leuchtet nichts. Runde 2 (Q-D2-PARADE, Q-ARMOR-ORANGE): Helm rund statt kastig und tief im Kragen, kein
sichtbarer langer Hals.
"""
from .shapes import loft, wrap, ring, tab, medallion, sec

SEGMENTS = ['head']

HELMET = tab([(36, 84, 94, 6), (80, 98, 108, 8), (170, 100, 110, 6), (220, 86, 96, 2), (250, 56, 66, -2), (262, 18, 22, -2)])
N = 3.0
FACE_GROW, FACE_T = 1.5, 4.0


def parts():
    P = [loft('neck', 'Hals', 'head', 'graphite', [sec(-30, 46, 46, n=2.2), sec(60, 42, 42, n=2.2)]),
         ring('neck_ring', 'Wirbelring', 'head', 'dark_metal', 8, 20, 48, 48, 6),
         loft('helmet', 'Helm', 'head', 'shell', [HELMET(z, n=N) for z in (36, 80, 170, 220, 250, 262)], sharp=50),
         ring('helmet_seam', 'Helmfuge', 'head', 'graphite', 198, 203, HELMET(200)['a'] - 0.6, HELMET(200)['b'] - 0.6, 1.6, n=N),
         # Gesicht: dunkle Platte vorn, unten schmaler (Kinn)
         wrap('face', 'Gesichtsplatte', 'head', 'anodized',
              [HELMET(62, FACE_GROW, n=N, a0=-42, a1=42), HELMET(90, FACE_GROW, n=N),
               HELMET(166, FACE_GROW, n=N), HELMET(188, FACE_GROW, n=N, a0=-50, a1=50)], -60, 60, FACE_T),
         wrap('visor', 'Augenlinie', 'head', 'energy',
              [HELMET(z, FACE_GROW + FACE_T, n=N) for z in (128, 134)], -40, 40, 1.0, sub=1, steps=16)]
    P += medallion('temple', 'head', (0, -8, 118), 28, 2 * HELMET(118)['a'] + 12)
    return P
