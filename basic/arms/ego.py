"""Ego-Ansicht der BASIC-Waffen: Kamera, Haltungen, Handgriffe, Aktionen (reines Python, Datenquelle für tools/ego_build.py).

Getrennt von Toolgen/Cube Escape (Nutzer 24.10.2026). Kameraraum = Blender-Welt: Kamera im Ursprung, Blick −Y, oben +Z,
rechts −X (wie Toolgen `ego_arms.bind`). Meter, 30 fps. Herkunft je Wert im Kommentar:
  T = Startwert aus Toolgen (`data/viewmodels.json`, `data/ego_arms.json`), M = gemessen an Destiny 2 (docs/quellen.md › Q-REF),
  E = entworfen (hier eingestellt, am Bild geprüft).
"""
import copy
import math

from basic.arms import robot_arm as RA

FPS = 30
CAMERA = dict(h_fov_deg=75.0, aspect=(16, 9), near_m=0.03)          # T: viewmodels.camera

# Haltungen der Waffe: Lage von Socket_Hand im Kameraraum, Zielpunkt der Laufachse, Rollwinkel um die Laufachse.
# 'ads' wird über Socket_Eye gesetzt (Auge auf der Kameraachse).
POSES = {
    'hip':       dict(pos=(-0.19, -0.42, -0.23), aim=(0.02, -3.0, -0.20), roll=6,
                      src='M Destiny-Hüfte: Mündung x 54–59 / y 60–71 % (Motiongen huefte › 4, Entscheidungsliste 2.1 A), Lage E; '
                          '0.15: Mündung x 58,8 / y 49,6 → x 58,2 / y 63,2 % (6,5 cm tiefer, Lauf zur Bildmitte); Toolgen-Hüfte als Start'),
    'ads':       dict(eye=(0.0, 0.0, 0.0), aim_dir=(0, -1, 0), roll=0,
                      src='Visier-Standard v2: Socket_Eye ist der Augenpunkt, liegt in der Kamera; Waffenmodell ungezoomt, Welt zoomt je Klasse'),
    'sprint':    dict(pos=(-0.10, -0.34, -0.23), aim=(1.2, -1.6, -0.55), roll=-35, src='E nach Destiny-Sprint (quer, gesenkt)'),
    'lowered':   dict(pos=(-0.17, -0.38, -0.25), aim=(0.4, -2.0, -1.2), roll=10, src='E'),
    'crouch':    dict(pos=(-0.18, -0.41, -0.245), aim=(0.02, -3.0, -0.25), roll=9, src='E (wie hip versetzt, 0.15 mit hip gesenkt)'),
    'air':       dict(pos=(-0.19, -0.42, -0.215), aim=(0.02, -3.0, -0.13), roll=4, src='E (wie hip versetzt, 0.15 mit hip gesenkt)'),
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

# Fingerstellungen der Ego-Griffe: die des Rigs (robot_arm.FINGER_POSES) und weitere je Griff. Sie stehen hier, weil sie Bewegung sind,
# keine Form (robot_arm.py liegt im Formquellen-Hash des Exports). foregrip (0.18): Faust um einen senkrechten Vordergriff direkt unter
# dem Vorbau, Daumen eingerollt hinter den Griff (Nutzer 26.10.2026: „Der Daumen bei der MP sitzt irgendwie ungünstig“ – mit underhand
# stand er 12–15 mm über dem Vorbau; von drei Proben wählte der Nutzer diese: „Oben links ist am besten“).
# foregrip_open: Finger offen, Daumen bleibt eingerollt – ein gestreckter Daumen (open) zeigt bei dieser Handstellung in den Vorbau.
FINGER_POSES = dict(RA.FINGER_POSES, foregrip=dict(f=[[62, 74, 48]] * 4, t=[80, 5, 60]),
                    foregrip_open=dict(f=[[4, 4, 3]] * 4, t=[80, 5, 60]))

# Aktionen. Kanäle: weapon (Haltung oder (Haltung, Versatz)), L/R (Griff, ('cam', Punkt) oder (Griff, Versatz mm in Waffenachsen)),
# fL/fR (Fingerstellung), mech (Bauteilbewegung 0..1 wie in den Waffenmodulen), carry (Magazin folgt der linken Hand), fire (Bilder
# der Schüsse), events (Marker). Zwischen Schlüsseln wird geglättet (Ease In/Out).
OFF_L = ('cam', (0.30, -0.25, -0.62))      # linke Hand unter dem Bild (Magazin holen)


def shots_720(first, n):
    """Schussbilder bei 720/min und 30 fps: alle 2,5 Bilder, also abwechselnd 2 und 3 Bilder Abstand (Unity: gameplay.rpm)."""
    return [first + int(2.5 * k) for k in range(n)]


def shots_at(first, last, rpm):
    """Schussbilder bei rpm und 30 fps von `first` bis höchstens `last` (0.20: Klassen mit eigener Kadenz, ego.profile); 720/min ergibt
    dieselben Bilder wie shots_720."""
    step, out = 60.0 * FPS / rpm, []
    while first + int(step * len(out) + 1e-9) <= last:
        out.append(first + int(step * len(out) + 1e-9))
    return out


def trigger_on(fire, f, semi=False):
    """Abzug gezogen im Bild f einer Feueraktion: Dauerfeuer vom Bild vor dem ersten bis nach dem letzten Schuss; Einzelfeuer (0.20,
    Feuerart semi_auto) je Schuss ein Bild davor bis ein Bild danach, dazwischen losgelassen (ein Schuss je Zug)."""
    if not fire:
        return False
    if semi:
        return any(s - 1 <= f <= s + 1 for s in fire)
    return fire[0] - 1 <= f <= fire[-1] + 1

ACTIONS = {
    'idle_hip': dict(de='Ruhe an der Hüfte (Atmen)', frames=60, weapon=[(0, 'hip'), (60, 'hip')], breathe=True,
                     events=[], src='E'),
    'draw': dict(de='Ziehen', frames=20, weapon=[(0, 'holstered'), (14, 'hip'), (20, 'hip')],
                 L=[(0, OFF_L), (6, OFF_L), (13, 'support'), (20, 'support')], fL=[(0, 'relaxed'), (11, 'open'), (14, 'underhand')],
                 events=[(14, 'Ready')], src='M Ziehen 0,23 s bis Hüfte (Auto Rifle, Q-REF) + Ausfedern E'),
    'holster': dict(de='Wegstecken', frames=8, weapon=[(0, 'hip'), (7.5, 'holstered'), (8, 'holstered')],
                    L=[(0, 'support'), (1, 'support'), (5, OFF_L)], fL=[(0, 'underhand'), (2, 'open'), (6, 'relaxed')],
                    events=[(1, 'HandOff'), (8, 'Holstered')],
                    src='M Destiny-Wechsel: Wegstecken 0,08–0,27 s (Motiongen wechsel › 4, Entscheidungsliste 6.1 A) → 0,27 s ohne '
                        'TIME_SCALE (bis 0.14: 0,60 s); Ablauf E (CE: Holster ab aktueller Stellung)'),
    'aim_in': dict(de='Hüfte → Zielen', frames=10, weapon=[(0, 'hip'), (9, 'ads'), (10, 'ads')], events=[(9, 'Aimed')],
                   src='E 0,30 s (CE-Handling Auto 0,39→0,20 s)'),
    'aim_out': dict(de='Zielen → Hüfte', frames=8, weapon=[(0, 'ads'), (8, 'hip')], events=[(8, 'Ready')], src='E'),
    'fire_hip': dict(de='Dauerfeuer aus der Hüfte', frames=32, weapon=[(0, 'hip'), (32, 'hip')], fire=shots_720(2, 10),
                     kick=1.0, events=[(2, 'Fire')],
                     src='M 720/min = 1 Schuss je 2,5 Bilder (Q-REF; bis 0.14 alle 2 Bilder ≈ 940/min); Rückstoß T 17,5 mm/3°'),
    'fire_ads': dict(de='Dauerfeuer im Zielen', frames=32, weapon=[(0, 'ads'), (32, 'ads')], fire=shots_720(2, 10),
                     kick=1.0, events=[(2, 'AimFire')],
                     src='M Kadenz wie fire_hip; Rückstoß im Zielen nach RECOIL ads_* (5.1 A: Visier steht, die Welt wandert) E'),
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
                    events=[(16, 'Start'), (94, 'End')], src='E nach Apex/CoD-Muster (Ego-Seite, dann Oberseite); Destiny hat keinen Ego-Inspect'),
    'sprint': dict(de='Sprint: Beginn, Schleife, Ende', frames=48, weapon=[(0, 'hip'), (8, 'sprint'), (38, 'sprint'), (48, 'hip')],
                   bob=dict(start=8, end=38, period=19, amp=(0.022, 0.018), roll=3.5, shape='u'), events=[(8, 'SprintLoop'), (48, 'Ready')],
                   src='E (CE: Waffe senkt sich und rollt zur Mitte); period = Doppelschritt (seitlich), vertikal je Schritt: '
                       '19 Bilder = 0,633 s → 3,16 Schritte/s, seitlich 1,58 Hz, Rollen ±3,5°, U-Bogen (oben an den Seitenumkehren) '
                       'nach Motiongen REF 0.23 (Destiny 2, Automatik/Handfeuerwaffe gemessen). 0.9: 10 Bilder = 6 Schritte/s („tapsig“). '
                       '0.15: Hub 12/10 → 22/18 mm (seitlich/vertikal) für ≈ 10 % H / 13 % B im Bild wie die Destiny-Automatik '
                       '(Entscheidungsliste 3.1 A, gemessen wie in Schritt 2: Oberkante, linke Kante)'),
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
                           fire=shots_720(7, 6), kick=1.0, events=[(0, 'SprintOut'), (7, 'Fire')], src='E (CE: Fire > Sprint)'),
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
KEEP_TIME = {'fire_hip', 'fire_ads', 'aim_in', 'aim_out', 'sprint_to_aim', 'sprint_to_fire',   # Spielgefühl: Zielen/Feuern bleiben schnell
             'holster'}                                    # Wechsel straff wie Destiny (6.1 A); das Ziehen bleibt gestreckt
