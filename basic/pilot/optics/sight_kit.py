"""Visier-Baukasten v3 – Katalog und Entwürfe. Nutzer 26.10.2026: „unterschiedliche Visiere anlegen, verschiedene Formen, Größen usw.,
die wir später verwenden können. Für manche Waffen fehlen ja Visiere auch noch“; zu v1: „fast alle zu klotzig … viel zu hoch“; zu
v2: „Das Visier von BASIC-01 sieht so um Welten besser aus als die neuen“; Leitlinie: „Visier vom aktuellen Automatikgewehr von der
Höhe optimal und vom Design gut. Daran sollte man sich orientieren“; Auftrag: „ein bis zwei prägende Designelemente je Visier …
schlicht, funktional und gut lesbar … sichtbar voneinander unterscheiden … Sichtfeld und Zielerfassung müssen klar bleiben.“

Seit 0.21 „Ironsight“ (Nutzerwahl „v3 bauen“) ist der Baukasten Produktionsform in `basic/common.py`: H0-Plattform
(`sight_platform`), Flachprofil `xprof` (Form in `kit.py`), Haube, Glas, gezeichnetes Absehen und die gebauten Visiere H0
(`reflex_sight_v21`), H2 Pille, H4 Kasten, Z1 Tropfen (Sitz nach Konzept A). Dieses Modul stellt sie auf einem neutralen Prüfkörper
mit BASIC-01-Maßen dar (Gehäuse u 135, Schiene bis u 143, Visierlinie u 169) und hält die übrigen Visiere als Entwürfe auf denselben
Bausteinen – keine zweite Kopie. Kimme/Korn und Mini-Reflex mit eigener Linie (Visier-Standard 3: Schiene + 11 bzw. + 15 mm).
Absehen gezeichnet (Hüftform der Klasse), Glas ohne Spiegelung (`glass_scope`), flache Scheiben.
Vorbilder: Destiny 2 (`~/Library/Caches/CubeEscapeBallon/refs/video/d2_ads/`), Formgen VS01–VS09 (`refs/formgen_vs/`), BF6.
"""
import math
import types

from basic import common as C
from basic.common import part, cyl, prof, cut_box, xprof, sight_arc as _arc, sight_rr as _rr, sight_sector as _sector
from basic.common import HOLO_SIZES, SCOPE_SIZES, SIGHT_T as T, SIGHT_MAT as MET
from basic.reticles import SIGHT

TOP, DECK = 135, 143                    # Gehäuseoberkante, Schienenoberkante (wie BASIC-01)
CU = C.sight_line(DECK)                 # Visierlinie u 169 wie BASIC-01 (Schiene + 26; Prüfkörper: Zielfernrohre auf derselben Schiene)
CU_IRON = C.sight_line(DECK, 'iron')    # Kimme/Korn: eigene, tiefe Linie Schiene + 11 (Kritik: sonst „Türme“)
CU_MINI = C.sight_line(DECK, 'mini_reflex')   # Mini-Reflex (Seitenwaffe, Handfeuerwaffe) Schiene + 15
BORE = CU - 66
REL = SIGHT['types']['reflex']['eye_relief_mm']   # Augenabstand (Visier-Standard 3)
F = -6                                  # Lage der Plattform wie BASIC-01 (reflex_sight_v21(-6, …))


def stub(deck_f0=-30, deck_f1=60, front_deck=False, length=420):
    """Neutraler Prüfkörper wie BASIC-01: Gehäuse (Creme, u 135, 44 breit), Schiene BRI-22 (u 135–143), Handschutz, Lauf."""
    f1 = length if front_deck else deck_f1
    return [prof('receiver', 'Prüfgehäuse', 'Test receiver', 'receiver', 'shell', 'Neutraler Träger (Maße wie BASIC-01)', 'Grundkörper',
                 [(-130, 70), (200, 70), (200, TOP), (-130, TOP)], 44),
            part('rail', 'Schiene', 'Top rail', 'receiver', 'box', 'anodized', 'Aufnahme für Visiere (BRI-22)', 'auf dem Gehäuse',
                 bevel=1.0, f0=deck_f0, f1=f1, u0=TOP - 0.5, u1=DECK, w=22),
            prof('handguard', 'Prüfhandschutz', 'Test handguard', 'receiver', 'graphite', 'Vorderer Körper', 'am Gehäuse',
                 [(200, 84), (length, 86), (length, TOP - 4), (200, TOP - 2)], 34),
            cyl('barrel', 'Lauf', 'Barrel', 'barrel', 'metal', 'Lauf', 'im Gehäuse', 'f', (BORE, 0), length, length + 120, 8, segs=24)]


