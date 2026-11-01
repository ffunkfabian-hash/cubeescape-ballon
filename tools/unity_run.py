"""Unity-Läufe für unity/ (0.4 „Firstfeel“), jeweils unter `ce lock unity`; Protokolle und Belege unter
~/Library/Caches/CubeEscapeBallon/unity/.

  python3 tools/unity_run.py setup      → URP, Ebene, Eingabe, Materialien, Szene (nach jedem Export)
  python3 tools/unity_run.py test       → EditMode- und PlayMode-Tests (JUnit-XML + Kurzfassung; BALLON_TEST_FILTER=Name|Name: nur diese)
  python3 tools/unity_run.py build      → macOS-Entwicklungsbuild unity/Build/BallonFirstfeel.app
  python3 tools/unity_run.py capture    → Ablauf als PNG-Folge aus der Build, MP4 720p mit Markern
  python3 tools/unity_run.py compare [n] → Standbilder hip/ads/reload/inspect_r aus der Build, Vergleich mit Blender (SSIM/PSNR); n = Waffe
      (Taste, 0.18; Blender-Stills aus BALLON_BLENDER_STILLS, sonst <EV>/blender_out/<Waffe>/ego/stills)
  python3 tools/unity_run.py sway|treffer → Belege Pendeln bzw. Schuss-Ring/Treffer-X (MP4, Kontaktbogen, feedback.csv)
  python3 tools/unity_run.py huefte    → Beleg Hüft-Fadenkreuz (0.13): Hüfte, Feuer, Zielen, Sprint, Nachladen (MP4, feedback.csv)
  python3 tools/unity_run.py sprint|wechsel|rueckstoss → Belege 0.15: Sprint-Hub und Sprint → Zielen, Waffenwechsel, Rückstoß im Zielen
  python3 tools/unity_run.py feuer → Beleg 0.16: Mündungsfeuer und Hülsen aus der Hüfte und im Zielen
  python3 tools/unity_run.py quickdraw → Beleg 0.18: Automatik Hüfte/Zielen, Taste 2 → MP, MP Hüfte/Zielen/Sprint
  python3 tools/unity_run.py spotter   → Beleg 0.20: Automatik, Taste 3 → Scout, Hüfte, Zielfernrohr mit Einzelfeuer, Sprint
  python3 tools/unity_run.py holdfast  → Beleg 0.36: Hüfte Automatik/Impuls/Scout, Handfeuerwaffe Schuss, Raketenwerfer Zielen, Bogen
      Spannen/Zielen (zoom.csv: Weltzoom je Bild, feedback.csv: Hüftzeichen sichtbar/Grund)
      (BALLON_CAPTURE_EXTRA="-ballonFps 60 -ballonKey 1": Messlauf mit Schlüsselfarbe in eigenem Ordner …_mess)
  python3 tools/unity_run.py bench      → Bildzeiten im Parcours (ohne VSync, 10 s Vorführablauf)
  python3 tools/unity_run.py ruckeln <name> [profil] → Ruckelmessung 0.37: je Waffe Wechsel, Hüftschuss, Dauerfeuer, Zielen, Nachladen, Bewegen,
      zwei Durchgänge (erster Einsatz/Wiederholung), Spieleinstellungen (VSync); <EV>/ruckeln/<name>/frames.csv + Tabelle
      (tools/stutter_report.py); „profil“: Profiler-Protokoll je Waffe, Ursachen der Spitzen ≥ 25 ms in spikes.json;
      „kalt“ (0.38): Kopie der Build mit eigener Bundle-ID = leerer Metal-Shader-Zwischenspeicher wie beim ersten Start einer
      neuen Build (Kopie und ihr Zwischenspeicher werden danach gelöscht); „einmal“: nur Durchgang 1; „laden“: nur Laden und
      3 s Ruhe (Ladezeit, ≈ 15 s)
  python3 tools/unity_run.py aufwaermen → Shader-Zustände für das Aufwärmen aufzeichnen (0.38): Ruckelmessung mit -ballonGscRecord,
      Sammlung nach Assets/Ballon/Warmup/, in die Szene, neue Build (nach Änderungen an Shadern, Materialien, Effekten)
  python3 tools/unity_run.py skins      → Kontaktbogen aller Waffen-Skins (hip, inspect_l) aus der Build
  python3 tools/unity_run.py fov        → Beleg A9 (0.32): Hüfte/Zielen bei Welt 60/75/100°, Wand 12 cm vor dem Auge
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
APP = os.environ.get('BALLON_UNITY_APP', os.path.join(PROJ, 'Build', 'BallonFirstfeel.app'))   # andere Build (0.37: vorher/nachher)
# frische Blender-Stills für den Vergleich (eigener Ausgabeort, damit fremde Renderings unberührt bleiben):
#   BASIC_OUT=<EV>/blender_out ce lock gpu -- blender -b --factory-startup -P <abs>/tools/ego_build.py -- --stills --gpu
CE = os.path.expanduser('~/Claude/cubeescape-nexogen/ce')
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'


def locked(cmd, log=None):
    print('»', ' '.join(cmd[:3]), '…')
    what = os.environ.get('BALLON_LOCK_WHAT')          # Sitzung und Schritt für `ce lock status` (heavy_lock --what)
    r = subprocess.run([LOCK, 'lock', 'unity'] + (['--what', what] if what else []) + ['--'] + cmd)
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
        filt = os.environ.get('BALLON_TEST_FILTER')     # Gegenproben: nur ausgewählte Tests (Unity -testFilter, Namen mit | getrennt)
        code = locked([UNITY, '-batchmode', '-projectPath', PROJ, '-runTests', '-testPlatform', plat, '-testResults', res, '-logFile', log]
                      + (['-testFilter', filt] if filt else []), log)
        if not os.path.exists(res):
            print(f'{plat}: keine Ergebnisse (Protokoll {log})')
            rc = 1
            continue
        t = ET.parse(res).getroot()
        total = int(t.get('total', 0))
        passed = int(t.get('passed', 0))
        if code or t.get('result', '').split('(')[0].split(':')[0] not in ('Passed', 'Skipped') or passed == 0 or t.get('failed') != '0':
            print(f"{plat}: Unity-Lauf Exit {code}, Ergebnis {t.get('result')}, {total} Tests, {passed} bestanden – nicht grün")
            rc = 1
        print(f"{plat}: {t.get('passed')} bestanden, {t.get('failed')} fehlgeschlagen, {t.get('skipped', '0')} übersprungen "
              f"({float(t.get('duration', 0)):.1f} s)")
        for c in t.iter('test-case'):
            out = c.find('output')
            msg = c.find('failure/message')
            if c.get('result') == 'Skipped':          # Assert.Ignore (z. B. „keine Szene exportiert“) ist kein Fehler
                print('  ⊘', c.get('name'), '–', (c.find('reason/message').text or '').strip()[:120] if c.find('reason/message') is not None else 'übersprungen')
            elif c.get('result') != 'Passed':
                rc = 1
                print('  ✗', c.get('name'), (msg.text or '').strip()[:400] if msg is not None else '')
            elif out is not None and out.text:
                lines = [ln for ln in out.text.strip().splitlines() if not ln.startswith('Saving results')]
                if lines:
                    print('  ✓', c.get('name'), '–', lines[-1][:200])
    return rc


def cold_copy(app, name):
    """Kopie der Build mit eigener Bundle-ID: macOS legt den Metal-Shader-Zwischenspeicher je Bundle-ID an, die Kopie startet also
    so kalt wie der erste Start einer neuen Build (0.37/0.38). APFS-Klon, neu signiert (ad hoc)."""
    bid = f'local.ballon.kalt.{name.lower().replace("_", "-")}.{os.getpid()}'
    dst = os.path.join(EV, 'kalt', f'{name}.app')
    shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    subprocess.run(['cp', '-cR', app, dst], check=True)
    subprocess.run(['plutil', '-replace', 'CFBundleIdentifier', '-string', bid, os.path.join(dst, 'Contents', 'Info.plist')], check=True)
    subprocess.run(['codesign', '--force', '--deep', '-s', '-', dst], check=True, capture_output=True)
    print('kalt:', bid)
    return dst, bid


def cold_cleanup(app, bid):
    """Kopie und den Zwischenspeicher ihrer Bundle-ID löschen (nur die eigene, eindeutige ID)."""
    shutil.rmtree(app, ignore_errors=True)
    cache = subprocess.run(['getconf', 'DARWIN_USER_CACHE_DIR'], capture_output=True, text=True).stdout.strip()
    if not bid.startswith('local.ballon.kalt.'):
        return
    for c in (os.path.join(cache, bid), os.path.expanduser(f'~/Library/Caches/{bid}')):
        shutil.rmtree(c, ignore_errors=True)
    prefs = os.path.expanduser(f'~/Library/Preferences/{bid}.plist')   # PlayerPrefs der Kopie
    if os.path.exists(prefs):
        os.remove(prefs)


def player(args, log):
    exe = os.path.join(APP, 'Contents', 'MacOS', 'BALLON Firstfeel')
    if not os.path.exists(exe):
        print('Build fehlt: python3 tools/unity_run.py build')
        return 1
    return locked([exe, '-screen-width', '1280', '-screen-height', '720', '-screen-fullscreen', '0', '-logFile', log] + args, log)


DEMOS = {'feel': 'BALLON 0.10 Stride · Unity · BASIC-01 v2.1 · Sprint, Zielen, Sprint → Zielen',
         'sway': 'BALLON Patch unity-abgleich · Unity · Pendeln: schnelle Drehung, Rückkehr ohne Überschwingen (2,5 Hz, ζ 1)',
         'treffer': 'BALLON Patch unity-abgleich · Unity · 720/min · Schuss-Ring im Zielen (1 Bild) · Treffer-X orange ≥ 0,17 s',
         'huefte': 'BALLON 0.13 Hipfire · Unity · Hüft-Fadenkreuz: Hüfte → Feuer → Zielen → Sprint („^“) → Nachladen',
         'sprint': 'BALLON 0.15 Plumb · Unity · Sprint-Hub ≈ 10 % H / 13 % B (3,16 Hz), Sprint → Zielen: Zoom mit dem Modell',
         'wechsel': 'BALLON 0.15 Plumb · Unity · Waffenwechsel (Q): Wegstecken 0,27 s, leere Sicht, Ziehen mit Nachfedern',
         'rueckstoss': 'BALLON 0.15 Plumb · Unity · Rückstoß: Hüfte, im Zielen Viererstöße und 12er-Stoß – Welt wandert, Visier steht',
         'feuer': 'BALLON 0.16 Flash · Unity · Mündungsfeuer (1 Bild bei 30/s) und Hülsen: Hüfte und Zielen',
         'quickdraw': 'BALLON 0.18 Quickdraw · Unity · Automatik → Taste 2 → MP: Hüfte, Zielen (Anflug 4d), Sprint (tief, nach links gerollt)',
         'spotter': 'BALLON 0.20 Spotter · Unity · Taste 3 → Scout: Hüfte, Zielfernrohr (Weltzoom 2,0), Einzelfeuer, Sprint',
         'volley': 'BALLON 0.22 Volley · Unity · 1 → 4 Impuls (Salve Hüfte/Zielen) → 5 Portalkanone (A links, B rechts) → 2 → 3 → 1',
         'projektil': 'BALLON 0.34 Payload · Unity · Granatwerfer (Bogen, Explosion, Laufrauch) → Raketenwerfer (gerade, Rauchspur)',
         'strahlen': 'BALLON 0.34 Payload · Unity · Spurgewehr (Dauerstrahl) → Fusion (Bolzen) → lineare Fusion (Strahl) → Bogen (Pfeil)',
         'streuschuss': 'BALLON 0.34 Payload · Unity · Schrot (Streukegel, Hüfte/Zielen) → Automatik → Handfeuerwaffe: Einschläge, Löcher',
         'fuellstand': 'BALLON 0.34 Payload · Unity · MG (Glieder, Gurt, Zählfenster) → Granatwerfer (Kammern) → Handfeuerwaffe (Trommel, Hülsen)',
         'holdfast': 'BALLON 0.36 Holdfast · Unity · Hüfte Automatik/Impuls/Scout, Handfeuerwaffe Schuss, Raketenwerfer Zielen, Bogen Spannen/Zielen'}
WEAPONS = {1: 'BASIC-01-v2.1', 2: 'BASIC-06-v2.1', 3: 'BASIC-03-v2.1', 4: 'BASIC-02-v2.1', 5: 'BASIC-T01-v2.1', 6: 'BASIC-04-v2.1',
           7: 'BASIC-05-v2.1', 8: 'BASIC-09-v2.1', 9: 'BASIC-12-v2.1', 10: 'BASIC-15-v2.1', 11: 'BASIC-08-v2.1', 12: 'BASIC-10-v2.1',
           13: 'BASIC-11-v2.1', 14: 'BASIC-07-v2.1', 15: 'BASIC-13-v2.1', 16: 'BASIC-14-v2.1'}   # Waffe n → ID (tools/export_unity.WEAPONS;
# 10 = Taste 0, 11–16 ohne Taste: Waffenmenü)


def capture(scene=None, demo=None):
    extra = os.environ.get('BALLON_CAPTURE_EXTRA', '').split()   # Messläufe: z. B. "-ballonFps 60 -ballonKey 1" (eigener Ordner, _mess)
    d = os.path.join(EV, 'capture' if not scene else f'capture_{scene}') + (f'_{demo}' if demo else '') + ('_mess' if extra else '')
    shutil.rmtree(d, ignore_errors=True)
    rc = player(['-ballonCapture', d] + (['-ballonScene', scene] if scene else []) + (['-ballonDemo', demo] if demo else []) + extra,
                os.path.join(EV, 'capture.log'))
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
    head = DEMOS[demo] if demo else 'BALLON 0.4 Firstfeel · Unity · BASIC-01 v2.1'
    cur, until = '', -1
    for i, p in enumerate(frames):
        if i in marks:
            cur, until = marks[i][-1], i + 18
        _, act, fr, ammo = rows.get(i, [i, '', '', ''])
        cmd = ['magick', p, '-font', FONT, '-fill', '#F2F3F4', '-stroke', '#00000060', '-pointsize', '20', '-annotate', '+18+34',
               head, '-pointsize', '16', '-annotate', '+18+58',
               f'Bild {i} · {i * 1000 / 30:.0f} ms · {act} {fr}', '-gravity', 'SouthEast', '-pointsize', '30', '-annotate', '+26+22',
               ammo if ('/' in ammo or ammo == '∞') else f'{ammo} / 30']   # 0.22: Bootstrap schreibt Munition / Magazin bzw. ∞
        if i <= until and cur:
            cmd += ['-gravity', 'NorthEast', '-fill', '#FFB070', '-pointsize', '22', '-annotate', '+20+34', '› ' + cur.split(' › ')[-1]]
        subprocess.run(cmd + [os.path.join(lab, f'{i:04d}.png')], check=True)
    stem = ('gefuehl' if demo == 'feel' else demo or '') + ('_mess' if extra else '')
    out = os.path.join(EV, f'{stem}_{scene or "parcours"}.mp4' if demo else 'firstfeel_ablauf.mp4' if not scene else f'firstfeel_{scene}.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '30', '-i', os.path.join(lab, '%04d.png'), '-vf', 'format=yuv420p',
                    '-c:v', 'libx264', '-crf', '20', '-movflags', '+faststart', out], check=True)
    shutil.rmtree(lab)
    sheet = os.path.join(EV, f'{stem}_{scene or "parcours"}.png' if demo else 'firstfeel_ablauf.png' if not scene else f'firstfeel_{scene}.png')
    pick = sorted({0, len(frames) - 1, *[f for f in marks if any(k in ' '.join(marks[f]) for k in
                                                                  ('Aimed', 'MagOut', 'MagIn', 'Chamber', 'inspect › Start'))]})
    if demo:                                                     # Bewegungsgefühl: gleichmäßig über den Ablauf
        pick = [round(k * (len(frames) - 1) / 11) for k in range(12)]
    subprocess.run(['magick', 'montage', *[x for f in pick for x in ('-label', f'Bild {f} · {" / ".join(marks.get(f, ["Start/Ende"]))}',
                                                                        frames[f])],
                    '-tile', '4x', '-geometry', '480x270+3+3', '-pointsize', '12', '-background', '#9EA4AC',
                    '-title', head if demo else 'BALLON 0.4 Firstfeel · Zielen → Feuerstoß → leeres Nachladen → Betrachten (Unity-Build)',
                    sheet], check=True)
    print(f'{len(frames)} Bilder ({len(frames) / 30:.1f} s) → {out}\nKontaktbogen → {sheet}')
    return 0


def course(lighting='tag', scene='hangar'):
    """Vorführlauf durch den Parcours (RouteRunner im Build) → MP4 mit Laufzeit, Kontrollpunkten und Treffern, dazu Kontaktbogen."""
    d = os.path.join(EV, f'course_{scene}_{lighting}')
    shutil.rmtree(d, ignore_errors=True)
    rc = player(['-ballonCourse', d, '-ballonScene', scene, '-ballonLighting', lighting], os.path.join(EV, 'course.log'))
    frames = sorted(glob.glob(os.path.join(d, '[0-9]*.png')))
    if not frames:
        print('Aufnahme fehlgeschlagen', rc)
        return 1
    if not os.path.exists(os.path.join(d, 'result.txt')):
        print('Aufnahme unvollständig (kein result.txt), Protokoll:', os.path.join(EV, 'course.log'))
        return 1
    result = open(os.path.join(d, 'result.txt'), encoding='utf-8').read().split('\n')[0]
    rows = [ln.strip().split(',') for ln in open(os.path.join(d, 'frames.csv'), encoding='utf-8')]
    lab = os.path.join(d, '_lab')
    os.makedirs(lab, exist_ok=True)

    def label(i):
        _, state, t, cps, hits, wp = rows[i]
        cmd = ['magick', frames[i], '-font', FONT, '-fill', '#F2F3F4', '-stroke', '#00000060', '-pointsize', '20', '-annotate', '+18+34',
               f'BALLON 0.9 Parcours · Unity · {scene.capitalize()} · {lighting.capitalize()}', '-pointsize', '16', '-annotate', '+18+58',
               f'Vorführlauf (automatisch) · Bild {i} · Wegpunkt {wp}', '-gravity', 'NorthEast', '-pointsize', '26', '-annotate', '+22+34',
               f'{float(t):.1f} s' if state != 'Bereit' else 'bereit', '-pointsize', '16', '-annotate', '+22+64',
               f'Kontrollpunkte {cps} · Treffer {hits}']
        subprocess.run(cmd + [os.path.join(lab, f'{i:04d}.png')], check=True)

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(8) as ex:
        list(ex.map(label, range(len(frames))))
    out = os.path.join(EV, f'parcours_{scene}_{lighting}.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '30', '-i', os.path.join(lab, '%04d.png'), '-vf', 'format=yuv420p',
                    '-c:v', 'libx264', '-crf', '21', '-movflags', '+faststart', out], check=True)
    sheet = os.path.join(EV, f'parcours_{scene}_{lighting}.png')
    pick = [round(k * (len(frames) - 1) / 11) for k in range(12)]
    subprocess.run(['magick', 'montage', *[x for f in pick for x in ('-label', f'{float(rows[f][2]):.1f} s · Kontrollpunkte {rows[f][3]} · '
                                                                        f'Treffer {rows[f][4]}', os.path.join(lab, f'{f:04d}.png'))],
                    '-tile', '4x', '-geometry', '480x270+3+3', '-pointsize', '12', '-background', '#9EA4AC',
                    '-title', f'BALLON 0.9 Parcours · Vorführlauf {scene} / {lighting} · {result}', sheet], check=True)
    shutil.rmtree(lab)
    print(f'{len(frames)} Bilder ({len(frames) / 30:.1f} s) → {out}\nKontaktbogen → {sheet}\n{result}')
    return rc


def lum(path):
    r = subprocess.run(['magick', path, '-alpha', 'off', '-colorspace', 'Gray', '-format', '%[fx:mean]', 'info:'],
                       capture_output=True, text=True)
    return float(r.stdout or 0)


def _num(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return float((r.stdout or r.stderr).strip().split()[0])


def metrics(u, b, mask=None):
    """Kennzahlen Unity gegen Blender. SSIM: ImageMagick 7 meldet DSSIM = (1 − SSIM) / 2, also SSIM = 1 − 2·DSSIM
    (geprüft: Schwarz gegen Weiß ergibt 0,49995). Mit Maske zusätzlich mittlere Abweichung, PSNR und Helligkeit nur über dem
    Viewmodel sowie SSIM im Ausschnitt der Maske."""
    d = os.path.dirname(u)
    rgb = os.path.join(d, '_ref.png')                         # Blender-PNG hat Alpha: für den Vergleich auf RGB
    subprocess.run(['magick', b, '-alpha', 'off', rgb], check=True)

    def m(kind, x, y):
        txt = subprocess.run(['magick', 'compare', '-metric', kind, x, y, 'null:'], capture_output=True, text=True).stderr.strip()
        return float(txt.split('(')[1].rstrip(')')) if kind == 'SSIM' else float(txt.split()[0])
    res = dict(ssim=round(1 - 2 * m('SSIM', u, rgb), 4), psnr_db=round(m('PSNR', u, rgb), 2),
               lum_unity=round(lum(u), 4), lum_blender=round(lum(b), 4))
    if mask and os.path.exists(mask):
        mk = os.path.join(d, '_mask.png')
        subprocess.run(['magick', mask, '-colorspace', 'Gray', '-threshold', '20%', mk], check=True)
        area = _num(['magick', mk, '-format', '%[fx:mean]', 'info:'])
        sq = os.path.join(d, '_sq.png')
        subprocess.run(['magick', u, rgb, '-compose', 'difference', '-composite', '-colorspace', 'Gray', '-depth', '16',
                        sq], check=True)
        mae = _num(['magick', sq, mk, '-compose', 'multiply', '-composite', '-format', '%[fx:mean]', 'info:']) / area
        mse = _num(['magick', sq, '-evaluate', 'pow', '2', mk, '-compose', 'multiply', '-composite', '-format', '%[fx:mean]',
                    'info:']) / area
        lu = _num(['magick', u, '-colorspace', 'Gray', mk, '-compose', 'multiply', '-composite', '-format', '%[fx:mean]',
                   'info:']) / area
        lb = _num(['magick', rgb, '-colorspace', 'Gray', mk, '-compose', 'multiply', '-composite', '-format', '%[fx:mean]',
                   'info:']) / area
        box = subprocess.run(['magick', mk, '-format', '%@', 'info:'], capture_output=True, text=True).stdout.strip()
        cu, cb = os.path.join(d, '_cu.png'), os.path.join(d, '_cb.png')
        subprocess.run(['magick', u, '-crop', box, '+repage', cu], check=True)
        subprocess.run(['magick', rgb, '-crop', box, '+repage', cb], check=True)
        import math
        res.update(vm_area=round(area, 3), vm_mae=round(mae, 4), vm_psnr_db=round(10 * math.log10(1 / max(mse, 1e-9)), 2),
                   vm_lum_unity=round(lu, 4), vm_lum_blender=round(lb, 4), vm_ssim_box=round(1 - 2 * m('SSIM', cu, cb), 4))
    return res


def compare(extra=(), weapon=1):
    d = os.path.join(EV, 'compare' + ('' if weapon == 1 else f'_{weapon}'))
    shutil.rmtree(d, ignore_errors=True)
    rc = player(['-ballonCompare', d, '-ballonWeapon', str(weapon)] + list(extra), os.path.join(EV, 'compare.log'))
    stills = os.environ.get('BALLON_BLENDER_STILLS') or os.path.join(EV, 'blender_out', WEAPONS[weapon], 'ego', 'stills')
    if rc:
        return rc
    tiles, mets = [], {}
    for pose in ('hip', 'ads', 'reload', 'inspect_r'):
        u = os.path.join(d, f'{pose}_unity.png')
        b = os.path.join(stills, f'{pose}_ego.png')
        if not (os.path.exists(u) and os.path.exists(b)):
            print('fehlt:', u if not os.path.exists(u) else b)
            continue
        edge = os.path.join(d, f'{pose}_kanten.png')
        # Kanten des Blender-Bildes (orange) über dem Unity-Bild: Deckung der Silhouetten
        subprocess.run(['magick', u, '(', b, '-colorspace', 'gray', '-blur', '0x1', '-edge', '1', '-threshold', '18%',
                        '-fill', '#FF7A1A', '-opaque', 'white', '-transparent', 'black', ')', '-composite', edge], check=True)
        mix = os.path.join(d, f'{pose}_mischung.png')
        subprocess.run(['magick', u, b, '-compose', 'blend', '-define', 'compose:args=50', '-composite', mix], check=True)
        m = mets[pose] = metrics(u, b, os.path.join(d, f'{pose}_mask.png'))
        print(f"  {pose}: SSIM {m['ssim']}, PSNR {m['psnr_db']} dB | Viewmodel: Abweichung {m.get('vm_mae')}, PSNR {m.get('vm_psnr_db')} dB, "
              f"SSIM (Ausschnitt) {m.get('vm_ssim_box')}, Helligkeit {m.get('vm_lum_unity')} / {m.get('vm_lum_blender')}")
        tiles += ['-label', f'{pose} · Blender (Cycles)', b, '-label', f"{pose} · Unity (URP) · SSIM {m['ssim']}", u,
                  '-label', f'{pose} · Blender-Kanten über Unity', edge]
    sheet = os.path.join(EV, 'firstfeel_vergleich.png' if weapon == 1 else f'firstfeel_vergleich_{WEAPONS[weapon]}.png')
    subprocess.run(['magick', 'montage', *tiles, '-tile', '3x', '-geometry', '600x338+3+3', '-pointsize', '14', '-background', '#9EA4AC',
                    '-title', f'BALLON · {WEAPONS[weapon]} · Standbildvergleich Blender gegen Unity (gleiche Haltung, Kamera 75° horizontal)', sheet],
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
        sys.exit(capture(sys.argv[2] if len(sys.argv) > 2 else None))
    if a in DEMOS:            # Sprint und Visier-Anflug (0.10); Pendeln, Rückmeldung (unity-abgleich); Hüft-Fadenkreuz (0.13); Sprint, Wechsel, Rückstoß (0.15); Feuer (0.16)
        sys.exit(capture(sys.argv[2] if len(sys.argv) > 2 else None, demo=a))
    if a == 'fov':            # Beleg A9 (0.32): Hüfte/Zielen bei Welt 60/75/100°, Wand 12 cm vor dem Auge
        d = os.path.join(EV, 'fov_shots')
        shutil.rmtree(d, ignore_errors=True)
        sys.exit(player(['-ballonFovShots', d], os.path.join(EV, 'fov_shots.log')))
    if a == 'scenes':
        d = os.path.join(EV, 'scene_shots')
        shutil.rmtree(d, ignore_errors=True)
        rc = player(['-ballonSceneShots', d], os.path.join(EV, 'scene_shots.log'))
        for f in sorted(glob.glob(os.path.join(d, '*_umgebung.png'))):
            name = os.path.basename(f)[:-len('_umgebung.png')]   # <szene>_<licht>
            ref = os.path.join(EV, 'scenes', f'{name}_ref.png')
            if not os.path.exists(ref):
                print(f'  {name}: kein Blender-Referenzbild {ref}')
            else:
                m = metrics(f, ref)
                print(f"  {name}: SSIM {m['ssim']}, PSNR {m['psnr_db']} dB, Helligkeit Unity {m['lum_unity']} / Blender {m['lum_blender']}")
                out = os.path.join(EV, f'szene_{name}_vergleich.png')
                subprocess.run(['magick', 'montage', '-label', 'Blender (Cycles)', ref, '-label', f"Unity · SSIM {m['ssim']}", f,
                                '-label', 'Unity mit Waffe', f.replace('_umgebung', '_waffe'), '-tile', '3x', '-geometry', '640x360+3+3',
                                '-pointsize', '14', '-background', '#9EA4AC', out], check=True)
                print('  →', out)
        sys.exit(rc)
    if a == 'course':
        sys.exit(course(*sys.argv[2:4]))                         # course [<licht> [<szene>]]
    if a == 'skins':
        d = os.path.join(EV, 'skins')
        shutil.rmtree(d, ignore_errors=True)
        rc = player(['-ballonSkins', d], os.path.join(EV, 'skins.log'))
        files = sorted(glob.glob(os.path.join(d, '*.png')))
        if rc or not files:
            sys.exit(rc or 1)
        out = os.path.join(EV, 'firstfeel_skins.png')
        tiles = [x for f in files for x in ('-label', os.path.basename(f)[3:-4].replace('_', ' · '), f)]
        subprocess.run(['magick', 'montage', *tiles, '-tile', '4x', '-geometry', '480x270+3+3', '-pointsize', '13',
                        '-background', '#9EA4AC', '-title', 'BALLON · Waffen-Skins in Unity (gebacken aus kit.SKINS)', out], check=True)
        print('Skins →', out)
        sys.exit(0)
    if a == 'bench':
        sc = sys.argv[2] if len(sys.argv) > 2 else None              # z. B. hangar: Vorführlauf durch den Parcours, Lichtszenen wechseln
        f = os.path.join(EV, f'bench_{sc}.json' if sc else 'bench.json')
        rc = player(['-ballonBench', f] + (['-ballonScene', sc] if sc else []), os.path.join(EV, 'bench.log'))
        print(open(f).read() if os.path.exists(f) else 'keine Messung')
        sys.exit(rc)
    if a in ('ruckeln', 'aufwaermen'):     # ruckeln <name> [profil] [kalt] [einmal]: Ruckelmessung (0.37), mit „profil“ Profiler-Protokoll
        rec = a == 'aufwaermen'            # + Ursachen; aufwaermen: dieselbe Messung zeichnet die Shader-Zustände auf (0.38)
        name = 'aufwaermen' if rec else sys.argv[2] if len(sys.argv) > 2 else 'messung'
        if not name.replace('_', '').replace('-', '').isalnum():
            sys.exit(f'ruckeln: Name nur aus Buchstaben, Ziffern, _ und - ({name!r})')
        flags = sys.argv[2:] if rec else sys.argv[3:]
        prof = 'profil' in flags
        d = os.path.join(EV, 'ruckeln', name)                   # nur dieser Messordner wird ersetzt
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        app = APP
        if 'kalt' in flags:
            app, bid = cold_copy(APP, name)
        exe = os.path.join(app, 'Contents', 'MacOS', 'BALLON Firstfeel')
        log = os.path.join(d, 'player.log')
        gsc = os.path.join(d, 'ballon_mac_metal.graphicsstate')
        args = (['-ballonStutter', os.path.join(d, 'frames.csv')] + (['-ballonProfile', os.path.join(d, 'raw')] if prof else [])
                + (['-ballonStutterPasses', '1'] if 'einmal' in flags else ['-ballonStutterPasses', '0'] if 'laden' in flags else [])
                + (['-ballonGscRecord', gsc] if rec else []))
        try:
            rc = locked(['caffeinate', '-di', exe, '-screen-width', '1280', '-screen-height', '720', '-screen-fullscreen', '0',
                         '-logFile', log] + args + os.environ.get('BALLON_PLAYER_EXTRA', '').split(), log)   # Bildschirm wach; Fenster
            # wie im Testbuild (1280 × 720); BALLON_PLAYER_EXTRA: weitere Argumente der Build
        finally:
            if app != APP:
                cold_cleanup(app, bid)
        if not rc and rec:
            if not os.path.exists(gsc):
                sys.exit(f'aufwaermen: keine Sammlung geschrieben ({log})')
            dst = os.path.join(PROJ, 'Assets', 'Ballon', 'Warmup', os.path.basename(gsc))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(gsc, dst)
            print('Sammlung →', dst)
            subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'gsc_complete.py'), dst], check=True)   # je Pass-Familie ergänzen
            rc = editor('Ballon.Ego.Editor.BallonSetup.AttachWarmup', 'aufwaermen') or editor('Ballon.Ego.Editor.BallonSetup.BuildMac', 'build')
        if not rc and prof:
            rc = locked([UNITY, '-batchmode', '-quit', '-projectPath', PROJ, '-executeMethod', 'Ballon.Ego.Editor.ProfileSpikes.Run',
                         '-ballonRawDir', os.path.join(d, 'raw'), '-ballonOut', os.path.join(d, 'spikes.json'),
                         '-logFile', os.path.join(d, 'spikes.log')], os.path.join(d, 'spikes.log'))
        if not rc:
            subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'stutter_report.py'), d])
        sys.exit(rc)
    if a == 'compare':                     # compare [n] [Zusatzargumente der Build]
        rest = sys.argv[2:]
        n = int(rest.pop(0)) if rest and rest[0].isdigit() else 1
        sys.exit(compare(rest, n))
    print(__doc__)
