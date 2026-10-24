"""BASIC-03 Scout-Gewehr (Scout Rifle): halbautomatische Präzisionswaffe.

Lang und schlank: Einteilgehäuse, Schaft S2, kurzes Kastenmagazin (8), kurzes Zielfernrohr, langer schmaler Handschutz.
Unterschied zum Scharfschützen: halbautomatisch, Ladehebel statt Kammerstängel, kürzeres Rohr, kein Unterteil.
"""
from basic.common import (prof, box, assemblies, stock_s2, grip_rifle, selector, rail, scope, rifle_mag, barrel, charging_handle,
                          stock_s1, vents, R_BODY, R_MID, R_FINE)

META = dict(id='BASIC-03', num='03', type='scout_rifle', type_de='Scout-Gewehr', type_en='Scout Rifle', name='Fernblick',
            nick='Standard', ammo='primary', fire='semi_auto', reference_length_m=1.00,
            reference_length_source='Toolgen scout_rifle / Formgen KG11 ref_len (Schätzung claude-0.10)',
            summary='Schlankes halbautomatisches Präzisionsgewehr mit Zielfernrohr.')
ASSEMBLIES = assemblies('receiver', 'barrel', 'ammo', 'sight', 'grip_controls', 'support', 'stock', 'mechanism')
BORE = 96
PARTS = [
    prof('receiver', 'Gehäuse', 'Receiver', 'receiver', 'shell', 'Schlankes Einteilgehäuse: Lauf, Schiene, Griffmodul, Schacht',
         'Grundkörper', [(-120, 62), (-70, 38), (140, 38), (178, 66), (200, 84), (200, 120), (192, 127), (-110, 127), (-120, 118)], 38),
    prof('handguard', 'Handschutz', 'Handguard', 'support', 'graphite', 'Griffbereich der Stützhand; lang und schmal',
         'am Oberen Gehäuse verschraubt, Fuge 1 mm', [(201, 66), (470, 66), (486, 78), (486, 114), (476, 120), (201, 120)], 40),
    prof('port_cover', 'Auswurfklappe', 'Ejection port cover', 'mechanism', 'dark_metal', 'Auswurffenster rechts',
         'Scharnier unten', [(20, 88), (74, 88), (74, 110), (20, 110)], 1.6, bevel=R_FINE, x=-20.6,
         move=dict(kind='rotate', pivot=(47, 88, -21), axis='f', range_deg=(0, 75), event='fire', expect=((47, 110, -21), (0, 0, -1)))),
]
PARTS += vents('vent', 'support', [300, 380], 60, 98, 108, 20.9)
PARTS += barrel(484, 690, BORE, r=8, muzzle_len=34, muzzle_r=12)
PARTS += rail(-100, 190, 127)
_s, SA, LINE = scope(-50, 135, length=160, r_obj=17, r_eye=14, r_tube=10)
PARTS += _s
PARTS += grip_rifle(top=38)
PARTS += selector(4, 62, x=20.5)
PARTS += rifle_mag(92, 62, depth=36, length=72, tilt=4, w=22, curve=2)
PARTS += stock_s2(-120, BORE, s=1.05)
PARTS += charging_handle(-90, 112, x=20.5, travel=55)
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip'),
    'Socket_SupportHand': dict(at=(330, 92, 0), part='handguard'),
    'Socket_Muzzle': dict(at=(690, BORE, 0), part='muzzle'),
    'Socket_MagWell': dict(at=(110, 62, 0), part='receiver'),
}
ANCHORS.update(SA)
ACTIONS = {
    'fire_semi': dict(de='Einzelschuss (Mechanik)', frames=12, step=1, keys={
        'trigger': [(0, 0), (2, 1), (6, 1), (9, 0)], 'port_cover': [(0, 0), (3, 1), (12, 1)]}, events=[(2, 'shot')]),
    'reload_empty': dict(de='Nachladen aus leerem Zustand', frames=80, keys={
        'magazine': [(0, 0), (14, 1), (30, 1), (46, 0)], 'charging_handle': [(0, 0), (56, 0), (64, 1), (70, 0)]},
        events=[(14, 'mag_out'), (46, 'mag_seated'), (64, 'charge'), (72, 'ready')]),
}
