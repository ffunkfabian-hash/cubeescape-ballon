"""Design-Serien aus Formgen v2 lokal spielbar machen (0.43 „Kiln“); `python3 tools/unity_run.py setup` ruft das vor dem Unity-Import auf.

  python3 tools/series_packages.py            → Datensätze holen, Fehlendes backen (unter `ce lock gpu`), einrichten, ego_series.json schreiben
  python3 tools/series_packages.py --status   → nur zeigen, was im Cache liegt und was gebacken werden müsste (ohne Blender)
  python3 tools/series_packages.py --only BJ01,BK05   → nur diese Blätter (Prüfläufe)
  python3 tools/series_packages.py --fixed BD01,BG01  → feste Varianten im Repo neu backen, nach Generated/Formgen/<ID>/ (0.44; danach `export_unity.py --formgen`)
  BALLON_NO_SERIES=1: setup ohne Serien.

Weg: `data/formgen_series.json` pinnt Formgen v2 auf einen Commit. Daraus entsteht je Blatt ein Auftrag (Formgens eigener Code aus `git archive`,
in dessen .venv: `asset.plan`/`bake_plan`: Datensatz `model`, Grundmodul, Skin der Linie). Gebacken wird mit Formgens unverändertem
`formgen/blender/asset_build.py`, aber auf **BALLONs heutigem Stand** (`snapshot` = dieses Repo), also mit den Bake-Einstellungen von hier, nicht
denen von Formgens BALLON-Pin. Ergebnis ist ein Paket Format 2 im Inhalts-Cache `~/Library/Caches/CubeEscapeBallon/series/pk/<Schlüssel>/`; der
Schlüssel hängt am Datensatz, an Skin, Bake-Einstellungen, Blender-Version und am Bake-Code (`code_files`), nicht an Commits. Ein zweiter
Lauf ohne Änderung backt nichts. Eingerichtet wird nach `Generated/FormgenSeries/<ID>/` (gitignoriert, APFS-Klon); `formgen_import.entry`
prüft jedes Paket wie die festen Varianten. Abgelehntes wird nicht still ausgelassen: Liste in der Ausgabe, in `series.failed` und im Bericht.
"""
import argparse
import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
PIN = os.path.join(ROOT, 'data', 'formgen_series.json')
CACHE = os.environ.get('BALLON_SERIES_CACHE', os.path.expanduser('~/Library/Caches/CubeEscapeBallon/series'))
GEN = os.path.join(ROOT, 'unity', 'Assets', 'Ballon', 'Generated')
DST = os.path.join(GEN, 'FormgenSeries')
FIXED = os.path.join(GEN, 'Formgen')               # feste Varianten (im Repo, 0.41), Paket wie die Serien
OUT_JSON = os.path.join(DST, 'Resources', 'ego_series.json')
BLENDER = os.environ.get('BLENDER', '/Applications/Blender.app/Contents/MacOS/Blender')
CE = os.path.expanduser('~/Claude/cubeescape-nexogen/ce')
PACKAGE_VERSION = 2
# BALLON-Code, der das Paket bestimmt. export_unity.py nur mit den Funktionen des Backens: sein übriger Inhalt (Datenexport) ändert sich oft und
# geht beim Einlesen ohnehin mit dem heutigen Stand in den Eintrag ein, er soll nicht 60 Waffen neu backen.
CODE_FILES = ('basic/kit.py', 'basic/common.py', 'basic/variant.py', 'tools/bake_unity.py', 'tools/blender_build.py', 'tools/skin_masks.py')
EXPORT_PARTS = ('TEXTURE_STORE', 'bake_weapon', 'store_texture', 'store_textures', 'export_fbx', 'parts_sha', '_identify')
SCENE_PARTS = ('Denoiser',)                        # scene_build.py: nur der Entrauscher des AO, der Rest ist Szene

