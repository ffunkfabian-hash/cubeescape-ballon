"""Szene „Hangar“ (0.9 „Parcours“): Sci-Fi-Militärhangar mit offener Torseite und einem Parcours durch die Halle.

Halle 40 × 60 m, Dach innen 14 m. x −20…20 (Westwand … Ostwand), y −30 (Tor) … +30 (Nordwand), Boden z = 0.
Der Spieler startet bei y = +25 und blickt nach −Y durch die Halle auf das offene Tor, dahinter Vorfeld, Splitterschutzwall
und Himmel. Vier Lichtszenen (Tag, Abend, Nacht, bewölkt) teilen dieselbe Geometrie und dieselben Lightmap-UVs.

Detailstufe (0.9, Nutzerwunsch „Detailtreue ähnlich wie bei der Waffe“): alle Bauteile gefast (`bevel_of`), Trapezblech als
echtes Profil (Wände 30 cm/3,5 cm, Dach 35 cm/5 cm, Container 28 cm), I-Profil-Stützen mit Fußplatte und Ankermuttern,
Schraubenreihen an Torpfosten und Torsturz, Knotenbleche am Fachwerk, Lichtband mit Sprossen, Kabeltrassen mit Kabeln,
Schaltschränke, Feuerlöscher, Strahlergehäuse mit Kühlrippen, Schilder (Strichschrift), Bodenfugen 5 m, Markierungen,
Ölflecken, Reifenspuren und Ausbesserungen als Bildmasken (DECALS), Kantenabrieb und Schmutz im Material (Rollen).

Parcours (COURSE, Reihenfolge): Start (y = 22) → Slalom zwischen Absperrgittern → Mauer 0,6 m überspringen → Kistenberg
0,6/1,2 m → Herunterspringen → Ducken durch die Containergasse unter der Rohrbrücke (1,35 m) → am Tor entlang über die
Leitwand → Treppe aufs Gerüst (3 m) → Laufsteg 20 m → Herunterspringen über eine Kiste → Ziel (y = 19, Ostseite).
14 Zielscheiben auf Höhen 0,45–10,95 m, Entfernungen bis ≈ 26 m, zwei teilverdeckt, drei nur von oben (Kistenburg).
"""
import math

from basic.scenes import box, cyl, beam, corr, solid, text_strokes

META = dict(name='hangar', de='Hangar', size_m=(40.0, 60.0, 14.0),
            summary='Sci-Fi-Militärhangar: Trapezblech, Stahlfachwerk, offenes Tor, Parcours mit 14 Zielen, vier Lichtszenen')

X0, X1, Y0, Y1, H = -20.0, 20.0, -30.0, 30.0, 14.0
TRUSS_Y = [-27.0 + 6.0 * k for k in range(10)]

# ------------------------------------------------------------------ Materialrollen
# color sRGB · rough/spec · vary (Helligkeitsrauschen, Maßstab vary_m) · pattern: joints (Fugen joint_m), stripes (45°, color2,
# stripe_m), grid (Gitterrost, color2, cell_m), vjoints (senkrechte Plattenfugen panel_m) · wear: Kantenabrieb (Bevel-Knoten,
# Messradius wear_r > Fase, Farbe wear_color) · grime: Schmutz in Ecken (AO, Abstand grime_d) · foot: Spritzschmutz unten (Höhe m)
# · streaks: Laufspuren senkrecht · decal: Bildmaske aus DECALS (im Weltraum projiziert) · Leuchten je Lichtszene (LIGHTINGS.emit)
W_STEEL = '#8E9399'
ROLES = {
    'concrete':      dict(color='#8E8B84', rough=0.82, spec=0.15, vary=0.16, vary_m=1.8, pattern='joints', joint_m=5.0, grime=0.35,
                          grime_d=0.6, mottle=0.16, mottle_m=9.0, decal='floor', de='Hallenboden Beton geglättet, Fugen 5 m, Markierungen und Flecken als Maske'),
    'concrete_out':  dict(color='#9B988F', rough=0.9, spec=0.15, vary=0.22, vary_m=2.5, pattern='joints', joint_m=5.0, grime=0.3,
                          grime_d=0.6, mottle=0.2, mottle_m=11.0, decal='apron', de='Vorfeld Beton, Fugen 5 m'),
    'concrete_wall': dict(color='#A39F94', rough=0.9, spec=0.2, vary=0.15, vary_m=0.8, wear=0.55, wear_color='#C9C5BA', grime=0.45,
                          foot=0.45, de='Fertigteilbeton (Schutzwand, Mauern)'),
    'concrete_panel': dict(color='#A7A398', rough=0.9, spec=0.2, vary=0.14, vary_m=0.8, pattern='vjoints', panel_m=3.0, wear=0.5,
                           wear_color='#C9C5BA', grime=0.45, foot=0.4, de='Betonsockel, Fertigteile 3 m'),
    'sheet':         dict(color='#C9C5B9', rough=0.55, spec=0.35, vary=0.07, vary_m=3.0, wear=0.2, wear_color=W_STEEL, grime=0.35,
                          streaks=0.16, mottle=0.07, mottle_m=6.0, de='Trapezblech lackiert cremeweiß (30 cm / 3,5 cm)'),
    'sheet_roof':    dict(color='#B2AFA6', rough=0.6, spec=0.3, vary=0.06, vary_m=4.0, grime=0.25, mottle=0.1, mottle_m=8.0, de='Dachblech innen (35 cm / 5 cm)'),
    'steel':         dict(color='#4A4F57', rough=0.5, spec=0.4, vary=0.06, vary_m=2.0, wear=0.45, wear_color=W_STEEL, grime=0.35,
                          de='Lackstahl Graphit (Tragwerk)'),
    'steel_dark':    dict(color='#34373D', rough=0.5, spec=0.4, vary=0.07, vary_m=1.2, wear=0.6, wear_color='#8A8F95', grime=0.3,
                          de='Lackstahl dunkel (Tor, Gehäuse)'),
    'steel_light':   dict(color='#D3CAB6', rough=0.5, spec=0.4, vary=0.06, vary_m=2.0, wear=0.4, wear_color=W_STEEL, grime=0.4,
                          foot=0.35, de='Lackstahl Creme (Torflügel, Container, Rohre)'),
    'galv':          dict(color='#9A9D9F', rough=0.45, spec=0.5, vary=0.12, vary_m=0.6, grime=0.3, de='Stahl verzinkt (Trassen, Gitter)'),
    'accent':        dict(color='#D9641E', rough=0.5, spec=0.4, wear=0.5, wear_color='#5E6166', grime=0.3,
                          de='Akzent Orange (Geländer, Regalträger)'),
    'hazard':        dict(color='#E0B21C', color2='#1D1E21', rough=0.6, spec=0.35, pattern='stripes', stripe_m=0.25, wear=0.45,
                          wear_color='#6E7176', grime=0.35, foot=0.3, de='Warnanstrich Gelb/Schwarz 45°'),
    'pipe_green':    dict(color='#4E6E58', rough=0.5, spec=0.35, wear=0.3, wear_color=W_STEEL, grime=0.3, de='Rohrleitung Grün'),
    'crate_olive':   dict(color='#5C6350', rough=0.7, spec=0.3, vary=0.06, vary_m=0.7, wear=0.7, wear_color='#A49E8C', grime=0.4,
                          foot=0.3, de='Transportkiste Oliv'),
    'crate_grey':    dict(color='#50555C', rough=0.65, spec=0.3, vary=0.06, vary_m=0.7, wear=0.7, wear_color='#A0A4A8', grime=0.4,
                          foot=0.3, de='Transportkiste Grau'),
    'crate_cream':   dict(color='#CFC4AC', rough=0.6, spec=0.3, vary=0.06, vary_m=0.7, wear=0.65, wear_color='#8E9399', grime=0.45,
                          foot=0.3, de='Transportkiste Creme'),
    'container_teal': dict(color='#2F5D62', rough=0.6, spec=0.3, vary=0.08, vary_m=1.2, wear=0.4, wear_color='#8E8A80', grime=0.4,
                           foot=0.35, streaks=0.25, decal='code_a', de='Seecontainer Petrol'),
    'container_rust': dict(color='#8A3B24', rough=0.65, spec=0.3, vary=0.1, vary_m=1.2, wear=0.4, wear_color='#8E8A80', grime=0.4,
                           foot=0.35, streaks=0.25, decal='code_b', de='Seecontainer Rostrot'),
    'barrel_blue':   dict(color='#34506B', rough=0.5, spec=0.4, wear=0.5, wear_color=W_STEEL, grime=0.35, foot=0.3, de='Fass Blau'),
    'barrel_orange': dict(color='#C85A1C', rough=0.5, spec=0.4, wear=0.5, wear_color=W_STEEL, grime=0.35, foot=0.3, de='Fass Orange'),
    'wood':          dict(color='#8E7556', rough=0.85, spec=0.25, vary=0.14, vary_m=0.3, grime=0.35, de='Palette Holz'),
    'rubber':        dict(color='#1B1C1F', rough=0.9, spec=0.2, de='Gummi (Räder, Kabel)'),
    'grating':       dict(color='#6A6E73', color2='#1E2023', rough=0.6, spec=0.35, pattern='grid', cell_m=0.06, wear=0.3,
                          wear_color='#A3A7AB', grime=0.3, de='Gitterrost verzinkt (Bühne, Stufen)'),
    'glass_dark':    dict(color='#232A31', rough=0.15, spec=0.5, de='Fensterscheibe (dunkel, undurchsichtig)'),
    'lamp':          dict(color='#FFF3E0', rough=0.5, spec=0.3, de='Leuchtfläche Hallenstrahler'),
    'emerg_red':     dict(color='#FF4A36', rough=0.3, spec=0.4, de='Notleuchte rot (Linse)'),
    'beacon_blue':   dict(color='#4A86FF', rough=0.3, spec=0.4, de='Rollweg-Randfeuer blau (Linse)'),
    'extinguisher':  dict(color='#B3261E', rough=0.4, spec=0.45, wear=0.3, wear_color='#D8D2C4', de='Feuerlöscher rot'),
}
# Untergrund für Einschläge (0.39 „Scatter“, ego.IMPACT_SURFACES): Rollen aus Stahl und Blech → metal; Beton, Holz, Gummi, Glas und
# Leuchten ohne (Einschlag unverändert). Reine Kollisionsquader nennen ihren Untergrund selbst (solid surface=…: Container, Bürocontainer,
# Geländer, Absperrgitter); Kisten bleiben ohne (Material der Transportkisten nicht festgelegt).
SURFACES = dict(metal=('sheet', 'sheet_roof', 'steel', 'steel_dark', 'steel_light', 'galv', 'accent', 'hazard', 'pipe_green', 'container_teal',
                       'container_rust', 'barrel_blue', 'barrel_orange', 'grating', 'extinguisher'))

# ------------------------------------------------------------------ Bildmasken (DECALS)
# Je Blatt: Ursprung (Weltpunkt der Ecke u = v = 0), Achsen u, v (Einheitsvektoren), Größe (m), Auflösung px_m (m je Pixel),
# optional Grundfarbe bg (deckend) und Tiefe (nur Flächen in ±depth um die Ebene). Einträge `items` (Maße in m auf dem Blatt):
#   rect a b color alpha · frame a b w color · hatch a b c1 c2 stripe_m (45°) · checker a b cell c1 c2 · text at h s color w align
#   line pts w color alpha · ring c r w color · disc c r color alpha · stain c r color alpha seed · track pts w gap color alpha seed
#   poly pts color
DECALS = {}


def _d(**kw):
    return kw


def F(x, y):
    """Weltlage (x, y) auf dem Bodenblatt."""
    return (x - X0, y - (Y0 - 0.5))


Y_START, Y_FINISH = 22.0, 19.0
floor = []
# Ausbesserungen und Verschmutzung (unter den Markierungen)
for (x, y, w, h, a) in ((-8.0, 12.0, 2.6, 1.6, 0.16), (6.0, -14.0, 3.0, 2.2, 0.14), (-12.0, -2.0, 1.8, 1.2, 0.15), (15.0, 26.0, 2.0, 1.5, 0.12)):
    floor.append(_d(kind='rect', a=F(x - w / 2, y - h / 2), b=F(x + w / 2, y + h / 2), color='#6E6B66', alpha=a))
STAINS = [(-8.3, -21.2, 0.9, 0.55, 1), (-7.2, -20.6, 0.5, 0.45, 2), (-9.1, -21.9, 0.35, 0.4, 3), (0.4, -10.5, 1.3, 0.35, 4),
          (-0.8, -12.0, 0.7, 0.3, 5), (1.2, -16.5, 0.5, 0.3, 6), (15.0, 13.5, 0.8, 0.35, 7), (14.2, 17.8, 0.5, 0.3, 8),
          (-6.0, 18.0, 0.4, 0.25, 9), (9.5, -27.0, 0.6, 0.3, 10), (-14.0, 4.0, 0.45, 0.25, 11), (6.0, 6.0, 0.35, 0.25, 12),
          (-2.0, -26.5, 0.8, 0.3, 13), (17.0, -22.0, 0.6, 0.35, 14), (-18.6, 9.5, 0.5, 0.3, 15),
          (-10.0, -6.5, 1.1, 0.4, 16), (5.0, -19.5, 0.9, 0.4, 17), (-14.5, -25.6, 0.7, 0.4, 18), (9.0, 16.0, 0.8, 0.35, 19),
          (-6.8, -22.6, 0.9, 0.5, 20), (-1.5, 21.0, 0.5, 0.3, 21), (13.5, -1.0, 1.0, 0.35, 22)]
for (x, y, r, a, s) in STAINS:
    floor.append(_d(kind='stain', c=F(x, y), r=r, color='#1E1A16', alpha=min(0.85, a * 1.5), seed=s))
# Gabelstapler-Spuren vom Tor zum Regal
TRACK = [(6.0, -29.5), (7.0, -22.0), (8.6, -12.0), (9.6, -2.0), (11.0, 6.0), (13.8, 10.6), (16.0, 12.6)]
floor.append(_d(kind='track', pts=[F(*p) for p in TRACK], w=0.2, gap=0.95, color='#24211E', alpha=0.2, seed=21))
floor.append(_d(kind='track', pts=[F(*p) for p in ((16.2, 12.0), (14.8, 15.5), (15.4, 19.5), (16.4, 23.0))], w=0.2, gap=0.95,
                color='#24211E', alpha=0.16, seed=22))
