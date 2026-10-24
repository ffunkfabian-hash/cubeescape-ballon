"""Unity-Läufe für unity/ (0.4 „Firstfeel“), jeweils unter `ce lock unity`; Protokolle und Belege unter
~/Library/Caches/CubeEscapeBallon/unity/.

  python3 tools/unity_run.py setup      → URP, Ebene, Eingabe, Materialien, Szene (nach jedem Export)
  python3 tools/unity_run.py test       → EditMode- und PlayMode-Tests (JUnit-XML + Kurzfassung)
  python3 tools/unity_run.py build      → macOS-Entwicklungsbuild unity/Build/BallonFirstfeel.app
  python3 tools/unity_run.py capture    → Ablauf als PNG-Folge aus der Build, MP4 720p mit Markern
  python3 tools/unity_run.py compare    → Standbilder hip/ads/reload/inspect_r aus der Build, Vergleich mit Blender (SSIM/PSNR)
  python3 tools/unity_run.py bench      → Bildzeiten im Parcours (ohne VSync, 10 s Vorführablauf)
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJ = os.path.join(ROOT, 'unity')
UNITY = os.environ.get('UNITY_EDITOR', '/Applications/Unity/Hub/Editor/6000.6.2f1/Unity.app/Contents/MacOS/Unity')
LOCK = os.path.expanduser('~/Claude/cubeescape-nexogen/ce')
EV = os.environ.get('BALLON_UNITY_EVIDENCE', os.path.expanduser('~/Library/Caches/CubeEscapeBallon/unity'))
APP = os.path.join(PROJ, 'Build', 'BallonFirstfeel.app')
# frische Blender-Stills für den Vergleich (eigener Ausgabeort, damit fremde Renderings unberührt bleiben):
#   BASIC_OUT=<EV>/blender_out ce lock gpu -- blender -b --factory-startup -P <abs>/tools/ego_build.py -- --stills --gpu
BLENDER_STILLS = os.path.join(EV, 'blender_out', 'BASIC-01-v2.1', 'ego', 'stills')
CE = os.path.expanduser('~/Claude/cubeescape-nexogen/ce')
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'


def locked(cmd, log=None):
    print('»', ' '.join(cmd[:3]), '…')
    r = subprocess.run([LOCK, 'lock', 'unity', '--'] + cmd)
    if log and os.path.exists(log):
        bad = [ln for ln in open(log, encoding='utf-8', errors='replace') if 'error CS' in ln or 'Aborting batchmode' in ln]
        if bad:
            print(''.join(bad[:20]))
    return r.returncode


def editor(method, name):
    log = os.path.join(EV, f'{name}.log')
    return locked([UNITY, '-batchmode', '-quit', '-projectPath', PROJ, '-executeMethod', method, '-logFile', log], log)


def tests():
    rc = 0
    for plat in ('EditMode', 'PlayMode'):
        res = os.path.join(EV, f'tests_{plat}.xml')
        log = os.path.join(EV, f'tests_{plat}.log')
        if os.path.exists(res):
            os.remove(res)
        code = locked([UNITY, '-batchmode', '-projectPath', PROJ, '-runTests', '-testPlatform', plat, '-testResults', res, '-logFile', log],
                      log)
        if not os.path.exists(res):
            print(f'{plat}: keine Ergebnisse (Protokoll {log})')
            rc = 1
            continue
        t = ET.parse(res).getroot()
        total = int(t.get('total', 0))
        if code or t.get('result', '').split('(')[0] != 'Passed' or total == 0:
            print(f"{plat}: Unity-Lauf Exit {code}, Ergebnis {t.get('result')}, {total} Tests – nicht grün")
            rc = 1
        print(f"{plat}: {t.get('passed')} bestanden, {t.get('failed')} fehlgeschlagen, {t.get('skipped', '0')} übersprungen "
              f"({float(t.get('duration', 0)):.1f} s)")
        for c in t.iter('test-case'):
            out = c.find('output')
            msg = c.find('failure/message')
            if c.get('result') != 'Passed':
                rc = 1
                print('  ✗', c.get('name'), (msg.text or '').strip()[:400] if msg is not None else '')
            elif out is not None and out.text:
                lines = [ln for ln in out.text.strip().splitlines() if not ln.startswith('Saving results')]
                if lines:
                    print('  ✓', c.get('name'), '–', lines[-1][:200])
    return rc


def player(args, log):
    exe = os.path.join(APP, 'Contents', 'MacOS', 'BALLON Firstfeel')
    if not os.path.exists(exe):
        print('Build fehlt: python3 tools/unity_run.py build')
        return 1
    return locked([exe, '-screen-width', '1280', '-screen-height', '720', '-screen-fullscreen', '0', '-logFile', log] + args, log)


def capture():
    d = os.path.join(EV, 'capture')
    shutil.rmtree(d, ignore_errors=True)
    rc = player(['-ballonCapture', d], os.path.join(EV, 'capture.log'))
    frames = sorted(glob.glob(os.path.join(d, '[0-9]*.png')))
    if rc or not frames:
        print('Aufnahme fehlgeschlagen', rc)
        return 1
    marks = {}
    for ln in open(os.path.join(d, 'markers.csv'), encoding='utf-8'):
        f, a, m = ln.strip().split(',', 2)
        if a != 'shot':
            marks.setdefault(int(f), []).append(f'{a} › {m}')
    rows = {int(r.split(',')[0]): r.strip().split(',') for r in open(os.path.join(d, 'frames.csv'), encoding='utf-8')}
    lab = os.path.join(d, '_lab')
    os.makedirs(lab, exist_ok=True)
    cur, until = '', -1
    for i, p in enumerate(frames):
        if i in marks:
            cur, until = marks[i][-1], i + 18
        _, act, fr, ammo = rows.get(i, [i, '', '', ''])
        cmd = ['magick', p, '-font', FONT, '-fill', '#F2F3F4', '-stroke', '#00000060', '-pointsize', '20', '-annotate', '+18+34',
               'BALLON 0.4 Firstfeel · Unity · BASIC-01 v2.1', '-pointsize', '16', '-annotate', '+18+58',
               f'Bild {i} · {i * 1000 / 30:.0f} ms · {act} {fr}', '-gravity', 'SouthEast', '-pointsize', '30', '-annotate', '+26+22',
               f'{ammo} / 30', '-gravity', 'Center', '-stroke', 'none', '-fill', '#FFFFFFD0', '-draw', 'rectangle 628,359 638,361',
               '-draw', 'rectangle 642,359 652,361', '-draw', 'rectangle 639,346 641,356', '-draw', 'rectangle 639,364 641,374']
        if i <= until and cur:
            cmd += ['-gravity', 'NorthEast', '-fill', '#FFB070', '-pointsize', '22', '-annotate', '+20+34', '› ' + cur.split(' › ')[-1]]
        subprocess.run(cmd + [os.path.join(lab, f'{i:04d}.png')], check=True)
    out = os.path.join(EV, 'firstfeel_ablauf.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '30', '-i', os.path.join(lab, '%04d.png'), '-vf', 'format=yuv420p',
                    '-c:v', 'libx264', '-crf', '20', '-movflags', '+faststart', out], check=True)
    shutil.rmtree(lab)
    sheet = os.path.join(EV, 'firstfeel_ablauf.png')
    pick = sorted({0, len(frames) - 1, *[f for f in marks if any(k in ' '.join(marks[f]) for k in
                                                                  ('Aimed', 'MagOut', 'MagIn', 'Chamber', 'inspect › Start'))]})
    subprocess.run(['magick', 'montage', *[x for f in pick for x in ('-label', f'Bild {f} · {" / ".join(marks.get(f, ["Start/Ende"]))}',
                                                                        frames[f])],
                    '-tile', '4x', '-geometry', '480x270+3+3', '-pointsize', '12', '-background', '#9EA4AC',
                    '-title', 'BALLON 0.4 Firstfeel · Zielen → Feuerstoß → leeres Nachladen → Betrachten (Unity-Build)', sheet], check=True)
    print(f'{len(frames)} Bilder ({len(frames) / 30:.1f} s) → {out}\nKontaktbogen → {sheet}')
    return 0


def lum(path):
    r = subprocess.run(['magick', path, '-alpha', 'off', '-colorspace', 'Gray', '-format', '%[fx:mean]', 'info:'],
                       capture_output=True, text=True)
    return float(r.stdout or 0)


def metrics(u, b):
    """SSIM (ImageMagick 7 meldet 1 − SSIM), PSNR und mittlere Helligkeit beider Bilder."""
    rgb = os.path.join(os.path.dirname(u), '_ref.png')          # Blender-PNG hat Alpha: für den Vergleich auf RGB
    subprocess.run(['magick', b, '-alpha', 'off', rgb], check=True)

    def m(kind):
        return subprocess.run(['magick', 'compare', '-metric', kind, u, rgb, 'null:'], capture_output=True, text=True).stderr.strip()
    dssim = float(m('SSIM').split('(')[1].rstrip(')'))
    return dict(ssim=round(1 - dssim, 4), psnr_db=round(float(m('PSNR').split()[0]), 2),
                lum_unity=round(lum(u), 4), lum_blender=round(lum(b), 4))


def compare(extra=()):
    d = os.path.join(EV, 'compare')
    shutil.rmtree(d, ignore_errors=True)
    rc = player(['-ballonCompare', d] + list(extra), os.path.join(EV, 'compare.log'))
    if rc:
        return rc
    tiles, mets = [], {}
    for pose in ('hip', 'ads', 'reload', 'inspect_r'):
        u = os.path.join(d, f'{pose}_unity.png')
        b = os.path.join(BLENDER_STILLS, f'{pose}_ego.png')
        if not (os.path.exists(u) and os.path.exists(b)):
            print('fehlt:', u if not os.path.exists(u) else b)
            continue
        edge = os.path.join(d, f'{pose}_kanten.png')
        # Kanten des Blender-Bildes (orange) über dem Unity-Bild: Deckung der Silhouetten
        subprocess.run(['magick', u, '(', b, '-colorspace', 'gray', '-blur', '0x1', '-edge', '1', '-threshold', '18%',
                        '-fill', '#FF7A1A', '-opaque', 'white', '-transparent', 'black', ')', '-composite', edge], check=True)
        mix = os.path.join(d, f'{pose}_mischung.png')
        subprocess.run(['magick', u, b, '-compose', 'blend', '-define', 'compose:args=50', '-composite', mix], check=True)
        m = mets[pose] = metrics(u, b)
        print(f"  {pose}: SSIM {m['ssim']}, PSNR {m['psnr_db']} dB, Helligkeit Unity {m['lum_unity']} / Blender {m['lum_blender']}")
        tiles += ['-label', f'{pose} · Blender (Cycles)', b, '-label', f"{pose} · Unity (URP) · SSIM {m['ssim']}", u,
                  '-label', f'{pose} · Blender-Kanten über Unity', edge]
    sheet = os.path.join(EV, 'firstfeel_vergleich.png')
    subprocess.run(['magick', 'montage', *tiles, '-tile', '3x', '-geometry', '600x338+3+3', '-pointsize', '14', '-background', '#9EA4AC',
                    '-title', 'BALLON 0.4 · Standbildvergleich Blender gegen Unity (gleiche Haltung, Kamera 75° horizontal)', sheet],
                   check=True)
    json.dump(mets, open(os.path.join(d, 'metrics.json'), 'w'), indent=1)
    print('Vergleich →', sheet)
    return 0


if __name__ == '__main__':
    os.makedirs(EV, exist_ok=True)
    a = sys.argv[1] if len(sys.argv) > 1 else ''
    if a == 'setup':
        sys.exit(editor('Ballon.Ego.Editor.BallonSetup.Run', 'setup'))
    if a == 'build':
        sys.exit(editor('Ballon.Ego.Editor.BallonSetup.BuildMac', 'build'))
    if a == 'test':
        sys.exit(tests())
    if a == 'capture':
        sys.exit(capture())
    if a == 'bench':
        f = os.path.join(EV, 'bench.json')
        rc = player(['-ballonBench', f], os.path.join(EV, 'bench.log'))
        print(open(f).read() if os.path.exists(f) else 'keine Messung')
        sys.exit(rc)
    if a == 'compare':
        sys.exit(compare(sys.argv[2:]))
    print(__doc__)
