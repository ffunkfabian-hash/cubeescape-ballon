"""BASIC-07 v2.1 – Kampfbogen im Stil v2.1 („Destiny-Detaildichte + AAA-Material, schlicht“), Familie des Piloten BASIC-01 v2.1.

Recherche (docs/quellen.md › Q-D2-IMG, gesichtet 28.10.2026, Bungie-Manifest): Hush und Biting Winds (Compound: Dreiteilung Wurfarm /
Mittelstück / Wurfarm, die Arme laufen in einem Bogen nach hinten zur Sehne, je eine Rolle an der Spitze, Mittelstück mit Fenster und
seitlichem Visierbügel, viel Negativraum zwischen Sehne und Bogen; Hush hell gegen dunkel), Arsenic Bite-4b und Imperial Needle
(Recurve: schlanke Arme, seitliche Schiene, gewickelter Griff). Nur Prinzipien; Zierknöpfe, Flügel, Ornamente und Leuchtspitzen nicht.

Der Bogen weicht von der Familie ab (Bogen-Regel, docs/familienmasse.md): **Griffstück statt Griff BGM-1** – die Hand umschließt den
Bogengriff, darüber die Pfeilauflage; Socket_Hand liegt wie bei allen Waffen in der Griffachse, die Schussachse ist der Pfeil
(ARROW_U über der Hand). Kein Lauf, kein Magazin, kein Auswurf (`EJECT = None`, Daten). Statt Stützhand die Zughand am Nockpunkt.
Der Bogen steht senkrecht; L × H im Spec sind Pfeilrichtung × Spanne.

Formsprache-Checkliste (stilhandbuch §3):
| Frage | Kampfbogen v2.1 |
|---|---|
| Leitmerkmal der Silhouette | Compound-Sichel: gerades Creme-Mittelstück, die dunklen Wurfarme schwingen in einem Bogen nach hinten zu großen Rollen; die Sehne schließt die Sichel zu einem D |
| Schichten | Mittelstück (Creme, Durchbruch unten) → Griffstück (Gummi) → Wurfarmaufnahmen (eloxiert) → Wurfarme (Graphit, gespalten) → Rollen; Visierträger mit Schiene → Visier B1 |
| Negativraum | Raum zwischen Sehne und Bogen; Sichtfenster im Mittelstück (gekröpfter Fensterbogen links, Pfeil und Blick frei); gespaltene Wurfarmspitzen; Rollen mit drei Durchbrüchen |
| Blickfang | Spannlicht: Leuchtlinse auf der Rückseite des Fensterbogens zum Auge, leuchtet bei vollem Auszug (Bogen bereit) |
| Zweiton-Blockung | Mittelstück Lack (`shell`), Wurfarme Polymer (`graphite`), Griff Gummi (`rubber`), Rollen `dark_metal` |
| Grafik | ein Schrägband am oberen Mittelstück, ein Schriftzug „BASIC BW-07“ (dunkel auf Creme, links unter dem Griff) |
| Front | Pfeilspitze zweistufig: blanke Hülse, dunkle Schneide; die Auflage führt den Pfeil im Fenster |
| Übergänge | Fensterbogen als Kröpfung aus einem Stück mit dem Mittelstück; Wurfarme stecken in den Aufnahmen (Fuge), Rollen zwischen den Zinken der gespaltenen Arme |
| Ergonomie | Griffstück mit Handballenwölbung, Pfeilauflage direkt über der Hand, Zughand am Nockpunkt |

Visier: B1 „Pins“ (Baukasten v3, visier-konzept › 6a; `sight_kit.pins`): drei Leuchtpins von der Pinschiene rechts sind das Absehen,
Ring Ø 52 auf einer kurzen H0-Plattform; die Plattform klemmt auf einer Schiene BRI-22 am Visierträger **links neben** dem
Fensterbogen (Seitenvisier, Ringmitte 58 mm links und 31,5 mm über dem Pfeil; Nutzer 28.10.2026: „das visier muss nach links,
nicht nach rechts“ – Wahl „ganz zur linken Seite“). Augenpunkt am Ankerpunkt bei vollem Auszug (20 mm hinter dem Nockpunkt), in
Linie mit dem Ring; Visierhöhe als Abstand zum Pfeil 66 mm (Familie; seitliche Visiere nur links, Regel aus 0.28). Im Zielbild
steht der Fensterbogen damit rechts neben dem Ring wie der Riser bei Destiny („Riser knapp rechts der Mitte“, cubeescape-reference
destiny2 › Imperial Needle ADS); die Pfeilspitze liegt rechts unten statt in der Mitte (Abweichung, Seitenvisier).
Schlichtheitsbudget: Leuchten 2 Funktionen (Visier: Pinköpfe · Auszug: Spannlicht) · Grafik 1 Band · Schrift 1 · Orange 2 (Klemmhebel
des Visiers, Leitfeder des Pfeils) · Schrauben nur an Pinschiene und Rollenachsen.
Proportion: Spanne 1016 mm (v1 1018), H/L mit Pfeil (Motiongen-Definition: L = Spanne, H in Pfeilrichtung) 0,72; Destiny-Bogen
0,73 (Motiongen, Trinity Ghoul), Hush/Biting Winds grob 0,7–0,85 (3/4-Bilder, ± 20–25 %). Spannzeit 0,60 s (Bild 18 bei 30/s) =
Draw Time 612 ms der Imperial Needle (cubeescape-reference destiny2, 0.7.0).
Bewegung (Daten): Auszug `draw` – Sehnenhälften folgen dem Nockpunkt (Segment), Pfeil nach hinten um DRAW, Rollen drehen 90°
(oben im, unten gegen den Uhrzeigersinn in der Seitenansicht, vorn rechts); Rücklauf beim Schuss (`release` → `shot`): Sehne und Rollen zurück,
Pfeil fliegt nach vorn. Die Wurfarme sind starr (Biegung erst mit dem Ego-Übertrag, wenn überhaupt). Spannlicht leuchtet bei vollem
Auszug. **Kein Magazin, kein Auswurf.**
Zwischenstopp (0.29): Nutzer „(a) so übernehmen“. Feinschliff nur in der Form: Griffstück mit Handballenwölbung statt Kasten
(Runde 1), Nocke r 3,4 und Auflage 0,4 mm unter dem Schaft (Posenprüfung: die Nocke streifte beim Pfeilflug die Auflage),
Schriftzug mit f als Vorderkante ganz auf dem Mittelstück (Lehre 0.28).
Status: Maße entworfen (Spanne und Auszug an v1 angelehnt; gemessene Werte im Spec), Formprinzipien abgeleitet.
"""
import math