INTERP = 'hermite_monotone'   # Kurven durch die Schlüssel (Tangente aus den Nachbarn, 0 bei Halt/Umkehr) statt Stopp an jedem Schlüssel
SECONDARY = dict(freq_hz=3.2, zeta=0.55,    # Waffe folgt ihrer Kurve über eine gedämpfte Feder: Trägheit und leichtes Nachschwingen
                 aim_freq_hz=10.0, aim_zeta=1.0)  # Aktionen, die im Zielen enden: schneller und kritisch gedämpft, das Visier landet
                                                  # ohne Überschwingen und ohne Nachhängen (0.10; 3,2 Hz kritisch hing 10° hinterher)


def ends_in_ads(A):
    """Endet die Aktion in der Haltung 'ads' (aim_in, sprint_to_aim, draw_aim, fire_ads …)? Dann gilt SECONDARY['aim_zeta']."""
    k = A['weapon'][-1][1]
    return (k[0] if isinstance(k, tuple) else k) == 'ads'
BREATHE_ALL = dict(period_s=3.4, up_m=0.0010, pitch_deg=0.15)   # dezentes Atmen in jeder Aktion
# Rückstoß (0.15, Entscheidungsliste 5.1 A und 5.2 A): vier getrennte Größen – Grundbahn, Kamera, Modellkick, Streuung.
# Destiny (Motiongen rueckstoss › 2/4, zielbewegung › 6b): Automatik steigt als Säule ≈ 1 % H je Schuss mit ≤ 2,5 % B Seitenwackeln,
# dreimal dieselbe Form; im Zielen wandert die Welt (Viererstoß ≈ 4 % H), das Holo-Visier bleibt < 1 % H; Rückkehr 0,4–0,6 s ohne
# Unterschwingen.
RECOIL = dict(
    # Modellkick: Federimpuls je Schuss (Waffe zurück, Mündung hoch), Hüfte; im Zielen mit ads_back/ads_pitch (Visier bleibt
    # < 1 % H) und ohne Hochziehen. Hüftwerte T 17,5 mm/3° (bis 0.14 im Zielen 0,45 für alles: „Visier springt leicht“)
    freq_hz=5.0, zeta=0.5, back_mps=0.62, pitch_dps=115.0, climb_deg=0.12, ads_back=0.45, ads_pitch=0.02,
    # Kamera: kurzer Ruck je Schuss, kritisch gedämpft (bis 0.14 ζ 0,6 mit Unterschwingen). Hüfte: Kamera samt Viewmodel;
    # Zielen: nur die Welt (ads_cam), das Viewmodel bleibt stehen
    cam_freq_hz=4.0, cam_zeta=1.0, cam_dps=18.0, ads_cam=0.45,
    # Grundbahn (fest, lernbar): je Schuss path_up_h der Bildhöhe nach oben, seitlich die feste Folge path_side_b (Lage nach
    # Schuss n in Bildbreite, wiederholt), beides im Bildmaßstab der Welt (im Zielen also kleinerer Winkel); die Kamera folgt der
    # Bahn mit path_hz, Schüsse gehen dorthin
    path_up_h=0.010, path_hz=10.0,
    path_side_b=[0.0, 0.003, 0.006, 0.007, 0.004, 0.0, -0.004, -0.007, -0.008, -0.005, -0.001, 0.003, 0.006, 0.008, 0.006, 0.002,
                 -0.003, -0.006],
    # Salven zweistufig: in der Salve (Abstand ≤ recover_delay_s, mindestens 1,5 Schussabstände) steigt die Bahn ohne Erholung,
    # danach kehrt sie kritisch gedämpft mit recover_hz zurück. burst_shots > 0: Salvenwaffe mit burst_rpm in der Salve
    recover_delay_s=0.12, recover_hz=2.0, burst_shots=0, burst_rpm=0,
    # Streuung um den Zielpunkt (Zufall, getrennt von der Bahn); bis 0.14 als MoveTuning in Unity
    spread_hip_deg=1.1, spread_ads_deg=0.12)
