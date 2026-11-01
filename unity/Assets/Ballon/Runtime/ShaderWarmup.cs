// Shader-Aufwärmen (0.38 „Prewarm“): Bei kaltem Metal-Zwischenspeicher (erster Start einer neuen Build) übersetzte der Renderthread
// beim ersten Einsatz einer Waffe Shader samt Pipeline-Zustand (`CreateGpuProgram`, bis 366 ms beim ersten MP-Wechsel). Eine im
// Spieler aufgezeichnete GraphicsStateCollection (Variante + Zustand: Netzformat, Renderziele, Blend) wird beim Laden auf
// Arbeitsthreads aufgewärmt. `Shader.WarmupAllShaders` kennt diese Zustände unter Metal nicht (0.37: +14,4 s, Rest 150 ms).
// Befehlszeile der Build:
//   -ballonGscRecord <datei>   Varianten und Zustände dieses Laufs aufzeichnen, beim Beenden speichern (mit -ballonStutter: alle
//                              Waffen und Ereignisse; tools/unity_run.py aufwaermen); ohne Aufwärmen
//   -ballonNoWarmup            Gegenprobe ohne Aufwärmen
//   -ballonShaderLog           jede Shader-Übersetzung ins Spielerprotokoll (GraphicsSettings.logWhenShaderIsCompiled)
using System;
using Unity.Jobs;
using UnityEngine;
using UnityEngine.Rendering;

namespace Ballon.Ego
{
    public static class ShaderWarmup
    {
        public const string AssetPath = "Assets/Ballon/Warmup/ballon_mac_metal.graphicsstate";
        static GraphicsStateCollection _trace;
        static string _tracePath;
        static bool _off;
        static JobHandle _job;

        /// <summary>Die aufgewärmte Sammlung (null: keine, abgeschaltet oder Aufzeichnung).</summary>
        public static GraphicsStateCollection Active { get; private set; }
        /// <summary>Beginn und Ende des Aufwärmens in s seit Programmstart (Ende −1: läuft noch oder nie begonnen).</summary>
        public static double StartedAt { get; private set; } = -1;
        public static double DoneAt { get; private set; } = -1;
        public static bool Recording => _trace != null;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        static void Init()
        {
            var a = Environment.GetCommandLineArgs();
            _off = Array.IndexOf(a, "-ballonNoWarmup") >= 0;
            if (Array.IndexOf(a, "-ballonShaderLog") >= 0) GraphicsSettings.logWhenShaderIsCompiled = true;
            int i = Array.IndexOf(a, "-ballonGscRecord");
            if (i < 0 || i + 1 >= a.Length) return;
            _tracePath = a[i + 1];
            _trace = new GraphicsStateCollection();
            if (!_trace.BeginTrace()) { Debug.LogError("[Ballon] Aufwärmen: Aufzeichnung nicht gestartet"); _trace = null; return; }
            Application.quitting += SaveTrace;
        }

        /// <summary>Aufzeichnung beenden und speichern (StutterBench am Ende, sonst beim Beenden).</summary>
        public static void SaveTrace()
        {
            if (_trace == null) return;
            _trace.EndTrace();
            bool ok = _trace.SaveToFile(_tracePath);
            Debug.Log($"[Ballon] Aufwärmen: {_trace.variantCount} Varianten, {_trace.totalGraphicsStateCount} Zustände " +
                      $"({_trace.graphicsDeviceType}, {_trace.qualityLevelName}) → {_tracePath}{(ok ? "" : " – nicht gespeichert")}");
            if (!ok) Debug.LogError($"[Ballon] Aufwärmen: {_tracePath} nicht schreibbar");
            _trace = null;
        }

        /// <summary>Aufwärmen auf Arbeitsthreads beginnen (Bootstrap.Awake, vor dem Aufbau der Welt); Fehlzugriffe danach mitschreiben.</summary>
        public static void Begin(GraphicsStateCollection gsc)
        {
            if (gsc == null || _off || _trace != null || Active != null || Application.isEditor) return;   // Editor: übersetzt selbst im Hintergrund
            if (gsc.graphicsDeviceType != SystemInfo.graphicsDeviceType)
            {
                Debug.LogWarning($"[Ballon] Aufwärmen: Sammlung für {gsc.graphicsDeviceType}, Gerät {SystemInfo.graphicsDeviceType} – übersprungen");
                return;
            }
            Active = gsc;
            StartedAt = Time.realtimeSinceStartupAsDouble;
            _job = gsc.WarmUp(default, true);                  // auf mehrere Sammlungen verteilt nicht schneller (4 Teile: 1,37–1,48 s statt 1,43 s)
            JobHandle.ScheduleBatchedJobs();
        }

        /// <summary>Fertig aufgewärmt (oder nichts aufzuwärmen); hält beim ersten Mal die Endzeit fest.</summary>
        public static bool Done
        {
            get
            {
                if (Active == null || DoneAt >= 0) return true;
                if (!_job.IsCompleted) return false;
                _job.Complete();
                DoneAt = Time.realtimeSinceStartupAsDouble;
                Debug.Log($"[Ballon] Aufwärmen: {Active.completedWarmupCount} von {Active.totalGraphicsStateCount} Zuständen " +
                          $"({Active.variantCount} Varianten) in {(DoneAt - StartedAt) * 1000:0} ms");
                return true;
            }
        }

        /// <summary>Zustände, die Unity nach dem Aufwärmen als Fehlzugriff meldet: Wegweiser, kein Beweis (0.38: weiter 9 gemeldet, alle in
        /// der Sammlung, ohne Hänger); maßgeblich ist die kalte Messung.</summary>
        public static int CacheMisses => Active != null && Active.cacheMissCollection != null ? Active.cacheMissCollection.totalGraphicsStateCount : 0;

        /// <summary>Fehlzugriffe als Text: Shader, Pass (Subshader.Pass), Schlüsselwörter, Zahl der Zustände.</summary>
        public static void WriteMisses(string path)
        {
            var miss = Active?.cacheMissCollection;
            if (miss == null) return;
            var list = new System.Collections.Generic.List<GraphicsStateCollection.ShaderVariant>();
            miss.GetVariants(list);
            var sb = new System.Text.StringBuilder();
            foreach (var v in list)
            {
                sb.Append(v.shader != null ? v.shader.name : "?").Append('\t').Append(v.passId.SubshaderIndex).Append('.').Append(v.passId.PassIndex).Append('\t');
                if (v.keywords != null) foreach (var k in v.keywords) sb.Append(k.name).Append(' ');
                sb.Append('\t').Append(miss.GetGraphicsStateCountForVariant(v)).Append('\n');
            }
            miss.SaveToFile(System.IO.Path.ChangeExtension(path, ".graphicsstate"));   // mit Zuständen, zum Vergleich mit der Sammlung
            try { System.IO.File.WriteAllText(path, sb.ToString()); }
            catch (Exception e) { Debug.LogError($"[Ballon] Aufwärmen: {path} nicht schreibbar – {e.Message}"); }
        }
    }
}
