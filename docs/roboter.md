<!-- erzeugt von tools/robot_doc.py – nicht von Hand ändern -->

# BASIC-Roboter – Baugruppen und Teile

Eigenständiges Modell `BASIC-ROBOT` (Version 0.5, Entwurf (Spaßfigur, nicht exportiert)). Quelle: `basic/robot/`; Aufbau, Bilder und Ankerprüfung: `tools/robot_build.py`. Die Arme sind an den Ego-Arm gekoppelt (`basic/arms/robot_arm.py`, Entscheidung des Nutzers 24.10.2026); Roboter-eigene Abwandlungen nur in `basic/robot/arms.py`.

Gemessen in der Grundhaltung `idle` (ohne Waffe): Höhe 1909 mm, Breite 702 mm, Tiefe 375 mm.

## Baugruppen

| Baugruppe | ID | Segmente | Teile | Objekte im Modell | Dreiecke | Größe B × T × H (mm) |
|---|---|---|---:|---:|---:|---|
| Kopf | `head` | `head` | 21 | 21 | 5540 | 200 × 237 × 387 |
| Arme | `arms` | `upper`, `fore`, `hand`, `f0_0`, `f0_1`, `f0_2` … | 67 | 134 | 23072 | 702 × 268 × 744 |
| Oberkörper | `upper_body` | `torso` | 38 | 38 | 9634 | 618 × 321 × 490 |
| Unterkörper | `lower_body` | `pelvis` | 7 | 7 | 1524 | 298 × 185 × 220 |
| Beine | `legs` | `thigh`, `shin`, `foot` | 26 | 52 | 11920 | 556 × 331 × 1066 |

Seitige Baugruppen (Arme, Beine) führen jedes Teil einmal; im Modell steht es rechts und links (Spiegelung an X).

## Anker

Lage in der Grundhaltung (Entwurf, mm, Welt: vorn −Y, oben +Z, rechts −X). Abstand = gemessener kleinster Abstand zwischen Eltern- und Kindbaugruppe (0 = sie greifen ineinander).

| Anker | Gelenk | Eltern → Kind | Lage (mm) | Abstand (mm) |
|---|---|---|---|---:|
| `Socket_Neck` | Hals | `upper_body` → `head` | (0, 0, 1480) | 0.0 |
| `Socket_Shoulder_R` | Schulter rechts | `upper_body` → `arms` | (-235, 0, 1440) | 0.0 |
| `Socket_Shoulder_L` | Schulter links | `upper_body` → `arms` | (235, 0, 1440) | 0.0 |
| `Socket_Waist` | Taille | `upper_body` → `lower_body` | (0, 0, 1110) | 0.0 |
| `Socket_Hip_R` | Hüfte rechts | `lower_body` → `legs` | (-110, 0, 1000) | 0.0 |
| `Socket_Hip_L` | Hüfte links | `lower_body` → `legs` | (110, 0, 1000) | 0.0 |

## Haltungen

- `ready`: Pilotwaffe `pilot.w01_auto_rifle_v21` tief vor dem Körper, Hände an den Griffen (`basic/arms/ego.GRIPS`), Zwei-Knochen-IK – Hero-, Nah- und Seitenbild.
- `idle`: ohne Waffe, Arme hängen leicht gebeugt – Grundhaltung für Prüfung, Explosionsansicht und Einzelblätter.

## Explosionsansicht

Grafischer Versatz je Baugruppe (mm; X gilt für die linke Seite, rechts gespiegelt):

| Baugruppe | Versatz (x, y, z) |
|---|---|
| Kopf | (0, 0, 260) |
| Arme | (300, 0, 40) |
| Oberkörper | (0, 0, 0) |
| Unterkörper | (0, 0, -170) |
| Beine | (90, 0, -360) |

## Teile je Baugruppe

### Kopf (`head`, 21 Teile)

