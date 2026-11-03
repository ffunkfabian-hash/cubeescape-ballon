// PlayMode (0.42 „Quickslot“): Leiste 1–9 und Waffenübersicht in der Szene – Taste wechselt zur Waffe des Platzes (Wechsel wie seit 0.18),
// Übersicht mit Zahl (Tastatur-Weg) oder Ziehen (Maus/Trackpad) belegt Plätze, Standard-Skins beim Start, Leiste und Skin bleiben über einen
// Neustart (LoadoutStore), kein GC-Speicher beim Wechsel über die Leiste und in der offenen Übersicht.
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
using UnityEngine.TestTools.Constraints;
using Is = UnityEngine.TestTools.Constraints.Is;

namespace Ballon.Ego.Tests
{
    public class QuickslotPlayTests
    {
        const float Dt = 1f / 60f;

        /// <summary>Maus/Trackpad als Ablauf: je Bild Zeigerlage und Taste (für das Ziehen auf die Leiste).</summary>
        sealed class PointerInput : IEgoInput
        {
            public readonly Queue<(Vector2 p, bool down, bool up, bool tab)> steps = new Queue<(Vector2, bool, bool, bool)>();
            public RawInput Read(float dt, float zoom)
            {
                var r = new RawInput();
                if (steps.Count == 0) return r;
                var (p, down, up, tab) = steps.Dequeue();
                r.menu.pointer = p;
                r.menu.moved = true;
                r.menu.down = down;
                r.menu.up = up;
                r.menu.toggle = tab;
                return r;
            }
        }

        [UnitySetUp]
        public IEnumerator LoadScene()
        {
            if (Object.FindAnyObjectByType<Bootstrap>() == null)
            {
                SceneManager.LoadScene("Firstfeel");
                yield return null;
                yield return null;
            }
            var p = Object.FindAnyObjectByType<Bootstrap>().Player;
            p.InitLoadout(null);                                     // Standardleiste und Standard-Skins, nichts speichern
            p.menu.Close();
            p.UseWeapon(0);
            foreach (var c in p.arsenal.C) { c.ReadyNow(); c.ammo = c.magSize; }
        }

        [TearDown]
        public void Zuruecksetzen()
        {
            var b = Object.FindAnyObjectByType<Bootstrap>();
            if (b == null || b.Player == null) return;
            b.Player.deltaOverride = null;
            b.Player.input = new ScriptedInput().Add(0, 1000);
            b.Player.menu.Close();
            b.Player.InitLoadout(null);
        }

        static void Steps(EgoPlayer p, float seconds)
        {
            for (float t = 0; t < seconds; t += Dt) p.Step(Dt);
        }

        [UnityTest]
        public IEnumerator Leiste_Taste_waehlt_die_Waffe_des_Platzes()
        {
            var p = Object.FindAnyObjectByType<Bootstrap>().Player;
            Assert.IsNull(Bootstrap.Store(new[] { "BALLON", "-ballonCapture", "x" }), "Aufnahmen und Messungen speichern nichts");
            Assert.AreEqual("x.json", Bootstrap.Store(new[] { "BALLON", "-ballonLoadout", "x.json" })?.path, "eigene Datei");
            var bar = p.hotbar;
            CollectionAssert.AreEqual(p.layout.DefaultSlots(), bar.slots, "Standardleiste");
            foreach (int key in new[] { 3, 5, 9, 1 })
            {
                var seq = new List<string>();
                p.input = new ScriptedInput().Add(0, 0.02f, press: $"slot{key}").Add(0.02f, 3f);
                for (float t = 0; t < 3f; t += Dt)
                {
                    p.Step(Dt);
                    var s = $"{p.arsenal.Active}:{p.C.ActionName}";
                    if (seq.Count == 0 || seq[seq.Count - 1] != s) seq.Add(s);
                    if (!p.arsenal.Switching && !p.C.Busy && p.arsenal.Active == bar.WeaponAt(key) && t > 0.1f) break;
                }
                Assert.AreEqual(bar.WeaponAt(key), p.arsenal.Active, $"Taste {key}: {string.Join(" ", seq)}");
                if (key != 1) Assert.That(seq.Any(x => x.EndsWith(":draw")), $"Taste {key}: Ziehen wie beim Wechsel ({string.Join(" ", seq)})");
            }
            yield return null;
        }

