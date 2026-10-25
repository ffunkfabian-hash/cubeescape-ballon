# Übergabe an Motiongen (cubeescape-reference): Sprint, Visier-Anflug, Fadenkreuz

Stand 25.10.2026, aus BALLON 0.10 „Stride“. Nutzer: „Das mit der Sprint Animation gilt ja dann für jeden Waffentyp einzeln … erstmal nur die
festgelegten Standard Waffen.“ Anlass: Nutzerrückmeldung zum Unity-Prototyp: „Sprint sehr tapsig, zu schnell, kein
Destiny-2-Eindruck“, „beim Visier-Zoom ein komisches Wippen kurz vor dem Visier“, „das durchgehende Fadenkreuz in der Mitte muss weg“.
Stand 25.10. ~16:00: Die Messung je Grundtyp läuft in Motiongen als REF 0.24 „Glidepath“ (Branch `claude/ref-0.24-glidepath`).
Ein Unteragent der BALLON-Sitzung hat den Sprint am Gewehr vorab gemessen; seinen Branch arbeitet Glidepath ein. Quellen:
yt-dlp mit dem Standard-Client und Deno im PATH (1080p60). Der Android-Client liefert nur 360p mit 30/s und dient nur für Metadaten.

## Prompt

```text
Auftrag für cubeescape-reference (Motiongen). Lies zuerst AGENTS.md, docs/LESSONS.md, docs/destiny2.md › 2 (Methode, Messtabelle) und
› 3 (Steckbriefe, Bewegungsabsatz) und docs/auswertung.md. Messregeln wie dort: native 60-fps-Clips, ±1 Bild, Lage in % mit
Mittenkreuz (--cross), Belegstärke ehrlich, nur Verweise und Zahlen ins Repo, Nichtmessbares unter „Methode“. Eigener Branch, Minor +1.

Vergleichsobjekt ist der BALLON-Prototyp (Repo cubeescape-ballon, Unity) mit einem Automatikgewehr (BASIC-01) und einem Holo-Visier.
Miss Destiny 2 für drei Themen, und zwar je Waffentyp. Erst einmal gilt das nur für die 17 festgelegten Standardtypen der BASIC-Reihe:
Automatikgewehr, Impulsgewehr, Scout-Gewehr, Handfeuerwaffe, Seitenwaffe, Maschinenpistole, Kampfbogen, Schrotflinte,
Scharfschützengewehr, Fusionsgewehr, lineares Fusionsgewehr, Spurgewehr, Granatwerfer, Raketenwerfer, Maschinengewehr, Schwert, Gleve.
Exoten und Sonderformen sind kein Maßstab; höchstens ein Beleg für ihren Typ, mit Hinweis darauf.
Ergebnis je Thema ist eine Tabelle mit einer Zeile je Typ. Die Belegstärke ist dabei „gemessen“, „vom Nachbartyp übertragen“ (welcher)
oder „offen“. Nichts erfinden. Reihenfolge: zuerst Automatikgewehr, Impulsgewehr, Handfeuerwaffe, Maschinenpistole und
Scharfschützengewehr, dann die übrigen.

1. Sprint (BALLON vorher: Waffe vertikal 6 Hz, seitlich 3 Hz, Hub 10 mm, Rollen 4°, „tapsig“; 0.10: vertikal 3 Hz)
   - Wippfrequenz der Waffe über mindestens 4 Zyklen an einem festen Bildanker, getrennt vertikal (je Schritt) und seitlich
     (je Doppelschritt), mit Zeitstempeln je Umkehr.
   - Hub vertikal und seitlich in % Bildhöhe bzw. -breite, Rollen in Grad, Trageform je Klasse (Gewehr tief/vorn-unten?
     Handfeuerwaffe hoch?).
   - Wippt der Kopf (Horizont) mit, oder nur die Waffe?
   - Ein- und Austritt: Hüfte → Sprint, Sprint → Hüfte, Sprint → ADS (Bilder bis zur Ruhe).

2. Visier-Anflug Hüfte → ADS (BALLON 0.9: das Absehen kam von 22° rechts und schwang im letzten Bild 3,3° über die Mitte, dann zurück)
   - Bahn des Visierpunkts Bild für Bild von der Hüfte bis zur Ruhe, als Lage in %.
   - Ankunft: Bremst die Waffe vor der Mitte ab (über wie viele Bilder)? Gibt es ein Überschwingen oder Nachfedern, und wie groß ist es
     in % bzw. wie viele Bilder dauert es? Ausdrücklich auch „kein Überschwingen sichtbar“ festhalten.
   - Reihenfolge Weltzoom gegen Modell bei Holo und Reflex: Beginnt der Zoom vor, mit oder nach der Waffenbewegung? Endet er gleichzeitig?
   - Dasselbe für ADS → Hüfte (darf dort Nachfedern sichtbar sein?).

3. Fadenkreuz (BALLON 0.10: kein ständiges Fadenkreuz mehr, nur eine kurze Trefferanzeige)
   - Gibt es in der Hüfte ein Fadenkreuz? Form und Größe in % Bildhöhe je Klasse.
   - Ist es im Sprint, beim Nachladen, beim Betrachten, beim Ziehen und beim Wegstecken sichtbar? Verschwindet es im ADS vollständig
     (ab welchem Bild des Anflugs)?
   - Trefferanzeige: Form, Farbe, Dauer in Bildern, Unterschied bei Präzisionstreffern.

Dokumentation: Messzeilen mit Anker in docs/destiny2.md › 2 und Einträge in data/clips.json. Steckbriefe und Bewegungsabsatz in › 3
aktualisieren; eine neue Erkenntnis ersetzt die alte, mit Datum und Grund. Den Vergleich mit dem BALLON-Prototyp in docs/auswertung.md
eintragen und dabei „BALLON-Prototyp (cubeescape-ballon)“ nennen, nicht Cube Escape. Dazu CHANGELOG, Versionsbericht und ./check grün.
Abschlussbericht mit Zahlen je Thema und Belegstärke, dazu eine knappe Empfehlung als Beobachtung; die Entscheidung trifft BALLON.
```

