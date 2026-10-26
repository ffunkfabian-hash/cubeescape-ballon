# Unity-Spürtest (0.4 „Firstfeel“)

Eigenes Unity-6-Projekt in [`unity/`](../unity) (6000.6.2f1, URP 17.6, Input System 1.20): Die Pilotwaffe BASIC-01 v2.1 mit
den Roboterarmen v3 lässt sich hier aus der Ego-Perspektive selbst spielen. Getrennt von Cube Escape, Toolgen und Robogen. **Blender
bleibt die Referenz.** Unity rechnet die Bewegung live in C# aus denselben Daten und mit denselben Formeln wie
[`tools/ego_build.py`](../tools/ego_build.py). Ein EditMode-Test rechnet jede Aktion lückenlos nach und vergleicht sie an 219 Stichproben mit Blender.

## Ablauf

```bash
BALLON_BAKE_GPU=1 ~/Claude/cubeescape-nexogen/ce lock gpu -- /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup \
    -P "$PWD/tools/export_unity.py"         # FBX + Atlanten + 8 Skins + AgX-LUT + ego.json + Referenz (≈ 20 min; absoluter Pfad: ce lock wechselt das Verzeichnis)
BASIC_OUT=~/Library/Caches/CubeEscapeBallon/unity/blender_out ~/Claude/cubeescape-nexogen/ce lock gpu -- \
    /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P "$PWD/tools/ego_build.py" -- --stills --gpu   # frische Blender-Stills
BALLON_EXPORT_DATA_ONLY=1 ~/Claude/cubeescape-nexogen/ce lock blender -- /Applications/Blender.app/Contents/MacOS/Blender -b \
    --factory-startup -P "$PWD/tools/export_unity.py"   # nur Bewegung/Daten geändert: ego.json + Referenz, ohne Backen (2 s, keine GPU-Sperre)
python3 tools/export_unity.py --check       # ego.json passt zu den Daten und zu den Quellen (SHA-256), läuft in ./check
python3 tools/unity_run.py setup            # URP, Ebene „Viewmodel“, Input System, Materialien je Rolle, Szene
python3 tools/unity_run.py test             # EditMode + PlayMode
python3 tools/unity_run.py build            # unity/Build/BallonFirstfeel.app (Entwicklungsbuild)
python3 tools/unity_run.py capture          # MP4 des Ablaufs (720p, 30 fps) + Kontaktbogen
python3 tools/unity_run.py feel             # MP4 Bewegungsgefühl: Sprint, Zielen aus dem Stand, Sprint → Zielen (0.10)
python3 tools/unity_run.py sway             # MP4 Pendeln: schnelle Drehung hin und zurück, Werte je Bild in feedback.csv
python3 tools/unity_run.py treffer          # MP4 Rückmeldung: Hüftschuss, im Zielen Einzelschuss und Feuerstoß (Ring, Treffer-X)
python3 tools/unity_run.py huefte           # MP4 Hüft-Fadenkreuz (0.13): Hüfte, Hüftfeuer, Zielen, Sprint, Nachladen; Zustand je Bild in feedback.csv
python3 tools/unity_run.py compare          # Standbilder hip/ads/reload/inspect_r gegen die Blender-Stills, SSIM/PSNR/Helligkeit
python3 tools/unity_run.py bench            # Bildzeiten im Parcours (ohne VSync)
python3 tools/unity_run.py bench hangar     # Bildzeiten im Hangar: Vorführlauf durch den Parcours, alle 2,5 s nächste Lichtszene
python3 tools/unity_run.py scenes           # je Szene und Lichtszene Bild vom Start gegen <szene>_<licht>_ref.png (SSIM/PSNR)
python3 tools/unity_run.py course tag       # Vorführlauf durch den Hangar-Parcours als MP4 + Kontaktbogen (Lichtszene wählbar)
open unity/Build/BallonFirstfeel.app        # spielen
```

Alle Unity-Läufe gehen über `ce lock unity`. Protokolle, Testergebnisse und Belege liegen unter
`~/Library/Caches/CubeEscapeBallon/unity/`. Nach jeder Änderung an `basic/arms/*.py` oder der Pilotwaffe den Export wiederholen,
danach `setup` (Materialien, Szene) und `test`. In einem neuen Git-Worktree zuerst `cp -cR <Hauptprojekt>/unity/Library unity/Library`
(bei beendetem Unity; APFS-Klon, Sekunden), sonst importiert der erste Lauf das ganze Projekt neu.

## Steuerung

