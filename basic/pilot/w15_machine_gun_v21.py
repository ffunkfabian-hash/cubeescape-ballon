"""BASIC-15 v2.1 – Maschinengewehr im Stil v2.1 („Destiny-Detaildichte + AAA-Material, schlicht“), Familie des Piloten BASIC-01 v2.1.

Recherche (docs/quellen.md › Q-D2-IMG, gesichtet 28.10.2026, Bungie-Manifest): Hammerhead, Avalanche, Retrofit Escapade (breites
Gehäuse, Munitionsbehälter vor dem Griff, Gurt sichtbar als Patronensäule an der linken Seite bis zur
Zuführung, Deckel mit Visier oben, langer Laufmantel mit Lüftung), Corrective Measure und Fixed Odds (gerade lange Oberkante,
Laufmantel mit Fenstern, freier Lauf vorn), Shattered Cipher (Zweibein; hier nicht verlangt). Nur Prinzipien; Leitmerkmal 15 nach
Designvertrag: Zuführdeckel, Munitionskasten, Tragegriff.

Formsprache-Checkliste (stilhandbuch §3):
| Frage | Maschinengewehr v2.1 |
|---|---|
| Leitmerkmal der Silhouette | breites Gehäuse mit Zuführdeckel (Visier darauf), links vor dem Griff der seitlich eingehängte Munitionskasten (Nutzer: „Kasten seitlich“); aus ihm steigt der Gurt als Patronensäule in den Einlauf; langer Laufmantel mit Lüftungsfenstern, freier Lauf |
| Schichten | Unteres Gehäuse, Handschutz, Schaft (Graphit) → Gehäuse, Zuführdeckel, Laufmantel (Creme, Fuge 1 mm) → Seitenpaneele, Kasten (eloxiert/Metall) → Schiene → Visier H6 |
| Negativraum | Gurt frei zwischen Kasten und Zuführung (Patronen sichtbar); Lüftungsfenster im Laufmantel zeigen den Lauf; Durchbruch im Schaft S1 |
| Blickfang | Gurtsäule: Messingpatronen in dunklen Gliedern an der linken Seite (Ego-Seite), die in den Gurteinlauf mit blanker Lippe laufen – starker Kontrast ohne Leuchten |
| Zweiton-Blockung | Gehäuse, Deckel, Laufmantel Lack (`shell`), Unteres Gehäuse, Handschutz, Schaft Polymer (`graphite`), Kasten `dark_metal` |
| Grafik | ein Schrägband vorn am Laufmantel, ein Schriftzug „BASIC MG-15“ (hell auf Graphit) |
| Front | gerändelte Mündungsbremse mit Schlitzen und blanker Krone vor dem freien Lauf |
| Übergänge | Kasten an einer blanken Einhängeleiste links am Unteren Gehäuse; Deckel liegt auf dem Gehäuse (Scharnier vorn, darunter die Zuführschale), Laufmantel stößt mit Fuge 1 mm an |
| Ergonomie | Griff BGM-1 in v2.1-Form (Familie), Kasten links vor dem Griff (Ego-Seite, Stützhand wechselt ihn), Handschutz unter dem Mantel mit Griffpolster; Tragegriff links am Mantel angeklappt (Laufwechsel), außerhalb des Zielbilds |

Visier: H6 „Achteck“ (Baukasten v3, visier-konzept › 6a; `sight_kit.achteck`) in **Größe L**: Fenster 34 × 26, 24,7 % der
Bildbreite – zugelassene Variante Holo L (bis 25 %, nur MG/Werfer, seit 0.21). Begründung: das MG zielt aus der Bewegung auf
Gruppen und hält Dauerfeuer, das größere Fenster behält das Ziel trotz Rückstoß im Bild; Größe M (30 × 22) läge mit 21,8 % über
dem Holo-Band und ist keine zugelassene Größe. H1 Fase (L) nur als Variante im Katalog. Absehen gezeichnet (`ring_dot` flach).
Schlichtheitsbudget: Leuchten 2 Funktionen (Munition: Zählfenster am Kasten · Visier: Emitter und Absehen) · Grafik 1 Band ·
Schrift 1 · Orange 3 (Ladehebel, Deckelriegel, Klemmhebel des Visiers) · Schrauben nur an Paneelen, Mantel und Schaft.
Proportion: Länge ≈ 0,96 m (v1 1,07 m); Destiny-MG H/L 0,30 (Shattered Cipher, mit Zweibein; Motiongen proportionen › 2).
Bewegung (Daten): Abzug, Verschluss, Auswurfklappe und Gurtvorschub (eine Gliedteilung 10,4 mm je Schuss nach oben, danach zurück:
`move.cycle = 'shot'`) beim Dauerfeuer (`fire_auto`), Deckel auf, Kasten tauschen, Deckel zu (`reload`). Nutzer 28.10.2026: „Ist die
Munitionskiste später animiert, dass man sieht, dass die Kugeln aus dem Kasten gezogen werden?“ – Daten jetzt, Clips mit dem Ego-Übertrag. Auswurf: Hülsen und Gurtglieder nach rechts (`EJECT` mit `links`, Daten statt Sonderlogik; check: Munitionskasten
BAB-1 → Hülse und Glied).
Status: Maße entworfen (Länge kürzer als v1, an Familie 01 angelehnt; gemessene Werte im Spec), Formprinzipien abgeleitet.
"""
from basic.common import (part, prof, box, cyl, cut_box, screws, mirror, rail, grip_v21, stock_s1, charging_handle,
                          R_MID, R_SMALL, R_FINE)
