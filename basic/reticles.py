"""Absehen-Katalog BASIC (reines Python, kein bpy): Formen, Farben, Linienstärken, Aufgehen beim Schießen, einstellbare Optionen.

Nutzerwünsche 24.10.2026: „verschiedene Varianten … Fadenkreuz“, „einfach nur ein Punkt“, „verschiedene Farben und
Linienstärken“, „beim Schießen größer werden wie man das von Shootern kennt“, „dass das Pattern eingestellt werden kann“.
„Pfeil von unten“ wurde gebaut und wieder entfernt („sieht kacke aus“).

Eine Quelle für zwei Abnehmer: `basic/common.drawn_reticle()` baut daraus das flache Absehen im Visierglas (Blender; `reticle()` die
Röhrenform für Katalogblätter), `tools/export_reticles.py`
schreibt `data/reticles.json` für die Laufzeit (Unity zeichnet Absehen und Hüft-Fadenkreuz prozedural und lässt sie aufgehen).

Grundelemente in mm auf der Scheibe (Zielpunkt = 0,0; x nach links, u nach oben), bei Größe 1,0:
- `line`  a=(x,u), b=(x,u), `d`=(dx,du) Spreizrichtung (Einheitsvektor; (0,0) = bleibt stehen)
- `ring`  r außen, ri innen, `grow` 1 = Radius wächst mit der Spreizung, 0 = fest
- `dot`   r (bleibt immer stehen: Zielpunkt)
Spreizung s (mm): Linien wandern um s·d, Ringe wachsen um s·grow. Linienstärke und Ringdicke skaliert `weight`.
"""
import math

_D = 1 / math.sqrt(2)

RETICLES = {
    'ring_dot': dict(de='Ring mit Punkt', en='Ring and dot', use='Holo-Standard: schneller Fang im Ring, genauer Punkt',
                     prims=[dict(t='ring', r=3.2, ri=2.5, grow=1), dict(t='dot', r=0.8)]),
    'dot': dict(de='Leuchtpunkt', en='Dot', use='Minimal, verdeckt nichts; zeigt keine Spreizung',
                prims=[dict(t='dot', r=1.0)]),
    'cross': dict(de='Fadenkreuz', en='Crosshair', use='Vier Balken mit Lücke und Mittelpunkt; Balken wandern nach außen',
                  prims=[dict(t='line', a=(-7, 0), b=(-1.6, 0), d=(-1, 0)), dict(t='line', a=(1.6, 0), b=(7, 0), d=(1, 0)),
                         dict(t='line', a=(0, -7), b=(0, -1.6), d=(0, -1)), dict(t='line', a=(0, 1.6), b=(0, 7), d=(0, 1)),
                         dict(t='dot', r=0.45)]),
    'chevron': dict(de='Winkel', en='Chevron', use='Spitze ist der Zielpunkt, Haltepunkt bleibt frei; zeigt keine Spreizung',
                    prims=[dict(t='line', a=(-3.2, -2.6), b=(0, 0), d=(0, 0)), dict(t='line', a=(0, 0), b=(3.2, -2.6), d=(0, 0))]),
    't_post': dict(de='T-Balken', en='T-post', use='Waagerechte zeigt Verkanten; Balken und Stachel wandern nach außen',
                   prims=[dict(t='line', a=(-7, 0), b=(-1.4, 0), d=(-1, 0)), dict(t='line', a=(1.4, 0), b=(7, 0), d=(1, 0)),
                          dict(t='line', a=(0, -1.4), b=(0, -8), d=(0, -1)), dict(t='dot', r=0.4)]),
    'circle_cross': dict(de='Kreis mit Kreuzmarken', en='Circle with ticks', use='Großer Ring mit vier Marken; Ring und Marken gehen auf',
                         prims=[dict(t='ring', r=4.6, ri=4.0, grow=1)]
                         + [dict(t='line', a=(sx * 5.4, su * 5.4), b=(sx * 7.4, su * 7.4), d=(sx, su))
                            for sx, su in ((1, 0), (-1, 0), (0, 1), (0, -1))] + [dict(t='dot', r=0.6)]),
    'corners': dict(de='Eckklammern', en='Corner brackets', use='Vier Winkel zeigen die Streuung, gehen diagonal auf',
                    prims=[dict(t='line', a=(sx * 5, su * 5), b=(sx * 5, su * 3), d=(sx * _D, su * _D)) for sx in (1, -1) for su in (1, -1)]
                    + [dict(t='line', a=(sx * 5, su * 5), b=(sx * 3, su * 5), d=(sx * _D, su * _D)) for sx in (1, -1) for su in (1, -1)]
                    + [dict(t='dot', r=0.6)]),
    # Hüftformen nach Glidepath (Entscheidungsliste 4.2 A, 25.10.2026): Handfeuerwaffe „Klammern + Punkt“, Scharfschütze und
    # Automatik im Sprint „^“ (Motiongen destiny2 › Glidepath, [M])
    'brackets': dict(de='Klammern', en='Brackets', use='Zwei eckige Klammern um einen Punkt; Klammern wandern seitlich nach außen',
                     prims=[dict(t='line', a=(sx * 5, -3), b=(sx * 5, 3), d=(sx, 0)) for sx in (1, -1)]
                     + [dict(t='line', a=(sx * 5, su * 3), b=(sx * 3.8, su * 3), d=(sx, 0)) for sx in (1, -1) for su in (1, -1)]
                     + [dict(t='dot', r=0.6)]),
    'caret': dict(de='Dach', en='Caret', use='Kleines „^“, Spitze am Zielpunkt; die Schenkel gehen seitlich auseinander',
                  prims=[dict(t='line', a=(2.0, -1.6), b=(0, 0), d=(1, 0)), dict(t='line', a=(0, 0), b=(-2.0, -1.6), d=(-1, 0))]),
}
COLORS = {'cyan': ('Cyan', '#5FD3E0', 'Standard, Familienfarbe'), 'red': ('Rot', '#FF3D2E', 'klassischer Leuchtpunkt'),
          'green': ('Grün', '#38E06E', 'hell auf dunklem Grund'), 'amber': ('Bernstein', '#FFB01F', 'warm, gut auf Grau'),
          'white': ('Weiß', '#EEF2F5', 'neutral, für helle Skins dezent')}
