"""BASIC-11 v2.1 – Lineares Fusionsgewehr im Stil v2.1 („Destiny-Detaildichte + AAA-Material, schlicht“), Familie des Piloten BASIC-01 v2.1.

Recherche (docs/quellen.md › Q-D2-IMG, gesichtet 28.10.2026, Bungie-Manifest): Komodo-4FR und Taipan-4fr (lange obere Laufhaube über
einer schlanken unteren Schiene, vorn offen, Zellenblock hinter dem Griff), Threaded Needle (lange offene Gabel nach vorn, gerippte
Spulenhülse; vermessen in Motiongen proportionen › 2), Cataclysmic (zwei parallele Platten, dazwischen sichtbare Spulen). Nur
Prinzipien; Leitmerkmal 11 nach Designvertrag: offene Doppelschiene mit Leuchtkern.

Formsprache-Checkliste (stilhandbuch §3):
| Frage | Lineares Fusionsgewehr v2.1 |
|---|---|
| Leitmerkmal der Silhouette | offene Doppelschiene: Creme-Schiene oben in Linie mit dem Gehäuse, Graphit-Schiene unten; dazwischen über die ganze Länge offen der Leuchtkern mit vier Spulen; vorn stehen beide Schienen als Gabel über die Mündungsbrücke hinaus |
| Schichten | Unteres Gehäuse, untere Schiene, Schaftrohr (Graphit) → Gehäuse und obere Schiene (Creme, Fuge 1 mm) → Seitenpaneele (eloxiert) → Schienen BRI-22 → Zielfernrohr Z2 |
| Negativraum | Spalt zwischen den Schienen vom Gehäuse bis zur Brücke (Kern und Spulen sichtbar); offene Gabel vor der Mündung; Durchbruch im Schaft S1 |
| Blickfang | Linearkern: leuchtende Linie zwischen den Schienen, die Spulen gliedern sie |
| Zweiton-Blockung | Gehäuse, obere Schiene, Schulterstütze Lack (`shell`), Unteres Gehäuse, untere Schiene, Schaftrohr Polymer (`graphite`), Brücke und Spulen `dark_metal` |
| Grafik | ein Schrägband vorn an der oberen Schiene, ein Schriftzug „BASIC LF-11“ (hell auf Graphit) |
| Front | Mündungsbrücke mit Fokusmündung und blanker Krone; Gabelspitzen oben/unten schräg zur Mitte |
| Übergänge | untere Schiene hinten als Handschutz tiefer, vorn schlank (Schräge); Zellentrichter im Unteren Gehäuse hinter dem Griff angeformt; Buckel hinter dem Auge im Gehäuseprofil |
| Ergonomie | Griff BGM-1 in v2.1-Form (Familie), Stützhand unter der tiefen Schienenzone mit Polster, Zelle hinter dem Griff, hohe Wangenauflage |

Visier: Z2 „Gabel“ (Baukasten v3, visier-konzept › 6a; `common.gabel`), Sitz nach Konzept A wie Z1/Z3: Rohrsattel auf dem Buckel
hinter dem Augenpunkt, H0-Klemmfuß unter dem Objektiv; Ring ohne Wulst (außen/innen 1,29), U-Gabel mit 3 mm Abstand und Laschen;
gezeichnetes Absehen (Hüftform `cross`) flach auf der Linse. Größe M (21,3 % bei 85,5 mm Linsenabstand, Standard 20–26 %). Z1 Tropfen nur als Variante.
Schlichtheitsbudget: Leuchten 3 Funktionen (Ladung: Linearkern · Munition: Ladefenster der Zelle · Visier: Absehen) · Grafik 1 Band ·
Schrift 1 · Orange 3 (Höhenturm, Klemmhebel des Visiers, Zellenhalter) · Schrauben nur an Paneelen, Brücke und Schaft.
Bewegung (Daten): Abzug, Linearkern leuchtet beim Aufladen auf (`charge_fire`), Zelle senkrecht nach unten heraus (`reload`),
Zellenhalter. Energiewaffe: **kein Hülsenauswurf** (`EJECT = None`, Daten statt Sonderlogik).
Status: Maße entworfen (Länge an v1 1,22 m und Familie 09 angelehnt; gemessene Werte im Spec), Formprinzipien abgeleitet.
"""
from basic.common import part, prof, box, cyl, cut_box, screws, mirror, rail, grip_v21, stock_s1, R_BODY, R_MID, R_SMALL, R_FINE
from basic.common import gabel
from basic.pilot.energy_roles import CHARGE_ROLES  # noqa: F401  (registriert die Rolle charge_core in Blender)
from basic.weapons import w11_linear_fusion_rifle as V1

