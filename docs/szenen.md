# Hintergrundszenen (0.9 „Parcours“)

Szenen sind Python-Daten (`basic/scenes/<name>.py`), Blender baut sie mit `tools/scene_build.py` und schreibt das Format
[`ballon-scene/2`](szenen-format.md) nach `unity/Assets/Ballon/Generated/Scenes/<name>/`. Unity zeigt die Umgebung unbeleuchtet
mit den gebackenen Lichtatlanten (ein Atlas je Zone und Lichtszene) und beleuchtet nur das Viewmodel mit den Lichtern der
gewählten Lichtszene. Nutzerwunsch 25.10.2026: Detailtreue wie bei der Waffe, mehrere Lichtszenen, Zielscheiben als Parcours,
„Alles bitte dokumentieren“.

## Befehl und Dauer

```sh
BALLON_BAKE_GPU=1 ~/Claude/cubeescape-nexogen/ce lock gpu -- /Applications/Blender.app/Contents/MacOS/Blender -b \
  --factory-startup -P <ABSOLUTER Pfad>/tools/scene_build.py -- hangar
python3 tools/scene_build.py --check      # Teil von ./check: Datei passt zu den Quellen (SHA-256 + alle Datenfelder + Parcoursprüfung)
```

Auf die Sperre zu warten ist normal; der Lauf gibt jeden Schritt mit Zeit aus (`flush=True`). Gemessen auf der M5-GPU
(Lauf 25.10.2026, 64 Samples + OIDN, Grundfarbe 48 Samples, 4 Lichtszenen):

| Schritt | Dauer |
|---|---|
| Bildmasken rastern, Bau (3139 Bauteile, gefast), UV aller Zonen | < 1 s |
| Grundfarbe aller Zonen (Bevel-Abrieb, AO-Schmutz, Masken; einmal) | 2,4 min |
| Normalen (Führung für das Entrauschen; einmal) | 9 s |
| je Lichtszene: Backen aller Zonen in einem Aufruf | 2,8–3,7 min |
| je Lichtszene: Entrauschen (OIDN, 4 Atlanten) | 32–40 s |
| je Lichtszene: Vergleichsrender 1600 × 900 / 256 Samples, Atlasansicht, 8 Sichtungsansichten | 35–45 s |
| je Lichtszene gesamt | 4,2–5,0 min |
| **Gesamt (4 Lichtszenen)** | **21,2 min** (Ziel ≤ 30 min) |

Testläufe (Ausgabe nur in `~/Library/Caches/CubeEscapeBallon/unity/scenes/test/`): `BALLON_SCENE_TEST=1` (Atlanten ½,
32/8 Samples), `BALLON_SCENE_LIGHTS=tag,nacht` (nur diese Lichtszenen), `BALLON_SCENE_DIV=1` (volle Atlasgröße),
`BALLON_SCENE_SAMPLES` / `BALLON_SCENE_ASAMPLES` (Samples Licht / Grundfarbe), `BALLON_SCENE_DENOISE=0`,
`BALLON_SCENE_UVONLY=1` (nur Bau und UV, ≈ 1 s – für Belegungsversuche), `BALLON_SCENE_UV_ANGLE` (Smart-UV-Winkel, Standard 66°).
Den Atlas-Abstand nie mit Atlanten ≤ 1024² prüfen: bei tausenden Inseln frisst der Packabstand die Fläche (siehe Lehren).

Ausgaben im Cache (nicht im Repo, `~/Library/Caches/CubeEscapeBallon/unity/scenes/`):

| Datei | Inhalt |
|---|---|
| `hangar_<licht>_ref.png` | Cycles-Vergleichsrender vom Startpunkt (Referenzbild der Szenendatei) |
| `hangar_<licht>_atlas_view.png` | dieselbe Kamera, Umgebung unbeleuchtet mit den Atlanten – so sieht Unity sie |
| `hangar_<licht>_<ansicht>.png` | Sichtungsansichten (Atlasansicht): `gasse`, `tor`, `geruest`, `laufsteg`, `wand`, `boden`, `nord`, `sturz` |
| `hangar_plan.png` | Skizze: Draufsicht ohne Dach mit Strecke (rot), Toren (grün), Kontrollpunkten 1–5 (cyan), Zielen (magenta), Start (weiß) |
| `hangar_albedo_<zone>.png`, `decals/*.png` | Grundfarbe je Zone, gerasterte Bildmasken |
| `hangar_build.blend`, `hangar_build.json` | Baustand und Kennzahlen (Dreiecke, Belegung, Zeiten je Schritt, Höchstwerte, Abweichung) |