WEIGHTS = {'fine': ('fein', 0.65), 'normal': ('normal', 1.0), 'bold': ('kräftig', 1.6)}
LINE_R = 0.3          # Linienradius bei Stärke „normal“ (mm)
# Visier-Standard v2 (Nutzerentscheidung 24.10.2026 „66 ± 4 mm, Augenpunkt, Zoom, Prüfung“; überarbeitet nach Nutzerhinweis
# „Visiere sehr klobig“ mit Destiny-Video und Motiongen-Messungen, docs/quellen.md › Q-D2-ADS):
# - Visierhöhe = Visierlinie (Socket_Eye) über der Laufachse, 66 ± 4 mm.
# - Socket_Eye = Augenpunkt beim Zielen, 90 mm hinter der vorderen Visieröffnung (Nutzer: „90 mm sieht ganz gut aus“): Reflex/Holo hinter dem Glas (Socket_Reticle),
#   Zielfernrohr hinter dem Objektivring (Socket_Objective); Teile mit `ads_hide` (Rohr, Okular) sind beim Zielen ausgeblendet.
# - Das Waffenmodell wird beim Zielen nicht vergrößert (viewmodel_zoom 1,0, eigene Viewmodel-Kamera); nur die Welt zoomt:
#   world_zoom = Klassengrundzoom (CLASS_ZOOM) + Visierbonus (zoom_bonus). Zielfernrohr: Linsenbild (Welt vergrößert in der Linse).
# Visier-Standard 3 (anfangs „Designsprache v3“; Nutzer 25.10.2026 „Mach alles so wie du empfiehlst“, Grundlage Motiongen REF 0.14 „Eyebox“ docs/visiere.md › 11):
# Öffnung im Zielen kleiner (Destiny: offene Visiere 12–20 % Bildbreite, Scout-Ring 21 %), Augenpunkt bleibt 90 mm (Nutzerwahl) –
# dafür kleinere Öffnungen; Bezugsbildwinkel 75° horizontal (der Anteil wächst mit dem Bildwinkel); Weltzoom ist ein
# Bildmaßstab (tan(Bildwinkel/2) wird durch den Zoom geteilt); eine Kamera: das Glas zeigt dasselbe Weltbild (kein eigenes
# Linsenbild, kostet Bildrate); Scharfschütze im Zielen als 2D-Vollbild mit eigener Kontur.
SIGHT = dict(height_mm=66.0, height_tol_mm=4.0, viewmodel_zoom=1.0, fov_ref_deg=75.0, zoom_kind='Bildmaßstab',
             types={'reflex': dict(de='Reflex-/Holovisier', eye_relief_mm=90.0, ref='Socket_Reticle', zoom_bonus=0.3,
                                   target_share=(0.12, 0.20), ads_view='glass', frame_max=0.10),
                    'scope': dict(de='Zielfernrohr', eye_relief_mm=90.0, ref='Socket_Objective', zoom_bonus=0.8,
                                  target_share=(0.20, 0.26), ads_view='glass', frame_max=0.15),
                    'fullscreen': dict(de='Vollbild (Scharfschütze)', ads_view='overlay', zoom_bonus=0.0,
                                       note='eigene Kontur je Waffe, außen schwarz')})
