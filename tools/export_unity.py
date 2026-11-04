"""Export für das Unity-Projekt (0.4 „Firstfeel“, je Waffe seit 0.18 „Quickdraw“): spielbare Waffen (WEAPONS) und Roboterarme als FBX,
Ego-Daten als JSON (`ballon-ego/8`).

  BALLON_BAKE_GPU=1 ce lock gpu -- blender -b --factory-startup -P <abs>/tools/export_unity.py   → unity/Assets/Ballon/Generated/
        <Waffe>.fbx je Waffe (Wurzel → ASM_* → Teile, Anker als Leerknoten), arms.fbx (R_/L_-Segmente → Teile),
        ego.json (Daten: Gemeinsames + weapons[]), ego_reference_<Waffe>.json (Blender-Auswertung von tools/ego_build.evaluate als
        Testreferenz). Gebacken wird nur, was sich geändert hat: eine Waffe, deren Form gleich blieb, behält Atlanten, Netzgrenzen und FBX
        (wie BALLON_EXPORT_DATA_ONLY=1 je Waffe); geänderte gemeinsame Formquellen backen alles neu.
  python3 tools/export_unity.py --check   → ego.json passt zu den Python-Daten (ohne Blender, Teil von ./check), Waffentexturen nach TEXTURE_STORE
  python3 tools/export_unity.py --store-textures → Waffenatlanten und Skins im vorhandenen ego.json nach TEXTURE_STORE ablegen (0.20, ohne Backen)
  python3 tools/export_unity.py --formgen → Formgen-Varianten aus Generated/Formgen/<ID>/ in ego.json eintragen (0.41, ohne Blender;
        tools/formgen_import.py). Eintrag je Variante: Grundtyp aus dem Paket, Haltungen/Griffe/Gameplay geerbt, Pfade relativ zu dir.

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
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic.arms import robot_arm as RA, ego as EG  # noqa: E402
from basic import variant as VA  # noqa: E402
from basic import loadout as LO  # noqa: E402

FORMAT = 'ballon-ego/12'   # 12 (0.42 „Quickslot“): hud (Kategorien, Leiste 1–9, Standard-Skin je Klasse aus basic/loadout.py); Unity liest /11 weiter (ohne hud: eine Kategorie, Leiste nach ego.json); 11 (0.41 „Intake“): weapons[].dir (Ordner unter Generated, leer = BALLONs eigene Waffe) und weapons[].origin (Herkunft einer Formgen-Variante, fehlt bei BALLONs Waffen), Formgen-Pakete unter Generated/Formgen/<ID>/ (tools/formgen_import.py); Unity liest /10 weiter (dir leer); 10 (0.39.1 ergänzt, ohne neues Format: motion.recoil/gameplay.recoil.support_still_dip – fehlt = 0, die Stützhand folgt dem Unterschwingen wie bis 0.39; Unity liest es ab 0.39.1); 10 (0.39 ergänzt, ohne neues Format: gameplay.fx pellet_impact/charge_*, motion.payload.surfaces/charge_glow, motion.payload.impacts[].hole_k, motion.payload.decal.min_life_s – fehlt = leer bzw. 0, Verhalten wie 0.38 (Form des Ladeleuchtens: Werte von 0.39); Unity liest sie ab 0.39); 10 (0.36 ergänzt, ohne neues Format: gameplay.zoom_in_min_s, gameplay.hip.shown_in, gameplay.hip.spread.charge_from, motion.recoil/gameplay.recoil.support_still – fehlt = 0 bzw. leer, Verhalten wie 0.35; Unity liest sie ab 0.36); 10 (0.33 ergänzt, ohne neues Format: weapon.live.glow, fehlt = leer; P3: gameplay.charge_s/charge_fade_s, 0 = ohne Aufladen); 10 (0.22): gameplay.burst_shots/burst_rpm (Salve je Klasse; Salvenlänge aus META fire) statt motion.recoil.burst_*, gameplay.path_up_h (Bahnstufe je Schuss je Klasse), gameplay.muzzle_flash, gameplay.portals/ring_turn_s und weapon.live.ring (Werkzeug), gameplay.sight 'none' ohne Visier; Klassen ohne Zielen/Nachladen lassen diese Aktionen und Haltungen weg; 9 (0.20): gameplay.fire_mode (Feuerart aus META fire), gameplay.zoom_start, roles[].no_coat (Linse im Rohr), weapon.parts[].ads_hide und motion.ads_hide (Zielfernrohr: Teile im Zielen aus), weapons[].textures.store/limit_mb (Ablage je Kanal); 8 (0.18): weapons[] je spielbarer Waffe (gameplay, weapon mit live, poses, grips, actions, profile, textures, mesh_bounds, sources, reference), gemeinsam motion/camera/arm/finger_poses/roles/textures(arms, lut)/mesh_bounds(arms); 7 (0.16): motion.flash (Mündungsfeuer), motion.eject und weapon.eject (Hülsen), Rollen flash_*; 6 (0.15): motion.recoil neu (Bahn, Kamera, Modellkick, Erholung, Salven, Streuung) und motion.switch; 5 (0.13): gameplay.weapon_type/world_zoom/zoom_table/hip (Weltzoom je Klasse, Hüft-Fadenkreuz); 4 (0.10): secondary.aim_freq_hz/aim_zeta (Zielen ohne Überschwingen); 3 (0.7.1/0.7.2): Spiegelkarte spec statt mask, textures.skins; 2 (0.7): Atlanten, AgX-LUT. Ältere neu erzeugen
# Spielbare Waffen in Unity, Reihenfolge = Taste 1, 2, 3 … (Entscheidungsliste Schritt 6: Ego-Übertrag je Klasse; BASIC-06 Nutzerwahl
# 26.10.2026, BASIC-03 Scout seit 0.20 „Spotter“, Impuls BASIC-02 und Portalkanone BASIC-T01 seit 0.22 „Volley“, Handfeuerwaffe BASIC-04
# und Seitenwaffe BASIC-05 seit 0.33 „Armory“ P1, Scharfschütze BASIC-09, Spurgewehr BASIC-12 und MG BASIC-15 seit P2: Tasten 8, 9, 0;
# Schrotflinte BASIC-08, Fusion BASIC-10, lineare Fusion BASIC-11 seit P3: ohne Taste, bis das Waffenmenü (Ziel 2) sie wählt)
WEAPONS = ['pilot.w01_auto_rifle_v21', 'pilot.w06_submachine_gun_v21', 'pilot.w03_scout_rifle_v21', 'pilot.w02_pulse_rifle_v21',
           'pilot.t01_portal_cannon_v21', 'pilot.w04_hand_cannon_v21', 'pilot.w05_sidearm_v21', 'pilot.w09_sniper_rifle_v21',
           'pilot.w12_trace_rifle_v21', 'pilot.w15_machine_gun_v21', 'pilot.w08_shotgun_v21', 'pilot.w10_fusion_rifle_v21',
           'pilot.w11_linear_fusion_rifle_v21', 'pilot.w07_combat_bow_v21', 'pilot.w13_grenade_launcher_v21', 'pilot.w14_rocket_launcher_v21']
WEAPON = WEAPONS[0]                 # Pilotwaffe (./check: Mündungsfeuer im Zielen, Bezug der Automatik)
SHARED_SRC = ['basic/common.py', 'basic/kit.py', 'basic/arms/robot_arm.py', 'basic/arms/ego.py', 'tools/ego_build.py',
              'tools/blender_build.py', 'tools/export_unity.py', 'tools/bake_unity.py']
ATLAS_KEY = {'BASIC-01-v2.1': 'weapon'}   # Dateinamen der Pilotwaffe seit 0.7 (weapon_albedo.png …); andere: weapon_<Waffe>
DST = os.path.join(ROOT, 'unity', 'Assets', 'Ballon', 'Generated')
# Ablage der Waffenatlanten und Skins (0.20 „Spotter“, Entscheidung 97 A, Nutzer 26.10.2026: „A“): gebacken wird weiter mit 4096²
# (tools/bake_unity.py), gespeichert je Kanal kleiner. Bis 0.19 lagen alle Kanäle als 4096²-PNG im Repo (Normale und AO mit 16 bit),
# BASIC-06 mit 7 Skins 191 MB. Unity liest die Dateien mit Kompression (BC7/BC5, 8 bit je Kanal): 16 bit trägt dort nichts bei.
# Gemessen am Ego-Bild (Hüfte, Zielen) vorher/nachher, siehe docs/unity.md › Texturen. Gilt nur für die Waffen, nicht für die Arme.
TEXTURE_STORE = dict(
    albedo=dict(size=4096, ext='jpg', quality=92,
                de='Diffusfarbe: volle Kantenlänge (Schrift, Kanten, Sprenkel), JPG Qualität 92 ohne Farbunterabtastung (4:4:4)'),
    spec=dict(size=2048, ext='png',
              de='Spiegelfarbe mit Glätte im Alpha: halbe Kantenlänge (linear verkleinert), PNG 8 bit RGBA – JPG trägt kein Alpha'),
    normal=dict(size=4096, ext='png',
                de='Normale: volle Kantenlänge, PNG 8 bit statt 16 (verlustarm: Unity speichert Normalen mit 8 bit je Kanal)'),
    ao=dict(size=2048, ext='png', de='AO: halbe Kantenlänge, ein Kanal mit 8 bit (niederfrequent)'),
    limit_mb=50.0,
    de='Grenze je Waffe ≈ ¼ von BASIC-06 vorher (191 MB); Unity-Test Texturen_je_Waffe_unter_der_Grenze und export_unity.py --check')
# Skins (0.42 „Quickslot“, Entscheid 247 A): keine Farb- und Glanzkarten je Skin mehr im Repo (bis 0.42 ≈ 4 MB je Skin und Waffe,
# 0.33–0.41 nur für sieben Waffen gebacken). Je Waffe backt tools/skin_masks.py einmal Masken (textures.skin_masks); tools/skin_compose.py
# setzt jeden Skin aus kit.SKINS lokal zusammen (unity_run.py setup), Dateinamen wie gebackene Skins. textures.skins nennt alle Skins.
SKIN_FILES_COMPOSED = True


def skin_entries(atlas, weapon_atlas):
    """textures.skins einer BALLON-Waffe: standard = Atlas, übrige aus kit.SKINS mit den Dateinamen der Zusammensetzung."""
    S = kit_literal('SKINS')
    out = [dict(name='standard', de=S['standard']['de'], kind=S['standard']['kind'], albedo=weapon_atlas['albedo'], spec=weapon_atlas['spec'])]
    for k, v in S.items():
        if k != 'standard':
            out.append(dict(name=k, de=v['de'], kind=v['kind'], albedo=f'{atlas}_{k}_albedo.jpg', spec=f'{atlas}_{k}_spec.png',
                            composed=True))
    return out


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


# Felder von gameplay, die nicht jede Klasse nennt (0.22): ohne Salve, mit Mündungsfeuer, ohne Portale
GAMEPLAY_DEFAULTS = dict(burst_shots=0, burst_rpm=0, muzzle_flash=True, ring_turn_s=0.0, portals=[], range_m=0.0, charge_s=0.0, charge_fade_s=0.0,
                         flash_scale=1.0,   # 0.33 P4: Maßstab des Mündungsfeuers je Klasse (Werfer: Öffnung ≤ 20 %)
                         zoom_in_min_s=0.0)  # 0.36: kürzeste Dauer des Weltzooms ins Zielen je Klasse (0 = folgt nur dem Modell)


def gameplay(weapon_type, G=None):
    """Spielwerte der Klasse: Kadenz, Magazin, Salve, Bahnstufe, Portale (ego.profile › gameplay, sonst ego.CLASSES), Weltzoom der Klasse
    (Entscheidungsliste 1.2 A) und das Hüft-Fadenkreuz (4.1 A / 4.2 A) aus dem Absehen-Katalog basic/reticles.py, aufgelöst für den
    Waffentyp. Ohne Visier (Werkzeug) Visiertyp 'none' und Weltzoom 1."""
    from basic import reticles as RT
    GAMEPLAY = dict(GAMEPLAY_DEFAULTS, **(G if G is not None else EG.CLASSES[weapon_type]['gameplay']))
    H = RT.hud_hip(weapon_type)          # 0.33: HUD-Hüftzeichen (Sonderklassen nach Glidepath); das Absehen im Glas bleibt RT.hip (sight_form)
    G0 = RT.hip(weapon_type)
    S = RT.SPREAD[H['spread']]
    sp = H['sprint']
    sprint = dict(kind=sp['kind'], share_h=sp['share_h'], extent_mm=sp['extent_mm'], prims=[prim(q) for q in RT.RETICLES[sp['kind']]['prims']]) \
        if sp else dict(kind='', share_h=0.0, extent_mm=0.0, prims=[])
    hip = dict(kind=H['kind'], share_h=H['share_h'], extent_mm=H['extent_mm'], status=H['status'],
               color=RT.COLORS[RT.HIP['color']][1], weight=RT.WEIGHTS[RT.HIP['weight']][1], line_r_mm=RT.LINE_R,
               opacity=RT.SETTINGS['opacity']['default'], min_line_px=RT.HIP['min_line_px'],
               prims=[prim(q) for q in RT.RETICLES[H['kind']]['prims']],
               spread=dict(id=H['spread'], **{k: S[k] for k in ('base', 'per_shot', 'max', 'recover_s', 'move')},
                           charge_from=S.get('charge_from', 0.0)), sprint=sprint, shown_in=list(RT.HIP['shown_in']),
               src='basic/reticles.py › HIP, DEFAULTS, SPREAD (Entscheidungsliste 4.1 A, 4.2 A; Glidepath)')
    sighted = RT.SIGHT_KIND[weapon_type] is not None
    return dict(GAMEPLAY, weapon_type=weapon_type, sight=RT.sight_type(weapon_type) if sighted else 'none',
                world_zoom=RT.class_world_zoom(weapon_type) if sighted else 1.0,
                zoom_table=[dict(type=k, zoom=RT.class_world_zoom(k)) for k in RT.CLASS_ZOOM], hip=hip,
                sight_form=dict(kind=G0['kind'], share_h=G0['share_h'], extent_mm=G0['extent_mm'],
                                prims=[prim(q) for q in RT.RETICLES[G0['kind']]['prims']]))


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
    return kit_literal('MATERIALS')


def kit_literal(name):
    """Ein Literal aus basic/kit.py ohne bpy (MATERIALS, SKINS)."""
    tree = ast.parse(open(os.path.join(ROOT, 'basic', 'kit.py'), encoding='utf-8').read())
    node = next(n for n in tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == name)
    return eval(compile(ast.Expression(node.value), 'kit.py', 'eval'), {'__builtins__': {}, 'dict': dict})


def weapon_data(W, live):
    W = VA.resolve(W)                               # 0.41: Weltpunkte aus POINTS (Varianten: verschoben mit ihren Teilen)
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
        elif mv and mv['kind'] == 'segment':   # Sehnenhälfte (0.33 P4, Bogen): rest = festes Ende (Wurfarmspitze), axis = Weg festes Ende →
            tip, nock = mv['tip'], mv['nock']     # Nockpunkt in Ruhe (m, kein Einheitsvektor), vec = Weg des Nockpunkts bei Anteil 1
            m.update(kind='segment', vec=xyz(*mv['vector_mm']), axis=xyz(*[b - a for a, b in zip(tip, nock)]))
        elif mv:
            m['kind'] = mv['kind']          # glow: in der Pilotwaffe nicht vorhanden, Laufzeit meldet unbekannte Arten
        parts.append(dict(id=p['id'], asm=p['asm'], role=p['mat'], parent=p.get('parent_part') or '', rest=rest, move=m,
                          ads_hide=bool(p.get('ads_hide')) or p['id'] in EG.profile(W)['ads_hide']))   # 0.33 P4: auch je Klasse (Bogen)
    anchors = [dict(id=k, part=v.get('part', ''), pos=xyz(*v['at'])) for k, v in W.ANCHORS.items()]
    wid = EG.weapon_id(W)
    ids = {p['id'] for p in parts}
    glow = list(live.get('glow', ()))              # 0.33: Leuchtteile, die beim Feuern angehen (Dauerstrahl), Bewegung glow
    missing = [v for k, v in live.items() if k in ('trigger', 'bolt', 'port', 'ring') and v and v not in ids] + [g for g in glow if g not in ids]
    if missing:
        raise KeyError(f'{wid}: Live-Teile {missing} fehlen (ego.LIVE bzw. Modul-Feld EGO_LIVE)')
    moves = {p['id']: p['move']['kind'] for p in parts}
    if any(moves[g] != 'glow' for g in glow):
        raise KeyError(f'{wid}: EGO_LIVE glow nennt Teile ohne Bewegung glow')
    index = list(live.get('index', ()))            # 0.34: Schrittteile je Schuss (Trommel, Gurtvorschub), Bewegung mit cycle 'shot'
    R = live.get('rounds') or {}                   # 0.34: Füllstand – Teile je Patrone (Gurt) bzw. je Kammer (Trommel)
    rounds = dict(mode=R.get('mode', ''), drum=R.get('drum', ''), barrel=R.get('barrel', 0), gate=R.get('gate', 0),
                  sets=[dict(parts=list(s)) for s in R.get('sets', ())])
    fill = list(live.get('fill', ()))              # 0.34: Zählfenster – Leuchtzellen nach dem Anteil der Munition
    bad = [q for q in index + fill + [q for s in rounds['sets'] for q in s['parts']] + ([rounds['drum']] if rounds['drum'] else [])
           if q not in ids]
    if bad:
        raise KeyError(f'{wid}: EGO_LIVE index/rounds/fill nennt fehlende Teile {bad}')
    if any(moves[q] != 'glow' for q in fill):
        raise KeyError(f'{wid}: EGO_LIVE fill nennt Teile ohne Bewegung glow')
    return dict(id=wid, root=W.META['id'], name=W.META['name'], type_de=W.META.get('type_de', ''),   # 0.33 Ziel 2: Klasse für HUD und Menü
                fbx=f'{wid}.fbx', parts=parts, anchors=anchors,
                eject=eject_data(W), live=dict({k: live.get(k, '') for k in ('trigger', 'bolt', 'port', 'ring')}, glow=glow,
                                               index=index, rounds=rounds, fill=fill))


def mesh(V, tris):
    """Netz im Autorenmaß (f, u, x mm) → flache Punktliste im Blender-Rahmen (m) und flache Dreiecksliste."""
    return [c for v in V for c in xyz(*v)], [i for t in tris for i in t]


def eject_data(W):
    """Hülsenauswurf der Waffe (Modul-Feld EJECT, 5.4 A): Startlage im Auswurffenster, Richtung (Einheit) und Hülsennetz; enabled false ohne Feld."""
    E = getattr(W, 'EJECT', None)
    if not E:
        return dict(enabled=False, pos=[0.0, 0.0, 0.0], dir=[0.0, 0.0, 0.0], case='', verts=[], tris=[], on='', src='kein Auswurf',
                    part='', ring_m=0.0, ring_n=0, speed_k=1.0, life_k=1.0,
                    links=dict(enabled=False, pos=[0.0, 0.0, 0.0], dir=[0.0, 0.0, 0.0], case='', verts=[], tris=[], src='kein Gliederauswurf'))
    d = vdir(E['dir'])
    n = sum(a * a for a in d) ** 0.5
    vs, ts = mesh(*EG.case_mesh(E['case']))
    ring = E.get('ring') or {}
    L = E.get('links')
    links = dict(enabled=False, pos=[0.0, 0.0, 0.0], dir=[0.0, 0.0, 0.0], case='', verts=[], tris=[], src='kein Gliederauswurf')
    if L:                                           # 0.34: Gurtglied je Schuss (MG), eigene Startlage und Richtung
        dl = vdir(L['dir'])
        nl = sum(a * a for a in dl) ** 0.5
        lv, lt = mesh(*EG.case_mesh(L['case']))
        links = dict(enabled=True, pos=xyz(*L['at']), dir=r6([a / nl for a in dl]), case=L['case'], verts=lv, tris=lt, src=L['src'])
    return dict(enabled=True, pos=xyz(*E['at']), dir=r6([a / n for a in d]), case=E['case'],
                verts=vs, tris=ts, on=E.get('on', 'shot'), src=E['src'],   # on (0.33 P4): 'shot' je Schuss, 'reload' beim Marker Eject
                part=E.get('part', ''), ring_m=r6(ring.get('r_mm', 0.0) * MM), ring_n=ring.get('n', 0),   # 0.34: Start im Teil, Kammerkreis
                speed_k=r6(E.get('speed_k', 1.0)), life_k=r6(E.get('life_k', 1.0)), links=links)   # life_k (0.34): Lebensdauer beim Nachladen


def payload_data():
    """Gemeinsame Werte der Wirkung (0.34, ego.DECAL, IMPACTS, EXPLOSION, MUZZLE_SMOKE; 0.39 IMPACT_SURFACES, CHARGE_GLOW):
    Einschusslöcher, Einschlagstile (Liste mit Namen), Explosion, Mündungsrauch, Untergründe, Form des Ladeleuchtens. Je Klasse steht die Art der Wirkung in gameplay.fx."""
    def num(d):
        return {k: (r6(v) if isinstance(v, float) else v) for k, v in d.items()}
    def boom(name, X):
        X = dict(X)
        colors = X.pop('colors')
        return dict(num(X), name=name, **{f'{k}_color': v for k, v in colors.items()})
    need = {t: P['pellets'] * EG.CLASSES[t]['gameplay']['rpm'] / 60 * EG.DECAL['min_life_s'] for t, P in
            ((t, EG.payload(t)) for t in EG.PAYLOAD) if P['pellets'] > 0 and t in EG.CLASSES}
    short = {t: n for t, n in need.items() if n > EG.DECAL['max']}
    if short:                                       # 0.39: Löcher einer Lochgruppe halten bei Dauerfeuer min_life_s (Aftermath ≥ 9 s)
        raise ValueError(f'DECAL max {EG.DECAL["max"]} reicht nicht für min_life_s {EG.DECAL["min_life_s"]} s: {short}')
    return dict(decal=num(EG.DECAL), impacts=[dict(num(v), name=k) for k, v in EG.IMPACTS.items()],
                surfaces=[dict(num(v), name=k) for k, v in EG.IMPACT_SURFACES.items()],          # 0.39: Untergrund (colliders[].surface)
                charge_glow={k: r6(v) if isinstance(v, (float, tuple)) else v for k, v in EG.CHARGE_GLOW.items()},   # 0.39: Ladeleuchten
                explosion=boom('rocket', EG.EXPLOSION),                                   # bis 0.34.1 die einzige (ältere Leser)
                explosions=[boom(k, v) for k, v in EG.EXPLOSIONS.items()],               # 0.34.2: je Art (PAYLOAD explosion)
                muzzle_smoke=num(EG.MUZZLE_SMOKE))


def flash_data():
    """Mündungsfeuer (ego.FLASH, 5.3 A): Netz relativ zu Socket_Muzzle (Blender-Waffenrahmen, m), Kern- und Flammendreiecke, Dauer,
    Drehfolge um die Laufachse, Rollen."""
    F = EG.FLASH
    V, core, flame = EG.flash_mesh()
    vs, ct = mesh(V, core)
    _, ft = mesh(V, flame)
    return dict(dur_s=r6(F['dur_s']), verts=vs, core_tris=ct, flame_tris=ft, roll_deg=r6(F['roll_deg']), core_role=F['core']['role'],
                flame_role=F['tongues']['role'], src=F['src'])


def charge_span(wid, part, muzzle, spec=None):
    """Ladeleuchten (0.39, ego.PAYLOAD charge_part): Spanne des Teils auf der Kernachse durch Socket_Muzzle (Blender-Meter wie die
    Anker; charge_a hinten, charge_b vorn) und sein Durchmesser charge_ring_m, gemessen aus der Spec (data/specs, für Varianten die Spec
    des Pakets). Ohne Teil: Nullen."""
    if not part:
        return dict(charge_a=[0.0, 0.0, 0.0], charge_b=[0.0, 0.0, 0.0], charge_ring_m=0.0)
    if spec is None:
        spec = json.load(open(os.path.join(ROOT, 'data', 'specs', f'{wid}.spec.json'), encoding='utf-8'))
    b = next((q['bounds_m'] for q in spec['parts'] if q['id'] == part), None)
    if b is None:
        raise KeyError(f'{wid}: charge_part {part} fehlt in der Spec')
    m = xyz(*muzzle)
    if not (b['min'][1] <= b['max'][1] <= 0 and m[1] < b['min'][1]):
        raise ValueError(f'{wid}: charge_part {part} liegt nicht hinter Socket_Muzzle auf der Laufachse (vorn −Y)')
    return dict(charge_a=r6([m[0], b['max'][1], m[2]]), charge_b=r6([m[0], b['min'][1], m[2]]),
                charge_ring_m=r6(max(b['max'][0] - b['min'][0], b['max'][2] - b['min'][2])))


def weapon_files(W):
    """Formquellen einer Waffe: ihr Modul und das Grundmodul, aus dem es META und Baugruppen übernimmt (V1)."""
    fs = [os.path.relpath(W.__file__, ROOT)]
    if getattr(W, 'V1', None) is not None:
        fs.append(os.path.relpath(W.V1.__file__, ROOT))
    return fs


def sha_files(paths):
    return [dict(path=p, sha256=hashlib.sha256(open(os.path.join(ROOT, p), 'rb').read()).hexdigest()) for p in paths]


def weapon_entry(W, atlas_key=None, spec=None, weapon=None):
    """Ein Eintrag von weapons[] (ohne textures/mesh_bounds, die schreibt der Blender-Teil): Ego-Profil der Klasse (ego.profile).
    0.41: auch für ein fremdes Modul oder einen Datensatz (basic/variant.as_module) ohne Eintrag in WEAPONS – atlas_key = Name des
    Atlas (sonst ATLAS_KEY bzw. weapon_<Waffe>), spec = Spec der Variante (Ladeleuchten; sonst data/specs), weapon = fertiger weapon-Block
    (Formgen-Paket ohne Datensatz; sonst aus W)."""
    W = VA.resolve(W)
    P = EG.profile(W)
    weapon = weapon or weapon_data(W, P['live'])
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
    fx = {k: (r6(v) if isinstance(v, float) else v) for k, v in EG.payload(P['type']).items()}   # 0.34: Wirkung der Klasse
    fx.update(charge_span(wid, fx['charge_part'], W.ANCHORS['Socket_Muzzle']['at'], spec))          # 0.39: Ladeleuchten
    return dict(id=wid, profile=profile, gameplay=dict(gameplay(P['type'], P['gameplay']), fire_mode=P['fire_mode'], fx=fx), weapon=weapon, poses=poses, grips=grips,
                actions=[action(k, A) for k, A in P['actions'].items()], atlas=atlas_key or ATLAS_KEY.get(wid, f'weapon_{wid}'),
                reference=f'ego_reference_{wid}.json',
                sources=dict(files=sha_files(weapon_files(W)), parts_sha256=parts_sha(W)))


def data():
    Ws = [importlib.import_module(f'basic.{m}') for m in WEAPONS]
    entries = [weapon_entry(W) for W in Ws]
    from tools import formgen_import as FG       # 0.41: Formgen-Varianten unter Generated/Formgen/<ID>/ hinter BALLONs Waffen
    variants = FG.entries(EU=sys.modules[__name__])
    entries += variants
    roles = kit_materials()
    bases = [importlib.import_module(v['origin']['base_module']) for v in variants]
    for W in Ws + bases:                            # Leuchtrollen aus dem Modul (Portalkanone PORTAL_ROLES, 0.17: kit.py liegt im Quellenhash;
        for R in (getattr(W, 'PORTAL_ROLES', {}), getattr(W, 'CHARGE_ROLES', {})):   # Ladekern der Energiewaffen CHARGE_ROLES, 0.33 P3)
            roles.update({k: v for k, v in R.items() if k not in roles})
        for M in (getattr(W, 'energy_roles', None), getattr(W, 'metal_roles', None)):   # 0.33 P4: Rollenmodule, die das Waffenmodul nur
            for R in (getattr(M, 'CHARGE_ROLES', {}), getattr(M, 'RING_ROLES', {})):     # importiert (Bogen: Pinköpfe, Spannlicht; Werfer: ring_anod)
                roles.update({k: v for k, v in R.items() if k not in roles})
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
                  ads_hide=dict(eye_m=r6(EG.ADS_HIDE['eye_m']), src=EG.ADS_HIDE['src']),
                  aim=dict(range_m=r6(EG.AIM['range_m']), src=EG.AIM['src']),
                  flash=flash_data(),
                  eject=dict(speed_mps=r6(EG.EJECT['speed_mps']), gravity_mps2=r6(EG.EJECT['gravity_mps2']), spin_dps=r6(EG.EJECT['spin_dps']),
                             spin_axis=r6(vdir(EG.EJECT['spin_axis'])), life_s=r6(EG.EJECT['life_s']), max_live=EG.EJECT['max_live'],
                             delay_frames=EG.EJECT['delay_frames'], role=EG.EJECT['role'], src=EG.EJECT['src']),
                  index=dict(frames=r6(EG.INDEX['frames']), share=r6(EG.INDEX['share']), src=EG.INDEX['src']),
                  payload=payload_data(),
                  de='Bewegungsgefühl v2 aus basic/arms/ego.py (Kurven, Feder-Nachlauf, Atmen, Rückstoß, Wechsel, Tempo)')
    return dict(format=FORMAT, generated_by='tools/export_unity.py', sources=sources, axes=AXES, fps=EG.FPS, motion=motion,
                camera=dict(h_fov_deg=EG.CAMERA['h_fov_deg'], aspect=list(EG.CAMERA['aspect']), near_m=EG.CAMERA['near_m']),
                arm=arm, finger_poses=fingers,
                roles=[dict(role=r, color=roles[r]['color'], aaa_color=roles[r].get('aaa_color', roles[r]['color']),
                            rough=roles[r]['rough'], metal=roles[r]['metal'], alpha=roles[r].get('alpha', 1.0),
                            emit=roles[r].get('emit', 0.0), emit_only=bool(roles[r].get('emit_only')), spec=roles[r].get('spec', 0.5),
                            no_coat=bool(roles[r].get('no_coat')),
                            **({'skin_as': roles[r]['skin_as']} if roles[r].get('skin_as') else {}),   # 0.42: Skin-Gruppe (skin_compose)
                            de=roles[r]['de']) for r in used + sorted(EG.FLASH['roles'])],
                hud=LO.hud_data([e['profile']['type'] for e in entries], kit_literal('SKINS')), weapons=entries)


def write_json(path, obj):
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write('\n')


MOTION_SOURCES = {'basic/arms/ego.py', 'tools/ego_build.py', 'tools/export_unity.py'}   # dürfen sich im Datenexport ändern
# Formquellen-Änderungen, die nachweislich nichts am Bau ändern (0.41): {Pfad: [(SHA-256 vorher, nachher, Beleg)]}. Nur genau dieser
# Übergang zählt nicht als Formänderung; jede weitere Änderung der Datei backt wieder alles (Richter 0.10).
NEUTRAL_EDITS = {
    'tools/blender_build.py': [('81d5b02d55747b71285dd9d1b1066a6b12a6f6658ae89c776c4ecb919dc26f12',
                                'ea42dd1b9e5cc7cb8a585913488c57c0aed795d88dff7560e7859776d3769749',
                                '0.41: main(W=…, base=…, argv=…) statt Modulname; GLB und Spec aller 16 Spielwaffen bytegleich zu 0.40 '
                                '(docs/versions/0.41-intake.md › Schnittstellen)')],
    # 0.43: kein neutraler Bau, sondern ein bewusster Übergang: der neue Bake gilt ab dem nächsten vollen Bake. Die 16 Atlanten im Repo bleiben
    # bis dahin die von 0.42 (Nutzerauftrag 0.43 d), damit Skin-Masken und Bild unverändert und keine neuen Binärdateien im Diff sind.
    'tools/bake_unity.py': [('4eaafdb72c7f8a9b76bb5fd7b69da6c85b8c5f40efb34d33b20e5f66c0034d3f',
                             'e8558c5a07353bed8e7a80f0d98bc099151dbee6846a013f4aff2ee3377203a6',
                             '0.43: schnellerer Bake, Atlanten im Repo nicht neu gebacken; Referenz und Grenzwerte data/bake_settings.json '
                             '(docs/versions/0.43-kiln.md › Neue Referenz)')],
}


def neutral_edit(path, was, now):
    """Führt eine Kette aus NEUTRAL_EDITS von SHA was nach now?"""
    seen = set()
    while was != now and was not in seen:
        seen.add(was)
        was = next((b for a, b, _ in NEUTRAL_EDITS.get(path, ()) if a == was), None)
        if was is None:
            return False
    return was == now


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
    own = [e for e in D['weapons'] if 'origin' not in e]   # 0.41: Formgen-Varianten bringen Atlas und FBX im Paket mit
    ids = [e['id'] for e in own]
    if old is None:
        return True, {i: 'full' for i in ids}, {'arms': 'kein ego.json mit Atlanten'}
    fmt, shared, _, _, ents = old
    changed = [f['path'] for f in D['sources']['files'] if f['path'] not in MOTION_SOURCES and shared.get(f['path']) != f['sha256']
               and not neutral_edit(f['path'], shared.get(f['path']), f['sha256'])]
    if changed:
        why = 'Form- oder Materialquellen geändert: ' + ', '.join(changed)
        return True, {i: 'full' for i in ids}, dict({i: why for i in ids}, arms=why)
    plan, why = {}, {}
    for e in own:
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



def _rounded(v, nd=6):
    """Floats auf nd Nachkommastellen (µm bei mm-Maßen) – Winkelfunktionen liefern auf macOS-libm und glibc nicht bitgleiche Werte (0.21)."""
    if isinstance(v, float):
        return round(v, nd) + 0.0                  # + 0.0: −0.0 und 0.0 gleich
    if isinstance(v, dict):
        return {k: _rounded(x, nd) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_rounded(x, nd) for x in v]
    return v


def parts_sha(W):
    """SHA-256 des Bauteil-Entwurfs der Waffe (PARTS und ASSEMBLIES: Form, Materialrolle, Bewegung) ohne Anker und Datenfelder wie EJECT.
    Zahlen gerundet (`_rounded`), damit der Hash auf Mac und Linux (CI) gleich ist."""
    return hashlib.sha256(json.dumps(_rounded(dict(parts=W.PARTS, assemblies=W.ASSEMBLIES)), sort_keys=True,
                                     ensure_ascii=False).encode()).hexdigest()


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


HAS_MAGICK = __import__('shutil').which('magick') is not None


def _identify(path):
    """(Breite, Bit je Kanal, Kanäle) einer Bilddatei (ImageMagick)."""
    import subprocess
    out = subprocess.run(['magick', 'identify', '-format', '%w %z %[channels]\n', path], capture_output=True, text=True,
                         check=True).stdout.split('\n')[0].split()
    return int(out[0]), int(out[1]), out[2]


def store_texture(tex_dir, name, kind):
    """Eine gebackene Datei `name` (Kanal `kind`) nach TEXTURE_STORE ablegen: verkleinern, Bittiefe, Format. Gibt den neuen Dateinamen
    zurück. Wiederholbar: eine schon abgelegte Datei bleibt unverändert; eine PNG, die als JPG abgelegt wird, entfällt samt .meta."""
    import subprocess
    R = TEXTURE_STORE[kind]
    base, ext = os.path.splitext(name)
    dst = f"{base}.{R['ext']}"
    src = os.path.join(tex_dir, name)
    if ext[1:] == R['ext']:
        w, z, ch = _identify(src)
        if w <= R['size'] and z == 8 and (kind != 'ao' or ch.startswith('gray')):
            return dst
    elif not os.path.exists(src):
        if os.path.exists(os.path.join(tex_dir, dst)):     # schon abgelegt (Datenexport nach der Umstellung)
            return dst
        raise FileNotFoundError(src)
    w = _identify(src)[0]
    cmd = ['magick', src]
    if kind == 'ao':
        cmd += ['-channel', 'R', '-separate', '+channel']       # Graukeil: R = G = B, ohne Farbraumumrechnung (lineare Daten)
    if R['size'] < w:                                            # nie vergrößern (0.43: Atlanten in 2048²)
        lin = kind in ('albedo', 'spec')                         # Farben in linearem Licht verkleinern (Alpha bleibt linear)
        cmd += (['-colorspace', 'RGB'] if lin else []) + ['-filter', 'Lanczos', '-resize', f"{R['size']}x{R['size']}"] + \
            (['-colorspace', 'sRGB'] if lin else [])
    cmd += ['-depth', '8', '-strip']
    cmd += ['-quality', str(R['quality']), '-sampling-factor', '4:4:4'] if R['ext'] == 'jpg' else ['-define', 'png:compression-level=9']
    tmp = os.path.join(tex_dir, f"_tmp_{base}.{R['ext']}")
    subprocess.run(cmd + [tmp], check=True)
    os.replace(tmp, os.path.join(tex_dir, dst))
    if dst != name:
        for f in (src, src + '.meta'):
            if os.path.exists(f):
                os.remove(f)
    return dst


def store_textures(tex, tex_dir):
    """Atlas und Skins einer Waffe (weapons[].textures) nach TEXTURE_STORE ablegen; ergänzt store (Regel) und limit_mb."""
    T = json.loads(json.dumps(tex))
    done = {}

    def put(name, kind):
        if name not in done:
            done[name] = store_texture(tex_dir, name, kind)
        return done[name]
    for k in ('albedo', 'spec', 'normal', 'ao'):
        T['weapon'][k] = put(T['weapon'][k], k)
    for s in T.get('skins', []):
        if not s.get('composed'):                   # 0.42: zusammengesetzte Skins entstehen schon in der Ablage (skin_compose)
            s['albedo'], s['spec'] = put(s['albedo'], 'albedo'), put(s['spec'], 'spec')
    T['store'] = [dict(kind=k, size=TEXTURE_STORE[k]['size'], ext=TEXTURE_STORE[k]['ext'], de=TEXTURE_STORE[k]['de'])
                  for k in ('albedo', 'spec', 'normal', 'ao')]
    T['limit_mb'] = TEXTURE_STORE['limit_mb']
    return T


def formgen_main():
    """--formgen (0.41): Formgen-Varianten (Generated/Formgen/<ID>/) und Rollen im vorhandenen ego.json erneuern, ohne Blender. Nur
    zulässig, wenn BALLONs eigener Teil aktuell ist (sonst voller Export); Pakete selbst bleiben unverändert."""
    p = os.path.join(DST, 'ego.json')
    cur = json.load(open(p, encoding='utf-8'))
    new = json.loads(json.dumps(data(), ensure_ascii=False))
    own_cur = [e for e in cur['weapons'] if 'origin' not in e]
    own_new = [e for e in new['weapons'] if 'origin' not in e]
    stale = [k for k in new if k not in ('weapons', 'roles') and cur.get(k) != new[k]]
    if [e['id'] for e in own_cur] != [e['id'] for e in own_new]:
        stale.append('weapons (Liste)')
    stale += [e['id'] for e, c in zip(own_new, own_cur) if any(c.get(k) != v for k, v in e.items())]
    if stale:
        print('ego.json: BALLONs Teil veraltet (' + ', '.join(stale[:8]) + ') – voller Export (Blender) statt --formgen')
        return 1
    cur['weapons'] = own_cur + [e for e in new['weapons'] if 'origin' in e]
    cur['roles'] = new['roles']
    write_json(p, cur)
    print('ego.json: Formgen-Varianten ' + (', '.join(e['id'] for e in cur['weapons'] if 'origin' in e) or 'keine'))
    return 0


def texture_files(tex):
    """Alle Dateien einer Waffe im Repo (Atlas, gebackene Skins, Skin-Masken; ohne Doppelte und ohne lokal zusammengesetzte Skins)."""
    fs = [tex['weapon'][k] for k in ('albedo', 'spec', 'normal', 'ao')]
    for s in tex.get('skins', []):
        if not s.get('composed'):
            fs += [s['albedo'], s['spec']]
    M = tex.get('skin_masks') or {}
    fs += [M[k] for k in ('a', 'b', 'c', 'p') if k in M]
    return sorted(set(fs))


def store_main():
    """--store-textures: die Atlanten aller Waffen im vorhandenen ego.json nach TEXTURE_STORE ablegen (ohne Blender, ohne Backen)."""
    p = os.path.join(DST, 'ego.json')
    D = json.load(open(p, encoding='utf-8'))
    tex_dir = os.path.join(DST, 'Textures')
    for e in D['weapons']:
        if 'origin' in e:                           # Formgen-Paket (0.41): Ablage macht Formgen (gleiche TEXTURE_STORE), BALLON ändert nichts
            continue
        before = sum(os.path.getsize(os.path.join(tex_dir, f)) for f in texture_files(e['textures']))
        e['textures'] = store_textures(e['textures'], tex_dir)
        after = sum(os.path.getsize(os.path.join(tex_dir, f)) for f in texture_files(e['textures']))
        print(f"{e['id']}: Texturen {before / 1e6:.1f} → {after / 1e6:.1f} MB ({after / before:.2f})")
    write_json(p, D)
    return 0


def entry_tex_dir(e):
    """Texturordner eines Eintrags: Generated/Textures für BALLONs Waffen, Generated/<dir>/textures für Formgen-Pakete (0.41)."""
    return os.path.join(DST, e['dir'], 'textures') if e.get('dir') else os.path.join(DST, 'Textures')


def texture_problems(D, tex_dir=None, store=None):
    """Abweichungen der abgelegten Waffentexturen von TEXTURE_STORE: je Datei (Atlas und Skins) Endung, Kantenlänge, 8 bit (AO ein Kanal),
    Summe je Waffe ≤ limit_mb. tex_dir/store: für tools/test_texture_store.py (sonst je Eintrag entry_tex_dir)."""
    bad = []
    R = store or TEXTURE_STORE
    fixed = tex_dir
    for e in D.get('weapons', []):
        T = e.get('textures')
        if not T:
            continue
        tex_dir = fixed or entry_tex_dir(e)
        files = [(k, T['weapon'][k]) for k in ('albedo', 'spec', 'normal', 'ao')]
        files += [(k, s[k]) for s in T.get('skins', []) for k in ('albedo', 'spec') if not s.get('composed')]
        composed = [(k, s[k]) for s in T.get('skins', []) for k in ('albedo', 'spec') if s.get('composed')]
        if composed and not T.get('skin_masks'):
            bad.append(f"{e['id']}: zusammengesetzte Skins ohne skin_masks (tools/skin_masks.py)")
        M = T.get('skin_masks') or {}
        if M:                                       # Richter 0.42: Pflichtfelder, Rollen und Bildform der Masken
            miss = [k for k in ('a', 'b', 'c', 'p', 'roles') if not M.get(k)]
            if miss:
                bad.append(f"{e['id']}: skin_masks ohne {', '.join(miss)}")
            elif len(M['roles']) > 254:
                bad.append(f"{e['id']}: skin_masks mit {len(M['roles'])} Rollen (8-bit-Index)")
        for k in ('a', 'b', 'c', 'p'):
            if not M.get(k):
                continue
            mp = os.path.join(tex_dir, M[k])
            if not os.path.exists(mp):
                bad.append(f"{e['id']}: fehlt {M[k]}")
            elif HAS_MAGICK:                        # Richter 0.42: a/b/c drei Farbkanäle, p ein Kanal, quadratisch, 8 bit, ohne Alpha
                out = subprocess.run(['magick', 'identify', '-format', '%w %h %z %[channels]\n', mp], capture_output=True, text=True,
                                     check=True).stdout.split('\n')[0].split()
                w, h, z, ch = int(out[0]), int(out[1]), int(out[2]), out[3]
                want = M.get('pattern_size' if k == 'p' else 'size')
                gray = ch.endswith('gray')
                if z != 8 or w != h or (want and w != want) or ch.endswith('a') or gray != (k == 'p'):
                    bad.append(f"{e['id']} skin_masks {M[k]}: {w}×{h} {z} bit {ch} statt {want}² 8 bit "
                               f"{'ein Kanal' if k == 'p' else 'drei Kanäle'} ohne Alpha")
        files += [(k, f) for k, f in composed if os.path.exists(os.path.join(tex_dir, f))]   # lokal (unity_run.py setup), im Repo nicht
        seen = set()
        for k, f in files:
            if f in seen:
                continue
            seen.add(f)
            p = os.path.join(tex_dir, f)
            if not f.endswith('.' + R[k]['ext']):
                bad.append(f"{e['id']} {k} {f} statt .{R[k]['ext']}")
            elif not os.path.exists(p):
                bad.append(f"{e['id']}: fehlt {f}")
            elif HAS_MAGICK:                        # Kantenlänge und Bittiefe brauchen ImageMagick (PR-Check auf Linux ohne: nur Mac)
                w, z, ch = _identify(p)
                half = k == 'albedo' and 2 * w == R[k]['size']   # 0.43: Albedo wahlweise halb so groß (Schalter size von bake_weapon)
                if (w != R[k]['size'] and not half) or z != 8 or (k == 'ao' and not ch.startswith('gray')):
                    bad.append(f"{e['id']} {k} {f}: {w}² {z} bit {ch} statt {R[k]['size']}² 8 bit")
        if any(b.startswith(f"{e['id']}: fehlt") for b in bad):
            continue
        mb = sum(os.path.getsize(os.path.join(tex_dir, f)) for f in seen if os.path.exists(os.path.join(tex_dir, f))) / 1e6   # was das
        # Spiel lädt (Atlas und Skins); die Skin-Masken nutzt nur skin_compose
        if mb > R['limit_mb']:
            bad.append(f"{e['id']}: Texturen {mb:.1f} MB > {R['limit_mb']:g} MB")
    return bad


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
        if e['reference'] and not os.path.exists(os.path.join(DST, e['reference'])):   # Varianten (0.41): ohne Blender-Referenz
            diff.append(e['reference'])
    if any(k not in cur for k in BAKED):
        diff.append('textures/mesh_bounds (Arme)')
    if not HAS_MAGICK:
        print('Hinweis: ImageMagick fehlt – Kantenlänge und Bittiefe der Waffentexturen nur auf dem Mac geprüft (Endung, Vollständigkeit, Grenze hier)')
    tex_bad = texture_problems(cur)
    if tex_bad:
        print('Waffentexturen nicht nach TEXTURE_STORE (' + '; '.join(tex_bad[:6]) + '): python3 tools/export_unity.py --store-textures')
        return 1
    if diff:
        print('ego.json veraltet (' + ', '.join(diff[:8]) + '): Export neu ausführen')
        return 1
    print(f"unity: ego.json aktuell ({len(new['weapons'])} Waffen, davon {sum('origin' in e for e in new['weapons'])} Formgen-Varianten: " +
          ', '.join(f"{e['id']} {len(e['actions'])} Aktionen/{len(e['weapon']['parts'])} Teile" for e in new['weapons']) +
          f"; {len(new['arm']['pieces'])} Armteile)")
    return 0


# ------------------------------------------------------------------ Blender-Teil
REF_OBJECTS = ['magazine', 'charging_handle', 'mag_release']    # dazu die Live-Teile der Waffe (Abzug, Verschluss, Auswurfklappe)
REF_SEGMENTS = ['upper', 'fore', 'hand', 'f0_0', 'f0_2', 'f3_1', 't_0', 't_2']


def reference(sc, e):
    """Blender-Auswertung (tools/ego_build.evaluate) einer Waffe als Testreferenz: Standbilder und Stichproben aller Aktionen."""
    from tools import ego_build as EB
    lv = e['weapon']['live']
    live = [lv[k] for k in ('trigger', 'bolt', 'port', 'ring') if lv.get(k)] + list(lv.get('index', ()))   # 0.34: Schrittteile bewegen sich
    acts = [pid for A in EG.CLASSES[sc.P['type']].get('actions', {}).values() for pid in A.get('mech', {})]   # 0.33: Teile der Klassenaktionen
    objs_ref = list(dict.fromkeys(k for k in REF_OBJECTS + [sc.P['mag']] + live + acts if k in sc.objs))

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
        for k, M in sorted(sc.fx_now.get('links', {}).items()):   # Gurtglieder (0.34) mit der Hülse desselben Schusses
            objs[f'link_{k}'] = flat(M)
        return dict(label=label, action=action, frame=frame, ads_hidden=bool(getattr(sc, 'ads_hidden', False)),   # 0.20: Zielfernrohr
                    objects=[dict(name=k, m=v) for k, v in objs.items()])

    samples = []
    for name in [k for k in ('hip', 'ads', 'reload', 'inspect_r') if k in sc.P['poses']]:   # Standbilder wie ego_build.main
        EB.evaluate(sc, EB.still_action(sc.P, name), 0, {}, {})   # 0.33 P4: wie ego_build.still_action (Bogen: Bogenhand links)
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


# Arme im Waffenatlas (0.41 „Intake“, Formgen-Befund 0.6): bis 0.40 lag beim Backen die ganze Ego-Szene vor – rest_pose setzt alle
# Armsegmente in den Ursprung (Socket_Hand), mitten in den Griff. Deren AO-Abdrücke sind keine Griffhaltung, sondern ein Bake-Fehler, und
# sie liegen auch an Stellen, die in anderen Haltungen frei sind. Regel für beide Wege (BALLON und Formgen): der Waffenatlas wird ohne Arme
# gebacken (arms=False); Kontaktschatten der Hände entstehen im Bild (Cycles-Render, in Unity nicht gebacken). Die Atlanten von BALLONs 16
# Waffen bleiben bis zu ihrem nächsten vollen Bake wie gebacken (export_plan 'reuse'); arms=True backt wie bis 0.40.
ARMS_IN_ATLAS = False
# Atlanten ohne Angabe textures.weapon.arms sind vor 0.41 gebacken, also mit Armen in der Szene (alle 16 Spielwaffen, Stand 0.42): Skin-Masken
# (tools/skin_masks.py) backen sie ebenso, damit der Schmutz in Vertiefungen zum Standard-Atlas passt. Neue Bakes schreiben arms mit.
def atlas_with_arms(e):
    return e['textures']['weapon'].get('arms', True)


def bake_weapon(root, tex_dir, atlas_key, fbx=None, skins=False, gpu=False, arms=ARMS_IN_ATLAS, objs=None, rest=None, size=4096,
                samples=None, settings=None):
    """Atlas einer Waffe (kit.aaa_nodes) und Skins (kit.SKINS: Farbe und Glanz je Skin neu, Normale und AO wie Standard), FBX. Ohne
    Ego-Szene (0.41): root = Wurzelobjekt der Waffe (kit.build), tex_dir/fbx = Zielordner bzw. -datei (fbx None: kein FBX), skins =
    True (alle kit.SKINS), False (nur Standard) oder Liste von Namen, arms = andere Netze der Szene (Arme) beim Backen sichtbar lassen
    (ARMS_IN_ATLAS), objs = {Teil-ID: Objekt} für kit.set_mode (sonst die Kinder von root), rest = Aufruf vor dem FBX-Export (Ego-Szene:
    Ruhelage), size = Albedo (2048 oder 4096, Favoriten; Normale mindestens bake_unity.SETTINGS['normal_size'], AO, Spec bleiben ['data_size']), settings = Abweichungen von
    bake_unity.SETTINGS. Gibt textures (weapon, skins) zurück; Ablage nach TEXTURE_STORE macht store_textures."""
    import bpy
    from tools import bake_unity as BK
    from basic import kit
    wobs = [root] + list(root.children_recursive)
    meshes = [o for o in wobs if o.type == 'MESH']
    objs = objs or {o.name: o for o in wobs if o is not root}
    BK.apply_modifiers(meshes)
    # Leuchtrollen aus dem Modul (Portalkanone PORTAL_ROLES, in kit.MATERIALS erst beim Import des Moduls registriert) gehören wie die
    # übrigen Leucht- und Glasrollen nicht in den Atlas; bake_unity.SKIP_ROLES entstand vorher (0.22, sonst lagen Kern A/B im Atlas)
    BK.SKIP_ROLES |= BK._skip_roles()
    bake = [o for o in meshes if BK.bakeable(o)]
    BK.unwrap(bake)
    hidden = [] if arms else [o for o in bpy.context.scene.objects if o.type == 'MESH' and o not in wobs and not o.hide_render]
    for o in hidden:                               # ohne Arme: übrige Netze (Ego-Arme) verdecken nichts
        o.hide_render = True
    kw = dict(samples=samples, settings=settings)
    try:
        files = BK.bake_atlas(bake, atlas_key, size, tex_dir, gpu=gpu, **kw)
        atlas = dict(size=size, objects=sorted(o.name for o in bake), arms=bool(arms), **files)
        print(f'[export_unity] {atlas_key}: {len(bake)} Objekte, {size}², Arme {"im" if arms else "nicht im"} Atlas'
              f'{f" ({len(hidden)} Netze ausgeblendet)" if hidden else ""}', flush=True)
        out = [dict(name='standard', de=kit.SKINS['standard']['de'], kind=kit.SKINS['standard']['kind'],
                    albedo=atlas['albedo'], spec=atlas['spec'])]
        want = [k for k in kit.SKINS if k != 'standard' and (skins is True or (not isinstance(skins, bool) and k in skins))]
        for skin in want:
            kit.SKIN['name'] = skin
            kit.set_mode(objs, 'aaa')
            f = BK.bake_atlas(bake, f'{atlas_key}_{skin}', size, tex_dir, gpu=gpu, color_only=True, **kw)
            out.append(dict(name=skin, de=kit.SKINS[skin]['de'], kind=kit.SKINS[skin]['kind'], **f))
            print(f'[export_unity] {atlas_key}: Skin {skin}', flush=True)
    finally:
        for o in hidden:
            o.hide_render = False
        kit.SKIN['name'] = 'standard'
        kit.set_mode(objs, 'aaa')
    if rest:
        rest()
    if fbx:
        export_fbx(fbx, wobs)
    return dict(weapon=atlas, skins=out)


def bake_arms(sc, tex_dir, gpu):
    """Atlas der Arme (Segmente zum Backen auseinandergelegt, sonst sehen Abrieb und AO Finger, Handfläche und Handrücken ineinander),
    arms.fbx. Gibt die Atlasdaten zurück."""
    import bpy
    from mathutils import Matrix
    from tools import bake_unity as BK
    aobs = [o for s in ('R', 'L') for e in sc.arms[s][0].values() for o in [e] + list(e.children)]
    meshes = [o for o in aobs if o.type == 'MESH']
    BK.apply_modifiers(meshes)
    # Leuchtrollen aus dem Modul (Portalkanone PORTAL_ROLES, in kit.MATERIALS erst beim Import des Moduls registriert) gehören wie die
    # übrigen Leucht- und Glasrollen nicht in den Atlas; bake_unity.SKIP_ROLES entstand vorher (0.22, sonst lagen Kern A/B im Atlas)
    BK.SKIP_ROLES |= BK._skip_roles()
    bake = [o for o in meshes if BK.bakeable(o)]
    BK.unwrap(bake)
    for si, s in enumerate(('R', 'L')):
        for i, e in enumerate(sc.arms[s][0].values()):
            e.matrix_world = Matrix.Translation((i * 0.5, si * 1.0, 0.0))
    bpy.context.view_layer.update()
    files = BK.bake_atlas(bake, 'arms', 2048, tex_dir, gpu=gpu, join_all=True, settings=dict(normal_size=2048))
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
            e['textures'] = bake_weapon(sc.root, tex_dir, e['atlas'], fbx=os.path.join(DST, e['weapon']['fbx']), skins=False,
                                        gpu=gpu, objs=sc.objs, rest=lambda: rest_pose(sc))
            e['mesh_bounds'] = dict(de='Netzgrenzen je Objekt im eigenen Objektraum (Blender, m, Modifikatoren angewandt)',
                                    objects=[b for k, b in mesh_bounds().items() if k in ids])
            tri = sum(b['tris'] for b in e['mesh_bounds']['objects'])
            print(f"[export_unity] {e['id']}: {len(e['mesh_bounds']['objects'])} Netze ({tri} Dreiecke) → {e['weapon']['fbx']}", flush=True)
        e['textures']['skins'] = skin_entries(e['atlas'], e['textures']['weapon'])   # 0.42: alle Skins, zusammengesetzt aus Masken
        if how != 'reuse':
            e['textures'].pop('skin_masks', None)                 # neue UVs: Masken neu (unten, nach dem FBX)
        e['textures'] = store_textures(e['textures'], tex_dir)      # 0.20: Ablage je Kanal (97 A), auch für übernommene Atlanten
        if i == 0 and arms_new:                # Arme sind für alle Waffen gleich: einmal in der Szene der ersten Waffe
            shared_tex = dict(de='Gebackene Atlanten (kit.aaa_nodes, Skin standard) und AgX-LUT; nicht gebacken: Glas, Leuchtteile',
                              arms=bake_arms(sc, tex_dir, gpu), lut=BK.agx_lut(os.path.join(tex_dir, 'agx_lut.png')))
            arm_bounds = dict(de='Netzgrenzen der Armteile im eigenen Objektraum (Blender, m, Modifikatoren angewandt)',
                              objects=[b for k, b in mesh_bounds().items() if k not in ids])
    D['textures'], D['mesh_bounds'] = shared_tex, arm_bounds
    write_json(os.path.join(DST, 'ego.json'), D)
    from tools import skin_masks as SM                     # 0.42: Masken für neu gebackene Atlanten (UVs aus dem gerade geschriebenen FBX)
    for m, e in zip(WEAPONS, D['weapons']):
        if 'skin_masks' not in e['textures']:
            e['textures']['skin_masks'] = SM.masks_for(m, e, tex_dir, gpu, arms=atlas_with_arms(e))
            write_json(os.path.join(DST, 'ego.json'), D)
    for f in ('ego_reference.json', 'ego_reference.json.meta'):      # bis 0.17 eine Referenz für die Pilotwaffe
        if os.path.exists(os.path.join(DST, f)):
            os.remove(os.path.join(DST, f))
    print(f"[export_unity] ego.json {FORMAT}: " + ', '.join(f"{e['id']} {plan.get(e['id'], 'Formgen-Paket')}" for e in D['weapons']) +
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
        sys.exit(check() if '--check' in sys.argv else store_main() if '--store-textures' in sys.argv else
                 formgen_main() if '--formgen' in sys.argv else (print(__doc__) or 0))
