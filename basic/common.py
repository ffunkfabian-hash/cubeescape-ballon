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
