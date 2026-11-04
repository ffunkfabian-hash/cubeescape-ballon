// PlayMode (0.43 „Kiln“): lokale Design-Serien im Spieler – Bootstrap hängt sie aus SeriesAssets an, jede Serie zieht mit ihrem eigenen Atlas. Ohne lokale Serien: übersprungen.
using System.Collections;
using System.Linq;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace Ballon.Ego.Tests
{
    public class SeriesPlayTests
    {
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

        [UnityTest]
        public IEnumerator Serienwaffen_ziehen_mit_eigenem_Atlas()
        {
            var b = Object.FindAnyObjectByType<Bootstrap>();
            var all = b.Solvers.Select(s => s.D).ToArray();
            var series = Enumerable.Range(0, all.Length).Where(i => !string.IsNullOrEmpty(all[i].origin?.series)).ToArray();
            if (series.Length == 0) Assert.Ignore("keine lokalen Serien (python3 tools/unity_run.py setup)");
            Assert.AreEqual(all.Length, b.Player.loadouts.Length, "alle Waffen im Spieler");
            var p = b.Player;
            foreach (var i in series.GroupBy(k => all[k].origin.series).Select(g => g.First()))
            {
                p.UseWeapon(i);
                p.C.ReadyNow();
                yield return null;
                Assert.AreEqual(i, p.arsenal.Active, all[i].weapon.id);
                Assert.IsTrue(p.loadouts[i].rig.space.gameObject.activeInHierarchy, $"{all[i].weapon.id} sichtbar");
                var mats = p.loadouts[i].rig.space.GetComponentsInChildren<Renderer>(true).SelectMany(r => r.sharedMaterials).Where(m => m != null).Select(m => m.name).ToArray();
                Assert.That(mats.Any(n => n.StartsWith($"Atlas_formgen_{all[i].weapon.id}")), $"{all[i].weapon.id}: eigener Atlas ({string.Join(", ", mats.Distinct().Take(6))})");
                Assert.IsNotNull(p.loadouts[i].icon, $"{all[i].weapon.id}: Symbol");
            }
            p.UseWeapon(0);
        }
    }
}