from basic.common import (part, prof, box, cyl, cut_box, screws, mirror, rail, band, R_BODY, R_MID, R_SMALL, R_FINE)
from basic.pilot import energy_roles  # noqa: F401  (Leuchtrollen pin_glow, draw_light)
from basic.pilot.optics.sight_kit import pins, side_mount, PINS_SIZES, PINS_LINE
from basic.reticles import SIGHT
from basic.weapons import w07_combat_bow as V1

META = dict(V1.META, variant='v2.1', name='Sehnenzug v2.1', nick='Familie v2.1',
            summary='Compound-Kampfbogen mit Sichtfenster im Mittelstück, gespaltenen Wurfarmen, Rollen und Pinvisier B1 (Stil v2.1).')
ASSEMBLIES = V1.ASSEMBLIES
ARROW_U = 46                 # Pfeilachse über der Griffachse (Auflage direkt über der Hand)
BORE = ARROW_U               # Schussachse für die Visierhöhe (Familie: Visierlinie 66 mm darüber)
STRING_F = -150              # Sehne in Ruhe (Standhöhe 150 mm hinter der Griffachse)
DRAW = 420                   # Auszug: Nockpunkt von f −150 nach f −570
EYE_BEHIND = 20              # Augenpunkt am Ankerpunkt, 20 mm hinter dem Nockpunkt bei vollem Auszug
AXLE = (-150, 478)           # Rollenachse oben (unten gespiegelt); die Sehne endet in der Achse
CAM_R = 30
CAM_DEG = 90                 # Rollendrehung beim vollen Auszug (oben im, unten gegen den Uhrzeigersinn, Seitenansicht vorn rechts)
ARROW = (-150, 505)          # Pfeilschaft Nocke bis Spitzenhülse
WIN = dict(x_in=16.0, x_out=32.0, u0=38.0, u1=170.0)   # Sichtfenster: rechts davon frei für den Pfeil (Federn bis x 13), links der Fensterbogen
SIGHT_X = 58                 # Seitenvisier links neben dem Fensterbogen (Nutzer 28.10.2026: „das visier muss nach links“); Auge ebenso
SIGHT_U = ARROW_U + math.sqrt(SIGHT['height_mm'] ** 2 - SIGHT_X ** 2)   # Visierlinie 66 mm vom Pfeil (seitlich: Abstand, wie 0.28)
DECK = SIGHT_U - PINS_SIZES['M'] - PINS_LINE                             # Schienenoberkante am Visierträger
W_RISER = 30

