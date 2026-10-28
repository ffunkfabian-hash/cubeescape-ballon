# CHANGELOG

## 0.27.0 „Tracer“ – Spurgewehr BASIC-12 und Maschinengewehr BASIC-15 im Stil v2.1 (Branch `claude/ballon-0.27-tracer`)

- BASIC-12 v2.1: Creme-Haube in Linie mit der Schiene über dem freien runden Fokusrohr (drei Ringe, Griffband), umgreift Rohransatz und
  Kegel, Fokusscheibe beidseitig, Zelle vor dem Griff, Einteilkörper mit Daumenloch, kein Auswurf; BASIC-15 v2.1: Zuführdeckel mit Visier,
  Kasten seitlich links, flach und lang (Nutzerwünsche nach dem Zwischenstopp), Gurtsäule in einen Gurteinlauf (Nutzerwunsch „Eingang“), Mantel mit Fenstern, Tragegriff links,
  Hülse und Glied als `EJECT`-Daten, Gurtvorschub je Schuss (`cycle='shot'`). Grundform nach Zwischenstopp, Nutzerwahl „a“.
- Visiere H3 „Zinken“ (`sight_kit.zinken`, M 18,7 %) und H6 „Achteck“ L (`sight_kit.achteck`, 24,7 %) gebaut; `test_sights` prüft ihre
  Merkmale, `check` Gurtwaffe → Hülse und Glied sowie den Takt je Schuss.
- Quellen Q-D2-IMG (7 Vertreter über das Bungie-Manifest); Bericht [docs/versions/0.27-tracer.md](docs/versions/0.27-tracer.md).

## 0.26.0 „Kindle“ – Fusionsgewehr BASIC-10 und Lineares Fusionsgewehr BASIC-11 im Stil v2.1 (Branch `claude/ballon-0.26-kindle`)

- BASIC-10 v2.1: gerade Creme-Oberkante über quer offener Ladekammer (drei Spulenringe um den Glutkern), gestufter Schlitz-Emitter, Zelle vor
  dem Griff, Schaft S2 mit Daumenloch; BASIC-11 v2.1: offene Doppelschiene (oben Creme, unten Graphit) mit Leuchtkern und vier Spulen, stumpfe
  Gabel vor der Mündungsbrücke, Zelle hinter dem Griff, Schaft S1. Grundform nach Zwischenstopp, Nutzerwahl „a“; Ladekern als reine Emission
  (`charge_core`, „Kern weniger grell“). Energiewaffen ohne Hülsenauswurf (`EJECT = None`, `check` verlangt es bei Energiezelle BEC-1).
- Visiere F1 „Bögen“ (`sight_kit.boegen`, Glas Ø 26) und Z2 „Gabel“ (`sight_kit.gabel`, Sitz nach Konzept A) gebaut; `test_sights` prüft
  ihre Merkmale, `test_sight_seat` den Sitz von Z2.
- Quellen Q-D2-IMG (6 Vertreter über das Bungie-Manifest); Bericht [docs/versions/0.26-kindle.md](docs/versions/0.26-kindle.md).

## 0.25.0 „Longshot“ – Schrotflinte BASIC-08 und Scharfschützengewehr BASIC-09 im Stil v2.1 (Branch `claude/ballon-0.25-longshot`)

- BASIC-08 v2.1: gerade Oberkante aus Schiene und Lüftungsschiene über dickem Lauf und Röhrenmagazin, große Graphit-Pumpe, Ladeschacht mit
  Ladeklappe, eigene Hülsenform `shotshell`; BASIC-09 v2.1: Creme-Gehäuse und Laufmantel mit Längsschlitz, freier Lauf mit Bremse,
  Kammerstängel links (Nutzerwunsch), Zielfernrohr mittig über dem Gehäuse (Nutzerhinweis). Grundform nach Zwischenstopp, Nutzerwahl „a“.
- Visiere K2 „Hörner“ (`sight_kit.hoerner`) und Z3 „Lang“ (`sight_kit.lang`, Vollbild, Sitz nach Konzept A) gebaut; `check`,
  `test_sights`, `test_sight_seat`, `make_docs` kennen den Vollbild-Typ und Hülsenformen im Modul (`EJECT_CASES`).