from basic.pilot.optics.sight_kit import achteck
from basic.weapons import w15_machine_gun as V1

META = dict(V1.META, variant='v2.1', name='Dauerlauf v2.1', nick='Familie v2.1',
            summary='Maschinengewehr mit Zuführdeckel, seitlichem Munitionskasten, sichtbarem Gurt und Visier H6 L (Stil v2.1).')
ASSEMBLIES = V1.ASSEMBLIES
GRIP_TOP = 40
BORE = 106                   # Laufachse
TOP = 122                    # Oberkante Gehäuse; Deckel bis u 138, Schiene bis u 146, Visierlinie u 172 (Visierhöhe 66)
COVER = (-60, 150, TOP, 138)  # Zuführdeckel f0, f1, u0, u1
COVER_PIV = (150, 130)       # Scharnier vorn
REC0, REC1 = -150, 210       # Gehäuse hinten / vorn
W_REC = 52
BOX = (92, 228, 0, 60)       # Munitionskasten f0, f1, u0, u1: seitlich links am Unteren Gehäuse eingehängt, flach und lang
                             # (Nutzer 28.10.2026: „Kasten seitlich“, dann „eher in die Breite … als in die Höhe“: 136 × 60 statt 104 × 96)
_bw = 46                     # Kastenbreite x
BOX_X = 24.6 + _bw / 2       # Kastenmitte x: Innenseite an der linken Seite des Unteren Gehäuses (x 24)
BELT_X = 31.8                # Mitte der Gurtsäule (außen an der linken Wand x 26; Glieder r 5,4 frei)
FEED = (98, 152, 96, 118)    # Zuführfenster links f0, f1, u0, u1
PORT = (100, 142, 86, 104)   # Auswurffenster rechts
LINK_PORT = (112, 138, 111, 118)   # Gliederauswurf rechts über dem Auswurffenster
SHROUD = (211, 520, 84, 124)  # Laufmantel f0, f1, u0, u1
MUZ = (604, 650)             # Mündungsbremse

