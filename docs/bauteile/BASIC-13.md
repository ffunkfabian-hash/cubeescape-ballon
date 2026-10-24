<!-- erzeugt von tools/make_docs.py – nicht von Hand ändern -->

# BASIC-13 Granatwerfer (Kipplauf) – „Kipplauf“

Einschüssiger Kipplauf-Granatwerfer.

Typ `grenade_launcher` (Grenade Launcher (breech-loaded)) · Munition special · Feuerart `single_shot` · Quelle des Entwurfs: `basic/weapons/` · Spec: [`data/specs/BASIC-13.spec.json`](../../data/specs/BASIC-13.spec.json).

**Maße (gemessen, Ruhelage, Visier montiert):** Länge 642 mm · Höhe 258 mm · Breite 66 mm · 21 Bauteile · 4568 Dreiecke (mit Fasen).

Rahmen: Meter, vorn −Y, oben +Z, links +X, Ursprung `Socket_Hand`. `origin_m` ist der Objektursprung (bei beweglichen Teilen der Drehpunkt).

## Baugruppenbaum

```
BASIC-13
├─ ASM_receiver  Hauptgehäuse / Receiver
│   ├─ frame  Rahmen
│   ├─ rail  Schiene
├─ ASM_barrel  Lauf / Emitter / Barrel / emitter
│   │  └(an barrel_lug) launch_tube  Abschusslauf
│   │  └(an barrel_lug) muzzle  Mündungsring
├─ ASM_ammo  Munitionsversorgung / Ammunition feed
│   │  └(an barrel_lug) grenade  Granate
│   │  └(an grenade) grenade_band  Zünderring
├─ ASM_sight  Visier / Sight
│   ├─ sight_mount  Visier-Klemmfuß
│   │  └(an sight_mount) sight_clamp  Klemmschraube
│   │  └(an sight_mount) sight_body  Visiergehäuse
│   │  └(an sight_mount) sight_frame  Haubenrahmen
│   │  └(an sight_mount) sight_glass  Visierglas
│   │  └(an sight_mount) sight_emitter  Emitter
├─ ASM_grip_controls  Griff und Bedienung / Grip and controls
│   ├─ latch  Verriegelungshebel
│   ├─ grip  Pistolengriff
│   ├─ trigger  Abzug
│   ├─ trigger_guard  Abzugsbügel
├─ ASM_support  Stützbereich / Support
│   │  └(an barrel_lug) forend  Vorderschaft
├─ ASM_stock  Schaft / Stock
│   ├─ stock  Schulterstütze S2
│   ├─ butt_pad  Schaftkappe
├─ ASM_mechanism  Bewegliche Mechanik / Moving mechanism
│   ├─ hinge_pin  Scharnierbolzen
│   ├─ barrel_lug  Laufhaken
```

## Bauteilliste

