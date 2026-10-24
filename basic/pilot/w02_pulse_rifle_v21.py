"""BASIC-02 v2.1 – Impulsgewehr im Stil v2.1 („Destiny-Detaildichte + AAA-Material, schlicht“), Familie des Piloten BASIC-01 v2.1.

Recherche (docs/quellen.md › Q-D2-IMG, beobachtet 24.10.2026): Ogma PR6 (geschlossener Vorderbau, flache abgeschrägte Stirn,
eingelassene Mündung), Yesteryear (keilförmig nach vorn abfallende Haube), Veles-X (gestufte Mündung, Zweiton). Nur Prinzipien;
Aufbau bleibt nach Designvertrag konventionell (Leitmerkmal 02: zweigeteilte Impulskammer, Salvenanzeigen, Schaft S2).

Formsprache-Checkliste (stilhandbuch §3):
| Frage | Impulsgewehr v2.1 |
|---|---|
| Leitmerkmal der Silhouette | geschlossene, zweigeteilte Impulskammer mit Keil-Oberseite und abgeschrägter Stirn; Mündung eingelassen |
| Schichten | Oberes Gehäuse → Seitenpaneele; Kammer-Oberschale (Creme) über Handschutz (Graphit), Fuge 1 mm; Deckplatte hinten |
| Negativraum | Kammerfenster beidseitig mit drei Impulsspulen um den Lauf; Daumenloch im Schaft S2 |
| Blickfang | drei Salvenanzeigen über den Spulen (eine Leuchtfunktion), links (Ego-Seite) |
| Zweiton-Blockung | Gehäuse/Kammer Lack (`shell`), Unterteil, Handschutz, Schaft Polymer (`graphite`) |
| Grafik | ein Schrägband an den Kammerseiten, ein Schriftzug „BASIC PR-02“ |
| Front | abgeschrägte Kammerstirn mit Mündungsmulde, dreistufige Mündung mit blanker Krone |
| Übergänge | Magazintrichter im Unterteil angeformt; Kammer schließt mit 1 mm Fuge an das Gehäuse an |
| Ergonomie | Griff BGM-1 in v2.1-Form, gerades kurzes Magazin mit Sichtfenster, Griffpolster am Handschutz |

Absehen: Vorgabe `circle_cross` (basic/reticles.py › DEFAULTS), Glas klar.
Schlichtheitsbudget: Leuchten 2 Funktionen (Salvenanzeige, Visier-Emitter mit Absehen) · Grafik 1 Band · Schrift 1 · Orange 3 (Ladehebel,
Feuerwahl beidseitig, Magazinhalter) · Schrauben nur an Paneelen, Kammer und Schaft.
Status: Maße entworfen (Länge an Toolgen-Bezug 0,862 m angelehnt), Formprinzipien abgeleitet aus den Bildreferenzen.
"""
from basic.common import (part, prof, box, cyl, rot, rail, rifle_mag, selector, charging_handle, cut_box, screws, mirror,
                          grip_v21, reflex_sight_v21, R_BODY, R_MID, R_SMALL, R_FINE)
from basic.reticles import DEFAULTS as RETICLE_DEFAULTS
from basic.weapons import w02_pulse_rifle as V1

META = dict(V1.META, variant='v2.1', name='Impuls v2.1', nick='Familie v2.1',
            summary='Impulsgewehr mit Dreier-Salve, geschlossener Impulskammer und Holo-Visier (Stil v2.1).')
ASSEMBLIES = V1.ASSEMBLIES
BORE = 100
TOP = 130            # Oberkante Gehäuse / Schiene (Visier-Standard: Visierhöhe 68,5 mm)
CH0, CH1 = 151, 460  # Impulskammer: Anfang (Fuge zum Gehäuse) und Stirn

