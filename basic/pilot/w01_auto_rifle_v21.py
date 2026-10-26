"""BASIC-01 v2.1 – Pilot „Destiny-Detaildichte + AAA-Material, schlicht“ (Formstudie 01).

Gegenüber v2 (`w01_auto_rifle_v2.py`): (1) Unterteil mit angeformtem Magazintrichter und schräger Front, (2) ergonomischer Griff
mit Fingerauflage, Handballenwölbung und ausgestelltem Boden, (3) leicht gekrümmtes Magazin mit Metalllippen und Bodenband,
(4) nach vorn verjüngte Visierhaube, (5) Handschutz in der Draufsicht nach vorn verjüngt, unter der Haube angeschmiegt.

---
v2 – Pilot „Destiny-Detaildichte + AAA-Material“ (Formstudie 01, zweite Fassung).

Gleiche Grundkonstruktion, Anker und Mechanik wie basic/weapons/w01_auto_rifle.py; neu sind die drei Detailebenen
(Schalen · Gliederung · Akzente), Negativraum, Schichtung und Materialbruch nach den Bildreferenzen in docs/quellen.md › Q-D2-IMG.
Ausgabe getrennt (`BASIC-01-v2`), damit die Reihe unverändert bleibt, bis der Nutzer entscheidet.
"""
import math
from basic.common import (part, prof, box, cyl, rot, rail, rifle_mag, grip_rifle, selector, charging_handle, reflex_sight_v21,
                          R_BODY, R_MID, R_SMALL, R_FINE)
from basic.weapons import w01_auto_rifle as V1

META = dict(V1.META, variant='v2.1', name='Formstudie 01 v2.1', nick='Pilot AAA',
            summary='Automatikgewehr mit Destiny-Detaildichte und PBR-Materialien (Pilot).')
ASSEMBLIES = V1.ASSEMBLIES
BORE = 106
RAIL_U = 135


def cut_box(f0, f1, u0, u1, w, x=0.0):
    return dict(shape='box', f0=f0, f1=f1, u0=u0, u1=u1, w=w, x=x)


def screws(pts, x, r=2.2, h=1.2, axis='x'):
    """Schraubenköpfe (Zylinder quer) an (f,u)-Punkten auf der Seitenfläche x (mm, Vorzeichen = Seite)."""
    s = 1 if x > 0 else -1
    return [dict(shape='cyl', axis=axis, c=(f, u), a0=x - s * 0.6, a1=x + s * h, r=r, segs=12) for f, u in pts]


def mirror(items):
    return items + [dict(i, a0=-i['a0'], a1=-i['a1']) for i in items]


