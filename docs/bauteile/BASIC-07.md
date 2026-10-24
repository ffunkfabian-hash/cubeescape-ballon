<!-- erzeugt von tools/make_docs.py – nicht von Hand ändern -->

# BASIC-07 Bogen – „Sehnenzug“

Kampfbogen mit Recurve-Wurfarmen, Pfeilfenster und Ringvisier.

Typ `combat_bow` (Combat Bow) · Munition primary · Feuerart `draw_release` · Quelle des Entwurfs: `basic/weapons/` · Spec: [`data/specs/BASIC-07.spec.json`](../../data/specs/BASIC-07.spec.json).

**Maße (gemessen, Ruhelage, Visier montiert):** Länge 686 mm · Höhe 1030 mm · Breite 38 mm · 23 Bauteile · 3512 Dreiecke (mit Fasen).

Rahmen: Meter, vorn −Y, oben +Z, links +X, Ursprung `Socket_Hand`. `origin_m` ist der Objektursprung (bei beweglichen Teilen der Drehpunkt).

## Baugruppenbaum

```
BASIC-07
├─ ASM_riser  Mittelstück / Riser
│   ├─ riser_lower  Mittelstück unten
│   ├─ riser_upper  Mittelstück oben
│   ├─ riser_bridge  Fensterbrücke
│   ├─ arrow_rest  Pfeilauflage
├─ ASM_limbs  Wurfarme / Limbs
│   ├─ pocket_top  Wurfarmaufnahme oben
│   ├─ pocket_bottom  Wurfarmaufnahme unten
│   ├─ limb_top  Wurfarm oben
│   ├─ limb_bottom  Wurfarm unten
│   ├─ cam_top  Rolle oben
│   ├─ cam_bottom  Rolle unten
├─ ASM_string  Sehne / String
│   ├─ string_top  Sehne oben
│   ├─ string_bottom  Sehne unten
├─ ASM_arrow  Pfeil / Arrow
│   ├─ arrow_shaft  Pfeilschaft
│   │  └(an arrow_shaft) arrow_head  Pfeilspitze
│   │  └(an arrow_shaft) arrow_nock  Nocke
│   │  └(an arrow_shaft) fletch_top  Befiederung oben
│   │  └(an arrow_shaft) fletch_l  Befiederung links
│   │  └(an arrow_shaft) fletch_r  Befiederung rechts
├─ ASM_sight  Visier / Sight
│   ├─ sight_arm  Visierarm
│   ├─ sight_ring  Visierring
│   ├─ sight_pin  Leuchtpin
│   ├─ sight_pin_post  Pinträger
├─ ASM_grip_controls  Griff und Bedienung / Grip and controls
│   ├─ grip  Griff
```

## Bauteilliste

