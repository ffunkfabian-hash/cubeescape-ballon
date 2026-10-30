"""BASIC-09 v2.1 – Scharfschützengewehr im Stil v2.1 („Destiny-Detaildichte + AAA-Material, schlicht“), Familie des Piloten BASIC-01 v2.1.

Recherche (docs/quellen.md › Q-D2-IMG, gesichtet 28.10.2026, Bungie-Manifest): Elegy-49 (hohes helles Gehäuse, langer Laufmantel mit
Längsschlitz, freier Lauf mit großer Mündungsbremse, großes Kastenmagazin), Maxim XI (eine lange durchgehende Haube vom Schaft bis
vor die Hälfte, darunter dunkler Vorderschaft, Kastenmagazin vor dem Griff), Far Future (Längsstaffelung: dünner langer freier
Lauf). Nur Prinzipien; Leitmerkmal 09 nach Designvertrag: Kammerstängel, großes Zielfernrohr.

Formsprache-Checkliste (stilhandbuch §3):
| Frage | Scharfschützengewehr v2.1 |
|---|---|
| Leitmerkmal der Silhouette | großes Zielfernrohr Z3 mit Sonnenblende über langem Creme-Gehäuse mit Laufmantel; Kammerstängel links (Ego-Seite); langer freier Lauf mit großer Bremse (Längsstaffelung dick – lang – dünn – Bremse) |
| Schichten | Unteres Gehäuse und Vorderschaft (Graphit, Fuge 1 mm) → Gehäuse (Creme) → Laufmantel (Creme, 4 mm schmaler, Fuge 1 mm, bis f 530) → Sattelblock (Creme, schmal) → Schienen (eloxiert) → Zielfernrohr |
| Negativraum | Längsschlitz quer durch den Laufmantel (Lauf sichtbar); offene Kammerbahn links und Auswurffenster rechts (Verschluss sichtbar); Lauf vorn frei; Durchbruch im Schaft |
| Blickfang | Zielfernrohr Z3 „Lang“: großer flacher Ring, blanke Sonnenblende, oranger Höhenturm |
| Zweiton-Blockung | Haube und Schulterstütze Lack (`shell`), Unteres Gehäuse, Vorderschaft, Schaftrohr Polymer (`graphite`), Griff `rubber` |
| Grafik | ein Chevronband vorn an der Haube, ein Schriftzug „BASIC SR-09“ (dunkel auf Creme) |
| Front | dreifach geschlitzte Mündungsbremse mit blanker Krone; kannelierter freier Lauf; Mantelstirn mit Laufdurchtritt |
| Übergänge | Magazintrichter im Unteren Gehäuse angeformt; Laufmantel fällt nach vorn leicht ab; Sattelblock 26 mm schmal auf dem Gehäuse (Rampe vorn), damit der gehobene Kammerknopf links vorbeiläuft |
| Ergonomie | Griff BGM-1 in v2.1-Form (Familie), Kastenmagazin (5) vor dem Griff, Kammerknopf links über dem Griff (die Stützhand repetiert, Nutzer 28.10.2026), hohe Wangenauflage |

Visier: Z3 „Lang“ (Baukasten v3, visier-konzept › 6a; Visier-Standard 3 Typ `fullscreen`: im Zielen Vollbild mit Duplex, Waffe aus),
Sitz nach Konzept A wie Z1 (0.21): Rohrsattel auf dem Sattelblock hinter dem Augenpunkt, H0-Klemmfuß unter dem Objektiv; Ring ohne Wulst
(außen/innen 1,29); auf der Linse das gezeichnete Hüft-Absehen flach (wie 0.21). Visierhöhe 66 mm; mittig über dem Gehäuse (Nutzerhinweis 28.10.2026). Keine Variante (§ 6a).
Schlichtheitsbudget: Leuchten 1 Funktion (Absehen) · Grafik 1 Band · Schrift 1 · Orange 3 (Höhenturm, Klemmhebel des Visiers,
Magazinhalter) · Schrauben nur an Sattel und Schaft.
Bewegung: Kammerstängel links (schräg nach unten hinten; Nutzer 28.10.2026 „mit links wird doch quasi nachgeladen“) hebt 60°
(linke Seite nach oben), dann gleitet der Verschluss 66 mm zurück (Aktion `fire_cycle`,
`reload_empty`); die Kammerbahn ist oben links offen, damit der gehobene Stängel nicht durch das Gehäuse läuft.
Hülse: `rifle` aus dem Auswurffenster rechts (Flugrichtung wie Destiny nach rechts; Stängel und Bahn links).
Status: Maße entworfen (Länge an Toolgen 1,134 m angelehnt, Verhältnis H/L an Destiny 0,17–0,32; gemessene Werte im Spec),
Formprinzipien abgeleitet aus den Bildreferenzen.
"""
from basic.common import part, prof, box, cyl, cut_box, rail, rifle_mag, grip_v21, stock_s1, R_MID, R_SMALL
from basic.common import lang
from basic.weapons import w09_sniper_rifle as V1

