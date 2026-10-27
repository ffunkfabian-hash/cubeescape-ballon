"""Parametrischer Militärhelm (Runde 5): Haube, Gesichtsmaske, Seiten-/Hinterkopfgehäuse, Kieferabschluss, Kommunikationstechnik.

Nach der Konstruktionsanweisung des Nutzers vom 27.10.2026 zur Referenz Q-D2-HELM-MIL (Konzeptblatt mit Front, Dreiviertel, Seite,
Rückseite; nur Prinzipien, Schal und Körper entfallen). Alle Maße in der Einheit E = Helmhöhe ohne Antennen / 100 und in den
Koordinaten der Anweisung: Z oben, X seitlich, vorn −Y. Umrechnung in den Kopfrahmen (mm): x = X·E, y = −Y·E, z = (Z + Z0)·E.
Alle Hauptmaße stehen zentral in PARAMS und lassen sich je Studie überschreiben (head(dict(style='mil', helmet={...}))).

Gruppen (je eigene Teile): Haube (oben weich gerundet, hinten kurzer Überstand als Dach über dem Gehäuse), Maske (breite,
leicht gewölbte Frontschale nach dem Seitenprofil, Braue am weitesten vorn, zum Kinn zurücklaufend), Gehäuse (hell, rund um Seiten
und Hinterkopf, vorn hinter der Maskenkante), Kiefer (U-Rahmen mit Kinnbügel und Schenkeln hinter den Wangen, unten als Band um den
Kopf). Stufe 1 (stage=1) baut nur diese Grundkörper zur Prüfung von Silhouette und Proportion; Stufe 2 ergänzt Augen, Wangen,
Gesichtsmitte, Hinterkopfmodul, Seitenmodule mit Halterung, Antennen und das gerippte Kabel um den Hinterkopf.
"""
import math
import os

from basic.arms.forms import _pt as contour_pt
from basic.robot.shapes import loft, wrap, sec, tab
from .body import cyl, tube, slot, surf_y, _lerp

PARAMS = dict(
    h=270,                       # Helmhöhe ohne Antennen (mm) = 100 E
    z0=-8,                       # Unterkante des Kieferbands bei Z = 10 liegt ≈ 2 E über Socket_Neck
    # Haube: (Z, halbe Breite, Front-Y, Rück-Y); Scheitel über der Kopfmitte, vorn lange konvexe Kurve, hinten Überstand
    cap=[(67, 40.6, -33, 42.6), (70, 40.5, -33, 42.4), (74, 40.4, -33, 41.2), (78, 40.0, -32.5, 40.2), (82, 38.8, -31, 38.8),
         (87, 36.8, -28.6, 36.6), (91, 33.8, -25.4, 33.6), (94.5, 29.4, -21.2, 29.6), (97.4, 22.2, -15.2, 22.8), (99.3, 12.6, -8, 13.2),
         (100, 4, -2, 5)],
    cap_n=2.3,
    # Maske: Seitenprofil der Außenkontur (Y, Z) und Breite (Z, halbe Breite); Querschnitt halbe Tiefe mask_b, Exponent mask_n
    profile=[(-31, 82), (-40, 66), (-36, 43), (-27, 15)],
    mask_w=[(15, 23), (29, 26), (43, 30), (55, 33.6), (60, 34), (66, 34.4), (74, 35), (82, 35)],
    mask_b=22, mask_n=4.0, mask_span=86, mask_t=1.8,
    # Gehäuse: (Z, halbe Breite, Mitte-Y, halbe Tiefe), Winkelbereich ab vorn (hinter der Maskenseite) um den Hinterkopf
    shell=[(18, 32, 3, 33), (30, 35, 2.5, 35.5), (45, 37.5, 2, 37), (60, 38.3, 2, 37), (69, 38.5, 2, 37)],
    shell_n=3.0, shell_from=48, shell_t=1.6,
    # Kiefer: Band um den Kopf (Z unten, Z oben, halbe Breite, Front-Y, Rück-Y), Kinnbügel (halbe Breite, Front-Y), Schenkel
    jaw=(10, 19, 31, -29, 37.5), chin=(25, -30.5), chin_n=5.0, legs=(15, 53), leg_w=8,
    # Augen: Breite, Höhe, Steg, außen höher, Mitte Z, Fassung
    eye=dict(w=16, h=5, gap=20, rise=4, z=59, frame=1.0),
    # Gesichtsmitte (Trapez) und Wangen
    trap=dict(z0=20, z1=49, w0=20, w1=10, ridge=2), cheek=dict(z0=22, z1=55.5),
    # Hinterkopfmodul, Seitenmodule, Antennen, Kabel
    rear=dict(w=30, h=15, d=5, z=60.5),
    comm=dict(z=46, y=-2, h=28, d=19, lat=9),
    antenna=dict(r=0.75, over=5), stub=dict(len=19, d=3, tilt=12, cap=4.8),
    cable=dict(z=25, d=3.6, pitch=1.15, off=2.4),
)


