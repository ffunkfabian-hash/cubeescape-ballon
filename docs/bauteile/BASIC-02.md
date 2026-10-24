<!-- erzeugt von tools/make_docs.py – nicht von Hand ändern -->

# BASIC-02 Impulsgewehr – „Impuls“

Impulsgewehr mit Dreier-Salve, Impulskammer und Holo-Visier.

Typ `pulse_rifle` (Pulse Rifle) · Munition primary · Feuerart `burst_3` · Quelle des Entwurfs: `basic/weapons/` · Spec: [`data/specs/BASIC-02.spec.json`](../../data/specs/BASIC-02.spec.json).

**Maße (gemessen, Ruhelage, Visier montiert):** Länge 797 mm · Höhe 255 mm · Breite 50 mm · 28 Bauteile · 4548 Dreiecke (mit Fasen).

Rahmen: Meter, vorn −Y, oben +Z, links +X, Ursprung `Socket_Hand`. `origin_m` ist der Objektursprung (bei beweglichen Teilen der Drehpunkt).

## Baugruppenbaum

```
BASIC-02
├─ ASM_receiver  Hauptgehäuse / Receiver
│   ├─ upper  Oberes Gehäuse
│   ├─ lower  Unteres Gehäuse
│   ├─ mag_well  Magazinschacht
│   ├─ rail  Schiene
├─ ASM_barrel  Lauf / Emitter / Barrel / emitter
│   ├─ pulse_chamber  Impulskammer
│   ├─ burst_1  Salvenanzeige 1
│   ├─ burst_2  Salvenanzeige 2
│   ├─ burst_3  Salvenanzeige 3
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
| `upper` | Oberes Gehäuse / Upper receiver | Tragkörper für Kammer und Schiene | mit Unterem Gehäuse verbolzt | ASM_receiver | shell | 44×260×51 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `lower` | Unteres Gehäuse / Lower receiver | Griffmodul, Abzug und Magazinschacht | unter dem Oberen Gehäuse, Fuge 1 mm | ASM_receiver | shell | 42×250×43 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `mag_well` | Magazinschacht / Magazine well | Führt das Magazin | am Unteren Gehäuse | ASM_receiver | shell | 30×46×14 | 0.000, 0.000, 0.000 | fest | nein | BMW-R | – |
| `pulse_chamber` | Impulskammer / Pulse chamber | Ummantelt Lauf und Impulsspule; formt die Salve | am Oberen Gehäuse verschraubt, Fuge 1 mm | ASM_barrel | shell | 42×257×32 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `handguard` | Handschutz / Handguard | Griffbereich der Stützhand | unter der Impulskammer, Fuge 1 mm | ASM_support | graphite | 44×227×34 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `burst_1` | Salvenanzeige 1 / Burst pip 1 | Leuchtet beim 1. Impuls | eingelassen | ASM_barrel | energy | 1.0×16×8.0 | 0.000, 0.000, 0.000 | Leuchten 0…5.0 (Ereignis charge) | nein | – | fire_burst |
| `burst_2` | Salvenanzeige 2 / Burst pip 2 | Leuchtet beim 2. Impuls | eingelassen | ASM_barrel | energy | 1.0×16×8.0 | 0.000, 0.000, 0.000 | Leuchten 0…5.0 (Ereignis charge) | nein | – | fire_burst |
| `burst_3` | Salvenanzeige 3 / Burst pip 3 | Leuchtet beim 3. Impuls | eingelassen | ASM_barrel | energy | 1.0×16×8.0 | 0.000, 0.000, 0.000 | Leuchten 0…5.0 (Ereignis charge) | nein | – | fire_burst |
| `port_cover` | Auswurfklappe / Ejection port cover | Auswurffenster rechts | Scharnier unten | ASM_mechanism | dark_metal | 1.6×54×24 | -0.023, -0.057, 0.092 | dreht um Achse f durch (57, 92, -23) mm, 0…75°; Ereignis fire | nein | – | fire_burst |
| `barrel` | Lauf / Barrel | Führt das Geschoss | im Gehäuse/Handschutz verschraubt | ASM_barrel | metal | 18×68×18 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `muzzle` | Mündungsbremse / Muzzle brake | Mündungsteil; Socket_Muzzle an der Stirnfläche | auf Laufende geschraubt (lösbar) | ASM_barrel | dark_metal | 24×36×24 | 0.000, 0.000, 0.000 | fest | nein | BMZ-15 | – |
| `rail` | Schiene / Top rail | Aufnahme für Visiere (BRI-22) | auf Oberem Gehäuse (fest) | ASM_receiver | dark_metal | 22×230×8.5 | 0.000, 0.000, 0.000 | fest | nein | BRI-22 | – |
| `sight_mount` | Visier-Klemmfuß / Sight mount | Klemmt das Visier auf die Schiene BRI-22 | Klemmung auf Schiene (lösbar) | ASM_sight | dark_metal | 26×50×7.5 | 0.000, -0.011, 0.141 | verschiebt 70 mm (f,u,x (0, 70, 0)); Ereignis swap_sight | ja – nach Lösen der Klemmschraube senkrecht abnehmen | BRI-22 | – |
| `sight_clamp` | Klemmschraube / Clamp screw | Spannt den Klemmfuß (Werkzeuglos, Rändel) | quer im Klemmfuß links | sight_mount | dark_metal | 6.0×11×11 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_body` | Visiergehäuse / Sight housing | Trägt Emitter und Batterie; hintere Kante = Socket_Sight | auf Klemmfuß (fest) | sight_mount | graphite | 26×49×8.5 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_frame` | Haubenrahmen / Sight hood frame | Hält und schützt das Glas; offener Rahmen für freie Durchsicht | auf Visiergehäuse (fest) | sight_mount | graphite | 44×12×38 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_glass` | Visierglas / Sight glass | Reflexscheibe; das Absehen erscheint auf ihr | im Rahmen (fest) | sight_mount | glass | 35×1.0×29 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_emitter` | Emitter / Reticle emitter | Leuchtfenster des Absehen-Projektors (zurückhaltend) | vorn im Emitterblock | sight_mount | energy | 7.0×2.0×2.2 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `grip` | Pistolengriff / Pistol grip | Haupthand hält die Waffe; trägt Socket_Hand | mit Unterem Gehäuse verschraubt (fest) | ASM_grip_controls | graphite | 30×68×104 | 0.000, 0.000, 0.000 | fest | nein | BGM-1 | – |
| `trigger` | Abzug / Trigger | Feuer auslösen (Zeigefinger) | Drehpunkt im Unteren Gehäuse | ASM_grip_controls | metal | 7.0×7.8×26 | 0.000, -0.045, 0.037 | dreht um Achse x durch (44.71796769724491, 37, 0) mm, 0…-12°; Ereignis fire | nein | – | fire_burst |
| `trigger_guard` | Abzugsbügel / Trigger guard | Schützt den Abzug, Fingerfreiraum ≥ 22 mm | Griff vorn und Unteres Gehäuse (fest) | ASM_grip_controls | graphite | 12×58×35 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `selector` | Feuerwahlhebel / Fire selector | Sichern / Feuer, mit dem Daumen der Haupthand | Achse quer im Unteren Gehäuse | ASM_grip_controls | accent | 3.0×20×8.0 | 0.000, -0.004, 0.064 | dreht um Achse x durch (4, 64, 0) mm, 0…90°; Ereignis safety | nein | – | – |
| `magazine` | Magazin / Magazine | Hält die Patronen; entnehmbar | rastet im Magazinschacht ein (lösbar, Magazinhalter) | ASM_ammo | shell | 24×38×104 | 0.000, -0.099, 0.062 | verschiebt 160 mm (f,u,x (0.0, -160.0, 0)); Ereignis reload | ja – Entnahme entlang der Magazinachse nach unten; Schacht nach unten offen | BMW-R | reload_empty |
| `magazine_base` | Magazinboden / Magazine base plate | Greifkante zum Herausziehen | am Magazin (fest) | magazine | graphite | 27×42×9.5 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `magazine_round` | Oberste Patrone / Top round | Zeigt den Ladezustand im Schacht | im Magazin | magazine | metal | 8.8×28×8.8 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `stock` | Schulterstütze S2 / Stock S2 | Einteilige Schulterstütze; Wange liegt oben auf | mit zwei Bolzen am Gehäuse (fest) | ASM_stock | graphite | 34×176×101 | 0.000, 0.000, 0.000 | fest | nein | BST-2 | – |
| `butt_pad` | Schaftkappe / Butt pad | Anlage an der Schulter | auf das Schaftende geschraubt | ASM_stock | dark_metal | 38×14×101 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `charging_handle` | Ladehebel / Charging handle | Verschluss spannen (Stützhand zieht nach hinten) | in Längsnut links (gleitet) | ASM_mechanism | accent | 9.0×30×12 | 0.022, 0.086, 0.118 | verschiebt 55 mm (f,u,x (-55, 0, 0)); Ereignis charge | nein | – | reload_empty |

## Anker

| Anker | Position m (X, Y, Z) | Teil | Hinweis |
|---|---|---|---|
| `Socket_Hand` | 0.0000, 0.0000, 0.0000 | grip | – |
| `Socket_SupportHand` | 0.0000, -0.2700, 0.0820 | handguard | Mitte Handschutz unter der Kammer |
| `Socket_Muzzle` | 0.0000, -0.5000, 0.1000 | muzzle | – |
| `Socket_MagWell` | 0.0000, -0.0990, 0.0620 | mag_well | – |
| `Socket_Sight` | 0.0000, 0.0130, 0.1720 | sight_body | hinteres Visierende auf der Visierlinie |
| `Socket_Reticle` | 0.0000, -0.0300, 0.1720 | sight_glass | Mitte Glas |
| `Socket_Eye` | 0.0000, -0.0240, 0.1720 | sight_frame | Vorschlag nach Formgen-Regel: hinterer Fensterrand (Reflexvisier ohne festen Augenabstand) |
| `Socket_CenterOfMass` | 0.0000, -0.0514, 0.0829 | – | abgeleitet: Volumenschwerpunkt, homogene Dichte, ohne Glas |

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
| `fire_burst` | Dreier-Salve (Mechanik und Anzeige) | 24 (0.80 s) | trigger, burst_1, burst_2, burst_3, port_cover | shot (2), shot (6), shot (10), ready (23) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |
| `reload_empty` | Nachladen aus leerem Zustand | 80 (2.67 s) | magazine, charging_handle | mag_out (16), mag_seated (48), charge (64), ready (72) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |

Haltungen, Übergänge und Status aller Aktionen: [haltungen.md › BASIC-02](../haltungen.md#basic-02).