META = dict(V1.META, variant='v2.1', name='Schienenlicht v2.1', nick='Familie v2.1',
            summary='Lineares Fusionsgewehr mit offener Doppelschiene, Leuchtkern, Gabelfront und Zielfernrohr Z2 (Stil v2.1).')
ASSEMBLIES = V1.ASSEMBLIES
GRIP_TOP = 40
BORE = 92                    # Kernachse: Mitte zwischen den Schienen (u 80–104)
TOP = 122                    # Oberkante Gehäuse und obere Schiene
R0 = 201                     # Fuge Gehäuse / Schienen
UR = (104, TOP)              # obere Schiene u
LR = (62, 80)                # untere Schiene u (schlanker Teil vorn)
BR = (680, 700)              # Mündungsbrücke f
TIP = 770                    # Gabelspitze oben
CELL = (-112, -58)           # Energiezelle hinter dem Griff (f)
# Visiersitz nach Konzept A (wie BASIC-03/09 v2.1): Visierlinie u 160 (Visierhöhe 66), Ringstirn f 150, Augenpunkt f 60; Buckel mit
# kurzer Schiene hinter dem Auge (Rohrsattel), vorn eine zweite kurze Schiene unter dem Klemmfuß des Objektivs.
_cu = BORE + 66
F_OBJ = 150
SCOPE_L = 190
SEAT = 146                   # Schienenoberkante hinten: unter der Okular-Unterkante (u 147)
HUMP = SEAT - 8
SEAT_F = (-20, 62)           # Schiene auf dem Buckel (Sattel f −14 … 56, endet vor dem Augenpunkt f 60)
FOOT_F = (116, 154)          # vordere Schiene unter dem Klemmfuß (f 120–150)
_scope, SIGHT_ANCHORS = gabel(F_OBJ, TOP + 8, _cu, weapon_type=V1.META['type'], seat_u=SEAT, length=SCOPE_L, saddle_f=(-14, 56))

P = []
# ---------------------------------------------------------------- Gehäuse mit Buckel hinter dem Auge
P += [
    prof('receiver', 'Gehäuse', 'Receiver', 'receiver', 'shell', 'Tragkörper: Schienen, Steuerung, Buckel für das Zielfernrohr',
         'mit dem Unteren Gehäuse über zwei Querbolzen (fest); Buckel hinter dem Augenpunkt angeformt',
         [(-122, 76), (200, 76), (200, TOP), (88, TOP), (66, HUMP), (-24, HUMP), (-44, TOP), (-112, TOP), (-122, TOP - 8)], 40,
         cuts=[cut_box(-96, -20, 84, 112, 3.0, x=20.6), cut_box(-96, -20, 84, 112, 3.0, x=-20.6)]),      # Paneel-Mulden
    prof('lower', 'Unteres Gehäuse', 'Lower receiver', 'receiver', 'graphite', 'Griffmodul, Abzugsgruppe, Zellenschacht hinter dem Griff',
         'unter dem Gehäuse, Fuge 1 mm; Zellentrichter angeformt',
         [(-122, 75), (-122, 32), (CELL[0] - 4, 24), (CELL[1] + 4, 24), (CELL[1] + 16, 40), (110, 40), (200, 60), (200, 75)], 38),
    prof('cell_lip', 'Schachtlippe', 'Cell well lip', 'receiver', 'trim', 'Blanke Einführkante des Zellenschachts',
         'unten am Trichter des Unteren Gehäuses', [(CELL[0] - 5, 21.5), (CELL[1] + 5, 21.5), (CELL[1] + 6, 25), (CELL[0] - 6, 25)], 39,
         bevel=0.6, iface='BEC-1'),
    box('side_panel_l', 'Seitenpaneel links', 'Side panel left', 'receiver', 'anodized', 'Wartungsdeckel über der Steuerung',
        'in die Mulde geschraubt (4 Schrauben)', -94, -22, 86, 110, 1.2, bevel=R_FINE, x=19.2),
    box('side_panel_r', 'Seitenpaneel rechts', 'Side panel right', 'receiver', 'anodized', 'Wartungsdeckel über der Steuerung',
        'in die Mulde geschraubt (4 Schrauben)', -94, -22, 86, 110, 1.2, bevel=R_FINE, x=-19.2),
    part('panel_screws', 'Paneelschrauben', 'Panel screws', 'receiver', 'multi', 'trim', 'Halten die Seitenpaneele',
         'in den Paneelen', bevel=0.2, items=mirror(screws([(-90, 90), (-90, 106), (-26, 90), (-26, 106)], 19.8, r=1.5, h=0.8))),
    part('takedown_pins', 'Querbolzen', 'Takedown pins', 'receiver', 'multi', 'metal', 'Verbinden Gehäuse und Unteres Gehäuse',
         'quer durch das Gehäuse (lösbar)', bevel=0.4, items=mirror(screws([(-104, 68), (186, 68)], 19.0, r=3.4, h=1.0))),
    part('cell_release', 'Zellenhalter', 'Cell release', 'grip_controls', 'cyl', 'accent', 'Löst die Energiezelle',
         'Druckknopf links', bevel=R_FINE, axis='x', c=(CELL[1] + 12, 54), a0=17, a1=21.5, r=5, segs=20,
         move=dict(kind='translate', pivot=(CELL[1] + 12, 54, 19), vector_mm=(0, 0, -2.5), event='reload',
                   expect=((CELL[1] + 12, 54, 21.5), (0, 0, -1)))),
]
P += [dict(p, mat='anodized', attach='auf dem Gehäusebuckel hinter dem Augenpunkt (fest)') for p in rail(*SEAT_F, HUMP)] \
    + [dict(p, id='rail_front', de='Schiene vorn', en='Front rail', mat='anodized', attach='auf dem Gehäuse unter dem Objektiv (fest)')
       for p in rail(*FOOT_F, TOP)]
