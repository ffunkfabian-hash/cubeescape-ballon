"""Gemeinsame BASIC-Baugruppen (reines Python, kein bpy).

Jede Funktion liefert Bauteil-Einträge (dict) für `PARTS`. Maße in mm, Seitenprofil (f nach vorn, u nach oben),
x nach links. Gleiche Funktion = gleiche Schnittstelle; Parameter nur dort, wo der Designvertrag sie erlaubt
(docs/designvertrag.md › Wiederkehrende Bauteile). Die Schnittstellen-IDs (`iface`) stehen in INTERFACES.
"""
import math

# Radienstufen des Designvertrags (mm)
R_BODY, R_MID, R_SMALL, R_FINE = 5.0, 3.0, 1.5, 0.8
SEAM = 1.0   # Fugenbreite zwischen getrennten Schalen

INTERFACES = {
    'BRI-22': dict(de='Schiene 22 mm (Oberseite Gehäuse)', en='Top rail 22 mm',
                   rule='Breite 22 mm, Höhe 8 mm, Klemmfuß 22 mm breit, Mindestlänge Klemmfuß 40 mm'),
    'BGM-1': dict(de='Griffmodul Typ 1 (Gewehrfamilie)', en='Grip module type 1',
                  rule='Oberkante 42 × 30 mm, Neigung 15° (oben nach vorn), Abzugsbügel bis f = +78 mm'),
    'BGM-P': dict(de='Griffmodul Pistole (Faustfeuerwaffen)', en='Pistol grip module',
                  rule='Neigung 18°, Magazin im Griff'),
    'BMW-R': dict(de='Magazinschacht Gewehr', en='Rifle magazine well', rule='Innenmaß 40 × 24 mm, Neigung je Waffe im Spec'),
    'BMZ-15': dict(de='Mündungsgewinde r 15', en='Muzzle mount r 15', rule='Laufende r 9 mm, Mündungsteil r 15 mm, Bohrung r 5 mm'),
}


def rot(pts, c, deg):
    """(f,u)-Punkte um c drehen; positiv = gegen den Uhrzeigersinn (unteres Ende wandert nach vorn)."""
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return [(c[0] + (f - c[0]) * ca - (u - c[1]) * sa, c[1] + (f - c[0]) * sa + (u - c[1]) * ca) for f, u in pts]


def rr(f0, f1, u0, u1, r=0):
    """Rechteck als Punktliste (Ecken hart; Rundung macht der Bevel)."""
    return [(f0, u0), (f1, u0), (f1, u1), (f0, u1)]


def part(pid, de, en, asm, shape, mat, func, attach, bevel=R_MID, move=None, iface=None, **geo):
    d = dict(id=pid, de=de, en=en, asm=asm, shape=shape, mat=mat, func=func, attach=attach, bevel=bevel)
    if move:
        d['move'] = move
    if iface:
        d['iface'] = iface
    d.update(geo)
    return d


# ------------------------------------------------------------------ Griffgruppe (Gewehrfamilie)

def grip_rifle(top=45, tilt=15, w=30, guard=True, trigger_f=None):
    """Pistolengriff, Abzug, Abzugsbügel. Socket_Hand (0,0) liegt auf der Griffachse."""
    t = math.tan(math.radians(tilt))

    def A(u, d):  # Punkt auf Griffachse in Höhe u, um d nach vorn versetzt
        return (u * t + d, u)
    grip = [A(top, -20), A(10, -22), A(-30, -24), A(-58, -22), A(-64, -16), A(-64, 18), A(-56, 21),
            A(-20, 18), A(10, 20), A(top, 21)]
    tf = trigger_f if trigger_f is not None else top * t + 32
    P = [part('grip', 'Pistolengriff', 'Pistol grip', 'grip_controls', 'prof', 'graphite',
              'Haupthand hält die Waffe; trägt Socket_Hand', 'mit Unterem Gehäuse verschraubt (fest)', bevel=R_BODY,
              iface='BGM-1', pts=grip, w=w)]
    P.append(part('trigger', 'Abzug', 'Trigger', 'grip_controls', 'prof', 'metal', 'Feuer auslösen (Zeigefinger)',
                  'Drehpunkt im Unteren Gehäuse', bevel=R_FINE,
                  move=dict(kind='rotate', pivot=(tf + 2, top - 3, 0), axis='x', range_deg=(0, -12), event='fire',
                            expect=((tf + 3, top - 26, 0), (-1, 0, 0))),
                  pts=[(tf, top - 1), (tf + 6, top - 1), (tf + 8, top - 16), (tf + 5, top - 27), (tf + 1, top - 26),
                       (tf + 3, top - 15)], w=7))
    if guard:
        g0, g1 = top * t + 18, tf + 40
        P.append(part('trigger_guard', 'Abzugsbügel', 'Trigger guard', 'grip_controls', 'prof', 'graphite',
                      'Schützt den Abzug, Fingerfreiraum ≥ 22 mm', 'Griff vorn und Unteres Gehäuse (fest)', bevel=R_SMALL,
                      pts=[(g0 - 4, top - 34), (g1, top - 34), (g1, top + 1), (g1 - 7, top + 1), (g1 - 7, top - 27),
                           (g0 - 2, top - 27)], w=12))
    return P


def selector(f, u, x=24.5):
    """Feuerwahlhebel (Akzent), links (+X); x = Mitte des Hebels (Seitenfläche + 1,5 mm)."""
    return [part('selector', 'Feuerwahlhebel', 'Fire selector', 'grip_controls', 'prof', 'accent',
                 'Sichern / Feuer, mit dem Daumen der Haupthand', 'Achse quer im Unteren Gehäuse', bevel=R_FINE,
                 move=dict(kind='rotate', pivot=(f, u, 0), axis='x', range_deg=(0, 90), event='safety'),
                 pts=[(f - 4, u - 4), (f + 4, u - 4), (f + 16, u - 2), (f + 16, u + 2), (f + 4, u + 4), (f - 4, u + 4)],
                 w=3, x=x)]


# ------------------------------------------------------------------ Schiene und Visiere

def rail(f0, f1, u, w=22):
    """Schiene BRI-22: flaches Band mit zwei Endstücken (kein Rillenmuster)."""
    return [part('rail', 'Schiene', 'Top rail', 'receiver', 'box', 'dark_metal', 'Aufnahme für Visiere (BRI-22)',
                 'auf Oberem Gehäuse (fest)', bevel=R_SMALL, iface='BRI-22', f0=f0, f1=f1, u0=u - 0.5, u1=u + 8, w=w)]


