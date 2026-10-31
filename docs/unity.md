# Unity-Spürtest (0.4 „Firstfeel“)

Eigenes Unity-6-Projekt in [`unity/`](../unity) (6000.6.2f1, URP 17.6, Input System 1.20): Die Pilotwaffe BASIC-01 v2.1 mit
den Roboterarmen v3 lässt sich hier aus der Ego-Perspektive selbst spielen. Getrennt von Cube Escape, Toolgen und Robogen. **Blender
bleibt die Referenz.** Unity rechnet die Bewegung live in C# aus denselben Daten und mit denselben Formeln wie
[`tools/ego_build.py`](../tools/ego_build.py). Ein EditMode-Test rechnet jede Aktion lückenlos nach und vergleicht sie an 219 Stichproben mit Blender.

## Ablauf

```bash
BALLON_BAKE_GPU=1 ~/Claude/cubeescape-nexogen/ce lock gpu -- /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup \
    -P "$PWD/tools/export_unity.py"         # FBX + Atlanten + Skins (nur SKIN_WEAPONS, 0.33) + AgX-LUT + ego.json + Referenz (≈ 7 min je neue Waffe ohne Skins, 28 mit; absoluter Pfad: ce lock wechselt das Verzeichnis)
# Skins einer Waffe nachbacken: ID in export_unity.SKIN_WEAPONS eintragen (der Plan backt sie dann neu) oder einmalig BALLON_BAKE_SKINS=all
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
python3 tools/unity_run.py sprint|wechsel|rueckstoss   # MP4 (0.15): Sprint-Hub und Sprint → Zielen; Waffenwechsel; Rückstoß Hüfte/Zielen
python3 tools/unity_run.py feuer            # MP4 (0.16): Mündungsfeuer und Hülsen aus der Hüfte und im Zielen
python3 tools/unity_run.py volley           # MP4 (0.22): Wechsel durch alle fünf Waffen, Impuls-Salven Hüfte/Zielen, Portal A und B
python3 tools/unity_run.py projektil    # MP4 (0.34): Granatwerfer, Raketenwerfer, Explosionen
python3 tools/unity_run.py strahlen      # MP4 (0.34): Spurgewehr, Fusion, lineare Fusion, Bogen
python3 tools/unity_run.py streuschuss  # MP4 (0.34): Schrot, Automatik, Handfeuerwaffe (Einschläge)
python3 tools/unity_run.py fuellstand   # MP4 (0.34): MG, Granatwerfer, Handfeuerwaffe (Hülsen, Füllstand)
BALLON_CAPTURE_EXTRA="-ballonFps 60 -ballonKey 1" python3 tools/unity_run.py feel   # Messlauf: 60/s, Waffe und Arme auf Magenta, ohne Fadenkreuz (…_mess)
BALLON_TEST_FILTER="Name1|Name2" python3 tools/unity_run.py test   # nur diese Tests (Gegenproben, 0.32)
open unity/Build/BallonFirstfeel.app --args -ballonFov 100   # Welt-Bildwinkel 100° waagrecht (50–120); Waffe und Arme bleiben bei 75° (A9, 0.32)
python3 tools/unity_run.py compare          # Standbilder hip/ads/reload/inspect_r gegen die Blender-Stills, SSIM/PSNR/Helligkeit
python3 tools/unity_run.py bench            # Bildzeiten im Parcours (ohne VSync)
python3 tools/unity_run.py bench hangar     # Bildzeiten im Hangar: Vorführlauf durch den Parcours, alle 2,5 s nächste Lichtszene
python3 tools/unity_run.py scenes           # je Szene und Lichtszene Bild vom Start gegen <szene>_<licht>_ref.png (SSIM/PSNR)
python3 tools/unity_run.py course tag       # Vorführlauf durch den Hangar-Parcours als MP4 + Kontaktbogen (Lichtszene wählbar)
open unity/Build/BallonFirstfeel.app        # spielen
```

Vor einem Unity-Lauf lässt sich C# in einer Sekunde prüfen: `dotnet build` eines Wegwerf-csproj (außerhalb des Repos) gegen `Unity.app/Contents/Resources/Scripting/Managed/UnityEngine/*.dll`, `unity/Library/ScriptAssemblies/*.dll` und NUnit aus `Library/PackageCache` (0.20). Alle Unity-Läufe gehen über `ce lock unity`. Protokolle, Testergebnisse und Belege liegen unter
`~/Library/Caches/CubeEscapeBallon/unity/`. Nach jeder Änderung an `basic/arms/*.py` oder der Pilotwaffe den Export wiederholen,
danach `setup` (Materialien, Szene) und `test`. In einem neuen Git-Worktree zuerst `cp -cR <Hauptprojekt>/unity/Library unity/Library`
(bei beendetem Unity; APFS-Klon, Sekunden), sonst importiert der erste Lauf das ganze Projekt neu.

## Steuerung