DRIVER = r'''
import json, sys
from formgen import asset, ballon, ballon_kit, variants
lines = set(sys.argv[1].split(","))
cfg = asset.settings()
sheets = {k: v for k, v in variants.sheets().items() if v["variant"]["letter"] in lines}
glb = asset.plan(sheets, ballon_kit.snapshot(), ballon.snapshot(), cfg)
jobs = []
for a in asset.bake_plan(glb, cfg, True):
    v = sheets[a.model_id]["variant"]
    jobs.append(dict(id=a.model_id, module=a.inputs["module"], model=a.inputs["model"], base=a.inputs["base"], skin=a.params["skin"],
                     skin_def=a.inputs.get("skin_def"), series=v["letter"], series_name=v["name"], num=sheets[a.model_id]["num"]))
json.dump(jobs, sys.stdout, ensure_ascii=False)
'''


class SeriesError(RuntimeError):
    pass


def pin(path=PIN):
    p = json.load(open(path, encoding='utf-8'))
    c = p.get('commit', '')
    if len(c) != 40 or any(x not in '0123456789abcdef' for x in c):
        raise SeriesError(f'{path}: commit muss eine volle SHA-1 sein')
    if not p.get('lines') or not p.get('bake'):
        raise SeriesError(f'{path}: lines oder bake fehlt')
    return p


def source(p):
    """Formgen am Pin als entpackter Stand (einmal, atomar). Das Repo wird nur gelesen."""
    target = os.path.join(CACHE, 'src', p['commit'])
    if os.path.exists(os.path.join(target, '.complete')):
        return target
    repo = os.path.expanduser(p['repo'])
    if subprocess.run(['git', '-C', repo, 'cat-file', '-e', p['commit'] + '^{commit}'], capture_output=True).returncode:
        raise SeriesError(f"Formgen-Commit {p['commit'][:12]} fehlt in {repo} (dort `git fetch origin`)")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='.src-', dir=os.path.dirname(target))
    try:
        tar = subprocess.run(['git', '-C', repo, 'archive', '--format=tar', p['commit']], capture_output=True, check=True).stdout
        subprocess.run(['tar', '-x', '-C', tmp], input=tar, check=True)
        open(os.path.join(tmp, '.complete'), 'w').write(p['commit'] + '\n')
        shutil.rmtree(target, ignore_errors=True)
        os.replace(tmp, target)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return target


def formgen_python(p):
    py = os.environ.get('BALLON_FORMGEN_PY') or os.path.join(os.path.expanduser(p['repo']), '.venv', 'bin', 'python')
    if not os.path.exists(py):
        raise SeriesError(f'Python von Formgen fehlt: {py} (dort .venv anlegen oder BALLON_FORMGEN_PY setzen)')
    return py


def plan_jobs(p, src):
    """Aufträge aller Blätter der Linien; hängen nur am Pin, darum je Commit und Linien gemerkt."""
    path = os.path.join(CACHE, 'jobs', f"{p['commit']}-{''.join(p['lines'])}.json")
    if os.path.exists(path):
        return json.load(open(path, encoding='utf-8'))
    r = subprocess.run([formgen_python(p), '-c', DRIVER, ','.join(p['lines'])], cwd=src, capture_output=True, text=True,
                       env=dict(os.environ, PYTHONPATH=src))
    if r.returncode:
        raise SeriesError('Formgen-Aufträge fehlgeschlagen:\n' + r.stderr[-1500:])
    jobs = json.loads(r.stdout)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + '.tmp', 'w', encoding='utf-8') as fh:
        json.dump(jobs, fh, ensure_ascii=False)
    os.replace(path + '.tmp', path)
    return jobs


def export_source(path, parts=EXPORT_PARTS):
    """Quelltext der Teile einer Datei, die das Paket bestimmen (export_unity.py, scene_build.py)."""
    text = open(path, encoding='utf-8').read()
    out = {}
    for n in ast.parse(text).body:
        name = getattr(n, 'name', None) or (n.targets[0].id if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) else None)
        if name in parts:
            out[name] = ast.get_source_segment(text, n)
    return out


