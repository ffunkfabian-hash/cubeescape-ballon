# BASIC-Spec (`cubeescape-ballon/basic-spec`, format_version 1)

Eine Datei je Waffe: `data/specs/BASIC-NN.spec.json`. Erzeugt von `tools/blender_build.py` **am gebauten Modell** (mit Fasen,
Ruhelage, Visier montiert); `tools/sync_specs.py` übernimmt sie aus der Bauausgabe ins Repo. Nicht von Hand ändern.

**Vertrag:** Felder werden nur ergänzt (gleiche `format_version`); Umbenennen, Entfernen oder Bedeutungswechsel → `format_version` 2.
Abnehmer prüfen `format` und `format_version` und ignorieren unbekannte Felder. Heute gibt es keinen Abnehmer außerhalb dieses Repos.

## Rahmen

Meter, 5 Nachkommastellen. Blender-Achsen: vorn −Y, oben +Z, links +X; Ursprung `Socket_Hand` (wie Formgen-Geometrie-Spec v1 und
Toolgen). Autorenmaß in den Waffenmodulen: mm als (f nach vorn, u nach oben, x nach links) → Meter (x, −f, u).

## Felder

| Feld | Inhalt |
|---|---|
| `format`, `format_version`, `generator` | Kennung, Version 1, Werkzeug und Blender-Version |
| `weapon` | `id` (BASIC-NN), `num`, `type` (englisch, eindeutig), `type_de`, `type_en`, `name`, `ammo`, `fire`, `reference_length_m` mit Quelle, `summary` |
| `axes`, `units` | siehe Rahmen |
| `assemblies[]` | `id`, `de`, `en`, `parts` (IDs) – Hierarchie Waffe → Baugruppe → Bauteil |
| `parts[]` | `id` (stabil, englisch), `name_de`, `name_en`, `assembly`, `function_de`, `attachment_de`, `material_role`, `material_de`, `interface`, `parent_part` (bewegtes Elternteil, z. B. Patrone am Magazin), `shape`, `bevel_mm`, `blender_object`, `origin_m` (Objektursprung = Drehpunkt bei beweglichen Teilen), `bounds_m`, `size_mm` (X, Y, Z), `triangles`, `volume_cm3`, `moving`, `removable` |
| `parts[].moving` | `kind` (`translate`, `rotate`, `segment` = Sehnenhälfte, `glow` = Leuchtstärke), `event`, `pivot_m`; translate: `vector_m`, `travel_mm`; rotate: `axis_blender`, `axis_sign`, `range_deg`; segment: `tip_m`, `nock_rest_m`, `vector_m` |
| `anchors` | `Socket_*` mit `position_m`, `part`, `note`, `source`; `Socket_CenterOfMass` ist der Volumenschwerpunkt (homogene Dichte, ohne Glas) |
| `dimensions` | `bounds_m`, `length_m` (Y), `height_m` (Z), `width_m` (X), `reference_length_m` |
| `counts` | `parts`, `triangles` (nach Fasen), `assemblies` |
| `actions` | je Aktion `de`, `frames`, `fps` (30), `parts`, `events` [(Bild, Name)], `status` |
| `interfaces` | verwendete Schnittstellen-IDs (Bedeutung: `basic/common.py › INTERFACES`, [designvertrag.md](designvertrag.md)) |

## Abgrenzung zu Formgen/Toolgen

Der BASIC-Spec ist kein Ersatz für `cubeescape-design/geometry-spec` v1. Für einen Toolgen-Import fehlen noch: Netze je Teil im JSON,
`grip` (Griffachse, Neigung, Querschnitt), `support.radius_m`, `sight`-Block mit Fensterdaten, `sheet`-Block. Die Netze liegen im
`.glb`/`.blend`; der Export im Formgen-Format ist **offen** und braucht Abstimmung mit Toolgen (Herkunftsnachweis `provenance.json`).
