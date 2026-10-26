"""Visier-Konzepte nach 0.20 „Spotter“ – Zielbild-Varianten für Holo (BASIC-01 v2.1) und Zielfernrohr (BASIC-03 v2.1).

Anlass und Nutzerzitate: docs/uebergabe-visier-konzept.md; Ergebnis und Bilder: docs/visier-konzept.md. Nur Entwurf für die
Nutzerwahl: die Waffenmodule und `common.py` (Unity-Quellenhash) bleiben unverändert, gebaut wird die gewählte Variante in einer
eigenen Version. Aufruf über `variant(concept, weapon)` mit concept 'hals'|'grat'|'offen', weapon 'holo'|'scope'.

Gemeinsam (Befund Motiongen visiere.md › 2/5/7, Destiny-Scout im Zielen, Video 1ERmScNiOk4):
- Im Zielen steht zwischen Auge und Ring nichts Waagerechtes nahe der Visierlinie; unter dem Ring sieht man einen schmalen, dunklen
  Hals, der nach unten breiter wird, darunter erst die Waffe.
- Ring ohne Wulst: Objektiv als langer Kegel zum Auge hin (r/d ≤ Ring/90 mm, f 30–64), so zeigt sich im Zielen nur die Stirnfläche; außen/innen
  18/14 = 1,29 (Destiny 1,28–1,30). Ring und Hals Graphit, blanke Innenkante als dünne Linie.
- Visierteile in einer dunklen Rolle ohne Kantenabrieb (`sight_dark`, nur im Entwurf von tools/sight_options.py angelegt): die
  Abriebmaske misst mit 4 mm Radius und färbt dünne Teile (Ring, Hals, Rahmen) ganz hellgrau-marmoriert.
- Absehen gezeichnet: flach, Hüftform der Klasse in Hüftgröße (wie Unity seit 0.20), tools/sight_options.py legt es ins Glas.
"""
import types

from basic.common import part, box, cyl, rail, screws
from basic.pilot import w01_auto_rifle_v21 as A
from basic.pilot import w03_scout_rifle_v21 as S
from basic.reticles import SIGHT

CONCEPTS = [('hals', 'A „Hals“', 'Destiny-nah: schmaler dunkler Hals unter Ring und Fenster, Sattel hinter dem Auge'),
            ('grat', 'B „Grat“', 'Rohr bleibt auf dem Gehäuse (0.19): schmaler dunkler Grat, vor dem Auge abgeschrägt'),
            ('offen', 'C „Offen“', 'Häkke/VEIST: offener Ring und offenes Fenster auf zwei dünnen Beinen, nichts in der Mitte')]
REL = SIGHT['types']['scope']['eye_relief_mm']

# ------------------------------------------------------------------------------------------------ Zielfernrohr (Scout)
F_EYE, F_OBJ, CU = -48, 72, S._cu          # Okularende, Objektivstirn, Visierlinie (u 161) wie 0.19
EYE = F_OBJ - REL                          # Augenpunkt f −18
R_IN, R_OUT = 14.0, 18.0                   # lichte Öffnung, Ring außen (1,29)


