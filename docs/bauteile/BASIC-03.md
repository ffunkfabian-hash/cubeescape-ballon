<!-- erzeugt von tools/make_docs.py – nicht von Hand ändern -->

# BASIC-03 Scout-Gewehr – „Fernblick“

Schlankes halbautomatisches Präzisionsgewehr mit Zielfernrohr.

Typ `scout_rifle` (Scout Rifle) · Munition primary · Feuerart `semi_auto` · Quelle des Entwurfs: `basic/weapons/` · Spec: [`data/specs/BASIC-03.spec.json`](../../data/specs/BASIC-03.spec.json).

**Maße (gemessen, Ruhelage, Visier montiert):** Länge 988 mm · Höhe 254 mm · Breite 46 mm · 28 Bauteile · 5936 Dreiecke (mit Fasen).

Rahmen: Meter, vorn −Y, oben +Z, links +X, Ursprung `Socket_Hand`. `origin_m` ist der Objektursprung (bei beweglichen Teilen der Drehpunkt).

## Baugruppenbaum

```
BASIC-03
├─ ASM_receiver  Hauptgehäuse / Receiver
│   ├─ receiver  Gehäuse
│   ├─ rail  Schiene
├─ ASM_barrel  Lauf / Emitter / Barrel / emitter
│   ├─ barrel  Lauf
│   ├─ muzzle  Mündungsbremse
├─ ASM_ammo  Munitionsversorgung / Ammunition feed
│   ├─ magazine  Magazin
│   │  └(an magazine) magazine_base  Magazinboden
│   │  └(an magazine) magazine_round  Oberste Patrone
├─ ASM_sight  Visier / Sight
│   ├─ scope_mount_r  Zielfernrohr-Ring hinten
│   │  └(an scope_mount_r) scope_mount_f  Zielfernrohr-Ring vorn
│   │  └(an scope_mount_r) scope_tube  Mittelrohr
│   │  └(an scope_mount_r) scope_eyepiece  Okular
│   │  └(an scope_mount_r) scope_objective  Objektiv
│   │  └(an scope_mount_r) scope_turret  Verstellturm
│   │  └(an scope_mount_r) scope_glass  Objektivglas
│   │  └(an scope_mount_r) scope_ocular_glass  Okularglas
├─ ASM_grip_controls  Griff und Bedienung / Grip and controls
│   ├─ grip  Pistolengriff
│   ├─ trigger  Abzug
│   ├─ trigger_guard  Abzugsbügel
│   ├─ selector  Feuerwahlhebel
├─ ASM_support  Stützbereich / Support
│   ├─ handguard  Handschutz
│   ├─ vent_l1  Lüftungsöffnung links 1
│   ├─ vent_r1  Lüftungsöffnung rechts 1
│   ├─ vent_l2  Lüftungsöffnung links 2
│   ├─ vent_r2  Lüftungsöffnung rechts 2
├─ ASM_stock  Schaft / Stock
│   ├─ stock  Schulterstütze S2
│   ├─ butt_pad  Schaftkappe
├─ ASM_mechanism  Bewegliche Mechanik / Moving mechanism
│   ├─ port_cover  Auswurfklappe
│   ├─ charging_handle  Ladehebel
```

## Bauteilliste

