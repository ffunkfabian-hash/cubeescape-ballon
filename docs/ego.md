<!-- erzeugt von tools/make_ego.py docs – nicht von Hand ändern -->

# Ego-Haltungen und Aktionen

Eigenes Roboterarm-Rig (`basic/arms/robot_arm.py`) und Ego-Daten (`basic/arms/ego.py`), getrennt von Toolgen und Cube Escape. Kamera 75° horizontal (16:9), 30 fps, Kameraraum: rechts −X, vorn −Y, oben +Z. Herkunft: **T** Toolgen-Startwert, **M** gemessen an Destiny 2, **E** entworfen, **S** Sekundärquelle (Menü, Datenbank). Handgelenk-Ziel 45°, Grenze 55° (Toolgen).

Spielbare Waffen (Taste 1 = BASIC-01-v2.1, 2 = BASIC-06-v2.1, 3 = BASIC-03-v2.1, 4 = BASIC-02-v2.1, 5 = BASIC-T01-v2.1, 6 = BASIC-04-v2.1, 7 = BASIC-05-v2.1, 8 = BASIC-09-v2.1, 9 = BASIC-12-v2.1, 0 = BASIC-15-v2.1, 1 = BASIC-08-v2.1, 2 = BASIC-10-v2.1, 3 = BASIC-11-v2.1, 4 = BASIC-07-v2.1, 5 = BASIC-13-v2.1, 6 = BASIC-14-v2.1). Haltungen, Dauer und Spielwerte je Klasse aus `ego.CLASSES` (Entscheidungsliste Schritt 6); was eine Klasse nicht nennt, gilt wie bei der Automatik.

## BASIC-01-v2.1 – Formstudie 01 v2.1 (auto_rifle)

### Klassen- und Spielwerte

| Wert | Stand | Herkunft |
|---|---|---|
| Klasse | auto_rifle | Bezugsklasse: Haltungen POSES, Zeiten ACTIONS (BASIC-01, Destiny-Automatik) |
| Kadenz | 720/min | M 720/min (Chroma Rush, Motiongen waffenwerte › 4; Frage 7.1 A), Clip fire_hip seit 0.15 ebenso (alle 2,5 Bilder); Magazin 30 E (Entwurf, Vorschlag Übergabe 0.4) |
| Magazin | 30 | M 720/min (Chroma Rush, Motiongen waffenwerte › 4; Frage 7.1 A), Clip fire_hip seit 0.15 ebenso (alle 2,5 Bilder); Magazin 30 E (Entwurf, Vorschlag Übergabe 0.4) |
| Feuerart | `full_auto` – Dauerfeuer | Spec (META fire, data/specs); Unity: gameplay.fire_mode (0.20) |
| Weltzoom im Zielen | 1.9 | M Glidepath (Entscheidungsliste 1.2 A, basic/reticles.py › CLASS_ZOOM) |
| Hüft-Fadenkreuz | ring_dot 3.2 % H | gemessen (Glidepath) (4.1 A / 4.2 A, basic/reticles.py › HIP) |
| Sprint-Fadenkreuz | caret | basic/reticles.py › HIP.sprint (4.1 A) |
| Bahnstufe je Schuss | 1.00 % H | ego.RECOIL (gemeinsam, Automatik ≈ 1 % H je Schuss, 5.2 A) |
| Mündungsfeuer | 33 ms | M Destiny: 1–2 Bilder bei 60/s, Kern klein, Seitenflammen breiter, Zielen Automatik ≈ 20 % der Öffnung (Motiongen muendung › 6, Entscheidungsliste 5.3 A); Maße und Farben E (Stil v2.1) |
| Hülsen | rifle (42 × 9.6 mm) | E: Auswurffenster rechts am Oberen Gehäuse (port_cover), Hülse nach rechts, etwas hoch und vorn; Bahn: M Destiny: Hülse im 1. Blitzbild oder 1 Bild danach, rechts/rechts unten (Motiongen muendung › 6, Entscheidungsliste 5d/5.4 A); Geschwindigkeit, Drehung, Lebensdauer E |
| Rückstoß | ego.RECOIL (gemeinsam) | M Destiny-Automatik: Säule 1 % H je Schuss, im Zielen wandert die Welt (5.1 A / 5.2 A) |
| Wirkung | Kugel, Einschlag bullet | M keine Spur, Funken, kein Loch in Destiny (REF 0.36 z-im-solemn-hymn); Loch E (Nutzerentscheid 180) (ego.PAYLOAD, Entscheidungsliste Block 9) |
| Sprint-Frequenz | 3,16 / 1,58 Hz (gemeinsam) | M Destiny Automatik/Handfeuerwaffe, für alle Klassen bis zu neuen Messungen (3c) |
| Griffe | grip, support, mag, charge | ego.GRIPS (Pilotwaffe) |
| Live-Teile | trigger = trigger, bolt = bolt_carrier, port = port_cover | ego.LIVE (Pilotwaffe) |

### Haltungen

| Haltung | Socket_Hand (m) | Handgelenk max | Herkunft |
|---|---|---|---|
| `hip` | [-0.2, -0.42, -0.165] | 24.9° | M Destiny-Hüfte: Mündung x 54–59 / y 60–71 % (Motiongen huefte › 4, Entscheidungsliste 2.1 A), Lage E; 0.15: Mündung x 58,8 / y 49,6 → x 58,2 / y 63,2 % (6,5 cm tiefer, Lauf zur Bildmitte); Toolgen-Hüfte als Start |
| `ads` | [0.0, -0.0556, -0.169] | 28.0° | Visier-Standard v2: Socket_Eye ist der Augenpunkt, liegt in der Kamera; Waffenmodell ungezoomt, Welt zoomt je Klasse |
| `sprint` | [-0.1, -0.34, -0.23] | 34.9° | E nach Destiny-Sprint (quer, gesenkt) |
| `lowered` | [-0.17, -0.38, -0.25] | 36.8° | E |
| `crouch` | [-0.19, -0.41, -0.18] | 23.9° | E (wie hip versetzt, 0.15 mit hip gesenkt) |
| `air` | [-0.19, -0.42, -0.215] | nur in Aktionen geprüft | E (wie hip versetzt, 0.15 mit hip gesenkt) |
| `holstered` | [-0.24, -0.25, -0.62] | nur in Aktionen geprüft | E (unter dem Bild) |
| `reload` | [-0.07, -0.34, -0.135] | 16.6° | T Reload roll −20/pitch 12, für Destiny-Anmutung verstärkt (E) |
| `inspect_l` | [-0.06, -0.36, -0.16] | 24.9° | E (Ego-Seite zeigt zur Kamera) |
| `inspect_r` | [-0.1, -0.36, -0.12] | 41.2° | E (Oberseite und rechte Seite) |

### Aktionen

| Aktion | Beschreibung | Bilder | Marker (Bild) | Handgelenk max | Clip | Sichtung | Herkunft |
|---|---|---|---|---|---|---|---|
| `idle_hip` | Ruhe an der Hüfte (Atmen) | 75 (2.50 s) | – | 24.9° | ego_BASIC-01-v2.1_idle_hip.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Atembewegung bewusst klein | E |
| `draw` | Ziehen | 25 (0.83 s) | Ready (18) | 42.7° | ego_BASIC-01-v2.1_draw.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Waffe kommt von unten in die tiefere Hüfte, Stützhand greift | M Ziehen 0,23 s bis Hüfte (Auto Rifle, Q-REF) + Ausfedern E |
| `holster` | Wegstecken | 8 (0.27 s) | HandOff (1), Holstered (8) | 43.1° | ego_BASIC-01-v2.1_holster.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; 0,27 s: ab Bild 4 nur noch die Mündung am unteren Rand, ab Bild 8 leer | M Destiny-Wechsel: Wegstecken 0,08–0,27 s (Motiongen wechsel › 4, Entscheidungsliste 6.1 A) → 0,27 s ohne TIME_SCALE (bis 0.14: 0,60 s); Ablauf E (CE: Holster ab aktueller Stellung) |
| `aim_in` | Hüfte → Zielen | 10 (0.33 s) | Aimed (9) | 28.0° | ego_BASIC-01-v2.1_aim_in.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Visierlinie mittig | E 0,30 s (CE-Handling Auto 0,39→0,20 s) |
| `aim_out` | Zielen → Hüfte | 8 (0.27 s) | Ready (8) | 28.0° | ego_BASIC-01-v2.1_aim_out.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png | E |
| `fire_hip` | Dauerfeuer aus der Hüfte | 32 (1.07 s) | Fire (2) | 25.0° | ego_BASIC-01-v2.1_fire_hip.mp4 | geprüft: Mündungsfeuer und Hülsen 0.16 gerendert und gesichtet (5.3 A / 5.4 A): Blitz genau 1 Bild je Schuss im Schussbild (Kern fast weiß, Seitenflammen Cyan, ohne Bloom), Hülse ab dem Schussbild nach rechts; Schussbild-Bogen schussbilder_blender.png; 10 Blitze in Bild 2–24, Hülsen steigen über das Gehäuse und fliegen rechts aus dem Bild | M 720/min = 1 Schuss je 2,5 Bilder (Q-REF; bis 0.14 alle 2 Bilder ≈ 940/min); Rückstoß T 17,5 mm/3° |
| `fire_ads` | Dauerfeuer im Zielen | 32 (1.07 s) | AimFire (2) | 28.0° | ego_BASIC-01-v2.1_fire_ads.mp4 | geprüft: Mündungsfeuer und Hülsen 0.16 gerendert und gesichtet (5.3 A / 5.4 A): Blitz genau 1 Bild je Schuss im Schussbild (Kern fast weiß, Seitenflammen Cyan, ohne Bloom), Hülse ab dem Schussbild nach rechts; Schussbild-Bogen schussbilder_blender.png; 10 Blitze, im Zielen bedecken die Seitenflammen ≤ 13,1 % der Holo-Öffnung, das Absehen bleibt frei; Hülse ein Bild unten rechts, groß (Auswurffenster 11 cm vor dem Auge) | M Kadenz wie fire_hip; Rückstoß im Zielen nach RECOIL ads_* (5.1 A: Visier steht, die Welt wandert) E |
| `reload_tactical` | Nachladen mit Restmunition | 63 (2.10 s) | HandOff (5), MagOut (12), MagIn (36), HandOn (48), Ready (58) | 36.9° | ego_BASIC-01-v2.1_reload_tactical.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Weg aus der tieferen Hüfte in die Nachladehaltung ohne Sprung | M MagIn ≈ 0,93 s; Ablauf T (Reload-Keys) mit Destiny-Kippen E; v2: Ausholen, Stoß bei MagIn, Nachfedern E |
| `reload_empty` | Nachladen aus leerem Zustand | 75 (2.50 s) | HandOff (6), MagOut (10), MagIn (35), Chamber (50), HandOn (60), Ready (70) | 37.0° | ego_BASIC-01-v2.1_reload_empty.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Magazin fällt, neues von unten, Durchladen; Hand am Ladehebel teils am rechten Bildrand | M leer 1,85 s, MagOut 0,25 s, MagIn 0,93 s (Q-REF Auto Rifle); Ladehebel E; v2: Ausholen, Stoß bei MagIn, Ruck beim Durchladen, Nachfedern E |
| `inspect` | Betrachten | 120 (4.00 s) | Start (20), End (118) | 41.3° | ego_BASIC-01-v2.1_inspect.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Ego-Seite, dann Oberseite; Rückkehr in die tiefere Hüfte | E nach Apex/CoD-Muster (Ego-Seite, dann Oberseite); Destiny hat keinen Ego-Inspect |
| `sprint` | Sprint: Beginn, Schleife, Ende | 60 (2.00 s) | SprintLoop (10), Ready (60) | 36.3° | ego_BASIC-01-v2.1_sprint.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Hub sichtbar größer als 0.14, U-Bogen | E (CE: Waffe senkt sich und rollt zur Mitte); period = Doppelschritt (seitlich), vertikal je Schritt: 19 Bilder = 0,633 s → 3,16 Schritte/s, seitlich 1,58 Hz, Rollen ±3,5°, U-Bogen (oben an den Seitenumkehren) nach Motiongen REF 0.23 (Destiny 2, Automatik/Handfeuerwaffe gemessen). 0.9: 10 Bilder = 6 Schritte/s („tapsig“). 0.15: Hub 12/10 → 22/18 mm (seitlich/vertikal) für ≈ 10 % H / 13 % B im Bild wie die Destiny-Automatik (Entscheidungsliste 3.1 A, gemessen wie in Schritt 2: Oberkante, linke Kante) |
| `lowered` | Gesenkte Haltung / Wandnähe | 45 (1.50 s) | Lowered (10), Ready (45) | 37.3° | ego_BASIC-01-v2.1_lowered.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png | E |
| `walk` | Gehen (liegende Acht) | 60 (2.00 s) | – | 25.3° | ego_BASIC-01-v2.1_walk.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; liegende Acht bewusst klein | E (CE: liegende Acht) |
| `crouch` | Ducken | 30 (1.00 s) | Crouched (10) | 24.9° | ego_BASIC-01-v2.1_crouch.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png | E |
| `jump_land` | Sprung, Luftphase, Landung | 50 (1.67 s) | Air (10), Land (35) | 25.6° | ego_BASIC-01-v2.1_jump_land.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Anheben und Landefeder bewusst klein | E (CE: Anheben, Landefeder) |
| `sprint_to_aim` | Sprint → Zielen | 18 (0.60 s) | SprintOut (0), Aimed (12) | 34.9° | ego_BASIC-01-v2.1_sprint_to_aim.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png | E (CE: ADS > Sprint) |
| `sprint_to_fire` | Sprint → Feuer | 26 (0.87 s) | SprintOut (0), Fire (7) | 34.9° | ego_BASIC-01-v2.1_sprint_to_fire.mp4 | geprüft: Mündungsfeuer und Hülsen 0.16 gerendert und gesichtet (5.3 A / 5.4 A): Blitz genau 1 Bild je Schuss im Schussbild (Kern fast weiß, Seitenflammen Cyan, ohne Bloom), Hülse ab dem Schussbild nach rechts; Schussbild-Bogen schussbilder_blender.png; 6 Blitze ab Bild 7, erste Hülse schon während der Waffe zur Hüfte kommt | E (CE: Fire > Sprint) |
| `draw_aim` | Ziehen bei gehaltenem Zielen | 35 (1.17 s) | Ready (18), Aimed (30) | 42.7° | ego_BASIC-01-v2.1_draw_aim.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png | E (CE: Draw nicht unterbrechbar, ADS danach) |
| `reload_to_switch` | Nachladen → Waffenwechsel (Abbruch) | 38 (1.27 s) | HandOff (5), Cancel (18), Holstered (35) | 43.0° | ego_BASIC-01-v2.1_reload_to_switch.mp4 | geprüft: Bewegung 0.15 gerendert und gesichtet (Hüfte tiefer, Sprint-Hub 22/18 mm, holster 0,27 s, im Zielen kein Kamera-Nicken, Schüsse alle 2,5 Bilder); Ego-Kontaktbogen evidence/ego_BASIC-01-v2.1_<aktion>.png; Abbruch bei Bild 18, Magazin bleibt eingesetzt; Tempo wie bisher | E (CE: Reload bricht bei Wechsel ab, Holster ab aktueller Stellung) |

### Abdeckung der Matrixzeilen

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

## BASIC-06-v2.1 – Kurzläufer v2.1 (submachine_gun)

### Klassen- und Spielwerte

| Wert | Stand | Herkunft |
|---|---|---|
| Klasse | submachine_gun | Entscheidungsliste Schritt 6, erste übertragene Klasse (Nutzer 26.10.2026): Hüfte 2b/2.1 A, Sprint 3b/3.2 A, Anflug 4d |
| Kadenz | 720/min | M 720/min (Destiny-MP PvP, Dauerfeuer im Zielen ≈ 5 Bilder Abstand bei 60/s, Motiongen REF destiny2; Menüs 750–900/min [S]), Clip fire_hip wie die Automatik alle 2,5 Bilder; Magazin 30 E (Destiny-MP 26–30 [S]) |
| Magazin | 30 | M 720/min (Destiny-MP PvP, Dauerfeuer im Zielen ≈ 5 Bilder Abstand bei 60/s, Motiongen REF destiny2; Menüs 750–900/min [S]), Clip fire_hip wie die Automatik alle 2,5 Bilder; Magazin 30 E (Destiny-MP 26–30 [S]) |
| Feuerart | `full_auto` – Dauerfeuer | Spec (META fire, data/specs); Unity: gameplay.fire_mode (0.20) |
| Weltzoom im Zielen | 1.45 | M Glidepath (Entscheidungsliste 1.2 A, basic/reticles.py › CLASS_ZOOM) |
| Hüft-Fadenkreuz | circle_cross 6.1 % H | gemessen (Glidepath, 5,9–6,3 % H) (4.1 A / 4.2 A, basic/reticles.py › HIP) |
| Sprint-Fadenkreuz | aus | basic/reticles.py › HIP.sprint (4.1 A) |
| Bahnstufe je Schuss | 1.00 % H | ego.RECOIL (gemeinsam, Automatik ≈ 1 % H je Schuss, 5.2 A) |
| Haltung `hip` | Socket_Hand [-0.121, -0.42, -0.186], Ziel [0.057, -3.0, -0.015], Rollen 6° | M Destiny-MP-Hüfte: Mündung ≈ 57/61 und 58/62 %, Holo ≈ 62–68/57–58 %, Lauf fast in Blickrichtung (Motiongen REF destiny2 › MP PvE-Hüfte, Huckleberry), Band Kurzwaffen x 53–71 / y 59–84 % (2b); Lage E, gerechnet auf Mündung 58/63 und Absehen 65,5/60 % (7 cm weiter zur Mitte und 4 cm höher als die Automatik) |
| Haltung `sprint` | Socket_Hand [-0.116, -0.34, -0.172], Ziel [0.673, -2.115, -0.48], Rollen 40° | M/O Destiny-MP-Sprint: tiefe Trageform, Mündung ≈ 43/80, Holo-Ring ≈ 52/72 %, nach links gerollt (Motiongen REF destiny2 › MP PvP, Entscheidungsliste 3b/3.2 A); Lage E, gerechnet auf Mündung 43/80 und Absehen 52/72 %, Rollen +40° (Oberseite nach links; Automatik −35°, Oberseite nach rechts) |
| Haltung `crouch` | Socket_Hand [-0.111, -0.41, -0.201], Rollen 9° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `air` | Socket_Hand [-0.121, -0.42, -0.171], Rollen 4° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `lowered` | Socket_Hand [-0.101, -0.38, -0.206], Rollen 10° | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| Dauer `aim_in` | 3 Bilder bei 30/s (0.100 s) | M Destiny-Anflug MP 8–12 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen Glidepath, Entscheidungsliste 4d) → 3 Bilder bei 30/s, mit dem Zielen-Nachlauf (10 Hz) am Unity-Bild 11 Bilder bei 60/s (4 Bilder ergaben 13; gleiches Maß bei der Automatik: 10 → 20 wie Destiny); aim_out im selben Verhältnis 0,3 (Destiny-MP ADS aus → ruhig 10–11 Bilder bei 60/s, Huckleberry/Ikelos) |
| Dauer `aim_out` | 2.4 Bilder bei 30/s (0.080 s) | M Destiny-Anflug MP 8–12 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen Glidepath, Entscheidungsliste 4d) → 3 Bilder bei 30/s, mit dem Zielen-Nachlauf (10 Hz) am Unity-Bild 11 Bilder bei 60/s (4 Bilder ergaben 13; gleiches Maß bei der Automatik: 10 → 20 wie Destiny); aim_out im selben Verhältnis 0,3 (Destiny-MP ADS aus → ruhig 10–11 Bilder bei 60/s, Huckleberry/Ikelos) |
| Mündungsfeuer | 33 ms | M Destiny: 1–2 Bilder bei 60/s, Kern klein, Seitenflammen breiter, Zielen Automatik ≈ 20 % der Öffnung (Motiongen muendung › 6, Entscheidungsliste 5.3 A); Maße und Farben E (Stil v2.1) |
| Hülsen | pistol (20 × 9.2 mm) | E: Auswurffenster rechts am Oberen Gehäuse (port_cover), Hülse nach rechts, etwas hoch und vorn (wie BASIC-01); Bahn: M Destiny: Hülse im 1. Blitzbild oder 1 Bild danach, rechts/rechts unten (Motiongen muendung › 6, Entscheidungsliste 5d/5.4 A); Geschwindigkeit, Drehung, Lebensdauer E |
| Rückstoß | ego.RECOIL (gemeinsam) | übertragen von der Automatik: Säule 1 % H je Schuss, im Zielen wandert die Welt (5.1 A / 5.2 A); Destiny-MP: Kick im Zielen ≤ 1 % H, Kamera-Anstieg < 2 % [M, ein PvP-Clip], keine Klassenmessung der Bahn |
| Wirkung | Kugel, Einschlag bullet | M keine Spur, Funken + dunkle Säule (REF 0.36 z-im-ikelos); Loch E (Nutzerentscheid 180) (ego.PAYLOAD, Entscheidungsliste Block 9) |
| Sprint-Frequenz | 3,16 / 1,58 Hz (gemeinsam) | M Destiny Automatik/Handfeuerwaffe, für alle Klassen bis zu neuen Messungen (3c) |
| Griffe | grip, support, mag, charge | Modul-Feld EGO_GRIPS |
| Live-Teile | trigger = trigger, bolt = bolt, port = port_cover | Modul-Feld EGO_LIVE |

### Haltungen

| Haltung | Socket_Hand (m) | Handgelenk max | Herkunft |
|---|---|---|---|
| `hip` | [-0.121, -0.42, -0.186] | 26.9° | M Destiny-MP-Hüfte: Mündung ≈ 57/61 und 58/62 %, Holo ≈ 62–68/57–58 %, Lauf fast in Blickrichtung (Motiongen REF destiny2 › MP PvE-Hüfte, Huckleberry), Band Kurzwaffen x 53–71 / y 59–84 % (2b); Lage E, gerechnet auf Mündung 58/63 und Absehen 65,5/60 % (7 cm weiter zur Mitte und 4 cm höher als die Automatik) |
| `ads` | [0.0, -0.0596, -0.147] | 28.0° | Visier-Standard v2: Socket_Eye ist der Augenpunkt, liegt in der Kamera; Waffenmodell ungezoomt, Welt zoomt je Klasse |
| `sprint` | [-0.116, -0.34, -0.172] | 34.2° | M/O Destiny-MP-Sprint: tiefe Trageform, Mündung ≈ 43/80, Holo-Ring ≈ 52/72 %, nach links gerollt (Motiongen REF destiny2 › MP PvP, Entscheidungsliste 3b/3.2 A); Lage E, gerechnet auf Mündung 43/80 und Absehen 52/72 %, Rollen +40° (Oberseite nach links; Automatik −35°, Oberseite nach rechts) |
| `lowered` | [-0.101, -0.38, -0.206] | 40.2° | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| `crouch` | [-0.111, -0.41, -0.201] | 27.1° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `air` | [-0.121, -0.42, -0.171] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `holstered` | [-0.24, -0.25, -0.62] | nur in Aktionen geprüft | E (unter dem Bild) |
| `reload` | [-0.07, -0.34, -0.135] | 19.3° | T Reload roll −20/pitch 12, für Destiny-Anmutung verstärkt (E) |
| `inspect_l` | [-0.06, -0.36, -0.16] | 40.4° | E (Ego-Seite zeigt zur Kamera) |
| `inspect_r` | [-0.1, -0.36, -0.12] | 14.9° | E (Oberseite und rechte Seite) |

### Aktionen

| Aktion | Beschreibung | Bilder | Marker (Bild) | Handgelenk max | Clip | Sichtung | Herkunft |
|---|---|---|---|---|---|---|---|
| `idle_hip` | Ruhe an der Hüfte (Atmen) | 75 (2.50 s) | – | 27.1° | ego_BASIC-06-v2.1_idle_hip.mp4 | geprüft: Ego-Clip 0.18 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-06-v2.1_<aktion>.png); Stützhand Faust foregrip am Vordergriff; Hüfte der Klasse: Mündung 58,0/62,9 %, Lauf fast in Blickrichtung, linker Unterarm von unten-mittig wie Destiny | E |
| `draw` | Ziehen | 25 (0.83 s) | Ready (18) | 45.0° | ego_BASIC-06-v2.1_draw.mp4 | geprüft: Ego-Clip 0.18 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-06-v2.1_<aktion>.png); Stützhand Faust foregrip am Vordergriff; kommt von unten rechts in die MP-Hüfte, Ready Bild 18 | M Ziehen 0,23 s bis Hüfte (Auto Rifle, Q-REF) + Ausfedern E |
| `holster` | Wegstecken | 8 (0.27 s) | HandOff (1), Holstered (8) | 45.0° | ego_BASIC-06-v2.1_holster.mp4 | geprüft: Ego-Clip 0.18 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-06-v2.1_<aktion>.png); Stützhand Faust foregrip am Vordergriff; ab Bild 4 nur Kante am unteren Rand, Bild 8 leer | M Destiny-Wechsel: Wegstecken 0,08–0,27 s (Motiongen wechsel › 4, Entscheidungsliste 6.1 A) → 0,27 s ohne TIME_SCALE (bis 0.14: 0,60 s); Ablauf E (CE: Holster ab aktueller Stellung) |
| `aim_in` | Hüfte → Zielen | 3 (0.10 s) | Aimed (3) | 27.8° | ego_BASIC-06-v2.1_aim_in.mp4 | geprüft: Ego-Clip 0.18 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-06-v2.1_<aktion>.png); Stützhand Faust foregrip am Vordergriff; 3 Bilder, Holo mittig in Bild 3, kein Überschwingen | E 0,30 s (CE-Handling Auto 0,39→0,20 s); Klasse submachine_gun: 10 → 3 Bilder (M Destiny-Anflug MP 8–12 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen Glidepath, Entscheidungsliste 4d) → 3 Bilder bei 30/s, mit dem Zielen-Nachlauf (10 Hz) am Unity-Bild 11 Bilder bei 60/s (4 Bilder ergaben 13; gleiches Maß bei der Automatik: 10 → 20 wie Destiny); aim_out im selben Verhältnis 0,3 (Destiny-MP ADS aus → ruhig 10–11 Bilder bei 60/s, Huckleberry/Ikelos)) |
| `aim_out` | Zielen → Hüfte | 3 (0.10 s) | Ready (2) | 28.0° | ego_BASIC-06-v2.1_aim_out.mp4 | geprüft: Ego-Clip 0.18 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-06-v2.1_<aktion>.png); Stützhand Faust foregrip am Vordergriff; 2,4 Bilder, Ready Bild 2 | E; Klasse submachine_gun: 8 → 2.4 Bilder (M Destiny-Anflug MP 8–12 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen Glidepath, Entscheidungsliste 4d) → 3 Bilder bei 30/s, mit dem Zielen-Nachlauf (10 Hz) am Unity-Bild 11 Bilder bei 60/s (4 Bilder ergaben 13; gleiches Maß bei der Automatik: 10 → 20 wie Destiny); aim_out im selben Verhältnis 0,3 (Destiny-MP ADS aus → ruhig 10–11 Bilder bei 60/s, Huckleberry/Ikelos)) |
| `fire_hip` | Dauerfeuer aus der Hüfte | 32 (1.07 s) | Fire (2) | 26.9° | ego_BASIC-06-v2.1_fire_hip.mp4 | geprüft: Ego-Clip 0.18 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-06-v2.1_<aktion>.png); Stützhand Faust foregrip am Vordergriff; Blitz und Kurzpatronen-Hülsen nach rechts | M 720/min = 1 Schuss je 2,5 Bilder (Q-REF; bis 0.14 alle 2 Bilder ≈ 940/min); Rückstoß T 17,5 mm/3° |
| `fire_ads` | Dauerfeuer im Zielen | 32 (1.07 s) | AimFire (2) | 28.0° | ego_BASIC-06-v2.1_fire_ads.mp4 | geprüft: Ego-Clip 0.18 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-06-v2.1_<aktion>.png); Stützhand Faust foregrip am Vordergriff; Blitz ≈ 14 % der Holo-Öffnung, Visier steht | M Kadenz wie fire_hip; Rückstoß im Zielen nach RECOIL ads_* (5.1 A: Visier steht, die Welt wandert) E |
| `reload_tactical` | Nachladen mit Restmunition | 63 (2.10 s) | HandOff (5), MagOut (12), MagIn (36), HandOn (48), Ready (58) | 27.9° | ego_BASIC-06-v2.1_reload_tactical.mp4 | geprüft: Ego-Clip 0.18 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-06-v2.1_<aktion>.png); Stützhand Faust foregrip am Vordergriff; linke Hand zieht das Magazin unter dem Griffboden, setzt es ein, Faust zurück am Vordergriff | M MagIn ≈ 0,93 s; Ablauf T (Reload-Keys) mit Destiny-Kippen E; v2: Ausholen, Stoß bei MagIn, Nachfedern E |
| `reload_empty` | Nachladen aus leerem Zustand | 75 (2.50 s) | HandOff (6), MagOut (10), MagIn (35), Chamber (50), HandOn (60), Ready (70) | 27.8° | ego_BASIC-06-v2.1_reload_empty.mp4 | geprüft: Ego-Clip 0.18 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-06-v2.1_<aktion>.png); Stützhand Faust foregrip am Vordergriff; wie taktisch, dann Ladehebel; beim Durchladen ragt der Schaft groß ins Bild (Bild 50) | M leer 1,85 s, MagOut 0,25 s, MagIn 0,93 s (Q-REF Auto Rifle); Ladehebel E; v2: Ausholen, Stoß bei MagIn, Ruck beim Durchladen, Nachfedern E |
| `inspect` | Betrachten | 120 (4.00 s) | Start (20), End (118) | 41.4° | ego_BASIC-06-v2.1_inspect.mp4 | geprüft: Ego-Clip 0.18 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-06-v2.1_<aktion>.png); Stützhand Faust foregrip am Vordergriff; Ego-Seite und Oberseite, Daumen bleibt eingerollt | E nach Apex/CoD-Muster (Ego-Seite, dann Oberseite); Destiny hat keinen Ego-Inspect |
| `sprint` | Sprint: Beginn, Schleife, Ende | 60 (2.00 s) | SprintLoop (10), Ready (60) | 34.4° | ego_BASIC-06-v2.1_sprint.mp4 | geprüft: Ego-Clip 0.18 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-06-v2.1_<aktion>.png); Stützhand Faust foregrip am Vordergriff; tief, Oberseite nach links (+40°), Wippen wie die Automatik | E (CE: Waffe senkt sich und rollt zur Mitte); period = Doppelschritt (seitlich), vertikal je Schritt: 19 Bilder = 0,633 s → 3,16 Schritte/s, seitlich 1,58 Hz, Rollen ±3,5°, U-Bogen (oben an den Seitenumkehren) nach Motiongen REF 0.23 (Destiny 2, Automatik/Handfeuerwaffe gemessen). 0.9: 10 Bilder = 6 Schritte/s („tapsig“). 0.15: Hub 12/10 → 22/18 mm (seitlich/vertikal) für ≈ 10 % H / 13 % B im Bild wie die Destiny-Automatik (Entscheidungsliste 3.1 A, gemessen wie in Schritt 2: Oberkante, linke Kante) |
| `lowered` | Gesenkte Haltung / Wandnähe | 45 (1.50 s) | Lowered (10), Ready (45) | 40.7° | ego_BASIC-06-v2.1_lowered.mp4 | geprüft: Ego-Clip 0.18 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-06-v2.1_<aktion>.png); Stützhand Faust foregrip am Vordergriff; gesenkt; der kurze Schaft ragt groß ins rechte Bild (Bild 10–22) | E |
| `walk` | Gehen (liegende Acht) | 60 (2.00 s) | – | 27.0° | ego_BASIC-06-v2.1_walk.mp4 | geprüft: Ego-Clip 0.18 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-06-v2.1_<aktion>.png); Stützhand Faust foregrip am Vordergriff; liegende Acht, ruhig | E (CE: liegende Acht) |
| `crouch` | Ducken | 30 (1.00 s) | Crouched (10) | 27.2° | ego_BASIC-06-v2.1_crouch.mp4 | geprüft: Ego-Clip 0.18 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-06-v2.1_<aktion>.png); Stützhand Faust foregrip am Vordergriff; leicht tiefer, gerollt | E |
| `jump_land` | Sprung, Luftphase, Landung | 50 (1.67 s) | Air (10), Land (35) | 28.2° | ego_BASIC-06-v2.1_jump_land.mp4 | geprüft: Ego-Clip 0.18 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-06-v2.1_<aktion>.png); Stützhand Faust foregrip am Vordergriff; Anheben, Landefeder | E (CE: Anheben, Landefeder) |
| `sprint_to_aim` | Sprint → Zielen | 18 (0.60 s) | SprintOut (0), Aimed (12) | 34.2° | ego_BASIC-06-v2.1_sprint_to_aim.mp4 | geprüft: Ego-Clip 0.18 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-06-v2.1_<aktion>.png); Stützhand Faust foregrip am Vordergriff; aus der tiefen Trageform direkt ins Visier, Aimed Bild 12 | E (CE: ADS > Sprint) |
| `sprint_to_fire` | Sprint → Feuer | 26 (0.87 s) | SprintOut (0), Fire (7) | 34.2° | ego_BASIC-06-v2.1_sprint_to_fire.mp4 | geprüft: Ego-Clip 0.18 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-06-v2.1_<aktion>.png); Stützhand Faust foregrip am Vordergriff; in die Hüfte, Schuss ab Bild 7 | E (CE: Fire > Sprint) |
| `draw_aim` | Ziehen bei gehaltenem Zielen | 35 (1.17 s) | Ready (18), Aimed (30) | 45.0° | ego_BASIC-06-v2.1_draw_aim.mp4 | geprüft: Ego-Clip 0.18 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-06-v2.1_<aktion>.png); Stützhand Faust foregrip am Vordergriff; Ziehen, dann ins Visier (Aimed Bild 30) | E (CE: Draw nicht unterbrechbar, ADS danach) |
| `reload_to_switch` | Nachladen → Waffenwechsel (Abbruch) | 38 (1.27 s) | HandOff (5), Cancel (18), Holstered (35) | 45.0° | ego_BASIC-06-v2.1_reload_to_switch.mp4 | geprüft: Ego-Clip 0.18 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-06-v2.1_<aktion>.png); Stützhand Faust foregrip am Vordergriff; Abbruch nach dem Magazingriff, Wegstecken bis Bild 35 | E (CE: Reload bricht bei Wechsel ab, Holster ab aktueller Stellung) |

### Abdeckung der Matrixzeilen

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

## BASIC-03-v2.1 – Fernblick v2.1 (scout_rifle)

### Klassen- und Spielwerte

| Wert | Stand | Herkunft |
|---|---|---|
| Klasse | scout_rifle | Entscheidungsliste Schritt 6, zweite übertragene Klasse (0.20 „Spotter“): Hüfte 2.1 A (lange Waffe), Sprint 3.2 A, Anflug 4d, Zielfernrohr nach Visier-Standard 3 |
| Kadenz | 180/min | M 180/min (Tone Patrol, Precision Frame: Schussabstand 20–21 Bilder bei 60/s und Menükarte, Motiongen destiny2 › 3; Manifest Precision Frame 180 [S], waffenwerte › 4); Magazin 15 M (Menükarte Tone Patrol; Destiny-Scouts 13–18 [S]); Feuerart aus der Spec (META fire), halbautomatisch: ein Schuss je Zug; zoom_start E (1d): der Weltzoom beginnt bei diesem Anteil des Augenwegs (Klassen ohne Wert 5 %) – am Unity-Bild gemessen, damit er wie beim Holo mit oder kurz nach dem Modell beginnt |
| Magazin | 15 | M 180/min (Tone Patrol, Precision Frame: Schussabstand 20–21 Bilder bei 60/s und Menükarte, Motiongen destiny2 › 3; Manifest Precision Frame 180 [S], waffenwerte › 4); Magazin 15 M (Menükarte Tone Patrol; Destiny-Scouts 13–18 [S]); Feuerart aus der Spec (META fire), halbautomatisch: ein Schuss je Zug; zoom_start E (1d): der Weltzoom beginnt bei diesem Anteil des Augenwegs (Klassen ohne Wert 5 %) – am Unity-Bild gemessen, damit er wie beim Holo mit oder kurz nach dem Modell beginnt |
| Feuerart | `semi_auto` – Einzelfeuer (ein Schuss je Zug) | Spec (META fire, data/specs); Unity: gameplay.fire_mode (0.20) |
| Weltzoom im Zielen | 2, beginnt bei 20 % des Augenwegs | M Glidepath (Entscheidungsliste 1.2 A, basic/reticles.py › CLASS_ZOOM); Beginn E (1d, siehe Kadenz) |
| Hüft-Fadenkreuz | cross 4.5 % H | entworfen (4.1 A / 4.2 A, basic/reticles.py › HIP) |
| Sprint-Fadenkreuz | aus | basic/reticles.py › HIP.sprint (4.1 A) |
| Bahnstufe je Schuss | 1.00 % H | ego.RECOIL (gemeinsam, Automatik ≈ 1 % H je Schuss, 5.2 A) |
| Haltung `hip` | Socket_Hand [-0.136, -0.42, -0.181], Ziel [-0.188, -3.414, -0.362], Rollen 9.9° | M cubeescape-reference huefte.json (Destiny 2, Mündung 57/65, 58/61, hintere Kimme 65/60, Visieröffnung 72/52 (Tone Patrol, Call to Serve); Lage E: Ausgleichsrechnung gegen diese Werte (0.33, Abgleich aller Waffen; Nutzer 31.10.2026 „Ja, nachziehen“ – bis dahin nur die Mündung eingestellt, das Visier lag 10–19 pp zu tief), gerechnet (Socket_Muzzle, Socket_Sight bzw. Socket_Reticle, Socket_Hand) Mündung 57,5/63,2 %, Visier 68,4/56,0 % |
| Haltung `sprint` | Socket_Hand [-0.1, -0.34, -0.23], Ziel [1.2, -1.6, -0.55], Rollen -35° | E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-Scout-Sprint nicht gemessen (Motiongen destiny2 › Glidepath: kein Sprint-Clip) (Haltung POSES['sprint'] unverändert) |
| Haltung `crouch` | Socket_Hand [-0.126, -0.41, -0.196], Rollen 12.899999999999999° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `air` | Socket_Hand [-0.136, -0.42, -0.166], Rollen 7.9° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `lowered` | Socket_Hand [-0.116, -0.38, -0.201], Rollen 13.899999999999999° | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| Dauer `aim_in` | 9 Bilder bei 30/s (0.300 s) | Nutzerentscheid 31.10.2026 („Neue Werte übernehmen“): Doom of Chelchis / Symmetry ADS ein 20 / 18, aus 16 / 17–18, Ziehen erstes Modellbild → ruhig 44 / 42 Bilder bei 60/s (Motiongen destiny2 › Gapfill) → aim_in 9 (19, zwischen 17 → 7 und 20 → 10), aim_out 8 (17, wie Vorgabe 16 → 8), draw 22 (43 halbiert). Bis 0.33.1: Scout bei Destiny nur grob gemessen: Tone Patrol ≈ 22 Bilder (0,37 s, Bestand, „vom Nachbartyp übertragen“), Patron of Lost Causes 0,20–0,25 s = 12–15 Bilder [M] (Motiongen destiny2 › Glidepath, visiere › v-d2-scout); dazwischen und zwischen Scharfschütze (15 Bilder bis ruhig) und Impuls (20) → E 17 Bilder bei 60/s erste Bewegung → Ruhe, am Unity-Bild gemessen; aim_out M Destiny-Scout ADS aus → Hüfte 0,17 s (Dead Man's Tale, Motiongen auswertung › V04) = 5 Bilder bei 30/s → aim_in 7, aim_out 5 |
| Dauer `aim_out` | 8 Bilder bei 30/s (0.267 s) | Nutzerentscheid 31.10.2026 („Neue Werte übernehmen“): Doom of Chelchis / Symmetry ADS ein 20 / 18, aus 16 / 17–18, Ziehen erstes Modellbild → ruhig 44 / 42 Bilder bei 60/s (Motiongen destiny2 › Gapfill) → aim_in 9 (19, zwischen 17 → 7 und 20 → 10), aim_out 8 (17, wie Vorgabe 16 → 8), draw 22 (43 halbiert). Bis 0.33.1: Scout bei Destiny nur grob gemessen: Tone Patrol ≈ 22 Bilder (0,37 s, Bestand, „vom Nachbartyp übertragen“), Patron of Lost Causes 0,20–0,25 s = 12–15 Bilder [M] (Motiongen destiny2 › Glidepath, visiere › v-d2-scout); dazwischen und zwischen Scharfschütze (15 Bilder bis ruhig) und Impuls (20) → E 17 Bilder bei 60/s erste Bewegung → Ruhe, am Unity-Bild gemessen; aim_out M Destiny-Scout ADS aus → Hüfte 0,17 s (Dead Man's Tale, Motiongen auswertung › V04) = 5 Bilder bei 30/s → aim_in 7, aim_out 5 |
| Dauer `draw` | 22 Bilder bei 30/s (0.733 s) | Nutzerentscheid 31.10.2026 („Neue Werte übernehmen“): Doom of Chelchis / Symmetry ADS ein 20 / 18, aus 16 / 17–18, Ziehen erstes Modellbild → ruhig 44 / 42 Bilder bei 60/s (Motiongen destiny2 › Gapfill) → aim_in 9 (19, zwischen 17 → 7 und 20 → 10), aim_out 8 (17, wie Vorgabe 16 → 8), draw 22 (43 halbiert). Bis 0.33.1: Scout bei Destiny nur grob gemessen: Tone Patrol ≈ 22 Bilder (0,37 s, Bestand, „vom Nachbartyp übertragen“), Patron of Lost Causes 0,20–0,25 s = 12–15 Bilder [M] (Motiongen destiny2 › Glidepath, visiere › v-d2-scout); dazwischen und zwischen Scharfschütze (15 Bilder bis ruhig) und Impuls (20) → E 17 Bilder bei 60/s erste Bewegung → Ruhe, am Unity-Bild gemessen; aim_out M Destiny-Scout ADS aus → Hüfte 0,17 s (Dead Man's Tale, Motiongen auswertung › V04) = 5 Bilder bei 30/s → aim_in 7, aim_out 5 |
| Zielfernrohr im Zielen | aus: scope_strap, scope_tube, scope_eyepiece, scope_eye_trim, scope_ocular_glass, scope_turret, scope_turret_w (Socket_Eye < 60 mm) | E: Okular bis an die Nahebene sichtbar (Augenabstand Okularende 30 mm + near 30 mm), danach Linsenbild; Destiny-Scharfschütze: Okular füllt das Bild 4 Bilder, Linse nach dem Modell (Motiongen destiny2 › 2, Entscheidungsliste 1d) |
| Mündungsfeuer | 33 ms | M Destiny: 1–2 Bilder bei 60/s, Kern klein, Seitenflammen breiter, Zielen Automatik ≈ 20 % der Öffnung (Motiongen muendung › 6, Entscheidungsliste 5.3 A); Maße und Farben E (Stil v2.1) |
| Hülsen | rifle (42 × 9.6 mm) | E: Auswurffenster rechts im Einteilgehäuse (port_cover), Hülse nach rechts, etwas hoch und vorn (wie BASIC-01); Bahn: M Destiny: Hülse im 1. Blitzbild oder 1 Bild danach, rechts/rechts unten (Motiongen muendung › 6, Entscheidungsliste 5d/5.4 A); Geschwindigkeit, Drehung, Lebensdauer E |
| Rückstoß | ego.RECOIL (gemeinsam) | übertragen von der Automatik: Säule 1 % H je Schuss, im Zielen wandert die Welt (5.1 A / 5.2 A); Destiny-Scout Tone Patrol: kräftiger Einzelimpuls, Rest wächst vor den Folgeschüssen, im Zielen fünf Schüsse ≈ 6 % H [M] (Motiongen rueckstoss › 4) – hier dieselbe Säule je Schuss, Salve = Schüsse im Abstand ≤ 1,5 × 60/rpm |
| Wirkung | Kugel, Einschlag bullet | M keine Spur (REF 0.36 z-im-sauerstoff); Einschlag wie Kugel, Loch E (Nutzerentscheid 180) (ego.PAYLOAD, Entscheidungsliste Block 9) |
| Sprint-Frequenz | 3,16 / 1,58 Hz (gemeinsam) | M Destiny Automatik/Handfeuerwaffe, für alle Klassen bis zu neuen Messungen (3c) |
| Griffe | grip, support, mag, charge | Modul-Feld EGO_GRIPS |
| Live-Teile | trigger = trigger, bolt = bolt, port = port_cover | Modul-Feld EGO_LIVE |

### Haltungen

| Haltung | Socket_Hand (m) | Handgelenk max | Herkunft |
|---|---|---|---|
| `hip` | [-0.19, -0.42, -0.23] | 25.7° | M cubeescape-reference huefte.json (Destiny 2, Mündung 57/65, 58/61, hintere Kimme 65/60, Visieröffnung 72/52 (Tone Patrol, Call to Serve); Lage E: Ausgleichsrechnung gegen diese Werte (0.33, Abgleich aller Waffen; Nutzer 31.10.2026 „Ja, nachziehen“ – bis dahin nur die Mündung eingestellt, das Visier lag 10–19 pp zu tief), gerechnet (Socket_Muzzle, Socket_Sight bzw. Socket_Reticle, Socket_Hand) Mündung 57,5/63,2 %, Visier 68,4/56,0 % |
| `ads` | [0.0, -0.018, -0.161] | 28.0° | Visier-Standard v2: Socket_Eye ist der Augenpunkt, liegt in der Kamera; Waffenmodell ungezoomt, Welt zoomt je Klasse |
| `sprint` | [-0.1, -0.34, -0.23] | 34.9° | E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-Scout-Sprint nicht gemessen (Motiongen destiny2 › Glidepath: kein Sprint-Clip) (Haltung POSES['sprint'] unverändert) |
| `lowered` | [-0.17, -0.38, -0.25] | 36.8° | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| `crouch` | [-0.18, -0.41, -0.245] | 26.1° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `air` | [-0.136, -0.42, -0.166] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `holstered` | [-0.24, -0.25, -0.62] | nur in Aktionen geprüft | E (unter dem Bild) |
| `reload` | [-0.07, -0.34, -0.135] | 16.6° | T Reload roll −20/pitch 12, für Destiny-Anmutung verstärkt (E) |
| `inspect_l` | [-0.06, -0.36, -0.16] | 24.9° | E (Ego-Seite zeigt zur Kamera) |
| `inspect_r` | [-0.1, -0.36, -0.12] | 41.2° | E (Oberseite und rechte Seite) |

### Aktionen

| Aktion | Beschreibung | Bilder | Marker (Bild) | Handgelenk max | Clip | Sichtung | Herkunft |
|---|---|---|---|---|---|---|---|
| `idle_hip` | Ruhe an der Hüfte (Atmen) | 75 (2.50 s) | – | 25.9° | ego_BASIC-03-v2.1_idle_hip.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz | E |
| `draw` | Ziehen | 22 (0.73 s) | Ready (16) | 42.7° | ego_BASIC-03-v2.1_draw.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz | M Ziehen 0,23 s bis Hüfte (Auto Rifle, Q-REF) + Ausfedern E; Klasse scout_rifle: 25 → 22 Bilder (Nutzerentscheid 31.10.2026 („Neue Werte übernehmen“): Doom of Chelchis / Symmetry ADS ein 20 / 18, aus 16 / 17–18, Ziehen erstes Modellbild → ruhig 44 / 42 Bilder bei 60/s (Motiongen destiny2 › Gapfill) → aim_in 9 (19, zwischen 17 → 7 und 20 → 10), aim_out 8 (17, wie Vorgabe 16 → 8), draw 22 (43 halbiert). Bis 0.33.1: Scout bei Destiny nur grob gemessen: Tone Patrol ≈ 22 Bilder (0,37 s, Bestand, „vom Nachbartyp übertragen“), Patron of Lost Causes 0,20–0,25 s = 12–15 Bilder [M] (Motiongen destiny2 › Glidepath, visiere › v-d2-scout); dazwischen und zwischen Scharfschütze (15 Bilder bis ruhig) und Impuls (20) → E 17 Bilder bei 60/s erste Bewegung → Ruhe, am Unity-Bild gemessen; aim_out M Destiny-Scout ADS aus → Hüfte 0,17 s (Dead Man's Tale, Motiongen auswertung › V04) = 5 Bilder bei 30/s → aim_in 7, aim_out 5) |
| `holster` | Wegstecken | 8 (0.27 s) | HandOff (1), Holstered (8) | 42.5° | ego_BASIC-03-v2.1_holster.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz | M Destiny-Wechsel: Wegstecken 0,08–0,27 s (Motiongen wechsel › 4, Entscheidungsliste 6.1 A) → 0,27 s ohne TIME_SCALE (bis 0.14: 0,60 s); Ablauf E (CE: Holster ab aktueller Stellung) |
| `aim_in` | Hüfte → Zielen | 9 (0.30 s) | Aimed (8) | 27.9° | ego_BASIC-03-v2.1_aim_in.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz; Okular wächst heran, ab Bild 6 Linsenbild (ads_hide), Ende im Zielfernrohr mit Absehen auf der Mitte | E 0,30 s (CE-Handling Auto 0,39→0,20 s); Klasse scout_rifle: 10 → 9 Bilder (Nutzerentscheid 31.10.2026 („Neue Werte übernehmen“): Doom of Chelchis / Symmetry ADS ein 20 / 18, aus 16 / 17–18, Ziehen erstes Modellbild → ruhig 44 / 42 Bilder bei 60/s (Motiongen destiny2 › Gapfill) → aim_in 9 (19, zwischen 17 → 7 und 20 → 10), aim_out 8 (17, wie Vorgabe 16 → 8), draw 22 (43 halbiert). Bis 0.33.1: Scout bei Destiny nur grob gemessen: Tone Patrol ≈ 22 Bilder (0,37 s, Bestand, „vom Nachbartyp übertragen“), Patron of Lost Causes 0,20–0,25 s = 12–15 Bilder [M] (Motiongen destiny2 › Glidepath, visiere › v-d2-scout); dazwischen und zwischen Scharfschütze (15 Bilder bis ruhig) und Impuls (20) → E 17 Bilder bei 60/s erste Bewegung → Ruhe, am Unity-Bild gemessen; aim_out M Destiny-Scout ADS aus → Hüfte 0,17 s (Dead Man's Tale, Motiongen auswertung › V04) = 5 Bilder bei 30/s → aim_in 7, aim_out 5) |
| `aim_out` | Zielen → Hüfte | 8 (0.27 s) | Ready (8) | 28.0° | ego_BASIC-03-v2.1_aim_out.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz | E; Klasse scout_rifle: 8 → 8 Bilder (Nutzerentscheid 31.10.2026 („Neue Werte übernehmen“): Doom of Chelchis / Symmetry ADS ein 20 / 18, aus 16 / 17–18, Ziehen erstes Modellbild → ruhig 44 / 42 Bilder bei 60/s (Motiongen destiny2 › Gapfill) → aim_in 9 (19, zwischen 17 → 7 und 20 → 10), aim_out 8 (17, wie Vorgabe 16 → 8), draw 22 (43 halbiert). Bis 0.33.1: Scout bei Destiny nur grob gemessen: Tone Patrol ≈ 22 Bilder (0,37 s, Bestand, „vom Nachbartyp übertragen“), Patron of Lost Causes 0,20–0,25 s = 12–15 Bilder [M] (Motiongen destiny2 › Glidepath, visiere › v-d2-scout); dazwischen und zwischen Scharfschütze (15 Bilder bis ruhig) und Impuls (20) → E 17 Bilder bei 60/s erste Bewegung → Ruhe, am Unity-Bild gemessen; aim_out M Destiny-Scout ADS aus → Hüfte 0,17 s (Dead Man's Tale, Motiongen auswertung › V04) = 5 Bilder bei 30/s → aim_in 7, aim_out 5) |
| `fire_hip` | Dauerfeuer aus der Hüfte | 32 (1.07 s) | Fire (2) | 25.7° | ego_BASIC-03-v2.1_fire_hip.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz; drei Einzelschüsse (180/min, Bild 2/12/22), Abzug je Schuss gezogen | M 720/min = 1 Schuss je 2,5 Bilder (Q-REF; bis 0.14 alle 2 Bilder ≈ 940/min); Rückstoß T 17,5 mm/3°; Klasse scout_rifle: 180/min, Einzelfeuer (ein Schuss je Zug) (Schussbilder [2, 12, 22]) |
| `fire_ads` | Dauerfeuer im Zielen | 32 (1.07 s) | AimFire (2) | 28.0° | ego_BASIC-03-v2.1_fire_ads.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz; drei Einzelschüsse im Zielfernrohr, Blitz im Glas ≤ 20 % der Öffnung (10,4 %) | M Kadenz wie fire_hip; Rückstoß im Zielen nach RECOIL ads_* (5.1 A: Visier steht, die Welt wandert) E; Klasse scout_rifle: 180/min, Einzelfeuer (ein Schuss je Zug) (Schussbilder [2, 12, 22]) |
| `reload_tactical` | Nachladen mit Restmunition | 63 (2.10 s) | HandOff (5), MagOut (12), MagIn (36), HandOn (48), Ready (58) | 36.9° | ego_BASIC-03-v2.1_reload_tactical.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz; linke Hand am kurzen Kastenmagazin | M MagIn ≈ 0,93 s; Ablauf T (Reload-Keys) mit Destiny-Kippen E; v2: Ausholen, Stoß bei MagIn, Nachfedern E |
| `reload_empty` | Nachladen aus leerem Zustand | 75 (2.50 s) | HandOff (6), MagOut (10), MagIn (35), Chamber (50), HandOn (60), Ready (70) | 37.0° | ego_BASIC-03-v2.1_reload_empty.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz; Magazin unten am kurzen Kastenmagazin, Ladehebel links | M leer 1,85 s, MagOut 0,25 s, MagIn 0,93 s (Q-REF Auto Rifle); Ladehebel E; v2: Ausholen, Stoß bei MagIn, Ruck beim Durchladen, Nachfedern E |
| `inspect` | Betrachten | 120 (4.00 s) | Start (20), End (118) | 41.3° | ego_BASIC-03-v2.1_inspect.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz | E nach Apex/CoD-Muster (Ego-Seite, dann Oberseite); Destiny hat keinen Ego-Inspect |
| `sprint` | Sprint: Beginn, Schleife, Ende | 60 (2.00 s) | SprintLoop (10), Ready (60) | 36.3° | ego_BASIC-03-v2.1_sprint.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz; Trageform der Automatik (tief, quer, Oberseite nach rechts) | E (CE: Waffe senkt sich und rollt zur Mitte); period = Doppelschritt (seitlich), vertikal je Schritt: 19 Bilder = 0,633 s → 3,16 Schritte/s, seitlich 1,58 Hz, Rollen ±3,5°, U-Bogen (oben an den Seitenumkehren) nach Motiongen REF 0.23 (Destiny 2, Automatik/Handfeuerwaffe gemessen). 0.9: 10 Bilder = 6 Schritte/s („tapsig“). 0.15: Hub 12/10 → 22/18 mm (seitlich/vertikal) für ≈ 10 % H / 13 % B im Bild wie die Destiny-Automatik (Entscheidungsliste 3.1 A, gemessen wie in Schritt 2: Oberkante, linke Kante) |
| `lowered` | Gesenkte Haltung / Wandnähe | 45 (1.50 s) | Lowered (10), Ready (45) | 37.2° | ego_BASIC-03-v2.1_lowered.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz | E |
| `walk` | Gehen (liegende Acht) | 60 (2.00 s) | – | 25.8° | ego_BASIC-03-v2.1_walk.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz | E (CE: liegende Acht) |
| `crouch` | Ducken | 30 (1.00 s) | Crouched (10) | 26.1° | ego_BASIC-03-v2.1_crouch.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz | E |
| `jump_land` | Sprung, Luftphase, Landung | 50 (1.67 s) | Air (10), Land (35) | 27.1° | ego_BASIC-03-v2.1_jump_land.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz | E (CE: Anheben, Landefeder) |
| `sprint_to_aim` | Sprint → Zielen | 18 (0.60 s) | SprintOut (0), Aimed (12) | 34.9° | ego_BASIC-03-v2.1_sprint_to_aim.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz | E (CE: ADS > Sprint) |
| `sprint_to_fire` | Sprint → Feuer | 26 (0.87 s) | SprintOut (0), Fire (7) | 34.9° | ego_BASIC-03-v2.1_sprint_to_fire.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz | E (CE: Fire > Sprint); Klasse scout_rifle: 180/min, Einzelfeuer (ein Schuss je Zug) (Schussbilder [7, 17]) |
| `draw_aim` | Ziehen bei gehaltenem Zielen | 35 (1.17 s) | Ready (18), Aimed (30) | 42.7° | ego_BASIC-03-v2.1_draw_aim.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz; Ziehen, dann direkt ins Zielfernrohr (Linsenbild am Ende) | E (CE: Draw nicht unterbrechbar, ADS danach) |
| `reload_to_switch` | Nachladen → Waffenwechsel (Abbruch) | 38 (1.27 s) | HandOff (5), Cancel (18), Holstered (35) | 43.0° | ego_BASIC-03-v2.1_reload_to_switch.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz | E (CE: Reload bricht bei Wechsel ab, Holster ab aktueller Stellung) |

### Abdeckung der Matrixzeilen

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

## BASIC-02-v2.1 – Impuls v2.1 (pulse_rifle)

### Klassen- und Spielwerte

| Wert | Stand | Herkunft |
|---|---|---|
| Klasse | pulse_rifle | Entscheidungsliste Schritt 6, dritte übertragene Klasse (0.22 „Volley“): Hüfte 2.1 A (lange Waffe), Sprint 3.2 A, Anflug 4d, Salve aus der Spec |
| Kadenz | 540/min | M Gridskipper (Rapid-Fire Frame): Menü 540/min und Magazin 36 [S], in der Salve 4 Bilder Abstand bei 60/s = 900/min [M], Salvenbeginn → Salvenbeginn 3 · 60/540 = 0,333 s (beobachtet ≥ 0,383 s im Spielertakt, kein Grenzwert; Motiongen destiny2 › z-gridskipper-salve); Salvenlänge aus der Spec (META fire burst_3); Bahnstufe ≈ 4 pp H je Salve, Erholung in der Pause (Motiongen rueckstoss › r-d2-gridskipper, 5.2 A) → path_up_h 0,0133 je Schuss (Automatik 0,010); Erholung zwischen den Salven ≈ 80 % (Gridskipper, Salvenfolge 0,38–0,40 s, Motiongen destiny2 › z-gridskipper-salve) → E Erholung ab 0,10 s nach dem Schuss (1,5 Takte) mit 5 Hz kritisch gedämpft: in der Pause von 0,2 s bleiben ≈ 20 % (gemeinsam 0,12 s / 2 Hz: ≈ 78 % blieben, und die nächste Salve sank anfangs ab) |
| Magazin | 36 | M Gridskipper (Rapid-Fire Frame): Menü 540/min und Magazin 36 [S], in der Salve 4 Bilder Abstand bei 60/s = 900/min [M], Salvenbeginn → Salvenbeginn 3 · 60/540 = 0,333 s (beobachtet ≥ 0,383 s im Spielertakt, kein Grenzwert; Motiongen destiny2 › z-gridskipper-salve); Salvenlänge aus der Spec (META fire burst_3); Bahnstufe ≈ 4 pp H je Salve, Erholung in der Pause (Motiongen rueckstoss › r-d2-gridskipper, 5.2 A) → path_up_h 0,0133 je Schuss (Automatik 0,010); Erholung zwischen den Salven ≈ 80 % (Gridskipper, Salvenfolge 0,38–0,40 s, Motiongen destiny2 › z-gridskipper-salve) → E Erholung ab 0,10 s nach dem Schuss (1,5 Takte) mit 5 Hz kritisch gedämpft: in der Pause von 0,2 s bleiben ≈ 20 % (gemeinsam 0,12 s / 2 Hz: ≈ 78 % blieben, und die nächste Salve sank anfangs ab) |
| Feuerart | `burst` – Salve (n Schuss je Zug) | Spec (META fire, data/specs); Unity: gameplay.fire_mode (0.20) |
| Weltzoom im Zielen | 2 | M Glidepath (Entscheidungsliste 1.2 A, basic/reticles.py › CLASS_ZOOM) |
| Hüft-Fadenkreuz | ring_dot 3.2 % H | übertragen (Automatik) (4.1 A / 4.2 A, basic/reticles.py › HIP) |
| Sprint-Fadenkreuz | aus | basic/reticles.py › HIP.sprint (4.1 A) |
| Salve | 3 Schuss je Zug, 900/min in der Salve (0.067 s), Salvenbeginn alle 0.333 s; gehalten Salve um Salve | Länge aus der Spec (META fire), Takt und Folge: M Gridskipper (Rapid-Fire Frame): Menü 540/min und Magazin 36 [S], in der Salve 4 Bilder Abstand bei 60/s = 900/min [M], Salvenbeginn → Salvenbeginn 3 · 60/540 = 0,333 s (beobachtet ≥ 0,383 s im Spielertakt, kein Grenzwert; Motiongen destiny2 › z-gridskipper-salve); Salvenlänge aus der Spec (META fire burst_3); Bahnstufe ≈ 4 pp H je Salve, Erholung in der Pause (Motiongen rueckstoss › r-d2-gridskipper, 5.2 A) → path_up_h 0,0133 je Schuss (Automatik 0,010); Erholung zwischen den Salven ≈ 80 % (Gridskipper, Salvenfolge 0,38–0,40 s, Motiongen destiny2 › z-gridskipper-salve) → E Erholung ab 0,10 s nach dem Schuss (1,5 Takte) mit 5 Hz kritisch gedämpft: in der Pause von 0,2 s bleiben ≈ 20 % (gemeinsam 0,12 s / 2 Hz: ≈ 78 % blieben, und die nächste Salve sank anfangs ab) |
| Bahnstufe je Schuss | 1.33 % H | M Gridskipper (Rapid-Fire Frame): Menü 540/min und Magazin 36 [S], in der Salve 4 Bilder Abstand bei 60/s = 900/min [M], Salvenbeginn → Salvenbeginn 3 · 60/540 = 0,333 s (beobachtet ≥ 0,383 s im Spielertakt, kein Grenzwert; Motiongen destiny2 › z-gridskipper-salve); Salvenlänge aus der Spec (META fire burst_3); Bahnstufe ≈ 4 pp H je Salve, Erholung in der Pause (Motiongen rueckstoss › r-d2-gridskipper, 5.2 A) → path_up_h 0,0133 je Schuss (Automatik 0,010); Erholung zwischen den Salven ≈ 80 % (Gridskipper, Salvenfolge 0,38–0,40 s, Motiongen destiny2 › z-gridskipper-salve) → E Erholung ab 0,10 s nach dem Schuss (1,5 Takte) mit 5 Hz kritisch gedämpft: in der Pause von 0,2 s bleiben ≈ 20 % (gemeinsam 0,12 s / 2 Hz: ≈ 78 % blieben, und die nächste Salve sank anfangs ab) |
| Haltung `hip` | Socket_Hand [-0.183, -0.42, -0.18], Ziel [0.066, -3.399, -0.43], Rollen 11.2° | M cubeescape-reference huefte.json (Destiny 2, Mündung 59/67, 58/64, Visier 73/55, 74/55); Lage E: Ausgleichsrechnung gegen diese Werte (0.33, Abgleich aller Waffen; Nutzer 31.10.2026 „Ja, nachziehen“ – bis dahin nur die Mündung eingestellt, das Visier lag 10–19 pp zu tief), gerechnet (Socket_Muzzle, Socket_Sight bzw. Socket_Reticle, Socket_Hand) Mündung 58,4/65,5 %, Visier 73,4/55,2 % |
| Haltung `sprint` | Socket_Hand [-0.1, -0.34, -0.23], Ziel [1.2, -1.6, -0.55], Rollen -35° | E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-Impuls-Sprint nicht gemessen (Haltung POSES['sprint'] unverändert) |
| Haltung `crouch` | Socket_Hand [-0.173, -0.41, -0.195], Rollen 14.2° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `air` | Socket_Hand [-0.183, -0.42, -0.165], Rollen 9.2° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `lowered` | Socket_Hand [-0.163, -0.38, -0.2], Rollen 15.2° | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| Dauer `draw` | 23 Bilder bei 30/s (0.767 s) | M Destiny-Anflug Automatik/Impuls/MG 20 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen Glidepath, Entscheidungsliste 4d; Gridskipper ADS ein 18 Bilder bis ruhig, Motiongen destiny2): aim_in 10 Bilder bei 30/s wie die Automatik; Ziehen erstes Modellbild → ruhig Smite of Merain 44, Insidious 49, Outbreak 47–48 Bilder bei 60/s (Motiongen destiny2 › Gapfill; Nutzerentscheid 31.10.2026) ≈ 47 → 23 (bis 0.33.1 Vorgabe 25) |
| Mündungsfeuer | 33 ms | M Destiny: 1–2 Bilder bei 60/s, Kern klein, Seitenflammen breiter, Zielen Automatik ≈ 20 % der Öffnung (Motiongen muendung › 6, Entscheidungsliste 5.3 A); Maße und Farben E (Stil v2.1) |
| Hülsen | rifle (42 × 9.6 mm) | E: Auswurffenster rechts im Oberen Gehäuse (port_cover f 22–74), Hülse nach rechts, etwas hoch und vorn (wie BASIC-01); Bahn: M Destiny: Hülse im 1. Blitzbild oder 1 Bild danach, rechts/rechts unten (Motiongen muendung › 6, Entscheidungsliste 5d/5.4 A); Geschwindigkeit, Drehung, Lebensdauer E |
| Rückstoß | ego.RECOIL (gemeinsam) | übertragen von der Automatik: Säule 1 % H je Schuss, im Zielen wandert die Welt (5.1 A / 5.2 A); Destiny-Impuls Gridskipper: Stufe ≈ 4 pp H je Salve, Erholung in der Pause, im Zielen Welt ≈ 5 pp H, Visier < 1 pp [M] (Motiongen rueckstoss › r-d2-gridskipper) – Bahnstufe der Klasse, zweistufig |
| Wirkung | Kugel, Einschlag bullet | M keine Spur, Funken (REF 0.36 z-im-outbreak); Loch E (Nutzerentscheid 180) (ego.PAYLOAD, Entscheidungsliste Block 9) |
| Sprint-Frequenz | 3,16 / 1,58 Hz (gemeinsam) | M Destiny Automatik/Handfeuerwaffe, für alle Klassen bis zu neuen Messungen (3c) |
| Griffe | grip, support, mag, charge | Modul-Feld EGO_GRIPS |
| Live-Teile | trigger = trigger, bolt = bolt_carrier, port = port_cover | Modul-Feld EGO_LIVE |

### Haltungen

| Haltung | Socket_Hand (m) | Handgelenk max | Herkunft |
|---|---|---|---|
| `hip` | [-0.17, -0.42, -0.214] | 25.6° | M cubeescape-reference huefte.json (Destiny 2, Mündung 59/67, 58/64, Visier 73/55, 74/55); Lage E: Ausgleichsrechnung gegen diese Werte (0.33, Abgleich aller Waffen; Nutzer 31.10.2026 „Ja, nachziehen“ – bis dahin nur die Mündung eingestellt, das Visier lag 10–19 pp zu tief), gerechnet (Socket_Muzzle, Socket_Sight bzw. Socket_Reticle, Socket_Hand) Mündung 58,4/65,5 %, Visier 73,4/55,2 % |
| `ads` | [0.0, -0.0616, -0.164] | 28.0° | Visier-Standard v2: Socket_Eye ist der Augenpunkt, liegt in der Kamera; Waffenmodell ungezoomt, Welt zoomt je Klasse |
| `sprint` | [-0.1, -0.34, -0.23] | 34.9° | E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-Impuls-Sprint nicht gemessen (Haltung POSES['sprint'] unverändert) |
| `lowered` | [-0.15, -0.38, -0.234] | 36.7° | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| `crouch` | [-0.16, -0.41, -0.229] | 26.0° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `air` | [-0.183, -0.42, -0.165] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `holstered` | [-0.24, -0.25, -0.62] | nur in Aktionen geprüft | E (unter dem Bild) |
| `reload` | [-0.07, -0.34, -0.135] | 16.6° | T Reload roll −20/pitch 12, für Destiny-Anmutung verstärkt (E) |
| `inspect_l` | [-0.06, -0.36, -0.16] | 24.9° | E (Ego-Seite zeigt zur Kamera) |
| `inspect_r` | [-0.1, -0.36, -0.12] | 41.2° | E (Oberseite und rechte Seite) |

### Aktionen

| Aktion | Beschreibung | Bilder | Marker (Bild) | Handgelenk max | Clip | Sichtung | Herkunft |
|---|---|---|---|---|---|---|---|
| `idle_hip` | Ruhe an der Hüfte (Atmen) | 75 (2.50 s) | – | 25.8° | ego_BASIC-02-v2.1_idle_hip.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-02-v2.1_<aktion>.png); eigene Hüfte, übrige Haltungen der Automatik, Stützhand underhand auf dem Griffpolster; Salven 3 Schuss im Takt 2 Bilder bei 30/s, Blitz klein im Kasten, Hülse rechts | E |
| `draw` | Ziehen | 23 (0.77 s) | Ready (17) | 42.7° | ego_BASIC-02-v2.1_draw.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-02-v2.1_<aktion>.png); eigene Hüfte, übrige Haltungen der Automatik, Stützhand underhand auf dem Griffpolster; Salven 3 Schuss im Takt 2 Bilder bei 30/s, Blitz klein im Kasten, Hülse rechts | M Ziehen 0,23 s bis Hüfte (Auto Rifle, Q-REF) + Ausfedern E; Klasse pulse_rifle: 25 → 23 Bilder (M Destiny-Anflug Automatik/Impuls/MG 20 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen Glidepath, Entscheidungsliste 4d; Gridskipper ADS ein 18 Bilder bis ruhig, Motiongen destiny2): aim_in 10 Bilder bei 30/s wie die Automatik; Ziehen erstes Modellbild → ruhig Smite of Merain 44, Insidious 49, Outbreak 47–48 Bilder bei 60/s (Motiongen destiny2 › Gapfill; Nutzerentscheid 31.10.2026) ≈ 47 → 23 (bis 0.33.1 Vorgabe 25)) |
| `holster` | Wegstecken | 8 (0.27 s) | HandOff (1), Holstered (8) | 42.5° | ego_BASIC-02-v2.1_holster.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-02-v2.1_<aktion>.png); eigene Hüfte, übrige Haltungen der Automatik, Stützhand underhand auf dem Griffpolster; Salven 3 Schuss im Takt 2 Bilder bei 30/s, Blitz klein im Kasten, Hülse rechts | M Destiny-Wechsel: Wegstecken 0,08–0,27 s (Motiongen wechsel › 4, Entscheidungsliste 6.1 A) → 0,27 s ohne TIME_SCALE (bis 0.14: 0,60 s); Ablauf E (CE: Holster ab aktueller Stellung) |
| `aim_in` | Hüfte → Zielen | 10 (0.33 s) | Aimed (9) | 28.0° | ego_BASIC-02-v2.1_aim_in.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-02-v2.1_<aktion>.png); eigene Hüfte, übrige Haltungen der Automatik, Stützhand underhand auf dem Griffpolster; Salven 3 Schuss im Takt 2 Bilder bei 30/s, Blitz klein im Kasten, Hülse rechts | E 0,30 s (CE-Handling Auto 0,39→0,20 s) |
| `aim_out` | Zielen → Hüfte | 8 (0.27 s) | Ready (8) | 28.0° | ego_BASIC-02-v2.1_aim_out.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-02-v2.1_<aktion>.png); eigene Hüfte, übrige Haltungen der Automatik, Stützhand underhand auf dem Griffpolster; Salven 3 Schuss im Takt 2 Bilder bei 30/s, Blitz klein im Kasten, Hülse rechts | E |
| `fire_hip` | Salven aus der Hüfte | 32 (1.07 s) | Fire (2) | 25.6° | ego_BASIC-02-v2.1_fire_hip.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-02-v2.1_<aktion>.png); eigene Hüfte, übrige Haltungen der Automatik, Stützhand underhand auf dem Griffpolster; Salven 3 Schuss im Takt 2 Bilder bei 30/s, Blitz klein im Kasten, Hülse rechts | M 720/min = 1 Schuss je 2,5 Bilder (Q-REF; bis 0.14 alle 2 Bilder ≈ 940/min); Rückstoß T 17,5 mm/3°; Klasse pulse_rifle: 540/min, Salve (n Schuss je Zug) (Schussbilder [2, 4, 6, 12, 14, 16, 22, 24, 26]) |
| `fire_ads` | Salven im Zielen | 32 (1.07 s) | AimFire (2) | 28.0° | ego_BASIC-02-v2.1_fire_ads.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-02-v2.1_<aktion>.png); eigene Hüfte, übrige Haltungen der Automatik, Stützhand underhand auf dem Griffpolster; Salven 3 Schuss im Takt 2 Bilder bei 30/s, Blitz klein im Kasten, Hülse rechts | M Kadenz wie fire_hip; Rückstoß im Zielen nach RECOIL ads_* (5.1 A: Visier steht, die Welt wandert) E; Klasse pulse_rifle: 540/min, Salve (n Schuss je Zug) (Schussbilder [2, 4, 6, 12, 14, 16, 22, 24, 26]) |
| `reload_tactical` | Nachladen mit Restmunition | 63 (2.10 s) | HandOff (5), MagOut (12), MagIn (36), HandOn (48), Ready (58) | 36.9° | ego_BASIC-02-v2.1_reload_tactical.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-02-v2.1_<aktion>.png); eigene Hüfte, übrige Haltungen der Automatik, Stützhand underhand auf dem Griffpolster; Salven 3 Schuss im Takt 2 Bilder bei 30/s, Blitz klein im Kasten, Hülse rechts | M MagIn ≈ 0,93 s; Ablauf T (Reload-Keys) mit Destiny-Kippen E; v2: Ausholen, Stoß bei MagIn, Nachfedern E |
| `reload_empty` | Nachladen aus leerem Zustand | 75 (2.50 s) | HandOff (6), MagOut (10), MagIn (35), Chamber (50), HandOn (60), Ready (70) | 37.0° | ego_BASIC-02-v2.1_reload_empty.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-02-v2.1_<aktion>.png); eigene Hüfte, übrige Haltungen der Automatik, Stützhand underhand auf dem Griffpolster; Salven 3 Schuss im Takt 2 Bilder bei 30/s, Blitz klein im Kasten, Hülse rechts | M leer 1,85 s, MagOut 0,25 s, MagIn 0,93 s (Q-REF Auto Rifle); Ladehebel E; v2: Ausholen, Stoß bei MagIn, Ruck beim Durchladen, Nachfedern E |
| `inspect` | Betrachten | 120 (4.00 s) | Start (20), End (118) | 41.3° | ego_BASIC-02-v2.1_inspect.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-02-v2.1_<aktion>.png); eigene Hüfte, übrige Haltungen der Automatik, Stützhand underhand auf dem Griffpolster; Salven 3 Schuss im Takt 2 Bilder bei 30/s, Blitz klein im Kasten, Hülse rechts | E nach Apex/CoD-Muster (Ego-Seite, dann Oberseite); Destiny hat keinen Ego-Inspect |
| `sprint` | Sprint: Beginn, Schleife, Ende | 60 (2.00 s) | SprintLoop (10), Ready (60) | 36.3° | ego_BASIC-02-v2.1_sprint.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-02-v2.1_<aktion>.png); eigene Hüfte, übrige Haltungen der Automatik, Stützhand underhand auf dem Griffpolster; Salven 3 Schuss im Takt 2 Bilder bei 30/s, Blitz klein im Kasten, Hülse rechts | E (CE: Waffe senkt sich und rollt zur Mitte); period = Doppelschritt (seitlich), vertikal je Schritt: 19 Bilder = 0,633 s → 3,16 Schritte/s, seitlich 1,58 Hz, Rollen ±3,5°, U-Bogen (oben an den Seitenumkehren) nach Motiongen REF 0.23 (Destiny 2, Automatik/Handfeuerwaffe gemessen). 0.9: 10 Bilder = 6 Schritte/s („tapsig“). 0.15: Hub 12/10 → 22/18 mm (seitlich/vertikal) für ≈ 10 % H / 13 % B im Bild wie die Destiny-Automatik (Entscheidungsliste 3.1 A, gemessen wie in Schritt 2: Oberkante, linke Kante) |
| `lowered` | Gesenkte Haltung / Wandnähe | 45 (1.50 s) | Lowered (10), Ready (45) | 37.1° | ego_BASIC-02-v2.1_lowered.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-02-v2.1_<aktion>.png); eigene Hüfte, übrige Haltungen der Automatik, Stützhand underhand auf dem Griffpolster; Salven 3 Schuss im Takt 2 Bilder bei 30/s, Blitz klein im Kasten, Hülse rechts | E |
| `walk` | Gehen (liegende Acht) | 60 (2.00 s) | – | 25.7° | ego_BASIC-02-v2.1_walk.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-02-v2.1_<aktion>.png); eigene Hüfte, übrige Haltungen der Automatik, Stützhand underhand auf dem Griffpolster; Salven 3 Schuss im Takt 2 Bilder bei 30/s, Blitz klein im Kasten, Hülse rechts | E (CE: liegende Acht) |
| `crouch` | Ducken | 30 (1.00 s) | Crouched (10) | 26.0° | ego_BASIC-02-v2.1_crouch.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-02-v2.1_<aktion>.png); eigene Hüfte, übrige Haltungen der Automatik, Stützhand underhand auf dem Griffpolster; Salven 3 Schuss im Takt 2 Bilder bei 30/s, Blitz klein im Kasten, Hülse rechts | E |
| `jump_land` | Sprung, Luftphase, Landung | 50 (1.67 s) | Air (10), Land (35) | 27.0° | ego_BASIC-02-v2.1_jump_land.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-02-v2.1_<aktion>.png); eigene Hüfte, übrige Haltungen der Automatik, Stützhand underhand auf dem Griffpolster; Salven 3 Schuss im Takt 2 Bilder bei 30/s, Blitz klein im Kasten, Hülse rechts | E (CE: Anheben, Landefeder) |
| `sprint_to_aim` | Sprint → Zielen | 18 (0.60 s) | SprintOut (0), Aimed (12) | 34.9° | ego_BASIC-02-v2.1_sprint_to_aim.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-02-v2.1_<aktion>.png); eigene Hüfte, übrige Haltungen der Automatik, Stützhand underhand auf dem Griffpolster; Salven 3 Schuss im Takt 2 Bilder bei 30/s, Blitz klein im Kasten, Hülse rechts | E (CE: ADS > Sprint) |
| `sprint_to_fire` | Sprint → Feuer | 26 (0.87 s) | SprintOut (0), Fire (7) | 34.9° | ego_BASIC-02-v2.1_sprint_to_fire.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-02-v2.1_<aktion>.png); eigene Hüfte, übrige Haltungen der Automatik, Stützhand underhand auf dem Griffpolster; Salven 3 Schuss im Takt 2 Bilder bei 30/s, Blitz klein im Kasten, Hülse rechts | E (CE: Fire > Sprint); Klasse pulse_rifle: 540/min, Salve (n Schuss je Zug) (Schussbilder [7, 9, 11, 17, 19, 21]) |
| `draw_aim` | Ziehen bei gehaltenem Zielen | 35 (1.17 s) | Ready (18), Aimed (30) | 42.7° | ego_BASIC-02-v2.1_draw_aim.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-02-v2.1_<aktion>.png); eigene Hüfte, übrige Haltungen der Automatik, Stützhand underhand auf dem Griffpolster; Salven 3 Schuss im Takt 2 Bilder bei 30/s, Blitz klein im Kasten, Hülse rechts | E (CE: Draw nicht unterbrechbar, ADS danach) |
| `reload_to_switch` | Nachladen → Waffenwechsel (Abbruch) | 38 (1.27 s) | HandOff (5), Cancel (18), Holstered (35) | 43.0° | ego_BASIC-02-v2.1_reload_to_switch.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-02-v2.1_<aktion>.png); eigene Hüfte, übrige Haltungen der Automatik, Stützhand underhand auf dem Griffpolster; Salven 3 Schuss im Takt 2 Bilder bei 30/s, Blitz klein im Kasten, Hülse rechts | E (CE: Reload bricht bei Wechsel ab, Holster ab aktueller Stellung) |

### Abdeckung der Matrixzeilen

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

## BASIC-T01-v2.1 – Portalkanone v2.1 (portal_cannon)

### Klassen- und Spielwerte

| Wert | Stand | Herkunft |
|---|---|---|
| Klasse | portal_cannon | Werkzeug der Familie (0.22 „Volley“): Hüfte nach Portal 2 (M) und Familienmaßen, Sprint als Klasse „Werkzeug“ E; Bedienung Linksklick A / Rechtsklick B ohne Zielen (Nutzer 27.10.2026 über Sightline: „A“ – „Linksklick = Portal A …, Rechtsklick = Portal B …, kein Zielen …, Abklingzeit 0,25 s als Datenfeld“; Präzision X zurückgestellt, docs/erweiterungen.md) |
| Kadenz | 240/min | Cube Escape (Q-CE-14/15): Linksklick Portal A (Cyan #1AD9FF), Rechtsklick Portal B (Orange #FF7314), Abklingzeit 0,25 s → 240/min, Kick E 0,6 der Automatik (Portal 2: obere Klaue ≈ 7 % H im ersten Schussbild, portal2.md), Reichweite 24 m, ohne Streuung (Sichtlinie zum Fadenkreuz), Munition keine (magazine 0 = unbegrenzt); Ring je Schuss 120° in 10 Bildern bei 30/s (Modul t01 fire_a/fire_b), Richtung je Portal; ohne Mündungsfeuer und ohne Bahnstufe (E: Werkzeug, Rückmeldung über Ring und Treffermarke in Portalfarbe) |
| Magazin | 0 | Cube Escape (Q-CE-14/15): Linksklick Portal A (Cyan #1AD9FF), Rechtsklick Portal B (Orange #FF7314), Abklingzeit 0,25 s → 240/min, Kick E 0,6 der Automatik (Portal 2: obere Klaue ≈ 7 % H im ersten Schussbild, portal2.md), Reichweite 24 m, ohne Streuung (Sichtlinie zum Fadenkreuz), Munition keine (magazine 0 = unbegrenzt); Ring je Schuss 120° in 10 Bildern bei 30/s (Modul t01 fire_a/fire_b), Richtung je Portal; ohne Mündungsfeuer und ohne Bahnstufe (E: Werkzeug, Rückmeldung über Ring und Treffermarke in Portalfarbe) |
| Feuerart | `single` – Einzelschuss je Klick (Werkzeug) | Spec (META fire, data/specs); Unity: gameplay.fire_mode (0.20) |
| Weltzoom im Zielen | kein Zielen (Werkzeug ohne Visier) | M Glidepath (Entscheidungsliste 1.2 A, basic/reticles.py › CLASS_ZOOM) |
| Hüft-Fadenkreuz | ring_dot 4.5 % H | entworfen (Werkzeug, Portal 2 / Cube Escape) (4.1 A / 4.2 A, basic/reticles.py › HIP) |
| Sprint-Fadenkreuz | aus | basic/reticles.py › HIP.sprint (4.1 A) |
| Bedienung | Portal A Linksklick (#1AD9FF, Ring im Uhrzeigersinn); Portal B Rechtsklick (#FF7314, Ring gegen den Uhrzeigersinn); kein Zielen, kein Nachladen; Ring 120° in 0.333 s; Reichweite 24 m | Werkzeug der Familie (0.22 „Volley“): Hüfte nach Portal 2 (M) und Familienmaßen, Sprint als Klasse „Werkzeug“ E; Bedienung Linksklick A / Rechtsklick B ohne Zielen (Nutzer 27.10.2026 über Sightline: „A“ – „Linksklick = Portal A …, Rechtsklick = Portal B …, kein Zielen …, Abklingzeit 0,25 s als Datenfeld“; Präzision X zurückgestellt, docs/erweiterungen.md) |
| Ohne | Aktionen `aim_in`, `aim_out`, `fire_hip`, `fire_ads`, `reload_tactical`, `reload_empty`, `sprint_to_aim`, `draw_aim`, `reload_to_switch`; Haltungen `ads`, `reload` | Werkzeug ohne Visier und Magazin (0.17): kein Zielen, kein Nachladen; Feuer als fire_a/fire_b (Portale) |
| Bahnstufe je Schuss | 0.00 % H | Cube Escape (Q-CE-14/15): Linksklick Portal A (Cyan #1AD9FF), Rechtsklick Portal B (Orange #FF7314), Abklingzeit 0,25 s → 240/min, Kick E 0,6 der Automatik (Portal 2: obere Klaue ≈ 7 % H im ersten Schussbild, portal2.md), Reichweite 24 m, ohne Streuung (Sichtlinie zum Fadenkreuz), Munition keine (magazine 0 = unbegrenzt); Ring je Schuss 120° in 10 Bildern bei 30/s (Modul t01 fire_a/fire_b), Richtung je Portal; ohne Mündungsfeuer und ohne Bahnstufe (E: Werkzeug, Rückmeldung über Ring und Treffermarke in Portalfarbe) |
| Haltung `hip` | Socket_Hand [-0.16, -0.4, -0.24], Ziel [1.4, -3.0, 0.0], Rollen -20° | M Portal-2-Portalkanone: rechts unten, vorderes Rohrende ≈ 57/75 %, beim Gehen 54–63/68–75 %, Rohr von rechts unten nach links oben (cubeescape-reference/docs/portal2.md › weißes Modell); Lage E, gerechnet auf Achskrone 56,9/71,2 %; quer gestellt, damit die linke Flanke beide Kerne zeigt (Nutzer 27.10.2026: „Schade dass man von der Portal Gun die Farb-Elemente nicht sieht“; von vier Varianten c14: Kern A und B sichtbar, Achskrone im Band); Kerbe (Leitkante) rechts im Bild; Stützhand am Vordergriff unter der Unterlippe |
| Haltung `sprint` | Socket_Hand [-0.1, -0.34, -0.22], Ziel [0.6, -2.1, -0.4], Rollen 30° | E (Klasse Werkzeug, in der Entscheidungsliste nicht gemessen; Portal 2 ohne eigene Sprintpose): Trageform der Kurzwaffen nach 3.2 A (MP: tief, nach links gerollt, Mündung ≈ 43/80 %), Rollen +30° statt +40° wegen der breiten Eischale; gerechnet Achskrone 44,3/80,4 % |
| Haltung `crouch` | Socket_Hand [-0.15, -0.39, -0.255], Rollen -17° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `air` | Socket_Hand [-0.16, -0.4, -0.225], Rollen -22° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `lowered` | Socket_Hand [-0.14, -0.36, -0.26], Rollen -16° | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| Mündungsfeuer | keins (Werkzeug) | Cube Escape (Q-CE-14/15): Linksklick Portal A (Cyan #1AD9FF), Rechtsklick Portal B (Orange #FF7314), Abklingzeit 0,25 s → 240/min, Kick E 0,6 der Automatik (Portal 2: obere Klaue ≈ 7 % H im ersten Schussbild, portal2.md), Reichweite 24 m, ohne Streuung (Sichtlinie zum Fadenkreuz), Munition keine (magazine 0 = unbegrenzt); Ring je Schuss 120° in 10 Bildern bei 30/s (Modul t01 fire_a/fire_b), Richtung je Portal; ohne Mündungsfeuer und ohne Bahnstufe (E: Werkzeug, Rückmeldung über Ring und Treffermarke in Portalfarbe) |
| Hülsen | keine | Waffe ohne Feld EJECT |
| Rückstoß | ego.RECOIL (gemeinsam) | übertragen von der Automatik: Säule 1 % H je Schuss, im Zielen wandert die Welt (5.1 A / 5.2 A); Werkzeug: Modellkick der Aktion (fire_a/fire_b kick 0,6), keine Bahnstufe (E; Portal 2: obere Klaue ≈ 7 % H im ersten Schussbild) |
| Wirkung | keine | Werkzeug: eigene Treffermarke in Portalfarbe (0.22), keine Wirkung (ego.PAYLOAD, Entscheidungsliste Block 9) |
| Sprint-Frequenz | 3,16 / 1,58 Hz (gemeinsam) | M Destiny Automatik/Handfeuerwaffe, für alle Klassen bis zu neuen Messungen (3c) |
| Griffe | grip, support | Modul-Feld EGO_GRIPS |
| Live-Teile | trigger = trigger, bolt = , port = , ring = emitter_ring | Modul-Feld EGO_LIVE |

### Haltungen

| Haltung | Socket_Hand (m) | Handgelenk max | Herkunft |
|---|---|---|---|
| `hip` | [-0.16, -0.4, -0.24] | 32.8° | M Portal-2-Portalkanone: rechts unten, vorderes Rohrende ≈ 57/75 %, beim Gehen 54–63/68–75 %, Rohr von rechts unten nach links oben (cubeescape-reference/docs/portal2.md › weißes Modell); Lage E, gerechnet auf Achskrone 56,9/71,2 %; quer gestellt, damit die linke Flanke beide Kerne zeigt (Nutzer 27.10.2026: „Schade dass man von der Portal Gun die Farb-Elemente nicht sieht“; von vier Varianten c14: Kern A und B sichtbar, Achskrone im Band); Kerbe (Leitkante) rechts im Bild; Stützhand am Vordergriff unter der Unterlippe |
| `sprint` | [-0.1, -0.34, -0.22] | 32.9° | E (Klasse Werkzeug, in der Entscheidungsliste nicht gemessen; Portal 2 ohne eigene Sprintpose): Trageform der Kurzwaffen nach 3.2 A (MP: tief, nach links gerollt, Mündung ≈ 43/80 %), Rollen +30° statt +40° wegen der breiten Eischale; gerechnet Achskrone 44,3/80,4 % |
| `lowered` | [-0.14, -0.36, -0.26] | 43.9° | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| `crouch` | [-0.15, -0.39, -0.255] | 32.9° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `air` | [-0.16, -0.4, -0.225] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `holstered` | [-0.24, -0.25, -0.62] | nur in Aktionen geprüft | E (unter dem Bild) |
| `inspect_l` | [-0.06, -0.36, -0.16] | 40.4° | E (Ego-Seite zeigt zur Kamera) |
| `inspect_r` | [-0.1, -0.36, -0.12] | 14.9° | E (Oberseite und rechte Seite) |

### Aktionen

| Aktion | Beschreibung | Bilder | Marker (Bild) | Handgelenk max | Clip | Sichtung | Herkunft |
|---|---|---|---|---|---|---|---|
| `idle_hip` | Ruhe an der Hüfte (Atmen) | 75 (2.50 s) | – | 33.0° | ego_BASIC-T01-v2.1_idle_hip.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-T01-v2.1_<aktion>.png); fire_a Ring im, fire_b gegen den Uhrzeigersinn 120°, ohne Mündungsfeuer und Hülsen; ohne Zielen und Nachladen | E |
| `draw` | Ziehen | 25 (0.83 s) | Ready (18) | 45.0° | ego_BASIC-T01-v2.1_draw.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-T01-v2.1_<aktion>.png); fire_a Ring im, fire_b gegen den Uhrzeigersinn 120°, ohne Mündungsfeuer und Hülsen; ohne Zielen und Nachladen | M Ziehen 0,23 s bis Hüfte (Auto Rifle, Q-REF) + Ausfedern E |
| `holster` | Wegstecken | 8 (0.27 s) | HandOff (1), Holstered (8) | 45.0° | ego_BASIC-T01-v2.1_holster.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-T01-v2.1_<aktion>.png); fire_a Ring im, fire_b gegen den Uhrzeigersinn 120°, ohne Mündungsfeuer und Hülsen; ohne Zielen und Nachladen | M Destiny-Wechsel: Wegstecken 0,08–0,27 s (Motiongen wechsel › 4, Entscheidungsliste 6.1 A) → 0,27 s ohne TIME_SCALE (bis 0.14: 0,60 s); Ablauf E (CE: Holster ab aktueller Stellung) |
| `inspect` | Betrachten | 120 (4.00 s) | Start (20), End (118) | 41.5° | ego_BASIC-T01-v2.1_inspect.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-T01-v2.1_<aktion>.png); fire_a Ring im, fire_b gegen den Uhrzeigersinn 120°, ohne Mündungsfeuer und Hülsen; ohne Zielen und Nachladen | E nach Apex/CoD-Muster (Ego-Seite, dann Oberseite); Destiny hat keinen Ego-Inspect |
| `sprint` | Sprint: Beginn, Schleife, Ende | 60 (2.00 s) | SprintLoop (10), Ready (60) | 33.7° | ego_BASIC-T01-v2.1_sprint.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-T01-v2.1_<aktion>.png); fire_a Ring im, fire_b gegen den Uhrzeigersinn 120°, ohne Mündungsfeuer und Hülsen; ohne Zielen und Nachladen | E (CE: Waffe senkt sich und rollt zur Mitte); period = Doppelschritt (seitlich), vertikal je Schritt: 19 Bilder = 0,633 s → 3,16 Schritte/s, seitlich 1,58 Hz, Rollen ±3,5°, U-Bogen (oben an den Seitenumkehren) nach Motiongen REF 0.23 (Destiny 2, Automatik/Handfeuerwaffe gemessen). 0.9: 10 Bilder = 6 Schritte/s („tapsig“). 0.15: Hub 12/10 → 22/18 mm (seitlich/vertikal) für ≈ 10 % H / 13 % B im Bild wie die Destiny-Automatik (Entscheidungsliste 3.1 A, gemessen wie in Schritt 2: Oberkante, linke Kante) |
| `lowered` | Gesenkte Haltung / Wandnähe | 45 (1.50 s) | Lowered (10), Ready (45) | 44.2° | ego_BASIC-T01-v2.1_lowered.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-T01-v2.1_<aktion>.png); fire_a Ring im, fire_b gegen den Uhrzeigersinn 120°, ohne Mündungsfeuer und Hülsen; ohne Zielen und Nachladen | E |
| `walk` | Gehen (liegende Acht) | 60 (2.00 s) | – | 32.9° | ego_BASIC-T01-v2.1_walk.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-T01-v2.1_<aktion>.png); fire_a Ring im, fire_b gegen den Uhrzeigersinn 120°, ohne Mündungsfeuer und Hülsen; ohne Zielen und Nachladen | E (CE: liegende Acht) |
| `crouch` | Ducken | 30 (1.00 s) | Crouched (10) | 33.0° | ego_BASIC-T01-v2.1_crouch.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-T01-v2.1_<aktion>.png); fire_a Ring im, fire_b gegen den Uhrzeigersinn 120°, ohne Mündungsfeuer und Hülsen; ohne Zielen und Nachladen | E |
| `jump_land` | Sprung, Luftphase, Landung | 50 (1.67 s) | Air (10), Land (35) | 34.2° | ego_BASIC-T01-v2.1_jump_land.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-T01-v2.1_<aktion>.png); fire_a Ring im, fire_b gegen den Uhrzeigersinn 120°, ohne Mündungsfeuer und Hülsen; ohne Zielen und Nachladen | E (CE: Anheben, Landefeder) |
| `sprint_to_fire` | Sprint → Feuer | 26 (0.87 s) | SprintOut (0), Fire (7) | 33.6° | ego_BASIC-T01-v2.1_sprint_to_fire.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-T01-v2.1_<aktion>.png); fire_a Ring im, fire_b gegen den Uhrzeigersinn 120°, ohne Mündungsfeuer und Hülsen; ohne Zielen und Nachladen | E (CE: Fire > Sprint); Klasse portal_cannon: 240/min, Einzelschuss je Klick (Werkzeug) (Schussbilder [7, 14]) |
| `fire_a` | Portal A (Linksklick): Ring dreht 120° im Uhrzeigersinn (von hinten) | 18 (0.60 s) | Fire (2) | 32.8° | ego_BASIC-T01-v2.1_fire_a.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-T01-v2.1_<aktion>.png); fire_a Ring im, fire_b gegen den Uhrzeigersinn 120°, ohne Mündungsfeuer und Hülsen; ohne Zielen und Nachladen | Ablauf aus dem Modul (t01 ACTIONS fire_a, 0.17): Ring 2 → 12 Bilder; Kick aus gameplay.kick |
| `fire_b` | Portal B (Rechtsklick): Ring dreht 120° gegen den Uhrzeigersinn | 18 (0.60 s) | Fire (2) | 32.8° | ego_BASIC-T01-v2.1_fire_b.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-T01-v2.1_<aktion>.png); fire_a Ring im, fire_b gegen den Uhrzeigersinn 120°, ohne Mündungsfeuer und Hülsen; ohne Zielen und Nachladen | wie fire_a, Gegenrichtung (t01 ACTIONS fire_b) |

### Abdeckung der Matrixzeilen

| Zeile | durch Aktion | Status |
|---|---|---|
| `pose_rest` | `idle_hip` | dargestellt (mit Händen) |
| `pose_hip` | `idle_hip` | dargestellt (mit Händen) |
| `draw` | `draw` | dargestellt (mit Händen) |
| `ready` | `draw` | dargestellt (mit Händen) |
| `holster` | `holster` | dargestellt (mit Händen) |
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
| `tr_sprint_fire` | `sprint_to_fire` | dargestellt (mit Händen) |

## BASIC-04-v2.1 – Trommel v2.1 (hand_cannon)

### Klassen- und Spielwerte

| Wert | Stand | Herkunft |
|---|---|---|
| Klasse | hand_cannon | Ego-Übertrag 0.33 „Armory“ P1: Hüfte, Sprint, Anflug, Ziehen und Nachladen nach Motiongen (Handfeuerwaffe), Trommelablauf E |
| Kadenz | 140/min | S Annual Skate 140/min, Magazin 10 (Menü, Motiongen waffenwerte:283, destiny2:94; Rahmen 100–257/min, 8–16 Schuss); gemessen Abstand 27 Bilder bei 60/s = 133/min „vereinbar“ (destiny2:94); Feuerart aus der Spec (Spannabzug, ein Schuss je Zug); Bahnstufe 0,017 M: Netto-Rest vor dem Folgeschuss 1,7 pp H (Hochimpuls bis 7,6 pp, Motiongen rueckstoss:106); Kick 2,5 E: Modell ≈ 6 % hoch und 8° gekippt (destiny2:492) gegen Automatik-Kick 3° je Schuss |
| Magazin | 10 | S Annual Skate 140/min, Magazin 10 (Menü, Motiongen waffenwerte:283, destiny2:94; Rahmen 100–257/min, 8–16 Schuss); gemessen Abstand 27 Bilder bei 60/s = 133/min „vereinbar“ (destiny2:94); Feuerart aus der Spec (Spannabzug, ein Schuss je Zug); Bahnstufe 0,017 M: Netto-Rest vor dem Folgeschuss 1,7 pp H (Hochimpuls bis 7,6 pp, Motiongen rueckstoss:106); Kick 2,5 E: Modell ≈ 6 % hoch und 8° gekippt (destiny2:492) gegen Automatik-Kick 3° je Schuss |
| Feuerart | `semi_auto` – Einzelfeuer (ein Schuss je Zug) | Spec (META fire, data/specs); Unity: gameplay.fire_mode (0.20) |
| Weltzoom im Zielen | 1.15 | M Glidepath (Entscheidungsliste 1.2 A, basic/reticles.py › CLASS_ZOOM) |
| Hüft-Fadenkreuz | brackets 6.0 % H | gemessen (Glidepath, ≈ 6 % H) (4.1 A / 4.2 A, basic/reticles.py › HIP) |
| Sprint-Fadenkreuz | aus | basic/reticles.py › HIP.sprint (4.1 A) |
| Bahnstufe je Schuss | 1.70 % H | S Annual Skate 140/min, Magazin 10 (Menü, Motiongen waffenwerte:283, destiny2:94; Rahmen 100–257/min, 8–16 Schuss); gemessen Abstand 27 Bilder bei 60/s = 133/min „vereinbar“ (destiny2:94); Feuerart aus der Spec (Spannabzug, ein Schuss je Zug); Bahnstufe 0,017 M: Netto-Rest vor dem Folgeschuss 1,7 pp H (Hochimpuls bis 7,6 pp, Motiongen rueckstoss:106); Kick 2,5 E: Modell ≈ 6 % hoch und 8° gekippt (destiny2:492) gegen Automatik-Kick 3° je Schuss |
| Haltung `hip` | Socket_Hand [-0.113, -0.441, -0.152], Ziel [0.313, -3.407, -0.312], Rollen 12.0° | M cubeescape-reference huefte.json (Destiny 2, Mündung 57/63, 54/69, Kimme 64/66, 62/62, Griffhand 67/87, 67/89); Lage E: Ausgleichsrechnung gegen diese Werte (0.33, Abgleich aller Waffen; Nutzer 31.10.2026 „Ja, nachziehen“ – bis dahin nur die Mündung eingestellt, die Griffhand lag 9–12 pp zu tief), gerechnet (Socket_Muzzle, Socket_Sight bzw. Socket_Reticle, Socket_Hand) Mündung 55,7/66,0 %, Kimme 63,4/63,4 %, Griffhand 66,7/89,9 % (Rollen 12° statt 13°: der Unterarm in lowered lag an der Kante der Handgelenksklemme, Unity wich dort 0,204° ab) |
| Haltung `sprint` | Socket_Hand [-0.1, -0.36, -0.15], Ziel [-0.02, -0.8, 1.6], Rollen 0° | M Destiny-Handfeuerwaffe Sprint: Waffe senkrecht, Lauf am oberen Rand, Körper 62–70 % B, hoch rechts (Motiongen destiny2:562/467); Lage E, gerechnet Mündung 68,4/10,8 %, Körper 66–72 % B |
| Haltung `reload` | Socket_Hand [-0.07, -0.37, -0.1], Ziel [0.6, -1.2, 1.05], Rollen 10° | M Destiny-Revolver: Hochdrehen 0,13 s, Trommel zur Kamera (Motiongen destiny2:492); Lage E: Mündung nach links oben, linke Seite mit der ausgeschwenkten Trommel zeigt zur Kamera; 4 cm weiter weg als der erste Entwurf (Stützhand verdeckte das halbe Bild); 0.34: 5 cm höher, damit das Trommelende und die fallenden Hülsen im Bild liegen |
| Haltung `crouch` | Socket_Hand [-0.103, -0.431, -0.167], Rollen 15.0° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `air` | Socket_Hand [-0.113, -0.441, -0.137], Rollen 10.0° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `lowered` | Socket_Hand [-0.093, -0.401, -0.172], Rollen 16.0° | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| Dauer `aim_in` | 3 Bilder bei 30/s (0.100 s) | M Destiny-Handfeuerwaffe: ADS ein 10 Bilder bei 60/s erste Bewegung → Ruhe, aus 9–10 (The Last Word, Motiongen destiny2:584) → wie die MP 3 und 2,4 Bilder bei 30/s (gleiche Umrechnung mit dem Zielen-Nachlauf, Entscheidungsliste 4d); Ziehen Bad News 16 Bilder bei 60/s bis hüftähnlich + 19 bis ruhig (Motiongen wechsel:51) = 0,58 s → 18 Bilder (Automatik 25) |
| Dauer `aim_out` | 2.4 Bilder bei 30/s (0.080 s) | M Destiny-Handfeuerwaffe: ADS ein 10 Bilder bei 60/s erste Bewegung → Ruhe, aus 9–10 (The Last Word, Motiongen destiny2:584) → wie die MP 3 und 2,4 Bilder bei 30/s (gleiche Umrechnung mit dem Zielen-Nachlauf, Entscheidungsliste 4d); Ziehen Bad News 16 Bilder bei 60/s bis hüftähnlich + 19 bis ruhig (Motiongen wechsel:51) = 0,58 s → 18 Bilder (Automatik 25) |
| Dauer `draw` | 18 Bilder bei 30/s (0.600 s) | M Destiny-Handfeuerwaffe: ADS ein 10 Bilder bei 60/s erste Bewegung → Ruhe, aus 9–10 (The Last Word, Motiongen destiny2:584) → wie die MP 3 und 2,4 Bilder bei 30/s (gleiche Umrechnung mit dem Zielen-Nachlauf, Entscheidungsliste 4d); Ziehen Bad News 16 Bilder bei 60/s bis hüftähnlich + 19 bis ruhig (Motiongen wechsel:51) = 0,58 s → 18 Bilder (Automatik 25) |
| Mündungsfeuer | 33 ms | M Destiny: 1–2 Bilder bei 60/s, Kern klein, Seitenflammen breiter, Zielen Automatik ≈ 20 % der Öffnung (Motiongen muendung › 6, Entscheidungsliste 5.3 A); Maße und Farben E (Stil v2.1) |
| Hülsen | revolver (30 × 11.2 mm) | M beim Nachladen (Motiongen muendung › 3/5); E: hinten aus den Kammern, langsam nach außen (vom Rahmen weg, zur Kamera) und etwas nach vorn, dann fallend, 0,8 s sichtbar; Bahn: M Destiny: Hülse im 1. Blitzbild oder 1 Bild danach, rechts/rechts unten (Motiongen muendung › 6, Entscheidungsliste 5d/5.4 A); Geschwindigkeit, Drehung, Lebensdauer E |
| Rückstoß | ego.RECOIL (gemeinsam) | übertragen von der Automatik: Säule 1 % H je Schuss, im Zielen wandert die Welt (5.1 A / 5.2 A); Werkzeug: Modellkick der Aktion (fire_a/fire_b kick 0,6), keine Bahnstufe (E; Portal 2: obere Klaue ≈ 7 % H im ersten Schussbild) |
| Wirkung | Kugel, Einschlag heavy | M keine Spur, kein Loch sichtbar (REF 0.36 › 7 Fußnote 1); Einschlag schwer E, Loch E (180) (ego.PAYLOAD, Entscheidungsliste Block 9) |
| Sprint-Frequenz | 3,16 / 1,58 Hz (gemeinsam) | M Destiny Automatik/Handfeuerwaffe, für alle Klassen bis zu neuen Messungen (3c) |
| Griffe | grip, support, mag, charge | Modul-Feld EGO_GRIPS |
| Live-Teile | trigger = trigger, bolt = hammer, port = , index = cylinder | Modul-Feld EGO_LIVE |

### Haltungen

| Haltung | Socket_Hand (m) | Handgelenk max | Herkunft |
|---|---|---|---|
| `hip` | [-0.113, -0.441, -0.152] | nur in Aktionen geprüft | M cubeescape-reference huefte.json (Destiny 2, Mündung 57/63, 54/69, Kimme 64/66, 62/62, Griffhand 67/87, 67/89); Lage E: Ausgleichsrechnung gegen diese Werte (0.33, Abgleich aller Waffen; Nutzer 31.10.2026 „Ja, nachziehen“ – bis dahin nur die Mündung eingestellt, die Griffhand lag 9–12 pp zu tief), gerechnet (Socket_Muzzle, Socket_Sight bzw. Socket_Reticle, Socket_Hand) Mündung 55,7/66,0 %, Kimme 63,4/63,4 %, Griffhand 66,7/89,9 % (Rollen 12° statt 13°: der Unterarm in lowered lag an der Kante der Handgelenksklemme, Unity wich dort 0,204° ab) |
| `ads` | [0.0, 0.0, 0.0] | nur in Aktionen geprüft | Visier-Standard v2: Socket_Eye ist der Augenpunkt, liegt in der Kamera; Waffenmodell ungezoomt, Welt zoomt je Klasse |
| `sprint` | [-0.1, -0.36, -0.15] | nur in Aktionen geprüft | M Destiny-Handfeuerwaffe Sprint: Waffe senkrecht, Lauf am oberen Rand, Körper 62–70 % B, hoch rechts (Motiongen destiny2:562/467); Lage E, gerechnet Mündung 68,4/10,8 %, Körper 66–72 % B |
| `lowered` | [-0.093, -0.401, -0.172] | nur in Aktionen geprüft | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| `crouch` | [-0.103, -0.431, -0.167] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `air` | [-0.113, -0.441, -0.137] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `holstered` | [-0.24, -0.25, -0.62] | nur in Aktionen geprüft | E (unter dem Bild) |
| `reload` | [-0.07, -0.37, -0.1] | nur in Aktionen geprüft | M Destiny-Revolver: Hochdrehen 0,13 s, Trommel zur Kamera (Motiongen destiny2:492); Lage E: Mündung nach links oben, linke Seite mit der ausgeschwenkten Trommel zeigt zur Kamera; 4 cm weiter weg als der erste Entwurf (Stützhand verdeckte das halbe Bild); 0.34: 5 cm höher, damit das Trommelende und die fallenden Hülsen im Bild liegen |
| `inspect_l` | [-0.06, -0.36, -0.16] | nur in Aktionen geprüft | E (Ego-Seite zeigt zur Kamera) |
| `inspect_r` | [-0.1, -0.36, -0.12] | nur in Aktionen geprüft | E (Oberseite und rechte Seite) |

### Aktionen

| Aktion | Beschreibung | Bilder | Marker (Bild) | Handgelenk max | Clip | Sichtung | Herkunft |
|---|---|---|---|---|---|---|---|
| `idle_hip` | Ruhe an der Hüfte (Atmen) | 75 (2.50 s) | – | offen° | offen | offen | E |
| `draw` | Ziehen | 18 (0.60 s) | Ready (13) | offen° | ego_BASIC-04-v2.1_draw.mp4 | offen | M Ziehen 0,23 s bis Hüfte (Auto Rifle, Q-REF) + Ausfedern E; Klasse hand_cannon: 25 → 18 Bilder (M Destiny-Handfeuerwaffe: ADS ein 10 Bilder bei 60/s erste Bewegung → Ruhe, aus 9–10 (The Last Word, Motiongen destiny2:584) → wie die MP 3 und 2,4 Bilder bei 30/s (gleiche Umrechnung mit dem Zielen-Nachlauf, Entscheidungsliste 4d); Ziehen Bad News 16 Bilder bei 60/s bis hüftähnlich + 19 bis ruhig (Motiongen wechsel:51) = 0,58 s → 18 Bilder (Automatik 25)) |
| `holster` | Wegstecken | 8 (0.27 s) | HandOff (1), Holstered (8) | offen° | offen | offen | M Destiny-Wechsel: Wegstecken 0,08–0,27 s (Motiongen wechsel › 4, Entscheidungsliste 6.1 A) → 0,27 s ohne TIME_SCALE (bis 0.14: 0,60 s); Ablauf E (CE: Holster ab aktueller Stellung) |
| `aim_in` | Hüfte → Zielen | 3 (0.10 s) | Aimed (3) | offen° | offen | offen | E 0,30 s (CE-Handling Auto 0,39→0,20 s); Klasse hand_cannon: 10 → 3 Bilder (M Destiny-Handfeuerwaffe: ADS ein 10 Bilder bei 60/s erste Bewegung → Ruhe, aus 9–10 (The Last Word, Motiongen destiny2:584) → wie die MP 3 und 2,4 Bilder bei 30/s (gleiche Umrechnung mit dem Zielen-Nachlauf, Entscheidungsliste 4d); Ziehen Bad News 16 Bilder bei 60/s bis hüftähnlich + 19 bis ruhig (Motiongen wechsel:51) = 0,58 s → 18 Bilder (Automatik 25)) |
| `aim_out` | Zielen → Hüfte | 3 (0.10 s) | Ready (2) | offen° | offen | offen | E; Klasse hand_cannon: 8 → 2.4 Bilder (M Destiny-Handfeuerwaffe: ADS ein 10 Bilder bei 60/s erste Bewegung → Ruhe, aus 9–10 (The Last Word, Motiongen destiny2:584) → wie die MP 3 und 2,4 Bilder bei 30/s (gleiche Umrechnung mit dem Zielen-Nachlauf, Entscheidungsliste 4d); Ziehen Bad News 16 Bilder bei 60/s bis hüftähnlich + 19 bis ruhig (Motiongen wechsel:51) = 0,58 s → 18 Bilder (Automatik 25)) |
| `fire_hip` | Dauerfeuer aus der Hüfte | 32 (1.07 s) | Fire (2) | offen° | offen | offen | M 720/min = 1 Schuss je 2,5 Bilder (Q-REF; bis 0.14 alle 2 Bilder ≈ 940/min); Rückstoß T 17,5 mm/3°; Klasse hand_cannon: 140/min, Einzelfeuer (ein Schuss je Zug) (Schussbilder [2, 14]) |
| `fire_ads` | Dauerfeuer im Zielen | 32 (1.07 s) | AimFire (2) | offen° | offen | offen | M Kadenz wie fire_hip; Rückstoß im Zielen nach RECOIL ads_* (5.1 A: Visier steht, die Welt wandert) E; Klasse hand_cannon: 140/min, Einzelfeuer (ein Schuss je Zug) (Schussbilder [2, 14]) |
| `reload_tactical` | Nachladen (Trommel: ausschwenken, auswerfen, laden, zuklappen) | 45 (1.50 s) | HandOff (2), MagOut (9), Eject (10), MagIn (26), Chamber (30), HandOn (36), Ready (41) | offen° | ego_BASIC-04-v2.1_reload_tactical.mp4 | offen | M Destiny-Revolver aus der Hüfte 1,0 s: Hochdrehen 0,13, Trommel 0,62, Schließen 0,2 s, Zähler bei ≈ 70 % (Motiongen destiny2:492; älterer Clip Munition 1,4 s, ausgefedert 2,1 s, destiny2:119) → 36 Bilder, MagIn bei 21; Ablauf E (Riegel mit dem Daumen der Stützhand, Kran ausschwenken, Auswerfen mit Hochreißen, Laden von vorn, Zuklappen mit Handgelenkschwung); Hülsen beim Auswerfen nicht dargestellt (Entscheidungsliste) |
| `reload_empty` | Nachladen (Trommel: ausschwenken, auswerfen, laden, zuklappen), auch leer | 45 (1.50 s) | HandOff (2), MagOut (9), Eject (10), MagIn (26), Chamber (30), HandOn (36), Ready (41) | offen° | offen | offen | M Destiny-Revolver aus der Hüfte 1,0 s: Hochdrehen 0,13, Trommel 0,62, Schließen 0,2 s, Zähler bei ≈ 70 % (Motiongen destiny2:492; älterer Clip Munition 1,4 s, ausgefedert 2,1 s, destiny2:119) → 36 Bilder, MagIn bei 21; Ablauf E (Riegel mit dem Daumen der Stützhand, Kran ausschwenken, Auswerfen mit Hochreißen, Laden von vorn, Zuklappen mit Handgelenkschwung); Hülsen beim Auswerfen nicht dargestellt (Entscheidungsliste) |
| `inspect` | Betrachten | 120 (4.00 s) | Start (20), End (118) | offen° | offen | offen | E nach Apex/CoD-Muster (Ego-Seite, dann Oberseite); Destiny hat keinen Ego-Inspect |
| `sprint` | Sprint: Beginn, Schleife, Ende | 60 (2.00 s) | SprintLoop (10), Ready (60) | offen° | ego_BASIC-04-v2.1_sprint.mp4 | offen | E (CE: Waffe senkt sich und rollt zur Mitte); period = Doppelschritt (seitlich), vertikal je Schritt: 19 Bilder = 0,633 s → 3,16 Schritte/s, seitlich 1,58 Hz, Rollen ±3,5°, U-Bogen (oben an den Seitenumkehren) nach Motiongen REF 0.23 (Destiny 2, Automatik/Handfeuerwaffe gemessen). 0.9: 10 Bilder = 6 Schritte/s („tapsig“). 0.15: Hub 12/10 → 22/18 mm (seitlich/vertikal) für ≈ 10 % H / 13 % B im Bild wie die Destiny-Automatik (Entscheidungsliste 3.1 A, gemessen wie in Schritt 2: Oberkante, linke Kante); Klasse hand_cannon: Hub (0.0068, 0.0234) (M Destiny-Handfeuerwaffe Sprint-Hub ≈ 13 % H / 4 % B bei 3,16 Hz (Motiongen destiny2:467): Automatik 0.022/0.018 m ergab 13 % B / 10 % H → seitlich × 4/13, senkrecht × 13/10) |
| `lowered` | Gesenkte Haltung / Wandnähe | 45 (1.50 s) | Lowered (10), Ready (45) | offen° | offen | offen | E |
| `walk` | Gehen (liegende Acht) | 60 (2.00 s) | – | offen° | offen | offen | E (CE: liegende Acht) |
| `crouch` | Ducken | 30 (1.00 s) | Crouched (10) | offen° | offen | offen | E |
| `jump_land` | Sprung, Luftphase, Landung | 50 (1.67 s) | Air (10), Land (35) | offen° | offen | offen | E (CE: Anheben, Landefeder) |
| `sprint_to_aim` | Sprint → Zielen | 18 (0.60 s) | SprintOut (0), Aimed (12) | offen° | offen | offen | E (CE: ADS > Sprint) |
| `sprint_to_fire` | Sprint → Feuer | 26 (0.87 s) | SprintOut (0), Fire (7) | offen° | offen | offen | E (CE: Fire > Sprint); Klasse hand_cannon: 140/min, Einzelfeuer (ein Schuss je Zug) (Schussbilder [7, 19]) |
| `draw_aim` | Ziehen bei gehaltenem Zielen | 35 (1.17 s) | Ready (18), Aimed (30) | offen° | offen | offen | E (CE: Draw nicht unterbrechbar, ADS danach) |
| `reload_to_switch` | Nachladen → Waffenwechsel (Abbruch) | 38 (1.27 s) | HandOff (5), Cancel (18), Holstered (35) | offen° | offen | offen | E (CE: Reload bricht bei Wechsel ab, Holster ab aktueller Stellung) |

### Abdeckung der Matrixzeilen

| Zeile | durch Aktion | Status |
|---|---|---|
| `pose_rest` | `idle_hip` | offen (nicht gesichtet) |
| `pose_hip` | `idle_hip` | offen (nicht gesichtet) |
| `draw` | `draw` | offen (nicht gesichtet) |
| `ready` | `draw` | offen (nicht gesichtet) |
| `holster` | `holster` | offen (nicht gesichtet) |
| `pose_aim` | `aim_in` | offen (nicht gesichtet) |
| `tr_hip_aim` | `aim_in` | offen (nicht gesichtet) |
| `tr_aim_hip` | `aim_out` | offen (nicht gesichtet) |
| `fire_auto` | `fire_ads` | offen (nicht gesichtet) |
| `recoil_mech` | `fire_hip` | offen (nicht gesichtet) |
| `recoil_camera` | `fire_hip` | offen (nicht gesichtet) |
| `reload_partial` | `reload_tactical` | offen (nicht gesichtet) |
| `reload_feed` | `reload_tactical` | offen (nicht gesichtet) |
| `reload_empty` | `reload_empty` | offen (nicht gesichtet) |
| `cycle` | `reload_empty` | offen (nicht gesichtet) |
| `inspect` | `inspect` | offen (nicht gesichtet) |
| `inspect_return` | `inspect` | offen (nicht gesichtet) |
| `sprint_in` | `sprint` | offen (nicht gesichtet) |
| `sprint_loop` | `sprint` | offen (nicht gesichtet) |
| `sprint_out` | `sprint` | offen (nicht gesichtet) |
| `pose_lowered` | `lowered` | offen (nicht gesichtet) |
| `tr_lowered_return` | `lowered` | offen (nicht gesichtet) |
| `move_walk` | `walk` | offen (nicht gesichtet) |
| `sway` | `walk` | offen (nicht gesichtet) |
| `crouch` | `crouch` | offen (nicht gesichtet) |
| `jump_start` | `jump_land` | offen (nicht gesichtet) |
| `air` | `jump_land` | offen (nicht gesichtet) |
| `land` | `jump_land` | offen (nicht gesichtet) |
| `tr_sprint_aim` | `sprint_to_aim` | offen (nicht gesichtet) |
| `tr_sprint_fire` | `sprint_to_fire` | offen (nicht gesichtet) |
| `tr_draw_aimheld` | `draw_aim` | offen (nicht gesichtet) |
| `tr_reload_switch` | `reload_to_switch` | offen (nicht gesichtet) |
| `switch` | `reload_to_switch` | offen (nicht gesichtet) |

## BASIC-05-v2.1 – Seitenwaffe v2.1 (sidearm)

### Klassen- und Spielwerte

| Wert | Stand | Herkunft |
|---|---|---|
| Klasse | sidearm | Ego-Übertrag 0.33 „Armory“ P1: Hüfte und Anflug nach Motiongen (Seitenwaffe), Sprint wie die Handfeuerwaffe, Nachladen der Bezugsklasse mit Magazin im Griff und Schlitten |
| Kadenz | 360/min | E: keine Einzelfeuer-Messung; Mitte des Manifest-Bands 260–491/min, Magazin 12–30 (Motiongen waffenwerte:332-340) → 360/min, Magazin 15 (Entscheidungsliste); Feuerart aus der Spec (Einzelfeuer); Bahnstufe wie die Automatik, Kick 1,2 E (Welt bis 9,8 pp H nur netto beobachtet, rueckstoss:107) |
| Magazin | 15 | E: keine Einzelfeuer-Messung; Mitte des Manifest-Bands 260–491/min, Magazin 12–30 (Motiongen waffenwerte:332-340) → 360/min, Magazin 15 (Entscheidungsliste); Feuerart aus der Spec (Einzelfeuer); Bahnstufe wie die Automatik, Kick 1,2 E (Welt bis 9,8 pp H nur netto beobachtet, rueckstoss:107) |
| Feuerart | `semi_auto` – Einzelfeuer (ein Schuss je Zug) | Spec (META fire, data/specs); Unity: gameplay.fire_mode (0.20) |
| Weltzoom im Zielen | 1.25 | M Glidepath (Entscheidungsliste 1.2 A, basic/reticles.py › CLASS_ZOOM) |
| Hüft-Fadenkreuz | cross 4.5 % H | entworfen (4.1 A / 4.2 A, basic/reticles.py › HIP) |
| Sprint-Fadenkreuz | aus | basic/reticles.py › HIP.sprint (4.1 A) |
| Bahnstufe je Schuss | 1.00 % H | ego.RECOIL (gemeinsam, Automatik ≈ 1 % H je Schuss, 5.2 A) |
| Haltung `hip` | Socket_Hand [-0.11, -0.448, -0.179], Ziel [0.302, -3.401, 0.156], Rollen 6.0° | M cubeescape-reference huefte.json (Destiny 2, Mündung 57/64, 59/67, Visier 66/71, 66/73, Griffhand 67/87, 67/88); Lage E: Ausgleichsrechnung gegen diese Werte (0.33, Abgleich aller Waffen; Nutzer 31.10.2026 „Ja, nachziehen“ – bis dahin nur die Mündung eingestellt, die Griffhand lag 9–12 pp zu tief), gerechnet (Socket_Muzzle, Socket_Sight bzw. Socket_Reticle, Socket_Hand) Mündung 58,0/65,5 %, Visier 65,8/71,5 %, Griffhand 66,0/96,3 % (Mündung, Visier und Griff nicht zugleich: Griff 8 pp tiefer) |
| Haltung `sprint` | Socket_Hand [-0.1, -0.36, -0.15], Ziel [-0.02, -0.8, 1.6], Rollen 0° | E: Seitenwaffen-Sprint nicht gemessen (Motiongen destiny2:563) → Trageform der Handfeuerwaffe (senkrecht, hoch rechts, destiny2:562), gerechnet Mündung 70,2/31,0 % |
| Haltung `reload` | Socket_Hand [-0.07, -0.36, -0.14], Ziel [0.75, -2.1, 0.45], Rollen -40° | E wie die Bezugshaltung reload (T Reload roll −20/pitch 12, verstärkt), 2 cm weiter vorn (gestreckte Arme), gerechnet Mündung 55,1/56,4 % |
| Haltung `crouch` | Socket_Hand [-0.1, -0.438, -0.194], Rollen 9.0° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `air` | Socket_Hand [-0.11, -0.448, -0.164], Rollen 4.0° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `lowered` | Socket_Hand [-0.09, -0.408, -0.199], Rollen 10.0° | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| Dauer `aim_in` | 2.4 Bilder bei 30/s (0.080 s) | M Destiny-Seitenwaffe: ADS ein Rattler 6–7 Bilder bei 60/s, Brass Attacks 12 (Motiongen destiny2:585/269) → 2,4 Bilder bei 30/s (MP: 8–12 → 3), ADS aus: Zoom 7 Bilder → 2; Ziehen Minimum Distance 12 + 16 Bilder bei 60/s bis ruhig (wechsel:52) → 14; Nachladen 1,1–1,2 s (destiny2:491) × TIME_SCALE 1,25 → 43 Bilder, leer E +0,3 s Durchladen am Schlitten → 52 (Destiny: taktisch gegen leer nicht gemessen) |
| Dauer `aim_out` | 2 Bilder bei 30/s (0.067 s) | M Destiny-Seitenwaffe: ADS ein Rattler 6–7 Bilder bei 60/s, Brass Attacks 12 (Motiongen destiny2:585/269) → 2,4 Bilder bei 30/s (MP: 8–12 → 3), ADS aus: Zoom 7 Bilder → 2; Ziehen Minimum Distance 12 + 16 Bilder bei 60/s bis ruhig (wechsel:52) → 14; Nachladen 1,1–1,2 s (destiny2:491) × TIME_SCALE 1,25 → 43 Bilder, leer E +0,3 s Durchladen am Schlitten → 52 (Destiny: taktisch gegen leer nicht gemessen) |
| Dauer `draw` | 14 Bilder bei 30/s (0.467 s) | M Destiny-Seitenwaffe: ADS ein Rattler 6–7 Bilder bei 60/s, Brass Attacks 12 (Motiongen destiny2:585/269) → 2,4 Bilder bei 30/s (MP: 8–12 → 3), ADS aus: Zoom 7 Bilder → 2; Ziehen Minimum Distance 12 + 16 Bilder bei 60/s bis ruhig (wechsel:52) → 14; Nachladen 1,1–1,2 s (destiny2:491) × TIME_SCALE 1,25 → 43 Bilder, leer E +0,3 s Durchladen am Schlitten → 52 (Destiny: taktisch gegen leer nicht gemessen) |
| Dauer `reload_tactical` | 43 Bilder bei 30/s (1.433 s) | M Destiny-Seitenwaffe: ADS ein Rattler 6–7 Bilder bei 60/s, Brass Attacks 12 (Motiongen destiny2:585/269) → 2,4 Bilder bei 30/s (MP: 8–12 → 3), ADS aus: Zoom 7 Bilder → 2; Ziehen Minimum Distance 12 + 16 Bilder bei 60/s bis ruhig (wechsel:52) → 14; Nachladen 1,1–1,2 s (destiny2:491) × TIME_SCALE 1,25 → 43 Bilder, leer E +0,3 s Durchladen am Schlitten → 52 (Destiny: taktisch gegen leer nicht gemessen) |
| Dauer `reload_empty` | 52 Bilder bei 30/s (1.733 s) | M Destiny-Seitenwaffe: ADS ein Rattler 6–7 Bilder bei 60/s, Brass Attacks 12 (Motiongen destiny2:585/269) → 2,4 Bilder bei 30/s (MP: 8–12 → 3), ADS aus: Zoom 7 Bilder → 2; Ziehen Minimum Distance 12 + 16 Bilder bei 60/s bis ruhig (wechsel:52) → 14; Nachladen 1,1–1,2 s (destiny2:491) × TIME_SCALE 1,25 → 43 Bilder, leer E +0,3 s Durchladen am Schlitten → 52 (Destiny: taktisch gegen leer nicht gemessen) |
| Mündungsfeuer | 33 ms | M Destiny: 1–2 Bilder bei 60/s, Kern klein, Seitenflammen breiter, Zielen Automatik ≈ 20 % der Öffnung (Motiongen muendung › 6, Entscheidungsliste 5.3 A); Maße und Farben E (Stil v2.1) |
| Hülsen | pistol (20 × 9.2 mm) | E: Auswurffenster rechts im Schlitten, Hülse nach rechts, etwas hoch und vorn (wie BASIC-06); Bahn: M Destiny: Hülse im 1. Blitzbild oder 1 Bild danach, rechts/rechts unten (Motiongen muendung › 6, Entscheidungsliste 5d/5.4 A); Geschwindigkeit, Drehung, Lebensdauer E |
| Rückstoß | ego.RECOIL (gemeinsam) | übertragen von der Automatik: Säule 1 % H je Schuss, im Zielen wandert die Welt (5.1 A / 5.2 A); Werkzeug: Modellkick der Aktion (fire_a/fire_b kick 0,6), keine Bahnstufe (E; Portal 2: obere Klaue ≈ 7 % H im ersten Schussbild) |
| Wirkung | Kugel, Einschlag bullet | M keine Spur, kein Loch sichtbar (REF 0.36 › 7 Fußnote 1); Einschlag auf Wand nicht gemessen; Loch E (180) (ego.PAYLOAD, Entscheidungsliste Block 9) |
| Sprint-Frequenz | 3,16 / 1,58 Hz (gemeinsam) | M Destiny Automatik/Handfeuerwaffe, für alle Klassen bis zu neuen Messungen (3c) |
| Griffe | grip, support, mag, charge | Modul-Feld EGO_GRIPS |
| Live-Teile | trigger = trigger, bolt = slide, port =  | Modul-Feld EGO_LIVE |

### Haltungen

| Haltung | Socket_Hand (m) | Handgelenk max | Herkunft |
|---|---|---|---|
| `hip` | [-0.11, -0.448, -0.179] | nur in Aktionen geprüft | M cubeescape-reference huefte.json (Destiny 2, Mündung 57/64, 59/67, Visier 66/71, 66/73, Griffhand 67/87, 67/88); Lage E: Ausgleichsrechnung gegen diese Werte (0.33, Abgleich aller Waffen; Nutzer 31.10.2026 „Ja, nachziehen“ – bis dahin nur die Mündung eingestellt, die Griffhand lag 9–12 pp zu tief), gerechnet (Socket_Muzzle, Socket_Sight bzw. Socket_Reticle, Socket_Hand) Mündung 58,0/65,5 %, Visier 65,8/71,5 %, Griffhand 66,0/96,3 % (Mündung, Visier und Griff nicht zugleich: Griff 8 pp tiefer) |
| `ads` | [0.0, 0.0, 0.0] | nur in Aktionen geprüft | Visier-Standard v2: Socket_Eye ist der Augenpunkt, liegt in der Kamera; Waffenmodell ungezoomt, Welt zoomt je Klasse |
| `sprint` | [-0.1, -0.36, -0.15] | nur in Aktionen geprüft | E: Seitenwaffen-Sprint nicht gemessen (Motiongen destiny2:563) → Trageform der Handfeuerwaffe (senkrecht, hoch rechts, destiny2:562), gerechnet Mündung 70,2/31,0 % |
| `lowered` | [-0.09, -0.408, -0.199] | nur in Aktionen geprüft | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| `crouch` | [-0.1, -0.438, -0.194] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `air` | [-0.11, -0.448, -0.164] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `holstered` | [-0.24, -0.25, -0.62] | nur in Aktionen geprüft | E (unter dem Bild) |
| `reload` | [-0.07, -0.36, -0.14] | nur in Aktionen geprüft | E wie die Bezugshaltung reload (T Reload roll −20/pitch 12, verstärkt), 2 cm weiter vorn (gestreckte Arme), gerechnet Mündung 55,1/56,4 % |
| `inspect_l` | [-0.06, -0.36, -0.16] | nur in Aktionen geprüft | E (Ego-Seite zeigt zur Kamera) |
| `inspect_r` | [-0.1, -0.36, -0.12] | nur in Aktionen geprüft | E (Oberseite und rechte Seite) |

### Aktionen

| Aktion | Beschreibung | Bilder | Marker (Bild) | Handgelenk max | Clip | Sichtung | Herkunft |
|---|---|---|---|---|---|---|---|
| `idle_hip` | Ruhe an der Hüfte (Atmen) | 75 (2.50 s) | – | offen° | offen | offen | E |
| `draw` | Ziehen | 14 (0.47 s) | Ready (10) | offen° | offen | offen | M Ziehen 0,23 s bis Hüfte (Auto Rifle, Q-REF) + Ausfedern E; Klasse sidearm: 25 → 14 Bilder (M Destiny-Seitenwaffe: ADS ein Rattler 6–7 Bilder bei 60/s, Brass Attacks 12 (Motiongen destiny2:585/269) → 2,4 Bilder bei 30/s (MP: 8–12 → 3), ADS aus: Zoom 7 Bilder → 2; Ziehen Minimum Distance 12 + 16 Bilder bei 60/s bis ruhig (wechsel:52) → 14; Nachladen 1,1–1,2 s (destiny2:491) × TIME_SCALE 1,25 → 43 Bilder, leer E +0,3 s Durchladen am Schlitten → 52 (Destiny: taktisch gegen leer nicht gemessen)) |
| `holster` | Wegstecken | 8 (0.27 s) | HandOff (1), Holstered (8) | offen° | offen | offen | M Destiny-Wechsel: Wegstecken 0,08–0,27 s (Motiongen wechsel › 4, Entscheidungsliste 6.1 A) → 0,27 s ohne TIME_SCALE (bis 0.14: 0,60 s); Ablauf E (CE: Holster ab aktueller Stellung) |
| `aim_in` | Hüfte → Zielen | 3 (0.10 s) | Aimed (2) | offen° | offen | offen | E 0,30 s (CE-Handling Auto 0,39→0,20 s); Klasse sidearm: 10 → 2.4 Bilder (M Destiny-Seitenwaffe: ADS ein Rattler 6–7 Bilder bei 60/s, Brass Attacks 12 (Motiongen destiny2:585/269) → 2,4 Bilder bei 30/s (MP: 8–12 → 3), ADS aus: Zoom 7 Bilder → 2; Ziehen Minimum Distance 12 + 16 Bilder bei 60/s bis ruhig (wechsel:52) → 14; Nachladen 1,1–1,2 s (destiny2:491) × TIME_SCALE 1,25 → 43 Bilder, leer E +0,3 s Durchladen am Schlitten → 52 (Destiny: taktisch gegen leer nicht gemessen)) |
| `aim_out` | Zielen → Hüfte | 2 (0.07 s) | Ready (2) | offen° | offen | offen | E; Klasse sidearm: 8 → 2 Bilder (M Destiny-Seitenwaffe: ADS ein Rattler 6–7 Bilder bei 60/s, Brass Attacks 12 (Motiongen destiny2:585/269) → 2,4 Bilder bei 30/s (MP: 8–12 → 3), ADS aus: Zoom 7 Bilder → 2; Ziehen Minimum Distance 12 + 16 Bilder bei 60/s bis ruhig (wechsel:52) → 14; Nachladen 1,1–1,2 s (destiny2:491) × TIME_SCALE 1,25 → 43 Bilder, leer E +0,3 s Durchladen am Schlitten → 52 (Destiny: taktisch gegen leer nicht gemessen)) |
| `fire_hip` | Dauerfeuer aus der Hüfte | 32 (1.07 s) | Fire (2) | offen° | offen | offen | M 720/min = 1 Schuss je 2,5 Bilder (Q-REF; bis 0.14 alle 2 Bilder ≈ 940/min); Rückstoß T 17,5 mm/3°; Klasse sidearm: 360/min, Einzelfeuer (ein Schuss je Zug) (Schussbilder [2, 7, 12, 17, 22]) |
| `fire_ads` | Dauerfeuer im Zielen | 32 (1.07 s) | AimFire (2) | offen° | offen | offen | M Kadenz wie fire_hip; Rückstoß im Zielen nach RECOIL ads_* (5.1 A: Visier steht, die Welt wandert) E; Klasse sidearm: 360/min, Einzelfeuer (ein Schuss je Zug) (Schussbilder [2, 7, 12, 17, 22]) |
| `reload_tactical` | Nachladen mit Restmunition | 43 (1.43 s) | HandOff (3), MagOut (8), MagIn (25), HandOn (33), Ready (40) | offen° | offen | offen | M MagIn ≈ 0,93 s; Ablauf T (Reload-Keys) mit Destiny-Kippen E; v2: Ausholen, Stoß bei MagIn, Nachfedern E; Klasse sidearm: 63 → 43 Bilder (M Destiny-Seitenwaffe: ADS ein Rattler 6–7 Bilder bei 60/s, Brass Attacks 12 (Motiongen destiny2:585/269) → 2,4 Bilder bei 30/s (MP: 8–12 → 3), ADS aus: Zoom 7 Bilder → 2; Ziehen Minimum Distance 12 + 16 Bilder bei 60/s bis ruhig (wechsel:52) → 14; Nachladen 1,1–1,2 s (destiny2:491) × TIME_SCALE 1,25 → 43 Bilder, leer E +0,3 s Durchladen am Schlitten → 52 (Destiny: taktisch gegen leer nicht gemessen)) |
| `reload_empty` | Nachladen aus leerem Zustand | 52 (1.73 s) | HandOff (4), MagOut (7), MagIn (24), Chamber (35), HandOn (42), Ready (49) | offen° | offen | offen | M leer 1,85 s, MagOut 0,25 s, MagIn 0,93 s (Q-REF Auto Rifle); Ladehebel E; v2: Ausholen, Stoß bei MagIn, Ruck beim Durchladen, Nachfedern E; Klasse sidearm: 75 → 52 Bilder (M Destiny-Seitenwaffe: ADS ein Rattler 6–7 Bilder bei 60/s, Brass Attacks 12 (Motiongen destiny2:585/269) → 2,4 Bilder bei 30/s (MP: 8–12 → 3), ADS aus: Zoom 7 Bilder → 2; Ziehen Minimum Distance 12 + 16 Bilder bei 60/s bis ruhig (wechsel:52) → 14; Nachladen 1,1–1,2 s (destiny2:491) × TIME_SCALE 1,25 → 43 Bilder, leer E +0,3 s Durchladen am Schlitten → 52 (Destiny: taktisch gegen leer nicht gemessen)) |
| `inspect` | Betrachten | 120 (4.00 s) | Start (20), End (118) | offen° | offen | offen | E nach Apex/CoD-Muster (Ego-Seite, dann Oberseite); Destiny hat keinen Ego-Inspect |
| `sprint` | Sprint: Beginn, Schleife, Ende | 60 (2.00 s) | SprintLoop (10), Ready (60) | offen° | offen | offen | E (CE: Waffe senkt sich und rollt zur Mitte); period = Doppelschritt (seitlich), vertikal je Schritt: 19 Bilder = 0,633 s → 3,16 Schritte/s, seitlich 1,58 Hz, Rollen ±3,5°, U-Bogen (oben an den Seitenumkehren) nach Motiongen REF 0.23 (Destiny 2, Automatik/Handfeuerwaffe gemessen). 0.9: 10 Bilder = 6 Schritte/s („tapsig“). 0.15: Hub 12/10 → 22/18 mm (seitlich/vertikal) für ≈ 10 % H / 13 % B im Bild wie die Destiny-Automatik (Entscheidungsliste 3.1 A, gemessen wie in Schritt 2: Oberkante, linke Kante); Klasse sidearm: Hub (0.0068, 0.0234) (E wie die Handfeuerwaffe (Seitenwaffen-Sprint nicht gemessen, Motiongen destiny2:563)) |
| `lowered` | Gesenkte Haltung / Wandnähe | 45 (1.50 s) | Lowered (10), Ready (45) | offen° | offen | offen | E |
| `walk` | Gehen (liegende Acht) | 60 (2.00 s) | – | offen° | offen | offen | E (CE: liegende Acht) |
| `crouch` | Ducken | 30 (1.00 s) | Crouched (10) | offen° | offen | offen | E |
| `jump_land` | Sprung, Luftphase, Landung | 50 (1.67 s) | Air (10), Land (35) | offen° | offen | offen | E (CE: Anheben, Landefeder) |
| `sprint_to_aim` | Sprint → Zielen | 18 (0.60 s) | SprintOut (0), Aimed (12) | offen° | offen | offen | E (CE: ADS > Sprint) |
| `sprint_to_fire` | Sprint → Feuer | 26 (0.87 s) | SprintOut (0), Fire (7) | offen° | offen | offen | E (CE: Fire > Sprint); Klasse sidearm: 360/min, Einzelfeuer (ein Schuss je Zug) (Schussbilder [7, 12, 17]) |
| `draw_aim` | Ziehen bei gehaltenem Zielen | 35 (1.17 s) | Ready (18), Aimed (30) | offen° | offen | offen | E (CE: Draw nicht unterbrechbar, ADS danach) |
| `reload_to_switch` | Nachladen → Waffenwechsel (Abbruch) | 38 (1.27 s) | HandOff (5), Cancel (18), Holstered (35) | offen° | offen | offen | E (CE: Reload bricht bei Wechsel ab, Holster ab aktueller Stellung) |

### Abdeckung der Matrixzeilen

| Zeile | durch Aktion | Status |
|---|---|---|
| `pose_rest` | `idle_hip` | offen (nicht gesichtet) |
| `pose_hip` | `idle_hip` | offen (nicht gesichtet) |
| `draw` | `draw` | offen (nicht gesichtet) |
| `ready` | `draw` | offen (nicht gesichtet) |
| `holster` | `holster` | offen (nicht gesichtet) |
| `pose_aim` | `aim_in` | offen (nicht gesichtet) |
| `tr_hip_aim` | `aim_in` | offen (nicht gesichtet) |
| `tr_aim_hip` | `aim_out` | offen (nicht gesichtet) |
| `fire_auto` | `fire_ads` | offen (nicht gesichtet) |
| `recoil_mech` | `fire_hip` | offen (nicht gesichtet) |
| `recoil_camera` | `fire_hip` | offen (nicht gesichtet) |
| `reload_partial` | `reload_tactical` | offen (nicht gesichtet) |
| `reload_feed` | `reload_tactical` | offen (nicht gesichtet) |
| `reload_empty` | `reload_empty` | offen (nicht gesichtet) |
| `cycle` | `reload_empty` | offen (nicht gesichtet) |
| `inspect` | `inspect` | offen (nicht gesichtet) |
| `inspect_return` | `inspect` | offen (nicht gesichtet) |
| `sprint_in` | `sprint` | offen (nicht gesichtet) |
| `sprint_loop` | `sprint` | offen (nicht gesichtet) |
| `sprint_out` | `sprint` | offen (nicht gesichtet) |
| `pose_lowered` | `lowered` | offen (nicht gesichtet) |
| `tr_lowered_return` | `lowered` | offen (nicht gesichtet) |
| `move_walk` | `walk` | offen (nicht gesichtet) |
| `sway` | `walk` | offen (nicht gesichtet) |
| `crouch` | `crouch` | offen (nicht gesichtet) |
| `jump_start` | `jump_land` | offen (nicht gesichtet) |
| `air` | `jump_land` | offen (nicht gesichtet) |
| `land` | `jump_land` | offen (nicht gesichtet) |
| `tr_sprint_aim` | `sprint_to_aim` | offen (nicht gesichtet) |
| `tr_sprint_fire` | `sprint_to_fire` | offen (nicht gesichtet) |
| `tr_draw_aimheld` | `draw_aim` | offen (nicht gesichtet) |
| `tr_reload_switch` | `reload_to_switch` | offen (nicht gesichtet) |
| `switch` | `reload_to_switch` | offen (nicht gesichtet) |

## BASIC-09-v2.1 – Weitschuss v2.1 (sniper_rifle)

### Klassen- und Spielwerte

| Wert | Stand | Herkunft |
|---|---|---|
| Klasse | sniper_rifle | Ego-Übertrag 0.33 „Armory“ P2: Hüfte, Anflug und Nachladen nach Motiongen (Scharfschütze Far Future), Sprint der Automatik, Repetieren nach jedem Schuss E |
| Kadenz | 90/min | S Far Future 90/min, Magazin 4 (Menü, Motiongen destiny2:260; A Single Clap 90/min, 5); Feuerart aus der Spec (Repetierer: ein Schuss je Zug, danach fire_cycle); Bahnstufe 0,12 M: im Zielfernrohr steigt die Welt ≈ 18 pp H in 4 Bildern bei 60/s und bleibt ≈ 12 pp H versetzt (Motiongen zielbewegung:73) → Erholung E langsam (ab 0,25 s, 1,5 Hz); Kick 3,0 E (schwerer Einzelschuss) |
| Magazin | 4 | S Far Future 90/min, Magazin 4 (Menü, Motiongen destiny2:260; A Single Clap 90/min, 5); Feuerart aus der Spec (Repetierer: ein Schuss je Zug, danach fire_cycle); Bahnstufe 0,12 M: im Zielfernrohr steigt die Welt ≈ 18 pp H in 4 Bildern bei 60/s und bleibt ≈ 12 pp H versetzt (Motiongen zielbewegung:73) → Erholung E langsam (ab 0,25 s, 1,5 Hz); Kick 3,0 E (schwerer Einzelschuss) |
| Feuerart | `bolt_action` – Repetierer (ein Schuss je Zug, danach Kammerstängel als Klassenaktion fire_cycle/fire_cycle_ads) | Spec (META fire, data/specs); Unity: gameplay.fire_mode (0.20) |
| Weltzoom im Zielen | 4 | M Glidepath (Entscheidungsliste 1.2 A, basic/reticles.py › CLASS_ZOOM) |
| Hüft-Fadenkreuz | caret 1.0 % H | gemessen (Glidepath, ≈ 1 % H) (4.1 A / 4.2 A, basic/reticles.py › HIP) |
| Sprint-Fadenkreuz | aus | basic/reticles.py › HIP.sprint (4.1 A) |
| Bahnstufe je Schuss | 12.00 % H | S Far Future 90/min, Magazin 4 (Menü, Motiongen destiny2:260; A Single Clap 90/min, 5); Feuerart aus der Spec (Repetierer: ein Schuss je Zug, danach fire_cycle); Bahnstufe 0,12 M: im Zielfernrohr steigt die Welt ≈ 18 pp H in 4 Bildern bei 60/s und bleibt ≈ 12 pp H versetzt (Motiongen zielbewegung:73) → Erholung E langsam (ab 0,25 s, 1,5 Hz); Kick 3,0 E (schwerer Einzelschuss) |
| Haltung `hip` | Socket_Hand [-0.19, -0.42, -0.23], Ziel [0.02, -3.0, -0.32], Rollen 6° | M Destiny-Scharfschütze Hüfte: Mündung 56/68 (Motiongen huefte:51), 56/66 (huefte:61), Far Future 56/64 (destiny2:496); Lage E wie die Automatik, Lauf 1,8° tiefer (langer Lauf: Automatik-Hüfte trifft 56,1/61,9), gerechnet Mündung 56,1/65,7 % |
| Haltung `sprint` | Socket_Hand [-0.2, -0.38, -0.21], Ziel [0.5, -2.4, -0.6], Rollen -25° | O cubeescape-reference destiny2 › Glidepath (Sprint): Scharfschütze „tief unten rechts“ (Sichtung, kein Wippen ≥ 3 pp); eine ältere Zeile (destiny2:483) nennt bei 60/s eine höhere, mittigere Form – widersprüchlich, hier die Glidepath-Sichtung. Lage E wie die Fusion (Trageform tief rechts), gerechnet Mündung 48/77 %, Visier rechts am Rand; bis 0.33 die Automatik-Form (Mündung 19/86 %) |
| Haltung `crouch` | Socket_Hand [-0.18, -0.41, -0.245], Rollen 9° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `air` | Socket_Hand [-0.19, -0.42, -0.215], Rollen 4° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `lowered` | Socket_Hand [-0.17, -0.38, -0.25], Rollen 10° | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| Dauer `aim_in` | 13 Bilder bei 30/s (0.433 s) | M Destiny-Scharfschütze Far Future ADS ein 14 Bilder bei 60/s bis stabil (6 Hochziehen + 10 Overlay, Motiongen destiny2:496) → 6 Bilder bei 30/s (Umrechnung mit dem Zielen-Nachlauf wie MP 8–12 → 3, Scout 17 → 7, Automatik 20 → 10); ADS aus 0,17–0,25 s → 6 Bilder (0,20 s) – bis 0.33.1; Nutzerentscheid 31.10.2026: Gapfill Defiance of Yasmin / Cloudstrike ein 25 / 27, aus 21 / 26–28 Bilder bei 60/s bis Ruhe → aim_in 13, aim_out 12 (über Automatik 20 → 10 hinaus linear, 22 → 11); Ziehen erstes Modellbild → ruhig Defiance of Yasmin 41, Cloudstrike 47–53 Bilder bei 60/s (Motiongen destiny2 › Gapfill, z-g34-kingsfall/-cloudstrike) ≈ 46 → 23 Bilder bei 30/s (wie MG 55 → 28) |
| Dauer `aim_out` | 12 Bilder bei 30/s (0.400 s) | M Destiny-Scharfschütze Far Future ADS ein 14 Bilder bei 60/s bis stabil (6 Hochziehen + 10 Overlay, Motiongen destiny2:496) → 6 Bilder bei 30/s (Umrechnung mit dem Zielen-Nachlauf wie MP 8–12 → 3, Scout 17 → 7, Automatik 20 → 10); ADS aus 0,17–0,25 s → 6 Bilder (0,20 s) – bis 0.33.1; Nutzerentscheid 31.10.2026: Gapfill Defiance of Yasmin / Cloudstrike ein 25 / 27, aus 21 / 26–28 Bilder bei 60/s bis Ruhe → aim_in 13, aim_out 12 (über Automatik 20 → 10 hinaus linear, 22 → 11); Ziehen erstes Modellbild → ruhig Defiance of Yasmin 41, Cloudstrike 47–53 Bilder bei 60/s (Motiongen destiny2 › Gapfill, z-g34-kingsfall/-cloudstrike) ≈ 46 → 23 Bilder bei 30/s (wie MG 55 → 28) |
| Dauer `draw` | 23 Bilder bei 30/s (0.767 s) | M Destiny-Scharfschütze Far Future ADS ein 14 Bilder bei 60/s bis stabil (6 Hochziehen + 10 Overlay, Motiongen destiny2:496) → 6 Bilder bei 30/s (Umrechnung mit dem Zielen-Nachlauf wie MP 8–12 → 3, Scout 17 → 7, Automatik 20 → 10); ADS aus 0,17–0,25 s → 6 Bilder (0,20 s) – bis 0.33.1; Nutzerentscheid 31.10.2026: Gapfill Defiance of Yasmin / Cloudstrike ein 25 / 27, aus 21 / 26–28 Bilder bei 60/s bis Ruhe → aim_in 13, aim_out 12 (über Automatik 20 → 10 hinaus linear, 22 → 11); Ziehen erstes Modellbild → ruhig Defiance of Yasmin 41, Cloudstrike 47–53 Bilder bei 60/s (Motiongen destiny2 › Gapfill, z-g34-kingsfall/-cloudstrike) ≈ 46 → 23 Bilder bei 30/s (wie MG 55 → 28) |
| Zielfernrohr im Zielen | aus: scope_strap, scope_tube, scope_eyepiece, scope_eye_trim, scope_ocular_glass, scope_turret, scope_turret_w (Socket_Eye < 60 mm) | E: Okular bis an die Nahebene sichtbar (Augenabstand Okularende 30 mm + near 30 mm), danach Linsenbild; Destiny-Scharfschütze: Okular füllt das Bild 4 Bilder, Linse nach dem Modell (Motiongen destiny2 › 2, Entscheidungsliste 1d) |
| Mündungsfeuer | 33 ms | M Destiny: 1–2 Bilder bei 60/s, Kern klein, Seitenflammen breiter, Zielen Automatik ≈ 20 % der Öffnung (Motiongen muendung › 6, Entscheidungsliste 5.3 A); Maße und Farben E (Stil v2.1) |
| Hülsen | rifle (42 × 9.6 mm) | E: Auswurffenster rechts beim Zurückziehen des Verschlusses (Stängel links), Hülse nach rechts, etwas hoch und vorn (wie Destiny, Motiongen muendung › 6); Bahn: M Destiny: Hülse im 1. Blitzbild oder 1 Bild danach, rechts/rechts unten (Motiongen muendung › 6, Entscheidungsliste 5d/5.4 A); Geschwindigkeit, Drehung, Lebensdauer E |
| Rückstoß | ego.RECOIL (gemeinsam) | übertragen von der Automatik: Säule 1 % H je Schuss, im Zielen wandert die Welt (5.1 A / 5.2 A); Werkzeug: Modellkick der Aktion (fire_a/fire_b kick 0,6), keine Bahnstufe (E; Portal 2: obere Klaue ≈ 7 % H im ersten Schussbild) |
| Wirkung | Kugel, Einschlag heavy | M keine Spur, Funken 0,1 s, Säule ≈ 0,38 s (REF 0.36 z-im-far-future); Loch E (180) (ego.PAYLOAD, Entscheidungsliste Block 9) |
| Sprint-Frequenz | 3,16 / 1,58 Hz (gemeinsam) | M Destiny Automatik/Handfeuerwaffe, für alle Klassen bis zu neuen Messungen (3c) |
| Griffe | grip, support, mag, charge | Modul-Feld EGO_GRIPS |
| Live-Teile | trigger = trigger, bolt = , port =  | Modul-Feld EGO_LIVE |

### Haltungen

| Haltung | Socket_Hand (m) | Handgelenk max | Herkunft |
|---|---|---|---|
| `hip` | [-0.19, -0.42, -0.23] | nur in Aktionen geprüft | M Destiny-Scharfschütze Hüfte: Mündung 56/68 (Motiongen huefte:51), 56/66 (huefte:61), Far Future 56/64 (destiny2:496); Lage E wie die Automatik, Lauf 1,8° tiefer (langer Lauf: Automatik-Hüfte trifft 56,1/61,9), gerechnet Mündung 56,1/65,7 % |
| `ads` | [0.0, 0.0, 0.0] | nur in Aktionen geprüft | Visier-Standard v2: Socket_Eye ist der Augenpunkt, liegt in der Kamera; Waffenmodell ungezoomt, Welt zoomt je Klasse |
| `sprint` | [-0.2, -0.38, -0.21] | nur in Aktionen geprüft | O cubeescape-reference destiny2 › Glidepath (Sprint): Scharfschütze „tief unten rechts“ (Sichtung, kein Wippen ≥ 3 pp); eine ältere Zeile (destiny2:483) nennt bei 60/s eine höhere, mittigere Form – widersprüchlich, hier die Glidepath-Sichtung. Lage E wie die Fusion (Trageform tief rechts), gerechnet Mündung 48/77 %, Visier rechts am Rand; bis 0.33 die Automatik-Form (Mündung 19/86 %) |
| `lowered` | [-0.17, -0.38, -0.25] | nur in Aktionen geprüft | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| `crouch` | [-0.18, -0.41, -0.245] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `air` | [-0.19, -0.42, -0.215] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `holstered` | [-0.24, -0.25, -0.62] | nur in Aktionen geprüft | E (unter dem Bild) |
| `reload` | [-0.07, -0.34, -0.135] | nur in Aktionen geprüft | T Reload roll −20/pitch 12, für Destiny-Anmutung verstärkt (E) |
| `inspect_l` | [-0.06, -0.36, -0.16] | nur in Aktionen geprüft | E (Ego-Seite zeigt zur Kamera) |
| `inspect_r` | [-0.1, -0.36, -0.12] | nur in Aktionen geprüft | E (Oberseite und rechte Seite) |

### Aktionen

| Aktion | Beschreibung | Bilder | Marker (Bild) | Handgelenk max | Clip | Sichtung | Herkunft |
|---|---|---|---|---|---|---|---|
| `idle_hip` | Ruhe an der Hüfte (Atmen) | 75 (2.50 s) | – | offen° | offen | offen | E |
| `draw` | Ziehen | 23 (0.77 s) | Ready (17) | offen° | offen | offen | M Ziehen 0,23 s bis Hüfte (Auto Rifle, Q-REF) + Ausfedern E; Klasse sniper_rifle: 25 → 23 Bilder (M Destiny-Scharfschütze Far Future ADS ein 14 Bilder bei 60/s bis stabil (6 Hochziehen + 10 Overlay, Motiongen destiny2:496) → 6 Bilder bei 30/s (Umrechnung mit dem Zielen-Nachlauf wie MP 8–12 → 3, Scout 17 → 7, Automatik 20 → 10); ADS aus 0,17–0,25 s → 6 Bilder (0,20 s) – bis 0.33.1; Nutzerentscheid 31.10.2026: Gapfill Defiance of Yasmin / Cloudstrike ein 25 / 27, aus 21 / 26–28 Bilder bei 60/s bis Ruhe → aim_in 13, aim_out 12 (über Automatik 20 → 10 hinaus linear, 22 → 11); Ziehen erstes Modellbild → ruhig Defiance of Yasmin 41, Cloudstrike 47–53 Bilder bei 60/s (Motiongen destiny2 › Gapfill, z-g34-kingsfall/-cloudstrike) ≈ 46 → 23 Bilder bei 30/s (wie MG 55 → 28)) |
| `holster` | Wegstecken | 8 (0.27 s) | HandOff (1), Holstered (8) | offen° | offen | offen | M Destiny-Wechsel: Wegstecken 0,08–0,27 s (Motiongen wechsel › 4, Entscheidungsliste 6.1 A) → 0,27 s ohne TIME_SCALE (bis 0.14: 0,60 s); Ablauf E (CE: Holster ab aktueller Stellung) |
| `aim_in` | Hüfte → Zielen | 13 (0.43 s) | Aimed (12) | 28.0° | ego_BASIC-09-v2.1_aim_in.mp4 | offen | E 0,30 s (CE-Handling Auto 0,39→0,20 s); Klasse sniper_rifle: 10 → 13 Bilder (M Destiny-Scharfschütze Far Future ADS ein 14 Bilder bei 60/s bis stabil (6 Hochziehen + 10 Overlay, Motiongen destiny2:496) → 6 Bilder bei 30/s (Umrechnung mit dem Zielen-Nachlauf wie MP 8–12 → 3, Scout 17 → 7, Automatik 20 → 10); ADS aus 0,17–0,25 s → 6 Bilder (0,20 s) – bis 0.33.1; Nutzerentscheid 31.10.2026: Gapfill Defiance of Yasmin / Cloudstrike ein 25 / 27, aus 21 / 26–28 Bilder bei 60/s bis Ruhe → aim_in 13, aim_out 12 (über Automatik 20 → 10 hinaus linear, 22 → 11); Ziehen erstes Modellbild → ruhig Defiance of Yasmin 41, Cloudstrike 47–53 Bilder bei 60/s (Motiongen destiny2 › Gapfill, z-g34-kingsfall/-cloudstrike) ≈ 46 → 23 Bilder bei 30/s (wie MG 55 → 28)) |
| `aim_out` | Zielen → Hüfte | 12 (0.40 s) | Ready (12) | 28.0° | ego_BASIC-09-v2.1_aim_out.mp4 | offen | E; Klasse sniper_rifle: 8 → 12 Bilder (M Destiny-Scharfschütze Far Future ADS ein 14 Bilder bei 60/s bis stabil (6 Hochziehen + 10 Overlay, Motiongen destiny2:496) → 6 Bilder bei 30/s (Umrechnung mit dem Zielen-Nachlauf wie MP 8–12 → 3, Scout 17 → 7, Automatik 20 → 10); ADS aus 0,17–0,25 s → 6 Bilder (0,20 s) – bis 0.33.1; Nutzerentscheid 31.10.2026: Gapfill Defiance of Yasmin / Cloudstrike ein 25 / 27, aus 21 / 26–28 Bilder bei 60/s bis Ruhe → aim_in 13, aim_out 12 (über Automatik 20 → 10 hinaus linear, 22 → 11); Ziehen erstes Modellbild → ruhig Defiance of Yasmin 41, Cloudstrike 47–53 Bilder bei 60/s (Motiongen destiny2 › Gapfill, z-g34-kingsfall/-cloudstrike) ≈ 46 → 23 Bilder bei 30/s (wie MG 55 → 28)) |
| `fire_hip` | Dauerfeuer aus der Hüfte | 32 (1.07 s) | Fire (2) | offen° | offen | offen | M 720/min = 1 Schuss je 2,5 Bilder (Q-REF; bis 0.14 alle 2 Bilder ≈ 940/min); Rückstoß T 17,5 mm/3°; Klasse sniper_rifle: 90/min, Repetierer (ein Schuss je Zug, danach Kammerstängel als Klassenaktion fire_cycle/fire_cycle_ads) (Schussbilder [2, 22]) |
| `fire_ads` | Dauerfeuer im Zielen | 32 (1.07 s) | AimFire (2) | offen° | offen | offen | M Kadenz wie fire_hip; Rückstoß im Zielen nach RECOIL ads_* (5.1 A: Visier steht, die Welt wandert) E; Klasse sniper_rifle: 90/min, Repetierer (ein Schuss je Zug, danach Kammerstängel als Klassenaktion fire_cycle/fire_cycle_ads) (Schussbilder [2, 22]) |
| `reload_tactical` | Nachladen (Kastenmagazin tauschen, am Ende repetieren) | 82 (2.73 s) | HandOff (4), MagOut (10), MagIn (26), Eject (44), Chamber (48), HandOn (60), Ready (78) | offen° | ego_BASIC-09-v2.1_reload_tactical.mp4 | offen | M Destiny-Scharfschütze Far Future: MagOut +0,28, MagIn +0,70, Kammerstängel +1,2, Hüfte 2,07, ruhig 2,18 s (Motiongen nachladen:58) → Marker bei 8/21/36/62 von 65 Bildern, × TIME_SCALE; Ablauf E wie das Nachladen der Automatik, Repetieren am Kammerknopf links (Nutzer 28.10.2026) aus der Hüfte wie fire_cycle (aus der Nachladehaltung lag der Oberarm groß vor der Kamera); taktisch gegen leer nicht gemessen (Entscheidungsliste) |
| `reload_empty` | Nachladen (Kastenmagazin tauschen, am Ende repetieren), auch leer | 82 (2.73 s) | HandOff (4), MagOut (10), MagIn (26), Eject (44), Chamber (48), HandOn (60), Ready (78) | offen° | offen | offen | M Destiny-Scharfschütze Far Future: MagOut +0,28, MagIn +0,70, Kammerstängel +1,2, Hüfte 2,07, ruhig 2,18 s (Motiongen nachladen:58) → Marker bei 8/21/36/62 von 65 Bildern, × TIME_SCALE; Ablauf E wie das Nachladen der Automatik, Repetieren am Kammerknopf links (Nutzer 28.10.2026) aus der Hüfte wie fire_cycle (aus der Nachladehaltung lag der Oberarm groß vor der Kamera); taktisch gegen leer nicht gemessen (Entscheidungsliste) |
| `inspect` | Betrachten | 120 (4.00 s) | Start (20), End (118) | offen° | offen | offen | E nach Apex/CoD-Muster (Ego-Seite, dann Oberseite); Destiny hat keinen Ego-Inspect |
| `sprint` | Sprint: Beginn, Schleife, Ende | 60 (2.00 s) | SprintLoop (10), Ready (60) | offen° | offen | offen | E (CE: Waffe senkt sich und rollt zur Mitte); period = Doppelschritt (seitlich), vertikal je Schritt: 19 Bilder = 0,633 s → 3,16 Schritte/s, seitlich 1,58 Hz, Rollen ±3,5°, U-Bogen (oben an den Seitenumkehren) nach Motiongen REF 0.23 (Destiny 2, Automatik/Handfeuerwaffe gemessen). 0.9: 10 Bilder = 6 Schritte/s („tapsig“). 0.15: Hub 12/10 → 22/18 mm (seitlich/vertikal) für ≈ 10 % H / 13 % B im Bild wie die Destiny-Automatik (Entscheidungsliste 3.1 A, gemessen wie in Schritt 2: Oberkante, linke Kante) |
| `lowered` | Gesenkte Haltung / Wandnähe | 45 (1.50 s) | Lowered (10), Ready (45) | offen° | offen | offen | E |
| `walk` | Gehen (liegende Acht) | 60 (2.00 s) | – | offen° | offen | offen | E (CE: liegende Acht) |
| `crouch` | Ducken | 30 (1.00 s) | Crouched (10) | offen° | offen | offen | E |
| `jump_land` | Sprung, Luftphase, Landung | 50 (1.67 s) | Air (10), Land (35) | offen° | offen | offen | E (CE: Anheben, Landefeder) |
| `sprint_to_aim` | Sprint → Zielen | 18 (0.60 s) | SprintOut (0), Aimed (12) | offen° | offen | offen | E (CE: ADS > Sprint) |
| `sprint_to_fire` | Sprint → Feuer | 26 (0.87 s) | SprintOut (0), Fire (7) | offen° | offen | offen | E (CE: Fire > Sprint); Klasse sniper_rifle: 90/min, Repetierer (ein Schuss je Zug, danach Kammerstängel als Klassenaktion fire_cycle/fire_cycle_ads) (Schussbilder [7]) |
| `draw_aim` | Ziehen bei gehaltenem Zielen | 35 (1.17 s) | Ready (18), Aimed (30) | offen° | offen | offen | E (CE: Draw nicht unterbrechbar, ADS danach) |
| `reload_to_switch` | Nachladen → Waffenwechsel (Abbruch) | 38 (1.27 s) | HandOff (5), Cancel (18), Holstered (35) | offen° | offen | offen | E (CE: Reload bricht bei Wechsel ab, Holster ab aktueller Stellung) |
| `fire_cycle` | Repetieren nach dem Schuss aus der Hüfte (Kammerstängel links: heben, zurück, vor, senken) | 18 (0.60 s) | HandOff (2), Eject (10), Chamber (12), HandOn (17) | offen° | ego_BASIC-09-v2.1_fire_cycle.mp4 | offen | E: Repetieren in 0,6 s nach dem Schuss (Kadenz 90/min = 0,67 s je Schuss, Far Future [S]); Stängel links, die Stützhand repetiert (Nutzer 28.10.2026), Hülse beim Zurückziehen (Marker Eject); Destiny zeigt beim Scharfschützen kein eigenes Repetieren (Entscheidungsliste) |
| `fire_cycle_ads` | Repetieren nach dem Schuss im Zielen (Waffe bleibt im Anschlag) | 18 (0.60 s) | HandOff (2), Eject (10), Chamber (12), HandOn (17) | offen° | ego_BASIC-09-v2.1_fire_cycle_ads.mp4 | offen | E wie fire_cycle, im Zielen ohne Kippen (Zielfernrohr bleibt vor dem Auge) |

### Abdeckung der Matrixzeilen

| Zeile | durch Aktion | Status |
|---|---|---|
| `pose_rest` | `idle_hip` | offen (nicht gesichtet) |
| `pose_hip` | `idle_hip` | offen (nicht gesichtet) |
| `draw` | `draw` | offen (nicht gesichtet) |
| `ready` | `draw` | offen (nicht gesichtet) |
| `holster` | `holster` | offen (nicht gesichtet) |
| `pose_aim` | `aim_in` | offen (nicht gesichtet) |
| `tr_hip_aim` | `aim_in` | offen (nicht gesichtet) |
| `tr_aim_hip` | `aim_out` | offen (nicht gesichtet) |
| `fire_auto` | `fire_ads` | offen (nicht gesichtet) |
| `recoil_mech` | `fire_hip` | offen (nicht gesichtet) |
| `recoil_camera` | `fire_hip` | offen (nicht gesichtet) |
| `reload_partial` | `reload_tactical` | offen (nicht gesichtet) |
| `reload_feed` | `reload_tactical` | offen (nicht gesichtet) |
| `reload_empty` | `reload_empty` | offen (nicht gesichtet) |
| `cycle` | `reload_empty` | offen (nicht gesichtet) |
| `inspect` | `inspect` | offen (nicht gesichtet) |
| `inspect_return` | `inspect` | offen (nicht gesichtet) |
| `sprint_in` | `sprint` | offen (nicht gesichtet) |
| `sprint_loop` | `sprint` | offen (nicht gesichtet) |
| `sprint_out` | `sprint` | offen (nicht gesichtet) |
| `pose_lowered` | `lowered` | offen (nicht gesichtet) |
| `tr_lowered_return` | `lowered` | offen (nicht gesichtet) |
| `move_walk` | `walk` | offen (nicht gesichtet) |
| `sway` | `walk` | offen (nicht gesichtet) |
| `crouch` | `crouch` | offen (nicht gesichtet) |
| `jump_start` | `jump_land` | offen (nicht gesichtet) |
| `air` | `jump_land` | offen (nicht gesichtet) |
| `land` | `jump_land` | offen (nicht gesichtet) |
| `tr_sprint_aim` | `sprint_to_aim` | offen (nicht gesichtet) |
| `tr_sprint_fire` | `sprint_to_fire` | offen (nicht gesichtet) |
| `tr_draw_aimheld` | `draw_aim` | offen (nicht gesichtet) |
| `tr_reload_switch` | `reload_to_switch` | offen (nicht gesichtet) |
| `switch` | `reload_to_switch` | offen (nicht gesichtet) |

## BASIC-12-v2.1 – Leitstrahl v2.1 (trace_rifle)

### Klassen- und Spielwerte

| Wert | Stand | Herkunft |
|---|---|---|
| Klasse | trace_rifle | Ego-Übertrag 0.33 „Armory“ P2: Hüfte und Anflug nach Motiongen (Spurgewehr), Sprint der Automatik, Nachladen der Bezugsklasse mit der Energiezelle (leer wie taktisch, kein Ladehebel) |
| Kadenz | 1000/min | S Retraced Path 1000/min, 94 (Manifest, Motiongen waffenwerte:363); Feuerart aus der Spec (Dauerstrahl); kein Rückstoß M (destiny2:500/512): Bahnstufe und Kick 0; kein Mündungsfeuer E (Strahl statt Blitz), keine Hülse (Energiezelle, EJECT None) |
| Magazin | 94 | S Retraced Path 1000/min, 94 (Manifest, Motiongen waffenwerte:363); Feuerart aus der Spec (Dauerstrahl); kein Rückstoß M (destiny2:500/512): Bahnstufe und Kick 0; kein Mündungsfeuer E (Strahl statt Blitz), keine Hülse (Energiezelle, EJECT None) |
| Feuerart | `continuous_beam` – Dauerstrahl (Dauerfeuer ohne Mündungsfeuer, Leuchtteile EGO_LIVE glow an, solange der Abzug zieht) | Spec (META fire, data/specs); Unity: gameplay.fire_mode (0.20) |
| Weltzoom im Zielen | 1.8 | M Glidepath (Entscheidungsliste 1.2 A, basic/reticles.py › CLASS_ZOOM) |
| Hüft-Fadenkreuz | circle_cross 4.5 % H | entworfen (4.1 A / 4.2 A, basic/reticles.py › HIP) |
| Sprint-Fadenkreuz | aus | basic/reticles.py › HIP.sprint (4.1 A) |
| Bahnstufe je Schuss | 0.00 % H | S Retraced Path 1000/min, 94 (Manifest, Motiongen waffenwerte:363); Feuerart aus der Spec (Dauerstrahl); kein Rückstoß M (destiny2:500/512): Bahnstufe und Kick 0; kein Mündungsfeuer E (Strahl statt Blitz), keine Hülse (Energiezelle, EJECT None) |
| Haltung `hip` | Socket_Hand [-0.136, -0.417, -0.156], Ziel [-0.075, -3.412, -0.315], Rollen 10.9° | M cubeescape-reference huefte.json (Destiny 2, Hollow Denial: Mündung 57,7/59,6, Visieröffnung 66,9/45,6); Lage E: Ausgleichsrechnung gegen diese Werte (0.33, Abgleich aller Waffen; Nutzer 31.10.2026 „Ja, nachziehen“ – bis dahin nur die Mündung eingestellt, das Visier lag 10–19 pp zu tief), gerechnet (Socket_Muzzle, Socket_Sight bzw. Socket_Reticle, Socket_Hand) Mündung 57,7/61,1 %, Visier 66,6/49,0 % – 12 mm tiefer als die Ausgleichslage: die Gehäusenase lag bei 53,4 % H in den Zonenspalten der Freihaltezone (A4, Ecke ab 55 %) |
| Haltung `sprint` | Socket_Hand [-0.1, -0.34, -0.23], Ziel [1.2, -1.6, -0.55], Rollen -35° | E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-Spurgewehr-Sprint nicht gemessen (Motiongen destiny2:570) (Haltung POSES['sprint'] unverändert) |
| Haltung `crouch` | Socket_Hand [-0.126, -0.407, -0.171], Rollen 13.899999999999999° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `air` | Socket_Hand [-0.136, -0.417, -0.141], Rollen 8.9° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `lowered` | Socket_Hand [-0.116, -0.377, -0.176], Rollen 14.899999999999999° | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| Dauer `aim_in` | 4 Bilder bei 30/s (0.133 s) | M Destiny-Spurgewehr Prometheus Lens ADS ein ≈ 12 Bilder bei 60/s (Motiongen destiny2:592) → 4 Bilder bei 30/s (Umrechnung wie Scharfschütze); Ager's Scepter ADS ein 13, aus 14 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen destiny2 › Gapfill, z-g34-agers) → aus 6 (Umrechnung wie Scharfschütze 14 → 6); Ziehen erstes Modellbild → ruhig 34 Bilder → 17; Nachladen ≈ 1,6 s bis Hüfte, „kein Klassenwert“ (destiny2:512) × TIME_SCALE = 60 Bilder bis Hüfte → Bezugsablauf (Hüfte bei 45/50) auf 67 Bilder gestreckt |
| Dauer `aim_out` | 6 Bilder bei 30/s (0.200 s) | M Destiny-Spurgewehr Prometheus Lens ADS ein ≈ 12 Bilder bei 60/s (Motiongen destiny2:592) → 4 Bilder bei 30/s (Umrechnung wie Scharfschütze); Ager's Scepter ADS ein 13, aus 14 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen destiny2 › Gapfill, z-g34-agers) → aus 6 (Umrechnung wie Scharfschütze 14 → 6); Ziehen erstes Modellbild → ruhig 34 Bilder → 17; Nachladen ≈ 1,6 s bis Hüfte, „kein Klassenwert“ (destiny2:512) × TIME_SCALE = 60 Bilder bis Hüfte → Bezugsablauf (Hüfte bei 45/50) auf 67 Bilder gestreckt |
| Dauer `draw` | 17 Bilder bei 30/s (0.567 s) | M Destiny-Spurgewehr Prometheus Lens ADS ein ≈ 12 Bilder bei 60/s (Motiongen destiny2:592) → 4 Bilder bei 30/s (Umrechnung wie Scharfschütze); Ager's Scepter ADS ein 13, aus 14 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen destiny2 › Gapfill, z-g34-agers) → aus 6 (Umrechnung wie Scharfschütze 14 → 6); Ziehen erstes Modellbild → ruhig 34 Bilder → 17; Nachladen ≈ 1,6 s bis Hüfte, „kein Klassenwert“ (destiny2:512) × TIME_SCALE = 60 Bilder bis Hüfte → Bezugsablauf (Hüfte bei 45/50) auf 67 Bilder gestreckt |
| Dauer `reload_tactical` | 67 Bilder bei 30/s (2.233 s) | M Destiny-Spurgewehr Prometheus Lens ADS ein ≈ 12 Bilder bei 60/s (Motiongen destiny2:592) → 4 Bilder bei 30/s (Umrechnung wie Scharfschütze); Ager's Scepter ADS ein 13, aus 14 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen destiny2 › Gapfill, z-g34-agers) → aus 6 (Umrechnung wie Scharfschütze 14 → 6); Ziehen erstes Modellbild → ruhig 34 Bilder → 17; Nachladen ≈ 1,6 s bis Hüfte, „kein Klassenwert“ (destiny2:512) × TIME_SCALE = 60 Bilder bis Hüfte → Bezugsablauf (Hüfte bei 45/50) auf 67 Bilder gestreckt |
| Mündungsfeuer | keins (Werkzeug) | S Retraced Path 1000/min, 94 (Manifest, Motiongen waffenwerte:363); Feuerart aus der Spec (Dauerstrahl); kein Rückstoß M (destiny2:500/512): Bahnstufe und Kick 0; kein Mündungsfeuer E (Strahl statt Blitz), keine Hülse (Energiezelle, EJECT None) |
| Hülsen | keine | Waffe ohne Feld EJECT |
| Rückstoß | ego.RECOIL (gemeinsam) | übertragen von der Automatik: Säule 1 % H je Schuss, im Zielen wandert die Welt (5.1 A / 5.2 A); Werkzeug: Modellkick der Aktion (fire_a/fire_b kick 0,6), keine Bahnstufe (E; Portal 2: obere Klaue ≈ 7 % H im ersten Schussbild) |
| Wirkung | Dauerstrahl 4.5 cm | M Kern #D0D8FF, Rand #5060E0, Kontaktpunkt pulsiert 12/s (REF 0.36 z-im-agers); E: durchgehender Strahl 4,5 cm vom Lauf zum Einschlag, solange der Abzug zieht; Destiny Prometheus Lens: Strahl ≈ 9–12 % B, Mündungslicht ≈ 8 % (ego.PAYLOAD, Entscheidungsliste Block 9) |
| Sprint-Frequenz | 3,16 / 1,58 Hz (gemeinsam) | M Destiny Automatik/Handfeuerwaffe, für alle Klassen bis zu neuen Messungen (3c) |
| Griffe | grip, support, mag, charge | Modul-Feld EGO_GRIPS |
| Live-Teile | trigger = trigger, bolt = , port = , glow = focus_lens + disc_lens | Modul-Feld EGO_LIVE |

### Haltungen

| Haltung | Socket_Hand (m) | Handgelenk max | Herkunft |
|---|---|---|---|
| `hip` | [-0.136, -0.417, -0.156] | nur in Aktionen geprüft | M cubeescape-reference huefte.json (Destiny 2, Hollow Denial: Mündung 57,7/59,6, Visieröffnung 66,9/45,6); Lage E: Ausgleichsrechnung gegen diese Werte (0.33, Abgleich aller Waffen; Nutzer 31.10.2026 „Ja, nachziehen“ – bis dahin nur die Mündung eingestellt, das Visier lag 10–19 pp zu tief), gerechnet (Socket_Muzzle, Socket_Sight bzw. Socket_Reticle, Socket_Hand) Mündung 57,7/61,1 %, Visier 66,6/49,0 % – 12 mm tiefer als die Ausgleichslage: die Gehäusenase lag bei 53,4 % H in den Zonenspalten der Freihaltezone (A4, Ecke ab 55 %) |
| `ads` | [0.0, 0.0, 0.0] | nur in Aktionen geprüft | Visier-Standard v2: Socket_Eye ist der Augenpunkt, liegt in der Kamera; Waffenmodell ungezoomt, Welt zoomt je Klasse |
| `sprint` | [-0.1, -0.34, -0.23] | nur in Aktionen geprüft | E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-Spurgewehr-Sprint nicht gemessen (Motiongen destiny2:570) (Haltung POSES['sprint'] unverändert) |
| `lowered` | [-0.116, -0.377, -0.176] | nur in Aktionen geprüft | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| `crouch` | [-0.126, -0.407, -0.171] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `air` | [-0.136, -0.417, -0.141] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `holstered` | [-0.24, -0.25, -0.62] | nur in Aktionen geprüft | E (unter dem Bild) |
| `reload` | [-0.07, -0.34, -0.135] | nur in Aktionen geprüft | T Reload roll −20/pitch 12, für Destiny-Anmutung verstärkt (E) |
| `inspect_l` | [-0.06, -0.36, -0.16] | nur in Aktionen geprüft | E (Ego-Seite zeigt zur Kamera) |
| `inspect_r` | [-0.1, -0.36, -0.12] | nur in Aktionen geprüft | E (Oberseite und rechte Seite) |

### Aktionen

| Aktion | Beschreibung | Bilder | Marker (Bild) | Handgelenk max | Clip | Sichtung | Herkunft |
|---|---|---|---|---|---|---|---|
| `idle_hip` | Ruhe an der Hüfte (Atmen) | 75 (2.50 s) | – | offen° | offen | offen | E |
| `draw` | Ziehen | 17 (0.57 s) | Ready (12) | offen° | offen | offen | M Ziehen 0,23 s bis Hüfte (Auto Rifle, Q-REF) + Ausfedern E; Klasse trace_rifle: 25 → 17 Bilder (M Destiny-Spurgewehr Prometheus Lens ADS ein ≈ 12 Bilder bei 60/s (Motiongen destiny2:592) → 4 Bilder bei 30/s (Umrechnung wie Scharfschütze); Ager's Scepter ADS ein 13, aus 14 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen destiny2 › Gapfill, z-g34-agers) → aus 6 (Umrechnung wie Scharfschütze 14 → 6); Ziehen erstes Modellbild → ruhig 34 Bilder → 17; Nachladen ≈ 1,6 s bis Hüfte, „kein Klassenwert“ (destiny2:512) × TIME_SCALE = 60 Bilder bis Hüfte → Bezugsablauf (Hüfte bei 45/50) auf 67 Bilder gestreckt) |
| `holster` | Wegstecken | 8 (0.27 s) | HandOff (1), Holstered (8) | offen° | offen | offen | M Destiny-Wechsel: Wegstecken 0,08–0,27 s (Motiongen wechsel › 4, Entscheidungsliste 6.1 A) → 0,27 s ohne TIME_SCALE (bis 0.14: 0,60 s); Ablauf E (CE: Holster ab aktueller Stellung) |
| `aim_in` | Hüfte → Zielen | 4 (0.13 s) | Aimed (4) | offen° | offen | offen | E 0,30 s (CE-Handling Auto 0,39→0,20 s); Klasse trace_rifle: 10 → 4 Bilder (M Destiny-Spurgewehr Prometheus Lens ADS ein ≈ 12 Bilder bei 60/s (Motiongen destiny2:592) → 4 Bilder bei 30/s (Umrechnung wie Scharfschütze); Ager's Scepter ADS ein 13, aus 14 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen destiny2 › Gapfill, z-g34-agers) → aus 6 (Umrechnung wie Scharfschütze 14 → 6); Ziehen erstes Modellbild → ruhig 34 Bilder → 17; Nachladen ≈ 1,6 s bis Hüfte, „kein Klassenwert“ (destiny2:512) × TIME_SCALE = 60 Bilder bis Hüfte → Bezugsablauf (Hüfte bei 45/50) auf 67 Bilder gestreckt) |
| `aim_out` | Zielen → Hüfte | 6 (0.20 s) | Ready (6) | offen° | offen | offen | E; Klasse trace_rifle: 8 → 6 Bilder (M Destiny-Spurgewehr Prometheus Lens ADS ein ≈ 12 Bilder bei 60/s (Motiongen destiny2:592) → 4 Bilder bei 30/s (Umrechnung wie Scharfschütze); Ager's Scepter ADS ein 13, aus 14 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen destiny2 › Gapfill, z-g34-agers) → aus 6 (Umrechnung wie Scharfschütze 14 → 6); Ziehen erstes Modellbild → ruhig 34 Bilder → 17; Nachladen ≈ 1,6 s bis Hüfte, „kein Klassenwert“ (destiny2:512) × TIME_SCALE = 60 Bilder bis Hüfte → Bezugsablauf (Hüfte bei 45/50) auf 67 Bilder gestreckt) |
| `fire_hip` | Dauerfeuer aus der Hüfte | 32 (1.07 s) | Fire (2) | offen° | ego_BASIC-12-v2.1_fire_hip.mp4 | offen | M 720/min = 1 Schuss je 2,5 Bilder (Q-REF; bis 0.14 alle 2 Bilder ≈ 940/min); Rückstoß T 17,5 mm/3°; Klasse trace_rifle: 1000/min, Dauerstrahl (Dauerfeuer ohne Mündungsfeuer, Leuchtteile EGO_LIVE glow an, solange der Abzug zieht) (Schussbilder [2, 3, 5, 7, 9, 11, 12, 14, 16, 18, 20, 21, 23]) |
| `fire_ads` | Dauerfeuer im Zielen | 32 (1.07 s) | AimFire (2) | offen° | offen | offen | M Kadenz wie fire_hip; Rückstoß im Zielen nach RECOIL ads_* (5.1 A: Visier steht, die Welt wandert) E; Klasse trace_rifle: 1000/min, Dauerstrahl (Dauerfeuer ohne Mündungsfeuer, Leuchtteile EGO_LIVE glow an, solange der Abzug zieht) (Schussbilder [2, 3, 5, 7, 9, 11, 12, 14, 16, 18, 20, 21, 23]) |
| `reload_tactical` | Nachladen mit Restmunition | 67 (2.23 s) | HandOff (5), MagOut (13), MagIn (38), HandOn (51), Ready (62) | offen° | ego_BASIC-12-v2.1_reload_tactical.mp4 | offen | M MagIn ≈ 0,93 s; Ablauf T (Reload-Keys) mit Destiny-Kippen E; v2: Ausholen, Stoß bei MagIn, Nachfedern E; Klasse trace_rifle: 63 → 67 Bilder (M Destiny-Spurgewehr Prometheus Lens ADS ein ≈ 12 Bilder bei 60/s (Motiongen destiny2:592) → 4 Bilder bei 30/s (Umrechnung wie Scharfschütze); Ager's Scepter ADS ein 13, aus 14 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen destiny2 › Gapfill, z-g34-agers) → aus 6 (Umrechnung wie Scharfschütze 14 → 6); Ziehen erstes Modellbild → ruhig 34 Bilder → 17; Nachladen ≈ 1,6 s bis Hüfte, „kein Klassenwert“ (destiny2:512) × TIME_SCALE = 60 Bilder bis Hüfte → Bezugsablauf (Hüfte bei 45/50) auf 67 Bilder gestreckt) |
| `reload_empty` | Nachladen mit Restmunition, auch leer | 67 (2.23 s) | HandOff (5), MagOut (13), MagIn (38), HandOn (51), Ready (62) | offen° | offen | offen | M MagIn ≈ 0,93 s; Ablauf T (Reload-Keys) mit Destiny-Kippen E; v2: Ausholen, Stoß bei MagIn, Nachfedern E; Klasse trace_rifle: 63 → 67 Bilder (M Destiny-Spurgewehr Prometheus Lens ADS ein ≈ 12 Bilder bei 60/s (Motiongen destiny2:592) → 4 Bilder bei 30/s (Umrechnung wie Scharfschütze); Ager's Scepter ADS ein 13, aus 14 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen destiny2 › Gapfill, z-g34-agers) → aus 6 (Umrechnung wie Scharfschütze 14 → 6); Ziehen erstes Modellbild → ruhig 34 Bilder → 17; Nachladen ≈ 1,6 s bis Hüfte, „kein Klassenwert“ (destiny2:512) × TIME_SCALE = 60 Bilder bis Hüfte → Bezugsablauf (Hüfte bei 45/50) auf 67 Bilder gestreckt) |
| `inspect` | Betrachten | 120 (4.00 s) | Start (20), End (118) | offen° | offen | offen | E nach Apex/CoD-Muster (Ego-Seite, dann Oberseite); Destiny hat keinen Ego-Inspect |
| `sprint` | Sprint: Beginn, Schleife, Ende | 60 (2.00 s) | SprintLoop (10), Ready (60) | offen° | offen | offen | E (CE: Waffe senkt sich und rollt zur Mitte); period = Doppelschritt (seitlich), vertikal je Schritt: 19 Bilder = 0,633 s → 3,16 Schritte/s, seitlich 1,58 Hz, Rollen ±3,5°, U-Bogen (oben an den Seitenumkehren) nach Motiongen REF 0.23 (Destiny 2, Automatik/Handfeuerwaffe gemessen). 0.9: 10 Bilder = 6 Schritte/s („tapsig“). 0.15: Hub 12/10 → 22/18 mm (seitlich/vertikal) für ≈ 10 % H / 13 % B im Bild wie die Destiny-Automatik (Entscheidungsliste 3.1 A, gemessen wie in Schritt 2: Oberkante, linke Kante) |
| `lowered` | Gesenkte Haltung / Wandnähe | 45 (1.50 s) | Lowered (10), Ready (45) | offen° | offen | offen | E |
| `walk` | Gehen (liegende Acht) | 60 (2.00 s) | – | offen° | offen | offen | E (CE: liegende Acht) |
| `crouch` | Ducken | 30 (1.00 s) | Crouched (10) | offen° | offen | offen | E |
| `jump_land` | Sprung, Luftphase, Landung | 50 (1.67 s) | Air (10), Land (35) | offen° | offen | offen | E (CE: Anheben, Landefeder) |
| `sprint_to_aim` | Sprint → Zielen | 18 (0.60 s) | SprintOut (0), Aimed (12) | offen° | offen | offen | E (CE: ADS > Sprint) |
| `sprint_to_fire` | Sprint → Feuer | 26 (0.87 s) | SprintOut (0), Fire (7) | offen° | offen | offen | E (CE: Fire > Sprint); Klasse trace_rifle: 1000/min, Dauerstrahl (Dauerfeuer ohne Mündungsfeuer, Leuchtteile EGO_LIVE glow an, solange der Abzug zieht) (Schussbilder [7, 8, 10, 12, 14, 16, 17, 19]) |
| `draw_aim` | Ziehen bei gehaltenem Zielen | 35 (1.17 s) | Ready (18), Aimed (30) | offen° | offen | offen | E (CE: Draw nicht unterbrechbar, ADS danach) |
| `reload_to_switch` | Nachladen → Waffenwechsel (Abbruch) | 38 (1.27 s) | HandOff (5), Cancel (18), Holstered (35) | offen° | offen | offen | E (CE: Reload bricht bei Wechsel ab, Holster ab aktueller Stellung) |

### Abdeckung der Matrixzeilen

| Zeile | durch Aktion | Status |
|---|---|---|
| `pose_rest` | `idle_hip` | offen (nicht gesichtet) |
| `pose_hip` | `idle_hip` | offen (nicht gesichtet) |
| `draw` | `draw` | offen (nicht gesichtet) |
| `ready` | `draw` | offen (nicht gesichtet) |
| `holster` | `holster` | offen (nicht gesichtet) |
| `pose_aim` | `aim_in` | offen (nicht gesichtet) |
| `tr_hip_aim` | `aim_in` | offen (nicht gesichtet) |
| `tr_aim_hip` | `aim_out` | offen (nicht gesichtet) |
| `fire_auto` | `fire_ads` | offen (nicht gesichtet) |
| `recoil_mech` | `fire_hip` | offen (nicht gesichtet) |
| `recoil_camera` | `fire_hip` | offen (nicht gesichtet) |
| `reload_partial` | `reload_tactical` | offen (nicht gesichtet) |
| `reload_feed` | `reload_tactical` | offen (nicht gesichtet) |
| `reload_empty` | `reload_empty` | offen (nicht gesichtet) |
| `cycle` | `reload_empty` | offen (nicht gesichtet) |
| `inspect` | `inspect` | offen (nicht gesichtet) |
| `inspect_return` | `inspect` | offen (nicht gesichtet) |
| `sprint_in` | `sprint` | offen (nicht gesichtet) |
| `sprint_loop` | `sprint` | offen (nicht gesichtet) |
| `sprint_out` | `sprint` | offen (nicht gesichtet) |
| `pose_lowered` | `lowered` | offen (nicht gesichtet) |
| `tr_lowered_return` | `lowered` | offen (nicht gesichtet) |
| `move_walk` | `walk` | offen (nicht gesichtet) |
| `sway` | `walk` | offen (nicht gesichtet) |
| `crouch` | `crouch` | offen (nicht gesichtet) |
| `jump_start` | `jump_land` | offen (nicht gesichtet) |
| `air` | `jump_land` | offen (nicht gesichtet) |
| `land` | `jump_land` | offen (nicht gesichtet) |
| `tr_sprint_aim` | `sprint_to_aim` | offen (nicht gesichtet) |
| `tr_sprint_fire` | `sprint_to_fire` | offen (nicht gesichtet) |
| `tr_draw_aimheld` | `draw_aim` | offen (nicht gesichtet) |
| `tr_reload_switch` | `reload_to_switch` | offen (nicht gesichtet) |
| `switch` | `reload_to_switch` | offen (nicht gesichtet) |

## BASIC-15-v2.1 – Dauerlauf v2.1 (machine_gun)

### Klassen- und Spielwerte

| Wert | Stand | Herkunft |
|---|---|---|
| Klasse | machine_gun | Ego-Übertrag 0.33 „Armory“ P2: Hüfte und Sprint der Automatik, Ziehen und Nachladen nach Motiongen (Gurtkasten), Ablauf E |
| Kadenz | 900/min | M/S Shattered Cipher 900/min, 75 (Motiongen destiny2:273); Feuerart aus der Spec (Gurt → Dauerfeuer, FIRE_ALIAS); Bahnstufe wie die Automatik: Destiny-MG Hüfte 2,8 pp H, im Zielen bis 12,4 pp H über mehrere Stöße (rueckstoss:110), kein Wert je Schuss; Kick 1,3 E (schwere Waffe) |
| Magazin | 75 | M/S Shattered Cipher 900/min, 75 (Motiongen destiny2:273); Feuerart aus der Spec (Gurt → Dauerfeuer, FIRE_ALIAS); Bahnstufe wie die Automatik: Destiny-MG Hüfte 2,8 pp H, im Zielen bis 12,4 pp H über mehrere Stöße (rueckstoss:110), kein Wert je Schuss; Kick 1,3 E (schwere Waffe) |
| Feuerart | `full_auto` – Dauerfeuer | Spec (META fire, data/specs); Unity: gameplay.fire_mode (0.20) |
| Weltzoom im Zielen | 1.9 | M Glidepath (Entscheidungsliste 1.2 A, basic/reticles.py › CLASS_ZOOM) |
| Hüft-Fadenkreuz | ring_dot 3.2 % H | übertragen (Automatik) (4.1 A / 4.2 A, basic/reticles.py › HIP) |
| Sprint-Fadenkreuz | aus | basic/reticles.py › HIP.sprint (4.1 A) |
| Bahnstufe je Schuss | 1.00 % H | ego.RECOIL (gemeinsam, Automatik ≈ 1 % H je Schuss, 5.2 A) |
| Haltung `hip` | Socket_Hand [-0.114, -0.417, -0.155], Ziel [-0.096, -3.411, -0.342], Rollen 4.8° | M cubeescape-reference huefte.json (Destiny 2, Shattered Cipher Mündung 56,1/55,1, Optik 66/39,6; Hammerhead Mündung 56,2/64, Reflexöffnung 65,9/48,2); Lage E: Ausgleichsrechnung gegen diese Werte (0.33, Abgleich aller Waffen; Nutzer 31.10.2026 „Ja, nachziehen“ – bis dahin nur die Mündung eingestellt, das Visier lag 10–19 pp zu tief), gerechnet (Socket_Muzzle, Socket_Sight bzw. Socket_Reticle, Socket_Hand) Mündung 56,1/59,7 %, Visier 66,1/44,9 % – 3 mm tiefer als die Ausgleichslage: der oberste belegte Punkt lag genau auf der Ecke der Freihaltezone (A4, 55 % H; Richter 0.33) |
| Haltung `sprint` | Socket_Hand [-0.1, -0.34, -0.23], Ziel [1.2, -1.6, -0.55], Rollen -35° | E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-MG-Sprint nicht gemessen (Motiongen destiny2:561) (Haltung POSES['sprint'] unverändert) |
| Haltung `crouch` | Socket_Hand [-0.104, -0.407, -0.17], Rollen 7.800000000000001° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `air` | Socket_Hand [-0.114, -0.417, -0.14], Rollen 2.8000000000000007° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `lowered` | Socket_Hand [-0.094, -0.377, -0.175], Rollen 8.8° | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| Dauer `aim_out` | 11 Bilder bei 30/s (0.367 s) | M Destiny-MG ADS ein 20 Bilder bei 60/s (Motiongen destiny2:583) = Automatik (aim_in 10 bei 30/s); ADS aus Qullim's Terminus 21, Thunderlord 23 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen destiny2 › Gapfill, z-g34-kingsfall/-thunderlord) ≈ 22 → 11 (über lineare Fusion 19 → 10 und Automatik 20 → 10 hinaus; bis 0.33 Vorgabe 8); Ziehen 18 + 37 Bilder bei 60/s bis ruhig (wechsel:56) = 0,92 s → bis 0.33.1 28 Bilder; Nutzerentscheid 31.10.2026: Gapfill Qullim's Terminus 50, Thunderlord 42 ≈ 46 → 23 |
| Dauer `draw` | 23 Bilder bei 30/s (0.767 s) | M Destiny-MG ADS ein 20 Bilder bei 60/s (Motiongen destiny2:583) = Automatik (aim_in 10 bei 30/s); ADS aus Qullim's Terminus 21, Thunderlord 23 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen destiny2 › Gapfill, z-g34-kingsfall/-thunderlord) ≈ 22 → 11 (über lineare Fusion 19 → 10 und Automatik 20 → 10 hinaus; bis 0.33 Vorgabe 8); Ziehen 18 + 37 Bilder bei 60/s bis ruhig (wechsel:56) = 0,92 s → bis 0.33.1 28 Bilder; Nutzerentscheid 31.10.2026: Gapfill Qullim's Terminus 50, Thunderlord 42 ≈ 46 → 23 |
| Mündungsfeuer | 33 ms | M Destiny: 1–2 Bilder bei 60/s, Kern klein, Seitenflammen breiter, Zielen Automatik ≈ 20 % der Öffnung (Motiongen muendung › 6, Entscheidungsliste 5.3 A); Maße und Farben E (Stil v2.1) |
| Hülsen | rifle (42 × 9.6 mm) | E: Auswurffenster rechts unter der Klappe port_cover, Hülse nach rechts und etwas nach unten; Bahn: M Destiny: Hülse im 1. Blitzbild oder 1 Bild danach, rechts/rechts unten (Motiongen muendung › 6, Entscheidungsliste 5d/5.4 A); Geschwindigkeit, Drehung, Lebensdauer E |
| Rückstoß | ego.RECOIL (gemeinsam) | übertragen von der Automatik: Säule 1 % H je Schuss, im Zielen wandert die Welt (5.1 A / 5.2 A); Werkzeug: Modellkick der Aktion (fire_a/fire_b kick 0,6), keine Bahnstufe (E; Portal 2: obere Klaue ≈ 7 % H im ersten Schussbild) |
| Wirkung | Kugel, Einschlag bullet, Leuchtspur jeder 3. Schuss | E: Einschlag Kugel; Leuchtspur jeder 3. Schuss, 320 m/s, 2,4 m, warmweiß (BF6 B36A4: roter Strich zur Bildmitte ist Leuchtspur, Motiongen muendung › z-mf-bf6-b36a4; Destiny-MG in REF 0.36 nicht gemessen) (ego.PAYLOAD, Entscheidungsliste Block 9) |
| Sprint-Frequenz | 3,16 / 1,58 Hz (gemeinsam) | M Destiny Automatik/Handfeuerwaffe, für alle Klassen bis zu neuen Messungen (3c) |
| Griffe | grip, support, mag, charge, cover | Modul-Feld EGO_GRIPS |
| Live-Teile | trigger = trigger, bolt = bolt, port = port_cover, index = belt, rounds = line (4 Sätze), fill = counter_cell_1 + counter_cell_2 + counter_cell_3 + counter_cell_4 + counter_cell_5 | Modul-Feld EGO_LIVE |

### Haltungen

| Haltung | Socket_Hand (m) | Handgelenk max | Herkunft |
|---|---|---|---|
| `hip` | [-0.114, -0.417, -0.155] | nur in Aktionen geprüft | M cubeescape-reference huefte.json (Destiny 2, Shattered Cipher Mündung 56,1/55,1, Optik 66/39,6; Hammerhead Mündung 56,2/64, Reflexöffnung 65,9/48,2); Lage E: Ausgleichsrechnung gegen diese Werte (0.33, Abgleich aller Waffen; Nutzer 31.10.2026 „Ja, nachziehen“ – bis dahin nur die Mündung eingestellt, das Visier lag 10–19 pp zu tief), gerechnet (Socket_Muzzle, Socket_Sight bzw. Socket_Reticle, Socket_Hand) Mündung 56,1/59,7 %, Visier 66,1/44,9 % – 3 mm tiefer als die Ausgleichslage: der oberste belegte Punkt lag genau auf der Ecke der Freihaltezone (A4, 55 % H; Richter 0.33) |
| `ads` | [0.0, 0.0, 0.0] | nur in Aktionen geprüft | Visier-Standard v2: Socket_Eye ist der Augenpunkt, liegt in der Kamera; Waffenmodell ungezoomt, Welt zoomt je Klasse |
| `sprint` | [-0.1, -0.34, -0.23] | nur in Aktionen geprüft | E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-MG-Sprint nicht gemessen (Motiongen destiny2:561) (Haltung POSES['sprint'] unverändert) |
| `lowered` | [-0.094, -0.377, -0.175] | nur in Aktionen geprüft | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| `crouch` | [-0.104, -0.407, -0.17] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `air` | [-0.114, -0.417, -0.14] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `holstered` | [-0.24, -0.25, -0.62] | nur in Aktionen geprüft | E (unter dem Bild) |
| `reload` | [-0.07, -0.34, -0.135] | nur in Aktionen geprüft | T Reload roll −20/pitch 12, für Destiny-Anmutung verstärkt (E) |
| `inspect_l` | [-0.06, -0.36, -0.16] | nur in Aktionen geprüft | E (Ego-Seite zeigt zur Kamera) |
| `inspect_r` | [-0.1, -0.36, -0.12] | nur in Aktionen geprüft | E (Oberseite und rechte Seite) |

### Aktionen

| Aktion | Beschreibung | Bilder | Marker (Bild) | Handgelenk max | Clip | Sichtung | Herkunft |
|---|---|---|---|---|---|---|---|
| `idle_hip` | Ruhe an der Hüfte (Atmen) | 75 (2.50 s) | – | offen° | offen | offen | E |
| `draw` | Ziehen | 23 (0.77 s) | Ready (17) | offen° | offen | offen | M Ziehen 0,23 s bis Hüfte (Auto Rifle, Q-REF) + Ausfedern E; Klasse machine_gun: 25 → 23 Bilder (M Destiny-MG ADS ein 20 Bilder bei 60/s (Motiongen destiny2:583) = Automatik (aim_in 10 bei 30/s); ADS aus Qullim's Terminus 21, Thunderlord 23 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen destiny2 › Gapfill, z-g34-kingsfall/-thunderlord) ≈ 22 → 11 (über lineare Fusion 19 → 10 und Automatik 20 → 10 hinaus; bis 0.33 Vorgabe 8); Ziehen 18 + 37 Bilder bei 60/s bis ruhig (wechsel:56) = 0,92 s → bis 0.33.1 28 Bilder; Nutzerentscheid 31.10.2026: Gapfill Qullim's Terminus 50, Thunderlord 42 ≈ 46 → 23) |
| `holster` | Wegstecken | 8 (0.27 s) | HandOff (1), Holstered (8) | offen° | offen | offen | M Destiny-Wechsel: Wegstecken 0,08–0,27 s (Motiongen wechsel › 4, Entscheidungsliste 6.1 A) → 0,27 s ohne TIME_SCALE (bis 0.14: 0,60 s); Ablauf E (CE: Holster ab aktueller Stellung) |
| `aim_in` | Hüfte → Zielen | 10 (0.33 s) | Aimed (9) | offen° | offen | offen | E 0,30 s (CE-Handling Auto 0,39→0,20 s) |
| `aim_out` | Zielen → Hüfte | 11 (0.37 s) | Ready (11) | offen° | offen | offen | E; Klasse machine_gun: 8 → 11 Bilder (M Destiny-MG ADS ein 20 Bilder bei 60/s (Motiongen destiny2:583) = Automatik (aim_in 10 bei 30/s); ADS aus Qullim's Terminus 21, Thunderlord 23 Bilder bei 60/s erste Bewegung → Ruhe (Motiongen destiny2 › Gapfill, z-g34-kingsfall/-thunderlord) ≈ 22 → 11 (über lineare Fusion 19 → 10 und Automatik 20 → 10 hinaus; bis 0.33 Vorgabe 8); Ziehen 18 + 37 Bilder bei 60/s bis ruhig (wechsel:56) = 0,92 s → bis 0.33.1 28 Bilder; Nutzerentscheid 31.10.2026: Gapfill Qullim's Terminus 50, Thunderlord 42 ≈ 46 → 23) |
| `fire_hip` | Dauerfeuer aus der Hüfte | 32 (1.07 s) | Fire (2) | offen° | offen | offen | M 720/min = 1 Schuss je 2,5 Bilder (Q-REF; bis 0.14 alle 2 Bilder ≈ 940/min); Rückstoß T 17,5 mm/3°; Klasse machine_gun: 900/min, Dauerfeuer (Schussbilder [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]) |
| `fire_ads` | Dauerfeuer im Zielen | 32 (1.07 s) | AimFire (2) | offen° | offen | offen | M Kadenz wie fire_hip; Rückstoß im Zielen nach RECOIL ads_* (5.1 A: Visier steht, die Welt wandert) E; Klasse machine_gun: 900/min, Dauerfeuer (Schussbilder [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]) |
| `reload_tactical` | Nachladen (Deckel auf, Kasten tauschen, Gurt einlegen, Deckel zu, durchladen) | 183 (6.10 s) | HandOff (4), CoverOpen (24), MagOut (40), BoxIn (50), MagIn (64), CoverClosed (104), Chamber (125), HandOn (140), Ready (175) | offen° | ego_BASIC-15-v2.1_reload_tactical.mp4 | offen | M Destiny-MG Gurtkasten 4,40 s bis Hüfte, 4,87 ruhig: Deckel +0,63, Kasten +1,32, Gurt +1,70, Deckel zu +2,78 s (Motiongen nachladen:60) → Marker bei 19/40/51/83/132 von 146 Bildern, × TIME_SCALE; Ablauf E (Deckel hinten anheben, Kasten nach links unten aus dem Bild und zurück, Gurt in die Zuführschale, Deckel zuschlagen, Ladehebel aus der Hüfte wie der Scharfschütze; der Deckel springt nach dem Entriegeln allein auf, beim Kasten 3–6 cm weiter weg – sonst lag der Arm groß vor der Kamera); Munition voll beim Gurt |
| `reload_empty` | Nachladen (Deckel auf, Kasten tauschen, Gurt einlegen, Deckel zu, durchladen), auch leer | 183 (6.10 s) | HandOff (4), CoverOpen (24), MagOut (40), BoxIn (50), MagIn (64), CoverClosed (104), Chamber (125), HandOn (140), Ready (175) | offen° | offen | offen | M Destiny-MG Gurtkasten 4,40 s bis Hüfte, 4,87 ruhig: Deckel +0,63, Kasten +1,32, Gurt +1,70, Deckel zu +2,78 s (Motiongen nachladen:60) → Marker bei 19/40/51/83/132 von 146 Bildern, × TIME_SCALE; Ablauf E (Deckel hinten anheben, Kasten nach links unten aus dem Bild und zurück, Gurt in die Zuführschale, Deckel zuschlagen, Ladehebel aus der Hüfte wie der Scharfschütze; der Deckel springt nach dem Entriegeln allein auf, beim Kasten 3–6 cm weiter weg – sonst lag der Arm groß vor der Kamera); Munition voll beim Gurt |
| `inspect` | Betrachten | 120 (4.00 s) | Start (20), End (118) | offen° | offen | offen | E nach Apex/CoD-Muster (Ego-Seite, dann Oberseite); Destiny hat keinen Ego-Inspect |
| `sprint` | Sprint: Beginn, Schleife, Ende | 60 (2.00 s) | SprintLoop (10), Ready (60) | offen° | offen | offen | E (CE: Waffe senkt sich und rollt zur Mitte); period = Doppelschritt (seitlich), vertikal je Schritt: 19 Bilder = 0,633 s → 3,16 Schritte/s, seitlich 1,58 Hz, Rollen ±3,5°, U-Bogen (oben an den Seitenumkehren) nach Motiongen REF 0.23 (Destiny 2, Automatik/Handfeuerwaffe gemessen). 0.9: 10 Bilder = 6 Schritte/s („tapsig“). 0.15: Hub 12/10 → 22/18 mm (seitlich/vertikal) für ≈ 10 % H / 13 % B im Bild wie die Destiny-Automatik (Entscheidungsliste 3.1 A, gemessen wie in Schritt 2: Oberkante, linke Kante) |
| `lowered` | Gesenkte Haltung / Wandnähe | 45 (1.50 s) | Lowered (10), Ready (45) | offen° | offen | offen | E |
| `walk` | Gehen (liegende Acht) | 60 (2.00 s) | – | offen° | offen | offen | E (CE: liegende Acht) |
| `crouch` | Ducken | 30 (1.00 s) | Crouched (10) | offen° | offen | offen | E |
| `jump_land` | Sprung, Luftphase, Landung | 50 (1.67 s) | Air (10), Land (35) | offen° | offen | offen | E (CE: Anheben, Landefeder) |
| `sprint_to_aim` | Sprint → Zielen | 18 (0.60 s) | SprintOut (0), Aimed (12) | offen° | offen | offen | E (CE: ADS > Sprint) |
| `sprint_to_fire` | Sprint → Feuer | 26 (0.87 s) | SprintOut (0), Fire (7) | offen° | offen | offen | E (CE: Fire > Sprint); Klasse machine_gun: 900/min, Dauerfeuer (Schussbilder [7, 9, 11, 13, 15, 17, 19]) |
| `draw_aim` | Ziehen bei gehaltenem Zielen | 35 (1.17 s) | Ready (18), Aimed (30) | offen° | offen | offen | E (CE: Draw nicht unterbrechbar, ADS danach) |
| `reload_to_switch` | Nachladen → Waffenwechsel (Abbruch) | 38 (1.27 s) | HandOff (5), Cancel (18), Holstered (35) | offen° | offen | offen | E (CE: Reload bricht bei Wechsel ab, Holster ab aktueller Stellung) |

### Abdeckung der Matrixzeilen

| Zeile | durch Aktion | Status |
|---|---|---|
| `pose_rest` | `idle_hip` | offen (nicht gesichtet) |
| `pose_hip` | `idle_hip` | offen (nicht gesichtet) |
| `draw` | `draw` | offen (nicht gesichtet) |
| `ready` | `draw` | offen (nicht gesichtet) |
| `holster` | `holster` | offen (nicht gesichtet) |
| `pose_aim` | `aim_in` | offen (nicht gesichtet) |
| `tr_hip_aim` | `aim_in` | offen (nicht gesichtet) |
| `tr_aim_hip` | `aim_out` | offen (nicht gesichtet) |
| `fire_auto` | `fire_ads` | offen (nicht gesichtet) |
| `recoil_mech` | `fire_hip` | offen (nicht gesichtet) |
| `recoil_camera` | `fire_hip` | offen (nicht gesichtet) |
| `reload_partial` | `reload_tactical` | offen (nicht gesichtet) |
| `reload_feed` | `reload_tactical` | offen (nicht gesichtet) |
| `reload_empty` | `reload_empty` | offen (nicht gesichtet) |
| `cycle` | `reload_empty` | offen (nicht gesichtet) |
| `inspect` | `inspect` | offen (nicht gesichtet) |
| `inspect_return` | `inspect` | offen (nicht gesichtet) |
| `sprint_in` | `sprint` | offen (nicht gesichtet) |
| `sprint_loop` | `sprint` | offen (nicht gesichtet) |
| `sprint_out` | `sprint` | offen (nicht gesichtet) |
| `pose_lowered` | `lowered` | offen (nicht gesichtet) |
| `tr_lowered_return` | `lowered` | offen (nicht gesichtet) |
| `move_walk` | `walk` | offen (nicht gesichtet) |
| `sway` | `walk` | offen (nicht gesichtet) |
| `crouch` | `crouch` | offen (nicht gesichtet) |
| `jump_start` | `jump_land` | offen (nicht gesichtet) |
| `air` | `jump_land` | offen (nicht gesichtet) |
| `land` | `jump_land` | offen (nicht gesichtet) |
| `tr_sprint_aim` | `sprint_to_aim` | offen (nicht gesichtet) |
| `tr_sprint_fire` | `sprint_to_fire` | offen (nicht gesichtet) |
| `tr_draw_aimheld` | `draw_aim` | offen (nicht gesichtet) |
| `tr_reload_switch` | `reload_to_switch` | offen (nicht gesichtet) |
| `switch` | `reload_to_switch` | offen (nicht gesichtet) |

## BASIC-08-v2.1 – Streuer v2.1 (shotgun)

### Klassen- und Spielwerte

| Wert | Stand | Herkunft |
|---|---|---|
| Klasse | shotgun | Ego-Übertrag 0.33 „Armory“ P3: Hüfte und Sprint der Automatik, Anflug und Ziehen nach Motiongen (Schrotflinte), Pumpen nach jedem Schuss und Einzelladen E nach den Destiny-Zeiten |
| Kadenz | 80/min | S Hawthorne 80/min, Magazin 7 (Menü, Motiongen destiny2:258; Baligant 55/min, 5) → 80/min, Magazin 6 E (Röhrenmagazin des Modells „hält sechs Patronen“); Feuerart aus der Spec (Pumpe: ein Schuss je Zug, danach fire_cycle); Bahnstufe 0,03 M: Ring 1–2 Bilder ≈ 3 % H hoch, nach 0,10 s zurück (destiny2:495) → Erholung E ab 0,2 s mit 3 Hz; Kick 3,0 E (schwerer Einzelschuss wie der Scharfschütze) |
| Magazin | 6 | S Hawthorne 80/min, Magazin 7 (Menü, Motiongen destiny2:258; Baligant 55/min, 5) → 80/min, Magazin 6 E (Röhrenmagazin des Modells „hält sechs Patronen“); Feuerart aus der Spec (Pumpe: ein Schuss je Zug, danach fire_cycle); Bahnstufe 0,03 M: Ring 1–2 Bilder ≈ 3 % H hoch, nach 0,10 s zurück (destiny2:495) → Erholung E ab 0,2 s mit 3 Hz; Kick 3,0 E (schwerer Einzelschuss wie der Scharfschütze) |
| Feuerart | `pump_action` – Vorderschaftrepetierer (ein Schuss je Zug, danach Pumpe als Klassenaktion fire_cycle/fire_cycle_ads; Nachladen je Patrone reload_shell, ein Zug am Abzug bricht ab) | Spec (META fire, data/specs); Unity: gameplay.fire_mode (0.20) |
| Weltzoom im Zielen | 1.25 | M Glidepath (Entscheidungsliste 1.2 A, basic/reticles.py › CLASS_ZOOM) |
| Hüft-Fadenkreuz | corners 4.5 % H | entworfen (4.1 A / 4.2 A, basic/reticles.py › HIP) |
| Sprint-Fadenkreuz | aus | basic/reticles.py › HIP.sprint (4.1 A) |
| Bahnstufe je Schuss | 3.00 % H | S Hawthorne 80/min, Magazin 7 (Menü, Motiongen destiny2:258; Baligant 55/min, 5) → 80/min, Magazin 6 E (Röhrenmagazin des Modells „hält sechs Patronen“); Feuerart aus der Spec (Pumpe: ein Schuss je Zug, danach fire_cycle); Bahnstufe 0,03 M: Ring 1–2 Bilder ≈ 3 % H hoch, nach 0,10 s zurück (destiny2:495) → Erholung E ab 0,2 s mit 3 Hz; Kick 3,0 E (schwerer Einzelschuss wie der Scharfschütze) |
| Haltung `reload` | Socket_Hand [-0.09, -0.36, -0.16], Ziel [0.55, -2.4, 0.25], Rollen -60° | E nach Destiny-Schrotflinte (Einzelladen, Motiongen nachladen:52/53): Waffe vor dem Körper nach rechts gerollt, Ladeklappe zeigt nach links unten zur Stützhand |
| Haltung `hip` | Socket_Hand [-0.19, -0.42, -0.23], Ziel [0.02, -3.0, -0.2], Rollen 6° | M Destiny-Schrotflinte Hüfte: Mündung FILO 57/63 (Motiongen huefte:54), ≈ 58/66 (destiny2:495); Lage E wie die Automatik: an der Schrotflinte gerechnet Mündung 58,4/64,1 % (Haltung POSES['hip'] unverändert) |
| Haltung `sprint` | Socket_Hand [-0.1, -0.34, -0.23], Ziel [1.2, -1.6, -0.55], Rollen -35° | E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-Schrotflinten-Sprint nicht gemessen (Motiongen destiny2:566) (Haltung POSES['sprint'] unverändert) |
| Dauer `aim_in` | 10 Bilder bei 30/s (0.333 s) | M Destiny-Schrotflinte FILO ADS ein ≈ 13 Bilder bei 60/s (Motiongen destiny2:588) → 5 Bilder bei 30/s (Umrechnung mit dem Zielen-Nachlauf wie Spur 12 → 4, Scharfschütze 14 → 6); ADS aus 6–8 Bilder bei 60/s → 3; Ziehen 14 Bilder bei 60/s bis hüftähnlich (wechsel:47) + Ausfedern E wie die Handfeuerwaffe (19) = 0,55 s → bis 0.33.1 17 Bilder; Nutzerentscheid 31.10.2026: The Fourth Horseman ADS ein 18–23 Bilder bei 60/s bis Ruhe → aim_in 10 (wie Automatik 20 → 10; aus geht dort immer ins Nachladen, bleibt 3), erstes Modellbild → ruhig 54 Bilder (Motiongen destiny2 › Gapfill) → draw 27 |
| Dauer `aim_out` | 3 Bilder bei 30/s (0.100 s) | M Destiny-Schrotflinte FILO ADS ein ≈ 13 Bilder bei 60/s (Motiongen destiny2:588) → 5 Bilder bei 30/s (Umrechnung mit dem Zielen-Nachlauf wie Spur 12 → 4, Scharfschütze 14 → 6); ADS aus 6–8 Bilder bei 60/s → 3; Ziehen 14 Bilder bei 60/s bis hüftähnlich (wechsel:47) + Ausfedern E wie die Handfeuerwaffe (19) = 0,55 s → bis 0.33.1 17 Bilder; Nutzerentscheid 31.10.2026: The Fourth Horseman ADS ein 18–23 Bilder bei 60/s bis Ruhe → aim_in 10 (wie Automatik 20 → 10; aus geht dort immer ins Nachladen, bleibt 3), erstes Modellbild → ruhig 54 Bilder (Motiongen destiny2 › Gapfill) → draw 27 |
| Dauer `draw` | 27 Bilder bei 30/s (0.900 s) | M Destiny-Schrotflinte FILO ADS ein ≈ 13 Bilder bei 60/s (Motiongen destiny2:588) → 5 Bilder bei 30/s (Umrechnung mit dem Zielen-Nachlauf wie Spur 12 → 4, Scharfschütze 14 → 6); ADS aus 6–8 Bilder bei 60/s → 3; Ziehen 14 Bilder bei 60/s bis hüftähnlich (wechsel:47) + Ausfedern E wie die Handfeuerwaffe (19) = 0,55 s → bis 0.33.1 17 Bilder; Nutzerentscheid 31.10.2026: The Fourth Horseman ADS ein 18–23 Bilder bei 60/s bis Ruhe → aim_in 10 (wie Automatik 20 → 10; aus geht dort immer ins Nachladen, bleibt 3), erstes Modellbild → ruhig 54 Bilder (Motiongen destiny2 › Gapfill) → draw 27 |
| Mündungsfeuer | 33 ms | M Destiny: 1–2 Bilder bei 60/s, Kern klein, Seitenflammen breiter, Zielen Automatik ≈ 20 % der Öffnung (Motiongen muendung › 6, Entscheidungsliste 5.3 A); Maße und Farben E (Stil v2.1) |
| Hülsen | shotshell (50 × 19 mm) | E: Auswurffenster rechts im Oberen Gehäuse beim Zurückziehen der Pumpe, Hülse nach rechts, etwas hoch und vorn; Bahn: M Destiny: Hülse im 1. Blitzbild oder 1 Bild danach, rechts/rechts unten (Motiongen muendung › 6, Entscheidungsliste 5d/5.4 A); Geschwindigkeit, Drehung, Lebensdauer E |
| Rückstoß | ego.RECOIL (gemeinsam) | übertragen von der Automatik: Säule 1 % H je Schuss, im Zielen wandert die Welt (5.1 A / 5.2 A); Werkzeug: Modellkick der Aktion (fire_a/fire_b kick 0,6), keine Bahnstufe (E; Portal 2: obere Klaue ≈ 7 % H im ersten Schussbild) |
| Wirkung | Schrot 12 Kugeln, Kegel 3° | S 12 Kugeln, feste Muster (Destiny 6.3.0); im Bild EIN Einschlag je Schuss (M, REF 0.36 z-im-python) → die Kugeln treffen (Scheiben), gezeigt wird ein Einschlag mit einem Loch an der mittleren Kugel (Nutzerentscheid 181); Kegel 3,0° E (ego.PAYLOAD, Entscheidungsliste Block 9) |
| Sprint-Frequenz | 3,16 / 1,58 Hz (gemeinsam) | M Destiny Automatik/Handfeuerwaffe, für alle Klassen bis zu neuen Messungen (3c) |
| Griffe | grip, support, mag, charge | Modul-Feld EGO_GRIPS |
| Live-Teile | trigger = trigger, bolt = , port =  | Modul-Feld EGO_LIVE |

### Haltungen

| Haltung | Socket_Hand (m) | Handgelenk max | Herkunft |
|---|---|---|---|
| `hip` | [-0.19, -0.42, -0.23] | nur in Aktionen geprüft | M Destiny-Schrotflinte Hüfte: Mündung FILO 57/63 (Motiongen huefte:54), ≈ 58/66 (destiny2:495); Lage E wie die Automatik: an der Schrotflinte gerechnet Mündung 58,4/64,1 % (Haltung POSES['hip'] unverändert) |
| `ads` | [0.0, 0.0, 0.0] | nur in Aktionen geprüft | Visier-Standard v2: Socket_Eye ist der Augenpunkt, liegt in der Kamera; Waffenmodell ungezoomt, Welt zoomt je Klasse |
| `sprint` | [-0.1, -0.34, -0.23] | nur in Aktionen geprüft | E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-Schrotflinten-Sprint nicht gemessen (Motiongen destiny2:566) (Haltung POSES['sprint'] unverändert) |
| `lowered` | [-0.17, -0.38, -0.25] | nur in Aktionen geprüft | E |
| `crouch` | [-0.18, -0.41, -0.245] | nur in Aktionen geprüft | E (wie hip versetzt, 0.15 mit hip gesenkt) |
| `air` | [-0.19, -0.42, -0.215] | nur in Aktionen geprüft | E (wie hip versetzt, 0.15 mit hip gesenkt) |
| `holstered` | [-0.24, -0.25, -0.62] | nur in Aktionen geprüft | E (unter dem Bild) |
| `reload` | [-0.09, -0.36, -0.16] | nur in Aktionen geprüft | E nach Destiny-Schrotflinte (Einzelladen, Motiongen nachladen:52/53): Waffe vor dem Körper nach rechts gerollt, Ladeklappe zeigt nach links unten zur Stützhand |
| `inspect_l` | [-0.06, -0.36, -0.16] | nur in Aktionen geprüft | E (Ego-Seite zeigt zur Kamera) |
| `inspect_r` | [-0.1, -0.36, -0.12] | nur in Aktionen geprüft | E (Oberseite und rechte Seite) |

### Aktionen

| Aktion | Beschreibung | Bilder | Marker (Bild) | Handgelenk max | Clip | Sichtung | Herkunft |
|---|---|---|---|---|---|---|---|
| `idle_hip` | Ruhe an der Hüfte (Atmen) | 75 (2.50 s) | – | offen° | offen | offen | E |
| `draw` | Ziehen | 27 (0.90 s) | Ready (19) | offen° | offen | offen | M Ziehen 0,23 s bis Hüfte (Auto Rifle, Q-REF) + Ausfedern E; Klasse shotgun: 25 → 27 Bilder (M Destiny-Schrotflinte FILO ADS ein ≈ 13 Bilder bei 60/s (Motiongen destiny2:588) → 5 Bilder bei 30/s (Umrechnung mit dem Zielen-Nachlauf wie Spur 12 → 4, Scharfschütze 14 → 6); ADS aus 6–8 Bilder bei 60/s → 3; Ziehen 14 Bilder bei 60/s bis hüftähnlich (wechsel:47) + Ausfedern E wie die Handfeuerwaffe (19) = 0,55 s → bis 0.33.1 17 Bilder; Nutzerentscheid 31.10.2026: The Fourth Horseman ADS ein 18–23 Bilder bei 60/s bis Ruhe → aim_in 10 (wie Automatik 20 → 10; aus geht dort immer ins Nachladen, bleibt 3), erstes Modellbild → ruhig 54 Bilder (Motiongen destiny2 › Gapfill) → draw 27) |
| `holster` | Wegstecken | 8 (0.27 s) | HandOff (1), Holstered (8) | offen° | offen | offen | M Destiny-Wechsel: Wegstecken 0,08–0,27 s (Motiongen wechsel › 4, Entscheidungsliste 6.1 A) → 0,27 s ohne TIME_SCALE (bis 0.14: 0,60 s); Ablauf E (CE: Holster ab aktueller Stellung) |
| `aim_in` | Hüfte → Zielen | 10 (0.33 s) | Aimed (9) | offen° | offen | offen | E 0,30 s (CE-Handling Auto 0,39→0,20 s); Klasse shotgun: 10 → 10 Bilder (M Destiny-Schrotflinte FILO ADS ein ≈ 13 Bilder bei 60/s (Motiongen destiny2:588) → 5 Bilder bei 30/s (Umrechnung mit dem Zielen-Nachlauf wie Spur 12 → 4, Scharfschütze 14 → 6); ADS aus 6–8 Bilder bei 60/s → 3; Ziehen 14 Bilder bei 60/s bis hüftähnlich (wechsel:47) + Ausfedern E wie die Handfeuerwaffe (19) = 0,55 s → bis 0.33.1 17 Bilder; Nutzerentscheid 31.10.2026: The Fourth Horseman ADS ein 18–23 Bilder bei 60/s bis Ruhe → aim_in 10 (wie Automatik 20 → 10; aus geht dort immer ins Nachladen, bleibt 3), erstes Modellbild → ruhig 54 Bilder (Motiongen destiny2 › Gapfill) → draw 27) |
| `aim_out` | Zielen → Hüfte | 3 (0.10 s) | Ready (3) | offen° | offen | offen | E; Klasse shotgun: 8 → 3 Bilder (M Destiny-Schrotflinte FILO ADS ein ≈ 13 Bilder bei 60/s (Motiongen destiny2:588) → 5 Bilder bei 30/s (Umrechnung mit dem Zielen-Nachlauf wie Spur 12 → 4, Scharfschütze 14 → 6); ADS aus 6–8 Bilder bei 60/s → 3; Ziehen 14 Bilder bei 60/s bis hüftähnlich (wechsel:47) + Ausfedern E wie die Handfeuerwaffe (19) = 0,55 s → bis 0.33.1 17 Bilder; Nutzerentscheid 31.10.2026: The Fourth Horseman ADS ein 18–23 Bilder bei 60/s bis Ruhe → aim_in 10 (wie Automatik 20 → 10; aus geht dort immer ins Nachladen, bleibt 3), erstes Modellbild → ruhig 54 Bilder (Motiongen destiny2 › Gapfill) → draw 27) |
| `fire_hip` | Dauerfeuer aus der Hüfte | 32 (1.07 s) | Fire (2) | offen° | offen | offen | M 720/min = 1 Schuss je 2,5 Bilder (Q-REF; bis 0.14 alle 2 Bilder ≈ 940/min); Rückstoß T 17,5 mm/3°; Klasse shotgun: 80/min, Vorderschaftrepetierer (ein Schuss je Zug, danach Pumpe als Klassenaktion fire_cycle/fire_cycle_ads; Nachladen je Patrone reload_shell, ein Zug am Abzug bricht ab) (Schussbilder [2, 24]) |
| `fire_ads` | Dauerfeuer im Zielen | 32 (1.07 s) | AimFire (2) | offen° | offen | offen | M Kadenz wie fire_hip; Rückstoß im Zielen nach RECOIL ads_* (5.1 A: Visier steht, die Welt wandert) E; Klasse shotgun: 80/min, Vorderschaftrepetierer (ein Schuss je Zug, danach Pumpe als Klassenaktion fire_cycle/fire_cycle_ads; Nachladen je Patrone reload_shell, ein Zug am Abzug bricht ab) (Schussbilder [2, 24]) |
| `reload_tactical` | Nachladen: Einstieg mit der ersten Patrone (Waffe kippen, Patrone holen, durch die Ladeklappe schieben) | 23 (0.77 s) | HandOff (2), ShellIn (19) | offen° | ego_BASIC-08-v2.1_reload_tactical.mp4 | offen | M Destiny-Schrotflinte Einzelladen: erste Patrone 0,57–0,60 s nach Beginn (Motiongen nachladen:109) → ShellIn bei 15 von 18 Bildern (× TIME_SCALE: 0,63 s); Ablauf E (Stützhand verlässt die Pumpe, holt die Patrone unter dem Bild, schiebt sie von unten durch die Ladeklappe); taktisch gegen leer nicht gemessen: ein Einstieg, nach leerem Beginn Pumpen am Ende |
| `reload_empty` | Nachladen: Einstieg mit der ersten Patrone (Waffe kippen, Patrone holen, durch die Ladeklappe schieben), auch leer | 23 (0.77 s) | HandOff (2), ShellIn (19) | offen° | offen | offen | M Destiny-Schrotflinte Einzelladen: erste Patrone 0,57–0,60 s nach Beginn (Motiongen nachladen:109) → ShellIn bei 15 von 18 Bildern (× TIME_SCALE: 0,63 s); Ablauf E (Stützhand verlässt die Pumpe, holt die Patrone unter dem Bild, schiebt sie von unten durch die Ladeklappe); taktisch gegen leer nicht gemessen: ein Einstieg, nach leerem Beginn Pumpen am Ende |
| `inspect` | Betrachten | 120 (4.00 s) | Start (20), End (118) | offen° | offen | offen | E nach Apex/CoD-Muster (Ego-Seite, dann Oberseite); Destiny hat keinen Ego-Inspect |
| `sprint` | Sprint: Beginn, Schleife, Ende | 60 (2.00 s) | SprintLoop (10), Ready (60) | offen° | offen | offen | E (CE: Waffe senkt sich und rollt zur Mitte); period = Doppelschritt (seitlich), vertikal je Schritt: 19 Bilder = 0,633 s → 3,16 Schritte/s, seitlich 1,58 Hz, Rollen ±3,5°, U-Bogen (oben an den Seitenumkehren) nach Motiongen REF 0.23 (Destiny 2, Automatik/Handfeuerwaffe gemessen). 0.9: 10 Bilder = 6 Schritte/s („tapsig“). 0.15: Hub 12/10 → 22/18 mm (seitlich/vertikal) für ≈ 10 % H / 13 % B im Bild wie die Destiny-Automatik (Entscheidungsliste 3.1 A, gemessen wie in Schritt 2: Oberkante, linke Kante) |
| `lowered` | Gesenkte Haltung / Wandnähe | 45 (1.50 s) | Lowered (10), Ready (45) | offen° | offen | offen | E |
| `walk` | Gehen (liegende Acht) | 60 (2.00 s) | – | offen° | offen | offen | E (CE: liegende Acht) |
| `crouch` | Ducken | 30 (1.00 s) | Crouched (10) | offen° | offen | offen | E |
| `jump_land` | Sprung, Luftphase, Landung | 50 (1.67 s) | Air (10), Land (35) | offen° | offen | offen | E (CE: Anheben, Landefeder) |
| `sprint_to_aim` | Sprint → Zielen | 18 (0.60 s) | SprintOut (0), Aimed (12) | offen° | offen | offen | E (CE: ADS > Sprint) |
| `sprint_to_fire` | Sprint → Feuer | 26 (0.87 s) | SprintOut (0), Fire (7) | offen° | offen | offen | E (CE: Fire > Sprint); Klasse shotgun: 80/min, Vorderschaftrepetierer (ein Schuss je Zug, danach Pumpe als Klassenaktion fire_cycle/fire_cycle_ads; Nachladen je Patrone reload_shell, ein Zug am Abzug bricht ab) (Schussbilder [7]) |
| `draw_aim` | Ziehen bei gehaltenem Zielen | 35 (1.17 s) | Ready (18), Aimed (30) | offen° | offen | offen | E (CE: Draw nicht unterbrechbar, ADS danach) |
| `reload_to_switch` | Nachladen → Waffenwechsel (Abbruch) | 38 (1.27 s) | HandOff (5), Cancel (18), Holstered (35) | offen° | offen | offen | E (CE: Reload bricht bei Wechsel ab, Holster ab aktueller Stellung) |
| `fire_cycle` | Pumpen nach dem Schuss aus der Hüfte (Pumpe zurück, Hülse, vor) | 21 (0.70 s) | Eject (16), Chamber (20) | offen° | ego_BASIC-08-v2.1_fire_cycle.mp4 | offen | M Destiny-Schrotflinte: Pumpen vor dem zweiten Schuss, Hülse rechts 0,63 s nach dem Schuss (Motiongen destiny2:495) → Pumpe hinten bei Bild 16–17 (0,55 s), vorn bei 20, Ende 21 (0,70 s) vor dem nächsten Schuss (80/min = 0,75 s); Ablauf E (Stützhand auf der Pumpe, Waffe ruckt beim Zurückziehen leicht zurück) |
| `fire_cycle_ads` | Pumpen nach dem Schuss im Zielen (Waffe bleibt im Anschlag) | 21 (0.70 s) | Eject (16), Chamber (20) | offen° | offen | offen | E wie fire_cycle, im Zielen ohne Kippen (Kimme und Korn bleiben vor dem Auge, nur ein kleiner Ruck zurück) |
| `reload_shell` | Nachladen: eine weitere Patrone (Unity wiederholt bis voll) | 24 (0.80 s) | ShellIn (20) | offen° | ego_BASIC-08-v2.1_reload_shell.mp4 | offen | M Destiny-Schrotflinte Einzelladen 0,617–0,633 s je Patrone (Hawthorne, Motiongen nachladen:52; Baligant 0,85–0,87, :53) → 19 Bilder (× TIME_SCALE 0,79 s); Ablauf E wie der Einstieg |
| `reload_end` | Nachladen: zurück zur Hüfte (voll oder durch Feuer abgebrochen) | 10 (0.33 s) | HandOn (8), Ready (10) | offen° | offen | offen | E: Rückweg kurz (0,33 s), damit ein Zug am Abzug während des Nachladens bald schießt (Destiny bricht das Einzelladen mit Feuer ab, nicht gemessen) |
| `reload_end_pump` | Nachladen nach leerem Beginn: zurück zur Hüfte und pumpen | 20 (0.67 s) | HandOn (8), Chamber (16), Ready (20) | offen° | ego_BASIC-08-v2.1_reload_end_pump.mp4 | offen | M Destiny-Schrotflinte: einmal Repetieren am Ende des Einzelladens (Motiongen nachladen:109); Ablauf E wie fire_cycle |

### Abdeckung der Matrixzeilen

| Zeile | durch Aktion | Status |
|---|---|---|
| `pose_rest` | `idle_hip` | offen (nicht gesichtet) |
| `pose_hip` | `idle_hip` | offen (nicht gesichtet) |
| `draw` | `draw` | offen (nicht gesichtet) |
| `ready` | `draw` | offen (nicht gesichtet) |
| `holster` | `holster` | offen (nicht gesichtet) |
| `pose_aim` | `aim_in` | offen (nicht gesichtet) |
| `tr_hip_aim` | `aim_in` | offen (nicht gesichtet) |
| `tr_aim_hip` | `aim_out` | offen (nicht gesichtet) |
| `fire_auto` | `fire_ads` | offen (nicht gesichtet) |
| `recoil_mech` | `fire_hip` | offen (nicht gesichtet) |
| `recoil_camera` | `fire_hip` | offen (nicht gesichtet) |
| `reload_partial` | `reload_tactical` | offen (nicht gesichtet) |
| `reload_feed` | `reload_tactical` | offen (nicht gesichtet) |
| `reload_empty` | `reload_empty` | offen (nicht gesichtet) |
| `cycle` | `reload_empty` | offen (nicht gesichtet) |
| `inspect` | `inspect` | offen (nicht gesichtet) |
| `inspect_return` | `inspect` | offen (nicht gesichtet) |
| `sprint_in` | `sprint` | offen (nicht gesichtet) |
| `sprint_loop` | `sprint` | offen (nicht gesichtet) |
| `sprint_out` | `sprint` | offen (nicht gesichtet) |
| `pose_lowered` | `lowered` | offen (nicht gesichtet) |
| `tr_lowered_return` | `lowered` | offen (nicht gesichtet) |
| `move_walk` | `walk` | offen (nicht gesichtet) |
| `sway` | `walk` | offen (nicht gesichtet) |
| `crouch` | `crouch` | offen (nicht gesichtet) |
| `jump_start` | `jump_land` | offen (nicht gesichtet) |
| `air` | `jump_land` | offen (nicht gesichtet) |
| `land` | `jump_land` | offen (nicht gesichtet) |
| `tr_sprint_aim` | `sprint_to_aim` | offen (nicht gesichtet) |
| `tr_sprint_fire` | `sprint_to_fire` | offen (nicht gesichtet) |
| `tr_draw_aimheld` | `draw_aim` | offen (nicht gesichtet) |
| `tr_reload_switch` | `reload_to_switch` | offen (nicht gesichtet) |
| `switch` | `reload_to_switch` | offen (nicht gesichtet) |

## BASIC-10-v2.1 – Glutkern v2.1 (fusion_rifle)

### Klassen- und Spielwerte

| Wert | Stand | Herkunft |
|---|---|---|
| Klasse | fusion_rifle | Ego-Übertrag 0.33 „Armory“ P3: Hüfte, Anflug, Aufladen und Nachladen nach Motiongen (Fusion), Sprint der Automatik, Nachladen der Bezugsklasse mit der Energiezelle (leer wie taktisch, kein Ladehebel) |
| Kadenz | 60/min | S Cartesian Coordinate Laden 500 ms, Magazin 7 (Menü, Motiongen destiny2:254), gemessen 0,517 s (destiny2:499); Salve 5–6 Strahlen in 0,25 s → 6 Schuss im Abstand 0,05 s (1200/min); Takt gehalten 60/min E (Aufladen 0,5 + Salve 0,25 + Pause); Feuerart aus der Spec (Aufladen → Salve); Leuchten fällt in 0,3 s (Modul charge_fire: 9 Bilder); Bahnstufe 0,004 je Strahl E (Waffe ruhig, Mündung steigt über die Salve, destiny2:254/499), Kick 0,6 je Strahl E |
| Magazin | 7 | S Cartesian Coordinate Laden 500 ms, Magazin 7 (Menü, Motiongen destiny2:254), gemessen 0,517 s (destiny2:499); Salve 5–6 Strahlen in 0,25 s → 6 Schuss im Abstand 0,05 s (1200/min); Takt gehalten 60/min E (Aufladen 0,5 + Salve 0,25 + Pause); Feuerart aus der Spec (Aufladen → Salve); Leuchten fällt in 0,3 s (Modul charge_fire: 9 Bilder); Bahnstufe 0,004 je Strahl E (Waffe ruhig, Mündung steigt über die Salve, destiny2:254/499), Kick 0,6 je Strahl E |
| Feuerart | `charge_burst` – Aufladen → Salve (Abzug halten lädt in charge_s, bei voller Ladung burst_shots Schuss; Loslassen bricht ab; gehalten Zyklus um Zyklus im Takt rpm) | Spec (META fire, data/specs); Unity: gameplay.fire_mode (0.20) |
| Weltzoom im Zielen | 1.45 | M Glidepath (Entscheidungsliste 1.2 A, basic/reticles.py › CLASS_ZOOM) |
| Hüft-Fadenkreuz | ring_corners 5.5 % H | gemessen (Glidepath, Quadrat 5,5 % H, Ring Ø 1,7 % H) (4.1 A / 4.2 A, basic/reticles.py › HUD_HIP) |
| Sprint-Fadenkreuz | aus | basic/reticles.py › HIP.sprint (4.1 A) |
| Absehen im Glas | corners 4.5 % H | basic/reticles.py › HIP (common.drawn_reticle, Teil des Modells); Unity: gameplay.sight_form |
| Salve | 6 Schuss je Zug, 1200/min in der Salve (0.050 s), Salvenbeginn alle 6.000 s; gehalten Salve um Salve | Länge aus der Spec (META fire), Takt und Folge: S Cartesian Coordinate Laden 500 ms, Magazin 7 (Menü, Motiongen destiny2:254), gemessen 0,517 s (destiny2:499); Salve 5–6 Strahlen in 0,25 s → 6 Schuss im Abstand 0,05 s (1200/min); Takt gehalten 60/min E (Aufladen 0,5 + Salve 0,25 + Pause); Feuerart aus der Spec (Aufladen → Salve); Leuchten fällt in 0,3 s (Modul charge_fire: 9 Bilder); Bahnstufe 0,004 je Strahl E (Waffe ruhig, Mündung steigt über die Salve, destiny2:254/499), Kick 0,6 je Strahl E |
| Bahnstufe je Schuss | 0.40 % H | S Cartesian Coordinate Laden 500 ms, Magazin 7 (Menü, Motiongen destiny2:254), gemessen 0,517 s (destiny2:499); Salve 5–6 Strahlen in 0,25 s → 6 Schuss im Abstand 0,05 s (1200/min); Takt gehalten 60/min E (Aufladen 0,5 + Salve 0,25 + Pause); Feuerart aus der Spec (Aufladen → Salve); Leuchten fällt in 0,3 s (Modul charge_fire: 9 Bilder); Bahnstufe 0,004 je Strahl E (Waffe ruhig, Mündung steigt über die Salve, destiny2:254/499), Kick 0,6 je Strahl E |
| Haltung `hip` | Socket_Hand [-0.17, -0.42, -0.215], Ziel [0.1, -3.0, -0.25], Rollen 6° | M Destiny-Fusion Hüfte: Mündung 59/68 (Motiongen huefte:57), 58/66 (destiny2:499); Lage E, gerechnet Mündung 59,0/67,3 % (Automatik-Hüfte an der kurzen Fusion: 61,4/68,0), 2 cm weiter zur Mitte, 1,5 cm höher |
| Haltung `sprint` | Socket_Hand [-0.2, -0.38, -0.21], Ziel [0.5, -2.4, -0.6], Rollen -25° | O cubeescape-reference destiny2 › Glidepath (Sprint): Fusion „groß und tief, Körper ≈ 55–100 % × 62–100 %“ (Sichtung). Lage E, gerechnet Mündung 58/79 %, Visier 91/68 %, Heck rechts aus dem Bild; bis 0.33 die Automatik-Form (Mündung 34/89 %, Körper zu weit links) |
| Haltung `crouch` | Socket_Hand [-0.16, -0.41, -0.23], Rollen 9° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `air` | Socket_Hand [-0.17, -0.42, -0.2], Rollen 4° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `lowered` | Socket_Hand [-0.15, -0.38, -0.235], Rollen 10° | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| Dauer `aim_in` | 7 Bilder bei 30/s (0.233 s) | M Destiny-Fusion ADS 0,083 s Achse, 0,117 s ruhig (Motiongen destiny2:499) = 7 Bilder bei 60/s → wie die MP 3 Bilder bei 30/s; ADS aus nicht gemessen → E 2,4 (Verhältnis der MP) – bis 0.33.1; Nutzerentscheid 31.10.2026: Gapfill bis Ruhe Jötunn / Gravitic Arrest / Midha / Deliverance ein 18–19 / 17 / 17 / 15 ≈ 17 → aim_in 7, aus 16–17 / 18 / 19 / 17 ≈ 17,5 → aim_out 8; Ziehen erstes Modellbild → ruhig Jötunn 48, Gravitic Arrest 44, Midha 49, Deliverance 40 (Motiongen destiny2 › Gapfill) ≈ 45 → 23; Nachladen Batterie bis Hüfte 1,72–1,77 s, ruhig 1,92, sitzt +1,0 s (nachladen:54) × TIME_SCALE = 65 Bilder bis Hüfte → Bezugsablauf (Hüfte bei 45/50) auf 73 Bilder gestreckt |
| Dauer `aim_out` | 8 Bilder bei 30/s (0.267 s) | M Destiny-Fusion ADS 0,083 s Achse, 0,117 s ruhig (Motiongen destiny2:499) = 7 Bilder bei 60/s → wie die MP 3 Bilder bei 30/s; ADS aus nicht gemessen → E 2,4 (Verhältnis der MP) – bis 0.33.1; Nutzerentscheid 31.10.2026: Gapfill bis Ruhe Jötunn / Gravitic Arrest / Midha / Deliverance ein 18–19 / 17 / 17 / 15 ≈ 17 → aim_in 7, aus 16–17 / 18 / 19 / 17 ≈ 17,5 → aim_out 8; Ziehen erstes Modellbild → ruhig Jötunn 48, Gravitic Arrest 44, Midha 49, Deliverance 40 (Motiongen destiny2 › Gapfill) ≈ 45 → 23; Nachladen Batterie bis Hüfte 1,72–1,77 s, ruhig 1,92, sitzt +1,0 s (nachladen:54) × TIME_SCALE = 65 Bilder bis Hüfte → Bezugsablauf (Hüfte bei 45/50) auf 73 Bilder gestreckt |
| Dauer `draw` | 23 Bilder bei 30/s (0.767 s) | M Destiny-Fusion ADS 0,083 s Achse, 0,117 s ruhig (Motiongen destiny2:499) = 7 Bilder bei 60/s → wie die MP 3 Bilder bei 30/s; ADS aus nicht gemessen → E 2,4 (Verhältnis der MP) – bis 0.33.1; Nutzerentscheid 31.10.2026: Gapfill bis Ruhe Jötunn / Gravitic Arrest / Midha / Deliverance ein 18–19 / 17 / 17 / 15 ≈ 17 → aim_in 7, aus 16–17 / 18 / 19 / 17 ≈ 17,5 → aim_out 8; Ziehen erstes Modellbild → ruhig Jötunn 48, Gravitic Arrest 44, Midha 49, Deliverance 40 (Motiongen destiny2 › Gapfill) ≈ 45 → 23; Nachladen Batterie bis Hüfte 1,72–1,77 s, ruhig 1,92, sitzt +1,0 s (nachladen:54) × TIME_SCALE = 65 Bilder bis Hüfte → Bezugsablauf (Hüfte bei 45/50) auf 73 Bilder gestreckt |
| Dauer `reload_tactical` | 73 Bilder bei 30/s (2.433 s) | M Destiny-Fusion ADS 0,083 s Achse, 0,117 s ruhig (Motiongen destiny2:499) = 7 Bilder bei 60/s → wie die MP 3 Bilder bei 30/s; ADS aus nicht gemessen → E 2,4 (Verhältnis der MP) – bis 0.33.1; Nutzerentscheid 31.10.2026: Gapfill bis Ruhe Jötunn / Gravitic Arrest / Midha / Deliverance ein 18–19 / 17 / 17 / 15 ≈ 17 → aim_in 7, aus 16–17 / 18 / 19 / 17 ≈ 17,5 → aim_out 8; Ziehen erstes Modellbild → ruhig Jötunn 48, Gravitic Arrest 44, Midha 49, Deliverance 40 (Motiongen destiny2 › Gapfill) ≈ 45 → 23; Nachladen Batterie bis Hüfte 1,72–1,77 s, ruhig 1,92, sitzt +1,0 s (nachladen:54) × TIME_SCALE = 65 Bilder bis Hüfte → Bezugsablauf (Hüfte bei 45/50) auf 73 Bilder gestreckt |
| Mündungsfeuer | 33 ms | M Destiny: 1–2 Bilder bei 60/s, Kern klein, Seitenflammen breiter, Zielen Automatik ≈ 20 % der Öffnung (Motiongen muendung › 6, Entscheidungsliste 5.3 A); Maße und Farben E (Stil v2.1) |
| Hülsen | keine | Waffe ohne Feld EJECT |
| Rückstoß | ego.RECOIL (gemeinsam) | übertragen von der Automatik: Säule 1 % H je Schuss, im Zielen wandert die Welt (5.1 A / 5.2 A); Werkzeug: Modellkick der Aktion (fire_a/fire_b kick 0,6), keine Bahnstufe (E; Portal 2: obere Klaue ≈ 7 % H im ersten Schussbild) |
| Wirkung | Bolzen 110 m/s, 2.5 m | M Auslöseblitz ≈ 0,07 s; Destiny-Bolzen im Bild nicht sichtbar, [S] 5–9 je Salve (REF 0.36 z-im-tadel) – sichtbare Bolzen bleiben (Nutzerwunsch 0.33, offen); E: je Strahl der Salve ein Bolzen 110 m/s, 2,5 m lang (ego.PAYLOAD, Entscheidungsliste Block 9) |
| Sprint-Frequenz | 3,16 / 1,58 Hz (gemeinsam) | M Destiny Automatik/Handfeuerwaffe, für alle Klassen bis zu neuen Messungen (3c) |
| Griffe | grip, support, mag, charge | Modul-Feld EGO_GRIPS |
| Live-Teile | trigger = trigger, bolt = , port = , glow = ember_core + sight_emitter | Modul-Feld EGO_LIVE |

### Haltungen

| Haltung | Socket_Hand (m) | Handgelenk max | Herkunft |
|---|---|---|---|
| `hip` | [-0.17, -0.42, -0.215] | nur in Aktionen geprüft | M Destiny-Fusion Hüfte: Mündung 59/68 (Motiongen huefte:57), 58/66 (destiny2:499); Lage E, gerechnet Mündung 59,0/67,3 % (Automatik-Hüfte an der kurzen Fusion: 61,4/68,0), 2 cm weiter zur Mitte, 1,5 cm höher |
| `ads` | [0.0, 0.0, 0.0] | nur in Aktionen geprüft | Visier-Standard v2: Socket_Eye ist der Augenpunkt, liegt in der Kamera; Waffenmodell ungezoomt, Welt zoomt je Klasse |
| `sprint` | [-0.2, -0.38, -0.21] | nur in Aktionen geprüft | O cubeescape-reference destiny2 › Glidepath (Sprint): Fusion „groß und tief, Körper ≈ 55–100 % × 62–100 %“ (Sichtung). Lage E, gerechnet Mündung 58/79 %, Visier 91/68 %, Heck rechts aus dem Bild; bis 0.33 die Automatik-Form (Mündung 34/89 %, Körper zu weit links) |
| `lowered` | [-0.15, -0.38, -0.235] | nur in Aktionen geprüft | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| `crouch` | [-0.16, -0.41, -0.23] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `air` | [-0.17, -0.42, -0.2] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `holstered` | [-0.24, -0.25, -0.62] | nur in Aktionen geprüft | E (unter dem Bild) |
| `reload` | [-0.07, -0.34, -0.135] | nur in Aktionen geprüft | T Reload roll −20/pitch 12, für Destiny-Anmutung verstärkt (E) |
| `inspect_l` | [-0.06, -0.36, -0.16] | nur in Aktionen geprüft | E (Ego-Seite zeigt zur Kamera) |
| `inspect_r` | [-0.1, -0.36, -0.12] | nur in Aktionen geprüft | E (Oberseite und rechte Seite) |

### Aktionen

| Aktion | Beschreibung | Bilder | Marker (Bild) | Handgelenk max | Clip | Sichtung | Herkunft |
|---|---|---|---|---|---|---|---|
| `idle_hip` | Ruhe an der Hüfte (Atmen) | 75 (2.50 s) | – | offen° | offen | offen | E |
| `draw` | Ziehen | 23 (0.77 s) | Ready (17) | offen° | offen | offen | M Ziehen 0,23 s bis Hüfte (Auto Rifle, Q-REF) + Ausfedern E; Klasse fusion_rifle: 25 → 23 Bilder (M Destiny-Fusion ADS 0,083 s Achse, 0,117 s ruhig (Motiongen destiny2:499) = 7 Bilder bei 60/s → wie die MP 3 Bilder bei 30/s; ADS aus nicht gemessen → E 2,4 (Verhältnis der MP) – bis 0.33.1; Nutzerentscheid 31.10.2026: Gapfill bis Ruhe Jötunn / Gravitic Arrest / Midha / Deliverance ein 18–19 / 17 / 17 / 15 ≈ 17 → aim_in 7, aus 16–17 / 18 / 19 / 17 ≈ 17,5 → aim_out 8; Ziehen erstes Modellbild → ruhig Jötunn 48, Gravitic Arrest 44, Midha 49, Deliverance 40 (Motiongen destiny2 › Gapfill) ≈ 45 → 23; Nachladen Batterie bis Hüfte 1,72–1,77 s, ruhig 1,92, sitzt +1,0 s (nachladen:54) × TIME_SCALE = 65 Bilder bis Hüfte → Bezugsablauf (Hüfte bei 45/50) auf 73 Bilder gestreckt) |
| `holster` | Wegstecken | 8 (0.27 s) | HandOff (1), Holstered (8) | offen° | offen | offen | M Destiny-Wechsel: Wegstecken 0,08–0,27 s (Motiongen wechsel › 4, Entscheidungsliste 6.1 A) → 0,27 s ohne TIME_SCALE (bis 0.14: 0,60 s); Ablauf E (CE: Holster ab aktueller Stellung) |
| `aim_in` | Hüfte → Zielen | 7 (0.23 s) | Aimed (6) | offen° | offen | offen | E 0,30 s (CE-Handling Auto 0,39→0,20 s); Klasse fusion_rifle: 10 → 7 Bilder (M Destiny-Fusion ADS 0,083 s Achse, 0,117 s ruhig (Motiongen destiny2:499) = 7 Bilder bei 60/s → wie die MP 3 Bilder bei 30/s; ADS aus nicht gemessen → E 2,4 (Verhältnis der MP) – bis 0.33.1; Nutzerentscheid 31.10.2026: Gapfill bis Ruhe Jötunn / Gravitic Arrest / Midha / Deliverance ein 18–19 / 17 / 17 / 15 ≈ 17 → aim_in 7, aus 16–17 / 18 / 19 / 17 ≈ 17,5 → aim_out 8; Ziehen erstes Modellbild → ruhig Jötunn 48, Gravitic Arrest 44, Midha 49, Deliverance 40 (Motiongen destiny2 › Gapfill) ≈ 45 → 23; Nachladen Batterie bis Hüfte 1,72–1,77 s, ruhig 1,92, sitzt +1,0 s (nachladen:54) × TIME_SCALE = 65 Bilder bis Hüfte → Bezugsablauf (Hüfte bei 45/50) auf 73 Bilder gestreckt) |
| `aim_out` | Zielen → Hüfte | 8 (0.27 s) | Ready (8) | offen° | offen | offen | E; Klasse fusion_rifle: 8 → 8 Bilder (M Destiny-Fusion ADS 0,083 s Achse, 0,117 s ruhig (Motiongen destiny2:499) = 7 Bilder bei 60/s → wie die MP 3 Bilder bei 30/s; ADS aus nicht gemessen → E 2,4 (Verhältnis der MP) – bis 0.33.1; Nutzerentscheid 31.10.2026: Gapfill bis Ruhe Jötunn / Gravitic Arrest / Midha / Deliverance ein 18–19 / 17 / 17 / 15 ≈ 17 → aim_in 7, aus 16–17 / 18 / 19 / 17 ≈ 17,5 → aim_out 8; Ziehen erstes Modellbild → ruhig Jötunn 48, Gravitic Arrest 44, Midha 49, Deliverance 40 (Motiongen destiny2 › Gapfill) ≈ 45 → 23; Nachladen Batterie bis Hüfte 1,72–1,77 s, ruhig 1,92, sitzt +1,0 s (nachladen:54) × TIME_SCALE = 65 Bilder bis Hüfte → Bezugsablauf (Hüfte bei 45/50) auf 73 Bilder gestreckt) |
| `fire_hip` | Aufladen und Salve aus der Hüfte | 32 (1.07 s) | Fire (2) | offen° | ego_BASIC-10-v2.1_fire_hip.mp4 | offen | M 720/min = 1 Schuss je 2,5 Bilder (Q-REF; bis 0.14 alle 2 Bilder ≈ 940/min); Rückstoß T 17,5 mm/3°; Klasse fusion_rifle: 60/min, Aufladen → Salve (Abzug halten lädt in charge_s, bei voller Ladung burst_shots Schuss; Loslassen bricht ab; gehalten Zyklus um Zyklus im Takt rpm) (Schussbilder [17, 18, 20, 21, 23, 24]) |
| `fire_ads` | Aufladen und Salve im Zielen | 32 (1.07 s) | AimFire (2) | offen° | offen | offen | M Kadenz wie fire_hip; Rückstoß im Zielen nach RECOIL ads_* (5.1 A: Visier steht, die Welt wandert) E; Klasse fusion_rifle: 60/min, Aufladen → Salve (Abzug halten lädt in charge_s, bei voller Ladung burst_shots Schuss; Loslassen bricht ab; gehalten Zyklus um Zyklus im Takt rpm) (Schussbilder [17, 18, 20, 21, 23, 24]) |
| `reload_tactical` | Nachladen mit Restmunition | 73 (2.43 s) | HandOff (6), MagOut (14), MagIn (42), HandOn (56), Ready (67) | offen° | offen | offen | M MagIn ≈ 0,93 s; Ablauf T (Reload-Keys) mit Destiny-Kippen E; v2: Ausholen, Stoß bei MagIn, Nachfedern E; Klasse fusion_rifle: 63 → 73 Bilder (M Destiny-Fusion ADS 0,083 s Achse, 0,117 s ruhig (Motiongen destiny2:499) = 7 Bilder bei 60/s → wie die MP 3 Bilder bei 30/s; ADS aus nicht gemessen → E 2,4 (Verhältnis der MP) – bis 0.33.1; Nutzerentscheid 31.10.2026: Gapfill bis Ruhe Jötunn / Gravitic Arrest / Midha / Deliverance ein 18–19 / 17 / 17 / 15 ≈ 17 → aim_in 7, aus 16–17 / 18 / 19 / 17 ≈ 17,5 → aim_out 8; Ziehen erstes Modellbild → ruhig Jötunn 48, Gravitic Arrest 44, Midha 49, Deliverance 40 (Motiongen destiny2 › Gapfill) ≈ 45 → 23; Nachladen Batterie bis Hüfte 1,72–1,77 s, ruhig 1,92, sitzt +1,0 s (nachladen:54) × TIME_SCALE = 65 Bilder bis Hüfte → Bezugsablauf (Hüfte bei 45/50) auf 73 Bilder gestreckt) |
| `reload_empty` | Nachladen mit Restmunition, auch leer | 73 (2.43 s) | HandOff (6), MagOut (14), MagIn (42), HandOn (56), Ready (67) | offen° | offen | offen | M MagIn ≈ 0,93 s; Ablauf T (Reload-Keys) mit Destiny-Kippen E; v2: Ausholen, Stoß bei MagIn, Nachfedern E; Klasse fusion_rifle: 63 → 73 Bilder (M Destiny-Fusion ADS 0,083 s Achse, 0,117 s ruhig (Motiongen destiny2:499) = 7 Bilder bei 60/s → wie die MP 3 Bilder bei 30/s; ADS aus nicht gemessen → E 2,4 (Verhältnis der MP) – bis 0.33.1; Nutzerentscheid 31.10.2026: Gapfill bis Ruhe Jötunn / Gravitic Arrest / Midha / Deliverance ein 18–19 / 17 / 17 / 15 ≈ 17 → aim_in 7, aus 16–17 / 18 / 19 / 17 ≈ 17,5 → aim_out 8; Ziehen erstes Modellbild → ruhig Jötunn 48, Gravitic Arrest 44, Midha 49, Deliverance 40 (Motiongen destiny2 › Gapfill) ≈ 45 → 23; Nachladen Batterie bis Hüfte 1,72–1,77 s, ruhig 1,92, sitzt +1,0 s (nachladen:54) × TIME_SCALE = 65 Bilder bis Hüfte → Bezugsablauf (Hüfte bei 45/50) auf 73 Bilder gestreckt) |
| `inspect` | Betrachten | 120 (4.00 s) | Start (20), End (118) | offen° | offen | offen | E nach Apex/CoD-Muster (Ego-Seite, dann Oberseite); Destiny hat keinen Ego-Inspect |
| `sprint` | Sprint: Beginn, Schleife, Ende | 60 (2.00 s) | SprintLoop (10), Ready (60) | offen° | offen | offen | E (CE: Waffe senkt sich und rollt zur Mitte); period = Doppelschritt (seitlich), vertikal je Schritt: 19 Bilder = 0,633 s → 3,16 Schritte/s, seitlich 1,58 Hz, Rollen ±3,5°, U-Bogen (oben an den Seitenumkehren) nach Motiongen REF 0.23 (Destiny 2, Automatik/Handfeuerwaffe gemessen). 0.9: 10 Bilder = 6 Schritte/s („tapsig“). 0.15: Hub 12/10 → 22/18 mm (seitlich/vertikal) für ≈ 10 % H / 13 % B im Bild wie die Destiny-Automatik (Entscheidungsliste 3.1 A, gemessen wie in Schritt 2: Oberkante, linke Kante) |
| `lowered` | Gesenkte Haltung / Wandnähe | 45 (1.50 s) | Lowered (10), Ready (45) | offen° | offen | offen | E |
| `walk` | Gehen (liegende Acht) | 60 (2.00 s) | – | offen° | offen | offen | E (CE: liegende Acht) |
| `crouch` | Ducken | 30 (1.00 s) | Crouched (10) | offen° | offen | offen | E |
| `jump_land` | Sprung, Luftphase, Landung | 50 (1.67 s) | Air (10), Land (35) | offen° | offen | offen | E (CE: Anheben, Landefeder) |
| `sprint_to_aim` | Sprint → Zielen | 18 (0.60 s) | SprintOut (0), Aimed (12) | offen° | offen | offen | E (CE: ADS > Sprint) |
| `sprint_to_fire` | Sprint → Feuer | 26 (0.87 s) | SprintOut (0), Fire (7) | offen° | offen | offen | E (CE: Fire > Sprint); Klasse fusion_rifle: 60/min, Aufladen → Salve (Abzug halten lädt in charge_s, bei voller Ladung burst_shots Schuss; Loslassen bricht ab; gehalten Zyklus um Zyklus im Takt rpm) (Schussbilder [22, 23, 25]) |
| `draw_aim` | Ziehen bei gehaltenem Zielen | 35 (1.17 s) | Ready (18), Aimed (30) | offen° | offen | offen | E (CE: Draw nicht unterbrechbar, ADS danach) |
| `reload_to_switch` | Nachladen → Waffenwechsel (Abbruch) | 38 (1.27 s) | HandOff (5), Cancel (18), Holstered (35) | offen° | offen | offen | E (CE: Reload bricht bei Wechsel ab, Holster ab aktueller Stellung) |

### Abdeckung der Matrixzeilen

| Zeile | durch Aktion | Status |
|---|---|---|
| `pose_rest` | `idle_hip` | offen (nicht gesichtet) |
| `pose_hip` | `idle_hip` | offen (nicht gesichtet) |
| `draw` | `draw` | offen (nicht gesichtet) |
| `ready` | `draw` | offen (nicht gesichtet) |
| `holster` | `holster` | offen (nicht gesichtet) |
| `pose_aim` | `aim_in` | offen (nicht gesichtet) |
| `tr_hip_aim` | `aim_in` | offen (nicht gesichtet) |
| `tr_aim_hip` | `aim_out` | offen (nicht gesichtet) |
| `fire_auto` | `fire_ads` | offen (nicht gesichtet) |
| `recoil_mech` | `fire_hip` | offen (nicht gesichtet) |
| `recoil_camera` | `fire_hip` | offen (nicht gesichtet) |
| `reload_partial` | `reload_tactical` | offen (nicht gesichtet) |
| `reload_feed` | `reload_tactical` | offen (nicht gesichtet) |
| `reload_empty` | `reload_empty` | offen (nicht gesichtet) |
| `cycle` | `reload_empty` | offen (nicht gesichtet) |
| `inspect` | `inspect` | offen (nicht gesichtet) |
| `inspect_return` | `inspect` | offen (nicht gesichtet) |
| `sprint_in` | `sprint` | offen (nicht gesichtet) |
| `sprint_loop` | `sprint` | offen (nicht gesichtet) |
| `sprint_out` | `sprint` | offen (nicht gesichtet) |
| `pose_lowered` | `lowered` | offen (nicht gesichtet) |
| `tr_lowered_return` | `lowered` | offen (nicht gesichtet) |
| `move_walk` | `walk` | offen (nicht gesichtet) |
| `sway` | `walk` | offen (nicht gesichtet) |
| `crouch` | `crouch` | offen (nicht gesichtet) |
| `jump_start` | `jump_land` | offen (nicht gesichtet) |
| `air` | `jump_land` | offen (nicht gesichtet) |
| `land` | `jump_land` | offen (nicht gesichtet) |
| `tr_sprint_aim` | `sprint_to_aim` | offen (nicht gesichtet) |
| `tr_sprint_fire` | `sprint_to_fire` | offen (nicht gesichtet) |
| `tr_draw_aimheld` | `draw_aim` | offen (nicht gesichtet) |
| `tr_reload_switch` | `reload_to_switch` | offen (nicht gesichtet) |
| `switch` | `reload_to_switch` | offen (nicht gesichtet) |

## BASIC-11-v2.1 – Schienenlicht v2.1 (linear_fusion_rifle)

### Klassen- und Spielwerte

| Wert | Stand | Herkunft |
|---|---|---|
| Klasse | linear_fusion_rifle | Ego-Übertrag 0.33 „Armory“ P3: Hüfte, Anflug, Ziehen, Aufladen und Nachladen nach Motiongen (lineare Fusion), Sprint der Automatik, Nachladen der Bezugsklasse mit der Energiezelle |
| Kadenz | 60/min | S Laden 563 ms, Magazin 5 (Menü, Motiongen destiny2:274), sichtbar 20 Bilder bei 60/s [M]; Takt gehalten 60/min E; Feuerart aus der Spec (Aufladen → Einzelschuss); Leuchten fällt in 0,2 s (Modul charge_fire: 6 Bilder); Bahnstufe 0,065 M: 6,5 pp H je Schuss (rueckstoss:111), Erholung langsam wie der Scharfschütze E; Kick 3,0 E |
| Magazin | 5 | S Laden 563 ms, Magazin 5 (Menü, Motiongen destiny2:274), sichtbar 20 Bilder bei 60/s [M]; Takt gehalten 60/min E; Feuerart aus der Spec (Aufladen → Einzelschuss); Leuchten fällt in 0,2 s (Modul charge_fire: 6 Bilder); Bahnstufe 0,065 M: 6,5 pp H je Schuss (rueckstoss:111), Erholung langsam wie der Scharfschütze E; Kick 3,0 E |
| Feuerart | `charge_single` – Aufladen → Einzelschuss (wie charge_burst mit einem Schuss) | Spec (META fire, data/specs); Unity: gameplay.fire_mode (0.20) |
| Weltzoom im Zielen | 3 | M Glidepath (Entscheidungsliste 1.2 A, basic/reticles.py › CLASS_ZOOM) |
| Hüft-Fadenkreuz | ring_corners 12.5 % H | gemessen (Glidepath, 12–13 % H) (4.1 A / 4.2 A, basic/reticles.py › HUD_HIP) |
| Sprint-Fadenkreuz | aus | basic/reticles.py › HIP.sprint (4.1 A) |
| Absehen im Glas | cross 4.5 % H | basic/reticles.py › HIP (common.drawn_reticle, Teil des Modells); Unity: gameplay.sight_form |
| Bahnstufe je Schuss | 6.50 % H | S Laden 563 ms, Magazin 5 (Menü, Motiongen destiny2:274), sichtbar 20 Bilder bei 60/s [M]; Takt gehalten 60/min E; Feuerart aus der Spec (Aufladen → Einzelschuss); Leuchten fällt in 0,2 s (Modul charge_fire: 6 Bilder); Bahnstufe 0,065 M: 6,5 pp H je Schuss (rueckstoss:111), Erholung langsam wie der Scharfschütze E; Kick 3,0 E |
| Haltung `hip` | Socket_Hand [-0.151, -0.417, -0.191], Ziel [-0.132, -3.397, -0.536], Rollen 4.2° | M cubeescape-reference huefte.json (Destiny 2, Mündung 58/69, 58/68, Visier 73/57, 73/60); Lage E: Ausgleichsrechnung gegen diese Werte (0.33, Abgleich aller Waffen; Nutzer 31.10.2026 „Ja, nachziehen“ – bis dahin nur die Mündung eingestellt, das Visier lag 10–19 pp zu tief), gerechnet (Socket_Muzzle, Socket_Sight bzw. Socket_Reticle, Socket_Hand) Mündung 57,9/68,5 %, Visier 73,0/58,8 % |
| Haltung `sprint` | Socket_Hand [-0.1, -0.34, -0.23], Ziel [1.2, -1.6, -0.55], Rollen -35° | E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-lineare-Fusion-Sprint nicht gemessen (Motiongen destiny2:569) (Haltung POSES['sprint'] unverändert) |
| Haltung `crouch` | Socket_Hand [-0.141, -0.407, -0.206], Rollen 7.199999999999999° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `air` | Socket_Hand [-0.151, -0.417, -0.176], Rollen 2.1999999999999993° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `lowered` | Socket_Hand [-0.131, -0.377, -0.211], Rollen 8.2° | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| Dauer `aim_in` | 7 Bilder bei 30/s (0.233 s) | M Destiny-lineare-Fusion ADS ein 17 Bilder bei 60/s (Motiongen destiny2:591) → 7 Bilder bei 30/s wie der Scout; ADS aus 0,32 s (destiny2:274) → 10; Ziehen 24 + 23 Bilder bei 60/s bis ruhig (wechsel:57) = 0,78 s → 24; Nachladen MagIn +1,53 s, ruhig 3,30 s (nachladen:61): Bezugsablauf so gestreckt, dass MagIn trifft (1,53 × 1,25 → Bild 57 von 99); ruhig damit nach 2,4 statt 3,3 s (Entscheidungsliste) |
| Dauer `aim_out` | 10 Bilder bei 30/s (0.333 s) | M Destiny-lineare-Fusion ADS ein 17 Bilder bei 60/s (Motiongen destiny2:591) → 7 Bilder bei 30/s wie der Scout; ADS aus 0,32 s (destiny2:274) → 10; Ziehen 24 + 23 Bilder bei 60/s bis ruhig (wechsel:57) = 0,78 s → 24; Nachladen MagIn +1,53 s, ruhig 3,30 s (nachladen:61): Bezugsablauf so gestreckt, dass MagIn trifft (1,53 × 1,25 → Bild 57 von 99); ruhig damit nach 2,4 statt 3,3 s (Entscheidungsliste) |
| Dauer `draw` | 24 Bilder bei 30/s (0.800 s) | M Destiny-lineare-Fusion ADS ein 17 Bilder bei 60/s (Motiongen destiny2:591) → 7 Bilder bei 30/s wie der Scout; ADS aus 0,32 s (destiny2:274) → 10; Ziehen 24 + 23 Bilder bei 60/s bis ruhig (wechsel:57) = 0,78 s → 24; Nachladen MagIn +1,53 s, ruhig 3,30 s (nachladen:61): Bezugsablauf so gestreckt, dass MagIn trifft (1,53 × 1,25 → Bild 57 von 99); ruhig damit nach 2,4 statt 3,3 s (Entscheidungsliste) |
| Dauer `reload_tactical` | 99 Bilder bei 30/s (3.300 s) | M Destiny-lineare-Fusion ADS ein 17 Bilder bei 60/s (Motiongen destiny2:591) → 7 Bilder bei 30/s wie der Scout; ADS aus 0,32 s (destiny2:274) → 10; Ziehen 24 + 23 Bilder bei 60/s bis ruhig (wechsel:57) = 0,78 s → 24; Nachladen MagIn +1,53 s, ruhig 3,30 s (nachladen:61): Bezugsablauf so gestreckt, dass MagIn trifft (1,53 × 1,25 → Bild 57 von 99); ruhig damit nach 2,4 statt 3,3 s (Entscheidungsliste) |
| Zielfernrohr im Zielen | aus: scope_strap, scope_tube, scope_eyepiece, scope_eye_trim, scope_ocular_glass, scope_turret, scope_turret_w (Socket_Eye < 60 mm) | E: Okular bis an die Nahebene sichtbar (Augenabstand Okularende 30 mm + near 30 mm), danach Linsenbild; Destiny-Scharfschütze: Okular füllt das Bild 4 Bilder, Linse nach dem Modell (Motiongen destiny2 › 2, Entscheidungsliste 1d) |
| Mündungsfeuer | 33 ms | M Destiny: 1–2 Bilder bei 60/s, Kern klein, Seitenflammen breiter, Zielen Automatik ≈ 20 % der Öffnung (Motiongen muendung › 6, Entscheidungsliste 5.3 A); Maße und Farben E (Stil v2.1) |
| Hülsen | keine | Waffe ohne Feld EJECT |
| Rückstoß | ego.RECOIL (gemeinsam) | übertragen von der Automatik: Säule 1 % H je Schuss, im Zielen wandert die Welt (5.1 A / 5.2 A); Werkzeug: Modellkick der Aktion (fire_a/fire_b kick 0,6), keine Bahnstufe (E; Portal 2: obere Klaue ≈ 7 % H im ersten Schussbild) |
| Wirkung | Strahl 3.5 cm, 0.07 s | M Schleier am Lauf 4 Bilder ≈ 0,07 s, kein fester Strahl (REF 0.36 z-im-threaded-needle) – hier ein Strahl für 0,07 s (Nutzerwunsch 0.33); Breite E (ego.PAYLOAD, Entscheidungsliste Block 9) |
| Sprint-Frequenz | 3,16 / 1,58 Hz (gemeinsam) | M Destiny Automatik/Handfeuerwaffe, für alle Klassen bis zu neuen Messungen (3c) |
| Griffe | grip, support, mag, charge | Modul-Feld EGO_GRIPS |
| Live-Teile | trigger = trigger, bolt = , port = , glow = linear_core | Modul-Feld EGO_LIVE |

### Haltungen

| Haltung | Socket_Hand (m) | Handgelenk max | Herkunft |
|---|---|---|---|
| `hip` | [-0.151, -0.417, -0.191] | nur in Aktionen geprüft | M cubeescape-reference huefte.json (Destiny 2, Mündung 58/69, 58/68, Visier 73/57, 73/60); Lage E: Ausgleichsrechnung gegen diese Werte (0.33, Abgleich aller Waffen; Nutzer 31.10.2026 „Ja, nachziehen“ – bis dahin nur die Mündung eingestellt, das Visier lag 10–19 pp zu tief), gerechnet (Socket_Muzzle, Socket_Sight bzw. Socket_Reticle, Socket_Hand) Mündung 57,9/68,5 %, Visier 73,0/58,8 % |
| `ads` | [0.0, 0.0, 0.0] | nur in Aktionen geprüft | Visier-Standard v2: Socket_Eye ist der Augenpunkt, liegt in der Kamera; Waffenmodell ungezoomt, Welt zoomt je Klasse |
| `sprint` | [-0.1, -0.34, -0.23] | nur in Aktionen geprüft | E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-lineare-Fusion-Sprint nicht gemessen (Motiongen destiny2:569) (Haltung POSES['sprint'] unverändert) |
| `lowered` | [-0.131, -0.377, -0.211] | nur in Aktionen geprüft | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| `crouch` | [-0.141, -0.407, -0.206] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `air` | [-0.151, -0.417, -0.176] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `holstered` | [-0.24, -0.25, -0.62] | nur in Aktionen geprüft | E (unter dem Bild) |
| `reload` | [-0.07, -0.34, -0.135] | nur in Aktionen geprüft | T Reload roll −20/pitch 12, für Destiny-Anmutung verstärkt (E) |
| `inspect_l` | [-0.06, -0.36, -0.16] | nur in Aktionen geprüft | E (Ego-Seite zeigt zur Kamera) |
| `inspect_r` | [-0.1, -0.36, -0.12] | nur in Aktionen geprüft | E (Oberseite und rechte Seite) |

### Aktionen

| Aktion | Beschreibung | Bilder | Marker (Bild) | Handgelenk max | Clip | Sichtung | Herkunft |
|---|---|---|---|---|---|---|---|
| `idle_hip` | Ruhe an der Hüfte (Atmen) | 75 (2.50 s) | – | offen° | offen | offen | E |
| `draw` | Ziehen | 24 (0.80 s) | Ready (17) | offen° | offen | offen | M Ziehen 0,23 s bis Hüfte (Auto Rifle, Q-REF) + Ausfedern E; Klasse linear_fusion_rifle: 25 → 24 Bilder (M Destiny-lineare-Fusion ADS ein 17 Bilder bei 60/s (Motiongen destiny2:591) → 7 Bilder bei 30/s wie der Scout; ADS aus 0,32 s (destiny2:274) → 10; Ziehen 24 + 23 Bilder bei 60/s bis ruhig (wechsel:57) = 0,78 s → 24; Nachladen MagIn +1,53 s, ruhig 3,30 s (nachladen:61): Bezugsablauf so gestreckt, dass MagIn trifft (1,53 × 1,25 → Bild 57 von 99); ruhig damit nach 2,4 statt 3,3 s (Entscheidungsliste)) |
| `holster` | Wegstecken | 8 (0.27 s) | HandOff (1), Holstered (8) | offen° | offen | offen | M Destiny-Wechsel: Wegstecken 0,08–0,27 s (Motiongen wechsel › 4, Entscheidungsliste 6.1 A) → 0,27 s ohne TIME_SCALE (bis 0.14: 0,60 s); Ablauf E (CE: Holster ab aktueller Stellung) |
| `aim_in` | Hüfte → Zielen | 7 (0.23 s) | Aimed (6) | offen° | offen | offen | E 0,30 s (CE-Handling Auto 0,39→0,20 s); Klasse linear_fusion_rifle: 10 → 7 Bilder (M Destiny-lineare-Fusion ADS ein 17 Bilder bei 60/s (Motiongen destiny2:591) → 7 Bilder bei 30/s wie der Scout; ADS aus 0,32 s (destiny2:274) → 10; Ziehen 24 + 23 Bilder bei 60/s bis ruhig (wechsel:57) = 0,78 s → 24; Nachladen MagIn +1,53 s, ruhig 3,30 s (nachladen:61): Bezugsablauf so gestreckt, dass MagIn trifft (1,53 × 1,25 → Bild 57 von 99); ruhig damit nach 2,4 statt 3,3 s (Entscheidungsliste)) |
| `aim_out` | Zielen → Hüfte | 10 (0.33 s) | Ready (10) | offen° | offen | offen | E; Klasse linear_fusion_rifle: 8 → 10 Bilder (M Destiny-lineare-Fusion ADS ein 17 Bilder bei 60/s (Motiongen destiny2:591) → 7 Bilder bei 30/s wie der Scout; ADS aus 0,32 s (destiny2:274) → 10; Ziehen 24 + 23 Bilder bei 60/s bis ruhig (wechsel:57) = 0,78 s → 24; Nachladen MagIn +1,53 s, ruhig 3,30 s (nachladen:61): Bezugsablauf so gestreckt, dass MagIn trifft (1,53 × 1,25 → Bild 57 von 99); ruhig damit nach 2,4 statt 3,3 s (Entscheidungsliste)) |
| `fire_hip` | Aufladen und Schuss aus der Hüfte | 32 (1.07 s) | Fire (2) | offen° | ego_BASIC-11-v2.1_fire_hip.mp4 | offen | M 720/min = 1 Schuss je 2,5 Bilder (Q-REF; bis 0.14 alle 2 Bilder ≈ 940/min); Rückstoß T 17,5 mm/3°; Klasse linear_fusion_rifle: 60/min, Aufladen → Einzelschuss (wie charge_burst mit einem Schuss) (Schussbilder [18]) |
| `fire_ads` | Aufladen und Schuss im Zielen | 32 (1.07 s) | AimFire (2) | offen° | offen | offen | M Kadenz wie fire_hip; Rückstoß im Zielen nach RECOIL ads_* (5.1 A: Visier steht, die Welt wandert) E; Klasse linear_fusion_rifle: 60/min, Aufladen → Einzelschuss (wie charge_burst mit einem Schuss) (Schussbilder [18]) |
| `reload_tactical` | Nachladen mit Restmunition | 99 (3.30 s) | HandOff (8), MagOut (19), MagIn (57), HandOn (75), Ready (91) | offen° | offen | offen | M MagIn ≈ 0,93 s; Ablauf T (Reload-Keys) mit Destiny-Kippen E; v2: Ausholen, Stoß bei MagIn, Nachfedern E; Klasse linear_fusion_rifle: 63 → 99 Bilder (M Destiny-lineare-Fusion ADS ein 17 Bilder bei 60/s (Motiongen destiny2:591) → 7 Bilder bei 30/s wie der Scout; ADS aus 0,32 s (destiny2:274) → 10; Ziehen 24 + 23 Bilder bei 60/s bis ruhig (wechsel:57) = 0,78 s → 24; Nachladen MagIn +1,53 s, ruhig 3,30 s (nachladen:61): Bezugsablauf so gestreckt, dass MagIn trifft (1,53 × 1,25 → Bild 57 von 99); ruhig damit nach 2,4 statt 3,3 s (Entscheidungsliste)) |
| `reload_empty` | Nachladen mit Restmunition, auch leer | 99 (3.30 s) | HandOff (8), MagOut (19), MagIn (57), HandOn (75), Ready (91) | offen° | offen | offen | M MagIn ≈ 0,93 s; Ablauf T (Reload-Keys) mit Destiny-Kippen E; v2: Ausholen, Stoß bei MagIn, Nachfedern E; Klasse linear_fusion_rifle: 63 → 99 Bilder (M Destiny-lineare-Fusion ADS ein 17 Bilder bei 60/s (Motiongen destiny2:591) → 7 Bilder bei 30/s wie der Scout; ADS aus 0,32 s (destiny2:274) → 10; Ziehen 24 + 23 Bilder bei 60/s bis ruhig (wechsel:57) = 0,78 s → 24; Nachladen MagIn +1,53 s, ruhig 3,30 s (nachladen:61): Bezugsablauf so gestreckt, dass MagIn trifft (1,53 × 1,25 → Bild 57 von 99); ruhig damit nach 2,4 statt 3,3 s (Entscheidungsliste)) |
| `inspect` | Betrachten | 120 (4.00 s) | Start (20), End (118) | offen° | offen | offen | E nach Apex/CoD-Muster (Ego-Seite, dann Oberseite); Destiny hat keinen Ego-Inspect |
| `sprint` | Sprint: Beginn, Schleife, Ende | 60 (2.00 s) | SprintLoop (10), Ready (60) | offen° | offen | offen | E (CE: Waffe senkt sich und rollt zur Mitte); period = Doppelschritt (seitlich), vertikal je Schritt: 19 Bilder = 0,633 s → 3,16 Schritte/s, seitlich 1,58 Hz, Rollen ±3,5°, U-Bogen (oben an den Seitenumkehren) nach Motiongen REF 0.23 (Destiny 2, Automatik/Handfeuerwaffe gemessen). 0.9: 10 Bilder = 6 Schritte/s („tapsig“). 0.15: Hub 12/10 → 22/18 mm (seitlich/vertikal) für ≈ 10 % H / 13 % B im Bild wie die Destiny-Automatik (Entscheidungsliste 3.1 A, gemessen wie in Schritt 2: Oberkante, linke Kante) |
| `lowered` | Gesenkte Haltung / Wandnähe | 45 (1.50 s) | Lowered (10), Ready (45) | offen° | offen | offen | E |
| `walk` | Gehen (liegende Acht) | 60 (2.00 s) | – | offen° | offen | offen | E (CE: liegende Acht) |
| `crouch` | Ducken | 30 (1.00 s) | Crouched (10) | offen° | offen | offen | E |
| `jump_land` | Sprung, Luftphase, Landung | 50 (1.67 s) | Air (10), Land (35) | offen° | offen | offen | E (CE: Anheben, Landefeder) |
| `sprint_to_aim` | Sprint → Zielen | 18 (0.60 s) | SprintOut (0), Aimed (12) | offen° | offen | offen | E (CE: ADS > Sprint) |
| `sprint_to_fire` | Sprint → Feuer | 26 (0.87 s) | SprintOut (0), Fire (7) | offen° | offen | offen | E (CE: Fire > Sprint); Klasse linear_fusion_rifle: 60/min, Aufladen → Einzelschuss (wie charge_burst mit einem Schuss) (Schussbilder [23]) |
| `draw_aim` | Ziehen bei gehaltenem Zielen | 35 (1.17 s) | Ready (18), Aimed (30) | offen° | offen | offen | E (CE: Draw nicht unterbrechbar, ADS danach) |
| `reload_to_switch` | Nachladen → Waffenwechsel (Abbruch) | 38 (1.27 s) | HandOff (5), Cancel (18), Holstered (35) | offen° | offen | offen | E (CE: Reload bricht bei Wechsel ab, Holster ab aktueller Stellung) |

### Abdeckung der Matrixzeilen

| Zeile | durch Aktion | Status |
|---|---|---|
| `pose_rest` | `idle_hip` | offen (nicht gesichtet) |
| `pose_hip` | `idle_hip` | offen (nicht gesichtet) |
| `draw` | `draw` | offen (nicht gesichtet) |
| `ready` | `draw` | offen (nicht gesichtet) |
| `holster` | `holster` | offen (nicht gesichtet) |
| `pose_aim` | `aim_in` | offen (nicht gesichtet) |
| `tr_hip_aim` | `aim_in` | offen (nicht gesichtet) |
| `tr_aim_hip` | `aim_out` | offen (nicht gesichtet) |
| `fire_auto` | `fire_ads` | offen (nicht gesichtet) |
| `recoil_mech` | `fire_hip` | offen (nicht gesichtet) |
| `recoil_camera` | `fire_hip` | offen (nicht gesichtet) |
| `reload_partial` | `reload_tactical` | offen (nicht gesichtet) |
| `reload_feed` | `reload_tactical` | offen (nicht gesichtet) |
| `reload_empty` | `reload_empty` | offen (nicht gesichtet) |
| `cycle` | `reload_empty` | offen (nicht gesichtet) |
| `inspect` | `inspect` | offen (nicht gesichtet) |
| `inspect_return` | `inspect` | offen (nicht gesichtet) |
| `sprint_in` | `sprint` | offen (nicht gesichtet) |
| `sprint_loop` | `sprint` | offen (nicht gesichtet) |
| `sprint_out` | `sprint` | offen (nicht gesichtet) |
| `pose_lowered` | `lowered` | offen (nicht gesichtet) |
| `tr_lowered_return` | `lowered` | offen (nicht gesichtet) |
| `move_walk` | `walk` | offen (nicht gesichtet) |
| `sway` | `walk` | offen (nicht gesichtet) |
| `crouch` | `crouch` | offen (nicht gesichtet) |
| `jump_start` | `jump_land` | offen (nicht gesichtet) |
| `air` | `jump_land` | offen (nicht gesichtet) |
| `land` | `jump_land` | offen (nicht gesichtet) |
| `tr_sprint_aim` | `sprint_to_aim` | offen (nicht gesichtet) |
| `tr_sprint_fire` | `sprint_to_fire` | offen (nicht gesichtet) |
| `tr_draw_aimheld` | `draw_aim` | offen (nicht gesichtet) |
| `tr_reload_switch` | `reload_to_switch` | offen (nicht gesichtet) |
| `switch` | `reload_to_switch` | offen (nicht gesichtet) |

## BASIC-07-v2.1 – Sehnenzug v2.1 (combat_bow)

### Klassen- und Spielwerte

| Wert | Stand | Herkunft |
|---|---|---|
| Klasse | combat_bow | Ego-Übertrag 0.33 „Armory“ P4: Hüfte, Spannhaltung, Sprint und Zeiten nach Motiongen (Bogen Imperial Needle), Ablauf E |
| Kadenz | 60/min | Feuerart aus der Spec (draw_release: Spannen, Halten, Lösen); kein Magazin (Vorrat, magazine 0 = unbegrenzt, Motiongen destiny2:270); Takt E 60/min (begrenzt nicht: Lösen, Auflegen und Spannen dauern 1,3 s, Destiny Lösen → Lösen 1,45 s); keine Bahnstufe (die Welt steigt nicht, der Bogen ruckt), Kick 1,5 E (Wurfarme-Ruck, destiny2:498); kein Mündungsfeuer, keine Hülse |
| Magazin | 0 | Feuerart aus der Spec (draw_release: Spannen, Halten, Lösen); kein Magazin (Vorrat, magazine 0 = unbegrenzt, Motiongen destiny2:270); Takt E 60/min (begrenzt nicht: Lösen, Auflegen und Spannen dauern 1,3 s, Destiny Lösen → Lösen 1,45 s); keine Bahnstufe (die Welt steigt nicht, der Bogen ruckt), Kick 1,5 E (Wurfarme-Ruck, destiny2:498); kein Mündungsfeuer, keine Hülse |
| Feuerart | `draw_release` – Bogen (Abzug halten spannt – Klassenaktion fire_draw/fire_draw_ads –, voller Auszug hält, Loslassen löst – fire_release/fire_release_ads –, vorher entspannt der Bogen ohne Schuss – let_down/let_down_ads) | Spec (META fire, data/specs); Unity: gameplay.fire_mode (0.20) |
| Weltzoom im Zielen | 2.2 | M Glidepath (Entscheidungsliste 1.2 A, basic/reticles.py › CLASS_ZOOM) |
| Hüft-Fadenkreuz | arcs_ladder 4.6 % H | gemessen (Glidepath, Ø 4,6 % H) (4.1 A / 4.2 A, basic/reticles.py › HUD_HIP) |
| Sprint-Fadenkreuz | aus | basic/reticles.py › HIP.sprint (4.1 A) |
| Ohne | Aktionen `fire_hip`, `fire_ads`, `reload_tactical`, `reload_empty`, `reload_to_switch`; Haltungen `reload` | Bogen ohne Magazin (Vorrat): kein Nachladen; Feuer als Klassenaktionen fire_draw/fire_release/let_down statt fire_hip/fire_ads |
| Bahnstufe je Schuss | 0.00 % H | Feuerart aus der Spec (draw_release: Spannen, Halten, Lösen); kein Magazin (Vorrat, magazine 0 = unbegrenzt, Motiongen destiny2:270); Takt E 60/min (begrenzt nicht: Lösen, Auflegen und Spannen dauern 1,3 s, Destiny Lösen → Lösen 1,45 s); keine Bahnstufe (die Welt steigt nicht, der Bogen ruckt), Kick 1,5 E (Wurfarme-Ruck, destiny2:498); kein Mündungsfeuer, keine Hülse |
| Haltung `hip` | Socket_Hand [-0.01, -0.61, -0.18], Ziel [-0.01, -3.61, -0.18], Rollen -80° | M cubeescape-reference huefte.json › hl-destiny-2-imperial-needle (Ultraclocked 0:47,000): linke Griffhand 46,6/84,8 %, Visier 57,3/75,2 %, Bogen breit im unteren Bild (Körper 7,6–100 × 68,6–100 %), rechte Hand an der Nocke 49–64 × 91–100 %; destiny2:514 quer gekantet von links unten nach rechts oben, Pfeil zur Mitte. Lage E (Ausgleichsrechnung gegen diese Werte, dann 3 cm nach rechts für die Freihaltezone A4), gerechnet Griff 50/84 %, Nocke 57/93 %, Pfeilspitze 53/67 %, Ring 56/68 %, Wurfarme links unten und rechts oben aus dem Bild |
| Haltung `ads` | Auge [0.0, 0.27, 0.0], Blickrichtung [0, -1, 0], Rollen 0° | M Destiny-Bogen Imperial Needle im Zielen (Bilder aus Ultraclocked dKNTDzi__Qo 47,75/48,3/67,7 s, Cache CubeEscape/reference/visiere; cubeescape-reference destiny2:105 Ring 50/57, zielbewegung: Zoom 2,2×): Blick durch den Ring, der Riser direkt rechts daneben, die Pfeilspitze unter dem Ring, Wurfarme über die volle Bildhöhe, linke Hand unten Mitte; der Ring ist ≈ 9 % B groß. Lage E: der Bogen steht 27 cm näher an der Kamera als der Ankerpunkt des vollen Auszugs (Socket_Eye 23 cm hinter dem Auge, Sehne und Zughand hinter der Kamera; Nutzer 30.10.2026: „beim Bogen ist das Visier näher am Bild“; mit 23 cm ≈ 6 % B im Bildvergleich), gerechnet Ring 50/50 % mit Ø 52 mm in 0,41 m ≈ 9,8 % B |
| Haltung `drawn` | Socket_Hand [0.0, -0.49, -0.16], Ziel [-0.776, -3.388, 0.101], Rollen -65° | M Destiny-Bogen Imperial Needle gespannt aus der Hüfte (Bild Ultraclocked dKNTDzi__Qo 45,3 s): weiter quer gekantet, etwas gehoben, Ring ≈ 57/64 %, linke Hand unten ≈ 47/89 %, oberer Wurfarm rechts aus dem Bild, Zughand nicht sichtbar (andere Bögen stehen dabei rechts senkrecht, destiny2:221). Lage E (Ausgleichsrechnung), gerechnet Griff 50/88 %, Ring 57/64 %, voller Auszug hinter der Kamera |
| Haltung `sprint` | Socket_Hand [-0.12, -0.4, -0.03], Ziel [0.0, -2.6, -0.5], Rollen -20° | O cubeescape-reference destiny2:221 (Sprint, wahrscheinlich): Riser größer und höher, Mitte ≈ 68/55 %, oberes Wurfarmende aus dem Bild, ≈ 20° geneigt; destiny2:231 ohne Pfeil tief rechts. Lage E, gerechnet Griff 69/61 % |
| Haltung `inspect_l` | Socket_Hand [-0.06, -0.52, -0.14], Ziel [1.6, -1.2, 0.0], Rollen -60° | E: Bogen 1 m hoch – Betrachten weiter weg als die Gewehre, Visierseite zur Kamera (gerechnet Ring 50/59 %); Destiny hat keinen Ego-Inspect |
| Haltung `inspect_r` | Socket_Hand [-0.1, -0.52, -0.14], Ziel [-0.6, -1.4, 0.2], Rollen 60° | E: rechte Seite mit dem Pfeil, Wurfarme quer aus dem Bild (gerechnet Pfeilspitze 71/43 %, Griff 63/81 %) |
| Haltung `crouch` | Socket_Hand [0.0, -0.6, -0.195], Rollen -77° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `air` | Socket_Hand [-0.01, -0.61, -0.165], Rollen -82° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `lowered` | Socket_Hand [0.01, -0.57, -0.2], Rollen -76° | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| Dauer `aim_in` | 6 Bilder bei 30/s (0.200 s) | M Destiny-Bogen: Zielen gespannt 0,25 s (Motiongen destiny2:270/508) → 6 Bilder bei 30/s (Umrechnung mit dem Zielen-Nachlauf wie Scharfschütze 14 B60 → 6), aus E 5; Ziehen 6–8 Bilder bei 60/s bis hüftähnlich (wechsel:48/50) + Ausfedern E → 14 (wie die Seitenwaffe) |
| Dauer `aim_out` | 5 Bilder bei 30/s (0.167 s) | M Destiny-Bogen: Zielen gespannt 0,25 s (Motiongen destiny2:270/508) → 6 Bilder bei 30/s (Umrechnung mit dem Zielen-Nachlauf wie Scharfschütze 14 B60 → 6), aus E 5; Ziehen 6–8 Bilder bei 60/s bis hüftähnlich (wechsel:48/50) + Ausfedern E → 14 (wie die Seitenwaffe) |
| Dauer `draw` | 14 Bilder bei 30/s (0.467 s) | M Destiny-Bogen: Zielen gespannt 0,25 s (Motiongen destiny2:270/508) → 6 Bilder bei 30/s (Umrechnung mit dem Zielen-Nachlauf wie Scharfschütze 14 B60 → 6), aus E 5; Ziehen 6–8 Bilder bei 60/s bis hüftähnlich (wechsel:48/50) + Ausfedern E → 14 (wie die Seitenwaffe) |
| Mündungsfeuer | keins (Werkzeug) | Feuerart aus der Spec (draw_release: Spannen, Halten, Lösen); kein Magazin (Vorrat, magazine 0 = unbegrenzt, Motiongen destiny2:270); Takt E 60/min (begrenzt nicht: Lösen, Auflegen und Spannen dauern 1,3 s, Destiny Lösen → Lösen 1,45 s); keine Bahnstufe (die Welt steigt nicht, der Bogen ruckt), Kick 1,5 E (Wurfarme-Ruck, destiny2:498); kein Mündungsfeuer, keine Hülse |
| Hülsen | keine | Waffe ohne Feld EJECT |
| Rückstoß | ego.RECOIL (gemeinsam) | übertragen von der Automatik: Säule 1 % H je Schuss, im Zielen wandert die Welt (5.1 A / 5.2 A); Werkzeug: Modellkick der Aktion (fire_a/fire_b kick 0,6), keine Bahnstufe (E; Portal 2: obere Klaue ≈ 7 % H im ersten Schussbild) |
| Wirkung | Pfeil 70 m/s, Fall 4 m/s², steckt 4 s | E: Pfeil 70 m/s mit leichter Fallkurve, steckt 4 s, Leuchtspur; beim Lösen ein Lichtpuls an der Auflage; Destiny Imperial Needle: blauer Entladefächer 2 Bilder ≈ 22 % beim Lösen (destiny2 › z-ballista-imperial-needle), Pfeilfall und Steckdauer offen (ego.PAYLOAD, Entscheidungsliste Block 9) |
| Sprint-Frequenz | 3,16 / 1,58 Hz (gemeinsam) | M Destiny Automatik/Handfeuerwaffe, für alle Klassen bis zu neuen Messungen (3c) |
| Griffe | grip, support, nock | Modul-Feld EGO_GRIPS |
| Live-Teile | trigger = , bolt = , port =  | Modul-Feld EGO_LIVE |

### Haltungen

| Haltung | Socket_Hand (m) | Handgelenk max | Herkunft |
|---|---|---|---|
| `hip` | [-0.01, -0.61, -0.18] | nur in Aktionen geprüft | M cubeescape-reference huefte.json › hl-destiny-2-imperial-needle (Ultraclocked 0:47,000): linke Griffhand 46,6/84,8 %, Visier 57,3/75,2 %, Bogen breit im unteren Bild (Körper 7,6–100 × 68,6–100 %), rechte Hand an der Nocke 49–64 × 91–100 %; destiny2:514 quer gekantet von links unten nach rechts oben, Pfeil zur Mitte. Lage E (Ausgleichsrechnung gegen diese Werte, dann 3 cm nach rechts für die Freihaltezone A4), gerechnet Griff 50/84 %, Nocke 57/93 %, Pfeilspitze 53/67 %, Ring 56/68 %, Wurfarme links unten und rechts oben aus dem Bild |
| `ads` | [0.0, 0.27, 0.0] | nur in Aktionen geprüft | M Destiny-Bogen Imperial Needle im Zielen (Bilder aus Ultraclocked dKNTDzi__Qo 47,75/48,3/67,7 s, Cache CubeEscape/reference/visiere; cubeescape-reference destiny2:105 Ring 50/57, zielbewegung: Zoom 2,2×): Blick durch den Ring, der Riser direkt rechts daneben, die Pfeilspitze unter dem Ring, Wurfarme über die volle Bildhöhe, linke Hand unten Mitte; der Ring ist ≈ 9 % B groß. Lage E: der Bogen steht 27 cm näher an der Kamera als der Ankerpunkt des vollen Auszugs (Socket_Eye 23 cm hinter dem Auge, Sehne und Zughand hinter der Kamera; Nutzer 30.10.2026: „beim Bogen ist das Visier näher am Bild“; mit 23 cm ≈ 6 % B im Bildvergleich), gerechnet Ring 50/50 % mit Ø 52 mm in 0,41 m ≈ 9,8 % B |
| `sprint` | [-0.12, -0.4, -0.03] | nur in Aktionen geprüft | O cubeescape-reference destiny2:221 (Sprint, wahrscheinlich): Riser größer und höher, Mitte ≈ 68/55 %, oberes Wurfarmende aus dem Bild, ≈ 20° geneigt; destiny2:231 ohne Pfeil tief rechts. Lage E, gerechnet Griff 69/61 % |
| `lowered` | [0.01, -0.57, -0.2] | nur in Aktionen geprüft | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| `crouch` | [0.0, -0.6, -0.195] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `air` | [-0.01, -0.61, -0.165] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `holstered` | [-0.24, -0.25, -0.62] | nur in Aktionen geprüft | E (unter dem Bild) |
| `inspect_l` | [-0.06, -0.52, -0.14] | nur in Aktionen geprüft | E: Bogen 1 m hoch – Betrachten weiter weg als die Gewehre, Visierseite zur Kamera (gerechnet Ring 50/59 %); Destiny hat keinen Ego-Inspect |
| `inspect_r` | [-0.1, -0.52, -0.14] | nur in Aktionen geprüft | E: rechte Seite mit dem Pfeil, Wurfarme quer aus dem Bild (gerechnet Pfeilspitze 71/43 %, Griff 63/81 %) |
| `drawn` | [0.0, -0.49, -0.16] | nur in Aktionen geprüft | M Destiny-Bogen Imperial Needle gespannt aus der Hüfte (Bild Ultraclocked dKNTDzi__Qo 45,3 s): weiter quer gekantet, etwas gehoben, Ring ≈ 57/64 %, linke Hand unten ≈ 47/89 %, oberer Wurfarm rechts aus dem Bild, Zughand nicht sichtbar (andere Bögen stehen dabei rechts senkrecht, destiny2:221). Lage E (Ausgleichsrechnung), gerechnet Griff 50/88 %, Ring 57/64 %, voller Auszug hinter der Kamera |

### Aktionen

| Aktion | Beschreibung | Bilder | Marker (Bild) | Handgelenk max | Clip | Sichtung | Herkunft |
|---|---|---|---|---|---|---|---|
| `idle_hip` | Ruhe an der Hüfte (Atmen) | 75 (2.50 s) | – | offen° | offen | offen | E |
| `draw` | Ziehen | 14 (0.47 s) | Ready (10) | offen° | offen | offen | M Ziehen 0,23 s bis Hüfte (Auto Rifle, Q-REF) + Ausfedern E; Klasse combat_bow: 25 → 14 Bilder (M Destiny-Bogen: Zielen gespannt 0,25 s (Motiongen destiny2:270/508) → 6 Bilder bei 30/s (Umrechnung mit dem Zielen-Nachlauf wie Scharfschütze 14 B60 → 6), aus E 5; Ziehen 6–8 Bilder bei 60/s bis hüftähnlich (wechsel:48/50) + Ausfedern E → 14 (wie die Seitenwaffe)) |
| `holster` | Wegstecken | 8 (0.27 s) | HandOff (1), Holstered (8) | offen° | offen | offen | M Destiny-Wechsel: Wegstecken 0,08–0,27 s (Motiongen wechsel › 4, Entscheidungsliste 6.1 A) → 0,27 s ohne TIME_SCALE (bis 0.14: 0,60 s); Ablauf E (CE: Holster ab aktueller Stellung) |
| `aim_in` | Hüfte → Zielen | 6 (0.20 s) | Aimed (5) | offen° | offen | offen | E 0,30 s (CE-Handling Auto 0,39→0,20 s); Klasse combat_bow: 10 → 6 Bilder (M Destiny-Bogen: Zielen gespannt 0,25 s (Motiongen destiny2:270/508) → 6 Bilder bei 30/s (Umrechnung mit dem Zielen-Nachlauf wie Scharfschütze 14 B60 → 6), aus E 5; Ziehen 6–8 Bilder bei 60/s bis hüftähnlich (wechsel:48/50) + Ausfedern E → 14 (wie die Seitenwaffe)) |
| `aim_out` | Zielen → Hüfte | 5 (0.17 s) | Ready (5) | offen° | offen | offen | E; Klasse combat_bow: 8 → 5 Bilder (M Destiny-Bogen: Zielen gespannt 0,25 s (Motiongen destiny2:270/508) → 6 Bilder bei 30/s (Umrechnung mit dem Zielen-Nachlauf wie Scharfschütze 14 B60 → 6), aus E 5; Ziehen 6–8 Bilder bei 60/s bis hüftähnlich (wechsel:48/50) + Ausfedern E → 14 (wie die Seitenwaffe)) |
| `inspect` | Betrachten | 120 (4.00 s) | Start (20), End (118) | offen° | offen | offen | E nach Apex/CoD-Muster (Ego-Seite, dann Oberseite); Destiny hat keinen Ego-Inspect |
| `sprint` | Sprint: Beginn, Schleife, Ende | 60 (2.00 s) | SprintLoop (10), Ready (60) | offen° | offen | offen | E (CE: Waffe senkt sich und rollt zur Mitte); period = Doppelschritt (seitlich), vertikal je Schritt: 19 Bilder = 0,633 s → 3,16 Schritte/s, seitlich 1,58 Hz, Rollen ±3,5°, U-Bogen (oben an den Seitenumkehren) nach Motiongen REF 0.23 (Destiny 2, Automatik/Handfeuerwaffe gemessen). 0.9: 10 Bilder = 6 Schritte/s („tapsig“). 0.15: Hub 12/10 → 22/18 mm (seitlich/vertikal) für ≈ 10 % H / 13 % B im Bild wie die Destiny-Automatik (Entscheidungsliste 3.1 A, gemessen wie in Schritt 2: Oberkante, linke Kante) |
| `lowered` | Gesenkte Haltung / Wandnähe | 45 (1.50 s) | Lowered (10), Ready (45) | offen° | offen | offen | E |
| `walk` | Gehen (liegende Acht) | 60 (2.00 s) | – | offen° | offen | offen | E (CE: liegende Acht) |
| `crouch` | Ducken | 30 (1.00 s) | Crouched (10) | offen° | offen | offen | E |
| `jump_land` | Sprung, Luftphase, Landung | 50 (1.67 s) | Air (10), Land (35) | offen° | offen | offen | E (CE: Anheben, Landefeder) |
| `sprint_to_aim` | Sprint → Zielen | 18 (0.60 s) | SprintOut (0), Aimed (12) | offen° | offen | offen | E (CE: ADS > Sprint) |
| `sprint_to_fire` | Sprint → Feuer | 26 (0.87 s) | SprintOut (0), Fire (7) | offen° | offen | offen | E (CE: Fire > Sprint); Klasse combat_bow: ohne Schuss (Bogen: Spannen beginnt nach dem Marker Fire) |
| `draw_aim` | Ziehen bei gehaltenem Zielen | 35 (1.17 s) | Ready (18), Aimed (30) | offen° | offen | offen | E (CE: Draw nicht unterbrechbar, ADS danach) |
| `fire_draw` | Spannen aus der Hüfte (Bogen senkrecht, Sehne zum Auge) | 18 (0.60 s) | FullDraw (18) | offen° | offen | offen | S/M Destiny-Bogen Imperial Needle Ziehzeit 612 ms, Anlegen → voll ≈ 0,60 s (cubeescape-reference destiny2:271) → voll bei Bild 18 (wie das Modul: Spannzeit 0,60 s); Heben 0,1 s, dann Ziehen (destiny2:231), senkrecht in 4 Bildern (destiny2:185); Spannlicht bei vollem Auszug (Modul draw_hold_release) |
| `fire_draw_ads` | Spannen im Zielen (Bogen bleibt im Anschlag) | 18 (0.60 s) | FullDraw (18) | offen° | offen | offen | E wie fire_draw, die Waffe bleibt im Zielen (Ringvisier vor dem Auge) |
| `draw_aim_in` | Gespannt ins Zielen (Bogen dreht senkrecht vor das Auge, bleibt gespannt) | 7 (0.23 s) | Aimed (6) | offen° | offen | offen | M cubeescape-reference destiny2:271: ADS mit gespanntem Bogen, Bogen dreht in ≈ 15 Bildern bei 60/s (0,25 s) senkrecht, Ring und Pfeilspitze mittig → 5 × TIME_SCALE = 7 Bilder bei 30/s |
| `draw_aim_out` | Gespannt aus dem Zielen (seitlich, bleibt gespannt) | 4 (0.13 s) | Ready (4) | offen° | offen | offen | M cubeescape-reference destiny2:252: ADS-Verlassen ist kein Spannabbruch, 5 Bilder bei 60/s (0,083 s) bis zur seitlichen gezogenen Form → 3 × TIME_SCALE = 4 Bilder |
| `fire_release` | Lösen aus der Hüfte (Pfeil fliegt, Bogen ruckt nach rechts unten, neuer Pfeil liegt auf) | 10 (0.33 s) | Release (0), Nocked (6), Ready (10) | offen° | offen | offen | M cubeescape-reference destiny2:231: Lösen → gespannt 0,60 s (0,23 s Fall/Schwingen, 0,10 s Heben, 0,25 s Ziehen), beim Lösen kippt der Bogen ≈ 15 % H nach rechts unten, der nächste Pfeil liegt gleich auf; destiny2:271 Bogen federt und senkt sich 0,35 s → 10 Bilder bis zur Hüfte; Pfeil fliegt in 3 Bildern aus dem Bild (danach weit vorn), Sehne in 2 Bildern vor |
| `fire_release_ads` | Lösen im Zielen (zugleich aus dem Zielen, neuer Pfeil liegt auf) | 10 (0.33 s) | Release (0), Nocked (6), Ready (10) | offen° | offen | offen | M cubeescape-reference destiny2:105: Lösen mit gleichzeitigem ADS-Ausstieg, Ringmitte ≈ 30 pp H nach unten im ersten Lösungsbild (50/57 → 53/87); Unity zielt danach wieder, wenn Rechtsklick gehalten bleibt; Ablauf sonst wie fire_release |
| `let_down` | Entspannen ohne Schuss (Nachladen-Taste beim Spannen) | 5 (0.17 s) | Ready (5) | offen° | offen | offen | M cubeescape-reference destiny2:253: Spann-Reset ohne Schuss 9 Bilder bei 60/s (0,150 s), der Bogen rollt nach rechts in eine fast waagerechte tiefe Haltung, der Pfeil bleibt; „Use while drawn to cancel the shot“ (Nachladen-Taste) → 4 × TIME_SCALE = 5 Bilder; Unity blendet vom erreichten Auszug über |
| `let_down_ads` | Entspannen ohne Schuss im Zielen | 5 (0.17 s) | Ready (5) | offen° | offen | offen | E wie let_down, aus dem Zielen |

### Abdeckung der Matrixzeilen

| Zeile | durch Aktion | Status |
|---|---|---|
| `pose_rest` | `idle_hip` | offen (nicht gesichtet) |
| `pose_hip` | `idle_hip` | offen (nicht gesichtet) |
| `draw` | `draw` | offen (nicht gesichtet) |
| `ready` | `draw` | offen (nicht gesichtet) |
| `holster` | `holster` | offen (nicht gesichtet) |
| `pose_aim` | `aim_in` | offen (nicht gesichtet) |
| `tr_hip_aim` | `aim_in` | offen (nicht gesichtet) |
| `tr_aim_hip` | `aim_out` | offen (nicht gesichtet) |
| `inspect` | `inspect` | offen (nicht gesichtet) |
| `inspect_return` | `inspect` | offen (nicht gesichtet) |
| `sprint_in` | `sprint` | offen (nicht gesichtet) |
| `sprint_loop` | `sprint` | offen (nicht gesichtet) |
| `sprint_out` | `sprint` | offen (nicht gesichtet) |
| `pose_lowered` | `lowered` | offen (nicht gesichtet) |
| `tr_lowered_return` | `lowered` | offen (nicht gesichtet) |
| `move_walk` | `walk` | offen (nicht gesichtet) |
| `sway` | `walk` | offen (nicht gesichtet) |
| `crouch` | `crouch` | offen (nicht gesichtet) |
| `jump_start` | `jump_land` | offen (nicht gesichtet) |
| `air` | `jump_land` | offen (nicht gesichtet) |
| `land` | `jump_land` | offen (nicht gesichtet) |
| `tr_sprint_aim` | `sprint_to_aim` | offen (nicht gesichtet) |
| `tr_sprint_fire` | `sprint_to_fire` | offen (nicht gesichtet) |
| `tr_draw_aimheld` | `draw_aim` | offen (nicht gesichtet) |

## BASIC-13-v2.1 – Trommel v2.1 (grenade_launcher)

### Klassen- und Spielwerte

| Wert | Stand | Herkunft |
|---|---|---|
| Klasse | grenade_launcher | Ego-Übertrag 0.33 „Armory“ P4: Hüfte, Anflug und Ladezeiten nach Motiongen (Granatwerfer), Sprint der Automatik, Trommel und Nachladen je Kammer E nach dem Modul |
| Kadenz | 90/min | S Destiny-Granatwerfer 90/min (Motiongen destiny2:271-272, Einzellader mit Magazin 1); Magazin 6 E (Trommel des Modells, Spec v2.1 semi_auto); Feuerart aus der Spec (Einzelfeuer, danach dreht die Trommel); Bahnstufe 0,04 E: Waffe schlägt hoch zur Kamera, Rückkehr ≈ 0,6 s (destiny2:509) → Erholung ab 0,2 s mit 1,7 Hz; Kick 2,5 E; Blitz 0,9 E (die D-Linse W1 lag bei 20,3 % > 20 %, 5.3 A) |
| Magazin | 6 | S Destiny-Granatwerfer 90/min (Motiongen destiny2:271-272, Einzellader mit Magazin 1); Magazin 6 E (Trommel des Modells, Spec v2.1 semi_auto); Feuerart aus der Spec (Einzelfeuer, danach dreht die Trommel); Bahnstufe 0,04 E: Waffe schlägt hoch zur Kamera, Rückkehr ≈ 0,6 s (destiny2:509) → Erholung ab 0,2 s mit 1,7 Hz; Kick 2,5 E; Blitz 0,9 E (die D-Linse W1 lag bei 20,3 % > 20 %, 5.3 A) |
| Feuerart | `semi_auto` – Einzelfeuer (ein Schuss je Zug) | Spec (META fire, data/specs); Unity: gameplay.fire_mode (0.20) |
| Weltzoom im Zielen | 1.4 | M Glidepath (Entscheidungsliste 1.2 A, basic/reticles.py › CLASS_ZOOM) |
| Hüft-Fadenkreuz | gl_brackets 11.2 % H | gemessen (Glidepath, 6,3 % B × 5,6 % H = 11,2 × 5,6 % H) (4.1 A / 4.2 A, basic/reticles.py › HUD_HIP) |
| Sprint-Fadenkreuz | aus | basic/reticles.py › HIP.sprint (4.1 A) |
| Absehen im Glas | circle_cross 4.5 % H | basic/reticles.py › HIP (common.drawn_reticle, Teil des Modells); Unity: gameplay.sight_form |
| Bahnstufe je Schuss | 4.00 % H | S Destiny-Granatwerfer 90/min (Motiongen destiny2:271-272, Einzellader mit Magazin 1); Magazin 6 E (Trommel des Modells, Spec v2.1 semi_auto); Feuerart aus der Spec (Einzelfeuer, danach dreht die Trommel); Bahnstufe 0,04 E: Waffe schlägt hoch zur Kamera, Rückkehr ≈ 0,6 s (destiny2:509) → Erholung ab 0,2 s mit 1,7 Hz; Kick 2,5 E; Blitz 0,9 E (die D-Linse W1 lag bei 20,3 % > 20 %, 5.3 A) |
| Haltung `hip` | Socket_Hand [-0.17, -0.42, -0.22], Ziel [0.1, -3.0, -0.14], Rollen 6° | M Destiny-Granatwerfer Hüfte: Mündung ≈ 58/67 (Motiongen destiny2:509), 56/63 (huefte:68); Lage E, gerechnet Mündung 60/64 % (Automatik-Hüfte am Werfer: 62/66), 2 cm weiter zur Mitte, 1 cm höher |
| Haltung `reload` | Socket_Hand [-0.12, -0.43, -0.19], Ziel [0.9, -2.0, 0.2], Rollen -50° | E: Waffe vor dem Körper nach rechts gerollt, die Ladeklappe hinten links zeigt zur Kamera; 6 cm weiter weg als der erste Entwurf (der linke Unterarm an der Granate deckte die linke Bildhälfte, Still 0.33 P4) |
| Haltung `sprint` | Socket_Hand [-0.1, -0.34, -0.23], Ziel [1.2, -1.6, -0.55], Rollen -35° | E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-Granatwerfer-Sprint nicht gemessen (Motiongen destiny2:571) (Haltung POSES['sprint'] unverändert) |
| Haltung `crouch` | Socket_Hand [-0.16, -0.41, -0.235], Rollen 9° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `air` | Socket_Hand [-0.17, -0.42, -0.205], Rollen 4° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `lowered` | Socket_Hand [-0.15, -0.38, -0.24], Rollen 10° | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| Dauer `aim_in` | 5 Bilder bei 30/s (0.167 s) | M Destiny-Granatwerfer ADS ein ≈ 12 Bilder bei 60/s (Motiongen destiny2:593; 19 B60 destiny2:271) → 5 Bilder bei 30/s (Umrechnung wie Schrotflinte 13 → 5); ADS aus Chill Inhibitor 25 Bilder bei 60/s bei ein 22 (Motiongen destiny2 › Gapfill, z-g34-vesper; die anderen gehen ins Nachladen) → Verhältnis aus/ein 1,14 auf aim_in 5 → 6; Ziehen erstes Modellbild → ruhig Chill 54, Velocity Baton 28, Forbearance 46, Witherhoard 39–52 → Mittel ≈ 43 → 22 |
| Dauer `aim_out` | 6 Bilder bei 30/s (0.200 s) | M Destiny-Granatwerfer ADS ein ≈ 12 Bilder bei 60/s (Motiongen destiny2:593; 19 B60 destiny2:271) → 5 Bilder bei 30/s (Umrechnung wie Schrotflinte 13 → 5); ADS aus Chill Inhibitor 25 Bilder bei 60/s bei ein 22 (Motiongen destiny2 › Gapfill, z-g34-vesper; die anderen gehen ins Nachladen) → Verhältnis aus/ein 1,14 auf aim_in 5 → 6; Ziehen erstes Modellbild → ruhig Chill 54, Velocity Baton 28, Forbearance 46, Witherhoard 39–52 → Mittel ≈ 43 → 22 |
| Dauer `draw` | 22 Bilder bei 30/s (0.733 s) | M Destiny-Granatwerfer ADS ein ≈ 12 Bilder bei 60/s (Motiongen destiny2:593; 19 B60 destiny2:271) → 5 Bilder bei 30/s (Umrechnung wie Schrotflinte 13 → 5); ADS aus Chill Inhibitor 25 Bilder bei 60/s bei ein 22 (Motiongen destiny2 › Gapfill, z-g34-vesper; die anderen gehen ins Nachladen) → Verhältnis aus/ein 1,14 auf aim_in 5 → 6; Ziehen erstes Modellbild → ruhig Chill 54, Velocity Baton 28, Forbearance 46, Witherhoard 39–52 → Mittel ≈ 43 → 22 |
| Mündungsfeuer | 33 ms | M Destiny: 1–2 Bilder bei 60/s, Kern klein, Seitenflammen breiter, Zielen Automatik ≈ 20 % der Öffnung (Motiongen muendung › 6, Entscheidungsliste 5.3 A); Maße und Farben E (Stil v2.1) |
| Hülsen | grenade_40 (35 × 42 mm) | E: aus der Ladekammer durch die offene Ladeklappe, nach links unten (Stützhand-Seite, Waffe beim Nachladen abgesenkt); nur beim Nachladen; Bahn: M Destiny: Hülse im 1. Blitzbild oder 1 Bild danach, rechts/rechts unten (Motiongen muendung › 6, Entscheidungsliste 5d/5.4 A); Geschwindigkeit, Drehung, Lebensdauer E |
| Rückstoß | ego.RECOIL (gemeinsam) | übertragen von der Automatik: Säule 1 % H je Schuss, im Zielen wandert die Welt (5.1 A / 5.2 A); Werkzeug: Modellkick der Aktion (fire_a/fire_b kick 0,6), keine Bahnstufe (E; Portal 2: obere Klaue ≈ 7 % H im ersten Schussbild) |
| Wirkung | Projektil 42 m/s, Fall 7 m/s², Explosion 3 m, Laufrauch 0.2 s | M Laufeffekt 0,05–0,2 s → 0,2 s (Nutzerentscheid 182), kein Schweif, Flug nah 0,17–0,22 s (REF 0.36 z-im-velocity-baton, z-im-chill-inhibitor); E: Granate 42 m/s mit Fallkurve (25 m: 0,6 s, 1,2 m Fall), Explosion Radius 3 m (ego.PAYLOAD, Entscheidungsliste Block 9) |
| Sprint-Frequenz | 3,16 / 1,58 Hz (gemeinsam) | M Destiny Automatik/Handfeuerwaffe, für alle Klassen bis zu neuen Messungen (3c) |
| Griffe | grip, support, mag, gate, charge | Modul-Feld EGO_GRIPS |
| Live-Teile | trigger = trigger, bolt = , port = , rounds = drum (6 Sätze, Trommel drum) | Modul-Feld EGO_LIVE |

### Haltungen

| Haltung | Socket_Hand (m) | Handgelenk max | Herkunft |
|---|---|---|---|
| `hip` | [-0.17, -0.42, -0.22] | nur in Aktionen geprüft | M Destiny-Granatwerfer Hüfte: Mündung ≈ 58/67 (Motiongen destiny2:509), 56/63 (huefte:68); Lage E, gerechnet Mündung 60/64 % (Automatik-Hüfte am Werfer: 62/66), 2 cm weiter zur Mitte, 1 cm höher |
| `ads` | [0.0, 0.0, 0.0] | nur in Aktionen geprüft | Visier-Standard v2: Socket_Eye ist der Augenpunkt, liegt in der Kamera; Waffenmodell ungezoomt, Welt zoomt je Klasse |
| `sprint` | [-0.1, -0.34, -0.23] | nur in Aktionen geprüft | E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-Granatwerfer-Sprint nicht gemessen (Motiongen destiny2:571) (Haltung POSES['sprint'] unverändert) |
| `lowered` | [-0.15, -0.38, -0.24] | nur in Aktionen geprüft | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| `crouch` | [-0.16, -0.41, -0.235] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `air` | [-0.17, -0.42, -0.205] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `holstered` | [-0.24, -0.25, -0.62] | nur in Aktionen geprüft | E (unter dem Bild) |
| `reload` | [-0.12, -0.43, -0.19] | nur in Aktionen geprüft | E: Waffe vor dem Körper nach rechts gerollt, die Ladeklappe hinten links zeigt zur Kamera; 6 cm weiter weg als der erste Entwurf (der linke Unterarm an der Granate deckte die linke Bildhälfte, Still 0.33 P4) |
| `inspect_l` | [-0.06, -0.36, -0.16] | nur in Aktionen geprüft | E (Ego-Seite zeigt zur Kamera) |
| `inspect_r` | [-0.1, -0.36, -0.12] | nur in Aktionen geprüft | E (Oberseite und rechte Seite) |

### Aktionen

| Aktion | Beschreibung | Bilder | Marker (Bild) | Handgelenk max | Clip | Sichtung | Herkunft |
|---|---|---|---|---|---|---|---|
| `idle_hip` | Ruhe an der Hüfte (Atmen) | 75 (2.50 s) | – | offen° | offen | offen | E |
| `draw` | Ziehen | 22 (0.73 s) | Ready (16) | 42.7° | ego_BASIC-13-v2.1_draw.mp4 | offen | M Ziehen 0,23 s bis Hüfte (Auto Rifle, Q-REF) + Ausfedern E; Klasse grenade_launcher: 25 → 22 Bilder (M Destiny-Granatwerfer ADS ein ≈ 12 Bilder bei 60/s (Motiongen destiny2:593; 19 B60 destiny2:271) → 5 Bilder bei 30/s (Umrechnung wie Schrotflinte 13 → 5); ADS aus Chill Inhibitor 25 Bilder bei 60/s bei ein 22 (Motiongen destiny2 › Gapfill, z-g34-vesper; die anderen gehen ins Nachladen) → Verhältnis aus/ein 1,14 auf aim_in 5 → 6; Ziehen erstes Modellbild → ruhig Chill 54, Velocity Baton 28, Forbearance 46, Witherhoard 39–52 → Mittel ≈ 43 → 22) |
| `holster` | Wegstecken | 8 (0.27 s) | HandOff (1), Holstered (8) | offen° | offen | offen | M Destiny-Wechsel: Wegstecken 0,08–0,27 s (Motiongen wechsel › 4, Entscheidungsliste 6.1 A) → 0,27 s ohne TIME_SCALE (bis 0.14: 0,60 s); Ablauf E (CE: Holster ab aktueller Stellung) |
| `aim_in` | Hüfte → Zielen | 5 (0.17 s) | Aimed (4) | offen° | offen | offen | E 0,30 s (CE-Handling Auto 0,39→0,20 s); Klasse grenade_launcher: 10 → 5 Bilder (M Destiny-Granatwerfer ADS ein ≈ 12 Bilder bei 60/s (Motiongen destiny2:593; 19 B60 destiny2:271) → 5 Bilder bei 30/s (Umrechnung wie Schrotflinte 13 → 5); ADS aus Chill Inhibitor 25 Bilder bei 60/s bei ein 22 (Motiongen destiny2 › Gapfill, z-g34-vesper; die anderen gehen ins Nachladen) → Verhältnis aus/ein 1,14 auf aim_in 5 → 6; Ziehen erstes Modellbild → ruhig Chill 54, Velocity Baton 28, Forbearance 46, Witherhoard 39–52 → Mittel ≈ 43 → 22) |
| `aim_out` | Zielen → Hüfte | 6 (0.20 s) | Ready (6) | 28.0° | ego_BASIC-13-v2.1_aim_out.mp4 | offen | E; Klasse grenade_launcher: 8 → 6 Bilder (M Destiny-Granatwerfer ADS ein ≈ 12 Bilder bei 60/s (Motiongen destiny2:593; 19 B60 destiny2:271) → 5 Bilder bei 30/s (Umrechnung wie Schrotflinte 13 → 5); ADS aus Chill Inhibitor 25 Bilder bei 60/s bei ein 22 (Motiongen destiny2 › Gapfill, z-g34-vesper; die anderen gehen ins Nachladen) → Verhältnis aus/ein 1,14 auf aim_in 5 → 6; Ziehen erstes Modellbild → ruhig Chill 54, Velocity Baton 28, Forbearance 46, Witherhoard 39–52 → Mittel ≈ 43 → 22) |
| `fire_hip` | Dauerfeuer aus der Hüfte | 32 (1.07 s) | Fire (2) | offen° | offen | offen | M 720/min = 1 Schuss je 2,5 Bilder (Q-REF; bis 0.14 alle 2 Bilder ≈ 940/min); Rückstoß T 17,5 mm/3°; Klasse grenade_launcher: 90/min, Einzelfeuer (ein Schuss je Zug) (Schussbilder [2, 22]) |
| `fire_ads` | Dauerfeuer im Zielen | 32 (1.07 s) | AimFire (2) | offen° | offen | offen | M Kadenz wie fire_hip; Rückstoß im Zielen nach RECOIL ads_* (5.1 A: Visier steht, die Welt wandert) E; Klasse grenade_launcher: 90/min, Einzelfeuer (ein Schuss je Zug) (Schussbilder [2, 22]) |
| `reload_tactical` | Nachladen: Einstieg (Klappe auf, Hülse fällt, erste Granate von hinten einschieben) | 33 (1.10 s) | HandOff (2), GateOpen (12), Eject (14), ShellIn (26) | offen° | offen | offen | M Destiny-Granatwerfer: Granate ein +0,69 s, Schließen +1,17, Hüfte +2,42 s (Motiongen destiny2:271/509, Einzellader) → ShellIn bei 21 von 26 Bildern (× TIME_SCALE 0,88 s); Ablauf E nach dem Modul (reload: Klappenknopf, Klappe, je Kammer Hülse aus, Granate ein, Trommel weiter); Trommel-Nachladen bei Destiny nicht gemessen |
| `reload_empty` | Nachladen: Einstieg (Klappe auf, Hülse fällt, erste Granate von hinten einschieben), auch leer | 33 (1.10 s) | HandOff (2), GateOpen (12), Eject (14), ShellIn (26) | offen° | offen | offen | M Destiny-Granatwerfer: Granate ein +0,69 s, Schließen +1,17, Hüfte +2,42 s (Motiongen destiny2:271/509, Einzellader) → ShellIn bei 21 von 26 Bildern (× TIME_SCALE 0,88 s); Ablauf E nach dem Modul (reload: Klappenknopf, Klappe, je Kammer Hülse aus, Granate ein, Trommel weiter); Trommel-Nachladen bei Destiny nicht gemessen |
| `inspect` | Betrachten | 120 (4.00 s) | Start (20), End (118) | offen° | offen | offen | E nach Apex/CoD-Muster (Ego-Seite, dann Oberseite); Destiny hat keinen Ego-Inspect |
| `sprint` | Sprint: Beginn, Schleife, Ende | 60 (2.00 s) | SprintLoop (10), Ready (60) | offen° | offen | offen | E (CE: Waffe senkt sich und rollt zur Mitte); period = Doppelschritt (seitlich), vertikal je Schritt: 19 Bilder = 0,633 s → 3,16 Schritte/s, seitlich 1,58 Hz, Rollen ±3,5°, U-Bogen (oben an den Seitenumkehren) nach Motiongen REF 0.23 (Destiny 2, Automatik/Handfeuerwaffe gemessen). 0.9: 10 Bilder = 6 Schritte/s („tapsig“). 0.15: Hub 12/10 → 22/18 mm (seitlich/vertikal) für ≈ 10 % H / 13 % B im Bild wie die Destiny-Automatik (Entscheidungsliste 3.1 A, gemessen wie in Schritt 2: Oberkante, linke Kante) |
| `lowered` | Gesenkte Haltung / Wandnähe | 45 (1.50 s) | Lowered (10), Ready (45) | offen° | offen | offen | E |
| `walk` | Gehen (liegende Acht) | 60 (2.00 s) | – | offen° | offen | offen | E (CE: liegende Acht) |
| `crouch` | Ducken | 30 (1.00 s) | Crouched (10) | offen° | offen | offen | E |
| `jump_land` | Sprung, Luftphase, Landung | 50 (1.67 s) | Air (10), Land (35) | offen° | offen | offen | E (CE: Anheben, Landefeder) |
| `sprint_to_aim` | Sprint → Zielen | 18 (0.60 s) | SprintOut (0), Aimed (12) | offen° | offen | offen | E (CE: ADS > Sprint) |
| `sprint_to_fire` | Sprint → Feuer | 26 (0.87 s) | SprintOut (0), Fire (7) | offen° | offen | offen | E (CE: Fire > Sprint); Klasse grenade_launcher: 90/min, Einzelfeuer (ein Schuss je Zug) (Schussbilder [7]) |
| `draw_aim` | Ziehen bei gehaltenem Zielen | 35 (1.17 s) | Ready (18), Aimed (30) | offen° | offen | offen | E (CE: Draw nicht unterbrechbar, ADS danach) |
| `reload_to_switch` | Nachladen → Waffenwechsel (Abbruch) | 38 (1.27 s) | HandOff (5), Cancel (18), Holstered (35) | offen° | offen | offen | E (CE: Reload bricht bei Wechsel ab, Holster ab aktueller Stellung) |
| `fire_cycle` | Trommel eine Kammer weiter nach dem Schuss (Hüfte) | 9 (0.30 s) | Chamber (8) | offen° | offen | offen | E wie das Modul (fire: Trommel 60° in 6 Bildern, danach zurück – sechsfache Teilung); 0,3 s vor dem nächsten Schuss (90/min = 0,67 s) |
| `fire_cycle_ads` | Trommel eine Kammer weiter nach dem Schuss (Zielen) | 9 (0.30 s) | Chamber (8) | offen° | offen | offen | E wie fire_cycle |
| `reload_shell` | Nachladen: eine weitere Granate (Unity wiederholt bis voll) | 28 (0.93 s) | Eject (1), ShellIn (20) | offen° | offen | offen | E wie der Einstieg (Hülse aus, Granate holen und einschieben, Trommel weiter), 22 Bilder (× TIME_SCALE 0,92 s) je Kammer |
| `reload_end` | Nachladen: Klappe zu, zurück zur Hüfte (voll oder durch Feuer abgebrochen) | 13 (0.43 s) | GateClosed (5), HandOn (10), Ready (12) | offen° | offen | offen | E: Klappe mit der Stützhand zuschlagen, Rückweg kurz wie die Schrotflinte (ein Zug am Abzug soll bald schießen) |

### Abdeckung der Matrixzeilen

| Zeile | durch Aktion | Status |
|---|---|---|
| `pose_rest` | `idle_hip` | offen (nicht gesichtet) |
| `pose_hip` | `idle_hip` | offen (nicht gesichtet) |
| `draw` | `draw` | offen (nicht gesichtet) |
| `ready` | `draw` | offen (nicht gesichtet) |
| `holster` | `holster` | offen (nicht gesichtet) |
| `pose_aim` | `aim_in` | offen (nicht gesichtet) |
| `tr_hip_aim` | `aim_in` | offen (nicht gesichtet) |
| `tr_aim_hip` | `aim_out` | offen (nicht gesichtet) |
| `fire_auto` | `fire_ads` | offen (nicht gesichtet) |
| `recoil_mech` | `fire_hip` | offen (nicht gesichtet) |
| `recoil_camera` | `fire_hip` | offen (nicht gesichtet) |
| `reload_partial` | `reload_tactical` | offen (nicht gesichtet) |
| `reload_feed` | `reload_tactical` | offen (nicht gesichtet) |
| `reload_empty` | `reload_empty` | offen (nicht gesichtet) |
| `cycle` | `reload_empty` | offen (nicht gesichtet) |
| `inspect` | `inspect` | offen (nicht gesichtet) |
| `inspect_return` | `inspect` | offen (nicht gesichtet) |
| `sprint_in` | `sprint` | offen (nicht gesichtet) |
| `sprint_loop` | `sprint` | offen (nicht gesichtet) |
| `sprint_out` | `sprint` | offen (nicht gesichtet) |
| `pose_lowered` | `lowered` | offen (nicht gesichtet) |
| `tr_lowered_return` | `lowered` | offen (nicht gesichtet) |
| `move_walk` | `walk` | offen (nicht gesichtet) |
| `sway` | `walk` | offen (nicht gesichtet) |
| `crouch` | `crouch` | offen (nicht gesichtet) |
| `jump_start` | `jump_land` | offen (nicht gesichtet) |
| `air` | `jump_land` | offen (nicht gesichtet) |
| `land` | `jump_land` | offen (nicht gesichtet) |
| `tr_sprint_aim` | `sprint_to_aim` | offen (nicht gesichtet) |
| `tr_sprint_fire` | `sprint_to_fire` | offen (nicht gesichtet) |
| `tr_draw_aimheld` | `draw_aim` | offen (nicht gesichtet) |
| `tr_reload_switch` | `reload_to_switch` | offen (nicht gesichtet) |
| `switch` | `reload_to_switch` | offen (nicht gesichtet) |

## BASIC-14-v2.1 – Schulterrohr v2.1 (rocket_launcher)

### Klassen- und Spielwerte

| Wert | Stand | Herkunft |
|---|---|---|
| Klasse | rocket_launcher | Ego-Übertrag 0.33 „Armory“ P4: Schulterhaltung, Anflug, Ziehen und Nachladezeit nach Motiongen (Raketenwerfer), Ablauf E |
| Kadenz | 20/min | S Destiny-Raketenwerfer 20/min, Magazin 1 (Motiongen destiny2:276); Feuerart aus der Spec (Einzelschuss, danach sofort nachladen); keine Bahnstufe, Kick 4,0 E: Schub zur Kamera, Linse 10 → 25 % H in 3–4 Bildern (destiny2:501); Mündungsfeuer 0,7 der Familie E (das Seitenvisier W2 liegt nah am Rohr: mit 1,0 deckte der Blitz 33,6 % der Öffnung, Regel ≤ 20 %, 5.3 A; Destiny-Weißblende 0,10–0,15 s offen) |
| Magazin | 1 | S Destiny-Raketenwerfer 20/min, Magazin 1 (Motiongen destiny2:276); Feuerart aus der Spec (Einzelschuss, danach sofort nachladen); keine Bahnstufe, Kick 4,0 E: Schub zur Kamera, Linse 10 → 25 % H in 3–4 Bildern (destiny2:501); Mündungsfeuer 0,7 der Familie E (das Seitenvisier W2 liegt nah am Rohr: mit 1,0 deckte der Blitz 33,6 % der Öffnung, Regel ≤ 20 %, 5.3 A; Destiny-Weißblende 0,10–0,15 s offen) |
| Feuerart | `single_shot` – Einzelschuss mit Magazin 1 (ein Schuss je Zug, danach sofort Nachladen als Klassenaktion reload_tactical) | Spec (META fire, data/specs); Unity: gameplay.fire_mode (0.20) |
| Weltzoom im Zielen | 2.8 | M Glidepath (Entscheidungsliste 1.2 A, basic/reticles.py › CLASS_ZOOM) |
| Hüft-Fadenkreuz | kein Hüftzeichen | gemessen (Glidepath, kein Mittenzeichen, 1 Clip) (4.1 A / 4.2 A, basic/reticles.py › HUD_HIP) |
| Sprint-Fadenkreuz | aus | basic/reticles.py › HIP.sprint (4.1 A) |
| Absehen im Glas | circle_cross 4.5 % H | basic/reticles.py › HIP (common.drawn_reticle, Teil des Modells); Unity: gameplay.sight_form |
| Bahnstufe je Schuss | 0.00 % H | S Destiny-Raketenwerfer 20/min, Magazin 1 (Motiongen destiny2:276); Feuerart aus der Spec (Einzelschuss, danach sofort nachladen); keine Bahnstufe, Kick 4,0 E: Schub zur Kamera, Linse 10 → 25 % H in 3–4 Bildern (destiny2:501); Mündungsfeuer 0,7 der Familie E (das Seitenvisier W2 liegt nah am Rohr: mit 1,0 deckte der Blitz 33,6 % der Öffnung, Regel ≤ 20 %, 5.3 A; Destiny-Weißblende 0,10–0,15 s offen) |
| Haltung `hip` | Socket_Hand [-0.23, -0.5, -0.16], Ziel [-0.01, -3.489, 0.616], Rollen 0° | M cubeescape-reference huefte.json (Hoosegow: Körper 60–100 × 0–100 %, Optik 65/68; Blue Shift: Körper 60–100 × 17–100 %, Optik 68/57) und destiny2:501 (Mündung ≈ 60/40): das Rohr steht rechts über die volle Bildhöhe, vorn oben, das Heck rechts unten unter dem Arm – nicht auf der Schulter (bis zum Abgleich aller Waffen mit huefte.json, 0.33 P4). Lage E (Ausgleichsrechnung, dann 5 cm nach rechts: das Rohr lag bis 56 % B in der Freihaltezone, A4; Destiny-Körper ab 60 % B; dann 1 cm weiter für die letzte Pixelspalte, 127 → 0 px), gerechnet Mündung 63,8/41,5 %, Visier 73,0/62,5 %, Rohr 13° steigend |
| Haltung `sprint` | Socket_Hand [-0.16, -0.36, -0.28], Ziel [0.3, -2.4, -1.3], Rollen -20° | E: Destiny-Raketenwerfer-Sprint nicht gemessen (Motiongen destiny2:572); Rohr von der Schulter gesenkt, Mündung nach vorn unten |
| Haltung `reload` | Socket_Hand [-0.22, -0.52, -0.12], Ziel [-2.9, -1.7, -0.5], Rollen 10° | E: Rohr quer vor dem Körper, Mündung nach rechts aus dem Bild, das Heck links im Bild (gerechnet Heckring 26/37 %, Griff 78/77 %) |
| Haltung `crouch` | Socket_Hand [-0.22, -0.49, -0.175], Rollen 3° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `air` | Socket_Hand [-0.23, -0.5, -0.145], Rollen -2° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `lowered` | Socket_Hand [-0.21, -0.46, -0.18], Rollen 4° | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| Dauer `aim_in` | 6 Bilder bei 30/s (0.200 s) | M Destiny-Raketenwerfer ADS ein 14 Bilder bei 60/s (Motiongen destiny2:594) → 6 Bilder bei 30/s (wie Scharfschütze); ADS aus nicht gemessen → E 5; Ziehen 0,18 s bis Hüfte (destiny2:481) + Ausfedern E → 14 |
| Dauer `aim_out` | 5 Bilder bei 30/s (0.167 s) | M Destiny-Raketenwerfer ADS ein 14 Bilder bei 60/s (Motiongen destiny2:594) → 6 Bilder bei 30/s (wie Scharfschütze); ADS aus nicht gemessen → E 5; Ziehen 0,18 s bis Hüfte (destiny2:481) + Ausfedern E → 14 |
| Dauer `draw` | 14 Bilder bei 30/s (0.467 s) | M Destiny-Raketenwerfer ADS ein 14 Bilder bei 60/s (Motiongen destiny2:594) → 6 Bilder bei 30/s (wie Scharfschütze); ADS aus nicht gemessen → E 5; Ziehen 0,18 s bis Hüfte (destiny2:481) + Ausfedern E → 14 |
| Mündungsfeuer | 33 ms | M Destiny: 1–2 Bilder bei 60/s, Kern klein, Seitenflammen breiter, Zielen Automatik ≈ 20 % der Öffnung (Motiongen muendung › 6, Entscheidungsliste 5.3 A); Maße und Farben E (Stil v2.1) |
| Hülsen | keine | Waffe ohne Feld EJECT |
| Rückstoß | ego.RECOIL (gemeinsam) | übertragen von der Automatik: Säule 1 % H je Schuss, im Zielen wandert die Welt (5.1 A / 5.2 A); Werkzeug: Modellkick der Aktion (fire_a/fire_b kick 0,6), keine Bahnstufe (E; Portal 2: obere Klaue ≈ 7 % H im ersten Schussbild) |
| Wirkung | Projektil 34 m/s, Fall 0 m/s², Explosion 4.5 m, Laufrauch 0 s | M Glühpunkt ohne Rauchzopf, Flug 0,32–0,65 s (REF 0.36 z-im-blue-shift): Flamme am Heck, keine Rauchspur; kein Rohrrauch sichtbar (REF 0.36 › 7; 0.34.2, vorher 2 s nach Nutzerwunsch 0.33); E: Rakete 34 m/s gerade (15 m: 0,44 s), Explosion Radius 4,5 m (ego.PAYLOAD, Entscheidungsliste Block 9) |
| Sprint-Frequenz | 3,16 / 1,58 Hz (gemeinsam) | M Destiny Automatik/Handfeuerwaffe, für alle Klassen bis zu neuen Messungen (3c) |
| Griffe | grip, support, mag, push, cap, charge | Modul-Feld EGO_GRIPS |
| Live-Teile | trigger = trigger, bolt = , port =  | Modul-Feld EGO_LIVE |

### Haltungen

| Haltung | Socket_Hand (m) | Handgelenk max | Herkunft |
|---|---|---|---|
| `hip` | [-0.23, -0.5, -0.16] | nur in Aktionen geprüft | M cubeescape-reference huefte.json (Hoosegow: Körper 60–100 × 0–100 %, Optik 65/68; Blue Shift: Körper 60–100 × 17–100 %, Optik 68/57) und destiny2:501 (Mündung ≈ 60/40): das Rohr steht rechts über die volle Bildhöhe, vorn oben, das Heck rechts unten unter dem Arm – nicht auf der Schulter (bis zum Abgleich aller Waffen mit huefte.json, 0.33 P4). Lage E (Ausgleichsrechnung, dann 5 cm nach rechts: das Rohr lag bis 56 % B in der Freihaltezone, A4; Destiny-Körper ab 60 % B; dann 1 cm weiter für die letzte Pixelspalte, 127 → 0 px), gerechnet Mündung 63,8/41,5 %, Visier 73,0/62,5 %, Rohr 13° steigend |
| `ads` | [0.0, 0.0, 0.0] | nur in Aktionen geprüft | Visier-Standard v2: Socket_Eye ist der Augenpunkt, liegt in der Kamera; Waffenmodell ungezoomt, Welt zoomt je Klasse |
| `sprint` | [-0.16, -0.36, -0.28] | nur in Aktionen geprüft | E: Destiny-Raketenwerfer-Sprint nicht gemessen (Motiongen destiny2:572); Rohr von der Schulter gesenkt, Mündung nach vorn unten |
| `lowered` | [-0.21, -0.46, -0.18] | nur in Aktionen geprüft | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| `crouch` | [-0.22, -0.49, -0.175] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `air` | [-0.23, -0.5, -0.145] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `holstered` | [-0.24, -0.25, -0.62] | nur in Aktionen geprüft | E (unter dem Bild) |
| `reload` | [-0.22, -0.52, -0.12] | nur in Aktionen geprüft | E: Rohr quer vor dem Körper, Mündung nach rechts aus dem Bild, das Heck links im Bild (gerechnet Heckring 26/37 %, Griff 78/77 %) |
| `inspect_l` | [-0.06, -0.36, -0.16] | nur in Aktionen geprüft | E (Ego-Seite zeigt zur Kamera) |
| `inspect_r` | [-0.1, -0.36, -0.12] | nur in Aktionen geprüft | E (Oberseite und rechte Seite) |

### Aktionen

| Aktion | Beschreibung | Bilder | Marker (Bild) | Handgelenk max | Clip | Sichtung | Herkunft |
|---|---|---|---|---|---|---|---|
| `idle_hip` | Ruhe an der Hüfte (Atmen) | 75 (2.50 s) | – | offen° | offen | offen | E |
| `draw` | Ziehen | 14 (0.47 s) | Ready (10) | offen° | offen | offen | M Ziehen 0,23 s bis Hüfte (Auto Rifle, Q-REF) + Ausfedern E; Klasse rocket_launcher: 25 → 14 Bilder (M Destiny-Raketenwerfer ADS ein 14 Bilder bei 60/s (Motiongen destiny2:594) → 6 Bilder bei 30/s (wie Scharfschütze); ADS aus nicht gemessen → E 5; Ziehen 0,18 s bis Hüfte (destiny2:481) + Ausfedern E → 14) |
| `holster` | Wegstecken | 8 (0.27 s) | HandOff (1), Holstered (8) | offen° | offen | offen | M Destiny-Wechsel: Wegstecken 0,08–0,27 s (Motiongen wechsel › 4, Entscheidungsliste 6.1 A) → 0,27 s ohne TIME_SCALE (bis 0.14: 0,60 s); Ablauf E (CE: Holster ab aktueller Stellung) |
| `aim_in` | Hüfte → Zielen | 6 (0.20 s) | Aimed (5) | offen° | offen | offen | E 0,30 s (CE-Handling Auto 0,39→0,20 s); Klasse rocket_launcher: 10 → 6 Bilder (M Destiny-Raketenwerfer ADS ein 14 Bilder bei 60/s (Motiongen destiny2:594) → 6 Bilder bei 30/s (wie Scharfschütze); ADS aus nicht gemessen → E 5; Ziehen 0,18 s bis Hüfte (destiny2:481) + Ausfedern E → 14) |
| `aim_out` | Zielen → Hüfte | 5 (0.17 s) | Ready (5) | offen° | offen | offen | E; Klasse rocket_launcher: 8 → 5 Bilder (M Destiny-Raketenwerfer ADS ein 14 Bilder bei 60/s (Motiongen destiny2:594) → 6 Bilder bei 30/s (wie Scharfschütze); ADS aus nicht gemessen → E 5; Ziehen 0,18 s bis Hüfte (destiny2:481) + Ausfedern E → 14) |
| `fire_hip` | Dauerfeuer aus der Hüfte | 32 (1.07 s) | Fire (2) | offen° | offen | offen | M 720/min = 1 Schuss je 2,5 Bilder (Q-REF; bis 0.14 alle 2 Bilder ≈ 940/min); Rückstoß T 17,5 mm/3°; Klasse rocket_launcher: 20/min, Einzelschuss mit Magazin 1 (ein Schuss je Zug, danach sofort Nachladen als Klassenaktion reload_tactical) (Schussbilder [2]) |
| `fire_ads` | Dauerfeuer im Zielen | 32 (1.07 s) | AimFire (2) | offen° | offen | offen | M Kadenz wie fire_hip; Rückstoß im Zielen nach RECOIL ads_* (5.1 A: Visier steht, die Welt wandert) E; Klasse rocket_launcher: 20/min, Einzelschuss mit Magazin 1 (ein Schuss je Zug, danach sofort Nachladen als Klassenaktion reload_tactical) (Schussbilder [2]) |
| `reload_tactical` | Nachladen nach dem Schuss (Heckklappe auf, Rakete von hinten einschieben, Klappe zu) | 105 (3.50 s) | Launch (0), HandOff (5), BreechOpen (25), MagIn (75), BreechClosed (90), HandOn (100), Ready (102) | offen° | offen | offen | M Destiny-Raketenwerfer Nachladen ≈ 2,8 s (Eyes of Tomorrow, Motiongen destiny2:276/513) → 84 Bilder (× TIME_SCALE 3,5 s), Rakete sitzt bei 60; Ablauf E nach dem Modul (reload: Klappenknopf, Heckklappe, Rakete von hinten, Klappe, Anzeige); die Rakete fliegt in 2 Bildern aus dem Rohr (danach verdeckt), die Hand holt die nächste unter dem Bild |
| `reload_empty` | Nachladen nach dem Schuss (Heckklappe auf, Rakete von hinten einschieben, Klappe zu), auch leer | 105 (3.50 s) | Launch (0), HandOff (5), BreechOpen (25), MagIn (75), BreechClosed (90), HandOn (100), Ready (102) | offen° | offen | offen | M Destiny-Raketenwerfer Nachladen ≈ 2,8 s (Eyes of Tomorrow, Motiongen destiny2:276/513) → 84 Bilder (× TIME_SCALE 3,5 s), Rakete sitzt bei 60; Ablauf E nach dem Modul (reload: Klappenknopf, Heckklappe, Rakete von hinten, Klappe, Anzeige); die Rakete fliegt in 2 Bildern aus dem Rohr (danach verdeckt), die Hand holt die nächste unter dem Bild |
| `inspect` | Betrachten | 120 (4.00 s) | Start (20), End (118) | offen° | offen | offen | E nach Apex/CoD-Muster (Ego-Seite, dann Oberseite); Destiny hat keinen Ego-Inspect |
| `sprint` | Sprint: Beginn, Schleife, Ende | 60 (2.00 s) | SprintLoop (10), Ready (60) | offen° | offen | offen | E (CE: Waffe senkt sich und rollt zur Mitte); period = Doppelschritt (seitlich), vertikal je Schritt: 19 Bilder = 0,633 s → 3,16 Schritte/s, seitlich 1,58 Hz, Rollen ±3,5°, U-Bogen (oben an den Seitenumkehren) nach Motiongen REF 0.23 (Destiny 2, Automatik/Handfeuerwaffe gemessen). 0.9: 10 Bilder = 6 Schritte/s („tapsig“). 0.15: Hub 12/10 → 22/18 mm (seitlich/vertikal) für ≈ 10 % H / 13 % B im Bild wie die Destiny-Automatik (Entscheidungsliste 3.1 A, gemessen wie in Schritt 2: Oberkante, linke Kante) |
| `lowered` | Gesenkte Haltung / Wandnähe | 45 (1.50 s) | Lowered (10), Ready (45) | offen° | offen | offen | E |
| `walk` | Gehen (liegende Acht) | 60 (2.00 s) | – | offen° | offen | offen | E (CE: liegende Acht) |
| `crouch` | Ducken | 30 (1.00 s) | Crouched (10) | offen° | offen | offen | E |
| `jump_land` | Sprung, Luftphase, Landung | 50 (1.67 s) | Air (10), Land (35) | offen° | offen | offen | E (CE: Anheben, Landefeder) |
| `sprint_to_aim` | Sprint → Zielen | 18 (0.60 s) | SprintOut (0), Aimed (12) | offen° | offen | offen | E (CE: ADS > Sprint) |
| `sprint_to_fire` | Sprint → Feuer | 26 (0.87 s) | SprintOut (0), Fire (7) | offen° | offen | offen | E (CE: Fire > Sprint); Klasse rocket_launcher: 20/min, Einzelschuss mit Magazin 1 (ein Schuss je Zug, danach sofort Nachladen als Klassenaktion reload_tactical) (Schussbilder [7]) |
| `draw_aim` | Ziehen bei gehaltenem Zielen | 35 (1.17 s) | Ready (18), Aimed (30) | offen° | offen | offen | E (CE: Draw nicht unterbrechbar, ADS danach) |
| `reload_to_switch` | Nachladen → Waffenwechsel (Abbruch) | 38 (1.27 s) | HandOff (5), Cancel (18), Holstered (35) | offen° | offen | offen | E (CE: Reload bricht bei Wechsel ab, Holster ab aktueller Stellung) |

### Abdeckung der Matrixzeilen

| Zeile | durch Aktion | Status |
|---|---|---|
| `pose_rest` | `idle_hip` | offen (nicht gesichtet) |
| `pose_hip` | `idle_hip` | offen (nicht gesichtet) |
| `draw` | `draw` | offen (nicht gesichtet) |
| `ready` | `draw` | offen (nicht gesichtet) |
| `holster` | `holster` | offen (nicht gesichtet) |
| `pose_aim` | `aim_in` | offen (nicht gesichtet) |
| `tr_hip_aim` | `aim_in` | offen (nicht gesichtet) |
| `tr_aim_hip` | `aim_out` | offen (nicht gesichtet) |
| `fire_auto` | `fire_ads` | offen (nicht gesichtet) |
| `recoil_mech` | `fire_hip` | offen (nicht gesichtet) |
| `recoil_camera` | `fire_hip` | offen (nicht gesichtet) |
| `reload_partial` | `reload_tactical` | offen (nicht gesichtet) |
| `reload_feed` | `reload_tactical` | offen (nicht gesichtet) |
| `reload_empty` | `reload_empty` | offen (nicht gesichtet) |
| `cycle` | `reload_empty` | offen (nicht gesichtet) |
| `inspect` | `inspect` | offen (nicht gesichtet) |
| `inspect_return` | `inspect` | offen (nicht gesichtet) |
| `sprint_in` | `sprint` | offen (nicht gesichtet) |
| `sprint_loop` | `sprint` | offen (nicht gesichtet) |
| `sprint_out` | `sprint` | offen (nicht gesichtet) |
| `pose_lowered` | `lowered` | offen (nicht gesichtet) |
| `tr_lowered_return` | `lowered` | offen (nicht gesichtet) |
| `move_walk` | `walk` | offen (nicht gesichtet) |
| `sway` | `walk` | offen (nicht gesichtet) |
| `crouch` | `crouch` | offen (nicht gesichtet) |
| `jump_start` | `jump_land` | offen (nicht gesichtet) |
| `air` | `jump_land` | offen (nicht gesichtet) |
| `land` | `jump_land` | offen (nicht gesichtet) |
| `tr_sprint_aim` | `sprint_to_aim` | offen (nicht gesichtet) |
| `tr_sprint_fire` | `sprint_to_fire` | offen (nicht gesichtet) |
| `tr_draw_aimheld` | `draw_aim` | offen (nicht gesichtet) |
| `tr_reload_switch` | `reload_to_switch` | offen (nicht gesichtet) |
| `switch` | `reload_to_switch` | offen (nicht gesichtet) |

Clips: `~/Library/Caches/CubeEscapeBallon/evidence/clips/ego_<waffe>_<aktion>.mp4`; Kontaktbögen `…/evidence/ego_<waffe>_<aktion>.png`; Szene `…/out/<waffe>/ego/<waffe>_ego.blend`.
