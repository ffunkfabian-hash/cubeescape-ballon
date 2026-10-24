<!-- erzeugt von tools/make_docs.py – nicht von Hand ändern -->

# BASIC-14 Raketenwerfer – „Schulterrohr“

Einschüssiges Schulterrohr mit Heckladung.

Typ `rocket_launcher` (Rocket Launcher) · Munition heavy · Feuerart `single_shot` · Quelle des Entwurfs: `basic/weapons/` · Spec: [`data/specs/BASIC-14.spec.json`](../../data/specs/BASIC-14.spec.json).

**Maße (gemessen, Ruhelage, Visier montiert):** Länge 946 mm · Höhe 294 mm · Breite 110 mm · 21 Bauteile · 5532 Dreiecke (mit Fasen).

Rahmen: Meter, vorn −Y, oben +Z, links +X, Ursprung `Socket_Hand`. `origin_m` ist der Objektursprung (bei beweglichen Teilen der Drehpunkt).

## Baugruppenbaum

```
BASIC-14
├─ ASM_receiver  Hauptgehäuse / Receiver
│   ├─ tube  Abschussrohr
│   ├─ ready_light  Bereitschaftsanzeige
│   ├─ rail  Schiene
├─ ASM_barrel  Lauf / Emitter / Barrel / emitter
│   ├─ muzzle  Mündungsring
│   ├─ rear_ring  Heckring
├─ ASM_ammo  Munitionsversorgung / Ammunition feed
│   ├─ rocket  Rakete
│   │  └(an rocket) rocket_nose  Raketenspitze
├─ ASM_sight  Visier / Sight
│   ├─ sight_riser  Visiersockel
│   ├─ sight_mount  Visier-Klemmfuß
│   │  └(an sight_mount) sight_clamp  Klemmschraube
│   │  └(an sight_mount) sight_body  Visiergehäuse
│   │  └(an sight_mount) sight_frame  Haubenrahmen
│   │  └(an sight_mount) sight_glass  Visierglas
│   │  └(an sight_mount) sight_emitter  Emitter
├─ ASM_grip_controls  Griff und Bedienung / Grip and controls
│   ├─ trigger_housing  Abzugsgehäuse
│   ├─ grip  Pistolengriff
│   ├─ trigger  Abzug
│   ├─ trigger_guard  Abzugsbügel
├─ ASM_support  Stützbereich / Support
│   ├─ foregrip  Vordergriff
├─ ASM_stock  Schaft / Stock
│   ├─ shoulder_rest  Schulterauflage
├─ ASM_mechanism  Bewegliche Mechanik / Moving mechanism
│   ├─ breech_cap  Heckverschluss
```

## Bauteilliste

