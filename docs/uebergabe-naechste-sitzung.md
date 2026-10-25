# Übergabe an die nächste BALLON-Unity-Sitzung (Stand 25.10.2026)

Frische Sitzung ohne Verlauf; erst `AGENTS.md`, `docs/LESSONS.md`, `docs/unity.md` und die Versionsberichte 0.8–0.10 lesen.

## Stand

- **Repo:** öffentlich, https://github.com/ffunkfabian-hash/cubeescape-ballon. Standardbranch `claude/basic-first-light` (Stand 0.9 „Parcours“).
  Merges macht Sightline (Postfach cubeescape-nexogen#16), nie Force.
- **Offene PRs:**
  - [#1](https://github.com/ffunkfabian-hash/cubeescape-ballon/pull/1) Repo-Gerüst: `.ce-repo.json`, `./ce` ce-shared 0.24, `check.yml`. Worktree `.claude/worktrees/ballon-scaffold`.
  - [#2](https://github.com/ffunkfabian-hash/cubeescape-ballon/pull/2) BALLON 0.10 „Stride“: Richter erledigt, Tests grün. Worktree `.claude/worktrees/nifty-hamilton-62a7ee`.
  - Reihenfolge: zuerst #1, dann #2.
- **Unity-Projekt:** `unity/` (6000.6.2f1, URP). Die Szene `Assets/Ballon/Scenes/Firstfeel.unity` läuft mit Hangar (Taste L), vier Lichtszenen (N), Parcours (T) und Skins (K). Der Build liegt unter `unity/Build/` (nicht im Repo) und wird mit `python3 tools/unity_run.py build` erzeugt.

## Als Nächstes

1. **Nach dem Merge von #1 und #2:**
   - `.ce-repo.json` auf 0.10.0 „Stride“ heben.
   - `./ce session reserve` aus dem eigenen Worktree, mit `--repo` als absolutem Pfad. Mit `--repo .` reserviert der Befehl versehentlich Nexogen.
   - Die eigenen Worktrees `nifty-hamilton-62a7ee` und `ballon-scaffold` sauber entfernen.
2. **Sprint-Werte je Waffentyp:** Sie kommen aus Motiongen REF 0.24 „Glidepath“ (Branch `claude/ref-0.24-glidepath`, nur die 17 BASIC-Standardtypen). Die Vorab-Messung (Automatik, Handfeuerwaffe) liegt lokal auf `claude/ref-0.23-stride`, Commit `b37f392`, Worktree `~/Claude/cubeescape-reference/.claude/worktrees/ref-0.23-stride`. Sie ist nicht gepusht und noch ohne Richter; Glidepath arbeitet sie ein.
3. **Entscheidung beim Nutzer:** Der Sprint-Hub ist kleiner als in Destiny 2 (geschätzt ≈ 6 % / 4 % gegen 10–13 % / 13 %). Vor einer Änderung den Hub am Bild messen.
4. **Antworten von Motiongen** zu Visier-Anflug und Fadenkreuz je Typ: [uebergabe-motiongen-gefuehl.md](uebergabe-motiongen-gefuehl.md).
5. **Blender-Ego-Clips:** Nach dem Merge von 0.10 neu rendern, weil sich `ego.py` und `ego_build.py` geändert haben. Das ist die Sache der Sitzung, die die Clips führt.
6. **Vorgemerkt (Richter 0.9):** Die Bewegungswerte des Spielers stehen doppelt in `basic/scenes/__init__.py` (`PLAYER`) und `EgoPlayer.cs` (`MoveTuning`).

## Werkzeuge und Regeln, die hier gelernt wurden

- Reine Bewegungsänderungen exportiert `BALLON_EXPORT_DATA_ONLY=1 … ce lock blender …` in 2 s. Haben sich Form- oder Materialquellen geändert, bricht er ab; dann den vollen Export unter `ce lock gpu`. Die GPU ist exklusiv, andere Repos warten.
- `unity_run.py scenes`, `course`, `feel` und `bench` nutzen den Build: nach Codeänderungen zuerst `build`.
- yt-dlp: Standard-Client mit Deno im PATH (1080p60). Der Android-Client nur für Metadaten.
- Merge-Hook „merge-nur-sightline“: Merges über Sightline oder den Nutzer.
