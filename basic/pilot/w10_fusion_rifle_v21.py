"""BASIC-10 v2.1 – Fusionsgewehr im Stil v2.1 („Destiny-Detaildichte + AAA-Material, schlicht“), Familie des Piloten BASIC-01 v2.1.

Recherche (docs/quellen.md › Q-D2-IMG, gesichtet 28.10.2026, Bungie-Manifest): Cruoris FR4 und Erentil FR4 (kurzes hohes Gehäuse
über dem Griff, davor ein offener Bund paralleler Kondensatorrohre bis zur stumpfen Front), Nox Echo III (kastige helle Oberschale mit
flacher Stirn über dunkler Unterseite, Energiezelle als Block vor dem Griff), Main Ingredient (Zweiton hell oben / dunkel unten,
Zelle vor dem Griff, Skelettschaft). Nur Prinzipien; Leitmerkmal 10 nach Designvertrag: Spulenringe, Schlitz-Emitter.

Formsprache-Checkliste (stilhandbuch §3):
| Frage | Fusionsgewehr v2.1 |
|---|---|
| Leitmerkmal der Silhouette | gerade Creme-Oberkante vom Schaft bis zum Emitter; darunter die quer offene Ladekammer mit drei Spulenringen um den Glutkern, vorn ein gestufter Schlitz-Emitter als stumpfe Front |
| Schichten | Unteres Gehäuse, Handschutz, Schaft (Graphit) → Gehäuse und Kammerhaube (Creme, Fuge 1 mm) → Seitenpaneele (eloxiert) → Schiene → Visier F1 |
| Negativraum | Kammerfenster quer durch zwischen Haube und Handschutz (Spulen und Glutkern sichtbar); Daumenloch im Schaft S2 |
| Blickfang | Glutkern: leuchtender Ladekern zwischen den Spulenringen, beidseitig sichtbar |
| Zweiton-Blockung | Gehäuse und Kammerhaube Lack (`shell`), Unteres Gehäuse, Handschutz, Schaft Polymer (`graphite`), Emitter `dark_metal` |
| Grafik | ein Schrägband vorn an der Kammerhaube, ein Schriftzug „BASIC FR-10“ (hell auf Graphit) |
| Front | Schlitz-Emitter zweistufig (Block, schmalere Stirn) mit blanker Schlitzkrone; Kern endet sichtbar im Emitter |
| Übergänge | Zellentrichter im Unteren Gehäuse angeformt; Haube und Handschutz enden im Emitterblock (Fuge 1 mm) |
| Ergonomie | Griff BGM-1 in v2.1-Form (Familie), Energiezelle vor dem Griff wie ein Magazin, Griffpolster unter dem Handschutz |

Visier: F1 „Bögen“ (Baukasten v3, visier-konzept › 6a; `common.boegen`): versetzte Bögen mit S-Öffnung und Stegen, Ladebalken auf
dem Gehäuse; Absehen gezeichnet (Hüftform `corners` flach im Glas). Größe M mit Glas Ø 26 (18,9 %, Standard 12–20 %). F2 Doppelring
nur als Variante im Katalog.
Schlichtheitsbudget: Leuchten 3 Funktionen (Ladung: Glutkern und Ladebalken im Visier · Munition: Ladefenster der Zelle · Visier:
Absehen) · Grafik 1 Band · Schrift 1 · Orange 2 (Zellenhalter, Klemmhebel des Visiers) · Schrauben nur an Paneelen und Schaft.
Proportion: Länge 0,70 m (v1 0,80 m; Destiny-Fusion kompakt, H/L 0,49 mit offener Zelle).
Bewegung (Daten): Abzug, Glutkern und Ladebalken leuchten beim Aufladen auf (`charge_fire`, `charge_cancel`), Zelle senkrecht nach
unten heraus (`reload`), Zellenhalter. Energiewaffe: **kein Hülsenauswurf** (`EJECT = None`, Daten statt Sonderlogik).
Status: Maße entworfen (Länge kürzer als v1, an Destiny H/L angelehnt; gemessene Werte im Spec), Formprinzipien abgeleitet.
"""
from basic.common import (part, prof, box, cyl, cut_box, screws, mirror, rail, grip_v21, stock_s2, R_BODY, R_MID, R_SMALL, R_FINE)
from basic.common import boegen
from basic.pilot.energy_roles import CHARGE_ROLES  # noqa: F401  (registriert die Rolle charge_core in Blender)
from basic.weapons import w10_fusion_rifle as V1