| Eingabe | Wirkung |
|---|---|
| Maus | umsehen (0,08°/Punkt, im Zielen durch den Zoom geteilt; nicht invertiert) |
| W A S D, Shift | gehen, sprinten (nur vorwärts, nicht im Zielen oder beim Feuern) |
| Strg oder C, Leertaste | ducken, springen |
| linke Maustaste | Dauerfeuer, 720/min wie der Clip `fire_hip` (Frage 7.1 A); Abzug bei leerem Magazin lädt selbst nach |
| rechte Maustaste | zielen (Weltzoom der Klasse aus `ego.json › gameplay.world_zoom`, Automatik 1,9 – vorher fest 1,35; Viewmodel bleibt bei 75° horizontal) |
| R | nachladen: taktisch bei Restmunition, sonst leer (mit Durchladen) |
| F | betrachten; Feuer, Zielen, Nachladen oder Sprint brechen ab |
| 1 / 2 | ziehen / wegstecken (beim Nachladen: `reload_to_switch`) |
| K | Waffen-Skin weiterschalten |
| L | Szene wechseln: Parcours → Szene 1 → … → Parcours (nur wenn Szenen exportiert sind, siehe „Szenen und Parcours“) |
| N | nächste Lichtszene der gezeigten Szene (Tag → Nacht → …); im grauen Parcours ohne Wirkung |
| T | zurück zum Startpunkt der Szene, ein laufender Lauf wird verworfen; ein Lauf startet auch beim erneuten Durchschreiten des Starts |
| Esc, Klick, H | Maus freigeben, Maus fangen, Anzeige ein/aus |

Der Parcours ist grau: Boden mit Meterraster, Wände, Brüstung, Deckungen, Rampe mit Podest, Treppe, ein niedriger Durchgang
zum Ducken und Säulen zum Testen der Wandnähe (`lowered`). Zielscheiben stehen in 10, 25 und 50 m, je drei. Treffer zählt die
Anzeige oben links, Einschläge bleiben als Punkte sichtbar. Ein ständiges Fadenkreuz gibt es seit 0.10 nicht mehr (Nutzerwunsch
25.10.2026). Seit 0.13 zeigt die Hüfte ein ausblendendes Hüft-Fadenkreuz (Entscheidungsliste 4.1 A / 4.2 A, `HipReticle.cs`, Daten aus
`ego.json › gameplay.hip` = Katalog `basic/reticles.py`): Automatik Ring mit Punkt, 3,2 % der Bildhöhe, weiß, fein; es geht beim Hüftfeuer
nach `SPREAD` auf, ist im ersten Bild des Zielens weg, im Sprint nur ein geschlossenes „^“ (1,5 % H), beim Nachladen, Ziehen, Wegstecken,
Betrachten und bei gesenkter Waffe aus. Gezielt wird über das Visier. Rückmeldung nach Visier-Standard 3 §6 (Frage 4.3 A, `AdsFeedback` in `EgoPlayer.cs`):
im Zielen zeigt jeder Schuss für ein Bild einen weißen Ring (2 % der Bildhöhe), jeder Treffer ein X mit freier Mitte (4,5 % H,
mindestens 0,17 s) in Familienfarbe Orange `#E0651E` statt Destiny-Rot; aus der Hüfte nur das X. Der HUD-Punkt (1,1 % H) wartet,
bis Motiongen Widerspruch 3 klärt. Die Werte stehen in `reticles.ADS_FEEDBACK` und als Konstanten in C# (kein Feld in `ego.json`,
sonst neues Format); `export_unity.py --check` (in `./check`) hält sie gleich mit `ADS_FEEDBACK` und der Akzentfarbe. Aufnahmen stempeln Ring und X ins Bild, weil `OnGUI` nicht in der Render-Textur liegt.

## Aufbau

| Teil | Datei | Aufgabe |
|---|---|---|
| Export | [`tools/export_unity.py`](../tools/export_unity.py) | FBX (Waffe: Wurzel → `ASM_*` → Teile, Anker als Leerknoten; Arme: `R_`/`L_`-Segmente → Teile), `ego.json` (`ballon-ego/5`), `ego_reference.json` |
| Daten | `Runtime/EgoData.cs` | JsonUtility-Klassen, Prüfung des Formats |
| Rechnen | `Runtime/BMath.cs`, `Runtime/EgoSolver.cs` | Blender-Kameraraum; `pose_matrix`, Hermite-Kurven, Feder-Nachlauf, Griffe, Zwei-Knochen-Arm mit Drehgelenk, Finger, Magazin, Rückstoßfeder |
| Zustand | `Runtime/EgoController.cs` | Spuren mit Markern, Haltungen (Hüfte, Zielen, Sprint, Ducken, Luft, gesenkt), Übergänge, Überblendung, Live-Ebenen |
| Szene | `Runtime/EgoPlayer.cs`, `EgoRig.cs`, `Range.cs`, `Bootstrap.cs` | Bewegung, Kameras (Welt + Overlay), Treffer, Anzeige, Parcours, Aufnahme- und Vergleichsmodus |
| Szenen (0.8, 0.9) | `Runtime/SceneData.cs`, `MiniJson.cs`, `SceneLoader.cs`, `Course.cs` | Format `ballon-scene/2` (Leser mit Prüfung, JsonUtility kann keine Wörterbücher), Umrechnung Blender → Unity, Lader (Zonenmaterialien, Collider, Lichtszenen, Ziele, Wegmarken), Parcours-Lauf (`CourseRun`) |
| Editor | `Editor/BallonSetup.cs` | Importeinstellungen, Knotenlagen aus `ego.json`, URP, Materialien, Szene, Build |
| Tests | `Tests/EditMode`, `Tests/PlayMode` | siehe unten |

