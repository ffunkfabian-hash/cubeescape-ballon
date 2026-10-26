"""Export für das Unity-Projekt (0.4 „Firstfeel“, je Waffe seit 0.18 „Quickdraw“): spielbare Waffen (WEAPONS) und Roboterarme als FBX,
Ego-Daten als JSON (`ballon-ego/8`).

  BALLON_BAKE_GPU=1 ce lock gpu -- blender -b --factory-startup -P <abs>/tools/export_unity.py   → unity/Assets/Ballon/Generated/
        <Waffe>.fbx je Waffe (Wurzel → ASM_* → Teile, Anker als Leerknoten), arms.fbx (R_/L_-Segmente → Teile),
        ego.json (Daten: Gemeinsames + weapons[]), ego_reference_<Waffe>.json (Blender-Auswertung von tools/ego_build.evaluate als
        Testreferenz). Gebacken wird nur, was sich geändert hat: eine Waffe, deren Form gleich blieb, behält Atlanten, Netzgrenzen und FBX
        (wie BALLON_EXPORT_DATA_ONLY=1 je Waffe); geänderte gemeinsame Formquellen backen alles neu.
  python3 tools/export_unity.py --check   → ego.json passt zu den Python-Daten (ohne Blender, Teil von ./check)

Alle Werte stehen im Blender-Kameraraum (Meter, rechts −X, vorn −Y, oben +Z), wie tools/ego_build.py rechnet; die Laufzeit in C#
rechnet dort und wandelt erst am Ende nach Unity. Die Umrechnung steht **einmal** hier (`AXES`) und wird von Unity gelesen und
getestet: Unity (x rechts, y oben, z vorn, linkshändig) = (−x, z, −y). Autorenmaß (f, u, x) mm → Blender (x, −f, u) m.
"""
import ast
import hashlib
import importlib
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic.arms import robot_arm as RA, ego as EG  # noqa: E402

FORMAT = 'ballon-ego/8'   # 8 (0.18): weapons[] je spielbarer Waffe (gameplay, weapon mit live, poses, grips, actions, profile, textures, mesh_bounds, sources, reference), gemeinsam motion/camera/arm/finger_poses/roles/textures(arms, lut)/mesh_bounds(arms); 7 (0.16): motion.flash (Mündungsfeuer), motion.eject und weapon.eject (Hülsen), Rollen flash_*; 6 (0.15): motion.recoil neu (Bahn, Kamera, Modellkick, Erholung, Salven, Streuung) und motion.switch; 5 (0.13): gameplay.weapon_type/world_zoom/zoom_table/hip (Weltzoom je Klasse, Hüft-Fadenkreuz); 4 (0.10): secondary.aim_freq_hz/aim_zeta (Zielen ohne Überschwingen); 3 (0.7.1/0.7.2): Spiegelkarte spec statt mask, textures.skins; 2 (0.7): Atlanten, AgX-LUT. Ältere neu erzeugen
# Spielbare Waffen in Unity, Reihenfolge = Taste 1, 2 (Entscheidungsliste Schritt 6: Ego-Übertrag je Klasse; BASIC-06 Nutzerwahl 26.10.2026)
WEAPONS = ['pilot.w01_auto_rifle_v21', 'pilot.w06_submachine_gun_v21']
WEAPON = WEAPONS[0]                 # Pilotwaffe (./check: Mündungsfeuer im Zielen, Bezug der Automatik)
SHARED_SRC = ['basic/common.py', 'basic/kit.py', 'basic/arms/robot_arm.py', 'basic/arms/ego.py', 'tools/ego_build.py',
              'tools/blender_build.py', 'tools/export_unity.py', 'tools/bake_unity.py']
ATLAS_KEY = {'BASIC-01-v2.1': 'weapon'}   # Dateinamen der Pilotwaffe seit 0.7 (weapon_albedo.png …); andere: weapon_<Waffe>
DST = os.path.join(ROOT, 'unity', 'Assets', 'Ballon', 'Generated')
MM = 0.001
AXES = dict(to_unity=[[-1, 0, 0], [0, 0, 1], [0, -1, 0]],
            de='Unity = M · Blender; Blender-Kameraraum rechts −X, vorn −Y, oben +Z → Unity rechts +X, oben +Y, vorn +Z')
AXIS = {'x': (0, -1.0), 'f': (1, -1.0), 'u': (2, 1.0)}   # wie tools/blender_build.AXIS (Index, Drehsinn)


def prim(q):
    """Grundelement aus basic/reticles.py für JsonUtility (feste Felder, Paare als Listen)."""
    d = dict(t=q['t'])
    if q['t'] == 'line':
        d.update(a=r6(q['a']), b=r6(q['b']), d=r6(q['d']))
    elif q['t'] == 'ring':
        d.update(r=r6(q['r']), ri=r6(q['ri']), grow=r6(q['grow']))
    else:
        d.update(r=r6(q['r']))
    return d


