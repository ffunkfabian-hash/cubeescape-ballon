# Visier-Konzept nach 0.20 „Spotter“ – Befund, Sitz, Baukasten v3

Stand 26.10.2026, Konzeptschritt (Patch, gebaut wird nach der Nutzerwahl in einer eigenen Version). Anlass und Zitate:
[uebergabe-visier-konzept.md](uebergabe-visier-konzept.md). Bilder liegen außerhalb des Repos (`~/Library/Caches/CubeEscapeBallon/`).
Werkzeuge: `tools/sight_options.py` (Sitz-Konzepte am echten BASIC-01/03), `tools/sight_catalog.py` (Baukasten auf Prüfkörper),
Quellen `basic/pilot/optics/sight_concepts.py`, `sight_kit.py` (und `sight_kit_more.py`, weitere Varianten).

## 1. Nutzerstimmen in dieser Sitzung

- „Visier-Punkte/Kreise/Fadenkreuze sehen so komisch 3D-mäßig aus … lieber etwas Gezeichnetes“; Scout: „vor allem die Unterseite,
  das was auf der Schiene sitzt“.
- „Du solltest dir nach Möglichkeit mehrere Waffen und deren Visiere anschauen“; „Schau dir auch mal Visiere von Battlefield 6 an“;
  „Formgen hat noch ein anderes Visier-Sheet. Nicht die Konzeptzeichnungen“.
- „Unterschiedliche Visiere anlegen, verschiedene Formen, Größen usw., die wir später verwenden können. Für manche Waffen fehlen ja
  Visiere auch noch“; „Bau mehr Varianten“.
- Zu v1: „fast alle zu klotzig … vom Gefühl her viel zu hoch“. Zu v2: „Das Visier von BASIC-01 sieht so um Welten besser aus als die
  neuen“. Leitlinie: „Visier vom aktuellen Automatikgewehr von der Höhe optimal und vom Design gut. Daran sollte man sich orientieren“.
- Auftrag Design: ein bis zwei prägende Elemente je Visier, schlicht, funktional, gut lesbar, unterscheidbar, Sichtfeld frei.

## 2. Befund

**Destiny 2** (Motiongen `visiere.md` › 2/5/7, `proportionen.md` › 5.2; 11 Visiere aus 8 Showcase-Videos, Belege
`refs/video/d2_ads/`, Scout `refs/video/scout_frames/`): Unter jedem Visier sitzt ein **schmaler dunkler Hals oder Block**, oft mit
Leuchtanzeige („027“, „021“), nie eine breite Platte nahe am Auge. Ringe außen/innen 1,28–1,30, offene Häkke-Ringe dünner. Glasgrafik
2–3 px, gezeichnet; HUD-Punkt getrennt.

**Battlefield 6** (Unteragent Sonnet, `refs/bf6/bf6_optiken.png`, Notiz `side-session-notes/…/bf6-optiken.md`): schlanke
Reflexvisiere (Mini Flex, R-MR, 1P87) sind **lang, flach, kompakt** – nur das Fenster steht auf, Rahmen/Öffnung ≈ 0,08–0,12; klobig
wirken Hauben ≥ 0,25 der Öffnung, hohe Riser, Glockenobjektive. Übernehmen: eine Fensterform je Visier, ein heller Akzentring,
Glastönung als Klassencode; nicht: Skalen im Glas, Mikrodetails, hohe Doppelklemmen.

**Formgen VS01–VS09** (Unteragent Sonnet, `refs/formgen_vs/formgen_visiere.png`, Quelle `cubeescape-formgen/claude/output/sheets/VSnn.dc.html`):
geschlossene Vollrahmen 2,5–5 mm auf breitem Block, 40–71 mm hoch – bewusst wuchtig, für BALLON zu klotzig. Übernehmen: Typ je
Waffe, je Visier vier Fadenkreuze, acht Glastönungen, Module (Entfernungsanzeige, Zielmarkierung), Prüfung der freien Durchsicht.

**Ursachen am BALLON-Bild 0.20** (`evidence/sight_options.png`, Zeile „0.20 jetzt“):
1. **Platte vor dem Auge:** Schiene BRI-22 und Rohrsattel liegen 10 mm unter der Visierlinie 0–50 mm vor dem Auge (Holo: Gehäuse
   hinter dem Fenster) – im Zielen ein breites Feld im unteren Bilddrittel.
