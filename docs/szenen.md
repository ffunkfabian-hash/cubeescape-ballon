# Hintergrundszenen (0.8 „Hangar“)

Szenen sind Python-Daten (`basic/scenes/<name>.py`), Blender baut sie mit `tools/scene_build.py` und schreibt das Format
[`ballon-scene/1`](szenen-format.md) nach `unity/Assets/Ballon/Generated/Scenes/<name>/`. Unity zeigt die Umgebung unbeleuchtet
mit dem gebackenen Lichtatlas und beleuchtet nur das Viewmodel mit den Lichtern aus der Datei.

## Befehl und Dauer

```sh
BALLON_BAKE_GPU=1 ~/Claude/cubeescape-nexogen/ce lock gpu -- /Applications/Blender.app/Contents/MacOS/Blender -b \
  --factory-startup -P <ABSOLUTER Pfad>/tools/scene_build.py -- hangar
python3 tools/scene_build.py --check      # Teil von ./check: Datei passt zu den Quellen (SHA-256 + alle Datenfelder)
```

- Hangar auf der M5-GPU: Bau und UV unter 1 s, Backen 4096² mit 256 Samples 3,6 min, Vergleichsrender 34 s, gesamt 4,2 min.
- Testläufe ohne Repo-Ausgabe: `BALLON_SCENE_SIZE=2048 BALLON_SCENE_SAMPLES=64` (oder `BALLON_SCENE_TEST=1`) schreibt nach
  `~/Library/Caches/CubeEscapeBallon/unity/scenes/test/` (2048²/64 Samples: 24 s Backen).
- Ausgaben im Cache (nicht im Repo): `<name>_ref.png` (Cycles-Vergleichsrender vom Startpunkt), `<name>_atlas_view.png`
  (dieselbe Kamera, Umgebung unbeleuchtet mit dem Atlas – so sieht Unity sie), `<name>_build.blend`, `<name>_pano.exr`.

## Ablauf in `scene_build.py`

1. **Bau:** Jedes Bauteil (`box`, `cyl`, `beam`) wird als Flächen in Weltlage in das Netz seiner Gruppe geschrieben; eine Gruppe
   ist ein FBX-Objekt im Ursprung. Unsichtbare Seiten (`skip`, Unterseiten auf dem Boden) entfallen und kosten keinen Atlasplatz.
2. **Material:** eigene Umgebungsrollen (`ROLES` im Szenenmodul; `kit.MATERIALS` bleibt unberührt), Principled mit
   Helligkeits- und Rauheitsrauschen, Fugen (Beton, 6 m), Warnstreifen (45°) und Trapezprofil des Wellblechs als Relief (Bump),
   alle im Weltraum. Das Relief backt in den Atlas, die Wand bleibt eine Fläche.
3. **Licht:** Flächenlichter, Sonne, Welt = Himmelfarbe × Stärke (`sky`). Leuchtflächen der Strahler sind Emission (1,0).
4. **Lightmap-UVs:** alle Objekte gemeinsam, Smart UV (50°), Inseln auf gleiche Texeldichte, gepackt mit 3 Texeln Abstand.
5. **Umgebungslicht:** Panorama 256 × 128 am Startpunkt in Augenhöhe, raumwinkelgewichtetes Mittel → `ambient`
   (Farbe mit Maximum 1, Stärke = lineare mittlere Radianz). Gemessen, darum vergleicht `--check` dieses Feld nicht.
6. **Backen:** Eine zusammengefügte Kopie aller Objekte backt `COMBINED` mit Filter Emission + Diffus direkt/indirekt (ohne
   Glanz, ohne Durchlässigkeit) in einen Float-Atlas; danach sRGB 8 bit mit Dreiecks-Dither. Die Originale sind beim Backen aus
   dem Render genommen (sonst schatten die deckungsgleichen Flächen alles ab).
7. **Vergleich:** Cycles-Render vom Startpunkt (1600 × 900, 75° horizontal, AgX „Medium High Contrast“, 256 Samples,
   entrauscht) und dieselbe Ansicht nur mit dem Atlas; die mittlere Abweichung steht im Protokoll.
8. **Ausgabe:** FBX (Optionen wie `export_unity.py`: `bake_space_transform`, `FBX_SCALE_ALL`, `-Z`/`Y`), ein Material
   `<name>_light`, UV-Kanal 0 = Lichtatlas; `scene_<name>.json`.

## Auslegung des Formats (für den Unity-Lader)

- `colliders[].name` ist die Bauteil-ID (englisch, stabil). Quader nur für begehbare und anstoßbare Teile: Fachwerk, Strahler,
  Pfetten, Treppenwangen und -handläufe und die 1-cm-Bodenfarbe haben keinen.
- `targets[].distance` ist der Abstand zum Startpunkt entlang −Y (Scheibenmitte 1,45 m, seitliche Lagen wie `Range.cs`).
- `lights[]`: 20 Flächenlichter (Quadrat 1 m, nach unten) und die Sonne (`kind: sun`, `power_w` = Stärke in W/m², `size_m` 0;
  im Blender-Bau zusätzlich 1,5° Winkel).
- Der Atlas enthält Licht × Farbe. Werte über 1 werden abgeschnitten (Hangar: 0,43 % der Texel, Höchstwert 2,46 – sonnenbeschienene
  helle Flächen am Tor).

## Hangar (`basic/scenes/hangar.py`)

Halle 40 × 60 m, Dach innen 14 m; offenes Tor 34 × 11 m bei y = −30, davor Vorfeld 40 × 21,5 m mit Splitterschutzwänden (T-Wall
3,6 m). Startpunkt (0, 25, 0), Blick −Y durch die Halle; Schusslinie bei y = 22,5, Bahn x = ±10, Scheiben in 10/25/50 m.

| Was | Inhalt |
|---|---|
| Tragwerk | 20 Stützen, 10 Fachwerkbinder (Untergurt 11,2 m), 9 Pfetten |
| Hülle | Betonsockel 1,2 m, Wellblech cremeweiß, Torpfosten und -sturz mit Warnstreifen, Faltflügel |
| Licht | 2 × 10 Hallenstrahler 320 W bei x = ±8, Sonne 7 W/m² 20° hoch von vorn (fällt bis etwa y = 0 herein), Himmel `#9FBAD6` × 1,3 |
| Ausstattung | Kistengruppen, Fässer auf Paletten, Schwerlastregal (6 Felder, 3 Ebenen), Wartungsbühne 3 m mit Treppe (12 × 0,25 m), Rohrbrücke mit 1,35 m Durchgang (Ducken), Sprungkisten 0,5/1,0/1,5 m, Bürocontainer, Stromaggregat |
| Kennzahlen | 19 Objekte, 860 Bauteile, 11 740 Dreiecke, 521 Kollisionsquader; 13 112 m² Oberfläche, Atlas 63 % belegt, **28,4 Texel/m (3,5 cm je Texel)** |
| Abgleich | mittlere Abweichung Atlasansicht ↔ Cycles-Render 5,4/255; `ambient` gemessen `#FFECCD` × 0,1675 |

Grenzen: Glanz fehlt in Unity (der Cycles-Render zeigt etwas Gegenlicht-Schimmer auf dem Boden vor dem Tor, darum Beton mit
Specular 0,15). Eine Cubemap für Spiegelungen am Viewmodel erzeugt `scene_build.py` noch nicht.
