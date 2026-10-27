"""BASIC-T01 v2.1 – Portalkanone im Stil v2.1 („Destiny-Detaildichte + AAA-Material, schlicht“): ein Werkzeug der Familie,
keine Waffe der 17 Grundtypen (0.17 „Gateway“).

Entscheidungen des Nutzers (26.10.2026): Werkzeug mit eigener Silhouette (kein Schaft, kein Magazin) · nur Hüfte, kein Visier,
oben eine Kerbe als Leitkante · zwei Portalfarben sichtbar, hinten Orange (Portal B), vorn Cyan (Portal A); Bedienelemente neutral,
damit Orange nur Portal B bedeutet · „mehr an der Portal-2-Portalgun orientieren, nur im BALLON-Stil“ → Skizze P1 „Ei und Klauen“
und dann P2 „Ei und Ring“ („Die Variante gefällt mir besser“; vorher A „Ring“) · nichts schwebt, der Ring dreht beim Schuss
eine Dritteldrehung.

Vorbild (beobachtet, nicht kopiert): Portal-2-Portalgun – weiße Eischale hinten, offen liegender Leuchtkern im Glas, gestufter
schwarzer Emitter mit heller Unterlippe. Die Klauen sind nicht übernommen (Nutzerwahl P2: Emitterring); Form, Proportionen, Facetten,
Griff und Farben folgen der Familie, kein Logo, kein Name.
Funktion aus Cube Escape (nur gelesen, docs/quellen.md › Q-CE-13 bis 16): Portal A Cyan `#1AD9FF`, Portal B Orange `#FF7314`;
Linksklick A, Rechtsklick B; kein Zielen mit Visier (X = „Präzision“); Abklingzeit 0,25 s, Reichweite 24 m.

Formsprache-Checkliste (stilhandbuch §3):
| Frage | Portalkanone v2.1 |
|---|---|
| Leitmerkmal der Silhouette | facettierte Eischale hinten, offener Zweifarbkern in der Mitte, gestufter Emitter, vorn offener Ring auf drei Speichen |
| Schichten | Eischale (Creme) auf Bauch (Graphit); Kernträger unter dem Glas; Ring auf Nabe und Achse; Unterlippe (Creme) unter dem Emitter |
| Negativraum | offener Kern zwischen Schale und Emitter (Glas, Kerne sichtbar von beiden Seiten); Durchblick durch den Ring |
| Blickfang | der Kern: hinten Portal B, vorn Portal A, getrennt durch einen blanken Ring |
| Zweiton-Blockung | Eischale und Unterlippe und Ring Lack (`shell`), Bauch und Vordergriff Polymer (`graphite`), Emitter, Nabe, Speichen `anodized` |
| Grafik | eine dunkle Marke auf der Ringstirn bei 12 Uhr (zeigt die Drehung), ein Schriftzug „BASIC PK-T01“ rechts am Bauch |
| Front | Emitter in drei Stufen mit blanker Krone; Achse mit Krone in der Nabe; Ring mit blanker Innenkante |
| Übergänge | blanker Stirnring, wo der Kern aus der Schale tritt; Kernträger verbindet Schale und Emitter, Achse trägt Nabe und Ring (nichts schwebt) |
| Ergonomie | Griff BGM-1 in v2.1-Form (`grip_v21`) unter dem Bauch, Vordergriff unter der Unterlippe; Kerbe oben auf der Schale statt Visier |

Schlichtheitsbudget: Leuchten 2 Funktionen (Kern A, Kern B) · Grafik 1 (Ringmarke) · Schrift 1 · Orange-Bedienelemente 0
(Orange ist hier Portal B) · keine Schrauben.
Laufzeit (nicht im Modell, wie das Aufgehen der Absehen): Beim Schuss leuchtet der Kern des Portals auf (`FLASH`); der Ring
dreht je Schuss um 120° weiter, A im, B gegen den Uhrzeigersinn (von hinten gesehen); die Winkel summieren sich.
Materialrollen `portal_a`/`portal_b`: hier registriert, weil `basic/kit.py` im Unity-Quellenhash liegt; beim nächsten vollen
Unity-Export nach `kit.MATERIALS` übernehmen.
Status: Maße entworfen (Toolgen-Bezug 0,606 m; gemessen siehe spec.json), Formprinzipien abgeleitet (Portal 2, Nutzerwunsch).
"""
import math