        [UnityTest]
        public IEnumerator Uebersicht_Zahl_legt_Waffe_auf_Platz()
        {
            var p = Object.FindAnyObjectByType<Bootstrap>().Player;
            var L = p.layout;
            int want = L.columns[2][1];                                  // Schwer, zweite Zeile (Pfeile rechts, rechts, runter)
            p.input = new ScriptedInput()
                .Add(0.0f, 0.02f, press: "menu").Add(0.1f, 0.12f, press: "menu_right").Add(0.2f, 0.22f, press: "menu_right")
                .Add(0.3f, 0.32f, press: "menu_down").Add(0.4f, 0.42f, press: "slot9").Add(0.5f, 0.52f, press: "menu_esc")
                .Add(0.6f, 0.62f, press: "slot9").Add(0.62f, 4f);
            Steps(p, 0.45f);
            Assert.IsTrue(p.menu.IsOpen, "Zahl schließt die Übersicht nicht");
            Assert.AreEqual(want, p.hotbar.slots[8], "Platz 9 belegt");
            Assert.AreEqual(0, p.arsenal.Active, "Zahl in der Übersicht wechselt nicht");
            Steps(p, 0.1f);
            Assert.IsFalse(p.menu.IsOpen);
            for (float t = 0; t < 3.4f && !(p.arsenal.Active == want && !p.arsenal.Switching && !p.C.Busy); t += Dt) p.Step(Dt);
            Assert.AreEqual(want, p.arsenal.Active, "Taste 9: neue Waffe");
            yield return null;
        }

        [UnityTest]
        public IEnumerator Uebersicht_Ziehen_auf_die_Leiste()
        {
            var p = Object.FindAnyObjectByType<Bootstrap>().Player;
            var L = p.layout;
            int w = L.columns[1][L.columns[1].Length - 1];
            int before = p.hotbar.slots[2];
            var inp = new PointerInput();
            Vector2 cell = p.MenuCellRect(w).center, slot = p.SlotRect(2).center;
            inp.steps.Enqueue((cell, false, false, true));                // Tab
            inp.steps.Enqueue((cell, true, false, false));                // drücken auf der Waffe
            for (int k = 1; k <= 4; k++) inp.steps.Enqueue((Vector2.Lerp(cell, slot, k / 4f), false, false, false));
            inp.steps.Enqueue((slot, false, true, false));                // loslassen über Platz 3
            p.input = inp;
            p.Step(Dt);
            Assert.IsTrue(p.menu.IsOpen);
            p.Step(Dt);
            Assert.AreEqual(w, p.menu.Dragging);
            for (int k = 0; k < 5; k++) p.Step(Dt);
            Assert.AreEqual(w, p.hotbar.slots[2], "gezogen auf Platz 3");
            Assert.AreEqual(1, p.hotbar.slots.Count(x => x == w), "Waffe einmal auf der Leiste");
            Assert.That(p.hotbar.SlotOf(before) != 2, "bisherige Waffe von Platz 3 verdrängt bzw. getauscht");
            Assert.AreEqual(-1, p.menu.Dragging);
            Assert.IsTrue(p.menu.IsOpen, "Übersicht bleibt offen");
            // Klick auf eine Waffe rüstet aus
            int w2 = L.columns[0][1];
            Vector2 c2 = p.MenuCellRect(w2).center;
            inp.steps.Enqueue((c2, true, false, false));
            inp.steps.Enqueue((c2, false, true, false));
            p.Step(Dt);
            p.Step(Dt);
            Assert.IsFalse(p.menu.IsOpen, "Klick wählt und schließt");
            for (float t = 0; t < 3f && !(p.arsenal.Active == w2 && !p.arsenal.Switching && !p.C.Busy); t += Dt) p.Step(Dt);
            Assert.AreEqual(w2, p.arsenal.Active);
            yield return null;
        }

        [UnityTest]
        public IEnumerator Standard_Skins_beim_Start()
        {
            var b = Object.FindAnyObjectByType<Bootstrap>();
            var p = b.Player;
            for (int k = 0; k < p.loadouts.Length; k++)
            {
                var L = p.loadouts[k];
                var d = b.Solvers[k].D;
                Assert.AreEqual(p.layout.DefaultSkin(k), p.layout.SkinName(k, L.skin), $"{d.weapon.id}: Standard-Skin der Klasse");
                Assert.AreSame(L.skins[L.skin], L.rig.WeaponAtlasMaterial, $"{d.weapon.id}: Material trägt ihn");
                if (!d.IsVariant) Assert.AreNotEqual(0, L.skin, $"{d.weapon.id}: nicht Cremeweiß (standard)");
            }
            yield return null;
        }

