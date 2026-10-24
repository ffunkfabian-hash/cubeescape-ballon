"""BASIC-02 Impulsgewehr (Pulse Rifle): Dreier-Salve je Abzugsdruck.

Unterschied zum Automatikgewehr: kürzer, Impulskammer als zweigeteilte Laufummantelung (oben Creme, unten Graphit-Handschutz),
drei Salvenanzeigen links an der Kammer, kurzes gerades Magazin, Holo-Visier mit breiterem Fenster.
"""
from basic.common import (prof, box, rot, assemblies, grip_rifle, selector, rail, reflex_sight, rifle_mag, barrel,
                          charging_handle, stock_s1, stock_s2, glow, R_BODY, R_MID, R_FINE)

META = dict(id='BASIC-02', num='02', type='pulse_rifle', type_de='Impulsgewehr', type_en='Pulse Rifle', name='Impuls',
            nick='Standard', ammo='primary', fire='burst_3', reference_length_m=0.862,
            reference_length_source='Toolgen pulse_rifle (Formgen KG03 spec units)',
            summary='Impulsgewehr mit Dreier-Salve, Impulskammer und Holo-Visier.')
ASSEMBLIES = assemblies('receiver', 'barrel', 'ammo', 'sight', 'grip_controls', 'support', 'stock', 'mechanism')
BORE = 100
PARTS = [
    prof('upper', 'Oberes Gehäuse', 'Upper receiver', 'receiver', 'shell', 'Tragkörper für Kammer und Schiene',
         'mit Unterem Gehäuse verbolzt', [(-110, 82), (150, 82), (150, 126), (142, 133), (-100, 133), (-110, 124)], 44),
    prof('lower', 'Unteres Gehäuse', 'Lower receiver', 'receiver', 'shell', 'Griffmodul, Abzug und Magazinschacht',
         'unter dem Oberen Gehäuse, Fuge 1 mm', [(-110, 60), (-60, 38), (100, 38), (140, 62), (140, 81), (-110, 81)], 42),
    prof('mag_well', 'Magazinschacht', 'Magazine well', 'receiver', 'shell', 'Führt das Magazin', 'am Unteren Gehäuse',
         [(76, 26), (122, 26), (122, 40), (76, 40)], 30, bevel=R_MID, iface='BMW-R'),
    prof('pulse_chamber', 'Impulskammer', 'Pulse chamber', 'barrel', 'shell', 'Ummantelt Lauf und Impulsspule; formt die Salve',
         'am Oberen Gehäuse verschraubt, Fuge 1 mm', [(151, 99), (392, 99), (408, 108), (408, 124), (396, 131), (151, 131)], 42),
    prof('handguard', 'Handschutz', 'Handguard', 'support', 'graphite', 'Griffbereich der Stützhand',
         'unter der Impulskammer, Fuge 1 mm', [(151, 64), (360, 64), (378, 80), (378, 98), (151, 98)], 44),
    glow('burst_1', 'Salvenanzeige 1', 'Burst pip 1', 'barrel', 250, 266, 112, 120, x=21.4, func='Leuchtet beim 1. Impuls'),
    glow('burst_2', 'Salvenanzeige 2', 'Burst pip 2', 'barrel', 272, 288, 112, 120, x=21.4, func='Leuchtet beim 2. Impuls'),
    glow('burst_3', 'Salvenanzeige 3', 'Burst pip 3', 'barrel', 294, 310, 112, 120, x=21.4, func='Leuchtet beim 3. Impuls'),
    prof('port_cover', 'Auswurfklappe', 'Ejection port cover', 'mechanism', 'dark_metal', 'Auswurffenster rechts',
         'Scharnier unten', [(30, 92), (84, 92), (84, 116), (30, 116)], 1.6, bevel=R_FINE, x=-22.6,
         move=dict(kind='rotate', pivot=(57, 92, -23), axis='f', range_deg=(0, 75), event='fire', expect=((57, 116, -23), (0, 0, -1)))),
]
PARTS += barrel(400, 500, BORE, r=9, muzzle_len=36, muzzle_r=13)
PARTS += rail(-90, 140, 133)
_s, SA, LINE = reflex_sight(-14, 141, win_w=34, win_h=28)
PARTS += _s
PARTS += grip_rifle(top=40)
PARTS += selector(4, 64, x=22.5)
PARTS += rifle_mag(80, 62, depth=38, length=104, tilt=0, w=24, curve=0)
PARTS += stock_s2(-110, BORE, s=1.1)
PARTS += charging_handle(-86, 118, x=22.5, travel=55)
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip'),
    'Socket_SupportHand': dict(at=(270, 82, 0), part='handguard', note='Mitte Handschutz unter der Kammer'),
    'Socket_Muzzle': dict(at=(500, BORE, 0), part='muzzle'),
    'Socket_MagWell': dict(at=(99, 62, 0), part='mag_well'),
}
ANCHORS.update(SA)
ACTIONS = {
    'fire_burst': dict(de='Dreier-Salve (Mechanik und Anzeige)', frames=24, step=1, keys={
        'trigger': [(0, 0), (2, 1), (16, 1), (19, 0)],
        'burst_1': [(0, 0), (2, 1), (12, 1), (22, 0)], 'burst_2': [(0, 0), (4, 0), (6, 1), (12, 1), (22, 0)],
        'burst_3': [(0, 0), (8, 0), (10, 1), (12, 1), (22, 0)], 'port_cover': [(0, 0), (3, 1), (24, 1)]},
        events=[(2, 'shot'), (6, 'shot'), (10, 'shot'), (23, 'ready')], view=(0.8, -0.3, 0.45)),
    'reload_empty': dict(de='Nachladen aus leerem Zustand', frames=80, keys={
        'magazine': [(0, 0), (16, 1), (32, 1), (48, 0)], 'charging_handle': [(0, 0), (56, 0), (64, 1), (70, 0)]},
        events=[(16, 'mag_out'), (48, 'mag_seated'), (64, 'charge'), (72, 'ready')]),
}