def ang_x(s, x):
    """Winkel (Grad, Parameter der Superellipse wie forms._pt), an dem die Kontur s die Breite x (mm, ≥ 0) erreicht."""
    u = min(max(x - s['x'], 0.0) / (s['a'] + 1e-9), 1.0)
    return math.degrees(math.asin(u ** (s['n'] / 2)))


def _catmull(pts, z):
    """Front-Y der Maske bei Z: Catmull-Rom durch die Profilpunkte (Y, Z), Z absteigend sortiert."""
    P = sorted(pts, key=lambda p: p[1])
    if z <= P[0][1]:
        return P[0][0]
    if z >= P[-1][1]:
        return P[-1][0]
    i = max(k for k in range(len(P) - 1) if P[k][1] <= z)
    p0, p1, p2, p3 = P[max(i - 1, 0)], P[i], P[i + 1], P[min(i + 2, len(P) - 1)]
    t = (z - p1[1]) / (p2[1] - p1[1])
    m1 = (p2[0] - p0[0]) / 2
    m2 = (p3[0] - p1[0]) / 2
    h00, h10, h01, h11 = 2 * t ** 3 - 3 * t * t + 1, t ** 3 - 2 * t * t + t, -2 * t ** 3 + 3 * t * t, t ** 3 - t * t
    return h00 * p1[0] + h10 * m1 + h01 * p2[0] + h11 * m2


