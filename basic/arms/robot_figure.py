"""BASIC-Roboter v2 (Spaßfigur, Nutzerwunsch 24.10.2026: „passenden Roboter just 4 fun“) – passend zu Arm v3, keine Spielfigur.

v2 nach Nutzerkritik „viel zu kantig“ und Titan-Vorlage (Q-D2-ARM, nur Prinzipien): gerundete Querschnitte und geglättete Flächen,
V-Silhouette (breite Brust, schmale Taille), kuppelförmige Schulterpanzer, runder Helm mit Mittelkamm, Lendenplatte, helle Platten
über dunklem Unteranzug.

Gleiche Formsprache wie robot_arm.py: Graphitkörper, glatte Cremeschalen mit Pfeilschnitt und Wölbung, dunkle Pfeilplatten mit zwei
Bolzen, Medaillons (Scheibe + blanker Ring) an Schultern, Ellbogen und Knien, je Bauteil höchstens eine Akzentlinie. Die Arme sind
robot_arm.parts() (v3) unverändert.

Welt (mm): Figur steht auf z = 0, schaut nach −Y, rechte Körperseite bei −X. Segmente: (name, A, B, hint, Seite) – Rahmen +Z von A
nach B, +Y = hint (Vorderseite/Panzerseite), +X entsprechend; Seite 'R'/'L' spiegelt die Teile an X. Teile wie robot_arm:
(id, de, segment-typ, form, rolle, params).
"""

HEIGHT_MM = 1860
SHOULDER_W = 215                       # Schultergelenk ±X
SHOULDER_Z = 1420
HIP = (110, 0, 960)                    # Hüftgelenk (rechts: x negativ)


def _bolts(seg, y, z, dx=14, r=4.4):
    return [(f'{seg}_bolt_{k}', 'Bolzen', seg, 'cyl', 'trim', dict(axis='y', r=r, len=4, c=(s * dx, y, z)))
            for k, s in (('a', -1), ('b', 1))]


def _medallion(name, seg, c, r, length, axis='x'):
    """Scheibe, blanker Ring, Nabe – das Medaillon-Motiv vom Ellbogen."""
    return [(f'{name}_disc', 'Medaillon', seg, 'cyl', 'graphite', dict(axis=axis, r=r, len=length, c=c)),
            (f'{name}_ring', 'Medaillonring', seg, 'cyl', 'trim', dict(axis=axis, r=r * 0.76, len=length + 4, c=c)),
            (f'{name}_hub', 'Medaillonnabe', seg, 'cyl', 'graphite', dict(axis=axis, r=r * 0.52, len=length + 8, c=c))]


def segments():
    """Ruhehaltung (Stand, leichtes Standbein links). Arme setzt tools/robot_build.py per IK an die Waffe."""
    hx, hy, hz = HIP
    S = []
    S += [('pelvis', (0, 0, 930), (0, 0, 1080), (0, -1, 0), 'C'),
          ('torso', (0, 0, 1080), (0, 0, 1470), (0, -1, 0), 'C'),
          ('head', (0, 0, 1470), (0, 0, 1760), (0, -1, 0), 'C')]
    legs = {'R': ((-hx, hy, hz), (-128, -40, 525), (-136, 10, 92), (-150, -190, 30)),
            'L': ((hx, hy, hz), (140, -10, 520), (158, 30, 92), (196, -160, 30))}
    for side, (hip, knee, ankle, toe) in legs.items():
        S += [(f'thigh_{side}', hip, knee, (0, -1, 0), side),
              (f'shin_{side}', knee, ankle, (0, -1, 0), side),
              (f'foot_{side}', ankle, toe, (0, 0, 1), side)]
    return S


