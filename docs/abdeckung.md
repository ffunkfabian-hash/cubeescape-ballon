<!-- erzeugt von tools/make_docs.py – nicht von Hand ändern -->

# Abdeckungsmatrix BASIC (erste Etappe)

Grundtyp → gewählte Standardausführung → BASIC-Entwurf → Bauteilstruktur → Posen-/Aktionsprofil → Quellen → Prüfstatus.
Maße und Zahlen gemessen am gebauten Modell (`data/specs/`). Zustände: **Entwurf** · **visuell geprüft** · **exportiert** · **im Spiel angebunden** (hier durchgehend *nein*). Zurückgestellte Varianten: [erweiterungen.md](erweiterungen.md).

| Nr. | Grundtyp | Standardausführung (Funktionsreferenz) | BASIC-Entwurf | Länge / Höhe | Bauteile · Baugruppen · Dreiecke | Magazin/Munition separat | Visier separat | Posen-/Aktionsprofil | Quellen | Prüfstatus |
|---|---|---|---|---|---|---|---|---|---|---|
| 01 | Automatikgewehr (Auto Rifle) | Halfdan-D (Häkke); Formgen KG02 | [BASIC-01](bauteile/BASIC-01.md) „Formstudie 01“ | 905 / 268 mm | 39 · 8 · 5852 | Magazin | ja: Visier-Klemmfuß | CE-Klasse rifle; Mechanik: reload_tactical, reload_empty, fire_auto, safety | Q-D2, Q-FG-01/02, Q-REF Auto Rifle | Entwurf ✓ · visuell geprüft (Claude, 2026-10-24) · Mechanik gesichtet 4/4 · exportiert (.blend/.glb/Spec) · angebunden: nein |
| 02 | Impulsgewehr (Pulse Rifle) | Ogma PR6 (Omolon); Formgen KG03 | [BASIC-02](bauteile/BASIC-02.md) „Impuls“ | 797 / 255 mm | 28 · 8 · 4548 | Magazin | ja: Visier-Klemmfuß | CE-Klasse rifle; Mechanik: fire_burst, reload_empty | Q-D2, Q-FG-01/02, Q-REF Pulse | Entwurf ✓ · visuell geprüft (Claude, 2026-10-24) · Mechanik gesichtet 2/2 · exportiert (.blend/.glb/Spec) · angebunden: nein |
| 03 | Scout-Gewehr (Scout Rifle) | Hung Jury SR4 (Omolon); Formgen KG11 | [BASIC-03](bauteile/BASIC-03.md) „Fernblick“ | 988 / 254 mm | 28 · 8 · 5936 | Magazin | ja: Zielfernrohr-Ring hinten | CE-Klasse rifle; Mechanik: fire_semi, reload_empty | Q-D2, Q-FG-01/02, Q-REF Scout | Entwurf ✓ · visuell geprüft (Claude, 2026-10-24) · Mechanik gesichtet 2/2 · exportiert (.blend/.glb/Spec) · angebunden: nein |
| 04 | Handfeuerwaffe (Hand Cannon) | Minuet-42 (SUROS); Formgen KG12 | [BASIC-04](bauteile/BASIC-04.md) „Trommel“ | 298 / 168 mm | 17 · 6 · 2684 | Trommel | Kimme/Korn als eigene Teile | CE-Klasse sidearm (Vorschlag); Mechanik: fire_da, reload | Q-D2, Q-FG-01/02, Q-REF Hand Cannon | Entwurf ✓ · visuell geprüft (Claude, 2026-10-24) · Mechanik gesichtet 2/2 · exportiert (.blend/.glb/Spec) · angebunden: nein |
| 05 | Pistole (Sidearm) | Ironwreath-D (Häkke); Formgen KG01 | [BASIC-05](bauteile/BASIC-05.md) „Seitenwaffe“ | 224 / 156 mm | 13 · 6 · 2004 | Magazin | Kimme/Korn als eigene Teile | CE-Klasse sidearm; Mechanik: fire_semi, reload_empty | Q-D2, Q-FG-01/02, Q-REF Sidearm | Entwurf ✓ · visuell geprüft (Claude, 2026-10-24) · Mechanik gesichtet 2/2 · exportiert (.blend/.glb/Spec) · angebunden: nein |
| 06 | Maschinenpistole (Submachine Gun) | Pizzicato-22 (SUROS); Formgen KG06 | [BASIC-06](bauteile/BASIC-06.md) „Kurzläufer“ | 559 / 292 mm | 29 · 8 · 4636 | Magazin | ja: Visier-Klemmfuß | CE-Klasse submachine_gun; Mechanik: fire_auto, reload_empty | Q-D2, Q-FG-01/02, Q-REF SMG | Entwurf ✓ · visuell geprüft (Claude, 2026-10-24) · Mechanik gesichtet 2/2 · exportiert (.blend/.glb/Spec) · angebunden: nein |
| 07 | Bogen (Combat Bow) | Mercury-A (Häkke); Formgen KG10 | [BASIC-07](bauteile/BASIC-07.md) „Sehnenzug“ | 686 / 1030 mm | 23 · 6 · 3512 | Pfeil als eigene Baugruppe (arrow) | ja: Visierarm, Visierring | CE-Klasse keine (Bogen nicht in CE); Mechanik: draw_hold_release, let_down | Q-D2, Q-FG-01/02, Q-REF Bow | Entwurf ✓ · visuell geprüft (Claude, 2026-10-24) · Mechanik gesichtet 2/2 · exportiert (.blend/.glb/Spec) · angebunden: nein |
| 08 | Schrotflinte (Shotgun) | Quitclaim Shotgun III (Häkke); Formgen KG04 | [BASIC-08](bauteile/BASIC-08.md) „Streuer“ | 882 / 244 mm | 25 · 8 · 4264 | Ladeklappe, Röhrenmagazin, Magazinkappe, Patrone | ja: Visier-Klemmfuß | CE-Klasse shotgun; Mechanik: fire_pump, load_shell | Q-D2, Q-FG-01/02, Q-REF Shotgun | Entwurf ✓ · visuell geprüft (Claude, 2026-10-24) · Mechanik gesichtet 2/2 · exportiert (.blend/.glb/Spec) · angebunden: nein |
| 09 | Scharfschützengewehr (Sniper Rifle) | Elegy-49 (SUROS); Formgen KG05 | [BASIC-09](bauteile/BASIC-09.md) „Weitschuss“ | 1143 / 270 mm | 34 · 8 · 6772 | Magazin | ja: Zielfernrohr-Ring hinten | CE-Klasse sniper; Mechanik: fire_cycle, reload_empty | Q-D2, Q-FG-01/02, Q-REF Sniper | Entwurf ✓ · visuell geprüft (Claude, 2026-10-24) · Mechanik gesichtet 2/2 · exportiert (.blend/.glb/Spec) · angebunden: nein |
| 10 | Fusionsgewehr (Fusion Rifle) | Cruoris FR4 (Omolon); Formgen KG07 | [BASIC-10](bauteile/BASIC-10.md) „Glutkern“ | 802 / 256 mm | 24 · 8 · 4808 | Energiezelle | ja: Visier-Klemmfuß | CE-Klasse rifle (Annahme, Profil ungeprüft); Mechanik: charge_fire, charge_cancel, reload | Q-D2, Q-FG-01/02, Q-REF Fusion | Entwurf ✓ · visuell geprüft (Claude, 2026-10-24) · Mechanik gesichtet 3/3 · exportiert (.blend/.glb/Spec) · angebunden: nein |
| 11 | Lineares Fusionsgewehr (Linear Fusion Rifle) | Taipan-4fr (VEIST); Formgen KG13 | [BASIC-11](bauteile/BASIC-11.md) „Schienenlicht“ | 1217 / 281 mm | 30 · 8 · 7152 | Energiezelle | ja: Zielfernrohr-Ring hinten | CE-Klasse sniper (Vorschlag); Mechanik: charge_fire, reload | Q-D2, Q-FG-01/02, Q-REF Linear | Entwurf ✓ · visuell geprüft (Claude, 2026-10-24) · Mechanik gesichtet 2/2 · exportiert (.blend/.glb/Spec) · angebunden: nein |
| 12 | Spurgewehr (Trace Rifle) | Ribbontail (Omolon); Formgen KG08 | [BASIC-12](bauteile/BASIC-12.md) „Leitstrahl“ | 871 / 252 mm | 22 · 7 · 3948 | Energiezelle | ja: Visier-Klemmfuß | CE-Klasse rifle (Annahme, Profil ungeprüft); Mechanik: beam, reload | Q-D2, Q-FG-01/02, Q-REF Trace | Entwurf ✓ · visuell geprüft (Claude, 2026-10-24) · Mechanik gesichtet 2/2 · exportiert (.blend/.glb/Spec) · angebunden: nein |
| 13 | Granatwerfer (Kipplauf) (Grenade Launcher (breech-loaded)) | Festival Flight (SUROS); Formgen KG14 | [BASIC-13](bauteile/BASIC-13.md) „Kipplauf“ | 642 / 258 mm | 21 · 8 · 4568 | Granate | ja: Visier-Klemmfuß | CE-Klasse heavy (Vorschlag); Mechanik: fire, reload | Q-D2, Q-FG-01/02, Q-REF GL | Entwurf ✓ · visuell geprüft (Claude, 2026-10-24) · Mechanik gesichtet 1/2 · exportiert (.blend/.glb/Spec) · angebunden: nein |
| 14 | Raketenwerfer (Rocket Launcher) | Morrigan-D (Häkke); Formgen KG09 | [BASIC-14](bauteile/BASIC-14.md) „Schulterrohr“ | 946 / 294 mm | 21 · 8 · 5532 | Rakete | ja: Visiersockel, Visier-Klemmfuß | CE-Klasse heavy; Mechanik: fire, reload | Q-D2, Q-FG-01/02, Q-REF Rocket | Entwurf ✓ · visuell geprüft (Claude, 2026-10-24) · Mechanik gesichtet 1/2 · exportiert (.blend/.glb/Spec) · angebunden: nein |
| 15 | Maschinengewehr (Machine Gun) | Unwavering Duty (SUROS); Formgen KG16 | [BASIC-15](bauteile/BASIC-15.md) „Dauerlauf“ | 1073 / 284 mm | 33 · 8 · 5040 | Zuführschale, Munitionskasten | ja: Visier-Klemmfuß | CE-Klasse heavy (Vorschlag); Mechanik: fire_auto, reload | Q-D2, Q-FG-01/02, Q-REF MG | Entwurf ✓ · visuell geprüft (Claude, 2026-10-24) · Mechanik gesichtet 1/2 · exportiert (.blend/.glb/Spec) · angebunden: nein |
| 16 | Schwert (Sword) | Goldtusk (VEIST); Formgen KG17 | [BASIC-16](bauteile/BASIC-16.md) „Klingenlauf“ | 1194 / 76 mm | 9 · 3 · 1136 | keine Munition; Ladeanzeige im Parierblock | kein Visier (Nahkampf) | CE-Klasse keine (Nahkampfprofil fehlt); Mechanik: guard_charge | Q-D2, Q-FG-01/02, Q-REF Sword | Entwurf ✓ · visuell geprüft (Claude, 2026-10-24) · Mechanik gesichtet 1/1 · exportiert (.blend/.glb/Spec) · angebunden: nein |
| 17 | Glefe (Glaive) | Rake Angle (Häkke); Formgen KG18 | [BASIC-17](bauteile/BASIC-17.md) „Schildwacht“ | 1423 / 152 mm | 13 · 7 · 1692 | Energiezelle | kein Visier (Nahkampf) | CE-Klasse keine (Nahkampfprofil fehlt); Mechanik: fire, shield, reload | Q-D2, Q-FG-01/02, Q-REF Glaive | Entwurf ✓ · visuell geprüft (Claude, 2026-10-24) · Mechanik gesichtet 3/3 · exportiert (.blend/.glb/Spec) · angebunden: nein |

