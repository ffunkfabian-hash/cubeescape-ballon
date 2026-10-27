# Übergabe: Roboter Runde 5 und Helm „Scout“ (0.23 „Gauntlet“)

Stand 27.10.2026, aus der Sitzung „Roboter Runde 5“ (Worktree-Branch `claude/ballon-0-23-gauntlet-runde5-b524af`, abgezweigt von
`claude/ballon-0.23-gauntlet` bei 3c50133). Für eine **frische Sitzung ohne Gesprächsverlauf**. Vorgeschichte: [versions/0.23-gauntlet.md](versions/0.23-gauntlet.md),
[uebergabe-roboter.md](uebergabe-roboter.md). Nichts davon ist gemergt; der Standard-Roboter (`basic/robot/{head,upper_body,…}.py`) und
seine Spec sind unverändert, `./check` ist grün.

## 1. Roboter Runde 5 – drei Körperstudien (wartet auf die Wahl des Nutzers)

- Code: `basic/robot/studies/` – `body.py` (gemeinsamer Baukasten), `a_waechter.py` (heroisch-schwer), `b_paladin.py` (athletisch),
  `c_mechanik.py` (schlank-mechanisch), `helmet.py` (parametrischer Militärhelm, alle drei tragen ihn). `basic.robot.use(<studie>)` tauscht
  Skelett und Teile; `tools/robot_build.py --study <name>` rendert (neue Ansichten `vorn`, `profil`, `kopf`; `--preview` = Workbench).
- Neu in `tools/robot_build.py`: `--study`, Teil-Drehung `p['rot']`; in `basic/robot/__init__.py`: `_derive()`, `use()`.
- Nutzerkritik dieser Runde (alle umgesetzt): runder → später „generell alles zu rund“ (jetzt gefaste Querschnitte, nur Helmkuppel rund),
  mehr Details/Highlights (blanke Kanten, orange Doppelstreifen, Lichter), Schultern nicht hochgezogen, Hüfte/Bein-Übergang, Titan-Formen
  (Q-D1-TITAN, Formbeschreibung des Nutzers), Kopf „nicht Eierkopf“, „B sieht traurig aus“ (Augenschräge war gespiegelt; Kopf aufrecht).
- Vergleichsseite (Artefakt, privat): https://claude.ai/code/artifact/16831234-f8ba-4538-b417-1c4617413eee (Version 4).
- Belege: `~/Library/Caches/CubeEscapeBallon/out/robot/studies/<studie>/`. Referenzen: `~/Library/Caches/CubeEscapeBallon/refs/`
  (`robot-parade.png`, `robot-armor-orange.png`, `robot-helm-mil.png`; Titan-Bild nicht auf der Platte).
- **Offen:** Der Nutzer hat noch keine Variante gewählt. Danach: gewählte Variante in die Baugruppenmodule übernehmen, `robot_build.py --spec`,
  `python3 tools/robot_doc.py`, `./check`, Bericht `docs/versions/0.23-gauntlet.md`, `docs/quellen.md` (Q-D1-TITAN, Q-D2-HELM-MIL) ergänzen.

## 2. Helm „Scout“ – eigenständige Blender-Nachbauten nach Spezifikationen des Nutzers

Drei Fassungen, je ein Skript (nur Bordmittel, Hintergrundlauf), Ausgabe außerhalb des Repos:

| Skript | Spezifikation | Ergebnis (`~/Library/Caches/CubeEscapeBallon/out/…`) | Stand |
|---|---|---|---|
| `tools/helm_scout.py` | v1 (Facettenhelm, Maße in H) | `helm_scout/` | erledigt; Hüllmaß-Widersprüche der Spec im Bericht |
| `tools/helm_scout_ref.py` | v1, „näher an der Referenz“ | `helm_scout_ref/` | erledigt (runde Kuppel, Augen außen höher) |
| `tools/build_helm.py` | v2 (glattes Ei, IoU-Phasen) | `helm_scout_v2/` | Kriterien 2–8 erfüllt, IoU offen |
| `tools/build_helm_v3.py` | **v3 (Hard-Surface, Turntable-Referenz) – aktuell** | `helm_v3/` | Kriterien 2–8 erfüllt, IoU offen |