def reflex_sight(f, u, win_w=30, win_h=24):
    """Kleines Reflexvisier mit freier Durchsicht: Klemmfuß mit Klemmschraube, flaches Gehäuse mit Emitterblock hinten,
    Haubenrahmen vorn, Glas. f = Hinterkante Klemmfuß, u = Oberkante Schiene. Liefert (Teile, Anker, Visierlinie)."""
    base_top = u + 8
    cu = base_top + 9 + win_h / 2                 # Mitte Fenster = Visierlinie
    fr0, fr1 = f + 38, f + 50                     # Haubenrahmen (12 mm tief)
    P = [
        part('sight_mount', 'Visier-Klemmfuß', 'Sight mount', 'sight', 'box', 'dark_metal',
             'Klemmt das Visier auf die Schiene BRI-22', 'Klemmung auf Schiene (lösbar)', bevel=R_SMALL, iface='BRI-22',
             move=dict(kind='translate', pivot=(f + 25, u, 0), vector_mm=(0, 70, 0), event='swap_sight',
                       note='nach Lösen der Klemmschraube senkrecht abnehmen', removable=True),
             f0=f, f1=f + 50, u0=u + 0.5, u1=base_top, w=26),
        part('sight_clamp', 'Klemmschraube', 'Clamp screw', 'sight', 'cyl', 'dark_metal',
             'Spannt den Klemmfuß (Werkzeuglos, Rändel)', 'quer im Klemmfuß links', bevel=R_FINE, parent_part='sight_mount',
             axis='x', c=(f + 25, u + 4), a0=13, a1=19, r=5.5, segs=16),
        part('sight_body', 'Visiergehäuse', 'Sight housing', 'sight', 'prof', 'graphite',
             'Trägt Emitter und Batterie; hintere Kante = Socket_Sight', 'auf Klemmfuß (fest)', bevel=R_MID, parent_part='sight_mount',
             pts=[(f + 1, base_top - 0.5), (f + 50, base_top - 0.5), (f + 50, base_top + 5), (f + 17, base_top + 5),
                  (f + 13, base_top + 8), (f + 1, base_top + 8)], w=26),
        part('sight_frame', 'Haubenrahmen', 'Sight hood frame', 'sight', 'frame', 'graphite',
             'Hält und schützt das Glas; offener Rahmen für freie Durchsicht', 'auf Visiergehäuse (fest)', bevel=R_SMALL,
             parent_part='sight_mount', f0=fr0, f1=fr1, cu=cu, ow=win_w + 10, oh=win_h + 10, iw=win_w, ih=win_h, r_out=5, r_in=3),
        part('sight_glass', 'Visierglas', 'Sight glass', 'sight', 'xbox', 'glass',
             'Reflexscheibe; das Absehen erscheint auf ihr', 'im Rahmen (fest)', bevel=0, parent_part='sight_mount',
             f0=fr0 + 5.5, f1=fr0 + 6.5, cu=cu, ww=win_w + 1, hh=win_h + 1),
        part('sight_emitter', 'Emitter', 'Reticle emitter', 'sight', 'box', 'energy',
             'Leuchtfenster des Absehen-Projektors (zurückhaltend)', 'vorn im Emitterblock', bevel=0.3, parent_part='sight_mount',
             f0=f + 15.5, f1=f + 17.5, u0=base_top + 5.2, u1=base_top + 7.4, w=7),
    ]
    A = {'Socket_Sight': dict(at=(f + 1, cu, 0), part='sight_body', note='hinteres Visierende auf der Visierlinie'),
         'Socket_Reticle': dict(at=(fr0 + 6, cu, 0), part='sight_glass', note='Mitte Glas'),
         'Socket_Eye': dict(at=(fr0, cu, 0), part='sight_frame',
                            note='Vorschlag nach Formgen-Regel: hinterer Fensterrand (Reflexvisier ohne festen Augenabstand)')}
    return P, A, cu


def scope(f, u, length=190, r_obj=19, r_eye=16, r_tube=12, name='Zielfernrohr'):
    """Einfaches Zielfernrohr auf zwei Ringen (Präzisionswaffen)."""
    cu = u + 9 + 6 + r_obj + 2
    f_eye, f_obj = f, f + length
    P = [
        part('scope_mount_r', 'Zielfernrohr-Ring hinten', 'Scope ring rear', 'sight', 'box', 'dark_metal',
             'Klemmt das Rohr auf die Schiene BRI-22', 'Klemmung auf Schiene (lösbar)', bevel=R_SMALL, iface='BRI-22',
             f0=f + 40, f1=f + 62, u0=u + 0.5, u1=cu - r_tube + 1, w=24),
        part('scope_mount_f', 'Zielfernrohr-Ring vorn', 'Scope ring front', 'sight', 'box', 'dark_metal',
             'Klemmt das Rohr auf die Schiene BRI-22', 'Klemmung auf Schiene (lösbar)', bevel=R_SMALL, iface='BRI-22',
             f0=f + length - 72, f1=f + length - 50, u0=u + 0.5, u1=cu - r_tube + 1, w=24),
        part('scope_tube', 'Mittelrohr', 'Scope tube', 'sight', 'cyl', 'graphite', 'Verbindet Okular und Objektiv',
             'in den Ringen (fest)', bevel=R_FINE, axis='f', c=(cu, 0), a0=f + 30, a1=f + length - 40, r=r_tube, segs=32),
        part('scope_eyepiece', 'Okular', 'Eyepiece', 'sight', 'cyl', 'graphite', 'Augenseite; Socket_Eye dahinter',
             'am Mittelrohr (fest)', bevel=R_SMALL, axis='f', c=(cu, 0), a0=f_eye, a1=f + 32, r=r_eye, r1=r_tube + 1,
             r_in=r_eye - 3, segs=32),
        part('scope_objective', 'Objektiv', 'Objective bell', 'sight', 'cyl', 'graphite', 'Lichteintritt vorn',
             'am Mittelrohr (fest)', bevel=R_SMALL, axis='f', c=(cu, 0), a0=f + length - 42, a1=f_obj, r=r_tube + 1,
             r1=r_obj, r_in=r_obj - 3, segs=32),
        part('scope_turret', 'Verstellturm', 'Elevation turret', 'sight', 'cyl', 'accent',
             'Höhenverstellung (Akzent, Bedienelement)', 'oben am Mittelrohr (fest)', bevel=R_FINE, axis='u',
             c=(f + length / 2 - 10, 0), a0=cu + r_tube - 2, a1=cu + r_tube + 9, r=8, segs=24),
        part('scope_glass', 'Objektivglas', 'Objective lens', 'sight', 'cyl', 'glass', 'Linse; Absehen-Ebene',
             'im Objektiv (fest)', bevel=0, axis='f', c=(cu, 0), a0=f_obj - 6, a1=f_obj - 5, r=r_obj - 3, segs=32),
        part('scope_ocular_glass', 'Okularglas', 'Ocular lens', 'sight', 'cyl', 'glass', 'Augenlinse',
             'im Okular (fest)', bevel=0, axis='f', c=(cu, 0), a0=f_eye + 4, a1=f_eye + 5, r=r_eye - 3, segs=32),
    ]
    # Das ganze Zielfernrohr hängt am hinteren Ring; der Ring ist das abnehmbare Teil (beide Ringe lösen, senkrecht abnehmen)
    P[0]['move'] = dict(kind='translate', pivot=(f + 51, u, 0), vector_mm=(0, 80, 0), event='swap_sight',
                        note='beide Ringe lösen, Zielfernrohr senkrecht abnehmen', removable=True)
    for q in P[1:]:
        q['parent_part'] = 'scope_mount_r'
    A = {'Socket_Sight': dict(at=(f_eye, cu, 0), part='scope_eyepiece', note='hinteres Okularende auf der Visierlinie'),
         'Socket_Reticle': dict(at=(f_obj - 5.5, cu, 0), part='scope_glass', note='Mitte Objektivglas'),
         'Socket_Eye': dict(at=(f_eye - 70, cu, 0), part='scope_eyepiece', note='Vorschlag: Augenabstand 70 mm')}
    return P, A, cu


