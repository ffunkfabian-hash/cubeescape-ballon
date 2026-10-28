"""Prüft den Visier-Baukasten v3 ohne Blender (0.21 „Ironsight“, Visier-Standard 3 mit Erweiterung, docs/visier-konzept.md):

  python3 tools/test_sights.py            (läuft in ./check)

- Öffnung im Zielen: lichte Öffnung (Glasbreite bzw. Objektivlinse) als Anteil der Bildbreite bei 75°, gemessen im echten Abstand
  zum Augenpunkt. Gebaute Visiere (common: H0, H2, H4, Z1) in M im Standard, in S/L im Standard oder in der zugelassenen Variante
  (`reticles.share_band`); Familienwaffen im Standard oder in der Variante ihres Typs.
- Ring ohne Wulst: Zielfernrohre außen/innen an der Ringstirn ≈ 1,29 (± 0,02), Innenfläche läuft auf den Augenpunkt zu.
- Absehen gezeichnet: `sight_reticle` flach (Querprofile ≤ 0,1 mm) in der Glasebene (± 0,5 mm), reine Emission, Hüftform der
  Klasse in Hüftgröße (± 3 %), Linien mindestens 1,6 px bei 1280 px Bildbreite.
- Kimme/Korn-Linie und Mini-Reflex, wo verwendet (Baukasten-Katalog): Augenpunkt auf Schiene + 11 bzw. + 15 mm.
- Kimme/Korn K1 an Familienwaffen (0.24, BASIC-04/05): Klasse passt, Linie Träger + 11 mm, Augenpunkt 70 mm hinter der Kimme,
  Lichtspalt zwischen Korn und Kerbe je Seite ≥ 0,25° (≈ 4 px bei 1280 px), Kornpunkt in der Kerbe.
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
    share = ext / (2 * d * TAN * 9 / 16)
    if q.get('drawn', {}).get('kind') != h['kind'] or abs(share / h['share_h'] - 1) > 0.03:
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
    fr = min(q[0] for q in rear['pts'])
    notch = rear['cuts'][0]
    post = front['items'][0]
    ff = max(q[0] for q in post['pts'] if q[1] == max(v[1] for v in post['pts']))
    dr, df = fr - eye_f, (dot['a0'] + dot['a1']) / 2 - eye_f
    deg = math.degrees
    notch_half, post_half = deg(math.atan(notch['w'] / 2 / dr)), deg(math.atan(post['w'] / 2 / (ff - eye_f)))
    return dict(eye_rear=dr, eye_front=df, notch_half=notch_half, post_half=post_half, gap=notch_half - post_half,
                dot=deg(math.atan((dot['c'][0] - cu) / df)), notch_floor=deg(math.atan((notch['u0'] - cu) / dr)),
                blade_top=deg(math.atan((max(q[1] for q in rear['pts']) - cu) / dr)))


def check_iron(W):
    """Kimme/Korn einer Familienwaffe (Visier-Standard 3, Erweiterung 0.21; gebaut 0.24): Fehlerliste."""
    from basic.pilot.optics.sight_kit import IRON_EYE_MM
    bad, e, t = [], W.ANCHORS['Socket_Eye'], W.META['type']
    if t not in RT.SIGHT['line_exempt']['iron'] or RT.SIGHT_KIND.get(t) != 'irons_brackets':
        bad.append(f'Kimme/Korn passt nicht zur Klasse {t} (Visier-Standard 3: {RT.SIGHT_KIND.get(t)})')
    want = RT.SIGHT['rail_line_mm']['iron']
    if e.get('deck') is None or abs(e['at'][1] - e['deck'] - want) > 1e-6:
        bad.append(f"Visierlinie u {e['at'][1]} statt Träger {e.get('deck')} + {want:g} mm")
    g = iron_picture(W.PARTS, W.ANCHORS)
    if abs(g['eye_rear'] - IRON_EYE_MM) > 0.5:
        bad.append(f"Augenpunkt {g['eye_rear']:.1f} mm statt {IRON_EYE_MM:.0f} mm hinter der Kimme")
    if g['gap'] < IRON_GAP_MIN_DEG:
        bad.append(f"Lichtspalt {g['gap']:.2f}° je Seite < {IRON_GAP_MIN_DEG}° (Korn füllt die Kerbe)")
    if not g['notch_floor'] < g['dot'] < g['blade_top']:
        bad.append(f"Kornpunkt bei {g['dot']:.2f}° nicht in der Kerbe ({g['notch_floor']:.2f}° … {g['blade_top']:.2f}°)")
    return bad


BUILT = {   # gebaute Visiere des Baukastens: (Bau mit Größe, Visiertyp, Waffentyp der Hüftform, Größen)
    'H0 Referenz': (lambda s: C.reflex_sight_v21(-6, 143), 'reflex', 'auto_rifle', ('M',)),
    'H2 Pille': (lambda s: C.holo_pille(-6, 143, s), 'reflex', 'submachine_gun', ('S', 'M', 'L')),
    'H4 Kasten': (lambda s: C.holo_kasten(-6, 143, s), 'reflex', 'pulse_rifle', ('S', 'M', 'L')),
    'Z1 Tropfen': (lambda s: C.scope_tropfen(72, 143, 169, s), 'scope', 'scout_rifle', ('S', 'M', 'L')),
}


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
