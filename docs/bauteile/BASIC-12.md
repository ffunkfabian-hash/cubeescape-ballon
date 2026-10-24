<!-- erzeugt von tools/make_docs.py – nicht von Hand ändern -->

# BASIC-12 Spurgewehr – „Leitstrahl“

Strahlwaffe mit Fokusrohr, seitlicher Energiezelle und Holo-Visier.

Typ `trace_rifle` (Trace Rifle) · Munition special · Feuerart `continuous_beam` · Quelle des Entwurfs: `basic/weapons/` · Spec: [`data/specs/BASIC-12.spec.json`](../../data/specs/BASIC-12.spec.json).

**Maße (gemessen, Ruhelage, Visier montiert):** Länge 871 mm · Höhe 252 mm · Breite 60 mm · 22 Bauteile · 3948 Dreiecke (mit Fasen).

Rahmen: Meter, vorn −Y, oben +Z, links +X, Ursprung `Socket_Hand`. `origin_m` ist der Objektursprung (bei beweglichen Teilen der Drehpunkt).

## Baugruppenbaum

```
BASIC-12
├─ ASM_receiver  Hauptgehäuse / Receiver
│   ├─ receiver  Gehäuse
│   ├─ rail  Schiene
├─ ASM_barrel  Lauf / Emitter / Barrel / emitter
│   ├─ focus_cone  Fokuskegel
│   ├─ focus_lens  Fokuslinse
│   ├─ focus_ring_1  Fokusring 1
│   ├─ focus_ring_2  Fokusring 2
│   ├─ focus_ring_3  Fokusring 3
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
├─ ASM_support  Stützbereich / Support
│   ├─ focus_tube  Fokusrohr
├─ ASM_stock  Schaft / Stock
│   ├─ rear_body  Hinterkörper
│   ├─ butt_pad  Schaftkappe
│   ├─ cheek_pad  Wangenpolster
```

## Bauteilliste

| ID | Name (de / en) | Funktion | Befestigung | übergeordnet | Material | Maße X×Y×Z mm | Ursprung m | Bewegung | Entnahme | Schnittstelle | Aktionen |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `receiver` | Gehäuse / Receiver | Tragkörper, Zellenschacht links | Grundkörper | ASM_receiver | shell | 46×320×84 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `focus_tube` | Fokusrohr / Focus tube | Umschließt den Strahlkanal; Griffbereich der Stützhand | am Gehäuse verschraubt | ASM_support | graphite | 44×322×44 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `focus_cone` | Fokuskegel / Focus cone | Verjüngt den Strahl; Socket_Muzzle | auf das Fokusrohr gesteckt | ASM_barrel | dark_metal | 47×62×47 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `focus_lens` | Fokuslinse / Focus lens | Leuchtet bei aktivem Strahl | in der Kegelspitze | ASM_barrel | energy | 16×6.0×16 | 0.000, 0.000, 0.000 | Leuchten 0…6.0 (Ereignis beam) | nein | – | beam |
| `focus_ring_1` | Fokusring 1 / Focus ring 1 | Hält die Fokusspule; gliedert das Rohr | auf das Fokusrohr gepresst | ASM_barrel | dark_metal | 50×10×50 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `focus_ring_2` | Fokusring 2 / Focus ring 2 | Hält die Fokusspule; gliedert das Rohr | auf das Fokusrohr gepresst | ASM_barrel | dark_metal | 50×10×50 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `focus_ring_3` | Fokusring 3 / Focus ring 3 | Hält die Fokusspule; gliedert das Rohr | auf das Fokusrohr gepresst | ASM_barrel | dark_metal | 50×10×50 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `energy_cell` | Energiezelle / Energy cell | Speichert die Ladungen; austauschbar | rastet im Zellenschacht ein (lösbar) | ASM_ammo | dark_metal | 12×120×42 | 0.028, -0.090, 0.093 | verschiebt 70 mm (f,u,x (0, 0, 70)); Ereignis reload | ja – entlang Bewegung | BEC-1 | reload |
| `energy_cell_window` | Ladefenster / Charge window | Zeigt den Ladezustand | in die Zelle eingelassen | energy_cell | energy | 1.0×60×4.0 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `rail` | Schiene / Top rail | Aufnahme für Visiere (BRI-22) | auf Oberem Gehäuse (fest) | ASM_receiver | dark_metal | 22×270×8.5 | 0.000, 0.000, 0.000 | fest | nein | BRI-22 | – |
| `sight_mount` | Visier-Klemmfuß / Sight mount | Klemmt das Visier auf die Schiene BRI-22 | Klemmung auf Schiene (lösbar) | ASM_sight | dark_metal | 26×50×7.5 | 0.000, -0.005, 0.140 | verschiebt 70 mm (f,u,x (0, 70, 0)); Ereignis swap_sight | ja – nach Lösen der Klemmschraube senkrecht abnehmen | BRI-22 | – |
| `sight_clamp` | Klemmschraube / Clamp screw | Spannt den Klemmfuß (Werkzeuglos, Rändel) | quer im Klemmfuß links | sight_mount | dark_metal | 6.0×11×11 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_body` | Visiergehäuse / Sight housing | Trägt Emitter und Batterie; hintere Kante = Socket_Sight | auf Klemmfuß (fest) | sight_mount | graphite | 26×49×8.5 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_frame` | Haubenrahmen / Sight hood frame | Hält und schützt das Glas; offener Rahmen für freie Durchsicht | auf Visiergehäuse (fest) | sight_mount | graphite | 46×12×36 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_glass` | Visierglas / Sight glass | Reflexscheibe; das Absehen erscheint auf ihr | im Rahmen (fest) | sight_mount | glass | 37×1.0×27 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_emitter` | Emitter / Reticle emitter | Leuchtfenster des Absehen-Projektors (zurückhaltend) | vorn im Emitterblock | sight_mount | energy | 7.0×2.0×2.2 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `grip` | Pistolengriff / Pistol grip | Haupthand hält die Waffe; trägt Socket_Hand | mit Unterem Gehäuse verschraubt (fest) | ASM_grip_controls | graphite | 30×70×112 | 0.000, 0.000, 0.000 | fest | nein | BGM-1 | – |
| `trigger` | Abzug / Trigger | Feuer auslösen (Zeigefinger) | Drehpunkt im Unteren Gehäuse | ASM_grip_controls | metal | 7.0×7.8×26 | 0.000, -0.047, 0.045 | dreht um Achse x durch (46.86156123669389, 45, 0) mm, 0…-12°; Ereignis fire | nein | – | beam |
| `trigger_guard` | Abzugsbügel / Trigger guard | Schützt den Abzug, Fingerfreiraum ≥ 22 mm | Griff vorn und Unteres Gehäuse (fest) | ASM_grip_controls | graphite | 12×58×35 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `rear_body` | Hinterkörper / Rear body | Einteilige Fortsetzung des Gehäuses bis zur Schulter | mit dem Gehäuse verschraubt, Fuge 1 mm | ASM_stock | shell | 40×153×105 | 0.000, 0.000, 0.000 | fest | nein | BST-T | – |
| `butt_pad` | Schaftkappe / Butt pad | Anlage an der Schulter | auf das Körperende gesteckt | ASM_stock | graphite | 42×16×109 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `cheek_pad` | Wangenpolster / Cheek pad | Anlage für die Wange beim Zielen | auf dem Hinterkörper | ASM_stock | graphite | 26×90×9.0 | 0.000, 0.000, 0.000 | fest | nein | – | – |

