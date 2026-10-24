"""Kopiert die gemessenen Specs aus der Bauausgabe ins Repo (data/specs/), damit Doku und Abnehmer eine versionierte Quelle haben."""
import glob
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.paths import OUT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dst = os.path.join(ROOT, 'data', 'specs')
os.makedirs(dst, exist_ok=True)
n = 0
for f in sorted(glob.glob(os.path.join(OUT, 'BASIC-*', 'BASIC-*.spec.json'))):
    shutil.copy2(f, dst)
    n += 1
print(f'{n} Specs nach {dst}')
