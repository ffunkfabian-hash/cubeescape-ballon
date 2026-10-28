"""BASIC-14 v2.1 – Raketenwerfer (Schulterrohr) im Stil v2.1 („Destiny-Detaildichte + AAA-Material, schlicht“), Familie des Piloten BASIC-01 v2.1.

Recherche (docs/quellen.md › Q-D2-IMG, gesichtet 28.10.2026, Bungie-Manifest): Palmyra-B und Morrigan-D (dickes Startrohr vorn,
schlankeres Heckrohr in anderer Farbe, Griffmodul unter dem Übergang, senkrechter Vordergriff unter dem Startrohr, Ringschellen,
Fenster in die Rakete; das Visier sitzt seitlich bzw. hinten, weil das dicke Rohr oben zu hoch wäre), Code Duello (langes Rohr mit
Seitenvisier; gerippte Hülle nicht übernommen), Bump in the Night und Sleepless (organische Schalen, Stacheln – nicht übernommen).
Nur Prinzipien; Leitmerkmal 14 nach Designvertrag: Schulterrohr.

Formsprache-Checkliste (stilhandbuch §3):
| Frage | Raketenwerfer v2.1 |
|---|---|
| Leitmerkmal der Silhouette | dickes gerades Creme-Startrohr (Ø 92) vorn, schlankes Graphit-Heckrohr (Ø 66) über der Schulter, kurzer Kegel dazwischen; Visier seitlich links am Startrohr auf einem Visierarm, Griff und Vordergriff hängen unter dem Rohr |
| Schichten | Heckrohr, Abzugsgehäuse, Vordergriff (Graphit) → Startrohr (Creme) → Schellen, Visierschelle mit Visierarm und Mündung (eloxiert/Metall) mit blanken Kanten → Schiene → Visier W2 |
| Negativraum | Sichtfenster links im Startrohr zeigt den orangen Gefechtskopf; freier Raum zwischen Griffmodul und Vordergriff unter dem Rohr; offene Heckdüse hinten |
| Blickfang | oranger Gefechtskopf im dunklen Sichtfenster auf der Creme-Fläche (Ego-Seite) – Kontrast ohne Leuchten |
| Zweiton-Blockung | Startrohr Lack (`shell`), Heckrohr, Abzugsgehäuse, Vordergriff Polymer (`graphite`), Schulterauflage `rubber`, Schellen (`ring_anod`, eloxiert ohne feine Kratzer), Mündung und Heckklappe `dark_metal`/`anodized` |
| Grafik | ein Ringband vorn am Startrohr, ein Schriftzug „BASIC RL-14“ (hell auf Graphit) |
| Front | mehrstufige Mündung: dunkler Mündungsring mit blanker Krone, innen ein Trichter auf die Bohrung – große dunkle Öffnung |
| Übergänge | Startrohr läuft hinten als Kegel in das Heckrohr; Schellen tragen Griffmodul, Vordergriff und den Visierarm (keine aufgesetzten Kästen) |
| Ergonomie | Griff BGM-1 in v2.1-Form (Familie) unter dem Übergang, senkrechter Vordergriff vor dem Fenster, Schulterauflage unter dem Heckrohr; Heckklappe schwenkt nach rechts (vom Gesicht weg) |

Visier: W2 „Entfernung“ (Baukasten v3, visier-konzept › 6a; `sight_kit.entfernung`), Visier-Standard 3 Typ `lens_chevron` (Reflex):
Haube 2,4 mm mit Schutzdach (oben 4 mm, 6 mm vorstehend) und leuchtendem Entfernungsfeld im Sockel; Größe M (26 × 18, 18,9 % der
Bildbreite); Absehen gezeichnet (Hüftform `circle_cross` flach im Glas); Weltzoom der Klasse 2,5 + 0,3 Reflexbonus (reticles).
Sitz **seitlich links** (Nutzer 28.10.2026: „Müsste das Visier vom raketenwerfer nicht eher an der Seite sitzen?“, dann „Seitlich links,
66 mm notfalls Bauteil dazu passend erfinden“): Visierlinie auf Achshöhe 66 mm links neben der Rohrachse (Visierhöhe als Abstand zur
Achse, 66 ± 4), Schiene BRI-22 auf einem Visierarm an einer Visierschelle um das Startrohr (`sight_kit.side_mount`). Wie bei Destiny
ragt das Rohr im Zielen rechts ins Fenster (bei 66 mm Abstand liegt die Rohrwand ≈ 20 mm neben der Visierlinie; erst ≈ 140 mm wären
frei); der Zielpunkt bleibt frei. W1 D-Linse in Größe L nur als Variante dokumentiert.
Schlichtheitsbudget: Leuchten 2 Funktionen (Munition: Bereitschaftsanzeige · Visier: Emitter, Entfernungsfeld und Absehen) · Grafik
1 Band · Schrift 1 · Orange 2 (Klappenknopf, Klemmhebel des Visiers; dazu der Gefechtskopf als Munitionskennung) · Schrauben nur an
Schellen und Heckring.
Proportion: Länge ≈ 0,91 m (v1 0,95 m), H/L ≈ 0,26 (Visier seitlich); Destiny-Raketenwerfer beobachtet (Bericht 0.28, grob aus 3/4-Bildern; Motiongen
Gjallarhorn 0,36).
Bewegung (Daten): Abzug und Bereitschaftsanzeige (`fire`); Klappenknopf, Heckklappe schwenkt um ein Scharnier rechts am Heckring nach
hinten rechts auf, Rakete von hinten eingeschoben, Klappe zu, Anzeige an (`reload`). **Kein Hülsenauswurf**: die Rakete verlässt das
Rohr ganz (`EJECT = None`; die Rakete trägt `caseless`, check: hülsenlose Munition → EJECT None).
Status: Maße entworfen (an Familie 15 angelehnt, Länge kürzer als v1; gemessene Werte im Spec), Formprinzipien abgeleitet.
"""
from basic.common import (part, prof, box, cyl, cut_box, screws, mirror, rail, grip_v21, R_BODY, R_MID, R_SMALL, R_FINE)
from basic.pilot import metal_roles  # noqa: F401  Rolle ring_anod (Schellen ohne feine Kratzer)
from basic.pilot.optics.sight_kit import entfernung, side_mount
from basic.weapons import w14_rocket_launcher as V1