        [UnityTest]
        public IEnumerator Leiste_und_Skin_bleiben_ueber_Neustart()
        {
            var p = Object.FindAnyObjectByType<Bootstrap>().Player;
            var path = Path.Combine(Application.temporaryCachePath, $"loadout_test_{System.Guid.NewGuid():N}.json");
            try
            {
                p.InitLoadout(new LoadoutStore(path));
                Assert.IsFalse(File.Exists(path), "ohne Änderung keine Datei");
                int skin0 = p.loadouts[0].skin;
                p.SetSkin(skin0 + 1);                                   // K
                int last = p.loadouts.Length - 1;
                p.input = new ScriptedInput().Add(0, 0.02f, press: "menu").Add(0.02f, 0.04f, press: "slot2").Add(0.06f, 0.08f, press: "menu_esc");
                p.menu.Close();
                p.Step(Dt);                                             // öffnet bei Waffe 1
                p.Step(Dt);                                             // Waffe 1 auf Platz 2 (tauscht mit Platz 1)
                p.Step(Dt);
                p.Step(Dt);
                Assert.IsTrue(File.Exists(path), "gespeichert");
                var slots = p.hotbar.slots.ToArray();
                Assert.AreEqual(0, slots[1], "Waffe 1 auf Platz 2");
                p.InitLoadout(null);                                    // „Neustart“ ohne Speicher: Standard
                Assert.AreEqual(skin0, p.loadouts[0].skin);
                p.InitLoadout(new LoadoutStore(path));                  // Neustart mit Datei
                CollectionAssert.AreEqual(slots, p.hotbar.slots, "Leiste wie gespeichert");
                Assert.AreEqual((skin0 + 1) % p.loadouts[0].skins.Length, p.loadouts[0].skin, "Skin wie gewählt");
                Assert.AreEqual(p.layout.SkinIndex(last, p.layout.DefaultSkin(last)), p.loadouts[last].skin, "ungewählt: Standard-Skin");
            }
            finally
            {
                File.Delete(path);
                p.InitLoadout(null);
            }
            yield return null;
        }

        /// <summary>Bei einem Fehlschlag: noch ein Lauf, je Schritt die GC.Alloc-Proben (wie SteadyframePlayTests.Where).</summary>
        static void Where(EgoPlayer p, ScriptedInput s, int steps)
        {
            p.UseWeapon(0);
            p.UpdateHudText();
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
            int shown = 0;
            for (int i = 0; i < steps; i++)
            {
                int a = Count(() => p.Step(Dt)), h = Count(p.UpdateHudText);
                if (a + h > 0 && shown++ < 25)
                    TestContext.WriteLine($"Schritt {i} ({i * Dt:0.00} s): Waffe {p.arsenal.Active + 1} {p.C.ActionName} {p.C.Frame:0.0} " +
                                          $"Übersicht {(p.menu.IsOpen ? "offen" : "zu")} – Step {a}, Anzeige {h} Proben");
            }
            TestContext.WriteLine($"{shown} Schritte mit Speicher");
        }

        [UnityTest]
        public IEnumerator Kein_GC_Speicher_bei_Leiste_und_Uebersicht()
        {
            var p = Object.FindAnyObjectByType<Bootstrap>().Player;
            ScriptedInput Run()
            {
                var s = new ScriptedInput();
                float t = 0;
                foreach (int k in new[] { 2, 3, 4, 6, 7, 8, 9, 5, 1 }) { s.Add(t, t + 0.02f, press: $"slot{k}"); t += 2f; }
                s.Add(t, t + 0.02f, press: "menu"); t += 0.2f;
                foreach (var a in new[] { "menu_right", "menu_down", "menu_down", "menu_left", "menu_next", "menu_up", "menu_prev" })
                { s.Add(t, t + 0.02f, press: a); t += 0.1f; }
                s.Add(t, t + 0.02f, press: "menu_esc"); t += 0.3f;
                s.Add(t, t + 0.5f);
                return s;
            }
            var warm = Run();
            int steps = Mathf.CeilToInt(warm.Duration / Dt);
            p.input = warm;
            for (int i = 0; i < steps; i++) { p.Step(Dt); p.UpdateHudText(); }
            p.UseWeapon(0);
            p.input = Run();
            for (int i = 0; i < steps; i++) { p.Step(Dt); p.UpdateHudText(); }
            p.UseWeapon(0);
            p.UpdateHudText();                                           // UseWeapon baut die Trefferzeile neu (gewollt) – nicht mitmessen
            p.input = Run();
            try
            {
                Assert.That(() => { for (int i = 0; i < steps; i++) { p.Step(Dt); p.UpdateHudText(); } }, Is.Not.AllocatingGCMemory(),
                            "Wechsel über die Leiste, Übersicht öffnen, bewegen, schließen");
            }
            catch (AssertionException)
            {
                Where(p, Run(), steps);                                  // Fundstellen: Schritte mit Speicher
                throw;
            }
            Assert.AreEqual(0, p.arsenal.Active, "Ablauf endet bei Platz 1");
            yield return null;
        }
    }
}