## Ablauf in `scene_build.py`

1. **Bildmasken:** `DECALS` (Boden, Vorfeld, Schilder, Containernummern) werden mit numpy gerastert: Rechtecke, Rahmen,
   Warnschraffur 45°, Schachbrett (Start/Ziel), Linien, Ringe, Strichschrift (`GLYPHS` in `basic/scenes/__init__.py`), Ölflecken
   (Rauschen, dunkler Rand), Reifenspuren (Doppelspur, unterbrochen), Dreiecke. Jede Maske wird im Weltraum auf ihre Ebene
   projiziert und nur innerhalb ±`depth` angewandt.
2. **Bau:** Jedes Bauteil wird als eigenes bmesh erzeugt, alle Kanten über 40° werden gefast (`bmesh.ops.bevel`, Breite
   `bevel_of`: ≈ 15 % der kleinsten Abmessung, 5–20 mm, unter 4 cm keine; Zylinder glatt ohne Fase) und in das Netz seiner Gruppe
   geschrieben. Trapezblech (`corr`) ist echte Geometrie mit Weltphase (Nachbarfelder passen). Verdeckte Seiten fallen weg
   (`skip`, Zylinderdeckel `caps`, offene Strebenenden `ends=False`).
3. **Materialien (Grundfarbe):** eigene Umgebungsrollen (`ROLES`, `kit.py` bleibt unberührt) nach dem Prinzip von `kit.aaa_nodes`:
   Helligkeits- und Rauheitsrauschen, großflächige Verschmutzung (`mottle`), Fugen (Boden 5 m mit Kantenausbrüchen, Sockel 3 m),
   Gitterrost, Warnstreifen, Laufspuren (`streaks`), Bildmasken, **Kantenabrieb** (Bevel-Knoten, Messradius 5 cm > Fase, gebrochen
   durch Rauschen), **Schmutz in Ecken** (AO-Knoten, 0,35–0,6 m) und Spritzschmutz am Fuß (`foot`).
4. **Lightmap-UVs je Zone:** Smart UV (66°), Inseln auf gleiche Texeldichte, gepackt mit 2 Texeln Abstand; eine UV-Lage für alle
   Lichtszenen. Je Zone ein Material-Satz (Kopien), damit jede Zone in ihr eigenes Bild backt.
5. **Grundfarbe backen:** einmal `DIFFUSE`/`COLOR` aller Zonen (48 Samples) – die teuren Knoten (Bevel, AO) laufen nur hier.
   Danach tragen die Lichtmaterialien den Albedo-Atlas (sRGB 8 bit) als Grundfarbe; Leuchtrollen (Strahler, Notlicht, Randfeuer,
   Fluchtwegschilder) leuchten mit Albedo × Stärke der Lichtszene (`LIGHTINGS[].emit`).
6. **Je Lichtszene:** Lichter und Himmel setzen, Umgebungslicht messen (Panorama 256 × 128 am Startpunkt, raumwinkelgewichtet →
   `ambient`), alle Zonen in **einem** Backaufruf backen (`COMBINED` mit Emission + Diffus direkt/indirekt, ohne Glanz; je Zone
   eine zusammengefügte Kopie, die Originale aus dem Render), mit **OIDN** entrauschen (Kompositor, Führung Albedo + Normalen),
   als Licht / `scale` in sRGB 8 bit mit Dreiecks-Dither speichern; Vergleichsrender, Atlasansicht und Sichtungsansichten.
7. **Ausgabe:** FBX (Optionen wie `export_unity.py`), ein Material je Zone `hangar_<zone>`, UV-Kanal 0 = Lichtatlas der Zone;
   `scene_hangar.json` mit den gemessenen Feldern `zones[].texel_m` und `lightings[].ambient`.

## Hangar (`basic/scenes/hangar.py`)

