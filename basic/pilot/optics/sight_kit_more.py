"""Visier-Baukasten v3 – weitere Varianten (Entwurf). Nutzer 26.10.2026: „mehr Varianten“; Vorgaben wie `sight_kit.py`:
„mehr Eigenständigkeit und bewusst gestaltete Details … schlicht, funktional und gut lesbar … ein bis zwei prägende
Designelemente … Sichtfeld und Zielerfassung müssen klar bleiben“; Höhe und Bauweise wie H0 (BASIC-01).

Gleiche Regeln wie `sight_kit.py`: H0-Plattform (`platform`) bzw. `_scope_body` + `_scope_foot`, Flachprofile (`_x`/`_hood`) mit
blanker Stirnkante, Material `MET` und höchstens ein Akzent, Glas `glass_scope` flach, Visierlinie `CU` (Kimme/Korn `CU_IRON`,
Mini `CU_MINI`). Neu je Visier nur Rahmenkontur und ein Funktionsdetail (`KIT` › Merkmale). tools/sight_catalog.py lädt dieses
Modul selbst. Koordinaten wie dort: f nach vorn, u nach oben, x nach links (aus Augensicht).
"""
import math
import types

from basic.common import part, cyl, prof
from basic.pilot.optics.sight_kit import (CU, CU_IRON, CU_MINI, DECK, F, MET, REL, T, HOLO_SIZES, SCOPE_SIZES, stub, _arc,
                                          _rr, _sector, _x, _hood, _glass, _eye, platform, _scope_body, _scope_foot,
                                          _scope_anchors, _irons_anchor, BORE, achteck)


def _iron_foot(fr, top):
    """Flacher Kimmenfuß wie K1 (zweistufig) mit orangem Hebel."""
    return [part('sight_mount', 'Kimmenfuß', 'Rear base', 'sight', 'multi', MET, 'Flacher Fuß, gestuft', 'hinten auf der Schiene',
                 bevel=0.8, items=[dict(shape='box', f0=fr - 4, f1=fr + 16, u0=DECK + 0.5, u1=DECK + 3.5, w=23),
                                   dict(shape='box', f0=fr - 2, f1=fr + 12, u0=DECK + 3, u1=top, w=16)]),
            part('sight_clamp', 'Klemmhebel', 'Clamp lever', 'sight', 'prof', 'accent', 'Spannt den Fuß', 'links am Fuß', bevel=0.4,
                 pts=[(fr, DECK + 0.8), (fr + 12, DECK + 0.8), (fr + 14, DECK + 3.2), (fr, DECK + 3.6)], w=1.8, x=12.4)]


# ------------------------------------------------------------------------------------------------ Holo
def holo_octagon(size='M'):
    """H6 „Achteck“ auf dem Prüfkörper (Katalogblatt, test_sights); gebaut von `sight_kit.achteck` (seit 0.27 an BASIC-15 v2.1, Größe L)."""
    return achteck(F, DECK, size)


def holo_visor(size='M'):
    """H7 „Schirm“ (Automatik, Spur): H0-Haube, deren Dach 11 mm über die Stirn nach vorn auskragt und seitlich 1 mm übersteht –
    Sonnenschild, unten zur Spitze verjüngt (Merkmal 1, von hinten verdeckt); Schildkante vorn orange (Merkmal 2)."""
    w, h = HOLO_SIZES[size]
    gb = CU - h / 2 - 0.4
    inner, outer = _rr(w, h, 2.0), _rr(w + 2 * T, h + 2 * T, 2.0 + T)
    fr, depth = F + 34, 12
    fe = fr + depth
    ut = CU + h / 2 + T
    ww = w + 2 * T + 2
    visor = prof('sight_visor', 'Sonnenschild', 'Sun visor', 'sight', MET, 'Dach kragt 11 mm nach vorn aus', 'auf der Haube',
                 [(fr + 1, ut - T), (fe + 3, ut - T), (fe + 10.6, ut - 0.7), (fe + 10.6, ut), (fr + 1, ut)], ww, bevel=0.4)
    edge = prof('sight_visor_edge', 'Schildkante', 'Visor edge', 'sight', 'accent', 'Orange Vorderkante des Schilds', 'vorn am Schild',
                [(fe + 9.8, ut - 0.85), (fe + 11.0, ut - 0.7), (fe + 11.0, ut + 0.05), (fe + 9.8, ut + 0.05)], ww + 0.1, bevel=0.15)
    return platform(w + 2 * T, gb) + _hood(inner, outer, fr=fr, depth=depth) + [visor, edge, _glass(F + 40, inner)], _eye(F + 40.4)


