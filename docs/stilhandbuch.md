# Stil- und Bauhandbuch für BASIC-Waffenvarianten (v2)

Stand 24.10.2026. Verbindliche Anleitung für **jede künftige Waffe oder Variante** im Stil v2 („Destiny-Detaildichte + AAA-Material,
schlicht“). Referenzumsetzung: Pilot `basic/pilot/w01_auto_rifle_v2.py` (Formstudie 01 v2), Vergleichsseite als Artefakt
„Formstudie 01 v2“. Der Designvertrag [designvertrag.md](designvertrag.md) gilt weiter für Maße, Rahmen, Schnittstellen und Grundregeln;
dieses Handbuch ergänzt Detaildichte, Material, Varianten und den Arbeitsablauf.

**Aktuelle Referenz: v2.1** (`basic/pilot/w01_auto_rifle_v21.py`, Ausgabe `BASIC-01-v2.1`); v2 bleibt als Vorstufe erhalten.

## 1 Entscheidungen des Nutzers

| Datum | Entscheidung |
|---|---|
| 24.10.2026 | Eigenes Projekt `cubeescape-ballon` für BASIC |
| 24.10.2026 | Stil: „Mix aus Destiny-Detaildichte und AAA-Look“; Internetrecherche freigegeben |
| 24.10.2026 | Toolgen-Vorgaben (Dreiecksbudgets, Fasen) vorerst ignorieren |
| 24.10.2026 | **„Wichtig ist es schlicht zu halten“** – Leitlinie über allem anderen |
| 24.10.2026 | Farb- und Texturvarianten erwünscht |
| 24.10.2026 | Bloom „ganz weg oder sehr sehr dezent“ → Standard aus |
| 24.10.2026 | „Der graue Hintergrund ist am besten“ → Standard `--bg mid` |

## 2 Gestaltungsregeln v2

1. **Schlicht zuerst.** Qualität kommt aus Silhouette, Schichtung und Material, nicht aus Kleinteilen. Im Zweifel weglassen.
2. **Drei Detailebenen.** Große ruhige Schalen (≈ 60 % der Fläche) · mittlere Gliederung: Fugen, Stufen, Einsätze (≈ 30 %) ·
   feine Akzente gebündelt an Mechanik, Visier und Mündung (≈ 10 %). Keine gleichmäßig verteilten Kleinteile.
3. **Negativraum.** Mindestens eine offene Zone, die Funktion zeigt: skelettierter Schaft, offener Laufraum unter einer Haube,
   Fenster mit sichtbarem Lauf oder Verschluss, Magazin-Sichtfenster.
4. **Schichtung.** Haube, Panzer oder Deckplatte liegen mit 2–3 mm Stufe auf dem Grundkörper; blanke Zierkante (`trim`) nur an
   Stirnkanten und Ringen.
5. **Ein Blickfang.** Genau ein zentrales Element mit Leuchten oder starkem Kontrast (Pilot: Energiekern links, Ego-Seite).
6. **Lesbare Front.** Mündung mehrstufig (Schlitze, Rändel, blanke Krone); Lauf sichtbar oder klar gefasst.

### Mengenbegrenzung je Waffe (Schlichtheitsbudget)

| Element | höchstens |
|---|---|
| Leuchtende Stellen | 3 Funktionen (z. B. Kern, Munitionsanzeige, Visier-Emitter) |
| Grafikelemente der Lackierung | 1 Band (z. B. Chevron über Haube und Seiten) |
| Schriftzüge | 1 (Kennung, z. B. „BASIC AR-01“) |
| Orange-Bedienelemente | 3 Funktionen (beidseitiger Hebel zählt einfach) |
| Schraubbilder | nur an Panzern, Paneelen, Ringen – nie als Füllmuster |
| Glanzeffekt (Bloom) | keiner (Option `--bloom` nur sehr dezent, Schwelle 8, Stärke 0,08) |

Nicht erlaubt: Zähne/Stacheln, sichtbare Federn als Dekor, mehrere Schriften, Seriennummern-Felder, Leuchtstreifen als Schmuck,
gefüllte Rillenmuster, Destiny-Formen/-Namen/-Logos.

