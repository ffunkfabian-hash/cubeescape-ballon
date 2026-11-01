// Ursachen der Ruckelspitzen (0.37 „Steadyframe“): liest die Profiler-Protokolle der Ruckelmessung (StutterBench, -ballonProfile) und
// schreibt je Bild über der Schwelle die teuersten Proben von Haupt- und Renderthread nach JSON, dazu Bildzeit, GC-Speicher und die
// Metadaten (Durchgang, Waffe, Ereignis). Aufruf im Batch-Editor:
//   Unity -batchmode -quit -projectPath unity -executeMethod Ballon.Ego.Editor.ProfileSpikes.Run -ballonRawDir <Ordner> -ballonOut <json>
//         [-ballonSpikeMs 25]
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEditor.Profiling;
using UnityEditorInternal;

namespace Ballon.Ego.Editor
{
    public static class ProfileSpikes
    {
        static string Arg(string k)
        {
            var a = Environment.GetCommandLineArgs();
            int i = Array.IndexOf(a, k);
            return i >= 0 && i + 1 < a.Length ? a[i + 1] : null;
        }

        struct Item { public string name, path; public float self, total, gcKb; public int calls; }

        public static void Run()
        {
            string dir = Arg("-ballonRawDir"), outFile = Arg("-ballonOut");
            float spike = float.TryParse(Arg("-ballonSpikeMs") ?? "", NumberStyles.Float, CultureInfo.InvariantCulture, out var s) ? s : 25f;
            var I = CultureInfo.InvariantCulture;
            var sb = new StringBuilder("[\n");
            bool first = true;
            foreach (var raw in Directory.GetFiles(dir, "*.raw").OrderBy(x => x))
            {
                if (!ProfilerDriver.LoadProfile(raw, false)) { UnityEngine.Debug.LogError($"[Ballon] nicht lesbar: {raw}"); continue; }
                int f0 = ProfilerDriver.firstFrameIndex, f1 = ProfilerDriver.lastFrameIndex;
                UnityEngine.Debug.Log($"[Ballon] {Path.GetFileName(raw)}: Bilder {f0}–{f1}");
                for (int f = f0; f <= f1; f++)
                {
                    float ms;
                    int[] meta;
                    using (var raw0 = ProfilerDriver.GetRawFrameDataView(f, 0))
                    {
                        if (!raw0.valid) continue;
                        ms = raw0.frameTimeMs;
                        var m = raw0.GetFrameMetaData<int>(StutterBench.MetaId, 0);
                        meta = m.IsCreated && m.Length >= 4 ? m.ToArray() : new[] { -1, -1, -1, -1 };
                    }
                    if (ms < spike) continue;
                    var threads = new List<(string, List<Item>, float)>();
                    for (int th = 0; th < 64; th++)
                    {
                        using (var probe = ProfilerDriver.GetRawFrameDataView(f, th))
                        {
                            if (!probe.valid) break;
                            if (probe.threadName != "Main Thread" && probe.threadName != "Render Thread") continue;
                        }
                        using (var h = ProfilerDriver.GetHierarchyFrameDataView(f, th, HierarchyFrameDataView.ViewModes.MergeSamplesWithTheSameName,
                                                                               HierarchyFrameDataView.columnSelfTime, false))
                        {
                            var items = new List<Item>();
                            Walk(h, h.GetRootItemID(), "", items);
                            threads.Add((h.threadName, items, h.frameTimeMs));
                        }
                    }
                    if (!first) sb.Append(",\n");
                    first = false;
                    sb.AppendFormat(I, "{{\"file\": \"{0}\", \"index\": {1}, \"frame\": {2}, \"pass\": {3}, \"weapon\": {4}, \"event\": \"{5}\", \"ms\": {6:0.00}",
                                    Path.GetFileName(raw), f, meta[0], meta[1], meta[2], meta[3] >= 0 && meta[3] < StutterBench.Events.Length ? StutterBench.Events[meta[3]] : "?", ms);
                    foreach (var (tn, items, tms) in threads)
                    {
                        string key = tn == "Main Thread" ? "main" : "render";
                        float gc = items.Where(x => x.name == "GC.Alloc").Sum(x => x.gcKb);
                        sb.AppendFormat(I, ", \"{0}_gc_kb\": {1:0.0}, \"{0}_self\": [", key, gc);
                        int n = 0;
                        foreach (var it in items.OrderByDescending(x => x.self).Take(14))
                            sb.AppendFormat(I, "{0}{{\"name\": \"{1}\", \"self_ms\": {2:0.00}, \"total_ms\": {3:0.00}, \"calls\": {4}, \"path\": \"{5}\"}}",
                                            n++ > 0 ? ", " : "", Esc(it.name), it.self, it.total, it.calls, Esc(it.path));
                        sb.Append("], \"" + key + "_alloc\": [");
                        n = 0;
                        foreach (var it in items.Where(x => x.name == "GC.Alloc").OrderByDescending(x => x.gcKb).Take(8))
                            sb.AppendFormat(I, "{0}{{\"kb\": {1:0.0}, \"calls\": {2}, \"path\": \"{3}\"}}", n++ > 0 ? ", " : "", it.gcKb, it.calls, Esc(it.path));
                        sb.Append("]");
                    }
                    sb.Append("}");
                }
            }
            sb.Append("\n]\n");
            File.WriteAllText(outFile, sb.ToString());
            UnityEngine.Debug.Log($"[Ballon] Spitzen ≥ {spike} ms → {outFile}");
        }

