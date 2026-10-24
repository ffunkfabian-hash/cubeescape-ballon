<!-- erzeugt von tools/make_docs.py – nicht von Hand ändern -->

# BASIC-11 Lineares Fusionsgewehr – „Schienenlicht“

Offener Linearbeschleuniger mit Zielfernrohr; ein Strahl nach kurzer Ladung.

Typ `linear_fusion_rifle` (Linear Fusion Rifle) · Munition heavy · Feuerart `charge_single` · Quelle des Entwurfs: `basic/weapons/` · Spec: [`data/specs/BASIC-11.spec.json`](../../data/specs/BASIC-11.spec.json).

**Maße (gemessen, Ruhelage, Visier montiert):** Länge 1217 mm · Höhe 281 mm · Breite 57 mm · 30 Bauteile · 7152 Dreiecke (mit Fasen).

Rahmen: Meter, vorn −Y, oben +Z, links +X, Ursprung `Socket_Hand`. `origin_m` ist der Objektursprung (bei beweglichen Teilen der Drehpunkt).

## Baugruppenbaum

```
BASIC-11
├─ ASM_receiver  Hauptgehäuse / Receiver
│   ├─ receiver  Gehäuse
│   ├─ rail  Schiene
├─ ASM_barrel  Lauf / Emitter / Barrel / emitter
│   ├─ rail_top  Beschleunigerschiene oben
│   ├─ rail_bottom  Beschleunigerschiene unten
│   ├─ linear_core  Linearkern
│   ├─ muzzle  Fokusmündung
│   ├─ muzzle_bridge  Mündungsbrücke
├─ ASM_ammo  Munitionsversorgung / Ammunition feed
│   ├─ energy_cell  Energiezelle
│   │  └(an energy_cell) energy_cell_window  Ladefenster
├─ ASM_sight  Visier / Sight
│   ├─ scope_mount_r  Zielfernrohr-Ring hinten
│   │  └(an scope_mount_r) scope_mount_f  Zielfernrohr-Ring vorn
│   │  └(an scope_mount_r) scope_tube  Mittelrohr
│   │  └(an scope_mount_r) scope_eyepiece  Okular
│   │  └(an scope_mount_r) scope_objective  Objektiv
│   │  └(an scope_mount_r) scope_turret  Verstellturm
│   │  └(an scope_mount_r) scope_glass  Objektivglas
│   │  └(an scope_mount_r) scope_ocular_glass  Okularglas
├─ ASM_grip_controls  Griff und Bedienung / Grip and controls
│   ├─ grip  Pistolengriff
│   ├─ trigger  Abzug
│   ├─ trigger_guard  Abzugsbügel
├─ ASM_support  Stützbereich / Support
│   ├─ support_grip  Stützgriff
├─ ASM_stock  Schaft / Stock
│   ├─ stock_joint  Schaftverbindung
│   ├─ stock_spine  Schaftrohr
│   ├─ stock  Schulterstütze
│   ├─ butt_pad  Schaftkappe
│   ├─ cheek_rest  Wangenauflage
├─ ASM_cooling  Kühlung / Cooling
│   ├─ coil_1  Spulenring 1
│   ├─ coil_2  Spulenring 2
│   ├─ coil_3  Spulenring 3
│   ├─ coil_4  Spulenring 4
```

## Bauteilliste

