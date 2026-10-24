<!-- erzeugt von tools/make_docs.py – nicht von Hand ändern -->

# BASIC-04 Handfeuerwaffe – „Trommel“

Revolver mit sechs Kammern, ausschwenkbarer Trommel und Kimme/Korn.

Typ `hand_cannon` (Hand Cannon) · Munition primary · Feuerart `semi_auto_double_action` · Quelle des Entwurfs: `basic/weapons/` · Spec: [`data/specs/BASIC-04.spec.json`](../../data/specs/BASIC-04.spec.json).

**Maße (gemessen, Ruhelage, Visier montiert):** Länge 298 mm · Höhe 168 mm · Breite 42 mm · 17 Bauteile · 2684 Dreiecke (mit Fasen).

Rahmen: Meter, vorn −Y, oben +Z, links +X, Ursprung `Socket_Hand`. `origin_m` ist der Objektursprung (bei beweglichen Teilen der Drehpunkt).

## Baugruppenbaum

```
BASIC-04
├─ ASM_receiver  Hauptgehäuse / Receiver
│   ├─ frame_rear  Rahmen hinten
│   ├─ top_strap  Oberbrücke
│   ├─ frame_front  Laufaufnahme
├─ ASM_barrel  Lauf / Emitter / Barrel / emitter
│   ├─ barrel  Lauf
│   ├─ barrel_rib  Laufschiene
│   ├─ underlug  Unterlauf
│   ├─ muzzle  Mündung
├─ ASM_ammo  Munitionsversorgung / Ammunition feed
│   │  └(an crane) cylinder  Trommel
├─ ASM_sight  Visier / Sight
│   ├─ rear_sight_l  Kimme links
│   ├─ rear_sight_r  Kimme rechts
│   ├─ front_sight  Korn
├─ ASM_grip_controls  Griff und Bedienung / Grip and controls
│   ├─ grip  Griff
│   ├─ trigger  Abzug
│   ├─ trigger_guard  Abzugsbügel
│   ├─ cylinder_latch  Trommelriegel
├─ ASM_mechanism  Bewegliche Mechanik / Moving mechanism
│   ├─ crane  Kran
│   ├─ hammer  Hahn
```

## Bauteilliste