META = dict(V1.META, variant='v2.1', name='Weitschuss v2.1', nick='Familie v2.1',
            summary='Repetier-Scharfschützengewehr mit langer Creme-Haube, freiem Lauf und Zielfernrohr Z3 (Stil v2.1).')
ASSEMBLIES = V1.ASSEMBLIES
GRIP_TOP = 40
BORE = 96
TOP = 120                          # Oberkante Haube hinten (Gehäuse), fällt nach vorn auf 110 ab
SH_F0 = 202                        # Fuge Gehäuse / Laufmantel
HOOD_F1 = 530                      # Stirn des Laufmantels
HG = (210, 500)                    # Vorderschaft
W_HOOD, W_LOW = 40, 38
# Visiersitz nach Konzept A (wie BASIC-03 v2.1): Visierlinie u 162 (Visierhöhe 66), Ringstirn f 130, Augenpunkt f 40 – das Visier sitzt mittig über dem Gehäuse (f −122 … 201; Nutzerhinweis 28.10.2026); Rohrsattel auf
# einer kurzen Schiene auf dem Sattelblock hinter dem Auge, vorn eine zweite kurze Schiene für den Klemmfuß unter dem Objektiv.
_cu = BORE + 66
F_OBJ = 130
SEAT = 147                         # Schienenoberkante hinten: unter der Okular-Unterkante (u 148,5)
HUMP = SEAT - 8
SEAT_F = (-74, -26)                # Schiene unter dem Sattel (Sattel f −68 … −28)
FOOT_F = (96, 134)                 # vordere Schiene unter dem Klemmfuß (f 100–130)
BOLT_F = (-50, 10)                 # Verschluss in Ruhelage (zurück bis f −116, nicht in den Schaft)
HANDLE_F = -40                     # Kammerstängel am Verschluss
KNOB = (HANDLE_F - 8, BORE - 14)   # Kammerknopf (f, u): schräg unten hinten, links unter der Kammerbahn auf Creme
BOLT_TRAVEL = 66
_scope, SIGHT_ANCHORS = lang(F_OBJ, TOP + 8, _cu, seat_u=SEAT)

