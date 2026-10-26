<!-- erzeugt von tools/make_ego.py docs – nicht von Hand ändern -->

# Ego-Haltungen und Aktionen – BASIC-01-v2.1

Eigenes Roboterarm-Rig (`basic/arms/robot_arm.py`) und Ego-Daten (`basic/arms/ego.py`), getrennt von Toolgen und Cube Escape. Kamera 75° horizontal (16:9), 30 fps, Kameraraum: rechts −X, vorn −Y, oben +Z. Herkunft: **T** Toolgen-Startwert, **M** gemessen an Destiny 2, **E** entworfen. Handgelenk-Ziel 45°, Grenze 55° (Toolgen).

## Haltungen

| Haltung | Socket_Hand (m) | Handgelenk max | Herkunft |
|---|---|---|---|
| `hip` | [-0.2, -0.42, -0.165] | 24.9° | E (Destiny-Hüfte: Griff unten rechts, Lauf zur Bildmitte); Toolgen-Hüfte (−0,21/−0,537/−0,176) als Start |
| `ads` | [0.0, -0.081, -0.172] | 28.0° | E (Visierlinie = Kameraachse) |
| `sprint` | [-0.1, -0.34, -0.23] | 34.9° | E nach Destiny-Sprint (quer, gesenkt) |
| `lowered` | [-0.17, -0.38, -0.25] | 36.8° | E |
| `crouch` | [-0.19, -0.41, -0.18] | 23.9° | E |
| `air` | [-0.2, -0.42, -0.15] | nur in Aktionen geprüft | E |
| `holstered` | [-0.24, -0.25, -0.62] | nur in Aktionen geprüft | E (unter dem Bild) |
| `reload` | [-0.07, -0.34, -0.135] | 16.6° | T Reload roll −20/pitch 12, für Destiny-Anmutung verstärkt (E) |
| `inspect_l` | [-0.06, -0.36, -0.16] | 24.9° | E (Ego-Seite zeigt zur Kamera) |
| `inspect_r` | [-0.1, -0.36, -0.12] | 41.2° | E (Oberseite und rechte Seite) |

## Aktionen

