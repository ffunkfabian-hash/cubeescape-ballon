"""BASIC-12 v2.1 – Spurgewehr im Stil v2.1 („Destiny-Detaildichte + AAA-Material, schlicht“), Familie des Piloten BASIC-01 v2.1.

Recherche (docs/quellen.md › Q-D2-IMG, gesichtet 28.10.2026, Bungie-Manifest): Keraunios und Retraced Path (lange helle Oberschale,
die vorn über den Emitter auskragt; darunter frei ein runder Strahlkanal; runde Scheibe am Übergang Gehäuse → Kanal; Zelle wie ein
Magazin vor dem Griff; geschlossener Schaft mit Daumenloch), Ribbontail (gestufte Schale über rundem Kern, Scheibe mittig).
Nur Prinzipien; Leitmerkmal 12 nach Designvertrag: rundes Fokusrohr mit Kegel, Einteilkörper (BST-T, kein Schaftrohr).

Formsprache-Checkliste (stilhandbuch §3):
| Frage | Spurgewehr v2.1 |
|---|---|
| Leitmerkmal der Silhouette | gerade Creme-Oberkante vom Schaft bis zur Haubenspitze; die schmale Haube kragt über das freie, runde Fokusrohr mit drei Ringen und den gestuften Fokuskegel aus |
| Schichten | Unteres Gehäuse, Fokusrohr (Graphit) → Gehäuse, Haube und Einteilkörper (Creme, Fuge 1 mm) → Seitenpaneele und Fokusscheibe (eloxiert) → Schiene → Visier H3 |
| Negativraum | Keil zwischen Haubenschürze und Fokusrohr: hinten umgreift die Haube das Rohr bis zur Achse, nach vorn öffnet sich der Spalt bis zum freien Kegel (Rohr unten frei); Daumenloch im Einteilkörper |
| Blickfang | Fokusscheibe: dunkle Scheibe mit blankem Ring am Übergang Gehäuse → Rohr, Mitte leuchtet beim Strahl (beidseitig) |
| Zweiton-Blockung | Gehäuse, Haube, Einteilkörper Lack (`shell`), Unteres Gehäuse und Fokusrohr Polymer (`graphite`), Kegel `dark_metal` |
| Grafik | ein Schrägband vorn an der Haube, ein Schriftzug „BASIC TR-12“ (hell auf Graphit) |
| Front | Fokuskegel zweistufig (Kegel, schmale Spitze) mit blanker Krone um die Fokuslinse; die Haubenspitze schützt die Linse |
| Übergänge | Zellentrichter im Unteren Gehäuse angeformt; Einteilkörper geht ohne Schaftrohr aus dem Gehäuse hervor (Fuge 1 mm) |
| Ergonomie | Griff BGM-1 in v2.1-Form (Familie), Energiezelle vor dem Griff wie ein Magazin, Griffband auf dem Fokusrohr für die Stützhand |

Visier: H3 „Zinken“ (Baukasten v3, visier-konzept › 6a; `sight_kit.zinken`): zwei Seitenplatten 15° nach außen, oben offen,
Emitterpunkt zum Auge; Absehen gezeichnet (Hüftform `circle_cross` flach im Glas). Größe M (Glas unten 15,6 / oben 25,8 mm, 18,7 %).
H9 Klappe und H7 Schirm nur als Varianten im Katalog.
Schlichtheitsbudget: Leuchten 3 Funktionen (Strahl: Fokuslinse und Scheibenmitte · Munition: Ladefenster der Zelle · Visier:
Emitterpunkt und Absehen) · Grafik 1 Band · Schrift 1 · Orange 2 (Zellenhalter, Klemmhebel des Visiers) · Schrauben nur an
Paneelen, Haubenstütze und Einteilkörper.
Proportion: Länge ≈ 0,78 m (v1 0,87 m), H/L 0,33; Destiny-Spurgewehre beobachtet H/L ≈ 0,40–0,55 (Bericht 0.27, grob aus 3/4-Bildern).
Bewegung (Daten): Abzug, Fokuslinse und Scheibenmitte leuchten beim Strahl (`beam`), Zelle senkrecht nach unten heraus (`reload`),
Zellenhalter. Energiewaffe: **kein Hülsenauswurf** (`EJECT = None`, Daten statt Sonderlogik).
Status: Maße entworfen (Länge kürzer als v1, an Familie 10 angelehnt; gemessene Werte im Spec), Formprinzipien abgeleitet.
"""
from basic.common import (part, prof, box, cyl, cut_box, screws, mirror, rail, grip_v21, R_MID, R_SMALL, R_FINE)
from basic.pilot.optics.sight_kit import zinken
from basic.weapons import w12_trace_rifle as V1