from basic.common import part, prof, cyl, cut_box, grip_v21, assemblies, R_BODY, R_MID, R_SMALL, R_FINE

PORTAL_ROLES = {   # emit_only: beleuchtete Grundfarbe wirkt pastellig; Cyan schwächer, sonst bleicht AgX es zu Hellblau (Runde 3)
    'portal_a': dict(color='#1AD9FF', rough=0.3, metal=0.0, emit=0.7, emit_only=True, de='Portal A Cyan (Kern, leuchtend; Cube Escape)'),
    'portal_b': dict(color='#FF7314', rough=0.3, metal=0.0, emit=1.2, emit_only=True, de='Portal B Orange (Kern, leuchtend; Cube Escape)'),
}
try:                                   # in Blender: Rollen ergänzen (ohne bpy, z. B. ./check, reicht die Tabelle)
    from basic import kit
    for _k, _v in PORTAL_ROLES.items():
        kit.MATERIALS.setdefault(_k, _v)
except ImportError:
    pass

META = dict(id='BASIC-T01', num='T01', type='portal_cannon', type_de='Portalkanone', type_en='Portal Cannon', variant='v2.1',
            name='Portalkanone v2.1', nick='Familie v2.1', ammo='none', fire='single', reference_length_m=0.606,
            reference_length_source='Toolgen Portalkanone (outputs/Portalkanone/README.md, Erstentwurf)',
            summary='Portalkanone mit Eischale, offenem Zweifarbkern und Emitterring (Werkzeug, Stil v2.1).')
ASSEMBLIES = assemblies('receiver', 'barrel', 'grip_controls', 'support')
B = 112               # Schussachse (Mitte von Schale, Kern und Emitter)
SEGS = 12             # Facetten der Eischale (BALLON-Stil: facettiert statt rund)
SHELL = [(-150, 18), (-138, 40), (-112, 55), (-62, 62), (-6, 61), (34, 51)]   # (f, Radius) entlang der Schale
CORE = (30, 132)      # Kernglas f
RING = (220, 242)     # Emitterring f (dreht)
RR, RI = 60, 48       # Ring außen / innen
SP_F = 231            # Ebene der Speichen


def _ring(f0, f1, r0, r1=None, segs=SEGS, r_in=None):
    d = dict(shape='cyl', axis='f', c=(B, 0), a0=f0, a1=f1, r=r0, r1=r0 if r1 is None else r1, segs=segs)
    if r_in:
        d['r_in'] = r_in
    return d


def _spoke(deg, r0=16, r1=RI + 2):
    """Speiche in der Ringebene; deg 0 = oben, im Uhrzeigersinn von hinten gesehen (x links positiv)."""
    a = math.radians(deg)
    return dict(shape='tube', path=[(SP_F, B + r0 * math.cos(a), -r0 * math.sin(a)), (SP_F, B + r1 * math.cos(a), -r1 * math.sin(a))],
                r=4.5)


