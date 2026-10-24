"""BASIC-09 Scharfschützengewehr (Sniper Rifle): Repetierer mit Kammerstängel.

Langer schwerer Lauf mit Mündungsbremse, großes Zielfernrohr, kurzes Kastenmagazin, Kammerstängel rechts (dreht und gleitet).
"""
from basic.common import (prof, box, cyl, assemblies, grip_rifle, selector, rail, scope, rifle_mag, barrel, stock_s1,
                          vents, R_BODY, R_MID, R_SMALL, R_FINE)

META = dict(id='BASIC-09', num='09', type='sniper_rifle', type_de='Scharfschützengewehr', type_en='Sniper Rifle',
            name='Weitschuss', nick='Standard', ammo='special', fire='bolt_action', reference_length_m=1.134,
            reference_length_source='Toolgen sniper_rifle (Formgen KG05 spec units)',
            summary='Repetier-Scharfschützengewehr mit großem Zielfernrohr.')
ASSEMBLIES = assemblies('receiver', 'barrel', 'ammo', 'sight', 'grip_controls', 'support', 'stock', 'mechanism')
BORE = 98
PARTS = [
    prof('upper', 'Oberes Gehäuse', 'Upper receiver', 'receiver', 'shell', 'Verschlussgehäuse und Schiene',
         'mit Unterem Gehäuse verbolzt', [(-120, 72), (196, 72), (196, 120), (188, 126), (-110, 126), (-120, 116)], 40),
    prof('lower', 'Unteres Gehäuse', 'Lower receiver', 'receiver', 'shell', 'Griffmodul und Magazinschacht',
         'unter dem Oberen Gehäuse, Fuge 1 mm', [(-120, 54), (-60, 38), (150, 38), (186, 60), (186, 71), (-120, 71)], 38),
    prof('handguard', 'Handschutz', 'Handguard', 'support', 'graphite', 'Langer Handschutz, frei schwingender Lauf',
         'am Oberen Gehäuse, Fuge 1 mm', [(197, 64), (520, 64), (536, 76), (536, 116), (526, 122), (197, 122)], 42),
    cyl('bolt', 'Verschluss', 'Bolt', 'mechanism', 'metal', 'Verriegelt die Patrone; gleitet zurück',
        'im Oberen Gehäuse (gleitet)', 'f', (BORE + 4, -12), -60, 40, 7, segs=16,
        move=dict(kind='translate', pivot=(-10, BORE + 4, -12), vector_mm=(-80, 0, 0), event='bolt')),
    cyl('bolt_handle', 'Kammerstängel', 'Bolt handle', 'mechanism', 'dark_metal', 'Hebel zum Öffnen des Verschlusses',
        'am Verschluss (dreht 60° hoch)', 'x', (-30, BORE + 4), -48, -14, 4.5, segs=12, parent_part='bolt',
        move=dict(kind='rotate', pivot=(-30, BORE + 4, -12), axis='f', range_deg=(0, -60), event='bolt',
                  expect=((-30, BORE + 4, -54), (0, 1, 0)))),
    cyl('bolt_knob', 'Kammerknopf', 'Bolt knob', 'mechanism', 'graphite', 'Griffkugel des Kammerstängels',
        'am Kammerstängel', 'x', (-30, BORE + 4), -60, -46, 8, segs=14, bevel=R_SMALL, parent_part='bolt_handle'),
    box('bolt_slot', 'Verschlussfenster', 'Bolt slot', 'receiver', 'dark_metal', 'Öffnung für Kammerstängel und Auswurf rechts',
        'im Oberen Gehäuse', -110, 50, 90, 116, 1.4, bevel=R_SMALL, x=-19.8),
]
PARTS += vents('vent', 'support', [300, 400], 70, 100, 110, 20.9)
PARTS += barrel(534, 812, BORE, r=11, muzzle_len=58, muzzle_r=17)
PARTS += rail(-100, 186, 126)
_s, SA, LINE = scope(-80, 134, length=236, r_obj=23, r_eye=17, r_tube=13)
PARTS += _s
PARTS += grip_rifle(top=40)
PARTS += selector(4, 62, x=19.5)
PARTS += rifle_mag(92, 60, depth=40, length=72, tilt=0, w=26, curve=0)
PARTS += stock_s1(-120, BORE, s=1.18)
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip'),
    'Socket_SupportHand': dict(at=(340, 92, 0), part='handguard'),
    'Socket_Muzzle': dict(at=(812, BORE, 0), part='muzzle'),
    'Socket_MagWell': dict(at=(112, 60, 0), part='lower'),
    'Socket_Bolt': dict(at=(-30, BORE + 4, -54), part='bolt_knob', note='Griffpunkt Kammerknopf (Haupthand)'),
}
ANCHORS.update(SA)
ACTIONS = {
    'fire_cycle': dict(de='Schuss und Repetieren', frames=40, step=1, keys={
        'trigger': [(0, 0), (2, 1), (6, 0)], 'bolt_handle': [(0, 0), (10, 0), (15, 1), (27, 1), (32, 0)],
        'bolt': [(0, 0), (15, 0), (20, 1), (22, 1), (27, 0)]},
        events=[(2, 'shot'), (15, 'unlock'), (20, 'eject'), (27, 'chamber'), (32, 'ready')], view=(-0.85, -0.2, 0.5)),
    'reload_empty': dict(de='Nachladen aus leerem Zustand', frames=90, keys={
        'magazine': [(0, 0), (16, 1), (34, 1), (50, 0)], 'bolt_handle': [(0, 0), (56, 0), (61, 1), (73, 1), (78, 0)],
        'bolt': [(0, 0), (61, 0), (66, 1), (68, 1), (73, 0)]},
        events=[(16, 'mag_out'), (50, 'mag_seated'), (73, 'chamber'), (80, 'ready')], view=(-0.85, -0.2, 0.5)),
}
