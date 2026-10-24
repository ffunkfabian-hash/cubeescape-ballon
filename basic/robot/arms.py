"""Baugruppe Arme: Ober-/Unterarm, Ellbogen, Hand mit vier Fingern und Daumen – je Seite.

Gekoppelt an den Ego-Arm (Entscheidung des Nutzers 24.10.2026): Die Teile kommen aus basic/arms/robot_arm.parts(); Änderungen am
Ego-Arm wirken hier mit. Roboter-eigene Ergänzungen stehen nur in EXTRA (und DROP), robot_arm.py bleibt unberührt.
Segmentrahmen wie dort: Ursprung im Gelenk, +Z entlang des Glieds, +Y Panzerseite; die linke Seite ist an X gespiegelt.
"""
from basic.arms import robot_arm as RA

SEGMENTS = list(RA.SEGMENTS)
UPPER_MM, FORE_MM = RA.UPPER_MM, RA.FORE_MM
FINGER_POSES = RA.FINGER_POSES
DROP = set()        # Ego-Teile, die der Roboter nicht zeigt
EXTRA = []          # Roboter-eigene Teile (gleiche Tupelform)


def parts():
    return [p for p in RA.parts() if p[0] not in DROP] + list(EXTRA)
