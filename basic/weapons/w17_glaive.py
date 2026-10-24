"""BASIC-17 Glefe (Glaive): Stangenwaffe mit Schuss, Schild und Hieb.

Graphitstange, Kernkörper mit Abzug und Energiezelle oben, Stützgriff, Klingenkopf mit Emitter, zwei Schildflügel,
die zum Blocken aufklappen, Gegengewicht hinten.
"""
from basic.common import (prof, box, cyl, assemblies, grip_rifle, energy_cell, R_BODY, R_MID, R_SMALL, R_FINE)

META = dict(id='BASIC-17', num='17', type='glaive', type_de='Glefe', type_en='Glaive', name='Schildwacht', nick='Standard',
            ammo='special', fire='melee_projectile_shield', reference_length_m=1.40,
            reference_length_source='Formgen KG18 ref_len (Schätzung claude-0.10)',
            summary='Glefe mit Projektil-Emitter, aufklappbarem Schild und Klingenkopf.')
ASSEMBLIES = assemblies('shaft', 'receiver', 'ammo', 'grip_controls', 'support', 'blade', 'shield')
AX = 40
PARTS = [
    cyl('shaft', 'Stange', 'Shaft', 'shaft', 'graphite', 'Trägt alle Baugruppen', 'durchgehend', 'f', (AX, 0), -300, 660, 13,
        segs=12, bevel=R_SMALL),
    cyl('counterweight', 'Gegengewicht', 'Counterweight', 'shaft', 'dark_metal', 'Balance und Stoßende', 'Stangenende',
        'f', (AX, 0), -334, -296, 20, segs=8, bevel=R_MID),
    prof('core', 'Kernkörper', 'Core body', 'receiver', 'shell', 'Abzugsmechanik und Zellenschacht', 'um die Stange geklemmt',
         [(-60, 18), (190, 18), (210, 34), (210, 62), (196, 70), (-50, 70), (-60, 60)], 40),
    cyl('support_grip', 'Stützgriff', 'Support grip', 'support', 'graphite', 'Griffbereich der Stützhand',
        'auf der Stange', 'f', (AX, 0), 300, 430, 17, segs=12, bevel=R_SMALL),
    box('blade_mount', 'Klingenaufnahme', 'Blade mount', 'blade', 'dark_metal', 'Fasst Klinge und Emitter',
        'am Stangenende', 640, 700, 18, 64, 34, bevel=R_MID),
    prof('blade', 'Klinge', 'Blade', 'blade', 'metal', 'Blattförmige Klinge für Stiche und Hiebe', 'in der Aufnahme',
         [(698, 12), (880, 8), (1090, AX), (880, 72), (698, 68)], 9, bevel=R_SMALL),
    cyl('emitter', 'Emitter', 'Emitter', 'blade', 'energy', 'Gibt das Projektil ab; leuchtet beim Schuss',
        'in der Klingenaufnahme', 'f', (AX, 0), 700, 760, 6, bevel=0, segs=12,
        move=dict(kind='glow', pivot=None, event='fire', max=6.0)),
    prof('shield_l', 'Schildflügel links', 'Shield wing left', 'shield', 'shell', 'Klappt zum Blocken nach vorn-außen auf',
         'Scharnier vorn an der Klingenaufnahme', [(470, -8), (636, 4), (636, 76), (470, 88)], 5, x=24, bevel=R_SMALL,
         move=dict(kind='rotate', pivot=(636, AX, 24), axis='u', range_deg=(0, -70), event='shield',
                   expect=((470, AX, 24), (0, 0, 1)))),
    prof('shield_r', 'Schildflügel rechts', 'Shield wing right', 'shield', 'shell', 'Klappt zum Blocken nach vorn-außen auf',
         'Scharnier vorn an der Klingenaufnahme', [(470, -8), (636, 4), (636, 76), (470, 88)], 5, x=-24, bevel=R_SMALL,
         move=dict(kind='rotate', pivot=(636, AX, -24), axis='u', range_deg=(0, 70), event='shield',
                   expect=((470, AX, -24), (0, 0, -1)))),
]
PARTS += energy_cell('energy_cell', 40, 160, 70, 86, 26, (0, 60, 0))
PARTS += [p for p in grip_rifle(top=20, w=30) if p['id'] != 'trigger_guard']
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip', note='hintere Hand mit Abzug'),
    'Socket_SupportHand': dict(at=(365, AX, 0), part='support_grip'),
    'Socket_Muzzle': dict(at=(760, AX, 0), part='emitter', note='Projektilaustritt'),
    'Socket_BladeCenter': dict(at=(900, AX, 0), part='blade'),
}
ACTIONS = {
    'fire': dict(de='Projektil abgeben', frames=14, step=1, keys={
        'trigger': [(0, 0), (2, 1), (6, 0)], 'emitter': [(0, 0), (2, 1), (8, 0)]}, events=[(2, 'shot')]),
    'shield': dict(de='Schild aufklappen, halten, schließen', frames=40, step=2, keys={
        'shield_l': [(0, 0), (8, 1), (30, 1), (38, 0)], 'shield_r': [(0, 0), (8, 1), (30, 1), (38, 0)]},
        events=[(8, 'shield_up'), (38, 'shield_down')], view=(-0.5, -0.8, 0.45)),
    'reload': dict(de='Energiezelle wechseln', frames=70, keys={'energy_cell': [(0, 0), (16, 1), (34, 1), (50, 0)]},
                   events=[(16, 'cell_out'), (50, 'cell_in')]),
}
EXPLODE = {'shield_l': (0, 0, 70), 'shield_r': (0, 0, -70), 'blade': (130, 0, 0), 'ammo': (0, 80, 0),
           'grip_controls': (0, -60, 0), 'support': (0, 0, 0)}

HERO = (-0.6, -0.4, 0.62)
