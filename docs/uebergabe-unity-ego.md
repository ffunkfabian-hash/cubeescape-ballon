# Übergabe: spielbare Ego-Perspektive als eigene Unity-Version (0.4 „Firstfeel“)

Stand 24.10.2026, aus der Sitzung „BALLON Auftrag · Mac“ (Branch `claude/basic-first-light`, Commit mit diesem Dokument).
Für eine **frische Sitzung ohne Gesprächsverlauf** geschrieben.

Opus 5.5, `high` – Grund: Spielgefühl und neues Laufzeitsystem (Entwurf).

## Auftrag des Nutzers

> „Bekommen wir die Ego-Perspektive als spürbare eigene Unity Version hin?“

Die Antwort war ja, mit dem unten beschriebenen Weg. Der Nutzer will alles **getrennt halten wie die Waffen**: Arme, Hände und
Animationen sollen frei überarbeitbar bleiben (Entscheidung vom 24.10.2026). Cube Escape, Toolgen und Robogen nur lesen.

- **Ziel:** Ein eigenes Unity-Projekt in diesem Repo, in dem man die Pilotwaffe BASIC-01 v2.1 mit den Roboterarmen v3 aus der
  Ego-Perspektive **selbst spielt und spürt**: Umsehen, Laufen, Zielen, Feuern mit Rückstoß, Nachladen, Betrachten. Die Bewegung
  läuft live in C# aus denselben Daten wie die Blender-Clips (Blender bleibt Referenz, Unity ist der Spürtest).
- **Dateien/Zuständigkeit:**
  - Neu: `unity/` (Unity-Projekt), `tools/export_unity.py` (Blender → FBX + JSON), Doku `docs/unity.md`,
    Bericht `docs/versions/0.4-firstfeel.md`.
  - Nur lesen: `basic/arms/robot_arm.py`, `basic/arms/ego.py`, `basic/pilot/w01_auto_rifle_v21.py`, `tools/ego_build.py`.
    Datenänderungen dort nur, wenn Unity einen echten Fehler aufdeckt, und dann mit Blender-Gegenprobe.
  - Nicht anfassen: Cube Escape, Toolgen (inklusive Lockstep), Robogen, Formgen.
  - Verträge: keine neuen gemeinsamen Verträge. Das JSON-Austauschformat ist projektintern mit `"format": "ballon-ego/1"`.
- **Prüfen:**
  - `./check` plus Unity-EditMode- und PlayMode-Tests.
  - Unity-Läufe nur mit `~/Claude/cubeescape-nexogen/ce lock unity -- …`, Blender-Export mit `ce lock blender`.
  - Nur auf dem Mac, nicht in der Cloud.
- **Fertig wenn:**
  - Eine macOS-Entwicklungsbuild startet in einem grauen Testparcours mit Zielscheiben.
  - Alle Steuerungen unten funktionieren.
  - Die Tests sind grün.
  - Ein MP4 (720p, so lang wie der Ablauf) zeigt Zielen → Feuerstoß → leeres Nachladen → Betrachten.
  - Ein Standbild-Vergleich Unity gegen Blender (gleiche Haltung `hip` und `ads`) liegt vor.
- **Release:** nein. Vor dem Merge kommt die Codex-Prüfung (`./ce judge`, ohne Codex `--opus`).

## Ausgangslage

- Unity **6000.6.2f1** installiert (`~/.unity/bin/unity`, Unity Hub). URP und Input System verwenden.
- **Kein Git-Remote** für dieses Repo: `./ce session reserve` (pusht auf `origin`) geht nicht. Lokalen Branch
  `claude/ballon-0.4-firstfeel` von `claude/basic-first-light` abzweigen und das im Start-Check nennen. Nie auf `main` committen.
- Pilotwaffe: `basic/pilot/w01_auto_rifle_v21.py`. Sie hat 70 Teile, Magazin und Visier sind eigene Teile.
  - Anker: `Socket_Hand`, `Socket_SupportHand`, `Socket_Sight`, `Socket_Eye`, `Socket_Charge`.
  - Mechanik als `ACTIONS` mit Bewegungen `translate`, `rotate`, `segment`, `glow`.
- Arm v3: `basic/arms/robot_arm.py`. Er besteht aus starren Teilen je Segment (`upper`, `fore`, `hand`, `f0_0` … `f3_2`,
  `t_0` … `t_2`), ohne Skinning.
  - Vier Finger und Daumen.
  - Formen `box`, `cyl`, `prism`, `plate`, `hull`, Geometrie in `tools/ego_build.py` (`piece_mesh`, `build_arm`).
- Ego-Daten: `basic/arms/ego.py`.
  - Kamera 75° horizontal, 30 fps.
  - `POSES`: 10 Haltungen.
  - `GRIPS`: grip, support, mag, charge – jeweils Kontaktpunkt, Handfläche, Fingerrichtung und Teil.
  - `ACTIONS`: 19 Aktionen mit Kanälen `weapon`, `L`/`R`, `fL`/`fR`, `mech`, `carry`, `drop`, `fire`, `breathe`, `bob`, `events`.
  - Achs- und Vorzeichenregeln stehen im Kopf von `tools/ego_build.py` und in `docs/stilhandbuch.md` › 10.