Halle 40 × 60 m, Dach innen 14 m; offenes Tor 34 × 11 m bei y = −30, davor Vorfeld 40 × 21,5 m mit Splitterschutzwänden (T-Wall
3,6 m). Startpunkt (0, 25, 0), Blick −Y durch die Halle.

### Aufbau und Detailstufe

| Was | Inhalt |
|---|---|
| Boden | 24 Felder 10 × 10 m (Nähte in Fugen), Fugen 5 m mit Kantenausbrüchen, Einrolllinie mit Haltebalken, Gehweglinien, Torschwelle mit Warnschraffur und Rinne, Start-/Zielschachbrett, „H3“ (2,4 m), Kontrollpunktringe 1 und 3, Stellplatz Aggregat, Schraffur vor dem Schaltschrank, 22 Ölflecken, zwei Gabelstapler-Doppelspuren, vier Ausbesserungen |
| Wände | Betonsockel 1,2 m (Fertigteilfugen 3 m, Blechabdeckung), Trapezblech 30 cm/3,5 cm als Profil, Lichtband 8,6–10,4 m in West- und Ostwand (offen, Sprossen alle 1,5 m, Brüstungs-/Sturzblech), zwei Stahltüren mit Zarge (Warnanstrich), Drücker, Trittblech, Fluchtwegschild (leuchtet) und Notleuchte, Hallennummer „H3“ an der Nordwand |
| Tragwerk | 20 Stützen HEB 400 als I-Profil (Flansche, Steg, Fußplatte, 4 Ankermuttern, Anfahrschutz-Anstrich bis 1,5 m, Voute), Wandverbände in den Endfeldern, 10 Fachwerkbinder mit Knotenblechen am Untergurt, 9 Pfetten, Dach Trapezblech 35 cm/5 cm |
| Tor | Torpfosten mit 68 Schrauben, Anschlagleisten, Torsturz mit 57 Schrauben, Aussteifungen, Schild „HANGAR 3“, Warnband, Faltflügel mit Querriegeln und Verriegelung, Lauf- und Bodenschiene, Notleuchten |
| Technik | Kabeltrassen (z = 4,6 m) mit je 4 Kabeln und Konsolen an beiden Längswänden, zwei Schaltschränke mit Türfuge, Schwenkgriffen, Warnschild und Leitungen zur Trasse, drei Feuerlöscher mit Halter und Hinweisschild |
| Strahler | 2 × 10 Gehäuse mit Blendrahmen, Leuchtfläche 1 m², 6 Kühlrippen, Vorschaltgerät, Abhängung, Zuleitung |
| Parcours | Start- und Zielportal (Schilder START/ZIEL mit Schachbrett), 2 × 24 m Absperrgitter, 4 Slalomhindernisse, Mauer 0,6 m, Kistenberg, Containergasse (2 Seecontainer mit Profilwänden, Eckbeschlägen, Türen, Verriegelung, Containernummern) mit Rohrbrücke (Flansche, Wanddurchführung, Steigleitungen, Warnmanschette, Schild „KOPFHÖHE 1,35 M“), Leitwand 0,6 m, Gerüst (Treppe, zwei Bühnen, Laufsteg mit Geländer, Verbände, Schilder 2/4/5), Absprungkiste, Kistenburg, 14 Zielständer/-rückplatten |
| Ausstattung | Kisten mit Deckelband, Kufen, Kantenschutz, Griffen; Paletten mit Kufen und Brettern; Fässer mit Rollreifen und Spundloch; Schwerlastregal mit Anfahrschutz und Rahmenstreben; Bürocontainer „LEITSTAND“ mit Rahmen, Fenstern, Klimagerät, Notleuchte; Stromaggregat mit Lamellen, Auspuff, Kranöse, Radnaben |
| Vorfeld | 8 Felder, Fugen 5 m, Mittellinie, Haltebalken, Randlinien, „H3“, Flecken, Flugzeug-Reifenspur, 12 blaue Randfeuer; T-Walls mit Fuß und Hebeösen |

**Kennzahlen (gemessen):** 21 Objekte, 3139 Netzbauteile, **68 946 Dreiecke** (Budget 160 000), 536 Kollisionsquader.
Leistung in Unity: die Umgebung ist unbeleuchtet, 21 Objekte mit je einem Material ihrer Zone (≈ 21 Zeichenaufrufe);
69 000 Dreiecke sind sechsmal so viele wie in 0.8 (11 740), liegen aber deutlich unter dem Budget (in Unity zu messen, siehe Grenzen).