P = []
# ---------------------------------------------------------------- Haube (Creme) mit Buckel, Längsschlitz und offener Kammerbahn
P += [
    prof('receiver', 'Gehäuse', 'Receiver', 'receiver', 'shell', 'Verschlussgehäuse; trägt Visier, Lauf und Laufmantel', 'Grundkörper',
         [(-122, 70), (SH_F0 - 1, 70), (SH_F0 - 1, TOP), (-116, TOP), (-122, TOP - 6)], W_HOOD, bevel=R_MID,
         cuts=[cut_box(-120, -28, 86, TOP + 2, 36, x=20),                           # Kammerbahn links, oben offen (x 2 … 38)
               cut_box(-60, -20, 90, 108, 24, x=-20)]),                            # Auswurffenster rechts (Verschluss sichtbar)
    prof('shroud', 'Laufmantel', 'Barrel shroud', 'barrel', 'shell', 'Umschließt den Lauf bis vor die Hälfte; Längsschlitz',
         'vorn am Gehäuse verschraubt, Fuge 1 mm, 4 mm schmaler (Stufe)',
         [(SH_F0, 72), (SH_F0 + 10, 80), (HOOD_F1 - 8, 80), (HOOD_F1, 88), (HOOD_F1, 104), (HOOD_F1 - 8, 110), (SH_F0, TOP - 2)], W_HOOD - 4,
         bevel=R_MID, cuts=[cut_box(250, 480, 92, 102, 60)]),                         # Längsschlitz quer durch (Lauf sichtbar)
    prof('saddle_block', 'Sattelblock', 'Saddle block', 'receiver', 'shell', 'Trägt die hintere Schiene hinter dem Augenpunkt (Konzept A)',
         'auf das Gehäuse gesetzt, schmaler als das Gehäuse (der gehobene Kammerknopf läuft links daran vorbei)',
         [(-74, TOP - 1), (-4, TOP - 1), (-18, HUMP), (-72, HUMP)], 26, bevel=R_SMALL),
    box('bolt', 'Verschluss', 'Bolt', 'mechanism', 'metal', 'Verriegelt die Patrone; gleitet nach dem Entriegeln zurück',
        'im Gehäuse geführt (gleitet)', *BOLT_F, BORE - 8, BORE + 8, 16, bevel=R_SMALL,
        move=dict(kind='translate', pivot=(-20, BORE, 0), vector_mm=(-BOLT_TRAVEL, 0, 0), event='bolt', expect=((-20, BORE, -8), (-1, 0, 0)))),
    part('bolt_handle', 'Kammerstängel', 'Bolt handle', 'mechanism', 'tube', 'dark_metal', 'Hebel zum Entriegeln (Stützhand); zeigt schräg '
         'nach unten hinten, hebt sich 60°', 'am Verschluss (dreht um die Laufachse)', bevel=0, parent_part='bolt', r=4.2,
         path=[(HANDLE_F, BORE - 2, 1.5), (HANDLE_F - 3, BORE - 4, 24), (KNOB[0], KNOB[1], 34)],
         move=dict(kind='rotate', pivot=(HANDLE_F, BORE, 0), axis='f', range_deg=(0, 60), event='bolt',
                   expect=((KNOB[0], KNOB[1], 40), (0, 1, 0)))),
    cyl('bolt_knob', 'Kammerknopf', 'Bolt knob', 'mechanism', 'graphite', 'Griffkugel des Kammerstängels (dunkel auf Creme)',
        'am Kammerstängel', 'x', KNOB, 32, 46, 7.5, segs=20, bevel=R_SMALL, parent_part='bolt_handle'),
    part('band_side', 'Chevronband', 'Chevron band', 'barrel', 'multi', 'accent', 'Lackiertes Band (einziges Grafikelement)',
         'lackiert', bevel=0, items=[dict(shape='prof', pts=[(492, 82), (500, 82), (508, 95), (500, 108), (492, 108), (500, 95)], w=0.3,
                                          x=sx * (W_HOOD / 2 - 2 + 0.15)) for sx in (1, -1)]),
    part('text_l', 'Schriftzug', 'Lettering', 'receiver', 'text', 'anodized', 'Kennung „BASIC SR-09“ (einzige Schrift)',
         'aufgedruckt (dunkel auf Creme)', bevel=0, text='BASIC  SR-09', size=4.6, f=120, u=76, x=W_HOOD / 2 + 0.05, side=1, depth=0.12),
]
P += [dict(p, mat='anodized', attach='auf dem Sattelblock hinter dem Augenpunkt (fest)') for p in rail(*SEAT_F, HUMP)]
P += [dict(p, id='rail_front', de='Schiene vorn', en='Front rail', mat='anodized', attach='auf dem Gehäuse unter dem Objektiv (fest)')
      for p in rail(*FOOT_F, TOP)]