META = dict(V1.META, variant='v2.1', name='Glutkern v2.1', nick='Familie v2.1',
            summary='Fusionsgewehr mit offener Ladekammer (Spulenringe um den Glutkern), Schlitz-Emitter und Visier F1 (Stil v2.1).')
ASSEMBLIES = V1.ASSEMBLIES
GRIP_TOP = 40
BORE = 96
TOP = 128                    # Oberkante Gehäuse und Kammerhaube; Schiene bis u 136, Visierlinie u 162 (Visierhöhe 66)
CH0, CH1 = 151, 382          # Ladekammer: Fuge zum Gehäuse, Emitterblock
HOOD_U = 112                 # Unterkante der Kammerhaube
HG_U = 80                    # Oberkante des Handschutzes (Kammerfenster u 80–112)
EM1 = 420                    # Stirn des Emitters (Socket_Muzzle)
CELL = (86, 126)             # Energiezelle vor dem Griff (f; 3 mm vor dem Abzugsbügel, Posenprüfung)

P = []
# ---------------------------------------------------------------- Gehäuse
P += [
    prof('upper', 'Gehäuse', 'Upper receiver', 'receiver', 'shell', 'Tragkörper für Kammer, Zellenschacht und Schiene',
         'mit dem Unteren Gehäuse über zwei Querbolzen (fest)', [(-110, 82), (150, 82), (150, TOP), (-100, TOP), (-110, TOP - 8)], 44,
         cuts=[cut_box(-92, -10, 92, 116, 3.0, x=22.6), cut_box(-92, -10, 92, 116, 3.0, x=-22.6)]),       # Paneel-Mulden
    prof('lower', 'Unteres Gehäuse', 'Lower receiver', 'receiver', 'graphite', 'Griffmodul, Abzugsgruppe, Zellenschacht',
         'unter dem Gehäuse, Fuge 1 mm; Zellentrichter angeformt',
         [(-110, 62), (-62, 40), (CELL[0] - 14, 40), (CELL[0] - 8, 28), (CELL[0] - 4, 20), (CELL[1] + 4, 20), (CELL[1] + 10, 30),
          (150, 64), (150, 81), (-110, 81)], 42),
    prof('cell_lip', 'Schachtlippe', 'Cell well lip', 'receiver', 'trim', 'Blanke Einführkante des Zellenschachts',
         'unten am Trichter des Unteren Gehäuses', [(CELL[0] - 5, 17.5), (CELL[1] + 5, 17.5), (CELL[1] + 6, 21), (CELL[0] - 6, 21)], 43,
         bevel=0.6, iface='BEC-1'),
    box('side_panel_l', 'Seitenpaneel links', 'Side panel left', 'receiver', 'anodized', 'Wartungsdeckel über der Steuerung',
        'in die Mulde geschraubt (4 Schrauben)', -90, -12, 94, 114, 1.2, bevel=R_FINE, x=21.2),
    box('side_panel_r', 'Seitenpaneel rechts', 'Side panel right', 'receiver', 'anodized', 'Wartungsdeckel über der Steuerung',
        'in die Mulde geschraubt (4 Schrauben)', -90, -12, 94, 114, 1.2, bevel=R_FINE, x=-21.2),
    part('panel_screws', 'Paneelschrauben', 'Panel screws', 'receiver', 'multi', 'trim', 'Halten die Seitenpaneele',
         'in den Paneelen', bevel=0.2, items=mirror(screws([(-86, 98), (-86, 110), (-16, 98), (-16, 110)], 21.8, r=1.6, h=0.8))),
    part('takedown_pins', 'Querbolzen', 'Takedown pins', 'receiver', 'multi', 'metal', 'Verbinden Gehäuse und Unteres Gehäuse',
         'quer durch das Gehäuse (lösbar)', bevel=0.4, items=mirror(screws([(-96, 74), (138, 74)], 21.0, r=3.6, h=1.0))),
    part('cell_release', 'Zellenhalter', 'Cell release', 'grip_controls', 'cyl', 'accent', 'Löst die Energiezelle',
         'Druckknopf links', bevel=R_FINE, axis='x', c=(CELL[0] - 10, 54), a0=19, a1=23.5, r=5, segs=20,
         move=dict(kind='translate', pivot=(CELL[0] - 10, 54, 21), vector_mm=(0, 0, -2.5), event='reload',
                   expect=((CELL[0] - 10, 54, 23.5), (0, 0, -1)))),
]
P += [dict(p, mat='anodized') for p in rail(-60, 70, TOP)]
P[-1]['cuts'] = [cut_box(-52 + 14 * i, -45 + 14 * i, TOP + 4, TOP + 9, 30) for i in range(9)]
# Visier F1 „Bögen“ (Baukasten v3, Standard Fusion nach visier-konzept › 6a): Glas Ø 26, Ladebalken auf dem Gehäuse
_sight, SIGHT_ANCHORS = boegen(-12, TOP + 8, weapon_type=V1.META['type'])
P += _sight
# ---------------------------------------------------------------- Ladekammer (Leitmerkmal): Haube, Handschutz, Spulen, Glutkern
COILS = (171, 241, 311)          # Spulen 50 mm, 20 mm Lücken: der Glutkern zeigt sich nur dazwischen
P += [
    prof('chamber_hood', 'Kammerhaube', 'Chamber hood', 'barrel', 'shell', 'Oberschale über der offenen Ladekammer; gerade Oberkante',
         'am Gehäuse verschraubt, Fuge 1 mm; vorn im Emitterblock', [(CH0, HOOD_U), (CH1 + 2, HOOD_U), (CH1 + 2, TOP), (CH0, TOP)], 44,
         bevel=R_BODY),
    prof('handguard', 'Handschutz', 'Handguard', 'support', 'graphite', 'Unterschale der Ladekammer; Griffbereich der Stützhand',
         'am Unteren Gehäuse, Fuge 1 mm; vorn im Emitterblock', [(CH0, 60), (CH1 - 30, 60), (CH1 + 2, 70), (CH1 + 2, HG_U), (CH0, HG_U)],
         42, bevel=R_BODY),
    prof('handguard_grip', 'Griffpolster', 'Grip pad', 'support', 'rubber', 'Rutschfeste Zone für die Stützhand',
         'unten auf den Handschutz geklebt', [(200, 56.5), (330, 56.5), (330, 62), (200, 62)], 36, bevel=R_SMALL),
    part('hood_screws', 'Haubenschrauben', 'Hood screws', 'barrel', 'multi', 'trim', 'Halten Haube und Handschutz am Gehäuse',
         'seitlich am Kammeranfang', bevel=0.2, items=mirror(screws([(162, 120), (162, 70)], 22.4, r=1.8, h=0.8))),
    cyl('ember_core', 'Glutkern', 'Ember core', 'barrel', 'charge_core', 'Ladekern: leuchtet beim Aufladen auf (Blickfang)',
        'zwischen Gehäuse und Emitter gespannt', 'f', (BORE, 0), CH0 - 2, CH1 + 10, 4.0, bevel=0, segs=24,
        move=dict(kind='glow', pivot=None, event='charge', max=6.0)),
    part('coils', 'Spulenringe', 'Coil rings', 'cooling', 'multi', 'dark_metal', 'Kondensatorspulen um den Glutkern; im Fenster sichtbar',
         'auf den Kern gepresst', bevel=0.8, smooth=True,
         items=[dict(shape='cyl', axis='f', c=(BORE, 0), a0=f, a1=f + 50, r=14.5, r_in=4.1, segs=40) for f in COILS]),
    part('coil_rims', 'Spulenkanten', 'Coil rims', 'cooling', 'multi', 'trim', 'Blanke Stirnringe der Spulen', 'an den Spulen',
         bevel=0.3, smooth=True,
         items=[dict(shape='cyl', axis='f', c=(BORE, 0), a0=f + d, a1=f + d + 1.6, r=15.1, r_in=11.5, segs=40)
                for f in COILS for d in (-0.6, 49)]),
    part('band_side', 'Schrägband', 'Slanted band', 'barrel', 'multi', 'accent', 'Lackiertes Band (einziges Grafikelement)',
         'lackiert', bevel=0, items=[dict(shape='prof', pts=[(334, HOOD_U + 0.5), (348, HOOD_U + 0.5), (356, TOP - 0.5), (342, TOP - 0.5)],
                                           w=0.3, x=sx * 22.15) for sx in (1, -1)]),
    part('text_l', 'Schriftzug', 'Lettering', 'support', 'text', 'decal', 'Kennung „BASIC FR-10“ (einzige Schrift)',
         'aufgedruckt', bevel=0, text='BASIC  FR-10', size=5.0, f=236, u=66, x=21.05, side=1, depth=0.12),
    # Schlitz-Emitter (Leitmerkmal): Block, schmalere Stirn, blanke Schlitzkrone
    prof('emitter', 'Schlitz-Emitter', 'Slit emitter', 'barrel', 'dark_metal', 'Formt die Salve; hinten Block, vorn schmalere Stirn',
         'auf Haube und Handschutz geschraubt (Fuge 1 mm)',
         [(CH1 + 3, 60), (CH1 + 26, 60), (CH1 + 26, 72), (EM1, 76), (EM1, 120), (CH1 + 26, 124), (CH1 + 26, TOP + 1), (CH1 + 3, TOP + 1)],
         46, bevel=R_MID, cuts=[cut_box(CH1 + 30, EM1 + 2, BORE - 5, BORE + 5, 36)]),
    part('emitter_crown', 'Schlitzkrone', 'Slit crown', 'barrel', 'frame', 'trim', 'Blanke Kante um den Schlitz', 'vorn im Emitter',
         bevel=0.3, f0=EM1 - 1.5, f1=EM1 + 0.6, cu=BORE, ow=40, oh=14, iw=36, ih=10, r_out=3, r_in=1.5),
]
# ---------------------------------------------------------------- Griff, Zelle, Schaft S2 (Daumenloch)
P += grip_v21(top=GRIP_TOP)
_cc = ((CELL[0] + CELL[1]) / 2, 10)
P += [
    part('energy_cell', 'Energiezelle', 'Energy cell', 'ammo', 'prof', 'dark_metal', 'Speichert die Ladungen; austauschbar',
         'rastet im Zellenschacht ein (lösbar)', bevel=R_MID, iface='BEC-1', w=24,
         pts=[(CELL[0], 60), (CELL[1], 60), (CELL[1], -26), (CELL[1] - 4, -32), (CELL[0] + 4, -32), (CELL[0], -26)],
         move=dict(kind='translate', pivot=(_cc[0], _cc[1], 0), vector_mm=(0, -110, 0), event='reload', removable=True,
                   expect=((_cc[0], -32, 0), (0, -1, 0)))),
    box('cell_band', 'Zellenband', 'Cell band', 'ammo', 'trim', 'Blankes Band über dem Zellenboden; Greifkante',
        'um die Zelle', CELL[0] - 0.6, CELL[1] + 0.6, -24, -20, 25.2, bevel=0.4, parent_part='energy_cell'),
    box('cell_window', 'Ladefenster', 'Charge window', 'ammo', 'energy', 'Zeigt den Ladezustand der Zelle',
        'links in die Zelle eingelassen', CELL[1] - 12, CELL[1] - 7, -14, 8, 1.0, bevel=0.3, x=12.2, parent_part='energy_cell'),
]
_f0, _ua, _s = -110, BORE, 1.0


