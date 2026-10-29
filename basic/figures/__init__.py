"""Figuren (Roboter-Spielfigur, M-4, NPCs) – Vertrag für die Prüfungen aus 0.30 „Rulebook“ (Regeln docs/stilhandbuch.md › 12).

Noch keine Figur in diesem Ordner. Sobald hier ein Modul `basic/figures/<name>.py` liegt, prüfen ./check (tools/rules.py, ohne Blender)
und tools/test_figure.py (Blender, am Netz) es automatisch. Ein Figurenmodul liefert:

  META      dict(id, de, role='player'|'friendly'|'enemy', form='square_circle'|'circle'|'triangle' (F2, passend zur Rolle),
            size_class='small'|'medium'|'large' und scale (Vielfaches der Spielerfigur, F7; für role 'player' entfällt beides))
  HEIGHT_MM, HEAD_MM  Körperhöhe und gemessene Helmhöhe (F1: ≈ 7,5 Kopfhöhen, Hinweis außerhalb 7,0–8,0)
  BONES     {name: dict(parent=None|name, head=(x, y, z))} – Welt mm, Figur steht auf z = 0 und schaut nach −Y (wie basic/robot);
            Hilfsknochen zählen mit (F4 Schulterpanzer), Simulation nicht (F6: ≤ 100)
  POSES     {name: {Knochen: (rx, ry, rz)}} – Grad um die Weltachsen am Knochenkopf, wirkt auf alle Kinder; Pflicht sind
            tools/rules.POSES (Arm oben, Arm vor der Brust, tiefe Hocke, Ausfallschritt, Rumpfdrehung ±45°, F3)
  pieces()  [dict(id, bone, kind, p)] – starre Teile je Knochen (F-R16), kind/p wie tools/ego_build.piece_mesh ('box' d/c, 'hull' pts,
            'cyl', 'plate', 'prism'; mm); Dreiecke ≤ 30 000 ohne Ausrüstung (F6)
  CONTACT_OK  Menge von Knochenpaaren (frozenset), deren Teile sich berühren dürfen (weicher Unteranzug in der Fuge, F-R19);
            alle anderen Teile verschiedener Knochen halten in der Grundhaltung ≥ 1 mm Abstand und durchdringen sich in keiner Pose
  HAND      Arm-Modul der Hand (F5: ein Handmaß – basic.arms.robot_arm, solange die Figur die Ego-Hand trägt; Abgleich mit Arm v3
            nach 0.23 „Gauntlet“)

Der Roboter aus 0.23 „Gauntlet“ (basic/robot, data/robot.spec.json) ist Außenansicht, noch keine Spielfigur: für ihn melden die
Prüfungen nur Budget und Proportion aus dem Spec; mit dem Schritt zur Spielfigur bekommt er ein Modul nach diesem Vertrag.
"""
