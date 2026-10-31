"""BASIC-13 v2.1 – Granatwerfer (Trommel) im Stil v2.1 („Destiny-Detaildichte + AAA-Material, schlicht“), Familie des Piloten BASIC-01 v2.1.

Nutzer 28.10.2026 (Zwischenstopp nach dem Kipplauf-Erstentwurf): „Warum hat der granatwerfer keine Trommel? Im besten Fall für später
animiert.“ – Wahl „Trommel statt Kipplauf“: BASIC-13 v2.1 ist der Trommelwerfer (Erweiterung EXT-02 vorgezogen, Leitmerkmal 13 im
Designvertrag geändert); die Reihe v1 (`basic/weapons/w13_grenade_launcher.py`) bleibt der Kipplauf.

Recherche (docs/quellen.md › Q-D2-IMG, gesichtet 28.10.2026, Bungie-Manifest): Wendigo GL3 und Bitter/Sweet (große Drehtrommel vor dem
Griff unter einem Rahmen, kurzer dicker Lauf darüber, Schaft), Wilderflight (Creme-Rücken über dunklem Lauf, Laufschellen, leuchtende
Munitionsanzeige), Flash and Thunder (Kipplauf; nicht mehr übernommen), Festival Flight (verspielt, nicht übernommen). Nur Prinzipien.

Formsprache-Checkliste (stilhandbuch §3):
| Frage | Granatwerfer v2.1 |
|---|---|
| Leitmerkmal der Silhouette | große Drehtrommel (Ø 140) in einem offenen Rahmen vor dem Griff: Gehäuse und Oberbrücke darüber, Stoßplatte dahinter, Joch davor; kurzer dicker Lauf auf Höhe der oberen Kammer |
| Schichten | Unteres Gehäuse, Stoßplatte, Halbschale am Lauf, Schaft S2 (Graphit) → Gehäuse, Oberbrücke, Joch, Lauf (Creme, Fuge 1 mm) → Trommel und Ladeklappe (eloxiert) mit blanker Stirnkante → Schiene → Visier W1 |
| Negativraum | offener Rahmen: die Trommel steht seitlich frei zwischen Stoßplatte und Joch; sechs Kammerfenster zeigen die Granaten; Ladeschale links am Gehäuse mit der Ladeklappe (Ladeweg der Granate); Daumenloch im Schaft S2 |
| Blickfang | Trommel mit sechs Kammerfenstern: Messinghülsen, orange Zünderringe und dunkle Köpfe in der eloxierten Trommel – Kontrast ohne Leuchten |
| Zweiton-Blockung | Gehäuse, Oberbrücke, Joch, Lauf Lack (`shell`), Unteres Gehäuse, Stoßplatte, Halbschale, Schaft Polymer (`graphite`), Trommel eloxiert (`ring_anod`, ohne feine Kratzer) |
| Grafik | ein Schrägband vorn am Gehäuse (rechts; links liegt die Ladeschale), ein Schriftzug „BASIC GL-13“ (hell auf Graphit) |
| Front | mehrstufige Mündung: dunkler Mündungsring mit vier Schlitzen, blanke Krone, dahinter blanker Laufring – große dunkle Bohrung Ø 43; darunter die Kammermündungen der Trommel |
| Übergänge | Oberbrücke geht aus dem Gehäuse in das Joch über (ein Rahmen); Trommelachse in Stoßplatte und Joch gelagert; Lauf stößt mit Fuge 1 mm an das Joch |
| Ergonomie | Griff BGM-1 in v2.1-Form (Familie), Trommel vor dem Abzugsbügel (Nachladen links wie Kammerstängel 09 und MG-Kasten 15: die Stützhand öffnet die Ladeklappe hinten links, die Granate gleitet in der Ladeschale in die Kammer; Nutzer 28.10.2026 „Müsste das Granatwerfer nachladen nicht auf die linke seite“), Halbschale unter dem Lauf für die Stützhand |

Visier: W1 „D-Linse“ (Baukasten v3, visier-konzept › 6a; `common.d_linse`), Visier-Standard 3 Typ `lens_chevron` (Reflex):
D-Haube aus Flachprofil 2,4 mm mit oranger Kerbmarke oben, drei Fallmarken links innen (Haltepunkte für den Bogenschuss);
Größe M (Glas 26 mm, 18,9 % der Bildbreite); Absehen gezeichnet (Hüftform `circle_cross` flach im Glas); Weltzoom der Klasse
1,4 (reticles.CLASS_ZOOM, ohne Visierbonus wie Destiny). W3 Leiter nur als Variante im Katalog (`sight_kit_more.launcher_ladder`).
Schlichtheitsbudget: Leuchten 1 Funktion (Visier: Emitter und Absehen) · Grafik 1 Band · Schrift 1 · Orange 3 (Klappenknopf,
Klemmhebel des Visiers, Kerbmarke; dazu die Zünderringe als Munitionskennung) · Schrauben nur an Paneelen und Schaft.
Proportion: Länge ≈ 0,67 m (v1 0,64 m), H/L ≈ 0,40; Destiny-Trommelwerfer beobachtet (Bericht 0.28, grob aus 3/4-Bildern).
Bewegung (Daten, für die Animation mit dem Ego-Übertrag): Abzug und Trommel dreht je Schuss eine Kammer weiter (60°, `move.cycle =
'shot'` wie der MG-Gurt; durch die sechsfache Teilung steht danach wieder eine volle Kammer oben) (`fire`); Klappenknopf, Ladeklappe
links auf, je Kammer Hülse aus, Granate ein und Trommel weiter (sechsmal), Klappe zu (`reload`). Auswurf: die leeren Hülsen fallen
nur beim Nachladen aus der Ladeklappe (`EJECT.on = 'reload'`, Ereignis `case_out`), nicht je Schuss (Daten statt Sonderlogik; check:
Munition in einer drehenden Kammer → kein Auswurf je Schuss).
Status: Maße entworfen (Trommel für sechs 40-mm-Granaten, Lagen an Familie 15 angelehnt; gemessene Werte im Spec), Formprinzipien
abgeleitet.
"""
import math

