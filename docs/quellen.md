# Quellenverzeichnis BASIC

Stand 24.10.2026. Status-Begriffe: **gemessen** (Zahl aus Messung mit Methode), **beobachtet** (gesehen, nicht vermessen),
**abgeleitet** (aus Quelle geschlossen), **entworfen** (Entscheidung dieses Projekts), **offen** (fehlt). Lokale Repos unter `~/Claude/`.

## Q-CE · Cube Escape und Toolgen (Schnittstellen, gelesen 24.10.2026)

| ID | Inhalt | Fundstelle | Status |
|---|---|---|---|
| Q-CE-01 | Roboter 1,50 m, Arm 0,42 m, Hand 0,09 m, Schultern 0,82 m hoch / 0,56 m breit | CE `Docs/EQUIPMENT.md:256`, Toolgen `weapon_kit.py:331` | gemessen (CE, 17.10.2026) |
| Q-CE-02 | Roboter-Variante: Stützhand ≤ 0,10 m vor `Socket_Hand`, Schaft ≤ 0,12 m dahinter, Lauf ≥ 0,03 m, Gehäuse ≥ 0,08 m | Toolgen `weapon_designs.py:742`, CE `EQUIPMENT.md:283` | gemessen/festgelegt |
| Q-CE-03 | Ego-Hand: Handfläche 0,082 × 0,086 × 0,042, Fingerglieder 0,034/0,027/0,022 (Handeinheiten × 0,65 × 1,4), Fingerposen open/grip/trigger/underhand/cup/wrap/mag_hold/pinch | Toolgen `data/ego_arms.json:13` | gemessen (Datenstand) |
| Q-CE-04 | Ego-Arm Oberarm 0,32 m, Unterarm 0,30 m, Handgelenk Ziel 45°/Grenze 55° | Toolgen `data/viewmodels.json:996-1012` | Datenstand |
| Q-CE-05 | Waffenzustände Hidden/Draw/Ready/Fire/Holster/Inspect/Empty; Aktionen Fire/Charge/Reload/Draw/Holster/Inspect/Activate; Abbruchgründe Sprint/Switch/Fire/Locked/Any/View/Release | CE `Items/WeaponStateMachine.cs:8-10`, `Toolgen/EquipmentActions.cs:6-12` | Code gelesen |
| Q-CE-06 | Priorität: Sperre/Tod/Menü > Holster/Draw > Reload (bis MagIn) > Fire/Activate > ADS/Präzision > Sprint > Inspect > Idle/Walk | CE `Docs/FIRST_PERSON_EQUIPMENT.md:760-780` | Doku gelesen |
| Q-CE-07 | Ebenen: Posendaten (Hüfte, ADS, Sprint, Lowered, Air), prozedural (Sway, Trägheit, Bob, Landung, Rückstoß, Kamera), Clips (Fire, Reload, Draw, Holster, Inspect, Charge, AutoFire, Burst) | CE `FIRST_PERSON_EQUIPMENT.md:497-507` | Doku gelesen |
| Q-CE-08 | Marker Fire/Shot, MagOut, MagIn, Chamber, Ready, Holstered, Aimed, HandOff, HandOn | CE `FIRST_PERSON_EQUIPMENT.md:630-668`, `Docs/EGO_CLIPS.md` | Doku gelesen |
| Q-CE-09 | Ego-Clips `<Name>_Idle/Walk/SprintIn/Sprint/SprintOut/Fire/AimIn/AimIdle/AimFire/AimOut/Draw/Holster/Inspect_A/Inspect_B/Reload` (+ ReloadEmpty, AutoFire, Burst, Charge) | Toolgen `docs/UNITY_EINBAU.md:198-231`, `docs/EGO_CLIPS.md` | Datenstand |
| Q-CE-10 | Toolgen liest `cubeescape-design/geometry-spec` v1 (Netze, Anker, Griff, Stützhand, Visier); `string`/`melee` werden nicht gelesen | Toolgen `scripts/tool_assets/concept_spec.py:82-400` | Code gelesen |
| Q-CE-11 | Dreiecksbudget LOD0 Welt 6 000 (Pistole) – 10 000 (Scharfschütze, Fusion, Rakete); neue Typen ohne Budget | Toolgen `data/game_budget.json:4-31` | Datenstand |
| Q-CE-12 | In CE angebunden: pistol, assault_rifle, pulse_rifle, shotgun, sniper_rifle, smg, fusion_rifle, trace_rifle, rocket_launcher, scout_rifle; kein Bogen | CE `Assets/Resources/Equipment/definitions/` | Datenstand |
| Q-CE-13 | Portale: A = Cyan (1; 0,85; 0,1 → `#1AD9FF`), B = Orange (1; 0,45; 0,08 → `#FF7314`) | CE `Assets/Scripts/Portals/Portal.cs:59`, `Assets/Scripts/Levels/BlockColors.cs:35-37` | Code gelesen (26.10.2026) |
| Q-CE-14 | Portalgerät: Linksklick A, Rechtsklick B, mittlere Taste schließt beide, R dreht das nächste Portal um 90°; Zielen nur mit X als „Präzision“ ohne Visier | CE `Docs/PORTALS.md:10-20`, `Docs/FIRST_PERSON.md:22` | Doku gelesen (26.10.2026) |
| Q-CE-15 | Abklingzeit 0,25 s, Reichweite 24 m (Level 4–60 m), Sichtlinie Pflicht | CE `Portals/PortalEmitter.cs:41`, `Portals/PortalRules.cs:29,77` | Code gelesen (26.10.2026) |
| Q-CE-16 | Toolgen „Portalkanone“: weißes Gehäuse, Portalring, etwa 606 × 226 × 351 mm (Erstentwurf), Anker Hand/Muzzle/SupportHand | Toolgen `outputs/Portalkanone/README.md:34`, `scripts/tool_assets/Portalkanone/create_portal_gun.py:235-237` | Datenstand; Form nicht übernommen (BASIC-T01) |
| Q-CE-17 | Vorbild Portal-2-Portalgun (Bild des Nutzers, 26.10.2026): weiße Eischale hinten, offener Leuchtkern im Glas, gestufter schwarzer Emitter mit heller Unterlippe, drei Klauen – übernommen nur Eischale, offener Kern, Stufen, Unterlippe; Klauen nicht (Nutzerwahl Ring). Ego-Messungen der Portalkanone (Hüftlage, Bob, Schuss) für später | Nutzerbild (nicht im Repo); `cubeescape-reference/docs/portal2.md:27-38` | Prinzipien beobachtet; Messungen gelesen, nicht verwendet |

