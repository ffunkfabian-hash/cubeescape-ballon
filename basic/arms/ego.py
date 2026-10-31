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
# fL/fR (Fingerstellung), mech (Bauteilbewegung 0..1 wie in den Waffenmodulen; −1 = Gegenrichtung, 0.35 Gegendrehung der
# Granatwerfer-Trommel), carry (Magazin folgt der linken Hand), fire (Bilder
# der Schüsse), events (Marker). Zwischen Schlüsseln wird geglättet (Ease In/Out).
OFF_L = ('cam', (0.30, -0.25, -0.62))      # linke Hand unter dem Bild (Magazin holen)
OFF_TL = ('cam', (0.34, -0.30, 0.22))      # linke Hand links über dem Bild (Raketenwerfer: Rakete von links oben, 0.35)


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


def shots_charge(pull, end, charge_f, rpm, n=1, burst_rpm=0):
    """Schussbilder einer Ladewaffe (0.33, Feuerart charge_burst/charge_single) bei 30 fps: Abzug ab `pull` gehalten; je Zyklus (60/rpm,
    Aufladen eingeschlossen) erst charge_f Bilder Aufladen, dann n Schuss im Abstand 60/burst_rpm; nur Schüsse bis `end`."""
    period, step, out, k = 60.0 * FPS / rpm, (60.0 * FPS / burst_rpm if n > 1 else 0.0), [], 0
    while pull + period * k + charge_f <= end + 1e-9:
        s0 = pull + period * k + charge_f
        out += [int(s0 + step * i + 1e-9) for i in range(n) if s0 + step * i <= end + 1e-9]
        k += 1
    return out


def charge_level(fire, f, charge_f, n=1, fade_f=9.0):
    """Ladung 0 … 1 im Bild f einer Feueraktion einer Ladewaffe (Leuchtteile EGO_LIVE glow; Unity EgoSolver.ChargeLevel): je Zyklus aus
    n Schuss steigt sie in den charge_f Bildern vor dem ersten Schuss linear auf 1, bleibt bis zum letzten Schuss und fällt danach in
    fade_f Bildern auf 0."""
    lv = 0.0
    for g in range(0, len(fire), n):
        s0, s1 = fire[g], fire[min(g + n, len(fire)) - 1]
        if s0 - charge_f <= f < s0:
            lv = max(lv, (f - (s0 - charge_f)) / charge_f)
        elif s0 <= f <= s1:
            lv = 1.0
        elif f > s1:
            lv = max(lv, 1.0 - (f - s1) / fade_f)
    return max(0.0, min(1.0, lv))


def trigger_on(fire, f, semi=False, lead=0.0):
    """Abzug gezogen im Bild f einer Feueraktion: Dauerfeuer vom Bild vor dem ersten bis nach dem letzten Schuss; Einzelfeuer (0.20,
    Feuerart semi_auto) je Schuss ein Bild davor bis ein Bild danach, dazwischen losgelassen (ein Schuss je Zug). lead (0.33, Ladewaffe):
    der Abzug zieht schon lead Bilder vor dem ersten Schuss (Aufladen)."""
    if not fire:
        return False
    if semi:
        return any(s - 1 <= f <= s + 1 for s in fire)
    return fire[0] - 1 - lead <= f <= fire[-1] + 1

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
    'walk': dict(de='Gehen (liegende Acht, Waffe etwas gesenkt)', frames=48,
                 weapon=[(0, ('hip', dict(up=-0.012, pitch=-1.5))), (48, ('hip', dict(up=-0.012, pitch=-1.5)))],
                 bob=dict(start=0, end=48, period=24, amp=(0.007, 0.006), roll=1.2), events=[],
                 src='O Motiongen REF 0.37 Verdict › C/G (z-v37-laufen): Laufen ohne Sprint mit eigenem, langsamerem Takt 0,37–0,41 s je '
                     'Schritt (Automatik, MP, Fusion, MG) → period 24 (Doppelschritt 0,80 s, vertikal 0,40 s je Schritt; Sprint 19) '
                     'bleibt; Hub vertikal 2–5 pp H ≈ 0,2–0,5 des Sprinthubs → 0,006 m (0,33 von 0,018; bis 0.34 0,004 = 0,22); Waffe in '
                     'abgesenkter Hüftlage mit vollem Fadenkreuz → E 12 mm tiefer, 1,5° gesenkt (≈ 3 pp H; Destiny-Hüllen beim Laufen '
                     'Automatik 4 pp tiefer, MP und Fusion höher als ihre Hüfte – kein einheitliches Maß). Unity legt den Versatz mit dem '
                     'Wippgewicht auf (EgoController); seitlich, Rollen und liegende Acht E (CE)'),
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
# Zielweite der Projektile (0.35 „Stance“, Richter): ohne Treffer längs der Blickachse zielt die Bahn ab der Mündung auf den Punkt in
# range_m voraus (Unity WeaponFx.Launch; mit Treffer auf den Treffpunkt unter dem Fadenkreuz)
AIM = dict(range_m=60.0, src='E: Nutzerbefund Testbuild 0.33 Bogen „Schuss geht daneben“ (parallel zur Blickachse lief die Bahn neben der '
                             'Mitte vorbei); Motiongen REF 0.35 Backblast › D: Pfeilachse durch die Bildmitte. 60 m ≈ halbe Parcourslänge, '
                             'Abweichung dahinter < 0,2° bei 20 cm Mündungsversatz')
# Zielbild wie Destiny (0.35 „Stance“, Nutzerentscheid 193 B, 31.10.2026 über Sightline: „So wie Destiny“): im Zielen sind alle Teile der
# Waffe aus außer dem Visier (Baugruppe sight), seiner Schiene (BRI-22), dem Mündungsteil (Teil von Socket_Muzzle, Mündungsaufsatz BMZ)
# und den Baugruppen in keep_asm der Klasse; die Arme sind ebenfalls aus (arms; ohne sie blieb die Automatik bei 12,4 %: Griffhand und
# Stützarm unter dem Visier) – dieselbe Regel ADS_HIDE in Blender und Unity (Teile mit ads_hide, Augenpunkt nah an der
# Ziellage). Bildwinkel und Augenabstand senkten den Bildanteil nachweislich nicht (Bericht 0.35 › 193 B / 194); Destiny erreicht 2,7–9,5 %
# nur ohne die Waffe unter dem Visier (Motiongen REF 0.35 Backblast › F, z-bb-bildanteil). Je Klasse: CLASSES[...]['ads_strip']
# (keep_asm, keep_parts; False = aus). Seit 0.35.1 steht die Regel still (ADS_STRIP_ON = False, Nutzerentscheid 208 A).
ADS_STRIP_ON = False      # 0.35.1 (Nutzerentscheid 208 A, 31.10.2026): Regel aus – im Zielen sind Waffe und Arme wieder sichtbar wie in 0.34; 193 B ruht bis zum Neuentscheid
ADS_STRIP = dict(keep_asm=('sight',), keep_iface=('BMZ',), keep_anchors=('Socket_Muzzle',), arms=True,
                 drop_iface=('BRI-22',), drop_parts=('sight_clamp', 'scope_keel'),   # Visierfuß, Klemme, Kiel: unter dem Glas, nah an der Kamera
                 src='Nutzerentscheid 193 B „So wie Destiny“ (31.10.2026): Destiny-Zielbild 2,7–9,5 % je Klasse (Backblast › F); Visier, '
                     'Absehen und Laufspitze bleiben sichtbar')


# Je Klasse (Waffentyp): Kamera im Zielen back_m hinter Socket_Eye (das Visier allein ist bei Visier-Standard 3 mit 90 mm Augenabstand
# größer als bei Destiny; ohne Schaft und Gehäuse wirkt der Abstand jetzt wie gerechnet: Fläche × (90 / (90 + back))²) bzw. weitere
# Baugruppen sichtbar, wo BALLON unter Destiny läge. Ziel Destiny-Zielen je Klasse (Backblast › F, Bericht 0.35 › Bildanteil).
ADS_STRIP_CLASS = {
    'auto_rifle': dict(back_m=0.05), 'submachine_gun': dict(back_m=0.015), 'scout_rifle': dict(back_m=0.005),
    'pulse_rifle': dict(back_m=0.005), 'trace_rifle': dict(back_m=0.01), 'fusion_rifle': dict(back_m=0.015),
    'linear_fusion_rifle': dict(back_m=0.03), 'grenade_launcher': dict(back_m=0.015),
    'sidearm': dict(keep_asm=('sight', 'barrel')), 'shotgun': dict(keep_asm=('sight', 'barrel')),
}


def ads_strip_rule(W, C):
    """Regel ADS_STRIP für die Waffe W (Klasse C): gemeinsamer Satz, Klassensatz ADS_STRIP_CLASS, Klassenwert ads_strip; None = aus."""
    if not ADS_STRIP_ON or C.get('ads_strip') is False:
        return None
    return dict(ADS_STRIP, **ADS_STRIP_CLASS.get(W.META['type'], {}), **(C.get('ads_strip') or {}))


def ads_strip_parts(W, C):
    """Teile der Waffe W, die im Zielen nach ads_strip_rule aus sind; leer, wenn die Klasse es abschaltet."""
    R = ads_strip_rule(W, C)
    if R is None:
        return ()
    keep = {W.ANCHORS[a]['part'] for a in R['keep_anchors'] if a in W.ANCHORS and W.ANCHORS[a].get('part')}
    keep |= set(R.get('keep_parts', ()))
    keep |= {p['id'] for p in W.PARTS if p['asm'] in R['keep_asm'] or any((p.get('iface') or '').startswith(i) for i in R['keep_iface'])}
    while True:                              # Kinder sichtbarer Teile bleiben sichtbar (parent_part, bis nichts mehr dazukommt)
        more = {p['id'] for p in W.PARTS if p.get('parent_part') in keep} - keep
        if not more:
            break
        keep |= more
    keep -= {p['id'] for p in W.PARTS if p['id'] in R['drop_parts'] or any((p.get('iface') or '').startswith(i) for i in R['drop_iface'])}
    return tuple(p['id'] for p in W.PARTS if p['id'] not in keep)


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
               pistol=dict(len_mm=20, r_mm=4.6, segs=12),      # 0.18: Kurzpatrone der MP (Patronen im Magazinfenster 24 × 4,4 mm) E
               shotshell=dict(len_mm=50, r_mm=9.5, segs=14),   # 0.33: Schrotpatrone (Maße der Patrone shell_round von BASIC-08) E
               grenade_40=dict(len_mm=35, r_mm=21, segs=16),   # 0.33 P4: leere 40-mm-Granathülse (BASIC-13, aus dem Modul EJECT_CASES) E
               revolver=dict(len_mm=30, r_mm=5.6, segs=12),    # 0.34: Hülse der Handfeuerwaffe (Kammer Ø 12 von BASIC-04 v2.1) E
               belt_link=dict(len_mm=8, r_mm=5.4, segs=10)),   # 0.34: Gurtglied des MG (aus w15 EJECT_CASES, Gliedring r 5,4) E
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
    k = CLASSES.get(getattr(W, 'META', {}).get('type'), {}).get('gameplay', {}).get('flash_scale', 1.0)   # Blitzmaßstab je Klasse (0.33 P4)
    V = [(f * k, u * k, x * k) for f, u, x in V]

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


# Schrittteile (0.34 „Payload“, EGO_LIVE index): Teile mit 'cycle shot' (Trommel der Handfeuerwaffe, Gurtvorschub des MG) laufen nach
# jedem Schuss in INDEX['frames'] Bildern von 0 auf 1 (eine Kammer, eine Gliedteilung) und stehen beim nächsten Schuss wieder auf 0 –
# die Teilung ist symmetrisch, der Sprung unsichtbar. Bei hoher Kadenz höchstens share des Schussabstands (MG 900/min: 1,6 Bilder).
INDEX = dict(frames=3.0, share=0.8, src='E: Trommel dreht nach dem Schuss in 0,1 s eine Kammer weiter (Spannabzug; Destiny dreht beim '
                                         'Schuss, Zeit nicht gemessen); Gurt zieht in derselben Zeit eine Gliedteilung nach')


def index_frames(rpm):
    """Dauer eines Schritts in Bildern bei der Kadenz rpm (INDEX)."""
    return min(INDEX['frames'], INDEX['share'] * FPS * 60.0 / rpm) if rpm > 0 else INDEX['frames']


def index_level(fire, f, dur):
    """Schrittteil im Bild f einer Feueraktion: 0 vor dem ersten Schuss, nach dem letzten Schuss s ≤ f linear in dur Bildern auf 1."""
    last = None
    for s in fire or ():
        if s <= f:
            last = s
    if last is None:
        return 0.0
    return min(1.0, max(0.0, (f - last) / dur))


# ------------------------------------------------------------------ Wirkung der Waffen (0.34 „Payload“, Nutzerbefunde Testbuild 0.33)
# Was die Waffe in der Welt anrichtet: Einschläge (Funken, Staub, Loch), Projektile mit eigener Flugbahn, Strahlen, Bolzen, Explosionen.
# Nur Unity zeichnet die Welt (Blender rendert Waffe und Arme vor neutralem Grund), darum sind diese Werte Spielwerte wie gameplay; die
# Form der Effekte (Shader Ballon/Fx, Pools) steht in unity/Assets/Ballon/Runtime/WeaponFx.cs. Motiongen hat für Projektile, Strahlen
# und Schrot keine Flugzeit, keine Geschwindigkeit und kein Pelletmuster gemessen (destiny2 › Methode 16: „keine m/s und keine
# Reichweite“, Pelletmuster offen) – alle Zahlen hier sind E, Zeilen in der Entscheidungsliste (Schritt 9). Gemessen sind nur die
# Begleitwerte unten (src).
DECAL = dict(size_m=0.05, max=96, life_s=30.0, fade_s=2.5, variants=4, scorch_m=1.4, scorch_max=8,
             src='E: Loch 5 cm (seit Patch einschuss), dunkler Kern, heller aufgeworfener Rand, Rußhof; vier Formen (gedreht, Rand '
                 'unregelmäßig), nach 30 s in 2,5 s ausgeblendet, höchstens 96 (der älteste wird wiederverwendet); Explosion: Brandfleck 1,4 m')