| ID | Bezeichnung | Segment | Form | Material |
|---|---|---|---|---|
| `neck` | Hals | `head` | Zylinder | `graphite` |
| `neck_ring_0` | Halsring | `head` | Zylinder | `dark_metal` |
| `neck_ring_1` | Halsring | `head` | Zylinder | `graphite` |
| `neck_ring_2` | Halsring | `head` | Zylinder | `dark_metal` |
| `neck_ring_3` | Halsring | `head` | Zylinder | `graphite` |
| `neck_ring_4` | Halsring | `head` | Zylinder | `dark_metal` |
| `neck_piston_r_cyl` | Halshydraulik | `head` | Hülle | `dark_metal` |
| `neck_piston_r_rod` | Halshydraulik (Stange) | `head` | Hülle | `trim` |
| `neck_cable_r` | Nackenkabel | `head` | Hüllenkette | `rubber` |
| `neck_piston_l_cyl` | Halshydraulik | `head` | Hülle | `dark_metal` |
| `neck_piston_l_rod` | Halshydraulik (Stange) | `head` | Hülle | `trim` |
| `neck_cable_l` | Nackenkabel | `head` | Hüllenkette | `rubber` |
| `head_core` | Kopfkern | `head` | Hülle | `graphite` |
| `helmet` | Helmband | `head` | Hülle | `shell` |
| `helmet_cap` | Helmkappe | `head` | Hülle | `shell` |
| `faceplate` | Gesichtsplatte | `head` | Hülle | `graphite` |
| `eye_line` | Visier | `head` | Hülle | `energy` |
| `crest` | Mittelkamm | `head` | Hülle | `dark_metal` |
| `ear_disc` | Medaillon | `head` | Zylinder | `graphite` |
| `ear_ring` | Medaillonring | `head` | Zylinder | `trim` |
| `ear_hub` | Medaillonnabe | `head` | Zylinder | `graphite` |

Materialrollen: `dark_metal` 6, `energy` 1, `graphite` 7, `rubber` 2, `shell` 2, `trim` 3

### Arme (`arms`, 67 Teile)

