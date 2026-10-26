"""BASIC-06 v2.1 – Maschinenpistole im Stil v2.1 („Destiny-Detaildichte + AAA-Material, schlicht“), Familie des Piloten BASIC-01 v2.1.

Recherche (docs/quellen.md › Q-D2-IMG, beobachtet 25.10.2026): Parabellum und New City (kompakter Kastenvorbau über dem Lauf,
geschlossener Bügel vom Abzug zum Vordergriff, langes Magazin im Griff, kurzer Schaft), The Recluse (schlank, großer Bügel als
Handstütze). Nur Prinzipien; Leitmerkmal 06 nach Designvertrag: Magazin im Griff, Vordergriff.

Formsprache-Checkliste (stilhandbuch §3):
| Frage | Maschinenpistole v2.1 |
|---|---|
| Leitmerkmal der Silhouette | kurzer Kastenvorbau, geschlossener Bügel vom Abzug zum Vordergriff, langes Magazin im Griff |
| Schichten | Oberes Gehäuse (Creme) → Seitenpaneele; Unteres Gehäuse (Graphit); Vorbau (Graphit) mit Creme-Deckleiste |
| Negativraum | Bügel umschließt den Raum für die Stützhand; Lüftungsschlitze quer durch den Vorbau |
| Blickfang | Munitionsanzeige links (eine Leuchtfunktion) |
| Zweiton-Blockung | Oberteil und Deckleiste Lack (`shell`), Unterteil, Vorbau, Griffe Polymer (`graphite`/`rubber`); Abzugsbügel und Bügel ein Band (`anodized`) |
| Grafik | ein Chevronband am Vorbau, ein Schriftzug „BASIC SM-06“ |
| Front | flache Vorbaustirn mit Mündungsmulde, kurzer Kompensator mit blanker Krone |
| Übergänge | Bügel geht aus dem Abzugsbügel hervor und endet im Vordergriff; Magazin tritt unten aus dem Griffboden |
| Ergonomie | Griff BGM-1 in v2.1-Form, Vordergriff mit Fingerauflagen, Magazin auf der Griffachse mit Sichtfenster (Patronen) unter dem Griffboden |

Visier: offenes Holo nach Visier-Standard 3 (`SIGHT_KIND['submachine_gun'] = 'holo'`), Absehen-Vorgabe `dot`.
Schlichtheitsbudget: Leuchten 2 Funktionen (Munitionsanzeige, Visier-Emitter mit Absehen) · Grafik 1 Band · Schrift 1 · Orange 3
(Ladehebel, Feuerwahl, Magazinhalter) · Schrauben nur an Paneelen und Vorbau.
Status: Maße entworfen (Länge an Toolgen-Bezug 0,616 m angelehnt; gemessen 0,547 m, spec.json), Formprinzipien abgeleitet aus den Bildreferenzen.
"""
import math

from basic.common import (part, prof, box, cyl, rot, rail, rifle_mag, selector, charging_handle, cut_box, screws, mirror,
                          grip_v21, reflex_sight_v21, stock_s1, R_BODY, R_MID, R_SMALL, R_FINE)
from basic.reticles import DEFAULTS as RETICLE_DEFAULTS
from basic.weapons import w06_submachine_gun as V1

META = dict(V1.META, variant='v2.1', name='Kurzläufer v2.1', nick='Familie v2.1',
            summary='Kompakte Maschinenpistole mit Magazin im Griff, Bügel-Vordergriff und Kastenvorbau (Stil v2.1).')
ASSEMBLIES = V1.ASSEMBLIES
BORE = 82
TOP = 113            # Oberkante Gehäuse / Schiene (Visierhöhe 65 mm)
FR0, FR1 = 171, 292       # Vorbau