def _scope_common(open_ring=False):
    """Rohr, Okular, Türme (ads_hide), Objektiv ohne Wulst, Glas. Ohne Hals/Sattel."""
    P = [
        cyl('scope_tube', 'Mittelrohr', 'Scope tube', 'sight', 'sight_dark', 'Verbindet Okular und Objektiv; hohl', 'auf dem Sattel (fest)',
            'f', (CU, 0), F_EYE + 20, 32, 9.5, r_in=8.0, segs=40, ads_hide=True),
        cyl('scope_eyepiece', 'Okular', 'Eyepiece', 'sight', 'sight_dark', 'Augenseite, schlank', 'am Mittelrohr (fest)',
            'f', (CU, 0), F_EYE, F_EYE + 22, 11, r1=10, r_in=9, segs=40, ads_hide=True),
        cyl('scope_eye_trim', 'Okularkante', 'Eyepiece trim', 'sight', 'trim', 'Blanke Kante am Okular', 'hinten am Okular',
            'f', (CU, 0), F_EYE - 1, F_EYE + 1.5, 11.4, r_in=9.5, segs=40, bevel=0.3, ads_hide=True),
        cyl('scope_turret', 'Höhenturm', 'Elevation turret', 'sight', 'accent', 'Höhenverstellung (Bedienelement)',
            'oben am Mittelrohr (fest)', 'u', (4, 0), CU + 7.5, CU + 15.5, 5.5, segs=32, ads_hide=True),
        cyl('scope_turret_w', 'Seitenturm', 'Windage turret', 'sight', 'anodized', 'Seitenverstellung', 'rechts am Mittelrohr (fest)',
            'x', (4, CU), -7.5, -14.5, 4.5, segs=32, ads_hide=True),
        cyl('scope_ocular_glass', 'Okularlinse', 'Ocular lens', 'sight', 'glass_scope', 'Augenlinse', 'im Okular (fest)', 'f', (CU, 0),
            F_EYE + 3, F_EYE + 4, 9, segs=40, bevel=0, ads_hide=True),
        cyl('scope_glass', 'Objektivlinse', 'Objective lens', 'sight', 'glass_scope', 'Linse vorn (im Zielen dasselbe Weltbild)',
            'im Objektiv (fest)', 'f', (CU, 0), F_OBJ - 6, F_OBJ - 5, R_IN, segs=48, bevel=0),
    ]
    if open_ring:   # Häkke-Ring: Lücke oben, dünner Rundstab; Kegel dahinter schmal und vorn offen
        import math
        arc = [(F_OBJ - 2, CU + 15.8 * math.sin(math.radians(a)), 15.8 * math.cos(math.radians(a))) for a in range(115, 426, 10)]
        P += [part('scope_rim', 'Offener Ring', 'Open ring', 'sight', 'tube', 'sight_dark', 'Dünner Ring mit Lücke oben (Häkke)',
                   'vorn auf dem Objektiv', bevel=0, path=arc, r=1.7),
              cyl('scope_objective', 'Objektiv', 'Objective bell', 'sight', 'sight_dark', 'Schlanker Kegel, im Zielen hinter dem Ring',
                  'am Mittelrohr (fest)', 'f', (CU, 0), 30, F_OBJ - 4, 9.6, r1=14.6, r_in=8.2, segs=48, bevel=0.4)]
    else:
        P += [cyl('scope_objective', 'Objektiv', 'Objective bell', 'sight', 'sight_dark',
                  'Kegel zum Auge hin: im Zielen hinter der Stirnfläche verborgen (kein Wulst)', 'am Mittelrohr (fest)',
                  'f', (CU, 0), 30, F_OBJ - 8, 9.6, r1=16.0, r_in=8.2, segs=48, bevel=0.4),
              cyl('scope_rim', 'Objektivring', 'Objective ring', 'sight', 'sight_dark', 'Dünner Ring, außen/innen 1,29',
                  'vorn auf dem Objektiv', 'f', (CU, 0), F_OBJ - 8, F_OBJ, 16.2, r1=R_OUT, r_in=R_IN, segs=64, bevel=0.5),
              cyl('scope_crown', 'Objektivkante', 'Objective trim', 'sight', 'trim', 'Blanke Innenkante als dünne Linie',
                  'innen am Ring', 'f', (CU, 0), F_OBJ - 5, F_OBJ + 0.1, R_IN + 0.6, r_in=R_IN, segs=64, bevel=0.1)]
    return P


def _scope_anchors():
    return {'Socket_Sight': dict(at=(F_EYE, CU, 0), part='scope_eyepiece', note='hinteres Okularende auf der Visierlinie'),
            'Socket_Objective': dict(at=(F_OBJ, CU, 0), part='scope_rim', note='Stirn des Objektivrings'),
            'Socket_Reticle': dict(at=(F_OBJ - 6, CU, 0), part='scope_glass', note='gezeichnetes Absehen in der Linsenebene'),
            'Socket_Eye': dict(at=(EYE, CU, 0), part='scope_objective', sight_type='scope', std=True,
                               note=f'Augenpunkt beim Zielen ({REL:.0f} mm hinter dem Objektivring, ads_hide-Teile aus)')}


