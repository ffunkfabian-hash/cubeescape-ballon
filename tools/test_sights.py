"""Prüft den Visier-Baukasten v3 ohne Blender (0.21 „Ironsight“, Visier-Standard 3 mit Erweiterung, docs/visier-konzept.md):

  python3 tools/test_sights.py            (läuft in ./check)

- Öffnung im Zielen: lichte Öffnung (Glasbreite bzw. Objektivlinse) als Anteil der Bildbreite bei 75°, gemessen im echten Abstand
  zum Augenpunkt. Gebaute Visiere (common: H0, H2, H4, Z1) in M im Standard, in S/L im Standard oder in der zugelassenen Variante
  (`reticles.share_band`); Familienwaffen im Standard oder in der Variante ihres Typs.
- Ring ohne Wulst: Zielfernrohre außen/innen an der Ringstirn ≈ 1,29 (± 0,02), Innenfläche läuft auf den Augenpunkt zu.
- Absehen gezeichnet: `sight_reticle` flach (Querprofile ≤ 0,1 mm) in der Glasebene (± 0,5 mm), reine Emission, Hüftform der
  Klasse in Hüftgröße (± 3 %, dazu der Zuwachs, wenn die Linie auf die Mindestbreite geklemmt ist – 0.25, Caret 1 % H), Linien
  mindestens 1,6 px bei 1280 px Bildbreite.
- Kimme/Korn-Linie und Mini-Reflex, wo verwendet (Baukasten-Katalog): Augenpunkt auf Schiene + 11 bzw. + 15 mm.
- Kimme/Korn K1 an Familienwaffen (0.24, BASIC-04/05): Klasse passt, Linie Träger + 11 mm, Augenpunkt 70 mm hinter der Kimme,
  Lichtspalt zwischen Korn und Kerbe je Seite ≥ 0,25° (≈ 4 px bei 1280 px), Kornpunkt in der Kerbe, Kimmen- und Kornfuß liegen
  auf dem Träger auf.
- Scharfschütze Z3 (0.25, BASIC-09): Vollbild-Typ zur Klasse, Visierhöhe 66 ± 4, Augenpunkt 90 mm hinter dem Ring, Ring ohne Wulst,
  gezeichnetes Absehen; Vollbild-Zielbild: Linse auf der Visierlinie, Kreis 80–83 % H, Duplex mit freier Mitte (`sight_kit.FULLSCREEN`).
  Kimme/Korn K2 (BASIC-08): wie K1, Kerbe als Lücke des Hörner-Querprofils auf der Visierlinie.
- Bauteil-Hash des Unity-Exports (`export_unity.parts_sha`) ist bei 1 ulp Abweichung gleich (Mac und Linux-CI).
- Mündungsfeuer im Zielen an der MP-Pille: in der Kontur gezählt (kleiner als im umschließenden Rechteck) und ≤ 20 % (5.3 A).
"""
import glob
import importlib
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic import common as C  # noqa: E402
from basic import reticles as RT  # noqa: E402

TAN = math.tan(math.radians(RT.SIGHT['fov_ref_deg'] / 2))


def opening_share(parts, anchors):
    """Lichte Öffnung im Zielen als Anteil der Bildbreite (75°): Breite der Visierscheibe bzw. Durchmesser der Objektivlinse im
    Abstand ihrer Ebene vom Augenpunkt."""
    P = {p['id']: p for p in parts}
    eye = anchors['Socket_Eye']['at'][0]
    if 'sight_glass' in P:
        g = P['sight_glass']
        w = (max(q[0] for q in g['pts']) - min(q[0] for q in g['pts'])) if 'pts' in g else g['ww']
        return w / (2 * (g['f0'] - eye) * TAN)
    g = P['scope_glass']
    return 2 * g['r'] / (2 * (g['a0'] - eye) * TAN)


def ring_ratio(parts):
    """Ring außen/innen an der Ringstirn (scope_rim: Kegel, innen mit r1/r skaliert wie kit.mesh_cyl)."""
    r = next(p for p in parts if p['id'] == 'scope_rim')
    r1 = r.get('r1', r['r'])
    return r1 / (r['r_in'] * r1 / r['r'])


