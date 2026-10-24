"""BASIC-10 Fusionsgewehr (Fusion Rifle): aufladen, dann Salve.

Hohes Gehäuse, Kondensatorgehäuse mit drei Spulenringen und drei Ladeanzeigen, breiter Schlitz-Emitter vorn,
Energiezelle hinter dem Griff (Entnahme nach unten).
"""
from basic.common import (prof, box, cyl, part, assemblies, grip_rifle, rail, reflex_sight, energy_cell, stock_s1, stock_s2, glow,
                          R_BODY, R_MID, R_SMALL, R_FINE)

META = dict(id='BASIC-10', num='10', type='fusion_rifle', type_de='Fusionsgewehr', type_en='Fusion Rifle', name='Glutkern',
            nick='Standard', ammo='special', fire='charge_burst', reference_length_m=0.960,
            reference_length_source='Toolgen fusion_rifle (Formgen KG07 spec units)',
            reference_note='kompakter Emitter statt langem Lauf (entworfen); Bezug aus Toolgen-Weltmodell',
            summary='Fusionsgewehr: Aufladen über drei Kondensatoren, Salve aus dem Schlitz-Emitter.')
ASSEMBLIES = assemblies('receiver', 'barrel', 'ammo', 'sight', 'grip_controls', 'support', 'stock', 'cooling')
BORE = 100
PARTS = [
    prof('receiver', 'Gehäuse', 'Receiver', 'receiver', 'shell', 'Tragkörper, Steuerung und Zellenschacht',
         'Grundkörper', [(-140, 46), (170, 46), (190, 64), (190, 130), (178, 138), (-130, 138), (-140, 128)], 50),
    prof('capacitor_housing', 'Kondensatorgehäuse', 'Capacitor housing', 'barrel', 'graphite',
         'Umschließt die Kondensatoren; Griffbereich der Stützhand', 'am Gehäuse verschraubt, Fuge 1 mm',
         [(191, 62), (452, 62), (470, 80), (470, 126), (456, 136), (191, 136)], 52),
    part('emitter', 'Schlitz-Emitter', 'Slit emitter', 'barrel', 'frame', 'dark_metal', 'Formt die Salve; Socket_Muzzle',
         'auf das Kondensatorgehäuse geschraubt', bevel=R_SMALL, f0=470, f1=500, cu=BORE, ow=60, oh=44, iw=40, ih=10,
         r_out=8, r_in=4),
    part('emitter_lens', 'Emitterlinse', 'Emitter lens', 'barrel', 'xbox', 'energy', 'Leuchtet beim Aufladen auf',
         'im Emitter', bevel=0, f0=474, f1=476, cu=BORE, ww=40, hh=10, move=dict(kind='glow', pivot=None, event='charge', max=6.0)),
]
for i, f0 in enumerate((240, 310, 380)):
    PARTS.append(part(f'coil_{i + 1}', f'Spulenring {i + 1}', f'Coil ring {i + 1}', 'cooling', 'frame', 'dark_metal',
                      'Kondensatorspule; führt Wärme nach außen', 'um das Kondensatorgehäuse', bevel=R_SMALL,
                      f0=f0, f1=f0 + 14, cu=99, ow=60, oh=80, iw=52, ih=72, r_out=10, r_in=7))
    PARTS.append(glow(f'charge_{i + 1}', f'Ladeanzeige {i + 1}', f'Charge pip {i + 1}', 'barrel', f0 + 24, f0 + 52, 118, 126,
                      x=26.2, func=f'Leuchtet bei {i + 1}/3 Ladung'))
PARTS += energy_cell('energy_cell', -124, -40, 22, 50, 40, (0, -110, 0))
PARTS += rail(-120, 160, 138)
_s, SA, LINE = reflex_sight(-30, 146, win_w=32, win_h=24)
PARTS += _s
PARTS += grip_rifle(top=46)
PARTS += stock_s2(-140, BORE, s=0.95)
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip'),
    'Socket_SupportHand': dict(at=(345, 80, 0), part='capacitor_housing'),
    'Socket_Muzzle': dict(at=(500, BORE, 0), part='emitter'),
    'Socket_Cell': dict(at=(-82, 36, 0), part='energy_cell'),
}
ANCHORS.update(SA)
ACTIONS = {
    'charge_fire': dict(de='Aufladen und Salve', frames=40, step=1, keys={
        'trigger': [(0, 0), (2, 1), (30, 1), (33, 0)],
        'charge_1': [(0, 0), (6, 1), (30, 1), (36, 0)], 'charge_2': [(0, 0), (12, 0), (16, 1), (30, 1), (36, 0)],
        'charge_3': [(0, 0), (20, 0), (24, 1), (30, 1), (36, 0)], 'emitter_lens': [(0, 0), (24, 0.4), (27, 1), (36, 0)]},
        events=[(2, 'charge_start'), (26, 'charged'), (27, 'burst'), (40, 'ready')], view=(0.8, -0.3, 0.45)),
    'charge_cancel': dict(de='Aufladen abbrechen', frames=24, step=1, keys={
        'trigger': [(0, 0), (2, 1), (12, 1), (14, 0)], 'charge_1': [(0, 0), (6, 1), (12, 1), (20, 0)],
        'charge_2': [(0, 0), (11, 0), (12, 0.6), (20, 0)]}, events=[(12, 'cancel')], view=(0.8, -0.3, 0.45)),
    'reload': dict(de='Energiezelle wechseln', frames=70, keys={'energy_cell': [(0, 0), (16, 1), (34, 1), (50, 0)]},
                   events=[(16, 'cell_out'), (50, 'cell_in'), (58, 'ready')]),
}
EXPLODE = {'cooling': (0, 0, 70)}
