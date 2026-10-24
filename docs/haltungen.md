<!-- erzeugt von tools/make_docs.py – nicht von Hand ändern -->

# Haltungs- und Animationsmatrix BASIC

Je Waffe alle Standardhaltungen und -aktionen mit Status **dargestellt**, **nicht anwendbar** (mit Grund) oder **offen** (mit Lücke). Quelle: `basic/matrix.py` (Zeilen und Regeln), Waffenmodule (`ACTIONS`). „Dargestellt“ heißt hier: Waffenmechanik als Bildfolge/Clip aus dem Modell; Hände und Arme gibt es erst mit einem Toolgen-Import (offen). Maschinenlesbar: [`data/matrix.json`](../data/matrix.json).

Ebenen nach Cube Escape (Q-CE-07): Posendaten (kalibrierbare Grundhaltungen), Clip, prozedural, gemischt. Bildrate der Mechanikfolgen 30 fps, Zeitbasis Bild 0 = Auslöser.

## Übersicht

| Waffe | dargestellt | nicht anwendbar | offen | Mechanik-Clips |
|---|---|---|---|---|
| [BASIC-01](#basic-01) Automatikgewehr | 3 | 8 | 32 | reload_tactical, reload_empty, fire_auto, safety |
| [BASIC-02](#basic-02) Impulsgewehr | 3 | 8 | 32 | fire_burst, reload_empty |
| [BASIC-03](#basic-03) Scout-Gewehr | 3 | 8 | 32 | fire_semi, reload_empty |
| [BASIC-04](#basic-04) Handfeuerwaffe | 3 | 8 | 32 | fire_da, reload |
| [BASIC-05](#basic-05) Pistole | 3 | 8 | 32 | fire_semi, reload_empty |
| [BASIC-06](#basic-06) Maschinenpistole | 3 | 8 | 32 | fire_auto, reload_empty |
| [BASIC-07](#basic-07) Bogen | 0 | 15 | 34 | draw_hold_release, let_down |
| [BASIC-08](#basic-08) Schrotflinte | 3 | 8 | 32 | fire_pump, load_shell |
| [BASIC-09](#basic-09) Scharfschützengewehr | 3 | 8 | 32 | fire_cycle, reload_empty |
| [BASIC-10](#basic-10) Fusionsgewehr | 5 | 6 | 32 | charge_fire, charge_cancel, reload |
| [BASIC-11](#basic-11) Lineares Fusionsgewehr | 4 | 6 | 33 | charge_fire, reload |
| [BASIC-12](#basic-12) Spurgewehr | 2 | 9 | 32 | beam, reload |
| [BASIC-13](#basic-13) Granatwerfer (Kipplauf) | 1 | 9 | 33 | fire, reload |
| [BASIC-14](#basic-14) Raketenwerfer | 1 | 9 | 33 | fire, reload |
| [BASIC-15](#basic-15) Maschinengewehr | 1 | 8 | 34 | fire_auto, reload |
| [BASIC-16](#basic-16) Schwert | 0 | 19 | 30 | guard_charge |
| [BASIC-17](#basic-17) Glefe | 3 | 9 | 36 | fire, shield, reload |

## Übergänge und Unterbrechungen (gemeinsam, Zuordnung je Waffe unten)

| ID | Start → Ende | Auslöser | Priorität | erlaubte Unterbrechung | Ereignisse | Dauer (Quelle) |
|---|---|---|---|---|---|---|
| tr_sprint_aim | Sprint → Zielen | Zieltaste im Sprint | ADS > Sprint | Sprint endet sofort | SprintOut, Aimed | vorgeschlagen 0,25–0,35 s (ADS-Messungen Q-REF) |
| tr_sprint_fire | Sprint → Feuer | Abzug im Sprint | Fire > Sprint | Sprint endet; Feuer nach SprintOut | SprintOut, Fire | vorgeschlagen 0,15–0,25 s |
| tr_draw_aimheld | Ziehen bei gehaltenem Zielen | Wechsel mit gehaltener Zieltaste | Draw > ADS | Draw nicht unterbrechbar; ADS danach | Ready, Aimed | Ziehen gemessen 0,18–0,60 s je Typ (Q-REF) |
| tr_reload_switch | Nachladen → Wechsel | Waffenwechsel während Reload | Holster/Draw > Reload | Reload bricht ab (CancelReason Switch) | MagOut ohne MagIn → Magazin bleibt draußen (Regel offen) | Holster ab aktueller Stellung (Q-CE-06) |
| tr_reload_cancel | Erlaubter Nachladeabbruch | Sprint oder Wechsel | Reload bis MagIn geschützt | nach MagIn gilt Nachladen als erfolgt | MagIn, Chamber | abhängig vom Reload-Clip |
| tr_charge_cancel | Aufladen abbrechen | Abzug loslassen vor Vollladung | Fire | jederzeit vor Auslösen | charge_start, cancel | Fusion: Laden bis Strahl 0,52–0,87 s (Q-REF) |
| tr_inspect_cancel | Betrachten abbrechen | jede Eingabe | Inspect niedrigste Priorität | sofort | End | vorgeschlagen 0,15 s |
| tr_fire_move | Feuer während Bewegung | Abzug beim Gehen | Fire > Walk | Bob gedämpft | Fire | prozedural |
| tr_fire_air | Feuer in der Luft | Abzug in Luftphase | Fire > Air | Landefeder läuft weiter | Fire | prozedural |
| tr_wall | Wandabsenkung und Rückkehr | Abstand zur Wand unter Waffenlänge | Lowered | Feuer gesperrt | Lowered | vorgeschlagen 0,2 s |
| tr_quick_switch | Schneller erneuter Wechsel | zweiter Wechsel während Draw | Holster/Draw | Holster ab aktueller Stellung | Holstered, Ready | Waffenwechsel V06/V07 (Q-REF) |
| tr_view | Ego-/ISO-Wechsel | Ansichtswechsel | View | CancelReason View | – | Schwert: 0,15 + 0,33 s (Q-REF Sword) |

## BASIC-01

Automatikgewehr „Formstudie 01“ · CE-Profilklasse: rifle · Munitionszufuhr: Magazin

| Zeile | Bereich | Ebene | Status | Detail |
|---|---|---|---|---|
| `pose_rest` Ruhehaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_hip` Hüftfeuerhaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_aim` Zielhaltung (Visier/Zielfernrohr) | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_hip_aim` Hüfte → Zielen | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_aim_hip` Zielen → Hüfte | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `pose_lowered` Gesenkte Haltung / Wandnähe | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_lowered_return` Rückkehr aus gesenkter Haltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_walk` Gehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_strafe` Seitwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_back` Rückwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_in` Sprintbeginn | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `sprint_loop` Sprintschleife | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_out` Sprintende | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `crouch` Ducken | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `crouch_move` Geduckte Bewegung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `jump_start` Sprungbeginn | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `air` Luftphase | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `land` Landung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `slide` Rutschen | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Walk, Sprint, Crouch, Air, Lowered; Q-CE-07) |
| `climb` Klettern | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Q-CE-07) |
| `sway` Nachschwingen beim Umsehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `inertia` Bewegungsträgheit | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `regrip` Griffkorrektur | Bewegung | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `draw` Ziehen | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `ready` Einsatzbereitschaft | Aktion | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `holster` Wegstecken | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `switch` Waffenwechsel | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `fire_single` Einzelschuss | Aktion | Clip | **nicht anwendbar** | anderer Feuermodus (Salve, Dauerfeuer, Aufladen oder Nahkampf) |
| `fire_burst` Salve | Aktion | Clip | **nicht anwendbar** | nur das Impulsgewehr feuert Salven (Burst-Rahmen anderer Typen zurückgestellt, EXT-12) |
| `fire_auto` Dauerfeuer / Dauerstrahl | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion fire_auto (Clip <EVIDENCE>/clips/BASIC-01_<aktion>.mp4, gesichtet laut data/review.json) |
| `recoil_mech` Rückstoß und Mechanik, Rückkehr | Aktion | prozedural | **offen** | Mechanik dargestellt (fire_auto); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `recoil_camera` Kamera-Feedback (getrennt) | Aktion | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `charge` Aufladen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ (Bogen: Auszug in eigenen Zeilen) |
| `charge_hold` Ladung halten | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_release` Ladung auslösen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_cancel` Aufladen abbrechen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `reload_partial` Nachladen mit Restmunition | Aktion | Clip | **offen** | Mechanik dargestellt (reload_tactical); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `reload_empty` Nachladen aus leerem Zustand | Aktion | Clip | **offen** | Mechanik dargestellt (reload_empty); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `reload_feed` Munitionszufuhr (Magazin, Trommel, Gurt, Zelle, Einzelpatrone) | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion reload_tactical, reload_empty (Clip <EVIDENCE>/clips/BASIC-01_<aktion>.mp4, gesichtet laut data/review.json) |
| `cycle` Repetieren / Spannen / Verschluss / Auswurf | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion reload_empty (Clip <EVIDENCE>/clips/BASIC-01_<aktion>.mp4, gesichtet laut data/review.json) |
| `inspect` Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `inspect_return` Rückkehr aus Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `displace` Verdrängung (Interaktion, Nahkampf, Fähigkeit) | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_sprint_aim` Sprint → Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,25–0,35 s (ADS-Messungen Q-REF) |
| `tr_sprint_fire` Sprint → Feuer | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15–0,25 s |
| `tr_draw_aimheld` Ziehen bei gehaltenem Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Ziehen gemessen 0,18–0,60 s je Typ (Q-REF) |
| `tr_reload_switch` Nachladen → Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Holster ab aktueller Stellung (Q-CE-06) |
| `tr_reload_cancel` Erlaubter Nachladeabbruch | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: abhängig vom Reload-Clip |
| `tr_charge_cancel` Aufladen abbrechen | Übergang | gemischt | **nicht anwendbar** | kein Nachladen/Aufladen bzw. kein Feuer bei diesem Typ |
| `tr_inspect_cancel` Betrachten abbrechen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15 s |
| `tr_fire_move` Feuer während Bewegung | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_fire_air` Feuer in der Luft | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_wall` Wandabsenkung und Rückkehr | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,2 s |
| `tr_quick_switch` Schneller erneuter Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Waffenwechsel V06/V07 (Q-REF) |
| `tr_view` Ego-/ISO-Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Schwert: 0,15 + 0,33 s (Q-REF Sword) |

## BASIC-02

Impulsgewehr „Impuls“ · CE-Profilklasse: rifle · Munitionszufuhr: Magazin

| Zeile | Bereich | Ebene | Status | Detail |
|---|---|---|---|---|
| `pose_rest` Ruhehaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_hip` Hüftfeuerhaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_aim` Zielhaltung (Visier/Zielfernrohr) | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_hip_aim` Hüfte → Zielen | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_aim_hip` Zielen → Hüfte | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `pose_lowered` Gesenkte Haltung / Wandnähe | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_lowered_return` Rückkehr aus gesenkter Haltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_walk` Gehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_strafe` Seitwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_back` Rückwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_in` Sprintbeginn | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `sprint_loop` Sprintschleife | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_out` Sprintende | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `crouch` Ducken | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `crouch_move` Geduckte Bewegung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `jump_start` Sprungbeginn | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `air` Luftphase | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `land` Landung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `slide` Rutschen | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Walk, Sprint, Crouch, Air, Lowered; Q-CE-07) |
| `climb` Klettern | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Q-CE-07) |
| `sway` Nachschwingen beim Umsehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `inertia` Bewegungsträgheit | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `regrip` Griffkorrektur | Bewegung | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `draw` Ziehen | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `ready` Einsatzbereitschaft | Aktion | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `holster` Wegstecken | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `switch` Waffenwechsel | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `fire_single` Einzelschuss | Aktion | Clip | **nicht anwendbar** | anderer Feuermodus (Salve, Dauerfeuer, Aufladen oder Nahkampf) |
| `fire_burst` Salve | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion fire_burst (Clip <EVIDENCE>/clips/BASIC-02_<aktion>.mp4, gesichtet laut data/review.json) |
| `fire_auto` Dauerfeuer / Dauerstrahl | Aktion | Clip | **nicht anwendbar** | kein Dauerfeuer bei diesem Typ |
| `recoil_mech` Rückstoß und Mechanik, Rückkehr | Aktion | prozedural | **offen** | Mechanik dargestellt (fire_burst); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `recoil_camera` Kamera-Feedback (getrennt) | Aktion | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `charge` Aufladen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ (Bogen: Auszug in eigenen Zeilen) |
| `charge_hold` Ladung halten | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_release` Ladung auslösen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_cancel` Aufladen abbrechen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `reload_partial` Nachladen mit Restmunition | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `reload_empty` Nachladen aus leerem Zustand | Aktion | Clip | **offen** | Mechanik dargestellt (reload_empty); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `reload_feed` Munitionszufuhr (Magazin, Trommel, Gurt, Zelle, Einzelpatrone) | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion reload_empty (Clip <EVIDENCE>/clips/BASIC-02_<aktion>.mp4, gesichtet laut data/review.json) |
| `cycle` Repetieren / Spannen / Verschluss / Auswurf | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion reload_empty (Clip <EVIDENCE>/clips/BASIC-02_<aktion>.mp4, gesichtet laut data/review.json) |
| `inspect` Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `inspect_return` Rückkehr aus Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `displace` Verdrängung (Interaktion, Nahkampf, Fähigkeit) | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_sprint_aim` Sprint → Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,25–0,35 s (ADS-Messungen Q-REF) |
| `tr_sprint_fire` Sprint → Feuer | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15–0,25 s |
| `tr_draw_aimheld` Ziehen bei gehaltenem Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Ziehen gemessen 0,18–0,60 s je Typ (Q-REF) |
| `tr_reload_switch` Nachladen → Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Holster ab aktueller Stellung (Q-CE-06) |
| `tr_reload_cancel` Erlaubter Nachladeabbruch | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: abhängig vom Reload-Clip |
| `tr_charge_cancel` Aufladen abbrechen | Übergang | gemischt | **nicht anwendbar** | kein Nachladen/Aufladen bzw. kein Feuer bei diesem Typ |
| `tr_inspect_cancel` Betrachten abbrechen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15 s |
| `tr_fire_move` Feuer während Bewegung | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_fire_air` Feuer in der Luft | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_wall` Wandabsenkung und Rückkehr | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,2 s |
| `tr_quick_switch` Schneller erneuter Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Waffenwechsel V06/V07 (Q-REF) |
| `tr_view` Ego-/ISO-Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Schwert: 0,15 + 0,33 s (Q-REF Sword) |

## BASIC-03

Scout-Gewehr „Fernblick“ · CE-Profilklasse: rifle · Munitionszufuhr: Magazin

| Zeile | Bereich | Ebene | Status | Detail |
|---|---|---|---|---|
| `pose_rest` Ruhehaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_hip` Hüftfeuerhaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_aim` Zielhaltung (Visier/Zielfernrohr) | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_hip_aim` Hüfte → Zielen | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_aim_hip` Zielen → Hüfte | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `pose_lowered` Gesenkte Haltung / Wandnähe | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_lowered_return` Rückkehr aus gesenkter Haltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_walk` Gehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_strafe` Seitwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_back` Rückwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_in` Sprintbeginn | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `sprint_loop` Sprintschleife | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_out` Sprintende | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `crouch` Ducken | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `crouch_move` Geduckte Bewegung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `jump_start` Sprungbeginn | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `air` Luftphase | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `land` Landung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `slide` Rutschen | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Walk, Sprint, Crouch, Air, Lowered; Q-CE-07) |
| `climb` Klettern | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Q-CE-07) |
| `sway` Nachschwingen beim Umsehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `inertia` Bewegungsträgheit | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `regrip` Griffkorrektur | Bewegung | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `draw` Ziehen | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `ready` Einsatzbereitschaft | Aktion | Posendaten | **offen** | Posendaten der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `holster` Wegstecken | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `switch` Waffenwechsel | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `fire_single` Einzelschuss | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion fire_semi (Clip <EVIDENCE>/clips/BASIC-03_<aktion>.mp4, gesichtet laut data/review.json) |
| `fire_burst` Salve | Aktion | Clip | **nicht anwendbar** | nur das Impulsgewehr feuert Salven (Burst-Rahmen anderer Typen zurückgestellt, EXT-12) |
| `fire_auto` Dauerfeuer / Dauerstrahl | Aktion | Clip | **nicht anwendbar** | kein Dauerfeuer bei diesem Typ |
| `recoil_mech` Rückstoß und Mechanik, Rückkehr | Aktion | prozedural | **offen** | Mechanik dargestellt (fire_semi); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `recoil_camera` Kamera-Feedback (getrennt) | Aktion | prozedural | **offen** | prozedural der CE-Klasse „rifle“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `charge` Aufladen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ (Bogen: Auszug in eigenen Zeilen) |
| `charge_hold` Ladung halten | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_release` Ladung auslösen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_cancel` Aufladen abbrechen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `reload_partial` Nachladen mit Restmunition | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `reload_empty` Nachladen aus leerem Zustand | Aktion | Clip | **offen** | Mechanik dargestellt (reload_empty); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `reload_feed` Munitionszufuhr (Magazin, Trommel, Gurt, Zelle, Einzelpatrone) | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion reload_empty (Clip <EVIDENCE>/clips/BASIC-03_<aktion>.mp4, gesichtet laut data/review.json) |
| `cycle` Repetieren / Spannen / Verschluss / Auswurf | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion reload_empty (Clip <EVIDENCE>/clips/BASIC-03_<aktion>.mp4, gesichtet laut data/review.json) |
| `inspect` Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `inspect_return` Rückkehr aus Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `displace` Verdrängung (Interaktion, Nahkampf, Fähigkeit) | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_sprint_aim` Sprint → Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,25–0,35 s (ADS-Messungen Q-REF) |
| `tr_sprint_fire` Sprint → Feuer | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15–0,25 s |
| `tr_draw_aimheld` Ziehen bei gehaltenem Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Ziehen gemessen 0,18–0,60 s je Typ (Q-REF) |
| `tr_reload_switch` Nachladen → Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Holster ab aktueller Stellung (Q-CE-06) |
| `tr_reload_cancel` Erlaubter Nachladeabbruch | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: abhängig vom Reload-Clip |
| `tr_charge_cancel` Aufladen abbrechen | Übergang | gemischt | **nicht anwendbar** | kein Nachladen/Aufladen bzw. kein Feuer bei diesem Typ |
| `tr_inspect_cancel` Betrachten abbrechen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15 s |
| `tr_fire_move` Feuer während Bewegung | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_fire_air` Feuer in der Luft | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_wall` Wandabsenkung und Rückkehr | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,2 s |
| `tr_quick_switch` Schneller erneuter Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Waffenwechsel V06/V07 (Q-REF) |
| `tr_view` Ego-/ISO-Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Schwert: 0,15 + 0,33 s (Q-REF Sword) |

## BASIC-04

Handfeuerwaffe „Trommel“ · CE-Profilklasse: sidearm (Vorschlag) · Munitionszufuhr: Trommel (Einzelpatronen)

| Zeile | Bereich | Ebene | Status | Detail |
|---|---|---|---|---|
| `pose_rest` Ruhehaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „sidearm (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_hip` Hüftfeuerhaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „sidearm (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_aim` Zielhaltung (Visier/Zielfernrohr) | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „sidearm (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_hip_aim` Hüfte → Zielen | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_aim_hip` Zielen → Hüfte | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `pose_lowered` Gesenkte Haltung / Wandnähe | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „sidearm (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_lowered_return` Rückkehr aus gesenkter Haltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „sidearm (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_walk` Gehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sidearm (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_strafe` Seitwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sidearm (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_back` Rückwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sidearm (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_in` Sprintbeginn | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `sprint_loop` Sprintschleife | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „sidearm (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_out` Sprintende | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `crouch` Ducken | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „sidearm (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `crouch_move` Geduckte Bewegung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sidearm (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `jump_start` Sprungbeginn | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sidearm (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `air` Luftphase | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „sidearm (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `land` Landung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sidearm (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `slide` Rutschen | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Walk, Sprint, Crouch, Air, Lowered; Q-CE-07) |
| `climb` Klettern | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Q-CE-07) |
| `sway` Nachschwingen beim Umsehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sidearm (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `inertia` Bewegungsträgheit | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sidearm (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `regrip` Griffkorrektur | Bewegung | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `draw` Ziehen | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `ready` Einsatzbereitschaft | Aktion | Posendaten | **offen** | Posendaten der CE-Klasse „sidearm (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `holster` Wegstecken | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `switch` Waffenwechsel | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `fire_single` Einzelschuss | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion fire_da (Clip <EVIDENCE>/clips/BASIC-04_<aktion>.mp4, gesichtet laut data/review.json) |
| `fire_burst` Salve | Aktion | Clip | **nicht anwendbar** | nur das Impulsgewehr feuert Salven (Burst-Rahmen anderer Typen zurückgestellt, EXT-12) |
| `fire_auto` Dauerfeuer / Dauerstrahl | Aktion | Clip | **nicht anwendbar** | kein Dauerfeuer bei diesem Typ |
| `recoil_mech` Rückstoß und Mechanik, Rückkehr | Aktion | prozedural | **offen** | prozedural der CE-Klasse „sidearm (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `recoil_camera` Kamera-Feedback (getrennt) | Aktion | prozedural | **offen** | prozedural der CE-Klasse „sidearm (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `charge` Aufladen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ (Bogen: Auszug in eigenen Zeilen) |
| `charge_hold` Ladung halten | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_release` Ladung auslösen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_cancel` Aufladen abbrechen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `reload_partial` Nachladen mit Restmunition | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `reload_empty` Nachladen aus leerem Zustand | Aktion | Clip | **offen** | Mechanik dargestellt (reload); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `reload_feed` Munitionszufuhr (Magazin, Trommel, Gurt, Zelle, Einzelpatrone) | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion reload (Clip <EVIDENCE>/clips/BASIC-04_<aktion>.mp4, gesichtet laut data/review.json) |
| `cycle` Repetieren / Spannen / Verschluss / Auswurf | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion fire_da (Clip <EVIDENCE>/clips/BASIC-04_<aktion>.mp4, gesichtet laut data/review.json) |
| `inspect` Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `inspect_return` Rückkehr aus Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `displace` Verdrängung (Interaktion, Nahkampf, Fähigkeit) | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_sprint_aim` Sprint → Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,25–0,35 s (ADS-Messungen Q-REF) |
| `tr_sprint_fire` Sprint → Feuer | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15–0,25 s |
| `tr_draw_aimheld` Ziehen bei gehaltenem Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Ziehen gemessen 0,18–0,60 s je Typ (Q-REF) |
| `tr_reload_switch` Nachladen → Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Holster ab aktueller Stellung (Q-CE-06) |
| `tr_reload_cancel` Erlaubter Nachladeabbruch | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: abhängig vom Reload-Clip |
| `tr_charge_cancel` Aufladen abbrechen | Übergang | gemischt | **nicht anwendbar** | kein Nachladen/Aufladen bzw. kein Feuer bei diesem Typ |
| `tr_inspect_cancel` Betrachten abbrechen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15 s |
| `tr_fire_move` Feuer während Bewegung | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_fire_air` Feuer in der Luft | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_wall` Wandabsenkung und Rückkehr | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,2 s |
| `tr_quick_switch` Schneller erneuter Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Waffenwechsel V06/V07 (Q-REF) |
| `tr_view` Ego-/ISO-Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Schwert: 0,15 + 0,33 s (Q-REF Sword) |

## BASIC-05

Pistole „Seitenwaffe“ · CE-Profilklasse: sidearm · Munitionszufuhr: Magazin im Griff

| Zeile | Bereich | Ebene | Status | Detail |
|---|---|---|---|---|
| `pose_rest` Ruhehaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „sidearm“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_hip` Hüftfeuerhaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „sidearm“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_aim` Zielhaltung (Visier/Zielfernrohr) | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „sidearm“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_hip_aim` Hüfte → Zielen | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_aim_hip` Zielen → Hüfte | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `pose_lowered` Gesenkte Haltung / Wandnähe | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „sidearm“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_lowered_return` Rückkehr aus gesenkter Haltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „sidearm“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_walk` Gehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sidearm“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_strafe` Seitwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sidearm“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_back` Rückwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sidearm“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_in` Sprintbeginn | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `sprint_loop` Sprintschleife | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „sidearm“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_out` Sprintende | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `crouch` Ducken | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „sidearm“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `crouch_move` Geduckte Bewegung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sidearm“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `jump_start` Sprungbeginn | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sidearm“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `air` Luftphase | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „sidearm“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `land` Landung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sidearm“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `slide` Rutschen | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Walk, Sprint, Crouch, Air, Lowered; Q-CE-07) |
| `climb` Klettern | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Q-CE-07) |
| `sway` Nachschwingen beim Umsehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sidearm“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `inertia` Bewegungsträgheit | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sidearm“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `regrip` Griffkorrektur | Bewegung | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `draw` Ziehen | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `ready` Einsatzbereitschaft | Aktion | Posendaten | **offen** | Posendaten der CE-Klasse „sidearm“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `holster` Wegstecken | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `switch` Waffenwechsel | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `fire_single` Einzelschuss | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion fire_semi (Clip <EVIDENCE>/clips/BASIC-05_<aktion>.mp4, gesichtet laut data/review.json) |
| `fire_burst` Salve | Aktion | Clip | **nicht anwendbar** | nur das Impulsgewehr feuert Salven (Burst-Rahmen anderer Typen zurückgestellt, EXT-12) |
| `fire_auto` Dauerfeuer / Dauerstrahl | Aktion | Clip | **nicht anwendbar** | kein Dauerfeuer bei diesem Typ |
| `recoil_mech` Rückstoß und Mechanik, Rückkehr | Aktion | prozedural | **offen** | Mechanik dargestellt (fire_semi); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `recoil_camera` Kamera-Feedback (getrennt) | Aktion | prozedural | **offen** | prozedural der CE-Klasse „sidearm“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `charge` Aufladen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ (Bogen: Auszug in eigenen Zeilen) |
| `charge_hold` Ladung halten | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_release` Ladung auslösen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_cancel` Aufladen abbrechen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `reload_partial` Nachladen mit Restmunition | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `reload_empty` Nachladen aus leerem Zustand | Aktion | Clip | **offen** | Mechanik dargestellt (reload_empty); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `reload_feed` Munitionszufuhr (Magazin, Trommel, Gurt, Zelle, Einzelpatrone) | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion reload_empty (Clip <EVIDENCE>/clips/BASIC-05_<aktion>.mp4, gesichtet laut data/review.json) |
| `cycle` Repetieren / Spannen / Verschluss / Auswurf | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion reload_empty (Clip <EVIDENCE>/clips/BASIC-05_<aktion>.mp4, gesichtet laut data/review.json) |
| `inspect` Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `inspect_return` Rückkehr aus Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `displace` Verdrängung (Interaktion, Nahkampf, Fähigkeit) | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_sprint_aim` Sprint → Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,25–0,35 s (ADS-Messungen Q-REF) |
| `tr_sprint_fire` Sprint → Feuer | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15–0,25 s |
| `tr_draw_aimheld` Ziehen bei gehaltenem Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Ziehen gemessen 0,18–0,60 s je Typ (Q-REF) |
| `tr_reload_switch` Nachladen → Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Holster ab aktueller Stellung (Q-CE-06) |
| `tr_reload_cancel` Erlaubter Nachladeabbruch | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: abhängig vom Reload-Clip |
| `tr_charge_cancel` Aufladen abbrechen | Übergang | gemischt | **nicht anwendbar** | kein Nachladen/Aufladen bzw. kein Feuer bei diesem Typ |
| `tr_inspect_cancel` Betrachten abbrechen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15 s |
| `tr_fire_move` Feuer während Bewegung | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_fire_air` Feuer in der Luft | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_wall` Wandabsenkung und Rückkehr | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,2 s |
| `tr_quick_switch` Schneller erneuter Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Waffenwechsel V06/V07 (Q-REF) |
| `tr_view` Ego-/ISO-Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Schwert: 0,15 + 0,33 s (Q-REF Sword) |

## BASIC-06

Maschinenpistole „Kurzläufer“ · CE-Profilklasse: submachine_gun · Munitionszufuhr: Magazin im Griff

| Zeile | Bereich | Ebene | Status | Detail |
|---|---|---|---|---|
| `pose_rest` Ruhehaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „submachine_gun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_hip` Hüftfeuerhaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „submachine_gun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_aim` Zielhaltung (Visier/Zielfernrohr) | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „submachine_gun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_hip_aim` Hüfte → Zielen | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_aim_hip` Zielen → Hüfte | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `pose_lowered` Gesenkte Haltung / Wandnähe | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „submachine_gun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_lowered_return` Rückkehr aus gesenkter Haltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „submachine_gun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_walk` Gehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „submachine_gun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_strafe` Seitwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „submachine_gun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_back` Rückwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „submachine_gun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_in` Sprintbeginn | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `sprint_loop` Sprintschleife | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „submachine_gun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_out` Sprintende | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `crouch` Ducken | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „submachine_gun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `crouch_move` Geduckte Bewegung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „submachine_gun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `jump_start` Sprungbeginn | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „submachine_gun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `air` Luftphase | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „submachine_gun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `land` Landung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „submachine_gun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `slide` Rutschen | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Walk, Sprint, Crouch, Air, Lowered; Q-CE-07) |
| `climb` Klettern | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Q-CE-07) |
| `sway` Nachschwingen beim Umsehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „submachine_gun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `inertia` Bewegungsträgheit | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „submachine_gun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `regrip` Griffkorrektur | Bewegung | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `draw` Ziehen | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `ready` Einsatzbereitschaft | Aktion | Posendaten | **offen** | Posendaten der CE-Klasse „submachine_gun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `holster` Wegstecken | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `switch` Waffenwechsel | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `fire_single` Einzelschuss | Aktion | Clip | **nicht anwendbar** | anderer Feuermodus (Salve, Dauerfeuer, Aufladen oder Nahkampf) |
| `fire_burst` Salve | Aktion | Clip | **nicht anwendbar** | nur das Impulsgewehr feuert Salven (Burst-Rahmen anderer Typen zurückgestellt, EXT-12) |
| `fire_auto` Dauerfeuer / Dauerstrahl | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion fire_auto (Clip <EVIDENCE>/clips/BASIC-06_<aktion>.mp4, gesichtet laut data/review.json) |
| `recoil_mech` Rückstoß und Mechanik, Rückkehr | Aktion | prozedural | **offen** | Mechanik dargestellt (fire_auto); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `recoil_camera` Kamera-Feedback (getrennt) | Aktion | prozedural | **offen** | prozedural der CE-Klasse „submachine_gun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `charge` Aufladen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ (Bogen: Auszug in eigenen Zeilen) |
| `charge_hold` Ladung halten | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_release` Ladung auslösen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_cancel` Aufladen abbrechen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `reload_partial` Nachladen mit Restmunition | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `reload_empty` Nachladen aus leerem Zustand | Aktion | Clip | **offen** | Mechanik dargestellt (reload_empty); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `reload_feed` Munitionszufuhr (Magazin, Trommel, Gurt, Zelle, Einzelpatrone) | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion reload_empty (Clip <EVIDENCE>/clips/BASIC-06_<aktion>.mp4, gesichtet laut data/review.json) |
| `cycle` Repetieren / Spannen / Verschluss / Auswurf | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion reload_empty (Clip <EVIDENCE>/clips/BASIC-06_<aktion>.mp4, gesichtet laut data/review.json) |
| `inspect` Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `inspect_return` Rückkehr aus Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `displace` Verdrängung (Interaktion, Nahkampf, Fähigkeit) | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_sprint_aim` Sprint → Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,25–0,35 s (ADS-Messungen Q-REF) |
| `tr_sprint_fire` Sprint → Feuer | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15–0,25 s |
| `tr_draw_aimheld` Ziehen bei gehaltenem Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Ziehen gemessen 0,18–0,60 s je Typ (Q-REF) |
| `tr_reload_switch` Nachladen → Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Holster ab aktueller Stellung (Q-CE-06) |
| `tr_reload_cancel` Erlaubter Nachladeabbruch | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: abhängig vom Reload-Clip |
| `tr_charge_cancel` Aufladen abbrechen | Übergang | gemischt | **nicht anwendbar** | kein Nachladen/Aufladen bzw. kein Feuer bei diesem Typ |
| `tr_inspect_cancel` Betrachten abbrechen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15 s |
| `tr_fire_move` Feuer während Bewegung | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_fire_air` Feuer in der Luft | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_wall` Wandabsenkung und Rückkehr | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,2 s |
| `tr_quick_switch` Schneller erneuter Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Waffenwechsel V06/V07 (Q-REF) |
| `tr_view` Ego-/ISO-Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Schwert: 0,15 + 0,33 s (Q-REF Sword) |

## BASIC-07

Bogen „Sehnenzug“ · CE-Profilklasse: keine (Bogen nicht in CE) · Munitionszufuhr: keine

| Zeile | Bereich | Ebene | Status | Detail |
|---|---|---|---|---|
| `pose_rest` Ruhehaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Bogen nicht in CE)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_hip` Hüftfeuerhaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Bogen nicht in CE)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_aim` Zielhaltung (Visier/Zielfernrohr) | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Bogen nicht in CE)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_hip_aim` Hüfte → Zielen | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_aim_hip` Zielen → Hüfte | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `pose_lowered` Gesenkte Haltung / Wandnähe | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Bogen nicht in CE)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_lowered_return` Rückkehr aus gesenkter Haltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Bogen nicht in CE)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_walk` Gehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Bogen nicht in CE)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_strafe` Seitwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Bogen nicht in CE)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_back` Rückwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Bogen nicht in CE)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_in` Sprintbeginn | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `sprint_loop` Sprintschleife | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Bogen nicht in CE)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_out` Sprintende | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `crouch` Ducken | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Bogen nicht in CE)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `crouch_move` Geduckte Bewegung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Bogen nicht in CE)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `jump_start` Sprungbeginn | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Bogen nicht in CE)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `air` Luftphase | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Bogen nicht in CE)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `land` Landung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Bogen nicht in CE)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `slide` Rutschen | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Walk, Sprint, Crouch, Air, Lowered; Q-CE-07) |
| `climb` Klettern | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Q-CE-07) |
| `sway` Nachschwingen beim Umsehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Bogen nicht in CE)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `inertia` Bewegungsträgheit | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Bogen nicht in CE)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `regrip` Griffkorrektur | Bewegung | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `draw` Ziehen | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `ready` Einsatzbereitschaft | Aktion | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Bogen nicht in CE)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `holster` Wegstecken | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `switch` Waffenwechsel | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `fire_single` Einzelschuss | Aktion | Clip | **nicht anwendbar** | anderer Feuermodus (Salve, Dauerfeuer, Aufladen oder Nahkampf) |
| `fire_burst` Salve | Aktion | Clip | **nicht anwendbar** | nur das Impulsgewehr feuert Salven (Burst-Rahmen anderer Typen zurückgestellt, EXT-12) |
| `fire_auto` Dauerfeuer / Dauerstrahl | Aktion | Clip | **nicht anwendbar** | kein Dauerfeuer bei diesem Typ |
| `recoil_mech` Rückstoß und Mechanik, Rückkehr | Aktion | prozedural | **nicht anwendbar** | Typ ohne Schusswaffenablauf (eigene Zeilen für Bogen bzw. Schwert) |
| `recoil_camera` Kamera-Feedback (getrennt) | Aktion | prozedural | **nicht anwendbar** | Typ ohne Schusswaffenablauf (eigene Zeilen für Bogen bzw. Schwert) |
| `charge` Aufladen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ (Bogen: Auszug in eigenen Zeilen) |
| `charge_hold` Ladung halten | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_release` Ladung auslösen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_cancel` Aufladen abbrechen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `reload_partial` Nachladen mit Restmunition | Aktion | Clip | **nicht anwendbar** | keine nachladbare Munition (Bogen: Pfeil, Schwert: Ladungen) |
| `reload_empty` Nachladen aus leerem Zustand | Aktion | Clip | **nicht anwendbar** | Typ ohne Schusswaffenablauf (eigene Zeilen für Bogen bzw. Schwert) |
| `reload_feed` Munitionszufuhr (Magazin, Trommel, Gurt, Zelle, Einzelpatrone) | Aktion | Clip | **nicht anwendbar** | Typ ohne Schusswaffenablauf (eigene Zeilen für Bogen bzw. Schwert) |
| `cycle` Repetieren / Spannen / Verschluss / Auswurf | Aktion | Clip | **nicht anwendbar** | kein Verschluss zu betätigen (Energiewaffe, Bogen oder Nahkampf) |
| `inspect` Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `inspect_return` Rückkehr aus Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `displace` Verdrängung (Interaktion, Nahkampf, Fähigkeit) | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `bow_nock` Pfeil auflegen | Typaktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `bow_draw` Ausziehen | Typaktion | Clip | **offen** | Mechanik dargestellt (draw_hold_release); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `bow_hold` Halten | Typaktion | Clip | **offen** | Mechanik dargestellt (draw_hold_release); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `bow_release` Lösen | Typaktion | Clip | **offen** | Mechanik dargestellt (draw_hold_release); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `bow_letdown` Entspannen | Typaktion | Clip | **offen** | Mechanik dargestellt (let_down); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `bow_renock` Erneut auflegen | Typaktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_sprint_aim` Sprint → Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,25–0,35 s (ADS-Messungen Q-REF) |
| `tr_sprint_fire` Sprint → Feuer | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15–0,25 s |
| `tr_draw_aimheld` Ziehen bei gehaltenem Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Ziehen gemessen 0,18–0,60 s je Typ (Q-REF) |
| `tr_reload_switch` Nachladen → Wechsel | Übergang | gemischt | **nicht anwendbar** | kein Nachladen/Aufladen bzw. kein Feuer bei diesem Typ |
| `tr_reload_cancel` Erlaubter Nachladeabbruch | Übergang | gemischt | **nicht anwendbar** | kein Nachladen/Aufladen bzw. kein Feuer bei diesem Typ |
| `tr_charge_cancel` Aufladen abbrechen | Übergang | gemischt | **nicht anwendbar** | kein Nachladen/Aufladen bzw. kein Feuer bei diesem Typ |
| `tr_inspect_cancel` Betrachten abbrechen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15 s |
| `tr_fire_move` Feuer während Bewegung | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_fire_air` Feuer in der Luft | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_wall` Wandabsenkung und Rückkehr | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,2 s |
| `tr_quick_switch` Schneller erneuter Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Waffenwechsel V06/V07 (Q-REF) |
| `tr_view` Ego-/ISO-Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Schwert: 0,15 + 0,33 s (Q-REF Sword) |

## BASIC-08

Schrotflinte „Streuer“ · CE-Profilklasse: shotgun · Munitionszufuhr: Einzelpatronen

| Zeile | Bereich | Ebene | Status | Detail |
|---|---|---|---|---|
| `pose_rest` Ruhehaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „shotgun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_hip` Hüftfeuerhaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „shotgun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_aim` Zielhaltung (Visier/Zielfernrohr) | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „shotgun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_hip_aim` Hüfte → Zielen | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_aim_hip` Zielen → Hüfte | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `pose_lowered` Gesenkte Haltung / Wandnähe | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „shotgun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_lowered_return` Rückkehr aus gesenkter Haltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „shotgun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_walk` Gehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „shotgun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_strafe` Seitwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „shotgun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_back` Rückwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „shotgun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_in` Sprintbeginn | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `sprint_loop` Sprintschleife | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „shotgun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_out` Sprintende | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `crouch` Ducken | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „shotgun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `crouch_move` Geduckte Bewegung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „shotgun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `jump_start` Sprungbeginn | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „shotgun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `air` Luftphase | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „shotgun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `land` Landung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „shotgun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `slide` Rutschen | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Walk, Sprint, Crouch, Air, Lowered; Q-CE-07) |
| `climb` Klettern | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Q-CE-07) |
| `sway` Nachschwingen beim Umsehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „shotgun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `inertia` Bewegungsträgheit | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „shotgun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `regrip` Griffkorrektur | Bewegung | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `draw` Ziehen | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `ready` Einsatzbereitschaft | Aktion | Posendaten | **offen** | Posendaten der CE-Klasse „shotgun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `holster` Wegstecken | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `switch` Waffenwechsel | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `fire_single` Einzelschuss | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion fire_pump (Clip <EVIDENCE>/clips/BASIC-08_<aktion>.mp4, gesichtet laut data/review.json) |
| `fire_burst` Salve | Aktion | Clip | **nicht anwendbar** | nur das Impulsgewehr feuert Salven (Burst-Rahmen anderer Typen zurückgestellt, EXT-12) |
| `fire_auto` Dauerfeuer / Dauerstrahl | Aktion | Clip | **nicht anwendbar** | kein Dauerfeuer bei diesem Typ |
| `recoil_mech` Rückstoß und Mechanik, Rückkehr | Aktion | prozedural | **offen** | prozedural der CE-Klasse „shotgun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `recoil_camera` Kamera-Feedback (getrennt) | Aktion | prozedural | **offen** | prozedural der CE-Klasse „shotgun“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `charge` Aufladen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ (Bogen: Auszug in eigenen Zeilen) |
| `charge_hold` Ladung halten | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_release` Ladung auslösen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_cancel` Aufladen abbrechen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `reload_partial` Nachladen mit Restmunition | Aktion | Clip | **offen** | Mechanik dargestellt (load_shell); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `reload_empty` Nachladen aus leerem Zustand | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `reload_feed` Munitionszufuhr (Magazin, Trommel, Gurt, Zelle, Einzelpatrone) | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion load_shell (Clip <EVIDENCE>/clips/BASIC-08_<aktion>.mp4, gesichtet laut data/review.json) |
| `cycle` Repetieren / Spannen / Verschluss / Auswurf | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion fire_pump (Clip <EVIDENCE>/clips/BASIC-08_<aktion>.mp4, gesichtet laut data/review.json) |
| `inspect` Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `inspect_return` Rückkehr aus Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `displace` Verdrängung (Interaktion, Nahkampf, Fähigkeit) | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_sprint_aim` Sprint → Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,25–0,35 s (ADS-Messungen Q-REF) |
| `tr_sprint_fire` Sprint → Feuer | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15–0,25 s |
| `tr_draw_aimheld` Ziehen bei gehaltenem Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Ziehen gemessen 0,18–0,60 s je Typ (Q-REF) |
| `tr_reload_switch` Nachladen → Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Holster ab aktueller Stellung (Q-CE-06) |
| `tr_reload_cancel` Erlaubter Nachladeabbruch | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: abhängig vom Reload-Clip |
| `tr_charge_cancel` Aufladen abbrechen | Übergang | gemischt | **nicht anwendbar** | kein Nachladen/Aufladen bzw. kein Feuer bei diesem Typ |
| `tr_inspect_cancel` Betrachten abbrechen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15 s |
| `tr_fire_move` Feuer während Bewegung | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_fire_air` Feuer in der Luft | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_wall` Wandabsenkung und Rückkehr | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,2 s |
| `tr_quick_switch` Schneller erneuter Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Waffenwechsel V06/V07 (Q-REF) |
| `tr_view` Ego-/ISO-Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Schwert: 0,15 + 0,33 s (Q-REF Sword) |

