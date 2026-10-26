# CHANGELOG

## 0.11.0 „Compact“ – in Arbeit (Branch `claude/ballon-0.11-compact`)

- BASIC-06 Maschinenpistole im Stil v2.1: Kastenvorbau, Abzugsbügel und Bügel als ein Band, Magazin auf der Griffachse mit
  Sichtfenster, Holo mit Absehen `dot`; drei Sichtungsrunden, 8 Skins, Bewegung gesichtet.
- Namen geklärt (Nutzerwahl (a)): Stil v2.1 = Waffenstil, Visier-Standard 3 = Visierregeln (früher „Visier-Designsprache v3“), kein Waffenstil v3.
  Bericht [docs/versions/0.11-compact.md](docs/versions/0.11-compact.md).
- Patch: Familienmaße v2.1 aus den Specs ([docs/familienmasse.md](docs/familienmasse.md), `make_docs.py`); v2.1-Specs in `data/specs/`,
  `./check` vergleicht sie mit dem Entwurf. Stilhandbuch §6: alle Familienbausteine mit Parametern und Nutzung, Muster im Waffenmodul.
- Patch: Entscheidungsliste Motiongen REF 0.14–0.28 ([docs/entscheidungsliste-motiongen.md](docs/entscheidungsliste-motiongen.md)):
  20 Nutzerantworten vom 25.10.2026 in 8 Blöcken, acht Glidepath-Widersprüche mit dem Wert, den BASIC bis zur Klärung nutzt,
  und eine Umsetzungsreihenfolge in 8 Schritten. Nichts gebaut oder gerendert.
- Patch: Messungen zu Schritt 2 der Entscheidungsliste (Hüftlage, Scout-Ring, Sprint-Hub, Zoom gegen Modell) in
  [docs/entscheidungsliste-motiongen.md](docs/entscheidungsliste-motiongen.md) › Messungen und `data/review.json`; nur gemessen, kein Wert geändert.
  Werkzeuge `tools/messen.py`, `tools/messen_bild.py`; Unity-Aufnahme mit `-ballonFps` und `-ballonKey` (nur Messhilfe).
- Patch: Unity-Abgleich (Entscheidungsliste Schritt 1): Kadenz 720/min wie `fire_hip`, Pendeln kritisch gedämpft (Rückkehr 0,30 s,
  kein Überschwingen), Schuss-Ring und Treffer-X in Orange nach Visier-Standard 3 §6 (ohne HUD-Punkt), Test Nachlade-Abbruch vor/nach
  `MagIn`, Herkunft `inspect` „Apex/CoD-Muster“. Vier neue PlayMode-Tests; Belege `unity_run.py sway|treffer`.

## 0.6.0 „Riflekin“ – unveröffentlicht (lokal, in Arbeit)

- Visier-Designsprache v3 nach Motiongen REF 0.14 „Eyebox“: Typ je Klasse, dünne Rahmen, kleinere Öffnungen (geprüft), Trapezsockel/-hals, eine Kamera, Absehen fein ohne Aufgehen im Zielen, Glasspuren nur am Rand.

- BASIC-02 Impulsgewehr im Stil v2.1 (geschlossene Impulskammer, Spulenfenster, Salvenanzeigen, Holo-Visier, S2 mit Daumenloch).
- Familienbausteine `grip_v21`, `reflex_sight_v21`, `reticle`, `cut_box`, `screws`, `mirror`; Absehen auch im Pilot.
- `./check` prüft die v2.1-Familie; Familienseite `make_sheets.py --family`; Stilhandbuch §7 Dokumentationspflicht.
- Absehen-Katalog `basic/reticles.py` (7 Formen, 5 Farben, 3 Stärken, 6 Glasvarianten, Aufgehen, Vorgaben, Optionen), Export `data/reticles.json`/`docs/absehen.md`, Katalogblatt und Aufgeh-Clip.
- BASIC-03 Scoutgewehr v2.1 mit Zielfernrohr `scope_v21`; Formskizze per Blender-MCP.
- Visier-Standard v2 nach Destiny-Video und Motiongen: schlanke Visiere, Zielfernrohr mit Linsenbild und `ads_hide`, Augenpunkt 90 mm vor der Öffnung, Modell ungezoomt, Weltzoom je Klasse; Prüfung in `./check`, Beispiele `tools/sight_examples.py`.

