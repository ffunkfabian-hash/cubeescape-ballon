"""Export für das Unity-Projekt (0.4 „Firstfeel“): Pilotwaffe und Roboterarme als FBX, Ego-Daten als JSON (`ballon-ego/4`).

  BALLON_BAKE_GPU=1 ce lock gpu -- blender -b --factory-startup -P <abs>/tools/export_unity.py   → unity/Assets/Ballon/Generated/
        BASIC-01-v2.1.fbx (Waffe: Wurzel → ASM_* → Teile, Anker als Leerknoten), arms.fbx (R_/L_-Segmente → Teile),
        ego.json (Daten), ego_reference.json (Blender-Auswertung von tools/ego_build.evaluate als Testreferenz)
  python3 tools/export_unity.py --check   → ego.json passt zu den Python-Daten (ohne Blender, Teil von ./check)

Alle Werte stehen im Blender-Kameraraum (Meter, rechts −X, vorn −Y, oben +Z), wie tools/ego_build.py rechnet; die Laufzeit in C#
rechnet dort und wandelt erst am Ende nach Unity. Die Umrechnung steht **einmal** hier (`AXES`) und wird von Unity gelesen und
getestet: Unity (x rechts, y oben, z vorn, linkshändig) = (−x, z, −y). Autorenmaß (f, u, x) mm → Blender (x, −f, u) m.
"""
import ast
import hashlib
import importlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic.arms import robot_arm as RA, ego as EG  # noqa: E402

FORMAT = 'ballon-ego/7'   # 7 (0.16): motion.flash (Mündungsfeuer), motion.eject und weapon.eject (Hülsen), Rollen flash_*; 6 (0.15): motion.recoil neu (Bahn, Kamera, Modellkick, Erholung, Salven, Streuung) und motion.switch; 5 (0.13): gameplay.weapon_type/world_zoom/zoom_table/hip (Weltzoom je Klasse, Hüft-Fadenkreuz); 4 (0.10): secondary.aim_freq_hz/aim_zeta (Zielen ohne Überschwingen); 3 (0.7.1/0.7.2): Spiegelkarte spec statt mask, textures.skins; 2 (0.7): Atlanten, AgX-LUT. Ältere neu erzeugen
WEAPON = 'pilot.w01_auto_rifle_v21'
WEAPON_SRC = 'basic/pilot/w01_auto_rifle_v21.py'
DST = os.path.join(ROOT, 'unity', 'Assets', 'Ballon', 'Generated')
MM = 0.001
AXES = dict(to_unity=[[-1, 0, 0], [0, 0, 1], [0, -1, 0]],
            de='Unity = M · Blender; Blender-Kameraraum rechts −X, vorn −Y, oben +Z → Unity rechts +X, oben +Y, vorn +Z')
# Spielwerte der Pilotwaffe: Kadenz wie der Clip fire_hip (Nutzer 25.10.2026, Entscheidungsliste Frage 7.1 A), Magazin Entwurf
GAMEPLAY = dict(rpm=720, magazine=30, src='M 720/min (Chroma Rush, Motiongen waffenwerte › 4; Frage 7.1 A), Clip fire_hip seit 0.15 '
                                          'ebenso (alle 2,5 Bilder); Magazin 30 E (Entwurf, Vorschlag Übergabe 0.4)')
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
    """Spielwerte der Pilotwaffe: Kadenz und Magazin (GAMEPLAY), Weltzoom der Klasse (Entscheidungsliste 1.2 A) und das
    Hüft-Fadenkreuz (4.1 A / 4.2 A) aus dem Absehen-Katalog basic/reticles.py, aufgelöst für den Waffentyp."""
    from basic import reticles as RT
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


def weapon_data(W):
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
    wid = W.META['id'] + (f"-{W.META['variant']}" if W.META.get('variant') else '')
    return dict(id=wid, root=W.META['id'], name=W.META['name'], fbx=f'{wid}.fbx', parts=parts, anchors=anchors,
                eject=eject_data(W)), kit_materials()


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