# Visier-Standard 3, Erweiterung 0.21 „Ironsight“ (Nutzerwahl 26.10.2026, docs/visier-konzept.md › 7 Punkte 3–4: „Tiefer, Schiene + 11 mm“,
# Größen „Zulassen für MG/Werfer“):
# - Visierlinie über der Schienenoberkante (BRI-22): Holo auf der H0-Plattform Schiene + 26 mm (Visierhöhe 66 ± 4 gilt); Zielfernrohre
#   nach Konzept A (Sattel hinter dem Auge, Fuß unter dem Objektiv, zwei Schienen auf eigener Höhe) richten sich nur nach der Visierhöhe;
#   Kimme/Korn (Handfeuerwaffe, Seitenwaffe, Schrot) Schiene + 11 mm und Mini-Reflex Schiene + 15 mm – dort gilt die Visierhöhe nicht.
# - Größen außerhalb des Standards sind zugelassene Varianten mit Grenzen: Holo L nur an MG und Werfern bis 25 % Bildbreite,
#   Zielfernrohr S ab 17 %. Standard je Typ bleibt Größe M.
# - Absehen gezeichnet (visier-konzept › 5): Hüftform der Klasse in Hüftgröße, flach in der Glasebene, Linien mindestens 1,6 px bei
#   1280 px Bildbreite (75°), reine Emission – Blender legt es als flaches Modellteil ins Glas (common.drawn_reticle), Unity zeichnet es.
SIGHT['rail_line_mm'] = {'holo': 26.0, 'mini_reflex': 15.0, 'iron': 11.0}
SIGHT['line_exempt'] = {'iron': ('hand_cannon', 'sidearm', 'shotgun'), 'mini_reflex': ('hand_cannon', 'sidearm')}
SIGHT['types']['reflex']['variants'] = {'L': dict(de='Holo L', share=(0.20, 0.25),
                                                  weapon_types=('machine_gun', 'grenade_launcher', 'rocket_launcher'))}
SIGHT['types']['scope']['variants'] = {'S': dict(de='Zielfernrohr S', share=(0.17, 0.20),
                                                 weapon_types=('scout_rifle', 'linear_fusion_rifle', 'pulse_rifle'))}
SIGHT['drawn'] = dict(ref_w_px=1280, min_line_px=1.6, plane_tol_mm=0.5, de='Hüftform der Klasse, flach in der Glasebene, reine Emission')


def share_band(sight_type, weapon_type=None, size='M'):
    """Zulässiger Bereich der Öffnung im Zielen (Anteil der Bildbreite): Standard, für Größe `size` auch die zugelassene Variante
    (nur an den genannten Waffentypen; ohne Waffentyp – Baukasten – jede). Gibt (lo, hi, Name) zurück."""
    T = SIGHT['types'][sight_type]
    V = T.get('variants', {}).get(size)
    if V and (weapon_type is None or weapon_type in V['weapon_types']):
        lo, hi = T['target_share']
        return min(lo, V['share'][0]), max(hi, V['share'][1]), V['de']
    return (*T['target_share'], 'Standard')