META = dict(V1.META, variant='v2.1', name='Leitstrahl v2.1', nick='Familie v2.1',
            summary='Spurgewehr mit freiem Fokusrohr unter auskragender Haube, Fokusscheibe, Einteilkörper und Visier H3 (Stil v2.1).')
ASSEMBLIES = V1.ASSEMBLIES
GRIP_TOP = 40
BORE = 96                    # Strahlachse
TOP = 128                    # Oberkante Gehäuse, Haube, Einteilkörper; Schiene bis u 136, Visierlinie u 162 (Visierhöhe 66)
REC1 = 176                   # Vorderkante Gehäuse (Fuge zur Haube)
TUBE_R = 16.0                # Fokusrohr Ø 32
HOOD0 = 90                   # Haube beginnt auf dem Gehäuse (hinter der Fokusscheibe), Stufe 2 mm seitlich
HOOD_TOP = 138               # Oberkante der Haube in Linie mit der Schienenoberkante (u 136): 24 mm unter der Visierlinie wie 01
# Unterkante der Haube vor dem Gehäuse: hinten bis zur Rohrachse (umgreift den Rohransatz), Mitte 12 mm über dem Rohr (offenes Fenster
# über Rohr und Ringen, Negativraum), vorn wieder herab um den Kegel (Nase)
SKIRT = ((REC1 + 1, BORE), (226, 124), (424, 124), (470, 104))
HOOD_W = (48, 30)            # Haubenbreite hinten (2 mm Stufe über dem Gehäuse) und an der Nase
TUBE1 = 448                  # Rohrende = Kegelansatz
TIP = 496                    # Stirn der Fokuslinse (Socket_Muzzle)
HOOD1 = 500                  # Haubennase, 4 mm vor der Linse
CELL = (86, 126)             # Energiezelle vor dem Griff (f; wie BASIC-10, 3 mm vor dem Abzugsbügel)
DISC = (150, 100, 19.0)      # Fokusscheibe: Mitte f, u und Radius (beidseitig am Gehäuse)
W_REC = 44