def check_reticle(parts, anchors, wtype):
    """Gezeichnetes Absehen flach in der Glasebene: Fehlerliste."""
    from tools.export_unity import kit_materials
    bad = []
    P = {p['id']: p for p in parts}
    q = P.get('sight_reticle')
    if not q:
        return ['kein sight_reticle']
    role = kit_materials().get(q['mat'], {})
    if not q['mat'].startswith('reticle_') or not role.get('emit_only'):
        bad.append(f"Rolle {q['mat']} ist keine reine Emission")
    items = q.get('items') or []
    if not items or any(i.get('shape') != 'xprof' or abs(i['f1'] - i['f0']) > 0.1 for i in items):
        bad.append('Absehen nicht flach (nur Querprofile ≤ 0,1 mm dick)')
        return bad
    g = P.get('sight_glass') or P.get('scope_glass')
    g0, g1 = (g['f0'], g['f1']) if 'f0' in g else (g['a0'], g['a1'])
    f = sum(i['f0'] + i['f1'] for i in items) / (2 * len(items))
    tol = RT.SIGHT['drawn']['plane_tol_mm']
    if not g0 - tol <= f <= g1 + tol:
        bad.append(f'Absehen bei f {f:.2f} nicht in der Glasebene {g0:.2f}–{g1:.2f} (± {tol} mm)')
    h = RT.hip(wtype)
    d = f - anchors['Socket_Eye']['at'][0]
    us = [pt[1] for i in items for pt in i['pts']]
    xs = [pt[0] for i in items for pt in i['pts']]
    ext = max(max(us) - min(us), max(xs) - min(xs))
    Hh = 2 * d * TAN * 9 / 16
    share = ext / Hh
    # Mindestlinie geht vor der Hüftgröße (0.25, Caret des Scharfschützen 1 % H): Zuwachs durch die auf min_line_px geklemmte Linie zulassen
    lw_nom = RT.LINE_R * RT.WEIGHTS[RT.HIP['weight']][1] * h['share_h'] * Hh / h['extent_mm']
    grow = 2 * max(0.0, RT.SIGHT['drawn']['min_line_px'] / 2 * 2 * d * TAN / RT.SIGHT['drawn']['ref_w_px'] - lw_nom) / Hh
    if q.get('drawn', {}).get('kind') != h['kind'] or abs(share - h['share_h']) > 0.03 * h['share_h'] + grow + 1e-9:
        bad.append(f"Absehen {q.get('drawn', {}).get('kind')} {share * 100:.2f} % H statt Hüftform {h['kind']} {h['share_h'] * 100:.1f} % H")
    px = 2 * d * TAN / RT.SIGHT['drawn']['ref_w_px']
    thin = min(math.dist(i['pts'][0], i['pts'][1]) for i in items if len(i['pts']) == 4)   # Linie: quer, Ring: radial
    if thin < RT.SIGHT['drawn']['min_line_px'] * px - 1e-6:
        bad.append(f"Linie {thin / px:.2f} px < {RT.SIGHT['drawn']['min_line_px']} px")
    return bad


IRON_GAP_MIN_DEG = 0.25     # Lichtspalt je Seite zwischen Korn und Kerbe, mindestens ≈ 4 px bei 1280 px Bildbreite (75°)


def iron_picture(parts, anchors):
    """Zielbild über Kimme und Korn (K1, 0.24) im Augenpunkt: Winkel in Grad (Kerbe halb, Korn halb, Lichtspalt je Seite, Kornpunkt,
    Kerbengrund, Blattoberkante; u nach oben positiv) und Abstände Auge–Kimme, Auge–Korn in mm."""
    P = {p['id']: p for p in parts}
    eye_f, cu = anchors['Socket_Eye']['at'][0], anchors['Socket_Eye']['at'][1]
    rear, front, dot = P['sight_rear'], P['sight_front'], P['sight_glass']
    if rear['shape'] == 'xprof':        # K2 „Hörner“ (0.25): Kimme als U-Querprofil um die Visierlinie, Kerbe = Lücke bei u 0
        fr, pts = rear['f0'], rear['pts']
        edges = list(zip(pts, pts[1:] + pts[:1]))
        xs = [a[0] + (b[0] - a[0]) * (0 - a[1]) / (b[1] - a[1]) for a, b in edges if (a[1] - 0) * (b[1] - 0) < 0]
        floor = max(a[1] + (b[1] - a[1]) * (0 - a[0]) / (b[0] - a[0]) for a, b in edges if a[0] * b[0] < 0 and
                    a[1] + (b[1] - a[1]) * (0 - a[0]) / (b[0] - a[0]) < 0)
        notch_w, floor_u, top_u = 2 * min(abs(x) for x in xs), floor, max(q[1] for q in pts)
    else:                               # K1 „Klammer“: Blatt als Seitenprofil mit Kerbe als Schnitt
        fr = min(q[0] for q in rear['pts'])
        notch = rear['cuts'][0]
        notch_w, floor_u, top_u = notch['w'], notch['u0'] - cu, max(q[1] for q in rear['pts']) - cu
    post = front['items'][0]
    ff = max(q[0] for q in post['pts'] if q[1] == max(v[1] for v in post['pts']))
    dr, df = fr - eye_f, (dot['a0'] + dot['a1']) / 2 - eye_f
    deg = math.degrees
    notch_half, post_half = deg(math.atan(notch_w / 2 / dr)), deg(math.atan(post['w'] / 2 / (ff - eye_f)))
    return dict(eye_rear=dr, eye_front=df, notch_half=notch_half, post_half=post_half, gap=notch_half - post_half,
                dot=deg(math.atan((dot['c'][0] - cu) / df)), notch_floor=deg(math.atan(floor_u / dr)),
                blade_top=deg(math.atan(top_u / dr)))


