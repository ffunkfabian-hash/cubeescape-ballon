"""Einlesen von Formgen-Paketen (0.41 „Intake“, tools/formgen_import.py) ohne Blender (./check).

1. Echte Pakete unter Generated/Formgen/<ID>/ (falls vorhanden): Eintrag entsteht, dir = Formgen/<ID>, keine Blender-Referenz, FBX und
   Texturen im Paket, Haltungen/Aktionen/Gameplay/Profil gleich dem BALLON-Grundtyp (vorerst geerbt), Atlas formgen_<ID>, Skin standard.
2. Erfundenes Paket 2 mit Datensatz (BASIC-01-v2.1, Teil `upper` samt Auswurf 25 mm nach vorn): Auswurf im Eintrag mitgewandert;
   falscher Bauteil-Hash und unvollständige POINTS (Punkt fehlt, Teil fehlt) werden abgelehnt.
3. Paket 1 ohne Datensatz, Teil eines Weltpunkts verändert (Netzgrenzen von `upper` in der Spec verschoben): abgelehnt, weil die
   Weltpunkte der Grundform dann nicht mehr stimmen. Unbekanntes Format, fehlende Texturen: abgelehnt.
"""
import copy
import importlib
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic.arms import ego as EG  # noqa: E402
from tools import export_unity as EU  # noqa: E402
from tools import formgen_import as FG  # noqa: E402

BASE = 'basic.pilot.w01_auto_rifle_v21'
INHERITED = ('profile', 'poses', 'actions')


def fake_package(tmp, sid, W, model=None, spec=None):
    """Paketordner wie Formgen ihn entpackt, mit leeren Bild-/FBX-Dateien (nur Pfade zählen)."""
    d = os.path.join(tmp, sid)
    os.makedirs(os.path.join(d, 'textures'))
    wid = EG.weapon_id(W)
    tex = {k: f'{sid}_{k}.' + ('jpg' if k == 'albedo' else 'png') for k in ('albedo', 'spec', 'normal', 'ao')}
    for f in tex.values():
        open(os.path.join(d, 'textures', f), 'wb').close()
    open(os.path.join(d, f'{sid}.fbx'), 'wb').close()
    V = FG.VA.as_module(model, W) if model else W
    spec = spec or json.load(open(os.path.join(ROOT, 'data', 'specs', f'{wid}.spec.json'), encoding='utf-8'))
    json.dump(spec, open(os.path.join(d, f'{sid}.spec.json'), 'w'))
    M = dict(format=FG.FORMAT, format_version=2 if model else 1, id=sid, skin='eloxal', blender='test', fbx=f'{sid}.fbx',
             ballon=dict(module=BASE, weapon_id=wid, parts_sha256=EU.parts_sha(V)),
             textures=dict(weapon=dict(size=4096, objects=[], **tex),
                           skins=[dict(name='eloxal', de='Eloxal', kind='Farbe', albedo=tex['albedo'], spec=tex['spec'])]),
             mesh_bounds=dict(objects=[], triangles=0), weapon=EU.weapon_data(V, EG.profile(V)['live']),
             bake=dict(atlas=4096, samples=64, device='gpu'))
    if model:
        M['model'] = model
    json.dump(M, open(os.path.join(d, f'{sid}.package.json'), 'w'))
    return d


def expect_error(bad, label, fn):
    try:
        fn()
    except FG.PackageError as e:
        return str(e)
    bad.append(f'{label}: nicht abgelehnt')
    return ''


