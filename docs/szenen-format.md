# Szenenformat `ballon-scene/1` (Blender → Unity)

Vertrag zwischen `tools/scene_build.py` (Blender, Erzeuger) und dem Szenenlader in `unity/` (Abnehmer, ab 0.8;
Test `python3 tools/unity_run.py test`). Eine Datei je Szene:
`unity/Assets/Ballon/Generated/Scenes/<name>/scene_<name>.json`, daneben `<name>.fbx` und der Lichtatlas `<name>_light.png`.

**Koordinaten.** Blender-Welt in Metern, Z oben, Spieler blickt beim Start nach −Y, wie der Blender-Kameraraum. Nach Unity
gilt dieselbe Umrechnung wie in `ego.json › axes.to_unity`: Unity = (−x, z, −y). Winkel in Grad.

```json
{
  "format": "ballon-scene/1",
  "name": "hangar",
  "de": "Hangar",
  "fbx": "hangar.fbx",
  "light_atlas": {"file": "hangar_light.png", "size": 4096, "scale": 3.0,
                  "de": "Diffuses Cycles-Licht (direkt + indirekt) mal Farbe, sRGB; Umgebung in Unity unbeleuchtet"},
  "objects": ["Boden", "Wand_N", "..."],
  "colliders": [{"name": "Boden", "center": [0, 0, -0.05], "size": [40, 60, 0.1]}],
  "spawn": {"pos": [0, 20, 0], "yaw_deg": 0},
  "sky": {"color": "#9FB4C8", "strength": 1.0},
  "ambient": {"color": "#8C96A3", "strength": 0.45},
  "lights": [{"name": "Strahler_1", "kind": "area", "pos": [0, 0, 13], "dir": [0, 0, -1], "power_w": 800, "size_m": 1.5,
              "color": "#FFF2E0"}],
  "targets": [{"pos": [0, -10, 1.45], "distance": 10}],
  "reference": {"png": "hangar_ref.png", "camera_pos": [0, 20, 1.62], "yaw_deg": 0, "pitch_deg": 0, "h_fov_deg": 75,
                "view": "AgX", "look": "AgX - Medium High Contrast"},
  "sources": [{"path": "basic/scenes/hangar.py", "sha256": "…"}]
}
```

- `light_atlas.scale`: Der Atlas speichert Licht / scale (8 bit sRGB), der Abnehmer multipliziert mit scale. So bleiben
  Sonnenflecken über 1 erhalten (fehlt der Wert: 1).
- `angle_deg`: Öffnungswinkel eines `spot` (Blender `spot_size`, Unity `spotAngle`), fehlt: 90.
- `kind` ist `area`, `sun`, `point` oder `spot`. `dir` ist die Leuchtrichtung, `power_w` die Blender-Leistung, `size_m` die
  Kantenlänge der Fläche bzw. der Radius.
- Unity beleuchtet die Umgebung nicht. Sie trägt ihr Licht im Atlas. Die Lichter dienen nur dem Viewmodel: Spots mit
  P/π², Lichtflächen in der Reflexionssonde (P / (π·A)), wie `Bootstrap.StudioLike`.
- Zielscheiben baut Unity selbst an `targets` (wie im Parcours).
- `sources` geht in den Abgleich in `./check` ein, wie bei `ego.json`.