# Zielfernrohr im Zielen (0.20, Visier-Standard 3: eine Kamera, Modell ungezoomt; Entscheidungsliste 1d): Teile mit `ads_hide` (Rohr,
# Okular, Türme, Spannband) sind aus, solange der Augenpunkt Socket_Eye der Grundhaltung (nach dem Feder-Nachlauf, ohne Wippen und
# Rückstoß) näher als eye_m an der Kamera liegt. Vorher wächst das Okular sichtbar heran wie bei Destiny (Scharfschütze: Okular füllt
# das Bild, dann das Linsenbild, Linse erst nach dem Modell); eye_m = Augenabstand des Okularendes (Socket_Eye − Socket_Sight, 30 mm
# beim Scout) plus Nahgrenze der Kamera (30 mm): darunter schnitte die Nahebene das Okular an. Blender (ego_build) und Unity
# (EgoController, EgoSolver) rechnen dieselbe Regel.
ADS_HIDE = dict(eye_m=0.06, src='E: Okular bis an die Nahebene sichtbar (Augenabstand Okularende 30 mm + near 30 mm), danach Linsenbild; '
                                'Destiny-Scharfschütze: Okular füllt das Bild 4 Bilder, Linse nach dem Modell (Motiongen destiny2 › 2, '
                                'Entscheidungsliste 1d)')
