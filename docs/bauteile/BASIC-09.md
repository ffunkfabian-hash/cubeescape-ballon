<!-- erzeugt von tools/make_docs.py – nicht von Hand ändern -->

# BASIC-09 Scharfschützengewehr – „Weitschuss“

Repetier-Scharfschützengewehr mit großem Zielfernrohr.

Typ `sniper_rifle` (Sniper Rifle) · Munition special · Feuerart `bolt_action` · Quelle des Entwurfs: `basic/weapons/` · Spec: [`data/specs/BASIC-09.spec.json`](../../data/specs/BASIC-09.spec.json).

**Maße (gemessen, Ruhelage, Visier montiert):** Länge 1143 mm · Höhe 270 mm · Breite 92 mm · 34 Bauteile · 6772 Dreiecke (mit Fasen).

Rahmen: Meter, vorn −Y, oben +Z, links +X, Ursprung `Socket_Hand`. `origin_m` ist der Objektursprung (bei beweglichen Teilen der Drehpunkt).

## Baugruppenbaum

```
BASIC-09
├─ ASM_receiver  Hauptgehäuse / Receiver
│   ├─ upper  Oberes Gehäuse
│   ├─ lower  Unteres Gehäuse
│   ├─ bolt_slot  Verschlussfenster
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
│   ├─ stock_joint  Schaftverbindung
│   ├─ stock_spine  Schaftrohr
│   ├─ stock  Schulterstütze
│   ├─ butt_pad  Schaftkappe
│   ├─ cheek_rest  Wangenauflage
├─ ASM_mechanism  Bewegliche Mechanik / Moving mechanism
│   ├─ bolt  Verschluss
│   │  └(an bolt) bolt_handle  Kammerstängel
│   │  └(an bolt_handle) bolt_knob  Kammerknopf
```

## Bauteilliste