P = []
# ---------------------------------------------------------------- Gehäuse: Schalen, Fenster, Fugen
P += [
    prof('upper', 'Oberes Gehäuse', 'Upper receiver', 'receiver', 'shell', 'Tragkörper für Lauf, Verschluss und Schiene',
         'mit Unterem Gehäuse über zwei Querbolzen (fest)', [(-120, 87), (190, 87), (198, 95), (198, 128), (186, 140),
                                                            (52, 140), (40, 135), (-108, 135), (-120, 125)], 44,
         cuts=[cut_box(22, 84, 95, 121, 18, x=-22),                       # Auswurffenster rechts (zeigt den Verschluss)
               cut_box(-100, -56, 116, 125, 10, x=22),                    # Ladehebel-Nut links
               cut_box(-96, -10, 94, 112, 3.0, x=22.6), cut_box(-96, -10, 94, 112, 3.0, x=-22.6),   # Seitenpaneel-Mulden
               dict(shape='cyl', axis='x', c=(30, 106), a0=18.5, a1=26, r=10.5, segs=32),          # Kernfenster links
               cut_box(110, 111, 139, 145, 60), cut_box(110, 111, 87, 140, 2, x=22.5), cut_box(110, 111, 87, 140, 2, x=-22.5),  # Fuge 1 mm tief
               ]),
    prof('lower', 'Unteres Gehäuse', 'Lower receiver', 'receiver', 'graphite', 'Griffmodul, Abzugsgruppe, Magazinschacht',
         'unter dem Oberen Gehäuse, Fuge 1 mm; Magazintrichter angeformt',
         [(-120, 64), (-64, 42), (70, 42), (78, 30), (82, 20), (142, 20), (148, 30), (186, 66), (186, 86), (-120, 86)], 42,
         cuts=[cut_box(-104, -70, 66, 80, 4.0, x=21.5), cut_box(-104, -70, 66, 80, 4.0, x=-21.5),
               cut_box(150, 170, 72, 82, 4.0, x=21.5), cut_box(150, 170, 72, 82, 4.0, x=-21.5)]),
    box('side_panel_l', 'Seitenpaneel links', 'Side panel left', 'receiver', 'anodized', 'Wartungsdeckel über der Mechanik',
        'in die Mulde geschraubt (4 Schrauben)', -94, -12, 96, 110, 1.2, bevel=R_FINE, x=21.2),
    box('side_panel_r', 'Seitenpaneel rechts', 'Side panel right', 'receiver', 'anodized', 'Wartungsdeckel über der Mechanik',
        'in die Mulde geschraubt (4 Schrauben)', -94, -12, 96, 110, 1.2, bevel=R_FINE, x=-21.2),
    part('panel_screws', 'Paneelschrauben', 'Panel screws', 'receiver', 'multi', 'trim', 'Halten die Seitenpaneele',
         'in den Paneelen', bevel=0.2, items=mirror(screws([(-90, 99), (-90, 107), (-16, 99), (-16, 107)], 21.8, r=1.6, h=0.8))),
    part('takedown_pins', 'Querbolzen', 'Takedown pins', 'receiver', 'multi', 'metal', 'Verbinden Ober- und Unterteil',
         'quer durch das Gehäuse (lösbar)', bevel=0.4,
         items=mirror(screws([(-96, 78), (162, 78)], 21.0, r=3.6, h=1.0))),
    prof('armor_l', 'Seitenpanzer links', 'Side armor left', 'receiver', 'shell', 'Zweite Schicht über Lauflager und Gasweg',
         'mit drei Schrauben aufgesetzt, Stufe 2,5 mm', [(58, 90), (176, 90), (194, 104), (194, 126), (182, 136), (72, 136),
                                                        (58, 122)], 2.5, bevel=R_SMALL, x=23.2),
    prof('armor_r', 'Seitenpanzer rechts', 'Side armor right', 'receiver', 'shell', 'Zweite Schicht über Lauflager und Gasweg',
         'mit drei Schrauben aufgesetzt, Stufe 2,5 mm', [(90, 90), (176, 90), (194, 104), (194, 126), (182, 136), (100, 136),
                                                        (90, 122)], 2.5, bevel=R_SMALL, x=-23.2),
    part('armor_screws', 'Panzerschrauben', 'Armor screws', 'receiver', 'multi', 'trim', 'Halten die Seitenpanzer',
         'in den Panzerplatten', bevel=0.2, items=screws([(66, 96), (186, 98), (186, 126)], 24.4, r=1.8, h=0.8)
         + screws([(98, 96), (186, 98), (186, 126)], -24.4, r=1.8, h=0.8)),
    prof('top_shroud', 'Laufhaube', 'Top shroud', 'receiver', 'shell',
         'Lange Haube über Lauflager und Lauf; kragt frei aus, darunter offener Laufraum', 'auf das Obere Gehäuse geschraubt',
         [(52, 139), (196, 139), (204, 126), (440, 126), (468, 120), (474, 124), (462, 138), (300, 146), (64, 146), (52, 142)],
         40, bevel=R_SMALL, cuts=[cut_box(100 + 22 * i, 112 + 22 * i, 143, 150, 30) for i in range(4)]),
    part('shroud_bracket', 'Haubenstütze', 'Shroud bracket', 'barrel', 'frame', 'anodized', 'Stützt die Haube am Lauf',
         'um den Lauf geklemmt', bevel=R_SMALL, f0=448, f1=460, cu=BORE, ow=28, oh=28, iw=21, ih=21, r_out=6, r_in=10),
    box('shroud_web', 'Haubensteg', 'Shroud web', 'barrel', 'anodized', 'Verbindet Stütze und Haube', 'zwischen Stütze und Haube',
        448, 460, BORE + 12, 128, 12, bevel=R_FINE),
    part('chevron_top', 'Chevronband oben', 'Chevron band top', 'receiver', 'multi', 'accent', 'Lackiertes Band (einziges Grafikelement)',
         'lackiert', bevel=0, items=[dict(shape='plan', pts=[(250 + o, -20), (262 + o, -20), (276 + o, 0), (262 + o, 20),
                                                             (250 + o, 20), (264 + o, 0)], u0=145.9, u1=146.25) for o in (0, 18)]),
    part('chevron_side', 'Chevronband Seiten', 'Chevron band sides', 'receiver', 'multi', 'accent', 'Band läuft über die Seiten',
         'lackiert', bevel=0, items=[dict(shape='prof', pts=[(264 + o, 126.5), (276 + o, 126.5), (262 + o, 145.5), (250 + o, 145.5)],
                                           w=0.3, x=sx * 20.15) for o in (0, 18) for sx in (1, -1)]),
    part('text_l', 'Schriftzug', 'Lettering', 'receiver', 'text', 'decal', 'Kennung „BASIC AR-01“ (einzige Schrift)',
         'aufgedruckt', bevel=0, text='BASIC  AR-01', size=5.0, f=440, u=134.5, x=20.05, side=1, depth=0.12),
    box('top_cover', 'Deckplatte', 'Top cover', 'receiver', 'shell', 'Staubschutz über dem Verschluss; zweite Schicht',
        'auf das Obere Gehäuse gesetzt, Stufe 3 mm', -112, -36, 134, 139, 38, bevel=R_SMALL),
    box('top_cover_trim', 'Deckplatten-Kante', 'Top cover trim', 'receiver', 'trim', 'Blanke Zierkante der Deckplatte',
        'vorn an der Deckplatte', -40, -35, 134, 139.6, 39, bevel=0.4),
    cyl('core_glow', 'Energiekern', 'Energy core', 'receiver', 'energy', 'Leuchtender Kern der Antriebszelle (Blickfang)',
        'hinter dem Kernfenster', 'x', (30, 106), 17.5, 19.6, 10.4, bevel=0, segs=32),
    cyl('core_lens', 'Kernglas', 'Core lens', 'receiver', 'glass', 'Schützt den Kern', 'im Kernfenster', 'x', (30, 106), 20.4, 21.0,
        10.4, bevel=0, segs=32),
    cyl('core_ring', 'Kernring', 'Core ring', 'receiver', 'trim', 'Fasst das Kernfenster', 'um das Kernfenster geschraubt',
        'x', (30, 106), 21.4, 24.2, 14.5, r_in=10.2, bevel=0.6, segs=32),
    box('counter_bezel', 'Anzeigenrahmen', 'Counter bezel', 'receiver', 'anodized', 'Fasst die Munitionsanzeige',
        'auf das Obere Gehäuse geschraubt', -48, -14, 112.5, 124, 2.4, bevel=0.6, x=22.6),
    box('ammo_counter', 'Munitionsanzeige', 'Ammo counter', 'receiver', 'energy', 'Füllstand; zurückhaltendes Leuchtfeld',
        'im Anzeigenrahmen', -44, -18, 114.5, 122, 1.0, bevel=0.2, x=23.6),
    part('mag_release', 'Magazinhalter', 'Magazine release', 'grip_controls', 'cyl', 'accent', 'Löst das Magazin',
         'Druckknopf links', bevel=R_FINE, axis='x', c=(74, 60), a0=19, a1=23.5, r=5, segs=20,
         move=dict(kind='translate', pivot=(74, 60, 21), vector_mm=(0, 0, -2.5), event='reload')),
]
# Magazinschacht: Trichter ist Teil des Unterteils; hier nur die blanke Einführlippe (Schnittstelle BMW-R)
P += [
    prof('mag_well', 'Schachtlippe', 'Magazine well lip', 'receiver', 'trim', 'Blanke Einführkante des Magazintrichters',
         'unten am Trichter des Unterteils', [(81, 17.5), (143, 17.5), (144, 21), (80, 21)], 43, bevel=0.6, iface='BMW-R'),
]
# Verschluss sichtbar im Auswurffenster
P += [
    box('bolt_carrier', 'Verschlussträger', 'Bolt carrier', 'mechanism', 'metal', 'Lädt und verriegelt; läuft beim Schuss zurück',
        'im Oberen Gehäuse geführt', -40, 82, 97, 119, 26, bevel=R_SMALL,
        cuts=[cut_box(30, 76, 104, 112, 4, x=-13)],
        move=dict(kind='translate', pivot=(20, 108, 0), vector_mm=(-42, 0, 0), event='fire')),
    prof('port_cover', 'Auswurfklappe', 'Ejection port cover', 'mechanism', 'anodized', 'Deckt das Auswurffenster ab',
         'Scharnier an der Unterkante', [(22, 95), (84, 95), (84, 121), (22, 121)], 1.6, bevel=R_FINE, x=-22.6,
         move=dict(kind='rotate', pivot=(53, 95, -23), axis='f', range_deg=(0, 75), event='fire',
                   expect=((53, 121, -23), (0, 0, -1)))),
]
P += [dict(p, mat='anodized') for p in rail(-30, 50, RAIL_U)]
P[-1]['cuts'] = [cut_box(-24 + 12 * i, -18 + 12 * i, RAIL_U + 4, RAIL_U + 9, 30) for i in range(7)]
# ---------------------------------------------------------------- Visier (Familienbaustein, schlank; Visier-Standard)
_sight, SIGHT_ANCHORS = reflex_sight_v21(-6, RAIL_U + 8)
P += _sight
# ---------------------------------------------------------------- Griff, Abzug, Bedienung
_t = math.tan(math.radians(15))