## 3 Formsprache-Checkliste je Waffe

Vor dem Bau im Modulkopf festhalten (Docstring), nach dem Bau am Bild prüfen:

| Frage | Pilot (Automatikgewehr) |
|---|---|
| Leitmerkmal der Silhouette | lange Haube, die frei über den Lauf auskragt |
| Schichten | Oberteil → Seitenpanzer → Haube; Deckplatte hinten |
| Negativraum | offener Laufraum mit Kühlrippen und Gaskolben; skelettierter Schaft mit Puffer |
| Blickfang | Energiekern links (Ego-Seite) |
| Zweiton-Blockung | Oberteil/Haube Lack (`shell`), Unterteil und Handschutz Polymer (`graphite`) |
| Grafik | ein Chevronband, ein Schriftzug |
| Front | gerändelter Kompensator mit Schlitzen, kannelierter Lauf |
| Übergänge (v2.1) | Magazintrichter im Unterteil angeformt; Handschutz schmiegt sich unter die Haube (1,5 mm Fuge) |
| Ergonomie (v2.1) | Griff mit Fingerauflagen, Handballenwölbung, ausgestelltem Boden; Magazin leicht gekrümmt |

### Formtechniken (v2.1)

- **Übergänge statt Ansetzen:** Funktionen in das Profil des Trägers einformen (Magazintrichter als Teil des Unterteil-Profils);
  separat bleibt nur, was getauscht wird oder ein anderes Material hat (Einführlippe `trim`).
- **Verjüngen in der Draufsicht:** Form `plan` (Draufsichtprofil, hochextrudiert) plus schräge Schneidkörper für die Seitenansicht
  (Pilot-Handschutz: Draufsicht vorn schmaler, Unterkante vorn schräg).
- **Ergonomische Konturen** über eine Hilfsfunktion entlang der Griffachse (`_A(u, d)`), Fingerauflagen als Wechsel von 17/21 mm.
- **Krümmungen** als Versatzfunktion (`_cv(u)`), auf Körper, Rillen, Fenster und Patronen gleich angewandt.
- **Verjüngte Hauben** aus `multi`: zwei Seitenwände und eine geneigte Deckplatte, vorn eine blanke Rahmenkante.

## 4 Materialrollen

| Rolle | Standardfarbe | Oberfläche (AAA-Modus) | Einsatz |
|---|---|---|---|
| `shell` | Creme | satinierter Lack, Kantenabrieb, Schmutz in Vertiefungen, feine Kratzer | Schalen, Hauben, Panzer |
| `graphite` | sehr dunkles Polymer | matt, Specular 0,25, feines Relief, Abrieb 0,15 (dezent) | Unterteil, Handschutz, Griffzonen |
| `rubber` | schwarz | Stippling (Voronoi-Relief), Specular 0,2 | Griff, Polster, Schaftkappe |
| `anodized` | Schwarz eloxiert | halbmatt metallisch, leichter Abrieb | Paneele, Klemmungen, Kappen |
| `dark_metal` / `metal` | Brüniert / Stahl | metallisch, Rauheitsvariation | Lauf, Kühlrippen, Mechanik |
| `trim` | blankes Metall | anisotrop poliert | Zierkanten, Ringe, Schrauben |
| `accent` | Orange | Lack mit Abrieb | Bedienelemente, Chevronband |
| `energy` | Cyan | Emission | nur die drei Leuchtfunktionen |
| `brass`, `decal`, `glass` | Messing, Hellgrau, beschichtet | – | Patronen, Schrift/Linien, Gläser |

Umsetzung: `basic/kit.py › MATERIALS`, Shader `aaa_nodes` (Bevel-Kantenmaske mit 4 mm Messradius, AO-Schmutz, gestreckte Kratzer,
Mikrorelief je Rolle).

## 5 Farb- und Texturvarianten (Skins)

Skins ändern **nur** Farben und Oberflächen der Materialrollen; Form, Bauteile, Anker und Mechanik bleiben identisch.

