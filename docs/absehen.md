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
| `brackets` | Klammern | Zwei eckige Klammern um einen Punkt; Klammern wandern seitlich nach außen | ja |
| `caret` | Dach | Kleines „^“, Spitze am Zielpunkt; die Schenkel gehen seitlich auseinander | ja |

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
| `clean` | Klar | unbehandelt beschichtet, Tönung ≤ 5 % |
| `dust` | Staub | feine Körner (~0,3 mm), jede siebte Zelle |
| `scratch` | Kratzer | dünne, schräg gestreckte Linien |
| `crack` | Riss | feines Rissnetz, nur obere Ecke |
| `cells` | Zellen | kaum sichtbare Zellvergütung über die Scheibe |
| `worn` | Benutzt | Staub und Kratzer |

## Aufgehen beim Schießen

Spreizung s in mm auf der Scheibe (Größe 1,0): Abklingen zur Basis mit Zeitkonstante, Impuls je Schuss bis zum Maximum, Laufen addiert, Zielen multipliziert.

| Profil | Name | Basis | je Schuss | Maximum | Abklingen | Laufen | Zielen |
|---|---|---|---|---|---|---|---|
| `auto` | Dauerfeuer | 0.0 | 0.9 | 5.0 | 0.28 s | 1.5 | ×0.0 |
| `burst` | Salve | 0.0 | 1.2 | 4.5 | 0.22 s | 1.4 | ×0.0 |
| `precision` | Präzision | 0.0 | 2.2 | 3.5 | 0.18 s | 1.0 | ×0.0 |
| `shotgun` | Schrot | 2.0 | 2.5 | 6.0 | 0.35 s | 1.0 | ×0.0 |
| `charge` | Aufladen | 0.0 | 1.5 | 4.0 | 0.25 s | 1.2 | ×0.0 |
| `explosive` | Sprengwaffe | 0.5 | 1.8 | 4.0 | 0.5 s | 0.8 | ×0.0 |
| `none` | kein Aufgehen | 0.0 | 0.0 | 0.0 | 0.2 s | 0.0 | ×0.0 |

Profil `charge`: während des Aufladens schrumpft die Spreizung von `charge_from` auf die Basis.

## Vorgabe je Waffentyp

| Typ | Visier | Hüfte | Aufgehen |
|---|---|---|---|
| `auto_rifle` | `ring_dot` | `ring_dot` | `auto` |
| `pulse_rifle` | `circle_cross` | `ring_dot` | `burst` |
| `scout_rifle` | `chevron` | `cross` | `precision` |
| `hand_cannon` | `dot` | `brackets` | `precision` |
| `sidearm` | `dot` | `cross` | `auto` |
| `submachine_gun` | `dot` | `circle_cross` | `auto` |
| `shotgun` | `corners` | `corners` | `shotgun` |
| `sniper_rifle` | `t_post` | `caret` | `precision` |
| `fusion_rifle` | `t_post` | `corners` | `charge` |
| `linear_fusion_rifle` | `t_post` | `cross` | `charge` |
| `trace_rifle` | `corners` | `circle_cross` | `auto` |
| `grenade_launcher` | `chevron` | `circle_cross` | `explosive` |
| `rocket_launcher` | `circle_cross` | `circle_cross` | `explosive` |
| `machine_gun` | `circle_cross` | `ring_dot` | `auto` |
| `combat_bow` | `dot` | `chevron` | `charge` |
| `sword` | – | `dot` | `none` |
| `glaive` | – | `cross` | `auto` |

## Hüft-Fadenkreuz

Nur in der Hüfte sichtbar, weiß, Linienstärke fein (Linien mindestens 1.2 px breit). Aus bei: ads, sprint, reload, draw, holster, inspect, lowered – beim Zielen schon im ersten Bild. Beim Schießen geht es nach dem Aufgehprofil auf; die Sprintform geht nicht auf. Größe = Außenmaß der Form bei Spreizung 0 (größere Seite des Rahmens um Linienmitten, Ringe und Punkte) als Anteil der Bildhöhe; Glidepath = Motiongen `destiny2.md` › Glidepath. Entscheidungsliste 4.1 A und 4.2 A.

