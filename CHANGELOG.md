# CHANGELOG

## 0.6.0 „Riflekin“ – unveröffentlicht (lokal, in Arbeit)

- BASIC-02 Impulsgewehr im Stil v2.1 (geschlossene Impulskammer, Spulenfenster, Salvenanzeigen, Holo-Visier, S2 mit Daumenloch).
- Familienbausteine `grip_v21`, `reflex_sight_v21`, `reticle`, `cut_box`, `screws`, `mirror`; Absehen auch im Pilot.
- `./check` prüft die v2.1-Familie; Familienseite `make_sheets.py --family`; Stilhandbuch §7 Dokumentationspflicht.
- Absehen-Katalog `basic/reticles.py` (7 Formen, 5 Farben, 3 Stärken, 6 Glasvarianten, Aufgehen, Vorgaben, Optionen), Export `data/reticles.json`/`docs/absehen.md`, Katalogblatt und Aufgeh-Clip.
- BASIC-03 Scoutgewehr v2.1 mit Zielfernrohr `scope_v21`; Formskizze per Blender-MCP.
- Visier-Standard v2 nach Destiny-Video und Motiongen: schlanke Visiere, Zielfernrohr mit Linsenbild und `ads_hide`, Augenpunkt 90 mm vor der Öffnung, Modell ungezoomt, Weltzoom je Klasse; Prüfung in `./check`, Beispiele `tools/sight_examples.py`.

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