def check_iron(W):
    """Kimme/Korn einer Familienwaffe (Visier-Standard 3, Erweiterung 0.21; gebaut 0.24): Fehlerliste."""
    from basic.pilot.optics.sight_kit import IRON_EYE_MM
    bad, e, t = [], W.ANCHORS['Socket_Eye'], W.META['type']
    if t not in RT.SIGHT['line_exempt']['iron'] or RT.SIGHT_KIND.get(t) != 'irons_brackets':
        bad.append(f'Kimme/Korn passt nicht zur Klasse {t} (Visier-Standard 3: {RT.SIGHT_KIND.get(t)})')
    want = RT.SIGHT['rail_line_mm']['iron']
    if e.get('deck') is None or abs(e['at'][1] - e['deck'] - want) > 1e-6:
        bad.append(f"Visierlinie u {e['at'][1]} statt Träger {e.get('deck')} + {want:g} mm")
    P = {p['id']: p for p in W.PARTS}
    for pid in ('sight_mount', 'sight_front'):          # Kimmenfuß und Kornfuß liegen auf dem Träger auf (nichts schwebt)
        low = min(i['u0'] if 'u0' in i else min(q[1] for q in i['pts']) for i in P[pid]['items'])
        if e.get('deck') is not None and low > e['deck'] + 1e-6:
            bad.append(f"{pid} beginnt bei u {low:g} über dem Träger {e['deck']:g} (schwebt)")
    g = iron_picture(W.PARTS, W.ANCHORS)
    if abs(g['eye_rear'] - IRON_EYE_MM) > 0.5:
        bad.append(f"Augenpunkt {g['eye_rear']:.1f} mm statt {IRON_EYE_MM:.0f} mm hinter der Kimme")
    if g['gap'] < IRON_GAP_MIN_DEG:
        bad.append(f"Lichtspalt {g['gap']:.2f}° je Seite < {IRON_GAP_MIN_DEG}° (Korn füllt die Kerbe)")
    if not g['notch_floor'] < g['dot'] < g['blade_top']:
        bad.append(f"Kornpunkt bei {g['dot']:.2f}° nicht in der Kerbe ({g['notch_floor']:.2f}° … {g['blade_top']:.2f}°)")
    return bad


def check_fullscreen(W):
    """Scharfschützen-Zielfernrohr Z3 (Visier-Standard 3 Typ `fullscreen`, 0.25): Klasse passt, Visierhöhe 66 ± 4 mm, Augenpunkt 90 mm
    hinter dem Objektivring (Sitz wie Z1), Ring ohne Wulst, gezeichnetes Hüft-Absehen auf der Linse; Vollbild-Zielbild: Linse und
    Augenpunkt auf der Visierlinie, Kreis im Destiny-Band, Duplex mit Lücke um die Mitte. Fehlerliste."""
    from basic.pilot.optics.sight_kit import FULLSCREEN
    bad, e, t = [], W.ANCHORS['Socket_Eye'], W.META['type']
    if RT.SIGHT_KIND.get(t) != 'fullscreen' or RT.SIGHT['types']['fullscreen']['ads_view'] != 'overlay':
        bad.append(f'Vollbild passt nicht zur Klasse {t} (Visier-Standard 3: {RT.SIGHT_KIND.get(t)})')
    h = e['at'][1] - W.BORE
    if abs(h - RT.SIGHT['height_mm']) > RT.SIGHT['height_tol_mm']:
        bad.append(f"Visierhöhe {h:.1f} mm außerhalb {RT.SIGHT['height_mm']:.0f} ± {RT.SIGHT['height_tol_mm']:.0f} mm")
    rel = W.ANCHORS['Socket_Objective']['at'][0] - e['at'][0]
    if abs(rel - RT.SIGHT['types']['scope']['eye_relief_mm']) > 0.5:
        bad.append(f"Augenpunkt {rel:.1f} mm statt {RT.SIGHT['types']['scope']['eye_relief_mm']:.0f} mm hinter dem Objektivring")
    if abs(ring_ratio(W.PARTS) - C.RING_RATIO) > 0.02:
        bad.append(f'Ring außen/innen {ring_ratio(W.PARTS):.3f} statt ≈ {C.RING_RATIO} (Wulst)')
    P = {p['id']: p for p in W.PARTS}
    g = P['scope_glass']
    if abs(g['c'][0] - e['at'][1]) > 1e-6 or abs(g['c'][1]) > 1e-6 or abs(e['at'][2] if len(e['at']) > 2 else 0) > 1e-6:
        bad.append('Vollbild: Objektivlinse und Augenpunkt nicht auf derselben Visierlinie (Bildmitte ≠ Zielpunkt)')
    lo, hi = FULLSCREEN['band']
    D = FULLSCREEN['duplex']
    if not lo <= FULLSCREEN['circle_h'] <= hi or not D['line_h'] < D['bar_h'] < D['gap_h'] < FULLSCREEN['circle_h'] / 2:
        bad.append(f"Vollbild: Kreis {FULLSCREEN['circle_h']:.2f} H außerhalb {lo:.2f}–{hi:.2f} oder Duplex ohne freie Mitte")
    bad += check_reticle(W.PARTS, W.ANCHORS, t)
    return bad


