<!-- erzeugt von tools/make_docs.py – nicht von Hand ändern -->

# BASIC-15 Maschinengewehr – „Dauerlauf“

Gurtgespeistes Maschinengewehr mit Munitionskasten und Tragegriff.

Typ `machine_gun` (Machine Gun) · Munition heavy · Feuerart `full_auto_belt` · Quelle des Entwurfs: `basic/weapons/` · Spec: [`data/specs/BASIC-15.spec.json`](../../data/specs/BASIC-15.spec.json).

**Maße (gemessen, Ruhelage, Visier montiert):** Länge 1073 mm · Höhe 284 mm · Breite 108 mm · 33 Bauteile · 5040 Dreiecke (mit Fasen).

Rahmen: Meter, vorn −Y, oben +Z, links +X, Ursprung `Socket_Hand`. `origin_m` ist der Objektursprung (bei beweglichen Teilen der Drehpunkt).

## Baugruppenbaum

```
BASIC-15
├─ ASM_receiver  Hauptgehäuse / Receiver
│   ├─ receiver  Gehäuse
│   │  └(an feed_cover) rail  Schiene
├─ ASM_barrel  Lauf / Emitter / Barrel / emitter
│   ├─ barrel  Lauf
│   ├─ muzzle  Mündungsbremse
├─ ASM_ammo  Munitionsversorgung / Ammunition feed
│   ├─ feed_tray  Zuführschale
│   ├─ ammo_box  Munitionskasten
│   │  └(an ammo_box) ammo_box_lid  Kastendeckel
│   │  └(an ammo_box) belt  Gurtstück
├─ ASM_sight  Visier / Sight
│   │  └(an feed_cover) sight_mount  Visier-Klemmfuß
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
│   ├─ shroud  Laufmantel
│   ├─ shroud_grip  Stützgriffzone
│   ├─ carry_handle  Tragegriff
│   ├─ vent_l1  Lüftungsöffnung links 1
│   ├─ vent_r1  Lüftungsöffnung rechts 1
│   ├─ vent_l2  Lüftungsöffnung links 2
│   ├─ vent_r2  Lüftungsöffnung rechts 2
│   ├─ vent_l3  Lüftungsöffnung links 3
│   ├─ vent_r3  Lüftungsöffnung rechts 3
├─ ASM_stock  Schaft / Stock
│   ├─ stock_joint  Schaftverbindung
│   ├─ stock_spine  Schaftrohr
│   ├─ stock  Schulterstütze
│   ├─ butt_pad  Schaftkappe
│   ├─ cheek_rest  Wangenauflage
├─ ASM_mechanism  Bewegliche Mechanik / Moving mechanism
│   ├─ feed_cover  Zuführdeckel
```

## Bauteilliste