# Markierungen
floor.append(_d(kind='hatch', a=F(-17.0, -29.5), b=F(17.0, -28.6), c1='#E0B21C', c2='#1D1E21', stripe_m=0.25))
floor.append(_d(kind='line', pts=[F(0.0, -28.4), F(0.0, -9.2)], w=0.15, color='#D6AE2E', alpha=1.0))          # Einrolllinie
floor.append(_d(kind='rect', a=F(-2.0, -9.2), b=F(2.0, -8.85), color='#D6AE2E', alpha=1.0))                     # Haltebalken
floor.append(_d(kind='rect', a=F(-17.0, -28.4), b=F(17.0, -28.2), color='#2C2E31', alpha=0.9))                  # Rinne
for s, x in (('w', -13.0), ('w2', -14.2)):
    floor.append(_d(kind='line', pts=[F(x, -6.5), F(x, 25.0)], w=0.1, color='#D6AE2E', alpha=0.95))           # Gehweg West
for x in (15.4, 16.6):
    floor.append(_d(kind='line', pts=[F(x, -4.0), F(x, 11.4)], w=0.1, color='#D6AE2E', alpha=0.95))            # Gehweg Ost
floor.append(_d(kind='checker', a=F(-3.5, Y_START - 0.2), b=F(3.5, Y_START + 0.2), cell=0.2, c1='#E8E5DC', c2='#1D1E21'))
floor.append(_d(kind='checker', a=F(8.6, Y_FINISH - 0.2), b=F(14.4, Y_FINISH + 0.2), cell=0.2, c1='#E8E5DC', c2='#1D1E21'))
floor.append(_d(kind='hatch', a=F(17.6, -18.8), b=F(18.95, -16.2), c1='#E0B21C', c2='#1D1E21', stripe_m=0.2))  # vor Schaltschrank
floor.append(_d(kind='frame', a=F(-10.0, -22.8), b=F(-6.2, -20.0), w=0.1, color='#D6AE2E'))                    # Stellplatz Aggregat
floor.append(_d(kind='text', at=F(6.0, -23.0), h=2.4, s='H3', color='#E3E0D6', w=0.11, align='center'))
for n, (x, y) in (('1', (0.0, 4.25)), ('3', (-18.0, -21.6))):
    floor.append(_d(kind='ring', c=F(x, y), r=0.62, w=0.08, color='#E3E0D6'))
    floor.append(_d(kind='text', at=(F(x, y)[0], F(x, y)[1] - 0.3), h=0.6, s=n, color='#E3E0D6', w=0.09, align='center'))
DECALS['floor'] = dict(origin=(X0, Y0 - 0.5, 0.0), u=(1, 0, 0), v=(0, 1, 0), size=(40.0, 60.5), px_m=0.02, depth=0.05, items=floor)

AY0, AY1 = -52.0, Y0 - 0.5


def FA(x, y):
    return (x - X0, y - AY0)


apron = [_d(kind='stain', c=FA(x, y), r=r, color='#1E1A16', alpha=a, seed=s)
         for (x, y, r, a, s) in ((1.0, -40.0, 1.6, 0.25, 31), (-1.5, -44.0, 1.0, 0.22, 32), (3.0, -36.0, 0.8, 0.2, 33),
                                 (-8.0, -47.0, 0.7, 0.2, 34), (11.0, -33.0, 0.6, 0.2, 35))]
apron.append(_d(kind='track', pts=[FA(*p) for p in ((-1.4, -51.0), (-1.2, -44.0), (-0.6, -36.0), (-0.3, -31.0))], w=0.35, gap=3.2,
                color='#1D1B19', alpha=0.22, seed=36))
apron.append(_d(kind='line', pts=[FA(0.0, -51.0), FA(0.0, -30.6)], w=0.15, color='#D6AE2E', alpha=1.0))
apron.append(_d(kind='rect', a=FA(-6.0, -38.2), b=FA(6.0, -37.8), color='#D6AE2E', alpha=1.0))
for x in (-17.4, 17.4):
    apron.append(_d(kind='line', pts=[FA(x, -51.0), FA(x, -30.6)], w=0.12, color='#D6AE2E', alpha=0.9))
apron.append(_d(kind='text', at=FA(0.0, -48.5), h=1.8, s='H3', color='#E3E0D6', w=0.1, align='center'))
DECALS['apron'] = dict(origin=(X0, AY0, 0.0), u=(1, 0, 0), v=(0, 1, 0), size=(40.0, AY1 - AY0), px_m=0.04, depth=0.05, items=apron)

P = []
M = 0.01   # Farbschicht


def right_of(n):
    """Rechte Richtung auf einer Fläche mit Normale n (Blick gegen n, oben = +Z); liegend (n = +Z): +X."""
    if abs(n[2]) > 0.9:
        return (1.0, 0.0, 0.0)
    return (-n[1], n[0], 0.0)


def sign(pid, de, group, center, n, w, h, bg, items, t=0.015, px_m=0.004, wear=0.25):
    """Schild: Platte w × h (Mitte `center` auf der Vorderseite, Normale n achsparallel), eigene Rolle mit Bildmaske."""
    u = right_of(n)
    v = (0.0, 0.0, 1.0) if abs(n[2]) < 0.9 else (0.0, 1.0, 0.0)
    o = tuple(center[k] - u[k] * w / 2 - v[k] * h / 2 for k in range(3))
    role = f'sign_{pid}'
    ROLES[role] = dict(color=bg, rough=0.45, spec=0.35, wear=wear, wear_color='#B8BBBE', wear_r=0.012, grime=0.2, decal=role,
                       de=f'Schild: {de}')
    DECALS[role] = dict(origin=o, u=u, v=v, size=(w, h), px_m=px_m, bg=bg, depth=0.05, items=items)
    lo = [center[k] - u[k] * w / 2 - v[k] * h / 2 for k in range(3)]
    hi = [center[k] + u[k] * w / 2 + v[k] * h / 2 for k in range(3)]
    ax = [k for k in range(3) if abs(n[k]) > 0.9][0]
    lo[ax] = center[ax] - (t if n[ax] > 0 else 0.0)
    hi[ax] = center[ax] + (0.0 if n[ax] > 0 else t)
    return box(pid, f'Schild {de}', group, role, lo, hi, collide=False, bev=0.0)


def txt(s, h, w_frac, color, cu, cv, align='center'):
    return _d(kind='text', at=(cu, cv), h=h, s=s, color=color, w=w_frac, align=align)


def bolts(pid, de, group, mat, axis, side, at, pts, r=0.022, l=0.024, segs=6):
    """Schraubenköpfe auf einer Fläche (Normale `axis`, sichtbar nach `side`, Fläche bei `at`), Punkte in den übrigen Achsen."""
    out = []
    i = 'xyz'.index(axis)
    for k, q in enumerate(pts):
        c = list(q)
        c.insert(i, at + side * l / 2)
        out.append(cyl(f'{pid}_{k:02d}', de, group, mat, axis, c, r, l, segs=segs, collide=False, bev=0.0))
    return out


# ------------------------------------------------------------------ Boden (Zone boden): 24 Felder 10 × 10 m, Fugen 5 m im Material
for i, xa in enumerate(range(-20, 20, 10)):
    for j, ya in enumerate((Y0 - 0.5, -20.0, -10.0, 0.0, 10.0, 20.0)):
        yb = (-20.0, -10.0, 0.0, 10.0, 20.0, Y1)[j]
        P.append(box(f'floor_{i}{j}', 'Hallenboden', 'Boden', 'concrete', (xa, ya, -0.3), (xa + 10, yb, 0.0),
                     skip=('-z', '+x', '-x', '+y', '-y'), bev=0.0))

# ------------------------------------------------------------------ Wände (Zone wand unten, Zone fern oben)
SOCKEL = 1.2
ALL = set(('+x', '-x', '+y', '-y', '+z', '-z'))
PROF_W = dict(period=0.3, depth=0.035, crest=0.09, flank=0.06)
PROF_R = dict(period=0.35, depth=0.05, crest=0.11, flank=0.06)
PROF_C = dict(period=0.28, depth=0.036, crest=0.07, flank=0.05)
BAND = (8.6, 10.4)                      # Lichtband (offen, Sprossen) in West- und Ostwand
BAYS = [Y0 + 0.5] + TRUSS_Y + [Y1]      # Felder zwischen den Stützenachsen (Stöße hinter den Stützen)
DOOR_E, DOOR_N = -2.0, 6.6                # Türmitten (Ostwand y, Nordwand x); Sockel dort unterbrochen (Zarge 1,5 m)
for s, x, sg in (('w', X0, 1), ('e', X1, -1)):
    G = 'Wand_West' if s == 'w' else 'Wand_Ost'
    cuts = [(Y0 + 0.5, Y1)] if s == 'w' else [(Y0 + 0.5, DOOR_E - 0.75), (DOOR_E + 0.75, Y1)]
    for m, (ya, yb) in enumerate(cuts):
        P.append(box(f'plinth_{s}{m}', 'Betonsockel', G, 'concrete_panel', (x if sg > 0 else x - 0.3, ya, 0),
                     (x + 0.3 if sg > 0 else x, yb, SOCKEL + 0.05), skip=('-x',) if sg > 0 else ('+x',), bev=0.02))
        P.append(box(f'plinth_{s}{m}_cap', 'Sockelabdeckung (Blech)', G, 'galv', (x if sg > 0 else x - 0.33, ya, SOCKEL + 0.05),
                     (x + 0.33 if sg > 0 else x, yb, SOCKEL + 0.08), skip=('-x',) if sg > 0 else ('+x',), collide=False, bev=0.006))
    for k, (ya, yb) in enumerate(zip(BAYS, BAYS[1:])):
        P.append(corr(f'wall_{s}_{k}_lo', 'Trapezblechwand', G, 'sheet', 'x', sg, x + sg * PROF_W['depth'], 'y', ya, yb, SOCKEL, BAND[0],
                      PROF_W))
        P.append(corr(f'wall_{s}_{k}_hi', 'Trapezblechwand oben', 'Wand_Oben', 'sheet', 'x', sg, x + sg * PROF_W['depth'], 'y', ya, yb,
                      BAND[1], H + 0.1, PROF_W))
        # Lichtband: Brüstungs- und Sturzblech, Sprossen alle 1,5 m
        P.append(box(f'band_{s}_{k}_sill', 'Lichtband Brüstungsblech', 'Wand_Oben', 'galv', (x if sg > 0 else x - 0.12, ya, BAND[0] - 0.06),
                     (x + 0.12 if sg > 0 else x, yb, BAND[0]), collide=False, bev=0.008))
        P.append(box(f'band_{s}_{k}_lintel', 'Lichtband Sturzblech', 'Wand_Oben', 'galv', (x if sg > 0 else x - 0.1, ya, BAND[1]),
                     (x + 0.1 if sg > 0 else x, yb, BAND[1] + 0.06), collide=False, bev=0.008))
        n = max(1, round((yb - ya) / 1.5))
        for m in range(1, n):
            ym = ya + (yb - ya) * m / n
            P.append(box(f'band_{s}_{k}_m{m}', 'Lichtband Sprosse', 'Wand_Oben', 'galv', (x if sg > 0 else x - 0.07, ym - 0.03, BAND[0]),
                         (x + 0.07 if sg > 0 else x, ym + 0.03, BAND[1]), collide=False, bev=0.0))
for m, (xa, xb, sk) in enumerate(((X0 + 0.3, DOOR_N - 0.75, ('+y', '-x')), (DOOR_N + 0.75, X1 - 0.3, ('+y', '+x')))):
    P.append(box(f'plinth_n{m}', 'Betonsockel Nord', 'Wand_Nord', 'concrete_panel', (xa, Y1 - 0.3, 0), (xb, Y1, SOCKEL + 0.05), skip=sk, bev=0.02))
    P.append(box(f'plinth_n{m}_cap', 'Sockelabdeckung Nord', 'Wand_Nord', 'galv', (xa, Y1 - 0.33, SOCKEL + 0.05), (xb, Y1, SOCKEL + 0.08),
                 skip=sk, collide=False, bev=0.006))
NB = [X0, -14.0, -8.0, -2.0, 4.0, 10.0, 16.0, X1]
for k, (xa, xb) in enumerate(zip(NB, NB[1:])):
    P.append(corr(f'wall_n_{k}_lo', 'Trapezblechwand Nord', 'Wand_Nord', 'sheet', 'y', -1, Y1 - PROF_W['depth'], 'x', xa, xb, SOCKEL,
                  BAND[0], PROF_W))
    P.append(corr(f'wall_n_{k}_hi', 'Trapezblechwand Nord oben', 'Wand_Oben', 'sheet', 'y', -1, Y1 - PROF_W['depth'], 'x', xa, xb,
                  BAND[0], H + 0.1, PROF_W))
for s, x in (('w', X0), ('e', X1)):
    sg = 1 if x < 0 else -1
    P.append(box(f'corner_{s}', 'Eckstütze Nord', 'Stuetzen', 'steel', (x, Y1 - 0.45, 0), (x + sg * 0.45, Y1, H + 0.1),
                 skip=('+y', '-x' if x < 0 else '+x')))
# Türen mit Zarge, Drücker, Notausgangsschild und Notleuchte
EMERG = []          # Lagen der Notleuchten (Linsenmitte, Leuchtrichtung)


