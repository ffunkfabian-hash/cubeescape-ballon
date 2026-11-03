# Formgen-Varianten in BALLON (ab 0.41 „Intake“)

Vertrag zwischen Formgen v2 (Varianten der 17 BASIC-Typen, Blätter `B<Linie><NN>`) und BALLON: welche Schnittstellen BALLONs Baukasten
anbietet und wie ein Formgen-Paket in Unity spielbar wird. Grundlage: Nutzerentscheid 242 (02.11.2026), Formgen
`docs/vorschlag-ballon-asset.md` (Punkte 1–9, Tabelle a–f). Formgen ändert BALLON nicht; BALLON ändert Formgen-Pakete nicht.

## 1. Schnittstellen im Baukasten (Python)

| Schnittstelle | Ort | Wofür |
|---|---|---|
| `as_module(data, base=None, name=None)` | `basic/variant.py` | Datensatz (dict mit `META`, `PARTS`, `ASSEMBLIES`, `ANCHORS`, `POINTS`, `ACTIONS` …) über einem Grundmodul (Modul oder Name wie `pilot.w01_auto_rifle_v21`) → Waffenmodul. Fehlende Felder kommen vom Grundmodul (`EJECT`, `EGO_GRIPS`, `EGO_LIVE`, Rollenmodule). Ersetzt das Einhängen von `basic.weapons.formgen_<ID>` in `sys.modules`. |
| `blender_build.main(W=…, base=…, argv=[…])` | `tools/blender_build.py` | Bauen ohne Modulnamen: `W` = Modul oder Datensatz, `argv` = Optionen wie nach `--` (`--views`, `--aaa` …). Der Aufruf über `sys.argv` bleibt gültig. GLB und Spec sind bytegleich zum Weg über den Modulnamen (16 Spielwaffen, BD01/BG01 gegen Formgens Paket-GLB). |
| `export_unity.weapon_entry(W, atlas_key=None, spec=None, weapon=None)` | `tools/export_unity.py` | Eintrag von `ego.json › weapons[]` für ein fremdes Modul ohne Eintrag in `WEAPONS`: Klassenprofil (Haltungen, Griffe, Aktionen, Gameplay, Wirkung) aus `ego.profile`, `atlas_key` als Atlasname, `spec` = Spec der Variante (Ladeleuchten). |
| `export_unity.weapon_data(W, live)` | dto. | `weapon`-Block (Teile, Anker, Auswurf, Live-Teile); löst `POINTS` auf. |
| `export_unity.bake_weapon(root, tex_dir, atlas_key, fbx=None, skins=False, gpu=False, arms=False, objs=None, rest=None, size=4096, samples=None)` | dto. | Atlas (+ Skins) und FBX **ohne Ego-Szene** und mit Zielordner. `skins`: `False` (nur Standard), `True` (alle `kit.SKINS`) oder Liste. `arms`: andere Netze der Szene beim Backen sichtbar lassen (siehe 3). Die Szene bereitet der Aufrufer vor (`kit.build`, `blender_build.setup_render(…, aaa=True, bg='mid')`, `kit.set_mode`). Ablage nach `TEXTURE_STORE` danach mit `store_textures`. |
| `export_unity.parts_sha(W)` | dto. | Bauteil-Hash (Manifest `ballon.parts_sha256`). |

## 2. Weltpunkte mit Teilbezug (`POINTS`)

Hülsenauswurf (`EJECT at`), Gurtgliederauswurf (`EJECT links at`) und alle Handkontakte der Ego-Griffe (`EGO_GRIPS` bzw. `ego.GRIPS`
`contact`) stehen in jedem Spielmodul zusätzlich als `POINTS` in derselben Form wie `ANCHORS`: `{name: dict(at=(f, u, x) mm, part=Teil-ID)}`.
Namen: `eject`, `eject.links`, `grip.<Griff>` (z. B. `grip.support`, `grip.mag`). Das Modul schreibt sie mit
`POINTS = collect(EJECT, EGO_GRIPS, dict(eject=…, grip=…, support=…))`; ein Griff mit eigenem `part` nimmt dieses Teil.

**Regel für Generatoren:** `POINTS` genau wie `ANCHORS` behandeln – beim Dehnen/Stauchen (Teil verschoben → Punkt verschoben; Teil
gedehnt → Punkt hinter dem Schnitt verschoben), beim Spiegeln und beim Tauschen von Teilen (Punkt eines entfernten Teils an das neue Teil
setzen oder melden). BALLON übernimmt die Punkte beim Bauen (`as_module` → `variant.resolve`) in `EJECT`/`EGO_GRIPS`; die Bewegung im
Spiel steuern weiter die Felder (`part` eines Griffs: folgt dem Teil; `part` von `EJECT`: Start im Teil). Mündungsfeuer und Ladeleuchten
hängen schon an `Socket_Muzzle` (Anker) und wandern mit. Beleg: `tools/test_points.py` (16 Waffen, zwei Schnitte je Waffe, 56 Punkte
mitgewandert; Gegenprobe mit den alten Modulfeldern ohne `POINTS`: alle 56 falsch).

