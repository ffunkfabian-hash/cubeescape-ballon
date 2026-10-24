"""Baut alle (oder ausgewählte) BASIC-Waffen nacheinander in Blender.

  python3 tools/build_all.py [w01 w07 …] [--views] [--motion] [--gpu] [--only hero,side] [--samples N] [--res N]
Die Sperre setzt der Aufrufer: ~/Claude/cubeescape-nexogen/ce lock gpu -- python3 tools/build_all.py … --gpu
"""
import glob
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLENDER = os.environ.get('BLENDER', '/Applications/Blender.app/Contents/MacOS/Blender')


def main(argv):
    sel = [a for a in argv if not a.startswith('--') and a.startswith('w')]
    flags = [a for a in argv if a not in sel]
    mods = sorted(os.path.basename(f)[:-3] for f in glob.glob(os.path.join(ROOT, 'basic', 'weapons', 'w*.py')))
    if sel:
        mods = [m for m in mods if any(m.startswith(s) for s in sel)]
    fails = []
    for m in mods:
        t = time.time()
        r = subprocess.run([BLENDER, '-b', '--factory-startup', '-P', os.path.join(ROOT, 'tools', 'blender_build.py'), '--', m]
                           + flags, capture_output=True, text=True)
        lines = [ln for ln in (r.stdout + r.stderr).splitlines() if '[basic]' in ln or 'Error' in ln or 'Traceback' in ln]
        print(f'{m}: {time.time() - t:.0f} s', *lines, sep='\n  ')
        if r.returncode or any('Traceback' in ln for ln in lines):
            fails.append(m)
            print('\n'.join((r.stdout + r.stderr).splitlines()[-15:]))
    print('Fehler:', fails or 'keine')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