def code_files(root=ROOT):
    return {**{f: hashlib.sha256(open(os.path.join(root, f), 'rb').read()).hexdigest() for f in CODE_FILES},
            'export_unity': hashlib.sha256(json.dumps(export_source(os.path.join(root, 'tools', 'export_unity.py')), sort_keys=True).encode()).hexdigest(),
            'scene_build': hashlib.sha256(json.dumps(export_source(os.path.join(root, 'tools', 'scene_build.py'), SCENE_PARTS), sort_keys=True).encode()).hexdigest()}


def blender_version():
    return subprocess.run([BLENDER, '--version'], capture_output=True, text=True, check=True).stdout.splitlines()[0].strip()


def job_key(job, bake, code, blender, script_sha, module_sha):
    """Inhaltsschlüssel eines Pakets. Keine Commits, keine Zeit: gleiche Eingaben = gleicher Schlüssel."""
    data = dict(model=job['model'], module=job['module'], module_sha=module_sha, skin=job['skin'], skin_def=job.get('skin_def'), bake=bake, code=code,
                blender=blender, script=script_sha, package=PACKAGE_VERSION, id=job['id'])
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def module_hash(module):
    path = os.path.join(ROOT, *module.split('.')) + '.py'
    return hashlib.sha256(open(path, 'rb').read()).hexdigest() if os.path.exists(path) else ''


def not_playable(job):
    """Grund, warum ein Blatt in BALLON nicht spielbar ist (BASIC-16/17 ohne Ego-Klasse), bevor Zeit ins Backen geht; sonst None."""
    import importlib
    from basic import variant as VA
    from basic.arms import ego as EG
    try:
        W = VA.as_module(job['model'], importlib.import_module(job['module']), name=f"basic.variant.{job['id']}")
        EG.profile(W)
    except (KeyError, ValueError, ImportError, AttributeError) as e:
        return f'{type(e).__name__}: {e}'[:200]
    return None


def package_dir(key):
    return os.path.join(CACHE, 'pk', key)


def cached(key):
    return os.path.exists(os.path.join(package_dir(key), '.complete'))


def installed(sid, key):
    """Paket mit diesem Schlüssel schon eingerichtet? Es zählt wie ein Cache-Treffer: ein leerer Cache (0.44) backt nicht neu, was in Unity liegt."""
    stamp = os.path.join(DST, sid, '.series_key')
    return os.path.exists(stamp) and open(stamp).read().strip() == key


def bake_one(job, key, bake, script, snapshot=ROOT):
    """Ein Paket in den Cache backen (eigene Blender-Instanz). snapshot: BALLON-Stand, der backt (Vergleich: tools/bake_ego_compare.py). Gibt die Zeit in s
    zurück; wirft SeriesError mit dem Ende des Protokolls."""
    target = package_dir(key)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='.bake-', dir=os.path.dirname(target))
    t0 = time.time()
    try:
        out = os.path.join(tmp, job['id'])
        os.makedirs(out)
        path = os.path.join(tmp, 'job.json')
        json.dump(dict(snapshot=snapshot, module=job['module'], model=job['model'], id=job['id'], out=out, package=True, skin=job['skin'],
                       skin_def=job.get('skin_def'), atlas=bake['size'], samples=bake.get('samples'), gpu=bake.get('device', 'gpu') == 'gpu',
                       package_version=PACKAGE_VERSION), open(path, 'w', encoding='utf-8'), ensure_ascii=False)
        r = subprocess.run([BLENDER, '-b', '--factory-startup', '-P', script, '--', path], capture_output=True, text=True)
        text = r.stdout + r.stderr
        if r.returncode or 'Traceback' in text or f"[formgen-asset] {job['id']}:" not in text:
            raise SeriesError('Blender: ' + ' | '.join(text.splitlines()[-6:])[:600])
        shutil.rmtree(os.path.join(out, '_ballon_out'), ignore_errors=True)
        glb = os.path.join(out, f"{job['id']}.glb")
        if os.path.exists(glb):
            os.remove(glb)                                    # Unity braucht nur das FBX
        open(os.path.join(out, '.complete'), 'w').write(key + '\n')
        shutil.rmtree(target, ignore_errors=True)
        os.replace(out, target)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return time.time() - t0