def _A(u, d):   # Punkt auf der Griffachse (Neigung 15°) in Höhe u, um d nach vorn versetzt
    return (u * _t + d, u)


for p in grip_rifle(top=42):
    if p['id'] == 'grip':
        p.update(mat='rubber', pts=[_A(42, -20), _A(12, -23), _A(-22, -26), _A(-52, -22), _A(-64, -25), _A(-74, -22),
                                    _A(-76, -12), _A(-76, 16), _A(-70, 23), _A(-60, 18), _A(-50, 21), _A(-40, 17), _A(-30, 21),
                                    _A(-20, 17), _A(-8, 21), _A(16, 20), _A(42, 21)])
    if p['id'] == 'trigger_guard':
        p['mat'] = 'anodized'
    P.append(p)
P.append(prof('grip_cap', 'Griffboden', 'Grip cap', 'grip_controls', 'anodized', 'Ausgestellter Abschluss; schützt den Griff',
              'unten auf den Griff geschraubt', [_A(-73, -23), _A(-73, 24), _A(-79, 22), _A(-79, -21)], 32, bevel=R_SMALL))
P += selector(8, 70, x=22.5)
P += [dict(p, id='selector_r', de='Feuerwahlhebel rechts', en='Fire selector right', x=-22.5) for p in selector(8, 70)]
P += charging_handle(-96, 121, x=22.5, travel=60)
# ---------------------------------------------------------------- Magazin mit Sichtfenster
_mc = (108, 72)
_mu0, _ml = 72, 142