| ID | Name (de / en) | Funktion | Befestigung | übergeordnet | Material | Maße X×Y×Z mm | Ursprung m | Bewegung | Entnahme | Schnittstelle | Aktionen |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `frame_rear` | Rahmen hinten / Rear frame | Nimmt Hahn, Abzug und Griff auf | Grundkörper | ASM_receiver | shell | 30×52×62 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `top_strap` | Oberbrücke / Top strap | Verbindet Rahmen und Laufaufnahme über der Trommel | mit dem Rahmen verbunden | ASM_receiver | shell | 22×70×10 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `frame_front` | Laufaufnahme / Barrel lug | Hält den Lauf und den Kran | mit dem Rahmen verbunden | ASM_receiver | shell | 30×16×66 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `crane` | Kran / Crane | Trägt die Trommel; schwenkt nach links aus | Scharnier an der linken unteren Rahmenkante | ASM_mechanism | dark_metal | 7.7×68×7.7 | 0.017, -0.048, 0.026 | dreht um Achse f durch (48, 26, 17) mm, 0…-90°; Ereignis reload | nein | – | reload |
| `cylinder` | Trommel / Cylinder | Sechs Kammern; dreht je Schuss um 60° | auf dem Kran gelagert | crane | dark_metal | 42×64×42 | 0.000, -0.048, 0.052 | dreht um Achse f durch (48, 52, 0) mm, 0…60°; Ereignis fire | nein | BCY-6 | fire_da |
| `barrel` | Lauf / Barrel | Führt das Geschoss | in die Laufaufnahme geschraubt | ASM_barrel | metal | 18×142×18 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `barrel_rib` | Laufschiene / Barrel rib | Trägt das Korn, versteift den Lauf | auf dem Lauf | ASM_barrel | shell | 12×142×8.0 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `underlug` | Unterlauf / Underlug | Gewicht vorn gegen Hochschlag | unter dem Lauf | ASM_barrel | shell | 18×132×18 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `muzzle` | Mündung / Muzzle | Mündungskrone; Socket_Muzzle | Laufende | ASM_barrel | dark_metal | 21×16×21 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `hammer` | Hahn / Hammer | Wird gespannt und schlägt beim Schuss vor | Drehpunkt hinten im Rahmen | ASM_mechanism | graphite | 8.0×20×26 | 0.000, 0.032, 0.072 | dreht um Achse x durch (-32, 72, 0) mm, 0…28°; Ereignis cock | nein | – | fire_da |
| `grip` | Griff / Grip | Haupthand; trägt Socket_Hand | am Rahmen verschraubt | ASM_grip_controls | graphite | 32×67×96 | 0.000, 0.000, 0.000 | fest | nein | BGM-P | – |
| `trigger` | Abzug / Trigger | Spannt und löst (Double Action) | Drehpunkt im Rahmen | ASM_grip_controls | metal | 6.0×8.7×24 | 0.000, -0.025, 0.025 | dreht um Achse x durch (25, 25, 0) mm, 0…-14°; Ereignis fire | nein | – | fire_da |
| `trigger_guard` | Abzugsbügel / Trigger guard | Schützt den Abzug | Rahmen vorn und Griff | ASM_grip_controls | graphite | 10×46×30 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `cylinder_latch` | Trommelriegel / Cylinder latch | Gibt den Kran frei (Daumen) | links am Rahmen, gleitet nach vorn | ASM_grip_controls | accent | 4.0×8.8×8.8 | 0.016, -0.002, 0.060 | verschiebt 6 mm (f,u,x (6, 0, 0)); Ereignis reload | ja – entlang Bewegung | – | reload |
| `rear_sight_l` | Kimme links / Rear sight left | Hintere Visiermarke; die Kerbe dazwischen | auf Verschluss bzw. Rahmen (fest) | ASM_sight | graphite | 6.0×9.8×9.0 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `rear_sight_r` | Kimme rechts / Rear sight right | Hintere Visiermarke; die Kerbe dazwischen | auf Verschluss bzw. Rahmen (fest) | ASM_sight | graphite | 6.0×9.8×9.0 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `front_sight` | Korn / Front sight | Vordere Visiermarke | auf Lauf bzw. Verschluss (fest) | ASM_sight | graphite | 3.0×7.7×9.0 | 0.000, 0.000, 0.000 | fest | nein | – | – |

## Anker

| Anker | Position m (X, Y, Z) | Teil | Hinweis |
|---|---|---|---|
| `Socket_Hand` | 0.0000, 0.0000, 0.0000 | grip | – |
| `Socket_Muzzle` | 0.0000, -0.2500, 0.0640 | muzzle | – |
| `Socket_Sight` | 0.0000, 0.0220, 0.0920 | rear_sight_l | Kimme; Visierlinie über Kimme und Korn |
| `Socket_Eye` | 0.0000, 0.1800, 0.0920 | rear_sight_l | Vorschlag: 160 mm hinter der Kimme |
| `Socket_CenterOfMass` | 0.0001, -0.0465, 0.0347 | – | abgeleitet: Volumenschwerpunkt, homogene Dichte, ohne Glas |

## Schnittstellen

| ID | Bedeutung | Regel |
|---|---|---|
| BCY-6 | Revolvertrommel 6 Kammern | Trommel r 22 mm auf Kran, Achse 12 mm unter Laufachse |
| BGM-P | Griffmodul Pistole (Faustfeuerwaffen) | Neigung 18°, Magazin im Griff |

## Aktionen der Mechanik

| Aktion | Beschreibung | Bilder (30 fps) | Teile | Ereignisse (Bild) | Status |
|---|---|---|---|---|---|
| `fire_da` | Schuss Double Action (Hahn, Trommel) | 14 (0.47 s) | trigger, hammer, cylinder | shot (7) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |
| `reload` | Trommel ausschwenken, laden, einschwenken | 72 (2.40 s) | cylinder_latch, crane | cylinder_open (18), eject (24), rounds_in (40), cylinder_closed (62) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |

Haltungen, Übergänge und Status aller Aktionen: [haltungen.md › BASIC-04](../haltungen.md#basic-04).