P = []
# ---------------------------------------------------------------- Gehäuse
P += [
    prof('upper', 'Oberes Gehäuse', 'Upper receiver', 'receiver', 'shell', 'Tragkörper für Verschluss, Schiene und Vorbau',
         'mit Unterem Gehäuse verbolzt', [(-92, 70), (170, 70), (170, TOP), (-82, TOP), (-92, 102)], 40,
         cuts=[cut_box(30, 80, 76, 98, 16, x=-20),                        # Auswurffenster rechts
               cut_box(-74, -40, 92, 102, 10, x=20),                      # Ladehebel-Nut links
               cut_box(-80, -12, 74, 88, 3.0, x=20.6), cut_box(-80, -12, 74, 88, 3.0, x=-20.6)]),
    prof('lower', 'Unteres Gehäuse', 'Lower receiver', 'receiver', 'graphite', 'Griffmodul, Abzugsgruppe, Magazinschacht im Griff',
         'unter dem Oberen Gehäuse, Fuge 1 mm', [(-92, 54), (-46, 40), (140, 40), (168, 56), (168, 69), (-92, 69)], 38),
    box('side_panel_l', 'Seitenpaneel links', 'Side panel left', 'receiver', 'anodized', 'Wartungsdeckel über der Mechanik',
        'in die Mulde geschraubt (4 Schrauben)', -78, -14, 76, 86, 1.2, bevel=R_FINE, x=19.2),
    box('side_panel_r', 'Seitenpaneel rechts', 'Side panel right', 'receiver', 'anodized', 'Wartungsdeckel über der Mechanik',
        'in die Mulde geschraubt (4 Schrauben)', -78, -14, 76, 86, 1.2, bevel=R_FINE, x=-19.2),
    part('panel_screws', 'Paneelschrauben', 'Panel screws', 'receiver', 'multi', 'trim', 'Halten die Seitenpaneele',
         'in den Paneelen', bevel=0.2, items=mirror(screws([(-74, 78), (-74, 84), (-18, 78), (-18, 84)], 19.8, r=1.4, h=0.8))),
    box('counter_bezel', 'Anzeigenrahmen', 'Counter bezel', 'receiver', 'anodized', 'Fasst die Munitionsanzeige',
        'auf das Obere Gehäuse geschraubt', 92, 132, 92, 104, 2.4, bevel=0.6, x=20.6),
    box('ammo_counter', 'Munitionsanzeige', 'Ammo counter', 'receiver', 'energy', 'Füllstand; Blickfang links',
        'im Anzeigenrahmen', 96, 128, 94.5, 101.5, 1.0, bevel=0.2, x=21.6),
    box('bolt', 'Verschluss', 'Bolt', 'mechanism', 'metal', 'Lädt und verriegelt; läuft beim Schuss zurück', 'im Gehäuse geführt',
        -20, 86, 78, 96, 20, bevel=R_SMALL, move=dict(kind='translate', pivot=(40, 87, 0), vector_mm=(-30, 0, 0), event='fire')),
    prof('port_cover', 'Auswurfklappe', 'Ejection port cover', 'mechanism', 'anodized', 'Deckt das Auswurffenster ab',
         'Scharnier an der Unterkante', [(30, 76), (80, 76), (80, 98), (30, 98)], 1.6, bevel=R_FINE, x=-20.6,
         move=dict(kind='rotate', pivot=(55, 76, -21), axis='f', range_deg=(0, 75), event='fire',
                   expect=((55, 98, -21), (0, 0, -1)))),
    part('mag_release', 'Magazinhalter', 'Magazine release', 'grip_controls', 'cyl', 'accent', 'Löst das Magazin im Griff',
         'Druckknopf links am Griff', bevel=R_FINE, axis='x', c=(16, 30), a0=15, a1=19, r=4.5, segs=20,
         move=dict(kind='translate', pivot=(16, 30, 17), vector_mm=(0, 0, -2.5), event='reload')),
]
P += [dict(p, mat='anodized') for p in rail(-60, 150, TOP)]
P[-1]['cuts'] = [cut_box(-54 + 14 * i, -47 + 14 * i, TOP + 4, TOP + 9, 30) for i in range(14)]
_sight, SIGHT_ANCHORS = reflex_sight_v21(-10, TOP + 8, reticle_kind=RETICLE_DEFAULTS['submachine_gun']['optic'])
P += _sight
# ---------------------------------------------------------------- Vorbau (Graphit), Deckleiste, Lauf, Mündung
_recess = dict(shape='cyl', axis='f', c=(BORE, 0), a0=FR1 - 18, a1=FR1 + 10, r=13, segs=32)
P += [
    prof('shroud', 'Vorbau', 'Barrel shroud', 'support', 'graphite', 'Kurzer Kastenvorbau um den Lauf; Griffbereich vorn',
         'am Oberen Gehäuse verschraubt, Fuge 1 mm', [(FR0, 58), (FR1 - 8, 58), (FR1, 66), (FR1, 100), (FR1 - 6, 106), (FR0, 106)], 38,
         cuts=[_recess] + [cut_box(196 + 16 * i, 204 + 16 * i, 84, 96, 60) for i in range(4)]),        # Schlitze quer durch
    prof('shroud_cap', 'Deckleiste', 'Shroud top cover', 'support', 'shell', 'Creme-Deckleiste auf dem Vorbau; zweite Schicht',
         'auf den Vorbau gesetzt, Stufe 2 mm', [(FR0 + 2, 105), (FR1 - 8, 105), (FR1 - 3, 101), (FR1 - 2, 108), (FR0 + 2, 109)], 34,
         bevel=R_SMALL),
    part('shroud_screws', 'Vorbauschrauben', 'Shroud screws', 'support', 'multi', 'trim', 'Halten den Vorbau', 'seitlich',
         bevel=0.2, items=mirror(screws([(180, 66), (180, 98)], 19.4, r=1.6, h=0.8))),
    part('band_side', 'Chevronband', 'Chevron band', 'support', 'multi', 'accent', 'Lackiertes Band (einziges Grafikelement)',
         'lackiert', bevel=0, items=[dict(shape='prof', pts=[(262 + o, 64), (270 + o, 64), (278 + o, 82), (270 + o, 100), (262 + o, 100),
                                                             (270 + o, 82)], w=0.3, x=sx * 19.15) for o in (0,) for sx in (1, -1)]),
    part('text_l', 'Schriftzug', 'Lettering', 'receiver', 'text', 'decal', 'Kennung „BASIC SM-06“ (einzige Schrift)',
         'aufgedruckt', bevel=0, text='BASIC  SM-06', size=4.2, f=100, u=86, x=20.05, side=1, depth=0.12),
    cyl('barrel', 'Lauf', 'Barrel', 'barrel', 'metal', 'Führt das Geschoss', 'im Gehäuse verschraubt', 'f', (BORE, 0), 160, 300, 7.5,
        segs=24),
    cyl('muzzle', 'Kompensator', 'Compensator', 'barrel', 'anodized', 'Kurzer Kompensator mit Schlitzen; sitzt in der Stirnmulde',
        'auf Laufende geschraubt (lösbar)', 'f', (BORE, 0), FR1 - 14, FR1 + 30, 11, r_in=5, segs=8, bevel=R_SMALL, iface='BMZ-15',
        cuts=[cut_box(FR1 + 8 + 7 * i, FR1 + 12 + 7 * i, BORE + 4, BORE + 14, 10) for i in range(3)]),
    cyl('muzzle_crown', 'Mündungskrone', 'Muzzle crown', 'barrel', 'trim', 'Blanke Stirnkante', 'vorn am Kompensator',
        'f', (BORE, 0), FR1 + 29, FR1 + 34, 10, r_in=5.5, segs=8, bevel=0.6),
]
# ---------------------------------------------------------------- Griff, Magazin im Griff, Bügel, Vordergriff
P += grip_v21(top=40)
P += selector(-26, 62, x=20.5)
P += [dict(p, id='selector_r', de='Feuerwahlhebel rechts', en='Fire selector right', x=-20.5) for p in selector(-26, 62)]
P += charging_handle(-72, 97, x=20.5, travel=42)
_mc = (9, 40)                       # Magazinachse = Griffachse (Runde 1: saß 11 mm dahinter und stand hinten aus dem Griff)
_m = rifle_mag(-6, 40, depth=30, length=165, tilt=-15, w=22, curve=0)
_win_u = [-92 - 5.4 * i for i in range(5)]                     # Patronen im Fenster (unterhalb des Griffbodens)
for p in _m:
    if p['id'] == 'magazine':
        p['de'], p['func'] = 'Magazin im Griff', 'Langes Magazin im Griff; tritt unten aus dem Griffboden; entnehmbar'
        p['cuts'] = [dict(shape='prof', pts=rot([(1, -88), (17, -88), (17, -116), (1, -116)], _mc, -15), w=8, x=10)]
    if p['id'] == 'magazine_base':
        p['mat'] = 'anodized'
    if p['id'] == 'magazine_round':
        p['mat'] = 'brass'
