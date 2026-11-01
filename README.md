# cubeescape-ballon

Die schlichte Waffenreihe **BASIC** für Cube Escape: 17 Grundtypen als echte 3D-Baugruppen in Blender, mit gemessenen Specs,
Konzept- und Baugruppenblättern, Explosionsansichten und Bewegungsvorschauen der Mechanik.

Gegründet mit **0.1.0 „First Light“** (24.10.2026) · öffentliches Repo (Stand und Version: `.ce-repo.json`, [CHANGELOG.md](CHANGELOG.md)) · Einstieg für Agenten: [AGENTS.md](AGENTS.md).

## Inhalt

| Ort | Inhalt |
|---|---|
| [docs/PROJEKT.md](docs/PROJEKT.md) | Warum ein eigenes Projekt, Zuständigkeiten, Schnittstellen, Datenfluss |
| [docs/designvertrag.md](docs/designvertrag.md) | Gestaltungsregeln: Formen, Radien, Fugen, Materialrollen, wiederkehrende Bauteile |
| [docs/stilhandbuch.md](docs/stilhandbuch.md) | **Stil v2 für künftige Varianten:** Destiny-Detaildichte + AAA-Material, schlicht; Skins, Baukasten, Ablauf |
| [docs/abdeckung.md](docs/abdeckung.md) | Abdeckungsmatrix der 17 Grundtypen (erzeugt) |
| [docs/haltungen.md](docs/haltungen.md) | Haltungs- und Animationsmatrix je Waffe, Übergänge (erzeugt) |
| [docs/bauteile/](docs/bauteile/) | Baugruppenbaum, Bauteilliste, Anker, Aktionen je Waffe (erzeugt) |
| [docs/quellen.md](docs/quellen.md) | Quellen mit Status (gemessen/beobachtet/abgeleitet/entworfen/offen) |
| [docs/erweiterungen.md](docs/erweiterungen.md) | Zurückgestellte Sondervarianten und Exoten |
| [docs/spec.md](docs/spec.md) | Datenformat `data/specs/BASIC-NN.spec.json` |
| `basic/` | Entwurf als Python-Daten (`weapons/wNN_*.py`), Bausteine (`common.py`), Blender-Baukasten (`kit.py`), Matrixregeln (`matrix.py`) |
| [docs/unity.md](docs/unity.md) | Unity-Spürtest 0.4: Pilotwaffe mit Armen aus der Ego-Perspektive spielen, Export, Tests, Build |
| `unity/` | Unity-6-Projekt (URP, Input System), Ego-Laufzeit in C# aus `basic/arms/ego.py` |
| `tools/` | Bau, Blätter, Clips, Kontaktbögen, Doku, Prüfung, Unity-Export (`export_unity.py`, `unity_run.py`) |

## Bauen und prüfen

```bash
./check                                                    # schnell: Daten, Konsistenz, Sichtung, Drehsinn-Test, Doku aktuell
~/Claude/cubeescape-nexogen/ce lock gpu -- python3 tools/build_all.py --views --gpu   # Modelle, Specs, Ansichten (≈ 1 min je Waffe)
~/Claude/cubeescape-nexogen/ce lock gpu -- python3 tools/build_all.py --motion --gpu  # Bildfolgen der Mechanik
python3 tools/sync_specs.py && python3 tools/make_docs.py  # Specs ins Repo, Doku neu
python3 tools/make_clips.py && python3 tools/motion_sheet.py && python3 tools/make_sheets.py && python3 tools/contact.py side --scale
python3 tools/make_sheets.py --gallery /pfad/galerie.html   # kompakte Galerie (Formstudie 01 + 17 Karten)
```

Ausgaben liegen außerhalb des Repos: `~/Library/Caches/CubeEscapeBallon/out/` (Modelle, Ansichten, Blätter) und `…/evidence/`
(Kontaktbögen, Clips). Ohne GPU-Sperre: `--gpu` weglassen und `ce lock blender` verwenden (CPU, langsamer).
