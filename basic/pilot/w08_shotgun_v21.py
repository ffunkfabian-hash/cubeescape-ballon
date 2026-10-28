"""BASIC-08 v2.1 – Schrotflinte im Stil v2.1 („Destiny-Detaildichte + AAA-Material, schlicht“), Familie des Piloten BASIC-01 v2.1.

Recherche (docs/quellen.md › Q-D2-IMG, gesichtet 28.10.2026, Bungie-Manifest): Matador 64 (lange gerade Linie, dicker Lauf über dem
Röhrenmagazin, langer glatter Vorderschaft), Ragnhild-D (Lüftungsschiene über die ganze Länge, kastiges helles Gehäuse, gerippte
Pumpe unter dem Lauf), Quitclaim Shotgun III (Lauf und Röhre vorn frei übereinander). Nur Prinzipien; Leitmerkmal 08 nach
Designvertrag: dicker Lauf über Röhrenmagazin, Pumpe.

Formsprache-Checkliste (stilhandbuch §3):
| Frage | Schrotflinte v2.1 |
|---|---|
| Leitmerkmal der Silhouette | eine gerade Oberkante von der Kimme bis zur Mündung (Schiene, dann Lüftungsschiene auf dem Lauf); darunter dicker Lauf über dem Röhrenmagazin mit großer Graphit-Pumpe |
| Schichten | Unteres Gehäuse (Graphit, 2 mm schmaler, Fuge 1 mm) → Oberes Gehäuse (Creme) → Schiene und Lüftungsschiene (eloxiert) |
| Negativraum | Fenster der Lüftungsschiene quer durch (Lauf darunter sichtbar); offener Spalt zwischen Lauf und Röhre vor und hinter der Pumpe; Auswurffenster rechts mit Verschluss; Durchbruch im Schaft |
| Blickfang | Munitionsanzeige links am Ladeschacht (Ego-Seite, einzige Leuchtfunktion) |
| Zweiton-Blockung | Oberes Gehäuse und Schulterstütze Lack (`shell`), Unteres Gehäuse, Pumpe, Schaftrohr Polymer (`graphite`), Griff `rubber` |
| Grafik | ein Chevronband vorn am Oberen Gehäuse, ein Schriftzug „BASIC SG-08“ (dunkel auf Creme) |
| Front | Mündungshülse mit zwei Schlitzen oben und blanker Krone, Magazinkappe, Laufschelle; Kornfuß auf dem Ende der Lüftungsschiene |
| Übergänge | Ladeschacht im Unteren Gehäuse angeformt (Bauch vor dem Abzugsbügel, Ladeklappe unten); Lüftungsschiene setzt die Schiene bündig fort |
| Ergonomie | Griff BGM-1 in v2.1-Form (Familie), Pumpe mit Gummiauflagen und vorderer Fingerlippe, Pumpenriegel unter dem Daumen links |

Visier: K2 „Hörner“ (Baukasten v3, visier-konzept › 6a; Kimme/Korn nach Visier-Standard 3, Linie Schiene + 11 mm wie K1):
Flachblatt-Hörner auf der Schiene, oranger Kornkopf auf dem Ende der Lüftungsschiene (gleiche Höhe wie die Schiene). K3 „Lochkimme“
bleibt Variante (nur dokumentiert, `sight_kit_more.iron_ghost`).
Schlichtheitsbudget: Leuchten 1 Funktion (Munitionsanzeige) · Grafik 1 Band · Schrift 1 · Orange 3 (Pumpenriegel, Klemmhebel der
Kimme, Kornkopf) · Schrauben keine.
Bewegung: Pumpe 72 mm zurück, Verschluss mit ihr (Aktion `fire_pump`); Patrone von unten durch die Ladeklappe (`load_shell`).
Hülse: eigene Form `shotshell` (EJECT_CASES, Maße der Patrone `shell_round`) aus dem Auswurffenster rechts; die Form liegt im Modul,
solange `basic/arms/ego.py` im Unity-Quellenhash steht (Umzug nach `ego.EJECT.cases` mit dem Ego-Übertrag).
Status: Maße entworfen (Länge an Toolgen 0,904 m angelehnt, Verhältnis H/L an Destiny 0,29; gemessene Werte im Spec),
Formprinzipien abgeleitet aus den Bildreferenzen.
"""
from basic.common import part, prof, box, cyl, cut_box, rail, grip_v21, stock_s1, R_MID, R_SMALL, R_FINE
from basic.pilot.optics.sight_kit import hoerner
from basic.weapons import w08_shotgun as V1

META = dict(V1.META, variant='v2.1', name='Streuer v2.1', nick='Familie v2.1',
            summary='Vorderschaftrepetierflinte mit Lüftungsschiene, dickem Lauf über dem Röhrenmagazin und Kimme/Korn K2 (Stil v2.1).')
