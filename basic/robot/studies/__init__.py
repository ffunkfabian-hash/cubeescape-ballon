"""Formstudien für den BASIC-Roboter, Runde 5 (0.23 „Gauntlet“): drei Körper zur Wahl, alle rund und mit sichtbarer Technik.

Nutzerkritik nach Runde 4 (27.10.2026): „da können auch bestimmt mehr details rein, mehr sichtbare robotische sachen halt. ggf. kann
man den kopf auch ‚runder‘ gestalten wie insgesamt den körper“, davor „Hüfte und Beine sowie Schultern und Oberkörper passen einfach
nicht“ und „klotzig und steif“. Vier Runden mit je einem Entwurf scheiterten; bei den Ego-Armen traf die Wahl aus drei Varianten
sofort (docs/uebergabe-roboter.md).

Gemeinsam (basic/robot/studies/body.py): Querschnitte als Superellipse (ch = 0, n 2,4–3,0), Material und Motive der Familie
(Graphitkörper, Cremeschale mit Pfeilschnitt, dunkle Lage mit zwei Bolzen, Medaillon, Akzentlinie, Augenlinie als einziger
Blickfang), sichtbare Technik (Gelenke, Kolben, Leitungen, Fugen), Baugruppen greifen ineinander (Schulterpanzer auf dem Rumpf,
Beintaschen über dem Oberschenkel), Haltung im Kontrapost (Standbein links, Becken und Schultern gegenläufig geneigt, Rumpf zur
Mündung gedreht). Verschieden sind Proportion und Technikanteil:

  a_waechter    heroisch-schwer (Prinzipien Q-ARMOR-ORANGE): gedrungen, breit, Platten in Lagen, Rückenmodul
  b_paladin     athletisch (Q-D2-PARADE): V-Rumpf, Hüfte bei halber Höhe, große Schulterpanzer, dunkler Anzug sichtbar
  c_mechanik    schlank-mechanisch (Zielbild robot-concept): offenes Skelett, Kolben an den großen Gelenken, Platten einzeln

Jede Studie liefert das Skelett (WAIST, NECK, PELVIS, HEAD_H, TORSO_HINT, HEAD_HINT, HEAD_TOP, SHOULDER_LOCAL, JOINTS, FOOT_H), die
Teile je Baugruppe (head, upper_body, lower_body, legs) und die Abwandlung der Arme (ARM_BULK, ARM_DROP, arm_extra). Übernommen von
basic.robot.use(); gerendert mit tools/robot_build.py --study <name> (Ansichten vorn, profil, hero).
"""
NAMES = ('a_waechter', 'b_paladin', 'c_mechanik')