P = []
# ---------------------------------------------------------------- Mittelstück mit Sichtfenster (gekröpft), Griffstück, Auflage
RISER_U = 218               # Mittelstück u −218 … 218 (≈ 0,43 der Spanne), Wurfarme ab den Aufnahmen
_riser = [(-6, -RISER_U), (28, -RISER_U), (44, -160), (46, -100), (30, -56), (12, -40), (12, 30), (34, 48), (46, 110), (44, 170),
          (28, RISER_U), (-6, RISER_U), (-14, 170), (-18, 110), (-20, 48), (-22, 30), (-22, -40), (-18, -60), (-14, -120), (-10, -170)]
_wx = (WIN['x_in'] + WIN['x_out'] + 1) / 2
P += [
    prof('riser', 'Mittelstück', 'Riser', 'riser', 'shell',
         'Trägt Wurfarme, Griffstück, Auflage und Visierträger; links gekröpft zum Fensterbogen (Sichtfenster für Pfeil und Blick)',
         'Grundkörper', _riser, W_RISER / 2 + WIN['x_out'] + 0.5, x=(WIN['x_out'] - W_RISER / 2) / 2,
         cuts=[cut_box(-60, 90, WIN['u0'], WIN['u1'], WIN['x_in'] + W_RISER / 2 + 1, x=(WIN['x_in'] - W_RISER / 2 - 1) / 2),   # Sichtfenster
               cut_box(-60, 90, 192, 300, 30, x=W_RISER / 2 + 15), cut_box(-60, 90, -300, 18, 30, x=W_RISER / 2 + 15),   # schlank
               dict(shape='prof', pts=[(2, -190), (24, -190), (32, -160), (28, -112), (10, -104), (2, -130)], w=60)]),       # Durchbruch
    prof('grip', 'Griffstück', 'Bow grip', 'grip_controls', 'rubber', 'Bogenhand umschließt das Mittelstück; trägt Socket_Hand',
         'um das Mittelstück geschraubt',
         # Runde 1: als Kasten gelesen → Handballenwölbung hinten (bis f −36), vorn schmaler mit Fingermulde, Kanten R_BODY
         [(-22, -52), (6, -52), (14, -40), (15, -18), (11, -2), (15, 18), (13, 34), (-14, 38), (-28, 26), (-36, 2), (-34, -26),
          (-28, -44)], W_RISER + 2, bevel=R_BODY),
    part('arrow_rest', 'Pfeilauflage', 'Arrow rest', 'riser', 'multi', 'anodized', 'Führt den Pfeil im Sichtfenster',
         'am Fensterbogen verschraubt (quer ins Fenster)', bevel=0.4,
         items=[dict(shape='box', f0=-6, f1=18, u0=ARROW_U - 9, u1=ARROW_U - 5, w=WIN['x_in'] + 2, x=WIN['x_in'] / 2),
                dict(shape='prof', pts=[(-2, ARROW_U - 6), (14, ARROW_U - 6), (10, ARROW_U - 3.6), (2, ARROW_U - 3.6)], w=3, x=0)]),   # Posenprüfung: Nocke frei
    box('pocket_top', 'Wurfarmaufnahme oben', 'Upper limb pocket', 'limbs', 'anodized', 'Klemmt den oberen Wurfarm',
        'auf dem Mittelstück verschraubt', -8, 38, RISER_U - 12, RISER_U + 16, W_RISER + 6, bevel=R_SMALL),
    box('pocket_bottom', 'Wurfarmaufnahme unten', 'Lower limb pocket', 'limbs', 'anodized', 'Klemmt den unteren Wurfarm',
        'auf dem Mittelstück verschraubt', -8, 38, -RISER_U - 16, -RISER_U + 12, W_RISER + 6, bevel=R_SMALL),
    part('band_side', 'Schrägband', 'Slanted band', 'riser', 'multi', 'accent', 'Lackiertes Band (einziges Grafikelement)', 'lackiert',
         bevel=0, items=[dict(shape='prof', pts=[(-12, 174), (-3, 174), (26, 200), (17, 200)], w=0.3, x=sx * (W_RISER / 2 + 0.15))
                         for sx in (1, -1)]),
    part('text_l', 'Schriftzug', 'Lettering', 'riser', 'text', 'anodized', 'Kennung „BASIC BW-07“ (einzige Schrift; dunkel auf Creme)',
         'aufgedruckt', bevel=0, text='BASIC  BW-07', size=4.2, f=25, u=-88, x=W_RISER / 2 + 0.05, side=1, depth=0.12),   # f = Vorderkante (wächst nach hinten, Lehre 0.28)
]
# Spannlicht (Blickfang): Linse auf der Rückseite des Fensterbogens, zum Auge; leuchtet bei vollem Auszug
_LU = 84
_lf = -19.4                  # Rückseite des Fensterbogens in Höhe der Linse (Kante (−20, 48) → (−18, 120))
P += [
    cyl('draw_light', 'Spannlicht', 'Draw light', 'riser', 'draw_light', 'Leuchtet bei vollem Auszug (Bogen bereit)',
        'in der Rückseite des Fensterbogens', 'f', (_LU, _wx), _lf - 0.6, _lf + 1.0, 3.2, bevel=0, segs=32,
        move=dict(kind='glow', pivot=None, event='full_draw', max=0.7)),
    cyl('draw_light_ring', 'Lichtring', 'Light ring', 'riser', 'trim', 'Blanker Ring um das Spannlicht', 'um die Linse',
        'f', (_LU, _wx), _lf - 0.9, _lf + 1.0, 4.6, r_in=3.2, bevel=0.3, segs=32),
]
# ---------------------------------------------------------------- Visierträger mit Schiene BRI-22, Visier B1 „Pins“
P += [
    part('sight_arm', 'Visierträger', 'Sight arm', 'riser', 'multi', 'anodized', 'Trägt die Visierschiene links neben dem Fensterbogen',
         'außen am Fensterbogen verschraubt', bevel=R_FINE,
         items=[dict(shape='box', f0=26, f1=62, u0=DECK - 14, u1=DECK - 6, w=SIGHT_X - 11 - WIN['x_out'] + 8,
                     x=(SIGHT_X - 11 + WIN['x_out'] - 4) / 2 + 2)]),
]
P += [dict(p, asm='riser', iface='BRI-22', x=SIGHT_X) for p in rail(30, 104, DECK - 8)]
P[-1]['cuts'] = [cut_box(36 + 12 * i, 41 + 12 * i, DECK - 4, DECK + 1, 30, x=SIGHT_X) for i in range(6)]
_sight, SIGHT_ANCHORS = side_mount(*pins(56, DECK, weapon_type=V1.META['type'], eye_f=STRING_F - DRAW - EYE_BEHIND), SIGHT_X)
P += _sight
# ---------------------------------------------------------------- Wurfarme (gespalten), Rollen mit Durchbrüchen
_c = [(16, RISER_U), (14, 290), (0, 360), (-30, 418), (-80, 460), (AXLE[0], AXLE[1]), (AXLE[0] - 12, AXLE[1] + 1)]
_th = [26, 24, 21, 18, 15, 13, 13]


