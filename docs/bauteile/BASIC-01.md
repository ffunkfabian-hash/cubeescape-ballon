<!-- erzeugt von tools/make_docs.py – nicht von Hand ändern -->

# BASIC-01 Automatikgewehr – „Formstudie 01“

Schlichtes Automatikgewehr: Dauerfeuer, Kastenmagazin, kleines Reflexvisier.

Typ `auto_rifle` (Auto Rifle) · Munition primary · Feuerart `full_auto` · Quelle des Entwurfs: `basic/weapons/` · Spec: [`data/specs/BASIC-01.spec.json`](../../data/specs/BASIC-01.spec.json).

**Maße (gemessen, Ruhelage, Visier montiert):** Länge 905 mm · Höhe 268 mm · Breite 51 mm · 39 Bauteile · 5852 Dreiecke (mit Fasen).

Rahmen: Meter, vorn −Y, oben +Z, links +X, Ursprung `Socket_Hand`. `origin_m` ist der Objektursprung (bei beweglichen Teilen der Drehpunkt).

## Baugruppenbaum

```
BASIC-01
├─ ASM_receiver  Hauptgehäuse / Receiver
│   ├─ upper  Oberes Gehäuse
│   ├─ lower  Unteres Gehäuse
│   ├─ mag_well  Magazinschacht
│   ├─ ammo_counter  Munitionsanzeige
│   ├─ rail  Schiene
├─ ASM_barrel  Lauf / Barrel
│   ├─ barrel  Lauf
│   ├─ muzzle  Mündungsbremse
├─ ASM_ammo  Munitionsversorgung / Ammunition feed
│   ├─ magazine  Magazin
│   │  └(an magazine) magazine_base  Magazinboden
│   │  └(an magazine) magazine_round  Oberste Patrone
├─ ASM_sight  Visier / Sight
│   ├─ sight_mount  Visier-Klemmfuß
│   │  └(an sight_mount) sight_clamp  Klemmschraube
│   │  └(an sight_mount) sight_body  Visiergehäuse
│   │  └(an sight_mount) sight_frame  Haubenrahmen
│   │  └(an sight_mount) sight_glass  Visierglas
│   │  └(an sight_mount) sight_emitter  Emitter
├─ ASM_grip_controls  Griff und Bedienung / Grip and controls
│   ├─ mag_release  Magazinhalter
│   ├─ grip  Pistolengriff
│   ├─ trigger  Abzug
│   ├─ trigger_guard  Abzugsbügel
│   ├─ selector  Feuerwahlhebel
│   ├─ selector_r  Feuerwahlhebel rechts
├─ ASM_support  Stützbereich / Support
│   ├─ handguard  Handschutz
│   ├─ handguard_cap  Handschutzkappe
│   ├─ vent_l1  Lüftungsöffnung links 1
│   ├─ vent_r1  Lüftungsöffnung rechts 1
│   ├─ vent_l2  Lüftungsöffnung links 2
│   ├─ vent_r2  Lüftungsöffnung rechts 2
│   ├─ vent_l3  Lüftungsöffnung links 3
│   ├─ vent_r3  Lüftungsöffnung rechts 3
│   ├─ vent_l4  Lüftungsöffnung links 4
│   ├─ vent_r4  Lüftungsöffnung rechts 4
├─ ASM_stock  Schaft / Stock
│   ├─ stock_joint  Schaftverbindung
│   ├─ stock_spine  Schaftrohr
│   ├─ stock  Schulterstütze
│   ├─ butt_pad  Schaftkappe
│   ├─ cheek_rest  Wangenauflage
├─ ASM_mechanism  Bewegliche Mechanik / Moving mechanism
│   ├─ port_cover  Auswurfklappe
│   ├─ charging_handle  Ladehebel
```

## Bauteilliste

