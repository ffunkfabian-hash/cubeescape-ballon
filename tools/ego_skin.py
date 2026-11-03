"""Ego-Standbilder einer BALLON-Waffe mit Skin in Blender (0.42 „Quickslot“) für den Vergleich mit Unity (tools/unity_run.py compare).

  BASIC_OUT=<Ordner> ce lock gpu -- blender -b --factory-startup -P <abs>/tools/ego_skin.py -- <modul> <skin> [--gpu]
  BALLON_BLENDER_STILLS=<Ordner>/<ID>/ego/stills python3 tools/unity_run.py compare <n> -ballonSkin <skin>

Seit 0.42 startet jede Waffe mit ihrem farbigen Standard-Skin (basic/loadout.DEFAULT_SKIN). Wie tools/ego_variant.py: der Skin gilt nur
an der Waffe, die Arme bleiben im Standard (wie der Arm-Atlas in Unity); danach läuft tools/ego_build.py --stills unverändert.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def main():
    a = sys.argv[sys.argv.index('--') + 1:]
    module, skin = a[0], a[1]
    import importlib
    from basic import kit
    if skin not in kit.SKINS:
        sys.exit(f'Skin {skin} nicht in kit.SKINS ({", ".join(kit.SKINS)})')
    W = importlib.import_module(f'basic.{module}')
    parts = {p['id'] for p in W.PARTS}
    set_mode = kit.set_mode

    def skinned(objs, mode):                       # Skin nur an der Waffe, Arme im Standard
        names = objs.keys() if isinstance(objs, dict) else [getattr(o, 'name', '') for o in objs]
        kit.SKIN['name'] = skin if parts & set(names) else 'standard'
        try:
            return set_mode(objs, mode)
        finally:
            kit.SKIN['name'] = 'standard'
    kit.set_mode = skinned
    sys.argv = [sys.argv[0], '--', '--stills', '--weapon', module] + (['--gpu'] if '--gpu' in a else [])
    from tools import ego_build as EB
    EB.main()
    print(f'[ego_skin] {module}: Standbilder mit Skin {skin}', flush=True)


main()