def gameplay(weapon_type):
    """Spielwerte der Klasse: Kadenz und Magazin (ego.CLASSES › gameplay), Weltzoom der Klasse (Entscheidungsliste 1.2 A) und das
    Hüft-Fadenkreuz (4.1 A / 4.2 A) aus dem Absehen-Katalog basic/reticles.py, aufgelöst für den Waffentyp."""
    from basic import reticles as RT
    GAMEPLAY = EG.CLASSES[weapon_type]['gameplay']
    H = RT.hip(weapon_type)
    S = RT.SPREAD[H['spread']]
    sp = H['sprint']
    sprint = dict(kind=sp['kind'], share_h=sp['share_h'], extent_mm=sp['extent_mm'], prims=[prim(q) for q in RT.RETICLES[sp['kind']]['prims']]) \
        if sp else dict(kind='', share_h=0.0, extent_mm=0.0, prims=[])
    hip = dict(kind=H['kind'], share_h=H['share_h'], extent_mm=H['extent_mm'], status=H['status'],
               color=RT.COLORS[RT.HIP['color']][1], weight=RT.WEIGHTS[RT.HIP['weight']][1], line_r_mm=RT.LINE_R,
               opacity=RT.SETTINGS['opacity']['default'], min_line_px=RT.HIP['min_line_px'],
               prims=[prim(q) for q in RT.RETICLES[H['kind']]['prims']],
               spread=dict(id=H['spread'], **{k: S[k] for k in ('base', 'per_shot', 'max', 'recover_s', 'move')}), sprint=sprint,
               src='basic/reticles.py › HIP, DEFAULTS, SPREAD (Entscheidungsliste 4.1 A, 4.2 A; Glidepath)')
    return dict(GAMEPLAY, weapon_type=weapon_type, sight=RT.sight_type(weapon_type), world_zoom=RT.class_world_zoom(weapon_type),
                zoom_table=[dict(type=k, zoom=RT.class_world_zoom(k)) for k in RT.CLASS_ZOOM], hip=hip)


def r6(v):
    if isinstance(v, (list, tuple)):
        return [r6(x) for x in v]
    return round(float(v), 6) + 0.0


def xyz(f, u, x=0.0):
    """Autorenmaß (mm) → Blender-Meter (wie kit.to_xyz)."""
    return r6((x * MM, -f * MM, u * MM))


def vdir(fux):
    """Richtung im Autorenmaß → Blender-Vektor (wie ego_build.vdir)."""
    return r6((fux[2], -fux[0], fux[1]))


def weapon_key(f, k):
    name, off = (k, {}) if isinstance(k, str) else k
    return dict(f=r6(f), pose=name, **{a: r6(off.get(a, 0.0)) for a in ('roll', 'yaw', 'pitch', 'up', 'right', 'back')})


def hand_key(f, k):
    f = r6(f)
    if isinstance(k, str):
        return dict(f=f, kind='grip', grip=k, point=[0.0, 0.0, 0.0], offset=[0.0, 0.0, 0.0])
    if k[0] == 'cam':
        return dict(f=f, kind='cam', grip='support', point=r6(k[1]), offset=[0.0, 0.0, 0.0])
    return dict(f=f, kind='grip', grip=k[0], point=[0.0, 0.0, 0.0], offset=r6([c * MM for c in vdir(k[1])]))


def action(name, A):
    B = A.get('bob')
    return dict(
        name=name, de=A['de'], frames=A['frames'], time_scale=r6(A.get('time_scale', 1.0)), src=A['src'],
        weapon=[weapon_key(f, k) for f, k in A['weapon']],
        L=[hand_key(f, k) for f, k in A.get('L', [(0, 'support')])],
        R=[hand_key(f, k) for f, k in A.get('R', [(0, 'grip')])],
        fL=[dict(f=r6(f), pose=p) for f, p in A.get('fL', [(0, 'underhand')])],
        fR=[dict(f=r6(f), pose=p) for f, p in A.get('fR', [(0, 'trigger')])],
        mech=[dict(part=pid, keys=[dict(f=r6(f), v=r6(v)) for f, v in keys]) for pid, keys in A.get('mech', {}).items()],
        carry=[dict(a=r6(a), b=r6(b)) for a, b in A.get('carry', [])],
        drop=dict(a=r6(A['drop'][0]), b=r6(A['drop'][1])) if A.get('drop') else dict(a=-1.0, b=-1.0),
        fire=list(A.get('fire', [])), kick=r6(A.get('kick', 1.0)), breathe=bool(A.get('breathe')),
        bob=dict(enabled=True, start=r6(B['start']), end=r6(B['end']), period=r6(B['period']), amp=r6(B['amp']), roll=r6(B['roll']),
                 u=B.get('shape') == 'u')
        if B else dict(enabled=False, start=0.0, end=0.0, period=1.0, amp=[0.0, 0.0], roll=0.0),
        events=[dict(f=f, name=n) for f, n in A.get('events', [])])


def kit_materials():
    """Materialrollen aus basic/kit.py (MATERIALS ist ein Literal; kit selbst braucht bpy)."""
    tree = ast.parse(open(os.path.join(ROOT, 'basic', 'kit.py'), encoding='utf-8').read())
    node = next(n for n in tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'MATERIALS')
    return eval(compile(ast.Expression(node.value), 'kit.py', 'eval'), {'__builtins__': {}, 'dict': dict})


