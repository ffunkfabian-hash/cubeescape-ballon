# Übergabe BALLON 0.35 „Stance“ – Etappe 2 (Stand 31.10.2026)

Frische Sitzung ohne Verlauf, gleicher Branch `claude/ballon-0.35-stance` (reserviert, Sitzungsname „BALLON 0.35 „Stance“ · Mac“; keine
neue Reservierung). Modell: Opus, Denkaufwand high (Formänderung und Abläufe, Spielgefühl). Erst `AGENTS.md`, `docs/LESSONS.md`,
`docs/ego.md` (erzeugt), den Berichtsentwurf [versions/0.35-stance.md](versions/0.35-stance.md) und den Auftrag unten lesen. Vorgaben aus
Motiongen `main` ec8e198: `~/Claude/cubeescape-reference/docs/destiny2.md` › `#s-backblast` (Tabellen A–G, E2) und `#s-verdict`
(Tabelle G, E2). Unity-Library liegt im Worktree (APFS-Klon); Unity und Blender nur unter `./ce lock unity|blender|gpu`.

## Auftrag (Sightline, 31.10.2026, Kurzfassung)

Ego-Haltungen und Abläufe nach Nutzerbefunden aus Testbuild 0.33 und Verdict › G, Laufen/Sprint, Bildanteil, Weltzoom. Daten nur in
`basic/arms/ego.py` (keine Waffen-IDs im Code); Wirkungsdaten aus 0.34 (`PAYLOAD`, `IMPACTS`, `EXPLOSION…`) nicht anfassen. Jede
Abweichung von Motiongen im Bericht begründen (E). Pflicht im Bericht: Tabelle „übernommen / bewusst nicht übernommen, warum“ mit
Fundstellen (steht im Entwurf, offene Zeilen nachtragen). Belege: je geänderter Bewegung ein MP4 (RL-Nachladen und -Ziehen,
Handfeuerwaffe Schuss Hüfte/Zielen, Bogen Spannen/Sprint, Laufen vs. Sprint, Hüftlagen-Wechsel – je Muster ein Vertreter) plus
Kontaktbogen, Standbilder für Bildanteil und Weltzoom; Ablage `~/Library/Caches/CubeEscapeBallon/0.35/belege/`. Version 0.35.0
„Stance“ in `.ce-repo.json`, CHANGELOG, Bericht, Entscheidungsliste nachgeführt; Richter `./ce judge` (Codex-Kontingent prüfen, sonst
`--api`). Commit und Push des Branches sind freigegeben, mergen macht Sightline. Nach dem Merge Testbuild nach
`~/BALLON-Testversionen/0.35/` mit LIESMICH.txt, dann aufräumen (Worktree ohne `--force`, Testkopien, eigene Caches bis auf Belege
0.34/0.35, `report.md`) und im Postfach melden.

## Etappe 1 – erledigt (Commit auf dem Branch, Einzelheiten im Berichtsentwurf)

Hüfte MG/Spur/LFR (Fluchtpunkt wie Automatik/Fusion), Raketenwerfer über der Schulter, Sprint-Formen je Klasse (Impuls, Schrot, MG, Spur,
Scharfschütze, Bogen), gespannte Bogenhüfte zur Mitte, Laufen (Hub, abgesenkt), RL-Zeiten, Weltzoom, eigener Rückstoßsatz der
Handfeuerwaffe (`CLASSES[...]['recoil']` → `gameplay.recoil`, Unity `EgoGameplay.RecoilOr`, Blender `sc.P['recoil']`), Projektile
zielen auf den Punkt unter dem Fadenkreuz (`WeaponFx.Launch`), Bildanteil gemessen. Werkzeuge: `tools/bildlage.py` (Anker und
Fluchtpunkt ohne Blender; `--fit <modul> <pose> mx my fx fy [roll] [tiefe]` rechnet pos/aim zurück), `tools/bildanteil.py`
(Workbench-Masken). Daten exportiert (`BALLON_EXPORT_DATA_ONLY=1`), `./check` grün.

## Etappe 2 – offen

1. **Raketenwerfer nachladen (Formänderung w14 v2.1 + Klassenaktion).** Destiny (Backblast › B, E2): Werfer quer kippen, Rohr nach rechts
   oben −14…−28°; die linke Hand senkt die Rakete **von oben** in einen Schacht auf der Oberseite nahe der Bildmitte (x 44–53 / y 47–75),
   rechte Hand bleibt am Griff; Start → ruhig Legendary 2,6–3,0 s (Hoosegow 3,00 s). Heute: Heckklappe `breech_cap`, Rakete von hinten;
   die Rakete schwebt durch das hintere Rohr (Nutzerbefund). Vorschlag: Ladeschacht mit Klappe auf der Rohroberseite hinter dem
   Gefechtskopf (neues Teil mit `move`, Rakete `move` senkrecht + längs), Ablauf `CLASSES['rocket_launcher']['actions']['reload_tactical']`
   und Haltung `poses['reload']` neu (heute 84 Bilder × TIME_SCALE = 3,5 s → ≈ 70 Bilder für 2,9 s). Kollision Rakete/Rohr am Modell
   prüfen (Bildfolge oder Abstandsrechnung je Bild). Neue Hüfthaltung (Etappe 1) beachten: Rohr neben dem Kopf, Heck an der Kamera.
   Danach Backen nur BASIC-14 (voller Export unter `ce lock gpu`, vgl. 0.34: „Neu gebacken nur BASIC-13 und BASIC-15“).