P = []
# ---------------------------------------------------------------- Gehäuse, Deckel, Mechanik
P += [
    prof('receiver', 'Gehäuse', 'Receiver', 'receiver', 'shell', 'Breiter Tragkörper; Zuführung links, Auswurf rechts',
         'Grundkörper; mit dem Unteren Gehäuse über zwei Querbolzen (fest)',
         [(REC0, 80), (REC1, 80), (REC1, TOP), (REC0 + 10, TOP), (REC0, TOP - 10)], W_REC,
         cuts=[cut_box(*FEED[:2], *FEED[2:], 12, x=W_REC / 2),                          # Zuführfenster links (Gurt tritt ein)
               cut_box(*PORT[:2], *PORT[2:], 12, x=-W_REC / 2),                         # Auswurffenster rechts (zeigt den Verschluss)
               cut_box(*LINK_PORT[:2], *LINK_PORT[2:], 12, x=-W_REC / 2),               # Gliederauswurf rechts
               cut_box(-128, -88, 108, 116, 10, x=W_REC / 2),                           # Ladehebel-Nut links
               cut_box(-132, -40, 86, 102, 3.0, x=W_REC / 2 + 0.6), cut_box(-132, -40, 86, 102, 3.0, x=-W_REC / 2 - 0.6),   # Paneel-Mulden
               cut_box(FEED[0] - 2, FEED[1] + 2, COVER[2] - 5, TOP + 2, W_REC - 8)]),   # Öffnung unter dem Deckel (Zuführschale)
    prof('lower', 'Unteres Gehäuse', 'Lower receiver', 'receiver', 'graphite', 'Griffmodul, Abzugsgruppe, Kastenaufnahme links',
         'unter dem Gehäuse, Fuge 1 mm',
         [(REC0, 62), (-70, 40), (204, 40), (REC1, 62), (REC1, 79),
          (REC0, 79)], W_REC - 4),
    box('box_lip', 'Einhängeleiste', 'Box hanger', 'receiver', 'trim', 'Blanke Leiste, an der der Kasten links eingehängt wird',
        'links am Unteren Gehäuse über dem Kasten', BOX[0] - 2, REC1 - 2, BOX[3], BOX[3] + 4, 2.4, bevel=0.6, x=24.6 + 1.2 - 0.6,
        iface='BAB-1'),
    box('side_panel_l', 'Seitenpaneel links', 'Side panel left', 'receiver', 'anodized', 'Wartungsdeckel über dem Puffer',
        'in die Mulde geschraubt (4 Schrauben)', -130, -42, 88, 100, 1.2, bevel=R_FINE, x=W_REC / 2 - 0.8),
    box('side_panel_r', 'Seitenpaneel rechts', 'Side panel right', 'receiver', 'anodized', 'Wartungsdeckel über dem Puffer',
        'in die Mulde geschraubt (4 Schrauben)', -130, -42, 88, 100, 1.2, bevel=R_FINE, x=-W_REC / 2 + 0.8),
    part('panel_screws', 'Paneelschrauben', 'Panel screws', 'receiver', 'multi', 'trim', 'Halten die Seitenpaneele',
         'in den Paneelen', bevel=0.2, items=mirror(screws([(-126, 91), (-126, 97), (-46, 91), (-46, 97)], W_REC / 2 - 0.2, r=1.6, h=0.8))),
    part('takedown_pins', 'Querbolzen', 'Takedown pins', 'receiver', 'multi', 'metal', 'Verbinden Gehäuse und Unteres Gehäuse',
         'quer durch das Gehäuse (lösbar)', bevel=0.4, items=mirror(screws([(-136, 72), (196, 72)], W_REC / 2 - 1, r=3.6, h=1.0))),
    prof('feed_cover', 'Zuführdeckel', 'Feed cover', 'mechanism', 'shell', 'Hält den Gurt in der Zuführung; trägt das Visier',
         'Scharnier vorn, öffnet hinten nach oben', [(COVER[0], COVER[2]), (COVER[1], COVER[2]), (COVER[1], COVER[3] - 4),
                                                     (COVER[1] - 8, COVER[3]), (COVER[0] + 8, COVER[3]), (COVER[0], COVER[3] - 6)], W_REC - 6.6,
         move=dict(kind='rotate', pivot=(COVER_PIV[0], COVER_PIV[1], 0), axis='x', range_deg=(0, -62), event='reload',
                   expect=((COVER[0] + 8, COVER[3], 0), (0, 1, 0)))),
    cyl('cover_hinge', 'Deckelscharnier', 'Cover hinge', 'mechanism', 'trim', 'Drehachse des Deckels', 'vorn quer durch das Gehäuse',
        'x', COVER_PIV, -W_REC / 2 - 0.8, W_REC / 2 + 0.8, 4.0, segs=20, bevel=0.4),
    prof('cover_latch', 'Deckelriegel', 'Cover latch', 'mechanism', 'accent', 'Verriegelt den Deckel; zum Öffnen nach vorn drücken',
         'hinten am Deckel', [(COVER[0] - 6, COVER[2] + 2), (COVER[0] + 1, COVER[2] + 2), (COVER[0] + 1, COVER[3] - 4),
                              (COVER[0] - 4, COVER[3] - 4)], 30, bevel=R_FINE, parent_part='feed_cover'),
    box('feed_tray', 'Zuführschale', 'Feed tray', 'ammo', 'dark_metal', 'Führt den Gurt quer ins Gehäuse', 'unter dem Deckel im Gehäuse',
        FEED[0] - 2, FEED[1] + 2, COVER[2] - 7, COVER[2] - 5, W_REC - 8, bevel=R_FINE),
    box('bolt', 'Verschluss', 'Bolt', 'mechanism', 'metal', 'Lädt und verriegelt; läuft beim Schuss zurück', 'im Gehäuse geführt',
        PORT[0] - 40, PORT[1] - 2, 90, 102, 30, bevel=R_SMALL,
        move=dict(kind='translate', pivot=(PORT[0], 96, 0), vector_mm=(-40, 0, 0), event='fire',
                  expect=((PORT[1] - 2, 96, 0), (-1, 0, 0)))),
    prof('port_cover', 'Auswurfklappe', 'Ejection port cover', 'mechanism', 'anodized', 'Deckt das Auswurffenster ab',
         'Scharnier an der Unterkante', [(PORT[0], PORT[2]), (PORT[1], PORT[2]), (PORT[1], PORT[3]), (PORT[0], PORT[3])], 1.6,
         bevel=R_FINE, x=-W_REC / 2 - 0.6,
         move=dict(kind='rotate', pivot=((PORT[0] + PORT[1]) / 2, PORT[2], -W_REC / 2 - 1.4), axis='f', range_deg=(0, 75), event='fire',
                   expect=(((PORT[0] + PORT[1]) / 2, PORT[3], -W_REC / 2 - 1.4), (0, 0, -1)))),
]
P += charging_handle(-124, 112, x=W_REC / 2 + 4.5, travel=70)
P += [dict(p, mat='anodized', parent_part='feed_cover') for p in rail(-30, 60, COVER[3])]
P[-1]['cuts'] = [cut_box(-24 + 12 * i, -18 + 12 * i, COVER[3] + 4, COVER[3] + 9, 30) for i in range(7)]
# Visier H6 „Achteck“ L (Baukasten v3, Standard MG nach visier-konzept › 6a; Holo-L-Variante)
SIGHT_SIZE = 'L'
_sight, SIGHT_ANCHORS = achteck(-26, COVER[3] + 8, SIGHT_SIZE, weapon_type=V1.META['type'])
for p in _sight:
    if p['id'] == 'sight_mount':
        p['parent_part'] = 'feed_cover'
