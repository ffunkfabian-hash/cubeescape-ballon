"""Ego-Ausgaben: Clips, Kontaktbögen und Doku aus den Bildfolgen von tools/ego_build.py.

  python3 tools/make_ego.py clips   [Waffe]   → <EVIDENCE>/clips/ego_<waffe>_<aktion>.mp4 (854 × 480, Marker eingeblendet)
  python3 tools/make_ego.py sheets  [Waffe]   → <EVIDENCE>/ego_<waffe>_<aktion>.png (Start, Marker, Ende) – Grundlage der Sichtung
  python3 tools/make_ego.py docs              → docs/ego.md (je spielbarer Waffe: Klassenwerte mit Herkunft, Haltungen, Aktionen, Marker,
                                               Gelenkprüfung, Sichtung)
  python3 tools/make_ego.py --check           → Ego-Daten konsistent (Haltungen, Griffe, Fingerstellungen, Matrixzeilen) je Waffe
Standardwaffe: BASIC-01-v2.1 (Pilot). Waffen mit Ego-Daten: tools/export_unity.WEAPONS; Aktionen und Haltungen je Klasse (ego.profile).
"""
import importlib
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools.paths import OUT, EVIDENCE  # noqa: E402
from basic.arms import ego as EG, robot_arm as RA  # noqa: E402
from basic import matrix, reticles as RT  # noqa: E402
from tools.export_unity import WEAPONS  # noqa: E402




def _fx_text(F):
    """Wirkung der Klasse (0.34, ego.PAYLOAD) als kurzer Text."""
    k = F['kind']
    t = {'hitscan': f"Kugel, Einschlag {F['impact']}", 'pellets': f"Schrot {F['pellets']} Kugeln, Kegel {F['cone_deg']:g}°",
         'projectile': f"Projektil {F['speed_mps']:g} m/s, Fall {F['gravity_mps2']:g} m/s², Explosion {F['radius_m']:g} m, Laufrauch {F['smoke_s']:g} s",
         'arrow': f"Pfeil {F['speed_mps']:g} m/s, Fall {F['gravity_mps2']:g} m/s², steckt {F['stick_s']:g} s",
         'beam': f"Dauerstrahl {F['width_m'] * 100:g} cm", 'bolts': f"Bolzen {F['speed_mps']:g} m/s, {F['length_m']:g} m",
         'rail': f"Strahl {F['width_m'] * 100:g} cm, {F['beam_s']:g} s", 'none': 'keine'}.get(k, k)
    if F.get('tracer_every'):
        t += f", Leuchtspur jeder {F['tracer_every']}. Schuss"
    return t

def _live_text(v):
    """Live-Teil für die Doku: Teil, Liste (glow, index, fill) oder Füllstand (rounds, 0.34) als kurzer Text."""
    if isinstance(v, dict):
        return f"{v.get('mode', '')} ({len(v.get('sets', ()))} Sätze{', Trommel ' + v['drum'] if v.get('drum') else ''})"
    if isinstance(v, (list, tuple)):
        return ' + '.join(v) if v else '–'
    return v

def module(wid):
    """Waffenmodul zu einer Waffen-ID (BASIC-06-v2.1) unter den spielbaren Waffen."""
    for m in WEAPONS:
        W = importlib.import_module(f'basic.{m}')
        if EG.weapon_id(W) == wid:
            return W
    raise KeyError(f'{wid}: keine spielbare Waffe (tools/export_unity.WEAPONS)')

FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
BG = '#9EA4AC'


def frames_of(wid, act):
    return sorted(glob.glob(os.path.join(OUT, wid, 'ego', act, '[0-9]*.png')))


