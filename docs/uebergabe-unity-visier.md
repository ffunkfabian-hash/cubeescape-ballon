# Übergabe: Absehen und Visier-Standard v2 in Unity (nach 0.4 „Firstfeel“)

Stand 24.10.2026, aus der Sitzung BALLON 0.4 „Firstfeel“ · Mac. Geschrieben für eine **frische Sitzung ohne Verlauf**.
Opus 5.5 `high`, Grund: Spielgefühl und Darstellung (Shader, Kameras).

## Auftrag (Nutzerwünsche, weitergereicht von der BASIC-Hauptsitzung)

- In den Visieren fehlt eine Zielhilfe. Gewünscht:
  - verschiedene Absehen, „einfach nur ein Punkt“;
  - Farben und Linienstärken für alle Formen;
  - Aufgehen beim Schießen „wie man das von Shootern kennt“;
  - Muster später einstellbar;
  - Glas dezent mit Staub, Kratzern oder Riss.
- Die Visiere sind „sehr klobig“. Der Visier-Standard v2 macht sie schlanker (Destiny-Video zum Scout, Motiongen-Messungen in
  `cubeescape-reference/docs/destiny2.md`).

## Voraussetzung

Erfüllt: Die Daten sind seit `cd27a66` und `8205514` (Augenpunkt 90 mm, Zielbereiche 18–26 % bzw. 26–34 %) auf
`claude/basic-first-light` committet, und 0.4 ist dorthin gemergt. Die Designsprache der Visiere ist noch offen (Analyse
„Visiere in Videospielen“): an den Visierformen nichts Endgültiges bauen; Absehen, Aufgehen, Weltzoom und Linsenbild sind
davon unabhängig.
Die Arbeit beginnt von `claude/basic-first-light`. Modelle und Unity-Daten sind beim Merge schon neu exportiert (72 Teile,
Visier v2 mit `sight_reticle`). Ändert die Hauptsitzung danach die Visierformen in `basic/common.py`, meldet `./check`
„ego.json veraltet“; dann erneut exportieren.

Quellen der Daten (nur lesen):

- `basic/reticles.py` mit `SHAPES`, Farben, Stärken, Glas, `SPREAD`, `DEFAULTS`, `SETTINGS`, `SIGHT`, `CLASS_ZOOM`,
  `world_zoom()` und `simulate()`;
- `data/reticles.json` (Format `cubeescape-ballon/reticles` v1, erzeugt von `tools/export_reticles.py`);
- Übersicht `docs/absehen.md`;
- `common.reflex_sight_v21`, `common.scope_v21` sowie die Teile `sight_reticle` und `ads_hide`.
- Referenzen:
  - `~/Library/Caches/CubeEscapeBallon/evidence/clips/reticle_spread.mp4`
  - `…/evidence/sight_examples_v2.png`

## Nachtrag 25.10.2026: Visier-Designsprache v3 (geht den Punkten unten vor)

Der Nutzer hat die Empfehlungen aus Motiongen REF 0.14 „Eyebox“ übernommen („Mach alles so wie du empfiehlst“) und den
Augenabstand 90 mm bestätigt. Gegenüber den Punkten unten gilt:

- **Eine Kamera statt Render-Textur:** Das Glas des Zielfernrohrs zeigt dasselbe Weltbild wie außen (kein eigenes Linsenbild,
  kostet Bildrate). Punkt 6 entfällt bis auf `ads_hide` (Rohr, Okular, Okularlinse, Türme ausblenden; der Trapezhals bleibt).
- **Augenpunkt 90 mm** vor der vorderen Öffnung (nicht 110 mm). Zielbereiche: Holo **12–20 %**, Zielfernrohr **20–26 %** der
  Bildbreite bei 75° horizontal (`SIGHT['fov_ref_deg']`). Weltzoom ist ein Bildmaßstab (`SIGHT['zoom_kind']`).
- **Spieleroption Visiernähe** `SETTINGS['ads_eye_relief']` 70/90/110 mm (Nutzer: 70 mm optional): beim Zielen rückt das
  Waffenmodell um (90 − Wert) mm entlang der Visierlinie näher an die Kamera; Standard 90.
- **Kein Aufgehen im Zielen** (`SPREAD[*]['ads'] = 0`): stattdessen `ADS_FEEDBACK` – Leuchtpunkt am Zielpunkt getrennt vom Glas,
  Schuss = kurzer Ring (1 Bild), Treffer = X (≥ 0,17 s). Das Aufgehen gilt nur dem Hüft-Fadenkreuz.
- **Absehen-Standard fein**, Glasspuren nur am Rand (Mitte klar).
- **Visiertyp je Klasse** `SIGHT_KIND` (Pilot: `holo`); neue Visierformen: Holo mit Trapezsockel bis zur Fensterunterkante,
  kurzes Ring-Zielfernrohr auf Trapezhals – Modelle neu exportiert (siehe Commit der Hauptsitzung).
- Referenzbild: `~/Library/Caches/CubeEscapeBallon/evidence/sight_examples.png` (v3, 70/90/110 mm).

