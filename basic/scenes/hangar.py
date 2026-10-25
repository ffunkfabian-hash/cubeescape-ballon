"""Szene „Hangar“ (0.8): Sci-Fi-Militärhangar mit offener Torseite, Schussbahn 10/25/50 m.

Halle 40 × 60 m, Dach innen 14 m. x −20…20 (Westwand … Ostwand), y −30 (Tor) … +30 (Nordwand), Boden z = 0.
Der Spieler startet bei y = +25 und blickt nach −Y durch die ganze Halle auf das offene Tor, dahinter Vorfeld, Splitterschutzwall
und Himmel; die Sonne steht vor dem Tor und fällt schräg herein.

Aufbau (Gruppe = FBX-Objekt):
  Boden, Markierung   Betonplatte mit Fugen 6 m, Schussbahn (weiße Linien x = ±10), Schusslinie, Gehwege, Warnstreifen am Tor
  Wand_*, Dach        Betonsockel 1,2 m, darüber Wellblech (Profil als Relief); Dach innen Trapezblech auf Pfetten
  Stuetzen, Fachwerk  HEB-Stützen je 6 m, zehn Fachwerkbinder (Strebenfachwerk, 10 Felder, Untergurt 11,2 m), neun Pfetten
  Tor                 Torpfosten mit Warnstreifen, Torsturz, Laufschiene, Faltflügel innen an beiden Pfosten
  Strahler            2 × 10 Hallenstrahler (Quadrat 1 m) an den Untergurten, x = ±8
  Kisten, Faesser     Gruppen an den Wänden, Sprungkisten neben der Schusslinie
  Regal               Schwerlastregal an der Ostwand (6 Felder, 3 Ebenen)
  Geruest             Wartungsbühne 3 m mit Treppe (12 Steigungen à 0,25 m) und Geländer
  Rohrbruecke         drei Rohre in 1,35 m Höhe an der Westwand (Ducken)
  Buero, Aggregat     Bürocontainer in der Nordwestecke, Stromaggregat am Tor
  Vorfeld, Schutzwall Vorfeld 40 × 21,5 m vor dem Tor, rundum Splitterschutzwand (T-Wall 3,6 m)
"""
from basic.scenes import box, cyl, beam

META = dict(name='hangar', de='Hangar', size_m=(40.0, 60.0, 14.0),
            summary='Sci-Fi-Militärhangar: Wellblech, Stahlfachwerk, offenes Tor mit Tageslicht, Schussbahn 10/25/50 m')

# Umgebungsrollen (sRGB-hex). vary: Helligkeitsschwankung (Rauschen, Maßstab vary_m), pattern: Muster im Weltraum
# ribs: (Achse 'x' | 'xy' = x + y, Teilung m, Tiefe m) Trapezprofil als Relief (Bump) im Weltraum
ROLES = {
    'concrete':     dict(color='#8C8A84', rough=0.85, spec=0.15, vary=0.18, vary_m=1.6, pattern='joints', de='Hallenboden Beton, Fugen 6 m'),
    'concrete_out': dict(color='#9C9991', rough=0.9, spec=0.15, vary=0.22, vary_m=2.5, pattern='joints', de='Vorfeld Beton'),
    'concrete_wall': dict(color='#A7A398', rough=0.9, spec=0.3, vary=0.15, vary_m=0.8, de='Sockel und Schutzwand Beton'),
    'sheet':        dict(color='#C9C5B9', rough=0.6, spec=0.35, vary=0.08, vary_m=3.0, ribs=('xy', 0.3, 0.04),
                         de='Wellblech lackiert (cremeweiß), Trapezprofil 30 cm als Relief'),
    'sheet_roof':   dict(color='#B4B1A8', rough=0.65, spec=0.35, vary=0.06, vary_m=4.0, ribs=('x', 0.35, 0.05),
                         de='Dachblech innen, Trapezprofil 35 cm als Relief'),
    'steel':        dict(color='#4A4F57', rough=0.55, spec=0.4, vary=0.06, vary_m=2.0, de='Lackstahl Graphit (Tragwerk)'),
    'steel_dark':   dict(color='#2B2E33', rough=0.5, spec=0.4, vary=0.05, vary_m=2.0, de='Lackstahl dunkel (Tor, Gehäuse)'),
    'steel_light':  dict(color='#D3CAB6', rough=0.5, spec=0.4, vary=0.06, vary_m=2.0, de='Lackstahl Creme (Torflügel, Container)'),
    'accent':       dict(color='#D9641E', rough=0.5, spec=0.4, de='Akzent Orange (Regalträger, Geländer)'),
    'hazard':       dict(color='#E0B21C', color2='#1D1E21', rough=0.6, spec=0.35, pattern='stripes', stripe_m=0.25,
                         de='Warnstreifen Gelb/Schwarz 45°'),
    'paint_yellow': dict(color='#D6AE2E', rough=0.7, spec=0.3, de='Bodenfarbe Gelb (Gehwege)'),
    'paint_white':  dict(color='#E3E0D6', rough=0.7, spec=0.3, de='Bodenfarbe Weiß (Schussbahn)'),
    'paint_red':    dict(color='#B23A2E', rough=0.7, spec=0.3, de='Bodenfarbe Rot (Schusslinie)'),
    'crate_olive':  dict(color='#5C6350', rough=0.7, spec=0.3, vary=0.06, vary_m=0.7, de='Transportkiste Oliv'),
    'crate_grey':   dict(color='#50555C', rough=0.65, spec=0.3, vary=0.06, vary_m=0.7, de='Transportkiste Grau'),
    'crate_cream':  dict(color='#CFC4AC', rough=0.6, spec=0.3, vary=0.06, vary_m=0.7, de='Transportkiste Creme'),
    'barrel_blue':  dict(color='#34506B', rough=0.5, spec=0.4, de='Fass Blau'),
    'barrel_orange': dict(color='#C85A1C', rough=0.5, spec=0.4, de='Fass Orange'),
    'wood':         dict(color='#8E7556', rough=0.85, spec=0.25, vary=0.12, vary_m=0.3, de='Palette Holz'),
    'rubber':       dict(color='#1B1C1F', rough=0.9, spec=0.2, de='Gummi (Räder)'),
    'grating':      dict(color='#4A4E54', rough=0.6, spec=0.35, de='Gitterrost / Trittstufe'),
    'glass_dark':   dict(color='#232A31', rough=0.15, spec=0.5, de='Fensterscheibe (dunkel, undurchsichtig)'),
    'lamp':         dict(color='#FFF3E0', rough=0.5, spec=0.3, emit=1.0, de='Leuchtfläche Hallenstrahler'),
}