## Q-FG · Formgen (Bezugslängen und Typen)

| ID | Inhalt | Fundstelle | Status |
|---|---|---|---|
| Q-FG-01 | Bezugslängen KG01–KG10 aus Toolgen-Weltmodellen (Pistole 0,243, Sturmgewehr 0,934, Impuls 0,862, Schrot 0,904, Scharfschütze 1,134, MP 0,616, Fusion 0,960, Spur 1,044, Rakete 0,725, Bogen 1,018 m) | Formgen `claude/generator/export_spec.py:26-36`, `KGnn.spec.json › units` | gemessen (Toolgen 0.13, 17.10.2026) |
| Q-FG-02 | Bezugslängen KG11–KG18 (Scout 1,00, Handfeuerwaffe 0,32, Linear 1,30, GL 0,78, MG 1,15, Schwert 1,10, Glefe 1,40 m) | Formgen `wtypes.py:36-68` | abgeleitet (Schätzung claude-0.10) |
| Q-FG-03 | Zielfernrohre nur an Präzisionswaffen (Scout, Scharfschütze, Linear, Armbrust); Impulsgewehr Holo | Formgen `claude/docs/ENTSCHEIDUNGEN.md` (22.10.2026), `vsmount.py:22-26` | Entscheidung des Nutzers |
| Q-FG-04 | Formstudie-Vorlage KG02 „Kantenläufer“ (Variante G) | Formgen `claude/output/sheets/KG02.dc.html`, Bild `docs/reference/BASIC-Referenz-Formgen-KG02.webp` | vorhanden |

## Q-REF · Destiny-2-Messungen (Motiongen, Repo `cubeescape-reference`)

Einzelbeispiele je Beispielwaffe, keine Typmittelwerte (Motiongen `docs/destiny2.md:466-488`, `docs/auswertung.md:40-113`,
Zeitstempel in `data/clips.json`). Diese Werte speisen die vorgeschlagenen Dauern in [haltungen.md](haltungen.md).

| Typ | Nachladen | Ziehen | Zielen ein | Feuer | Status |
|---|---|---|---|---|---|
| Auto Rifle | leer 1,85 s (MagOut 0,25, MagIn 0,93) | 0,23 s | 0,07–0,08 s | 720/min | gemessen (clips 8, 133–135) |
| Pulse Rifle | leer 1,60–1,65 s | offen | 0,30 s | 3er-Salve, 0,067 s Abstand | gemessen (136–137) |
| Scout Rifle | 1,7–1,85 s | offen | ≈ 0,37 s | Einzelschuss | gemessen (138) |
| Hand Cannon | Hüfte 1,0 s | 0,08 s ins ADS | offen | 300–350/min | beobachtet (4, 53–54) |
| Sidearm | ≈ 1,1–1,75 s | offen | 0,20 s | 2er-Salve im Beispiel | gemessen (139) |
| SMG | ruhig 2,82–2,87 s (MagOut 0,32–0,35) | offen | 0,32 s | Kadenz widersprüchlich | gemessen (110–117) |
| Combat Bow | – | offen | 0,25 s | Auszug ≈ 0,60 s | gemessen (140) |
| Shotgun | 0,62–0,87 s je Patrone | 0,25 s | ≈ 0,08 s | offen | gemessen (10–11, 122–123) |
| Sniper | 2,05 s Hüfte / 2,80 s ruhig | 0,60 s | 0,15–0,17 s | Einzelschuss | gemessen (124–126) |
| Fusion | 1,73 s / ≈ 2,8 s | offen | 0,08–0,12 s | Laden bis Strahl 0,52–0,87 s | gemessen (118–121) |
| Linear Fusion | 0,85 s aus ADS / 3,3 s Hüfte | 0,28 s | 0,17–0,32 s | sichtbares Laden 0,33 s | gemessen (144, 43) |
| Trace | 2,55 s (Exotic) | offen | offen | Dauerstrahl | gemessen nur Nachladen (145) |
| Grenade Launcher | ≈ 2,52 s (1,87 s widersprüchlich) | offen | 0,32 s | Einzelschuss | gemessen, widersprüchlich (38, 141–142) |
| Rocket Launcher | ≈ 2,8 s (Exotic) | 0,18–0,28 s | 0,30–0,33 s | – | gemessen (14, 146) |
| Machine Gun | ≈ 4,87 s | offen | 0,37 s | 900/min | gemessen (143) |
| Sword | – | offen | – | Ansichtswechsel 0,15 + 0,33 s | gemessen nur Ansicht (148) |
| Glaive | 2,28 s (Exotic) | offen | offen | offen | gemessen nur Nachladen (149) |