## BASIC-09

Scharfschützengewehr „Weitschuss“ · CE-Profilklasse: sniper · Munitionszufuhr: Magazin

| Zeile | Bereich | Ebene | Status | Detail |
|---|---|---|---|---|
| `pose_rest` Ruhehaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „sniper“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_hip` Hüftfeuerhaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „sniper“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_aim` Zielhaltung (Visier/Zielfernrohr) | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „sniper“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_hip_aim` Hüfte → Zielen | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_aim_hip` Zielen → Hüfte | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `pose_lowered` Gesenkte Haltung / Wandnähe | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „sniper“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_lowered_return` Rückkehr aus gesenkter Haltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „sniper“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_walk` Gehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sniper“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_strafe` Seitwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sniper“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_back` Rückwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sniper“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_in` Sprintbeginn | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `sprint_loop` Sprintschleife | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „sniper“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_out` Sprintende | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `crouch` Ducken | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „sniper“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `crouch_move` Geduckte Bewegung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sniper“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `jump_start` Sprungbeginn | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sniper“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `air` Luftphase | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „sniper“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `land` Landung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sniper“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `slide` Rutschen | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Walk, Sprint, Crouch, Air, Lowered; Q-CE-07) |
| `climb` Klettern | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Q-CE-07) |
| `sway` Nachschwingen beim Umsehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sniper“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `inertia` Bewegungsträgheit | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sniper“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `regrip` Griffkorrektur | Bewegung | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `draw` Ziehen | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `ready` Einsatzbereitschaft | Aktion | Posendaten | **offen** | Posendaten der CE-Klasse „sniper“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `holster` Wegstecken | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `switch` Waffenwechsel | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `fire_single` Einzelschuss | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion fire_cycle (Clip <EVIDENCE>/clips/BASIC-09_<aktion>.mp4, gesichtet laut data/review.json) |
| `fire_burst` Salve | Aktion | Clip | **nicht anwendbar** | nur das Impulsgewehr feuert Salven (Burst-Rahmen anderer Typen zurückgestellt, EXT-12) |
| `fire_auto` Dauerfeuer / Dauerstrahl | Aktion | Clip | **nicht anwendbar** | kein Dauerfeuer bei diesem Typ |
| `recoil_mech` Rückstoß und Mechanik, Rückkehr | Aktion | prozedural | **offen** | prozedural der CE-Klasse „sniper“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `recoil_camera` Kamera-Feedback (getrennt) | Aktion | prozedural | **offen** | prozedural der CE-Klasse „sniper“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `charge` Aufladen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ (Bogen: Auszug in eigenen Zeilen) |
| `charge_hold` Ladung halten | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_release` Ladung auslösen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_cancel` Aufladen abbrechen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `reload_partial` Nachladen mit Restmunition | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `reload_empty` Nachladen aus leerem Zustand | Aktion | Clip | **offen** | Mechanik dargestellt (reload_empty); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `reload_feed` Munitionszufuhr (Magazin, Trommel, Gurt, Zelle, Einzelpatrone) | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion reload_empty (Clip <EVIDENCE>/clips/BASIC-09_<aktion>.mp4, gesichtet laut data/review.json) |
| `cycle` Repetieren / Spannen / Verschluss / Auswurf | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion fire_cycle, reload_empty (Clip <EVIDENCE>/clips/BASIC-09_<aktion>.mp4, gesichtet laut data/review.json) |
| `inspect` Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `inspect_return` Rückkehr aus Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `displace` Verdrängung (Interaktion, Nahkampf, Fähigkeit) | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_sprint_aim` Sprint → Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,25–0,35 s (ADS-Messungen Q-REF) |
| `tr_sprint_fire` Sprint → Feuer | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15–0,25 s |
| `tr_draw_aimheld` Ziehen bei gehaltenem Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Ziehen gemessen 0,18–0,60 s je Typ (Q-REF) |
| `tr_reload_switch` Nachladen → Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Holster ab aktueller Stellung (Q-CE-06) |
| `tr_reload_cancel` Erlaubter Nachladeabbruch | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: abhängig vom Reload-Clip |
| `tr_charge_cancel` Aufladen abbrechen | Übergang | gemischt | **nicht anwendbar** | kein Nachladen/Aufladen bzw. kein Feuer bei diesem Typ |
| `tr_inspect_cancel` Betrachten abbrechen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15 s |
| `tr_fire_move` Feuer während Bewegung | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_fire_air` Feuer in der Luft | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_wall` Wandabsenkung und Rückkehr | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,2 s |
| `tr_quick_switch` Schneller erneuter Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Waffenwechsel V06/V07 (Q-REF) |
| `tr_view` Ego-/ISO-Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Schwert: 0,15 + 0,33 s (Q-REF Sword) |

## BASIC-10

Fusionsgewehr „Glutkern“ · CE-Profilklasse: rifle (Annahme, Profil ungeprüft) · Munitionszufuhr: Energiezelle

| Zeile | Bereich | Ebene | Status | Detail |
|---|---|---|---|---|
| `pose_rest` Ruhehaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_hip` Hüftfeuerhaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_aim` Zielhaltung (Visier/Zielfernrohr) | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_hip_aim` Hüfte → Zielen | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_aim_hip` Zielen → Hüfte | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `pose_lowered` Gesenkte Haltung / Wandnähe | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_lowered_return` Rückkehr aus gesenkter Haltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_walk` Gehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_strafe` Seitwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_back` Rückwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_in` Sprintbeginn | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `sprint_loop` Sprintschleife | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_out` Sprintende | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `crouch` Ducken | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `crouch_move` Geduckte Bewegung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `jump_start` Sprungbeginn | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `air` Luftphase | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `land` Landung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `slide` Rutschen | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Walk, Sprint, Crouch, Air, Lowered; Q-CE-07) |
| `climb` Klettern | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Q-CE-07) |
| `sway` Nachschwingen beim Umsehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `inertia` Bewegungsträgheit | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `regrip` Griffkorrektur | Bewegung | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `draw` Ziehen | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `ready` Einsatzbereitschaft | Aktion | Posendaten | **offen** | Posendaten der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `holster` Wegstecken | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `switch` Waffenwechsel | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `fire_single` Einzelschuss | Aktion | Clip | **nicht anwendbar** | anderer Feuermodus (Salve, Dauerfeuer, Aufladen oder Nahkampf) |
| `fire_burst` Salve | Aktion | Clip | **nicht anwendbar** | nur das Impulsgewehr feuert Salven (Burst-Rahmen anderer Typen zurückgestellt, EXT-12) |
| `fire_auto` Dauerfeuer / Dauerstrahl | Aktion | Clip | **nicht anwendbar** | kein Dauerfeuer bei diesem Typ |
| `recoil_mech` Rückstoß und Mechanik, Rückkehr | Aktion | prozedural | **offen** | prozedural der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `recoil_camera` Kamera-Feedback (getrennt) | Aktion | prozedural | **offen** | prozedural der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `charge` Aufladen | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion charge_fire (Clip <EVIDENCE>/clips/BASIC-10_<aktion>.mp4, gesichtet laut data/review.json) |
| `charge_hold` Ladung halten | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion charge_fire (Clip <EVIDENCE>/clips/BASIC-10_<aktion>.mp4, gesichtet laut data/review.json) |
| `charge_release` Ladung auslösen | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion charge_fire (Clip <EVIDENCE>/clips/BASIC-10_<aktion>.mp4, gesichtet laut data/review.json) |
| `charge_cancel` Aufladen abbrechen | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion charge_cancel (Clip <EVIDENCE>/clips/BASIC-10_<aktion>.mp4, gesichtet laut data/review.json) |
| `reload_partial` Nachladen mit Restmunition | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `reload_empty` Nachladen aus leerem Zustand | Aktion | Clip | **offen** | Mechanik dargestellt (reload); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `reload_feed` Munitionszufuhr (Magazin, Trommel, Gurt, Zelle, Einzelpatrone) | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion reload (Clip <EVIDENCE>/clips/BASIC-10_<aktion>.mp4, gesichtet laut data/review.json) |
| `cycle` Repetieren / Spannen / Verschluss / Auswurf | Aktion | Clip | **nicht anwendbar** | kein Verschluss zu betätigen (Energiewaffe, Bogen oder Nahkampf) |
| `inspect` Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `inspect_return` Rückkehr aus Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `displace` Verdrängung (Interaktion, Nahkampf, Fähigkeit) | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_sprint_aim` Sprint → Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,25–0,35 s (ADS-Messungen Q-REF) |
| `tr_sprint_fire` Sprint → Feuer | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15–0,25 s |
| `tr_draw_aimheld` Ziehen bei gehaltenem Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Ziehen gemessen 0,18–0,60 s je Typ (Q-REF) |
| `tr_reload_switch` Nachladen → Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Holster ab aktueller Stellung (Q-CE-06) |
| `tr_reload_cancel` Erlaubter Nachladeabbruch | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: abhängig vom Reload-Clip |
| `tr_charge_cancel` Aufladen abbrechen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Fusion: Laden bis Strahl 0,52–0,87 s (Q-REF) |
| `tr_inspect_cancel` Betrachten abbrechen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15 s |
| `tr_fire_move` Feuer während Bewegung | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_fire_air` Feuer in der Luft | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_wall` Wandabsenkung und Rückkehr | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,2 s |
| `tr_quick_switch` Schneller erneuter Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Waffenwechsel V06/V07 (Q-REF) |
| `tr_view` Ego-/ISO-Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Schwert: 0,15 + 0,33 s (Q-REF Sword) |

