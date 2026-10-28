"""BASIC-05 v2.1 – Seitenwaffe im Stil v2.1 („Destiny-Detaildichte + AAA-Material, schlicht“), Familie des Piloten BASIC-01 v2.1.

Recherche (docs/quellen.md › Q-D2-IMG, gesichtet 28.10.2026, Bungie-Manifest): Minimum Distance (klassischer Schlitten mit
Auswurffenster, Farbzonen auf dem Schlitten, dunkler Rahmen mit Schiene, Führungsstange vorn sichtbar), Drang (flacher kantiger
Schlitten auf kurzem Kastenrahmen, Kimme am Schlittenende), Brass Attacks (Zweiton Schlitten/Rahmen). Nur Prinzipien;
Leitmerkmal 05 nach Designvertrag: Schlitten.

Formsprache-Checkliste (stilhandbuch §3):
| Frage | Seitenwaffe v2.1 |
|---|---|
| Leitmerkmal der Silhouette | hoher Creme-Schlitten als ein Block über kurzem Graphitrahmen, vorn 26 mm frei überstehend; Magazinboden bündig unter dem Griffboden |
| Schichten | Rahmen (Graphit) → Schlitten (Creme, 2 mm breiter, Fuge 1 mm) → dunkle Schlittenkappe hinten mit Spitze nach vorn |
| Negativraum | Auswurffenster rechts mit sichtbarem Verriegelungsblock; Schlitz oben im Schlittenkopf über dem Lauf |
| Blickfang | Munitionsanzeige links im Rahmen (Ego-Seite, eine Leuchtfunktion) |
| Zweiton-Blockung | Schlitten Lack (`shell`), Rahmen und Schlittenkappe Polymer (`graphite`), Griff `rubber`, Bügel und Magazinboden `anodized` |
| Grafik | ein Chevronband vorn am Schlitten, ein Schriftzug „BASIC SA-05“ (hell auf Graphit) |
| Front | Schlittenstirn mit Mündungsmulde und blanker Krone, darunter Führungsstange; Staubschutz des Rahmens zurückgesetzt |
| Übergänge | Rahmen geht hinten in einen Handballenschutz über; Rahmenunterkante läuft gerade über den ganzen Abzugsbügel |
| Ergonomie | Griff BGM-1 in v2.1-Form (Familie), Magazin auf der Griffachse (Mitte f = u·tan 15°), Bedienelemente links unter dem Daumen |

Visier: K1 „Klammer“ (Baukasten v3, visier-konzept › 6a; Kimme/Korn nach Visier-Standard 3, Linie Schlittenoberkante + 11 mm),
Kimme und Korn folgen dem Schlitten. Varianten H8 „Halbmond“ und M1 „Mini“ nur dokumentiert, nicht gebaut.
Schlichtheitsbudget: Leuchten 2 Funktionen (Munitionsanzeige; Visier: Klammern und Kornpunkt) · Grafik 1 Band · Schrift 1 ·
Orange 3 (Schlittenfang, Magazinhalter, Klemmhebel des Visiers) · Schrauben keine.
Status: Maße entworfen (Länge an Toolgen 0,243 m angelehnt, Verhältnis H/L an Destiny 0,74–0,83; gemessene Werte im Spec),
Formprinzipien abgeleitet aus den Bildreferenzen.
"""
import math

from basic.common import part, prof, box, cyl, cut_box, grip_v21, R_BODY, R_MID, R_SMALL, R_FINE
from basic.pilot.optics.sight_kit import klammer
from basic.weapons import w05_sidearm as V1

META = dict(V1.META, variant='v2.1', name='Seitenwaffe v2.1', nick='Familie v2.1',
            summary='Kompakte Schlittenpistole mit hohem Creme-Schlitten, Magazin im Griff und Kimme/Korn K1 (Stil v2.1).')
ASSEMBLIES = V1.ASSEMBLIES
T15 = math.tan(math.radians(15))
GRIP_TOP = 34                      # Griffoberkante = Rahmenunterkante
BORE = 74                          # Laufachse
SL_U, DECK = 54, 92                # Schlitten unten / oben (Träger des Visiers, Kimme-Linie DECK + 11)
SL_F = (-22, 196)                  # Schlitten hinten / Stirn
FR_W, SL_W = 26, 28                # Rahmenbreite, Schlittenbreite
ROD_U = 59.5                       # Führungsstange