| ID | Name | Art | Kern |
|---|---|---|---|
| `standard` | Standard | Farbe | Creme / Polymer / Orange |
| `nacht` | Nachtschicht | Farbe | Anthrazit-Lack, mehr Abrieb |
| `polar` | Polar | Farbe | Weiß, graues Polymer, Cyan statt Orange, wenig Abrieb |
| `kobalt` | Kobalt | Farbe | Marineblau / Schwarz / Orange |
| `wueste` | Wüste | Farbe | Sand / Oliv / Ziegelrot |
| `tarnung` | Tarnung | Textur | dreifarbiges Flächenmuster auf `shell` |
| `gebraucht` | Gebraucht | Textur | starker Abrieb, Schmutz, vergilbter Lack |
| `eloxal` | Eloxal | Textur | `shell` wird metallisch eloxiert (Blaugrau) |

**Neuen Skin anlegen:** Eintrag in `basic/kit.py › SKINS` mit `de`, `kind` (`Farbe`/`Textur`), `roles` (Rolle → Hex), optional
`wear` (Faktor Abrieb), `grime` (Faktor Schmutz), `pattern` (drei Hex-Farben), `metal_shell`. Regeln: höchstens drei Hauptfarben;
Orange/Cyan behalten ihre Funktion (Bedienung/Leuchten); Kontrast zwischen `shell` und `graphite` muss in der Silhouette lesbar bleiben.
Rendern: `--skins name1,name2` (Hauptansicht und linke Seite je Skin → `views/skin_<id>_<ansicht>.png`).

## 6 Baukasten (Kurzreferenz)

Autorenmaß mm: `f` vorn, `u` oben, `x` links; Ursprung `Socket_Hand`. Formen (`shape`):

| Form | Zweck | Wichtige Felder |
|---|---|---|
| `prof` / `box` | Seitenprofil quer extrudiert / Quader | `pts` bzw. `f0 f1 u0 u1`, `w`, `x` |
| `cyl` | Zylinder, Rohr, Kegel, Ring | `axis` (`f`/`x`/`u`), `c`, `a0 a1`, `r`, `r1`, `r_in`, `segs` |
| `plan` | Draufsicht-Profil (liegende Decals, Bänder auf Oberseiten) | `pts` (f,x), `u0 u1` |
| `frame` / `xbox` | Rahmen oder Platte quer zur Laufachse | `cu`, `ow oh`, `iw ih`, Radien |
| `multi` | mehrere Formen als ein Bauteil (Schrauben, Rippen) | `items` |
| `tube` | Leitung entlang Polylinie | `path` [(f,u,x) …], `r` |
| `text` | Schriftzug als Geometrie | `text`, `size`, `f u x`, `side` (+1 links, −1 rechts, 0 oben) |

Weitere Felder: `cuts` (Durchbrüche/Fugen, Exact-Boolean, sofort angewandt), `bevel` (Stufen R_BODY 5 · R_MID 3 · R_SMALL 1,5 · R_FINE 0,8),
`parent_part` (folgt beweglichem Elternteil), `move` (`translate`/`rotate`/`segment`/`glow`, Drehsinn siehe `kit.py`, `expect` für den
Test), `removable`, `iface`. Gemeinsame Bausteine in `basic/common.py` (Griffmodul, Schiene, Visiere, Magazin, Lauf, Schäfte, Zelle).

## 7 Arbeitsablauf für eine neue Waffe oder Variante

1. **Recherche (beobachtet, nicht kopiert).** Bildersuche „destiny 2 legendary <typ> light.gg“; im Browser-Fenster die Original-
   Renderings von Bungie über die Treffer-Metadaten holen:
   `[...document.querySelectorAll('a.iusc')].map(a=>JSON.parse(a.getAttribute('m')).murl).filter(u=>u.includes('screenshots'))`
   → `bungie.net/common/destiny2_content/screenshots/<id>.jpg`. Zwei bis drei gewöhnliche Legendary-Vertreter ansehen, Prinzipien
   in `docs/quellen.md › Q-D2-IMG` eintragen (Waffe, Typ, URL, beobachtetes Prinzip). Keine Bilder ins Repo.