2. **Ringwulst:** Der Objektivtrichter ist hinter dem Ring winkelmäßig größer als die Stirn (r/d 0,194 bei d 54 gegen 0,183 am Ring) –
   seine Flanke steht als Wulst um den Ring. Abhilfe: Objektiv als Kegel zum Auge, r/d ≤ Ring/90 mm.
3. **Hellgrau-Marmor:** Die Abriebmaske misst mit 4 mm Radius; Teile mit 2–4 mm Wand gelten ganz als Kante (Ring, Haube; auch Unity).
4. **Absehen als Röhren:** Modellteil aus Rundröhren; gezeichnet wirkt es flach.

**Warum H0 (BASIC-01) besser aussieht als v2** (Designkritik Opus, Notiz `side-session-notes/…/visier-kritik.md`): flache gefaste
Profile mit blanker Stirnkante statt Rundstab; liegende Masse in drei Lagen (Klemmfuß, Gehäuse, Haube) statt „Schild auf Stele“;
Funktionsdetails (Emitter, Knopf, Batteriedeckel, oranger Hebel); eloxiert mit Abrieb statt einfarbig matt; Trapezsockel in
Fensterbreite.

## 3. Sitz-Konzepte am echten Gewehr (BASIC-01 Holo, BASIC-03 Zielfernrohr)

Blatt `evidence/sight_options.png` (Destiny-Referenz, 0.20, A/B/C; je Holo/Zielfernrohr im Zielen und von der Seite):

| Konzept | Zielfernrohr (Scout) | Holo | Urteil |
|---|---|---|---|
| **A „Hals“** | Rohr hinten auf Buckel **hinter dem Auge** (Sattel im Zielen unsichtbar), vorn schmaler Hals unter dem Objektiv | Fenster auf schmalem Hals, kein Gehäuse hinter dem Fenster | Destiny-nah, unter dem Ring nur ein dunkler Hals; empfohlen |
| B „Grat“ | Rohr bleibt auf dem Gehäuse (0.19), schmaler Grat, vor dem Auge abgeschrägt | Keilsockel mit Anzeige | schmaler, aber vorn bleibt eine Fläche |
| C „Offen“ | Häkke-Ring offen auf zwei Beinen | VEIST-Zinken, Leuchtlinie | sehr luftig, wirkt zerbrechlich |

Alle drei: Ring ohne Wulst (außen/innen 1,29), Absehen gezeichnet. Der Baukasten v3 übernimmt A für Zielfernrohre (Sattel hinter dem
Auge, Fuß unter dem Objektiv) und die H0-Bauweise für alles andere.

## 4. Baukasten v3

Blätter: `evidence/sight_catalog.png` (je Visier im Zielen und Nahansicht, Größe M), `evidence/sight_catalog_sizes.png` (S/M/L).
Prüfkörper mit BASIC-01-Maßen (Gehäuse u 135, Schiene bis u 143, Visierlinie u 169). **Plattform = H0:** zweistufiger Klemmfuß
46 × 23/18 mm mit orangem Hebel, flaches Gehäuse (Emitter, Knopf, Batteriedeckel), Trapezsockel in Fensterbreite, Haube aus
Flachprofil (Stirn 1,6 mm, Werfer 2,4 mm, Tiefe 10–12 mm) mit blanker Stirnkante, eloxiert mit Abrieb für dünne Teile.

