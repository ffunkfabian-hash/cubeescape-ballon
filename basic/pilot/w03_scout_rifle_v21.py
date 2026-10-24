"""BASIC-03 v2.1 – Scoutgewehr im Stil v2.1 („Destiny-Detaildichte + AAA-Material, schlicht“), Familie des Piloten BASIC-01 v2.1.

Recherche (docs/quellen.md › Q-D2-IMG, beobachtet 24.10.2026): Red Tape (sehr lang und schlank, Lauf mit Unterrohr, kompaktes
Gehäuse), Perses-D (schlanker geschlitzter Handschutz, kräftige mehrstufige Mündungsbremse, ein Farbband). Vouchsafe (Hive-Form)
nicht übernommen. Leitmerkmal 03 nach Designvertrag: schlankes Einteilgehäuse, kurzes Zielfernrohr, Schaft S2.

Formsprache-Checkliste (stilhandbuch §3):
| Frage | Scoutgewehr v2.1 |
|---|---|
| Leitmerkmal der Silhouette | lange, flache Linie: schlankes Einteilgehäuse, langer schmaler Handschutz, Lauf mit Unterrohr, Zielfernrohr |
| Schichten | Einteilgehäuse (Creme) → Seitenpaneele; Handschutz (Graphit) mit 1 mm Fuge; Endkappe |
| Negativraum | Schlitzfenster im Handschutz quer durch (Lauf sichtbar); offener Spalt zwischen Lauf und Unterrohr vor dem Handschutz; Daumenloch im Schaft |
| Blickfang | Zielfernrohr mit orangem Höhenturm und blanker Objektivkante; Ladeanzeige links (eine Leuchtfunktion) |
| Zweiton-Blockung | Gehäuse Lack (`shell`), Handschutz, Griff, Schaft Polymer (`graphite`/`rubber`) |
| Grafik | ein Schrägband vorn am Gehäuse, ein Schriftzug „BASIC SR-03“ |
| Front | dreifach geschlitzte Mündungsbremse mit blanker Krone, kannelierter Lauf, Gasblock mit Unterrohr |
| Übergänge | Magazintrichter im Gehäuse angeformt; Gehäusefront schräg zum Handschutz |
| Ergonomie | Griff BGM-1 in v2.1-Form, kurzes Kastenmagazin (8) mit Sichtfenster, Wangenauflage am Schaft |

Absehen: Vorgabe `chevron` (basic/reticles.py › DEFAULTS) im Zielfernrohr, Glas klar.
Schlichtheitsbudget: Leuchten 2 Funktionen (Ladeanzeige, Absehen) · Grafik 1 Band · Schrift 1 · Orange 3 (Ladehebel, Feuerwahl
beidseitig, Höhenturm) · Schrauben nur an Paneelen, Ringen und Schaft.
Status: Maße entworfen (Länge an Toolgen-Bezug 1,00 m angelehnt), Formprinzipien abgeleitet aus den Bildreferenzen.
"""
from basic.common import (part, prof, box, cyl, rot, rail, rifle_mag, selector, charging_handle, cut_box, screws, mirror,
                          grip_v21, scope_v21, R_BODY, R_MID, R_SMALL, R_FINE)
from basic.reticles import DEFAULTS as RETICLE_DEFAULTS
from basic.weapons import w03_scout_rifle as V1

META = dict(V1.META, variant='v2.1', name='Fernblick v2.1', nick='Familie v2.1',
            summary='Schlankes halbautomatisches Präzisionsgewehr mit Zielfernrohr (Stil v2.1).')
ASSEMBLIES = V1.ASSEMBLIES
BORE = 96
TOP = 122
HG0, HG1 = 201, 476      # Handschutz