| ID | Bezeichnung | Segment | Form | Material |
|---|---|---|---|---|
| `upper_body` | Oberarmkörper | `upper` | Hülle | `graphite` |
| `upper_shell` | Oberarmschale | `upper` | Hülle | `shell` |
| `elbow` | Ellbogengelenk | `fore` | Zylinder | `dark_metal` |
| `elbow_disc` | Ellbogenscheibe | `fore` | Zylinder | `graphite` |
| `elbow_ring` | Ellbogenring | `fore` | Zylinder | `trim` |
| `elbow_hub` | Ellbogennabe | `fore` | Zylinder | `graphite` |
| `fore_body` | Unterarmkörper | `fore` | Hülle | `graphite` |
| `fore_shell` | Unterarmschale | `fore` | Hülle | `shell` |
| `fore_inset` | Akzentlinie | `fore` | Hülle | `accent` |
| `fore_top` | Handgelenkplatte | `fore` | Hülle | `anodized` |
| `fore_bolt_a` | Bolzen | `fore` | Zylinder | `trim` |
| `fore_bolt_b` | Bolzen | `fore` | Zylinder | `trim` |
| `fore_cuff` | Stulpe | `fore` | Hülle | `dark_metal` |
| `fore_cuff_trim` | Stulpenkante | `fore` | Hülle | `trim` |
| `wrist_block` | Kardanblock | `hand` | Quader | `dark_metal` |
| `wrist_pin` | Kardanbolzen | `hand` | Zylinder | `trim` |
| `palm` | Handfläche | `hand` | Quader | `graphite` |
| `back_plate` | Handrückenschale | `hand` | Facettenplatte | `shell` |
| `back_inset` | Handrücken-Akzentlinie | `hand` | Facettenplatte | `accent` |
| `knuckles` | Knöchelwelle | `hand` | Zylinder | `dark_metal` |
| `knuckle_guard` | Knöchelschutz | `hand` | Facettenplatte | `dark_metal` |
| `thumb_mount` | Daumensockel | `hand` | Quader | `graphite` |
| `f0_0_core` | Finger 1 Glied 1 | `f0_0` | Quader | `graphite` |
| `f0_0_plate` | Finger 1 Glied 1 Platte | `f0_0` | Facettenplatte | `shell` |
| `f0_0_joint` | Finger 1 Gelenk 1 | `f0_0` | Zylinder | `dark_metal` |
| `f0_1_core` | Finger 1 Glied 2 | `f0_1` | Quader | `graphite` |
| `f0_1_plate` | Finger 1 Glied 2 Platte | `f0_1` | Facettenplatte | `shell` |
| `f0_1_joint` | Finger 1 Gelenk 2 | `f0_1` | Zylinder | `dark_metal` |
| `f0_2_core` | Finger 1 Glied 3 | `f0_2` | Quader | `graphite` |
| `f0_2_plate` | Finger 1 Glied 3 Platte | `f0_2` | Facettenplatte | `shell` |
| `f0_2_joint` | Finger 1 Gelenk 3 | `f0_2` | Zylinder | `dark_metal` |
| `f1_0_core` | Finger 2 Glied 1 | `f1_0` | Quader | `graphite` |
| `f1_0_plate` | Finger 2 Glied 1 Platte | `f1_0` | Facettenplatte | `shell` |
| `f1_0_joint` | Finger 2 Gelenk 1 | `f1_0` | Zylinder | `dark_metal` |
| `f1_1_core` | Finger 2 Glied 2 | `f1_1` | Quader | `graphite` |
| `f1_1_plate` | Finger 2 Glied 2 Platte | `f1_1` | Facettenplatte | `shell` |
| `f1_1_joint` | Finger 2 Gelenk 2 | `f1_1` | Zylinder | `dark_metal` |
| `f1_2_core` | Finger 2 Glied 3 | `f1_2` | Quader | `graphite` |
| `f1_2_plate` | Finger 2 Glied 3 Platte | `f1_2` | Facettenplatte | `shell` |
| `f1_2_joint` | Finger 2 Gelenk 3 | `f1_2` | Zylinder | `dark_metal` |
| `f2_0_core` | Finger 3 Glied 1 | `f2_0` | Quader | `graphite` |
| `f2_0_plate` | Finger 3 Glied 1 Platte | `f2_0` | Facettenplatte | `shell` |
| `f2_0_joint` | Finger 3 Gelenk 1 | `f2_0` | Zylinder | `dark_metal` |
| `f2_1_core` | Finger 3 Glied 2 | `f2_1` | Quader | `graphite` |
| `f2_1_plate` | Finger 3 Glied 2 Platte | `f2_1` | Facettenplatte | `shell` |
| `f2_1_joint` | Finger 3 Gelenk 2 | `f2_1` | Zylinder | `dark_metal` |
| `f2_2_core` | Finger 3 Glied 3 | `f2_2` | Quader | `graphite` |
| `f2_2_plate` | Finger 3 Glied 3 Platte | `f2_2` | Facettenplatte | `shell` |
| `f2_2_joint` | Finger 3 Gelenk 3 | `f2_2` | Zylinder | `dark_metal` |
| `f3_0_core` | Finger 4 Glied 1 | `f3_0` | Quader | `graphite` |
| `f3_0_plate` | Finger 4 Glied 1 Platte | `f3_0` | Facettenplatte | `shell` |
| `f3_0_joint` | Finger 4 Gelenk 1 | `f3_0` | Zylinder | `dark_metal` |
| `f3_1_core` | Finger 4 Glied 2 | `f3_1` | Quader | `graphite` |
| `f3_1_plate` | Finger 4 Glied 2 Platte | `f3_1` | Facettenplatte | `shell` |
| `f3_1_joint` | Finger 4 Gelenk 2 | `f3_1` | Zylinder | `dark_metal` |
| `f3_2_core` | Finger 4 Glied 3 | `f3_2` | Quader | `graphite` |
| `f3_2_plate` | Finger 4 Glied 3 Platte | `f3_2` | Facettenplatte | `shell` |
| `f3_2_joint` | Finger 4 Gelenk 3 | `f3_2` | Zylinder | `dark_metal` |
| `t_0_core` | Daumen Glied 1 | `t_0` | Quader | `graphite` |
| `t_0_plate` | Daumen Glied 1 Platte | `t_0` | Facettenplatte | `shell` |
| `t_0_joint` | Daumengelenk 1 | `t_0` | Zylinder | `dark_metal` |
| `t_1_core` | Daumen Glied 2 | `t_1` | Quader | `graphite` |
| `t_1_plate` | Daumen Glied 2 Platte | `t_1` | Facettenplatte | `shell` |
| `t_1_joint` | Daumengelenk 2 | `t_1` | Zylinder | `dark_metal` |
| `t_2_core` | Daumen Glied 3 | `t_2` | Quader | `graphite` |
| `t_2_plate` | Daumen Glied 3 Platte | `t_2` | Facettenplatte | `shell` |
| `t_2_joint` | Daumengelenk 3 | `t_2` | Zylinder | `dark_metal` |

