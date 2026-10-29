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
| 28.10.2026 | Handfeuerwaffe BASIC-04 und Seitenwaffe BASIC-05 v2.1 (0.24 „Holster“): Grundform nach Zwischenstopp mit Wahl „a“ übernommen (04 lange gerade Haube über freistehender Trommel, Kastenunterlauf; 05 hoher Schlitten auf kurzem Rahmen); Feinschliff nur in der Form: 05 dunkle Schlittenkappe hinten statt leerer Griffmulde, Magazinboden bündig; 04 Hahngehäuse runder und kleiner. Visier K1 „Klammer“ gebaut, M1 „Mini“ nur dokumentiert |
| 28.10.2026 | Schrotflinte BASIC-08 und Scharfschützengewehr BASIC-09 v2.1 (0.25 „Longshot“): Grundform nach Zwischenstopp mit Wahl „a“ übernommen (08 gerade Oberkante Schiene → Lüftungsschiene über dickem Lauf und Röhre, große Graphit-Pumpe; 09 Creme-Gehäuse und schmalerer Laufmantel mit Längsschlitz, freier Lauf, Z3 „Lang“ groß); Feinschliff nur in der Form. Kammerstängel des Scharfschützen **links** („mit links wird doch quasi nachgeladen“): die Stützhand repetiert, Hülse fliegt weiter nach rechts aus einem Auswurffenster rechts. Visiere K2 „Hörner“ und Z3 „Lang“ gebaut, K3 „Lochkimme“ nur dokumentiert |
| 28.10.2026 | Fusionsgewehr BASIC-10 und Lineares Fusionsgewehr BASIC-11 v2.1 (0.26 „Kindle“): Grundform nach Zwischenstopp mit Wahl „a“ übernommen (10 gerade Creme-Oberkante über quer offener Ladekammer mit drei Spulenringen um den Glutkern, gestufter Schlitz-Emitter, Zelle vor dem Griff; 11 offene Doppelschiene oben Creme / unten Graphit mit Leuchtkern und vier Spulen, stumpfe Gabel vor der Mündungsbrücke, Zelle hinter dem Griff); Feinschliff nur in der Form („Kern weniger grell“ → Ladekern als reine Emission). Die Abweichung von den Destiny-Proportionen (H/L 0,36 statt 0,49 bzw. 0,23 statt 0,43) ist damit bewusst gewählt. Energiewaffen ohne Hülsenauswurf (`EJECT = None`). Visiere F1 „Bögen“ und Z2 „Gabel“ gebaut, F2 Doppelring und Z1 als Variante nur dokumentiert |
| 28.10.2026 | Spurgewehr BASIC-12 und Maschinengewehr BASIC-15 v2.1 (0.27 „Tracer“): Grundform nach Zwischenstopp mit Wahl „a“ übernommen (12 Creme-Haube auf dem Gehäuse, Oberkante in Linie mit der Schiene, kragt über das freie runde Fokusrohr mit drei Ringen und umgreift vorn den Kegel, Fokusscheibe beidseitig, Zelle vor dem Griff, Einteilkörper mit Daumenloch; 15 Zuführdeckel mit Visier, Munitionskasten vor dem Griff, Gurt als Patronensäule links, Mantel mit Fenstern, Tragegriff links angeklappt; danach „Ich fand den MG Kasten Seitlich eigentlich sehr gut“ → Kasten seitlich links eingehängt wie v1; „eher in die breite … anstelle in die länge“ → flach und breit 104 × 60 × 76 mm); 12 bleibt bewusst flacher als die beobachteten Destiny-Spurgewehre (H/L 0,33 statt ≈ 0,40–0,55). Dazu am MG „eine Art ‚Eingang‘ für die Munition“ (Gurteinlauf mit blanker Lippe); Nutzerhinweise am Bild: Fokusscheibe mittig auf das Creme-Feld, Schriftzug ganz auf der Waffe, MG-Schaft tiefer und ohne dünnen Steg im Durchbruch und der Gurtvorschub je Schuss als Bewegungsdaten (`move.cycle = 'shot'`). Visiere H3 „Zinken“ und H6 „Achteck“ L gebaut, H9 Klappe, H7 Schirm und H1 Fase (L) nur dokumentiert |
| 28.10.2026 | Granatwerfer BASIC-13 und Raketenwerfer BASIC-14 v2.1 (0.28 „Breech“): am Zwischenstopp nach dem Kipplauf-Erstentwurf „Warum hat der granatwerfer keine Trommel? Im besten Fall für später animiert.“ → Wahl „Trommel statt Kipplauf“: 13 v2.1 ist der Trommelwerfer (Erweiterung EXT-02 vorgezogen, Leitmerkmal 13 im Designvertrag „Drehtrommel im offenen Rahmen“; v1 bleibt Kipplauf), sechs Kammern, Trommel dreht je Schuss eine Kammer weiter (Daten `move.cycle = 'shot'`), Ladeklappe, Hülsen nur beim Nachladen (`EJECT.on = 'reload'`); am Bild „schwebender Ring“ → Ladeklappe auf der Stoßplatte in einer Ladeschale; „Müsste das Granatwerfer nachladen nicht auf die linke seite anstelle der rechten seite?“ → Ladeschale, Ladeklappe und Klappenknopf links (Stützhand-Seite, wie Kammerstängel 09 und MG-Kasten 15). 14: „Müsste das Visier vom raketenwerfer nicht eher an der Seite sitzen?“ → nach der Korrektur, dass bei 66 mm Abstand das Rohr in jeder Richtung ins Fenster ragt, „Seitlich links, 66 mm notfalls Bauteil dazu passend erfinden“: Visier auf einem Visierarm an einer Visierschelle links neben dem Startrohr, Visierlinie auf Achshöhe; die Visierhöhe zählt seitdem als Abstand der Visierlinie zur Laufachse (66 ± 4). Raketenwerfer hülsenlos (`caseless`, `EJECT = None`); er bleibt mit dem seitlichen Visier flacher als die beobachteten Destiny-Raketenwerfer (H/L 0,26 statt ≈ 0,38–0,40). Visiere W1 „D-Linse“ und W2 „Entfernung“ gebaut, W3 Leiter und W1 L nur dokumentiert |
| 29.10.2026 | Kampfbogen BASIC-07 v2.1 (0.29 „Bowstring“): beim ersten Entwurf „das visier muss nach links, nicht nach rechts“ (Wahl „ganz zur linken Seite“) → Pinvisier B1 seitlich links neben dem Fensterbogen, 66 mm vom Pfeil (60 links, 27,5 darüber; Regel „seitlich nur links“ aus 0.28), Augenpunkt in Linie; dazu „achte hier besonders auf cubeescape reference zum thema bogen“ → Spannzeit 0,60 s (Draw Time 612 ms), Riser im Zielbild rechts der Mitte, H/L 0,72 gegen Destiny 0,73. Zwischenstopp „(a) so übernehmen“: Compound-Sichel (Creme-Mittelstück mit Sichtfenster und Durchbruch, dunkle gespaltene Wurfarme schwingen nach hinten zu Rollen, Sehne und Pfeil als eigene Teile); Feinschliff nur in der Form (Griffstück mit Handballenwölbung statt Kasten, Nocke schlanker). Bogen-Regel in [familienmasse.md](familienmasse.md): Griffstück statt BGM-1, kein Magazin, kein Auswurf; Weltzoom der Referenz (2,2×) erst mit dem Ego-Übertrag |
| 26.10.2026 | Portalkanone BASIC-T01 (0.17 „Gateway“): Werkzeug mit eigener Silhouette statt Familienkörper; nur Hüfte mit Kerbe als Leitkante, kein Visier; zwei Portalfarben (vorn Cyan = Portal A, hinten Orange = Portal B), Bedienelemente neutral; nach Skizze A „Ring“ der Wunsch „mehr an der Portal-2-Portalgun orientieren, nur im BALLON-Stil“ → Skizze P2 „Ei und Ring“ (facettierte Eischale, offener Zweifarbkern, Ring fest auf Speichen, dreht je Schuss 120°); „am Abzug sind die Teile in der Luft“ → Spalte gemessen und geschlossen |
| 29.10.2026 | Regeln aus Motiongen REF 0.30 „Blueprint“ ([design-ausruestung.md › 5](https://github.com/ffunkfabian-hash/cubeescape-reference/blob/main/docs/design-ausruestung.md#5-entscheidungsliste), [design-figuren.md › 5](https://github.com/ffunkfabian-hash/cubeescape-reference/blob/main/docs/design-figuren.md#5-entscheidungsliste), Quellen-IDs aus `data/design_quellen.json`): „Alle wie empfohlen“ – A1–A7 A, **A8 B**, A9 A; F1–F9 A. Übernommen in 0.30 „Rulebook“ als Regeln in §2 (Ausrüstung) und §12 (Figuren) und als Prüfungen in `./check`; A6 (gewichtete Normalen) und A9 (eigener Bildwinkel in Unity) folgen als eigene Version mit Export und Backen |

## 2 Gestaltungsregeln v2

1. **Schlicht zuerst.** Qualität kommt aus Silhouette, Schichtung und Material, nicht aus Kleinteilen. Im Zweifel weglassen.
2. **Drei Detailebenen.** Große ruhige Schalen (≈ 60 % der Fläche) · mittlere Gliederung: Fugen, Stufen, Einsätze (≈ 30 %) ·
   feine Akzente gebündelt an Mechanik, Visier und Mündung (≈ 10 %). Keine gleichmäßig verteilten Kleinteile.
   **Akzente kameranah (A3, 0.30):** die feinen Akzente vorrangig an den Teilen, die im Ego-Bild nah und wenig verzerrt liegen –
   Visier, Verschluss, linke Bedienseite; die Mündung bleibt mehrstufig, aber mit Abständen ≥ 4 px im Ego-Hüftbild (lieber zwei
   Schlitze als vier, breitere Rändel). Die Front verzerrt in der Ego-Sicht am stärksten, feines Detail verschmilzt dort.
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

### Ausrüstungsregeln aus REF 0.30 „Blueprint“ (0.30 „Rulebook“)

Beschlossen vom Nutzer am 29.10.2026 („Alle wie empfohlen“, §1). Regeltexte und Belege in Motiongen
[design-ausruestung.md › 3](https://github.com/ffunkfabian-hash/cubeescape-reference/blob/main/docs/design-ausruestung.md#3-gestaltungsregeln);
Quelle = ID in `data/design_quellen.json` (Motiongen `main` 7949582). Gilt für alle Waffen und Werkzeuge der Familie v2.1
(BASIC-01–15, T01); Fehler lassen `./check` scheitern, Warnungen werden gemeldet und nur nach Rückfrage umgebaut.

| Frage | Regel | Prüfung | Quellen |
|---|---|---|---|
| A1 | **Silhouette je Klasse eindeutig** (A-R1, A-R7): schwarze Seitensilhouetten aller Klassen auf gleiche Länge normiert, paarweise IoU < 0,85 (beste senkrechte Verschiebung, also streng); die Sichtung wertet zusätzlich das Ego-Bild (Ansicht `ego`, schwarz) | `tools/silhouettes.py` rastert die Netze ohne Rendern → `data/silhouettes.json`; `./check` rechnet die Matrix (**Fehler**, mit Liste der Paare; veraltet, wenn Entwurf oder Dreieckszahl sich ändern) | A01, A02, A20, A08, YA02, YA03; A07, A15, YA04 |
| A2 | **Dreiecksbudget je Ego-Waffe** (A-R24): Ziel 20 000, Grenze **50 000** (Nutzer 29.10.2026: „dreiecksbudget erhöhen auf 50 k“; vorher 30 000) | Zahlen aus `data/specs` (Blender-Netze); `./check` meldet **Warnung** (> 50 000) bzw. Hinweis (> 20 000), kein Umbau ohne Auftrag | A05, YB09, A21, A09, A10, A12, A06, A08 |
| A3 | **Akzente kameranah** (A-R8): siehe Regel 2 oben | Sichtungspunkt (§3, §7) | YA02, A05, A06, A08, A12 |
| A4 | **Freihaltezone im Hüftbild** (A-R9): ±10 % der Bildbreite um die Absehen-Spalte (Bildmitte), obere zwei Drittel frei von Waffe und Händen; **gelockert** (Nutzer 29.10.2026: „B Zone lockern“): das vordere Ende darf in die untere äußere Ecke ragen (alles Belegte rechts von 53 % B und unterhalb 55 % H), die Destiny-Hüftlage hat Vorrang | `tools/ego_clear.py` (GPU): Ego-Still `hip` und Maske aus derselben Szene → `data/ego_clear.json`; `./check` meldet **Warnung** je spielbarer Waffe (Umbau erst nach Rückfrage) | YA01 (einziger Beleg, Bungie-Vortrag) |
| A5 | **Fasen als Materialsignal** (A-R12): Griffpolster (`rubber`) eine Stufe breiter als der harte Träger – neue Stufe **R_SOFT 6,5 mm** nur für Griffpolster ([designvertrag](designvertrag.md#radien-fasen-fugen)) | Regel; Umsetzung in Teil 2 (die Stufen liegen in `basic/common.py`, das im Unity-Quellenhash liegt, und die bestehenden Griffe sind fertige, exportierte Waffen) | A06, A09, A10, A11, A13, YA09 |
| A6 | **Ruhiges Shading über gewichtete Normalen** (A-R13) | Stand 0.30: `kit.add_bevel` setzt schon `harden_normals` und `Weighted Normal` je gefastem Teil; Prüfung von Export und Wirkung in Unity in Teil 2 | A26, A25, A13, A16 |
| A7 | **Distanzansicht `far`** (A-R10, A-R1): Hauptansicht in 3 m und 5 m bei gleicher Brennweite (Bezugsbildwinkel 75° waagrecht), Ausschnitt in echten Pixeln eines 1080p-Bildes | `tools/far_views.py` (GPU) → `views/far_3m.png`, `far_5m.png`, im Sichtbogen (`make_sheets.py`) und in Runde 1 (§7) | A02, A23; A01, A20 |
| A8 | **Teilungen ungleich** (A-R4, Wahl B): Hauptblöcke (Schale/Unterbau, Haube/Gehäuse, Zweiton) möglichst nicht im Verhältnis 0,4–0,6 teilen, eher ≈ 70:30 | nur Sichtungspunkt in §3 (viele Klassen haben funktional vorgegebene Teilungen) | YA07, A13 |
| A9 | **Viewmodel mit eigenem Bildwinkel** (A-R11): Waffe und Arme immer mit dem Bezugsbildwinkel von Visier-Standard 3 (75° h), unabhängig vom Welt-FOV, eigener Tiefenbereich gegen Wandclipping | Laufzeit (Unity/Cube Escape), Teil 2 | A22, A28, A21, YB09 |

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
| Akzente kameranah (0.30, A3) | Kern, Anzeige und Wahlhebel links; Kompensator mit zwei breiten Schlitzen statt vieler feiner |
| Teilungen (0.30, A8, nur Sichtung) | Hauptblöcke nicht 0,4–0,6 teilen (Pilot-Gehäuse Lack/Polymer ≈ 1 : 1 – funktional, zur Kenntnis) |
| Lesbarkeit (0.30, A1/A7) | Seitensilhouette eindeutig (`./check`), Ego-Silhouette und `far` 3 m / 5 m gesichtet |

Ab 0.30 gehören die drei letzten Zeilen in jede neue Checkliste; fertige Waffen werden nicht nachgetragen (ihre Module liegen zum Teil
im Unity-Quellenhash), ihr Stand steht im Bericht [0.30 „Rulebook“](versions/0.30-rulebook.md).

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
| `klammer(fr, ff, deck, size, parent)` (in `basic/pilot/optics/sight_kit.py`) | **K1 „Klammer“** (Kimme/Korn, 0.24): Kimmenblatt mit Kerbe und bündigen Leuchtklammern auf flachem Fuß, Korn mit Leuchtpunkt; Linie Träger + 11 mm, Augenpunkt 70 mm hinter der Kimme; gibt `(Teile, Anker)` mit `Socket_Sight` zurück. Liegt nicht in `common.py`, weil dieses im Unity-Quellenhash steht (Umzug mit dem Ego-Übertrag) | `fr` Kimmenrückseite, `ff` Kornspitze, `deck` Oberkante des Trägers, `parent` Schlitten | 04, 05 |
| `hoerner(fr, ff, deck, size, parent, front_w)` (in `basic/pilot/optics/sight_kit.py`) | **K2 „Hörner“** (Schrot, 0.25): zweistufiger Fuß mit orangem Hebel, Kimmenblatt als U-Querprofil (zwei Flachblatt-Hörner 20° nach außen, Spitzen Linie + 4, Steg 2 mm unter der Linie), schlankes Korn mit orangem Kornkopf Ø 3,6 (kein Leuchten); Linie Träger + 11 mm, Augenpunkt 70 mm hinter der Kimme wie K1 | `deck` Schiene/Lüftungsschiene (Kimme und Korn auf gleicher Höhe), `front_w` Kornfuß auf schmaler Laufschiene | 08 |
| `lang(f_obj, u, cu, size, weapon_type, seat_u, length, saddle_f)` (in `sight_kit.py`) | **Z3 „Lang“** (Scharfschütze, 0.25): Sitz nach Konzept A wie Z1 (Rohrsattel hinter dem Auge, H0-Klemmfuß unter dem Objektiv, Trapezsockel), Rohr Ø 24 × 200 mm, Ring ohne Wulst (M: Linse Ø 38, Ring Ø 52), blanke Sonnenblende 16 mm nach vorn; `Socket_Eye` 90 mm hinter dem Ring mit `sight_type 'fullscreen'`; Vollbild-Werte `FULLSCREEN` (Kreis 82 % H, Duplex) | wie `scope_tropfen`; `length` Standard 200 | 09 |
| `boegen(f, u, size, weapon_type)` (in `sight_kit.py`) | **F1 „Bögen“** (Fusion, 0.26): H0-Plattform ohne Emitterblock, zwei Flachprofil-Bögen mit 3 mm Radiusversatz (Lücken 3/9 Uhr, schräge Stege) = S-Öffnung, Ladebalken 10 × 1,5 mm leuchtet mit der Ladung; Glas Ø 26 (M, 18,9 %), Visierlinie Schiene + 26 | `f`, `u` wie `holo_kasten`; `BOEGEN_SIZES` S/M/L | 10 |
| `gabel(f_obj, u, cu, size, weapon_type, seat_u, length, saddle_f)` (in `sight_kit.py`) | **Z2 „Gabel“** (Lineare Fusion, 0.26): Sitz nach Konzept A wie Z1, Ring ohne Wulst (1,29), U-Gabel 3 × 10 mm mit 3 mm Abstand um den Ring, Laschen auf 3/9 Uhr; die Gabel ruht auf dem Klemmfuß (kein Sockelblock) | wie `scope_tropfen` | 11 |
| `zinken(f, u, size, weapon_type)` (in `sight_kit.py`) | **H3 „Zinken“** (Spur, 0.27): H0-Plattform, zwei Seitenplatten 15° nach außen, oben offen, Spitzen innen gekappt; Emitterpunkt mittig in der Sockelrückseite zum Auge; Glas als Trapez zwischen den Platten (M unten 15,6 / oben 25,8 mm = 18,7 %), Visierlinie Schiene + 26 | `f`, `u` wie `holo_kasten`; `ZINKEN_SIZES` S/M/L, `ZINKEN_DEG` | 12 |
| `achteck(f, u, size, weapon_type)` (in `sight_kit.py`) | **H6 „Achteck“** (MG, 0.27): H0-Plattform, Achteckhaube aus Flachprofil 1,6 × 12 mit 45°-Fasen, vier blanke Fasenflächen außen, Sockel so breit wie die untere Achteckseite; am MG Größe **L** (34 × 26, 24,7 %, Holo-L-Variante), M läge mit 21,8 % über dem Band | `f`, `u` wie `holo_kasten`; `ACHTECK_SIZES` S/M/L (Standard `size='L'`) | 15 |
| `d_linse(f, u, size, weapon_type)` (in `sight_kit.py`) | **W1 „D-Linse“** (Granatwerfer, 0.28): H0-Plattform, D-Haube aus Flachprofil 2,4 mm (Werfer), oben gerade mit oranger Kerbmarke, drei blanke Fallmarken links innen an der Haubenwand unter der Visierlinie (4/3/2 mm, Abstand 0,3 r); Sockel so breit wie die D-Unterseite in Sockelhöhe; M Glas 26 mm = 18,9 % | `f`, `u` wie `holo_kasten`; `DLINSE_SIZES` S/M/L (L = Holo L) | 13 |
| `entfernung(f, u, size, weapon_type)` (in `sight_kit.py`) | **W2 „Entfernung“** (Raketenwerfer, 0.28): H0-Plattform, Rundrechteck-Haube 2,4 mm mit Dach 4 mm, das 6 mm vor die Haube steht (Schutzdach), leuchtendes Entfernungsfeld (drei Ziffern + Einheit) in der Sockelrückseite; M 26 × 18 = 18,9 % | `f`, `u` wie `holo_kasten`; `ENTF_SIZES` S/M/L | 14 |
| `side_mount(P, A, dx)` (in `sight_kit.py`) | verschiebt ein gebautes Visier samt Schneidkörpern, Bewegungen und Ankern um dx quer zur Laufachse (0.28, Raketenwerfer: Visier 66 mm links auf Achshöhe; Visierhöhe = Abstand zur Achse) | `dx` > 0 links | 14 |
| `pins(f, u, size, eye_f)` (in `sight_kit.py`) | **B1 „Pins“** (Bogen, 0.29): kurze H0-Plattform ohne Emitter und Glas, Ring aus Flachprofil 1,8 × 8, rechts abgeflacht mit Pinschiene und Klemmen, drei waagerechte Pins von rechts mit Leuchtköpfen (Rolle `pin_glow`, reine Emission) – die Pins sind das Absehen; Visierlinie Schiene + r + 12; M Ring Ø 52 = 5,0 % bei Augenpunkt am Ankerpunkt (680 mm), Pinabstand 0,36 r = 0,79° | `eye_f` Augenpunkt (Bogen: Ankerpunkt bei vollem Auszug); seitlich mit `side_mount`; `PINS_SIZES` S/M/L | 07 |
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
     Scout Z1, MP H2 gebaut; K1 seit 0.24, K2 und Z3 seit 0.25, F1 und Z2 seit 0.26, H3 und H6 seit 0.27, W1 und W2 seit 0.28, B1 seit 0.29 in `sight_kit.py`; die übrigen als Entwurf).
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
   in `docs/quellen.md › Q-D2-IMG` eintragen (Waffe, Typ, URL, beobachtetes Prinzip). Keine Bilder ins Repo. Ohne Browser (0.24): Typ und
   Bild-ID stehen im öffentlichen Bungie-Manifest (`bungie.net/Platform/Destiny2/Manifest/` › `DestinyInventoryItemDefinition`,
   Felder `itemTypeDisplayName`, `screenshot`); light.gg lehnt direkte Abrufe ab.
2. **Checkliste (Abschnitt 3)** im Modul-Docstring ausfüllen; Schlichtheitsbudget (Abschnitt 2) einplanen.
3. **Modul bauen:** neue Waffe als `basic/weapons/wNN_*.py`; Neugestaltung einer bestehenden zuerst als `basic/pilot/…` mit
   `META['variant']` (eigener Ausgabeordner, Reihe bleibt unberührt).
4. **Rendern (GPU-Sperre):**
   `~/Claude/cubeescape-nexogen/ce lock gpu -- /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P tools/blender_build.py -- <modul> --views --aaa --gpu --samples 128 --res 1600 --skins standard,nacht,polar,kobalt,wueste,tarnung,gebraucht,eloxal`
   (Schnelldurchlauf: `--only hero,hero_p,side_left,ego --samples 64`).
5. **Sichten in Runden** (meist drei): Silhouette und Zweiton → Schichten und Negativraum → Material und Schlichtheitsbudget.
   Je Runde Hauptansicht, linke Seite, Ego-nah, Explosion; zusätzlich Visierlinie (`sightline.png`) und bei Hohlformen eine
   Volumenprüfung (Blender, `bmesh.calc_volume`). **Runde 1 ab 0.30 (A1, A7):** Silhouetten neu rastern
   (`ce lock blender -- Blender -b --factory-startup -P <repo>/tools/silhouettes.py -- <ID>`; `./check` meldet Paare mit IoU ≥ 0,85),
   Ego-Silhouette im Mosaik (`python3 tools/rules_evidence.py`) und `far` 3 m / 5 m
   (`ce lock gpu -- Blender -b --factory-startup -P <repo>/tools/far_views.py -- --gpu <ID>`) sichten: Klasse auf Distanz erkennbar,
   Leitmerkmal trägt. **Runde 3:** Akzente kameranah (A3), Teilungen (A8), Dreiecke gegen Ziel 20 000 / Grenze 50 000 (A2); für
   spielbare Waffen die Freihaltezone im Hüftbild (A4, `tools/ego_clear.py`, GPU).
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
| Distanzansicht `far` (0.30, A7) | Erkennbarkeit auf Distanz, Sichtung Runde 1 | `tools/far_views.py`: Hauptrichtung, 3 m und 5 m, gleiche Brennweite 23,5 mm KB (75° waagrecht wie die Ego-Kamera), 1920 × 1080, gespeichert nur der mittlere Ausschnitt 640 × 360 in echten Pixeln; lange oder hohe Waffen (Bogen in 3 m) werden angeschnitten |
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
- Dünne Stege mit großer Fase: 5 mm Rahmen unter der Trommel mit `R_MID` fiel auf der Seitenfläche zusammen (dunkler Keil im Render)
  → Stege ≥ 3 × Fase, Fenster ins Profil legen statt per Boolean (BASIC-04 v2.1).
- Kammerstängel, der sich hebt, läuft durch alles, was über der Kammerbahn breiter ist als das Gehäuse innen: Bahn oben offen,
  Visierbuckel als schmaler Sattelblock (26 mm) statt in voller Gehäusebreite; Endlagen am Netz prüfen (BVH je Pose), nicht schätzen
  (BASIC-09 v2.1).
- Pumpe als volles Profil um das Röhrenmagazin: Loch für das Rohr schneiden, Führungsstangen brauchen Bahnen im Gehäuse – sonst meldet
  die Posenprüfung Durchdringungen in Endlage (BASIC-08 v2.1).
- Ladekern in der Familienrolle `energy` (beleuchtete Grundfarbe, Stärke 3) bleicht unter AgX zu Weißblau und liest sich als Leuchtröhre → reine Emission wie die Portalfarben (`charge_core`, Stärke 0,7) und Spulen so lang, dass der Kern nur in kurzen Lücken leuchtet (BASIC-10/11 v2.1).
- Zelle oder Magazin vor dem Griff bei f 80 schneidet den Abzugsbügel von `grip_v21(top=40)` (Vorderkante f 82,7) – Posenprüfung (BVH) meldete 2,7 mm; Zelle ab f 86 (BASIC-10 v2.1).
- Holo mit nach oben geöffneten Platten (H3): die Öffnung zählt die breiteste Stelle des Glases – der Katalog-Entwurf mit 26 mm unten war oben 36 mm breit (26 %) → Glas unten schmaler (M 15,6 mm), Platten genau 15° an der Innenkante (BASIC-12 v2.1).
- Tragegriff oben auf dem Laufmantel steht im Zielbild: bei 172 mm Visierlinie läge ein Griff auf u 146 nur 3,9° unter der Bildmitte im unteren Fenster (H6 L reicht bis 8,2°) → Griff links am Mantel angeklappt, auf Griffböcken mit Abstand, außerhalb des Zielbilds (BASIC-15 v2.1).
- Durchbruch im Schaft S1 parallel zur schrägen Unterkante zu nah: der Steg wurde 3 mm dünn und zeigte mit der Fase einen schwarzen Keil (Nutzer am Bild) → Rand ≥ 12 mm; Schaftachse unter die Gehäuseoberkante legen, sonst steht die Schaftverbindung über dem Gehäuse (BASIC-15 v2.1).
- Gurtsäule außen an der Gehäusewand: Glieder (r 5,4) breiter als die Patronen (r 4,6) – Mitte der Säule so legen, dass die Glieder frei von Wand und Einlauf bleiben (Posenprüfung am Netz, BASIC-15 v2.1).
- Fallmarken in einer runden Haube auf festem x: unten liegt die Wand weiter innen, die Marke schwebt außerhalb der Haube (Katalog-Entwurf W1 0.21) → x aus der Wand in Markenhöhe berechnen (`dlinse_wall_x`) und am Bild prüfen (BASIC-13 v2.1).
- Dickes Rohr unter dem Visier (Raketenwerfer Ø 92): bei 66 mm Visierhöhe liegt die Rohrwand nur ≈ 20 mm neben der Visierlinie und läuft im Zielen bis 2° an den Zielpunkt heran – in jeder Richtung, auch seitlich; frei wäre erst ≈ 140 mm Abstand. Seitliches Visier verschiebt nur die Ecke, in die das Rohr ragt (BASIC-14 v2.1).
- Ladeklappe einer Trommel, die nach hinten aufschwenkt, läuft mit der inneren Kante durch das Gehäuse → Klappe in einem Spalt zwischen Gehäuse und Stoßplatte, Schwenk in ihrer Ebene (Achse f); Endlage am Netz prüfen (BASIC-13 v2.1).
- Schriftzug links (`side=1`) wächst von `f` nach hinten: als `f` die Vorderkante der Schrift setzen; der Raketenwerfer-Schriftzug stand mit f −30 über das Abzugsgehäuse hinaus in der Luft (Nutzer am Bild, „erneut“ nach 0.27) → am Netz prüfen, dass jede Buchstabenecke aufliegt (Strahl in die Waffe, BASIC-14 v2.1).
- Ladeklappe in einem offenen Spalt zwischen Gehäuse und Stoßplatte wirkt wie ein schwebender Ring (Nutzer am Bild) → Spalt schließen, Klappe auf der Stoßplatte in einer Ladeschale des Gehäuses (BASIC-13 v2.1; Ladeseite links, Nutzerwunsch).
- Weiße Sprenkel auf einer großen eloxierten Trommel (feine Kratzer quer zur Rundung, wie 0.21 am Visier) → Rolle `ring_anod` ohne feine Kratzer (`basic/pilot/metal_roles.py`, auch an den Schellen von BASIC-14), kit.py bleibt (BASIC-13 v2.1).
- Pinvisier am Bogen mittig über dem Pfeil: der Riser liegt zwischen Auge und Ring und verdeckt ihn → Fenster im Mittelstück („cut past center“) oder Visier seitlich neben dem Fensterbogen; die Lage aus dem Sichtkegel rechnen ((r + Stirn) × Abstand Riser / Abstand Ring) und am Netz prüfen (`test_sight_seat`, BASIC-07 v2.1). Maßgeblich ist die Vorderkante des Fensterbogens (dort ist der Kegel am weitesten) und der Ring samt Stirn; auch das flache Visiergehäuse der H0-Plattform ragte bei Schiene + r + 10 in den unteren Ringrand → + 12 (Richter 0.29).
- Rolle mit 160° Drehung: `move.expect` misst die Verschiebung bei voller Bewegung, der Prüfpunkt kommt im Bogen fast wieder zurück und ein umgedrehtes Vorzeichen bleibt grün → ≤ 90°, Prüfpunkt 45° neben der Achse (BASIC-07 v2.1).
- Nocke dicker als der Pfeilschaft streift beim Pfeilflug die Auflage → Posenprüfung auch für den Flug (Wert < 0) und Nocke schlank (BASIC-07 v2.1).
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
Eigenes Arm-Rig v3 (vier Finger) und 19 Ego-Aktionen am Pilot; andere Waffenklassen offen. Familie Stil v2.1 mit Visier-Standard 3: BASIC-01, 02, 03,
04 und 05 (Handfeuerwaffe und Seitenwaffe mit Kimme/Korn K1, 0.24 „Holster“; ohne Ego-Übertrag und Unity), 06 (Maschinenpistole, 0.11 „Compact“), 08 und 09 (Schrotflinte mit Kimme/Korn K2, Scharfschützengewehr mit Z3 „Lang“ im Vollbild, 0.25 „Longshot“; ohne Ego-Übertrag und Unity), 10 und 11 (Fusionsgewehr mit F1 „Bögen“, Lineares Fusionsgewehr mit Z2 „Gabel“, Energiewaffen ohne Hülsenauswurf, 0.26 „Kindle“; ohne Ego-Übertrag und Unity), 12 und 15 (Spurgewehr mit H3 „Zinken“ ohne Hülsenauswurf, Maschinengewehr mit H6 „Achteck“ L, Gurteinlauf, Hülsen- und Gliederauswurf als Daten und Gurtvorschub je Schuss, 0.27 „Tracer“; ohne Ego-Übertrag und Unity), 13 und 14 (Granatwerfer als Trommelwerfer mit W1 „D-Linse“, Trommel je Schuss eine Kammer weiter und Hülsen nur beim Nachladen; Raketenwerfer mit W2 „Entfernung“ seitlich links und hülsenloser Rakete, 0.28 „Breech“; ohne Ego-Übertrag und Unity), 07 (Kampfbogen als Compound-Sichel mit Pinvisier B1 seitlich links, Sehne, Pfeil und Rollen als Bewegungsdaten, kein Magazin und kein Auswurf, Bogen-Regel in den Familienmaßen, 0.29 „Bowstring“; ohne Ego-Übertrag und Unity); als erstes Werkzeug die Portalkanone BASIC-T01 (0.17 „Gateway“). Die 2 übrigen Waffen (Schwert, Gleve) sind im Stil v1; Übertragung in der Reihenfolge des Designvertrags
nach diesem Handbuch. Toolgen-Anbindung des v2-Stils (Budgets, Fasen, Texturen) ist offen und bewusst zurückgestellt.

## 12 Figuren (Roboter-Spielfigur, M-4, NPCs)

Regeln aus Motiongen REF 0.30 „Blueprint“ ([design-figuren.md › 3](https://github.com/ffunkfabian-hash/cubeescape-reference/blob/main/docs/design-figuren.md#3-gestaltungsregeln)),
vom Nutzer am 29.10.2026 beschlossen (F1–F9 A, §1); Quelle = ID in `data/design_quellen.json` (Motiongen `main` 7949582). **Noch keine
Figur gebaut** (0.30 „Rulebook“). Der Vertrag eines Figurenmoduls steht in [basic/figures/__init__.py](../basic/figures/__init__.py):
sobald dort ein Modul liegt, prüfen `./check` (`tools/rules.py`) und `tools/test_figure.py` (Blender, BVH) es ohne weiteren Auftrag. Der
Roboter aus 0.23 „Gauntlet“ (Außenansicht, `data/robot.spec.json`) bekommt bis dahin nur Budget- und Proportionshinweise aus seinem Spec.
Die Formregeln von Arm v3 und Roboter stehen in §10; dieser Abschnitt ergänzt, was eine Spielfigur oder ein NPC zusätzlich braucht.

| Frage | Regel | Prüfung | Quellen |
|---|---|---|---|
| F1 | **Proportion schlank nach dem Zielbild:** ≈ 7,5 Kopfhöhen (Helm gemessen), lange Beine, Kopf **nicht** vergrößern (der Vorschlag „Kopf + 10 %“ der Roboter-Übergabe entfällt) | Kennzahl im Modul/Spec (`HEIGHT_MM`, `HEAD_MM`); `./check` meldet einen Hinweis außerhalb 7,0–8,0 | F28, F05, F07, F19, F12 |
| F2 | **Formsprache je Rolle:** Spielerfigur Quadrat mit Kreis-Akzenten (stabil, verlässlich; Medaillons), M-4 und freundliche NPCs kreisdominiert, Gegner mit Dreiecken und Schrägen; Grundform im Modulkopf | `META role`/`form` (`player`→`square_circle`, `friendly`→`circle`, `enemy`→`triangle`), **Fehler** bei fehlender oder falscher Grundform | F06, F29, YB01, YA02 |
| F3 | **Posensatz mit Durchdringungsprüfung:** Arm oben, Arm vor der Brust, tiefe Hocke, Ausfallschritt, Rumpfdrehung ±45°; Plattenabstand ≥ 1 mm in der Grundhaltung | `tools/test_figure.py` (in `./check`, Mac): je Teilpaar verschiedener Knochen BVH-Überlappung und „Teil im Teil“ in jeder Pose, Abstand in Grundhaltung; Selbsttest an einem Prüfkörper (richtig grün, drei falsche Fassungen rot) | F31, F32, F22, F33, YB11; F20, F15, YB04 |
| F4 | **Panzer starr je Segment;** Schulterpanzer an einem Hilfsknochen mit Einfluss nach Armhöhe, Brustpanzer endet an der Taille, Bauch zweigeteilt | Regel; der Posensatz (Arm oben, Rumpfdrehung) zeigt Verstöße als Durchdringung | YB13, YB14, YB04, F21, F22, F33 |
| F5 | **Ein Handmaß** für Ego und Figur (Ego-Arm v3); Änderungen am Ego-Arm wirken auf die Figur; Griffbreite 30 mm der Familie (BGM-1) bleibt Bezug | `HAND` im Modul; `./check` vergleicht Handflächenbreite und -länge, Fingerteilung und -längen, Daumen mit `basic/arms/robot_arm.py` (±1 %, **Fehler**). Stand 0.30 (Arm v3 vor „Gauntlet“): Handfläche 93,9 × 74,6 mm, Fingerteilung 20,3 mm, Finger 75,5/80,1/75,5/63,4 mm, Daumen 78,3 mm, Handfläche ÷ Griffbreite 3,1 – nach 0.23 „Gauntlet“ mit dessen Arm neu abgleichen | F11, YB06, A24 |
| F6 | **Budget:** Figur höchstens 30 000 Dreiecke (Ausrüstung getrennt gezählt), höchstens 100 Knochen (ohne Simulation) | **Warnung** in `./check` (Figurenmodule und Roboter-Specs) | YB09, F27 |
| F7 | **Größenklassen** für NPCs und Gegner als Vielfaches der Spielerfigur: klein ≈ 0,6, mittel ≈ 1,0, groß ≥ 1,6; Schwachstellen hell auf dunklem Körper | `META size_class`/`scale` (klein 0,5–0,7, mittel 0,9–1,1, groß ≥ 1,6), **Fehler** außerhalb; Abnehmer Cube Escape | F18, F04, F13, F14, YB02, YB01 |
| F8 | **Kantenlicht statt Umrisslinie:** Fresnel-Kantenlicht für Figuren in Unity, oben betont, Gegner farbig; keine Umrisslinie | Laufzeitregel (Unity/Cube Escape); in Blender nur das Rim-Licht der Renderings – Umsetzung mit dem Unity-Teil | F01, F03, YB05, YB08 |
| F9 | **Vorn/Hinten im Umriss:** ein Rückenmodul (Kühl- oder Energieblock) gibt der Rückseite einen eigenen Umriss; vorn Visier und Brustsensor | Sichtung: Silhouette von vorn, hinten und seitlich je Runde | F04, YB05 |
