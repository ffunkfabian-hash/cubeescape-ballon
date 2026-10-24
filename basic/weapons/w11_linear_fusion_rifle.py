"""BASIC-11 Lineares Fusionsgewehr (Linear Fusion Rifle): Aufladen, ein gebündelter Präzisionsstrahl.

Offener Beschleuniger: zwei Schienen über und unter dem Linearkern, vier Spulenringe, Stützgriff unter der unteren Schiene,
Zielfernrohr, Energiezelle hinter dem Griff.
"""
from basic.common import (prof, box, cyl, part, assemblies, grip_rifle, rail, scope, energy_cell, stock_s1,
                          R_BODY, R_MID, R_SMALL, R_FINE)

META = dict(id='BASIC-11', num='11', type='linear_fusion_rifle', type_de='Lineares Fusionsgewehr',
            type_en='Linear Fusion Rifle', name='Schienenlicht', nick='Standard', ammo='heavy', fire='charge_single',
            reference_length_m=1.30, reference_length_source='Formgen KG13 ref_len (Schätzung claude-0.10)',
            summary='Offener Linearbeschleuniger mit Zielfernrohr; ein Strahl nach kurzer Ladung.')
ASSEMBLIES = assemblies('receiver', 'barrel', 'ammo', 'sight', 'grip_controls', 'support', 'stock', 'cooling')
BORE = 100
PARTS = [
    prof('receiver', 'Gehäuse', 'Receiver', 'receiver', 'shell', 'Tragkörper; Schienen und Zellenschacht',
         'Grundkörper', [(-150, 48), (200, 48), (222, 66), (222, 134), (210, 142), (-140, 142), (-150, 132)], 48),
    box('rail_top', 'Beschleunigerschiene oben', 'Upper accelerator rail', 'barrel', 'shell', 'Führt das Feld oben',
        'im Gehäuse verankert', 222, 820, 122, 136, 26, bevel=R_MID),
    box('rail_bottom', 'Beschleunigerschiene unten', 'Lower accelerator rail', 'barrel', 'shell', 'Führt das Feld unten',
        'im Gehäuse verankert', 222, 800, 64, 78, 26, bevel=R_MID),
    cyl('linear_core', 'Linearkern', 'Linear core', 'barrel', 'energy', 'Leuchtender Kern; lädt sich sichtbar auf',
        'zwischen den Schienen', 'f', (BORE, 0), 222, 812, 5, bevel=0, segs=12,
        move=dict(kind='glow', pivot=None, event='charge', max=6.0)),
    cyl('muzzle', 'Fokusmündung', 'Focus muzzle', 'barrel', 'dark_metal', 'Bündelt den Strahl; Socket_Muzzle',
        'vor den Schienen', 'f', (BORE, 0), 812, 852, 16, bevel=R_SMALL, segs=12, r_in=7),
    box('muzzle_bridge', 'Mündungsbrücke', 'Muzzle bridge', 'barrel', 'dark_metal', 'Verbindet Schienenenden und Mündung',
        'zwischen den Schienen', 796, 812, 64, 136, 22, bevel=R_SMALL),
    prof('support_grip', 'Stützgriff', 'Support grip', 'support', 'graphite', 'Griff der Stützhand unter der Schiene',
         'unter die untere Schiene geschraubt', [(270, 65), (390, 65), (380, 40), (282, 40)], 34),
]
for i, f0 in enumerate((300, 430, 560, 690)):
    PARTS.append(part(f'coil_{i + 1}', f'Spulenring {i + 1}', f'Coil ring {i + 1}', 'cooling', 'frame', 'dark_metal',
                      'Beschleunigerspule um Kern und Schienen', 'um beide Schienen geklemmt', bevel=R_SMALL,
                      f0=f0, f1=f0 + 16, cu=BORE, ow=40, oh=88, iw=28, ih=76, r_out=8, r_in=4))
PARTS += energy_cell('energy_cell', -134, -46, 24, 52, 40, (0, -110, 0))
PARTS += rail(-130, 190, 142)
_s, SA, LINE = scope(-90, 150, length=220, r_obj=21, r_eye=16, r_tube=12)
PARTS += _s
PARTS += grip_rifle(top=48)
PARTS += stock_s1(-150, BORE, s=1.2)
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip'),
    'Socket_SupportHand': dict(at=(330, 52, 0), part='support_grip'),
    'Socket_Muzzle': dict(at=(852, BORE, 0), part='muzzle'),
    'Socket_Cell': dict(at=(-90, 38, 0), part='energy_cell'),
}
ANCHORS.update(SA)
ACTIONS = {
    'charge_fire': dict(de='Aufladen und Einzelstrahl', frames=36, step=1, keys={
        'trigger': [(0, 0), (2, 1), (18, 1), (21, 0)], 'linear_core': [(0, 0), (16, 0.7), (18, 1), (24, 0)]},
        events=[(2, 'charge_start'), (16, 'charged'), (18, 'beam'), (34, 'ready')]),
    'reload': dict(de='Energiezelle wechseln', frames=80, keys={'energy_cell': [(0, 0), (18, 1), (38, 1), (56, 0)]},
                   events=[(18, 'cell_out'), (56, 'cell_in'), (64, 'ready')]),
}
EXPLODE = {'cooling': (0, 0, 80), 'support': (0, -60, 0)}