## Anker

| Anker | Position m (X, Y, Z) | Teil | Hinweis |
|---|---|---|---|
| `Socket_Hand` | 0.0000, 0.0000, 0.0000 | grip | – |
| `Socket_SupportHand` | 0.0000, -0.3200, 0.0900 | focus_tube | Stützhand umgreift das Fokusrohr |
| `Socket_Muzzle` | 0.0000, -0.5820, 0.0960 | focus_lens | – |
| `Socket_Cell` | 0.0340, -0.0900, 0.0930 | energy_cell | Zelle links seitlich |
| `Socket_Sight` | 0.0000, 0.0190, 0.1700 | sight_body | hinteres Visierende auf der Visierlinie |
| `Socket_Reticle` | 0.0000, -0.0240, 0.1700 | sight_glass | Mitte Glas |
| `Socket_Eye` | 0.0000, -0.0180, 0.1700 | sight_frame | Vorschlag nach Formgen-Regel: hinterer Fensterrand (Reflexvisier ohne festen Augenabstand) |
| `Socket_CenterOfMass` | 0.0006, -0.0582, 0.0870 | – | abgeleitet: Volumenschwerpunkt, homogene Dichte, ohne Glas |

## Schnittstellen

| ID | Bedeutung | Regel |
|---|---|---|
| BEC-1 | Energiezelle Typ 1 | Zellenschacht je Waffe; Maß im Spec |
| BGM-1 | Griffmodul Typ 1 (Gewehrfamilie) | Oberkante 42 × 30 mm, Neigung 15° (oben nach vorn), Abzugsbügel bis f = +78 mm |
| BRI-22 | Schiene 22 mm (Oberseite Gehäuse) | Breite 22 mm, Höhe 8 mm, Klemmfuß 22 mm breit, Mindestlänge Klemmfuß 40 mm |
| BST-T | Einteilkörper Spurgewehr | Hinterkörper bündig am Gehäuse, Fuge 1 mm |

## Aktionen der Mechanik

| Aktion | Beschreibung | Bilder (30 fps) | Teile | Ereignisse (Bild) | Status |
|---|---|---|---|---|---|
| `beam` | Strahl halten und loslassen | 36 (1.20 s) | trigger, focus_lens | beam_start (4), beam_end (28) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |
| `reload` | Energiezelle seitlich wechseln | 70 (2.33 s) | energy_cell | cell_out (16), cell_in (50), ready (58) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |

Haltungen, Übergänge und Status aller Aktionen: [haltungen.md › BASIC-12](../haltungen.md#basic-12).
