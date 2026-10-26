// PlayMode: jede Aktion endet und meldet ihre Marker in der Reihenfolge der Daten; Spielablauf (Feuer, Nachladen, Zielen,
// Betrachten, Wegstecken, Sprint-Übergänge); die Szene startet und reagiert auf einen Eingabeablauf.
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
using UnityEngine.TestTools.Constraints;
using Is = UnityEngine.TestTools.Constraints.Is;   // NUnit-Is plus AllocatingGCMemory

namespace Ballon.Ego.Tests
{
    public class EgoPlayTests
    {
        const float Dt = 1f / 60f;
        static EgoFile _d, _mp, _sr;

        static EgoFile D => _d;
        static EgoFile MP => _mp;                           // zweite Waffe (0.18): Maschinenpistole BASIC-06
        static EgoFile SR => _sr;                           // dritte Waffe (0.20): Scout BASIC-03

        static EgoIntent Idle => new EgoIntent { grounded = true };

        static EgoController Ready(List<(string, string)> markers = null)
        {
            var c = new EgoController(new EgoSolver(D));
            if (markers != null) c.Marker += (a, m) => markers.Add((a, m));
            c.ReadyNow();
            c.Tick(Dt, Idle);
            return c;
        }

        static void Run(EgoController c, EgoIntent i, float seconds)
        {
            for (float t = 0; t < seconds; t += Dt) c.Tick(Dt, i);
        }

        [UnitySetUp]
        public IEnumerator LoadScene()
        {
            var boot = Object.FindAnyObjectByType<Bootstrap>();            // jeder Test beginnt mit Waffe 1 (0.18), auch nach einem Abbruch
            if (boot != null && boot.Player != null) boot.Player.UseWeapon(0);
            if (_d == null)
            {
                SceneManager.LoadScene("Firstfeel");
                yield return null;
                yield return null;
                var b = Object.FindAnyObjectByType<Bootstrap>();
                _d = b.Solvers[0].D;
                _mp = b.Solvers.Select(x => x.D).FirstOrDefault(d => d.gameplay.weapon_type == "submachine_gun");
                _sr = b.Solvers.Select(x => x.D).FirstOrDefault(d => d.gameplay.weapon_type == "scout_rifle");
            }
        }

        [Test]
        public void Jede_Aktion_endet_mit_Markern_in_Reihenfolge()
        {
            foreach (var A in D.actions)
            {
                var c = new EgoController(new EgoSolver(D));
                var got = new List<string>();
                bool ended = false;
                c.Marker += (a, m) => { if (a == A.name && !ended) got.Add(m); };
                c.PlayAction(A.name, scripted: true, onEnd: () => ended = true);
                int ticks = 0;
                while (!ended && ticks < A.frames * 2 + 10)
                {
                    c.Tick(1f / 30f, Idle);
                    ticks++;
                    foreach (var v in c.output.segR.Concat(c.output.segL))
                        Assert.IsFalse(float.IsNaN(v.m03) || float.IsNaN(v.m00), $"{A.name}: NaN");
                }
                Assert.IsTrue(ended, $"{A.name} endet nicht");
                Assert.LessOrEqual(ticks, A.frames + 1, $"{A.name}: {ticks} Bilder statt {A.frames}");
                CollectionAssert.AreEqual(A.events.Select(e => e.name).ToList(), got, $"{A.name}: Marker {string.Join(",", got)}");
            }
        }

        [Test]
        public void Dauerfeuer_mit_Kadenz_leert_das_Magazin()
        {
            var c = Ready();
            int shots = 0;
            c.Shot += () => shots++;
            Assert.AreEqual(D.gameplay.magazine, c.ammo);
            Run(c, new EgoIntent { grounded = true, fire = true }, 1.0f);
            float perS = D.gameplay.rpm / 60f;
            Assert.That(shots, Is.InRange((int)perS - 1, (int)perS + 1), "Schüsse in 1 s");
            Run(c, new EgoIntent { grounded = true, fire = true }, 3.0f);
            Assert.AreEqual(D.gameplay.magazine, shots, "ein Magazin");
            Assert.AreEqual(0, c.ammo);
        }

        /// <summary>Frage 7.1 A: Unity schießt wie der Clip fire_hip mit 720/min – bei 60 Bildern/s ein Schuss alle 5 Bilder
        /// (Motiongen: Chroma Rush, 5 Bilder Abstand), bei 30/s abwechselnd 2 und 3 Bilder. Vorher 600/min (6 bzw. 3 Bilder).</summary>
        [Test]
        public void Kadenz_720_wie_fire_hip()
        {
            Assert.AreEqual(720, D.gameplay.rpm, "ego.json › gameplay.rpm");
            StringAssert.StartsWith("M ", D.gameplay.src, "Herkunft gemessen");
            foreach (int fps in new[] { 60, 30 })
            {
                var c = Ready();
                c.ammo = c.magSize = 1000;
                var at = new List<int>();
                int k = 0;
                c.Shot += () => at.Add(k);
                for (; k < 2 * fps; k++) c.Tick(1f / fps, new EgoIntent { grounded = true, fire = true });
                var gaps = at.Zip(at.Skip(1), (a, b) => b - a).ToList();
                float rpm = 60f * fps / (float)gaps.Average(), ideal = fps * 60f / 720f;
                TestContext.WriteLine($"Kadenz live bei {fps}/s: {at.Count} Schüsse in 2 s, Bildabstand {string.Join(",", gaps.Distinct())} → {rpm:0} /min");
                Assert.AreEqual(24, at.Count, $"Schüsse in 2 s bei {fps}/s");
                Assert.That(gaps, Has.All.InRange(Mathf.FloorToInt(ideal) - 1, Mathf.CeilToInt(ideal) + 1), $"Bildabstand bei {fps}/s");
                Assert.AreEqual(720f, rpm, 15f, $"Kadenz aus den Bildabständen bei {fps}/s (Übertrag bleibt)");
            }
        }

        /// <summary>Frage 3.3 A: nach einer schnellen Drehung (360°/s, 0,3 s) zieht die Waffe gegen die Drehung nach, höchstens 3°,
        /// und kehrt kritisch gedämpft in ≈ 0,3 s ohne Überschwingen zurück. Gemessen als Gieren des Laufs gegen einen Zwilling ohne
        /// Mausbewegung (gleiche Zeitschritte, Atmen hebt sich auf). Vorher ζ 0,55: Überschwingen 0,22°, Rückkehr ≈ 0,1 s (Gegenlauf mit altem Code).</summary>
        [Test]
        public void Pendeln_kehrt_ohne_Ueberschwingen_zurueck()
        {
            var c = Ready();
            var c0 = Ready();
            float Yaw(EgoController x)
            {
                var d = x.output.weapon.MultiplyVector(new Vector3(0, -1, 0));   // Lauf zeigt nach −Y (Blender-Kameraraum)
                return Mathf.Atan2(-d.x, -d.y) * Mathf.Rad2Deg;
            }
            var dev = new List<float>();
            const int turn = 18;                                   // 0,3 s bei 60/s
            for (int k = 0; k < 90; k++)
            {
                var i = new EgoIntent { grounded = true, look = new Vector2(k < turn ? 360f * Dt : 0, 0) };
                c.Tick(Dt, i);
                c0.Tick(Dt, Idle);
                dev.Add(Mathf.DeltaAngle(Yaw(c0), Yaw(c)));
            }
            float peak = dev.Take(turn).OrderByDescending(v => Mathf.Abs(v)).First();
            var after = dev.Skip(turn).ToList();
            float over = after.Max(v => -Mathf.Sign(peak) * v);
            int back = after.Count;
            while (back > 0 && Mathf.Abs(after[back - 1]) < 0.05f * Mathf.Abs(peak)) back--;
            float ret = back * Dt;
            TestContext.WriteLine($"Pendeln: Auslenkung {peak:0.00}°, Überschwingen {Mathf.Max(0, over):0.000}°, Rückkehr (< 5 %) {ret:0.000} s");
            Assert.Less(Mathf.Abs(peak), 3.05f, "Auslenkung begrenzt");
            Assert.Greater(Mathf.Abs(peak), 0.5f, "Waffe zieht nach");
            Assert.Less(over, 0.02f, "kein Überschwingen");
            Assert.That(ret, Is.InRange(0.22f, 0.4f), "Rückkehr ≈ 0,3 s");
        }

        /// <summary>6c: Nachlade-Abbruch (Wegstecken) vor MagIn gibt keine Munition, danach ist das Magazin voll und bleibt es.</summary>
        [Test]
        public void Nachlade_Abbruch_vor_und_nach_MagIn()
        {
            foreach (var act in new[] { "reload_tactical", "reload_empty" })
            {
                float magIn = D.Action(act).events.First(e => e.name == "MagIn").f / 30f;
                foreach (bool afterMagIn in new[] { false, true })
                {
                    var m = new List<(string, string)>();
                    var c = Ready(m);
                    int before = c.ammo = act == "reload_empty" ? 0 : 5;
                    c.Tick(Dt, new EgoIntent { grounded = true, reload = true });
                    Assert.AreEqual(act, c.ActionName);
                    Run(c, Idle, magIn + (afterMagIn ? 0.1f : -0.1f));
                    Assert.AreEqual(afterMagIn, m.Contains((act, "MagIn")), $"{act}: MagIn vor dem Abbruch");
                    c.Tick(Dt, new EgoIntent { grounded = true, holster = true });
                    Assert.AreEqual("reload_to_switch", c.ActionName, act);
                    Run(c, Idle, D.Action("reload_to_switch").frames / 30f + 0.3f);
                    Assert.IsTrue(c.Holstered);
                    c.Tick(Dt, new EgoIntent { grounded = true, draw = true });
                    Run(c, Idle, D.Action("draw").frames / 30f + 0.3f);
                    Assert.AreEqual(afterMagIn ? c.magSize : before, c.ammo, $"{act}, Abbruch {(afterMagIn ? "nach" : "vor")} MagIn");
                }
            }
        }

        [Test]
        public void Leeres_Nachladen_und_taktisches_Nachladen()
        {
            var m = new List<(string, string)>();
            var c = Ready(m);
            c.ammo = 0;
            c.Tick(Dt, new EgoIntent { grounded = true, reload = true });
            Assert.AreEqual("reload_empty", c.ActionName);
            Run(c, Idle, D.Action("reload_empty").frames / 30f + 0.3f);
            CollectionAssert.AreEqual(new[] { "HandOff", "MagOut", "MagIn", "Chamber", "HandOn", "Ready" },
                m.Where(x => x.Item1 == "reload_empty").Select(x => x.Item2).ToArray());
            Assert.AreEqual(D.gameplay.magazine, c.ammo);
            Assert.AreEqual("idle_hip", c.ActionName);
            c.ammo = 7;
            c.Tick(Dt, new EgoIntent { grounded = true, reload = true });
            Assert.AreEqual("reload_tactical", c.ActionName);
            Run(c, Idle, D.Action("reload_tactical").frames / 30f + 0.3f);
            Assert.AreEqual(D.gameplay.magazine, c.ammo);
            // Abzug bei leerem Magazin lädt selbst nach
            c.ammo = 0;
            c.Tick(Dt, Idle);
            c.Tick(Dt, new EgoIntent { grounded = true, fire = true });
            Assert.AreEqual("reload_empty", c.ActionName);
        }

        [Test]
        public void Zielen_hin_und_zurueck()
        {
            var m = new List<(string, string)>();
            var c = Ready(m);
            Run(c, new EgoIntent { grounded = true, aim = true }, 0.6f);
            Assert.AreEqual(EgoController.Stance.Ads, c.CurrentStance);
            Assert.AreEqual(1f, c.adsWeight, 1e-4f);
            Assert.Contains(("aim_in", "Aimed"), m);
            Run(c, Idle, 0.6f);
            Assert.AreEqual(EgoController.Stance.Hip, c.CurrentStance);
            Assert.Contains(("aim_out", "Ready"), m);
            Assert.AreEqual(0f, c.adsWeight, 1e-4f);
            // Augenpunkt liegt im Zielen auf der Kameraachse
            var c2 = Ready();
            Run(c2, new EgoIntent { grounded = true, aim = true }, 0.8f);
            var eye = c2.output.weapon.MultiplyPoint3x4(BMath.V(D.Anchor("Socket_Eye").pos));
            Assert.That(new Vector2(eye.x, eye.z).magnitude, Is.LessThan(0.004f), $"Auge {eye:F4}");
        }

        /// <summary>Live (EgoController, wie im Spiel und im feel-MP4): Zielen aus der Hüfte bringt das Absehen ohne Überschwingen auf die
        /// Mitte und hängt nach 0,45 s nicht mehr nach (0.10; Destiny 2 hat beim Zielen kein Überschwingen).</summary>
        [Test]
        public void Zielen_live_ohne_Ueberschwingen()
        {
            var c = Ready();
            var ret = BMath.V(D.Anchor("Socket_Reticle").pos);
            float first = float.NaN, worst = 0, at045 = 0;
            for (int k = 0; k < 60; k++)                           // 1 s bei 60 Bildern/s
            {
                c.Tick(Dt, new EgoIntent { grounded = true, aim = true });
                var t = c.output.weapon.MultiplyPoint3x4(ret);
                float az = Mathf.Atan2(-t.x, -t.y) * Mathf.Rad2Deg;   // Blender-Kameraraum: rechts −X, vorn −Y
                if (float.IsNaN(first)) first = az;
                worst = Mathf.Max(worst, -Mathf.Sign(first) * az);
                if (k == 26) at045 = Mathf.Abs(az);
            }
            TestContext.WriteLine($"live aim_in: Start {first:0.00}°, Überschwingen {worst:0.00}°, Rest nach 0,45 s {at045:0.00}°");
            Assert.Less(worst, 0.3f, $"Absehen schwingt {worst:0.00}° über die Mitte");
            Assert.Less(at045, 1.0f, $"Absehen hängt nach 0,45 s {at045:0.00}° nach");
        }