P = [
    # ------------------------------------------------------------ Eischale, Bauch, Kern
    part('shell', 'Eischale', 'Egg shell', 'receiver', 'multi', 'shell', 'Hülle um Energiequelle und Elektronik; Leitkante oben',
         'auf den Bauch geschraubt', bevel=R_MID, smooth=False,        # Runde 1: glatt wirkte wie ein weiches Ei – Facetten wie Skizze P2
         items=[_ring(f0, f1, r0, r1) for (f0, r0), (f1, r1) in zip(SHELL, SHELL[1:])],
         cuts=[cut_box(-104, 36, B + 56, B + 70, 6)]),                               # Kerbe = Leitkante (kein Visier)
    cyl('shell_rim', 'Stirnring', 'Front rim', 'receiver', 'trim', 'Blanke Stirnkante, wo der Kern aus der Schale tritt',
        'vorn in die Schale gesetzt', 'f', (B, 0), CORE[0], CORE[0] + 6, 46, r_in=27, segs=SEGS * 2, bevel=0.6),
    prof('belly', 'Bauch', 'Belly', 'receiver', 'graphite', 'Trägt Schale, Kernträger und Griff; Abzugsgruppe',
         'unter die Schale geschraubt, Fuge 1 mm', [(-112, 72), (-84, 50), (-54, 40), (92, 40), (104, 56), (104, 80), (-112, 80)], 70),   # unten gerade über den Abzugsbügel
    cyl('core_glass', 'Kernglas', 'Core glass', 'receiver', 'glass_scope', 'Schützt den offen liegenden Kern (klar wie die Linse, 0.22: Kerne in Unity sichtbar)', 'zwischen Schale und Emitter',
        'f', (B, 0), CORE[0], CORE[1], 24, segs=32, bevel=0),
    cyl('core_b', 'Kern B', 'Core B', 'receiver', 'portal_b', 'Kern für Portal B (Orange, Rechtsklick); leuchtet beim Schuss auf',
        'hinten im Kernglas', 'f', (B, 0), CORE[0] + 4, 79, 11, segs=24, bevel=R_FINE),
    cyl('core_a', 'Kern A', 'Core A', 'receiver', 'portal_a', 'Kern für Portal A (Cyan, Linksklick); leuchtet beim Schuss auf',
        'vorn im Kernglas', 'f', (B, 0), 85, CORE[1] - 2, 11, segs=24, bevel=R_FINE),
    part('core_frame', 'Kernträger', 'Core frame', 'receiver', 'multi', 'anodized', 'Fasst Glas und Kerne; verbindet Schale und Emitter',
         'auf den Bauch geschraubt', bevel=R_SMALL,
         items=[_ring(78, 86, 26, segs=24), _ring(CORE[1] - 2, CORE[1] + 2, 27, segs=24),
                dict(shape='box', f0=CORE[0] - 4, f1=CORE[1] + 2, u0=B - 33, u1=B - 23, w=14)]),
    cyl('core_split', 'Trennring', 'Divider ring', 'receiver', 'trim', 'Blanke Trennung der beiden Kerne', 'auf dem Kernträger',
        'f', (B, 0), 80, 84, 27.5, r_in=24.5, segs=32, bevel=0.4),
    part('text_r', 'Schriftzug', 'Lettering', 'receiver', 'text', 'decal', 'Kennung „BASIC PK-T01“ (einzige Schrift)',
         'aufgedruckt', bevel=0, text='BASIC  PK-T01', size=5.0, f=-40, u=58, x=-35.05, side=-1, depth=0.12),
    # ------------------------------------------------------------ Emitter und Ring
    part('emitter', 'Emitter', 'Emitter', 'barrel', 'multi', 'anodized', 'Bündelt den Portalstrahl; drei Stufen',
         'auf den Kernträger geschraubt', bevel=R_SMALL,
         items=[_ring(CORE[1], 164, 34, segs=24, r_in=14), _ring(164, 174, 30, segs=24, r_in=14),
                _ring(174, 198, 36, segs=24, r_in=14), _ring(198, 206, 31, segs=24, r_in=22)]),
    cyl('emitter_bore', 'Bohrung', 'Bore', 'barrel', 'dark_metal', 'Innenrohr des Emitters; Austritt des Strahls',
        'im Emitter', 'f', (B, 0), 150, 204, 22, r_in=14, segs=24, bevel=0),
    cyl('crown', 'Emitterkrone', 'Emitter crown', 'barrel', 'trim', 'Blanke Stirnkante des Emitters', 'vorn am Emitter',
        'f', (B, 0), 205, 209, 31, r_in=23, segs=24, bevel=0.6),
    part('axle', 'Achse', 'Axle', 'barrel', 'multi', 'dark_metal', 'Trägt Nabe und Ring; Austritt des Strahls',
         'in der Emitterbohrung verschraubt (fest)', bevel=R_FINE,
         items=[_ring(190, 207, 14, segs=24, r_in=6), _ring(207, RING[1] + 8, 10, segs=24, r_in=6)]),   # füllt die Bohrung (r 14)
    cyl('axle_crown', 'Achskrone', 'Axle crown', 'barrel', 'trim', 'Blanke Stirnkante der Achse', 'vorn auf der Achse',
        'f', (B, 0), RING[1] + 8, RING[1] + 12, 11, r_in=6, segs=24, bevel=0.6),
    cyl('emitter_ring', 'Emitterring', 'Emitter ring', 'barrel', 'shell', 'Formt das Portal; dreht je Schuss um 120°',
        'auf drei Speichen an der Nabe; dreht auf der Achse', 'f', (B, 0), RING[0], RING[1], RR, r_in=RI, segs=SEGS * 4, bevel=R_MID,
        move=dict(kind='rotate', pivot=(SP_F, B, 0), axis='f', range_deg=(0, 120), event='fire',
                  expect=((SP_F, B + RR, 0), (0, -1, -1)))),
    cyl('ring_lip', 'Ringkante', 'Ring lip', 'barrel', 'trim', 'Blanke Innenkante des Rings', 'vorn innen am Ring', 'f', (B, 0),
        RING[1] - 1, RING[1] + 2, RI + 2.5, r_in=RI - 0.5, segs=SEGS * 4, bevel=0.4, parent_part='emitter_ring'),
    cyl('hub', 'Nabe', 'Hub', 'barrel', 'anodized', 'Lagert Ring und Speichen auf der Achse', 'auf der Achse (drehbar)',
        'f', (B, 0), RING[0] - 6, RING[1] - 2, 18, r_in=10, segs=24, bevel=R_SMALL, parent_part='emitter_ring'),
    part('spokes', 'Speichen', 'Spokes', 'barrel', 'multi', 'anodized', 'Tragen den Ring an der Nabe (nichts schwebt)',
         'zwischen Nabe und Ring', bevel=0, smooth=True, parent_part='emitter_ring', items=[_spoke(d) for d in (0, 120, 240)]),
    part('ring_mark', 'Ringmarke', 'Ring mark', 'barrel', 'box', 'anodized', 'Zeigt die Drehung des Rings (einziges Grafikelement)',
         'auf die Ringstirn gedruckt bei 12 Uhr', bevel=0, parent_part='emitter_ring', f0=RING[1] - 0.2, f1=RING[1] + 0.3,
         u0=B + RI + 3, u1=B + RR - 3, w=8),
    # ------------------------------------------------------------ Unterlippe und Stützhand
    prof('lip', 'Unterlippe', 'Lower lip', 'support', 'shell', 'Helle Schale unter dem Emitter; Übergang zum Vordergriff',
         'an den Kernträger geschraubt', [(96, 58), (150, 52), (198, 60), (214, 76), (206, 82), (170, 72), (122, 74), (96, 82)], 64,
         bevel=R_MID),
    prof('foregrip', 'Vordergriff', 'Foregrip', 'support', 'graphite', 'Senkrechter Griff der Stützhand; Socket_SupportHand',
         'unter die Unterlippe geschraubt', [(140, 56), (176, 56), (175, 26), (178, 10), (172, -10), (164, -16), (148, -16), (140, -8),
                                             (138, 10)], 26, bevel=R_BODY),
    prof('foregrip_pad', 'Griffpolster', 'Grip pad', 'support', 'rubber', 'Rutschfeste Front des Vordergriffs', 'vorn aufgeklebt',
         [(173, 48), (178, 48), (179.5, 12), (175, 12)], 22, bevel=R_FINE),
]
P += grip_v21(top=40)
for p in P:     # Nutzerhinweis „am Abzug sind die Teile in der Luft“: Bügel hinten in den Griff, Abzug oben in den Bauch (gemessen 2,7 / 1,0 mm)
    if p['id'] == 'trigger_guard':
        p['pts'] = [(f - 5, u) if i in (0, 5) else (f, u) for i, (f, u) in enumerate(p['pts'])]
    if p['id'] == 'trigger':
        p['pts'] = [(f, u + 2) if i in (0, 1) else (f, u) for i, (f, u) in enumerate(p['pts'])]