def door(pid, group, axis, side, at, c, wall_de):
    """Stahltür 1,2 × 2,2 m in der Wand (Wandvorderfläche bei `at`, sichtbar nach `side`, Sockel dort unterbrochen), Mitte c."""
    out = []
    i = 'xyz'.index(axis)
    j = 1 - i if i < 2 else 0

    def bx(pid2, de, mat, d0, d1, s0, s1, z0, z1, collide=False, bev=None):
        a, b = [0.0] * 3, [0.0] * 3
        a[i], b[i] = sorted((at + side * d0, at + side * d1))
        a[j], b[j] = c + s0, c + s1
        a[2], b[2] = z0, z1
        return box(pid2, de, group, mat, a, b, collide=collide, bev=bev)
    out.append(bx(pid, f'Personaltür {wall_de}', 'steel_dark', -0.035, 0.04, -0.6, 0.6, 0, 2.2, collide=True, bev=0.01))
    out.append(bx(pid + '_frame_t', 'Türzarge oben', 'hazard', -0.035, 0.1, -0.75, 0.75, 2.2, 2.35, bev=0.01))
    for k, s0 in enumerate((-0.75, 0.6)):
        out.append(bx(f'{pid}_frame_{k}', 'Türzarge', 'hazard', -0.035, 0.1, s0, s0 + 0.15, 0, 2.2, bev=0.01))
    out.append(bx(pid + '_kick', 'Trittblech', 'galv', 0.04, 0.045, -0.55, 0.55, 0.02, 0.3, bev=0.0))
    out.append(bx(pid + '_handle', 'Drücker', 'galv', 0.04, 0.1, 0.32, 0.47, 1.02, 1.06, bev=0.0))
    out.append(bx(pid + '_handle_rose', 'Rosette', 'galv', 0.04, 0.06, 0.33, 0.39, 0.98, 1.12, bev=0.0))
    cen = [0.0] * 3
    cen[i] = at + side * 0.0
    cen[j] = c
    cen[2] = 2.62
    nrm = [0.0] * 3
    nrm[i] = float(side)
    out.append(sign(pid + '_exit', 'Notausgang', group, cen, nrm, 0.9, 0.3, '#1E8A4A',
                    [txt('NOTAUSGANG', 0.11, 0.13, '#F2F2EC', 0.38, 0.095), _d(kind='text', at=(0.76, 0.09), h=0.13, s='>',
                                                                                   color='#F2F2EC', w=0.14, align='center')]))
    # Notleuchte über dem Schild
    out.append(bx(pid + '_emerg', 'Notleuchte Gehäuse', 'steel_dark', 0.0, 0.12, -0.16, 0.16, 2.86, 2.98, bev=0.008))
    out.append(bx(pid + '_emerg_lens', 'Notleuchte Linse', 'emerg_red', 0.12, 0.15, -0.12, 0.12, 2.88, 2.96, bev=0.0))
    pos = [0.0] * 3
    pos[i] = at + side * 0.3
    pos[j] = c
    pos[2] = 2.92
    EMERG.append((tuple(pos), tuple(nrm)))
    return out


P += door('door_n', 'Wand_Nord', 'y', -1, Y1 - PROF_W['depth'], DOOR_N, 'Nordwand')
P += door('door_e', 'Wand_Ost', 'x', -1, X1 - PROF_W['depth'], DOOR_E, 'Ostwand')
P.append(sign('hall_n', 'Hallennummer Nord', 'Wand_Nord', (0.0, Y1 - PROF_W['depth'] - 0.01, 7.6), (0, -1, 0), 4.6, 2.6, '#2B2E33',
              [_d(kind='frame', a=(0.08, 0.08), b=(4.52, 2.52), w=0.05, color='#E3E0D6'), txt('H3', 1.7, 0.13, '#E3E0D6', 2.3, 0.45)],
              px_m=0.008))

# ------------------------------------------------------------------ Stützen HEB 400 (Zone wand), Wandverbände, Feuerlöscher
for k, y in enumerate(TRUSS_Y):
    for s, sg in (('w', -1), ('e', 1)):
        xo, xi = sg * 19.98, sg * 19.58           # Außen-, Innenflansch
        lo, hi = min(xo, xi), max(xo, xi)
        fin = (xi - sg * 0.024, xi)
        P.append(box(f'column_{k}_{s}_fl_in_lo', 'Stütze Innenflansch (Anfahrschutz-Anstrich)', 'Stuetzen', 'hazard',
                     (min(fin), y - 0.15, 0), (max(fin), y + 0.15, 1.5)))
        P.append(box(f'column_{k}_{s}_fl_in', 'Stütze Innenflansch', 'Stuetzen', 'steel', (min(fin), y - 0.15, 1.5), (max(fin), y + 0.15, H)))
        fout = (xo, xo - sg * 0.024)
        P.append(box(f'column_{k}_{s}_fl_out', 'Stütze Außenflansch', 'Stuetzen', 'steel', (min(fout), y - 0.15, 0), (max(fout), y + 0.15, H),
                     skip=('-x' if sg < 0 else '+x',)))
        P.append(box(f'column_{k}_{s}_web', 'Stütze Steg', 'Stuetzen', 'steel', (lo + 0.024, y - 0.008, 0), (hi - 0.024, y + 0.008, H),
                     bev=0.0))
        P.append(box(f'column_{k}_{s}_base', 'Fußplatte', 'Stuetzen', 'steel_dark', (min(xo, xi - sg * 0.12), y - 0.26, 0),
                     (max(xo, xi - sg * 0.12), y + 0.26, 0.03), collide=False, bev=0.008))
        for m, (dx, dy) in enumerate(((-0.08, -0.2), (-0.08, 0.2), (-0.32, -0.2), (-0.32, 0.2))):
            P.append(cyl(f'column_{k}_{s}_nut{m}', 'Ankermutter', 'Stuetzen', 'steel_dark', 'z', (xi + sg * dx, y + dy, 0.055), 0.028, 0.05,
                         segs=6, collide=False, bev=0.0))
        P.append(beam(f'column_{k}_{s}_haunch', 'Voute (Binderanschluss)', 'Stuetzen', 'steel', (xi, y, 10.2), (xi - sg * 0.9, y, 11.25),
                      0.2, 0.12))
for s, x in (('w', -19.5), ('e', 19.5)):          # Wandverbände (Rundstahl) in den Endfeldern
    for (ya, yb) in ((-27.0, -21.0), (21.0, 27.0)):
        P.append(beam(f'brace_{s}_{int(ya)}_a', 'Wandverband', 'Stuetzen', 'steel', (x, ya + 0.2, 1.4), (x, yb - 0.2, 8.4), 0.04, 0.04, bev=0.0))
        P.append(beam(f'brace_{s}_{int(ya)}_b', 'Wandverband', 'Stuetzen', 'steel', (x, yb - 0.2, 1.4), (x, ya + 0.2, 8.4), 0.04, 0.04, bev=0.0))
for k, (s, sg) in ((6, ('w', -1)), (3, ('e', 1)), (8, ('e', 1))):
    y = TRUSS_Y[k]
    xf = sg * 19.58 - sg * 0.12
    P.append(cyl(f'extinguisher_{s}{k}', 'Feuerlöscher', 'Stuetzen', 'extinguisher', 'z', (xf, y, 0.95), 0.085, 0.5, segs=12, collide=False))
    P.append(cyl(f'extinguisher_{s}{k}_head', 'Feuerlöscher Armatur', 'Stuetzen', 'steel_dark', 'z', (xf, y, 1.25), 0.03, 0.1, segs=8,
                 collide=False, bev=0.0))
    P.append(box(f'extinguisher_{s}{k}_bracket', 'Halter', 'Stuetzen', 'steel_dark', (min(xf, sg * 19.58), y - 0.06, 0.9),
                 (max(xf, sg * 19.58), y + 0.06, 0.98), collide=False, bev=0.0))
    P.append(box(f'extinguisher_{s}{k}_plate', 'Hinweisschild Feuerlöscher', 'Stuetzen', 'extinguisher',
                 (min(sg * 19.58, sg * 19.565), y - 0.14, 1.55), (max(sg * 19.58, sg * 19.565), y + 0.14, 1.85), collide=False, bev=0.0))

# ------------------------------------------------------------------ Kabeltrassen, Schaltschränke (Zone wand)
TZ = 4.6
for s, sg in (('w', -1), ('e', 1)):
    xa, xb = sorted((sg * 19.5, sg * 19.1))
    for k, (ya, yb) in enumerate(zip(BAYS, BAYS[1:])):
        G = 'Technik'
        P.append(box(f'tray_{s}{k}', 'Kabeltrasse Boden', G, 'galv', (xa, ya, TZ), (xb, yb, TZ + 0.01), collide=False, bev=0.0))
        for m, xr in enumerate((xa, xb - 0.012)):
            P.append(box(f'tray_{s}{k}_rail{m}', 'Kabeltrasse Seitenholm', G, 'galv', (xr, ya, TZ), (xr + 0.012, yb, TZ + 0.08),
                         collide=False, bev=0.0))
        for m, (xc, rc) in enumerate(((xa + 0.08, 0.022), (xa + 0.15, 0.018), (xa + 0.22, 0.026), (xa + 0.3, 0.016))):
            P.append(cyl(f'tray_{s}{k}_cable{m}', 'Kabel', G, 'rubber', 'y', (xc, (ya + yb) / 2, TZ + 0.01 + rc), rc, yb - ya,
                         segs=8, collide=False, bev=0.0))
    for k, y in enumerate(TRUSS_Y):
        P.append(box(f'tray_{s}_bracket{k}', 'Trassenkonsole', 'Technik', 'galv', (min(sg * 19.58, sg * 19.08), y - 0.03, TZ - 0.06),
                     (max(sg * 19.58, sg * 19.08), y + 0.03, TZ), collide=False, bev=0.0))


def cabinet(pid, group, x0, x1, y0, y1, face, de):
    """Schaltschrank (Standgerät 2,0 m) mit zwei Türen, Griffen, Sockel, Warnschild; Leitungen hoch zur Trasse."""
    out = [box(pid, de, group, 'steel_light', (x0, y0, 0.1), (x1, y1, 2.0), bev=0.012),
           box(pid + '_plinth', 'Schranksockel', group, 'steel_dark', (x0 + 0.02, y0 + 0.02, 0), (x1 - 0.02, y1 - 0.02, 0.1), collide=False,
               bev=0.0),
           box(pid + '_roof', 'Schrankdach', group, 'steel_dark', (x0 - 0.02, y0 - 0.02, 2.0), (x1 + 0.02, y1 + 0.02, 2.04), collide=False,
               bev=0.006)]
    ax, sd = face
    if ax == 'x':
        xf = x0 if sd < 0 else x1
        cy = (y0 + y1) / 2
        out.append(box(pid + '_seam', 'Türfuge', group, 'steel_dark', (xf - 0.003, cy - 0.006, 0.15), (xf + 0.003, cy + 0.006, 1.95),
                       collide=False, bev=0.0))
        for m, yy in enumerate((cy - 0.08, cy + 0.08)):
            out.append(box(f'{pid}_grip{m}', 'Schwenkgriff', group, 'steel_dark', (xf + sd * 0.03 if sd > 0 else xf - 0.03, yy - 0.015, 1.0),
                           (xf if sd < 0 else xf + 0.03, yy + 0.015, 1.18), collide=False, bev=0.0))
        cen = (xf, cy - 0.45 if (y1 - y0) > 1.2 else cy, 1.55)
        nrm = (float(sd), 0.0, 0.0)
        rng = (y0, y1)
    else:
        yf = y0 if sd < 0 else y1
        cx = (x0 + x1) / 2
        out.append(box(pid + '_seam', 'Türfuge', group, 'steel_dark', (cx - 0.006, yf - 0.003, 0.15), (cx + 0.006, yf + 0.003, 1.95),
                       collide=False, bev=0.0))
        for m, xx in enumerate((cx - 0.08, cx + 0.08)):
            out.append(box(f'{pid}_grip{m}', 'Schwenkgriff', group, 'steel_dark', (xx - 0.015, yf - 0.03 if sd < 0 else yf, 1.0),
                           (xx + 0.015, yf if sd < 0 else yf + 0.03, 1.18), collide=False, bev=0.0))
        cen = (cx - 0.45, yf, 1.55)
        nrm = (0.0, float(sd), 0.0)
        rng = (x0, x1)
    out.append(sign(pid + '_volt', 'Warnung Spannung', group, cen, nrm, 0.3, 0.27, '#E8C21E',
                    [_d(kind='poly', pts=[(0.03, 0.03), (0.27, 0.03), (0.15, 0.245)], color='#1D1E21'),
                     _d(kind='poly', pts=[(0.055, 0.045), (0.245, 0.045), (0.15, 0.21)], color='#E8C21E'),
                     _d(kind='line', pts=[(0.165, 0.18), (0.13, 0.12), (0.17, 0.115), (0.135, 0.06)], w=0.014, color='#1D1E21',
                        alpha=1.0)], px_m=0.002))
    for m in range(3):
        t = 0.25 + 0.25 * m
        if ax == 'x':
            c = ((x0 + x1) / 2, y0 + (y1 - y0) * t, (2.04 + TZ) / 2)
        else:
            c = (x0 + (x1 - x0) * t, (y0 + y1) / 2, (2.04 + TZ) / 2)
        out.append(cyl(f'{pid}_conduit{m}', 'Leitungsrohr', group, 'galv', 'z', c, 0.028, TZ - 2.04, segs=8, collide=False, bev=0.0))
    return out


P += cabinet('cabinet_e', 'Technik', 19.0, 19.6, -18.6, -16.4, ('x', -1), 'Schaltschrank Ost')
P += cabinet('cabinet_n', 'Technik', 8.4, 10.4, 29.05, 29.65, ('y', -1), 'Schaltschrank Nord')

# ------------------------------------------------------------------ Dach (Zone fern): Trapezblech, Pfetten, Fachwerk mit Knotenblechen
for i, xa in enumerate(range(-20, 20, 10)):
    for j, (ya, yb) in enumerate(zip((Y0 - 0.5, -20.0, -10.0, 0.0, 10.0, 20.0), (-20.0, -10.0, 0.0, 10.0, 20.0, Y1))):
        P.append(corr(f'roof_{i}{j}', 'Dachblech innen', 'Dach', 'sheet_roof', 'z', -1, H, 'y', ya, yb, xa, xa + 10, PROF_R, collide=False))
XC = 19.58
for k, y in enumerate(TRUSS_Y):
    zb0, zb1, zt0, zt1 = 11.2, 11.45, 13.5, 13.78
    P.append(box(f'truss_{k}_bottom', 'Binder Untergurt', 'Fachwerk', 'steel', (-XC, y - 0.12, zb0), (XC, y + 0.12, zb1), collide=False))
    P.append(box(f'truss_{k}_top', 'Binder Obergurt', 'Fachwerk', 'steel', (-XC, y - 0.12, zt0), (XC, y + 0.12, zt1), collide=False))
    n = 10
    xs = [-XC + i * 2 * XC / n for i in range(n + 1)]
    for i, x in enumerate(xs[1:-1], 1):
        P.append(box(f'truss_{k}_v{i}', 'Binder Pfosten', 'Fachwerk', 'steel', (x - 0.06, y - 0.06, zb1), (x + 0.06, y + 0.06, zt0),
                     skip=('-z', '+z'), collide=False, bev=0.0))
    for i in range(n):
        xa, xb = xs[i], xs[i + 1]
        a, b = ((xa, y, zt0), (xb, y, zb1)) if i < n // 2 else ((xa, y, zb1), (xb, y, zt0))
        P.append(beam(f'truss_{k}_d{i}', 'Binder Diagonale', 'Fachwerk', 'steel', a, b, 0.1, 0.1, bev=0.0, ends=False))
    for i, x in enumerate(xs[1:-1], 1):                          # Knotenbleche am Untergurt, beidseitig
        for sd, (ya, yb) in (('s', (y - 0.135, y - 0.12)), ('n', (y + 0.12, y + 0.135))):
            P.append(box(f'truss_{k}_g{i}{sd}', 'Knotenblech', 'Fachwerk', 'steel', (x - 0.22, ya, zb0 - 0.05), (x + 0.22, yb, zb1 + 0.3),
                         skip=('+z', '-z', '+y' if sd == 's' else '-y'), collide=False, bev=0.0))
