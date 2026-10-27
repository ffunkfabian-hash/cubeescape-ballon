<!-- erzeugt von tools/make_ego.py docs – nicht von Hand ändern -->

# Ego-Haltungen und Aktionen

Eigenes Roboterarm-Rig (`basic/arms/robot_arm.py`) und Ego-Daten (`basic/arms/ego.py`), getrennt von Toolgen und Cube Escape. Kamera 75° horizontal (16:9), 30 fps, Kameraraum: rechts −X, vorn −Y, oben +Z. Herkunft: **T** Toolgen-Startwert, **M** gemessen an Destiny 2, **E** entworfen, **S** Sekundärquelle (Menü, Datenbank). Handgelenk-Ziel 45°, Grenze 55° (Toolgen).

Spielbare Waffen (Taste 1 = BASIC-01-v2.1, 2 = BASIC-06-v2.1, 3 = BASIC-03-v2.1, 4 = BASIC-02-v2.1, 5 = BASIC-T01-v2.1). Haltungen, Dauer und Spielwerte je Klasse aus `ego.CLASSES` (Entscheidungsliste Schritt 6); was eine Klasse nicht nennt, gilt wie bei der Automatik.

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
| Haltung `hip` | Socket_Hand [-0.19, -0.42, -0.23], Ziel [0.02, -3.0, -0.2], Rollen 6° | M Destiny-Hüfte lange Waffen: Mündung x 54–59 / y 60–71 % (Motiongen huefte › 4, Entscheidungsliste 2.1 A); Destiny-Scout Tone Patrol Mündung ≈ 57/63, Call to Serve 58/61 (Motiongen destiny2 › 3, huefte); Lage E wie die Automatik: am Scout gerechnet Mündung 57,0/62,9 %, Okular 24 pp rechts der Mündung (Band 7–34) (Haltung POSES['hip'] unverändert) |
| Haltung `sprint` | Socket_Hand [-0.1, -0.34, -0.23], Ziel [1.2, -1.6, -0.55], Rollen -35° | E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-Scout-Sprint nicht gemessen (Motiongen destiny2 › Glidepath: kein Sprint-Clip) (Haltung POSES['sprint'] unverändert) |
| Dauer `aim_in` | 7 Bilder bei 30/s (0.233 s) | Scout bei Destiny nur grob gemessen: Tone Patrol ≈ 22 Bilder (0,37 s, Bestand, „vom Nachbartyp übertragen“), Patron of Lost Causes 0,20–0,25 s = 12–15 Bilder [M] (Motiongen destiny2 › Glidepath, visiere › v-d2-scout); dazwischen und zwischen Scharfschütze (15 Bilder bis ruhig) und Impuls (20) → E 17 Bilder bei 60/s erste Bewegung → Ruhe, am Unity-Bild gemessen; aim_out M Destiny-Scout ADS aus → Hüfte 0,17 s (Dead Man's Tale, Motiongen auswertung › V04) = 5 Bilder bei 30/s |
| Dauer `aim_out` | 5 Bilder bei 30/s (0.167 s) | Scout bei Destiny nur grob gemessen: Tone Patrol ≈ 22 Bilder (0,37 s, Bestand, „vom Nachbartyp übertragen“), Patron of Lost Causes 0,20–0,25 s = 12–15 Bilder [M] (Motiongen destiny2 › Glidepath, visiere › v-d2-scout); dazwischen und zwischen Scharfschütze (15 Bilder bis ruhig) und Impuls (20) → E 17 Bilder bei 60/s erste Bewegung → Ruhe, am Unity-Bild gemessen; aim_out M Destiny-Scout ADS aus → Hüfte 0,17 s (Dead Man's Tale, Motiongen auswertung › V04) = 5 Bilder bei 30/s |
| Zielfernrohr im Zielen | aus: scope_strap, scope_tube, scope_eyepiece, scope_eye_trim, scope_ocular_glass, scope_turret, scope_turret_w (Socket_Eye < 60 mm) | E: Okular bis an die Nahebene sichtbar (Augenabstand Okularende 30 mm + near 30 mm), danach Linsenbild; Destiny-Scharfschütze: Okular füllt das Bild 4 Bilder, Linse nach dem Modell (Motiongen destiny2 › 2, Entscheidungsliste 1d) |
| Mündungsfeuer | 33 ms | M Destiny: 1–2 Bilder bei 60/s, Kern klein, Seitenflammen breiter, Zielen Automatik ≈ 20 % der Öffnung (Motiongen muendung › 6, Entscheidungsliste 5.3 A); Maße und Farben E (Stil v2.1) |
| Hülsen | rifle (42 × 9.6 mm) | E: Auswurffenster rechts im Einteilgehäuse (port_cover), Hülse nach rechts, etwas hoch und vorn (wie BASIC-01); Bahn: M Destiny: Hülse im 1. Blitzbild oder 1 Bild danach, rechts/rechts unten (Motiongen muendung › 6, Entscheidungsliste 5d/5.4 A); Geschwindigkeit, Drehung, Lebensdauer E |
| Rückstoß | ego.RECOIL (gemeinsam) | übertragen von der Automatik: Säule 1 % H je Schuss, im Zielen wandert die Welt (5.1 A / 5.2 A); Destiny-Scout Tone Patrol: kräftiger Einzelimpuls, Rest wächst vor den Folgeschüssen, im Zielen fünf Schüsse ≈ 6 % H [M] (Motiongen rueckstoss › 4) – hier dieselbe Säule je Schuss, Salve = Schüsse im Abstand ≤ 1,5 × 60/rpm |
| Sprint-Frequenz | 3,16 / 1,58 Hz (gemeinsam) | M Destiny Automatik/Handfeuerwaffe, für alle Klassen bis zu neuen Messungen (3c) |
| Griffe | grip, support, mag, charge | Modul-Feld EGO_GRIPS |
| Live-Teile | trigger = trigger, bolt = bolt, port = port_cover | Modul-Feld EGO_LIVE |

### Haltungen

| Haltung | Socket_Hand (m) | Handgelenk max | Herkunft |
|---|---|---|---|
| `hip` | [-0.19, -0.42, -0.23] | 25.7° | M Destiny-Hüfte lange Waffen: Mündung x 54–59 / y 60–71 % (Motiongen huefte › 4, Entscheidungsliste 2.1 A); Destiny-Scout Tone Patrol Mündung ≈ 57/63, Call to Serve 58/61 (Motiongen destiny2 › 3, huefte); Lage E wie die Automatik: am Scout gerechnet Mündung 57,0/62,9 %, Okular 24 pp rechts der Mündung (Band 7–34) (Haltung POSES['hip'] unverändert) |
| `ads` | [0.0, -0.018, -0.161] | 28.0° | Visier-Standard v2: Socket_Eye ist der Augenpunkt, liegt in der Kamera; Waffenmodell ungezoomt, Welt zoomt je Klasse |
| `sprint` | [-0.1, -0.34, -0.23] | 34.9° | E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-Scout-Sprint nicht gemessen (Motiongen destiny2 › Glidepath: kein Sprint-Clip) (Haltung POSES['sprint'] unverändert) |
| `lowered` | [-0.17, -0.38, -0.25] | 36.8° | E |
| `crouch` | [-0.18, -0.41, -0.245] | 26.1° | E (wie hip versetzt, 0.15 mit hip gesenkt) |
| `air` | [-0.19, -0.42, -0.215] | nur in Aktionen geprüft | E (wie hip versetzt, 0.15 mit hip gesenkt) |
| `holstered` | [-0.24, -0.25, -0.62] | nur in Aktionen geprüft | E (unter dem Bild) |
| `reload` | [-0.07, -0.34, -0.135] | 16.6° | T Reload roll −20/pitch 12, für Destiny-Anmutung verstärkt (E) |
| `inspect_l` | [-0.06, -0.36, -0.16] | 24.9° | E (Ego-Seite zeigt zur Kamera) |
| `inspect_r` | [-0.1, -0.36, -0.12] | 41.2° | E (Oberseite und rechte Seite) |

### Aktionen

| Aktion | Beschreibung | Bilder | Marker (Bild) | Handgelenk max | Clip | Sichtung | Herkunft |
|---|---|---|---|---|---|---|---|
| `idle_hip` | Ruhe an der Hüfte (Atmen) | 75 (2.50 s) | – | 25.9° | ego_BASIC-03-v2.1_idle_hip.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz | E |
| `draw` | Ziehen | 25 (0.83 s) | Ready (18) | 42.7° | ego_BASIC-03-v2.1_draw.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz | M Ziehen 0,23 s bis Hüfte (Auto Rifle, Q-REF) + Ausfedern E |
| `holster` | Wegstecken | 8 (0.27 s) | HandOff (1), Holstered (8) | 42.5° | ego_BASIC-03-v2.1_holster.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz | M Destiny-Wechsel: Wegstecken 0,08–0,27 s (Motiongen wechsel › 4, Entscheidungsliste 6.1 A) → 0,27 s ohne TIME_SCALE (bis 0.14: 0,60 s); Ablauf E (CE: Holster ab aktueller Stellung) |
| `aim_in` | Hüfte → Zielen | 7 (0.23 s) | Aimed (6) | 27.9° | ego_BASIC-03-v2.1_aim_in.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz; Okular wächst heran, ab Bild 6 Linsenbild (ads_hide), Ende im Zielfernrohr mit Absehen auf der Mitte | E 0,30 s (CE-Handling Auto 0,39→0,20 s); Klasse scout_rifle: 10 → 7 Bilder (Scout bei Destiny nur grob gemessen: Tone Patrol ≈ 22 Bilder (0,37 s, Bestand, „vom Nachbartyp übertragen“), Patron of Lost Causes 0,20–0,25 s = 12–15 Bilder [M] (Motiongen destiny2 › Glidepath, visiere › v-d2-scout); dazwischen und zwischen Scharfschütze (15 Bilder bis ruhig) und Impuls (20) → E 17 Bilder bei 60/s erste Bewegung → Ruhe, am Unity-Bild gemessen; aim_out M Destiny-Scout ADS aus → Hüfte 0,17 s (Dead Man's Tale, Motiongen auswertung › V04) = 5 Bilder bei 30/s) |
| `aim_out` | Zielen → Hüfte | 5 (0.17 s) | Ready (5) | 28.0° | ego_BASIC-03-v2.1_aim_out.mp4 | geprüft: Ego-Clip 0.20 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-03-v2.1_<aktion>.png); Haltungen der Automatik, Stützhand underhand unter dem langen Handschutz | E; Klasse scout_rifle: 8 → 5 Bilder (Scout bei Destiny nur grob gemessen: Tone Patrol ≈ 22 Bilder (0,37 s, Bestand, „vom Nachbartyp übertragen“), Patron of Lost Causes 0,20–0,25 s = 12–15 Bilder [M] (Motiongen destiny2 › Glidepath, visiere › v-d2-scout); dazwischen und zwischen Scharfschütze (15 Bilder bis ruhig) und Impuls (20) → E 17 Bilder bei 60/s erste Bewegung → Ruhe, am Unity-Bild gemessen; aim_out M Destiny-Scout ADS aus → Hüfte 0,17 s (Dead Man's Tale, Motiongen auswertung › V04) = 5 Bilder bei 30/s) |
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
| Haltung `hip` | Socket_Hand [-0.17, -0.42, -0.214], Ziel [0.07, -3.0, -0.184], Rollen 6° | M Destiny-Hüfte lange Waffen: Mündung x 54–59 / y 60–71 % (Motiongen huefte › 4, Entscheidungsliste 2.1 A); Destiny-Impuls Gridskipper Mündung ≈ 57/61 (Motiongen destiny2 › z-gridskipper-salve); Lage E, gerechnet auf Mündung 57,9/63,6 % (Automatik-Hüfte am Impuls: 59,7/65,6) |
| Haltung `sprint` | Socket_Hand [-0.1, -0.34, -0.23], Ziel [1.2, -1.6, -0.55], Rollen -35° | E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-Impuls-Sprint nicht gemessen (Haltung POSES['sprint'] unverändert) |
| Haltung `crouch` | Socket_Hand [-0.16, -0.41, -0.229], Rollen 9° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `air` | Socket_Hand [-0.17, -0.42, -0.199], Rollen 4° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `lowered` | Socket_Hand [-0.15, -0.38, -0.234], Rollen 10° | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| Mündungsfeuer | 33 ms | M Destiny: 1–2 Bilder bei 60/s, Kern klein, Seitenflammen breiter, Zielen Automatik ≈ 20 % der Öffnung (Motiongen muendung › 6, Entscheidungsliste 5.3 A); Maße und Farben E (Stil v2.1) |
| Hülsen | rifle (42 × 9.6 mm) | E: Auswurffenster rechts im Oberen Gehäuse (port_cover f 22–74), Hülse nach rechts, etwas hoch und vorn (wie BASIC-01); Bahn: M Destiny: Hülse im 1. Blitzbild oder 1 Bild danach, rechts/rechts unten (Motiongen muendung › 6, Entscheidungsliste 5d/5.4 A); Geschwindigkeit, Drehung, Lebensdauer E |
| Rückstoß | ego.RECOIL (gemeinsam) | übertragen von der Automatik: Säule 1 % H je Schuss, im Zielen wandert die Welt (5.1 A / 5.2 A); Destiny-Impuls Gridskipper: Stufe ≈ 4 pp H je Salve, Erholung in der Pause, im Zielen Welt ≈ 5 pp H, Visier < 1 pp [M] (Motiongen rueckstoss › r-d2-gridskipper) – Bahnstufe der Klasse, zweistufig |
| Sprint-Frequenz | 3,16 / 1,58 Hz (gemeinsam) | M Destiny Automatik/Handfeuerwaffe, für alle Klassen bis zu neuen Messungen (3c) |
| Griffe | grip, support, mag, charge | Modul-Feld EGO_GRIPS |
| Live-Teile | trigger = trigger, bolt = bolt_carrier, port = port_cover | Modul-Feld EGO_LIVE |

### Haltungen

| Haltung | Socket_Hand (m) | Handgelenk max | Herkunft |
|---|---|---|---|
| `hip` | [-0.17, -0.42, -0.214] | 25.6° | M Destiny-Hüfte lange Waffen: Mündung x 54–59 / y 60–71 % (Motiongen huefte › 4, Entscheidungsliste 2.1 A); Destiny-Impuls Gridskipper Mündung ≈ 57/61 (Motiongen destiny2 › z-gridskipper-salve); Lage E, gerechnet auf Mündung 57,9/63,6 % (Automatik-Hüfte am Impuls: 59,7/65,6) |
| `ads` | [0.0, -0.0616, -0.164] | 28.0° | Visier-Standard v2: Socket_Eye ist der Augenpunkt, liegt in der Kamera; Waffenmodell ungezoomt, Welt zoomt je Klasse |
| `sprint` | [-0.1, -0.34, -0.23] | 34.9° | E nach 3.2 A „Gewehre tief und quer wie heute“: Trageform der Automatik; Destiny-Impuls-Sprint nicht gemessen (Haltung POSES['sprint'] unverändert) |
| `lowered` | [-0.15, -0.38, -0.234] | 36.7° | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| `crouch` | [-0.16, -0.41, -0.229] | 26.0° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `air` | [-0.17, -0.42, -0.199] | nur in Aktionen geprüft | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| `holstered` | [-0.24, -0.25, -0.62] | nur in Aktionen geprüft | E (unter dem Bild) |
| `reload` | [-0.07, -0.34, -0.135] | 16.6° | T Reload roll −20/pitch 12, für Destiny-Anmutung verstärkt (E) |
| `inspect_l` | [-0.06, -0.36, -0.16] | 24.9° | E (Ego-Seite zeigt zur Kamera) |
| `inspect_r` | [-0.1, -0.36, -0.12] | 41.2° | E (Oberseite und rechte Seite) |

### Aktionen

| Aktion | Beschreibung | Bilder | Marker (Bild) | Handgelenk max | Clip | Sichtung | Herkunft |
|---|---|---|---|---|---|---|---|
| `idle_hip` | Ruhe an der Hüfte (Atmen) | 75 (2.50 s) | – | 25.8° | ego_BASIC-02-v2.1_idle_hip.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-02-v2.1_<aktion>.png); eigene Hüfte, übrige Haltungen der Automatik, Stützhand underhand auf dem Griffpolster; Salven 3 Schuss im Takt 2 Bilder bei 30/s, Blitz klein im Kasten, Hülse rechts | E |
| `draw` | Ziehen | 25 (0.83 s) | Ready (18) | 42.7° | ego_BASIC-02-v2.1_draw.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-02-v2.1_<aktion>.png); eigene Hüfte, übrige Haltungen der Automatik, Stützhand underhand auf dem Griffpolster; Salven 3 Schuss im Takt 2 Bilder bei 30/s, Blitz klein im Kasten, Hülse rechts | M Ziehen 0,23 s bis Hüfte (Auto Rifle, Q-REF) + Ausfedern E |
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
| Kadenz | 240/min | Cube Escape (Q-CE-14/15): Linksklick Portal A (Cyan #1AD9FF), Rechtsklick Portal B (Orange #FF7314), Abklingzeit 0,25 s → 240/min, Reichweite 24 m, ohne Streuung (Sichtlinie zum Fadenkreuz), Munition keine (magazine 0 = unbegrenzt); Ring je Schuss 120° in 10 Bildern bei 30/s (Modul t01 fire_a/fire_b), Richtung je Portal; ohne Mündungsfeuer und ohne Bahnstufe (E: Werkzeug, Rückmeldung über Ring und Treffermarke in Portalfarbe) |
| Magazin | 0 | Cube Escape (Q-CE-14/15): Linksklick Portal A (Cyan #1AD9FF), Rechtsklick Portal B (Orange #FF7314), Abklingzeit 0,25 s → 240/min, Reichweite 24 m, ohne Streuung (Sichtlinie zum Fadenkreuz), Munition keine (magazine 0 = unbegrenzt); Ring je Schuss 120° in 10 Bildern bei 30/s (Modul t01 fire_a/fire_b), Richtung je Portal; ohne Mündungsfeuer und ohne Bahnstufe (E: Werkzeug, Rückmeldung über Ring und Treffermarke in Portalfarbe) |
| Feuerart | `single` – Einzelschuss je Klick (Werkzeug) | Spec (META fire, data/specs); Unity: gameplay.fire_mode (0.20) |
| Weltzoom im Zielen | kein Zielen (Werkzeug ohne Visier) | M Glidepath (Entscheidungsliste 1.2 A, basic/reticles.py › CLASS_ZOOM) |
| Hüft-Fadenkreuz | ring_dot 4.5 % H | entworfen (Werkzeug, Portal 2 / Cube Escape) (4.1 A / 4.2 A, basic/reticles.py › HIP) |
| Sprint-Fadenkreuz | aus | basic/reticles.py › HIP.sprint (4.1 A) |
| Bedienung | Portal A Linksklick (#1AD9FF, Ring im Uhrzeigersinn); Portal B Rechtsklick (#FF7314, Ring gegen den Uhrzeigersinn); kein Zielen, kein Nachladen; Ring 120° in 0.333 s; Reichweite 24 m | Werkzeug der Familie (0.22 „Volley“): Hüfte nach Portal 2 (M) und Familienmaßen, Sprint als Klasse „Werkzeug“ E; Bedienung Linksklick A / Rechtsklick B ohne Zielen (Nutzer 27.10.2026 über Sightline: „A“ – „Linksklick = Portal A …, Rechtsklick = Portal B …, kein Zielen …, Abklingzeit 0,25 s als Datenfeld“; Präzision X zurückgestellt, docs/erweiterungen.md) |
| Ohne | Aktionen `aim_in`, `aim_out`, `fire_hip`, `fire_ads`, `reload_tactical`, `reload_empty`, `sprint_to_aim`, `draw_aim`, `reload_to_switch`; Haltungen `ads`, `reload` | Werkzeug ohne Visier und Magazin (0.17): kein Zielen, kein Nachladen; Feuer als fire_a/fire_b (Portale) |
| Bahnstufe je Schuss | 0.00 % H | Cube Escape (Q-CE-14/15): Linksklick Portal A (Cyan #1AD9FF), Rechtsklick Portal B (Orange #FF7314), Abklingzeit 0,25 s → 240/min, Reichweite 24 m, ohne Streuung (Sichtlinie zum Fadenkreuz), Munition keine (magazine 0 = unbegrenzt); Ring je Schuss 120° in 10 Bildern bei 30/s (Modul t01 fire_a/fire_b), Richtung je Portal; ohne Mündungsfeuer und ohne Bahnstufe (E: Werkzeug, Rückmeldung über Ring und Treffermarke in Portalfarbe) |
| Haltung `hip` | Socket_Hand [-0.16, -0.4, -0.24], Ziel [1.4, -3.0, 0.0], Rollen -20° | M Portal-2-Portalkanone: rechts unten, vorderes Rohrende ≈ 57/75 %, beim Gehen 54–63/68–75 %, Rohr von rechts unten nach links oben (cubeescape-reference/docs/portal2.md › weißes Modell); Lage E, gerechnet auf Achskrone 56,9/71,2 %; quer gestellt, damit die linke Flanke beide Kerne zeigt (Nutzer 27.10.2026: „Schade dass man von der Portal Gun die Farb-Elemente nicht sieht“; von vier Varianten c14: Kern A und B sichtbar, Achskrone im Band); Kerbe (Leitkante) rechts im Bild; Stützhand am Vordergriff unter der Unterlippe |
| Haltung `sprint` | Socket_Hand [-0.1, -0.34, -0.22], Ziel [0.6, -2.1, -0.4], Rollen 30° | E (Klasse Werkzeug, in der Entscheidungsliste nicht gemessen; Portal 2 ohne eigene Sprintpose): Trageform der Kurzwaffen nach 3.2 A (MP: tief, nach links gerollt, Mündung ≈ 43/80 %), Rollen +30° statt +40° wegen der breiten Eischale; gerechnet Achskrone 44,3/80,4 % |
| Haltung `crouch` | Socket_Hand [-0.15, -0.39, -0.255], Rollen -17° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `air` | Socket_Hand [-0.16, -0.4, -0.225], Rollen -22° | wie E (wie hip versetzt, 0.15 mit hip gesenkt), an der Klassen-Hüfte (FOLLOW_HIP) |
| Haltung `lowered` | Socket_Hand [-0.14, -0.36, -0.26], Rollen -16° | wie E, an der Klassen-Hüfte (FOLLOW_HIP) |
| Mündungsfeuer | keins (Werkzeug) | Cube Escape (Q-CE-14/15): Linksklick Portal A (Cyan #1AD9FF), Rechtsklick Portal B (Orange #FF7314), Abklingzeit 0,25 s → 240/min, Reichweite 24 m, ohne Streuung (Sichtlinie zum Fadenkreuz), Munition keine (magazine 0 = unbegrenzt); Ring je Schuss 120° in 10 Bildern bei 30/s (Modul t01 fire_a/fire_b), Richtung je Portal; ohne Mündungsfeuer und ohne Bahnstufe (E: Werkzeug, Rückmeldung über Ring und Treffermarke in Portalfarbe) |
| Hülsen | keine | Waffe ohne Feld EJECT |
| Rückstoß | ego.RECOIL (gemeinsam) | übertragen von der Automatik: Säule 1 % H je Schuss, im Zielen wandert die Welt (5.1 A / 5.2 A); Werkzeug: Modellkick der Aktion (fire_a/fire_b kick 0,6), keine Bahnstufe (E; Portal 2: obere Klaue ≈ 7 % H im ersten Schussbild) |
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
| `fire_a` | Portal A (Linksklick): Ring dreht 120° im Uhrzeigersinn (von hinten) | 18 (0.60 s) | Fire (2) | 32.8° | ego_BASIC-T01-v2.1_fire_a.mp4 | geprüft: Ego-Clip 0.22 gerendert und gesichtet (Kontaktbogen evidence/ego_BASIC-T01-v2.1_<aktion>.png); fire_a Ring im, fire_b gegen den Uhrzeigersinn 120°, ohne Mündungsfeuer und Hülsen; ohne Zielen und Nachladen | Ablauf aus dem Modul (t01 ACTIONS fire_a, 0.17): Ring 2 → 12 Bilder; Kick E 0,6 (Portal 2: obere Klaue ≈ 7 % H im ersten Schussbild, portal2.md) |
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

Clips: `~/Library/Caches/CubeEscapeBallon/evidence/clips/ego_<waffe>_<aktion>.mp4`; Kontaktbögen `…/evidence/ego_<waffe>_<aktion>.png`; Szene `…/out/<waffe>/ego/<waffe>_ego.blend`.