def _scout_receiver(top):
    r = S.receiver(seat=False)
    pts = [q for q in r['pts'] if q[1] != S.TOP]                 # Oberkante ersetzen
    i = pts.index((200, 116)) + 1
    r['pts'] = pts[:i] + top + pts[i:]
    return r


def _scope_hals():
    """A: Rohr hinten auf einem Buckel hinter dem Auge (Sattel unsichtbar im Zielen), vorn ein schmaler Hals unter dem Objektiv."""
    hump = S.HUMP
    rec = _scout_receiver([(194, S.TOP), (6, S.TOP), (-22, hump), (-50, hump), (-70, S.TOP), (-112, S.TOP)])
    seat = CU - 9.5 - 0.3
    P = [rec] + [dict(p, mat='anodized', attach='auf dem Buckel hinter dem Auge (fest)') for p in rail(-50, -24, hump)]
    P += [part('scope_mount_r', 'Rohrsattel', 'Scope saddle', 'sight', 'multi', 'anodized',
               'Trägt das Rohr hinten auf der Schiene BRI-22 (hinter dem Augenpunkt, im Zielen unsichtbar)',
               'Klemmung auf Schiene (lösbar)', bevel=1.0, iface='BRI-22',
               items=[dict(shape='box', f0=-46, f1=-28, u0=hump + 0.5, u1=seat, w=26)]),
          cyl('scope_strap', 'Spannband', 'Scope strap', 'sight', 'anodized', 'Hält das Rohr im Sattel', 'um das Mittelrohr',
              'f', (CU, 0), -43, -31, 11.1, r_in=9.5, segs=40),
          part('scope_neck', 'Objektivhals', 'Objective neck', 'sight', 'multi', 'sight_dark',
               'Schmaler Hals unter dem Objektiv, nach unten breiter (Destiny-Scout); Fuß auf kurzer Schiene',
               'unter dem Objektiv, auf das Gehäuse geschraubt', bevel=1.0,
               items=[dict(shape='prof', pts=[(46, S.TOP + 14), (62, S.TOP + 14), (62, CU - 12), (48, CU - 10)], w=13),
                      dict(shape='prof', pts=[(44, S.TOP + 8), (64, S.TOP + 8), (64, S.TOP + 16), (46, S.TOP + 16)], w=19),
                      dict(shape='box', f0=42, f1=66, u0=S.TOP + 0.5, u1=S.TOP + 9, w=24)]
               + screws([(48, S.TOP + 5), (60, S.TOP + 5)], 12.0, r=1.2, h=0.6)),
          box('sight_clamp', 'Klemmhebel', 'Clamp lever', 'sight', 'accent', 'Spannt den Hals werkzeuglos', 'links am Halsfuß',
              45, 61, S.TOP + 1.5, S.TOP + 4.5, 1.8, x=12.6)]
    return P + _scope_common()


def _scope_grat():
    """B: Rohr liegt wie 0.19 auf dem Gehäuse, aber auf einem schmalen dunklen Grat; vor dem Auge abgeschrägt, vor dem Sattel steil ab."""
    seat = CU - 9.5 - 0.3
    rec = _scout_receiver([(194, S.TOP), (-112, S.TOP)])
    top = [(-60, 136), (-40, 141), (-18, 141), (6, seat), (30, seat), (42, 140), (48, 136)]
    P = [rec,
         part('scope_ridge', 'Visiergrat', 'Sight ridge', 'receiver', 'multi', 'sight_dark',
              'Schmaler Grat auf dem Gehäuse, trägt das Rohr; vor dem Auge abgeschrägt, im Zielen ein schmaler Keil unter dem Ring',
              'auf dem Gehäuse verschraubt', bevel=1.0,
              items=[dict(shape='prof', pts=top, w=11),
                     dict(shape='prof', pts=[(-74, S.TOP - 1), (40, S.TOP - 1), (26, S.TOP + 15), (-66, S.TOP + 15)], w=20)]),
         part('scope_mount_r', 'Rohrsattel', 'Scope saddle', 'sight', 'multi', 'anodized', 'Klemmt das Rohr auf den Grat',
              'auf dem Grat verschraubt (lösbar)', bevel=0.6, items=[dict(shape='box', f0=8, f1=28, u0=seat - 5, u1=seat, w=14)]
              + screws([(12, seat - 2.5), (24, seat - 2.5)], -7.0, r=1.0, h=0.5)),
         cyl('scope_strap', 'Spannband', 'Scope strap', 'sight', 'anodized', 'Hält das Rohr im Sattel', 'um das Mittelrohr',
             'f', (CU, 0), 11, 25, 11.1, r_in=9.5, segs=40, ads_hide=True),
         box('sight_clamp', 'Klemmhebel', 'Clamp lever', 'sight', 'accent', 'Spannt den Sattel', 'links am Sattel',
             10, 26, seat - 4.5, seat - 1.5, 1.6, x=7.6)]
    return P + _scope_common()


