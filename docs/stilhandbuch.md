# Stil- und Bauhandbuch für BASIC-Waffenvarianten (v2)

Stand 24.10.2026. Verbindliche Anleitung für **jede künftige Waffe oder Variante** im Stil v2 („Destiny-Detaildichte + AAA-Material,
schlicht“). Referenzumsetzung: Pilot `basic/pilot/w01_auto_rifle_v2.py` (Formstudie 01 v2), Vergleichsseite als Artefakt
„Formstudie 01 v2“. Der Designvertrag [designvertrag.md](designvertrag.md) gilt weiter für Maße, Rahmen, Schnittstellen und Grundregeln;
dieses Handbuch ergänzt Detaildichte, Material, Varianten und den Arbeitsablauf.

**Aktuelle Referenz: v2.1** (`basic/pilot/w01_auto_rifle_v21.py`, Ausgabe `BASIC-01-v2.1`); v2 bleibt als Vorstufe erhalten.

**Namen (Nutzer 25.10.2026, Wahl (a)):** Versionen zählen getrennt. **Stil v2.1** ist der Waffenstil (Form, Material, Budget).
**Visier-Standard 3** sind die Visierregeln in §6 (Stufe 1: Höhe 66 ± 4 mm, Stufe 2: schlanke Visiere, Stufe 3: REF 0.14
„Eyebox“); früher „Visier-Designsprache v3“, in Code-Kommentaren von `common.py`/`kit.py` weiter kurz „v3“. **Arm v3** ist das
Arm-Rig. Ein Waffenstil v3 existiert nicht.

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
| 24.10.2026 | Visier-Standard: Visierhöhe 66 ± 4 mm, Augenpunkt, Zoom, Prüfung in `./check`; nach „Visiere sehr klobig“ (Destiny-Video, Motiongen) als v2: Augenpunkt 90 mm vor der Öffnung, Modell ungezoomt, Weltzoom je Klasse, schlanke Visiere |
| 24.10.2026 | Absehen-Katalog mit Formen, Farben, Linienstärken, Glasvarianten, Aufgehen und Spieleroptionen; „Pfeil von unten“ verworfen |
| 25.10.2026 | Visier-Standard 3 (anfangs „Visier-Designsprache v3“) nach Motiongen REF 0.14 „Eyebox“: „Mach alles so wie du empfiehlst“ (Augenpunkt bleibt 90 mm, kleinere Öffnungen; Impuls bleibt Holo) |
| 25.10.2026 | Kein Waffenstil v3: Familie bleibt im Stil v2.1, nur die Namen werden geklärt (Wahl (a) auf „Warum wird nicht erst v3 gemacht?“); weiter mit der Maschinenpistole |
| 26.10.2026 | Portalkanone BASIC-T01 (0.17 „Gateway“): Werkzeug mit eigener Silhouette statt Familienkörper; nur Hüfte mit Kerbe als Leitkante, kein Visier; zwei Portalfarben (vorn Cyan = Portal A, hinten Orange = Portal B), Bedienelemente neutral; nach Skizze A „Ring“ der Wunsch „mehr an der Portal-2-Portalgun orientieren, nur im BALLON-Stil“ → Skizze P2 „Ei und Ring“ (facettierte Eischale, offener Zweifarbkern, Ring fest auf Speichen, dreht je Schuss 120°); „am Abzug sind die Teile in der Luft“ → Spalte gemessen und geschlossen |

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
- **Speichen um die Schussachse:** `tube` mit zwei Punkten, berechnet aus Winkel und Radius (`_spoke` in BASIC-T01) – `box`/`prof` lassen sich nicht um f drehen; Speichen, Nabe und Marke als `parent_part` am drehenden Ring.
- **Verjüngte Hauben** aus `multi`: zwei Seitenwände und eine geneigte Deckplatte, vorn eine blanke Rahmenkante.

## 4 Materialrollen

