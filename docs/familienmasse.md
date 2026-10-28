<!-- erzeugt von tools/make_docs.py – nicht von Hand ändern -->
# Familienmaße Stil v2.1

Gemessen am gebauten Modell (`data/specs/<Waffe>-v2.1.spec.json`, mit Fasen, Visier montiert, Ruhelage). Startpunkt für
neue Waffen der Familie: ähnliche Klasse suchen, Lagen übernehmen, Abweichungen im Modul-Docstring begründen
([stilhandbuch.md](stilhandbuch.md) §6/§7). Nach jedem Vollrendering `tools/sync_specs.py` und `tools/make_docs.py`.

## Lagen

mm relativ zu `Socket_Hand` (Griffachse), f vorn, u oben. Mündung f = Stirn der Mündung, Heck f = hinterste Kante
(negativ = hinter dem Griff). Visierhöhe = Visierlinie über der Laufachse (Soll 66 ± 4 mm; Kimme/Korn mit eigener Linie Träger + 11 mm, dort gilt sie nicht), Augenabstand = Augenpunkt bis Glas, Objektiv bzw. Kimme.

| Waffe | L × H × B | Laufachse u | Mündung f | Heck f | Visierlinie u | Visierhöhe | Augenabstand | Stützhand f / u | Magazinschacht f / u | Schwerpunkt f / u | Teile / Dreiecke |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BASIC-01-v2.1 Automatikgewehr | 915 × 260 × 52 | 106 | 616 | -299 | 169 | 63.0 | 90 (Reflex-/Holovisier) | 282 / 95 | 108 / 70 | 79 / 84 | 72 / 33450 |
| BASIC-02-v2.1 Impulsgewehr | 816 × 255 × 51 | 100 | 512 | -304 | 164 | 64.0 | 90 (Reflex-/Holovisier) | 290 / 80 | 99 / 62 | 68 / 79 | 57 / 28710 |
| BASIC-03-v2.1 Scout-Gewehr | 1023 × 259 × 47 | 96 | 721 | -302 | 161 | 65.0 | 90 (Zielfernrohr) | 300 / 90 | 110 / 62 | 53 / 80 | 58 / 30850 |
| BASIC-04-v2.1 Handfeuerwaffe | 306 × 184 × 45 | 71 | 261 | -42 | 103 | 32.0 | 70 (Kimme/Korn) | -4 / -34 | 78 / 57 | 93 / 44 | 20 / 9356 |
| BASIC-05-v2.1 Pistole | 239 × 190 × 34 | 74 | 193 | -43 | 103 | 29.0 | 70 (Kimme/Korn) | -4 / -34 | 9 / 34 | 74 / 30 | 25 / 7588 |
| BASIC-06-v2.1 Maschinenpistole | 547 × 291 × 47 | 82 | 326 | -221 | 147 | 65.0 | 90 (Reflex-/Holovisier) | 230 / 24 | 9 / 40 | 22 / 53 | 49 / 18172 |
| BASIC-08-v2.1 Schrotflinte | 869 × 222 × 52 | 100 | 602 | -267 | 139 | 39.0 | 70 (Kimme/Korn) | 310 / 46 | 122 / 32 (Ladeklappe) | 118 / 74 | 36 / 12798 |
| BASIC-09-v2.1 Scharfschützengewehr | 1135 × 268 × 72 | 96 | 807 | -328 | 162 | 66.0 | 90 (Zielfernrohr, Vollbild) | 340 / 52 | 112 / 20 | 103 / 75 | 47 / 21626 |
| BASIC-10-v2.1 Fusionsgewehr | 701 × 254 × 47 | 96 | 420 | -280 | 162 | 66.0 | 90 (Reflex-/Holovisier) | 265 / 56 | – | 49 / 72 | 45 / 25456 |
| BASIC-11-v2.1 Lineares Fusionsgewehr | 1098 × 256 × 50 | 92 | 729 | -328 | 158 | 66.0 | 90 (Zielfernrohr) | 350 / 42 | – | 126 / 75 | 53 / 29610 |
| BASIC-12-v2.1 Spurgewehr | 777 × 253 × 49 | 96 | 496 | -277 | 162 | 66.0 | 90 (Reflex-/Holovisier) | 259 / 79 | – | 55 / 75 | 50 / 26096 |
| BASIC-15-v2.1 Maschinengewehr | 983 × 266 × 99 | 106 | 654 | -329 | 172 | 66.0 | 90 (Reflex-/Holovisier) | 335 / 60 | – | 100 / 75 | 62 / 32020 |