# Einschläge: Funken (gestreckt, kurz), Staub bzw. dunkle Säule (dust_color, steigt mit dust_rise_mps), Lichtpunkt; je Stil.
# 0.34.1 „impact“: Zeiten und Farben nach REF 0.36 „Impact“ (Motiongen main d0181c7, einschlag.md › 7, einschlag.json › ballon_uebernahme); Größen (m) misst Impact nicht (E).
IMPACTS = dict(
    bullet=dict(sparks=9, spark_mps=6.0, spark_s=0.10, dust=4, dust_m=0.14, dust_s=0.30, dust_color='#150F0D', dust_rise_mps=0.9,
                glow_m=0.28, glow_s=0.03, decal='hole',
                src='M Funken 0,02–0,1 s, dunkle Säule (B : H ≈ 1 : 3–4) bis 0,25–0,3 s, #150F0D–#2A1D1A, Leuchten 1–2 Bilder '
                    '(IKELOS, Outbreak, Solemn Hymn; z-im-ikelos); Loch E (Destiny zeigt keins, Nutzerentscheid 180: behalten)'),
    heavy=dict(sparks=14, spark_mps=8.0, spark_s=0.10, dust=6, dust_m=0.20, dust_s=0.38, dust_color='#150F0D', dust_rise_mps=1.1,
               glow_m=0.42, glow_s=0.04, decal='hole',
               src='M Scharfschütze: Funken 0,1 s, Säule ≈ 0,38 s (Far Future, z-im-far-future); Handfeuerwaffe auf Wand nicht gemessen'),
    pellet=dict(sparks=3, spark_mps=5.0, spark_s=0.16, dust=1, dust_m=0.16, dust_s=0.5, dust_color='#8E9196', dust_rise_mps=0.0,
                glow_m=0.16, glow_s=0.06, decal='hole',
                src='E: je Schrotkugel (nur mit shot_impacts 0; seit 0.34.1 zeigt die Schrotflinte einen Einschlag je Schuss)'),
    shotgun=dict(sparks=28, spark_mps=5.0, spark_s=0.17, dust=3, dust_m=0.35, dust_s=0.5, dust_color='#101828', dust_rise_mps=0.4,
                 glow_m=0.55, glow_s=0.17, decal='hole',
                 src='M ein Einschlag je Schuss: Funkenball dicht ≈ 0,17 s, Funken bis ≈ 0,5 s, Rauchball ≈ 0,5 s, #F1EBFA/#101828 (Python, '
                     'Horseman; z-im-python, z-im-horseman); Nutzerentscheid 181'),
    energy=dict(sparks=8, spark_mps=4.5, spark_s=0.25, dust=2, dust_m=0.16, dust_s=0.38, dust_color='#150F0D', dust_rise_mps=0.9,
                glow_m=0.45, glow_s=0.12, decal='scorch',
                src='M lineare Fusion: Funkenkrone 0,25 s, Säule 0,35–0,4 s (Threaded Needle, z-im-threaded-needle); Brandfleck E'),
    arrow=dict(sparks=4, spark_mps=3.5, spark_s=0.25, dust=2, dust_m=0.16, dust_s=0.6, dust_color='#8E9196', dust_rise_mps=0.0,
               glow_m=0.20, glow_s=0.08, decal='scorch',
               src='E: Pfeil: kleiner Lichtpunkt in der Leuchtfarbe, wenig Staub; der Pfeil steckt stick_s (Destiny-Pfeil im Flug unsichtbar)'),
)
# Explosion je Art (0.34.2 „impact-nachtrag“, PAYLOAD explosion): Kern (flash_s), bildweiter Blitz (screen_s, screen_k = Deckung), Feuerkugeln,
# Druckring, Funken, Rauch, kurzes Licht; Lache (pool_s Dauer, pool_k Radius zum Explosionsradius, pool_hz aufsteigende Glut je Sekunde,
# pool_fade_s Ausblenden; 0 = keine); Größen mit radius_m der Klasse skaliert (E). Farbe leer = Leuchtfarbe der Waffe (Elementfarbe).
EXPLOSIONS = dict(
    rocket=dict(flash_s=0.17, flash_k=1.3, screen_s=0.025, screen_k=0.3, pool_s=0.0, pool_k=0.0, pool_hz=0.0, pool_fade_s=0.0, fire=10, fire_s=0.75, fire_k=0.75, ring_s=0.10, ring_k=0.9,
                sparks=40, spark_mps=14.0, spark_s=0.7, smoke=16, smoke_s=1.0, smoke_k=0.7, light_s=0.15, light_k=4.0,
                colors=dict(core='#FCECDE', fire='#E9B268', smoke='#020C08', ring='#FFE2B8', pool=''),
                src='M Rakete (Blue Shift, Hoosegow, Mos Epoch; REF 0.36 z-im-blue-shift): bildweiter Blitz 0,02–0,03 s getrennt vom Kern '
                    '0,12–0,22 s, Ring 0,07–0,13 s, Feuer 0,5–1,0 s, Rauch 0,75–1,2 s, Licht 0,15 s, Kern #FCECDE, Feuer #E9B268 → #CA774A, '
                    'Rauch #020C08; Deckung des Blitzes, Ringfarbe und Größen E'),
    grenade=dict(flash_s=0.125, flash_k=1.1, screen_s=0.0, screen_k=0.0, pool_s=5.6, pool_k=0.5, pool_hz=8.0, pool_fade_s=1.0, fire=5, fire_s=0.35, fire_k=0.55, ring_s=0.10, ring_k=0.8,
                 sparks=24, spark_mps=10.0, spark_s=0.4, smoke=0, smoke_s=0.0, smoke_k=0.0, light_s=0.15, light_k=3.0,
                 colors=dict(core='#EEFEFE', fire='#F3AF62', smoke='', ring='', pool=''),
                 src='M Granatwerfer (Velocity Baton, Chill Inhibitor, Witherhoard, Forbearance; REF 0.36 z-im-velocity-baton, '
                     'z-im-chill-inhibitor): Kern 0,12–0,13 s, kein bildweiter Blitz gemessen, kein Rauch; Kern #EEFEFE (Chill Inhibitor), '
                     'Ring in der Leuchtfarbe der Waffe (Element nicht gemessen). Feuerball: Destiny zeigt keinen (Elementeffekt) – '
                     'Nutzerentscheid 184 B: kleiner und kürzer als bei der Rakete (5 Kugeln, 0,35 s, × 0,55, #F3AF62 aus der Impact-Palette), '
                     'E; Lache ≈ 5,6 s nach dem Einschlag (REF 0.36 z-im-witherhoard, z-im-forbearance) als leuchtender Fleck in der '
                     'Leuchtfarbe mit aufsteigender Glut, nur auf Flächen (Nutzerwunsch 31.10.2026); Ring, Funken, Größen, Glut E'),
)
EXPLOSION = EXPLOSIONS['rocket']    # bis 0.34.1 eine gemeinsame Explosion (motion.payload.explosion, ältere Leser)
# Rauchschwaden aus der Mündung der Werfer nach dem Schuss (Viewmodel-Ebene, steigt und wird breiter)
MUZZLE_SMOKE = dict(rate_hz=9.0, puff_m=0.05, grow=3.0, rise_mps=0.10, life_s=1.3, color='#C9CCD1', alpha=0.35,
                    src='E: nach dem Schuss weiße Schwaden aus dem Rohr (Nutzerbefund 0.33; CoD MW .357: heller Rauchpuff vor dem Lauf, '
                        'Motiongen muendung › z-mf-cod-357)')
# Je Klasse (META type): Art der Wirkung und ihre Werte. kind: hitscan (Strahl ohne Flugzeit wie bisher), pellets (Streuschuss),
# projectile (Geschoss mit Flugbahn, Explosion), arrow (Pfeil mit Flugbahn), beam (Dauerstrahl), bolts (Bolzen je Schuss), rail
# (ein scharfer Strahl je Schuss), none. color '' = Leuchtfarbe der Waffe (erste Rolle von EGO_LIVE glow).
PAYLOAD_DEFAULTS = dict(kind='hitscan', impact='bullet', pellets=0, cone_deg=0.0, cone_ads=1.0, speed_mps=0.0, gravity_mps2=0.0,
                        life_s=0.0, radius_m=0.0, smoke_s=0.0, trail='', width_m=0.0, length_m=0.0, beam_s=0.0, stick_s=0.0,
                        muzzle_glow_m=0.0, muzzle_glow_s=0.10, color='', tracer_every=0, tracer_mps=0.0, tracer_m=0.0, tracer_w_m=0.0,
                        tracer_color='', trail_step_m=0.0, trail_life_s=0.0, scorch_every=1, spark_hz=0.0, shot_impacts=0, pulse_hz=6.0,
                        explosion='')
# explosion (0.34.2): Name in EXPLOSIONS (Granatwerfer grenade, Raketenwerfer rocket), leer = keine
# shot_impacts (0.34.1): sichtbare Einschläge je Schuss beim Streuschuss (0 = je Kugel); pulse_hz: Pulsen des Dauerstrahls
# Spur hinter Projektilen (trail_step_m Abstand der Ballen, trail_life_s ihre Dauer); Dauerstrahl: beam_s = Strahl hält nach dem letzten
# Takt, scorch_every = Brandfleck je n. Takt, spark_hz = Funken je Sekunde am Kontakt; muzzle_glow_s = Dauer des Mündungslichts
# Leuchtspur (hitscan): jeder tracer_every-te Schuss zeigt einen Strich (tracer_m lang, tracer_mps schnell) von der Mündung zum Einschlag
TRACER_MG = dict(tracer_every=3, tracer_mps=320.0, tracer_m=2.4, tracer_w_m=0.018, tracer_color='#FFC27A')
PAYLOAD = {
    'auto_rifle': dict(src='M keine Spur, Funken, kein Loch in Destiny (REF 0.36 z-im-solemn-hymn); Loch E (Nutzerentscheid 180)'),
    'submachine_gun': dict(src='M keine Spur, Funken + dunkle Säule (REF 0.36 z-im-ikelos); Loch E (Nutzerentscheid 180)'),
    'scout_rifle': dict(src='M keine Spur (REF 0.36 z-im-sauerstoff); Einschlag wie Kugel, Loch E (Nutzerentscheid 180)'),
    'pulse_rifle': dict(src='M keine Spur, Funken (REF 0.36 z-im-outbreak); Loch E (Nutzerentscheid 180)'),
    'sidearm': dict(src='M keine Spur, kein Loch sichtbar (REF 0.36 › 7 Fußnote 1); Einschlag auf Wand nicht gemessen; Loch E (180)'),
    'machine_gun': dict(TRACER_MG, src='E: Einschlag Kugel; Leuchtspur jeder 3. Schuss, 320 m/s, 2,4 m, warmweiß (BF6 B36A4: roter Strich '
                                         'zur Bildmitte ist Leuchtspur, Motiongen muendung › z-mf-bf6-b36a4; Destiny-MG in REF 0.36 nicht gemessen)'),
    'hand_cannon': dict(impact='heavy', src='M keine Spur, kein Loch sichtbar (REF 0.36 › 7 Fußnote 1); Einschlag schwer E, Loch E (180)'),
    'sniper_rifle': dict(impact='heavy', src='M keine Spur, Funken 0,1 s, Säule ≈ 0,38 s (REF 0.36 z-im-far-future); Loch E (180)'),
    'shotgun': dict(kind='pellets', impact='shotgun', pellets=12, cone_deg=3.0, cone_ads=0.75, shot_impacts=1,
                    src='S 12 Kugeln, feste Muster (Destiny 6.3.0); im Bild EIN Einschlag je Schuss (M, REF 0.36 z-im-python) → die Kugeln '
                        'treffen (Scheiben), gezeigt wird ein Einschlag mit einem Loch an der mittleren Kugel (Nutzerentscheid 181); Kegel 3,0° E'),
    'grenade_launcher': dict(kind='projectile', impact='explosion', explosion='grenade', speed_mps=42.0, gravity_mps2=7.0, life_s=4.0,
                             radius_m=3.0, smoke_s=0.2,
                             trail='grenade', width_m=0.045, length_m=0.07, trail_step_m=0.30, trail_life_s=0.0,
                             src='M Laufeffekt 0,05–0,2 s → 0,2 s (Nutzerentscheid 182), kein Schweif, Flug nah 0,17–0,22 s (REF 0.36 '
                                 'z-im-velocity-baton, z-im-chill-inhibitor); E: Granate 42 m/s mit Fallkurve (25 m: 0,6 s, 1,2 m Fall), '
                                 'Explosion Radius 3 m'),
    'rocket_launcher': dict(kind='projectile', impact='explosion', explosion='rocket', speed_mps=34.0, gravity_mps2=0.0, life_s=5.0,
                            radius_m=4.5, smoke_s=0.0,
                            trail='rocket', width_m=0.07, length_m=0.42, trail_step_m=0.18, trail_life_s=0.0,
                            src='M Glühpunkt ohne Rauchzopf, Flug 0,32–0,65 s (REF 0.36 z-im-blue-shift): Flamme am Heck, keine Rauchspur; '
                                'kein Rohrrauch sichtbar (REF 0.36 › 7; 0.34.2, vorher 2 s nach Nutzerwunsch 0.33); E: Rakete 34 m/s gerade '
                                '(15 m: 0,44 s), Explosion Radius 4,5 m'),
    'trace_rifle': dict(kind='beam', impact='energy', width_m=0.045, muzzle_glow_m=0.05, beam_s=0.15, scorch_every=3, spark_hz=40.0,
                        color='#D0D8FF', pulse_hz=12.0,
                        src='M Kern #D0D8FF, Rand #5060E0, Kontaktpunkt pulsiert 12/s (REF 0.36 z-im-agers); E: durchgehender Strahl 4,5 cm '
                            'vom Lauf zum Einschlag, solange der Abzug zieht; Destiny Prometheus Lens: Strahl ≈ 9–12 % B, Mündungslicht ≈ 8 %'),
    'fusion_rifle': dict(kind='bolts', impact='energy', speed_mps=110.0, width_m=0.05, length_m=2.5, muzzle_glow_m=0.06, muzzle_glow_s=0.07,
                         src='M Auslöseblitz ≈ 0,07 s; Destiny-Bolzen im Bild nicht sichtbar, [S] 5–9 je Salve (REF 0.36 z-im-tadel) – sichtbare '
                             'Bolzen bleiben (Nutzerwunsch 0.33, offen); E: je Strahl der Salve ein Bolzen 110 m/s, 2,5 m lang'),
    'linear_fusion_rifle': dict(kind='rail', impact='energy', width_m=0.035, beam_s=0.07, muzzle_glow_m=0.08,
                                src='M Schleier am Lauf 4 Bilder ≈ 0,07 s, kein fester Strahl (REF 0.36 z-im-threaded-needle) – hier ein Strahl '
                                    'für 0,07 s (Nutzerwunsch 0.33); Breite E'),
    'combat_bow': dict(kind='arrow', impact='arrow', speed_mps=70.0, gravity_mps2=4.0, life_s=3.0, stick_s=4.0, width_m=0.008, length_m=0.70,
                       muzzle_glow_m=0.05, trail_step_m=0.35, trail_life_s=0.18,
                       src='E: Pfeil 70 m/s mit leichter Fallkurve, steckt 4 s, Leuchtspur; beim Lösen ein Lichtpuls an der Auflage; Destiny '
                           'Imperial Needle: blauer Entladefächer 2 Bilder ≈ 22 % beim Lösen (destiny2 › z-ballista-imperial-needle), Pfeilfall '
                           'und Steckdauer offen'),
    'portal_cannon': dict(kind='none', impact='', src='Werkzeug: eigene Treffermarke in Portalfarbe (0.22), keine Wirkung'),
}


