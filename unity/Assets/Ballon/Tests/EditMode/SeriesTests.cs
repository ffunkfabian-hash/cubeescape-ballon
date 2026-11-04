// EditMode (0.43 „Kiln“): Design-Serien aus Formgen v2 sind lokal (tools/series_packages.py, gitignoriert). Ohne sie bleibt alles wie vorher; mit ihnen
// stehen sie hinter den festen Waffen, unter ihrem Grundtyp und mit Serienkennung. Die Szene im Repo kennt sie nicht.
using System.IO;
using System.Linq;
using Ballon.Ego.Editor;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace Ballon.Ego.Tests
{
    public class SeriesTests
    {
        static EgoFile[] Own => EgoFile.ParseAll(File.ReadAllText($"{BallonSetup.Gen}/ego.json"));

        static EgoFile[] Merged()
        {
            if (!File.Exists(BallonSetup.SeriesJson)) Assert.Ignore("keine lokalen Serien (python3 tools/unity_run.py setup)");
            return EgoFile.ParseAll(File.ReadAllText(BallonSetup.SeriesJson));
        }

        [Test]
        public void Serien_stehen_hinter_den_festen_Waffen()
        {
            var own = Own;
            var all = Merged();
            Assert.Greater(all.Length, own.Length, "Serien fehlen in ego_series.json");
            CollectionAssert.AreEqual(own.Select(d => d.weapon.id).ToArray(), all.Take(own.Length).Select(d => d.weapon.id).ToArray(), "Tasten und Leiste bleiben");
            foreach (var d in all.Skip(own.Length))
            {
                Assert.That(BallonSetup.IsSeries(d), d.weapon.id);
                Assert.That("JKLM".Contains(d.origin.series), $"{d.weapon.id}: Serie {d.origin.series}");
                Assert.AreEqual($"B{d.origin.series}", d.weapon.id.Substring(0, 2), "Kennung wie das Blatt");
                Assert.That(!string.IsNullOrEmpty(d.origin.series_name), d.weapon.id);
                Assert.That(File.Exists($"{BallonSetup.Gen}/{d.AssetPath(d.weapon.fbx)}"), $"{d.weapon.id}: FBX");
                foreach (var f in new[] { d.textures.weapon.albedo, d.textures.weapon.spec, d.textures.weapon.normal, d.textures.weapon.ao })
                    Assert.That(File.Exists($"{BallonSetup.Gen}/{d.TexturePath(f)}"), $"{d.weapon.id}: {f}");
                Assert.AreEqual(1, d.textures.skins.Length, $"{d.weapon.id}: nur der Skin der Linie");
            }
        }

        [Test]
        public void Uebersicht_unter_dem_Grundtyp_mit_Kennung()
        {
            var all = Merged();
            var L = new HudLayout(all);
            CollectionAssert.AreEquivalent(Enumerable.Range(0, all.Length).ToArray(), L.Order(), "jede Waffe genau einmal");
            Assert.That(L.columns.All(c => c.Sum(L.RowUnits) <= HudLayout.MaxRows), "Spalten passen in die Höhe");
            for (int i = 0; i < all.Length; i++)
                if (!string.IsNullOrEmpty(all[i].origin?.series))
                    StringAssert.StartsWith($"Serie {all[i].origin.series} · ", L.Subtitle(i));
            var order = L.Order();
            for (int k = 1; k < order.Length; k++)
                if (all[order[k]].IsVariant)
                {
                    var prev = all[order[k - 1]];
                    Assert.That(prev.weapon.id == all[order[k]].origin.base_id || (prev.IsVariant && prev.origin.base_id == all[order[k]].origin.base_id),
                                $"{all[order[k]].weapon.id} unter seinem Grundtyp");
                }
            Assert.LessOrEqual(L.columns.Length, 8, "Spalten lesbar breit bei 1470 × 956");
        }

        [Test]
        public void Lokales_Asset_passt_und_Szene_kennt_die_Serien_nicht()
        {
            var all = Merged();
            var own = Own;
            var s = AssetDatabase.LoadAssetAtPath<SeriesAssets>(BallonSetup.SeriesAsset);
            Assert.IsNotNull(s, "SeriesAssets fehlt: python3 tools/unity_run.py setup");
            CollectionAssert.AreEqual(all.Skip(own.Length).Select(d => d.weapon.id).ToArray(), s.weapons.Select(w => w.id).ToArray());
            Assert.That(s.weapons.All(w => w.model != null && w.skins.Length == 1 && w.skins[0] != null && w.icon != null), "Modell, Material, Symbol");
            var scene = File.ReadAllText(BallonSetup.ScenePath);
            Assert.That(!scene.Contains("id: BJ") && !scene.Contains("id: BK") && !scene.Contains("id: BL") && !scene.Contains("id: BM"), "Szene im Repo ohne Serien");
        }
    }
}
