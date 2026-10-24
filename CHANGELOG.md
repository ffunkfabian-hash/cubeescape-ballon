# CHANGELOG

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