- Quellen Q-D2-IMG (6 Vertreter über das Bungie-Manifest); Bericht [docs/versions/0.25-longshot.md](docs/versions/0.25-longshot.md).

## 0.24.0 „Holster“ – Handfeuerwaffe BASIC-04 und Seitenwaffe BASIC-05 im Stil v2.1 (Branch `claude/ballon-0.24-holster`)

- BASIC-04 v2.1: lange gerade Creme-Haube über freistehender, kannelierter Trommel auf Kran, Kastenunterlauf mit Fenster zum Lauf;
  BASIC-05 v2.1: hoher Schlitten mit dunkler Kappe, Auswurffenster und Magazin auf der Griffachse. Grundform nach Zwischenstopp, Nutzerwahl „a“.
- Visier K1 „Klammer“ gebaut (`sight_kit.klammer`, Linie Träger + 11 mm); `check`, `test_sights` und `make_docs` kennen Kimme/Korn.
- Quellen Q-D2-IMG über das Bungie-Manifest; Bericht [docs/versions/0.24-holster.md](docs/versions/0.24-holster.md).

## 0.22.0 „Volley“ – Impulsgewehr BASIC-02 und Portalkanone BASIC-T01 spielbar (Tasten 4 und 5) (Branch `claude/ballon-0.22-volley`)

- Schritt 6 der [Entscheidungsliste](docs/entscheidungsliste-motiongen.md) für die Klasse Impuls: eigene Hüfte (Mündung 57,9/63,4 %, mit der
  Automatik-Hüfte lag sie bei 59,7 % außerhalb des Bands), Sprint wie die Automatik, Anflug 20 Bilder bei 60/s, Weltzoom 2,0, `ring_dot`;
  Feuerart **Salve** aus der Spec (`burst_3`): 3 Schuss im Takt 900/min, Salvenbeginn alle 0,333 s (540/min wie Gridskipper), Magazin 36,
  Bahnstufe 4,0 % H je Salve, Erholung je Klasse (≈ 80 % zwischen den Salven); Mündungsfeuer im Zielen 13,5 % der H4-Öffnung, Hülsen über `EJECT`.
- Portalkanone als Klasse „Werkzeug“ (Nutzerwahl A über Sightline): Linksklick Portal A (Cyan, Ring 120° im Uhrzeigersinn), Rechtsklick
  Portal B (Orange, gegen den Uhrzeigersinn), kein Zielen, kein Nachladen, Abklingzeit 0,25 s, Reichweite 24 m, Treffermarke in Portalfarbe;
  Hüfte nach Portal 2, auf Nutzerhinweis quer gestellt, damit beide Kerne sichtbar sind; Sprint E. Präzision (X) zurückgestellt (EXT-18).
- Format `ballon-ego/10`: Salve, Bahnstufe und Erholung je Klasse in `gameplay`, Portale, `weapon.live.ring`; Klassen ohne Zielen/Nachladen
  lassen diese Aktionen weg (Unity schaltet nach den Daten, nicht nach der Waffen-ID). Leser liest `/9`–`/7`; `/9` von main als Fixture,
  Automatik, MP und Scout Feld für Feld unverändert. Export: Leuchtrollen aus Modulen nicht im Atlas (Lehre). Bericht [docs/versions/0.22-volley.md](docs/versions/0.22-volley.md).

## 0.21.0 „Ironsight“ – Visier-Baukasten v3 als Produktionsform, Visiere an BASIC-01/02/03/06 (Branch `claude/ballon-0.21-ironsight`)

- Baukasten v3 in `basic/common.py` (Nutzerwahl „v3 bauen“): H0-Plattform `sight_platform`, Flachprofil `xprof` (neue Form in `kit.py`),
  Haube, flache Scheibe, gezeichnetes Absehen `drawn_reticle` (Hüftform der Klasse flach in der Glasebene, ≥ 1,6 px, reine Emission);
  gebaut H0 (BASIC-01, unverändert bis aufs Absehen), H4 „Kasten“ (BASIC-02), H2 „Pille“ (BASIC-06, 19 × 23 mm wegen Mündungsfeuer ≤ 20 %, gemessen in der Pillenkontur),
  Z1 „Tropfen“ (BASIC-03) mit Sitz nach Konzept A (Wiege hinter dem Auge, Klemmfuß unter dem Objektiv, Ring 1,29 ohne Wulst).
  `sight_kit.py` nutzt dieselben Bausteine (25 Visiere im Katalogblatt v3).
