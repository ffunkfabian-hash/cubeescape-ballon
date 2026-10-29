"""Regeln aus Motiongen REF 0.30 „Blueprint“ als Prüfungen ohne Blender (BALLON 0.30 „Rulebook“, Nutzer 29.10.2026: „Alle wie
empfohlen“ – A1–A7 A, A8 B, A9 A, F1–F9 A). Regeln und Quellen: docs/stilhandbuch.md › 2 und › 12.

Reines Python (kein bpy, kein numpy): läuft in ./check auf dem Mac und im PR-Check auf Linux. Die Messungen am Netz schreiben
Blender-Werkzeuge in data/ (tools/silhouettes.py → data/silhouettes.json, tools/ego_clear.py → data/ego_clear.json); hier wird nur
ausgewertet. Fehler (A1 Silhouette, Figurenvertrag, Handmaß) lassen ./check scheitern; Budget, Freihaltezone und Proportion sind
Warnungen bzw. Hinweise (Umbau nur nach Rückfrage beim Nutzer).
"""
import glob
import hashlib
import importlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# A1 (A-R1, A-R7; Quellen A01, A02, A20, A08, YA02, YA03): schwarze Seitensilhouetten auf gleiche Länge normiert, paarweise IoU
IOU_LIMIT = 0.85
SIL_SHARED = ['basic/common.py', 'basic/kit.py']      # Formbausteine aller Waffen: Teil des Aktualitätsschlüssels (Richter 0.30)
# A2 (A-R24; Quellen A05, YB09, A21): Dreiecke je Ego-Waffe, Ziel und Obergrenze (Warnung); Grenze 50 000 (Nutzer 29.10.2026)
TRI_TARGET, TRI_LIMIT = 20000, 50000
# A4 (A-R9; Quelle YA01): Freihaltezone im Hüftbild – ±10 % der Bildbreite um die Absehen-Spalte, obere zwei Drittel
ZONE = dict(half_w=0.10, top=0.0, bottom=2 / 3)
# A4 gelockert (Nutzer 29.10.2026, „B Zone lockern“): das vordere Ende (Mündung) darf in die untere äußere Ecke der Zone ragen – alles
# Belegte liegt dann rechts von x0 und unterhalb von y0 (Anteile von B/H); die Destiny-Hüftlage (Mündung x 54–59 / y 60–71 %) hat Vorrang
ZONE_FRONT = dict(x0=0.53, y0=0.55)
# F1 (F-R8; F28, F05, F07): ≈ 7,5 Kopfhöhen, Helm gemessen, Kopf nicht vergrößert
HEADS_TARGET, HEADS_BAND = 7.5, (7.0, 8.0)
# F5 (F-R11; F11, YB06, A24): ein Handmaß für Ego und Figur; Bezug Griffbreite der Familie (BGM-1, common.grip_rifle w)
GRIP_W_MM = 30.0
HAND_TOL = 0.01
# F6 (F-R15; YB09, F27): Figur ohne Ausrüstung, Knochen ohne Simulation (Warnung)
FIG_TRI_LIMIT, FIG_BONE_LIMIT = 30000, 100
# F2 (F-R7) Grundform je Rolle, F7 (F-R9, F-R13) Größenklassen als Vielfaches der Spielerfigur
ROLE_FORM = {'player': 'square_circle', 'friendly': 'circle', 'enemy': 'triangle'}
SIZE_CLASSES = {'small': (0.5, 0.7), 'medium': (0.9, 1.1), 'large': (1.6, None)}
# F3 (F-R17, F-R18; F20, F15, YB04): Posensatz mit Durchdringungsprüfung, Plattenabstand in Grundhaltung
POSES = ('arm_up', 'arm_cross', 'deep_squat', 'lunge', 'twist_l45', 'twist_r45')
PLATE_GAP_MM = 1.0


def family():
    """Stil-v2.1-Familie (alle Waffen BASIC-01–15 v2.1 und Werkzeuge T*): [(Ausgabe-ID, Modul)] in fester Reihenfolge."""
    out = []
    for pat in ('w*_v21.py', 't*_v21.py'):
        for f in sorted(glob.glob(os.path.join(ROOT, 'basic', 'pilot', pat))):
            W = importlib.import_module('basic.pilot.' + os.path.basename(f)[:-3])
            out.append((f"{W.META['id']}-{W.META['variant']}", W))
    return out