# ------------------------------------------------------------------------------------------------ Bausteine (aus basic/common.py)
def _x(pid, de, mat, f0, f1, pts, cu=CU, holes=(), func='', attach='am Visier', bevel=0.4, **kw):
    return xprof(pid, de, mat, f0, f1, pts, cu, holes=holes, func=func, attach=attach, bevel=bevel, **kw)


def _hood(inner, outer, fr=F + 34, depth=12, cu=CU, trim=True, mat=MET):
    return C.sight_hood(inner, outer, fr, cu, depth=depth, trim=trim, mat=mat)


def _glass(f, pts, cu=CU):
    return C.sight_glass_x(f, pts, cu)


def _eye(f_glass, cu=CU, typ='reflex', part_id='sight_glass'):
    return {'Socket_Reticle': dict(at=(f_glass, cu, 0), part=part_id),
            'Socket_Eye': dict(at=(f_glass - REL, cu, 0), part=part_id, sight_type=typ, std=True,
                               note=f'Augenpunkt ({REL:.0f} mm hinter der Öffnung)')}


def platform(base_w, gb, f=F, k=1.0, emitter=True, extra=()):
    """H0-Plattform (common.sight_platform) an der Lage des Prüfkörpers."""
    return C.sight_platform(f, DECK, base_w, gb, k=k, emitter=emitter, mat=MET) + list(extra)


def _base_rear_f(gb, f=F, k=1.0, u_at=None):
    return C.sight_base_rear_f(f, DECK, gb, u_at, k=k)


# ------------------------------------------------------------------------------------------------ Holo
def holo_ref(size='M'):
    """H0 Referenz: das heutige Holo von BASIC-01 v2.1 (`common.reflex_sight_v21`, Lage wie dort), Größe immer M."""
    from basic.common import reflex_sight_v21
    return reflex_sight_v21(F, DECK, reticle_kind='ring_dot')


def holo_fase(size='M'):
    """H1 „Fase“ (Automatik, MG): H0 mit geschlossener Haube, Ecke oben rechts 6 mm gefast (Merkmal)."""
    w, h = HOLO_SIZES[size]
    gb = CU - h / 2 - 0.4
    inner, outer = _rr(w, h, 2.0, cut=6), _rr(w + 2 * T, h + 2 * T, 2.0 + T, cut=6 + 0.6 * T)
    return platform(w + 2 * T, gb) + _hood(inner, outer) + [_glass(F + 40, inner)], _eye(F + 40.4)


def holo_pille(size='M'):
    """H2 „Pille“ (MP): gebaut in common.holo_pille (BASIC-06 v2.1)."""
    return C.holo_pille(F, DECK, size, mat=MET)


def holo_zinken(size='M'):
    """H3 „Zinken“ (Spur, MP): H0-Haube ohne Dach – zwei Seitenplatten 15° nach außen geneigt, unten 3, oben 1,5 mm Stirn, Spitzen
    45° nach innen gekappt (Merkmal 1, VEIST); Emitterpunkt auf der Sockelrückseite zum Auge (Merkmal 2)."""
    w, h = HOLO_SIZES[size]
    gb = CU - h / 2 - 0.4
    ub, ut = -h / 2 - 0.4, h / 2 + 3
    tn = math.tan(math.radians(15)) * (ut - ub)
    plates = []
    for s in (1, -1):
        xb, xt = w / 2, w / 2 + tn
        plates.append([(s * xb, ub), (s * (xb + 3), ub), (s * (xt + 1.5), ut), (s * xt, ut - 1.5)])
    fr = F + 34
    P = platform(w + 6, gb) + [_x(f'sight_frame{"" if s > 0 else "_r"}', 'Zinke', MET, fr, fr + 12, pl, func='Seitenplatte, oben offen')
                               for s, pl in zip((1, -1), plates)]
    P += [_x(f'sight_frame_trim{"" if s > 0 else "_r"}', 'Zinkenkante', 'trim', fr + 11.6, fr + 12.6, pl, bevel=0.2)
          for s, pl in zip((1, -1), plates)]
    ue = gb - 3.5
    fe = _base_rear_f(gb, u_at=ue)
    P += [part('sight_status', 'Emitterpunkt', 'Emitter pip', 'sight', 'cyl', 'energy', 'Leuchtpunkt zum Auge', 'Sockelrückseite',
               bevel=0, axis='f', c=(ue, 0), a0=fe - 0.4, a1=fe + 0.6, r=0.9, segs=16),
          _glass(F + 40, [(w / 2 - 0.2, ub + 0.4), (w / 2 + tn * 0.8, ut - 3), (-w / 2 - tn * 0.8, ut - 3), (-w / 2 + 0.2, ub + 0.4)])]
    return P, _eye(F + 40.4)


