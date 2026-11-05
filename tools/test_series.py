"""Serien aus Formgen v2 (0.43 „Kiln“): Pin, Inhalts-Cache (zweiter Lauf backt nichts) und nichts davon im Repo. Ohne Blender und ohne Formgen, Teil von ./check."""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools import series_packages as SP  # noqa: E402

bad = []


def ok(c, what):
    if not c:
        bad.append(what)


# Pin
P = SP.pin()
ok(P['lines'] == ['J', 'K', 'L', 'M'], 'Linien J–M')
ok(len(P['commit']) == 40, 'volle SHA')
for broken in (dict(P, commit='8486994'), dict(P, lines=[]), dict(P, bake={})):
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as fh:
        json.dump(broken, fh)
    try:
        SP.pin(fh.name)
        bad.append(f'Pin ohne Prüfung angenommen: {broken}')
    except SP.SeriesError:
        pass
    os.remove(fh.name)

# nichts im Repo
rel = 'unity/Assets/Ballon/Generated/FormgenSeries'
for path in (f'{rel}/BJ01/BJ01.fbx', f'{rel}/BJ01/textures/BJ01_albedo.jpg', f'{rel}/BJ01.meta', f'{rel}/Materials/Atlas_formgen_BJ01.mat',
             f'{rel}/Icons/BJ01.png', f'{rel}/Resources/ego_series.json', f'{rel}/Resources/BallonSeries.asset', f'{rel}.meta'):
    ok(subprocess.run(['git', '-C', ROOT, 'check-ignore', '-q', path]).returncode == 0, f'nicht ignoriert: {path}')
tracked = subprocess.run(['git', '-C', ROOT, 'ls-files', rel, f'{rel}.meta'], capture_output=True, text=True).stdout.split()
ok(not tracked, f'Serien-Dateien im Repo: {tracked[:4]}')
ego = json.load(open(os.path.join(SP.GEN, 'ego.json'), encoding='utf-8'))
ok(not [e['id'] for e in ego['weapons'] if e.get('dir', '').startswith('FormgenSeries/')], 'Serien in ego.json im Repo')
scene = open(os.path.join(ROOT, 'unity', 'Assets', 'Ballon', 'Scenes', 'Firstfeel.unity'), encoding='utf-8', errors='replace').read()
ok(f"id: BJ01" not in scene, 'Serien in der Szene im Repo')

# Schlüssel: gleiche Eingaben gleich, jede Eingabe wirkt
job = dict(id='BJ01', module='basic.pilot.w01_auto_rifle_v21', model=dict(PARTS=[1]), skin='frost', skin_def=dict(wear=0.5))
bake, code = dict(size=2048), dict(a='1')
k0 = SP.job_key(job, bake, code, 'Blender 5.2', 's', 'm')
ok(k0 == SP.job_key(dict(job), dict(bake), dict(code), 'Blender 5.2', 's', 'm'), 'Schlüssel nicht stabil')
for k in (SP.job_key(dict(job, model=dict(PARTS=[2])), bake, code, 'Blender 5.2', 's', 'm'), SP.job_key(dict(job, skin='cube'), bake, code, 'Blender 5.2', 's', 'm'),
          SP.job_key(dict(job, skin_def=dict(wear=0.6)), bake, code, 'Blender 5.2', 's', 'm'), SP.job_key(job, dict(size=4096), code, 'Blender 5.2', 's', 'm'),
          SP.job_key(job, bake, dict(a='2'), 'Blender 5.2', 's', 'm'), SP.job_key(job, bake, code, 'Blender 5.3', 's', 'm'),
          SP.job_key(job, bake, code, 'Blender 5.2', 't', 'm'), SP.job_key(job, bake, code, 'Blender 5.2', 's', 'n')):
    ok(k != k0, 'Eingabe ohne Wirkung auf den Schlüssel')

# Bake-Code im Schlüssel: Backen zählt, der übrige Export nicht
with tempfile.TemporaryDirectory() as t:
    p = os.path.join(t, 'e.py')
    src = "TEXTURE_STORE = dict(a=1)\ndef bake_weapon():\n    return 1\ndef data():\n    return 2\n"
    open(p, 'w').write(src)
    a = SP.export_source(p)
    open(p, 'w').write(src.replace('return 2', 'return 3'))
    ok(SP.export_source(p) == a, 'Datenexport ändert den Bake-Schlüssel')
    open(p, 'w').write(src.replace('return 1', 'return 4'))
    ok(SP.export_source(p) != a, 'bake_weapon fehlt im Bake-Schlüssel')
