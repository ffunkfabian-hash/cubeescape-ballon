<!-- erzeugt von tools/make_docs.py – nicht von Hand ändern -->

# BASIC-05 Pistole – „Seitenwaffe“

Kompakte Schlittenpistole mit Magazin im Griff.

Typ `sidearm` (Sidearm) · Munition primary · Feuerart `semi_auto` · Quelle des Entwurfs: `basic/weapons/` · Spec: [`data/specs/BASIC-05.spec.json`](../../data/specs/BASIC-05.spec.json).

**Maße (gemessen, Ruhelage, Visier montiert):** Länge 224 mm · Höhe 156 mm · Breite 30 mm · 13 Bauteile · 2004 Dreiecke (mit Fasen).

Rahmen: Meter, vorn −Y, oben +Z, links +X, Ursprung `Socket_Hand`. `origin_m` ist der Objektursprung (bei beweglichen Teilen der Drehpunkt).

## Baugruppenbaum

```
BASIC-05
├─ ASM_receiver  Hauptgehäuse / Receiver
│   ├─ frame  Rahmen
├─ ASM_barrel  Lauf / Emitter / Barrel / emitter
│   ├─ barrel  Lauf
├─ ASM_ammo  Munitionsversorgung / Ammunition feed
│   ├─ magazine  Magazin
│   │  └(an magazine) magazine_base  Magazinboden
├─ ASM_sight  Visier / Sight
│   │  └(an slide) rear_sight_l  Kimme links
│   │  └(an slide) rear_sight_r  Kimme rechts
│   │  └(an slide) front_sight  Korn
├─ ASM_grip_controls  Griff und Bedienung / Grip and controls
│   ├─ grip  Griff
│   ├─ trigger  Abzug
│   ├─ trigger_guard  Abzugsbügel
│   ├─ slide_stop  Schlittenfang
│   ├─ mag_release  Magazinhalter
├─ ASM_mechanism  Bewegliche Mechanik / Moving mechanism
│   ├─ slide  Schlitten
```

## Bauteilliste

| ID | Name (de / en) | Funktion | Befestigung | übergeordnet | Material | Maße X×Y×Z mm | Ursprung m | Bewegung | Entnahme | Schnittstelle | Aktionen |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `frame` | Rahmen / Frame | Trägt Schlitten, Abzug und Griff | Grundkörper | ASM_receiver | graphite | 26×193×16 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `slide` | Schlitten / Slide | Verschluss; läuft beim Schuss zurück | auf den Rahmenschienen (gleitet) | ASM_mechanism | shell | 26×220×28 | 0.000, -0.060, 0.060 | verschiebt 42 mm (f,u,x (-42, 0, 0)); Ereignis fire | nein | – | fire_semi, reload_empty |
| `barrel` | Lauf / Barrel | Führt das Geschoss; Mündung schaut aus dem Schlitten | im Rahmen gelagert | ASM_barrel | metal | 12×54×12 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `grip` | Griff / Grip | Haupthand; Magazinschacht innen; trägt Socket_Hand | Teil des Rahmens | ASM_grip_controls | graphite | 28×69×98 | 0.000, 0.000, 0.000 | fest | nein | BGM-P | – |
| `magazine` | Magazin / Magazine | Hält die Patronen; steckt im Griff | rastet im Griff ein (lösbar) | ASM_ammo | dark_metal | 20×51×86 | 0.000, 0.006, -0.020 | verschiebt 120 mm (f,u,x (-37.1, -114.1, 0)); Ereignis reload | ja – Entnahme entlang der Griffachse nach unten | – | reload_empty |
| `magazine_base` | Magazinboden / Magazine base plate | Greifkante; schließt den Griff unten ab | am Magazin | magazine | shell | 30×40×9.0 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `trigger` | Abzug / Trigger | Feuer auslösen | Drehpunkt im Rahmen | ASM_grip_controls | metal | 6.0×7.9×24 | 0.000, -0.033, 0.029 | dreht um Achse x durch (33, 29, 0) mm, 0…-12°; Ereignis fire | nein | – | fire_semi |
| `trigger_guard` | Abzugsbügel / Trigger guard | Schützt den Abzug | Teil des Rahmens | ASM_grip_controls | graphite | 14×54×33 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `slide_stop` | Schlittenfang / Slide stop | Hält den Schlitten nach dem letzten Schuss offen | links am Rahmen (dreht) | ASM_grip_controls | accent | 2.4×24×5.0 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `mag_release` | Magazinhalter / Magazine release | Löst das Magazin | links im Rahmen | ASM_grip_controls | accent | 3.5×7.8×7.8 | 0.014, -0.016, 0.036 | verschiebt 2 mm (f,u,x (0, 0, -2.5)); Ereignis reload | ja – entlang Bewegung | – | reload_empty |
| `rear_sight_l` | Kimme links / Rear sight left | Hintere Visiermarke; die Kerbe dazwischen | auf Verschluss bzw. Rahmen (fest) | slide | graphite | 6.0×9.8×8.0 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `rear_sight_r` | Kimme rechts / Rear sight right | Hintere Visiermarke; die Kerbe dazwischen | auf Verschluss bzw. Rahmen (fest) | slide | graphite | 6.0×9.8×8.0 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `front_sight` | Korn / Front sight | Vordere Visiermarke | auf Lauf bzw. Verschluss (fest) | slide | graphite | 3.0×7.6×8.0 | 0.000, 0.000, 0.000 | fest | nein | – | – |

## Anker

| Anker | Position m (X, Y, Z) | Teil | Hinweis |
|---|---|---|---|
| `Socket_Hand` | 0.0000, 0.0000, 0.0000 | grip | – |
| `Socket_Muzzle` | 0.0000, -0.1740, 0.0580 | barrel | – |
| `Socket_Sight` | 0.0000, 0.0420, 0.0800 | rear_sight_l | Kimme |
| `Socket_Eye` | 0.0000, 0.2000, 0.0800 | rear_sight_l | Vorschlag: Augenabstand ausgestreckter Arm, Wert offen |
| `Socket_CenterOfMass` | 0.0000, -0.0421, 0.0224 | – | abgeleitet: Volumenschwerpunkt, homogene Dichte, ohne Glas |

## Schnittstellen

| ID | Bedeutung | Regel |
|---|---|---|
| BGM-P | Griffmodul Pistole (Faustfeuerwaffen) | Neigung 18°, Magazin im Griff |

## Aktionen der Mechanik

| Aktion | Beschreibung | Bilder (30 fps) | Teile | Ereignisse (Bild) | Status |
|---|---|---|---|---|---|
| `fire_semi` | Einzelschuss (Schlitten) | 10 (0.33 s) | trigger, slide | shot (2) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |
| `reload_empty` | Nachladen aus leerem Zustand | 60 (2.00 s) | mag_release, magazine, slide | mag_out (14), mag_seated (40), slide_release (50), ready (54) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |

Haltungen, Übergänge und Status aller Aktionen: [haltungen.md › BASIC-05](../haltungen.md#basic-05).