        /// <summary>Live-Sprint (EgoController.LiveLayers): vertikal 2,9–3,4 Hochpunkte je Sekunde, Hochpunkte an den Seitenumkehren
        /// (U-Bogen wie Destiny 2, Motiongen REF 0.23), nicht in der Mitte.</summary>
        [Test]
        public void Sprint_live_im_Destiny_Rhythmus()
        {
            var c = Ready();
            var sprint = new EgoIntent { grounded = true, sprint = true, move = new Vector2(0, 1), speed01 = 1.6f };
            Run(c, sprint, 1.5f);                                  // in die Schleife, Gewichte eingeschwungen
            int n = 180;                                           // 3 s
            var x = new float[n]; var z = new float[n];
            for (int k = 0; k < n; k++)
            {
                c.Tick(Dt, sprint);
                var p = c.output.weapon.GetColumn(3);
                x[k] = p.x; z[k] = p.z;
            }
            float mx = 0, mz = 0;
            for (int k = 0; k < n; k++) { mx += x[k] / n; mz += z[k] / n; }
            int peaks = 0;
            float atSide = 0, atMid = 0; int nSide = 0, nMid = 0;
            float ax = 0;
            for (int k = 0; k < n; k++) ax = Mathf.Max(ax, Mathf.Abs(x[k] - mx));
            for (int k = 1; k < n - 1; k++)
            {
                if (z[k] > z[k - 1] && z[k] >= z[k + 1] && z[k] > mz) peaks++;
                float s = Mathf.Abs(x[k] - mx) / ax;
                if (s > 0.8f) { atSide += z[k] - mz; nSide++; }
                if (s < 0.2f) { atMid += z[k] - mz; nMid++; }
            }
            float hz = peaks / (n * Dt);
            atSide /= Mathf.Max(1, nSide); atMid /= Mathf.Max(1, nMid);
            TestContext.WriteLine($"live sprint: {hz:0.00} Hochpunkte/s, Höhe an den Seiten {atSide * 1000:0.0} mm, in der Mitte {atMid * 1000:0.0} mm");
            Assert.That(hz, Is.InRange(2.9f, 3.4f), "Schritte je Sekunde");
            Assert.Greater(atSide, atMid, "U-Bogen: oben an den Seitenumkehren, unten in der Mitte");
        }

        static EgoScreen _scr;
        static EgoScreen Scr => _scr ?? (_scr = new EgoScreen(new EgoSolver(D)));

        /// <summary>Anteil der Bildhöhe/-breite (%) eines Winkels im Weltbild mit Zoom z (16:9, 75° horizontal).</summary>
        static float ShareH(float deg, float z) => Mathf.Tan(deg * Mathf.Deg2Rad) / (2 * Mathf.Tan(37.5f * Mathf.Deg2Rad) * 9f / 16f / z) * 100;
        static float ShareB(float deg, float z) => Mathf.Tan(deg * Mathf.Deg2Rad) / (2 * Mathf.Tan(37.5f * Mathf.Deg2Rad) / z) * 100;

        /// <summary>Entscheidungsliste 6.1 A: Waffenwechsel (Q) wie Destiny – Wegstecken ≈ 0,25 s (Destiny 0,08–0,27 s, bis 0.14 0,60 s),
        /// danach 0,1–0,2 s leere Sicht (weder Waffe noch Arme im Bild), dann Ziehen wie bisher mit Nachfedern. Die Marker Wegstecken,
        /// leer, erstes neues Bild, Hüfte und ruhig einzeln; sichtbar heißt: eine Kante der Netzgrenzen von Waffe oder Armen liegt im Bild.</summary>
        [Test]
        public void Wechsel_mit_leerer_Sicht()
        {
            foreach (bool fromReload in new[] { false, true })
            {
                var c = Ready();
                if (fromReload) { c.ammo = 5; c.Tick(Dt, new EgoIntent { grounded = true, reload = true }); }
                Run(c, Idle, 0.3f);
                var marks = new List<(int k, string a, string m)>();
                int k = 0;
                c.Marker += (a, m) => marks.Add((k, a, m));
                var pts = new List<Vector2>();
                var vis = new List<bool>();
                var acts = new List<string>();
                var eye = BMath.V(D.Anchor("Socket_Eye").pos);
                var move = new List<float>();
                Vector3 prev = Vector3.zero;
                for (; k < 150; k++)                                   // 2,5 s bei 60/s
                {
                    c.Tick(Dt, k == 0 ? new EgoIntent { grounded = true, swap = true } : Idle);
                    Scr.Silhouette(c.output, pts);
                    vis.Add(pts.Count > 0);
                    acts.Add(c.ActionName);
                    var e = c.BaseWeapon.MultiplyPoint3x4(eye);
                    move.Add(k == 0 ? 0 : (e - prev).magnitude);
                    prev = e;
                }
                string act = fromReload ? "reload_to_switch" : "holster";
                int hol = marks.FindIndex(x => x.a == act && x.m == "Holstered");
                int empty = marks.FindIndex(x => x.a == "switch" && x.m == "Empty"), draw = marks.FindIndex(x => x.a == "switch" && x.m == "Draw");
                int ready = marks.FindIndex(x => x.a == "draw" && x.m == "Ready");
                Assert.IsTrue(hol >= 0 && empty >= 0 && draw >= 0 && ready >= 0, string.Join(" ", marks.Select(x => $"{x.k}:{x.a}/{x.m}")));
                float T(int frame) => (frame + 1) * Dt;                 // Ende des Bilds
                int gone = vis.IndexOf(false), back = vis.IndexOf(true, Mathf.Max(0, gone));
                Assert.Greater(gone, 0, "Waffe verschwindet");
                Assert.Greater(back, gone, "neue Waffe erscheint");
                int rk = marks[ready].k, calm = -1;
                for (int q = rk; q < move.Count - 6 && calm < 0; q++)          // ruhig: 6 Bilder unter 0,2 mm je Bild
                    if (move.Skip(q).Take(6).All(v => v < 0.0002f)) calm = q;
                float tHol = T(marks[hol].k), tEmpty = (back - gone) * Dt;
                TestContext.WriteLine($"Wechsel{(fromReload ? " aus dem Nachladen" : "")} bei 60/s: Wegstecken bis {T(gone - 1):0.000} s sichtbar, Marker " +
                                      $"{act} › Holstered {tHol:0.000} s; leer {T(gone - 1):0.000}–{T(back - 1):0.000} s = {tEmpty:0.000} s " +
                                      $"(switch › Empty {T(marks[empty].k):0.000}, Draw {T(marks[draw].k):0.000}); erstes neues Bild {T(back):0.000} s; " +
                                      $"Hüfte (draw › Ready) {T(rk):0.000} s; ruhig {(calm < 0 ? "–" : T(calm).ToString("0.000"))} s");
                if (!fromReload)                                         // reload_to_switch (Abbruch) bleibt wie bisher
                {
                    Assert.That(tHol, Is.InRange(0.2f, 0.3f), "Wegstecken ≈ 0,25 s (Destiny 0,08–0,27 s)");
                    Assert.LessOrEqual(T(gone - 1), tHol + 1e-4f, "beim Marker Holstered ist die Waffe aus dem Bild");
                    Assert.That(tEmpty, Is.InRange(0.1f - 1e-4f, 0.2f + 1e-4f), "leere Sicht 0,1–0,2 s");
                }
                Assert.LessOrEqual(marks[hol].k, marks[empty].k, "leer nach dem Wegstecken");
                Assert.AreEqual("draw", acts[back], "das erste neue Bild gehört zum Ziehen");
                Assert.Greater(rk, back, "Hüfte nach dem ersten neuen Bild");
                float skip = EgoController.DrawEnters(new EgoSolver(D));
                Assert.AreEqual((D.Action("draw").events.First(e => e.name == "Ready").f - skip) / 30f, (rk - marks[draw].k) * Dt, 2 * Dt,
                                "Ziehen wie bisher: nur der unsichtbare Anfang entfällt");
                Assert.Greater(calm, rk, "ruhig nach dem Nachfedern");
                Assert.Less((calm - rk) * Dt, 0.6f, "ruhig binnen 0,6 s nach der Hüfte");
                Assert.IsFalse(c.Holstered);
            }
        }

        /// <summary>6.1 A über die ganze Eingabekette wie im Spiel und in der Aufnahme: Taste Q (ScriptedInput „swap“) → EgoPlayer.Step →
        /// Controller. Richter 0.15: der Wechseltest oben setzt den Intent direkt; EgoPlayer reichte `swap` nicht weiter.</summary>
        [UnityTest]
        public IEnumerator Wechsel_mit_Q_im_Spieler()
        {
            var p = Object.FindAnyObjectByType<Bootstrap>().Player;
            p.UseWeapon(0);
            p.C.ReadyNow();
            p.Teleport(new Vector3(0f, 0.01f, 1.6f), 0f);
            p.input = Bootstrap.SwitchScript();
            p.deltaOverride = () => 1f / 30f;
            var marks = new List<string>();
            var used = new List<int>();
            System.Action<string, string> on = (a, m) => { marks.Add($"{a}/{m}"); if (m == "Ready") used.Add(p.arsenal.Active); };
            foreach (var c in p.arsenal.C) c.Marker += on;       // 0.18: Q wechselt zur nächsten Waffe (0.20 mit drei Waffen: Automatik → MP → Scout)
            for (int k = 0; k < 150 && (marks.Count(m => m == "draw/Ready") < 2 || p.C.Busy); k++) yield return null;   // bis das Ziehen endet
            foreach (var c in p.arsenal.C) c.Marker -= on;
            CollectionAssert.AreEqual(new[] { 1, 2 }, used, "Q: erst die MP, dann der Scout (zur nächsten Waffe)");
            bool holstered = p.C.Holstered;
            p.input = new ScriptedInput().Add(0, 1000);
            yield return null;
            p.deltaOverride = null;
            TestContext.WriteLine("Marker: " + string.Join(" ", marks));
            Assert.AreEqual(2, marks.Count(m => m == "holster/Holstered"), "zweimal weggesteckt");
            Assert.AreEqual(2, marks.Count(m => m == "switch/Empty") , "zweimal leere Sicht");
            Assert.AreEqual(2, marks.Count(m => m == "switch/Draw"), "zweimal gezogen");
            Assert.AreEqual(2, marks.Count(m => m == "draw/Ready"), "zweimal in der Hüfte");
            Assert.IsFalse(holstered, "nach dem Ziehen bereit");
        }

        // ---------------------------------------------------------------- Ego-Übertrag je Klasse und Waffenwechsel 1/2 (0.18)
        /// <summary>Entscheidungsliste 4d live bei 60/s: Anflug erste Bewegung → Ruhe am Bild (Absehen, Grundhaltung nach dem Feder-Nachlauf,
        /// Bildweg je Bild unter 0,09 % (≈ 1,7 px bei 1080p); so gemessen braucht die Automatik mit aim_in 0,33 s die Destiny-Automatik-Zeit 20 Bilder).
        /// MP ≤ 12 Bilder (Destiny-MP 8–12), Automatik unverändert ≈ 20. Ruhe wie Motiongen am Bild: fester Bildweg je Bild (Still, % von B/H),
        /// nicht relativ zum Weg – der kürzere MP-Weg hätte sonst eine strengere Schwelle.</summary>
        [Test]
        public void Anflug_je_Klasse_live_bei_60()
        {
            const float Still = 0.09f;
            int Frames(EgoFile d)
            {
                var c = new EgoController(new EgoSolver(d));
                c.ReadyNow();
                Run(c, Idle, 1f);
                var E = new EgoScreen(c.S);
                var ret = BMath.V(d.Anchor("Socket_Reticle").pos);
                var pos = new List<Vector3>();
                for (int k = 0; k < 90; k++)
                {
                    c.Tick(Dt, new EgoIntent { grounded = true, aim = true });
                    pos.Add(E.ToScreen(c.BaseWeapon.MultiplyPoint3x4(ret)));
                }
                var p0 = E.ToScreen(new EgoSolver(d).PoseMatrix("hip").MultiplyPoint3x4(ret));
                float total = Vector3.Distance(new Vector2(p0.x, p0.y), new Vector2(pos.Last().x, pos.Last().y));
                var step = new List<float> { Vector2.Distance(p0, pos[0]) };
                for (int k = 1; k < pos.Count; k++) step.Add(Vector2.Distance(pos[k - 1], pos[k]));
                int Span(float thr, out int first)
                {
                    int f0 = first = step.FindIndex(v => v > thr);
                    return Enumerable.Range(f0, step.Count - f0).First(k => step.Skip(k).All(v => v < thr)) - f0;
                }
                int n = Span(Still, out int fa), nr = Span(0.003f * total, out _);
                TestContext.WriteLine($"{d.weapon.id} ({d.profile.type}): aim_in {d.Action("aim_in").frames} Bilder bei 30/s; am Bild erste Bewegung " +
                                      $"Bild {fa}, Ruhe nach {n} Bildern bei 60/s ({n / 60f:0.000} s; Schwelle {Still} % je Bild), Weg {total:0.0} %; " +
                                      $"mit Schwelle 0,3 % des Wegs: {nr} Bilder");
                return n;
            }
            int mp = Frames(MP), ar = Frames(D), sr = Frames(SR);
            Assert.That(sr, Is.InRange(15, 20), "Scout-Anflug 15–20 Bilder bei 60/s (zwischen Scharfschütze 15 und Impuls 20; Destiny-Scout 12–22)");
            Assert.LessOrEqual(mp, 12, "MP-Anflug ≤ 12 Bilder bei 60/s (Destiny-MP 8–12)");
            Assert.GreaterOrEqual(mp, 8, "MP-Anflug ≥ 8 Bilder (Destiny-MP 8–12)");
            Assert.That(ar, Is.InRange(18, 22), "Automatik wie bisher ≈ 20 Bilder (Destiny-Automatik 20)");
            Assert.AreEqual(10f / 30f, D.Action("aim_in").frames / 30f, 1e-6f, "Automatik aim_in 0,33 s");
        }