**Format.** `ego.json` hat das Format `ballon-ego/5`. Der Abnehmer ist `unity/` ab 0.13. Die Stufen:
- 2 (0.7): Texturen, AgX-LUT, `emit_only`;
- 3 (0.7.1/0.7.2): Spiegelkarte `spec` statt `mask`, `textures.skins`;
- 4 (0.10): `motion.secondary.aim_freq_hz` und `aim_zeta`. Aktionen, die im Zielen enden (`ego.ends_in_ads`: `aim_in`,
  `sprint_to_aim`, `draw_aim`, `fire_ads`), folgen ihrer Kurve mit einer schnellen, kritisch gedämpften Feder (10 Hz, ζ 1). So schwingt das
  Visier nicht mehr über die Mitte (0.9: 3,3°) und hängt nicht nach (am Ende von `aim_in` 0,8°). Alle übrigen Aktionen behalten
  3,2 Hz bei ζ 0,55.
- 5 (0.13): `gameplay.weapon_type`, `sight`, `world_zoom` (Weltzoom der Klasse, Entscheidungsliste 1.2 A), `zoom_table` (alle Waffentypen)
  und `hip` (Hüft-Fadenkreuz: Form als Grundelemente, Größe, Farbe, Linienstärke, Aufgehprofil, Sprintform), aufgelöst aus `basic/reticles.py`.

Ältere Exporte (`/1` bis `/4`) lehnt `EgoFile.Parse` mit dem Hinweis „neu exportieren“ ab.

**Achsen.** Die Umrechnung steht einmal in `ego.json › axes.to_unity`: Unity = (−x, z, −y) aus Blender. Matrizen werden als
M·B·Mᵀ umgerechnet. Gerechnet wird überall im Blender-Raum, umgerechnet erst beim Setzen der Transforms. Die Netze kommen aus dem
FBX (mit „Apply Transform“). Die Lagen der Knoten setzt der Importer aus `ego.json`, weil das FBX die Kindknoten der Waffe verdreht
und versetzt (beim ersten Import gemessen: 90° am Magazin, bis 218 mm).

**Live statt geskriptet.** Abläufe, Haltungen und Marker kommen aus den Aktionen in `ego.py`, gestreckt mit `TIME_SCALE`. Im Spiel
ersetzt der Controller die geskripteten Ebenen durch live gerechnete:

- Schüsse kommen aus der Kadenz (Übertrag zwischen den Bildern, damit 720/min bei jeder Bildrate gelten) und lösen Impulse in die
  Rückstoßfeder `RECOIL` aus, die Kamera federt getrennt.
- Das Hochziehen klingt erst nach dem Feuern ab.
- Das Gehwippen folgt der Laufgeschwindigkeit, mit den Werten aus `walk`/`sprint`.
- Das Atmen nutzt `BREATHE_ALL`, dazu in Ruhe die `idle_hip`-Formel.
- Der Feder-Nachlauf `SECONDARY` läuft in Echtzeit über alle Spurwechsel.
- Das Pendeln aus der Maus ist dieselbe Feder wie Feder-Nachlauf und Visier-Anflug (`EgoSolver.SpringStep`), seit dem Patch
  unity-abgleich kritisch gedämpft (2,5 Hz, ζ 1; vorher 9 Hz, ζ 0,55 mit 0,22° Überschwingen bei 60/s, 0,30° bei 30/s): Die Waffe zieht höchstens 3°
  gegen die Drehung nach und kehrt in ≈ 0,3 s ohne Überschwingen zurück wie in Destiny (Frage 3.3 A).

Spielwerte, die nicht aus Blender kommen, stehen in `EgoTuning` und `MoveTuning`: Laufgeschwindigkeiten, Zoom, Streuung,
Pendeln und Blickhochziehen. Alle sind entworfen.

## Tests

