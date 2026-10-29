# BASIC-Designvertrag

> Stil v2 (Destiny-Detaildichte, AAA-Material, Farb-/Texturvarianten) ergänzt diesen Vertrag: [stilhandbuch.md](stilhandbuch.md).

Stand 24.10.2026 (0.1.0). Gilt für alle 17 BASIC-Entwürfe. Umsetzung im Code: Radien und Bausteine `basic/common.py`,
Materialrollen `basic/kit.py › MATERIALS`. Dieser Vertrag beschreibt Gestaltungsregeln, keinen Datenvertrag mit Toolgen.

## Ziel

Industriell gefertigte Science-Fiction-Ausrüstung: schlicht, funktional, gut lesbar. Qualität kommt aus Proportion, Konstruktion,
sauberen Anschlüssen und klaren Baugruppen – nicht aus Detail- oder Polygonzahl.

## Grundformen und Proportion

| Regel | Festlegung |
|---|---|
| Hauptkörper | Seitenprofile mit geraden Kanten und wenigen Schrägen (Gehäuse, Schaft, Handschutz); Rohre nur, wo die Funktion rund ist (Lauf, Fokusrohr, Abschussrohr, Trommel) |
| Silhouette | Jede Klasse hat ein eigenes Leitmerkmal (Tabelle unten); geprüft als schwarze Silhouette im gleichen Maßstab |
| Gehäuseteilung | Gewehrfamilie: Oberes und Unteres Gehäuse, Fuge 1 mm; das Untere ist 2 mm schmaler (sichtbare Stufe) |
| Laufachse | liegt im oberen Drittel des Gehäuses; Visierlinie 60–80 mm darüber (Familie v2.1: Visier-Standard 66 ± 4 mm, [absehen.md](absehen.md)) |
| Länge | Bezug Toolgen-/Formgen-Länge je Typ (Abweichungen begründet in der Abdeckungsmatrix) |

## Radien, Fasen, Fugen

| Stufe | Radius (Bevel, 2 Segmente, Winkelgrenze 30°) | Einsatz |
|---|---|---|
| R_BODY | 5,0 mm | Gehäuse, Schaft, Handschutz, Griff |
| R_MID | 3,0 mm | Magazine, Zellen, Visierkörper |
| R_SMALL | 1,5 mm | Ringe, Schienen, Klemmfüße |
| R_FINE | 0,8 mm | Abzug, Hebel, Kimme/Korn |
| R_SOFT | 6,5 mm | nur Griffpolster (`rubber`), eine Stufe über dem harten Träger (Fase als Materialsignal, A5, Nutzer 29.10.2026); im Code seit 0.32 (`common.R_SOFT`) an jedem Griff in Gummi; dünne Polsterstreifen (Dicke < 3 × R_SOFT) behalten ihre Stufe |
| Fuge | 1,0 mm Abstand zwischen getrennten Schalen | Gehäuse/Handschutz, Ober-/Unterteil |

Toolgen setzt eigene Fasen (0,5–2 mm) auf importierte Netze (Formgen-Entscheidung 19.10.2026); die BASIC-Fasen sind Gestaltung
und werden bei einem Import bewertet (offen).

## Materialrollen und Farben

| Rolle | Farbe | Verwendung | Regel |
|---|---|---|---|
| `shell` | Creme `#D8CCB4` | Gehäuse, Schulterstütze S1, Rohre, Magazinkörper (Gewehr) | große ruhige Flächen |
| `graphite` | Graphit `#2C2E33` | **jede Handkontaktfläche** (Griff, Handschutz, Vordergriff, Stützgriff), Schaft S2, Visiergehäuse | Hand = Graphit |
| `dark_metal` | `#4A4E55` | Mündungen, Ringe, Schienen, Klemmungen, Zellen, Kühlflächen | Funktion = Metall |
| `metal` | `#8C9198` | Läufe, Abzug, Bolzen, Schneide | nur sichtbare Funktionsflächen |
| `accent` | Orange `#E0651E` | nur Bedienelemente (Ladehebel, Feuerwahl, Magazinhalter, Riegel, Nocke) und Munitionskennung | höchstens drei Bedienfunktionen je Waffe; ein beidseitiger Hebel (z. B. Feuerwahl links und rechts) zählt als eine |
| `energy` | Cyan `#5FD3E0` | nur Anzeigen (Munition, Ladung, Emitter, Leuchtpin) | klein, zurückhaltend, nie Dekor |
| `glass` | `#BFE3EA`, durchsichtig | Visiergläser | freie Durchsicht geprüft |

