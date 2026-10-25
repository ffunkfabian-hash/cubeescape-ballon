"""Ego-Ansicht der BASIC-Waffen: Kamera, Haltungen, Handgriffe, Aktionen (reines Python, Datenquelle für tools/ego_build.py).

Getrennt von Toolgen/Cube Escape (Nutzer 24.10.2026). Kameraraum = Blender-Welt: Kamera im Ursprung, Blick −Y, oben +Z,
rechts −X (wie Toolgen `ego_arms.bind`). Meter, 30 fps. Herkunft je Wert im Kommentar:
  T = Startwert aus Toolgen (`data/viewmodels.json`, `data/ego_arms.json`), M = gemessen an Destiny 2 (docs/quellen.md › Q-REF),
  E = entworfen (hier eingestellt, am Bild geprüft).
"""
import math

FPS = 30
CAMERA = dict(h_fov_deg=75.0, aspect=(16, 9), near_m=0.03)          # T: viewmodels.camera

# Haltungen der Waffe: Lage von Socket_Hand im Kameraraum, Zielpunkt der Laufachse, Rollwinkel um die Laufachse.
# 'ads' wird über Socket_Eye gesetzt (Auge auf der Kameraachse).
POSES = {
    'hip':       dict(pos=(-0.20, -0.42, -0.165), aim=(0.02, -3.0, 0.10), roll=6,
                      src='E (Destiny-Hüfte: Griff unten rechts, Lauf zur Bildmitte); Toolgen-Hüfte (−0,21/−0,537/−0,176) als Start'),
    'ads':       dict(eye=(0.0, 0.0, 0.0), aim_dir=(0, -1, 0), roll=0,
                      src='Visier-Standard v2: Socket_Eye ist der Augenpunkt, liegt in der Kamera; Waffenmodell ungezoomt, Welt zoomt je Klasse'),
    'sprint':    dict(pos=(-0.10, -0.34, -0.23), aim=(1.2, -1.6, -0.55), roll=-35, src='E nach Destiny-Sprint (quer, gesenkt)'),
    'lowered':   dict(pos=(-0.17, -0.38, -0.25), aim=(0.4, -2.0, -1.2), roll=10, src='E'),
    'crouch':    dict(pos=(-0.19, -0.41, -0.18), aim=(0.02, -3.0, 0.05), roll=9, src='E'),
    'air':       dict(pos=(-0.20, -0.42, -0.15), aim=(0.02, -3.0, 0.17), roll=4, src='E'),
    'holstered': dict(pos=(-0.24, -0.25, -0.62), aim=(0.5, -1.2, -1.8), roll=30, src='E (unter dem Bild)'),
    'reload':    dict(pos=(-0.07, -0.34, -0.135), aim=(0.75, -2.1, 0.45), roll=-40,
                      src='T Reload roll −20/pitch 12, für Destiny-Anmutung verstärkt (E)'),
    'inspect_l': dict(pos=(-0.06, -0.36, -0.16), aim=(1.6, -1.0, 0.15), roll=-8, src='E (Ego-Seite zeigt zur Kamera)'),
    'inspect_r': dict(pos=(-0.10, -0.36, -0.12), aim=(0.1, -1.0, 0.9), roll=-110, src='E (Oberseite und rechte Seite)'),
}

# Handgriffe an der Pilotwaffe (Autorenmaß der Waffe: f vorn, u oben, x links, mm). contact = Mitte der Handfläche auf der
# Oberfläche, palm = Richtung von der Handfläche in das Bauteil, fingers = Richtung der Finger. part = Bauteil, an dem der Griff
# hängt (bewegt sich mit), sonst Waffe.
GRIPS = {
    'grip':    dict(contact=(-3, -6, -16.5), palm=(0.15, 0.0, 1.0), fingers=(1.0, -0.06, 0.0), fingers_pose='trigger',
                    src='E am Griff BGM-1 (Toolgen-Griffrichtung als Start)'),
    'support': dict(contact=(278, 61.5, -2), palm=(0.0, 1.0, -0.25), fingers=(0.08, 0.15, -1.0), fingers_pose='underhand',
                    src='E unter dem Handschutz (Toolgen: underhand)'),
    'mag':     dict(part='magazine', contact=(114, -18, 13.5), palm=(0.0, 0.0, -1.0), fingers=(1.0, 0.45, 0.0), fingers_pose='mag_hold',
                    src='E seitlich am Magazin, Hand greift von unten hinten (Toolgen: mag_hold)'),
    'charge':  dict(part='charging_handle', contact=(-84, 112, 30), palm=(0.0, 0.0, -1.0), fingers=(0.45, 0.9, 0.0),
                    fingers_pose='pinch', src='E am Ladehebel links (Toolgen: pinch)'),
}