def holo_kasten(size='M'):
    """H4 „Kasten“ (Impuls): gebaut in common.holo_kasten (BASIC-02 v2.1)."""
    return C.holo_kasten(F, DECK, size, mat=MET)


def ring_haekke(size='M'):
    """H5 „Häkke“ (Impuls, Automatik leicht): Ringhaube aus Flachprofil 1,8 × 10 mit Lücke oben 45° (Merkmal 1); Nasen auf 3 und
    9 Uhr, dort 3 mm breiter mit blanker Kante (Merkmal 2). Wächst aus dem H0-Trapezsockel."""
    r = {'S': 10.5, 'M': 12.5, 'L': 16}[size]
    t = 1.8
    gb = CU - r - 0.4
    ring = _sector(r, r + t, 112.5, 427.5, 48)
    noses = [[(s * (r + t - 0.2), -1.6), (s * (r + t + 3), -1.6), (s * (r + t + 3), 1.6), (s * (r + t - 0.2), 1.6)] for s in (1, -1)]
    fr = F + 36
    P = platform(2 * (r + t), gb) + [_x('sight_frame', 'Ringhaube', MET, fr, fr + 10, ring, func='Ring mit Lücke oben'),
                                     _x('sight_frame_trim', 'Stirnkante', 'trim', fr + 9.6, fr + 10.6, ring, bevel=0.2)]
    P += [_x(f'sight_nose{"" if s > 0 else "_r"}', 'Nase', MET, fr + 2, fr + 10, n, func='Nase 3/9 Uhr') for s, n in zip((1, -1), noses)]
    P += [_x(f'sight_nose_trim{"" if s > 0 else "_r"}', 'Nasenkante', 'trim', fr + 1.6, fr + 2.4, n, bevel=0.1)
          for s, n in zip((1, -1), noses)]
    P.append(_glass(F + 40, _arc(r - 0.6, 112.5, 427.5, 48)))
    return P, _eye(F + 40.4)


def fusion_boegen(size='M'):
    """F1 „Bögen“ (Fusion): zwei Bögen aus Flachprofil mit Radiusversatz – oben r, unten r + 3, Lücken 25° auf 3 und 9 Uhr – ergeben
    im Zielen eine S-Öffnung (Merkmal 1); Ladeanzeige als Leuchtbalken 10 × 1,5 mm auf dem Gehäuse (Merkmal 2)."""
    r = {'S': 11.5, 'M': 13.5, 'L': 17}[size]
    gb = CU - r - 3 - 0.4
    fr = F + 34
    top, bot = _sector(r, r + T, 12.5, 167.5), _sector(r + 3, r + 3 + T, 192.5, 347.5)

    def pt(rr, a):
        return (rr * math.cos(math.radians(a)), rr * math.sin(math.radians(a)))
    # Stege in den Lücken (3/9 Uhr): verbinden das Bogenende oben schräg mit dem Bogenanfang unten
    webs = [[pt(r + T, 12.5), pt(r, 12.5), pt(r + 3, -12.5), pt(r + 3 + T, -12.5)],
            [pt(r, 167.5), pt(r + T, 167.5), pt(r + 3 + T, 192.5), pt(r + 3, 192.5)]]
    bt = DECK + 6
    P = platform(2 * (r + 3 + T), gb, emitter=False) + [
        _x('sight_frame', 'Oberer Bogen', MET, fr, fr + 12, top), _x('sight_frame_b', 'Unterer Bogen', MET, fr, fr + 12, bot),
        _x('sight_frame_trim', 'Stirnkante oben', 'trim', fr + 11.6, fr + 12.6, top, bevel=0.2),
        _x('sight_frame_trim_b', 'Stirnkante unten', 'trim', fr + 11.6, fr + 12.6, bot, bevel=0.2),
        _x('sight_web', 'Steg', MET, fr, fr + 12, webs[0]), _x('sight_web_r', 'Steg', MET, fr, fr + 12, webs[1]),
        part('sight_emitter', 'Ladebalken', 'Charge bar', 'sight', 'box', 'energy', 'Ladeanzeige 10 × 1,5 mm', 'oben auf dem Gehäuse',
             bevel=0.2, f0=F + 3, f1=F + 13, u0=bt + 5.8, u1=bt + 6.3, w=1.5),
        _glass(F + 40, _arc(r + 1.5, 0, 360, 48)[:-1])]
    return P, _eye(F + 40.4)