def holo_crescent(size='M'):
    """H8 „Halbmond“ (Seitenwaffe): Mini-Plattform, Haube als Sichel – links geschlossen und 3,2 mm kräftig, nach oben und unten
    auf 1,3 mm auslaufend, rechts offen (Merkmal 1, asymmetrisch); obere Sichelspitze orange (Merkmal 2). Tiefe Linie wie M1."""
    r = {'S': 7.0, 'M': 8.5, 'L': 10.0}[size]
    k = 0.7
    cu = CU_MINI
    gb = cu - r - 0.4
    a0, a1, n = -138, 138, 44

    def t(a):
        return 2.1 + 1.1 * math.cos(math.radians(a))

    def sickle(b0, b1, grow=0.0):
        outer = [((r + t(a) + grow) * math.cos(math.radians(a)), (r + t(a) + grow) * math.sin(math.radians(a)))
                 for a in (b0 + (b1 - b0) * i / n for i in range(n + 1))]
        inner = [((r - grow) * math.cos(math.radians(a)), (r - grow) * math.sin(math.radians(a)))
                 for a in (b1 - (b1 - b0) * i / n for i in range(n + 1))]
        return outer + inner
    fr = F + 46 * k - 12 + 0.6
    crescent = sickle(a0, a1)
    P = platform(2 * r, gb, k=k) + [
        _x('sight_frame', 'Sichelhaube', MET, fr, fr + 9, crescent, cu=cu, func='Sichel, rechts offen'),
        _x('sight_frame_trim', 'Stirnkante', 'trim', fr + 8.6, fr + 9.6, crescent, cu=cu, bevel=0.2),
        _x('sight_tip', 'Sichelspitze', 'accent', fr - 0.2, fr + 9.8, sickle(a1 - 14, a1 + 0.3, grow=0.12), cu=cu,
           func='Orange Spitze oben', bevel=0.15),
        _glass(fr + 5, _arc(r - 0.6, a0, a1, 44), cu=cu)]
    return P, _eye(fr + 5.4, cu=cu)


def holo_flipcap(size='M'):
    """H9 „Klappe“ (Spur, MP): H0-Haube mit Schutzdeckel, der links an einem blanken Scharnier 100° aufgeklappt neben der Haube nach
    vorn steht – im Zielen ganz hinter der Haube (Merkmal 1); orange Grifflasche am freien Ende (Merkmal 2)."""
    w, h = HOLO_SIZES[size]
    gb = CU - h / 2 - 0.4
    inner, outer = _rr(w, h, 2.5), _rr(w + 2 * T, h + 2 * T, 2.5 + T)
    fr, depth = F + 34, 11
    fe = fr + depth
    xh, fh = w / 2 + T + 1.3, fe - 1.6
    th = math.radians(10)
    d, nrm = (math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th))
    L, tk = w + 2 * T - 1, 1.2
    s = (fh + 1.0 - 0.6 * nrm[0], xh - 0.6 * nrm[1])

    def quad(l0, l1):
        p0 = (s[0] + l0 * d[0], s[1] + l0 * d[1])
        p1 = (s[0] + l1 * d[0], s[1] + l1 * d[1])
        return [p0, p1, (p1[0] + tk * nrm[0], p1[1] + tk * nrm[1]), (p0[0] + tk * nrm[0], p0[1] + tk * nrm[1])]
    hu0, hu1 = CU - h / 2 - T + 0.6, CU + h / 2 + T - 0.6
    P = platform(w + 2 * T, gb) + _hood(inner, outer, fr=fr, depth=depth) + [
        cyl('sight_hinge', 'Scharnier', 'Hinge', 'sight', 'trim', 'Senkrechtes Deckelscharnier', 'vorn links an der Haube', 'u',
            (fh, xh), hu0, hu1, 1.3, segs=16, bevel=0.2),
        part('sight_cap', 'Schutzdeckel', 'Lens cap', 'sight', 'plan', MET, 'Deckel 100° offen, steht neben der Haube',
             'am Scharnier', bevel=0.4, pts=quad(0, L), u0=hu0 + 0.4, u1=hu1 - 0.4),
        part('sight_cap_tab', 'Grifflasche', 'Cap tab', 'sight', 'plan', 'accent', 'Orange Lasche zum Schließen', 'am Deckelende',
             bevel=0.3, pts=quad(L - 0.5, L + 3.5), u0=CU - 3, u1=CU + 3),
        _glass(F + 40, inner)]
    return P, _eye(F + 40.4)


