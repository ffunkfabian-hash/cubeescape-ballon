// Einstieg der Szene „Firstfeel“: liest ego.json, baut Licht, Parcours und Spielfigur. Befehlszeile der Build:
//   -ballonCapture <Ordner>   Ablauf Zielen → Feuerstoß → leeres Nachladen → Betrachten als PNG-Folge (1280 × 720, 30 fps)
//   -ballonCompare <Ordner>   Standbilder hip/ads (1600 × 900) im Studiolicht für den Vergleich mit Blender
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEngine.InputSystem;

namespace Ballon.Ego
{
    public sealed class Bootstrap : MonoBehaviour
    {
        public TextAsset egoJson;
        public GameObject weaponModel, armsModel;
        public Material[] roleMaterials;         // Namen „Role_<rolle>“
        public Material floor, wall, cover, target, targetRing, flash, post, decal, backdrop;
        public Material[] skinMaterials;         // Waffen-Skins in der Reihenfolge von ego.json › textures.skins (0 = standard)
        public TextAsset[] sceneJson;            // Szenen (ballon-scene/2), von BallonSetup aus Generated/Scenes/*/scene_*.json gesetzt;
        public GameObject[] scenePrefabs;        // gleiche Reihenfolge: FBX der Umgebung
        public Material[] sceneMaterials;        // Unlit-Vorlage (je Zone entsteht eine Kopie)
        public SceneAssetSet[] sceneAtlases;     // Atlanten der Szene, flach: Lichtszene · Zonenzahl + Zone (Reihenfolge wie im JSON)

        /// <summary>Alle Lichtatlanten einer Szene, flach: Index = Lichtszene · Zonenzahl + Zone.</summary>
        [Serializable] public class SceneAssetSet { public Texture2D[] textures; }
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
            ParcoursLook();
            Sun = new GameObject("Sonne").AddComponent<Light>();
            Sun.type = LightType.Directional;
            Sun.intensity = 1.25f;
            Sun.color = new Color(1f, 0.97f, 0.92f);
            Sun.shadows = LightShadows.Soft;
            Sun.transform.rotation = Quaternion.Euler(48, -35, 0);
            RangeRoot = new GameObject("Parcours").transform;
            _targetMats = new RangeBuilder.Mats { floor = floor, wall = wall, cover = cover, target = target,
                                                  targetRing = targetRing, flash = flash, post = post };
            Range = RangeBuilder.Build(RangeRoot, _targetMats);
            Probe = new GameObject("Reflexion").AddComponent<ReflectionProbe>();   // Metalle spiegeln den Parcours statt Schwarz
            Probe.mode = UnityEngine.Rendering.ReflectionProbeMode.Realtime;
            Probe.refreshMode = UnityEngine.Rendering.ReflectionProbeRefreshMode.ViaScripting;
            Probe.timeSlicingMode = UnityEngine.Rendering.ReflectionProbeTimeSlicingMode.NoTimeSlicing;
            Probe.clearFlags = UnityEngine.Rendering.ReflectionProbeClearFlags.SolidColor;
            ParcoursProbe();
            Probe.RenderProbe();
            Player = EgoPlayer.Create(S, weaponModel, armsModel, roles, ViewmodelLayer, ParcoursStart, 0);
            _parcoursBg = Player.worldCam.backgroundColor;
            _worldMask = Player.worldCam.cullingMask;
            Player.decalMat = decal;
            Player.skins = skinMaterials;
            Player.skinNames = D.textures?.skins?.Select(s => s.de).ToArray();
            Player.range = Range;
            LoadScenes();
            var args = Environment.GetCommandLineArgs();
            string cap = Arg(args, "-ballonCapture"), cmp = Arg(args, "-ballonCompare");
            if (float.TryParse(Arg(args, "-ballonStudioScale") ?? "", System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out var ss)) studioScale = ss;
            if (float.TryParse(Arg(args, "-ballonEmitScale") ?? "", System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out var es)) emitScale = es;
            string shotDir = Arg(args, "-ballonSceneShots");
            if (shotDir != null) { StartCoroutine(SceneShots(shotDir)); return; }
            string skinsDir = Arg(args, "-ballonSkins");
            if (skinsDir != null) { StartCoroutine(SkinSheet(skinsDir)); return; }
            string courseDir = Arg(args, "-ballonCourse");
            if (courseDir != null) { StartCoroutine(CourseCapture(courseDir, Arg(args, "-ballonScene") ?? "hangar", Arg(args, "-ballonLighting"))); return; }
            string bench = Arg(args, "-ballonBench");
            if (bench != null) StartCoroutine(Bench(bench, Arg(args, "-ballonScene")));
            else if (cap != null) StartCoroutine(Capture(cap));
            else if (cmp != null) StartCoroutine(Compare(cmp));
            else Cursor.lockState = CursorLockMode.Locked;
        }