def iron_post(f, u, h=14, pid='front_post', de='Korn'):
    return [part(pid, de, 'Front sight post', 'sight', 'prof', 'graphite', 'Kimme-Korn-Notvisier vorn',
                 'auf dem Handschutz (fest)', bevel=R_FINE,
                 pts=[(f, u), (f + 14, u), (f + 10, u + h), (f + 4, u + h)], w=10)]


# ------------------------------------------------------------------ Magazin, Lauf

def rifle_mag(f_well, u_top, depth=40, length=118, tilt=8, w=24, curve=6, pid='magazine', rounds=True):
    """Gewehrmagazin: Körper (Creme), Bodenplatte (Graphit), sichtbare oberste Patrone.
    f_well = Hinterkante Schacht, u_top = Oberkante Magazin (im Schacht verborgen). Entnahme entlang der Magazinachse."""
    c = (f_well + depth / 2, u_top)
    body = [(f_well, u_top), (f_well + depth, u_top), (f_well + depth + curve, u_top - length),
            (f_well + curve, u_top - length)]
    base = [(f_well + curve - 2, u_top - length + 0.5), (f_well + depth + curve + 2, u_top - length + 0.5),
            (f_well + depth + curve + 2, u_top - length - 9), (f_well + curve - 2, u_top - length - 9)]
    ax = math.radians(-90 + tilt)
    path = (round(160 * math.cos(ax), 1), round(160 * math.sin(ax), 1), 0)
    mv = dict(kind='translate', pivot=(c[0], c[1], 0), vector_mm=path, event='reload',
              note='Entnahme entlang der Magazinachse nach unten; Schacht nach unten offen', removable=True)
    P = [part(pid, 'Magazin', 'Magazine', 'ammo', 'prof', 'shell', 'Hält die Patronen; entnehmbar',
              'rastet im Magazinschacht ein (lösbar, Magazinhalter)', bevel=R_MID, move=mv, iface='BMW-R',
              pts=rot(body, c, tilt), w=w),
         part(pid + '_base', 'Magazinboden', 'Magazine base plate', 'ammo', 'prof', 'graphite',
              'Greifkante zum Herausziehen', 'am Magazin (fest)', bevel=R_SMALL, parent_part=pid,
              pts=rot(base, c, tilt), w=w + 3)]
    if rounds:
        P.append(part(pid + '_round', 'Oberste Patrone', 'Top round', 'ammo', 'cyl', 'metal',
                      'Zeigt den Ladezustand im Schacht', 'im Magazin', bevel=R_FINE, parent_part=pid,
                      axis='f', c=(u_top + 3, 0), a0=f_well + 4, a1=f_well + depth - 6, r=4.5, segs=16))
    return P


def barrel(f0, f1, u, r=9, muzzle_len=50, muzzle_r=15, segs=24, muzzle_segs=8):
    P = [part('barrel', 'Lauf', 'Barrel', 'barrel', 'cyl', 'metal', 'Führt das Geschoss', 'im Gehäuse/Handschutz verschraubt',
              bevel=R_FINE, axis='f', c=(u, 0), a0=f0, a1=f1 - muzzle_len + 4, r=r, segs=segs),
         part('muzzle', 'Mündungsbremse', 'Muzzle brake', 'barrel', 'cyl', 'dark_metal',
              'Mündungsteil; Socket_Muzzle an der Stirnfläche', 'auf Laufende geschraubt (lösbar)', bevel=R_SMALL, iface='BMZ-15',
              axis='f', c=(u, 0), a0=f1 - muzzle_len, a1=f1, r=muzzle_r, r_in=5, segs=muzzle_segs)]
    return P


def charging_handle(f, u, x=26.5, travel=60):
    return [part('charging_handle', 'Ladehebel', 'Charging handle', 'mechanism', 'prof', 'accent',
                 'Verschluss spannen (Stützhand zieht nach hinten)', 'in Längsnut links (gleitet)', bevel=R_SMALL,
                 move=dict(kind='translate', pivot=(f, u, x), vector_mm=(-travel, 0, 0), event='charge'),
                 pts=[(f, u - 6), (f + 26, u - 6), (f + 30, u - 2), (f + 30, u + 2), (f + 26, u + 6), (f, u + 6)],
                 w=9, x=x)]


# ------------------------------------------------------------------ Kurzformen

def prof(pid, de, en, asm, mat, func, attach, pts, w, bevel=R_BODY, **kw):
    return part(pid, de, en, asm, 'prof', mat, func, attach, bevel=bevel, pts=pts, w=w, **kw)


def box(pid, de, en, asm, mat, func, attach, f0, f1, u0, u1, w, bevel=R_MID, **kw):
    return part(pid, de, en, asm, 'box', mat, func, attach, bevel=bevel, f0=f0, f1=f1, u0=u0, u1=u1, w=w, **kw)


def cyl(pid, de, en, asm, mat, func, attach, axis, c, a0, a1, r, bevel=R_FINE, **kw):
    return part(pid, de, en, asm, 'cyl', mat, func, attach, bevel=bevel, axis=axis, c=c, a0=a0, a1=a1, r=r, **kw)


# ------------------------------------------------------------------ Schaft S1 (Gewehrfamilie)