def mini_reflex(size='M'):
    """M1 „Mini“ (Seitenwaffe, Handfeuerwaffe): H0-Plattform auf 70 % gekürzt, Fenster 16 × 12 (Merkmal 1: kleinste Haube); tiefe
    Visierlinie (Schiene + 15 mm)."""
    w, h = {'S': (14, 10.5), 'M': (16, 12), 'L': (19, 14)}[size]
    gb = CU_MINI - h / 2 - 0.4
    k = 0.7
    inner, outer = _rr(w, h, 1.6), _rr(w + 2 * T, h + 2 * T, 1.6 + T)
    fr = F + 46 * k - 12 + 0.6
    P = platform(w + 2 * T, gb, k=k) + _hood(inner, outer, fr=fr, depth=9, cu=CU_MINI) + [_glass(fr + 5, inner, cu=CU_MINI)]
    return P, _eye(fr + 5.4, cu=CU_MINI)


def launcher_d(size='M'):
    """W1 „D-Linse“ (Granatwerfer): H0-Plattform, Haube als D aus Flachprofil 2,4 × 12, oben gerade (Merkmal 1) mit oranger Kerbe;
    drei blanke Fallmarken 4/3/2 mm links innen (Merkmal 2)."""
    r = {'S': 13, 'M': 15.5, 'L': 20}[size]
    t = 2.4
    top = r * 0.62

    def d(rr, cap):
        return [(x, min(u, cap)) for x, u in _arc(rr, -90, 270, 60)][:-1]
    inner, outer = d(r, top), d(r + t, top + t)
    gb = CU - r - 0.4
    fr = F + 34
    marks = part('sight_marks', 'Fallmarken', 'Drop marks', 'sight', 'multi', 'trim', 'Drei Fallmarken 4/3/2 mm', 'innen links',
                 bevel=0.1, items=[dict(shape='box', f0=fr + 11, f1=fr + 12, u0=CU - 4 * i - 0.4, u1=CU - 4 * i + 0.4, w=wd,
                                        x=r - 0.2 - wd / 2) for i, wd in ((1, 4), (2, 3), (3, 2))])
    notch = part('sight_notch', 'Kerbe', 'Notch', 'sight', 'box', 'accent', 'Orange Kerbe oben', 'oben an der Haube', bevel=0.2,
                 f0=fr + 2, f1=fr + 12, u0=CU + top + t - 0.2, u1=CU + top + t + 1.6, w=2.4)
    return platform(2 * (r + t), gb) + _hood(inner, outer) + [marks, notch, _glass(F + 40, inner)], _eye(F + 40.4)


def rocket_kasten(size='M'):
    """W2 „Entfernung“ (Raketenwerfer): breite H0-Haube 34 × 22 mit kräftiger Stirn oben 4 mm (Merkmal 1, Schutzdach) und
    Entfernungsfeld im Sockel zum Auge (Merkmal 2)."""
    w, h = {'S': (30, 19), 'M': (34, 22), 'L': (42, 27)}[size]
    gb = CU - h / 2 - 0.4
    inner = _rr(w, h, 2.5)
    outer = _rr(w + 2 * 2.4, h + 2.4 + 4, 2.5 + 2.4)
    outer = [(x, u + 0.8) for x, u in outer]
    ud = gb - 6.5
    fd = _base_rear_f(gb, u_at=ud + 2)
    field = part('sight_status', 'Entfernungsfeld', 'Range field', 'sight', 'multi', 'energy', 'Entfernung (drei Ziffern + Einheit)',
                 'in der Sockelrückseite', bevel=0, items=[dict(shape='box', f0=fd - 0.5, f1=fd + 0.5, u0=ud, u1=ud + 4, w=3.0, x=x)
                                                          for x in (6, 2.4, -1.2)]
                 + [dict(shape='box', f0=fd - 0.5, f1=fd + 0.5, u0=ud, u1=ud + 2, w=2.4, x=-5.2)])
    return platform(w + 4.8, gb) + _hood(inner, outer, depth=12) + [field, _glass(F + 40, inner)], _eye(F + 40.4)


# ------------------------------------------------------------------------------------------------ Zielfernrohr
def _scope_body(f_obj, r_in, r_out, length=120, tube_r=9.5, step=False):
    """Zielfernrohr (common.scope_body) mit Rohrsattel hinter dem Auge (common.scope_saddle, Konzept A) auf der Prüfkörper-Schiene."""
    fe, eye = f_obj - length, f_obj - SIGHT['types']['scope']['eye_relief_mm']
    return C.scope_saddle(fe + 2, eye - 2, DECK, CU, fe, tube_r, mat=MET) \
        + C.scope_body(f_obj, CU, r_in, r_out, length=length, tube_r=tube_r, step=step, mat=MET)