        // ------------------------------------------------------------------------------------------------ Parcours
        public static readonly Vector3 ParcoursStart = new Vector3(0, 0.01f, 1.5f);
        RangeBuilder.Mats _targetMats;
        Color _parcoursBg;
        int _worldMask;

        /// <summary>Licht und Nebel des Parcours (Awake und Rückkehr aus einer Szene).</summary>
        void ParcoursLook()
        {
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.62f, 0.66f, 0.72f);
            RenderSettings.ambientEquatorColor = new Color(0.46f, 0.48f, 0.5f);
            RenderSettings.ambientGroundColor = new Color(0.28f, 0.28f, 0.29f);
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogColor = new Color(0.62f, 0.66f, 0.70f);
            RenderSettings.fogStartDistance = 60;
            RenderSettings.fogEndDistance = 220;
        }

        void ParcoursProbe()
        {
            Probe.transform.position = new Vector3(0, 1.6f, 6);
            Probe.center = Vector3.zero;
            Probe.size = new Vector3(44, 24, 120);
            Probe.resolution = 128;
            Probe.hdr = true;
            Probe.cullingMask = ~(1 << ViewmodelLayer);
            Probe.backgroundColor = RenderSettings.fogColor;
        }

        // ------------------------------------------------------------------------------------------------ Szenen (0.8, Lichtszenen 0.9)
        sealed class SceneEntry
        {
            public SceneFile data;
            public GameObject prefab;
            public Material mat;
            public Texture2D[][] atlases;       // [Lichtszene][Zone]
            public LoadedScene loaded;
            public int lighting;                // zuletzt gezeigte Lichtszene dieser Szene
        }
        readonly List<SceneEntry> _scenes = new List<SceneEntry>();

        /// <summary>-1 = Parcours, sonst Index der Szene.</summary>
        public int CurrentScene { get; private set; } = -1;
        /// <summary>Aktive Lichtszene der gezeigten Szene; -1 im grauen Parcours.</summary>
        public int CurrentLighting { get; private set; } = -1;
        public int SceneCount => _scenes.Count;
        /// <summary>Anzahl der Lichtszenen der gezeigten Szene (0 im Parcours).</summary>
        public int LightingCount => CurrentScene < 0 ? 0 : _scenes[CurrentScene].data.lightings.Length;
        public SceneFile SceneDataAt(int i) => _scenes[i].data;
        public string SceneName(int i) => i < 0 ? "Parcours" : string.IsNullOrEmpty(_scenes[i].data.de) ? _scenes[i].data.name : _scenes[i].data.de;
        /// <summary>Die gebaute Szene i, oder null, solange sie noch nie gezeigt wurde.</summary>
        public LoadedScene LoadedSceneAt(int i) => _scenes[i].loaded;

        void LoadScenes()
        {
            if (sceneJson == null) return;
            for (int i = 0; i < sceneJson.Length; i++)
            {
                if (sceneJson[i] == null) continue;
                try
                {
                    var f = SceneFile.Parse(sceneJson[i].text);
                    var flat = sceneAtlases != null && i < sceneAtlases.Length && sceneAtlases[i] != null ? sceneAtlases[i].textures : null;
                    AddScene(f, scenePrefabs != null && i < scenePrefabs.Length ? scenePrefabs[i] : null,
                             sceneMaterials != null && i < sceneMaterials.Length ? sceneMaterials[i] : null, Shape(f, flat));
                }
                catch (FormatException e)
                {
                    Debug.LogWarning($"[Ballon] {sceneJson[i].name} übersprungen: {e.Message}");     // z. B. ältere Szene: neu bauen (tools/scene_build.py)
                }
            }
        }

        /// <summary>Flache Atlasliste (Lichtszene · Zonenzahl + Zone) in [Lichtszene][Zone] ordnen.</summary>
        static Texture2D[][] Shape(SceneFile f, Texture2D[] flat)
        {
            var r = new Texture2D[f.lightings.Length][];
            if (flat != null && flat.Length != f.lightings.Length * f.zones.Length)
                Debug.LogWarning($"[Ballon] Szene {f.name}: {flat.Length} Atlanten eingetragen, erwartet {f.lightings.Length} Lichtszenen × {f.zones.Length} Zonen – " +
                                 "python3 tools/unity_run.py setup erneut ausführen");
            for (int li = 0; li < r.Length; li++)
            {
                r[li] = new Texture2D[f.zones.Length];
                for (int zi = 0; zi < f.zones.Length; zi++)
                {
                    int k = li * f.zones.Length + zi;
                    if (flat != null && k < flat.Length) r[li][zi] = flat[k];
                }
            }
            return r;
        }

        /// <summary>Szene anmelden (gebaut wird erst beim ersten Zeigen); gibt ihren Index zurück.
        /// `atlases` = [Lichtszene][Zone], `atlasMaterial` = Unlit-Vorlage (je Zone entsteht eine Kopie).</summary>
        public int AddScene(SceneFile f, GameObject prefab, Material atlasMaterial, Texture2D[][] atlases = null)
        {
            if (prefab == null) Debug.LogWarning($"[Ballon] Szene {f.name}: kein FBX – nur Collider, Lichter und Ziele");
            if (atlasMaterial == null) Debug.LogWarning($"[Ballon] Szene {f.name}: kein Atlas-Material");
            if (atlases == null) Debug.LogWarning($"[Ballon] Szene {f.name}: keine Lichtatlanten");
            _scenes.Add(new SceneEntry { data = f, prefab = prefab, mat = atlasMaterial, atlases = atlases });
            if (Player != null && _scenes.Count == 1) Player.SetScene(SceneName(CurrentScene), Range);   // Anzeige nennt ab jetzt die Szene
            return _scenes.Count - 1;
        }

        public void RemoveScene(int i)
        {
            if (CurrentScene == i) ShowScene(-1);
            if (_scenes[i].loaded != null) Destroy(_scenes[i].loaded.root.gameObject);
            _scenes.RemoveAt(i);
            if (CurrentScene > i) CurrentScene--;
        }

        /// <summary>Taste L: Parcours → Szene 0 → … → letzte Szene → Parcours.</summary>
        public void NextScene() => ShowScene(CurrentScene + 1 >= _scenes.Count ? -1 : CurrentScene + 1);

        /// <summary>Taste N: nächste Lichtszene der gezeigten Szene (im Parcours ohne Wirkung).</summary>
        public void NextLighting()
        {
            int n = LightingCount;
            if (n > 1) ShowLighting((CurrentLighting + 1) % n);
        }

        /// <summary>Taste T: zurück zum Startpunkt der gezeigten Szene (Parcours: Parcours-Start); ein laufender Lauf wird verworfen.</summary>
        public void ResetToStart()
        {
            if (CurrentScene < 0) { Player.Teleport(ParcoursStart, 0, 0); return; }
            var L = _scenes[CurrentScene].loaded;
            Player.Teleport(L.spawnPos, L.spawnYaw, 0);
            L.course?.Reset();
        }

        /// <summary>Parcours (-1) oder Szene i zeigen: Umgebung, Licht, Himmel, Reflexionssonde, Ziele und Spieler wechseln gemeinsam.
        /// Die Lichtszene ist die zuletzt gezeigte dieser Szene (anfangs die erste).</summary>
        public void ShowScene(int i)
        {
            if (i < -1 || i >= _scenes.Count) throw new ArgumentOutOfRangeException(nameof(i), $"Szene {i} (von {_scenes.Count})");
            if (i == CurrentScene) return;
            if (CurrentScene >= 0 && _scenes[CurrentScene].loaded != null) _scenes[CurrentScene].loaded.root.gameObject.SetActive(false);
            CurrentScene = i;
            var cam = Player.worldCam;
            if (i < 0)
            {
                CurrentLighting = -1;
                RangeRoot.gameObject.SetActive(true);
                Sun.enabled = true;
                ParcoursLook();
                cam.backgroundColor = _parcoursBg;
                cam.cullingMask = _worldMask;
                ParcoursProbe();
                Probe.RenderProbe();
                Player.SetScene("Parcours", Range);
                Player.Teleport(ParcoursStart, 0, 0);
                return;
            }
            var e = _scenes[i];
            var L = e.loaded ?? (e.loaded = SceneLoader.Build(e.data, e.prefab, e.mat, e.atlases, backdrop, _targetMats));
            RangeRoot.gameObject.SetActive(false);
            Sun.enabled = false;
            L.root.gameObject.SetActive(true);
            RenderSettings.fog = false;
            cam.cullingMask = _worldMask & ~(1 << StudioEmitLayer);  // Lichtflächen sieht nur die Sonde
            var eye = L.spawnPos + Vector3.up * Player.move.eye;
            Probe.transform.position = eye;
            Probe.center = L.bounds.center - eye;
            Probe.size = L.bounds.size + Vector3.one * 2f;
            Probe.resolution = 256;
            Probe.hdr = true;
            Probe.cullingMask = ~(1 << ViewmodelLayer);              // unbeleuchtete Umgebung plus Lichtflächen
            Player.SetScene(SceneName(i), L.targets, L.course);
            ApplyLighting(e, Mathf.Clamp(e.lighting, 0, e.data.lightings.Length - 1));
            Player.Teleport(L.spawnPos, L.spawnYaw, 0);
            L.course?.Reset();
        }

        /// <summary>Lichtszene li der gezeigten Szene: tauscht nur Atlanten, Lichtgruppe, Umgebungslicht, Himmel und Sonde (keine Geometrie).</summary>
        public void ShowLighting(int li)
        {
            if (CurrentScene < 0) throw new InvalidOperationException("Lichtszenen gibt es nur in einer Szene, nicht im Parcours");
            var e = _scenes[CurrentScene];
            if (li < 0 || li >= e.data.lightings.Length) throw new ArgumentOutOfRangeException(nameof(li), $"Lichtszene {li} (von {e.data.lightings.Length})");
            ApplyLighting(e, li);
        }

        void ApplyLighting(SceneEntry e, int li)
        {
            var L = e.loaded;
            e.lighting = li;
            CurrentLighting = li;
            for (int k = 0; k < L.lightings.Length; k++) L.lightings[k].group.SetActive(k == li);
            var LL = L.lightings[li];
            L.ApplyAtlas(li);
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = LL.ambientGamma;
            RenderSettings.ambientIntensity = 1f;
            DynamicGI.UpdateEnvironment();
            Player.worldCam.backgroundColor = LL.skyGamma;           // Himmel: Farbe × Stärke aus der Lichtszene
            Probe.backgroundColor = LL.skyGamma;
            Probe.RenderProbe();
            Player.SetLighting(e.data.LightingLabel(li), e.data.lightings.Length);
        }

        void Update()
        {
            var k = Keyboard.current;
            if (k == null) return;
            if (k.lKey.wasPressedThisFrame && _scenes.Count > 0) NextScene();
            if (k.nKey.wasPressedThisFrame) NextLighting();
            if (k.tKey.wasPressedThisFrame) ResetToStart();
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

        /// <summary>Bewegungsgefühl (0.10): Sprint, Zielen aus dem Stand, Sprint → Zielen – zum Prüfen von Sprint-Rhythmus und Visier-Anflug.</summary>
        public static ScriptedInput FeelScript() => new ScriptedInput()
            .Add(0.0f, 0.6f)                                                   // Ruhe
            .Add(0.6f, 2.4f, hold: "sprint", move: new Vector2(0, 1))          // Sprint
            .Add(2.4f, 3.2f)                                                   // Sprint-Ende, Hüfte
            .Add(3.2f, 4.6f, hold: "aim")                                      // Zielen aus dem Stand
            .Add(4.6f, 5.4f)                                                   // zurück zur Hüfte
            .Add(5.4f, 6.8f, hold: "sprint", move: new Vector2(0, 1))          // Sprint
            .Add(6.8f, 8.2f, hold: "aim")                                      // Sprint → Zielen
            .Add(8.2f, 9.0f);

        /// <summary>Pendeln (Frage 3.3): schnelle Drehung rechts, Ruhe, schnelle Drehung zurück, Ruhe – Rückkehr ohne Überschwingen.</summary>
        public static ScriptedInput SwayScript() => new ScriptedInput()
            .Add(0.0f, 0.5f)
            .Add(0.5f, 0.8f, lookPerS: new Vector2(360, 0))
            .Add(0.8f, 1.8f)
            .Add(1.8f, 2.1f, lookPerS: new Vector2(-360, 0))
            .Add(2.1f, 3.2f);

        /// <summary>Rückmeldung (Fragen 4.3, 7.1): Hüftschuss (nur Treffer-X), im Zielen Einzelschuss und Feuerstoß mit 720/min.</summary>
        public static ScriptedInput FeedbackScript() => new ScriptedInput()
            .Add(0.0f, 0.4f)
            .Add(0.4f, 0.43f, hold: "fire")
            .Add(0.9f, 3.4f, hold: "aim")
            .Add(1.6f, 1.65f, hold: "aim fire")              // ein Bild bei 30/s
            .Add(2.2f, 2.75f, hold: "aim fire")               // 7 Schüsse: 1 + 1 + 7 = 9 Patronen der Aufnahme
            .Add(3.4f, 4.0f);

        /// <summary>Hüft-Fadenkreuz (4.1 A): Hüfte → Hüftfeuer (geht auf) → Zielen (weg im 1. Bild) → Sprint („^“) → Nachladen (aus) → Hüfte.</summary>
        public static ScriptedInput HipScript() => new ScriptedInput()
            .Add(0.0f, 0.6f)                                                   // Ruhe an der Hüfte
            .Add(0.6f, 1.1f, hold: "fire")                                     // Hüftfeuer, 6 Schuss: Fadenkreuz geht auf
            .Add(1.1f, 1.8f)                                                   // klingt ab
            .Add(1.8f, 3.0f, hold: "aim")                                      // Zielen
            .Add(3.0f, 3.5f)                                                   // zurück zur Hüfte
            .Add(3.5f, 4.7f, hold: "sprint", move: new Vector2(0, 1))          // Sprint
            .Add(4.7f, 5.1f)                                                   // Hüfte
            .Add(5.1f, 5.2f, press: "reload")                                  // taktisches Nachladen
            .Add(5.2f, 8.0f);

        /// <summary>Sprint (0.15, 3.1 A): Sprint, Ende, zweiter Sprint und Sprint → Zielen (Zoom gegen Modell, 1d); 7,8 s.</summary>
        public static ScriptedInput SprintScript() => new ScriptedInput()
            .Add(0.0f, 0.5f)
            .Add(0.5f, 3.3f, hold: "sprint", move: new Vector2(0, 1))
            .Add(3.3f, 4.1f)
            .Add(4.1f, 5.9f, hold: "sprint", move: new Vector2(0, 1))
            .Add(5.9f, 7.1f, hold: "aim")
            .Add(7.1f, 7.8f);

        /// <summary>Waffenwechsel (0.15, 6.1 A): Q aus der Ruhe, nach dem Ziehen ein zweites Mal; Wegstecken, leere Sicht, Ziehen; 3,8 s.</summary>
        public static ScriptedInput SwitchScript() => new ScriptedInput()
            .Add(0.0f, 0.5f)
            .Add(0.5f, 0.55f, press: "swap")
            .Add(0.55f, 2.2f)
            .Add(2.2f, 2.25f, press: "swap")
            .Add(2.25f, 3.8f);

        /// <summary>Rückstoß (0.15, 5.1 A / 5.2 A): Viererstoß aus der Hüfte, dann im Zielen zwei Viererstöße und ein langer Stoß
        /// (12 Schuss); die Welt wandert, das Visier steht; 6,6 s.</summary>
        public static ScriptedInput RecoilScript() => new ScriptedInput()
            .Add(0.0f, 0.5f)
            .Add(0.5f, 0.8f, hold: "fire")
            .Add(1.5f, 6.0f, hold: "aim")
            .Add(2.3f, 2.6f, hold: "aim fire")
            .Add(3.3f, 3.6f, hold: "aim fire")
            .Add(4.3f, 5.25f, hold: "aim fire")
            .Add(6.0f, 6.6f);

        /// <summary>Beleg 0.16 (5.3 A / 5.4 A): Mündungsfeuer und Hülsen aus der Hüfte (Einzelschuss, Feuerstoß) und im Zielen (zwei
        /// Einzelschüsse, Feuerstoß) vor der 10-m-Mitte, 7,4 s.</summary>
        public static ScriptedInput FireScript() => new ScriptedInput()
            .Add(0.0f, 0.4f)
            .Add(0.4f, 0.45f, hold: "fire")
            .Add(1.0f, 1.45f, hold: "fire")
            .Add(2.2f, 7.0f, hold: "aim")
            .Add(3.0f, 3.05f, hold: "aim fire")
            .Add(3.8f, 3.85f, hold: "aim fire")
            .Add(4.6f, 5.5f, hold: "aim fire")
            .Add(7.0f, 7.4f);

        IEnumerator Capture(string dir)
        {
            Directory.CreateDirectory(dir);
            Player.hud = false;
            string dn = Arg(Environment.GetCommandLineArgs(), "-ballonDemo");
            var demo = dn == "feel" ? FeelScript() : dn == "sway" ? SwayScript() : dn == "treffer" ? FeedbackScript() : dn == "huefte" ? HipScript()
                     : dn == "sprint" ? SprintScript() : dn == "wechsel" ? SwitchScript() : dn == "rueckstoss" ? RecoilScript() : dn == "feuer" ? FireScript() : DemoScript();
            Player.input = demo;
            Player.C.ReadyNow();
            Player.C.ammo = dn == "rueckstoss" || dn == "feuer" ? Player.C.magSize : 9;
            float fps = float.TryParse(Arg(Environment.GetCommandLineArgs(), "-ballonFps") ?? "", out var fp) ? fp : 30f;   // Messläufe: 60
            float dt = 1f / fps;
            Player.deltaOverride = () => dt;
            string sc = Arg(Environment.GetCommandLineArgs(), "-ballonScene");      // Aufnahme in einer Szene statt im Parcours
            int si = -1;
            for (int i = 0; i < SceneCount; i++) if (_scenes[i].data.name == sc) si = i;
            if (si >= 0)
            {
                ShowScene(si);
                for (int k = 0; k < 10; k++) yield return null;
                var L = LoadedSceneAt(si);
                Player.Teleport(L.spawnPos, L.spawnYaw, 1.5f);
            }
            else if (dn == "sway" || dn == "treffer" || dn == "huefte" || dn == "rueckstoss" || dn == "wechsel" || dn == "feuer") Player.Teleport(new Vector3(0f, 0.01f, 1.6f), 0f, 0.8f);   // vor die 10-m-Mitte
            else Player.Teleport(new Vector3(0.6f, 0.01f, 1.6f), -4f, 1.5f);
            var rt = HdrTarget(1280, 720, 4);
            Player.worldCam.targetTexture = rt;
            bool key = Arg(Environment.GetCommandLineArgs(), "-ballonKey") != null;
            if (key)                                                                 // Messlauf: nur Waffe und Arme auf Magenta
            {
                Player.worldCam.cullingMask = 0;
                Player.worldCam.clearFlags = CameraClearFlags.SolidColor;
                Player.worldCam.backgroundColor = new Color(1, 0, 1);
            }
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
                if (!key) Player.StampFeedback(tex);          // Messlauf ohne Fadenkreuz-Stempel: die Maske zeigt nur Waffe und Arme
                File.WriteAllBytes(Path.Combine(dir, $"{i:0000}.png"), tex.EncodeToPNG());
                File.AppendAllText(Path.Combine(dir, "frames.csv"), $"{i},{Player.C.ActionName},{Player.C.Frame:0.0},{Player.C.ammo}\n");
                File.AppendAllText(Path.Combine(dir, "feedback.csv"), FormattableString.Invariant(
                    $"{i},{Player.C.SwayDeg.x:0.000},{Player.C.SwayDeg.y:0.000},{(Player.ShotRingVisible ? 1 : 0)},{(Player.HitXVisible ? 1 : 0)},{Player.hits},{(Player.HipVisible ? 1 : 0)},{Player.hipReticle.Reason},{Player.hipReticle.spread:0.000},{Player.hipReticle.ExtentPx(720):0.0}\n"));
                File.AppendAllText(Path.Combine(dir, "zoom.csv"), $"{i},{Player.C.adsWeight:0.0000},{Player.worldCam.fieldOfView:0.000}\n");
            }
            File.WriteAllLines(Path.Combine(dir, "markers.csv"), markers);
            Debug.Log($"[Ballon] Aufnahme: {n} Bilder in {dir}");
            Application.Quit();
        }

        int _f0;

        /// <summary>Vorführlauf durch den Parcours der Szene (RouteRunner), 1280 × 720 bei 30 Bildern/s; je Bild Laufzeit, Kontrollpunkte
        /// und Treffer in frames.csv (für die Beschriftung in unity_run.py course).</summary>
        IEnumerator CourseCapture(string dir, string scene, string lighting)
        {
            Directory.CreateDirectory(dir);
            int si = -1;
            for (int i = 0; i < SceneCount; i++) if (_scenes[i].data.name == scene) si = i;
            if (si >= 0) ShowScene(si);                                               // lädt die Szene beim ersten Zeigen
            var L = si >= 0 ? LoadedSceneAt(si) : null;
            if (L?.course == null || L.data.course.route == null)
            {
                Debug.LogError($"[Ballon] Szene {scene} hat keinen Parcours");
                Application.Quit(1);
                yield break;
            }
            int li = 0;
            for (int k = 0; k < L.data.lightings.Length; k++) if (L.data.lightings[k].name == lighting) li = k;
            ShowLighting(li);
            Player.hud = false;
            Player.C.ReadyNow();
            Player.Teleport(L.spawnPos, L.spawnYaw, 4f);
            for (int k = 0; k < 10; k++) yield return null;
            var route = new List<Vector3>();
            foreach (var b in L.data.course.route) route.Add(SceneConvert.Point(b));
            var runner = new RouteRunner(Player, route, L.targets.targets);
            Player.input = runner;
            const float dt = 1f / 30f;
            Player.deltaOverride = () => dt;
            var rt = HdrTarget(1280, 720, 4);
            Player.worldCam.targetTexture = rt;
            var tex = new Texture2D(1280, 720, TextureFormat.RGB24, false);
            string result = "";
            L.course.Result += m => result = m;
            string key = CourseRun.PrefsKey(L.data.name);                            // Vorführlauf ändert die Bestzeit des Spielers nicht
            bool hadBest = PlayerPrefs.HasKey(key);
            float best = PlayerPrefs.GetFloat(key, 0f);
            Player.enabled = false;
            var csv = new System.Text.StringBuilder();
            int n = 0, after = -1;
            while (n < 120 * 30 && (after < 0 || n < after))
            {
                Player.Step(dt);
                yield return new WaitForEndOfFrame();
                ReadBack(rt, tex);
                File.WriteAllBytes(Path.Combine(dir, $"{n:0000}.png"), tex.EncodeToPNG());
                var c = L.course;
                csv.Append(FormattableString.Invariant($"{n},{c.State},{c.Elapsed:0.00},{c.CheckpointsDone}/{c.CheckpointCount},{c.TargetsHit}/{c.TargetCount},{runner.Waypoint}/{route.Count}\n"));
                n++;
                if (after < 0 && (c.RunsFinished > 0 || runner.Done)) after = n + 45;       // 1,5 s Auslauf
            }
            if (hadBest) PlayerPrefs.SetFloat(key, best); else PlayerPrefs.DeleteKey(key);
            PlayerPrefs.Save();
            File.WriteAllText(Path.Combine(dir, "frames.csv"), csv.ToString());
            File.WriteAllText(Path.Combine(dir, "result.txt"), $"{result}\nlicht={L.data.lightings[li].name}\n");
            Debug.Log($"[Ballon] Parcourslauf: {n} Bilder in {dir} · {result}");
            Application.Quit(L.course.LastValid ? 0 : 2);
        }

        /// <summary>Je Szene ein Bild vom Startpunkt (1600 × 900, ohne Viewmodel) wie das Blender-Referenzbild, dazu eins mit Waffe.</summary>
        IEnumerator SceneShots(string dir)
        {
            Directory.CreateDirectory(dir);
            Player.hud = false;
            Player.C.ReadyNow();
            var cam = Player.worldCam;
            var rt = HdrTarget(1600, 900, 8);
            cam.targetTexture = rt;
            var tex = new Texture2D(1600, 900, TextureFormat.RGB24, false);
            for (int i = 0; i < SceneCount; i++)
            {
                ShowScene(i);
                Player.input = new ScriptedInput().Add(0, 100);
                for (int li = 0; li < LightingCount; li++)           // je Lichtszene ein Paar <szene>_<licht>_…, wie das Blender-Referenzbild <szene>_<licht>_ref.png
                {
                    ShowLighting(li);
                    for (int k = 0; k < 20; k++) yield return null;      // Sonde, Spieler steht
                    var sp = LoadedSceneAt(i).spawnPos;
                    Player.Teleport(sp, LoadedSceneAt(i).spawnYaw, 0);
                    cam.fieldOfView = Player.viewCam.fieldOfView = Camera.HorizontalToVerticalFieldOfView(D.camera.h_fov_deg, 16f / 9f);
                    int vmMask = Player.viewCam.cullingMask;
                    string stem = $"{_scenes[i].data.name}_{_scenes[i].data.lightings[li].name}";
                    foreach (var withVm in new[] { false, true })
                    {
                        Player.viewCam.cullingMask = withVm ? vmMask : 0;   // Kamera bleibt an: an ihr hängt der AgX-Durchgang
                        if (LoadedSceneAt(i).routeMarkers != null) LoadedSceneAt(i).routeMarkers.SetActive(withVm);   // Wegpfeile gibt es in Blender nicht
                        yield return new WaitForEndOfFrame();
                        yield return new WaitForEndOfFrame();
                        ReadBack(rt, tex);
                        File.WriteAllBytes(Path.Combine(dir, $"{stem}_{(withVm ? "waffe" : "umgebung")}.png"), tex.EncodeToPNG());
                    }
                    Player.viewCam.cullingMask = vmMask;
                }
            }
            Debug.Log($"[Ballon] Szenenbilder in {dir}");
            Application.Quit();
        }

        /// <summary>Jeder Skin einmal in der Haltung hip und inspect_l im Studiolicht (Beleg Skins).</summary>
        IEnumerator SkinSheet(string dir)
        {
            Directory.CreateDirectory(dir);
            Player.hud = false;
            Player.enabled = false;
            RangeRoot.gameObject.SetActive(false);
            Sun.enabled = false;
            RenderSettings.fog = false;
            var cam = Player.worldCam;
            StudioLike(cam);
            yield return null;
            yield return null;
            var rt = HdrTarget(1280, 720, 8);
            cam.targetTexture = rt;
            cam.fieldOfView = Player.viewCam.fieldOfView = Camera.HorizontalToVerticalFieldOfView(D.camera.h_fov_deg, 16f / 9f);
            var tex = new Texture2D(1280, 720, TextureFormat.RGB24, false);
            for (int i = 0; i < skinMaterials.Length; i++)
            {
                Player.SetSkin(i);
                foreach (var pose in new[] { "hip", "inspect_l" })
                {
                    Player.rig.Apply(S.Evaluate(S.StillAction(pose), 0, new EgoState()));
                    yield return new WaitForEndOfFrame();
                    ReadBack(rt, tex);
                    File.WriteAllBytes(Path.Combine(dir, $"{i:00}_{D.textures.skins[i].name}_{pose}.png"), tex.EncodeToPNG());
                }
            }
            Debug.Log($"[Ballon] Skins in {dir}");
            Application.Quit();
        }

        /// <summary>HDR-Ziel (Half, linear): URP übernimmt das Zielformat für den Zwischenpuffer, ein 8-Bit-Ziel schnitte vor AgX bei 1 ab.</summary>
        public static RenderTexture HdrTarget(int w, int h, int aa) =>
            new RenderTexture(w, h, 24, RenderTextureFormat.ARGBHalf, RenderTextureReadWrite.Linear) { antiAliasing = aa };

        /// <summary>HDR-Ziel (nach AgX: Anzeige-linear ≤ 1) → sRGB-kodierte Pixel in `tex` (RGB24).</summary>
        public static void ReadBack(RenderTexture hdr, Texture2D tex)
        {
            var prev = RenderTexture.active;
            var ldr = RenderTexture.GetTemporary(hdr.width, hdr.height, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
            try
            {
                Graphics.Blit(hdr, ldr);
                RenderTexture.active = ldr;
                tex.ReadPixels(new Rect(0, 0, hdr.width, hdr.height), 0, 0);
                tex.Apply();
            }
            finally
            {
                RenderTexture.active = prev;
                RenderTexture.ReleaseTemporary(ldr);
            }
        }

        /// <summary>Leistung im Parcours: Vorführablauf in Echtzeit ohne VSync, Bildzeiten (ms) nach `file` (Mittel, 95-, 99-Perzentil).</summary>
        /// <summary>Bildzeiten über 10 s: im Parcours der Vorführablauf, in einer Szene (-ballonScene) der Vorführlauf durch ihren
        /// Parcours, dabei alle 2,5 s die nächste Lichtszene (Umschalten zählt mit).</summary>
        IEnumerator Bench(string file, string scene)
        {
            QualitySettings.vSyncCount = 0;
            Application.targetFrameRate = -1;
            Player.hud = true;
            Player.C.ReadyNow();
            Player.C.ammo = 9;
            Player.input = DemoScript();
            LoadedScene L = null;
            for (int i = 0; i < SceneCount; i++)
                if (_scenes[i].data.name == scene) { ShowScene(i); L = LoadedSceneAt(i); }
            if (L != null)
            {
                Player.Teleport(L.spawnPos, L.spawnYaw, 4f);
                if (L.data.course?.route != null)
                {
                    var route = new List<Vector3>();
                    foreach (var b in L.data.course.route) route.Add(SceneConvert.Point(b));
                    Player.input = new RouteRunner(Player, route, L.targets.targets);
                }
            }
            for (int i = 0; i < 30; i++) yield return null;      // Aufwärmen
            var ms = new List<float>();
            float t = 0;
            int lit = 0;
            while (t < 10f)
            {
                yield return null;
                ms.Add(Time.unscaledDeltaTime * 1000f);
                t += Time.unscaledDeltaTime;
                if (L != null && t > 2.5f * (lit + 1) && L.data.lightings.Length > 1) ShowLighting(++lit % L.data.lightings.Length);
            }
            ms.Sort();
            float mean = 0;
            foreach (var v in ms) mean += v;
            mean /= ms.Count;
            var I = System.Globalization.CultureInfo.InvariantCulture;
            File.WriteAllText(file, string.Format(I, "{{\"frames\": {0}, \"mean_ms\": {1:0.00}, \"p95_ms\": {2:0.00}, \"p99_ms\": {3:0.00}, " +
                "\"width\": {4}, \"height\": {5}, \"gpu\": \"{6}\", \"scene\": \"{7}\", \"max_ms\": {8:0.00}}}\n", ms.Count, mean, ms[(int)(ms.Count * 0.95f)],
                ms[(int)(ms.Count * 0.99f)], Screen.width, Screen.height, SystemInfo.graphicsDeviceName, L?.data.name ?? "parcours", ms[ms.Count - 1]));
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
            // Maske von Waffe und Armen (weiß auf schwarz) für Kennzahlen nur über dem Viewmodel
            var white = new Material(backdrop);
            white.SetColor("_BaseColor", Color.white);
            white.SetTexture("_BaseMap", Texture2D.whiteTexture);
            foreach (var r in Player.rig.space.GetComponentsInChildren<Renderer>(true))
            {
                var ms = r.sharedMaterials;
                for (int k = 0; k < ms.Length; k++) ms[k] = white;
                r.sharedMaterials = ms;
            }
            cam.cullingMask = 0;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = Color.black;
            foreach (var pose in new[] { "hip", "ads", "reload", "inspect_r" })
            {
                Player.rig.Apply(S.Evaluate(S.StillAction(pose), 0, new EgoState()));
                yield return new WaitForEndOfFrame();
                ReadBack(rt, tex);
                File.WriteAllBytes(Path.Combine(dir, $"{pose}_mask.png"), tex.EncodeToPNG());
            }
            Debug.Log($"[Ballon] Vergleichsbilder in {dir}");
            Application.Quit();
        }
    }
}