BUILT = {   # gebaute Visiere des Baukastens: (Bau mit Größe, Visiertyp, Waffentyp der Hüftform, Größen)
    'H0 Referenz': (lambda s: C.reflex_sight_v21(-6, 143), 'reflex', 'auto_rifle', ('M',)),
    'H2 Pille': (lambda s: C.holo_pille(-6, 143, s), 'reflex', 'submachine_gun', ('S', 'M', 'L')),
    'H4 Kasten': (lambda s: C.holo_kasten(-6, 143, s), 'reflex', 'pulse_rifle', ('S', 'M', 'L')),
    'Z1 Tropfen': (lambda s: C.scope_tropfen(72, 143, 169, s), 'scope', 'scout_rifle', ('S', 'M', 'L')),
    # 0.26 „Kindle“: F1 an BASIC-10, Z2 an BASIC-11 (sight_kit; Umzug nach common.py mit dem Ego-Übertrag)
    'F1 Bögen': (lambda s: _kit().boegen(-6, 143, s), 'reflex', 'fusion_rifle', ('S', 'M', 'L')),
    'Z2 Gabel': (lambda s: _kit().gabel(72, 143, 169, s), 'scope', 'linear_fusion_rifle', ('S', 'M', 'L')),
    # 0.27 „Tracer“: H3 an BASIC-12, H6 an BASIC-15 in Größe L (M läge mit 21,8 % über dem Holo-Band und ist keine zugelassene Größe)
    'H3 Zinken': (lambda s: _kit().zinken(-6, 143, s), 'reflex', 'trace_rifle', ('S', 'M', 'L')),
    'H6 Achteck': (lambda s: _kit().achteck(-6, 143, s), 'reflex', 'machine_gun', ('S', 'L')),
}


def _kit():
    from basic.pilot.optics import sight_kit
    return sight_kit


def _radii(p):
    rs = [math.hypot(x, u) for x, u in p['pts']]
    return min(rs), max(rs)


KIT_PARTS = {   # Pflichtteile der Merkmale je Visier-ID (0.26): F1 Bögen, Z2 Gabel; 0.27: H3 Zinken, H6 Achteck
    'F1': ('sight_frame', 'sight_frame_b', 'sight_web', 'sight_web_r', 'sight_glass', 'sight_base'),
    'Z2': ('scope_rim', 'scope_fork', 'scope_tabs', 'scope_tabs_r', 'scope_mount_f'),
    'H3': ('sight_frame', 'sight_frame_r', 'sight_status', 'sight_glass', 'sight_base'),
    'H6': ('sight_frame', 'sight_frame_trim', 'sight_facet_0', 'sight_facet_1', 'sight_facet_2', 'sight_facet_3', 'sight_glass',
           'sight_base'),
}
# Teile, an denen ein Visier ohne ausdrückliche ID erkannt wird (nur Merkmalsteile, die kein anderes Visier der Familie trägt)
KIT_MARKERS = {'F1': ('sight_frame_b', 'sight_web', 'sight_web_r'), 'Z2': ('scope_fork', 'scope_tabs', 'scope_tabs_r'),
               'H3': ('sight_frame_r',), 'H6': ('sight_facet_0', 'sight_facet_1', 'sight_facet_2', 'sight_facet_3')}
ZINKEN_TOL_DEG = 0.5      # Neigung der Zinken 15° ± 0,5°
DIAG_TOL_DEG = 0.5        # Achteck: Fasen 45° ± 0,5°