## Was zu tun ist

1. **Neu exportieren.** Das Visier ist schlanker und hat jetzt ein Absehen-Teil. `./check` meldet „ego.json veraltet“, sobald
   sich die Quellen ändern (SHA-256 in `ego.json › sources`).
   - Ablauf: Export in Blender, dann `python3 tools/unity_run.py setup && … test` ([unity.md](unity.md)).
   - `reticles.json` nach `unity/Assets/Ballon/Generated/` übernehmen, am besten im Exporter.
2. **Zoom.** In `EgoPlayer.MoveTuning.adsZoom` (heute fest 1,35) kommt `world_zoom` aus den Daten: Klassengrundzoom plus
   Visierbonus, für das Automatikgewehr mit Reflexvisier ×1,9.
   - Nur die Weltkamera zoomt. Die Viewmodel-Kamera bleibt bei 75° horizontal; das ist schon so gebaut.
   - Die Empfindlichkeit im Zielen teilt bereits durch den Zoom.
3. **Visierabsehen.** Ein Glasshader zeichnet das Absehen kollimiert, also im Unendlichen, mit Parallaxe gegen die Glasebene.
   - Er baut es prozedural aus `prims` (`line`, `ring`, `dot`, mm auf der Scheibe), leuchtend in der Farbe, ohne Bloom.
   - Das Modellteil `sight_reticle` dient nur als Rückfall oder wird ausgeblendet, damit nichts doppelt erscheint.
   - Glasvarianten (Staub, Kratzer, Riss) werden dezente Masken auf dem Glas.
   - Heute ist die Rolle `glass` ein einfaches transparentes URP Lit (`BallonSetup.Materials`). Ein Shader-Graph- oder
     HLSL-Shader ersetzt es, damit gehört er zum Projekt `unity/`.
4. **Hüft-Fadenkreuz.** Das heutige HUD-Fadenkreuz in `EgoPlayer.OnGUI` (vier Striche, Lücke aus der Streuung) wird aus
   `DEFAULTS.hip` und `prims` erzeugt.
   - Aufgehen nach `SPREAD`: s ← base(+move) + (s − base)·exp(−dt/recover_s), je Schuss s ← min(max, s + per_shot), im
     Zielen s·ads. Linien wandern um s·d, Ringe wachsen um s·grow, Punkte bleiben stehen.
   - Beim Zielen ausblenden.
   - Ein Unity-Test vergleicht die Reihe mit `reticles.simulate()`.
5. **Einstellungsmenü** für `SETTINGS`: Form, Farbe, Stärke, Größe 0,6–1,6, Deckkraft 0,3–1,0, Mittelpunkt, Aufgehen
   an/aus, Glas. Über eine Taste erreichbar, Werte per Spieler gespeichert (`PlayerPrefs` reicht).
6. **Zielfernrohr** (`common.scope_v21`, falls die Pilotwaffe oder eine zweite Waffe es trägt):
   - Linsenbild als Render-Textur in der Objektivlinse; die Umgebung um den Ring bleibt sichtbar.
   - Teile mit `ads_hide` beim Zielen ausblenden; der Klemmfuß bleibt.
   - `Socket_Eye` liegt 110 mm hinter der vorderen Öffnung (`Socket_Objective`).
7. **Prüfen.**
   - Öffnung am Bildschirm: Reflex/Holo 18–26 %, Zielfernrohr 26–34 % der Bildbreite. Messen im Vergleichsmodus (`compare`);
     als Test aus der projizierten Öffnung.
   - Belege: Standbild ADS je Absehenform, ein MP4 des Aufgehens beim Feuern (Bewegung geändert), Vergleich mit
     `sight_examples_v2.png`.

## Stand in Unity, auf dem aufgebaut wird

- Kameras: `EgoPlayer.Create`, Weltkamera als Basis plus Overlay-Viewmodel-Kamera, Ebene 31 „Viewmodel“.
- Kamerafeedback: `EgoRig.CameraKick`.
- `EgoController.adsWeight` (0…1) treibt Zoom, Streuung und Empfindlichkeit.
- Streuung heute fest: `MoveTuning.spreadHipDeg` 1,1° und `spreadAdsDeg` 0,12°. Die Treffer sollen dem Aufgehen des
  Absehens folgen.
- Materialien je Rolle legt `BallonSetup.Materials` an. Knotenlagen setzt `BallonModelImport` aus `ego.json`; neue Teile
  kommen dabei automatisch mit.
- Tests: `unity/Assets/Ballon/Tests/*`. GC-Freiheit im laufenden Bild wird geprüft (`Kein_GC_Muell_im_laufenden_Bild`). Das
  gilt auch für neue HUD- und Absehen-Pfade.

## Nicht hier

Cube Escape, Toolgen und Robogen nur lesen. `basic/robot/` gehört der Roboter-Sitzung. Unity-Läufe gehen über
`ce lock unity`, Blender über `ce lock blender`. Skriptpfade absolut angeben, weil `ce lock` das Verzeichnis wechselt.
