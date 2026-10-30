# Klassenwerte für den Ego-Übertrag (0.33 „Armory“)

Sammlung der an Destiny 2 gemessenen bzw. belegten Werte je Waffenklasse für `basic/arms/ego.py › CLASSES`, gelesen am 30.10.2026
aus Motiongen (`~/Claude/cubeescape-reference/docs/`, Stand `4fa6f27`) und BALLON (`basic/reticles.py`). Herkunft: **M** am Bild
gemessen, **S** Sekundärquelle (Menükarte, Manifest), **E** keine Messung (Entwurf, Zeile in der Entscheidungsliste). Bilder immer
bei 60/s (B60). Messungen sind Beispiele einer Waffe, kein Klassenmittel; Exoten nur als Typbeleg.

Fundstellen: D2 = `destiny2.md`, WW = `waffenwerte.md`, NL = `nachladen.md`, WE = `wechsel.md`, RS = `rueckstoss.md`,
MU = `muendung.md`, HU = `huefte.md`, ZB = `zielbewegung.md` (alle unter `cubeescape-reference/docs/`), RT = `basic/reticles.py`.

Umrechnung wie die bisherigen Klassen: ADS-Anflug „erste Bewegung → Ruhe“ bei 60/s → Bilder bei 30/s mit dem Zielen-Nachlauf
(MP: 8–12 B60 → 3, Automatik 20 B60 → 10); Abläufe (Nachladen, Ziehen) × `TIME_SCALE` 1,25.

## Feuerarten (Spec `META.fire`)

| Klasse | META fire | im Spiel (0.33) |
|---|---|---|
| hand_cannon | `semi_auto_double_action` | Einzelfeuer (`ego.FIRE_ALIAS`), Hahn als Live-Teil — **P1 erledigt** |
| sidearm | `semi_auto` | Einzelfeuer — **P1 erledigt** |
| combat_bow | `draw_release` | offen: Spannen, Halten, Lösen (eigene Feuerart in Unity) |
| shotgun | `pump_action` | offen: Einzelschuss + Pumpen, Einzelladen je Patrone |
| sniper_rifle | `bolt_action` | offen: Einzelschuss + Kammerstängel |
| fusion_rifle | `charge_burst` | offen: Aufladen, dann Salve 5–6 Strahlen |
| linear_fusion_rifle | `charge_single` | offen: Aufladen, ein Schuss |
| trace_rifle | `continuous_beam` | offen: Dauerstrahl |
| grenade_launcher | `single_shot` | offen: Einzelschuss, Nachladen nach jedem Schuss (Kipplauf) |
| rocket_launcher | `single_shot` | offen: Einzelschuss, Nachladen nach jedem Schuss |
| machine_gun | `full_auto_belt` | offen: Dauerfeuer (Alias `full_auto` möglich), Gurtkasten-Nachladen |

## Werte je Klasse