# Visiertyp je Waffentyp (Form nach Visiertyp, Farbe nach Familie/Hersteller – Destiny-Muster, REF 0.14 › 3)
SIGHT_KIND = {'auto_rifle': 'holo', 'submachine_gun': 'holo', 'trace_rifle': 'holo', 'machine_gun': 'holo', 'pulse_rifle': 'holo',
              'scout_rifle': 'ring_scope', 'linear_fusion_rifle': 'ring_scope', 'hand_cannon': 'irons_brackets',
              'sidearm': 'irons_brackets', 'shotgun': 'irons_brackets', 'sniper_rifle': 'fullscreen', 'fusion_rifle': 'ring',
              'grenade_launcher': 'lens_chevron', 'rocket_launcher': 'lens_chevron', 'combat_bow': 'arrow_tip', 'sword': None,
              'glaive': None, 'portal_cannon': None}
SIGHT_KIND_DE = {'holo': 'offenes Holo (abgerundetes Rechteck)', 'ring_scope': 'kurzes Ring-Zielfernrohr, Sattel hinter dem Auge, Fuß unter dem Objektiv',
                 'irons_brackets': 'Kimme und Korn mit leuchtenden Klammern', 'fullscreen': 'Zielfernrohr außen, im Zielen Vollbild',
                 'ring': 'Ring oder Doppelring', 'lens_chevron': 'runde Linse mit Winkel', 'arrow_tip': 'Pfeilspitze, kein Visier',
                 None: 'kein Visier'}
# Im Zielen (Destiny, REF 0.14 › 7): Leuchtpunkt am Zielpunkt getrennt vom Glas, kein Aufgehen, Schuss = kurzer Ring, Treffer = X
ADS_FEEDBACK = dict(hud_dot=dict(share_h=0.011, color='cyan'), shot_ring=dict(share_h=0.02, frames=1),
                    hit_x=dict(share_h=0.045, min_s=0.17), spread_in_ads=0.0)
# Grundzoom der Welt beim Zielen je Waffentyp (Destiny 2, Q-D2-ZOOM; „entworfen“ = keine Messung, abgeleitet).
# Entscheidungsliste 1.2 A (Nutzer 25.10.2026): Weltzoom an die Glidepath-Messung (Motiongen destiny2 › Glidepath, [M]) angeglichen –
# Scout 2,9 → 2,0 (Grundzoom 1,2 + Zielfernrohr 0,8), Handfeuerwaffe 1,5 → 1,15, MP 1,25 → 1,45; übrige Klassen unverändert.
CLASS_ZOOM = {'auto_rifle': 1.6, 'pulse_rifle': 1.7, 'scout_rifle': 1.2, 'hand_cannon': 1.15, 'sidearm': 1.25, 'submachine_gun': 1.45,
              'shotgun': 1.25, 'grenade_launcher': 1.4, 'sniper_rifle': 5.5, 'fusion_rifle': 1.5, 'linear_fusion_rifle': 3.0,
              'trace_rifle': 1.5, 'rocket_launcher': 2.5, 'machine_gun': 1.6, 'combat_bow': 1.5, 'sword': 1.0, 'glaive': 1.25}
CLASS_ZOOM_STATUS = {k: 'beobachtet' for k in ('auto_rifle', 'pulse_rifle', 'scout_rifle', 'hand_cannon', 'sidearm', 'submachine_gun',
                                               'shotgun', 'grenade_launcher', 'sniper_rifle')}
CLASS_ZOOM_STATUS.update({k: 'gemessen (Glidepath)' for k in ('scout_rifle', 'hand_cannon', 'submachine_gun')})


def world_zoom(weapon_type, sight_type):
    """Zoom der Welt beim Zielen: Klassengrundzoom + Visierbonus (MP, Seitenwaffe, Schrotflinte: kein Bonus, wie Destiny)."""
    base = CLASS_ZOOM[weapon_type]
    no_bonus = weapon_type in ('submachine_gun', 'sidearm', 'shotgun', 'hand_cannon', 'grenade_launcher', 'sniper_rifle')
    return round(base + (0.0 if no_bonus else SIGHT['types'][sight_type]['zoom_bonus']), 2)