# Aktionen. Kanäle: weapon (Haltung oder (Haltung, Versatz)), L/R (Griff, ('cam', Punkt) oder (Griff, Versatz mm in Waffenachsen)),
# fL/fR (Fingerstellung), mech (Bauteilbewegung 0..1 wie in den Waffenmodulen), carry (Magazin folgt der linken Hand), fire (Bilder
# der Schüsse), events (Marker). Zwischen Schlüsseln wird geglättet (Ease In/Out).
OFF_L = ('cam', (0.30, -0.25, -0.62))      # linke Hand unter dem Bild (Magazin holen)
ACTIONS = {
    'idle_hip': dict(de='Ruhe an der Hüfte (Atmen)', frames=60, weapon=[(0, 'hip'), (60, 'hip')], breathe=True,
                     events=[], src='E'),
    'draw': dict(de='Ziehen', frames=20, weapon=[(0, 'holstered'), (14, 'hip'), (20, 'hip')],
                 L=[(0, OFF_L), (6, OFF_L), (13, 'support'), (20, 'support')], fL=[(0, 'relaxed'), (11, 'open'), (14, 'underhand')],
                 events=[(14, 'Ready')], src='M Ziehen 0,23 s bis Hüfte (Auto Rifle, Q-REF) + Ausfedern E'),
    'holster': dict(de='Wegstecken', frames=14, weapon=[(0, 'hip'), (12, 'holstered'), (14, 'holstered')],
                    L=[(0, 'support'), (2, 'support'), (8, OFF_L)], fL=[(0, 'underhand'), (3, 'open'), (10, 'relaxed')],
                    events=[(2, 'HandOff'), (12, 'Holstered')], src='E (CE: Holster ab aktueller Stellung)'),
    'aim_in': dict(de='Hüfte → Zielen', frames=10, weapon=[(0, 'hip'), (9, 'ads'), (10, 'ads')], events=[(9, 'Aimed')],
                   src='E 0,30 s (CE-Handling Auto 0,39→0,20 s)'),
    'aim_out': dict(de='Zielen → Hüfte', frames=8, weapon=[(0, 'ads'), (8, 'hip')], events=[(8, 'Ready')], src='E'),
    'fire_hip': dict(de='Dauerfeuer aus der Hüfte', frames=32, weapon=[(0, 'hip'), (32, 'hip')], fire=list(range(2, 26, 2)) + [25],
                     kick=1.0, events=[(2, 'Fire')], src='M 720/min ≈ 1 Schuss je 2,5 Bilder (Q-REF); Rückstoß T 17,5 mm/3°'),
    'fire_ads': dict(de='Dauerfeuer im Zielen', frames=32, weapon=[(0, 'ads'), (32, 'ads')], fire=list(range(2, 26, 2)) + [25],
                     kick=0.45, events=[(2, 'AimFire')], src='M Kadenz wie fire_hip; Rückstoß im Zielen gedämpft E'),
    'reload_tactical': dict(
        de='Nachladen mit Restmunition', frames=50,
        weapon=[(0, 'hip'), (3, ('hip', dict(roll=-3, up=-0.004))), (10, 'reload'), (16, ('reload', dict(roll=-3))),
                (26, ('reload', dict(up=-0.004, pitch=1.5))), (30, ('reload', dict(up=0.009, pitch=-2.5, roll=4))), (33, 'reload'),
                (37, ('reload', dict(roll=8, up=0.006))), (45, ('hip', dict(roll=-2, up=-0.003))), (50, 'hip')],
        L=[(0, 'support'), (4, 'support'), (8, 'mag'), (13, ('mag', (8, -70, 25))), (19, OFF_L), (21, OFF_L),
           (26, ('mag', (6, -55, 20))), (29, 'mag'), (31, 'mag'), (38, 'support'), (50, 'support')],
        fL=[(0, 'underhand'), (5, 'open'), (8, 'mag_hold'), (30, 'mag_hold'), (33, 'open'), (38, 'underhand')],
        carry=[(8, 29)], mech={'mag_release': [(0, 0), (6, 1), (10, 0)]},
        events=[(4, 'HandOff'), (10, 'MagOut'), (29, 'MagIn'), (38, 'HandOn'), (46, 'Ready')],
        src='M MagIn ≈ 0,93 s; Ablauf T (Reload-Keys) mit Destiny-Kippen E; v2: Ausholen, Stoß bei MagIn, Nachfedern E'),
    'reload_empty': dict(
        de='Nachladen aus leerem Zustand', frames=60,
        weapon=[(0, 'hip'), (3, ('hip', dict(roll=-3, up=-0.004))), (9, 'reload'), (15, ('reload', dict(roll=-3))),
                (25, ('reload', dict(up=-0.004, pitch=1.5))), (29, ('reload', dict(up=0.010, pitch=-3, roll=4))), (32, 'reload'),
                (35, ('reload', dict(roll=12, yaw=-7))), (39, ('reload', dict(roll=15, yaw=-8, back=0.010))),
                (41, ('reload', dict(roll=10, yaw=-5, up=0.010, pitch=-2))), (45, ('reload', dict(roll=9))),
                (54, ('hip', dict(roll=-2, up=-0.003))), (60, 'hip')],
        L=[(0, 'support'), (4, 'support'), (10, OFF_L), (16, OFF_L), (24, ('mag', (6, -55, 20))), (28, 'mag'), (30, 'mag'),
           (35, 'charge'), (38, ('charge', (-58, 0, 0))), (40, ('charge', (-58, 0, 0))), (42, 'charge'),
           (48, 'support'), (60, 'support')],
        fL=[(0, 'underhand'), (5, 'open'), (14, 'mag_hold'), (30, 'mag_hold'), (32, 'open'), (35, 'pinch'), (42, 'pinch'),
            (44, 'open'), (48, 'underhand')],
        drop=(6, 15), carry=[(16, 28)], mech={'mag_release': [(0, 0), (5, 1), (9, 0)],
                                             'charging_handle': [(0, 0), (35, 0), (38, 1), (40, 1), (42, 0)]},
        events=[(5, 'HandOff'), (8, 'MagOut'), (28, 'MagIn'), (40, 'Chamber'), (48, 'HandOn'), (56, 'Ready')],
        src='M leer 1,85 s, MagOut 0,25 s, MagIn 0,93 s (Q-REF Auto Rifle); Ladehebel E; v2: Ausholen, Stoß bei MagIn, '
            'Ruck beim Durchladen, Nachfedern E'),
    'inspect': dict(de='Betrachten', frames=96,
                    weapon=[(0, 'hip'), (16, 'inspect_l'), (44, ('inspect_l', dict(roll=-6, yaw=4))), (60, 'inspect_r'),
                            (80, ('inspect_r', dict(roll=8))), (94, 'hip'), (96, 'hip')],
                    L=[(0, 'support'), (40, 'support'), (48, OFF_L), (84, OFF_L), (94, 'support'), (96, 'support')],
                    fL=[(0, 'underhand'), (42, 'open'), (50, 'relaxed'), (86, 'open'), (94, 'underhand')],
                    events=[(16, 'Start'), (94, 'End')], src='E nach Destiny-Inspektion (Ego-Seite, dann Oberseite)'),
    'sprint': dict(de='Sprint: Beginn, Schleife, Ende', frames=48, weapon=[(0, 'hip'), (8, 'sprint'), (38, 'sprint'), (48, 'hip')],
                   bob=dict(start=8, end=38, period=20, amp=(0.012, 0.010), roll=4), events=[(8, 'SprintLoop'), (48, 'Ready')],
                   src='E (CE: Waffe senkt sich und rollt zur Mitte); period = Doppelschritt (seitlich), vertikal je Schritt: '
                       '20 Bilder = 0,67 s → 3 Schritte/s bei 6,8 m/s (Schritt ≈ 2,3 m). 0.10: vorher 10 = 6 Schritte/s („tapsig“)'),
    'lowered': dict(de='Gesenkte Haltung / Wandnähe', frames=36, weapon=[(0, 'hip'), (8, 'lowered'), (26, 'lowered'), (36, 'hip')],
                    events=[(8, 'Lowered'), (36, 'Ready')], src='E'),
    'walk': dict(de='Gehen (liegende Acht)', frames=48, weapon=[(0, 'hip'), (48, 'hip')],
                 bob=dict(start=0, end=48, period=24, amp=(0.007, 0.004), roll=1.2), events=[], src='E (CE: liegende Acht)'),
    'crouch': dict(de='Ducken', frames=24, weapon=[(0, 'hip'), (8, 'crouch'), (24, 'crouch')], events=[(8, 'Crouched')], src='E'),
    'jump_land': dict(de='Sprung, Luftphase, Landung', frames=40,
                      weapon=[(0, 'hip'), (8, 'air'), (26, 'air'), (30, ('hip', dict(up=-0.022, pitch=-3))), (40, 'hip')],
                      events=[(8, 'Air'), (28, 'Land')], src='E (CE: Anheben, Landefeder)'),
    'sprint_to_aim': dict(de='Sprint → Zielen', frames=18, weapon=[(0, 'sprint'), (12, 'ads'), (18, 'ads')],
                          events=[(0, 'SprintOut'), (12, 'Aimed')], src='E (CE: ADS > Sprint)'),
    'sprint_to_fire': dict(de='Sprint → Feuer', frames=26, weapon=[(0, 'sprint'), (6, 'hip'), (26, 'hip')],
                           fire=list(range(7, 22, 2)), kick=1.0, events=[(0, 'SprintOut'), (7, 'Fire')], src='E (CE: Fire > Sprint)'),
    'draw_aim': dict(de='Ziehen bei gehaltenem Zielen', frames=28,
                     weapon=[(0, 'holstered'), (14, 'hip'), (24, 'ads'), (28, 'ads')],
                     L=[(0, OFF_L), (6, OFF_L), (13, 'support'), (28, 'support')], fL=[(0, 'relaxed'), (11, 'open'), (14, 'underhand')],
                     events=[(14, 'Ready'), (24, 'Aimed')], src='E (CE: Draw nicht unterbrechbar, ADS danach)'),
    'reload_to_switch': dict(de='Nachladen → Waffenwechsel (Abbruch)', frames=30,
                             weapon=[(0, 'hip'), (9, 'reload'), (14, 'reload'), (28, 'holstered'), (30, 'holstered')],
                             L=[(0, 'support'), (4, 'support'), (8, 'mag'), (14, 'mag'), (22, OFF_L)],
                             fL=[(0, 'underhand'), (5, 'open'), (8, 'mag_hold'), (16, 'open')],
                             events=[(4, 'HandOff'), (14, 'Cancel'), (28, 'Holstered')],
                             src='E (CE: Reload bricht bei Wechsel ab, Holster ab aktueller Stellung)'),
}

