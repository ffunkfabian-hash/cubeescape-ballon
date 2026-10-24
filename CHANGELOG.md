# CHANGELOG

## 0.5.0-teardown „Teardown“ – unveröffentlicht (lokal)

- BASIC-Roboter als eigenständiges Modell `basic/robot/`, zerlegt in Kopf, Arme, Oberkörper, Unterkörper, Beine mit Ankern `Socket_Neck`, `Socket_Shoulder_L/R`, `Socket_Waist`, `Socket_Hip_L/R`; Arme an den Ego-Arm gekoppelt (Nutzerentscheidung); löst `basic/arms/robot_figure.py` ab.
- `tools/robot_build.py`: Haltungen `ready`/`idle`, Explosionsansicht, Einzelblätter je Baugruppe, Kontaktbogen, Ankerprüfung (`--check`, in `./check`), Spec `data/robot.spec.json`; `tools/robot_doc.py` erzeugt [docs/roboter.md](docs/roboter.md).
- Form nach Nutzerkritik („viel zu kantig“ = klotzig) und Konzeptbild: schlanker, lange Beine, schmale Taille, Trapezbrust mit Sensor, Fasen statt runder Blöcke; danach Abgleich mit dem Konzeptbild (kleiner Kopf auf langem Hals, kastige Schulterpanzer, hohes Knie, Kabel und Hydraulik, Gebrauchsspuren, Licht warm/kühl); Bericht [docs/versions/0.5-teardown.md](docs/versions/0.5-teardown.md).

## 0.3.0-ego „Handshake“ – unveröffentlicht (lokal)

- Eigenes Roboterarm-Rig (`basic/arms/robot_arm.py`) und Ego-Daten (`basic/arms/ego.py`): 10 Haltungen, 4 Griffe, 19 Aktionen inkl. Übergänge; getrennt von Toolgen/Cube Escape.
- `tools/ego_build.py` (Szene, Arm-Lösung, Render), `tools/make_ego.py` (Clips, Kontaktbögen, Doku `docs/ego.md`, Ergebnisseite, Prüfung in `./check`).
- Arm v3 nach Nutzerbildern (gewölbte Schale, Medaillon-Ellbogen, Drehgelenk, vier Finger, +15 %); Formen `hull`/`plate`/`prism`; `tools/arm_preview.py`; Spaßfigur `robot_figure.py` + `tools/robot_build.py`.
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