| Typ | Hüfte | Größe (% H) | Außenmaß | Status | Sprint |
|---|---|---|---|---|---|
| `auto_rifle` | `ring_dot` | 3.2 | 6.4 mm | gemessen (Glidepath) | `caret` 1.5 % H |
| `pulse_rifle` | `ring_dot` | 3.2 | 6.4 mm | übertragen (Automatik) | aus |
| `scout_rifle` | `cross` | 4.5 | 14 mm | entworfen | aus |
| `hand_cannon` | `brackets` | 6.0 | 10 mm | gemessen (Glidepath, ≈ 6 % H) | aus |
| `sidearm` | `cross` | 4.5 | 14 mm | entworfen | aus |
| `submachine_gun` | `circle_cross` | 6.1 | 14.8 mm | gemessen (Glidepath, 5,9–6,3 % H) | aus |
| `shotgun` | `corners` | 4.5 | 10 mm | entworfen | aus |
| `sniper_rifle` | `caret` | 1.0 | 4 mm | gemessen (Glidepath, ≈ 1 % H) | aus |
| `fusion_rifle` | `corners` | 4.5 | 10 mm | entworfen | aus |
| `linear_fusion_rifle` | `cross` | 4.5 | 14 mm | entworfen | aus |
| `trace_rifle` | `circle_cross` | 4.5 | 14.8 mm | entworfen | aus |
| `grenade_launcher` | `circle_cross` | 4.5 | 14.8 mm | entworfen | aus |
| `rocket_launcher` | `circle_cross` | 4.5 | 14.8 mm | entworfen | aus |
| `machine_gun` | `ring_dot` | 3.2 | 6.4 mm | übertragen (Automatik) | aus |
| `combat_bow` | `chevron` | 4.5 | 6.4 mm | entworfen | aus |
| `sword` | `dot` | 4.5 | 2 mm | entworfen | aus |
| `glaive` | `cross` | 4.5 | 14 mm | entworfen | aus |

## Visier-Standard

Visierhöhe (Socket_Eye über der Laufachse) 66 ± 4 mm. Socket_Eye ist der Augenpunkt beim Zielen, gemessen ab der vorderen Visieröffnung. Das Waffenmodell wird nicht vergrößert (Viewmodel-Zoom ×1.0); nur die Welt zoomt (Bildmaßstab: tan(Bildwinkel/2) geteilt durch den Zoom), Bezugsbildwinkel 75° horizontal. Eine Kamera: das Glas zeigt dasselbe Weltbild; Teile mit `ads_hide` (Zielfernrohr-Rohr, Okular, Türme) sind beim Zielen ausgeblendet. Geprüft in `./check`. Herleitung: Destiny-Video, Motiongen-Messungen und REF 0.14 „Eyebox“ (`cubeescape-reference/docs/visiere.md`).

| Visiertyp | Name | Augenabstand | gemessen ab | Visierbonus | Öffnung im Zielen (% Bildbreite) | Rahmen höchstens | Zielbild |
|---|---|---|---|---|---|---|---|
| `reflex` | Reflex-/Holovisier | 90 mm | `Socket_Reticle` | +0.3 | 12–20 % | 0.1 × Öffnung | glass |
| `scope` | Zielfernrohr | 90 mm | `Socket_Objective` | +0.8 | 20–26 % | 0.15 × Öffnung | glass |
| `fullscreen` | Vollbild (Scharfschütze) | – | – | – | – | – | overlay: eigene Kontur je Waffe, außen schwarz |

Weltzoom der Klasse = Grundzoom + Bonus des Visiers, das der Typ trägt (fett); 1.2 A: Scout, Handfeuerwaffe und MP nach Glidepath.

