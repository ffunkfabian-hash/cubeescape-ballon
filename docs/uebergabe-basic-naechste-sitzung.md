# Übergabe an die nächste BASIC-Sitzung (Waffen, Visiere, Ego-Clips in Blender) – Stand 25.10.2026

Für eine **frische Sitzung ohne Verlauf**, direkt auf dem Mac (Blender, GPU). Modell Opus 5.5 `high`, weil es um Entwurf und
Spielgefühl geht. Antworten auf Deutsch.

## Zuerst lesen

1. `AGENTS.md` und `docs/LESSONS.md` (Lehren, ≤ 60 Zeilen).
2. `docs/stilhandbuch.md`: §1 enthält die Nutzerentscheidungen, §7 den Arbeitsablauf je Waffe, §6 mit „Absehen und Visierglas“
   die Visier-Designsprache v3.
3. `docs/versions/0.6-riflekin.md` mit den Familienwaffen 01–03 und Visier v3, außerdem `docs/absehen.md`.
4. Lange Docs nicht ganz lesen, sondern erst mit `ce_search` oder `rg -n` den Abschnitt finden.

## Stand

- **Repo:** öffentlich, https://github.com/ffunkfabian-hash/cubeescape-ballon. Der Standardbranch `claude/basic-first-light` steht
  auf Stand 0.10 „Stride“ (PR #1, #2 und #4 sind gemergt).
- **Dieser Branch** `claude/basic-smg-uebergabe` geht von `origin/claude/basic-first-light` aus und enthält nur diese Datei und
  den Entwurf der Maschinenpistole. Er ist lokal und nicht gepusht.
- **Familie Stil v2.1:** Fertig, gesichtet und committet sind BASIC-01 Automatikgewehr, 02 Impulsgewehr und 03 Scout, alle mit
  Visier-Designsprache v3:
  - Holo-Visier mit Trapezsockel, kurzes Ring-Zielfernrohr auf Trapezhals;
  - Augenabstand 90 mm, Visierhöhe 66 ± 4 mm;
  - Absehen fein, Glasspuren nur am Rand.

  Die Module liegen in `basic/pilot/w0N_*_v21.py`, die Bausteine `reflex_sight_v21` und `scope_v21` in `basic/common.py`.
- **Absehen-Katalog:** `basic/reticles.py` mit Formen, Farben, Stärken, Glas, Aufgehen, `SETTINGS`, `SIGHT`, `SIGHT_KIND`,
  `CLASS_ZOOM` und `ADS_FEEDBACK`. Daraus erzeugt `tools/export_reticles.py` die Dateien `data/reticles.json` und
  `docs/absehen.md`.
- **Spieleroption Visiernähe:** `SETTINGS['ads_eye_relief']` mit 70, 90 oder 110 mm, Standard 90 (Nutzer: „90 mm, 70 mm
  optional“). Umgesetzt ist das nur als Daten. Die Unity-Seite steht in `docs/uebergabe-unity-visier.md` (Nachtrag v3).

## Offen – in dieser Reihenfolge

### 1. Entscheidung des Nutzers abholen (blockiert die Maschinenpistole)

Der Nutzer fragte: „Warum wird nicht erst v3 gemacht?“ Die Namen waren verwirrend: „v3“ ist nur die Visier-Designsprache, der
Waffenstil heißt weiter v2.1. Offen ist seine Wahl:

- **(a)** Alles bleibt, nur die Namen werden geklärt („Visier v3“ im Stil v2.1). Dann die Maschinenpistole fertig machen.
- **(b)** Erst einen **Waffenstil v3** festlegen und danach die Familie weiterbauen.

Der Nutzer wollte erst Motiongen und die Analysen abwarten und meldet sich mit einem OK. Vor dem OK nichts bauen.

**Entschieden 25.10.2026: (a).** Namen in `docs/stilhandbuch.md` (Kopf und §1) geklärt: Stil v2.1, Visier-Standard 3, Arm v3.

### 2. Maschinenpistole BASIC-06 v2.1 (bei Wahl (a)) – **erledigt in 0.11 „Compact“** ([Bericht](versions/0.11-compact.md))

- Der Entwurf liegt in `basic/pilot/entwurf/w06_submachine_gun_v21.py`. Er ist geparkt, damit `./check` grün bleibt: Die Prüfung
  sucht nur nach `basic/pilot/w*_v21.py`. Zum Weiterarbeiten mit `git mv` nach `basic/pilot/` zurückholen.
- Inhalt:
  - Bohrungsachse 82 mm, Gehäuseoberkante 113 mm (Visierhöhe 65 mm);
  - Kastenvorbau 171–292 mm mit Lüftungsschlitzen, Bügel vom Abzug zum Vordergriff;
  - Magazin im Griff mit Sichtfenster, Holo-Visier mit Absehen `dot`, kurzer Schaft S1 (×0,72);
  - Aktionen `fire_auto` und `reload_empty` aus V1.
- Schnellrenderings liegen in `~/Library/Caches/CubeEscapeBallon/out/BASIC-06-v2.1/views/`, **noch nicht gesichtet**. Vorgemerkt:
  Der Bügel wirkt eventuell zu dünn.
- Es fehlt (Dokumentationspflicht, stilhandbuch §7):
  - drei Sichtungsrunden;
  - volles Rendering mit Skins und Bewegung (`ce lock gpu`);
  - Einträge in `data/review.json` (BASIC-06-v2.1: Ansichten und jede Aktion);
  - Zeilen in `docs/quellen.md › Q-D2-IMG`: Parabellum `3769072067`, The Recluse `1050806815`, New City `2414612776`, je mit
    beobachtetem Prinzip;
  - Familienseite (`tools/make_sheets.py --family`), Bericht und CHANGELOG.
- Danach kommen die übrigen 13 Grundtypen in der Reihenfolge des Designvertrags. Je Typ gelten `SIGHT_KIND` und
  `RETICLE_DEFAULTS` aus `basic/reticles.py`.

### 3. Blender-Ego-Clips neu rendern (unabhängig von 1)

0.10 „Stride“ hat `basic/arms/ego.py` und `tools/ego_build.py` geändert:
- Sprint nach Destiny 2 gemessen: 3,16 Hz, U-Bogen, Rollen ±3,5°;
- `aim_zeta = 1,0`, also kein Überschwingen ins Visier;
- Format `ballon-ego/4`.

Die Ego-Stills und -Clips in `~/Library/Caches/CubeEscapeBallon/evidence/` (`ego_BASIC-01-v2.1_*.png`, `clips/`) sind veraltet.
Neu erzeugen mit `tools/make_ego.py` unter `ce lock gpu`, dann die Sichtung der Ego-Aktionen in `data/review.json` erneuern.

### 4. Daten aus Motiongen einarbeiten (nach Merge von cubeescape-motiongen#51)

- REF 0.24 „Glidepath“ und REF 0.23 „Stride“ liefern je BASIC-Grundtyp drei Dinge: Sprint, Anflug Hüfte↔Zielen und Fadenkreuz.
  Sie stehen in den Motiongen-Docs `huefte.md` und `visiere.md` (`~/Claude/cubeescape-reference`, nur lesen).
- Kurzfassung:
  - Kein gemessener Typ schwingt beim Anflug über.
  - Destiny 2 hat ein Hüft-Fadenkreuz, das im Sprint und zu Beginn des Zielens ausblendet.
  - Der Nutzer hat das ständige Fadenkreuz in Unity entfernen lassen („muss weg“). Ein ausblendendes Hüft-Fadenkreuz wäre eine
    neue Nutzerentscheidung.
- **Entscheidung beim Nutzer:** Der Sprint wippt kleiner auf und ab als in Destiny 2 (geschätzt ≈ 6 % gegen 10–13 %). Vor einer
  Änderung am Bild messen.

## Regeln (Stand 25.10., von Sightline und Nutzer)

- **Commit** ist freigegeben, nur auf eigenen Branches, vor jedem Commit `./check`. **Push** auf eigene Branches ist erlaubt,
  nie Force. **Merge** nur durch Sightline (Postfach cubeescape-nexogen#16) oder den Nutzer; der Hook „merge-nur-sightline“
  blockiert sonst.
- Das Repo ist **öffentlich**: keine Geheimnisse, keine fremden Medien (Destiny-Bilder nur als URL in `docs/quellen.md`), nichts
  Privates.
- **Sitzung reservieren** mit `./ce session reserve` und `--repo` als **absolutem** Pfad. Mit `--repo .` reserviert der Befehl
  versehentlich Nexogen.
- **GPU exklusiv:** Rendern und voller Unity-Export laufen unter `~/Claude/cubeescape-nexogen/ce lock gpu -- …` mit `--gpu`.
  Alles ohne GPU-Bedarf läuft unter `ce lock blender` aus dem eigenen Worktree. Skriptpfade absolut angeben.
- **Unity-Kopplung:** Jede Änderung an `kit.py`, `common.py`, der Pilotwaffe BASIC-01 oder den Arm- und Ego-Daten macht `./check`
  rot („ego.json veraltet“), bis neu exportiert ist. Für reine Bewegungsdaten reicht `BALLON_EXPORT_DATA_ONLY=1` unter
  `ce lock blender` (2 s). Bei Form oder Material braucht es den vollen Export (≈ 20 min, `ce lock gpu`), siehe `docs/unity.md`.
  `reticles.py` ist nicht im Hash.
- **Unity folgt Blender** so nah wie möglich. Unity-Arbeit gehört einer eigenen Unity-Sitzung; hier nur die Blender-Quelle
  pflegen.
- **Belege** liegen außerhalb des Repos unter `~/Library/Caches/CubeEscapeBallon/`. MP4 nur, wenn sich Bewegung geändert hat.
- **Blender-MCP** darf genutzt werden: nur in eigener Szene, speichern nur über `wm.save_as_mainfile`. Die interaktive
  Oberfläche ist deutsch, deshalb `use_translate_new_dataname = False` setzen und danach zurücksetzen.
- **Zuarbeit:** Werte von Antigravity nur nach eigener Nachmessung übernehmen.
- **yt-dlp:** Standard-Client mit Deno im PATH (`/opt/homebrew/bin`) für 1080p60, den Android-Client nur für Metadaten.
- **Nur lesen:** Toolgen, Robogen, Formgen und Cube Escape. Der Roboter (`basic/robot/`, Branch `claude/ballon-0.5-teardown`)
  gehört nicht hierher.

## Abschluss dieser Sitzung

Die alte BASIC-Hauptsitzung räumt nichts mehr auf. Der Hauptcheckout `~/Claude/cubeescape-ballon` steht noch auf dem lokalen
`claude/basic-first-light` (`1a51419`, hinter origin). Die Arbeit hier deshalb in einem eigenen Worktree von diesem Branch
beginnen.