def weapon_data(W, live):
    parts = []
    for p in W.PARTS:
        mv = p.get('move')
        rest = xyz(*mv['pivot']) if mv and mv.get('pivot') is not None else [0.0, 0.0, 0.0]
        m = dict(kind='none', vec=[0.0, 0.0, 0.0], axis=[0.0, 0.0, 0.0], a0=0.0, a1=0.0)
        if mv and mv['kind'] == 'translate':
            m.update(kind='translate', vec=xyz(*mv['vector_mm']))
        elif mv and mv['kind'] == 'rotate':
            i, s = AXIS[mv['axis']]
            ax = [0.0, 0.0, 0.0]
            ax[i] = s
            m.update(kind='rotate', axis=ax, a0=r6(mv['range_deg'][0]), a1=r6(mv['range_deg'][1]))
        elif mv:
            m['kind'] = mv['kind']          # glow/segment: in der Pilotwaffe nicht vorhanden, Laufzeit meldet unbekannte Arten
        parts.append(dict(id=p['id'], asm=p['asm'], role=p['mat'], parent=p.get('parent_part') or '', rest=rest, move=m))
    anchors = [dict(id=k, part=v.get('part', ''), pos=xyz(*v['at'])) for k, v in W.ANCHORS.items()]
    wid = EG.weapon_id(W)
    ids = {p['id'] for p in parts}
    missing = [v for v in live.values() if v not in ids]
    if missing:
        raise KeyError(f'{wid}: Live-Teile {missing} fehlen (ego.LIVE bzw. Modul-Feld EGO_LIVE)')
    return dict(id=wid, root=W.META['id'], name=W.META['name'], fbx=f'{wid}.fbx', parts=parts, anchors=anchors,
                eject=eject_data(W), live=dict(live))


def mesh(V, tris):
    """Netz im Autorenmaß (f, u, x mm) → flache Punktliste im Blender-Rahmen (m) und flache Dreiecksliste."""
    return [c for v in V for c in xyz(*v)], [i for t in tris for i in t]


def eject_data(W):
    """Hülsenauswurf der Waffe (Modul-Feld EJECT, 5.4 A): Startlage im Auswurffenster, Richtung (Einheit) und Hülsennetz; enabled false ohne Feld."""
    E = getattr(W, 'EJECT', None)
    if not E:
        return dict(enabled=False, pos=[0.0, 0.0, 0.0], dir=[0.0, 0.0, 0.0], case='', verts=[], tris=[], src='kein Auswurf')
    d = vdir(E['dir'])
    n = sum(a * a for a in d) ** 0.5
    vs, ts = mesh(*EG.case_mesh(E['case']))
    return dict(enabled=True, pos=xyz(*E['at']), dir=r6([a / n for a in d]), case=E['case'],
                verts=vs, tris=ts, src=E['src'])


def flash_data():
    """Mündungsfeuer (ego.FLASH, 5.3 A): Netz relativ zu Socket_Muzzle (Blender-Waffenrahmen, m), Kern- und Flammendreiecke, Dauer,
    Drehfolge um die Laufachse, Rollen."""
    F = EG.FLASH
    V, core, flame = EG.flash_mesh()
    vs, ct = mesh(V, core)
    _, ft = mesh(V, flame)
    return dict(dur_s=r6(F['dur_s']), verts=vs, core_tris=ct, flame_tris=ft, roll_deg=r6(F['roll_deg']), core_role=F['core']['role'],
                flame_role=F['tongues']['role'], src=F['src'])


def weapon_files(W):
    """Formquellen einer Waffe: ihr Modul und das Grundmodul, aus dem es META und Baugruppen übernimmt (V1)."""
    fs = [os.path.relpath(W.__file__, ROOT)]
    if getattr(W, 'V1', None) is not None:
        fs.append(os.path.relpath(W.V1.__file__, ROOT))
    return fs


def sha_files(paths):
    return [dict(path=p, sha256=hashlib.sha256(open(os.path.join(ROOT, p), 'rb').read()).hexdigest()) for p in paths]


def weapon_entry(W):
    """Ein Eintrag von weapons[] (ohne textures/mesh_bounds, die schreibt der Blender-Teil): Ego-Profil der Klasse (ego.profile)."""
    P = EG.profile(W)
    weapon = weapon_data(W, P['live'])
    wid = weapon['id']
    poses = []
    for k, Q in P['poses'].items():
        poses.append(dict(name=k, ads='eye' in Q, roll=r6(Q.get('roll', 0)), src=Q['src'],
                          pos=r6(Q.get('pos', (0, 0, 0))), aim=r6(Q.get('aim', (0, 0, 0))),
                          eye=r6(Q.get('eye', (0, 0, 0))), aim_dir=r6(Q.get('aim_dir', (0, 0, 0)))))
    grips = [dict(name=k, part=G.get('part', ''), contact=xyz(*G['contact']), palm=vdir(G['palm']), fingers=vdir(G['fingers']),
                  fingers_pose=G['fingers_pose'], src=G['src']) for k, G in P['grips'].items()]
    C = EG.CLASSES[P['type']]
    profile = dict(type=P['type'], src=P['src'], poses=sorted(C['poses']), frames=[dict(action=k, frames=r6(v)) for k, v in C['frames'].items()],
                   frames_src=P['frames_src'])
    return dict(id=wid, profile=profile, gameplay=gameplay(P['type']), weapon=weapon, poses=poses, grips=grips,
                actions=[action(k, A) for k, A in P['actions'].items()], atlas=ATLAS_KEY.get(wid, f'weapon_{wid}'),
                reference=f'ego_reference_{wid}.json',
                sources=dict(files=sha_files(weapon_files(W)), parts_sha256=parts_sha(W)))