        // ---------------------------------------------------------------- Scout BASIC-03 (0.20 „Spotter“)
        /// <summary>Feuerart semi_auto (Spec): ein Schuss je Zug. Gehaltener Abzug schießt einmal; fünf Klicks im Abstand 0,5 s geben fünf
        /// Schüsse; zwei Klicks schneller als der Schussabstand (60/180 s) geben zwei Schüsse, der zweite nach dem Schussabstand. Automatik
        /// und MP bleiben im Dauerfeuer (720/min). Bis 0.19 kannte der Controller nur Dauerfeuer.</summary>
        [Test]
        public void Einzelfeuer_feuert_genau_einmal_je_Klick()
        {
            var c = new EgoController(new EgoSolver(SR));
            var at = new List<int>();
            int k = 0;
            c.Shot += () => at.Add(k);
            c.ReadyNow();
            Run(c, Idle, 0.3f);
            var fire = new EgoIntent { grounded = true, fire = true };
            for (int j = 0; j < 90; j++, k++) c.Tick(Dt, fire);                      // 1,5 s gehalten
            Assert.AreEqual(1, at.Count, "gehaltener Abzug: genau ein Schuss");
            for (int j = 0; j < 30; j++, k++) c.Tick(Dt, Idle);
            for (int n = 0; n < 5; n++)                                               // fünf Klicks, je 2 Bilder gedrückt, Abstand 0,5 s
            {
                for (int j = 0; j < 2; j++, k++) c.Tick(Dt, fire);
                for (int j = 0; j < 28; j++, k++) c.Tick(Dt, Idle);
            }
            Assert.AreEqual(6, at.Count, "fünf Klicks: fünf Schüsse");
            at.Clear();
            for (int j = 0; j < 2; j++, k++) c.Tick(Dt, fire);                        // zwei schnelle Klicks im Abstand 0,1 s
            for (int j = 0; j < 4; j++, k++) c.Tick(Dt, Idle);
            for (int j = 0; j < 2; j++, k++) c.Tick(Dt, fire);
            for (int j = 0; j < 40; j++, k++) c.Tick(Dt, Idle);
            float gap = at.Count == 2 ? (at[1] - at[0]) * Dt : 0, want = 60f / SR.gameplay.rpm;
            TestContext.WriteLine($"Scout: zwei Klicks im Abstand 0,100 s → {at.Count} Schüsse, Abstand {gap:0.000} s (60/rpm = {want:0.000} s); Munition {c.ammo}/{c.magSize}");
            Assert.AreEqual(2, at.Count, "zwei Klicks: zwei Schüsse");
            Assert.GreaterOrEqual(gap, want - 1e-4f, "der zweite nach dem Schussabstand");
            Assert.Less(gap, want + 2 * Dt, "… und nicht später");
            Assert.AreEqual(SR.gameplay.magazine - 8, c.ammo, "acht Schüsse");
            // Richter 0.20: kurzer Klick bei gehaltenem Sprint – der Schuss fällt nach sprint_to_fire, danach wieder Sprint
            var sprint = new EgoIntent { grounded = true, sprint = true, move = new Vector2(0, 1), speed01 = 1.6f };
            for (int j = 0; j < 60; j++, k++) c.Tick(Dt, sprint);
            Assert.AreEqual(EgoController.Stance.Sprint, c.CurrentStance, "im Sprint");
            at.Clear();
            var tap = sprint;
            tap.fire = true;
            c.Tick(Dt, tap); k++;
            for (int j = 0; j < 45; j++, k++) c.Tick(Dt, sprint);
            TestContext.WriteLine($"Scout: Klick im Sprint → {at.Count} Schuss nach {(at.Count > 0 ? at[0] - (k - 46) : -1)} Bildern, danach {c.CurrentStance}");
            Assert.AreEqual(1, at.Count, "kurzer Klick im Sprint: ein Schuss");
            for (int j = 0; j < 40; j++, k++) c.Tick(Dt, sprint);
            Assert.AreEqual(EgoController.Stance.Sprint, c.CurrentStance, "danach wieder Sprint");
            foreach (var d in new[] { D, MP })                                          // Dauerfeuer unverändert
            {
                var a = new EgoController(new EgoSolver(d));
                a.ReadyNow();
                Run(a, Idle, 0.3f);
                long s0 = a.shots;
                for (int j = 0; j < 60; j++) a.Tick(Dt, fire);
                TestContext.WriteLine($"{d.weapon.id}: 1 s gehalten → {a.shots - s0} Schüsse");
                Assert.AreEqual(12, a.shots - s0, 1, $"{d.weapon.id}: Dauerfeuer 720/min");
            }
        }

        /// <summary>Tasten 1 → 3 → 2 (6.1 A, wie 0.18): jede Waffe wird weggesteckt, die leere Sicht dauert 0,1–0,2 s, das erste neue Bild
        /// gehört zum Ziehen der gewählten Waffe; jede Waffe behält ihre Munition (Automatik, Scout, MP).</summary>
        [Test]
        public void Wechsel_1_3_2_mit_leerer_Sicht_ohne_Munitionsverlust()
        {
            int k = 0;
            var marks = new List<(int k, string a, string m, int w)>();
            var A = new EgoArsenal(new EgoController(new EgoSolver(D)), new EgoController(new EgoSolver(MP)), new EgoController(new EgoSolver(SR)));
            for (int w = 0; w < 3; w++) { int ww = w; A.C[w].Marker += (a, m) => marks.Add((k, a, m, ww)); }
            A.C[0].ReadyNow();
            A.Tick(Dt, Idle);
            var scr = A.C.Select(c => new EgoScreen(c.S)).ToArray();
            var pts = new List<Vector2>();
            for (int t = 0; t < 20; t++) A.Tick(Dt, new EgoIntent { grounded = true, fire = true });   // Automatik schießt
            int ar = A.C[0].ammo;
            Assert.Less(ar, 30);
            int sr = -1;
            foreach (int target in new[] { 3, 2, 1 })
            {
                marks.Clear();
                var vis = new List<bool>();
                var who = new List<int>();
                var acts = new List<string>();
                int from = A.Active;
                for (k = 0; k < 120; k++)
                {
                    A.Tick(Dt, Idle, k == 0 ? target : 0);
                    scr[A.Active].Silhouette(A.Current.output, pts);
                    vis.Add(pts.Count > 0);
                    who.Add(A.Active);
                    acts.Add(A.Current.ActionName);
                }
                int gone = vis.IndexOf(false), back = vis.IndexOf(true, Mathf.Max(0, gone));
                float tEmpty = (back - gone) * Dt;
                int hol = marks.FindIndex(x => x.a == "holster" && x.m == "Holstered" && x.w == from);
                TestContext.WriteLine($"Taste {target} (von {from + 1}): Holstered {(hol >= 0 ? (marks[hol].k + 1) * Dt : -1):0.000} s, leer {tEmpty:0.000} s, " +
                                      $"erstes neues Bild {(back + 1) * Dt:0.000} s ({acts[back]} von Waffe {who[back] + 1})");
                Assert.GreaterOrEqual(hol, 0, $"Taste {target}: weggesteckt");
                Assert.That(tEmpty, Is.InRange(0.1f - 1e-4f, 0.2f + 1e-4f), $"Taste {target}: leere Sicht 0,1–0,2 s");
                Assert.AreEqual(target - 1, who[back], "das erste neue Bild zeigt die gewählte Waffe");
                Assert.AreEqual("draw", acts[back], "… beim Ziehen");
                Assert.AreEqual(target - 1, A.Active);
                Assert.AreEqual(ar, A.C[0].ammo, "Automatik behält ihre Munition");
                if (target == 3)
                {
                    Assert.AreEqual(SR.gameplay.magazine, A.C[2].ammo, "Scout voll");
                    for (int n = 0; n < 2; n++)                                       // zwei Klicks
                    {
                        A.Tick(Dt, new EgoIntent { grounded = true, fire = true });
                        for (int t = 0; t < 30; t++) A.Tick(Dt, Idle);
                    }
                    sr = A.C[2].ammo;
                    Assert.AreEqual(SR.gameplay.magazine - 2, sr, "Scout: zwei Klicks, zwei Schüsse");
                }
                if (sr >= 0) Assert.AreEqual(sr, A.C[2].ammo, "Scout behält seine Munition");
                Assert.AreEqual(30, A.C[1].ammo, "MP unberührt");
            }
        }

        /// <summary>Entscheidungsliste 1d am Zielfernrohr (60/s, Hüfte → Zielen und zurück): der Weltzoom beginnt mit oder kurz nach dem
        /// Modell (0–2 Bilder) und endet mit ihm (±1 Bild) wie beim Holo; das Linsenbild (Okular, Rohr, Türme aus) kommt in der letzten Phase
        /// des Anflugs, sobald das Okular die Nahebene erreicht (Destiny-Scharfschütze: Linse nach dem Modell; mit einer Kamera und echtem
        /// Okular geht das nicht ohne angeschnittenes Okular). Zielen → Hüfte: die Teile kommen zurück, bevor das Modell die Hüfte erreicht.</summary>
        [Test]
        public void Zielfernrohr_Zoom_und_Linse_mit_dem_Modell()
        {
            var aim = new EgoIntent { grounded = true, aim = true };
            var E = new EgoScreen(new EgoSolver(SR));
            // Socket_Sight (Okularende) liegt im Zielen 30 mm hinter dem Auge, also hinter der Kamera, das Objektiv 90 mm davor: ihre Bildbewegung
            // wächst am Ende ohne Grenze und hebt die 5-%-Schwelle an. Gemessen wird an den fernen Punkten (Mündung, Schacht, Griff, Stützhand)
            var anchors = new[] { "Socket_Muzzle", "Socket_SupportHand", "Socket_MagWell", "Socket_Hand" }.Select(a => BMath.V(SR.Anchor(a).pos)).ToArray();
            var prev = new Vector2[anchors.Length];
            foreach (bool inAim in new[] { true, false })
            {
                var c = new EgoController(new EgoSolver(SR));
                c.ReadyNow();
                Run(c, inAim ? Idle : aim, 0.8f);
                for (int a = 0; a < anchors.Length; a++) prev[a] = E.ToScreen(c.BaseWeapon.MultiplyPoint3x4(anchors[a]));
                var w = new List<float> { c.adsWeight };
                var mv = new List<float> { 0 };
                var hid = new List<bool> { c.output.adsHidden };
                for (int k = 0; k < 60; k++)
                {
                    c.Tick(Dt, inAim ? aim : Idle);
                    float sum = 0;
                    for (int a = 0; a < anchors.Length; a++)
                    {
                        Vector2 q = E.ToScreen(c.BaseWeapon.MultiplyPoint3x4(anchors[a]));
                        sum += (q - prev[a]).magnitude;
                        prev[a] = q;
                    }
                    mv.Add(sum);
                    w.Add(c.adsWeight);
                    hid.Add(c.output.adsHidden);
                }
                float w0 = w[0], w1 = w[w.Count - 1], peak = mv.Max();
                int zs = w.FindIndex(x => x != w0), ze = w.FindIndex(x => x == w1);
                int ms = mv.FindIndex(x => x > 0.05f * peak), me = mv.FindLastIndex(x => x > 0.05f * peak);
                int lens = hid.IndexOf(inAim);
                TestContext.WriteLine($"Scout {(inAim ? "Hüfte → Zielen" : "Zielen → Hüfte")} bei 60/s: Modell Bild {ms}–{me}, Zoom {zs}–{ze} " +
                                      $"(Start {zs - ms:+0;-0;0}, Ende {ze - me:+0;-0;0}), Linsenbild {(inAim ? "an" : "aus")} ab Bild {lens} ({lens - me:+0;-0;0} zum Modellende)");
                Assert.AreEqual(1f, Mathf.Abs(w1 - w0), 1e-4f, "Zoom ganz durchlaufen");
                Assert.That(zs - ms, Is.InRange(0, 2), "Zoom beginnt mit oder kurz nach dem Modell");
                Assert.Greater(lens, 0, "Linsenbild schaltet um");
                Assert.IsTrue(hid.Skip(lens).All(x => x == inAim), "einmal umschalten, kein Flackern");
                if (inAim)
                {
                    Assert.That(ze - me, Is.InRange(-1, 1), "Zoom endet mit dem Modell (±1 Bild)");
                    // Festlegung 0.20 (1d am Zielfernrohr): Linsenbild, sobald das Okular die Nahebene erreicht (Auge 60 mm vor der Kamera, 86 % des
                    // Wegs); danach bewegt sich das Modell fast nur noch längs der Blickachse. Später ginge nicht ohne angeschnittenes Okular.
                    Assert.That(lens - me, Is.InRange(-8, 0), "Linsenbild in der letzten Phase des Anflugs, spätestens mit dem Modellende");
                    Assert.Greater(lens, zs, "Linsenbild nach dem Beginn des Zooms");
                }
                else Assert.Less(lens, me, "Zielen → Hüfte: Teile zurück, bevor das Modell die Hüfte erreicht");
            }
        }

        /// <summary>Scout im Spieler (Taste 3 über die Eingabekette): Weltzoom 2,0, Teile mit ads_hide im Zielen aus und in der Hüfte da,
        /// Einzelfeuer mit gehaltenem Abzug genau ein Schuss, Hüft-Fadenkreuz der Klasse.</summary>
        [UnityTest]
        public IEnumerator Scout_im_Spieler_Taste_3_Zielfernrohr_Einzelfeuer()
        {
            var p = Object.FindAnyObjectByType<Bootstrap>().Player;
            p.UseWeapon(0);
            p.C.ReadyNow();
            p.Teleport(new Vector3(0f, 0.01f, 1.6f), 0f);
            p.input = new ScriptedInput().Add(0, 0.05f, press: "weapon3").Add(0.05f, 1.4f);
            p.deltaOverride = () => 1f / 30f;
            for (int k = 0; k < 42; k++) yield return null;
            Assert.AreEqual(2, p.arsenal.Active, "Taste 3: Scout");
            var rig = p.rig;
            Assert.AreEqual(7, rig.AdsHideCount, "Okular, Rohr, Okularkante, Okularlinse, Türme, Spannband");
            Assert.IsFalse(rig.AdsHidden, "Hüfte: Zielfernrohr ganz");
            Assert.AreEqual("cross", p.hipReticle.Kind, "Hüft-Fadenkreuz des Scouts");
            long s0 = p.C.shots;
            p.input = new ScriptedInput().Add(0, 1.2f, hold: "aim").Add(0.6f, 1.2f, hold: "aim fire");
            for (int k = 0; k < 36; k++) yield return null;
            float zoom = Mathf.Tan(p.viewCam.fieldOfView * Mathf.Deg2Rad / 2) / Mathf.Tan(p.worldCam.fieldOfView * Mathf.Deg2Rad / 2);
            Assert.IsTrue(rig.AdsHidden, "Zielen: Teile mit ads_hide aus");
            Assert.AreEqual(2.0f, zoom, 1e-3f, "Weltzoom 2,0");
            Assert.IsTrue(p.SightVisible, "gezeichnetes Absehen im Zielfernrohr");
            var sc = p.SightScreen();
            Assert.AreEqual(0.5f, sc.x / p.viewCam.pixelWidth, 0.02f, "Absehen nahe der Bildmitte");
            Assert.AreEqual(0.5f, sc.y / p.viewCam.pixelHeight, 0.02f);
            Assert.AreEqual(1, p.C.shots - s0, "gehaltener Abzug im Zielen: ein Schuss");
            p.input = new ScriptedInput().Add(0, 1000);
            for (int k = 0; k < 20; k++) yield return null;
            Assert.IsFalse(rig.AdsHidden, "zurück in der Hüfte: Zielfernrohr ganz");
            p.input = new ScriptedInput().Add(0, 0.05f, press: "weapon1").Add(0.05f, 1.5f);     // sauber zurück zur Automatik (wie Taste 1)
            for (int k = 0; k < 45; k++) yield return null;
            p.input = new ScriptedInput().Add(0, 1000);
            yield return null;
            p.deltaOverride = null;
            Assert.AreEqual(0, p.arsenal.Active);
        }

