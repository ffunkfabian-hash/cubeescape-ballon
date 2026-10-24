"""BASIC-12 Spurgewehr (Trace Rifle): kontinuierlicher Strahl bei gehaltenem Abzug.

Rundes Fokusrohr in Graphit (zugleich Stützhandbereich) mit drei Ringen und Fokuskegel, Energiezelle links seitlich,
Holo-Visier mit breitem Fenster, einteiliger Creme-Körper bis zur Schulter (kein Schaftrohr).
"""
from basic.common import (prof, box, cyl, part, assemblies, grip_rifle, rail, reflex_sight, energy_cell, stock_s1, stock_s2,
                          R_BODY, R_MID, R_SMALL, R_FINE)

META = dict(id='BASIC-12', num='12', type='trace_rifle', type_de='Spurgewehr', type_en='Trace Rifle', name='Leitstrahl',
            nick='Standard', ammo='special', fire='continuous_beam', reference_length_m=1.044,
            reference_length_source='Toolgen trace_rifle (Formgen KG08 spec units)',
            summary='Strahlwaffe mit Fokusrohr, seitlicher Energiezelle und Holo-Visier.')
ASSEMBLIES = assemblies('receiver', 'barrel', 'ammo', 'sight', 'grip_controls', 'support', 'stock')
BORE = 96
PARTS = [
    prof('receiver', 'Gehäuse', 'Receiver', 'receiver', 'shell', 'Tragkörper, Zellenschacht links',
         'Grundkörper', [(-120, 48), (180, 48), (200, 70), (200, 124), (186, 132), (-110, 132), (-120, 122)], 46),
    cyl('focus_tube', 'Fokusrohr', 'Focus tube', 'support', 'graphite', 'Umschließt den Strahlkanal; Griffbereich der Stützhand',
        'am Gehäuse verschraubt', 'f', (BORE, 0), 198, 520, 22, segs=24, bevel=R_SMALL),
    cyl('focus_cone', 'Fokuskegel', 'Focus cone', 'barrel', 'dark_metal', 'Verjüngt den Strahl; Socket_Muzzle',
        'auf das Fokusrohr gesteckt', 'f', (BORE, 0), 518, 580, 24, r1=12, segs=24, bevel=R_SMALL),
    cyl('focus_lens', 'Fokuslinse', 'Focus lens', 'barrel', 'energy', 'Leuchtet bei aktivem Strahl', 'in der Kegelspitze',
        'f', (BORE, 0), 576, 582, 8, bevel=0, segs=16, move=dict(kind='glow', pivot=None, event='beam', max=6.0)),
]
for i, f0 in enumerate((280, 360, 440)):
    PARTS.append(cyl(f'focus_ring_{i + 1}', f'Fokusring {i + 1}', f'Focus ring {i + 1}', 'barrel', 'dark_metal',
                     'Hält die Fokusspule; gliedert das Rohr', 'auf das Fokusrohr gepresst', 'f', (BORE, 0), f0, f0 + 10, 25,
                     segs=24, bevel=R_SMALL))
PARTS += energy_cell('energy_cell', 30, 150, 72, 114, 12, (0, 0, 70), x=28)
PARTS += rail(-100, 170, 132)
_s, SA, LINE = reflex_sight(-20, 140, win_w=36, win_h=26)
PARTS += _s
PARTS += grip_rifle(top=48)
PARTS += [
    prof('rear_body', 'Hinterkörper', 'Rear body', 'stock', 'shell', 'Einteilige Fortsetzung des Gehäuses bis zur Schulter',
         'mit dem Gehäuse verschraubt, Fuge 1 mm', [(-121, 62), (-121, 132), (-262, 128), (-274, 120), (-274, 34), (-244, 26),
                                                    (-170, 46)], 40, iface='BST-T'),
    prof('butt_pad', 'Schaftkappe', 'Butt pad', 'stock', 'graphite', 'Anlage an der Schulter', 'auf das Körperende gesteckt',
         [(-273, 22), (-273, 132), (-286, 130), (-289, 118), (-289, 32), (-286, 24)], 42, bevel=3.0),
    box('cheek_pad', 'Wangenpolster', 'Cheek pad', 'stock', 'graphite', 'Anlage für die Wange beim Zielen', 'auf dem Hinterkörper',
        -240, -150, 128, 137, 26, bevel=3.0),
]
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip'),
    'Socket_SupportHand': dict(at=(320, BORE - 6, 0), part='focus_tube', note='Stützhand umgreift das Fokusrohr'),
    'Socket_Muzzle': dict(at=(582, BORE, 0), part='focus_lens'),
    'Socket_Cell': dict(at=(90, 93, 34), part='energy_cell', note='Zelle links seitlich'),
}
ANCHORS.update(SA)
ACTIONS = {
    'beam': dict(de='Strahl halten und loslassen', frames=36, step=1, keys={
        'trigger': [(0, 0), (2, 1), (28, 1), (31, 0)], 'focus_lens': [(0, 0), (4, 1), (28, 1), (32, 0)]},
        events=[(4, 'beam_start'), (28, 'beam_end')]),
    'reload': dict(de='Energiezelle seitlich wechseln', frames=70, keys={'energy_cell': [(0, 0), (16, 1), (34, 1), (50, 0)]},
                   events=[(16, 'cell_out'), (50, 'cell_in'), (58, 'ready')], view=(0.8, -0.3, 0.5)),
}
EXPLODE = {'ammo': (0, 0, 90)}
