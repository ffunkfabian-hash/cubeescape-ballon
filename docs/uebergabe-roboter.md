# Übergabe: BASIC-Roboter für die Außenansicht, Runde 5 (nach 0.23 „Gauntlet“)

Stand 27.10.2026, aus der Sitzung „BALLON 0.23 „Gauntlet“ · Mac“ (Branch `claude/ballon-0.23-gauntlet`). Geschrieben für eine
**frische Sitzung ohne Gesprächsverlauf**. Vorgänger (0.5 „Teardown“, auf Eis) und alle Runden stehen in
[versions/0.23-gauntlet.md](versions/0.23-gauntlet.md).

Opus 5.5, `high`, weil es um Formentwurf nach Nutzerkritik geht.

## Auftrag des Nutzers

> „Aber ich wünsche mir ja von dir das du einen passenden Roboter zu den Ego-Ansichten baust“ – „Der Roboter soll den
> Stilanforderungen von Ego v3 und Waffen entsprechen“

Kritik in Reihenfolge, alle vom 27.10.2026:
1. „lang und Schlacksig … irgendwie so ‚klotzig‘“
2. „Ggf. müssen die Arme ja auch einfach nur etwas dicker und stämmiger werden“
3. „Da fehlt irgendwie das gewisse etwas. er ist so klotzig und steif“
4. „Ich finde Hüfte und Beine sowie Schultern und Oberkörper passen einfach nicht“
5. „da können auch bestimmt mehr details rein, mehr sichtbare robotische sachen halt. ggf. kann man den kopf auch ‚runder‘
   gestalten wie insgesamt den körper“

**Vorgaben für Runde 5:**
- **Mehr sichtbare Robotertechnik.** Gelenke, Kolben, Leitungen und Fugen dürfen sichtbar sein. Für den Roboter gilt das
  Schlichtheitsbudget der Waffen damit nicht mehr streng (Kritik 5). Material, Skin und Medaillon bleiben aus der Familie.
- **Runder.** Kopf und Körper gewölbt statt flächig gefast. Runde 2 hatte gefaste Querschnitte (`ch`) eingeführt, damit der Körper
  zu den Facetten von Arm v3 passt. Das hat „klotzig“ verstärkt.
- **Die Baugruppen greifen ineinander.** Schulterpanzer, Rumpf, Becken und Oberschenkel überlappen. Jede Baugruppe als eigener
  Block wirkte „passt nicht“.
- **Nicht steif.** Haltung mit Standbein und Drehung, dazu Gegensatz von großer Masse zu schlanker Verbindung (Taille, Knie,
  Knöchel).
- **Arme:** Arm v3 bleibt für die Ego-Ansicht unverändert („Ich würde V3 Arme und Hände gerne auch behalten“). Am Roboter dürfen
  sie in `basic/robot/arms.py` abgewandelt werden (`BULK`, `EXTRA`, `DROP`).
- **Referenzen**, nur Prinzipien: [quellen.md](quellen.md) › Q-D2-PARADE, Q-ARMOR-ORANGE, Q-D2-ARM, dazu das Zielbild
  `~/Library/Caches/CubeEscapeBallon/refs/robot-concept.png`. Die beiden Bilder vom 27.10. liegen nicht auf der Platte. Den Nutzer
  bitten, sie erneut anzuhängen, und unter `refs/robot-parade.png` und `refs/robot-armor-orange.png` sichern.

## Empfohlenes Vorgehen

Drei Anläufe mit einem einzigen Entwurf und Korrektur nach jeder Kritik sind gescheitert (0.5, „gross“, 0.23 Runden 1–4). Bei
den Ego-Armen funktionierte dagegen: **drei Varianten nebeneinander, der Nutzer wählt** („Ich finde alle drei gut“). Deshalb:

1. Drei Körpervarianten als Blockout (Rumpf, Becken, Beine, Kopf, Arme v3 ×1,22), alle **rund** und mit sichtbarer Technik, aber
   verschieden in Proportion und Technikanteil. Zum Beispiel: heroisch-schwer wie Q-ARMOR-ORANGE, athletisch wie Q-D2-PARADE, und
   schlank-mechanisch wie robot-concept.
2. Eine Vergleichsseite mit Vorder-, Seiten- und Dreiviertelansicht je Variante, daneben die Ego-Hüftsicht mit Arm v3.
3. Erst nach der Wahl des Nutzers ins Detail gehen: Fugen, Kolben, Leitungen, Bolzen, die orangen Doppelstreifen der Waffen.

## Ausgangslage im Code

- Paket `basic/robot/`: `__init__.py` mit Skelett (`WAIST`, `NECK`, Rumpf- und Kopfdrehung `TORSO_HINT`/`HEAD_HINT`, die Schultern
  folgen dem Rumpfrahmen über `_torso_point`), `POSES`, `ANCHORS`, `EXPLODE` und `validate()`. Je Baugruppe ein Modul. Formhelfer
  in `shapes.py`: `loft`, `wrap`, `ring`, `tab` (mit `ch`), `arrow` (Pfeilschnitt), `two_bolts`, `medallion`, sowie aus 0.5 noch
  `piston` und `cable` für sichtbare Technik.
- Formen in `basic/arms/forms.py`, gebaut von `tools/ego_build.form_mesh`. Rund heißt `ch=0` und `n` 2,4–3,0.
- Aufbau und Bilder: `tools/robot_build.py` (`--check`, `--spec`, `--only hero,seite,nah`, `--tag`, `--samples`, `--res`). Teileliste
  mit `tools/robot_doc.py`. Regressionstest `tools/test_robot.py`.
- Rendern nur mit `~/Claude/cubeescape-nexogen/ce lock gpu -- /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup
  -P "$PWD/tools/robot_build.py" -- …`. Die Prüfung (`--check`) braucht keine Sperre.
- Nach Formänderungen: `--spec`, `python3 tools/robot_doc.py`, `./check`.

## Fertig wenn

Der Nutzer hat eine Variante gewählt, sie ist ausgearbeitet (Hero, Seite, Nah, Explosion, Baugruppen auf `--bg mid`), `./check` ist
grün, und der Bericht nennt die Wahl. Vor dem Merge kommt die Codex-Prüfung (`./ce judge`, ohne Codex `--opus`).
