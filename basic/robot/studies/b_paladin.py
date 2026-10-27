"""Studie B „Paladin“: athletisch (Prinzipien Q-D2-PARADE, nur Prinzipien).

V-Rumpf: breite Brust mit Pfeilschnitt zur schmalen, offenen Taille (Wirbelringe über dem dunklen Anzug), Hüfte bei halber Höhe,
große runde Schulterpanzer mit zweiter Lage über dem Oberarm, Helm mit Kamm tief im Kragen, lange Lendenplatte, Platten nur vorn
und hinten (dunkle Seiten sichtbar). Technik mittel bis hoch: Kniekolben in der Kniekehle, Halsleitungen, Leitung am Oberschenkel,
Gürtelmodule. Arme: Oberarm v3 bleibt, nur die Schulterkugel kommt dazu.
"""
from . import body as B

SK = B.skeleton(dict(
    waist=(0, 0, 1050), neck=(18, -16, 1452), pelvis=(20, 0, 866), head_h=262, head_off=(-10, 6),
    torso_hint=(0.18, -1, 0), head_hint=(0.4, -1, 0), shoulder=(262, 0, 306),
    hip_x=108, hip_z=40, thigh=418, shin=400, foot_h=104,
    ankles={'R': (-160, -80), 'L': (132, 10)}, toes={'R': (-224, -232), 'L': (168, -150)},
    knee_pole={'R': (-0.3, -1, 0), 'L': (0.1, -1, 0)}))
globals().update(SK)

ARM_BULK = 1.22
ARM_DROP = ('upper_shell',)        # Oberarm dunkel und schlank (Q-D1-TITAN)
POSES = {'idle': dict(upper=(-0.2, 0.03, -1.0), fore=(-0.04, -0.3, -1.0))}


def arm_extra():
    return B.upper_arm(dict(ball=56))


def head():
    return B.head(dict(style='mil', h=256, a=104, b=108, n=2.6, hz=1.16, neck=42, ear='out', crest=True, neck_cables=True))


def upper_body():
    return B.torso(dict(
        core=[(90, 120, 92, -2), (180, 158, 108, 0), (250, 194, 118, -4), (300, 204, 112, -6), (350, 176, 100, -8), (395, 120, 84, -10)],
        core_ch=42, waist=(80, 64), abdomen='vribs', lights=True, gorget=(380, 136, 104, 14), bridges=(168, 360, 190, 16),
        collar=[(370, 130, 96, -10), (418, 100, 84, -8), (436, 90, 78, -8)],
        chest=dict(a=(-80, 80), full=200, tip=112, mid=(262, 316), top=360, t=11, plate=240, emblem=True, vents=(320, 332, 344), vent_x=118),
        back=dict(kind='plate', z=(150, 220, 360)),
        SX=262, SZ=306, joint_r=54,
        pauldron=dict(n=2.8, rows=[(224, 102, 120, -6, 44), (274, 118, 132, -6, 32), (329, 116, 128, -6, 12), (374, 104, 116, -6, -2),
                                   (400, 66, 80, -6, -14)],
                      flare=[(154, 110, 126, -6, 52), (230, 98, 112, -6, 44)], flare2=[(96, 98, 114, -6, 58), (170, 88, 104, -6, 50)], flare_span=100, band=250, med=(244, 24), stripes=True, tilt=22, ch=42,
                      grooves=(294, 308))))


def lower_body():
    return B.pelvis(dict(
        pel=[(-20, 128, 88, -2), (60, 140, 92, -2), (140, 112, 80, -2), (196, 90, 70, -2)], belt=(126, 152, 116, 84),
        front=dict(full=10, tip=-170, a=28), side=dict(rows=[(-100, 204, 108, -4), (-10, 172, 100, -4), (120, 150, 94, -4)], span=26, center=82),
        hip_x=108, hip_z=40, hip_r=46, butt=True, belt_boxes=True, pel_ch=30))


def legs():
    return B.legs(dict(
        LT=418, LS=400, foot_h=104, thigh_ch=24, shin_ch=22, knee_ch=20,
        thigh=[(-12, 70, 76, 0), (120, 86, 92, 2), (290, 76, 80, 0), (418, 60, 64, 0)], thigh_shell=(-70, 60), thigh_seams=(210,),
        thigh_cable=True,
        knee_r=52, kneecap=[(-66, 56, 62), (-20, 66, 72), (36, 68, 74), (82, 60, 66)], knee_pistons=True,
        shin=[(30, 66, 70, 0), (150, 76, 84, -6), (300, 62, 66, -2), (400, 54, 56, 0)], shin_shell=(-84, 84),
        calf=True, lights=True, ankle_r=36,
        foot=[(-96, 60, 40, -62), (-28, 66, 52, -52), (70, 66, 44, -60), (160, 60, 30, -72), (220, 48, 20, -82)]))