def sight_type(weapon_type):
    """Visiertyp aus SIGHT['types'] für den Weltzoom eines Waffentyps (Zielfernrohr bei Ring-Zielfernrohren, sonst Reflex)."""
    kind = SIGHT_KIND[weapon_type]
    return 'scope' if kind == 'ring_scope' else 'fullscreen' if kind == 'fullscreen' else 'reflex'


def class_world_zoom(weapon_type):
    """Weltzoom beim Zielen mit dem Visier, das der Waffentyp nach Visier-Standard 3 trägt (Laufzeit: ego.json › gameplay)."""
    return world_zoom(weapon_type, sight_type(weapon_type))


# Glasvarianten der Reflexscheibe (Rolle glass_<id>, Wirkung in kit.glass_fx; v3: nur am Rand, Mitte klar, höchstens +0,15 Deckkraft)
GLASS = {'clean': ('Klar', 'unbehandelt beschichtet, Tönung ≤ 5 %'), 'dust': ('Staub', 'feine Körner (~0,3 mm), jede siebte Zelle'),
         'scratch': ('Kratzer', 'dünne, schräg gestreckte Linien'), 'crack': ('Riss', 'feines Rissnetz, nur obere Ecke'),
         'cells': ('Zellen', 'kaum sichtbare Zellvergütung über die Scheibe'), 'worn': ('Benutzt', 'Staub und Kratzer')}