## Abweichungen von der Bezugslänge

| Nr. | Bezug | BASIC | Abweichung | Grund |
|---|---|---|---|---|
| 10 | 0.960 m | 0.801 m | -17 % | kompakter Emitter statt langem Lauf (entworfen); Bezug aus Toolgen-Weltmodell |
| 12 | 1.044 m | 0.871 m | -17 % | offen: Proportion beim Feinentwurf prüfen |
| 13 | 0.780 m | 0.642 m | -18 % | kurzer Kipplauf für Ego-Lesbarkeit (entworfen); Bezug ist eine Schätzung (Q-FG-02) |
| 14 | 0.725 m | 0.946 m | +30 % | Toolgens Raketenwerfer ist mit 0,725 m ein verdichtetes Spielmodell; BASIC zeigt das Schulterrohr in Gebrauchslänge (entworfen) |

## Ergonomie gegen Robotermaße (Maßprüfung, ohne Hände)

Bezug: Ego-Handfläche 78 mm breit (Q-CE-03), Roboterhand 90 mm (Q-CE-01); Roboter-Variante verlangt Stützhand ≤ 100 mm vor und Schaft ≤ 120 mm hinter `Socket_Hand` (Q-CE-02) – das ist ein Umbau in Toolgen, kein Maß der Weltwaffe. Abstände entlang der Laufachse (−Y = vorn).