P = []
X0, X1, Y0, Y1, H = -20.0, 20.0, -30.0, 30.0, 14.0
TRUSS_Y = [-27.0 + 6.0 * k for k in range(10)]

# --- Boden und Markierungen ------------------------------------------------------------------------------------------------
# Große Flächen in Felder geteilt (Fugen bei y = 6k, Stoß hinter Stützen): der Atlas packt dichter, die Nähte liegen in Fugen
SPLIT = (Y0 - 0.5, -18.0, -6.0, 6.0, 18.0, Y1)
for i, (ya, yb) in enumerate(zip(SPLIT, SPLIT[1:])):
    P.append(box(f'floor_{i}', 'Hallenboden', 'Boden', 'concrete', (X0, ya, -0.3), (X1, yb, 0.0), skip=('-z', '+x', '-x', '+y', '-y')))
M = 0.01   # Farbschicht 1 cm (kein Z-Fighting in Unity)
for s, x in (('w', -10.0), ('e', 10.0)):
    P.append(box(f'lane_line_{s}', 'Schussbahn-Begrenzung (weiß)', 'Markierung', 'paint_white', (x - 0.06, -28.6, 0), (x + 0.06, 22.4, M),
                 collide=False))
    for d, y in ((10, 15.0), (25, 0.0), (50, -25.0)):
        P.append(box(f'dist_mark_{d}_{s}', f'Distanzmarke {d} m', 'Markierung', 'paint_white',
                     (x - 0.6 if x < 0 else x - 0.06, y - 0.06, 0), (x + 0.06 if x < 0 else x + 0.6, y + 0.06, M), collide=False))
P.append(box('firing_line', 'Schusslinie (rot)', 'Markierung', 'paint_red', (-10.0, 22.4, 0), (10.0, 22.6, M), collide=False))
for s, x in (('w', -13.0), ('e', 13.0)):
    P.append(box(f'walkway_{s}', 'Gehweglinie (gelb)', 'Markierung', 'paint_yellow', (x - 0.07, -28.6, 0), (x + 0.07, 29.5, M),
                 collide=False))
P.append(box('gate_hazard', 'Warnstreifen Torschwelle', 'Markierung', 'hazard', (-17.0, -29.5, 0), (17.0, -28.6, M), collide=False))
P.append(box('gate_rail', 'Bodenschiene Tor', 'Tor', 'steel_dark', (-17.0, -30.3, 0), (17.0, -30.1, 0.02), collide=False))

# --- Wände: Betonsockel + Wellblech ----------------------------------------------------------------------------------------
SOCKEL = 1.2
P.append(box('plinth_w', 'Betonsockel West', 'Wand_West', 'concrete_wall', (X0, -29.5, 0), (X0 + 0.3, Y1, SOCKEL + 0.05), skip=('-x',)))
P.append(box('plinth_e', 'Betonsockel Ost', 'Wand_Ost', 'concrete_wall', (X1 - 0.3, -29.5, 0), (X1, Y1, SOCKEL + 0.05), skip=('+x',)))
P.append(box('plinth_n', 'Betonsockel Nord', 'Wand_Nord', 'concrete_wall', (X0 + 0.3, Y1 - 0.3, 0), (X1 - 0.3, Y1, SOCKEL + 0.05),
             skip=('+y', '-x', '+x')))