def bow_pins(size='M'):
    """B1 „Pins“ (Bogen): kurze H0-Plattform ohne Glas; Ring aus Flachprofil 1,8 × 8, rechts abgeflacht als Pinschiene (Merkmal 2);
    drei waagerechte Pins von rechts mit Leuchtköpfen in der Mitte, 0/−4,5/−9 mm, Köpfe kleiner werdend (Merkmal 1). Die Pins
    sind das Absehen (kein gezeichnetes)."""
    r = {'S': 10.0, 'M': 12.0, 'L': 14.0}[size]
    t, k = 1.8, 0.85
    cap = 0.72 * r
    gb = CU - r - 0.4

    def d_ring(rr, cp):
        return [(max(x, -cp), u) for x, u in _arc(rr, 0, 360, 72)[:-1]]
    inner, outer = d_ring(r, cap), d_ring(r + t, cap + t)
    fr = F + 46 * k - 9.4
    P = platform(14, gb, k=k, emitter=False) + _hood(inner, outer, fr=fr, depth=8)
    fp = fr + 4
    for i, (du, rd) in enumerate(((0.0, 1.15), (-4.5, 0.95), (-9.0, 0.8))):
        du *= r / 12
        xs = -min(cap, math.sqrt(max(r * r - du * du, 0)))
        P += [_x(f'sight_pin_blade_{i}', 'Pin', MET, fp - 1.0, fp + 1.0, [(xs - 0.4, du - 0.45), (-0.6, du - 0.45), (-0.6, du + 0.45),
                                                                         (xs - 0.4, du + 0.45)], func='Waagerechter Pin', bevel=0.15),
              cyl('sight_pin' if i == 0 else f'sight_pin_{i}', 'Pinkopf', 'Pin head', 'sight', 'energy', 'Leuchtkopf (Zielpunkt)',
                  'am Pin', 'f', (CU + du, 0), fp - 1.3, fp + 1.3, rd, segs=20, bevel=0.1)]
    return P, {'Socket_Reticle': dict(at=(fp, CU, 0), part='sight_pin'),
               'Socket_Eye': dict(at=(fp - REL, CU, 0), part='sight_pin', sight_type='iron', std=False,
                                  note=f'Augenpunkt {REL} mm hinter den Pins; die Pins sind das Absehen')}