| Eingabe | Wirkung |
|---|---|
| Maus | umsehen (0,08°/Punkt, im Zielen durch den Zoom geteilt; nicht invertiert) |
| W A S D, Shift | gehen, sprinten (nur vorwärts, nicht im Zielen oder beim Feuern) |
| Strg oder C, Leertaste | ducken, springen |
| linke Maustaste | Feuer nach der Feuerart der Waffe (`gameplay.fire_mode` aus der Spec): Automatik und MP Dauerfeuer, 720/min wie der Clip `fire_hip` (Frage 7.1 A); Scout (0.20) Einzelfeuer, ein Schuss je Klick, höchstens 180/min; Handfeuerwaffe (0.33) Einzelfeuer 140/min (Spannabzug, Hahn zuckt), Seitenwaffe 360/min – ein Klick vor Ablauf des Schussabstands wartet bis zu 0,4 s; Impuls (0.22) Salve: 3 Schuss je Zug im Takt 900/min, gehalten Salve um Salve (Salvenbeginn alle 3 · 60/540 = 0,333 s); Portalkanone (0.22, Nutzerwahl A): Portal A (Cyan), Ring 120° im Uhrzeigersinn, Abklingzeit 0,25 s, Treffermarke in Portalfarbe auf jeder Fläche bis 24 m; Abzug bei leerem Magazin lädt selbst nach |
| rechte Maustaste | zielen (Weltzoom der Klasse aus `ego.json › gameplay.world_zoom`, Automatik 1,9 – vorher fest 1,35, Scout 2,0; Viewmodel bleibt bei 75° horizontal; der Zoom folgt dem Modell, 1d). Scout: Zielfernrohr nach Visier-Standard 3 – eine Kamera, das Okular wächst heran, dann sind Okular, Rohr und Türme aus (`motion.ads_hide`) und das Objektiv zeigt das gezoomte Weltbild mit dem Absehen `chevron`. Portalkanone (0.22): kein Zielen – Portal B (Orange), Ring 120° gegen den Uhrzeigersinn; Waffen ohne Aktion `aim_in` zielen nicht (Daten, keine Abfrage nach der Waffen-ID) |
| R | nachladen: taktisch bei Restmunition, sonst leer (mit Durchladen); Portalkanone ohne Magazin (`gameplay.magazine` 0): unbegrenzt, kein Nachladen, Anzeige „∞“ |
| F | betrachten; Feuer, Zielen, Nachladen oder Sprint brechen ab |
| 1 – 0 | Waffe wählen (0.18, Taste 3 seit 0.20, 4/5 seit 0.22, 6–0 seit 0.33; Tasten nach der Reihenfolge in `ego.json`): 1 Automatik BASIC-01, 2 Maschinenpistole BASIC-06, 3 Scout BASIC-03, 4 Impulsgewehr BASIC-02, 5 Portalkanone BASIC-T01, 6 Handfeuerwaffe BASIC-04, 7 Seitenwaffe BASIC-05, 8 Scharfschütze BASIC-09, 9 Spurgewehr BASIC-12, 0 MG BASIC-15; Schrotflinte, Fusion, lineare Fusion, Bogen, Granatwerfer und Raketenwerfer (Waffe 11–16) über das Waffenmenü – wegstecken (0,27 s, beim Nachladen `reload_to_switch`), leere Sicht ≈ 0,13 s, die andere Waffe ziehen (6.1 A); die Taste der aktiven Waffe zieht sie, wenn sie weggesteckt ist. Jede Waffe behält ihre Munition. Bis 0.17: 1 ziehen, 2 wegstecken |
| Tab, Mausrad | Waffenmenü (0.33): Tab oder Mausrad öffnet (das Rad markiert gleich die nächste bzw. vorige Waffe), Mausrad und Pfeiltasten bewegen im Raster 4 × 4, Enter oder Linksklick wählt (wie eine Zifferntaste), Esc oder Tab schließt ohne Wahl; offen schießt, zielt und blickt nichts, Laufen bleibt; beim gespannten Bogen entspannt das Menü ohne Schuss. HUD unten rechts: Symbol, Klasse, Munition |
| Feuerarten (0.33) | Repetierer (Scharfschütze): nach jedem Schuss Kammerstängel; Pumpe (Schrotflinte): pumpen, Nachladen je Patrone, ein Zug am Abzug bricht ab; Dauerstrahl (Spurgewehr); Aufladen (Fusion: Salve, lineare Fusion: Schuss) – Loslassen vorher bricht ab; Granatwerfer: Trommel dreht je Schuss, Nachladen je Kammer; Raketenwerfer: Magazin 1, nach dem Schuss sofort nachladen; Bogen: linke Maustaste halten spannt (0,6 s), gespannt mit Rechtsklick zielen und zurück, Loslassen löst (halb gespannt schwach, im Zielen zugleich aus dem Zielen), R entspannt ohne Schuss, kein Magazin |
| Q | zur nächsten Waffe wechseln (wie Taste 1–0, reihum: 1 → 2 → … → 16 → 1; mit nur einer Waffe in `ego.json` wegstecken und dieselbe ziehen, 0.15); mit gehaltenem Zielen direkt ins Visier (`draw_aim`) |
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
| Export | [`tools/export_unity.py`](../tools/export_unity.py) | FBX je Waffe (Wurzel → `ASM_*` → Teile, Anker als Leerknoten; Arme: `R_`/`L_`-Segmente → Teile), `ego.json` (`ballon-ego/8`), `ego_reference_<Waffe>.json`; gebacken wird nur, was sich geändert hat (Waffe mit gleicher Form behält Atlanten, Netzgrenzen und FBX) |
| Daten | `Runtime/EgoData.cs` | JsonUtility-Klassen, Prüfung des Formats |
| Rechnen | `Runtime/BMath.cs`, `Runtime/EgoSolver.cs`, `Runtime/EgoScreen.cs` (Bildlage, Silhouette; Tests und Messung) | Blender-Kameraraum; `pose_matrix`, Hermite-Kurven, Feder-Nachlauf, Griffe, Zwei-Knochen-Arm mit Drehgelenk, Finger, Magazin, Rückstoßfeder |
| Zustand | `Runtime/EgoController.cs` | Spuren mit Markern, Haltungen (Hüfte, Zielen, Sprint, Ducken, Luft, gesenkt), Übergänge, Überblendung, Live-Ebenen |
| Szene | `Runtime/EgoPlayer.cs`, `EgoRig.cs`, `Range.cs`, `Bootstrap.cs` | Bewegung, Kameras (Welt + Overlay), Treffer, Anzeige, Parcours, Aufnahme- und Vergleichsmodus; `EgoRig` baut seit 0.16 auch Blitz und Hülsenpool aus den Netzen in `ego.json` |
| Szenen (0.8, 0.9) | `Runtime/SceneData.cs`, `MiniJson.cs`, `SceneLoader.cs`, `Course.cs` | Format `ballon-scene/2` (Leser mit Prüfung, JsonUtility kann keine Wörterbücher), Umrechnung Blender → Unity, Lader (Zonenmaterialien, Collider, Lichtszenen, Ziele, Wegmarken), Parcours-Lauf (`CourseRun`) |
| Editor | `Editor/BallonSetup.cs` | Importeinstellungen, Knotenlagen aus `ego.json`, URP, Materialien, Szene, Build |
| Tests | `Tests/EditMode`, `Tests/PlayMode` | siehe unten |

**Format.** `ego.json` hat das Format `ballon-ego/9`. Der Abnehmer ist `unity/` ab 0.20; `EgoFile.ParseAll` liest `/8` und `/7` weiter. Die Stufen:
- 2 (0.7): Texturen, AgX-LUT, `emit_only`;
- 3 (0.7.1/0.7.2): Spiegelkarte `spec` statt `mask`, `textures.skins`;
- 4 (0.10): `motion.secondary.aim_freq_hz` und `aim_zeta`. Aktionen, die im Zielen enden (`ego.ends_in_ads`: `aim_in`,
  `sprint_to_aim`, `draw_aim`, `fire_ads`), folgen ihrer Kurve mit einer schnellen, kritisch gedämpften Feder (10 Hz, ζ 1). So schwingt das
  Visier nicht mehr über die Mitte (0.9: 3,3°) und hängt nicht nach (am Ende von `aim_in` 0,8°). Alle übrigen Aktionen behalten
  3,2 Hz bei ζ 0,55.
- 5 (0.13): `gameplay.weapon_type`, `sight`, `world_zoom` (Weltzoom der Klasse, Entscheidungsliste 1.2 A), `zoom_table` (alle Waffentypen)
  und `hip` (Hüft-Fadenkreuz: Form als Grundelemente, Größe, Farbe, Linienstärke, Aufgehprofil, Sprintform), aufgelöst aus `basic/reticles.py`.
- 6 (0.15): `motion.recoil` in vier Größen (Entscheidungsliste 5.2 A) – Modellkick mit `ads_back`/`ads_pitch`, Kamera-Ruck kritisch
  gedämpft mit `ads_cam`, Grundbahn `path_up_h`/`path_side_b`/`path_hz`, Erholung `recover_delay_s`/`recover_hz`, Salven
  `burst_shots`/`burst_rpm`, Streuung `spread_hip_deg`/`spread_ads_deg` (vorher `MoveTuning`) – und `motion.switch.empty_s` (Wechsel, 6.1 A).
- 7 (0.16): `motion.flash` (Mündungsfeuer, 5.3 A: Dauer `dur_s` = 1/30 s, Netz relativ zu `Socket_Muzzle`, Kern- und Flammendreiecke,
  Drehfolge `roll_deg`), `motion.eject` (Hülsenbahn, 5.4 A: Geschwindigkeit, Schwerkraft, Drehung, `life_s`, `max_live`, `delay_frames`),
  `weapon.eject` (je Waffe aus dem Modul-Feld `EJECT`: `enabled`, Startlage, Richtung, Hülsennetz) und die Rollen `flash_core`/`flash_flame`.
- 9 (0.20): `gameplay.fire_mode` (Feuerart aus der Spec: `full_auto`, `semi_auto`), `weapon.parts[].ads_hide` und `motion.ads_hide`
  (`eye_m`: Teile mit `ads_hide` sind aus, solange `Socket_Eye` der Grundhaltung näher an der Kamera liegt), `weapons[].textures.store`
  und `limit_mb` (Ablage der Atlanten je Kanal, siehe „Texturen“); die Referenz trägt je Stichprobe `ads_hidden`. `EgoFile.ParseAll`
  liest `/8` und `/7` weiter und setzt dabei Dauerfeuer und `eye_m` 0 (bis 0.19 hatte keine spielbare Waffe solche Teile).
