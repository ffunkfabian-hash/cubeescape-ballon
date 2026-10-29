"""Prüft den Visier-Baukasten v3 ohne Blender (0.21 „Ironsight“, Visier-Standard 3 mit Erweiterung, docs/visier-konzept.md):

  python3 tools/test_sights.py            (läuft in ./check)

- Öffnung im Zielen: lichte Öffnung (Glasbreite bzw. Objektivlinse) als Anteil der Bildbreite bei 75°, gemessen im echten Abstand
  zum Augenpunkt. Gebaute Visiere (common: H0, H2, H4, Z1) in M im Standard, in S/L im Standard oder in der zugelassenen Variante
  (`reticles.share_band`); Familienwaffen im Standard oder in der Variante ihres Typs.
- Ring ohne Wulst: Zielfernrohre außen/innen an der Ringstirn ≈ 1,29 (± 0,02), Innenfläche läuft auf den Augenpunkt zu.
- Absehen gezeichnet: `sight_reticle` flach (Querprofile ≤ 0,1 mm) in der Glasebene (± 0,5 mm), reine Emission, Hüftform der
  Klasse in Hüftgröße (± 3 %, dazu der Zuwachs, wenn die Linie auf die Mindestbreite geklemmt ist – 0.25, Caret 1 % H), Linien
  mindestens 1,6 px bei 1280 px Bildbreite.
- Holo an Familienwaffen (0.28): Klemmfuß liegt auf einer Schiene BRI-22 und innerhalb ihrer Länge (Sitz).
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
    ex = anchors['Socket_Eye']['at'][2] if len(anchors['Socket_Eye']['at']) > 2 else 0
    if any(abs(i.get('cx', 0) - ex) > 0.1 for i in items):     # 0.28: auch beim seitlichen Visier mittig auf der Visierlinie
        bad.append(f'Absehen nicht auf der Visierlinie (x {items[0].get("cx", 0):.1f} statt Auge x {ex:.1f})')
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


FOOT_GAP = min(i['u0'] for i in C.sight_platform(0, 0, 10, 20)[0]['items'])   # Klemmfuß über der Schiene (common.sight_platform)


def check_reflex_seat(W):
    """Sitz eines Holo/Reflex-Visiers an der Waffe (0.28): der Klemmfuß der H0-Plattform liegt auf einer Schiene BRI-22 (Unterkante
    0,5 mm über der Schienenoberkante wie common.sight_platform, ± 0,1), ganz innerhalb ihrer Länge und mittig auf ihr (± 0,5 mm,
    auch seitlich versetzt). Fehlerliste."""
    P = {p['id']: p for p in W.PARTS}
    m = P.get('sight_mount')
    if not m or m.get('shape') != 'multi':
        return ['Holo ohne Klemmfuß der H0-Plattform (sight_mount)']
    foot = min(m['items'], key=lambda i: i['u0'])                        # unterste Stufe = Klemmfuß
    for r in (p for p in W.PARTS if p.get('iface') == 'BRI-22' and p['id'] != 'sight_mount' and 'u1' in p):
        if abs(foot['u0'] - FOOT_GAP - r['u1']) <= 0.1 and r['f0'] - 1e-6 <= foot['f0'] and foot['f1'] <= r['f1'] + 1e-6 \
                and abs(foot.get('x', 0) - r.get('x', 0)) <= 0.5:
            return []
    return [f"Klemmfuß (f {foot['f0']:g}–{foot['f1']:g}, u {foot['u0']:g}) liegt auf keiner Schiene BRI-22"]


PINS_PARTS = ('sight_mount', 'sight_base', 'sight_frame', 'sight_frame_trim', 'sight_pin_rail', 'sight_pin', 'sight_pin_1',
              'sight_pin_2', 'sight_pin_blade_0', 'sight_pin_blade_1', 'sight_pin_blade_2')


def pins_picture(parts, anchors):
    """Zielbild durch das Pinvisier B1 (0.29) im Augenpunkt: Abstand Auge–Pins, lichter Ring (Anteil der Bildbreite), je Pin
    Mittelpunkt (u relativ zur Visierlinie, Winkel unter der Bildmitte) und Kopfdurchmesser in px bei 1280 px Bildbreite."""
    P = {p['id']: p for p in parts}
    eye = anchors['Socket_Eye']['at']
    fr = P['sight_frame']
    d = (P['sight_pin']['a0'] + P['sight_pin']['a1']) / 2 - eye[0]
    xs = [q[0] for q in fr['cuts'][0]['pts']]
    r = max(xs)                                           # links runder Ring: lichter Radius (rechts die Abflachung)
    px = 2 * d * TAN / RT.SIGHT['drawn']['ref_w_px']
    heads = [P[k] for k in ('sight_pin', 'sight_pin_1', 'sight_pin_2')]
    pins = [dict(du=h['c'][0] - fr['cu'], x=h['c'][1] - fr.get('cx', 0.0), rd=h['r'], deg=math.degrees(math.atan((fr['cu'] - h['c'][0]) / d)),
                 px=2 * h['r'] / px) for h in heads]
    return dict(dist=d, r=r, cap=-min(xs), share=2 * r / (2 * d * TAN), pins=pins, cx=fr.get('cx', 0.0))


def check_pins(W):
    """Pinvisier B1 an einer Familienwaffe (Bogen, 0.29): Fehlerliste. Pflichtteile; Klasse; Visierlinie Schiene + r + 12 und
    Visierhöhe 66 ± 4 über dem Pfeil; Augenpunkt am Ankerpunkt (hinter dem Nockpunkt bei vollem Auszug, höchstens 40 mm); oberster
    Pinkopf in der Bildmitte; Pin-Abstände (gleiche Stufen, ≥ pin_gap_min_deg) und Köpfe (≥ pin_head_min_px, nach unten kleiner,
    ganz im Ring); Sichtfeld: lichter Ring im Band, Pins nur von rechts (linke Ringhälfte frei), Fensterbogen des Mittelstücks
    verdeckt den Ring nicht."""
    from basic.pilot.optics.sight_kit import PINS_LINE, PINS_T
    T = RT.SIGHT['types']['pins']
    bad, e, t = [], W.ANCHORS['Socket_Eye'], W.META['type']
    P = {p['id']: p for p in W.PARTS}
    miss = [k for k in PINS_PARTS if k not in P]
    if miss:
        return [f'B1: Pflichtteile fehlen: {", ".join(miss)}']
    if RT.SIGHT_KIND.get(t) != 'pins':
        bad.append(f'Pinvisier passt nicht zur Klasse {t} (Visier-Standard 3: {RT.SIGHT_KIND.get(t)})')
    g = pins_picture(W.PARTS, W.ANCHORS)
    cu = P['sight_frame']['cu']
    if e.get('deck') is None or abs(cu - e['deck'] - g['r'] - PINS_LINE) > 1e-6:
        bad.append(f"Visierlinie u {cu} statt Schiene {e.get('deck')} + r {g['r']:g} + {PINS_LINE:g} mm")
    ex = e['at'][2] if len(e['at']) > 2 else 0
    h = math.hypot(e['at'][1] - W.BORE, ex)          # seitliches Visier: Abstand zum Pfeil (wie 0.28), nur über dem Pfeil oder links
    if abs(h - RT.SIGHT['height_mm']) > RT.SIGHT['height_tol_mm']:
        bad.append(f"Visierhöhe {h:.1f} mm vom Pfeil außerhalb {RT.SIGHT['height_mm']:.0f} ± {RT.SIGHT['height_tol_mm']:.0f} mm")
    if e['at'][1] < W.BORE - RT.SIGHT['height_tol_mm'] or ex < -0.5:
        bad.append(f"Visierlinie unter dem Pfeil oder rechts daneben (u {e['at'][1]:.1f}, x {ex:.1f}; seitlich nur links)")
    full = W.ANCHORS.get('Socket_DrawFull', {}).get('at')
    if not full or not 0 <= full[0] - e['at'][0] <= 40:
        bad.append('Augenpunkt nicht am Ankerpunkt (0–40 mm hinter dem Nockpunkt bei vollem Auszug, Socket_DrawFull)')
    p0 = g['pins'][0]
    if abs(e['at'][1] - cu) > 1e-6 or abs(p0['du']) > 1e-6 or abs(p0['x']) > 1e-6 or abs(ex - g['cx']) > 1e-6:
        bad.append('oberster Pinkopf nicht in der Bildmitte (Augenpunkt, Ringmitte und Pin nicht auf einer Linie)')
    steps = [a['du'] - b['du'] for a, b in zip(g['pins'], g['pins'][1:])]
    if min(steps) <= 0 or max(steps) - min(steps) > 0.05:
        bad.append(f'Pins nicht in gleichen Stufen nach unten ({", ".join(f"{x:.2f}" for x in steps)} mm)')
    gaps = [b['deg'] - a['deg'] for a, b in zip(g['pins'], g['pins'][1:])]
    if min(gaps) < T['pin_gap_min_deg']:
        bad.append(f"Pinabstand {min(gaps):.2f}° < {T['pin_gap_min_deg']}° (Köpfe fließen zusammen)")
    heads = [q['px'] for q in g['pins']]
    if min(heads) < T['pin_head_min_px'] or any(a <= b for a, b in zip(heads, heads[1:])):
        bad.append(f"Pinköpfe {', '.join(f'{x:.1f}' for x in heads)} px: nicht ≥ {T['pin_head_min_px']} px oder nicht nach unten kleiner")
    for i, q in enumerate(g['pins']):
        if abs(q['du']) + q['rd'] > g['r'] - 1.0:
            bad.append(f'Pinkopf {i + 1} reicht an den Ring (Abstand < 1 mm)')
    lo, hi = T['target_share']
    if not lo <= g['share'] <= hi:
        bad.append(f"Sichtfeld: lichter Ring {g['share'] * 100:.1f} % außerhalb {lo * 100:.0f}–{hi * 100:.0f} %")
    for i in range(3):
        xs = [q[0] for q in P[f'sight_pin_blade_{i}']['pts']]
        if max(xs) > 0 or min(xs) > -(g['cap'] + PINS_T):
            bad.append(f'Pin {i + 1} nicht von der Pinschiene rechts zur Mitte (linke Ringhälfte muss frei bleiben)')
    if (PINS_T / g['r']) > T['frame_max'] + 1e-9:
        bad.append(f"Ringstirn {PINS_T:g} mm = {PINS_T / g['r']:.3f} × Öffnung > {T['frame_max']} (Rahmen zu dick)")
    win = getattr(W, 'WIN', None)
    if win:     # Fensterbogen: der Ring samt Stirn (r + T) muss im Sichtkegel frei bleiben – geprüft an der Vorderseite des
        # Fensterbogens (dort ist der Kegel am weitesten, Richter 0.29) mit den Kanten aus dem gebauten Profil
        rs = P['riser']
        rp = [q for q in rs['pts'] if win['u0'] <= q[1] <= win['u1']]
        d_front = max(q[0] for q in rp) - e['at'][0]
        need = (g['r'] + PINS_T) * d_front / g['dist']
        x_out = rs.get('x', 0.0) + rs['w'] / 2                                       # Außenkante des Fensterbogens
        cut = next(c for c in rs['cuts'] if c.get('u0') == win['u0'] and c.get('u1') == win['u1'])
        x_in = cut.get('x', 0.0) + cut['w'] / 2                                       # Innenkante = Rand des Fensterschnitts
        if ex >= x_out and x_out > ex - need - 1.0:      # Seitenvisier links vom Fensterbogen
            bad.append(f"Fensterbogen bis x {x_out:g} verdeckt den Ring (frei nur bis x {ex - need - 1.0:.2f})")
        elif ex < x_out and x_in < ex + need + 1.0:      # Ring über dem Pfeil, Fensterbogen links
            bad.append(f"Fensterbogen ab x {x_in:g} verdeckt den Ring (frei erst ab x {ex + need + 1.0:.2f})")
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
    # 0.28 „Breech“: W1 an BASIC-13, W2 an BASIC-14 (Größe M; L ist die Holo-L-Variante der Werfer)
    'W1 D-Linse': (lambda s: _kit().d_linse(-6, 143, s), 'reflex', 'grenade_launcher', ('S', 'M', 'L')),
    'W2 Entfernung': (lambda s: _kit().entfernung(-6, 143, s), 'reflex', 'rocket_launcher', ('S', 'M', 'L')),
    # 0.29 „Bowstring“: B1 an BASIC-07 v2.1 (Pins sind das Absehen, kein Glas; Öffnung = lichter Ring, Augenpunkt 680 mm wie am Bogen)
    'B1 Pins': (lambda s: _kit().pins(-6, 143, s), 'pins', 'combat_bow', ('S', 'M', 'L')),
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
    'W1': ('sight_frame', 'sight_frame_trim', 'sight_notch', 'sight_marks', 'sight_glass', 'sight_base'),     # 0.28
    'W2': ('sight_frame', 'sight_frame_trim', 'sight_roof', 'sight_range', 'sight_glass', 'sight_base'),
}
# Teile, an denen ein Visier ohne ausdrückliche ID erkannt wird (nur Merkmalsteile, die kein anderes Visier der Familie trägt)
KIT_MARKERS = {'F1': ('sight_frame_b', 'sight_web', 'sight_web_r'), 'Z2': ('scope_fork', 'scope_tabs', 'scope_tabs_r'),
               'H3': ('sight_frame_r',), 'H6': ('sight_facet_0', 'sight_facet_1', 'sight_facet_2', 'sight_facet_3'),
               'W1': ('sight_notch', 'sight_marks'), 'W2': ('sight_roof', 'sight_range')}
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
    if 'W1' in ids:
        bad += _check_dlinse(P)
    if 'W2' in ids:
        bad += _check_entfernung(P)
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


def _hood_seat(P, tag):
    """Haube sitzt im Sockel der H0-Plattform: Sockeloberkante zwischen Außen- und Innenunterkante der Haube (nichts schwebt)."""
    hood = P['sight_frame']
    outer, inner = hood['pts'], hood['cuts'][0]['pts']
    bt, _ = _base_top(P)
    cu = hood['cu']
    if not cu + min(u for _, u in outer) - 1e-6 <= bt <= cu + min(u for _, u in inner) + 1e-6:
        return [f'{tag}: Haube sitzt nicht im Sockel (Sockel u {bt:.2f}, Haube unten u {cu + min(u for _, u in outer):.2f})']
    return []


def _glass_inside(P, inside, tag):
    if any(not inside(x, u) for x, u in P['sight_glass']['pts']):
        return [f'{tag}: Glas steht über die Innenkontur der Haube']
    return []


def _check_dlinse(P):
    """W1 „D-Linse“ (0.28): Haube innen und außen ein D (Kreisbogen um die Visierlinie, oben gerade), Stirn 2,4 mm (Werfer) am Bogen und
    an der Geraden; orange Kerbmarke mittig auf der Geraden (sitzt auf); drei blanke Fallmarken links innen unter der Visierlinie,
    nach unten kürzer, jede an der Innenwand (weder schwebend noch in der Wand); Glas in der Innenkontur; Haube im Sockel, Sockel so breit
    wie die D-Unterseite in Sockelhöhe."""
    K = _kit()
    bad = []
    hood = P['sight_frame']
    cu = hood['cu']
    outer, inner = hood['pts'], hood['cuts'][0]['pts']

    def dfit(pts):                       # (Radius des Bogens, Höhe der Geraden) oder None, wenn kein D
        top = max(u for _, u in pts)
        arc = [math.hypot(x, u) for x, u in pts if u < top - 1e-6]
        flat = [x for x, u in pts if abs(u - top) < 1e-6]
        if len(flat) < 2 or max(flat) - min(flat) < 1.0 or not arc or max(arc) - min(arc) > 0.05 or top >= min(arc) - 1e-6:
            return None
        return sum(arc) / len(arc), top
    fo, fi = dfit(outer), dfit(inner)
    if fo is None or fi is None:
        return ['W1: Haube ist kein D (Bogen um die Visierlinie, oben gerade)']
    if abs(fo[0] - fi[0] - K.WERFER_T) > 0.05 or abs(fo[1] - fi[1] - K.WERFER_T) > 0.05:
        bad.append(f'W1: Stirn {fo[0] - fi[0]:.2f} (Bogen) / {fo[1] - fi[1]:.2f} mm (Gerade) statt {K.WERFER_T}')
    r, top = fi
    n = P['sight_notch']
    if n['mat'] != 'accent' or abs(n.get('x', 0.0)) > 0.1 or not n['u0'] <= cu + fo[1] + 1e-6 <= n['u0'] + 0.3:
        bad.append(f"W1: Kerbmarke nicht orange mittig auf der Geraden (u0 {n['u0']:.2f}, Gerade u {cu + fo[1]:.2f})")
    m = P['sight_marks']
    items = m['items']
    us = [(i['u0'] + i['u1']) / 2 - cu for i in items]
    ws = [i['w'] for i in items]
    if m['mat'] != 'trim' or len(items) != 3 or not all(du < 0 for du in us) or us != sorted(us, reverse=True) \
            or ws != sorted(ws, reverse=True) or len(set(ws)) != 3:
        bad.append('W1: Fallmarken nicht drei blanke Marken unter der Visierlinie, nach unten kürzer')
    for i, du in zip(items, us):
        xw = K.dlinse_wall_x(r, du)
        xi, xo = i.get('x', 0) - i['w'] / 2, i.get('x', 0) + i['w'] / 2
        if xi <= 0 or not xi < xw <= xo or xo - xw > 0.6:
            bad.append(f'W1: Fallmarke u {du:+.1f} sitzt nicht links innen an der Wand (x {xi:.2f}–{xo:.2f}, Wand {xw:.2f})')
    bad += _glass_inside(P, lambda x, u: u <= top + 1e-6 and math.hypot(x, u) <= r + 1e-6, 'W1')   # D: überall Bogen r, oben die Gerade
    bad += _hood_seat(P, 'W1')
    bt, bw = _base_top(P)
    chord = 2 * math.sqrt(max(fo[0] ** 2 - (bt - cu) ** 2, 0))
    if abs(bw - chord) > 0.5:
        bad.append(f'W1: Sockel {bw:.1f} mm breit statt der D-Unterseite in Sockelhöhe {chord:.1f} mm')
    return bad


def _check_entfernung(P):
    """W2 „Entfernung“ (0.28): Haube als Rundrechteck mit Stirn 2,4 mm an den Seiten und unten, oben 4 mm (Schutzdach); das Dach liegt
    auf der Haube, steht mindestens 4 mm vor ihre Stirn und nicht über ihre Breite; Entfernungsfeld leuchtend aus drei Ziffern und
    Einheit, mittig in der Sockelrückseite unter dem Fenster; Glas in der Innenkontur; Haube im Sockel."""
    K = _kit()
    bad = []
    hood = P['sight_frame']
    cu = hood['cu']
    outer, inner = hood['pts'], hood['cuts'][0]['pts']
    side = max(x for x, _ in outer) - max(x for x, _ in inner)
    low = min(u for _, u in inner) - min(u for _, u in outer)
    roof_t = max(u for _, u in outer) - max(u for _, u in inner)
    if abs(side - K.WERFER_T) > 0.05 or abs(low - K.WERFER_T) > 0.05 or abs(roof_t - K.ENTF_ROOF) > 0.05:
        bad.append(f'W2: Stirn Seite {side:.2f} / unten {low:.2f} / oben {roof_t:.2f} mm statt {K.WERFER_T} / {K.WERFER_T} / {K.ENTF_ROOF}')
    rf = P['sight_roof']
    hf1 = hood['f1']
    ru0, ru1 = min(u for _, u in rf['pts']), max(u for _, u in rf['pts'])
    if abs(ru1 - max(u for _, u in outer)) > 0.05 or ru0 < max(u for _, u in inner) - 1e-6 or rf['f1'] - hf1 < 4.0 - 1e-6 \
            or rf['f0'] > hf1 + 0.6 or max(abs(x) for x, _ in rf['pts']) > max(x for x, _ in outer) + 1e-6:
        bad.append(f"W2: Schutzdach liegt nicht auf der Haube oder steht nicht ≥ 4 mm vor (vor der Stirn {rf['f1'] - hf1:.1f} mm)")
    fld = P['sight_range']
    it = fld['items']
    b = P['sight_base']['pts']
    bt, bw = _base_top(P)
    xs = [i.get('x', 0) for i in it]
    off = []
    for i in it:
        uc = (i['u0'] + i['u1']) / 2
        fr = b[0][0] + (b[3][0] - b[0][0]) * (uc - b[0][1]) / (b[3][1] - b[0][1])
        off.append(abs((i['f0'] + i['f1']) / 2 - fr))
    if fld['mat'] != 'energy' or len(it) != 4 or max(off) > 0.6 or abs(sum(xs) / len(xs)) > 1.5 \
            or max(i['u1'] for i in it) > bt - 1e-6 or max(abs(x) + i['w'] / 2 for x, i in zip(xs, it)) > bw / 2:
        bad.append('W2: Entfernungsfeld nicht leuchtend aus drei Ziffern und Einheit mittig in der Sockelrückseite unter dem Fenster')
    xi, ui = max(x for x, _ in inner), max(u for _, u in inner)
    bad += _glass_inside(P, lambda x, u: abs(x) <= xi + 1e-6 and abs(u) <= ui + 1e-6, 'W2')
    bad += _hood_seat(P, 'W2')
    return bad


def main():
    bad, n = [], 0
    for name, (build, typ, wtype, sizes) in BUILT.items():
        for s in sizes:
            P, A = build(s)
            if typ == 'pins':           # B1: lichter Ring, Pinabstände und Köpfe auf dem Prüfkörper (Augenpunkt 680 mm)
                import types as _t
                g = pins_picture(P, A)
                n += 1
                print(f"[test_sights] {name} {s}: Ring {g['share'] * 100:.1f} %, Pins "
                      + ' / '.join(f"{q['deg']:.2f}° {q['px']:.1f} px" for q in g['pins']))
                Wk = _t.SimpleNamespace(PARTS=P, ANCHORS=dict(A, Socket_DrawFull=dict(at=(A['Socket_Eye']['at'][0] + 20, 0, 0))),
                                        META=dict(type=wtype), BORE=A['Socket_Eye']['at'][1] - RT.SIGHT['height_mm'])
                bad += [f'{name} {s}: {b}' for b in check_pins(Wk)]
                continue
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
        if e.get('sight_type') == 'pins':
            g = pins_picture(W.PARTS, W.ANCHORS)
            n += 1
            print(f"[test_sights] {wid}: Pinvisier (B1), Auge {g['dist']:.0f} mm hinter den Pins, Ring {g['share'] * 100:.1f} %, Pins "
                  + ' / '.join(f"{q['deg']:.2f}° {q['px']:.1f} px" for q in g['pins']))
            bad += [f'{wid}: {b}' for b in check_pins(W)]
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
        dx = e['at'][2] if len(e['at']) > 2 else 0     # 0.28: seitliches Visier (Werfer) für die Formprüfung wieder mittig
        Pk, Ak = _kit().side_mount(W.PARTS, W.ANCHORS, -dx) if dx else (W.PARTS, W.ANCHORS)
        bad += [f'{wid}: {b}' for b in check_kit_form(Pk, Ak, getattr(W, 'SIGHT_ID', None))]
        if e['sight_type'] == 'reflex':
            bad += [f'{wid}: {b}' for b in check_reflex_seat(W)]
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