from basic.common import (part, prof, box, cyl, cut_box, screws, mirror, rail, grip_v21, stock_s2, R_MID, R_SMALL, R_FINE)
from basic.pilot import metal_roles  # noqa: F401  Rolle ring_anod (Trommel ohne feine Kratzer)
from basic.common import d_linse
from basic.weapons import w13_grenade_launcher as V1

META = dict(V1.META, variant='v2.1', name='Trommel v2.1', nick='Familie v2.1', type_de='Granatwerfer (Trommel)',
            type_en='Grenade Launcher (drum)', ammo='heavy', fire='semi_auto',
            summary='Granatwerfer mit sechsschüssiger Drehtrommel im offenen Rahmen, Ladeklappe, Schaft S2 und Visier W1 „D-Linse“ '
                    '(Stil v2.1; Nutzerwahl „Trommel statt Kipplauf“, EXT-02).')
ASSEMBLIES = V1.ASSEMBLIES
GRIP_TOP = 40
BORE = 112                   # Laufachse = obere Kammer
TOP = 144                    # Oberkante Gehäuse und Oberbrücke; Schiene bis u 152, Visierlinie u 178 (Visierhöhe 66)
REC0, REC1 = -110, 88        # Gehäuse hinten / vorn an der Stoßplatte
W_REC = 48
DRUM_U = 66                  # Trommelachse
RC, R_DRUM = 46.0, 70.0      # Kammerkreis, Trommelradius (sechs Kammern Ø 43, Wand ≥ 3 mm)
CH_R = 21.5                  # Kammer Ø 43 (40-mm-Granate)
DRUM = (98, 206)             # Trommel f0, f1
PLATE = (88, DRUM[0] - 1)    # Stoßplatte hinter der Trommel
GATE_F = (83.8, 87.8)        # Ladeklappe 0,2 mm vor der Stoßplatte im Ladeausschnitt des Gehäuses (schwenkt in ihrer Ebene)
NOTCH = (-4, 90, 62, 118)    # Ladeschale links in Gehäuse und Unterem Gehäuse (f0, f1, u0, u1), x ab +15: Klappe und Ladeweg
YOKE = (DRUM[1] + 2, 224)    # Joch vor der Trommel
BAR_R = 30.0                 # Lauf Ø 60
MUZ = (360, 388)             # Mündungsring
SLEEVE = (246, 336)          # Halbschale unter dem Lauf
ANG = [90 + 60 * k for k in range(6)]   # Kammerwinkel (x links, u oben): 90° = oben = Laufachse
GATE_K = 5                   # Ladekammer: ANG[5] = 390° = 30° = oben links (Nachladen auf der Stützhand-Seite)
G0 = DRUM[0] + 1             # Hülsenboden der Granaten


