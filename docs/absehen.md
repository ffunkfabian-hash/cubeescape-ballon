# Absehen, Visierglas und Visier-Standard

> Erzeugt aus `basic/reticles.py` mit `python3 tools/export_reticles.py` – nicht von Hand ändern.

Eine Quelle für Blender (`basic/common.drawn_reticle`, Visier-Baukasten v3 in `basic/common.py`; `reticle()` für Katalogblätter) und die Laufzeit (`data/reticles.json`). Katalogblatt: `python3 tools/reticle_sheet.py --sheet` (Belege `reticles.png`, Clip `clips/reticle_spread.mp4`).

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
| `arcs_ladder` | Bögen mit Leiter | Zwei offene Bögen gehen seitlich auf; drei Striche darunter als Fallmarken | ja |
| `ring_corners` | Ring mit Eckmarken | Kleiner Ring in der Mitte, vier Eckwinkel gehen diagonal auf | ja |
| `gl_brackets` | Werferklammern | Zwei Eckklammern gehen seitlich auf; Mittenstrich und tieferer Strich als Fallmarke | ja |
| `none` | ohne | Kein Hüftzeichen (Raketenwerfer, Destiny) | nein |

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
| `portal_cannon` | – | `ring_dot` | `none` |

## Hüft-Fadenkreuz

Nur in der Hüfte sichtbar, weiß, Linienstärke fein (Linien mindestens 1.2 px breit). Aus bei: ads, sprint, reload, draw, holster, inspect, lowered – beim Zielen schon im ersten Bild. Beim Schießen geht es nach dem Aufgehprofil auf; die Sprintform geht nicht auf. Größe = sichtbares Außenmaß der Form bei Spreizung 0 mit Linienstärke (größere Seite des Rahmens) als Anteil der Bildhöhe; Glidepath = Motiongen `destiny2.md` › Glidepath. Entscheidungsliste 4.1 A und 4.2 A. Sonderklassen (0.33 „Armory“, `reticles.HUD_HIP`): das HUD zeigt die gemessene Glidepath-Form, das gezeichnete Absehen im Visierglas behält die Form der Spalte „Glas“ (Teil des Waffenmodells).

| Typ | Hüfte (HUD) | Größe (% H) | Außenmaß | Status | Sprint | Glas |
|---|---|---|---|---|---|---|
| `auto_rifle` | `ring_dot` | 3.2 | 5.91 mm | gemessen (Glidepath) | `caret` 1.5 % H | wie Hüfte |
| `pulse_rifle` | `ring_dot` | 3.2 | 5.91 mm | übertragen (Automatik) | aus | wie Hüfte |
| `scout_rifle` | `cross` | 4.5 | 14.39 mm | entworfen | aus | wie Hüfte |
| `hand_cannon` | `brackets` | 6.0 | 10.39 mm | gemessen (Glidepath, ≈ 6 % H) | aus | wie Hüfte |
| `sidearm` | `cross` | 4.5 | 14.39 mm | entworfen | aus | wie Hüfte |
| `submachine_gun` | `circle_cross` | 6.1 | 15.19 mm | gemessen (Glidepath, 5,9–6,3 % H) | aus | wie Hüfte |
| `shotgun` | `corners` | 4.5 | 10.39 mm | entworfen | aus | wie Hüfte |
| `sniper_rifle` | `caret` | 1.0 | 4.39 mm | gemessen (Glidepath, ≈ 1 % H) | aus | wie Hüfte |
| `fusion_rifle` | `ring_corners` | 5.5 | 10.39 mm | gemessen (Glidepath, Quadrat 5,5 % H, Ring Ø 1,7 % H) | aus | `corners` 4.5 % H |
| `linear_fusion_rifle` | `ring_corners` | 12.5 | 10.39 mm | gemessen (Glidepath, 12–13 % H) | aus | `cross` 4.5 % H |
| `trace_rifle` | `circle_cross` | 4.5 | 15.19 mm | entworfen | aus | wie Hüfte |
| `grenade_launcher` | `gl_brackets` | 11.2 | 10.39 mm | gemessen (Glidepath, 6,3 % B × 5,6 % H = 11,2 × 5,6 % H) | aus | `circle_cross` 4.5 % H |
| `rocket_launcher` | `none` | 0.0 | 0 mm | gemessen (Glidepath, kein Mittenzeichen, 1 Clip) | aus | `circle_cross` 4.5 % H |
| `machine_gun` | `ring_dot` | 3.2 | 5.91 mm | übertragen (Automatik) | aus | wie Hüfte |
| `combat_bow` | `arcs_ladder` | 4.6 | 8.05 mm | gemessen (Glidepath, Ø 4,6 % H) | aus | `chevron` 4.5 % H |
| `sword` | `dot` | 4.5 | 1.65 mm | entworfen | aus | wie Hüfte |
| `glaive` | `cross` | 4.5 | 14.39 mm | entworfen | aus | wie Hüfte |
| `portal_cannon` | `ring_dot` | 4.5 | 5.91 mm | entworfen (Werkzeug, Portal 2 / Cube Escape) | aus | wie Hüfte |