ALL = set(('+x', '-x', '+y', '-y', '+z', '-z'))
# Wellblech: ebene Fläche (eine Insel im Atlas), das Trapezprofil trägt das Material als Relief (ROLES › ribs) und backt mit
for i, (ya, yb) in enumerate(((-29.5, -9.0), (-9.0, 15.0), (15.0, Y1))):     # Stöße hinter den Stützen
    P.append(box(f'wall_w_{i}', 'Wellblechwand West', 'Wand_West', 'sheet', (X0, ya, SOCKEL), (X0 + 0.02, yb, H + 0.1), skip=ALL - {'+x'}))
    P.append(box(f'wall_e_{i}', 'Wellblechwand Ost', 'Wand_Ost', 'sheet', (X1 - 0.02, ya, SOCKEL), (X1, yb, H + 0.1), skip=ALL - {'-x'}))
P.append(box('wall_n', 'Wellblechwand Nord', 'Wand_Nord', 'sheet', (X0, Y1 - 0.02, SOCKEL), (X1, Y1, H + 0.1), skip=ALL - {'-y'}))
for s, x in (('w', X0), ('e', X1)):
    sg = 1 if x < 0 else -1
    P.append(box(f'corner_{s}', 'Eckstütze Nord', 'Stuetzen', 'steel', (x, Y1 - 0.45, 0), (x + sg * 0.45, Y1, H + 0.1),
                 skip=('+y', '-x' if x < 0 else '+x')))
P.append(box('door_n', 'Personaltür Nordwand', 'Wand_Nord', 'steel_dark', (6.0, Y1 - 0.36, 0), (7.2, Y1 - 0.02, 2.2), skip=('+y',)))
P.append(box('door_n_frame', 'Türzarge', 'Wand_Nord', 'hazard', (5.85, Y1 - 0.38, 2.2), (7.35, Y1 - 0.02, 2.35), skip=('+y',)))
for i, (ya, yb) in enumerate(zip(SPLIT, SPLIT[1:])):
    P.append(box(f'roof_{i}', 'Dachblech innen', 'Dach', 'sheet_roof', (X0, ya, H), (X1, yb, H + 0.02), skip=ALL - {'-z'}))

# --- Stützen, Fachwerk, Pfetten ---------------------------------------------------------------------------------------------
XC = 19.3        # Innenkante der Stützen
for k, y in enumerate(TRUSS_Y):
    for s, sg in (('w', -1), ('e', 1)):
        P.append(box(f'column_{k}_{s}', 'Stahlstütze HEB 400', 'Stuetzen', 'steel',
                     (sg * XC, y - 0.2, 0), (sg * 19.98, y + 0.2, H), skip=('-x' if sg < 0 else '+x',)))
        P.append(box(f'column_foot_{k}_{s}', 'Stützenfuß', 'Stuetzen', 'steel_dark',
                     (sg * (XC - 0.1), y - 0.3, 0), (sg * 19.7, y + 0.3, 0.06), skip=('-x' if sg < 0 else '+x',)))
    zb0, zb1, zt0, zt1 = 11.2, 11.45, 13.5, 13.78
    P.append(box(f'truss_{k}_bottom', 'Binder Untergurt', 'Fachwerk', 'steel', (-XC, y - 0.12, zb0), (XC, y + 0.12, zb1), collide=False))
    P.append(box(f'truss_{k}_top', 'Binder Obergurt', 'Fachwerk', 'steel', (-XC, y - 0.12, zt0), (XC, y + 0.12, zt1), collide=False))
    n = 10
    xs = [-XC + i * 2 * XC / n for i in range(n + 1)]
    for i, x in enumerate(xs[1:-1], 1):
        P.append(box(f'truss_{k}_v{i}', 'Binder Pfosten', 'Fachwerk', 'steel', (x - 0.06, y - 0.06, zb1), (x + 0.06, y + 0.06, zt0),
                     skip=('-z', '+z'), collide=False))
    for i in range(n):
        xa, xb = xs[i], xs[i + 1]
        if i < n // 2:     # Strebenfachwerk: Diagonalen fallen zur Mitte hin
            a, b = (xa, y, zt0), (xb, y, zb1)
        else:
            a, b = (xa, y, zb1), (xb, y, zt0)
        P.append(beam(f'truss_{k}_d{i}', 'Binder Diagonale', 'Fachwerk', 'steel', a, b, 0.1, 0.1))