def data():
    W = importlib.import_module(f'basic.{WEAPON}')
    weapon, roles = weapon_data(W)
    poses = []
    for k, P in EG.POSES.items():
        d = dict(name=k, ads='eye' in P, roll=r6(P.get('roll', 0)), src=P['src'],
                 pos=r6(P.get('pos', (0, 0, 0))), aim=r6(P.get('aim', (0, 0, 0))),
                 eye=r6(P.get('eye', (0, 0, 0))), aim_dir=r6(P.get('aim_dir', (0, 0, 0))))
        poses.append(d)
    grips = [dict(name=k, part=G.get('part', ''), contact=xyz(*G['contact']), palm=vdir(G['palm']), fingers=vdir(G['fingers']),
                  fingers_pose=G['fingers_pose'], src=G['src']) for k, G in EG.GRIPS.items()]
    fingers = [dict(name=k, f=[float(a) for row in v['f'] for a in row], t=[float(a) for a in v['t']])
               for k, v in RA.FINGER_POSES.items()]
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
    srcs = ['basic/pilot/w01_auto_rifle_v21.py', 'basic/weapons/w01_auto_rifle.py', 'basic/common.py', 'basic/kit.py',
            'basic/arms/robot_arm.py', 'basic/arms/ego.py', 'tools/ego_build.py', 'tools/blender_build.py', 'tools/export_unity.py',
            'tools/bake_unity.py']
    sources = dict(de='SHA-256 der Generatorquellen beim Export; --check meldet auch reine Formänderungen',
                   files=[dict(path=p, sha256=hashlib.sha256(open(os.path.join(ROOT, p), 'rb').read()).hexdigest()) for p in srcs],
                   parts_sha256=parts_sha(W))
    used = sorted({p['role'] for p in weapon['parts']} | {p['role'] for p in arm['pieces']} | {EG.EJECT['role']})
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
                gameplay=gameplay(W.META['type']), weapon=weapon, arm=arm, poses=poses, grips=grips, finger_poses=fingers,
                actions=[action(k, A) for k, A in EG.ACTIONS.items()],
                roles=[dict(role=r, color=roles[r]['color'], aaa_color=roles[r].get('aaa_color', roles[r]['color']),
                            rough=roles[r]['rough'], metal=roles[r]['metal'], alpha=roles[r].get('alpha', 1.0),
                            emit=roles[r].get('emit', 0.0), emit_only=bool(roles[r].get('emit_only')), spec=roles[r].get('spec', 0.5),
                            de=roles[r]['de']) for r in used + sorted(EG.FLASH['roles'])])


def write_json(path, obj):
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write('\n')


MOTION_SOURCES = {'basic/arms/ego.py', 'tools/ego_build.py', 'tools/export_unity.py'}   # dürfen sich im Datenexport ändern


def data_only_allowed(D):
    """(altes ego.json, Grund) – Grund None, wenn nur Bewegungsquellen anders sind als beim letzten vollen Export; sonst wären
    FBX, Atlanten und Netzgrenzen veraltet, während --check „aktuell“ meldet (Richter 0.10)."""
    p = os.path.join(DST, 'ego.json')
    if not os.path.exists(p):
        return None, 'kein ego.json'
    with open(p, encoding='utf-8') as fh:
        old = json.load(fh)
    if 'textures' not in old or 'mesh_bounds' not in old:
        return None, f"altes ego.json ({old.get('format')}) ohne Atlanten oder Netzgrenzen"
    was = {f['path']: f['sha256'] for f in old.get('sources', {}).get('files', [])}
    changed = [f['path'] for f in D['sources']['files'] if f['path'] not in MOTION_SOURCES and was.get(f['path']) != f['sha256']]
    if changed == [WEAPON_SRC]:        # nur das Waffenmodul: erlaubt, wenn der Bauteil-Entwurf gleich ist (Form, Material, Bewegung; z. B.
        want = old['sources'].get('parts_sha256') or parts_sha_at(WEAPON_SRC, was.get(WEAPON_SRC))   # nur EJECT neu) und die
        if want is None:                                                                              # Netze gleich bleiben
            return None, f'{WEAPON_SRC} geändert, Bauteil-Entwurf des letzten Exports nicht auffindbar'
        if want != D['sources']['parts_sha256']:
            return None, f'{WEAPON_SRC}: Bauteile geändert (Form, Material oder Bewegung)'
        return old, 'bounds'           # dazu Netzgrenzen in blender_main (Richter 0.16: Grenzen allein beweisen keine gleiche Geometrie)
    if changed:
        return None, 'Form- oder Materialquellen geändert: ' + ', '.join(changed)
    return old, None


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


def write_reference(ref):
    with open(os.path.join(DST, 'ego_reference.json'), 'w', encoding='utf-8') as fh:   # groß: kompakt, eine Probe je Zeile
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
    diff = [k for k in new if cur.get(k) != new[k]]
    if diff:
        print('ego.json veraltet (' + ', '.join(diff) + '): Export neu ausführen')
        return 1
    print(f"unity: ego.json aktuell ({len(new['actions'])} Aktionen, {len(new['weapon']['parts'])} Waffenteile, "
          f"{len(new['arm']['pieces'])} Armteile)")
    return 0