# Waffenwechsel (6.1 A): Wegstecken (holster 0,27 s), danach leere Sicht, dann Ziehen wie bisher (draw mit Nachfedern).
# empty_s ist die Pause zwischen Ende von holster und Beginn von draw; die sichtbare leere Sicht ist länger, weil die Waffe schon vor
# dem Ende des Wegsteckens unter dem Bildrand ist und beim Ziehen erst nach einigen Bildern auftaucht.
SWITCH = dict(empty_s=0.03, src='M Destiny-Wechsel: leere Sicht 0,07–0,30 s (Motiongen wechsel › 4); Ziel 0,1–0,2 s (6.1 A), gemessen 0,13 s bei 60/s')
# Mündungsfeuer (0.16, Entscheidungsliste 5.3 A): 1 Bild bei 30/s (in Unity dieselbe Dauer dur_s), kleiner heller Kern längs des Laufs
# und kurze Seitenflammen quer dazu, reine Emission ohne Bloom an Socket_Muzzle. Destiny (Motiongen muendung › 3/6): Blitz 1–2 Bilder
# bei 60/s, im Zielen deckt er bei der Automatik ≈ 20 % der Holo-Öffnung ab; hier höchstens 20 % (./check und Unity-Test messen es).
# Farbe Stil v2.1: Flammen in der Familienfarbe Cyan (Leuchtfunktion), der Kern als einziger Akzent fast weiß. Je Schuss dreht der
# Blitz um die Laufachse nach der festen Folge roll_deg (lebendig, aber in Blender und Unity gleich). Form E, am Bild geprüft.
FLASH = dict(
    dur_s=1.0 / 30,
    core=dict(len_mm=80, r_mm=22, back_mm=4, ring_at=0.3, segs=8, role='flash_core'),
    tongues=dict(n=4, len_mm=80, w_mm=30, t_mm=16, base_mm=10, sweep_deg=28, at=0.35, role='flash_flame'),
    roll_deg=[45, 20, 65, 35, 55, 10],
    roles=dict(flash_core=dict(color='#EAFBFF', emit=3.0, de='Mündungsfeuer Kern (fast weiß, reine Emission)'),
               flash_flame=dict(color='#5FD3E0', emit=0.8, de='Mündungsfeuer Seitenflammen (Familienfarbe Cyan, reine Emission)')),
    src='M Destiny: 1–2 Bilder bei 60/s, Kern klein, Seitenflammen breiter, Zielen Automatik ≈ 20 % der Öffnung (Motiongen muendung › 6, '
        'Entscheidungsliste 5.3 A); Maße und Farben E (Stil v2.1)')
# Hülsenauswurf (0.16, Entscheidungsliste 5.4 A, Nutzer 26.10.2026): je Schuss eine Messinghülse (Rolle brass) aus dem Auswurffenster
# (Startlage und Richtung je Waffe: Modul-Feld EJECT, ohne Feld kein Auswurf), sichtbar ab dem Schussbild (delay_frames 0, 1 Bild später
# frei über dem Gehäuse), kurze Bahn nach rechts und rechts unten mit Drehung, nach life_s ausgeblendet. Die Bahn rechnet im
# Kameraraum (Viewmodel-Ebene wie die Waffe): Startlage aus der Waffe im Schussbild, Schwerkraft nach unten im Bild.
# Destiny (Motiongen muendung › 3/6): goldene Hülse im 1. Blitzbild oder 1 Bild danach, nach rechts bzw. rechts unten.
EJECT = dict(
    speed_mps=2.4, gravity_mps2=9.81, spin_dps=1500.0, spin_axis=(1.0, 0.25, 0.0), life_s=0.4, max_live=6, delay_frames=0,
    cases=dict(rifle=dict(len_mm=42, r_mm=4.8, segs=12),
               pistol=dict(len_mm=20, r_mm=4.6, segs=12)),     # 0.18: Kurzpatrone der MP (Patronen im Magazinfenster 24 × 4,4 mm) E
    role='brass',
    src='M Destiny: Hülse im 1. Blitzbild oder 1 Bild danach, rechts/rechts unten (Motiongen muendung › 6, Entscheidungsliste 5d/5.4 A); '
        'Geschwindigkeit, Drehung, Lebensdauer E')


def _norm(v):
    n = math.sqrt(sum(a * a for a in v))
    return tuple(a / n for a in v)