def fusion_rings(size='M'):
    """F2 „Doppelring“ (Fusion): zwei konzentrische Ringe aus Flachprofil 1,6 mit 2,5 mm Spalt, der äußere 7 mm, der innere 12 mm
    tief (Merkmal 1, gestuft); im Spalt oben ein Leuchtbogen 60° als Ladeanzeige zwischen zwei Stegen auf 2 und 10 Uhr (Merkmal 2)."""
    r = {'S': 9.5, 'M': 11.0, 'L': 14.0}[size]
    ri1 = r + T
    ro0 = ri1 + 2.5
    ro1 = ro0 + T
    fr = F + 34
    gb = CU - r - 0.4
    inner_ring = _arc(ri1, 0, 360, 64)[:-1]
    outer_full = _arc(ro1, 0, 360, 72)[:-1]

    def spoke(a):
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        return [((ri1 - 0.3) * c - 1.2 * -s, (ri1 - 0.3) * s - 1.2 * c), ((ro0 + 0.3) * c - 1.2 * -s, (ro0 + 0.3) * s - 1.2 * c),
                ((ro0 + 0.3) * c + 1.2 * -s, (ro0 + 0.3) * s + 1.2 * c), ((ri1 - 0.3) * c + 1.2 * -s, (ri1 - 0.3) * s + 1.2 * c)]
    P = platform(16, gb) + [
        _x('sight_frame', 'Innenring', MET, fr, fr + 12, inner_ring, holes=[_arc(r, 0, 360, 64)[:-1]], func='Innenring 1,6 × 12'),
        _x('sight_frame_trim', 'Stirnkante innen', 'trim', fr + 11.6, fr + 12.6, inner_ring, holes=[_arc(r, 0, 360, 64)[:-1]], bevel=0.2),
        _x('sight_frame_b', 'Außenring', MET, fr + 5, fr + 12, outer_full, holes=[_arc(ro0, 0, 360, 72)[:-1]], func='Außenring 1,6 × 7'),
        _x('sight_frame_trim_b', 'Stirnkante außen', 'trim', fr + 11.6, fr + 12.6, outer_full, holes=[_arc(ro0, 0, 360, 72)[:-1]],
           bevel=0.2),
        _x('sight_web', 'Steg', MET, fr + 5, fr + 12, spoke(30)), _x('sight_web_r', 'Steg', MET, fr + 5, fr + 12, spoke(150)),
        _x('sight_charge', 'Ladebogen', 'energy', fr + 6, fr + 11.4, _sector(ri1 + 0.5, ro0 - 0.5, 62, 118, 24),
           func='Ladeanzeige im Spalt', bevel=0.1),
        _glass(F + 40, _arc(r + 0.4, 0, 360, 64)[:-1])]
    return P, _eye(F + 40.4)


# ------------------------------------------------------------------------------------------------ Zielfernrohr
def scope_prism(size='M'):
    """Z4 „Prisma“ (Impuls, Scout kurz): kurzes, niedriges Kastenfernrohr 64 mm – Objektivkasten als Rundrechteck 30 × 22 (Stirn 2)
    mit blanker Innenkante, steht über das schmalere Gehäuse 24 × 20 hinaus, Unterkanten bündig (Merkmal 1); Leuchtstreifen oben
    auf dem Gehäuse (Merkmal 2, Beleuchtung an)."""
    s = {'S': 0.88, 'M': 1.0, 'L': 1.15}[size]
    f_obj = 72
    wi, hi = 30 * s, 22 * s
    wo, ho = wi + 4, hi + 4
    bot = CU - ho / 2
    bw, bh = 24 * s, 20 * s
    cb = bot + bh / 2
    P = [_x('scope_eyepiece', 'Okular', MET, f_obj - 64, f_obj - 55.5, _rr(bw - 2, bh - 2, 4), cu=cb, holes=[_rr(bw - 8, bh - 8, 3)],
            func='Okular (Rundrechteck)', ads_hide=True),
         _x('scope_tube', 'Prismengehäuse', MET, f_obj - 56, f_obj - 13.5, _rr(bw, bh, 4), cu=cb, func='Schmales Kastengehäuse',
            ads_hide=True),
         part('scope_glow', 'Leuchtstreifen', 'Glow strip', 'sight', 'box', 'energy', 'Beleuchtung an', 'oben auf dem Gehäuse',
              bevel=0.2, f0=f_obj - 46, f1=f_obj - 24, u0=cb + bh / 2 - 0.4, u1=cb + bh / 2 + 0.25, w=2.2, ads_hide=True),
         _x('scope_rim', 'Objektivrahmen', MET, f_obj - 14, f_obj, _rr(wo, ho, 5), holes=[_rr(wi, hi, 3)],
            func='Rundrechteck mit 2 mm Flansch'),
         _x('scope_crown', 'Objektivkante', 'trim', f_obj - 3, f_obj + 0.1, _rr(wi + 1.2, hi + 1.2, 3.5), holes=[_rr(wi, hi, 3)],
            func='Blanke Innenkante', bevel=0.1),
         _x('scope_glass', 'Objektivscheibe', 'glass_scope', f_obj - 4, f_obj - 3.4, _rr(wi + 0.4, hi + 0.4, 3.2),
            func='Scheibe ohne Spiegelung', bevel=0)]
    return P + _scope_foot(f_obj - 52, f_obj - 4, bot + 0.3), _scope_anchors(f_obj)