for j, x in enumerate([-18.0 + 4.5 * i for i in range(9)]):
    P.append(box(f'purlin_{j}', 'Pfette', 'Fachwerk', 'steel', (x - 0.07, Y0 - 0.5, 13.78), (x + 0.07, Y1, H), skip=('+z',),
                 collide=False))

# --- Tor ------------------------------------------------------------------------------------------------------------------
GY0, GY1, GH = Y0 - 0.5, Y0 + 0.5, 11.0
for s, (xa, xb) in (('w', (X0, -17.0)), ('e', (17.0, X1))):
    P.append(box(f'gate_post_{s}_low', 'Torpfosten unten (Warnstreifen)', 'Tor', 'hazard', (xa, GY0, 0), (xb, GY1, 2.0)))
    P.append(box(f'gate_post_{s}', 'Torpfosten', 'Tor', 'steel_dark', (xa, GY0, 2.0), (xb, GY1, GH)))
    xi = -17.0 if s == 'w' else 17.0
    sg = 1 if s == 'w' else -1
    for i in range(3):     # Faltflügel, innen an die Pfosten geklappt
        xf = xi + sg * (0.12 + i * 0.22)
        P.append(box(f'gate_leaf_{s}{i}', 'Torflügel (gefaltet)', 'Tor', 'steel_light', (xf - 0.05, GY1 + 0.05, 0.05),
                     (xf + 0.05, GY1 + 3.8, GH - 0.25)))
P.append(box('gate_header', 'Torsturz', 'Tor', 'steel_dark', (X0, GY0, GH + 0.4), (X1, GY1, H + 0.5), skip=('+z',)))
P.append(box('gate_header_band', 'Torsturz Warnband', 'Tor', 'hazard', (X0, GY0, GH), (X1, GY1, GH + 0.4)))
P.append(box('gate_track', 'Laufschiene Torflügel', 'Tor', 'steel', (-17.0, GY1, GH - 0.2), (17.0, GY1 + 0.25, GH), collide=False))

# --- Hallenstrahler ----------------------------------------------------------------------------------------------------------
LIGHTS = []
LAMP_Z = 10.42
for k, y in enumerate(TRUSS_Y):
    for s, x in (('w', -8.0), ('e', 8.0)):
        P.append(box(f'lamp_{k}_{s}_housing', 'Strahlergehäuse', 'Strahler', 'steel_dark', (x - 0.56, y - 0.56, 10.45), (x + 0.56, y + 0.56, 10.72),
                     collide=False))
        P.append(box(f'lamp_{k}_{s}_panel', 'Leuchtfläche', 'Strahler', 'lamp', (x - 0.5, y - 0.5, 10.43), (x + 0.5, y + 0.5, 10.45),
                     skip=('+z',), collide=False))
        for r, dx in (('a', -0.4), ('b', 0.4)):
            P.append(cyl(f'lamp_{k}_{s}_rod_{r}', 'Abhängung', 'Strahler', 'steel', 'z', (x + dx, y, 10.96), 0.015, 0.48, segs=6,
                         collide=False))
        LIGHTS.append(dict(name=f'Strahler_{k + 1:02d}_{s.upper()}', kind='area', pos=(x, y, LAMP_Z), dir=(0.0, 0.0, -1.0),
                           power_w=320.0, size_m=1.0, color='#FFF1DC'))
# Sonne vor dem Tor (Leuchtrichtung: nach +Y, schräg von Westen, 20° hoch) und Himmel
LIGHTS.append(dict(name='Sonne', kind='sun', pos=(0.0, -80.0, 45.0), dir=(0.357, 0.865, -0.342), power_w=7.0, size_m=0.0,
                   color='#FFF0D8', angle_deg=1.5))
SKY = dict(color='#9FBAD6', strength=1.3)

# --- Kisten, Fässer, Paletten ------------------------------------------------------------------------------------------------


def crate(pid, x, y, z0, sx, sy, sz, mat, group='Kisten'):
    """Kiste mit Mittelpunkt (x, y) auf Höhe z0, dazu umlaufendes Deckelband (dunkel, 1,5 cm vorstehend)."""
    out = [box(pid, 'Transportkiste', group, mat, (x - sx / 2, y - sy / 2, z0), (x + sx / 2, y + sy / 2, z0 + sz - 0.08))]
    e = 0.015
    out.append(box(pid + '_lid', 'Kistendeckel', group, 'steel_dark', (x - sx / 2 - e, y - sy / 2 - e, z0 + sz - 0.08),
                   (x + sx / 2 + e, y + sy / 2 + e, z0 + sz)))
    out.append(box(pid + '_skid', 'Kistenkufen', group, 'steel_dark', (x - sx / 2 + 0.04, y - sy / 2 + 0.04, z0 - 0.0),
                   (x + sx / 2 - 0.04, y + sy / 2 - 0.04, z0 + 0.06), skip=('+z',)))
    # Kufen liegen unter dem Kistenkörper: Körper beginnt bei z0 + 0,06
    out[0]['a'] = (out[0]['a'][0], out[0]['a'][1], z0 + 0.06)
    return out