def flash_mesh():
    """Blitz als Netz im Autorenmaß (f vorn, u oben, x links; mm) relativ zu Socket_Muzzle: (Punkte, Dreiecke Kern, Dreiecke Flammen).
    Kern = Spindel längs des Laufs, Flammen = n flache Doppelpyramiden quer zum Lauf, nach vorn geneigt. Blender und Unity bauen daraus
    dasselbe Netz (Unity über ego.json › motion.flash)."""
    C, T = FLASH['core'], FLASH['tongues']
    V, core, flame = [], [], []
    V.append((-C['back_mm'], 0.0, 0.0))
    V.append((C['len_mm'], 0.0, 0.0))
    f_ring = C['len_mm'] * C['ring_at']
    for i in range(C['segs']):
        a = 2 * math.pi * i / C['segs']
        V.append((f_ring, C['r_mm'] * math.cos(a), C['r_mm'] * math.sin(a)))
    n = C['segs']
    for i in range(n):
        a, b = 2 + i, 2 + (i + 1) % n
        core += [(0, b, a), (1, a, b)]
    sw = math.tan(math.radians(T['sweep_deg']))
    for k in range(T['n']):
        a = 2 * math.pi * k / T['n']
        e = (0.0, math.cos(a), math.sin(a))                  # radial
        t = (0.0, -math.sin(a), math.cos(a))                 # quer (tangential)
        base = (T['base_mm'], 0.0, 0.0)
        tip = (base[0] + T['len_mm'] * sw, T['len_mm'] * e[1], T['len_mm'] * e[2])
        m = tuple(base[j] + (tip[j] - base[j]) * T['at'] for j in range(3))
        i0 = len(V)
        V += [base, tip,
              tuple(m[j] + t[j] * T['w_mm'] / 2 for j in range(3)), tuple(m[j] - t[j] * T['w_mm'] / 2 for j in range(3)),
              (m[0] + T['t_mm'] / 2, m[1], m[2]), (m[0] - T['t_mm'] / 2, m[1], m[2])]
        ring = [i0 + 2, i0 + 4, i0 + 3, i0 + 5]
        for j in range(4):
            p, q = ring[j], ring[(j + 1) % 4]
            flame += [(i0, q, p), (i0 + 1, p, q)]
    return V, core, flame


def case_mesh(kind):
    """Hülse als Zylinder längs der Querachse x (liegt quer im Auswurffenster), Mitte im Ursprung; mm wie flash_mesh."""
    c = EJECT['cases'][kind]
    n, h, r = c['segs'], c['len_mm'] / 2, c['r_mm']
    V = [(0.0, 0.0, -h), (0.0, 0.0, h)]
    for s in (-h, h):
        for i in range(n):
            a = 2 * math.pi * i / n
            V.append((r * math.cos(a), r * math.sin(a), s))
    F = []
    for i in range(n):
        a0, a1, b0, b1 = 2 + i, 2 + (i + 1) % n, 2 + n + i, 2 + n + (i + 1) % n
        F += [(0, a1, a0), (1, b0, b1), (a0, a1, b1), (a0, b1, b0)]
    return V, F


def flash_roll(n):
    """Drehung des n-ten Blitzes (0-basiert) um die Laufachse in Grad."""
    return FLASH['roll_deg'][n % len(FLASH['roll_deg'])]