2. **Bogen im Zielen (Formänderung w07 v2.1).** Destiny (Backblast › D, E2): Visierpunkt 50/50, Pfeil senkrecht darunter in derselben
   Spalte, Spitze 16–22 pp tiefer, ruhig beim Spannen, ohne abgesetzte Pfeilauflage. Heute: Seitenvisier 60 mm links und 27,5 mm über der
   Pfeillinie (`Socket_Sight` u 73,5, x 60; Pfeil u 46, x 0) → Spitze bei 54,5/53,6 und hinter dem Riser (Nutzer: „Pfeil beim Spannen
   unsichtbar“). Rechnung: Augenabstand zur Spitze bei vollem Auszug ≈ 0,45 m → 16–22 pp = 7,5–10,3° → Visierring **59–82 mm direkt über**
   der Pfeillinie (x 0). `ads_hide` für Schaft/Federn danach prüfen (Pfeil soll unter dem Ring sichtbar sein, der Schaft darf nicht groß
   vor der Kamera stehen); `tools/bildlage.py` mit `Socket_ArrowTip` und ein Blender-Still im Zielen und bei vollem Auszug. Backen BASIC-07.
3. **Granatwerfer-Ladefolge mit Gegendrehung** (offen aus 0.34, Entscheidungsliste › Block 9 unten): Laden dreht heute die Trommel in
   Schussrichtung (`reload_tactical`/`reload_shell`: `drum` 0 → 1); stimmig ist eine Gegendrehung je geladener Kammer, damit die Kammern
   in Schussfolge liegen. Unity ordnet heute beim ersten `fire_cycle` um (Test) – mit Gegendrehung entfällt das; Test anpassen.
4. **Revolver-Nachladehaltung neu fassen** (offen aus 0.34): `CLASSES['hand_cannon']['poses']['reload']` liegt seit 0.34 nur 5 cm höher
   (Hülsen im Bild). Destiny-Revolver: Hochdrehen 0,13 s, Trommel zur Kamera (Motiongen destiny2 › Revolver). Haltung und Ablauf am Still
   neu fassen (Trommel und fallende Hülsen sichtbar, Stützhand verdeckt nicht).
5. **Freihaltezone A4 und Bildanteil neu** nach allen Haltungsänderungen: `ce lock gpu -- …/tools/ego_clear.py -- --gpu` (alle 16),
   `tools/bildanteil.py --poses hip,ads,sprint`; Tabelle im Bericht nachziehen. Stand Etappe 1: Warnung nur Raketenwerfer (0,13 %, danach
   1 cm nach rechts geschoben, nicht neu gemessen).
6. **Unity:** EditMode/PlayMode (Ergebnis Etappe 1 im Bericht), Gegenprobe (eine Erwartung absichtlich falsch → rot), `tools/unity_run.py
   compare <n>` gegen frische Blender-Stills für die geänderten Waffen (Tasten in `unity_run.WEAPONS`: MG, Spur, LFR, Raketenwerfer,
   Bogen, Handfeuerwaffe).
7. **Belege** (Liste oben) unter `~/Library/Caches/CubeEscapeBallon/0.35/belege/`; Unity-Aufnahmen über `tools/unity_run.py` (Demos), Ego-Clips
   über `tools/ego_build.py --actions …` und `tools/make_ego.py clips|sheets`.
8. **Abschluss:** `.ce-repo.json` 0.35.0 „Stance“, CHANGELOG, Bericht fertig (erste Zeile, Ist-Zeit Warten/Rechnen/Lesen/Umsetzen;
   Etappe 1: ≈ 3 h), Entscheidungsliste (neuer Block 10 „Stance“), Lehren in `docs/LESSONS.md`, `./ce judge`, PR (Bericht = Beschreibung),
   Postfach an Sightline mit PR-Link und vollem Head.

## Entscheidung nötig (im Bericht stehen lassen, über Sightline)

- **Zielbild 2–5× größer als Destiny** (BALLON 8–17 %, Destiny 2,7–9,5 %): Folge von Visier-Standard 3 (Modell ungezoomt, Öffnung 12–26 % B).
- **Raketenwerfer im Zielen 50 %** (Destiny 16,7 %): Seitenvisier W2 66 mm neben der Rohrachse.