def sha_files(paths):
    h = hashlib.sha256()
    for p in paths:
        h.update(p.encode())
        h.update(open(os.path.join(ROOT, p), 'rb').read())
    return h.hexdigest()


# ------------------------------------------------------------------ A1 Silhouetten
def rows(mask):
    """Maske {w, h, rows: [[Beginn, Ende, …] je Zeile]} → Zeilen als Bitfelder (int)."""
    out = []
    for r in mask['rows']:
        v = 0
        for s, e in zip(r[::2], r[1::2]):
            v |= (1 << e) - (1 << s)
        out.append(v)
    return out


def best_iou(a, b):
    """Größte Überdeckung (IoU) zweier gleich langer Masken über alle senkrechten Verschiebungen (Länge normiert, daher waagrecht
    fest). Gibt (IoU, Verschiebung in Zeilen). Strenger als eine Ausrichtung an der Laufachse: kein Paar wird durch die Lage geschont."""
    ra, rb = rows(a), rows(b)
    na, nb = sum(v.bit_count() for v in ra), sum(v.bit_count() for v in rb)
    best, at = 0, 0
    for dy in range(-(len(rb) - 1), len(ra)):
        inter = sum((ra[i] & rb[i - dy]).bit_count() for i in range(max(0, dy), min(len(ra), len(rb) + dy)))
        if inter > best:
            best, at = inter, dy
    return (best / (na + nb - best) if na + nb else 0.0), at


def iou_matrix(data, view='side'):
    """{(a, b): IoU} für alle Paare der Masken in data['weapons'] (a < b in Reihenfolge der Datei)."""
    ids = list(data['weapons'])
    return {(a, b): best_iou(data['weapons'][a][view], data['weapons'][b][view])[0]
            for i, a in enumerate(ids) for b in ids[i + 1:]}


def silhouette_problems(data, fam, specs):
    """Fehlerliste A1: jede Waffe der Familie gemessen und aktuell (parts_sha256 und Dreieckszahl des Specs), jedes Paar der
    Seitensilhouetten unter IOU_LIMIT. Aktuell = gleicher parts_sha256, gleiche Dreieckszahl und gleicher SHA von SIL_SHARED. fam: [(ID, Modul)], specs: {ID: Spec}."""
    from tools.export_unity import parts_sha
    bad = []
    W = data.get('weapons', {})
    for wid, mod in fam:
        e = W.get(wid)
        if e is None:
            bad.append(f'{wid}: Silhouette fehlt in data/silhouettes.json (ce lock blender -- Blender -b -P tools/silhouettes.py)')
        elif e.get('parts_sha256') != parts_sha(mod) or e.get('triangles') != specs.get(wid, {}).get('counts', {}).get('triangles') \
                or e.get('shared_sha256') != sha_files(SIL_SHARED):
            bad.append(f'{wid}: Silhouette veraltet (Entwurf oder Netz geändert; tools/silhouettes.py neu laufen lassen)')
    if bad:
        return bad
    over = sorted(((v, a, b) for (a, b), v in iou_matrix(dict(weapons={k: W[k] for k, _ in fam})).items() if v >= IOU_LIMIT),
                  reverse=True)
    return [f'Silhouetten {a} ↔ {b}: IoU {v:.3f} ≥ {IOU_LIMIT} (verwechselbar; Leitmerkmal schärfen)' for v, a, b in over]


# ------------------------------------------------------------------ A2 Dreiecksbudget
def budget_notes(specs):
    """Warnungen A2: {ID: Spec} → Zeilen für Waffen über Ziel (Hinweis) bzw. Obergrenze (Warnung)."""
    out = []
    for wid, S in specs.items():
        t = S['counts']['triangles']
        if t > TRI_LIMIT:
            out.append(f'Warnung Budget {wid}: {t} Dreiecke > Grenze {TRI_LIMIT} (A2)')
        elif t > TRI_TARGET:
            out.append(f'Hinweis Budget {wid}: {t} Dreiecke > Ziel {TRI_TARGET} (A2)')
    return out


