"""Bake messen (0.43 „Kiln“): Zeit je Karte und Schritt für eine Waffe, Reihe mehrerer Waffen am Stück (Drosselung des lüfterlosen Macs).

Äußerer Lauf (Python, unter `ce lock gpu`, eine frische Blender-Instanz je Waffe wie Formgens Bake):
  python3 tools/bake_bench.py run --tag base --kit <Ordner mit basic/, tools/> --modules pilot.w01_auto_rifle_v21,… [--size 4096] [--opts '{…}']
Ergebnis: <EV>/kiln/bench/<tag>/<nn>_<Waffe>/timing.json (Schritte in s) und <tag>/summary.csv. --kit: gepinnter Stand für vorher/nachher.
Innerer Lauf (Blender): blender -b --factory-startup -P tools/bake_bench.py -- <job.json>
Geplant wie der Formgen-Weg: blender_build.main, setup_render(aaa, mid), export_unity.bake_weapon(arms=False), store_textures. Die Zeiten
kommen von Hüllen um die Schritte in bake_unity/export_unity, gemessen wird also derselbe Code, den der Stand unter --kit mitbringt.
"""
import csv
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV = os.environ.get('BALLON_KILN_EVIDENCE', os.path.expanduser('~/Library/Caches/CubeEscapeBallon/kiln'))
BLENDER = os.environ.get('BLENDER', '/Applications/Blender.app/Contents/MacOS/Blender')


def inner():
    job = json.load(open(sys.argv[sys.argv.index('--') + 1], encoding='utf-8'))
    t_start = time.time()
    out = job['out']
    os.environ['BASIC_OUT'] = os.path.join(out, '_build')
    sys.path.insert(0, job['kit'])
    import importlib
    import bpy
    from basic import kit
    import tools.blender_build as BB
    import tools.bake_unity as BK
    import tools.export_unity as EU
    steps = []

    def timed(mod, name, label=None):
        f = getattr(mod, name)

        def wrap(*a, **k):
            t = time.time()
            try:
                return f(*a, **k)
            finally:
                what = label or name
                if name == '_bake':
                    what = f"bake:{a[3]}:{(a[5] if len(a) > 5 else k.get('channel')) or ''}:{a[2].name}:{a[4]}"
                steps.append((what, round(time.time() - t, 2)))
        setattr(mod, name, wrap)
    for n in ('apply_modifiers', 'unwrap', '_joined', '_bake', 'bake_atlas'):
        timed(BK, n)
    for n in ('export_fbx', 'store_textures'):
        timed(EU, n)
    W = importlib.import_module(f"basic.{job['module']}")
    BB.main(argv=[job['module']])
    steps.append(('build', round(time.time() - t_start, 2)))
    objs = {p['id']: bpy.data.objects[p['id']] for p in W.PARTS}
    root = bpy.data.objects[W.META['id']]
    t = time.time()
    BB.setup_render(854, 1, gpu=job['gpu'], aaa=True, bloom=False, bg='mid')
    kit.set_mode(objs, 'aaa')
    steps.append(('setup_render', round(time.time() - t, 2)))
    tex_dir = os.path.join(out, 'textures')
    os.makedirs(tex_dir, exist_ok=True)
    name = job['id']
    tex = EU.bake_weapon(root, tex_dir, name, fbx=os.path.join(out, f'{name}.fbx'), skins=False, gpu=job['gpu'], arms=False, objs=objs,
                         **job.get('bake', {}))
    tex = EU.store_textures(tex, tex_dir)
    total = time.time() - t_start
    json.dump(dict(id=name, module=job['module'], total_s=round(total, 1), steps=steps, parts=len(W.PARTS),
                   tris=sum(len(o.data.loop_triangles) if o.type == 'MESH' else 0 for o in bpy.data.objects),
                   textures=tex), open(os.path.join(out, 'timing.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'[bake_bench] {name}: {total:.1f} s', flush=True)


def therm():
    return ' '.join(subprocess.run(['pmset', '-g', 'therm'], capture_output=True, text=True).stdout.split())[:160]


def outer(argv):
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('cmd')
    p.add_argument('--tag', required=True)
    p.add_argument('--kit', default=ROOT)
    p.add_argument('--modules', required=True)
    p.add_argument('--bake', default='{}', help='JSON: Argumente für bake_weapon (size, samples, …)')
    p.add_argument('--cpu', action='store_true')
    a = p.parse_args(argv)
    base = os.path.join(EV, 'bench', a.tag)
    os.makedirs(base, exist_ok=True)
    rows = []
    t_run = time.time()
    for i, m in enumerate(a.modules.split(',')):
        name = m.split('.')[-1]
        out = os.path.join(base, f'{i:02d}_{name}')
        os.makedirs(out, exist_ok=True)
        path = os.path.join(out, 'job.json')
        json.dump(dict(kit=a.kit, module=m, id=name, out=out, gpu=not a.cpu, bake=json.loads(a.bake)), open(path, 'w', encoding='utf-8'))
        t = time.time()
        with open(os.path.join(out, 'blender.log'), 'w', encoding='utf-8') as log:
            r = subprocess.run([BLENDER, '-b', '--factory-startup', '-P', os.path.abspath(__file__), '--', path], stdout=log, stderr=subprocess.STDOUT)
        wall = time.time() - t
        ok = r.returncode == 0 and os.path.exists(os.path.join(out, 'timing.json'))
        rows.append(dict(i=i, weapon=name, wall_s=round(wall, 1), since_start_s=round(time.time() - t_run), ok=ok, therm=therm()))
        print(f"[{a.tag}] {i:02d} {name}: {wall:.0f} s {'ok' if ok else 'FEHLER'} (seit Start {rows[-1]['since_start_s']} s)", flush=True)
        if not ok:
            break
    with open(os.path.join(base, 'summary.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return 0 if all(r['ok'] for r in rows) else 1


if __name__ == '__main__':
    if '--' in sys.argv and sys.argv[sys.argv.index('--') + 1].endswith('job.json'):
        inner()
    else:
        sys.exit(outer(sys.argv[1:]))