        /// <summary>Nutzerwunsch 26.10.2026 („lieber etwas Gezeichnetes als Grafik … im Bestfall das Fadenkreuz vom Hüftfeuer im Visier“): das
        /// Absehen aller drei Waffen ist im Spiel gezeichnet, nicht das Modellteil – im Zielen die Hüftform der Klasse in der Farbe des
        /// Modell-Absehens an der Bildlage von Socket_Reticle (auf der Mitte), ohne Aufgehen; in der Hüfte und beim Nachladen aus; das
        /// Modellteil (Rolle reticle_*) ist immer aus.</summary>
        [UnityTest]
        public IEnumerator Absehen_gezeichnet_in_Hueftform_im_Visier()
        {
            var p = Object.FindAnyObjectByType<Bootstrap>().Player;
            p.deltaOverride = () => 1f / 30f;
            for (int w = 0; w < p.loadouts.Length; w++)
            {
                p.UseWeapon(w);
                p.C.ReadyNow();
                var L = p.Current;
                Assert.IsNotNull(L.sight, $"{p.C.S.D.weapon.id}: gezeichnetes Absehen");
                Assert.AreEqual(L.hip.Kind, L.sight.Kind, "Form wie das Hüft-Fadenkreuz");
                var role = p.C.S.D.weapon.parts.First(q => q.role.StartsWith("reticle"));
                Assert.IsFalse(L.rig.Part(role.id).GetComponent<Renderer>().enabled, "Modell-Absehen aus");
                ColorUtility.TryParseHtmlString(p.C.S.D.Role(role.role).color, out var want);
                Assert.AreEqual(want, L.sightColor, "Farbe der Absehen-Rolle (Cyan)");
                p.input = new ScriptedInput().Add(0, 1000);
                for (int k = 0; k < 10; k++) yield return null;
                Assert.IsFalse(p.SightVisible, "Hüfte: kein Absehen im Visier");
                p.input = new ScriptedInput().Add(0, 1000, hold: "aim");
                for (int k = 0; k < 30; k++) yield return null;
                Assert.IsTrue(p.SightVisible, $"{p.C.S.D.weapon.id}: im Zielen gezeichnetes Absehen");
                var s = p.SightScreen();
                float spread0 = L.sight.spread;
                TestContext.WriteLine($"{p.C.S.D.weapon.id}: Absehen {L.sight.Kind} bei x {s.x / p.viewCam.pixelWidth * 100:0.0} / y {100 - s.y / p.viewCam.pixelHeight * 100:0.0} %");
                Assert.AreEqual(0.5f, s.x / p.viewCam.pixelWidth, 0.02f);
                Assert.AreEqual(0.5f, s.y / p.viewCam.pixelHeight, 0.02f);
                p.input = new ScriptedInput().Add(0, 1000, hold: "aim fire");
                for (int k = 0; k < 6; k++) yield return null;
                Assert.AreEqual(spread0, L.sight.spread, 1e-6f, "ohne Aufgehen im Zielen");
                p.input = new ScriptedInput().Add(0, 1000);
                for (int k = 0; k < 30; k++) yield return null;
            }
            p.deltaOverride = null;
            p.UseWeapon(0);
            p.C.ReadyNow();
        }

        static EgoArsenal Arsenal(List<(int k, string a, string m, int w)> marks, System.Func<int> k)
        {
            var A = new EgoArsenal(new EgoController(new EgoSolver(D)), new EgoController(new EgoSolver(MP)));
            for (int w = 0; w < 2; w++)
            {
                int ww = w;
                if (marks != null) A.C[w].Marker += (a, m) => marks.Add((k(), a, m, ww));
            }
            A.C[0].ReadyNow();
            A.Tick(Dt, Idle);
            return A;
        }

        /// <summary>Tasten 1/2 (6.1 A über holster/draw): Automatik → MP → Automatik mit leerer Sicht wie beim Wechsel mit Q (Wegstecken bis
        /// Holstered ≈ 0,27 s, leer 0,1–0,2 s, das erste neue Bild gehört zum Ziehen der anderen Waffe, sichtbar = Kante von Waffe oder Armen
        /// im Bild); jede Waffe behält ihre Munition, auch beim Abbruch des Nachladens (vor MagIn keine Munition).</summary>
        [Test]
        public void Wechsel_1_2_mit_leerer_Sicht_ohne_Munitionsverlust()
        {
            int k = 0;
            var marks = new List<(int k, string a, string m, int w)>();
            var A = Arsenal(marks, () => k);
            var scr = new[] { new EgoScreen(A.C[0].S), new EgoScreen(A.C[1].S) };
            var pts = new List<Vector2>();
            for (int t = 0; t < 20; t++) A.Tick(Dt, new EgoIntent { grounded = true, fire = true });   // Automatik schießt
            int ar = A.C[0].ammo;
            Assert.Less(ar, 30, "Automatik hat geschossen");
            Assert.AreEqual(30, A.C[1].ammo, "MP voll");
            foreach (int target in new[] { 2, 1 })
            {
                marks.Clear();
                var vis = new List<bool>();
                var who = new List<int>();
                var acts = new List<string>();
                int from = A.Active;
                for (k = 0; k < 120; k++)
                {
                    A.Tick(Dt, Idle, k == 0 ? target : 0);
                    scr[A.Active].Silhouette(A.Current.output, pts);
                    vis.Add(pts.Count > 0);
                    who.Add(A.Active);
                    acts.Add(A.Current.ActionName);
                }
                int hol = marks.FindIndex(x => x.a == "holster" && x.m == "Holstered" && x.w == from);
                int draw = marks.FindIndex(x => x.a == "switch" && x.m == "Draw" && x.w == target - 1);
                int ready = marks.FindIndex(x => x.a == "draw" && x.m == "Ready" && x.w == target - 1);
                Assert.IsTrue(hol >= 0 && draw >= 0 && ready >= 0, string.Join(" ", marks.Select(x => $"{x.k}:{x.w}:{x.a}/{x.m}")));
                int gone = vis.IndexOf(false), back = vis.IndexOf(true, Mathf.Max(0, gone));
                float T(int f) => (f + 1) * Dt;
                float tHol = T(marks[hol].k), tEmpty = (back - gone) * Dt;
                TestContext.WriteLine($"Taste {target}: Wegstecken bis {T(gone - 1):0.000} s sichtbar, Holstered {tHol:0.000} s, leer {tEmpty:0.000} s, " +
                                      $"erstes neues Bild {T(back):0.000} s ({acts[back]} von Waffe {who[back] + 1}), Hüfte {T(marks[ready].k):0.000} s");
                Assert.That(tHol, Is.InRange(0.2f, 0.3f), "Wegstecken ≈ 0,27 s");
                Assert.That(tEmpty, Is.InRange(0.1f - 1e-4f, 0.2f + 1e-4f), "leere Sicht 0,1–0,2 s");
                int empty = marks.FindIndex(x => x.a == "switch" && x.m == "Empty" && x.w == from);
                float pause = (marks[draw].k - marks[empty].k) * Dt, want = D.motion.@switch.empty_s;
                TestContext.WriteLine($"  Pause Empty → Draw {pause:0.000} s (switch.empty_s {want:0.000} s)");
                Assert.That(pause, Is.InRange(want - 1e-4f, want + Dt + 1e-4f), $"Pause Empty → Draw = switch.empty_s ({want:0.000} s, wie Q)");
                Assert.AreEqual(target - 1, who[back], "das erste neue Bild zeigt die andere Waffe");
                Assert.AreEqual("draw", acts[back], "… beim Ziehen");
                Assert.AreEqual(target - 1, A.Active);
                Assert.IsFalse(A.Switching);
                Assert.IsTrue(A.C[from].Holstered, "die alte Waffe bleibt weggesteckt");
                Assert.AreEqual(ar, A.C[0].ammo, "Automatik behält ihre Munition");
                if (target == 2)
                {
                    for (int t = 0; t < 12; t++) A.Tick(Dt, new EgoIntent { grounded = true, fire = true });   // MP schießt
                    Assert.Less(A.C[1].ammo, 30);
                }
            }
            int mp = A.C[1].ammo;
            Assert.AreEqual(ar, A.C[0].ammo);
            // Wechsel mitten im Nachladen (vor MagIn): reload_to_switch, keine Munition (6c), die andere Waffe behält ihre
            A.Tick(Dt, new EgoIntent { grounded = true, reload = true });
            Assert.AreEqual("reload_tactical", A.Current.ActionName);
            for (int t = 0; t < 10; t++) A.Tick(Dt, Idle);
            A.Tick(Dt, Idle, 2);
            Assert.AreEqual("reload_to_switch", A.Current.ActionName, "Nachladen bricht beim Wechsel ab");
            for (int t = 0; t < 120; t++) A.Tick(Dt, Idle);
            Assert.AreEqual(1, A.Active);
            Assert.AreEqual(ar, A.C[0].ammo, "Abbruch vor MagIn: keine Munition");
            Assert.AreEqual(mp, A.C[1].ammo, "MP unverändert");
            // Taste der aktiven Waffe: nichts; Taste während eines Wechsels: übergangen
            A.Tick(Dt, Idle, 2);
            Assert.IsFalse(A.Switching);
            Assert.AreEqual("idle_hip", A.Current.ActionName);
        }

        /// <summary>Kein Speicher je Bild beim Wechsel (Tasten 1/2): Wegstecken, leere Sicht, Ziehen und zurück, nach einem ersten Wechsel
        /// (Übersetzung, Zwischenspeicher); Spuren und Rückrufe des Controllers werden wiederverwendet (0.18).</summary>
        [Test]
        public void Kein_GC_Muell_beim_Wechsel()
        {
            var A = Arsenal(null, () => 0);
            void Round()
            {
                for (int k = 0; k < 80; k++) A.Tick(Dt, Idle, k == 0 ? 2 : 0);
                for (int k = 0; k < 80; k++) A.Tick(Dt, Idle, k == 0 ? 1 : 0);
            }
            Round();
            Round();
            Assert.AreEqual(0, A.Active);
            NUnit.Framework.Assert.That(() => Round(), Is.Not.AllocatingGCMemory(), "Wechsel 1 → 2 → 1");
            Assert.AreEqual(0, A.Active);
            Assert.AreEqual("idle_hip", A.Current.ActionName);
        }

        /// <summary>Tasten 1/2 über die ganze Eingabekette (ScriptedInput „weapon2“/„weapon1“ → EgoPlayer.Step → EgoArsenal): nur das Modell der
        /// aktiven Waffe ist sichtbar, der Weltzoom und das Hüft-Fadenkreuz folgen der Klasse (MP 1,45, Ring mit Marken).</summary>
        [UnityTest]
        public IEnumerator Wechsel_mit_Tasten_1_2_im_Spieler()
        {
            var p = Object.FindAnyObjectByType<Bootstrap>().Player;
            Assert.AreEqual(3, p.loadouts.Length, "drei Waffen in der Szene (0.20: Scout)");
            p.UseWeapon(0);
            p.C.ReadyNow();
            p.Teleport(new Vector3(0f, 0.01f, 1.6f), 0f);
            p.input = new ScriptedInput().Add(0, 0.2f).Add(0.2f, 0.25f, press: "weapon2").Add(0.25f, 1.6f).Add(1.6f, 1.65f, hold: "aim")
                                         .Add(1.65f, 2.4f, hold: "aim");
            p.deltaOverride = () => 1f / 30f;
            for (int k = 0; k < 72; k++) yield return null;
            Assert.AreEqual(1, p.arsenal.Active, "Taste 2: MP");
            Assert.IsTrue(p.loadouts[1].rig.space.gameObject.activeInHierarchy, "MP sichtbar");
            Assert.IsFalse(p.loadouts[0].rig.space.gameObject.activeInHierarchy, "Automatik versteckt");
            Assert.AreEqual(1.45f, p.C.worldZoom, 1e-5f, "Weltzoom der MP");
            Assert.AreEqual("circle_cross", p.hipReticle.Kind, "Hüft-Fadenkreuz der MP");
            p.input = new ScriptedInput().Add(0, 0.05f, press: "weapon1").Add(0.05f, 1.5f);
            for (int k = 0; k < 45; k++) yield return null;
            p.input = new ScriptedInput().Add(0, 1000);
            yield return null;
            p.deltaOverride = null;
            Assert.AreEqual(0, p.arsenal.Active, "Taste 1: Automatik");
            Assert.IsTrue(p.loadouts[0].rig.space.gameObject.activeInHierarchy);
            Assert.IsFalse(p.loadouts[1].rig.space.gameObject.activeInHierarchy);
            Assert.IsFalse(p.C.Holstered, "gezogen");
        }

        /// <summary>Richter 0.18: der Treffertext der Anzeige entsteht nur bei geänderten Werten oder beim Waffenwechsel neu, nicht bei jedem
        /// Aktionsbild (der Zustandstext folgt dem Bild).</summary>
        [UnityTest]
        public IEnumerator Anzeige_baut_Treffertext_nur_bei_Aenderung()
        {
            var p = Object.FindAnyObjectByType<Bootstrap>().Player;
            p.C.ReadyNow();
            p.input = new ScriptedInput().Add(0, 1000);
            p.deltaOverride = () => 1f / 30f;
            yield return null;
            p.UpdateHudText();
            var hit = p.HudHitText;
            for (int k = 0; k < 10; k++) { yield return null; p.UpdateHudText(); }
            Assert.AreSame(hit, p.HudHitText, "gleiche Werte: Treffertext nicht neu gebaut, obwohl die Aktionsbilder weiterlaufen");
            p.UseWeapon(1);
            p.UpdateHudText();
            Assert.AreNotSame(hit, p.HudHitText, "Waffenwechsel: neu gebaut (Skin der anderen Waffe)");
            p.UseWeapon(0);
            p.deltaOverride = null;
        }