P += _sight
# ---------------------------------------------------------------- Munitionskasten und Gurt (Blickfang)
_bc = ((BOX[0] + BOX[1]) / 2, (BOX[2] + BOX[3]) / 2)
PITCH = 10.4                                        # Gliedteilung (Patronenabstand im Gurt)
ROUNDS = [BOX[3] + 4.4 + PITCH * i for i in range(4)]   # Patronenmitten u der Gurtsäule (Kastenoberkante innen → Einlauf)
MOUTH = FEED[2] - 2                                 # Unterkante des Gurteinlaufs (Lippe); darüber läuft der Gurt ins Gehäuse
P += [
    part('ammo_box', 'Munitionskasten', 'Ammo box', 'ammo', 'box', 'dark_metal', 'Hält den Gurt; austauschbar',
         'links am Unteren Gehäuse eingehängt (lösbar)', bevel=R_MID, iface='BAB-1', f0=BOX[0], f1=BOX[1], u0=BOX[2], u1=BOX[3], w=_bw, x=BOX_X,
         cuts=[cut_box(BOX[0] + 8, BOX[1] - 8, BOX[2] + 14, BOX[3] - 10, 3.0, x=BOX_X + sx * _bw / 2) for sx in (1, -1)],   # Seitenmulden
         move=dict(kind='translate', pivot=(_bc[0], _bc[1], BOX_X), vector_mm=(0, -70, 90), event='reload', removable=True,
                   expect=((_bc[0], BOX[2], BOX_X + _bw / 2), (0, -1, 1)))),
    box('box_band', 'Kastenband', 'Box band', 'ammo', 'trim', 'Blankes Band über dem Kastenboden; Greifkante', 'um den Kasten',
        BOX[0] - 0.6, BOX[1] + 0.6, BOX[2] + 6, BOX[2] + 10, _bw + 1.2, bevel=0.4, x=BOX_X, parent_part='ammo_box'),
    box('box_counter', 'Zählfenster', 'Round counter', 'ammo', 'energy', 'Zeigt den Füllstand des Kastens', 'links in den Kasten eingelassen',
        BOX[1] - 34, BOX[1] - 14, BOX[2] + 18, BOX[2] + 24, 1.0, bevel=0.3, x=BOX_X + _bw / 2 - 1.0, parent_part='ammo_box'),
    prof('box_grip', 'Kastengriff', 'Box grip', 'ammo', 'anodized', 'Griffleiste vorn am Kasten (Kasten ziehen)', 'vorn am Kasten verschraubt',
         [(BOX[1] - 1, BOX[2] + 12), (BOX[1] + 5, BOX[2] + 16), (BOX[1] + 5, BOX[3] - 16), (BOX[1] - 1, BOX[3] - 12)], 22, bevel=R_SMALL,
         x=BOX_X, parent_part='ammo_box'),
    part('belt', 'Gurt', 'Belt', 'ammo', 'multi', 'brass', 'Patronen im Gurt vom Kasten zur Zuführung (sichtbarer Füllstand)',
         'im Kasten, durch die Gurtführung in den Einlauf', bevel=0.3, smooth=True, parent_part='ammo_box',
         move=dict(kind='translate', pivot=(FEED[0] + 22, ROUNDS[-1], BELT_X), vector_mm=(0, PITCH, 0), event='fire', cycle='shot',
                   note='Vorschub um eine Gliedteilung je Schuss nach oben in den Einlauf, danach zurück (Schleife: die nächste Patrone '
                        'steht an derselben Stelle); Animation mit dem Ego-Übertrag',
                   expect=((FEED[0] + 22, ROUNDS[-1], BELT_X), (0, 1, 0))),
         items=[dict(shape='cyl', axis='f', c=(u, BELT_X), a0=FEED[0] + 2, a1=FEED[0] + 44, r=4.6, segs=16) for u in ROUNDS]
         + [dict(shape='cyl', axis='f', c=(u, BELT_X), a0=FEED[0] + 44, a1=FEED[0] + 54, r=4.6, r1=1.6, segs=16) for u in ROUNDS]),
    part('belt_links', 'Gurtglieder', 'Belt links', 'ammo', 'multi', 'dark_metal', 'Verbinden die Patronen; werden ausgeworfen',
         'um die Patronen', bevel=0.2, smooth=True, parent_part='belt',
         items=[dict(shape='cyl', axis='f', c=(u, BELT_X), a0=FEED[0] + a, a1=FEED[0] + a + 7, r=5.4, r_in=4.5, segs=16)
                for u in ROUNDS for a in (8, 30)]),
    part('belt_guide', 'Gurtführung', 'Belt guide', 'ammo', 'multi', 'anodized', 'Führt den Gurt vom Kasten zum Zuführfenster',
         'links am Gehäuse verschraubt', bevel=R_FINE,
         items=[dict(shape='box', f0=f0, f1=f0 + 4, u0=BOX[3] - 2, u1=MOUTH, w=12, x=BELT_X) for f0 in (FEED[0] - 4, FEED[1] + 1)]),
    # Gurteinlauf (Nutzer 28.10.2026: „eine Art ‚Eingang‘ für die Munition“): Schacht links über dem Zuführfenster, unten offen mit
    # blanker Lippe; der Gurt läuft von unten hinein
    prof('feed_mouth', 'Gurteinlauf', 'Belt feed mouth', 'ammo', 'anodized', 'Schacht, in den der Gurt läuft; führt ihn ins Zuführfenster',
         'links über dem Zuführfenster verschraubt', [(FEED[0] - 5, MOUTH), (FEED[1] + 5, MOUTH), (FEED[1] + 5, FEED[3] - 2),
                                                      (FEED[1] - 3, FEED[3] + 2), (FEED[0] + 3, FEED[3] + 2), (FEED[0] - 5, FEED[3] - 2)],
         BELT_X + 8 - W_REC / 2 + 1, bevel=R_SMALL, x=(BELT_X + 8 + W_REC / 2 - 1) / 2,
         cuts=[cut_box(FEED[0] - 1, FEED[1] + 2, MOUTH - 4, FEED[3] - 1, BELT_X + 6 - W_REC / 2 + 1.4, x=(BELT_X + 6 + W_REC / 2 - 1.4) / 2)]),
    part('feed_lip', 'Einlauflippe', 'Feed lip', 'ammo', 'multi', 'trim', 'Blanke Kante um die Öffnung des Einlaufs',
         'unten am Gurteinlauf', bevel=0.3,
         items=[dict(shape='box', f0=FEED[0] - 5.6, f1=FEED[1] + 5.6, u0=MOUTH - 1.2, u1=MOUTH + 1.4, w=1.8, x=BELT_X + 7.4)]
         + [dict(shape='box', f0=f0, f1=f0 + 3.0, u0=MOUTH - 1.2, u1=MOUTH + 1.4, w=BELT_X + 8.3 - W_REC / 2, x=(BELT_X + 8.3 + W_REC / 2) / 2)
            for f0 in (FEED[0] - 5.6, FEED[1] + 2.6)]),
]
# ---------------------------------------------------------------- Laufmantel, Handschutz, Tragegriff, Lauf
VENTS = [(344, 376), (388, 420), (432, 464), (476, 508)]   # vor dem Tragegriff
HANDLE = (226, 326)          # Tragegriff f (Griffböcke an beiden Enden)
P += [
    prof('shroud', 'Laufmantel', 'Barrel shroud', 'support', 'shell', 'Hitzeschutz mit Lüftungsfenstern; Lauf sichtbar',
         'am Gehäuse verschraubt, Fuge 1 mm', [(SHROUD[0], SHROUD[2]), (SHROUD[1] - 16, SHROUD[2]), (SHROUD[1], SHROUD[2] + 14),
                                                (SHROUD[1], SHROUD[3] - 6), (SHROUD[1] - 8, SHROUD[3]), (SHROUD[0], SHROUD[3])], 42,
         cuts=[cut_box(f0, f1, 98, 116, 60) for f0, f1 in VENTS]
         + [dict(shape='cyl', axis='f', c=(BORE, 0), a0=SHROUD[0] - 1, a1=SHROUD[1] + 1, r=15, segs=32)]),
    prof('handguard', 'Handschutz', 'Handguard', 'support', 'graphite', 'Griffbereich der Stützhand unter dem Mantel',
         'unter den Laufmantel geschraubt, Fuge 1 mm', [(SHROUD[0] + 20, 64), (420, 64), (440, 74), (440, 83), (SHROUD[0] + 20, 83)], 44),
    prof('handguard_grip', 'Griffpolster', 'Grip pad', 'support', 'rubber', 'Rutschfeste Zone für die Stützhand',
         'unten auf den Handschutz geklebt', [(270, 60.5), (400, 60.5), (400, 66), (270, 66)], 38, bevel=R_SMALL),
    part('shroud_screws', 'Mantelschrauben', 'Shroud screws', 'support', 'multi', 'trim', 'Halten Mantel und Handschutz',
         'seitlich', bevel=0.2, items=mirror(screws([(218, 92), (218, 116), (240, 72)], 21.0, r=1.8, h=0.8))),
    prof('carry_handle', 'Tragegriff', 'Carry handle', 'support', 'rubber', 'Tragen und Laufwechsel; links am Mantel angeklappt',
         'zwischen den Griffböcken (klappt nach oben)', [(HANDLE[0] + 10, 100), (HANDLE[1] - 10, 100), (HANDLE[1] - 6, 104),
                                                         (HANDLE[1] - 6, 112), (HANDLE[1] - 10, 116), (HANDLE[0] + 10, 116),
                                                         (HANDLE[0] + 6, 112), (HANDLE[0] + 6, 104)], 7, bevel=R_SMALL, x=29.5),
    part('handle_blocks', 'Griffböcke', 'Handle blocks', 'support', 'multi', 'anodized', 'Lagern den Tragegriff mit Abstand zum Mantel',
         'links auf den Mantel geschraubt', bevel=R_SMALL,
         items=[dict(shape='prof', pts=[(f0, 96), (f0 + 14, 96), (f0 + 14, 120), (f0, 120)], w=12, x=26.0)
                for f0 in (HANDLE[0], HANDLE[1] - 14)]),
    part('band_side', 'Schrägband', 'Slanted band', 'support', 'multi', 'accent', 'Lackiertes Band (einziges Grafikelement)',
         'lackiert', bevel=0, items=[dict(shape='prof', pts=[(492, SHROUD[2] + 0.5), (502, SHROUD[2] + 0.5), (508, SHROUD[3] - 0.5),
                                                              (498, SHROUD[3] - 0.5)], w=0.3, x=sx * 21.15) for sx in (1, -1)]),
    part('text_l', 'Schriftzug', 'Lettering', 'support', 'text', 'decal', 'Kennung „BASIC MG-15“ (einzige Schrift)',
         'aufgedruckt', bevel=0, text='BASIC  MG-15', size=5.0, f=300, u=70, x=22.05, side=1, depth=0.12),
    cyl('barrel', 'Lauf', 'Barrel', 'barrel', 'metal', 'Führt das Geschoss; im Mantel sichtbar, vorn frei', 'im Gehäuse verschraubt',
        'f', (BORE, 0), 190, MUZ[0] + 4, 11, segs=24, smooth=True),
    part('barrel_fins', 'Kühlrippen', 'Cooling fins', 'barrel', 'multi', 'dark_metal', 'Führen Laufwärme ab; in den Fenstern sichtbar',
         'auf den Lauf gepresst', bevel=0.4, smooth=True,
         items=[dict(shape='cyl', axis='f', c=(BORE, 0), a0=f0 + 6 + 10 * k, a1=f0 + 10 + 10 * k, r=13.5, segs=24)
                for f0, f1 in VENTS for k in range(3)]),
    cyl('muzzle', 'Mündungsbremse', 'Muzzle brake', 'barrel', 'anodized', 'Mündungsteil mit Schlitzen; Socket_Muzzle',
        'auf Laufende geschraubt (lösbar)', 'f', (BORE, 0), MUZ[0], MUZ[1], 16, r_in=5.5, segs=8, bevel=R_SMALL, iface='BMZ-15',
        cuts=[cut_box(MUZ[0] + 22 + 8 * i, MUZ[0] + 27 + 8 * i, BORE + 6, BORE + 22, 14) for i in range(3)]
        + [cut_box(MUZ[0] + 24, MUZ[1] - 6, BORE - 4, BORE + 4, 44)]
        + [dict(shape='cyl', axis='f', c=(BORE, 0), a0=MUZ[0] + 4 + 4 * i, a1=MUZ[0] + 5.6 + 4 * i, r=18, r_in=15.4, segs=8)
           for i in range(4)]),
    cyl('muzzle_crown', 'Mündungskrone', 'Muzzle crown', 'barrel', 'trim', 'Blanke Stirnkante', 'vorn an der Bremse',
        'f', (BORE, 0), MUZ[1] - 2, MUZ[1] + 4, 14.5, r_in=6, segs=8, bevel=0.6),
    cyl('barrel_nut', 'Laufmutter', 'Barrel nut', 'barrel', 'trim', 'Spannt den Lauf im Gehäuse', 'am Gehäuseende vorn',
        'f', (BORE, 0), REC1 - 4, REC1 + 4, 16, segs=24, bevel=0.6),
]
# ---------------------------------------------------------------- Griff, Schaft S1 mit Durchbruch
P += grip_v21(top=GRIP_TOP)
_f0, _s, _ua = REC0, 1.0, BORE - 6    # Schaftachse 6 mm unter dem Lauf: Verbindung und Schulterstütze nicht über dem Gehäuse (Nutzer)