| Aktion | Beschreibung | Bilder | Marker (Bild) | Handgelenk max | Clip | Sichtung | Herkunft |
|---|---|---|---|---|---|---|---|
| `idle_hip` | Ruhe an der Hüfte (Atmen) | 75 (2.50 s) | – | 24.9° | ego_BASIC-01-v2.1_idle_hip.mp4 | geprüft: Bewegung v2 (Hermite, Feder-Nachlauf, 30 fps) gerendert und gesichtet; Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Atembewegung bewusst klein | E |
| `draw` | Ziehen | 25 (0.83 s) | Ready (18) | 42.7° | ego_BASIC-01-v2.1_draw.mp4 | geprüft: Bewegung v2 (Hermite, Feder-Nachlauf, 30 fps) gerendert und gesichtet; Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Waffe kommt von unten, Stützhand greift bei Bild 13 | M Ziehen 0,23 s bis Hüfte (Auto Rifle, Q-REF) + Ausfedern E |
| `holster` | Wegstecken | 18 (0.60 s) | HandOff (2), Holstered (15) | 43.1° | ego_BASIC-01-v2.1_holster.mp4 | geprüft: Bewegung v2 (Hermite, Feder-Nachlauf, 30 fps) gerendert und gesichtet; Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png | E (CE: Holster ab aktueller Stellung) |
| `aim_in` | Hüfte → Zielen | 10 (0.33 s) | Aimed (9) | 28.1° | ego_BASIC-01-v2.1_aim_in.mp4 | geprüft: Bewegung v2 (Hermite, Feder-Nachlauf, 30 fps) gerendert und gesichtet; Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Visierlinie mittig | E 0,30 s (CE-Handling Auto 0,39→0,20 s) |
| `aim_out` | Zielen → Hüfte | 8 (0.27 s) | Ready (8) | 28.0° | ego_BASIC-01-v2.1_aim_out.mp4 | geprüft: Bewegung v2 (Hermite, Feder-Nachlauf, 30 fps) gerendert und gesichtet; Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png | E |
| `fire_hip` | Dauerfeuer aus der Hüfte | 32 (1.07 s) | Fire (2) | 25.0° | ego_BASIC-01-v2.1_fire_hip.mp4 | geprüft: Bewegung v2 (Hermite, Feder-Nachlauf, 30 fps) gerendert und gesichtet; Schlüsselbilder in halber Originalgröße (Bild 16): Rückstoß sichtbar, Stützhand am Handschutz | M 720/min ≈ 1 Schuss je 2,5 Bilder (Q-REF); Rückstoß T 17,5 mm/3° |
| `fire_ads` | Dauerfeuer im Zielen | 32 (1.07 s) | AimFire (2) | 28.0° | ego_BASIC-01-v2.1_fire_ads.mp4 | geprüft: Bewegung v2 (Hermite, Feder-Nachlauf, 30 fps) gerendert und gesichtet; Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Visier springt leicht | M Kadenz wie fire_hip; Rückstoß im Zielen gedämpft E |
| `reload_tactical` | Nachladen mit Restmunition | 63 (2.10 s) | HandOff (5), MagOut (12), MagIn (36), HandOn (48), Ready (58) | 36.9° | ego_BASIC-01-v2.1_reload_tactical.mp4 | geprüft: Bewegung v2 (Hermite, Feder-Nachlauf, 30 fps) gerendert und gesichtet; Schlüsselbilder in halber Originalgröße (Bild 12): Hand zieht Magazin nach unten | M MagIn ≈ 0,93 s; Ablauf T (Reload-Keys) mit Destiny-Kippen E; v2: Ausholen, Stoß bei MagIn, Nachfedern E |
| `reload_empty` | Nachladen aus leerem Zustand | 75 (2.50 s) | HandOff (6), MagOut (10), MagIn (35), Chamber (50), HandOn (60), Ready (70) | 37.0° | ego_BASIC-01-v2.1_reload_empty.mp4 | geprüft: Bewegung v2 (Hermite, Feder-Nachlauf, 30 fps) gerendert und gesichtet; Schlüsselbilder in halber Originalgröße (Bilder 8, 20, 27, 38): Magazin fällt, neues von unten, eingesetzt; Hinweis: Hand am Ladehebel liegt am rechten Bildrand | M leer 1,85 s, MagOut 0,25 s, MagIn 0,93 s (Q-REF Auto Rifle); Ladehebel E; v2: Ausholen, Stoß bei MagIn, Ruck beim Durchladen, Nachfedern E |
| `inspect` | Betrachten | 120 (4.00 s) | Start (20), End (118) | 41.3° | ego_BASIC-01-v2.1_inspect.mp4 | geprüft: Bewegung v2 (Hermite, Feder-Nachlauf, 30 fps) gerendert und gesichtet; Schlüsselbilder in halber Originalgröße (Bilder 16, 62): Ego-Seite, dann Oberseite; rechte Hand umgreift den Griff | E nach Apex/CoD-Muster (Ego-Seite, dann Oberseite); Destiny hat keinen Ego-Inspect |
| `sprint` | Sprint: Beginn, Schleife, Ende | 60 (2.00 s) | SprintLoop (10), Ready (60) | 36.5° | ego_BASIC-01-v2.1_sprint.mp4 | geprüft: Bewegung v2 (Hermite, Feder-Nachlauf, 30 fps) gerendert und gesichtet; Schlüsselbilder in halber Originalgröße (Bild 20) und Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png | E (CE: Waffe senkt sich und rollt zur Mitte); Rhythmus Robogen SprintFull 0,33 s je Doppelschritt |
| `lowered` | Gesenkte Haltung / Wandnähe | 45 (1.50 s) | Lowered (10), Ready (45) | 37.3° | ego_BASIC-01-v2.1_lowered.mp4 | geprüft: Bewegung v2 (Hermite, Feder-Nachlauf, 30 fps) gerendert und gesichtet; Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png | E |
| `walk` | Gehen (liegende Acht) | 60 (2.00 s) | – | 25.3° | ego_BASIC-01-v2.1_walk.mp4 | geprüft: Bewegung v2 (Hermite, Feder-Nachlauf, 30 fps) gerendert und gesichtet; Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; liegende Acht bewusst klein | E (CE: liegende Acht) |
| `crouch` | Ducken | 30 (1.00 s) | Crouched (10) | 24.9° | ego_BASIC-01-v2.1_crouch.mp4 | geprüft: Bewegung v2 (Hermite, Feder-Nachlauf, 30 fps) gerendert und gesichtet; Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png | E |
| `jump_land` | Sprung, Luftphase, Landung | 50 (1.67 s) | Air (10), Land (35) | 25.6° | ego_BASIC-01-v2.1_jump_land.mp4 | geprüft: Bewegung v2 (Hermite, Feder-Nachlauf, 30 fps) gerendert und gesichtet; Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Anheben und Landefeder bewusst klein | E (CE: Anheben, Landefeder) |
| `sprint_to_aim` | Sprint → Zielen | 18 (0.60 s) | SprintOut (0), Aimed (12) | 34.9° | ego_BASIC-01-v2.1_sprint_to_aim.mp4 | geprüft: Bewegung v2 (Hermite, Feder-Nachlauf, 30 fps) gerendert und gesichtet; Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png | E (CE: ADS > Sprint) |
| `sprint_to_fire` | Sprint → Feuer | 26 (0.87 s) | SprintOut (0), Fire (7) | 34.9° | ego_BASIC-01-v2.1_sprint_to_fire.mp4 | geprüft: Bewegung v2 (Hermite, Feder-Nachlauf, 30 fps) gerendert und gesichtet; Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png | E (CE: Fire > Sprint) |
| `draw_aim` | Ziehen bei gehaltenem Zielen | 35 (1.17 s) | Ready (18), Aimed (30) | 42.7° | ego_BASIC-01-v2.1_draw_aim.mp4 | geprüft: Bewegung v2 (Hermite, Feder-Nachlauf, 30 fps) gerendert und gesichtet; Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png | E (CE: Draw nicht unterbrechbar, ADS danach) |
| `reload_to_switch` | Nachladen → Waffenwechsel (Abbruch) | 38 (1.27 s) | HandOff (5), Cancel (18), Holstered (35) | 43.0° | ego_BASIC-01-v2.1_reload_to_switch.mp4 | geprüft: Bewegung v2 (Hermite, Feder-Nachlauf, 30 fps) gerendert und gesichtet; Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Abbruch bei Bild 14, Magazin bleibt eingesetzt | E (CE: Reload bricht bei Wechsel ab, Holster ab aktueller Stellung) |

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