def stock_s1(f0, ua, s=1.0, cheek=True):
    """Schaft S1: Schaftverbindung, Schaftrohr, Schulterstütze, Wangenauflage, Schaftkappe.
    f0 = Hinterkante Gehäuse, ua = Laufachse. s streckt die Länge (1.0 = Automatikgewehr)."""
    L = lambda d: f0 - d * s  # noqa: E731
    P = [
        box('stock_joint', 'Schaftverbindung', 'Stock joint', 'stock', 'dark_metal', 'Verbindet Schaft und Gehäuse; Verriegelung',
            'Steckverbindung am Gehäuseende (fest)', f0 - 11, f0 + 1, ua - 22, ua + 20, 30, bevel=R_SMALL),
        box('stock_spine', 'Schaftrohr', 'Stock spine', 'stock', 'graphite', 'Trägt die Schulterstütze in Linie mit dem Lauf',
            'in der Schaftverbindung (fest)', L(92), f0 - 10, ua - 12, ua + 16, 28),
        prof('stock', 'Schulterstütze', 'Buttstock', 'stock', 'shell', 'Anlage an der Schulter, Wangenauflage oben',
             'auf dem Schaftrohr (fest)', [(L(86), ua - 14), (L(86), ua + 22), (L(156), ua + 24), (L(164), ua + 18),
                                         (L(164), ua - 78), (L(152), ua - 84)], 36),
        prof('butt_pad', 'Schaftkappe', 'Butt pad', 'stock', 'graphite', 'Rutschfeste Anlage an der Schulter',
             'auf das Schaftende gesteckt (fest)', [(L(163), ua - 88), (L(163), ua + 28), (L(176), ua + 26), (L(179), ua + 14),
                                                  (L(179), ua - 80), (L(176), ua - 86)], 40, bevel=R_MID),
    ]
    if cheek:
        P.append(box('cheek_rest', 'Wangenauflage', 'Cheek rest', 'stock', 'graphite', 'Anlage für die Wange beim Zielen',
                     'auf der Schulterstütze (fest)', L(146), L(80), ua + 20, ua + 30, 26))
    return P


# ------------------------------------------------------------------ Energiezelle

def energy_cell(pid, f0, f1, u0, u1, w, vec, de='Energiezelle', en='Energy cell', iface='BEC-1', window=True, x=0.0):
    """Austauschbare Energiezelle: Graphitkörper mit kleinem Ladefenster. vec = Entnahmeweg (f,u,x) mm."""
    P = [part(pid, de, en, 'ammo', 'box', 'dark_metal', 'Speichert die Ladungen; austauschbar',
              'rastet im Zellenschacht ein (lösbar)', bevel=R_MID, iface=iface,
              move=dict(kind='translate', pivot=((f0 + f1) / 2, (u0 + u1) / 2, x), vector_mm=vec, event='reload', removable=True),
              f0=f0, f1=f1, u0=u0, u1=u1, w=w, x=x)]
    if window:
        P.append(part(pid + '_window', 'Ladefenster', 'Charge window', 'ammo', 'box', 'energy', 'Zeigt den Ladezustand',
                      'in die Zelle eingelassen', bevel=0.3, parent_part=pid,
                      f0=f0 + (f1 - f0) * 0.25, f1=f1 - (f1 - f0) * 0.25, u0=(u0 + u1) / 2 - 2, u1=(u0 + u1) / 2 + 2,
                      w=1.0, x=x + w / 2 + 0.2))
    return P


INTERFACES['BEC-1'] = dict(de='Energiezelle Typ 1', en='Energy cell type 1', rule='Zellenschacht je Waffe; Maß im Spec')
INTERFACES['BST-1'] = dict(de='Schaft S1', en='Stock S1', rule='Schaftverbindung 30 × 42 mm am Gehäuseende, Laufachse mittig')


# ------------------------------------------------------------------ Kimme und Korn

def iron_sights(f_rear, f_front, u, h=10, gap=4.0):
    """Kimme (zwei Ohren mit Kerbe) und Korn; feste Visiermarken."""
    P = []
    for side, x in (('l', gap / 2 + 3), ('r', -(gap / 2 + 3))):
        P.append(prof(f'rear_sight_{side}', f'Kimme {"links" if side == "l" else "rechts"}', f'Rear sight {"left" if side == "l" else "right"}',
                      'sight', 'graphite', 'Hintere Visiermarke; die Kerbe dazwischen', 'auf Verschluss bzw. Rahmen (fest)',
                      [(f_rear, u - 1), (f_rear + 10, u - 1), (f_rear + 10, u + h), (f_rear + 2, u + h)], 6, bevel=R_FINE, x=x))
    P.append(prof('front_sight', 'Korn', 'Front sight', 'sight', 'graphite', 'Vordere Visiermarke',
                  'auf Lauf bzw. Verschluss (fest)', [(f_front, u - 1), (f_front + 8, u - 1), (f_front + 6, u + h), (f_front + 2, u + h)],
                  3, bevel=R_FINE))
    return P


ASM = {
    'receiver': ('Hauptgehäuse', 'Receiver'), 'barrel': ('Lauf / Emitter', 'Barrel / emitter'),
    'ammo': ('Munitionsversorgung', 'Ammunition feed'), 'sight': ('Visier', 'Sight'),
    'grip_controls': ('Griff und Bedienung', 'Grip and controls'), 'support': ('Stützbereich', 'Support'),
    'stock': ('Schaft', 'Stock'), 'mechanism': ('Bewegliche Mechanik', 'Moving mechanism'),
    'cooling': ('Kühlung', 'Cooling'), 'blade': ('Klinge', 'Blade'), 'guard': ('Parierblock', 'Guard'),
    'riser': ('Mittelstück', 'Riser'), 'limbs': ('Wurfarme', 'Limbs'), 'string': ('Sehne', 'String'),
    'arrow': ('Pfeil', 'Arrow'), 'shaft': ('Stange', 'Shaft'), 'shield': ('Schild', 'Shield'),
}


def assemblies(*ids):
    return [dict(id=i, de=ASM[i][0], en=ASM[i][1]) for i in ids]


def glow(pid, de, en, asm, f0, f1, u0, u1, w=1.0, x=0.0, func='Leuchtanzeige', attach='eingelassen', **kw):
    """Leuchtfeld, dessen Helligkeit in Aktionen gesteuert wird (Aufladen, Salve)."""
    return box(pid, de, en, asm, 'energy', func, attach, f0, f1, u0, u1, w, bevel=0.3, x=x,
               move=dict(kind='glow', pivot=None, event='charge', max=5.0), **kw)


def vents(prefix, asm, f_list, length, u0, u1, half_w, de='Lüftungsöffnung', en='Vent'):
    P = []
    for i, f0 in enumerate(f_list):
        for side, x in (('l', half_w - 0.1), ('r', -(half_w - 0.1))):
            P.append(box(f'{prefix}_{side}{i + 1}', f'{de} {"links" if side == "l" else "rechts"} {i + 1}',
                         f'{en} {"left" if side == "l" else "right"} {i + 1}', asm, 'dark_metal',
                         'Kühlluft; tiefliegendes Gitter', 'eingelassen', f0, f0 + length, u0, u1, 1.4, bevel=R_SMALL, x=x))
    return P


def band(center, thick):
    """Profil eines Bandes konstanter Dicke entlang einer (f,u)-Mittellinie (Wurfarme, Bügel)."""
    L, R = [], []
    for i, (f, u) in enumerate(center):
        a = center[max(0, i - 1)]
        b = center[min(len(center) - 1, i + 1)]
        df, du = b[0] - a[0], b[1] - a[1]
        n = math.hypot(df, du) or 1
        nf, nu = -du / n, df / n
        th = thick[i] if isinstance(thick, (list, tuple)) else thick
        L.append((f + nf * th / 2, u + nu * th / 2))
        R.append((f - nf * th / 2, u - nu * th / 2))
    return L + R[::-1]

