"""Erzeugt die abgeleiteten Dokumente aus den Waffenmodulen und den gemessenen Specs (data/specs/).

  python3 tools/make_docs.py          → docs/abdeckung.md, docs/haltungen.md, docs/bauteile/BASIC-NN.md, data/matrix.json,
                                         docs/familienmasse.md (Stil v2.1, aus data/specs/*-v2.1.spec.json)
  python3 tools/make_docs.py --check  → nur prüfen, ob die Dateien aktuell sind (Exit 1 bei Abweichung)
Die erzeugten Dateien nicht von Hand ändern; Quelle sind basic/weapons/*.py, basic/matrix.py und data/specs/*.json.
"""
import glob
import importlib
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic import matrix, common  # noqa: E402

HEAD = '<!-- erzeugt von tools/make_docs.py – nicht von Hand ändern -->\n'
REVIEW = os.path.join(ROOT, 'data', 'review.json')


def review():
    return json.load(open(REVIEW, encoding='utf-8')) if os.path.exists(REVIEW) else {}


def shown_actions(W):
    """Aktionen, die als dargestellt gelten: Sichtung in data/review.json 'geprüft' (eine Sichtung setzt den Clip voraus).
    Nur Repo-Daten, keine lokalen Belege: die erzeugte Doku ist auf jedem Rechner gleich (PR-Check auf Linux)."""
    rv = review().get(W.META['id'], {}).get('actions', {})
    return [a for a in W.ACTIONS if rv.get(a, {}).get('status') == 'geprüft']


def static_status(W):
    s = review().get(W.META['id'], {}).get('static', {})
    return f"visuell geprüft ({s.get('by')}, {s.get('date')})" if s.get('status') == 'geprüft' else 'visuelle Prüfung offen'
D2 = {'auto_rifle': 'Halfdan-D (Häkke)', 'pulse_rifle': 'Ogma PR6 (Omolon)', 'scout_rifle': 'Hung Jury SR4 (Omolon)',
      'hand_cannon': 'Minuet-42 (SUROS)', 'sidearm': 'Ironwreath-D (Häkke)', 'submachine_gun': 'Pizzicato-22 (SUROS)',
      'combat_bow': 'Mercury-A (Häkke)', 'shotgun': 'Quitclaim Shotgun III (Häkke)', 'sniper_rifle': 'Elegy-49 (SUROS)',
      'fusion_rifle': 'Cruoris FR4 (Omolon)', 'linear_fusion_rifle': 'Taipan-4fr (VEIST)', 'trace_rifle': 'Ribbontail (Omolon)',
      'grenade_launcher': 'Festival Flight (SUROS)', 'rocket_launcher': 'Morrigan-D (Häkke)',
      'machine_gun': 'Unwavering Duty (SUROS)', 'sword': 'Goldtusk (VEIST)', 'glaive': 'Rake Angle (Häkke)'}
FG = {'01': 'KG02', '02': 'KG03', '03': 'KG11', '04': 'KG12', '05': 'KG01', '06': 'KG06', '07': 'KG10', '08': 'KG04',
      '09': 'KG05', '10': 'KG07', '11': 'KG13', '12': 'KG08', '13': 'KG14', '14': 'KG09', '15': 'KG16', '16': 'KG17', '17': 'KG18'}
REF = {'auto_rifle': 'Q-REF Auto Rifle', 'pulse_rifle': 'Q-REF Pulse', 'scout_rifle': 'Q-REF Scout', 'hand_cannon': 'Q-REF Hand Cannon',
       'sidearm': 'Q-REF Sidearm', 'submachine_gun': 'Q-REF SMG', 'combat_bow': 'Q-REF Bow', 'shotgun': 'Q-REF Shotgun',
       'sniper_rifle': 'Q-REF Sniper', 'fusion_rifle': 'Q-REF Fusion', 'linear_fusion_rifle': 'Q-REF Linear',
       'trace_rifle': 'Q-REF Trace', 'grenade_launcher': 'Q-REF GL', 'rocket_launcher': 'Q-REF Rocket',
       'machine_gun': 'Q-REF MG', 'sword': 'Q-REF Sword', 'glaive': 'Q-REF Glaive'}


