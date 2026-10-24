# Übergabe: Roboterarme, Hände und Ego-Animationen im Destiny-Stil

Stand 24.10.2026, aus der Sitzung „BALLON Auftrag · Mac“ (Branch `claude/basic-first-light`, Commit mit diesem Dokument).
Für eine frische Sitzung ohne Gesprächsverlauf geschrieben.

## Auftrag des Nutzers

> „Jetzt müssten nur noch Arme, Hände, ‚Gelenke‘ im Roboterstil entwickelt werden und die Animationen, Positionen, usw.
> Destiny 2 like erstellt werden.“ – „bitte alles umsetzen“ – und ergänzend: **„Allerdings müssen ggf. Animationen überarbeitet
> werden, das würde ich gerne zurzeit alles, so wie die Waffen, möglichst separat halten.“**

## Entscheidung zum Weg (vom Nutzer bestätigt)

**Getrennt halten, wie die Waffen.** Arme, Hände, Gelenke und alle Animationen entstehen **eigenständig in diesem Projekt**
(eigene Daten, eigene Szene, eigene Clips), damit sie frei überarbeitet werden können. Keine Einbindung in Toolgen oder Cube Escape
und keine Laufzeitabhängigkeit von deren Dateien. Die vorhandenen Systeme sind **Referenz und Startwerte** (nur lesen, Werte mit
Quelle übernehmen, nicht verlinken):
- **Toolgen** (`~/Claude/cubeescape-toolgen`): Ego-Arm-Rig „Vertrag 5“ – `toolgen/ego_arms.py`, `data/ego_arms.json`
  (Handfläche, Fingerglieder, Fingerposen open/grip/regrip/trigger/underhand/cup/wrap/mag_hold/pinch, Gelenkgrenzen),
  `data/viewmodels.json` (Ober-/Unterarm 0,32/0,30 m, `hand_scale` 0,65, Profile je Waffenklasse), `data/ego_clips.json`,
  `docs/EGO_CLIPS.md`, `docs/UNITY_EINBAU.md` (Anker, Clipnamen, Marker) – Maße, Gelenkgrenzen und Clipnamen als Startwerte.
- **Robogen** (`~/Claude/cubeescape-robogen`): Roboter `output/CubeEscape_Robot.blend`, Typvarianten, Körperclips
  `output/ANIMATIONS.md`, Maße 1,50 m / Arm 0,42 m / Hand 0,09 m – Formensprache der Gelenke als Vorbild.
- **Motiongen/Reference** (`~/Claude/cubeescape-reference`): gemessene Destiny-Zeiten je Typ (`docs/quellen.md › Q-REF`).
- **Cube Escape**: `Docs/FIRST_PERSON_EQUIPMENT.md` (Zustände, Prioritäten, Ebenen, Marker; `docs/quellen.md › Q-CE`).

Die Roboterarme und Hände werden hier im Stil v2.1 (schlicht, Destiny-Detaildichte, AAA-Material) **neu gestaltet**, als eigenes
Rig in diesem Repo (z. B. `basic/arms/`, eigene Datenquelle wie `basic/weapons/`), maßlich kompatibel zu den Toolgen-Startwerten,
damit eine spätere Zusammenführung möglich bleibt. Eine spätere Übergabe an Toolgen/Cube Escape ist **nicht** Teil dieses Auftrags.

## Ausgangslage in diesem Repo

- 17 BASIC-Waffen (Stil v1) in `basic/weapons/`; **Pilot im Stil v2.1**: `basic/pilot/w01_auto_rifle_v21.py`
  (Formstudie 01, 70 Teile, Anker `Socket_Hand`, `Socket_SupportHand`, `Socket_Sight`, `Socket_Eye`, `Socket_Charge`, Mechanik-Aktionen).
- Regeln: `docs/stilhandbuch.md` (schlicht, grauer Hintergrund `--bg mid`, **kein Bloom**, Skins), `docs/designvertrag.md`.
- Matrix: `docs/haltungen.md` / `data/matrix.json` (Zeilen, Ebenen, Status; Hände überall „offen“), Regeln in `basic/matrix.py`,
  Sichtungen in `data/review.json`.
- Werkzeuge: `tools/blender_build.py` (`--aaa`, `--motion`, `--skins`, `--bg`, `--tag`), `tools/make_clips.py`, `./check`.
- Schwere Läufe nur mit `~/Claude/cubeescape-nexogen/ce lock gpu -- …` (bzw. `blender`).

## Zu liefern (erste Etappe: Pilot BASIC-01 v2.1)

1. **Eigenes Arm-Rig im Roboterstil** (Oberarm, Unterarm, Handgelenk, Hand, Finger mit sichtbaren Gelenken; schlicht, v2.1-Material,
   Skins wie die Waffen), Maße/Gelenkgrenzen aus Toolgen als Startwerte mit Quelle; Datenquelle als Python-Modul, Bauteile und
   Gelenke dokumentiert wie bei den Waffen.
2. **Ego-Szene:** Arme mit der Pilotwaffe an `Socket_Hand` / `Socket_SupportHand`; Ego-Kamera (Startwerte `viewmodels.json`);
   Prüfung: Finger am Abzug, Stützhand am Handschutz, keine Durchdringung, Visierlinie frei.
3. **Haltungen (Posendaten):** Ruhe, Hüfte, Zielen (ADS), gesenkt/Wand, Sprint, Ducken, Luft – je Waffenklasse „rifle“ zuerst.
4. **Aktionen mit Händen (Clips, 30 fps):** Ziehen, Wegstecken, Dauerfeuer mit Rückstoß (Waffe und getrenntes Kamera-Feedback),
   Nachladen taktisch und leer (MagOut/MagIn/Charge mit Stützhand am Ladehebel), Betrachten; Timings aus Q-REF (gemessen) bzw.
   als „vorgeschlagen“ gekennzeichnet.
5. **Übergänge:** Sprint → Zielen, Sprint → Feuer, Nachladen → Wechsel, Abbruch, Wandabsenkung (Tabelle in `docs/haltungen.md`).
6. **Destiny-Anmutung:** gewichtige, leicht überzeichnete Ego-Bewegungen (Waffe kippt beim Nachladen ein, Handgelenk dreht,
   Inspektion zeigt die Ego-Seite); Recherche mit Gameplay-Bildern/Videos erlaubt, Belege nach `docs/quellen.md`.
7. **Belege:** MP4 je Aktion (854 × 480), Kontaktbögen, grauer Hintergrund; Matrix und `data/review.json` ehrlich aktualisieren
   (nur „dargestellt“, was gesichtet ist).
8. **Doku für künftige Waffen:** Abschnitt „Arme und Animation“ im `docs/stilhandbuch.md` (Rig-Quelle, Posenformat, Ablauf, Fehler).

Danach: Übertragung auf weitere Waffenklassen (sidearm, smg, shotgun, sniper, heavy, Bogen, Nahkampf) in eigener Etappe.

## Grenzen

Toolgen, Robogen, Cube Escape, Formgen nicht ändern und nicht einbinden (alles getrennt halten). Nichts auf `main`; Commit nur auf dem eigenen Branch, kein Push/Remote.
Schlicht halten; kein Bloom; grauer Hintergrund. Fertig ist die erste Etappe, wenn das Arm-Rig steht und die Pilotwaffe in allen Haltungen und
Aktionen aus Punkt 3–5 mit Händen als Clip vorliegt, gesichtet ist, `./check` grün ist und Bericht/Handbuch aktualisiert sind.
