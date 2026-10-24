# Übergabe: BASIC-Roboter als eigenständiges, zerlegtes Modell (0.5 „Teardown“)

Stand 24.10.2026, aus der Sitzung „BALLON Auftrag · Mac“ (Branch `claude/basic-first-light`, Commit mit diesem Dokument).
Für eine **frische Sitzung ohne Gesprächsverlauf** geschrieben.

Opus 5.5, `high` – Grund: Form- und Systementwurf (neue Baugruppenstruktur, Gestaltung nach Nutzerkritik).

## Auftrag des Nutzers

> „Bau dazu mal einen passenden Roboter just 4 fun“ – nach dem ersten Stand: „Viel zu Kantig. Hier mal Inspiration“ (Titan-Bild) –
> und dann: **„Wichtig ist das der Roboter seperat gehalten wird! Er soll auch in Bauteile ‚zerlegt‘ werden. Kopf, Arme, Ober &
> Unterkörper, Beine“**

- **Ziel:**
  1. Den Roboter als **eigenständiges Modell** in eigenem Paket führen, getrennt von Waffen und Ego-Animation.
  2. Ihn in die fünf **Baugruppen** Kopf, Arme, Oberkörper, Unterkörper und Beine **zerlegen**: mit Ankern dazwischen,
     Explosionsansicht und Einzelblättern je Baugruppe, wie bei den Waffen.
  3. Dabei die Silhouette weniger kastig gestalten.
- **Dateien/Zuständigkeit:**
  - Neu: `basic/robot/` mit einem Modul je Baugruppe, etwa `head.py`, `arms.py`, `upper_body.py`, `lower_body.py`, `legs.py`,
    sowie `__init__.py` mit `META`, `ASSEMBLIES`, `ANCHORS` und `POSES`.
  - Ablösen: `basic/arms/robot_figure.py` (heutige Daten, wandert nach `basic/robot/`), `tools/robot_build.py`
    (wird zu Aufbau, Explosionsansicht und Blättern).
  - Dazu `docs/roboter.md` und der Bericht `docs/versions/0.5-teardown.md`.
  - Nicht anfassen: `basic/weapons/`, `basic/pilot/`, `basic/arms/ego.py`, `unity/` (eine parallele Unity-Sitzung arbeitet dort),
    Toolgen, Robogen, Cube Escape.
  - Verträge: keine gemeinsamen. Teil-IDs englisch in snake_case und stabil. Anker heißen `Socket_*`.
- **Prüfen:**
  - `./check` mit einer neuen Konsistenzprüfung: jede Baugruppe hat Teile, jedes Teil gehört zu genau einer Baugruppe, Anker passen
    zusammen, keine Lücke zwischen den Baugruppen in der Grundhaltung.
  - Renderings nur mit `~/Claude/cubeescape-nexogen/ce lock gpu -- …`.
- **Fertig wenn:**
  - Hero-, Nah- und Seitenbild sowie Explosionsansicht liegen vor, dazu ein Kontaktbogen mit den fünf Baugruppen einzeln.
  - Alles auf grauem Hintergrund (`--bg mid`), ohne Bloom.
  - Die Teileliste je Baugruppe ist in `docs/roboter.md` erzeugt.
  - Der Nutzer hat die Form gesehen.
- **Release:** nein. Vor dem Merge kommt die Codex-Prüfung (`./ce judge`, ohne Codex `--opus`).

## Ausgangslage

- **Kein Git-Remote:** Lokalen Branch `claude/ballon-0.5-teardown` von `claude/basic-first-light` abzweigen. Nie auf `main` committen.
- Heutiger Roboter v2: `basic/arms/robot_figure.py`.
  - Segmente `pelvis`, `torso`, `head`, `thigh_R/L`, `shin_R/L` und `foot_R/L`; Teile als konvexe Hüllen aus gerundeten Querschnitten.
  - Hilfen `rsection`, `rsection_top` und `dome`; `_medallion` und `_bolts` als Motive.
  - Aufbau und Rendern in `tools/robot_build.py`: zuerst Waffe, dann IK der Arme an die Pilotwaffe, Glättung `set_sharp_from_angle(40°)`.
  - Bilder unter `~/Library/Caches/CubeEscapeBallon/out/robot/` (`hero_v1_kantig.png` ist der erste, kritisierte Stand).
