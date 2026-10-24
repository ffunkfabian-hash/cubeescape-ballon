<!-- erzeugt von tools/make_docs.py – nicht von Hand ändern -->

# BASIC-06 Maschinenpistole – „Kurzläufer“

Kompakte Maschinenpistole, Magazin im Griff, Vordergriff.

Typ `submachine_gun` (Submachine Gun) · Munition primary · Feuerart `full_auto` · Quelle des Entwurfs: `basic/weapons/` · Spec: [`data/specs/BASIC-06.spec.json`](../../data/specs/BASIC-06.spec.json).

**Maße (gemessen, Ruhelage, Visier montiert):** Länge 559 mm · Höhe 292 mm · Breite 46 mm · 29 Bauteile · 4636 Dreiecke (mit Fasen).

Rahmen: Meter, vorn −Y, oben +Z, links +X, Ursprung `Socket_Hand`. `origin_m` ist der Objektursprung (bei beweglichen Teilen der Drehpunkt).

## Baugruppenbaum

```
BASIC-06
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
│   ├─ sight_mount  Visier-Klemmfuß
│   │  └(an sight_mount) sight_clamp  Klemmschraube
│   │  └(an sight_mount) sight_body  Visiergehäuse
│   │  └(an sight_mount) sight_frame  Haubenrahmen
│   │  └(an sight_mount) sight_glass  Visierglas
│   │  └(an sight_mount) sight_emitter  Emitter
├─ ASM_grip_controls  Griff und Bedienung / Grip and controls
│   ├─ grip  Pistolengriff
│   ├─ trigger  Abzug
│   ├─ trigger_guard  Abzugsbügel
│   ├─ selector  Feuerwahlhebel
├─ ASM_support  Stützbereich / Support
│   ├─ handguard  Handschutz
│   ├─ foregrip  Vordergriff
│   ├─ vent_l1  Lüftungsöffnung links 1
│   ├─ vent_r1  Lüftungsöffnung rechts 1
│   ├─ vent_l2  Lüftungsöffnung links 2
│   ├─ vent_r2  Lüftungsöffnung rechts 2
├─ ASM_stock  Schaft / Stock
│   ├─ stock_joint  Schaftverbindung
│   ├─ stock_spine  Schaftrohr
│   ├─ stock  Schulterstütze
│   ├─ butt_pad  Schaftkappe
├─ ASM_mechanism  Bewegliche Mechanik / Moving mechanism
│   ├─ port_cover  Auswurfklappe
│   ├─ charging_handle  Ladehebel
```

## Bauteilliste

