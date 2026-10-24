"""BASIC-08 Schrotflinte (Shotgun): gewöhnliche Streuschrot-Vorderschaftrepetierflinte.

Dicker Lauf über Röhrenmagazin, Graphit-Vorderschaft als Pumpe, Ladeklappe unten, Patronen einzeln geladen, Reflexvisier.
"""
from basic.common import (prof, box, cyl, assemblies, grip_rifle, rail, reflex_sight, stock_s1, R_BODY, R_MID, R_SMALL,
                          R_FINE)

META = dict(id='BASIC-08', num='08', type='shotgun', type_de='Schrotflinte', type_en='Shotgun', name='Streuer',
            nick='Standard', ammo='special', fire='pump_action', reference_length_m=0.904,
            reference_length_source='Toolgen shotgun (Formgen KG04 spec units)',
            summary='Vorderschaftrepetierflinte mit Röhrenmagazin, Streuschrot.')
ASSEMBLIES = assemblies('receiver', 'barrel', 'ammo', 'sight', 'grip_controls', 'support', 'stock', 'mechanism')
BORE = 100
TUBE_U = 66
PARTS = [
    prof('receiver', 'Gehäuse', 'Receiver', 'receiver', 'shell', 'Verschluss, Zuführung und Ladeklappe',
         'Grundkörper', [(-110, 50), (120, 50), (130, 60), (130, 118), (120, 126), (-100, 126), (-110, 116)], 46),
    box('loading_gate', 'Ladeklappe', 'Loading gate', 'ammo', 'dark_metal', 'Öffnung unten zum Einschieben einzelner Patronen',
        'im Gehäuseboden (federnd)', 64, 122, 47, 52, 26, bevel=R_FINE),
    box('ejection_port', 'Auswurffenster', 'Ejection port', 'mechanism', 'dark_metal', 'Hülsenauswurf rechts',
        'im Gehäuse eingelassen', 20, 90, 88, 112, 1.4, bevel=R_SMALL, x=-22.7),
    cyl('barrel', 'Lauf', 'Barrel', 'barrel', 'metal', 'Dicker Glattlauf für Streuschrot', 'im Gehäuse verschraubt',
        'f', (BORE, 0), 128, 556, 14, segs=24),
    cyl('muzzle', 'Mündung', 'Muzzle', 'barrel', 'dark_metal', 'Weite Mündung; Socket_Muzzle', 'Laufende',
        'f', (BORE, 0), 548, 584, 18, bevel=R_SMALL, segs=12, r_in=11),
    cyl('tube_mag', 'Röhrenmagazin', 'Tube magazine', 'ammo', 'dark_metal', 'Hält sechs Patronen unter dem Lauf',
        'unter dem Lauf, Laufschelle vorn', 'f', (TUBE_U, 0), 128, 510, 11, segs=20),
    cyl('tube_cap', 'Magazinkappe', 'Magazine cap', 'ammo', 'graphite', 'Verschließt das Röhrenmagazin', 'aufgeschraubt',
        'f', (TUBE_U, 0), 508, 526, 12.5, bevel=R_SMALL, segs=16),
    box('barrel_clamp', 'Laufschelle', 'Barrel clamp', 'barrel', 'dark_metal', 'Verbindet Lauf und Magazinrohr',
        'auf Lauf und Rohr geklemmt', 470, 488, 56, 114, 22, bevel=R_SMALL),
    prof('pump', 'Vorderschaft (Pumpe)', 'Pump fore-end', 'mechanism', 'graphite',
         'Stützhand repetiert: zurück und vor', 'gleitet auf dem Magazinrohr', [(220, 48), (370, 48), (378, 56), (378, 84),
                                                                               (370, 90), (220, 90), (212, 82), (212, 56)], 40,
         move=dict(kind='translate', pivot=(296, TUBE_U, 0), vector_mm=(-84, 0, 0), event='pump')),
    cyl('shell_round', 'Patrone', 'Shell', 'ammo', 'accent', 'Einzelne Schrotpatrone (beim Laden sichtbar)',
        'wird durch die Ladeklappe ins Rohr geschoben', 'f', (TUBE_U - 2, 0), 70, 130, 9.5, bevel=R_FINE, segs=16,
        move=dict(kind='translate', pivot=(100, TUBE_U - 2, 0), vector_mm=(-30, -70, 0), event='load_shell',
                  note='Ruhelage = im Magazin (verdeckt); Aktion beginnt außen', removable=True)),
]
PARTS += rail(-90, 110, 126)
_s, SA, LINE = reflex_sight(-30, 134, win_w=30, win_h=24)
PARTS += _s
PARTS += grip_rifle(top=48)
PARTS += stock_s1(-110, BORE, s=1.05)
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip'),
    'Socket_SupportHand': dict(at=(296, 70, 0), part='pump', note='bewegt sich mit der Pumpe'),
    'Socket_Muzzle': dict(at=(584, BORE, 0), part='muzzle'),
    'Socket_LoadingGate': dict(at=(93, 48, 0), part='loading_gate', note='Patronen einzeln von unten'),
}
ANCHORS.update(SA)
ACTIONS = {
    'fire_pump': dict(de='Schuss und Repetieren', frames=30, step=1, keys={
        'trigger': [(0, 0), (2, 1), (6, 0)], 'pump': [(0, 0), (8, 0), (14, 1), (22, 0)]},
        events=[(2, 'shot'), (14, 'eject'), (22, 'ready')]),
    'load_shell': dict(de='Eine Patrone laden (wiederholt je Patrone)', frames=24, step=2, keys={
        'shell_round': [(0, 1), (8, 1), (18, 0)]}, events=[(18, 'shell_in')], view=(-0.7, -0.3, -0.55)),
}
