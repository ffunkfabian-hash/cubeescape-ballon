"""Ausgabeorte (außerhalb des Repos, globale Regel › Belege)."""
import os

OUT = os.environ.get('BASIC_OUT', os.path.expanduser('~/Library/Caches/CubeEscapeBallon/out'))
EVIDENCE = os.environ.get('BASIC_EVIDENCE', os.path.expanduser('~/Library/Caches/CubeEscapeBallon/evidence'))
