"""BASIC-13 Granatwerfer (Grenade Launcher, einschüssig, Kipplauf).

Kurzer dicker Abschusslauf am Scharnier vor dem Abzug, Verriegelungshebel oben, Vorderschaft am Lauf, eine Granate im
Patronenlager; zum Laden kippt der Lauf 35° nach unten. Die Trommel-Bauweise bleibt zurückgestellt.
"""
from basic.common import (prof, box, cyl, assemblies, grip_rifle, rail, reflex_sight, stock_s1, stock_s2, R_BODY, R_MID, R_SMALL,
                          R_FINE)

META = dict(id='BASIC-13', num='13', type='grenade_launcher', type_de='Granatwerfer (Kipplauf)',
            type_en='Grenade Launcher (breech-loaded)', name='Kipplauf', nick='Standard', ammo='special', fire='single_shot',
            reference_length_m=0.78, reference_length_source='Formgen KG14 ref_len (Schätzung claude-0.10)',
            reference_note='kurzer Kipplauf für Ego-Lesbarkeit (entworfen); Bezug ist eine Schätzung (Q-FG-02)',
            summary='Einschüssiger Kipplauf-Granatwerfer.')
ASSEMBLIES = assemblies('receiver', 'barrel', 'ammo', 'sight', 'grip_controls', 'support', 'stock', 'mechanism')
BORE = 104
HINGE = (74, 64)
PARTS = [
    prof('frame', 'Rahmen', 'Frame', 'receiver', 'shell', 'Trägt Scharnier, Abzug, Verriegelung und Visier',
         'Grundkörper', [(-100, 50), (50, 50), (84, 56), (84, 72), (52, 76), (40, 134), (-90, 134), (-100, 124)], 48),
    cyl('hinge_pin', 'Scharnierbolzen', 'Hinge pin', 'mechanism', 'dark_metal', 'Drehachse des Kipplaufs',
        'quer im Rahmen', 'x', HINGE, -26, 26, 7, segs=16),
    box('barrel_lug', 'Laufhaken', 'Barrel lug', 'mechanism', 'dark_metal', 'Verbindet Lauf und Scharnier',
        'am Lauf (dreht mit)', 62, 106, 60, 80, 36, bevel=R_SMALL,
        move=dict(kind='rotate', pivot=(HINGE[0], HINGE[1], 0), axis='x', range_deg=(0, -35), event='breech',
                  expect=((390, BORE, 0), (0, -1, 0)))),
    cyl('launch_tube', 'Abschusslauf', 'Launch tube', 'barrel', 'shell', 'Dicker Lauf; nimmt eine Granate auf',
        'am Laufhaken', 'f', (BORE, 0), 46, 392, 30, segs=28, bevel=R_SMALL, r_in=22, parent_part='barrel_lug'),
    cyl('muzzle', 'Mündungsring', 'Muzzle ring', 'barrel', 'dark_metal', 'Verstärkt die Mündung; Socket_Muzzle',
        'auf den Lauf gepresst', 'f', (BORE, 0), 370, 398, 33, segs=28, bevel=R_SMALL, r_in=22, parent_part='barrel_lug'),
    prof('forend', 'Vorderschaft', 'Fore-end', 'support', 'graphite', 'Griff der Stützhand; kippt mit dem Lauf',
         'unter den Lauf geschraubt', [(130, 52), (290, 52), (300, 62), (300, 80), (130, 80), (122, 70)], 40,
         parent_part='barrel_lug'),
    cyl('grenade', 'Granate', 'Grenade', 'ammo', 'dark_metal', 'Eine Granate im Patronenlager',
        'im Lauf (Ruhelage verdeckt)', 'f', (BORE, 0), 50, 140, 20, segs=20, bevel=R_SMALL, parent_part='barrel_lug',
        move=dict(kind='translate', pivot=(95, BORE, 0), vector_mm=(-150, 30, 0), event='load',
                  note='Ruhelage = geladen; die Ladeaktion beginnt außerhalb', removable=True)),
    cyl('grenade_band', 'Zünderring', 'Fuse band', 'ammo', 'accent', 'Kennzeichnet die Granate', 'auf der Granate',
        'f', (BORE, 0), 124, 136, 20.6, segs=20, bevel=R_FINE, parent_part='grenade'),
    prof('latch', 'Verriegelungshebel', 'Breech latch', 'grip_controls', 'accent', 'Entriegelt den Kipplauf (Daumen)',
         'Drehpunkt oben im Rahmen', [(12, 134), (40, 134), (44, 140), (16, 144)], 10, bevel=R_FINE,
         move=dict(kind='rotate', pivot=(20, 136, 0), axis='x', range_deg=(0, 20), event='breech')),
]
PARTS += rail(-90, 30, 134)
_s, SA, LINE = reflex_sight(-80, 142, win_w=34, win_h=30)
PARTS += _s
PARTS += grip_rifle(top=50)
PARTS += stock_s2(-100, BORE - 4, s=0.85)
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip'),
    'Socket_SupportHand': dict(at=(215, 66, 0), part='forend'),
    'Socket_Muzzle': dict(at=(398, BORE, 0), part='muzzle'),
    'Socket_Breech': dict(at=(46, BORE, 0), part='launch_tube', note='Lageröffnung bei gekipptem Lauf'),
}
ANCHORS.update(SA)
ACTIONS = {
    'fire': dict(de='Einzelschuss', frames=12, step=1, keys={'trigger': [(0, 0), (2, 1), (6, 0)]}, events=[(2, 'shot')]),
    'reload': dict(de='Kipplauf öffnen, Granate laden, schließen', frames=80, keys={
        'latch': [(0, 0), (6, 1), (14, 0)], 'barrel_lug': [(0, 0), (6, 0), (18, 1), (56, 1), (66, 0)],
        'grenade': [(0, 0), (18, 0), (24, 1), (34, 1), (48, 0)]},
        events=[(18, 'breech_open'), (24, 'case_out'), (48, 'grenade_in'), (66, 'breech_closed')]),
}