- 8 (0.18): `weapons[]` je spielbarer Waffe (`tools/export_unity.WEAPONS`, Reihenfolge = Taste 1, 2): `profile` (Klasse und Herkunft aus
  `ego.CLASSES`), `gameplay`, `weapon` mit `live` (Abzug, Verschluss, Auswurfklappe; bis 0.17 fest im Code), `poses`, `grips`, `actions`,
  `atlas` (Material `Atlas_<atlas>`, Pilotwaffe `weapon`), `textures` (Waffenatlas, Skins), `mesh_bounds`, `sources`, `reference`. Gemeinsam
  bleiben `motion`, `camera`, `arm`, `finger_poses`, `roles`, `textures` (Arme, LUT) und `mesh_bounds` (Armteile).

Ältere Exporte (`/1` bis `/6`) und unbekannte neuere lehnt `EgoFile.Parse` mit dem Hinweis „neu exportieren“ ab.

**Achsen.** Die Umrechnung steht einmal in `ego.json › axes.to_unity`: Unity = (−x, z, −y) aus Blender. Matrizen werden als
M·B·Mᵀ umgerechnet. Gerechnet wird überall im Blender-Raum, umgerechnet erst beim Setzen der Transforms. Die Netze kommen aus dem
FBX (mit „Apply Transform“). Die Lagen der Knoten setzt der Importer aus `ego.json`, weil das FBX die Kindknoten der Waffe verdreht
und versetzt (beim ersten Import gemessen: 90° am Magazin, bis 218 mm).

**Live statt geskriptet.** Abläufe, Haltungen und Marker kommen aus den Aktionen in `ego.py`, gestreckt mit `TIME_SCALE`. Im Spiel
ersetzt der Controller die geskripteten Ebenen durch live gerechnete:

- Schüsse kommen aus der Kadenz (Übertrag zwischen den Bildern, damit 720/min bei jeder Bildrate gelten). Eine Salvenwaffe
  (`burst_shots` > 0) schießt in der Salve mit `burst_rpm` und läuft eine angefangene Salve zu Ende. **Einzelfeuer (0.20,
  `gameplay.fire_mode` `semi_auto`):** ein Schuss je Zug (Flanke des Abzugs), höchstens 60/rpm; ein Zug vor Ablauf des Schussabstands
  oder im Übergang aus dem Sprint wartet bis zu 0,4 s (E). Im Clip ist der Abzug je Schuss ein Bild davor bis ein Bild danach gezogen
  (`ego.trigger_on`, Blender und `EgoSolver` gleich).
- **Gezeichnetes Absehen (0.20, Nutzer 26.10.2026):** „Ich finde die Visier-Punkte/Kreise/Fadenkreuze sehen so komisch 3D-mäßig aus. Mir
  wäre lieber etwas Gezeichnetes … Im Bestfall hat man das Fadenkreuz/Punkt/Kreis/wie auch immer vom Hüftfeuer im Visier.“ Unity blendet das
  Modell-Absehen (Teile mit Rolle `reticle_*`) aus und zeichnet im Zielen (Zielen-Anteil ≥ 0,9, beim Zielfernrohr im Linsenbild) die
  Hüftform der Klasse (`gameplay.hip`, gleiche Größe, ohne Aufgehen) in der Farbe der Absehen-Rolle (Cyan) an der Bildlage von
  `Socket_Reticle` (`EgoPlayer.SightVisible`, Aufnahmen stempeln es wie das Hüft-Fadenkreuz). Seit 0.21 „Ironsight“ legt Blender
  dieselbe Hüftform flach in die Glasebene (`common.drawn_reticle`, Linien ≥ 1,6 px, reine Emission) – Formblätter und Ego-Clips
  zeigen also, was Unity zeichnet; Unity blendet das Modellteil weiter aus. Die Leuchtkontur der MP-Pille (H2) hat die Rolle
  `sight_line` und bleibt in Unity sichtbar.
- **Glas und Leuchten nach dem Reimport (0.20):** URPs Materialprüfung setzte beim Reimport der Rollenmaterialien das Glas auf
  vormultipliert (SrcBlend One, milchig) und nahm dem Absehen `_EMISSION` (Emissive-Flag fehlte). `BallonSetup` setzt jetzt
  `_BlendModePreserveSpecular` 0 und `RealtimeEmissive`. Linsen im Zielfernrohr (`roles[].no_coat`) wie `kit.aaa_nodes`: Alpha 0,04, ohne
  Glanz und Spiegelung – gemessen im Parcours 1,3–2,6 % heller als außen (Visier-Standard 3: ≤ 5 %).
- **Zielfernrohr (0.20, Visier-Standard 3):** eine Kamera, das Modell bleibt ungezoomt, die Welt zoomt mit dem Klassenwert. Teile mit
  `ads_hide` (Okular, Okularkante, Okularlinse, Rohr, Türme, Spannband) schaltet `EgoRig` aus, solange `Socket_Eye` der Grundhaltung
  näher als `motion.ads_hide.eye_m` (60 mm = Okularende 30 mm + Nahebene 30 mm) an der Kamera liegt; Blender (`ego_build.evaluate`) rechnet
  dieselbe Regel, die Referenz prüft sie je Stichprobe. Vorher wächst das Okular heran wie bei Destiny; der Zeitpunkt ist in
  „Tests“ gemessen (`Zielfernrohr_Zoom_und_Linse_mit_dem_Modell`).
- **Rückstoß in vier Größen (0.15, Entscheidungsliste 5.1 A / 5.2 A):**
  - *Grundbahn* (Destiny-Säule): je Schuss `path_up_h` = 1 % der Bildhöhe nach oben, seitlich die feste Folge `path_side_b`
    (≤ 1,6 % B Spitze–Spitze, je Salve dieselbe Form). Gerechnet im Bildmaßstab der Welt, im Zielen also kleinere Winkel. Sie dreht nur
    die Weltkamera (`EgoOutput.worldPitch/worldYaw`, `EgoRig.WorldKick`), Schüsse gehen dorthin. In der Salve folgt sie mit 10 Hz ohne
    Erholung; ist `recover_delay_s` (mindestens 1,5 Schussabstände) kein Schuss gefallen, kehrt sie kritisch gedämpft mit 2 Hz zurück.
    Gemessen: Viererstoß im Zielen 4,3 % H, 12 Schuss aus der Hüfte 12,0 % H; zurück unter 0,25 % H nach 0,48 bzw. 0,60 s, ohne Unterschwingen.
    Bis 0.14 blieb das Hochziehen (0,18°/Schuss) stehen, bis der Spieler gegenlenkte.
  - *Kamera-Ruck*: Federimpuls je Schuss, kritisch gedämpft (bis 0.14 ζ 0,6 mit Unterschwingen). In der Hüfte drehen Welt- und
    Viewmodel-Kamera, im Zielen nur die Welt (`ads_cam`): das Visier bleibt stehen.
  - *Modellkick*: Feder der Waffe (zurück, Mündung hoch, Hochziehen des Modells). Im Zielen `ads_back` 0,45 und `ads_pitch` 0,02, ohne
    Hochziehen: das Visier bewegt sich durch den Rückstoß 0,12 % H (vorher 1,0 % H).
  - *Streuung*: Zufall um den Zielpunkt (`spread_hip_deg` 1,1°, `spread_ads_deg` 0,12°), getrennt von der Bahn.
