"""Visier-Baukasten v3 – Katalog und Entwürfe. Nutzer 26.10.2026: „unterschiedliche Visiere anlegen, verschiedene Formen, Größen usw.,
die wir später verwenden können. Für manche Waffen fehlen ja Visiere auch noch“; zu v1: „fast alle zu klotzig … viel zu hoch“; zu
v2: „Das Visier von BASIC-01 sieht so um Welten besser aus als die neuen“; Leitlinie: „Visier vom aktuellen Automatikgewehr von der
Höhe optimal und vom Design gut. Daran sollte man sich orientieren“; Auftrag: „ein bis zwei prägende Designelemente je Visier …
schlicht, funktional und gut lesbar … sichtbar voneinander unterscheiden … Sichtfeld und Zielerfassung müssen klar bleiben.“

Seit 0.21 „Ironsight“ (Nutzerwahl „v3 bauen“) ist der Baukasten Produktionsform in `basic/common.py`: H0-Plattform
(`sight_platform`), Flachprofil `xprof` (Form in `kit.py`), Haube, Glas, gezeichnetes Absehen und die gebauten Visiere H0
(`reflex_sight_v21`), H2 Pille, H4 Kasten, Z1 Tropfen (Sitz nach Konzept A); seit 0.33 „Armory“ auch alle übrigen Produktionsvisiere
(H3 Zinken, H6 Achteck, F1 Bögen, W1 D-Linse, W2 Entfernung, Z2 Gabel, Z3 Lang, K1 Klammer, K2 Hörner, B1 Pins, `side_mount`). Dieses Modul stellt sie auf einem neutralen Prüfkörper
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
from basic.common import (zinken, ZINKEN_SIZES, ZINKEN_DEG, boegen, BOEGEN_SIZES, achteck, ACHTECK_SIZES, _oct,  # noqa: F401
                          WERFER_T, DLINSE_SIZES, DLINSE_TOP, _dshape, dlinse_wall_x, d_linse, ENTF_SIZES, ENTF_ROOF,
                          ENTF_OVERHANG, entfernung, side_mount, gabel, LANG_SIZES, LANG_TUBE_R, FULLSCREEN, lang,
                          IRON_EYE_MM, KLAMMER_SIZES, klammer, HOERNER_SIZES, hoerner, PINS_SIZES, PINS_LINE,
                          PINS_STEP, PINS_HEAD, PINS_EYE_MM, PINS_T, PINS_DEPTH, PINS_CAP, pins)
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
    """H3 „Zinken“ auf dem Prüfkörper (Katalogblatt, test_sights); gebaut von `zinken` (seit 0.27 an BASIC-12 v2.1)."""
    return zinken(F, DECK, size)


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
    """F1 „Bögen“ auf dem Prüfkörper (Katalogblatt, test_sights); gebaut von `boegen` (seit 0.26 an BASIC-10 v2.1)."""
    return boegen(F, DECK, size)


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
    """W1 „D-Linse“ auf dem Prüfkörper (Katalogblatt, test_sights); gebaut von `d_linse` (seit 0.28 an BASIC-13 v2.1)."""
    return d_linse(F, DECK, size)


def rocket_kasten(size='M'):
    """W2 „Entfernung“ auf dem Prüfkörper (Katalogblatt, test_sights); gebaut von `entfernung` (seit 0.28 an BASIC-14 v2.1)."""
    return entfernung(F, DECK, size)


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
    """Z2 „Gabel“ auf dem Prüfkörper (Katalogblatt, test_sights); gebaut von `gabel` (seit 0.26 an BASIC-11 v2.1)."""
    return gabel(72, DECK, CU, size)


def sniper_lang(size='M'):
    """Z3 „Lang“ auf dem Prüfkörper (Katalogblatt, test_sights); gebaut von `lang` (seit 0.25 an BASIC-09 v2.1)."""
    return lang(100, DECK, CU, size)


# ------------------------------------------------------------------------------------------------ Kimme/Korn
def _irons_anchor(fr, ff, cu=CU_IRON, deck=DECK):
    """Anker von Kimme/Korn (common._irons_anchor) mit der Linie des Prüfkörpers als Vorgabe."""
    return C._irons_anchor(fr, ff, cu, deck)


def iron_klammer(size='M'):
    """K1 „Klammer“ auf dem Prüfkörper (Katalogblatt, test_sights); gebaut von `klammer`."""
    return klammer(20, 330, DECK, size)


def iron_hoerner(size='M'):
    """K2 „Hörner“ auf dem Prüfkörper (Katalogblatt, test_sights); gebaut von `hoerner` (seit 0.25 an BASIC-08 v2.1)."""
    return hoerner(20, 330, DECK, size)


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


# ------------------------------------------------------------------------------------------------ Bogen