PARTS = P
ANCHORS = {
    'Socket_Hand': dict(at=(0, 0, 0), part='grip', note='Haupthand, auf der Griffachse'),
    'Socket_SupportHand': dict(at=(158, 20, 0), part='foregrip', note='Mitte Vordergriff'),
    'Socket_Muzzle': dict(at=(RING[1] + 12, B, 0), part='axle_crown', note='Stirn der Achskrone auf der Schussachse'),
}
FLASH = {   # Laufzeit: Aufleuchten des Kerns je Portal (Emission: Ruhe = Rolle, Spitze ×4; Bilder bei 30 fps)
    'fire_a': dict(part='core_a', role='portal_a', rest=0.7, peak=2.8, frames=(2, 10)),
    'fire_b': dict(part='core_b', role='portal_b', rest=1.2, peak=4.8, frames=(2, 10)),
}
ACTIONS = {
    'fire_a': dict(de='Portal A setzen (Linksklick): Ring dreht 120° im Uhrzeigersinn', frames=18, step=1, keys={
        'trigger': [(0, 0), (2, 1), (7, 1), (10, 0)], 'emitter_ring': [(0, 0), (2, 0), (12, 1), (18, 1)]},
        events=[(2, 'shot_a'), (16, 'ready')], view=(0.85, -0.3, 0.45)),
    'fire_b': dict(de='Portal B setzen (Rechtsklick): Ring dreht 120° gegen den Uhrzeigersinn', frames=18, step=1, keys={
        'trigger': [(0, 0), (2, 1), (7, 1), (10, 0)], 'emitter_ring': [(0, 0), (2, 0), (12, -1), (18, -1)]},
        events=[(2, 'shot_b'), (16, 'ready')], view=(0.85, -0.3, 0.45)),
}
EXPLODE = {'barrel': (110, 0, 0), 'support': (40, -80, 0), 'grip_controls': (-10, -80, 0), 'receiver': (0, 0, 0),
           'core_glass': (0, 0, 70), 'shell': (-60, 30, 0), 'shell_rim': (-60, 30, 0)}