# Haltungs-/Aktionszeilen der Matrix, die eine Aktion darstellt (für docs/haltungen.md)
# ------------------------------------------------------------------ Bewegungsgefühl (v2, 24.10.2026; Nutzer: „zu schnell, rappelig,
# abgehackt, statisch“). Alle Werte entworfen; Unity übernimmt sie über den Export.
TIME_SCALE = 1.25        # Ablauftempo: 25 % langsamer als die Destiny-Messung (lesbar ohne Ton/Bewegungsunschärfe)
KEEP_TIME = {'fire_hip', 'fire_ads', 'aim_in', 'aim_out', 'sprint_to_aim', 'sprint_to_fire'}   # Spielgefühl: Zielen/Feuern bleiben schnell
INTERP = 'hermite_monotone'   # Kurven durch die Schlüssel (Tangente aus den Nachbarn, 0 bei Halt/Umkehr) statt Stopp an jedem Schlüssel
SECONDARY = dict(freq_hz=3.2, zeta=0.55,    # Waffe folgt ihrer Kurve über eine gedämpfte Feder: Trägheit und leichtes Nachschwingen
                 aim_freq_hz=10.0, aim_zeta=1.0)  # Aktionen, die im Zielen enden: schneller und kritisch gedämpft, das Visier landet
                                                  # ohne Überschwingen und ohne Nachhängen (0.10; 3,2 Hz kritisch hing 10° hinterher)


