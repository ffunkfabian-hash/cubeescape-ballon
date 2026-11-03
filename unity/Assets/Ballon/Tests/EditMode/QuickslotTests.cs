// EditMode (0.42 „Quickslot“): Waffenübersicht nach Kategorien, Leiste 1–9 und Standard-Skins aus ego.json › hud (basic/loadout.py) –
// Zuordnung aus den Daten (keine Waffen-IDs im Test), Leiste belegen/tauschen/speichern, Tastatur- und Mausweg der Übersicht.
using System.IO;
using System.Linq;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace Ballon.Ego.Tests
{
    public class QuickslotTests
    {
        const string Gen = "Assets/Ballon/Generated";
        static EgoFile[] _all;
        static EgoFile[] All => _all ?? (_all = EgoFile.ParseAll(File.ReadAllText($"{Gen}/ego.json")));
        static string Type(EgoFile d) => d.profile.type;

        [Test]
        public void Kategorien_aus_den_Daten()
        {
            var hud = All[0].hud;
            Assert.IsNotNull(hud, $"ego.json {All[0].format} ohne hud (erst {EgoFile.Format})");
            Assert.That(All.All(d => ReferenceEquals(d.hud, hud)), "hud gemeinsam für alle Waffen");
            var L = new HudLayout(All);
            CollectionAssert.AreEqual(hud.categories.Select(c => c.id).Where(id => L.categories.Any(k => k.id == id)).ToArray(),
                                      L.categories.Select(c => c.id).ToArray(), "Kategorien in der Reihenfolge der Daten, leere entfallen");
            Assert.That(L.categories.All(c => c.id != "other"), "jede Klasse hat eine Kategorie");
            var seen = L.categories.SelectMany(c => c.weapons).ToArray();
            CollectionAssert.AreEquivalent(Enumerable.Range(0, All.Length).ToArray(), seen, "jede Waffe genau einmal");
            for (int c = 0; c < L.categories.Length; c++)
            {
                var data = hud.categories.Single(k => k.id == L.categories[c].id);
                var order = L.categories[c].weapons.Select(w => System.Array.IndexOf(data.classes, Type(All[w]))).ToArray();
                Assert.That(order.All(i => i >= 0), $"{data.id}: nur Klassen der Kategorie");
                CollectionAssert.IsOrdered(order, $"{data.id}: Klassen in der Reihenfolge der Daten");
                foreach (int w in L.categories[c].weapons) Assert.AreEqual(c, L.categoryOf[w]);
            }
            foreach (var v in Enumerable.Range(0, All.Length).Where(i => All[i].IsVariant))   // Variante direkt hinter ihrem Grundtyp
            {
                var col = L.categories[L.categoryOf[v]].weapons;
                int at = System.Array.IndexOf(col, v);
                Assert.Greater(at, 0);
                var prev = All[col[at - 1]];
                Assert.That(prev.weapon.id == All[v].origin.base_id || (prev.IsVariant && prev.origin.base_id == All[v].origin.base_id),
                            $"{All[v].weapon.id} unter {All[v].origin.base_id}");
                StringAssert.Contains(All[v].weapon.id, L.Subtitle(v), "Varianten-Kennung");
            }
            Assert.GreaterOrEqual(L.columns.Length, 3, "Primär | Spezial | Schwer + Werkzeug (lange Spalten geteilt)");
            Assert.AreEqual(L.categories[0].weapons[0], L.columns[0][0], "erste Spalte beginnt mit Primär");
            Assert.That(L.columns.All(c => c.Length <= HudLayout.MaxRows));
            var tools = L.categories.Where((c, i) => i >= 3).SelectMany(c => c.weapons);
            int heavyCol = System.Array.FindIndex(L.columns, c => c.Contains(L.categories[2].weapons[0]));
            Assert.That(tools.All(w => L.columns.Skip(heavyCol).Any(c => c.Contains(w))), "Werkzeug unter Schwer");
            TestContext.WriteLine(string.Join(" | ", L.categories.Select(c => $"{c.de}: " + string.Join(", ", c.weapons.Select(w => All[w].weapon.type_de + (All[w].IsVariant ? " " + All[w].weapon.id : ""))))));
        }

        [Test]
        public void Altes_Format_11_ohne_hud_eine_Kategorie()
        {
            var old = EgoFile.ParseAll(File.ReadAllText($"{Gen}/ego.json").Replace($"\"{EgoFile.Format}\"", $"\"{EgoFile.Format11}\""));
            Assert.IsNull(old[0].hud, "/11: hud wird nicht gelesen");
            var L = new HudLayout(old);
            Assert.AreEqual(1, L.categories.Length);
            Assert.AreEqual("Waffen", L.categories[0].de);
            CollectionAssert.AreEqual(Enumerable.Range(0, 9).ToArray(), L.DefaultSlots(), "Leiste wie bis 0.41: Waffen 1–9");
            Assert.AreEqual("standard", L.DefaultSkin(0), "ohne Daten: Standard");
            Assert.That(L.columns.All(c => c.Length <= HudLayout.MaxRows), "lange Spalte geteilt");
        }

        [Test]
        public void Standardleiste_aus_Klassen()
        {
            var L = new HudLayout(All);
            var s = L.DefaultSlots();
            Assert.AreEqual(9, s.Length);
            for (int k = 0; k < 9; k++)
            {
                Assert.GreaterOrEqual(s[k], 0, $"Platz {k + 1}: Klasse {All[0].hud.hotbar[k]} vorhanden");
                Assert.AreEqual(All[0].hud.hotbar[k], Type(All[s[k]]), $"Platz {k + 1}");
                Assert.IsFalse(All[s[k]].IsVariant, $"Platz {k + 1}: BALLONs Waffe vor Varianten");
            }
            Assert.AreEqual(9, s.Distinct().Count(), "jede Waffe einmal");
        }

        [Test]
        public void Standard_Skin_farbig_statt_standard()
        {
            var L = new HudLayout(All);
            for (int i = 0; i < All.Length; i++)
            {
                var d = All[i];
                string sk = L.DefaultSkin(i);
                int k = L.SkinIndex(i, sk);
                Assert.GreaterOrEqual(k, 0, $"{d.weapon.id}: Skin {sk} gebacken");
                if (d.IsVariant)
                {
                    Assert.AreEqual(0, k, $"{d.weapon.id}: Skin der Linie (einziger Atlas)");
                    Assert.AreEqual(d.textures.skins[0].de.Split(new[] { ": " }, System.StringSplitOptions.None).Last(), L.SkinLabel(i, 0));
                    StringAssert.Contains(d.origin.skin.Substring(0, 3), L.SkinLabel(i, 0).ToLowerInvariant().Replace("ü", "ue"), "Linie laut Herkunft");
                    continue;
                }
                Assert.AreNotEqual("standard", sk, $"{d.weapon.id}: farbiger Standard statt Cremeweiß");
                Assert.That(sk != "polar" && sk != "gebraucht", $"{d.weapon.id}: {sk} ist hell/creme");
                Assert.Greater(d.textures.skins.Length, 2, $"{d.weapon.id}: K schaltet durch mehrere Skins");
            }
            foreach (var col in L.columns)                           // Nachbarn in der Übersicht unterscheidbar
                for (int r = 1; r < col.Length; r++)
                    Assert.AreNotEqual(L.SkinLook(col[r - 1]), L.SkinLook(col[r]), $"{All[col[r - 1]].weapon.id} / {All[col[r]].weapon.id}");
            var s = L.DefaultSlots();
            for (int k = 1; k < s.Length; k++)
                Assert.AreNotEqual(L.SkinLook(s[k - 1]), L.SkinLook(s[k]), $"Leiste {k} / {k + 1}");
        }

        [Test]
        public void Leiste_belegen_und_tauschen()
        {
            var b = new Hotbar(new[] { 0, 1, 2, 3, 4, 5, 6, 7, -1 });
            Assert.AreEqual(0, b.WeaponAt(1));
            Assert.AreEqual(-1, b.WeaponAt(9), "leerer Platz");
            Assert.AreEqual(-1, b.WeaponAt(0));
            int v = b.Version;
            b.Assign(8, 12);                                         // neue Waffe auf den leeren Platz
            Assert.AreEqual(12, b.slots[8]);
            Assert.Greater(b.Version, v);
            b.Assign(0, 3);                                          // Waffe von Platz 4 auf Platz 1: tauschen
            CollectionAssert.AreEqual(new[] { 3, 1, 2, 0, 4, 5, 6, 7, 12 }, b.slots);
            b.Assign(1, 15);                                         // neue Waffe ersetzt
            Assert.AreEqual(15, b.slots[1]);
            Assert.AreEqual(-1, b.SlotOf(1));
            v = b.Version;
            b.Assign(1, 15);
            Assert.AreEqual(v, b.Version, "gleicher Platz: keine Änderung");
            b.Assign(9, 2);
            b.Assign(-1, 2);
            Assert.AreEqual(v, b.Version, "ungültiger Platz");
        }

        [Test]
        public void Leiste_und_Skins_speichern_und_laden()
        {
            var L = new HudLayout(All);
            var path = Path.Combine(Path.GetTempPath(), $"ballon_loadout_{System.Guid.NewGuid():N}.json");
            try
            {
                var st = new LoadoutStore(path);
                Assert.IsFalse(st.Load(L, All.Length, out _, out _), "ohne Datei: Standard");
                var bar = new Hotbar(L.DefaultSlots());
                bar.Assign(8, All.Length - 1);
                var skins = new string[All.Length];
                skins[0] = "polar";
                st.Save(L, bar, skins);
                var text = File.ReadAllText(path);
                StringAssert.Contains(LoadoutStore.Format, text, "Format mit Version");
                StringAssert.Contains(All[All.Length - 1].weapon.id, text, "Waffe mit ID gespeichert");
                Assert.IsTrue(st.Load(L, All.Length, out var slots, out var sk));
                CollectionAssert.AreEqual(bar.slots, slots);
                Assert.AreEqual("polar", sk[0]);
                Assert.IsNull(sk[1], "nicht gewählt: Standard-Skin der Klasse");
                // unbekannte Waffe und doppelter Platz (von Hand bearbeitet)
                File.WriteAllText(path, text.Replace($"\"{All[1].weapon.id}\"", "\"BASIC-99\"").Replace($"\"{All[L.DefaultSlots()[2]].weapon.id}\"", $"\"{All[0].weapon.id}\""));
                Assert.IsTrue(st.Load(L, All.Length, out slots, out _));
                Assert.AreEqual(0, slots[0]);
                Assert.AreEqual(-1, slots[2], "doppelt: nur der erste Platz zählt");
                File.WriteAllText(path, "{\"format\": \"ballon-loadout/0\", \"slots\": []}");
                LogAssert.Expect(LogType.Warning, new System.Text.RegularExpressions.Regex("Format ballon-loadout/0"));
                Assert.IsFalse(st.Load(L, All.Length, out _, out _), "falsches Format: Standard");
                File.WriteAllText(path, "kein json");
                LogAssert.Expect(LogType.Warning, new System.Text.RegularExpressions.Regex("unlesbar|Format"));
                Assert.IsFalse(st.Load(L, All.Length, out _, out _), "kaputte Datei: Standard");
            }
            finally { File.Delete(path); }
        }

        [Test]
        public void Uebersicht_Tastatur_und_Maus()
        {
            var L = new HudLayout(All);
            var M = new EgoMenu(L.columns, L.Order());
            Assert.AreEqual(All.Length, M.count);
            int first = L.columns[0][0];
            M.Step(new MenuInput { toggle = true }, first);
            Assert.AreEqual(first, M.Index, "öffnet bei der aktiven Waffe");
            M.Step(new MenuInput { arrows = new Vector2Int(1, 0) }, first);
            Assert.AreEqual(L.columns[1][0], M.Index, "rechts: Spezial");
            M.Step(new MenuInput { arrows = new Vector2Int(1, 0) }, first);
            M.Step(new MenuInput { arrows = new Vector2Int(0, 1) }, first);
            Assert.AreEqual(L.columns[2][1], M.Index, "Schwer, zweite Zeile");
            M.Step(new MenuInput { arrows = new Vector2Int(-1, 0) }, first);
            Assert.AreEqual(L.columns[1][1], M.Index, "links: Zeile bleibt");
            M.Step(new MenuInput { arrows = new Vector2Int(0, -1) }, first);
            M.Step(new MenuInput { arrows = new Vector2Int(0, -1) }, first);
            Assert.AreEqual(L.columns[1][L.columns[1].Length - 1], M.Index, "oben umlaufen");
            int last0 = L.columns[0][L.columns[0].Length - 1];
            M.Step(new MenuInput { arrows = new Vector2Int(-1, 0) }, first);
            Assert.AreEqual(L.columns[0][Mathf.Min(L.columns[1].Length - 1, L.columns[0].Length - 1)], M.Index);
            // Mausrad: Lesereihenfolge Spalte für Spalte
            var order = L.Order();
            int at = System.Array.IndexOf(order, M.Index);
            M.Step(new MenuInput { wheel = 1 }, first);
            Assert.AreEqual(order[(at + 1) % order.Length], M.Index);
            // Zahl: markierte Waffe auf den Platz, Menü bleibt offen
            int marked = M.Index;
            Assert.AreEqual(0, M.Step(new MenuInput { digit = 4 }, first));
            Assert.AreEqual(3, M.AssignSlot);
            Assert.AreEqual(marked, M.AssignWeapon);
            Assert.IsTrue(M.IsOpen);
            M.Step(new MenuInput(), first);
            Assert.AreEqual(-1, M.AssignSlot, "nur im Bild der Taste");
            // Ziehen: drücken auf einer Waffe, loslassen über Platz 7
            M.Step(new MenuInput { press = last0 + 1 }, first);
            Assert.AreEqual(last0, M.Dragging);
            M.Step(new MenuInput { moved = true, hover = first + 1 }, first);
            Assert.AreEqual(last0, M.Dragging, "Ziehen läuft weiter");
            M.Step(new MenuInput { release = -1, releaseSlot = 7 }, first);
            Assert.AreEqual(6, M.AssignSlot);
            Assert.AreEqual(last0, M.AssignWeapon);
            Assert.AreEqual(-1, M.Dragging);
            // daneben losgelassen: nichts
            M.Step(new MenuInput { press = first + 1 }, first);
            Assert.AreEqual(0, M.Step(new MenuInput { release = -1 }, first));
            Assert.AreEqual(-1, M.AssignSlot);
            Assert.IsTrue(M.IsOpen);
            // Klick: drücken und auf derselben Waffe loslassen – ausrüsten
            M.Step(new MenuInput { press = last0 + 1 }, first);
            Assert.AreEqual(last0 + 1, M.Step(new MenuInput { release = last0 + 1 }, first));
            Assert.IsFalse(M.IsOpen);
            // Enter wählt die markierte
            M.Step(new MenuInput { toggle = true }, first);
            Assert.AreEqual(first + 1, M.Step(new MenuInput { confirm = true }, first));
        }
    }
}