P = []
# ---------------------------------------------------------------- Rahmen (Graphit), Bedienelemente, Munitionsanzeige
P += [
    prof('frame', 'Rahmen', 'Frame', 'receiver', 'graphite', 'Trägt Schlitten, Abzug, Griff und Magazinschacht',
         'Grundkörper', [(-14, GRIP_TOP), (86, GRIP_TOP), (94, 40), (166, 40), (170, 44), (170, SL_U - 1), (-24, SL_U - 1),
                         (-31, 49), (-28, 44)], FR_W, bevel=R_MID),
    box('slide_stop', 'Schlittenfang', 'Slide stop', 'grip_controls', 'accent', 'Hält den Schlitten nach dem letzten Schuss offen',
        'links am Rahmen (dreht)', 40, 64, 47, 52.5, 2.4, bevel=R_FINE, x=FR_W / 2 + 0.6),
    cyl('mag_release', 'Magazinhalter', 'Magazine release', 'grip_controls', 'accent', 'Löst das Magazin im Griff',
        'Druckknopf links am Griff', 'x', (22, 28), 14.5, 17.5, 4.2, segs=20,
        move=dict(kind='translate', pivot=(22, 28, 16), vector_mm=(0, 0, -2.5), event='reload', expect=((22, 28, 17.5), (0, 0, -1)))),
    box('counter_bezel', 'Anzeigenrahmen', 'Counter bezel', 'receiver', 'anodized', 'Fasst die Munitionsanzeige',
        'in den Staubschutz eingelassen', 100, 136, 41, 50, 2.4, bevel=0.6, x=FR_W / 2 + 0.6),
    box('ammo_counter', 'Munitionsanzeige', 'Ammo counter', 'receiver', 'energy', 'Füllstand; Blickfang links',
        'im Anzeigenrahmen', 104, 132, 42.5, 48.5, 1.0, bevel=0.2, x=FR_W / 2 + 1.6),
    part('text_l', 'Schriftzug', 'Lettering', 'receiver', 'text', 'decal', 'Kennung „BASIC SA-05“ (einzige Schrift)',
         'aufgedruckt (hell auf Graphit)', bevel=0, text='BASIC  SA-05', size=3.6, f=44, u=37.5, x=FR_W / 2 + 0.05, side=1, depth=0.12),
]
# ---------------------------------------------------------------- Schlitten (Creme), Lauf, Verriegelungsblock, Führungsstange
P += [
    prof('slide', 'Schlitten', 'Slide', 'mechanism', 'shell', 'Verschluss; läuft beim Schuss zurück; trägt Kimme und Korn',
         'auf den Rahmenschienen (gleitet), Fuge 1 mm', [(SL_F[0], SL_U), (SL_F[1] - 6, SL_U), (SL_F[1], SL_U + 6), (SL_F[1], DECK - 4),
                                                         (SL_F[1] - 4, DECK), (SL_F[0] + 4, DECK), (SL_F[0], DECK - 4)], SL_W, bevel=R_MID,
         cuts=[cut_box(52, 94, 72, DECK + 2, 16, x=-SL_W / 2),     # Auswurffenster rechts, oben offen, 8 mm tief bis über den Block (Richter)
               cut_box(140, 180, 82, DECK + 2, 12),                                    # Schlitz im Schlittenkopf über dem Lauf
               dict(shape='cyl', axis='f', c=(BORE, 0), a0=SL_F[1] - 8, a1=SL_F[1] + 2, r=8.5, segs=32),      # Mündungsmulde
               dict(shape='cyl', axis='f', c=(ROD_U, 0), a0=SL_F[1] - 6, a1=SL_F[1] + 2, r=3.6, segs=16)],    # Stangenloch
         move=dict(kind='translate', pivot=(60, BORE, 0), vector_mm=(-32, 0, 0), event='fire', expect=((60, DECK, 0), (-1, 0, 0)))),
    prof('slide_cap', 'Schlittenkappe', 'Slide rear cap', 'mechanism', 'graphite',     # anodized zeigte Kratz-Sprenkel (Sichtung Runde 3)
         'Dunkle Griffzone hinten am Schlitten (zweite Schicht; Nutzerwahl a, 28.10.2026, statt leerer Griffmulde)',
         'hinten auf den Schlitten gesetzt (0,6 mm), folgt dem Schlitten',
         [(SL_F[0] - 1, SL_U + 3), (8, SL_U + 3), (14, (SL_U + DECK) / 2), (8, DECK - 3), (SL_F[0] - 1, DECK - 3)], SL_W + 1.2,
         bevel=R_SMALL, parent_part='slide'),
    box('barrel_hood', 'Verriegelungsblock', 'Barrel hood', 'barrel', 'metal', 'Verriegelt den Lauf im Schlitten; im Auswurffenster sichtbar',
        'am Lauf (fest)', 50, 96, 66, 81, 16, bevel=R_SMALL),
    cyl('barrel', 'Lauf', 'Barrel', 'barrel', 'metal', 'Führt das Geschoss', 'im Rahmen gelagert',
        'f', (BORE, 0), 94, SL_F[1] - 3, 6.5, segs=24),
    cyl('muzzle_crown', 'Mündungskrone', 'Muzzle crown', 'barrel', 'trim', 'Blanke Stirnkante in der Mündungsmulde', 'Laufende',
        'f', (BORE, 0), SL_F[1] - 7, SL_F[1] - 3, 7.2, r_in=3.6, segs=24, bevel=0.5),
    cyl('guide_rod', 'Führungsstange', 'Guide rod', 'barrel', 'metal', 'Führt die Schließfeder; vorn in der Schlittenstirn sichtbar',
        'im Rahmen (fest)', 'f', (ROD_U, 0), 100, SL_F[1] - 3, 3.0, segs=16),
    part('band_side', 'Chevronband', 'Chevron band', 'mechanism', 'multi', 'accent', 'Lackiertes Band (einziges Grafikelement)',
         'lackiert', bevel=0, parent_part='slide',
         items=[dict(shape='prof', pts=[(160, 60), (167, 60), (174, 73), (167, 86), (160, 86), (167, 73)], w=0.3, x=sx * (SL_W / 2 + 0.15))
                for sx in (1, -1)]),
]
# ---------------------------------------------------------------- Griff, Abzug, Bügel (BGM-1 v2.1), Magazin auf der Griffachse
P += grip_v21(top=GRIP_TOP)


