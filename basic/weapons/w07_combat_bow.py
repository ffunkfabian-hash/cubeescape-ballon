"""BASIC-07 Bogen (Combat Bow): gewöhnlicher Kampfbogen mit Pfeil, Sehne und Auszug.

Mittelstück in Creme mit Graphitgriff und Pfeilfenster rechts, zwei Recurve-Wurfarme, Rollen an den Spitzen, Sehne aus
zwei Hälften (folgt dem Nockpunkt), Pfeil mit Nocke und Befiederung, kleines Ringvisier mit Leuchtpin.
"""
from basic.common import prof, box, cyl, part, assemblies, band, R_BODY, R_MID, R_SMALL, R_FINE

META = dict(id='BASIC-07', num='07', type='combat_bow', type_de='Bogen', type_en='Combat Bow', name='Sehnenzug',
            nick='Standard', ammo='primary', fire='draw_release', reference_length_m=1.018,
            reference_length_source='Toolgen 0.13 bow, größte Ausdehnung (Formgen KG10 spec units)',
            reference_axis='height_m', reference_note='Bogen: Bezug ist die größte Ausdehnung (Höhe), Länge = Pfeilrichtung',
            summary='Kampfbogen mit Recurve-Wurfarmen, Pfeilfenster und Ringvisier.')