## Q-D2 · Formreferenzen Destiny 2 (Legendary, Abruf 24.10.2026)

Quelle Destinypedia (`https://www.destinypedia.com/<Name>`); belegt sind Typ, Hersteller, Seltenheit, Munition. **Formprinzipien
sind abgeleitet, nicht beobachtet** – keine Modellansicht und kein Video ausgewertet (bungie.net und light.gg nicht abrufbar).

| Typ | Funktionsreferenz | Übernommenes Prinzip (abgeleitet) | Eigenständige BASIC-Umsetzung |
|---|---|---|---|
| Auto Rifle | Halfdan-D (Häkke) | Magazin vor dem Abzug, Handschutz länger als Gehäuse, Optik auf Schiene | zweigeteiltes Gehäuse, Graphit-Handschutz, kleines Reflexvisier |
| Pulse Rifle | Ogma PR6 (Omolon) | schlanker, Mündungsaufsatz, Optik mittig | Impulskammer zweigeteilt, Salvenanzeigen, Schaft S2 |
| Scout Rifle | Hung Jury SR4 (Omolon) | Lauf deutlich länger als Körper, schmales Gehäuse | schlanke Gewehrfamilie, Zielfernrohr, kurzes Magazin |
| Hand Cannon | Minuet-42 (SUROS) | großes Gehäuse, kurzer kräftiger Lauf, Kimme/Korn | Revolver mit Kran (Formgen KG12-Mechanik), Unterlauf |
| Sidearm | Ironwreath-D (Häkke) | klein, Magazin im Griff | Schlittenpistole, Graphitrahmen |
| SMG | Pizzicato-22 (SUROS) | kompakt, Griff und Magazin eng | Magazin im Griff, Vordergriff, kurzer S1 |
| Combat Bow | Mercury-A (Häkke) | zwei Wurfarme, mittiges Griffstück mit Pfeilführung | Recurve, Pfeilfenster rechts, Ringvisier |
| Shotgun | Quitclaim Shotgun III (Häkke) | dicker kurzer Lauf, Rohr unter dem Lauf | Pumpe auf Röhrenmagazin, Ladeklappe |
| Sniper | Elegy-49 (SUROS) | langer Lauf, Zielfernrohr, hohe Wangenauflage, Mündungsbremse | Kammerstängel rechts, großes Rohr |
| Fusion | Cruoris FR4 (Omolon) | frontlastig, Zelle und Leuchtfenster | drei Spulenringe, drei Ladeanzeigen, Schlitz-Emitter |
| Linear Fusion | Taipan-4fr (VEIST) | sehr lang, Schienenoptik, Ladeanzeige | offene Doppelschiene mit Leuchtkern |
| Trace | Ribbontail (Omolon) | Emitter vorn, Spulenblock dahinter | Fokusrohr mit Ringen und Kegel, Seitenzelle |
| Grenade Launcher | Festival Flight (SUROS) | dicke kurze Rohrbaugruppe; Kipplauf aus blueberries.gg „breech grenade launchers“ | Kipplauf am Scharnier, Vorderschaft am Lauf |
| Rocket Launcher | Morrigan-D (Häkke) | großes Schulterrohr, Griff und Visier unter/neben dem Rohr | Heckladung, Visiersockel |
| Machine Gun | Unwavering Duty (SUROS) | voluminöser Munitionsbehälter, langer Ablauf beim Nachladen | Zuführdeckel, Kasten links, Tragegriff |
| Sword | Goldtusk (VEIST) | Klinge 4–5 × so lang wie breit, Parierstange | Einschneider mit Parierblock |
| Glaive | Rake Angle (Häkke) | langer Schaft, Klinge mit Projektil-Mündung und Schild | Schildflügel aufklappbar, Seitenzelle oben |