| Test | prüft |
|---|---|
| `Format_und_Umfang`, `Falsches_Format_wird_abgelehnt` | JSON-Import: Format `ballon-ego/5` (`/1` bis `/4` abgelehnt), 10 Haltungen, 4 Griffe, 19 Aktionen, 72 Teile (Visier v2 aus 0.6), vier Finger, sortierte Schlüssel |
| `Achsumrechnung_Blender_nach_Unity` | Determinante −1, vorn/oben/rechts, Mündung vorn oben, Drehsinn bleibt erhalten |
| `FBX_Import_passt_zur_Achsumrechnung` | Netzgrenzen jedes der 206 Netzobjekte = umgerechnete Blender-Grenzen (≤ 0,5 mm), Maßstab 1 |
| `FBX_Ruhelagen_und_Anker_wie_in_den_Daten` | Lage aller Teile und Anker im importierten Modell |
| `Armlaengen_in_allen_Bildern` | Ober-/Unterarm 0,32/0,30 m in allen Haltungen und allen Bildern aller Aktionen |
| `Handgelenkknick_hoechstens_45_Grad` | Knick ≤ 45° in allen Haltungen und Bildern |
| `Gleich_wie_Blender_Referenz` | Weltmatrizen von Waffe, Mechanik, Magazin, Kamera und 16 Armsegmenten in 219 Stichproben gegen `tools/ego_build.evaluate` (≤ 0,5 mm, ≤ 0,1°) |
| `Jede_Aktion_endet_mit_Markern_in_Reihenfolge` | alle 19 Aktionen enden in ihrer Bildzahl, Marker in Datenreihenfolge, keine NaN |
| Spielablauf (6 Tests) | Kadenz und Magazin, leeres/taktisches/automatisches Nachladen, Zielen hin und zurück (Auge auf der Kameraachse), Betrachten abbrechen, Wegstecken beim Nachladen und Ziehen, Sprintschleife und Übergänge, Ducken/Springen/Wandnähe |
| `Zielen_live_ohne_Ueberschwingen` (0.10) | Live-Controller: Zielen aus der Hüfte, Überschwingen am `Socket_Reticle` < 0,3°, Rest nach 0,45 s < 1°; Messwerte im Testprotokoll |
| `Sprint_live_im_Destiny_Rhythmus` (0.10) | Live-Sprint: 2,9–3,4 Hochpunkte/s, U-Bogen (oben an den Seitenumkehren); Messwerte im Testprotokoll |
| `Zielen_landet_ohne_Ueberschwingen`, `Sprintschritt_wie_ein_Laeufer` (EditMode, 0.10) | Skriptpfad wie Blender: `aim_in`, `sprint_to_aim`, `draw_aim` ohne Überschwingen (< 0,3°), Rest am Ende < 1,5°; Sprintdaten 2,9–3,4 Schritte/s mit U-Bogen |
| `Kadenz_720_wie_fire_hip` (Patch unity-abgleich) | `gameplay.rpm` 720 mit Herkunft M; live bei 60/s und 30/s je 24 Schüsse in 2 s, Bildabstand 5 bzw. 2/3, Kadenz 720 ± 15 /min (der Rest eines Intervalls wird übertragen; vorher bei 30/s 3 Bilder = 600/min) |
| `Pendeln_kehrt_ohne_Ueberschwingen_zurueck` (Patch unity-abgleich) | 360°/s für 0,3 s, Gieren des Laufs gegen einen Zwilling ohne Maus: Auslenkung 0,5–3°, Überschwingen < 0,02°, Rückkehr unter 5 % in 0,22–0,4 s |
| `Nachlade_Abbruch_vor_und_nach_MagIn` (Patch unity-abgleich) | taktisch und leer: Wegstecken 0,1 s vor `MagIn` lässt die Munition (5 bzw. 0), 0,1 s danach ist das Magazin voll und bleibt es nach dem Ziehen |
| `Schuss_Ring_und_Treffer_X` (Patch unity-abgleich) | Spieler in der Szene, Scheibe 3 m vor dem Auge: Hüftschuss ohne Ring, Schuss im Zielen mit Ring für genau 1 Bild, Treffer-X 0,17–0,25 s, Größen 2 % / 4,5 % H, Orange `#E0651E` |
| `Weltzoom_je_Klasse`, `Hueftform_der_Automatik_aus_dem_Katalog`, `Hueft_Fadenkreuz_geht_nach_SPREAD_auf` (EditMode, 0.13) | Weltzoom Scout 2,0 / Handfeuerwaffe 1,15 / MP 1,45 / Automatik 1,9 aus den Daten; Hüftform `ring_dot` 3,2 % H, weiß, fein, Sprint `caret` 1,5 % H, Außenmaß im Bild ±0,5 px; Aufgehen je Bild gleich `reticles.simulate` |
| `Hueft_Fadenkreuz_je_Zustand`, `Weltzoom_im_Spiel_aus_der_Klasse` (PlayMode, 0.13) | Spieler in der Szene bei 30/s: in der Hüfte sichtbar, geht beim Hüftfeuer auf und ab, im ersten Bild des Zielens weg, im Sprint nur „^“, beim Nachladen, Wegstecken und Ziehen aus, danach wieder da; Welt-FOV im Zielen = Zoom 1,9 |
| `Kein_GC_Muell_im_laufenden_Bild` | Gehen, Zielen mit Dauerfeuer, Sprintschleife, Hüft-Fadenkreuz (Aufgehen, Sichtbarkeit, Rastern): kein Speicher im laufenden Bild |
| `Wandnaehe_im_Parcours_senkt_die_Waffe` | vor Säule 1 senkt sich die Waffe (`lowered`), im Freien zurück zur Hüfte |
| `Szene_startet_und_spielt_den_Ablauf` | Szene lädt, Viewmodel-Ebene, Vorführablauf feuert, lädt leer nach, betrachtet |
| Szenen, EditMode (11) | `SceneDataTests` mit Fixture `Tests/EditMode/scene_fixture_v2.json` (2 Zonen, 2 Lichtszenen, Kurs mit 2 Kontrollpunkten und 3 Zielen): Format und Umfang, Atlas je Zone und Lichtszene, `ballon-scene/1` und `/0` mit Hinweis „neu bauen (tools/scene_build.py)“ abgelehnt (Fixture `scene_fixture_v1.json`), 19 Lücken und Widersprüche abgelehnt, Szene ohne Parcours gültig, Umrechnung gleich `ego.json › axes.to_unity`, Collider, Startpunkt und Gier, Auslösequader, Zielscheiben und Strecke, Lichtmaßstab und Atlas-Helligkeit, `MiniJson` |
| Parcours, EditMode (10) | `CourseTests`: gültiger Lauf mit Zeit, Kontrollpunkten und Treffern; falsche Reihenfolge und fehlende Kontrollpunkte ergeben keine Zeit; Neustart über den Start; Start nach dem Ziel; Spawn im Quader und Reset (T); Treffer vor dem Start; Bestzeit nur wenn besser und in `PlayerPrefs`; Anzeigetexte ohne Speicher je Bild; Wegmarken (Anzahl, flach, nach oben) |
| Szenen, PlayMode (6) | `ScenePlayTests` mit der Fixture-Szene „Testkurs“ (Umgebung als Quader im Test, kein FBX; Atlanten als kleine Testtexturen): Lader (Zonenmaterialien, Atlas der Lichtszene, `_BaseColor`, Collider, Lichtgruppen, Ziele mit Normale und Radius, Wegmarken, Spieler steht am Start auf dem Boden, Anzeige ohne GC); Schießstand-Ziele ohne Parcours; Lichtszene N tauscht Atlas, Himmel, Umgebungslicht, Lichter, Sonde ohne Neuaufbau der Geometrie und ohne GC; Tasten N und T; L hin und zurück mit Tastenereignis; Parcours danach unverändert |
| Parcours, PlayMode (3) | gültiger Lauf per Teleport durch Start, Kontrollpunkte und Ziel (mit echtem Schuss auf ein Ziel, Bestzeit in `PlayerPrefs`, Marker im Log, Neustart über den Start); falsche Reihenfolge ergibt keine Zeit; kein GC je Bild im laufenden Lauf (`Step`, Zeit, Anzeigetexte) |
| Exportierte Szenen, PlayMode (2) | `Exportierte_Szenen_…`: lädt alle exportierten Szenen (0.9: Hangar), wechselt jede Lichtszene (Atlas in jeder Zone, Himmel, eine Lichtgruppe an), läuft jeden Parcours per Teleport der Reihe nach durch. `Vorfuehrlauf_schafft_jeden_Parcours`: der `RouteRunner` läuft jeden Parcours mit festen Schritten (1/30 s) und echten Bewegungen (Springen, Ducken, Kollision) und muss gültig unter der Richtzeit ankommen (Hangar: 33,0 s, 9/14 Treffer; vor 720/min 32,1 s) – fällt ein Hindernis aus Sprunghöhe oder Kapselhöhe, schlägt er fehl. Beide überspringen sich ohne exportierte Szene |