META = dict(V1.META, variant='v2.1', name='Schulterrohr v2.1', nick='Familie v2.1',
            summary='Raketenwerfer mit dickem Startrohr, schlankem Heckrohr, Sichtfenster, Heckklappe und Visier W2 „Entfernung“ (Stil v2.1).')
ASSEMBLIES = V1.ASSEMBLIES
GRIP_TOP = 40
BORE = 112                   # Rohrachse
R_F, R_R, R_IN = 46.0, 33.0, 28.0    # Startrohr Ø 92, Heckrohr Ø 66, Bohrung Ø 56
SIDE = 66.0                  # Visier seitlich links: Visierlinie auf Achshöhe, 66 mm neben der Rohrachse (Visierhöhe als Abstand)
DECK = BORE - 26             # Schienenoberkante am Visierarm; Visierlinie u = BORE (Holo: Schiene + 26)
ARM = (2, 38)                # Visierarm f0, f1 (trägt die Schiene, endet vor der Schelle des Griffmoduls); Visierschelle um das Startrohr

CONE = (-14, 6)              # Kegel Heckrohr → Startrohr
FRONT1 = 444                 # Ende Startrohr; Mündungsring davor
MUZ = (440, 476)
REAR0 = -392                 # Ende Heckrohr; Heckring und Klappe dahinter
RING_R = R_R + 4
CLAMPS = (40, 248)           # Schellen (Griffmodul, Vordergriff), je 20 mm
WIN = (300, 372, BORE - 11, BORE + 11)   # Sichtfenster links auf den Gefechtskopf
HINGE = (REAR0 - 18, BORE, -(RING_R + 5))   # Scharnier der Heckklappe rechts am Heckring
R0, R1 = -360, 300           # Rakete: Heck, Beginn Gefechtskopf