def data():
    Ws = [importlib.import_module(f'basic.{m}') for m in WEAPONS]
    entries = [weapon_entry(W) for W in Ws]
    roles = kit_materials()
    fingers = [dict(name=k, f=[float(a) for row in v['f'] for a in row], t=[float(a) for a in v['t']])
               for k, v in EG.FINGER_POSES.items()]
    arm = dict(rig_version=RA.RIG_VERSION, upper_m=r6(RA.UPPER_MM * MM), fore_m=r6(RA.FORE_MM * MM),
               shoulder_R=r6(RA.SHOULDER['R']), shoulder_L=r6(RA.SHOULDER['L']), elbow_pole=r6(RA.ELBOW_POLE),
               wrist_limit_deg=RA.WRIST_LIMIT_DEG, wrist_target_deg=RA.WRIST_TARGET_DEG, forearm_pref=r6(RA.FOREARM_PREF),
               palm_center=r6((0, -RA.PALM_T / 2 * MM, (RA.PALM_START + RA.PALM_LEN / 2) * MM)),
               knuckle_z=r6(RA.KNUCKLE_Z * MM), finger_x=r6([x * MM for x in RA.FINGER_X]),
               finger_scale=r6(getattr(RA, 'FINGER_SCALE', [1.0] * len(RA.FINGER_X))),
               finger_links=r6([x * MM for x in RA.FINGER_LINKS]), thumb_base=r6([x * MM for x in RA.THUMB_BASE]),
               thumb_dir=r6(RA.THUMB_DIR), thumb_links=r6([x * MM for x in RA.THUMB_LINKS]),
               segments=list(RA.SEGMENTS), fbx='arms.fbx',
               pieces=[dict(id=pid, segment=seg, role=role) for pid, de, seg, kind, role, p in RA.parts()], src=RA.SOURCE)
    sources = dict(de='SHA-256 der gemeinsamen Generatorquellen beim Export (je Waffe: weapons[].sources); --check meldet auch reine '
                      'Formänderungen', files=sha_files(SHARED_SRC))
    used = sorted({p['role'] for e in entries for p in e['weapon']['parts']} | {p['role'] for p in arm['pieces']} | {EG.EJECT['role']})
    for k, F in EG.FLASH['roles'].items():          # Leuchtrollen des Mündungsfeuers stehen in ego.FLASH (reine Emission wie Absehen)
        roles[k] = dict(color=F['color'], rough=0.3, metal=0.0, emit=F['emit'], emit_only=True, spec=0.0, de=F['de'])
    motion = dict(interp=EG.INTERP, time_scale=EG.TIME_SCALE, keep_time=sorted(EG.KEEP_TIME),
                  secondary=dict(freq_hz=EG.SECONDARY['freq_hz'], zeta=EG.SECONDARY['zeta'],
                                 aim_freq_hz=EG.SECONDARY['aim_freq_hz'], aim_zeta=EG.SECONDARY['aim_zeta']),
                  breathe_all={k: r6(v) for k, v in EG.BREATHE_ALL.items()},
                  recoil={k: v if isinstance(v, int) else r6(v) for k, v in EG.RECOIL.items()},
                  switch=dict(empty_s=r6(EG.SWITCH['empty_s']), src=EG.SWITCH['src']),
                  flash=flash_data(),
                  eject=dict(speed_mps=r6(EG.EJECT['speed_mps']), gravity_mps2=r6(EG.EJECT['gravity_mps2']), spin_dps=r6(EG.EJECT['spin_dps']),
                             spin_axis=r6(vdir(EG.EJECT['spin_axis'])), life_s=r6(EG.EJECT['life_s']), max_live=EG.EJECT['max_live'],
                             delay_frames=EG.EJECT['delay_frames'], role=EG.EJECT['role'], src=EG.EJECT['src']),
                  de='Bewegungsgefühl v2 aus basic/arms/ego.py (Kurven, Feder-Nachlauf, Atmen, Rückstoß, Wechsel, Tempo)')
    return dict(format=FORMAT, generated_by='tools/export_unity.py', sources=sources, axes=AXES, fps=EG.FPS, motion=motion,
                camera=dict(h_fov_deg=EG.CAMERA['h_fov_deg'], aspect=list(EG.CAMERA['aspect']), near_m=EG.CAMERA['near_m']),
                arm=arm, finger_poses=fingers,
                roles=[dict(role=r, color=roles[r]['color'], aaa_color=roles[r].get('aaa_color', roles[r]['color']),
                            rough=roles[r]['rough'], metal=roles[r]['metal'], alpha=roles[r].get('alpha', 1.0),
                            emit=roles[r].get('emit', 0.0), emit_only=bool(roles[r].get('emit_only')), spec=roles[r].get('spec', 0.5),
                            de=roles[r]['de']) for r in used + sorted(EG.FLASH['roles'])],
                weapons=entries)


def write_json(path, obj):
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write('\n')


MOTION_SOURCES = {'basic/arms/ego.py', 'tools/ego_build.py', 'tools/export_unity.py'}   # dürfen sich im Datenexport ändern
BAKED = ('textures', 'mesh_bounds')                  # schreibt nur der Blender-Teil (Atlanten, Netzgrenzen)