def _scope_foot(f0, f1, top):
    """H0-Klemmfuß unter dem Objektiv (common.scope_foot); im Entwurf ohne Rohrsattel als Elternteil."""
    foot, clamp = C.scope_foot(f0, f1, DECK, top, mat=MET)
    return [{k: v for k, v in foot.items() if k != 'parent_part'}, clamp]


def _scope_anchors(f_obj, length=120):
    return C.scope_anchors(f_obj, f_obj - length, CU)


def scope_tropfen(size='M'):
    """Z1 „Tropfen“ (Scout): gebaut in common.scope_tropfen (BASIC-03 v2.1), Fuß und Sattel auf der Prüfkörper-Schiene."""
    return C.scope_tropfen(72, DECK, CU, size, mat=MET)


def scope_gabel(size='M'):
    """Z2 „Gabel“ (lineare Fusion): geschlossener flacher Ring; darum eine U-Gabel aus Flachprofil 3 × 10 mit 3 mm Abstand, Enden auf
    3/9 Uhr schräg gekappt, in derselben Ebene (Merkmal 1); kurze Laschen verbinden Ring und Gabel (Merkmal 2)."""
    r_in = SCOPE_SIZES[size]
    ro = r_in + 2.2
    f_obj = 72
    g0, g1 = ro + 3, ro + 6
    fork = [(g1, 1.6), (g0, 0.0)] + _arc(g0, 0, -180, 32)[1:-1] + [(-g0, 0.0), (-g1, 1.6)] + _arc(g1, -180, 0, 32)[1:-1]
    tabs = [[(s * (ro - 0.3), -1.2), (s * (g0 + 0.3), -1.2), (s * (g0 + 0.3), 1.2), (s * (ro - 0.3), 1.2)] for s in (1, -1)]
    bottom = CU - g1
    return _scope_body(f_obj, r_in, g1 * 0.0 + ro, step=False) + _scope_foot(f_obj - 28, f_obj, bottom + 0.5) + [
        cyl('scope_rim', 'Objektivring', 'Objective ring', 'sight', MET, 'Geschlossener flacher Ring', 'vorn', 'f', (CU, 0), f_obj - 6,
            f_obj, ro * (REL - 6) / REL - 0.1, r1=ro, r_in=r_in, segs=64, bevel=0.5),
        _x('scope_fork', 'Gabel', MET, f_obj - 10, f_obj, fork, func='U-Gabel, 3 mm Abstand zum Ring'),
        _x('scope_fork_trim', 'Gabelkante', 'trim', f_obj - 0.4, f_obj + 0.6, fork, bevel=0.2),
        _x('scope_tabs', 'Laschen', MET, f_obj - 8, f_obj - 2, tabs[0]), _x('scope_tabs_r', 'Laschen', MET, f_obj - 8, f_obj - 2, tabs[1])], \
        _scope_anchors(f_obj)


def sniper_lang(size='M'):
    """Z3 „Lang“ (Scharfschütze): kräftigeres Rohr Ø 21, Objektiv Ø 40 mit blanker Sonnenblende (Merkmal 1); zwei Ringe auf
    H0-Klemmfüßen mit orangem Hebel; im Zielen Vollbild mit Duplex-Absehen (Merkmal 2, gezeichnet)."""
    r_obj = {'S': 17, 'M': 20, 'L': 23}[size]
    fe, fo, tr = -110, 150, 10.5
    P = [cyl('scope_tube', 'Mittelrohr', 'Scope tube', 'sight', MET, 'Langes Rohr Ø 21', 'in zwei Ringen', 'f', (CU, 0), fe + 26, fo - 50,
             tr, segs=40),
         cyl('scope_eyepiece', 'Okular', 'Eyepiece', 'sight', MET, 'Okular', 'am Rohr', 'f', (CU, 0), fe, fe + 28, 13, r1=11, segs=40),
         cyl('scope_objective', 'Objektiv', 'Objective bell', 'sight', MET, 'Objektivglocke', 'am Rohr', 'f', (CU, 0), fo - 52, fo,
             11, r1=r_obj, r_in=r_obj - 2.6, segs=48, bevel=0.5),
         part('scope_shade', 'Sonnenblende', 'Sun shade', 'sight', 'prof', 'trim', 'Flache blanke Blende über dem Objektiv',
              'oben am Objektiv', bevel=0.4, pts=[(fo - 12, CU + r_obj - 0.5), (fo + 16, CU + r_obj - 0.5), (fo + 16, CU + r_obj + 0.9),
                                                   (fo - 8, CU + r_obj + 1.6)], w=r_obj * 1.2),
         cyl('scope_glass', 'Objektivlinse', 'Objective lens', 'sight', 'glass_scope', 'Linse', 'im Objektiv', 'f', (CU, 0), fo - 3,
             fo - 2, r_obj - 2.6, segs=48, bevel=0),
         cyl('scope_turret', 'Höhenturm', 'Elevation turret', 'sight', 'accent', 'Höhenverstellung', 'oben', 'u', (10, 0), CU + 8,
             CU + 16, 5.5, segs=32),
         part('scope_rings', 'Montageringe', 'Scope rings', 'sight', 'multi', MET, 'Zwei Ringe mit Steg', 'auf den Klemmfüßen', bevel=0.6,
              items=[dict(shape='cyl', axis='f', c=(CU, 0), a0=f0, a1=f0 + 9, r=tr + 2.4, r_in=tr, segs=40) for f0 in (-70, 60)]
              + [dict(shape='box', f0=f0, f1=f0 + 9, u0=DECK + 5, u1=CU - tr, w=10) for f0 in (-70, 60)])]
    for i, f0 in enumerate((-74, 56)):
        for q in _scope_foot(f0, f0 + 17, DECK + 6):
            P.append({k: v for k, v in dict(q, id=f"{q['id']}_{i}").items() if k != 'parent_part'})
    return P, {'Socket_Reticle': dict(at=(fo, CU, 0), part='scope_glass'),
               'Socket_Eye': dict(at=(fe - 60, CU, 0), part='scope_eyepiece', sight_type='fullscreen', std=False,
                                  note='Vollbild (Art A): Duplex gezeichnet, Waffe ausgeblendet')}