Abgleich mit der Cube-Escape-Palette (Creme, Graphit/Anthrazit, Metallgrau, sparsames Orange; Formgen-Variante G) ist eine
Ausgangsrichtung. Ein Abgleich mit dem Formgen-Texturkatalog `docs/textures/catalog.json` ist **offen**.

## Wiederkehrende Bauteile (Familienähnlichkeit, echte Schnittstellen)

| ID | Baustein | Waffen | Kompatibilität |
|---|---|---|---|
| BGM-1 | Griffmodul Gewehr (Griff 15°, Abzug, Bügel) | 01 02 03 06 08 09 10 11 12 13 14 15 17 | gleiche Funktion `grip_rifle`; Neigung je Waffe im Spec |
| BGM-P | Pistolengriff | 04 05 | eigene Form je Waffe |
| BRI-22 | Schiene 22 mm | alle Visierträger außer 04 05 07 16 17 (07 v2.1: kurze Schiene am Visierträger für B1, 0.29) | Visiere austauschbar, soweit Klemmfuß 50 mm auf die Schienenlänge passt (im Spec geprüft: `interfaces`) |
| Reflexvisier | Klemmfuß, Gehäuse, Haubenrahmen, Glas, Emitter | 01 02 06 08 10 12 13 14 15 | Fenster je Waffe (26 × 20 bis 44 × 30 mm) |
| Zielfernrohr | zwei Ringe, Okular, Mittelrohr, Objektiv, Turm | 03 09 11 | nur Präzisionswaffen (Formgen-Typregel 22.10.2026) |
| BST-1 Schaft S1 | Schaftrohr + Schulterstütze | 01 06 09 11 15 | Länge über Faktor `s` |
| BST-2 Schaft S2 | einteilig Graphit | 02 03 10 13 | Länge über Faktor `s` |
| BST-T Einteilkörper | Hinterkörper in Creme ohne Schaftrohr | 12 | nur Spurgewehr |
| BMW-R | Magazinschacht Gewehr | 01 02 03 09 | Magazine **nicht** zwischen Waffen getauscht (Maße je Waffe) |
| BEC-1 | Energiezelle | 10 11 12 17 | Zellmaße je Waffe verschieden; kein Austausch behauptet |

Ähnlichkeit macht Teile nicht austauschbar: Austausch gilt nur, wo der Spec dieselbe Schnittstelle **und** dieselben Maße zeigt.

## Leitmerkmal je Klasse

01 langes Gehäuse + Graphit-Handschutz · 02 zweigeteilte Impulskammer, Salvenanzeigen, Schaft S2 · 03 schlankes Einteilgehäuse, kurzes Zielfernrohr, S2 ·
04 Trommel auf Kran, Unterlauf · 05 Schlitten · 06 Magazin im Griff, Vordergriff · 07 Compound-Bogen mit Rollen, Sichtfenster, Pinvisier links (v2.1, Nutzer 29.10.2026 „(a) so übernehmen“; v1 Recurve-Bogen, Pfeilfenster) ·
08 dicker Lauf über Röhrenmagazin, Pumpe · 09 Kammerstängel, großes Zielfernrohr · 10 Spulenringe, Schlitz-Emitter ·
11 offene Doppelschiene mit Leuchtkern · 12 rundes Fokusrohr mit Kegel, Einteilkörper · 13 Drehtrommel im offenen Rahmen (v2.1, Nutzer 28.10.2026; v1 kurzer dicker Kipplauf) · 14 Schulterrohr ·
15 Zuführdeckel, Munitionskasten, Tragegriff · 16 Einschneider mit Parierblock · 17 Stange mit Klingenkopf und Schildflügeln.

## Nicht erlaubt

Wahllose Rillen, Schrauben, Leuchtstreifen, aufgesetzte Kästen, dekorative Symbole und Glyphen; Leuchteffekte als Ersatz für Form;
dieselbe Waffe mit anderem Lauf als neuer Typ; übernommene Destiny-Modelle, Namen oder Logos.