def load_old():
    """Letztes ego.json als (Format, gemeinsame Quellen {Pfad: sha}, Atlanten Arme+LUT, Netzgrenzen Arme, {Waffe: alter Eintrag}) oder None.
    /7 (bis 0.17, eine Waffe) wird in die Teile von /8 zerlegt: Waffenquellen und -netze gehören zum Eintrag, der Rest ist gemeinsam."""
    p = os.path.join(DST, 'ego.json')
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8') as fh:
        old = json.load(fh)
    if 'textures' not in old or 'mesh_bounds' not in old:
        return None
    if old.get('format') == 'ballon-ego/7':
        files = old.get('sources', {}).get('files', [])
        wfiles = [f for f in files if f['path'].startswith(('basic/pilot/', 'basic/weapons/'))]
        ids = {q['id'] for q in old['weapon']['parts']}
        T = old['textures']
        e = dict(id=old['weapon']['id'], sources=dict(files=wfiles, parts_sha256=old['sources'].get('parts_sha256')),
                 textures=dict(weapon=T['weapon'], skins=T.get('skins', [])),
                 mesh_bounds=dict(de=old['mesh_bounds']['de'], objects=[b for b in old['mesh_bounds']['objects'] if b['name'] in ids]))
        shared = {f['path']: f['sha256'] for f in files if f not in wfiles}
        return ('ballon-ego/7', shared, dict(de=T['de'], arms=T['arms'], lut=T['lut']),
                dict(de=old['mesh_bounds']['de'], objects=[b for b in old['mesh_bounds']['objects'] if b['name'] not in ids]), {e['id']: e})
    return (old['format'], {f['path']: f['sha256'] for f in old['sources']['files']}, old['textures'], old['mesh_bounds'],
            {e['id']: e for e in old.get('weapons', []) if all(k in e for k in BAKED)})


def export_plan(D, old):
    """Was der Export backen muss: (Arme neu?, {Waffe: 'reuse' | 'bounds' | 'full'}, {Waffe oder 'arms': Grund}). 'reuse': Form gleich,
    Atlanten, Netzgrenzen und FBX bleiben; 'bounds': nur das Waffenmodul geändert, Bauteil-Entwurf gleich (z. B. nur EJECT/EGO_*) – gilt,
    wenn die Netzgrenzen in Blender gleich bleiben (Richter 0.16: Grenzen allein beweisen keine gleiche Geometrie, darum zusätzlich der
    Bauteil-Entwurf); 'full': backen. Geänderte gemeinsame Formquellen backen alles (Richter 0.10: sonst meldet --check „aktuell“, während
    FBX und Atlanten veraltet sind)."""
    ids = [e['id'] for e in D['weapons']]
    if old is None:
        return True, {i: 'full' for i in ids}, {'arms': 'kein ego.json mit Atlanten'}
    fmt, shared, _, _, ents = old
    changed = [f['path'] for f in D['sources']['files'] if f['path'] not in MOTION_SOURCES and shared.get(f['path']) != f['sha256']]
    if changed:
        why = 'Form- oder Materialquellen geändert: ' + ', '.join(changed)
        return True, {i: 'full' for i in ids}, dict({i: why for i in ids}, arms=why)
    plan, why = {}, {}
    for e in D['weapons']:
        o = ents.get(e['id'])
        if o is None:
            plan[e['id']], why[e['id']] = 'full', 'neu (kein Eintrag mit Atlanten im letzten Export)'
            continue
        was = {f['path']: f['sha256'] for f in o['sources']['files']}
        diff = [f['path'] for f in e['sources']['files'] if was.get(f['path']) != f['sha256']]
        if not diff:
            plan[e['id']] = 'reuse'
            continue
        want = o['sources'].get('parts_sha256') or next((parts_sha_at(f, was.get(f)) for f in diff[:1]), None)
        if diff == [e['sources']['files'][0]['path']] and want == e['sources']['parts_sha256']:
            plan[e['id']], why[e['id']] = 'bounds', f'{diff[0]} geändert, Bauteil-Entwurf gleich'
        else:
            plan[e['id']], why[e['id']] = 'full', f'{", ".join(diff)}: Bauteile geändert (Form, Material oder Bewegung)'
    return False, plan, why