def check_kit_form(parts, anchors, sight_id=None):
    """Merkmale von F1 und Z2 (0.26) am Entwurf: F1 – unterer Bogen 3 mm weiter außen (S-Öffnung), Stege in beiden Lücken, Glas hinter
    dem oberen Bogen, unterer Bogen sitzt im Sockel; Z2 – Gabel 3 mm außerhalb des Rings, Laschen an beiden Seiten, Gabel ruht auf dem
    Klemmfuß (nichts schwebt). sight_id ('F1'/'Z2') kommt vom Aufrufer (Baukasten-Name, Modulfeld SIGHT_ID); ohne Angabe gilt ein
    Visier als F1/Z2, sobald eines seiner Pflichtteile außer Ring, Glas und Sockel da ist. Fehlerliste (leer ohne F1/Z2)."""
    P = {p['id']: p for p in parts}
    ids = [sight_id] if sight_id else [k for k, mark in KIT_MARKERS.items() if any(r in P for r in mark)]
    bad = []
    for k in ids:
        missing = [r for r in KIT_PARTS.get(k, ()) if r not in P]
        if missing:
            bad.append(f'{k}: Pflichtteile fehlen: {", ".join(missing)}')
    if bad:
        return bad
    if 'F1' in ids:
        (ti, _), (bi, bo) = _radii(P['sight_frame']), _radii(P['sight_frame_b'])
        gx = max(math.hypot(x, u) for x, u in P['sight_glass']['pts'])      # Glasrand als Radius wie die Bögen (Richter Runde 5)
        cu = P['sight_frame']['cu']
        if abs(bi - ti - 3.0) > 0.05:
            bad.append(f'F1: Radiusversatz der Bögen {bi - ti:.2f} mm statt 3 (S-Öffnung)')
        if not ti < gx < bi:
            bad.append(f'F1: Glasrand r {gx:.2f} nicht zwischen den Bögen ({ti:.2f}–{bi:.2f})')
        if P['sight_base']['pts'][2][1] < cu - bo - 1e-6 or P['sight_base']['pts'][2][1] > cu - bi:
            bad.append('F1: unterer Bogen sitzt nicht auf dem Sockel (schwebt oder steht darüber)')
        for wid, mid in (('sight_web', 0.0), ('sight_web_r', 180.0)):   # Stege in den Lücken auf 3 bzw. 9 Uhr (± 12,5°), zwischen den Bögen
            for x, u in P[wid]['pts']:
                a = (math.degrees(math.atan2(u, x)) - mid + 180) % 360 - 180
                if abs(a) > 12.5 + 1e-6 or not ti - 1e-6 <= math.hypot(x, u) <= bo + 1e-6:
                    bad.append(f'F1: Steg {wid} liegt nicht in der Lücke ({a:+.1f}° neben {mid:.0f}°, r {math.hypot(x, u):.2f})')
                    break
    if 'Z2' in ids:
        rim = P['scope_rim']
        ro = rim.get('r1', rim['r'])
        g0, g1 = _radii(P['scope_fork'])
        foot = max(i['u1'] for i in P['scope_mount_f']['items'])
        cu = P['scope_fork']['cu']
        if abs(g0 - ro - 3.0) > 0.1:
            bad.append(f'Z2: Gabel {g0 - ro:.2f} mm vom Ring statt 3 mm')
        support = foot if 'scope_keel' not in P else max(q[1] for q in P['scope_keel']['pts']) + cu
        if support < cu - g1 - 1e-6:
            bad.append(f'Z2: Gabel schwebt {cu - g1 - support:.2f} mm über dem Klemmfuß')
    if 'H3' in ids:
        bad += _check_zinken(P)
    if 'H6' in ids:
        bad += _check_achteck(P)
    return bad


def _base_top(P):
    """Oberkante (u) und Breite des Haubensockels der H0-Plattform (common.sight_platform: pts[2] = vorn oben)."""
    b = P['sight_base']
    return b['pts'][2][1], b['w']


