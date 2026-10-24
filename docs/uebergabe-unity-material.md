# Übergabe: Unity so nah wie möglich an die Blender-Vorlage (0.7 „Truecolor“)

Stand 24.10.2026, aus der Sitzung BALLON 0.4 „Firstfeel“ · Mac. Geschrieben für eine **frische Sitzung ohne Verlauf**.
Opus 5.5 `high`, Grund: Darstellung und Pipeline (Backen, Shader, Nachbearbeitung), Abnahme am Bild.

## Auftrag des Nutzers

> „Ich würde dich bitten, auch für die Zukunft, das Unity … so nah wie möglich auf die Blender-Vorlage ran kommt. Bitte setze
> das um.“

Das ist dauerhaft als Regel in [AGENTS.md](../AGENTS.md) festgehalten.

**Anlass:** Im Standbildvergleich wirkt Unity flacher und dunkler als Cycles. Form, Maße und Bewegung sind schon 1:1 (Referenztest
≤ 0,22 mm). Abweichungen gibt es nur bei Material, Licht und Tonwerten.

**Ziel:** Gleiche Haltung, gleiche Kamera, und im Bild sollen Material und Licht dem Cycles-Bild nahekommen. Gemeint sind
Kantenabrieb, Schmutz, Relief und AO, das Metall mit seinen Spiegelungen, die Tonwerte nach AgX und der graue
Verlaufshintergrund.

- **Dateien/Zuständigkeit:**
  - Neu oder geändert: `tools/export_unity.py`, neu `tools/bake_unity.py` (Backen in Blender), `unity/` (Materialien,
    Nachbearbeitung, Studio- und Parcourslicht), `docs/unity.md`, Bericht `docs/versions/0.7-truecolor.md`.
  - Nur lesen: `basic/kit.py` (`aaa_nodes`, `MATERIALS`, `WEAR`, `GRIME`, `BUMP`), `tools/blender_build.py` (`setup_render`,
    `setup_aaa`, `BACKDROPS`), `tools/ego_build.py`.
  - Nicht anfassen: die Visierformen in `basic/common.py`. Ihre Designsprache ist noch offen (Analyse „Visiere in
    Videospielen“); bei Formänderungen nur neu exportieren und neu backen. `basic/robot/` gehört der Roboter-Sitzung.
- **Prüfen:**
  - `./check`, Unity EditMode und PlayMode.
  - Der Standbildvergleich hip/ads/reload/inspect_r gegen **frisch gerenderte** Blender-Stills: `tools/ego_build.py --stills`
    unter `ce lock gpu` mit `--gpu`.
  - Eine Bildkennzahl je Pose, z. B. mittlere Farbabweichung ΔE oder SSIM über die Viewmodel-Maske (`./ce evidence diff` oder
    eigene Messung). Werte vor und nach der Änderung festhalten.
- **Fertig wenn:**
  - Der Vergleich zeigt sichtbar Kantenabrieb, AO und Metallspiegelungen in Unity.
  - Die Kennzahl ist deutlich besser als vorher und im Bericht genannt.
  - Tests sind grün, die macOS-Build ist neu.
  - Die Build kostet höchstens 16,7 ms je Bild, also 60 fps, im Parcours auf dem MacBook Air; gemessen und genannt.
- **Release:** nein. Vor dem Merge kommt der Richter (`ce judge --repo <worktree> --base claude/basic-first-light --files
  <Quellen ohne Generated>`).

## Weg (empfohlen)