| ID | Name | für | Merkmal (1–2) |
|---|---|---|---|
| `holo_ref` | H0 Referenz | Automatik heute | offene Haube, Trapezsockel |
| `holo_fase` | H1 Fase | Automatik, MG | gefaste Ecke oben rechts |
| `holo_pille` | H2 Pille | MP | ohne Haube; Emitterblock, Pillenkontur nur gezeichnet |
| `holo_zinken` | H3 Zinken | Spur, MP | Seitenplatten 15° geneigt, oben offen; Punkt zum Auge |
| `holo_kasten` | H4 Kasten | Impuls | runde Dachecken, Seiten einwärts; Ziffernfeld im Sockel |
| `ring_haekke` | H5 Häkke-Ring | Impuls, Automatik leicht | Lücke oben; Nasen 3/9 Uhr |
| `fusion_boegen` | F1 Bögen | Fusion | versetzte Bögen (S-Öffnung) mit Stegen; Ladebalken |
| `mini_reflex` | M1 Mini | Seitenwaffe, Handfeuerwaffe (wahlweise) | kleinste Haube, Plattform 70 % |
| `launcher_d` | W1 D-Linse | Granatwerfer | D-Haube mit oranger Kerbe; Fallmarken |
| `rocket_kasten` | W2 Entfernung | Raketenwerfer | Schutzdach; Entfernungsfeld |
| `scope_tropfen` | Z1 Tropfen | Scout (Standard) | Sockel läuft in die Ringstirn; blanker Absatz am Objektiv |
| `scope_gabel` | Z2 Gabel | Lineare Fusion, Scout | U-Gabel mit 3 mm Abstand; Laschen |
| `sniper_lang` | Z3 Lang | Scharfschütze | Sonnenblende; im Zielen Vollbild mit Duplex |
| `iron_klammer` | K1 Klammer | Handfeuerwaffe, Seitenwaffe | Leuchtklammern bündig im Kimmenblatt; Kornpunkt |
| `iron_hoerner` | K2 Hörner | Schrot | Flachblatt-Hörner; oranger Kornkopf |

Weitere zehn Varianten: Abschnitt 6, Zuordnung je Waffentyp: Abschnitt 6a.

Größen: Holo S/M/L = 22 × 17 / 26 × 20 / 34 × 26 mm → 15,9 / 18,8 / 24,6 % Bildbreite bei 90 mm (Standard 12–20 %: **L liegt
darüber**, gedacht für MG/Werfer); Zielfernrohr r 12/14/17 → 17,4 / 20,3 / 24,6 % (Standard 20–26 %: **S liegt darunter**).

## 5. Absehen gezeichnet – auch in Blender

Konzeptbilder legen das Absehen flach in die Glasebene: Hüftform der Klasse in Hüftgröße (`reticles.hip`, wie Unity seit 0.20),
Linien mindestens 1,6 px, reine Emission (`reticle_cyan`). Kimme/Korn ohne gezeichnetes Absehen (die Leuchtklammern sind es),
Scharfschütze Vollbild mit Duplex. In der Bau-Version wird das ein flaches Modellteil (statt Röhren) bzw. die Ego-Clips zeichnen es
wie Unity.

## 6. Weitere Varianten (`sight_kit_more.py`, Unteragent Opus, im Bild geprüft)

| ID | Name | für | Merkmal (1–2) | offen |
|---|---|---|---|---|
| `holo_octagon` | H6 Achteck | MG | Achteckhaube; blanke Fasenflächen | Fenster M 30 mm ≈ 22 % (über 20 %) |
| `holo_visor` | H7 Schirm | Automatik, Spur | Sonnenschild nach vorn; orange Schildkante | im Zielen wie H0 |
| `holo_crescent` | H8 Halbmond | Seitenwaffe | Sichelhaube rechts offen; orange Spitze | Glaskante rechts als feine Linie |
| `holo_flipcap` | H9 Klappe | Spur, MP | Schutzdeckel seitlich offen; orange Lasche | – |
| `fusion_rings` | F2 Doppelring | Fusion | zwei Ringe gestuft; Ladebogen cyan | etwas groß |
| `bow_pins` | B1 Pins | Bogen | drei Leuchtpins (sind das Absehen); Pinschiene | – |
| `scope_prism` | Z4 Prisma | Impuls, Scout kurz | Kastenobjektiv mit Flansch; Leuchtstreifen | Gehäuse unter dem Fenster sichtbar |
| `scope_peak` | Z5 Spitze | Scout | Ring mit Spitze oben; orange Marke | Spitze von außen kaum lesbar |
| `iron_ghost` | K3 Lochkimme | Schrot | Ghost-Ring; Kornring | – |
| `launcher_ladder` | W3 Leiter | Granatwerfer | Klappleiter mit Kerben; Stufenstriche | Leiter belegt das Feld über dem Zielpunkt |

Verworfen: Doppelfenster „Brille“ für das MG (Mittelsteg läge auf dem Absehen); Gleve und Schwert bleiben ohne Visier.

## 6a. Zuordnung je Waffentyp (Vorschlag)