| ID | Name (de / en) | Funktion | Befestigung | übergeordnet | Material | Maße X×Y×Z mm | Ursprung m | Bewegung | Entnahme | Schnittstelle | Aktionen |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `receiver` | Gehäuse / Receiver | Einteiliger Tragkörper | Grundkörper | ASM_receiver | shell | 40×270×72 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `handguard` | Handschutz / Handguard | Kurzer Handschutz um den Lauf | am Gehäuse, Fuge 1 mm | ASM_support | graphite | 38×103×52 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `foregrip` | Vordergriff / Foregrip | Senkrechter Griff der Stützhand; Socket_SupportHand | unter den Handschutz geschraubt | ASM_support | graphite | 28×35×65 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `port_cover` | Auswurfklappe / Ejection port cover | Auswurffenster rechts | Scharnier unten | ASM_mechanism | dark_metal | 1.6×52×20 | -0.021, -0.066, 0.080 | dreht um Achse f durch (66, 80, -21) mm, 0…75°; Ereignis fire | nein | – | fire_auto |
| `vent_l1` | Lüftungsöffnung links 1 / Vent left 1 | Kühlluft; tiefliegendes Gitter | eingelassen | ASM_support | dark_metal | 1.4×26×10 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_r1` | Lüftungsöffnung rechts 1 / Vent right 1 | Kühlluft; tiefliegendes Gitter | eingelassen | ASM_support | dark_metal | 1.4×26×10 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_l2` | Lüftungsöffnung links 2 / Vent left 2 | Kühlluft; tiefliegendes Gitter | eingelassen | ASM_support | dark_metal | 1.4×26×10 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_r2` | Lüftungsöffnung rechts 2 / Vent right 2 | Kühlluft; tiefliegendes Gitter | eingelassen | ASM_support | dark_metal | 1.4×26×10 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `barrel` | Lauf / Barrel | Führt das Geschoss | im Gehäuse/Handschutz verschraubt | ASM_barrel | metal | 16×34×16 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `muzzle` | Mündungsbremse / Muzzle brake | Mündungsteil; Socket_Muzzle an der Stirnfläche | auf Laufende geschraubt (lösbar) | ASM_barrel | dark_metal | 22×28×22 | 0.000, 0.000, 0.000 | fest | nein | BMZ-15 | – |
| `rail` | Schiene / Top rail | Aufnahme für Visiere (BRI-22) | auf Oberem Gehäuse (fest) | ASM_receiver | dark_metal | 22×210×8.5 | 0.000, 0.000, 0.000 | fest | nein | BRI-22 | – |
| `sight_mount` | Visier-Klemmfuß / Sight mount | Klemmt das Visier auf die Schiene BRI-22 | Klemmung auf Schiene (lösbar) | ASM_sight | dark_metal | 26×50×7.5 | 0.000, -0.025, 0.120 | verschiebt 70 mm (f,u,x (0, 70, 0)); Ereignis swap_sight | ja – nach Lösen der Klemmschraube senkrecht abnehmen | BRI-22 | – |
| `sight_clamp` | Klemmschraube / Clamp screw | Spannt den Klemmfuß (Werkzeuglos, Rändel) | quer im Klemmfuß links | sight_mount | dark_metal | 6.0×11×11 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_body` | Visiergehäuse / Sight housing | Trägt Emitter und Batterie; hintere Kante = Socket_Sight | auf Klemmfuß (fest) | sight_mount | graphite | 26×49×8.5 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_frame` | Haubenrahmen / Sight hood frame | Hält und schützt das Glas; offener Rahmen für freie Durchsicht | auf Visiergehäuse (fest) | sight_mount | graphite | 36×12×30 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_glass` | Visierglas / Sight glass | Reflexscheibe; das Absehen erscheint auf ihr | im Rahmen (fest) | sight_mount | glass | 27×1.0×21 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_emitter` | Emitter / Reticle emitter | Leuchtfenster des Absehen-Projektors (zurückhaltend) | vorn im Emitterblock | sight_mount | energy | 7.0×2.0×2.2 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `grip` | Pistolengriff / Pistol grip | Haupthand hält die Waffe; trägt Socket_Hand | mit Unterem Gehäuse verschraubt (fest) | ASM_grip_controls | graphite | 34×56×104 | 0.000, 0.000, 0.000 | fest | nein | BGM-1 | – |
| `trigger` | Abzug / Trigger | Feuer auslösen (Zeigefinger) | Drehpunkt im Unteren Gehäuse | ASM_grip_controls | metal | 7.0×7.8×26 | 0.000, -0.040, 0.037 | dreht um Achse x durch (39.62163338809566, 37, 0) mm, 0…-12°; Ereignis fire | nein | – | fire_auto |
| `trigger_guard` | Abzugsbügel / Trigger guard | Schützt den Abzug, Fingerfreiraum ≥ 22 mm | Griff vorn und Unteres Gehäuse (fest) | ASM_grip_controls | graphite | 12×58×35 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `selector` | Feuerwahlhebel / Fire selector | Sichern / Feuer, mit dem Daumen der Haupthand | Achse quer im Unteren Gehäuse | ASM_grip_controls | accent | 3.0×20×8.0 | 0.000, 0.030, 0.070 | dreht um Achse x durch (-30, 70, 0) mm, 0…90°; Ereignis safety | nein | – | – |
| `magazine` | Magazin / Magazine | Hält die Patronen; entnehmbar | rastet im Magazinschacht ein (lösbar, Magazinhalter) | ASM_ammo | shell | 22×51×162 | 0.000, -0.005, 0.040 | verschiebt 160 mm (f,u,x (-22.3, -158.4, 0)); Ereignis reload | ja – Entnahme entlang der Magazinachse nach unten; Schacht nach unten offen | BMW-R | reload_empty |
| `magazine_base` | Magazinboden / Magazine base plate | Greifkante zum Herausziehen | am Magazin (fest) | magazine | graphite | 25×35×14 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `magazine_round` | Oberste Patrone / Top round | Zeigt den Ladezustand im Schacht | im Magazin | magazine | metal | 8.8×20×8.8 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `stock_joint` | Schaftverbindung / Stock joint | Verbindet Schaft und Gehäuse; Verriegelung | Steckverbindung am Gehäuseende (fest) | ASM_stock | dark_metal | 30×12×42 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `stock_spine` | Schaftrohr / Stock spine | Trägt die Schulterstütze in Linie mit dem Lauf | in der Schaftverbindung (fest) | ASM_stock | graphite | 28×56×28 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `stock` | Schulterstütze / Buttstock | Anlage an der Schulter, Wangenauflage oben | auf dem Schaftrohr (fest) | ASM_stock | shell | 36×56×106 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `butt_pad` | Schaftkappe / Butt pad | Rutschfeste Anlage an der Schulter | auf das Schaftende gesteckt (fest) | ASM_stock | graphite | 40×12×115 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `charging_handle` | Ladehebel / Charging handle | Verschluss spannen (Stützhand zieht nach hinten) | in Längsnut links (gleitet) | ASM_mechanism | accent | 9.0×30×12 | 0.021, 0.070, 0.100 | verschiebt 45 mm (f,u,x (-45, 0, 0)); Ereignis charge | nein | – | reload_empty |

## Anker

| Anker | Position m (X, Y, Z) | Teil | Hinweis |
|---|---|---|---|
| `Socket_Hand` | 0.0000, 0.0000, 0.0000 | grip | – |
| `Socket_SupportHand` | 0.0000, -0.2360, 0.0240 | foregrip | – |
| `Socket_Muzzle` | 0.0000, -0.3400, 0.0820 | muzzle | – |
| `Socket_MagWell` | 0.0000, 0.0000, 0.0400 | grip | Magazinschacht im Griff |
| `Socket_Sight` | 0.0000, -0.0010, 0.1470 | sight_body | hinteres Visierende auf der Visierlinie |
| `Socket_Reticle` | 0.0000, -0.0440, 0.1470 | sight_glass | Mitte Glas |
| `Socket_Eye` | 0.0000, -0.0380, 0.1470 | sight_frame | Vorschlag nach Formgen-Regel: hinterer Fensterrand (Reflexvisier ohne festen Augenabstand) |
| `Socket_CenterOfMass` | 0.0000, -0.0398, 0.0595 | – | abgeleitet: Volumenschwerpunkt, homogene Dichte, ohne Glas |

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
| `fire_auto` | Dauerfeuer (Mechanik) | 24 (0.80 s) | trigger, port_cover | shot (2), shot (5), shot (7), shot (10), shot (12), shot (15), shot (17), shot (20) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |
| `reload_empty` | Nachladen aus leerem Zustand | 78 (2.60 s) | magazine, charging_handle | mag_out (16), mag_seated (48), charge (62), ready (70) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |

Haltungen, Übergänge und Status aller Aktionen: [haltungen.md › BASIC-06](../haltungen.md#basic-06).
