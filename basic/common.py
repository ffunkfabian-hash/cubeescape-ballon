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


# ------------------------------------------------------------------ Visier-Baukasten v3 (0.21 „Ironsight“, docs/visier-konzept.md)
# Nutzerwahl 26.10.2026 „v3 bauen“: H0-Plattform (das Holo von BASIC-01, Nutzer: „von der Höhe optimal und vom Design gut“) für alle
# Visiere – zweistufiger Klemmfuß 46 × 23/18 mm mit orangem Hebel, flaches Gehäuse hinten (Emitter, Knopf, Batteriedeckel),
# Trapezsockel in Fensterbreite bis zur Fensterunterkante, Haube aus Flachprofil (Stirn 1,6 mm, Tiefe 10–12 mm) mit blanker
# Stirnkante; je Visier ändern sich nur Rahmenkontur und höchstens ein Funktionsdetail. Zielfernrohre nach Konzept A: Sattel hinter
# dem Auge, Klemmfuß unter dem Objektiv, Ring ohne Wulst (außen/innen 1,29). Absehen gezeichnet: flach in der Glasebene.
# Entwürfe, weitere Varianten und Katalogblatt: basic/pilot/optics/sight_kit.py (nutzt diese Bausteine). Querprofile in mm um die
# Visierlinie cu: x nach links (aus Augensicht), u nach oben.

SIGHT_MAT = 'sight_anod'                                     # Rolle der Visierteile: eloxiert, Abrieb für dünne Teile (kit.py)
SIGHT_T = 1.6                                                # Stirn des Flachprofils
HOLO_SIZES = {'S': (22, 17), 'M': (26, 20), 'L': (34, 26)}   # Fenster B × H; L nur an MG/Werfern (reticles.SIGHT › variants)
SCOPE_SIZES = {'S': 12.0, 'M': 14.0, 'L': 17.0}              # Radius der Objektivlinse (lichte Öffnung); S ist Variante
RING_RATIO = 1.29                                            # Ring außen/innen (Destiny 1,28–1,30)


def sight_line(u, kind='holo'):
    """Visierlinie über der Schienenoberkante u (Visier-Standard 3, reticles.SIGHT['rail_line_mm']): Holo auf der H0-Plattform + 26 mm,
    Mini-Reflex + 15 mm, Kimme/Korn + 11 mm. Zielfernrohre nach Konzept A haben zwei Schienen auf eigener Höhe und richten sich nur
    nach der Visierhöhe 66 ± 4 mm (`scope_tropfen(…, cu)`)."""
    from basic.reticles import SIGHT
    return u + SIGHT['rail_line_mm'][kind]


