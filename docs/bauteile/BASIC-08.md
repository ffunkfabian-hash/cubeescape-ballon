<!-- erzeugt von tools/make_docs.py – nicht von Hand ändern -->

# BASIC-08 Schrotflinte – „Streuer“

Vorderschaftrepetierflinte mit Röhrenmagazin, Streuschrot.

Typ `shotgun` (Shotgun) · Munition special · Feuerart `pump_action` · Quelle des Entwurfs: `basic/weapons/` · Spec: [`data/specs/BASIC-08.spec.json`](../../data/specs/BASIC-08.spec.json).

**Maße (gemessen, Ruhelage, Visier montiert):** Länge 882 mm · Höhe 244 mm · Breite 46 mm · 25 Bauteile · 4264 Dreiecke (mit Fasen).

Rahmen: Meter, vorn −Y, oben +Z, links +X, Ursprung `Socket_Hand`. `origin_m` ist der Objektursprung (bei beweglichen Teilen der Drehpunkt).

## Baugruppenbaum

```
BASIC-08
├─ ASM_receiver  Hauptgehäuse / Receiver
│   ├─ receiver  Gehäuse
│   ├─ rail  Schiene
├─ ASM_barrel  Lauf / Emitter / Barrel / emitter
│   ├─ barrel  Lauf
│   ├─ muzzle  Mündung
│   ├─ barrel_clamp  Laufschelle
├─ ASM_ammo  Munitionsversorgung / Ammunition feed
│   ├─ loading_gate  Ladeklappe
│   ├─ tube_mag  Röhrenmagazin
│   ├─ tube_cap  Magazinkappe
│   ├─ shell_round  Patrone
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
├─ ASM_stock  Schaft / Stock
│   ├─ stock_joint  Schaftverbindung
│   ├─ stock_spine  Schaftrohr
│   ├─ stock  Schulterstütze
│   ├─ butt_pad  Schaftkappe
│   ├─ cheek_rest  Wangenauflage
├─ ASM_mechanism  Bewegliche Mechanik / Moving mechanism
│   ├─ ejection_port  Auswurffenster
│   ├─ pump  Vorderschaft (Pumpe)
```

## Bauteilliste

| ID | Name (de / en) | Funktion | Befestigung | übergeordnet | Material | Maße X×Y×Z mm | Ursprung m | Bewegung | Entnahme | Schnittstelle | Aktionen |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `receiver` | Gehäuse / Receiver | Verschluss, Zuführung und Ladeklappe | Grundkörper | ASM_receiver | shell | 46×240×76 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `loading_gate` | Ladeklappe / Loading gate | Öffnung unten zum Einschieben einzelner Patronen | im Gehäuseboden (federnd) | ASM_ammo | dark_metal | 26×58×5.0 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `ejection_port` | Auswurffenster / Ejection port | Hülsenauswurf rechts | im Gehäuse eingelassen | ASM_mechanism | dark_metal | 1.4×70×24 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `barrel` | Lauf / Barrel | Dicker Glattlauf für Streuschrot | im Gehäuse verschraubt | ASM_barrel | metal | 28×428×28 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `muzzle` | Mündung / Muzzle | Weite Mündung; Socket_Muzzle | Laufende | ASM_barrel | dark_metal | 35×36×35 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `tube_mag` | Röhrenmagazin / Tube magazine | Hält sechs Patronen unter dem Lauf | unter dem Lauf, Laufschelle vorn | ASM_ammo | dark_metal | 22×382×22 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `tube_cap` | Magazinkappe / Magazine cap | Verschließt das Röhrenmagazin | aufgeschraubt | ASM_ammo | graphite | 24×18×24 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `barrel_clamp` | Laufschelle / Barrel clamp | Verbindet Lauf und Magazinrohr | auf Lauf und Rohr geklemmt | ASM_barrel | dark_metal | 22×18×58 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `pump` | Vorderschaft (Pumpe) / Pump fore-end | Stützhand repetiert: zurück und vor | gleitet auf dem Magazinrohr | ASM_mechanism | graphite | 40×166×42 | 0.000, -0.296, 0.066 | verschiebt 84 mm (f,u,x (-84, 0, 0)); Ereignis pump | nein | – | fire_pump |
| `shell_round` | Patrone / Shell | Einzelne Schrotpatrone (beim Laden sichtbar) | wird durch die Ladeklappe ins Rohr geschoben | ASM_ammo | accent | 19×60×19 | 0.000, -0.100, 0.064 | verschiebt 76 mm (f,u,x (-30, -70, 0)); Ereignis load_shell | nein | – | load_shell |
| `rail` | Schiene / Top rail | Aufnahme für Visiere (BRI-22) | auf Oberem Gehäuse (fest) | ASM_receiver | dark_metal | 22×200×8.5 | 0.000, 0.000, 0.000 | fest | nein | BRI-22 | – |
| `sight_mount` | Visier-Klemmfuß / Sight mount | Klemmt das Visier auf die Schiene BRI-22 | Klemmung auf Schiene (lösbar) | ASM_sight | dark_metal | 26×50×7.5 | 0.000, 0.005, 0.134 | verschiebt 70 mm (f,u,x (0, 70, 0)); Ereignis swap_sight | ja – nach Lösen der Klemmschraube senkrecht abnehmen | BRI-22 | – |
| `sight_clamp` | Klemmschraube / Clamp screw | Spannt den Klemmfuß (Werkzeuglos, Rändel) | quer im Klemmfuß links | sight_mount | dark_metal | 6.0×11×11 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_body` | Visiergehäuse / Sight housing | Trägt Emitter und Batterie; hintere Kante = Socket_Sight | auf Klemmfuß (fest) | sight_mount | graphite | 26×49×8.5 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_frame` | Haubenrahmen / Sight hood frame | Hält und schützt das Glas; offener Rahmen für freie Durchsicht | auf Visiergehäuse (fest) | sight_mount | graphite | 40×12×34 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_glass` | Visierglas / Sight glass | Reflexscheibe; das Absehen erscheint auf ihr | im Rahmen (fest) | sight_mount | glass | 31×1.0×25 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_emitter` | Emitter / Reticle emitter | Leuchtfenster des Absehen-Projektors (zurückhaltend) | vorn im Emitterblock | sight_mount | energy | 7.0×2.0×2.2 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `grip` | Pistolengriff / Pistol grip | Haupthand hält die Waffe; trägt Socket_Hand | mit Unterem Gehäuse verschraubt (fest) | ASM_grip_controls | graphite | 30×70×112 | 0.000, 0.000, 0.000 | fest | nein | BGM-1 | – |
| `trigger` | Abzug / Trigger | Feuer auslösen (Zeigefinger) | Drehpunkt im Unteren Gehäuse | ASM_grip_controls | metal | 7.0×7.8×26 | 0.000, -0.047, 0.045 | dreht um Achse x durch (46.86156123669389, 45, 0) mm, 0…-12°; Ereignis fire | nein | – | fire_pump |
| `trigger_guard` | Abzugsbügel / Trigger guard | Schützt den Abzug, Fingerfreiraum ≥ 22 mm | Griff vorn und Unteres Gehäuse (fest) | ASM_grip_controls | graphite | 12×58×35 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `stock_joint` | Schaftverbindung / Stock joint | Verbindet Schaft und Gehäuse; Verriegelung | Steckverbindung am Gehäuseende (fest) | ASM_stock | dark_metal | 30×12×42 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `stock_spine` | Schaftrohr / Stock spine | Trägt die Schulterstütze in Linie mit dem Lauf | in der Schaftverbindung (fest) | ASM_stock | graphite | 28×87×28 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `stock` | Schulterstütze / Buttstock | Anlage an der Schulter, Wangenauflage oben | auf dem Schaftrohr (fest) | ASM_stock | shell | 36×82×106 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `butt_pad` | Schaftkappe / Butt pad | Rutschfeste Anlage an der Schulter | auf das Schaftende gesteckt (fest) | ASM_stock | graphite | 40×17×115 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `cheek_rest` | Wangenauflage / Cheek rest | Anlage für die Wange beim Zielen | auf der Schulterstütze (fest) | ASM_stock | graphite | 26×69×10 | 0.000, 0.000, 0.000 | fest | nein | – | – |