for j, x in enumerate([-18.0 + 4.5 * i for i in range(9)]):
    P.append(box(f'purlin_{j}', 'Pfette', 'Fachwerk', 'steel', (x - 0.07, Y0 - 0.5, 13.78), (x + 0.07, Y1, H), skip=('+z',), collide=False))

# ------------------------------------------------------------------ Tor (Zone wand)
GY0, GY1, GH = Y0 - 0.5, Y0 + 0.5, 11.0
for s, (xa, xb) in (('w', (X0, -17.0)), ('e', (17.0, X1))):
    P.append(box(f'gate_post_{s}_low', 'Torpfosten unten (Warnanstrich)', 'Tor', 'hazard', (xa, GY0, 0), (xb, GY1, 2.0), skip=('+z',)))
    P.append(box(f'gate_post_{s}', 'Torpfosten', 'Tor', 'steel_dark', (xa, GY0, 2.0), (xb, GY1, GH), skip=('-z', '+z')))
    pts = [(x, z) for x in (xa + 0.35, xb - 0.35) for z in [2.4 + 0.5 * i for i in range(17)]]
    P += bolts(f'gate_post_{s}_bolt', 'Schraubenreihe Torpfosten', 'Tor', 'steel', 'y', 1, GY1, pts)
    P.append(box(f'gate_post_{s}_stop', 'Anschlagleiste', 'Tor', 'steel', ((xa + xb) / 2 - 0.08, GY1, 2.0), ((xa + xb) / 2 + 0.08, GY1 + 0.06, GH),
                 collide=False, bev=0.01))
    xi = -17.0 if s == 'w' else 17.0
    sg = 1 if s == 'w' else -1
    for i in range(3):     # Faltflügel, innen an die Pfosten geklappt
        xf = xi + sg * (0.12 + i * 0.22)
        P.append(box(f'gate_leaf_{s}{i}', 'Torflügel (gefaltet)', 'Tor', 'steel_light', (xf - 0.05, GY1 + 0.05, 0.05),
                     (xf + 0.05, GY1 + 3.8, GH - 0.25), bev=0.012))
    xf = xi + sg * (0.12 + 2 * 0.22 + 0.05)
    for m, z in enumerate((2.2, 5.4, 8.6)):
        P.append(box(f'gate_leaf_{s}_rib{m}', 'Flügel-Querriegel', 'Tor', 'steel_light', (min(xf, xf + sg * 0.04), GY1 + 0.1, z),
                     (max(xf, xf + sg * 0.04), GY1 + 3.75, z + 0.12), collide=False, bev=0.008))
    P.append(cyl(f'gate_leaf_{s}_lock', 'Verriegelungsstange', 'Tor', 'galv', 'z', (xf + sg * 0.03, GY1 + 3.5, 1.3), 0.018, 2.4, segs=8,
                 collide=False, bev=0.0))
P.append(box('gate_header', 'Torsturz', 'Tor', 'steel_dark', (X0, GY0, GH + 0.4), (X1, GY1, H + 0.5), skip=('+z', '-z')))
P.append(box('gate_header_band', 'Torsturz Warnband', 'Tor', 'hazard', (X0, GY0, GH), (X1, GY1, GH + 0.4), skip=('+z',)))
P.append(box('gate_track', 'Laufschiene Torflügel', 'Tor', 'steel', (-17.0, GY1, GH - 0.2), (17.0, GY1 + 0.25, GH), collide=False))
P.append(box('gate_rail', 'Bodenschiene Tor', 'Tor', 'steel_dark', (-17.0, -30.3, 0), (17.0, -30.1, 0.02), collide=False, bev=0.0))
for i, x in enumerate([-15.0 + 2.5 * k for k in range(13)]):
    if abs(x) < 5.4:
        continue
    P.append(box(f'gate_header_rib{i}', 'Sturz-Aussteifung', 'Tor', 'steel', (x - 0.06, GY1, GH + 0.45), (x + 0.06, GY1 + 0.12, H - 0.1),
                 collide=False, bev=0.01))
P += bolts('gate_header_bolt', 'Schraubenreihe Torsturz', 'Tor', 'steel', 'y', 1, GY1, [(-16.8 + 0.6 * i, GH + 0.62) for i in range(57)])
P.append(sign('hangar', 'Hallenname', 'Tor', (0.0, GY1 + 0.015, 12.8), (0, 1, 0), 9.4, 1.6, '#2B2E33',
              [_d(kind='frame', a=(0.1, 0.1), b=(9.3, 1.5), w=0.05, color='#E3E0D6'), txt('HANGAR 3', 0.95, 0.13, '#E3E0D6', 4.7, 0.32)],
              px_m=0.008))
for s, x in (('w', -17.6), ('e', 17.6)):      # Notleuchten an den Torpfosten
    P.append(box(f'gate_emerg_{s}', 'Notleuchte Gehäuse', 'Tor', 'steel_dark', (x - 0.16, GY1, 3.0), (x + 0.16, GY1 + 0.12, 3.12), collide=False,
                 bev=0.008))
    P.append(box(f'gate_emerg_{s}_lens', 'Notleuchte Linse', 'Tor', 'emerg_red', (x - 0.12, GY1 + 0.12, 3.02), (x + 0.12, GY1 + 0.15, 3.1),
                 collide=False, bev=0.0))
    EMERG.append(((x, GY1 + 0.3, 3.06), (0.0, 1.0, 0.0)))

# ------------------------------------------------------------------ Hallenstrahler (Zone fern)
LAMPS = []
LAMP_Z = 10.42
for k, y in enumerate(TRUSS_Y):
    for s, x in (('w', -8.0), ('e', 8.0)):
        G = 'Strahler'
        P.append(box(f'lamp_{k}_{s}_housing', 'Strahlergehäuse', G, 'steel_dark', (x - 0.56, y - 0.56, 10.47), (x + 0.56, y + 0.56, 10.62),
                     collide=False, bev=0.02))
        P.append(box(f'lamp_{k}_{s}_bezel', 'Blendrahmen', G, 'steel_dark', (x - 0.56, y - 0.56, 10.4), (x + 0.56, y + 0.56, 10.47),
                     skip=('+z', '-z'), collide=False, bev=0.0))
        P.append(box(f'lamp_{k}_{s}_panel', 'Leuchtfläche', G, 'lamp', (x - 0.5, y - 0.5, 10.43), (x + 0.5, y + 0.5, 10.45), skip=('+z',),
                     collide=False, bev=0.0))
        for m in range(6):
            yy = y - 0.4 + m * 0.16
            P.append(box(f'lamp_{k}_{s}_fin{m}', 'Kühlrippe', G, 'galv', (x - 0.48, yy - 0.008, 10.62), (x + 0.48, yy + 0.008, 10.7),
                         skip=('-z',), collide=False, bev=0.0))
        P.append(box(f'lamp_{k}_{s}_driver', 'Vorschaltgerät', G, 'galv', (x - 0.2, y - 0.1, 10.7), (x + 0.2, y + 0.1, 10.78), skip=('-z',),
                     collide=False, bev=0.008))
        for r, dx in (('a', -0.4), ('b', 0.4)):
            P.append(cyl(f'lamp_{k}_{s}_rod_{r}', 'Abhängung', G, 'steel', 'z', (x + dx, y, 10.94), 0.012, 0.48, segs=6, collide=False))
        P.append(beam(f'lamp_{k}_{s}_cable', 'Zuleitung', G, 'rubber', (x + 0.2, y, 10.78), (x + 0.3, y + 0.05, 11.2), 0.02, 0.02, bev=0.0))
        LAMPS.append((f'Strahler_{k + 1:02d}_{s.upper()}', (x, y, LAMP_Z)))

# ------------------------------------------------------------------ Hilfen für Ausstattung (Zone nah)