| ID | Name (de / en) | Funktion | Befestigung | übergeordnet | Material | Maße X×Y×Z mm | Ursprung m | Bewegung | Entnahme | Schnittstelle | Aktionen |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `upper` | Oberes Gehäuse / Upper receiver | Tragkörper für Lauf, Verschluss und Schiene | mit Unterem Gehäuse über zwei Querbolzen (fest) | ASM_receiver | shell | 44×310×48 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `lower` | Unteres Gehäuse / Lower receiver | Nimmt Griffmodul, Abzugsgruppe und Magazinschacht auf | unter dem Oberen Gehäuse, Fuge 1 mm | ASM_receiver | shell | 42×306×46 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `mag_well` | Magazinschacht / Magazine well | Führt das Magazin; nach unten offen | am Unteren Gehäuse angeformt (fest) | ASM_receiver | shell | 31×51×21 | 0.000, 0.000, 0.000 | fest | nein | BMW-R | – |
| `port_cover` | Auswurfklappe / Ejection port cover | Deckt das Auswurffenster rechts ab; öffnet beim ersten Schuss | Scharnier an der Unterkante (dreht) | ASM_mechanism | dark_metal | 1.6×60×24 | -0.023, -0.050, 0.097 | dreht um Achse f durch (50, 97, -23) mm, 0…75°; Ereignis fire | nein | – | reload_empty, fire_auto |
| `ammo_counter` | Munitionsanzeige / Ammo counter | Zeigt den Füllstand; zurückhaltendes Leuchtfeld links hinten | in das Obere Gehäuse eingelassen | ASM_receiver | energy | 1.0×30×9.0 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `mag_release` | Magazinhalter / Magazine release | Löst das Magazin (Daumen der Haupthand) | Druckknopf im Unteren Gehäuse links | ASM_grip_controls | accent | 4.5×9.9×9.9 | 0.021, -0.074, 0.060 | verschiebt 2 mm (f,u,x (0, 0, -2.5)); Ereignis reload | ja – entlang Bewegung | – | reload_tactical, reload_empty |
| `rail` | Schiene / Top rail | Aufnahme für Visiere (BRI-22) | auf Oberem Gehäuse (fest) | ASM_receiver | dark_metal | 22×276×8.5 | 0.000, 0.000, 0.000 | fest | nein | BRI-22 | – |
| `sight_mount` | Visier-Klemmfuß / Sight mount | Klemmt das Visier auf die Schiene BRI-22 | Klemmung auf Schiene (lösbar) | ASM_sight | dark_metal | 26×50×7.5 | 0.000, -0.019, 0.143 | verschiebt 70 mm (f,u,x (0, 70, 0)); Ereignis swap_sight | ja – nach Lösen der Klemmschraube senkrecht abnehmen | BRI-22 | – |
| `sight_clamp` | Klemmschraube / Clamp screw | Spannt den Klemmfuß (Werkzeuglos, Rändel) | quer im Klemmfuß links | sight_mount | dark_metal | 6.0×11×11 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_body` | Visiergehäuse / Sight housing | Trägt Emitter und Batterie; hintere Kante = Socket_Sight | auf Klemmfuß (fest) | sight_mount | graphite | 26×49×8.5 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_frame` | Haubenrahmen / Sight hood frame | Hält und schützt das Glas; offener Rahmen für freie Durchsicht | auf Visiergehäuse (fest) | sight_mount | graphite | 40×12×34 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_glass` | Visierglas / Sight glass | Reflexscheibe; das Absehen erscheint auf ihr | im Rahmen (fest) | sight_mount | glass | 31×1.0×25 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_emitter` | Emitter / Reticle emitter | Leuchtfenster des Absehen-Projektors (zurückhaltend) | vorn im Emitterblock | sight_mount | energy | 7.0×2.0×2.2 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `grip` | Pistolengriff / Pistol grip | Haupthand hält die Waffe; trägt Socket_Hand | mit Unterem Gehäuse verschraubt (fest) | ASM_grip_controls | graphite | 30×68×106 | 0.000, 0.000, 0.000 | fest | nein | BGM-1 | – |
| `trigger` | Abzug / Trigger | Feuer auslösen (Zeigefinger) | Drehpunkt im Unteren Gehäuse | ASM_grip_controls | metal | 7.0×7.8×26 | 0.000, -0.045, 0.039 | dreht um Achse x durch (45.25386608210715, 39, 0) mm, 0…-12°; Ereignis fire | nein | – | fire_auto |
| `trigger_guard` | Abzugsbügel / Trigger guard | Schützt den Abzug, Fingerfreiraum ≥ 22 mm | Griff vorn und Unteres Gehäuse (fest) | ASM_grip_controls | graphite | 12×58×35 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `selector` | Feuerwahlhebel / Fire selector | Sichern / Feuer, mit dem Daumen der Haupthand | Achse quer im Unteren Gehäuse | ASM_grip_controls | accent | 3.0×20×8.0 | 0.000, -0.008, 0.070 | dreht um Achse x durch (8, 70, 0) mm, 0…90°; Ereignis safety | nein | – | safety |
| `selector_r` | Feuerwahlhebel rechts / Fire selector right | Sichern / Feuer, mit dem Daumen der Haupthand | Achse quer im Unteren Gehäuse | ASM_grip_controls | accent | 3.0×20×8.0 | 0.000, -0.008, 0.070 | dreht um Achse x durch (8, 70, 0) mm, 0…90°; Ereignis safety | nein | – | safety |
| `magazine` | Magazin / Magazine | Hält die Patronen; entnehmbar | rastet im Magazinschacht ein (lösbar, Magazinhalter) | ASM_ammo | shell | 24×64×144 | 0.000, -0.108, 0.072 | verschiebt 160 mm (f,u,x (22.3, -158.4, 0)); Ereignis reload | ja – Entnahme entlang der Magazinachse nach unten; Schacht nach unten offen | BMW-R | reload_tactical, reload_empty |
| `magazine_base` | Magazinboden / Magazine base plate | Greifkante zum Herausziehen | am Magazin (fest) | magazine | graphite | 27×44×15 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `magazine_round` | Oberste Patrone / Top round | Zeigt den Ladezustand im Schacht | im Magazin | magazine | metal | 8.8×30×8.8 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `handguard` | Handschutz / Handguard | Griffbereich der Stützhand; trägt Socket_SupportHand | am Oberen Gehäuse verschraubt, Fuge 1 mm | ASM_support | graphite | 46×233×65 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `handguard_cap` | Handschutzkappe / Handguard end cap | Stirnabschluss; Lauf tritt mittig aus, Hitzeschutz | auf das Handschutzende gesteckt (fest) | ASM_support | dark_metal | 40×11×40 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_l1` | Lüftungsöffnung links 1 / Vent left 1 | Kühlluft am Lauf vorbei; tiefliegendes Gitter | in den Handschutz eingelassen | ASM_support | dark_metal | 1.4×26×12 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_r1` | Lüftungsöffnung rechts 1 / Vent right 1 | Kühlluft am Lauf vorbei; tiefliegendes Gitter | in den Handschutz eingelassen | ASM_support | dark_metal | 1.4×26×12 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_l2` | Lüftungsöffnung links 2 / Vent left 2 | Kühlluft am Lauf vorbei; tiefliegendes Gitter | in den Handschutz eingelassen | ASM_support | dark_metal | 1.4×26×12 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_r2` | Lüftungsöffnung rechts 2 / Vent right 2 | Kühlluft am Lauf vorbei; tiefliegendes Gitter | in den Handschutz eingelassen | ASM_support | dark_metal | 1.4×26×12 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_l3` | Lüftungsöffnung links 3 / Vent left 3 | Kühlluft am Lauf vorbei; tiefliegendes Gitter | in den Handschutz eingelassen | ASM_support | dark_metal | 1.4×26×12 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_r3` | Lüftungsöffnung rechts 3 / Vent right 3 | Kühlluft am Lauf vorbei; tiefliegendes Gitter | in den Handschutz eingelassen | ASM_support | dark_metal | 1.4×26×12 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_l4` | Lüftungsöffnung links 4 / Vent left 4 | Kühlluft am Lauf vorbei; tiefliegendes Gitter | in den Handschutz eingelassen | ASM_support | dark_metal | 1.4×26×12 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_r4` | Lüftungsöffnung rechts 4 / Vent right 4 | Kühlluft am Lauf vorbei; tiefliegendes Gitter | in den Handschutz eingelassen | ASM_support | dark_metal | 1.4×26×12 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `barrel` | Lauf / Barrel | Führt das Geschoss | im Gehäuse/Handschutz verschraubt | ASM_barrel | metal | 20×136×20 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `muzzle` | Mündungsbremse / Muzzle brake | Mündungsteil; Socket_Muzzle an der Stirnfläche | auf Laufende geschraubt (lösbar) | ASM_barrel | dark_metal | 28×50×28 | 0.000, 0.000, 0.000 | fest | nein | BMZ-15 | – |
| `stock_joint` | Schaftverbindung / Stock joint | Verbindet Schaft und Gehäuse; Verriegelung | Steckverbindung am Gehäuseende (fest) | ASM_stock | dark_metal | 30×12×42 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `stock_spine` | Schaftrohr / Stock spine | Trägt die Schulterstütze in Linie mit dem Lauf | in der Schaftverbindung (fest) | ASM_stock | graphite | 28×82×28 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `stock` | Schulterstütze / Buttstock | Anlage an der Schulter, Wangenauflage oben | auf dem Schaftrohr (fest) | ASM_stock | shell | 36×78×106 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `butt_pad` | Schaftkappe / Butt pad | Rutschfeste Anlage an der Schulter | auf das Schaftende gesteckt (fest) | ASM_stock | graphite | 40×16×115 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `cheek_rest` | Wangenauflage / Cheek rest | Anlage für die Wange beim Zielen | auf der Schulterstütze (fest) | ASM_stock | graphite | 26×66×10 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `charging_handle` | Ladehebel / Charging handle | Verschluss spannen (Stützhand zieht nach hinten) | in Längsnut links (gleitet) | ASM_mechanism | accent | 9.0×30×12 | 0.022, 0.096, 0.121 | verschiebt 60 mm (f,u,x (-60, 0, 0)); Ereignis charge | nein | – | reload_empty |

