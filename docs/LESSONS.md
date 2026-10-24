# Lehren

- Freestyle-Linien in Cycles brauchen einen ausdrücklich angelegten Linienstil (`bpy.data.linestyles.new`), sonst bricht der Hintergrundlauf ab ([blender_build.py](../tools/blender_build.py)).
- Flächenlichter mit Werkseinstellung überstrahlen Creme völlig; Key 115 W, Fill 35 W, Rim 70 W bei Standard-Ansicht ([blender_build.py](../tools/blender_build.py)).
- Drehpunkte beweglicher Teile weit genug vom Schwerpunkt legen: ein Kran direkt unter der Trommelachse dreht die Trommel auf der Stelle ([w04](../basic/weapons/w04_hand_cannon.py)).
- Visierlinie per Kamera in `Socket_Eye` prüfen: ein Emitterblock über der Fensterunterkante verdeckt die halbe Durchsicht ([common.reflex_sight](../basic/common.py)).
- Ein gemeinsamer Schaft für alle Gewehre macht die Reihe zu einer Waffe mit verschiedenen Läufen; zweiter Schafttyp S2 für Energie-/Impulswaffen ([designvertrag](designvertrag.md)).
- Wiki-Seiten zu Destiny-Waffen belegen Typ und Hersteller, nicht Form oder Nachladeablauf: Formprinzipien bleiben „abgeleitet“ ([quellen](quellen.md)).
- Drehsinn um die Querachse einmal festlegen und testen: ein vertauschtes Vorzeichen ließ alle Abzüge nach vorn und den MG-Deckel ins Gehäuse drehen; `move.expect` + [test_motion.py](../tools/test_motion.py) fangen das ([kit.py](../basic/kit.py)).
- Prüfstatus nie als festen Text in Werkzeuge schreiben: „visuell geprüft“ und „dargestellt“ kommen aus [data/review.json](../data/review.json) und vorhandenen Clips.
- Exact-Boolean mit mehreren, sich überlappenden Schneidkörpern ergibt ohne `use_self` ein leeres Netz; `kit.apply_cuts` prüft das ([kit.py](../basic/kit.py)).
- Schwarzes Polymer wirkt unter Studiolicht grau, solange der Specular-Anteil 0,5 bleibt; 0,2–0,25 und dunklere Grundfarbe ([kit.py](../basic/kit.py)).
- Kantenabrieb-Maske muss größer messen als die Modellfase (≥ 4 mm), sonst bleibt sie unsichtbar ([stilhandbuch](stilhandbuch.md#9-typische-fehler)).
- Bloom mit Schwelle ≤ 4 erfasst helle Lackflächen; Nutzerwunsch: Bloom aus ([stilhandbuch](stilhandbuch.md#1-entscheidungen-des-nutzers)).
- Ego-Kamera in Blender: 90° um X schaut nach +Y; für Blick −Y zusätzlich 180° um Z ([ego_build.py](../tools/ego_build.py)).
- Viewmodel-Arme: Unterarm an der Hand ausrichten und den Knick begrenzen, statt die Schulter festzuhalten; Hände greifen von unten hinten ([stilhandbuch](stilhandbuch.md#10-arme-und-animation)).
- Arme: Querschnitt skalieren macht ein Rohr nicht kräftig – Form (Wölbung, Schale, zweite Lage) trägt die Masse; Vorschau ohne Waffe mit [arm_preview.py](../tools/arm_preview.py) zuerst.
- Ego-Standbilder müssen die Handbelegung der Aktion übernehmen, sonst zeigt die Sichtung Fehler, die im Clip nicht auftreten ([ego_build.py](../tools/ego_build.py)).
- Ego-Clips wirkten abgehackt: Ease je Schlüsselabschnitt stoppt an jedem Schlüssel; Kurven durch die Schlüssel, Feder-Nachlauf und volle Bildrate ([stilhandbuch](stilhandbuch.md#10-arme-und-animation)).