def _ch(a, r=RC):
    """Kammermitte (u, x) beim Winkel a."""
    return (DRUM_U + r * math.sin(math.radians(a)), r * math.cos(math.radians(a)))


GATE_C = _ch(ANG[GATE_K])

P = []
# ---------------------------------------------------------------- Gehäuse, Rahmen (Oberbrücke, Joch), Stoßplatte
P += [
    prof('receiver', 'Gehäuse', 'Receiver', 'receiver', 'shell', 'Tragkörper: Schloss, Schiene, Oberbrücke über der Trommel',
         'mit dem Unteren Gehäuse über zwei Querbolzen (fest)', [(REC0, 82), (REC1, 82), (REC1, TOP), (REC0 + 6, TOP), (REC0, TOP - 6)],
         W_REC, cuts=[cut_box(-92, -10, 92, 132, 3.0, x=W_REC / 2 + 0.6), cut_box(-92, -10, 92, 132, 3.0, x=-W_REC / 2 - 0.6),
                     cut_box(*NOTCH, 20, x=25)]),
    prof('top_strap', 'Oberbrücke', 'Top strap', 'receiver', 'shell', 'Verbindet Gehäuse und Joch über der Trommel (Rahmen)',
         'aus dem Gehäuse in das Joch, verschraubt', [(REC1 - 2, DRUM_U + R_DRUM + 2), (YOKE[1], DRUM_U + R_DRUM + 2), (YOKE[1], TOP),
                                                     (REC1 - 2, TOP)], 40),
    prof('yoke', 'Joch', 'Yoke', 'receiver', 'shell', 'Lagert Trommelachse und Lauf vorn', 'unter der Oberbrücke angeformt',
         [(YOKE[0], DRUM_U - 16), (YOKE[1], DRUM_U - 16), (YOKE[1], TOP), (YOKE[0], TOP)], 44),
    prof('lower', 'Unteres Gehäuse', 'Lower receiver', 'receiver', 'graphite', 'Griffmodul, Abzugsgruppe',
         'unter dem Gehäuse, Fuge 1 mm; Bauch gerade bis vor den Abzugsbügel',
         [(REC0, 62), (-62, 40), (REC1 - 2, 40), (REC1, 46), (REC1, 81), (REC0, 81)], W_REC - 4, cuts=[cut_box(*NOTCH, 20, x=25)]),
    cyl('recoil_plate', 'Stoßplatte', 'Recoil plate', 'receiver', 'graphite', 'Schließt die Kammern hinten; Loch der Ladeklappe links',
        'vor dem Unteren Gehäuse verschraubt', 'f', (DRUM_U, 0), PLATE[0], PLATE[1], R_DRUM + 1, segs=64, bevel=R_SMALL, smooth=True,
        cuts=[dict(shape='cyl', axis='f', c=GATE_C, a0=PLATE[0] - 1, a1=PLATE[1] + 1, r=CH_R + 0.5, segs=32)]),
    cyl('drum_axle', 'Trommelachse', 'Drum axle', 'mechanism', 'trim', 'Lagert die Trommel; Stirn blank',
        'in Stoßplatte und Joch', 'f', (DRUM_U, 0), PLATE[0] - 1, YOKE[1] + 1, 9.0, segs=32, bevel=0.4, smooth=True),
    box('side_panel_l', 'Seitenpaneel links', 'Side panel left', 'receiver', 'anodized', 'Wartungsdeckel über dem Schloss',
        'in die Mulde geschraubt (4 Schrauben)', -90, -12, 94, 130, 1.2, bevel=R_FINE, x=W_REC / 2 - 0.8),
    box('side_panel_r', 'Seitenpaneel rechts', 'Side panel right', 'receiver', 'anodized', 'Wartungsdeckel über dem Schloss',
        'in die Mulde geschraubt (4 Schrauben)', -90, -12, 94, 130, 1.2, bevel=R_FINE, x=-W_REC / 2 + 0.8),
    part('panel_screws', 'Paneelschrauben', 'Panel screws', 'receiver', 'multi', 'trim', 'Halten die Seitenpaneele',
         'in den Paneelen', bevel=0.2, items=mirror(screws([(-86, 98), (-86, 126), (-16, 98), (-16, 126)], W_REC / 2 - 0.2, r=1.6, h=0.8))),
    part('takedown_pins', 'Querbolzen', 'Takedown pins', 'receiver', 'multi', 'metal', 'Verbinden Gehäuse und Unteres Gehäuse',
         'quer durch das Gehäuse (lösbar)', bevel=0.4, items=mirror(screws([(-98, 74), (70, 52)], W_REC / 2 - 1, r=3.6, h=1.0))),
    part('band_side', 'Schrägband', 'Slanted band', 'receiver', 'multi', 'accent', 'Lackiertes Band (einziges Grafikelement)',
         'lackiert rechts (links liegt die Ladeschale)', bevel=0,
         items=[dict(shape='prof', pts=[(48, 82.5), (58, 82.5), (70, TOP - 0.5), (60, TOP - 0.5)], w=0.3, x=-W_REC / 2 - 0.15)]),
    part('text_l', 'Schriftzug', 'Lettering', 'receiver', 'text', 'decal', 'Kennung „BASIC GL-13“ (einzige Schrift)',
         'aufgedruckt', bevel=0, text='BASIC  GL-13', size=5.0, f=-40, u=62, x=(W_REC - 4) / 2 + 0.05, side=1, depth=0.12),
]
P += [dict(p, mat='anodized') for p in rail(-90, 10, TOP)]
P[-1]['cuts'] = [cut_box(-82 + 14 * i, -75 + 14 * i, TOP + 4, TOP + 9, 30) for i in range(7)]
# Visier W1 „D-Linse“ (Baukasten v3, Standard Granatwerfer nach visier-konzept › 6a)
_sight, SIGHT_ANCHORS = d_linse(-60, TOP + 8, weapon_type=V1.META['type'])
P += _sight
# ---------------------------------------------------------------- Trommel (Leitmerkmal, Blickfang) und Ladeklappe
P += [
    cyl('drum', 'Trommel', 'Drum', 'mechanism', 'ring_anod', 'Sechs Kammern; dreht je Schuss eine Kammer weiter; sechs Kammerfenster',
        'auf der Trommelachse zwischen Stoßplatte und Joch', 'f', (DRUM_U, 0), DRUM[0], DRUM[1], R_DRUM, r_in=9.4, segs=64,
        bevel=R_SMALL, smooth=True,
        cuts=[dict(shape='cyl', axis='f', c=_ch(a), a0=DRUM[0] - 1, a1=DRUM[1] + 1, r=CH_R, segs=32) for a in ANG]
        + [dict(shape='cyl', axis='f', c=_ch(a, RC + 32), a0=DRUM[0] + 22, a1=DRUM[1] - 22, r=14.0, segs=32) for a in ANG],
        move=dict(kind='rotate', pivot=(DRUM[0], DRUM_U, 0), axis='f', range_deg=(0, 60), event='fire', cycle='shot',
                  note='eine Kammer weiter je Schuss (oben → rechts), danach zurück: durch die sechsfache Teilung steht wieder eine volle '
                       'Kammer oben; Animation mit dem Ego-Übertrag',
                  expect=((DRUM[0], BORE, 0), (0, 0, -1)))),
    cyl('drum_rim', 'Trommelkante', 'Drum rim', 'mechanism', 'trim', 'Blanke Stirnkante vorn an der Trommel', 'vorn an der Trommel',
        'f', (DRUM_U, 0), DRUM[1] - 3, DRUM[1] + 0.4, R_DRUM + 0.4, r_in=R_DRUM - 4, segs=64, bevel=0.4, smooth=True, parent_part='drum'),
    part('load_gate', 'Ladeklappe', 'Loading gate', 'ammo', 'cyl', 'anodized',
         'Deckt die Ladekammer hinten links ab; schwenkt in ihrer Ebene nach links', 'auf der Stoßplatte in der Ladeschale; Drehpunkt '
         'links außen in Höhe der Trommelachse', bevel=R_SMALL, axis='f', c=GATE_C, a0=GATE_F[0], a1=GATE_F[1], r=CH_R + 3, segs=32,
         move=dict(kind='rotate', pivot=(GATE_F[0], DRUM_U, 68), axis='f', range_deg=(0, -90), event='reload',
                   expect=((GATE_F[0], GATE_C[0], GATE_C[1]), (0, 0.1, 1)))),
    part('gate_button', 'Klappenknopf', 'Gate release', 'grip_controls', 'cyl', 'accent', 'Entriegelt die Ladeklappe',
         'Druckknopf links am Gehäuse über der Ladeschale', bevel=R_FINE, axis='x', c=(34, 126), a0=W_REC / 2 - 2, a1=W_REC / 2 + 3, r=4.5,
         segs=20, move=dict(kind='translate', pivot=(34, 126, W_REC / 2), vector_mm=(0, 0, -2.5), event='reload',
                            expect=((34, 126, W_REC / 2 + 3), (0, 0, -1)))),
]
# ---------------------------------------------------------------- Granaten in den Kammern (fünf fest, die Ladekammer als eigenes Teil)