P += _m
P += [
    part('mag_rounds', 'Patronen im Fenster', 'Visible rounds', 'ammo', 'multi', 'brass', 'Zeigt den Füllstand', 'im Magazin',
         bevel=0.3, parent_part='magazine', smooth=True,
         items=[dict(shape='cyl', axis='f', c=(rot([(9, u)], _mc, -15)[0][1], 4 if i % 2 else -2),
                     a0=rot([(9, u)], _mc, -15)[0][0] - 12, a1=rot([(9, u)], _mc, -15)[0][0] + 12, r=4.4, segs=12)
                for i, u in enumerate(_win_u)]),
]
for p in P:
    if p['id'] == 'trigger_guard':      # Runde 1: Bügel wirkte wie Draht – Abzugsbügel und Bügel als ein Band, 9–13 mm hoch
        _g0, _g1 = 40 * math.tan(math.radians(15)) + 18, 40 * math.tan(math.radians(15)) + 72     # wie grip_rifle(top=40)
        p.update(pts=[(_g0 - 4, 4), (_g1, 4), (_g1, 41), (_g1 - 7, 41), (_g1 - 7, 13), (_g0 - 2, 13)], w=14)
P += [
    prof('loop', 'Bügel', 'Support loop', 'support', 'anodized', 'Verbindet Abzugsbügel und Vordergriff; umschließt die Stützhand',
         'am Abzugsbügel und am Vordergriff (fest)', [(70, 4), (213, -7), (213, 6), (70, 13)], 14, bevel=R_SMALL),
    prof('foregrip', 'Vordergriff', 'Foregrip', 'support', 'graphite', 'Senkrechter Griff der Stützhand; Socket_SupportHand',
         'unter den Vorbau geschraubt', [(214, 58), (246, 58), (244, 30), (248, 20), (244, 8), (246, -6), (236, -12), (216, -12),
                                         (212, -4)], 26, bevel=R_BODY),
    prof('foregrip_pad', 'Griffpolster', 'Grip pad', 'support', 'rubber', 'Rutschfeste Front des Vordergriffs', 'vorn aufgeklebt',
         [(242, 50), (247, 50), (245, -4), (240, -4)], 22, bevel=R_FINE),
]
P += stock_s1(-92, BORE, s=0.72, cheek=False)
PARTS = P
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip', note='Haupthand, auf der Griffachse'),
    'Socket_SupportHand': dict(at=(230, 24, 0), part='foregrip', note='Mitte Vordergriff'),
    'Socket_Muzzle': dict(at=(FR1 + 34, BORE, 0), part='muzzle_crown', note='Stirn der Mündungskrone auf der Laufachse'),
    'Socket_MagWell': dict(at=(9, 40, 0), part='grip', note='Magazinschacht im Griff'),
    'Socket_Charge': dict(at=(-60, 97, 25), part='charging_handle', note='Griffpunkt Ladehebel für die Stützhand'),
}
ANCHORS.update(SIGHT_ANCHORS)
# Hülsenauswurf (0.18, wie BASIC-01 seit 0.16): Mitte des Auswurffensters unter der Klappe port_cover (rechts), Kurzpatrone, nach rechts,
# etwas hoch und vorn
EJECT = dict(at=(55, 87, -20), dir=(0.3, 0.4, -1.0), case='pistol',
             src='E: Auswurffenster rechts am Oberen Gehäuse (port_cover), Hülse nach rechts, etwas hoch und vorn (wie BASIC-01)')