- **Zoom folgt dem Modell (0.15, 1d):** Der Zielen-Anteil (Weltzoom, Empfindlichkeit, Streuung) ist der Weg, den der Augenpunkt
  `Socket_Eye` der Grundhaltung (nach dem Feder-Nachlauf, ohne Wippen und Rückstoß) zur Kamera zurückgelegt hat, zwischen 5 % und
  99,85 % des Wegs (`AdsStart`/`AdsEnd`). Vorher lief eine eigene Zeitkurve über 9 Bilder ab der Eingabe: Der Zoom begann 2–3 Bilder vor
  dem Modell, nach dem Sprint 11 Bilder danach.
- **Wechsel (0.15, 6.1 A):** `holster` 0,27 s, dann `switch.empty_s`, dann `draw` ab dem letzten Bild ohne Waffe und Arme im Bild
  (`EgoController.DrawEnters`, aus der Silhouette gerechnet); der sichtbare Teil des Ziehens ist derselbe wie mit Taste 1. Marker
  `switch › Empty` und `switch › Draw`.
- **Mündungsfeuer und Hülsen (0.16, Entscheidungsliste 5.3 A / 5.4 A):** Form und Bahn stehen nur in `basic/arms/ego.py` (`FLASH`,
  `EJECT`, `flash_mesh`, `case_mesh`); Blender (`ego_build.fx_eval`) und Unity (`EgoSolver.FxScripted`, `EgoController.LiveFx`) rechnen
  dieselben Formeln. Der Blitz kommt nur aus einem echten Schuss (`FireOne`), steht `dur_s` = 1/30 s (30/s: 1 Bild, 60/s: 2, 144/s: 5)
  an `Socket_Muzzle` und dreht je Schuss nach `roll_deg`; reine Emission ohne Bloom, ohne Schatten. Je Schuss startet eine Hülse mit der
  Waffe dieses Bilds im Auswurffenster und fliegt im Kameraraum (Viewmodel-Ebene) nach rechts, etwas hoch und dann nach unten, mit
  Drehung; nach `life_s` 0,4 s ist sie weg. Unity nimmt dafür einen festen Pool aus `max_live` = 6 Objekten (Ring, der älteste wird
  überschrieben), keine Speicheranforderung je Bild. Waffen ohne Feld `EJECT` (`weapon.eject.enabled` false) werfen nichts aus.
- **Wirkung der Waffen (0.34 „Payload“, Entscheidungsliste Block 9):** Werte nur in `basic/arms/ego.py` (`PAYLOAD` je Klasse →
  `gameplay.fx`; `IMPACTS`, `DECAL`, `EXPLOSION`, `MUZZLE_SMOKE` → `motion.payload`), gezeichnet von `Runtime/WeaponFx.cs` mit dem Shader
  `Ballon/Fx` (Form aus der UV: weicher Fleck, Ring, Einschussloch, Strahl, Funke; Materialien `Fx_*` aus `BallonSetup`). Arten je Klasse:
  `hitscan` (Kugel: Funken, Staub, Licht, Loch; MG mit Leuchtspur jeder 3. Schuss), `pellets` (Schrot: 12 Kugeln im Kegel),
  `projectile` (Granate im Bogen, Rakete gerade mit Rauchspur; Explosion mit Blitz, Feuer, Druckring, Funken, Rauch, Licht, Brandfleck,
  Scheiben im Radius zählen), `arrow` (Pfeil mit Fall, steckt), `beam` (Dauerstrahl), `bolts` (Bolzen je Strahl der Salve, Einschlag bei
  Ankunft), `rail` (scharfer Strahl, blendet aus), `none` (Werkzeug). Strahlen und Projektile beginnen an `Socket_Muzzle`, durch die
  Viewmodel-Kamera auf denselben Bildpunkt der Weltkamera gerechnet. An der Waffe: Rauch aus dem Rohr (Werfer) und Mündungslicht
  (Energie, Bogen) in der Viewmodel-Ebene. Alles in festen Pools (Löcher 96, Projektile 8, Linien 24, Ringe 4, Lichter 2,
  Brandflecken 8, Partikel je System fest); die Partikel sind angehalten und laufen mit der Spielzeit (`Simulate`), damit Tests und
  Aufnahmen mit virtueller Zeit dieselben Bilder sehen. Gegenprobe: `BALLON_PAYLOAD_OFF=1` schaltet die Wirkung samt Schrittteilen,
  Füllstand, Gliedern und Nachlade-Hülsen ab.
- **Schrittteile, Füllstand, Glieder (0.34):** `EGO_LIVE index` (Trommel der Handfeuerwaffe, Gurtvorschub des MG) läuft nach jedem Schuss
  in `ego.index_frames` Bildern von 0 auf 1 – Blender (`ego_build`) und Unity gleich. `EGO_LIVE rounds` zeigt den Füllstand nur im Spiel
  (Clips voll): MG-Gurt (`line`, Satz i an bei mehr als i Patronen), Granatwerfer-Trommel (`drum`, je Kammer; der Zustand rückt mit, wenn
  die Trommel zurückspringt). `EGO_LIVE fill`: Zählzellen des MG leuchten nach dem Anteil. `EJECT links`: je Schuss ein Gurtglied
  (Blender und Unity). Hülsen beim Nachladen (`EJECT on='reload'`): Granatwerfer eine je Kammer, Handfeuerwaffe so viele wie verschossen
  aus der ausgeschwenkten Trommel (`part`, Kammerkreis `ring`, langsam `speed_k`) – nur Unity, die Blender-Nachladeclips zeigen keine Hülsen.
- Das Hochziehen des Modells klingt erst nach dem Feuern ab.
- Das Gehwippen folgt der Laufgeschwindigkeit, mit den Werten aus `walk`/`sprint`.
- Das Atmen nutzt `BREATHE_ALL`, dazu in Ruhe die `idle_hip`-Formel.
- Der Feder-Nachlauf `SECONDARY` läuft in Echtzeit über alle Spurwechsel.
- Das Pendeln aus der Maus ist dieselbe Feder wie Feder-Nachlauf und Visier-Anflug (`EgoSolver.SpringStep`), seit dem Patch
  unity-abgleich kritisch gedämpft (2,5 Hz, ζ 1; vorher 9 Hz, ζ 0,55 mit 0,22° Überschwingen bei 60/s, 0,30° bei 30/s): Die Waffe zieht höchstens 3°
  gegen die Drehung nach und kehrt in ≈ 0,3 s ohne Überschwingen zurück wie in Destiny (Frage 3.3 A).

Spielwerte, die nicht aus Blender kommen, stehen in `EgoTuning` und `MoveTuning`: Laufgeschwindigkeiten, Pendeln, Wippen und
Atmen im Zielen. Alle sind entworfen. Weltzoom, Streuung und Hochziehen des Blicks kommen seit 0.15 aus `ego.json`.

## Tests