INTERFACES['BCY-6'] = dict(de='Revolvertrommel 6 Kammern', en='Revolver cylinder 6', rule='Trommel r 22 mm auf Kran, Achse 12 mm unter Laufachse')
INTERFACES['BAB-1'] = dict(de='Munitionskasten MG', en='MG ammo box', rule='Einhängung links am Gehäuse, Gurt nach oben zur Zuführschale')


def stock_s2(f0, ua, s=1.0):
    """Schaft S2: einteilige Graphit-Schulterstütze mit Daumenmulde, direkt am Gehäuse (Energie- und Impulswaffen,
    Granatwerfer). f0 = Hinterkante Gehäuse, ua = Laufachse."""
    L = lambda d: f0 - d * s  # noqa: E731
    return [
        prof('stock', 'Schulterstütze S2', 'Stock S2', 'stock', 'graphite', 'Einteilige Schulterstütze; Wange liegt oben auf',
             'mit zwei Bolzen am Gehäuse (fest)', [(f0 + 2, ua - 40), (f0 + 2, ua + 24), (L(60), ua + 26), (L(150), ua + 22),
                                                 (L(158), ua + 14), (L(158), ua - 70), (L(146), ua - 76), (L(60), ua - 46)],
             34, iface='BST-2'),
        prof('butt_pad', 'Schaftkappe', 'Butt pad', 'stock', 'dark_metal', 'Anlage an der Schulter',
             'auf das Schaftende geschraubt', [(L(157), ua - 78), (L(157), ua + 24), (L(168), ua + 20), (L(170), ua + 10),
                                              (L(170), ua - 70), (L(168), ua - 76)], 38, bevel=R_MID),
    ]


INTERFACES['BST-2'] = dict(de='Schaft S2', en='Stock S2', rule='Anlage 64 mm hoch am Gehäuseende, Laufachse 24 mm unter der Oberkante')
INTERFACES['BST-T'] = dict(de='Einteilkörper Spurgewehr', en='Trace one-piece body', rule='Hinterkörper bündig am Gehäuse, Fuge 1 mm')


# ------------------------------------------------------------------ Bausteine Stil v2.1 (Familie; aus dem Pilot übernommen)
# Der Pilot basic/pilot/w01_auto_rifle_v21.py führt dieselben Formen noch inline (unverändert, damit seine Ausgabe gleich bleibt).

def cut_box(f0, f1, u0, u1, w, x=0.0):
    """Schneidkörper (Quader) für `cuts`."""
    return dict(shape='box', f0=f0, f1=f1, u0=u0, u1=u1, w=w, x=x)


def screws(pts, x, r=2.2, h=1.2, axis='x'):
    """Schraubenköpfe (Zylinder quer) an (f,u)-Punkten auf der Seitenfläche x (Vorzeichen = Seite)."""
    s = 1 if x > 0 else -1
    return [dict(shape='cyl', axis=axis, c=(f, u), a0=x - s * 0.6, a1=x + s * h, r=r, segs=12) for f, u in pts]


def mirror(items):
    """Spiegelt Quer-Zylinder (`a0`/`a1`) auf die andere Seite und hängt sie an."""
    return items + [dict(i, a0=-i['a0'], a1=-i['a1']) for i in items]


def grip_v21(top=42, mat='rubber'):
    """Griffmodul BGM-1 in v2.1-Form: Fingerauflagen (Wechsel 17/21 mm), Handballenwölbung, ausgestellter Boden (Griffboden)."""
    t = math.tan(math.radians(15))

    def A(u, d):
        return (u * t + d, u)
    P = []
    for p in grip_rifle(top=top):
        if p['id'] == 'grip':
            p.update(mat=mat, pts=[A(top, -20), A(12, -23), A(-22, -26), A(-52, -22), A(-64, -25), A(-74, -22), A(-76, -12),
                                   A(-76, 16), A(-70, 23), A(-60, 18), A(-50, 21), A(-40, 17), A(-30, 21), A(-20, 17), A(-8, 21),
                                   A(16, 20), A(top, 21)])
        if p['id'] == 'trigger_guard':
            p['mat'] = 'anodized'
        P.append(p)
    P.append(prof('grip_cap', 'Griffboden', 'Grip cap', 'grip_controls', 'anodized', 'Ausgestellter Abschluss; schützt den Griff',
                  'unten auf den Griff geschraubt', [A(-73, -23), A(-73, 24), A(-79, 22), A(-79, -21)], 32, bevel=R_SMALL))
    return P


def reticle(f, cu, kind='ring_dot', s=1.0, pid='sight_reticle', color='cyan', weight='normal', spread=0.0, center_dot=True,
            parent='sight_mount'):
    """Absehen aus dem Katalog basic/reticles.py auf der Reflexscheibe (Ebene f, Mitte cu): Form `kind`, Farbe `color`
    (Rolle reticle_<color>, gedämpft leuchtend, gehört zur Leuchtfunktion des Emitters), Linienstärke `weight`, Größe s,
    Spreizung `spread` mm (0 = Ruhezustand; Aufgehen beim Schießen zeigt die Laufzeit, Clip: tools/reticle_sheet.py)."""
    from basic import reticles as RT
    k = RT.WEIGHTS[weight][1]
    lw = RT.LINE_R * s * k
    items = []
    for q in RT.prims_at(kind, spread, center_dot):
        if q['t'] == 'line':
            items.append(dict(shape='tube', path=[(f + 0.2, cu + q['a'][1] * s, q['a'][0] * s), (f + 0.2, cu + q['b'][1] * s, q['b'][0] * s)],
                              r=lw))
        elif q['t'] == 'ring':
            items.append(dict(shape='cyl', axis='f', c=(cu, 0), a0=f, a1=f + 0.4, r=(q['ri'] + (q['r'] - q['ri']) * k) * s,
                              r_in=q['ri'] * s, segs=48))
        else:
            items.append(dict(shape='cyl', axis='f', c=(cu, 0), a0=f, a1=f + 0.4, r=q['r'] * s * (0.5 + 0.5 * k), segs=16))
    R = RT.RETICLES[kind]
    return part(pid, f'Absehen {R["de"]}', f'Reticle {R["en"]}', 'sight', 'multi', f'reticle_{color}',
                f'Zielpunkt im Glas: {R["de"]}, {RT.COLORS[color][0]}, {RT.WEIGHTS[weight][0]} (vom Emitter projiziert)',
                'auf der Reflexscheibe' if parent == 'sight_mount' else 'auf der Absehenebene im Rohr', bevel=0, parent_part=parent,
                smooth=True, reticle=dict(kind=kind, color=color, weight=weight), items=items)


