"""Studie C „Mechanik“: schlank-mechanisch (Prinzipien des Zielbilds robot-concept, nur Prinzipien).

Offenes Skelett: schmaler Graphitkörper, Platten einzeln aufgesetzt (zwei Brustplatten mit Linse dazwischen, Schulterblattplatten,
Oberschenkel- und Schienbeinplatten nur vorn), offene Wirbelsäule mit blanken Wirbeln, kompakte runde Schulterpanzer, große
Kniegelenke, Kameralinse an der Schläfe. Technik hoch: Kolben an Taille, Schulter, Hals, Oberschenkel, Oberarm und Wade,
Leitungen an Hals und Oberschenkel, Antenne.
"""
from . import body as B

SK = B.skeleton(dict(
    waist=(0, 0, 1070), neck=(16, -16, 1470), pelvis=(18, 0, 905), head_h=250, head_off=(-10, 6),
    torso_hint=(0.16, -1, 0), head_hint=(0.4, -1, 0), shoulder=(244, 0, 310),
    hip_x=100, hip_z=36, thigh=430, shin=420, foot_h=106,
    ankles={'R': (-150, -80), 'L': (122, 10)}, toes={'R': (-206, -226), 'L': (150, -150)},
    knee_pole={'R': (-0.3, -1, 0), 'L': (0.1, -1, 0)}))
globals().update(SK)

ARM_BULK = 1.12
ARM_DROP = ('upper_body', 'upper_shell')
POSES = {'idle': dict(upper=(-0.16, 0.03, -1.0), fore=(-0.04, -0.3, -1.0))}


def arm_extra():
    return B.upper_arm(dict(rows=[(10, 50, 48, 0), (150, 54, 52, 0), (290, 44, 42, 0)], ball=52, shell=(-80, 80), piston=True, ch=16))


def head():
    return B.head(dict(style='mil', h=250, a=88, b=100, n=2.6, hz=1.1, neck=36, ear='lens', neck_pistons=True, neck_cables=True, antenna=True))


def upper_body():
    return B.torso(dict(
        core=[(60, 100, 78, -2), (160, 136, 96, 0), (240, 166, 106, -4), (290, 176, 102, -6), (340, 150, 92, -8), (390, 100, 78, -10)],
        core_ch=34, waist=(66, 54), abdomen='spine', rings=(-30, -2, 26), waist_pistons=True, shoulder_pistons=True, lights=True, gorget=(370, 118, 92, 12),
        collar=[(360, 112, 86, -10), (410, 88, 76, -8), (428, 78, 70, -8)],
        chest=dict(a=(-74, 74), full=130, mid=(200, 260, 318), top=356, t=9, split=True, stripe=290),
        back=dict(kind='spine'),
        SX=244, SZ=310, joint_r=50,
        pauldron=dict(rows=[(258, 84, 98, -6, 30), (298, 96, 108, -6, 20), (348, 90, 102, -6, 4), (378, 66, 80, -6, -8),
                            (392, 34, 44, -6, -16)], band=284, med=(270, 22), stripes=True, tilt=12, ch=26, grooves=(314, 328))))


def lower_body():
    return B.pelvis(dict(
        pel=[(-20, 112, 78, -2), (60, 122, 84, -2), (140, 96, 72, -2), (190, 76, 62, -2)], belt=(120, 140, 100, 76),
        front=dict(full=20, tip=-60, a=24), side=dict(rows=[(-60, 176, 96, -4), (30, 150, 90, -4), (110, 136, 86, -4)], span=24, center=84),
        hip_x=100, hip_z=36, hip_r=48, hip_len=112, pel_ch=26))


def legs():
    return B.legs(dict(
        LT=430, LS=420, foot_h=106, thigh_ch=20, shin_ch=18, knee_ch=16,
        thigh=[(-12, 56, 60, 0), (120, 70, 76, 2), (300, 62, 66, 0), (430, 50, 54, 0)], thigh_shell=(-56, 56), thigh_seams=(220,),
        thigh_piston=True, thigh_cable=True,
        knee_r=54, knee_len=128, kneecap=[(-50, 44, 50), (-14, 52, 58), (30, 54, 60), (64, 48, 54)],
        shin=[(30, 56, 60, 0), (150, 64, 70, -6), (310, 52, 56, -2), (420, 46, 48, 0)], shin_shell=(-70, 70),
        calf_piston=True, lights=True, ankle_r=40,
        foot=[(-90, 54, 36, -60), (-24, 60, 46, -52), (70, 60, 40, -58), (160, 54, 28, -70), (216, 44, 18, -80)]))