2. **Checkliste (Abschnitt 3)** im Modul-Docstring ausfüllen; Schlichtheitsbudget (Abschnitt 2) einplanen.
3. **Modul bauen:** neue Waffe als `basic/weapons/wNN_*.py`; Neugestaltung einer bestehenden zuerst als `basic/pilot/…` mit
   `META['variant']` (eigener Ausgabeordner, Reihe bleibt unberührt).
4. **Rendern (GPU-Sperre):**
   `~/Claude/cubeescape-nexogen/ce lock gpu -- /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P tools/blender_build.py -- <modul> --views --aaa --gpu --samples 128 --res 1600 --skins standard,nacht,polar,kobalt,wueste,tarnung,gebraucht,eloxal`
   (Schnelldurchlauf: `--only hero,hero_p,side_left,ego --samples 64`).
5. **Sichten in Runden** (meist drei): Silhouette und Zweiton → Schichten und Negativraum → Material und Schlichtheitsbudget.
   Je Runde Hauptansicht, linke Seite, Ego-nah, Explosion; zusätzlich Visierlinie (`sightline.png`) und bei Hohlformen eine
   Volumenprüfung (Blender, `bmesh.calc_volume`).
6. **Mechanik:** `move.expect` für jede Drehung, `./check` (enthält den Drehsinn-Test), Bildfolgen mit `--motion`, Sichtung in
   `data/review.json` eintragen (nur „geprüft“, was im Bild stimmt).
7. **Doku und Blätter:** `tools/sync_specs.py`, `tools/make_docs.py`, `tools/make_sheets.py` (Pilotvergleich: `--pilot <datei>`),
   Bericht in `docs/versions/`.

## 8 Rendern

| Modus | Einsatz | Einstellungen |
|---|---|---|
| Illustration (Standard) | Konstruktionsblätter, Kontaktbögen | Cycles, Freestyle-Kontur, flache Farben, transparenter Grund |
| AAA (`--aaa`) | Produkt- und Stilprüfung, Skins | Cycles GPU, AgX „Medium High Contrast“, Key 170 W / Fill 40 W / Rim 320 W / Top 60 W, Hintergrund siehe `--bg` (Standard mittelgrau), Umgebungslicht 0,35–0,55, ohne Kontur, **ohne Bloom** |
| Produktansicht `hero_p` | Hauptbild | Perspektive 70 mm aus der Hauptrichtung |
| Hintergrund `--bg` | Sichtprüfung | `dark` (Inspektionsbild), `mid` (**Standard**, Grau `#4C525A → #9EA4AC`, Creme und Schwarz gleich gut lesbar), `light`; Vergleichsläufe mit `--tag` in eigenen Ordner `views_<tag>` |

## 9 Typische Fehler

- Exact-Boolean mit überlappenden Schneidkörpern ohne `use_self` → leeres Netz (wird jetzt als Fehler gemeldet).
- Aus Kurven/Text erzeugte Netze bringen einen leeren Materialslot mit → `materials.clear()` vor dem Zuweisen.
- Kantenmaske misst kleiner als die Modellfase → kein sichtbarer Abrieb (Messradius ≥ 4 mm).
- Mit 4 mm Messradius werden dunkle Teile auf Grau kreidig → Abrieb für `graphite` 0,15, `anodized` 0,3, `dark_metal` 0,25.
- Schwarzes Polymer mit Specular 0,5 wirkt grau → 0,2–0,25.
- Bloom mit niedriger Schwelle lässt helle Lackflächen glimmen → aus.
- Teile auf der linken Seite (Anzeigen, Kern) sind in der Standardkamera (rechts vorn) unsichtbar → Aktion mit `view` von links rendern.
- Schneidkörper, die eine Fläche ganz durchtrennen (Fugen, Griffrillen), teilen das Bauteil → Fugen als 1 mm tiefe Nuten je Seite.

## 10 Stand

Pilot Formstudie 01 v2.1 fertig (70 Teile, 32 694 Dreiecke, 8 Skins, grauer Hintergrund); v2 als Vorstufe erhalten. Die 16 übrigen Waffen sind im Stil v1; Übertragung nach Freigabe
des Nutzers nach diesem Handbuch. Toolgen-Anbindung des v2-Stils (Budgets, Fasen, Texturen) ist offen und bewusst zurückgestellt.