### Zonen und Texeldichte

Jedes FBX-Objekt gehört zu genau einer Zone; alle Lichtszenen nutzen dieselben UVs. Gemessen nach dem Packen (`texel_m` in der
Szenendatei):

| Zone | Objekte | Atlas | Fläche | belegt | **Texel** | Dreiecke |
|---|---|---|---|---|---|---|
| `boden` (nah) | Boden | 4096² | 2420 m² | 92 % | **1,25 cm** | 48 |
| `nah` | Parcours, Geruest, Ducken, Kisten, Faesser, Regal, Buero, Aggregat | 4096² | 1787 m² | 71 % | **1,23 cm** | 26 666 |
| `wand` (mittel) | Wand_West, Wand_Ost, Wand_Nord (bis 8,6 m), Stuetzen, Tor, Technik | 4096² | 3525 m² | 61 % | **1,85 cm** | 17 018 |
| `fern` | Wand_Oben, Dach, Fachwerk, Strahler, Vorfeld, Schutzwall | 2048² | 6422 m² | 48 % | **5,63 cm** | 25 214 |

Die Belegung von `fern` ist geringer, weil dort tausende kleine Inseln (Fachwerk, Strahler, Ösen) je 2 Texel Abstand brauchen.

### Lichtszenen

Erster Eintrag ist der Standard. Werte aus `LIGHTINGS` (Leistung in Blender-W, Sonne in W/m², Höhe/Herkunft der Sonne:
Azimut 0 = vom Tor, 90 = von Westen); `ambient` gemessen.

| Name | Stimmung | Sonne | Himmel | Strahler (20 × 1 m²) | weitere Lichter | Leuchten | scale | ambient |
|---|---|---|---|---|---|---|---|---|
| `tag` Tag | klare Mittagssonne fällt durchs Tor bis etwa zur Hallenmitte | 7,0, 20° hoch, Az. 22°, `#FFF0D8` | `#9FBAD6` × 1,3 | 320 W `#FFF1DC` | – | Strahler 1,0 | 3 | `#FFF0D6` × 0,157 |
| `abend` Abend | tiefe warme Sonne: lange Streifen durch Tor und Lichtband über Boden und Ostwand | 6,0, 14° hoch, Az. 52°, `#FFAA58` | `#9A90A8` × 0,5 | 200 W `#FFE6C4` | – | Strahler 0,75 | 4 | `#FFD4A6` × 0,123 |
| `nacht` Nacht | nur gedimmte Strahler, rote Notleuchten, blaue Randfeuer, dunkler Himmel | Mond 0,04, 38° hoch | `#1A2438` × 0,1 | 110 W `#FFDDB0` | 5 Notlichter 25 W `#FF3020`, 12 Randfeuer 6 W `#3A70FF` (Punkt) | Strahler 0,4, Notlinsen 6, Randfeuer 8, Fluchtwegschilder 1,2 | 1,5 | `#FFD29D` × 0,052 |
| `bewoelkt` Bewölkt | geschlossene Wolkendecke, weiches Licht durch Tor und Lichtband, keine Schatten | – | `#C3C8CC` × 2,2 | 320 W `#FFF1DC` | – | Strahler 1,0 | 3 | `#FFEFD5` × 0,174 |

Gemessen je Lichtszene (Atlasansicht ↔ Cycles-Render, mittlere Abweichung; Anteil über `scale`):

| Lichtszene | Backen | Entrauschen | gesamt | Abweichung | über `scale` |
|---|---|---|---|---|---|
| tag | 2,8 min | 34 s | 4,2 min | 4,8/255 | ≤ 0,002 % |
| abend | 3,2 min | 33 s | 4,4 min | 3,1/255 | ≤ 0,001 % |
| nacht | 3,5 min | 40 s | 4,9 min | 1,5/255 | ≤ 0,04 % (nur Leuchtlinsen) |
| bewoelkt | 3,7 min | 32 s | 5,0 min | 5,0/255 | ≤ 0,002 % |

### Parcours

