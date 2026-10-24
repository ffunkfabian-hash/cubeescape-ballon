# Absehen, Visierglas und Visier-Standard

> Erzeugt aus `basic/reticles.py` mit `python3 tools/export_reticles.py` – nicht von Hand ändern.

Eine Quelle für Blender (`basic/common.reticle`, Familienvisier `reflex_sight_v21`) und die Laufzeit (`data/reticles.json`). Katalogblatt: `python3 tools/reticle_sheet.py --sheet` (Belege `reticles.png`, Clip `clips/reticle_spread.mp4`).

## Formen

| ID | Name | Einsatz | Aufgehen |
|---|---|---|---|
| `ring_dot` | Ring mit Punkt | Holo-Standard: schneller Fang im Ring, genauer Punkt | ja |
| `dot` | Leuchtpunkt | Minimal, verdeckt nichts; zeigt keine Spreizung | nein |
| `cross` | Fadenkreuz | Vier Balken mit Lücke und Mittelpunkt; Balken wandern nach außen | ja |
| `chevron` | Winkel | Spitze ist der Zielpunkt, Haltepunkt bleibt frei; zeigt keine Spreizung | nein |
| `t_post` | T-Balken | Waagerechte zeigt Verkanten; Balken und Stachel wandern nach außen | ja |
| `circle_cross` | Kreis mit Kreuzmarken | Großer Ring mit vier Marken; Ring und Marken gehen auf | ja |
| `corners` | Eckklammern | Vier Winkel zeigen die Streuung, gehen diagonal auf | ja |

Jede Form gibt es in jeder Farbe und jeder Linienstärke.

## Farben

| ID | Name | Hex | Hinweis |
|---|---|---|---|
| `cyan` | Cyan | `#5FD3E0` | Standard, Familienfarbe |
| `red` | Rot | `#FF3D2E` | klassischer Leuchtpunkt |
| `green` | Grün | `#38E06E` | hell auf dunklem Grund |
| `amber` | Bernstein | `#FFB01F` | warm, gut auf Grau |
| `white` | Weiß | `#EEF2F5` | neutral, für helle Skins dezent |

## Linienstärken

| ID | Name | Faktor |
|---|---|---|
| `fine` | fein | 0.65 (Linie r = 0.20 mm) |
| `normal` | normal | 1.0 (Linie r = 0.30 mm) |
| `bold` | kräftig | 1.6 (Linie r = 0.48 mm) |

## Glasvarianten (dezent)

| ID | Name | Wirkung |
|---|---|---|
| `clean` | Klar | unbehandelt beschichtet |
| `dust` | Staub | feine Körner (~0,3 mm), jede siebte Zelle |
| `scratch` | Kratzer | dünne, schräg gestreckte Linien |
| `crack` | Riss | feines Rissnetz, nur obere Ecke |
| `cells` | Zellen | kaum sichtbare Zellvergütung über die Scheibe |
| `worn` | Benutzt | Staub und Kratzer |

## Aufgehen beim Schießen

Spreizung s in mm auf der Scheibe (Größe 1,0): Abklingen zur Basis mit Zeitkonstante, Impuls je Schuss bis zum Maximum, Laufen addiert, Zielen multipliziert.

| Profil | Name | Basis | je Schuss | Maximum | Abklingen | Laufen | Zielen |
|---|---|---|---|---|---|---|---|
| `auto` | Dauerfeuer | 0.0 | 0.9 | 5.0 | 0.28 s | 1.5 | ×0.35 |
| `burst` | Salve | 0.0 | 1.2 | 4.5 | 0.22 s | 1.4 | ×0.3 |
| `precision` | Präzision | 0.0 | 2.2 | 3.5 | 0.18 s | 1.0 | ×0.15 |
| `shotgun` | Schrot | 2.0 | 2.5 | 6.0 | 0.35 s | 1.0 | ×0.6 |
| `charge` | Aufladen | 0.0 | 1.5 | 4.0 | 0.25 s | 1.2 | ×0.3 |
| `explosive` | Sprengwaffe | 0.5 | 1.8 | 4.0 | 0.5 s | 0.8 | ×0.5 |
| `none` | kein Aufgehen | 0.0 | 0.0 | 0.0 | 0.2 s | 0.0 | ×0.0 |

Profil `charge`: während des Aufladens schrumpft die Spreizung von `charge_from` auf die Basis.

## Vorgabe je Waffentyp