P = []
# ---------------------------------------------------------------- Gehäuse
P += [
    prof('upper', 'Oberes Gehäuse', 'Upper receiver', 'receiver', 'shell', 'Tragkörper für Kammer, Verschluss und Schiene',
         'mit Unterem Gehäuse über zwei Querbolzen (fest)', [(-112, 82), (150, 82), (150, TOP), (-100, TOP), (-112, 124)], 44,
         cuts=[cut_box(22, 74, 92, 116, 18, x=-22),                       # Auswurffenster rechts
               cut_box(-92, -52, 108, 120, 10, x=22),                     # Ladehebel-Nut links
               cut_box(-96, -14, 90, 108, 3.0, x=22.6), cut_box(-96, -14, 90, 108, 3.0, x=-22.6)]),   # Paneel-Mulden
    prof('lower', 'Unteres Gehäuse', 'Lower receiver', 'receiver', 'graphite', 'Griffmodul, Abzugsgruppe, Magazinschacht',
         'unter dem Oberen Gehäuse, Fuge 1 mm; Magazintrichter angeformt',
         [(-112, 62), (-62, 40), (66, 40), (72, 28), (76, 18), (124, 18), (130, 28), (146, 64), (146, 81), (-112, 81)], 42,
         cuts=[cut_box(-100, -70, 64, 76, 4.0, x=21.5), cut_box(-100, -70, 64, 76, 4.0, x=-21.5)]),
    prof('mag_well', 'Schachtlippe', 'Magazine well lip', 'receiver', 'trim', 'Blanke Einführkante des Magazintrichters',
         'unten am Trichter des Unterteils', [(75, 15.5), (125, 15.5), (126, 19), (74, 19)], 43, bevel=0.6, iface='BMW-R'),
    box('side_panel_l', 'Seitenpaneel links', 'Side panel left', 'receiver', 'anodized', 'Wartungsdeckel über der Mechanik',
        'in die Mulde geschraubt (4 Schrauben)', -94, -16, 92, 106, 1.2, bevel=R_FINE, x=21.2),
    box('side_panel_r', 'Seitenpaneel rechts', 'Side panel right', 'receiver', 'anodized', 'Wartungsdeckel über der Mechanik',
        'in die Mulde geschraubt (4 Schrauben)', -94, -16, 92, 106, 1.2, bevel=R_FINE, x=-21.2),
    part('panel_screws', 'Paneelschrauben', 'Panel screws', 'receiver', 'multi', 'trim', 'Halten die Seitenpaneele',
         'in den Paneelen', bevel=0.2, items=mirror(screws([(-90, 95), (-90, 103), (-20, 95), (-20, 103)], 21.8, r=1.6, h=0.8))),
    part('takedown_pins', 'Querbolzen', 'Takedown pins', 'receiver', 'multi', 'metal', 'Verbinden Ober- und Unterteil',
         'quer durch das Gehäuse (lösbar)', bevel=0.4, items=mirror(screws([(-96, 76), (134, 76)], 21.0, r=3.6, h=1.0))),
    box('top_cover', 'Deckplatte', 'Top cover', 'receiver', 'shell', 'Staubschutz über dem Verschluss; zweite Schicht',
        'auf das Obere Gehäuse gesetzt, Stufe 3 mm', -110, -42, TOP - 1, TOP + 3, 38, bevel=R_SMALL),
    box('top_cover_trim', 'Deckplatten-Kante', 'Top cover trim', 'receiver', 'trim', 'Blanke Zierkante der Deckplatte',
        'vorn an der Deckplatte', -46, -41, TOP - 1, TOP + 3.6, 39, bevel=0.4),
    part('mag_release', 'Magazinhalter', 'Magazine release', 'grip_controls', 'cyl', 'accent', 'Löst das Magazin',
         'Druckknopf links', bevel=R_FINE, axis='x', c=(70, 58), a0=19, a1=23.5, r=5, segs=20,
         move=dict(kind='translate', pivot=(70, 58, 21), vector_mm=(0, 0, -2.5), event='reload')),
    box('bolt_carrier', 'Verschlussträger', 'Bolt carrier', 'mechanism', 'metal', 'Lädt und verriegelt; läuft je Impuls zurück',
        'im Oberen Gehäuse geführt', -36, 72, 94, 114, 26, bevel=R_SMALL, cuts=[cut_box(28, 66, 100, 108, 4, x=-13)],
        move=dict(kind='translate', pivot=(20, 104, 0), vector_mm=(-30, 0, 0), event='fire')),
    prof('port_cover', 'Auswurfklappe', 'Ejection port cover', 'mechanism', 'anodized', 'Deckt das Auswurffenster ab',
         'Scharnier an der Unterkante', [(22, 92), (74, 92), (74, 116), (22, 116)], 1.6, bevel=R_FINE, x=-22.6,
         move=dict(kind='rotate', pivot=(48, 92, -23), axis='f', range_deg=(0, 75), event='fire',
                   expect=((48, 116, -23), (0, 0, -1)))),
]
P += [dict(p, mat='anodized') for p in rail(-90, 120, TOP)]
P[-1]['cuts'] = [cut_box(-84 + 14 * i, -77 + 14 * i, TOP + 4, TOP + 9, 30) for i in range(14)]
_sight, SIGHT_ANCHORS = reflex_sight_v21(-12, TOP + 8, ww=34, wh=26,       # Holo-Visier: etwas breiteres Fenster als 01
                                         reticle_kind=RETICLE_DEFAULTS['pulse_rifle']['optic'])