def parts(over=None):
    P = dict(PARAMS)
    for k, v in (over or {}).items():
        P[k] = dict(P[k], **v) if isinstance(P.get(k), dict) else v
    stage = int(os.environ.get('BALLON_HELM_STAGE', P.get('stage', 2)))
    E = P['h'] / 100

    def zz(Z):
        return (Z + P['z0']) * E

    def S(Z, a, front, back, n):    # Querschnitt aus Anweisungsmaßen (Front-/Rück-Y) im Kopfrahmen
        return sec(zz(Z), a * E, (back - front) / 2 * E, -(front + back) / 2 * E, n=n)
    out = []
    # ---- 1 Schädelhaube
    cap = [S(Z, a, f, b, P['cap_n']) for Z, a, f, b in P['cap']]
    out += [loft('cap', 'Schädelhaube', 'head', 'anodized', cap, sharp=40, bevel=1.4)]
    # ---- 2 Gesichtsmaske: dichte Querschnitte nach dem Seitenprofil (Catmull-Rom), Breite linear
    W = tab([(z, a, 0, 0) for z, a in P['mask_w']])
    mb, mn = P['mask_b'], P['mask_n']
    mz = [15, 19, 24, 29, 34, 39, 43, 48, 52, 56, 60, 63, 66, 70, 74, 78, 82]
    mrows = [(zz(Z), W(Z)['a'] * E, mb * E, -(_catmull(P['profile'], Z) + mb) * E) for Z in mz]
    M = tab(mrows)

    def MS(Z, g=0.0, **kw):
        return M(zz(Z), g, n=mn, **kw)
    sp = P['mask_span']
    # ---- 3 Gesichtsmaske mit Augen (Stufe 2): Schlitze durch die Schale, zweistufige Fassung, Scheiben dahinter
    e = P['eye']
    mt = P['mask_t'] * E
    cuts, glass = [], []
    if stage >= 2:
        sl = math.degrees(math.atan2(e['rise'], e['w']))
        for sx in (1, -1):
            xc, zc = sx * (e['gap'] / 2 + e['w'] / 2) * E, zz(e['z'])
            ys = surf_y(MS(e['z']), abs(xc)) + mt

            def box(k, L, H, xc=xc, zc=zc, ys=ys, sx=sx):
                D = 2 * k + 20
                return slot((xc, ys - k + D / 2, zc), (D, L, H), rz=90, rx=-sx * sl)
            fr = e['frame'] * E
            cuts += [box(0.5 * E, e['w'] * E + 2 * fr, e['h'] * E + 2 * fr), box(1.0 * E, e['w'] * E + 0.8 * fr, e['h'] * E + 0.8 * fr),
                     box(mt + 2.5, e['w'] * E, e['h'] * E)]
            yg = ys - mt - 0.6 * E
            glass += [(f'eye_glass_{"r" if sx > 0 else "l"}', 'Sichtscheibe', 'head', 'box', 'reticle_cyan',
                       dict(d=(e['w'] * E + 2, 1.6, e['h'] * E + 2), c=(xc, yg, zc), bevel=0.3, rot=('y', -sx * sl, (xc, yg, zc))))]
    out += [wrap('mask', 'Gesichtsmaske', 'head', 'graphite', [MS(Z) for Z in mz], -sp, sp, mt, sharp=30, bevel=1.0, cuts=cuts)] + glass
    # Innenkern: schließt Maske und Gehäuse innen (hinter den Scheiben dunkel)
    out += [loft('helmet_core', 'Helmkern', 'head', 'graphite',
                 [S(12, 26, -26, 30, 2.6), S(40, 31, -30, 33, 2.6), S(66, 33.5, -33, 35, 2.6), S(80, 32, -28, 34, 2.6)])]
    # ---- 3 Seiten-/Hinterkopfgehäuse (hell), vorn hinter der Maskenseite, rund um den Hinterkopf
    sh = [sec(zz(Z), a * E, b * E, -c * E, n=P['shell_n']) for Z, a, c, b in P['shell']]
    f0 = P['shell_from']
    out += [wrap('shell', 'Seiten- und Hinterkopfgehäuse', 'head', 'shell', sh, f0, 360 - f0, P['shell_t'] * E, sharp=30, bevel=1.2)]
    # ---- 4 Kieferabschluss: Band um den Kopf, Kinnbügel mit flacher Front, Schenkel hinter den Wangen
    jz0, jz1, ja, jf, jb = P['jaw']
    band = [S(jz0, ja, jf, jb, 3.6), S(jz1, ja + 0.6, jf + 0.4, jb, 3.6)]
    out += [wrap('jaw_band', 'Kieferband', 'head', 'shell', band, -180, 180, 1.8 * E, sub=2, sharp=30, bevel=1.0)]
    cw, cf = P['chin']
    chin = [S(jz0 - 0.6, cw, cf, jb, P['chin_n']), S(jz1 + 0.4, cw + 0.4, cf + 0.3, jb, P['chin_n'])]
    cr = ang_x(chin[0], (cw - 1) * E)
    out += [wrap('chin_bar', 'Kinnbügel', 'head', 'shell', chin, -cr, cr, 1.6 * E, sharp=25, bevel=1.4)]
    lz0, lz1 = P['legs']
    for k, sx in (('r', 1), ('l', -1)):
        rows = []
        for Z in (lz0, (lz0 + lz1) / 2, lz1):
            s = MS(Z, 0.15 * E)
            a0 = ang_x(s, s['a'] - P['leg_w'] * E)
            rows.append(dict(s, a0=a0 if sx > 0 else -sp, a1=sp if sx > 0 else -a0))
        out += [wrap(f'jaw_leg_{k}', 'Kieferschenkel', 'head', 'shell', rows, rows[0]['a0'], rows[0]['a1'], 1.6 * E, sharp=25, bevel=1.0)]
    if stage < 2:
        return out
    # ---- 5 Wangenplatten und Gesichtsmitte
    tr = P['trap']

    def tx(Z):                      # halbe Breite des Trapezes
        u = (Z - tr['z0']) / (tr['z1'] - tr['z0'])
        return (tr['w0'] + (tr['w1'] - tr['w0']) * min(1.0, max(0.0, u))) / 2 * E
    cz0, cz1 = P['cheek']['z0'], P['cheek']['z1']
    gc = mt + 0.35 * E
    for k, sx in (('r', 1), ('l', -1)):
        def lo(Z, x0, x1, sx=sx):
            s = MS(Z, gc)
            a0, a1 = ang_x(s, x0), ang_x(s, x1)
            return dict(s, a0=a0 if sx > 0 else -a1, a1=a1 if sx > 0 else -a0)
        Ws = [W(Z)['a'] * E for Z in (cz0, cz0 + 4, 40, cz1)]
        rows = [lo(cz0, tx(cz0) + 1.6 * E, Ws[0] - 4 * E), lo(cz0 + 4, tx(cz0 + 4) + E, Ws[1] - 1.2 * E),
                lo(40, tx(40) + E, Ws[2] - 0.8 * E), lo(cz1, tx(cz1) + E, Ws[3] - 0.8 * E)]
        j0 = (Ws[3] - 3 * E, zz(cz1 - 3))                         # Fuge von außen oben nach innen unten
        j1 = (tx(cz0 + 7) + 2 * E, zz(cz0 + 7))
        jl = math.hypot(j1[0] - j0[0], j1[1] - j0[1])
        ja_ = math.degrees(math.atan2(j0[1] - j1[1], j0[0] - j1[0]))
        jm = ((j0[0] + j1[0]) / 2, (j0[1] + j1[1]) / 2)
        Zm = jm[1] / E - P['z0']
        out += [wrap(f'cheek_{k}', 'Wangenplatte', 'head', 'anodized', rows, rows[0]['a0'], rows[0]['a1'], 1.5 * E, sharp=25, bevel=1.4,
                     cuts=[slot((sx * jm[0], surf_y(MS(Zm, gc + 1.5 * E), jm[0]), jm[1]), (12, jl + 10, 0.9 * E), rz=90, rx=-sx * ja_)])]
    gt = mt + 0.2 * E
    tsec = [dict(MS(Z, gt), a0=-ang_x(MS(Z, gt), tx(Z)), a1=ang_x(MS(Z, gt), tx(Z))) for Z in (tr['z0'], (tr['z0'] + tr['z1']) / 2, tr['z1'])]
    zt = tr['z1'] - 3.5
    out += [wrap('face_center', 'Gesichtsmitte', 'head', 'graphite', tsec, tsec[0]['a0'], tsec[0]['a1'], 0.9 * E, sharp=25, bevel=0.6,
                 cuts=[slot((0, surf_y(MS(zt, gt + 0.9 * E), 0), zz(zt)), (10, 4 * E, 2.4 * E))])]
    for k, sx in (('r', 1), ('l', -1)):
        rs = []
        for Z in (tr['z0'], tr['z1']):
            s = MS(Z, gt)
            a1_, a0_ = ang_x(s, tx(Z)), ang_x(s, tx(Z) - tr['ridge'] * E)
            rs.append(dict(s, a0=a0_ if sx > 0 else -a1_, a1=a1_ if sx > 0 else -a0_))
        out += [wrap(f'face_ridge_{k}', 'Seitenleiste', 'head', 'graphite', rs, rs[0]['a0'], rs[0]['a1'], 2.2 * E, steps=2, sharp=25,
                     bevel=0.8)]
    # ---- 6 Hinterkopfmodul unter dem Haubenüberstand: flach, querrechteckig, Felder und Vertiefungen
    rm = P['rear']
    sb = sh[2]
    yb = sb['y'] - sb['b'] - P['shell_t'] * E
    rc = (0, yb - rm['d'] / 2 * E + 1.0 * E, zz(rm['z']))
    out += [('rear_module', 'Hinterkopfmodul', 'head', 'box', 'dark_metal', dict(d=(rm['w'] * E, rm['d'] * E, rm['h'] * E), c=rc, bevel=2.4))]
    yf = rc[1] - rm['d'] / 2 * E
    out += [(f'rear_field_{k}', 'Modulfeld', 'head', 'box', 'graphite', dict(d=(10.5 * E, 1.2 * E, 9 * E), c=(sx * 7.2 * E, yf - 0.3 * E, rc[2] + 0.6 * E), bevel=1.0))
            for k, sx in (('r', 1), ('l', -1))]
    out += [('rear_slot', 'Modulvertiefung', 'head', 'box', 'anodized', dict(d=(3.4 * E, 0.8 * E, 9 * E), c=(0, yf + 0.1 * E, rc[2] + 0.6 * E), bevel=0.6)),
            ('rear_strip', 'Modulleiste', 'head', 'box', 'trim', dict(d=(24 * E, 0.6 * E, 0.9 * E), c=(0, yf - 0.1 * E, rc[2] - 5.6 * E), bevel=0.3))]
    # ---- 7 Seitenmodule auf Ohrhöhe: vertikal oval, flache Außenfläche, kräftiger runder Rand, Halterung über das Gehäuse
    cm = P['comm']
    sz = sec(zz(cm['z']), 0, 0)
    sa = [s for s in sh if s['z'] <= sz['z']][-1]
    xin = sa['a'] + P['shell_t'] * E
    for k, sx in (('r', 1), ('l', -1)):
        xc = sx * (xin + cm['lat'] / 2 * E)
        yc = -cm['y'] * E
        zc = zz(cm['z'])
        hh, dd = cm['h'] / 2 * E, cm['d'] / 2 * E

        def ov(scale_h, scale_d, x, a, n=3.0, m=9):
            rows = []
            for i in range(m):
                u = -1 + 2 * i / (m - 1)
                rows.append(sec(zc + u * hh * scale_h, a, max(1.2, dd * scale_d * math.sqrt(max(0.0, 1 - u * u)) ** 0.85), yc, x, n=n))
            return rows
        out += [loft(f'comm_{k}', 'Seitenmodul', 'head', 'dark_metal', ov(1.0, 1.0, xc, cm['lat'] / 2 * E), sharp=40, bevel=1.2),
                loft(f'comm_{k}_rim', 'Modulrand', 'head', 'rubber', ov(1.06, 1.06, xc + sx * (cm['lat'] / 2 - 1.3) * E, 1.3 * E, n=2.4),
                     sharp=60),
                loft(f'comm_{k}_face', 'Modulfläche', 'head', 'dark_metal', ov(0.84, 0.82, xc + sx * (cm['lat'] / 2 - 0.2) * E, 0.8 * E),
                     sharp=40)]
        xo = xc + sx * (cm['lat'] / 2 + 0.6) * E          # Halterung: senkrechter Bügel über die Außenfläche bis unter die Haube
        top = zz(P['cap'][0][0])
        out += [(f'comm_{k}_holder', 'Modulhalterung', 'head', 'box', 'dark_metal',
                 dict(d=(1.1 * E, 4 * E, top - (zc - 0.35 * hh)), c=(xo, yc, (top + zc - 0.35 * hh) / 2), bevel=0.8)),
                (f'comm_{k}_holder_top', 'Halterungsfuß', 'head', 'box', 'dark_metal',
                 dict(d=(abs(xo) - xin + 2 * E, 4 * E, 1.4 * E), c=(sx * (xin + abs(xo)) / 2, yc, top - 0.2 * E), bevel=0.6)),
                cyl(f'comm_{k}_pin', 'Halterungsschraube', 'head', 'trim', 'x', 1.1 * E, 1.4 * E, (xo + sx * 0.4 * E, yc, zc))]
    # ---- 8 Antennen: lange dünne rechts am Körper (+X, in der Front links), kurzer dicker Stab gegenüber
    an, st = P['antenna'], P['stub']
    xa = xin + cm['lat'] * E * 0.55
    a0 = (xa, -cm['y'] * E + cm['d'] / 2 * E * 0.55, zz(cm['z']) + cm['h'] / 2 * E * 0.7)
    a1 = (xa + 0.8 * E, a0[1] - 0.6 * E, zz(100 + an['over']))
    out += [tube('antenna', 'Stabantenne', 'head', 'dark_metal', [a0, a1], an['r'] * E, segs=8),
            cyl('antenna_tip', 'Antennenspitze', 'head', 'trim', 'z', an['r'] * E + 0.7, 4, (a1[0], a1[1], a1[2] + 1)),
            ('antenna_clip', 'Antennenhalter', 'head', 'box', 'dark_metal', dict(d=(2.6 * E, 3 * E, 4 * E), c=(a0[0], a0[1], a0[2] + 1.5 * E), bevel=0.6))]
    t_ = math.radians(st['tilt'])
    b0 = (-xa, a0[1], a0[2])
    b1 = (b0[0] - st['len'] * E * math.sin(t_), b0[1], b0[2] + st['len'] * E * math.cos(t_))
    out += [tube('stub', 'Antennenstab', 'head', 'dark_metal', [b0, b1], st['d'] / 2 * E, segs=12),
            tube('stub_cap', 'Endkappe', 'head', 'graphite', [_lerp(b0, b1, 0.86), _lerp(b0, b1, 1.05)], st['cap'] / 2 * E, segs=16),
            ('stub_clip', 'Stabhalter', 'head', 'box', 'dark_metal', dict(d=(3.4 * E, 3.4 * E, 4 * E), c=(b0[0], b0[1], b0[2] + 1.2 * E), bevel=0.6))]
    # ---- 9 Kabel: gerippt (Wendel um eine Seele), vom unteren Modulrand nach hinten um den Hinterkopf zum anderen Modul
    cb = P['cable']
    s_c = [s for s in sh if s['z'] <= zz(cb['z'])][-1]
    s_c = dict(s_c, z=zz(cb['z']))
    yc = -cm['y'] * E
    zb = zz(cm['z']) - cm['h'] / 2 * E * 0.86
    xm = xin + cm['lat'] / 2 * E
    path = [(xm, yc, zb), (xm - 0.4 * E, yc - 1.6 * E, zb - 3 * E)]
    path += [contour_pt(s_c, u, (P['shell_t'] + cb['off']) * E) for u in range(78, 283, 12)]
    path += [(-xm + 0.4 * E, yc - 1.6 * E, zb - 3 * E), (-xm, yc, zb)]
    out += [tube('cable', 'Kabelseele', 'head', 'rubber', path, cb['d'] / 2 * E * 0.72, segs=10)]
    # Wendel: Punkte entlang der geglätteten Bahn
    L = [0.0]
    for p, q in zip(path, path[1:]):
        L.append(L[-1] + math.dist(p, q))
    turns = int(L[-1] / (cb['pitch'] * E))
    helix, prev_n = [], None
    for i in range(turns * 8 + 1):
        s_ = L[-1] * i / (turns * 8)
        j = max(k for k in range(len(L) - 1) if L[k] <= s_) if s_ < L[-1] else len(L) - 2
        t = (s_ - L[j]) / max(L[j + 1] - L[j], 1e-6)
        p = _lerp(path[j], path[j + 1], t)
        d = [path[j + 1][m] - path[j][m] for m in range(3)]
        dl = math.sqrt(sum(v * v for v in d)) or 1.0
        d = [v / dl for v in d]
        up = (0, 0, 1) if abs(d[2]) < 0.9 else (1, 0, 0)
        n1 = (d[1] * up[2] - d[2] * up[1], d[2] * up[0] - d[0] * up[2], d[0] * up[1] - d[1] * up[0])
        nl = math.sqrt(sum(v * v for v in n1)) or 1.0
        n1 = tuple(v / nl for v in n1)
        n2 = (d[1] * n1[2] - d[2] * n1[1], d[2] * n1[0] - d[0] * n1[2], d[0] * n1[1] - d[1] * n1[0])
        ang = 2 * math.pi * i / 8
        r = cb['d'] / 2 * E * 0.78
        helix.append(tuple(p[m] + r * (math.cos(ang) * n1[m] + math.sin(ang) * n2[m]) for m in range(3)))
    out += [tube('cable_wrap', 'Kabelwendel', 'head', 'rubber', helix, cb['d'] / 2 * E * 0.24, segs=6)]
    for k, sx in (('r', 1), ('l', -1)):            # Anschlüsse in die Module
        out += [tube(f'cable_plug_{k}', 'Kabelanschluss', 'head', 'dark_metal', [(sx * xm, yc, zb - 0.8 * E), (sx * xm, yc, zb + 1.6 * E)],
                     cb['d'] / 2 * E * 1.15, segs=12)]
    return out
