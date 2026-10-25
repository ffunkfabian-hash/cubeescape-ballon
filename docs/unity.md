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
python3 tools/export_unity.py --check       # ego.json passt zu den Daten und zu den Quellen (SHA-256), läuft in ./check
python3 tools/unity_run.py setup            # URP, Ebene „Viewmodel“, Input System, Materialien je Rolle, Szene
python3 tools/unity_run.py test             # EditMode + PlayMode
python3 tools/unity_run.py build            # unity/Build/BallonFirstfeel.app (Entwicklungsbuild)
python3 tools/unity_run.py capture          # MP4 des Ablaufs (720p, 30 fps) + Kontaktbogen
python3 tools/unity_run.py compare          # Standbilder hip/ads/reload/inspect_r gegen die Blender-Stills, SSIM/PSNR/Helligkeit
python3 tools/unity_run.py bench            # Bildzeiten im Parcours (ohne VSync)
open unity/Build/BallonFirstfeel.app        # spielen
```

Alle Unity-Läufe gehen über `ce lock unity`. Protokolle, Testergebnisse und Belege liegen unter
`~/Library/Caches/CubeEscapeBallon/unity/`. Nach jeder Änderung an `basic/arms/*.py` oder der Pilotwaffe den Export wiederholen,
danach `setup` (Materialien, Szene) und `test`.

## Steuerung

| Eingabe | Wirkung |
|---|---|
| Maus | umsehen (0,08°/Punkt, im Zielen durch den Zoom geteilt; nicht invertiert) |
| W A S D, Shift | gehen, sprinten (nur vorwärts, nicht im Zielen oder beim Feuern) |
| Strg oder C, Leertaste | ducken, springen |
| linke Maustaste | Dauerfeuer, 600/min; Abzug bei leerem Magazin lädt selbst nach |
| rechte Maustaste | zielen (Welt-FOV × 1/1,35, Viewmodel bleibt bei 75° horizontal) |
| R | nachladen: taktisch bei Restmunition, sonst leer (mit Durchladen) |
| F | betrachten; Feuer, Zielen, Nachladen oder Sprint brechen ab |
| 1 / 2 | ziehen / wegstecken (beim Nachladen: `reload_to_switch`) |
| Esc, Klick, H | Maus freigeben, Maus fangen, Anzeige ein/aus |

Der Parcours ist grau: Boden mit Meterraster, Wände, Brüstung, Deckungen, Rampe mit Podest, Treppe, ein niedriger Durchgang
zum Ducken und Säulen zum Testen der Wandnähe (`lowered`). Zielscheiben stehen in 10, 25 und 50 m, je drei. Treffer zählt die
Anzeige oben links, Einschläge bleiben als Punkte sichtbar.

## Aufbau

| Teil | Datei | Aufgabe |
|---|---|---|
| Export | [`tools/export_unity.py`](../tools/export_unity.py) | FBX (Waffe: Wurzel → `ASM_*` → Teile, Anker als Leerknoten; Arme: `R_`/`L_`-Segmente → Teile), `ego.json` (`ballon-ego/3`), `ego_reference.json` |
| Daten | `Runtime/EgoData.cs` | JsonUtility-Klassen, Prüfung des Formats |
| Rechnen | `Runtime/BMath.cs`, `Runtime/EgoSolver.cs` | Blender-Kameraraum; `pose_matrix`, Hermite-Kurven, Feder-Nachlauf, Griffe, Zwei-Knochen-Arm mit Drehgelenk, Finger, Magazin, Rückstoßfeder |
| Zustand | `Runtime/EgoController.cs` | Spuren mit Markern, Haltungen (Hüfte, Zielen, Sprint, Ducken, Luft, gesenkt), Übergänge, Überblendung, Live-Ebenen |
| Szene | `Runtime/EgoPlayer.cs`, `EgoRig.cs`, `Range.cs`, `Bootstrap.cs` | Bewegung, Kameras (Welt + Overlay), Treffer, Anzeige, Parcours, Aufnahme- und Vergleichsmodus |
| Editor | `Editor/BallonSetup.cs` | Importeinstellungen, Knotenlagen aus `ego.json`, URP, Materialien, Szene, Build |
| Tests | `Tests/EditMode`, `Tests/PlayMode` | siehe unten |

**Format.** `ego.json` hat das Format `ballon-ego/3`. Der Abnehmer ist `unity/` ab 0.7.2. Die Stufen:
- 2 (0.7): Texturen, AgX-LUT, `emit_only`;
- 3 (0.7.1/0.7.2): Spiegelkarte `spec` statt `mask`, `textures.skins`.

Ältere Exporte (`/1`, `/2`) lehnt `EgoFile.Parse` mit dem Hinweis „neu exportieren“ ab.

**Achsen.** Die Umrechnung steht einmal in `ego.json › axes.to_unity`: Unity = (−x, z, −y) aus Blender. Matrizen werden als
M·B·Mᵀ umgerechnet. Gerechnet wird überall im Blender-Raum, umgerechnet erst beim Setzen der Transforms. Die Netze kommen aus dem
FBX (mit „Apply Transform“). Die Lagen der Knoten setzt der Importer aus `ego.json`, weil das FBX die Kindknoten der Waffe verdreht
und versetzt (beim ersten Import gemessen: 90° am Magazin, bis 218 mm).

**Live statt geskriptet.** Abläufe, Haltungen und Marker kommen aus den Aktionen in `ego.py`, gestreckt mit `TIME_SCALE`. Im Spiel
ersetzt der Controller die geskripteten Ebenen durch live gerechnete:

- Schüsse kommen aus der Kadenz und lösen Impulse in die Rückstoßfeder `RECOIL` aus, die Kamera federt getrennt.
- Das Hochziehen klingt erst nach dem Feuern ab.
- Das Gehwippen folgt der Laufgeschwindigkeit, mit den Werten aus `walk`/`sprint`.
- Das Atmen nutzt `BREATHE_ALL`, dazu in Ruhe die `idle_hip`-Formel.
- Der Feder-Nachlauf `SECONDARY` läuft in Echtzeit über alle Spurwechsel.
- Das Pendeln aus der Maus ist eine eigene gedämpfte Feder (entworfen).

Spielwerte, die nicht aus Blender kommen, stehen in `EgoTuning` und `MoveTuning`: Laufgeschwindigkeiten, Zoom, Streuung,
Pendeln und Blickhochziehen. Alle sind entworfen.

## Tests

| Test | prüft |
|---|---|
| `Format_und_Umfang`, `Falsches_Format_wird_abgelehnt` | JSON-Import: Format `ballon-ego/3`, 10 Haltungen, 4 Griffe, 19 Aktionen, 72 Teile (Visier v2 aus 0.6), vier Finger, sortierte Schlüssel |
| `Achsumrechnung_Blender_nach_Unity` | Determinante −1, vorn/oben/rechts, Mündung vorn oben, Drehsinn bleibt erhalten |
| `FBX_Import_passt_zur_Achsumrechnung` | Netzgrenzen jedes der 206 Netzobjekte = umgerechnete Blender-Grenzen (≤ 0,5 mm), Maßstab 1 |
| `FBX_Ruhelagen_und_Anker_wie_in_den_Daten` | Lage aller Teile und Anker im importierten Modell |
| `Armlaengen_in_allen_Bildern` | Ober-/Unterarm 0,32/0,30 m in allen Haltungen und allen Bildern aller Aktionen |
| `Handgelenkknick_hoechstens_45_Grad` | Knick ≤ 45° in allen Haltungen und Bildern |
| `Gleich_wie_Blender_Referenz` | Weltmatrizen von Waffe, Mechanik, Magazin, Kamera und 16 Armsegmenten in 219 Stichproben gegen `tools/ego_build.evaluate` (≤ 0,5 mm, ≤ 0,1°) |
| `Jede_Aktion_endet_mit_Markern_in_Reihenfolge` | alle 19 Aktionen enden in ihrer Bildzahl, Marker in Datenreihenfolge, keine NaN |
| Spielablauf (6 Tests) | Kadenz und Magazin, leeres/taktisches/automatisches Nachladen, Zielen hin und zurück (Auge auf der Kameraachse), Betrachten abbrechen, Wegstecken beim Nachladen und Ziehen, Sprintschleife und Übergänge, Ducken/Springen/Wandnähe |
| `Kein_GC_Muell_im_laufenden_Bild` | Gehen, Zielen mit Dauerfeuer, Sprintschleife: kein Speicher im laufenden Bild |
| `Wandnaehe_im_Parcours_senkt_die_Waffe` | vor Säule 1 senkt sich die Waffe (`lowered`), im Freien zurück zur Hüfte |
| `Szene_startet_und_spielt_den_Ablauf` | Szene lädt, Viewmodel-Ebene, Vorführablauf feuert, lädt leer nach, betrachtet |

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
