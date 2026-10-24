<!-- erzeugt von tools/make_docs.py – nicht von Hand ändern -->

# BASIC-10 Fusionsgewehr – „Glutkern“

Fusionsgewehr: Aufladen über drei Kondensatoren, Salve aus dem Schlitz-Emitter.

Typ `fusion_rifle` (Fusion Rifle) · Munition special · Feuerart `charge_burst` · Quelle des Entwurfs: `basic/weapons/` · Spec: [`data/specs/BASIC-10.spec.json`](../../data/specs/BASIC-10.spec.json).

**Maße (gemessen, Ruhelage, Visier montiert):** Länge 802 mm · Höhe 256 mm · Breite 60 mm · 24 Bauteile · 4808 Dreiecke (mit Fasen).

Rahmen: Meter, vorn −Y, oben +Z, links +X, Ursprung `Socket_Hand`. `origin_m` ist der Objektursprung (bei beweglichen Teilen der Drehpunkt).

## Baugruppenbaum

```
BASIC-10
├─ ASM_receiver  Hauptgehäuse / Receiver
│   ├─ receiver  Gehäuse
│   ├─ rail  Schiene
├─ ASM_barrel  Lauf / Emitter / Barrel / emitter
│   ├─ capacitor_housing  Kondensatorgehäuse
│   ├─ emitter  Schlitz-Emitter
│   ├─ emitter_lens  Emitterlinse
│   ├─ charge_1  Ladeanzeige 1
│   ├─ charge_2  Ladeanzeige 2
│   ├─ charge_3  Ladeanzeige 3
├─ ASM_ammo  Munitionsversorgung / Ammunition feed
│   ├─ energy_cell  Energiezelle
│   │  └(an energy_cell) energy_cell_window  Ladefenster
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
│   ├─ stock  Schulterstütze S2
│   ├─ butt_pad  Schaftkappe
├─ ASM_cooling  Kühlung / Cooling
│   ├─ coil_1  Spulenring 1
│   ├─ coil_2  Spulenring 2
│   ├─ coil_3  Spulenring 3
```

## Bauteilliste

| ID | Name (de / en) | Funktion | Befestigung | übergeordnet | Material | Maße X×Y×Z mm | Ursprung m | Bewegung | Entnahme | Schnittstelle | Aktionen |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `receiver` | Gehäuse / Receiver | Tragkörper, Steuerung und Zellenschacht | Grundkörper | ASM_receiver | shell | 50×330×92 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `capacitor_housing` | Kondensatorgehäuse / Capacitor housing | Umschließt die Kondensatoren; Griffbereich der Stützhand | am Gehäuse verschraubt, Fuge 1 mm | ASM_barrel | graphite | 52×279×74 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `emitter` | Schlitz-Emitter / Slit emitter | Formt die Salve; Socket_Muzzle | auf das Kondensatorgehäuse geschraubt | ASM_barrel | dark_metal | 60×30×44 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `emitter_lens` | Emitterlinse / Emitter lens | Leuchtet beim Aufladen auf | im Emitter | ASM_barrel | energy | 40×2.0×10 | 0.000, 0.000, 0.000 | Leuchten 0…6.0 (Ereignis charge) | nein | – | charge_fire |
| `coil_1` | Spulenring 1 / Coil ring 1 | Kondensatorspule; führt Wärme nach außen | um das Kondensatorgehäuse | ASM_cooling | dark_metal | 60×14×80 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `charge_1` | Ladeanzeige 1 / Charge pip 1 | Leuchtet bei 1/3 Ladung | eingelassen | ASM_barrel | energy | 1.0×28×8.0 | 0.000, 0.000, 0.000 | Leuchten 0…5.0 (Ereignis charge) | nein | – | charge_fire, charge_cancel |
| `coil_2` | Spulenring 2 / Coil ring 2 | Kondensatorspule; führt Wärme nach außen | um das Kondensatorgehäuse | ASM_cooling | dark_metal | 60×14×80 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `charge_2` | Ladeanzeige 2 / Charge pip 2 | Leuchtet bei 2/3 Ladung | eingelassen | ASM_barrel | energy | 1.0×28×8.0 | 0.000, 0.000, 0.000 | Leuchten 0…5.0 (Ereignis charge) | nein | – | charge_fire, charge_cancel |
| `coil_3` | Spulenring 3 / Coil ring 3 | Kondensatorspule; führt Wärme nach außen | um das Kondensatorgehäuse | ASM_cooling | dark_metal | 60×14×80 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `charge_3` | Ladeanzeige 3 / Charge pip 3 | Leuchtet bei 3/3 Ladung | eingelassen | ASM_barrel | energy | 1.0×28×8.0 | 0.000, 0.000, 0.000 | Leuchten 0…5.0 (Ereignis charge) | nein | – | charge_fire |
| `energy_cell` | Energiezelle / Energy cell | Speichert die Ladungen; austauschbar | rastet im Zellenschacht ein (lösbar) | ASM_ammo | dark_metal | 40×84×28 | 0.000, 0.082, 0.036 | verschiebt 110 mm (f,u,x (0, -110, 0)); Ereignis reload | ja – entlang Bewegung | BEC-1 | reload |
| `energy_cell_window` | Ladefenster / Charge window | Zeigt den Ladezustand | in die Zelle eingelassen | energy_cell | energy | 1.0×42×4.0 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `rail` | Schiene / Top rail | Aufnahme für Visiere (BRI-22) | auf Oberem Gehäuse (fest) | ASM_receiver | dark_metal | 22×280×8.5 | 0.000, 0.000, 0.000 | fest | nein | BRI-22 | – |
| `sight_mount` | Visier-Klemmfuß / Sight mount | Klemmt das Visier auf die Schiene BRI-22 | Klemmung auf Schiene (lösbar) | ASM_sight | dark_metal | 26×50×7.5 | 0.000, 0.005, 0.146 | verschiebt 70 mm (f,u,x (0, 70, 0)); Ereignis swap_sight | ja – nach Lösen der Klemmschraube senkrecht abnehmen | BRI-22 | – |
| `sight_clamp` | Klemmschraube / Clamp screw | Spannt den Klemmfuß (Werkzeuglos, Rändel) | quer im Klemmfuß links | sight_mount | dark_metal | 6.0×11×11 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_body` | Visiergehäuse / Sight housing | Trägt Emitter und Batterie; hintere Kante = Socket_Sight | auf Klemmfuß (fest) | sight_mount | graphite | 26×49×8.5 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_frame` | Haubenrahmen / Sight hood frame | Hält und schützt das Glas; offener Rahmen für freie Durchsicht | auf Visiergehäuse (fest) | sight_mount | graphite | 42×12×34 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_glass` | Visierglas / Sight glass | Reflexscheibe; das Absehen erscheint auf ihr | im Rahmen (fest) | sight_mount | glass | 33×1.0×25 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_emitter` | Emitter / Reticle emitter | Leuchtfenster des Absehen-Projektors (zurückhaltend) | vorn im Emitterblock | sight_mount | energy | 7.0×2.0×2.2 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `grip` | Pistolengriff / Pistol grip | Haupthand hält die Waffe; trägt Socket_Hand | mit Unterem Gehäuse verschraubt (fest) | ASM_grip_controls | graphite | 30×69×110 | 0.000, 0.000, 0.000 | fest | nein | BGM-1 | – |
| `trigger` | Abzug / Trigger | Feuer auslösen (Zeigefinger) | Drehpunkt im Unteren Gehäuse | ASM_grip_controls | metal | 7.0×7.8×26 | 0.000, -0.046, 0.043 | dreht um Achse x durch (46.325662851831645, 43, 0) mm, 0…-12°; Ereignis fire | nein | – | charge_fire, charge_cancel |
| `trigger_guard` | Abzugsbügel / Trigger guard | Schützt den Abzug, Fingerfreiraum ≥ 22 mm | Griff vorn und Unteres Gehäuse (fest) | ASM_grip_controls | graphite | 12×58×35 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `stock` | Schulterstütze S2 / Stock S2 | Einteilige Schulterstütze; Wange liegt oben auf | mit zwei Bolzen am Gehäuse (fest) | ASM_stock | graphite | 34×152×101 | 0.000, 0.000, 0.000 | fest | nein | BST-2 | – |
| `butt_pad` | Schaftkappe / Butt pad | Anlage an der Schulter | auf das Schaftende geschraubt | ASM_stock | dark_metal | 38×12×100 | 0.000, 0.000, 0.000 | fest | nein | – | – |

