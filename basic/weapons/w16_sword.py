"""BASIC-16 Schwert (Sword): gewöhnliches Nahkampfschwert ohne Sonderangriffe.

Einschneidige Klinge (dunkler Kern, helle Schneide), Parierblock in Creme mit kleiner Ladeanzeige, Parierstange,
langer Graphitgriff für beide Hände, Knauf. Keine Wurf-, Fernkampf- oder Energieangriffe.
"""
from basic.common import prof, box, cyl, assemblies, glow, R_BODY, R_MID, R_SMALL, R_FINE

META = dict(id='BASIC-16', num='16', type='sword', type_de='Schwert', type_en='Sword', name='Klingenlauf', nick='Standard',
            ammo='heavy', fire='melee', reference_length_m=1.10,
            reference_length_source='Formgen KG17 ref_len (Schätzung claude-0.10)',
            summary='Einschneidiges Schwert mit Parierblock und Zweihandgriff.')
ASSEMBLIES = assemblies('blade', 'guard', 'grip_controls')
PARTS = [
    prof('blade_core', 'Klingenkern', 'Blade core', 'blade', 'dark_metal', 'Tragender Klingenrücken',
         'in den Parierblock gesteckt', [(96, -18), (96, 24), (880, 20), (1000, 2), (940, -14)], 9, bevel=R_SMALL),
    prof('blade_spine', 'Klingenrücken', 'Blade spine', 'blade', 'shell', 'Versteift die Klinge; heller Familienakzent oben',
         'auf den Klingenkern geklebt', [(104, 12), (104, 27), (860, 23), (900, 16)], 12, bevel=R_SMALL),
    prof('blade_edge', 'Schneide', 'Edge', 'blade', 'metal', 'Helle Schneide unten; Trefferfläche',
         'mit dem Kern verbunden', [(100, -34), (100, -16), (944, -12), (1010, 0), (952, -24), (860, -32)], 5, bevel=R_FINE),
    box('guard', 'Parierblock', 'Guard block', 'guard', 'shell', 'Fasst die Klinge, schützt die Hand, trägt die Zelle',
        'auf die Angel geschoben', 54, 104, -36, 40, 46, bevel=R_BODY),
    box('crossguard', 'Parierstange', 'Crossguard', 'guard', 'dark_metal', 'Fängt gegnerische Klingen ab',
        'am Parierblock', 44, 58, -30, 34, 96, bevel=R_SMALL),
    glow('charge_window', 'Ladeanzeige', 'Charge window', 'guard', 66, 92, 4, 14, x=23.2,
         func='Zeigt die Ladungen für schwere Angriffe'),
    cyl('grip', 'Griff', 'Grip', 'grip_controls', 'graphite', 'Zweihandgriff; Socket_Hand vorn, Stützhand hinten',
        'auf der Angel', 'f', (0, 0), -150, 44, 16, segs=12, bevel=R_SMALL),
    cyl('grip_ring', 'Griffring', 'Grip ring', 'grip_controls', 'accent', 'Trennt die beiden Handpositionen (Akzent)',
        'auf dem Griff', 'f', (0, 0), -60, -52, 17.5, segs=12, bevel=R_FINE),
    cyl('pommel', 'Knauf', 'Pommel', 'grip_controls', 'dark_metal', 'Gegengewicht, sichert die Angel', 'Griffende',
        'f', (0, 0), -184, -148, 22, segs=8, bevel=R_MID),
]
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip', note='vordere Hand am Parierblock'),
    'Socket_SupportHand': dict(at=(-104, 0, 0), part='grip', note='hintere Hand vor dem Knauf'),
    'Socket_Muzzle': dict(at=(1010, 0, 0), part='blade_edge', note='Klingenspitze (Formgen-Konvention)'),
    'Socket_BladeCenter': dict(at=(560, 0, 0), part='blade_core', note='Trefferzentrum'),
}
ACTIONS = {
    'guard_charge': dict(de='Blocken: Ladeanzeige zieht Energie', frames=30, step=2, keys={
        'charge_window': [(0, 1), (6, 0.3), (24, 0.3), (30, 1)]}, events=[(6, 'block_start'), (24, 'block_end')],
        view=(0.55, -0.3, 0.75)),
}
EXPLODE = {'blade': (170, 0, 0), 'guard': (70, 0, 0), 'grip_controls': (-60, 0, 0)}

HERO = (-0.55, -0.35, 0.75)
