"""Ego-Ausgaben: Clips, Kontaktbögen und Doku aus den Bildfolgen von tools/ego_build.py.

  python3 tools/make_ego.py clips   [Waffe]   → <EVIDENCE>/clips/ego_<waffe>_<aktion>.mp4 (854 × 480, Marker eingeblendet)
  python3 tools/make_ego.py sheets  [Waffe]   → <EVIDENCE>/ego_<waffe>_<aktion>.png (Start, Marker, Ende) – Grundlage der Sichtung
  python3 tools/make_ego.py docs    [Waffe]   → docs/ego.md (Haltungen, Aktionen, Marker, Gelenkprüfung, Sichtung)
  python3 tools/make_ego.py --check           → Ego-Daten konsistent (Haltungen, Griffe, Fingerstellungen, Matrixzeilen)
Standardwaffe: BASIC-01-v2.1 (Pilot).
"""
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools.paths import OUT, EVIDENCE  # noqa: E402
from basic.arms import ego as EG, robot_arm as RA  # noqa: E402
from basic import matrix  # noqa: E402

FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
BG = '#9EA4AC'


def frames_of(wid, act):
    return sorted(glob.glob(os.path.join(OUT, wid, 'ego', act, '[0-9]*.png')))


def clips(wid):
    dst = os.path.join(EVIDENCE, 'clips')
    os.makedirs(dst, exist_ok=True)
    made = {}
    for act, A in EG.ACTIONS.items():
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
    for act, A in EG.ACTIONS.items():
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


def docs(wid):
    mp = os.path.join(OUT, wid, 'ego', 'ego.json')
    M = json.load(open(mp, encoding='utf-8')) if os.path.exists(mp) else dict(poses={}, actions={})
    rv = json.load(open(os.path.join(ROOT, 'data', 'review.json'), encoding='utf-8')).get(f'{wid}-ego', {}).get('actions', {})
    clips_j = os.path.join(EVIDENCE, 'clips', 'clips.json')
    clipset = json.load(open(clips_j)) if os.path.exists(clips_j) else {}
    L = ['<!-- erzeugt von tools/make_ego.py docs – nicht von Hand ändern -->', '',
         f'# Ego-Haltungen und Aktionen – {wid}', '',
         'Eigenes Roboterarm-Rig (`basic/arms/robot_arm.py`) und Ego-Daten (`basic/arms/ego.py`), getrennt von Toolgen und Cube Escape. '
         'Kamera 75° horizontal (16:9), 30 fps, Kameraraum: rechts −X, vorn −Y, oben +Z. Herkunft: **T** Toolgen-Startwert, '
         '**M** gemessen an Destiny 2, **E** entworfen. Handgelenk-Ziel 45°, Grenze 55° (Toolgen).', '',
         '## Haltungen', '', '| Haltung | Socket_Hand (m) | Handgelenk max | Herkunft |', '|---|---|---|---|']
    for k, P in EG.POSES.items():
        m = M['poses'].get(k, {})
        wb = f"{m['wrist_bend_max_deg']}°" if 'wrist_bend_max_deg' in m else 'nur in Aktionen geprüft'
        L.append(f"| `{k}` | {m.get('socket_hand_m', list(P.get('pos', P.get('eye'))))} | {wb} | {P['src']} |")
    L += ['', '## Aktionen', '', '| Aktion | Beschreibung | Bilder | Marker (Bild) | Handgelenk max | Clip | Sichtung | Herkunft |',
          '|---|---|---|---|---|---|---|---|']
    for k, A in EG.ACTIONS.items():
        m = M['actions'].get(k, {})
        ev = ', '.join(f'{n} ({f})' for f, n in A.get('events', [])) or '–'
        clip = f'ego_{wid}_{k}.mp4' if f'ego_{wid}_{k}.mp4' in clipset else 'offen'
        s = rv.get(k, {})
        L.append(f"| `{k}` | {A['de']} | {A['frames']} ({A['frames'] / 30:.2f} s) | {ev} | {m.get('wrist_bend_max_deg', 'offen')}° | "
                 f"{clip} | {s.get('status', 'offen')}{(': ' + s['method']) if s.get('method') else ''} | {A['src']} |")
    L += ['', '## Abdeckung der Matrixzeilen (Pilot)', '', '| Zeile | durch Aktion | Status |', '|---|---|---|']
    rows = {r: a for a, rs in EG.ROWS.items() for r in rs}
    for r, a in rows.items():
        st = 'dargestellt (mit Händen)' if rv.get(a, {}).get('status') == 'geprüft' else 'offen (nicht gesichtet)'
        L.append(f'| `{r}` | `{a}` | {st} |')
    L += ['', 'Clips: `~/Library/Caches/CubeEscapeBallon/evidence/clips/ego_<waffe>_<aktion>.mp4`; Kontaktbögen '
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
    for k, A in EG.ACTIONS.items():
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
    for k, A in EG.ACTIONS.items():
        for f, key in A['weapon']:
            name = key if isinstance(key, str) else key[0]
            if name not in EG.POSES:
                err.append(f'{k}: Haltung {name} fehlt')
        for ch in ('L', 'R'):
            for f, key in A.get(ch, []):
                g = key if isinstance(key, str) else key[0]
                if g != 'cam' and g not in EG.GRIPS:
                    err.append(f'{k}: Griff {g} fehlt')
        for ch in ('fL', 'fR'):
            for f, p in A.get(ch, []):
                if p not in RA.FINGER_POSES:
                    err.append(f'{k}: Fingerstellung {p} fehlt')
        fr = [f for f, _ in A['weapon']]
        if fr != sorted(fr) or fr[-1] > A['frames']:
            err.append(f'{k}: Schlüsselbilder unsortiert oder hinter dem Ende')
        for r in EG.ROWS.get(k, []):
            if r not in rows:
                err.append(f'{k}: Matrixzeile {r} unbekannt')
    for n, fp in RA.FINGER_POSES.items():
        if len(fp['f']) != len(RA.FINGER_X) or any(len(x) != len(RA.FINGER_LINKS) for x in fp['f']):
            err.append(f'Fingerstellung {n}: {len(fp["f"])} Finger statt {len(RA.FINGER_X)}')
    for g in EG.GRIPS.values():
        if g['fingers_pose'] not in RA.FINGER_POSES:
            err.append(f"Griff: Fingerstellung {g['fingers_pose']} fehlt")
    print('\n'.join(err) if err else f'ego: {len(EG.ACTIONS)} Aktionen, {len(EG.POSES)} Haltungen, {len(EG.GRIPS)} Griffe konsistent')
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