def payload(weapon_type):
    """Wirkung der Klasse (PAYLOAD mit PAYLOAD_DEFAULTS); unbekannte Klassen ohne Wirkung."""
    P = PAYLOAD.get(weapon_type, dict(kind='none', impact='', src='keine Wirkung (Klasse ohne Eintrag in PAYLOAD)'))
    return dict(PAYLOAD_DEFAULTS, **P)


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


# Bogen (0.33 P4): Teile des Auszugs (Modul w07: Ereignis draw) mit denselben Schlüsseln, Spannlicht erst bei vollem Auszug


def _bow_draw(*keys):
    k = list(keys)
    if k[0][1] < 1 <= k[-1][1]:                    # Spannen: Spannlicht 2 Bilder vor dem vollen Auszug an
        light = [(0, 0), (k[-1][0] - 2, 0), (k[-1][0], 1)]
    else:                                          # gespannt halten, entspannen: Licht aus, sobald der Auszug nachlässt
        light = [(f, 1.0 if v >= 1 else 0.0) for f, v in k]
    return {p: list(k) for p in ('arrow_shaft', 'string_top', 'string_bottom', 'cam_top', 'cam_bottom')} | {'draw_light': light}


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
        # Sprint wie die Automatik (lange Waffe, Gewehr); eigene Hüfte nach cubeescape-reference huefte.json (0.33, Abgleich aller Waffen)
        poses=dict(
            hip=dict(pos=(-0.136, -0.42, -0.181), aim=(-0.188, -3.414, -0.362), roll=9.9,
                     src='M cubeescape-reference huefte.json (Destiny 2, Mündung 57/65, 58/61, hintere Kimme 65/60, Visieröffnung 72/52 (Tone '
                         'Patrol, Call to Serve); Lage E: Ausgleichsrechnung gegen diese Werte (0.33, Abgleich aller Waffen; Nutzer 31.10.2026 '
                         '„Ja, nachziehen“ – bis dahin nur die Mündung eingestellt, das Visier lag 10–19 pp zu tief), gerechnet (Socket_Muzzle, '
                         'Socket_Sight bzw. Socket_Reticle, Socket_Hand) Mündung 57,5/63,2 %, Visier 68,4/56,0 %'),
        ),
        keep=dict(
            sprint='E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-Scout-Sprint nicht gemessen (Motiongen '
                   'destiny2 › Glidepath: kein Sprint-Clip)'),
        frames=dict(aim_in=9, aim_out=8, draw=22),
        frames_src='Nutzerentscheid 31.10.2026 („Neue Werte übernehmen“): Doom of Chelchis / Symmetry ADS ein 20 / 18, aus 16 / '
                   '17–18, Ziehen erstes Modellbild → ruhig 44 / 42 Bilder bei 60/s (Motiongen destiny2 › Gapfill) → aim_in 9 (19, '
                   'zwischen 17 → 7 und 20 → 10), aim_out 8 (17, wie Vorgabe 16 → 8), draw 22 (43 halbiert). Bis 0.33.1: Scout bei Destiny '
                   'nur grob gemessen: Tone Patrol ≈ 22 Bilder (0,37 s, Bestand, „vom Nachbartyp übertragen“), Patron of '
                   'Lost Causes 0,20–0,25 s = 12–15 Bilder [M] (Motiongen destiny2 › Glidepath, visiere › v-d2-scout); dazwischen und '
                   'zwischen Scharfschütze (15 Bilder bis ruhig) und Impuls (20) → E 17 Bilder bei 60/s erste Bewegung → Ruhe, am '
                   'Unity-Bild gemessen; aim_out M Destiny-Scout ADS aus → Hüfte 0,17 s (Dead Man\'s Tale, Motiongen auswertung › V04) '
                   '= 5 Bilder bei 30/s → aim_in 7, aim_out 5',
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
        # Kammer liegt weiter rechts; Hüfte seit 0.33 nach cubeescape-reference huefte.json (Visier 73–74/55 %)
        poses=dict(
            hip=dict(pos=(-0.183, -0.42, -0.18), aim=(0.066, -3.399, -0.43), roll=11.2,
                     src='M cubeescape-reference huefte.json (Destiny 2, Mündung 59/67, 58/64, Visier 73/55, 74/55); Lage E: Ausgleichsrechnung '
                         'gegen diese Werte (0.33, Abgleich aller Waffen; Nutzer 31.10.2026 „Ja, nachziehen“ – bis dahin nur die Mündung '
                         'eingestellt, das Visier lag 10–19 pp zu tief), gerechnet (Socket_Muzzle, Socket_Sight bzw. Socket_Reticle, Socket_Hand) '
                         'Mündung 58,4/65,5 %, Visier 73,4/55,2 %'),
            sprint=dict(pos=(-0.12, -0.34, -0.22), aim=(0.8, -1.8, -0.95), roll=-30,
                        src='M Motiongen REF 0.37 Verdict › C/G (z-v37-sprint, Die Abgenutzte Spitze): fast aus dem Bild gesenkt, Hülle '
                            'x 46–100 / y 66–100, Visier 56–65 / 67–80, Fadenkreuz „^“; Lage E. Bis 0.34 die Trageform der Automatik'),
        ),
        frames=dict(draw=23),
        frames_src='M Destiny-Anflug Automatik/Impuls/MG 20 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen Glidepath, Entscheidungsliste '
                   '4d; Gridskipper ADS ein 18 Bilder bis ruhig, Motiongen destiny2): aim_in 10 Bilder bei 30/s wie die Automatik; Ziehen '
                   'erstes Modellbild → ruhig Smite of Merain 44, Insidious 49, Outbreak 47–48 Bilder bei 60/s (Motiongen destiny2 › '
                   'Gapfill; Nutzerentscheid 31.10.2026) ≈ 47 → 23 (bis 0.33.1 Vorgabe 25)',
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
            hip=dict(pos=(-0.113, -0.441, -0.152), aim=(0.313, -3.407, -0.312), roll=12.0,
                     src='M cubeescape-reference huefte.json (Destiny 2, Mündung 57/63, 54/69, Kimme 64/66, 62/62, Griffhand 67/87, 67/89); Lage '
                         'E: Ausgleichsrechnung gegen diese Werte (0.33, Abgleich aller Waffen; Nutzer 31.10.2026 „Ja, nachziehen“ – bis dahin '
                         'nur die Mündung eingestellt, die Griffhand lag 9–12 pp zu tief), gerechnet (Socket_Muzzle, Socket_Sight bzw. '
                         'Socket_Reticle, Socket_Hand) Mündung 55,7/66,0 %, Kimme 63,4/63,4 %, Griffhand 66,7/89,9 % (Rollen 12° statt 13°: der '
                         'Unterarm in lowered lag an der Kante der Handgelenksklemme, Unity wich dort 0,204° ab)'),
            sprint=dict(pos=(-0.10, -0.36, -0.15), aim=(-0.02, -0.8, 1.6), roll=0,
                        src='M Destiny-Handfeuerwaffe Sprint: Waffe senkrecht, Lauf am oberen Rand, Körper 62–70 % B, hoch rechts (Motiongen '
                            'destiny2:562/467); Lage E, gerechnet Mündung 68,4/10,8 %, Körper 66–72 % B'),
            reload=dict(pos=(-0.07, -0.37, -0.10), aim=(0.5, -1.6, 0.7), roll=10,
                        src='M Destiny-Revolver: Hochdrehen 0,13 s, Trommel zur Kamera (Motiongen destiny2:492); Lage E: Mündung nach links oben, '
                            'linke Seite mit der ausgeschwenkten Trommel zeigt zur Kamera; 4 cm weiter weg als der erste Entwurf (Stützhand '
                            'verdeckte das halbe Bild); 0.34: 5 cm höher, damit das Trommelende und die fallenden Hülsen im Bild liegen. '
                            '0.35 (offen aus 0.34): Mündung weiter nach vorn gekippt (Lauf 41° statt 55° über der Waagerechten): die Rückseite '
                            'der Trommel, aus der die Hülsen fallen, zeigt zur Kamera (Kosinus 0,32 → 0,64, tools/bildlage.frame), Trommel '
                            '52/67 %, Mündung 47/30 %'),
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
                   (19, ('mag', (75, 0, 10))), (21, ('mag', (45, 0, 8))), (23, ('mag', (45, 0, 8))), (25, ('mag', (40, 0, 16))), (29, 'support'),
                   (36, 'support')],
                fL=[(0, 'underhand'), (3, 'open'), (4, 'pinch'), (6, 'mag_hold'), (9, 'open'), (11, 'relaxed'), (16, 'open'),
                    (19, 'mag_hold'), (24, 'open'), (29, 'underhand')],
                mech={'cylinder_latch': [(0, 0), (4, 0), (5, 1), (7, 1), (9, 0)], 'crane': [(0, 0), (5, 0), (7, 1), (22, 1), (24, 0)]},
                events=[(2, 'HandOff'), (7, 'MagOut'), (8, 'Eject'), (21, 'MagIn'), (24, 'Chamber'), (29, 'HandOn'), (33, 'Ready')],
                src='M Destiny-Revolver aus der Hüfte 1,0 s: Hochdrehen 0,13, Trommel 0,62, Schließen 0,2 s, Zähler bei ≈ 70 % (Motiongen '
                    'destiny2:492; älterer Clip Munition 1,4 s, ausgefedert 2,1 s, destiny2:119) → 36 Bilder, MagIn bei 21; Ablauf E '
                    '(Riegel mit dem Daumen der Stützhand, Kran ausschwenken, Auswerfen mit Hochreißen, Laden von vorn, Zuklappen mit '
                    'Handgelenkschwung); Hülsen beim Auswerfen nicht dargestellt (Entscheidungsliste). 0.35: die Stützhand lädt vor der '
                    'Trommel (45 mm vor dem Griff an der Trommelseite), damit sie die Trommel nicht verdeckt'),
        ),
        same_reload=True,
        recoil=dict(freq_hz=1.56, zeta=0.4, back_mps=0.5, pitch_dps=800.0, ads_pitch=0.2,
                    cam_freq_hz=0.94, cam_zeta=1.0, cam_dps=48.0, ads_cam=3.0,
                    src='M Motiongen REF 0.35 Backblast › E (z-bb-hc-rueckstoss, Annual Skate/Kindled Orchid, 60/s): Hüftschuss Spitze '
                        '+5…+10 Bilder (Median +7) mit ≈ +55° Kippen, Modell kommt zur Kamera, Unterschwingen bis +25…+32 (25–54 % der '
                        'Spitze), Rückkehr ≤ 1 pp bei +38…+47 → Feder 1,56 Hz, ζ 0,4: Spitze +7,7, Tiefpunkt +29, Nulldurchgang +42 '
                        'Bilder bei 60/s, Tiefe 25 % der Spitze; Kippen 800 °/s → ≈ 49° Spitze (E: etwas unter 55°, Visier bleibt '
                        'lesbar), zur Kamera 0,5 m/s → ≈ 3 cm (E). Zielen (› G, z-bb-hc-exotics, Lumina): Modell ≈ 10 pp hoch, ruhig '
                        'nach +28…+32 → ads_pitch 0,2 (≈ 10°, E). Kamera (Verdict › B/E2, z-v37-hc-kick): ≈ 22 pp H in 0,17 s, nach '
                        '0,40 s noch 14 pp → kritisch gedämpft 0,94 Hz (Spitze nach 1/ω = 0,17 s, bei 0,40 s 61 %); Hüfte 5–9 pp H [O] '
                        '→ 48 °/s ≈ 3°, im Zielen × 3,0 bei Weltzoom 1,15 ≈ 22 pp H („großen senkrechten Kick testen“, keine '
                        'Stabilitätsregel). Bis 0.34: gemeinsame Federn (5 Hz, ζ 0,5) mit Kick 2,5 ≈ 5° ohne sichtbares Unterschwingen'),
        gameplay=dict(rpm=140, magazine=10, path_up_h=0.017, kick=1.0,
                      src='S Annual Skate 140/min, Magazin 10 (Menü, Motiongen waffenwerte:283, destiny2:94; Rahmen 100–257/min, 8–16 Schuss); '
                          'gemessen Abstand 27 Bilder bei 60/s = 133/min „vereinbar“ (destiny2:94); Feuerart aus der Spec (Spannabzug, '
                          'ein Schuss je Zug); Bahnstufe 0,017 M: Netto-Rest vor dem Folgeschuss 1,7 pp H (Hochimpuls bis 7,6 pp, Motiongen '
                          'rueckstoss:106); Kick 1,0: die Federn stehen seit 0.35 als eigener Satz in recoil (bis 0.34 Kick 2,5)'),
        src='Ego-Übertrag 0.33 „Armory“ P1: Hüfte, Sprint, Anflug, Ziehen und Nachladen nach Motiongen (Handfeuerwaffe), Trommelablauf E'),
    'sidearm': dict(
        # Seitenwaffe (0.33, P1): Pistolengriff wie die Handfeuerwaffe, Magazin im Griff (Nachladen der Bezugsklasse mit Magazin unten),
        # Durchladen am Schlitten statt am Ladehebel (mech_map, charge_back_mm)
        poses=dict(
            hip=dict(pos=(-0.11, -0.448, -0.179), aim=(0.302, -3.401, 0.156), roll=6.0,
                     src='M cubeescape-reference huefte.json (Destiny 2, Mündung 57/64, 59/67, Visier 66/71, 66/73, Griffhand 67/87, 67/88); Lage '
                         'E: Ausgleichsrechnung gegen diese Werte (0.33, Abgleich aller Waffen; Nutzer 31.10.2026 „Ja, nachziehen“ – bis dahin '
                         'nur die Mündung eingestellt, die Griffhand lag 9–12 pp zu tief), gerechnet (Socket_Muzzle, Socket_Sight bzw. '
                         'Socket_Reticle, Socket_Hand) Mündung 58,0/65,5 %, Visier 65,8/71,5 %, Griffhand 66,0/96,3 % (Mündung, Visier und Griff '
                         'nicht zugleich: Griff 8 pp tiefer)'),
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
            sprint=dict(pos=(-0.32, -0.42, -0.27), aim=(0.6, -2.3, -0.05), roll=-20,
                        src='O Motiongen REF 0.37 Verdict › C/G (z-v37-sprint, Widerruf, eine Stelle): tief unten rechts, Hülle x 56–100 / '
                            'y 64–100, Längskante ≈ +22°, kein Fadenkreuz; 0.35: 4 cm weiter rechts, 1 cm tiefer (Hülle begann bei x 48). '
                            'Vorher: O cubeescape-reference destiny2 › Glidepath (Sprint): Scharfschütze „tief unten rechts“ (Sichtung, kein Wippen ≥ 3 '
                            'pp); eine ältere Zeile (destiny2:483) nennt bei 60/s eine höhere, mittigere Form – widersprüchlich, hier die '
                            'Glidepath-Sichtung. Lage E wie die Fusion (Trageform tief rechts), gerechnet Mündung 48/77 %, Visier rechts am Rand; '
                            'bis 0.33 die Automatik-Form (Mündung 19/86 %)'),
        ),
        frames=dict(aim_in=13, aim_out=12, draw=23),
        frames_src='M Destiny-Scharfschütze Far Future ADS ein 14 Bilder bei 60/s bis stabil (6 Hochziehen + 10 Overlay, Motiongen '
                   'destiny2:496) → 6 Bilder bei 30/s (Umrechnung mit dem Zielen-Nachlauf wie MP 8–12 → 3, Scout 17 → 7, Automatik 20 → 10); '
                   'ADS aus 0,17–0,25 s → 6 Bilder (0,20 s) – bis 0.33.1; Nutzerentscheid 31.10.2026: Gapfill Defiance of Yasmin / '
                   'Cloudstrike ein 25 / 27, aus 21 / 26–28 Bilder bei 60/s bis Ruhe → aim_in 13, aim_out 12 (über Automatik 20 → 10 hinaus '
                   'linear, 22 → 11); Ziehen erstes Modellbild → ruhig Defiance of Yasmin 41, Cloudstrike 47–53 Bilder '
                   'bei 60/s (Motiongen destiny2 › Gapfill, z-g34-kingsfall/-cloudstrike) ≈ 46 → 23 Bilder bei 30/s (wie MG 55 → 28)',
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
            hip=dict(pos=(-0.169, -0.424, -0.183), aim=(0.061, -3.415, -0.183), roll=10.9,
                     src='M Motiongen REF 0.35 Backblast › C (z-bb-neigung): Spurgewehr ohne Klassenmuster (Coldheart Fluchtpunkt 48/51, '
                         'Prometheus Lens 51,5/59 wie die Automatik); Nutzerbefund Testbuild 0.33 „Spurgewehr-Hüfte zu tief“ (31.10.2026). '
                         'Lage E (tools/bildlage.py --fit): Fluchtpunkt 45/50 wie die Automatik (44,7/48,7) statt 48,7/56,1, Mündung 58/61,2 %, '
                         'Visier 72,1/56,7 % (Gehäusenase unter 55 % H, A4). Bis 0.34: huefte.json-Ausgleich (Hollow Denial Mündung 57,7/59,6, Visier 66,9/45,6)'),
            sprint=dict(pos=(-0.19, -0.37, -0.23), aim=(1.4, -1.5, -0.10), roll=-15,
                        src='M Motiongen REF 0.37 Verdict › C/G (z-v37-sprint, schweres Spurgewehr Mikrokosmos): flach quer ganz unten, '
                            'Hülle x 29–100 / y 60–100, Oberkante +8–10°, Fadenkreuz „^“; Lage E. Bis 0.34 die Trageform der Automatik'),
        ),
        frames=dict(aim_in=4, aim_out=6, draw=17, reload_tactical=67),
        frames_src='M Destiny-Spurgewehr Prometheus Lens ADS ein ≈ 12 Bilder bei 60/s (Motiongen destiny2:592) → 4 Bilder bei 30/s (Umrechnung '
                   'wie Scharfschütze); Ager\'s Scepter ADS ein 13, aus 14 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen destiny2 › '
                   'Gapfill, z-g34-agers) → aus 6 (Umrechnung wie Scharfschütze 14 → 6); Ziehen erstes Modellbild → ruhig '
                   '34 Bilder → 17; Nachladen ≈ 1,6 s bis Hüfte, „kein Klassenwert“ (destiny2:512) × TIME_SCALE = 60 Bilder bis Hüfte '
                   '→ Bezugsablauf (Hüfte bei 45/50) auf 67 Bilder gestreckt',
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
        poses=dict(
            hip=dict(pos=(-0.182, -0.431, -0.185), aim=(0.273, -3.396, -0.185), roll=4.8,
                     src='M Motiongen REF 0.35 Backblast › C (z-bb-neigung): Fluchtpunkt der Laufachse beim MG quer links (Hammerhead −22/51, '
                         'Bitter End 31/46), die Waffe zeigt ihre Seite; Nutzerbefund Testbuild 0.33 „MG-Hüfte zu tief“ (31.10.2026). Lage E '
                         '(tools/bildlage.py --fit): Fluchtpunkt 40/50 statt 49,6/57,2 (Lauf waagerecht wie Automatik 44,7/48,7 und Fusion '
                         '43,2/51,6), Mündung 54,5/58,5 % (vorderes Ende in der erlaubten Ecke der Freihaltezone A4), Visier 77,7/53,9 %. Bis 0.34: huefte.json-Ausgleich (Shattered Cipher Mündung 56,1/55,1, '
                         'Optik 66/39,6; Hammerhead Mündung 56,2/64, Reflex 65,9/48,2) mit Lauf 7 pp unter die Mitte'),
            sprint=dict(pos=(-0.25, -0.40, -0.20), aim=(1.4, -1.8, -0.34), roll=-6,
                        src='M Motiongen REF 0.37 Verdict › C/G (z-v37-sprint, 21% Delirium): flach quer unten, Hülle x 38–100 / y 55–100, '
                            'Längskante 0…−2°, Fadenkreuz „^“; Lage E. Bis 0.34 die Trageform der Automatik (Hülle ab y ≈ 80)'),
        ),
        frames=dict(aim_out=11, draw=23),
        frames_src='M Destiny-MG ADS ein 20 Bilder bei 60/s (Motiongen destiny2:583) = Automatik (aim_in 10 bei 30/s); ADS aus Qullim\'s Terminus 21, '
                   'Thunderlord 23 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen destiny2 › Gapfill, z-g34-kingsfall/-thunderlord) ≈ 22 → 11 '
                   '(über lineare Fusion 19 → 10 und Automatik 20 → 10 hinaus; bis 0.33 Vorgabe 8); Ziehen 18 + 37 Bilder bei 60/s bis ruhig (wechsel:56) = 0,92 s → '
                   'bis 0.33.1 28 Bilder; Nutzerentscheid 31.10.2026: Gapfill Qullim\'s Terminus 50, Thunderlord 42 ≈ 46 → 23',
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
    'shotgun': dict(
        # Schrotflinte (0.33 „Armory“, P3): Vorderschaftrepetierer – nach jedem Schuss pumpt die Stützhand (Klassenaktionen fire_cycle aus
        # der Hüfte, fire_cycle_ads im Zielen; die Stützhand liegt auf der Pumpe und folgt ihr, Hülse beim Zurückziehen). Nachladen je
        # Patrone: reload_tactical (leer ebenso) ist der Einstieg mit der ersten Patrone, reload_shell lädt je eine weitere (Unity schleift
        # sie bis voll), reload_end führt zurück zur Hüfte, reload_end_pump nach leerem Beginn mit Pumpen. Ein Zug am Abzug bricht ab.
        # Die Patrone (Griff 'mag', Bauteil shell_round) kommt in der linken Hand von unter dem Bild (carry) und wird durch die Ladeklappe
        # geschoben (Bewegung load_shell: 1 = unter der Klappe, 0 = im Rohr, verdeckt)
        poses=dict(
            reload=dict(pos=(-0.09, -0.36, -0.16), aim=(0.55, -2.4, 0.25), roll=-60,
                        src='E nach Destiny-Schrotflinte (Einzelladen, Motiongen nachladen:52/53): Waffe vor dem Körper nach rechts gerollt, '
                            'Ladeklappe zeigt nach links unten zur Stützhand'),
            sprint=dict(pos=(-0.18, -0.32, -0.27), aim=(0.4, -1.3, -1.3), roll=-25,
                        src='M Motiongen REF 0.37 Verdict › C/G (z-v37-sprint, Python): Waffe fast ganz aus dem Bild, nur der Rand x ≥ 72 / '
                            'y ≥ 85, Fadenkreuz „^“; Lage E. Bis 0.34 die Trageform der Automatik'),
        ),
        keep=dict(
            hip='M Destiny-Schrotflinte Hüfte: Mündung FILO 57/63 (Motiongen huefte:54), ≈ 58/66 (destiny2:495); Lage E wie die Automatik: '
                'an der Schrotflinte gerechnet Mündung 58,4/64,1 %'),
        frames=dict(aim_in=10, aim_out=3, draw=27),
        frames_src='M Destiny-Schrotflinte FILO ADS ein ≈ 13 Bilder bei 60/s (Motiongen destiny2:588) → 5 Bilder bei 30/s (Umrechnung mit dem '
                   'Zielen-Nachlauf wie Spur 12 → 4, Scharfschütze 14 → 6); ADS aus 6–8 Bilder bei 60/s → 3; Ziehen 14 Bilder bei 60/s bis '
                   'hüftähnlich (wechsel:47) + Ausfedern E wie die Handfeuerwaffe (19) = 0,55 s → bis 0.33.1 17 Bilder; Nutzerentscheid '
                   '31.10.2026: The Fourth Horseman ADS ein 18–23 Bilder bei 60/s bis Ruhe → aim_in 10 (wie Automatik 20 → 10; aus geht '
                   'dort immer ins Nachladen, bleibt 3), erstes Modellbild → ruhig 54 Bilder (Motiongen destiny2 › Gapfill) → draw 27',
        actions=dict(
            fire_cycle=dict(
                de='Pumpen nach dem Schuss aus der Hüfte (Pumpe zurück, Hülse, vor)', frames=21,
                weapon=[(0, 'hip'), (11, 'hip'), (15, ('hip', dict(back=0.008, pitch=-1.5, roll=-2))),
                        (18, ('hip', dict(back=0.004, up=0.002, roll=-1))), (21, 'hip')],
                mech={'pump': [(0, 0), (11, 0), (16, 1), (17, 1), (20, 0)], 'bolt': [(0, 0), (11, 0), (16, 1), (17, 1), (20, 0)]},
                events=[(16, 'Eject'), (20, 'Chamber')],
                src='M Destiny-Schrotflinte: Pumpen vor dem zweiten Schuss, Hülse rechts 0,63 s nach dem Schuss (Motiongen destiny2:495) → Pumpe '
                    'hinten bei Bild 16–17 (0,55 s), vorn bei 20, Ende 21 (0,70 s) vor dem nächsten Schuss (80/min = 0,75 s); Ablauf E '
                    '(Stützhand auf der Pumpe, Waffe ruckt beim Zurückziehen leicht zurück)'),
            fire_cycle_ads=dict(
                de='Pumpen nach dem Schuss im Zielen (Waffe bleibt im Anschlag)', frames=21,
                weapon=[(0, 'ads'), (11, 'ads'), (15, ('ads', dict(back=0.005))), (18, ('ads', dict(back=0.002))), (21, 'ads')],
                mech={'pump': [(0, 0), (11, 0), (16, 1), (17, 1), (20, 0)], 'bolt': [(0, 0), (11, 0), (16, 1), (17, 1), (20, 0)]},
                events=[(16, 'Eject'), (20, 'Chamber')],
                src='E wie fire_cycle, im Zielen ohne Kippen (Kimme und Korn bleiben vor dem Auge, nur ein kleiner Ruck zurück)'),
            reload_tactical=dict(
                de='Nachladen: Einstieg mit der ersten Patrone (Waffe kippen, Patrone holen, durch die Ladeklappe schieben)', frames=18,
                weapon=[(0, 'hip'), (2, ('hip', dict(roll=-3, up=-0.004))), (6, 'reload'), (13, 'reload'),
                        (15, ('reload', dict(up=0.004, pitch=-1))), (18, 'reload')],
                L=[(0, 'support'), (2, 'support'), (6, OFF_L), (11, 'mag'), (14, 'mag'), (16, ('mag', (0, -25, 0))), (18, ('mag', (0, -25, 0)))],
                fL=[(0, 'underhand'), (3, 'open'), (6, 'pinch'), (14, 'pinch'), (16, 'open')],
                carry=[(6, 11)], mech={'shell_round': [(0, 0), (6, 0), (7, 1), (11, 1), (15, 0)]},
                events=[(2, 'HandOff'), (15, 'ShellIn')],
                src='M Destiny-Schrotflinte Einzelladen: erste Patrone 0,57–0,60 s nach Beginn (Motiongen nachladen:109) → ShellIn bei 15 von '
                    '18 Bildern (× TIME_SCALE: 0,63 s); Ablauf E (Stützhand verlässt die Pumpe, holt die Patrone unter dem Bild, schiebt sie '
                    'von unten durch die Ladeklappe); taktisch gegen leer nicht gemessen: ein Einstieg, nach leerem Beginn Pumpen am Ende'),
            reload_shell=dict(
                de='Nachladen: eine weitere Patrone (Unity wiederholt bis voll)', frames=19,
                weapon=[(0, 'reload'), (14, 'reload'), (16, ('reload', dict(up=0.004, pitch=-1))), (19, 'reload')],
                L=[(0, ('mag', (0, -25, 0))), (3, ('mag', (-10, -70, 10))), (7, OFF_L), (12, 'mag'), (15, 'mag'), (17, ('mag', (0, -25, 0))),
                   (19, ('mag', (0, -25, 0)))],
                fL=[(0, 'open'), (6, 'pinch'), (15, 'pinch'), (17, 'open')],
                carry=[(7, 12)], mech={'shell_round': [(0, 0), (7, 0), (8, 1), (12, 1), (16, 0)]},
                events=[(16, 'ShellIn')],
                src='M Destiny-Schrotflinte Einzelladen 0,617–0,633 s je Patrone (Hawthorne, Motiongen nachladen:52; Baligant 0,85–0,87, :53) → '
                    '19 Bilder (× TIME_SCALE 0,79 s); Ablauf E wie der Einstieg'),
            reload_end=dict(
                de='Nachladen: zurück zur Hüfte (voll oder durch Feuer abgebrochen)', frames=8,
                weapon=[(0, 'reload'), (6, 'hip'), (8, 'hip')],
                L=[(0, ('mag', (0, -25, 0))), (3, ('support', (0, -40, 0))), (6, 'support'), (8, 'support')],
                fL=[(0, 'open'), (4, 'open'), (6, 'underhand')],
                events=[(6, 'HandOn'), (8, 'Ready')],
                src='E: Rückweg kurz (0,33 s), damit ein Zug am Abzug während des Nachladens bald schießt (Destiny bricht das Einzelladen '
                    'mit Feuer ab, nicht gemessen)'),
            reload_end_pump=dict(
                de='Nachladen nach leerem Beginn: zurück zur Hüfte und pumpen', frames=16,
                weapon=[(0, 'reload'), (6, 'hip'), (10, ('hip', dict(back=0.008, pitch=-1.5, roll=-2))),
                        (13, ('hip', dict(back=0.004, up=0.002, roll=-1))), (16, 'hip')],
                L=[(0, ('mag', (0, -25, 0))), (3, ('support', (0, -40, 0))), (6, 'support'), (16, 'support')],
                fL=[(0, 'open'), (4, 'open'), (6, 'underhand')],
                mech={'pump': [(0, 0), (7, 0), (10, 1), (11, 1), (13, 0)], 'bolt': [(0, 0), (7, 0), (10, 1), (11, 1), (13, 0)]},
                events=[(6, 'HandOn'), (13, 'Chamber'), (16, 'Ready')],
                src='M Destiny-Schrotflinte: einmal Repetieren am Ende des Einzelladens (Motiongen nachladen:109); Ablauf E wie fire_cycle'),
        ),
        same_reload=True,
        gameplay=dict(rpm=80, magazine=6, path_up_h=0.03, recover_delay_s=0.2, recover_hz=3.0, kick=3.0,
                      src='S Hawthorne 80/min, Magazin 7 (Menü, Motiongen destiny2:258; Baligant 55/min, 5) → 80/min, Magazin 6 E (Röhrenmagazin '
                          'des Modells „hält sechs Patronen“); Feuerart aus der Spec (Pumpe: ein Schuss je Zug, danach fire_cycle); Bahnstufe '
                          '0,03 M: Ring 1–2 Bilder ≈ 3 % H hoch, nach 0,10 s zurück (destiny2:495) → Erholung E ab 0,2 s mit 3 Hz; Kick 3,0 E '
                          '(schwerer Einzelschuss wie der Scharfschütze)'),
        src='Ego-Übertrag 0.33 „Armory“ P3: Hüfte und Sprint der Automatik, Anflug und Ziehen nach Motiongen (Schrotflinte), Pumpen nach '
            'jedem Schuss und Einzelladen E nach den Destiny-Zeiten'),
    'fusion_rifle': dict(
        # Fusionsgewehr (0.33, P3): Aufladen → Salve. Abzug halten lädt in charge_s (Glutkern und Ladebalken leuchten mit der Ladung,
        # EGO_LIVE glow), bei voller Ladung schießt die Salve von selbst; Loslassen vorher bricht ab (Ladung fällt in charge_fade_s).
        # Gehalten Salve um Salve im Takt rpm. Nachladen der Bezugsklasse mit der Energiezelle (mech_map, leer wie taktisch)
        poses=dict(
            hip=dict(pos=(-0.17, -0.42, -0.215), aim=(0.10, -3.0, -0.25), roll=6,
                     src='M Destiny-Fusion Hüfte: Mündung 59/68 (Motiongen huefte:57), 58/66 (destiny2:499); Lage E, gerechnet Mündung '
                         '59,0/67,3 % (Automatik-Hüfte an der kurzen Fusion: 61,4/68,0), 2 cm weiter zur Mitte, 1,5 cm höher'),
            sprint=dict(pos=(-0.20, -0.38, -0.21), aim=(0.5, -2.4, -0.6), roll=-25,
                        src='O cubeescape-reference destiny2 › Glidepath (Sprint): Fusion „groß und tief, Körper ≈ 55–100 % × 62–100 %“ '
                            '(Sichtung). Lage E, gerechnet Mündung 58/79 %, Visier 91/68 %, Heck rechts aus dem Bild; bis 0.33 die Automatik-Form '
                            '(Mündung 34/89 %, Körper zu weit links)'),
        ),
        frames=dict(aim_in=7, aim_out=8, draw=23, reload_tactical=73),
        frames_src='M Destiny-Fusion ADS 0,083 s Achse, 0,117 s ruhig (Motiongen destiny2:499) = 7 Bilder bei 60/s → wie die MP 3 Bilder bei 30/s; '
                   'ADS aus nicht gemessen → E 2,4 (Verhältnis der MP) – bis 0.33.1; Nutzerentscheid 31.10.2026: Gapfill bis Ruhe '
                   'Jötunn / Gravitic Arrest / Midha / Deliverance ein 18–19 / 17 / 17 / 15 ≈ 17 → aim_in 7, aus 16–17 / 18 / 19 / 17 ≈ 17,5 '
                   '→ aim_out 8; Ziehen erstes Modellbild → ruhig Jötunn 48, Gravitic Arrest 44, Midha 49, Deliverance 40 '
                   '(Motiongen destiny2 › Gapfill) ≈ 45 → 23; Nachladen Batterie bis Hüfte 1,72–1,77 s, ruhig 1,92, sitzt +1,0 s (nachladen:54) '
                   '× TIME_SCALE = 65 Bilder bis Hüfte → Bezugsablauf (Hüfte bei 45/50) auf 73 Bilder gestreckt',
        mech_map=dict(mag_release='cell_release'),
        same_reload=True,
        gameplay=dict(rpm=60, magazine=7, charge_s=0.5, charge_fade_s=0.3, burst_shots=6, burst_rpm=1200, path_up_h=0.004, kick=0.6,
                      src='S Cartesian Coordinate Laden 500 ms, Magazin 7 (Menü, Motiongen destiny2:254), gemessen 0,517 s (destiny2:499); Salve '
                          '5–6 Strahlen in 0,25 s → 6 Schuss im Abstand 0,05 s (1200/min); Takt gehalten 60/min E (Aufladen 0,5 + Salve 0,25 + '
                          'Pause); Feuerart aus der Spec (Aufladen → Salve); Leuchten fällt in 0,3 s (Modul charge_fire: 9 Bilder); Bahnstufe '
                          '0,004 je Strahl E (Waffe ruhig, Mündung steigt über die Salve, destiny2:254/499), Kick 0,6 je Strahl E'),
        src='Ego-Übertrag 0.33 „Armory“ P3: Hüfte, Anflug, Aufladen und Nachladen nach Motiongen (Fusion), Sprint der Automatik, Nachladen der '
            'Bezugsklasse mit der Energiezelle (leer wie taktisch, kein Ladehebel)'),
    'linear_fusion_rifle': dict(
        # Lineare Fusion (0.33, P3): Aufladen → ein Schuss (wie die Fusion, ohne Salve; Linearkern leuchtet mit der Ladung). Nachladen der
        # Bezugsklasse mit der Energiezelle hinter dem Griff
        poses=dict(
            hip=dict(pos=(-0.204, -0.424, -0.228), aim=(0.025, -3.415, -0.28), roll=4.2,
                     src='M Motiongen REF 0.35 Backblast › C (z-bb-neigung): lineare Fusion Man O\' War Fluchtpunkt 46/56, lange Diagonale '
                         '+17…+21°; Nutzerbefund Testbuild 0.33 „LFR-Hüfte zu tief“ (31.10.2026). Lage E (tools/bildlage.py --fit): '
                         'Fluchtpunkt 45/52 (zwischen Automatik 44,7/48,7 und Man O\' War) statt 49,6/63,4, Mündung 58/65 % statt 57,9/68,5, '
                         'Visier 70,7/64,8 %. Bis 0.34: huefte.json-Ausgleich (Mündung 58/69, 58/68, Visier 73/57, 73/60)'),
        ),
        keep=dict(sprint='E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-lineare-Fusion-Sprint nicht gemessen '
                         '(Motiongen destiny2:569)'),
        frames=dict(aim_in=7, aim_out=10, draw=24, reload_tactical=99),
        frames_src='M Destiny-lineare-Fusion ADS ein 17 Bilder bei 60/s (Motiongen destiny2:591) → 7 Bilder bei 30/s wie der Scout; ADS aus 0,32 s '
                   '(destiny2:274) → 10; Ziehen 24 + 23 Bilder bei 60/s bis ruhig (wechsel:57) = 0,78 s → 24; Nachladen MagIn +1,53 s, ruhig '
                   '3,30 s (nachladen:61): Bezugsablauf so gestreckt, dass MagIn trifft (1,53 × 1,25 → Bild 57 von 99); ruhig damit nach '
                   '2,4 statt 3,3 s (Entscheidungsliste)',
        mech_map=dict(mag_release='cell_release'),
        same_reload=True,
        gameplay=dict(rpm=60, magazine=5, charge_s=0.563, charge_fade_s=0.2, path_up_h=0.065, recover_delay_s=0.25, recover_hz=1.5, kick=3.0,
                      src='S Laden 563 ms, Magazin 5 (Menü, Motiongen destiny2:274), sichtbar 20 Bilder bei 60/s [M]; Takt gehalten 60/min E; '
                          'Feuerart aus der Spec (Aufladen → Einzelschuss); Leuchten fällt in 0,2 s (Modul charge_fire: 6 Bilder); Bahnstufe '
                          '0,065 M: 6,5 pp H je Schuss (rueckstoss:111), Erholung langsam wie der Scharfschütze E; Kick 3,0 E'),
        src='Ego-Übertrag 0.33 „Armory“ P3: Hüfte, Anflug, Ziehen, Aufladen und Nachladen nach Motiongen (lineare Fusion), Sprint der '
            'Automatik, Nachladen der Bezugsklasse mit der Energiezelle'),
    'combat_bow': dict(
        # Bogen (0.33 „Armory“, P4): Spannen, Halten, Lösen (Feuerart draw_release). Abzug halten spielt die Klassenaktion fire_draw (aus der
        # Hüfte: Bogen kommt senkrecht hoch in die Haltung 'drawn', die Zughand zieht die Sehne zum Auge; im Zielen fire_draw_ads), am Ende
        # hält der volle Auszug, solange der Abzug zieht. Loslassen bei vollem Auszug löst (fire_release: Pfeil fliegt, Sehne schnellt vor,
        # der nächste Pfeil liegt gleich auf); halb gespannt fliegt ein schwacher Pfeil, die Nachladen-Taste entspannt ohne Schuss (let_down).
        # Kein Magazin (Vorrat unbegrenzt), kein Nachladen, kein Mündungsfeuer, keine Hülse. Wie Destiny hält die linke Hand den Bogen
        # (hands.swap: Griff grip links), die rechte Zughand (Griff 'support') hängt am Pfeil und folgt dem Auszug.
        poses=dict(
            hip=dict(pos=(-0.01, -0.61, -0.18), aim=(-0.01, -3.61, -0.18), roll=-80,
                     src='M cubeescape-reference huefte.json › hl-destiny-2-imperial-needle (Ultraclocked 0:47,000): linke Griffhand 46,6/84,8 %, '
                         'Visier 57,3/75,2 %, Bogen breit im unteren Bild (Körper 7,6–100 × 68,6–100 %), rechte Hand an der Nocke 49–64 × '
                         '91–100 %; destiny2:514 quer gekantet von links unten nach rechts oben, Pfeil zur Mitte. Lage E (Ausgleichsrechnung '
                         'gegen diese Werte, dann 3 cm nach rechts für die Freihaltezone A4), gerechnet Griff 50/84 %, Nocke 57/93 %, '
                         'Pfeilspitze 53/67 %, Ring 56/68 %, Wurfarme links unten und rechts oben aus dem Bild'),
            ads=dict(eye=(0.0, 0.27, 0.0), aim_dir=(0, -1, 0), roll=0,
                     src='M Destiny-Bogen Imperial Needle im Zielen (Bilder aus Ultraclocked dKNTDzi__Qo 47,75/48,3/67,7 s, Cache '
                         'CubeEscape/reference/visiere; cubeescape-reference destiny2:105 Ring 50/57, zielbewegung: Zoom 2,2×): Blick durch den '
                         'Ring, der Riser direkt rechts daneben, die Pfeilspitze unter dem Ring, Wurfarme über die volle Bildhöhe, linke Hand '
                         'unten Mitte; der Ring ist ≈ 9 % B groß. Lage E: der Bogen steht 27 cm näher an der Kamera als der Ankerpunkt des vollen '
                         'Auszugs (Socket_Eye 23 cm hinter dem Auge, Sehne und Zughand hinter der Kamera; Nutzer 30.10.2026: „beim Bogen ist das '
                         'Visier näher am Bild“; mit 23 cm ≈ 6 % B im Bildvergleich), gerechnet Ring 50/50 % mit Ø 52 mm in 0,41 m ≈ 9,8 % B'),
            drawn=dict(pos=(-0.001, -0.477, -0.159), aim=(-0.001, -3.477, -0.159), roll=-65,
                       src='M Motiongen REF 0.35 Backblast › D (z-bb-bogen-huefte): die Pfeilachse zeigt in allen Phasen durch die Bildmitte '
                            '(acht Bögen, Schnitt bei y = 50: x 47,7–51,4), voll gespannt 61–75° im Bild; Nutzerbefund Testbuild 0.33 '
                            '„Hüftzielen zeigt nach rechts, Schuss geht daneben“: bis 0.34 lag der Fluchtpunkt bei 67,4/39,6. 0.35 E '
                            '(tools/bildlage.py --fit): Fluchtpunkt 50/50, Pfeilspitze 52,7/65,7, Nocke 58,5/99,4 (Achse im Bild 73°). Vorher M Destiny-Bogen Imperial '
                           'Needle gespannt aus der Hüfte (Bild Ultraclocked dKNTDzi__Qo 45,3 s): weiter quer '
                           'gekantet, etwas gehoben, Ring ≈ 57/64 %, linke Hand unten ≈ 47/89 %, oberer Wurfarm rechts aus dem Bild, Zughand '
                           'nicht sichtbar (andere Bögen stehen dabei rechts senkrecht, destiny2:221). Lage E (Ausgleichsrechnung), gerechnet '
                           'Griff 50/88 %, Ring 57/64 %, voller Auszug hinter der Kamera'),
            sprint=dict(pos=(-0.14, -0.38, -0.13), aim=(0.4, -2.6, -0.28), roll=-75,
                        src='M Motiongen REF 0.35 Backblast › D/E2 (z-bb-bogen-sprint, vier Bögen): flach quer rechts unten, Neigung '
                            '−9…−28° (meist −15…−24°), Oberkante 45–70 % H, Hülle 13–27 %; Nutzerbefund Testbuild 0.33 „Bogen-Sprint zu '
                            'hoch“. Lage E. Bis 0.34 (O destiny2:221): Riser hoch rechts, Griff 69/61 %'),
            inspect_l=dict(pos=(-0.06, -0.52, -0.14), aim=(1.6, -1.2, 0.0), roll=-60,
                           src='E: Bogen 1 m hoch – Betrachten weiter weg als die Gewehre, Visierseite zur Kamera (gerechnet Ring 50/59 %); '
                               'Destiny hat keinen Ego-Inspect'),
            inspect_r=dict(pos=(-0.10, -0.52, -0.14), aim=(-0.6, -1.4, 0.2), roll=60,
                           src='E: rechte Seite mit dem Pfeil, Wurfarme quer aus dem Bild (gerechnet Pfeilspitze 71/43 %, Griff 63/81 %)'),
        ),
        drop=dict(poses=('reload',), actions=('fire_hip', 'fire_ads', 'reload_tactical', 'reload_empty', 'reload_to_switch'),
                  src='Bogen ohne Magazin (Vorrat): kein Nachladen; Feuer als Klassenaktionen fire_draw/fire_release/let_down statt fire_hip/fire_ads'),
        ads_hand=dict(off=OFF_L, src='E: im ungespannten Zielen hängt die Zughand unter dem Bild (an der Nocke, 0,42 m vor dem Auge, lag der rechte '
                                      'Arm groß rechts im Bild); sie kommt beim Spannen an die Nocke (fire_draw_ads)'),
        ads_strip=False,   # 193 B: der Bogen bleibt im Zielen ganz (Destiny: Riser und Wurfarme über die volle Höhe, 6,0–6,8 %; BALLON 9,9 %)
        ads_hide=dict(parts=('arrow_nock', 'fletch_top', 'fletch_l', 'fletch_r', 'string_top', 'string_bottom'),
                      src='M Motiongen REF 0.35 Backblast › D (z-bb-bogen-ads): Pfeil senkrecht unter dem Visierpunkt, Spitze 16–22 pp tiefer. Seit '
                          '0.35 liegt der Pfeil 69,5 mm unter der Visierlinie (Visier über dem Pfeil): der Schaft ist eine schmale Linie von der '
                          'Spitze bis an den unteren Bildrand (≤ 2,7 % B) und bleibt sichtbar; Nocke und Federn sind im Zielen aus (ungespannt '
                          'lägen sie unten in der Mitte, gespannt hinter der Kamera), ebenso die Sehne (sie liegt in der Ebene der Visierlinie: '
                          'ungespannt ein Strich senkrecht durch den Ring, gespannt zwei Striche von oben bis vor die Kamera). Bis 0.34 (Seitenvisier 60 mm neben dem Pfeil) war auch '
                          'der Schaft aus'),
        hands=dict(swap=True, src='M Destiny: Bogenhand links, Zughand rechts (die Sehnenhand liegt beim Halten rechts unten ≈ 85/95 %, '
                                  'cubeescape-reference destiny2:221/231); Daten: in allen Aktionen tauschen L und R (Griff grip = Bogengriff '
                                  'links, support = Zughand rechts an der Nocke), Bildpunkte unter dem Bild gespiegelt (Nutzerhinweis 30.10.2026: '
                                  '„Muss der Bogen nicht in der anderen Hand gehalten werden?“)'),
        frames=dict(aim_in=6, aim_out=5, draw=14),
        frames_src='M Destiny-Bogen: Zielen gespannt 0,25 s (Motiongen destiny2:270/508) → 6 Bilder bei 30/s (Umrechnung mit dem Zielen-Nachlauf '
                   'wie Scharfschütze 14 B60 → 6), aus E 5; Ziehen 6–8 Bilder bei 60/s bis hüftähnlich (wechsel:48/50) + Ausfedern E → 14 '
                   '(wie die Seitenwaffe)',
        actions=dict(
            fire_draw=dict(
                de='Spannen aus der Hüfte (Bogen senkrecht, Sehne zum Auge)', frames=18,
                weapon=[(0, 'hip'), (4, 'drawn'), (18, 'drawn')],
                L=[(0, 'support'), (18, 'support')], fL=[(0, 'pinch')],
                mech=_bow_draw((0, 0), (4, 0), (18, 1)), events=[(18, 'FullDraw')],
                src='S/M Destiny-Bogen Imperial Needle Ziehzeit 612 ms, Anlegen → voll ≈ 0,60 s (cubeescape-reference destiny2:271) → voll bei '
                    'Bild 18 (wie das Modul: Spannzeit 0,60 s); Heben 0,1 s, dann Ziehen (destiny2:231), senkrecht in 4 Bildern (destiny2:185); '
                    'Spannlicht bei vollem Auszug (Modul draw_hold_release)'),
            fire_draw_ads=dict(
                de='Spannen im Zielen (Ring kommt von unten, die Pfeilspitze bleibt ruhig)', frames=18,
                weapon=[(0, 'ads'), (4, ('ads', dict(up=-0.055))), (18, 'ads')],
                L=[(0, OFF_L), (5, 'support'), (18, 'support')], fL=[(0, 'relaxed'), (3, 'open'), (5, 'pinch')],
                mech=_bow_draw((0, 0), (4, 0), (18, 1)), events=[(18, 'FullDraw')],
                src='M Motiongen REF 0.35 Backblast › D/E2 (z-bb-bogen-ads): beim Spannen bleibt die Spitze ruhig (≤ 2 pp), der Ring kommt '
                    'von rechts unten (55,8/68,4 → 50/57,3 in 0,4 s). Lage E: der Bogen senkt sich vor dem Auszug um 55 mm (Ring 67 %) und '
                    'steigt mit dem Auszug zurück; so wandert die Spitze von Bild 4 bis 18 nur 66,6 → 67,8 % (1,2 pp, tools/bildlage.frame; '
                    'mit 65 mm stünde sie still, aber der Bogen verließe die Ausblendgrenze ADS_HIDE 6 cm und die Sehne spränge ins Bild). Ring nur von unten, nicht von rechts '
                    '(E: ein seitlicher Versatz bewegte die Spitze mit). Bis 0.34: Bogen bleibt im Anschlag, Spitze wanderte 9 pp'),
            draw_aim_in=dict(
                de='Gespannt ins Zielen (Bogen dreht senkrecht vor das Auge, bleibt gespannt)', frames=5,
                weapon=[(0, 'drawn'), (5, 'ads')], L=[(0, 'support'), (5, 'support')], fL=[(0, 'pinch')],
                mech=_bow_draw((0, 1), (5, 1)), events=[(5, 'Aimed')],
                src='M cubeescape-reference destiny2:271: ADS mit gespanntem Bogen, Bogen dreht in ≈ 15 Bildern bei 60/s (0,25 s) senkrecht, '
                    'Ring und Pfeilspitze mittig → 5 × TIME_SCALE = 7 Bilder bei 30/s'),
            draw_aim_out=dict(
                de='Gespannt aus dem Zielen (seitlich, bleibt gespannt)', frames=3,
                weapon=[(0, 'ads'), (3, 'drawn')], L=[(0, 'support'), (3, 'support')], fL=[(0, 'pinch')],
                mech=_bow_draw((0, 1), (3, 1)), events=[(3, 'Ready')],
                src='M cubeescape-reference destiny2:252: ADS-Verlassen ist kein Spannabbruch, 5 Bilder bei 60/s (0,083 s) bis zur seitlichen '
                    'gezogenen Form → 3 × TIME_SCALE = 4 Bilder'),
            fire_release=dict(
                de='Lösen aus der Hüfte (Pfeil fliegt, Bogen ruckt nach rechts unten, neuer Pfeil liegt auf)', frames=10,
                weapon=[(0, 'drawn'), (2, ('drawn', dict(back=0.012, pitch=-5, roll=-4, right=0.015, up=-0.03))),
                        (5, ('drawn', dict(up=-0.04, right=0.02, roll=-6))), (10, 'hip')], fire=[0],
                L=[(0, 'support'), (1, 'nock'), (4, ('nock', (-40, 20, -30))), (8, 'support'), (10, 'support')],
                fL=[(0, 'pinch'), (1, 'open'), (7, 'pinch')],
                mech=dict(_bow_draw((0, 1), (2, 0)), arrow_shaft=[(0, 1), (1, -0.5), (3, -6), (6, -6), (6, 0)], draw_light=[(0, 1), (1, 0)]),
                events=[(0, 'Release'), (6, 'Nocked'), (10, 'Ready')],
                src='M cubeescape-reference destiny2:231: Lösen → gespannt 0,60 s (0,23 s Fall/Schwingen, 0,10 s Heben, 0,25 s Ziehen), beim '
                    'Lösen kippt der Bogen ≈ 15 % H nach rechts unten, der nächste Pfeil liegt gleich auf; destiny2:271 Bogen federt und senkt '
                    'sich 0,35 s → 10 Bilder bis zur Hüfte; Pfeil fliegt in 3 Bildern aus dem Bild (danach weit vorn), Sehne in 2 Bildern vor'),
            fire_release_ads=dict(
                de='Lösen im Zielen (zugleich aus dem Zielen, neuer Pfeil liegt auf)', frames=10,
                weapon=[(0, 'ads'), (1, ('ads', dict(up=-0.05, pitch=-7, right=0.01))), (4, ('drawn', dict(up=-0.04, right=0.02, roll=-6))),
                        (10, 'hip')], fire=[0],
                L=[(0, 'support'), (1, 'nock'), (4, ('nock', (-40, 20, -30))), (8, 'support'), (10, 'support')],
                fL=[(0, 'pinch'), (1, 'open'), (7, 'pinch')],
                mech=dict(_bow_draw((0, 1), (2, 0)), arrow_shaft=[(0, 1), (1, -0.5), (3, -6), (6, -6), (6, 0)], draw_light=[(0, 1), (1, 0)]),
                events=[(0, 'Release'), (6, 'Nocked'), (10, 'Ready')],
                src='M cubeescape-reference destiny2:105: Lösen mit gleichzeitigem ADS-Ausstieg, Ringmitte ≈ 30 pp H nach unten im ersten '
                    'Lösungsbild (50/57 → 53/87); Unity zielt danach wieder, wenn Rechtsklick gehalten bleibt; Ablauf sonst wie fire_release'),
            let_down=dict(
                de='Entspannen ohne Schuss (Nachladen-Taste beim Spannen)', frames=4,
                weapon=[(0, 'drawn'), (2, ('hip', dict(roll=-45, up=-0.05, right=0.02))), (4, 'hip')],
                L=[(0, 'support'), (4, 'support')], fL=[(0, 'pinch')],
                mech=_bow_draw((0, 1), (3, 0)), events=[(4, 'Ready')],
                src='M cubeescape-reference destiny2:253: Spann-Reset ohne Schuss 9 Bilder bei 60/s (0,150 s), der Bogen rollt nach rechts in eine '
                    'fast waagerechte tiefe Haltung, der Pfeil bleibt; „Use while drawn to cancel the shot“ (Nachladen-Taste) → 4 × TIME_SCALE = '
                    '5 Bilder; Unity blendet vom erreichten Auszug über'),
            let_down_ads=dict(
                de='Entspannen ohne Schuss im Zielen', frames=4,
                weapon=[(0, 'ads'), (2, ('hip', dict(roll=-45, up=-0.05, right=0.02))), (4, 'hip')],
                L=[(0, 'support'), (4, 'support')], fL=[(0, 'pinch')],
                mech=_bow_draw((0, 1), (3, 0)), events=[(4, 'Ready')], src='E wie let_down, aus dem Zielen'),
        ),
        gameplay=dict(rpm=60, magazine=0, path_up_h=0.0, kick=1.5, muzzle_flash=False,
                      src='Feuerart aus der Spec (draw_release: Spannen, Halten, Lösen); kein Magazin (Vorrat, magazine 0 = unbegrenzt, Motiongen '
                          'destiny2:270); Takt E 60/min (begrenzt nicht: Lösen, Auflegen und Spannen dauern 1,3 s, Destiny Lösen → Lösen 1,45 s); '
                          'keine Bahnstufe (die Welt steigt nicht, der Bogen ruckt), Kick 1,5 E (Wurfarme-Ruck, destiny2:498); kein '
                          'Mündungsfeuer, keine Hülse'),
        src='Ego-Übertrag 0.33 „Armory“ P4: Hüfte, Spannhaltung, Sprint und Zeiten nach Motiongen (Bogen Imperial Needle), Ablauf E'),
    'grenade_launcher': dict(
        # Granatwerfer (0.33 „Armory“, P4): Trommel mit sechs Kammern (Spec v2.1 semi_auto, Nutzerwahl „Trommel statt Kipplauf“). Nach jedem
        # Schuss dreht die Trommel eine Kammer weiter (Klassenaktion fire_cycle). Nachladen je Kammer wie die Schrotflinte: reload_tactical
        # (Klappenknopf, Ladeklappe auf, Hülse fällt, erste Granate) ist der Einstieg, reload_shell lädt je eine weitere (Unity bis voll),
        # reload_end schließt die Klappe; ein Zug am Abzug bricht ab. Ladefolge (0.35): vor jeder Granate dreht die Trommel eine Kammer
        # zurück (Gegendrehung, bringt die nächste leere Kammer an die Klappe), beim Schließen eine Kammer vor – die Kammern liegen danach in
        # Schussfolge, auch nach einem abgebrochenen Nachladen. Die Granate (Griff 'mag', Bauteil grenade) kommt in der linken Hand
        # von unter dem Bild und wird von hinten in die Ladekammer geschoben; die Hülse fällt beim Marker Eject (Modul EJECT on='reload')
        poses=dict(
            hip=dict(pos=(-0.17, -0.42, -0.22), aim=(0.10, -3.0, -0.14), roll=6,
                     src='M Destiny-Granatwerfer Hüfte: Mündung ≈ 58/67 (Motiongen destiny2:509), 56/63 (huefte:68); Lage E, gerechnet Mündung '
                         '60/64 % (Automatik-Hüfte am Werfer: 62/66), 2 cm weiter zur Mitte, 1 cm höher'),
            reload=dict(pos=(-0.12, -0.43, -0.19), aim=(0.9, -2.0, 0.20), roll=-50,
                        src='E: Waffe vor dem Körper nach rechts gerollt, die Ladeklappe hinten links zeigt zur Kamera; 6 cm weiter weg als der '
                            'erste Entwurf (der linke Unterarm an der Granate deckte die linke Bildhälfte, Still 0.33 P4)'),
        ),
        keep=dict(sprint='E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-Granatwerfer-Sprint nicht gemessen '
                         '(Motiongen destiny2:571)'),
        frames=dict(aim_in=5, aim_out=6, draw=22),
        frames_src='M Destiny-Granatwerfer ADS ein ≈ 12 Bilder bei 60/s (Motiongen destiny2:593; 19 B60 destiny2:271) → 5 Bilder bei 30/s '
                   '(Umrechnung wie Schrotflinte 13 → 5); ADS aus Chill Inhibitor 25 Bilder bei 60/s bei ein 22 (Motiongen destiny2 › '
                   'Gapfill, z-g34-vesper; die anderen gehen ins Nachladen) → Verhältnis aus/ein 1,14 auf aim_in 5 → 6; Ziehen erstes '
                   'Modellbild → ruhig Chill 54, Velocity Baton 28, Forbearance 46, Witherhoard 39–52 → Mittel ≈ 43 → 22',
        actions=dict(
            fire_cycle=dict(
                de='Trommel eine Kammer weiter nach dem Schuss (Hüfte)', frames=9,
                weapon=[(0, 'hip'), (9, 'hip')], mech={'drum': [(0, 0), (2, 0), (8, 1), (8, 0)]}, events=[(8, 'Chamber')],
                src='E wie das Modul (fire: Trommel 60° in 6 Bildern, danach zurück – sechsfache Teilung); 0,3 s vor dem nächsten Schuss '
                    '(90/min = 0,67 s)'),
            fire_cycle_ads=dict(
                de='Trommel eine Kammer weiter nach dem Schuss (Zielen)', frames=9,
                weapon=[(0, 'ads'), (9, 'ads')], mech={'drum': [(0, 0), (2, 0), (8, 1), (8, 0)]}, events=[(8, 'Chamber')],
                src='E wie fire_cycle'),
            reload_tactical=dict(
                de='Nachladen: Einstieg (Klappe auf, Hülse fällt, erste Granate von hinten einschieben)', frames=26,
                weapon=[(0, 'hip'), (2, ('hip', dict(roll=-3, up=-0.004))), (7, 'reload'), (20, 'reload'),
                        (22, ('reload', dict(up=0.005, pitch=-1.5))), (26, 'reload')],
                L=[(0, 'support'), (2, 'support'), (5, 'gate'), (7, 'gate'), (9, ('gate', (-30, -20, 25))), (12, OFF_L), (14, OFF_L),
                   (19, ('mag', (-90, 0, 0))), (21, 'mag'), (23, ('mag', (-30, 0, 15))), (26, ('mag', (-60, -20, 20)))],
                fL=[(0, 'underhand'), (3, 'open'), (5, 'pinch'), (8, 'open'), (12, 'mag_hold'), (23, 'open')],
                drop=(11, 11), carry=[(14, 21)],
                mech={'gate_button': [(0, 0), (5, 0), (6, 1), (8, 1), (9, 0)], 'load_gate': [(0, 0), (6, 0), (10, 1), (26, 1)],
                      'drum': [(0, 0), (6, 0), (10, -1), (10, 0)]},
                events=[(2, 'HandOff'), (10, 'GateOpen'), (11, 'Eject'), (21, 'ShellIn')],
                src='M Destiny-Granatwerfer: Granate ein +0,69 s, Schließen +1,17, Hüfte +2,42 s (Motiongen destiny2:271/509, Einzellader) → '
                    'ShellIn bei 21 von 26 Bildern (× TIME_SCALE 0,88 s); Ablauf E nach dem Modul (reload: Klappenknopf, Klappe, je Kammer '
                    'Hülse aus, Granate ein); Trommel-Nachladen bei Destiny nicht gemessen. 0.35: Gegendrehung beim Öffnen (6–10) statt Weiterdrehen '
                    'nach dem Einlegen (offen aus 0.34: die geladenen Kammern lagen nach teilweisem Nachladen nicht in Schussfolge)'),
            reload_shell=dict(
                de='Nachladen: eine weitere Granate (Unity wiederholt bis voll)', frames=22,
                weapon=[(0, 'reload'), (16, 'reload'), (18, ('reload', dict(up=0.005, pitch=-1.5))), (22, 'reload')],
                L=[(0, ('mag', (-60, -20, 20))), (3, OFF_L), (6, OFF_L), (14, ('mag', (-90, 0, 0))), (16, 'mag'), (18, ('mag', (-30, 0, 15))),
                   (22, ('mag', (-60, -20, 20)))],
                fL=[(0, 'open'), (4, 'mag_hold'), (18, 'open')],
                drop=(1, 1), carry=[(6, 16)],
                mech={'load_gate': [(0, 1), (22, 1)], 'drum': [(0, 0), (2, 0), (6, -1), (6, 0)]},
                events=[(1, 'Eject'), (16, 'ShellIn')],
                src='E wie der Einstieg (Trommel eine Kammer zurück, Hülse aus, Granate holen und einschieben), 22 Bilder (× TIME_SCALE 0,92 s) '
                    'je Kammer; 0.35 Gegendrehung vor dem Einlegen statt Weiterdrehen danach'),
            reload_end=dict(
                de='Nachladen: Klappe zu, zurück zur Hüfte (voll oder durch Feuer abgebrochen)', frames=10,
                weapon=[(0, 'reload'), (8, 'hip'), (10, 'hip')],
                L=[(0, ('mag', (-60, -20, 20))), (2, ('gate', (40, -30, 0))), (4, ('gate', (40, -30, 0))), (8, 'support'), (10, 'support')],
                fL=[(0, 'open'), (6, 'underhand')],
                mech={'load_gate': [(0, 1), (2, 1), (4, 0)], 'drum': [(0, 0), (4, 0), (7, 1), (7, 0)]},
                events=[(4, 'GateClosed'), (7, 'Chamber'), (8, 'HandOn'), (10, 'Ready')],
                src='E: Klappe mit der Stützhand zuschlagen, Rückweg kurz wie die Schrotflinte (ein Zug am Abzug soll bald schießen); 0.35: '
                    'nach dem Schließen dreht die Trommel eine Kammer vor (die zuletzt geladene Kammer in den Lauf)'),
        ),
        same_reload=True,
        gameplay=dict(rpm=90, magazine=6, path_up_h=0.04, recover_delay_s=0.2, recover_hz=1.7, kick=2.5, flash_scale=0.9,
                      src='S Destiny-Granatwerfer 90/min (Motiongen destiny2:271-272, Einzellader mit Magazin 1); Magazin 6 E (Trommel des Modells, '
                          'Spec v2.1 semi_auto); Feuerart aus der Spec (Einzelfeuer, danach dreht die Trommel); Bahnstufe 0,04 E: Waffe schlägt '
                          'hoch zur Kamera, Rückkehr ≈ 0,6 s (destiny2:509) → Erholung ab 0,2 s mit 1,7 Hz; Kick 2,5 E; Blitz 0,9 E (die '
                          'D-Linse W1 lag bei 20,3 % > 20 %, 5.3 A)'),
        src='Ego-Übertrag 0.33 „Armory“ P4: Hüfte, Anflug und Ladezeiten nach Motiongen (Granatwerfer), Sprint der Automatik, Trommel und '
            'Nachladen je Kammer E nach dem Modul'),
    'rocket_launcher': dict(
        # Raketenwerfer (0.33 „Armory“, P4): Einzelschuss (Spec single_shot), Magazin 1. Nach jedem Schuss lädt Unity sofort nach (Klassenaktion
        # reload_tactical, leer ebenso). 0.35 „Stance“ (Backblast › B): der Werfer kippt quer (Rohr nach rechts oben), die Ladeklappe springt
        # auf, die linke Hand holt die nächste Rakete von links oben und senkt sie von oben in den Schacht (Griff 'mag' auf der Rakete, 'push'
        # drückt sie in den Sitz), drückt die Klappe zu ('cap', folgt der Klappe) und verriegelt am Klappenknopf ('charge'); die rechte Hand
        # bleibt am Griff
        poses=dict(
            hip=dict(pos=(-0.190, -0.418, -0.118), aim=(-0.190, -3.414, -0.273), roll=0,
                     src='M Motiongen REF 0.35 Backblast › A/E2 (z-bb-rl-huefte, vier Werfer) und REF 0.37 Verdict (Todbringer 68–70/64–72): '
                         'großer Keil rechts von oben bis unten, Optik mit der Spitze zur Mitte x 63–70 / y 48–72, Oberkante −27…−42°, '
                         'Mündung und Rohrachse nicht im Bild; Nutzerbefund Testbuild 0.33 „Raketenwerfer über die Schulter“. Lage E '
                         '(tools/bildlage.py --fit): Rohr rechts neben dem Kopf auf Augenhöhe, Heck neben der Kamera (Socket_Breech in 2 cm '
                         'Tiefe; Etappe 2: 3 mm weiter nach rechts, Freihaltezone A4 15 → 0 px), Fluchtpunkt 50/56 – „leicht nach unten“ (Nutzer) ist in Destiny nicht belegt (E, 6 pp wie die Automatik), Mündung '
                         '63,5/54 %, Visier 68,5/51,7 % (Optik ab 60 % B, A4). Bis 0.34: huefte.json (Hoosegow: Körper 60–100 × 0–100 %, Optik 65/68; Blue Shift: Körper 60–100 × '
                         '17–100 %, Optik 68/57) und destiny2:501 (Mündung ≈ 60/40): das Rohr steht rechts über die volle Bildhöhe, vorn oben, '
                         'das Heck rechts unten unter dem Arm – nicht auf der Schulter (bis zum Abgleich aller Waffen mit huefte.json, 0.33 P4). '
                         'Lage E (Ausgleichsrechnung, dann 5 cm nach rechts: das Rohr lag bis 56 % B in der Freihaltezone, A4; Destiny-Körper '
                         'ab 60 % B; dann 1 cm weiter für die letzte Pixelspalte, 127 → 0 px), gerechnet Mündung 63,8/41,5 %, Visier 73,0/62,5 %, '
                         'Rohr 13° steigend, Heck rechts unten unter dem Arm'),
            sprint=dict(pos=(-0.16, -0.36, -0.28), aim=(0.3, -2.4, -1.3), roll=-20,
                        src='E: Destiny-Raketenwerfer-Sprint nicht gemessen (Motiongen destiny2:572); Rohr von der Schulter gesenkt, Mündung '
                            'nach vorn unten'),
            reload=dict(pos=(0.129, -0.544, -0.201), aim=(-2.526, -1.585, 0.704), roll=-40,
                        src='M Motiongen REF 0.35 Backblast › B/E2 (z-bb-rl-nachladen, vier Legendary): Werfer quer, Rohr nach rechts oben '
                            '(obere Kante −14…−28°), Schacht auf der Oberseite bei x 44–53 / y 47–75, Optikende links unten. Lage E (Ausgleich '
                            'mit tools/bildlage.frame): Ladeklappe 51/59 % in 0,49 m, Oberkante steigt 21° nach rechts, Schacht zur Kamera '
                            'gekippt (cos 0,74), Mündung 80/45 %, Visier 30/68 %; der Griff liegt bei BALLON hinter dem Schacht und damit '
                            'links unten (34/93 %, Destiny 80–98 / 70–95: E, der Griff BGM-1 sitzt 154 mm hinter der Schachtmitte). '
                            'Bis 0.34: Rohr quer, Mündung nach rechts aus dem Bild, Heck links (Laden von hinten)'),
        ),
        frames=dict(aim_in=15, aim_out=16, draw=27),
        frames_src='M Motiongen REF 0.37 Verdict › D/G (z-v37-rl-gjallarhorn): Gjallarhorn ADS ein / aus 15 / 16 echte Bilder bei 30/s '
                   '(0,50 / 0,53 s) → aim_in 15, aim_out 16 (Umrechnung wie Automatik 20 B60 → 10: gleiche Dauer); Ziehen nach Wechsel bis '
                   'ruhig 0,90 s mit Überschwingen −11,5 / +16,7 pp (Gjallarhorn) bzw. 0,30 s ohne (Todbringer, O) → draw 27 E: der '
                   'schwere Werfer schwingt mit dem Feder-Nachlauf nach wie Gjallarhorn. Bis 0.34: aim_in 6 (Destiny 14 B60, destiny2:594), '
                   'aim_out 5 E, draw 14 (0,18 s bis Hüfte, destiny2:481)',
        actions=dict(
            reload_tactical=dict(
                de='Nachladen nach dem Schuss (Werfer quer, Ladeklappe auf, Rakete von oben in den Schacht, Klappe zu, verriegeln)',
                frames=70,
                weapon=[(0, 'hip'), (3, ('hip', dict(back=0.02, pitch=3))), (13, 'reload'), (26, ('reload', dict(up=0.004))),
                        (29, ('reload', dict(up=-0.008))), (32, 'reload'), (36, ('reload', dict(up=-0.005))), (40, 'reload'), (44, 'reload'),
                        (58, ('hip', dict(up=-0.004))), (70, 'hip')],
                L=[(0, 'support'), (4, 'support'), (11, OFF_TL), (22, ('mag', (0, 60, 0))), (25, 'mag'), (28, 'mag'), (30, 'push'),
                   (32, ('push', (0, 30, 0))), (34, ('cap', (0, 25, 0))), (36, 'cap'), (40, 'cap'), (43, 'charge'), (45, 'charge'),
                   (47, ('charge', (0, 10, 25))), (56, 'support'), (70, 'support')],
                fL=[(0, 'foregrip'), (5, 'open'), (11, 'mag_hold'), (28, 'mag_hold'), (30, 'open'), (41, 'open'), (43, 'pinch'), (47, 'open'),
                    (54, 'foregrip')],
                drop=(0, 1), carry=[(11, 25)],
                mech={'rocket': [(0, 0), (1, 0.25), (25, 0.25), (28, 0.04), (30, 0)],
                      'load_hatch': [(0, 0), (4, 0), (10, 1), (33, 1), (36, 0.3), (40, 0)],
                      'cap_release': [(0, 0), (43, 0), (44, 1), (45, 1), (46, 0)], 'ready_light': [(0, 1), (1, 0), (44, 0), (48, 1)]},
                events=[(0, 'Launch'), (4, 'HandOff'), (10, 'BreechOpen'), (30, 'MagIn'), (40, 'BreechClosed'), (45, 'Chamber'),
                        (56, 'HandOn'), (58, 'Ready')],
                src='M Motiongen REF 0.35 Backblast › B/G, E2 (z-bb-rl-nachladen, z-bb-rl-zeiten): Start → ruhig 2,6–3,0 s (Hoosegow 3,00 s '
                    'in Normaltempo, Blue Shift 3,03, Mos Epoch 2,73), „im Schacht“ 0,5–1,2 s nach dem Start → 70 Bilder (× TIME_SCALE '
                    '2,92 s), Rakete im Schacht bei 30 (1,25 s), Klappe zu 40, verriegelt 45, ruhig 70. Ablauf nach Backblast › B: quer '
                    'kippen, linke Hand bringt die Rakete von links oben und senkt sie von oben ein, Druck von oben, Klappe, Werfer dreht '
                    'zurück; die Klappe springt nach dem Schuss selbst auf (E). Die Rakete verlässt das Rohr im Schussbild (danach '
                    'ausgeblendet, Unity fliegt das Geschoss). Bis 0.34: 84 Bilder (3,5 s), Heckklappe, Rakete von hinten'),
        ),
        same_reload=True,
        ads_hide=dict(parts=('rear_tube', 'tube_cone', 'rear_ring', 'hinge_block', 'breech_cap', 'cap_rim', 'shoulder_rest'),
                      src='M Motiongen REF 0.35 Backblast › F (z-bb-bildanteil): Destiny-Werfer im Zielen nur am rechten Rand (Hoosegow x 81–100, '
                          '16,6–16,8 %); Nutzerentscheid 194 (31.10.2026): BALLON-Zielbild nicht mehr 50 %. Das Heckrohr läuft neben dem Auge '
                          '33 mm an der Kamera vorbei – Heckrohr, Kegel, Heck und Schulterauflage sind im Zielen aus (Regel ADS_HIDE wie beim '
                          'Zielfernrohr); Startrohr, Visier, Griffe bleiben. Allein gemessen 50,1 → 50,4 % (das Startrohr läuft zur Mitte); '
                          'mit ADS_STRIP (Nutzer „So wie Destiny“, Startrohr bis auf die Mündung aus) 11,2 %'),
        gameplay=dict(rpm=20, magazine=1, path_up_h=0.0, recover_hz=1.5, kick=4.0, flash_scale=0.7,
                      src='S Destiny-Raketenwerfer 20/min, Magazin 1 (Motiongen destiny2:276); Feuerart aus der Spec (Einzelschuss, danach sofort '
                          'nachladen); keine Bahnstufe, Kick 4,0 E: Schub zur Kamera, Linse 10 → 25 % H in 3–4 Bildern (destiny2:501); '
                          'Mündungsfeuer 0,7 der Familie E (das Seitenvisier W2 liegt nah am Rohr: mit 1,0 deckte der Blitz 33,6 % der Öffnung, '
                          'Regel ≤ 20 %, 5.3 A; Destiny-Weißblende 0,10–0,15 s offen)'),
        src='Ego-Übertrag 0.33 „Armory“ P4: Schulterhaltung, Anflug, Ziehen und Nachladezeit nach Motiongen (Raketenwerfer), Ablauf E'),
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
              'continuous_beam': 'Dauerstrahl (Dauerfeuer ohne Mündungsfeuer, Leuchtteile EGO_LIVE glow an, solange der Abzug zieht)',
              'pump_action': 'Vorderschaftrepetierer (ein Schuss je Zug, danach Pumpe als Klassenaktion fire_cycle/fire_cycle_ads; Nachladen '
                             'je Patrone reload_shell, ein Zug am Abzug bricht ab)',
              'charge_burst': 'Aufladen → Salve (Abzug halten lädt in charge_s, bei voller Ladung burst_shots Schuss; Loslassen bricht ab; '
                              'gehalten Zyklus um Zyklus im Takt rpm)',
              'charge_single': 'Aufladen → Einzelschuss (wie charge_burst mit einem Schuss)',
              'draw_release': 'Bogen (Abzug halten spannt – Klassenaktion fire_draw/fire_draw_ads –, voller Auszug hält, Loslassen löst – '
                              'fire_release/fire_release_ads –, vorher entspannt der Bogen ohne Schuss – let_down/let_down_ads)',
              'single_shot': 'Einzelschuss mit Magazin 1 (ein Schuss je Zug, danach sofort Nachladen als Klassenaktion reload_tactical)'}