def _legs(f, u_top, x_top, u_foot, x_foot, r=1.5):
    return [dict(shape='tube', path=[(f, u_top, s * x_top), (f, u_foot, s * x_foot)], r=r) for s in (1, -1)]


def _scope_offen():
    """C: offener Ring (Lücke oben) auf zwei dünnen gespreizten Beinen; Sattel hinter dem Auge wie A."""
    P = [p for p in _scope_hals() if p['id'] in ('receiver', 'rail')]
    seat = CU - 9.5 - 0.3
    P += [part('scope_mount_r', 'Rohrsattel', 'Scope saddle', 'sight', 'multi', 'anodized', 'Trägt das Rohr hinten (hinter dem Auge)',
               'Klemmung auf Schiene (lösbar)', bevel=1.0, iface='BRI-22',
               items=[dict(shape='box', f0=-46, f1=-28, u0=S.HUMP + 0.5, u1=seat, w=26)]),
          cyl('scope_strap', 'Spannband', 'Scope strap', 'sight', 'anodized', 'Hält das Rohr im Sattel', 'um das Mittelrohr',
              'f', (CU, 0), -43, -31, 11.1, r_in=9.5, segs=40),
          part('scope_legs', 'Ringbeine', 'Ring legs', 'sight', 'multi', 'sight_dark', 'Zwei dünne gespreizte Beine unter dem Ring',
               'vom Ring zum Fuß', bevel=0, smooth=True, items=_legs(F_OBJ - 6, CU - 11, 11.5, S.TOP + 5, 18, r=1.6)),
          box('scope_foot', 'Ringfuß', 'Ring foot', 'sight', 'anodized', 'Flacher Fuß vor dem Auswurf', 'auf dem Gehäuse',
              F_OBJ - 14, F_OBJ + 2, S.TOP - 1, S.TOP + 5, 42, bevel=1.0)]
    return P + _scope_common(open_ring=True)


# ------------------------------------------------------------------------------------------------ Holo (Automatik)
HF, HU = -6, A.RAIL_U + 8                    # Lage wie 0.20 (reflex_sight_v21(-6, RAIL_U + 8))
WW, WH = 26, 20
HCU = HU + 6 + WH / 2 + 10                   # Visierlinie u 169
FG = HF + 40                                 # Glasebene f 34
GB = HCU - WH / 2 - 0.4                      # Fensterunterkante