def _check_zinken(P):
    """H3 „Zinken“ (0.27): Platten 15° nach außen und spiegelgleich, oben offen (kein Teil quer über dem Glas), Platten sitzen auf dem
    Sockel, Glas zwischen den Platten und nicht über ihnen, Emitterpunkt mittig auf der Sockelrückseite unter dem Fenster (zum Auge)."""
    bad = []
    L, R, g = P['sight_frame'], P['sight_frame_r'], P['sight_glass']
    cu = L['cu']
    for pid in ('sight_frame', 'sight_frame_r'):
        pts = P[pid]['pts']
        if not (all(x > 0 for x, _ in pts) or all(x < 0 for x, _ in pts)):
            bad.append(f'H3: {pid} kreuzt die Mitte (Platte statt Haube)')
            return bad
    pts = L['pts']
    u_lo, u_hi = min(q[1] for q in pts), max(q[1] for q in pts)
    lo = min((q for q in pts if q[1] == u_lo), key=lambda q: abs(q[0]))            # Innenkante unten
    hi = min((q for q in pts if q[1] > (u_lo + u_hi) / 2), key=lambda q: abs(q[0]))   # Innenkante oben
    ang = math.degrees(math.atan2(abs(hi[0]) - abs(lo[0]), hi[1] - lo[1]))
    if abs(ang - _kit().ZINKEN_DEG) > ZINKEN_TOL_DEG:
        bad.append(f'H3: Zinken {ang:+.1f}° statt {_kit().ZINKEN_DEG:.0f}° nach außen geneigt')
    if sorted((-x, u) for x, u in R['pts']) != sorted(pts) and \
            any(abs(a[0] + b[0]) > 1e-6 or abs(a[1] - b[1]) > 1e-6 for a, b in zip(sorted((-x, u) for x, u in R['pts']), sorted(pts))):
        bad.append('H3: rechte Zinke ist nicht das Spiegelbild der linken')
    gu = max(q[1] for q in g['pts'])
    for p in P.values():                     # oben offen: kein Querprofil über die Mitte oberhalb des Glases
        if p.get('shape') == 'xprof' and p['id'] not in ('sight_glass', 'sight_reticle') and p['id'].startswith('sight') \
                and min(q[0] for q in p['pts']) < -1 and max(q[0] for q in p['pts']) > 1 and max(q[1] for q in p['pts']) > gu + 0.5:
            bad.append(f"H3: {p['id']} schließt die Zinken oben (Dach)")
    bt, bw = _base_top(P)
    if not bt - 1.0 - 1e-6 <= cu + u_lo <= bt + 1e-6 or max(abs(q[0]) for q in pts if q[1] == u_lo) > bw / 2 + 1e-6:
        bad.append(f'H3: Zinken sitzen nicht auf dem Sockel (unten u {cu + u_lo:.2f}, Sockel u {bt:.2f}, Breite {bw:g})')
    tg = math.tan(math.radians(ang))
    for x, u in g['pts']:
        if abs(x) > abs(lo[0]) + tg * (u - lo[1]) + 1e-6 or u > u_hi:
            bad.append(f'H3: Glaspunkt ({x:.2f}, {u:.2f}) liegt außerhalb der Zinken')
            break
    pip = P['sight_status']
    b = P['sight_base']['pts']
    fr = b[0][0] + (b[3][0] - b[0][0]) * (pip['c'][0] - b[0][1]) / (b[3][1] - b[0][1])   # Sockelrückseite in Höhe des Punkts
    if pip['mat'] != 'energy' or abs(pip['c'][1]) > 1e-6 or not pip['c'][0] < bt or not pip['a0'] - 1e-6 <= fr <= pip['a1'] + 1e-6:
        bad.append(f"H3: Emitterpunkt nicht mittig in der Sockelrückseite unter dem Fenster (f {pip['a0']:.1f}–{pip['a1']:.1f}, "
                   f"Rückseite f {fr:.1f}, u {pip['c'][0]:.1f})")
    return bad


def _diag_k(pts):
    """Fasen eines Achtecks: {(sx, su): Abstand der Fasenlinie vom Mittelpunkt}; None, wenn eine Kante weder achsparallel noch 45° ist."""
    k = {}
    for a, b in zip(pts, pts[1:] + pts[:1]):
        d = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 90
        if min(d, 90 - d) < DIAG_TOL_DEG:
            continue
        if abs(d - 45) > DIAG_TOL_DEG:
            return None
        sx, su = (1 if a[0] + b[0] > 0 else -1), (1 if a[1] + b[1] > 0 else -1)
        k[(sx, su)] = (sx * (a[0] + b[0]) / 2 + su * (a[1] + b[1]) / 2) / math.sqrt(2)
    return k


def _check_achteck(P):
    """H6 „Achteck“ (0.27): Haube innen und außen Achtecke mit vier 45°-Fasen, Stirn 1,6 mm ringsum (auch über den Fasen), je Fase
    eine blanke Fasenfläche außen auf der Haube, Glas in der Innenkontur, Haube sitzt im Sockel (nichts schwebt), Sockel so breit wie
    die untere Achteckseite."""
    from basic.common import SIGHT_T
    bad = []
    hood, g = P['sight_frame'], P['sight_glass']
    outer, inner = hood['pts'], hood['cuts'][0]['pts']
    ko, ki = _diag_k(outer), _diag_k(inner)
    if ko is None or ki is None or len(ko) != 4 or len(ki) != 4:
        return ['H6: Haube ist kein Achteck mit vier 45°-Fasen']
    for q in ko:
        if abs(ko[q] - ki[q] - SIGHT_T) > 0.05:
            bad.append(f'H6: Stirn über der Fase {q} {ko[q] - ki[q]:.2f} mm statt {SIGHT_T}')
    if abs(max(x for x, _ in outer) - max(x for x, _ in inner) - SIGHT_T) > 0.05 or \
            abs(max(u for _, u in outer) - max(u for _, u in inner) - SIGHT_T) > 0.05:
        bad.append(f'H6: Stirn an den Seiten nicht {SIGHT_T} mm')
    mids = {}                               # Mitte jeder Außenfase
    for a, b in zip(outer, outer[1:] + outer[:1]):
        if abs(a[0] - b[0]) > 1e-6 and abs(a[1] - b[1]) > 1e-6:
            mids[(1 if a[0] + b[0] > 0 else -1, 1 if a[1] + b[1] > 0 else -1)] = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    seen = set()
    for i in range(4):                       # je Fase genau eine Fläche, mittig auf der Außenfase (± 0,5 mm)
        f = P[f'sight_facet_{i}']
        cx, cu_ = sum(x for x, _ in f['pts']) / len(f['pts']), sum(u for _, u in f['pts']) / len(f['pts'])
        q = (1 if cx > 0 else -1, 1 if cu_ > 0 else -1)
        d = math.dist((cx, cu_), mids[q])
        if q in seen or d > 0.5:
            bad.append(f'H6: Fasenfläche {i} liegt nicht mittig auf einer eigenen Außenfase ({d:.2f} mm daneben)')
        seen.add(q)
    xs, us = [x for x, _ in inner], [u for _, u in inner]
    if any(not min(xs) - 1e-6 <= x <= max(xs) + 1e-6 or not min(us) - 1e-6 <= u <= max(us) + 1e-6 for x, u in g['pts']):
        bad.append('H6: Glas steht über die Innenkontur der Haube')
    bt, bw = _base_top(P)
    cu = hood['cu']
    if not cu + min(u for _, u in outer) - 1e-6 <= bt <= cu + min(us) + 1e-6:
        bad.append(f'H6: Haube sitzt nicht im Sockel (Sockel u {bt:.2f}, Haube unten u {cu + min(u for _, u in outer):.2f})')
    flat = [abs(a[0] - b[0]) for a, b in zip(outer, outer[1:] + outer[:1]) if abs(a[1] - b[1]) < 1e-6 and a[1] < 0]
    if not flat or abs(bw - flat[0]) > 0.5:
        bad.append(f'H6: Sockel {bw:.1f} mm breit statt der unteren Achteckseite {flat[0] if flat else 0:.1f} mm')
    return bad