P = []
# ---------------------------------------------------------------- Einteilgehäuse
P += [
    prof('receiver', 'Gehäuse', 'Receiver', 'receiver', 'shell', 'Schlankes Einteilgehäuse: Lauf, Schiene, Griffmodul, Schacht',
         'Grundkörper; Magazintrichter angeformt',
         [(-122, 64), (-74, 40), (82, 40), (88, 28), (92, 20), (128, 20), (134, 30), (146, 64), (200, 76), (200, 116), (194, TOP),
          (-112, TOP), (-122, 114)], 38,
         cuts=[cut_box(20, 70, 86, 106, 16, x=-19),                         # Auswurffenster rechts
               cut_box(-92, -56, 104, 114, 10, x=19),                       # Ladehebel-Nut links
               cut_box(-96, -20, 82, 98, 3.0, x=19.6), cut_box(-96, -20, 82, 98, 3.0, x=-19.6)]),   # Paneel-Mulden
    prof('mag_well', 'Schachtlippe', 'Magazine well lip', 'receiver', 'trim', 'Blanke Einführkante des Magazintrichters',
         'unten am Trichter des Gehäuses', [(91, 17.5), (129, 17.5), (130, 21), (90, 21)], 39, bevel=0.6, iface='BMW-R'),
    box('side_panel_l', 'Seitenpaneel links', 'Side panel left', 'receiver', 'anodized', 'Wartungsdeckel über der Mechanik',
        'in die Mulde geschraubt (4 Schrauben)', -94, -22, 84, 96, 1.2, bevel=R_FINE, x=18.2),
    box('side_panel_r', 'Seitenpaneel rechts', 'Side panel right', 'receiver', 'anodized', 'Wartungsdeckel über der Mechanik',
        'in die Mulde geschraubt (4 Schrauben)', -94, -22, 84, 96, 1.2, bevel=R_FINE, x=-18.2),
    part('panel_screws', 'Paneelschrauben', 'Panel screws', 'receiver', 'multi', 'trim', 'Halten die Seitenpaneele',
         'in den Paneelen', bevel=0.2, items=mirror(screws([(-90, 87), (-90, 93), (-26, 87), (-26, 93)], 18.8, r=1.5, h=0.8))),
    box('top_cover', 'Deckplatte', 'Top cover', 'receiver', 'shell', 'Staubschutz über dem Verschluss; zweite Schicht',
        'auf das Gehäuse gesetzt, Stufe 3 mm', -112, -66, TOP - 1, TOP + 3, 32, bevel=R_SMALL),
    box('top_cover_trim', 'Deckplatten-Kante', 'Top cover trim', 'receiver', 'trim', 'Blanke Zierkante der Deckplatte',
        'vorn an der Deckplatte', -70, -65, TOP - 1, TOP + 3.6, 33, bevel=0.4),
    box('chamber_pip', 'Ladeanzeige', 'Chamber indicator', 'receiver', 'energy', 'Leuchtet, wenn eine Patrone im Lager ist',
        'links über dem Lager eingelassen', 72, 86, 106, 110, 1.0, bevel=0.3, x=19.4),
    box('pip_bezel', 'Anzeigenrahmen', 'Indicator bezel', 'receiver', 'anodized', 'Fasst die Ladeanzeige', 'aufgeschraubt',
        68, 90, 104, 112, 2.0, bevel=0.5, x=18.8),
    part('band_side', 'Schrägband', 'Slanted band', 'receiver', 'multi', 'accent', 'Lackiertes Band (einziges Grafikelement)',
         'lackiert', bevel=0, items=[dict(shape='prof', pts=[(170, 96), (182, 96), (188, 121.5), (176, 121.5)], w=0.3,
                                          x=sx * 19.15) for sx in (1, -1)]),
    part('text_l', 'Schriftzug', 'Lettering', 'receiver', 'text', 'decal', 'Kennung „BASIC SR-03“ (einzige Schrift)',
         'aufgedruckt', bevel=0, text='BASIC  SR-03', size=4.6, f=100, u=113, x=19.05, side=1, depth=0.12),
    box('bolt', 'Verschluss', 'Bolt', 'mechanism', 'metal', 'Lädt und verriegelt; läuft beim Schuss zurück', 'im Gehäuse geführt',
        -30, 66, 88, 104, 22, bevel=R_SMALL, move=dict(kind='translate', pivot=(20, 96, 0), vector_mm=(-34, 0, 0), event='fire')),
    prof('port_cover', 'Auswurfklappe', 'Ejection port cover', 'mechanism', 'anodized', 'Deckt das Auswurffenster ab',
         'Scharnier an der Unterkante', [(20, 86), (70, 86), (70, 106), (20, 106)], 1.6, bevel=R_FINE, x=-19.6,
         move=dict(kind='rotate', pivot=(45, 86, -20), axis='f', range_deg=(0, 75), event='fire',
                   expect=((45, 106, -20), (0, 0, -1)))),
]
P += [dict(p, mat='anodized') for p in rail(-104, 186, TOP)]
P[-1]['cuts'] = [cut_box(-98 + 14 * i, -91 + 14 * i, TOP + 4, TOP + 9, 30) for i in range(20)]
_scope, SIGHT_ANCHORS, _cu = scope_v21(-48, TOP + 2, reticle_kind=RETICLE_DEFAULTS['scout_rifle']['optic'])
P += _scope
# ---------------------------------------------------------------- Handschutz, Lauf, Unterrohr, Mündung
P += [
    prof('handguard', 'Handschutz', 'Handguard', 'support', 'graphite', 'Griffbereich der Stützhand; lang, schmal, geschlitzt',
         'am Gehäuse verschraubt, Fuge 1 mm', [(HG0, 74), (HG1 - 14, 74), (HG1, 84), (HG1, 112), (HG1 - 8, 116), (HG0, 116)], 32,
         cuts=[cut_box(236 + 38 * i, 262 + 38 * i, 89, 103, 60) for i in range(6)]),           # Schlitzfenster quer durch
    prof('handguard_grip', 'Griffpolster', 'Grip pad', 'support', 'rubber', 'Rutschfeste Zone für die Stützhand',
         'unten auf den Handschutz geklebt', [(230, 70.5), (330, 70.5), (330, 75), (230, 75)], 26, bevel=R_SMALL),
    part('handguard_cap', 'Handschutzkappe', 'Handguard end cap', 'support', 'frame', 'anodized', 'Stirnabschluss mit Laufdurchtritt',
         'auf das Handschutzende gesteckt', bevel=R_SMALL, f0=HG1, f1=HG1 + 8, cu=BORE, ow=28, oh=32, iw=20, ih=20, r_out=7, r_in=9),
    part('handguard_screws', 'Handschutzschrauben', 'Handguard screws', 'support', 'multi', 'trim', 'Halten den Handschutz',
         'seitlich', bevel=0.2, items=mirror(screws([(210, 80), (210, 110)], 16.4, r=1.6, h=0.8))),
    cyl('barrel', 'Lauf', 'Barrel', 'barrel', 'metal', 'Führt das Geschoss; kanneliert', 'im Gehäuse verschraubt',
        'f', (BORE, 0), 196, 676, 7.5, segs=24,
        cuts=[cut_box(500, 600, BORE - 1.3, BORE + 1.3, 4, x=sx * 7.5) for sx in (1, -1)]),
    cyl('gas_tube', 'Unterrohr', 'Gas tube', 'barrel', 'metal', 'Gasrohr unter dem Lauf; offener Spalt vor dem Handschutz',
        'zwischen Handschutz und Gasblock', 'f', (BORE - 16, 0), 300, 606, 4.0, segs=16),
    box('gas_block', 'Gasblock', 'Gas block', 'barrel', 'dark_metal', 'Verbindet Lauf und Unterrohr', 'auf den Lauf geklemmt',
        596, 610, BORE - 22, BORE + 9, 18, bevel=R_SMALL),
    cyl('muzzle', 'Mündungsbremse', 'Muzzle brake', 'barrel', 'anodized', 'Dreifach geschlitzte Bremse; Socket_Muzzle vorn',
        'auf Laufende geschraubt (lösbar)', 'f', (BORE, 0), 670, 718, 12.5, r_in=5, segs=8, bevel=R_SMALL, iface='BMZ-15',
        cuts=[cut_box(680 + 11 * i, 686 + 11 * i, BORE - 6, BORE + 6, 30) for i in range(3)]),
    cyl('muzzle_crown', 'Mündungskrone', 'Muzzle crown', 'barrel', 'trim', 'Blanke Stirnkante', 'vorn an der Bremse',
        'f', (BORE, 0), 716, 721, 11.5, r_in=5.5, segs=8, bevel=0.6),
]
# ---------------------------------------------------------------- Griff, Bedienung, Magazin
P += grip_v21(top=40)
P += selector(4, 62, x=20.5)
P += [dict(p, id='selector_r', de='Feuerwahlhebel rechts', en='Fire selector right', x=-20.5) for p in selector(4, 62)]
P += charging_handle(-90, 109, x=20.5, travel=55)
P.append(part('mag_release', 'Magazinhalter', 'Magazine release', 'grip_controls', 'cyl', 'anodized', 'Löst das Magazin',
              'Druckknopf links', bevel=R_FINE, axis='x', c=(86, 56), a0=17, a1=21.5, r=4.5, segs=20,
              move=dict(kind='translate', pivot=(86, 56, 19), vector_mm=(0, 0, -2.5), event='reload')))