def sight_arc(r, a0, a1, n=32):
    """Kreisbogen (x, u) von a0 bis a1 Grad."""
    return [(r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def sight_rr(w, h, r, cut=0.0, n=6):
    """Rundrechteck w × h, Eckradius r; cut > 0 fast die Ecke oben rechts aus Augensicht (x < 0) um cut mm."""
    pts = []
    for cx, cu, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        if cut and a0 == 90:
            pts += [(-w / 2 + cut, h / 2), (-w / 2, h / 2 - cut)]
            continue
        pts += [(cx + r * math.cos(math.radians(a0 + 90 * i / n)), cu + r * math.sin(math.radians(a0 + 90 * i / n))) for i in range(n + 1)]
    return pts


def sight_sector(r0, r1, a0, a1, n=32):
    """Ringsegment (Flachprofil) von a0 bis a1 Grad, innen r0, außen r1."""
    return sight_arc(r1, a0, a1, n) + sight_arc(r0, a1, a0, n)


def xprof(pid, de, mat, f0, f1, pts, cu, holes=(), func='', attach='am Visier', bevel=0.4, en=None, **kw):
    """Flaches Profil quer zur Laufachse (Form `xprof`): Kontur pts (x, u relativ zu cu) von f0 bis f1; holes = innere Konturen."""
    return part(pid, de, en or de, 'sight', 'xprof', mat, func or de, attach, bevel=bevel, f0=f0, f1=f1, cu=cu, pts=pts,
                cuts=[dict(shape='xprof', f0=f0 - 1, f1=f1 + 1, cu=cu, pts=h) for h in holes], **kw)


def sight_hood(inner, outer, fr, cu, depth=12, trim=True, mat=SIGHT_MAT):
    """Haube als Flachprofil (Stirn = outer − inner) mit blanker Stirnkante vorn (H0: sight_frame_trim)."""
    P = [xprof('sight_frame', 'Haube', mat, fr, fr + depth, outer, cu, holes=[inner], func='Haube aus Flachprofil',
               attach='auf dem Haubensockel (fest)', en='Sight hood', parent_part='sight_mount')]
    if trim:
        P.append(xprof('sight_frame_trim', 'Stirnkante', 'trim', fr + depth - 0.4, fr + depth + 0.6, outer, cu, holes=[inner],
                       func='Blanke Stirnkante der Haube (dünn)', attach='vorn an der Haube', bevel=0.2, en='Hood trim',
                       parent_part='sight_mount'))
    return P


def sight_glass_x(f, pts, cu, glass='glass_scope'):
    """Flache Scheibe in Fensterform (ohne Spiegelung), 0,8 mm dick, Ebene f."""
    return xprof('sight_glass', 'Visierglas', glass, f, f + 0.8, pts, cu, func='Reflexscheibe ohne Spiegelung; das Absehen liegt flach darauf',
                 attach='in der Haube (fest)', bevel=0, en='Sight glass', parent_part='sight_mount')


def sight_platform(f, u, base_w, gb, k=1.0, emitter=True, mat=SIGHT_MAT):
    """H0-Plattform: Klemmfuß zweistufig (lösbar, trägt alle Visierteile), oranger Klemmhebel, flaches Gehäuse (Emitter, Knopf,
    Batteriedeckel), Trapezsockel in Fensterbreite base_w bis zur Fensterunterkante gb. f = Hinterkante Klemmfuß, u = Schienenoberkante;
    k kürzt die Länge (Mini-Reflex). Maße und Fasen wie BASIC-01 (reflex_sight_v21)."""
    bt = u + 6
    L = 46 * k
    P = [part('sight_mount', 'Visier-Klemmfuß', 'Sight mount', 'sight', 'multi', mat,
              'Klemmt das Visier auf die Schiene BRI-22; gestuftes Trapez', 'Klemmung auf Schiene (lösbar)', bevel=R_SMALL, iface='BRI-22',
              items=[dict(shape='box', f0=f, f1=f + L, u0=u + 0.5, u1=u + 3.5, w=23),
                     dict(shape='box', f0=f + 2, f1=f + L - 2, u0=u + 3, u1=bt, w=18)],
              move=dict(kind='translate', pivot=(f + L / 2, u, 0), vector_mm=(0, 70, 0), event='swap_sight', removable=True)),
         part('sight_clamp', 'Klemmhebel', 'Clamp lever', 'sight', 'prof', 'accent', 'Spannt den Klemmfuß werkzeuglos',
              'Drehachse links am Klemmfuß', bevel=R_FINE, parent_part='sight_mount',
              pts=[(f + 12 * k, u + 0.8), (f + 32 * k, u + 0.8), (f + 34 * k, u + 3.2), (f + 12 * k, u + 3.6)], w=1.8, x=12.4),
         prof('sight_body', 'Visiergehäuse', 'Sight housing', 'sight', mat, 'Trägt Emitter und Batterie; flach, hinten',
              'auf Klemmfuß (fest)', [(f + 1, bt - 0.5), (f + 30 * k, bt - 0.5), (f + 30 * k, bt + 3.5), (f + 18 * k, bt + 3.5),
                                      (f + 14 * k, bt + 6), (f + 1, bt + 6)], 16, bevel=R_SMALL, parent_part='sight_mount'),
         part('sight_base', 'Haubensockel', 'Hood base', 'sight', 'prof', mat,
              'Trägt Haube und Glas bis zur Fensterunterkante; trapezförmig verjüngt, Anzeigen unter der Visierlinie',
              'auf Klemmfuß (fest)', bevel=R_FINE, parent_part='sight_mount',
              pts=[(f + 29 * k, bt - 0.5), (f + L + 0.6, bt - 0.5), (f + L + 0.6, gb), (f + 29 * k + 4, gb)], w=base_w),
         cyl('sight_knob_w', 'Seitenverstellung', 'Windage knob', 'sight', 'trim', 'Verstellt das Absehen seitlich',
             'rechts am Gehäuse', 'x', (f + 24 * k, bt + 1.8), -7.5, -10, 2.4, parent_part='sight_mount', segs=16),
         cyl('sight_battery', 'Batteriedeckel', 'Battery cap', 'sight', mat, 'Batteriefach links',
             'links am Gehäuse (schraubbar)', 'x', (f + 24 * k, bt + 1.8), 7.5, 10, 3.2, parent_part='sight_mount', segs=16)]
    if emitter:
        P.append(box('sight_emitter', 'Emitter', 'Reticle emitter', 'sight', 'energy',
                     'Leuchtfenster des Absehen-Projektors (unter der Visierlinie)', 'vorn im Emitterblock',
                     f + 15.5 * k, f + 17.5 * k, bt + 3.6, bt + 5.4, 6, bevel=0.3, parent_part='sight_mount'))
    return P


def sight_base_rear_f(f, u, gb, u_at, k=1.0):
    """f der Sockelrückseite (Schräge) in Höhe u_at – für Anzeigen zum Auge."""
    bt = u + 6
    f0, f1 = f + 29 * k, f + 29 * k + 4
    return f0 + (f1 - f0) * (u_at - (bt - 0.5)) / (gb - (bt - 0.5))


def drawn_reticle(f, cu, weapon_type, dist, color='cyan', pid='sight_reticle', parent='sight_mount'):
    """Gezeichnetes Absehen (visier-konzept › 5, wie Unity seit 0.20): Hüftform der Klasse (reticles.hip) in Hüftgröße als Anteil
    der Bildhöhe bei 75° und 16:9, flach in der Ebene f (0,05 mm dick, zum Auge vor dem Glas), dist = Abstand zum Augenpunkt; Linien
    mindestens 1,6 px bei 1280 px Bildbreite, reine Emission (Rolle reticle_<color>). Unity blendet das Teil aus und zeichnet selbst."""
    from basic import reticles as RT
    D = RT.SIGHT['drawn']
    h = RT.hip(weapon_type)
    k = RT.WEIGHTS[RT.HIP['weight']][1]
    th = math.tan(math.radians(RT.SIGHT['fov_ref_deg'] / 2))
    s = h['share_h'] * 2 * dist * th * 9 / 16 / h['extent_mm']
    px = 2 * dist * th / D['ref_w_px']
    lw = max(RT.LINE_R * k * s, D['min_line_px'] / 2 * px)                # halbe Linienbreite
    items = []

    def quad(pts):
        items.append(dict(shape='xprof', f0=f - 0.05, f1=f, cu=cu, pts=pts))
    for q in RT.prims_at(h['kind'], 0.0, True):
        if q['t'] == 'line':
            (ax, au), (bx, bu) = [(c[0] * s, c[1] * s) for c in (q['a'], q['b'])]
            L = math.hypot(bx - ax, bu - au) or 1.0
            nx, nu = -(bu - au) / L * lw, (bx - ax) / L * lw
            quad([(ax + nx, au + nu), (ax - nx, au - nu), (bx - nx, bu - nu), (bx + nx, bu + nu)])
        elif q['t'] == 'ring':
            ro = max((q['ri'] + (q['r'] - q['ri']) * k) * s, 2.4 * lw)
            ri = min(q['ri'] * s, ro - 2 * lw)
            n = 48
            for i in range(n):
                a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
                quad([(ri * math.cos(a0), ri * math.sin(a0)), (ro * math.cos(a0), ro * math.sin(a0)),
                      (ro * math.cos(a1), ro * math.sin(a1)), (ri * math.cos(a1), ri * math.sin(a1))])
        else:
            quad(sight_arc(max(q['r'] * s * (0.5 + 0.5 * k), 1.2 * lw), 0, 360, 20)[:-1])
    R = RT.RETICLES[h['kind']]
    return part(pid, f'Absehen {R["de"]}', f'Reticle {R["en"]}', 'sight', 'multi', f'reticle_{color}',
                f'Zielpunkt im Glas: {R["de"]} gezeichnet (Hüftform der Klasse, {RT.COLORS[color][0]}, vom Emitter projiziert)',
                'flach auf der Glasebene', bevel=0, parent_part=parent, drawn=dict(kind=h['kind'], share_h=h['share_h'], dist_mm=dist),
                items=items)


def _reflex_anchors(f, fg, cu, eye_part='sight_frame'):
    from basic.reticles import SIGHT
    rel = SIGHT['types']['reflex']['eye_relief_mm']
    return {'Socket_Sight': dict(at=(f + 1, cu, 0), part='sight_body'),
            'Socket_Reticle': dict(at=(fg + 0.4, cu, 0), part='sight_glass'),
            'Socket_Eye': dict(at=(fg + 0.4 - rel, cu, 0), part=eye_part, sight_type='reflex', std=True,
                               note=f'Augenpunkt beim Zielen (Visier-Standard: {rel:.0f} mm hinter dem Glas)')}


def reflex_sight_v21(f, u, ww=26, wh=20, reticle_kind='ring_dot', reticle_color='cyan', reticle_weight='fine', glass='clean',
                     weapon_type='auto_rifle'):
    """H0 „Referenz“ – offenes Holovisier v2.1, Designsprache v3 (Nutzer 25.10.2026; Motiongen REF 0.14 „Eyebox“): kleine Öffnung
    (bei 90 mm Augenabstand 12–20 % der Bildbreite), Rahmen ≤ 0,10 × Öffnung (Bügel 1,6 mm, Dach 1,2 mm), gestufter Trapezsockel bis
    zur Fensterunterkante (nichts schwebt, Anzeigen unter der Visierlinie), neutrales Gehäuse mit einem Akzent (Klemmhebel). Plattform
    des Baukastens v3 (sight_platform). ww × wh = Glasfenster (Vertrag: 26 × 20 bis 44 × 30 mm). Absehen gezeichnet (0.21): Hüftform
    von weapon_type flach im Glas in reticle_color; reticle_kind/reticle_weight wirken nicht mehr (Signatur für tools/reticle_sheet.py, das
    die Röhrenform selbst einsetzt). Liefert (Teile, Anker)."""
    bt = u + 6                              # Oberkante Klemmfuß
    cu = bt + wh / 2 + 10                   # Visierlinie
    hw = ww / 2 + 0.8                       # Mitte der Haubenbügel
    top = cu + wh / 2 + 0.8                 # Unterkante Haubendach
    gb = cu - wh / 2 - 0.4                  # Fensterunterkante (Oberkante Sockel)
    fg = f + 40                             # Glasebene
    B = {p['id']: p for p in sight_platform(f, u, ww + 3.2, gb)}
    P = [B['sight_mount'], B['sight_clamp'], B['sight_body'], B['sight_base'],
         part('sight_frame', 'Visierhaube', 'Sight hood', 'sight', 'multi', SIGHT_MAT, 'Offene Haube aus zwei Bügeln und dünnem Dach',
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
         B['sight_emitter'],
         drawn_reticle(fg, cu, weapon_type, 90.0 - 0.4, color=reticle_color),
         B['sight_knob_w'], B['sight_battery']]
    return P, _reflex_anchors(f, fg, cu)


def holo_kasten(f, u, size='M', weapon_type='pulse_rifle', mat=SIGHT_MAT):
    """H4 „Kasten“ (Impuls-Standard): H0-Plattform; Haube mit Dachradius 6 mm, unten scharfkantig, Seiten nach unten 4° einwärts
    (Merkmal 1); im Trapezsockel zum Auge ein eingelassenes Ziffernfeld 14 × 4 mm (Merkmal 2, Destiny-Anzeigekasten)."""
    w, h = HOLO_SIZES[size]
    cu = sight_line(u)
    gb = cu - h / 2 - 0.4
    dx = math.tan(math.radians(4)) * h

    def cont(ww, hh, r):
        bw = ww - 2 * dx
        return [(bw / 2, -hh / 2)] + [(ww / 2 - r + r * math.cos(math.radians(a)), hh / 2 - r + r * math.sin(math.radians(a)))
                                      for a in range(0, 91, 15)] \
            + [(-ww / 2 + r + r * math.cos(math.radians(a)), hh / 2 - r + r * math.sin(math.radians(a))) for a in range(90, 181, 15)] \
            + [(-bw / 2, -hh / 2)]
    inner, outer = cont(w, h, 6), cont(w + 2 * SIGHT_T, h + 2 * SIGHT_T, 6 + SIGHT_T)
    ud = gb - 6.5
    fd = sight_base_rear_f(f, u, gb, ud + 2)
    field = part('sight_status', 'Ziffernfeld', 'Digit field', 'sight', 'multi', 'energy', 'Ziffern 14 × 4 mm zum Auge (Munition)',
                 'in der Sockelrückseite', bevel=0, parent_part='sight_mount',
                 items=[dict(shape='box', f0=fd - 0.5, f1=fd + 0.5, u0=ud, u1=ud + 4, w=3.2, x=x) for x in (-4.6, -1.0)]
                 + [dict(shape='box', f0=fd - 0.5, f1=fd + 0.5, u0=ud, u1=ud + 1.2, w=4.2, x=3.8)])
    fg = f + 40
    P = sight_platform(f, u, w + 2 * SIGHT_T, gb, mat=mat) + sight_hood(inner, outer, f + 34, cu, mat=mat) + [
        field, sight_glass_x(fg, inner, cu), drawn_reticle(fg, cu, weapon_type, 90.0 - 0.4)]
    return P, _reflex_anchors(f, fg, cu)


def holo_pille(f, u, size='M', weapon_type='submachine_gun', mat=SIGHT_MAT):
    """H2 „Pille“ (MP-Standard): H0-Fuß und Gehäuse ohne Haube (Merkmal 1); auf dem Sockel ein Emitterblock mit Leuchtschlitz nach
    oben und drei Cyanpunkten zum Auge (Merkmal 2); die Pillenkontur ist nur gezeichnet (flach, Rolle sight_line) und steht 2 mm über
    dem Block."""
    w, h = {'S': (18, 21), 'M': (19, 23), 'L': (24, 29)}[size]     # Höhe M 26 → 23: Mündungsfeuer im Zielen sonst 20,2 % der Kontur (5.3 A ≤ 20 %)
    cu = sight_line(u)
    gb = cu - h / 2 - 2
    blk = gb - 5
    fg = f + 40
    pill = sight_rr(w, h, w / 2 - 0.01, n=10)
    inner = sight_rr(w - 0.8, h - 0.8, (w - 0.8) / 2 - 0.01, n=10)
    dots = part('sight_status', 'Statuspunkte', 'Status dots', 'sight', 'multi', 'energy', 'Drei Cyanpunkte zum Auge', 'am Emitterblock',
                bevel=0, parent_part='sight_mount',
                items=[dict(shape='cyl', axis='f', c=(blk + 2.5, x), a0=f + 28.4, a1=f + 29.2, r=0.7, segs=12) for x in (-2.6, 0, 2.6)])
    P = sight_platform(f, u, 16, blk, emitter=False, mat=mat) + [
        part('sight_block', 'Emitterblock', 'Emitter block', 'sight', 'prof', mat, 'Block 16 × 5 mm mit Leuchtschlitz oben',
             'auf dem Sockel', bevel=0.6, parent_part='sight_mount',
             pts=[(f + 29, blk - 0.5), (f + 46.6, blk - 0.5), (f + 46.6, gb - 0.2), (f + 30, gb - 0.2)], w=16),
        box('sight_emitter', 'Leuchtschlitz', 'Glow slit', 'sight', 'energy', 'Schlitz nach oben (projiziert die Kontur)', 'oben im Block',
            f + 34, f + 46, gb - 0.4, gb, 1.2, bevel=0.2, parent_part='sight_mount'),
        xprof('sight_line', 'Leuchtkontur', 'sight_line', fg - 0.05, fg, pill, cu, holes=[inner],
              func='Gezeichnete Pillenkontur (SUROS), flach in der Glasebene', attach='über dem Block (projiziert)', bevel=0,
              en='Glow outline', parent_part='sight_mount'),
        sight_glass_x(fg, sight_rr(w - 1, h - 1, (w - 1) / 2 - 0.01, n=10), cu), dots,
        drawn_reticle(fg - 0.1, cu, weapon_type, 90.0 - 0.5)]
    return P, _reflex_anchors(f, fg, cu, eye_part='sight_glass')


def scope_body(f_obj, cu, r_lens, r_out, length=120, tube_r=9.5, step=False, mat=SIGHT_MAT):
    """Zielfernrohr ohne Sitz: Rohr, Okular mit blanker Kante und Linse, Türme (alle `ads_hide`), Objektiv als Kegel zum Auge
    (r/d ≤ Ring/90 mm: im Zielen hinter der Ringstirn, kein Wulst), auf Wunsch zweistufig mit blankem Absatz, Objektivlinse r_lens
    4,5 mm hinter der Ringstirn. f_obj = Ringstirn, r_out = Ring außen an der Stirn."""
    from basic.reticles import SIGHT
    rel = SIGHT['types']['scope']['eye_relief_mm']
    eye, fe = f_obj - rel, f_obj - length
    k = r_out / rel
    fb = eye + (tube_r + 0.1) / k
    fl = f_obj - 4.5
    P = [cyl('scope_tube', 'Mittelrohr', 'Scope tube', 'sight', mat, 'Verbindet Okular und Objektiv; hohl', 'im Sattel (fest)',
             'f', (cu, 0), fe + 20, fb + 2, tube_r, r_in=tube_r - 1.5, segs=40, ads_hide=True),
         cyl('scope_eyepiece', 'Okular', 'Eyepiece', 'sight', mat, 'Augenseite, schlank; Socket_Sight hinten', 'am Mittelrohr (fest)',
             'f', (cu, 0), fe, fe + 22, tube_r + 1.5, r1=tube_r + 0.5, r_in=tube_r - 0.5, segs=40, bevel=R_SMALL, ads_hide=True),
         cyl('scope_eye_trim', 'Okularkante', 'Eyepiece trim', 'sight', 'trim', 'Blanke Kante am Okular', 'hinten am Okular',
             'f', (cu, 0), fe - 1, fe + 1.5, tube_r + 1.9, r_in=tube_r, segs=40, bevel=0.3, ads_hide=True),
         cyl('scope_ocular_glass', 'Okularlinse', 'Ocular lens', 'sight', 'glass_scope', 'Augenlinse', 'im Okular (fest)', 'f', (cu, 0),
             fe + 3, fe + 4, tube_r - 0.5, segs=40, bevel=0, ads_hide=True),
         cyl('scope_turret', 'Höhenturm', 'Elevation turret', 'sight', 'accent', 'Höhenverstellung (Bedienelement)', 'oben am Mittelrohr (fest)',
             'u', ((fe + fb) / 2 + 10, 0), cu + tube_r - 2, cu + tube_r + 5, 5.0, segs=32, ads_hide=True),
         cyl('scope_turret_w', 'Seitenturm', 'Windage turret', 'sight', mat, 'Seitenverstellung', 'rechts am Mittelrohr (fest)',
             'x', ((fe + fb) / 2 + 10, cu), -(tube_r - 2), -(tube_r + 4), 4.0, segs=32, ads_hide=True),
         cyl('scope_glass', 'Objektivlinse', 'Objective lens', 'sight', 'glass_scope', 'Linse vorn (im Zielen dasselbe Weltbild, lichte Öffnung)',
             'im Objektiv (fest)', 'f', (cu, 0), fl, fl + 0.5, r_lens, segs=48, bevel=0)]
    if step:
        fm = (fb + f_obj - 6) / 2
        P += [cyl('scope_objective', 'Objektiv', 'Objective bell', 'sight', mat, 'Kegel 1 zum Auge (kein Wulst)', 'am Mittelrohr (fest)',
                  'f', (cu, 0), fb, fm, tube_r + 0.1, r1=k * (fm - eye) - 0.3, r_in=tube_r - 1.1, segs=48, bevel=0.3),
              cyl('scope_step', 'Absatz', 'Step', 'sight', 'trim', 'Blanker Absatz zwischen den Kegeln', 'am Objektiv', 'f', (cu, 0), fm,
                  fm + 1.5, k * (fm - eye) - 0.3, r1=k * (fm - eye) - 1.3, r_in=k * (fm - eye) - 1.5, segs=48, bevel=0.2),
              cyl('scope_objective_b', 'Objektiv vorn', 'Objective front', 'sight', mat, 'Kegel 2 zum Auge', 'am Objektiv', 'f', (cu, 0),
                  fm + 1.5, f_obj - 6, k * (fm + 1.5 - eye) - 1.3, r1=k * (rel - 6) - 0.3, r_in=k * (fm + 1.5 - eye) - 2.5, segs=48,
                  bevel=0.3)]
    else:
        P.append(cyl('scope_objective', 'Objektiv', 'Objective bell', 'sight', mat, 'Kegel zum Auge (kein Wulst)', 'am Mittelrohr (fest)',
                     'f', (cu, 0), fb, f_obj - 6, tube_r + 0.1, r1=k * (rel - 6) - 0.3, r_in=tube_r - 1.3, segs=48, bevel=0.4))
    for q in P:
        q['parent_part'] = 'scope_mount_r'
    return P


def scope_ring(f_obj, cu, r_lens, mat=SIGHT_MAT):
    """Flacher Objektivring ohne Wulst: Innen- und Außenfläche laufen auf das Auge zu (Kegel durch den Augenpunkt), außen/innen
    RING_RATIO; innen deckt der Ring die Linse genau (lichte Öffnung = Linse); blanke Innenkante als dünne Linie. Liefert
    (Teile, Ring außen an der Stirn)."""
    from basic.reticles import SIGHT
    rel = SIGHT['types']['scope']['eye_relief_mm']
    k_in = r_lens / (rel - 4.5)
    ri0, ri1 = k_in * (rel - 6), k_in * rel
    r_out = RING_RATIO * ri1
    return [cyl('scope_rim', 'Objektivring', 'Objective ring', 'sight', mat, f'Flacher Stirnring, außen/innen {RING_RATIO:.2f}',
                'vorn auf dem Objektiv', 'f', (cu, 0), f_obj - 6, f_obj, RING_RATIO * ri0, r1=r_out, r_in=ri0, segs=64, bevel=0.5,
                parent_part='scope_mount_r'),
            cyl('scope_crown', 'Objektivkante', 'Objective trim', 'sight', 'trim', 'Blanke Innenkante (dünne Linie im Zielen)',
                'innen am Ring', 'f', (cu, 0), f_obj - 1.5, f_obj + 0.1, ri1 + 0.6, r_in=ri1, segs=64, bevel=0.1,
                parent_part='scope_mount_r')], r_out


def scope_foot(f0, f1, u, top, pid='scope_mount_f', mat=SIGHT_MAT):
    """H0-Klemmfuß unter dem Objektiv: zweistufig, oranger Hebel; u = Schienenoberkante, top = Oberkante der oberen Stufe."""
    return [part(pid, 'Klemmfuß vorn', 'Front sight mount', 'sight', 'multi', mat, 'Klemmfuß unter dem Objektiv (gestuft)',
                 'Klemmung auf Schiene (lösbar)', bevel=R_SMALL, iface='BRI-22', parent_part='scope_mount_r',
                 items=[dict(shape='box', f0=f0, f1=f1, u0=u + 0.5, u1=u + 3.5, w=23),
                        dict(shape='box', f0=f0 + 2, f1=f1 - 2, u0=u + 3, u1=top, w=18)]),
            part('sight_clamp', 'Klemmhebel', 'Clamp lever', 'sight', 'prof', 'accent', 'Spannt den Klemmfuß werkzeuglos', 'links am Klemmfuß',
                 bevel=R_FINE, parent_part=pid, pts=[(f0 + 4, u + 0.8), (f1 - 6, u + 0.8), (f1 - 4, u + 3.2), (f0 + 4, u + 3.6)], w=1.8,
                 x=12.4)]


def scope_saddle(f0, f1, seat_u, cu, fe, tube_r=9.5, mat=SIGHT_MAT):
    """Rohrsattel hinter dem Augenpunkt (Konzept A, im Zielen unsichtbar): Wiege unter Okular und Rohr (Oberkante folgt der
    Unterkante des Zielfernrohrs mit 0,3 mm Luft), unten ein Klemmblock um die Schiene mit Oberkante seat_u; Spannband um das
    Okular. fe = hinteres Okularende (Okular fe … fe + 22, Kegel r tube_r + 1,5 → + 0,5)."""
    def low(f):                       # Unterkante des Zielfernrohrs bei f (Okular bis fe + 22, danach Rohr)
        return cu - (tube_r + 1.5 - (f - fe) / 22 if f <= fe + 22 else tube_r)
    top = [(f1, low(f1) - 0.3)] + ([(fe + 22.01, low(fe + 22.01) - 0.3), (fe + 22, low(fe + 22) - 0.3)] if f0 < fe + 22 < f1 else []) \
        + [(f0, low(f0) - 0.3)]
    mv = dict(kind='translate', pivot=((f0 + f1) / 2, seat_u, 0), vector_mm=(0, 80, 0), event='swap_sight',
              note='Spannband und Klemmhebel lösen, Zielfernrohr senkrecht abnehmen', removable=True)
    fs = (f0 + 4, min(f1, fe + 22) - 6)
    rs = tube_r + 1.5 - (fs[0] - fe) / 22 + 0.1
    return [part('scope_mount_r', 'Rohrsattel', 'Scope saddle', 'sight', 'multi', mat,
                 'Wiege unter Okular und Rohr hinter dem Augenpunkt (im Zielen unsichtbar); Klemmblock um die Schiene BRI-22',
                 'Klemmung auf Schiene (lösbar)', bevel=R_SMALL, iface='BRI-22', move=mv,
                 items=[dict(shape='prof', pts=[(f0, seat_u - 7.5), (f1, seat_u - 7.5)] + top, w=26)]
                 + screws([(f0 + 4, seat_u - 3.5), (f1 - 4, seat_u - 3.5)], -13.0, r=1.2, h=0.6)
                 + screws([(f0 + 4, seat_u - 3.5), (f1 - 4, seat_u - 3.5)], 13.0, r=1.2, h=0.6)),
            cyl('scope_strap', 'Spannband', 'Scope strap', 'sight', mat, 'Hält das Okular in der Wiege', 'um das Okular, im Sattel verschraubt',
                'f', (cu, 0), fs[0], fs[1], rs + 1.6, r_in=rs, segs=40, ads_hide=True, parent_part='scope_mount_r')]


def scope_anchors(f_obj, fe, cu, part_eye='scope_objective'):
    from basic.reticles import SIGHT
    rel = SIGHT['types']['scope']['eye_relief_mm']
    return {'Socket_Sight': dict(at=(fe, cu, 0), part='scope_eyepiece', note='hinteres Okularende auf der Visierlinie'),
            'Socket_Objective': dict(at=(f_obj, cu, 0), part='scope_rim', note='Stirn des Objektivrings'),
            'Socket_Reticle': dict(at=(f_obj - 4.5, cu, 0), part='scope_glass', note='gezeichnetes Absehen auf der Objektivlinse'),
            'Socket_Eye': dict(at=(f_obj - rel, cu, 0), part=part_eye, sight_type='scope', std=True,
                               note=f'Augenpunkt beim Zielen (Visier-Standard: {rel:.0f} mm hinter dem Objektivring, ads_hide-Teile aus)')}


def scope_tropfen(f_obj, u, cu, size='M', weapon_type='scout_rifle', seat_u=None, length=120, mat=SIGHT_MAT, saddle_f=None):
    """Z1 „Tropfen“ (Scout-Standard), Sitz nach Konzept A: Rohrsattel hinter dem Auge (Wiege unter dem Okular, Klemmblock um die
    Schiene mit Oberkante seat_u, Standard u; saddle_f = Längslage, Standard Okularende + 2 bis Augenpunkt − 2), H0-Klemmfuß unter dem Objektiv auf der Schiene u. Flacher Ring ohne Wulst (außen/innen 1,29); der Sockel unter dem Ring läuft
    tangential in die Ringstirn – von hinten eine Tropfenkontur (Merkmal 1); Objektiv zweistufig mit blankem Absatz (Merkmal 2).
    f_obj = Ringstirn, cu = Visierlinie. Liefert (Teile, Anker)."""
    from basic.reticles import SIGHT
    rel = SIGHT['types']['scope']['eye_relief_mm']
    r_lens = SCOPE_SIZES[size]
    ring, r_out = scope_ring(f_obj, cu, r_lens, mat=mat)
    eye, fe = f_obj - rel, f_obj - length
    bt = u + 6
    b = min(bt - cu, -r_out - 3)          # große Ringe sitzen fast auf dem Fuß: Sockel reicht dann in den Fuß
    tang = 42
    keel = [(11, b), (r_out * math.cos(math.radians(-tang)), r_out * math.sin(math.radians(-tang)))] \
        + sight_arc(r_out, -tang, -180 + tang, 24)[1:-1] \
        + [(r_out * math.cos(math.radians(-180 + tang)), r_out * math.sin(math.radians(-180 + tang))), (-11, b)]
    sf = saddle_f or (fe + 2, eye - 2)
    P = scope_saddle(sf[0], sf[1], u if seat_u is None else seat_u, cu, fe, mat=mat) \
        + scope_body(f_obj, cu, r_lens, r_out, length=length, step=True, mat=mat) + ring + scope_foot(f_obj - 30, f_obj, u, bt, mat=mat) + [
            xprof('scope_keel', 'Tropfensockel', mat, f_obj - 16, f_obj - 2, keel, cu, func='Sockel läuft tangential in die Ringstirn',
                  attach='auf dem Klemmfuß unter dem Ring (fest)', en='Drop base', parent_part='scope_mount_r'),
            drawn_reticle(f_obj - 4.5, cu, weapon_type, rel - 4.5, parent='scope_mount_r')]
    return P, scope_anchors(f_obj, fe, cu)


def box_scope_v21(f, u, style='prism', reticle_kind='chevron', reticle_color='cyan', reticle_weight='fine'):
    """Kastenoptik v2.1 nach Destiny-Scouts (Nutzerbilder 24.10.2026): kompakter Kasten statt Rohr mit Ringen.
    style 'prism': kurzer quadratischer Kasten (Graphit) mit runder Linse vorn, schmalem Okular, seitlichen Knöpfen, Sockel.
    style 'flat' : flacher, langer Kasten zweifarbig (Creme oben, Graphit unten) mit rechteckiger Öffnung und Lüftungsschlitzen.
    Der Kasten ist ein Rahmen mit durchgehender Bohrung; im Zielen (Augenpunkt 90 mm vor der Öffnung) sieht man durch ihn auf
    Linse und Absehen; Okular/Augenring tragen `ads_hide`. Liefert (Teile, Anker, Visierlinie cu)."""
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