def clips(wid):
    dst = os.path.join(EVIDENCE, 'clips')
    os.makedirs(dst, exist_ok=True)
    made = {}
    for act, A in EG.profile(module(wid))['actions'].items():
        fr = frames_of(wid, act)
        if not fr:
            continue
        step = A.get('step', 1)
        tmp = os.path.join(OUT, wid, 'ego', act, '_lab')
        os.makedirs(tmp, exist_ok=True)
        for i, p in enumerate(fr):
            n = int(os.path.basename(p)[:4])
            cur = [nm for f0, nm in A.get('events', []) if f0 <= n < f0 + 8]
            cmd = ['magick', p, '-font', FONT, '-fill', '#14171A', '-pointsize', '18', '-annotate', '+16+30',
                   f'{wid} · Ego · {act}', '-fill', '#2C3036', '-pointsize', '15', '-annotate', '+16+54',
                   f'Bild {n} · {n * 1000 / 30:.0f} ms · 30 fps']
            if cur:
                cmd += ['-fill', '#B4470F', '-pointsize', '19', '-gravity', 'NorthEast', '-annotate', '+16+30', '> ' + cur[-1]]
            subprocess.run(cmd + [os.path.join(tmp, f'{i:04d}.png')], check=True)
        out = os.path.join(dst, f'ego_{wid}_{act}.mp4')
        r = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', f'{30 / step:g}', '-i', os.path.join(tmp, '%04d.png'),
                            '-vf', 'format=yuv420p', '-c:v', 'libx264', '-crf', '22', '-movflags', '+faststart', out],
                           capture_output=True, text=True)
        for q in glob.glob(os.path.join(tmp, '*.png')):
            os.remove(q)
        os.rmdir(tmp)
        if r.returncode == 0:
            made[os.path.basename(out)] = os.path.getsize(out)
        else:
            print('Fehler', act, r.stderr[-300:])
    j = os.path.join(dst, 'clips.json')
    allc = json.load(open(j)) if os.path.exists(j) else {}
    allc.update(made)
    json.dump(allc, open(j, 'w'), indent=1)
    print(f'{len(made)} Ego-Clips in {dst}')