def _L(d):
    return _f0 - d * _s


for p in stock_s1(_f0, _ua, s=_s):
    if p['id'] == 'stock':
        # Durchbruch mit ≥ 12 mm Rand zur schrägen Unterkante (dünner Steg gab einen schwarzen Keil, Nutzer)
        p['cuts'] = [dict(shape='prof', pts=[(_L(100), _ua + 8), (_L(146), _ua + 10), (_L(148), _ua - 58), (_L(118), _ua - 36)], w=50)]
        p['func'] = 'Anlage an der Schulter; Durchbruch'
    if p['id'] == 'butt_pad':
        p['mat'] = 'rubber'
    P.append(p)
P += [part('stock_bolts', 'Schaftbolzen', 'Stock bolts', 'stock', 'multi', 'trim', 'Halten den Schaft am Gehäuse',
           'quer durch die Schaftverbindung', bevel=0.3, items=mirror(screws([(_f0 - 6, _ua + 12), (_f0 - 6, _ua - 16)], 15.4, r=2.4, h=1.0)))]
PARTS = P
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip', note='Haupthand, auf der Griffachse'),
    'Socket_SupportHand': dict(at=(335, 60.5, 0), part='handguard', note='Griffpolster unter dem Laufmantel'),
    'Socket_Muzzle': dict(at=(MUZ[1] + 4, BORE, 0), part='muzzle_crown', note='Stirn der Mündungskrone auf der Laufachse'),
    'Socket_FeedCover': dict(at=(COVER[0] + 8, COVER[3], 0), part='feed_cover', note='Griffpunkt zum Öffnen'),
    'Socket_AmmoBox': dict(at=(_bc[0], BOX[2], BOX_X), part='ammo_box', note='Griffpunkt am Kastenboden (Schnittstelle BAB-1)'),
}
ANCHORS.update(SIGHT_ANCHORS)
# Auswurf (Daten, kein Anker): Hülse aus dem Auswurffenster rechts unten, Glied aus dem Gliederauswurf darüber; beide nach rechts
# (vom Auge weg). Das Glied ist eine eigene Form im Modul, solange ego.py im Unity-Quellenhash steht (wie die Schrothülse von 08).
EJECT_CASES = {'belt_link': dict(len_mm=8, r_mm=5.4, segs=10)}
EJECT = dict(at=((PORT[0] + PORT[1]) / 2, (PORT[2] + PORT[3]) / 2, -W_REC / 2), dir=(0.15, -0.3, -1.0), case='rifle',
             src='E: Auswurffenster rechts unter der Klappe port_cover, Hülse nach rechts und etwas nach unten',
             links=dict(at=((LINK_PORT[0] + LINK_PORT[1]) / 2, (LINK_PORT[2] + LINK_PORT[3]) / 2, -W_REC / 2), dir=(0.1, 0.35, -1.0),
                        case='belt_link', src='E: Gliederauswurf rechts über dem Auswurffenster, Glied nach rechts und etwas hoch'))