def scope_peak(size='M'):
    """Z5 „Spitze“ (Scout): flacher Ring (außen/innen 1,22) mit einfachem Objektivkegel; die Ringkontur läuft oben tangential in eine
    flache Spitze (Merkmal 1, Gegenstück zum Tropfen Z1); Spitze orange als Schnellzielmarke (Merkmal 2)."""
    r_in = SCOPE_SIZES[size]
    r_out = r_in * 1.22
    f_obj = 72
    bt = DECK + 6
    b = bt - CU
    phi = 32
    rt = r_out * 0.95
    apex = rt / math.cos(math.radians(phi))
    t1 = (rt * math.cos(math.radians(90 - phi)), rt * math.sin(math.radians(90 - phi)))
    t2 = (-t1[0], t1[1])
    fin = [(0.0, apex), t2] + _arc(r_in + 1.2, 90 + phi, 90 - phi, 16) + [t1]
    tip_h = 2.6
    xx = tip_h * math.tan(math.asin(rt / apex))
    tip = [(0.0, apex + 0.18), (xx + 0.3, apex - tip_h), (-xx - 0.3, apex - tip_h)]
    keel = [(8, b), (-8, b), (-5.5, -r_out * 0.93 + 1.6), (5.5, -r_out * 0.93 + 1.6)]
    return _scope_body(f_obj, r_in, r_out, step=False) + _scope_foot(f_obj - 30, f_obj, bt) + [
        cyl('scope_rim', 'Objektivring', 'Objective ring', 'sight', MET, 'Flacher Stirnring', 'vorn', 'f', (CU, 0), f_obj - 6, f_obj,
            r_out * (REL - 6) / REL - 0.1, r1=r_out, r_in=r_in, segs=64, bevel=0.5),
        cyl('scope_crown', 'Objektivkante', 'Objective trim', 'sight', 'trim', 'Blanke Innenkante', 'innen am Ring', 'f', (CU, 0),
            f_obj - 3, f_obj + 0.1, r_in + 0.5, r_in=r_in, segs=64, bevel=0.1),
        _x('scope_peak', 'Spitze', MET, f_obj - 6, f_obj, fin, func='Ring läuft oben tangential in eine Spitze'),
        _x('scope_peak_tip', 'Spitzenmarke', 'accent', f_obj - 6.3, f_obj + 0.3, tip, func='Orange Schnellzielmarke', bevel=0.15),
        _x('scope_keel', 'Sockel', MET, f_obj - 16, f_obj - 2, keel, func='Schlanker Trapezsockel')], _scope_anchors(f_obj)