def _grenade(c, f0):
    return [dict(shape='cyl', axis='f', c=c, a0=f0 + 34, a1=f0 + 72, r=20.0, segs=24),
            dict(shape='cyl', axis='f', c=c, a0=f0 + 72, a1=f0 + 97, r=20.0, r1=10.0, segs=24)]


def _case(c, f0):
    return [dict(shape='cyl', axis='f', c=c, a0=f0, a1=f0 + 2, r=21.3, segs=24),
            dict(shape='cyl', axis='f', c=c, a0=f0 + 2, a1=f0 + 35, r=20.8, segs=24)]


def _band(c, f0):
    return [dict(shape='cyl', axis='f', c=c, a0=f0 + 42, a1=f0 + 50, r=20.4, segs=24)]


_full = [_ch(a) for k, a in enumerate(ANG) if k != GATE_K]
# Füllstand (0.34 „Payload“): je Kammer ein eigener Granatkopf mit Zünderring, damit Unity leere Kammern zeigt (der Kopf ist weg, die
# Hülse bleibt bis zum Nachladen). Kammer 0 (Laufachse) behält die IDs grenades/grenade_bands, die Kammern 1–4 sind neu; die Hülsen
# bleiben ein Teil (grenade_cases), die Ladekammer (5) ist das Teil grenade.
_KS = [k for k in range(6) if k != GATE_K]