P += _scope
# ---------------------------------------------------------------- Unteres Gehäuse und Vorderschaft (Graphit)
P += [
    prof('lower', 'Unteres Gehäuse', 'Lower receiver', 'receiver', 'graphite', 'Griffmodul und Magazinschacht',
         'unter dem Gehäuse, Fuge 1 mm', [(-112, 69), (HG[0] - 2, 69), (HG[0] - 2, 52), (150, 48), (136, 30), (130, 20), (92, 20), (88, 28),
                                        (82, GRIP_TOP), (-70, GRIP_TOP), (-112, 60)], W_LOW, bevel=R_MID),
    prof('mag_well', 'Schachtlippe', 'Magazine well lip', 'receiver', 'trim', 'Blanke Einführkante des Magazintrichters',
         'unten am Trichter', [(91, 17.5), (131, 17.5), (131.5, 21), (90.5, 21)], W_LOW + 1, bevel=0.6, iface='BMW-R'),
    prof('handguard', 'Vorderschaft', 'Fore-end', 'support', 'graphite', 'Griffbereich der Stützhand unter dem Laufmantel',
         'an Laufmantel und Unterem Gehäuse verschraubt, Fuge 1 mm', [(HG[0], 79), (HG[1], 79), (HG[1], 66), (HG[1] - 14, 54), (HG[0], 52)],
         W_HOOD - 6, bevel=R_MID),
    prof('handguard_grip', 'Griffpolster', 'Grip pad', 'support', 'rubber', 'Rutschfeste Zone für die Stützhand',
         'unten auf den Vorderschaft geklebt', [(270, 49.5), (400, 51.4), (400, 55), (270, 55)], 28, bevel=R_SMALL),
    cyl('mag_release', 'Magazinhalter', 'Magazine release', 'grip_controls', 'accent', 'Löst das Magazin', 'Druckknopf links',
        'x', (84, 56), W_LOW / 2 - 0.5, W_LOW / 2 + 3, 4.2, segs=20,
        move=dict(kind='translate', pivot=(84, 56, W_LOW / 2), vector_mm=(0, 0, -2.5), event='reload',
                  expect=((84, 56, W_LOW / 2 + 3), (0, 0, -1)))),
]
# ---------------------------------------------------------------- Lauf (frei, kanneliert), Mündungsbremse
P += [
    cyl('barrel', 'Lauf', 'Barrel', 'barrel', 'metal', 'Schwerer Lauf; vor der Haube frei und kanneliert', 'in der Haube verschraubt',
        'f', (BORE, 0), 200, 760, 9.0, segs=24, cuts=[cut_box(560, 720, BORE - 1.5, BORE + 1.5, 4, x=sx * 9.0) for sx in (1, -1)]),
    cyl('muzzle', 'Mündungsbremse', 'Muzzle brake', 'barrel', 'anodized', 'Dreifach geschlitzte Bremse; Socket_Muzzle vorn',
        'auf das Laufende geschraubt (lösbar)', 'f', (BORE, 0), 744, 804, 16, r_in=6, segs=8, bevel=R_SMALL, iface='BMZ-15',
        cuts=[cut_box(756 + 13 * i, 764 + 13 * i, BORE - 7, BORE + 7, 40) for i in range(3)]),
    cyl('muzzle_crown', 'Mündungskrone', 'Muzzle crown', 'barrel', 'trim', 'Blanke Stirnkante', 'vorn an der Bremse',
        'f', (BORE, 0), 802, 807, 15, r_in=6.5, segs=8, bevel=0.6),
]
# ---------------------------------------------------------------- Griff, Magazin, Schaft S1 mit hoher Wange und Durchbruch
P += grip_v21(top=GRIP_TOP)
for p in rifle_mag(93, 24, depth=37, length=60, tilt=0, w=24, curve=0):
    if p['id'] == 'magazine':
        p['func'] = 'Kastenmagazin (5); entnehmbar'
    if p['id'] == 'magazine_base':
        p['mat'] = 'anodized'
    if p['id'] == 'magazine_round':
        p['mat'] = 'brass'
    P.append(p)
_f0, _s, _ua = -122, 1.15, BORE


def _L(d):
    return _f0 - d * _s