P = []
# ---------------------------------------------------------------- Gehäuse
P += [
    prof('receiver', 'Gehäuse', 'Receiver', 'receiver', 'shell', 'Tragkörper für Fokusrohr, Zellenschacht und Schiene',
         'mit dem Unteren Gehäuse über zwei Querbolzen (fest); vorn unten abgeschrägt', [(-110, 82), (REC1 - 16, 82), (REC1, 92), (REC1, TOP),
                                                                                       (-104, TOP), (-110, TOP - 6)], W_REC,
         cuts=[cut_box(-92, -10, 92, 116, 3.0, x=22.6), cut_box(-92, -10, 92, 116, 3.0, x=-22.6)]),       # Paneel-Mulden
    prof('lower', 'Unteres Gehäuse', 'Lower receiver', 'receiver', 'graphite', 'Griffmodul, Abzugsgruppe, Zellenschacht',
         'unter dem Gehäuse, Fuge 1 mm; Zellentrichter angeformt',
         [(-110, 62), (-62, 40), (CELL[0] - 14, 40), (CELL[0] - 8, 28), (CELL[0] - 4, 20), (CELL[1] + 4, 20), (CELL[1] + 10, 30),
          (REC1 - 16, 66), (REC1 - 16, 81), (-110, 81)], 42),
    prof('cell_lip', 'Schachtlippe', 'Cell well lip', 'receiver', 'trim', 'Blanke Einführkante des Zellenschachts',
         'unten am Trichter des Unteren Gehäuses', [(CELL[0] - 1.5, 17.5), (CELL[1] + 5, 17.5), (CELL[1] + 6, 21), (CELL[0] - 2.5, 21)], 43,
         bevel=0.6, iface='BEC-1'),
    box('side_panel_l', 'Seitenpaneel links', 'Side panel left', 'receiver', 'anodized', 'Wartungsdeckel über der Steuerung',
        'in die Mulde geschraubt (4 Schrauben)', -90, -12, 94, 114, 1.2, bevel=R_FINE, x=21.2),
    box('side_panel_r', 'Seitenpaneel rechts', 'Side panel right', 'receiver', 'anodized', 'Wartungsdeckel über der Steuerung',
        'in die Mulde geschraubt (4 Schrauben)', -90, -12, 94, 114, 1.2, bevel=R_FINE, x=-21.2),
    part('panel_screws', 'Paneelschrauben', 'Panel screws', 'receiver', 'multi', 'trim', 'Halten die Seitenpaneele',
         'in den Paneelen', bevel=0.2, items=mirror(screws([(-86, 98), (-86, 110), (-16, 98), (-16, 110)], 21.8, r=1.6, h=0.8))),
    part('takedown_pins', 'Querbolzen', 'Takedown pins', 'receiver', 'multi', 'metal', 'Verbinden Gehäuse und Unteres Gehäuse',
         'quer durch das Gehäuse (lösbar)', bevel=0.4, items=mirror(screws([(-96, 74), (146, 74)], 21.0, r=3.6, h=1.0))),
    part('cell_release', 'Zellenhalter', 'Cell release', 'grip_controls', 'cyl', 'accent', 'Löst die Energiezelle',
         'Druckknopf links', bevel=R_FINE, axis='x', c=(CELL[0] - 10, 54), a0=19, a1=23.5, r=5, segs=20,
         move=dict(kind='translate', pivot=(CELL[0] - 10, 54, 21), vector_mm=(0, 0, -2.5), event='reload',
                   expect=((CELL[0] - 10, 54, 23.5), (0, 0, -1)))),
    # Fokusscheibe (Blickfang): dunkle Scheibe mit blankem Ring, Mitte leuchtet beim Strahl; beidseitig am Gehäuse vor dem Rohransatz
    part('focus_disc', 'Fokusscheibe', 'Focus disc', 'receiver', 'multi', 'anodized', 'Deckel der Fokuskammer am Rohransatz (beidseitig)',
         'in das Gehäuse eingelassen', bevel=0.6, smooth=True,
         items=mirror([dict(shape='cyl', axis='x', c=DISC[:2], a0=W_REC / 2 - 0.6, a1=W_REC / 2 + 1.6, r=DISC[2], segs=48)])),
    part('focus_disc_ring', 'Scheibenring', 'Disc ring', 'receiver', 'multi', 'trim', 'Blanker Ring um die Fokusscheibe',
         'um die Scheibe geschraubt', bevel=0.4, smooth=True,
         items=mirror([dict(shape='cyl', axis='x', c=DISC[:2], a0=W_REC / 2 - 0.6, a1=W_REC / 2 + 2.4, r=DISC[2] + 2.2, r_in=DISC[2] + 0.2,
                            segs=48)])),
    part('disc_lens', 'Scheibenmitte', 'Disc lens', 'receiver', 'multi', 'energy', 'Leuchtet beim Strahl (Fokuskammer aktiv)',
         'in der Mitte der Fokusscheibe', bevel=0, smooth=True,
         items=mirror([dict(shape='cyl', axis='x', c=DISC[:2], a0=W_REC / 2 + 1.4, a1=W_REC / 2 + 1.9, r=5.0, segs=32)]),
         move=dict(kind='glow', pivot=None, event='beam', max=5.0)),
]
P += [dict(p, mat='anodized') for p in rail(-60, 70, TOP)]
P[-1]['cuts'] = [cut_box(-52 + 14 * i, -45 + 14 * i, TOP + 4, TOP + 9, 30) for i in range(9)]
# Visier H3 „Zinken“ (Baukasten v3, Standard Spur nach visier-konzept › 6a)
_sight, SIGHT_ANCHORS = zinken(-12, TOP + 8, weapon_type=V1.META['type'])
P += _sight
# ---------------------------------------------------------------- Fokusrohr (Leitmerkmal), Haube, Kegel
RINGS = (196, 320, 404)      # Ringe 10 mm; zwischen Ring 1 und 2 das Griffband der Stützhand
P += [
    cyl('focus_tube', 'Fokusrohr', 'Focus tube', 'support', 'graphite', 'Umschließt den Strahlkanal; frei unter der Haube',
        'im Gehäuse verschraubt', 'f', (BORE, 0), REC1 - 4, TUBE1, TUBE_R, segs=40, bevel=R_SMALL, smooth=True),
    cyl('tube_grip', 'Griffband', 'Grip band', 'support', 'rubber', 'Rutschfeste Zone für die Stützhand', 'auf das Fokusrohr gezogen',
        'f', (BORE, 0), 218, 300, TUBE_R + 1.0, segs=40, bevel=R_SMALL, smooth=True),
]
for i, f0 in enumerate(RINGS):
    P.append(cyl(f'focus_ring_{i + 1}', f'Fokusring {i + 1}', f'Focus ring {i + 1}', 'support', 'dark_metal',
                 'Hält die Fokusspule; gliedert das Rohr', 'auf das Fokusrohr gepresst', 'f', (BORE, 0), f0, f0 + 10, TUBE_R + 4,
                 r_in=TUBE_R - 0.2, segs=40, bevel=R_FINE, smooth=True))