Herstellerstile (Abgrenzung): Häkke sechseckig, Tan, orange Streifen · SUROS rund, Rot-Weiß · Omolon Schwarz/Aqua, Flüssigkeitsanzeigen ·
VEIST Klingenfortsätze, Seitenmagazine. BASIC übernimmt keinen davon: rechteckige Grundformen, Orange nur an Bedienelementen.

## Q-D2-IMG · Bildreferenzen (gesichtet 24.10.2026, Pilot v2)

Bungie-Inspektionsrenderings gewöhnlicher Legendary-Waffen, aufgerufen über die Bildersuche (Treffer von light.gg) und direkt von
`bungie.net/common/destiny2_content/screenshots/<id>.jpg`. Status **beobachtet** (angesehen, nicht vermessen). Keine Bilder ins Repo
übernommen; nur Prinzipien.

| Waffe | Typ | Quelle | Beobachtetes Prinzip |
|---|---|---|---|
| Shadow Price | Auto Rifle | `…/screenshots/3142989221.jpg` | geschichtete Oberschale über dem Verschluss, eingelassene Seitenplatten, mehrstufige Mündung mit Schlitzen, Klappvisiere, Lochmuster am Griff, Orange als grafisches Decal |
| Kibou AR3 | Auto Rifle | `…/screenshots/4014434381.jpg` | große ruhige Oberschale, skelettierter Unterbau mit Negativraum, sichtbare Leitungen, Lochgitter-Paneel, eingelassene Leuchtleiste, blanke Zierkanten |
| Inaugural Address | Pulse Rifle | `…/screenshots/3325744914.jpg` | rhythmische Flächengliederung (Kanneluren), Kontrastmetall an Mündung und Magazin |
| Positive Outlook | Auto Rifle | `…/screenshots/3625635456.jpg` | lange Haube über dem Lauf mit offenem Raum darunter, runder Leuchtkanister, Chevronband als Lackierung |
| BrayTech Werewolf | Auto Rifle | `…/screenshots/3558681245.jpg` | Lackierung als Grafik über mehrere Bauteile, Bügel über dem Gehäuse, freiliegender Lauf mit Ringen |
| Lethal Abundance | Auto Rifle | `…/screenshots/3428407746.jpg` | Zweiton-Lackierung, Zierlinien an Panelkanten, gerändelte Mündung |
| Ogma PR6 | Pulse Rifle | `…/screenshots/324584912.jpg` | geschlossener kastiger Vorderbau mit flacher, abgeschrägter Stirn; Mündung eingelassen; Bullpup (nicht übernommen, Vertrag 02 konventionell) |
| Yesteryear | Pulse Rifle | `…/screenshots/4028000428.jpg` | keilförmig nach vorn abfallende Haube; gelochter Mündungsmantel; Bullpup |
| Veles-X | Pulse Rifle | `…/screenshots/438540299.jpg` | Zweiton-Band über Gehäuse und Vorderbau, mehrstufige Mündung, Frontgriff (nicht übernommen: Leitmerkmal 06) |
| Red Tape | Scout Rifle | `…/screenshots/736362511.jpg` | sehr lang und schlank, Lauf mit Unterrohr, kompaktes Gehäuse, Schaft mit kantigem Durchbruch |
| Perses-D | Scout Rifle | `…/screenshots/1019000888.jpg` | schlanker geschlitzter Handschutz, kräftige mehrstufige Mündungsbremse, ein Farbband |
| Vouchsafe | Scout Rifle | `…/screenshots/3218302023.jpg` | organische Hive-Form – nicht übernommen (passt nicht zu BASIC) |
| Parabellum | Submachine Gun | `…/screenshots/3769072067.jpg` | kastiger Vorbau über dem Lauf, kräftiger gebogener Bügel vom Abzugsbügel nach vorn, langes Magazin im Griff tritt unten aus, kurzer Schaft |
| The Recluse | Submachine Gun | `…/screenshots/1050806815.jpg` | schlanke, nach vorn abfallende Linie; großer Bügel als Handstütze unter dem Lauf; Magazin im Griff |
| New City | Submachine Gun | `…/screenshots/2414612776.jpg` | gleiche Grundform wie Parabellum: Kastenvorbau, Bügel, Magazin im Griff mit geripptem Unterteil |
| Fatebringer | Hand Cannon | `…/screenshots/2171478765.jpg` | lange, gerade Oberkante über Lauf und Trommel; Kastenlauf mit Schlitzfenstern; Kastenunterlauf; dunkler, leicht geneigter Griff mit schmaler Kappe; hell oben, dunkel unten |
| Austringer | Hand Cannon | `…/screenshots/3055790362.jpg` | rechteckiger, schlichter Hauptblock; dunkler Rahmen hinten, heller Lauf vorn; offene runde Mündung, Hahn sichtbar; Zierfenster und Lampe nicht übernommen |
| Igneous Hammer | Hand Cannon | `…/screenshots/2351180975.jpg` | heller Deckel über dunklem Rahmen; Fächerrippen und Wickelgriff zu verziert (nicht übernommen) |
| Minimum Distance | Sidearm | `…/screenshots/1911843789.jpg` | klassischer Schlitten mit Auswurffenster und Farbzonen, dunkler Rahmen mit Schiene, Führungsstange vorn sichtbar, eckiger Abzugsbügel |
| Drang | Sidearm | `…/screenshots/2362471600.jpg` | flacher, kantiger Schlitten auf kurzem Kastenrahmen, Kimme am Schlittenende; langer Dämpfer und Medaillon nicht übernommen |
| Brass Attacks | Sidearm | `…/screenshots/2121785039.jpg` | Zweiton Schlitten/Rahmen; Nieten und Lüftungsfenster zu verziert (nicht übernommen) |
| Matador 64 | Shotgun | `…/screenshots/2563012876.jpg` | lange gerade Linie; dicker Lauf über dem Röhrenmagazin, langer glatter Vorderschaft; hohes kurzes Gehäuse hinten |
| Ragnhild-D | Shotgun | `…/screenshots/4225322581.jpg` | Lüftungsschiene über die ganze Länge, helles kastiges Gehäuse, gerippte Pumpe; der Mantel über dem Lauf bis vorn nicht übernommen (Nutzerwahl a: Lauf und Röhre sichtbar) |
| Quitclaim Shotgun III | Shotgun | `…/screenshots/2478247171.jpg` | Lauf und Röhre vorn frei übereinander, Schelle; Doppelrohr-Stirn und Rippen zu verziert (nicht übernommen) |
| Elegy-49 | Sniper Rifle | `…/screenshots/3666954563.jpg` | hohes helles Gehäuse, Laufmantel mit Längsschlitz, freier Lauf mit großer Mündung, großes Kastenmagazin; gelochter Mündungsmantel nicht übernommen |
| Maxim XI | Sniper Rifle | `…/screenshots/3239754990.jpg` | lange durchgehende Haube vom Schaft bis vor die Hälfte, darunter dunkler Vorderschaft, Kastenmagazin vor dem Griff |
| Far Future | Sniper Rifle | `…/screenshots/893527433.jpg` | Längsstaffelung: dünner, sehr langer freier Lauf (vermessen in Motiongen proportionen › 3); Zellen und Goldplatten nicht übernommen |
| Cruoris FR4 | Fusion Rifle | `…/screenshots/891996636.jpg` | kurzes hohes Gehäuse über dem Griff, davor ein offener Bund paralleler Kondensatorrohre bis zur stumpfen Front; Rohrbündel als Spulenringe um einen Kern vereinfacht |
| Erentil FR4 | Fusion Rifle | `…/screenshots/3027844941.jpg` | wie Cruoris (gleiche Hersteller-Grundform), Kammer offen zwischen Gehäuse und Front; Rohrschellen und Bügel nicht übernommen |
| Nox Echo III | Fusion Rifle | `…/screenshots/2502422774.jpg` | kastige helle Oberschale mit flacher Stirn über dunkler Unterseite, Zellenblock vor dem Griff (vermessen in Motiongen proportionen › 2) |
| Komodo-4FR | Linear Fusion Rifle | `…/screenshots/2697058914.jpg` | lange obere Laufhaube über schlanker unterer Schiene, vorn offen; Block hinter dem Griff; Lochreihe und Haken vorn nicht übernommen |
| Taipan-4fr | Linear Fusion Rifle | `…/screenshots/1911060537.jpg` | wie Komodo: oben schwer, unten schlank, dazwischen Luft; Zweiton dunkel/hell |
| Threaded Needle | Linear Fusion Rifle | `…/screenshots/3075224551.jpg` | lange offene Gabel nach vorn, Spulenhülse gerippt (vermessen in Motiongen proportionen › 2); spitze Zinken nicht übernommen (Stacheln, Budget) |
| Keraunios | Trace Rifle | `…/screenshots/2029899814.jpg` | lange helle Oberschale kragt vorn über den Emitter aus, darunter frei ein runder Strahlkanal; runde Scheibe am Übergang Gehäuse → Kanal; Zelle wie ein Magazin vor dem Griff; geschlossener Schaft mit Daumenloch (H/L grob 0,4–0,55, 3/4-Bild) |
| Retraced Path | Trace Rifle | `…/screenshots/548958835.jpg` | wie Keraunios (gleiche Grundform): Oberschale, untere Zinke, goldener Kanal frei dazwischen, Scheibe mittig; Höcker hinter dem Visier und untere Zinke nicht übernommen (Rohr unten frei, Schlichtheit) |
| Ribbontail | Trace Rifle | `…/screenshots/407150808.jpg` | gestufte Schale über rundem Kern, Scheibe mit Leuchtmitte, kurzer Hinterbau (H/L grob 0,4, 3/4-Bild); gestufte Dreieckspanzer nicht übernommen |
| Hammerhead | Machine Gun | `…/screenshots/1346714574.jpg` | breites Gehäuse, Trommel unter dem Gehäuse vor dem Griff, Gurt als Patronensäule an der linken Seite bis zur Zuführung, Deckel mit Visier, Skelettschaft |
| Avalanche | Machine Gun | `…/screenshots/1845978721.jpg` | kurzer Kastenkörper, Gurt sichtbar links, Behälter unten, gefensterter Mantel; Lochmuster nicht übernommen |
| Retrofit Escapade | Machine Gun | `…/screenshots/3103325054.jpg` | lange gerade Oberkante, offener Laufmantel, Gurtsäule links in den Einlauf; Leuchtpunktvisier nicht übernommen (H6 nach Baukasten) |
| Shattered Cipher | Machine Gun | `…/screenshots/2434225986.jpg` | Zweibein unter dem Lauf (vermessen in Motiongen proportionen › 2: H/L 0,30 mit Zweibein); Zweibein nicht übernommen (Spec verlangt keines) |
| Flash and Thunder | Grenade Launcher | `…/screenshots/1983332560.jpg` | Kipplauf: langer gerader Lauf über die halbe Länge, kurzes Gehäuse mit Klappvisier, senkrechter Stützgriff unter dem Lauf, Pistolengriff, kein Schaft (H/L grob 0,45–0,6 mit Visier, 3/4-Bild); Stoffwicklung nicht übernommen |
| Wilderflight | Grenade Launcher | `…/screenshots/1206729100.jpg` | dicker dunkler Lauf mit Creme-Rücken, Laufschellen, Stützgriff auf einer Schiene unter dem Lauf, Klappvisier, leuchtende Munitionsanzeige am Gehäuse, Skelettschaft |
| Festival Flight | Grenade Launcher | `…/screenshots/3622281554.jpg` | runder Körper mit großer Mündungsglocke und Bügelgriff – zu verspielt, nicht übernommen |
| Wendigo GL3 | Grenade Launcher | `…/screenshots/1854753404.jpg` | große Drehtrommel vor dem Griff unter einem kastigen Rahmen, kurzer Lauf darüber, offener Schaft (Grundform von BASIC-13 v2.1 nach der Nutzerwahl „Trommel“) |
| Bitter/Sweet | Grenade Launcher | `…/screenshots/2599338625.jpg` | Trommel unter dem Gehäuse vor dem Griff, Lauf obenauf, Klappschaft; Zacken auf dem Rücken nicht übernommen |
| Palmyra-B | Rocket Launcher | `…/screenshots/3489657138.jpg` | dickes Startrohr vorn mit Ringpaaren, schlankeres Heckrohr (andere Farbe), Griffmodul unter dem Übergang, Klappgriff vorn, Visiermodul seitlich links (H/L grob 0,38, 3/4-Bild) |
| Morrigan-D | Rocket Launcher | `…/screenshots/3748713779.jpg` | wie Palmyra (gleiche Grundform): Creme-Startrohr mit Fenster auf die Rakete, schlankes Heckrohr, senkrechter Vordergriff, Visierkasten seitlich (H/L grob 0,40); Skelettrahmen an der Seite nicht übernommen |
| Code Duello | Rocket Launcher | `…/screenshots/2496242052.jpg` | langes Rohr mit Seitenvisier und Griffmodul darunter; gerippte Hülle und Zierschienen nicht übernommen |