| ID | Name (de / en) | Funktion | Befestigung | übergeordnet | Material | Maße X×Y×Z mm | Ursprung m | Bewegung | Entnahme | Schnittstelle | Aktionen |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `receiver` | Gehäuse / Receiver | Tragkörper; Schienen und Zellenschacht | Grundkörper | ASM_receiver | shell | 48×372×94 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `rail_top` | Beschleunigerschiene oben / Upper accelerator rail | Führt das Feld oben | im Gehäuse verankert | ASM_barrel | shell | 26×598×14 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `rail_bottom` | Beschleunigerschiene unten / Lower accelerator rail | Führt das Feld unten | im Gehäuse verankert | ASM_barrel | shell | 26×578×14 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `linear_core` | Linearkern / Linear core | Leuchtender Kern; lädt sich sichtbar auf | zwischen den Schienen | ASM_barrel | energy | 9.7×590×9.7 | 0.000, 0.000, 0.000 | Leuchten 0…6.0 (Ereignis charge) | nein | – | charge_fire |
| `muzzle` | Fokusmündung / Focus muzzle | Bündelt den Strahl; Socket_Muzzle | vor den Schienen | ASM_barrel | dark_metal | 31×40×31 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `muzzle_bridge` | Mündungsbrücke / Muzzle bridge | Verbindet Schienenenden und Mündung | zwischen den Schienen | ASM_barrel | dark_metal | 22×16×72 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `support_grip` | Stützgriff / Support grip | Griff der Stützhand unter der Schiene | unter die untere Schiene geschraubt | ASM_support | graphite | 34×116×25 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `coil_1` | Spulenring 1 / Coil ring 1 | Beschleunigerspule um Kern und Schienen | um beide Schienen geklemmt | ASM_cooling | dark_metal | 40×16×88 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `coil_2` | Spulenring 2 / Coil ring 2 | Beschleunigerspule um Kern und Schienen | um beide Schienen geklemmt | ASM_cooling | dark_metal | 40×16×88 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `coil_3` | Spulenring 3 / Coil ring 3 | Beschleunigerspule um Kern und Schienen | um beide Schienen geklemmt | ASM_cooling | dark_metal | 40×16×88 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `coil_4` | Spulenring 4 / Coil ring 4 | Beschleunigerspule um Kern und Schienen | um beide Schienen geklemmt | ASM_cooling | dark_metal | 40×16×88 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `energy_cell` | Energiezelle / Energy cell | Speichert die Ladungen; austauschbar | rastet im Zellenschacht ein (lösbar) | ASM_ammo | dark_metal | 40×88×28 | 0.000, 0.090, 0.038 | verschiebt 110 mm (f,u,x (0, -110, 0)); Ereignis reload | ja – entlang Bewegung | BEC-1 | reload |
| `energy_cell_window` | Ladefenster / Charge window | Zeigt den Ladezustand | in die Zelle eingelassen | energy_cell | energy | 1.0×44×4.0 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `rail` | Schiene / Top rail | Aufnahme für Visiere (BRI-22) | auf Oberem Gehäuse (fest) | ASM_receiver | dark_metal | 22×320×8.5 | 0.000, 0.000, 0.000 | fest | nein | BRI-22 | – |
| `scope_mount_r` | Zielfernrohr-Ring hinten / Scope ring rear | Klemmt das Rohr auf die Schiene BRI-22 | Klemmung auf Schiene (lösbar) | ASM_sight | dark_metal | 24×22×26 | 0.000, 0.039, 0.150 | verschiebt 80 mm (f,u,x (0, 80, 0)); Ereignis swap_sight | ja – beide Ringe lösen, Zielfernrohr senkrecht abnehmen | BRI-22 | – |
| `scope_mount_f` | Zielfernrohr-Ring vorn / Scope ring front | Klemmt das Rohr auf die Schiene BRI-22 | Klemmung auf Schiene (lösbar) | scope_mount_r | dark_metal | 24×22×26 | 0.000, 0.000, 0.000 | fest | nein | BRI-22 | – |
| `scope_tube` | Mittelrohr / Scope tube | Verbindet Okular und Objektiv | in den Ringen (fest) | scope_mount_r | graphite | 24×150×24 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `scope_eyepiece` | Okular / Eyepiece | Augenseite; Socket_Eye dahinter | am Mittelrohr (fest) | scope_mount_r | graphite | 32×32×32 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `scope_objective` | Objektiv / Objective bell | Lichteintritt vorn | am Mittelrohr (fest) | scope_mount_r | graphite | 57×42×57 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `scope_turret` | Verstellturm / Elevation turret | Höhenverstellung (Akzent, Bedienelement) | oben am Mittelrohr (fest) | scope_mount_r | accent | 16×16×11 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `scope_glass` | Objektivglas / Objective lens | Linse; Absehen-Ebene | im Objektiv (fest) | scope_mount_r | glass | 36×1.0×36 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `scope_ocular_glass` | Okularglas / Ocular lens | Augenlinse | im Okular (fest) | scope_mount_r | glass | 26×1.0×26 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `grip` | Pistolengriff / Pistol grip | Haupthand hält die Waffe; trägt Socket_Hand | mit Unterem Gehäuse verschraubt (fest) | ASM_grip_controls | graphite | 30×70×112 | 0.000, 0.000, 0.000 | fest | nein | BGM-1 | – |
| `trigger` | Abzug / Trigger | Feuer auslösen (Zeigefinger) | Drehpunkt im Unteren Gehäuse | ASM_grip_controls | metal | 7.0×7.8×26 | 0.000, -0.047, 0.045 | dreht um Achse x durch (46.86156123669389, 45, 0) mm, 0…-12°; Ereignis fire | nein | – | charge_fire |
| `trigger_guard` | Abzugsbügel / Trigger guard | Schützt den Abzug, Fingerfreiraum ≥ 22 mm | Griff vorn und Unteres Gehäuse (fest) | ASM_grip_controls | graphite | 12×58×35 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `stock_joint` | Schaftverbindung / Stock joint | Verbindet Schaft und Gehäuse; Verriegelung | Steckverbindung am Gehäuseende (fest) | ASM_stock | dark_metal | 30×12×42 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `stock_spine` | Schaftrohr / Stock spine | Trägt die Schulterstütze in Linie mit dem Lauf | in der Schaftverbindung (fest) | ASM_stock | graphite | 28×100×28 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `stock` | Schulterstütze / Buttstock | Anlage an der Schulter, Wangenauflage oben | auf dem Schaftrohr (fest) | ASM_stock | shell | 36×94×106 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `butt_pad` | Schaftkappe / Butt pad | Rutschfeste Anlage an der Schulter | auf das Schaftende gesteckt (fest) | ASM_stock | graphite | 40×19×115 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `cheek_rest` | Wangenauflage / Cheek rest | Anlage für die Wange beim Zielen | auf der Schulterstütze (fest) | ASM_stock | graphite | 26×79×10 | 0.000, 0.000, 0.000 | fest | nein | – | – |

