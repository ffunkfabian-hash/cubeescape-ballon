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

Gesichtet 24.10.2026 für BASIC-02 v2.1 (Bildersuche „destiny 2 legendary pulse rifle light.gg“): übernommen geschlossene
Kammer mit abgeschrägter Stirn und Mündungsmulde, Keil-Oberseite, gestufte Mündung.

Daraus die fünf Regeln des Piloten: drei Detailebenen, Negativraum, Schichtung, Materialbruch, lesbare Front
([versions/0.2-pilot.md](versions/0.2-pilot.md)).

## Q-D2-ARM · Armreferenzen des Nutzers (24.10.2026)

Sechs Bildschirmfotos von Destiny-2-Panzerhandschuhen, vom Nutzer ausdrücklich **nur als Inspiration** geschickt. Status
**beobachtet**; Kopien außerhalb des Repos unter `~/Library/Caches/CubeEscapeBallon/refs/arm-v2/` und `…/arm-v3/`.

| Satz | Beobachtetes Prinzip | Übernommen in |
|---|---|---|
| arm-v2 (4 Bilder: weiß-rote Titan-Stulpen, facettierte Panzer mit Leuchtkanten, ACD/0 Feedback Fence) | Panzer umschließt das Glied, Verjüngung, Facetten mit Grat, Stulpe überlappt die Hand | Hand und Finger (Rückenschale mit Grat); Facettenplatten am Unterarm wieder verworfen (wirkten klobig) |
| arm-v3 (2 Bilder: dunkler und silber-goldener Handschuh mit Scheibe am Oberarm) | glatte große Schale mit Fasen und Pfeilschnitt, zweite Lage mit Bolzen, Kontraststreifen, Medaillon mit Ring | Ober-/Unterarm und Ellbogen v3 |

## Q-BG · Bungie-Startpunkte des Auftrags

Bungie-Seiten aus dem Auftrag (Neuspieler-Guide, „Your Guardian“, Dev Insights, TWID 06.11./26.11.2025) waren über den
Rechercheweg nicht abrufbar (Seite lieferte nur den Titel) – **offen**. Die Typenliste stützt sich auf Formgen `waffentypen.md`
(destinytracker, Abruf 18.10.2026).