Gesichtet 24.10.2026 für BASIC-02 v2.1 (Bildersuche „destiny 2 legendary pulse rifle light.gg“): übernommen geschlossene
Kammer mit abgeschrägter Stirn und Mündungsmulde, Keil-Oberseite, gestufte Mündung. Für BASIC-03 v2.1 (Bildersuche „destiny 2
legendary scout rifle light.gg“): übernommen lange flache Linie, geschlitzter Handschutz, Unterrohr, dreifach geschlitzte Bremse. Für BASIC-06 v2.1 (Namen aus der
Vorsitzung, Bilder am 25.10.2026 selbst gesichtet): übernommen Kastenvorbau, Bügel aus dem Abzugsbügel, Magazin im Griff mit
Austritt unten; nicht übernommen der gebogene Bügel ohne Vordergriff (Designvertrag 06 verlangt den Vordergriff; gerades Band ist
schlichter) und das gerippte Magazin (Schlichtheitsbudget). Für BASIC-04 und BASIC-05 v2.1 (0.24 „Holster“, gesichtet 28.10.2026;
Typ und Bild-ID aus dem öffentlichen Bungie-Manifest `bungie.net/Platform/Destiny2/Manifest/` › `DestinyInventoryItemDefinition`
(`itemTypeDisplayName`, `screenshot`), weil light.gg den Abruf ablehnt; Bilder nur im Cache `refs/q-d2-img/`): übernommen bei der
Handfeuerwaffe die lange gerade Oberkante, der Kastenlauf mit Fenster und der Kastenunterlauf, hell oben/dunkel unten; bei der
Seitenwaffe der Schlitten mit Auswurffenster, die sichtbare Führungsstange und der kurze dunkle Rahmen. Nicht übernommen: Zierfenster,
Fächerrippen, Lampen, Dämpfer, Medaillons, Nieten und Rautengriffe (Schlichtheitsbudget); Midnight Coup (Keil wie ein Gewehr) und
Traveler's Judgment 5 (Schläuche, Kapsel) gesichtet und verworfen. Für BASIC-08 und BASIC-09 v2.1 (0.25 „Longshot“, gesichtet
28.10.2026, Bungie-Manifest wie 0.24; Bilder nur im Cache `refs/q-d2-img/sg_*`, `sr_*`): übernommen bei der Schrotflinte die gerade
Oberkante mit Lüftungsschiene, dicker Lauf über der Röhre und die große Pumpe; beim Scharfschützen die lange Creme-Haube (geteilt in
Gehäuse und Laufmantel) mit Längsschlitz, freier Lauf mit großer Bremse und Kastenmagazin vor dem Griff. Gesichtet und verworfen:
Badlander und Retold Tale (organisch, Verzierungen), Beloved (Leuchtzellen), Twilight Oath (geschwungene Klinge), Uzume RR4 (Kastenoptik).
Für BASIC-10 und BASIC-11 v2.1 (0.26 „Kindle“, gesichtet 28.10.2026, Bungie-Manifest wie 0.24; Bilder nur im Cache
`refs/q-d2-img/fr_*`, `lf_*`): übernommen beim Fusionsgewehr das kurze Gehäuse mit offener Ladekammer davor, die stumpfe Front und die
Zelle vor dem Griff; beim Linearen Fusionsgewehr die zwei Schienen mit Luft dazwischen, die offene Gabel vorn und der Block hinter dem
Griff. Gesichtet und verworfen: Main Ingredient und Elatha FR4/Proelium FR3 (Varianten derselben Grundformen), Stormchaser und Doomed
Petitioner (Klingenspitze, organische Linien), Cataclysmic (Raid-Waffe, Zahnreihe).
Für BASIC-12 und BASIC-15 v2.1 (0.27 „Tracer“, gesichtet 28.10.2026, Bungie-Manifest wie 0.24; Bilder nur im Cache
`refs/q-d2-img/tr_*`, `mg_*`): übernommen beim Spurgewehr die Oberschale, die über den freien runden Kanal auskragt, die runde Scheibe
am Kanalansatz, die Zelle vor dem Griff und der geschlossene Schaft mit Daumenloch; beim Maschinengewehr der Behälter vor dem Griff (bei BASIC seitlich links
statt unten, Nutzerwunsch) mit sichtbarer Gurtsäule links bis in den Einlauf, der Deckel mit Visier und der lange Mantel mit Fenstern. Gesichtet und
verworfen: Hollow Denial und Unsworn (Rippen-/Zahnreihen, organisch), Path of Least Resistance (Rohr mit Schild, nahe am Linearen
Fusionsgewehr), Bane of Sorrow, Corrective Measure und Fixed Odds (Verzierungen, Leuchtfenster als Schmuck). Die Spurgewehr-Werte H/L
sind eigene grobe Messungen an 3/4-Menübildern (Sightline 28.10.2026: „(a) passt … im Bericht als ‚beobachtet (BALLON 0.27)‘ mit
Unsicherheit führen, nicht in Motiongen schreiben“).
Für BASIC-13 und BASIC-14 v2.1 (0.28 „Breech“, gesichtet 28.10.2026, Bungie-Manifest wie 0.24, Bild über die Item-ID; Bilder nur im
Cache `refs/q-d2-img/gl_*`, `rl_*`): übernommen beim Granatwerfer zuerst (Kipplauf-Entwurf) der dicke gerade Lauf vor einem kurzen Gehäuse und der Griff der
Stützhand unter dem Lauf, nach der Nutzerwahl „Trommel statt Kipplauf“ die große Drehtrommel vor dem Griff unter dem Rahmen mit dem
kurzen Lauf darüber (Wendigo GL3, Bitter/Sweet); beim Raketenwerfer das dicke Startrohr mit schlankerem Heckrohr, Griffmodul unter dem
Übergang, senkrechter Vordergriff, das Fenster auf die Rakete und das Visier seitlich links. Gesichtet und verworfen: Lingering Dread,
Bump in the Night und Sleepless (organisch, Stacheln, Zahnreihen), Festival Flight (verspielt).
Die H/L-Werte sind wie 0.27 eigene grobe Messungen an 3/4-Menübildern (beobachtet, Unsicherheit mindestens ± 25 %).