- Arme: Arm v3 aus `basic/arms/robot_arm.py`.
  - Schale mit Wölbung, Medaillon-Ellbogen, Handgelenkplatte mit Bolzen, vier Finger und Daumen.
  - Formen `box`, `cyl`, `prism`, `plate` und `hull` in `tools/ego_build.py` (`piece_mesh`, `build_arm`).
  - **Entscheidung offen:** Die Roboterarme sollen zur Ego-Hand passen, aber der Nutzer will den Roboter getrennt. Vorschlag:
    `basic/robot/arms.py` übernimmt `robot_arm.parts()` als Ausgangspunkt und darf eigene Abwandlungen führen. Den Nutzer fragen,
    ob sich Änderungen am Ego-Arm automatisch auf den Roboter auswirken sollen.
- Inspiration (nur Prinzipien), `docs/quellen.md` › Q-D2-ARM, Bilder unter `~/Library/Caches/CubeEscapeBallon/refs/`:
  - Heldensilhouette: breite, runde Schultern, V-Rumpf mit schmaler Taille, kräftige Oberschenkel.
  - Helle Platten über dunklem Unteranzug, Gürtel mit Lendenplatte, Helm mit Mittelkamm und schmalem Visier.
  - Schlicht bleiben: keine Stacheln, kein Leuchten außer der Augenlinie, höchstens eine Akzentlinie je Teil.
- **Zielbild vom Nutzer (ChatGPT-Konzept, 24.10.2026):** ein fotorealistisches Konzeptbild, das auf unserem ersten Roboter beruht.
  Das Bild liegt nicht auf der Platte. **Den Nutzer bitten, es in dieser Sitzung erneut anzuhängen**, und es dann unter
  `~/Library/Caches/CubeEscapeBallon/refs/robot-concept.png` sichern. Die Kernpunkte aus seinem Prompt:
  - Schlanker humanoider Körper, lange gepanzerte Beine, schmale Taille; **keine** übermäßig massige Rüstung.
  - Elfenbeinweiße Panzerplatten über dunkelgrauer bis schwarzer mechanischer Unterstruktur, die in den Fugen sichtbar ist.
  - Abgerundete Schulterpanzer mit kreisförmigen Gelenken (unser Medaillon).
  - Kantiger Helm mit schwarzer Gesichtsfläche und schmalem, horizontal leuchtendem cyanblauem Visier.
  - Trapezförmige Brustplatte mit einem einzelnen runden Sensor.
  - Sichtbare Gelenke, kleine Hydraulik, nachvollziehbare Verbindungen.
  - Präzise abgeschrägte Kanten, dezente Schrauben, sauber getrennte Segmente, leichte Gebrauchsspuren.
  - Hero-Ansicht: Dreiviertelansicht im Hochformat, Ganzkörper, leicht niedrige Kamera, Gewehr diagonal mit gesenkter Mündung.
    Dazu ein dunkler, zurückhaltender Sci-Fi-Hangar, warmweißes Hauptlicht, kühles Kantenlicht und ein dezent spiegelnder Boden.
    Das ist eine **zusätzliche** Roboter-Hero-Ansicht. Der graue Standardhintergrund bleibt für Blätter und Waffen.
  - Zum Widerspruch: „Viel zu kantig“ betraf vermutlich das Klotzige (große Blöcke, kurze Beine), nicht die Fasen, denn das
    Zielbild hat bewusst abgeschrägte Kanten. **Vor dem Umbau mit dem Nutzer klären.**
- Bekannte Schwächen von v2:
  - Rumpf und Oberschenkel wirken noch kastig (große ebene Flächen, gerade Seiten).
  - Der Kopf ist im Verhältnis klein.
  - Der Boden zeigt eine harte Horizontkante.
- Vorbild Waffen: `basic/kit.py` (`ASSEMBLIES`, `ANCHORS`, `EXPLODE`, `HERO`) und `tools/blender_build.py`
  (Explosionsansicht, Kontaktbogen). Wo möglich wiederverwenden, statt neu zu schreiben.

## Vorschlag zum Vorgehen

1. Paket `basic/robot/` anlegen, Daten aus `robot_figure.py` übernehmen, Baugruppen und Anker definieren:
   `Socket_Neck`, `Socket_Shoulder_L/R`, `Socket_Waist`, `Socket_Hip_L/R`.
2. Die Arme bekommen als Baugruppe ihre Grundhaltung. Mit Waffe ist das die Haltung `ready` (tiefe Bereitschaft), ohne Waffe `idle`.
3. Silhouette überarbeiten: Querschnitte mit mehr Zwischenstufen, Seiten leicht gewölbt; Oberschenkel nach unten verjüngt;
   Kopf etwa 10 % größer.
4. Explosionsansicht entlang der Anker, Einzelblätter je Baugruppe und Kontaktbogen; danach `docs/roboter.md` erzeugen.
5. Bilder an den Nutzer schicken und erst nach seinem Blick weiter verfeinern.
