"""Formgen-Varianten in Unity (0.41 „Intake“): Pakete aus Formgen v2 einlesen und als Einträge von ego.json weapons[] anbieten.

Ordnerkonvention: unity/Assets/Ballon/Generated/Formgen/<ID>/ enthält ein Paket, wie Formgen es entpackt
(`python -m formgen.asset --bake <IDs> --unpack unity/Assets/Ballon/Generated/Formgen`): <ID>.package.json (formgenv2/weapon-package),
<ID>.fbx, textures/<ID>_albedo.jpg|_spec.png|_normal.png|_ao.png, <ID>.spec.json (GLB nur in Formgens eigenem Entpacken; `series_packages.py --fixed` lässt es weg, 0.44). BALLON ändert dort nichts; der Eintrag
entsteht in tools/export_unity.data() (also auch in `--check`) und landet mit dem nächsten Export bzw. `export_unity.py --formgen` in
ego.json. Der Unity-Import (BallonSetup) liest Pfade relativ zu `dir` (Generated/<dir>).

Eintrag = BALLON-Grundtyp (Grundmodul aus dem Manifest, ego.profile: Haltungen, Aktionen, Gameplay, Wirkung – vorerst geerbt, Tabelle f)
plus das, was die Variante selbst mitbringt:
  - Paket mit Datensatz (`model`: META/PARTS/ASSEMBLIES/ANCHORS/POINTS/ACTIONS, ab Formgen-Paket 2): Waffe aus basic/variant.as_module,
    alles mit BALLONs heutigem Code (weapon_entry); Bauteil-Hash muss zum Manifest passen (sonst passt das FBX nicht).
  - Paket ohne Datensatz (Formgen 0.6, Paket 1): `weapon` aus dem Manifest (Teile, Anker, Auswurf, Live-Teile – von BALLONs Code am
    Pin gerechnet) und die Weltpunkte (Griffkontakte) der Grundform. Das ist nur richtig, solange die Teile dieser Punkte unverändert sind:
    `point_problems` vergleicht ihre Netzgrenzen (Spec der Variante gegen data/specs der Grundform) und lehnt das Paket sonst ab.
"""
import hashlib
import importlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic import variant as VA  # noqa: E402

DIR = os.path.join(ROOT, 'unity', 'Assets', 'Ballon', 'Generated', 'Formgen')
FORMAT = 'formgenv2/weapon-package'
VERSIONS = (1, 2)                     # 1: Formgen 0.6 (ohne Datensatz), 2: mit `model` (Vorschlag an Formgen, 0.41)
TOL_MM = 0.05                         # Netzgrenzen gleich (Rundung der Spec auf 0,1 mm bzw. µm)


class PackageError(ValueError):
    pass


def packages(folder=None):
    """Paketordner unter Generated/Formgen (sortiert nach ID): nur Ordner mit <ID>.package.json."""
    folder = folder or DIR
    if not os.path.isdir(folder):
        return []
    return [os.path.join(folder, d) for d in sorted(os.listdir(folder))
            if os.path.isfile(os.path.join(folder, d, f'{d}.package.json'))]


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def load(folder):
    """Manifest eines Paketordners, geprüft: Format, ID = Ordnername, FBX, Spec und alle Texturen vorhanden, Waffe mit Ego-Profil."""
    sid = os.path.basename(folder.rstrip('/'))
    path = os.path.join(folder, f'{sid}.package.json')
    M = json.load(open(path, encoding='utf-8'))
    if M.get('format') != FORMAT or M.get('format_version') not in VERSIONS:
        raise PackageError(f"{sid}: Format {M.get('format')}/{M.get('format_version')} statt {FORMAT} {VERSIONS}")
    if M.get('id') != sid:
        raise PackageError(f"{sid}: Manifest-ID {M.get('id')} passt nicht zum Ordner")
    if M.get('weapon') is None:
        raise PackageError(f"{sid}: ohne weapon-Block (Formgen: {M.get('ego_profile_error') or 'kein Ego-Profil'})")
    files = [M['fbx'], f'{sid}.spec.json'] + [os.path.join('textures', f) for f in texture_files(M['textures'])]
    missing = [f for f in files if not os.path.isfile(os.path.join(folder, f))]
    if missing:
        raise PackageError(f'{sid}: Dateien fehlen: {missing}')
    if M.get('format_version', 1) >= 2 and not M.get('model'):
        raise PackageError(f'{sid}: Paket 2 ohne Datensatz model')
    return M


def texture_files(T):
    fs = {T['weapon'][k] for k in ('albedo', 'spec', 'normal', 'ao')}
    for s in T.get('skins', []):
        fs |= {s['albedo'], s['spec']}
    return sorted(fs)


def _author(pos):
    """Blender-Waffenrahmen (m: rechts −X … wie export_unity.xyz) → Autorenmaß (f, u, x) mm."""
    return (round(-pos[1] * 1000, 3) + 0.0, round(pos[2] * 1000, 3) + 0.0, round(pos[0] * 1000, 3) + 0.0)


def _bounds(spec):
    return {p['id']: p['bounds_m'] for p in spec['parts']}