# Aufgehen beim Schießen (entworfen, an Shooter-Konventionen angelehnt): Spreizung s in mm auf der Scheibe bei Größe 1,0.
# s folgt base + Σ Schussimpulse, begrenzt auf max, klingt mit Zeitkonstante recover_s ab; Laufen addiert move, Zielen
# multipliziert mit ads – v3: im Zielen 0 (Destiny: kein Aufgehen, stattdessen Schuss-Ring, ADS_FEEDBACK); das Aufgehen gilt dem
# Hüft-Fadenkreuz. charge: Spreizung schrumpft während des Aufladens auf base.
SPREAD = {
    'auto':      dict(de='Dauerfeuer', base=0.0, per_shot=0.9, max=5.0, recover_s=0.28, move=1.5, ads=0.0),
    'burst':     dict(de='Salve', base=0.0, per_shot=1.2, max=4.5, recover_s=0.22, move=1.4, ads=0.0),
    'precision': dict(de='Präzision', base=0.0, per_shot=2.2, max=3.5, recover_s=0.18, move=1.0, ads=0.0),
    'shotgun':   dict(de='Schrot', base=2.0, per_shot=2.5, max=6.0, recover_s=0.35, move=1.0, ads=0.0),
    'charge':    dict(de='Aufladen', base=0.0, per_shot=1.5, max=4.0, recover_s=0.25, move=1.2, ads=0.0, charge_from=4.0),
    'explosive': dict(de='Sprengwaffe', base=0.5, per_shot=1.8, max=4.0, recover_s=0.5, move=0.8, ads=0.0),
    'none':      dict(de='kein Aufgehen', base=0.0, per_shot=0.0, max=0.0, recover_s=0.2, move=0.0, ads=0.0),
}
# Vorgabe je Waffentyp (META['type']): Absehen im Visier (Optik) und Hüft-Fadenkreuz (HUD) mit Aufgehverhalten
DEFAULTS = {
    'auto_rifle':          dict(optic='ring_dot', hip='ring_dot', spread='auto'),
    'pulse_rifle':         dict(optic='circle_cross', hip='ring_dot', spread='burst'),
    'scout_rifle':         dict(optic='chevron', hip='cross', spread='precision'),
    'hand_cannon':         dict(optic='dot', hip='brackets', spread='precision'),
    'sidearm':             dict(optic='dot', hip='cross', spread='auto'),
    'submachine_gun':      dict(optic='dot', hip='circle_cross', spread='auto'),
    'shotgun':             dict(optic='corners', hip='corners', spread='shotgun'),
    'sniper_rifle':        dict(optic='t_post', hip='caret', spread='precision'),
    'fusion_rifle':        dict(optic='t_post', hip='corners', spread='charge'),
    'linear_fusion_rifle': dict(optic='t_post', hip='cross', spread='charge'),
    'trace_rifle':         dict(optic='corners', hip='circle_cross', spread='auto'),
    'grenade_launcher':    dict(optic='chevron', hip='circle_cross', spread='explosive'),
    'rocket_launcher':     dict(optic='circle_cross', hip='circle_cross', spread='explosive'),
    'machine_gun':         dict(optic='circle_cross', hip='ring_dot', spread='auto'),
    'combat_bow':          dict(optic='dot', hip='chevron', spread='charge'),
    'sword':               dict(optic=None, hip='dot', spread='none'),
    'glaive':              dict(optic=None, hip='cross', spread='auto'),
    # Werkzeug (0.22): kein Visier; Hüftform Ring mit Punkt (Portal 2: Halbkreise um die Mitte, Cube Escape: Fadenkreuz), ohne Aufgehen
    'portal_cannon':       dict(optic=None, hip='ring_dot', spread='none'),
}
# Hüft-Fadenkreuz (HUD), Entscheidungsliste 4.1 A / 4.2 A (Nutzer 25.10.2026), Maße nach Glidepath (Motiongen destiny2 › Glidepath,
# [M], je 1 Clip in der Hüfte): Größe = sichtbares Außenmaß der Form bei Spreizung 0 mit Linienstärke (größere Seite des Rahmens,
# siehe extent_mm) als Anteil der Bildhöhe. Weiß, Linienstärke fein. Sichtbar nur in der Hüfte (auch geduckt und in der Luft); aus beim Zielen
# (schon im ersten Bild), im Sprint (Automatik: nur „^“), beim Nachladen, Ziehen, Wegstecken, Betrachten und bei gesenkter Waffe.
# Beim Schießen geht es nach SPREAD auf (Profil aus DEFAULTS); das „^“ im Sprint ist ein Haltungszeichen und geht nicht auf. Glidepath-Werte anderer Typen (Bogen 4,6 % H, kurze Fusion 5,5 %,
# lineare Fusion 12–13 %, Granatwerfer 5,6 % H) folgen mit Form beim Ego-Übertrag je Klasse (Entscheidungsliste Schritt 6).
HIP = dict(color='white', weight='fine', share_h={'auto_rifle': 0.032, 'pulse_rifle': 0.032, 'machine_gun': 0.032,
                                                  'submachine_gun': 0.061, 'hand_cannon': 0.06, 'sniper_rifle': 0.01},
           share_h_default=0.045, min_line_px=0.6,
           sprint={'auto_rifle': dict(kind='caret', share_h=0.015)},
           hidden_in=('ads', 'sprint', 'reload', 'draw', 'holster', 'inspect', 'lowered'))
HIP_STATUS = {'auto_rifle': 'gemessen (Glidepath)', 'submachine_gun': 'gemessen (Glidepath, 5,9–6,3 % H)',
              'hand_cannon': 'gemessen (Glidepath, ≈ 6 % H)', 'sniper_rifle': 'gemessen (Glidepath, ≈ 1 % H)',
              'pulse_rifle': 'übertragen (Automatik)', 'machine_gun': 'übertragen (Automatik)',
              'portal_cannon': 'entworfen (Werkzeug, Portal 2 / Cube Escape)'}


def extent_mm(kind, weight=None):
    """Außenmaß einer Form bei Spreizung 0 (mm): größere Seite des Rahmens um alle Grundelemente. Mit `weight` (Faktor aus WEIGHTS)
    das sichtbare Maß wie gezeichnet (common.reticle, Unity HipReticle): Linien ± LINE_R·weight (runde Enden), Ringe außen
    ri + (r − ri)·weight, Punkte r·(0,5 + 0,5·weight); ohne `weight` die Mittellinien und r."""
    xs, us = [], []
    lw = LINE_R * weight if weight is not None else 0.0
    for p in RETICLES[kind]['prims']:
        if p['t'] == 'line':
            xs += [min(p['a'][0], p['b'][0]) - lw, max(p['a'][0], p['b'][0]) + lw]
            us += [min(p['a'][1], p['b'][1]) - lw, max(p['a'][1], p['b'][1]) + lw]
        else:
            r = p['r'] if weight is None else p['ri'] + (p['r'] - p['ri']) * weight if p['t'] == 'ring' else p['r'] * (0.5 + 0.5 * weight)
            xs += [-r, r]
            us += [-r, r]
    return round(float(max(max(xs) - min(xs), max(us) - min(us))), 4)