## Anker

| Anker | Position m (X, Y, Z) | Teil | Hinweis |
|---|---|---|---|
| `Socket_Hand` | 0.0000, 0.0000, 0.0000 | grip | Haupthand, auf der Griffachse |
| `Socket_SupportHand` | 0.0000, -0.2820, 0.0950 | handguard | Mitte Handschutz, Stützhand umgreift |
| `Socket_Muzzle` | 0.0000, -0.6060, 0.1060 | muzzle | Stirnfläche Mündungsbremse auf der Laufachse |
| `Socket_MagWell` | 0.0000, -0.1080, 0.0700 | mag_well | Einrastpunkt Magazin (Schnittstelle BMW-R) |
| `Socket_Charge` | 0.0270, 0.0830, 0.1210 | charging_handle | Griffpunkt Ladehebel für die Stützhand |
| `Socket_Sight` | 0.0000, 0.0050, 0.1720 | sight_body | hinteres Visierende auf der Visierlinie |
| `Socket_Reticle` | 0.0000, -0.0380, 0.1720 | sight_glass | Mitte Glas |
| `Socket_Eye` | 0.0000, -0.0320, 0.1720 | sight_frame | Vorschlag nach Formgen-Regel: hinterer Fensterrand (Reflexvisier ohne festen Augenabstand) |
| `Socket_CenterOfMass` | 0.0000, -0.0953, 0.0849 | – | abgeleitet: Volumenschwerpunkt, homogene Dichte, ohne Glas |

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
| `reload_tactical` | Nachladen mit Restmunition | 66 (2.20 s) | mag_release, magazine | mag_release (6), mag_out (20), mag_seated (50) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |
| `reload_empty` | Nachladen aus leerem Zustand | 84 (2.80 s) | mag_release, magazine, charging_handle, port_cover | mag_out (18), mag_seated (50), charge (66), ready (72) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |
| `fire_auto` | Dauerfeuer (Mechanik) | 30 (1.00 s) | trigger, port_cover | shot (3), shot (7), shot (11), shot (15), shot (19), shot (23) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |
| `safety` | Sichern / Entsichern | 20 (0.67 s) | selector, selector_r | safe (8) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |

Haltungen, Übergänge und Status aller Aktionen: [haltungen.md › BASIC-01](../haltungen.md#basic-01).
