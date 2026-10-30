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


def shots_burst(first, last, n, burst_rpm, rpm):
    """Schussbilder einer Salvenwaffe bei 30 fps (0.22): Salven zu n Schuss im Abstand 60/burst_rpm, Salvenbeginn alle n · 60/rpm
    (rpm wie das Destiny-Menü: Schuss je Minute über die Salvenfolge gemittelt); nur ganze Salven, die bis `last` beginnen."""
    step, period, out = 60.0 * FPS / burst_rpm, n * 60.0 * FPS / rpm, []
    k = 0
    while first + period * k <= last + 1e-9:
        out += [first + int(period * k + step * i + 1e-9) for i in range(n)]
        k += 1
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
    # danach kehrt sie kritisch gedämpft mit recover_hz zurück. Salvenwaffen (0.22): Salvenlänge und Takt je Klasse in
    # CLASSES[...]['gameplay'] (burst_shots aus der Spec, burst_rpm), Bahnstufe je Schuss path_up_h je Klasse (Vorgabe hier)
    recover_delay_s=0.12, recover_hz=2.0,
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
    dasselbe im Test mit dem laufenden Controller. Ohne Fenster (Kimme/Korn, 0.33) None."""
    th = math.tan(math.radians(CAMERA['h_fov_deg'] / 2))
    tv = th * CAMERA['aspect'][1] / CAMERA['aspect'][0]
    eye, mz = W.ANCHORS['Socket_Eye']['at'], W.ANCHORS['Socket_Muzzle']['at']

    def proj(f, u, x):
        d = f - eye[0]
        return 50 - 50 * (x / d) / th, 50 - 50 * ((u - eye[1]) / d) / tv

    P = {q['id']: q for q in W.PARTS}
    circle = poly = None
    if 'scope_glass' not in P and not ('sight_glass' in P and ('pts' in P['sight_glass'] or 'ww' in P['sight_glass'])):
        return None                          # Kimme/Korn (0.33): keine Öffnung – der Kornpunkt heißt sight_glass, ist aber kein Fenster
    if 'sight_glass' in P:
        g = P['sight_glass']
        if 'pts' in g:                       # Baukasten v3 (0.21): Fenster als Querprofil – gezählt wird nur innerhalb der Kontur
            poly = [[proj(g['f0'], g['cu'] + u, x) for x, u in g['pts']]]
            tr = P.get('sight_frame_trim')   # vordere Haubenöffnung (Durchbruch der Stirnkante) als zweite Kontur
            if tr and tr.get('cuts') and 'pts' in tr['cuts'][0]:
                poly.append([proj(tr['f1'], tr['cu'] + u, x) for x, u in tr['cuts'][0]['pts']])
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
        if poly:                             # Querprofil-Glas: Punkte in allen projizierten Konturen (Glas, Haubenöffnung; Strahlwurf)
            def in_poly(px, py, pg):
                c = False
                for (ax, ay), (bx, by) in zip(pg, pg[1:] + pg[:1]):
                    if (ay > py) != (by > py) and px < ax + (py - ay) * (bx - ax) / (by - ay):
                        c = not c
                return c
            pts = [(x, y) for x, y in pts if all(in_poly(x, y, pg) for pg in poly)]
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
    def keys(v):                             # auf 1e-9 gerundet: 14 · (25/14) bliebe sonst 14,000000000000002 > Ende (0.33)
        return [(round(f * k, 9), x) for f, x in v]
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
    'pulse_rifle': dict(
        # Hüfte E an der Automatik ausgerichtet: deren Haltung trifft am Impuls x 59,7 / y 65,6 % (über dem Band 54–59), die kürzere
        # Kammer liegt weiter rechts; 2 cm weiter zur Mitte, 1,6 cm höher, Lauf leicht zur Mitte
        poses=dict(
            hip=dict(pos=(-0.17, -0.42, -0.214), aim=(0.07, -3.0, -0.184), roll=6,
                     src='M Destiny-Hüfte lange Waffen: Mündung x 54–59 / y 60–71 % (Motiongen huefte › 4, Entscheidungsliste 2.1 A); '
                         'Destiny-Impuls Gridskipper Mündung ≈ 57/61 (Motiongen destiny2 › z-gridskipper-salve); Lage E, gerechnet auf '
                         'Mündung 57,9/63,6 % (Automatik-Hüfte am Impuls: 59,7/65,6)'),
        ),
        keep=dict(sprint='E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-Impuls-Sprint nicht gemessen'),
        frames={},
        frames_src='M Destiny-Anflug Automatik/Impuls/MG 20 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen Glidepath, Entscheidungsliste '
                   '4d; Gridskipper ADS ein 18 Bilder bis ruhig, Motiongen destiny2): aim_in 10 Bilder bei 30/s wie die Automatik',
        gameplay=dict(rpm=540, magazine=36, burst_rpm=900, path_up_h=0.0133, recover_delay_s=0.10, recover_hz=5.0,
                      src='M Gridskipper (Rapid-Fire Frame): Menü 540/min und Magazin 36 [S], in der Salve 4 Bilder Abstand bei 60/s = '
                          '900/min [M], Salvenbeginn → Salvenbeginn 3 · 60/540 = 0,333 s (beobachtet ≥ 0,383 s im Spielertakt, kein '
                          'Grenzwert; Motiongen destiny2 › z-gridskipper-salve); Salvenlänge aus der Spec (META fire burst_3); Bahnstufe '
                          '≈ 4 pp H je Salve, Erholung in der Pause (Motiongen rueckstoss › r-d2-gridskipper, 5.2 A) → path_up_h 0,0133 je '
                          'Schuss (Automatik 0,010); Erholung zwischen den Salven ≈ 80 % (Gridskipper, Salvenfolge 0,38–0,40 s, Motiongen '
                          'destiny2 › z-gridskipper-salve) → E Erholung ab 0,10 s nach dem Schuss (1,5 Takte) mit 5 Hz kritisch gedämpft: in der '
                          'Pause von 0,2 s bleiben ≈ 20 % (gemeinsam 0,12 s / 2 Hz: ≈ 78 % blieben, und die nächste Salve sank anfangs ab)'),
        src='Entscheidungsliste Schritt 6, dritte übertragene Klasse (0.22 „Volley“): Hüfte 2.1 A (lange Waffe), Sprint 3.2 A, Anflug 4d, '
            'Salve aus der Spec'),
    'hand_cannon': dict(
        # Handfeuerwaffe (0.33 „Armory“, P1): beidhändiger Pistolengriff, kurze Waffe näher an der Kamera als die Gewehre (Körper im Bild
        # wie Destiny 53–70 % B); Trommel: Nachladen als eigene Aktion (Kran schwenkt aus, Hülsen raus, laden, zuklappen), kein Magazin
        poses=dict(
            hip=dict(pos=(-0.119, -0.38, -0.158), aim=(0.331, -3.0, 0.012), roll=6,
                     src='M Destiny-Handfeuerwaffe Hüfte: Mündung Annual Skate 57/63 (Motiongen huefte:52), Bad News 54/69 (huefte:60), Körper '
                         '53–70 % × 59–84 % (huefte:170); Lage E, gerechnet auf Mündung 57,1/63,0 %, Kimme 69,2/67,4 % (Körper 57–70 % B), '
                         'Lauf zur Mitte geneigt'),
            sprint=dict(pos=(-0.10, -0.36, -0.15), aim=(-0.02, -0.8, 1.6), roll=0,
                        src='M Destiny-Handfeuerwaffe Sprint: Waffe senkrecht, Lauf am oberen Rand, Körper 62–70 % B, hoch rechts (Motiongen '
                            'destiny2:562/467); Lage E, gerechnet Mündung 68,4/10,8 %, Körper 66–72 % B'),
            reload=dict(pos=(-0.07, -0.37, -0.15), aim=(0.6, -1.2, 1.0), roll=10,
                        src='M Destiny-Revolver: Hochdrehen 0,13 s, Trommel zur Kamera (Motiongen destiny2:492); Lage E: Mündung nach links oben '
                            '(gerechnet 47,3/27,6 %), linke Seite mit der ausgeschwenkten Trommel zeigt zur Kamera; 4 cm weiter weg als der '
                            'erste Entwurf (Stützhand verdeckte das halbe Bild)'),
        ),
        frames=dict(aim_in=3, aim_out=2.4, draw=18),
        frames_src='M Destiny-Handfeuerwaffe: ADS ein 10 Bilder bei 60/s erste Bewegung → Ruhe, aus 9–10 (The Last Word, Motiongen destiny2:584) '
                   '→ wie die MP 3 und 2,4 Bilder bei 30/s (gleiche Umrechnung mit dem Zielen-Nachlauf, Entscheidungsliste 4d); Ziehen Bad News '
                   '16 Bilder bei 60/s bis hüftähnlich + 19 bis ruhig (Motiongen wechsel:51) = 0,58 s → 18 Bilder (Automatik 25)',
        bob=dict(amp=(0.0068, 0.0234),
                 src='M Destiny-Handfeuerwaffe Sprint-Hub ≈ 13 % H / 4 % B bei 3,16 Hz (Motiongen destiny2:467): Automatik 0.022/0.018 m ergab '
                     '13 % B / 10 % H → seitlich × 4/13, senkrecht × 13/10'),
        actions=dict(
            reload_tactical=dict(
                de='Nachladen (Trommel: ausschwenken, auswerfen, laden, zuklappen)', frames=36,
                weapon=[(0, 'hip'), (2, ('hip', dict(roll=-3, up=-0.004))), (5, 'reload'), (8, ('reload', dict(pitch=8, up=0.012))),
                        (11, 'reload'), (19, ('reload', dict(roll=3))), (21, ('reload', dict(up=0.006, pitch=-2))),
                        (24, ('reload', dict(roll=-16, yaw=6))), (26, 'reload'), (31, ('hip', dict(roll=-2, up=-0.003))), (36, 'hip')],
                L=[(0, 'support'), (2, 'support'), (4, 'charge'), (6, 'mag'), (8, ('mag', (-25, 0, 4))), (10, OFF_L), (14, OFF_L),
                   (19, ('mag', (35, 0, 6))), (21, 'mag'), (23, 'mag'), (25, ('mag', (0, 0, 12))), (29, 'support'), (36, 'support')],
                fL=[(0, 'underhand'), (3, 'open'), (4, 'pinch'), (6, 'mag_hold'), (9, 'open'), (11, 'relaxed'), (16, 'open'),
                    (19, 'mag_hold'), (24, 'open'), (29, 'underhand')],
                mech={'cylinder_latch': [(0, 0), (4, 0), (5, 1), (7, 1), (9, 0)], 'crane': [(0, 0), (5, 0), (7, 1), (22, 1), (24, 0)]},
                events=[(2, 'HandOff'), (7, 'MagOut'), (8, 'Eject'), (21, 'MagIn'), (24, 'Chamber'), (29, 'HandOn'), (33, 'Ready')],
                src='M Destiny-Revolver aus der Hüfte 1,0 s: Hochdrehen 0,13, Trommel 0,62, Schließen 0,2 s, Zähler bei ≈ 70 % (Motiongen '
                    'destiny2:492; älterer Clip Munition 1,4 s, ausgefedert 2,1 s, destiny2:119) → 36 Bilder, MagIn bei 21; Ablauf E '
                    '(Riegel mit dem Daumen der Stützhand, Kran ausschwenken, Auswerfen mit Hochreißen, Laden von vorn, Zuklappen mit '
                    'Handgelenkschwung); Hülsen beim Auswerfen nicht dargestellt (Entscheidungsliste)'),
        ),
        same_reload=True,
        gameplay=dict(rpm=140, magazine=10, path_up_h=0.017, kick=2.5,
                      src='S Annual Skate 140/min, Magazin 10 (Menü, Motiongen waffenwerte:283, destiny2:94; Rahmen 100–257/min, 8–16 Schuss); '
                          'gemessen Abstand 27 Bilder bei 60/s = 133/min „vereinbar“ (destiny2:94); Feuerart aus der Spec (Spannabzug, '
                          'ein Schuss je Zug); Bahnstufe 0,017 M: Netto-Rest vor dem Folgeschuss 1,7 pp H (Hochimpuls bis 7,6 pp, Motiongen '
                          'rueckstoss:106); Kick 2,5 E: Modell ≈ 6 % hoch und 8° gekippt (destiny2:492) gegen Automatik-Kick 3° je Schuss'),
        src='Ego-Übertrag 0.33 „Armory“ P1: Hüfte, Sprint, Anflug, Ziehen und Nachladen nach Motiongen (Handfeuerwaffe), Trommelablauf E'),
    'sidearm': dict(
        # Seitenwaffe (0.33, P1): Pistolengriff wie die Handfeuerwaffe, Magazin im Griff (Nachladen der Bezugsklasse mit Magazin unten),
        # Durchladen am Schlitten statt am Ladehebel (mech_map, charge_back_mm)
        poses=dict(
            hip=dict(pos=(-0.109, -0.38, -0.164), aim=(0.341, -3.0, 0.006), roll=6,
                     src='M Destiny-Seitenwaffe Hüfte: Mündung Dead Man Walking 57/64 (Motiongen huefte:53), Minimum Distance 59/67 (huefte:65), '
                         'Brass Attacks 58/68 (destiny2:507); Lage E wie die Handfeuerwaffe, gerechnet auf Mündung 58,0/66,1 %'),
            sprint=dict(pos=(-0.10, -0.36, -0.15), aim=(-0.02, -0.8, 1.6), roll=0,
                        src='E: Seitenwaffen-Sprint nicht gemessen (Motiongen destiny2:563) → Trageform der Handfeuerwaffe (senkrecht, hoch '
                            'rechts, destiny2:562), gerechnet Mündung 70,2/31,0 %'),
            reload=dict(pos=(-0.07, -0.36, -0.14), aim=(0.75, -2.1, 0.45), roll=-40,
                        src='E wie die Bezugshaltung reload (T Reload roll −20/pitch 12, verstärkt), 2 cm weiter vorn (gestreckte Arme), '
                            'gerechnet Mündung 55,1/56,4 %'),
        ),
        frames=dict(aim_in=2.4, aim_out=2, draw=14, reload_tactical=43, reload_empty=52),
        frames_src='M Destiny-Seitenwaffe: ADS ein Rattler 6–7 Bilder bei 60/s, Brass Attacks 12 (Motiongen destiny2:585/269) → 2,4 Bilder bei '
                   '30/s (MP: 8–12 → 3), ADS aus: Zoom 7 Bilder → 2; Ziehen Minimum Distance 12 + 16 Bilder bei 60/s bis ruhig (wechsel:52) → '
                   '14; Nachladen 1,1–1,2 s (destiny2:491) × TIME_SCALE 1,25 → 43 Bilder, leer E +0,3 s Durchladen am Schlitten → 52 '
                   '(Destiny: taktisch gegen leer nicht gemessen)',
        bob=dict(amp=(0.0068, 0.0234), src='E wie die Handfeuerwaffe (Seitenwaffen-Sprint nicht gemessen, Motiongen destiny2:563)'),
        mech_map=dict(charging_handle='slide'), charge_back_mm=32,
        gameplay=dict(rpm=360, magazine=15, kick=1.2,
                      src='E: keine Einzelfeuer-Messung; Mitte des Manifest-Bands 260–491/min, Magazin 12–30 (Motiongen waffenwerte:332-340) '
                          '→ 360/min, Magazin 15 (Entscheidungsliste); Feuerart aus der Spec (Einzelfeuer); Bahnstufe wie die Automatik, '
                          'Kick 1,2 E (Welt bis 9,8 pp H nur netto beobachtet, rueckstoss:107)'),
        src='Ego-Übertrag 0.33 „Armory“ P1: Hüfte und Anflug nach Motiongen (Seitenwaffe), Sprint wie die Handfeuerwaffe, Nachladen der '
            'Bezugsklasse mit Magazin im Griff und Schlitten'),
    'sniper_rifle': dict(
        # Scharfschütze (0.33 „Armory“, P2): Repetierer – nach jedem Schuss repetiert die Stützhand am Kammerknopf links (Klassenaktionen
        # fire_cycle aus der Hüfte, fire_cycle_ads im Zielen; Unity spielt sie nach dem Schuss, solange Munition da ist); Nachladen mit
        # Kastenmagazin und Repetieren am Ende wie Far Future
        poses=dict(
            hip=dict(pos=(-0.19, -0.42, -0.23), aim=(0.02, -3.0, -0.32), roll=6,
                     src='M Destiny-Scharfschütze Hüfte: Mündung 56/68 (Motiongen huefte:51), 56/66 (huefte:61), Far Future 56/64 '
                         '(destiny2:496); Lage E wie die Automatik, Lauf 1,8° tiefer (langer Lauf: Automatik-Hüfte trifft 56,1/61,9), '
                         'gerechnet Mündung 56,1/65,7 %'),
        ),
        keep=dict(sprint='O Destiny-Scharfschütze „tief rechts“ nur beobachtet (Motiongen destiny2:567); E nach 3.2 A „Gewehre tief und quer '
                         'wie heute“: Trageform der Automatik (Entscheidungsliste)'),
        frames=dict(aim_in=6, aim_out=6),
        frames_src='M Destiny-Scharfschütze Far Future ADS ein 14 Bilder bei 60/s bis stabil (6 Hochziehen + 10 Overlay, Motiongen '
                   'destiny2:496) → 6 Bilder bei 30/s (Umrechnung mit dem Zielen-Nachlauf wie MP 8–12 → 3, Scout 17 → 7, Automatik 20 → 10); '
                   'ADS aus 0,17–0,25 s → 6 Bilder (0,20 s)',
        actions=dict(
            fire_cycle=dict(
                de='Repetieren nach dem Schuss aus der Hüfte (Kammerstängel links: heben, zurück, vor, senken)', frames=18,
                weapon=[(0, 'hip'), (4, ('hip', dict(roll=-6, yaw=-3))), (9, ('hip', dict(roll=-9, yaw=-4, back=0.006))),
                        (13, ('hip', dict(roll=-6, yaw=-3, up=0.003))), (18, 'hip')],
                L=[(0, 'support'), (2, 'support'), (6, 'charge'), (13, 'charge'), (17, 'support'), (18, 'support')],
                fL=[(0, 'underhand'), (3, 'open'), (6, 'pinch'), (13, 'pinch'), (15, 'open'), (17, 'underhand')],
                mech={'bolt_handle': [(0, 0), (6, 0), (8, 1), (12, 1), (14, 0)], 'bolt': [(0, 0), (8, 0), (10, 1), (11, 1), (12, 0)]},
                events=[(2, 'HandOff'), (10, 'Eject'), (12, 'Chamber'), (17, 'HandOn')],
                src='E: Repetieren in 0,6 s nach dem Schuss (Kadenz 90/min = 0,67 s je Schuss, Far Future [S]); Stängel links, die Stützhand '
                    'repetiert (Nutzer 28.10.2026), Hülse beim Zurückziehen (Marker Eject); Destiny zeigt beim Scharfschützen kein '
                    'eigenes Repetieren (Entscheidungsliste)'),
            fire_cycle_ads=dict(
                de='Repetieren nach dem Schuss im Zielen (Waffe bleibt im Anschlag)', frames=18,
                weapon=[(0, 'ads'), (18, 'ads')],
                L=[(0, 'support'), (2, 'support'), (6, 'charge'), (13, 'charge'), (17, 'support'), (18, 'support')],
                fL=[(0, 'underhand'), (3, 'open'), (6, 'pinch'), (13, 'pinch'), (15, 'open'), (17, 'underhand')],
                mech={'bolt_handle': [(0, 0), (6, 0), (8, 1), (12, 1), (14, 0)], 'bolt': [(0, 0), (8, 0), (10, 1), (11, 1), (12, 0)]},
                events=[(2, 'HandOff'), (10, 'Eject'), (12, 'Chamber'), (17, 'HandOn')],
                src='E wie fire_cycle, im Zielen ohne Kippen (Zielfernrohr bleibt vor dem Auge)'),
            reload_tactical=dict(
                de='Nachladen (Kastenmagazin tauschen, am Ende repetieren)', frames=65,
                weapon=[(0, 'hip'), (3, ('hip', dict(roll=-3, up=-0.004))), (9, 'reload'), (14, ('reload', dict(roll=-3))),
                        (19, ('reload', dict(up=-0.004, pitch=1.5))), (22, ('reload', dict(up=0.009, pitch=-2.5, roll=4))), (25, 'reload'),
                        (31, ('hip', dict(roll=-6, yaw=-3, up=0.010))), (35, ('hip', dict(roll=-9, yaw=-4, back=0.006, up=0.006))),
                        (39, ('hip', dict(roll=-6, yaw=-3, up=0.004))), (45, ('hip', dict(roll=-3))),
                        (58, ('hip', dict(roll=-2, up=-0.003))), (65, 'hip')],
                L=[(0, 'support'), (3, 'support'), (6, 'mag'), (10, ('mag', (8, -70, 25))), (14, OFF_L), (16, OFF_L),
                   (19, ('mag', (6, -55, 20))), (21, 'mag'), (23, 'mag'), (29, 'charge'), (41, 'charge'), (48, 'support'), (65, 'support')],
                fL=[(0, 'underhand'), (4, 'open'), (6, 'mag_hold'), (23, 'mag_hold'), (25, 'open'), (29, 'pinch'), (41, 'pinch'),
                    (43, 'open'), (48, 'underhand')],
                carry=[(6, 21)],
                mech={'mag_release': [(0, 0), (5, 1), (8, 0)], 'bolt_handle': [(0, 0), (30, 0), (32, 1), (39, 1), (41, 0)],
                      'bolt': [(0, 0), (32, 0), (35, 1), (37, 1), (39, 0)]},
                events=[(3, 'HandOff'), (8, 'MagOut'), (21, 'MagIn'), (35, 'Eject'), (38, 'Chamber'), (48, 'HandOn'), (62, 'Ready')],
                src='M Destiny-Scharfschütze Far Future: MagOut +0,28, MagIn +0,70, Kammerstängel +1,2, Hüfte 2,07, ruhig 2,18 s (Motiongen '
                    'nachladen:58) → Marker bei 8/21/36/62 von 65 Bildern, × TIME_SCALE; Ablauf E wie das Nachladen der Automatik, '
                    'Repetieren am Kammerknopf links (Nutzer 28.10.2026) aus der Hüfte wie fire_cycle (aus der Nachladehaltung lag der '
                    'Oberarm groß vor der Kamera); taktisch gegen leer nicht gemessen (Entscheidungsliste)'),
        ),
        same_reload=True,
        gameplay=dict(rpm=90, magazine=4, path_up_h=0.12, recover_delay_s=0.25, recover_hz=1.5, kick=3.0,
                      src='S Far Future 90/min, Magazin 4 (Menü, Motiongen destiny2:260; A Single Clap 90/min, 5); Feuerart aus der Spec '
                          '(Repetierer: ein Schuss je Zug, danach fire_cycle); Bahnstufe 0,12 M: im Zielfernrohr steigt die Welt ≈ 18 pp H '
                          'in 4 Bildern bei 60/s und bleibt ≈ 12 pp H versetzt (Motiongen zielbewegung:73) → Erholung E langsam (ab 0,25 s, '
                          '1,5 Hz); Kick 3,0 E (schwerer Einzelschuss)'),
        src='Ego-Übertrag 0.33 „Armory“ P2: Hüfte, Anflug und Nachladen nach Motiongen (Scharfschütze Far Future), Sprint der Automatik, '
            'Repetieren nach jedem Schuss E'),
    'trace_rifle': dict(
        # Spurgewehr (0.33, P2): Dauerstrahl – Dauerfeuer in der Kadenz der Klasse ohne Mündungsfeuer, Hülse und Rückstoß; Fokuslinse und
        # Scheibenmitte leuchten, solange der Abzug zieht (EGO_LIVE glow). Nachladen der Bezugsklasse mit der Energiezelle (mech_map)
        poses=dict(
            hip=dict(pos=(-0.165, -0.42, -0.205), aim=(0.10, -3.0, -0.12), roll=6,
                     src='M Destiny-Spurgewehr Hüfte: Mündung 57/60 (Motiongen destiny2:512), 57,7/59,6 (huefte:78); Lage E, gerechnet auf '
                         'Mündung 57,5/61,9 % (Automatik-Hüfte am Spurgewehr: 60,0/66,4 – kürzere Waffe), 2,5 cm weiter zur Mitte, 2,5 cm höher; '
                         'mit Mündung 59,2 % lag die Haubennase bei 53,7 % H in der Freihaltezone (A4, Ecke ab 55 %)'),
        ),
        keep=dict(sprint='E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-Spurgewehr-Sprint nicht gemessen '
                         '(Motiongen destiny2:570)'),
        frames=dict(aim_in=4, aim_out=3, reload_tactical=67),
        frames_src='M Destiny-Spurgewehr Prometheus Lens ADS ein ≈ 12 Bilder bei 60/s (Motiongen destiny2:592) → 4 Bilder bei 30/s (Umrechnung '
                   'wie Scharfschütze); ADS aus nicht gemessen → E 3 (Verhältnis der MP); Nachladen ≈ 1,6 s bis Hüfte, „kein Klassenwert“ '
                   '(destiny2:512) × TIME_SCALE = 60 Bilder bis Hüfte → Bezugsablauf (Hüfte bei 45/50) auf 67 Bilder gestreckt',
        mech_map=dict(mag_release='cell_release'),
        same_reload=True,
        gameplay=dict(rpm=1000, magazine=94, path_up_h=0.0, kick=0.0, muzzle_flash=False,
                      src='S Retraced Path 1000/min, 94 (Manifest, Motiongen waffenwerte:363); Feuerart aus der Spec (Dauerstrahl); kein '
                          'Rückstoß M (destiny2:500/512): Bahnstufe und Kick 0; kein Mündungsfeuer E (Strahl statt Blitz), keine Hülse '
                          '(Energiezelle, EJECT None)'),
        src='Ego-Übertrag 0.33 „Armory“ P2: Hüfte und Anflug nach Motiongen (Spurgewehr), Sprint der Automatik, Nachladen der Bezugsklasse '
            'mit der Energiezelle (leer wie taktisch, kein Ladehebel)'),
    'machine_gun': dict(
        # Maschinengewehr (0.33, P2): Gurtwaffe wie Dauerfeuer (FIRE_ALIAS); Nachladen als Klassenaktion mit Deckel, Kasten und Gurt
        poses={},
        keep=dict(
            hip='M Destiny-MG Hüfte: Mündung 56,2/64 (Motiongen huefte:72), ≈ 56/54 (destiny2:510); Lage E wie die Automatik: am MG gerechnet '
                'Mündung 57,7/62,7 % (Band lange Waffen 54–59 / 60–71)',
            sprint='E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-MG-Sprint nicht gemessen (Motiongen '
                   'destiny2:561)'),
        frames=dict(draw=28),
        frames_src='M Destiny-MG ADS ein 20 Bilder bei 60/s (Motiongen destiny2:583) = Automatik (aim_in 10 bei 30/s); Ziehen 18 + 37 Bilder bei '
                   '60/s bis ruhig (wechsel:56) = 0,92 s → 28 Bilder (Automatik 25)',
        actions=dict(
            reload_tactical=dict(
                de='Nachladen (Deckel auf, Kasten tauschen, Gurt einlegen, Deckel zu, durchladen)', frames=146,
                weapon=[(0, 'hip'), (3, ('hip', dict(roll=-3, up=-0.004))), (10, 'reload'), (19, ('reload', dict(pitch=2, up=0.004))),
                        (24, ('reload', dict(back=-0.05))), (31, ('reload', dict(roll=-4, up=-0.006, back=-0.06))),
                        (40, ('reload', dict(up=0.010, pitch=-3, roll=3, back=-0.05))), (44, ('reload', dict(back=-0.04))),
                        (51, ('reload', dict(up=-0.004, pitch=1.5, back=-0.02))), (60, 'reload'),
                        (83, ('reload', dict(up=-0.012, pitch=3))), (88, 'reload'), (96, ('hip', dict(roll=-6, yaw=-3, up=0.010))),
                        (100, ('hip', dict(roll=-9, yaw=-4, up=0.006))), (106, ('hip', dict(roll=-6, yaw=-3, up=0.004))),
                        (114, ('hip', dict(roll=-3))), (132, ('hip', dict(roll=-2, up=-0.003))), (146, 'hip')],
                L=[(0, 'support'), (3, 'support'), (11, 'cover'), (14, 'cover'), (19, ('mag', (50, -10, 15))), (27, 'mag'),
                   (33, ('mag', (0, -60, 40))),
                   (38, 'mag'), (42, 'mag'), (48, ('cover', (-40, -30, 26))), (53, ('cover', (-40, -30, 26))), (64, ('cover', (0, 30, 0))),
                   (72, 'cover'), (83, 'cover'), (90, ('charge', (10, 0, 30))), (96, 'charge'), (100, ('charge', (-70, 0, 0))),
                   (103, 'charge'), (112, 'support'), (146, 'support')],
                fL=[(0, 'underhand'), (5, 'open'), (11, 'pinch'), (14, 'pinch'), (17, 'open'), (27, 'mag_hold'), (42, 'mag_hold'),
                    (45, 'pinch'), (55, 'open'), (72, 'open'), (86, 'open'), (96, 'pinch'), (103, 'pinch'), (106, 'open'),
                    (112, 'underhand')],
                mech={'feed_cover': [(0, 0), (12, 0), (19, 1), (72, 1), (83, 0)],
                      'ammo_box': [(0, 0), (28, 0), (32, 3), (35, 3), (40, 0)],
                      'charging_handle': [(0, 0), (96, 0), (100, 1), (103, 0)]},
                events=[(3, 'HandOff'), (19, 'CoverOpen'), (32, 'MagOut'), (40, 'BoxIn'), (51, 'MagIn'), (83, 'CoverClosed'),
                        (100, 'Chamber'), (112, 'HandOn'), (140, 'Ready')],
                src='M Destiny-MG Gurtkasten 4,40 s bis Hüfte, 4,87 ruhig: Deckel +0,63, Kasten +1,32, Gurt +1,70, Deckel zu +2,78 s (Motiongen '
                    'nachladen:60) → Marker bei 19/40/51/83/132 von 146 Bildern, × TIME_SCALE; Ablauf E (Deckel hinten anheben, Kasten nach '
                    'links unten aus dem Bild und zurück, Gurt in die Zuführschale, Deckel zuschlagen, Ladehebel aus der Hüfte wie der Scharfschütze; '
                    'der Deckel springt nach dem Entriegeln allein auf, beim Kasten 3–6 cm weiter weg – sonst lag der Arm groß vor der '
                    'Kamera); Munition voll beim Gurt'),
        ),
        same_reload=True,
        gameplay=dict(rpm=900, magazine=75, kick=1.3,
                      src='M/S Shattered Cipher 900/min, 75 (Motiongen destiny2:273); Feuerart aus der Spec (Gurt → Dauerfeuer, '
                          'FIRE_ALIAS); Bahnstufe wie die Automatik: Destiny-MG Hüfte 2,8 pp H, im Zielen bis 12,4 pp H über mehrere Stöße '
                          '(rueckstoss:110), kein Wert je Schuss; Kick 1,3 E (schwere Waffe)'),
        src='Ego-Übertrag 0.33 „Armory“ P2: Hüfte und Sprint der Automatik, Ziehen und Nachladen nach Motiongen (Gurtkasten), Ablauf E'),
    'portal_cannon': dict(
        # Werkzeug (0.17 „Gateway“): nur Hüfte, kein Visier (kein Socket_Eye), kein Magazin – ohne Zielen und Nachladen; diese Haltungen
        # und Aktionen fehlen in den Daten (drop), Unity schaltet danach (nicht nach der Waffen-ID)
        poses=dict(
            hip=dict(pos=(-0.16, -0.40, -0.24), aim=(1.4, -3.0, 0.0), roll=-20,
                     src='M Portal-2-Portalkanone: rechts unten, vorderes Rohrende ≈ 57/75 %, beim Gehen 54–63/68–75 %, Rohr von rechts '
                         'unten nach links oben (cubeescape-reference/docs/portal2.md › weißes Modell); Lage E, gerechnet auf Achskrone '
                         '56,9/71,2 %; quer gestellt, damit die linke Flanke beide Kerne zeigt (Nutzer 27.10.2026: „Schade dass man von der '
                         'Portal Gun die Farb-Elemente nicht sieht“; von vier Varianten c14: Kern A und B sichtbar, Achskrone im Band); '
                         'Kerbe (Leitkante) rechts im Bild; Stützhand am Vordergriff unter der Unterlippe'),
            sprint=dict(pos=(-0.10, -0.34, -0.22), aim=(0.6, -2.1, -0.4), roll=30,
                        src='E (Klasse Werkzeug, in der Entscheidungsliste nicht gemessen; Portal 2 ohne eigene Sprintpose): Trageform der '
                            'Kurzwaffen nach 3.2 A (MP: tief, nach links gerollt, Mündung ≈ 43/80 %), Rollen +30° statt +40° wegen der breiten '
                            'Eischale; gerechnet Achskrone 44,3/80,4 %'),
        ),
        drop=dict(poses=('ads', 'reload'),
                  actions=('aim_in', 'aim_out', 'fire_hip', 'fire_ads', 'reload_tactical', 'reload_empty', 'sprint_to_aim', 'draw_aim',
                           'reload_to_switch'),
                  src='Werkzeug ohne Visier und Magazin (0.17): kein Zielen, kein Nachladen; Feuer als fire_a/fire_b (Portale)'),
        actions=dict(
            fire_a=dict(de='Portal A (Linksklick): Ring dreht 120° im Uhrzeigersinn (von hinten)', frames=18,
                        weapon=[(0, 'hip'), (18, 'hip')], fire=[2], portal='A',
                        mech={'emitter_ring': [(0, 0), (2, 0), (12, 1), (18, 1)]}, events=[(2, 'Fire')],
                        src='Ablauf aus dem Modul (t01 ACTIONS fire_a, 0.17): Ring 2 → 12 Bilder; Kick aus gameplay.kick'),
            fire_b=dict(de='Portal B (Rechtsklick): Ring dreht 120° gegen den Uhrzeigersinn', frames=18,
                        weapon=[(0, 'hip'), (18, 'hip')], fire=[2], portal='B',
                        mech={'emitter_ring': [(0, 0), (2, 0), (12, -1), (18, -1)]}, events=[(2, 'Fire')],
                        src='wie fire_a, Gegenrichtung (t01 ACTIONS fire_b)'),
        ),
        frames={},
        gameplay=dict(rpm=240, magazine=0, path_up_h=0.0, muzzle_flash=False, range_m=24.0, kick=0.6, ring_turn_s=round(10 / 30, 6),
                      portals=[dict(name='A', input='fire', role='portal_a', color='#1AD9FF', ring=1),
                               dict(name='B', input='aim', role='portal_b', color='#FF7314', ring=-1)],
                      src='Cube Escape (Q-CE-14/15): Linksklick Portal A (Cyan #1AD9FF), Rechtsklick Portal B (Orange #FF7314), Abklingzeit '
                          '0,25 s → 240/min, Kick E 0,6 der Automatik (Portal 2: obere Klaue ≈ 7 % H im ersten Schussbild, portal2.md), Reichweite 24 m, ohne Streuung (Sichtlinie zum Fadenkreuz), Munition keine (magazine 0 = unbegrenzt); Ring je Schuss 120° in 10 Bildern bei 30/s (Modul '
                          't01 fire_a/fire_b), Richtung je Portal; ohne Mündungsfeuer und ohne Bahnstufe (E: Werkzeug, Rückmeldung über '
                          'Ring und Treffermarke in Portalfarbe)'),
        src='Werkzeug der Familie (0.22 „Volley“): Hüfte nach Portal 2 (M) und Familienmaßen, Sprint als Klasse „Werkzeug“ E; Bedienung '
            'Linksklick A / Rechtsklick B ohne Zielen (Nutzer 27.10.2026 über Sightline: „A“ – „Linksklick = Portal A …, Rechtsklick = Portal '
            'B …, kein Zielen …, Abklingzeit 0,25 s als Datenfeld“; Präzision X zurückgestellt, docs/erweiterungen.md)'),
}
# META fire der spielbaren Waffen → Feuerart in Unity (gameplay.fire_mode). burst_N (0.22): Salve zu N Schuss je Zug, gehalten Salve um
# Salve; single (Werkzeug): ein Schuss je Klick, bei zwei Portalen je Taste
FIRE_MODES = {'full_auto': 'Dauerfeuer', 'semi_auto': 'Einzelfeuer (ein Schuss je Zug)', 'burst': 'Salve (n Schuss je Zug)',
              'single': 'Einzelschuss je Klick (Werkzeug)',
              'bolt_action': 'Repetierer (ein Schuss je Zug, danach Kammerstängel als Klassenaktion fire_cycle/fire_cycle_ads)',
              'continuous_beam': 'Dauerstrahl (Dauerfeuer ohne Mündungsfeuer, Leuchtteile EGO_LIVE glow an, solange der Abzug zieht)'}
# Feuerarten mit einem Schuss je Zug (Abzug je Schuss gezogen und gelöst; ego_build und Unity EgoData.Semi)
SEMI_MODES = ('semi_auto', 'single', 'bolt_action')


# Feuerarten der Spec, die im Spiel wie eine vorhandene laufen (0.33): der Spannabzug der Trommel schießt wie Einzelfeuer, der Hahn ist
# Live-Teil (EGO_LIVE bolt); das Gurt-MG schießt wie Dauerfeuer, der Gurt ist Teil des Nachladens (Klassenaktion)
FIRE_ALIAS = {'semi_auto_double_action': 'semi_auto', 'full_auto_belt': 'full_auto'}


def fire_spec(fire):
    """Feuerart und Salvenlänge aus META fire: 'burst_3' → ('burst', 3), FIRE_ALIAS aufgelöst, sonst (fire, 0)."""
    if fire.startswith('burst_'):
        return 'burst', int(fire.split('_')[1])
    return FIRE_ALIAS.get(fire, fire), 0
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
    fire_mode, burst = fire_spec(W.META.get('fire', 'full_auto'))
    if fire_mode not in FIRE_MODES:
        raise KeyError(f'{wid}: Feuerart {fire_mode} nicht spielbar (ego.FIRE_MODES)')
    if (fire_mode == 'burst') != ('burst_rpm' in C['gameplay']):
        raise KeyError(f'{wid}: Salve braucht burst_rpm in der Klasse {t} (und nur sie)')
    drop = C.get('drop', {})
    poses = {k: dict(v) for k, v in POSES.items() if k not in drop.get('poses', ())}
    for k, note in C.get('keep', {}).items():      # Haltung der Automatik übernommen, Herkunft für diese Klasse
        poses[k]['src'] = f"{note} (Haltung POSES['{k}'] unverändert)"
    for k, v in C['poses'].items():
        poses[k] = dict(v)
    if 'hip' in C['poses']:
        for k in FOLLOW_HIP:
            if k not in C['poses']:
                poses[k] = _follow(poses['hip'], POSES['hip'], POSES[k])
    actions = {k: copy.deepcopy(A) for k, A in ACTIONS.items() if k not in drop.get('actions', ())}
    mmap, back = C.get('mech_map', {}), C.get('charge_back_mm')
    for A in actions.values():                       # Bauteile der Bezugswaffe → Bauteile der Klasse (Pistole: Schlitten statt Ladehebel)
        if mmap and 'mech' in A:
            A['mech'] = {mmap.get(pid, pid): v for pid, v in A['mech'].items()}
        if back is not None and 'L' in A:            # Durchladeweg der Stützhand am Griff 'charge' (Bezug 58 mm Ladehebel)
            A['L'] = [(f, ('charge', (-back, 0, 0)) if isinstance(k, tuple) and k[0] == 'charge' else k) for f, k in A['L']]
    for k, A in C.get('actions', {}).items():        # Aktionen der Klasse (Werkzeug: fire_a/fire_b, Trommel: Nachladen); Feuer in
        actions[k] = copy.deepcopy(A)                 # Originalzeit wie fire_hip (KEEP_TIME), alles andere mit TIME_SCALE wie ACTIONS
        _retime(actions[k], 1.0 if k in KEEP_TIME or k.startswith('fire') else TIME_SCALE)
    grips = getattr(W, 'EGO_GRIPS', None) or GRIPS
    # Stützhand: Fingerstellung des Griffs statt underhand (Pilotwaffe: underhand), dazu die Ersetzungen des Griffs (finger_map)
    fmap = dict(grips['support'].get('finger_map', {}), underhand=grips['support']['fingers_pose'])
    for A in actions.values():
        A['fL'] = [(f, fmap.get(p, p)) for f, p in A.get('fL', [(0, 'underhand')])]
    if 'bob' in C:                                  # Sprint-Hub der Klasse (Handfeuerwaffe: schmal und hoch)
        actions['sprint']['bob'] = dict(actions['sprint']['bob'], amp=C['bob']['amp'])
        actions['sprint']['src'] = f"{actions['sprint']['src']}; Klasse {t}: Hub {C['bob']['amp']} ({C['bob']['src']})"
    for k, n in C['frames'].items():
        A = actions[k]
        old = A['frames']
        _retime(A, n / old)
        A['frames'] = int(math.ceil(n - 1e-9))
        A['src'] = f"{A['src']}; Klasse {t}: {old} → {n:g} Bilder ({C['frames_src']})"
    if C.get('same_reload'):                       # leer wie taktisch (Trommel, Repetierer, Energiezelle, Gurt): ein Ablauf, nach dem Strecken
        actions['reload_empty'] = dict(copy.deepcopy(actions['reload_tactical']), de=actions['reload_tactical']['de'] + ', auch leer')
    G = dict(C['gameplay'])
    for k in ('path_up_h', 'recover_delay_s', 'recover_hz'):   # Bahn je Klasse (0.22), sonst gemeinsam (ego.RECOIL)
        G.setdefault(k, RECOIL[k])
    G.setdefault('kick', 1.0)                   # Modellkick und Kamera-Ruck je Schuss relativ zu ego.RECOIL (0.22; Clips und Unity gleich)
    for A in actions.values():
        if A.get('fire') and G['kick'] != 1.0:
            A['kick'] = G['kick']
    if burst:
        G['burst_shots'] = burst                  # Salvenlänge aus der Spec (META fire burst_N)
    rpm = G['rpm']
    for k, A in actions.items():                # Schussbilder der Feueraktionen in der Kadenz der Klasse (Clips wie Unity: gameplay.rpm)
        if not A.get('fire') or k in C.get('actions', {}):
            continue
        if burst:
            A['fire'] = shots_burst(A['fire'][0], A['fire'][-1], burst, G['burst_rpm'], rpm)
            A['de'] = A['de'].replace('Dauerfeuer', 'Salven')
        elif rpm != 720:
            A['fire'] = shots_at(A['fire'][0], A['fire'][-1], rpm)
        else:
            continue
        A['src'] = f"{A['src']}; Klasse {t}: {rpm}/min, {FIRE_MODES[fire_mode]} (Schussbilder {A['fire']})"
    live = getattr(W, 'EGO_LIVE', None) or LIVE
    P = dict(type=t, poses=poses, actions=actions, grips=grips, live=live, gameplay=G, src=C['src'],
             frames_src=C.get('frames_src', ''), fire_mode=fire_mode, drop=drop,
             mag=grips.get('mag', {}).get('part', 'magazine'))   # Bauteil, das das Nachladen trägt (carry/drop): Magazin, Energiezelle (0.33)
    _PROFILES[wid] = P
    return P
