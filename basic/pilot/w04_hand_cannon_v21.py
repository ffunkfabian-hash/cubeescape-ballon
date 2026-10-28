"""BASIC-04 v2.1 – Handfeuerwaffe im Stil v2.1 („Destiny-Detaildichte + AAA-Material, schlicht“), Familie des Piloten BASIC-01 v2.1.

Recherche (docs/quellen.md › Q-D2-IMG, gesichtet 28.10.2026, Bungie-Manifest): Fatebringer (lange flache Oberkante über Lauf und
Trommel, Kastenlauf mit Schlitzfenstern, Kastenunterlauf), Austringer (rechteckiger Hauptblock, dunkler Rahmen, heller Lauf),
Igneous Hammer (heller Deckel über dunklem Rahmen). Nur Prinzipien; Leitmerkmal 04 nach Designvertrag: Trommel auf Kran, Unterlauf.

Formsprache-Checkliste (stilhandbuch §3):
| Frage | Handfeuerwaffe v2.1 |
|---|---|
| Leitmerkmal der Silhouette | lange gerade Oberkante von der Kimme bis zur Mündung über einer großen, freistehenden Trommel; Kastenunterlauf mit Keilstirn |
| Schichten | Rahmen (Graphit) → Creme-Haube aus Oberbrücke, Laufmantel und Unterlauf (4 mm schmaler, Stufe zum Rahmen) |
| Negativraum | Trommelfenster im Rahmen (Trommel frei mit Spalten); Laufmantel mit Fenster quer durch, der Lauf ist sichtbar |
| Blickfang | die kannelierte dunkle Trommel im Creme-Graphit-Körper (Kontrast, keine Leuchte) |
| Zweiton-Blockung | Haube Lack (`shell`), Rahmen Polymer (`graphite`), Griff `rubber`, Trommel und Kran `dark_metal` |
| Grafik | ein Chevronband vorn am Unterlauf, ein Schriftzug „BASIC HC-04“ (dunkel auf Creme) |
| Front | Keilstirn des Unterlaufs, Mündungsmulde in der Mantelstirn, blanke Krone |
| Übergänge | Oberbrücke, Laufmantel und Unterlauf sind ein Profil; Rahmenunterkante läuft gerade über den ganzen Abzugsbügel |
| Ergonomie | Griff BGM-1 in v2.1-Form (Familie), Hahnsporn unter der Visierlinie, Trommelriegel unter dem Daumen links |

Visier: K1 „Klammer“ (Baukasten v3, visier-konzept › 6a; Kimme/Korn nach Visier-Standard 3, Linie Oberbrücke + 11 mm):
Leuchtklammern bündig im Kimmenblatt, Kornpunkt. M1 „Mini“ bleibt Variante (nur dokumentiert, nicht gebaut).
Schlichtheitsbudget: Leuchten 1 Funktion (Visier: Klammern und Kornpunkt) · Grafik 1 Band · Schrift 1 · Orange 2 (Trommelriegel,
Klemmhebel des Visiers) · Schrauben keine.
Hülsen: Trommel – kein Auswurf beim Schuss (`EJECT = None`); die leeren Hülsen fallen beim Nachladen (Aktion `reload`, Marke `eject`).
Status: Maße entworfen (Länge an v1 0,32 m angelehnt, Verhältnis H/L an Destiny 0,52–0,61; gemessene Werte im Spec),
Formprinzipien abgeleitet aus den Bildreferenzen.
"""
import math

from basic.common import part, prof, box, cyl, cut_box, grip_v21, R_BODY, R_MID, R_SMALL, R_FINE
from basic.pilot.optics.sight_kit import klammer
from basic.weapons import w04_hand_cannon as V1

META = dict(V1.META, variant='v2.1', name='Trommel v2.1', nick='Familie v2.1',
            summary='Revolver mit freistehender, kannelierter Trommel auf Kran, Kastenunterlauf und Kimme/Korn K1 (Stil v2.1).')
ASSEMBLIES = V1.ASSEMBLIES
T15 = math.tan(math.radians(15))
GRIP_TOP = 24                      # Griffoberkante = Rahmenunterkante (Runde 1: 28 ließ unter der Trommel nur 5 mm, die Fase
#                                    schloss die Seitenfläche dort zu einem Strich – Schattierfehler)
BORE = 71                          # Laufachse = oberste Kammer
CYL_U, CYL_R, CYL_F = 57, 22.5, (19.5, 78.5)    # Trommelachse, Radius, Länge (Kammerkreis 14 mm)
STRAP = 81                         # Unterkante Oberbrücke (1,5 mm über der Trommel)
DECK = 92                          # Oberkante Haube = Träger des Visiers (Kimme-Linie DECK + 11)
FRONT = 264                        # Stirn des Laufmantels
FR_W, SH_W = 34, 26                # Rahmenbreite, Haubenbreite
WIN_U = CYL_U - CYL_R - 1.5      # Unterkante Trommelfenster
PIVOT = (CYL_U - 26, 14)           # Kranachse (u, x): unten links im Rahmen, 29,5 mm von der Trommelachse

