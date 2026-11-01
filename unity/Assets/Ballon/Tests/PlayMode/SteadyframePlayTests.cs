// PlayMode (0.37 „Steadyframe“): kein GC-Speicher je Schuss, Waffenwechsel, Zielen, Nachladen und Bewegen nach dem Aufwärmen – über
// die ganze Kette EgoPlayer.Step (Eingabe, Arsenal, Controller, Rig, Schuss mit Strahl und Treffer, Wirkung, Projektile, Explosionen)
// für alle Waffen, dazu die Anzeigetexte und das Hüft-Fadenkreuz beim Aufgehen. Virtuelle Zeit (1/60 s je Schritt).
// Gegenprobe: BALLON_STEADYFRAME_OFF=1 (Markertexte je Ereignis neu, Protokoll unbegrenzt) – dann scheitert der Test.
using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
using UnityEngine.TestTools.Constraints;
using Is = UnityEngine.TestTools.Constraints.Is;

namespace Ballon.Ego.Tests
{
    public class SteadyframePlayTests
    {
        const float Dt = 1f / 60f;

        [UnitySetUp]
        public IEnumerator LoadScene()
        {
            if (Object.FindAnyObjectByType<Bootstrap>() == null)
            {
                SceneManager.LoadScene("Firstfeel");
                yield return null;
                yield return null;
            }
        }

        [TearDown]
        public void Zuruecksetzen()                          // auch nach einem Fehlschlag: keine feste Zeit und kein Ablauf für Folgetests
        {
            var b = Object.FindAnyObjectByType<Bootstrap>();
            if (b == null || b.Player == null) return;
            b.Player.deltaOverride = null;
            b.Player.input = new ScriptedInput().Add(0, 1000);
        }

        /// <summary>Ablauf der Ruckelmessung (StutterBench) je Waffe: wählen, Hüftschuss (Bogen spannen, Fusion laden), Dauerfeuer 3 s,
        /// Zielen, Nachladen, Bewegen mit Drehung. Ende bei Waffe 1.</summary>
        static ScriptedInput Cycle(Bootstrap b, out float seconds)
        {
            var s = new ScriptedInput();
            float t = 0;
            int nw = b.Solvers.Length;
            for (int w = 0; w <= nw; w++)
            {
                int k = w % nw;
                s.Add(t, t + 2f, press: $"weapon{k + 1}");
                t += 2f;
                if (w == nw) break;
                var g = b.Solvers[k].D.gameplay;
                float tap = g.Draw ? 1.2f : g.charge_s > 0 ? 1.0f : 0.05f;
                s.Add(t, t + tap, hold: "fire"); s.Add(t + tap, t + 2f); t += 2f;
                s.Add(t, t + 3f, hold: "fire"); s.Add(t + 3f, t + 3.5f); t += 3.5f;
                s.Add(t, t + 1.5f, hold: "aim"); s.Add(t + 1.5f, t + 2f); t += 2f;
                s.Add(t, t + 3f, press: "reload"); t += 3f;
                s.Add(t, t + 1.5f, move: new Vector2(0.6f, 0.8f), lookPerS: new Vector2(60, 0));
                s.Add(t + 1.5f, t + 3f, move: new Vector2(-0.6f, -0.8f), lookPerS: new Vector2(-60, 0));
                t += 3f;
            }
            seconds = t;
            return s;
        }