| ID | Name (de / en) | Funktion | Befestigung | übergeordnet | Material | Maße X×Y×Z mm | Ursprung m | Bewegung | Entnahme | Schnittstelle | Aktionen |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `tube` | Abschussrohr / Launch tube | Hauptkörper; führt die Rakete | Grundkörper | ASM_receiver | shell | 100×890×100 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `muzzle` | Mündungsring / Muzzle ring | Mündung; Socket_Muzzle | auf das Rohr gepresst | ASM_barrel | dark_metal | 110×50×110 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `rear_ring` | Heckring / Rear ring | Trägt das Scharnier des Heckverschlusses | auf das Rohr gepresst | ASM_barrel | dark_metal | 110×40×110 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `breech_cap` | Heckverschluss / Breech cap | Verschließt das Heck; klappt zum Laden auf | Scharnier links am Heckring | ASM_mechanism | graphite | 106×16×106 | 0.054, 0.348, 0.112 | dreht um Achse u durch (-348, 112, 54) mm, 0…-105°; Ereignis reload | nein | – | reload |
| `rocket` | Rakete / Rocket | Eine Rakete im Rohr (Ruhelage verdeckt) | im Rohr | ASM_ammo | dark_metal | 71×710×71 | 0.000, -0.060, 0.112 | verschiebt 880 mm (f,u,x (-880, 0, 0)); Ereignis load | nein | – | reload |
| `rocket_nose` | Raketenspitze / Rocket nose | Gefechtskopf | an der Rakete | rocket | accent | 70×62×70 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `shoulder_rest` | Schulterauflage / Shoulder rest | Liegt auf der Schulter | unter das Rohr geschraubt | ASM_stock | graphite | 56×166×20 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `trigger_housing` | Abzugsgehäuse / Trigger housing | Verbindet Griffmodul und Rohr | unter das Rohr geschraubt | ASM_grip_controls | graphite | 36×130×26 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `foregrip` | Vordergriff / Foregrip | Griff der Stützhand | unter das Rohr geschraubt | ASM_support | graphite | 30×40×74 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_riser` | Visiersockel / Sight riser | Hebt das Visier über das Rohr | auf dem Rohr verschraubt | ASM_sight | shell | 30×180×12 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `ready_light` | Bereitschaftsanzeige / Ready light | Leuchtet, wenn eine Rakete geladen ist | eingelassen | ASM_receiver | energy | 1.0×40×12 | 0.000, 0.000, 0.000 | Leuchten 0…5.0 (Ereignis charge) | nein | – | fire, reload |
| `rail` | Schiene / Top rail | Aufnahme für Visiere (BRI-22) | auf Oberem Gehäuse (fest) | ASM_receiver | dark_metal | 22×160×8.5 | 0.000, 0.000, 0.000 | fest | nein | BRI-22 | – |
| `sight_mount` | Visier-Klemmfuß / Sight mount | Klemmt das Visier auf die Schiene BRI-22 | Klemmung auf Schiene (lösbar) | ASM_sight | dark_metal | 26×50×7.5 | 0.000, 0.045, 0.178 | verschiebt 70 mm (f,u,x (0, 70, 0)); Ereignis swap_sight | ja – nach Lösen der Klemmschraube senkrecht abnehmen | BRI-22 | – |
| `sight_clamp` | Klemmschraube / Clamp screw | Spannt den Klemmfuß (Werkzeuglos, Rändel) | quer im Klemmfuß links | sight_mount | dark_metal | 6.0×11×11 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_body` | Visiergehäuse / Sight housing | Trägt Emitter und Batterie; hintere Kante = Socket_Sight | auf Klemmfuß (fest) | sight_mount | graphite | 26×49×8.5 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_frame` | Haubenrahmen / Sight hood frame | Hält und schützt das Glas; offener Rahmen für freie Durchsicht | auf Visiergehäuse (fest) | sight_mount | graphite | 54×12×40 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_glass` | Visierglas / Sight glass | Reflexscheibe; das Absehen erscheint auf ihr | im Rahmen (fest) | sight_mount | glass | 45×1.0×31 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_emitter` | Emitter / Reticle emitter | Leuchtfenster des Absehen-Projektors (zurückhaltend) | vorn im Emitterblock | sight_mount | energy | 7.0×2.0×2.2 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `grip` | Pistolengriff / Pistol grip | Haupthand hält die Waffe; trägt Socket_Hand | mit Unterem Gehäuse verschraubt (fest) | ASM_grip_controls | graphite | 30×69×108 | 0.000, 0.000, 0.000 | fest | nein | BGM-1 | – |
| `trigger` | Abzug / Trigger | Feuer auslösen (Zeigefinger) | Drehpunkt im Unteren Gehäuse | ASM_grip_controls | metal | 7.0×7.8×26 | 0.000, -0.046, 0.041 | dreht um Achse x durch (45.7897644669694, 41, 0) mm, 0…-12°; Ereignis fire | nein | – | fire |
| `trigger_guard` | Abzugsbügel / Trigger guard | Schützt den Abzug, Fingerfreiraum ≥ 22 mm | Griff vorn und Unteres Gehäuse (fest) | ASM_grip_controls | graphite | 12×58×35 | 0.000, 0.000, 0.000 | fest | nein | – | – |

## Anker

| Anker | Position m (X, Y, Z) | Teil | Hinweis |
|---|---|---|---|
| `Socket_Hand` | 0.0000, 0.0000, 0.0000 | grip | – |
| `Socket_SupportHand` | 0.0000, -0.2300, 0.0300 | foregrip | – |
| `Socket_Muzzle` | 0.0000, -0.5900, 0.1120 | muzzle | – |
| `Socket_Breech` | 0.0000, 0.3560, 0.1120 | breech_cap | Ladeöffnung hinten |
| `Socket_Sight` | 0.0000, 0.0690, 0.2100 | sight_body | hinteres Visierende auf der Visierlinie |
| `Socket_Reticle` | 0.0000, 0.0260, 0.2100 | sight_glass | Mitte Glas |
| `Socket_Eye` | 0.0000, 0.0320, 0.2100 | sight_frame | Vorschlag nach Formgen-Regel: hinterer Fensterrand (Reflexvisier ohne festen Augenabstand) |
| `Socket_CenterOfMass` | 0.0000, -0.0797, 0.1070 | – | abgeleitet: Volumenschwerpunkt, homogene Dichte, ohne Glas |

## Schnittstellen

| ID | Bedeutung | Regel |
|---|---|---|
| BGM-1 | Griffmodul Typ 1 (Gewehrfamilie) | Oberkante 42 × 30 mm, Neigung 15° (oben nach vorn), Abzugsbügel bis f = +78 mm |
| BRI-22 | Schiene 22 mm (Oberseite Gehäuse) | Breite 22 mm, Höhe 8 mm, Klemmfuß 22 mm breit, Mindestlänge Klemmfuß 40 mm |

## Aktionen der Mechanik

| Aktion | Beschreibung | Bilder (30 fps) | Teile | Ereignisse (Bild) | Status |
|---|---|---|---|---|---|
| `fire` | Abschuss | 12 (0.40 s) | trigger, ready_light | launch (2) | Mechanik definiert, Sichtung offen; Hände offen; Dauer entworfen |
| `reload` | Heck öffnen, Rakete einschieben, schließen | 96 (3.20 s) | breech_cap, rocket, ready_light | breech_open (14), rocket_in (60), breech_closed (82), ready (86) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |

Haltungen, Übergänge und Status aller Aktionen: [haltungen.md › BASIC-14](../haltungen.md#basic-14).
