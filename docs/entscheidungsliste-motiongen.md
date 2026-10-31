# Entscheidungsliste Motiongen → BASIC

Stand 25.10.2026, Patch „BALLON Motiongen-Entscheidungen“ (Branch `claude/ballon-patch-motiongen-entscheidungen`). Ausgewertet sind
alle Motiongen-Analysen für BASIC aus [cubeescape-motiongen](https://github.com/ffunkfabian-hash/cubeescape-motiongen) `main`
`4fa6f27` (REF 0.14–0.28). Diese Datei stellt nur Fragen und hält Antworten fest. Gebaut oder gerendert wird hier nichts.

**Quellen** (je Doc die Abschnitte „Empfehlungen/Vorschläge für BASIC“, „Muster“ und „Offen“):
[visiere] REF 0.14 · [proportionen] 0.15 · [rueckstoss] 0.16 · [zielbewegung] 0.17 · [oberflaechen] 0.18 · [muendung] 0.19 ·
[inspektion] 0.20 · [huefte] 0.22 · [destiny2] › Sprint-Wippen 0.23 und › Glidepath 0.24 · [nachladen] 0.25 · [wechsel] 0.26 ·
[waffenwerte] 0.27 · [zielhilfe] 0.28 · Vergleich mit BALLON in [auswertung] › BALLON-Prototyp.

**Legende**
- Status der Messung (Motiongen [standard]): **[M]** am Bild gemessen · **[S]** Sekundärquelle (Datenbank, API) · **[B]** Entwickler
  · **[C]** Zuarbeit, nicht ganz nachgeprüft · **[O]** Sichtung ohne belastbare Zahl. „1 Bsp.“ heißt: ein Waffenbeispiel, kein Klassenmittel.
- Einstufung: **Pflicht** = sonst wird eine Bildregel oder ein Vertrag dieses Repos verletzt (Stilhandbuch, Visier-Standard 3,
  „Unity folgt Blender“) · **Destiny** = Destiny-typisch, empfohlen · **optional**.
- Aufwand: **S** Daten oder Parameter, Datenexport ohne Backen (`BALLON_EXPORT_DATA_ONLY=1`), Unity-Test · **M** Unity- oder
  Blender-Änderung mit Test und Beleg, eine Patch-Sitzung · **L** neue Geometrie oder neuer Effekt mit Rendern, vollem Export und
  Sichtung, eigene Version.
- Destiny-Prozente gelten für das Spielbild bei unbekanntem FOV. Motiongen liefert sie ausdrücklich als Beobachtung, nicht als Startwert.
  BASIC-Werte stammen aus dem Code dieses Stands. „nicht gemessen“ heißt, dass es kein BASIC-Bild mit Mittenkreuz dazu gibt.

## Schon entschieden (nicht neu fragen)

| Bereich | Entscheidung | Wo |
|---|---|---|
| Stil | Stil v2.1, „schlicht“ über allem, Schlichtheitsbudget, Bloom aus, grauer Hintergrund | [stilhandbuch](stilhandbuch.md) §1–2 |
| Visier-Standard 3 | Typ je Klasse, Rahmen Holo ≤ 0,10 / Ring ≤ 0,15 × Öffnung, Öffnung im Zielen Holo 12–20 % / Zielfernrohr 20–26 % B bei 90 mm und 75°, eine Kamera, Modell ungezoomt, Weltzoom je Klasse, Trapezsockel, Absehen fein ohne Aufgehen im Zielen, HUD-Punkt + Schuss-Ring + Treffer-X (`ADS_FEEDBACK`), Glas ≤ 5 %, Gehäuse neutral mit einem Akzent, Absehen Cyan | [stilhandbuch](stilhandbuch.md) §6, [absehen](absehen.md) |
| Sprint (0.10) | vertikal 3,16 Hz, seitlich 1,58 Hz, U-Bogen, Rollen ±3,5°, kein Kopfwippen | [0.10](versions/0.10-stride.md), `ego.py` |
| Visier-Anflug (0.10) | kritisch gedämpfte Feder (10 Hz, ζ 1), kein Überschwingen; `aim_in` 0,33 s = Destiny-Automatik 20 Bilder bei 60/s | [0.10](versions/0.10-stride.md) |
| Fadenkreuz (0.10) | kein ständiges Fadenkreuz, kurze Trefferanzeige | [0.10](versions/0.10-stride.md) |
| Tempo | Ablauftempo 1,25 gegenüber der Destiny-Messung; Zielen und Feuern bleiben schnell | [stilhandbuch](stilhandbuch.md) §10 |
| Unity | Unity folgt Blender so nah wie möglich | [AGENTS.md](../AGENTS.md) |

**Erfüllt ohne Frage:** Munitionsanzeige springt vor der Rückkehr in die Hüfte (Destiny, Apex, Titanfall, Marathon in 12 von 12 Fällen
[M] [nachladen] › 4; Unity setzt `ammo = magSize` beim Marker `MagIn`). Leer gegen taktisch: Titanfall-CAR Δ 0,42 s [M], BASIC Δ 0,40 s
(2,50 / 2,10 s). Rollen im Sprint: Destiny-Automatik ≈ 7° Spitze–Spitze [M], BASIC ±3,5°. Gewehrgehäuse: BASIC 0,10–0,13 L, Destiny
0,16–0,25 L, also kein zu hoher Körper ([proportionen] › 5.1). Hell/Dunkel: BASIC `shell` L* ≈ 82 gegen `graphite` ≈ 19 (Albedo),
Destiny-Schalen ΔL* 64–78 [M].

## Block 1 – Visier

| # | Thema | Gemessen (Quelle, Status) | BASIC heute | Empfehlung | Einstufung | Aufwand |
|---|---|---|---|---|---|---|
| 1a | Scout-Ring außen/Öffnung | BASIC 1,76–1,91 gegen Destiny 1,28–1,30 [M] ([proportionen] › 5.2) – gemessen an `sight_options.png` vom 24.10. 19:51, **vor** Visier-Standard 3 | `common.scope_v21`: Objektivring außen 16,5 mm, Öffnung 14,0–14,8 mm, also ≈ 1,11–1,18 (aus dem Code gerechnet, nicht am Bild) · **BASIC gemessen (25.10.2026, [Messungen](#messungen-25102026)):** Ring außen ÷ Ringinnenkante **1,31**, ÷ lichtes Glas **1,56** (±0,02), Scout-Zielbild nach Visier-Standard 3; der Codewert 1,11–1,18 trifft das Bild nicht · **nachgemessen am neuen Scout-Zielbild (26.10.2026, BALLON 0.19 „Saddle“):** unverändert **1,31 / 1,56** (322 / 246 / 207 px); die äußere Kante im Bild ist die Fasenwulst des Objektivtrichters (r ≈ 21 mm), nicht der Objektivrand (16,5 mm) | keine Entscheidung nötig; beim nächsten Ego-Still am Bild nachmessen und in `data/review.json` eintragen | Pflicht (Prüfung) | S |
| 1b | Scout-Visier über dem Gehäuse | Destiny-Scouts 0,02–0,04 L (Tone Patrol 0,013–0,019 [M], übrige [C]); das Rohr liegt direkt auf der Gehäuseoberkante ([visiere] › 6); BASIC alter Bildstand 0,063 L | Visierbaugruppe 57 mm hoch bei L 1023 mm (0,056 L, Hülle mit Hals); Rohr auf Trapezhals; Visierhöhe 65 mm (Soll 66 ± 4) · **umgesetzt (26.10.2026, BALLON 0.19 „Saddle“, [Bericht](versions/0.19-saddle.md)), am Netz gemessen mit `tools/test_sight_seat.py`:** vorher Spalt Rohr–Gehäuse **21,5–25,5 mm**, Visier über Gehäuse **52,0 mm = 0,051 L**; nachher Rohr auf einem Gehäusebuckel mit kurzer Schiene, Spalt **0,3 mm** auf 57,5 mm Länge, Visier über Gehäuse **30,8 mm = 0,030 L** (Visierbaugruppe als Hülle 42 mm = 0,041 L, ohne Hals), Visierhöhe **65,0 mm** | Frage 1.1 | Destiny | M (Blender, Rendern, Export) |
| 1c | Weltzoom je Klasse | Bildmaßstab Destiny [M] ([destiny2] › Glidepath, [visiere] › 4): Automatik 1,84, Impuls 2,10, MG 1,84, Scout 2,0 (1 Paar), Handfeuerwaffe 1,15 (Exotic), Seitenwaffe 1,29, MP-Holo 1,43 / MP-Kimme 1,71, Granatwerfer 1,44 | `reticles` (Grundzoom + Visierbonus): Automatik 1,9, Impuls 2,0, MG 1,9, Granatwerfer 1,4, Seitenwaffe 1,25 passen; abweichend **Scout 2,9** (Zielfernrohr), **Handfeuerwaffe 1,5**, **MP 1,25** | Frage 1.2 | Destiny | S |
| 1d | Zoom gegen Modell | Holo: Zoom beginnt 0–2 Bilder nach dem Modell und endet gleichzeitig ±1 Bild (Automatik, Impuls, MG); Kimme-MP: Modell schnappt in 1–2 Bildern ein, Zoom endet 5 Bilder später; Scharfschütze: Linse erst nach dem Modell [M] | in Unity nicht gemessen · **BASIC gemessen (25.10.2026, Holo, 60/s):** Hüfte → Zielen: Weltzoom beginnt **2–3 Bilder vor** dem Modell und endet 3–5 Bilder vor ihm; Sprint → Zielen: Zoom beginnt 11 Bilder nach dem Modell, Ende 0 bis +2; Zielfernrohr in Unity nicht messbar | in Unity messen (Testprotokoll wie `Zielen_landet_ohne_Ueberschwingen`) und auf „Start mit oder kurz nach dem Modell, Ende gemeinsam“ legen | Destiny | S–M |
| 1e | Durchblick, Glas, Gehäusefarbe | Destiny: eine Kamera, Glas kaum getönt, keine Gebrauchsspuren, Gehäuse neutral [M] | Visier-Standard 3 §4, §7, §8 | entschieden; Gegenbeispiele zur neutralen Gehäusefarbe stehen in Block 8 | – | – |

**Frage 1.1 – Scout-Optik tiefer setzen?**
- **A (Empfehlung):** Beim nächsten Scout-Umbau steigt die Gehäuseoberkante unter dem Rohr. Das Rohr sitzt dann wie bei Destiny direkt
  auf dem Gehäuse, der Hals entfällt, die Visierhöhe bleibt 66 ± 4 mm.
- **B:** So lassen. Der Hals bleibt sichtbar, die Optik steht etwas höher als bei Destiny.
- Antwort (Nutzer, 25.10.2026): „Block 1: 1.1 A, 1.2 A, Rest wie empfohlen.“ → **A** – *überholt* durch die Antwort vom 26.10.2026 (umgesetzt in 0.19 „Saddle“)
- Neue Antwort (Nutzer, 26.10.2026, Visier-Konzept [visier-konzept.md](visier-konzept.md) › 7, Auswahl im Dialog): „v3 bauen“ →
  **Konzept A „Hals“:** Sattel hinter dem Auge, Klemmfuß unter dem Objektiv, Ring ohne Wulst; die Visierhöhe bleibt 66 ± 4 mm, das
  Rohr liegt hinten auf einem Gehäusebuckel auf. Umgesetzt in **0.21 „Ironsight“** ([Bericht](versions/0.21-ironsight.md)), am Netz
  geprüft mit `tools/test_sight_seat.py` (Sattel hinter dem Auge, unteres Bilddrittel zwischen Auge und Objektiv frei).

**Frage 1.2 – Weltzoom an die Glidepath-Messung angleichen?**
- **A (Empfehlung):** Ja, für die drei abweichenden Klassen: Scout 2,0 statt 2,9, Handfeuerwaffe 1,15–1,2 statt 1,5, MP 1,45 statt 1,25.
  Danach `export_reticles.py`, Datenexport und `./check`.
- **B:** Bei den Werten von Visier-Standard 3 bleiben.
- Antwort (Nutzer, 25.10.2026): „Block 1: 1.1 A, 1.2 A, Rest wie empfohlen.“ → **A**

**Rest von Block 1:** 1a und 1d wie empfohlen? Antwort (Nutzer, 25.10.2026): „Rest wie empfohlen.“ → **ja**

## Block 2 – Haltung und Hüfte

| # | Thema | Gemessen (Quelle, Status) | BASIC heute | Empfehlung | Einstufung | Aufwand |
|---|---|---|---|---|---|---|
| 2a | Hüftlage im Bild | Destiny, lange Waffen: Mündung **rechts unter der Mitte** bei x 54–59 / y 60–71 % (21 Beispiele [M], Showcases); hintere Visieröffnung 7–34 pp rechts der Mündung; Kontur reicht bis zum rechten und unteren Rand ([huefte] › 4) | `ego.POSES['hip']` Socket_Hand (−0,20 / −0,42 / −0,165) m, entworfen; Bildlage nicht gemessen · **BASIC gemessen (25.10.2026):** Mündung x **58,8** / y **49,6** %, hintere Visierkante x 80,3 % (21,5 pp rechts der Mündung), Kontur reicht über den rechten und unteren Rand | Frage 2.1 | Destiny | S Messung, M Anpassung |
| 2b | Hüftlage je Klasse | Kurzwaffen kompakt bei x 53–71 × y 59–84 %; große Waffen reichen bis y ≤ 45 % (MG, Werfer); Bögen quer unten [M] | eine Hüfthaltung, Ego-Daten nur für BASIC-01 | Haltung je Klasse festlegen, sobald eine Klasse Ego-Daten bekommt | Destiny | M je Klasse |
| 2c | Waffenlage als Spieleroption | Halo hat Versatzregler je Klasse [B]; Destiny hat nur einen Welt-FOV-Regler, keinen Modellregler [B]; Spielerwünsche sind Einzelstimmen [C] | nur `ads_eye_relief` (70/90/110 mm) | Frage 2.2 | optional | M |

**Frage 2.1 – Hüftlage auf das Destiny-Band ziehen?**
- **A (Empfehlung):** Zuerst an einem Ego-Still mit Mittenkreuz messen (Mündung, Visier, Körper in %), dann `hip` so legen, dass die
  Mündung in x 54–59 / y 60–71 % liegt. Danach je Klasse beim Ego-Übertrag.
- **B:** So lassen, bis weitere Waffen Ego-Daten haben.
- Antwort (Nutzer, 25.10.2026): „Block 2: 2.1 A, 2.2 B.“ → **A**

**Frage 2.2 – Waffenlage als Spieleroption?**
- **A:** Ja, Versatz x/y/z je Klasse (Halo).
- **B (Empfehlung):** Nein. Destiny hat keinen Modellregler, und „schlicht“ spricht dagegen.
- Antwort (Nutzer, 25.10.2026): „Block 2: 2.1 A, 2.2 B.“ → **B**

## Block 3 – Sprint und Bewegung

| # | Thema | Gemessen (Quelle, Status) | BASIC heute | Empfehlung | Einstufung | Aufwand |
|---|---|---|---|---|---|---|
| 3a | Sprint-Hub | Automatikgewehr (Last Wish, 1 Bsp.): ≈ **10–11 % H** vertikal, ≈ **13 % B** seitlich [M], bei NCC < 0,85 ±1–2 pp; Handfeuerwaffe ≈ 13 % H / 4 % B [M]; das Scourge-Plateau ≤ 0,6 % H ist kein Sprinthub (Widerspruch 8) | `sprint.bob.amp` 12 mm seitlich / 10 mm vertikal, geschätzt ≈ 6 % H / 4 % B (aus Abstand und FOV, nicht am Bild) · **BASIC gemessen (25.10.2026, Unity 60/s, 3,16 Hz):** Hub vertikal **2,1–2,3 % H** (Schwerpunkt) bis **5,1–5,7 % H** (Oberkante), seitlich **7,0–8,7 % B** (Mündungsende) bzw. 0,3–1,4 % B (Schwerpunkt) | Frage 3.1 | Destiny | S Messung, S Wert |
| 3b | Trageform je Klasse | Automatik tief und quer im unteren Drittel, Mündung links [M]; Handfeuerwaffe hoch rechts, Lauf fast senkrecht, verlässt das Bild [M]; Scharfschütze höher und mittiger; MP tief, nach links gerollt; kurze Fusion groß und tief [O] | eine Haltung `sprint` (quer, gesenkt, Rollen −35°) | Frage 3.2 | Destiny | M je Klasse |
| 3c | Sprint-Frequenz je Typ | nur Automatik und Handfeuerwaffe gemessen (3,16 Hz); 13 der übrigen 15 Typen offen, Schwert trifft nicht zu | 3,16 / 1,58 Hz für alle | entschieden (0.10); bis zu neuen Messungen für alle Klassen | – | – |
| 3d | Umsehen (Sway) | Bei schnellen Drehungen zieht die Waffe ≈ 10 % B gegen die Drehung nach und kehrt in ≈ 0,3 s **ohne Überschwingen** zurück (Scharfschütze, 60/s, [destiny2] › 3, Stand 18.10.) [M] | Unity `swayDamp` 0,55 (unterkritisch, schwingt über), `swayFreq` 9, höchstens 3° | Frage 3.3 | Destiny | S |
| 3e | Sprint → Hüfte | Handfeuerwaffe ≈ 4 Bilder bis nahe Hüfte, ≈ 8 bis ruhig (1 Bsp.) [M]; Ein- und Austritt sonst nicht isoliert | `sprint` Ende 10 Bilder bei 30/s (× 1,25) | beobachten, keine Änderung, solange nur 1 Beispiel vorliegt | optional | – |

**Frage 3.1 – Sprint-Hub auf das Destiny-Maß heben?**
- **A (Empfehlung):** Zuerst den BALLON-Hub am Unity-Bild messen (`unity_run.py feel`, Mittenkreuz), dann auf ≈ 10 % H / 13 % B
  (Automatik) heben. Der Test `Sprintschritt_wie_ein_Laeufer` prüft zusätzlich den Hub.
- **B:** Beim heutigen, ruhigeren Hub bleiben.
- Antwort (Nutzer, 25.10.2026): „Block 3: 3.1 A, 3.2 A, 3.3 A.“ → **A**

**Frage 3.2 – Sprint-Trageform je Klasse?**
- **A (Empfehlung):** Ja, beim Ego-Übertrag je Klasse: Gewehre tief und quer wie heute, Handfeuerwaffe und Seitenwaffe hoch rechts mit
  steilem Lauf, Scharfschütze höher und mittiger.
- **B:** Eine Sprinthaltung für alle Klassen.
- Antwort (Nutzer, 25.10.2026): „Block 3: 3.1 A, 3.2 A, 3.3 A.“ → **A**

**Frage 3.3 – Sway ohne Überschwingen?**
- **A (Empfehlung):** Ja. Die Feder wird kritisch gedämpft (ζ ≈ 1), die Rückkehr dauert ≈ 0,3 s, wie beim Visier-Anflug in 0.10.
- **B:** So lassen.
- Antwort (Nutzer, 25.10.2026): „Block 3: 3.1 A, 3.2 A, 3.3 A.“ → **A**

## Block 4 – Zielen und Fadenkreuz

| # | Thema | Gemessen (Quelle, Status) | BASIC heute | Empfehlung | Einstufung | Aufwand |
|---|---|---|---|---|---|---|
| 4a | Hüft-Fadenkreuz | an 8 Typen in der Hüfte [M], je 1 Clip: Automatik Ring aus vier Bögen 3,2 % H; MP Ring + vier Eckmarken 5,9–6,3 % H; Handfeuerwaffe Klammern + Punkt ≈ 6 % H; Bogen 4,6 % H; Scharfschütze nur „^“ ≈ 1 % H; kurze Fusion 1,7 / 5,5 % H; lineare Fusion 12–13 % H; Granatwerfer 6,3 % B × 5,6 % H; meist weiß. Sprint: Automatik nur „^“ 1,5 % H, Handfeuerwaffe weg. Zielen: weg im 1. Bild (Automatik 11 Bilder vor dem Visier, MP 0,19 s) | `reticles.DEFAULTS[typ]['hip']` (z. B. Automatik `cross`, MP `circle_cross`) und `SPREAD` sind vorhanden; Unity zeigt seit 0.10 kein Fadenkreuz | Frage 4.1 | Destiny | M |
| 4b | Hüftform je Typ | siehe 4a | Automatik `cross`, Impuls `cross`, Handfeuerwaffe `cross`, Scharfschütze `dot`, MP `circle_cross` | Frage 4.2 | Destiny | S |
| 4c | Rückmeldung im Zielen | Visier-Standard 3 §6 (entschieden): HUD-Punkt 1,1 % H, Schuss-Ring 2 % H für 1 Bild, Treffer-X 4,5 % H ≥ 0,17 s. Glidepath [M]: Treffer-X rot 3,0–3,6 % H, Einzeltreffer 6–7 Bilder, Salve 15–19 Bilder; Präzisionstreffer als gelbe Zahl. **Widerspruch 3:** der rote HUD-Punkt stammt vermutlich aus dem Showcase-HUD, in Spielclips liegt in der Hüfte ein Ring je Typ | Unity: kein HUD-Punkt, kein Schuss-Ring; Treffer = vier orange Quadrate für 0,12 s | Frage 4.3 | Pflicht (Unity folgt dem Standard) | S–M |
| 4d | Anflugdauer je Klasse | erste Bewegung → Ruhe [M]: Seitenwaffe 6–7, MP 8–12, Handfeuerwaffe 10, Schrot ≈ 13, lineare Fusion 17, Automatik/Impuls/MG 20 Bilder bei 60/s | `aim_in` 0,33 s für alle (nur BASIC-01 hat Ego-Daten) | beim Ego-Übertrag je Klasse übernehmen | Destiny | S je Klasse |

**Frage 4.1 – ausblendendes Hüft-Fadenkreuz?**
- **A (Empfehlung):** Ja. Ein kleines weißes Fadenkreuz (3–6 % H), nur in der Hüfte. Im Sprint ist es aus (Automatik höchstens „^“), es
  verschwindet im ersten Bild des Zielens, beim Nachladen und Ziehen ist es aus (Destiny dort offen). Es geht beim Schießen nach
  `SPREAD` auf. Das ständige Kreuz von 0.9 kommt nicht zurück.
- **B:** Gar kein Fadenkreuz (Stand 0.10).
- Antwort (Nutzer, 25.10.2026): „Block 4: 4.1 A, 4.2 A, 4.3 A.“ → **A**

**Frage 4.2 – Hüftformen an die gemessenen Destiny-Formen angleichen (nur bei A in 4.1)?**
- **A (Empfehlung):** Ja, wo gemessen: Automatik, Impuls (übertragen) und MG (übertragen) bekommen Ring mit Punkt (`ring_dot`)
  statt `cross`; Handfeuerwaffe Klammern; Scharfschütze „^“; MP bleibt `circle_cross`. Neue Formen kommen in den Katalog `reticles.py`.
- **B:** Hüftformen wie im Katalog lassen.
- Antwort (Nutzer, 25.10.2026): „Block 4: 4.1 A, 4.2 A, 4.3 A.“ → **A**

**Frage 4.3 – Rückmeldung im Zielen in Unity nachziehen?**
- **A (Empfehlung):** Schuss-Ring und Treffer-X nach Visier-Standard 3 jetzt in Unity, Treffer in Familienfarbe Orange statt Destiny-Rot.
  Der HUD-Punkt wartet, bis Motiongen Widerspruch 3 geklärt hat (Rückfrage über Sightline).
- **B:** Alles aus Visier-Standard 3 sofort, auch den HUD-Punkt.
- Antwort (Nutzer, 25.10.2026): „Block 4: 4.1 A, 4.2 A, 4.3 A.“ → **A**

## Block 5 – Rückstoß und Mündung

| # | Thema | Gemessen (Quelle, Status) | BASIC heute | Empfehlung | Einstufung | Aufwand |
|---|---|---|---|---|---|---|
| 5a | Rückstoß im Zielen | Im Zielen wandert vor allem die **Welt**, das Visier bleibt fast stehen: Welt Automatik ≈ 4, Impuls ≈ 5, Scout und Handfeuerwaffe je ≈ 6, lineare Fusion ≈ 13, Scharfschütze ≈ 18 pp H; Holo-Visier < 1 pp H; Rückkehr zur Basis 36–75 Bilder, kein Unterschwingen [M] ([zielbewegung] › 6b) | `RECOIL`: Modell-Feder (5 Hz, ζ 0,5, 0,62 m/s zurück, 115 °/s Nicken) und Kamera 18 °/s; im Zielen „gedämpft“ (entworfen); Sichtung `fire_ads`: „Visier springt leicht“ | Frage 5.1 | Destiny | M |
| 5b | Bahnform | Automatik (Chroma Rush, Abyss Defiant): gleichmäßig steigende Säule, ≈ 1 pp H je Schuss, seitlich ≤ 2,2–2,5 pp B, dreimal dieselbe Form; Impuls: Stufe ≈ 4 pp je Salve, Erholung in der Pause; Scout und lineare Fusion: Rest wächst von Schuss zu Schuss; Rücklauf 0,2–0,4 s [M] ([rueckstoss] › 4, 6) | `climb_deg` 0,12 je Schuss plus Zufallsstreuung (Hüfte 1,1°, Zielen 0,12°); Salven nicht getrennt | Frage 5.2 | Destiny | M |
| 5c | Mündungsfeuer | Blitz 1–2 Bilder bei 60/s: kleiner heller Kern, breitere Seitenflammen; im Zielen deckt er 5 % (Impuls), 20 % (Automatik), 40 % (MG), 50 % (Scout) bis ≈ 100 % (Schrot, am Spitzenwert) der Öffnung ab [M, 5 Werte nachgemessen] ([muendung] › 6) | kein Mündungsfeuer in Blender und Unity; `Socket_Muzzle` vorhanden; Bloom aus | Frage 5.3 | Destiny | L |
| 5d | Hülsen | goldene Hülsen im 1. Blitzbild oder 1 Bild danach, nach rechts bzw. rechts unten, auch neben Energieeffekten [M] | keine (Rolle `brass` vorhanden) | Frage 5.4 | optional | M |
| 5e | Mündungsform | offene Endstücke vor geschlitzten Mänteln, Emitter statt Laufmund bei Energiewaffen [M] | Stilhandbuch §2 Regel 6 „lesbare Front“ | entschieden | – | – |

**Frage 5.1 – Rückstoß im Zielen in die Welt statt ins Visier?**
- **A (Empfehlung):** Ja. Im Zielen geht der Rückstoß fast ganz in die Kamera (Automatik ≈ 4 % H je Stoß), das Visier bleibt unter
  1 % H. Die Rückkehr dauert 0,4–0,6 s ohne Unterschwingen. Messung mit Weltanker im Unity-Test.
- **B:** So lassen (Modell-Kick auch im Zielen).
- Antwort (Nutzer, 25.10.2026): „Block 5: 5.1 A, 5.2 A, 5.3 A, 5.4 B.“ → **A**

**Frage 5.2 – welche Rückstoß-Bahn?**
- **A (Empfehlung):** Destiny-Säule: feste, lernbare Grundbahn senkrecht mit kleinem, begrenztem Seitenwackeln. Bahn, Kamera, Modellkick
  und Streuung sind getrennte Größen, Salven zweistufig (Takt in der Salve, Erholung danach).
- **B:** Erkennbare Signaturform je Waffe (Diagonale, Bogen, S wie in CS2 oder CoD).
- Antwort (Nutzer, 25.10.2026): „Block 5: 5.1 A, 5.2 A, 5.3 A, 5.4 B.“ → **A**

**Frage 5.3 – Mündungsfeuer einführen?**
- **A (Empfehlung):** Ja, in Blender und Unity gleich. 1 Bild bei 30/s, kleiner heller Kern und kurze Seitenflammen, reine Emission ohne
  Bloom. Im Zielen deckt es bei Holo-Klassen höchstens ≈ 20 % der Öffnung ab. Eigene Version.
- **B:** Kein Mündungsfeuer.
- Antwort (Nutzer, 25.10.2026): „Block 5: 5.1 A, 5.2 A, 5.3 A, 5.4 B.“ → **A**

**Frage 5.4 – Hülsenauswurf?**
- **A:** Ja, zusammen mit 5.3 (Messing, nach rechts unten, 1 Bild nach dem Blitz).
- **B (Empfehlung):** Erst Mündungsfeuer, Hülsen später. Das ist schlichter, und die Hülse ist ohne Ton und bei 30/s kaum lesbar.
- ~~Antwort (Nutzer, 25.10.2026): „Block 5: 5.1 A, 5.2 A, 5.3 A, 5.4 B.“ → **B**~~ (überholt am 26.10.2026)
- Antwort (Nutzer, 26.10.2026, zu Schritt 5): „Können wir die Hülsen nicht doch dazu machen. Wenn wir da schon einmal dran sind.“ → **A**
  (umgesetzt mit 5.3 in BALLON 0.16 „Flash“)

## Block 6 – Nachladen, Wechsel, Betrachten

| # | Thema | Gemessen (Quelle, Status) | BASIC heute | Empfehlung | Einstufung | Aufwand |
|---|---|---|---|---|---|---|
| 6a | Wegstecken und Wechsel | Destiny-Wechsel (7 Fälle): Wegstecken 5–16 Bilder (0,08–0,27 s), leere Sicht 4–18 Bilder (0,07–0,30 s), Ziehen bis zur ersten Hüftpassage 4–14 Bilder; nach der ersten Passage Überschwingen 8–10 pp (3 Fälle); bei gehaltenem Zielen zieht die Waffe direkt in ADS [M] ([wechsel] › 4) | `holster` 0,60 s, `draw` 0,83 s (Ready bei 0,60 s) mit Ausfedern, `draw_aim` vorhanden; leere Sicht in Unity nicht festgelegt | Frage 6.1 | Destiny | S |
| 6b | Betrachten (Inspect) | **Destiny 2 hat keinen Ego-Inspect** (nicht gefunden), nur das Menü ohne Hände, frei drehbar, Waffe auf 40–50 % der Fläche [M/O]. Andere Spiele: heben → Breitseite → Rolle → Hüfte, beide Flanken, kein Blick durch die Optik, 2,8–6,5 s [M] ([inspektion] › 3, 6) | Ego-Aktion `inspect` 4,0 s (Ego-Seite, dann Oberseite und rechte Seite), Herkunft „E nach Destiny-Inspektion“ | Frage 6.2 | optional | S |
| 6c | Nachlade-Abbruch | Abbruch vor oder nach der Munitionsübernahme in Destiny nicht belegt; Spielerthreads über Schusssperre trotz voller Anzeige [C] | Munition gilt ab `MagIn`, `reload_to_switch` bricht vorher ab (Magazin bleibt eingesetzt, Munition nicht) | so lassen und im Unity-Test ausdrücklich prüfen: Abbruch vor `MagIn` = keine Munition, danach = voll | Destiny | S |

**Frage 6.1 – Wechsel straffer, mit kurzer leerer Sicht?**
- **A (Empfehlung):** Ja. `holster` ≈ 0,25 s (statt 0,60 s), danach 0,1–0,2 s ohne Waffe, dann Ziehen wie heute mit Nachfedern. Unity
  nimmt die Marker (Wegstecken, leer, erstes neues Bild, Hüfte, ruhig) einzeln in den Test.
- **B:** Bei den heutigen Zeiten bleiben.
- Antwort (Nutzer, 25.10.2026): „Block 6: 6.1 A, 6.2 A.“ → **A**

**Frage 6.2 – Betrachten (Inspect) ja oder nein?**
- **A (Empfehlung):** Ego-Inspect behalten (wie Apex, CoD, Valorant), Herkunft berichtigen auf „E nach Apex/CoD-Muster; Destiny hat
  keinen Ego-Inspect“. Eine Menüansicht ohne Hände wird nicht gebaut.
- **B:** Wie Destiny: Ego-Inspect weg, später eine Menüansicht ohne Hände, frei drehbar.
- Antwort (Nutzer, 25.10.2026): „Block 6: 6.1 A, 6.2 A.“ → **A**

## Block 7 – Waffenwerte und Zielhilfe

| # | Thema | Gemessen (Quelle, Status) | BASIC heute | Empfehlung | Einstufung | Aufwand |
|---|---|---|---|---|---|---|
| 7a | Kadenz | Chroma Rush 720/min (Menükarte [M], Clip 5 Bilder Abstand [M]); Manifest-Rahmen sind Rohwerte, keine Startwerte [S] ([waffenwerte] › 4) | Clip `fire_hip` mit 720/min (Herkunft M), Unity schießt mit `GAMEPLAY.rpm` = 600 („noch nicht vom Nutzer festgelegt“): Blender und Unity widersprechen sich | Frage 7.1 | Pflicht (Unity folgt Blender) | S |
| 7b | Wertetabelle je Typ | Destiny: Menükarte und Manifest liegen 1–25 Stat-Punkte auseinander; Handling sind je Familie andere Sekunden [S]; Motiongen rät: Roll, Stand und Basis/ausgerüstet immer nennen | nur `GAMEPLAY` (rpm, Magazin) für BASIC-01 | Frage 7.2 | optional | S |
| 7c | Zielhilfe | Destiny trennt Schusskorrektur (Bullet Bend, Maus und Controller) von Kamerahilfe (Bremse und Anhaftung, nur Controller); Stärken unveröffentlicht [B] ([zielhilfe] › 4) | keine Zielhilfe | Frage 7.3 | optional | M |

**Frage 7.1 – Kadenz angleichen?**
- **A (Empfehlung):** Unity auf 720/min wie der gemessene Clip; Magazin 30 bleibt Entwurf.
- **B:** 600/min festlegen und den Feuerclip neu rendern.
- Antwort (Nutzer, 25.10.2026): „Block 7: 7.1 A, 7.2 B, 7.3 A.“ → **A**

**Frage 7.2 – Wertetabelle je BASIC-Typ?**
- **A:** Jetzt eine Entwurfstabelle (Kadenz, Magazin, Ziehen, Nachladen) für alle 17 Typen in `data/`.
- **B (Empfehlung):** Erst wenn eine zweite Waffe in Unity spielbar wird; bis dahin nur BASIC-01.
- Antwort (Nutzer, 25.10.2026): „Block 7: 7.1 A, 7.2 B, 7.3 A.“ → **B**

**Frage 7.3 – Zielhilfe?**
- **A (Empfehlung):** Zurückstellen, bis Controller-Eingabe Thema ist. Dann getrennte, benannte Bausteine (Schusskorrektur, Bremse,
  Anhaftung) mit eigener Doku.
- **B:** Jetzt eine schwache Schusskorrektur für alle Eingaben.
- Antwort (Nutzer, 25.10.2026): „Block 7: 7.1 A, 7.2 B, 7.3 A.“ → **A**

## Block 8 – Oberflächen und Materialrollen

| # | Thema | Gemessen (Quelle, Status) | BASIC heute | Empfehlung | Einstufung | Aufwand |
|---|---|---|---|---|---|---|
| 8a | Akzentanteil | bunte Pixel (C* > 25) 1,7–9,9 % bei 7 von 8 Grundlacken; Farbtonfläche der Akzente 5,6–11,7 % [M] ([oberflaechen] › 4) | Budget zählt Funktionen (3 Orange, 1 Band), keine Fläche | Frage 8.1 | Destiny | S |
| 8b | Abnutzung | gemalt und flächig (Sprenkel im Band, abgeriebene Flächen, ganze Schale), nicht nur an Kanten [O] | Kantenabrieb (4-mm-Maske) und AO-Schmutz; Skin `gebraucht` stark | Frage 8.2 | optional | M |
| 8c | Visiergehäuse folgt dem Lack | Gegenbeispiele (Uriel's Gift, The Mornin' Comes, Cabal-Waffen) [O], keine Quote ausgezählt | Visier-Standard 3 §8: Gehäuse neutral, ein Akzent | entschieden; die Gegenbeispiele ändern nichts | – | – |
| 8d | Muster und Skins | Shader färben die ganze Waffe; Muster kommen aus dem Shader oder als festes Bandlayout der Waffe und queren Paneele; Emblem, Leuchtanzeige und Magazinfenster bleiben [O] | Skins färben Rollen; `tarnung` als Flächenmuster auf `shell`; Orange und Cyan behalten ihre Funktion | passt; keine Änderung | – | – |
| 8e | Formgliederung | schlank wirken Längsstaffelung, Negativräume und Detail in Zonen, nicht „alles dünner“ ([proportionen] › 3) | Stilhandbuch §2 (Negativraum, drei Detailebenen); läuft in BALLON 0.12 „Silhouette“ | entschieden bzw. dort in Arbeit | – | – |

**Frage 8.1 – Akzentfläche beim Sichten messen?**
- **A (Empfehlung):** Ja. In Sichtrunde 3 wird an der Hauptansicht der Anteil bunter Pixel (C* > 25) gemessen, Ziel ≤ 10 %. Das ist
  eine Zahl im Bericht, kein neues Werkzeug.
- **B:** Bei der Zählung nach Funktionen bleiben.
- Antwort (Nutzer, 25.10.2026): „8.1: B“ → **B**

**Frage 8.2 – flächige Abnutzung?**
- **A (Empfehlung):** Nur im Skin `gebraucht` zusätzlich flächige Sprenkel; der Standard bleibt bei Kantenabrieb.
- **B:** Gar nicht, nur Kantenabrieb.
- Antwort (Nutzer, 25.10.2026): „8.2: A“ → **A**

## Block 9 – Wirkung der Waffen (BALLON 0.34 „Payload“, Entwurf E)

Nutzerbefunde aus dem Testbuild 0.33 (31.10.2026): Projektile, Explosionen, Strahlen, Einschläge, Hülsen und Füllstände fehlten.
Motiongen hat für Projektile, Strahlen und Schrot **keine** Flugzeit, keine Geschwindigkeit, keine Bolzenzahl und kein Pelletmuster
gemessen ([destiny2 › Methode 16][destiny2]: „keine m/s und keine Reichweite“). Darum steht jeder Wert unten als **E** in
`basic/arms/ego.py` (PAYLOAD je Klasse → `ego.json › weapons[].gameplay.fx`; IMPACTS, DECAL, EXPLOSION, MUZZLE_SMOKE, INDEX →
`motion.payload`, `motion.index`). Die Messungen von REF 0.36 „Impact“ ersetzen sie danach als Patch: nur `ego.py` ändern und den
Datenexport laufen lassen (`BALLON_EXPORT_DATA_ONLY=1`, ohne Backen).

| # | Thema | Gemessen (Quelle, Status) | BASIC 0.34 (E) | Offen für REF 0.36 |
|---|---|---|---|---|
| 9a | Granate | Geschoss 3 Bilder bei 60/s sichtbar, Einschlag 0,13 s nach dem Blitz; Ignition Code Spur 6 Bilder (keine reine Flugzeit) [O] | 42 m/s, Fall 7 m/s², Explosion Radius 3 m, Lebensdauer 4 s | m/s, Fallkurve, Zünder/Abprall |
| 9b | Rakete | große Explosion 0,45 s nach dem Blitz (Blue Shift) [O] | 34 m/s gerade, Radius 4,5 m, Rauchspur | m/s, Spurlänge, Rauchdauer |
| 9c | Explosion | Ignition Code 9 Bilder bei 60/s, Blitz 3 Bilder [M] | Blitz 0,12 s, 10 Feuerkugeln 0,45 s, Druckring 0,35 s (× 0,9 Radius), 40 Funken, 16 Rauchballen 2,6 s, Licht 0,18 s, Brandfleck 1,4 m | Ring, Rauch, Ende |
| 9d | Rauch aus dem Lauf | nicht gemessen (CoD .357 Rauchpuff [O]) | Werfer: 9 Ballen/s, 1,4 s (Granate) bzw. 2,0 s (Rakete), steigen 0,1 m/s | Dauer, Menge |
| 9e | Dauerstrahl (Spurgewehr) | Prometheus Lens: Strahl ≈ 9–12 % B, Mündungslicht ≈ 8 %, Strahl und Kontakt gemeinsam [M] | 4,5 cm breit, flackernd, Licht und Funken am Kontakt, Mündungslicht | Breite in m, Farbe |
| 9f | Fusion | Bolzenzahl, Abstand, Streuung offen (Cartesian Coordinate) [O] | je Strahl der Salve ein Bolzen 110 m/s, 2,5 m lang | Bolzenzahl, m/s |
| 9g | lineare Fusion | Threaded Needle: diffuse Phase ohne Kern [O] | ein Strahl 3,5 cm, 0,22 s, wird schmaler | Dauer, Breite |
| 9h | Bogen | Imperial Needle: Entladefächer 2 Bilder ≈ 22 % beim Lösen [M]; Pfeilfall, Steckdauer offen | Pfeil 70 m/s, Fall 4 m/s², steckt 4 s, Lichtpuls beim Lösen | Fall, Steckdauer |
| 9i | Schrot | Pelletmuster offen [O] | 12 Kugeln (Mitte + Ring 0,5 · + Ring 1,0 ·), Kegel 3,0° halb, Zielen × 0,75 | Anzahl, Kegel |
| 9j | Einschlag Kugel | Einschlagrauch überlagert, Ende offen (Chroma Rush) [O] | Stile bullet/heavy/pellet/energy/arrow: Funken, Staub, Licht, Loch bzw. Brandfleck | Größe, Dauer je Klasse |
| 9k | Einschussloch | – | 5 cm, Kern, aufgeworfener Rand, Ruß, 4 Formen, 30 s dann 2,5 s ausblenden, Pool 96 | Lebensdauer |
| 9l | Leuchtspur | BF6 B36A4: Leuchtspur zur Bildmitte [O]; Destiny nicht gemessen | nur MG: jeder 3. Schuss, 320 m/s, 2,4 m, warmweiß | Häufigkeit, Farbe je Klasse |
| 9m | Revolver-Hülsen | Revolver werfen beim Nachladen aus (Wingman, .357, Annual Skate) [O] | Handfeuerwaffe: beim Marker Eject je verschossene Kammer eine Hülse aus der ausgeschwenkten Trommel; Trommel dreht nach jedem Schuss eine Kammer (0,1 s) | Drehzeitpunkt (Schuss oder Spannen) |
| 9n | Füllstand | – | Granatwerfer: Kopf je Kammer an/aus (Hülse bleibt); MG: Gurt leert sich von unten (4 Patronen), Zählfenster 5 Zellen, Gurtglied je Schuss, Gurtvorschub je Schuss | – |

Granatwerfer nach **teilweisem** Nachladen (9n): Das Laden dreht die Trommel in Schussrichtung weiter, die geladenen Kammern liegen dann
nicht in Schussfolge (physikalisch stimmig nur beim vollen Nachladen). Unity ordnet die Kammern beim ersten Weiterdrehen nach dem Schuss
(`fire_cycle`) in Schussfolge – der Wechsel fällt in die Drehung, danach leert jeder Schuss sichtbar die Laufkammer (Test). Ein Ablauf mit
Gegendrehung bleibt ein Animationsthema für 0.35 „Stance“.
Revolver-Hülsen (9m): die Nachladehaltung der Handfeuerwaffe liegt 5 cm höher (E), damit Trommelende und Hülsen im Bild liegen.
Weitere Daten (Richter 0.34): Spur der Projektile `trail_step_m`/`trail_life_s` (Rakete 0,18 m / 1,8 s, Granate 0,30 m / 0,65 s, Pfeil
0,35 m / 0,18 s), Dauerstrahl `beam_s` 0,15 s, Brandfleck je 3. Takt, Funken 40/s, Mündungslicht 0,10 s – alle E.

## Widersprüche in Motiongen REF 0.24 (dort zu klären)

Motiongen hat acht Widersprüche zwischen Bestand und Glidepath gelistet, aber nicht entschieden ([destiny2] › Glidepath). Entscheiden
muss Motiongen. BASIC hält hier nur fest, welchen Wert es bis dahin verwendet.

| # | Widerspruch (kurz) | betrifft BASIC | BASIC verwendet bis zur Klärung |
|---|---|---|---|
| 1 | Chroma Rush / Gridskipper: Visier „auf der Achse“, „steigt“, „Zoom 2 Bilder vor der Ruhe fertig“ gegen Höhe konstant und Zoom-Ende gleichzeitig ±1 | ja, 1d | Glidepath (vom Koordinator am Bild bestätigt) |
| 2 | Spurgewehr „ADS nicht gesehen“ gegen Prometheus Lens mit ADS (12 Bilder) | BASIC-12 | Glidepath; das Holo nach Visier-Standard 3 passt |
| 3 | roter HUD-Punkt im Zielen (visiere › 7) gegen Hüft-Ring je Typ in Spielclips; Punkt vermutlich aus dem Showcase-HUD | **ja, 4a/4c** | Hüft-Ring nach Glidepath; HUD-Punkt bis zur Klärung zurückgestellt (Frage 4.3) |
| 4 | Gewehr „Sprint tief“, aber Ring 7 s durchgehend sichtbar | schwach, 4a | Sprint = Fadenkreuz aus (Automatik höchstens „^“) |
| 5 | Raketenwerfer „ADS mit Linsenbild“ ist vermutlich ein Scharfschützengewehr | nein (BASIC: eine Kamera) | – |
| 6 | Bogen „im Sprint“ ist ein Waffenwechsel | nein (Bogen-Sprint offen) | – |
| 7 | Startmarker um 1–3 Bilder verschieden (MG, kurze Fusion, lineare Fusion, Sprint-Hub Handfeuerwaffe) | nein (unter der BASIC-Genauigkeit) | – |
| 8 | Scourge-Plateau ≤ 0,6 % H gegen Sprint-Hub 10–11 % H | **ja, 3a** | 0.23 „Stride“: 10–11 % H |

Rückfrage an Motiongen zu 3 und 4 über Sightline, sobald diese Liste gemergt ist.

## Nicht messbar oder offen (nur gezählt)

Aus den Abschnitten „Offen und nicht messbar“ der zwölf Docs: zusammen **84 Punkte**. visiere 7, proportionen 5, rueckstoss 4,
zielbewegung 10, oberflaechen 5, muendung 7, inspektion 9, huefte 7, nachladen 8, wechsel 6, waffenwerte 9, zielhilfe 7. Dazu
Glidepath: Sprint bei 13 der 17 Typen offen, Visier-Anflug bei Scout übertragen und bei kurzer Fusion nur gesichtet, Hüft-Fadenkreuz bei
6 Typen offen (Scout, Seitenwaffe, Schrot, Spur, Gleve und Raketenwerfer nur 1 Clip). Gehen-Wippen, Atemperiode und Rückstoß ohne
Spielereingabe sind für Destiny 2 grundsätzlich nicht belegt. BASIC stellt dazu keine Frage, die Messung bleibt bei Motiongen.

## Ergebnis

Alle 20 Fragen sind am 25.10.2026 beantwortet, keine ist offen. **Umsetzen:** 1.1, 1.2, 1a, 1d, 2.1, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3,
5.1, 5.2, 5.3, 6.1, 6.2, 7.1, 8.2, dazu der Test 6c. **Nicht umsetzen:** 2.2 (keine Option für die Waffenlage), 8.1 (Budget bleibt
nach Funktionen). **Zurückgestellt:** ~~5.4 Hülsen~~ (am 26.10.2026 auf A geändert, in 0.16 gebaut), 7.2 Wertetabelle (bis eine zweite Waffe in Unity spielbar ist), 7.3 Zielhilfe (bis
Controller-Eingabe Thema ist), der HUD-Punkt aus 4.3 (bis Motiongen Widerspruch 3 klärt).

## Messungen (25.10.2026)

Schritt 2 der Reihenfolge, Patch „BALLON Patch messen“. **Nur gemessen, kein Wert geändert.** Alle Lagen in % von Bildbreite B / Bildhöhe H,
Ursprung oben links, Bezugsbildwinkel 75° horizontal (16:9, Visier-Standard 3). Messwerkzeuge: [`tools/messen.py`](../tools/messen.py)
(Blender: Anker und Waffenkontur ins Bild projiziert) und [`tools/messen_bild.py`](../tools/messen_bild.py) (Raster, Ringprofil,
Waffenmaske, Zoom-Zeitlinie). Unity-Aufnahmen: `-ballonFps 60 -ballonKey 1` (Messhilfe in `Bootstrap.cs`, nur Aufnahme; Waffe und Arme auf
Schlüsselfarbe, Welt aus). Belege unter `~/Library/Caches/CubeEscapeBallon/messen/belege/`. Frisch gerendert aus diesem Stand (`ego_build.py --stills`,
`sight_options.py`), Unity aus dem eigenen Worktree gebaut.

| Punkt | Messung | Unsicherheit | Destiny (Liste) | Abweichung BASIC − Destiny |
|---|---|---|---|---|
| **2.1** Hüftlage, Mündung | Blender-Still `hip_ego` (1600 × 900, Bild 0): Socket_Muzzle **x 58,8 / y 49,6**; sichtbare Spitze x 57,8; Unity-Messlauf Bild 30 (0,5 s, Ruhe): Spitze x 58,2–59,4 / y 49,3 | ±0,1 pp (Projektion), ±1 pp (Anker gegen sichtbare Spitze) | x 54–59 / y 60–71 | x: im Band; y: **10,4–21,4 pp höher** als das Band |
| **2.1** hintere Visieröffnung | Socket_Sight (hintere Kante des Visiergehäuses) x **80,3** / y 49,5; Absehen x 77,1 / y 48,5 | ±0,1 pp, Anker ±1 pp | 7–34 pp rechts der Mündung | 21,5 pp rechts: im Band |
| **2.1** Waffenkontur | Waffenteile: links x 57,8, oben y 44,8; rechts und unten über den Bildrand hinaus (Eckpunkte bis x 185 %, y 217 %); im Bild berührt die Waffe den rechten und unteren Rand | – | „reicht bis zum rechten und unteren Rand“ | wie Destiny |
| **1a** Scout-Ring | `rohr_ziel.png` (Scout BASIC-03 v2.1, 960 × 540, Zeile 270 durch die Ringmitte): außen 320–641 = 322 px (33,5 % B); Kante der dunklen Innenwand 354–599 = 246 px (25,6 % B); lichtes Glas 382–588 = 207 px. **außen ÷ Ringinnenkante 1,31, außen ÷ lichtes Glas 1,56** | ±2 px je Kante → ±0,02 | 1,28–1,30 | Innenkante: +0,01 bis +0,03; Glas: +0,26 bis +0,28 |
| **3.1** Sprint-Hub | Unity `feel`, 60/s, Sprint 1 Bild 36–144 (1,8 s ≈ 5,7 Zyklen), Sprint 2 Bild 354–408; Auswertung Bild 54–144 (4,7 Zyklen) und Bild 354–408. Spitze–Spitze (Median): **vertikal** Schwerpunkt Waffe + Arme 2,1–2,3 % H (1,7–2,5), Oberkante 5,1–5,7 % H (3,8–6,2); **seitlich** Mündungsende (linke Kante) 7,0–8,7 % B (6,3–10,7), Schwerpunkt 0,3–1,4 % B. **Frequenz 0,317 s = 3,16 Hz** (Extrema Bild 79▼ 89▲ 98▼ 107▲ 117▼ 127▲ 136▼) | ±0,3 pp H / ±0,2 pp B je Extremwert (1 px bei 640 × 360); der Messpunkt der Destiny-Zahl ist nicht bekannt | ≈ 10–11 % H / 13 % B | vertikal 4,3–8,9 pp kleiner (Oberkante 4,3–5,9, Schwerpunkt 7,7–8,9); seitlich 4,3–6,0 pp kleiner (Mündungsende); Frequenz wie Messwert 3,16 Hz |
| **1d** Zoom gegen Modell, Holo | Unity 60/s, Weltzoom aus dem FOV je Bild (46,692° → 35,460°, Tangente × 1,350), Modell aus der Bildbewegung der Waffe (Schwellen 5 / 10 / 20 % der Spitzenbewegung). **Hüfte → Zielen** (Eingabe Bild 192): Zoom Bild 193–210 (18 Bilder); Modell 195–215 / 196–214 / 196–213 → Zoom beginnt **2–3 Bilder vor** dem Modell, endet 3–5 Bilder vor ihm. **Zielen → Hüfte** (Eingabe Bild 276): Zoom 276–293; Modell 277–305 / 278–301 / 279–294 → Start −1 bis −3, Ende −1 bis −12 (das Modell federt nach). **Sprint → Zielen** (Eingabe Bild 408): Modell ab Bild 408, Zoom erst 419–436 → Zoom beginnt **11 Bilder nach** dem Modell, Ende 0 bis +2. Zweiter Durchlauf (Bild 492, Zielen → Hüfte) wie der erste. | ±1 Bild (60/s) plus 1–2 Bilder je nach Schwelle | Zoom beginnt 0–2 Bilder **nach** dem Modell, Ende gemeinsam ±1 | Hüfte → Zielen: Start 2–5 Bilder früher, Ende 2–6 Bilder früher; Sprint → Zielen: Start 9–11 Bilder später, Ende im Band |

**Zielfernrohr (1d):** nicht messbar. Unity trägt nur BASIC-01 mit Holo; der Weltzoom ist dort ein Wert für alle Klassen (`adsZoom` 1,35, die
Klassenwerte aus 1.2 folgen in Schritt 3). Ein Ego-Still oder eine Aufnahme mit Zielfernrohr gibt es nicht; das Scout-Zielbild aus 1a ist kein Ego-Still.

**Methode kurz.** *Lage:* Anker und alle Eckpunkte der ausgewerteten Waffennetze werden mit der Ego-Kamera (75° horizontal) projiziert
(`world_to_camera_view`), Bildkontrolle mit Raster und Marken über dem Still. *Ring:* Helligkeitsprofil einer Bildzeile durch die Ringmitte, Kanten
bei Sprung gegen Hintergrund (> 6 Stufen), dunkler Innenwand (< 80) und Glas (≥ 100). *Sprint:* Aufnahme mit Waffe und Armen auf Schlüsselfarbe,
je Bild (auf 640 × 360 verkleinert) Schwerpunkt, linke und obere Kante der Waffenmaske, lokale Extrema, Abstände Spitze–Spitze und Periode.
*Zoom:* FOV je Bild aus `zoom.csv`; Modellbewegung = Summe der Pixelunterschiede aufeinanderfolgender Waffenbilder, normiert auf ihr Maximum. Die Schwelle
bestimmt Start und Ende; deshalb stehen drei. Der Sprint-Hub hängt vom Messpunkt ab (Schwerpunkt, Oberkante und Mündungsende bewegen sich verschieden,
weil die Waffe auch rollt); welcher Punkt Destiny entspricht, ist offen, hier nicht entschieden.

## Messungen nach Schritt 4 (26.10.2026)

BALLON 0.15 „Plumb“ ([Bericht](versions/0.15-plumb.md)). Gleiche Bezugsgrößen wie oben (75° horizontal, 16:9, % von B/H, Ursprung oben links).
Bildmessung wie in Schritt 2: Unity-Build aus dem eigenen Worktree, `-ballonFps 60 -ballonKey 1`, `tools/messen_bild.py`. Neu: im Messlauf wird
kein Fadenkreuz mehr ins Bild gestempelt (seit 0.13 lag das Sprint-„^“ in der Maske und hielt die Oberkante bei 50 %). Dazu die Unity-Tests
mit `EgoScreen` (Projektion der Anker und der Kanten der Netzgrenzen). Mit den alten Daten liefert `EgoScreen` die Hüftlage 58,8 / 49,6 %,
also genau den Blender-Messwert aus Schritt 2. Belege unter `~/Library/Caches/CubeEscapeBallon/plumb/`.

| Punkt | vorher (Schritt 2 bzw. alter Code) | nachher (0.15) | Destiny (Liste) |
|---|---|---|---|
| **2.1** Hüftlage, Mündung | x 58,8 / y 49,6 % | x **58,1** / y **63,1** % (`Hueftlage_im_Destiny_Band`) | x 54–59 / y 60–71 |
| **2.1** hintere Visieröffnung | x 80,3 % (21,5 pp rechts) | x 77,4 / y 67,5 % (**19,3 pp** rechts) | 7–34 pp rechts |
| **3.1** Sprint, Oberkante vertikal | 5,1–5,7 % H | **9,5 / 8,9** % H (zwei Sprints; Silhouette im Test 10,5) | ≈ 10–11 % H |
| **3.1** Sprint, linke Kante seitlich | 7,0–8,7 % B | **12,7 / 13,7** % B (Silhouette 13,8) | ≈ 13 % B |
| **3.1** Sprint, Schwerpunkt | vertikal 2,1–2,3 % H, seitlich 0,3–1,4 % B | vertikal 4,0 / 3,8 % H, seitlich 3,1 / 3,0 % B | Messpunkt offen |
| **3.1** Frequenz | 3,16 Hz | 3,16 Hz (seitlich 1,58 Hz) | 3,16 Hz |
| **1d** Hüfte → Zielen (Schwelle 5/10/20 %) | Zoom − Modell: Start −2…−3, Ende −3…−5 | Start **+2 / +1 / 0**, Ende **−1 / 0 / +1** | Start 0…+2, Ende ±1 |
| **1d** Sprint → Zielen | Start +11, Ende 0…+2 | Ende −1 / 0 / +1; Start am Bild +5, weil das Sprint-Wippen schon ab dem Eingabebild Bewegung zeigt; an der Grundhaltung (Test) +1 | wie oben |
| **1d** Zielen → Hüfte | Start −1…−3, Ende −1…−12 | Start +1 / 0 / 0, Ende −12 / −2 / −1 (das Modell federt nach) | – |
| **6.1** Wechsel (60/s) | Wegstecken 0,60 s (Marker); Waffe bis 0,27 s sichtbar | Waffe bis **0,150 s** sichtbar, `Holstered` **0,267 s**, leer **0,133 s**, erstes neues Bild 0,300 s, Hüfte 0,517 s, ruhig 0,750 s | Wegstecken 0,08–0,27 s, leer 0,07–0,30 s, Hüfte 4–14 Bilder nach dem ersten Bild |
| **5.1** Rückstoß im Zielen, Viererstoß | Visier durch den Rückstoß 1,03 % H (alter Modellkick, Gegenprobe); Welt: bleibendes Hochziehen 0,09°/Schuss (rechnerisch ≈ 1,4 % H, ohne Rückkehr) | Welt **4,32 % H**, Visier **0,12 % H**, Rückkehr unter 0,25 % H nach **0,483 s**, kein Unterschwingen | Welt ≈ 4 pp H, Visier < 1 pp, Basis nach 36 Bildern (0,6 s) |
| **5.2** Bahn, 12 Schuss Hüfte | bleibend 0,18°/Schuss (≈ 0,36 % H), keine Seitenbahn, keine Erholung | **12,0 % H**, seitlich **1,5 % B**, dreimal dieselbe Form, Erholung 0,60 s | ≈ 1 pp H je Schuss, ≤ 2,2–2,5 pp B, Rücklauf 0,4 s ins ±3-pp-Band |
| **5.2** Salven (Daten im Test umgestellt) | Salven nicht getrennt | 3 Schuss im Abstand 4 Bilder, 22 Bilder Pause; Erholung in der Pause, keine in der Salve | Gridskipper: Stufe ≈ 4 pp je Salve, Erholung in der Pause |

**Lesart Sprint seitlich:** Die linke Kante (Maße oben) pulsiert mit der Schrittfrequenz 3,16 Hz, nicht mit der Seitenfrequenz 1,58 Hz.
Sie misst also vor allem den vertikalen Hub dort, wo Lauf und linker Arm den unteren Bildrand schneiden. Das galt schon für die
Schritt-2-Werte 7,0–8,7 % B. Die echte Seitenbewegung (Schwerpunkt, 1,58 Hz) liegt bei 3 % B. Welcher Messpunkt der Destiny-Zahl 13 % B
entspricht, ist weiter offen (siehe oben); eine reine Seitenbewegung von 13 % B bräuchte nach dem Schwerpunktmaß rund den vierfachen Seitenhub (≈ 90 statt 22 mm).

## Messungen Schritt 6, MP (26.10.2026)

BALLON 0.18 „Quickdraw“ ([Bericht](versions/0.18-quickdraw.md)): erste übertragene Klasse Maschinenpistole BASIC-06 „Kurzläufer v2.1“
(Nutzerwahl 26.10.2026). Klassenwerte als Daten in `basic/arms/ego.py › CLASSES`, die Automatik behält alle Werte. Gleiche Bezugsgrößen
wie oben (75° horizontal, 16:9, % von B/H, Ursprung oben links). Lagen aus `EgoScreen` (Unity-Tests) und am Ego-Still mit Mittenkreuz
(`tools/messen_bild.py grid`), Zeiten am Live-Controller bei 60/s. Belege unter `~/Library/Caches/CubeEscapeBallon/quickdraw/`.

| Punkt | Automatik (unverändert) | MP (0.18) | Destiny MP (Liste, Motiongen REF destiny2) |
|---|---|---|---|
| **2b / 2.1** Hüfte, Mündung | x 58,1 / y 63,1 % | x **58,0** / y **62,9** % (`Hueftlage_der_MP_im_Band`) | Band Kurzwaffen x 53–71 / y 59–84; MP ≈ 57/61 und 58/62 |
| **2b / 2.1** Hüfte, Absehen (Holo-Mitte) | x 74,6 / y 65,8 % | x **65,5** / y **60,0** % | Holo ≈ 62–68 / 57–58 |
| **2b** Waffenkontur Hüfte | x 57–99 / y 60–100 % | x 57–92 / y 56–100 % | Körper ≈ 56–90 (100) × 47–100 % |
| **3b / 3.2 A** Sprint-Trageform | quer, Oberseite **−20°** (nach rechts), Rollen −35° | tief, Oberseite **+40°** (nach links), Mündung **42,9 / 79,9** %, Absehen **52,0 / 72,0** % | tief, nach links gerollt; Mündung ≈ 43/80, Holo-Ring ≈ 52/72 |
| **3c** Sprint-Frequenz und Hub | 3,16 / 1,58 Hz, 22/18 mm | gleich (gemeinsame Daten) | nicht gemessen |
| **4d** Anflug erste Bewegung → Ruhe, 60/s | `aim_in` 10 Bilder bei 30/s → **20 Bilder** (0,333 s) | `aim_in` **3** Bilder bei 30/s → **12 Bilder** (0,200 s); mit 4 Bildern waren es 13 | Automatik 20, MP 8–12 |
| **4d** Zielen → Hüfte | `aim_out` 8 Bilder bei 30/s | `aim_out` 2,4 Bilder (Verhältnis 0,3) | MP ADS aus → ruhig 10–11 Bilder |
| **6.1** Wechsel Taste 1 ↔ 2, 60/s | Waffe bis 0,150 s sichtbar, `Holstered` 0,267 s, leer **0,133 s**, Pause `Empty` → `Draw` 0,033 s, erstes neues Bild 0,300 s, Hüfte 0,517 s – wie Q | gleich | Wegstecken 0,08–0,27 s, leer 0,07–0,30 s |

**Ruhe (4d):** Bildweg des Absehens (Grundhaltung nach dem Feder-Nachlauf, ohne Atmen) je Bild unter 0,09 % – ein fester Bildwert wie
Motiongens Bilddifferenz, nicht relativ zum Weg; so gemessen braucht die Automatik genau die Destiny-Zeit 20 Bilder. Relativ zum Weg (0,3 %)
wären es bei der MP 13 Bilder, weil ihr Weg kürzer ist (18,5 statt 29,3 % B). Der MP-Wert liegt am oberen Rand des Destiny-Bands.

## Messungen Schritt 6, Scout (26.10.2026)

BALLON 0.20 „Spotter“ ([Bericht](versions/0.20-spotter.md)): zweite übertragene Klasse Scout BASIC-03 „Fernblick v2.1“ (Modell aus 0.19
„Saddle“ unverändert). Gleiche Bezugsgrößen wie oben (75° horizontal, 16:9, % von B/H, Ursprung oben links); Lagen aus `EgoScreen`
(Unity-Tests) und am Ego-Still mit Mittenkreuz, Zeiten am Live-Controller bei 60/s. Belege unter `~/Library/Caches/CubeEscapeBallon/spotter/`.

| Punkt | Automatik (unverändert) | Scout (0.20) | Destiny-Scout (Motiongen REF destiny2, huefte) |
|---|---|---|---|
| **2.1** Hüfte, Mündung | x 58,1 / y 63,1 % | x **57,0** / y **62,7** % (`Hueftlage_des_Scouts_im_Band`; Haltung der Automatik) | Tone Patrol ≈ 57/63, Call to Serve 58/61; Band lange Waffen x 54–59 / y 60–71 |
| **2.1** Okularende rechts der Mündung | 19,3 pp | **24,4** pp (x 81,3 / y 72,2 %) | 7–34 pp |
| **3.2 A** Sprint-Trageform | Oberseite −20° | wie die Automatik: Oberseite **−20,3°**, Mündung **21,9 / 86,3** % | Scout-Sprint nicht gemessen (kein Clip) |
| **4d** Anflug erste Bewegung → Ruhe, 60/s | 20 Bilder | `aim_in` **7** Bilder bei 30/s → **17 Bilder** (0,283 s) | Tone Patrol ≈ 22 (Bestand), Patron 12–15 [M]; Scharfschütze 15, Impuls 20 |
| **4d** Zielen → Hüfte | `aim_out` 8 Bilder bei 30/s | `aim_out` **5** Bilder (0,167 s) | Dead Man's Tale ADS aus → Hüfte 0,17 s |
| **1d** Zoom gegen Modell (Hüfte → Zielen) | Start 0, Ende 0 (5-%-Schwelle) | Start **0**, Ende **−1** mit `zoom_start` 0,2 (mit 0,05: Start −2) | Holo: Start 0…+2, Ende ±1 |
| **1d** Linsenbild | – | ab Bild **12** von 19 (Okular an der Nahebene, Auge 60 mm vor der Kamera), 7 Bilder vor dem Ende der Restbewegung; vorher füllt das Okular kurz das Bild | Scharfschütze: Okular füllt 4 Bilder das Bild, Linse nach dem Modell; Scout: Linse klar in ≤ 3 Bildern |
| **Visier-Standard 3** Öffnung im Zielen | Holo | **21,5** % B (Netz, Test) · am Unity-Bild 20–24 % B | 20–26 % B; Patron 20,8 % B |
| **1a** Ring außen ÷ Innenkante / ÷ Glas | – | Unity-Zielbild **1,32 / 1,40** (320 / 243 / 228 px bei 960 B; Glas-Kante im Unity-Bild schmaler) | Blender 1,31 / 1,56; Destiny 1,28–1,30 |
| Glas getönt | – | Parcours **1,3–2,6 %** heller als außen | ≤ 5 % (Destiny 0,98–1,01) |
| Kadenz, Feuerart | 720/min Dauerfeuer | **180/min Einzelfeuer** (Spec `semi_auto`), Magazin 15 | Tone Patrol 180/min, 15 Schuss |

## Messungen Schritt 6, Impuls und Portalkanone (27.10.2026)

BALLON 0.22 „Volley“ ([Bericht](versions/0.22-volley.md)): dritte und vierte übertragene Klasse – Impulsgewehr BASIC-02 v2.1 (Visier H4
aus 0.21 unverändert) und Portalkanone BASIC-T01 v2.1 als Klasse „Werkzeug“ (Modell aus 0.17). Gleiche Bezugsgrößen wie oben; Lagen aus
`EgoScreen` (Unity-Tests) und am Ego-Still mit Mittenkreuz, Zeiten am Live-Controller bei 60/s. Belege unter `~/Library/Caches/CubeEscapeBallon/volley/`.

| Punkt | Automatik (unverändert) | Impuls (0.22) | Portalkanone (0.22) | Destiny / Portal 2 |
|---|---|---|---|---|
| **2.1** Hüfte, Mündung | x 58,1 / y 63,1 % | x **57,9** / y **63,4** % (`Hueftlage_des_Impulses_im_Band`; mit der Automatik-Hüfte 59,7/65,6 – außerhalb) | Achskrone x **56,9** / y **71,1** %, quer gestellt, beide Kerne sichtbar (Nutzerhinweis) | lange Waffen x 54–59 / y 60–71, Gridskipper ≈ 57/61; Portal 2 Rohrende ≈ 57/75, beim Gehen 54–63 / 68–75 |
| **3.2 A** Sprint-Trageform | Oberseite −20° | wie die Automatik: −20,3°, Mündung 29,6 / 87,1 % | E (Klasse Werkzeug, nicht gemessen): Oberseite +29,8°, Achskrone 44,3 / 80,3 % (Kurzwaffen-Trageform wie die MP) | Impuls-Sprint nicht gemessen; Portal 2 ohne Sprintpose |
| **4d** Anflug erste Bewegung → Ruhe, 60/s | 20 Bilder | `aim_in` 10 Bilder bei 30/s → **20 Bilder** (0,333 s) | kein Zielen (Nutzerwahl A) | Automatik/Impuls/MG 20 |
| Weltzoom, Hüftform | 1,9, `ring_dot` | **2,0** (Holo, seit 0.13), `ring_dot` 3,2 % H | 1 (kein Zielen), `ring_dot` 4,5 % H ohne Aufgehen (E) | Impuls 2,10 [M] |
| Feuerart | 720/min Dauerfeuer | **Salve** aus der Spec (`burst_3`): 3 Schuss im Takt 4 Bilder bei 60/s (900/min), Salvenbeginn alle 20 Bilder (540/min gemittelt), Magazin 36 | Linksklick Portal A, Rechtsklick Portal B, Abklingzeit 0,25 s, unbegrenzt, Reichweite 24 m | Gridskipper: Takt 4 Bilder [M], Menü 540/min, 36 Schuss [S]; Cube Escape Q-CE-14/15 |
| **5.2** Bahn je Salve | Säule 1 % H je Schuss | Stufe **4,0 % H** je Salve, Erholung ab 0,10 s mit 5 Hz (≈ 80 % in der Pause; gemessen 75 %) | keine Bahnstufe (Ring und Treffermarke als Rückmeldung) | Gridskipper: ≈ 4 pp je Salve, ≈ 80 % zurück zwischen den Salven |
| **5.3 A** Mündungsfeuer im Zielen | 13,1 % der Öffnung | **13,5 %** der H4-Öffnung (`./check`; Grenze 20) | kein Mündungsfeuer | Destiny-Impuls ≈ 5 % |
| **6.1** Wechsel 1 → 4 → 5 → 2 | – | Holstered 0,267 s, leer 0,133 s, erstes neues Bild 0,300 s, Munition je Waffe bleibt | gleich | Wegstecken 0,08–0,27 s, leer 0,07–0,30 s |

## Reihenfolge der Umsetzung (Vorschlag)

Leitlinie: zuerst, was ohne Rendern geht und eine Regel verletzt; dann messen; dann die Bewegung; zuletzt neue Effekte. Einstufung
Patch oder Version nach den globalen Regeln (bis ≈ 100 Zeilen Diff ohne Format- oder Vertragsänderung = Patch). Unity-Änderungen nur in
der Testkopie und mit `ce lock unity`, Messbilder mit `ce lock gpu`.

| Schritt | Inhalt | Antworten | Art | Sperre | Voraussetzung |
|---|---|---|---|---|---|
| 1 | **Unity-Abgleich (erledigt 26.10.2026, Patch unity-abgleich, Messwerte in [unity.md](unity.md) › Tests):** Kadenz 720/min, Sway kritisch gedämpft, Schuss-Ring und Treffer-X in Orange, Test Nachlade-Abbruch vor und nach `MagIn`, Herkunft von `inspect` berichtigt | 7.1, 3.3, 4.3, 6c, 6.2 | Patch | unity | – |
| 2 | **Messen (erledigt 25.10.2026, [Messungen](#messungen-25102026)):** ein Ego-Still je Haltung mit Mittenkreuz (Hüftlage, Scout-Ring), Unity-Aufnahme `feel` für Sprint-Hub und Zoom-Timing; Werte in diese Datei und `data/review.json` | 1a, 1d, 2.1, 3.1 | Patch (nur Messung) | gpu, unity | – |
| 3 | **Weltzoom und Hüft-Fadenkreuz (erledigt 26.10.2026, BALLON 0.13 „Hipfire“, [Bericht](versions/0.13-hipfire.md)):** Weltzoom Scout 2,0 / Handfeuerwaffe 1,15 / MP 1,45, Unity zoomt mit dem Klassenwert (Automatik 1,9 statt fest 1,35); Hüftformen `ring_dot` (Automatik, Impuls, MG), `brackets` (Handfeuerwaffe, neu), `caret` (Scharfschütze und Sprint der Automatik, neu) im Katalog `reticles.py`; ausblendendes Hüft-Fadenkreuz in Unity (Hüfte, Sprint, Zielen, Nachladen, Ziehen) | 1.2, 4.1, 4.2 | Version | unity | 1 |
| 4 | **Bewegung (erledigt 26.10.2026, BALLON 0.15 „Plumb“, [Bericht](versions/0.15-plumb.md), [Messungen](#messungen-nach-schritt-4-26102026)):** Hüftlage auf das Destiny-Band, Sprint-Hub ≈ 10 % H / 13 % B, Wechsel mit `holster` 0,27 s und leerer Sicht, Zoom mit dem Modell (1d), Rückstoß im Zielen in die Welt, feste Rückstoß-Bahn mit zweistufigen Salven; Ego-Clips neu gerendert | 2.1, 3.1, 6.1, 1d, 5.1, 5.2 | Version | unity, danach gpu | 2 (Messwerte) |
| 5 | **Mündungsfeuer und Hülsen (erledigt 26.10.2026, BALLON 0.16 „Flash“, [Bericht](versions/0.16-flash.md)):** Blitz in Blender und Unity gleich (1 Bild bei 30/s, gleiche Dauer bei höherer Bildrate, reine Emission ohne Bloom, im Zielen ≤ 20 % der Holo-Öffnung, gemessen 13,1 %); Hülsen je Schuss aus dem Auswurffenster nach rechts und rechts unten, Feld `EJECT` je Waffe, Pool in Unity | 5.3, 5.4 (A seit 26.10.) | Version | gpu, unity | 4 (Rückstoß im Zielen) |
| 6 | **Beim Ego-Übertrag je Klasse:** Hüfthaltung, Sprint-Trageform und Anflugdauer je Klasse · **MP übertragen (26.10.2026, BALLON 0.18 „Quickdraw“, [Bericht](versions/0.18-quickdraw.md), [Messungen](#messungen-schritt-6-mp-26102026)):** Maschinenpistole BASIC-06 als zweite spielbare Waffe (Taste 2), Klassenwerte als Daten in `ego.CLASSES` · **Scout übertragen (26.10.2026, BALLON 0.20 „Spotter“, [Bericht](versions/0.20-spotter.md), [Messungen](#messungen-schritt-6-scout-26102026)):** Scout BASIC-03 v2.1 als dritte Waffe (Taste 3), Hüfte und Sprint wie die Automatik (lange Waffe), Anflug 7 Bilder bei 30/s, Einzelfeuer aus der Spec, Zielfernrohr nach Visier-Standard 3 in Unity · **Impuls und Portalkanone übertragen (27.10.2026, BALLON 0.22 „Volley“, [Bericht](versions/0.22-volley.md), [Messungen](#messungen-schritt-6-impuls-und-portalkanone-27102026)):** Impulsgewehr BASIC-02 v2.1 (Taste 4) mit eigener Hüfte (lange Waffe, Band 54–59 / 60–71 %), Sprint wie die Automatik, Anflug 10 Bilder bei 30/s (Destiny 20 bei 60/s), Salve aus der Spec (3 Schuss, 900/min in der Salve, 540/min gemittelt, Bahnstufe ≈ 4 pp H je Salve); Portalkanone BASIC-T01 v2.1 (Taste 5) als Klasse „Werkzeug“: Hüfte nach Portal 2, Sprint E, ohne Zielen und Nachladen, Linksklick Portal A / Rechtsklick Portal B (Nutzerwahl A); weitere Klassen offen | 2.1, 3.2, 4d | je Klasse in der Version der Waffe | gpu, unity | 3, 4 |
| 7 | **Scout-Umbau (erledigt 26.10.2026, BALLON 0.19 „Saddle“, [Bericht](versions/0.19-saddle.md)):** Gehäuseoberkante unter dem Rohr als Buckel angehoben, Hals weg (flacher Rohrsattel auf kurzer Schiene), Visierhöhe 65 mm; Visier über Gehäuse 0,030 L; Prüfung `tools/test_sight_seat.py` in `./check`; 1a am neuen Zielbild nachgemessen | 1.1 | in der Version des Umbaus | gpu | nach BALLON 0.12 „Silhouette“ (nicht parallel an `w03`) |
| 8 | **Bei der nächsten Skin-Arbeit:** flächige Sprenkel nur im Skin `gebraucht` | 8.2 | Patch | gpu | – |

Zwischen den Schritten: die Rückfrage an Motiongen zu den Widersprüchen 3 und 4 (über Sightline). Nach der Antwort entscheidet BASIC
über den HUD-Punkt aus 4.3; das ist keine neue Nutzerfrage, solange Motiongen den Punkt im Spielbild belegt oder widerlegt.

Befund aus Schritt 1 (für Schritt 4, **erledigt in 0.15**): Der Clip `fire_hip` hatte die Herkunft „M 720/min ≈ 1 Schuss je 2,5 Bilder“, seine
Schussbilder `fire` lagen aber 2 Bilder auseinander (13 Schüsse in Bild 2–25, ≈ 940/min; `fire_ads` gleich). Seit 0.15 liegen sie wie
`gameplay.rpm` 2,5 Bilder auseinander (`ego.shots_720`: 2, 4, 7, 9, …, abwechselnd 2 und 3; `sprint_to_fire` ebenso), die Clips sind neu gerendert.

[visiere]: https://github.com/ffunkfabian-hash/cubeescape-motiongen/blob/4fa6f27/docs/visiere.md
[proportionen]: https://github.com/ffunkfabian-hash/cubeescape-motiongen/blob/4fa6f27/docs/proportionen.md
[rueckstoss]: https://github.com/ffunkfabian-hash/cubeescape-motiongen/blob/4fa6f27/docs/rueckstoss.md
[zielbewegung]: https://github.com/ffunkfabian-hash/cubeescape-motiongen/blob/4fa6f27/docs/zielbewegung.md
[oberflaechen]: https://github.com/ffunkfabian-hash/cubeescape-motiongen/blob/4fa6f27/docs/oberflaechen.md
[muendung]: https://github.com/ffunkfabian-hash/cubeescape-motiongen/blob/4fa6f27/docs/muendung.md
[inspektion]: https://github.com/ffunkfabian-hash/cubeescape-motiongen/blob/4fa6f27/docs/inspektion.md
[huefte]: https://github.com/ffunkfabian-hash/cubeescape-motiongen/blob/4fa6f27/docs/huefte.md
[destiny2]: https://github.com/ffunkfabian-hash/cubeescape-motiongen/blob/4fa6f27/docs/destiny2.md
[nachladen]: https://github.com/ffunkfabian-hash/cubeescape-motiongen/blob/4fa6f27/docs/nachladen.md
[wechsel]: https://github.com/ffunkfabian-hash/cubeescape-motiongen/blob/4fa6f27/docs/wechsel.md
[waffenwerte]: https://github.com/ffunkfabian-hash/cubeescape-motiongen/blob/4fa6f27/docs/waffenwerte.md
[zielhilfe]: https://github.com/ffunkfabian-hash/cubeescape-motiongen/blob/4fa6f27/docs/zielhilfe.md
[auswertung]: https://github.com/ffunkfabian-hash/cubeescape-motiongen/blob/4fa6f27/docs/auswertung.md
[standard]: https://github.com/ffunkfabian-hash/cubeescape-motiongen/blob/4fa6f27/docs/standard.md