        /// <summary>Entscheidungsliste 1d (Destiny-Holo, Motiongen glidepath): der Weltzoom beginnt mit oder kurz nach dem Modell (0–2
        /// Bilder bei 60/s) und endet mit ihm (±1 Bild); Modell = Bildbewegung der Waffe in der Grundhaltung (Summe der Wege von Mündung,
        /// Visier, Magazinschacht und Griff im Bild) je Bild über 5 % ihres Höchstwerts (die empfindlichste Schwelle der Bildmessung;
        /// am Unity-Bild gemessen 0.15: Start +2/+1/0, Ende −1/0/+1 Bilder bei 5/10/20 %). Bis 0.14 begann der Zoom 2–3 Bilder vor dem Modell (eigene Zeitkurve) und nach dem Sprint 11 Bilder danach.
        /// Zielen → Hüfte: der Zoom ist zurück, wenn das Modell die Hüfte erreicht; das Nachfedern danach zählt nicht.</summary>
        [Test]
        public void Zoom_beginnt_und_endet_mit_dem_Modell()
        {
            var aim = new EgoIntent { grounded = true, aim = true };
            var sprint = new EgoIntent { grounded = true, sprint = true, move = new Vector2(0, 1), speed01 = 1.6f };
            var cases = new (string name, EgoIntent before, float pre, EgoIntent after)[]
            {
                ("Hüfte → Zielen", Idle, 0.6f, aim), ("Zielen → Hüfte", aim, 0.8f, Idle), ("Sprint → Zielen", sprint, 1.5f, aim),
            };
            var anchors = new[] { "Socket_Muzzle", "Socket_Sight", "Socket_MagWell", "Socket_Hand" }.Select(a => BMath.V(D.Anchor(a).pos)).ToArray();
            var prev = new Vector2[anchors.Length];
            float Motion(EgoController c, bool first)
            {
                float sum = 0;
                for (int a = 0; a < anchors.Length; a++)
                {
                    Vector2 q = Scr.ToScreen(c.BaseWeapon.MultiplyPoint3x4(anchors[a]));
                    if (!first) sum += (q - prev[a]).magnitude;
                    prev[a] = q;
                }
                return sum;
            }
            foreach (var (name, before, pre, after) in cases)
            {
                var c = Ready();
                Run(c, before, pre);
                var w = new List<float> { c.adsWeight };
                Motion(c, true);                                       // Ausgangslage merken
                var mv = new List<float> { 0 };
                for (int k = 0; k < 60; k++)
                {
                    c.Tick(Dt, after);
                    mv.Add(Motion(c, false));
                    w.Add(c.adsWeight);
                }
                float w0 = w[0], w1 = w[w.Count - 1], peak = mv.Max();
                int zs = w.FindIndex(x => x != w0), ze = w.FindIndex(x => x == w1);
                var line = new System.Text.StringBuilder($"{name}: Zoom Bild {zs}–{ze} ({w0:0}→{w1:0})");
                int ms5 = 0, me5 = 0;
                foreach (float thr in new[] { 0.05f, 0.10f, 0.20f })
                {
                    int ms = mv.FindIndex(x => x > thr * peak), me = mv.FindLastIndex(x => x > thr * peak);
                    line.Append($"; Schwelle {thr * 100:0} %: Modell {ms}–{me}, Zoom − Modell Start {zs - ms:+0;-0;0}, Ende {ze - me:+0;-0;0}");
                    if (thr == 0.05f) { ms5 = ms; me5 = me; }
                }
                TestContext.WriteLine(line.ToString());
                Assert.AreEqual(1f, Mathf.Abs(w1 - w0), 1e-4f, $"{name}: Zoom ganz durchlaufen");
                Assert.That(zs - ms5, Is.InRange(0, 2), $"{name}: Zoom beginnt mit oder kurz nach dem Modell");
                if (after.aim) Assert.That(ze - me5, Is.InRange(-1, 1), $"{name}: Zoom endet mit dem Modell (±1 Bild)");
                else Assert.LessOrEqual(ze - me5, 1, $"{name}: Zoom ist zurück, wenn das Modell die Hüfte erreicht (danach federt es nach)");
            }
            // aus dem Zielen direkt nachladen: das Auge liegt beim Nachladen näher an der Kamera als in der Hüfte – kein Rest-Zoom
            var cr = Ready();
            cr.ammo = 5;
            Run(cr, aim, 0.8f);
            cr.Tick(Dt, new EgoIntent { grounded = true, reload = true });
            Assert.AreEqual("reload_tactical", cr.ActionName);
            Run(cr, Idle, 0.5f);
            TestContext.WriteLine($"Zielen → Nachladen: Zoom-Anteil nach 0,5 s {cr.adsWeight:0.000}");
            Assert.AreEqual(0f, cr.adsWeight, 1e-4f, "Zielen → Nachladen: Zoom spätestens nach 0,5 s zurück");
        }

        /// <summary>Entscheidungsliste 5.2 A: Destiny-Säule – feste, lernbare Grundbahn: je Schuss 1 % H nach oben (Anteil des Weltbilds,
        /// im Zielen also kleinerer Winkel), seitlich eine feste Folge mit ≤ 2,5 % B, dreimal dieselbe Form; zweistufig: in der Salve keine
        /// Erholung, danach kritisch gedämpft zurück ohne Unterschwingen. Salvenwaffe (Daten hier umgestellt): drei Schuss je Salve,
        /// Erholung in der Pause, eine angefangene Salve läuft zu Ende. Bis 0.14: bleibendes Hochziehen 0,18°/Schuss, keine Seitenbahn.</summary>
        [Test]
        public void Rueckstoss_Saeule_fest_und_zweistufig()
        {
            var c = Ready();
            c.ammo = c.magSize = 1000;
            int shots = 0;
            c.Shot += () => shots++;
            var bursts = new List<List<Vector2>>();
            float minY = 0;
            for (int b = 0; b < 3; b++)
            {
                var path = new List<Vector2>();
                int s0 = shots;
                while (shots - s0 < 12) { c.Tick(Dt, new EgoIntent { grounded = true, fire = true }); path.Add(c.PathDeg); }
                for (int k = 0; k < 72; k++) { c.Tick(Dt, Idle); path.Add(c.PathDeg); minY = Mathf.Min(minY, c.PathDeg.y); }
                bursts.Add(path);
            }
            float diff = 0;
            for (int k = 0; k < bursts[0].Count; k++)
                for (int b = 1; b < 3; b++) diff = Mathf.Max(diff, (bursts[b][k] - bursts[0][k]).magnitude);
            var first = bursts[0];
            int last = first.Count - 72;
            float up = ShareH(first.Max(v => v.y), 1);
            float side = ShareB(first.Max(v => v.x), 1) - ShareB(first.Min(v => v.x), 1);
            float rest = ShareH(first[first.Count - 1].y, 1);
            int backK = first.FindIndex(last, v => ShareH(v.y, 1) < 0.25f);
            TestContext.WriteLine($"Hüfte, 12 Schuss: Säule {up:0.00} % H, seitlich {side:0.00} % B, dreimal gleich (größte Abweichung {diff:0.0000}°), " +
                                  $"zurück unter 0,25 % H nach {(backK - last + 1) * Dt:0.000} s, Rest {rest:0.000} % H, tiefster Wert {ShareH(minY, 1):0.000} % H");
            Assert.That(up, Is.InRange(11f, 13.5f), "≈ 1 % H je Schuss (Destiny Chroma Rush: 12 Schuss ≈ 12 % H)");
            Assert.That(side, Is.InRange(0.5f, 2.5f), "kleines, begrenztes Seitenwackeln ≤ 2,5 % B");
            Assert.Less(diff, 0.001f, "feste Bahn: dreimal dieselbe Form");
            Assert.That((backK - last + 1) * Dt, Is.InRange(0.4f, 0.75f), "Erholung nach dem Stoß");
            Assert.Greater(ShareH(minY, 1), -0.05f, "kein Unterschwingen");

            // Zielen: gleicher Bildanteil im gezoomten Weltbild
            var ca = Ready();
            ca.ammo = ca.magSize = 1000;
            Run(ca, new EgoIntent { grounded = true, aim = true }, 0.8f);
            int sa = 0;
            ca.Shot += () => sa++;
            float pk = 0;
            while (sa < 4) { ca.Tick(Dt, new EgoIntent { grounded = true, aim = true, fire = true }); }
            for (int k = 0; k < 10; k++) { ca.Tick(Dt, new EgoIntent { grounded = true, aim = true }); pk = Mathf.Max(pk, ca.PathDeg.y); }
            float upAds = ShareH(pk, ca.worldZoom);
            TestContext.WriteLine($"Zielen, 4 Schuss: Bahn {upAds:0.00} % H des gezoomten Bilds ({pk:0.000}°, Zoom {ca.worldZoom})");
            Assert.That(upAds, Is.InRange(3.5f, 4.5f), "Viererstoß im Zielen ≈ 4 % H (Destiny Chroma Rush)");

            // Salvenwaffe: Takt in der Salve, Erholung danach (Daten nur für diesen Test umgestellt)
            var Rc = D.motion.recoil;
            int oldShots = Rc.burst_shots, oldBurstRpm = Rc.burst_rpm;
            try
            {
                Rc.burst_shots = 3;
                Rc.burst_rpm = 900;
                var cb = Ready();
                cb.ammo = cb.magSize = 1000;
                cb.rpm = 120;                                          // eine Salve je 0,5 s
                var at = new List<(int k, float y)>();
                int kk = 0;
                cb.Shot += () => at.Add((kk, cb.PathDeg.y));
                var ys = new List<float>();
                for (; kk < 90; kk++) { cb.Tick(Dt, new EgoIntent { grounded = true, fire = kk < 75 }); ys.Add(cb.PathDeg.y); }
                var gaps = at.Zip(at.Skip(1), (a, b) => b.k - a.k).ToList();
                TestContext.WriteLine($"Salvenwaffe (3 × 900/min, alle 0,5 s): Schüsse in Bild {string.Join(",", at.Select(a => a.k))}; Bahn je Schuss " +
                                      string.Join(" ", at.Select(a => ShareH(a.y, 1).ToString("0.0"))) + " % H");
                Assert.AreEqual(new[] { 4, 4, 22, 4, 4, 22, 4, 4 }, gaps.Take(8).ToArray(), "Takt in der Salve 4 Bilder, Salve alle 30 Bilder");
                float peak1 = ys.Skip(at[2].k).Take(12).Max(), atNext = at[3].y;
                Assert.Less(atNext, 0.35f * peak1, "Erholung in der Pause");
                Assert.Greater(at[2].y, at[1].y, "keine Erholung in der Salve");
                var cs = Ready();                                       // ein kurzer Druck: die Salve läuft zu Ende
                cs.ammo = cs.magSize = 1000;
                int n3 = 0;
                cs.Shot += () => n3++;
                cs.Tick(Dt, new EgoIntent { grounded = true, fire = true });
                Run(cs, Idle, 0.3f);
                Assert.AreEqual(3, n3, "angefangene Salve läuft zu Ende");
            }
            finally
            {
                Rc.burst_shots = oldShots;
                Rc.burst_rpm = oldBurstRpm;
            }
        }

        [Test]
        public void Betrachten_bricht_beim_Feuern_ab()
        {
            var c = Ready();
            c.Tick(Dt, new EgoIntent { grounded = true, inspect = true });
            Assert.AreEqual("inspect", c.ActionName);
            Run(c, Idle, 0.5f);
            int shots = 0;
            c.Shot += () => shots++;
            Run(c, new EgoIntent { grounded = true, fire = true }, 0.6f);
            Assert.AreNotEqual("inspect", c.ActionName);
            Assert.Greater(shots, 0, "nach dem Abbruch wird gefeuert");
            // ein einzelner R-Druck beim Betrachten bricht ab und lädt nach
            Run(c, Idle, 1.0f);
            c.Tick(Dt, new EgoIntent { grounded = true, inspect = true });
            Run(c, Idle, 0.3f);
            c.Tick(Dt, new EgoIntent { grounded = true, reload = true });
            Assert.AreEqual("reload_tactical", c.ActionName);
        }

        [Test]
        public void Wegstecken_beim_Nachladen_und_Ziehen()
        {
            var m = new List<(string, string)>();
            var c = Ready(m);
            c.ammo = 5;
            c.Tick(Dt, new EgoIntent { grounded = true, reload = true });
            Run(c, Idle, 0.15f);
            c.Tick(Dt, new EgoIntent { grounded = true, holster = true });
            Assert.AreEqual("reload_to_switch", c.ActionName);
            Run(c, Idle, D.Action("reload_to_switch").frames / 30f + 0.3f);
            Assert.IsTrue(c.Holstered);
            Assert.AreEqual(5, c.ammo, "Abbruch vor MagIn lässt die Munition");
            Assert.Contains(("reload_to_switch", "Cancel"), m);
            Assert.Contains(("reload_to_switch", "Holstered"), m);
            int shots = 0;
            c.Shot += () => shots++;
            Run(c, new EgoIntent { grounded = true, fire = true }, 0.3f);
            Assert.AreEqual(0, shots, "weggesteckt feuert nicht");
            c.Tick(Dt, new EgoIntent { grounded = true, draw = true });
            Assert.AreEqual("draw", c.ActionName);
            Run(c, Idle, D.Action("draw").frames / 30f + 0.3f);
            Assert.IsFalse(c.Holstered);
            Assert.Contains(("draw", "Ready"), m);
        }

        [Test]
        public void Sprint_Schleife_und_Uebergaenge()
        {
            var m = new List<(string, string)>();
            var c = Ready(m);
            var sprint = new EgoIntent { grounded = true, sprint = true, move = new Vector2(0, 1), speed01 = 1.6f };
            Run(c, sprint, 2.0f);
            Assert.AreEqual(EgoController.Stance.Sprint, c.CurrentStance);
            Assert.AreEqual("sprint", c.ActionName);
            var sk = D.Action("sprint").weapon;
            Assert.That(c.Frame, Is.InRange(sk[1].f, sk[2].f), "Schleife");
            Assert.Contains(("sprint", "SprintLoop"), m);
            var toAim = sprint;
            toAim.aim = true;
            c.Tick(Dt, toAim);
            Assert.AreEqual("sprint_to_aim", c.ActionName);
            Run(c, toAim, 0.8f);
            Assert.Contains(("sprint_to_aim", "Aimed"), m);
            Assert.AreEqual(EgoController.Stance.Ads, c.CurrentStance);
            Run(c, Idle, 0.6f);
            Run(c, sprint, 1.0f);
            int shots = 0;
            c.Shot += () => shots++;
            var toFire = sprint;
            toFire.fire = true;
            c.Tick(Dt, toFire);
            Assert.AreEqual("sprint_to_fire", c.ActionName);
            Assert.AreEqual(0, shots, "erst nach dem Marker Fire");
            Run(c, toFire, 0.6f);
            Assert.Contains(("sprint_to_fire", "Fire"), m);
            Assert.Greater(shots, 0);
            // Sprint loslassen beendet die Schleife über 38 → 48
            var c2 = Ready(m);
            Run(c2, sprint, 1.0f);
            Run(c2, Idle, 0.6f);
            Assert.AreEqual(EgoController.Stance.Hip, c2.CurrentStance);
            Assert.Contains(("sprint", "Ready"), m);
        }