# ------------------------------------------------------------------------------------------------ Kimme/Korn
IRON_EYE_MM = 70.0                      # Augenpunkt hinter der Kimme (Entwurf 0.21; Visier-Standard 3 legt für Kimme/Korn keinen fest)
KLAMMER_SIZES = {'S': 0.85, 'M': 1.0, 'L': 1.2}


def _irons_anchor(fr, ff, cu=CU_IRON, deck=DECK):
    return {'Socket_Reticle': dict(at=(ff, cu, 0), part='sight_glass'),
            'Socket_Sight': dict(at=(fr, cu, 0), part='sight_rear', note='Kimme (Rückseite des Kimmenblatts) auf der Visierlinie'),
            'Socket_Eye': dict(at=(fr - IRON_EYE_MM, cu, 0), part='sight_rear', sight_type='iron', std=False, deck=deck,
                               note=f'{IRON_EYE_MM:.0f} mm hinter der Kimme, eigene Linie Schiene + {cu - deck:g} mm')}


def iron_klammer(size='M'):
    """K1 „Klammer“ auf dem Prüfkörper (Katalogblatt, test_sights); gebaut von `klammer`."""
    return klammer(20, 330, DECK, size)


def klammer(fr, ff, deck, size='M', parent=None):
    """K1 „Klammer“ (Handfeuerwaffe, Seitenwaffe; seit 0.24 an BASIC-04/05 v2.1): Kimme als ein Blatt 20 × 7 × 6 mm mit Kerbe 4,6 auf
    flachem Fuß (H0-Profilsprache); Leuchtklammern „[ ]“ bündig in der Blattrückseite (Merkmal 1); Korn 3 mm mit Leuchtpunkt
    (Merkmal 2). fr = Rückseite des Kimmenblatts, ff = Kornspitze, deck = Oberkante des Trägers (Schiene, Oberbrücke, Schlitten);
    Visierlinie Schiene + 11 mm (Visier-Standard 3). parent: bewegliches Trägerteil (Schlitten). Gibt (Teile, Anker) zurück.
    Liegt hier statt in common.py, weil common.py im Unity-Quellenhash steht (export_unity.SHARED_SRC; Umzug mit dem Ego-Übertrag)."""
    s = KLAMMER_SIZES[size]
    notch, cu = 4.6 * s, C.sight_line(deck, 'iron')
    b0 = deck + 6
    br = []
    for x in (1, -1):
        xi = x * (notch / 2 + 2.6 * s)
        br += [dict(shape='box', f0=fr - 0.1, f1=fr + 0.3, u0=cu - 3.6 * s, u1=cu + 1.2 * s, w=0.7 * s, x=xi),
               dict(shape='box', f0=fr - 0.1, f1=fr + 0.3, u0=cu + 0.5 * s, u1=cu + 1.2 * s, w=1.6 * s, x=xi - x * 0.8 * s),
               dict(shape='box', f0=fr - 0.1, f1=fr + 0.3, u0=cu - 3.6 * s, u1=cu - 2.9 * s, w=1.6 * s, x=xi - x * 0.8 * s)]
    P = [part('sight_mount', 'Kimmenfuß', 'Rear base', 'sight', 'multi', MET, 'Flacher Fuß, gestuft', 'hinten auf der Schiene',
              bevel=0.8, items=[dict(shape='box', f0=fr - 4, f1=fr + 18, u0=deck - 0.5, u1=deck + 3.5, w=23),     # sitzt auf (Richter 0.24: lag 0,5 mm darüber)
                                dict(shape='box', f0=fr - 2, f1=fr + 14, u0=deck + 3, u1=b0, w=16)]),
         part('sight_clamp', 'Klemmhebel', 'Clamp lever', 'sight', 'prof', 'accent', 'Spannt den Fuß', 'links am Fuß', bevel=0.4,
              pts=[(fr, deck + 0.8), (fr + 12, deck + 0.8), (fr + 14, deck + 3.2), (fr, deck + 3.6)], w=1.8, x=12.4),
         part('sight_rear', 'Kimmenblatt', 'Rear blade', 'sight', 'prof', MET, 'Blatt 20 × 7 × 6 mm mit Kerbe', 'auf dem Kimmenfuß',
              bevel=0.5, pts=[(fr, b0 - 0.5), (fr + 8, b0 - 0.5), (fr + 6, cu + 2 * s), (fr, cu + 2 * s)], w=20 * s,
              cuts=[cut_box(fr - 3, fr + 12, cu - 2.6 * s, cu + 6, notch)]),
         part('sight_status', 'Leuchtklammern', 'Glow brackets', 'sight', 'multi', 'energy', 'Klammern „[ ]“ bündig zum Auge',
              'in der Blattrückseite', bevel=0, items=br),
         part('sight_front', 'Korn', 'Front sight', 'sight', 'multi', MET, 'Korn 3 mm auf flachem Fuß', 'vorn auf der Schiene', bevel=0.4,
              items=[dict(shape='prof', pts=[(ff - 7, deck - 0.5), (ff + 6, deck - 0.5), (ff + 2, cu - 0.8), (ff, cu - 0.8)], w=3.0),
                     dict(shape='box', f0=ff - 8, f1=ff + 8, u0=deck - 0.5, u1=deck + 2.5, w=12)]),
         part('sight_glass', 'Kornpunkt', 'Front dot', 'sight', 'cyl', 'energy', 'Leuchtpunkt auf dem Korn', 'oben am Korn', bevel=0,
              axis='f', c=(cu - 1.4, 0), a0=ff - 0.5, a1=ff + 0.1, r=0.9 * s, segs=16)]
    if parent:
        for p in P:
            p['parent_part'] = parent
    return P, _irons_anchor(fr, ff, cu, deck)