def weapons():
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'basic', 'weapons', 'w*.py'))):
        W = importlib.import_module('basic.weapons.' + os.path.basename(f)[:-3])
        sp = os.path.join(ROOT, 'data', 'specs', f"{W.META['id']}.spec.json")
        S = json.load(open(sp, encoding='utf-8')) if os.path.exists(sp) else None
        out.append((W, S))
    return out


def fmt_mm(v):
    return f'{v:.0f}' if v >= 10 else f'{v:.1f}'


def coverage(ws):
    L = [HEAD, '# Abdeckungsmatrix BASIC (erste Etappe)\n',
         'Grundtyp → gewählte Standardausführung → BASIC-Entwurf → Bauteilstruktur → Posen-/Aktionsprofil → Quellen → Prüfstatus.',
         'Maße und Zahlen gemessen am gebauten Modell (`data/specs/`). Zustände: **Entwurf** · **visuell geprüft** · **exportiert** · '
         '**im Spiel angebunden** (hier durchgehend *nein*). Zurückgestellte Varianten: [erweiterungen.md](erweiterungen.md).\n',
         '| Nr. | Grundtyp | Standardausführung (Funktionsreferenz) | BASIC-Entwurf | Länge / Höhe | Bauteile · Baugruppen · Dreiecke | '
         'Magazin/Munition separat | Visier separat | Posen-/Aktionsprofil | Quellen | Prüfstatus |',
         '|---|---|---|---|---|---|---|---|---|---|---|']
    for W, S in ws:
        m = W.META
        ids = {p['id'] for p in W.PARTS}
        asm_of = {p['id']: p['asm'] for p in W.PARTS}
        top = lambda a: [p for p in W.PARTS if p['asm'] == a and asm_of.get(p.get('parent_part')) != a]  # noqa: E731
        ammo, sight = top('ammo'), top('sight')
        none = {'combat_bow': 'Pfeil als eigene Baugruppe (arrow)', 'sword': 'keine Munition; Ladeanzeige im Parierblock'}
        ammo_s = ', '.join(p['de'] for p in ammo) or none.get(m['type'], 'keine')
        sight_s = ('ja: ' + ', '.join(p['de'] for p in sight[:2])) if sight else 'kein Visier (Nahkampf)'
        if m['type'] in ('hand_cannon', 'sidearm'):
            sight_s = 'Kimme/Korn als eigene Teile'
        dims = f"{S['dimensions']['length_m'] * 1000:.0f} / {S['dimensions']['height_m'] * 1000:.0f} mm" if S else 'offen'
        cnt = f"{S['counts']['parts']} · {S['counts']['assemblies']} · {S['counts']['triangles']}" if S else 'offen'
        acts = ', '.join(W.ACTIONS)
        L.append(f"| {m['num']} | {m['type_de']} ({m['type_en']}) | {D2[m['type']]}; Formgen {FG[m['num']]} | "
                 f"[{m['id']}](bauteile/{m['id']}.md) „{m['name']}“ | {dims} | {cnt} | {ammo_s} | {sight_s} | "
                 f"CE-Klasse {matrix.CE_CLASS[m['type']]}; Mechanik: {acts} | Q-D2, Q-FG-01/02, {REF[m['type']]} | "
                 f"Entwurf ✓ · {static_status(W)} · Mechanik gesichtet {len(shown_actions(W))}/{len(W.ACTIONS)} · exportiert "
                 "(.blend/.glb/Spec) · angebunden: nein |")
    L += ['', '## Abweichungen von der Bezugslänge', '',
          '| Nr. | Bezug | BASIC | Abweichung | Grund |', '|---|---|---|---|---|']
    for W, S in ws:
        if not S:
            continue
        ref = W.META['reference_length_m']
        got = S['dimensions'][W.META.get('reference_axis', 'length_m')]
        dev = (got - ref) / ref * 100
        if abs(dev) >= 10:
            L.append(f"| {W.META['num']} | {ref:.3f} m | {got:.3f} m | {dev:+.0f} % | {W.META.get('reference_note', 'offen: Proportion beim Feinentwurf prüfen')} |")
    return '\n'.join(L) + '\n'