def _head_id(k):
    return 'grenades' if k == 0 else f'grenade_k{k}'


def _band_id(k):
    return 'grenade_bands' if k == 0 else f'grenade_band_k{k}'


P += [
    part('grenade_cases', 'Granathülsen', 'Grenade cases', 'ammo', 'multi', 'brass', 'Hülsen der fünf Granaten (bleiben nach dem Schuss in der Kammer)',
         'in den Kammern', bevel=0.6, smooth=True, parent_part='drum', items=[i for c in _full for i in _case(c, G0)]),
]
for k in _KS:
    c = _ch(ANG[k])
    P += [
        part(_head_id(k), f'Granate Kammer {k}', f'Grenade chamber {k}', 'ammo', 'multi', 'dark_metal',
             'Granatkopf in der Kammer (sichtbar im Kammerfenster); fehlt, wenn die Kammer verschossen ist',
             'in der Kammer auf der Hülse', bevel=R_SMALL, smooth=True, parent_part='drum', items=_grenade(c, G0)),
        part(_band_id(k), f'Zünderring Kammer {k}', f'Fuse band chamber {k}', 'ammo', 'multi', 'accent',
             'Kennzeichnet die Granate (Munitionskennung)', 'auf dem Granatkopf', bevel=R_FINE, smooth=True, parent_part=_head_id(k),
             items=_band(c, G0)),
    ]