def main():
    bad, notes = [], []
    W = importlib.import_module(BASE)
    base_entries = {EG.weapon_id(importlib.import_module(f'basic.{m}')): None for m in EU.WEAPONS}
    # 1. echte Pakete
    for folder in FG.packages():
        e = FG.entry(folder)
        sid = e['id']
        B = EU.weapon_entry(importlib.import_module(e['origin']['base_module']))
        base_entries[e['origin']['base_id']] = B
        if e['dir'] != f'Formgen/{sid}' or e['reference'] or e['atlas'] != f'formgen_{sid}':
            bad.append(f"{sid}: dir/reference/atlas {e['dir']!r} {e['reference']!r} {e['atlas']!r}")
        for k in INHERITED:
            if e[k] != B[k]:
                bad.append(f'{sid}: {k} nicht vom Grundtyp geerbt')
        if {k: v for k, v in e['gameplay'].items() if k != 'fx'} != {k: v for k, v in B['gameplay'].items() if k != 'fx'}:
            bad.append(f'{sid}: Gameplay nicht vom Grundtyp geerbt')
        if [g['name'] for g in e['grips']] != [g['name'] for g in B['grips']]:
            bad.append(f'{sid}: Griffe nicht vom Grundtyp')
        if e['textures']['skins'][0]['name'] != 'standard':
            bad.append(f'{sid}: erster Skin nicht standard')
        for f in FG.texture_files(e['textures']) + [e['weapon']['fbx']]:
            p = os.path.join(FG.DIR, sid, 'textures' if not f.endswith('.fbx') else '', f)
            if not os.path.isfile(p):
                bad.append(f'{sid}: {f} fehlt')
        notes.append(f"{sid} ({e['origin']['base_id']}, {e['origin']['points'].split(' (')[0]})")
    with tempfile.TemporaryDirectory() as tmp:
        # 2. Paket mit Datensatz: upper und Auswurf 25 mm nach vorn
        model = dict(ANCHORS=copy.deepcopy(W.ANCHORS), POINTS=copy.deepcopy(W.POINTS))
        model['POINTS']['eject']['at'] = (W.POINTS['eject']['at'][0] + 25,) + tuple(W.POINTS['eject']['at'][1:])
        e = FG.entry(fake_package(tmp, 'BX01', W, model=model))
        want = EU.xyz(*model['POINTS']['eject']['at'])
        if e['weapon']['eject']['pos'] != want:
            bad.append(f"Datensatz: Auswurf {e['weapon']['eject']['pos']} statt {want}")
        if 'mit POINTS' not in e['origin']['points']:
            bad.append(f"Datensatz: Herkunft der Weltpunkte {e['origin']['points']}")
        d = fake_package(tmp, 'BX02', W, model=model)
        M = json.load(open(os.path.join(d, 'BX02.package.json')))
        M['ballon']['parts_sha256'] = '0' * 64
        json.dump(M, open(os.path.join(d, 'BX02.package.json'), 'w'))
        expect_error(bad, 'falscher Bauteil-Hash', lambda: FG.entry(d))
        # Datensatz mit unvollständigen POINTS (ein Punkt fehlt, ein Teilbezug zeigt ins Leere): abgelehnt statt Grundform-Punkte
        for label, edit in (('POINTS ohne grip.mag', lambda P: P.pop('grip.mag')),
                            ('POINTS mit fehlendem Teil', lambda P: P['grip.support'].update(part='kein_teil'))):
            m2 = dict(ANCHORS=copy.deepcopy(W.ANCHORS), POINTS=copy.deepcopy(W.POINTS))
            edit(m2['POINTS'])
            sid = 'BX0' + ('7' if 'ohne' in label else '8')
            msg = expect_error(bad, label, lambda: FG.entry(fake_package(tmp, sid, W, model=m2)))
            if msg and 'Weltpunkte' not in msg:
                bad.append(f'{label}: Meldung nennt die Weltpunkte nicht ({msg})')
        # 3. Paket ohne Datensatz mit verändertem Teil eines Weltpunkts
        spec = json.load(open(os.path.join(ROOT, 'data', 'specs', 'BASIC-01-v2.1.spec.json'), encoding='utf-8'))
        for p in spec['parts']:
            if p['id'] == W.POINTS['eject']['part']:
                for k in ('min', 'max'):
                    p['bounds_m'][k][1] -= 0.025
        msg = expect_error(bad, 'Teil des Auswurfs verändert', lambda: FG.entry(fake_package(tmp, 'BX03', W, spec=spec)))
        if msg and 'eject' not in msg:
            bad.append(f'Teil des Auswurfs verändert: Meldung nennt den Punkt nicht ({msg})')
        ok = FG.entry(fake_package(tmp, 'BX04', W))                  # unverändert: angenommen
        if ok['weapon']['eject']['pos'] != EU.xyz(*W.EJECT['at']):
            bad.append('Paket 1 unverändert: Auswurf weicht ab')
        d = fake_package(tmp, 'BX05', W)
        os.remove(os.path.join(d, 'textures', 'BX05_ao.png'))
        expect_error(bad, 'fehlende Textur', lambda: FG.entry(d))
        d = fake_package(tmp, 'BX06', W)
        M = json.load(open(os.path.join(d, 'BX06.package.json')))
        M['format_version'] = 9
        json.dump(M, open(os.path.join(d, 'BX06.package.json'), 'w'))
        expect_error(bad, 'unbekanntes Format', lambda: FG.entry(d))
    for b in bad:
        print('FEHLER', b)
    print(f"Formgen-Einlesen geprüft: {len(notes)} Paket(e) {', '.join(notes) or '–'}; Datensatz, Hash, verändertes Teil, Format, Dateien"
          if not bad else f'{len(bad)} Fehler')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