P = []
# ---------------------------------------------------------------- Rohr (Leitmerkmal): Heckrohr, Kegel, Startrohr, Mündung
P += [
    cyl('rear_tube', 'Heckrohr', 'Rear tube', 'receiver', 'graphite', 'Schlankes Rohr über der Schulter; führt die Rakete beim Laden',
        'Grundkörper; im Startrohr verschraubt', 'f', (BORE, 0), REAR0, CONE[0] + 2, R_R, r_in=R_IN, segs=48, bevel=R_SMALL, smooth=True),
    cyl('tube_cone', 'Rohrkegel', 'Tube cone', 'receiver', 'shell', 'Übergang Heckrohr → Startrohr', 'hinten am Startrohr angeformt',
        'f', (BORE, 0), CONE[0], CONE[1], R_R + 0.6, r1=R_F, r_in=R_IN, segs=48, bevel=R_SMALL, smooth=True),
    cyl('tube', 'Startrohr', 'Launch tube', 'barrel', 'shell', 'Dickes Rohr; führt die Rakete; Sichtfenster links',
        'am Heckrohr verschraubt, Fuge 1 mm', 'f', (BORE, 0), CONE[1], FRONT1, R_F, r_in=R_IN, segs=48, bevel=R_SMALL, smooth=True,
        cuts=[cut_box(*WIN[:2], *WIN[2:], 30, x=R_F - 6)]),
    cyl('window_rim', 'Fensterrahmen', 'Window rim', 'barrel', 'dark_metal', 'Dunkler Rahmen in der Fensterlaibung',
        'in das Startrohr eingesetzt', 'f', (BORE, 0), WIN[0] - 4, WIN[1] + 4, R_IN + 4, r_in=R_IN, segs=48, bevel=R_FINE, smooth=True,
        cuts=[cut_box(WIN[0] + 3, WIN[1] - 3, WIN[2] + 3, WIN[3] - 3, 30, x=R_F - 6)]),
    cyl('muzzle', 'Mündungsring', 'Muzzle ring', 'barrel', 'dark_metal', 'Mündung mit Trichter; Socket_Muzzle', 'auf das Startrohr gepresst',
        'f', (BORE, 0), MUZ[0], MUZ[1], R_F + 4, r_in=R_IN, segs=48, bevel=R_SMALL, smooth=True,
        cuts=[dict(shape='cyl', axis='f', c=(BORE, 0), a0=MUZ[1] - 14, a1=MUZ[1] + 1, r=R_IN + 1, r1=R_F - 6, segs=48)]),   # Trichter
    cyl('muzzle_crown', 'Mündungskrone', 'Muzzle crown', 'barrel', 'trim', 'Blanke Stirnkante der Mündung', 'vorn am Mündungsring',
        'f', (BORE, 0), MUZ[1] - 2, MUZ[1] + 1.5, R_F + 3, r_in=R_F - 3, segs=48, bevel=0.5, smooth=True),
    cyl('band_ring', 'Ringband', 'Ring band', 'barrel', 'accent', 'Lackiertes Band (einziges Grafikelement)', 'lackiert',
        'f', (BORE, 0), 404, 418, R_F + 0.15, r_in=R_F - 1, segs=48, bevel=0, smooth=True),
]
# Schellen (dunkel, blanke Kanten) tragen Griffmodul und Vordergriff
for i, f0 in enumerate(CLAMPS):
    P.append(cyl(f'clamp_{i + 1}', f'Schelle {i + 1}', f'Clamp {i + 1}', 'support', 'ring_anod',
                 'Trägt ' + ('das Griffmodul' if i == 0 else 'den Vordergriff') + ' am Startrohr', 'um das Startrohr geschraubt',
                 'f', (BORE, 0), f0, f0 + 20, R_F + 3, r_in=R_F - 0.5, segs=48, bevel=R_FINE, smooth=True))