def _holo_glass(hood=True, line=False):
    """Glas, Fenster (dünner Rundrahmen 1,6 mm) oder offenes U (C), optional Leuchtlinie am Glasrand."""
    P = [part('sight_glass', 'Visierglas', 'Sight glass', 'sight', 'xbox', 'glass_scope', 'Reflexscheibe ohne Spiegelung', 'im Fenster (fest)',
              bevel=0, f0=FG, f1=FG + 0.8, cu=HCU, ww=WW, hh=WH)]
    if hood:
        P.append(part('sight_frame', 'Fensterrahmen', 'Window frame', 'sight', 'frame', 'sight_dark', 'Dünner Rundrahmen (1,6 mm)',
                      'auf dem Hals (fest)', bevel=0.4, f0=FG - 3, f1=FG + 3, cu=HCU, ow=WW + 3.2, oh=WH + 3.2, iw=WW, ih=WH,
                      r_out=4.6, r_in=3.0))
    else:   # VEIST: zwei Zinken und Schwelle, oben offen
        hw = WW / 2 + 0.8
        P.append(part('sight_frame', 'Fensterzinken', 'Window tines', 'sight', 'multi', 'sight_dark', 'Zwei dünne Zinken, oben offen',
                      'auf den Beinen (fest)', bevel=0.4,
                      items=[dict(shape='prof', pts=[(FG - 3, GB - 1.6), (FG + 3, GB - 1.6), (FG + 3, HCU + WH / 2 - 3),
                                                     (FG - 1, HCU + WH / 2 - 1)], w=1.6, x=s * hw) for s in (1, -1)]
                      + [dict(shape='prof', pts=[(FG - 3, GB - 1.6), (FG + 3, GB - 1.6), (FG + 3, GB), (FG - 3, GB)], w=WW + 3.2)]))
    if line:
        P.append(part('sight_line', 'Leuchtlinie', 'Glow line', 'sight', 'frame', 'reticle_cyan',
                      'Gezeichnete Leuchtlinie am Glasrand (SUROS, ≈ 0,4 % Bildbreite)', 'auf dem Glas', bevel=0,
                      f0=FG - 0.3, f1=FG - 0.1, cu=HCU, ow=WW - 1.0, oh=WH - 1.0, iw=WW - 1.8, ih=WH - 1.8, r_out=2.6, r_in=2.2))
    return P


def _holo_anchors(part_eye='sight_frame'):
    rel = SIGHT['types']['reflex']['eye_relief_mm']
    return {'Socket_Sight': dict(at=(HF + 20, HCU, 0), part='sight_glass'),
            'Socket_Reticle': dict(at=(FG + 0.4, HCU, 0), part='sight_glass'),
            'Socket_Eye': dict(at=(FG + 0.4 - rel, HCU, 0), part=part_eye, sight_type='reflex', std=True,
                               note=f'Augenpunkt beim Zielen ({rel:.0f} mm hinter dem Glas)')}


def _holo_rail(f0, f1):
    r = [dict(p, mat='anodized') for p in rail(f0, f1, A.RAIL_U)]
    return r


def _holo_hals():
    """A: Fenster auf schmalem Hals direkt darunter; Emitter vorn im Hals, kein Gehäuse hinter dem Fenster; kurze Schiene."""
    u0 = A.RAIL_U + 8
    P = _holo_rail(10, 48) + [
        part('sight_mount', 'Visier-Klemmfuß', 'Sight mount', 'sight', 'multi', 'anodized', 'Klemmt das Visier auf die Schiene BRI-22',
             'Klemmung auf Schiene (lösbar)', bevel=1.0, iface='BRI-22',
             items=[dict(shape='box', f0=12, f1=46, u0=u0 + 0.5, u1=u0 + 4, w=23)]),
        part('sight_neck', 'Visierhals', 'Sight neck', 'sight', 'multi', 'sight_dark', 'Schmaler Hals bis zur Fensterunterkante',
             'auf dem Klemmfuß (fest)', bevel=0.8,
             items=[dict(shape='prof', pts=[(16, u0 + 3.5), (42, u0 + 3.5), (40, u0 + 9), (18, u0 + 9)], w=17),
                    dict(shape='prof', pts=[(20, u0 + 8.5), (38, u0 + 8.5), (37, GB), (24, GB)], w=11)]),
        box('sight_emitter', 'Emitter', 'Reticle emitter', 'sight', 'energy', 'Leuchtfenster des Projektors (zum Glas hin)',
            'vorn im Hals', 37.4, 38.2, u0 + 9.5, u0 + 11.5, 4, bevel=0.2),
        box('sight_clamp', 'Klemmhebel', 'Clamp lever', 'sight', 'accent', 'Spannt den Klemmfuß', 'links am Klemmfuß',
            16, 40, u0 + 1, u0 + 3.5, 1.8, x=12.4),
        cyl('sight_battery', 'Batteriedeckel', 'Battery cap', 'sight', 'anodized', 'Batteriefach links', 'links am Hals', 'x',
            (30, u0 + 6), 8.5, 10.5, 2.6, segs=16)]
    return P + _holo_glass()


