# Übergabe: Visier-Konzept neu (nach BALLON 0.20 „Spotter“)

Stand 26.10.2026, aus der Sitzung „BALLON 0.20 „Spotter“ · Mac“. Für eine **frische Sitzung** (eigene Version, nicht Teil von 0.20).

## Anlass (Nutzer, 26.10.2026)

- „Ich finde die Visier-Punkte/Kreise/Fadenkreuze sehen so komisch 3D-mäßig aus. Mir wäre lieber etwas Gezeichnetes als Grafik so oder so
  ähnlich“ und „Im Bestfall hat man das Fadenkreuz/Punkt/Kreis/wie auch immer vom Hüftfeuer im Visier“ → in 0.20 umgesetzt (Unity:
  gezeichnetes Absehen in Hüftform, siehe [unity.md](unity.md) › Steuerung, Test `Absehen_gezeichnet_in_Hueftform_im_Visier`).
- Zum Scout-Zielbild: „Irgendwie sieht das Scout-Gewehr-Scope auf dem Bild so komisch aus, vor allem die Unterseite, das was auf der
  Schiene sitzt. Wir müssen uns echt was für die Visiere überlegen. Ggf. müssen wir cubeescape-reference nochmal anschauen und ein
  separates Konzept entwerfen.“

## Was im Zielbild auffällt (0.20, Augenpunkt 90 mm hinter dem Objektivring, 75°)

- Unter dem Objektivring liegt eine große flache Platte quer durchs untere Bilddrittel: Oberseite von Schiene BRI-22 und Rohrsattel
  (`rail`, `scope_mount_r`, 0.19 „Saddle“) 10–40 mm vor dem Auge. In Blender (Ego-Still `ads`) und Unity gleich, also Form, nicht Unity.
- Der Objektivring wirkt als breiter Wulst (Fase des Objektivtrichters r ≈ 21 mm, Befund 0.19); 1a am Unity-Bild 1,32 / ≈ 1,62.
- Das Okular füllt beim Anflug kurz das Bild, dann schalten Okular/Rohr/Türme ab (`ads_hide`, Festlegung 0.20).

## Vorschlag für die Konzeptsitzung

1. Motiongen (`~/Claude/cubeescape-reference`, `origin/main`, docs `visiere.md`, `destiny2.md` › Glidepath, `proportionen.md` › 5.2)
   neu sichten: Was sieht man bei Destiny im Zielen **unter** dem Ring (Sockel/Gehäuse, Abstand, Helligkeit), wie dick ist der Ring,
   wo liegt das Absehen (Glas, Overlay)?
2. 2–3 Konzepte als Zielbild (Blender, `tools/sight_options.py`) nebeneinander: z. B. Sattel tiefer/schmaler, Schiene vor dem Auge
   abgeschrägt, Ring ohne Wulst (`common.scope_v21`, Unity-Formquelle → Neubacken), Absehen nur gezeichnet.
3. Nutzerwahl, dann Umsetzung als Version (Blender, Export mit Backen, Unity-Vergleich, Visier-Standard 3 und Stilhandbuch anpassen).

Offen aus 0.20: Blender zeichnet das Absehen weiter als Modellteil (Formblätter, Ego-Clips); nur Unity zeigt die gezeichnete Hüftform.