## Startprompt für eine koordinierende Sitzung mit Unteragenten

```text
Motiongen (cubeescape-reference), Koordination mit Unteragenten.
Modell: Opus high für dich als Koordinator, weil du Belege bewertest und zusammenführst.
Unteragenten: Sonnet medium, weil sie nach fester Methode messen. Richter: Opus.

Ziel: Destiny-2-Referenz je Waffentyp für drei Themen des BALLON-Prototyps (Repo cubeescape-ballon):
(1) Sprint, (2) Visier-Anflug Hüfte → ADS, (3) Fadenkreuz in der Hüfte und Trefferanzeige.
Nur die 17 BASIC-Standardtypen: Automatikgewehr, Impulsgewehr, Scout-Gewehr, Handfeuerwaffe, Seitenwaffe, Maschinenpistole,
Kampfbogen, Schrotflinte, Scharfschützengewehr, Fusionsgewehr, lineares Fusionsgewehr, Spurgewehr, Granatwerfer, Raketenwerfer,
Maschinengewehr, Schwert, Gleve. Exoten sind kein Maßstab.
Vollständige Fragen je Thema mit den BALLON-Werten von vorher und nachher:
~/Claude/cubeescape-ballon/.claude/worktrees/nifty-hamilton-62a7ee/docs/uebergabe-motiongen-gefuehl.md (Abschnitt „Prompt“;
nach dem Merge von BALLON 0.10 unter ~/Claude/cubeescape-ballon/docs/).

Vorab:
1. Lies AGENTS.md, docs/LESSONS.md, docs/destiny2.md › 2 und › 3, docs/auswertung.md, data/clips.json.
2. Prüf `git branch -a` und `git worktree list`: Ein Branch zur Sprint-Messung (z. B. claude/ref-0.18-stride) läuft eventuell schon.
   Übernimm dessen Ergebnisse, statt sie neu zu messen, und schreib nie in dessen Dateien, solange er nicht gemergt ist.
   Ist er gemergt, baue darauf auf.
3. Eigener Branch, Minor +1, englischer Name. Kein Push, nie main.

Aufteilung: Jeder Unteragent bekommt einen eigenen Worktree und genau eine Typgruppe für alle drei Themen. Dadurch schreibt nie
jemand zweites in dieselben Messzeilen.
- A: Automatikgewehr, Impulsgewehr, Scout-Gewehr, Maschinengewehr
- B: Handfeuerwaffe, Seitenwaffe, Maschinenpistole
- C: Schrotflinte, Scharfschützengewehr, Fusionsgewehr, lineares Fusionsgewehr, Spurgewehr
- D: Kampfbogen, Granatwerfer, Raketenwerfer, Schwert, Gleve
  (D hat Sonderfälle ohne klassisches ADS: Bogen spannt, Schwert und Gleve führen. Dann „trifft nicht zu“ eintragen, mit Grund.)
Höchstens vier gleichzeitig. Sie laden Clips nur über tools/reference_frames.py (Twitch, ohne Anmeldung) in den Scratch
außerhalb des Repos.

Auftrag je Unteragent:
- Messen nach den Messregeln: native 60 fps, ±1 Bild, Lage in % mit --cross.
- Sprint: Frequenz über mindestens 4 Zyklen, vertikal und seitlich getrennt.
- Visier: Bahn Bild für Bild, Ankunft, Überschwingen ja/nein mit Größe, Reihenfolge von Zoom und Modell.
- Fadenkreuz: Form, Größe, Sichtbarkeit je Zustand.
- Jeder Wert bekommt eine Belegstärke: gemessen / vom Nachbartyp übertragen (welcher) / offen. Nichts erfinden.
- Er liefert seine Messzeilen mit Anker und clips.json-Einträge als Datei in seinem Worktree. In die gemeinsamen Docs schreibt er nicht.
- Bericht höchstens 15 Zeilen.

Du führst zusammen:
- Messzeilen in docs/destiny2.md › 2 und data/clips.json eintragen (doppelte Clips zusammenlegen).
- In › 3 je Thema eine Tabelle mit einer Zeile je Typ und den Spalten aus der Übergabe.
- Den Vergleich mit dem BALLON-Prototyp in docs/auswertung.md eintragen, als „BALLON-Prototyp (cubeescape-ballon)“, nicht Cube Escape.
- CHANGELOG, Versionsbericht und LESSONS pflegen; ./check grün.
- Danach den Richter (Opus, Checkliste ~/.claude/templates/pruefung.md) über deinen Diff laufen lassen und die Befunde beheben.
- Unteragenten-Ergebnisse selbst stichprobenartig am Bild prüfen, mindestens einen Wert je Gruppe.

Abschluss:
- Erste Zeile: fertig, nicht fertig oder Entscheidung nötig.
- Je Thema die Typtabelle in Kurzform, dazu was offen bleibt und warum.
- Eine knappe Empfehlung in Zahlen als Beobachtung; die Entscheidung trifft BALLON.
- Hinweis an BALLON per Übergabedatei, nie dort selbst schreiben.
- Ist-Zeit als Warten / Rechnen / Lesen / Umsetzen.
```