P += [
    part('grenade', 'Ladegranate', 'Loading grenade', 'ammo', 'multi', 'dark_metal', 'Granate der Ladekammer; wird von hinten eingeschoben',
         'in der Ladekammer', bevel=R_SMALL, smooth=True, parent_part='drum', items=_grenade(GATE_C, G0),
         move=dict(kind='translate', pivot=(G0 + 50, GATE_C[0], GATE_C[1]), vector_mm=(-100, 0, 0), event='reload', removable=True,
                   note='Ruhelage = geladen; je Kammer durch die offene Ladeklappe aus der Ladeschale von hinten eingeschoben',
                   expect=((G0, GATE_C[0], GATE_C[1]), (-1, 0, 0)))),
    part('grenade_case', 'Hülse der Ladegranate', 'Loading grenade case', 'ammo', 'multi', 'brass', 'Hülse der Ladegranate',
         'an der Ladegranate', bevel=0.6, smooth=True, parent_part='grenade', items=_case(GATE_C, G0)),
    part('grenade_band', 'Zünderring der Ladegranate', 'Loading grenade fuse band', 'ammo', 'multi', 'accent',
         'Kennzeichnet die Ladegranate', 'auf dem Granatkopf', bevel=R_FINE, smooth=True, parent_part='grenade', items=_band(GATE_C, G0)),
]
# ---------------------------------------------------------------- Lauf, Mündung, Halbschale
P += [
    cyl('barrel', 'Abschusslauf', 'Launch tube', 'barrel', 'shell', 'Kurzer dicker Lauf vor der oberen Kammer',
        'im Joch verschraubt, Fuge 1 mm', 'f', (BORE, 0), YOKE[1] + 1, MUZ[0] + 4, BAR_R, r_in=CH_R, segs=48, bevel=R_SMALL, smooth=True),
    part('barrel_rings', 'Laufringe', 'Barrel rings', 'barrel', 'multi', 'trim', 'Blanke Ringe am Laufansatz und vor der Mündung',
         'auf den Lauf gepresst', bevel=0.3, smooth=True,
         items=[dict(shape='cyl', axis='f', c=(BORE, 0), a0=a, a1=a + 4, r=BAR_R + 1.0, r_in=BAR_R - 0.4, segs=48)
                for a in (YOKE[1] + 6, MUZ[0] - 14)]),
    cyl('muzzle', 'Mündungsring', 'Muzzle ring', 'barrel', 'dark_metal', 'Verstärkt die Mündung, vier Schlitze; Socket_Muzzle',
        'auf das Laufende geschraubt', 'f', (BORE, 0), MUZ[0], MUZ[1], BAR_R + 3.5, r_in=CH_R, segs=48, bevel=R_SMALL, smooth=True,
        cuts=[cut_box(MUZ[0] + 8, MUZ[1] - 8, BORE - 4, BORE + 4, 2 * BAR_R + 12), cut_box(MUZ[0] + 8, MUZ[1] - 8, BORE - 40, BORE + 40, 8)]),
    cyl('muzzle_crown', 'Mündungskrone', 'Muzzle crown', 'barrel', 'trim', 'Blanke Stirnkante um die Bohrung', 'vorn am Mündungsring',
        'f', (BORE, 0), MUZ[1] - 2, MUZ[1] + 2, BAR_R + 1.0, r_in=CH_R + 0.5, segs=48, bevel=0.5, smooth=True),
    cyl('forend', 'Vorderschaft', 'Fore-end', 'support', 'graphite', 'Halbschale der Stützhand unter dem Lauf',
        'um die untere Laufhälfte geschraubt', 'f', (BORE, 0), SLEEVE[0], SLEEVE[1], BAR_R + 4, r_in=BAR_R - 0.5, segs=48, bevel=R_MID,
        smooth=True, cuts=[cut_box(SLEEVE[0] - 1, SLEEVE[1] + 1, BORE + 6, BORE + 50, 2 * BAR_R + 20)]
        + [dict(shape='cyl', axis='f', c=(BORE, 0), a0=SLEEVE[0] + 24 + 22 * i, a1=SLEEVE[0] + 28 + 22 * i, r=BAR_R + 5, r_in=BAR_R + 3,
                segs=48) for i in range(3)]),                                                 # Griffrillen als Nuten
]
# ---------------------------------------------------------------- Griff, Schaft S2 mit Daumenloch
P += grip_v21(top=GRIP_TOP)
_ua = TOP - 24               # Schaft S2: Laufachse der Schnittstelle 24 mm unter der Oberkante (BST-2)
for p in stock_s2(REC0, _ua):
    if p['id'] == 'stock':
        p['cuts'] = [dict(shape='prof', pts=[(-132, _ua - 28), (-132, _ua - 2), (-176, _ua + 2), (-200, _ua - 8), (-204, _ua - 30),
                                             (-190, _ua - 38), (-160, _ua - 32)], w=50)]
        p['func'] = 'Einteilige Schulterstütze mit Daumenloch'
    if p['id'] == 'butt_pad':
        p['mat'] = 'rubber'
    P.append(p)