P += [
    part('ring_rims', 'Ringkanten', 'Ring rims', 'support', 'multi', 'trim', 'Blanke Stirnkanten der Fokusringe', 'vorn an den Ringen',
         bevel=0.3, smooth=True, items=[dict(shape='cyl', axis='f', c=(BORE, 0), a0=f0 + 9.4, a1=f0 + 10.6, r=TUBE_R + 4.4,
                                              r_in=TUBE_R + 1.5, segs=40) for f0 in RINGS]),
    part('hood', 'Haube', 'Top hood', 'barrel', 'plan', 'shell',
         'Oberschale vom Gehäuse bis vor den Kegel; umgreift das Rohr hinten und den Kegel vorn, dazwischen offen',
         'auf dem Gehäuse verschraubt (Stufe 2 mm), vorn auf den Kegel geklemmt', bevel=R_SMALL,
         pts=[(HOOD0, -HOOD_W[0] / 2), (300, -HOOD_W[0] / 2 + 3), (HOOD1, -HOOD_W[1] / 2), (HOOD1, HOOD_W[1] / 2),
              (300, HOOD_W[0] / 2 - 3), (HOOD0, HOOD_W[0] / 2)], u0=BORE, u1=HOOD_TOP,
         cuts=[dict(shape='prof', pts=[(HOOD0 - 2, BORE - 6), (HOOD0 - 2, TOP), (REC1, TOP), (REC1, BORE - 6)], w=60),   # liegt auf dem Gehäuse
               dict(shape='prof', pts=[(REC1 - 2, BORE - 6)] + list(SKIRT) + [(HOOD1 + 8, SKIRT[-1][1]), (HOOD1 + 8, BORE - 6)], w=60),
               dict(shape='prof', pts=[(HOOD1 - 14, HOOD_TOP + 6), (HOOD1 + 6, HOOD_TOP + 6), (HOOD1 + 6, BORE)], w=60),   # Nase schräg
               dict(shape='cyl', axis='f', c=(BORE, 0), a0=REC1 - 2, a1=HOOD1 + 8, r=TUBE_R + 4.5, segs=48)]),          # Kanal um das Rohr
    part('hood_screws', 'Haubenschrauben', 'Hood screws', 'barrel', 'multi', 'trim', 'Halten die Haube am Gehäuse und am Kegel',
         'seitlich', bevel=0.2, items=mirror(screws([(186, 110), (HOOD1 - 26, 112)], HOOD_W[1] / 2 + 0.6, r=1.6, h=0.8))),
    part('band_side', 'Schrägband', 'Slanted band', 'barrel', 'multi', 'accent', 'Lackiertes Band (einziges Grafikelement)',
         'lackiert', bevel=0, items=[dict(shape='prof', pts=[(404, 124.5), (416, 124.5), (422, HOOD_TOP - 0.5), (410, HOOD_TOP - 0.5)],
                                           w=0.3, x=sx * (HOOD_W[0] / 2 - 3 - (HOOD_W[0] / 2 - 3 - HOOD_W[1] / 2) * (413 - 300) / (HOOD1 - 300) + 0.15))
                                      for sx in (1, -1)]),
    # Fokuskegel zweistufig mit blanker Krone und Fokuslinse
    cyl('focus_cone', 'Fokuskegel', 'Focus cone', 'barrel', 'dark_metal', 'Verjüngt den Strahl', 'auf das Fokusrohr gesteckt',
        'f', (BORE, 0), TUBE1 - 2, TIP - 10, TUBE_R + 4, r1=11, segs=40, bevel=R_SMALL, smooth=True),
    cyl('focus_tip', 'Fokusspitze', 'Focus tip', 'barrel', 'dark_metal', 'Schmale Stufe vor der Linse', 'vorn im Kegel',
        'f', (BORE, 0), TIP - 11, TIP - 1, 9, segs=40, bevel=R_FINE, smooth=True),
    cyl('focus_crown', 'Fokuskrone', 'Focus crown', 'barrel', 'trim', 'Blanke Stirnkante um die Linse', 'vorn an der Spitze',
        'f', (BORE, 0), TIP - 2, TIP + 0.5, 9.4, r_in=6.2, segs=40, bevel=0.4, smooth=True),
    cyl('focus_lens', 'Fokuslinse', 'Focus lens', 'barrel', 'energy', 'Leuchtet bei aktivem Strahl', 'in der Kegelspitze',
        'f', (BORE, 0), TIP - 2.5, TIP, 6.2, bevel=0, segs=32, move=dict(kind='glow', pivot=None, event='beam', max=6.0)),
    part('text_l', 'Schriftzug', 'Lettering', 'receiver', 'text', 'decal', 'Kennung „BASIC TR-12“ (einzige Schrift)',
         'aufgedruckt', bevel=0, text='BASIC  TR-12', size=5.0, f=-100, u=68, x=21.05, side=1, depth=0.12),
]
# ---------------------------------------------------------------- Griff, Zelle, Einteilkörper (BST-T) mit Daumenloch
P += grip_v21(top=GRIP_TOP)
_cc = ((CELL[0] + CELL[1]) / 2, 10)
P += [
    part('energy_cell', 'Energiezelle', 'Energy cell', 'ammo', 'prof', 'dark_metal', 'Speichert die Ladung; austauschbar',
         'rastet im Zellenschacht ein (lösbar)', bevel=R_MID, iface='BEC-1', w=24,
         pts=[(CELL[0], 60), (CELL[1], 60), (CELL[1], -26), (CELL[1] - 4, -32), (CELL[0] + 4, -32), (CELL[0], -26)],
         move=dict(kind='translate', pivot=(_cc[0], _cc[1], 0), vector_mm=(0, -110, 0), event='reload', removable=True,
                   expect=((_cc[0], -32, 0), (0, -1, 0)))),
    box('cell_band', 'Zellenband', 'Cell band', 'ammo', 'trim', 'Blankes Band über dem Zellenboden; Greifkante',
        'um die Zelle', CELL[0] - 0.6, CELL[1] + 0.6, -24, -20, 25.2, bevel=0.4, parent_part='energy_cell'),
    box('cell_window', 'Ladefenster', 'Charge window', 'ammo', 'energy', 'Zeigt den Ladezustand der Zelle',
        'links in die Zelle eingelassen', CELL[1] - 12, CELL[1] - 7, -14, 8, 1.0, bevel=0.3, x=12.2, parent_part='energy_cell'),
]
_B0, _B1 = -111, -262        # Einteilkörper: Fuge am Gehäuse, Schaftende
P += [
    prof('rear_body', 'Hinterkörper', 'Rear body', 'stock', 'shell', 'Einteilige Fortsetzung des Gehäuses bis zur Schulter; Daumenloch',
         'mit dem Gehäuse verschraubt, Fuge 1 mm', [(_B0, 62), (_B0, TOP), (_B1 + 10, TOP - 2), (_B1, TOP - 8), (_B1, 26), (_B1 + 18, 20),
                                                    (-170, 40), (-128, 58)], 40, iface='BST-T',
         cuts=[dict(shape='prof', pts=[(-132, 70), (-132, 110), (-200, 112), (-226, 102), (-232, 60), (-214, 44), (-176, 54)], w=50)]),
    prof('butt_pad', 'Schaftkappe', 'Butt pad', 'stock', 'rubber', 'Rutschfeste Anlage an der Schulter', 'auf das Körperende gesteckt',
         [(_B1 + 1, 18), (_B1 + 1, TOP - 6), (_B1 - 12, TOP - 8), (_B1 - 15, TOP - 20), (_B1 - 15, 28), (_B1 - 12, 20)], 42, bevel=R_MID),
    part('stock_bolts', 'Schaftbolzen', 'Stock bolts', 'stock', 'multi', 'trim', 'Halten den Hinterkörper am Gehäuse',
         'quer durch den Körperansatz', bevel=0.3, items=mirror(screws([(_B0 - 10, 120), (_B0 - 10, 66)], 20.4, r=2.6, h=1.0))),
]
PARTS = P
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip', note='Haupthand, auf der Griffachse'),
    'Socket_SupportHand': dict(at=(259, BORE - TUBE_R - 1, 0), part='tube_grip', note='Stützhand umgreift das Fokusrohr (Griffband)'),
    'Socket_Muzzle': dict(at=(TIP, BORE, 0), part='focus_lens', note='Stirn der Fokuslinse auf der Strahlachse'),
    'Socket_Cell': dict(at=(_cc[0], 20, 0), part='energy_cell', note='Einrastpunkt der Energiezelle (Schnittstelle BEC-1)'),
}
ANCHORS.update(SIGHT_ANCHORS)
_beam = [(0, 0), (4, 1), (28, 1), (32, 0)]
ACTIONS = {
    'beam': dict(de='Strahl halten und loslassen', frames=36, step=1, keys={
        'trigger': [(0, 0), (2, 1), (28, 1), (31, 0)], 'focus_lens': _beam, 'disc_lens': _beam},
        events=[(4, 'beam_start'), (28, 'beam_end')], view=(0.8, -0.3, 0.45)),
    'reload': dict(de='Energiezelle wechseln', frames=70, keys={'cell_release': [(0, 0), (6, 1), (14, 1), (18, 0)],
                                                                'energy_cell': [(0, 0), (16, 1), (34, 1), (50, 0)]},
                   events=[(16, 'cell_out'), (50, 'cell_in'), (58, 'ready')], view=(0.8, -0.3, 0.45)),
}
EXPLODE = {'sight': (0, 110, 0), 'ammo': (0, -140, 0), 'stock': (-110, 0, 0), 'barrel': (150, 40, 0), 'support': (60, -60, 0),
           'grip_controls': (-10, -80, 0), 'receiver': (0, 0, 0)}
SIGHT_ID = 'H3'    # Visier des Baukastens v3 (visier-konzept › 6a); test_sights prüft dessen Pflichtteile und Merkmale
EJECT = None    # Energiewaffe: keine Hülse (Daten statt Sonderlogik; check: Energiezelle BEC-1 → EJECT None)