def iron_hoerner(size='M'):
    """K2 „Hörner“ (Schrot): Kimmenblock 22 × 8 mit zwei Flachblatt-Hörnern 3 mm, 20° nach außen, Spitzen auf Linie + 4 (Merkmal 1);
    oranger Kornkopf Ø 3,6 mit flacher Stirn zum Auge (Merkmal 2)."""
    s = {'S': 0.85, 'M': 1.0, 'L': 1.2}[size]
    fr, ff, cu = 20, 330, CU_IRON
    b0 = DECK + 8
    h = cu + 4 * s - b0
    tn = math.tan(math.radians(20)) * h
    horns = [[(x * 3.2 * s, b0 - CU_IRON - 0.5), (x * 6.4 * s, b0 - CU_IRON - 0.5), (x * (6.4 * s + tn), 4 * s - 1.2), (x * (3.2 * s + tn), 4 * s)]
             for x in (1, -1)]
    P = [part('sight_rear', 'Kimmenblock', 'Rear block', 'sight', 'prof', MET, 'Block 22 × 8 mm', 'hinten auf der Schiene', bevel=0.6,
              pts=[(fr - 2, DECK - 0.5), (fr + 14, DECK - 0.5), (fr + 12, b0), (fr, b0)], w=22 * s),
         part('sight_clamp', 'Klemmhebel', 'Clamp lever', 'sight', 'prof', 'accent', 'Spannt den Block', 'links am Block', bevel=0.4,
              pts=[(fr, DECK + 0.8), (fr + 10, DECK + 0.8), (fr + 12, DECK + 3.2), (fr, DECK + 3.6)], w=1.8, x=11.4 * s)]
    P += [_x(f'sight_horn{"" if x > 0 else "_r"}', 'Horn', MET, fr + 2, fr + 5, hp, cu=cu, func='Flachblatt-Horn 3 mm')
          for x, hp in zip((1, -1), horns)]
    P += [part('sight_front', 'Korn', 'Front sight', 'sight', 'prof', MET, 'Schlankes Korn', 'vorn auf der Schiene', bevel=0.4,
               pts=[(ff - 7, DECK - 0.5), (ff + 6, DECK - 0.5), (ff + 2, cu - 1.6), (ff, cu - 1.6)], w=2.6),
          part('sight_glass', 'Kornkopf', 'Front bead', 'sight', 'cyl', 'accent', 'Oranger Kornkopf, Stirn flach zum Auge', 'oben am Korn',
               bevel=0.2, axis='f', c=(cu, 0), a0=ff - 1.2, a1=ff + 1.6, r=1.8 * s, segs=20)]
    return P, _irons_anchor(fr, ff)