        [Test]
        public void Ducken_Springen_Wandnaehe()
        {
            var m = new List<(string, string)>();
            var c = Ready(m);
            Run(c, new EgoIntent { grounded = true, crouch = true }, 0.5f);
            Assert.AreEqual(EgoController.Stance.Crouch, c.CurrentStance);
            Assert.Contains(("crouch", "Crouched"), m);
            Run(c, Idle, 0.5f);
            Assert.AreEqual(EgoController.Stance.Hip, c.CurrentStance);
            Run(c, new EgoIntent { grounded = false }, 0.6f);
            Assert.AreEqual(EgoController.Stance.Air, c.CurrentStance);
            Assert.Contains(("jump_land", "Air"), m);
            Run(c, Idle, 0.6f);
            Assert.Contains(("jump_land", "Land"), m);
            Run(c, new EgoIntent { grounded = true, nearWall = true }, 0.6f);
            Assert.AreEqual(EgoController.Stance.Lowered, c.CurrentStance);
            Assert.Contains(("lowered", "Lowered"), m);
            Run(c, Idle, 0.6f);
            Assert.Contains(("lowered", "Ready"), m);
        }

        [Test]
        public void Kein_GC_Muell_im_laufenden_Bild()
        {
            var c = Ready();
            var states = new[]
            {
                new EgoIntent { grounded = true, look = new Vector2(0.4f, -0.2f), move = new Vector2(0.3f, 1), speed01 = 1 },
                new EgoIntent { grounded = true, aim = true, fire = true, look = new Vector2(-0.3f, 0.1f) },
                new EgoIntent { grounded = true, sprint = true, move = new Vector2(0, 1), speed01 = 1.6f },
            };
            foreach (var st in states)
            {
                c.ammo = 1000;
                c.magSize = 1000;
                Run(c, st, 1.5f);                     // Haltung erreicht, Zwischenspeicher gefüllt
                var s = st;
                NUnit.Framework.Assert.That(() => { for (int k = 0; k < 30; k++) c.Tick(Dt, s); },
                    Is.Not.AllocatingGCMemory(), $"{c.ActionName}");
            }
            var hip = new HipReticle(D.gameplay.hip);            // Hüft-Fadenkreuz: Aufgehen, Sichtbarkeit, Rastern bei jeder Spreizung,
            var atHip = Ready();                                 // Wechsel Sprint („^“) ↔ Hüfte in jedem Bild
            Assert.AreEqual(EgoController.Stance.Sprint, c.CurrentStance);
            hip.See(c); hip.Mask(1080); hip.See(atHip); hip.Mask(1080);
            NUnit.Framework.Assert.That(() =>
            {
                for (int k = 0; k < 30; k++) { hip.Decay(Dt, 0.5f); hip.Kick(); hip.See(k % 2 == 0 ? c : atHip); hip.Mask(1080); }
            }, Is.Not.AllocatingGCMemory(), "HipReticle");
            hip.Release();
            var demo = Bootstrap.DemoScript();                   // Eingabeablauf der Aufnahme
            demo.Read(Dt, 1);
            NUnit.Framework.Assert.That(() => { for (int k = 0; k < 300; k++) demo.Read(Dt, 1); }, Is.Not.AllocatingGCMemory(), "ScriptedInput");
        }

        // ---------------------------------------------------------------- Mündungsfeuer und Hülsen 0.16 (5.3 A / 5.4 A)
        static EgoIntent FireIntent(bool fire) => new EgoIntent { grounded = true, fire = fire };

        /// <summary>5.3 A: der Blitz steht 1 Bild bei 30/s, bei höherer Bildrate gleich lang (dur_s = 1/30 s: 60/s 2 Bilder, 144/s 5 Bilder),
        /// beginnt im Bild des Schusses und erscheint im Dauerfeuer genau einmal je Schuss.</summary>
        [Test]
        public void Muendungsfeuer_ein_Bild_bei_30_gleiche_Dauer_bei_hoeherer_Rate()
        {
            float dur = D.motion.flash.dur_s;
            Assert.AreEqual(1f / 30, dur, 1e-5f);
            foreach (float fps in new[] { 30f, 60f, 144f })
            {
                float dt = 1f / fps;
                var c = Ready();
                long s0 = c.shots;
                int tick = 0, shotTick = -1, on = 0, firstOn = -1;
                c.Shot += () => { if (shotTick < 0) shotTick = tick; };
                for (tick = 0; tick < (int)(0.5f * fps); tick++)                 // ein Schuss: Abzug ein Bild lang
                {
                    var o = c.Tick(dt, FireIntent(tick == 0));
                    if (o.flashOn) { on++; if (firstOn < 0) firstOn = tick; }
                }
                int want = Mathf.CeilToInt(dur * fps - 1e-3f);
                TestContext.WriteLine($"{fps:0}/s: {c.shots - s0} Schuss, Blitz {on} Bild(er) = {on * dt * 1000:0.0} ms ab Bild {firstOn} (Schuss im Bild {shotTick})");
                Assert.AreEqual(1, c.shots - s0, $"{fps}/s: ein Schuss");
                Assert.AreEqual(want, on, $"{fps}/s: Blitzbilder");
                Assert.AreEqual(shotTick, firstOn, $"{fps}/s: Blitz im Bild des Schusses");
                Assert.That(on * dt, Is.InRange(dur - 1e-4f, dur + dt), $"{fps}/s: Dauer wie 1 Bild bei 30/s");
                // Dauerfeuer: je Schuss genau ein Blitz (Anstiege zählen)
                c = Ready();
                s0 = c.shots;
                int onsets = 0;
                bool prev = false;
                for (int k = 0; k < (int)(1.0f * fps); k++)
                {
                    var o = c.Tick(dt, FireIntent(true));
                    if (o.flashOn && !prev) onsets++;
                    prev = o.flashOn;
                }
                Assert.AreEqual(c.shots - s0, onsets, $"{fps}/s: ein Blitz je Schuss im Dauerfeuer");
            }
        }

        /// <summary>5.4 A: je Schuss genau eine Hülse, sichtbar ab dem Bild des Schusses, im Bild nach rechts und zuletzt nach rechts unten.</summary>
        [Test]
        public void Huelse_je_Schuss_einmal_nach_rechts_unten()
        {
            var c = Ready();
            var E = new EgoScreen(c.S);
            long s0 = c.shots, e0 = c.shellsEjected;
            var shotTicks = new List<int>();
            var first = new Dictionary<int, int>();
            var track = new Dictionary<int, List<Vector3>>();
            int tick = 0;
            c.Shot += () => shotTicks.Add(tick);
            for (tick = 0; tick < 72; tick++)                                    // 0,5 s Feuer, dann 0,7 s Ruhe (60/s)
            {
                var o = c.Tick(Dt, FireIntent(tick < 30));
                for (int k = 0; k < o.shellCount; k++)
                {
                    int id = o.shellIds[k];
                    if (!first.ContainsKey(id)) { first[id] = tick; track[id] = new List<Vector3>(); }
                    track[id].Add(E.ToScreen(o.shells[k].GetColumn(3), o.camPitch));
                }
                Assert.LessOrEqual(o.shellCount, D.motion.eject.max_live, "höchstens max_live gleichzeitig");
            }
            int n = (int)(c.shots - s0);
            Assert.Greater(n, 4);
            Assert.AreEqual(n, c.shellsEjected - e0, "eine Hülse je Schuss");
            Assert.AreEqual(n, first.Count, "jede Hülse erscheint");
            for (int i = 0; i < n; i++)
            {
                int id = (int)s0 + i;
                Assert.AreEqual(shotTicks[i], first[id], $"Hülse {i} im Bild des Schusses");
                var t = track[id];
                Assert.AreEqual(Mathf.CeilToInt(D.motion.eject.life_s * 60 - 1e-3f), t.Count, 1, $"Hülse {i}: life_s sichtbar");
                Assert.Greater(t[6].x - t[0].x, 5f, $"Hülse {i}: nach 0,1 s ≥ 5 % B nach rechts");
                Assert.Greater(t[t.Count - 1].x, t[6].x, $"Hülse {i}: weiter nach rechts");
                Assert.Greater(t[t.Count - 1].y, t[6].y, $"Hülse {i}: zuletzt nach unten");
                if (i == 0) TestContext.WriteLine($"Hülse 0: Start x {t[0].x:0.0} / y {t[0].y:0.0} %, nach 0,1 s x {t[6].x:0.0} / y {t[6].y:0.0} %, " +
                                                  $"Ende x {t[t.Count - 1].x:0.0} / y {t[t.Count - 1].y:0.0} % ({t.Count} Bilder bei 60/s)");
            }
        }

        /// <summary>Kein Blitz und keine Hülse ohne Schuss: Abzug bei leerem Magazin (startet das Nachladen) und gehaltener Abzug während des
        /// taktischen und des leeren Nachladens.</summary>
        [Test]
        public void Kein_Feuer_und_keine_Huelse_bei_leerem_Magazin_und_Nachladen()
        {
            foreach (int ammo in new[] { 0, 10 })
            {
                var c = Ready();
                c.ammo = ammo;
                long s0 = c.shots, e0 = c.shellsEjected;
                int flash = 0, shells = 0, reloadTicks = 0;
                c.Tick(Dt, new EgoIntent { grounded = true, fire = ammo == 0, reload = ammo > 0 });
                long shotsInReload = 0, ejectedInReload = 0;
                for (int k = 0; k < 150; k++)
                {
                    var o = c.Tick(Dt, FireIntent(true));
                    if (!c.ActionName.StartsWith("reload")) break;    // im Bild nach dem Ende darf wieder geschossen werden
                    shotsInReload = c.shots - s0;
                    ejectedInReload = c.shellsEjected - e0;
                    reloadTicks++;
                    if (o.flashOn) flash++;
                    shells += o.shellCount;
                }
                TestContext.WriteLine($"Magazin {ammo}: {reloadTicks} Bilder Nachladen mit gehaltenem Abzug, Blitz {flash}, Hülsen {shells}");
                Assert.Greater(reloadTicks, 30, $"Magazin {ammo}: Nachladen läuft");
                Assert.AreEqual(0, shotsInReload, $"Magazin {ammo}: kein Schuss");
                Assert.AreEqual(0, flash, $"Magazin {ammo}: kein Blitz");
                Assert.AreEqual(0, shells, $"Magazin {ammo}: keine Hülse");
                Assert.AreEqual(0, ejectedInReload, $"Magazin {ammo}: nichts ausgeworfen");
            }
        }

        /// <summary>Waffen ohne Hülsen (Energie) über das Datenfeld weapon.eject.enabled, keine Sonderlogik nach Waffen-ID: Blitz ja,
        /// Hülse nein – live, in den Clips und im Pool des Modells.</summary>
        [UnityTest]
        public IEnumerator Waffe_ohne_Auswurf_wirft_keine_Huelsen()
        {
            var b = Object.FindAnyObjectByType<Bootstrap>();
            var d2 = EgoFile.Parse(b.egoJson.text);
            d2.weapon.eject.enabled = false;
            var S2 = new EgoSolver(d2);
            Assert.IsFalse(S2.Ejects);
            var c = new EgoController(S2);
            c.ReadyNow();
            int flash = 0, shells = 0;
            for (int k = 0; k < 60; k++)
            {
                var o = c.Tick(Dt, FireIntent(true));
                if (o.flashOn) flash++;
                shells += o.shellCount;
            }
            Assert.Greater(c.shots, 5);
            Assert.Greater(flash, 0, "Blitz bleibt");
            Assert.AreEqual(0, shells, "keine Hülse");
            Assert.AreEqual(0, c.shellsEjected);
            var A = d2.Action("fire_hip");
            var st = new EgoState();
            for (int f = 0; f <= A.frames; f++) Assert.AreEqual(0, S2.Evaluate(A, f, st).shellCount, "Clip ohne Hülse");
            var roles = new Dictionary<string, Material>();
            foreach (var m in b.roleMaterials) roles[m.name.Replace("Role_", "")] = m;
            var space = new GameObject("ohne_auswurf").transform;
            var rig = new EgoRig(S2, space, b.weaponModel, b.armsModel, roles, Bootstrap.ViewmodelLayer);
            Assert.AreEqual(0, rig.ShellPool, "kein Hülsenpool");
            Assert.AreEqual(D.motion.eject.max_live, b.Player.rig.ShellPool, "BASIC-01: Pool mit max_live Hülsen");
            Object.Destroy(space.gameObject);
            yield return null;
        }

        /// <summary>5.4 A: Hülsen aus einem festen Pool – im Dauerfeuer keine neuen Objekte nach dem Aufwärmen, höchstens max_live sichtbar,
        /// kein GC-Müll je Bild (Controller und Modell).</summary>
        [UnityTest]
        public IEnumerator Huelsenpool_ohne_neue_Objekte()
        {
            var p = Object.FindAnyObjectByType<Bootstrap>().Player;
            int mag = p.C.magSize;
            p.C.ReadyNow();
            p.C.magSize = p.C.ammo = 100000;
            p.Teleport(new Vector3(0f, 0.01f, 1.6f), 0f);
            p.input = new ScriptedInput().Add(0, 100, hold: "fire");
            p.deltaOverride = () => Dt;
            for (int k = 0; k < 30; k++) yield return null;                    // aufwärmen
            int objs = p.GetComponentsInChildren<Transform>(true).Length;
            long e0 = p.C.shellsEjected;
            int most = 0, flashes = 0;
            for (int k = 0; k < 120; k++)
            {
                yield return null;
                most = Mathf.Max(most, p.C.output.shellCount);
                if (p.rig.FlashShown) flashes++;
            }
            TestContext.WriteLine($"2 s Dauerfeuer: {p.C.shellsEjected - e0} Hülsen ausgeworfen, höchstens {most} sichtbar (Pool {p.rig.ShellPool}), {flashes} Blitzbilder");
            Assert.Greater(p.C.shellsEjected - e0, 20);
            Assert.AreEqual(objs, p.GetComponentsInChildren<Transform>(true).Length, "keine neuen Objekte");
            Assert.LessOrEqual(most, p.rig.ShellPool);
            Assert.Greater(flashes, 0);
            var c = p.C;
            var rig = p.rig;
            NUnit.Framework.Assert.That(() => { for (int k = 0; k < 60; k++) rig.Apply(c.Tick(Dt, FireIntent(true))); },
                Is.Not.AllocatingGCMemory(), "Feuer, Blitz und Hülsen je Bild");
            p.input = new ScriptedInput().Add(0, 1000);
            yield return null;
            p.deltaOverride = null;
            p.C.magSize = mag;
            p.C.ReadyNow();
            p.C.ammo = mag;
        }