def rsection(w, y0, y1, r, z, n=4):
    """Gerundeter Rechteckquerschnitt bei z (Eckradius r, n Zwischenpunkte je Ecke)."""
    import math
    r = min(r, w / 2 - 0.1, (y1 - y0) / 2 - 0.1)
    pts = []
    for cx, cy, a0 in ((w / 2 - r, y1 - r, 0), (-(w / 2 - r), y1 - r, 90), (-(w / 2 - r), y0 + r, 180), (w / 2 - r, y0 + r, 270)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
    return pts


def rsection_top(w, y0, y1, r, z, z_top=None, n=4):
    """Obere Hälfte (Schale) mit gerundeten Außenkanten; Punkte über y0 + r bekommen z_top (Pfeilschnitt)."""
    zt = z if z_top is None else z_top
    pts = [p for p in rsection(w, y0 - (y1 - y0), y1, r, z, n) if p[1] >= y0 - 1e-6]
    pts += [(w / 2, y0, z), (-w / 2, y0, z)]
    return [(x, y, zt if y > y0 + r else z) for x, y, z in pts]


def dome(sx, c, rings, n=4):
    """Kuppel entlang X (Schulter): rings = [(x, breite_y, höhe_z, radius)], c = (y, z) Mitte."""
    pts = []
    for x, wy, hz, r in rings:
        for yy, zz, _ in rsection(wy, -hz / 2, hz / 2, r, 0, n):
            pts.append((sx * x, c[0] + yy, c[1] + zz))
    return pts


def parts():
    P = []
    # Becken: Körper, Gürtel mit Schnalle, lange Lendenplatte (dunkel) mit heller Kante
    P += [('pelvis_core', 'Becken', 'pelvis', 'hull', 'graphite',
           dict(pts=rsection(240, -84, 80, 50, 0) + rsection(226, -80, 72, 46, 150))),
          ('belt', 'Gürtel', 'pelvis', 'hull', 'dark_metal', dict(pts=rsection(256, -92, 90, 54, 96) + rsection(256, -92, 90, 54, 134))),
          ('buckle', 'Gürtelschnalle', 'pelvis', 'hull', 'shell', dict(pts=rsection_top(64, 84, 100, 8, 100) + rsection_top(64, 84, 100, 8, 130))),
          ('tasset', 'Lendenplatte', 'pelvis', 'hull', 'graphite',
           dict(pts=rsection_top(150, 72, 94, 10, 92) + rsection_top(118, 64, 86, 10, -200))),
          ('tasset_edge', 'Lendenplattenkante', 'pelvis', 'hull', 'shell',
           dict(pts=rsection_top(122, 63, 88, 10, -186) + rsection_top(118, 62, 88, 10, -204)))]
    # Rumpf (V-Silhouette): Graphitkörper, Brustschale mit Pfeilschnitt, Brustmedaillon, Bauchbänder, Kragen, Rückenmodul
    P += [('torso_core', 'Rumpf', 'torso', 'hull', 'graphite',
           dict(pts=rsection(220, -78, 68, 44, 0) + rsection(300, -100, 100, 56, 170) + rsection(376, -106, 112, 60, 320)
                + rsection(300, -92, 82, 50, 394))),
          ('chest', 'Brustschale', 'torso', 'hull', 'shell',
           dict(pts=rsection_top(240, 20, 108, 50, 196, z_top=160) + rsection_top(362, 10, 128, 60, 306)
                + rsection_top(304, 10, 96, 50, 386))),
          ('chest_line', 'Akzentlinie', 'torso', 'hull', 'accent',
           dict(pts=[(x, y, z) for x in (-1.8, 1.8) for y, z in ((108, 168), (125, 250), (110, 170), (127, 250))])),
          ('collar', 'Kragen', 'torso', 'hull', 'dark_metal', dict(pts=rsection(222, -82, 74, 44, 380) + rsection(176, -64, 60, 40, 420)))]
    P += _medallion('chest_core', 'torso', (0, 128, 300), 30, 10, axis='y')
    for k, z in enumerate((30, 70, 110)):
        P.append((f'abs_{k}', 'Bauchband', 'torso', 'hull', 'dark_metal',
                  dict(pts=rsection_top(170 + 10 * k, 30, 80 + 5 * k, 24, z - 15) + rsection_top(174 + 10 * k, 30, 82 + 5 * k, 24, z + 15))))
    P += [('pack', 'Rückenmodul', 'torso', 'hull', 'graphite',
           dict(pts=rsection(250, -168, -80, 40, 120) + rsection(272, -180, -80, 44, 360))),
          ('pack_plate', 'Rückenplatte', 'torso', 'hull', 'shell',
           dict(pts=rsection(200, -190, -172, 8, 170) + rsection(220, -194, -176, 8, 340)))]
    # Schulterpanzer: Kuppel mit dunklem Rand und Medaillon an der Spitze
    for side, sx in (('r', -1), ('l', 1)):
        P += [(f'pauldron_{side}', 'Schulterpanzer', 'torso', 'hull', 'shell',
               dict(pts=dome(sx, (6, 372), [(160, 210, 170, 66), (250, 240, 196, 86), (322, 190, 150, 66), (350, 116, 86, 40)]))),
              (f'pauldron_rim_{side}', 'Schulterrand', 'torso', 'hull', 'dark_metal',
               dict(pts=dome(sx, (6, 364), [(150, 226, 186, 70), (176, 228, 188, 70)])))]
        P += _medallion(f'shoulder_{side}', 'torso', (sx * 352, 6, 372), 38, 10)
    # Kopf: Hals, Kern, gewölbter Helm, Visier mit Augenlinie, Mittelkamm, Ohrmedaillons
    P += [('neck', 'Hals', 'head', 'cyl', 'dark_metal', dict(axis='z', r=46, len=80, c=(0, 0, 30))),
          ('head_core', 'Kopfkern', 'head', 'hull', 'graphite',
           dict(pts=rsection(150, -96, 92, 50, 56) + rsection(176, -108, 104, 60, 150) + rsection(150, -96, 96, 54, 250))),
          ('helmet', 'Helm', 'head', 'hull', 'shell',
           dict(pts=rsection(188, -118, 70, 70, 128) + rsection(184, -116, 100, 76, 206) + rsection(152, -102, 86, 64, 264)
                + rsection(96, -70, 50, 44, 294))),
          ('visor', 'Visier', 'head', 'hull', 'anodized', dict(pts=rsection_top(150, 60, 114, 30, 122) + rsection_top(160, 60, 116, 32, 198))),
          ('eye_line', 'Augenlinie', 'head', 'hull', 'energy',
           dict(pts=[(x, y, z) for x in (-46, 46) for y in (110, 119) for z in (162, 169)])),
          ('crest', 'Mittelkamm', 'head', 'hull', 'dark_metal',
           dict(pts=[(x, y, z) for x in (-5, 5) for y, z in ((100, 200), (88, 262), (40, 294), (-60, 292), (106, 206), (94, 268), (46, 300), (-60, 298))]))]
    P += _medallion('ear', 'head', (0, -6, 168), 30, 196)
    # Oberschenkel
    P += [('thigh_body', 'Oberschenkel', 'thigh', 'hull', 'graphite',
           dict(pts=rsection(160, -80, 74, 50, 30) + rsection(176, -86, 86, 56, 160) + rsection(116, -60, 58, 40, 420))),
          ('thigh_shell', 'Oberschenkelschale', 'thigh', 'hull', 'shell',
           dict(pts=rsection_top(170, -6, 98, 48, 70) + rsection_top(162, -6, 94, 48, 200) + rsection_top(120, -4, 70, 36, 396)))]
    # Knie
    P += [('knee', 'Kniegelenk', 'shin', 'cyl', 'dark_metal', dict(axis='x', r=52, len=128, c=(0, 0, 0))),
          ('knee_cap', 'Kniekappe', 'shin', 'hull', 'shell',
           dict(pts=rsection_top(110, 24, 86, 36, -50) + rsection_top(124, 24, 98, 42, 30) + rsection_top(88, 14, 76, 32, 80, z_top=104)))]
    P += _medallion('knee_med', 'shin', (0, 0, 0), 44, 134)
    # Schienbein (wie der Unterarm)
    P += [('shin_body', 'Schienbein', 'shin', 'hull', 'graphite',
           dict(pts=rsection(112, -62, 56, 36, 40) + rsection(136, -74, 68, 44, 170) + rsection(90, -50, 46, 30, 400))),
          ('shin_shell', 'Schienbeinschale', 'shin', 'hull', 'shell',
           dict(pts=rsection_top(126, -6, 82, 40, 120) + rsection_top(146, -8, 94, 46, 180) + rsection_top(98, -4, 64, 30, 392))),
          ('shin_plate', 'Schienbeinplatte', 'shin', 'hull', 'anodized',
           dict(pts=[(x, y, z) for z, w, yt in ((262, 54, 81), (380, 42, 64)) for x in (-w / 2, w / 2) for y in (yt - 3, yt + 6)]
                + [(0, y, 232) for y in (83, 92)]))]
    P += _bolts('shin', 76, 352)
    # Fuß (Rahmen: +Z nach vorn, +Y nach oben, Ursprung Knöchel)
    P += [('ankle', 'Knöchel', 'foot', 'cyl', 'dark_metal', dict(axis='x', r=34, len=104, c=(0, 0, 0))),
          ('foot_body', 'Fuß', 'foot', 'hull', 'graphite',
           dict(pts=rsection(112, -88, 26, 30, -70) + rsection(124, -88, 24, 34, 120) + rsection(104, -88, -6, 30, 196))),
          ('toe_cap', 'Zehenkappe', 'foot', 'hull', 'shell', dict(pts=rsection_top(126, -60, 30, 30, 80) + rsection_top(110, -84, -14, 26, 204))),
          ('heel', 'Fersenplatte', 'foot', 'hull', 'shell', dict(pts=rsection(116, -84, 12, 30, -82) + rsection(118, -84, 18, 30, -40))),
          ('sole', 'Sohle', 'foot', 'hull', 'rubber', dict(pts=rsection(128, -96, -84, 5, -86) + rsection(128, -96, -84, 5, 212)))]
    return P