def flash_cover_ads(W, n=120):
    """Größter Anteil der lichten Visieröffnung, den der Blitz im Zielen bedeckt (über alle Drehungen roll_deg), ohne Rendern: Haltung
    'ads' (Auge in Socket_Eye, Blick längs des Laufs), Öffnung = Glasfenster (sight_glass) an seiner Rückseite geschnitten mit demselben
    Fenster in der Ebene der vorderen Haubenkante (sight_frame_trim, falls vorhanden; Innenmaß dort gleich dem Glas; Glas als Querprofil:
nur Rasterpunkte in der projizierten Kontur, 0.21), Raster n × n; beim Zielfernrohr
    (0.20) die kreisrunde Objektivlinse (scope_glass). Verdeckung durch die Waffe zählt nicht (obere Schranke). Für ./check (≤ 20 %, 5.3 A); Unity misst
    dasselbe im Test mit dem laufenden Controller."""
    th = math.tan(math.radians(CAMERA['h_fov_deg'] / 2))
    tv = th * CAMERA['aspect'][1] / CAMERA['aspect'][0]
    eye, mz = W.ANCHORS['Socket_Eye']['at'], W.ANCHORS['Socket_Muzzle']['at']

    def proj(f, u, x):
        d = f - eye[0]
        return 50 - 50 * (x / d) / th, 50 - 50 * ((u - eye[1]) / d) / tv

    P = {q['id']: q for q in W.PARTS}
    circle = poly = None
    if 'sight_glass' in P:
        g = P['sight_glass']
        if 'pts' in g:                       # Baukasten v3 (0.21): Fenster als Querprofil – gezählt wird nur innerhalb der Kontur
            poly = [proj(g['f0'], g['cu'] + u, x) for x, u in g['pts']]
            xs, us = [q[0] for q in g['pts']], [q[1] for q in g['pts']]
            hw, hu, cu = (max(xs) - min(xs)) / 2, (max(us) - min(us)) / 2, g['cu'] + (max(us) + min(us)) / 2
        else:
            hw, hu, cu = g['ww'] / 2, g['hh'] / 2, g['cu']
        ga, gb = proj(g['f0'], cu + hu, hw), proj(g['f0'], cu - hu, -hw)
        t = P.get('sight_frame_trim')         # ohne Haube (H2 „Pille“) begrenzt nur das Glas
        ta, tb = (proj(t['f1'], cu + hu, hw), proj(t['f1'], cu - hu, -hw)) if t else (ga, gb)
        x0, y0, x1, y1 = max(ga[0], ta[0]), max(ga[1], ta[1]), min(gb[0], tb[0]), min(gb[1], tb[1])
    else:                                    # Zielfernrohr (0.20): lichte Öffnung = Objektivlinse, ein Kreis
        g = P['scope_glass']
        cx, cy = proj(g['a0'], g['c'][0], 0.0)
        rr = abs(proj(g['a0'], g['c'][0], g['r'])[0] - cx)
        circle = (cx, cy, rr)
        x0, y0, x1, y1 = cx - rr, cy - rr * 16 / 9, cx + rr, cy + rr * 16 / 9
    V, core, flame = flash_mesh()

    def inside(px, py, a, b, c):
        def s(p, q):
            return (px - q[0]) * (p[1] - q[1]) - (p[0] - q[0]) * (py - q[1])
        d = (s(a, b), s(b, c), s(c, a))
        return not (min(d) < 0 < max(d))

    best = 0.0
    for roll in sorted(set(FLASH['roll_deg'])):
        r = math.radians(roll)
        Q = [proj(mz[0] + f, mz[1] + u * math.cos(r) - x * math.sin(r), mz[2] + u * math.sin(r) + x * math.cos(r)) for f, u, x in V]
        T = [(Q[a], Q[b], Q[c]) for a, b, c in core + flame]
        pts = [(x0 + (i + .5) / n * (x1 - x0), y0 + (j + .5) / n * (y1 - y0)) for i in range(n) for j in range(n)]
        if circle:                           # % B und % H: Kreis im Bild als Ellipse (16:9)
            pts = [(x, y) for x, y in pts if ((x - circle[0]) / circle[2]) ** 2 + ((y - circle[1]) * 9 / 16 / circle[2]) ** 2 <= 1]
        if poly:                             # Querprofil-Glas: Punkte in der projizierten Kontur (Strahlwurf)
            def in_poly(px, py):
                c = False
                for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
                    if (ay > py) != (by > py) and px < ax + (py - ay) * (bx - ax) / (by - ay):
                        c = not c
                return c
            pts = [(x, y) for x, y in pts if in_poly(x, y)]
        hit = sum(any(inside(x, y, *t_) for t_ in T) for x, y in pts)
        best = max(best, hit / len(pts))
    return best


def flash_visible(fire, f):
    """Index des Schusses, dessen Blitz im Bild f (30/s) sichtbar ist, sonst None: sichtbar für dur_s ab dem Schussbild."""
    for i, s in enumerate(fire):
        if 0 <= f - s < FLASH['dur_s'] * FPS - 1e-6:
            return i
    return None


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


# ------------------------------------------------------------------ Ego-Übertrag je Klasse (0.18 „Quickdraw“, Entscheidungsliste Schritt 6)
# Haltungen, Anflugdauer und Spielwerte je Waffentyp (META['type']) als Daten (2.1 A/2b, 3.2 A/3b, 4d): ein Eintrag ersetzt einzelne
# Haltungen und streckt einzelne Aktionen auf eine neue Dauer; was er nicht nennt, gilt wie oben (POSES, ACTIONS). Bezug ist die
# Automatik (BASIC-01), deren Werte unverändert bleiben. Keine Sonderlogik nach Waffen-ID: Klassenwerte hier, Formwerte (Griffe,
# Live-Teile, Hülsenauswurf) als Felder im Waffenmodul (EGO_GRIPS, EGO_LIVE, EJECT). Bildlagen in % von B/H, Ursprung oben links,
# 75° horizontal (16:9) wie die Ego-Stills; Prüfung: Unity EditMode/PlayMode-Tests und docs/entscheidungsliste-motiongen.md › Schritt 6.
FOLLOW_HIP = ('crouch', 'air', 'lowered')   # Haltungen, die an der Hüfte hängen: wandern mit einer Klassen-Hüfte um denselben Versatz


