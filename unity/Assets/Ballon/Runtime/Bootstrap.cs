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
        public Material floor, wall, cover, target, targetRing, flash, post, decal;
        public const int ViewmodelLayer = 31;     // Ebene „Viewmodel“ (in den Projekteinstellungen benannt)

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
            if (cap != null) StartCoroutine(Capture(cap));
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
            var rt = new RenderTexture(1280, 720, 24) { antiAliasing = 4 };
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
                RenderTexture.active = rt;
                tex.ReadPixels(new Rect(0, 0, 1280, 720), 0, 0);
                tex.Apply();
                RenderTexture.active = null;
                File.WriteAllBytes(Path.Combine(dir, $"{i:0000}.png"), tex.EncodeToPNG());
                File.AppendAllText(Path.Combine(dir, "frames.csv"), $"{i},{Player.C.ActionName},{Player.C.Frame:0.0},{Player.C.ammo}\n");
            }
            File.WriteAllLines(Path.Combine(dir, "markers.csv"), markers);
            Debug.Log($"[Ballon] Aufnahme: {n} Bilder in {dir}");
            Application.Quit();
        }

        int _f0;

        IEnumerator Compare(string dir)
        {
            Directory.CreateDirectory(dir);
            Player.hud = false;
            Player.enabled = false;
            RangeRoot.gameObject.SetActive(false);
            Sun.enabled = false;
            RenderSettings.fog = false;
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.42f, 0.45f, 0.5f);
            var cam = Player.worldCam;
            cam.backgroundColor = new Color(0.44f, 0.47f, 0.51f);
            Probe.backgroundColor = new Color(0.55f, 0.59f, 0.64f);     // Blender: Umgebung #8C96A3 für Nicht-Kamerastrahlen
            Probe.RenderProbe();
            Player.viewCam.transform.localRotation = Quaternion.identity;
            // Studiolicht wie tools/blender_build.setup_aaa (Lage im Blender-Kameraraum, Ziel (0, −0,1, 0,1))
            var lights = new (string, Vector3, float, Color)[]
            {
                ("Key", new Vector3(-0.9f, -0.9f, 1.3f), 1.25f, new Color(1f, 0.96f, 0.9f)),
                ("Fill", new Vector3(1.2f, -0.5f, 0.2f), 0.35f, new Color(0.86f, 0.9f, 0.95f)),
                ("Rim", new Vector3(0.6f, 1.4f, 0.9f), 1.1f, new Color(0.91f, 0.95f, 1f)),
                ("Top", new Vector3(0f, 0f, 1.8f), 0.4f, Color.white),
            };
            foreach (var (nm, p, k, c) in lights)
            {
                var l = new GameObject("Studio " + nm).AddComponent<Light>();
                l.type = LightType.Directional;
                l.intensity = k;
                l.color = c;
                l.shadows = LightShadows.None;
                l.transform.SetParent(Player.head, false);
                var dirB = new Vector3(0, -0.1f, 0.1f) - p;
                l.transform.localRotation = Quaternion.LookRotation(BMath.PointToUnity(D.toUnity, dirB), Vector3.up);
            }
            var rt = new RenderTexture(1600, 900, 24) { antiAliasing = 8 };
            cam.targetTexture = rt;
            cam.fieldOfView = Player.viewCam.fieldOfView = Camera.HorizontalToVerticalFieldOfView(D.camera.h_fov_deg, 16f / 9f);
            var tex = new Texture2D(1600, 900, TextureFormat.RGB24, false);
            foreach (var pose in new[] { "hip", "ads", "reload", "inspect_r" })
            {
                var o = S.Evaluate(S.StillAction(pose), 0, new EgoState());
                Player.rig.Apply(o);
                yield return new WaitForEndOfFrame();
                RenderTexture.active = rt;
                tex.ReadPixels(new Rect(0, 0, 1600, 900), 0, 0);
                tex.Apply();
                RenderTexture.active = null;
                File.WriteAllBytes(Path.Combine(dir, $"{pose}_unity.png"), tex.EncodeToPNG());
            }
            Debug.Log($"[Ballon] Vergleichsbilder in {dir}");
            Application.Quit();
        }
    }
}