ASSEMBLIES = V1.ASSEMBLIES
GRIP_TOP = 44                      # Griffoberkante = Unterkante Unteres Gehäuse
BORE, BAR_R = 100, 12.5            # Laufachse, Laufradius (Ø 25)
TUBE_U, TUBE_R = 68, 10            # Röhrenmagazin
UP_U, TOP, DECK = 74, 120, 128     # Oberes Gehäuse unten / oben, Schienen- und Lüftungsschienen-Oberkante (Kimme-Linie DECK + 11)
RF = (-70, 150)                    # Gehäuse hinten / vorn
PUMP = (230, 390)                  # Pumpe in Ruhelage (zurück um PUMP_TRAVEL bis kurz vor das Gehäuse)
PUMP_TRAVEL = 72
RIB_F1 = 594                       # Ende der Lüftungsschiene
UP_W, LO_W = 42, 40

P = []
# ---------------------------------------------------------------- Gehäuse: Unteres (Graphit, Ladeschacht), Oberes (Creme), Mechanik
P += [
    prof('lower', 'Unteres Gehäuse', 'Lower receiver', 'receiver', 'graphite', 'Griffmodul, Abzug und Ladeschacht mit Ladeklappe',
         'unter dem Oberen Gehäuse, Fuge 1 mm', [(RF[0] + 12, UP_U - 1), (RF[1], UP_U - 1), (RF[1], 38), (144, 32), (100, 32), (92, 40),
                                                (92, GRIP_TOP), (-50, GRIP_TOP), (RF[0] + 12, 54)], LO_W, bevel=R_MID,
         cuts=[cut_box(RF[1] - PUMP_TRAVEL - 8, RF[1] + 1, TUBE_U - 3.6, TUBE_U + 3.6, 3.2, x=sx * (TUBE_R + 1.6)) for sx in (1, -1)]),   # Bahnen der Führungsstangen
    prof('upper', 'Oberes Gehäuse', 'Upper receiver', 'receiver', 'shell', 'Verschlussgehäuse; trägt Schiene und Lauf',
         'Grundkörper', [(RF[0], UP_U), (RF[1], UP_U), (RF[1], TOP - 4), (RF[1] - 4, TOP), (RF[0] + 8, TOP), (RF[0], TOP - 8)], UP_W,
         bevel=R_MID, cuts=[cut_box(26, 84, 86, 112, 24, x=-UP_W / 2)]),        # Auswurffenster rechts bis zum Verschluss
    box('bolt', 'Verschluss', 'Bolt', 'mechanism', 'metal', 'Verriegelt die Patrone; läuft mit der Pumpe zurück (im Fenster sichtbar)',
        'im Oberen Gehäuse geführt', 22, 88, 88, 110, 18, bevel=R_SMALL,
        move=dict(kind='translate', pivot=(55, BORE, 0), vector_mm=(-PUMP_TRAVEL, 0, 0), event='pump', expect=((88, BORE, -9), (-1, 0, 0)))),
    box('loading_gate', 'Ladeklappe', 'Loading gate', 'ammo', 'dark_metal', 'Öffnung unten zum Einschieben einzelner Patronen',
        'im Boden des Ladeschachts (federnd)', 104, 140, 31.4, 33, 24, bevel=R_FINE),
    box('counter_bezel', 'Anzeigenrahmen', 'Counter bezel', 'receiver', 'anodized', 'Fasst die Munitionsanzeige',
        'in den Ladeschacht eingelassen', 104, 140, 46, 57, 2.4, bevel=0.6, x=LO_W / 2 + 0.6),
    box('ammo_counter', 'Munitionsanzeige', 'Ammo counter', 'receiver', 'energy', 'Patronen im Röhrenmagazin; Blickfang links',
        'im Anzeigenrahmen', 107, 137, 48, 55, 1.0, bevel=0.2, x=LO_W / 2 + 1.6),
    cyl('pump_release', 'Pumpenriegel', 'Action release', 'grip_controls', 'accent', 'Gibt die Pumpe ohne Schuss frei (Daumen)',
        'Druckknopf links am Unteren Gehäuse', 'x', (74, 62), LO_W / 2 - 0.5, LO_W / 2 + 2.5, 3.6, segs=20,
        move=dict(kind='translate', pivot=(74, 62, LO_W / 2), vector_mm=(0, 0, -2.0), event='unlock',
                  expect=((74, 62, LO_W / 2 + 2.5), (0, 0, -1)))),
    part('band_side', 'Chevronband', 'Chevron band', 'receiver', 'multi', 'accent', 'Lackiertes Band (einziges Grafikelement)',
         'lackiert', bevel=0, items=[dict(shape='prof', pts=[(118, 80), (126, 80), (134, 96), (126, 112), (118, 112), (126, 96)], w=0.3,
                                          x=sx * (UP_W / 2 + 0.15)) for sx in (1, -1)]),
    part('text_l', 'Schriftzug', 'Lettering', 'receiver', 'text', 'anodized', 'Kennung „BASIC SG-08“ (einzige Schrift)',
         'aufgedruckt (dunkel auf Creme)', bevel=0, text='BASIC  SG-08', size=4.6, f=10, u=79, x=UP_W / 2 + 0.05, side=1, depth=0.12),
]
P += [dict(p, mat='anodized', attach='auf dem Oberen Gehäuse (fest)') for p in rail(RF[0] + 8, RF[1], TOP)]
# ---------------------------------------------------------------- Lauf, Lüftungsschiene, Röhrenmagazin, Mündung
P += [
    cyl('barrel', 'Lauf', 'Barrel', 'barrel', 'metal', 'Dicker Glattlauf für Streuschrot', 'im Oberen Gehäuse verschraubt',
        'f', (BORE, 0), RF[1], 582, BAR_R, segs=32),
    prof('vent_rib', 'Lüftungsschiene', 'Ventilated rib', 'barrel', 'anodized',
         'Visierebene über dem Lauf; setzt die Schiene bündig fort, trägt das Korn', 'auf Stegen über dem Lauf (fest)',
         [(RF[1], BORE + BAR_R + 0.1), (RIB_F1 - 4, BORE + BAR_R + 0.1), (RIB_F1, BORE + BAR_R + 3.5), (RIB_F1, DECK), (RF[1], DECK)], 9,
         bevel=R_FINE, cuts=[cut_box(182 + 60 * i, 218 + 60 * i, BORE + BAR_R - 1, DECK - 4, 20) for i in range(6)]),
    cyl('muzzle', 'Mündungshülse', 'Muzzle sleeve', 'barrel', 'anodized', 'Mündung mit zwei Schlitzen oben (hält die Mündung unten)',
        'auf das Laufende geschraubt', 'f', (BORE, 0), 572, 600, BAR_R + 2.5, r_in=9, segs=32, bevel=R_SMALL,
        cuts=[cut_box(580 + 8 * i, 584 + 8 * i, BORE + 6, BORE + 18, 12) for i in range(2)]),
    cyl('muzzle_crown', 'Mündungskrone', 'Muzzle crown', 'barrel', 'trim', 'Blanke Stirnkante', 'vorn an der Mündungshülse',
        'f', (BORE, 0), 598, 602, BAR_R + 1.5, r_in=9.5, segs=32, bevel=0.5),
    cyl('tube_mag', 'Röhrenmagazin', 'Tube magazine', 'ammo', 'dark_metal', 'Hält sechs Patronen unter dem Lauf',
        'unter dem Lauf, Laufschelle vorn', 'f', (TUBE_U, 0), RF[1], 546, TUBE_R, segs=24),
    cyl('tube_cap', 'Magazinkappe', 'Magazine cap', 'ammo', 'anodized', 'Verschließt das Röhrenmagazin', 'aufgeschraubt',
        'f', (TUBE_U, 0), 544, 560, TUBE_R + 1.5, segs=24, bevel=R_SMALL),
    box('barrel_clamp', 'Laufschelle', 'Barrel clamp', 'barrel', 'anodized', 'Verbindet Lauf und Magazinrohr',
        'auf Lauf und Rohr geklemmt', 514, 530, TUBE_U - TUBE_R - 2, BORE + BAR_R - 0.5, 27, bevel=R_SMALL),
]
# ---------------------------------------------------------------- Pumpe (Graphit) mit Gummiauflagen und Führungsstangen
_pm = dict(kind='translate', pivot=((PUMP[0] + PUMP[1]) / 2, TUBE_U, 0), vector_mm=(-PUMP_TRAVEL, 0, 0), event='pump')
P += [
    prof('pump', 'Vorderschaft (Pumpe)', 'Pump fore-end', 'mechanism', 'graphite', 'Stützhand repetiert: zurück und vor',
         'gleitet auf dem Röhrenmagazin', [(PUMP[0] + 10, 46), (PUMP[1] - 10, 46), (PUMP[1], 38), (PUMP[1] + 4, 44), (PUMP[1] + 2, 86),
                                           (PUMP[0], 86), (PUMP[0] - 4, 82), (PUMP[0] - 4, 50)], 50, bevel=R_MID,
         cuts=[dict(shape='cyl', axis='f', c=(TUBE_U, 0), a0=PUMP[0] - 6, a1=PUMP[1] + 6, r=TUBE_R + 0.4, segs=24)],   # läuft auf dem Rohr
         move=dict(_pm, expect=((PUMP[0] + 70, 46, 0), (-1, 0, 0)))),
    part('pump_pad', 'Pumpenauflagen', 'Pump pads', 'mechanism', 'multi', 'rubber', 'Rutschfeste Seiten für die Stützhand',
         'seitlich auf die Pumpe geklebt', bevel=0.6, parent_part='pump',
         items=[dict(shape='box', f0=PUMP[0] + 18, f1=PUMP[1] - 18, u0=54, u1=78, w=1.2, x=sx * 25.4) for sx in (1, -1)]),
    part('action_bars', 'Führungsstangen', 'Action bars', 'mechanism', 'multi', 'metal', 'Übertragen die Pumpe auf den Verschluss',
         'an der Pumpe, laufen ins Gehäuse', bevel=0.3, parent_part='pump',
         items=[dict(shape='box', f0=RF[1] - 4, f1=PUMP[0] + 4, u0=TUBE_U - 3, u1=TUBE_U + 3, w=2.2, x=sx * (TUBE_R + 1.6))
                for sx in (1, -1)]),
]
# ---------------------------------------------------------------- Patrone (Laden), Griff, Schaft S1 mit Durchbruch
P += [
    cyl('shell_round', 'Patrone', 'Shell', 'ammo', 'accent', 'Einzelne Schrotpatrone (beim Laden sichtbar)',
        'wird durch die Ladeklappe ins Rohr geschoben', 'f', (50, 0), 104, 148, 9.5, bevel=R_FINE, segs=20,
        move=dict(kind='translate', pivot=(124, 50, 0), vector_mm=(-24, -58, 0), event='load_shell', removable=True,
                  note='Ruhelage = im Ladeschacht (verdeckt); Aktion beginnt außen unter der Ladeklappe', expect=((148, 50, 0), (0, -1, 0)))),
    cyl('shell_head', 'Patronenboden', 'Shell head', 'ammo', 'brass', 'Messingboden der Patrone', 'an der Patrone',
        'f', (50, 0), 98, 104.5, 9.8, bevel=0.5, segs=20, parent_part='shell_round'),
]
P += grip_v21(top=GRIP_TOP)
_s = 1.1
_ua = BORE