def _follow(hip, ref_hip, ref):
    """Haltung `ref` (zur Bezugshüfte `ref_hip`) an eine neue Hüfte `hip` gehängt: gleicher Versatz in Lage, Zielpunkt und Rollen."""
    return dict(pos=tuple(round(h + r - b, 4) for h, r, b in zip(hip['pos'], ref['pos'], ref_hip['pos'])),
                aim=tuple(round(h + r - b, 4) for h, r, b in zip(hip['aim'], ref['aim'], ref_hip['aim'])),
                roll=hip['roll'] + ref['roll'] - ref_hip['roll'], src=f"wie {ref['src']}, an der Klassen-Hüfte (FOLLOW_HIP)")


CLASSES = {
    'auto_rifle': dict(
        poses={}, frames={},
        gameplay=dict(rpm=720, magazine=30, src='M 720/min (Chroma Rush, Motiongen waffenwerte › 4; Frage 7.1 A), Clip fire_hip seit 0.15 '
                                                 'ebenso (alle 2,5 Bilder); Magazin 30 E (Entwurf, Vorschlag Übergabe 0.4)'),
        src='Bezugsklasse: Haltungen POSES, Zeiten ACTIONS (BASIC-01, Destiny-Automatik)'),
    'submachine_gun': dict(
        poses=dict(
            hip=dict(pos=(-0.121, -0.42, -0.186), aim=(0.057, -3.0, -0.015), roll=6,
                     src='M Destiny-MP-Hüfte: Mündung ≈ 57/61 und 58/62 %, Holo ≈ 62–68/57–58 %, Lauf fast in Blickrichtung (Motiongen '
                         'REF destiny2 › MP PvE-Hüfte, Huckleberry), Band Kurzwaffen x 53–71 / y 59–84 % (2b); Lage E, gerechnet auf '
                         'Mündung 58/63 und Absehen 65,5/60 % (7 cm weiter zur Mitte und 4 cm höher als die Automatik)'),
            sprint=dict(pos=(-0.116, -0.34, -0.172), aim=(0.673, -2.115, -0.48), roll=40,
                        src='M/O Destiny-MP-Sprint: tiefe Trageform, Mündung ≈ 43/80, Holo-Ring ≈ 52/72 %, nach links gerollt (Motiongen REF '
                            'destiny2 › MP PvP, Entscheidungsliste 3b/3.2 A); Lage E, gerechnet auf Mündung 43/80 und Absehen 52/72 %, Rollen '
                            '+40° (Oberseite nach links; Automatik −35°, Oberseite nach rechts)'),
        ),
        frames=dict(aim_in=3, aim_out=2.4),
        frames_src='M Destiny-Anflug MP 8–12 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen Glidepath, Entscheidungsliste 4d) → 3 Bilder '
                   'bei 30/s, mit dem Zielen-Nachlauf (10 Hz) am Unity-Bild 11 Bilder bei 60/s (4 Bilder ergaben 13; gleiches Maß bei der '
                   'Automatik: 10 → 20 wie Destiny); aim_out im selben Verhältnis 0,3 (Destiny-MP ADS aus → ruhig 10–11 Bilder bei 60/s, '
                   'Huckleberry/Ikelos)',
        gameplay=dict(rpm=720, magazine=30,
                      src='M 720/min (Destiny-MP PvP, Dauerfeuer im Zielen ≈ 5 Bilder Abstand bei 60/s, Motiongen REF destiny2; Menüs '
                          '750–900/min [S]), Clip fire_hip wie die Automatik alle 2,5 Bilder; Magazin 30 E (Destiny-MP 26–30 [S])'),
        src='Entscheidungsliste Schritt 6, erste übertragene Klasse (Nutzer 26.10.2026): Hüfte 2b/2.1 A, Sprint 3b/3.2 A, Anflug 4d'),
    'scout_rifle': dict(
        # Hüfte und Sprint wie die Automatik (lange Waffe, Gewehr): die Haltungen POSES treffen am Scout schon das Destiny-Band
        poses={},
        keep=dict(
            hip='M Destiny-Hüfte lange Waffen: Mündung x 54–59 / y 60–71 % (Motiongen huefte › 4, Entscheidungsliste 2.1 A); Destiny-Scout '
                'Tone Patrol Mündung ≈ 57/63, Call to Serve 58/61 (Motiongen destiny2 › 3, huefte); Lage E wie die Automatik: am Scout '
                'gerechnet Mündung 57,0/62,9 %, Okular 24 pp rechts der Mündung (Band 7–34)',
            sprint='E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-Scout-Sprint nicht gemessen (Motiongen '
                   'destiny2 › Glidepath: kein Sprint-Clip)'),
        frames=dict(aim_in=7, aim_out=5),
        frames_src='Scout bei Destiny nur grob gemessen: Tone Patrol ≈ 22 Bilder (0,37 s, Bestand, „vom Nachbartyp übertragen“), Patron of '
                   'Lost Causes 0,20–0,25 s = 12–15 Bilder [M] (Motiongen destiny2 › Glidepath, visiere › v-d2-scout); dazwischen und '
                   'zwischen Scharfschütze (15 Bilder bis ruhig) und Impuls (20) → E 17 Bilder bei 60/s erste Bewegung → Ruhe, am '
                   'Unity-Bild gemessen; aim_out M Destiny-Scout ADS aus → Hüfte 0,17 s (Dead Man\'s Tale, Motiongen auswertung › V04) '
                   '= 5 Bilder bei 30/s',
        gameplay=dict(rpm=180, magazine=15, zoom_start=0.2,
                      src='M 180/min (Tone Patrol, Precision Frame: Schussabstand 20–21 Bilder bei 60/s und Menükarte, Motiongen destiny2 '
                          '› 3; Manifest Precision Frame 180 [S], waffenwerte › 4); Magazin 15 M (Menükarte Tone Patrol; Destiny-Scouts '
                          '13–18 [S]); Feuerart aus der Spec (META fire), halbautomatisch: ein Schuss je Zug; zoom_start E (1d): der Weltzoom '
                          'beginnt bei diesem Anteil des Augenwegs (Klassen ohne Wert 5 %) – am Unity-Bild gemessen, damit er wie beim Holo mit '
                          'oder kurz nach dem Modell beginnt'),
        src='Entscheidungsliste Schritt 6, zweite übertragene Klasse (0.20 „Spotter“): Hüfte 2.1 A (lange Waffe), Sprint 3.2 A, Anflug 4d, '
            'Zielfernrohr nach Visier-Standard 3'),
}
FIRE_MODES = {'full_auto': 'Dauerfeuer', 'semi_auto': 'Einzelfeuer (ein Schuss je Zug)'}   # META fire der spielbaren Waffen
# Live-Teile der Pilotwaffe (Abzug, Verschluss, Auswurfklappe im laufenden Feuer); andere Waffen nennen ihre im Modul-Feld EGO_LIVE
LIVE = dict(trigger='trigger', bolt='bolt_carrier', port='port_cover')
_PROFILES = {}