# ------------------------------------------------------------------------------------------------ Katalog
# id → (Bau, Name, Waffentyp für die Hüftform des gezeichneten Absehens, Einsatz, prägende Merkmale)
KIT = {
    'holo_ref':      (holo_ref, 'H0 Referenz (BASIC-01 heute)', 'auto_rifle', 'Bezug für Höhe und Bauweise', 'offene Haube · Trapezsockel'),
    'holo_fase':     (holo_fase, 'H1 Fase', 'auto_rifle', 'Automatik, MG', 'gefaste Ecke oben rechts'),
    'holo_pille':    (holo_pille, 'H2 Pille', 'submachine_gun', 'MP', 'ohne Haube · Emitterblock, Kontur gezeichnet'),
    'holo_zinken':   (holo_zinken, 'H3 Zinken', 'trace_rifle', 'Spur, MP', 'geneigte Zinken, oben offen · Punkt zum Auge'),
    'holo_kasten':   (holo_kasten, 'H4 Kasten', 'pulse_rifle', 'Impuls', 'runde Dachecken, Seiten einwärts · Ziffernfeld'),
    'ring_haekke':   (ring_haekke, 'H5 Häkke-Ring', 'pulse_rifle', 'Impuls, Automatik leicht', 'Lücke oben · Nasen 3/9 Uhr'),
    'fusion_boegen': (fusion_boegen, 'F1 Bögen', 'fusion_rifle', 'Fusion', 'versetzte Bögen (S-Öffnung) · Ladebalken'),
    'mini_reflex':   (mini_reflex, 'M1 Mini', 'hand_cannon', 'Seitenwaffe, Handfeuerwaffe (wahlweise)', 'kleinste Haube, kurze Plattform'),
    'launcher_d':    (launcher_d, 'W1 D-Linse', 'grenade_launcher', 'Granatwerfer', 'D-Haube mit oranger Kerbe · Fallmarken'),
    'rocket_kasten': (rocket_kasten, 'W2 Entfernung', 'rocket_launcher', 'Raketenwerfer', 'Schutzdach · Entfernungsfeld'),
    'scope_tropfen': (scope_tropfen, 'Z1 Tropfen', 'scout_rifle', 'Scout (Standard)', 'Tropfensockel · blanker Absatz'),
    'scope_gabel':   (scope_gabel, 'Z2 Gabel', 'linear_fusion_rifle', 'Lineare Fusion, Scout', 'U-Gabel mit Abstand · Laschen'),
    'sniper_lang':   (sniper_lang, 'Z3 Lang', 'sniper_rifle', 'Scharfschütze (Vollbild)', 'Sonnenblende · Duplex im Vollbild'),
    'iron_klammer':  (iron_klammer, 'K1 Klammer', 'hand_cannon', 'Handfeuerwaffe, Seitenwaffe', 'Leuchtklammern bündig · Kornpunkt'),
    'iron_hoerner':  (iron_hoerner, 'K2 Hörner', 'shotgun', 'Schrot', 'Flachblatt-Hörner · oranger Kornkopf'),
}
SIZED = ('holo_fase', 'ring_haekke', 'scope_tropfen', 'iron_klammer')     # im Blatt zusätzlich in S und L


def weapon(kid, size='M'):
    build, name, wtype, use, feat = KIT[kid]
    P, A = build(size)
    irons = kid.startswith('iron')
    rail = dict(deck_f0=-90, deck_f1=110) if kid.startswith(('scope', 'sniper')) else dict(deck_f0=-30, deck_f1=60)
    return types.SimpleNamespace(META=dict(id=f'KIT-{kid}-{size}', name=name, type=wtype, variant=size),
                                 ASSEMBLIES=[dict(id='receiver'), dict(id='barrel'), dict(id='sight')],
                                 PARTS=stub(front_deck=irons, **rail) + P, ANCHORS=A, ACTIONS={}, EXPLODE={}, BORE=BORE,
                                 __doc__=build.__doc__)
