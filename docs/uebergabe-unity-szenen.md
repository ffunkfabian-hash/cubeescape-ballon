# Übergabe: Hintergrundszenen mit eigenem Licht (0.8 „Hangar“)

Stand 25.10.2026, aus der Sitzung BALLON 0.4 „Firstfeel“ · Mac (dieselbe Sitzung baute auch 0.7–0.7.2). Geschrieben für eine
**frische Sitzung ohne Verlauf** (Claude, Codex oder Antigravity).

Opus 5.5 `high`, Grund: Gestaltung (neue Formen, Licht) und Pipeline-Erweiterung.

## Auftrag des Nutzers

> „Es wäre mal cool verschiedene Szenen im Hintergrund mit verschiedenen Lichtern zu haben.“ –
> „Aber auch verschiedene Hintergrundszene wie z.B. Hangar oder so.“ – „Arbeite nach belieben.“ –
> „Du darfst Blender MCP nutzen. Wir können gerne auch Aufgaben an Antigravity oder Codex abgeben.“

- **Ziel:** In der Unity-Build lassen sich Hintergrundszenen mit eigenem Licht umschalten (Taste L): Parcours (heute) und
  Hangar. Danach nach Eindruck des Nutzers Landeplattform (Abendsonne), Industriekorridor (Neon) und Nachtstraße. Waffe und Arme
  bekommen Licht und Spiegelungen aus der jeweiligen Szene.
- **Grundsatz** ([AGENTS.md](../AGENTS.md)): Unity folgt Blender so nah wie möglich, Blender bleibt die Quelle.
  - Szenen entstehen als Python-Daten, Blender baut sie und backt das komplette Cycles-Licht (direkt und indirekt) in Texturen
    der Umgebung. Weil die Umgebung statisch ist, ist das fast 1:1.
  - Unity zeigt die Umgebung mit den gebackenen Texturen (unbeleuchtet) und beleuchtet nur das Viewmodel live, mit Lichtern
    aus denselben Daten.
- **Dateien/Zuständigkeit:**
  - Neu: `basic/scenes/<szene>.py` (Daten: Maße, Bauteile, Materialien, Lichter, Startpunkt), `tools/scene_build.py`
    (Blender: Bau, UV, Licht backen, FBX, `scene_<name>.json`), Unity: Laden und Umschalten in `Bootstrap`/`Range`.
  - Doku: Abschnitt „Szenen“ in `docs/unity.md`. Bericht `docs/versions/0.8-hangar.md`.
  - Nur lesen: `basic/kit.py` (Materialien, AAA-Knoten), `tools/blender_build.py` (Licht, `BACKDROPS`).
  - Nicht anfassen: Waffen und Visiere (`basic/common.py`, die Hauptsitzung arbeitet daran), `basic/robot/`.
- **Prüfen:**
  - `./check`, Unity-Tests: Szene lädt, Kollisionen, Umschalten, Startpunkt frei, kein GC-Müll beim Umschalten nach dem
    ersten Mal.
  - Vergleich: Blender-Render der Umgebung vom Startpunkt (gleiche Kamera) gegen Unity, mit `unity_run.py compare`-Kennzahl.
  - Leistung (`unity_run.py bench`) je Szene ≤ 16,7 ms.
- **Fertig wenn:**
  - Hangar spielbar und umschaltbar.
  - Vergleichsbild Blender gegen Unity vom Startpunkt.
  - Ein MP4 des Umschaltens.
  - Tests grün, Bericht steht.
- **Release:** nein. Codex-Richter vor dem Merge (`ce judge --repo <worktree> --base claude/basic-first-light --files
  <Quellen>`).

## Weg (empfohlen)

1. **Formen skizzieren** im Blender-MCP in eigener Szene, speichern nur mit `wm.save_as_mainfile`. Quelle bleibt der
   Generator.
   - Hangar etwa 40 × 60 × 14 m.
   - Stahlfachwerk unter dem Dach, Wellblechwände, eine offene Torseite mit Tageslicht und Himmel.
   - Deckenstrahler in zwei Reihen, Bodenmarkierungen, Kisten, Fässer, Regale, ein Wartungsgerüst mit Treppe (Springen und
     Ducken testen).
   - Zielscheiben wie im Parcours (10/25/50 m).