| Rolle | Standardfarbe | Oberfläche (AAA-Modus) | Einsatz |
|---|---|---|---|
| `shell` | Creme | satinierter Lack, Kantenabrieb, Schmutz in Vertiefungen, feine Kratzer | Schalen, Hauben, Panzer |
| `graphite` | sehr dunkles Polymer | matt, Specular 0,25, feines Relief, Abrieb 0,15 (dezent) | Unterteil, Handschutz, Griffzonen |
| `rubber` | schwarz | Stippling (Voronoi-Relief), Specular 0,2 | Griff, Polster, Schaftkappe |
| `anodized` | Schwarz eloxiert | halbmatt metallisch, leichter Abrieb | Paneele, Klemmungen, Kappen |
| `sight_anod` | Schwarz eloxiert | wie `anodized`, feines Relief, Kantenabrieb mit 1,2 mm Messradius (dünne Teile bleiben dunkel), keine Kratzer | alle Visierteile (0.21) |
| `dark_metal` / `metal` | Brüniert / Stahl | metallisch, Rauheitsvariation | Lauf, Kühlrippen, Mechanik |
| `trim` | blankes Metall | anisotrop poliert | Zierkanten, Ringe, Schrauben |
| `accent` | Orange | Lack mit Abrieb | Bedienelemente, Chevronband |
| `energy` | Cyan | Emission | nur die drei Leuchtfunktionen |
| `brass`, `decal`, `glass` | Messing, Hellgrau, beschichtet | – | Patronen, Schrift/Linien, Gläser |
| `reticle_<farbe>`, `sight_line` | Cyan (Familie) | reine Emission 0,6 | gezeichnetes Absehen; Leuchtkontur am Visier (H2), die Unity nicht wie ein Absehen ausblendet |