def pallet(pid, x, y, z0=0.0, sx=1.2, sy=1.0):
    return box(pid, 'Palette', 'Kisten', 'wood', (x - sx / 2, y - sy / 2, z0), (x + sx / 2, y + sy / 2, z0 + 0.14))


def barrel(pid, x, y, z0, mat):
    return [cyl(pid, 'Fass 200 l', 'Faesser', mat, 'z', (x, y, z0 + 0.44), 0.29, 0.88, segs=20),
            cyl(pid + '_rim', 'Fassdeckel', 'Faesser', 'steel_dark', 'z', (x, y, z0 + 0.885), 0.27, 0.01, segs=20, collide=False)]


# Gruppe West bei der Schusslinie (Deckung, Springen: 0,5 m → 1,0 m → 1,5 m)
P += crate('crate_w1', -16.6, 18.6, 0, 2.4, 1.2, 1.2, 'crate_olive')
P += crate('crate_w2', -17.0, 18.6, 1.2, 1.2, 1.2, 1.0, 'crate_grey')
P += crate('crate_w3', -14.6, 18.7, 0, 1.2, 1.2, 1.2, 'crate_cream')
P += crate('crate_w4', -15.3, 16.3, 0, 1.6, 1.0, 0.8, 'crate_olive')
P += crate('crate_w5', -17.6, 15.4, 0, 1.2, 1.2, 1.2, 'crate_grey')
P += crate('crate_w6', -17.6, 15.4, 1.2, 1.2, 1.2, 0.9, 'crate_olive')
P += crate('jump_1', -14.0, 21.6, 0, 1.2, 1.0, 0.5, 'crate_cream')
P += crate('jump_2', -14.0, 20.4, 0, 1.2, 1.2, 1.0, 'crate_olive')
P += crate('jump_3', -15.3, 20.4, 0, 1.2, 1.2, 1.5, 'crate_grey')
# Tische an der Schusslinie (Mitte frei)
for s, (xa, xb) in (('w', (-3.8, -2.2)), ('e', (2.2, 3.8))):
    P.append(box(f'bench_{s}', 'Schießtisch', 'Kisten', 'steel_light', (xa, 21.7, 0.98), (xb, 22.3, 1.05)))
    for i, x in enumerate((xa + 0.08, xb - 0.08)):
        P.append(box(f'bench_{s}_leg{i}', 'Tischbein', 'Kisten', 'steel', (x - 0.04, 21.75, 0), (x + 0.04, 22.25, 0.98)))
# Gruppe West Mitte mit Fässern
P.append(pallet('pallet_w1', -17.2, -9.0, sx=1.2, sy=1.2))
for i, (dx, dy) in enumerate(((-0.3, -0.3), (0.3, -0.3), (-0.3, 0.3), (0.3, 0.3))):
    P += barrel(f'barrel_w1_{i}', -17.2 + dx, -9.0 + dy, 0.14, 'barrel_blue')
P += crate('crate_w7', -17.4, -12.0, 0, 2.4, 1.2, 1.2, 'crate_grey')
P += crate('crate_w8', -14.9, -12.2, 0, 1.2, 1.2, 1.0, 'crate_cream')
P += crate('crate_w9', -17.4, -12.0, 1.2, 1.2, 1.2, 1.2, 'crate_olive')
P += barrel('barrel_w2', -14.6, -9.4, 0, 'barrel_orange')
P += barrel('barrel_w3', -17.8, 7.2, 0, 'barrel_orange')
P += barrel('barrel_w4', -17.1, 7.0, 0, 'barrel_blue')
P += barrel('barrel_w5', -17.5, 7.8, 0, 'barrel_blue')
# Gruppe Ost am Tor
P += crate('crate_e1', 16.6, -20.4, 0, 2.4, 1.2, 1.2, 'crate_olive')
P += crate('crate_e2', 16.6, -20.4, 1.2, 2.4, 1.2, 1.2, 'crate_grey')
P += crate('crate_e3', 17.2, -18.6, 0, 1.2, 1.2, 1.2, 'crate_cream')
P += crate('crate_e4', 14.4, -21.0, 0, 1.6, 1.0, 0.8, 'crate_grey')
P += crate('crate_e5', 16.9, -23.0, 0, 1.2, 1.2, 1.0, 'crate_olive')
P.append(pallet('pallet_e1', 14.2, -17.4, sx=1.2, sy=1.2))
for i, (dx, dy) in enumerate(((-0.3, -0.3), (0.3, -0.3), (-0.3, 0.3), (0.3, 0.3))):
    P += barrel(f'barrel_e1_{i}', 14.2 + dx, -17.4 + dy, 0.14, 'barrel_orange' if i == 2 else 'barrel_blue')