def _L(d):
    return RF[0] - d * _s


for p in stock_s1(RF[0], _ua, s=_s):
    if p['id'] == 'stock':          # Durchbruch (Negativraum, wie First In, Last Out)
        p['cuts'] = [dict(shape='prof', pts=[(_L(100), _ua + 8), (_L(148), _ua + 10), (_L(150), _ua - 58), (_L(110), _ua - 26)], w=50)]
        p['func'] = 'Anlage an der Schulter, Wangenauflage oben; Durchbruch'
    P.append(p)
# ---------------------------------------------------------------- Visier K2 „Hörner“: Kimme auf der Schiene, Korn auf der Lüftungsschiene
_sight, SIGHT_ANCHORS = hoerner(-36, RIB_F1 - 8, DECK, front_w=8)
P += _sight
PARTS = P
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip', note='Haupthand, auf der Griffachse'),
    'Socket_SupportHand': dict(at=((PUMP[0] + PUMP[1]) / 2, 46, 0), part='pump', note='Unterseite der Pumpe; bewegt sich mit ihr'),
    'Socket_Muzzle': dict(at=(602, BORE, 0), part='muzzle_crown', note='Stirn der Mündungskrone auf der Laufachse'),
    'Socket_LoadingGate': dict(at=(122, 32, 0), part='loading_gate', note='Patronen einzeln von unten'),
}
ANCHORS.update(SIGHT_ANCHORS)
# Hülsenauswurf: eigene Form (Maße der Patrone); im Modul, solange ego.py im Unity-Quellenhash steht
EJECT_CASES = {'shotshell': dict(len_mm=50, r_mm=9.5, segs=14)}
EJECT = dict(at=(55, BORE, -UP_W / 2), dir=(0.15, 0.55, -1.0), case='shotshell',
             src='E: Auswurffenster rechts im Oberen Gehäuse beim Zurückziehen der Pumpe, Hülse nach rechts, etwas hoch und vorn')
ACTIONS = {
    'fire_pump': dict(de='Schuss und Repetieren', frames=30, step=1, keys={
        'trigger': [(0, 0), (2, 1), (6, 0)], 'pump': [(0, 0), (8, 0), (14, 1), (22, 0)], 'bolt': [(0, 0), (8, 0), (14, 1), (22, 0)]},
        events=[(2, 'shot'), (14, 'eject'), (22, 'ready')]),
    'load_shell': dict(V1.ACTIONS['load_shell']),
}
EXPLODE = {'sight': (0, 90, 0), 'ammo': (0, -120, 0), 'stock': (-110, 0, 0), 'barrel': (150, 0, 0), 'support': (0, 0, 0),
           'grip_controls': (-10, -80, 0), 'mechanism': (40, -60, 0), 'receiver': (0, 0, 0)}