| Test | prüft |
|---|---|
| `Granatwerfer_Granate_fliegt_im_Bogen_und_explodiert`, `Raketenwerfer_Rakete_gerade_mit_Rauchspur_und_Explosion` (PlayMode, 0.34) | Start an der Mündung (Bildlage), Geschwindigkeit, Fallkurve bzw. gerade Bahn, Rauch aus dem Lauf, Rauchspur; Explosion mit Ring, Licht, Brandfleck, Funken, Rauch; Flug und Partikel ohne Speicher je Bild |
| `Spurgewehr_Dauerstrahl_vom_Lauf_zum_Einschlag`, `Fusion_Salve_aus_Bolzen`, `Lineare_Fusion_ein_scharfer_Strahl`, `Bogen_Pfeil_loest_fliegt_und_steckt` (PlayMode, 0.34) | Strahl von der Mündung (± 1 % des Bilds) bis zur Wand, Mündungslicht; ein Bolzen je Strahl, Einschlag bei Ankunft; Strahl `beam_s`; Pfeil fliegt, steckt `stick_s` |
| `Schrot_Streuschuss_mit_mehreren_Einschlaegen`, `Einschlag_Funken_Staub_Loch_und_Ausblenden` (PlayMode, 0.34) | 12 Einschläge und Löcher im Kegel; je Kugelklasse Funken, Staub, Loch (Stil bullet/heavy), Ausblenden nach `life_s`, Pool-Obergrenze |
| `Handfeuerwaffe_Trommel_dreht_je_Schuss_Huelsen_beim_Nachladen`, `MG_Glieder_Gurtvorschub_und_Fuellstand`, `Granatwerfer_Trommel_zeigt_geladene_und_leere_Kammern` (PlayMode, 0.34) | Trommel eine Kammer je Schuss, Hülsen beim Nachladen je verschossene Kammer; Glied je Hülse, Gurtvorschub, Gurt leert sich von unten, Zählzellen, Modell; Kammern leer nach dem Schuss, rücken mit der Trommel, füllen sich beim Nachladen |
| `Klassen_vollstaendig_in_ego_json` (0.33) | alle 16 Waffen in Tastenreihenfolge mit Klasse und Feuerart, Herkunft, Spielwerte, Griffe, Live-Teile, Atlanten |
| `Repetierer_repetiert_nach_jedem_Schuss`, `Dauerstrahl_leuchtet_solange_der_Abzug_zieht`, `MG_Gurtkasten_nachladen` (0.33 P2) | Kammerstängel nach dem Schuss, Strahl-Leuchtteile, Gurtkasten-Nachladen |
| `Pumpe_pumpt_und_laedt_je_Patrone`, `Fusion_laedt_auf_und_schiesst_die_Salve`, `Lineare_Fusion_laedt_auf_und_schiesst_einmal` (0.33 P3) | Pumpe, Einzelladen mit Abbruch durch Feuer, Aufladen |
| `Bogen_spannt_haelt_und_loest`, `Granatwerfer_Trommel_dreht_und_laedt_je_Kammer`, `Raketenwerfer_laedt_nach_jedem_Schuss` (0.33 P4) | Spannen/Halten/Lösen, gespannt zielen, R entspannt, Zoom 2,2×; Trommel und Nachladen je Kammer, Hülse je Kammer; Sofort-Nachladen |
| `Waffenmenue_waehlt_und_wechselt`, `Abbruch_beim_Spannen_und_Einzelladen` (0.33 Ziel 2) | Menü (Rad, Pfeile, Esc, Enter → Wechsel, Nachladen bricht ab); Wechsel beim Spannen ohne Schuss, Menü entspannt, Wechsel im Einzelladen |
| `Format_und_Umfang`, `Falsches_Format_wird_abgelehnt` | JSON-Import: Format `ballon-ego/8` mit zwei Waffen (`/1` bis `/6` und `/9` abgelehnt, `/7` gelesen), je Waffe 10 Haltungen, 4 Griffe, 19 Aktionen, 72 Teile (Visier v2 aus 0.6), vier Finger, sortierte Schlüssel |
| `Achsumrechnung_Blender_nach_Unity` | Determinante −1, vorn/oben/rechts, Mündung vorn oben, Drehsinn bleibt erhalten |
| `FBX_Import_passt_zur_Achsumrechnung` | Netzgrenzen jedes der 206 Netzobjekte = umgerechnete Blender-Grenzen (≤ 0,5 mm), Maßstab 1 |
| `FBX_Ruhelagen_und_Anker_wie_in_den_Daten` | Lage aller Teile und Anker im importierten Modell |
| `Armlaengen_in_allen_Bildern` | Ober-/Unterarm 0,32/0,30 m in allen Haltungen und allen Bildern aller Aktionen |
| `Handgelenkknick_hoechstens_45_Grad` | Knick ≤ 45° in allen Haltungen und Bildern |
| `Gleich_wie_Blender_Referenz` | Weltmatrizen von Waffe, Mechanik, Magazin, Kamera und 16 Armsegmenten in 279 Stichproben gegen `tools/ego_build.evaluate` (≤ 0,5 mm, ≤ 0,1°); seit 0.16 Feueraktionen lückenlos, dazu Blitz und jede sichtbare Hülse (gleiche Sichtbarkeit wie Blender) |
| `Clips_Blitz_ein_Bild_und_Huelse_je_Schuss` (EditMode, 0.16) | `fire_hip`, `fire_ads`, `sprint_to_fire` wie ego_build: je Schuss genau ein Blitzbild im Schussbild, je Schuss eine Hülse ab dem Schussbild, `life_s` lang, im Bild nach rechts und zuletzt nach unten |
| `Muendungsfeuer_im_Zielen_hoechstens_20_Prozent_der_Oeffnung` (EditMode, 0.16) | jedes Blitzbild von `fire_ads`: Blitznetz projiziert und gerastert gegen die lichte Holo-Öffnung, höchstens 20 % (5.3 A), mehr als 5 % (sichtbar); `./check` rechnet dasselbe in Python (`ego.flash_cover_ads`) |
| `Muendungsfeuer_ein_Bild_bei_30_gleiche_Dauer_bei_hoeherer_Rate`, `Huelse_je_Schuss_einmal_nach_rechts_unten`, `Kein_Feuer_und_keine_Huelse_bei_leerem_Magazin_und_Nachladen`, `Waffe_ohne_Auswurf_wirft_keine_Huelsen`, `Huelsenpool_ohne_neue_Objekte` (PlayMode, 0.16) | Live-Controller: Blitz 1 Bild bei 30/s, 2 bei 60/s, 5 bei 144/s, ab dem Bild des Schusses, im Dauerfeuer einer je Schuss; eine Hülse je Schuss im Bild des Schusses, nach 0,1 s ≥ 5 % B nach rechts, zuletzt nach unten, ≤ `max_live` gleichzeitig; kein Blitz und keine Hülse bei leerem Magazin und während des Nachladens (gehaltener Abzug); `weapon.eject.enabled` false: Blitz ja, Hülse nein (live, Clip, kein Pool im Modell); Spieler in der Szene, 2 s Dauerfeuer: keine neuen Objekte, kein GC je Bild |
| `Jede_Aktion_endet_mit_Markern_in_Reihenfolge` | alle 19 Aktionen enden in ihrer Bildzahl, Marker in Datenreihenfolge, keine NaN |
| Spielablauf (6 Tests) | Kadenz und Magazin, leeres/taktisches/automatisches Nachladen, Zielen hin und zurück (Auge auf der Kameraachse), Betrachten abbrechen, Wegstecken beim Nachladen und Ziehen, Sprintschleife und Übergänge, Ducken/Springen/Wandnähe |
| `Zielen_live_ohne_Ueberschwingen` (0.10) | Live-Controller: Zielen aus der Hüfte, Überschwingen am `Socket_Reticle` < 0,3°, Rest nach 0,45 s < 1°; Messwerte im Testprotokoll |
| `Sprint_live_im_Destiny_Rhythmus` (0.10) | Live-Sprint: 2,9–3,4 Hochpunkte/s, U-Bogen (oben an den Seitenumkehren); Messwerte im Testprotokoll |
| `Zielen_landet_ohne_Ueberschwingen`, `Sprintschritt_wie_ein_Laeufer` (EditMode, 0.10) | Skriptpfad wie Blender: `aim_in`, `sprint_to_aim`, `draw_aim` ohne Überschwingen (< 0,3°), Rest am Ende < 1,5°; Sprintdaten 2,9–3,4 Schritte/s mit U-Bogen; seit 0.15 auch der Hub an der Silhouette (`EgoScreen`, Kanten der Netzgrenzen von Waffe und Armen): Oberkante 8,5–12,5 % H, linke Kante 11–15,5 % B (gemessen 10,5 / 13,8; am Unity-Bild 8,9–9,5 % H / 12,7–13,7 % B) |
| `Hueftlage_im_Destiny_Band` (EditMode, 0.15) | Ego-Still `hip`: Mündung x 54–59 / y 60–71 % (gemessen 58,1 / 63,1), hintere Visieröffnung 7–34 pp rechts (19,3), Kontur bis zum rechten und unteren Rand |
| `Wechsel_mit_Q_im_Spieler` (PlayMode, 0.15, 0.18) | ScriptedInput „swap“ → `EgoPlayer.Step` → `EgoArsenal`: zweimal Wegstecken, leer, Ziehen, Hüfte – seit 0.18 Automatik → MP → Automatik |
| `Altes_Format_7_wird_gelesen` (EditMode, 0.18) | `ballon-ego/8` mit `weapons[]`; der Leser erkennt die alte Datei `/7` (Stand 0.17, Kopie `Tests/EditMode/Data/ego_v7.json`) und liefert für die Pilotwaffe dieselben Haltungen, Griffe, Aktionen, Spielwerte, Teile, Atlanten, Netzgrenzen und dieselbe Auswertung wie die neue Datei; Live-Teile wie bis 0.17 im Code; seit 0.21 mit `Visier_0_21` (nur benannte Felder normiert: Visierrolle anodized → sight_anod; MP: Haube/Haubenkante entfallen, Scheibe glass_scope, Augenpunkt an der Scheibe) und `Visier_v3` (neue H2-Teile der MP), Netzgrenzen ohne das flache Absehen |
| `Werte_je_Klasse`, `Hueftlage_der_MP_im_Band`, `Sprint_Rollrichtung_je_Klasse` (EditMode, 0.18) | Klassenwerte aus `ego.CLASSES`: MP `aim_in` 3 Bilder bei 30/s, `aim_out` 2,4, sonst alle Aktionen wie die Automatik; Automatik `aim_in` 0,33 s unverändert; Weltzoom MP 1,45, Kadenz 720/min, Magazin 30, Hüft-Fadenkreuz `circle_cross` 6,1 % H, Hülse `pistol`; MP-Hüfte Mündung im Band der Kurzwaffen (x 53–71 / y 59–84 %, nahe Destiny-MP 57–58/61–62), Absehen 60–70 % x; Sprint: MP mit der Oberseite nach links (> 20°), Mündung nahe 43/80 %, Automatik nach rechts |
| `Daumen_der_Stuetzhand_nicht_im_Vorbau` (EditMode, 0.18) | MP, alle Haltungen und Aktionsbilder mit der Stützhand am Vordergriff (585): Daumenspitze nicht im Vorbau und unter seiner Oberkante (höchstens 39 mm, Vorbau 58–106 mm); Fingerstellung `foregrip` (Faust, Daumen hinter dem Griff, Nutzerwahl) und `foregrip_open` statt `underhand`/`open` |
| `Anzeige_baut_Treffertext_nur_bei_Aenderung` (PlayMode, 0.18) | Treffertext der Anzeige bleibt dasselbe Objekt, solange nur Aktionsbilder weiterlaufen; beim Waffenwechsel neu (Skin-Name der anderen Waffe) |
| `Anflug_je_Klasse_live_bei_60` (PlayMode, 0.18, 0.20) | Live-Controller bei 60/s, Absehen der Grundhaltung am Bild, Ruhe = Bildweg je Bild unter 0,09 % (fest, wie Motiongen am Bild): MP 8–12 Bilder (Destiny-MP 8–12), Automatik 18–22 (Destiny 20), Scout 15–20 (zwischen Scharfschütze 15 und Impuls 20) |
| `Wechsel_1_2_mit_leerer_Sicht_ohne_Munitionsverlust`, `Kein_GC_Muell_beim_Wechsel`, `Wechsel_mit_Tasten_1_2_im_Spieler` (PlayMode, 0.18) | Tasten 1/2 bei 60/s wie Q: Wegstecken 0,2–0,3 s, leere Sicht 0,1–0,2 s, erstes neues Bild = `draw` der anderen Waffe; Munition je Waffe bleibt (auch beim Abbruch des Nachladens vor `MagIn`); Wechsel 1 → 2 → 1 ohne Speicher je Bild (Spurpool im Controller); im Spieler nur das aktive Modell sichtbar, Weltzoom und Hüft-Fadenkreuz der Klasse |
| `Wechsel_mit_leerer_Sicht` (PlayMode, 0.15) | Q bei 60/s, sichtbar = Kante der Netzgrenzen von Waffe oder Armen im Bild: Wegstecken bis zum Marker `Holstered` 0,2–0,3 s (0,267), leere Sicht 0,1–0,2 s (0,133), erstes neues Bild gehört zu `draw`, Hüfte (`draw › Ready`) und ruhig danach in Reihenfolge; das Ziehen wie mit Taste 1. Aus dem Nachladen (`reload_to_switch`) nur protokolliert |
| `Zoom_beginnt_und_endet_mit_dem_Modell` (PlayMode, 0.15) | Hüfte → Zielen und Sprint → Zielen bei 60/s: Zoom beginnt 0–2 Bilder nach dem Modell und endet ±1 Bild (Bildbewegung von Mündung, Visier, Magazinschacht, Griff, Schwelle 5 %); Zielen → Hüfte: Zoom zurück, wenn das Modell die Hüfte erreicht |
| `Rueckstoss_Saeule_fest_und_zweistufig` (PlayMode, 0.15) | 3 × 12 Schuss aus der Hüfte: Säule 11–13,5 % H, seitlich 0,5–2,5 % B, dreimal dieselbe Bahn, Erholung 0,4–0,75 s ohne Unterschwingen; Viererstoß im Zielen 3,5–4,5 % H des gezoomten Bilds; Salvenwaffe (Daten im Test umgestellt): Takt 4 Bilder, Pause, Erholung zwischen den Salven, angefangene Salve läuft zu Ende |
| `Rueckstoss_im_Zielen_geht_in_die_Welt` (PlayMode, 0.15) | Spieler in der Szene, 16:9, 60/s: Weltanker 20 m voraus wandert beim Viererstoß im Zielen 3,5–5 % H (4,32), zurück unter 0,25 % H nach 0,4–0,6 s (0,483), kein Unterschwingen; Visier gegen einen Zwilling ohne Schuss < 1 % H (0,12), aus der Hüfte mehr als dreimal so viel |
| `Kadenz_720_wie_fire_hip` (Patch unity-abgleich) | `gameplay.rpm` 720 mit Herkunft M; live bei 60/s und 30/s je 24 Schüsse in 2 s, Bildabstand 5 bzw. 2/3, Kadenz 720 ± 15 /min (der Rest eines Intervalls wird übertragen; vorher bei 30/s 3 Bilder = 600/min) |
| `Pendeln_kehrt_ohne_Ueberschwingen_zurueck` (Patch unity-abgleich) | 360°/s für 0,3 s, Gieren des Laufs gegen einen Zwilling ohne Maus: Auslenkung 0,5–3°, Überschwingen < 0,02°, Rückkehr unter 5 % in 0,22–0,4 s |
| `Nachlade_Abbruch_vor_und_nach_MagIn` (Patch unity-abgleich) | taktisch und leer: Wegstecken 0,1 s vor `MagIn` lässt die Munition (5 bzw. 0), 0,1 s danach ist das Magazin voll und bleibt es nach dem Ziehen |
| `Schuss_Ring_und_Treffer_X` (Patch unity-abgleich) | Spieler in der Szene, Scheibe 3 m vor dem Auge: Hüftschuss ohne Ring, Schuss im Zielen mit Ring für genau 1 Bild, Treffer-X 0,17–0,25 s, Größen 2 % / 4,5 % H, Orange `#E0651E` |
| `Altes_Format_8_wird_gelesen_Automatik_und_MP_unveraendert` (EditMode, 0.20) | `ballon-ego/9`; die Datei von main (0.19, Kopie `Tests/EditMode/Data/ego_v8.json`) wird gelesen (Dauerfeuer, `eye_m` 0), Automatik und MP sind in `/9` Feld für Feld gleich (Haltungen, Griffe, Aktionen, Spielwerte, Teile, Profil, Bewegung ohne `ads_hide`); seit 0.21 mit `Visier_0_21` (nur benannte Felder normiert: Visierrolle anodized → sight_anod; MP: Haube/Haubenkante entfallen, Scheibe glass_scope, Augenpunkt an der Scheibe) und `Visier_v3` (neue H2-Teile der MP), Netzgrenzen ohne das flache Absehen |
| `Werte_des_Scouts`, `Hueftlage_des_Scouts_im_Band` (EditMode, 0.20) | Klassenwerte Scout aus `ego.CLASSES`: Einzelfeuer aus der Spec, 180/min, Magazin 15, Weltzoom 2,0, Hüftform `cross`, `aim_in` 7 / `aim_out` 5 Bilder, Schussbilder 2/12/22, Hüfte und Sprint wie die Automatik, übrige Aktionen gleich, sieben Teile mit `ads_hide`; Hüfte: Mündung x 54–59 / y 60–71 %, Okularende 7–34 pp rechts, Kontur bis zum Rand |
| `Zielfernrohr_Oeffnung_und_Teile_im_Zielen`, `Einzelfeuer_im_Clip_ein_Zug_je_Schuss` (EditMode, 0.20) | Zielen: lichte Öffnung (Objektivlinse) 20–26 % B bei 90 mm und 75°, Absehen auf der Mitte, `ads_hide`-Teile aus, in der Hüfte da, `aim_in` schaltet einmal um; Clip: Scout je Schuss ein Zug am Abzug, Automatik/MP einer je Salve |
| `Texturen_je_Waffe_unter_der_Grenze` (EditMode, 0.20) | je Waffe Atlas + Skins ≤ `limit_mb` (50 MB), Endung und Kantenlänge je Kanal nach `TEXTURE_STORE`, wie Unity importiert |
| `Gleich_wie_Blender_Referenz` (0.20 erweitert) | dazu je Stichprobe `ads_hidden` (Zielfernrohr-Teile aus/an) gleich wie Blender, für alle drei Waffen |
| `Einzelfeuer_feuert_genau_einmal_je_Klick`, `Wechsel_1_3_2_mit_leerer_Sicht_ohne_Munitionsverlust` (PlayMode, 0.20) | Scout: gehaltener Abzug = 1 Schuss, 5 Klicks = 5, zwei Klicks im Abstand 0,1 s = 2 Schüsse im Abstand 60/180 s; Automatik und MP 12 Schuss/s; Tasten 1 → 3 → 2 → 1: leere Sicht 0,1–0,2 s, erstes neues Bild `draw` der gewählten Waffe, Munition je Waffe bleibt |
| `Altes_Format_9_wird_gelesen_drei_Waffen_unveraendert`, `Werte_des_Impulses`, `Werte_der_Portalkanone`, `Hueftlage_des_Impulses_im_Band`, `Hueftlage_der_Portalkanone` (EditMode, 0.22) | `/9` von main (0.21) als Fixture: Automatik, MP, Scout Feld für Feld gleich (Spielwerte, Teile, Profil, Haltungen, Griffe, Aktionen, Bewegung); Impuls: Salve aus der Spec (3), 900/540 pro min, Magazin 36, Bahnstufe 1,33 % H, Weltzoom 2,0, `ring_dot`, `aim_in` 10, Schussbilder in ganzen Salven, Sprint wie die Automatik, eigene Hüfte (Mündung x 54–59 / y 60–71 %); Portalkanone: ohne Zielen/Nachladen/Visier/Blitz/Hülsen/Bahnstufe, Portale A Linksklick Cyan +1 und B Rechtsklick Orange −1, 240/min, 24 m, Ring 120° in 10 Bildern; Hüfte: Achskrone x 54–63 / y 68–76 % (Portal 2), Kerbe im Bild, Stützhand am Vordergriff |
| `Salve_feuert_genau_n_Schuss_je_Abzug_mit_Salvenabstand`, `Portalkanone_dreht_Ring_120_je_Schuss_und_wechselt_Portal`, `Wechsel_1_4_5_2_mit_leerer_Sicht_ohne_Munitionsverlust`, `Kein_GC_Muell_bei_Salve_und_Portal`, `Portalkanone_im_Spieler_Taste_5_Treffermarke_in_Portalfarbe` (PlayMode, 0.22) | Impuls: ein Zug = genau 3 Schuss im Takt 60/900 s, gehalten Salvenbeginn alle 0,333 s, Bahn steigt in der Salve und erholt sich in der Pause; Automatik/MP weiter 12 Schuss/s. Portalkanone: Linksklick A (+120°), Rechtsklick B (−120°), Ring dreht weich in 0,333 s, Abklingzeit 0,25 s, gehalten ein Schuss, kein Zielen, kein Nachladen, unbegrenzt, Rechtsklick aus dem Sprint = Portal B; Tasten 1 → 4 → 5 → 2: leere Sicht 0,1–0,2 s, Munition je Waffe bleibt; Salve und Portale ohne Speicher je Bild; im Spieler Treffermarke Cyan/Orange, kein Weltzoom, Hüft-Fadenkreuz bleibt |
| `Zielfernrohr_Zoom_und_Linse_mit_dem_Modell`, `Scout_im_Spieler_Taste_3_Zielfernrohr_Einzelfeuer` (PlayMode, 0.20) | 60/s: Zoom beginnt 0–2 Bilder nach dem Modell und endet ±1 (gemessen 0 / −1, mit `gameplay.zoom_start` 0,2; mit 0,05 begann er 2 Bilder vor dem Modell), Linsenbild, sobald das Okular die Nahebene erreicht (Bild 12, 7 Bilder vor dem Ende der Restbewegung, nach dem Zoombeginn); zurück: Teile 4 Bilder vor der Hüfte wieder da; im Spieler: Taste 3, Weltzoom 2,0, `ads_hide`-Renderer im Zielen aus, gehaltener Abzug ein Schuss |
| `Weltzoom_je_Klasse`, `Hueftform_der_Automatik_aus_dem_Katalog`, `Hueft_Fadenkreuz_geht_nach_SPREAD_auf` (EditMode, 0.13) | Weltzoom Scout 2,0 / Handfeuerwaffe 1,15 / MP 1,45 / Automatik 1,9 aus den Daten; Hüftform `ring_dot` 3,2 % H, weiß, fein, Sprint `caret` 1,5 % H, sichtbares Außenmaß an den Maskenpixeln ±1 px; Aufgehen je Bild gleich `reticles.simulate` |
| `Hueft_Fadenkreuz_je_Zustand`, `Weltzoom_im_Spiel_aus_der_Klasse` (PlayMode, 0.13) | Spieler in der Szene bei 30/s: in der Hüfte sichtbar, geht beim Hüftfeuer auf und ab, im ersten Bild des Zielens weg, im Sprint nur „^“, beim Nachladen, Wegstecken und Ziehen aus, danach wieder da; Welt-FOV im Zielen = Zoom 1,9 |
| `Kein_GC_Muell_im_laufenden_Bild` | Gehen, Zielen mit Dauerfeuer, Sprintschleife, Hüft-Fadenkreuz (Aufgehen, Sichtbarkeit, Rastern): kein Speicher im laufenden Bild |
| `Wandnaehe_im_Parcours_senkt_die_Waffe` | vor Säule 1 senkt sich die Waffe (`lowered`), im Freien zurück zur Hüfte |
| `FBX_Normalen_gewichtet_an_gefasten_Teilen` (EditMode, 0.32, A6) | Normals „Import“; am Griff jeder Waffe > 50 % der Dreiecke weich (Fase), > 8 % flach (Originalflächen), > 25 % der Ecken > 2° neben lageweise geglätteten Normalen; rot mit dem Export vor 0.32 und mit „Calculate“ |
| `Viewmodel_bleibt_75_Grad_bei_Welt_FOV_60_und_100` (PlayMode, 0.32, A9) | Welt 60° und 100° waagrecht: Weltkamera folgt, Viewmodel bleibt 75°, near 0,03 m, kein Speicher je Bild |
| `Weltzoom_nur_auf_die_Welt_Zielbild_unveraendert` (PlayMode, 0.32, A9) | jede Waffe mit Absehen im Zielen, Haltung eingefroren: Welt = 2·atan(tan(eingestellt/2)/Zoom), Absehen und Glas im Bild bei 60°/100° wie bei 75° (≤ 0,1 %) |
| `Muendungsfeuer_Abdeckung_im_Zielen_unabhaengig_vom_Welt_FOV` (PlayMode, 0.32, A9) | Blitzbild aus `fire_ads` in der Viewmodel-Kamera über dem Glasrechteck gerastert: Abdeckung (± 0,2 pp), Lage und Größe des Blitzes bei 60°/100° wie bei 75° |
| `Nahe_Wand_schneidet_die_Waffe_nicht` (PlayMode, 0.32, A9) | Wand 12 cm vor dem Auge (ohne Kollider): in der Viewmodel-Maske ändert sich höchstens 0,5 % des Bildes; Viewmodel-Kamera leert die Tiefe |
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