# ------------------------------------------------------------------ A5 Fasen als Materialsignal
def soft_bevel_problems(fam):
    """Fehler A5 (A-R12; Quellen A06, A09, A10, A11, A13, YA09): der Griff der Haupthand in Gummi (`grip`, Rolle `rubber`) trägt R_SOFT,
    und R_SOFT steht nur an Gummi. Die übrigen Gummiteile behalten ihre Stufe (Auslegung 0.32, docs/versions/0.32-softgrip.md › A5):
    Polsterstreifen, Tragegriff und Rippen zu dünn, Griffband BASIC-12 eine Hülse mit 1 mm Wand, Wangen-/Schulterauflagen keine Griffe."""
    from basic.common import R_SOFT
    out = []
    for wid, W in fam:
        for p in W.PARTS:
            b = p.get('bevel')
            if p['id'] == 'grip' and p['mat'] == 'rubber' and b != R_SOFT:
                out.append(f'{wid}: Griff in Gummi mit Fase {b} mm statt R_SOFT {R_SOFT} mm (A5)')
            elif b == R_SOFT and p['mat'] != 'rubber':
                out.append(f'{wid}: {p["id"]} ({p["mat"]}) mit R_SOFT – nur für Griffpolster in Gummi (A5)')
    return out


# ------------------------------------------------------------------ A4 Freihaltezone im Hüftbild
def zone_px(w, h):
    """Freihaltezone in Pixeln (x0, x1, y0, y1; y von oben), Absehen-Spalte = Bildmitte (Unity EgoPlayer zeichnet das
    Hüft-Fadenkreuz bei Screen.width / 2)."""
    cx = w / 2
    return (round(cx - ZONE['half_w'] * w), round(cx + ZONE['half_w'] * w), round(ZONE['top'] * h), round(ZONE['bottom'] * h))


def clear_sources(mod):
    """Quellen der Hüftbild-Maske einer spielbaren Waffe: Waffenmodul(e), Haltungen, Arm, Ego-Szene."""
    from tools.export_unity import weapon_files
    return weapon_files(mod) + ['basic/arms/ego.py', 'basic/arms/robot_arm.py', 'basic/common.py', 'basic/kit.py', 'tools/ego_build.py',
                                'tools/blender_build.py', 'tools/ego_clear.py']


def clear_zone_notes(data, playable):
    """Warnungen A4: playable [(ID, Modul)] gegen data/ego_clear.json. Belegte Zonenpixel > 0 → Verletzung; fehlend oder veraltet
    → Hinweis (die Prüfung braucht die GPU, ein Umbau anderer Teile soll ./check nicht rot machen)."""
    out = []
    for wid, mod in playable:
        e = data.get('weapons', {}).get(wid)
        if e is None:
            out.append(f'Hinweis Freihaltezone {wid}: nicht gemessen (ce lock gpu -- Blender -b -P tools/ego_clear.py)')
            continue
        stale = e.get('sources_sha256') != sha_files(clear_sources(mod))
        if stale:
            out.append(f'Hinweis Freihaltezone {wid}: Messung veraltet (Waffe, Haltung oder Arm geändert; tools/ego_clear.py)')
        if e['zone_px'] > 0 and e['cols'] and e['cols'][0] >= ZONE_FRONT['x0'] and e['top_y'] >= ZONE_FRONT['y0']:
            continue                                    # nur das vordere Ende in der erlaubten Ecke (A4 gelockert)
        if e['zone_px'] > 0:
            pre = 'Hinweis Freihaltezone (Stand vorher)' if stale else 'Warnung Freihaltezone'
            out.append(f"{pre} {wid}: {e['zone_px']} px ({e['zone_share'] * 100:.2f} % der Zone) belegt, "
                       f"oberster Punkt in den Zonenspalten {e['top_y'] * 100:.1f} % H, Spalten {e['cols'][0] * 100:.1f}–{e['cols'][1] * 100:.1f} % B (A4)")
    return out