Umsetzung: `basic/kit.py › MATERIALS`, Shader `aaa_nodes` (Bevel-Kantenmaske mit 4 mm Messradius, `WEAR_RADIUS` je Rolle, AO-Schmutz, gestreckte Kratzer (`SCRATCH` je Rolle),
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
| `xprof` | Querprofil um die Visierlinie, entlang der Laufachse extrudiert (Visier-Baukasten v3: Hauben, Sockel, Glas, Absehen) | `pts` [(x,u) …] relativ zu `cu`, `f0 f1`; Durchbrüche als `cuts` mit `xprof` |
| `multi` | mehrere Formen als ein Bauteil (Schrauben, Rippen) | `items` |
| `tube` | Leitung entlang Polylinie | `path` [(f,u,x) …], `r` |
| `text` | Schriftzug als Geometrie | `text`, `size`, `f u x`, `side` (+1 links, −1 rechts, 0 oben) |

Weitere Felder: `cuts` (Durchbrüche/Fugen, Exact-Boolean, sofort angewandt), `bevel` (Stufen R_BODY 5 · R_MID 3 · R_SMALL 1,5 · R_FINE 0,8),
`parent_part` (folgt beweglichem Elternteil), `move` (`translate`/`rotate`/`segment`/`glow`, Drehsinn siehe `kit.py`, `expect` für den
Test), `removable`, `iface`. Gemeinsame Bausteine in `basic/common.py` (Griffmodul, Schiene, Visiere, Magazin, Lauf, Schäfte, Zelle).

**Familienbausteine v2.1** (`basic/common.py`; Maße in mm, `f` vorn, `u` oben, Ursprung `Socket_Hand`). Gemessene Lagen und
Größen der fertigen Familie stehen in [familienmasse.md](familienmasse.md) (erzeugt aus den Specs) – dort die ähnlichste Klasse als
Startpunkt nehmen.

| Baustein | Liefert | Wichtige Parameter | Genutzt in |
|---|---|---|---|
| `grip_v21(top)` | Griff mit Fingerauflagen und Griffboden, Abzug, Abzugsbügel (`anodized`) | `top` = Griffoberkante (Unterkante Unteres Gehäuse); Griffachse um 15° nach hinten geneigt, f = u·tan 15° + Versatz | 02, 03, 06 (01 inline) |
| `reflex_sight_v21(f, u, ww, wh, …, weapon_type)` | **H0 „Referenz“** (Baukasten v3): offene Haube auf der H0-Plattform, Glas ww × wh, gezeichnetes Absehen; gibt `(Teile, Anker)` zurück | `f` Hinterkante Klemmfuß, `u` = Schienenoberkante | 01 |
| `holo_kasten(f, u, size, weapon_type)` | **H4 „Kasten“** (Impuls): Haube mit runden Dachecken, Seiten einwärts, Ziffernfeld im Sockel | `size` S/M/L (`HOLO_SIZES`, L nur MG/Werfer) | 02 |
| `holo_pille(f, u, size, weapon_type)` | **H2 „Pille“** (MP): ohne Haube, Emitterblock mit Statuspunkten, Pillenkontur gezeichnet (Rolle `sight_line`) | `size` S/M/L | 06 |
| `scope_tropfen(f_obj, u, cu, size, weapon_type, seat_u, saddle_f)` | **Z1 „Tropfen“** (Scout), Sitz nach Konzept A: Wiege hinter dem Auge (`scope_saddle`), H0-Klemmfuß unter dem Objektiv (`scope_foot`), Ring ohne Wulst (`scope_ring`, außen/innen 1,29), Tropfensockel, zweistufiges Objektiv | `f_obj` Ringstirn, `cu` Visierlinie, `seat_u` Schiene unter dem Sattel, `size` S/M/L (`SCOPE_SIZES`, S Variante) | 03 |
| `sight_platform`, `sight_hood`, `sight_glass_x`, `xprof`, `scope_body` | Bausteine der übrigen Visiere: H0-Plattform (Klemmfuß 46 × 23/18, oranger Hebel, Gehäuse, Trapezsockel), Flachprofil-Haube (Stirn 1,6 mm) mit blanker Stirnkante, flache Scheibe | Katalog und Entwürfe: `basic/pilot/optics/sight_kit.py`, Blatt `tools/sight_catalog.py` | über Visiere |
| `drawn_reticle(f, cu, weapon_type, dist)` | gezeichnetes Absehen: Hüftform der Klasse in Hüftgröße, flach in der Glasebene, Linien ≥ 1,6 px, reine Emission | `dist` Abstand zum Augenpunkt | über Visiere |
| `box_scope_v21(f, u, style)` | Kastenoptik (`prism`/`flat`) – nur als Entwurf | `style` | – |
| `reticle(f, cu, kind, …)` | Absehen als Röhrenform (Katalogblatt `reticle_sheet.py`) | `kind`, `color`, `weight` | Katalog |
| `rifle_mag(f_well, u_top, depth, length, tilt, w, curve)` | Magazin, Boden, oberste Patrone; Entnahme entlang der Magazinachse | `tilt` > 0 unten nach vorn; im Griff (06): `tilt=-15` und Mitte auf der Griffachse | 01, 02, 03, 06 |
| `rail(f0, f1, u)` | Schiene BRI-22 | Rillen per `cuts` im Modul (Material `anodized`) | 01, 02, 03, 06 |
| `selector(f, u, x)` | Feuerwahlhebel (Akzent); rechts als Kopie mit `id='selector_r'`, `x` negativ | `x` = Seitenfläche + 1,5 mm | 01, 02, 03, 06 |
| `charging_handle(f, u, x, travel)` | Ladehebel (Akzent) mit Bewegung `charge` | `travel` Weg nach hinten | 01, 02, 03, 06 |
| `stock_s1(f0, ua, s, cheek)` | Schaft S1: Verbindung, Rohr, Schulterstütze, Kappe | `f0` Gehäusehinterkante, `ua` Laufachse, `s` Längenfaktor (06: 0,72, ohne Wange) | 06 (01 inline) |
| `stock_s2(f0, ua, s)` | Schaft S2 einteilig (Energie/Impuls) | wie S1 | 02 und 03 bauen S2 inline (Daumenloch, Wange) |
| `prof` / `box` / `cyl` | Bauteil mit allen Pflichtfeldern | siehe Formen oben | alle |
| `cut_box(f0, f1, u0, u1, w, x)` | Schneidkörper für `cuts` (Fenster, Schlitze, Nuten) | quer durch: `w` breiter als das Teil | alle |
| `screws(pts, x)` + `mirror(items)` | Schraubenköpfe auf einer Seite, gespiegelt auf beide | nur an Paneelen, Panzern, Ringen (Budget) | alle |
| `rot(pts, c, deg)` | dreht (f,u)-Punkte um `c`; für Fenster und Patronen in geneigten Magazinen gleich wie der Körper | positiv = unteres Ende nach vorn | 01, 02, 03, 06 |

**Muster im Waffenmodul:**
- *Variante einer Reihenwaffe:* `basic/pilot/wNN_<typ>_v21.py`, `META = dict(V1.META, variant='v2.1', …)`, `ASSEMBLIES = V1.ASSEMBLIES`,
  Aktionen aus V1 übernehmen oder neu schlüsseln; Ausgabe `BASIC-NN-v2.1`.
- *Familienteil anpassen:* Teile aus einem Baustein nach dem Aufruf in `P` per `id` suchen und mit `p.update(...)` oder
  `dict(p, ...)` ändern (06: Abzugsbügel dicker als Band zum Bügel, Punkte aus `grip_rifle(top)` berechnet; Magazin: `de`, `func`,
  `cuts`, Material). Feste Zahlen nur, wenn sie aus den Baustein-Formeln berechnet sind.
- *Sichtfenster mit Inhalt:* Fenster als `cuts` im Träger, Inhalt als eigenes `multi`-Teil mit `parent_part` (02, 06: Patronen;
  02: Spulen), damit es der Bewegung folgt.
- *Werkzeug der Familie* (`basic/pilot/tNN_<typ>_v21.py`, ID `BASIC-TNN`, Ausgabe `BASIC-TNN-v2.1`): `grip_v21` und Materialrollen wie die Waffen, kein Visier und kein `Socket_Eye`, keine Orange-Bedienelemente, wenn Orange eine Funktion hat (Portal B). Eigene Leuchtrollen im Modul (`PORTAL_ROLES`), solange `kit.py` im Unity-Quellenhash liegt; Aufleuchten beim Schuss als Laufzeitangabe (`FLASH`). `./check` prüft Werkzeuge in einem eigenen Block, die Familienmaße führen sie unter „Werkzeuge“.
- *Anker:* `ANCHORS` mit `Socket_Hand`, `Socket_SupportHand`, `Socket_Muzzle`, `Socket_MagWell`, `Socket_Charge`; die Visieranker
  kommen aus dem Visierbaustein (`ANCHORS.update(SIGHT_ANCHORS)`). `./check` vergleicht die Anker mit dem Spec.

### Absehen und Visierglas

Katalog in `basic/reticles.py` (eine Quelle), Übersicht [absehen.md](absehen.md) (erzeugt), Laufzeitdaten `data/reticles.json`
(`tools/export_reticles.py`), Katalogblatt und Aufgeh-Clip `tools/reticle_sheet.py`.
- Jedes Visier hat ein **gezeichnetes Absehen** (0.21, Nutzer 26.10.2026 „lieber etwas Gezeichnetes … das Fadenkreuz … vom
  Hüftfeuer im Visier“): `drawn_reticle` legt die Hüftform der Klasse flach in die Glasebene, wie Unity sie zeichnet; die Röhrenform
  (`reticle`, `DEFAULTS[type]['optic']`) bleibt nur für das Katalogblatt.
- Sieben Formen, fünf Farben, drei Linienstärken; jede Form in jeder Farbe und Stärke. Farben sind eigene Leuchtrollen
  (`reticle_<farbe>`): reine Emission (`emit_only`, Grundfarbe schwarz) mit Stärke 0,6 – mit beleuchteter Grundfarbe oder
  höherer Stärke wirken sie pastellig (Test im Blender per MCP, 24.10.2026).
- Glas klar als Standard; Staub, Kratzer, Riss, Zellen, Benutzt nur dezent (höchstens +0,38 Deckkraft an der Maske).
- Aufgehen beim Schießen und Spieleroptionen sind Laufzeitverhalten: im Modell steht der Ruhezustand, die Profile stehen in
  `SPREAD`, die Optionen in `SETTINGS`.
- **Visier-Standard 3** (`reticles.SIGHT`, `SIGHT_KIND`, `ADS_FEEDBACK`; Übersicht [absehen.md](absehen.md); Nutzer
  25.10.2026 „Mach alles so wie du empfiehlst“; Grundlage Motiongen REF 0.14 „Eyebox“, `cubeescape-reference/docs/visiere.md`):
  1. **Typ je Klasse, Farbe nach Familie:** Automatik, MP, Spur, MG, Impuls → offenes Holo; Scout, Lineare Fusion → kurzes
     Ring-Zielfernrohr; Handfeuerwaffe, Seitenwaffe, Schrot → Kimme/Korn mit Leuchtklammern; Scharfschütze →
     Zielfernrohr außen, im Zielen Vollbild; Fusion → Ring/Doppelring; Werfer → runde Linse mit Winkel; Kastenoptiken nur als Variante.
     **Baukasten v3** (0.21 „Ironsight“, Nutzerwahl „v3 bauen“, [visier-konzept.md](visier-konzept.md) › 4/6a): alle Visiere auf der
     H0-Plattform, je Visier nur Rahmenkontur und höchstens ein Funktionsdetail; Standard je Typ nach § 6a (Automatik H0, Impuls H4,
     Scout Z1, MP H2 gebaut; die übrigen als Entwurf in `sight_kit.py`).
  2. **Rahmen:** Holo ≤ 0,10 × Öffnung (Bügel 1,6 mm, Dach 1,2 mm), Ring ≤ 0,15 × Öffnung. „Klobig“ kommt von großen, hohen
     Gehäusen und Block-Sockeln.
  3. **Öffnung im Zielen** bei 90 mm Augenabstand (Standard; Spieleroption `ads_eye_relief` 70/90/110 mm, Nutzerwunsch: 70 mm
     optional) und 75° Bezugsbildwinkel: Holo 12–20 %, Zielfernrohr 20–26 % der Bildbreite
     (Holo-Fenster 26 × 20 mm, Objektivlinse Ø 28 mm), gemessen als lichte Öffnung im echten Abstand; zugelassene Varianten mit
     Grenzen: Holo L bis 25 % nur an MG und Werfern, Zielfernrohr S ab 17 %; `./check` prüft Anteil, Höhe 66 ± 4 mm und Augenabstand,
     `tools/test_sights.py` jedes gebaute Visier in S/M/L. **Visierlinie:** Schiene + 26 mm (Holo auf der H0-Plattform; Zielfernrohre nach
     Konzept A haben zwei Schienen auf eigener Höhe und richten sich nur nach der Visierhöhe 66 ± 4), Mini-Reflex
     Schiene + 15 mm, Kimme/Korn Schiene + 11 mm (≈ 51 mm über dem Lauf; dort gilt die Visierhöhe nicht).
  4. **Eine Kamera:** das Glas zeigt dasselbe Weltbild (kein eigenes Linsenbild); Waffenmodell ungezoomt, Weltzoom je Klasse als
     Bildmaßstab; Zielfernrohr-Rohr, Okular und Türme `ads_hide`.
  5. **Sockel:** gestuftes Trapez bis zur Fensterunterkante (nichts schwebt), Anzeigen unter der Visierlinie. Zielfernrohr nach
     **Konzept A** (Entscheidungsliste 1.1, Antwort 26.10.2026 „v3 bauen“): Rohr liegt hinten in einer Wiege auf einem Gehäusebuckel
     **hinter dem Auge**, vorn trägt ein H0-Klemmfuß den Sockel unter dem Objektiv – zwischen Auge und Objektiv nichts im unteren
     Bilddrittel; Ring ohne Wulst (Objektiv als Kegel zum Auge, außen/innen 1,29). Visier über Gehäuse 0,02–0,04 L;
     `tools/test_sight_seat.py` prüft Auflage, Sattel hinter dem Auge und das freie Zielbild am Netz.
  6. **Absehen:** Standard fein, im Zielen kein Aufgehen; Leuchtpunkt am Zielpunkt getrennt vom Glas, Schuss = kurzer Ring,
     Treffer = X (Laufzeit, `ADS_FEEDBACK`).
  7. **Glas:** Tönung ≤ 5 %, Gebrauchsspuren nur am Rand (≤ +0,15 Deckkraft), Mitte klar.
  8. **Farbe:** Gehäuse neutral mit einem Akzent; Visierteile in der Rolle `sight_anod` (eloxiert, Kantenabrieb mit 1,2 mm
     Messradius, ohne feine Kratzer – Nutzerwahl A zur Abriebmaske, 0.21); Absehen in Familienfarbe Cyan.
- Neue Form: Grundelemente mit Spreizrichtung in `RETICLES` ergänzen, `export_reticles.py` und `reticle_sheet.py` laufen lassen,
  Katalogblatt sichten.

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
7. **Doku und Blätter:** `tools/sync_specs.py`, `tools/make_docs.py`, `tools/make_sheets.py` (Pilotvergleich: `--pilot <datei>`,
   Familienseite: `--family <datei>`), Bericht in `docs/versions/`.

**Dokumentationspflicht je Waffe** (abhaken, bevor die Waffe als fertig gilt; `./check` prüft die mit ✓ markierten Punkte):
- [ ] Recherche: 2–3 Vertreter in `docs/quellen.md › Q-D2-IMG` (Waffe, Typ, URL, beobachtetes Prinzip; was nicht übernommen wurde und warum)
- [ ] ✓ Modul-Docstring: Recherche-Kurzfassung, Checkliste §3 als Tabelle, Schlichtheitsbudget gezählt, Status der Maße
- [ ] Neue gemeinsame Bausteine in `basic/common.py` und hier in §6; neue Formtechniken in §3
- [ ] ✓ Sichtung: Ansichten (`static`) und jede Aktion in `data/review.json` (Methode, Datum, Befund)
- [ ] Belege außerhalb des Repos (Ansichten, Skins, Bildfolgen), Pfade im Bericht
- [ ] Lehren als je eine Zeile in `docs/LESSONS.md`; Typische Fehler in §9
- [ ] Bericht `docs/versions/<version>.md` (Runden, Befunde, offene Punkte, Belege) und CHANGELOG
- [ ] Abweichungen vom Designvertrag nur mit Nutzerentscheidung (in §1 eintragen)

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
- Reflexvisier ohne Absehen: der Emitter allein zeigt keinen Zielpunkt → `reticle()` auf die Scheibe (Nutzerhinweis 24.10.2026).
- Zielfernrohr mit massivem Mittelrohr: Absehen unsichtbar, kein Durchblick → Rohr hohl (`r_in`), Visierlinie prüfen.
- Visiere wirken klobig, wenn Rahmen dick sind und das Waffenmodell beim Zielen mitgezoomt wird → dünne Bügel, Modell ungezoomt,
  Augenpunkt 90 mm vor der Öffnung; beim Zielfernrohr ohne `ads_hide` blickt man in einen Tunnel aus Ringen und Okular; ein Fuß
  zwischen Auge und Objektiv ragt als Klotz in die Linse.
- Fenster in massiven Profilen bleiben Mulden: für sichtbare Innenteile quer durchschneiden (Schneidkörper breiter als das Teil).
- Schneidkörper, die eine Fläche ganz durchtrennen (Fugen, Griffrillen), teilen das Bauteil → Fugen als 1 mm tiefe Nuten je Seite.
- Helle Markierung (`decal`) auf Creme verschwindet: Schrift und Marken auf Graphit legen oder dunkel (`anodized`) ausführen (BASIC-T01, Runde 1).
- Teile am Abzug „in der Luft“: Bauchunterkante muss gerade über den ganzen Abzugsbügel laufen (f ≈ 83 mm bei `grip_v21(top=40)`); der Bügel beginnt 2,7 mm vor dem Griff – Spalte am gebauten Modell messen (BVH-Abstand je Teilpaar), nicht schätzen (BASIC-T01).
- Leuchtende Flächen (Kammerkerne) mit beleuchteter Grundfarbe wirken pastellig wie dünne Linien: `emit_only`, Stärke 1,2 für Orange, 0,7 für Cyan (helles Cyan bleicht unter AgX sonst zu Weiß; BASIC-T01).
- Magazin im Griff neben die Griffachse gesetzt steht hinten aus dem Griff und versteckt sein Sichtfenster → Magazinmitte auf
  der Griffachse von `grip_v21` (f ≈ u·tan 15°), Fenster in den Teil unter dem Griffboden (BASIC-06 v2.1).

## 10 Arme und Animation

Getrennt von Toolgen und Cube Escape (Nutzer 24.10.2026: „so wie die Waffen, möglichst separat halten“). Übersicht und Status je
Aktion: [ego.md](ego.md) (erzeugt). Ergebnisseite als Artefakt „BASIC Ego-Animationen“.

| Baustein | Datei | Inhalt |
|---|---|---|
| Arm-Rig v3 | `basic/arms/robot_arm.py` | Oberarm, Medaillon-Ellbogen, Unterarm (Graphitkörper mit Wölbung, Cremeschale mit Pfeilschnitt, dunkle Handgelenkplatte mit zwei Bolzen, eine Akzentlinie, Stulpe), Kardan-Handgelenk, Hand (Handfläche, Rückenschale mit Grat, Knöchelschutz), **vier Finger** und Daumen mit je drei Gliedern; `ARM_BULK`/`HAND_BULK`; Fingerstellungen `FINGER_POSES`; Längen aus Toolgen mit Quelle. v1 als Vorstufe in `robot_arm_v1.py` |
| Formen | `tools/ego_build.py` | `box`, `cyl` (Achse x/y/z), `prism` (Achteck), `plate` (Facettenplatte mit Grat), `hull` (konvexe Hülle aus Querschnitten `section`/`section_top`; Pfeilschnitt über abweichendes z der Deckfläche) |
| Arm-Vorschau | `tools/arm_preview.py` | rechter Arm ohne Waffe: Seite, schräg, Hand offen, Faust; `--rig v1\|v2`, `--k` (Querschnitt testen) |
| Roboter (Spaß) | `basic/arms/robot_figure.py`, `tools/robot_build.py` | ganze Figur in derselben Formsprache, Arme v3 per IK an der Pilotwaffe; keine Spielfigur |
| Ego-Daten | `basic/arms/ego.py` | Kamera (75° h), Haltungen `POSES` (Socket_Hand, Zielpunkt, Rollen; `ads` über Socket_Eye), Griffe `GRIPS` (Handfläche auf der Oberfläche, Fingerrichtung, Teil), Aktionen `ACTIONS` (Kanäle unten), Matrixzuordnung `ROWS` |
| Szene und Render | `tools/ego_build.py` | baut Waffe und beide Arme, löst je Bild Haltung, Hände, Arme, Finger, Mechanik, Magazin, Rückstoß, Kamera-Feedback; `--stills`, `--actions all`, `--gpu` |
| Belege und Doku | `tools/make_ego.py` | `clips`, `sheets`, `docs`, `page <datei>`, `--check` (in `./check`) |

**Aktionskanäle:** `weapon` (Haltung oder Haltung mit Versatz `roll/pitch/yaw/up/right/back`; pitch positiv = Mündung hoch),
`L`/`R` (Griff, Griff mit Versatz in mm, oder `('cam', Punkt)`), `fL`/`fR` (Fingerstellung), `mech` (Bauteilbewegung 0..1 wie
in den Waffenmodulen), `carry` (Magazin folgt der linken Hand), `drop` (Magazin fällt), `fire` (Schussbilder, Rückstoß der Waffe und
getrenntes Kamera-Feedback), `breathe`, `bob` (liegende Acht), `events` (Marker wie CE: HandOff, MagOut, MagIn, Chamber, HandOn,
Ready, Aimed …), `src` (Herkunft T/M/E).

**Formregeln Arm v3** (aus Nutzerbildern Q-D2-ARM, nur Prinzipien):
- Glatte, große Schale statt Rohr plus Brett; der Unterarm wölbt sich unter dem Ellbogen (größte Breite bei etwa einem Drittel)
  und verjüngt sich stark zum Handgelenk. Größte Breite ≈ 0,4 × Länge.
- Zwei Lagen: helle Schale, darauf eine dunkle Platte mit Pfeilschnitt und zwei Bolzen; darunter sichtbarer Graphitkörper.
- Medaillon (Scheibe, blanker Ring, Nabe) an Gelenken; das Wiedererkennungsmerkmal.
- Je Glied höchstens eine Akzentlinie; kein Leuchten, keine Stacheln.
- Vier Finger und Daumen (liest sich als Hand, Zeigefinger am Abzug).

**Bewegungsgefühl** (`ego.py`: `INTERP`, `SECONDARY`, `BREATHE_ALL`, `RECOIL`, `TIME_SCALE`; Nutzer: „zu schnell, rappelig,
abgehackt, statisch“):
- Schlüssel sind Durchgangspunkte, keine Stopps: monotone kubische Hermite-Kurve; anhalten nur, wo ein Schlüssel wiederholt wird
  oder die Richtung umkehrt.
- Die Waffe folgt ihrer Kurve über eine gedämpfte Feder (3,2 Hz, ζ 0,55): Trägheit und leichtes Nachschwingen; Hände folgen über
  die Griffe von selbst.
- Jede Aktion atmet dezent (3,4 s, 1 mm, 0,15°). Rückstoß ist ein Impuls je Schuss in eine Feder, die Kamera federt getrennt.
- Choreografie mit Akzenten: Ausholen vor großen Bewegungen, Stoß beim Einsetzen, Ruck beim Durchladen, Nachfedern am Ende.
- Ablauftempo 1,25 gegenüber der Destiny-Messung (lesbar ohne Ton und Bewegungsunschärfe); Zielen und Feuern bleiben schnell
  (`KEEP_TIME`). Clips immer mit vollen 30 fps rendern (kein `step`).

**Regeln für Arme und Haltungen**
- Drehgelenk in der Stulpe: Ober- und Unterarm zeigen ihre Panzerseite zur Kamera, die Hand dreht frei
  (sonst zeigt die Stützhand dem Spieler den Graphitkörper).
- Unterarm folgt der Hand (Viewmodel-Konvention wie Toolgen `arm_pose.forearm`), gemischt mit einer Vorzugsrichtung nach hinten
  unten außen; Handgelenk ≤ 45° (Toolgen-Ziel), Grenze 55°. Die Schulter folgt außerhalb des Bildes.
- Griffe so legen, dass die Hand **von unten hinten** zugreift (Magazin, Ladehebel); Finger nach unten lassen den Arm von oben
  vor die Kamera kommen.
- Hüfte: Griff unten rechts, Lauf zur Bildmitte, Visier rechts oben; Zielen: Socket_Eye auf der Kameraachse.
- Zeiten: gemessen (Q-REF) vor Toolgen-Startwert vor entworfen; jede Aktion nennt ihre Herkunft.
- Sichtung je Aktion in `data/review.json` (`<waffe>-ego`); „dargestellt“ nur nach Sichtung mit Schlüsselbildern.

**Typische Fehler:** Blender-Kamera mit nur 90° um X schaut nach +Y (zusätzlich 180° um Z); Toolgen-Schulterwerte knicken den Arm
an anderen Haltungen zu stark (Schulter folgt); Nicken um die lokale X-Achse senkt die Mündung (Vorzeichen); Teile links vom
Gewehr sind in der Standardkamera unsichtbar; nur den Querschnitt zu skalieren macht einen drahtigen Arm nicht kräftig (Form statt
Dicke); Standbilder müssen die Handbelegung der Aktion übernehmen (inspect_r ohne linke Hand).

## 11 Stand

Pilot Formstudie 01 v2.1 fertig (70 Teile, 32 694 Dreiecke, 8 Skins, grauer Hintergrund); v2 als Vorstufe erhalten.
Eigenes Arm-Rig v3 (vier Finger) und 19 Ego-Aktionen am Pilot; andere Waffenklassen offen. Familie Stil v2.1 mit Visier-Standard 3: BASIC-01, 02, 03 und
06 (Maschinenpistole, 0.11 „Compact“); als erstes Werkzeug die Portalkanone BASIC-T01 (0.17 „Gateway“). Die 13 übrigen Waffen sind im Stil v1; Übertragung in der Reihenfolge des Designvertrags
nach diesem Handbuch. Toolgen-Anbindung des v2-Stils (Budgets, Fasen, Texturen) ist offen und bewusst zurückgestellt.