P += _scope
# ---------------------------------------------------------------- Doppelschiene (Leitmerkmal), Kern, Spulen, Brücke
COILS = (270, 370, 470, 570)
P += [
    prof('rail_top', 'Beschleunigerschiene oben', 'Upper accelerator rail', 'barrel', 'shell',
         'Führt das Feld oben; gerade Oberkante in Linie mit dem Gehäuse, vorn Gabelspitze',
         'am Gehäuse verschraubt, Fuge 1 mm; vorn auf der Mündungsbrücke',
         [(R0, UR[0]), (TIP - 30, UR[0]), (TIP, UR[0] + 5), (TIP, UR[1] - 5), (TIP - 14, UR[1]), (R0, UR[1])], 30, bevel=R_MID),
    prof('rail_bottom', 'Beschleunigerschiene unten', 'Lower accelerator rail', 'support', 'graphite',
         'Führt das Feld unten; hinten tiefer als Handschutz der Stützhand, vorn schlank mit Gabelspitze',
         'am Unteren Gehäuse, Fuge 1 mm; vorn auf der Mündungsbrücke',
         [(R0, 46), (460, 46), (510, LR[0]), (TIP - 50, LR[0]), (TIP - 10, LR[0] + 6), (TIP - 10, LR[1] - 3), (TIP - 26, LR[1]), (R0, LR[1])], 30,
         bevel=R_MID),
    prof('rail_grip', 'Griffpolster', 'Grip pad', 'support', 'rubber', 'Rutschfeste Zone für die Stützhand',
         'unten auf die untere Schiene geklebt', [(270, 42.5), (430, 42.5), (430, 48), (270, 48)], 24, bevel=R_SMALL),
    cyl('linear_core', 'Linearkern', 'Linear core', 'barrel', 'charge_core', 'Leuchtender Kern zwischen den Schienen; lädt sich sichtbar auf',
        'zwischen Gehäuse und Mündungsbrücke gespannt', 'f', (BORE, 0), R0 - 2, BR[0] + 4, 2.6, bevel=0, segs=16,
        move=dict(kind='glow', pivot=None, event='charge', max=6.0)),
    part('coils', 'Spulen', 'Accelerator coils', 'cooling', 'multi', 'dark_metal', 'Beschleunigerspulen um den Kern; zwischen den Schienen sichtbar',
         'auf den Kern gepresst', bevel=0.6, smooth=True,
         items=[dict(shape='cyl', axis='f', c=(BORE, 0), a0=f, a1=f + 40, r=11.0, r_in=2.7, segs=36) for f in COILS]),
    part('coil_rims', 'Spulenkanten', 'Coil rims', 'cooling', 'multi', 'trim', 'Blanke Stirnringe der Spulen', 'vorn an den Spulen',
         bevel=0.3, smooth=True,
         items=[dict(shape='cyl', axis='f', c=(BORE, 0), a0=f + 39, a1=f + 40.6, r=11.5, r_in=8.5, segs=36) for f in COILS]),
    prof('muzzle_bridge', 'Mündungsbrücke', 'Muzzle bridge', 'barrel', 'dark_metal', 'Verbindet die Schienen und trägt die Mündung',
         'zwischen den Schienen verschraubt', [(BR[0], LR[0] + 2), (BR[1], LR[0] + 2), (BR[1], UR[1] - 2), (BR[0], UR[1] - 2)], 24,
         bevel=R_SMALL),
    part('bridge_screws', 'Brückenschrauben', 'Bridge screws', 'barrel', 'multi', 'trim', 'Halten die Schienen an der Brücke',
         'seitlich in der Brücke', bevel=0.2, items=mirror(screws([(BR[0] + 10, UR[0] + 7), (BR[0] + 10, LR[1] - 7)], 15.4, r=1.6, h=0.8))),
    cyl('muzzle', 'Fokusmündung', 'Focus muzzle', 'barrel', 'dark_metal', 'Bündelt den Strahl', 'vorn in der Brücke (lösbar)',
        'f', (BORE, 0), BR[0] - 6, BR[1] + 26, 10, r_in=3.0, segs=24, bevel=R_SMALL, iface='BMZ-15'),
    cyl('muzzle_crown', 'Mündungskrone', 'Muzzle crown', 'barrel', 'trim', 'Blanke Stirnkante', 'vorn an der Mündung',
        'f', (BORE, 0), BR[1] + 25, BR[1] + 29, 9, r_in=3.5, segs=24, bevel=0.6),
    part('band_side', 'Schrägband', 'Slanted band', 'barrel', 'multi', 'accent', 'Lackiertes Band (einziges Grafikelement)',
         'lackiert', bevel=0, items=[dict(shape='prof', pts=[(630, UR[0] + 0.5), (642, UR[0] + 0.5), (648, UR[1] - 0.5), (636, UR[1] - 0.5)],
                                           w=0.3, x=sx * 15.15) for sx in (1, -1)]),
    part('text_l', 'Schriftzug', 'Lettering', 'support', 'text', 'decal', 'Kennung „BASIC LF-11“ (einzige Schrift)',
         'aufgedruckt', bevel=0, text='BASIC  LF-11', size=5.0, f=290, u=56, x=15.05, side=1, depth=0.12),
]
# ---------------------------------------------------------------- Griff, Zelle, Schaft S1 mit hoher Wange und Durchbruch
P += grip_v21(top=GRIP_TOP)
_cc = ((CELL[0] + CELL[1]) / 2, 0)
P += [
    part('energy_cell', 'Energiezelle', 'Energy cell', 'ammo', 'prof', 'dark_metal', 'Speichert die Ladungen; austauschbar',
         'rastet im Zellenschacht hinter dem Griff ein (lösbar)', bevel=R_MID, iface='BEC-1', w=24,
         pts=[(CELL[0], 60), (CELL[1], 60), (CELL[1], -20), (CELL[1] - 4, -26), (CELL[0] + 4, -26), (CELL[0], -20)],
         move=dict(kind='translate', pivot=(_cc[0], _cc[1], 0), vector_mm=(0, -110, 0), event='reload', removable=True,
                   expect=((_cc[0], -26, 0), (0, -1, 0)))),
    box('cell_band', 'Zellenband', 'Cell band', 'ammo', 'trim', 'Blankes Band über dem Zellenboden; Greifkante',
        'um die Zelle', CELL[0] - 0.6, CELL[1] + 0.6, -18, -14, 25.2, bevel=0.4, parent_part='energy_cell'),
    box('cell_window', 'Ladefenster', 'Charge window', 'ammo', 'energy', 'Zeigt den Ladezustand der Zelle',
        'links in die Zelle eingelassen', CELL[1] - 12, CELL[1] - 7, -8, 12, 1.0, bevel=0.3, x=12.2, parent_part='energy_cell'),
]
_f0, _s, _ua = -122, 1.15, BORE