## Szenen und Parcours (0.8 Hangar, 0.9 Parcours)

Neben dem grauen Parcours lädt Unity Räume aus Blender im Format `ballon-scene/2` ([szenen-format.md](szenen-format.md), Erzeuger
`tools/scene_build.py`). Die Dateien liegen in `unity/Assets/Ballon/Generated/Scenes/<name>/`: `scene_<name>.json`, `<name>.fbx` und je
Lichtszene und Zone ein Lichtatlas (`<name>_<licht>_<zone>.png`). Ältere Dateien (`ballon-scene/1`) lehnt `SceneFile.Parse` mit
„neu bauen (tools/scene_build.py)“ ab; `setup` überspringt sie mit einer Warnung, das Spiel läuft ohne sie weiter.

- **Einrichten:** `python3 tools/unity_run.py setup` sucht `Generated/Scenes/*/scene_*.json`, importiert JSON, FBX und alle Atlanten
  (Atlas = jede PNG der Szene außer `*_ref.png` und `*_view.png`: sRGB-Farbe, 4096², Mips, Clamp), legt je Szene eine Unlit-Vorlage
  `Generated/Materials/Scene_<name>.mat` an und trägt JSON, FBX, Vorlage und die Atlasliste (Lichtszene · Zonenzahl + Zone, wie im
  JSON) in die `Bootstrap`-Felder `sceneJson`, `scenePrefabs`, `sceneMaterials`, `sceneAtlases` ein. Unvollständige Szenen (FBX oder ein
  Atlas fehlt, falsches Format) überspringt `setup`. Ohne Szenen läuft alles wie zuvor.
- **Tasten:**

  | Taste | Wirkung |
  |---|---|
  | L | Szene wechseln: Parcours (grau) → Szene 1 → … → Parcours |
  | N | nächste Lichtszene der gezeigten Szene (Tag → Nacht → … → Tag); im grauen Parcours ohne Wirkung |
  | T | zurück zum Startpunkt der Szene, ein laufender Lauf wird verworfen (im grauen Parcours: zum Parcours-Start) |
  | R | bleibt Nachladen (und lädt nichts neu) |

  Den Neustart eines Laufs gibt es zweimal: erneut den Starttor-Quader durchschreiten oder T drücken.
- **Umschalten der Szene:** Gebaut wird eine Szene beim ersten Zeigen und bleibt danach (ausgeschaltet) im Speicher. Die Anzeige nennt
  Szene und Licht („Szene Hangar (L)   Licht Tag (N)“). Den Text baut sie nur bei Änderung neu (kein GC je Bild, Test).
- **Umschalten der Lichtszene (N):** tauscht nur die Atlanten der Zonenmaterialien (`_BaseMap`, `_BaseColor`), die Gruppe der Viewmodel-
  Lichter samt Lichtflächen, Umgebungslicht, Himmel (Kamerahintergrund und Sondenhintergrund) und rendert die Reflexionssonde neu.
  Geometrie, Collider, Materialinstanzen, Zielscheiben und Lauf bleiben unberührt. Alle Lichtgruppen entstehen beim Laden der Szene
  (ausgeschaltet), so kostet das Umschalten selbst nur ein paar Materialeigenschaften und eine Sonde; je Bild fällt danach kein Speicher an
  (Test). Die zuletzt gezeigte Lichtszene einer Szene bleibt beim Szenenwechsel erhalten.