Materialrollen: `accent` 2, `anodized` 1, `dark_metal` 20, `graphite` 21, `shell` 18, `trim` 5

### Oberkörper (`upper_body`, 38 Teile)

| ID | Bezeichnung | Segment | Form | Material |
|---|---|---|---|---|
| `waist_joint` | Taillengelenk | `torso` | Zylinder | `graphite` |
| `waist_ring_0` | Taillenring | `torso` | Zylinder | `dark_metal` |
| `waist_ring_1` | Taillenring | `torso` | Zylinder | `dark_metal` |
| `waist_ring_2` | Taillenring | `torso` | Zylinder | `dark_metal` |
| `torso_core` | Rumpf | `torso` | Hülle | `graphite` |
| `chest` | Brustplatte | `torso` | Hülle | `shell` |
| `chest_line` | Mittelfuge | `torso` | Hülle | `anodized` |
| `collar` | Kragen | `torso` | Hülle | `graphite` |
| `chest_core_disc` | Medaillon | `torso` | Zylinder | `graphite` |
| `chest_core_ring` | Medaillonring | `torso` | Zylinder | `trim` |
| `chest_core_hub` | Medaillonnabe | `torso` | Zylinder | `graphite` |
| `chest_bolt_0` | Schraube | `torso` | Zylinder | `trim` |
| `chest_bolt_1` | Schraube | `torso` | Zylinder | `trim` |
| `chest_bolt_2` | Schraube | `torso` | Zylinder | `trim` |
| `chest_bolt_3` | Schraube | `torso` | Zylinder | `trim` |
| `flank_r` | Flankenplatte | `torso` | Hülle | `shell` |
| `flank_l` | Flankenplatte | `torso` | Hülle | `shell` |
| `abs_0` | Bauchband | `torso` | Hülle | `graphite` |
| `abs_1` | Bauchband | `torso` | Hülle | `graphite` |
| `abs_2` | Bauchband | `torso` | Hülle | `graphite` |
| `pack` | Rückenmodul | `torso` | Hülle | `graphite` |
| `pack_plate` | Rückenplatte | `torso` | Hülle | `shell` |
| `pauldron_r` | Schulterpanzer | `torso` | Hülle | `shell` |
| `pauldron_rim_r` | Schulterrand | `torso` | Hülle | `graphite` |
| `shoulder_r_disc` | Medaillon | `torso` | Zylinder | `graphite` |
| `shoulder_r_ring` | Medaillonring | `torso` | Zylinder | `trim` |
| `shoulder_r_hub` | Medaillonnabe | `torso` | Zylinder | `graphite` |
| `abs_piston_r_cyl` | Bauchhydraulik | `torso` | Hülle | `dark_metal` |
| `abs_piston_r_rod` | Bauchhydraulik (Stange) | `torso` | Hülle | `trim` |
| `flank_cable_r` | Flankenkabel | `torso` | Hüllenkette | `rubber` |
| `pauldron_l` | Schulterpanzer | `torso` | Hülle | `shell` |
| `pauldron_rim_l` | Schulterrand | `torso` | Hülle | `graphite` |
| `shoulder_l_disc` | Medaillon | `torso` | Zylinder | `graphite` |
| `shoulder_l_ring` | Medaillonring | `torso` | Zylinder | `trim` |
| `shoulder_l_hub` | Medaillonnabe | `torso` | Zylinder | `graphite` |
| `abs_piston_l_cyl` | Bauchhydraulik | `torso` | Hülle | `dark_metal` |
| `abs_piston_l_rod` | Bauchhydraulik (Stange) | `torso` | Hülle | `trim` |
| `flank_cable_l` | Flankenkabel | `torso` | Hüllenkette | `rubber` |