ASSEMBLIES = assemblies('riser', 'limbs', 'string', 'arrow', 'sight', 'grip_controls')
ARROW_U = 46
TIP_F, TIP_U = -60, 505
DRAW = 380
_upper = [(14, 250), (30, 330), (16, 412), (-22, 480), (-60, TIP_U)]
_thick = [26, 24, 20, 15, 11]
PARTS = [
    prof('grip', 'Griff', 'Grip', 'grip_controls', 'graphite', 'Bogenhand; trägt Socket_Hand', 'auf das Mittelstück geschraubt',
         [(-22, -42), (18, -42), (26, -10), (22, 30), (-18, 30), (-25, -10)], 32, iface=None),
    prof('riser_lower', 'Mittelstück unten', 'Lower riser', 'riser', 'shell', 'Trägt den unteren Wurfarm',
         'Grundkörper', [(-18, -38), (26, -38), (44, -120), (50, -200), (38, -246), (-10, -246), (-6, -200), (-16, -120)], 32),
    prof('riser_upper', 'Mittelstück oben', 'Upper riser', 'riser', 'shell', 'Trägt den oberen Wurfarm und das Visier',
         'Grundkörper', [(-14, 68), (30, 68), (50, 150), (48, 215), (38, 246), (-10, 246), (-6, 200), (-12, 140)], 32),
    box('riser_bridge', 'Fensterbrücke', 'Window bridge', 'riser', 'shell', 'Verbindet beide Hälften links; rechts bleibt das Pfeilfenster frei',
        'Teil des Mittelstücks', -12, 30, 24, 74, 10, x=11),
    box('arrow_rest', 'Pfeilauflage', 'Arrow rest', 'riser', 'accent', 'Führt den Pfeil im Fenster', 'auf der Fensterbrücke',
        -2, 16, ARROW_U - 8, ARROW_U - 4, 10, bevel=R_FINE, x=1),
    box('pocket_top', 'Wurfarmaufnahme oben', 'Upper limb pocket', 'limbs', 'dark_metal', 'Klemmt den oberen Wurfarm',
        'am Mittelstück', -12, 42, 238, 258, 38, bevel=R_SMALL),
    box('pocket_bottom', 'Wurfarmaufnahme unten', 'Lower limb pocket', 'limbs', 'dark_metal', 'Klemmt den unteren Wurfarm',
        'am Mittelstück', -12, 42, -258, -238, 38, bevel=R_SMALL),
    prof('limb_top', 'Wurfarm oben', 'Upper limb', 'limbs', 'shell', 'Speichert die Zugenergie (Recurve)',
         'in der Aufnahme geklemmt', band(_upper, _thick), 34, bevel=R_MID),
    prof('limb_bottom', 'Wurfarm unten', 'Lower limb', 'limbs', 'shell', 'Speichert die Zugenergie (Recurve)',
         'in der Aufnahme geklemmt', band([(f, -u) for f, u in _upper], _thick), 34, bevel=R_MID),
    cyl('cam_top', 'Rolle oben', 'Upper cam', 'limbs', 'dark_metal', 'Sehnenende oben', 'an der Wurfarmspitze',
        'x', (TIP_F, TIP_U), -10, 10, 10, segs=16),
    cyl('cam_bottom', 'Rolle unten', 'Lower cam', 'limbs', 'dark_metal', 'Sehnenende unten', 'an der Wurfarmspitze',
        'x', (TIP_F, -TIP_U), -10, 10, 10, segs=16),
    cyl('string_top', 'Sehne oben', 'Upper string', 'string', 'string', 'Obere Sehnenhälfte; folgt dem Nockpunkt',
        'zwischen Rolle und Nockpunkt', 'u', (TIP_F, 0), ARROW_U, TIP_U, 1.8, bevel=0, segs=8,
        move=dict(kind='segment', pivot=(TIP_F, TIP_U, 0), tip=(TIP_F, TIP_U, 0), nock=(TIP_F, ARROW_U, 0),
                  vector_mm=(-DRAW, 0, 0), event='draw')),
    cyl('string_bottom', 'Sehne unten', 'Lower string', 'string', 'string', 'Untere Sehnenhälfte; folgt dem Nockpunkt',
        'zwischen Rolle und Nockpunkt', 'u', (TIP_F, 0), -TIP_U, ARROW_U, 1.8, bevel=0, segs=8,
        move=dict(kind='segment', pivot=(TIP_F, -TIP_U, 0), tip=(TIP_F, -TIP_U, 0), nock=(TIP_F, ARROW_U, 0),
                  vector_mm=(-DRAW, 0, 0), event='draw')),
    cyl('arrow_shaft', 'Pfeilschaft', 'Arrow shaft', 'arrow', 'graphite', 'Pfeil; wird mit der Sehne zurückgezogen',
        'auf der Auflage, Nocke an der Sehne', 'f', (ARROW_U, 0), TIP_F, 560, 3.5, segs=10,
        removable=True, move=dict(kind='translate', pivot=(TIP_F, ARROW_U, 0), vector_mm=(-DRAW, 0, 0), event='draw')),
    cyl('arrow_head', 'Pfeilspitze', 'Arrow head', 'arrow', 'dark_metal', 'Spitze', 'auf dem Schaft', 'f', (ARROW_U, 0),
        556, 616, 7, r1=0.6, segs=6, bevel=R_FINE, parent_part='arrow_shaft'),
    cyl('arrow_nock', 'Nocke', 'Nock', 'arrow', 'accent', 'Rastet an der Sehne ein', 'Schaftende', 'f', (ARROW_U, 0),
        TIP_F - 6, TIP_F + 6, 4.5, segs=10, parent_part='arrow_shaft'),
    prof('fletch_top', 'Befiederung oben', 'Top vane', 'arrow', 'accent', 'Stabilisiert den Flug (Leitfeder)', 'am Schaft',
         [(TIP_F + 14, ARROW_U), (TIP_F + 76, ARROW_U), (TIP_F + 70, ARROW_U + 12), (TIP_F + 22, ARROW_U + 13)], 1.2,
         bevel=0.3, parent_part='arrow_shaft'),
    part('fletch_l', 'Befiederung links', 'Left vane', 'arrow', 'plan', 'graphite', 'Stabilisiert den Flug', 'am Schaft',
         bevel=0.3, parent_part='arrow_shaft', u0=ARROW_U - 0.6, u1=ARROW_U + 0.6,
         pts=[(TIP_F + 14, 2), (TIP_F + 76, 2), (TIP_F + 70, 13), (TIP_F + 22, 14)]),
    part('fletch_r', 'Befiederung rechts', 'Right vane', 'arrow', 'plan', 'graphite', 'Stabilisiert den Flug', 'am Schaft',
         bevel=0.3, parent_part='arrow_shaft', u0=ARROW_U - 0.6, u1=ARROW_U + 0.6,
         pts=[(TIP_F + 14, -2), (TIP_F + 22, -14), (TIP_F + 70, -13), (TIP_F + 76, -2)]),
    box('sight_arm', 'Visierarm', 'Sight arm', 'sight', 'dark_metal', 'Trägt den Visierring vor dem Mittelstück',
        'am Mittelstück verschraubt', 26, 60, 78, 84, 6, bevel=R_FINE),
    part('sight_ring', 'Visierring', 'Sight ring', 'sight', 'frame', 'graphite', 'Ringvisier; frei durchsichtig',
         'am Visierarm', bevel=R_FINE, f0=54, f1=60, cu=64, ow=26, oh=26, iw=19, ih=19, r_out=12, r_in=9),
    box('sight_pin', 'Leuchtpin', 'Sight pin', 'sight', 'energy', 'Zielpunkt in Ringmitte', 'im Visierring',
        56, 58, 63, 66, 1.6, bevel=0.2),
    box('sight_pin_post', 'Pinträger', 'Pin post', 'sight', 'dark_metal', 'Hält den Leuchtpin', 'im Visierring',
        56, 58, 54, 63, 1.2, bevel=0.2),
]
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip', note='Bogenhand'),
    'Socket_Nock': dict(at=(TIP_F, ARROW_U, 0), part='string_top', note='Nockpunkt in Ruhe (Toolgen-Name)'),
    'Socket_ArrowTip': dict(at=(616, ARROW_U, 0), part='arrow_head', note='Pfeilspitze in Ruhe (Toolgen-Name)'),
    'Socket_Muzzle': dict(at=(8, ARROW_U, 0), part='arrow_rest', note='Abgangspunkt des Pfeils an der Auflage'),
    'Socket_Sight': dict(at=(54, 64, 0), part='sight_ring', note='Hinterkante Visierring'),
    'Socket_Eye': dict(at=(TIP_F - DRAW - 30, 70, 0), part='sight_ring', note='Vorschlag: Auge am Ankerpunkt bei vollem Auszug'),
}
ACTIONS = {
    'draw_hold_release': dict(de='Ausziehen, halten, lösen', frames=60, step=2, keys={
        'arrow_shaft': [(0, 0), (18, 1), (40, 1), (42, -0.4), (46, -4)], 'string_top': [(0, 0), (18, 1), (40, 1), (42, 0)],
        'string_bottom': [(0, 0), (18, 1), (40, 1), (42, 0)]},
        events=[(0, 'nocked'), (18, 'full_draw'), (40, 'release'), (42, 'shot'), (46, 'arrow_gone')], view=(-0.95, 0.15, 0.3)),
    'let_down': dict(de='Entspannen ohne Schuss', frames=40, keys={
        'arrow_shaft': [(0, 0), (16, 1), (24, 1), (40, 0)], 'string_top': [(0, 0), (16, 1), (24, 1), (40, 0)],
        'string_bottom': [(0, 0), (16, 1), (24, 1), (40, 0)]},
        events=[(16, 'full_draw'), (40, 'relaxed')], view=(-0.95, 0.15, 0.3)),
}
EXPLODE = {'arrow': (0, 0, -90), 'string': (-40, 0, 0), 'limbs': (0, 0, 0), 'sight': (60, 40, 0), 'grip_controls': (-60, 0, 0)}

HERO = (-0.92, -0.3, 0.22)