def ergonomics(ws):
    """Ergonomie gegen Robotermaße (Q-CE-01..04), gemessen an den Specs. Keine Hände modelliert: reine Maßprüfung."""
    palm_w = 0.086 * 0.65 * 1.4   # Toolgen ego_arms palm_width × hand_scale × Rig-scale (Q-CE-03)
    L = ['', '## Ergonomie gegen Robotermaße (Maßprüfung, ohne Hände)', '',
         f'Bezug: Ego-Handfläche {palm_w * 1000:.0f} mm breit (Q-CE-03), Roboterhand 90 mm (Q-CE-01); Roboter-Variante verlangt Stützhand '
         '≤ 100 mm vor und Schaft ≤ 120 mm hinter `Socket_Hand` (Q-CE-02) – das ist ein Umbau in Toolgen, kein Maß der Weltwaffe. '
         'Abstände entlang der Laufachse (−Y = vorn).', '',
         '| Nr. | Griff B × T × H mm | Abzug vor Griffachse mm | Stützhand vor Hand mm | Schaft hinter Hand mm | Visierlinie über Laufachse mm | Befund |',
         '|---|---|---|---|---|---|---|']
    for W, S in ws:
        if not S:
            continue
        P = {p['id']: p for p in S['parts']}
        A = S['anchors']
        g = P.get('grip')
        gs = '×'.join(f'{v:.0f}' for v in g['size_mm']) if g else 'offen'
        tr = f"{-P['trigger']['bounds_m']['min'][1] * 1000:.0f}" if 'trigger' in P else 'kein Abzug'
        sup = f"{-A['Socket_SupportHand']['position_m'][1] * 1000:.0f}" if 'Socket_SupportHand' in A else 'einhändig'
        stock = [p for p in S['parts'] if p['assembly'] == 'stock']
        st = f"{max(p['bounds_m']['max'][1] for p in stock) * 1000:.0f}" if stock else 'kein Schaft'
        mz = A.get('Socket_Muzzle', {}).get('position_m')
        sl = A.get('Socket_Reticle', {}).get('position_m')
        line = f'{(sl[2] - mz[2]) * 1000:.0f}' if mz and sl else 'kein Visierglas'
        notes = []
        if g and g['size_mm'][0] > palm_w * 1000 * 0.6:
            notes.append('Griff breiter als 60 % der Handfläche')
        if 'Socket_SupportHand' in A and -A['Socket_SupportHand']['position_m'][1] > 0.10:
            notes.append('Robotervariante braucht Umbau (Stützhand)')
        L.append(f"| {W.META['num']} | {gs} | {tr} | {sup} | {st} | {line} | {'; '.join(notes) or 'im Rahmen'} |")
    return '\n'.join(L) + '\n'