- Visier-Standard 3 erweitert: Visierlinien Schiene + 26/15/11 mm (Holo-Plattform/Mini-Reflex/Kimme-Korn; Zielfernrohr nach Visierhöhe), Varianten Holo L (MG/Werfer ≤ 25 %) und
  Zielfernrohr S (≥ 17 %), Öffnung als lichte Öffnung im echten Abstand; Stilhandbuch § 4/§ 6, `absehen.md`, Entscheidungsliste 1.1.
- Abriebmaske (Nutzerwahl A): Rolle `sight_anod` für alle Visierteile, Messradius 1,2 mm, ohne feine Kratzer; Leuchtrolle `sight_line`.
- Prüfungen: neu `tools/test_sights.py` (Öffnung je Visier und Größe, Ring 1,29, Absehen flach, Kimme-Linie), `test_sight_seat.py` auf
  Konzept A (Sattel hinter dem Auge, unteres Bilddrittel frei); Unity-Formattests ohne die bewusst geänderte Baugruppe Visier.
- Export: Bauteil-Hash `parts_sha256` gerundet (plattformfest, CI unter Linux). Export mit Backen für BASIC-01/03/06 und Arme; Bericht [docs/versions/0.21-ironsight.md](docs/versions/0.21-ironsight.md).

## Patch visier-konzept – Visier-Konzept und Baukasten v3 (Branch `claude/ballon-patch-visier-konzept`)

- Konzept nach 0.20: Befund (Destiny, BF6, Formgen VS01–09; Platte vor dem Auge, Ringwulst, Abriebmaske), Sitz-Konzepte A/B/C und
  Visier-Baukasten v3 mit 25 Entwürfen auf der H0-Plattform (BASIC-01) – [docs/visier-konzept.md](docs/visier-konzept.md), Nutzerwahl „v3 bauen“.
  Entwurfswerkzeuge `tools/sight_options.py`, `tools/sight_catalog.py`, Quellen `basic/pilot/optics/sight_*.py`; Modelle und Unity unverändert.

## 0.20.0 „Spotter“ – Scout BASIC-03 spielbar (Taste 3, Zielfernrohr, Einzelfeuer, gezeichnetes Absehen) und kleinere Texturen (Branch `claude/ballon-0.20-spotter`)

- Entscheidung 97 A: Waffenatlanten und Skins je Kanal kleiner abgelegt (`export_unity.TEXTURE_STORE`: albedo JPG 4096, spec PNG 2048,
  normal PNG 8 bit 4096, ao PNG 8 bit 2048), aus der Exporteinstellung: BASIC-01 145,7 → 39,6 MB, BASIC-06 189,4 → 43,8 MB, BASIC-03 40,6 MB;
  Grenze 50 MB je Waffe in `./check` und Unity-Test. Ego-Bild Hüfte vorher/nachher SSIM 0,999, Kanten, Schrift, Sprenkel unverändert.
- Schritt 6 der [Entscheidungsliste](docs/entscheidungsliste-motiongen.md) für die Klasse Scout: Hüfte und Sprint wie die Automatik (Mündung
  57,0/62,7 %), Anflug 7 Bilder bei 30/s = 17 Bilder bei 60/s, Weltzoom 2,0 (Beginn bei 20 % des Augenwegs), Hüft-Fadenkreuz `cross`,
  180/min Einzelfeuer aus der Spec, Magazin 15, Hülsen `rifle`. Zielfernrohr in Unity nach Visier-Standard 3 (eine Kamera, Okular/Rohr/Türme
  im Linsenbild aus, Öffnung 21,5 % B, Glas ≤ 3 % heller). Nutzerwunsch: Absehen aller Waffen in Unity gezeichnet in Hüftform (Cyan).
  Glas und Leuchten nach URP-Reimport repariert. `ego.json` jetzt `ballon-ego/9`, der Leser liest `/8` und `/7` weiter. Tasten 1/2/3, Q reihum.
  Bericht [docs/versions/0.20-spotter.md](docs/versions/0.20-spotter.md).