## Anker

| Anker | Position m (X, Y, Z) | Teil | Hinweis |
|---|---|---|---|
| `Socket_Hand` | 0.0000, 0.0000, 0.0000 | grip | – |
| `Socket_SupportHand` | 0.0000, -0.3300, 0.0520 | support_grip | – |
| `Socket_Muzzle` | 0.0000, -0.8520, 0.1000 | muzzle | – |
| `Socket_Cell` | 0.0000, 0.0900, 0.0380 | energy_cell | – |
| `Socket_Sight` | 0.0000, 0.0900, 0.1880 | scope_eyepiece | hinteres Okularende auf der Visierlinie |
| `Socket_Reticle` | 0.0000, -0.1245, 0.1880 | scope_glass | Mitte Objektivglas |
| `Socket_Eye` | 0.0000, 0.1600, 0.1880 | scope_eyepiece | Vorschlag: Augenabstand 70 mm |
| `Socket_CenterOfMass` | 0.0000, -0.0966, 0.0948 | – | abgeleitet: Volumenschwerpunkt, homogene Dichte, ohne Glas |

## Schnittstellen

| ID | Bedeutung | Regel |
|---|---|---|
| BEC-1 | Energiezelle Typ 1 | Zellenschacht je Waffe; Maß im Spec |
| BGM-1 | Griffmodul Typ 1 (Gewehrfamilie) | Oberkante 42 × 30 mm, Neigung 15° (oben nach vorn), Abzugsbügel bis f = +78 mm |
| BRI-22 | Schiene 22 mm (Oberseite Gehäuse) | Breite 22 mm, Höhe 8 mm, Klemmfuß 22 mm breit, Mindestlänge Klemmfuß 40 mm |

## Aktionen der Mechanik

| Aktion | Beschreibung | Bilder (30 fps) | Teile | Ereignisse (Bild) | Status |
|---|---|---|---|---|---|
| `charge_fire` | Aufladen und Einzelstrahl | 36 (1.20 s) | trigger, linear_core | charge_start (2), charged (16), beam (18), ready (34) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |
| `reload` | Energiezelle wechseln | 80 (2.67 s) | energy_cell | cell_out (18), cell_in (56), ready (64) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |

Haltungen, Übergänge und Status aller Aktionen: [haltungen.md › BASIC-11](../haltungen.md#basic-11).