def _holo_grat():
    """B: flacher Keilsockel, zum Auge hin abgeschrägt; Anzeige auf der Schräge unter der Visierlinie."""
    u0 = A.RAIL_U + 8
    P = _holo_rail(-10, 48) + [
        part('sight_mount', 'Keilsockel', 'Wedge base', 'sight', 'multi', 'sight_dark',
             'Klemmfuß und Sockel in einem: Keil, zum Auge hin flach auslaufend, bis zur Fensterunterkante', 'Klemmung auf Schiene (lösbar)',
             bevel=1.0, iface='BRI-22',
             items=[dict(shape='prof', pts=[(-8, u0 + 0.5), (46, u0 + 0.5), (46, GB), (30, GB), (-8, u0 + 3)], w=18),
                    dict(shape='box', f0=-8, f1=46, u0=u0 + 0.5, u1=u0 + 3, w=23)]),
        part('sight_emitter', 'Anzeige', 'Status display', 'sight', 'prof', 'energy', 'Leuchtstrich auf der Schräge (Munition/Status)',
             'auf der Schräge', bevel=0, pts=[(14, 153.4), (19, 155.1), (19, 155.5), (14, 153.8)], w=3),
        box('sight_clamp', 'Klemmhebel', 'Clamp lever', 'sight', 'accent', 'Spannt den Sockel', 'links am Sockel',
            0, 30, u0 + 1, u0 + 3, 1.8, x=12.4)]
    return P + _holo_glass()


def _holo_offen():
    """C: offenes Fenster (zwei Zinken, Schwelle) auf zwei dünnen Beinen, Leuchtlinie am Glasrand."""
    u0 = A.RAIL_U + 8
    P = _holo_rail(14, 48) + [
        part('sight_mount', 'Visier-Klemmfuß', 'Sight mount', 'sight', 'multi', 'anodized', 'Flacher Fuß auf der Schiene',
             'Klemmung auf Schiene (lösbar)', bevel=1.0, iface='BRI-22', items=[dict(shape='box', f0=16, f1=46, u0=u0 + 0.5, u1=u0 + 4, w=26)]),
        part('sight_legs', 'Fensterbeine', 'Window legs', 'sight', 'multi', 'sight_dark', 'Zwei dünne gespreizte Beine unter dem Fenster',
             'vom Fuß zur Schwelle', bevel=0, smooth=True, items=_legs(FG, GB - 1.2, 10, u0 + 3.5, 14, r=1.3)),
        box('sight_clamp', 'Klemmhebel', 'Clamp lever', 'sight', 'accent', 'Spannt den Fuß', 'links am Fuß', 18, 42, u0 + 1, u0 + 3.5,
            1.8, x=13.6)]
    return P + _holo_glass(hood=False, line=True)


# ------------------------------------------------------------------------------------------------ Varianten
_BUILD = {('hals', 'scope'): _scope_hals, ('grat', 'scope'): _scope_grat, ('offen', 'scope'): _scope_offen,
          ('hals', 'holo'): _holo_hals, ('grat', 'holo'): _holo_grat, ('offen', 'holo'): _holo_offen}


def variant(concept, weapon):
    W = S if weapon == 'scope' else A
    new = _BUILD[(concept, weapon)]()
    ids = {p['id'] for p in new}
    drop = {'receiver', 'rail', 'scope_strap'} if weapon == 'scope' else {'rail'}
    parts = [dict(p) for p in W.PARTS if p['asm'] != 'sight' and p['id'] not in drop and p['id'] not in ids] + new
    keep = {p['id'] for p in parts}
    for p in parts:       # Entwurf: kein Elternteil aus dem alten Visier
        if p.get('parent_part') not in keep:
            p.pop('parent_part', None)
    anchors = {k: v for k, v in W.ANCHORS.items() if k not in ('Socket_Sight', 'Socket_Objective', 'Socket_Reticle', 'Socket_Eye')}
    anchors.update(_scope_anchors() if weapon == 'scope' else _holo_anchors())
    return types.SimpleNamespace(META=dict(W.META, variant=f'v2.1-{concept}', name=f"{W.META['name']} ({concept})"),
                                 ASSEMBLIES=W.ASSEMBLIES, PARTS=parts, ANCHORS=anchors, ACTIONS=W.ACTIONS, EXPLODE=W.EXPLODE,
                                 BORE=W.BORE, __doc__=W.__doc__)