def _L(d):
    return _f0 - d * _s


for p in stock_s1(_f0, _ua, s=_s):
    if p['id'] == 'stock':
        p['cuts'] = [dict(shape='prof', pts=[(_L(100), _ua + 8), (_L(148), _ua + 10), (_L(150), _ua - 58), (_L(110), _ua - 26)], w=50)]
        p['func'] = 'Anlage an der Schulter; Durchbruch'
    if p['id'] == 'cheek_rest':     # hohe Wange für das Zielfernrohr (Visierlinie 66 mm über dem Kern)
        p.update(mat='rubber', u1=_ua + 40, func='Hohe Anlage für die Wange (Zielfernrohr)', bevel=R_SMALL)
    P.append(p)
PARTS = P
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip', note='Haupthand, auf der Griffachse'),
    'Socket_SupportHand': dict(at=(350, 42.5, 0), part='rail_bottom', note='Griffpolster unter der tiefen Zone der unteren Schiene'),
    'Socket_Muzzle': dict(at=(BR[1] + 29, BORE, 0), part='muzzle_crown', note='Stirn der Mündungskrone auf der Kernachse'),
    'Socket_Cell': dict(at=(_cc[0], 24, 0), part='energy_cell', note='Einrastpunkt der Energiezelle (Schnittstelle BEC-1)'),
}
ANCHORS.update(SIGHT_ANCHORS)
ACTIONS = {
    'charge_fire': dict(de='Aufladen und Einzelstrahl', frames=36, step=1, keys={
        'trigger': [(0, 0), (2, 1), (18, 1), (21, 0)], 'linear_core': [(0, 0), (6, 0.25), (16, 0.8), (18, 1), (24, 0)]},
        events=[(2, 'charge_start'), (16, 'charged'), (18, 'beam'), (34, 'ready')], view=(0.8, -0.3, 0.45)),
    'reload': dict(de='Energiezelle wechseln', frames=80, keys={'cell_release': [(0, 0), (6, 1), (14, 1), (18, 0)],
                                                                'energy_cell': [(0, 0), (18, 1), (38, 1), (56, 0)]},
                   events=[(18, 'cell_out'), (56, 'cell_in'), (64, 'ready')], view=(0.8, -0.3, 0.45)),
}
EXPLODE = {'sight': (0, 130, 0), 'ammo': (0, -140, 0), 'stock': (-120, 0, 0), 'barrel': (200, 0, 0), 'cooling': (0, 0, 80),
           'support': (60, -60, 0), 'grip_controls': (-10, -80, 0), 'receiver': (0, 0, 0)}