def weapon_id(W):
    return W.META['id'] + (f"-{W.META['variant']}" if W.META.get('variant') else '')


def profile(W):
    """Ego-Daten einer Waffe aus ihrer Klasse (CLASSES[META['type']]) und ihren Modul-Feldern: dict(type, poses, actions, grips, live,
    gameplay, src). Die Pilotwaffe ohne EGO_GRIPS/EGO_LIVE nutzt GRIPS und LIVE; ein Typ ohne Eintrag in CLASSES hat kein Ego-Profil."""
    wid = weapon_id(W)
    if wid in _PROFILES:
        return _PROFILES[wid]
    t = W.META['type']
    if t not in CLASSES:
        raise KeyError(f'{wid}: Waffentyp {t} hat kein Ego-Profil (ego.CLASSES)')
    C = CLASSES[t]
    fire_mode = W.META.get('fire', 'full_auto')
    if fire_mode not in FIRE_MODES:
        raise KeyError(f'{wid}: Feuerart {fire_mode} nicht spielbar (ego.FIRE_MODES)')
    poses = {k: dict(v) for k, v in POSES.items()}
    for k, note in C.get('keep', {}).items():      # Haltung der Automatik übernommen, Herkunft für diese Klasse
        poses[k]['src'] = f"{note} (Haltung POSES['{k}'] unverändert)"
    for k, v in C['poses'].items():
        poses[k] = dict(v)
    if 'hip' in C['poses']:
        for k in FOLLOW_HIP:
            if k not in C['poses']:
                poses[k] = _follow(poses['hip'], POSES['hip'], POSES[k])
    actions = copy.deepcopy(ACTIONS)
    grips = getattr(W, 'EGO_GRIPS', None) or GRIPS
    # Stützhand: Fingerstellung des Griffs statt underhand (Pilotwaffe: underhand), dazu die Ersetzungen des Griffs (finger_map)
    fmap = dict(grips['support'].get('finger_map', {}), underhand=grips['support']['fingers_pose'])
    for A in actions.values():
        A['fL'] = [(f, fmap.get(p, p)) for f, p in A.get('fL', [(0, 'underhand')])]
    for k, n in C['frames'].items():
        A = actions[k]
        old = A['frames']
        _retime(A, n / old)
        A['frames'] = int(math.ceil(n - 1e-9))
        A['src'] = f"{A['src']}; Klasse {t}: {old} → {n:g} Bilder ({C['frames_src']})"
    rpm = C['gameplay']['rpm']
    for A in actions.values():                  # Schussbilder der Feueraktionen in der Kadenz der Klasse (Clips wie Unity: gameplay.rpm)
        if A.get('fire') and rpm != 720:
            A['fire'] = shots_at(A['fire'][0], A['fire'][-1], rpm)
            A['src'] = f"{A['src']}; Klasse {t}: {rpm}/min, {FIRE_MODES[fire_mode]} (Schussbilder {A['fire']})"
    live = getattr(W, 'EGO_LIVE', None) or LIVE
    P = dict(type=t, poses=poses, actions=actions, grips=grips, live=live, gameplay=C['gameplay'], src=C['src'],
             frames_src=C.get('frames_src', ''), fire_mode=fire_mode)
    _PROFILES[wid] = P
    return P