Materialrollen: `anodized` 1, `dark_metal` 5, `graphite` 15, `rubber` 2, `shell` 6, `trim` 9

### Unterkörper (`lower_body`, 7 Teile)

| ID | Bezeichnung | Segment | Form | Material |
|---|---|---|---|---|
| `pelvis_core` | Becken | `pelvis` | Hülle | `graphite` |
| `belt` | Gürtel | `pelvis` | Hülle | `graphite` |
| `buckle` | Gürtelschnalle | `pelvis` | Hülle | `shell` |
| `tasset` | Lendenplatte | `pelvis` | Hülle | `shell` |
| `tasset_edge` | Lendenplattenkante | `pelvis` | Hülle | `dark_metal` |
| `hip_joint_r` | Hüftgelenk | `pelvis` | Zylinder | `dark_metal` |
| `hip_joint_l` | Hüftgelenk | `pelvis` | Zylinder | `dark_metal` |

Materialrollen: `dark_metal` 3, `graphite` 2, `shell` 2

### Beine (`legs`, 26 Teile)

| ID | Bezeichnung | Segment | Form | Material |
|---|---|---|---|---|
| `thigh_body` | Oberschenkel | `thigh` | Hülle | `graphite` |
| `thigh_shell` | Oberschenkelschale | `thigh` | Hülle | `shell` |
| `thigh_bolt_a` | Bolzen | `thigh` | Zylinder | `trim` |
| `thigh_bolt_b` | Bolzen | `thigh` | Zylinder | `trim` |
| `thigh_piston_cyl` | Oberschenkelhydraulik | `thigh` | Hülle | `dark_metal` |
| `thigh_piston_rod` | Oberschenkelhydraulik (Stange) | `thigh` | Hülle | `trim` |
| `knee` | Kniegelenk | `shin` | Zylinder | `dark_metal` |
| `knee_cap` | Kniekappe | `shin` | Hülle | `shell` |
| `knee_med_disc` | Medaillon | `shin` | Zylinder | `graphite` |
| `knee_med_ring` | Medaillonring | `shin` | Zylinder | `trim` |
| `knee_med_hub` | Medaillonnabe | `shin` | Zylinder | `graphite` |
| `shin_body` | Schienbein | `shin` | Hülle | `graphite` |
| `shin_shell` | Schienbeinschale | `shin` | Hülle | `shell` |
| `shin_plate` | Schienbeinplatte | `shin` | Hülle | `anodized` |
| `shin_bolt_a` | Bolzen | `shin` | Zylinder | `trim` |
| `shin_bolt_b` | Bolzen | `shin` | Zylinder | `trim` |
| `calf_piston_cyl` | Wadenhydraulik | `shin` | Hülle | `dark_metal` |
| `calf_piston_rod` | Wadenhydraulik (Stange) | `shin` | Hülle | `trim` |
| `ankle_med_disc` | Medaillon | `foot` | Zylinder | `graphite` |
| `ankle_med_ring` | Medaillonring | `foot` | Zylinder | `trim` |
| `ankle_med_hub` | Medaillonnabe | `foot` | Zylinder | `graphite` |
| `ankle` | Knöchel | `foot` | Zylinder | `dark_metal` |
| `foot_body` | Fuß | `foot` | Hülle | `graphite` |
| `toe_cap` | Zehenkappe | `foot` | Hülle | `shell` |
| `heel` | Fersenplatte | `foot` | Hülle | `shell` |
| `sole` | Sohle | `foot` | Hülle | `rubber` |

Materialrollen: `anodized` 1, `dark_metal` 4, `graphite` 7, `rubber` 1, `shell` 5, `trim` 8
