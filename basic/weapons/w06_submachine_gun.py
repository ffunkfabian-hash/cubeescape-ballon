"""BASIC-06 Maschinenpistole (Submachine Gun): kompakte Vollautomatik.

Magazin im Griff (deutlich länger als der Griff, Creme gegen Graphit), kurzer Vordergriff, kurzer Schaft S1 (0,75),
kompaktes Reflexvisier.
"""
import math
from basic.common import (prof, box, assemblies, grip_rifle, selector, rail, reflex_sight, rifle_mag, barrel,
                          charging_handle, stock_s1, vents, R_BODY, R_MID, R_FINE)

META = dict(id='BASIC-06', num='06', type='submachine_gun', type_de='Maschinenpistole', type_en='Submachine Gun',
            name='Kurzläufer', nick='Standard', ammo='primary', fire='full_auto', reference_length_m=0.616,
            reference_length_source='Toolgen smg (Formgen KG06 spec units)',
            summary='Kompakte Maschinenpistole, Magazin im Griff, Vordergriff.')
ASSEMBLIES = assemblies('receiver', 'barrel', 'ammo', 'sight', 'grip_controls', 'support', 'stock', 'mechanism')
BORE = 82
TILT = 8
PARTS = [
    prof('receiver', 'Gehäuse', 'Receiver', 'receiver', 'shell', 'Einteiliger Tragkörper', 'Grundkörper',
         [(-90, 40), (160, 40), (180, 58), (180, 104), (170, 112), (-80, 112), (-90, 102)], 40),
    prof('handguard', 'Handschutz', 'Handguard', 'support', 'graphite', 'Kurzer Handschutz um den Lauf',
         'am Gehäuse, Fuge 1 mm', [(181, 56), (270, 56), (284, 68), (284, 102), (181, 108)], 38),
    prof('foregrip', 'Vordergriff', 'Foregrip', 'support', 'graphite', 'Senkrechter Griff der Stützhand; Socket_SupportHand',
         'unter den Handschutz geschraubt', [(220, 57), (252, 57), (248, -2), (240, -8), (222, -8), (216, -2)], 28),
    prof('port_cover', 'Auswurfklappe', 'Ejection port cover', 'mechanism', 'dark_metal', 'Auswurffenster rechts',
         'Scharnier unten', [(40, 80), (92, 80), (92, 100), (40, 100)], 1.6, bevel=R_FINE, x=-20.6,
         move=dict(kind='rotate', pivot=(66, 80, -21), axis='f', range_deg=(0, 75), event='fire', expect=((66, 100, -21), (0, 0, -1)))),
]
PARTS += vents('vent', 'support', [200, 236], 26, 86, 96, 18.9)
PARTS += barrel(282, 340, BORE, r=8, muzzle_len=28, muzzle_r=12)
PARTS += rail(-60, 150, 112)
_s, SA, LINE = reflex_sight(0, 120, win_w=26, win_h=20)
PARTS += _s
_g = grip_rifle(top=40, tilt=TILT, w=34)
PARTS += _g
PARTS += selector(-30, 70, x=20.5)
t = math.tan(math.radians(TILT))
PARTS += rifle_mag(40 * t - 16, 40, depth=30, length=160, tilt=-TILT, w=22, curve=0)
PARTS += stock_s1(-90, BORE, s=0.72, cheek=False)
PARTS += charging_handle(-70, 100, x=20.5, travel=45)
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip'),
    'Socket_SupportHand': dict(at=(236, 24, 0), part='foregrip'),
    'Socket_Muzzle': dict(at=(340, BORE, 0), part='muzzle'),
    'Socket_MagWell': dict(at=(0, 40, 0), part='grip', note='Magazinschacht im Griff'),
}
ANCHORS.update(SA)
ACTIONS = {
    'fire_auto': dict(de='Dauerfeuer (Mechanik)', frames=24, step=1, keys={
        'trigger': [(0, 0), (2, 1), (20, 1), (23, 0)], 'port_cover': [(0, 0), (3, 1), (24, 1)]},
        events=[(2, 'shot'), (5, 'shot'), (7, 'shot'), (10, 'shot'), (12, 'shot'), (15, 'shot'), (17, 'shot'), (20, 'shot')]),
    'reload_empty': dict(de='Nachladen aus leerem Zustand', frames=78, keys={
        'magazine': [(0, 0), (16, 1), (32, 1), (48, 0)], 'charging_handle': [(0, 0), (56, 0), (62, 1), (68, 0)]},
        events=[(16, 'mag_out'), (48, 'mag_seated'), (62, 'charge'), (70, 'ready')]),
}