| Klasse | Kadenz / Magazin | ADS ein / aus | Hüfte (Mündung % B/H) | Sprint | Nachladen | Ziehen | Rückstoß, Blitz, Hülse |
|---|---|---|---|---|---|---|---|
| hand_cannon | 140/min, 10 [S] Annual Skate (WW:283, D2:94); Abstand 27 B60 ≈ 133/min (D2:94) | 10 B60 / 9–10 B60 [M] Last Word (D2:584) | 57/63 Annual Skate (HU:52), 54/69 (HU:60); Körper 53–70 × 59–84 (HU:170) | [M] senkrecht, Lauf am oberen Rand, Körper 62–70 % B (D2:562); Hub 13 % H / 4 % B, 3,16 Hz (D2:467) | 1,0 s: Hochdrehen 0,13, Trommel 0,62, Schließen 0,2; Zähler ≈ 70 % (D2:492) | 16 B60 + 19 bis ruhig (WE:51) | Netto 1,7 pp H/Schuss, Hochimpuls 7,6 (RS:106); Modell 6 % hoch, 8° (D2:492); Blitz Hüfte 28 × 42 % (MU:91); Hülse nicht sichtbar |
| sidearm | kein Einzelfeuer-Wert; Manifest 260–491/min, 12–30 (WW:332-340) | 6–7 B60 Rattler, 12 Brass (D2:585/269) / Zoom 7 B60 | 57/64 (HU:53), 59/67 (HU:65), 58/68 (D2:507) | keine Messung (D2:563) | 1,1–1,2 s (D2:491) | 12 B60 + 16 (WE:52) | Welt bis 9,8 pp H netto (RS:107); Blitz 14 × 20 % (MU:92) |
| combat_bow | Ziehzeit 612 ms [S]; Anlegen → voll ≈ 0,60 s, Lösen → Lösen 1,45 s [M] (D2:270); PvE Lösen → gespannt 0,60 s (D2:230) | Spannen statt ADS: 4 B60 bis senkrecht, ≈ 0,10 s ruhig (D2:587); ADS gespannt 0,25 s (D2:270/508) | Visier 57,3/75,2 Imperial Needle (HU:74), 58,2/78 (HU:75); quer von links unten (D2:498) | tief rechts [O] (D2:565) | kein Magazin; Halten 0,75 s ruhig (ZB:79); Spann-Reset ohne Schuss 0,150 s (D2:498); perfekter Zug keine Messung | 6–8 B60 bis hüftähnlich (WE:48/50) | Wurfarme-Ruck, Bogen kippt ≈ 15 % (D2:498); ADS-Lösen Ring 30 pp nach unten (D2:508); kein Blitz, keine Hülse |
| shotgun | 80/min, 7 Hawthorne; 55/min, 5 Baligant [S] (D2:258-259); Pump vor dem 2. Schuss (D2:495) | ≈ 13 B60 FILO (D2:588) / 6–8 B60 | 57/63 FILO (HU:54), ≈ 58/66 (D2:495) | keine Messung (D2:566) | Einzelladen 0,617–0,633 s je Patrone Hawthorne (NL:52), 0,850–0,867 Baligant (NL:53); erste 0,57–0,60 s nach Beginn, einmal Repetieren am Ende (NL:109) | 14 B60 (WE:47) | Ring 1–2 B ≈ 3 % hoch, 0,10 s zurück (D2:495); Blitz ADS 30 × 45 % (MU:94); Hülse beim Pumpen 0,63 s nach dem Schuss rechts (D2:495) |
| sniper_rifle | 90/min, 4 Far Future; 90/min, 5 A Single Clap [S] (D2:260/262) | 14 B60 Far Future bis stabil (6 Hochziehen + 10 Overlay) (D2:496) / 0,17–0,25 s, Linse zuerst | 56/68 (HU:51), 56/66 (HU:61), 56/64 (D2:496) | tief rechts [O] (D2:567) | Far Future: MagOut +0,28, MagIn +0,70, Kammerstängel +1,2, Hüfte 2,07, ruhig 2,18 s (NL:58) | – | ADS Welt ≈ 18 pp H in 4 B, Rest 12 (ZB:73); Blitz Hüfte 2 B 14 × 35 %, im Scope aus (MU:87); **Weltzoom ≈ 4× gegen CLASS_ZOOM 5,5** (D2:496) |
| fusion_rifle | Laden 500 ms, 7 Cartesian; 860 ms, 5 Shock and Awe [S]; gemessen 0,517 / 0,867 s [M] (D2:254/499); Salve 5–6 Strahlen in 0,25 s | 0,083 s Achse, 0,117 s ruhig (D2:499) | 59/68 (HU:57), 58/66 (D2:499) | groß und tief [O] (D2:568) | Batterie: bis Hüfte 1,72–1,77 s, ruhig 1,92 (NL:54); löst +0,32, sitzt +1,0 s | keine Messung | Waffe ruhig, Mündung steigt bis ≈ 52/55; Ladehaltung zieht 8 % zur Mitte in 0,25 s (D2:254/499) |
| linear_fusion_rifle | Laden 563 ms, 5 Threaded Needle [S] (D2:274); sichtbar 20 B60 [M] | 17 B60 (D2:591) / 0,32 s (D2:274) | 58/69 (HU:69), 58/68 (HU:70), 59/56 (D2:511) | keine Messung (D2:569) | MagIn +1,53 s, ruhig 3,30 s (NL:61) | 24 B60 + 23 (WE:57) | 6,5 pp H/Schuss (RS:111); ADS Welt 13 pp nach 8 B (ZB:75); Weltzoom offen (Kandidat 3,0×, ZB:106-107) |
| trace_rifle | 1000/min, 94 Retraced Path [S] (WW:363) | ≈ 12 B60 Prometheus Lens (D2:592) / keine Messung | 57/60 (D2:512), 57,7/59,6 (HU:78) | keine Messung (D2:570) | ≈ 1,6 s bis Hüfte, 2,55 ruhig, „kein Klassenwert“ (D2:512) | keine Messung | kein Rückstoß (D2:500/512) |
| grenade_launcher | 90/min, 1 [S] (D2:271-272) | ≈ 12 B60 (D2:593), 19 B60 (D2:271) / keine Messung | ≈ 57/54, ≈ 58/67 (D2:509), 56/63 (HU:68) | keine Messung (D2:571) | nach jedem Schuss ≈ 2,5 s: Granate ein +0,69, Schließen +1,17, Hüfte +2,42, ruhig +2,52 (D2:271/509) | – | schlägt hoch zur Kamera, Rückkehr ≈ 0,6 s; ADS Visier +2,6 %, 0,43 s (D2:509) |
| rocket_launcher | 20/min, 1 [S] (D2:276) | 14 B60 (D2:594) / keine Messung | ≈ 60/40 (D2:501); Visier 65/68, 68/57 (HU:56/71) | keine Messung (D2:572) | ≈ 2,8 s Eyes of Tomorrow (D2:276/513) | 0,18 s Hüfte (D2:481) | Schub zur Kamera, Linse 10 → 25 % H in 3–4 B (D2:501); Weißblende 0,10–0,15 s |
| machine_gun | 900/min, 75 Shattered Cipher [M/S] (D2:273) | 20 B60 (D2:583) / keine Messung | 56,2/64 (HU:72), ≈ 56/54 (D2:510) | keine Messung (D2:561) | Gurtkasten 4,40 s bis Hüfte, 4,87 ruhig: Deckel +0,63, Kasten +1,32, Gurt +1,70, Deckel zu +2,78 (NL:60) | 18 B60 + 37 (WE:56) | Hüfte 2,8 pp, ADS bis 12,4 pp über mehrere Stöße (RS:110); Blitz ADS 2 B 25 × 35 % (MU:93); Hülse im 1. Blitzbild |

