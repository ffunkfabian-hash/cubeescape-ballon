// EditMode (0.37 „Steadyframe“): Hüft-Fadenkreuz und Absehen werden nur noch im Rahmen der Formteile gerastert. Gleich (Deckung ± 1/255) mit dem
// bisherigen Weg (volles Quadrat) für jede Waffe, Hüfte und Glas, bei Spreizung Basis/Mitte/Höchstwert und drei Bildhöhen; und schnell
// genug fürs Aufgehen in jedem Bild. Gegenprobe: BALLON_STEADYFRAME_OFF=1 – dann rastert Mask den alten Weg und der Zeittest scheitert.
using System.Diagnostics;
using System.IO;
using NUnit.Framework;

namespace Ballon.Ego.Tests
{
    public class SteadyframeTests
    {
        const string Gen = "Assets/Ballon/Generated";
        static EgoFile[] _all;
        static EgoFile[] All => _all ?? (_all = EgoFile.ParseAll(File.ReadAllText($"{Gen}/ego.json")));

        static System.Collections.Generic.IEnumerable<(string name, EgoHip hip)> Forms()
        {
            foreach (var d in All)
            {
                if (d.gameplay.hip?.prims != null && d.gameplay.hip.prims.Length > 0) yield return ($"{d.weapon.id} Hüfte", d.gameplay.hip);
                var s = d.gameplay.SightHip;
                if (s?.prims != null && s.prims.Length > 0) yield return ($"{d.weapon.id} Glas", s);
            }
        }

        [Test]
        public void Fadenkreuz_Raster_gleich_dem_vollen_Quadrat()
        {
            int forms = 0, pixels = 0, lsb = 0;
            foreach (var (name, hip) in Forms())
            {
                forms++;
                var R = new HipReticle(hip);
                try
                {
                    foreach (float h in new[] { 720f, 1080f, 1664f })
                        foreach (float f in new[] { 0f, 0.5f, 1f })
                        {
                            R.spread = UnityEngine.Mathf.Lerp(hip.spread.@base, hip.spread.max, f);
                            var fast = R.MaskPixels(h, false);
                            var slow = R.MaskPixels(h, true);
                            Assert.AreEqual(slow.Length, fast.Length, name);
                            for (int i = 0; i < fast.Length; i++)
                            {
                                int da = System.Math.Abs(fast[i].a - slow[i].a);
                                if (da > 1 || fast[i].r != slow[i].r)
                                    Assert.Fail($"{name}, Höhe {h}, Spreizung {R.spread:0.00} mm: Pixel {i} Deckung {fast[i].a} statt {slow[i].a}");
                                if (da == 1) lsb++;
                            }
                            pixels += fast.Length;
                        }
                }
                finally { R.Release(); }                    // Texturen auch nach einem Fehlschlag freigeben
            }
            TestContext.WriteLine($"{forms} Formen, {pixels} Pixel gleich, davon {lsb} um 1/255 gerundet (Gleitkomma-Reihenfolge)");
            Assert.Greater(forms, 10);
        }

        /// <summary>Aufgehen in jedem Bild (Dauerfeuer, Laufen): je neue Spreizung ein Raster. Bis 0.36 kostete das größte Fadenkreuz
        /// 13–21 ms je Bild im Spieler (Profiler, Lauf vorher_b); Grenze hier 2 ms je Raster im Editor bei 1080 px.</summary>
        [Test]
        public void Fadenkreuz_Aufgehen_je_Bild_unter_2_ms()
        {
            string worst = "";
            double worstMs = 0;
            foreach (var (name, hip) in Forms())
            {
                var R = new HipReticle(hip);
                R.Mask(1080);
                const int n = 30;
                var sw = Stopwatch.StartNew();
                for (int i = 0; i < n; i++)
                {
                    R.spread = UnityEngine.Mathf.Lerp(hip.spread.@base, hip.spread.max, (i + 1) / (float)n);
                    R.Mask(1080);
                }
                double ms = sw.Elapsed.TotalMilliseconds / n;
                R.Release();
                if (ms > worstMs) { worstMs = ms; worst = name; }
            }
            TestContext.WriteLine($"teuerstes Raster: {worst} {worstMs:0.000} ms");
            Assert.Less(worstMs, 2.0, $"{worst}: {worstMs:0.00} ms je Raster");
        }
    }
}