P += [part('stock_bolts', 'Schaftbolzen', 'Stock bolts', 'stock', 'multi', 'trim', 'Halten den Schaft am Gehäuse',
           'quer durch den Schaftansatz', bevel=0.3, items=mirror(screws([(REC0 - 10, _ua + 14), (REC0 - 10, _ua - 26)], 17.4, r=2.4, h=1.0)))]
PARTS = P
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip', note='Haupthand, auf der Griffachse'),
    'Socket_SupportHand': dict(at=((SLEEVE[0] + SLEEVE[1]) / 2, BORE - BAR_R - 4, 0), part='forend', note='Unterseite der Halbschale'),
    'Socket_Muzzle': dict(at=(MUZ[1] + 2, BORE, 0), part='muzzle_crown', note='Stirn der Mündungskrone auf der Laufachse'),
    'Socket_LoadingGate': dict(at=(GATE_F[0], GATE_C[0], GATE_C[1]), part='load_gate', note='Ladeklappe hinten links (Ladekammer)'),
}
ANCHORS.update(SIGHT_ANCHORS)
# Auswurf (Daten, kein Anker): beim Nachladen fällt je Kammer die leere Hülse aus der offenen Ladeklappe nach hinten links unten, nicht
# beim Schuss (Trommel: die Hülse bleibt in der Kammer).
# Hülsenform grenade_40 in ego.EJECT.cases (seit dem Ego-Übertrag 0.33 „Armory“ P4)
EJECT = dict(at=(GATE_F[0], round(GATE_C[0], 1), round(GATE_C[1], 1)), dir=(-0.4, -0.6, 0.7), case='grenade_40', on='reload',
             event='case_out', src='E: aus der Ladekammer durch die offene Ladeklappe, nach links unten (Stützhand-Seite, Waffe beim Nachladen abgesenkt); '
                                    'nur beim Nachladen')