HERO = (0.78, -0.50, 0.42)      # Hauptansicht von links vorn
# Ego-Griffe (0.22 „Volley“, basic/arms/ego.profile): Autorenmaß wie ego.GRIPS. Werkzeug ohne Magazin und Ladehebel: nur Griff und
# Stützhand am Vordergriff unter der Unterlippe (Faust wie an der MP, Daumen eingerollt).
EGO_GRIPS = {
    'grip':    dict(contact=(-3, -6, -16.5), palm=(0.15, 0.0, 1.0), fingers=(1.0, -0.06, 0.0), fingers_pose='trigger',
                    src='E wie die Pilotwaffe (Griff BGM-1 v2.1, gleiche Lage zu Socket_Hand)'),
    'support': dict(contact=(154, 16, 14.5), palm=(0.15, 0.0, -1.0), fingers=(1.0, -0.12, 0.0), fingers_pose='foregrip',
                    finger_map=dict(open='foregrip_open'),
                    src='E links am Vordergriff unter der Unterlippe (foregrip f 138–178, Breite 26; Socket_SupportHand 158/20), Faust um den '
                        'Griff wie an der MP (ego.FINGER_POSES foregrip, Nutzerwahl 0.18)'),
}
# Live-Teile: Abzug und Emitterring (dreht je Schuss um 120°, Laufzeit); kein Verschluss, keine Auswurfklappe
EGO_LIVE = dict(trigger='trigger', bolt='', port='', ring='emitter_ring')