- **Zonen:** Je Zone eine Kopie der Unlit-Vorlage mit dem Atlas der aktiven Lichtszene in `_BaseMap` und `_BaseColor` = `scale` als
  `.gamma` (Materialfarben sind Gamma-Werte; Atlas = Licht / `scale`). Jeder Renderer des FBX bekommt das Material der Zone, deren
  `objects` seinen Knotennamen (oder den eines Elternknotens) nennen; ohne Treffer gilt Zone 1 mit einer Warnung im Log. Alle Renderer
  ohne Schatten und ohne Sondenspiegelung, der FBX braucht die Atlas-UVs im ersten UV-Satz. Kollision kommt nur aus `colliders`
  (Quader, Blender → Unity wie `axes.to_unity`: Mitte (−x, z, −y), Kantenlängen (x, z, y)), nicht aus dem FBX.
- **Spieler:** Start an `spawn.pos` (Füße, 2 cm Spiel), Blick nach `spawn.yaw_deg`. Blender dreht gegen den Uhrzeigersinn positiv,
  Unity im Uhrzeigersinn, daher Unity-Gier = −`yaw_deg`. Zurück im Parcours steht der Spieler wieder am Start (0 / 0,01 / 1,5).
- **Himmel und Umgebungslicht:** `sky` = Kamerahintergrund und Hintergrund der Reflexionssonde (Farbe × Stärke, linear gerechnet, als
  Gamma-Wert gesetzt). `ambient` = einheitliches Umgebungslicht für das Viewmodel. Kein Nebel, keine Sonne des Parcours.
- **Lichter nur für das Viewmodel:** `Light.cullingMask` = Ebene „Viewmodel“, ohne Echtzeitschatten. Intensität in Unity-Einheiten:

  | Art | Unity-Intensität | Form |
  |---|---|---|
  | `area` | P/π² | Spotlicht 150° / 60° wie `StudioLike`, zusätzlich leuchtende Fläche (Kante `size_m`, Strahldichte P/(π·A)) auf der Ebene `StudioEmitLayer`, die nur die Reflexionssonde sieht |
  | `spot` | P/(4π²) | Spotlicht mit `angle_deg` (fehlt er: 90°), innen 60 % davon |
  | `point` | P/(4π²) | Punktlicht |
  | `sun` | S/π | Richtungslicht |

  P/(4π²) für Spot und Punkt ist aus der Strahlstärke P/(4π) von Cycles abgeleitet (nicht gemessen, anders als P/π² für Flächen).
- **Reflexionssonde:** Wird beim Wechsel der Szene und der Lichtszene neu gerendert (256², HDR, auf Augenhöhe am Start, Größe =
  Umgebung + 2 m). Sie sieht die unbeleuchtete Umgebung plus die Lichtflächen der aktiven Lichtszene, nicht das Viewmodel.
- **Zielscheiben:** `course.targets`: Mitte `pos`, Ringseite entlang `normal` (waagerecht gedreht), Radius `radius`. Der Pfosten reicht von
  der Scheibe bis zur Oberkante des höchsten Colliders darunter (sonst 1,45 m). Zusätzlich wie in 0.8 `targets` (Schießstand ohne
  Strecke: Pfosten 1,45 m, Radius nach Entfernung 0,30 / 0,45 / 0,60 m, Anzeige führt die Treffer je Entfernung).
- **Parcours-Lauf** (`Runtime/Course.cs`, `CourseRun`): Start, Kontrollpunkte und Ziel sind achsparallele Auslösequader
  (`course.start`, `checkpoints`, `finish`); geprüft wird der Körpermittelpunkt des Spielers (Füße + 0,9 m) je Spielschritt.
  - *Start:* Zeit läuft ab dem Durchschreiten des Start-Quaders (Eintritt, nicht Verweilen). Erneutes Durchschreiten startet neu und
    setzt Kontrollpunkte, Zeit und Trefferzählung zurück. Steht der Spieler beim Laden schon im Quader, startet das nichts (der
    erste Schritt merkt sich nur den Stand).
  - *Kontrollpunkte:* in der Reihenfolge der Daten. Ein späterer Kontrollpunkt zuerst zählt nicht, die Anzeige nennt den fehlenden.
  - *Ziel:* nur wenn alle Kontrollpunkte in Reihenfolge passiert sind, stoppt die Zeit und gilt als Lauf. Ohne alle Kontrollpunkte
    bleibt der Lauf offen, die Anzeige sagt „Ziel nicht gewertet“, es gibt keine Zeit. Fallen Start und Ziel in denselben Quader
    (Runde), gewinnt das Ziel, sobald alle Kontrollpunkte da sind; sonst startet das Tor neu.
  - *Treffer:* getroffene Zielscheiben dieses Laufs von allen („Ziele n/m“); Treffer vor dem Start zählen nicht, mehrere Treffer an
    derselben Scheibe zählen einmal.
  - *Anzeige:* oben links Laufzeit (Zehntel, groß), Zustand, darunter Kontrollpunkte n/m, Ziele n/m, Richtzeit (`par_time_s`),
    Bestzeit und Hinweise. Die Zeit kommt aus einer Tabelle, der Rest wird nur bei Änderung neu gebaut: kein Speicher je Bild.
  - *Bestzeit:* je Szene in `PlayerPrefs` (`Ballon.Best.<szene>`), nur gültige Läufe, nur wenn besser.
  - *Ergebnis im Log (für Tests und Belege):*
    `[Ballon] Lauf: gültig szene=… zeit=… kontrollpunkte=2/2 treffer=1/3 richtzeit=… bestzeit=… neue_bestzeit=ja|nein`
    bzw. `[Ballon] Lauf: ungültig szene=… kontrollpunkte=1/2 treffer=…` (Ziel ohne alle Kontrollpunkte).
  - *Wegmarken:* flache Pfeile alle 1,5 m entlang `route` (ein Netz, Unlit, dezentes Blau, 3 cm über dem Boden, ohne Schatten).