def _limb(pid, de, en, sgn):
    c = [(f, sgn * u) for f, u in _c]
    return prof(pid, de, en, 'limbs', 'graphite', 'Speichert die Zugenergie; zur Spitze gespalten (Rolle dazwischen)',
                'in der Aufnahme geklemmt', band(c, _th), 34, bevel=R_SMALL,
                cuts=[dict(shape='prof', pts=band(c[2:] + [(AXLE[0] - 40, sgn * (AXLE[1] + 2))], [t + 6 for t in _th[2:]] + [18]),
                           w=12)])


def _cam(pid, de, en, sgn):
    a = (AXLE[0], sgn * AXLE[1])
    pts = [(a[0] + (CAM_R + 3 * math.cos(math.radians(d))) * math.cos(math.radians(d)) - 3,
            a[1] + CAM_R * math.sin(math.radians(d))) for d in range(0, 360, 12)]
    holes = [dict(shape='cyl', axis='x', c=(a[0] + 12.5 * math.cos(math.radians(d)), a[1] + 12.5 * math.sin(math.radians(d))),
                  a0=-6, a1=6, r=6.5, segs=24) for d in (90, 210, 330)]
    return prof(pid, de, en, 'limbs', 'dark_metal', 'Exzentrische Rolle; wickelt die Sehne ab und dreht beim Auszug',
                'auf der Achse zwischen den Zinken', pts, 8, bevel=R_FINE, cuts=holes,
                move=dict(kind='rotate', pivot=(a[0], a[1], 0), axis='x', range_deg=(0, -CAM_DEG * sgn), event='draw',
                          # Prüfpunkt 45° vor/unter (oben) bzw. vor/über (unten) der Achse: läuft bei vollem Auszug nach hinten;
                          # mit umgedrehtem Vorzeichen nach oben bzw. unten (Gegenprobe rot, test_motion)
                          expect=((a[0] + CAM_R * math.cos(math.radians(45)), a[1] - sgn * CAM_R * math.sin(math.radians(45)), 0),
                                  (-1, 0, 0))))