1. **UV und Backen in Blender** (`tools/bake_unity.py`, Sperre `gpu`):
   - Die generierten Teile haben keine UVs. Je Objekt nach dem Anwenden der Modifikatoren „Smart UV Project“ oder Lightmap
     Pack, dann ein Atlas je FBX: Waffe 4096², Arme 2048², Ränder ≥ 8 px.
   - Gebacken wird aus `kit.aaa_nodes` mit dem aktiven Skin.
   - Grundfarbe mit Abrieb und Schmutz: Emission-Trick, also die Farbe vor dem BSDF auf Emission legen und `EMIT` backen.
   - Rauheit und Metall genauso, gepackt in `MetallicGlossMap` (R Metall, A Glätte = 1 − Rauheit).
   - Normal (Bump/Relief) im Tangentenraum, AO mit Cycles.
   - Die UVs und Texturen ins FBX bzw. nach `unity/Assets/Ballon/Generated/Textures/`. Die Quellen kommen in den SHA-256 von
     `ego.json › sources`.
   - Der Import setzt die Knotenlagen weiter aus `ego.json` (`BallonModelImport`). Die UVs kommen aus dem FBX; prüfen, dass
     Unity sie nicht neu erzeugt.
2. **Materialien in Unity:** URP Lit je Atlas mit `_BaseMap`, `_MetallicGlossMap`, `_BumpMap` und `_OcclusionMap`.
   - Die Rollen-Materialien bleiben nur als Rückfall.
   - Glas und Energie behalten Sondermaterialien. Energie leuchtet ohne Bloom, das ist eine Entscheidung des Nutzers.
3. **Tonwerte:** URP-Volume mit Nachbearbeitung.
   - AgX gibt es in URP nicht. Darum eine LUT aus Blender backen: einen Farbwürfel durch die View Transform „AgX – Medium High
     Contrast“ rendern und als `ColorLookup` in Unity einsetzen. Kein Bloom.
   - `postProcessData` des Renderers ist intern. Den Renderer deshalb über `UniversalRenderPipelineAsset.CreateRendererAsset`
     anlegen (internal, per Reflection) oder aus dem URP-Paket laden.
   - HDR in der URP-Pipeline einschalten.
4. **Licht:**
   - Im Vergleichsmodus wie `setup_aaa`: Key, Fill, Rim und Top als weiche Punkt- oder Spotlichter. URP kennt keine
     Echtzeit-Flächenlichter, daher die Weichheit über Schattenfilter.
   - Die Umgebung aus `BACKDROPS['mid']` (Verlauf #4C525A → #9EA4AC) als Hintergrund, Umgebungslicht #8C96A3, Stärke 0,45. Am
     besten als Cubemap aus der Blender-Welt backen und als Reflexion und Umgebung nutzen.
   - Dazu SSAO als Renderer-Feature und Schatten am Viewmodel.
   - Im Parcours dieselben Materialien und dieselbe LUT.
5. **Vergleich ausbauen:** `tools/unity_run.py compare` misst die Kennzahl je Pose und schreibt sie in den Kontaktbogen.

## Ausgangslage

- Branch `claude/ballon-0.7-truecolor` von `claude/basic-first-light`. Diese Übergabe ist dort der erste Commit; 0.4 ist
  gemergt.
- Unity 6000.6.2f1, URP 17.6, Input System 1.20.
- Ablauf und Befehle: [unity.md](unity.md).
- Unity-Läufe über `~/Claude/cubeescape-nexogen/ce lock unity -- …`, Blender über `ce lock blender` bzw. `ce lock gpu`.
  Skriptpfade absolut angeben, weil `ce lock` das Verzeichnis wechselt.
- Heutige Materialien: `BallonSetup.Materials` (URP Lit je Rolle). Reflexionssonde in `Bootstrap`. Vergleichsmodus
  `Bootstrap.Compare` mit Richtungslichtern.
- Belege unter `~/Library/Caches/CubeEscapeBallon/unity/`. Dort liegt der aktuelle Vergleich `firstfeel_vergleich.png`; seine
  Blender-Stills sind älter als Visier v2.
- Lehren: [LESSONS.md](LESSONS.md) (FBX-Kindknoten, `ce lock`, `Quaternion.Angle`).
- Getrennt von Cube Escape, Toolgen und Robogen, diese nur lesen. Nie auf `main` committen, kein Push.