## Größen der Hauptteile

Außenmaße L × H × B in mm (Länge entlang f, Höhe u, Breite x): Baugruppen als Hülle aller ihrer Teile, Griff und Magazin
als einzelne Teile.

| Waffe | Gehäuse `receiver` | Vorderbau `support` | Schaft `stock` | Visier `sight` | Griff `grip` | Magazin `magazine` |
|---|---|---|---|---|---|---|
| BASIC-01-v2.1 | 593 × 129 × 50 | 173 × 64 × 48 | 196 × 120 × 46 | 47 × 38 × 29 | 73 × 118 × 30 | 71 × 144 × 24 |
| BASIC-02-v2.1 | 262 × 123 × 45 | 309 × 38 × 44 | 194 × 116 × 38 | 47 × 37 × 29 | 72 × 116 × 30 | 45 × 106 × 24 |
| BASIC-03-v2.1 | 322 × 130 × 40 | 283 × 46 × 34 | 182 × 106 × 34 | 121 × 49 × 38 | 72 × 116 × 30 | 42 × 74 × 22 |
| BASIC-04-v2.1 | 293 × 68 × 34 | – | – | 260 × 13 × 25 | 68 × 100 × 30 | – |
| BASIC-05-v2.1 | 200 × 19 × 28 | – | – | 208 × 13 × 25 | 71 × 110 × 30 | 59 × 129 × 20 |
| BASIC-06-v2.1 | 262 × 81 × 43 | 222 × 121 × 40 | 130 × 115 × 40 | 47 × 37 × 25 | 72 × 116 × 30 | 70 × 166 × 22 |
| BASIC-08-v2.1 | 220 × 96 × 43 | – | 198 × 118 × 40 | 631 × 15 × 26 | 73 × 120 × 30 | – |
| BASIC-09-v2.1 | 330 × 130 × 40 | 290 × 29 × 34 | 207 × 128 × 40 | 217 × 61 × 51 | 72 × 116 × 30 | 37 × 60 × 24 |
| BASIC-10-v2.1 | 260 × 119 × 45 | 233 × 24 × 42 | 172 × 103 × 38 | 47 × 39 × 32 | 72 × 116 × 30 | – |
| BASIC-11-v2.1 | 322 × 124 × 41 | 559 × 38 × 30 | 207 × 128 × 40 | 192 × 46 × 50 | 72 × 116 × 30 | – |
| BASIC-12-v2.1 | 286 × 119 × 49 | 276 × 41 × 41 | 166 × 109 × 43 | 47 × 38 × 31 | 72 × 116 × 30 | – |
| BASIC-15-v2.1 | 360 × 106 × 53 | 309 × 64 × 55 | 180 × 118 × 40 | 47 × 40 × 37 | 72 × 116 × 30 | – |

## Werkzeuge

Werkzeuge der Familie (`basic/pilot/t*_v21.py`): gleicher Griff und gleiche Lagen um `Socket_Hand`, ohne Visier und
Magazin; Schussachse statt Laufachse.

| Werkzeug | L × H × B | Schussachse u | Mündung f | Heck f | Stützhand f / u | Schwerpunkt f / u | Teile / Dreiecke |
|---|---|---|---|---|---|---|---|
| BASIC-T01-v2.1 Portalkanone | 404 × 251 × 120 | 112 | 254 | -150 | 158 / 20 | 10 / 100 | 26 / 14940 |