_mc = (110, 62)
_m = rifle_mag(92, 62, depth=36, length=72, tilt=4, w=22, curve=2)
for p in _m:
    if p['id'] == 'magazine':
        p['de'], p['func'] = 'Magazin', 'Kurzes Kastenmagazin (8); entnehmbar'
        p['cuts'] = [dict(shape='prof', pts=rot([(100, 50), (116, 50), (116, 14), (100, 14)], _mc, 4), w=8, x=9.5)]
    if p['id'] == 'magazine_base':
        p['mat'] = 'anodized'
    if p['id'] == 'magazine_round':
        p['mat'] = 'brass'
P += _m
P.append(part('mag_rounds', 'Patronen im Fenster', 'Visible rounds', 'ammo', 'multi', 'brass', 'Zeigt den Füllstand', 'im Magazin',
              bevel=0.3, parent_part='magazine', smooth=True,
              items=[dict(shape='cyl', axis='f', c=(rot([(108, 44 - 6 * i)], _mc, 4)[0][1], 3 if i % 2 else -2),
                          a0=rot([(108, 44 - 6 * i)], _mc, 4)[0][0] - 12, a1=rot([(108, 44 - 6 * i)], _mc, 4)[0][0] + 12, r=4.2,
                          segs=12) for i in range(5)]))