P += [
    part('clamp_rims', 'Schellenkanten', 'Clamp rims', 'support', 'multi', 'trim', 'Blanke Stirnkanten der Schellen', 'an den Schellen',
         bevel=0.3, smooth=True, items=[dict(shape='cyl', axis='f', c=(BORE, 0), a0=f0 + a, a1=f0 + a + 1.2, r=R_F + 3.4, r_in=R_F + 1,
                                             segs=48) for f0 in CLAMPS for a in (-0.4, 19.2)]),
    part('clamp_screws', 'Schellenschrauben', 'Clamp screws', 'support', 'multi', 'trim', 'Spannen die Schellen',
         'oben an den Schellen', bevel=0.2, items=mirror(screws([(f0 + 10, BORE + 26) for f0 in CLAMPS], R_F + 1.6, r=1.8, h=0.8))),
]
# ---------------------------------------------------------------- Heck: Heckring, Klappe mit Düse, Klappenknopf
P += [
    cyl('rear_ring', 'Heckring', 'Rear ring', 'mechanism', 'dark_metal', 'Trägt das Scharnier der Heckklappe', 'auf das Heckrohr gepresst',
        'f', (BORE, 0), REAR0 - 12, REAR0 + 10, RING_R, r_in=R_IN, segs=48, bevel=R_SMALL, smooth=True),
    box('hinge_block', 'Klappenscharnier', 'Breech hinge', 'mechanism', 'dark_metal', 'Lagert die Heckklappe rechts',
        'rechts am Heckring angeformt', REAR0 - 24, REAR0 - 6, BORE - 9, BORE + 9, 10, bevel=R_SMALL, x=HINGE[2] + 2),
    part('breech_cap', 'Heckklappe', 'Breech cap', 'mechanism', 'multi', 'anodized', 'Verschließt das Heck mit offener Düse; schwenkt zum Laden auf',
         'Scharnier rechts am Heckring', bevel=R_SMALL, smooth=True,
         items=[dict(shape='cyl', axis='f', c=(BORE, 0), a0=REAR0 - 26, a1=REAR0 - 12, r=RING_R - 1, r_in=R_IN - 6, segs=48),
                dict(shape='cyl', axis='f', c=(BORE, 0), a0=REAR0 - 40, a1=REAR0 - 25, r=R_IN - 2, r1=R_IN + 4, r_in=R_IN - 8, segs=48),
                dict(shape='box', f0=REAR0 - 24, f1=REAR0 - 14, u0=BORE - 6, u1=BORE + 6, w=8, x=HINGE[2] + 9)],
         move=dict(kind='rotate', pivot=HINGE, axis='u', range_deg=(0, 110), event='reload',
                   expect=((REAR0 - 26, BORE, 0), (-1, 0, -0.5)))),
    cyl('cap_rim', 'Düsenkante', 'Nozzle rim', 'mechanism', 'trim', 'Blanke Kante der Heckdüse', 'hinten an der Klappe',
        'f', (BORE, 0), REAR0 - 41, REAR0 - 39, R_IN + 4, r_in=R_IN + 1, segs=48, bevel=0.3, smooth=True, parent_part='breech_cap'),
    part('cap_release', 'Klappenknopf', 'Breech release', 'grip_controls', 'cyl', 'accent', 'Entriegelt die Heckklappe',
         'Druckknopf links am Heckring', bevel=R_FINE, axis='x', c=(REAR0 - 1, BORE + 10), a0=RING_R - 2, a1=RING_R + 3, r=4.5, segs=20,
         move=dict(kind='translate', pivot=(REAR0 - 1, BORE + 10, RING_R), vector_mm=(0, 0, -2.5), event='reload',
                   expect=((REAR0 - 1, BORE + 10, RING_R + 3), (0, 0, -1)))),
]
# ---------------------------------------------------------------- Abzugsgehäuse, Griff, Vordergriff, Schulterauflage
P += [
    prof('lower', 'Abzugsgehäuse', 'Trigger housing', 'receiver', 'graphite', 'Griffmodul und Abzugsgruppe unter dem Rohrübergang',
         'an der hinteren Schelle und am Heckrohr verschraubt',
         [(-48, 60), (-28, 40), (100, 40), (110, 50), (110, BORE - R_F + 3), (CONE[1], BORE - R_F + 3), (CONE[0], BORE - R_R + 2),
          (-48, BORE - R_R + 2)], 40),
    box('ready_light', 'Bereitschaftsanzeige', 'Ready light', 'receiver', 'energy', 'Leuchtet, wenn eine Rakete geladen ist',
        'links in das Abzugsgehäuse eingelassen', 30, 54, 52, 58, 1.0, bevel=0.3, x=20.2,
        move=dict(kind='glow', pivot=None, event='ready', max=5.0)),
    part('text_l', 'Schriftzug', 'Lettering', 'receiver', 'text', 'decal', 'Kennung „BASIC RL-14“ (einzige Schrift)',
         'aufgedruckt', bevel=0, text='BASIC  RL-14', size=5.0, f=68, u=45.5, x=20.05, side=1, depth=0.12),
    box('grip_mount', 'Griffträger', 'Foregrip mount', 'support', 'anodized', 'Verbindet den Vordergriff mit der Schelle',
        'unter der vorderen Schelle verschraubt', CLAMPS[1] - 6, CLAMPS[1] + 32, BORE - R_F - 8, BORE - R_F + 2, 24, bevel=R_SMALL),
    prof('foregrip', 'Vordergriff', 'Foregrip', 'support', 'graphite', 'Senkrechter Griff der Stützhand (Form wie BASIC-06)',
         'unter den Griffträger geschraubt', [(CLAMPS[1] - 2, BORE - R_F - 7), (CLAMPS[1] + 30, BORE - R_F - 7), (CLAMPS[1] + 28, 30),
                                             (CLAMPS[1] + 32, 20), (CLAMPS[1] + 28, 8), (CLAMPS[1] + 30, -6), (CLAMPS[1] + 20, -12),
                                             (CLAMPS[1], -12), (CLAMPS[1] - 4, -4)], 26, bevel=R_BODY),
    prof('foregrip_pad', 'Griffpolster', 'Grip pad', 'support', 'rubber', 'Rutschfeste Front des Vordergriffs', 'vorn aufgeklebt',
         [(CLAMPS[1] + 26, 50), (CLAMPS[1] + 31, 50), (CLAMPS[1] + 29, -4), (CLAMPS[1] + 24, -4)], 22, bevel=R_FINE),
    prof('shoulder_rest', 'Schulterauflage', 'Shoulder rest', 'stock', 'rubber', 'Liegt auf der Schulter',
         'unter das Heckrohr geschraubt', [(-344, BORE - R_R + 3), (-176, BORE - R_R + 3), (-180, BORE - R_R - 6), (-200, BORE - R_R - 18),
                                          (-232, BORE - R_R - 26), (-292, BORE - R_R - 26), (-326, BORE - R_R - 18), (-342, BORE - R_R - 6)],
         50, bevel=R_BODY),
]
P += grip_v21(top=GRIP_TOP)
# Visier W2 „Entfernung“ (Baukasten v3, Standard Raketenwerfer nach visier-konzept › 6a) seitlich links (Nutzer 28.10.2026: „Seitlich
# links, 66 mm notfalls Bauteil dazu passend erfinden“): Visierschelle um das Startrohr, Visierarm nach links, Schiene darauf
P += [
    cyl('sight_collar', 'Visierschelle', 'Sight collar', 'support', 'ring_anod', 'Trägt den Visierarm am Startrohr',
        'um das Startrohr geschraubt', 'f', (BORE, 0), ARM[0] + 6, ARM[1] - 6, R_F + 3, r_in=R_F - 0.5, segs=48, bevel=R_FINE, smooth=True),
    prof('sight_arm', 'Visierarm', 'Sight arm', 'support', 'anodized', 'Hält die Schiene 66 mm links neben der Rohrachse',
         'an der Visierschelle angeformt', [(ARM[0], DECK - 16), (ARM[1], DECK - 16), (ARM[1], DECK - 8), (ARM[0], DECK - 8)],
         SIDE + 11 - 28, bevel=R_SMALL, x=(SIDE + 11 + 28) / 2),
]
_rail = [dict(p, mat='anodized', x=SIDE, attach='auf dem Visierarm (fest)') for p in rail(ARM[0] - 2, ARM[0] + 48, DECK - 8)]
_rail[-1]['cuts'] = [cut_box(ARM[0] + 4 + 10 * i, ARM[0] + 9 + 10 * i, DECK - 4, DECK + 1, 30, x=SIDE) for i in range(4)]
P += _rail
_sight, SIGHT_ANCHORS = side_mount(*entfernung(ARM[0], DECK, weapon_type=V1.META['type']), SIDE)
P += _sight
# ---------------------------------------------------------------- Rakete (hülsenlos)
P += [
    part('rocket', 'Rakete', 'Rocket', 'ammo', 'multi', 'dark_metal', 'Eine Rakete im Rohr; verlässt das Rohr ganz (keine Hülse)',
         'im Rohr (Gefechtskopf im Sichtfenster)', bevel=R_SMALL, smooth=True, caseless=True,
         items=[dict(shape='cyl', axis='f', c=(BORE, 0), a0=R0, a1=R1, r=R_IN - 2, segs=32)]
         + [dict(shape='box', f0=R0, f1=R0 + 40, u0=BORE - 0.8, u1=BORE + 0.8, w=2 * (R_IN - 1)),
            dict(shape='box', f0=R0, f1=R0 + 40, u0=BORE - R_IN + 1, u1=BORE + R_IN - 1, w=1.6)],
         move=dict(kind='translate', pivot=(0, BORE, 0), vector_mm=(-920, 0, 0), event='reload', removable=True,
                   note='Ruhelage = geladen; die Ladeaktion schiebt sie von hinten durch das Heckrohr ein',
                   expect=((R0, BORE, 0), (-1, 0, 0)))),
    cyl('rocket_head', 'Gefechtskopf', 'Warhead', 'ammo', 'accent', 'Gefechtskopf (Munitionskennung), im Sichtfenster zu sehen',
        'vorn an der Rakete', 'f', (BORE, 0), R1, R1 + 90, R_IN - 2, r1=9, segs=32, bevel=R_SMALL, smooth=True, parent_part='rocket'),
]
PARTS = P
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip', note='Haupthand, auf der Griffachse'),
    'Socket_SupportHand': dict(at=(CLAMPS[1] + 14, 24, 0), part='foregrip', note='Mitte des Vordergriffs'),
    'Socket_Muzzle': dict(at=(MUZ[1] + 1.5, BORE, 0), part='muzzle_crown', note='Stirn der Mündungskrone auf der Rohrachse'),
    'Socket_Breech': dict(at=(REAR0 - 12, BORE, 0), part='rear_ring', note='Ladeöffnung hinten (Heckklappe offen)'),
}
ANCHORS.update(SIGHT_ANCHORS)
EJECT = None    # hülsenlos: die Rakete verlässt das Rohr ganz (Daten statt Sonderlogik; check: Teil mit caseless → EJECT None)
ACTIONS = {
    'fire': dict(de='Abschuss', frames=12, step=1, keys={'trigger': [(0, 0), (2, 1), (6, 0)],
                                                         'ready_light': [(0, 1), (2, 1), (4, 0), (12, 0)]},
                 events=[(2, 'launch')]),
    'reload': dict(de='Klappe öffnen, Rakete von hinten einschieben, schließen', frames=100, keys={
        'cap_release': [(0, 0), (4, 1), (10, 1), (14, 0)], 'breech_cap': [(0, 0), (6, 0), (20, 1), (72, 1), (86, 0)],
        'rocket': [(0, 1), (24, 1), (64, 0)], 'ready_light': [(0, 0), (86, 0), (90, 1), (100, 1)]},
        events=[(20, 'breech_open'), (64, 'rocket_in'), (86, 'breech_closed'), (90, 'ready')], view=(0.2, 0.85, 0.5)),
}
EXPLODE = {'sight': (0, 110, 0), 'mechanism': (-120, 0, -60), 'ammo': (0, 0, 130), 'barrel': (120, 0, 0), 'support': (60, -60, 0),
           'stock': (0, -70, 0), 'grip_controls': (-10, -80, 0), 'receiver': (0, 0, 0)}
SIGHT_ID = 'W2'    # Visier des Baukastens v3 (visier-konzept › 6a); test_sights prüft dessen Pflichtteile und Merkmale