SIGHT_ID = 'Z2'    # Visier des Baukastens v3 (visier-konzept › 6a); test_sights prüft dessen Pflichtteile und Merkmale
EJECT = None    # Energiewaffe: keine Hülse (Daten statt Sonderlogik; check: Energiezelle BEC-1 → EJECT None)
# Ego-Griffe (0.33 „Armory“ P3, basic/arms/ego.profile): Autorenmaß dieser Waffe wie ego.GRIPS der Pilotwaffe; 'mag' an der Energiezelle
# hinter dem Griff, 'charge' am Zellenhalter (kein Ladehebel; leer wie taktisch)
EGO_GRIPS = {
    'grip':    dict(contact=(-3, -6, -16.5), palm=(0.15, 0.0, 1.0), fingers=(1.0, -0.06, 0.0), fingers_pose='trigger',
                    src='E wie die Pilotwaffe (Griff BGM-1 v2.1, gleiche Lage zu Socket_Hand)'),
    'support': dict(contact=(350, 41.0, -2), palm=(0.0, 1.0, -0.25), fingers=(0.08, 0.15, -1.0), fingers_pose='underhand',
                    src='E unter der unteren Schiene auf dem Griffpolster (rail_grip f 270–430, Unterkante u 42,5, Socket_SupportHand), Lage wie '
                        'die Pilotwaffe'),
    'mag':     dict(part='energy_cell', contact=(-95, -5, 12.5), palm=(0.0, 0.0, -1.0), fingers=(1.0, 0.2, 0.0), fingers_pose='mag_hold',
                    src='E links an der Energiezelle (Breite 24, f −112 … −58), Hand greift von unten hinten (wie die Pilotwaffe)'),
    'charge':  dict(part='cell_release', contact=(CELL[1] + 12, 54, 21.5), palm=(0.0, 0.0, -1.0), fingers=(0.45, 0.9, 0.0),
                    fingers_pose='pinch', src='E am Zellenhalter links (kein Ladehebel; vom Nachladen nicht genutzt, leer wie taktisch)'),
}
# Abzug je Ladung; der Linearkern leuchtet mit der Ladung (Feuerart charge_single, Bewegung glow 0 → 1)
EGO_LIVE = dict(trigger='trigger', bolt='', port='', glow=('linear_core',))