P += _sight
# ---------------------------------------------------------------- Impulskammer (Leitmerkmal): Oberschale + Handschutz
_recess = dict(shape='cyl', axis='f', c=(BORE, 0), a0=CH1 - 22, a1=CH1 + 12, r=16, segs=32)          # Mündungsmulde in der Stirn
_win = [cut_box(240, 340, 104, 121, 60)]                                    # Kammerfenster quer durch (Spulen und Lauf sichtbar)
P += [
    prof('pulse_chamber', 'Impulskammer', 'Pulse chamber', 'barrel', 'shell',
         'Oberschale um Lauf und Impulsspulen; Keil-Oberseite, abgeschrägte Stirn', 'am Oberen Gehäuse verschraubt, Fuge 1 mm',
         [(CH0, 99), (CH1 - 6, 99), (CH1, 104), (CH1 - 12, 121), (340, 129), (200, TOP + 4), (CH0, TOP + 4)], 44, bevel=R_BODY,
         cuts=_win + [_recess, cut_box(CH0 + 30, CH0 + 31, TOP - 2, TOP + 8, 50)]),              # Fuge 1 mm quer über die Oberseite
    prof('handguard', 'Handschutz', 'Handguard', 'support', 'graphite', 'Unterschale der Kammer; Griffbereich der Stützhand',
         'unter der Kammer-Oberschale, Fuge 1 mm', [(CH0, 64), (400, 64), (CH1 - 4, 86), (CH1, 98), (CH0, 98)], 44, bevel=R_BODY,
         cuts=[_recess] + [cut_box(250 + 30 * i, 262 + 30 * i, 70, 90, 8, x=sx * 22) for i in range(3) for sx in (1, -1)]),
    prof('handguard_grip', 'Griffpolster', 'Grip pad', 'support', 'rubber', 'Rutschfeste Zone für die Stützhand',
         'unten auf den Handschutz geklebt', [(214, 60.5), (330, 60.5), (330, 66), (214, 66)], 38, bevel=R_SMALL),
    part('chamber_screws', 'Kammerschrauben', 'Chamber screws', 'barrel', 'multi', 'trim', 'Halten Oberschale und Handschutz',
         'seitlich am Kammeranfang', bevel=0.2, items=mirror(screws([(162, 106), (162, 126), (162, 76)], 22.4, r=1.8, h=0.8))),
    part('pulse_coils', 'Impulsspulen', 'Pulse coils', 'barrel', 'multi', 'dark_metal',
         'Formen die Dreier-Salve; im Kammerfenster sichtbar', 'auf den Lauf gepresst', bevel=0.6, smooth=True,
         items=[dict(shape='cyl', axis='f', c=(BORE, 0), a0=f, a1=f + 14, r=15, r_in=8.5, segs=32) for f in (252, 283, 314)]),
    part('coil_rings', 'Spulenringe', 'Coil rings', 'barrel', 'multi', 'trim', 'Blanke Stirnringe der Spulen', 'an den Spulen',
         bevel=0.3, smooth=True,
         items=[dict(shape='cyl', axis='f', c=(BORE, 0), a0=f, a1=f + 1.6, r=15.6, r_in=12, segs=32) for f in (251, 282, 313)]),
    part('burst_1', 'Salvenanzeige 1', 'Burst pip 1', 'barrel', 'box', 'energy', 'Leuchtet beim 1. Impuls',
         'über der 1. Spule eingelassen', bevel=0.3, f0=252, f1=266, u0=124.5, u1=128, w=1.0, x=23.6,
         move=dict(kind='glow', pivot=None, event='fire', max=5.0)),
    part('burst_2', 'Salvenanzeige 2', 'Burst pip 2', 'barrel', 'box', 'energy', 'Leuchtet beim 2. Impuls',
         'über der 2. Spule eingelassen', bevel=0.3, f0=283, f1=297, u0=124.5, u1=128, w=1.0, x=23.6,
         move=dict(kind='glow', pivot=None, event='fire', max=5.0)),
    part('burst_3', 'Salvenanzeige 3', 'Burst pip 3', 'barrel', 'box', 'energy', 'Leuchtet beim 3. Impuls',
         'über der 3. Spule eingelassen', bevel=0.3, f0=314, f1=328, u0=124.5, u1=128, w=1.0, x=23.6,
         move=dict(kind='glow', pivot=None, event='fire', max=5.0)),
    part('pip_bezel', 'Anzeigenleiste', 'Pip bezel', 'barrel', 'box', 'anodized', 'Fasst die drei Salvenanzeigen',
         'auf die Kammer geschraubt', bevel=0.6, f0=248, f1=332, u0=122.6, u1=129.9, w=2.4, x=22.6),
    part('band_side', 'Schrägband', 'Slanted band', 'barrel', 'multi', 'accent', 'Lackiertes Band (einziges Grafikelement)',
         'lackiert', bevel=0, items=[dict(shape='prof', pts=[(392, 99.5), (406, 99.5), (398, 125.2), (384, 126.8)], w=0.3,
                                           x=sx * 22.15) for sx in (1, -1)]),
    part('text_l', 'Schriftzug', 'Lettering', 'barrel', 'text', 'decal', 'Kennung „BASIC PR-02“ (einzige Schrift)',
         'aufgedruckt', bevel=0, text='BASIC  PR-02', size=5.0, f=360, u=104.5, x=22.05, side=1, depth=0.12),
    cyl('barrel', 'Lauf', 'Barrel', 'barrel', 'metal', 'Führt das Geschoss; kanneliert', 'im Oberen Gehäuse verschraubt',
        'f', (BORE, 0), 150, 470, 8, segs=24,
        cuts=[cut_box(236, 344, BORE - 1.4, BORE + 1.4, 4, x=sx * 8) for sx in (1, -1)]),
    cyl('muzzle', 'Mündung', 'Muzzle', 'barrel', 'anodized', 'Erste Mündungsstufe mit Schlitzen; sitzt in der Stirnmulde',
        'auf Laufende geschraubt (lösbar)', 'f', (BORE, 0), CH1 - 16, CH1 + 26, 14, r_in=5.5, segs=8, bevel=R_SMALL, iface='BMZ-15',
        cuts=[cut_box(CH1 + 6 + 7 * i, CH1 + 10 + 7 * i, BORE + 5, BORE + 18, 12) for i in range(3)]),
    cyl('muzzle_tip', 'Mündungsspitze', 'Muzzle tip', 'barrel', 'dark_metal', 'Zweite, schmalere Stufe', 'vorn auf der Mündung',
        'f', (BORE, 0), CH1 + 26, CH1 + 48, 11, r_in=5, segs=8, bevel=R_SMALL),
    cyl('muzzle_crown', 'Mündungskrone', 'Muzzle crown', 'barrel', 'trim', 'Blanke Stirnkante', 'vorn an der Spitze',
        'f', (BORE, 0), CH1 + 47, CH1 + 52, 10, r_in=5.5, segs=8, bevel=0.6),
]
# ---------------------------------------------------------------- Griff, Bedienung, Magazin
P += grip_v21(top=40)
P += selector(4, 66, x=22.5)
P += [dict(p, id='selector_r', de='Feuerwahlhebel rechts', en='Fire selector right', x=-22.5) for p in selector(4, 66)]
P += charging_handle(-88, 114, x=22.5, travel=55)
_mc = (99, 62)
_m = rifle_mag(80, 62, depth=38, length=104, tilt=4, w=24, curve=0)
for p in _m:
    if p['id'] == 'magazine':
        p['de'], p['func'] = 'Magazin', 'Hält die Patronen; kurz und gerade; entnehmbar'
        p['cuts'] = ([dict(shape='prof', pts=rot([(86, u), (114, u), (114, u + 2.2), (86, u + 2.2)], _mc, 4), w=3, x=sx * 12)
                      for u in (-8, -20) for sx in (1, -1)]
                     + [dict(shape='prof', pts=rot([(92, 50), (110, 50), (110, 6), (92, 6)], _mc, 4), w=8, x=10)])
    if p['id'] == 'magazine_base':
        p['mat'] = 'anodized'
    if p['id'] == 'magazine_round':
        p['mat'] = 'brass'