def point_problems(base, spec, W0):
    """Paket ohne Datensatz: Weltpunkte der Grundform gelten nur, wenn ihr Teil in der Variante dieselben Netzgrenzen hat wie in der
    Grundform (sonst wäre der Punkt verschoben worden). Fehlerliste."""
    b0, b1 = _bounds(base), _bounds(spec)
    bad = []
    for name, P in sorted(W0.POINTS.items()):
        part = P['part']
        if part not in b1:
            bad.append(f'{name}: Teil {part} fehlt in der Variante')
            continue
        d = max(abs(a - b) * 1000 for k in ('min', 'max') for a, b in zip(b0[part][k], b1[part][k]))
        if d > TOL_MM:
            bad.append(f'{name}: Teil {part} verändert ({d:.1f} mm) – Paket mit Datensatz (POINTS) nötig')
    return bad


def entry(folder, EU=None):
    """Eintrag von ego.json weapons[] für ein Formgen-Paket (mit textures und mesh_bounds aus dem Paket, ohne Blender)."""
    if EU is None:
        from tools import export_unity as EU
    from basic.arms import ego as EG
    M = load(folder)
    sid = M['id']
    rel = os.path.relpath(folder, os.path.dirname(DIR)).replace(os.sep, '/')
    rel = 'Formgen/' + sid if rel.startswith('..') else rel           # Pakete außerhalb (Tests): Pfad wie im Unity-Projekt
    spec = json.load(open(os.path.join(folder, f'{sid}.spec.json'), encoding='utf-8'))
    base_mod = importlib.import_module(M['ballon']['module'])
    base_id = EG.weapon_id(base_mod)
    if base_id != M['ballon']['weapon_id']:
        raise PackageError(f"{sid}: Grundmodul {M['ballon']['module']} ist {base_id}, Manifest nennt {M['ballon']['weapon_id']}")
    own_points = bool(M.get('model', {}).get('POINTS'))
    if M.get('model'):
        W = VA.as_module(M['model'], base_mod, name=f'basic.variant.{sid}')
        if EU.parts_sha(W) != M['ballon']['parts_sha256']:
            raise PackageError(f'{sid}: Bauteil-Hash des Datensatzes passt nicht zum Manifest (FBX aus anderem Stand)')
        weapon = None
        points = 'Datensatz des Pakets mit POINTS' if own_points else 'Grundform (Datensatz ohne POINTS; Teile der Punkte unverändert geprüft)'
        bad = VA.problems(W) if own_points else []     # Richter 0.41: POINTS vollständig, Teilbezüge vorhanden (kein halber Satz)
        if bad:
            raise PackageError(f'{sid}: Weltpunkte im Datensatz unvollständig: ' + '; '.join(bad))
    else:
        anchors = {a['id']: dict(at=_author(a['pos']), part=a['part']) for a in M['weapon']['anchors']}
        W = VA.as_module(dict(ANCHORS=anchors), base_mod, name=f'basic.variant.{sid}')
        weapon, points = M['weapon'], 'Grundform (Paket ohne Datensatz; Teile der Punkte unverändert geprüft)'
    if not own_points:
        base_spec = json.load(open(os.path.join(ROOT, 'data', 'specs', f'{base_id}.spec.json'), encoding='utf-8'))
        bad = point_problems(base_spec, spec, base_mod)
        if bad:
            raise PackageError(f'{sid}: ' + '; '.join(bad))
    e = EU.weapon_entry(W, atlas_key=f'formgen_{sid}', spec=spec, weapon=weapon)
    name = f"{sid} · {e['weapon']['name']}"
    e['id'] = sid
    e['weapon'] = dict(e['weapon'], id=sid, name=name, fbx=M['fbx'])
    e['reference'] = ''                                               # keine Blender-Auswertung (tools/ego_build) für Varianten
    T = json.loads(json.dumps(M['textures']))
    skin = M.get('skin', 'standard')
    for s in T.get('skins', []):                                      # gebacken ist nur der Skin der Linie: er ist der Standard der Variante
        if s['name'] == skin:
            s.update(name='standard', de=f"Skin der Linie: {s.get('de', skin)}")
    e['textures'] = T
    e['mesh_bounds'] = dict(de='Netzgrenzen je Objekt (Formgen-Paket, Blender, m, Modifikatoren angewandt)',
                            objects=M['mesh_bounds']['objects'])
    pkg = os.path.join(folder, f'{sid}.package.json')
    e['sources'] = dict(files=[dict(path=f'unity/Assets/Ballon/Generated/{rel}/{f}', sha256=sha(os.path.join(folder, f)))
                               for f in (f'{sid}.package.json', M['fbx'])],
                        parts_sha256=M['ballon']['parts_sha256'])
    e['dir'] = rel
    e['origin'] = dict(kind='formgen', id=sid, package=f'{sid}.package.json', package_format=M['format_version'],
                       base_module=M['ballon']['module'], base_id=base_id, skin=skin, blender=M.get('blender', ''),
                       bake=f"{M['bake']['atlas']}², {M['bake']['samples']} Samples, {M['bake']['device']}" if M.get('bake') else '',
                       points=points, gameplay=f'geerbt von {base_id} (Klasse {e["profile"]["type"]})')
    return e


def entries(folder=None, EU=None):
    """Einträge aller Pakete; ein fehlerhaftes Paket bricht ab (keine halben Varianten in ego.json)."""
    return [entry(f, EU) for f in packages(folder)]


def main():
    ok = 0
    for f in packages():
        try:
            e = entry(f)
            print(f"{e['id']}: {e['weapon']['name']} – Grundtyp {e['origin']['base_id']}, Weltpunkte: {e['origin']['points']}")
            ok += 1
        except PackageError as err:
            print(f'Fehler: {err}')
            return 1
    print(f'Formgen: {ok} Paket(e) unter {os.path.relpath(DIR, ROOT)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
