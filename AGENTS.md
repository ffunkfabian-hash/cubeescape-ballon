# Regeln für Agenten in cubeescape-ballon

Zentraler Einstieg: [Nexogen](https://github.com/ffunkfabian-hash/cubeescape-nexogen) (`~/Claude/cubeescape-nexogen`), globale Regeln
dort (`~/.claude/CLAUDE.md`). Dieses Repo ist dort **noch nicht** in `repos.json` eingetragen. **BALLON bleibt lokal** (Entscheidung des Nutzers 25.10.2026:
„Ballon bleibt lokal“): kein Remote, kein öffentliches Repo; Merges nur nach Ja des Nutzers in der Sitzung, per `--ff-only`.

## Was hier liegt

Die Waffenreihe BASIC (17 Grundtypen) als Blender-Modelle. Erst [README.md](README.md), dann [docs/PROJEKT.md](docs/PROJEKT.md),
[docs/designvertrag.md](docs/designvertrag.md) und [docs/LESSONS.md](docs/LESSONS.md) lesen. **Für jede neue Waffe oder Variante
im Stil v2 (Destiny-Detaildichte + AAA-Material, schlicht) gilt [docs/stilhandbuch.md](docs/stilhandbuch.md)** – Regeln,
Schlichtheitsbudget, Materialrollen, Skins, Baukasten, Arbeitsablauf.

## Regeln

- **Eine Quelle:** Entwurf nur in `basic/weapons/wNN_*.py` (Bauteile, Baugruppen, Anker, Bewegungen) und `basic/common.py`
  (gemeinsame Bausteine). `data/specs/`, `docs/abdeckung.md`, `docs/haltungen.md`, `docs/bauteile/`, `data/matrix.json` sind erzeugt.
- **IDs sind stabil:** Waffen `BASIC-NN`, Bauteile englisch snake_case, Anker `Socket_*` (Toolgen-Namen). Umbenennen nur mit
  Spec-Version 2 und Migrationshinweis.
- **Maße nur aus dem Modell:** Blätter und Doku nennen ausschließlich gemessene Werte aus `spec.json`.
- **Status ehrlich führen:** Entwurf, visuell geprüft, exportiert, im Spiel angebunden sind verschiedene Zustände. Matrixfelder nie leer.
- **Schwere Läufe** (Renderings, Bildfolgen) nur mit Sperre: `~/Claude/cubeescape-nexogen/ce lock gpu -- …` (mit `--gpu`) bzw. `ce lock blender`.
- **Belege außerhalb des Repos:** `~/Library/Caches/CubeEscapeBallon/`.
- **Nicht hier:** Formgen-Blätter, Toolgen-Assets/Clips, Cube-Escape-Code. Diese Repos nur lesen.
- **Zurückgestellt bleibt zurückgestellt:** Einträge in [docs/erweiterungen.md](docs/erweiterungen.md) nicht ohne Auftrag bauen.
- Commit, Push, Remote, Tag, Release nur auf Wunsch des Nutzers; nie auf `main` committen.
- **Unity folgt Blender so nah wie möglich** (Nutzerwunsch 24.10.2026, dauerhaft). Das gilt für Form, Bewegung, Material,
  Licht und Tonwerte. Blender bleibt die Quelle: Material backen statt in Unity neu erfinden. Jede sichtbare Unity-Änderung
  wird gegen frisch gerenderte Blender-Stills verglichen (`tools/unity_run.py compare`); Abweichungen messen und im Bericht
  begründen ([docs/unity.md](docs/unity.md)).
- Vor Commit: `./check`.