def reflex_sight_v21(f, u, ww=26, wh=20, reticle_kind='ring_dot', reticle_color='cyan', reticle_weight='fine', glass='clean'):
    """Offenes Holovisier v2.1, Designsprache v3 (Nutzer 25.10.2026; Motiongen REF 0.14 „Eyebox“): kleine Öffnung (bei 90 mm
    Augenabstand 12–20 % der Bildbreite), Rahmen ≤ 0,10 × Öffnung (Bügel 1,6 mm, Dach 1,2 mm), gestufter Trapezsockel bis zur
    Fensterunterkante (nichts schwebt, Anzeigen unter der Visierlinie), neutrales Gehäuse mit einem Akzent (Klemmhebel), Absehen
    fein in Familienfarbe. ww × wh = Glasfenster (Vertrag: 26 × 20 bis 44 × 30 mm). Liefert (Teile, Anker)."""
    from basic.reticles import SIGHT
    bt = u + 6                              # Oberkante Klemmfuß
    cu = bt + wh / 2 + 10                   # Visierlinie
    hw = ww / 2 + 0.8                       # Mitte der Haubenbügel
    top = cu + wh / 2 + 0.8                 # Unterkante Haubendach
    gb = cu - wh / 2 - 0.4                  # Fensterunterkante (Oberkante Sockel)
    fg = f + 40                             # Glasebene
    P = [
        part('sight_mount', 'Visier-Klemmfuß', 'Sight mount', 'sight', 'multi', 'anodized',
             'Klemmt das Visier auf die Schiene BRI-22; gestuftes Trapez', 'Klemmung auf Schiene (lösbar)', bevel=R_SMALL, iface='BRI-22',
             items=[dict(shape='box', f0=f, f1=f + 46, u0=u + 0.5, u1=u + 3.5, w=23),
                    dict(shape='box', f0=f + 2, f1=f + 44, u0=u + 3, u1=bt, w=18)],
             move=dict(kind='translate', pivot=(f + 23, u, 0), vector_mm=(0, 70, 0), event='swap_sight', removable=True)),
        part('sight_clamp', 'Klemmhebel', 'Clamp lever', 'sight', 'prof', 'accent', 'Spannt den Klemmfuß werkzeuglos',
             'Drehachse links am Klemmfuß', bevel=R_FINE, parent_part='sight_mount',
             pts=[(f + 12, u + 0.8), (f + 32, u + 0.8), (f + 34, u + 3.2), (f + 12, u + 3.6)], w=1.8, x=12.4),
        prof('sight_body', 'Visiergehäuse', 'Sight housing', 'sight', 'anodized', 'Trägt Emitter und Batterie; flach, hinten',
             'auf Klemmfuß (fest)', [(f + 1, bt - 0.5), (f + 30, bt - 0.5), (f + 30, bt + 3.5), (f + 18, bt + 3.5), (f + 14, bt + 6),
                                     (f + 1, bt + 6)], 16, bevel=R_SMALL, parent_part='sight_mount'),
        part('sight_base', 'Haubensockel', 'Hood base', 'sight', 'prof', 'anodized',
             'Trägt Haube und Glas bis zur Fensterunterkante; trapezförmig verjüngt, Anzeigen unter der Visierlinie',
             'auf Klemmfuß (fest)', bevel=R_FINE, parent_part='sight_mount',
             pts=[(f + 29, bt - 0.5), (f + 46.6, bt - 0.5), (f + 46.6, gb), (f + 33, gb)], w=ww + 3.2),
        part('sight_frame', 'Visierhaube', 'Sight hood', 'sight', 'multi', 'anodized', 'Offene Haube aus zwei Bügeln und dünnem Dach',
             'auf dem Haubensockel (fest)', bevel=0.5, parent_part='sight_mount',
             items=[dict(shape='prof', pts=[(f + 34, gb - 0.5), (f + 46, gb - 0.5), (f + 46, top + 1.2), (f + 36, top + 1.2)], w=1.6,
                         x=sx * hw) for sx in (1, -1)]
                   + [dict(shape='prof', pts=[(f + 36, top), (f + 46, top), (f + 46, top + 1.2), (f + 36, top + 1.2)], w=ww + 3.2)]),
        part('sight_frame_trim', 'Haubenkante', 'Hood trim', 'sight', 'frame', 'trim', 'Blanke Stirnkante der Haube (dünn)',
             'vorn an der Haube', bevel=0.3, parent_part='sight_mount', f0=f + 45.6, f1=f + 46.6, cu=cu + 0.2, ow=ww + 3.2,
             oh=wh + 3.0, iw=ww, ih=wh + 0.4, r_out=2, r_in=1.5),
        part('sight_glass', 'Visierglas', 'Sight glass', 'sight', 'xbox', 'glass' if glass == 'clean' else f'glass_{glass}',
             'Beschichtete Reflexscheibe' + ('' if glass == 'clean' else f' ({glass})'), 'in der Haube (fest)', bevel=0,
             parent_part='sight_mount', f0=fg, f1=fg + 0.8, cu=cu, ww=ww, hh=wh),
        box('sight_emitter', 'Emitter', 'Reticle emitter', 'sight', 'energy', 'Leuchtfenster des Absehen-Projektors (unter der Visierlinie)',
            'vorn im Emitterblock', f + 15.5, f + 17.5, bt + 3.6, bt + 5.4, 6, bevel=0.3, parent_part='sight_mount'),
        reticle(fg - 0.6, cu, reticle_kind, color=reticle_color, weight=reticle_weight),
        cyl('sight_knob_w', 'Seitenverstellung', 'Windage knob', 'sight', 'trim', 'Verstellt das Absehen seitlich',
            'rechts am Gehäuse', 'x', (f + 24, bt + 1.8), -7.5, -10, 2.4, parent_part='sight_mount', segs=16),
        cyl('sight_battery', 'Batteriedeckel', 'Battery cap', 'sight', 'anodized', 'Batteriefach links',
            'links am Gehäuse (schraubbar)', 'x', (f + 24, bt + 1.8), 7.5, 10, 3.2, parent_part='sight_mount', segs=16),
    ]
    rel = SIGHT['types']['reflex']['eye_relief_mm']
    A = {'Socket_Sight': dict(at=(f + 1, cu, 0), part='sight_body'),
         'Socket_Reticle': dict(at=(fg + 0.4, cu, 0), part='sight_glass'),
         'Socket_Eye': dict(at=(fg + 0.4 - rel, cu, 0), part='sight_frame', sight_type='reflex', std=True,
                            note=f'Augenpunkt beim Zielen (Visier-Standard: {rel:.0f} mm hinter dem Glas)')}
    return P, A