def _L(d):
    return _f0 - d * _s


for p in stock_s2(_f0, _ua, s=_s):
    if p['id'] == 'stock':
        p['cuts'] = [dict(shape='prof', pts=[(_L(38), _ua - 20), (_L(38), _ua + 8), (_L(116), _ua + 12), (_L(130), _ua - 2),
                                             (_L(126), _ua - 48), (_L(76), _ua - 32)], w=50)]
        p['func'] = 'Einteilige Schulterstütze mit Daumenloch'
    if p['id'] == 'butt_pad':
        p['mat'] = 'rubber'
    P.append(p)
P += [part('stock_bolts', 'Schaftbolzen', 'Stock bolts', 'stock', 'multi', 'trim', 'Halten den Schaft am Gehäuse',
           'quer durch den Schaftansatz', bevel=0.3, items=mirror(screws([(_f0 - 12, _ua + 14), (_f0 - 12, _ua - 26)], 17.4, r=2.6, h=1.0)))]
PARTS = P
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip', note='Haupthand, auf der Griffachse'),
    'Socket_SupportHand': dict(at=(265, 56.5, 0), part='handguard', note='Griffpolster unter der Ladekammer'),
    'Socket_Muzzle': dict(at=(EM1, BORE, 0), part='emitter', note='Stirn des Schlitz-Emitters auf der Kernachse'),
    'Socket_Cell': dict(at=(_cc[0], 20, 0), part='energy_cell', note='Einrastpunkt der Energiezelle (Schnittstelle BEC-1)'),
}
ANCHORS.update(SIGHT_ANCHORS)
_charge = [(0, 0), (4, 0.2), (14, 0.5), (24, 1.0), (27, 1.0), (36, 0)]
ACTIONS = {
    'charge_fire': dict(de='Aufladen und Salve', frames=40, step=1, keys={
        'trigger': [(0, 0), (2, 1), (30, 1), (33, 0)], 'ember_core': _charge, 'sight_emitter': _charge},
        events=[(2, 'charge_start'), (24, 'charged'), (27, 'burst'), (40, 'ready')], view=(0.8, -0.3, 0.45)),
    'charge_cancel': dict(de='Aufladen abbrechen', frames=24, step=1, keys={
        'trigger': [(0, 0), (2, 1), (12, 1), (14, 0)], 'ember_core': [(0, 0), (12, 0.45), (20, 0)],
        'sight_emitter': [(0, 0), (12, 0.45), (20, 0)]}, events=[(12, 'cancel')], view=(0.8, -0.3, 0.45)),
    'reload': dict(de='Energiezelle wechseln', frames=70, keys={'cell_release': [(0, 0), (6, 1), (14, 1), (18, 0)],
                                                                'energy_cell': [(0, 0), (16, 1), (34, 1), (50, 0)]},
                   events=[(16, 'cell_out'), (50, 'cell_in'), (58, 'ready')], view=(0.8, -0.3, 0.45)),
}
EXPLODE = {'sight': (0, 110, 0), 'ammo': (0, -140, 0), 'stock': (-110, 0, 0), 'barrel': (140, 0, 0), 'cooling': (0, 0, 80),
           'support': (60, -60, 0), 'grip_controls': (-10, -80, 0), 'receiver': (0, 0, 0)}
SIGHT_ID = 'F1'    # Visier des Baukastens v3 (visier-konzept › 6a); test_sights prüft dessen Pflichtteile und Merkmale
EJECT = None    # Energiewaffe: keine Hülse (Daten statt Sonderlogik; check: Energiezelle BEC-1 → EJECT None)
