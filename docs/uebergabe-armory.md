# Übergabe 0.33 „Armory“ – nach P2

Stand: Branch `claude/ballon-0.33-armory` (Basis `main` d0c7b8c, 0.32 „Softgrip“). Die erste Sitzung (Opus 5.5, high) hat P1
erledigt und übergibt hier an eine **frische Sitzung ohne Verlauf** (globale Regel: Übergabe am Etappenende, keine Fork-Übergabe).
Auftrag unverändert wie in der Zielsitzung 0.33 „Armory“ (Sightline, 30.10.2026); diese Datei ersetzt den Verlauf.

## Erledigt (P1)

- **Visier-Umzug:** alle Produktionsvisiere aus `basic/pilot/optics/sight_kit.py` nach `basic/common.py` (K1 `klammer`, K2 `hoerner`,
  Z2 `gabel`, Z3 `lang`, F1 `boegen`, H3 `zinken`, H6 `achteck`, W1 `d_linse`, W2 `entfernung`, B1 `pins`, `side_mount` samt
  Konstanten). `sight_kit.py` behält Katalog, Prüfkörper und Entwürfe und importiert die Bausteine; die Pilotmodule importieren aus
  `basic.common`. Nachweis bitgleich: `parts_sha` und Anker aller 16 Waffen und die 75 Katalogvarianten (`sight_kit`, `sight_kit_more`)
  vor/nach gleich. `sight_kit_more.py` ist nicht produktiv (nur Varianten) und blieb.
- **Klassen 04 Handfeuerwaffe, 05 Seitenwaffe** in `ego.CLASSES` (Werte und Fundstellen: [armory-klassenwerte.md](armory-klassenwerte.md)),
  `EGO_GRIPS`/`EGO_LIVE` in den Modulen, `export_unity.WEAPONS` (Taste 6 und 7). Neue Klassenfelder in `ego.profile`:
  `bob` (Sprint-Hub der Klasse), `mech_map` (Bauteil der Bezugsaktion → Bauteil der Klasse, Pistole: `charging_handle` → `slide`),
  `charge_back_mm` (Durchladeweg), `same_reload` (leer = taktisch, Trommel), Klassenaktionen laufen jetzt mit `TIME_SCALE` (außer
  `fire*`), `FIRE_ALIAS` (`semi_auto_double_action` → `semi_auto`). `flash_cover_ads` gibt bei Kimme/Korn `None` (keine Öffnung).
- Unity: Tasten 1–9 nach `ego.json` (`EgoInput.Digits`), EditMode-Test `Klassen_vollstaendig_in_ego_json` (Liste `Playable`),
  `Umfang` erlaubt Waffen ohne Auswurfklappe.
- Voller Export mit Backen (common.py liegt im Quellenhash), Silhouetten und Freihaltezone neu, Stilhandbuch § 6.

## Erledigt (P2)

- **Klassen 09 Scharfschütze, 12 Spurgewehr, 15 MG** spielbar (Tasten 8, 9, 0). Neue Feuerarten: `bolt_action` (Repetierer, Klassenaktionen
  `fire_cycle`/`fire_cycle_ads`, Hülse beim Marker `Eject`) und `continuous_beam` (Dauerstrahl, Leuchtteile `EGO_LIVE glow`, Unity
  `EgoRig.SetGlow`); `full_auto_belt` als `FIRE_ALIAS`. MG-Nachladen als Klassenaktion mit eigenem Griff `cover`.
- Bauteil des Nachladens aus dem Griff `mag` (`ego.profile › mag`, Unity `EgoFile.MagPart`) statt fest `magazine`.
- **Skins nur bei Bedarf** (`export_unity.SKIN_WEAPONS`, Hebel 1 unten): P2-Waffen haben nur den Standard-Atlas.

Ergebnisse, Messungen und Repo-Größe stehen im Versionsbericht [versions/0.33-armory.md](versions/0.33-armory.md).

## Rest des Auftrags

Der Zwischenstopp Repo-Größe entfällt: Nutzer 30.10.2026 „Scheiß auf das Limit von 1 GB“ – weiter backen, Größe nur messen und im
Bericht nennen.