def ends_in_ads(A):
    """Endet die Aktion in der Haltung 'ads' (aim_in, sprint_to_aim, draw_aim, fire_ads …)? Dann gilt SECONDARY['aim_zeta']."""
    k = A['weapon'][-1][1]
    return (k[0] if isinstance(k, tuple) else k) == 'ads'
BREATHE_ALL = dict(period_s=3.4, up_m=0.0010, pitch_deg=0.15)   # dezentes Atmen in jeder Aktion
RECOIL = dict(freq_hz=5.0, zeta=0.5, back_mps=0.62, pitch_dps=115.0, climb_deg=0.12,    # Rückstoß als Federimpuls je Schuss
              cam_freq_hz=4.0, cam_zeta=0.6, cam_dps=18.0)


def _retime(A, k):
    """Alle Bildangaben einer Aktion um k strecken (Feueraktionen bleiben in Originalkadenz)."""
    def keys(v):
        return [(f * k, x) for f, x in v]
    for ch in ('weapon', 'L', 'R', 'fL', 'fR'):
        if ch in A:
            A[ch] = keys(A[ch])
    if 'events' in A:                        # Marker liegen auf ganzen Bildern
        A['events'] = [(int(round(f * k)), n) for f, n in A['events']]
    if 'mech' in A:
        A['mech'] = {pid: keys(v) for pid, v in A['mech'].items()}
    if 'carry' in A:
        A['carry'] = [(a * k, b * k) for a, b in A['carry']]
    if 'drop' in A:
        A['drop'] = (A['drop'][0] * k, A['drop'][1] * k)
    if 'bob' in A:
        A['bob'] = dict(A['bob'], start=A['bob']['start'] * k, end=A['bob']['end'] * k)
    A['frames'] = int(math.ceil(A['frames'] * k - 1e-9))
    A['time_scale'] = k


for _n, _a in ACTIONS.items():
    _retime(_a, 1.0 if _n in KEEP_TIME else TIME_SCALE)


ROWS = {
    'idle_hip': ['pose_rest', 'pose_hip'], 'draw': ['draw', 'ready'], 'holster': ['holster'], 'aim_in': ['pose_aim', 'tr_hip_aim'],
    'aim_out': ['tr_aim_hip'], 'fire_hip': ['fire_auto', 'recoil_mech', 'recoil_camera'], 'fire_ads': ['fire_auto'],
    'reload_tactical': ['reload_partial', 'reload_feed'], 'reload_empty': ['reload_empty', 'cycle'], 'inspect': ['inspect', 'inspect_return'],
    'sprint': ['sprint_in', 'sprint_loop', 'sprint_out'], 'lowered': ['pose_lowered', 'tr_lowered_return'], 'walk': ['move_walk', 'sway'],
    'crouch': ['crouch'], 'jump_land': ['jump_start', 'air', 'land'], 'sprint_to_aim': ['tr_sprint_aim'],
    'sprint_to_fire': ['tr_sprint_fire'], 'draw_aim': ['tr_draw_aimheld'], 'reload_to_switch': ['tr_reload_switch', 'switch'],
}