def scope_v21(f, u, length=120, r_obj=16, r_eye=11, r_tube=9.5, reticle_kind='chevron', reticle_color='cyan',
              reticle_weight='fine'):
    """Kurzes Ring-Zielfernrohr, Designsprache v3 (Nutzer 25.10.2026; Motiongen REF 0.14 „Eyebox“; Destiny-Scout: dünner Ring,
    trapezförmiger Hals, Öffnung ≈ 21 % Bildbreite): kurzes Rohr, Objektiv mit dünnem Rand (Rahmen ≤ 0,15 × Öffnung) und blanker
    Innenkante, ein gestufter Trapezhals statt zweier Ringe, Höhenturm (Akzent), Linsen, feines Absehen hinter der Objektivlinse.
    Teile mit `ads_hide` (Rohr, Okular, Okularlinse, Türme) sind beim Zielen ausgeblendet; der Augenpunkt liegt 90 mm hinter dem
    Objektivring (Visier-Standard), der Hals bleibt unterhalb der Linse sichtbar. Liefert (Teile, Anker, Rohrachse cu)."""
    from basic.reticles import SIGHT
    cu = u + 21 + r_obj
    f_eye, f_obj = f, f + length
    fb = f_obj - 36                                   # Beginn des Objektivs
    P = [
        part('scope_mount_r', 'Zielfernrohr-Hals', 'Scope neck', 'sight', 'multi', 'anodized',
             'Trägt das Zielfernrohr auf der Schiene BRI-22; gestuftes Trapez', 'Klemmung auf Schiene (lösbar)', bevel=R_SMALL,
             iface='BRI-22',
             items=[dict(shape='box', f0=f + 34, f1=f + 70, u0=u + 0.5, u1=u + 5, w=22),
                    dict(shape='prof', pts=[(f + 37, u + 4.5), (f + 67, u + 4.5), (f + 62, cu - r_tube + 1), (f + 42, cu - r_tube + 1)],
                         w=15),
                    dict(shape='prof', pts=[(f + 44, u + 4.5), (f + 60, u + 4.5), (f + 58, cu - r_tube + 1), (f + 46, cu - r_tube + 1)],
                         w=18)]
             + screws([(f + 40, u + 2.8), (f + 64, u + 2.8)], 11.0, r=1.2, h=0.6)),
        part('sight_clamp', 'Klemmhebel', 'Clamp lever', 'sight', 'prof', 'accent', 'Spannt den Hals werkzeuglos',
             'links am Hals', bevel=R_FINE, pts=[(f + 40, u + 0.8), (f + 58, u + 0.8), (f + 60, u + 3.2), (f + 40, u + 3.6)], w=1.8,
             x=11.6),
        cyl('scope_tube', 'Mittelrohr', 'Scope tube', 'sight', 'graphite', 'Verbindet Okular und Objektiv; hohl',
            'auf dem Hals (fest)', 'f', (cu, 0), f + 20, fb + 2, r_tube, r_in=r_tube - 1.5, segs=40, ads_hide=True),
        cyl('scope_eyepiece', 'Okular', 'Eyepiece', 'sight', 'graphite', 'Augenseite, schlank; Socket_Sight hinten', 'am Mittelrohr (fest)',
            'f', (cu, 0), f_eye, f + 22, r_eye, r1=r_tube + 0.5, r_in=r_eye - 2, segs=40, bevel=R_SMALL, ads_hide=True),
        cyl('scope_eye_trim', 'Okularkante', 'Eyepiece trim', 'sight', 'trim', 'Blanke Kante am Okular', 'hinten am Okular',
            'f', (cu, 0), f_eye - 1, f_eye + 1.5, r_eye + 0.4, r_in=r_eye - 1.5, segs=40, bevel=0.3, ads_hide=True),
        cyl('scope_objective', 'Objektiv', 'Objective bell', 'sight', 'graphite', 'Lichteintritt vorn', 'am Mittelrohr (fest)',
            'f', (cu, 0), fb, f_obj - 4, r_tube + 1, r1=r_obj, r_in=r_obj - 2.0, segs=48, bevel=R_SMALL),
        cyl('scope_rim', 'Objektivrand', 'Objective rim', 'sight', 'anodized', 'Dünner Rand um die Linse', 'vorn auf dem Objektiv',
            'f', (cu, 0), f_obj - 4, f_obj, r_obj + 0.5, r_in=r_obj - 1.2, segs=48, bevel=0.4),
        cyl('scope_crown', 'Objektivkante', 'Objective trim', 'sight', 'trim', 'Blanke Innenkante (Blickfang im Zielen)',
            'innen am Rand', 'f', (cu, 0), f_obj - 6, f_obj - 0.4, r_obj - 1.2, r_in=r_obj - 2.0, segs=48, bevel=0.2),
        cyl('scope_turret', 'Höhenturm', 'Elevation turret', 'sight', 'accent', 'Höhenverstellung (Bedienelement)',
            'oben am Mittelrohr (fest)', 'u', (f + 52, 0), cu + r_tube - 2, cu + r_tube + 6, 5.5, segs=32, ads_hide=True),
        cyl('scope_turret_w', 'Seitenturm', 'Windage turret', 'sight', 'anodized', 'Seitenverstellung', 'rechts am Mittelrohr (fest)',
            'x', (f + 52, cu), -(r_tube - 2), -(r_tube + 5), 4.5, segs=32, ads_hide=True),
        cyl('scope_glass', 'Objektivlinse', 'Objective lens', 'sight', 'glass_scope', 'Linse vorn (im Zielen dasselbe Weltbild)',
            'im Objektiv (fest)', 'f', (cu, 0), f_obj - 5, f_obj - 4, r_obj - 2.0, segs=48, bevel=0),
        cyl('scope_ocular_glass', 'Okularlinse', 'Ocular lens', 'sight', 'glass_scope', 'Augenlinse', 'im Okular (fest)', 'f', (cu, 0),
            f_eye + 3, f_eye + 4, r_eye - 2, segs=40, bevel=0, ads_hide=True),
        reticle(f_obj - 6, cu, reticle_kind, s=r_obj / 13, color=reticle_color, weight=reticle_weight, parent='scope_mount_r'),
    ]
    P[0]['move'] = dict(kind='translate', pivot=(f + 52, u, 0), vector_mm=(0, 80, 0), event='swap_sight',
                        note='Klemmhebel lösen, Zielfernrohr senkrecht abnehmen', removable=True)
    for q in P[1:]:
        q['parent_part'] = 'scope_mount_r'
    rel = SIGHT['types']['scope']['eye_relief_mm']
    A = {'Socket_Sight': dict(at=(f_eye, cu, 0), part='scope_eyepiece', note='hinteres Okularende auf der Visierlinie'),
         'Socket_Objective': dict(at=(f_obj, cu, 0), part='scope_rim', note='Stirn des Objektivrings'),
         'Socket_Reticle': dict(at=(f_obj - 6, cu, 0), part='sight_reticle', note='Absehen hinter der Objektivlinse'),
         'Socket_Eye': dict(at=(f_obj - rel, cu, 0), part='scope_objective', sight_type='scope', std=True,
                            note=f'Augenpunkt beim Zielen (Visier-Standard: {rel:.0f} mm hinter dem Objektivring, ads_hide-Teile aus)')}
    return P, A, cu


