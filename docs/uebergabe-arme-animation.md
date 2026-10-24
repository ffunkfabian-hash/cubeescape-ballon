# Übergabe: Roboterarme, Hände und Ego-Animationen im Destiny-Stil

Stand 24.10.2026, aus der Sitzung „BALLON Auftrag · Mac“ (Branch `claude/basic-first-light`, Commit mit diesem Dokument).
Für eine frische Sitzung ohne Gesprächsverlauf geschrieben.

## Auftrag des Nutzers

> „Jetzt müssten nur noch Arme, Hände, ‚Gelenke‘ im Roboterstil entwickelt werden und die Animationen, Positionen, usw.
> Destiny 2 like erstellt werden.“ – auf Rückfrage: „bitte alles umsetzen“ (Weg 1, siehe unten).

## Entscheidung zum Weg (vom Nutzer bestätigt)

**Weg 1 – vorhandenes Rig nutzen.** Kein zweites Arm-Rig in diesem Projekt. Grundlage sind
- **Toolgen** (`~/Claude/cubeescape-toolgen`, nur lesen): gemeinsames Ego-Arm-Rig „Vertrag 5“ – `toolgen/ego_arms.py`,
  `data/ego_arms.json` (Handfläche, Fingerglieder, Fingerposen open/grip/regrip/trigger/underhand/cup/wrap/mag_hold/pinch,
  Gelenkgrenzen), `data/viewmodels.json` (Ober-/Unterarm 0,32/0,30 m, `hand_scale` 0,65, Profile je Waffenklasse),
  `data/ego_clips.json`, `docs/EGO_CLIPS.md`, `docs/UNITY_EINBAU.md` (Anker, Clipnamen, Marker).
- **Robogen** (`~/Claude/cubeescape-robogen`, nur lesen): Roboter `output/CubeEscape_Robot.blend`, Typvarianten `output/Types/`,
  Körperclips `output/ANIMATIONS.md` (Idle, Walk, Sprint, Strafe, Jump, Land, Crouch …), Maße 1,50 m / Arm 0,42 m / Hand 0,09 m.
- **Motiongen/Reference** (`~/Claude/cubeescape-reference`, nur lesen): gemessene Destiny-Zeiten je Typ, zusammengefasst in
  `docs/quellen.md › Q-REF` dieses Repos (Ziehen, Zielen, Nachladen, Feuerrate, MagOut/MagIn).
- **Cube Escape** (nur lesen): `Docs/FIRST_PERSON_EQUIPMENT.md` (Zustände, Prioritäten, Ebenen: Posendaten / Clip / prozedural,
  Marker), siehe `docs/quellen.md › Q-CE`.

Wenn die Toolgen-Arme optisch nicht zum v2.1-Stil passen (Gelenke, Panzerplatten, Material), wird das als **Auftrag an Toolgen**
formuliert (Datei in diesem Repo, z. B. `docs/auftrag-toolgen-arme-v2.md`) – nicht hier umgebaut.

## Ausgangslage in diesem Repo

- 17 BASIC-Waffen (Stil v1) in `basic/weapons/`; **Pilot im Stil v2.1**: `basic/pilot/w01_auto_rifle_v21.py`
  (Formstudie 01, 70 Teile, Anker `Socket_Hand`, `Socket_SupportHand`, `Socket_Sight`, `Socket_Eye`, `Socket_Charge`, Mechanik-Aktionen).
- Regeln: `docs/stilhandbuch.md` (schlicht, grauer Hintergrund `--bg mid`, **kein Bloom**, Skins), `docs/designvertrag.md`.
- Matrix: `docs/haltungen.md` / `data/matrix.json` (Zeilen, Ebenen, Status; Hände überall „offen“), Regeln in `basic/matrix.py`,
  Sichtungen in `data/review.json`.
- Werkzeuge: `tools/blender_build.py` (`--aaa`, `--motion`, `--skins`, `--bg`, `--tag`), `tools/make_clips.py`, `./check`.
- Schwere Läufe nur mit `~/Claude/cubeescape-nexogen/ce lock gpu -- …` (bzw. `blender`).

## Zu liefern (erste Etappe: Pilot BASIC-01 v2.1)

1. **Ego-Szene:** Toolgen-Arme (lesend importiert oder aus `ego_arms.json` nachgebaut, ohne Toolgen-Dateien zu ändern) mit der
   Pilotwaffe an `Socket_Hand` / `Socket_SupportHand`; Ego-Kamera nach `viewmodels.json`; Prüfung: Finger am Abzug, Stützhand
   am Handschutz, keine Durchdringung, Visierlinie frei.
2. **Haltungen (Posendaten):** Ruhe, Hüfte, Zielen (ADS), gesenkt/Wand, Sprint, Ducken, Luft – je Waffenklasse „rifle“ zuerst.
3. **Aktionen mit Händen (Clips, 30 fps):** Ziehen, Wegstecken, Dauerfeuer mit Rückstoß (Waffe und getrenntes Kamera-Feedback),
   Nachladen taktisch und leer (MagOut/MagIn/Charge mit Stützhand am Ladehebel), Betrachten; Timings aus Q-REF (gemessen) bzw.
   als „vorgeschlagen“ gekennzeichnet.
4. **Übergänge:** Sprint → Zielen, Sprint → Feuer, Nachladen → Wechsel, Abbruch, Wandabsenkung (Tabelle in `docs/haltungen.md`).
5. **Destiny-Anmutung:** gewichtige, leicht überzeichnete Ego-Bewegungen (Waffe kippt beim Nachladen ein, Handgelenk dreht,
   Inspektion zeigt die Ego-Seite); Recherche mit Gameplay-Bildern/Videos erlaubt, Belege nach `docs/quellen.md`.
6. **Belege:** MP4 je Aktion (854 × 480), Kontaktbögen, grauer Hintergrund; Matrix und `data/review.json` ehrlich aktualisieren
   (nur „dargestellt“, was gesichtet ist).
7. **Doku für künftige Waffen:** Abschnitt „Arme und Animation“ im `docs/stilhandbuch.md` (Rig-Quelle, Posenformat, Ablauf, Fehler).

Danach: Übertragung auf weitere Waffenklassen (sidearm, smg, shotgun, sniper, heavy, Bogen, Nahkampf) in eigener Etappe.

## Grenzen

Toolgen, Robogen, Cube Escape, Formgen nicht ändern. Nichts auf `main`; Commit nur auf dem eigenen Branch, kein Push/Remote.
Schlicht halten; kein Bloom; grauer Hintergrund. Fertig ist die erste Etappe, wenn die Pilotwaffe in allen Haltungen und
Aktionen aus Punkt 2–4 mit Händen als Clip vorliegt, gesichtet ist, `./check` grün ist und Bericht/Handbuch aktualisiert sind.