# Feuerarten mit einem Schuss je Zug (Abzug je Schuss gezogen und gelöst; ego_build und Unity EgoData.Semi)
SEMI_MODES = ('semi_auto', 'single', 'bolt_action', 'pump_action', 'single_shot')
# Feuerarten mit Aufladen (0.33): gameplay.charge_s/charge_fade_s, Leuchtteile folgen der Ladung (charge_level, Unity EgoData.Charge)
CHARGE_MODES = ('charge_burst', 'charge_single')


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
    if (fire_mode in ('burst', 'charge_burst')) != ('burst_rpm' in C['gameplay']):
        raise KeyError(f'{wid}: Salve braucht burst_rpm in der Klasse {t} (und nur sie)')
    if (fire_mode in CHARGE_MODES) != ('charge_s' in C['gameplay']):
        raise KeyError(f'{wid}: Aufladen braucht charge_s in der Klasse {t} (und nur sie)')
    if fire_mode == 'charge_burst':                  # Salvenlänge der Ladewaffe aus der Klasse (die Spec nennt nur charge_burst)
        burst = C['gameplay']['burst_shots']
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
    SR = ads_strip_rule(W, C)
    if 'ads' in poses and SR and SR.get('back_m'):   # 0.35 (193 B): Kamera im Zielen hinter Socket_Eye, je Klasse
        e = poses['ads']['eye']
        poses['ads'] = dict(poses['ads'], eye=(e[0], round(e[1] - SR['back_m'], 6), e[2]),
                            src=poses['ads']['src'] + f" · 0.35 Nutzerentscheid 193 B: Kamera {SR['back_m'] * 1000:.0f} mm hinter Socket_Eye "
                                                      f"(ego.ADS_STRIP_CLASS)")
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
    if 'ads_hand' in C:                              # Stützhand im Zielen frei (Bogen, 0.33 P4): in den Bezugsaktionen, die ins Zielen führen
        off = C['ads_hand']['off']
        for k, A in actions.items():
            if k in C.get('actions', {}) or 'ads' not in [w[1] if isinstance(w[1], str) else w[1][0] for w in A['weapon']]:
                continue
            ws = [(f, w if isinstance(w, str) else w[0]) for f, w in A['weapon']]
            a_in = next(f for f, w in ws if w == 'ads')                          # erstes Bild im Zielen
            a_out = max((f for f, w in ws if w != 'ads' and f > a_in), default=None)
            L = A.get('L', [(0, 'support')])
            if a_out is None:                                                    # endet im Zielen: Hand geht unter das Bild
                A['L'] = [k_ for k_ in L if k_[0] < a_in * 0.6] + [(round(a_in * 0.6, 6), 'support'), (a_in, off)]
            else:                                                                # beginnt im Zielen (aim_out): Hand kommt an die Nocke
                A['L'] = [(0, off), (a_out, 'support')]
            A['fL'] = [(f, p) for f, p in A['fL'] if f < a_in * 0.6] + [(a_in, 'relaxed')] if a_out is None else [(0, 'relaxed'), (a_out, A['fL'][-1][1])]
    if C.get('hands', {}).get('swap'):               # Bogenhand links (Bogen, 0.33 P4): L und R tauschen, Bildpunkte gespiegelt (x links)
        def mirror(keys, default):
            return [(f, ('cam', (-k[1][0],) + tuple(k[1][1:])) if isinstance(k, tuple) and k[0] == 'cam' else k) for f, k in keys or default]
        for A in actions.values():
            L, R = A.get('L', [(0, 'support')]), A.get('R', [(0, 'grip')])
            fL, fR = A['fL'], A.get('fR', [(0, 'trigger')])
            A['L'], A['R'] = mirror(R, None), mirror(L, None)
            A['fL'], A['fR'] = fR, fL
    gpose = grips['grip'].get('fingers_pose', 'trigger')
    if gpose != 'trigger':                           # Haupthand ohne Abzugsfinger (Bogen, 0.33 P4): Fingerstellung des Griffs statt trigger
        ch = 'fL' if C.get('hands', {}).get('swap') else 'fR'
        for A in actions.values():
            A[ch] = [(f, gpose if p == 'trigger' else p) for f, p in A.get(ch, [(0, 'trigger')])]
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
    G['ads_hide_arms'] = bool(ads_strip_rule(W, C) and ads_strip_rule(W, C)['arms'] and 'ads' in poses)   # 193 B
    recoil = dict(RECOIL, **C.get('recoil', {}))  # Rückstoßfedern je Klasse (0.35, Handfeuerwaffe: Kippen und Unterschwingen), sonst RECOIL
    recoil.pop('src', None)
    if 'recoil' in C:                           # nur Klassen mit eigenem Satz tragen ihn im Export (gameplay.recoil, Unity RecoilOr)
        G['recoil'] = recoil
    for A in actions.values():
        if A.get('fire') and G['kick'] != 1.0:
            A['kick'] = G['kick']
    if burst:
        G['burst_shots'] = burst                  # Salvenlänge aus der Spec (META fire burst_N)
    rpm = G['rpm']
    for k, A in actions.items():                # Schussbilder der Feueraktionen in der Kadenz der Klasse (Clips wie Unity: gameplay.rpm)
        if not A.get('fire') or k in C.get('actions', {}):
            continue
        if fire_mode == 'draw_release':           # Bogen (0.33 P4): geschossen wird nur in fire_release (Klassenaktion), sprint_to_fire ohne Schuss
            A.pop('fire')
            A.pop('kick', None)
            A['src'] = f"{A['src']}; Klasse {t}: ohne Schuss (Bogen: Spannen beginnt nach dem Marker Fire)"
            continue
        if fire_mode in CHARGE_MODES:             # Ladewaffe (0.33): Abzug ab dem ersten Schussbild der Bezugsaktion, Schüsse nach dem Aufladen
            A['fire'] = shots_charge(A['fire'][0], A['frames'], G['charge_s'] * FPS, rpm, burst or 1, G.get('burst_rpm', 0))
            A['de'] = A['de'].replace('Dauerfeuer', 'Aufladen und Salve' if burst else 'Aufladen und Schuss')
        elif burst:
            A['fire'] = shots_burst(A['fire'][0], A['fire'][-1], burst, G['burst_rpm'], rpm)
            A['de'] = A['de'].replace('Dauerfeuer', 'Salven')
        elif rpm != 720:
            A['fire'] = shots_at(A['fire'][0], A['fire'][-1], rpm)
        else:
            continue
        A['src'] = f"{A['src']}; Klasse {t}: {rpm}/min, {FIRE_MODES[fire_mode]} (Schussbilder {A['fire']})"
    live = getattr(W, 'EGO_LIVE', None) or LIVE
    P = dict(type=t, poses=poses, actions=actions, grips=grips, live=live, gameplay=G, src=C['src'],
             frames_src=C.get('frames_src', ''), fire_mode=fire_mode, drop=drop, recoil=recoil,
             mag=grips.get('mag', {}).get('part', 'magazine'),   # Bauteil, das das Nachladen trägt (carry/drop): Magazin, Energiezelle (0.33)
             hands_swap=bool(C.get('hands', {}).get('swap')),     # Bogenhand links (0.33 P4)
             ads_hide=tuple(dict.fromkeys(tuple(C.get('ads_hide', {}).get('parts', ())) +   # je Klasse (0.33 P4, Bogen)
                                          (ads_strip_parts(W, C) if 'ads' in poses else ()))))   # Zielbild wie Destiny (0.35, 193 B)
    _PROFILES[wid] = P
    return P