## 0.19.0 „Saddle“ – Scout BASIC-03 v2.1: Zielfernrohr direkt auf dem Gehäuse (Branch `claude/ballon-0.19-saddle`)

- Schritt 7 der [Entscheidungsliste](docs/entscheidungsliste-motiongen.md) (1.1 A, Prüfung 1a): Gehäusebuckel unter dem Rohr mit kurzer Schiene,
  Rohrsattel statt Trapezhals, Spannband `scope_strap` mit `ads_hide`. Spalt Rohr–Gehäuse 21,5–25,5 → 0,3 mm, Visier über Gehäuse 0,051 → 0,030 L,
  Visierhöhe 65 mm; 1a unverändert 1,31 / 1,56. Neuer Test `tools/test_sight_seat.py` in `./check` (am Netz, rot mit altem Modell).
  Bericht [docs/versions/0.19-saddle.md](docs/versions/0.19-saddle.md).

## 0.18.0 „Quickdraw“ – Ego-Übertrag je Klasse, Maschinenpistole BASIC-06 spielbar (Branch `claude/ballon-0.18-quickdraw`)

- Schritt 6 der [Entscheidungsliste](docs/entscheidungsliste-motiongen.md) (2.1 A, 3.2 A, 4d) für die erste Klasse, die MP „Kurzläufer v2.1“:
  Klassenwerte als Daten (`ego.CLASSES`): Hüfte Mündung 58,0/62,9 %, Absehen 65,5/60,0 % (Destiny-MP 57–58/61–62); Sprint tief, Oberseite
  +40° nach links, Mündung 42,9/79,9 % (Destiny 43/80); Anflug 3 Bilder bei 30/s = 12 Bilder bei 60/s bis Ruhe (Destiny-MP 8–12, Automatik
  unverändert 20). Weltzoom 1,45, Hüft-Fadenkreuz `circle_cross` 6,1 % H, 720/min, Magazin 30, Hülsen `pistol`. Automatik unverändert.
- Ego-Pipeline je Waffe: `ego.profile(W)`, Modul-Felder `EGO_GRIPS`/`EGO_LIVE`/`EJECT`, Export backt nur Geändertes; `ego.json` jetzt
  `ballon-ego/8` mit `weapons[]`, der Unity-Leser liest `/7` weiter. Unity: zwei Waffen, Tasten 1/2 (Q zur anderen) über holster/draw mit
  leerer Sicht 0,133 s, Munition je Waffe, Wechsel ohne Speicher je Bild. MP-Stützhand als Faust am Vordergriff (Nutzerhinweis Daumen).
  Bericht [docs/versions/0.18-quickdraw.md](docs/versions/0.18-quickdraw.md).

## 0.17.0 „Gateway“ – Portalkanone BASIC-T01 im Stil v2.1 (Branch `claude/ballon-0.17-gateway`)

- Erstes Werkzeug der Familie (`basic/pilot/t01_portal_cannon_v21.py`): facettierte Eischale, offener Zweifarbkern (Portal B Orange
  hinten, Portal A Cyan vorn, Farben aus Cube Escape), gestufter Emitter, Ring auf drei Speichen (dreht 120° je Schuss), Unterlippe mit
  Vordergriff, Familiengriff; kein Visier, Kerbe als Leitkante. Nach Portal-2-Prinzip im BALLON-Stil (Nutzerwahl P2). 26 Teile, 404 mm.
- `./check` prüft Werkzeuge (`t*_v21.py`), `test_motion.py` auch die v2.1-Module; Familienmaße und Familienseite mit Werkzeugen.
  Bericht [docs/versions/0.17-gateway.md](docs/versions/0.17-gateway.md).

## 0.16.0 „Flash“ – Mündungsfeuer und Hülsen in Blender und Unity (Branch `claude/ballon-0.16-flash`)