        [UnityTest]
        public IEnumerator Kein_GC_Speicher_je_Schuss_und_Wechsel_nach_dem_Aufwaermen()
        {
            var b = Object.FindAnyObjectByType<Bootstrap>();
            var p = b.Player;
            p.UseWeapon(0);
            p.Teleport(Bootstrap.ParcoursStart, 0f);
            foreach (var c in p.arsenal.C) { c.ReadyNow(); c.ammo = c.magSize; }
            var warm = Cycle(b, out float sec);
            var run = Cycle(b, out _);
            int steps = Mathf.CeilToInt(sec / Dt);
            var fx = p.fx;
            Assert.IsNotNull(fx, "Wirkung der Waffen (WeaponFx) angelegt");
            int shots0 = fx.launched, hits0 = p.hits;
            p.deltaOverride = () => Dt;
            p.input = warm;
            for (int i = 0; i < steps; i++) { p.Step(Dt); p.UpdateHudText(); }   // Aufwärmen: Übersetzung, Texte, Tabellen, Pools
            p.Teleport(Bootstrap.ParcoursStart, 0f);                           // zweiter Lauf aus dem Endzustand des ersten (wie gemessen)
            p.input = Cycle(b, out _);
            for (int i = 0; i < steps; i++) { p.Step(Dt); p.UpdateHudText(); }
            long markers0 = p.log.Count;
            p.Teleport(Bootstrap.ParcoursStart, 0f);
            p.input = run;
            int ex0 = fx.explosions, imp0 = fx.impacts;
            try
            {
                NUnit.Framework.Assert.That(() => { for (int i = 0; i < steps; i++) { p.Step(Dt); p.UpdateHudText(); } },
                    Is.Not.AllocatingGCMemory(), "Schuss, Wechsel, Zielen, Nachladen, Bewegen (alle Waffen)");
            }
            catch (AssertionException)
            {
                Where(p, Cycle(b, out _), steps);              // Fundstellen nennen: Schritte mit Speicher, Waffe und Aktion
                throw;
            }
            TestContext.WriteLine($"{b.Solvers.Length} Waffen, {steps} Schritte: {fx.explosions - ex0} Explosionen, " +
                                  $"{fx.impacts - imp0} Einschläge, {fx.launched - shots0} Projektile (beide Läufe), " +
                                  $"{p.hits - hits0} Treffer, Protokoll {p.log.Count} Einträge");
            Assert.AreEqual(0, p.arsenal.Active, "Ablauf endet bei Waffe 1");
            Assert.Greater(fx.explosions - ex0, 0, "Explosionen im gemessenen Lauf");
            Assert.Greater(fx.impacts - imp0, 0, "Einschläge im gemessenen Lauf");
            Assert.LessOrEqual(p.log.Count, EgoPlayer.LogMax, "Protokoll begrenzt");
            Assert.Greater(markers0, 0, "Protokoll nach dem Aufwärmen nicht leer");
            p.input = new ScriptedInput().Add(0, 1000);
            p.deltaOverride = null;
            yield return null;
        }

        /// <summary>Bei einem Fehlschlag: noch ein Lauf, je Schritt die GC.Alloc-Proben (Recorder auf diesem Thread, wie
        /// Is.Not.AllocatingGCMemory) – die ersten 25 Schritte mit Speicher mit Waffe, Aktion und Aktionsbild.</summary>
        static void Where(EgoPlayer p, ScriptedInput s, int steps)
        {
            p.Teleport(Bootstrap.ParcoursStart, 0f);
            p.input = s;
            var rec = UnityEngine.Profiling.Recorder.Get("GC.Alloc");
            int Count(System.Action a)
            {
                rec.enabled = false;
                rec.FilterToCurrentThread();
                rec.enabled = true;
                a();
                rec.enabled = false;
                rec.CollectFromAllThreads();
                return rec.sampleBlockCount;
            }
            int shown = 0, total = 0;
            for (int i = 0; i < steps; i++)
            {
                int a = Count(() => p.Step(Dt)), h = Count(p.UpdateHudText);
                if (a + h == 0) continue;
                total += a + h;
                if (shown++ < 25)
                    TestContext.WriteLine($"Schritt {i} ({i * Dt:0.00} s): Waffe {p.arsenal.Active + 1} {p.C.S.D.gameplay.weapon_type} " +
                                          $"{p.C.ActionName} {p.C.Frame:0.0} – Step {a}, Anzeige {h} Proben");
            }
            TestContext.WriteLine($"{shown} Schritte mit Speicher, zusammen {total} GC.Alloc-Proben");
        }

        /// <summary>Hüft-Fadenkreuz beim Aufgehen (Dauerfeuer, Laufen): je Bild ein neues Raster, ohne Speicher (Textur und Pixel bleiben).</summary>
        [Test]
        public void Fadenkreuz_Aufgehen_ohne_Speicher()
        {
            var b = Object.FindAnyObjectByType<Bootstrap>();
            foreach (var L in b.Player.loadouts)
            {
                var hip = L.hip;
                if (hip.H.prims == null || hip.H.prims.Length == 0) continue;
                hip.Mask(720);
                hip.Kick();
                hip.Mask(720);
                NUnit.Framework.Assert.That(() => { for (int k = 0; k < 20; k++) { hip.Decay(Dt, 1f); hip.Kick(); hip.Mask(720); } },
                    Is.Not.AllocatingGCMemory(), hip.H.kind);
            }
        }
    }
}