def install(job, key, root=None):
    """Paket aus dem Cache nach Generated/FormgenSeries/<ID>/ (APFS-Klon); gleicher Schlüssel: nichts anfassen, Unity importiert nicht neu.
    root: anderer Zielordner ohne Schlüsseldatei (feste Varianten, im Repo)."""
    dst = os.path.join(root or DST, job['id'])
    stamp = os.path.join(dst, '.series_key')
    if not root and installed(job['id'], key):
        return False
    os.makedirs(root or DST, exist_ok=True)
    metas = {}
    if os.path.isdir(dst):                                    # .meta behalten: GUIDs der Materialien bleiben gültig
        for base, _, names in os.walk(dst):
            for n in names:
                if n.endswith('.meta'):
                    metas[os.path.relpath(os.path.join(base, n), dst)] = open(os.path.join(base, n), 'rb').read()
        shutil.rmtree(dst)
    if subprocess.run(['cp', '-cR', package_dir(key), dst], capture_output=True).returncode:
        shutil.copytree(package_dir(key), dst)
    os.remove(os.path.join(dst, '.complete'))
    for rel, data in metas.items():
        path = os.path.join(dst, rel)
        if os.path.exists(path[:-5]):
            open(path, 'wb').write(data)
    if not root:
        open(stamp, 'w').write(key + '\n')
    return True


def merged_ego(entries, failed, p):
    D = json.load(open(os.path.join(GEN, 'ego.json'), encoding='utf-8'))
    D['weapons'] = [e for e in D['weapons'] if not e.get('dir', '').startswith('FormgenSeries/')] + entries
    D['series'] = dict(de='Lokal erzeugt (tools/series_packages.py), nicht im Repo', formgen=p['commit'], version=p.get('version', ''), lines=p['lines'],
                       bake=p['bake'], weapons=[e['id'] for e in entries], failed=failed)
    return D


def remove_stale(keep):
    if not os.path.isdir(DST):
        return []
    gone = []
    for d in sorted(os.listdir(DST)):
        path = os.path.join(DST, d)
        if os.path.exists(os.path.join(path, '.series_key')) and d not in keep:
            shutil.rmtree(path)
            if os.path.exists(path + '.meta'):
                os.remove(path + '.meta')
            gone.append(d)
    return gone


def prepare(jobs, p, code, blender, script_sha):
    """(nicht Spielbares, {ID: Schlüssel}, Aufträge ohne Cache-Treffer)."""
    failed, keys, todo = [], {}, []
    for j in jobs:
        why = not_playable(j)
        if why:
            failed.append(dict(id=j['id'], step='Ego-Profil', reason=why))
            continue
        keys[j['id']] = job_key(j, p['bake'], code, blender, script_sha, module_hash(j['module']))
        if not cached(keys[j['id']]) and not installed(j['id'], keys[j['id']]):
            todo.append(j)
    return failed, keys, todo


def bake_all(todo, keys, p, script, baker=bake_one):
    """Fehlendes nacheinander backen (eine GPU); ein Fehler stoppt die anderen nicht, das Einrichten meldet ihn."""
    log = os.path.join(CACHE, 'bake_log.csv')
    for i, j in enumerate(todo):
        try:
            s = baker(j, keys[j['id']], p['bake'], script)
            print(f"[{i + 1}/{len(todo)}] {j['id']}: {s:.0f} s", flush=True)
            with open(log, 'a') as fh:
                fh.write(f"{time.strftime('%F %T')},{j['id']},{s:.1f},{p['bake']['size']}\n")
        except SeriesError as e:
            print(f"[{i + 1}/{len(todo)}] {j['id']}: FEHLER {e}", flush=True)