- **Grenzen:** URP beleuchtet ein Objekt mit höchstens vier Zusatzlichtern (die nächsten); bei mehr Lichtern in der Szene sehen Waffe und
  Arme nur diese. Das Viewmodel wirft Schatten nur auf sich selbst, nicht auf die Umgebung, und die Umgebung keine auf das Viewmodel.
  Die Sonde sitzt am Startpunkt (kein Wechsel beim Gehen). Flächenlichter sind Spotlichter, keine echten Flächen. Was Cycles aus dem Raum
  zurückwirft (indirektes Licht auf die Waffe), fehlt, soweit es nicht in den Flächenlichtern steckt. Auslösequader sind achsparallel
  (keine Drehung); der Prüfpunkt ist eine Höhe, nicht der ganze Körper: ein sehr dünner Quader kann bei hoher Geschwindigkeit und
  niedriger Bildrate übersprungen werden (Sprint 6,8 m/s bei 60 Bildern/s = 0,11 m je Schritt; Quader mindestens 0,3 m dick bauen).
  Die Bestzeit ist pro Rechner (PlayerPrefs), ohne Bestenliste. Ein Referenzbild (`reference`) und `sources` liest Unity nicht.

### Vorführlauf, Vergleich und Leistung (0.9)

- **Vorführlauf** (`Runtime/RouteRunner.cs`, eine `IEgoInput`): läuft die Wegpunkte von `course.route` ab (erreicht bei 0,7 m
  waagrecht), dreht mit 240°/s, sprintet auf geraden Stücken über 6 m. Vor einem Hindernis in 0,45 m Höhe springt er, vor einem
  Balken in 1,5 m Höhe bei freier Kniehöhe (und solange eine Decke unter 1,75 m über ihm ist) duckt er sich; steckt er 1,2 s fest,
  springt er. Scheiben bis 20 m in ±55° zur Laufrichtung mit freier Sicht und Ringseite zum Läufer visiert er an (160°/s, Zielen)
  und schießt, sobald das Fadenkreuz unter 1,2° liegt; höchstens 2,5 s je Scheibe. Entworfen für Belege und den Test, kein Spielerersatz.
- **MP4** (`unity_run.py course <licht>`): Build mit `-ballonCourse <dir> -ballonScene hangar -ballonLighting <licht>`, 1280 × 720,
  30 Bilder/s mit festen Schritten, Beschriftung mit Laufzeit, Kontrollpunkten und Treffern aus `frames.csv`, Kontaktbogen mit 12
  Bildern. Die Bestzeit des Spielers in `PlayerPrefs` stellt der Vorführlauf danach wieder her. Exit 2, wenn der Lauf ungültig war.
- **Vergleich je Lichtszene** (`unity_run.py scenes`): Bilder `<szene>_<licht>_umgebung.png` (ohne Waffe und ohne Wegpfeile, die es
  in Blender nicht gibt) und `<szene>_<licht>_waffe.png`, Vergleich gegen `scenes/<szene>_<licht>_ref.png` aus `scene_build.py`.
- **Leistung** (`unity_run.py bench hangar`): Vorführlauf durch den Parcours, alle 2,5 s die nächste Lichtszene; Ergebnis in
  `bench_hangar.json` mit Mittel, p95, p99 und Höchstwert. Werte stehen im Versionsbericht [0.9](versions/0.9-parcours.md).

## Material, Licht und Tonwerte wie Blender (0.7)

Grundsatz (AGENTS.md): Unity folgt der Blender-Vorlage so nah wie möglich, Blender bleibt die Quelle.

- **Backen** (`tools/bake_unity.py`, im Export): Je FBX entsteht ein Atlas (Waffe 4096², Arme 2048²) aus `kit.aaa_nodes`:
  - Diffusfarbe mit Kantenabrieb und Schmutz;
  - Spiegelfarbe F0 je Pixel mit Glätte (Spezular-Modus, 0.7.1). F0 = 0,08 · Specular IOR Level, so wie Blender Graphit und
    Gummi nur etwa 2 % spiegeln lässt;
  - Normale (Mikrorelief) und AO.
  - Teile mit gleichem Objektraum backen als eine Kopie: 4 min statt 58 min.
  - Die Armsegmente werden zum Backen nebeneinandergelegt. In Ruhe stehen sie alle im Ursprung, und dann rechnen Abrieb und AO
    fremde Finger mit.
  - Der Abrieb wird mit 64 Samples gebacken.
  - Leuchtende und durchsichtige Rollen (Energie, Absehen, Gläser) bleiben ungebacken. Sie haben eigene Materialien, mit
    Leuchtstärke `emit · 1,6` wie in Blender.