def main():
    bad, n = [], 0
    for name, (build, typ, wtype, sizes) in BUILT.items():
        for s in sizes:
            P, A = build(s)
            sh = opening_share(P, A)
            lo, hi, band = RT.share_band(typ, None, s)
            n += 1
            print(f'[test_sights] {name} {s}: Öffnung {sh * 100:.1f} % ({band} {lo * 100:.0f}–{hi * 100:.0f} %)')
            if not lo - 1e-9 <= sh <= hi + 1e-9 or (s == 'M' and band != 'Standard'):
                bad.append(f'{name} {s}: Öffnung im Zielen {sh * 100:.1f} % außerhalb {band} {lo * 100:.0f}–{hi * 100:.0f} %')
            if typ == 'scope' and abs(ring_ratio(P) - C.RING_RATIO) > 0.02:
                bad.append(f'{name} {s}: Ring außen/innen {ring_ratio(P):.3f} statt ≈ {C.RING_RATIO}')
            bad += [f'{name} {s}: {b}' for b in check_reticle(P, A, wtype)]
            bad += [f'{name} {s}: {b}' for b in check_kit_form(P, A, name.split()[0] if name.split()[0] in KIT_PARTS else None)]
    for f in sorted(glob.glob(os.path.join(ROOT, 'basic', 'pilot', 'w*_v21.py'))):
        W = importlib.import_module('basic.pilot.' + os.path.basename(f)[:-3])
        wid, e = f"{W.META['id']}-{W.META['variant']}", W.ANCHORS.get('Socket_Eye', {})
        if e.get('sight_type') == 'iron':
            g = iron_picture(W.PARTS, W.ANCHORS)
            n += 1
            print(f"[test_sights] {wid}: Kimme/Korn, Linie Träger + {e['at'][1] - e['deck']:g} mm, Auge {g['eye_rear']:.0f} mm hinter der "
                  f"Kimme, Kerbe ±{g['notch_half']:.2f}°, Korn ±{g['post_half']:.2f}°, Lichtspalt {g['gap']:.2f}°, Kornpunkt {g['dot']:.2f}°")
            bad += [f'{wid}: {b}' for b in check_iron(W)]
            continue
        if e.get('sight_type') == 'fullscreen':
            from basic.pilot.optics.sight_kit import FULLSCREEN
            n += 1
            print(f"[test_sights] {wid}: Vollbild (Z3), Visierhöhe {e['at'][1] - W.BORE:g} mm, Auge "
                  f"{W.ANCHORS['Socket_Objective']['at'][0] - e['at'][0]:g} mm hinter dem Ring, Ring {ring_ratio(W.PARTS):.3f}, "
                  f"Kreis {FULLSCREEN['circle_h'] * 100:.0f} % H")
            bad += [f'{wid}: {b}' for b in check_fullscreen(W)]
            continue
        if e.get('sight_type') not in ('reflex', 'scope'):
            continue
        sh = opening_share(W.PARTS, W.ANCHORS)
        lo, hi, band = RT.share_band(e['sight_type'], W.META['type'], getattr(W, 'SIGHT_SIZE', 'M'))
        n += 1
        print(f'[test_sights] {wid}: Öffnung {sh * 100:.1f} % ({band}), ' + (f'Ring {ring_ratio(W.PARTS):.3f}'
                                                                         if e['sight_type'] == 'scope' else 'Holo'))
        if not lo - 1e-9 <= sh <= hi + 1e-9:
            bad.append(f'{wid}: Öffnung im Zielen {sh * 100:.1f} % außerhalb {band} {lo * 100:.0f}–{hi * 100:.0f} %')
        if e['sight_type'] == 'scope' and abs(ring_ratio(W.PARTS) - C.RING_RATIO) > 0.02:
            bad.append(f'{wid}: Ring außen/innen {ring_ratio(W.PARTS):.3f} statt ≈ {C.RING_RATIO} (Wulst)')
        bad += [f'{wid}: {b}' for b in check_reticle(W.PARTS, W.ANCHORS, W.META['type'])]
        bad += [f'{wid}: {b}' for b in check_kit_form(W.PARTS, W.ANCHORS, getattr(W, 'SIGHT_ID', None))]
    # Mündungsfeuer im Zielen (5.3 A) bei Querprofil-Glas: nur innerhalb der Kontur gezählt (0.21, Richter) – die Pille misst weniger
    # als ihr umschließendes Rechteck und bleibt unter 20 %
    import types
    from basic.arms import ego as EG
    W = importlib.import_module('basic.pilot.w06_submachine_gun_v21')
    cov = EG.flash_cover_ads(W)
    g = next(p for p in W.PARTS if p['id'] == 'sight_glass')
    xs, us = [q[0] for q in g['pts']], [q[1] for q in g['pts']]
    box = dict(g, pts=[(min(xs), min(us)), (max(xs), min(us)), (max(xs), max(us)), (min(xs), max(us))])
    cov_box = EG.flash_cover_ads(types.SimpleNamespace(PARTS=[box if p is g else p for p in W.PARTS], ANCHORS=W.ANCHORS))
    n += 1
    print(f'[test_sights] BASIC-06-v2.1: Mündungsfeuer im Zielen {cov * 100:.1f} % der Pillenkontur (Rechteck {cov_box * 100:.1f} %)')
    if cov > 0.20 or not cov < cov_box:
        bad.append(f'BASIC-06-v2.1: Mündungsfeuer {cov * 100:.1f} % (Kontur) / {cov_box * 100:.1f} % (Rechteck) – Kontur nicht gezählt oder > 20 %')
    # H4 (BASIC-02): die vordere Haubenöffnung zählt als zweite Kontur – weniger oder gleich viele Punkte als nur mit dem Glas
    W2 = importlib.import_module('basic.pilot.w02_pulse_rifle_v21')
    cov2 = EG.flash_cover_ads(W2)
    cov2_glass = EG.flash_cover_ads(types.SimpleNamespace(PARTS=[p for p in W2.PARTS if p['id'] != 'sight_frame_trim'], ANCHORS=W2.ANCHORS))
    n += 1
    print(f'[test_sights] BASIC-02-v2.1: Mündungsfeuer im Zielen {cov2 * 100:.1f} % (Glas und Haubenöffnung; nur Glas {cov2_glass * 100:.1f} %)')
    if cov2 > 0.20 or abs(cov2 - cov2_glass) < 1e-9 and cov2 > 0:
        bad.append(f'BASIC-02-v2.1: Mündungsfeuer {cov2 * 100:.1f} % – Haubenöffnung nicht als Kontur gezählt oder > 20 %')
    # Bauteil-Hash des Exports plattformfest (0.21, CI unter Linux): Werte mit 1 ulp Abstand (libm-Unterschied bei cos/sin) ergeben
    # denselben Hash, eine echte Maßänderung von 0,01 mm einen anderen
    from tools.export_unity import parts_sha
    x = 23.799999999999997

    def H(v):
        return parts_sha(types.SimpleNamespace(PARTS=[dict(id='p', pts=[(v, -0.0), (math.cos(0.3), 1.0)])], ASSEMBLIES=[]))
    n += 1
    if H(x) != H(math.nextafter(x, math.inf)) or H(x) != H(math.nextafter(x, -math.inf)) or H(x) == H(x + 0.01):
        bad.append('export_unity.parts_sha: 1 ulp Abweichung ändert den Hash oder 0,01 mm nicht (plattformabhängig)')
    from basic.pilot.optics import sight_kit as K
    for kid, kind in (('iron_klammer', 'iron'), ('iron_hoerner', 'iron'), ('mini_reflex', 'mini_reflex')):
        for s in ('S', 'M', 'L'):
            W = K.weapon(kid, s)
            want = K.DECK + RT.SIGHT['rail_line_mm'][kind]
            n += 1
            if abs(W.ANCHORS['Socket_Eye']['at'][1] - want) > 1e-6:
                bad.append(f"{kid} {s}: Visierlinie u {W.ANCHORS['Socket_Eye']['at'][1]} statt Schiene + {RT.SIGHT['rail_line_mm'][kind]:g}")
    print(f'[test_sights] {n} Visiere geprüft')
    for b in bad:
        print('[test_sights] FEHLER', b)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