- Schritt 5 der [Entscheidungsliste](docs/entscheidungsliste-motiongen.md) (5.3 A, dazu 5.4 A seit 26.10.2026): Blitz an `Socket_Muzzle`, 1 Bild bei
  30/s (Unity gleich lang: 60/s 2 Bilder, 144/s 5), fast weißer Kern und vier Seitenflammen in Cyan, reine Emission ohne Bloom; im Zielen
  ≤ 13,1 % der Holo-Öffnung (Grenze 20 %, `./check` und Unity-Test). Messinghülse je Schuss aus dem Auswurffenster nach rechts, mit Drehung,
  0,4 s; Waffen-Feld `EJECT`, Unity-Pool aus 6 Hülsen ohne GC. Form und Bahn einmal in `basic/arms/ego.py`. `ego.json` jetzt `ballon-ego/7`.
  Bericht [docs/versions/0.16-flash.md](docs/versions/0.16-flash.md).

## 0.15.0 „Plumb“ – Haltung, Bewegung und Rückstoß nach Destiny (Branch `claude/ballon-0.15-plumb`)

- Schritt 4 der [Entscheidungsliste](docs/entscheidungsliste-motiongen.md) (2.1 A, 3.1 A, 6.1 A, 1d, 5.1 A, 5.2 A): Hüfte tiefer (Mündung
  x 58,1 / y 63,1 % statt 49,6 %), Sprint-Hub 22/18 mm (Oberkante ≈ 9 % H, linke Kante ≈ 13 % B), Waffenwechsel mit Q (Wegstecken
  0,27 s, leere Sicht 0,13 s, Ziehen wie bisher), Weltzoom folgt dem Modell, Rückstoß in vier Größen: im Zielen wandert die Welt (Viererstoß
  4,3 % H), das Visier steht (0,12 % H); feste Säule 1 % H je Schuss mit ≤ 1,6 % B Seitenwackeln, Erholung nach der Salve, Salvenwaffen.
  Clip-Schussbilder auf 720/min (2,5 Bilder). `ego.json` jetzt `ballon-ego/6`. Bericht [docs/versions/0.15-plumb.md](docs/versions/0.15-plumb.md).
- Patch einschuss (Nutzerbild 26.10.2026: „Die Einschusslöcher werden so breit schwarz“): Ab dem 81. Treffer bekam ein wiederverwendetes
  Loch seine Größe noch im Maßstab des alten Trägers (Wand 20 m breit → Loch 1 m breit). Jetzt erst lösen, dann Weltgröße 5 cm setzen;
  Test `Einschussloecher_behalten_ihre_Groesse_beim_Wiederverwenden` (mit alter Reihenfolge rot).

## 0.13.0 „Hipfire“ – Weltzoom je Klasse und Hüft-Fadenkreuz (Branch `claude/ballon-0.13-hipfire`)

- Schritt 3 der [Entscheidungsliste](docs/entscheidungsliste-motiongen.md) (1.2 A, 4.1 A, 4.2 A): Weltzoom nach Glidepath (Scout 2,0,
  Handfeuerwaffe 1,15, MP 1,45; Unity zoomt mit dem Klassenwert, Automatik 1,9 statt fest 1,35); Hüftformen `ring_dot` (Automatik,
  Impuls, MG), neu `brackets` (Handfeuerwaffe) und `caret` (Scharfschütze, Sprint der Automatik) mit Größen in % der Bildhöhe;
  ausblendendes Hüft-Fadenkreuz in Unity (`HipReticle.cs`). `ego.json` jetzt `ballon-ego/5`. Bericht [docs/versions/0.13-hipfire.md](docs/versions/0.13-hipfire.md).

## 0.11.0 „Compact“ – in Arbeit (Branch `claude/ballon-0.11-compact`)

- BASIC-06 Maschinenpistole im Stil v2.1: Kastenvorbau, Abzugsbügel und Bügel als ein Band, Magazin auf der Griffachse mit
  Sichtfenster, Holo mit Absehen `dot`; drei Sichtungsrunden, 8 Skins, Bewegung gesichtet.
- Namen geklärt (Nutzerwahl (a)): Stil v2.1 = Waffenstil, Visier-Standard 3 = Visierregeln (früher „Visier-Designsprache v3“), kein Waffenstil v3.
  Bericht [docs/versions/0.11-compact.md](docs/versions/0.11-compact.md).
