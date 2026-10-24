"""BASIC-01 Automatikgewehr (Auto Rifle) – Formstudie 01.

Inspiriert von Formgen KG02 „Kantenläufer“ (lange lesbare Hauptform, Creme/Graphit); eigene Konstruktion:
zweiteiliges Gehäuse mit Fuge, Griffmodul BGM-1, Schiene BRI-22 mit kleinem Reflexvisier, Gewehrmagazin im Schacht,
Handschutz mit Kühlflächen, Lauf mit Mündungsbremse. Orange nur an drei Bedienelementen.
"""
from basic.common import (part, rot, stock_s1, grip_rifle, selector, rail, reflex_sight, rifle_mag, barrel, charging_handle,
                          R_BODY, R_MID, R_SMALL, R_FINE)

META = dict(id='BASIC-01', num='01', type='auto_rifle', type_de='Automatikgewehr', type_en='Auto Rifle',
            name='Formstudie 01', nick='Standard', ammo='primary', fire='full_auto',
            reference_length_m=0.934, reference_length_source='Toolgen 0.13 assault_rifle (Formgen KG02 spec units)',
            inspired_by='Formgen KG02 „Kantenläufer“ (Variante G)',
            summary='Schlichtes Automatikgewehr: Dauerfeuer, Kastenmagazin, kleines Reflexvisier.')

ASSEMBLIES = [
    dict(id='receiver', de='Hauptgehäuse', en='Receiver'),
    dict(id='barrel', de='Lauf', en='Barrel'),
    dict(id='ammo', de='Munitionsversorgung', en='Ammunition feed'),
    dict(id='sight', de='Visier', en='Sight'),
    dict(id='grip_controls', de='Griff und Bedienung', en='Grip and controls'),
    dict(id='support', de='Stützbereich', en='Support'),
    dict(id='stock', de='Schaft', en='Stock'),
    dict(id='mechanism', de='Bewegliche Mechanik', en='Moving mechanism'),
]

BORE = 106          # Laufachse (mm über Socket_Hand)
RAIL_U = 135        # Oberkante Oberes Gehäuse = Unterkante Schiene

PARTS = []
PARTS += [
    part('upper', 'Oberes Gehäuse', 'Upper receiver', 'receiver', 'prof', 'shell',
         'Tragkörper für Lauf, Verschluss und Schiene', 'mit Unterem Gehäuse über zwei Querbolzen (fest)', bevel=R_BODY,
         pts=[(-120, 87), (190, 87), (190, 128), (183, 135), (-108, 135), (-120, 125)], w=44),
    part('lower', 'Unteres Gehäuse', 'Lower receiver', 'receiver', 'prof', 'shell',
         'Nimmt Griffmodul, Abzugsgruppe und Magazinschacht auf', 'unter dem Oberen Gehäuse, Fuge 1 mm', bevel=R_BODY,
         pts=[(-120, 64), (-62, 40), (150, 40), (186, 70), (186, 86), (-120, 86)], w=42),
    part('mag_well', 'Magazinschacht', 'Magazine well', 'receiver', 'prof', 'shell',
         'Führt das Magazin; nach unten offen', 'am Unteren Gehäuse angeformt (fest)', bevel=R_MID, iface='BMW-R',
         pts=rot([(84, 27), (134, 27), (134, 42), (84, 42)], (108, 70), 8), w=31),
    part('port_cover', 'Auswurfklappe', 'Ejection port cover', 'mechanism', 'prof', 'dark_metal',
         'Deckt das Auswurffenster rechts ab; öffnet beim ersten Schuss', 'Scharnier an der Unterkante (dreht)', bevel=R_FINE,
         move=dict(kind='rotate', pivot=(50, 97, -23), axis='f', range_deg=(0, 75), event='fire', expect=((50, 121, -23), (0, 0, -1))),
         pts=[(22, 97), (82, 97), (82, 121), (22, 121)], w=1.6, x=-22.6),
    part('ammo_counter', 'Munitionsanzeige', 'Ammo counter', 'receiver', 'box', 'energy',
         'Zeigt den Füllstand; zurückhaltendes Leuchtfeld links hinten', 'in das Obere Gehäuse eingelassen', bevel=0.3,
         f0=-44, f1=-14, u0=112, u1=121, w=1.0, x=22.3),
    part('mag_release', 'Magazinhalter', 'Magazine release', 'grip_controls', 'cyl', 'accent',
         'Löst das Magazin (Daumen der Haupthand)', 'Druckknopf im Unteren Gehäuse links', bevel=R_FINE,
         move=dict(kind='translate', pivot=(74, 60, 21), vector_mm=(0, 0, -2.5), event='reload'),
         axis='x', c=(74, 60), a0=19, a1=23.5, r=5, segs=20),
]
PARTS += rail(-100, 176, RAIL_U)
_sight, SIGHT_ANCHORS, SIGHT_LINE = reflex_sight(-6, RAIL_U + 8)
PARTS += _sight
PARTS += grip_rifle(top=42)
PARTS += selector(8, 70, x=22.5)
PARTS += [dict(p, id='selector_r', de='Feuerwahlhebel rechts', en='Fire selector right', x=-22.5) for p in selector(8, 70)]
PARTS += rifle_mag(88, 72, depth=40, length=142, tilt=8, w=24)
PARTS += [
    part('handguard', 'Handschutz', 'Handguard', 'support', 'prof', 'graphite',
         'Griffbereich der Stützhand; trägt Socket_SupportHand', 'am Oberen Gehäuse verschraubt, Fuge 1 mm', bevel=R_BODY,
         pts=[(191, 64), (408, 64), (424, 80), (424, 122), (414, 129), (191, 129)], w=46),
    part('handguard_cap', 'Handschutzkappe', 'Handguard end cap', 'support', 'prof', 'dark_metal',
         'Stirnabschluss; Lauf tritt mittig aus, Hitzeschutz', 'auf das Handschutzende gesteckt (fest)', bevel=R_MID,
         pts=[(425, 80), (436, 84), (436, 118), (425, 122)], w=40),
]
for i, f0 in enumerate((262, 300, 338, 376)):
    for side, x in (('l', 22.9), ('r', -22.9)):
        PARTS.append(part(f'vent_{side}{i + 1}', f'Lüftungsöffnung {"links" if side == "l" else "rechts"} {i + 1}',
                          f'Vent {"left" if side == "l" else "right"} {i + 1}', 'support', 'box', 'dark_metal',
                          'Kühlluft am Lauf vorbei; tiefliegendes Gitter', 'in den Handschutz eingelassen', bevel=R_SMALL,
                          f0=f0, f1=f0 + 26, u0=102, u1=114, w=1.4, x=x))