| ID | Name (de / en) | Funktion | Befestigung | übergeordnet | Material | Maße X×Y×Z mm | Ursprung m | Bewegung | Entnahme | Schnittstelle | Aktionen |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `upper` | Oberes Gehäuse / Upper receiver | Verschlussgehäuse und Schiene | mit Unterem Gehäuse verbolzt | ASM_receiver | shell | 40×316×54 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `lower` | Unteres Gehäuse / Lower receiver | Griffmodul und Magazinschacht | unter dem Oberen Gehäuse, Fuge 1 mm | ASM_receiver | shell | 38×306×33 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `handguard` | Handschutz / Handguard | Langer Handschutz, frei schwingender Lauf | am Oberen Gehäuse, Fuge 1 mm | ASM_support | graphite | 42×339×58 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `bolt` | Verschluss / Bolt | Verriegelt die Patrone; gleitet zurück | im Oberen Gehäuse (gleitet) | ASM_mechanism | metal | 14×100×14 | -0.012, 0.010, 0.102 | verschiebt 80 mm (f,u,x (-80, 0, 0)); Ereignis bolt | nein | – | fire_cycle, reload_empty |
| `bolt_handle` | Kammerstängel / Bolt handle | Hebel zum Öffnen des Verschlusses | am Verschluss (dreht 60° hoch) | bolt | dark_metal | 34×8.7×8.7 | -0.012, 0.030, 0.102 | dreht um Achse f durch (-30, 102, -12) mm, 0…-60°; Ereignis bolt | nein | – | fire_cycle, reload_empty |
| `bolt_knob` | Kammerknopf / Bolt knob | Griffkugel des Kammerstängels | am Kammerstängel | bolt_handle | graphite | 14×16×16 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `bolt_slot` | Verschlussfenster / Bolt slot | Öffnung für Kammerstängel und Auswurf rechts | im Oberen Gehäuse | ASM_receiver | dark_metal | 1.4×160×26 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_l1` | Lüftungsöffnung links 1 / Vent left 1 | Kühlluft; tiefliegendes Gitter | eingelassen | ASM_support | dark_metal | 1.4×70×10 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_r1` | Lüftungsöffnung rechts 1 / Vent right 1 | Kühlluft; tiefliegendes Gitter | eingelassen | ASM_support | dark_metal | 1.4×70×10 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_l2` | Lüftungsöffnung links 2 / Vent left 2 | Kühlluft; tiefliegendes Gitter | eingelassen | ASM_support | dark_metal | 1.4×70×10 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_r2` | Lüftungsöffnung rechts 2 / Vent right 2 | Kühlluft; tiefliegendes Gitter | eingelassen | ASM_support | dark_metal | 1.4×70×10 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `barrel` | Lauf / Barrel | Führt das Geschoss | im Gehäuse/Handschutz verschraubt | ASM_barrel | metal | 22×224×22 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `muzzle` | Mündungsbremse / Muzzle brake | Mündungsteil; Socket_Muzzle an der Stirnfläche | auf Laufende geschraubt (lösbar) | ASM_barrel | dark_metal | 31×58×31 | 0.000, 0.000, 0.000 | fest | nein | BMZ-15 | – |
| `rail` | Schiene / Top rail | Aufnahme für Visiere (BRI-22) | auf Oberem Gehäuse (fest) | ASM_receiver | dark_metal | 22×286×8.5 | 0.000, 0.000, 0.000 | fest | nein | BRI-22 | – |
| `scope_mount_r` | Zielfernrohr-Ring hinten / Scope ring rear | Klemmt das Rohr auf die Schiene BRI-22 | Klemmung auf Schiene (lösbar) | ASM_sight | dark_metal | 24×22×28 | 0.000, 0.029, 0.134 | verschiebt 80 mm (f,u,x (0, 80, 0)); Ereignis swap_sight | ja – beide Ringe lösen, Zielfernrohr senkrecht abnehmen | BRI-22 | – |
| `scope_mount_f` | Zielfernrohr-Ring vorn / Scope ring front | Klemmt das Rohr auf die Schiene BRI-22 | Klemmung auf Schiene (lösbar) | scope_mount_r | dark_metal | 24×22×28 | 0.000, 0.000, 0.000 | fest | nein | BRI-22 | – |
| `scope_tube` | Mittelrohr / Scope tube | Verbindet Okular und Objektiv | in den Ringen (fest) | scope_mount_r | graphite | 26×166×26 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `scope_eyepiece` | Okular / Eyepiece | Augenseite; Socket_Eye dahinter | am Mittelrohr (fest) | scope_mount_r | graphite | 34×32×34 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `scope_objective` | Objektiv / Objective bell | Lichteintritt vorn | am Mittelrohr (fest) | scope_mount_r | graphite | 64×42×64 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `scope_turret` | Verstellturm / Elevation turret | Höhenverstellung (Akzent, Bedienelement) | oben am Mittelrohr (fest) | scope_mount_r | accent | 16×16×11 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `scope_glass` | Objektivglas / Objective lens | Linse; Absehen-Ebene | im Objektiv (fest) | scope_mount_r | glass | 40×1.0×40 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `scope_ocular_glass` | Okularglas / Ocular lens | Augenlinse | im Okular (fest) | scope_mount_r | glass | 28×1.0×28 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `grip` | Pistolengriff / Pistol grip | Haupthand hält die Waffe; trägt Socket_Hand | mit Unterem Gehäuse verschraubt (fest) | ASM_grip_controls | graphite | 30×68×104 | 0.000, 0.000, 0.000 | fest | nein | BGM-1 | – |
| `trigger` | Abzug / Trigger | Feuer auslösen (Zeigefinger) | Drehpunkt im Unteren Gehäuse | ASM_grip_controls | metal | 7.0×7.8×26 | 0.000, -0.045, 0.037 | dreht um Achse x durch (44.71796769724491, 37, 0) mm, 0…-12°; Ereignis fire | nein | – | fire_cycle |
| `trigger_guard` | Abzugsbügel / Trigger guard | Schützt den Abzug, Fingerfreiraum ≥ 22 mm | Griff vorn und Unteres Gehäuse (fest) | ASM_grip_controls | graphite | 12×58×35 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `selector` | Feuerwahlhebel / Fire selector | Sichern / Feuer, mit dem Daumen der Haupthand | Achse quer im Unteren Gehäuse | ASM_grip_controls | accent | 3.0×20×8.0 | 0.000, -0.004, 0.062 | dreht um Achse x durch (4, 62, 0) mm, 0…90°; Ereignis safety | nein | – | – |
| `magazine` | Magazin / Magazine | Hält die Patronen; entnehmbar | rastet im Magazinschacht ein (lösbar, Magazinhalter) | ASM_ammo | shell | 26×40×72 | 0.000, -0.112, 0.060 | verschiebt 160 mm (f,u,x (0.0, -160.0, 0)); Ereignis reload | ja – Entnahme entlang der Magazinachse nach unten; Schacht nach unten offen | BMW-R | reload_empty |
| `magazine_base` | Magazinboden / Magazine base plate | Greifkante zum Herausziehen | am Magazin (fest) | magazine | graphite | 29×44×9.5 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `magazine_round` | Oberste Patrone / Top round | Zeigt den Ladezustand im Schacht | im Magazin | magazine | metal | 8.8×30×8.8 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `stock_joint` | Schaftverbindung / Stock joint | Verbindet Schaft und Gehäuse; Verriegelung | Steckverbindung am Gehäuseende (fest) | ASM_stock | dark_metal | 30×12×42 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `stock_spine` | Schaftrohr / Stock spine | Trägt die Schulterstütze in Linie mit dem Lauf | in der Schaftverbindung (fest) | ASM_stock | graphite | 28×99×28 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `stock` | Schulterstütze / Buttstock | Anlage an der Schulter, Wangenauflage oben | auf dem Schaftrohr (fest) | ASM_stock | shell | 36×92×106 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `butt_pad` | Schaftkappe / Butt pad | Rutschfeste Anlage an der Schulter | auf das Schaftende gesteckt (fest) | ASM_stock | graphite | 40×19×115 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `cheek_rest` | Wangenauflage / Cheek rest | Anlage für die Wange beim Zielen | auf der Schulterstütze (fest) | ASM_stock | graphite | 26×78×10 | 0.000, 0.000, 0.000 | fest | nein | – | – |