Weltzoom (`RT.CLASS_ZOOM`) und Hüft-Fadenkreuz (`RT.HIP`) stehen in `basic/reticles.py`; Abweichungen zu Motiongen: Scharfschütze 5,5
gegen ≈ 4×, lineare Fusion 3,8 gegen „offen“, Bogen 1,8 gegen 2,2×, Raketenwerfer nicht messbar; Hüftzeichen lineare Fusion 4,5 % H
gegen 12–13 % H, Raketenwerfer `circle_cross` gegen „kein Hüftzeichen“ (D2:606-616).

## Offen für die Entscheidungsliste

1. Feuerarten der Sonderklassen (Tabelle oben): je Klasse eine Feuerart in Unity mit eigener Aktion (Pumpen, Spannen/Halten/Lösen,
   Aufladen, Dauerstrahl, Einzelschuss mit Nachladen nach jedem Schuss).
2. Taktisch gegen leer: bei Destiny nirgends gemessen; Marker MagOut/MagIn nur bei Scharfschütze, linearer Fusion, Granatwerfer,
   Batterie und MG.
3. Sprint-Haltung nur bei der Handfeuerwaffe gemessen; Bogen, Scharfschütze, Fusion nur beobachtet [O]; übrige offen.
4. Seitenwaffe Kadenz/Magazin (0.33: 360/min, 15 E), Handfeuerwaffe Kick (0.33: 2,5 E), Hülsen der Trommel beim Auswerfen (0.33 nicht
   dargestellt).
5. Ohne Messung: perfekter Zug des Bogens, Mündungsfeuer-Dauer bei Handfeuerwaffe, Seitenwaffe, Fusion, Spur, Granatwerfer; ADS aus bei
   Granatwerfer, Raketenwerfer, Spur, MG; legendäres Raketen-Nachladen.