## Visier-Standard

Visierhöhe (Socket_Eye über der Laufachse) 66 ± 4 mm. Socket_Eye ist der Augenpunkt beim Zielen, gemessen ab der vorderen Visieröffnung. Das Waffenmodell wird nicht vergrößert (Viewmodel-Zoom ×1.0); nur die Welt zoomt (Bildmaßstab: tan(Bildwinkel/2) geteilt durch den Zoom), Bezugsbildwinkel 75° horizontal. Eine Kamera: das Glas zeigt dasselbe Weltbild; Teile mit `ads_hide` (Zielfernrohr-Rohr, Okular, Türme) sind beim Zielen ausgeblendet. Geprüft in `./check`. Herleitung: Destiny-Video, Motiongen-Messungen und REF 0.14 „Eyebox“ (`cubeescape-reference/docs/visiere.md`).

| Visiertyp | Name | Augenabstand | gemessen ab | Visierbonus | Öffnung im Zielen (% Bildbreite) | Rahmen höchstens | Zielbild |
|---|---|---|---|---|---|---|---|
| `reflex` | Reflex-/Holovisier | 90 mm | `Socket_Reticle` | +0.3 | 12–20 % | 0.1 × Öffnung | glass |
| `scope` | Zielfernrohr | 90 mm | `Socket_Objective` | +0.8 | 20–26 % | 0.15 × Öffnung | glass |
| `fullscreen` | Vollbild (Scharfschütze) | – | – | – | – | – | overlay: eigene Kontur je Waffe, außen schwarz |
| `pins` | Pinvisier (Bogen) | Ankerpunkt bei vollem Auszug | `Socket_Reticle` | +0.0 | 4–7 % (lichter Ring, entworfen) | 0.1 × Öffnung | Pins ≥ 3 px, Abstand ≥ 0.6° |

**Erweiterung 0.21 „Ironsight“** (Nutzerwahl 26.10.2026, `docs/visier-konzept.md` › 7): Visierlinie über der Schienenoberkante (BRI-22) – Holo auf der H0-Plattform + 26 mm (Visierhöhe gilt; Zielfernrohre nach Konzept A mit zwei Schienen auf eigener Höhe richten sich nur nach der Visierhöhe), Mini-Reflex + 15 mm (hand_cannon, sidearm), Kimme/Korn + 11 mm (hand_cannon, sidearm, shotgun); für die beiden letzten gilt die Visierhöhe 66 ± 4 mm nicht. Zielfernrohre sitzen nach Konzept A: Sattel hinter dem Auge, Klemmfuß unter dem Objektiv, Ring ohne Wulst (außen/innen 1,29). Öffnung im Zielen = lichte Öffnung (Scheibe bzw. Objektivlinse) im echten Abstand zum Augenpunkt.

