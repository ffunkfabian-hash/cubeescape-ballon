// Einstieg der Szene „Firstfeel“: liest ego.json, baut Licht, Parcours und Spielfigur. Befehlszeile der Build:
//   -ballonCapture <Ordner>   Ablauf Zielen → Feuerstoß → leeres Nachladen → Betrachten als PNG-Folge (1280 × 720, 30 fps)
//   -ballonCompare <Ordner>   Standbilder hip/ads (1600 × 900) im Studiolicht für den Vergleich mit Blender
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace Ballon.Ego
{
    public sealed class Bootstrap : MonoBehaviour
    {
        public TextAsset egoJson;
        public GameObject weaponModel, armsModel;
        public Material[] roleMaterials;         // Namen „Role_<rolle>“
        public Material floor, wall, cover, target, targetRing, flash, post, decal, backdrop;
        public const int ViewmodelLayer = 31;
        public const int OutRenderer = 1;
        public const int StudioEmitLayer = 30;   // Lichtflächen nur für die Reflexionssonde (Vergleichsmodus)         // Renderer „Out“ mit dem AgX-Durchgang (BallonSetup.OutRenderer)     // Ebene „Viewmodel“ (in den Projekteinstellungen benannt)

        public EgoFile D { get; private set; }
        public EgoSolver S { get; private set; }
        public EgoPlayer Player { get; private set; }
        public RangeTargets Range { get; private set; }
        public Transform RangeRoot { get; private set; }
        public Light Sun { get; private set; }
        public ReflectionProbe Probe { get; private set; }

        void Awake()
        {
            Application.targetFrameRate = 120;
            QualitySettings.vSyncCount = 1;
            D = EgoFile.Parse(egoJson.text);
            S = new EgoSolver(D);
            var roles = new Dictionary<string, Material>();
            foreach (var m in roleMaterials) roles[m.name.Replace("Role_", "")] = m;
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.62f, 0.66f, 0.72f);
            RenderSettings.ambientEquatorColor = new Color(0.46f, 0.48f, 0.5f);
            RenderSettings.ambientGroundColor = new Color(0.28f, 0.28f, 0.29f);
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogColor = new Color(0.62f, 0.66f, 0.70f);
            RenderSettings.fogStartDistance = 60;
            RenderSettings.fogEndDistance = 220;
            Sun = new GameObject("Sonne").AddComponent<Light>();
            Sun.type = LightType.Directional;
            Sun.intensity = 1.25f;
            Sun.color = new Color(1f, 0.97f, 0.92f);
            Sun.shadows = LightShadows.Soft;
            Sun.transform.rotation = Quaternion.Euler(48, -35, 0);
            RangeRoot = new GameObject("Parcours").transform;
            Range = RangeBuilder.Build(RangeRoot, new RangeBuilder.Mats { floor = floor, wall = wall, cover = cover, target = target,
                                                                          targetRing = targetRing, flash = flash, post = post });
            Probe = new GameObject("Reflexion").AddComponent<ReflectionProbe>();   // Metalle spiegeln den Parcours statt Schwarz
            Probe.transform.position = new Vector3(0, 1.6f, 6);
            Probe.mode = UnityEngine.Rendering.ReflectionProbeMode.Realtime;
            Probe.refreshMode = UnityEngine.Rendering.ReflectionProbeRefreshMode.ViaScripting;
            Probe.timeSlicingMode = UnityEngine.Rendering.ReflectionProbeTimeSlicingMode.NoTimeSlicing;
            Probe.size = new Vector3(44, 24, 120);
            Probe.resolution = 128;
            Probe.cullingMask = ~(1 << ViewmodelLayer);
            Probe.clearFlags = UnityEngine.Rendering.ReflectionProbeClearFlags.SolidColor;
            Probe.backgroundColor = RenderSettings.fogColor;
            Probe.RenderProbe();
            Player = EgoPlayer.Create(S, weaponModel, armsModel, roles, ViewmodelLayer, new Vector3(0, 0.01f, 1.5f), 0);
            Player.decalMat = decal;
            Player.range = Range;
            var args = Environment.GetCommandLineArgs();
            string cap = Arg(args, "-ballonCapture"), cmp = Arg(args, "-ballonCompare");
            if (float.TryParse(Arg(args, "-ballonStudioScale") ?? "", System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out var ss)) studioScale = ss;
            if (float.TryParse(Arg(args, "-ballonEmitScale") ?? "", System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out var es)) emitScale = es;
            string bench = Arg(args, "-ballonBench");
            if (bench != null) StartCoroutine(Bench(bench));
            else if (cap != null) StartCoroutine(Capture(cap));
            else if (cmp != null) StartCoroutine(Compare(cmp));
            else Cursor.lockState = CursorLockMode.Locked;
        }

        static string Arg(string[] a, string k)
        {
            int i = Array.IndexOf(a, k);
            return i >= 0 && i + 1 < a.Length ? a[i + 1] : null;
        }

        /// <summary>Vorführablauf für das MP4 (Zeiten in Sekunden); Magazin mit 9 Patronen, damit der Feuerstoß es leert.</summary>
        public static ScriptedInput DemoScript() => new ScriptedInput()
            .Add(0.0f, 0.9f)                                   // Ruhe an der Hüfte
            .Add(0.9f, 3.0f, hold: "aim")                      // Zielen
            .Add(1.6f, 2.8f, hold: "aim fire")                 // Feuerstoß, leert das Magazin (9 Patronen)
            .Add(3.4f, 3.5f, press: "reload")                  // leeres Nachladen
            .Add(6.4f, 6.5f, press: "inspect")                 // Betrachten (nach dem Nachladen, 2,5 s bei Tempo 1,25)
            .Add(6.5f, 10.9f);

        IEnumerator Capture(string dir)
        {
            Directory.CreateDirectory(dir);
            Player.hud = false;
            var demo = DemoScript();
            Player.input = demo;
            Player.C.ReadyNow();
            Player.C.ammo = 9;
            const float dt = 1f / 30f;
            Player.deltaOverride = () => dt;
            Player.Teleport(new Vector3(0.6f, 0.01f, 1.6f), -4f, 1.5f);
            var rt = HdrTarget(1280, 720, 4);
            Player.worldCam.targetTexture = rt;
            var tex = new Texture2D(1280, 720, TextureFormat.RGB24, false);
            var markers = new List<string>();
            Player.C.Marker += (a, m) => markers.Add($"{Time.frameCount - _f0},{a},{m}");
            Player.C.Shot += () => markers.Add($"{Time.frameCount - _f0},shot,{Player.C.ammo}");
            Player.enabled = false;                    // Schritte hier, damit Bild und Auswertung zusammenpassen
            _f0 = Time.frameCount;
            int n = Mathf.CeilToInt(demo.Duration / dt);
            for (int i = 0; i < n; i++)
            {
                Player.Step(dt);
                yield return new WaitForEndOfFrame();
                ReadBack(rt, tex);
                File.WriteAllBytes(Path.Combine(dir, $"{i:0000}.png"), tex.EncodeToPNG());
                File.AppendAllText(Path.Combine(dir, "frames.csv"), $"{i},{Player.C.ActionName},{Player.C.Frame:0.0},{Player.C.ammo}\n");
            }
            File.WriteAllLines(Path.Combine(dir, "markers.csv"), markers);
            Debug.Log($"[Ballon] Aufnahme: {n} Bilder in {dir}");
            Application.Quit();
        }

        int _f0;

        /// <summary>HDR-Ziel (Half, linear): URP übernimmt das Zielformat für den Zwischenpuffer, ein 8-Bit-Ziel schnitte vor AgX bei 1 ab.</summary>
        public static RenderTexture HdrTarget(int w, int h, int aa) =>
            new RenderTexture(w, h, 24, RenderTextureFormat.ARGBHalf, RenderTextureReadWrite.Linear) { antiAliasing = aa };

        /// <summary>HDR-Ziel (nach AgX: Anzeige-linear ≤ 1) → sRGB-kodierte Pixel in `tex` (RGB24).</summary>
        public static void ReadBack(RenderTexture hdr, Texture2D tex)
        {
            var ldr = RenderTexture.GetTemporary(hdr.width, hdr.height, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
            Graphics.Blit(hdr, ldr);
            var prev = RenderTexture.active;
            RenderTexture.active = ldr;
            tex.ReadPixels(new Rect(0, 0, hdr.width, hdr.height), 0, 0);
            tex.Apply();
            RenderTexture.active = prev;
            RenderTexture.ReleaseTemporary(ldr);
        }

        /// <summary>Leistung im Parcours: Vorführablauf in Echtzeit ohne VSync, Bildzeiten (ms) nach `file` (Mittel, 95-, 99-Perzentil).</summary>
        IEnumerator Bench(string file)
        {
            QualitySettings.vSyncCount = 0;
            Application.targetFrameRate = -1;
            Player.hud = true;
            Player.C.ReadyNow();
            Player.C.ammo = 9;
            Player.input = DemoScript();
            for (int i = 0; i < 30; i++) yield return null;      // Aufwärmen
            var ms = new List<float>();
            float t = 0;
            while (t < 10f)
            {
                yield return null;
                ms.Add(Time.unscaledDeltaTime * 1000f);
                t += Time.unscaledDeltaTime;
            }
            ms.Sort();
            float mean = 0;
            foreach (var v in ms) mean += v;
            mean /= ms.Count;
            var I = System.Globalization.CultureInfo.InvariantCulture;
            File.WriteAllText(file, string.Format(I, "{{\"frames\": {0}, \"mean_ms\": {1:0.00}, \"p95_ms\": {2:0.00}, \"p99_ms\": {3:0.00}, " +
                "\"width\": {4}, \"height\": {5}, \"gpu\": \"{6}\"}}\n", ms.Count, mean, ms[(int)(ms.Count * 0.95f)], ms[(int)(ms.Count * 0.99f)],
                Screen.width, Screen.height, SystemInfo.graphicsDeviceName));
            Debug.Log($"[Ballon] Leistung: {ms.Count} Bilder, Mittel {mean:0.00} ms");
            Application.Quit();
        }

        /// <summary>Lichtmaßstab: Unity-Intensität = studioScale · P / π² aus der Blender-Leistung P (W) eines Flächenlichts.</summary>
        [NonSerialized] public float studioScale = 1f;    // nicht in der Szene speichern: der Code-Wert gilt
        [NonSerialized] public float emitScale = 1f;      // Anteil der Lichtflächen in der Sonde: 1 = Blender-Strahldichte; Messreihe 0/0,25/0,5/1 bestätigt 1

        static Color Lin(string hex)
        {
            ColorUtility.TryParseHtmlString(hex, out var c);
            return c.linear;
        }

        /// <summary>Studio wie tools/blender_build.setup_aaa (bg 'mid'): vier Flächenlichter als weiche Spotlichter, Verlaufshintergrund
        /// im Bildraum (#4C525A → #9EA4AC zwischen 5 und 95 % Höhe), Umgebung #8C96A3 × 0,45 für Licht und Spiegelungen.</summary>
        public void StudioLike(Camera cam)
        {
            var amb = Lin("#8C96A3") * 0.45f;
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = amb.gamma;
            RenderSettings.ambientIntensity = 1f;
            DynamicGI.UpdateEnvironment();
            Player.viewCam.transform.localRotation = Quaternion.identity;
            cam.cullingMask &= ~(1 << StudioEmitLayer);
            var lights = new (string, Vector3, float, string)[]
            {
                ("Key", new Vector3(-0.9f, -0.9f, 1.3f), 170f, "#FFF4E6"), ("Fill", new Vector3(1.2f, -0.5f, 0.2f), 40f, "#DCE6F2"),
                ("Rim", new Vector3(0.6f, 1.4f, 0.9f), 320f, "#E8F1FF"), ("Top", new Vector3(0f, 0f, 1.8f), 60f, "#FFFFFF"),
            };
            var sizes = new Dictionary<string, float> { ["Key"] = 1.2f, ["Fill"] = 2.5f, ["Rim"] = 0.9f, ["Top"] = 3.0f };
            foreach (var (nm, p, watt, hex) in lights)
            {
                // Spiegelbild des Flächenlichts: leuchtende Fläche mit Strahldichte P / (π · A), nur für die Reflexionssonde sichtbar
                if (backdrop != null)
                {
                    float a = sizes[nm];
                    var e = GameObject.CreatePrimitive(PrimitiveType.Quad);
                    Destroy(e.GetComponent<Collider>());
                    e.name = "Studio Fläche " + nm;
                    e.layer = StudioEmitLayer;
                    var em = new Material(backdrop);
                    var c = Lin(hex) * (emitScale * studioScale * watt / (Mathf.PI * a * a));
                    em.SetColor("_BaseColor", new Color(c.r, c.g, c.b, 1).gamma);   // Materialfarben sind Gamma-Werte (Unity linearisiert)
                    e.GetComponent<Renderer>().sharedMaterial = em;
                    e.GetComponent<Renderer>().shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                    e.transform.SetParent(Player.head, false);
                    e.transform.localPosition = BMath.PointToUnity(D.toUnity, p);
                    e.transform.localRotation = Quaternion.LookRotation(BMath.PointToUnity(D.toUnity, p - new Vector3(0, -0.1f, 0.1f)), Vector3.up);
                    e.transform.localScale = new Vector3(a, a, 1);
                }
                var l = new GameObject("Studio " + nm).AddComponent<Light>();
                l.type = LightType.Spot;
                l.spotAngle = 150f;
                l.innerSpotAngle = 60f;
                l.range = 20f;
                l.intensity = studioScale * watt / (Mathf.PI * Mathf.PI);
                l.color = Lin(hex).gamma;
                l.shadows = LightShadows.None;      // Cycles-Flächenlichter dieser Größe werfen kaum sichtbare Schatten; Kontaktschatten im AO
                l.transform.SetParent(Player.head, false);
                l.transform.localPosition = BMath.PointToUnity(D.toUnity, p);
                l.transform.localRotation = Quaternion.LookRotation(BMath.PointToUnity(D.toUnity, new Vector3(0, -0.1f, 0.1f) - p), Vector3.up);
            }
            if (backdrop != null)
            {
                var g = new Texture2D(1, 256, TextureFormat.RGBAHalf, false, true) { wrapMode = TextureWrapMode.Clamp };
                Color lo = Lin("#4C525A"), hi = Lin("#9EA4AC");
                for (int y = 0; y < 256; y++) g.SetPixel(0, y, Color.Lerp(lo, hi, Mathf.Clamp01((y / 255f - 0.05f) / 0.9f)));
                g.Apply();
                var m = new Material(backdrop);
                m.SetTexture("_BaseMap", g);
                m.SetColor("_BaseColor", Color.white);
                var q = GameObject.CreatePrimitive(PrimitiveType.Quad);
                Destroy(q.GetComponent<Collider>());
                q.name = "Studio Hintergrund";
                q.GetComponent<Renderer>().sharedMaterial = m;
                q.GetComponent<Renderer>().shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                q.transform.SetParent(cam.transform, false);
                float d = 30f, hgt = 2 * d * Mathf.Tan(Camera.HorizontalToVerticalFieldOfView(D.camera.h_fov_deg, 16f / 9f) * Mathf.Deg2Rad / 2) * 1.02f;
                q.transform.localPosition = new Vector3(0, 0, d);
                q.transform.localScale = new Vector3(hgt * 16f / 9f, hgt, 1);
            }
            // Umgebung für Spiegelungen wie Blenders Nicht-Kamerastrahlen: einheitlich + die Lichtflächen
            Probe.transform.position = Player.head.position;
            Probe.resolution = 512;
            Probe.size = new Vector3(20, 20, 20);
            Probe.hdr = true;
            Probe.cullingMask = 1 << StudioEmitLayer;
            Probe.backgroundColor = amb.gamma;
            Probe.RenderProbe();
        }

        IEnumerator Compare(string dir)
        {
            Directory.CreateDirectory(dir);
            Player.hud = false;
            Player.enabled = false;
            RangeRoot.gameObject.SetActive(false);
            Sun.enabled = false;
            RenderSettings.fog = false;
            var cam = Player.worldCam;
            StudioLike(cam);
            yield return null;                      // Reflexionssonde rendern lassen
            yield return null;
            var rt = HdrTarget(1600, 900, 8);
            cam.targetTexture = rt;
            cam.fieldOfView = Player.viewCam.fieldOfView = Camera.HorizontalToVerticalFieldOfView(D.camera.h_fov_deg, 16f / 9f);
            var tex = new Texture2D(1600, 900, TextureFormat.RGB24, false);
            foreach (var pose in new[] { "hip", "ads", "reload", "inspect_r" })
            {
                var o = S.Evaluate(S.StillAction(pose), 0, new EgoState());
                Player.rig.Apply(o);
                yield return new WaitForEndOfFrame();
                ReadBack(rt, tex);
                File.WriteAllBytes(Path.Combine(dir, $"{pose}_unity.png"), tex.EncodeToPNG());
            }
            Debug.Log($"[Ballon] Vergleichsbilder in {dir}");
            Application.Quit();
        }
    }
}