ok(set(SP.code_files()) == set(SP.CODE_FILES) | {'export_unity', 'scene_build'}, 'Bake-Code unvollständig')
ok('tools/skin_masks.py' in SP.CODE_FILES, 'Masken (_freeze) im Schlüssel')
ok(set(SP.export_source(os.path.join(ROOT, 'tools', 'scene_build.py'), SP.SCENE_PARTS)) == set(SP.SCENE_PARTS), 'Entrauscher (_denoise) im Schlüssel')
have = SP.export_source(os.path.join(ROOT, 'tools', 'export_unity.py'))
ok(set(have) == set(SP.EXPORT_PARTS), f'Teile fehlen in export_unity: {set(SP.EXPORT_PARTS) - set(have)}')

# Cache-Treffer beim zweiten Lauf, Durchgefallene werden genannt, nicht ausgelassen
with tempfile.TemporaryDirectory() as t:
    SP.CACHE, SP.DST = os.path.join(t, 'cache'), os.path.join(t, 'dst')
    SP.OUT_JSON = os.path.join(SP.DST, 'Resources', 'ego_series.json')
    baked = []

    def baker(j, key, b, script):
        d = SP.package_dir(key)
        os.makedirs(d)
        open(os.path.join(d, 'x.txt'), 'w').write(j['id'])
        open(os.path.join(d, '.complete'), 'w').write(key)
        baked.append(j['id'])
        return 0.0

    real = SP.not_playable
    SP.not_playable = lambda j: 'Formstudie' if j['id'] == 'BJ16' else None
    jobs = [dict(job, id=i, series='J', series_name='Cold Shard', module='basic.none') for i in ('BJ01', 'BJ02', 'BJ16', 'BJ03')]
    fail, keys, todo = SP.prepare(jobs, dict(P), dict(code), 'B', 's')
    ok([j['id'] for j in todo] == ['BJ01', 'BJ02', 'BJ03'], f'erster Lauf {todo}')
    ok([f['id'] for f in fail] == ['BJ16'], 'nicht Spielbares nicht gemeldet')
    os.makedirs(SP.CACHE)

    def broken(j, key, b, script):
        if j['id'] == 'BJ03':
            raise SP.SeriesError('Absturz')
        return baker(j, key, b, script)
    SP.bake_all(todo, keys, dict(P), 's', baker=broken)
    ok(baked == ['BJ01', 'BJ02'], f'gebacken {baked}')
    fail2, keys2, todo2 = SP.prepare(jobs, dict(P), dict(code), 'B', 's')
    ok(keys2 == keys, 'zweiter Lauf: andere Schlüssel')
    ok([j['id'] for j in todo2] == ['BJ03'], f'zweiter Lauf backt {todo2} statt nur BJ03')
    ok(SP.install(jobs[0], keys['BJ01']) is True, 'Einrichten')
    meta = os.path.join(SP.DST, 'BJ01', 'x.txt.meta')
    open(meta, 'w').write('guid: 1')
    ok(SP.install(jobs[0], keys['BJ01']) is False, 'gleiches Paket neu eingerichtet (Unity importierte neu)')
    new = dict(jobs[0], skin='cube')
    k2 = SP.job_key(new, P['bake'], dict(code), 'B', 's', '')
    baker(new, k2, None, None)
    ok(SP.install(new, k2) is True and open(meta).read() == 'guid: 1', 'neues Paket: .meta muss bleiben (GUIDs)')
    # 0.44: leerer Cache, Paket liegt schon in Unity: kein Neubau; ohne passenden Stempel wie bisher backen
    cache_was, SP.CACHE = SP.CACHE, os.path.join(t, 'leer')
    stamp = open(os.path.join(SP.DST, 'BJ01', '.series_key')).read().strip()
    other = dict(jobs[0], skin='anders')
    fail3, keys3, todo3 = SP.prepare([other], dict(P), dict(code), 'B', 's')
    ok(todo3 and not SP.installed('BJ01', keys3['BJ01']), 'fremder Stempel zählt als Treffer')
    ok(SP.installed('BJ01', stamp) and not SP.cached(stamp), 'Stempel ohne Cache nicht erkannt')
    open(os.path.join(SP.DST, 'BJ01', '.series_key'), 'w').write(keys3['BJ01'] + '\n')
    ok(SP.prepare([other], dict(P), dict(code), 'B', 's')[2] == [], 'leerer Cache backt Eingerichtetes neu')
    open(os.path.join(SP.DST, 'BJ01', '.series_key'), 'w').write(stamp + '\n')
    SP.CACHE = cache_was
    # 0.44: feste Varianten: .meta bleiben, kein Stempel im Repo, ohne Bake nichts einrichten
    fixed = os.path.join(t, 'fixed')
    os.makedirs(os.path.join(fixed, 'BJ01'))
    open(os.path.join(fixed, 'BJ01', 'x.txt.meta'), 'w').write('guid: 2')
    open(os.path.join(fixed, 'BJ01', 'alt.glb'), 'w').write('alt')
    open(os.path.join(fixed, 'BJ01', 'alt.glb.meta'), 'w').write('guid: 3')
    SP.FIXED = fixed
    SP.install_fixed([jobs[0]], {'BJ01': keys['BJ01']}, [])
    ok(sorted(os.listdir(os.path.join(fixed, 'BJ01'))) == ['x.txt', 'x.txt.meta'] and open(os.path.join(fixed, 'BJ01', 'x.txt.meta')).read() == 'guid: 2',
       'feste Variante: .meta, Stempel oder Altes falsch')
    try:
        SP.install_fixed([jobs[0], jobs[3]], keys, [])
        bad.append('feste Variante ohne Bake eingerichtet')
    except SP.SeriesError:
        pass
    ok(SP.remove_stale({'BJ01'}) == [] and SP.remove_stale(set()) == ['BJ01'], 'Veraltetes nicht entfernt')
    D = SP.merged_ego([dict(id='BJ01', dir='FormgenSeries/BJ01')], [dict(id='BJ16', step='Ego-Profil', reason='Formstudie')], P)
    ok([e['id'] for e in D['weapons']][:len(ego['weapons'])] == [e['id'] for e in ego['weapons']] and D['weapons'][-1]['id'] == 'BJ01', 'Serien hinter den festen Waffen')
    ok(D['series']['failed'][0]['id'] == 'BJ16' and D['format'] == ego['format'], 'Durchgefallene in ego_series.json')
    SP.not_playable = real