2. **Daten** `basic/scenes/hangar.py` im Stil der Waffenmodule:
   - Bauteile als Formen (`box`, `cyl`, `prof`) mit Materialrolle.
   - Neue Umgebungsrollen (Beton, Lackstahl, Wellblech, Gummi, Warnstreifen) in einem eigenen Rollenverzeichnis der Szene;
     `kit.MATERIALS` bleibt unberührt.
   - Lichter als Daten: Art, Lage, Leistung W, Größe, Farbe. Dazu Himmel (Farbe/Stärke) und Startpunkt.
3. **Blender** `tools/scene_build.py` (unter `ce lock gpu`, mit `BALLON_BAKE_GPU=1`):
   - Bauen und Lightmap-UVs vergeben (Smart UV, ein Atlas je Szene, 4096²).
   - Die Diffusbeleuchtung samt Farbe backen (`DIFFUSE` mit direct + indirect + color, oder `COMBINED` ohne Glanz).
   - Zusätzlich die Umgebung als Cubemap aus der Spielerposition für Spiegelungen des Viewmodels.
   - Ausgabe: FBX, Atlas, `scene_hangar.json` mit Lichtern, Startpunkt, Kollisionsquadern und Quellen-SHA-256.
   - Vergleichsrender vom Startpunkt (75° horizontal, AgX wie `setup_aaa`).
   - Lehre aus 0.7: Teile, die sich beim Backen überlagern, verfälschen AO und Abrieb, also nicht überlagert backen. Teile
     mit gleichem Objektraum zu einer Kopie zusammenfügen (Backen sonst je Objekt über den ganzen Atlas).
4. **Unity:**
   - Szenen-Datei laden: Umgebung unbeleuchtet mit Atlas, MeshCollider.
   - Lichter fürs Viewmodel aus den Daten: Spots ohne Echtzeitschatten, Lichtflächen in der Reflexionssonde wie im
     Studiomodus (`Bootstrap.StudioLike`). Umgebungslicht, Nebel.
   - Taste L schaltet um, die Anzeige nennt die Szene, der Spieler springt zum Startpunkt.
   - Farben als `SetColor(farbe.gamma)` setzen (Materialfarben sind Gamma-Werte), in ein HDR-Ziel rendern (`HdrTarget`). Beides
     Lehren aus 0.7.
5. **Aufteilen mit Unteragenten** (Nutzer: „Es sollten auch Unteragenten genutzt werden“; Codex und Antigravity erlaubt).
   Die koordinierende Sitzung hält ihren Verlauf kurz und prüft jedes Ergebnis selbst.

   | Teil | Wer | Modell |
   |---|---|---|
   | Szene in Blender: Daten, Skizze per MCP, Backen, FBX, Vergleichsrender | Unteragent mit `isolation: worktree` | Opus `high` |
   | Weitere Szenen (Landeplattform, Korridor, Nachtstraße) | je ein Unteragent, Codex oder Antigravity | |
   | Unity: Laden, Taste L, Viewmodel-Licht, Tests | koordinierende Sitzung | |
   | Belege (Vergleichsbild, MP4) | `ce-recorder` | Sonnet |
   | Suche in Schwester-Repos (wie dort Szenen und Licht gebaut sind) | `ce-searcher` | Haiku |
   | Prüfung vor dem Merge | Codex-Richter (`ce judge`), sonst `ce-judge` | Opus |

   Bilder, Blender und Unity laufen nur auf dem Mac, nicht in der Cloud. Schwere Läufe gehen immer über die Sperren; zwei
   Unteragenten teilen sich die GPU nacheinander.

## Ausgangslage

- Branch von `claude/basic-first-light` (dort sind 0.4 bis 0.7.2 gemergt).
- Ablauf und Befehle: [unity.md](unity.md).
- Sperren: `ce lock unity|blender|gpu`, Skriptpfade absolut (`ce lock` wechselt das Verzeichnis).
- Belege unter `~/Library/Caches/CubeEscapeBallon/unity/`.
- Offene Nutzerfrage: Downloads freier CC0-Texturen oder -Modelle (ambientCG, Poly Haven). Ohne ausdrückliches Ja alles selbst
  generieren.
- Lehren in [LESSONS.md](LESSONS.md); die URP-Fallen stehen dort: HDR-Ziel, Gamma-Farben, `WaitForEndOfFrame` im
  Stapelbetrieb.