P = []
# ---------------------------------------------------------------- Rahmen (Graphit) mit Trommelfenster, Hahn, Riegel
P += [
    prof('frame', 'Rahmen', 'Frame', 'receiver', 'graphite', 'Trägt Trommel, Hahn, Abzug und Griff; Trommelfenster',
         'Grundkörper', [(-13, GRIP_TOP), (100, GRIP_TOP), (104, GRIP_TOP + 4), (104, 58), (CYL_F[1] + 3, 58), (CYL_F[1] + 3, WIN_U),
                         (CYL_F[0] - 1, WIN_U), (CYL_F[0] - 1, STRAP), (-8, STRAP), (-8, 85), (-19, 85), (-25, 82), (-28.5, 76), (-29, 64), (-25, 48)],
         FR_W, bevel=R_MID, cuts=[cut_box(-34, -8, 64, 90, 9)]),     # Trommelfenster im Profil; Hahngehäuse hinten rund (Nutzerwahl a); Hahnschlitz
    prof('hammer', 'Hahn', 'Hammer', 'mechanism', 'anodized', 'Wird gespannt und schlägt beim Schuss vor; Sporn unter der Visierlinie',
         'Drehpunkt hinten im Rahmen', [(-24, 62), (-14, 62), (-12, 82), (-18, 90), (-30, 94), (-33, 91), (-25, 83)], 7, bevel=R_FINE,
         move=dict(kind='rotate', pivot=(-19, 66, 0), axis='x', range_deg=(0, 28), event='cock', expect=((-31, 93, 0), (-1, 0, 0)))),
    cyl('cylinder_latch', 'Trommelriegel', 'Cylinder latch', 'grip_controls', 'accent', 'Gibt den Kran frei (Daumen)',
        'links am Rahmen hinter der Trommel, gleitet nach vorn', 'x', (4, 62), FR_W / 2 - 0.5, FR_W / 2 + 3, 4.5, segs=20,
        move=dict(kind='translate', pivot=(4, 62, FR_W / 2), vector_mm=(6, 0, 0), event='reload', expect=((4, 62, FR_W / 2), (1, 0, 0)))),
]
# ---------------------------------------------------------------- Kran und Trommel (schwenkt nach links unten aus)
_flutes = [dict(shape='cyl', axis='f', c=(CYL_U + 24.5 * math.cos(math.radians(a)), 24.5 * math.sin(math.radians(a))),
                a0=CYL_F[0] + 9, a1=CYL_F[1] - 6, r=5.2, segs=16) for a in range(30, 360, 60)]
_chambers = [dict(shape='cyl', axis='f', c=(CYL_U + 14 * math.cos(math.radians(a)), 14 * math.sin(math.radians(a))),
                  a0=CYL_F[1] - 4, a1=CYL_F[1] + 1, r=4.4, segs=16) for a in range(0, 360, 60)]