for p in stock_s1(_f0, _ua, s=_s):
    if p['id'] == 'stock':
        p['cuts'] = [dict(shape='prof', pts=[(_L(100), _ua + 8), (_L(148), _ua + 10), (_L(150), _ua - 58), (_L(110), _ua - 26)], w=50)]
        p['func'] = 'Anlage an der Schulter; Durchbruch'
    if p['id'] == 'cheek_rest':     # hohe Wange für das Zielfernrohr (Visierlinie 66 mm über dem Lauf)
        p.update(mat='rubber', u1=_ua + 40, func='Hohe Anlage für die Wange (Zielfernrohr)', bevel=R_SMALL)
    P.append(p)
PARTS = P
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip', note='Haupthand, auf der Griffachse'),
    'Socket_SupportHand': dict(at=(340, 52, 0), part='handguard', note='Unterseite des Vorderschafts'),
    'Socket_Muzzle': dict(at=(807, BORE, 0), part='muzzle_crown', note='Stirn der Mündungskrone auf der Laufachse'),
    'Socket_MagWell': dict(at=(111.5, 20, 0), part='mag_well', note='Einrastpunkt Magazin (Schnittstelle BMW-R)'),
    'Socket_Bolt': dict(at=(KNOB[0], KNOB[1], 40), part='bolt_knob', note='Griffpunkt Kammerknopf links (Stützhand repetiert; Nutzer 28.10.2026)'),
}
ANCHORS.update(SIGHT_ANCHORS)
EJECT = dict(at=(-40, BORE + 2, -W_HOOD / 2), dir=(0.15, 0.6, -1.0), case='rifle',
             src='E: Auswurffenster rechts beim Zurückziehen des Verschlusses (Stängel links), Hülse nach rechts, etwas hoch und vorn '
                 '(wie Destiny, Motiongen muendung › 6)')
# Ego-Griffe (0.33 „Armory“ P2, basic/arms/ego.profile): Autorenmaß dieser Waffe wie ego.GRIPS der Pilotwaffe. 'charge' am Kammerknopf
# links (folgt Stängel und Verschluss): die Stützhand repetiert nach jedem Schuss (ego.CLASSES sniper_rifle › fire_cycle)
EGO_GRIPS = {
    'grip':    dict(contact=(-3, -6, -16.5), palm=(0.15, 0.0, 1.0), fingers=(1.0, -0.06, 0.0), fingers_pose='trigger',
                    src='E wie die Pilotwaffe (Griff BGM-1 v2.1, gleiche Lage zu Socket_Hand)'),
    'support': dict(contact=(330, 50.4, -2), palm=(0.0, 1.0, -0.25), fingers=(0.08, 0.15, -1.0), fingers_pose='underhand',
                    src='E unter dem Vorderschaft auf dem Griffpolster (handguard_grip f 270–400, Unterkante u 49,5–51,4), Lage wie die '
                        'Pilotwaffe (Toolgen: underhand)'),
    'mag':     dict(part='magazine', contact=(100, -10, 12.5), palm=(0.0, 0.0, -1.0), fingers=(1.0, 0.2, 0.0), fingers_pose='mag_hold',
                    src='E links am Kastenmagazin (Breite 24, f 93–130), Hand greift von unten hinten (wie die Pilotwaffe)'),
    'charge':  dict(part='bolt_knob', contact=(KNOB[0], KNOB[1], 47), palm=(0.0, 0.0, -1.0), fingers=(0.45, 0.9, 0.0),
                    fingers_pose='pinch', src='E am Kammerknopf links (Socket_Bolt), die Stützhand hebt, zieht und schiebt den Stängel'),
}
EGO_LIVE = dict(trigger='trigger', bolt='', port='')     # nur der Abzug je Schuss; Verschluss und Stängel bewegt fire_cycle
ACTIONS = {k: dict(A, view=(0.85, -0.2, 0.5)) for k, A in V1.ACTIONS.items()}     # von links: Stängel links (stilhandbuch § 9)
EXPLODE = {'sight': (0, 130, 0), 'ammo': (30, -140, 0), 'stock': (-120, 0, 0), 'barrel': (200, 0, 0), 'support': (60, -60, 0),
           'grip_controls': (-10, -80, 0), 'mechanism': (0, 0, -90), 'receiver': (0, 0, 0)}