| Waffentyp | Visier (Visier-Standard 3) | Grundzoom | Status | Weltzoom Reflex | Weltzoom Zielfernrohr |
|---|---|---|---|---|---|
| `auto_rifle` | offenes Holo (abgerundetes Rechteck) | ×1.6 | beobachtet | **×1.9** | ×2.4 |
| `pulse_rifle` | offenes Holo (abgerundetes Rechteck) | ×1.7 | beobachtet | **×2.0** | ×2.5 |
| `scout_rifle` | kurzes Ring-Zielfernrohr auf Trapezhals | ×1.2 | gemessen (Glidepath) | ×1.5 | **×2.0** |
| `hand_cannon` | Kimme und Korn mit leuchtenden Klammern | ×1.15 | gemessen (Glidepath) | **×1.15** | ×1.15 |
| `sidearm` | Kimme und Korn mit leuchtenden Klammern | ×1.25 | beobachtet | **×1.25** | ×1.25 |
| `submachine_gun` | offenes Holo (abgerundetes Rechteck) | ×1.45 | gemessen (Glidepath) | **×1.45** | ×1.45 |
| `shotgun` | Kimme und Korn mit leuchtenden Klammern | ×1.25 | beobachtet | **×1.25** | ×1.25 |
| `grenade_launcher` | runde Linse mit Winkel | ×1.4 | beobachtet | **×1.4** | ×1.4 |
| `sniper_rifle` | Zielfernrohr außen, im Zielen Vollbild | ×5.5 | beobachtet | **×5.5** | ×5.5 |
| `fusion_rifle` | Ring oder Doppelring | ×1.5 | entworfen | **×1.8** | ×2.3 |
| `linear_fusion_rifle` | kurzes Ring-Zielfernrohr auf Trapezhals | ×3.0 | entworfen | ×3.3 | **×3.8** |
| `trace_rifle` | offenes Holo (abgerundetes Rechteck) | ×1.5 | entworfen | **×1.8** | ×2.3 |
| `rocket_launcher` | runde Linse mit Winkel | ×2.5 | entworfen | **×2.8** | ×3.3 |
| `machine_gun` | offenes Holo (abgerundetes Rechteck) | ×1.6 | entworfen | **×1.9** | ×2.4 |
| `combat_bow` | Pfeilspitze, kein Visier | ×1.5 | entworfen | **×1.8** | ×2.3 |
| `sword` | kein Visier | ×1.0 | entworfen | **×1.3** | ×1.8 |
| `glaive` | kein Visier | ×1.25 | entworfen | **×1.55** | ×2.05 |

Im Zielen: Leuchtpunkt am Zielpunkt getrennt vom Glas (1.1 % Bildhöhe), kein Aufgehen (×0.0), Schuss = kurzer Ring (2 % Höhe, 1 Bild), Treffer = X (4.5 % Höhe, ≥ 0.17 s).

## Spieleroptionen

| Option | Name | Werte | Vorgabe |
|---|---|---|---|
| `kind` | Form | `ring_dot`, `dot`, `cross`, `chevron`, `t_post`, `circle_cross`, `corners`, `brackets`, `caret` | Vorgabe der Waffe |
| `color` | Farbe | `cyan`, `red`, `green`, `amber`, `white` | cyan |
| `weight` | Linienstärke | `fine`, `normal`, `bold` | fine |
| `scale` | Größe | 0.6 – 1.6 | 1.0 |
| `opacity` | Deckkraft | 0.3 – 1.0 | 0.9 |
| `center_dot` | Mittelpunkt | `True`, `False` | True |
| `spread` | Aufgehen beim Schießen | `True`, `False` | True |
| `glass` | Glas | `clean`, `dust`, `scratch`, `crack`, `cells`, `worn` | clean |
| `ads_eye_relief` | Visiernähe beim Zielen (mm) | `70`, `90`, `110` | 90 |