## Anker

| Anker | Position m (X, Y, Z) | Teil | Hinweis |
|---|---|---|---|
| `Socket_Hand` | 0.0000, 0.0000, 0.0000 | grip | – |
| `Socket_SupportHand` | 0.0000, -0.3450, 0.0800 | capacitor_housing | – |
| `Socket_Muzzle` | 0.0000, -0.5000, 0.1000 | emitter | – |
| `Socket_Cell` | 0.0000, 0.0820, 0.0360 | energy_cell | – |
| `Socket_Sight` | 0.0000, 0.0290, 0.1750 | sight_body | hinteres Visierende auf der Visierlinie |
| `Socket_Reticle` | 0.0000, -0.0140, 0.1750 | sight_glass | Mitte Glas |
| `Socket_Eye` | 0.0000, -0.0080, 0.1750 | sight_frame | Vorschlag nach Formgen-Regel: hinterer Fensterrand (Reflexvisier ohne festen Augenabstand) |
| `Socket_CenterOfMass` | 0.0000, -0.1146, 0.0912 | – | abgeleitet: Volumenschwerpunkt, homogene Dichte, ohne Glas |

## Schnittstellen

| ID | Bedeutung | Regel |
|---|---|---|
| BEC-1 | Energiezelle Typ 1 | Zellenschacht je Waffe; Maß im Spec |
| BGM-1 | Griffmodul Typ 1 (Gewehrfamilie) | Oberkante 42 × 30 mm, Neigung 15° (oben nach vorn), Abzugsbügel bis f = +78 mm |
| BRI-22 | Schiene 22 mm (Oberseite Gehäuse) | Breite 22 mm, Höhe 8 mm, Klemmfuß 22 mm breit, Mindestlänge Klemmfuß 40 mm |
| BST-2 | Schaft S2 | Anlage 64 mm hoch am Gehäuseende, Laufachse 24 mm unter der Oberkante |

## Aktionen der Mechanik

| Aktion | Beschreibung | Bilder (30 fps) | Teile | Ereignisse (Bild) | Status |
|---|---|---|---|---|---|
| `charge_fire` | Aufladen und Salve | 40 (1.33 s) | trigger, charge_1, charge_2, charge_3, emitter_lens | charge_start (2), charged (26), burst (27), ready (40) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |
| `charge_cancel` | Aufladen abbrechen | 24 (0.80 s) | trigger, charge_1, charge_2 | cancel (12) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |
| `reload` | Energiezelle wechseln | 70 (2.33 s) | energy_cell | cell_out (16), cell_in (50), ready (58) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |

Haltungen, Übergänge und Status aller Aktionen: [haltungen.md › BASIC-10](../haltungen.md#basic-10).