## 0.10.0 „Stride“ – in Arbeit (Branch `claude/ballon-0.10-stride`, öffentliches Repo)

- Sprint-Wippen wie in Destiny 2 gemessen (Motiongen REF 0.23): 3,16 statt 6 Schritte/s, U-Bogen, Rollen ±3,5°. Das Zielen endet ohne Überschwingen (0.9: 3,3° über die Mitte), mit eigener schneller,
  kritisch gedämpfter Feder; Format `ballon-ego/4`. Das ständige Fadenkreuz ist entfernt, nur Treffer zeigen kurz eine Marke.
- Datenexport ohne Backen (`BALLON_EXPORT_DATA_ONLY=1`, 2 s, `ce lock blender`). Beleg `unity_run.py feel`. Übergabe an Motiongen
  je Waffentyp. Bericht [docs/versions/0.10-stride.md](docs/versions/0.10-stride.md).

## 0.9.0 „Parcours“ – unveröffentlicht (lokal)

- Hangar mit Detail wie die Waffe (Fasen, Trapezblech, Nieten, Fugen, Schilder, Abrieb, Schmutz; 68 946 Dreiecke), Zonen-Atlanten
  bis 1,23 cm je Texel, vier Lichtszenen Tag/Abend/Nacht/Bewölkt (Taste N). Format `ballon-scene/2`.
- Parcours mit 151 m Strecke, 5 Kontrollpunkten, 14 Zielscheiben, Richtzeit 45 s und Bestzeit; Taste T zurück zum Start.
- Vorführlauf (`RouteRunner`): MP4 `unity_run.py course`, Leistung `bench hangar`, Test „Vorführlauf schafft jeden Parcours“.
  Bericht [docs/versions/0.9-parcours.md](docs/versions/0.9-parcours.md).

## 0.8.0 „Hangar“ – unveröffentlicht (lokal)

- Hintergrundszene Hangar aus Python-Daten (`basic/scenes/hangar.py`), in Blender gebaut mit gebackenem Cycles-Licht
  (`tools/scene_build.py`). Format `ballon-scene/1` ([docs/szenen-format.md](docs/szenen-format.md)).
- Unity: Szenenlader, Taste L (Parcours ↔ Hangar), Viewmodel-Licht aus denselben Daten. Vergleich vom Startpunkt: SSIM 0,885,
  PSNR 26,0 dB.
- Fix: AO beim Backen der Waffe war zu dunkel (Originale unter der zusammengefügten Kopie). Gebaut mit zwei Unteragenten;
  Bericht [docs/versions/0.8-hangar.md](docs/versions/0.8-hangar.md).

## 0.7.2 – unveröffentlicht (lokal)

- Acht Waffen-Skins aus `kit.SKINS` gebacken (Farbe und Glanz je Skin, Normale und AO geteilt). In Unity schaltet Taste K
  durch; Kontaktbogen über `unity_run.py skins`. Doku: Grenzen und Entscheidung „Restabweichungen bleiben“.

## 0.7.1 – unveröffentlicht (lokal)

- Spezular-Modus mit gebackener Spiegelfarbe (Polymer wieder mattschwarz). Armsegmente werden zum Backen auseinandergelegt (keine
  schwarzen Streifen am Handrücken), Abrieb mit 64 Samples. Über Waffe und Arme Abweichung −25 bis −40 % gegenüber 0.7.

## 0.7.0 „Truecolor“ – unveröffentlicht (lokal)

- Unity folgt Blender so nah wie möglich (dauerhafte Regel in AGENTS.md):
  - Material aus `kit.aaa_nodes` in Atlanten gebacken (`tools/bake_unity.py`): Farbe mit Abrieb und Schmutz, Metall und
    Glätte, Normale, AO.
  - Blender-AgX als 3D-LUT im Vollbild-Durchgang, HDR an.
  - Studiolicht und Hintergrund wie `setup_aaa`.
- Vergleich mit Kennzahl über Waffe und Arme (`unity_run.py compare`, Maske): Abweichung −14 bis −31 %, SSIM im Ausschnitt
  0,74–0,81 → 0,78–0,85. Ganzes Bild PSNR +3–5 dB. Leistungsmessung
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