| Nr. | Griff B × T × H mm | Abzug vor Griffachse mm | Stützhand vor Hand mm | Schaft hinter Hand mm | Visierlinie über Laufachse mm | Befund |
|---|---|---|---|---|---|---|
| 01 | 30×68×106 | 51 | 282 | 299 | 66 | Robotervariante braucht Umbau (Stützhand) |
| 02 | 30×68×104 | 51 | 270 | 297 | 72 | Robotervariante braucht Umbau (Stützhand) |
| 03 | 30×67×102 | 50 | 330 | 298 | 73 | Robotervariante braucht Umbau (Stützhand) |
| 04 | 32×67×96 | 31 | einhändig | kein Schaft | kein Visierglas | im Rahmen |
| 05 | 28×69×98 | 38 | einhändig | kein Schaft | kein Visierglas | im Rahmen |
| 06 | 34×56×104 | 46 | 236 | 219 | 65 | Robotervariante braucht Umbau (Stützhand) |
| 07 | 32×51×72 | kein Abzug | einhändig | kein Schaft | kein Visierglas | im Rahmen |
| 08 | 30×70×112 | 53 | 296 | 298 | 63 | Robotervariante braucht Umbau (Stützhand) |
| 09 | 30×68×104 | 51 | 340 | 331 | 76 | Robotervariante braucht Umbau (Stützhand) |
| 10 | 30×69×110 | 52 | 345 | 302 | 75 | Robotervariante braucht Umbau (Stützhand) |
| 11 | 30×70×112 | 53 | 330 | 365 | 88 | Robotervariante braucht Umbau (Stützhand) |
| 12 | 30×70×112 | 53 | 320 | 289 | 74 | Robotervariante braucht Umbau (Stützhand) |
| 13 | 30×70×114 | 53 | 215 | 244 | 70 | Robotervariante braucht Umbau (Stützhand) |
| 14 | 30×69×108 | 52 | 230 | 278 | 98 | Robotervariante braucht Umbau (Stützhand) |
| 15 | 30×68×104 | 51 | 340 | 347 | 95 | Robotervariante braucht Umbau (Stützhand) |
| 16 | 31×194×31 | kein Abzug | -104 | kein Schaft | kein Visierglas | im Rahmen |
| 17 | 30×62×84 | 45 | 365 | kein Schaft | kein Visierglas | Robotervariante braucht Umbau (Stützhand) |
