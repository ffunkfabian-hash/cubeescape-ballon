<!-- erzeugt von tools/make_ego.py docs – nicht von Hand ändern -->

# Ego-Haltungen und Aktionen – BASIC-01-v2.1

Eigenes Roboterarm-Rig (`basic/arms/robot_arm.py`) und Ego-Daten (`basic/arms/ego.py`), getrennt von Toolgen und Cube Escape. Kamera 75° horizontal (16:9), 30 fps, Kameraraum: rechts −X, vorn −Y, oben +Z. Herkunft: **T** Toolgen-Startwert, **M** gemessen an Destiny 2, **E** entworfen. Handgelenk-Ziel 45°, Grenze 55° (Toolgen).

## Haltungen

| Haltung | Socket_Hand (m) | Handgelenk max | Herkunft |
|---|---|---|---|
| `hip` | [-0.19, -0.42, -0.23] | 25.7° | M Destiny-Hüfte: Mündung x 54–59 / y 60–71 % (Motiongen huefte › 4, Entscheidungsliste 2.1 A), Lage E; 0.15: Mündung x 58,8 / y 49,6 → x 58,2 / y 63,2 % (6,5 cm tiefer, Lauf zur Bildmitte); Toolgen-Hüfte als Start |
| `ads` | [0.0, -0.0556, -0.169] | 28.0° | Visier-Standard v2: Socket_Eye ist der Augenpunkt, liegt in der Kamera; Waffenmodell ungezoomt, Welt zoomt je Klasse |
| `sprint` | [-0.1, -0.34, -0.23] | 34.9° | E nach Destiny-Sprint (quer, gesenkt) |
| `lowered` | [-0.17, -0.38, -0.25] | 36.8° | E |
| `crouch` | [-0.18, -0.41, -0.245] | 26.1° | E (wie hip versetzt, 0.15 mit hip gesenkt) |
| `air` | [-0.19, -0.42, -0.215] | nur in Aktionen geprüft | E (wie hip versetzt, 0.15 mit hip gesenkt) |
| `holstered` | [-0.24, -0.25, -0.62] | nur in Aktionen geprüft | E (unter dem Bild) |
| `reload` | [-0.07, -0.34, -0.135] | 16.6° | T Reload roll −20/pitch 12, für Destiny-Anmutung verstärkt (E) |
| `inspect_l` | [-0.06, -0.36, -0.16] | 24.9° | E (Ego-Seite zeigt zur Kamera) |
| `inspect_r` | [-0.1, -0.36, -0.12] | 41.2° | E (Oberseite und rechte Seite) |

## Aktionen