- Blender-Referenz: `tools/ego_build.py`.
  - Funktionen `pose_matrix`, `grip_hand`, `solve_arm` (Unterarm folgt der Hand, Knick ≤ 45°, Drehgelenk: Panzerseite zur Kamera),
    `evaluate` (Rückstoß, Kamera-Feedback, Atmen, Gehwippen, Magazin tragen und fallen lassen).
  - Belege unter `~/Library/Caches/CubeEscapeBallon/out/BASIC-01-v2.1/ego/` und `…/evidence/clips/ego_BASIC-01-v2.1_*.mp4`.
  - Übersicht in `docs/ego.md`.
- Koordinaten:
  - Autorenmaß (f vorn, u oben, x links) in mm. Blender: (x, −f, u) in Metern, vorn −Y, oben +Z.
  - Unity ist linkshändig mit Y oben und Z vorn. Die Umrechnung **einmal** im Exporter festlegen und mit einem Test absichern
    (Lehre: vertauschte Vorzeichen kosteten in Blender zweimal eine Runde).

## Weg (empfohlen, vom Nutzer nicht im Detail festgelegt)

1. **Export** `tools/export_unity.py` (headless Blender, `ce lock blender`):
   - Pilotwaffe und ein Arm-Set (R und L) als FBX. Jedes Teil bleibt ein eigenes Objekt unter seinem Segment- bzw. Baugruppen-Knoten.
   - Teil-IDs als Objektnamen, Anker als leere Knoten.
   - Dazu `ego.json` mit Haltungen, Griffen, Aktionen, Fingerstellungen, Armmaßen und Materialrollen.
   - `ego.json` erzeugen, nicht von Hand pflegen.
2. **Materialien:** zuerst URP Lit je Rolle aus `basic/kit.py` (`ROLES`: Farbe, Rauheit, Metall). Gebackene Kantenabnutzung und AO
   sind eine spätere Stufe und gehören nicht zu diesem Auftrag. Kein Bloom.
3. **Laufzeit in C#** (eigene Assembly):
   - Waffenhaltung mit Überblendung (`pose_matrix`), Hände aus Griffen (`grip_hand`).
   - Zwei-Knochen-Arm wie `solve_arm`, Fingerstellungen über Gelenkwinkel.
   - Mechanik-Teile aus den `mech`-Kanälen, Magazin tragen und fallen lassen.
   - Rückstoß als gedämpfte Feder, getrenntes Kamera-Feedback.
   - Waffenpendeln aus der Mausbewegung, Gehwippen aus der Laufgeschwindigkeit, Atmen.
   - Aktionen als Zustandsmaschine mit Markern (HandOff, MagOut, MagIn, Chamber, HandOn, Ready, Aimed …) und Übergängen
     (sprint_to_aim, sprint_to_fire, draw_aim, reload_to_switch).
4. **Spielbar:** grauer Testparcours (Boden, Wände, Zielscheiben in 10/25/50 m mit Trefferanzeige).
   - Maus Umsehen, WASD, Shift Sprint, Strg Ducken, Leertaste Springen.
   - Linke Maustaste Feuer (Auto Rifle), rechte Maustaste Zielen mit FOV-Wechsel.
   - R Nachladen (taktisch, oder leer bei leerem Magazin), F Betrachten, 1/2 Ziehen und Wegstecken.
   - Einfaches Fadenkreuz und Munitionszähler.
5. **Tests:**
   - EditMode: JSON-Import und Format, Achsumrechnung, Armlängen, Handgelenkknick ≤ 45° in allen Haltungen.
   - PlayMode: jede Aktion endet, und ihre Marker kommen in der richtigen Reihenfolge.
6. **Belege:** MP4 des Ablaufs und Standbildvergleich Unity gegen Blender, abgelegt unter `~/Library/Caches/CubeEscapeBallon/unity/`.

## Offene Entscheidungen (fragen statt raten)

- Feuerrate und Magazingröße der Pilotwaffe für die Spielbarkeit. Vorschlag: 600 Schuss pro Minute, 30 Patronen. Als „entworfen“ kennzeichnen.
- Ob Mündungsfeuer oder Hülsenauswurf dazukommen. Bisher bewusst weggelassen (schlicht).
- Mauszeiger, Sensitivität und Invertierung: Standardwerte, später einstellbar.

## Bekannte Grenzen aus Blender (nicht hier lösen, nur beobachten)

- An der Hüfte ist die rechte Hand nicht im Bild.
- Beim Durchladen ist die Hand am Ladehebel teils außerhalb des Bildes.
- In der Faust hängt der Daumen nach unten.