- Patch: Familienmaße v2.1 aus den Specs ([docs/familienmasse.md](docs/familienmasse.md), `make_docs.py`); v2.1-Specs in `data/specs/`,
  `./check` vergleicht sie mit dem Entwurf. Stilhandbuch §6: alle Familienbausteine mit Parametern und Nutzung, Muster im Waffenmodul.
- Patch: Entscheidungsliste Motiongen REF 0.14–0.28 ([docs/entscheidungsliste-motiongen.md](docs/entscheidungsliste-motiongen.md)):
  20 Nutzerantworten vom 25.10.2026 in 8 Blöcken, acht Glidepath-Widersprüche mit dem Wert, den BASIC bis zur Klärung nutzt,
  und eine Umsetzungsreihenfolge in 8 Schritten. Nichts gebaut oder gerendert.
- Patch: Messungen zu Schritt 2 der Entscheidungsliste (Hüftlage, Scout-Ring, Sprint-Hub, Zoom gegen Modell) in
  [docs/entscheidungsliste-motiongen.md](docs/entscheidungsliste-motiongen.md) › Messungen und `data/review.json`; nur gemessen, kein Wert geändert.
  Werkzeuge `tools/messen.py`, `tools/messen_bild.py`; Unity-Aufnahme mit `-ballonFps` und `-ballonKey` (nur Messhilfe).
- Patch: Unity-Abgleich (Entscheidungsliste Schritt 1): Kadenz 720/min wie `fire_hip` bei jeder Bildrate (Übertrag statt Abrunden), Pendeln kritisch gedämpft (Rückkehr 0,30 s,
  kein Überschwingen), Schuss-Ring und Treffer-X in Orange nach Visier-Standard 3 §6 (ohne HUD-Punkt), Test Nachlade-Abbruch vor/nach
  `MagIn`, Herkunft `inspect` „Apex/CoD-Muster“. Vier neue PlayMode-Tests; Belege `unity_run.py sway|treffer`.

## 0.6.0 „Riflekin“ – unveröffentlicht (lokal, in Arbeit)

- Visier-Designsprache v3 nach Motiongen REF 0.14 „Eyebox“: Typ je Klasse, dünne Rahmen, kleinere Öffnungen (geprüft), Trapezsockel/-hals, eine Kamera, Absehen fein ohne Aufgehen im Zielen, Glasspuren nur am Rand.

- BASIC-02 Impulsgewehr im Stil v2.1 (geschlossene Impulskammer, Spulenfenster, Salvenanzeigen, Holo-Visier, S2 mit Daumenloch).
- Familienbausteine `grip_v21`, `reflex_sight_v21`, `reticle`, `cut_box`, `screws`, `mirror`; Absehen auch im Pilot.
- `./check` prüft die v2.1-Familie; Familienseite `make_sheets.py --family`; Stilhandbuch §7 Dokumentationspflicht.
- Absehen-Katalog `basic/reticles.py` (7 Formen, 5 Farben, 3 Stärken, 6 Glasvarianten, Aufgehen, Vorgaben, Optionen), Export `data/reticles.json`/`docs/absehen.md`, Katalogblatt und Aufgeh-Clip.
- BASIC-03 Scoutgewehr v2.1 mit Zielfernrohr `scope_v21`; Formskizze per Blender-MCP.
- Visier-Standard v2 nach Destiny-Video und Motiongen: schlanke Visiere, Zielfernrohr mit Linsenbild und `ads_hide`, Augenpunkt 90 mm vor der Öffnung, Modell ungezoomt, Weltzoom je Klasse; Prüfung in `./check`, Beispiele `tools/sight_examples.py`.

## 0.10.0 „Stride“ – in Arbeit (Branch `claude/ballon-0.10-stride`, öffentliches Repo)

- Sprint-Wippen wie in Destiny 2 gemessen (Motiongen REF 0.23): 3,16 statt 6 Schritte/s, U-Bogen, Rollen ±3,5°. Das Zielen endet ohne Überschwingen (0.9: 3,3° über die Mitte), mit eigener schneller,
  kritisch gedämpfter Feder; Format `ballon-ego/4`. Das ständige Fadenkreuz ist entfernt, nur Treffer zeigen kurz eine Marke.