# ------------------------------------------------------------------ F Figuren
def hand_measure(arm):
    """Handmaß eines Arm-Moduls (robot_arm-Form, mm): Handflächenbreite und -länge, Fingerteilung, Fingerlängen, Daumen."""
    return dict(palm_w=arm.PALM_W, palm_len=arm.PALM_LEN, finger_pitch=abs(arm.FINGER_X[0] - arm.FINGER_X[1]),
                finger_w=arm.FINGER_W, finger_len=[sum(arm.FINGER_LINKS) * s for s in arm.FINGER_SCALE],
                thumb_len=sum(arm.THUMB_LINKS), palm_per_grip=arm.PALM_W / GRIP_W_MM)


def hand_problems(fig, ego, tol=HAND_TOL):
    """Fehler F5: jedes Maß der Figurenhand weicht höchstens tol (relativ) von der Ego-Hand ab."""
    bad = []
    for k, v in ego.items():
        f = fig.get(k)
        vs, fs = (v, f) if isinstance(v, list) else ([v], [f] if f is not None else None)
        if fs is None or len(fs) != len(vs) or any(abs(a - b) > tol * abs(b) for a, b in zip(fs, vs)):
            bad.append(f'Handmaß {k}: Figur {f} ≠ Ego {v} (F5: ein Handmaß für Ego und Figur, ±{tol * 100:.0f} %)')
    return bad


def figure_budget_notes(name, tris, bones):
    out = []
    if tris is not None and tris > FIG_TRI_LIMIT:
        out.append(f'Warnung Figur {name}: {tris} Dreiecke > {FIG_TRI_LIMIT} (F6, Ausrüstung getrennt gezählt)')
    if bones is None:
        out.append(f'Hinweis Figur {name}: Knochenzahl nicht angegeben (F6: ≤ {FIG_BONE_LIMIT})')
    elif bones > FIG_BONE_LIMIT:
        out.append(f'Warnung Figur {name}: {bones} Knochen > {FIG_BONE_LIMIT} (F6)')
    return out


def proportion_note(name, height_mm, head_mm, measured='Helm'):
    """Hinweis F1: Körperhöhe in Kopfhöhen außerhalb HEADS_BAND."""
    k = height_mm / head_mm
    if not HEADS_BAND[0] <= k <= HEADS_BAND[1]:
        return [f'Hinweis Figur {name}: {k:.2f} Kopfhöhen ({measured} {head_mm:.0f} mm bei {height_mm:.0f} mm) statt ≈ {HEADS_TARGET} (F1)']
    return []


def figure_meta_problems(F):
    """Fehler F2/F7/F3/F5: Vertrag eines Figurenmoduls in basic/figures/ (siehe basic/figures/__init__.py)."""
    bad = []
    m = getattr(F, 'META', {})
    name = m.get('id', F.__name__)
    if m.get('role') not in ROLE_FORM:
        bad.append(f'{name}: META role {m.get("role")!r} unbekannt ({", ".join(ROLE_FORM)})')
    elif m.get('form') != ROLE_FORM[m['role']]:
        bad.append(f'{name}: Grundform {m.get("form")!r} passt nicht zur Rolle {m["role"]} ({ROLE_FORM[m["role"]]}, F2)')
    sc = m.get('size_class')
    if m.get('role') != 'player':
        if sc not in SIZE_CLASSES:
            bad.append(f'{name}: Größenklasse {sc!r} fehlt ({", ".join(SIZE_CLASSES)}, F7)')
        elif 'scale' in m:
            lo, hi = SIZE_CLASSES[sc]
            if m['scale'] < lo or (hi is not None and m['scale'] > hi):
                bad.append(f'{name}: Maßstab {m["scale"]} außerhalb der Klasse {sc} (F7)')
    miss = [p for p in POSES if p not in getattr(F, 'POSES', {})]
    if miss:
        bad.append(f'{name}: Posensatz unvollständig, es fehlen {", ".join(miss)} (F3)')
    if not hasattr(F, 'HAND'):
        bad.append(f'{name}: HAND (Arm-Modul der Hand) fehlt (F5)')
    return bad


def figure_modules():
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'basic', 'figures', '*.py'))):
        if not os.path.basename(f).startswith('_'):
            out.append(importlib.import_module('basic.figures.' + os.path.basename(f)[:-3]))
    return out