def _cv(u):   # Krümmung: Versatz nach vorn, wächst quadratisch zum Magazinboden (max. 12 mm)
    s = (_mu0 - u) / _ml
    return 12 * s * s


def _mag_side(f0, us):
    return [(f0 + _cv(u), u) for u in us]


_us = [72, 40, 10, -20, -50, -70]
_body = _mag_side(88, _us) + _mag_side(128, _us[::-1])
_m = rifle_mag(88, 72, depth=40, length=142, tilt=8, w=24)
for p in _m:
    if p['id'] == 'magazine':
        p['pts'] = rot(_body, _mc, 8)
        p['de'], p['func'] = 'Magazin (gekrümmt)', 'Hält die Patronen; leicht gekrümmt; entnehmbar'
        p['cuts'] = ([dict(shape='prof', pts=rot([(94 + _cv(uu), uu), (124 + _cv(uu), uu), (124 + _cv(uu), uu + 2.2),
                                                  (94 + _cv(uu), uu + 2.2)], _mc, 8), w=3, x=sx * 12)
                      for uu in (-12, -26, -40) for sx in (1, -1)]
                     + [dict(shape='prof', pts=rot([(100 + _cv(u), u) for u in (34, 16, -2)] + [(118 + _cv(u), u) for u in (-2, 16, 34)],
                                                   _mc, 8), w=8, x=10)])
    if p['id'] == 'magazine_base':
        p['mat'] = 'anodized'
        p['pts'] = rot([(86 + _cv(-70), -70.5), (132 + _cv(-70), -70.5), (132 + _cv(-79), -79), (86 + _cv(-79), -79)], _mc, 8)
    if p['id'] == 'magazine_round':
        p['mat'] = 'brass'