P += _m
P += [
    prof('mag_band', 'Bodenband', 'Base band', 'ammo', 'metal', 'Metallband über dem Magazinboden; Greifkante', 'am Magazin',
         rot([(79, -34), (119, -34), (119, -40), (79, -40)], _mc, 4), 25, bevel=R_FINE, parent_part='magazine'),
    part('mag_rounds', 'Patronen im Fenster', 'Visible rounds', 'ammo', 'multi', 'brass', 'Zeigt den Füllstand', 'im Magazin',
         bevel=0.3, parent_part='magazine', smooth=True,
         items=[dict(shape='cyl', axis='f', c=(rot([(101, 46 - 5.4 * i)], _mc, 4)[0][1], 4 if i % 2 else -2),
                     a0=rot([(101, 46 - 5.4 * i)], _mc, 4)[0][0] - 13, a1=rot([(101, 46 - 5.4 * i)], _mc, 4)[0][0] + 13, r=4.4,
                     segs=12) for i in range(7)]),
]
# ---------------------------------------------------------------- Schaft S2 (einteilig Graphit, Daumenloch)
_f0, _ua, _s = -112, BORE, 1.12


def _L(d):
    return _f0 - d * _s


P += [
    prof('stock', 'Schulterstütze S2', 'Stock S2', 'stock', 'graphite', 'Einteilige Schulterstütze mit Daumenloch',
         'mit zwei Bolzen am Gehäuse (fest)', [(_f0 + 2, _ua - 40), (_f0 + 2, _ua + 30), (_L(60), _ua + 32), (_L(150), _ua + 28),
                                             (_L(158), _ua + 20), (_L(158), _ua - 72), (_L(146), _ua - 78), (_L(60), _ua - 48)],
         34, iface='BST-2',
         cuts=[dict(shape='prof', pts=[(_L(38), _ua - 20), (_L(38), _ua + 10), (_L(116), _ua + 14), (_L(132), _ua),
                                       (_L(128), _ua - 50), (_L(76), _ua - 34)], w=50)]),
    part('stock_bolts', 'Schaftbolzen', 'Stock bolts', 'stock', 'multi', 'trim', 'Halten den Schaft am Gehäuse',
         'quer durch den Schaftansatz', bevel=0.3, items=mirror(screws([(_f0 - 12, _ua + 18), (_f0 - 12, _ua - 26)], 17.4, r=2.6, h=1.0))),
    prof('cheek_pad', 'Wangenauflage', 'Cheek pad', 'stock', 'rubber', 'Weiche Anlage für die Wange', 'auf den Schaftrücken geklebt',
         [(_L(56), _ua + 31), (_L(140), _ua + 27.5), (_L(140), _ua + 33), (_L(56), _ua + 36.5)], 26, bevel=R_SMALL),
    prof('butt_pad', 'Schaftkappe', 'Butt pad', 'stock', 'rubber', 'Rutschfeste Anlage an der Schulter',
         'auf das Schaftende gesteckt', [(_L(157), _ua - 80), (_L(157), _ua + 30), (_L(168), _ua + 26), (_L(171), _ua + 16),
                                        (_L(171), _ua - 72), (_L(168), _ua - 78)], 38, bevel=R_MID,
         cuts=[cut_box(_L(173), _L(165), _ua - 62 + 14 * i, _ua - 59 + 14 * i, 44) for i in range(6)]),
]
PARTS = P
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip', note='Haupthand, auf der Griffachse'),
    'Socket_SupportHand': dict(at=(290, 80, 0), part='handguard', note='Mitte Handschutz unter der Kammer'),
    'Socket_Muzzle': dict(at=(CH1 + 52, BORE, 0), part='muzzle_crown', note='Stirn der Mündungskrone auf der Laufachse'),
    'Socket_MagWell': dict(at=(99, 62, 0), part='mag_well', note='Einrastpunkt Magazin (Schnittstelle BMW-R)'),
    'Socket_Charge': dict(at=(-75, 114, 27), part='charging_handle', note='Griffpunkt Ladehebel für die Stützhand'),
}
ANCHORS.update(SIGHT_ANCHORS)
ACTIONS = {
    'fire_burst': dict(de='Dreier-Salve (Verschluss, Anzeigen)', frames=24, step=1, keys={
        'trigger': [(0, 0), (2, 1), (16, 1), (19, 0)],
        'burst_1': [(0, 0), (2, 1), (12, 1), (22, 0)], 'burst_2': [(0, 0), (4, 0), (6, 1), (12, 1), (22, 0)],
        'burst_3': [(0, 0), (8, 0), (10, 1), (12, 1), (22, 0)], 'port_cover': [(0, 0), (3, 1), (24, 1)],
        'bolt_carrier': [(0, 0), (2, 0), (3, 1), (5, 0), (6, 0), (7, 1), (9, 0), (10, 0), (11, 1), (13, 0)]},
        events=[(2, 'shot'), (6, 'shot'), (10, 'shot'), (23, 'ready')], view=(0.8, -0.3, 0.45)),
    'reload_empty': dict(V1.ACTIONS['reload_empty']),
}
EXPLODE = {'sight': (0, 110, 0), 'ammo': (30, -140, 0), 'stock': (-110, 0, 0), 'barrel': (140, 0, 0), 'support': (60, -60, 0),
           'grip_controls': (-10, -80, 0), 'mechanism': (0, 0, -90), 'receiver': (0, 0, 0)}