def parts_doc(W, S):
    m = W.META
    P = {p['id']: p for p in S['parts']} if S else {}
    acts = {}
    for a, A in W.ACTIONS.items():
        for pid in A['keys']:
            acts.setdefault(pid, []).append(a)
    L = [HEAD, f"# {m['id']} {m['type_de']} – „{m['name']}“\n", m['summary'], '',
         f"Typ `{m['type']}` ({m['type_en']}) · Munition {m['ammo']} · Feuerart `{m['fire']}` · Quelle des Entwurfs: "
         f"`basic/weapons/` · Spec: [`data/specs/{m['id']}.spec.json`](../../data/specs/{m['id']}.spec.json).", '']
    if S:
        d = S['dimensions']
        L += [f"**Maße (gemessen, Ruhelage, Visier montiert):** Länge {d['length_m'] * 1000:.0f} mm · Höhe {d['height_m'] * 1000:.0f} mm · "
              f"Breite {d['width_m'] * 1000:.0f} mm · {S['counts']['parts']} Bauteile · {S['counts']['triangles']} Dreiecke (mit Fasen).", '',
              'Rahmen: Meter, vorn −Y, oben +Z, links +X, Ursprung `Socket_Hand`. `origin_m` ist der Objektursprung '
              '(bei beweglichen Teilen der Drehpunkt).', '']
    L += ['## Baugruppenbaum', '', '```', f"{m['id']}"]
    for a in W.ASSEMBLIES:
        ps = [p for p in W.PARTS if p['asm'] == a['id']]
        if not ps:
            continue
        L.append(f"├─ ASM_{a['id']}  {a['de']} / {a['en']}")
        for p in ps:
            ind = '│   ├─ ' if not p.get('parent_part') else f"│   │  └(an {p['parent_part']}) "
            L.append(f"{ind}{p['id']}  {p['de']}")
    L += ['```', '', '## Bauteilliste', '',
          '| ID | Name (de / en) | Funktion | Befestigung | übergeordnet | Material | Maße X×Y×Z mm | Ursprung m | Bewegung | Entnahme | Schnittstelle | Aktionen |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for p in W.PARTS:
        s = P.get(p['id'], {})
        mv = p.get('move')
        if mv:
            k = mv['kind']
            if k == 'translate':
                mvs = f"verschiebt {sum(c * c for c in mv['vector_mm']) ** 0.5:.0f} mm (f,u,x {tuple(mv['vector_mm'])}); Ereignis {mv.get('event')}"
            elif k == 'rotate':
                mvs = f"dreht um Achse {mv['axis']} durch {tuple(mv['pivot'])} mm, {mv['range_deg'][0]}…{mv['range_deg'][1]}°; Ereignis {mv.get('event')}"
            elif k == 'segment':
                mvs = f"Sehnenhälfte: Ende fest an {tuple(mv['tip'])}, Nockpunkt {sum(c * c for c in mv['vector_mm']) ** 0.5:.0f} mm Auszug"
            else:
                mvs = f"Leuchten 0…{mv.get('max')} (Ereignis {mv.get('event')})"
        else:
            mvs = 'fest'
        rem = 'ja – ' + mv.get('note', 'entlang Bewegung') if mv and mv['kind'] == 'translate' and mv.get('event') in ('reload', 'swap_sight') else 'nein'
        size = '×'.join(fmt_mm(v) for v in s.get('size_mm', [])) or 'offen'
        org = ', '.join(f'{v:.3f}' for v in s.get('origin_m', [])) or 'offen'
        L.append(f"| `{p['id']}` | {p['de']} / {p['en']} | {p['func']} | {p['attach']} | {p.get('parent_part') or 'ASM_' + p['asm']} | "
                 f"{p['mat']} | {size} | {org} | {mvs} | {rem} | {p.get('iface') or '–'} | {', '.join(acts.get(p['id'], [])) or '–'} |")
    if S:
        L += ['', '## Anker', '', '| Anker | Position m (X, Y, Z) | Teil | Hinweis |', '|---|---|---|---|']
        for k, a in S['anchors'].items():
            L.append(f"| `{k}` | {', '.join(f'{v:.4f}' for v in a['position_m'])} | {a.get('part') or '–'} | {a.get('note') or '–'} |")
    ifs = sorted({p['iface'] for p in W.PARTS if p.get('iface')})
    if ifs:
        L += ['', '## Schnittstellen', '', '| ID | Bedeutung | Regel |', '|---|---|---|']
        for i in ifs:
            d = common.INTERFACES[i]
            L.append(f"| {i} | {d['de']} | {d['rule']} |")
    L += ['', '## Aktionen der Mechanik', '', '| Aktion | Beschreibung | Bilder (30 fps) | Teile | Ereignisse (Bild) | Status |',
          '|---|---|---|---|---|---|']
    shown = shown_actions(W)
    for a, A in W.ACTIONS.items():
        ev = ', '.join(f'{n} ({f})' for f, n in A.get('events', []))
        L.append(f"| `{a}` | {A['de']} | {A['frames']} ({A['frames'] / 30:.2f} s) | {', '.join(A['keys'])} | {ev} | "
                 f"{'Mechanik gesichtet (Clip)' if a in shown else 'Mechanik definiert, Sichtung offen'}; Hände offen; Dauer entworfen |")
    L += ['', f"Haltungen, Übergänge und Status aller Aktionen: [haltungen.md › {m['id']}](../haltungen.md#{m['id'].lower()}).", '']
    return '\n'.join(L)


def poses(ws):
    L = [HEAD, '# Haltungs- und Animationsmatrix BASIC\n',
         'Je Waffe alle Standardhaltungen und -aktionen mit Status **dargestellt**, **nicht anwendbar** (mit Grund) oder **offen** '
         '(mit Lücke). Quelle: `basic/matrix.py` (Zeilen und Regeln), Waffenmodule (`ACTIONS`). „Dargestellt“ heißt hier: '
         'Waffenmechanik als Bildfolge/Clip aus dem Modell; Hände und Arme gibt es erst mit einem Toolgen-Import (offen). '
         'Maschinenlesbar: [`data/matrix.json`](../data/matrix.json).\n',
         'Ebenen nach Cube Escape (Q-CE-07): Posendaten (kalibrierbare Grundhaltungen), Clip, prozedural, gemischt. Bildrate der '
         'Mechanikfolgen 30 fps, Zeitbasis Bild 0 = Auslöser.\n', '## Übersicht', '',
         '| Waffe | dargestellt | nicht anwendbar | offen | Mechanik-Clips |', '|---|---|---|---|---|']
    data = {}
    for W, S in ws:
        st = matrix.status(W.META, shown_actions(W), f"Clip <EVIDENCE>/clips/{W.META['id']}_<aktion>.mp4, gesichtet laut data/review.json",
                           defined=list(W.ACTIONS))
        data[W.META['id']] = st
        c = {k: sum(1 for _, s, _ in st if s == k) for k in ('dargestellt', 'nicht anwendbar', 'offen')}
        L.append(f"| [{W.META['id']}](#{W.META['id'].lower()}) {W.META['type_de']} | {c['dargestellt']} | {c['nicht anwendbar']} | "
                 f"{c['offen']} | {', '.join(W.ACTIONS)} |")
    L += ['', '## Übergänge und Unterbrechungen (gemeinsam, Zuordnung je Waffe unten)', '',
          '| ID | Start → Ende | Auslöser | Priorität | erlaubte Unterbrechung | Ereignisse | Dauer (Quelle) |', '|---|---|---|---|---|---|---|']
    for t in matrix.TRANSITIONS:
        L.append('| ' + ' | '.join(t) + ' |')
    L.append('')
    for W, S in ws:
        m = W.META
        L += [f"## {m['id']}", '', f"{m['type_de']} „{m['name']}“ · CE-Profilklasse: {matrix.CE_CLASS[m['type']]} · "
              f"Munitionszufuhr: {matrix.FEED.get(m['type'], 'keine')}", '',
              '| Zeile | Bereich | Ebene | Status | Detail |', '|---|---|---|---|---|']
        for r, s, d in data[m['id']]:
            L.append(f"| `{r['id']}` {r['de']} | {r['cat']} | {r['layer']} | **{s}** | {d} |")
        tr_na = {'tr_charge_cancel': m['type'] not in matrix.CHARGE,
                 'tr_reload_switch': m['type'] in ('sword', 'combat_bow'), 'tr_reload_cancel': m['type'] in ('sword', 'combat_bow'),
                 'tr_fire_move': m['type'] == 'sword', 'tr_fire_air': m['type'] == 'sword'}
        for t in matrix.TRANSITIONS:
            na = tr_na.get(t[0], False)
            L.append(f"| `{t[0]}` {t[1]} | Übergang | gemischt | **{'nicht anwendbar' if na else 'offen'}** | "
                     f"{'kein Nachladen/Aufladen bzw. kein Feuer bei diesem Typ' if na else 'Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: ' + t[6]} |")
        L.append('')
    js = {k: [dict(row=r['id'], de=r['de'], cat=r['cat'], layer=r['layer'], status=s, detail=d) for r, s, d in v] for k, v in data.items()}
    js['_transitions'] = [dict(zip(('id', 'de', 'trigger', 'priority', 'interrupt', 'events', 'duration'), t)) for t in matrix.TRANSITIONS]
    return '\n'.join(L), js


def family_dims():
    """Familienmaße Stil v2.1: Lagen und Größen aus den gemessenen Specs der Module basic/pilot/w*_v21.py (Startpunkt für neue
    Waffen). Lagen in mm relativ zu Socket_Hand, f vorn, u oben (Spec: −Y vorn, +Z oben)."""
    from basic.reticles import SIGHT
    def fu(p):
        return -p[1] * 1000, p[2] * 1000
    rows, sizes = [], []
    for f in sorted(glob.glob(os.path.join(ROOT, 'basic', 'pilot', 'w*_v21.py'))):
        W = importlib.import_module('basic.pilot.' + os.path.basename(f)[:-3])
        wid = f"{W.META['id']}-{W.META['variant']}"
        sp = os.path.join(ROOT, 'data', 'specs', f'{wid}.spec.json')
        if not os.path.exists(sp):
            continue
        S = json.load(open(sp, encoding='utf-8'))
        A = {k: fu(v['position_m']) for k, v in S['anchors'].items()}
        D = S['dimensions']
        e = W.ANCHORS['Socket_Eye']
        iron = e['sight_type'] == 'iron'     # Kimme/Korn (0.24): Augenabstand zur Kimme, eigene Linie (Visierhöhe gilt nicht)
        full = e['sight_type'] == 'fullscreen'   # Scharfschütze (0.25): Augenabstand zum Objektivring wie das Zielfernrohr
        ref = 'Socket_Sight' if iron else SIGHT['types']['scope' if full else e['sight_type']]['ref']
        de = 'Kimme/Korn' if iron else 'Zielfernrohr, Vollbild' if full else SIGHT['types'][e['sight_type']]['de']
        mw = A.get('Socket_MagWell') or A.get('Socket_LoadingGate')     # Schrot (0.25): Röhrenmagazin, Ladeklappe statt Schacht
        mw = '–' if mw is None else f"{mw[0]:.0f} / {mw[1]:.0f}" + ('' if 'Socket_MagWell' in A else ' (Ladeklappe)')
        mf, mu = A['Socket_Muzzle']
        ex = S['anchors']['Socket_Eye']['position_m'][0] * 1000     # 0.28: seitliches Visier (Werfer) – Visierhöhe als Abstand zur Achse
        side = f' (x {ex:.0f})' if abs(ex) > 0.5 else ''
        rear = -D['bounds_m']['max'][1] * 1000
        rows.append(f"| {wid} {W.META['type_de']} | {D['length_m'] * 1000:.0f} × {D['height_m'] * 1000:.0f} × {D['width_m'] * 1000:.0f} | "
                    f"{mu:.0f} | {mf:.0f} | {rear:.0f} | {A['Socket_Eye'][1]:.0f}{side} | {math.hypot(A['Socket_Eye'][1] - mu, ex):.1f} | "
                    f"{A[ref][0] - A['Socket_Eye'][0]:.0f} ({de}) | "
                    f"{A['Socket_SupportHand'][0]:.0f} / {A['Socket_SupportHand'][1]:.0f} | "
                    f"{mw} | "
                    f"{A['Socket_CenterOfMass'][0]:.0f} / {A['Socket_CenterOfMass'][1]:.0f} | "
                    f"{S['counts']['parts']} / {S['counts']['triangles']} |")
        box = {}
        for q in S['parts']:
            for key in (q['assembly'], q['id']):
                lo, hi = box.get(key, (q['bounds_m']['min'], q['bounds_m']['max']))
                box[key] = ([min(a, b) for a, b in zip(lo, q['bounds_m']['min'])], [max(a, b) for a, b in zip(hi, q['bounds_m']['max'])])
        cell = [(f"{(box[k][1][1] - box[k][0][1]) * 1000:.0f} × {(box[k][1][2] - box[k][0][2]) * 1000:.0f} × "
                 f"{(box[k][1][0] - box[k][0][0]) * 1000:.0f}" if k in box else '–')
                for k in ('receiver', 'support', 'stock', 'sight', 'grip', 'magazine')]
        sizes.append(f"| {wid} | " + ' | '.join(cell) + ' |')
    L = [HEAD.rstrip('\n'), '# Familienmaße Stil v2.1', '',
         'Gemessen am gebauten Modell (`data/specs/<Waffe>-v2.1.spec.json`, mit Fasen, Visier montiert, Ruhelage). Startpunkt für',
         'neue Waffen der Familie: ähnliche Klasse suchen, Lagen übernehmen, Abweichungen im Modul-Docstring begründen',
         '([stilhandbuch.md](stilhandbuch.md) §6/§7). Nach jedem Vollrendering `tools/sync_specs.py` und `tools/make_docs.py`.', '',
         '## Lagen', '',
         'mm relativ zu `Socket_Hand` (Griffachse), f vorn, u oben. Mündung f = Stirn der Mündung, Heck f = hinterste Kante',
         '(negativ = hinter dem Griff). Visierhöhe = Abstand der Visierlinie zur Laufachse, bei mittigem Visier die Höhe darüber (Soll '
         f"{SIGHT['height_mm']:.0f} ± {SIGHT['height_tol_mm']:.0f} mm; Kimme/Korn mit eigener Linie Träger + "
         f"{SIGHT['rail_line_mm']['iron']:g} mm, dort gilt sie nicht), Augenabstand = Augenpunkt bis Glas, Objektiv bzw. Kimme.", '',
         '| Waffe | L × H × B | Laufachse u | Mündung f | Heck f | Visierlinie u | Visierhöhe | Augenabstand | Stützhand f / u | '
         'Magazinschacht f / u | Schwerpunkt f / u | Teile / Dreiecke |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|'] + rows + [
         '', '## Größen der Hauptteile', '',
         'Außenmaße L × H × B in mm (Länge entlang f, Höhe u, Breite x): Baugruppen als Hülle aller ihrer Teile, Griff und Magazin',
         'als einzelne Teile.', '',
         '| Waffe | Gehäuse `receiver` | Vorderbau `support` | Schaft `stock` | Visier `sight` | Griff `grip` | Magazin `magazine` |',
         '|---|---|---|---|---|---|---|'] + sizes
    tools = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'basic', 'pilot', 't*_v21.py'))):    # Werkzeuge: ohne Visier und Magazin
        W = importlib.import_module('basic.pilot.' + os.path.basename(f)[:-3])
        wid = f"{W.META['id']}-{W.META['variant']}"
        sp = os.path.join(ROOT, 'data', 'specs', f'{wid}.spec.json')
        if not os.path.exists(sp):
            continue
        S = json.load(open(sp, encoding='utf-8'))
        A = {k: fu(v['position_m']) for k, v in S['anchors'].items()}
        D = S['dimensions']
        mf, mu = A['Socket_Muzzle']
        tools.append(f"| {wid} {W.META['type_de']} | {D['length_m'] * 1000:.0f} × {D['height_m'] * 1000:.0f} × "
                     f"{D['width_m'] * 1000:.0f} | {mu:.0f} | {mf:.0f} | {-D['bounds_m']['max'][1] * 1000:.0f} | "
                     f"{A['Socket_SupportHand'][0]:.0f} / {A['Socket_SupportHand'][1]:.0f} | "
                     f"{A['Socket_CenterOfMass'][0]:.0f} / {A['Socket_CenterOfMass'][1]:.0f} | "
                     f"{S['counts']['parts']} / {S['counts']['triangles']} |")
    if tools:
        L += ['', '## Werkzeuge', '',
              'Werkzeuge der Familie (`basic/pilot/t*_v21.py`): gleicher Griff und gleiche Lagen um `Socket_Hand`, ohne Visier und',
              'Magazin; Schussachse statt Laufachse.', '',
              '| Werkzeug | L × H × B | Schussachse u | Mündung f | Heck f | Stützhand f / u | Schwerpunkt f / u | Teile / Dreiecke |',
              '|---|---|---|---|---|---|---|---|'] + tools
    return '\n'.join(L) + '\n'


def main(argv):
    ws = weapons()
    files = {os.path.join(ROOT, 'docs', 'abdeckung.md'): coverage(ws) + ergonomics(ws)}
    txt, js = poses(ws)
    files[os.path.join(ROOT, 'docs', 'haltungen.md')] = txt
    files[os.path.join(ROOT, 'data', 'matrix.json')] = json.dumps(js, ensure_ascii=False, indent=1) + '\n'
    for W, S in ws:
        files[os.path.join(ROOT, 'docs', 'bauteile', f"{W.META['id']}.md")] = parts_doc(W, S)
    files[os.path.join(ROOT, 'docs', 'familienmasse.md')] = family_dims()
    if '--check' in argv:
        bad = [f for f, t in files.items() if not os.path.exists(f) or open(f, encoding='utf-8').read() != t]
        print('veraltet:', [os.path.relpath(f, ROOT) for f in bad] or 'nichts')
        return 1 if bad else 0
    os.makedirs(os.path.join(ROOT, 'docs', 'bauteile'), exist_ok=True)
    for f, t in files.items():
        open(f, 'w', encoding='utf-8').write(t)
    print(f'{len(files)} Dateien geschrieben')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