def sheets(wid):
    tmp = os.path.join(EVIDENCE, '_ego_tiles')
    os.makedirs(tmp, exist_ok=True)
    for act, A in EG.profile(module(wid))['actions'].items():
        fr = frames_of(wid, act)
        if not fr:
            continue
        nums = [int(os.path.basename(p)[:4]) for p in fr]
        names = {f: n for f, n in A.get('events', [])}
        keys = sorted({0, A['frames'], A['frames'] // 2, *names})
        tiles = []
        for k in keys:
            i = min(range(len(nums)), key=lambda j: abs(nums[j] - k))
            o = os.path.join(tmp, f'{act}_{k:04d}.png')
            subprocess.run(['magick', fr[i], '-resize', '400x', o], check=True)
            tiles += ['-label', f"Bild {nums[i]} · {names.get(k, 'Start' if k == 0 else ('Ende' if k == A['frames'] else 'Mitte'))}", o]
        res = os.path.join(EVIDENCE, f'ego_{wid}_{act}.png')
        subprocess.run(['magick', 'montage', *tiles, '-tile', 'x1', '-geometry', '+3+3', '-pointsize', '12', '-background', BG,
                        '-title', f'{wid} · {act} · {A["de"]}', res], check=True)
    print('Kontaktbögen in', EVIDENCE)


def _src_table(W):
    """Klassen- und Spielwerte einer Waffe mit Herkunft (M gemessen, E entworfen, T Toolgen, S Sekundärquelle)."""
    P = EG.profile(W)
    from tools import export_unity as XU
    G = XU.gameplay(P['type'], P['gameplay'])
    C = EG.CLASSES[P['type']]
    H = G['hip']
    rows = [('Klasse', P['type'], P['src']),
            ('Kadenz', f"{G['rpm']}/min", G['src']), ('Magazin', str(G['magazine']), G['src']),
            ('Feuerart', f"`{P['fire_mode']}` – {EG.FIRE_MODES[P['fire_mode']]}", 'Spec (META fire, data/specs); Unity: gameplay.fire_mode (0.20)'),
            ('Weltzoom im Zielen', 'kein Zielen (Werkzeug ohne Visier)' if G['sight'] == 'none' else f"{G['world_zoom']:g}" + (f", beginnt bei {G['zoom_start'] * 100:.0f} % des Augenwegs" if 'zoom_start' in G else ''),
             'M Glidepath (Entscheidungsliste 1.2 A, basic/reticles.py › CLASS_ZOOM)' + ('; Beginn E (1d, siehe Kadenz)' if 'zoom_start' in G else '')),
            ('Hüft-Fadenkreuz', 'kein Hüftzeichen' if H['kind'] == 'none' else f"{H['kind']} {H['share_h'] * 100:.1f} % H", f"{H['status']} (4.1 A / 4.2 A, basic/reticles.py › {'HUD_HIP' if P['type'] in RT.HUD_HIP else 'HIP'})"),
            ('Sprint-Fadenkreuz', H['sprint']['kind'] or 'aus', 'basic/reticles.py › HIP.sprint (4.1 A)')]
    if G['sight_form']['kind'] != H['kind'] and RT.SIGHT_KIND.get(P['type']) != 'pins':   # 0.33: Sonderklassen – das Absehen im Glas
        # behält die Form des Waffenmodells (der Bogen zielt über Pins, ohne gezeichnetes Absehen)
        rows.append(('Absehen im Glas', f"{G['sight_form']['kind']} {G['sight_form']['share_h'] * 100:.1f} % H",
                     'basic/reticles.py › HIP (common.drawn_reticle, Teil des Modells); Unity: gameplay.sight_form'))
    if G['burst_shots']:                         # 0.22: Salve je Klasse
        rows.append(('Salve', f"{G['burst_shots']} Schuss je Zug, {G['burst_rpm']}/min in der Salve ({60 / G['burst_rpm']:.3f} s), Salvenbeginn alle "
                              f"{G['burst_shots'] * 60 / G['rpm']:.3f} s; gehalten Salve um Salve", 'Länge aus der Spec (META fire), Takt und Folge: ' + G['src']))
    if G['portals']:                             # 0.22: Werkzeug
        rows.append(('Bedienung', '; '.join(f"Portal {q['name']} {'Linksklick' if q['input'] == 'fire' else 'Rechtsklick'} ({q['color']}, Ring "
                                            f"{'im' if q['ring'] > 0 else 'gegen den'} Uhrzeigersinn)" for q in G['portals'])
                     + f"; kein Zielen, kein Nachladen; Ring 120° in {G['ring_turn_s']:.3f} s; Reichweite {G['range_m']:g} m", C['src']))
    if P['drop']:
        rows.append(('Ohne', 'Aktionen ' + ', '.join(f'`{a}`' for a in P['drop']['actions']) + '; Haltungen ' +
                     ', '.join(f'`{a}`' for a in P['drop']['poses']), P['drop']['src']))
    rows.append(('Bahnstufe je Schuss', f"{G['path_up_h'] * 100:.2f} % H", G['src'] if G['path_up_h'] != EG.RECOIL['path_up_h'] else
                 'ego.RECOIL (gemeinsam, Automatik ≈ 1 % H je Schuss, 5.2 A)'))
    for k in list(C['poses']) + list(C.get('keep', {})):
        q = P['poses'][k]
        at = (f"Socket_Hand {list(q['pos'])}, Ziel {list(q['aim'])}" if 'pos' in q else    # Bogen (0.33): Zielen über den Augenpunkt
              f"Auge {list(q['eye'])}, Blickrichtung {list(q['aim_dir'])}")
        rows.append((f'Haltung `{k}`', f"{at}, Rollen {q['roll']}°", q['src']))
    for k in EG.FOLLOW_HIP:
        if 'hip' in C['poses'] and k not in C['poses']:
            q = P['poses'][k]
            rows.append((f'Haltung `{k}`', f"Socket_Hand {list(q['pos'])}, Rollen {q['roll']}°", q['src']))
    for k, n in C['frames'].items():
        rows.append((f'Dauer `{k}`', f"{n:g} Bilder bei 30/s ({n / 30:.3f} s)", C['frames_src']))
    hid = [p['id'] for p in W.PARTS if p.get('ads_hide')]
    if hid:
        rows.append(('Zielfernrohr im Zielen', f"aus: {', '.join(hid)} (Socket_Eye < {EG.ADS_HIDE['eye_m'] * 1000:.0f} mm)", EG.ADS_HIDE['src']))
    E = getattr(W, 'EJECT', None)
    rows += [('Mündungsfeuer', f"{EG.FLASH['dur_s'] * 1000:.0f} ms" if G['muzzle_flash'] else 'keins (Werkzeug)', EG.FLASH['src'] if G['muzzle_flash'] else G['src']),
             ('Hülsen', f"{E['case']} ({EG.EJECT['cases'][E['case']]['len_mm']} × {EG.EJECT['cases'][E['case']]['r_mm'] * 2:g} mm)" if E else 'keine',
              (E['src'] + '; Bahn: ' + EG.EJECT['src']) if E else 'Waffe ohne Feld EJECT'),
             ('Rückstoß', 'ego.RECOIL (gemeinsam)', ('M Destiny-Automatik: ' if P['type'] == 'auto_rifle' else 'übertragen von der Automatik: ')
              + 'Säule 1 % H je Schuss, im Zielen wandert die Welt (5.1 A / 5.2 A)'
              + ('' if P['type'] == 'auto_rifle' else '; Destiny-MP: Kick im Zielen ≤ 1 % H, Kamera-Anstieg < 2 % [M, ein PvP-Clip], '
                                                       'keine Klassenmessung der Bahn' if P['type'] == 'submachine_gun' else
                 '; Destiny-Scout Tone Patrol: kräftiger Einzelimpuls, Rest wächst vor den Folgeschüssen, im Zielen fünf Schüsse ≈ 6 % H '
                 '[M] (Motiongen rueckstoss › 4) – hier dieselbe Säule je Schuss, Salve = Schüsse im Abstand ≤ 1,5 × 60/rpm' if P['type'] == 'scout_rifle' else
                 '; Destiny-Impuls Gridskipper: Stufe ≈ 4 pp H je Salve, Erholung in der Pause, im Zielen Welt ≈ 5 pp H, Visier < 1 pp [M] '
                 '(Motiongen rueckstoss › r-d2-gridskipper) – Bahnstufe der Klasse, zweistufig' if P['type'] == 'pulse_rifle' else
                 '; Werkzeug: Modellkick der Aktion (fire_a/fire_b kick 0,6), keine Bahnstufe (E; Portal 2: obere Klaue ≈ 7 % H im ersten '
                 'Schussbild)')),
             ('Wirkung', _fx_text(EG.payload(P['type'])), EG.payload(P['type'])['src'] + ' (ego.PAYLOAD, Entscheidungsliste Block 9)'),
             ('Sprint-Frequenz', '3,16 / 1,58 Hz (gemeinsam)', 'M Destiny Automatik/Handfeuerwaffe, für alle Klassen bis zu neuen Messungen (3c)'),
             ('Griffe', ', '.join(P['grips']), 'Modul-Feld EGO_GRIPS' if getattr(W, 'EGO_GRIPS', None) else 'ego.GRIPS (Pilotwaffe)'),
             ('Live-Teile', ', '.join(f'{k} = {_live_text(v)}' for k, v in P['live'].items()), 'Modul-Feld EGO_LIVE' if getattr(W, 'EGO_LIVE', None) else 'ego.LIVE (Pilotwaffe)')]
    return ['| Wert | Stand | Herkunft |', '|---|---|---|'] + [f'| {a} | {b} | {c} |' for a, b, c in rows]


def docs(_wid=None):
    rv_all = json.load(open(os.path.join(ROOT, 'data', 'review.json'), encoding='utf-8'))
    clips_j = os.path.join(EVIDENCE, 'clips', 'clips.json')
    clipset = json.load(open(clips_j)) if os.path.exists(clips_j) else {}
    Ws = [importlib.import_module(f'basic.{m}') for m in WEAPONS]
    L = ['<!-- erzeugt von tools/make_ego.py docs – nicht von Hand ändern -->', '',
         '# Ego-Haltungen und Aktionen', '',
         'Eigenes Roboterarm-Rig (`basic/arms/robot_arm.py`) und Ego-Daten (`basic/arms/ego.py`), getrennt von Toolgen und Cube Escape. '
         'Kamera 75° horizontal (16:9), 30 fps, Kameraraum: rechts −X, vorn −Y, oben +Z. Herkunft: **T** Toolgen-Startwert, '
         '**M** gemessen an Destiny 2, **E** entworfen, **S** Sekundärquelle (Menü, Datenbank). Handgelenk-Ziel 45°, Grenze 55° (Toolgen).', '',
         'Spielbare Waffen (Taste ' + ', '.join(f'{(i + 1) % 10} = {EG.weapon_id(W)}' for i, W in enumerate(Ws)) + '). Haltungen, Dauer und '
         'Spielwerte je Klasse aus `ego.CLASSES` (Entscheidungsliste Schritt 6); was eine Klasse nicht nennt, gilt wie bei der Automatik.', '']
    for W in Ws:
        wid = EG.weapon_id(W)
        P = EG.profile(W)
        mp = os.path.join(OUT, wid, 'ego', 'ego.json')
        M = json.load(open(mp, encoding='utf-8')) if os.path.exists(mp) else dict(poses={}, actions={})
        rv = rv_all.get(f'{wid}-ego', {}).get('actions', {})
        L += [f'## {wid} – {W.META["name"]} ({P["type"]})', '', '### Klassen- und Spielwerte', ''] + _src_table(W)
        L += ['', '### Haltungen', '', '| Haltung | Socket_Hand (m) | Handgelenk max | Herkunft |', '|---|---|---|---|']
        for k, Q in P['poses'].items():
            m = M['poses'].get(k, {})
            wb = f"{m['wrist_bend_max_deg']}°" if 'wrist_bend_max_deg' in m else 'nur in Aktionen geprüft'
            L.append(f"| `{k}` | {m.get('socket_hand_m', list(Q.get('pos', Q.get('eye'))))} | {wb} | {Q['src']} |")
        L += ['', '### Aktionen', '', '| Aktion | Beschreibung | Bilder | Marker (Bild) | Handgelenk max | Clip | Sichtung | Herkunft |',
              '|---|---|---|---|---|---|---|---|']
        for k, A in P['actions'].items():
            m = M['actions'].get(k, {})
            ev = ', '.join(f'{n} ({f})' for f, n in A.get('events', [])) or '–'
            clip = f'ego_{wid}_{k}.mp4' if f'ego_{wid}_{k}.mp4' in clipset else 'offen'
            sv = rv.get(k, {})
            L.append(f"| `{k}` | {A['de']} | {A['frames']} ({A['frames'] / 30:.2f} s) | {ev} | {m.get('wrist_bend_max_deg', 'offen')}° | "
                     f"{clip} | {sv.get('status', 'offen')}{(': ' + sv['method']) if sv.get('method') else ''} | {A['src']} |")
        L += ['', '### Abdeckung der Matrixzeilen', '', '| Zeile | durch Aktion | Status |', '|---|---|---|']
        rows = {r: a for a, rs in EG.ROWS.items() for r in rs if a in P['actions']}
        for r, a in rows.items():
            st = 'dargestellt (mit Händen)' if rv.get(a, {}).get('status') == 'geprüft' else 'offen (nicht gesichtet)'
            L.append(f'| `{r}` | `{a}` | {st} |')
        L.append('')
    L += ['Clips: `~/Library/Caches/CubeEscapeBallon/evidence/clips/ego_<waffe>_<aktion>.mp4`; Kontaktbögen '
          '`…/evidence/ego_<waffe>_<aktion>.png`; Szene `…/out/<waffe>/ego/<waffe>_ego.blend`.', '']
    open(os.path.join(ROOT, 'docs', 'ego.md'), 'w', encoding='utf-8').write('\n'.join(L))
    print('docs/ego.md geschrieben')


def page(wid, path):
    """Ergebnisseite (eigenständiges HTML): Standbilder, eingebettete Clips (MP4 als data:), Haltungen, Hinweise."""
    import base64
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    from tools.make_sheets import CSS, FONTS, webp, fig, E as esc
    d = os.path.join(OUT, wid, 'ego')
    M = json.load(open(os.path.join(d, 'ego.json'), encoding='utf-8'))
    rv = json.load(open(os.path.join(ROOT, 'data', 'review.json'), encoding='utf-8')).get(f'{wid}-ego', {})
    st = lambda n, w=900, cap='': fig(webp(os.path.join(d, 'stills', n), w, 86), n, cap, aspect='16/9')  # noqa: E731
    poses = ''.join(st(f'{k}_ego.png', 640, f'<b>{esc(k)}</b> · Ego-Ansicht') for k in
                    ('hip', 'ads', 'sprint', 'lowered', 'crouch', 'reload', 'inspect_l', 'inspect_r'))
    outs = ''.join(st(f'{k}_out.png', 640, f'<b>{esc(k)}</b> · Außenansicht (Arme)') for k in ('hip', 'ads', 'reload', 'inspect_r'))
    vids = ''
    for k, A in EG.profile(module(wid))['actions'].items():
        mp = os.path.join(EVIDENCE, 'clips', f'ego_{wid}_{k}.mp4')
        if not os.path.exists(mp):
            continue
        b64 = base64.b64encode(open(mp, 'rb').read()).decode()
        ev = ', '.join(f'{n} {f}' for f, n in A.get('events', [])) or '–'
        s = rv.get('actions', {}).get(k, {})
        vids += (f'<figure><div class="plate" style="aspect-ratio:16/9"><video src="data:video/mp4;base64,{b64}" autoplay muted loop '
                 f'playsinline controls style="width:100%;height:100%;display:block"></video></div><figcaption><b>{esc(A["de"])}</b> · '
                 f'{A["frames"] / 30:.2f} s · Marker: {esc(ev)}<br><span class="muted">{esc(A["src"])} · Sichtung: '
                 f'{esc(s.get("status", "offen"))}</span></figcaption></figure>')
    notes = ''.join(f'<li>{esc(n)}</li>' for n in rv.get('notes', []))
    body = (f'<header class="head"><div style="display:grid;gap:10px"><span class="eyebrow">BASIC · Ego · {esc(wid)}</span>'
            '<h1>Roboterarme und Ego-Animationen</h1><p>Eigenes Arm-Rig im Stil v2.1 (Panzerplatten, dunkle Gelenke, drei Greiffinger und '
            'Daumen) und 19 Ego-Aktionen im Destiny-Stil an der Formstudie 01. Getrennt von Toolgen und Cube Escape; Maße und Zeiten mit '
            'Quelle übernommen.</p></div><div class="titleblock">'
            f'<div>Kamera</div><div>75° horizontal · 16:9 · 30 fps</div><div>Arme</div><div>Ober-/Unterarm 0,32/0,30 m (Toolgen)</div>'
            f'<div>Handgelenk</div><div>≤ 45° in allen Aktionen</div><div>Aktionen</div><div>{len(M["actions"])} · gesichtet '
            f'{sum(1 for v in rv.get("actions", {}).values() if v.get("status") == "geprüft")}</div>'
            '<div>Stand</div><div>Entwurf · gesichtet · nicht angebunden</div></div></header>'
            + st('hip_ego.png', 1500, '<b>Hüfte.</b> Griff unten rechts, Lauf zur Bildmitte, linke Hand am Handschutz.')
            + f'<section><h2>Abläufe</h2><div class="grid2">{vids}</div></section>'
            + f'<section><h2>Haltungen</h2><div class="grid4">{poses}</div></section>'
            + f'<section><h2>Arme von außen</h2><div class="grid4">{outs}</div></section>'
            + f'<section><h2>Hinweise</h2><ul style="display:grid;gap:6px">{notes}</ul></section>')
    from tools.make_sheets import page as pg
    open(path, 'w', encoding='utf-8').write(pg('BASIC Ego-Animationen', body, 'Roboterarme und Ego-Animationen'))
    print(path, f'{os.path.getsize(path) / 1e6:.1f} MB')


def check():
    err = []
    rows = {r[0] for r in matrix.ROWS} | {r for v in matrix.TYPE_ROWS.values() for r, _ in v} | {t[0] for t in matrix.TRANSITIONS}
    n = []
    for m in WEAPONS:
        W = importlib.import_module(f'basic.{m}')
        wid = EG.weapon_id(W)
        try:
            P = EG.profile(W)
        except KeyError as e:
            err.append(str(e))
            continue
        ids = {p['id'] for p in W.PARTS}
        for k, A in P['actions'].items():
            for f, key in A['weapon']:
                name = key if isinstance(key, str) else key[0]
                if name not in P['poses']:
                    err.append(f'{wid} {k}: Haltung {name} fehlt')
            for ch in ('L', 'R'):
                for f, key in A.get(ch, []):
                    g = key if isinstance(key, str) else key[0]
                    if g != 'cam' and g not in P['grips']:
                        err.append(f'{wid} {k}: Griff {g} fehlt')
            for ch in ('fL', 'fR'):
                for f, p in A.get(ch, []):
                    if p not in EG.FINGER_POSES:
                        err.append(f'{wid} {k}: Fingerstellung {p} fehlt')
            fr = [f for f, _ in A['weapon']]
            if fr != sorted(fr) or fr[-1] > A['frames']:
                err.append(f'{wid} {k}: Schlüsselbilder unsortiert oder hinter dem Ende')
            for pid in A.get('mech', {}):
                if pid not in ids:
                    err.append(f'{wid} {k}: Bauteil {pid} (mech) fehlt')
            for r in EG.ROWS.get(k, []):
                if r not in rows:
                    err.append(f'{k}: Matrixzeile {r} unbekannt')
        for g, G in P['grips'].items():
            for fp in [G['fingers_pose'], *G.get('finger_map', {}).values()]:
                if fp not in EG.FINGER_POSES:
                    err.append(f"{wid} Griff {g}: Fingerstellung {fp} fehlt")
            if G.get('part') and G['part'] not in ids:
                err.append(f"{wid} Griff {g}: Bauteil {G['part']} fehlt")
        want = set(EG.GRIPS) if not P['drop'] else {'grip', 'support'}   # Werkzeug ohne Nachladen (0.22): ohne Magazin- und Ladegriff
        named = {(k[0] if isinstance(k, tuple) else k) for A in P['actions'].values() for ch in ('L', 'R') for _, k in A.get(ch, [])}
        extra = set(P['grips']) - want - (named if P['drop'] else set(P['grips']))   # 0.33: Klassen dürfen weitere Griffe haben (MG: Deckel);
        if not want <= set(P['grips']) or extra:     # ohne Nachladen (drop) nur solche, die eine Aktion nennt (Bogen: Pfeil, Nockpunkt, P4)
            err.append(f'{wid}: Griffe {sorted(P["grips"])} statt {sorted(want)}')
        for k, v in P['live'].items():
            if k == 'rounds':                           # 0.34: Füllstand – Sätze von Teilen, Trommelteil
                v = [q for st in v.get('sets', ()) for q in st] + [v.get('drum', '')]
            for q in (v if k in ('glow', 'index', 'fill', 'rounds') else [v]):   # glow (0.33), index/fill (0.34): Teillisten
                if q and q not in ids:
                    err.append(f'{wid}: Live-Teil {k} = {q} fehlt')
                elif k in ('glow', 'fill') and q and next(p for p in W.PARTS if p['id'] == q).get('move', {}).get('kind') != 'glow':
                    err.append(f'{wid}: Leuchtteil {q} ohne Bewegung glow')
        used = {k for A in P['actions'].values() for ch in ('L', 'R') for _, k in A.get(ch, [])}
        for g in used:
            g = g[0] if isinstance(g, tuple) else g
            if g != 'cam' and g not in P['grips']:
                err.append(f'{wid}: Griff {g} in einer Aktion fehlt')
        n.append(f'{wid} {len(P["actions"])} Aktionen/{len(P["poses"])} Haltungen/{len(P["grips"])} Griffe')
    for nm, fp in EG.FINGER_POSES.items():
        if len(fp['f']) != len(RA.FINGER_X) or any(len(x) != len(RA.FINGER_LINKS) for x in fp['f']):
            err.append(f'Fingerstellung {nm}: {len(fp["f"])} Finger statt {len(RA.FINGER_X)}')
    print('\n'.join(err) if err else 'ego: ' + ', '.join(n) + ' konsistent')
    return 1 if err else 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if '--check' in a:
        sys.exit(check())
    if a[0] == 'page':
        page('BASIC-01-v2.1', a[1])
        sys.exit(0)
    wid = a[1] if len(a) > 1 else 'BASIC-01-v2.1'
    {'clips': clips, 'sheets': sheets, 'docs': docs}[a[0]](wid)