P += [_limb('limb_top', 'Wurfarm oben', 'Upper limb', 1), _limb('limb_bottom', 'Wurfarm unten', 'Lower limb', -1),
      _cam('cam_top', 'Rolle oben', 'Upper cam', 1), _cam('cam_bottom', 'Rolle unten', 'Lower cam', -1),
      part('cam_axles', 'Rollenachsen', 'Cam axles', 'limbs', 'multi', 'trim', 'Lagern die Rollen in den Zinken',
           'quer durch die Wurfarmspitzen', bevel=0.4,
           items=[dict(shape='cyl', axis='x', c=(AXLE[0], s * AXLE[1]), a0=-19, a1=19, r=4.5, segs=20) for s in (1, -1)])]
# ---------------------------------------------------------------- Sehne (zwei Hälften, folgen dem Nockpunkt) und Pfeil
for s, pid, de, en in ((1, 'string_top', 'Sehne oben', 'Upper string'), (-1, 'string_bottom', 'Sehne unten', 'Lower string')):
    a = (AXLE[0], s * AXLE[1])
    P.append(cyl(pid, de, en, 'string', 'string', f'{"Obere" if s > 0 else "Untere"} Sehnenhälfte; folgt dem Nockpunkt',
                 'zwischen Rollenachse und Nockpunkt', 'u', (STRING_F, 0), min(ARROW_U, a[1]), max(ARROW_U, a[1]), 1.6, bevel=0, segs=8,
                 move=dict(kind='segment', pivot=(a[0], a[1], 0), tip=(a[0], a[1], 0), nock=(STRING_F, ARROW_U, 0),
                           vector_mm=(-DRAW, 0, 0), event='draw', expect=((STRING_F, ARROW_U, 0), (-1, 0, 0)))))