def hip(weapon_type):
    """Hüft-Fadenkreuz eines Waffentyps: Form, Größe (Anteil der Bildhöhe), Außenmaß in mm, Aufgehprofil, Sprintform (oder None)."""
    D = DEFAULTS[weapon_type]
    sp = HIP['sprint'].get(weapon_type)
    w = WEIGHTS[HIP['weight']][1]
    return dict(kind=D['hip'], share_h=HIP['share_h'].get(weapon_type, HIP['share_h_default']), extent_mm=extent_mm(D['hip'], w),
                spread=D['spread'], status=HIP_STATUS.get(weapon_type, 'entworfen'),
                sprint=dict(sp, extent_mm=extent_mm(sp['kind'], w)) if sp else None)


# Einstellbare Optionen (Spieler): Wertebereich und Vorgabe
SETTINGS = {
    'kind':       dict(de='Form', values=list(RETICLES), default='Vorgabe der Waffe'),
    'color':      dict(de='Farbe', values=list(COLORS), default='cyan'),
    'weight':     dict(de='Linienstärke', values=list(WEIGHTS), default='fine'),
    'scale':      dict(de='Größe', min=0.6, max=1.6, default=1.0),
    'opacity':    dict(de='Deckkraft', min=0.3, max=1.0, default=0.9),
    'center_dot': dict(de='Mittelpunkt', values=[True, False], default=True),
    'spread':     dict(de='Aufgehen beim Schießen', values=[True, False], default=True),
    'glass':      dict(de='Glas', values=list(GLASS), default='clean'),
    # Nutzer 25.10.2026: „Wir nehmen die 90 mm. Wären die 70 mm optional möglich?“ – Standard bleibt 90 mm (Modelle, Prüfung);
    # die Option rückt das Waffenmodell beim Zielen um (90 − Wert) mm entlang der Visierlinie näher an die Kamera (Laufzeit).
    'ads_eye_relief': dict(de='Visiernähe beim Zielen (mm)', values=[70, 90, 110], default=90),
}


def prims_at(kind, spread=0.0, center_dot=True):
    """Grundelemente einer Form mit Spreizung s (mm) angewendet; center_dot=False lässt Punkte weg, außer bei 'dot'."""
    out = []
    for p in RETICLES[kind]['prims']:
        if p['t'] == 'line':
            dx, du = p['d']
            out.append(dict(p, a=(p['a'][0] + spread * dx, p['a'][1] + spread * du), b=(p['b'][0] + spread * dx, p['b'][1] + spread * du)))
        elif p['t'] == 'ring':
            g = spread * p['grow']
            out.append(dict(p, r=p['r'] + g, ri=p['ri'] + g))
        elif center_dot or kind == 'dot':
            out.append(dict(p))
    return out


def simulate(spread_id, shots_s, t_end, fps=30, moving=False, ads=False):
    """Spreizung je Bild für Schusszeiten (s): Impuls je Schuss, Begrenzung, exponentielles Abklingen (wie die Laufzeit)."""
    S = SPREAD[spread_id]
    s, out, k = S['base'], [], 0
    shots = sorted(shots_s)
    for i in range(int(round(t_end * fps)) + 1):
        t = i / fps
        tgt = S['base'] + (S['move'] if moving else 0.0)
        s = tgt + (s - tgt) * math.exp(-(1 / fps) / S['recover_s'])
        while k < len(shots) and shots[k] <= t:
            s = min(S['max'], s + S['per_shot'])
            k += 1
        out.append(s * (S['ads'] if ads else 1.0))
    return out