Rundkurs, **151 m**, Richtzeit **45 s**. Die Strecke (`course.route`) liegt auf der Lauffläche (z = Boden, Kiste oder Bühne);
Tore und Kontrollpunkte sind Auslösequader. Abschnitt für Abschnitt (Maße aus dem Modul):

1. **Start:** Startpunkt (0, 25), Startportal bei y = 22 (Pfosten x = ±3,65, Auslöser 7 × 0,4 × 2,4 m).
2. **Slalom** (y 20,2 → 5,1, 25 m Zickzack): Gasse 7 m zwischen Absperrgittern (1,1 m hoch, x = ±3,5), vier Kistenhindernisse
   (1,2–2,0 m hoch, nicht überspringbar) bei y = 17,6 / 13,8 / 10,0 / 6,2 abwechselnd an West- und Ostseite, freie Breite
   2,75 m. **Kontrollpunkt 1 „Slalom“** bei y = 4,6.
3. **Mauer** 0,6 m (y 2,6–2,95) **überspringen** (Sprunghöhe 5²/(2 · 16) = 0,78 m).
4. **Kistenberg:** Stufe A 0,6 m, Stufe B 1,2 m (je 0,6 m Sprungstufe), **Kontrollpunkt 2** auf B, 1,2 m **herunterspringen**.
5. Quer zur **Containergasse** an der Westwand (x = −18; 2,68 m zwischen Stützen und Containern).
6. **Ducken** unter der Rohrbrücke (drei Rohre Ø 0,30/0,34/0,30 m quer über die Gasse, Unterkante **1,35 m**; geduckt 1,15 m,
   stehend 1,8 m), Schild „KOPFHÖHE 1,35 M“. **Kontrollpunkt 3 „Ducken“** bei y = −20,5.
7. Am Tor entlang nach Osten (y ≈ −25,5), **Leitwand** 0,6 m bei x = −4 überspringen.
8. **Treppe** (x 9,0–10,2): 12 Steigungen à 0,25 m, Auftritt 0,30 m, auf Bühne P1 (3,0 m). **Kontrollpunkt 4 „Gerüst oben“**.
9. **Laufsteg** 1,2 m breit, 20,4 m lang, Geländer 1,0 m; unterwegs Blick in die Kistenburg.
10. Bühne P2, **Kontrollpunkt 5 „Laufsteg Ende“**, durch die Geländerlücke 1,4 m auf die Absprungkiste (1,6 m) und auf den Boden
    **herunterspringen**.
11. **Ziel:** Zielportal bei y = 19 auf der Ostseite (x 8,45–14,55).

**Automatische Prüfung** (`basic/scenes/__init__.py › course_check`, läuft in `validate` und `./check`): entlang der Strecke alle
0,2 m ein Quadrat 0,7 m bis Kopfhöhe frei von Kollisionsquadern (Durchgang ≥ 0,7 m), Stufen beim Gehen/Treppe ≤ 0,35 m
(CharacterController `stepOffset`), Sprungstufen ≤ 0,75 m, Duckstellen 1,2–1,6 m (gemessen 1,35 m), Streckenpunkte liegen auf
der Lauffläche, Start, Kontrollpunkte in Reihenfolge und Ziel am Ende auf der Strecke, Startpunkt frei, jede Zielscheibe von der
Strecke aus sichtbar (5 Prüfpunkte auf der Scheibe, Augenhöhe 1,62 m bzw. 1,0 m geduckt, Scheibe dem Auge zugewandt).

**Zielscheiben** (`course.targets`, 14; Unity baut die Scheibe, der Hangar liefert Ständer bzw. Rückplatte):