# ------------------------------------------------------------------------------------------------ Kimme/Korn
def iron_ghost(size='M'):
    """K3 „Lochkimme“ (Schrot): Ghost-Ring – Lochblatt 4,5 mm dick, Loch Ø 8,4, Stirn 2,2, unten mit Schultern in den flachen Fuß
    auslaufend, blanke Lochkante zum Auge (Merkmal 1); vorn ein Kornring Ø 9,6 um ein Korn mit oranger Spitze – im Zielen zwei
    konzentrische Ringe (Merkmal 2)."""
    s = {'S': 0.85, 'M': 1.0, 'L': 1.2}[size]
    fr, ff, cu = 20, 330, CU_IRON
    top = DECK + 5
    ri, ro = 4.2 * s, 6.4 * s
    bu = top - 0.5 - cu
    blade = _arc(ro, -48, 228, 40) + [(-9.5 * s, bu), (9.5 * s, bu)]
    hole = _arc(ri, 0, 360, 40)[:-1]
    fb = DECK + 2.5 - cu
    hood = _arc(4.8, -55, 235, 32) + [(-4.6, fb), (4.6, fb)]
    P = _iron_foot(fr, top) + [
        _x('sight_rear', 'Lochblatt', MET, fr, fr + 4.5, blade, cu=cu, holes=[hole], func='Ghost-Ring mit Schultern', bevel=0.5),
        _x('sight_rear_trim', 'Lochkante', 'trim', fr - 0.3, fr + 0.6, _arc(ri + 0.7, 0, 360, 40)[:-1], cu=cu, holes=[hole],
           func='Blanke Lochkante zum Auge', bevel=0.1),
        part('sight_front', 'Kornfuß', 'Front base', 'sight', 'box', MET, 'Flacher Fuß', 'vorn auf der Schiene', bevel=0.4,
             f0=ff - 8, f1=ff + 8, u0=DECK - 0.5, u1=DECK + 2.5, w=12),
        _x('sight_front_hood', 'Kornring', MET, ff - 3, ff + 3, hood, cu=cu, holes=[_arc(3.6, 0, 360, 32)[:-1]], func='Kornring Ø 9,6'),
        part('sight_post', 'Korn', 'Front post', 'sight', 'prof', MET, 'Schlankes Korn im Ring', 'im Kornring', bevel=0.2,
             pts=[(ff - 1.6, cu - 4.0), (ff + 1.6, cu - 4.0), (ff + 0.6, cu - 1.3), (ff - 0.6, cu - 1.3)], w=1.5),
        part('sight_glass', 'Kornspitze', 'Post tip', 'sight', 'prof', 'accent', 'Orange Kornspitze, Oberkante auf der Linie',
             'oben am Korn', bevel=0.15, pts=[(ff - 0.7, cu - 1.4), (ff + 0.7, cu - 1.4), (ff + 0.6, cu), (ff - 0.6, cu)], w=1.6)]
    return P, _irons_anchor(fr, ff)


def launcher_ladder(size='M'):
    """W3 „Leiter“ (Granatwerfer): Klappkimme als schmale Leiter aus Flachprofil 2,4 (Wange 1,6) – drei Sprossen mit Kimmenkerbe auf 0/4,4/8,8 mm über der
    Linie, unten ein blankes Querscharnier (Merkmal 1); auf jeder Sprosse 1/2/3 blanke Striche als Entfernungsstufe (Merkmal 2).
    Korn schlank mit oranger Spitze."""
    s = {'S': 0.85, 'M': 1.0, 'L': 1.2}[size]
    fr, ff, cu = 20, 330, CU_IRON
    top = DECK + 4
    hw, iw, rung = 6.6 * s, 5.0 * s, 1.3
    b = top - 0.4 - cu
    ut = 13 * s
    outer = [(hw, b), (hw, ut - 1.6), (hw - 1.6, ut), (-hw + 1.6, ut), (-hw, ut - 1.6), (-hw, b)]
    levels = [0.0, 4.4 * s, 8.8 * s]
    tops = [4.4 * s - rung, 8.8 * s - rung, ut - 1.6]
    nw, nd = 1.0 * s, 1.1 * s
    holes = [[(iw, u0), (nw, u0), (nw, u0 - nd), (-nw, u0 - nd), (-nw, u0), (-iw, u0), (-iw, u1), (iw, u1)]
             for u0, u1 in zip(levels, tops)]
    marks = []
    for i, u0 in enumerate(levels):
        for j in range(i + 1):
            marks.append(dict(shape='box', f0=fr - 0.25, f1=fr + 0.2, u0=cu + u0 - 1.15, u1=cu + u0 - 0.2, w=0.5,
                              x=nw + 0.9 + j * 0.9))
    P = _iron_foot(fr, top) + [
        cyl('sight_hinge', 'Scharnier', 'Hinge', 'sight', 'trim', 'Querscharnier der Klappkimme', 'unten an der Leiter', 'x',
            (fr + 1.2, top + 1.0), -hw - 0.6, hw + 0.6, 1.3, segs=16, bevel=0.2),
        _x('sight_rear', 'Leiter', MET, fr, fr + 2.4, outer, cu=cu, holes=holes, func='Leiter mit drei Kerbensprossen', bevel=0.3),
        part('sight_status', 'Stufenstriche', 'Range strokes', 'sight', 'multi', 'trim', '1/2/3 Striche je Sprosse',
             'auf der Leiterrückseite', bevel=0, items=marks),
        part('sight_front', 'Korn', 'Front sight', 'sight', 'multi', MET, 'Schlankes Korn auf flachem Fuß', 'vorn auf der Schiene',
             bevel=0.4, items=[dict(shape='prof', pts=[(ff - 7, DECK - 0.5), (ff + 6, DECK - 0.5), (ff + 1.4, cu - 1.4), (ff - 0.6, cu - 1.4)],
                                    w=2.2),
                               dict(shape='box', f0=ff - 8, f1=ff + 8, u0=DECK - 0.5, u1=DECK + 2.5, w=12)]),
        part('sight_glass', 'Kornspitze', 'Post tip', 'sight', 'box', 'accent', 'Orange Kornspitze auf der Linie', 'oben am Korn',
             bevel=0.15, f0=ff - 0.8, f1=ff + 1.4, u0=cu - 1.5, u1=cu, w=2.2)]
    return P, _irons_anchor(fr, ff)