# ------------------------------------------------------------------ Blender-Teil
REF_OBJECTS = ['magazine', 'charging_handle', 'mag_release', 'trigger', 'bolt_carrier', 'port_cover']
REF_SEGMENTS = ['upper', 'fore', 'hand', 'f0_0', 'f0_2', 'f3_1', 't_0', 't_2']


def blender_main():
    import bpy
    from mathutils import Matrix
    gpu = '--gpu' in sys.argv or os.environ.get('BALLON_BAKE_GPU') == '1'   # GPU-Backen (nur unter ce lock gpu; ce lock reicht '-- --gpu' nicht durch)
    sys.argv = [sys.argv[0]]                   # ego_build.args() liest nichts mehr
    from tools import bake_unity as BK
    from tools import ego_build as EB
    W = importlib.import_module(f'basic.{WEAPON}')
    os.makedirs(DST, exist_ok=True)
    D = data()
    data_only = os.environ.get('BALLON_EXPORT_DATA_ONLY') == '1'
    if data_only:                                      # vor jeder Arbeit: darf der Datenexport Atlanten, Netze und FBX übernehmen?
        old, why = data_only_allowed(D)
        if why and why != 'bounds':
            print(f'[export_unity] nur Daten nicht möglich: {why} – voller Export nötig (ohne BALLON_EXPORT_DATA_ONLY)', flush=True)
            sys.exit(2)
    sc = EB.Scene(W, dict(stills=False, actions=[], gpu=False, samples=1, weapon=WEAPON, fx=False))

    def flat(M):
        return r6([M[i][j] for i in range(4) for j in range(4)])

    def snap(label, action, frame):
        objs = {'weapon': flat(sc.root.matrix_world), 'camera': flat(sc.cam_base.inverted() @ sc.cam.matrix_world)}
        for pid in REF_OBJECTS:
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
    for name, A in EG.ACTIONS.items():
        st, rep = {}, {}
        n = A['frames']
        frames = sorted({*range(0, n + 1, max(1, n // 8)), n, *[f for f, _ in A.get('events', [])]})
        if A.get('fire'):                                  # Feueraktionen lückenlos: jedes Blitz- und Hülsenbild prüfen
            frames = list(range(0, n + 1))
        for f in range(0, n + 1):                          # lückenlos auswerten (Zustand Magazin), nur Stichproben speichern
            EB.evaluate(sc, A, f, rep, st)
            if f in frames:
                samples.append(snap(f'{name}:{f}', name, f))
        print(f'[export_unity] {name}: {len(frames)} Stichproben, Handgelenk max {rep.get("wrist_max_deg", 0):.1f}°')
    ref = dict(format=FORMAT + '-reference', de='Weltmatrizen (Blender-Kameraraum, zeilenweise) aus tools/ego_build.evaluate',
               tolerance_m=0.0005, tolerance_deg=0.1, samples=samples)

    # Ruhelage für den Export: Waffe im Ursprung, Teile in Ruhe, Armsegmente im Ursprung
    sc.set_weapon(Matrix.Identity(3), Matrix.Identity(4).translation, {}, {})
    for s in ('R', 'L'):
        for e in sc.arms[s][0].values():
            e.matrix_world = Matrix.Identity(4)
    bpy.context.view_layer.update()
    if data_only:                                      # nur Bewegung/Daten geändert (0.10): Atlanten, Netzgrenzen und FBX bleiben
        if why == 'bounds':                            # 0.16: Waffenmodul geändert – nur zulässig, wenn alle Netze gleich geblieben sind
            now = mesh_bounds()
            was = {b['name']: b for b in old['mesh_bounds']['objects']}
            diff = sorted(k for k in set(now) | set(was) if now.get(k) != was.get(k))
            if diff:
                print(f'[export_unity] nur Daten nicht möglich: Netze geändert ({", ".join(diff[:6])}) – voller Export nötig', flush=True)
                sys.exit(2)
            print(f'[export_unity] Waffenmodul geändert, {len(now)} Netzgrenzen unverändert: FBX und Atlanten bleiben gültig', flush=True)
        D['textures'], D['mesh_bounds'] = old['textures'], old['mesh_bounds']
        write_json(os.path.join(DST, 'ego.json'), D)
        write_reference(ref)
        print(f'[export_unity] nur Daten: ego.json + Referenz ({len(samples)} Proben), Atlanten und FBX unverändert', flush=True)
        return
    # Material backen (0.7): je FBX ein Atlas aus kit.aaa_nodes, dazu die AgX-LUT der Blender-Ansicht
    wobs = [sc.root] + list(sc.root.children_recursive)
    aobs = [o for s in ('R', 'L') for e in sc.arms[s][0].values() for o in [e] + list(e.children)]
    tex_dir = os.path.join(DST, 'Textures')
    os.makedirs(tex_dir, exist_ok=True)
    textures = {}
    for key, obs, size in (('weapon', wobs, 4096), ('arms', aobs, 2048)):
        meshes = [o for o in obs if o.type == 'MESH']
        BK.apply_modifiers(meshes)
        bake = [o for o in meshes if BK.bakeable(o)]
        BK.unwrap(bake)
        if key == 'arms':       # Segmente stehen in Ruhe alle im Ursprung: zum Backen auseinanderlegen, sonst sehen Abrieb und AO
            for si, s in enumerate(('R', 'L')):         # Finger, Handfläche und Handrücken ineinander (schwarze Streifen)
                for i, e in enumerate(sc.arms[s][0].values()):
                    e.matrix_world = Matrix.Translation((i * 0.5, si * 1.0, 0.0))
            bpy.context.view_layer.update()
        files = BK.bake_atlas(bake, key, size, tex_dir, gpu=gpu, join_all=(key == 'arms'))
        if key == 'arms':
            for s in ('R', 'L'):
                for e in sc.arms[s][0].values():
                    e.matrix_world = Matrix.Identity(4)
            bpy.context.view_layer.update()
        textures[key] = dict(size=size, objects=sorted(o.name for o in bake), **files)
        print(f'[export_unity] Atlas {key}: {len(bake)} Objekte, {size}²')
    # Skins (kit.SKINS) für die Waffe: Farbe und Glanz je Skin neu backen; Arme bleiben im Standard (Waffen-Skin färbt die Arme nicht)
    from basic import kit
    wb = textures['weapon']['objects']
    wbake = [o for o in wobs if o.name in set(wb)]
    skins = [dict(name='standard', de=kit.SKINS['standard']['de'], kind=kit.SKINS['standard']['kind'],
                  albedo=textures['weapon']['albedo'], spec=textures['weapon']['spec'])]
    for skin, S in kit.SKINS.items():
        if skin == 'standard':
            continue
        kit.SKIN['name'] = skin
        kit.set_mode(sc.objs, 'aaa')
        f = BK.bake_atlas(wbake, f'weapon_{skin}', 4096, tex_dir, gpu=gpu, color_only=True)
        skins.append(dict(name=skin, de=S['de'], kind=S['kind'], **f))
    kit.SKIN['name'] = 'standard'
    kit.set_mode(sc.objs, 'aaa')
    textures['skins'] = skins
    textures['lut'] = BK.agx_lut(os.path.join(tex_dir, 'agx_lut.png'))
    D['textures'] = dict(de='Gebackene Atlanten (kit.aaa_nodes, Skin standard) und AgX-LUT; nicht gebacken: Glas, Leuchtteile',
                         **textures)
    bounds = mesh_bounds()
    D['mesh_bounds'] = dict(de='Netzgrenzen je Objekt im eigenen Objektraum (Blender, m, Modifikatoren angewandt)',
                            objects=list(bounds.values()))

    def export(path, obs):
        bpy.ops.object.select_all(action='DESELECT')
        for o in obs:
            o.select_set(True)
        bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'EMPTY', 'MESH'}, use_mesh_modifiers=True,
                                 mesh_smooth_type='OFF', use_custom_props=False, add_leaf_bones=False, bake_anim=False,
                                 apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL', bake_space_transform=True,
                                 axis_forward='-Z', axis_up='Y', path_mode='STRIP', embed_textures=False)
    export(os.path.join(DST, D['weapon']['fbx']), wobs)
    export(os.path.join(DST, D['arm']['fbx']), aobs)
    write_json(os.path.join(DST, 'ego.json'), D)
    write_reference(ref)
    tri_w = sum(b['tris'] for k, b in bounds.items() if k in {p['id'] for p in D['weapon']['parts']})
    print(f"[export_unity] {len(wobs)} Waffenobjekte ({tri_w} Dreiecke), {len(aobs)} Armobjekte, {len(samples)} Referenzproben → {DST}")


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