def parts_sha(W):
    """SHA-256 des Bauteil-Entwurfs der Waffe (PARTS und ASSEMBLIES: Form, Materialrolle, Bewegung) ohne Anker und Datenfelder wie EJECT."""
    return hashlib.sha256(json.dumps(dict(parts=W.PARTS, assemblies=W.ASSEMBLIES), sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def parts_sha_at(path, sha):
    """parts_sha der Fassung von path, deren Datei-SHA-256 sha ist (aus der Git-Geschichte; für ego.json ohne parts_sha256), sonst None."""
    import subprocess
    import importlib.util
    import tempfile
    revs = subprocess.run(['git', '-C', ROOT, 'log', '--format=%H', '--', path], capture_output=True, text=True).stdout.split()
    for rev in revs:
        body = subprocess.run(['git', '-C', ROOT, 'show', f'{rev}:{path}'], capture_output=True).stdout
        if hashlib.sha256(body).hexdigest() != sha:
            continue
        with tempfile.NamedTemporaryFile('wb', suffix='.py', delete=False) as fh:
            fh.write(body)
        spec = importlib.util.spec_from_file_location('_weapon_at_export', fh.name)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        os.unlink(fh.name)
        return parts_sha(mod)
    return None


def mesh_bounds():
    """Netzgrenzen aller Netzobjekte der Szene im eigenen Objektraum (Modifikatoren angewandt), wie im vollen Export."""
    import bpy
    bounds = {}
    dg = bpy.context.evaluated_depsgraph_get()
    for ob in bpy.context.scene.objects:
        if ob.type != 'MESH':
            continue
        e = ob.evaluated_get(dg)
        me = e.to_mesh()
        vs = [v.co for v in me.vertices]
        if vs:
            bounds[ob.name] = dict(name=ob.name, min=r6([min(v[i] for v in vs) for i in range(3)]),
                                   max=r6([max(v[i] for v in vs) for i in range(3)]),
                                   tris=sum(len(p.vertices) - 2 for p in me.polygons))
        e.to_mesh_clear()
    return bounds


def write_reference(path, ref):
    with open(path, 'w', encoding='utf-8') as fh:   # groß: kompakt, eine Probe je Zeile
        fh.write('{' + ', '.join(f'"{k}": {json.dumps(v, ensure_ascii=False)}' for k, v in ref.items() if k != 'samples')
                 + ', "samples": [\n' + ',\n'.join(json.dumps(s, separators=(',', ':')) for s in ref['samples']) + '\n]}\n')


def feedback_mismatch():
    """Rückmeldung im Zielen steht als C#-Konstanten in EgoPlayer.AdsFeedback (kein Feld in ego.json, sonst neues Format):
    Werte müssen reticles.ADS_FEEDBACK und der Akzentfarbe aus kit.MATERIALS folgen. Gibt die abweichenden Namen zurück."""
    from basic import reticles
    cs = open(os.path.join(ROOT, 'unity', 'Assets', 'Ballon', 'Runtime', 'EgoPlayer.cs'), encoding='utf-8').read()
    F = reticles.ADS_FEEDBACK
    want = dict(ShotRingShareH=F['shot_ring']['share_h'], ShotRingFrames=F['shot_ring']['frames'], HitXShareH=F['hit_x']['share_h'],
                HitXMinS=F['hit_x']['min_s'])
    bad = [k for k, v in want.items() if not re.search(rf'\b{k} = {v:g}f?[,;]', cs)]
    rgb = kit_materials()['accent']['color'].lstrip('#')
    if f'new Color32(0x{rgb[0:2]}, 0x{rgb[2:4]}, 0x{rgb[4:6]}'.lower() not in cs.lower():
        bad.append('Orange')
    return bad


def check():
    bad = feedback_mismatch()
    if bad:
        print('EgoPlayer.AdsFeedback weicht von reticles.ADS_FEEDBACK / kit accent ab: ' + ', '.join(bad))
        return 1
    p = os.path.join(DST, 'ego.json')
    if not os.path.exists(p):
        print('unity/Assets/Ballon/Generated/ego.json fehlt (Blender-Export ausführen)')
        return 1
    cur = json.load(open(p, encoding='utf-8'))
    new = json.loads(json.dumps(data(), ensure_ascii=False))
    diff = [k for k in new if k != 'weapons' and cur.get(k) != new[k]]
    cw = {e.get('id'): e for e in cur.get('weapons', [])}
    if [e.get('id') for e in cur.get('weapons', [])] != [e['id'] for e in new['weapons']]:
        diff.append('weapons (Liste)')
    for e in new['weapons']:
        c = cw.get(e['id'], {})
        diff += [f"{e['id']}.{k}" for k in list(e) + list(BAKED) if k not in c or (k in e and c[k] != e[k])]
        if not os.path.exists(os.path.join(DST, e['reference'])):
            diff.append(e['reference'])
    if any(k not in cur for k in BAKED):
        diff.append('textures/mesh_bounds (Arme)')
    if diff:
        print('ego.json veraltet (' + ', '.join(diff[:8]) + '): Export neu ausführen')
        return 1
    print(f"unity: ego.json aktuell ({len(new['weapons'])} Waffen: " +
          ', '.join(f"{e['id']} {len(e['actions'])} Aktionen/{len(e['weapon']['parts'])} Teile" for e in new['weapons']) +
          f"; {len(new['arm']['pieces'])} Armteile)")
    return 0


# ------------------------------------------------------------------ Blender-Teil
REF_OBJECTS = ['magazine', 'charging_handle', 'mag_release']    # dazu die Live-Teile der Waffe (Abzug, Verschluss, Auswurfklappe)
REF_SEGMENTS = ['upper', 'fore', 'hand', 'f0_0', 'f0_2', 'f3_1', 't_0', 't_2']


def reference(sc, e):
    """Blender-Auswertung (tools/ego_build.evaluate) einer Waffe als Testreferenz: Standbilder und Stichproben aller Aktionen."""
    from tools import ego_build as EB
    objs_ref = [k for k in REF_OBJECTS + list(e['weapon']['live'].values()) if k in sc.objs]

    def flat(M):
        return r6([M[i][j] for i in range(4) for j in range(4)])

    def snap(label, action, frame):
        objs = {'weapon': flat(sc.root.matrix_world), 'camera': flat(sc.cam_base.inverted() @ sc.cam.matrix_world)}
        for pid in objs_ref:
            objs[pid] = flat(sc.objs[pid].matrix_world)
        for s in ('R', 'L'):
            for g in REF_SEGMENTS:
                objs[f'{s}_{g}'] = flat(sc.arms[s][0][g].matrix_world)
        if sc.fx_now['flash'] is not None:                 # Mündungsfeuer und Hülsen (0.16): nur sichtbare, Name = Schuss in der Aktion
            objs['flash'] = flat(sc.fx_now['flash'])
        for k, M in sorted(sc.fx_now['shells'].items()):
            objs[f'shell_{k}'] = flat(M)
        return dict(label=label, action=action, frame=frame, objects=[dict(name=k, m=v) for k, v in objs.items()])

    samples = []
    for name in ('hip', 'ads', 'reload', 'inspect_r'):          # Standbilder wie ego_build.main (Handbelegung je Haltung)
        A = dict(weapon=[(0, name)], L=[(0, EG.OFF_L if name == 'inspect_r' else 'support')], R=[(0, 'grip')])
        if name == 'reload':
            A.update(L=[(0, 'mag')], fL=[(0, 'mag_hold')])
        EB.evaluate(sc, A, 0, {}, {})
        samples.append(snap(f'still:{name}', '', 0))
    wrist = {}
    for name, A in sc.P['actions'].items():
        st, rep = {}, {}
        n = A['frames']
        frames = sorted({*range(0, n + 1, max(1, n // 8)), n, *[f for f, _ in A.get('events', [])]})
        if A.get('fire'):                                  # Feueraktionen lückenlos: jedes Blitz- und Hülsenbild prüfen
            frames = list(range(0, n + 1))
        for f in range(0, n + 1):                          # lückenlos auswerten (Zustand Magazin), nur Stichproben speichern
            EB.evaluate(sc, A, f, rep, st)
            if f in frames:
                samples.append(snap(f'{name}:{f}', name, f))
        wrist[name] = rep.get('wrist_max_deg', 0)
        print(f'[export_unity] {e["id"]} {name}: {len(frames)} Stichproben, Handgelenk max {wrist[name]:.1f}°', flush=True)
    return dict(format=FORMAT + '-reference', weapon=e['id'], de='Weltmatrizen (Blender-Kameraraum, zeilenweise) aus tools/ego_build.evaluate',
                tolerance_m=0.0005, tolerance_deg=0.1,
                # Ober- und Unterarm sind Richtungen zwischen zwei gelösten Punkten (je ≤ tolerance_m): daraus folgt ihre Drehgrenze (0.18)
                tolerance_arm_deg=round(math.degrees(math.atan2(2 * 0.0005, RA.UPPER_MM * MM)), 3), samples=samples)


def rest_pose(sc):
    """Ruhelage für den Export: Waffe im Ursprung, Teile in Ruhe, Armsegmente im Ursprung."""
    import bpy
    from mathutils import Matrix
    sc.set_weapon(Matrix.Identity(3), Matrix.Identity(4).translation, {}, {})
    for s in ('R', 'L'):
        for e in sc.arms[s][0].values():
            e.matrix_world = Matrix.Identity(4)
    bpy.context.view_layer.update()


def export_fbx(path, obs):
    import bpy
    bpy.ops.object.select_all(action='DESELECT')
    for o in obs:
        o.select_set(True)
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'EMPTY', 'MESH'}, use_mesh_modifiers=True,
                             mesh_smooth_type='OFF', use_custom_props=False, add_leaf_bones=False, bake_anim=False,
                             apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL', bake_space_transform=True,
                             axis_forward='-Z', axis_up='Y', path_mode='STRIP', embed_textures=False)


def bake_weapon(sc, e, tex_dir, gpu):
    """Atlas der Waffe (kit.aaa_nodes) und Skins (kit.SKINS: Farbe und Glanz je Skin neu, Normale und AO wie Standard), FBX."""
    from tools import bake_unity as BK
    from basic import kit
    wobs = [sc.root] + list(sc.root.children_recursive)
    meshes = [o for o in wobs if o.type == 'MESH']
    BK.apply_modifiers(meshes)
    bake = [o for o in meshes if BK.bakeable(o)]
    BK.unwrap(bake)
    key = e['atlas']
    files = BK.bake_atlas(bake, key, 4096, tex_dir, gpu=gpu)
    atlas = dict(size=4096, objects=sorted(o.name for o in bake), **files)
    print(f'[export_unity] {e["id"]}: Atlas {key}, {len(bake)} Objekte, 4096²', flush=True)
    skins = [dict(name='standard', de=kit.SKINS['standard']['de'], kind=kit.SKINS['standard']['kind'],
                  albedo=atlas['albedo'], spec=atlas['spec'])]
    for skin, S in kit.SKINS.items():
        if skin == 'standard':
            continue
        kit.SKIN['name'] = skin
        kit.set_mode(sc.objs, 'aaa')
        f = BK.bake_atlas(bake, f'{key}_{skin}', 4096, tex_dir, gpu=gpu, color_only=True)
        skins.append(dict(name=skin, de=S['de'], kind=S['kind'], **f))
        print(f'[export_unity] {e["id"]}: Skin {skin}', flush=True)
    kit.SKIN['name'] = 'standard'
    kit.set_mode(sc.objs, 'aaa')
    rest_pose(sc)
    export_fbx(os.path.join(DST, e['weapon']['fbx']), wobs)
    return dict(weapon=atlas, skins=skins)


def bake_arms(sc, tex_dir, gpu):
    """Atlas der Arme (Segmente zum Backen auseinandergelegt, sonst sehen Abrieb und AO Finger, Handfläche und Handrücken ineinander),
    arms.fbx. Gibt die Atlasdaten zurück."""
    import bpy
    from mathutils import Matrix
    from tools import bake_unity as BK
    aobs = [o for s in ('R', 'L') for e in sc.arms[s][0].values() for o in [e] + list(e.children)]
    meshes = [o for o in aobs if o.type == 'MESH']
    BK.apply_modifiers(meshes)
    bake = [o for o in meshes if BK.bakeable(o)]
    BK.unwrap(bake)
    for si, s in enumerate(('R', 'L')):
        for i, e in enumerate(sc.arms[s][0].values()):
            e.matrix_world = Matrix.Translation((i * 0.5, si * 1.0, 0.0))
    bpy.context.view_layer.update()
    files = BK.bake_atlas(bake, 'arms', 2048, tex_dir, gpu=gpu, join_all=True)
    rest_pose(sc)
    export_fbx(os.path.join(DST, 'arms.fbx'), aobs)
    print(f'[export_unity] Atlas arms: {len(bake)} Objekte, 2048²', flush=True)
    return dict(size=2048, objects=sorted(o.name for o in bake), **files)


def blender_main():
    gpu = '--gpu' in sys.argv or os.environ.get('BALLON_BAKE_GPU') == '1'   # GPU-Backen (nur unter ce lock gpu; ce lock reicht '-- --gpu' nicht durch)
    sys.argv = [sys.argv[0]]                   # ego_build.args() liest nichts mehr
    from tools import ego_build as EB
    from tools import bake_unity as BK
    os.makedirs(DST, exist_ok=True)
    D = data()
    old = load_old()
    arms_new, plan, why = export_plan(D, old)
    data_only = os.environ.get('BALLON_EXPORT_DATA_ONLY') == '1'
    print('[export_unity] Plan: ' + ', '.join(f'{k} {v}' + (f' ({why[k]})' if k in why else '') for k, v in plan.items()) +
          f"; Arme {'backen' + (' (' + why.get('arms', '') + ')') if arms_new else 'bleiben'}", flush=True)
    if data_only and (arms_new or 'full' in plan.values()):    # vor jeder Arbeit: darf der Datenexport Atlanten, Netze und FBX übernehmen?
        print('[export_unity] nur Daten nicht möglich: ' + '; '.join(f'{k}: {v}' for k, v in why.items()) +
              ' – voller Export nötig (ohne BALLON_EXPORT_DATA_ONLY)', flush=True)
        sys.exit(2)
    tex_dir = os.path.join(DST, 'Textures')
    os.makedirs(tex_dir, exist_ok=True)
    shared_tex = dict(old[2]) if old else {}
    arm_bounds = old[3] if old else None
    for i, (m, e) in enumerate(zip(WEAPONS, D['weapons'])):
        W = importlib.import_module(f'basic.{m}')
        sc = EB.Scene(W, dict(stills=False, actions=[], gpu=False, samples=1, weapon=m, fx=False))
        ref = reference(sc, e)
        rest_pose(sc)
        write_reference(os.path.join(DST, e['reference']), ref)
        ids = {p['id'] for p in e['weapon']['parts']}
        how = plan[e['id']]
        if how == 'bounds':                    # 0.16: Waffenmodul geändert – nur zulässig, wenn alle Netze gleich geblieben sind
            now = {k: b for k, b in mesh_bounds().items() if k in ids}
            was = {b['name']: b for b in old[4][e['id']]['mesh_bounds']['objects']}
            diff = sorted(k for k in set(now) | set(was) if now.get(k) != was.get(k))
            if diff and data_only:
                print(f'[export_unity] nur Daten nicht möglich: {e["id"]} Netze geändert ({", ".join(diff[:6])}) – voller Export nötig', flush=True)
                sys.exit(2)
            how = 'full' if diff else 'reuse'
            print(f'[export_unity] {e["id"]}: Waffenmodul geändert, Netzgrenzen ' + ('geändert: backen' if diff else 'gleich: FBX und Atlanten bleiben'), flush=True)
        if how == 'reuse':
            o = old[4][e['id']]
            e['textures'], e['mesh_bounds'] = o['textures'], o['mesh_bounds']
        else:
            e['textures'] = bake_weapon(sc, e, tex_dir, gpu)
            e['mesh_bounds'] = dict(de='Netzgrenzen je Objekt im eigenen Objektraum (Blender, m, Modifikatoren angewandt)',
                                    objects=[b for k, b in mesh_bounds().items() if k in ids])
            tri = sum(b['tris'] for b in e['mesh_bounds']['objects'])
            print(f"[export_unity] {e['id']}: {len(e['mesh_bounds']['objects'])} Netze ({tri} Dreiecke) → {e['weapon']['fbx']}", flush=True)
        if i == 0 and arms_new:                # Arme sind für alle Waffen gleich: einmal in der Szene der ersten Waffe
            shared_tex = dict(de='Gebackene Atlanten (kit.aaa_nodes, Skin standard) und AgX-LUT; nicht gebacken: Glas, Leuchtteile',
                              arms=bake_arms(sc, tex_dir, gpu), lut=BK.agx_lut(os.path.join(tex_dir, 'agx_lut.png')))
            arm_bounds = dict(de='Netzgrenzen der Armteile im eigenen Objektraum (Blender, m, Modifikatoren angewandt)',
                              objects=[b for k, b in mesh_bounds().items() if k not in ids])
    D['textures'], D['mesh_bounds'] = shared_tex, arm_bounds
    write_json(os.path.join(DST, 'ego.json'), D)
    for f in ('ego_reference.json', 'ego_reference.json.meta'):      # bis 0.17 eine Referenz für die Pilotwaffe
        if os.path.exists(os.path.join(DST, f)):
            os.remove(os.path.join(DST, f))
    print(f"[export_unity] ego.json {FORMAT}: " + ', '.join(f"{e['id']} {plan[e['id']]}" for e in D['weapons']) +
          f"; Arme {'gebacken' if arms_new else 'übernommen'} → {DST}", flush=True)


if __name__ == '__main__':
    try:
        import bpy  # noqa: F401
        IN_BLENDER = True
    except ImportError:
        IN_BLENDER = False
    if IN_BLENDER:
        blender_main()
    else:
        sys.exit(check() if '--check' in sys.argv else (print(__doc__) or 0))