Daraus die fünf Regeln des Piloten: drei Detailebenen, Negativraum, Schichtung, Materialbruch, lesbare Front
([versions/0.2-pilot.md](versions/0.2-pilot.md)).

## Q-D2-ARM · Armreferenzen des Nutzers (24.10.2026)

Sechs Bildschirmfotos von Destiny-2-Panzerhandschuhen, vom Nutzer ausdrücklich **nur als Inspiration** geschickt. Status
**beobachtet**; Kopien außerhalb des Repos unter `~/Library/Caches/CubeEscapeBallon/refs/arm-v2/` und `…/arm-v3/`.

| Satz | Beobachtetes Prinzip | Übernommen in |
|---|---|---|
| arm-v2 (4 Bilder: weiß-rote Titan-Stulpen, facettierte Panzer mit Leuchtkanten, ACD/0 Feedback Fence) | Panzer umschließt das Glied, Verjüngung, Facetten mit Grat, Stulpe überlappt die Hand | Hand und Finger (Rückenschale mit Grat); Facettenplatten am Unterarm wieder verworfen (wirkten klobig) |
| arm-v3 (2 Bilder: dunkler und silber-goldener Handschuh mit Scheibe am Oberarm) | glatte große Schale mit Fasen und Pfeilschnitt, zweite Lage mit Bolzen, Kontraststreifen, Medaillon mit Ring | Ober-/Unterarm und Ellbogen v3 |