Reihenfolge mit Stopp und Postfach-Meldung (Nexogen #16) nach jedem Paket:

- ~~P2 09 Scharfschütze, 12 Spur, 15 MG~~ erledigt
- **P3 08 Schrotflinte, 10 Fusion, 11 lineare Fusion**
- **P4 07 Bogen, 13 Granatwerfer, 14 Raketenwerfer**
- **Ziel 2 HUD und Waffenmenü** (Symbole per ImageMagick aus `data/silhouettes.json`, HUD ohne Speicher je Bild, Menü Tab/Mausrad,
  Pfeile/Enter/Esc, Auswahl löst holster → draw aus, Nachladen bricht ab wie `reload_to_switch`; Sichtprüfung 1470 × 956)
- Abnahme wie im Auftrag (Tests, Belege, Bericht, Richter, Merge-Bitte an Sightline, Testbuild nach dem Merge).

### So kommt eine Klasse dazu (Muster aus P1)

1. `basic/arms/ego.py › CLASSES[<type>]`: `poses` (mindestens `hip`, `sprint`; `reload` wenn die Bezugshaltung nicht passt), `frames` +
   `frames_src`, `gameplay` (rpm, magazine, ggf. path_up_h, kick, recover_*), `src`; Sonderabläufe als `actions` (wie `reload_tactical`
   der Trommel). Herkunft je Wert M/S/E mit Fundstelle; fehlt eine Messung: E und Zeile in der Entscheidungsliste.
2. Waffenmodul `basic/pilot/wNN_*_v21.py`: `EGO_GRIPS` (grip, support, mag, charge – Autorenmaß, `part` = bewegliches Bauteil),
   `EGO_LIVE` (trigger, bolt, port; leer = fehlt), `EJECT` (Modul hat es meist schon).
3. `tools/export_unity.py › WEAPONS` anhängen (Taste = Reihenfolge), Unity-Test `Playable` ergänzen.
4. Bildlagen ohne Blender rechnen: Mündung/Anker im Bild nach `ego_build.pose_matrix` (Kamera 75° waagrecht, 16:9; x % = 50 + 50·(−X)/(−Y·tan 37,5°),
   y % = 50 − 50·(Z/−Y)/(tan 37,5°·9/16)); dann Stills prüfen:
   `BASIC_OUT=~/Library/Caches/CubeEscapeBallon/0.33/blender_out ce lock gpu -- Blender -b --factory-startup -P <abs>/tools/ego_build.py -- --stills --gpu --weapon pilot.<modul>`
   (≈ 2,5 min je Waffe; `ego/ego.json` meldet Handgelenk und Überstreckung je Haltung).
5. Export: neue Waffe backt allein (≈ 10–12 min GPU), die übrigen bleiben (`reuse`), solange `common.py`, `kit.py`,
   `blender_build.py`, `bake_unity.py`, `robot_arm.py` unverändert bleiben. Danach `ego_clear.py` (A4) und `./check`.

### Was P2–P4 in Unity brauchen (Feuerarten)

`ego.FIRE_MODES` kennt `full_auto`, `semi_auto`, `burst`, `single`; die übrigen Specs brechen in `ego.profile` ab, bis sie eine
Spielart haben:

| Klasse | META fire | Vorschlag |
|---|---|---|
| 15 MG | `full_auto_belt` | `FIRE_ALIAS` → `full_auto`; Nachladen als Klassenaktion (Deckel `feed_cover`, Kasten `ammo_box`, Gurt) |
| 09 Scharfschütze | `bolt_action` | Einzelfeuer mit Repetieraktion nach jedem Schuss (`bolt_handle`/`bolt`), Kammerstängel links (LESSONS) |
| 12 Spur | `continuous_beam` | Dauerfeuer mit 1000/min ohne Blitz/Hülse, Strahl als Leuchtteil (`disc_lens`, `focus_lens` glow) |
| 08 Schrot | `pump_action` | Einzelfeuer + Pumpaktion; Nachladen je Patrone (`load_shell`, `shell_round`), abbrechbar durch Feuer |
| 10 Fusion | `charge_burst` | Aufladen (Feuer halten, `charge` glow) → Salve 5–6 Strahlen in 0,25 s |
| 11 lineare Fusion | `charge_single` | Aufladen → ein Schuss |
| 07 Bogen | `draw_release` | Spannen (Feuer halten), Halten, Lösen; kein Magazin (Vorrat), kein Blitz; `let_down` beim Abbrechen |
| 13/14 Werfer | `single_shot` | Einzelschuss, Magazin 1, Nachladen nach jedem Schuss als Klassenaktion |

Unity-Stellen: `EgoData.Semi`/`BoltAction`/`Beam`, `EgoController` (Feuerlogik, `MagIn` füllt das Magazin, `CanReload`, `Cycle()` nach dem
Schuss), `EgoSolver.Layers` (Live-Teile je Schuss, `glow`), `EgoRig.SetGlow`. Neue Feuerarten brauchen eigene PlayMode-Tests (Gegenprobe rot
mit dem alten Code). Muster für P3: Pumpe (08) wie `fire_cycle` des Repetierers (Klassenaktion nach dem Schuss, sperrt per Busy); Aufladen
(10/11) braucht einen Zustand „Feuer gehalten“ vor dem Schuss – neu im Controller; die Leuchtteile `charge` gehen über `EGO_LIVE glow`.

### GPU auf anderen Rechnern (RTX 4060)

`tools/gpu_device.enable(scene)` wählt OptiX, sonst CUDA, HIP, oneAPI, Metal und bricht ohne GPU ab (statt still auf der CPU zu
rechnen). Die drei Stellen mit festem `compute_device_type = 'METAL'` – `tools/bake_unity.bake_atlas`, `tools/blender_build.setup_render`,
`tools/scene_build.setup_cycles` – rufen es **noch nicht** auf: alle drei Dateien liegen in Quellenhashes (bake_unity, blender_build im
Unity-Quellenhash → jede Änderung backt alle Waffen neu, ≈ 30 min je Waffe auf dem M5; scene_build im Szenen-Hash → Szenen neu). Umstellen
beim ersten Lauf auf der RTX 4060 (Nutzer 30.10.2026: „Beim ersten RTX-Lauf“), im selben Commit wie der dortige volle Export mit
Backen, der zugleich die Backzeit gegen den M5 misst (≈ 4–5 min Atlas + 7 Skins je ≈ 3–3,5 min je Waffe): je Stelle die
fünf Zeilen `pr = …` bis `sc.cycles.device = 'GPU'` durch `from tools import gpu_device` und `kind, names = gpu_device.enable(sc)` ersetzen,
Art und Namen ausgeben. Außerdem auf dem PC: Blender-Pfad statt `/Applications/Blender.app`, `ce lock`, Cache-Pfade.

### Backzeit sparen (Nutzer 30.10.2026: „wenn wir Zeit sparen können und es sinnvoll ist auf jedenfall aufnehmen“)

Gemessen im Export 0.33 auf dem M5: je Waffe 26 Backaufrufe (Atlas 5, je Skin 3 × 7 Skins) ≈ 28 min. Jeder Aufruf hat ≈ 35–40 s
Grundlast (Normale ohne Rechenarbeit: 41 s – Szene an Cycles, BVH, 4096² zurücklesen, Bild schreiben; überwiegend CPU, ein Kern),
nur ≈ 10–30 s sind GPU. Darum bringt eine schnellere GPU beim Backen wenig: RTX 4060 + i7-9700K (halbe Einzelkernleistung des M5)
geschätzt ≈ 30–40 min je Waffe, eher langsamer; bei Renderings (Stills, Clips, Lightmaps) ≈ 2× schneller. Hebel, vor P2 prüfen:

1. **Skins nur bei Bedarf** – umgesetzt in P2 (`SKIN_WEAPONS`, `BALLON_BAKE_SKINS=all`). Ursprünglicher Vorschlag: neue Waffen backen zuerst nur den Atlas (5 Aufrufe ≈ 7 min statt 28), Skins mit einem eigenen
   Schalter bzw. Lauf. P2–P4 (9 Waffen) sparen ≈ 3 h. Klären: Unity-Tests und `textures.skins` mit 0 Skins je Waffe (Taste K schaltet
   dann nur vorhandene), Bericht nennt, welche Waffen Skins haben. Änderung in `export_unity.py` (Bewegungsquelle, kein Neubacken);
   wenn `bake_unity.py` geändert werden muss: gemeinsam mit dem nächsten vollen Export (Quellenhash).
2. **Skins je Pass in einem Aufruf**: je Skin eine Kopie des zusammengefügten Objekts mit eigenem Zielbild, 3 statt 21 Aufrufe – spart
   Grundlast, aber laut LESSONS wächst die Backzeit mit der Zahl der Objekte; erst an einer Waffe messen.
3. **Zwei Rechner parallel**: Mac backt, PC rendert Stills/Clips/Lightmaps (bei Renderings schneller). Waffen auf zwei Rechnern getrennt
   backen geht erst mit einem Schritt, der zwei `ego.json` zusammenführt.

### Hinweise

- Aufteilung Roboter/Waffen (Sightline im Postfach #16, Kommentar 6522039900, Nexogen #55): BALLON macht nur Waffen samt Ego-Ansicht
  und Ego-Armen, Critic die Roboter (übernimmt die Ego-Arme unverändert). Armory fasst die Roboter-Reste nicht an; Doku-Änderungen
  folgen dieser Aufteilung.
- Motiongen REF 0.32 „Spectator“ (Postfach #16, Kommentar 6523848528): Waffe am Körper von außen (Rückensockel diagonal ≈ 40°, schwere
  Waffe auf der Schulter ≈ 24°, Ruhehaltung tiefe Bereitschaft, ein Handmaß für Ego und außen). Nicht Teil von Armory (Ego); Quelle für
  einen späteren Auftrag, entschieden wird in BALLON. Folgemeldung REF 0.33 „Gaitline“ (Nachladen/Wechsel von außen) kommt nach deren Merge.

- `ce lock gpu` ist exklusiv; Unity-Läufe über `tools/unity_run.py` nehmen `ce lock unity` selbst.
- C# vor dem Unity-Lauf mit `dotnet build` prüfen: Wegwerf-csproj außerhalb des Repos mit `Compile` auf `unity/Assets/Ballon/{Runtime,Tests,Editor}`,
  Referenzen `Unity.app/Contents/Resources/Scripting/Managed/UnityEngine/*.dll` (ohne `UnityEditor.dll`, doppelt mit CoreModule),
  `unity/Library/ScriptAssemblies/*.dll` ohne `Ballon.*`, NUnit aus `Library/PackageCache/com.unity.ext.nunit@*`.
- Belege der Sitzung unter `~/Library/Caches/CubeEscapeBallon/0.33/`.