| ID | Name (de / en) | Funktion | Befestigung | übergeordnet | Material | Maße X×Y×Z mm | Ursprung m | Bewegung | Entnahme | Schnittstelle | Aktionen |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `receiver` | Gehäuse / Receiver | Breiter Tragkörper; Zuführung oben links | Grundkörper | ASM_receiver | shell | 56×370×100 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `feed_cover` | Zuführdeckel / Feed cover | Hält den Gurt in der Zuführung; trägt das Visier | Scharnier vorn, öffnet hinten nach oben | ASM_mechanism | shell | 52×226×21 | 0.000, -0.150, 0.146 | dreht um Achse x durch (150, 146, 0) mm, 0…-62°; Ereignis reload | nein | – | reload |
| `feed_tray` | Zuführschale / Feed tray | Führt den Gurt ins Gehäuse | oben im Gehäuse | ASM_ammo | dark_metal | 50×80×5.0 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `ammo_box` | Munitionskasten / Ammo box | Hält den Gurt; austauschbar | links am Gehäuse eingehängt (lösbar) | ASM_ammo | dark_metal | 46×120×106 | 0.056, -0.050, 0.060 | verschiebt 114 mm (f,u,x (0, -70, 90)); Ereignis reload | ja – entlang Bewegung | BAB-1 | reload |
| `ammo_box_lid` | Kastendeckel / Ammo box lid | Deckel mit Griffmulde | auf dem Munitionskasten | ammo_box | shell | 48×124×8.0 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `belt` | Gurtstück / Belt section | Sichtbarer Gurt vom Kasten zur Zuführung | zwischen Kasten und Zuführschale | ammo_box | metal | 16×60×22 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `shroud` | Laufmantel / Barrel shroud | Hitzeschutz; Griffbereich der Stützhand unten | am Gehäuse verschraubt, Fuge 1 mm | ASM_support | shell | 46×319×60 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `shroud_grip` | Stützgriffzone / Support grip zone | Griffbereich der Stützhand | unter dem Laufmantel | ASM_support | graphite | 44×176×16 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `carry_handle` | Tragegriff / Carry handle | Tragen und Laufwechsel | auf dem Laufmantel | ASM_support | graphite | 16×110×39 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_l1` | Lüftungsöffnung links 1 / Vent left 1 | Kühlluft; tiefliegendes Gitter | eingelassen | ASM_support | dark_metal | 1.4×34×14 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_r1` | Lüftungsöffnung rechts 1 / Vent right 1 | Kühlluft; tiefliegendes Gitter | eingelassen | ASM_support | dark_metal | 1.4×34×14 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_l2` | Lüftungsöffnung links 2 / Vent left 2 | Kühlluft; tiefliegendes Gitter | eingelassen | ASM_support | dark_metal | 1.4×34×14 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_r2` | Lüftungsöffnung rechts 2 / Vent right 2 | Kühlluft; tiefliegendes Gitter | eingelassen | ASM_support | dark_metal | 1.4×34×14 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_l3` | Lüftungsöffnung links 3 / Vent left 3 | Kühlluft; tiefliegendes Gitter | eingelassen | ASM_support | dark_metal | 1.4×34×14 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `vent_r3` | Lüftungsöffnung rechts 3 / Vent right 3 | Kühlluft; tiefliegendes Gitter | eingelassen | ASM_support | dark_metal | 1.4×34×14 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `barrel` | Lauf / Barrel | Führt das Geschoss | im Gehäuse/Handschutz verschraubt | ASM_barrel | metal | 24×140×24 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `muzzle` | Mündungsbremse / Muzzle brake | Mündungsteil; Socket_Muzzle an der Stirnfläche | auf Laufende geschraubt (lösbar) | ASM_barrel | dark_metal | 31×52×31 | 0.000, 0.000, 0.000 | fest | nein | BMZ-15 | – |
| `rail` | Schiene / Top rail | Aufnahme für Visiere (BRI-22) | auf Oberem Gehäuse (fest) | feed_cover | dark_metal | 22×190×8.5 | 0.000, 0.000, 0.000 | fest | nein | BRI-22 | – |
| `sight_mount` | Visier-Klemmfuß / Sight mount | Klemmt das Visier auf die Schiene BRI-22 | Klemmung auf Schiene (lösbar) | feed_cover | dark_metal | 26×50×7.5 | 0.000, 0.015, 0.170 | verschiebt 70 mm (f,u,x (0, 70, 0)); Ereignis swap_sight | ja – nach Lösen der Klemmschraube senkrecht abnehmen | BRI-22 | – |
| `sight_clamp` | Klemmschraube / Clamp screw | Spannt den Klemmfuß (Werkzeuglos, Rändel) | quer im Klemmfuß links | sight_mount | dark_metal | 6.0×11×11 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_body` | Visiergehäuse / Sight housing | Trägt Emitter und Batterie; hintere Kante = Socket_Sight | auf Klemmfuß (fest) | sight_mount | graphite | 26×49×8.5 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_frame` | Haubenrahmen / Sight hood frame | Hält und schützt das Glas; offener Rahmen für freie Durchsicht | auf Visiergehäuse (fest) | sight_mount | graphite | 44×12×38 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_glass` | Visierglas / Sight glass | Reflexscheibe; das Absehen erscheint auf ihr | im Rahmen (fest) | sight_mount | glass | 35×1.0×29 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_emitter` | Emitter / Reticle emitter | Leuchtfenster des Absehen-Projektors (zurückhaltend) | vorn im Emitterblock | sight_mount | energy | 7.0×2.0×2.2 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `grip` | Pistolengriff / Pistol grip | Haupthand hält die Waffe; trägt Socket_Hand | mit Unterem Gehäuse verschraubt (fest) | ASM_grip_controls | graphite | 30×68×104 | 0.000, 0.000, 0.000 | fest | nein | BGM-1 | – |
| `trigger` | Abzug / Trigger | Feuer auslösen (Zeigefinger) | Drehpunkt im Unteren Gehäuse | ASM_grip_controls | metal | 7.0×7.8×26 | 0.000, -0.045, 0.037 | dreht um Achse x durch (44.71796769724491, 37, 0) mm, 0…-12°; Ereignis fire | nein | – | fire_auto |
| `trigger_guard` | Abzugsbügel / Trigger guard | Schützt den Abzug, Fingerfreiraum ≥ 22 mm | Griff vorn und Unteres Gehäuse (fest) | ASM_grip_controls | graphite | 12×58×35 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `selector` | Feuerwahlhebel / Fire selector | Sichern / Feuer, mit dem Daumen der Haupthand | Achse quer im Unteren Gehäuse | ASM_grip_controls | accent | 3.0×20×8.0 | 0.000, -0.004, 0.066 | dreht um Achse x durch (4, 66, 0) mm, 0…90°; Ereignis safety | nein | – | – |
| `stock_joint` | Schaftverbindung / Stock joint | Verbindet Schaft und Gehäuse; Verriegelung | Steckverbindung am Gehäuseende (fest) | ASM_stock | dark_metal | 30×12×42 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `stock_spine` | Schaftrohr / Stock spine | Trägt die Schulterstütze in Linie mit dem Lauf | in der Schaftverbindung (fest) | ASM_stock | graphite | 28×91×28 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `stock` | Schulterstütze / Buttstock | Anlage an der Schulter, Wangenauflage oben | auf dem Schaftrohr (fest) | ASM_stock | shell | 36×86×106 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `butt_pad` | Schaftkappe / Butt pad | Rutschfeste Anlage an der Schulter | auf das Schaftende gesteckt (fest) | ASM_stock | graphite | 40×18×115 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `cheek_rest` | Wangenauflage / Cheek rest | Anlage für die Wange beim Zielen | auf der Schulterstütze (fest) | ASM_stock | graphite | 26×73×10 | 0.000, 0.000, 0.000 | fest | nein | – | – |

## Anker

| Anker | Position m (X, Y, Z) | Teil | Hinweis |
|---|---|---|---|
| `Socket_Hand` | 0.0000, 0.0000, 0.0000 | grip | – |
| `Socket_SupportHand` | 0.0000, -0.3400, 0.0640 | shroud_grip | – |
| `Socket_Muzzle` | 0.0000, -0.7260, 0.1060 | muzzle | – |
| `Socket_FeedCover` | 0.0000, 0.0600, 0.1620 | feed_cover | Griffpunkt zum Öffnen |
| `Socket_AmmoBox` | 0.0800, -0.0500, 0.0600 | ammo_box | – |
| `Socket_Sight` | 0.0000, 0.0390, 0.2010 | sight_body | hinteres Visierende auf der Visierlinie |
| `Socket_Reticle` | 0.0000, -0.0040, 0.2010 | sight_glass | Mitte Glas |
| `Socket_Eye` | 0.0000, 0.0020, 0.2010 | sight_frame | Vorschlag nach Formgen-Regel: hinterer Fensterrand (Reflexvisier ohne festen Augenabstand) |
| `Socket_CenterOfMass` | 0.0077, -0.0984, 0.0906 | – | abgeleitet: Volumenschwerpunkt, homogene Dichte, ohne Glas |

## Schnittstellen

| ID | Bedeutung | Regel |
|---|---|---|
| BAB-1 | Munitionskasten MG | Einhängung links am Gehäuse, Gurt nach oben zur Zuführschale |
| BGM-1 | Griffmodul Typ 1 (Gewehrfamilie) | Oberkante 42 × 30 mm, Neigung 15° (oben nach vorn), Abzugsbügel bis f = +78 mm |
| BMZ-15 | Mündungsgewinde r 15 | Laufende r 9 mm, Mündungsteil r 15 mm, Bohrung r 5 mm |
| BRI-22 | Schiene 22 mm (Oberseite Gehäuse) | Breite 22 mm, Höhe 8 mm, Klemmfuß 22 mm breit, Mindestlänge Klemmfuß 40 mm |

## Aktionen der Mechanik

| Aktion | Beschreibung | Bilder (30 fps) | Teile | Ereignisse (Bild) | Status |
|---|---|---|---|---|---|
| `fire_auto` | Dauerfeuer (Mechanik) | 24 (0.80 s) | trigger | shot (2), shot (6), shot (10), shot (14), shot (18) | Mechanik definiert, Sichtung offen; Hände offen; Dauer entworfen |
| `reload` | Deckel auf, Kasten tauschen, Gurt einlegen, Deckel zu | 150 (5.00 s) | feed_cover, ammo_box | cover_open (16), box_out (44), box_in (100), belt_seated (112), cover_closed (134) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |

Haltungen, Übergänge und Status aller Aktionen: [haltungen.md › BASIC-15](../haltungen.md#basic-15).
