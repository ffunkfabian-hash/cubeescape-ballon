"""BASIC-15 Maschinengewehr (Machine Gun): gurtgespeistes Dauerfeuer.

Breites Gehäuse, Zuführdeckel mit Scharnier vorn (Visier sitzt darauf), Munitionskasten links mit sichtbarem Gurtstück,
Tragegriff über dem Laufmantel, Laufmantel mit Lüftung, Schaft S1 (1,1).
"""
from basic.common import (prof, box, cyl, assemblies, grip_rifle, selector, rail, reflex_sight, barrel, stock_s1, vents,
                          R_BODY, R_MID, R_SMALL, R_FINE)

META = dict(id='BASIC-15', num='15', type='machine_gun', type_de='Maschinengewehr', type_en='Machine Gun', name='Dauerlauf',
            nick='Standard', ammo='heavy', fire='full_auto_belt', reference_length_m=1.15,
            reference_length_source='Formgen KG16 ref_len (Schätzung claude-0.10)',
            summary='Gurtgespeistes Maschinengewehr mit Munitionskasten und Tragegriff.')
ASSEMBLIES = assemblies('receiver', 'barrel', 'ammo', 'sight', 'grip_controls', 'support', 'stock', 'mechanism')
BORE = 106
COVER_PIV = (150, 146)
PARTS = [
    prof('receiver', 'Gehäuse', 'Receiver', 'receiver', 'shell', 'Breiter Tragkörper; Zuführung oben links',
         'Grundkörper', [(-150, 40), (196, 40), (220, 60), (220, 140), (-140, 140), (-150, 130)], 56),
    prof('feed_cover', 'Zuführdeckel', 'Feed cover', 'mechanism', 'shell', 'Hält den Gurt in der Zuführung; trägt das Visier',
         'Scharnier vorn, öffnet hinten nach oben', [(-70, 141), (156, 141), (156, 156), (146, 162), (-60, 162), (-70, 154)], 52,
         move=dict(kind='rotate', pivot=(COVER_PIV[0], COVER_PIV[1], 0), axis='x', range_deg=(0, -62), event='reload',
                   expect=((-60, 160, 0), (0, 1, 0)))),
    box('feed_tray', 'Zuführschale', 'Feed tray', 'ammo', 'dark_metal', 'Führt den Gurt ins Gehäuse', 'oben im Gehäuse',
        -20, 60, 136, 141, 50, bevel=R_FINE),
    box('ammo_box', 'Munitionskasten', 'Ammo box', 'ammo', 'dark_metal', 'Hält den Gurt; austauschbar',
        'links am Gehäuse eingehängt (lösbar)', -10, 110, 6, 112, 46, bevel=R_MID, x=56, iface='BAB-1',
        move=dict(kind='translate', pivot=(50, 60, 56), vector_mm=(0, -70, 90), event='reload', removable=True)),
    box('ammo_box_lid', 'Kastendeckel', 'Ammo box lid', 'ammo', 'shell', 'Deckel mit Griffmulde', 'auf dem Munitionskasten',
        -12, 112, 110, 118, 48, bevel=R_SMALL, x=56, parent_part='ammo_box'),
    prof('belt', 'Gurtstück', 'Belt section', 'ammo', 'metal', 'Sichtbarer Gurt vom Kasten zur Zuführung',
         'zwischen Kasten und Zuführschale', [(0, 118), (60, 118), (60, 140), (0, 140)], 16, bevel=R_FINE, x=32,
         parent_part='ammo_box'),
    prof('shroud', 'Laufmantel', 'Barrel shroud', 'support', 'shell', 'Hitzeschutz; Griffbereich der Stützhand unten',
         'am Gehäuse verschraubt, Fuge 1 mm', [(221, 72), (520, 72), (540, 90), (540, 132), (221, 132)], 46),
    prof('shroud_grip', 'Stützgriffzone', 'Support grip zone', 'support', 'graphite', 'Griffbereich der Stützhand',
         'unter dem Laufmantel', [(260, 56), (420, 56), (430, 72), (250, 72)], 44),
    prof('carry_handle', 'Tragegriff', 'Carry handle', 'support', 'graphite', 'Tragen und Laufwechsel',
         'auf dem Laufmantel', [(236, 131), (250, 131), (256, 156), (326, 156), (332, 131), (346, 131), (346, 138),
                                (338, 170), (244, 170), (236, 138)], 16),
]
PARTS += vents('vent', 'support', [380, 430, 480], 34, 104, 118, 22.9)
PARTS += barrel(538, 726, BORE, r=12, muzzle_len=52, muzzle_r=17)
PARTS += rail(-50, 140, 162)
_s, SA, LINE = reflex_sight(-40, 170, win_w=34, win_h=28)
PARTS += _s
for p in PARTS:
    if p['id'] in ('rail', 'sight_mount'):
        p['parent_part'] = 'feed_cover'
PARTS += grip_rifle(top=40)
PARTS += selector(4, 66, x=28.5)
PARTS += stock_s1(-150, BORE, s=1.1)
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip'),
    'Socket_SupportHand': dict(at=(340, 64, 0), part='shroud_grip'),
    'Socket_Muzzle': dict(at=(726, BORE, 0), part='muzzle'),
    'Socket_FeedCover': dict(at=(-60, 162, 0), part='feed_cover', note='Griffpunkt zum Öffnen'),
    'Socket_AmmoBox': dict(at=(50, 60, 80), part='ammo_box'),
}
ANCHORS.update(SA)
ACTIONS = {
    'fire_auto': dict(de='Dauerfeuer (Mechanik)', frames=24, step=1, keys={'trigger': [(0, 0), (2, 1), (20, 1), (23, 0)]},
                      events=[(2, 'shot'), (6, 'shot'), (10, 'shot'), (14, 'shot'), (18, 'shot')]),
    'reload': dict(de='Deckel auf, Kasten tauschen, Gurt einlegen, Deckel zu', frames=150, keys={
        'feed_cover': [(0, 0), (16, 1), (118, 1), (134, 0)], 'ammo_box': [(0, 0), (24, 0), (44, 1), (76, 1), (100, 0)]},
        events=[(16, 'cover_open'), (44, 'box_out'), (100, 'box_in'), (112, 'belt_seated'), (134, 'cover_closed')],
        view=(0.75, -0.35, 0.55)),
}
EXPLODE = {'mechanism': (0, 80, 0), 'ammo': (0, -40, 110)}
