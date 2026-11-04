"""Ego-Standbilder einer Formgen-Variante in Blender (0.41 „Intake“) für den Vergleich mit Unity (tools/unity_run.py compare).

  BASIC_OUT=<Ordner> ce lock gpu -- blender -b --factory-startup -P <abs>/tools/ego_variant.py -- <Paketordner> [<datensatz.json>] [--skin-def <json>] [--gpu]

Die Variante entsteht wie beim Einlesen (tools/formgen_import.py) aus Grundmodul und Datensatz (basic/variant.as_module): Paket 2 trägt
den Datensatz (`model`), für ein Paket 1 (Formgen 0.6) wird er als Datei übergeben (Formgen `asset.variant_model`). Der Bauteil-Hash muss
zum Manifest passen (gleiche Form wie das FBX). Die Waffe trägt den Skin der Linie (wie ihr Atlas), die Arme den Standard (wie der
Arm-Atlas in Unity). --skin-def: Palette einer Design-Serie (Form wie kit.SKINS, 0.43), wenn der Skin nicht in kit.SKINS steht. Danach läuft tools/ego_build.py --stills unverändert; Bilder unter <BASIC_OUT>/<Grund-ID>/ego/stills/.
"""
import importlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def main():
    a = sys.argv[sys.argv.index('--') + 1:]
    folder = os.path.abspath(a[0])
    sid = os.path.basename(folder.rstrip('/'))
    M = json.load(open(os.path.join(folder, f'{sid}.package.json'), encoding='utf-8'))
    skin_def = None
    if '--skin-def' in a:
        i = a.index('--skin-def')
        skin_def = json.load(open(a[i + 1], encoding='utf-8'))
        a = a[:i] + a[i + 2:]
    extra = [x for x in a[1:] if not x.startswith('--')]
    data = M.get('model') or (json.load(open(extra[0], encoding='utf-8')) if extra else None)
    if data is None:
        sys.exit(f'{sid}: Paket ohne Datensatz – Datensatz als zweites Argument übergeben')
    from basic import variant, kit
    from tools import export_unity as EU
    if skin_def:
        kit.SKINS[M['skin']] = skin_def
    base = importlib.import_module(M['ballon']['module'])
    W = variant.as_module(data, base, name=f'basic.variant_{sid}')
    if EU.parts_sha(W) != M['ballon']['parts_sha256']:
        sys.exit(f'{sid}: Bauteil-Hash des Datensatzes passt nicht zum Paket')
    sys.modules[W.__name__] = W
    parts = {p['id'] for p in W.PARTS}
    set_mode = kit.set_mode

    def skinned(objs, mode):                       # Skin der Linie nur an der Waffe, Arme im Standard
        names = objs.keys() if isinstance(objs, dict) else [getattr(o, 'name', '') for o in objs]
        kit.SKIN['name'] = M.get('skin', 'standard') if parts & set(names) else 'standard'
        try:
            return set_mode(objs, mode)
        finally:
            kit.SKIN['name'] = 'standard'
    kit.set_mode = skinned
    sys.argv = [sys.argv[0], '--', '--stills', '--weapon', W.__name__.split('basic.', 1)[1]] + (['--gpu'] if '--gpu' in a else [])
    from tools import ego_build as EB
    EB.main()
    print(f'[ego_variant] {sid}: Standbilder mit Skin {M.get("skin")} (Grundmodul {M["ballon"]["module"]})', flush=True)


main()