# Ego-Griffe (0.18, basic/arms/ego.profile): Autorenmaß dieser Waffe wie ego.GRIPS der Pilotwaffe. contact = Mitte der Handfläche auf der
# Oberfläche, palm = Richtung in das Bauteil, fingers = Fingerrichtung; part = Bauteil, an dem der Griff hängt.
EGO_GRIPS = {
    'grip':    dict(contact=(-3, -6, -16.5), palm=(0.15, 0.0, 1.0), fingers=(1.0, -0.06, 0.0), fingers_pose='trigger',
                    src='E wie die Pilotwaffe (Griff BGM-1 v2.1, gleiche Lage zu Socket_Hand)'),
    'support': dict(contact=(226, 26, 14.5), palm=(0.15, 0.0, -1.0), fingers=(1.0, -0.12, 0.0), fingers_pose='grip',
                    src='E links am Vordergriff, Finger umfassen ihn von hinten nach vorn (Socket_SupportHand)'),
    'mag':     dict(part='magazine', contact=(-24, -96, 12.5), palm=(0.0, 0.0, -1.0), fingers=(1.0, 0.2, 0.0), fingers_pose='mag_hold',
                    src='E links am Magazin unter dem Griffboden, Hand greift von unten hinten (wie die Pilotwaffe)'),
    'charge':  dict(part='charging_handle', contact=(-60, 88, 28), palm=(0.0, 0.0, -1.0), fingers=(0.45, 0.9, 0.0),
                    fingers_pose='pinch', src='E am Ladehebel links (Socket_Charge), wie die Pilotwaffe'),
}
EGO_LIVE = dict(trigger='trigger', bolt='bolt', port='port_cover')     # Abzug, Verschluss, Auswurfklappe im laufenden Feuer
ACTIONS = {
    'fire_auto': dict(de='Dauerfeuer (Verschluss, Auswurfklappe)', frames=24, step=1, keys={
        'trigger': [(0, 0), (2, 1), (20, 1), (23, 0)], 'port_cover': [(0, 0), (3, 1), (24, 1)],
        'bolt': [(0, 0), (2, 0), (3, 1), (4, 0), (5, 1), (6, 0), (7, 1), (8, 0), (10, 1), (11, 0), (12, 1), (13, 0)]},
        events=[(2, 'shot'), (5, 'shot'), (7, 'shot'), (10, 'shot'), (12, 'shot')], view=(-0.85, -0.25, 0.45)),
    'reload_empty': dict(V1.ACTIONS['reload_empty']),
}
EXPLODE = {'sight': (0, 100, 0), 'ammo': (0, -150, 0), 'stock': (-100, 0, 0), 'barrel': (130, 0, 0), 'support': (60, -60, 0),
           'grip_controls': (-10, -80, 0), 'mechanism': (0, 0, -90), 'receiver': (0, 0, 0)}