| Typ | Standard | Varianten |
|---|---|---|
| Automatik | **H0 (bleibt, Nutzer: „optimal“)** | H1 Fase, H7 Schirm |
| Impuls | H4 Kasten | H5 Häkke-Ring, Z4 Prisma |
| Scout | Z1 Tropfen | Z5 Spitze, Z2 Gabel |
| Handfeuerwaffe | K1 Klammer | M1 Mini |
| Seitenwaffe | K1 Klammer | H8 Halbmond, M1 Mini |
| MP | H2 Pille | H3 Zinken, H9 Klappe |
| Schrot | K2 Hörner | K3 Lochkimme |
| Scharfschütze | Z3 Lang (Vollbild) | – |
| Fusion | F1 Bögen | F2 Doppelring |
| Lineare Fusion | Z2 Gabel | Z1 Tropfen |
| Spur | H3 Zinken | H9 Klappe, H7 Schirm |
| Granatwerfer | W1 D-Linse | W3 Leiter |
| Raketenwerfer | W2 Entfernung | W1 D-Linse (L) |
| MG | H6 Achteck | H1 Fase (L) |
| Bogen | B1 Pins | – |
| Schwert, Gleve | kein Visier | – |

## 7. Entscheidungen

**Nutzerwahl 26.10.2026** (Auswahl im Dialog): Richtung „Ja, v3 bauen“ – H0-Plattform für alle Visiere, Zuordnung nach Abschnitt 6a,
Automatik behält H0; Kimme/Korn „Tiefer, Schiene + 11 mm“; Größen „Zulassen für MG/Werfer“ (Holo L, Zielfernrohr S als Variante,
Visier-Standard 3 wird erweitert); Ablauf „Konzept committen, Bau neu“ (frische Sitzung, eigene Version). Punkte 1–4 unten sind damit
entschieden; Punkt 5 (Abriebmaske in `kit.py`) folgt mit der Bau-Version.

Die Fragen waren:

1. **Richtung:** Baukasten v3 (H0-Plattform) als Visier-Familie übernehmen? Sitz für Zielfernrohre nach Konzept A (Sattel hinter dem
   Auge, Fuß unter dem Objektiv) statt 0.19 „Rohr auf dem Gehäuse“ (Entscheidungsliste 1.1 A würde dafür geändert).
2. **Zuordnung je Waffe** (Vorschlag Abschnitt 6a): Standard je Typ und Varianten; Automatik behält H0.
3. **Kimme/Korn-Linie:** eigene Linie Schiene + 11 mm (≈ 51 mm über dem Lauf) statt 66 ± 4 mm – Abweichung vom Visier-Standard 3
   für Handfeuerwaffe/Seitenwaffe/Schrot; Mini-Reflex Schiene + 15 mm.
4. **Größen außerhalb des Standards:** Holo L (24,6 %) für MG/Werfer und Zielfernrohr S (17,4 %) zulassen oder streichen?
5. **Material:** neue Abriebmaske für dünne Teile (Messradius 4 → 1,2 mm) in `kit.py` – ändert den Unity-Quellenhash, voller Export.

## 8. Umsetzung danach (eigene Version, `./ce session reserve`) – erledigt in 0.21 „Ironsight“

**Erledigt (26.10.2026, [Bericht](versions/0.21-ironsight.md)):** Baukasten v3 in `basic/common.py` (Form `xprof` in `kit.py`, Rolle
`sight_anod` nach Punkt 5 = Antwort A), Visier-Standard 3 erweitert (Visierlinien, Varianten Holo L / Zielfernrohr S), Absehen in
Blender flach; BASIC-01 H0, BASIC-02 H4, BASIC-03 Z1 nach Konzept A, BASIC-06 H2; Unity-Export mit Backen für 01/03/06. Die bisher
visierlosen Waffen sind **nicht** Teil von 0.21 (Auftrag: zwei Hauptziele) – Zuordnung nach § 6a bleibt offen für eine eigene Version.


Baukasten in `basic/common.py` (Form `xprof` in `kit.py`), gewählte Visiere an BASIC-01/02/03/06 und den bisher visierlosen Waffen,
Visier-Standard 3 und Stilhandbuch § 6 anpassen (Profil, Sitz, Kimme-Linie), `test_sight_seat.py`, Export mit Backen, Unity-Vergleich
gegen frische Blender-Stills, Absehen in Blender flach.
