<!-- erzeugt von tools/robot_doc.py – nicht von Hand ändern -->

# BASIC-Roboter – Baugruppen und Teile

Eigenständiges Modell `BASIC-ROBOT` (Version 0.23, Entwurf (Außenansicht zu den Ego-Armen v3, nicht exportiert)). Quelle: `basic/robot/`; Aufbau, Bilder und Ankerprüfung: `tools/robot_build.py`. Die Arme sind an den Ego-Arm gekoppelt (`basic/arms/robot_arm.py`, Entscheidung des Nutzers 24.10.2026); Roboter-eigene Abwandlungen nur in `basic/robot/arms.py`.

Gemessen in der Grundhaltung `idle` (ohne Waffe): Höhe 1709 mm, Breite 755 mm, Tiefe 399 mm.

## Baugruppen

| Baugruppe | ID | Segmente | Teile | Objekte im Modell | Dreiecke | Größe B × T × H (mm) |
|---|---|---|---:|---:|---:|---|
| Kopf | `head` | `head` | 9 | 9 | 11248 | 227 × 240 × 297 |
| Arme | `arms` | `upper`, `fore`, `hand`, `f0_0`, `f0_1`, `f0_2` … | 67 | 134 | 23072 | 753 × 362 × 752 |
| Oberkörper | `upper_body` | `torso` | 23 | 23 | 28928 | 755 × 301 × 509 |
| Unterkörper | `lower_body` | `pelvis` | 7 | 7 | 8456 | 439 × 198 × 316 |
| Beine | `legs` | `thigh`, `shin`, `foot` | 22 | 44 | 73576 | 577 × 398 × 942 |

Seitige Baugruppen (Arme, Beine) führen jedes Teil einmal; im Modell steht es rechts und links (Spiegelung an X).

## Anker

Lage in der Grundhaltung (Entwurf, mm, Welt: vorn −Y, oben +Z, rechts −X). Abstand = gemessener kleinster Abstand zwischen Eltern- und Kindbaugruppe (0 = sie greifen ineinander).

| Anker | Gelenk | Eltern → Kind | Lage (mm) | Abstand (mm) |
|---|---|---|---|---:|
| `Socket_Neck` | Hals | `upper_body` → `head` | (0, -28, 1439) | 0.0 |
| `Socket_Shoulder_R` | Schulter rechts | `upper_body` → `arms` | (-246.845, -64.696, 1396.345) | 0.0 |
| `Socket_Shoulder_L` | Schulter links | `upper_body` → `arms` | (246.845, 14.294, 1401.888) | 0.0 |
| `Socket_Waist` | Taille | `upper_body` → `lower_body` | (0, 0, 1040) | 0.0 |
| `Socket_Hip_R` | Hüfte rechts | `lower_body` → `legs` | (-116, 0, 910) | 0.0 |
| `Socket_Hip_L` | Hüfte links | `lower_body` → `legs` | (116, 0, 910) | 0.0 |

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

### Kopf (`head`, 9 Teile)

| ID | Bezeichnung | Segment | Form | Material |
|---|---|---|---|---|
| `neck` | Hals | `head` | loft | `graphite` |
| `neck_ring` | Wirbelring | `head` | wrap | `dark_metal` |
| `helmet` | Helm | `head` | loft | `shell` |
| `helmet_seam` | Helmfuge | `head` | wrap | `graphite` |
| `face` | Gesichtsplatte | `head` | wrap | `anodized` |
| `visor` | Augenlinie | `head` | wrap | `energy` |
| `temple_disc` | Medaillon | `head` | Zylinder | `graphite` |
| `temple_ring` | Medaillonring | `head` | Zylinder | `trim` |
| `temple_hub` | Medaillonnabe | `head` | Zylinder | `graphite` |

Materialrollen: `anodized` 1, `dark_metal` 1, `energy` 1, `graphite` 4, `shell` 1, `trim` 1

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

### Oberkörper (`upper_body`, 23 Teile)