## BASIC-11

Lineares Fusionsgewehr „Schienenlicht“ · CE-Profilklasse: sniper (Vorschlag) · Munitionszufuhr: Energiezelle

| Zeile | Bereich | Ebene | Status | Detail |
|---|---|---|---|---|
| `pose_rest` Ruhehaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „sniper (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_hip` Hüftfeuerhaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „sniper (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_aim` Zielhaltung (Visier/Zielfernrohr) | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „sniper (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_hip_aim` Hüfte → Zielen | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_aim_hip` Zielen → Hüfte | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `pose_lowered` Gesenkte Haltung / Wandnähe | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „sniper (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_lowered_return` Rückkehr aus gesenkter Haltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „sniper (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_walk` Gehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sniper (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_strafe` Seitwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sniper (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_back` Rückwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sniper (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_in` Sprintbeginn | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `sprint_loop` Sprintschleife | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „sniper (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_out` Sprintende | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `crouch` Ducken | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „sniper (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `crouch_move` Geduckte Bewegung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sniper (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `jump_start` Sprungbeginn | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sniper (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `air` Luftphase | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „sniper (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `land` Landung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sniper (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `slide` Rutschen | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Walk, Sprint, Crouch, Air, Lowered; Q-CE-07) |
| `climb` Klettern | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Q-CE-07) |
| `sway` Nachschwingen beim Umsehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sniper (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `inertia` Bewegungsträgheit | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „sniper (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `regrip` Griffkorrektur | Bewegung | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `draw` Ziehen | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `ready` Einsatzbereitschaft | Aktion | Posendaten | **offen** | Posendaten der CE-Klasse „sniper (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `holster` Wegstecken | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `switch` Waffenwechsel | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `fire_single` Einzelschuss | Aktion | Clip | **nicht anwendbar** | anderer Feuermodus (Salve, Dauerfeuer, Aufladen oder Nahkampf) |
| `fire_burst` Salve | Aktion | Clip | **nicht anwendbar** | nur das Impulsgewehr feuert Salven (Burst-Rahmen anderer Typen zurückgestellt, EXT-12) |
| `fire_auto` Dauerfeuer / Dauerstrahl | Aktion | Clip | **nicht anwendbar** | kein Dauerfeuer bei diesem Typ |
| `recoil_mech` Rückstoß und Mechanik, Rückkehr | Aktion | prozedural | **offen** | prozedural der CE-Klasse „sniper (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `recoil_camera` Kamera-Feedback (getrennt) | Aktion | prozedural | **offen** | prozedural der CE-Klasse „sniper (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `charge` Aufladen | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion charge_fire (Clip <EVIDENCE>/clips/BASIC-11_<aktion>.mp4, gesichtet laut data/review.json) |
| `charge_hold` Ladung halten | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion charge_fire (Clip <EVIDENCE>/clips/BASIC-11_<aktion>.mp4, gesichtet laut data/review.json) |
| `charge_release` Ladung auslösen | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion charge_fire (Clip <EVIDENCE>/clips/BASIC-11_<aktion>.mp4, gesichtet laut data/review.json) |
| `charge_cancel` Aufladen abbrechen | Aktion | Clip | **offen** | Mechanik dieser Aktion im Modell nicht animiert |
| `reload_partial` Nachladen mit Restmunition | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `reload_empty` Nachladen aus leerem Zustand | Aktion | Clip | **offen** | Mechanik dargestellt (reload); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `reload_feed` Munitionszufuhr (Magazin, Trommel, Gurt, Zelle, Einzelpatrone) | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion reload (Clip <EVIDENCE>/clips/BASIC-11_<aktion>.mp4, gesichtet laut data/review.json) |
| `cycle` Repetieren / Spannen / Verschluss / Auswurf | Aktion | Clip | **nicht anwendbar** | kein Verschluss zu betätigen (Energiewaffe, Bogen oder Nahkampf) |
| `inspect` Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `inspect_return` Rückkehr aus Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `displace` Verdrängung (Interaktion, Nahkampf, Fähigkeit) | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_sprint_aim` Sprint → Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,25–0,35 s (ADS-Messungen Q-REF) |
| `tr_sprint_fire` Sprint → Feuer | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15–0,25 s |
| `tr_draw_aimheld` Ziehen bei gehaltenem Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Ziehen gemessen 0,18–0,60 s je Typ (Q-REF) |
| `tr_reload_switch` Nachladen → Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Holster ab aktueller Stellung (Q-CE-06) |
| `tr_reload_cancel` Erlaubter Nachladeabbruch | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: abhängig vom Reload-Clip |
| `tr_charge_cancel` Aufladen abbrechen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Fusion: Laden bis Strahl 0,52–0,87 s (Q-REF) |
| `tr_inspect_cancel` Betrachten abbrechen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15 s |
| `tr_fire_move` Feuer während Bewegung | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_fire_air` Feuer in der Luft | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_wall` Wandabsenkung und Rückkehr | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,2 s |
| `tr_quick_switch` Schneller erneuter Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Waffenwechsel V06/V07 (Q-REF) |
| `tr_view` Ego-/ISO-Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Schwert: 0,15 + 0,33 s (Q-REF Sword) |

## BASIC-12

Spurgewehr „Leitstrahl“ · CE-Profilklasse: rifle (Annahme, Profil ungeprüft) · Munitionszufuhr: Energiezelle (seitlich)

| Zeile | Bereich | Ebene | Status | Detail |
|---|---|---|---|---|
| `pose_rest` Ruhehaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_hip` Hüftfeuerhaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_aim` Zielhaltung (Visier/Zielfernrohr) | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_hip_aim` Hüfte → Zielen | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_aim_hip` Zielen → Hüfte | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `pose_lowered` Gesenkte Haltung / Wandnähe | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_lowered_return` Rückkehr aus gesenkter Haltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_walk` Gehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_strafe` Seitwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_back` Rückwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_in` Sprintbeginn | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `sprint_loop` Sprintschleife | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_out` Sprintende | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `crouch` Ducken | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `crouch_move` Geduckte Bewegung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `jump_start` Sprungbeginn | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `air` Luftphase | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `land` Landung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `slide` Rutschen | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Walk, Sprint, Crouch, Air, Lowered; Q-CE-07) |
| `climb` Klettern | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Q-CE-07) |
| `sway` Nachschwingen beim Umsehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `inertia` Bewegungsträgheit | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `regrip` Griffkorrektur | Bewegung | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `draw` Ziehen | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `ready` Einsatzbereitschaft | Aktion | Posendaten | **offen** | Posendaten der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `holster` Wegstecken | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `switch` Waffenwechsel | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `fire_single` Einzelschuss | Aktion | Clip | **nicht anwendbar** | anderer Feuermodus (Salve, Dauerfeuer, Aufladen oder Nahkampf) |
| `fire_burst` Salve | Aktion | Clip | **nicht anwendbar** | nur das Impulsgewehr feuert Salven (Burst-Rahmen anderer Typen zurückgestellt, EXT-12) |
| `fire_auto` Dauerfeuer / Dauerstrahl | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion beam (Clip <EVIDENCE>/clips/BASIC-12_<aktion>.mp4, gesichtet laut data/review.json) |
| `recoil_mech` Rückstoß und Mechanik, Rückkehr | Aktion | prozedural | **offen** | prozedural der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `recoil_camera` Kamera-Feedback (getrennt) | Aktion | prozedural | **offen** | prozedural der CE-Klasse „rifle (Annahme, Profil ungeprüft)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `charge` Aufladen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ (Bogen: Auszug in eigenen Zeilen) |
| `charge_hold` Ladung halten | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_release` Ladung auslösen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_cancel` Aufladen abbrechen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `reload_partial` Nachladen mit Restmunition | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `reload_empty` Nachladen aus leerem Zustand | Aktion | Clip | **offen** | Mechanik dargestellt (reload); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `reload_feed` Munitionszufuhr (Magazin, Trommel, Gurt, Zelle, Einzelpatrone) | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion reload (Clip <EVIDENCE>/clips/BASIC-12_<aktion>.mp4, gesichtet laut data/review.json) |
| `cycle` Repetieren / Spannen / Verschluss / Auswurf | Aktion | Clip | **nicht anwendbar** | kein Verschluss zu betätigen (Energiewaffe, Bogen oder Nahkampf) |
| `inspect` Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `inspect_return` Rückkehr aus Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `displace` Verdrängung (Interaktion, Nahkampf, Fähigkeit) | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_sprint_aim` Sprint → Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,25–0,35 s (ADS-Messungen Q-REF) |
| `tr_sprint_fire` Sprint → Feuer | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15–0,25 s |
| `tr_draw_aimheld` Ziehen bei gehaltenem Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Ziehen gemessen 0,18–0,60 s je Typ (Q-REF) |
| `tr_reload_switch` Nachladen → Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Holster ab aktueller Stellung (Q-CE-06) |
| `tr_reload_cancel` Erlaubter Nachladeabbruch | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: abhängig vom Reload-Clip |
| `tr_charge_cancel` Aufladen abbrechen | Übergang | gemischt | **nicht anwendbar** | kein Nachladen/Aufladen bzw. kein Feuer bei diesem Typ |
| `tr_inspect_cancel` Betrachten abbrechen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15 s |
| `tr_fire_move` Feuer während Bewegung | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_fire_air` Feuer in der Luft | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_wall` Wandabsenkung und Rückkehr | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,2 s |
| `tr_quick_switch` Schneller erneuter Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Waffenwechsel V06/V07 (Q-REF) |
| `tr_view` Ego-/ISO-Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Schwert: 0,15 + 0,33 s (Q-REF Sword) |

## BASIC-13

Granatwerfer (Kipplauf) „Kipplauf“ · CE-Profilklasse: heavy (Vorschlag) · Munitionszufuhr: eine Granate

| Zeile | Bereich | Ebene | Status | Detail |
|---|---|---|---|---|
| `pose_rest` Ruhehaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_hip` Hüftfeuerhaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_aim` Zielhaltung (Visier/Zielfernrohr) | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_hip_aim` Hüfte → Zielen | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_aim_hip` Zielen → Hüfte | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `pose_lowered` Gesenkte Haltung / Wandnähe | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_lowered_return` Rückkehr aus gesenkter Haltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_walk` Gehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_strafe` Seitwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_back` Rückwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_in` Sprintbeginn | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `sprint_loop` Sprintschleife | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_out` Sprintende | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `crouch` Ducken | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `crouch_move` Geduckte Bewegung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `jump_start` Sprungbeginn | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `air` Luftphase | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `land` Landung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `slide` Rutschen | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Walk, Sprint, Crouch, Air, Lowered; Q-CE-07) |
| `climb` Klettern | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Q-CE-07) |
| `sway` Nachschwingen beim Umsehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `inertia` Bewegungsträgheit | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `regrip` Griffkorrektur | Bewegung | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `draw` Ziehen | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `ready` Einsatzbereitschaft | Aktion | Posendaten | **offen** | Posendaten der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `holster` Wegstecken | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `switch` Waffenwechsel | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `fire_single` Einzelschuss | Aktion | Clip | **offen** | Mechanik definiert (fire), Clip noch nicht gesichtet |
| `fire_burst` Salve | Aktion | Clip | **nicht anwendbar** | nur das Impulsgewehr feuert Salven (Burst-Rahmen anderer Typen zurückgestellt, EXT-12) |
| `fire_auto` Dauerfeuer / Dauerstrahl | Aktion | Clip | **nicht anwendbar** | kein Dauerfeuer bei diesem Typ |
| `recoil_mech` Rückstoß und Mechanik, Rückkehr | Aktion | prozedural | **offen** | prozedural der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `recoil_camera` Kamera-Feedback (getrennt) | Aktion | prozedural | **offen** | prozedural der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `charge` Aufladen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ (Bogen: Auszug in eigenen Zeilen) |
| `charge_hold` Ladung halten | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_release` Ladung auslösen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_cancel` Aufladen abbrechen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `reload_partial` Nachladen mit Restmunition | Aktion | Clip | **nicht anwendbar** | einschüssig: kein Teilnachladen |
| `reload_empty` Nachladen aus leerem Zustand | Aktion | Clip | **offen** | Mechanik dargestellt (reload); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `reload_feed` Munitionszufuhr (Magazin, Trommel, Gurt, Zelle, Einzelpatrone) | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion reload (Clip <EVIDENCE>/clips/BASIC-13_<aktion>.mp4, gesichtet laut data/review.json) |
| `cycle` Repetieren / Spannen / Verschluss / Auswurf | Aktion | Clip | **offen** | Mechanik dieser Aktion im Modell nicht animiert |
| `inspect` Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `inspect_return` Rückkehr aus Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `displace` Verdrängung (Interaktion, Nahkampf, Fähigkeit) | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_sprint_aim` Sprint → Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,25–0,35 s (ADS-Messungen Q-REF) |
| `tr_sprint_fire` Sprint → Feuer | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15–0,25 s |
| `tr_draw_aimheld` Ziehen bei gehaltenem Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Ziehen gemessen 0,18–0,60 s je Typ (Q-REF) |
| `tr_reload_switch` Nachladen → Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Holster ab aktueller Stellung (Q-CE-06) |
| `tr_reload_cancel` Erlaubter Nachladeabbruch | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: abhängig vom Reload-Clip |
| `tr_charge_cancel` Aufladen abbrechen | Übergang | gemischt | **nicht anwendbar** | kein Nachladen/Aufladen bzw. kein Feuer bei diesem Typ |
| `tr_inspect_cancel` Betrachten abbrechen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15 s |
| `tr_fire_move` Feuer während Bewegung | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_fire_air` Feuer in der Luft | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_wall` Wandabsenkung und Rückkehr | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,2 s |
| `tr_quick_switch` Schneller erneuter Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Waffenwechsel V06/V07 (Q-REF) |
| `tr_view` Ego-/ISO-Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Schwert: 0,15 + 0,33 s (Q-REF Sword) |

## BASIC-14

Raketenwerfer „Schulterrohr“ · CE-Profilklasse: heavy · Munitionszufuhr: eine Rakete

| Zeile | Bereich | Ebene | Status | Detail |
|---|---|---|---|---|
| `pose_rest` Ruhehaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_hip` Hüftfeuerhaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_aim` Zielhaltung (Visier/Zielfernrohr) | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_hip_aim` Hüfte → Zielen | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_aim_hip` Zielen → Hüfte | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `pose_lowered` Gesenkte Haltung / Wandnähe | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_lowered_return` Rückkehr aus gesenkter Haltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_walk` Gehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_strafe` Seitwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_back` Rückwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_in` Sprintbeginn | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `sprint_loop` Sprintschleife | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_out` Sprintende | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `crouch` Ducken | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `crouch_move` Geduckte Bewegung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `jump_start` Sprungbeginn | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `air` Luftphase | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `land` Landung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `slide` Rutschen | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Walk, Sprint, Crouch, Air, Lowered; Q-CE-07) |
| `climb` Klettern | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Q-CE-07) |
| `sway` Nachschwingen beim Umsehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `inertia` Bewegungsträgheit | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `regrip` Griffkorrektur | Bewegung | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `draw` Ziehen | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `ready` Einsatzbereitschaft | Aktion | Posendaten | **offen** | Posendaten der CE-Klasse „heavy“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `holster` Wegstecken | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `switch` Waffenwechsel | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `fire_single` Einzelschuss | Aktion | Clip | **offen** | Mechanik definiert (fire), Clip noch nicht gesichtet |
| `fire_burst` Salve | Aktion | Clip | **nicht anwendbar** | nur das Impulsgewehr feuert Salven (Burst-Rahmen anderer Typen zurückgestellt, EXT-12) |
| `fire_auto` Dauerfeuer / Dauerstrahl | Aktion | Clip | **nicht anwendbar** | kein Dauerfeuer bei diesem Typ |
| `recoil_mech` Rückstoß und Mechanik, Rückkehr | Aktion | prozedural | **offen** | prozedural der CE-Klasse „heavy“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `recoil_camera` Kamera-Feedback (getrennt) | Aktion | prozedural | **offen** | prozedural der CE-Klasse „heavy“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `charge` Aufladen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ (Bogen: Auszug in eigenen Zeilen) |
| `charge_hold` Ladung halten | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_release` Ladung auslösen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_cancel` Aufladen abbrechen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `reload_partial` Nachladen mit Restmunition | Aktion | Clip | **nicht anwendbar** | einschüssig: kein Teilnachladen |
| `reload_empty` Nachladen aus leerem Zustand | Aktion | Clip | **offen** | Mechanik dargestellt (reload); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `reload_feed` Munitionszufuhr (Magazin, Trommel, Gurt, Zelle, Einzelpatrone) | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion reload (Clip <EVIDENCE>/clips/BASIC-14_<aktion>.mp4, gesichtet laut data/review.json) |
| `cycle` Repetieren / Spannen / Verschluss / Auswurf | Aktion | Clip | **offen** | Mechanik dieser Aktion im Modell nicht animiert |
| `inspect` Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `inspect_return` Rückkehr aus Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `displace` Verdrängung (Interaktion, Nahkampf, Fähigkeit) | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_sprint_aim` Sprint → Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,25–0,35 s (ADS-Messungen Q-REF) |
| `tr_sprint_fire` Sprint → Feuer | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15–0,25 s |
| `tr_draw_aimheld` Ziehen bei gehaltenem Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Ziehen gemessen 0,18–0,60 s je Typ (Q-REF) |
| `tr_reload_switch` Nachladen → Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Holster ab aktueller Stellung (Q-CE-06) |
| `tr_reload_cancel` Erlaubter Nachladeabbruch | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: abhängig vom Reload-Clip |
| `tr_charge_cancel` Aufladen abbrechen | Übergang | gemischt | **nicht anwendbar** | kein Nachladen/Aufladen bzw. kein Feuer bei diesem Typ |
| `tr_inspect_cancel` Betrachten abbrechen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15 s |
| `tr_fire_move` Feuer während Bewegung | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_fire_air` Feuer in der Luft | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_wall` Wandabsenkung und Rückkehr | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,2 s |
| `tr_quick_switch` Schneller erneuter Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Waffenwechsel V06/V07 (Q-REF) |
| `tr_view` Ego-/ISO-Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Schwert: 0,15 + 0,33 s (Q-REF Sword) |

## BASIC-15

Maschinengewehr „Dauerlauf“ · CE-Profilklasse: heavy (Vorschlag) · Munitionszufuhr: Munitionskasten und Gurt

| Zeile | Bereich | Ebene | Status | Detail |
|---|---|---|---|---|
| `pose_rest` Ruhehaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_hip` Hüftfeuerhaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_aim` Zielhaltung (Visier/Zielfernrohr) | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_hip_aim` Hüfte → Zielen | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_aim_hip` Zielen → Hüfte | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `pose_lowered` Gesenkte Haltung / Wandnähe | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_lowered_return` Rückkehr aus gesenkter Haltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_walk` Gehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_strafe` Seitwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_back` Rückwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_in` Sprintbeginn | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `sprint_loop` Sprintschleife | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_out` Sprintende | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `crouch` Ducken | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `crouch_move` Geduckte Bewegung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `jump_start` Sprungbeginn | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `air` Luftphase | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `land` Landung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `slide` Rutschen | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Walk, Sprint, Crouch, Air, Lowered; Q-CE-07) |
| `climb` Klettern | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Q-CE-07) |
| `sway` Nachschwingen beim Umsehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `inertia` Bewegungsträgheit | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `regrip` Griffkorrektur | Bewegung | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `draw` Ziehen | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `ready` Einsatzbereitschaft | Aktion | Posendaten | **offen** | Posendaten der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `holster` Wegstecken | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `switch` Waffenwechsel | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `fire_single` Einzelschuss | Aktion | Clip | **nicht anwendbar** | anderer Feuermodus (Salve, Dauerfeuer, Aufladen oder Nahkampf) |
| `fire_burst` Salve | Aktion | Clip | **nicht anwendbar** | nur das Impulsgewehr feuert Salven (Burst-Rahmen anderer Typen zurückgestellt, EXT-12) |
| `fire_auto` Dauerfeuer / Dauerstrahl | Aktion | Clip | **offen** | Mechanik definiert (fire_auto), Clip noch nicht gesichtet |
| `recoil_mech` Rückstoß und Mechanik, Rückkehr | Aktion | prozedural | **offen** | prozedural der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `recoil_camera` Kamera-Feedback (getrennt) | Aktion | prozedural | **offen** | prozedural der CE-Klasse „heavy (Vorschlag)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `charge` Aufladen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ (Bogen: Auszug in eigenen Zeilen) |
| `charge_hold` Ladung halten | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_release` Ladung auslösen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_cancel` Aufladen abbrechen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `reload_partial` Nachladen mit Restmunition | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `reload_empty` Nachladen aus leerem Zustand | Aktion | Clip | **offen** | Mechanik dargestellt (reload); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `reload_feed` Munitionszufuhr (Magazin, Trommel, Gurt, Zelle, Einzelpatrone) | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion reload (Clip <EVIDENCE>/clips/BASIC-15_<aktion>.mp4, gesichtet laut data/review.json) |
| `cycle` Repetieren / Spannen / Verschluss / Auswurf | Aktion | Clip | **offen** | Mechanik dieser Aktion im Modell nicht animiert |
| `inspect` Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `inspect_return` Rückkehr aus Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `displace` Verdrängung (Interaktion, Nahkampf, Fähigkeit) | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_sprint_aim` Sprint → Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,25–0,35 s (ADS-Messungen Q-REF) |
| `tr_sprint_fire` Sprint → Feuer | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15–0,25 s |
| `tr_draw_aimheld` Ziehen bei gehaltenem Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Ziehen gemessen 0,18–0,60 s je Typ (Q-REF) |
| `tr_reload_switch` Nachladen → Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Holster ab aktueller Stellung (Q-CE-06) |
| `tr_reload_cancel` Erlaubter Nachladeabbruch | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: abhängig vom Reload-Clip |
| `tr_charge_cancel` Aufladen abbrechen | Übergang | gemischt | **nicht anwendbar** | kein Nachladen/Aufladen bzw. kein Feuer bei diesem Typ |
| `tr_inspect_cancel` Betrachten abbrechen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15 s |
| `tr_fire_move` Feuer während Bewegung | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_fire_air` Feuer in der Luft | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_wall` Wandabsenkung und Rückkehr | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,2 s |
| `tr_quick_switch` Schneller erneuter Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Waffenwechsel V06/V07 (Q-REF) |
| `tr_view` Ego-/ISO-Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Schwert: 0,15 + 0,33 s (Q-REF Sword) |

## BASIC-16

Schwert „Klingenlauf“ · CE-Profilklasse: keine (Nahkampfprofil fehlt) · Munitionszufuhr: keine

| Zeile | Bereich | Ebene | Status | Detail |
|---|---|---|---|---|
| `pose_rest` Ruhehaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_hip` Hüftfeuerhaltung | Grundhaltung | Posendaten | **nicht anwendbar** | Schwert: Bereitschaftshaltung statt Hüftfeuer (Zeile sword_ready) |
| `pose_aim` Zielhaltung (Visier/Zielfernrohr) | Grundhaltung | Posendaten | **nicht anwendbar** | Schwert hat keinen Zielmodus; Blocken übernimmt die Haltung |
| `tr_hip_aim` Hüfte → Zielen | Grundhaltung | Clip | **nicht anwendbar** | Schwert hat keinen Zielmodus; Blocken übernimmt die Haltung |
| `tr_aim_hip` Zielen → Hüfte | Grundhaltung | Clip | **nicht anwendbar** | Schwert hat keinen Zielmodus; Blocken übernimmt die Haltung |
| `pose_lowered` Gesenkte Haltung / Wandnähe | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_lowered_return` Rückkehr aus gesenkter Haltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_walk` Gehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_strafe` Seitwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_back` Rückwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_in` Sprintbeginn | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `sprint_loop` Sprintschleife | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_out` Sprintende | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `crouch` Ducken | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `crouch_move` Geduckte Bewegung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `jump_start` Sprungbeginn | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `air` Luftphase | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `land` Landung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `slide` Rutschen | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Walk, Sprint, Crouch, Air, Lowered; Q-CE-07) |
| `climb` Klettern | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Q-CE-07) |
| `sway` Nachschwingen beim Umsehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `inertia` Bewegungsträgheit | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `regrip` Griffkorrektur | Bewegung | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `draw` Ziehen | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `ready` Einsatzbereitschaft | Aktion | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `holster` Wegstecken | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `switch` Waffenwechsel | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `fire_single` Einzelschuss | Aktion | Clip | **nicht anwendbar** | anderer Feuermodus (Salve, Dauerfeuer, Aufladen oder Nahkampf) |
| `fire_burst` Salve | Aktion | Clip | **nicht anwendbar** | nur das Impulsgewehr feuert Salven (Burst-Rahmen anderer Typen zurückgestellt, EXT-12) |
| `fire_auto` Dauerfeuer / Dauerstrahl | Aktion | Clip | **nicht anwendbar** | kein Dauerfeuer bei diesem Typ |
| `recoil_mech` Rückstoß und Mechanik, Rückkehr | Aktion | prozedural | **nicht anwendbar** | Typ ohne Schusswaffenablauf (eigene Zeilen für Bogen bzw. Schwert) |
| `recoil_camera` Kamera-Feedback (getrennt) | Aktion | prozedural | **nicht anwendbar** | Typ ohne Schusswaffenablauf (eigene Zeilen für Bogen bzw. Schwert) |
| `charge` Aufladen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ (Bogen: Auszug in eigenen Zeilen) |
| `charge_hold` Ladung halten | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_release` Ladung auslösen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_cancel` Aufladen abbrechen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `reload_partial` Nachladen mit Restmunition | Aktion | Clip | **nicht anwendbar** | keine nachladbare Munition (Bogen: Pfeil, Schwert: Ladungen) |
| `reload_empty` Nachladen aus leerem Zustand | Aktion | Clip | **nicht anwendbar** | Typ ohne Schusswaffenablauf (eigene Zeilen für Bogen bzw. Schwert) |
| `reload_feed` Munitionszufuhr (Magazin, Trommel, Gurt, Zelle, Einzelpatrone) | Aktion | Clip | **nicht anwendbar** | Typ ohne Schusswaffenablauf (eigene Zeilen für Bogen bzw. Schwert) |
| `cycle` Repetieren / Spannen / Verschluss / Auswurf | Aktion | Clip | **nicht anwendbar** | kein Verschluss zu betätigen (Energiewaffe, Bogen oder Nahkampf) |
| `inspect` Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `inspect_return` Rückkehr aus Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `displace` Verdrängung (Interaktion, Nahkampf, Fähigkeit) | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `sword_ready` Bereitschaft | Typaktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `sword_light` Leichter Angriff | Typaktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `sword_heavy` Schwerer Angriff | Typaktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `sword_combo` Kombination | Typaktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `sword_block` Blocken | Typaktion | Clip | **offen** | Mechanik dargestellt (guard_charge); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `sword_recover` Erholung | Typaktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_sprint_aim` Sprint → Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,25–0,35 s (ADS-Messungen Q-REF) |
| `tr_sprint_fire` Sprint → Feuer | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15–0,25 s |
| `tr_draw_aimheld` Ziehen bei gehaltenem Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Ziehen gemessen 0,18–0,60 s je Typ (Q-REF) |
| `tr_reload_switch` Nachladen → Wechsel | Übergang | gemischt | **nicht anwendbar** | kein Nachladen/Aufladen bzw. kein Feuer bei diesem Typ |
| `tr_reload_cancel` Erlaubter Nachladeabbruch | Übergang | gemischt | **nicht anwendbar** | kein Nachladen/Aufladen bzw. kein Feuer bei diesem Typ |
| `tr_charge_cancel` Aufladen abbrechen | Übergang | gemischt | **nicht anwendbar** | kein Nachladen/Aufladen bzw. kein Feuer bei diesem Typ |
| `tr_inspect_cancel` Betrachten abbrechen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15 s |
| `tr_fire_move` Feuer während Bewegung | Übergang | gemischt | **nicht anwendbar** | kein Nachladen/Aufladen bzw. kein Feuer bei diesem Typ |
| `tr_fire_air` Feuer in der Luft | Übergang | gemischt | **nicht anwendbar** | kein Nachladen/Aufladen bzw. kein Feuer bei diesem Typ |
| `tr_wall` Wandabsenkung und Rückkehr | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,2 s |
| `tr_quick_switch` Schneller erneuter Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Waffenwechsel V06/V07 (Q-REF) |
| `tr_view` Ego-/ISO-Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Schwert: 0,15 + 0,33 s (Q-REF Sword) |

## BASIC-17

Glefe „Schildwacht“ · CE-Profilklasse: keine (Nahkampfprofil fehlt) · Munitionszufuhr: Energiezelle

| Zeile | Bereich | Ebene | Status | Detail |
|---|---|---|---|---|
| `pose_rest` Ruhehaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_hip` Hüftfeuerhaltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `pose_aim` Zielhaltung (Visier/Zielfernrohr) | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_hip_aim` Hüfte → Zielen | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_aim_hip` Zielen → Hüfte | Grundhaltung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `pose_lowered` Gesenkte Haltung / Wandnähe | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `tr_lowered_return` Rückkehr aus gesenkter Haltung | Grundhaltung | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_walk` Gehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_strafe` Seitwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `move_back` Rückwärts | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_in` Sprintbeginn | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `sprint_loop` Sprintschleife | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `sprint_out` Sprintende | Bewegung | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `crouch` Ducken | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `crouch_move` Geduckte Bewegung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `jump_start` Sprungbeginn | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `air` Luftphase | Bewegung | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `land` Landung | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `slide` Rutschen | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Walk, Sprint, Crouch, Air, Lowered; Q-CE-07) |
| `climb` Klettern | Bewegung | – | **nicht anwendbar** | kein Zustand in CE `EquipmentPoseState.cs` (Q-CE-07) |
| `sway` Nachschwingen beim Umsehen | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `inertia` Bewegungsträgheit | Bewegung | prozedural | **offen** | prozedural der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `regrip` Griffkorrektur | Bewegung | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `draw` Ziehen | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `ready` Einsatzbereitschaft | Aktion | Posendaten | **offen** | Posendaten der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `holster` Wegstecken | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `switch` Waffenwechsel | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `fire_single` Einzelschuss | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion fire (Clip <EVIDENCE>/clips/BASIC-17_<aktion>.mp4, gesichtet laut data/review.json) |
| `fire_burst` Salve | Aktion | Clip | **nicht anwendbar** | nur das Impulsgewehr feuert Salven (Burst-Rahmen anderer Typen zurückgestellt, EXT-12) |
| `fire_auto` Dauerfeuer / Dauerstrahl | Aktion | Clip | **nicht anwendbar** | kein Dauerfeuer bei diesem Typ |
| `recoil_mech` Rückstoß und Mechanik, Rückkehr | Aktion | prozedural | **offen** | prozedural der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `recoil_camera` Kamera-Feedback (getrennt) | Aktion | prozedural | **offen** | prozedural der CE-Klasse „keine (Nahkampfprofil fehlt)“ nicht für das BASIC-Modell geprüft (fehlender Import, Q-CE-07) |
| `charge` Aufladen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ (Bogen: Auszug in eigenen Zeilen) |
| `charge_hold` Ladung halten | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_release` Ladung auslösen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `charge_cancel` Aufladen abbrechen | Aktion | Clip | **nicht anwendbar** | kein Aufladen bei diesem Typ |
| `reload_partial` Nachladen mit Restmunition | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `reload_empty` Nachladen aus leerem Zustand | Aktion | Clip | **offen** | Mechanik dargestellt (reload); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `reload_feed` Munitionszufuhr (Magazin, Trommel, Gurt, Zelle, Einzelpatrone) | Aktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion reload (Clip <EVIDENCE>/clips/BASIC-17_<aktion>.mp4, gesichtet laut data/review.json) |
| `cycle` Repetieren / Spannen / Verschluss / Auswurf | Aktion | Clip | **nicht anwendbar** | kein Verschluss zu betätigen (Energiewaffe, Bogen oder Nahkampf) |
| `inspect` Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `inspect_return` Rückkehr aus Betrachten | Aktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `displace` Verdrängung (Interaktion, Nahkampf, Fähigkeit) | Aktion | gemischt | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `glaive_shot` Schuss | Typaktion | Clip | **offen** | Mechanik dargestellt (fire); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `glaive_reload` Nachladen | Typaktion | Clip | **offen** | Mechanik dargestellt (reload); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, BASIC hat noch keinen Toolgen-Import |
| `glaive_shield` Schild | Typaktion | Clip | **dargestellt** | Mechanik ohne Hände: Aktion shield (Clip <EVIDENCE>/clips/BASIC-17_<aktion>.mp4, gesichtet laut data/review.json) |
| `glaive_melee` Stiche/Hiebe | Typaktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `glaive_switch` Wechsel zwischen Aktionen | Typaktion | Clip | **offen** | Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09) |
| `tr_sprint_aim` Sprint → Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,25–0,35 s (ADS-Messungen Q-REF) |
| `tr_sprint_fire` Sprint → Feuer | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15–0,25 s |
| `tr_draw_aimheld` Ziehen bei gehaltenem Zielen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Ziehen gemessen 0,18–0,60 s je Typ (Q-REF) |
| `tr_reload_switch` Nachladen → Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Holster ab aktueller Stellung (Q-CE-06) |
| `tr_reload_cancel` Erlaubter Nachladeabbruch | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: abhängig vom Reload-Clip |
| `tr_charge_cancel` Aufladen abbrechen | Übergang | gemischt | **nicht anwendbar** | kein Nachladen/Aufladen bzw. kein Feuer bei diesem Typ |
| `tr_inspect_cancel` Betrachten abbrechen | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,15 s |
| `tr_fire_move` Feuer während Bewegung | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_fire_air` Feuer in der Luft | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: prozedural |
| `tr_wall` Wandabsenkung und Rückkehr | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: vorgeschlagen 0,2 s |
| `tr_quick_switch` Schneller erneuter Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Waffenwechsel V06/V07 (Q-REF) |
| `tr_view` Ego-/ISO-Wechsel | Übergang | gemischt | **offen** | Zustandslogik und Hände fehlen für das BASIC-Modell; Dauer: Schwert: 0,15 + 0,33 s (Q-REF Sword) |