# 0.44: BALLON_EXPORT_FORCE backt nur die Genannten, Tippfehler stoppen
from tools import export_unity as EU  # noqa: E402
plan, why = EU.force_full({'A': 'reuse', 'B': 'reuse'}, {}, 'B')
ok(plan == {'A': 'reuse', 'B': 'full'} and list(why) == ['B'], f'Erzwingen {plan}')
ok(EU.force_full({'A': 'reuse'}, {}, '') == ({'A': 'reuse'}, {}), 'Erzwingen ohne Angabe')
try:
    EU.force_full({'A': 'reuse'}, {}, 'X')
    bad.append('unbekannte Waffe still übergangen')
except SystemExit:
    pass

# 0.44: Vergleich der festen Waffen: Haltungen aus den Daten, fehlende Bilder brechen ab
from tools import bake_ego_compare as BC  # noqa: E402
ok(BC.own_poses(dict(actions=[dict(name='fire_a')])) == ('hip',) and BC.own_poses(dict(actions=[dict(name='aim_in')])) == ('hip', 'ads'), 'Haltungen im Vergleich')
own = {w[0]: w[2] for w in BC.own_weapons()}
ok(own['BASIC-T01-v2.1'] == ('hip',) and own['BASIC-01-v2.1'] == ('hip', 'ads') and len(own) >= 18, f'Haltungen aus ego.json: {len(own)}')
import shutil  # noqa: E402
if shutil.which('magick'):
    with tempfile.TemporaryDirectory() as t:
        BC.EV = t
        was = BC.own_weapons
        BC.own_weapons = lambda only='': [('BASIC-01-v2.1', 1, ('hip',))]
        try:
            BC.own_compare('a', 'b')
            bad.append('Vergleich ohne Bilder meldet Erfolg')
        except subprocess.CalledProcessError as e:
            ok(any('hip_unity.png' in str(x) for x in e.cmd), f'anderer Fehler als das fehlende Bild: {e.cmd}')
        # Erfolgsfall und Grenze: gleiche Bilder bestehen, ein verändertes Viewmodel fällt unter ego_vm_ssim
        for tag, extra in (('a', []), ('b', []), ('c', ['-fill', 'black', '-draw', 'rectangle 40,40 90,90'])):
            d = os.path.join(t, 'ego_eigene', tag, 'BASIC-01-v2.1')
            os.makedirs(d)
            subprocess.run(['magick', '-size', '128x128', 'gradient:gray60-gray90', *extra, os.path.join(d, 'hip_unity.png')], check=True)
            subprocess.run(['magick', '-size', '128x128', 'xc:white', os.path.join(d, 'hip_mask.png')], check=True)
        ok(BC.own_compare('a', 'b') == 0, 'gleiche Bilder fallen durch')
        ok(BC.own_compare('a', 'c') == 1, 'verändertes Viewmodel besteht die Grenze')
        BC.own_weapons = was
elif os.environ.get('GITHUB_ACTIONS') == 'true':   # PR-Check auf Linux ohne ImageMagick 7: wie test_texture_store
    print('Hinweis: magick fehlt im PR-Check – Bildvergleich in test_series nur auf dem Mac')
else:
    bad.append('magick (ImageMagick 7) fehlt')

print(f'Serien: {len(bad)} Fehler' if bad else 'Serien: Pin, Inhalts-Cache (zweiter Lauf ohne Backen), nichts im Repo – geprüft')
for b in bad:
    print('  ✗', b)
sys.exit(1 if bad else 0)