def _A(u, d):                       # Punkt auf der Griffachse (15° nach hinten geneigt) in Höhe u, um d nach vorn versetzt
    return (u * T15 + d, u)


_down = (round(-140 * math.sin(math.radians(15)), 1), round(-140 * math.cos(math.radians(15)), 1), 0)
P += [
    prof('magazine', 'Magazin im Griff', 'Magazine', 'ammo', 'dark_metal', 'Hält die Patronen; steckt im Griff, entnehmbar',
         'rastet im Griff ein (lösbar, Magazinhalter)', [_A(50, -13), _A(50, 13), _A(-79, 13), _A(-79, -13)], 20, bevel=R_MID,
         move=dict(kind='translate', pivot=(*_A(-20, 0), 0), vector_mm=_down, event='reload',
                   note='Entnahme entlang der Griffachse nach unten', removable=True, expect=((*_A(-79, 0), 0), (-0.26, -0.97, 0)))),
    prof('magazine_base', 'Magazinboden', 'Magazine base plate', 'ammo', 'anodized', 'Greifkante; schließt den Griff unten ab',
         'am Magazin (fest); bündig mit dem Griffboden (Nutzerwahl a)', [_A(-79, -21), _A(-79, 22), _A(-85, 21), _A(-85, -20)], 32,
         bevel=R_SMALL, parent_part='magazine'),
]
# ---------------------------------------------------------------- Visier K1 „Klammer“ (folgt dem Schlitten)
_sight, SIGHT_ANCHORS = klammer(-12, 184, DECK, parent='slide')
P += _sight
PARTS = P
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip', note='Haupthand, auf der Griffachse'),
    'Socket_SupportHand': dict(at=(-4, -34, 17), part='grip', note='Stützhand umfasst die Griffhand von links (Pistolengriff beidhändig)'),
    'Socket_Muzzle': dict(at=(SL_F[1] - 3, BORE, 0), part='muzzle_crown', note='Stirn der Mündungskrone auf der Laufachse'),
    'Socket_MagWell': dict(at=(round(GRIP_TOP * T15, 1), GRIP_TOP, 0), part='grip', note='Magazinschacht im Griff'),
}
ANCHORS.update(SIGHT_ANCHORS)
# Hülsenauswurf (wie BASIC-06): Mitte des Auswurffensters rechts im Schlitten, Kurzpatrone, nach rechts, etwas hoch und vorn
EJECT = dict(at=(73, 80, -12), dir=(0.2, 0.5, -1.0), case='pistol',
             src='E: Auswurffenster rechts im Schlitten, Hülse nach rechts, etwas hoch und vorn (wie BASIC-06)')
ACTIONS = {k: dict(A) for k, A in V1.ACTIONS.items()}
EXPLODE = {'sight': (0, 90, 0), 'ammo': (0, -140, 0), 'barrel': (0, 0, -70), 'grip_controls': (-10, -80, 0), 'mechanism': (0, 60, 0),
           'receiver': (0, 0, 0)}
