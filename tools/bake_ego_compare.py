"""Alter gegen neuer Bake in der Ego-Ansicht (0.43 „Kiln“): dieselbe Waffe mehrfach gebacken und nebeneinander in einer Build, Standbilder aus Unity, Kennzahlen.

  python3 tools/bake_ego_compare.py bake [Ordner mit altem BALLON-Stand] [QB,QC]   (unter `ce lock gpu`) → Pakete im Cache
  python3 tools/bake_ego_compare.py install → Vergleichswaffen in Generated/FormgenSeries und ego_series.json; danach `BALLON_NO_SERIES=1 python3 tools/unity_run.py setup` und `build` (ohne die Umgebungsvariable räumt setup die Vergleichswaffen wieder weg)
  python3 tools/bake_ego_compare.py shots   → Standbilder Hüfte und Zielen je Waffe (1470 × 956), Tabelle und Kontaktbogen nach <EV>/kiln/ego/
  python3 tools/bake_ego_compare.py remove  → Vergleichswaffen wieder entfernen (danach setup und build)
  python3 tools/bake_ego_compare.py eigene <Stand> [Waffe,…] → Standbilder Hüfte und Zielen der festen Waffen (BASIC-*, BD01, BG01) nach <EV>/ego_eigene/<Stand>/ (0.44)
  python3 tools/bake_ego_compare.py eigene-vergleich <vorher> <nachher> [Waffe,…] → Tabelle und Kontaktbogen beider Stände, Viewmodel gegen ego_vm_ssim
  python3 tools/bake_ego_compare.py serie   → eine Serienwaffe je Linie gegen frische Blender-Stills (tools/ego_variant.py, `unity_run.compare`) nach <EV>/kiln/serie/

Waffen: BA01 (Formgen-Linie A = BASIC-01 unverändert) und BJ01. Je Waffe QA.. = heutiger Bake (Stand vor 0.43: 4096², 64 Samples), QB.. = neu (Albedo 2048², Normale 4096²), QC.. = neu 4096².
Nichts davon gelangt ins Repo (Ordner FormgenSeries).
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools import series_packages as SP  # noqa: E402
from tools import unity_run as UR  # noqa: E402

EV = os.environ.get('BALLON_KILN_EVIDENCE', os.path.expanduser('~/Library/Caches/CubeEscapeBallon/kiln'))
KINDS = (('QA', 'alt 4096² / 64', 4096, 64), ('QB', 'neu Albedo 2048²', 2048, None), ('QC', 'neu 4096²', 4096, None))
SHEETS = (('BA01', '01'), ('BJ01', '02'))
SIZE = '1470x956'
REFERENCE = ('BJ01', 'BK04', 'BL09', 'BM14')           # je Linie eine Waffe, verschiedene Grundtypen


def jobs():
    p = dict(SP.pin(), lines=['A', 'J'])
    src = SP.source(p)
    allj = {j['id']: j for j in SP.plan_jobs(p, src)}
    out = []
    for sheet, nr in SHEETS:
        for q, de, size, samples in KINDS:
            out.append(dict(allj[sheet], id=f'{q}{nr}', series='Q', series_name=de, sheet=sheet, size=size, samples=samples))
    return out, os.path.join(src, 'formgen', 'blender', 'asset_build.py')


def key(j):
    return f"vergleich-{j['id']}"


def bake(old, only=''):
    js, script = jobs()
    for j in js:
        if only and j['id'][:2] not in only.split(','):
            continue
        snap = old if j['id'].startswith('QA') else SP.ROOT
        s = SP.bake_one(j, key(j), dict(size=j['size'], samples=j['samples'], device='gpu'), script, snapshot=snap)
        print(f"{j['id']} ({j['sheet']}, {j['series_name']}): {s:.0f} s", flush=True)


def install():
    from tools import formgen_import as FI
    js, _ = jobs()
    D = json.load(open(SP.OUT_JSON, encoding='utf-8'))
    D['weapons'] = [e for e in D['weapons'] if e.get('origin', {}).get('series') != 'Q']
    for j in js:
        SP.install(j, key(j))
        e = FI.entry(os.path.join(SP.DST, j['id']))
        e['origin'].update(series='Q', series_name=j['series_name'])
        D['weapons'].append(e)
    json.dump(D, open(SP.OUT_JSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(js)} Vergleichswaffen eingerichtet')


def remove():
    import shutil
    D = json.load(open(SP.OUT_JSON, encoding='utf-8'))
    ids = [e['id'] for e in D['weapons'] if e.get('origin', {}).get('series') == 'Q']
    D['weapons'] = [e for e in D['weapons'] if e['id'] not in ids]
    json.dump(D, open(SP.OUT_JSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for i in ids:
        shutil.rmtree(os.path.join(SP.DST, i), ignore_errors=True)
        if os.path.exists(os.path.join(SP.DST, i + '.meta')):
            os.remove(os.path.join(SP.DST, i + '.meta'))
    print('entfernt:', ', '.join(ids))


def serie():
    """Blender-Abgleich der Serien (AGENTS.md: sichtbare Unity-Änderungen gegen frische Blender-Stills): braucht den fertigen Build."""
    import glob
    import shutil
    p = SP.pin()
    plan = {j['id']: j for j in SP.plan_jobs(p, SP.source(p))}
    D = json.load(open(SP.OUT_JSON, encoding='utf-8'))
    index = {e['id']: k + 1 for k, e in enumerate(D['weapons'])}
    for sid in REFERENCE:
        out = os.path.join(EV, 'serie', sid)
        shutil.rmtree(out, ignore_errors=True)         # nur frische Stills zählen
        os.makedirs(out, exist_ok=True)
        skin = os.path.join(out, 'skin.json')
        json.dump(plan[sid]['skin_def'], open(skin, 'w', encoding='utf-8'), ensure_ascii=False)
        rc = subprocess.run([os.path.expanduser('~/Claude/cubeescape-nexogen/ce'), 'lock', 'gpu', '--what', f'BALLON Stills {sid}', '--', SP.BLENDER, '-b', '--factory-startup', '--python-exit-code', '1',
                             '-P', os.path.join(SP.ROOT, 'tools', 'ego_variant.py'), '--', os.path.join(SP.DST, sid), '--skin-def', skin, '--gpu'],
                            env=dict(os.environ, BASIC_OUT=out), capture_output=True, text=True)
        stills = glob.glob(os.path.join(out, '*', 'ego', 'stills'))
        if rc.returncode or not stills:
            print(f'{sid}: Blender-Stills fehlgeschlagen', rc.stdout[-800:], rc.stderr[-400:])
            return 1
        os.environ['BALLON_BLENDER_STILLS'] = stills[0]
        print(f'== {sid} (Waffe {index[sid]})', flush=True)
        if UR.compare((), index[sid]):
            return 1
    return 0


def shots():
    D = json.load(open(SP.OUT_JSON, encoding='utf-8'))
    index = {e['id']: k + 1 for k, e in enumerate(D['weapons'])}
    base = os.path.join(EV, 'ego')
    os.makedirs(base, exist_ok=True)
    table, tiles = {}, []
    for sheet, nr in SHEETS:
        for q, de, _, _ in KINDS:
            d = os.path.join(base, f'{q}{nr}')
            rc = UR.player(['-ballonCompare', d, '-ballonWeapon', str(index[f'{q}{nr}']), '-ballonCompareSize', SIZE], os.path.join(base, f'{q}{nr}.log'), (1470, 956))
            if rc:
                return rc
        for pose in ('hip', 'ads'):
            old = os.path.join(base, f'QA{nr}', f'{pose}_unity.png')
            mask = os.path.join(base, f'QA{nr}', f'{pose}_mask.png')
            for q, de, _, _ in KINDS[1:]:
                new = os.path.join(base, f'{q}{nr}', f'{pose}_unity.png')
                m = UR.metrics(new, old, mask)
                table[f'{sheet} {pose} {de}'] = m
                print(f"{sheet} {pose} {de}: SSIM {m['ssim']}, PSNR {m['psnr_db']} dB | Viewmodel Abweichung {m.get('vm_mae')}, SSIM {m.get('vm_ssim_box')}, "
                      f"Helligkeit {m.get('vm_lum_unity')} / {m.get('vm_lum_blender')}", flush=True)
            tiles += ['-label', f'{sheet} {pose} · {KINDS[0][1]}', old] + sum((['-label', f'{sheet} {pose} · {de}', os.path.join(base, f'{q}{nr}', f'{pose}_unity.png')]
                                                                                for q, de, _, _ in KINDS[1:]), [])
    json.dump(table, open(os.path.join(base, 'ego_vergleich.json'), 'w'), ensure_ascii=False, indent=1)
    low = json.load(open(os.path.join(SP.ROOT, 'data', 'bake_settings.json'), encoding='utf-8'))['limits']['ego_vm_ssim']
    over = [f"{k}: {m.get('vm_ssim_box')}" for k, m in table.items() if m.get('vm_ssim_box', 0) < low]
    print(f'Grenzwert Viewmodel-SSIM {low}: ' + ('unterschritten – ' + '; '.join(over) if over else 'eingehalten'))
    subprocess.run(['magick', 'montage', *tiles, '-tile', '3x', '-geometry', '735x478+3+3', '-pointsize', '14', '-background', '#9EA4AC',
                    os.path.join(base, 'ego_vergleich.png')], check=True)
    print('Kontaktbogen →', os.path.join(base, 'ego_vergleich.png'))
    return 1 if over else 0


def own_weapons(only=''):
    """[(ID, Platz in der Build, Haltungen)] der festen Waffen; Serien stehen dahinter und zählen nicht."""
    D = json.load(open(SP.OUT_JSON if os.path.exists(SP.OUT_JSON) else os.path.join(SP.GEN, 'ego.json'), encoding='utf-8'))
    all_ = [(e['id'], k + 1, own_poses(e)) for k, e in enumerate(D['weapons']) if not e.get('dir', '').startswith('FormgenSeries/')]
    want = [i for i in only.split(',') if i]
    unknown = sorted(set(want) - {w[0] for w in all_})
    if unknown:
        raise SystemExit(f'Unbekannt: {unknown}')
    return [w for w in all_ if not want or w[0] in want]


def own_poses(entry):
    """Haltungen im Vergleich, aus den Daten: Zielen nur mit Aktion aim_in (die Portalkanone hat keine). Fehlt ein Bild, bricht der Vergleich ab, statt still weniger zu prüfen."""
    return ('hip', 'ads') if 'aim_in' in entry['actions'] else ('hip',)


def own_shots(tag, only=''):
    base = os.path.join(EV, 'ego_eigene', tag)
    os.makedirs(base, exist_ok=True)
    for sid, nr, _ in own_weapons(only):
        rc = UR.player(['-ballonCompare', os.path.join(base, sid), '-ballonWeapon', str(nr), '-ballonCompareSize', SIZE], os.path.join(base, f'{sid}.log'), (1470, 956))
        print(f'{sid}: Exit {rc}', flush=True)
        if rc:
            return rc
    return 0


def own_compare(before, after, only=''):
    root = os.path.join(EV, 'ego_eigene')
    table, tiles = {}, []
    for sid, _, poses in own_weapons(only):
        for pose in poses:
            old, new = (os.path.join(root, t, sid, f'{pose}_unity.png') for t in (before, after))
            m = table[f'{sid} {pose}'] = UR.metrics(new, old, os.path.join(root, before, sid, f'{pose}_mask.png'))
            print(f"{sid} {pose}: SSIM {m['ssim']} | Viewmodel Abweichung {m.get('vm_mae')}, SSIM {m.get('vm_ssim_box')}, Helligkeit {m.get('vm_lum_unity')} / {m.get('vm_lum_blender')}", flush=True)
            tiles += ['-label', f'{sid} {pose} · {before}', old, '-label', f'{sid} {pose} · {after}', new]
    out = os.path.join(root, f'{before}_gegen_{after}')
    json.dump(table, open(out + '.json', 'w'), ensure_ascii=False, indent=1)
    low = json.load(open(os.path.join(SP.ROOT, 'data', 'bake_settings.json'), encoding='utf-8'))['limits']['ego_vm_ssim']
    over = [f"{k}: {m.get('vm_ssim_box')}" for k, m in table.items() if m.get('vm_ssim_box', 0) < low]
    print(f'Grenzwert Viewmodel-SSIM {low}: ' + ('unterschritten – ' + '; '.join(over) if over else 'eingehalten'))
    subprocess.run(['magick', 'montage', *tiles, '-tile', '4x', '-geometry', '490x319+2+2', '-pointsize', '12', '-background', '#9EA4AC', out + '.png'], check=True)
    print('Kontaktbogen →', out + '.png')
    return 1 if over else 0


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'bake':
        bake(sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser('~/Library/Caches/CubeEscapeBallon/kiln/base'), sys.argv[3] if len(sys.argv) > 3 else '')
    elif cmd in ('install', 'remove'):
        globals()[cmd]()
    elif cmd == 'shots':
        sys.exit(shots())
    elif cmd == 'serie':
        sys.exit(serie())
    elif cmd == 'eigene':
        sys.exit(own_shots(sys.argv[2], *sys.argv[3:4]))
    elif cmd == 'eigene-vergleich':
        sys.exit(own_compare(sys.argv[2], sys.argv[3], *sys.argv[4:5]))
    else:
        print(__doc__)
