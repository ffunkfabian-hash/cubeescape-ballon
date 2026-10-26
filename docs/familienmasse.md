<!-- erzeugt von tools/make_docs.py – nicht von Hand ändern -->
# Familienmaße Stil v2.1

Gemessen am gebauten Modell (`data/specs/<Waffe>-v2.1.spec.json`, mit Fasen, Visier montiert, Ruhelage). Startpunkt für
neue Waffen der Familie: ähnliche Klasse suchen, Lagen übernehmen, Abweichungen im Modul-Docstring begründen
([stilhandbuch.md](stilhandbuch.md) §6/§7). Nach jedem Vollrendering `tools/sync_specs.py` und `tools/make_docs.py`.

## Lagen

mm relativ zu `Socket_Hand` (Griffachse), f vorn, u oben. Mündung f = Stirn der Mündung, Heck f = hinterste Kante
(negativ = hinter dem Griff). Visierhöhe = Visierlinie über der Laufachse (Soll 66 ± 4 mm), Augenabstand = Augenpunkt bis Glas bzw. Objektiv.

| Waffe | L × H × B | Laufachse u | Mündung f | Heck f | Visierlinie u | Visierhöhe | Augenabstand | Stützhand f / u | Magazinschacht f / u | Schwerpunkt f / u | Teile / Dreiecke |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BASIC-01-v2.1 Automatikgewehr | 915 × 260 × 52 | 106 | 616 | -299 | 169 | 63.0 | 90 (Reflex-/Holovisier) | 282 / 95 | 108 / 70 | 79 / 84 | 72 / 33242 |
| BASIC-02-v2.1 Impulsgewehr | 816 × 256 × 51 | 100 | 512 | -304 | 164 | 64.5 | 90 (Reflex-/Holovisier) | 290 / 80 | 99 / 62 | 68 / 79 | 56 / 29350 |
| BASIC-03-v2.1 Scout-Gewehr | 1023 × 261 × 47 | 96 | 721 | -302 | 161 | 65.0 | 90 (Zielfernrohr) | 300 / 90 | 110 / 62 | 58 / 79 | 52 / 28258 |
| BASIC-06-v2.1 Maschinenpistole | 547 × 291 × 47 | 82 | 326 | -221 | 147 | 65.0 | 90 (Reflex-/Holovisier) | 230 / 24 | 9 / 40 | 22 / 53 | 48 / 17600 |

## Größen der Hauptteile

Außenmaße L × H × B in mm (Länge entlang f, Höhe u, Breite x): Baugruppen als Hülle aller ihrer Teile, Griff und Magazin
als einzelne Teile.

| Waffe | Gehäuse `receiver` | Vorderbau `support` | Schaft `stock` | Visier `sight` | Griff `grip` | Magazin `magazine` |
|---|---|---|---|---|---|---|
| BASIC-01-v2.1 | 593 × 129 × 50 | 173 × 64 × 48 | 196 × 120 × 46 | 47 × 38 × 29 | 73 × 118 × 30 | 71 × 144 × 24 |
| BASIC-02-v2.1 | 262 × 123 × 45 | 309 × 38 × 44 | 194 × 116 × 38 | 47 × 38 × 30 | 72 × 116 × 30 | 45 × 106 × 24 |
| BASIC-03-v2.1 | 322 × 112 × 40 | 283 × 46 × 34 | 182 × 106 × 34 | 121 × 57 × 42 | 72 × 116 × 30 | 42 × 74 × 22 |
| BASIC-06-v2.1 | 262 × 81 × 43 | 222 × 121 × 40 | 130 × 115 × 40 | 47 × 38 × 29 | 72 × 116 × 30 | 70 × 166 × 22 |

## Werkzeuge

Werkzeuge der Familie (`basic/pilot/t*_v21.py`): gleicher Griff und gleiche Lagen um `Socket_Hand`, ohne Visier und
Magazin; Schussachse statt Laufachse.

| Werkzeug | L × H × B | Schussachse u | Mündung f | Heck f | Stützhand f / u | Schwerpunkt f / u | Teile / Dreiecke |
|---|---|---|---|---|---|---|---|
| BASIC-T01-v2.1 Portalkanone | 404 × 251 × 120 | 112 | 254 | -150 | 158 / 20 | 6 / 99 | 26 / 14940 |