def install_all(jobs, keys, failed, p, only=False):
    """Pakete einrichten, einlesen, ego_series.json schreiben. Gibt (Einträge, Durchgefallene, neu eingerichtet) zurück."""
    from tools import formgen_import as FI
    entries, failed, changed = [], list(failed), 0
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    for j in jobs:
        key = keys.get(j['id'])
        if key is None:
            continue
        if not cached(key) and not installed(j['id'], key):
            failed.append(dict(id=j['id'], step='Backen', reason='kein Paket im Cache (Protokoll oben)'))
            continue
        changed += install(j, key)
        try:
            e = FI.entry(os.path.join(DST, j['id']))
        except (FI.PackageError, KeyError, ValueError, FileNotFoundError) as err:
            failed.append(dict(id=j['id'], step='Einlesen', reason=str(err)[:300]))
            continue
        e['origin'].update(series=j['series'], series_name=j['series_name'])
        entries.append(e)
    gone = [] if only else remove_stale({e['id'] for e in entries})
    failed.sort(key=lambda f: f['id'])
    with open(OUT_JSON + '.tmp', 'w', encoding='utf-8') as fh:
        json.dump(merged_ego(entries, failed, p), fh, ensure_ascii=False, indent=1)
    os.replace(OUT_JSON + '.tmp', OUT_JSON)
    print(f'Serien eingerichtet: {len(entries)} Waffen ({changed} neu, {len(gone)} entfernt) → {os.path.relpath(DST, ROOT)}', flush=True)
    for f in failed:
        print(f"  durchgefallen {f['id']} ({f['step']}): {f['reason']}", flush=True)
    return entries, failed, changed


def install_fixed(jobs, keys, failed):
    """Feste Varianten einrichten: alles oder nichts, ein Paket ohne Bake bleibt wie es ist. Das GLB entfällt mit dem Paket (bake_one), Unity nutzt das FBX."""
    missing = [f['id'] for f in failed] + [j['id'] for j in jobs if j['id'] in keys and not cached(keys[j['id']])]
    if missing:
        raise SeriesError(f'Nicht gebacken, nichts eingerichtet: {missing}')
    for j in jobs:
        install(j, keys[j['id']], FIXED)
        print(f"Feste Variante {j['id']} → {os.path.relpath(os.path.join(FIXED, j['id']), ROOT)}", flush=True)
    return 0


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument('--status', action='store_true')
    a.add_argument('--only', default='')
    a.add_argument('--fixed', default='', help='feste Varianten neu backen (IDs, Komma)')
    a.add_argument('--bake-only', action='store_true', help='innerer Lauf unter ce lock gpu')
    o = a.parse_args(argv)
    p = pin()
    src = source(p)
    if o.fixed:
        p = dict(p, lines=sorted({i[1] for i in o.fixed.split(',')}))
    jobs = plan_jobs(p, src)
    if o.only or o.fixed:
        want = set((o.only or o.fixed).split(','))
        unknown = want - {j['id'] for j in jobs}
        if unknown:
            raise SeriesError(f'Unbekannte Blätter: {sorted(unknown)}')
        jobs = [j for j in jobs if j['id'] in want]
    script = os.path.join(src, 'formgen', 'blender', 'asset_build.py')
    script_sha = hashlib.sha256(open(script, 'rb').read()).hexdigest()
    failed, keys, todo = prepare(jobs, p, code_files(), blender_version(), script_sha)
    print(f"Serien {''.join(p['lines'])} (Formgen {p['commit'][:7]}): {len(jobs)} Blätter, {len(keys) - len(todo)} im Cache, {len(todo)} zu backen, "
          f'{len(failed)} nicht spielbar', flush=True)
    if o.status:
        for f in failed:
            print(f"  nicht spielbar {f['id']}: {f['reason']}", flush=True)
        return 0
    if o.bake_only:
        bake_all(todo, keys, p, script)
        return 0
    if todo:
        r = subprocess.run([CE, 'lock', 'gpu', '--what', f'BALLON Serien backen ({len(todo)})', '--', sys.executable, os.path.abspath(__file__), '--bake-only'] +
                           (['--only', o.only] if o.only else []) + (['--fixed', o.fixed] if o.fixed else []))
        if r.returncode:
            raise SeriesError(f'Backen: Exit {r.returncode}')
    if o.fixed:
        return install_fixed(jobs, keys, failed)
    install_all(jobs, keys, failed, p, only=bool(o.only))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except SeriesError as e:
        print(f'Serien: {e}', flush=True)
        sys.exit(1)