## Q-D2-ZOOM · Zoom beim Zielen (gelesen 24.10.2026)

Destiny 2 Wiki „Zoom“ (`d2.destinygamewiki.com/wiki/Zoom`, Messungen von u/gintellectual via Reddit), Status **beobachtet**
(Community-Messung, ±0,05). Zoom = Grundzoom der Klasse + Visierbonus; Bildwinkel beim Zielen = Grundbildwinkel / Zoom.

| Klasse | Grundzoom | | Visier (Beispiele) | Bonus |
|---|---|---|---|---|
| Automatikgewehr | 1,6 | | Red Dot | +0,4 |
| Impulsgewehr | 1,7 | | Holo/Kreis (IS 5 Circle) | +0,15 |
| Scoutgewehr | 2,1 | | Okulare (SRO-41/-52) | +0,8/+0,9 |
| Handfeuerwaffe | 1,5 | | Reflex (Model 8 Red) | +0,6 |
| Granatwerfer | 1,4 | | | |
| MP, Seitenwaffe, Schrotflinte | 1,25 | | Visiere bringen bei diesen Klassen keinen Bonus | |
| Scharfschütze | 5,1–8,0 (gesamt) | | | |

Beispiele: Automatikgewehr mit Red Dot ≈ ×2,0; Scout mit Okular ≈ ×2,9–3,0. Verwendet für die Visierbild-Beispiele
(`tools/sight_examples.py`) und als Grundlage für `reticles.SIGHT['…']['ads_zoom']`.