## Anker

| Anker | Position m (X, Y, Z) | Teil | Hinweis |
|---|---|---|---|
| `Socket_Hand` | 0.0000, 0.0000, 0.0000 | grip | – |
| `Socket_SupportHand` | 0.0000, -0.2960, 0.0700 | pump | bewegt sich mit der Pumpe |
| `Socket_Muzzle` | 0.0000, -0.5840, 0.1000 | muzzle | – |
| `Socket_LoadingGate` | 0.0000, -0.0930, 0.0480 | loading_gate | Patronen einzeln von unten |
| `Socket_Sight` | 0.0000, 0.0290, 0.1630 | sight_body | hinteres Visierende auf der Visierlinie |
| `Socket_Reticle` | 0.0000, -0.0140, 0.1630 | sight_glass | Mitte Glas |
| `Socket_Eye` | 0.0000, -0.0080, 0.1630 | sight_frame | Vorschlag nach Formgen-Regel: hinterer Fensterrand (Reflexvisier ohne festen Augenabstand) |
| `Socket_CenterOfMass` | -0.0000, -0.0789, 0.0809 | – | abgeleitet: Volumenschwerpunkt, homogene Dichte, ohne Glas |

## Schnittstellen

| ID | Bedeutung | Regel |
|---|---|---|
| BGM-1 | Griffmodul Typ 1 (Gewehrfamilie) | Oberkante 42 × 30 mm, Neigung 15° (oben nach vorn), Abzugsbügel bis f = +78 mm |
| BRI-22 | Schiene 22 mm (Oberseite Gehäuse) | Breite 22 mm, Höhe 8 mm, Klemmfuß 22 mm breit, Mindestlänge Klemmfuß 40 mm |

## Aktionen der Mechanik

| Aktion | Beschreibung | Bilder (30 fps) | Teile | Ereignisse (Bild) | Status |
|---|---|---|---|---|---|
| `fire_pump` | Schuss und Repetieren | 30 (1.00 s) | trigger, pump | shot (2), eject (14), ready (22) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |
| `load_shell` | Eine Patrone laden (wiederholt je Patrone) | 24 (0.80 s) | shell_round | shell_in (18) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |

Haltungen, Übergänge und Status aller Aktionen: [haltungen.md › BASIC-08](../haltungen.md#basic-08).