        [UnityTest]
        public IEnumerator Wandnaehe_im_Parcours_senkt_die_Waffe()
        {
            var p = Object.FindAnyObjectByType<Bootstrap>().Player;
            p.input = new ScriptedInput().Add(0, 100);
            p.deltaOverride = () => 1f / 30f;
            p.C.ReadyNow();
            p.Teleport(new Vector3(-6f, 0.01f, -2.95f), 0f);     // vor Säule 1 (Vorderseite bei z −2,4)
            for (int i = 0; i < 30; i++) yield return null;
            Assert.IsTrue(p.NearWall(), "Säule vor dem Kopf erkannt");
            Assert.AreEqual(EgoController.Stance.Lowered, p.C.CurrentStance);
            p.Teleport(new Vector3(0f, 0.01f, 1.5f), 0f);         // frei: zurück zur Hüfte
            for (int i = 0; i < 45; i++) yield return null;
            Assert.IsFalse(p.NearWall());
            Assert.AreEqual(EgoController.Stance.Hip, p.C.CurrentStance);
        }

        /// <summary>AgX-Durchgang im gerenderten Bild: lineare Werte einer unbeleuchteten Fläche kommen wie Blender-AgX an
        /// (0,18 → ≈ 0,44; ohne Abbildung würden 1 und 4 beide als 1,0 abgeschnitten).</summary>
        [UnityTest]
        public IEnumerator AgX_Tonwerte_im_Bild()
        {
            var b = Object.FindAnyObjectByType<Bootstrap>();
            var cam = b.Player.worldCam;
            var q = GameObject.CreatePrimitive(PrimitiveType.Quad);
            Object.Destroy(q.GetComponent<Collider>());
            var m = new Material(b.backdrop);
            q.GetComponent<Renderer>().sharedMaterial = m;
            q.transform.SetParent(cam.transform, false);
            q.transform.localPosition = new Vector3(0, 0, 0.5f);
            q.transform.localScale = new Vector3(3, 3, 1);
            var rt = Bootstrap.HdrTarget(64, 36, 1);
            var old = cam.targetTexture;
            cam.targetTexture = rt;
            var tex = new Texture2D(64, 36, TextureFormat.RGB24, false);
            var got = new Dictionary<float, float>();
            foreach (var v in new[] { 0.18f, 1f, 4f })
            {
                m.SetColor("_BaseColor", new Color(v, v, v, 1).gamma);    // linear v (Materialfarben sind Gamma-Werte)
                yield return null;                             // WaitForEndOfFrame kommt im Stapelbetrieb nicht
                yield return null;
                Bootstrap.ReadBack(rt, tex);
                got[v] = tex.GetPixel(12, 28).r;               // oben links: kein Viewmodel davor
                TestContext.WriteLine($"Wert {v}: Mitte {tex.GetPixel(32, 18)} oben links {tex.GetPixel(12, 28)} unten rechts {tex.GetPixel(52, 6)}");
            }
            var vd = UnityEngine.Rendering.Universal.CameraExtensions.GetUniversalAdditionalCameraData(b.Player.viewCam);
            TestContext.WriteLine($"HDR {cam.allowHDR}, rt {rt.format}, Stapel {vd.renderType}, Quad-Ebene {q.layer}, Maske {cam.cullingMask}, " +
                                  $"Nebel {RenderSettings.fog} {RenderSettings.fogStartDistance}, Kamera {cam.transform.position} → {cam.transform.forward}");
            cam.targetTexture = old;
            Object.Destroy(q);
            Assert.AreEqual(0.461f, got[0.18f], 0.02f, "Mittelgrau (Blender AgX MHC: 0,18 → 0,461)");
            Assert.That(got[1f], Is.InRange(0.65f, 0.92f), "1,0 wird abgebildet, nicht abgeschnitten");
            Assert.Greater(got[4f], got[1f] + 0.03f, "Spitzlichter über 1 bleiben unterscheidbar");
            Assert.Less(got[4f], 0.995f);
        }

        [UnityTest]
        public IEnumerator Skin_wechseln_nur_an_der_Waffe()
        {
            var p = Object.FindAnyObjectByType<Bootstrap>().Player;
            Assert.AreEqual(8, p.skins.Length);
            var arm = p.rig.SegR("hand").GetComponentInChildren<Renderer>().sharedMaterial;
            var before = p.rig.WeaponAtlasMaterial;
            p.SetSkin(3);
            yield return null;
            Assert.AreSame(p.skins[3], p.rig.WeaponAtlasMaterial, "Waffe trägt den Skin");
            Assert.AreSame(arm, p.rig.SegR("hand").GetComponentInChildren<Renderer>().sharedMaterial, "Arme bleiben");
            p.SetSkin(0);
            Assert.AreSame(before, p.rig.WeaponAtlasMaterial);
        }

        /// <summary>Frage 4.3 A (Visier-Standard 3 §6): Schuss-Ring 2 % H nur im Zielen für genau ein Bild, Treffer-X 4,5 % H mindestens
        /// 0,17 s, in Familienfarbe Orange; aus der Hüfte nur das Treffer-X. Vorher: vier Quadrate für 0,12 s, kein Ring.</summary>
        [UnityTest]
        public IEnumerator Schuss_Ring_und_Treffer_X()
        {
            var p = Object.FindAnyObjectByType<Bootstrap>().Player;
            p.C.ReadyNow();
            p.Teleport(new Vector3(0f, 0.01f, 1.6f), 0f);
            yield return null;
            var wall = GameObject.CreatePrimitive(PrimitiveType.Cube);   // Scheibe 3 m vor dem Auge, größer als jede Streuung
            wall.transform.position = p.worldCam.transform.position + p.worldCam.transform.forward * 3f;
            wall.transform.rotation = p.worldCam.transform.rotation;
            wall.transform.localScale = new Vector3(1.5f, 1.5f, 0.1f);
            wall.AddComponent<RangeTarget>();
            p.input = new ScriptedInput().Add(0, 10).Add(0.2f, 0.25f, hold: "fire").Add(0.6f, 2.6f, hold: "aim").Add(1.5f, 1.55f, hold: "aim fire");
            p.deltaOverride = () => 1f / 30f;
            long s0 = p.C.shots;
            int h0 = p.hits;
            var rows = new List<(long shots, int hits, bool ring, bool x, float ads)>();
            for (int k = 0; k < 75; k++)                       // 2,5 s
            {
                yield return null;
                rows.Add((p.C.shots - s0, p.hits - h0, p.ShotRingVisible, p.HitXVisible, p.C.adsWeight));
            }
            wall.SetActive(false);                             // nicht zerstören: die Einschläge hängen an ihr und bleiben in der Warteschlange
            p.input = new ScriptedInput().Add(0, 1000);
            yield return null;
            p.deltaOverride = null;
            p.C.ReadyNow();
            p.C.ammo = p.C.magSize;
            p.Teleport(new Vector3(0f, 0.01f, 1.6f), 0f);
            int hipShot = rows.FindIndex(r => r.shots == 1), adsShot = rows.FindIndex(r => r.shots == 2);
            Assert.AreEqual(2, rows[rows.Count - 1].shots, "zwei Schüsse");
            Assert.AreEqual(2, rows[rows.Count - 1].hits, "beide treffen");
            Assert.Less(rows[hipShot].ads, 0.5f);
            Assert.Greater(rows[adsShot].ads, 0.99f);
            int ringHip = rows.Take(adsShot).Count(r => r.ring), ringAds = rows.Skip(adsShot).Count(r => r.ring);
            int xHip = rows.Skip(hipShot).Take(adsShot - hipShot).Count(r => r.x), xAds = rows.Skip(adsShot).Count(r => r.x);
            TestContext.WriteLine($"Rückmeldung bei 30/s: Ring Hüfte {ringHip} Bilder, Ring Zielen {ringAds} Bild(er) ab Bild {adsShot}; " +
                                  $"Treffer-X Hüfte {xHip} Bilder ({xHip / 30f:0.000} s), Zielen {xAds} Bilder ({xAds / 30f:0.000} s)");
            Assert.AreEqual(0, ringHip, "aus der Hüfte kein Schuss-Ring");
            Assert.AreEqual(1, ringAds, "Schuss-Ring genau ein Bild");
            Assert.IsTrue(rows[adsShot].ring, "Ring im Bild des Schusses");
            foreach (int x in new[] { xHip, xAds }) Assert.That(x / 30f, Is.InRange(0.17f, 0.25f), "Treffer-X ≥ 0,17 s");
            Assert.AreEqual(0.02f, AdsFeedback.ShotRingShareH, 1e-6f, "Ring 2 % H");
            Assert.AreEqual(0.045f, AdsFeedback.HitXShareH, 1e-6f, "Treffer-X 4,5 % H");
            Assert.AreEqual((Color)new Color32(0xE0, 0x65, 0x1E, 0xFF), AdsFeedback.Orange, "Familienfarbe Orange (kit accent)");
        }

        /// <summary>Patch einschuss (Nutzerbild 26.10.2026: „Die Einschusslöcher werden so breit schwarz“): Ab dem 81. Treffer wird das älteste
        /// Loch wiederverwendet. Es muss seine Weltgröße (DecalSize) behalten, auch wenn es vorher an einem breiten, flachen Träger hing
        /// (Wand 20 × 4 × 0,2 m). Vorher galt localScale im Maßstab des alten Trägers: das Loch wurde 1 m breit.</summary>
        [UnityTest]
        public IEnumerator Einschussloecher_behalten_ihre_Groesse_beim_Wiederverwenden()
        {
            var p = Object.FindAnyObjectByType<Bootstrap>().Player;
            int mag = p.C.magSize;
            p.C.ReadyNow();
            p.C.magSize = p.C.ammo = 1000;
            p.Teleport(new Vector3(0f, 0.01f, 1.6f), 0f);
            yield return null;
            var cam = p.worldCam.transform;
            var wall = GameObject.CreatePrimitive(PrimitiveType.Cube);
            wall.transform.SetPositionAndRotation(cam.position + cam.forward * 3f, cam.rotation);
            wall.transform.localScale = new Vector3(20f, 4f, 0.2f);
            GameObject block = null;
            try                                                // aufräumen auch bei Fehlschlag: sonst stehen Wand und Würfel für die Folgetests im Weg
            {
                var bursts = new ScriptedInput();                  // Feuerstöße mit Pause: die Rückstoßbahn kehrt zurück, alles trifft die Wand
                for (int k = 0; k < 40; k++) bursts.Add(k * 1.2f, k * 1.2f + 0.6f, hold: "fire").Add(k * 1.2f + 0.6f, k * 1.2f + 1.2f);
                p.input = bursts;
                p.deltaOverride = () => 1f / 30f;
                int onWall = 0;
                for (int f = 0; f < 1400 && onWall < EgoPlayer.DecalMax; f++)               // bis jedes Loch im Pool an der Wand hängt
                {
                    yield return null;
                    onWall = wall.transform.childCount;
                }
                Assert.AreEqual(EgoPlayer.DecalMax, onWall, "alle Löcher an der Wand");
                p.input = new ScriptedInput().Add(0, 100, hold: "fire");
                block = GameObject.CreatePrimitive(PrimitiveType.Cube);                 // neuer Träger davor, gleichmäßig skaliert
                block.transform.SetPositionAndRotation(cam.position + cam.forward * 2f, cam.rotation);
                block.transform.localScale = Vector3.one * 0.8f;
                long s1 = p.C.shots;
                while (p.C.shots < s1 + 10) yield return null;
                p.input = new ScriptedInput().Add(0, 1000);
                yield return null;
                var holes = Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None).Where(r => r.name == "Einschlag").ToList();
                var moved = holes.Where(r => r.transform.parent == block.transform).ToList();
                float worst = holes.Max(r => Mathf.Max(r.transform.lossyScale.x, r.transform.lossyScale.y));
                TestContext.WriteLine($"{holes.Count} Löcher (höchstens {EgoPlayer.DecalMax}), {moved.Count} wiederverwendet auf dem neuen Träger, " +
                                      $"größte Kante {worst * 100:0.0} cm (Soll {EgoPlayer.DecalSize * 100:0.0} cm)");
                Assert.AreEqual(EgoPlayer.DecalMax, holes.Count, "Pool voll, alle Löcher an Wand und neuem Träger");
                Assert.GreaterOrEqual(moved.Count, 8, "wiederverwendete Löcher auf dem neuen Träger");
                foreach (var r in holes)
                {
                    var ls = r.transform.lossyScale;
                    Assert.AreEqual(EgoPlayer.DecalSize, ls.x, 0.002f, $"Lochbreite {ls.x * 100:0.0} cm");
                    Assert.AreEqual(EgoPlayer.DecalSize, ls.y, 0.002f, $"Lochhöhe {ls.y * 100:0.0} cm");
                }
            }
            finally
            {
                p.input = new ScriptedInput().Add(0, 1000);
                if (block != null) block.SetActive(false);    // nicht zerstören: die Löcher hängen daran und bleiben in der Warteschlange
                wall.SetActive(false);
                p.deltaOverride = null;
                p.C.magSize = mag;
                p.C.ReadyNow();
                p.C.ammo = mag;
            }
        }

