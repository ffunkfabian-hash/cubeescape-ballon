"""BASIC-04 Handfeuerwaffe (Hand Cannon): Revolver mit ausschwenkbarer Trommel.

Schwerer Rahmen in Creme, Trommel auf Kran nach links ausschwenkbar, Lauf mit Laufschiene und Unterlauf, Hahn, Kimme und Korn.
"""
import math
from basic.common import prof, box, cyl, part, assemblies, iron_sights, R_BODY, R_MID, R_SMALL, R_FINE

META = dict(id='BASIC-04', num='04', type='hand_cannon', type_de='Handfeuerwaffe', type_en='Hand Cannon', name='Trommel',
            nick='Standard', ammo='primary', fire='semi_auto_double_action', reference_length_m=0.32,
            reference_length_source='Formgen KG12 ref_len (Schätzung claude-0.10)',
            summary='Revolver mit sechs Kammern, ausschwenkbarer Trommel und Kimme/Korn.')
ASSEMBLIES = assemblies('receiver', 'barrel', 'ammo', 'sight', 'grip_controls', 'mechanism')
BORE = 64
CYL_U = 52          # Trommelachse (oberste Kammer auf Laufachse)
t = math.tan(math.radians(16))
PARTS = [
    prof('frame_rear', 'Rahmen hinten', 'Rear frame', 'receiver', 'shell', 'Nimmt Hahn, Abzug und Griff auf',
         'Grundkörper', [(-38, 26), (14, 26), (14, 84), (-26, 88), (-38, 80)], 30),
    box('top_strap', 'Oberbrücke', 'Top strap', 'receiver', 'shell', 'Verbindet Rahmen und Laufaufnahme über der Trommel',
        'mit dem Rahmen verbunden', 12, 82, 78, 88, 22),
    prof('frame_front', 'Laufaufnahme', 'Barrel lug', 'receiver', 'shell', 'Hält den Lauf und den Kran',
         'mit dem Rahmen verbunden', [(80, 22), (96, 22), (96, 88), (80, 88)], 30),
    cyl('crane', 'Kran', 'Crane', 'mechanism', 'dark_metal', 'Trägt die Trommel; schwenkt nach links aus',
        'Scharnier an der linken unteren Rahmenkante', 'f', (26, 17), 14, 82, 4, bevel=R_FINE, segs=12,
        move=dict(kind='rotate', pivot=(48, 26, 17), axis='f', range_deg=(0, -90), event='reload',
                  note='Trommel schwenkt vollständig links neben den Rahmen', expect=((48, 52, 0), (0, 0, 1)))),
    cyl('cylinder', 'Trommel', 'Cylinder', 'ammo', 'dark_metal', 'Sechs Kammern; dreht je Schuss um 60°',
        'auf dem Kran gelagert', 'f', (CYL_U, 0), 16, 80, 22, bevel=R_SMALL, segs=12, parent_part='crane', iface='BCY-6',
        move=dict(kind='rotate', pivot=(48, CYL_U, 0), axis='f', range_deg=(0, 60), event='fire')),
    cyl('barrel', 'Lauf', 'Barrel', 'barrel', 'metal', 'Führt das Geschoss', 'in die Laufaufnahme geschraubt',
        'f', (BORE, 0), 94, 236, 9, segs=20),
    box('barrel_rib', 'Laufschiene', 'Barrel rib', 'barrel', 'shell', 'Trägt das Korn, versteift den Lauf',
        'auf dem Lauf', 94, 236, 68, 76, 12, bevel=R_SMALL),
    box('underlug', 'Unterlauf', 'Underlug', 'barrel', 'shell', 'Gewicht vorn gegen Hochschlag',
        'unter dem Lauf', 94, 226, 40, 58, 18, bevel=R_MID),
    cyl('muzzle', 'Mündung', 'Muzzle', 'barrel', 'dark_metal', 'Mündungskrone; Socket_Muzzle', 'Laufende',
        'f', (BORE, 0), 234, 250, 11, bevel=R_SMALL, segs=12, r_in=4.5),
    prof('hammer', 'Hahn', 'Hammer', 'mechanism', 'graphite', 'Wird gespannt und schlägt beim Schuss vor',
         'Drehpunkt hinten im Rahmen', [(-36, 72), (-30, 72), (-28, 90), (-46, 98), (-48, 92), (-38, 84)], 8, bevel=R_FINE,
         move=dict(kind='rotate', pivot=(-32, 72, 0), axis='x', range_deg=(0, 28), event='cock', expect=((-46, 98, 0), (-1, 0, 0)))),
    prof('grip', 'Griff', 'Grip', 'grip_controls', 'graphite', 'Haupthand; trägt Socket_Hand', 'am Rahmen verschraubt',
         [(26 * t - 22, 26), (-60 * t - 26, -60), (-70 * t - 22, -70), (-70 * t + 16, -70), (-30 * t + 18, -30),
          (26 * t + 18, 26)], 32, bevel=R_BODY, iface='BGM-P'),
    prof('trigger', 'Abzug', 'Trigger', 'grip_controls', 'metal', 'Spannt und löst (Double Action)', 'Drehpunkt im Rahmen',
         [(22, 26), (28, 26), (31, 12), (27, 2), (24, 3), (25, 12)], 6, bevel=R_FINE,
         move=dict(kind='rotate', pivot=(25, 25, 0), axis='x', range_deg=(0, -14), event='fire', expect=((27, 2, 0), (-1, 0, 0)))),
    prof('trigger_guard', 'Abzugsbügel', 'Trigger guard', 'grip_controls', 'graphite', 'Schützt den Abzug',
         'Rahmen vorn und Griff', [(12, -6), (58, -6), (58, 24), (51, 24), (51, 1), (12, 1)], 10, bevel=R_SMALL),
    cyl('cylinder_latch', 'Trommelriegel', 'Cylinder latch', 'grip_controls', 'accent', 'Gibt den Kran frei (Daumen)',
        'links am Rahmen, gleitet nach vorn', 'x', (2, 60), 14, 18, 4.5, segs=16,
        move=dict(kind='translate', pivot=(2, 60, 16), vector_mm=(6, 0, 0), event='reload')),
]
PARTS += iron_sights(-22, 222, 88, h=8)
for p in PARTS:
    if p['id'] == 'front_sight':
        p.update(pts=[(222, 75), (230, 75), (228, 84), (224, 84)])
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip'),
    'Socket_Muzzle': dict(at=(250, BORE, 0), part='muzzle'),
    'Socket_Sight': dict(at=(-22, 92, 0), part='rear_sight_l', note='Kimme; Visierlinie über Kimme und Korn'),
    'Socket_Eye': dict(at=(-180, 92, 0), part='rear_sight_l', note='Vorschlag: 160 mm hinter der Kimme'),
}
ACTIONS = {
    'fire_da': dict(de='Schuss Double Action (Hahn, Trommel)', frames=14, step=1, keys={
        'trigger': [(0, 0), (6, 1), (10, 0)], 'hammer': [(0, 0), (6, 1), (7, 0)], 'cylinder': [(0, 0), (6, 1), (14, 1)]},
        events=[(7, 'shot')]),
    'reload': dict(de='Trommel ausschwenken, laden, einschwenken', frames=72, keys={
        'cylinder_latch': [(0, 0), (6, 1), (14, 0)], 'crane': [(0, 0), (8, 0), (18, 1), (52, 1), (62, 0)]},
        events=[(18, 'cylinder_open'), (24, 'eject'), (40, 'rounds_in'), (62, 'cylinder_closed')], view=(0.55, -0.65, 0.5)),
}