PARTS += barrel(424, 606, BORE, r=10, muzzle_len=50, muzzle_r=15)
PARTS += stock_s1(-120, BORE)
PARTS += charging_handle(-96, 121, x=22.5, travel=60)

ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip', note='Haupthand, auf der Griffachse'),
    'Socket_SupportHand': dict(at=(282, 95, 0), part='handguard', note='Mitte Handschutz, Stützhand umgreift'),
    'Socket_Muzzle': dict(at=(606, BORE, 0), part='muzzle', note='Stirnfläche Mündungsbremse auf der Laufachse'),
    'Socket_MagWell': dict(at=(108, 70, 0), part='mag_well', note='Einrastpunkt Magazin (Schnittstelle BMW-R)'),
    'Socket_Charge': dict(at=(-83, 121, 27), part='charging_handle', note='Griffpunkt Ladehebel für die Stützhand'),
}
ANCHORS.update(SIGHT_ANCHORS)

# Aktionen der Mechanik (Zeit in Bildern bei 30 fps). Schlüssel je Teil: Anteil 0..1 der Bewegung aus part.move.
# Quelle der Dauer: entworfen (Vorschlag) – gemessene Werte siehe docs/quellen.md.
ACTIONS = {
    'reload_tactical': dict(de='Nachladen mit Restmunition', frames=66, keys={
        'mag_release': [(0, 0), (6, 1), (14, 0)],
        'magazine': [(0, 0), (6, 0), (20, 1), (34, 1), (50, 0)]},
        events=[(6, 'mag_release'), (20, 'mag_out'), (50, 'mag_seated')]),
    'reload_empty': dict(de='Nachladen aus leerem Zustand', frames=84, keys={
        'mag_release': [(0, 0), (6, 1), (14, 0)],
        'magazine': [(0, 0), (6, 0), (18, 1), (34, 1), (50, 0)],
        'charging_handle': [(0, 0), (58, 0), (66, 1), (72, 0)],
        'port_cover': [(0, 1), (84, 1)]},
        events=[(18, 'mag_out'), (50, 'mag_seated'), (66, 'charge'), (72, 'ready')]),
    'fire_auto': dict(de='Dauerfeuer (Mechanik)', frames=30, keys={
        'trigger': [(0, 0), (3, 1), (27, 1), (30, 0)],
        'port_cover': [(0, 0), (4, 1), (30, 1)]},
        events=[(3, 'shot'), (7, 'shot'), (11, 'shot'), (15, 'shot'), (19, 'shot'), (23, 'shot')]),
    'safety': dict(de='Sichern / Entsichern', frames=20, keys={'selector': [(0, 0), (8, 1), (20, 1)],
                                                              'selector_r': [(0, 0), (8, 1), (20, 1)]},
                   events=[(8, 'safe')]),
}