P += _m
P += [
    prof('mag_band', 'Bodenband', 'Base band', 'ammo', 'metal', 'Metallband über dem Magazinboden; Greifkante', 'am Magazin',
         rot([(87 + _cv(-62), -62), (129 + _cv(-62), -62), (129 + _cv(-69), -69), (87 + _cv(-69), -69)], _mc, 8), 25,
         bevel=R_FINE, parent_part='magazine'),
    part('mag_lips', 'Zuführlippen', 'Feed lips', 'ammo', 'multi', 'metal', 'Halten die oberste Patrone; im Schacht verborgen',
         'oben am Magazin', bevel=0.3, parent_part='magazine',
         items=[dict(shape='prof', pts=rot([(92, 72), (124, 72), (124, 76), (96, 76)], _mc, 8), w=2, x=sx * 10) for sx in (1, -1)]),
]
_rounds = []
for i in range(7):
    uu0 = 30 - 5.4 * i
    ff, uu = rot([(110 + _cv(uu0) + (3 if i % 2 else -3), uu0)], _mc, 8)[0]
    _rounds.append(dict(shape='cyl', axis='f', c=(uu, 4 if i % 2 else -2), a0=ff - 14, a1=ff + 14, r=4.4, segs=12))
P.append(part('mag_rounds', 'Patronen im Fenster', 'Visible rounds', 'ammo', 'multi', 'brass', 'Zeigt den Füllstand',
              'im Magazin', bevel=0.3, parent_part='magazine', items=_rounds, smooth=True))