# ---------------------------------------------------------------- Schaft S2 (schlank, Daumenloch, Wangenauflage)
_f0, _ua, _s = -122, BORE, 1.05


def _L(d):
    return _f0 - d * _s


P += [
    prof('stock', 'Schulterstütze S2', 'Stock S2', 'stock', 'graphite', 'Schlanke einteilige Schulterstütze mit Daumenloch',
         'mit zwei Bolzen am Gehäuse (fest)', [(_f0 + 2, _ua - 36), (_f0 + 2, _ua + 26), (_L(60), _ua + 28), (_L(150), _ua + 24),
                                             (_L(158), _ua + 16), (_L(158), _ua - 62), (_L(146), _ua - 68), (_L(60), _ua - 38)],
         30, iface='BST-2',
         cuts=[dict(shape='prof', pts=[(_L(36), _ua - 18), (_L(36), _ua + 8), (_L(116), _ua + 12), (_L(132), _ua - 2),
                                       (_L(128), _ua - 44), (_L(74), _ua - 28)], w=50)]),
    part('stock_bolts', 'Schaftbolzen', 'Stock bolts', 'stock', 'multi', 'trim', 'Halten den Schaft am Gehäuse',
         'quer durch den Schaftansatz', bevel=0.3, items=mirror(screws([(_f0 - 12, _ua + 16), (_f0 - 12, _ua - 24)], 15.4, r=2.4, h=1.0))),
    prof('cheek_pad', 'Wangenauflage', 'Cheek pad', 'stock', 'rubber', 'Erhöhte Anlage für die Wange (Zielfernrohr)',
         'auf den Schaftrücken geschraubt', [(_L(50), _ua + 27), (_L(142), _ua + 23.5), (_L(142), _ua + 33), (_L(50), _ua + 36)], 24,
         bevel=R_SMALL),
    prof('butt_pad', 'Schaftkappe', 'Butt pad', 'stock', 'rubber', 'Rutschfeste Anlage an der Schulter',
         'auf das Schaftende gesteckt', [(_L(157), _ua - 70), (_L(157), _ua + 26), (_L(168), _ua + 22), (_L(171), _ua + 12),
                                        (_L(171), _ua - 62), (_L(168), _ua - 68)], 34, bevel=R_MID,
         cuts=[cut_box(_L(173), _L(165), _ua - 54 + 14 * i, _ua - 51 + 14 * i, 40) for i in range(6)]),
]
PARTS = P
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip', note='Haupthand, auf der Griffachse'),
    'Socket_SupportHand': dict(at=(300, 90, 0), part='handguard', note='Mitte Handschutz'),
    'Socket_Muzzle': dict(at=(721, BORE, 0), part='muzzle_crown', note='Stirn der Mündungskrone auf der Laufachse'),
    'Socket_MagWell': dict(at=(110, 62, 0), part='mag_well', note='Einrastpunkt Magazin (Schnittstelle BMW-R)'),
    'Socket_Charge': dict(at=(-77, 109, 25), part='charging_handle', note='Griffpunkt Ladehebel für die Stützhand'),
}
ANCHORS.update(SIGHT_ANCHORS)
ACTIONS = {
    'fire_semi': dict(de='Einzelschuss (Verschluss, Ladeanzeige)', frames=12, step=1, keys={
        'trigger': [(0, 0), (2, 1), (6, 1), (9, 0)], 'port_cover': [(0, 0), (3, 1), (12, 1)],
        'bolt': [(0, 0), (2, 0), (3, 1), (6, 0)]}, events=[(2, 'shot')], view=(-0.85, -0.25, 0.45)),
    'reload_empty': dict(V1.ACTIONS['reload_empty']),
}
EXPLODE = {'sight': (0, 120, 0), 'ammo': (30, -140, 0), 'stock': (-110, 0, 0), 'barrel': (160, 0, 0), 'support': (70, -50, 0),
           'grip_controls': (-10, -80, 0), 'mechanism': (0, 0, -90), 'receiver': (0, 0, 0)}