## Q-D2-ADS · Visierbild beim Zielen (24.10.2026)

Status **beobachtet**. Grundlage für den Visier-Standard v2 (`basic/reticles.py › SIGHT`) nach dem Nutzerhinweis „Visiere sehr
klobig“.

| Quelle | Beobachtung |
|---|---|
| YouTube `1ERmScNiOk4` („The most unique + rare Scout Rifle in Destiny 2“, Patron of Lost Causes), lokal geladen nach `~/Library/Caches/CubeEscapeBallon/refs/video/`, Zielbilder bei 3:30, 3:50, 5:50, 7:10, 7:30, 8:10, 8:40 | Scout im Zielen: man sieht den **Objektivring** (dünner Rand, farbige Innenkante), ≈ 25 % Bildbreite, ≈ 50 % Bildhöhe; in der Linse die **vergrößerte Welt** mit feinem Absehen (Bögen, Punkt); kein Okular, keine Augenmuschel, kein Rohrtunnel; darunter nur ein schmaler Fuß; die Welt um den Ring bleibt sichtbar |
| Motiongen `docs/destiny2.md` (gemessene Clips) | Seitenwaffe Holo-Ring ≈ 10 % Bildhöhe, Körper ≈ 12 % Breite; Handfeuerwaffe ≈ 18–25 % Breite, Korn auf dem Kreuz; Impulsgewehr eckige Kimme ≈ 20 % Höhe, Körper ≈ 20 % Breite; Lineare Fusion „Bild in der Linse“; Scharfschütze Vollbild-Overlay |

Folgerung: dünne Ränder um große Öffnungen; das Waffenmodell wird beim Zielen nicht vergrößert, nur die Welt; Zielfernrohr
zeigt ein Linsenbild, die Teile hinter dem Auge sind beim Zielen ausgeblendet.

## Q-REF-EYEBOX · Visiere in Videospielen (Motiongen REF 0.14)

`cubeescape-reference` Branch `claude/ref-0.14-eyebox`, [PR ffunkfabian-hash/cubeescape-motiongen#42](https://github.com/ffunkfabian-hash/cubeescape-motiongen/pull/42),
`docs/visiere.md` (31 Spiele, Destiny 2 mit 8 Herstellern/31 Waffen, gemessene Bildanteile, fünf Darstellungsarten) und
`data/visiere.json`; Abschnitt 11 „Empfehlungen für BASIC“ ist die Grundlage des Visier-Standards 3 (anfangs „Visier-Designsprache v3“). Status der Werte dort.

## Q-BG · Bungie-Startpunkte des Auftrags

Bungie-Seiten aus dem Auftrag (Neuspieler-Guide, „Your Guardian“, Dev Insights, TWID 06.11./26.11.2025) waren über den
Rechercheweg nicht abrufbar (Seite lieferte nur den Titel) – **offen**. Die Typenliste stützt sich auf Formgen `waffentypen.md`
(destinytracker, Abruf 18.10.2026).