| Typ | Visier | Hüfte | Aufgehen |
|---|---|---|---|
| `auto_rifle` | `ring_dot` | `cross` | `auto` |
| `pulse_rifle` | `circle_cross` | `cross` | `burst` |
| `scout_rifle` | `chevron` | `cross` | `precision` |
| `hand_cannon` | `dot` | `cross` | `precision` |
| `sidearm` | `dot` | `cross` | `auto` |
| `submachine_gun` | `dot` | `circle_cross` | `auto` |
| `shotgun` | `corners` | `corners` | `shotgun` |
| `sniper_rifle` | `t_post` | `dot` | `precision` |
| `fusion_rifle` | `t_post` | `corners` | `charge` |
| `linear_fusion_rifle` | `t_post` | `cross` | `charge` |
| `trace_rifle` | `corners` | `circle_cross` | `auto` |
| `grenade_launcher` | `chevron` | `circle_cross` | `explosive` |
| `rocket_launcher` | `circle_cross` | `circle_cross` | `explosive` |
| `machine_gun` | `circle_cross` | `cross` | `auto` |
| `combat_bow` | `dot` | `chevron` | `charge` |
| `sword` | – | `dot` | `none` |
| `glaive` | – | `cross` | `auto` |

## Visier-Standard

Visierhöhe (Socket_Eye über der Laufachse) 66 ± 4 mm. Socket_Eye ist der Augenpunkt beim Zielen, gemessen ab der vorderen Visieröffnung. Das Waffenmodell wird nicht vergrößert (Viewmodel-Zoom ×1.0); nur die Welt zoomt: Klassengrundzoom + Visierbonus. Teile mit `ads_hide` (Zielfernrohr-Rohr und Okular) sind beim Zielen ausgeblendet. Geprüft in `./check`. Herleitung: Destiny-Video und Motiongen-Messungen (`docs/quellen.md` › Q-D2-ADS, Q-D2-ZOOM).

| Visiertyp | Name | Augenabstand | gemessen ab | Visierbonus | Ziel: Öffnung in % der Bildbreite | Zielbild |
|---|---|---|---|---|---|---|
| `reflex` | Reflex-/Holovisier | 110 mm | `Socket_Reticle` | +0.3 | 15–22 % | glass |
| `scope` | Zielfernrohr | 110 mm | `Socket_Objective` | +0.8 | 22–30 % | lens_picture |

| Waffentyp | Grundzoom | Status | Weltzoom Reflex | Weltzoom Zielfernrohr |
|---|---|---|---|---|
| `auto_rifle` | ×1.6 | beobachtet | ×1.9 | ×2.4 |
| `pulse_rifle` | ×1.7 | beobachtet | ×2.0 | ×2.5 |
| `scout_rifle` | ×2.1 | beobachtet | ×2.4 | ×2.9 |
| `hand_cannon` | ×1.5 | beobachtet | ×1.5 | ×1.5 |
| `sidearm` | ×1.25 | beobachtet | ×1.25 | ×1.25 |
| `submachine_gun` | ×1.25 | beobachtet | ×1.25 | ×1.25 |
| `shotgun` | ×1.25 | beobachtet | ×1.25 | ×1.25 |
| `grenade_launcher` | ×1.4 | beobachtet | ×1.4 | ×1.4 |
| `sniper_rifle` | ×5.5 | beobachtet | ×5.5 | ×5.5 |
| `fusion_rifle` | ×1.5 | entworfen | ×1.8 | ×2.3 |
| `linear_fusion_rifle` | ×3.0 | entworfen | ×3.3 | ×3.8 |
| `trace_rifle` | ×1.5 | entworfen | ×1.8 | ×2.3 |
| `rocket_launcher` | ×2.5 | entworfen | ×2.8 | ×3.3 |
| `machine_gun` | ×1.6 | entworfen | ×1.9 | ×2.4 |
| `combat_bow` | ×1.5 | entworfen | ×1.8 | ×2.3 |
| `sword` | ×1.0 | entworfen | ×1.3 | ×1.8 |
| `glaive` | ×1.25 | entworfen | ×1.55 | ×2.05 |

## Spieleroptionen

| Option | Name | Werte | Vorgabe |
|---|---|---|---|
| `kind` | Form | `ring_dot`, `dot`, `cross`, `chevron`, `t_post`, `circle_cross`, `corners` | Vorgabe der Waffe |
| `color` | Farbe | `cyan`, `red`, `green`, `amber`, `white` | cyan |
| `weight` | Linienstärke | `fine`, `normal`, `bold` | normal |
| `scale` | Größe | 0.6 – 1.6 | 1.0 |
| `opacity` | Deckkraft | 0.3 – 1.0 | 0.9 |
| `center_dot` | Mittelpunkt | `True`, `False` | True |
| `spread` | Aufgehen beim Schießen | `True`, `False` | True |
| `glass` | Glas | `clean`, `dust`, `scratch`, `crack`, `cells`, `worn` | clean |