def crate(pid, x, y, z0, sx, sy, sz, mat, group='Kisten', detail=True, collide=True):
    """Transportkiste: Körper, Deckelband, Kufen, Kantenschutz, Griffe; Kollision als ein Quader."""
    e = 0.015
    out = [box(pid, 'Transportkiste', group, mat, (x - sx / 2, y - sy / 2, z0 + 0.06), (x + sx / 2, y + sy / 2, z0 + sz - 0.08),
               skip=('+z', '-z'), collide=False, bev=0.02),
           box(pid + '_lid', 'Kistendeckel', group, 'steel_dark', (x - sx / 2 - e, y - sy / 2 - e, z0 + sz - 0.08),
               (x + sx / 2 + e, y + sy / 2 + e, z0 + sz), skip=('-z',), collide=False, bev=0.012),
           box(pid + '_skid', 'Kistenkufen', group, 'steel_dark', (x - sx / 2 + 0.04, y - sy / 2 + 0.04, z0), (x + sx / 2 - 0.04, y + sy / 2 - 0.04,
               z0 + 0.06), skip=('+z', '-z'), collide=False, bev=0.0)]
    if detail:
        for m, (cx, cy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
            px, py = x + cx * sx / 2, y + cy * sy / 2
            out.append(box(f'{pid}_corner{m}', 'Kantenschutz', group, 'steel_dark', (px - 0.035 - 0.01 * (cx < 0), py - 0.035 - 0.01 * (cy < 0),
                           z0 + 0.06), (px + 0.035 + 0.01 * (cx > 0), py + 0.035 + 0.01 * (cy > 0), z0 + sz - 0.08),
                           skip=('+z', '-z', '-x' if cx > 0 else '+x', '-y' if cy > 0 else '+y'), collide=False, bev=0.006))
        if sz >= 0.7:
            zg = z0 + sz * 0.62
            if sx >= sy:
                for m, sd in enumerate((-1, 1)):
                    yy = y + sd * (sy / 2 + 0.02)
                    out.append(box(f'{pid}_grip{m}', 'Kistengriff', group, 'steel_dark', (x - 0.12, min(yy, y + sd * sy / 2), zg),
                                   (x + 0.12, max(yy, y + sd * sy / 2), zg + 0.04), skip=('-y' if sd > 0 else '+y',), collide=False, bev=0.0))
            else:
                for m, sd in enumerate((-1, 1)):
                    xx = x + sd * (sx / 2 + 0.02)
                    out.append(box(f'{pid}_grip{m}', 'Kistengriff', group, 'steel_dark', (min(xx, x + sd * sx / 2), y - 0.12, zg),
                                   (max(xx, x + sd * sx / 2), y + 0.12, zg + 0.04), skip=('-x' if sd > 0 else '+x',), collide=False, bev=0.0))
    if collide:
        out.append(solid(pid + '_col', 'Kiste (Kollision)', (x - sx / 2 - e, y - sy / 2 - e, z0), (x + sx / 2 + e, y + sy / 2 + e, z0 + sz)))
    return out


def pallet(pid, x, y, z0=0.0, sx=1.2, sy=1.0, group='Kisten', simple=False):
    if simple:
        return [box(pid, 'Palette', group, 'wood', (x - sx / 2, y - sy / 2, z0), (x + sx / 2, y + sy / 2, z0 + 0.14), skip=('-z',), collide=False,
                    bev=0.008)]
    out = [box(f'{pid}_r{m}', 'Palettenkufe', group, 'wood', (x - sx / 2, y + o - 0.05, z0), (x + sx / 2, y + o + 0.05, z0 + 0.12),
               skip=('-z',), collide=False, bev=0.008) for m, o in enumerate((-sy / 2 + 0.05, 0.0, sy / 2 - 0.05))]
    for m in range(5):
        xx = x - sx / 2 + 0.07 + m * (sx - 0.14) / 4
        out.append(box(f'{pid}_b{m}', 'Palettenbrett', group, 'wood', (xx - 0.07, y - sy / 2, z0 + 0.12), (xx + 0.07, y + sy / 2, z0 + 0.145),
                       skip=('-z',), collide=False, bev=0.0))
    out.append(solid(pid + '_col', 'Palette (Kollision)', (x - sx / 2, y - sy / 2, z0), (x + sx / 2, y + sy / 2, z0 + 0.145)))
    return out


def barrel(pid, x, y, z0, mat, group='Faesser'):
    out = [cyl(pid, 'Fass 200 l', group, mat, 'z', (x, y, z0 + 0.44), 0.29, 0.88, segs=20, caps='top'),
           cyl(pid + '_rim', 'Fassdeckel', group, 'steel_dark', 'z', (x, y, z0 + 0.885), 0.27, 0.012, segs=20, collide=False, caps='top'),
           cyl(pid + '_bung', 'Spundloch', group, 'steel_dark', 'z', (x + 0.15, y, z0 + 0.9), 0.03, 0.02, segs=8, collide=False, caps='top')]
    for m, zz in enumerate((0.29, 0.59)):
        out.append(cyl(f'{pid}_hoop{m}', 'Rollreifen', group, mat, 'z', (x, y, z0 + zz), 0.3, 0.025, segs=20, collide=False, caps='none'))
    return out


def barrier(pid, x, y0, y1, group='Parcours'):
    """Absperrgitter entlang y bei x (1,1 m): Rahmen, Stäbe, Füße; Kollision als dünner Quader."""
    out = []
    n = max(1, round((y1 - y0) / 2.5))
    L = (y1 - y0) / n
    for k in range(n):
        a, b = y0 + k * L + 0.03, y0 + (k + 1) * L - 0.03
        q = f'{pid}_{k}'
        for m, yy in enumerate((a, b - 0.04)):
            out.append(box(f'{q}_post{m}', 'Gitterpfosten', group, 'galv', (x - 0.02, yy, 0.06), (x + 0.02, yy + 0.04, 1.1), collide=False,
                           bev=0.0))
        out.append(box(f'{q}_top', 'Gitter Oberholm', group, 'galv', (x - 0.02, a, 1.06), (x + 0.02, b, 1.1), collide=False, bev=0.0))
        out.append(box(f'{q}_bot', 'Gitter Unterholm', group, 'galv', (x - 0.02, a, 0.1), (x + 0.02, b, 0.14), collide=False, bev=0.0))
        nb = int((b - a) / 0.32)
        for m in range(1, nb):
            yy = a + (b - a) * m / nb
            out.append(box(f'{q}_bar{m}', 'Gitterstab', group, 'galv', (x - 0.008, yy - 0.008, 0.14), (x + 0.008, yy + 0.008, 1.06),
                           collide=False, bev=0.0))
        for m, yy in enumerate((a + 0.02, b - 0.02)):
            out.append(box(f'{q}_foot{m}', 'Gitterfuß', group, 'hazard', (x - 0.3, yy - 0.03, 0), (x + 0.3, yy + 0.03, 0.06), collide=False,
                           bev=0.0))
    out.append(solid(pid + '_col', 'Absperrgitter (Kollision)', (x - 0.025, y0, 0.0), (x + 0.025, y1, 1.1), surface='metal'))
    return out


def railing(pid, group, a, b, z0, open_=None):
    """Geländer auf Höhe z0 entlang einer achsparallelen Linie a→b (Draufsicht): Pfosten ≤ 1,5 m, Handlauf 1,0 m, Knieleiste,
    Fußleiste (Warnanstrich); Kollision als ein dünner Quader bis Handlaufhöhe."""
    out = []
    (xa, ya), (xb, yb) = a, b
    alongx = abs(yb - ya) < 1e-6
    L = abs(xb - xa) if alongx else abs(yb - ya)
    n = max(1, math.ceil(L / 1.5))
    t = 0.05

    def seg(q, de, mat, z_lo, z_hi, thick):
        if alongx:
            return box(q, de, group, mat, (min(xa, xb), ya - thick / 2, z_lo), (max(xa, xb), ya + thick / 2, z_hi), collide=False, bev=0.0)
        return box(q, de, group, mat, (xa - thick / 2, min(ya, yb), z_lo), (xa + thick / 2, max(ya, yb), z_hi), collide=False, bev=0.0)
    out.append(seg(pid + '_top', 'Handlauf', 'accent', z0 + 0.95, z0 + 1.0, t))
    out.append(seg(pid + '_mid', 'Knieleiste', 'accent', z0 + 0.48, z0 + 0.52, 0.035))
    out.append(seg(pid + '_toe', 'Fußleiste', 'hazard', z0, z0 + 0.15, 0.02))
    for k in range(n + 1):
        f = k / n
        px, py = xa + (xb - xa) * f, ya + (yb - ya) * f
        out.append(cyl(f'{pid}_post{k}', 'Geländerpfosten', group, 'accent', 'z', (px, py, z0 + 0.5), 0.022, 1.0, segs=8, collide=False,
                       bev=0.0))
    if alongx:
        out.append(solid(pid + '_col', 'Geländer (Kollision)', (min(xa, xb), ya - 0.03, z0), (max(xa, xb), ya + 0.03, z0 + 1.0), surface='metal'))
    else:
        out.append(solid(pid + '_col', 'Geländer (Kollision)', (xa - 0.03, min(ya, yb), z0), (xa + 0.03, max(ya, yb), z0 + 1.0), surface='metal'))
    return out


def deck(pid, group, x0, x1, y0, y1, z, posts):
    """Bühne/Laufsteg: Gitterrost auf Randträgern, Stützen (Hohlprofil) mit Fußplatten."""
    out = [box(pid, 'Gitterrost', group, 'grating', (x0, y0, z - 0.05), (x1, y1, z), skip=('-z',), bev=0.006),
           box(pid + '_edge', 'Randträger', group, 'steel', (x0, y0, z - 0.25), (x1, y1, z - 0.05), skip=('+z',), collide=False, bev=0.01)]
    for k, (px, py) in enumerate(posts):
        out.append(box(f'{pid}_post{k}', 'Stütze', group, 'steel', (px - 0.06, py - 0.06, 0.02), (px + 0.06, py + 0.06, z - 0.25), skip=('+z',)))
        out.append(box(f'{pid}_post{k}_foot', 'Fußplatte', group, 'steel_dark', (px - 0.12, py - 0.12, 0), (px + 0.12, py + 0.12, 0.02),
                       collide=False, bev=0.0))
    return out


def stand(pid, pos, nrm, r, group='Parcours', mount='floor'):
    """Zielständer: Rückplatte hinter der Scheibe (Unity baut die Scheibe an `pos`), bei mount='floor' Pfosten und Fuß."""
    out = []
    back = tuple(pos[k] - nrm[k] * 0.05 for k in range(3))
    a = tuple(back[k] - nrm[k] * 0.012 for k in range(3))
    b = tuple(back[k] + nrm[k] * 0.012 for k in range(3))
    out.append(beam(pid + '_plate', 'Zielrückplatte', group, 'steel_dark', a, b, 2.4 * r, 2.4 * r, bev=0.0))
    if mount == 'floor':
        zt = back[2] - 1.2 * r * max(0.3, math.sqrt(1 - nrm[2] ** 2))
        out.append(cyl(pid + '_post', 'Zielständer', group, 'steel_dark', 'z', (back[0], back[1], zt / 2), 0.03, zt, segs=8, collide=False,
                       bev=0.0))
        out.append(box(pid + '_foot', 'Ständerfuß', group, 'hazard', (back[0] - 0.25, back[1] - 0.25, 0), (back[0] + 0.25, back[1] + 0.25, 0.04),
                       collide=False, bev=0.0))
    return out


# ------------------------------------------------------------------ Parcours (Zone nah)
LANE = 3.5
# Start- und Zielportal
for nm, (y, xa, xb, word) in (('start', (Y_START, -LANE - 0.15, LANE + 0.15, 'START')), ('finish', (Y_FINISH, 8.45, 14.55, 'ZIEL'))):
    for m, x in enumerate((xa, xb)):
        P.append(box(f'portal_{nm}_post{m}', 'Portalpfosten', 'Parcours', 'hazard', (x - 0.12, y - 0.12, 0), (x + 0.12, y + 0.12, 3.2)))
        P.append(box(f'portal_{nm}_post{m}_foot', 'Portalfuß', 'Parcours', 'steel_dark', (x - 0.25, y - 0.25, 0), (x + 0.25, y + 0.25, 0.04),
                     collide=False, bev=0.0))
    P.append(box(f'portal_{nm}_beam', 'Portalriegel', 'Parcours', 'steel_dark', (xa - 0.12, y - 0.1, 3.0), (xb + 0.12, y + 0.1, 3.25),
                 collide=False))
    P.append(sign(f'portal_{nm}', f'Portal {word}', 'Parcours', ((xa + xb) / 2, y + 0.101, 3.6), (0, 1, 0), 2.6, 0.6, '#1D1E21',
                  [_d(kind='checker', a=(0.04, 0.04), b=(0.34, 0.56), cell=0.1, c1='#E8E5DC', c2='#1D1E21'),
                   _d(kind='checker', a=(2.26, 0.04), b=(2.56, 0.56), cell=0.1, c1='#E8E5DC', c2='#1D1E21'),
                   txt(word, 0.32, 0.14, '#E8E5DC', 1.3, 0.14)], px_m=0.005))
    P.append(sign(f'portal_{nm}_b', f'Portal {word} Rückseite', 'Parcours', ((xa + xb) / 2, y - 0.101, 3.6), (0, -1, 0), 2.6, 0.6, '#1D1E21',
                  [txt(word, 0.32, 0.14, '#E8E5DC', 1.3, 0.14)], px_m=0.005))
    P.append(box(f'portal_{nm}_hang', 'Schildträger', 'Parcours', 'steel_dark', ((xa + xb) / 2 - 1.3, y - 0.1, 3.25), ((xa + xb) / 2 + 1.3, y + 0.1, 3.3),
                 collide=False, bev=0.0))
# Absperrgitter der Slalom- und Sprunggasse (x = ±3,5, y 20,5 … −3,5)
P += barrier('barrier_w', -LANE, -3.5, 20.5)
P += barrier('barrier_e', LANE, -3.5, 20.5)
# Slalom: vier Kistenhindernisse, abwechselnd an der West- und Ostseite (Gasse 2,5 m), nicht überspringbar (≥ 1,2 m)
SLALOM = [(17.6, -1), (13.8, 1), (10.0, -1), (6.2, 1)]
for i, (y, sd) in enumerate(SLALOM):
    xa, xb = (-LANE + 0.05, 0.7) if sd < 0 else (-0.7, LANE - 0.05)
    xm = (xa + xb) / 2
    w1 = (xb - xa) * 0.55
    mats = ('crate_olive', 'crate_grey', 'crate_cream', 'crate_olive')
    P += crate(f'slalom_{i}a', xa + w1 / 2, y, 0, w1 - 0.02, 1.2, 1.2, mats[i], group='Parcours')
    P += crate(f'slalom_{i}b', xa + w1 + (xb - xa - w1) / 2, y, 0, xb - xa - w1 - 0.02, 1.2, 1.3, mats[(i + 1) % 4], group='Parcours')
    P += crate(f'slalom_{i}c', xa + w1 / 2 + (0.3 if sd < 0 else -0.3), y, 1.2, 1.2, 1.0, 0.8, mats[(i + 2) % 4], group='Parcours')
    P.append(box(f'slalom_{i}_tape', 'Warnband', 'Parcours', 'hazard', (xa, y - 0.62, 1.0), (xb, y - 0.6, 1.12), collide=False, bev=0.0))
# Mauer 0,6 m (Überspringen) und Kistenberg 0,6/1,2 m
WALL1 = (2.6, 2.95)
P.append(box('wall_low', 'Mauer 0,6 m', 'Parcours', 'concrete_wall', (-LANE + 0.03, WALL1[0], 0), (LANE - 0.03, WALL1[1], 0.55)))
P.append(box('wall_low_cap', 'Mauerabdeckung', 'Parcours', 'hazard', (-LANE + 0.03, WALL1[0] - 0.02, 0.55), (LANE - 0.03, WALL1[1] + 0.02, 0.6),
             bev=0.008))
for i, x in enumerate((-2.3, 0.0, 2.3)):
    P += crate(f'step_a{i}', x, 0.6, 0, 2.28 if i != 1 else 2.3, 1.2, 0.6, ('crate_grey', 'crate_olive', 'crate_cream')[i], group='Parcours',
               detail=False)
    P += crate(f'step_b{i}', x, -0.6, 0, 2.28 if i != 1 else 2.3, 1.2, 1.2, ('crate_olive', 'crate_cream', 'crate_grey')[i], group='Parcours')
P.append(sign('cp2', 'Kontrollpunkt 2', 'Parcours', (1.2, 0.03, 0.92), (0, 1, 0), 0.4, 0.4, '#1D1E21',
              [_d(kind='ring', c=(0.2, 0.2), r=0.17, w=0.025, color='#E8E5DC'), txt('2', 0.2, 0.14, '#E8E5DC', 0.2, 0.1)], px_m=0.003))
# Containergasse mit Rohrbrücke (Ducken 1,35 m)
CX0, CX1 = -16.9, -14.46


def container(pid, y0, y1, mat, door_end):
    """20-Fuß-Seecontainer (6,06 × 2,44 × 2,59 m): Eckpfosten, Rahmen, Wände als Trapezblech, Türseite mit Verriegelung."""
    G = 'Ducken'
    out = [solid(pid + '_col', 'Container (Kollision)', (CX0, y0, 0), (CX1, y1, 2.59), surface='metal')]
    for m, (x, y) in enumerate(((CX0, y0), (CX1 - 0.15, y0), (CX0, y1 - 0.15), (CX1 - 0.15, y1 - 0.15))):
        out.append(box(f'{pid}_cp{m}', 'Eckpfosten', G, mat, (x, y, 0), (x + 0.15, y + 0.15, 2.59), collide=False, bev=0.01))
        for zc in (0.0, 2.47):
            out.append(box(f'{pid}_cc{m}{int(zc)}', 'Eckbeschlag', G, 'steel_dark', (x - 0.005, y - 0.005, zc), (x + 0.155, y + 0.155, zc + 0.12),
                           collide=False, bev=0.006))
    for nm, (z0, z1) in (('bot', (0.0, 0.15)), ('top', (2.44, 2.59))):
        out.append(box(f'{pid}_rail_w_{nm}', 'Längsträger', G, mat, (CX0, y0 + 0.15, z0), (CX0 + 0.1, y1 - 0.15, z1), collide=False, bev=0.008))
        out.append(box(f'{pid}_rail_e_{nm}', 'Längsträger', G, mat, (CX1 - 0.1, y0 + 0.15, z0), (CX1, y1 - 0.15, z1), collide=False, bev=0.008))
        for yy, sd in ((y0, 0), (y1 - 0.1, 1)):
            out.append(box(f'{pid}_rail_{sd}_{nm}', 'Querträger', G, mat, (CX0 + 0.15, yy, z0), (CX1 - 0.15, yy + 0.1, z1), collide=False,
                           bev=0.008))
    out.append(corr(pid + '_side_w', 'Containerwand', G, mat, 'x', -1, CX0 + 0.02, 'y', y0 + 0.15, y1 - 0.15, 0.15, 2.44, PROF_C,
                    collide=False))
    out.append(corr(pid + '_side_e', 'Containerwand', G, mat, 'x', 1, CX1 - 0.02, 'y', y0 + 0.15, y1 - 0.15, 0.15, 2.44, PROF_C,
                    collide=False))
    out.append(box(pid + '_roof', 'Containerdach', G, mat, (CX0 + 0.1, y0 + 0.1, 2.5), (CX1 - 0.1, y1 - 0.1, 2.56), skip=('-z',), collide=False,
                   bev=0.0))
    for yy, sd, kind in ((y0, -1, 'door' if door_end < 0 else 'end'), (y1, 1, 'door' if door_end > 0 else 'end')):
        at = yy + sd * 0.0
        if kind == 'end':
            out.append(corr(f'{pid}_end_{sd}', 'Stirnwand', G, mat, 'y', sd, at - sd * 0.02, 'x', CX0 + 0.15, CX1 - 0.15, 0.15, 2.44, PROF_C,
                            collide=False))
            continue
        for m, (xa, xb) in enumerate(((CX0 + 0.15, (CX0 + CX1) / 2 - 0.005), ((CX0 + CX1) / 2 + 0.005, CX1 - 0.15))):
            out.append(box(f'{pid}_door{m}', 'Containertür', G, mat, (xa, min(at, at - sd * 0.04), 0.15), (xb, max(at, at - sd * 0.04), 2.44),
                           collide=False, bev=0.006))
            for q in range(2):
                xr = xa + (xb - xa) * (0.28 + 0.44 * q)
                out.append(cyl(f'{pid}_door{m}_bar{q}', 'Verriegelungsstange', G, 'galv', 'z', (xr, at + sd * 0.03, 1.3), 0.017, 2.2, segs=8,
                               collide=False, bev=0.0))
                out.append(box(f'{pid}_door{m}_lever{q}', 'Verschlusshebel', G, 'galv', (xr - 0.02, min(at, at + sd * 0.06), 0.95),
                               (xr + 0.02, max(at, at + sd * 0.06), 1.2), collide=False, bev=0.0))
    return out


P += container('cont_a', -24.0, -17.94, 'container_teal', door_end=-1)
P += container('cont_b', -16.0, -9.94, 'container_rust', door_end=1)
for nm, y0, txt_ in (('code_a', -24.0, 'BLNU 300512 2'), ('code_b', -16.0, 'HGRU 418806 5')):
    DECALS[nm] = dict(origin=(CX0 + 0.004, y0 + 4.2, 1.9), u=(0, -1, 0), v=(0, 0, 1), size=(3.6, 0.5), px_m=0.006, depth=0.06,
                      items=[txt(txt_, 0.22, 0.13, '#E8E5DC', 0.0, 0.14, 'left'), txt('22G1  MAX 30480 KG', 0.1, 0.13, '#E8E5DC', 0.0, 0.0, 'left')])
# Rohrbrücke: drei Rohre aus der Westwand über die Gasse (Unterkante 1,35 m), Steigleitungen östlich der Container
PZ = 1.35
PIPES = [(-17.45, 0.15, 'steel_light'), (-17.0, 0.17, 'pipe_green'), (-16.55, 0.15, 'steel_light')]
for i, (y, r, mat) in enumerate(PIPES):
    xa, xb = -19.97, -13.2
    P.append(cyl(f'pipe_{i}', 'Rohrleitung', 'Ducken', mat, 'x', ((xa + xb) / 2, y, PZ + r), r, xb - xa, segs=16))
    P.append(cyl(f'pipe_{i}_riser', 'Steigleitung', 'Ducken', mat, 'z', (xb, y, (PZ + H) / 2), r, H - PZ, segs=16))
    P.append(cyl(f'pipe_{i}_sleeve', 'Wanddurchführung', 'Ducken', 'steel_dark', 'x', (-19.92, y, PZ + r), r + 0.05, 0.1, segs=16, collide=False))
    for m, x in enumerate((-17.0, -15.2, -14.0)):
        P.append(cyl(f'pipe_{i}_flange{m}', 'Flansch', 'Ducken', 'steel_dark', 'x', (x, y, PZ + r), r + 0.03, 0.05, segs=16, collide=False,
                     bev=0.0))
    P.append(cyl(f'pipe_{i}_elbow', 'Rohrbogen', 'Ducken', mat, 'z', (xb, y, PZ + r), r + 0.012, 2 * r + 0.02, segs=16, collide=False, bev=0.0))
P.append(cyl('pipe_hazard', 'Warnmanschette', 'Ducken', 'hazard', 'x', (-18.0, -16.55, PZ + 0.15), 0.156, 2.3, segs=16, collide=False, bev=0.0))
for j, x in enumerate((-19.2, -15.68, -13.8)):
    for s, y in (('s', -17.82), ('n', -16.12)):
        P.append(box(f'pipe_post_{j}{s}', 'Rohrstütze', 'Ducken', 'steel', (x - 0.06, y - 0.06, 0), (x + 0.06, y + 0.06, PZ - 0.12)))
    P.append(box(f'pipe_beam_{j}', 'Rohrjoch', 'Ducken', 'accent', (x - 0.06, -17.9, PZ - 0.12), (x + 0.06, -16.04, PZ), collide=False))
P.append(sign('duck', 'Kopfhöhe 1,35 m', 'Ducken', (-18.0, -16.38, 1.64), (0, 1, 0), 0.9, 0.55, '#E8C21E',
              [_d(kind='frame', a=(0.02, 0.02), b=(0.88, 0.53), w=0.025, color='#1D1E21'), txt('KOPFHÖHE', 0.12, 0.14, '#1D1E21', 0.45, 0.31),
               txt('1,35 M', 0.12, 0.14, '#1D1E21', 0.45, 0.1)], px_m=0.003))
# Leitwand am Tor (0,6 m) mit Kistenstapel nördlich
P.append(box('wall_gate', 'Leitwand 0,6 m', 'Parcours', 'concrete_wall', (-4.175, -28.4, 0), (-3.825, -23.4, 0.55)))
P.append(box('wall_gate_cap', 'Leitwand Abdeckung', 'Parcours', 'hazard', (-4.195, -28.4, 0.55), (-3.805, -23.4, 0.6), bev=0.008))
P += crate('gate_stack_1', -4.0, -22.6, 0, 1.2, 1.6, 1.2, 'crate_grey', group='Parcours')
P += crate('gate_stack_2', -4.0, -22.6, 1.2, 1.2, 1.2, 0.9, 'crate_olive', group='Parcours')
# Gerüst: Treppe (12 × 0,25 m) → Bühne P1 (3 m) → Laufsteg 20,4 m → Bühne P2 → Absprungkiste
GZ = 3.0
SX0, SX1, SY = 9.0, 10.2, -24.9
NS, RISE, RUN = 12, GZ / 12, 0.3
for k in range(1, NS):
    y0 = SY + (k - 1) * RUN
    P.append(box(f'stair_step_{k:02d}', 'Treppenstufe', 'Geruest', 'grating', (SX0 + 0.05, y0, k * RISE - 0.05), (SX1 - 0.05, y0 + RUN, k * RISE),
                 bev=0.006))
    P.append(box(f'stair_step_{k:02d}_nose', 'Trittkante', 'Geruest', 'hazard', (SX0 + 0.05, y0, k * RISE - 0.05), (SX1 - 0.05, y0 + 0.04, k * RISE + 0.003),
                 collide=False, bev=0.0))
Y_P1 = SY + (NS - 1) * RUN                         # −21,6
for s, x in (('w', SX0 + 0.025), ('e', SX1 - 0.025)):
    P.append(beam(f'stair_stringer_{s}', 'Treppenwange', 'Geruest', 'steel', (x, SY - 0.1, 0.02), (x, Y_P1, GZ - 0.05), 0.05, 0.25))
    P.append(beam(f'stair_rail_{s}', 'Treppenhandlauf', 'Geruest', 'accent', (x, SY, 1.0), (x, Y_P1, GZ + 1.0), 0.05, 0.05, bev=0.0))
    P.append(beam(f'stair_mid_{s}', 'Treppenknieleiste', 'Geruest', 'accent', (x, SY, 0.5), (x, Y_P1, GZ + 0.5), 0.035, 0.035, bev=0.0))
    P.append(cyl(f'stair_post_{s}', 'Treppenpfosten', 'Geruest', 'accent', 'z', (x, SY + 0.05, 0.5), 0.022, 1.0, segs=8, collide=False, bev=0.0))
    P.append(solid(f'stair_rail_{s}_col', 'Treppengeländer (Kollision)', (x - 0.03, SY, 0.0), (x + 0.03, Y_P1, GZ + 1.0), surface='metal'))
P1 = (9.0, 13.0, Y_P1, -18.4)
P += deck('p1', 'Geruest', P1[0], P1[1], P1[2], P1[3], GZ, [(9.06, P1[2] + 0.06), (12.94, P1[2] + 0.06), (9.06, P1[3] - 0.06), (12.94, P1[3] - 0.06)])
CW = (11.4, 12.6, -18.4, 2.0)
P += deck('walk', 'Geruest', CW[0], CW[1], CW[2], CW[3], GZ, [(x, y) for y in (-15.0, -11.6, -8.2, -4.8, -1.4) for x in (11.46, 12.54)])
for i, (ya, yb) in enumerate(((-15.0, -11.6), (-8.2, -4.8), (-1.4, 2.0))):
    for s, x in (('w', 11.46), ('e', 12.54)):
        P.append(beam(f'walk_brace_{i}{s}', 'Verband', 'Geruest', 'steel', (x, ya + 0.06, 0.2), (x, yb - 0.06, GZ - 0.3), 0.05, 0.05, bev=0.0))
P2 = (10.0, 14.0, 2.0, 5.0)
P += deck('p2', 'Geruest', P2[0], P2[1], P2[2], P2[3], GZ, [(10.06, 2.06), (13.94, 2.06), (10.06, 4.94), (13.94, 4.94)])
RAILS = [('p1_s', (10.2, P1[2]), (13.0, P1[2])), ('p1_w', (9.0, P1[2]), (9.0, P1[3])), ('p1_e', (13.0, P1[2]), (13.0, P1[3])),
         ('p1_nw', (9.0, P1[3]), (CW[0], P1[3])), ('p1_ne', (CW[1], P1[3]), (13.0, P1[3])),
         ('walk_w', (CW[0], CW[2]), (CW[0], CW[3])), ('walk_e', (CW[1], CW[2]), (CW[1], CW[3])),
         ('p2_sw', (P2[0], P2[2]), (CW[0], P2[2])), ('p2_se', (CW[1], P2[2]), (P2[1], P2[2])), ('p2_w', (P2[0], P2[2]), (P2[0], P2[3])),
         ('p2_e', (P2[1], P2[2]), (P2[1], P2[3])), ('p2_nw', (P2[0], P2[3]), (CW[0], P2[3])), ('p2_ne', (CW[1], P2[3]), (P2[1], P2[3]))]
for nm, a, b in RAILS:
    P += railing(f'rail_{nm}', 'Geruest', a, b, GZ)
P.append(sign('cp4', 'Kontrollpunkt 4', 'Geruest', (12.965, -20.0, GZ + 0.75), (-1, 0, 0), 0.4, 0.4, '#1D1E21',
              [_d(kind='ring', c=(0.2, 0.2), r=0.17, w=0.025, color='#E8E5DC'), txt('4', 0.2, 0.14, '#E8E5DC', 0.2, 0.1)], px_m=0.003))
P.append(sign('cp5', 'Kontrollpunkt 5', 'Geruest', (13.965, 3.5, GZ + 0.75), (-1, 0, 0), 0.4, 0.4, '#1D1E21',
              [_d(kind='ring', c=(0.2, 0.2), r=0.17, w=0.025, color='#E8E5DC'), txt('5', 0.2, 0.14, '#E8E5DC', 0.2, 0.1)], px_m=0.003))
P += crate('drop_1', 12.0, 5.7, 0, 2.0, 1.2, 1.0, 'crate_olive', group='Parcours')
P += crate('drop_2', 12.0, 5.7, 1.0, 2.0, 1.2, 0.6, 'crate_cream', group='Parcours')
# Kistenburg östlich des Laufstegs (Ziele nur von oben sichtbar)
FX0, FX1, FY0, FY1, FH = 13.4, 18.4, -13.0, -5.0, 1.0
for lvl in range(2):
    z = lvl * FH
    mats = ('crate_grey', 'crate_olive') if lvl == 0 else ('crate_olive', 'crate_cream')
    for m, (xa, xb) in enumerate(((FX0, 15.9), (15.9, FX1))):
        P += crate(f'fort_s{lvl}{m}', (xa + xb) / 2, FY0 + 0.6, z, xb - xa - 0.02, 1.2, FH, mats[m], group='Parcours', detail=lvl == 1)
        P += crate(f'fort_n{lvl}{m}', (xa + xb) / 2, FY1 - 0.6, z, xb - xa - 0.02, 1.2, FH, mats[1 - m], group='Parcours', detail=lvl == 1)
    for m, (ya, yb) in enumerate(((FY0 + 1.2, -9.0), (-9.0, FY1 - 1.2))):
        P += crate(f'fort_w{lvl}{m}', FX0 + 0.6, (ya + yb) / 2, z, 1.2, yb - ya - 0.02, FH, mats[m], group='Parcours', detail=lvl == 1)
        P += crate(f'fort_e{lvl}{m}', FX1 - 0.6, (ya + yb) / 2, z, 1.2, yb - ya - 0.02, FH, mats[1 - m], group='Parcours', detail=lvl == 1)
P += pallet('fort_pal', 16.4, -9.3, sx=1.2, sy=1.0, group='Parcours')
for i, (dx, dy) in enumerate(((-0.3, -0.25), (0.3, 0.25))):
    P += barrel(f'fort_barrel{i}', 16.4 + dx, -9.3 + dy, 0.145, 'barrel_blue', group='Parcours')
# Deckungskiste für Ziel T02 (östlich der Slalomgasse)
P += crate('cover_t02', 5.55, 11.0, 0, 0.7, 1.2, 1.0, 'crate_grey', group='Parcours')

# ------------------------------------------------------------------ Ausstattung (Zone nah): Regal, Büro, Aggregat, Kisten, Fässer
RX0, RX1, RY0, BAY, NBAY = 17.9, 19.1, 12.0, 2.7, 6
LEVELS = (1.8, 3.6, 5.4)
for i in range(NBAY + 1):
    y = RY0 + i * BAY
    for s, x in (('f', RX0), ('b', RX1 - 0.1)):
        P.append(box(f'rack_up_{i}{s}', 'Regalstütze', 'Regal', 'galv', (x, y - 0.05, 0), (x + 0.1, y + 0.05, 6.2), bev=0.006))
        P.append(box(f'rack_up_{i}{s}_foot', 'Stützenfuß', 'Regal', 'steel_dark', (x - 0.02, y - 0.08, 0), (x + 0.12, y + 0.08, 0.015),
                     collide=False, bev=0.0))
    P.append(box(f'rack_guard_{i}', 'Anfahrschutz', 'Regal', 'hazard', (RX0 - 0.12, y - 0.1, 0), (RX0 - 0.02, y + 0.1, 0.4), bev=0.008))
    for m in range(3):
        za = 0.3 + m * 2.0
        P.append(beam(f'rack_diag_{i}{m}', 'Rahmenstrebe', 'Regal', 'galv', (RX0 + 0.1, y, za), (RX1 - 0.1, y, za + 1.6), 0.03, 0.03, bev=0.0))
for li, z in enumerate(LEVELS):
    for s, x in (('f', RX0), ('b', RX1 - 0.1)):
        P.append(box(f'rack_beam_{li}{s}', 'Regalträger', 'Regal', 'accent', (x - 0.01, RY0, z), (x + 0.11, RY0 + NBAY * BAY, z + 0.15)))
    P.append(box(f'rack_deck_{li}', 'Regalboden', 'Regal', 'grating', (RX0 + 0.1, RY0, z + 0.12), (RX1 - 0.1, RY0 + NBAY * BAY, z + 0.15)))
MATS = ('crate_olive', 'crate_grey', 'crate_cream', 'crate_grey', 'crate_olive')
HS = (1.1, 0.8, 1.3, 0.9, 1.2, 0.7, 1.0)
for b in range(NBAY):
    for li, z in enumerate((0.0,) + tuple(z + 0.15 for z in LEVELS)):
        for j in range(2):
            n = b * 8 + li * 2 + j
            if n % 7 == 5:
                continue
            y = RY0 + b * BAY + 0.7 + j * 1.3
            P += pallet(f'rack_pal_{b}_{li}_{j}', 18.5, y, z, sx=1.0, sy=1.15, group='Regal', simple=True)
            P += crate(f'rack_crate_{b}_{li}_{j}', 18.5, y, z + 0.14, 0.95, 1.1, min(HS[n % 7], 1.45 if li < 3 else 1.3), MATS[n % 5],
                       group='Regal', detail=li == 0)
# Bürocontainer (Leitstand) Nordwestecke
OX0, OX1, OY0, OY1, OZ = -19.3, -13.3, 26.8, 29.6, 2.9
G = 'Buero'
P.append(box('office', 'Bürocontainer', G, 'steel_light', (OX0 + 0.06, OY0 + 0.06, 0.12), (OX1 - 0.06, OY1 - 0.06, OZ - 0.12), collide=False, bev=0.0))
P.append(solid('office_col', 'Bürocontainer (Kollision)', (OX0, OY0, 0), (OX1, OY1, OZ), surface='metal'))
for m, (x, y) in enumerate(((OX0, OY0), (OX1 - 0.14, OY0), (OX0, OY1 - 0.14), (OX1 - 0.14, OY1 - 0.14))):
    P.append(box(f'office_post{m}', 'Eckpfosten', G, 'steel_dark', (x, y, 0), (x + 0.14, y + 0.14, OZ), collide=False, bev=0.01))
for nm, (z0, z1) in (('bot', (0.0, 0.14)), ('top', (OZ - 0.14, OZ))):
    P.append(box(f'office_frame_s_{nm}', 'Rahmen', G, 'steel_dark', (OX0 + 0.14, OY0, z0), (OX1 - 0.14, OY0 + 0.1, z1), collide=False, bev=0.008))
    P.append(box(f'office_frame_e_{nm}', 'Rahmen', G, 'steel_dark', (OX1 - 0.1, OY0 + 0.14, z0), (OX1, OY1 - 0.14, z1), collide=False, bev=0.008))
P.append(box('office_roof', 'Containerdach', G, 'steel_dark', (OX0 - 0.03, OY0 - 0.03, OZ), (OX1 + 0.03, OY1 + 0.03, OZ + 0.08), collide=False, bev=0.01))
for nm, (a, b) in (('e', ((OX1 - 0.02, 27.3, 1.0), (OX1 + 0.005, 29.1, 2.2))), ('s1', ((-18.8, OY0 - 0.005, 1.0), (-17.2, OY0 + 0.02, 2.2))),
                   ('s2', ((-17.0, OY0 - 0.005, 1.0), (-16.2, OY0 + 0.02, 2.2)))):
    P.append(box(f'office_window_{nm}', 'Fenster', G, 'glass_dark', a, b, collide=False, bev=0.0))
    ax = 0 if nm == 'e' else 1
    fa, fb = list(a), list(b)
    fa[ax] -= 0.03 if ax == 1 else 0.0
    fb[ax] += 0.0 if ax == 1 else 0.03
    for q, (d0, d1) in enumerate(((a[2] - 0.06, a[2]), (b[2], b[2] + 0.06))):
        lo, hi = list(fa), list(fb)
        lo[2], hi[2] = d0, d1
        lo[ax] = min(fa[ax], fb[ax]) - (0.03 if ax == 1 else 0.0)
        hi[ax] = max(fa[ax], fb[ax]) + (0.03 if ax == 0 else 0.0)
        P.append(box(f'office_window_{nm}_f{q}', 'Fensterrahmen', G, 'galv', lo, hi, collide=False, bev=0.0))
P.append(box('office_door', 'Containertür', G, 'steel_dark', (-15.8, OY0 - 0.03, 0.14), (-14.8, OY0 + 0.02, 2.14), collide=False, bev=0.006))
P.append(box('office_door_handle', 'Türdrücker', G, 'galv', (-15.0, OY0 - 0.07, 1.02), (-14.88, OY0 - 0.03, 1.06), collide=False, bev=0.0))
P.append(box('office_step', 'Trittstufe', G, 'grating', (-16.0, 26.3, 0), (-14.6, OY0, 0.18), bev=0.006))
P.append(box('office_ac', 'Klimagerät', G, 'galv', (OX1, 28.0, 1.9), (OX1 + 0.32, 28.9, 2.5), collide=False, bev=0.01))
P.append(box('office_ac_grille', 'Lüftergitter', G, 'grating', (OX1 + 0.32, 28.1, 1.95), (OX1 + 0.33, 28.8, 2.45), collide=False, bev=0.0))
P.append(sign('office_sign', 'Leitstand', G, (-15.3, OY0 - 0.005, 2.45), (0, -1, 0), 1.5, 0.3, '#2B2E33',
              [txt('LEITSTAND', 0.15, 0.13, '#E3E0D6', 0.75, 0.075)], px_m=0.003))
P.append(box('office_emerg', 'Notleuchte Gehäuse', G, 'steel_dark', (-14.46, OY0 - 0.12, 2.3), (-14.14, OY0, 2.42), collide=False, bev=0.008))
P.append(box('office_emerg_lens', 'Notleuchte Linse', G, 'emerg_red', (-14.42, OY0 - 0.15, 2.32), (-14.18, OY0 - 0.12, 2.4), collide=False, bev=0.0))
EMERG.append(((-14.3, OY0 - 0.3, 2.36), (0.0, -1.0, 0.0)))
# Stromaggregat (Stellplatz am Tor)
G = 'Aggregat'
GX0, GX1, GYA, GYB = -9.5, -6.7, -22.2, -20.6
P.append(box('gen_body', 'Stromaggregat', G, 'crate_olive', (GX0, GYA, 0.42), (GX1, GYB, 1.75), bev=0.02))
P.append(box('gen_top', 'Aggregat Abdeckung', G, 'steel_dark', (GX0 + 0.1, GYA + 0.1, 1.75), (GX1 - 0.1, GYB - 0.1, 1.85), bev=0.01))
P.append(box('gen_panel', 'Bedienfeld', G, 'steel_dark', (GX0 - 0.04, -21.9, 0.9), (GX0, -21.1, 1.5), collide=False, bev=0.006))
P.append(box('gen_panel_lamp', 'Betriebsleuchte', G, 'accent', (GX0 - 0.055, -21.3, 1.38), (GX0 - 0.04, -21.2, 1.44), collide=False, bev=0.0))
P.append(box('gen_frame', 'Fahrgestell', G, 'steel_dark', (GX0 - 0.1, GYA - 0.05, 0.3), (GX1 + 0.1, GYB + 0.05, 0.42), collide=False))
for sd, y in (('s', GYA), ('n', GYB)):
    for m in range(6):
        z = 0.75 + m * 0.14
        P.append(box(f'gen_louvre_{sd}{m}', 'Lüftungslamelle', G, 'steel_dark', (GX1 - 1.2, min(y, y + (0.03 if sd == 'n' else -0.03)), z),
                     (GX1 - 0.2, max(y, y + (0.03 if sd == 'n' else -0.03)), z + 0.05), collide=False, bev=0.0))
P.append(cyl('gen_exhaust', 'Auspuff', G, 'steel_dark', 'z', (GX1 - 0.5, -21.0, 2.15), 0.07, 0.6, segs=12, collide=False, bev=0.0))
P.append(box('gen_eye', 'Kranöse', G, 'steel_dark', (-8.15, -21.45, 1.85), (-8.05, -21.35, 2.0), collide=False, bev=0.0))
for i, (x, y) in enumerate(((GX0 + 0.6, GYA - 0.16), (GX1 - 0.6, GYA - 0.16), (GX0 + 0.6, GYB + 0.16), (GX1 - 0.6, GYB + 0.16))):
    P.append(cyl(f'gen_wheel_{i}', 'Rad', G, 'rubber', 'y', (x, y, 0.3), 0.3, 0.2, segs=20))
    P.append(cyl(f'gen_wheel_{i}_hub', 'Radnabe', G, 'steel_dark', 'y', (x, y + (0.1 if y > -21.4 else -0.1), 0.3), 0.12, 0.02, segs=12,
                 collide=False, bev=0.0))
P.append(beam('gen_drawbar', 'Deichsel', G, 'steel_dark', (GX1 + 0.1, -21.4, 0.36), (GX1 + 1.3, -21.4, 0.1), 0.08, 0.08, collide=True))
# Kisten und Fässer zur Ausstattung (abseits der Strecke)
P += crate('crate_nw1', -18.2, 23.8, 0, 2.4, 1.2, 1.2, 'crate_olive')
P += crate('crate_nw2', -18.2, 23.8, 1.2, 1.2, 1.2, 1.0, 'crate_grey')
P += crate('crate_nw3', -18.6, 21.9, 0, 1.2, 1.6, 1.0, 'crate_cream')
P += crate('crate_nw4', -16.5, 22.3, 0, 1.6, 1.0, 0.8, 'crate_olive')
P += pallet('pallet_w1', -18.4, 10.5, sx=1.2, sy=1.2)
for i, (dx, dy) in enumerate(((-0.3, -0.3), (0.3, -0.3), (-0.3, 0.3), (0.3, 0.3))):
    P += barrel(f'barrel_w1_{i}', -18.4 + dx, 10.5 + dy, 0.145, 'barrel_blue')
P += barrel('barrel_w2', -18.6, 8.2, 0, 'barrel_orange')
P += barrel('barrel_w3', -17.9, 8.0, 0, 'barrel_blue')
P += crate('crate_w7', -18.2, 14.0, 0, 2.4, 1.2, 1.2, 'crate_grey')
P += crate('crate_w8', -18.6, 15.6, 0, 1.2, 1.2, 1.0, 'crate_cream')
P += crate('crate_w9', -18.2, 14.0, 1.2, 1.2, 1.2, 1.2, 'crate_olive')
P += crate('crate_e1', 16.6, -22.4, 0, 2.4, 1.2, 1.2, 'crate_olive')
P += crate('crate_e2', 16.6, -22.4, 1.2, 2.4, 1.2, 1.2, 'crate_grey')
P += crate('crate_e3', 17.4, -20.6, 0, 1.2, 1.2, 1.2, 'crate_cream')
P += crate('crate_e4', 14.6, -24.6, 0, 1.6, 1.0, 0.8, 'crate_grey')
P += pallet('pallet_e1', 6.6, 14.6, sx=1.2, sy=1.2)
for i, (dx, dy) in enumerate(((-0.3, -0.3), (0.3, -0.3), (-0.3, 0.3), (0.3, 0.3))):
    P += barrel(f'barrel_e1_{i}', 6.6 + dx, 14.6 + dy, 0.145, 'barrel_orange' if i == 2 else 'barrel_blue')
P += barrel('barrel_e2', 7.4, 13.2, 0, 'barrel_orange')
P += crate('crate_m1', -8.0, 6.0, 0, 1.6, 1.2, 1.0, 'crate_cream')
P += crate('crate_m2', -9.2, 6.2, 0, 1.0, 1.0, 0.8, 'crate_olive')

# ------------------------------------------------------------------ Vorfeld und Splitterschutzwand (Zone fern)
for i, xa in enumerate(range(-20, 20, 10)):
    for j, (ya, yb) in enumerate(((AY0, -41.25), (-41.25, AY1))):
        P.append(box(f'apron_{i}{j}', 'Vorfeld', 'Vorfeld', 'concrete_out', (xa, ya, -0.3), (xa + 10, yb, 0.0),
                     skip=('-z', '+x', '-x', '+y', '-y'), bev=0.0))
APRON_LIGHTS = []
for s, x in (('w', -18.4), ('e', 18.4)):
    for k, y in enumerate((-33.0, -36.5, -40.0, -43.5, -47.0, -50.5)):
        P.append(cyl(f'edge_light_{s}{k}', 'Randfeuer Fuß', 'Vorfeld', 'steel_dark', 'z', (x, y, 0.11), 0.09, 0.22, segs=10))
        P.append(cyl(f'edge_light_{s}{k}_lens', 'Randfeuer Linse', 'Vorfeld', 'beacon_blue', 'z', (x, y, 0.26), 0.06, 0.08, segs=10,
                     collide=False, bev=0.0))
        APRON_LIGHTS.append((f'Randfeuer_{s.upper()}{k + 1}', (x, y, 0.5)))
TW, TH, TT = 1.5, 3.6, 0.35


def twall(pid, axis, u, at, sg):
    """T-Wall-Segment (Breite TW, Höhe TH) quer zur Achse `axis` bei `at`; Fuß zur Innenseite (sg = Richtung nach innen)."""
    if axis == 'y':
        out = [box(pid, 'Splitterschutzwand', 'Schutzwall', 'concrete_wall', (u + 0.015, at - TT / 2, 0), (u + TW - 0.015, at + TT / 2, TH),
                   skip=('-y',), bev=0.02),
               box(pid + '_foot', 'Wandfuß', 'Schutzwall', 'concrete_wall', (u + 0.015, at, 0), (u + TW - 0.015, at + sg * 0.6, 0.35), bev=0.02)]
        for m, du in enumerate((0.35, TW - 0.35)):
            out.append(box(f'{pid}_loop{m}', 'Hebeöse', 'Schutzwall', 'galv', (u + du - 0.06, at - 0.02, TH), (u + du + 0.06, at + 0.02, TH + 0.1),
                           collide=False, bev=0.0))
    else:
        out = [box(pid, 'Splitterschutzwand', 'Schutzwall', 'concrete_wall', (at - TT / 2, u + 0.015, 0), (at + TT / 2, u + TW - 0.015, TH),
                   skip=('+x' if sg < 0 else '-x',), bev=0.02),
               box(pid + '_foot', 'Wandfuß', 'Schutzwall', 'concrete_wall', (at, u + 0.015, 0), (at + sg * 0.6, u + TW - 0.015, 0.35), bev=0.02)]
        for m, du in enumerate((0.35, TW - 0.35)):
            out.append(box(f'{pid}_loop{m}', 'Hebeöse', 'Schutzwall', 'galv', (at - 0.02, u + du - 0.06, TH), (at + 0.02, u + du + 0.06, TH + 0.1),
                           collide=False, bev=0.0))
    return out


ns = round((X1 - X0) / TW) + 1
for i in range(ns):
    P += twall(f'twall_s{i:02d}', 'y', X0 - 0.5 + i * TW, AY0 + TT / 2, 1)
nside = round((AY1 - AY0) / TW)
for i in range(nside):
    P += twall(f'twall_w{i:02d}', 'x', AY0 + TT + i * TW, X0 + TT / 2, 1)
    P += twall(f'twall_e{i:02d}', 'x', AY0 + TT + i * TW, X1 - TT / 2, -1)

# ------------------------------------------------------------------ Spieler, Parcours, Ziele
SPAWN = dict(pos=(0.0, 25.0, 0.0), yaw_deg=0.0, de='Vor dem Startportal (y = 22), Blick nach −Y durch die Halle')


def _n(v):
    s = math.sqrt(sum(x * x for x in v))
    return tuple(round(x / s, 4) for x in v)


# Zielscheiben: Mitte, Blickrichtung (zum Spieler), Radius, Sichtbarkeit (frei | deckung | oben), Halterung
TARGETS = [
    dict(name='T01', pos=(17.8, 14.0, 4.2), normal=(-1.0, 0.0, 0.0), radius=0.3, vis='frei', mount='wall', de='Regal Ost, 4,2 m hoch'),
    dict(name='T02', pos=(6.12, 11.0, 1.1), normal=(-1.0, 0.0, 0.0), radius=0.3, vis='deckung', mount='floor',
         de='hinter einer Kiste, nur die obere Hälfte frei'),
    dict(name='T03', pos=(-3.0, -8.0, 1.5), normal=_n((0.3, 1.0, 0.0)), radius=0.3, vis='frei', mount='floor', de='vor dem Kistenberg'),
    dict(name='T04', pos=(-18.0, -29.43, 1.6), normal=(0.0, 1.0, 0.0), radius=0.25, vis='frei', mount='wall',
         de='Torpfosten West, Ende der Containergasse'),
    dict(name='T05', pos=(2.0, -42.0, 1.6), normal=(0.0, 1.0, 0.0), radius=0.35, vis='frei', mount='floor', de='Vorfeld, durchs Tor'),
    dict(name='T06', pos=(-6.0, -51.6, 2.4), normal=(0.0, 1.0, 0.0), radius=0.4, vis='frei', mount='wall',
         de='Splitterschutzwand Süd, ≈ 26 m'),
    dict(name='T07', pos=(3.0, -27.6, 0.45), normal=_n((-1.0, 0.0, 0.15)), radius=0.25, vis='frei', mount='floor', de='bodennah am Tor'),
    dict(name='T08', pos=(6.0, -21.0, 11.13), normal=(0.0, 0.0, -1.0), radius=0.35, vis='frei', mount='wall',
         de='unter dem Binder, 11,1 m hoch'),
    dict(name='T09', pos=(15.9, -10.6, 1.25), normal=_n((-0.72, 0.0, 0.69)), radius=0.3, vis='oben', mount='floor', de='Kistenburg'),
    dict(name='T10', pos=(16.6, -8.3, 1.2), normal=_n((-0.75, 0.0, 0.66)), radius=0.3, vis='oben', mount='floor', de='Kistenburg'),
    dict(name='T11', pos=(15.5, -6.9, 1.3), normal=_n((-0.7, 0.2, 0.69)), radius=0.3, vis='oben', mount='floor', de='Kistenburg'),
    dict(name='T12', pos=(8.0, -9.0, 1.6), normal=_n((1.0, 0.0, 0.3)), radius=0.3, vis='frei', mount='floor', de='unter dem Laufsteg'),
    dict(name='T13', pos=(6.0, Y1 - PROF_W['depth'] - 0.07, 5.0), normal=(0.0, -1.0, 0.0), radius=0.3, vis='frei', mount='wall',
         de='Nordwand, 5 m hoch'),
    dict(name='T14', pos=(17.8, 24.0, 5.9), normal=(-1.0, 0.0, 0.0), radius=0.25, vis='frei', mount='wall', de='Regal Ost, oberste Ebene'),
]
for t in TARGETS:
    P += stand(f'stand_{t["name"].lower()}', t['pos'], t['normal'], t['radius'], mount=t['mount'])

PARTS = P

# Strecke am Boden: (x, y, z der Lauffläche, Art des folgenden Abschnitts: run | jump | duck | stairs | drop)
ROUTE = [
    (0.0, 23.5, 0.0, 'run'), (0.0, 20.2, 0.0, 'run'), (2.2, 18.6, 0.0, 'run'), (2.2, 16.6, 0.0, 'run'), (-2.2, 14.8, 0.0, 'run'),
    (-2.2, 12.8, 0.0, 'run'), (2.2, 11.0, 0.0, 'run'), (2.2, 9.0, 0.0, 'run'), (-2.2, 7.2, 0.0, 'run'), (-2.2, 5.1, 0.0, 'run'),
    (0.0, 4.2, 0.0, 'jump'), (0.0, 2.0, 0.0, 'jump'), (0.0, 0.95, 0.6, 'jump'), (0.0, -0.25, 1.2, 'drop'),
    (0.0, -2.4, 0.0, 'run'), (-5.0, -5.6, 0.0, 'run'), (-18.0, -8.2, 0.0, 'run'), (-18.0, -15.3, 0.0, 'duck'), (-18.0, -18.7, 0.0, 'run'),
    (-18.0, -24.5, 0.0, 'run'), (-15.0, -24.9, 0.0, 'run'), (-6.0, -25.6, 0.0, 'jump'), (-2.0, -25.6, 0.0, 'run'), (9.6, -25.5, 0.0, 'stairs'),
    (9.6, -21.45, 3.0, 'run'), (9.6, -20.4, 3.0, 'run'), (12.0, -19.4, 3.0, 'run'), (12.0, 4.6, 3.0, 'drop'), (12.0, 5.75, 1.6, 'drop'),
    (12.0, 7.4, 0.0, 'run'), (11.5, 12.0, 0.0, 'run'), (11.5, 20.6, 0.0, 'run'),
]
COURSE = dict(
    de='Rundkurs durch die Halle: Slalom, Mauer, Kistenberg, Ducken, Leitwand, Treppe, Laufsteg, Herunterspringen',
    start=dict(center=(0.0, Y_START, 1.2), size=(7.0, 0.4, 2.4)),
    finish=dict(center=(11.5, Y_FINISH, 1.2), size=(5.8, 0.4, 2.4)),
    checkpoints=[dict(name='Slalom', center=(0.0, 4.6, 1.2), size=(6.9, 1.0, 2.4)),
                 dict(name='Kistenberg', center=(0.0, -0.6, 2.4), size=(6.9, 1.0, 2.4)),
                 dict(name='Ducken', center=(-18.0, -20.5, 1.2), size=(2.6, 1.0, 2.4)),
                 dict(name='Gerüst oben', center=(11.0, -20.0, GZ + 1.2), size=(4.0, 3.2, 2.4)),
                 dict(name='Laufsteg Ende', center=(12.0, 3.5, GZ + 1.2), size=(4.0, 3.0, 2.4))],
    targets=TARGETS,
    route=ROUTE,
)

# ------------------------------------------------------------------ Zonen und Lichtszenen
ZONES = [
    dict(name='boden', de='Hallenboden (nah)', groups=['Boden'], size=4096),
    dict(name='nah', de='Parcours, Gerüst, Kisten, Container, Ausstattung (nah)',
         groups=['Parcours', 'Geruest', 'Ducken', 'Kisten', 'Faesser', 'Regal', 'Buero', 'Aggregat'], size=4096),
    dict(name='wand', de='Wände bis Lichtband, Stützen, Tor, Technik (mittel)',
         groups=['Wand_West', 'Wand_Ost', 'Wand_Nord', 'Stuetzen', 'Tor', 'Technik'], size=4096),
    dict(name='fern', de='Wände oben, Dach, Fachwerk, Strahler, Vorfeld, Schutzwall (fern)',
         groups=['Wand_Oben', 'Dach', 'Fachwerk', 'Strahler', 'Vorfeld', 'Schutzwall'], size=2048),
]


def _lamps(power, color):
    return [dict(name=n, kind='area', pos=p, dir=(0.0, 0.0, -1.0), power_w=power, size_m=1.0, color=color) for n, p in LAMPS]


def _sun(name, elev_deg, azim_deg, power, color, angle=1.5):
    """Sonne: Höhe über dem Horizont, Herkunftsrichtung (Azimut 0 = von −Y/Tor, 90 = von −X/Westen); `dir` = Leuchtrichtung."""
    e, a = math.radians(elev_deg), math.radians(azim_deg)
    d = (math.cos(e) * math.sin(a), math.cos(e) * math.cos(a), -math.sin(e))
    d = tuple(round(x, 4) for x in d)
    return dict(name=name, kind='sun', pos=tuple(round(-90 * x, 2) for x in d), dir=d, power_w=power, size_m=0.0, color=color,
                blender_angle_deg=angle)


SIGNS_LIT = [r for r in ROLES if r.startswith('sign_door_')]
LIGHTINGS = [
    dict(name='tag', de='Tag', stimmung='klare Mittagssonne steht vor dem Tor und fällt 20° hoch bis etwa zur Hallenmitte, Strahler an',
         sky=dict(color='#9FBAD6', strength=1.3), scale=3.0,
         lights=_lamps(320.0, '#FFF1DC') + [_sun('Sonne', 20.0, 22.4, 7.0, '#FFF0D8')],
         emit=dict({'lamp': 1.0}, **{r: 0.8 for r in SIGNS_LIT})),
    dict(name='abend', de='Abend', stimmung='tiefe warme Sonne (14°) aus Westsüdwest: lange Lichtstreifen durch Tor und Lichtband '
                                            'über Boden und Ostwand, Strahler gedämpft, Himmel mauve',
         sky=dict(color='#9A90A8', strength=0.5), scale=4.0,
         lights=_lamps(200.0, '#FFE6C4') + [_sun('Sonne', 14.0, 52.0, 6.0, '#FFAA58', angle=1.2)],
         emit=dict({'lamp': 0.75}, **{r: 0.8 for r in SIGNS_LIT})),
    dict(name='nacht', de='Nacht', stimmung='nur die Strahler gedimmt (≈ 35 %), rote Notleuchten an Türen und Tor, blaue Randfeuer auf '
                                            'dem Vorfeld, Mondlicht schwach, dunkler Himmel',
         sky=dict(color='#1A2438', strength=0.1), scale=1.5,
         lights=(_lamps(110.0, '#FFDDB0') + [_sun('Mond', 38.0, -25.0, 0.04, '#A8BEFF', angle=0.6)]
                 + [dict(name=f'Notlicht_{i + 1}', kind='point', pos=tuple(round(x, 3) for x in p), dir=d, power_w=25.0, size_m=0.05,
                         color='#FF3020') for i, (p, d) in enumerate(EMERG)]
                 + [dict(name=n, kind='point', pos=p, dir=(0.0, 0.0, 1.0), power_w=6.0, size_m=0.05, color='#3A70FF')
                    for n, p in APRON_LIGHTS]),
         emit=dict({'lamp': 0.4, 'emerg_red': 6.0, 'beacon_blue': 8.0}, **{r: 1.2 for r in SIGNS_LIT})),
    dict(name='bewoelkt', de='Bewölkt', stimmung='geschlossene Wolkendecke: weiches gleichmäßiges Himmelslicht durch Tor und Lichtband, '
                                                 'keine Schatten, Strahler an',
         sky=dict(color='#C3C8CC', strength=2.2), scale=3.0,
         lights=_lamps(320.0, '#FFF1DC'),
         emit=dict({'lamp': 1.0}, **{r: 0.8 for r in SIGNS_LIT})),
]
REFERENCE = dict(eye_m=1.62, h_fov_deg=75.0, res=(1600, 900), view='AgX', look='AgX - Medium High Contrast', samples=256)
# Sichtungsansichten (nur Cache, je Lichtszene als Atlasansicht wie in Unity): Lage, Gier (0 = −Y, 90 = +X), Nick, Bildwinkel
VIEWS = [
    dict(name='gasse', pos=(-18.0, -10.6, 1.62), yaw=0.0, pitch=-4.0, fov=70.0, de='Containergasse mit Rohrbrücke (Ducken)'),
    dict(name='tor', pos=(-10.0, -24.5, 1.7), yaw=-118.0, pitch=4.0, fov=70.0, de='Torpfosten West, Container, Aggregat'),
    dict(name='geruest', pos=(4.0, -27.4, 1.62), yaw=148.0, pitch=8.0, fov=75.0, de='Treppe, Bühne, Laufsteg'),
    dict(name='laufsteg', pos=(12.0, -14.0, 4.62), yaw=142.0, pitch=-35.0, fov=75.0, de='Blick vom Laufsteg in die Kistenburg'),
    dict(name='wand', pos=(-14.5, 7.0, 1.7), yaw=-62.0, pitch=8.0, fov=70.0, de='Westwand: Sockel, Trapezblech, Stütze, Trasse'),
    dict(name='boden', pos=(-3.0, -16.0, 2.4), yaw=-45.0, pitch=-28.0, fov=70.0, de='Bodenmarkierungen, Flecken am Aggregat'),
    dict(name='nord', pos=(7.0, 0.0, 1.7), yaw=190.0, pitch=6.0, fov=80.0, de='Rückblick zur Nordwand über den Slalom'),
    dict(name='sturz', pos=(0.0, -21.0, 1.62), yaw=0.0, pitch=46.0, fov=60.0, de='Torsturz mit Schild und Schraubenreihen'),
]
BAKE = dict(samples=64, albedo_samples=48, denoise=True, margin_px=2, pack_margin_px=2, bounces=6, clamp_indirect=4.0)
BUDGET = dict(triangles=160000, objects=40, de='Unity: Umgebung unbeleuchtet, ein Material je Zone; 16,7 ms bei 160 000 Dreiecken')