## 3. Handschatten im Waffenatlas – Regel für beide Wege

Formgen fand in BALLONs Waffen-AO handförmige Verschattungen. Ursache: `export_unity.rest_pose` legt vor dem Backen **alle Armsegmente
in den Ursprung (Socket_Hand)**, also mitten in den Griff – das ist keine Griffhaltung, sondern ein Back-Fehler; die Abdrücke liegen auch
an Stellen, die in anderen Haltungen frei sind. **Regel ab 0.41: der Waffenatlas wird ohne Arme gebacken** (`bake_weapon(arms=False)`,
`ARMS_IN_ATLAS = False`), BALLON wie Formgen. Kontaktschatten der Hände entstehen im Bild (Cycles), in Unity nicht gebacken. BALLONs 16
vorhandene Atlanten bleiben, bis sie wieder voll gebacken werden (`export_plan` übernimmt sie, solange die Form gleich ist); `arms=True`
backt wie bis 0.40.

## 4. Paket und Ordner in Unity

Formgen entpackt ein Bake-Paket direkt nach `unity/Assets/Ballon/Generated/Formgen/<ID>/`
(`python -m formgen.asset --bake <IDs> --unpack <BALLON>/unity/Assets/Ballon/Generated/Formgen`):

```
Generated/Formgen/<ID>/<ID>.package.json   formgenv2/weapon-package, format_version 1 (0.6) oder 2 (mit model)
Generated/Formgen/<ID>/<ID>.fbx            FBX wie export_unity.export_fbx (Wurzel = META id, Teile, Anker)
Generated/Formgen/<ID>/textures/<ID>_albedo.jpg, _spec.png, _normal.png, _ao.png   nach TEXTURE_STORE
Generated/Formgen/<ID>/<ID>.spec.json, <ID>.glb
```

Einlesen: `python3 tools/export_unity.py --formgen` (ohne Blender; nur wenn BALLONs eigener Teil von `ego.json` aktuell ist) oder der
nächste volle Export. `tools/formgen_import.py` prüft das Paket (Format, ID = Ordner, FBX/Spec/Texturen vorhanden, Grundmodul = Manifest)
und baut den Eintrag:

- **Paket 2 mit `model`** (Vorschlag an Formgen, ab jetzt gültig): `model` = Datensatz der Variante wie `formgen.asset.kit_model` plus
  `POINTS`. BALLON baut die Waffe mit `as_module(model, Grundmodul)` und rechnet den Eintrag mit seinem heutigen Code; der Bauteil-Hash muss
  zu `ballon.parts_sha256` passen.
- **Paket 1 ohne `model`** (Formgen 0.6): `weapon`-Block aus dem Manifest, Weltpunkte der Grundform. Das gilt nur, wenn die Teile aller
  Weltpunkte in der Variante dieselben Netzgrenzen haben wie in der Grundform (Spec gegen `data/specs`); sonst wird das Paket abgelehnt.
  BD01 und BG01 bestehen das (Schnitte bei f ≈ 475 mm, Auswurf f = 53 mm).

Eintrag in `ego.json` (Format `ballon-ego/11`, nur additiv): hinter BALLONs 16 Waffen, sortiert nach ID; `dir = Formgen/<ID>` (Pfade von
FBX und Texturen relativ dazu), `origin` (Herkunft: Paket, Grundtyp, Skin, Weltpunkte, Bake), `reference` leer (keine Blender-Referenz),
`atlas = formgen_<ID>`, Skin der Linie als `standard`. Haltungen, Griffe, Aktionen und Gameplay sind vom BALLON-Grundtyp geerbt (Tabelle f:
vorerst). Unity (`BallonSetup`) legt Material `Atlas_formgen_<ID>`, Knotenlagen aus `ego.json`, das Symbol `Icons/<ID>.png` (aus dem FBX
gerastert, Seitenansicht wie `tools/make_icons.py`) und den Platz in der Waffenauswahl (Menü, ab 17) an.

## 5. Offen

- **Tabelle e:** Piloten für BASIC-16/17 (Schwert, Glefe) – ohne Pilot bleibt dort die Formstudie; kein Ego-Profil, kein Paket-Eintrag.
- **Tabelle f:** Gameplay je Variante – vorerst geerbt; Felder im Datensatz wären der nächste Schritt (dann neues Format).
- Formgen 0.6 bewegt `POINTS` noch nicht und liefert kein `model`; bis dahin nur Varianten, deren Weltpunkt-Teile unverändert sind.
- Blender-Referenz (`ego_reference_*.json`) und Clips je Variante gibt es nicht; die Haltungen sind die des Grundtyps.