### v3 im Detail (letzter Arbeitsstand)

- Aufruf: `~/Claude/cubeescape-nexogen/ce lock gpu -- /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P "$PWD/tools/build_helm_v3.py" -- [--reuse-phase1] [--phase1-only] [--samples N]`
  (`--reuse-phase1` liest `phase1.json` und spart ≈ 10 min). Bericht: `out/helm_v3/REPORT.md`, Vergleich `out/helm_v3/vergleich_alle.jpg`.
- Referenzen: `refs/robot-helm-v3.png` (verbindlich, 2000 × 500, vier 90°-Ansichten), `refs/robot-helm-v3b.png` (Gegenprüfung),
  Turntable-Einzelbilder `refs/helm_v3_video/` (aus dem Video des Nutzers).
- Abnahme: 2 Hüllbox 0,81 × 1,05 × 1,00 ✓, 3 Kragenstufe ✓, 4 Krempe 0,020 ✓, 5 Pods/Antenne ✓, 6 Kabelabstand 0,035 ✓, 7 Objekte/18 Schrauben ✓, 8 ✓.
- **Offen: Kriterium 1 (IoU).** Phase 1: vorn 0,866 / rechts 0,904 / hinten 0,872 / links 0,763 (Soll 0,90 / 0,88 / 0,90 / 0,88);
  nach Details 0,82 / 0,72 / 0,86 / 0,81 (Soll ≥ 0,86). Gründe: Seitenansichten der Referenz tiefer als hoch (≈ 1,36), Abnahme 2 lässt nur
  1,06 ± 0,03 zu; Tuch-Oberkante von Hand abgelesen (`REF_CUT`), Schnitthöhe am Render geschätzt (`Z_CUT`).
- Bekannte Kleinigkeit: an den Augen innen unten eine kleine dunkle Kerbe (nicht untersucht).
- Gelernt (für alle Fassungen): exakte Booleans brauchen `use_self=True` (sonst leeres Netz), Schneidkörper nie in ausgeblendeten Collections
  (werden nicht ausgewertet), Solidify ohne „Even Thickness“ an schmalen Streifen, große projizierte N-Gons vermeiden (eben triangulieren,
  unterteilen, dann projizieren), Fugen dicht vor heller Schale brauchen eine dunkle Unterlage. Das Tuch hat der Nutzer zuletzt ausdrücklich
  weggelassen („Lass das Tuch bitte weg“).

## Prompt für die nächste Sitzung

> Repo cubeescape-ballon, Branch `claude/ballon-0-23-gauntlet-runde5-b524af` (Worktree der Sitzung „Roboter Runde 5“). Lies zuerst
> `docs/uebergabe-helm-roboter.md`, dann `docs/LESSONS.md`. Zwei offene Stränge: (1) Roboter Runde 5 – der Nutzer wählt eine der drei
> Studien (`basic/robot/studies/`, Vergleichsseite im Übergabedokument); danach ausarbeiten wie dort beschrieben. (2) Helm „Scout v3“ –
> `tools/build_helm_v3.py`, Ergebnis unter `~/Library/Caches/CubeEscapeBallon/out/helm_v3/`; Kriterien 2–8 erfüllt, offen ist die
> Silhouetten-IoU (Phase 1 vorn 0,866 / rechts 0,904 / hinten 0,872 / links 0,763). Frag den Nutzer, woran er weiterarbeiten will.
> Rendern nur unter `~/Claude/cubeescape-nexogen/ce lock gpu -- …`, Belege außerhalb des Repos, Commit/Push nur auf Wunsch, Antworten auf Deutsch.