P += barrel('barrel_e2', 14.0, 9.0, 0, 'barrel_orange')
P += barrel('barrel_e3', 14.7, 9.3, 0, 'barrel_orange')

# --- Schwerlastregal Ostwand -------------------------------------------------------------------------------------------------
RX0, RX1, RY0, BAY, NB = 17.9, 19.1, 12.0, 2.7, 6
LEVELS = (1.8, 3.6, 5.4)
for i in range(NB + 1):
    y = RY0 + i * BAY
    for s, x in (('f', RX0), ('b', RX1 - 0.1)):
        P.append(box(f'rack_up_{i}{s}', 'Regalstütze', 'Regal', 'steel', (x, y - 0.05, 0), (x + 0.1, y + 0.05, 6.2)))
for li, z in enumerate(LEVELS):
    for s, x in (('f', RX0), ('b', RX1 - 0.1)):
        P.append(box(f'rack_beam_{li}{s}', 'Regalträger', 'Regal', 'accent', (x - 0.01, RY0, z), (x + 0.11, RY0 + NB * BAY, z + 0.15)))
    P.append(box(f'rack_deck_{li}', 'Regalboden', 'Regal', 'grating', (RX0 + 0.1, RY0, z + 0.12), (RX1 - 0.1, RY0 + NB * BAY, z + 0.15)))
MATS = ('crate_olive', 'crate_grey', 'crate_cream', 'crate_grey', 'crate_olive')
HS = (1.1, 0.8, 1.3, 0.9, 1.2, 0.7, 1.0)
for b in range(NB):
    for li, z in enumerate((0.0,) + tuple(z + 0.15 for z in LEVELS)):
        for j in range(2):
            n = b * 8 + li * 2 + j
            if n % 7 == 5:          # ein paar Plätze bleiben leer
                continue
            y = RY0 + b * BAY + 0.7 + j * 1.3
            P.append(pallet(f'rack_pal_{b}_{li}_{j}', 18.5, y, z, sx=1.0, sy=1.15))
            P += crate(f'rack_crate_{b}_{li}_{j}', 18.5, y, z + 0.14, 0.95, 1.1, min(HS[n % 7], 1.45 if li < 3 else 1.3),
                       MATS[n % 5], group='Regal')

# --- Wartungsbühne mit Treppe ------------------------------------------------------------------------------------------------
GX0, GX1, GYA, GYB, GZ = 10.5, 16.5, -6.0, -2.5, 3.0
P.append(box('platform', 'Bühne Gitterrost', 'Geruest', 'grating', (GX0, GYA, GZ - 0.1), (GX1, GYB, GZ)))
P.append(box('platform_edge', 'Bühne Randträger', 'Geruest', 'steel', (GX0, GYA, GZ - 0.3), (GX1, GYB, GZ - 0.1), skip=('+z',)))
for i, (x, y) in enumerate(((GX0, GYA), (GX1 - 0.12, GYA), (GX0, GYB - 0.12), (GX1 - 0.12, GYB - 0.12), ((GX0 + GX1) / 2 - 0.06, GYA),
                            ((GX0 + GX1) / 2 - 0.06, GYB - 0.12))):
    P.append(box(f'platform_post_{i}', 'Bühnenstütze', 'Geruest', 'steel', (x, y, 0), (x + 0.12, y + 0.12, GZ - 0.3), skip=('+z',)))
for i, (xa, xb) in enumerate(((GX0 + 0.06, (GX0 + GX1) / 2), ((GX0 + GX1) / 2, GX1 - 0.06))):
    P.append(beam(f'platform_brace_{i}', 'Verband', 'Geruest', 'steel', (xa, GYA + 0.06, 0.25), (xb, GYA + 0.06, GZ - 0.35), 0.06, 0.06))
# Geländer: Pfosten, Handlauf 1,0 m, Knieleiste 0,5 m, Fußleiste (Warnstreifen); Treppenöffnung x 10,5…11,7 an der Kante y = −2,5
RH = GZ + 1.0
posts = [(GX0 + 0.03, GYA + 0.03)] + [(GX0 + 1.5 * i, GYA + 0.03) for i in range(1, 4)] + [(GX1 - 0.03, GYA + 0.03), (GX1 - 0.03, GYB - 0.03)]
posts += [(GX0 + 1.5 * i, GYB - 0.03) for i in range(3, 0, -1)] + [(11.73, GYB - 0.03), (GX0 + 0.03, (GYA + GYB) / 2)]
for i, (x, y) in enumerate(posts):
    P.append(cyl(f'rail_post_{i}', 'Geländerpfosten', 'Geruest', 'accent', 'z', (x, y, GZ + 0.5), 0.025, 1.0, segs=8))