TIP = ARROW[1] + 48
P += [
    cyl('arrow_shaft', 'Pfeilschaft', 'Arrow shaft', 'arrow', 'graphite', 'Pfeil; wird mit der Sehne zurückgezogen',
        'auf der Auflage, Nocke an der Sehne', 'f', (ARROW_U, 0), ARROW[0], ARROW[1], 3.2, segs=12, removable=True,
        move=dict(kind='translate', pivot=(ARROW[0], ARROW_U, 0), vector_mm=(-DRAW, 0, 0), event='draw',
                  expect=((TIP, ARROW_U, 0), (-1, 0, 0)))),
    cyl('arrow_ferrule', 'Spitzenhülse', 'Ferrule', 'arrow', 'trim', 'Blanke Hülse; trägt die Spitze', 'vorn auf dem Schaft',
        'f', (ARROW_U, 0), ARROW[1] - 6, ARROW[1] + 4, 4.2, segs=16, bevel=0.4, parent_part='arrow_shaft'),
    cyl('arrow_head', 'Pfeilspitze', 'Arrow head', 'arrow', 'dark_metal', 'Schneide (vierkant)', 'auf der Hülse', 'f', (ARROW_U, 0),
        ARROW[1] + 3, TIP, 6.5, r1=0.6, segs=4, bevel=R_FINE, parent_part='arrow_shaft'),
    cyl('arrow_nock', 'Nocke', 'Nock', 'arrow', 'anodized', 'Rastet an der Sehne ein', 'Schaftende', 'f', (ARROW_U, 0),
        ARROW[0] - 8, ARROW[0] + 6, 3.4, segs=12, parent_part='arrow_shaft',
        cuts=[cut_box(ARROW[0] - 10, ARROW[0] + 1.5, ARROW_U - 1.4, ARROW_U + 1.4, 12)]),
    prof('fletch_top', 'Leitfeder', 'Cock vane', 'arrow', 'accent', 'Stabilisiert den Flug; zeigt die Nockrichtung', 'am Schaft',
         [(ARROW[0] + 14, ARROW_U), (ARROW[0] + 74, ARROW_U), (ARROW[0] + 68, ARROW_U + 11), (ARROW[0] + 24, ARROW_U + 12)], 1.2,
         bevel=0.3, parent_part='arrow_shaft'),
    part('fletch_l', 'Befiederung links', 'Left vane', 'arrow', 'plan', 'graphite', 'Stabilisiert den Flug', 'am Schaft',
         bevel=0.3, parent_part='arrow_shaft', u0=ARROW_U - 0.6, u1=ARROW_U + 0.6,
         pts=[(ARROW[0] + 14, 2), (ARROW[0] + 74, 2), (ARROW[0] + 68, 12), (ARROW[0] + 24, 13)]),
    part('fletch_r', 'Befiederung rechts', 'Right vane', 'arrow', 'plan', 'graphite', 'Stabilisiert den Flug', 'am Schaft',
         bevel=0.3, parent_part='arrow_shaft', u0=ARROW_U - 0.6, u1=ARROW_U + 0.6,
         pts=[(ARROW[0] + 14, -2), (ARROW[0] + 24, -13), (ARROW[0] + 68, -12), (ARROW[0] + 74, -2)]),
]
PARTS = P
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip', note='Bogenhand im Griffstück (Griffachse)'),
    'Socket_SupportHand': dict(at=(STRING_F, ARROW_U, 0), part='string_top', note='Zughand am Nockpunkt in Ruhe'),
    'Socket_Nock': dict(at=(STRING_F, ARROW_U, 0), part='string_top', note='Nockpunkt in Ruhe (Toolgen-Name)'),
    'Socket_DrawFull': dict(at=(STRING_F - DRAW, ARROW_U, 0), part='string_top', note=f'Nockpunkt bei vollem Auszug ({DRAW} mm)'),
    'Socket_ArrowTip': dict(at=(TIP, ARROW_U, 0), part='arrow_head', note='Pfeilspitze in Ruhe (Toolgen-Name)'),
    'Socket_Muzzle': dict(at=(10, ARROW_U, 0), part='arrow_rest', note='Abgangspunkt des Pfeils an der Auflage'),
}
ANCHORS.update(SIGHT_ANCHORS)
_d = [(0, 0), (18, 1), (40, 1), (42, 0)]
_light = [(0, 0), (16, 0), (18, 1), (40, 1), (41, 0)]
ACTIONS = {
    'draw_hold_release': dict(de='Ausziehen, halten, lösen', frames=60, step=2, keys={
        'arrow_shaft': [(0, 0), (18, 1), (40, 1), (42, -0.4), (46, -4)], 'string_top': _d, 'string_bottom': _d,
        'cam_top': _d, 'cam_bottom': _d, 'draw_light': _light},
        events=[(0, 'nocked'), (18, 'full_draw'), (40, 'release'), (42, 'shot'), (46, 'arrow_gone')], view=(-0.95, 0.15, 0.3)),
    'let_down': dict(de='Entspannen ohne Schuss', frames=40, keys={
        'arrow_shaft': [(0, 0), (16, 1), (24, 1), (40, 0)], 'string_top': [(0, 0), (16, 1), (24, 1), (40, 0)],
        'string_bottom': [(0, 0), (16, 1), (24, 1), (40, 0)], 'cam_top': [(0, 0), (16, 1), (24, 1), (40, 0)],
        'cam_bottom': [(0, 0), (16, 1), (24, 1), (40, 0)], 'draw_light': [(0, 0), (14, 0), (16, 1), (24, 1), (26, 0)]},
        events=[(16, 'full_draw'), (40, 'relaxed')], view=(-0.95, 0.15, 0.3)),
}
EXPLODE = {'arrow': (0, 0, -90), 'string': (-40, 0, 0), 'limbs': (0, 0, 0), 'sight': (60, 40, 0), 'grip_controls': (-60, 0, 0),
           'riser': (0, 0, 0)}
HERO = V1.HERO
SIGHT_ID = 'B1'    # Visier des Baukastens v3 (visier-konzept › 6a); test_sights prüft dessen Pflichtteile, Pinabstände und Sichtfeld
EJECT = None       # Bogen: kein Magazin, kein Hülsenauswurf (Daten statt Sonderlogik; check: fire 'draw_release' → EJECT None)