# ---------------------------------------------------------------- Handschutz mit Fenstern, Lauf, Gasrohr
_win = [cut_box(240 + 40 * i, 268 + 40 * i, 92, 110, 12, x=sx * 22) for i in range(2) for sx in (1, -1)]
P += [
    part('handguard', 'Handschutz', 'Handguard', 'support', 'plan', 'graphite',
         'Griffbereich der Stützhand; nach vorn verjüngt, unter der Haube angeschmiegt', 'am Oberen Gehäuse verschraubt, Fuge 1 mm',
         bevel=R_BODY, pts=[(199, -23), (300, -23), (362, -18), (362, 18), (300, 23), (199, 23)], u0=64, u1=124.5,
         cuts=_win + [cut_box(199, 352, 74, 114, 30),
                      dict(shape='prof', pts=[(300, 50), (380, 50), (380, 83), (362, 83)], w=60),         # schräge Unterkante vorn
                      dict(shape='prof', pts=[(190, 140), (214, 140), (214, 124.6), (199, 117)], w=60)]),  # Übergang zum Gehäuse
    prof('handguard_grip', 'Griffpolster', 'Grip pad', 'support', 'rubber', 'Rutschfeste Zone für die Stützhand',
         'unten auf den Handschutz geklebt', [(222, 60.5), (298, 60.5), (298, 66), (222, 66)], 38, bevel=R_SMALL),
    part('handguard_cap', 'Handschutzkappe', 'Handguard end cap', 'support', 'frame', 'anodized', 'Stirnabschluss mit Laufdurchtritt',
         'auf das Handschutzende gesteckt', bevel=R_SMALL, f0=362, f1=372, cu=BORE, ow=34, oh=36, iw=26, ih=26, r_out=8, r_in=12),
    part('handguard_screws', 'Handschutzschrauben', 'Handguard screws', 'support', 'multi', 'trim', 'Halten den Handschutz',
         'seitlich', bevel=0.2, items=mirror(screws([(206, 74), (206, 112)], 23.0, r=1.8, h=0.8))
         + mirror(screws([(348, 88)], 18.8, r=1.6, h=0.8))),
    part('heatsink', 'Kühlrippen', 'Heat sink', 'barrel', 'multi', 'dark_metal', 'Führt Laufwärme ab; im offenen Laufraum',
         'auf den Lauf gepresst', bevel=0.4, items=[dict(shape='cyl', axis='f', c=(BORE, 0), a0=388 + 9 * i, a1=392 + 9 * i, r=15,
                                                         segs=24) for i in range(4)], smooth=True),
    cyl('gas_piston', 'Gaskolben', 'Gas piston', 'barrel', 'metal', 'Überträgt Treibgasdruck; unter dem Lauf sichtbar',
        'im Gasblock geführt', 'f', (BORE - 17, 0), 362, 452, 3.2, segs=12),
    cyl('barrel', 'Lauf', 'Barrel', 'barrel', 'metal', 'Führt das Geschoss; kanneliert', 'im Oberen Gehäuse verschraubt',
        'f', (BORE, 0), 150, 556, 10, segs=24,
        cuts=[cut_box(440, 535, BORE - 1.5, BORE + 1.5, 4, x=sx * 10) for sx in (1, -1)]
             + [cut_box(440, 535, BORE + 8.6, BORE + 12, 3), cut_box(440, 535, BORE - 12, BORE - 8.6, 3)]),
    box('gas_block', 'Gasblock', 'Gas block', 'barrel', 'dark_metal', 'Verbindet Lauf und Gaskolben', 'auf den Lauf geklemmt',
        452, 466, BORE - 24, BORE + 11, 20, bevel=R_SMALL),
    cyl('muzzle', 'Kompensator', 'Compensator', 'barrel', 'anodized', 'Mündungsteil mit Schlitzen und Rändel; Socket_Muzzle',
        'auf Laufende geschraubt (lösbar)', 'f', (BORE, 0), 548, 612, 17, r_in=5.5, segs=8, bevel=R_SMALL, iface='BMZ-15',
        cuts=[cut_box(576 + 9 * i, 581 + 9 * i, BORE + 6, BORE + 22, 14) for i in range(3)]
             + [cut_box(580, 600, BORE - 4, BORE + 4, 44)]
             + [dict(shape='cyl', axis='f', c=(BORE, 0), a0=552 + 4 * i, a1=553.6 + 4 * i, r=19, r_in=16.4, segs=8) for i in range(4)]),
    cyl('muzzle_crown', 'Mündungskrone', 'Muzzle crown', 'barrel', 'trim', 'Blanke Stirnkante', 'vorn am Kompensator',
        'f', (BORE, 0), 610, 616, 15.5, r_in=6, segs=8, bevel=0.6),
    cyl('barrel_nut', 'Laufmutter', 'Barrel nut', 'barrel', 'trim', 'Spannt den Lauf im Gehäuse', 'am Gehäuseende vorn',
        'f', (BORE, 0), 186, 194, 16, segs=24, bevel=0.6),
]
# ---------------------------------------------------------------- Schaft: skelettiert, Schichten
ua = BORE
P += [
    box('stock_joint', 'Schaftverbindung', 'Stock joint', 'stock', 'dark_metal', 'Verbindet Schaft und Gehäuse; Verriegelung',
        'Steckverbindung am Gehäuseende', -131, -119, ua - 22, ua + 20, 30, bevel=R_SMALL),
    cyl('stock_ring', 'Verriegelungsring', 'Lock ring', 'stock', 'trim', 'Sichert die Schaftverbindung', 'auf dem Schaftrohr',
        'f', (ua + 2, 0), -146, -138, 16.5, segs=24, bevel=0.6),
    box('stock_spine', 'Schaftrohr', 'Stock spine', 'stock', 'anodized', 'Trägt die Schulterstütze in Linie mit dem Lauf',
        'in der Schaftverbindung', -212, -130, ua - 12, ua + 16, 28, bevel=R_MID,
        cuts=[dict(shape='cyl', axis='x', c=(-196 + 22 * i, ua + 2), a0=-20, a1=20, r=5.5, segs=16) for i in range(3)]),
    prof('stock', 'Schulterstütze', 'Buttstock', 'stock', 'shell', 'Skelettierte Schulterstütze', 'auf dem Schaftrohr',
         [(-206, ua - 14), (-206, ua + 22), (-276, ua + 24), (-284, ua + 18), (-284, ua - 78), (-272, ua - 84)], 36,
         cuts=[dict(shape='prof', pts=[(-216, ua - 6), (-216, ua + 10), (-266, ua + 12), (-272, ua - 60), (-262, ua - 62)], w=50)]),
    cyl('buffer_body', 'Puffergehäuse', 'Buffer body', 'stock', 'anodized', 'Hydraulischer Rückstoßpuffer, im Durchbruch sichtbar',
        'zwischen Schaftrohr und Schaftkappe', 'f', (ua - 24, 0), -246, -214, 6.5, segs=20, bevel=R_FINE),
    cyl('buffer_rod', 'Pufferstange', 'Buffer rod', 'stock', 'trim', 'Kolbenstange des Puffers', 'im Puffergehäuse',
        'f', (ua - 24, 0), -276, -244, 3.0, segs=16, bevel=0.4),
    box('cheek_rest', 'Wangenauflage', 'Cheek rest', 'stock', 'rubber', 'Verstellbare Anlage für die Wange',
        'auf zwei Säulen (verstellbar)', -266, -200, ua + 24, ua + 32, 26, bevel=R_MID),
    part('cheek_posts', 'Wangensäulen', 'Cheek posts', 'stock', 'multi', 'trim', 'Tragen die Wangenauflage',
         'in der Schulterstütze', bevel=0.4, items=[dict(shape='cyl', axis='u', c=(fp, 0), a0=ua + 18, a1=ua + 25, r=3.2, segs=12)
                                                    for fp in (-252, -214)]),
    prof('butt_pad', 'Schaftkappe', 'Butt pad', 'stock', 'rubber', 'Rutschfeste Anlage an der Schulter',
         'auf das Schaftende gesteckt', [(-283, ua - 88), (-283, ua + 28), (-296, ua + 26), (-299, ua + 14), (-299, ua - 80), (-296, ua - 86)], 40, bevel=R_MID,
         cuts=[cut_box(-300, -294, ua - 70 + 14 * i, ua - 67 + 14 * i, 44) for i in range(6)]),
    part('stock_cable', 'Leitung', 'Conduit', 'stock', 'tube', 'rubber', 'Versorgt die Anzeige aus dem Schaftakku',
         'Clips am Schaftrohr und Gehäuse', bevel=0, r=2.4,
         path=[(-200, ua - 10, 15), (-170, ua - 18, 18), (-140, ua - 16, 19), (-118, ua - 6, 23), (-104, ua + 4, 23.6)]),
]
PARTS = P
ANCHORS = dict(V1.ANCHORS)
ANCHORS.update(SIGHT_ANCHORS)
ANCHORS['Socket_Muzzle'] = dict(at=(616, BORE, 0), part='muzzle_crown')
# Hülsenauswurf (0.16, Entscheidungsliste 5.4 A): Start in der Mitte des Auswurffensters unter der Klappe port_cover (rechts, x negativ),
# Richtung im Autorenmaß (f, u, x): nach rechts, etwas hoch und vorn (im Zielen fliegt sie so nicht dicht am Auge vorbei). Kein eigener
# Anker (der stünde als Knoten im FBX). Waffen ohne Hülsen (Energie) haben kein Feld EJECT.
EJECT = dict(at=(53, 108, -20), dir=(0.3, 0.4, -1.0), case='rifle',
             src='E: Auswurffenster rechts am Oberen Gehäuse (port_cover), Hülse nach rechts, etwas hoch und vorn')
ACTIONS = {
    'fire_auto': dict(de='Dauerfeuer (Verschluss sichtbar)', frames=30, step=1, keys={
        'trigger': [(0, 0), (3, 1), (27, 1), (30, 0)], 'port_cover': [(0, 0), (4, 1), (30, 1)],
        'bolt_carrier': [(0, 0), (3, 0), (5, 1), (7, 0), (9, 1), (11, 0), (13, 1), (15, 0), (17, 1), (19, 0), (21, 1), (23, 0)]},
        events=[(3, 'shot'), (7, 'shot'), (11, 'shot'), (15, 'shot'), (19, 'shot')], view=(-0.85, -0.25, 0.45)),
    'reload_empty': dict(V1.ACTIONS['reload_empty']),
}
EXPLODE = {'sight': (0, 110, 0), 'ammo': (30, -140, 0), 'stock': (-110, 0, 0), 'barrel': (140, 0, 0), 'support': (70, 0, 0),
           'grip_controls': (-10, -80, 0), 'mechanism': (0, 0, -90), 'receiver': (0, 0, 0)}