for nm, (a, b) in (('s', ((GX0, GYA), (GX1, GYA + 0.06))), ('e', ((GX1 - 0.06, GYA), (GX1, GYB))), ('n', ((11.7, GYB - 0.06), (GX1, GYB))),
                   ('w', ((GX0, GYA), (GX0 + 0.06, GYB)))):
    P.append(box(f'rail_top_{nm}', 'Handlauf', 'Geruest', 'accent', (a[0], a[1], RH - 0.05), (b[0], b[1], RH)))
    P.append(box(f'rail_mid_{nm}', 'Knieleiste', 'Geruest', 'accent', (a[0], a[1], GZ + 0.48), (b[0], b[1], GZ + 0.52)))
    P.append(box(f'rail_toe_{nm}', 'Fußleiste', 'Geruest', 'hazard', (a[0], a[1], GZ), (b[0], b[1], GZ + 0.15)))
NS, RISE, RUN = 12, GZ / 12, 0.3
SX0, SX1 = GX0, 11.7
for k in range(1, NS):
    y0 = GYB + (NS - k) * RUN
    P.append(box(f'stair_step_{k:02d}', 'Treppenstufe', 'Geruest', 'grating', (SX0 + 0.05, y0, k * RISE - 0.05), (SX1 - 0.05, y0 + RUN, k * RISE)))
P.append(box('stair_landing', 'Austritt', 'Geruest', 'grating', (SX0 + 0.05, GYB, GZ - 0.05), (SX1 - 0.05, GYB + RUN, GZ)))
for s, x in (('w', SX0 + 0.025), ('e', SX1 - 0.025)):
    P.append(beam(f'stair_stringer_{s}', 'Treppenwange', 'Geruest', 'steel', (x, GYB + NS * RUN + 0.1, 0.12), (x, GYB, GZ - 0.05), 0.05, 0.25))
    P.append(beam(f'stair_rail_{s}', 'Treppenhandlauf', 'Geruest', 'accent', (x, GYB + NS * RUN, 1.0), (x, GYB, RH), 0.05, 0.05))
    P.append(cyl(f'stair_post_{s}', 'Treppenpfosten', 'Geruest', 'accent', 'z', (x, GYB + NS * RUN - 0.05, 0.5), 0.025, 1.0, segs=8))

# --- Rohrbrücke Westwand (Ducken: Unterkante 1,35 m) ------------------------------------------------------------------------
PZ = 1.35
for i, y in enumerate((3.6, 4.0, 4.4)):
    r = 0.15 if i != 1 else 0.17
    P.append(cyl(f'pipe_{i}', 'Rohrleitung', 'Rohrbruecke', 'steel_light' if i == 1 else 'steel', 'x', (-16.35, y, PZ + r), r, 5.9, segs=20))
    P.append(cyl(f'pipe_{i}_riser', 'Steigleitung', 'Rohrbruecke', 'steel_light' if i == 1 else 'steel', 'z', (-13.4, y, (PZ + H) / 2),
                 r, H - PZ, segs=20))
for j, x in enumerate((-18.5, -16.0, -13.9)):
    for s, y in (('s', 3.2), ('n', 4.7)):
        P.append(box(f'pipe_post_{j}{s}', 'Rohrstütze', 'Rohrbruecke', 'steel', (x - 0.06, y - 0.06, 0), (x + 0.06, y + 0.06, PZ)))
    P.append(box(f'pipe_beam_{j}', 'Rohrjoch', 'Rohrbruecke', 'accent', (x - 0.06, 3.14, PZ - 0.12), (x + 0.06, 4.76, PZ)))

# --- Bürocontainer Nordwestecke, Stromaggregat --------------------------------------------------------------------------------
P.append(box('office', 'Bürocontainer', 'Buero', 'steel_light', (-19.3, 26.8, 0), (-13.3, 29.6, 2.9)))
P.append(box('office_roof', 'Containerdach', 'Buero', 'steel_dark', (-19.35, 26.75, 2.9), (-13.25, 29.65, 3.0)))
P.append(box('office_window_e', 'Fensterband Ost', 'Buero', 'glass_dark', (-13.3, 27.2, 1.1), (-13.28, 29.2, 2.2), collide=False))
P.append(box('office_window_s', 'Fenster Süd', 'Buero', 'glass_dark', (-18.6, 26.78, 1.1), (-16.6, 26.8, 2.2), collide=False))
P.append(box('office_door', 'Containertür', 'Buero', 'steel_dark', (-15.8, 26.78, 0), (-14.8, 26.8, 2.1), collide=False))
P.append(box('office_step', 'Trittstufe', 'Buero', 'grating', (-16.0, 26.3, 0), (-14.6, 26.8, 0.18)))
P.append(box('gen_body', 'Stromaggregat', 'Aggregat', 'crate_olive', (-16.2, -22.2, 0.42), (-13.4, -20.6, 1.75)))
P.append(box('gen_top', 'Aggregat Abdeckung', 'Aggregat', 'steel_dark', (-16.1, -22.1, 1.75), (-13.5, -20.7, 1.85)))
P.append(box('gen_panel', 'Bedienfeld', 'Aggregat', 'accent', (-13.4, -21.9, 0.9), (-13.36, -21.1, 1.5), collide=False))
P.append(box('gen_frame', 'Fahrgestell', 'Aggregat', 'steel_dark', (-16.3, -22.25, 0.3), (-13.3, -20.55, 0.42)))
for i, (x, y) in enumerate(((-15.6, -22.36), (-14, -22.36), (-15.6, -20.44), (-14, -20.44))):
    P.append(cyl(f'gen_wheel_{i}', 'Rad', 'Aggregat', 'rubber', 'y', (x, y, 0.3), 0.3, 0.2, segs=20))