| ID | Name (de / en) | Funktion | Befestigung | übergeordnet | Material | Maße X×Y×Z mm | Ursprung m | Bewegung | Entnahme | Schnittstelle | Aktionen |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `frame` | Rahmen / Frame | Trägt Scharnier, Abzug, Verriegelung und Visier | Grundkörper | ASM_receiver | shell | 48×184×84 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `hinge_pin` | Scharnierbolzen / Hinge pin | Drehachse des Kipplaufs | quer im Rahmen | ASM_mechanism | dark_metal | 52×14×14 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `barrel_lug` | Laufhaken / Barrel lug | Verbindet Lauf und Scharnier | am Lauf (dreht mit) | ASM_mechanism | dark_metal | 36×44×20 | 0.000, -0.074, 0.064 | dreht um Achse x durch (74, 64, 0) mm, 0…-35°; Ereignis breech | nein | – | reload |
| `launch_tube` | Abschusslauf / Launch tube | Dicker Lauf; nimmt eine Granate auf | am Laufhaken | barrel_lug | shell | 60×346×60 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `muzzle` | Mündungsring / Muzzle ring | Verstärkt die Mündung; Socket_Muzzle | auf den Lauf gepresst | barrel_lug | dark_metal | 66×28×66 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `forend` | Vorderschaft / Fore-end | Griff der Stützhand; kippt mit dem Lauf | unter den Lauf geschraubt | barrel_lug | graphite | 40×177×28 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `grenade` | Granate / Grenade | Eine Granate im Patronenlager | im Lauf (Ruhelage verdeckt) | barrel_lug | dark_metal | 40×90×40 | 0.000, -0.095, 0.104 | verschiebt 153 mm (f,u,x (-150, 30, 0)); Ereignis load | nein | – | reload |
| `grenade_band` | Zünderring / Fuse band | Kennzeichnet die Granate | auf der Granate | grenade | accent | 41×12×41 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `latch` | Verriegelungshebel / Breech latch | Entriegelt den Kipplauf (Daumen) | Drehpunkt oben im Rahmen | ASM_grip_controls | accent | 10×31×9.9 | 0.000, -0.020, 0.136 | dreht um Achse x durch (20, 136, 0) mm, 0…20°; Ereignis breech | nein | – | reload |
| `rail` | Schiene / Top rail | Aufnahme für Visiere (BRI-22) | auf Oberem Gehäuse (fest) | ASM_receiver | dark_metal | 22×120×8.5 | 0.000, 0.000, 0.000 | fest | nein | BRI-22 | – |
| `sight_mount` | Visier-Klemmfuß / Sight mount | Klemmt das Visier auf die Schiene BRI-22 | Klemmung auf Schiene (lösbar) | ASM_sight | dark_metal | 26×50×7.5 | 0.000, 0.055, 0.142 | verschiebt 70 mm (f,u,x (0, 70, 0)); Ereignis swap_sight | ja – nach Lösen der Klemmschraube senkrecht abnehmen | BRI-22 | – |
| `sight_clamp` | Klemmschraube / Clamp screw | Spannt den Klemmfuß (Werkzeuglos, Rändel) | quer im Klemmfuß links | sight_mount | dark_metal | 6.0×11×11 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_body` | Visiergehäuse / Sight housing | Trägt Emitter und Batterie; hintere Kante = Socket_Sight | auf Klemmfuß (fest) | sight_mount | graphite | 26×49×8.5 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_frame` | Haubenrahmen / Sight hood frame | Hält und schützt das Glas; offener Rahmen für freie Durchsicht | auf Visiergehäuse (fest) | sight_mount | graphite | 44×12×40 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_glass` | Visierglas / Sight glass | Reflexscheibe; das Absehen erscheint auf ihr | im Rahmen (fest) | sight_mount | glass | 35×1.0×31 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_emitter` | Emitter / Reticle emitter | Leuchtfenster des Absehen-Projektors (zurückhaltend) | vorn im Emitterblock | sight_mount | energy | 7.0×2.0×2.2 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `grip` | Pistolengriff / Pistol grip | Haupthand hält die Waffe; trägt Socket_Hand | mit Unterem Gehäuse verschraubt (fest) | ASM_grip_controls | graphite | 30×70×114 | 0.000, 0.000, 0.000 | fest | nein | BGM-1 | – |
| `trigger` | Abzug / Trigger | Feuer auslösen (Zeigefinger) | Drehpunkt im Unteren Gehäuse | ASM_grip_controls | metal | 7.0×7.8×26 | 0.000, -0.047, 0.047 | dreht um Achse x durch (47.39745962155614, 47, 0) mm, 0…-12°; Ereignis fire | nein | – | fire |
| `trigger_guard` | Abzugsbügel / Trigger guard | Schützt den Abzug, Fingerfreiraum ≥ 22 mm | Griff vorn und Unteres Gehäuse (fest) | ASM_grip_controls | graphite | 12×58×35 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `stock` | Schulterstütze S2 / Stock S2 | Einteilige Schulterstütze; Wange liegt oben auf | mit zwei Bolzen am Gehäuse (fest) | ASM_stock | graphite | 34×136×101 | 0.000, 0.000, 0.000 | fest | nein | BST-2 | – |
| `butt_pad` | Schaftkappe / Butt pad | Anlage an der Schulter | auf das Schaftende geschraubt | ASM_stock | dark_metal | 38×11×100 | 0.000, 0.000, 0.000 | fest | nein | – | – |

## Anker

| Anker | Position m (X, Y, Z) | Teil | Hinweis |
|---|---|---|---|
| `Socket_Hand` | 0.0000, 0.0000, 0.0000 | grip | – |
| `Socket_SupportHand` | 0.0000, -0.2150, 0.0660 | forend | – |
| `Socket_Muzzle` | 0.0000, -0.3980, 0.1040 | muzzle | – |
| `Socket_Breech` | 0.0000, -0.0460, 0.1040 | launch_tube | Lageröffnung bei gekipptem Lauf |
| `Socket_Sight` | 0.0000, 0.0790, 0.1740 | sight_body | hinteres Visierende auf der Visierlinie |
| `Socket_Reticle` | 0.0000, 0.0360, 0.1740 | sight_glass | Mitte Glas |
| `Socket_Eye` | 0.0000, 0.0420, 0.1740 | sight_frame | Vorschlag nach Formgen-Regel: hinterer Fensterrand (Reflexvisier ohne festen Augenabstand) |
| `Socket_CenterOfMass` | 0.0000, -0.0463, 0.0835 | – | abgeleitet: Volumenschwerpunkt, homogene Dichte, ohne Glas |

## Schnittstellen

| ID | Bedeutung | Regel |
|---|---|---|
| BGM-1 | Griffmodul Typ 1 (Gewehrfamilie) | Oberkante 42 × 30 mm, Neigung 15° (oben nach vorn), Abzugsbügel bis f = +78 mm |
| BRI-22 | Schiene 22 mm (Oberseite Gehäuse) | Breite 22 mm, Höhe 8 mm, Klemmfuß 22 mm breit, Mindestlänge Klemmfuß 40 mm |
| BST-2 | Schaft S2 | Anlage 64 mm hoch am Gehäuseende, Laufachse 24 mm unter der Oberkante |

## Aktionen der Mechanik

| Aktion | Beschreibung | Bilder (30 fps) | Teile | Ereignisse (Bild) | Status |
|---|---|---|---|---|---|
| `fire` | Einzelschuss | 12 (0.40 s) | trigger | shot (2) | Mechanik definiert, Sichtung offen; Hände offen; Dauer entworfen |
| `reload` | Kipplauf öffnen, Granate laden, schließen | 80 (2.67 s) | latch, barrel_lug, grenade | breech_open (18), case_out (24), grenade_in (48), breech_closed (66) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |

Haltungen, Übergänge und Status aller Aktionen: [haltungen.md › BASIC-13](../haltungen.md#basic-13).
