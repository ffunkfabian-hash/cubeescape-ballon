# CHANGELOG

## 0.6.0 „Riflekin“ – unveröffentlicht (lokal, in Arbeit)

- BASIC-02 Impulsgewehr im Stil v2.1 (geschlossene Impulskammer, Spulenfenster, Salvenanzeigen, Holo-Visier, S2 mit Daumenloch).
- Familienbausteine `grip_v21`, `reflex_sight_v21`, `reticle`, `cut_box`, `screws`, `mirror`; Absehen auch im Pilot.
- `./check` prüft die v2.1-Familie; Familienseite `make_sheets.py --family`; Stilhandbuch §7 Dokumentationspflicht.
- Absehen-Katalog `basic/reticles.py` (7 Formen, 5 Farben, 3 Stärken, 6 Glasvarianten, Aufgehen, Vorgaben, Optionen), Export `data/reticles.json`/`docs/absehen.md`, Katalogblatt und Aufgeh-Clip.
- BASIC-03 Scoutgewehr v2.1 mit Zielfernrohr `scope_v21`; Formskizze per Blender-MCP.
- Visier-Standard v2 nach Destiny-Video und Motiongen: schlanke Visiere, Zielfernrohr mit Linsenbild und `ads_hide`, Augenpunkt 90 mm vor der Öffnung, Modell ungezoomt, Weltzoom je Klasse; Prüfung in `./check`, Beispiele `tools/sight_examples.py`.

## 0.7.0 „Truecolor“ – unveröffentlicht (lokal)

- Unity folgt Blender so nah wie möglich (dauerhafte Regel in AGENTS.md):
  - Material aus `kit.aaa_nodes` in Atlanten gebacken (`tools/bake_unity.py`): Farbe mit Abrieb und Schmutz, Metall und
    Glätte, Normale, AO.
  - Blender-AgX als 3D-LUT im Vollbild-Durchgang, HDR an.
  - Studiolicht und Hintergrund wie `setup_aaa`.
- Vergleich mit Kennzahl (`unity_run.py compare`): SSIM 0,94–0,95 → 0,95–0,97, PSNR +3–5 dB. Leistungsmessung
  (`unity_run.py bench`). Bericht [docs/versions/0.7-truecolor.md](docs/versions/0.7-truecolor.md).

## 0.4.0 „Firstfeel“ – unveröffentlicht (lokal)

- Eigenes Unity-6-Projekt `unity/` (URP, Input System): Pilotwaffe BASIC-01 v2.1 mit Roboterarmen v3 spielbar aus der Ego-Perspektive im grauen Testparcours (Zielscheiben 10/25/50 m); macOS-Entwicklungsbuild.
- `tools/export_unity.py` (FBX + `ego.json` im Format `ballon-ego/1` + Blender-Referenz), `tools/unity_run.py` (Einrichten, Tests, Build, Aufnahme, Vergleich); `./check` prüft, ob `ego.json` aktuell ist.
- Ego-Laufzeit in C# aus denselben Daten und Formeln wie `tools/ego_build.py` (Bewegung v2), live mit Rückstoßfeder, Feder-Nachlauf, Pendeln, Wippen, Atmen; 8 EditMode- und 11 PlayMode-Tests. Doku [docs/unity.md](docs/unity.md), Bericht [docs/versions/0.4-firstfeel.md](docs/versions/0.4-firstfeel.md).

## 0.3.0-ego „Handshake“ – unveröffentlicht (lokal)

- Eigenes Roboterarm-Rig (`basic/arms/robot_arm.py`) und Ego-Daten (`basic/arms/ego.py`): 10 Haltungen, 4 Griffe, 19 Aktionen inkl. Übergänge; getrennt von Toolgen/Cube Escape.
- `tools/ego_build.py` (Szene, Arm-Lösung, Render), `tools/make_ego.py` (Clips, Kontaktbögen, Doku `docs/ego.md`, Ergebnisseite, Prüfung in `./check`).
- Arm v3 nach Nutzerbildern (gewölbte Schale, Medaillon-Ellbogen, Drehgelenk, vier Finger, +15 %); Formen `hull`/`plate`/`prism`; `tools/arm_preview.py`; Spaßfigur `robot_figure.py` + `tools/robot_build.py`.
- Bewegungsgefühl: Hermite-Kurven statt Stopp je Schlüssel, Feder-Nachlauf der Waffe, Atmen in jeder Aktion, Rückstoßfeder, Tempo 1,25, volle 30 fps, Nachladen neu choreografiert.
- Stilhandbuch › Arme und Animation; Bericht [docs/versions/0.3-ego.md](docs/versions/0.3-ego.md).

## 0.2.0-pilot „Inspect“ – unveröffentlicht (lokal)

- Pilot Stil v2 (Destiny-Detaildichte + AAA-Material, schlicht): `basic/pilot/w01_auto_rifle_v2.py`, Ausgabe `BASIC-01-v2`; Reihe unverändert.
- Baukasten: Durchbrüche (Exact-Boolean), `multi`, `tube`, `text`, AAA-Shader (Abrieb, Schmutz, Kratzer, Stippling), Skins (8 Farb-/Texturvarianten), Render `--aaa`, `--skins`, Perspektive `hero_p`, Bloom standardmäßig aus.
- [Stil- und Bauhandbuch](docs/stilhandbuch.md) für künftige Varianten; Bericht [docs/versions/0.2-pilot.md](docs/versions/0.2-pilot.md).
- v2.1: Magazintrichter, ergonomischer Griff, gekrümmtes Magazin, verjüngte Visierhaube und Handschutz; Hintergrund grau als Standard (`--bg mid`); dezenter Abrieb an dunklen Teilen.

## 0.1.0 „First Light“ – unveröffentlicht (lokal)

- Neues Projekt für die Waffenreihe BASIC (Entscheidung des Nutzers 24.10.2026), Begründung und Schnittstellen in [docs/PROJEKT.md](docs/PROJEKT.md).
- Blender-Baukasten (`basic/kit.py`, `basic/common.py`) und 17 BASIC-Entwürfe (`basic/weapons/`), je Waffe Hierarchie Waffe → Baugruppe → Bauteil, Anker, Bewegungen.
- Gemessene Specs `data/specs/` (Format `cubeescape-ballon/basic-spec` v1), Designvertrag, Abdeckungs- und Haltungsmatrix, Bauteilblätter, Quellen- und Erweiterungsverzeichnis.
- Werkzeuge: Bau, Blätter, Clips, Kontaktbögen, Doku, `./check`. Bericht [docs/versions/0.1.md](docs/versions/0.1.md).