- **Tonwerte:** Die Blender-Ansicht AgX mit dem Look „Medium High Contrast“ ist als 3D-LUT gebacken, mit log2-Formung als
  Eingang. Der Shader `Ballon/AgX` wendet sie als Vollbild-Durchgang am Ende des Kamerastapels an, im Renderer „Out“ der
  Viewmodel-Kamera. Dafür ist HDR an; Bloom bleibt aus.
- **Studio (Vergleichsmodus):**
  - Die vier Flächenlichter aus `setup_aaa` sind weiche Spotlichter mit der Intensität P/π², ohne Echtzeitschatten. Cycles
    wirft bei Lichtern dieser Größe kaum Schatten, die Kontaktschatten stecken im AO.
  - Der Hintergrundverlauf entspricht `BACKDROPS['mid']`.
  - Die Umgebung ist #8C96A3 × 0,45.
  - Die Lichtflächen liegen mit voller Blender-Strahldichte P/(π·A) in der Reflexionssonde (Messreihe 0 / 0,25 / 0,5 / 1).
  - Gerendert wird in ein HDR-Ziel (`Bootstrap.HdrTarget`), weil URP das Zielformat für den Zwischenpuffer übernimmt.
  - Materialfarben sind in Unity Gamma-Werte: lineare Werte über `SetColor(farbe.gamma)` setzen.
- **Messung:** `compare` schreibt SSIM, PSNR und Helligkeit je Pose nach `compare/metrics.json`.

## Skins (0.7.2)

Die acht Waffen-Skins aus `kit.SKINS` sind gebacken: Standard, Nachtschicht, Polar, Kobalt, Wüste, Tarnung, Gebraucht und
Eloxal.

- **Backen:** Je Skin entstehen eine Farbkarte (Diffus) und eine Glanzkarte (Spiegelfarbe plus Glätte) der Waffe, etwa 2 min
  je Skin auf der GPU. Normale und AO teilen sich alle Skins, weil Form und UVs gleich sind.
- **Arme:** bleiben im Standard; ein Waffen-Skin färbt die Roboterarme nicht.
- **Im Spiel:** Taste K schaltet durch, die Anzeige nennt den Skin (`EgoPlayer.SetSkin`).
- **Beleg:** `python3 tools/unity_run.py skins` erzeugt einen Kontaktbogen (hip und inspect_l je Skin) in
  `…/unity/firstfeel_skins.png`.
- **Grenze:** In der Haltung inspect_l zeigen die Seitenflächen direkt zur Kamera. Dort glänzen dunkle Flächen stärker als in
  Blender, dunkle Skins (Nachtschicht, Kobalt) wirken heller. Das ist dieselbe Restabweichung wie unter Grenzen (keine
  Abschattung der Spiegelung).

Zeiten des Exports mit Backen: Waffe 3 min, Arme 0,5 min, 7 Skins 15 min, gesamt ≈ 20 min ohne Wartezeit an der GPU-Sperre.

## Grenzen

Entscheidung des Nutzers (25.10.2026): Die Restabweichungen bleiben so. „Lassen wir es so wie es ist. Das ist ok.“

Ganz 1:1 geht es nicht, weil Unity in Echtzeit rastert, während Cycles Licht verfolgt. Gemessen über Waffe und Armen bleibt eine
mittlere Abweichung von etwa 0,08, die SSIM im Ausschnitt liegt bei 0,86–0,89 (Bericht 0.7). Was bleibt:

- **Dunkle Teile zu hell:** Schwarzes Gehäuseunterteil und eloxierte Platte sind etwas heller. Die Reflexionssonde kennt keine
  Abschattung durch Waffe und Arm.
  - Möglich: Spiegelung über das gebackene AO abdunkeln.
- **Glas dunkel:** Glasring und Fenster wirken dunkel statt hellblau, denn Glas hat keine Durchlässigkeit und keinen Klarlack.
  - Möglich: ein eigener Glas-Shader mit Fresnel.
- **Creme kühler:** Indirektes Licht (Mehrfachstreuung) fehlt, Unity hat nur einheitliches Umgebungslicht.
  - Möglich: indirektes Licht mitbacken. Das gilt dann nur für die Studiohaltung.
- **Glasvarianten:** Staub, Kratzer und Riss sind einfaches transparentes Lit.
- **Parcours:** Dieselben Materialien und dieselbe LUT; das Licht dort ist entworfen, nicht aus Blender.
- **Wie in Blender:** An der Hüfte ist die rechte Hand nicht im Bild, die Hand am Ladehebel ist teils außerhalb, und in der Faust
  hängt der Daumen nach unten.
- **Spieldetails:** Kein Ton, kein Mündungsfeuer, kein Hülsenauswurf (offene Entscheidung des Nutzers). Das fallende Magazin wird
  nicht zum Weltobjekt.