P.append(beam('gen_drawbar', 'Deichsel', 'Aggregat', 'steel_dark', (-13.3, -21.4, 0.36), (-12.1, -21.4, 0.1), 0.08, 0.08, collide=True))

# --- Vorfeld und Splitterschutzwand -----------------------------------------------------------------------------------------
AY0, AY1 = -52.0, GY0
for i, (xa, xb) in enumerate(((X0, 0.0), (0.0, X1))):
    P.append(box(f'apron_{i}', 'Vorfeld', 'Vorfeld', 'concrete_out', (xa, AY0, -0.3), (xb, AY1, 0.0), skip=('-z', '+x', '-x', '+y', '-y')))
P.append(box('apron_line', 'Rollweg-Mittellinie', 'Vorfeld', 'paint_yellow', (-0.08, AY0 + 1.0, 0), (0.08, AY1, M), collide=False))
P.append(box('apron_stop', 'Haltebalken', 'Vorfeld', 'paint_yellow', (-6.0, -38.0, 0), (6.0, -37.6, M), collide=False))
TW, TH, TT = 1.5, 3.6, 0.35


def twall(pid, axis, u, at, sg):
    """T-Wall-Segment (Breite TW, Höhe TH) quer zur Achse `axis` bei `at`; Fuß zur Innenseite (sg = Richtung nach innen)."""
    if axis == 'y':      # Wand verläuft entlang x (Südabschluss)
        body = box(pid, 'Splitterschutzwand', 'Schutzwall', 'concrete_wall', (u + 0.015, at - TT / 2, 0), (u + TW - 0.015, at + TT / 2, TH),
                   skip=('-y',))
        foot = box(pid + '_foot', 'Wandfuß', 'Schutzwall', 'concrete_wall', (u + 0.015, at, 0), (u + TW - 0.015, at + sg * 0.6, 0.35))
    else:                # entlang y (Seiten)
        body = box(pid, 'Splitterschutzwand', 'Schutzwall', 'concrete_wall', (at - TT / 2, u + 0.015, 0), (at + TT / 2, u + TW - 0.015, TH),
                   skip=('+x' if sg < 0 else '-x',))
        foot = box(pid + '_foot', 'Wandfuß', 'Schutzwall', 'concrete_wall', (at, u + 0.015, 0), (at + sg * 0.6, u + TW - 0.015, 0.35))
    return [body, foot]


ns = round((X1 - X0) / TW) + 1
for i in range(ns):
    P += twall(f'twall_s{i:02d}', 'y', X0 - 0.5 + i * TW, AY0 + TT / 2, 1)
nside = round((AY1 - AY0) / TW)
for i in range(nside):
    P += twall(f'twall_w{i:02d}', 'x', AY0 + TT + i * TW, X0 + TT / 2, 1)
    P += twall(f'twall_e{i:02d}', 'x', AY0 + TT + i * TW, X1 - TT / 2, -1)

PARTS = P

# --- Spieler und Ziele ------------------------------------------------------------------------------------------------------
SPAWN = dict(pos=(0.0, 25.0, 0.0), yaw_deg=0.0, de='Hinter der Schusslinie (y = 22,5), Blick nach −Y durch die Halle')
# Abstand der Scheibe vom Startpunkt (y = 25), Mitte 1,45 m wie im Parcours; seitliche Lagen wie Range.cs
TARGETS = [dict(pos=(x, SPAWN['pos'][1] - d, 1.45), distance=d) for d, xs in ((10, (-3, 0, 3)), (25, (-6, 0, 6)), (50, (-8, 0, 8)))
           for x in xs]
REFERENCE = dict(eye_m=1.62, h_fov_deg=75.0, res=(1600, 900), view='AgX', look='AgX - Medium High Contrast', samples=256)
BAKE = dict(size=4096, samples=256, margin_px=2, pack_margin_px=3, bounces=6, clamp_indirect=4.0)