| Aktion | Beschreibung | Bilder | Marker (Bild) | Handgelenk max | Clip | Sichtung | Herkunft |
|---|---|---|---|---|---|---|---|
| `idle_hip` | Ruhe an der Hüfte (Atmen) | 75 (2.50 s) | – | 25.9° | ego_BASIC-01-v2.1_idle_hip.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Atembewegung bewusst klein | E |
| `draw` | Ziehen | 25 (0.83 s) | Ready (18) | 42.7° | ego_BASIC-01-v2.1_draw.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Waffe kommt von unten in die tiefere Hüfte, Stützhand greift | M Ziehen 0,23 s bis Hüfte (Auto Rifle, Q-REF) + Ausfedern E |
| `holster` | Wegstecken | 8 (0.27 s) | HandOff (1), Holstered (8) | 42.5° | ego_BASIC-01-v2.1_holster.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; 0,27 s: ab Bild 4 nur noch die Mündung am unteren Rand, ab Bild 8 leer | M Destiny-Wechsel: Wegstecken 0,08–0,27 s (Motiongen wechsel › 4, Entscheidungsliste 6.1 A) → 0,27 s ohne TIME_SCALE (bis 0.14: 0,60 s); Ablauf E (CE: Holster ab aktueller Stellung) |
| `aim_in` | Hüfte → Zielen | 10 (0.33 s) | Aimed (9) | 28.0° | ego_BASIC-01-v2.1_aim_in.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Visierlinie mittig | E 0,30 s (CE-Handling Auto 0,39→0,20 s) |
| `aim_out` | Zielen → Hüfte | 8 (0.27 s) | Ready (8) | 28.0° | ego_BASIC-01-v2.1_aim_out.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png | E |
| `fire_hip` | Dauerfeuer aus der Hüfte | 32 (1.07 s) | Fire (2) | 25.7° | ego_BASIC-01-v2.1_fire_hip.mp4 | geprüft: Mündungsfeuer und Hülsen 0.16 gerendert und gesichtet (5.3 A / 5.4 A): Blitz genau 1 Bild je Schuss im Schussbild (Kern fast weiß, Seitenflammen Cyan, ohne Bloom), Hülse ab dem Schussbild nach rechts; Schussbild-Bogen schussbilder_blender.png; 10 Blitze in Bild 2–24, Hülsen steigen über das Gehäuse und fliegen rechts aus dem Bild | M 720/min = 1 Schuss je 2,5 Bilder (Q-REF; bis 0.14 alle 2 Bilder ≈ 940/min); Rückstoß T 17,5 mm/3° |
| `fire_ads` | Dauerfeuer im Zielen | 32 (1.07 s) | AimFire (2) | 28.0° | ego_BASIC-01-v2.1_fire_ads.mp4 | geprüft: Mündungsfeuer und Hülsen 0.16 gerendert und gesichtet (5.3 A / 5.4 A): Blitz genau 1 Bild je Schuss im Schussbild (Kern fast weiß, Seitenflammen Cyan, ohne Bloom), Hülse ab dem Schussbild nach rechts; Schussbild-Bogen schussbilder_blender.png; 10 Blitze, im Zielen bedecken die Seitenflammen ≤ 13,1 % der Holo-Öffnung, das Absehen bleibt frei; Hülse ein Bild unten rechts, groß (Auswurffenster 11 cm vor dem Auge) | M Kadenz wie fire_hip; Rückstoß im Zielen nach RECOIL ads_* (5.1 A: Visier steht, die Welt wandert) E |
| `reload_tactical` | Nachladen mit Restmunition | 63 (2.10 s) | HandOff (5), MagOut (12), MagIn (36), HandOn (48), Ready (58) | 36.9° | ego_BASIC-01-v2.1_reload_tactical.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Weg aus der tieferen Hüfte in die Nachladehaltung ohne Sprung | M MagIn ≈ 0,93 s; Ablauf T (Reload-Keys) mit Destiny-Kippen E; v2: Ausholen, Stoß bei MagIn, Nachfedern E |
| `reload_empty` | Nachladen aus leerem Zustand | 75 (2.50 s) | HandOff (6), MagOut (10), MagIn (35), Chamber (50), HandOn (60), Ready (70) | 37.0° | ego_BASIC-01-v2.1_reload_empty.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Magazin fällt, neues von unten, Durchladen; Hand am Ladehebel teils am rechten Bildrand | M leer 1,85 s, MagOut 0,25 s, MagIn 0,93 s (Q-REF Auto Rifle); Ladehebel E; v2: Ausholen, Stoß bei MagIn, Ruck beim Durchladen, Nachfedern E |
| `inspect` | Betrachten | 120 (4.00 s) | Start (20), End (118) | 41.3° | ego_BASIC-01-v2.1_inspect.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Ego-Seite, dann Oberseite; Rückkehr in die tiefere Hüfte | E nach Apex/CoD-Muster (Ego-Seite, dann Oberseite); Destiny hat keinen Ego-Inspect |
| `sprint` | Sprint: Beginn, Schleife, Ende | 60 (2.00 s) | SprintLoop (10), Ready (60) | 36.3° | ego_BASIC-01-v2.1_sprint.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Hub sichtbar größer als 0.14, U-Bogen | E (CE: Waffe senkt sich und rollt zur Mitte); period = Doppelschritt (seitlich), vertikal je Schritt: 19 Bilder = 0,633 s → 3,16 Schritte/s, seitlich 1,58 Hz, Rollen ±3,5°, U-Bogen (oben an den Seitenumkehren) nach Motiongen REF 0.23 (Destiny 2, Automatik/Handfeuerwaffe gemessen). 0.9: 10 Bilder = 6 Schritte/s („tapsig“). 0.15: Hub 12/10 → 22/18 mm (seitlich/vertikal) für ≈ 10 % H / 13 % B im Bild wie die Destiny-Automatik (Entscheidungsliste 3.1 A, gemessen wie in Schritt 2: Oberkante, linke Kante) |
| `lowered` | Gesenkte Haltung / Wandnähe | 45 (1.50 s) | Lowered (10), Ready (45) | 37.2° | ego_BASIC-01-v2.1_lowered.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png | E |
| `walk` | Gehen (liegende Acht) | 60 (2.00 s) | – | 25.8° | ego_BASIC-01-v2.1_walk.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; liegende Acht bewusst klein | E (CE: liegende Acht) |
| `crouch` | Ducken | 30 (1.00 s) | Crouched (10) | 26.1° | ego_BASIC-01-v2.1_crouch.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png | E |
| `jump_land` | Sprung, Luftphase, Landung | 50 (1.67 s) | Air (10), Land (35) | 27.1° | ego_BASIC-01-v2.1_jump_land.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Anheben und Landefeder bewusst klein | E (CE: Anheben, Landefeder) |
| `sprint_to_aim` | Sprint → Zielen | 18 (0.60 s) | SprintOut (0), Aimed (12) | 34.9° | ego_BASIC-01-v2.1_sprint_to_aim.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png | E (CE: ADS > Sprint) |
| `sprint_to_fire` | Sprint → Feuer | 26 (0.87 s) | SprintOut (0), Fire (7) | 34.9° | ego_BASIC-01-v2.1_sprint_to_fire.mp4 | geprüft: Mündungsfeuer und Hülsen 0.16 gerendert und gesichtet (5.3 A / 5.4 A): Blitz genau 1 Bild je Schuss im Schussbild (Kern fast weiß, Seitenflammen Cyan, ohne Bloom), Hülse ab dem Schussbild nach rechts; Schussbild-Bogen schussbilder_blender.png; 6 Blitze ab Bild 7, erste Hülse schon während der Waffe zur Hüfte kommt | E (CE: Fire > Sprint) |
| `draw_aim` | Ziehen bei gehaltenem Zielen | 35 (1.17 s) | Ready (18), Aimed (30) | 42.7° | ego_BASIC-01-v2.1_draw_aim.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png | E (CE: Draw nicht unterbrechbar, ADS danach) |
| `reload_to_switch` | Nachladen → Waffenwechsel (Abbruch) | 38 (1.27 s) | HandOff (5), Cancel (18), Holstered (35) | 43.0° | ego_BASIC-01-v2.1_reload_to_switch.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Abbruch bei Bild 18, Magazin bleibt eingesetzt; Tempo wie bisher | E (CE: Reload bricht bei Wechsel ab, Holster ab aktueller Stellung) |