| Visiertyp | zugelassene Variante | Öffnung im Zielen | nur an |
|---|---|---|---|
| `reflex` | Holo L (Größe L) | 20–25 % | `machine_gun`, `grenade_launcher`, `rocket_launcher` |
| `scope` | Zielfernrohr S (Größe S) | 17–20 % | `scout_rifle`, `linear_fusion_rifle`, `pulse_rifle` |

Absehen gezeichnet: Hüftform der Klasse, flach in der Glasebene, reine Emission; Linien mindestens 1.6 px bei 1280 px Bildbreite (75°), Ebene höchstens 0.5 mm neben der Scheibe (`common.drawn_reticle`; Unity zeichnet es selbst). Geprüft in `tools/test_sights.py` und `tools/test_sight_seat.py`.

Weltzoom der Klasse = Grundzoom + Bonus des Visiers, das der Typ trägt (fett); 1.2 A: Scout, Handfeuerwaffe und MP nach Glidepath. Der Bogen (Visiertyp `pins`) nutzt bis zum Ego-Übertrag den Reflexbonus (`reticles.sight_type`), weil die Zoomtabelle in Unitys ego.json steht; Referenz Imperial Needle ≈ 2,2× (cubeescape-reference, REF 0.17).

| Waffentyp | Visier (Visier-Standard 3) | Grundzoom | Status | Weltzoom Reflex | Weltzoom Zielfernrohr |
|---|---|---|---|---|---|
| `auto_rifle` | offenes Holo (abgerundetes Rechteck) | ×1.6 | beobachtet | **×1.9** | ×2.4 |
| `pulse_rifle` | offenes Holo (abgerundetes Rechteck) | ×1.7 | beobachtet | **×2.0** | ×2.5 |
| `scout_rifle` | kurzes Ring-Zielfernrohr, Sattel hinter dem Auge, Fuß unter dem Objektiv | ×1.2 | gemessen (Glidepath) | ×1.5 | **×2.0** |
| `hand_cannon` | Kimme und Korn mit leuchtenden Klammern | ×1.15 | gemessen (Glidepath) | **×1.15** | ×1.15 |
| `sidearm` | Kimme und Korn mit leuchtenden Klammern | ×1.25 | beobachtet | **×1.25** | ×1.25 |
| `submachine_gun` | offenes Holo (abgerundetes Rechteck) | ×1.45 | gemessen (Glidepath) | **×1.45** | ×1.45 |
| `shotgun` | Kimme und Korn mit leuchtenden Klammern | ×1.25 | beobachtet | **×1.25** | ×1.25 |
| `grenade_launcher` | runde Linse mit Winkel | ×1.4 | beobachtet | **×1.4** | ×1.4 |
| `sniper_rifle` | Zielfernrohr außen, im Zielen Vollbild | ×4.0 | beobachtet | **×4.0** | ×4.0 |
| `fusion_rifle` | Ring oder Doppelring | ×1.5 | entworfen | **×1.8** | ×2.3 |
| `linear_fusion_rifle` | kurzes Ring-Zielfernrohr, Sattel hinter dem Auge, Fuß unter dem Objektiv | ×3.0 | entworfen | ×3.3 | **×3.8** |
| `trace_rifle` | offenes Holo (abgerundetes Rechteck) | ×1.5 | entworfen | **×1.8** | ×2.3 |
| `rocket_launcher` | runde Linse mit Winkel | ×2.5 | entworfen | **×2.8** | ×3.3 |
| `machine_gun` | offenes Holo (abgerundetes Rechteck) | ×1.6 | entworfen | **×1.9** | ×2.4 |
| `combat_bow` | Pinvisier: drei Leuchtpins im Ring (B1) | ×1.9 | entworfen | **×2.2** | ×2.7 |
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