        /// <summary>Entscheidungsliste 5.1 A: im Zielen geht der Rückstoß in die Welt – Weltanker 20 m voraus (Weltkamera) wandert beim
        /// Viererstoß ≈ 4 % H (Destiny Chroma Rush), das Visier (Socket_Reticle durch die Viewmodel-Kamera) bleibt unter 1 % H; Rückkehr
        /// 0,4–0,6 s nach dem letzten Schuss unter 0,25 % H, ohne Unterschwingen. Zum Vergleich aus der Hüfte: dort springt die Waffe
        /// sichtbar. Bis 0.14 nickte im Zielen auch das Viewmodel („Visier springt leicht“).</summary>
        [UnityTest]
        public IEnumerator Rueckstoss_im_Zielen_geht_in_die_Welt()
        {
            var p = Object.FindAnyObjectByType<Bootstrap>().Player;
            var rt = new RenderTexture(1280, 720, 16);                 // 16:9 wie die Ego-Stills und die Destiny-Messung
            p.worldCam.targetTexture = rt;
            var ret = BMath.V(D.Anchor("Socket_Reticle").pos);
            var res = new Dictionary<bool, (float world, float sight, float back, float under)>();
            foreach (bool ads in new[] { true, false })
            {
                p.C.ReadyNow();
                p.C.ammo = p.C.magSize;
                p.Teleport(new Vector3(0f, 0.01f, 1.6f), 0f);
                p.input = new ScriptedInput().Add(0, 100);
                p.deltaOverride = () => Dt;
                for (int k = 0; k < 40; k++) yield return null;          // Pendeln, Rückstoß und Bahn klingen ab
                var input = new ScriptedInput().Add(0, 3.2f, hold: ads ? "aim" : "").Add(1.0f, 1.3f, hold: ads ? "aim fire" : "fire");
                p.input = input;
                yield return null;
                var anchor = p.worldCam.transform.position + p.worldCam.transform.forward * 20f;
                long s0 = p.C.shots;
                var rows = new List<(float t, long shots, float world, float sight)>();
                for (int k = 0; k < 180; k++)                             // 3 s
                {
                    yield return null;
                    float wy = (1 - p.worldCam.WorldToViewportPoint(anchor).y) * 100;   // % H von oben
                    var o = p.C.output;
                    float sy = Scr.ToScreen(o.weapon.MultiplyPoint3x4(ret), o.camPitch).y;
                    rows.Add((input.time, p.C.shots - s0, wy, sy));
                }
                int f1 = rows.FindIndex(r => r.shots >= 1), fl = rows.FindIndex(r => r.shots >= 4);
                Assert.Greater(f1, 0, "erster Schuss");
                Assert.AreEqual(4, rows[rows.Count - 1].shots, "Viererstoß");
                float w0 = rows[f1 - 1].world, s0y = rows[f1 - 1].sight;
                var after = rows.Skip(f1).ToList();
                float world = after.Max(r => r.world - w0);              // Welt wandert nach unten (Blick hoch)
                float sight = after.Max(r => r.sight) - after.Min(r => r.sight);
                int back = rows.FindIndex(fl, r => Mathf.Abs(r.world - w0) < 0.25f && r.t > rows[fl].t + 0.1f);
                float under = rows.Skip(fl).Min(r => r.world - w0);
                res[ads] = (world, sight, back < 0 ? -1 : (back - fl) * Dt, under);
                TestContext.WriteLine($"{(ads ? "Zielen" : "Hüfte")}: Welt {world:0.00} % H, Visier mit Atmen {sight:0.00} % H Spitze–Spitze, zurück unter 0,25 % H " +
                                      $"{res[ads].back:0.000} s nach dem letzten Schuss, tiefster Wert {under:0.000} % H");
            }
            p.input = new ScriptedInput().Add(0, 1000);
            yield return null;
            p.deltaOverride = null;
            p.worldCam.targetTexture = null;
            rt.Release();
            p.C.ReadyNow();
            p.C.ammo = p.C.magSize;
            p.Teleport(new Vector3(0f, 0.01f, 1.6f), 0f);
            // Visier: gegen einen Zwilling, der nicht schießt (gleiche Zeitschritte, das Atmen hebt sich auf)
            var vis = new Dictionary<bool, float>();
            foreach (bool ads in new[] { true, false })
            {
                var c = Ready();
                var c0 = Ready();
                var hold = new EgoIntent { grounded = true, aim = ads };
                Run(c, hold, 0.8f);
                Run(c0, hold, 0.8f);
                int n = 0;
                c.Shot += () => n++;
                var dy = new List<float>();
                for (int k = 0; k < 72; k++)                                // 1,2 s ab dem ersten Schuss
                {
                    var fire = hold;
                    fire.fire = n < 4;
                    c.Tick(Dt, fire);
                    c0.Tick(Dt, hold);
                    float y = Scr.ToScreen(c.output.weapon.MultiplyPoint3x4(ret), c.output.camPitch).y;
                    float y0 = Scr.ToScreen(c0.output.weapon.MultiplyPoint3x4(ret), c0.output.camPitch).y;
                    dy.Add(y - y0);
                }
                vis[ads] = dy.Max() - dy.Min();
                TestContext.WriteLine($"{(ads ? "Zielen" : "Hüfte")}: Visier durch den Rückstoß {vis[ads]:0.00} % H Spitze–Spitze (gegen den Zwilling ohne Schuss)");
            }
            var a = res[true];
            Assert.That(a.world, Is.InRange(3.5f, 5.0f), "Welt ≈ 4 % H je Viererstoß");
            Assert.Less(vis[true], 1.0f, "Visier < 1 % H");
            Assert.That(a.back, Is.InRange(0.4f, 0.6f), "Rückkehr 0,4–0,6 s");
            Assert.Greater(a.under, -0.15f, "kein Unterschwingen");
            Assert.Greater(vis[false], 3 * vis[true], "aus der Hüfte springt die Waffe sichtbar, im Zielen steht das Visier");
        }

        /// <summary>Entscheidungsliste 4.1 A: das Hüft-Fadenkreuz ist nur in der Hüfte sichtbar und geht beim Hüftfeuer auf; es ist im
        /// ersten Bild des Zielens weg (nicht erst mit dem Zoom), im Sprint zeigt die Automatik nur „^“, beim Nachladen, Wegstecken und
        /// Ziehen ist es aus; danach wieder da. Vorher (0.10 bis 0.12) gab es kein Hüft-Fadenkreuz.</summary>
        [UnityTest]
        public IEnumerator Hueft_Fadenkreuz_je_Zustand()
        {
            var p = Object.FindAnyObjectByType<Bootstrap>().Player;
            p.C.ReadyNow();
            p.C.ammo = p.C.magSize;
            p.Teleport(new Vector3(0f, 0.01f, 1.6f), 0f);
            yield return null;
            const float dt = 1f / 30f;
            var script = new ScriptedInput().Add(0, 12)
                .Add(0.5f, 0.75f, hold: "fire")                                  // Hüftfeuer
                .Add(1.5f, 2.3f, hold: "aim")                                    // Zielen
                .Add(3.0f, 3.9f, hold: "sprint", move: new Vector2(0, 1))        // Sprint
                .Add(4.6f, 4.65f, press: "reload")                               // taktisch nachladen
                .Add(8.0f, 8.05f, press: "holster")
                .Add(9.4f, 9.45f, press: "draw");
            p.input = script;
            p.deltaOverride = () => dt;
            var rows = new List<(float t0, bool vis, string why, EgoController.Stance st, string act, float spread, bool sprintForm, string kind)>();
            for (int k = 0; k < 330; k++)                      // 11 s
            {
                float t0 = script.time;
                yield return null;
                var h = p.hipReticle;
                rows.Add((t0, h.Visible, h.Reason, p.C.CurrentStance, p.C.ActionName, h.spread, h.SprintForm, h.Kind));
            }
            p.input = new ScriptedInput().Add(0, 1000);
            yield return null;
            p.deltaOverride = null;
            p.C.ReadyNow();
            p.C.ammo = p.C.magSize;
            p.Teleport(new Vector3(0f, 0.01f, 1.6f), 0f);

            var runs = new System.Text.StringBuilder();          // Zustandsfolge (Grund, ab t) fürs Protokoll
            for (int k = 0; k < rows.Count; k++)
                if (k == 0 || rows[k].why != rows[k - 1].why) runs.Append($"{rows[k].t0:0.00} {rows[k].why}/{rows[k].act}{(rows[k].vis ? "+" : "-")} · ");
            TestContext.WriteLine(runs.ToString());
            var idle = rows.Where(r => r.t0 < 0.45f).ToList();
            Assert.IsTrue(idle.All(r => r.vis && r.why == "hip" && r.kind == "ring_dot"), "Hüfte in Ruhe: sichtbar, Ring mit Punkt");
            var fire = rows.Where(r => r.t0 >= 0.5f && r.t0 < 1.4f).ToList();
            Assert.IsTrue(fire.All(r => r.vis), "Hüftfeuer: sichtbar");
            float peak = fire.Max(r => r.spread);
            Assert.Greater(peak, 2 * D.gameplay.hip.spread.per_shot, "geht beim Hüftfeuer auf (3 Schuss in 0,25 s)");
            Assert.Less(rows.First(r => r.t0 >= 1.45f).spread, 0.25f * peak, "klingt ab");
            int ads = rows.FindIndex(r => r.st == EgoController.Stance.Ads);
            Assert.That(rows[ads].t0, Is.InRange(1.5f - 1e-4f, 1.5f + dt), "Zielen beginnt im Bild der Eingabe");
            Assert.IsTrue(rows[ads - 1].vis, "Bild davor noch sichtbar");
            Assert.IsFalse(rows[ads].vis, "im ersten Bild des Zielens weg");
            Assert.IsTrue(rows.Where(r => r.t0 >= 1.5f && r.t0 < 2.3f).All(r => !r.vis), "im Zielen aus");
            var back = rows.FindIndex(ads, r => r.t0 >= 2.3f && r.vis);
            Assert.Greater(back, 0, "nach dem Zielen wieder da");
            Assert.Less(rows[back].t0, 2.9f, "zurück in der Hüfte");
            var spr = rows.Where(r => r.st == EgoController.Stance.Sprint).ToList();
            Assert.Greater(spr.Count, 15, "Sprint erreicht");
            Assert.IsTrue(spr.All(r => r.vis && r.sprintForm && r.kind == "caret"), "Sprint: Automatik nur „^“");
            var rel = rows.Where(r => r.act == "reload_tactical").ToList();
            Assert.Greater(rel.Count, 50, "Nachladen läuft (2,1 s)");
            Assert.IsTrue(rel.All(r => !r.vis && r.why == "reload_tactical"), "Nachladen: aus");
            Assert.IsTrue(rows.Where(r => r.t0 >= 7.0f && r.t0 < 7.9f).All(r => r.vis), "nach dem Nachladen wieder da");
            var hol = rows.Where(r => r.t0 >= 8.0f + dt && r.t0 < 9.4f).ToList();
            Assert.IsTrue(hol.All(r => !r.vis), "Wegstecken und weggesteckt: aus");
            Assert.IsTrue(hol.Any(r => r.why == "holster") && hol.Any(r => r.why == "holstered"));
            var drw = rows.Where(r => r.act == "draw").ToList();               // Grund „holstered“: der Controller ist bis Ready weggesteckt
            Assert.Greater(drw.Count, 3, "Ziehen läuft");
            Assert.IsTrue(drw.All(r => !r.vis), "Ziehen: aus");
            Assert.IsTrue(rows[rows.Count - 1].vis && rows[rows.Count - 1].why == "hip", "danach wieder in der Hüfte");
            TestContext.WriteLine($"Hüft-Fadenkreuz bei 30/s: Spitze {peak:0.00} mm, Zielen ab Bild {ads} (t {rows[ads].t0:0.000} s) weg, zurück ab " +
                                  $"t {rows[back].t0:0.000} s, Sprint {spr.Count} Bilder „^“, Nachladen {rel.Count} Bilder aus, Ziehen {drw.Count} Bilder aus");
        }

        /// <summary>Entscheidungsliste 1.2 A: im Zielen zoomt die Welt mit dem Klassenwert der Pilot-Automatik (1,9 aus basic/reticles.py,
        /// vorher fest 1,35): tan(Welt-FOV/2) = tan(Viewmodel-FOV/2) / 1,9; das Viewmodel bleibt bei 75° horizontal.</summary>
        [UnityTest]
        public IEnumerator Weltzoom_im_Spiel_aus_der_Klasse()
        {
            var p = Object.FindAnyObjectByType<Bootstrap>().Player;
            p.C.ReadyNow();
            p.Teleport(new Vector3(0f, 0.01f, 1.6f), 0f);
            p.input = new ScriptedInput().Add(0, 1.2f, hold: "aim");
            p.deltaOverride = () => 1f / 30f;
            for (int k = 0; k < 30; k++) yield return null;
            float zoom = Mathf.Tan(p.viewCam.fieldOfView * Mathf.Deg2Rad / 2) / Mathf.Tan(p.worldCam.fieldOfView * Mathf.Deg2Rad / 2);
            float hip0 = p.viewCam.fieldOfView;
            p.input = new ScriptedInput().Add(0, 1000);
            for (int k = 0; k < 20; k++) yield return null;
            float back = p.worldCam.fieldOfView;
            p.deltaOverride = null;
            TestContext.WriteLine($"Weltzoom im Zielen {zoom:0.000} (Daten {D.gameplay.world_zoom}), Welt-FOV Hüfte {back:0.00}° = Viewmodel {hip0:0.00}°");
            Assert.AreEqual(1f, p.C.adsWeight > 0 ? 0f : 1f, "zurück in der Hüfte");
            Assert.AreEqual(D.gameplay.world_zoom, zoom, 1e-3f, "Weltzoom = Klassenwert");
            Assert.AreEqual(1.9f, zoom, 1e-3f, "Automatik 1,9");
            Assert.AreEqual(hip0, back, 0.01f, "Hüfte ungezoomt");
        }

        [UnityTest]
        public IEnumerator Szene_startet_und_spielt_den_Ablauf()
        {
            var b = Object.FindAnyObjectByType<Bootstrap>();
            Assert.IsNotNull(b, "Bootstrap in der Szene");
            var p = b.Player;
            Assert.IsNotNull(p);
            Assert.IsTrue(p.rig.weaponRoot.gameObject.activeInHierarchy);
            Assert.AreEqual(Bootstrap.ViewmodelLayer, p.rig.weaponRoot.gameObject.layer);
            int shots = 0;
            p.C.Shot += () => shots++;
            p.C.ReadyNow();
            p.C.ammo = 9;
            p.input = Bootstrap.DemoScript();
            p.deltaOverride = () => 1f / 30f;
            for (int i = 0; i < 30 * 8 && i < 1000; i++) yield return null;
            Assert.Greater(shots, 0, "Feuerstoß");
            Assert.IsTrue(p.log.Any(l => l.Contains("reload_empty MagIn")), "leeres Nachladen: " + string.Join(" | ", p.log));
            Assert.IsTrue(p.log.Any(l => l.Contains("inspect Start")), "Betrachten");
            Assert.Greater(p.C.ammo, 0);
        }
    }
}