- Datenexport ohne Backen (`BALLON_EXPORT_DATA_ONLY=1`, 2 s, `ce lock blender`). Beleg `unity_run.py feel`. Übergabe an Motiongen
  je Waffentyp. Bericht [docs/versions/0.10-stride.md](docs/versions/0.10-stride.md).

## 0.9.0 „Parcours“ – unveröffentlicht (lokal)

- Hangar mit Detail wie die Waffe (Fasen, Trapezblech, Nieten, Fugen, Schilder, Abrieb, Schmutz; 68 946 Dreiecke), Zonen-Atlanten
  bis 1,23 cm je Texel, vier Lichtszenen Tag/Abend/Nacht/Bewölkt (Taste N). Format `ballon-scene/2`.
- Parcours mit 151 m Strecke, 5 Kontrollpunkten, 14 Zielscheiben, Richtzeit 45 s und Bestzeit; Taste T zurück zum Start.
- Vorführlauf (`RouteRunner`): MP4 `unity_run.py course`, Leistung `bench hangar`, Test „Vorführlauf schafft jeden Parcours“.
  Bericht [docs/versions/0.9-parcours.md](docs/versions/0.9-parcours.md).

## 0.8.0 „Hangar“ – unveröffentlicht (lokal)

- Hintergrundszene Hangar aus Python-Daten (`basic/scenes/hangar.py`), in Blender gebaut mit gebackenem Cycles-Licht
  (`tools/scene_build.py`). Format `ballon-scene/1` ([docs/szenen-format.md](docs/szenen-format.md)).
- Unity: Szenenlader, Taste L (Parcours ↔ Hangar), Viewmodel-Licht aus denselben Daten. Vergleich vom Startpunkt: SSIM 0,885,
  PSNR 26,0 dB.
- Fix: AO beim Backen der Waffe war zu dunkel (Originale unter der zusammengefügten Kopie). Gebaut mit zwei Unteragenten;
  Bericht [docs/versions/0.8-hangar.md](docs/versions/0.8-hangar.md).

## 0.7.2 – unveröffentlicht (lokal)

- Acht Waffen-Skins aus `kit.SKINS` gebacken (Farbe und Glanz je Skin, Normale und AO geteilt). In Unity schaltet Taste K
  durch; Kontaktbogen über `unity_run.py skins`. Doku: Grenzen und Entscheidung „Restabweichungen bleiben“.

## 0.7.1 – unveröffentlicht (lokal)

- Spezular-Modus mit gebackener Spiegelfarbe (Polymer wieder mattschwarz). Armsegmente werden zum Backen auseinandergelegt (keine
  schwarzen Streifen am Handrücken), Abrieb mit 64 Samples. Über Waffe und Arme Abweichung −25 bis −40 % gegenüber 0.7.

## 0.7.0 „Truecolor“ – unveröffentlicht (lokal)

- Unity folgt Blender so nah wie möglich (dauerhafte Regel in AGENTS.md):
  - Material aus `kit.aaa_nodes` in Atlanten gebacken (`tools/bake_unity.py`): Farbe mit Abrieb und Schmutz, Metall und
    Glätte, Normale, AO.
  - Blender-AgX als 3D-LUT im Vollbild-Durchgang, HDR an.
  - Studiolicht und Hintergrund wie `setup_aaa`.
- Vergleich mit Kennzahl über Waffe und Arme (`unity_run.py compare`, Maske): Abweichung −14 bis −31 %, SSIM im Ausschnitt
  0,74–0,81 → 0,78–0,85. Ganzes Bild PSNR +3–5 dB. Leistungsmessung
  (`unity_run.py bench`). Bericht [docs/versions/0.7-truecolor.md](docs/versions/0.7-truecolor.md).

## 0.4.0 „Firstfeel“ – unveröffentlicht (lokal)

