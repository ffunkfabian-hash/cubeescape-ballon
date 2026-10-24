<!-- erzeugt von tools/make_docs.py – nicht von Hand ändern -->

# BASIC-17 Glefe – „Schildwacht“

Glefe mit Projektil-Emitter, aufklappbarem Schild und Klingenkopf.

Typ `glaive` (Glaive) · Munition special · Feuerart `melee_projectile_shield` · Quelle des Entwurfs: `basic/weapons/` · Spec: [`data/specs/BASIC-17.spec.json`](../../data/specs/BASIC-17.spec.json).

**Maße (gemessen, Ruhelage, Visier montiert):** Länge 1423 mm · Höhe 152 mm · Breite 53 mm · 13 Bauteile · 1692 Dreiecke (mit Fasen).

Rahmen: Meter, vorn −Y, oben +Z, links +X, Ursprung `Socket_Hand`. `origin_m` ist der Objektursprung (bei beweglichen Teilen der Drehpunkt).

## Baugruppenbaum

```
BASIC-17
├─ ASM_shaft  Stange / Shaft
│   ├─ shaft  Stange
│   ├─ counterweight  Gegengewicht
├─ ASM_receiver  Hauptgehäuse / Receiver
│   ├─ core  Kernkörper
├─ ASM_ammo  Munitionsversorgung / Ammunition feed
│   ├─ energy_cell  Energiezelle
│   │  └(an energy_cell) energy_cell_window  Ladefenster
├─ ASM_grip_controls  Griff und Bedienung / Grip and controls
│   ├─ grip  Pistolengriff
│   ├─ trigger  Abzug
├─ ASM_support  Stützbereich / Support
│   ├─ support_grip  Stützgriff
├─ ASM_blade  Klinge / Blade
│   ├─ blade_mount  Klingenaufnahme
│   ├─ blade  Klinge
│   ├─ emitter  Emitter
├─ ASM_shield  Schild / Shield
│   ├─ shield_l  Schildflügel links
│   ├─ shield_r  Schildflügel rechts
```

## Bauteilliste

| ID | Name (de / en) | Funktion | Befestigung | übergeordnet | Material | Maße X×Y×Z mm | Ursprung m | Bewegung | Entnahme | Schnittstelle | Aktionen |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `shaft` | Stange / Shaft | Trägt alle Baugruppen | durchgehend | ASM_shaft | graphite | 25×960×25 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `counterweight` | Gegengewicht / Counterweight | Balance und Stoßende | Stangenende | ASM_shaft | dark_metal | 37×38×37 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `core` | Kernkörper / Core body | Abzugsmechanik und Zellenschacht | um die Stange geklemmt | ASM_receiver | shell | 40×270×52 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `support_grip` | Stützgriff / Support grip | Griffbereich der Stützhand | auf der Stange | ASM_support | graphite | 33×130×33 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `blade_mount` | Klingenaufnahme / Blade mount | Fasst Klinge und Emitter | am Stangenende | ASM_blade | dark_metal | 34×60×46 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `blade` | Klinge / Blade | Blattförmige Klinge für Stiche und Hiebe | in der Aufnahme | ASM_blade | metal | 9.0×391×64 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `emitter` | Emitter / Emitter | Gibt das Projektil ab; leuchtet beim Schuss | in der Klingenaufnahme | ASM_blade | energy | 12×60×12 | 0.000, 0.000, 0.000 | Leuchten 0…6.0 (Ereignis fire) | nein | – | fire |
| `shield_l` | Schildflügel links / Shield wing left | Klappt zum Blocken nach vorn-außen auf | Scharnier vorn an der Klingenaufnahme | ASM_shield | shell | 5.0×166×96 | 0.024, -0.636, 0.040 | dreht um Achse u durch (636, 40, 24) mm, 0…-70°; Ereignis shield | nein | – | shield |
| `shield_r` | Schildflügel rechts / Shield wing right | Klappt zum Blocken nach vorn-außen auf | Scharnier vorn an der Klingenaufnahme | ASM_shield | shell | 5.0×166×96 | -0.024, -0.636, 0.040 | dreht um Achse u durch (636, 40, -24) mm, 0…70°; Ereignis shield | nein | – | shield |
| `energy_cell` | Energiezelle / Energy cell | Speichert die Ladungen; austauschbar | rastet im Zellenschacht ein (lösbar) | ASM_ammo | dark_metal | 26×120×16 | 0.000, -0.100, 0.078 | verschiebt 60 mm (f,u,x (0, 60, 0)); Ereignis reload | ja – entlang Bewegung | BEC-1 | reload |
| `energy_cell_window` | Ladefenster / Charge window | Zeigt den Ladezustand | in die Zelle eingelassen | energy_cell | energy | 1.0×60×4.0 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `grip` | Pistolengriff / Pistol grip | Haupthand hält die Waffe; trägt Socket_Hand | mit Unterem Gehäuse verschraubt (fest) | ASM_grip_controls | graphite | 30×62×84 | 0.000, 0.000, 0.000 | fest | nein | BGM-1 | – |
| `trigger` | Abzug / Trigger | Feuer auslösen (Zeigefinger) | Drehpunkt im Unteren Gehäuse | ASM_grip_controls | metal | 7.0×7.8×26 | 0.000, -0.039, 0.017 | dreht um Achse x durch (39.35898384862246, 17, 0) mm, 0…-12°; Ereignis fire | nein | – | fire |

## Anker

| Anker | Position m (X, Y, Z) | Teil | Hinweis |
|---|---|---|---|
| `Socket_Hand` | 0.0000, 0.0000, 0.0000 | grip | hintere Hand mit Abzug |
| `Socket_SupportHand` | 0.0000, -0.3650, 0.0400 | support_grip | – |
| `Socket_Muzzle` | 0.0000, -0.7600, 0.0400 | emitter | Projektilaustritt |
| `Socket_BladeCenter` | 0.0000, -0.9000, 0.0400 | blade | – |
| `Socket_CenterOfMass` | 0.0000, -0.2539, 0.0389 | – | abgeleitet: Volumenschwerpunkt, homogene Dichte, ohne Glas |

## Schnittstellen

| ID | Bedeutung | Regel |
|---|---|---|
| BEC-1 | Energiezelle Typ 1 | Zellenschacht je Waffe; Maß im Spec |
| BGM-1 | Griffmodul Typ 1 (Gewehrfamilie) | Oberkante 42 × 30 mm, Neigung 15° (oben nach vorn), Abzugsbügel bis f = +78 mm |

## Aktionen der Mechanik

| Aktion | Beschreibung | Bilder (30 fps) | Teile | Ereignisse (Bild) | Status |
|---|---|---|---|---|---|
| `fire` | Projektil abgeben | 14 (0.47 s) | trigger, emitter | shot (2) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |
| `shield` | Schild aufklappen, halten, schließen | 40 (1.33 s) | shield_l, shield_r | shield_up (8), shield_down (38) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |
| `reload` | Energiezelle wechseln | 70 (2.33 s) | energy_cell | cell_out (16), cell_in (50) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |

Haltungen, Übergänge und Status aller Aktionen: [haltungen.md › BASIC-17](../haltungen.md#basic-17).