# Ego-Griffe (0.33 „Armory“ P4, ego.profile)
EGO_GRIPS = {
    'grip':    dict(contact=(-3, -6, -16.5), palm=(0.15, 0.0, 1.0), fingers=(1.0, -0.06, 0.0), fingers_pose='trigger',
                    src='E wie die Pilotwaffe (Griff BGM-1 v2.1, gleiche Lage zu Socket_Hand)'),
    'support': dict(contact=(291, 76.5, -2), palm=(0.0, 1.0, -0.25), fingers=(0.08, 0.15, -1.0), fingers_pose='underhand',
                    src='E unter der Halbschale (Socket_SupportHand, Unterkante u 78), Lage wie die Pilotwaffe'),
    'mag':     dict(part='grenade', contact=(165, GATE_C[0], round(GATE_C[1] + 21, 1)), palm=(0.0, 0.0, -1.0), fingers=(1.0, 0.3, 0.0),
                    fingers_pose='mag_hold', src='E links an der Ladegranate (Ruhelage in der Ladekammer), schiebt sie von hinten ein'),
    'gate':    dict(contact=(34, 126, W_REC / 2 + 4), palm=(0.0, 0.0, -1.0), fingers=(0.45, 0.9, 0.0), fingers_pose='pinch',
                    src='E am Klappenknopf links über der Ladeschale'),
    'charge':  dict(contact=(34, 126, W_REC / 2 + 4), palm=(0.0, 0.0, -1.0), fingers=(0.45, 0.9, 0.0), fingers_pose='pinch',
                    src='E wie gate (vom Nachladen nicht genutzt)'),
}
# Live-Teile: nur der Abzug je Schuss; die Trommel dreht fire_cycle. rounds (0.34 „Payload“): Füllstand je Kammer in Kammerfolge ANG
# (k = 0 Laufachse, 5 Ladekammer); Unity verfolgt, welche Kammer geladen ist (Schuss leert die Laufkammer, ShellIn füllt die Ladekammer,
# die Trommel trägt den Zustand mit, sobald sie nach fire_cycle bzw. dem Laden zurückspringt) und blendet Kopf und Zünderring leerer
# Kammern aus; die Hülse bleibt. Drehsinn: die Trommel bringt Kammer k nach k + 1 (die Ladekammer 5 rückt in den Lauf).
EGO_LIVE = dict(trigger='trigger', bolt='', port='',
                rounds=dict(mode='drum', drum='drum', barrel=0, gate=GATE_K,
                            sets=[['grenade', 'grenade_band'] if k == GATE_K else [_head_id(k), _band_id(k)] for k in range(6)]))
_idx = [22 + 14 * k for k in range(6)]          # Kammerwechsel beim Laden
ACTIONS = {
    'fire': dict(de='Schuss, Trommel eine Kammer weiter', frames=18, step=1, keys={
        'trigger': [(0, 0), (2, 1), (6, 0)], 'drum': [(0, 0), (3, 0), (9, 1), (9, 0)]}, events=[(2, 'shot')], view=(-0.85, -0.25, 0.45)),
    'reload': dict(de='Klappe auf, je Kammer Hülse aus und Granate ein, Trommel weiter, Klappe zu', frames=120, keys={
        'gate_button': [(0, 0), (4, 1), (10, 1), (14, 0)], 'load_gate': [(0, 0), (6, 0), (16, 1), (106, 1), (116, 0)],
        'grenade': [(0, 0)] + [k for f in _idx for k in ((f - 4, 0), (f - 3, 1), (f + 6, 0))],
        'drum': [(0, 0)] + [k for f in _idx for k in ((f + 6, 0), (f + 11, 1), (f + 11, 0))]},
        events=[(16, 'gate_open')] + [(f - 3, 'case_out') for f in _idx] + [(f + 6, 'grenade_in') for f in _idx] + [(116, 'gate_closed')],
        view=(0.6, 0.75, 0.45)),          # von links hinten: Ladeklappe links
}
EXPLODE = {'sight': (0, 110, 0), 'mechanism': (0, -60, 120), 'barrel': (130, 30, 0), 'ammo': (0, -60, -120), 'support': (130, -50, 0),
           'stock': (-110, 0, 0), 'grip_controls': (-10, -80, 0), 'receiver': (0, 0, 0)}
SIGHT_ID = 'W1'    # Visier des Baukastens v3 (visier-konzept › 6a); test_sights prüft dessen Pflichtteile und Merkmale