| ID | Bezeichnung | Segment | Form | Material |
|---|---|---|---|---|
| `waist_core` | Taillenkern | `torso` | loft | `graphite` |
| `waist_ring_a` | Wirbelring | `torso` | wrap | `dark_metal` |
| `waist_ring_b` | Wirbelring | `torso` | wrap | `dark_metal` |
| `torso_core` | Rumpf | `torso` | loft | `graphite` |
| `collar` | Kragen | `torso` | loft | `graphite` |
| `chest` | Brustplatte | `torso` | wrap | `shell` |
| `chest_plate` | Brustlage | `torso` | wrap | `anodized` |
| `chest_line` | Akzentlinie | `torso` | wrap | `accent` |
| `chest_bolt_a` | Bolzen | `torso` | Zylinder | `trim` |
| `chest_bolt_b` | Bolzen | `torso` | Zylinder | `trim` |
| `back` | Rückenplatte | `torso` | wrap | `shell` |
| `shoulder_joint_r` | Schultergelenk | `torso` | Zylinder | `dark_metal` |
| `pauldron_r` | Schulterpanzer | `torso` | loft | `shell` |
| `pauldron_band_r` | Schulterband | `torso` | wrap | `graphite` |
| `shoulder_r_disc` | Medaillon | `torso` | Zylinder | `graphite` |
| `shoulder_r_ring` | Medaillonring | `torso` | Zylinder | `trim` |
| `shoulder_r_hub` | Medaillonnabe | `torso` | Zylinder | `graphite` |
| `shoulder_joint_l` | Schultergelenk | `torso` | Zylinder | `dark_metal` |
| `pauldron_l` | Schulterpanzer | `torso` | loft | `shell` |
| `pauldron_band_l` | Schulterband | `torso` | wrap | `graphite` |
| `shoulder_l_disc` | Medaillon | `torso` | Zylinder | `graphite` |
| `shoulder_l_ring` | Medaillonring | `torso` | Zylinder | `trim` |
| `shoulder_l_hub` | Medaillonnabe | `torso` | Zylinder | `graphite` |

Materialrollen: `accent` 1, `anodized` 1, `dark_metal` 4, `graphite` 9, `shell` 4, `trim` 4

### Unterkörper (`lower_body`, 7 Teile)

| ID | Bezeichnung | Segment | Form | Material |
|---|---|---|---|---|
| `pelvis_core` | Becken | `pelvis` | loft | `graphite` |
| `belt` | Gürtelring | `pelvis` | wrap | `dark_metal` |
| `tasset` | Lendenplatte | `pelvis` | wrap | `shell` |
| `tasset_side_r` | Beintasche | `pelvis` | wrap | `shell` |
| `hip_joint_r` | Hüftgelenk | `pelvis` | Zylinder | `dark_metal` |
| `tasset_side_l` | Beintasche | `pelvis` | wrap | `shell` |
| `hip_joint_l` | Hüftgelenk | `pelvis` | Zylinder | `dark_metal` |

Materialrollen: `dark_metal` 3, `graphite` 1, `shell` 3

### Beine (`legs`, 22 Teile)

| ID | Bezeichnung | Segment | Form | Material |
|---|---|---|---|---|
| `thigh_core` | Oberschenkel | `thigh` | loft | `graphite` |
| `thigh_shell` | Oberschenkelschale | `thigh` | wrap | `shell` |
| `knee` | Kniegelenk | `shin` | Zylinder | `dark_metal` |
| `knee_med_disc` | Medaillon | `shin` | Zylinder | `graphite` |
| `knee_med_ring` | Medaillonring | `shin` | Zylinder | `trim` |
| `knee_med_hub` | Medaillonnabe | `shin` | Zylinder | `graphite` |
| `knee_cap` | Kniekappe | `shin` | wrap | `shell` |
| `shin_core` | Schienbein | `shin` | loft | `graphite` |
| `shin_shell` | Schienbeinschale | `shin` | wrap | `shell` |
| `shin_plate` | Schienbeinlage | `shin` | wrap | `anodized` |
| `calf` | Wadenplatte | `shin` | wrap | `shell` |
| `boot_cuff` | Stiefelschaft | `shin` | wrap | `shell` |
| `shin_bolt_a` | Bolzen | `shin` | Zylinder | `trim` |
| `shin_bolt_b` | Bolzen | `shin` | Zylinder | `trim` |
| `ankle` | Knöchel | `foot` | Zylinder | `dark_metal` |
| `ankle_med_disc` | Medaillon | `foot` | Zylinder | `graphite` |
| `ankle_med_ring` | Medaillonring | `foot` | Zylinder | `trim` |
| `ankle_med_hub` | Medaillonnabe | `foot` | Zylinder | `graphite` |
| `foot_core` | Fuß | `foot` | loft | `graphite` |
| `toe_cap` | Zehenkappe | `foot` | wrap | `shell` |
| `heel_cap` | Fersenkappe | `foot` | wrap | `shell` |
| `sole` | Sohle | `foot` | loft | `rubber` |

Materialrollen: `anodized` 1, `dark_metal` 2, `graphite` 7, `rubber` 1, `shell` 7, `trim` 4
