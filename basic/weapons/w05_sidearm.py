"""BASIC-05 Pistole (Sidearm): halbautomatische Schlittenpistole.

Graphit-Rahmen mit Griff, Creme-Schlitten mit Kimme und Korn, Magazin im Griff, Schlittenfang als Akzent.
"""
import math
from basic.common import prof, box, cyl, assemblies, iron_sights, R_BODY, R_MID, R_SMALL, R_FINE

META = dict(id='BASIC-05', num='05', type='sidearm', type_de='Pistole', type_en='Sidearm', name='Seitenwaffe',
            nick='Standard', ammo='primary', fire='semi_auto', reference_length_m=0.243,
            reference_length_source='Toolgen 0.13 pistol (Formgen KG01 spec units)',
            summary='Kompakte Schlittenpistole mit Magazin im Griff.')
ASSEMBLIES = assemblies('receiver', 'barrel', 'ammo', 'sight', 'grip_controls', 'mechanism')
BORE = 58
TILT = 18
t = math.tan(math.radians(TILT))
PARTS = [
    prof('frame', 'Rahmen', 'Frame', 'receiver', 'graphite', 'Trägt Schlitten, Abzug und Griff',
         'Grundkörper', [(-34, 30), (150, 30), (156, 36), (156, 46), (-38, 46)], 26),
    prof('slide', 'Schlitten', 'Slide', 'mechanism', 'shell', 'Verschluss; läuft beim Schuss zurück',
         'auf den Rahmenschienen (gleitet)', [(-50, 46), (166, 46), (170, 52), (170, 68), (162, 74), (-44, 74), (-50, 68)], 26,
         move=dict(kind='translate', pivot=(60, 60, 0), vector_mm=(-42, 0, 0), event='fire')),
    cyl('barrel', 'Lauf', 'Barrel', 'barrel', 'metal', 'Führt das Geschoss; Mündung schaut aus dem Schlitten',
        'im Rahmen gelagert', 'f', (BORE, 0), 120, 174, 6, segs=16, r_in=3.2),
    prof('grip', 'Griff', 'Grip', 'grip_controls', 'graphite', 'Haupthand; Magazinschacht innen; trägt Socket_Hand',
         'Teil des Rahmens', [(30 * t - 22, 32), (-58 * t - 24, -58), (-66 * t - 20, -66), (-66 * t + 14, -66),
                              (-20 * t + 17, -20), (32 * t + 17, 32)], 28, bevel=R_BODY, iface='BGM-P'),
    prof('magazine', 'Magazin', 'Magazine', 'ammo', 'dark_metal', 'Hält die Patronen; steckt im Griff',
         'rastet im Griff ein (lösbar)', [(20 * t - 14, 20), (-66 * t - 15, -66), (-66 * t + 9, -66), (20 * t + 10, 20)], 20,
         bevel=R_MID, move=dict(kind='translate', pivot=(-20 * t, -20, 0),
                                vector_mm=(round(-120 * math.sin(math.radians(TILT)), 1), round(-120 * math.cos(math.radians(TILT)), 1), 0),
                                event='reload', note='Entnahme entlang der Griffachse nach unten', removable=True)),
    prof('magazine_base', 'Magazinboden', 'Magazine base plate', 'ammo', 'shell', 'Greifkante; schließt den Griff unten ab',
         'am Magazin', [(-66 * t - 22, -66), (-66 * t + 16, -66), (-75 * t + 16, -75), (-75 * t - 22, -75)], 30,
         bevel=R_SMALL, parent_part='magazine'),
    prof('trigger', 'Abzug', 'Trigger', 'grip_controls', 'metal', 'Feuer auslösen', 'Drehpunkt im Rahmen',
         [(30, 30), (36, 30), (38, 16), (34, 6), (31, 7), (32, 18)], 6, bevel=R_FINE,
         move=dict(kind='rotate', pivot=(33, 29, 0), axis='x', range_deg=(0, -12), event='fire', expect=((34, 6, 0), (-1, 0, 0)))),
    prof('trigger_guard', 'Abzugsbügel', 'Trigger guard', 'grip_controls', 'graphite', 'Schützt den Abzug',
         'Teil des Rahmens', [(14, -2), (64, -2), (68, 4), (68, 31), (61, 31), (61, 5), (14, 5)], 14, bevel=R_SMALL),
    box('slide_stop', 'Schlittenfang', 'Slide stop', 'grip_controls', 'accent', 'Hält den Schlitten nach dem letzten Schuss offen',
        'links am Rahmen (dreht)', 46, 70, 42, 47, 2.4, bevel=R_FINE, x=13.8),
    cyl('mag_release', 'Magazinhalter', 'Magazine release', 'grip_controls', 'accent', 'Löst das Magazin', 'links im Rahmen',
        'x', (16, 36), 12, 15.5, 4, segs=16, move=dict(kind='translate', pivot=(16, 36, 14), vector_mm=(0, 0, -2.5), event='reload')),
]
PARTS += iron_sights(-42, 152, 74, h=7)
for p in PARTS:
    if p['id'].startswith('rear_sight') or p['id'] == 'front_sight':
        p['parent_part'] = 'slide'
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip'),
    'Socket_Muzzle': dict(at=(174, BORE, 0), part='barrel'),
    'Socket_Sight': dict(at=(-42, 80, 0), part='rear_sight_l', note='Kimme'),
    'Socket_Eye': dict(at=(-200, 80, 0), part='rear_sight_l', note='Vorschlag: Augenabstand ausgestreckter Arm, Wert offen'),
}
ACTIONS = {
    'fire_semi': dict(de='Einzelschuss (Schlitten)', frames=10, step=1, keys={
        'trigger': [(0, 0), (2, 1), (6, 0)], 'slide': [(0, 0), (2, 0), (4, 1), (8, 0)]}, events=[(2, 'shot')]),
    'reload_empty': dict(de='Nachladen aus leerem Zustand', frames=60, keys={
        'mag_release': [(0, 0), (4, 1), (10, 0)], 'magazine': [(0, 0), (4, 0), (14, 1), (28, 1), (40, 0)],
        'slide': [(0, 1), (44, 1), (50, 0)]},
        events=[(14, 'mag_out'), (40, 'mag_seated'), (50, 'slide_release'), (54, 'ready')]),
}
