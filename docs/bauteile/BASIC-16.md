<!-- erzeugt von tools/make_docs.py – nicht von Hand ändern -->

# BASIC-16 Schwert – „Klingenlauf“

Einschneidiges Schwert mit Parierblock und Zweihandgriff.

Typ `sword` (Sword) · Munition heavy · Feuerart `melee` · Quelle des Entwurfs: `basic/weapons/` · Spec: [`data/specs/BASIC-16.spec.json`](../../data/specs/BASIC-16.spec.json).

**Maße (gemessen, Ruhelage, Visier montiert):** Länge 1194 mm · Höhe 76 mm · Breite 96 mm · 9 Bauteile · 1136 Dreiecke (mit Fasen).

Rahmen: Meter, vorn −Y, oben +Z, links +X, Ursprung `Socket_Hand`. `origin_m` ist der Objektursprung (bei beweglichen Teilen der Drehpunkt).

## Baugruppenbaum

```
BASIC-16
├─ ASM_blade  Klinge / Blade
│   ├─ blade_core  Klingenkern
│   ├─ blade_spine  Klingenrücken
│   ├─ blade_edge  Schneide
├─ ASM_guard  Parierblock / Guard
│   ├─ guard  Parierblock
│   ├─ crossguard  Parierstange
│   ├─ charge_window  Ladeanzeige
├─ ASM_grip_controls  Griff und Bedienung / Grip and controls
│   ├─ grip  Griff
│   ├─ grip_ring  Griffring
│   ├─ pommel  Knauf
```

## Bauteilliste

| ID | Name (de / en) | Funktion | Befestigung | übergeordnet | Material | Maße X×Y×Z mm | Ursprung m | Bewegung | Entnahme | Schnittstelle | Aktionen |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `blade_core` | Klingenkern / Blade core | Tragender Klingenrücken | in den Parierblock gesteckt | ASM_blade | dark_metal | 9.0×903×42 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `blade_spine` | Klingenrücken / Blade spine | Versteift die Klinge; heller Familienakzent oben | auf den Klingenkern geklebt | ASM_blade | shell | 12×795×15 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `blade_edge` | Schneide / Edge | Helle Schneide unten; Trefferfläche | mit dem Kern verbunden | ASM_blade | metal | 5.0×910×34 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `guard` | Parierblock / Guard block | Fasst die Klinge, schützt die Hand, trägt die Zelle | auf die Angel geschoben | ASM_guard | shell | 46×50×76 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `crossguard` | Parierstange / Crossguard | Fängt gegnerische Klingen ab | am Parierblock | ASM_guard | dark_metal | 96×14×64 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `charge_window` | Ladeanzeige / Charge window | Zeigt die Ladungen für schwere Angriffe | eingelassen | ASM_guard | energy | 1.0×26×10 | 0.000, 0.000, 0.000 | Leuchten 0…5.0 (Ereignis charge) | nein | – | guard_charge |
| `grip` | Griff / Grip | Zweihandgriff; Socket_Hand vorn, Stützhand hinten | auf der Angel | ASM_grip_controls | graphite | 31×194×31 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `grip_ring` | Griffring / Grip ring | Trennt die beiden Handpositionen (Akzent) | auf dem Griff | ASM_grip_controls | accent | 34×8.0×34 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `pommel` | Knauf / Pommel | Gegengewicht, sichert die Angel | Griffende | ASM_grip_controls | dark_metal | 41×36×41 | 0.000, 0.000, 0.000 | fest | nein | – | – |

## Anker

| Anker | Position m (X, Y, Z) | Teil | Hinweis |
|---|---|---|---|
| `Socket_Hand` | 0.0000, 0.0000, 0.0000 | grip | vordere Hand am Parierblock |
| `Socket_SupportHand` | 0.0000, 0.1040, 0.0000 | grip | hintere Hand vor dem Knauf |
| `Socket_Muzzle` | 0.0000, -1.0100, 0.0000 | blade_edge | Klingenspitze (Formgen-Konvention) |
| `Socket_BladeCenter` | 0.0000, -0.5600, 0.0000 | blade_core | Trefferzentrum |
| `Socket_CenterOfMass` | 0.0000, -0.2549, 0.0018 | – | abgeleitet: Volumenschwerpunkt, homogene Dichte, ohne Glas |

## Aktionen der Mechanik

| Aktion | Beschreibung | Bilder (30 fps) | Teile | Ereignisse (Bild) | Status |
|---|---|---|---|---|---|
| `guard_charge` | Blocken: Ladeanzeige zieht Energie | 30 (1.00 s) | charge_window | block_start (6), block_end (24) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |

Haltungen, Übergänge und Status aller Aktionen: [haltungen.md › BASIC-16](../haltungen.md#basic-16).