## Abdeckung der Matrixzeilen (Pilot)

| Zeile | durch Aktion | Status |
|---|---|---|
| `pose_rest` | `idle_hip` | dargestellt (mit Händen) |
| `pose_hip` | `idle_hip` | dargestellt (mit Händen) |
| `draw` | `draw` | dargestellt (mit Händen) |
| `ready` | `draw` | dargestellt (mit Händen) |
| `holster` | `holster` | dargestellt (mit Händen) |
| `pose_aim` | `aim_in` | dargestellt (mit Händen) |
| `tr_hip_aim` | `aim_in` | dargestellt (mit Händen) |
| `tr_aim_hip` | `aim_out` | dargestellt (mit Händen) |
| `fire_auto` | `fire_ads` | dargestellt (mit Händen) |
| `recoil_mech` | `fire_hip` | dargestellt (mit Händen) |
| `recoil_camera` | `fire_hip` | dargestellt (mit Händen) |
| `reload_partial` | `reload_tactical` | dargestellt (mit Händen) |
| `reload_feed` | `reload_tactical` | dargestellt (mit Händen) |
| `reload_empty` | `reload_empty` | dargestellt (mit Händen) |
| `cycle` | `reload_empty` | dargestellt (mit Händen) |
| `inspect` | `inspect` | dargestellt (mit Händen) |
| `inspect_return` | `inspect` | dargestellt (mit Händen) |
| `sprint_in` | `sprint` | dargestellt (mit Händen) |
| `sprint_loop` | `sprint` | dargestellt (mit Händen) |
| `sprint_out` | `sprint` | dargestellt (mit Händen) |
| `pose_lowered` | `lowered` | dargestellt (mit Händen) |
| `tr_lowered_return` | `lowered` | dargestellt (mit Händen) |
| `move_walk` | `walk` | dargestellt (mit Händen) |
| `sway` | `walk` | dargestellt (mit Händen) |
| `crouch` | `crouch` | dargestellt (mit Händen) |
| `jump_start` | `jump_land` | dargestellt (mit Händen) |
| `air` | `jump_land` | dargestellt (mit Händen) |
| `land` | `jump_land` | dargestellt (mit Händen) |
| `tr_sprint_aim` | `sprint_to_aim` | dargestellt (mit Händen) |
| `tr_sprint_fire` | `sprint_to_fire` | dargestellt (mit Händen) |
| `tr_draw_aimheld` | `draw_aim` | dargestellt (mit Händen) |
| `tr_reload_switch` | `reload_to_switch` | dargestellt (mit Händen) |
| `switch` | `reload_to_switch` | dargestellt (mit Händen) |

Clips: `~/Library/Caches/CubeEscapeBallon/evidence/clips/ego_<waffe>_<aktion>.mp4`; Kontaktbögen `…/evidence/ego_<waffe>_<aktion>.png`; Szene `…/out/<waffe>/ego/<waffe>_ego.blend`.