# ------------------------------------------------------------------------------------------------ Katalog
# id → (Bau, Name, Waffentyp für die Hüftform des gezeichneten Absehens, Einsatz, prägende Merkmale) – Format wie sight_kit.KIT
KIT = {
    'holo_octagon':    (holo_octagon, 'H6 Achteck', 'machine_gun', 'MG', 'schlanke Achteckhaube · blanke Fasenflächen'),
    'holo_visor':      (holo_visor, 'H7 Schirm', 'auto_rifle', 'Automatik, Spur', 'Sonnenschild nach vorn · orange Schildkante'),
    'holo_crescent':   (holo_crescent, 'H8 Halbmond', 'sidearm', 'Seitenwaffe', 'Sichelhaube, rechts offen · orange Spitze'),
    'holo_flipcap':    (holo_flipcap, 'H9 Klappe', 'trace_rifle', 'Spur, MP', 'Schutzdeckel seitlich offen · orange Lasche'),
    'fusion_rings':    (fusion_rings, 'F2 Doppelring', 'fusion_rifle', 'Fusion', 'konzentrische Ringe, gestuft · Ladebogen'),
    'bow_pins':        (bow_pins, 'B1 Pins', 'combat_bow', 'Bogen', 'drei Leuchtpins · Pinschiene rechts'),
    'scope_prism':     (scope_prism, 'Z4 Prisma', 'pulse_rifle', 'Impuls, Scout kurz', 'Kastenobjektiv mit Flansch · Leuchtstreifen'),
    'scope_peak':      (scope_peak, 'Z5 Spitze', 'scout_rifle', 'Scout', 'Ring mit Spitze oben · orange Marke'),
    'iron_ghost':      (iron_ghost, 'K3 Lochkimme', 'shotgun', 'Schrot', 'Ghost-Ring · Kornring (zwei Ringe)'),
    'launcher_ladder': (launcher_ladder, 'W3 Leiter', 'grenade_launcher', 'Granatwerfer', 'Klappleiter mit Kerben · Stufenstriche'),
}
SIZED = ('holo_octagon', 'scope_prism')      # im Blatt zusätzlich in S und L
IRONS = ('iron_ghost', 'launcher_ladder')


def weapon(kid, size='M'):
    build, name, wtype, use, feat = KIT[kid]
    P, A = build(size)
    rail = dict(deck_f0=-90, deck_f1=110) if kid.startswith('scope') else dict(deck_f0=-30, deck_f1=60)
    return types.SimpleNamespace(META=dict(id=f'KIT-{kid}-{size}', name=name, type=wtype, variant=size),
                                 ASSEMBLIES=[dict(id='receiver'), dict(id='barrel'), dict(id='sight')],
                                 PARTS=stub(front_deck=kid in IRONS, **rail) + P, ANCHORS=A, ACTIONS={}, EXPLODE={}, BORE=BORE,
                                 __doc__=build.__doc__)