| ID | Name (de / en) | Funktion | Befestigung | übergeordnet | Material | Maße X×Y×Z mm | Ursprung m | Bewegung | Entnahme | Schnittstelle | Aktionen |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `receiver` | Gehäuse / Receiver | Schlankes Einteilgehäuse: Lauf, Schiene, Griffmodul, Schacht | Grundkörper | ASM_receiver | shell | 38×320×89 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `handguard` | Handschutz / Handguard | Griffbereich der Stützhand; lang und schmal | am Oberen Gehäuse verschraubt, Fuge 1 mm | ASM_support | graphite | 40×285×54 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `port_cover` | Auswurfklappe / Ejection port cover | Auswurffenster rechts | Scharnier unten | ASM_mechanism | dark_metal | 1.6×54×22 | -0.021, -0.047, 0.088 | dreht um Achse f durch (47, 88, -21) mm, 0…75°; Ereignis fire | nein | – | fire_semi |
| `vent_l1` | Lüftungsöffnung links 1 / Vent left 1 | Kühlluft; tiefliegendes Gitter | eingelassen | ASM_support | dark_metal | 1.4×60×10 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_r1` | Lüftungsöffnung rechts 1 / Vent right 1 | Kühlluft; tiefliegendes Gitter | eingelassen | ASM_support | dark_metal | 1.4×60×10 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_l2` | Lüftungsöffnung links 2 / Vent left 2 | Kühlluft; tiefliegendes Gitter | eingelassen | ASM_support | dark_metal | 1.4×60×10 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_r2` | Lüftungsöffnung rechts 2 / Vent right 2 | Kühlluft; tiefliegendes Gitter | eingelassen | ASM_support | dark_metal | 1.4×60×10 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `barrel` | Lauf / Barrel | Führt das Geschoss | im Gehäuse/Handschutz verschraubt | ASM_barrel | metal | 16×176×16 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `muzzle` | Mündungsbremse / Muzzle brake | Mündungsteil; Socket_Muzzle an der Stirnfläche | auf Laufende geschraubt (lösbar) | ASM_barrel | dark_metal | 22×34×22 | 0.000, 0.000, 0.000 | fest | nein | BMZ-15 | – |
| `rail` | Schiene / Top rail | Aufnahme für Visiere (BRI-22) | auf Oberem Gehäuse (fest) | ASM_receiver | dark_metal | 22×290×8.5 | 0.000, 0.000, 0.000 | fest | nein | BRI-22 | – |
| `scope_mount_r` | Zielfernrohr-Ring hinten / Scope ring rear | Klemmt das Rohr auf die Schiene BRI-22 | Klemmung auf Schiene (lösbar) | ASM_sight | dark_metal | 24×22×24 | 0.000, -0.001, 0.135 | verschiebt 80 mm (f,u,x (0, 80, 0)); Ereignis swap_sight | ja – beide Ringe lösen, Zielfernrohr senkrecht abnehmen | BRI-22 | – |
| `scope_mount_f` | Zielfernrohr-Ring vorn / Scope ring front | Klemmt das Rohr auf die Schiene BRI-22 | Klemmung auf Schiene (lösbar) | scope_mount_r | dark_metal | 24×22×24 | 0.000, 0.000, 0.000 | fest | nein | BRI-22 | – |
| `scope_tube` | Mittelrohr / Scope tube | Verbindet Okular und Objektiv | in den Ringen (fest) | scope_mount_r | graphite | 20×90×20 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `scope_eyepiece` | Okular / Eyepiece | Augenseite; Socket_Eye dahinter | am Mittelrohr (fest) | scope_mount_r | graphite | 28×32×28 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `scope_objective` | Objektiv / Objective bell | Lichteintritt vorn | am Mittelrohr (fest) | scope_mount_r | graphite | 42×42×42 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `scope_turret` | Verstellturm / Elevation turret | Höhenverstellung (Akzent, Bedienelement) | oben am Mittelrohr (fest) | scope_mount_r | accent | 16×16×11 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `scope_glass` | Objektivglas / Objective lens | Linse; Absehen-Ebene | im Objektiv (fest) | scope_mount_r | glass | 28×1.0×28 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `scope_ocular_glass` | Okularglas / Ocular lens | Augenlinse | im Okular (fest) | scope_mount_r | glass | 22×1.0×22 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `grip` | Pistolengriff / Pistol grip | Haupthand hält die Waffe; trägt Socket_Hand | mit Unterem Gehäuse verschraubt (fest) | ASM_grip_controls | graphite | 30×67×102 | 0.000, 0.000, 0.000 | fest | nein | BGM-1 | – |
| `trigger` | Abzug / Trigger | Feuer auslösen (Zeigefinger) | Drehpunkt im Unteren Gehäuse | ASM_grip_controls | metal | 7.0×7.8×26 | 0.000, -0.044, 0.035 | dreht um Achse x durch (44.182069312382666, 35, 0) mm, 0…-12°; Ereignis fire | nein | – | fire_semi |
| `trigger_guard` | Abzugsbügel / Trigger guard | Schützt den Abzug, Fingerfreiraum ≥ 22 mm | Griff vorn und Unteres Gehäuse (fest) | ASM_grip_controls | graphite | 12×58×35 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `selector` | Feuerwahlhebel / Fire selector | Sichern / Feuer, mit dem Daumen der Haupthand | Achse quer im Unteren Gehäuse | ASM_grip_controls | accent | 3.0×20×8.0 | 0.000, -0.004, 0.062 | dreht um Achse x durch (4, 62, 0) mm, 0…90°; Ereignis safety | nein | – | – |
| `magazine` | Magazin / Magazine | Hält die Patronen; entnehmbar | rastet im Magazinschacht ein (lösbar, Magazinhalter) | ASM_ammo | shell | 22×42×74 | 0.000, -0.110, 0.062 | verschiebt 160 mm (f,u,x (11.2, -159.6, 0)); Ereignis reload | ja – Entnahme entlang der Magazinachse nach unten; Schacht nach unten offen | BMW-R | reload_empty |
| `magazine_base` | Magazinboden / Magazine base plate | Greifkante zum Herausziehen | am Magazin (fest) | magazine | graphite | 25×40×12 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `magazine_round` | Oberste Patrone / Top round | Zeigt den Ladezustand im Schacht | im Magazin | magazine | metal | 8.8×26×8.8 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `stock` | Schulterstütze S2 / Stock S2 | Einteilige Schulterstütze; Wange liegt oben auf | mit zwei Bolzen am Gehäuse (fest) | ASM_stock | graphite | 34×168×101 | 0.000, 0.000, 0.000 | fest | nein | BST-2 | – |
| `butt_pad` | Schaftkappe / Butt pad | Anlage an der Schulter | auf das Schaftende geschraubt | ASM_stock | dark_metal | 38×14×100 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `charging_handle` | Ladehebel / Charging handle | Verschluss spannen (Stützhand zieht nach hinten) | in Längsnut links (gleitet) | ASM_mechanism | accent | 9.0×30×12 | 0.021, 0.090, 0.112 | verschiebt 55 mm (f,u,x (-55, 0, 0)); Ereignis charge | nein | – | reload_empty |

## Anker

| Anker | Position m (X, Y, Z) | Teil | Hinweis |
|---|---|---|---|
| `Socket_Hand` | 0.0000, 0.0000, 0.0000 | grip | – |
| `Socket_SupportHand` | 0.0000, -0.3300, 0.0920 | handguard | – |
| `Socket_Muzzle` | 0.0000, -0.6900, 0.0960 | muzzle | – |
| `Socket_MagWell` | 0.0000, -0.1100, 0.0620 | receiver | – |
| `Socket_Sight` | 0.0000, 0.0500, 0.1690 | scope_eyepiece | hinteres Okularende auf der Visierlinie |
| `Socket_Reticle` | 0.0000, -0.1045, 0.1690 | scope_glass | Mitte Objektivglas |
| `Socket_Eye` | 0.0000, 0.1200, 0.1690 | scope_eyepiece | Vorschlag: Augenabstand 70 mm |
| `Socket_CenterOfMass` | 0.0000, -0.0868, 0.0844 | – | abgeleitet: Volumenschwerpunkt, homogene Dichte, ohne Glas |

## Schnittstellen

| ID | Bedeutung | Regel |
|---|---|---|
| BGM-1 | Griffmodul Typ 1 (Gewehrfamilie) | Oberkante 42 × 30 mm, Neigung 15° (oben nach vorn), Abzugsbügel bis f = +78 mm |
| BMW-R | Magazinschacht Gewehr | Innenmaß 40 × 24 mm, Neigung je Waffe im Spec |
| BMZ-15 | Mündungsgewinde r 15 | Laufende r 9 mm, Mündungsteil r 15 mm, Bohrung r 5 mm |
| BRI-22 | Schiene 22 mm (Oberseite Gehäuse) | Breite 22 mm, Höhe 8 mm, Klemmfuß 22 mm breit, Mindestlänge Klemmfuß 40 mm |
| BST-2 | Schaft S2 | Anlage 64 mm hoch am Gehäuseende, Laufachse 24 mm unter der Oberkante |

## Aktionen der Mechanik

| Aktion | Beschreibung | Bilder (30 fps) | Teile | Ereignisse (Bild) | Status |
|---|---|---|---|---|---|
| `fire_semi` | Einzelschuss (Mechanik) | 12 (0.40 s) | trigger, port_cover | shot (2) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |
| `reload_empty` | Nachladen aus leerem Zustand | 80 (2.67 s) | magazine, charging_handle | mag_out (14), mag_seated (46), charge (64), ready (72) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |

Haltungen, Übergänge und Status aller Aktionen: [haltungen.md › BASIC-03](../haltungen.md#basic-03).