- Eigenes Unity-6-Projekt `unity/` (URP, Input System): Pilotwaffe BASIC-01 v2.1 mit Roboterarmen v3 spielbar aus der Ego-Perspektive im grauen Testparcours (Zielscheiben 10/25/50 m); macOS-Entwicklungsbuild.
- `tools/export_unity.py` (FBX + `ego.json` im Format `ballon-ego/1` + Blender-Referenz), `tools/unity_run.py` (Einrichten, Tests, Build, Aufnahme, Vergleich); `./check` prüft, ob `ego.json` aktuell ist.
- Ego-Laufzeit in C# aus denselben Daten und Formeln wie `tools/ego_build.py` (Bewegung v2), live mit Rückstoßfeder, Feder-Nachlauf, Pendeln, Wippen, Atmen; 8 EditMode- und 11 PlayMode-Tests. Doku [docs/unity.md](docs/unity.md), Bericht [docs/versions/0.4-firstfeel.md](docs/versions/0.4-firstfeel.md).

## 0.3.0-ego „Handshake“ – unveröffentlicht (lokal)

- Eigenes Roboterarm-Rig (`basic/arms/robot_arm.py`) und Ego-Daten (`basic/arms/ego.py`): 10 Haltungen, 4 Griffe, 19 Aktionen inkl. Übergänge; getrennt von Toolgen/Cube Escape.
- `tools/ego_build.py` (Szene, Arm-Lösung, Render), `tools/make_ego.py` (Clips, Kontaktbögen, Doku `docs/ego.md`, Ergebnisseite, Prüfung in `./check`).
- Arm v3 nach Nutzerbildern (gewölbte Schale, Medaillon-Ellbogen, Drehgelenk, vier Finger, +15 %); Formen `hull`/`plate`/`prism`; `tools/arm_preview.py`; Spaßfigur `robot_figure.py` + `tools/robot_build.py`.
- Bewegungsgefühl: Hermite-Kurven statt Stopp je Schlüssel, Feder-Nachlauf der Waffe, Atmen in jeder Aktion, Rückstoßfeder, Tempo 1,25, volle 30 fps, Nachladen neu choreografiert.
- Stilhandbuch › Arme und Animation; Bericht [docs/versions/0.3-ego.md](docs/versions/0.3-ego.md).

## 0.2.0-pilot „Inspect“ – unveröffentlicht (lokal)

- Pilot Stil v2 (Destiny-Detaildichte + AAA-Material, schlicht): `basic/pilot/w01_auto_rifle_v2.py`, Ausgabe `BASIC-01-v2`; Reihe unverändert.
- Baukasten: Durchbrüche (Exact-Boolean), `multi`, `tube`, `text`, AAA-Shader (Abrieb, Schmutz, Kratzer, Stippling), Skins (8 Farb-/Texturvarianten), Render `--aaa`, `--skins`, Perspektive `hero_p`, Bloom standardmäßig aus.
- [Stil- und Bauhandbuch](docs/stilhandbuch.md) für künftige Varianten; Bericht [docs/versions/0.2-pilot.md](docs/versions/0.2-pilot.md).
- v2.1: Magazintrichter, ergonomischer Griff, gekrümmtes Magazin, verjüngte Visierhaube und Handschutz; Hintergrund grau als Standard (`--bg mid`); dezenter Abrieb an dunklen Teilen.

## 0.1.0 „First Light“ – unveröffentlicht (lokal)

- Neues Projekt für die Waffenreihe BASIC (Entscheidung des Nutzers 24.10.2026), Begründung und Schnittstellen in [docs/PROJEKT.md](docs/PROJEKT.md).
- Blender-Baukasten (`basic/kit.py`, `basic/common.py`) und 17 BASIC-Entwürfe (`basic/weapons/`), je Waffe Hierarchie Waffe → Baugruppe → Bauteil, Anker, Bewegungen.
- Gemessene Specs `data/specs/` (Format `cubeescape-ballon/basic-spec` v1), Designvertrag, Abdeckungs- und Haltungsmatrix, Bauteilblätter, Quellen- und Erweiterungsverzeichnis.
- Werkzeuge: Bau, Blätter, Clips, Kontaktbögen, Doku, `./check`. Bericht [docs/versions/0.1.md](docs/versions/0.1.md).
