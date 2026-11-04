"""Bake-Einstellungen (0.43 „Kiln“) ohne Blender, Teil von ./check: gewählte Werte, 2048²/4096²-Schalter, Pin, Ablage vergrößert nie. Backen selbst: tools/test_bake_blender.py."""
import ast
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import tools.export_unity as XU  # noqa: E402

bad = []


def ok(c, what):
    if not c:
        bad.append(what)


src = open(os.path.join(ROOT, 'tools', 'bake_unity.py'), encoding='utf-8').read()
S = next(n for n in ast.parse(src).body
         if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'SETTINGS')
S = {k.arg: ast.literal_eval(k.value) for k in S.value.keywords}
want = json.load(open(os.path.join(ROOT, 'data', 'bake_settings.json'), encoding='utf-8'))
ok(S == want['settings'], f"SETTINGS {S} weicht von data/bake_settings.json ab (Änderung nur mit neuer Messung)")
ok(S['data_size'] == 2048, 'AO und Spec in 2048²')
ok(S['normal_size'] == XU.TEXTURE_STORE['normal']['size'] == 4096, 'Normale immer 4096²: bei 2048² fleckig beim Zielen')
ok(XU.TEXTURE_STORE['spec']['size'] == S['data_size'] and XU.TEXTURE_STORE['ao']['size'] == S['data_size'], 'Ablage von Spec und AO = Backgröße')
ok(want['size_default'] in (2048, 4096) and set(want['size_choices']) == {2048, 4096}, 'Schalter 2048/4096')
series = json.load(open(os.path.join(ROOT, 'data', 'formgen_series.json'), encoding='utf-8'))
ok(series['bake']['size'] == want['size_default'], 'Serien backen mit der gewählten Größe')
sig = next(n for n in ast.parse(open(os.path.join(ROOT, 'tools', 'export_unity.py'), encoding='utf-8').read()).body
           if isinstance(n, ast.FunctionDef) and n.name == 'bake_weapon')
names = [a.arg for a in sig.args.args]
ok(names[:10] == ['root', 'tex_dir', 'atlas_key', 'fbx', 'skins', 'gpu', 'arms', 'objs', 'rest', 'size'] and 'samples' in names, 'Schnittstelle für Formgen unverändert')

if XU.HAS_MAGICK:                                    # 2048²-Atlas bleibt 2048²; 8 bit AO, gedrehter Weg über die Ablage
    with tempfile.TemporaryDirectory() as t:
        for name, depth in (('a_albedo.png', 8), ('a_normal.png', 16), ('a_ao.png', 16), ('a_spec.png', 8)):
            subprocess.run(['magick', '-size', '32x32', 'plasma:', '-depth', str(depth), os.path.join(t, name)], check=True, capture_output=True)
        store = json.loads(json.dumps(XU.TEXTURE_STORE))
        for kind, f in (('albedo', 'a_albedo.png'), ('normal', 'a_normal.png'), ('ao', 'a_ao.png'), ('spec', 'a_spec.png')):
            out = XU.store_texture(t, f, kind)
            w = XU._identify(os.path.join(t, out))[0]
            ok(w == 32, f'{kind}: Ablage vergrößert auf {w}')
            ok(XU.store_texture(t, out, kind) == out, f'{kind}: zweite Ablage nicht wiederholbar')

print(f'Bake-Einstellungen: {len(bad)} Fehler' if bad else 'Bake-Einstellungen geprüft')
for b in bad:
    print('  ✗', b)
sys.exit(1 if bad else 0)
