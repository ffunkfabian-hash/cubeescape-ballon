# Szenenformat `ballon-scene/2` (Blender → Unity)

Vertrag zwischen `tools/scene_build.py` (Blender, Erzeuger) und dem Szenenlader in `unity/` (Abnehmer ab 0.9, Test
`python3 tools/unity_run.py test`). Eine Datei je Szene: `unity/Assets/Ballon/Generated/Scenes/<name>/scene_<name>.json`, daneben
`<name>.fbx` und die Lichtatlanten. Ältere Dateien (`ballon-scene/1`, 0.8) lehnt Unity mit „neu bauen (tools/scene_build.py)“ ab.

**Koordinaten.** Blender-Welt in Metern, Z oben, Spieler blickt beim Start nach −Y, wie der Blender-Kameraraum. Nach Unity
gilt dieselbe Umrechnung wie in `ego.json › axes.to_unity`: Unity = (−x, z, −y). Winkel in Grad.

## Neu in /2 (0.9)

- **`zones`:** Die Umgebung ist in Zonen geteilt, jede mit eigenem UV-Satz und Atlas. Nahe Bereiche bekommen eine höhere
  Texeldichte. Jedes Objekt gehört zu genau einer Zone. Die UVs sind für alle Lichtvarianten gleich.
- **`lightings`:** Mehrere Lichtszenen derselben Geometrie. Jede bringt eigene Atlasdateien je Zone, Himmel, Umgebungslicht,
  Lichter und ein Referenzbild mit. Der erste Eintrag ist der Standard.
- **`course`:** ein Parcours mit Start- und Zieltor, Kontrollpunkten in Reihenfolge, Zielscheiben entlang der Strecke und
  einer Richtzeit.
- `targets` (Schießstand ohne Strecke) bleibt optional.

```json
{
  "format": "ballon-scene/2",
  "name": "hangar",
  "de": "Hangar",
  "fbx": "hangar.fbx",
  "zones": [{"name": "nah", "objects": ["Boden_Mitte", "Kisten", "..."], "size": 4096, "texel_m": 0.015}],
  "objects": ["Boden_Mitte", "..."],
  "colliders": [{"name": "kiste_03", "center": [2, 10, 0.6], "size": [1.2, 1.2, 1.2]}],
  "spawn": {"pos": [0, 25, 0], "yaw_deg": 0},
  "lightings": [
    {"name": "tag", "de": "Tag",
     "atlases": {"nah": "hangar_tag_nah.png", "fern": "hangar_tag_fern.png"}, "scale": 3.0,
     "sky": {"color": "#9FBAD6", "strength": 1.3},
     "ambient": {"color": "#FFECCD", "strength": 0.17},
     "lights": [{"name": "Sonne", "kind": "sun", "pos": [0, -80, 45], "dir": [0.36, 0.87, -0.34], "power_w": 7.0, "size_m": 0,
                 "angle_deg": 0, "color": "#FFF0D8"}],
     "reference": {"png": "hangar_tag_ref.png", "camera_pos": [0, 25, 1.62], "yaw_deg": 0, "pitch_deg": 0, "h_fov_deg": 75}}
  ],
  "course": {
    "start":  {"center": [0, 22, 1.2], "size": [6, 0.4, 2.4]},
    "finish": {"center": [8, 22, 1.2], "size": [6, 0.4, 2.4]},
    "checkpoints": [{"name": "Gerüst oben", "center": [-12, 0, 5.2], "size": [3, 1, 2.4]}],
    "targets": [{"name": "T01", "pos": [-6, 10, 1.6], "normal": [0, 1, 0], "radius": 0.3}],
    "route": [[0, 22, 0], [-6, 12, 0], [-12, 0, 4.5]],
    "par_time_s": 45
  },
  "targets": [],
  "sources": [{"path": "basic/scenes/hangar.py", "sha256": "…"}]
}
```

- **Lichter:** `kind` ist `area`, `sun`, `point` oder `spot`.
  - `dir` ist die Leuchtrichtung, `power_w` die Blender-Leistung (bei der Sonne die Stärke in W/m²).
  - `size_m` ist die Kantenlänge der Fläche bzw. der Radius.
  - `angle_deg` ist der Öffnungswinkel eines `spot`; fehlt er, gilt 90.
- **Atlanten:** speichern Licht / `scale` (8 bit sRGB). Unity multipliziert mit `scale`, so bleiben Sonnenflecken über 1
  erhalten.
- **Beleuchtung:** Unity beleuchtet die Umgebung nicht, sie trägt ihr Licht im Atlas. Die Lichter dienen nur dem Viewmodel:
  - Flächenlicht mit P/π², Spot und Punktlicht mit P/(4π²), Sonne mit S/π;
  - dazu Lichtflächen in der Reflexionssonde mit P/(π·A), wie `Bootstrap.StudioLike`.
- **Parcours:** Tore und Kontrollpunkte sind achsparallele Auslösequader. Die Zielscheiben baut Unity an `course.targets`:
  Mitte `pos`, Blickrichtung `normal`, Radius `radius`. `route` ist die Strecke für Wegmarken am Boden; `z` ist die Höhe der
  Lauffläche (auf Kisten und Gerüst ungleich 0). Start und Ziel dürfen derselbe Quader sein (Runde): Dann gewinnt das Ziel, sobald alle
  Kontrollpunkte passiert sind, sonst startet das Tor den Lauf neu.
- **Pflicht und optional:** Pflicht sind `format`, `name`, `fbx`, `zones` (mit `name`, `objects`, `size`), `objects`, `colliders`,
  `spawn`, `lightings` (mit `name`, `atlases` für jede Zone, `scale` > 0, `sky`, `ambient`, `lights`). Optional sind `de`, `texel_m`,
  `reference`, `course`, `targets` und `sources`; Unity liest `reference` und `sources` nicht.
- **`sources`** geht in den Abgleich in `./check` ein, wie bei `ego.json`.
