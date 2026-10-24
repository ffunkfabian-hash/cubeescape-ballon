"""BASIC-14 Raketenwerfer (Rocket Launcher): Schulterrohr mit Ladung von hinten.

Großes Creme-Rohr, Mündungs- und Heckring, aufklappbarer Heckverschluss (seitliches Scharnier), Graphit-Schulterauflage,
Griffmodul und Vordergriff unter dem Rohr, großes Holo-Visier auf einem Sockel.
"""
from basic.common import (prof, box, cyl, assemblies, grip_rifle, rail, reflex_sight, glow, R_BODY, R_MID, R_SMALL,
                          R_FINE)

META = dict(id='BASIC-14', num='14', type='rocket_launcher', type_de='Raketenwerfer', type_en='Rocket Launcher',
            name='Schulterrohr', nick='Standard', ammo='heavy', fire='single_shot', reference_length_m=0.725,
            reference_length_source='Toolgen rocket_launcher (Formgen KG09 spec units); BASIC bewusst länger, siehe Bericht',
            reference_note='Toolgens Raketenwerfer ist mit 0,725 m ein verdichtetes Spielmodell; BASIC zeigt das Schulterrohr in Gebrauchslänge (entworfen)',
            summary='Einschüssiges Schulterrohr mit Heckladung.')
ASSEMBLIES = assemblies('receiver', 'barrel', 'ammo', 'sight', 'grip_controls', 'support', 'stock', 'mechanism')
AX = 112
R = 50
PARTS = [
    cyl('tube', 'Abschussrohr', 'Launch tube', 'receiver', 'shell', 'Hauptkörper; führt die Rakete', 'Grundkörper',
        'f', (AX, 0), -330, 560, R, segs=32, bevel=R_SMALL, r_in=40),
    cyl('muzzle', 'Mündungsring', 'Muzzle ring', 'barrel', 'dark_metal', 'Mündung; Socket_Muzzle', 'auf das Rohr gepresst',
        'f', (AX, 0), 540, 590, R + 5, segs=32, bevel=R_SMALL, r_in=40),
    cyl('rear_ring', 'Heckring', 'Rear ring', 'barrel', 'dark_metal', 'Trägt das Scharnier des Heckverschlusses',
        'auf das Rohr gepresst', 'f', (AX, 0), -340, -300, R + 5, segs=32, bevel=R_SMALL, r_in=40),
    cyl('breech_cap', 'Heckverschluss', 'Breech cap', 'mechanism', 'graphite', 'Verschließt das Heck; klappt zum Laden auf',
        'Scharnier links am Heckring', 'f', (AX, 0), -356, -340, R + 3, segs=32, bevel=R_MID,
        move=dict(kind='rotate', pivot=(-348, AX, R + 4), axis='u', range_deg=(0, -105), event='reload',
                  expect=((-348, AX, 0), (-1, 0, 0)))),
    cyl('rocket', 'Rakete', 'Rocket', 'ammo', 'dark_metal', 'Eine Rakete im Rohr (Ruhelage verdeckt)',
        'im Rohr', 'f', (AX, 0), -290, 420, 36, segs=24, bevel=R_SMALL,
        move=dict(kind='translate', pivot=(60, AX, 0), vector_mm=(-880, 0, 0), event='load',
                  note='Ruhelage = geladen; die Ladeaktion beginnt hinter dem Rohr', removable=True)),
    cyl('rocket_nose', 'Raketenspitze', 'Rocket nose', 'ammo', 'accent', 'Gefechtskopf', 'an der Rakete', 'f', (AX, 0),
        418, 480, 36, r1=10, segs=24, bevel=R_SMALL, parent_part='rocket'),
    prof('shoulder_rest', 'Schulterauflage', 'Shoulder rest', 'stock', 'graphite', 'Liegt auf der Schulter',
         'unter das Rohr geschraubt', [(-270, 70), (-120, 70), (-110, 58), (-130, 50), (-260, 50), (-280, 58)], 56),
    box('trigger_housing', 'Abzugsgehäuse', 'Trigger housing', 'grip_controls', 'graphite', 'Verbindet Griffmodul und Rohr',
        'unter das Rohr geschraubt', -40, 90, 44, 70, 36, bevel=R_MID),
    prof('foregrip', 'Vordergriff', 'Foregrip', 'support', 'graphite', 'Griff der Stützhand', 'unter das Rohr geschraubt',
         [(210, 66), (250, 66), (246, -2), (238, -8), (218, -8), (212, -2)], 30),
    box('sight_riser', 'Visiersockel', 'Sight riser', 'sight', 'shell', 'Hebt das Visier über das Rohr',
        'auf dem Rohr verschraubt', -110, 70, 158, 170, 30, bevel=R_MID),
    glow('ready_light', 'Bereitschaftsanzeige', 'Ready light', 'receiver', -60, -20, 120, 132, x=R + 0.4,
         func='Leuchtet, wenn eine Rakete geladen ist'),
]
PARTS += rail(-100, 60, 170)
_s, SA, LINE = reflex_sight(-70, 178, win_w=44, win_h=30)
PARTS += _s
PARTS += grip_rifle(top=44)
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip'),
    'Socket_SupportHand': dict(at=(230, 30, 0), part='foregrip'),
    'Socket_Muzzle': dict(at=(590, AX, 0), part='muzzle'),
    'Socket_Breech': dict(at=(-356, AX, 0), part='breech_cap', note='Ladeöffnung hinten'),
}
ANCHORS.update(SA)
ACTIONS = {
    'fire': dict(de='Abschuss', frames=12, step=1, keys={'trigger': [(0, 0), (2, 1), (6, 0)],
                                                         'ready_light': [(0, 1), (2, 1), (4, 0), (12, 0)]},
                 events=[(2, 'launch')]),
    'reload': dict(de='Heck öffnen, Rakete einschieben, schließen', frames=96, keys={
        'breech_cap': [(0, 0), (14, 1), (70, 1), (82, 0)], 'rocket': [(0, 1), (20, 1), (60, 0)],
        'ready_light': [(0, 0), (82, 0), (86, 1), (96, 1)]},
        events=[(14, 'breech_open'), (60, 'rocket_in'), (82, 'breech_closed'), (86, 'ready')], view=(-0.6, 0.75, 0.4)),
}
EXPLODE = {'mechanism': (-80, 0, 40), 'ammo': (0, 120, 0), 'stock': (0, -60, 0)}