        /// <summary>Bildschirmfoto des Profiler-Fensters bei einem Bild (Beleg): Editor mit Oberfläche, nicht im Batch –
        ///   Unity -projectPath unity -executeMethod Ballon.Ego.Editor.ProfileSpikes.Shot -ballonRaw <raw> -ballonIndex <Profiler-Bild>
        ///         -ballonPng <png>
        /// Lädt das Protokoll, wählt das Bild, wartet einige Editor-Takte und liest die Fensterpixel; beendet danach den Editor.</summary>
        public static void Shot()
        {
            string raw = Arg("-ballonRaw"), png = Arg("-ballonPng");
            var win = EditorWindow.GetWindow<ProfilerWindow>();
            win.position = new UnityEngine.Rect(40, 60, 1800, 1000);
            win.Show();
            ProfilerDriver.LoadProfile(raw, false);
            int index = Arg("-ballonIndex") != null ? int.Parse(Arg("-ballonIndex"), CultureInfo.InvariantCulture) : -1;
            string ev = Arg("-ballonEvent");                   // ohne Index: längstes Bild dieses Ereignisses im Protokoll
            if (index < 0)
            {
                float best = -1;
                for (int f = ProfilerDriver.firstFrameIndex; f <= ProfilerDriver.lastFrameIndex; f++)
                    using (var v = ProfilerDriver.GetRawFrameDataView(f, 0))
                    {
                        if (!v.valid) continue;
                        var m = v.GetFrameMetaData<int>(StutterBench.MetaId, 0);
                        bool hit = ev == null || m.IsCreated && m.Length >= 4 && m[3] >= 0 && m[3] < StutterBench.Events.Length && StutterBench.Events[m[3]] == ev;
                        if (hit && v.frameTimeMs > best) { best = v.frameTimeMs; index = f; }
                    }
                UnityEngine.Debug.Log($"[Ballon] längstes Bild ({ev ?? "alle"}): {index}, {best:0.0} ms");
            }
            int ticks = 0;
            void Tick()
            {
                ticks++;
                if (ticks == 20 || ticks == 90 || ticks == 160)           // nachwählen: die Detailtafel folgt der Wahl erst nach dem Laden
                {
                    win.selectedFrameIndex = index;
                    win.Focus();
                    win.Repaint();
                }
                if (ticks < 240) return;
                EditorApplication.update -= Tick;
                var r = win.position;
                float ppp = EditorGUIUtility.pixelsPerPoint;
                var px = UnityEditorInternal.InternalEditorUtility.ReadScreenPixel(r.position * ppp, (int)(r.width * ppp), (int)(r.height * ppp));
                var tex = new UnityEngine.Texture2D((int)(r.width * ppp), (int)(r.height * ppp), UnityEngine.TextureFormat.RGB24, false);
                tex.SetPixels(px);
                tex.Apply();
                File.WriteAllBytes(png, UnityEngine.ImageConversion.EncodeToPNG(tex));
                UnityEngine.Debug.Log($"[Ballon] Profiler-Bild {index} → {png}");
                EditorApplication.Exit(0);
            }
            EditorApplication.update += Tick;
        }

        static void Walk(HierarchyFrameDataView h, int id, string path, List<Item> items)
        {
            var kids = new List<int>();
            h.GetItemChildren(id, kids);
            foreach (var k in kids)
            {
                string name = h.GetItemName(k);
                string p = path.Length == 0 ? name : path + " › " + name;
                items.Add(new Item
                {
                    name = name, path = p.Length > 300 ? "…" + p.Substring(p.Length - 300) : p,
                    self = h.GetItemColumnDataAsFloat(k, HierarchyFrameDataView.columnSelfTime),
                    total = h.GetItemColumnDataAsFloat(k, HierarchyFrameDataView.columnTotalTime),
                    gcKb = h.GetItemColumnDataAsFloat(k, HierarchyFrameDataView.columnGcMemory) / 1024f,
                    calls = (int)h.GetItemColumnDataAsFloat(k, HierarchyFrameDataView.columnCalls),
                });
                Walk(h, k, p, items);
            }
        }

        static string Esc(string s) => s.Replace("\\", "\\\\").Replace("\"", "\\\"");
    }
}