## Viewmodel-Bildwinkel (A9, 0.32)

Regel A9 (A-R11, Nutzer 29.10.2026 „Alle wie empfohlen“, [stilhandbuch](stilhandbuch.md#2-gestaltungsregeln-v2)):
Waffe und Arme immer mit dem Bezugsbildwinkel von Visier-Standard 3, unabhängig vom Welt-Bildwinkel, mit eigenem Tiefenbereich.

- **Zwei Kameras wie bisher, nichts dupliziert:** `ViewCam` (Overlay im Stapel der `WorldCam`) zeichnet nur die Ebene „Viewmodel“ mit
  `EgoPlayer.ViewmodelHFovDeg` = `ego.json › camera.h_fov_deg` = 75° waagrecht (dieselbe Kamera wie die Blender-Stills). `WorldCam`
  folgt `worldHFovDeg` (Vorgabe 75°, Build-Option `-ballonFov 50–120`), im Zielen geteilt durch den Weltzoom der Klasse:
  tan(Welt/2) = tan(eingestellt/2) / Zoom. Vorher teilten sich beide Kameras einen Winkel.
- **Unverändert bei anderem Welt-Bildwinkel:** Zielbild (Absehen, Glas, Okular), Abdeckung durch das Mündungsfeuer, Hüftlage im Bild;
  Rückstoß-Grundbahn und Mausempfindlichkeit rechnen in Winkeln vom Bezugsbildwinkel (kein Unterschied zu vorher).
- **Tiefe:** die Overlay-Kamera leert die Tiefe (URP-Vorgabe, `clearDepth`) und zeichnet von `near_m` 0,03 m bis 6 m; eine Wand vor
  dem Gesicht verdeckt Waffe und Arme nicht. Die Wandnähe senkt die Waffe weiterhin (`lowered`, eigener Test).
- **Grenze:** Das Hüft-Fadenkreuz und die Rückmeldung bleiben Anteile der Bildhöhe; bei einem anderen Welt-Bildwinkel als 75° deckt
  sich der gezeichnete Streukreis nicht mehr genau mit dem Streuwinkel der Welt (Destiny skaliert ihn mit; nicht Teil dieses Auftrags).

## Texturen (0.20)

**Entscheidung 97 A** (Nutzer, 26.10.2026: „A“): Ego-Waffentexturen und Skins kleiner speichern – halbe Kantenlänge und/oder JPG bzw.
stärker komprimiertes PNG je Kanal, Normal-Map verlustarm, Ziel ≈ ¼ der Größe je Waffe, ohne sichtbaren Verlust im Ego-Bild.

**Regel** (`tools/export_unity.TEXTURE_STORE`, aus der Exporteinstellung, nicht von Hand): gebacken wird weiter mit 4096²
(`tools/bake_unity.py`), gespeichert wird je Kanal

| Kanal | Ablage | Grund |
|---|---|---|
| Diffusfarbe `albedo` | 4096², JPG Qualität 92, 4:4:4 | volle Kantenlänge für Kanten, Schrift und Sprenkel; JPG ohne Farbunterabtastung (PSNR 47 dB gegen das PNG) |
| Spiegelfarbe + Glätte `spec` | 2048², PNG 8 bit RGBA, linear verkleinert | JPG trägt kein Alpha; Glanz und F0 sind flächig |
| Normale `normal` | 4096², PNG 8 bit (statt 16) | verlustarm: Unity speichert Normalen ohnehin mit 8 bit je Kanal (BC5) |
| AO `ao` | 2048², PNG 8 bit, ein Kanal (statt 16 bit RGB) | niederfrequent |

Der Export legt neu gebackene Atlanten und Skins so ab und stellt übernommene beim nächsten Lauf um; ohne Blender:
`python3 tools/export_unity.py --store-textures`. `ego.json` nennt die Regel je Waffe (`textures.store`, `limit_mb` 50 MB ≈ ¼ von
BASIC-06 vorher); `export_unity.py --check` (in `./check`) und der EditMode-Test `Texturen_je_Waffe_unter_der_Grenze` prüfen Endung,
Kantenlänge (wie Unity importiert) und Summe je Waffe. Arme und LUT bleiben unverändert (nicht Teil von 97 A).

| Waffe | vorher (0.19) | nachher | Anteil |
|---|---|---|---|
| BASIC-01 v2.1 (Atlas + 7 Skins) | 145,7 MB | 39,6 MB | 0,27 |
| BASIC-06 v2.1 (Atlas + 7 Skins) | 189,4 MB | 43,8 MB | 0,23 |
| BASIC-03 v2.1 (neu, Atlas + 7 Skins) | – (direkt nach der Regel abgelegt) | 40,6 MB | – |

**Sichtprüfung im Ego-Bild** (Unity-Build, 1600 × 900, gleiche Haltung vorher/nachher, `ce evidence diff --kind bake`): Hüfte BASIC-01
SSIM 0,9991 / PSNR 40,0 dB (0,2 % Pixel geändert), BASIC-06 0,9994 / 40,2 dB, Skin Gebraucht (`inspect_l`) 0,9985 / 49,9 dB, Nachtschicht
0,9983; Kanten, Schrift und Sprenkel im Ausschnitt nicht unterscheidbar. Im Zielen (SSIM 0,990 / 0,992) liegt der Unterschied nur im Glas:
Glasmaterial und gezeichnetes Absehen (siehe unten), nicht die Texturen. Beleg `~/Library/Caches/CubeEscapeBallon/spotter/texturen_vorher_nachher.png`.

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