## Anker

| Anker | Position m (X, Y, Z) | Teil | Hinweis |
|---|---|---|---|
| `Socket_Hand` | 0.0000, 0.0000, 0.0000 | grip | – |
| `Socket_SupportHand` | 0.0000, -0.3400, 0.0920 | handguard | – |
| `Socket_Muzzle` | 0.0000, -0.8120, 0.0980 | muzzle | – |
| `Socket_MagWell` | 0.0000, -0.1120, 0.0600 | lower | – |
| `Socket_Bolt` | -0.0540, 0.0300, 0.1020 | bolt_knob | Griffpunkt Kammerknopf (Haupthand) |
| `Socket_Sight` | 0.0000, 0.0800, 0.1740 | scope_eyepiece | hinteres Okularende auf der Visierlinie |
| `Socket_Reticle` | 0.0000, -0.1505, 0.1740 | scope_glass | Mitte Objektivglas |
| `Socket_Eye` | 0.0000, 0.1500, 0.1740 | scope_eyepiece | Vorschlag: Augenabstand 70 mm |
| `Socket_CenterOfMass` | -0.0002, -0.1307, 0.0884 | – | abgeleitet: Volumenschwerpunkt, homogene Dichte, ohne Glas |

## Schnittstellen

| ID | Bedeutung | Regel |
|---|---|---|
| BGM-1 | Griffmodul Typ 1 (Gewehrfamilie) | Oberkante 42 × 30 mm, Neigung 15° (oben nach vorn), Abzugsbügel bis f = +78 mm |
| BMW-R | Magazinschacht Gewehr | Innenmaß 40 × 24 mm, Neigung je Waffe im Spec |
| BMZ-15 | Mündungsgewinde r 15 | Laufende r 9 mm, Mündungsteil r 15 mm, Bohrung r 5 mm |
| BRI-22 | Schiene 22 mm (Oberseite Gehäuse) | Breite 22 mm, Höhe 8 mm, Klemmfuß 22 mm breit, Mindestlänge Klemmfuß 40 mm |

## Aktionen der Mechanik

| Aktion | Beschreibung | Bilder (30 fps) | Teile | Ereignisse (Bild) | Status |
|---|---|---|---|---|---|
| `fire_cycle` | Schuss und Repetieren | 40 (1.33 s) | trigger, bolt_handle, bolt | shot (2), unlock (15), eject (20), chamber (27), ready (32) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |
| `reload_empty` | Nachladen aus leerem Zustand | 90 (3.00 s) | magazine, bolt_handle, bolt | mag_out (16), mag_seated (50), chamber (73), ready (80) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |

Haltungen, Übergänge und Status aller Aktionen: [haltungen.md › BASIC-09](../haltungen.md#basic-09).
