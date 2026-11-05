# Regeln für Agenten in cubeescape-ballon

Zentraler Einstieg: [Nexogen](https://github.com/ffunkfabian-hash/cubeescape-nexogen) (`~/Claude/cubeescape-nexogen`), globale Regeln
dort (`~/.claude/CLAUDE.md`). Öffentliches Repo [ffunkfabian-hash/cubeescape-ballon](https://github.com/ffunkfabian-hash/cubeescape-ballon), Standardbranch
`main`. Der Eintrag in Nexogens `repos.json` macht Sightline.

## Harter Kern

Quelle: Nexogen `templates/kern.md`, nur dort ändern; gilt auch in Cloud-Sitzungen.

1. Kein Commit direkt auf `main`.
2. Kein Force-Push, keine überschriebenen Branches oder Tags.
3. Nichts Fremdes anfassen oder löschen: andere Sitzungen, Worktrees, Stash, Haupt-Checkout.
4. Merge nach `main` nur mit Ja des Nutzers, außer Patch bis 100 Zeilen ohne Format, Vertrag, Kernpfad bei grünem `merge-check`; Tag, Release, Repo öffentlich machen immer nur mit Ja.
5. Tests nie löschen oder abschwächen, um grün zu werden.
6. Keine Zugangsdaten, kein fremdes Material, keine großen Binärdaten nach außen (öffentliche Repos, fremde APIs).
7. Formate, Verträge und IDs nur mit Migration; IDs sind ewig.
8. Nichts als fertig melden, was nicht geprüft ist.

## Was hier liegt

Die Waffenreihe BASIC (17 Grundtypen) als Blender-Modelle. Erst [README.md](README.md), dann [docs/PROJEKT.md](docs/PROJEKT.md),
[docs/designvertrag.md](docs/designvertrag.md) und [docs/LESSONS.md](docs/LESSONS.md) lesen (Langform: [LESSONS-lang.md](docs/LESSONS-lang.md)). **Für jede neue Waffe oder Variante
im Stil v2 (Destiny-Detaildichte + AAA-Material, schlicht) gilt [docs/stilhandbuch.md](docs/stilhandbuch.md)** – Regeln,
Schlichtheitsbudget, Materialrollen, Skins, Baukasten, Arbeitsablauf.

## Regeln

- **Eine Quelle:** Entwurf nur in `basic/weapons/wNN_*.py` (Bauteile, Baugruppen, Anker, Bewegungen) und `basic/common.py`
  (gemeinsame Bausteine). `data/specs/`, `docs/abdeckung.md`, `docs/haltungen.md`, `docs/bauteile/`, `data/matrix.json`,
  `packages/ego-arms/` (Arm-Paket, `tools/export_arms.py`) sind erzeugt.
- **IDs sind stabil:** Waffen `BASIC-NN`, Bauteile englisch snake_case, Anker `Socket_*` (Toolgen-Namen). Umbenennen nur mit
  Spec-Version 2 und Migrationshinweis.
- **Maße nur aus dem Modell:** Blätter und Doku nennen ausschließlich gemessene Werte aus `spec.json`.
- **Status ehrlich führen:** Entwurf, visuell geprüft, exportiert, im Spiel angebunden sind verschiedene Zustände. Matrixfelder nie leer.
- **Schwere Läufe** (Renderings, Bildfolgen, Bakes) nur mit `./ce lock gpu -- …` (Blender mit `--gpu`) bzw. `./ce lock blender|unity -- …`, je Ressource einzeln, nicht ineinander ([Lehre](docs/LESSONS.md)).
- **Erst Muster, dann Masse:** Vor jedem Lauf über viele Waffen (Serien, Voll-Bake) die Einstellung an zwei, drei Waffen in der Ego-Ansicht abnehmen, Hüfte und Zielen, nicht nur je Karte. Große Läufe möglichst über Nacht ([Lehre 0.43](docs/LESSONS.md)).
- **Belege** liegen in `~/Library/Caches/CubeEscapeBallon/`.
- **Nicht hier:** Formgen-Blätter, Toolgen-Assets/Clips, Cube-Escape-Code. Diese Repos nur lesen. Ausnahme seit 0.41: Formgen-Pakete
  liegen entpackt unter `unity/Assets/Ballon/Generated/Formgen/<ID>/` (Formgens Ausgabe, nicht von Hand ändern; Vertrag
  [docs/formgen-schnittstelle.md](docs/formgen-schnittstelle.md)).
- **Zurückgestellt bleibt zurückgestellt:** Einträge in [docs/erweiterungen.md](docs/erweiterungen.md) nicht ohne Auftrag bauen.
- **Unity folgt Blender so nah wie möglich** (Nutzerwunsch 24.10.2026, dauerhaft). Das gilt für Form, Bewegung, Material,
  Licht und Tonwerte. Blender bleibt die Quelle: Material backen statt in Unity neu erfinden. Jede sichtbare Unity-Änderung
  wird gegen frisch gerenderte Blender-Stills verglichen (`tools/unity_run.py compare`); Abweichungen messen und im Bericht
  begründen ([docs/unity.md](docs/unity.md)).