def box_scope_v21(f, u, style='prism', reticle_kind='chevron', reticle_color='cyan', reticle_weight='fine'):
    """Kastenoptik v2.1 nach Destiny-Scouts (Nutzerbilder 24.10.2026): kompakter Kasten statt Rohr mit Ringen.
    style 'prism': kurzer quadratischer Kasten (Graphit) mit runder Linse vorn, schmalem Okular, seitlichen Knöpfen, Sockel.
    style 'flat' : flacher, langer Kasten zweifarbig (Creme oben, Graphit unten) mit rechteckiger Öffnung und Lüftungsschlitzen.
    Der Kasten ist ein Rahmen mit durchgehender Bohrung; im Zielen (Augenpunkt 90 mm vor der Öffnung) sieht man durch ihn auf
    Linse und Absehen; Okular/Augenring tragen `ads_hide`. Liefert (Teile, Anker, Visierlinie cu) wie scope_v21."""
    from basic.reticles import SIGHT
    if style == 'prism':
        L, ow, oh, iw, ih, r_o, r_i, base_h = 64, 32, 30, 22, 22, 6, 11, 15      # Sockel für Visierhöhe 66 mm
    else:
        L, ow, oh, iw, ih, r_o, r_i, base_h = 108, 30, 20, 26, 14, 3, 2.5, 18    # Sockel für Visierhöhe 64 mm
    cu = u + 8 + base_h + oh / 2                     # Rail-Oberkante u + 8, Sockel, halbe Kastenhöhe
    f0, f1 = f, f + L                                # Kasten hinten / vorn
    P = [
        box('scope_mount_r', 'Optik-Sockel', 'Optic base', 'sight', 'anodized', 'Klemmt die Optik auf die Schiene BRI-22',
            'Klemmung auf Schiene (lösbar)', f0 + 10, f1 - 10, u + 0.5, cu - oh / 2 + 1, 20, bevel=R_SMALL, iface='BRI-22',
            move=dict(kind='translate', pivot=(f0 + L / 2, u, 0), vector_mm=(0, 80, 0), event='swap_sight', removable=True)),
        part('sight_clamp', 'Klemmhebel', 'Clamp lever', 'sight', 'prof', 'accent', 'Spannt den Sockel werkzeuglos',
             'links am Sockel', bevel=R_FINE, pts=[(f0 + 16, u + 1), (f0 + 34, u + 1), (f0 + 36, u + 4), (f0 + 16, u + 4.6)], w=2.0, x=10.6),
        part('scope_body', 'Optikkasten', 'Optic housing', 'sight', 'frame', 'graphite' if style == 'prism' else 'shell',
             'Kompakter Kasten mit durchgehender Bohrung', 'auf dem Sockel (fest)', bevel=R_MID if style == 'prism' else R_SMALL,
             f0=f0, f1=f1, cu=cu, ow=ow, oh=oh, iw=iw, ih=ih, r_out=r_o, r_in=r_i,
             cuts=[cut_box(f0 + 30 + 9 * i, f0 + 34 + 9 * i, cu + oh / 2 - 2, cu + oh / 2 + 2, 18) for i in range(6)]
             if style == 'flat' else []),
        part('scope_front', 'Optikfront', 'Optic front', 'sight', 'frame', 'trim', 'Blanke Stirnkante um die Öffnung',
             'vorn am Kasten', bevel=0.3, f0=f1 - 0.6, f1=f1 + 1.0, cu=cu, ow=iw + 3, oh=ih + 3, iw=iw - 0.6, ih=ih - 0.6,
             r_out=r_i + 1.5, r_in=r_i - 0.3),
        part('scope_glass', 'Optiklinse', 'Optic lens', 'sight', 'xbox', 'glass_scope', 'Linse vorn; zeigt im Zielen das Linsenbild',
             'in der Kastenfront (fest)', bevel=0, f0=f1 - 3, f1=f1 - 2.2, cu=cu, ww=iw - 0.6, hh=ih - 0.6),
        reticle(f1 - 4, cu, reticle_kind, s=min(iw, ih) / 26, color=reticle_color, weight=reticle_weight, parent='scope_mount_r'),
        cyl('scope_eyepiece', 'Okular', 'Eyepiece', 'sight', 'graphite', 'Kurzes Okular hinten', 'hinten am Kasten (fest)',
            'f', (cu, 0), f0 - 10, f0 + 1, min(iw, ih) / 2 - 1, r_in=min(iw, ih) / 2 - 3, segs=40, bevel=R_SMALL, ads_hide=True),
        cyl('scope_eye_trim', 'Okularring', 'Eyepiece ring', 'sight', 'trim', 'Blanker Ring am Okular', 'hinten am Okular',
            'f', (cu, 0), f0 - 12, f0 - 9, min(iw, ih) / 2 - 0.4, r_in=min(iw, ih) / 2 - 2.6, segs=40, bevel=0.3, ads_hide=True),
    ]
    if style == 'prism':
        P += [cyl('scope_turret', 'Seitenknopf', 'Side knob', 'sight', 'accent', 'Verstellung (Bedienelement)', 'links am Kasten',
                  'x', (f0 + L / 2, cu - 4), ow / 2 - 1, ow / 2 + 4, 5.5, segs=32),
              cyl('scope_turret_w', 'Seitenknopf rechts', 'Side knob right', 'sight', 'anodized', 'Verstellung', 'rechts am Kasten',
                  'x', (f0 + L / 2, cu - 4), -(ow / 2 - 1), -(ow / 2 + 4), 5.5, segs=32)]
    else:
        P += [box('scope_lower', 'Kastenunterteil', 'Housing lower', 'sight', 'graphite', 'Dunkle untere Lage (Zweiton)',
                  'unter den Kasten geschraubt', f0 + 4, f1 - 14, cu - oh / 2 - 1.5, cu - oh / 2 + 4, ow + 0.6, bevel=R_FINE),
              box('scope_turret', 'Verstellknopf', 'Adjust button', 'sight', 'accent', 'Verstellung (Bedienelement)', 'links am Kasten',
                  f0 + 14, f0 + 24, cu - 2, cu + 3, 2.0, bevel=0.4, x=ow / 2 + 0.8)]
    for q in P[1:]:
        q['parent_part'] = 'scope_mount_r'
    rel = SIGHT['types']['scope']['eye_relief_mm']
    A = {'Socket_Sight': dict(at=(f0 - 12, cu, 0), part='scope_eyepiece', note='hinteres Okularende'),
         'Socket_Objective': dict(at=(f1 + 1.0, cu, 0), part='scope_front', note='Stirn der Kastenöffnung'),
         'Socket_Reticle': dict(at=(f1 - 4, cu, 0), part='sight_reticle', note='Absehen hinter der Linse'),
         'Socket_Eye': dict(at=(f1 + 1.0 - rel, cu, 0), part='scope_body', sight_type='scope', std=True,
                            note=f'Augenpunkt beim Zielen (Visier-Standard: {rel:.0f} mm hinter der Öffnung, ads_hide-Teile aus)')}
    return P, A, cu