| ID | Name (de / en) | Funktion | Befestigung | übergeordnet | Material | Maße X×Y×Z mm | Ursprung m | Bewegung | Entnahme | Schnittstelle | Aktionen |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `grip` | Griff / Grip | Bogenhand; trägt Socket_Hand | auf das Mittelstück geschraubt | ASM_grip_controls | graphite | 32×51×72 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `riser_lower` | Mittelstück unten / Lower riser | Trägt den unteren Wurfarm | Grundkörper | ASM_riser | shell | 32×68×208 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `riser_upper` | Mittelstück oben / Upper riser | Trägt den oberen Wurfarm und das Visier | Grundkörper | ASM_riser | shell | 32×64×178 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `riser_bridge` | Fensterbrücke / Window bridge | Verbindet beide Hälften links; rechts bleibt das Pfeilfenster frei | Teil des Mittelstücks | ASM_riser | shell | 10×42×50 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `arrow_rest` | Pfeilauflage / Arrow rest | Führt den Pfeil im Fenster | auf der Fensterbrücke | ASM_riser | accent | 10×18×4.0 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `pocket_top` | Wurfarmaufnahme oben / Upper limb pocket | Klemmt den oberen Wurfarm | am Mittelstück | ASM_limbs | dark_metal | 38×54×20 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `pocket_bottom` | Wurfarmaufnahme unten / Lower limb pocket | Klemmt den unteren Wurfarm | am Mittelstück | ASM_limbs | dark_metal | 38×54×20 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `limb_top` | Wurfarm oben / Upper limb | Speichert die Zugenergie (Recurve) | in der Aufnahme geklemmt | ASM_limbs | shell | 34×104×260 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `limb_bottom` | Wurfarm unten / Lower limb | Speichert die Zugenergie (Recurve) | in der Aufnahme geklemmt | ASM_limbs | shell | 34×104×260 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `cam_top` | Rolle oben / Upper cam | Sehnenende oben | an der Wurfarmspitze | ASM_limbs | dark_metal | 20×20×20 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `cam_bottom` | Rolle unten / Lower cam | Sehnenende unten | an der Wurfarmspitze | ASM_limbs | dark_metal | 20×20×20 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `string_top` | Sehne oben / Upper string | Obere Sehnenhälfte; folgt dem Nockpunkt | zwischen Rolle und Nockpunkt | ASM_string | string | 3.3×3.3×459 | 0.000, 0.060, 0.505 | Sehnenhälfte: Ende fest an (-60, 505, 0), Nockpunkt 380 mm Auszug | nein | – | draw_hold_release, let_down |
| `string_bottom` | Sehne unten / Lower string | Untere Sehnenhälfte; folgt dem Nockpunkt | zwischen Rolle und Nockpunkt | ASM_string | string | 3.3×3.3×551 | 0.000, 0.060, -0.505 | Sehnenhälfte: Ende fest an (-60, -505, 0), Nockpunkt 380 mm Auszug | nein | – | draw_hold_release, let_down |
| `arrow_shaft` | Pfeilschaft / Arrow shaft | Pfeil; wird mit der Sehne zurückgezogen | auf der Auflage, Nocke an der Sehne | ASM_arrow | graphite | 6.7×620×6.7 | 0.000, 0.060, 0.046 | verschiebt 380 mm (f,u,x (-380, 0, 0)); Ereignis draw | nein | – | draw_hold_release, let_down |
| `arrow_head` | Pfeilspitze / Arrow head | Spitze | auf dem Schaft | arrow_shaft | dark_metal | 14×60×12 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `arrow_nock` | Nocke / Nock | Rastet an der Sehne ein | Schaftende | arrow_shaft | accent | 8.7×12×8.6 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `fletch_top` | Befiederung oben / Top vane | Stabilisiert den Flug (Leitfeder) | am Schaft | arrow_shaft | accent | 1.2×62×13 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `fletch_l` | Befiederung links / Left vane | Stabilisiert den Flug | am Schaft | arrow_shaft | graphite | 12×62×1.2 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `fletch_r` | Befiederung rechts / Right vane | Stabilisiert den Flug | am Schaft | arrow_shaft | graphite | 12×62×1.2 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_arm` | Visierarm / Sight arm | Trägt den Visierring vor dem Mittelstück | am Mittelstück verschraubt | ASM_sight | dark_metal | 6.0×34×6.0 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_ring` | Visierring / Sight ring | Ringvisier; frei durchsichtig | am Visierarm | ASM_sight | graphite | 26×6.0×26 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_pin` | Leuchtpin / Sight pin | Zielpunkt in Ringmitte | im Visierring | ASM_sight | energy | 1.6×2.0×3.0 | 0.000, 0.000, 0.000 | fest | nein | – | – |
| `sight_pin_post` | Pinträger / Pin post | Hält den Leuchtpin | im Visierring | ASM_sight | dark_metal | 1.2×2.0×9.0 | 0.000, 0.000, 0.000 | fest | nein | – | – |

## Anker

| Anker | Position m (X, Y, Z) | Teil | Hinweis |
|---|---|---|---|
| `Socket_Hand` | 0.0000, 0.0000, 0.0000 | grip | Bogenhand |
| `Socket_Nock` | 0.0000, 0.0600, 0.0460 | string_top | Nockpunkt in Ruhe (Toolgen-Name) |
| `Socket_ArrowTip` | 0.0000, -0.6160, 0.0460 | arrow_head | Pfeilspitze in Ruhe (Toolgen-Name) |
| `Socket_Muzzle` | 0.0000, -0.0080, 0.0460 | arrow_rest | Abgangspunkt des Pfeils an der Auflage |
| `Socket_Sight` | 0.0000, -0.0540, 0.0640 | sight_ring | Hinterkante Visierring |
| `Socket_Eye` | 0.0000, 0.4700, 0.0700 | sight_ring | Vorschlag: Auge am Ankerpunkt bei vollem Auszug |
| `Socket_CenterOfMass` | 0.0002, -0.0091, -0.0010 | – | abgeleitet: Volumenschwerpunkt, homogene Dichte, ohne Glas |

## Aktionen der Mechanik

| Aktion | Beschreibung | Bilder (30 fps) | Teile | Ereignisse (Bild) | Status |
|---|---|---|---|---|---|
| `draw_hold_release` | Ausziehen, halten, lösen | 60 (2.00 s) | arrow_shaft, string_top, string_bottom | nocked (0), full_draw (18), release (40), shot (42), arrow_gone (46) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |
| `let_down` | Entspannen ohne Schuss | 40 (1.33 s) | arrow_shaft, string_top, string_bottom | full_draw (16), relaxed (40) | Mechanik gesichtet (Clip); Hände offen; Dauer entworfen |

Haltungen, Übergänge und Status aller Aktionen: [haltungen.md › BASIC-07](../haltungen.md#basic-07).