def robot_spec_notes(path):
    """Budget- und Proportionshinweise aus einem Roboter-Spec (Format cubeescape-ballon/robot-spec, 0.23 „Gauntlet“): Dreiecke
    aller Baugruppen, Knochen aus measured.bones (sonst Hinweis), Kopfhöhe aus der Kopfbaugruppe (mit Hals, daher nur Näherung)."""
    S = json.load(open(path, encoding='utf-8'))
    if S.get('format') != 'cubeescape-ballon/robot-spec':
        return []
    M = S.get('measured', {})
    A = M.get('assemblies', {})
    tris = sum(a.get('triangles', 0) for a in A.values()) or None
    out = figure_budget_notes(S.get('id', os.path.basename(path)), tris, M.get('bones'))
    if M.get('height_mm') and A.get('head', {}).get('size_mm'):
        out += proportion_note(S.get('id'), M['height_mm'], M.get('head_mm', A['head']['size_mm'][2]),
                               'Helm' if 'head_mm' in M else 'Kopfbaugruppe mit Hals')
    return out


def arm_rigs():
    """Wählbare Ego-Armsätze neben Arm v3 (Formstudien basic/arms/studies/, 0.31 „Gauntlet“): F5 gilt auch für sie."""
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'basic', 'arms', 'studies', '*.py'))):
        if not os.path.basename(f).startswith('_'):
            out.append(importlib.import_module('basic.arms.studies.' + os.path.basename(f)[:-3]))
    return out


def figure_report():
    """(Fehler, Hinweise) aller Figuren im Repo: Module in basic/figures/ (Vertrag, Handmaß), Ego-Armsätze (Handmaß) und
    Roboter-Specs in data/."""
    from basic.arms import robot_arm
    err, notes = [], []
    ego = hand_measure(robot_arm)
    for A in arm_rigs():
        err += [f"Armsatz {A.__name__.split('.')[-1]}: {b}" for b in hand_problems(hand_measure(A), ego)]
    for F in figure_modules():
        err += figure_meta_problems(F)
        if hasattr(F, 'HAND'):
            err += [f"{F.META.get('id', F.__name__)}: {b}" for b in hand_problems(hand_measure(F.HAND), ego)]
        if hasattr(F, 'HEIGHT_MM') and hasattr(F, 'HEAD_MM'):
            notes += proportion_note(F.META.get('id'), F.HEIGHT_MM, F.HEAD_MM)
    for p in sorted(glob.glob(os.path.join(ROOT, 'data', '*.spec.json'))):
        notes += robot_spec_notes(p)
    return err, notes


# ------------------------------------------------------------------ Zusammenfassung für ./check
def summarize(notes):
    """Warnungen/Hinweise gleicher Art in einer Zeile (für ./check): „Warnung Budget BASIC-01-v2.1: …“ → je Art eine Zeile."""
    groups = {}
    for n in notes:
        head, _, rest = n.partition(': ')
        kind, _, who = head.rpartition(' ')
        groups.setdefault(kind, []).append(f'{who.replace("BASIC-", "").replace("-v2.1", "")} {rest}'.strip())
    return [f'{k} ({len(v)}): ' + ' · '.join(v) for k, v in groups.items()]


def report():
    """(Fehler, Warnungen/Hinweise) aller Regeln dieses Moduls am Repo-Stand."""
    from tools.export_unity import WEAPONS
    fam = family()
    specs = {wid: json.load(open(os.path.join(ROOT, 'data', 'specs', f'{wid}.spec.json'), encoding='utf-8'))
             for wid, _ in fam if os.path.exists(os.path.join(ROOT, 'data', 'specs', f'{wid}.spec.json'))}
    err, notes = [], []
    sp = os.path.join(ROOT, 'data', 'silhouettes.json')
    err += silhouette_problems(json.load(open(sp, encoding='utf-8')) if os.path.exists(sp) else {}, fam, specs)
    err += soft_bevel_problems(fam)
    notes += budget_notes(specs)
    cp = os.path.join(ROOT, 'data', 'ego_clear.json')
    mods = {f"{m.META['id']}-{m.META['variant']}": m for m in (importlib.import_module(f'basic.{w}') for w in WEAPONS)}
    notes += clear_zone_notes(json.load(open(cp, encoding='utf-8')) if os.path.exists(cp) else {}, sorted(mods.items()))
    e, n = figure_report()
    return err + e, notes + n