| Ziel | Lage (m) | Höhe | Radius | Sichtbarkeit (geprüft) | nächste Sichtweite |
|---|---|---|---|---|---|
| T01 | Regal Ost (17,8 / 14,0) | 4,2 | 0,30 | frei | 6,8 m |
| T02 | hinter Kiste östlich des Slaloms (6,1 / 11,0) | 1,1 | 0,30 | **Deckung**: höchstens 4/5 Punkte | 4,0 m |
| T03 | Ständer vor dem Kistenberg (−3,0 / −8,0) | 1,5 | 0,30 | frei | 3,1 m |
| T04 | Torpfosten West, Ende der Containergasse | 1,6 | 0,25 | frei (hinter der Rohrbrücke) | 4,9 m |
| T05 | Vorfeld, durchs Tor (2,0 / −42,0) | 1,6 | 0,35 | frei | 16,4 m |
| T06 | Splitterschutzwand Süd (−6,0 / −51,6) | 2,4 | 0,40 | frei, ≈ 26 m | 26,0 m |
| T07 | bodennah am Tor (3,0 / −27,6) | 0,45 | 0,25 | frei | 2,5 m |
| T08 | unter dem Binder (6,0 / −21,0), zeigt nach unten | 11,1 | 0,35 | frei | 7,5 m |
| T09–T11 | in der Kistenburg (x 14,6–17,2, y −11,8…−6,2; Wände 2,0 m) | 1,2–1,3 | 0,30 | **nur von oben** (vom Boden 0/5, vom Gerüst 4–5/5) | 4,8–5,7 m |
| T12 | Ständer unter dem Laufsteg (8,0 / −9,0) | 1,6 | 0,30 | frei (vom Gerüst) | 5,0 m |
| T13 | Nordwand (6,0 / 29,9) | 5,0 | 0,30 | frei | 9,4 m |
| T14 | Regal Ost, oberste Ebene (17,8 / 24,0) | 5,9 | 0,25 | frei | 8,8 m |

Die alte Zielreihe (10/25/50 m) entfällt; `targets` (Schießstand ohne Strecke) ist leer.

**Richtzeit** (`par_time`): Laufen 127,4 m mit 85 % Sprint (5,78 m/s, Kurven) = 22,0 s; Ducken 3,4 m mit 2,4 m/s = 1,4 s;
Treppe, Sprünge und Herunterspringen 20,4 m mit Gehtempo 4,2 m/s = 4,9 s; je Sprung 0,3 s (4) und je Herunterspringen 0,3 s (3)
= 2,1 s; je Ziel 1,0 s für Zielen und Treffen (14 s) → 44,4 s, aufgerundet **45 s**.

## Auslegung des Formats (für den Unity-Lader)

- `colliders[].name` ist die Bauteil-ID (englisch, stabil). Viele kleine sichtbare Teile haben einen gemeinsamen Quader
  (`*_col`: Kiste, Palette, Container, Absperrgitter, Geländer, Treppengeländer). Fachwerk, Strahler, Pfetten, Trassen, Bolzen und
  Bodenmasken haben keinen.
- `lights[].angle_deg` ist nur beim `spot` der Öffnungswinkel; für Sonne, Flächen- und Punktlicht steht 0 (der Blender-Sonnenwinkel
  `blender_angle_deg` bleibt im Szenenmodul).
- `zones[].size` ist die Kantenlänge des quadratischen Atlas, `texel_m` die gemessene Kantenlänge eines Texels in Metern.
- Atlasdateien heißen `<szene>_<licht>_<zone>.png`; jedes FBX-Objekt hat eine UV-Lage (Kanal 0) für den Atlas seiner Zone und
  ein Material `<szene>_<zone>`.
- Die Atlanten enthalten Licht × Grundfarbe (einschließlich Kantenabrieb, Schmutz und Masken), gespeichert als Licht / `scale`.
  Nachts sind Leuchtlinsen über `scale` (≤ 0,04 % der Texel) und werden dort abgeschnitten.
- `course.route` ist die Polylinie auf der Lauffläche (z ≠ 0 auf Kisten und Gerüst); Start- und Zieltor sind verschieden.

## Grenzen

- Glanz fehlt in Unity (Diffus-Atlas); Metall ist darum überall nicht metallisch gemalt.
- Leistung in Unity (≤ 16,7 ms) ist hier nicht gemessen – das misst der Unity-Lader.
- Die PNG-Atlanten sind groß (16 Dateien, zusammen ≈ 205 MB); Unity komprimiert sie beim Import.
- Lichtband offen (ohne Glas): in Unity zeigt es den Himmel; Glas mit Durchsicht passt nicht zur unbeleuchteten Umgebung.
- Schrift ist eine einfache Strichschrift (Großbuchstaben, Ziffern, Ö); Schilder unter ≈ 30 Texeln Höhe bleiben unscharf.
- Ölflecken haben im Atlas keinen eigenen Glanz (nur in der Grundfarbe).