_shots = [3, 7, 11, 15, 19]
ACTIONS = {
    'fire_auto': dict(de='Dauerfeuer (Verschluss sichtbar)', frames=30, step=1, keys={
        'trigger': [(0, 0), (3, 1), (27, 1), (30, 0)], 'port_cover': [(0, 0), (4, 1), (30, 1)],
        'bolt': [(0, 0), (3, 0)] + [k for s in _shots for k in ((s + 2, 1), (s + 4, 0))],
        'belt': [(0, 0)] + [k for s in _shots for k in ((s, 0), (s + 3, 1), (s + 3, 0))]},
        events=[(s, 'shot') for s in _shots], view=(-0.85, -0.25, 0.45)),
    'reload': dict(de='Deckel auf, Kasten tauschen, Gurt einlegen, Deckel zu', frames=150, keys={
        'feed_cover': [(0, 0), (16, 1), (118, 1), (134, 0)], 'ammo_box': [(0, 0), (24, 0), (44, 1), (76, 1), (100, 0)]},
        events=[(16, 'cover_open'), (44, 'box_out'), (100, 'box_in'), (112, 'belt_seated'), (134, 'cover_closed')],
        view=(0.75, -0.35, 0.55)),
}
EXPLODE = {'sight': (0, 120, 0), 'mechanism': (0, 70, 0), 'ammo': (0, -150, 40), 'stock': (-110, 0, 0), 'barrel': (160, 0, 0),
           'support': (60, -50, 0), 'grip_controls': (-10, -80, 0), 'receiver': (0, 0, 0)}
SIGHT_ID = 'H6'    # Visier des Baukastens v3 (visier-konzept › 6a); test_sights prüft dessen Pflichtteile und Merkmale