P += [
    part('crane', 'Kran', 'Crane', 'mechanism', 'multi', 'dark_metal', 'Trägt die Trommel; schwenkt nach links unten aus',
         'Achse unten links im Rahmen', bevel=R_FINE,
         move=dict(kind='rotate', pivot=(50, PIVOT[0], PIVOT[1]), axis='f', range_deg=(0, -90), event='reload',
                   note='Trommel schwenkt vollständig links neben den Rahmen', expect=((50, CYL_U, 0), (0, 0, 1))),
         items=[dict(shape='cyl', axis='f', c=PIVOT, a0=CYL_F[0], a1=CYL_F[1] + 2.5, r=3.2, segs=12),
                dict(shape='xprof', f0=CYL_F[1], f1=CYL_F[1] + 2.5, cu=CYL_U,
                     pts=[(-4.5, 3), (4.5, 3), (PIVOT[1] + 4, PIVOT[0] - CYL_U + 2), (PIVOT[1] - 3, PIVOT[0] - CYL_U - 3)])]),
    cyl('cylinder', 'Trommel', 'Cylinder', 'ammo', 'dark_metal', 'Sechs Kammern, kanneliert; dreht je Schuss um 60°',
        'auf dem Kran gelagert', 'f', (CYL_U, 0), CYL_F[0], CYL_F[1], CYL_R, bevel=R_SMALL, segs=36, parent_part='crane', iface=None,
        cuts=_flutes + _chambers, move=dict(kind='rotate', pivot=(50, CYL_U, 0), axis='f', range_deg=(0, -60), event='fire',
                                           note='oben nach links (von hinten gesehen gegen den Uhrzeigersinn)',
                                           expect=((50, BORE, 0), (0, 0, 1)))),
]
# ---------------------------------------------------------------- Haube (Creme): Oberbrücke, Laufmantel, Unterlauf
_recess = dict(shape='cyl', axis='f', c=(BORE, 0), a0=FRONT - 10, a1=FRONT + 2, r=12, segs=32)
P += [
    prof('shroud', 'Haube', 'Top strap and barrel shroud', 'receiver', 'shell',
         'Oberbrücke über der Trommel, Laufmantel und Unterlauf als ein Profil; trägt Kimme und Korn',
         'auf den Rahmen gesetzt, 4 mm schmaler (Stufe)', [(-8, STRAP), (81.5, STRAP), (81.5, 58), (104, 58), (104, 42), (244, 42),
                                                            (FRONT, 56), (FRONT, 88), (FRONT - 4, DECK), (-4, DECK), (-8, 88)],
         SH_W, bevel=R_MID,
         cuts=[_recess, cut_box(132, 214, 66, 78, 60)]),                        # Mündungsmulde; Fenster quer durch (Lauf sichtbar)
    cyl('barrel', 'Lauf', 'Barrel', 'barrel', 'metal', 'Führt das Geschoss; im Fenster sichtbar', 'in den Rahmen geschraubt',
        'f', (BORE, 0), 80, FRONT - 4, 9.5, segs=24),
    cyl('muzzle_crown', 'Mündungskrone', 'Muzzle crown', 'barrel', 'trim', 'Blanke Stirnkante in der Mündungsmulde', 'Laufende',
        'f', (BORE, 0), FRONT - 7, FRONT - 3, 10.5, r_in=5, segs=24, bevel=0.6),
    part('band_side', 'Chevronband', 'Chevron band', 'receiver', 'multi', 'accent', 'Lackiertes Band (einziges Grafikelement)',
         'lackiert', bevel=0, items=[dict(shape='prof', pts=[(222, 43), (230, 43), (238, 50), (230, 57), (222, 57), (230, 50)],
                                          w=0.3, x=sx * (SH_W / 2 + 0.15)) for sx in (1, -1)]),
    part('text_l', 'Schriftzug', 'Lettering', 'receiver', 'text', 'anodized', 'Kennung „BASIC HC-04“ (einzige Schrift)',
         'aufgedruckt (dunkel auf Creme)', bevel=0, text='BASIC  HC-04', size=4.2, f=172, u=47, x=SH_W / 2 + 0.05, side=1, depth=0.12),
]
# ---------------------------------------------------------------- Griff, Abzug, Bügel (BGM-1 v2.1)
P += grip_v21(top=GRIP_TOP)
# ---------------------------------------------------------------- Visier K1 „Klammer“ (Kimme hinten auf der Oberbrücke, Korn vorn)
_sight, SIGHT_ANCHORS = klammer(0, 248, DECK)
P += _sight
PARTS = P
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip', note='Haupthand, auf der Griffachse'),
    'Socket_SupportHand': dict(at=(-4, -34, 17), part='grip', note='Stützhand umfasst die Griffhand von links (Pistolengriff beidhändig)'),
    'Socket_Muzzle': dict(at=(FRONT - 3, BORE, 0), part='muzzle_crown', note='Stirn der Mündungskrone auf der Laufachse'),
    'Socket_MagWell': dict(at=(CYL_F[1], CYL_U, 0), part='cylinder', note='Ladestelle: Trommelstirn (ausgeschwenkt beim Nachladen)'),
}
ANCHORS.update(SIGHT_ANCHORS)
EJECT = None    # Trommel: keine Hülse beim Schuss (Daten statt Sonderlogik); die Hülsen fallen beim Nachladen (reload › eject)
ACTIONS = {k: dict(A) for k, A in V1.ACTIONS.items()}
EXPLODE = {'sight': (0, 90, 0), 'ammo': (0, 0, 80), 'barrel': (110, 0, 0), 'grip_controls': (-10, -80, 0), 'mechanism': (0, 0, 60),
           'receiver': (0, 0, 0)}
