// Projekt einrichten und bauen (Stapelbetrieb):
//   Unity -batchmode -quit -projectPath unity -executeMethod Ballon.Ego.Editor.BallonSetup.Run      (URP, Ebene, Eingabe, Materialien, Szene)
//   Unity -batchmode -quit -projectPath unity -executeMethod Ballon.Ego.Editor.BallonSetup.BuildMac (Entwicklungsbuild macOS)
// Alles hier ist erzeugt; Daten kommen aus Assets/Ballon/Generated (tools/export_unity.py).
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Ballon.Ego.Editor
{
    public sealed class BallonModelImport : AssetPostprocessor
    {
        /// <summary>Gebackene Atlanten und LUT aus Blender: Farbe sRGB, Masken und Normale linear, LUT ohne Mips und Kompression.</summary>
        void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith("Assets/Ballon/Generated/Textures/")) return;
            var ti = (TextureImporter)assetImporter;
            var f = Path.GetFileNameWithoutExtension(assetPath);
            ti.maxTextureSize = 4096;
            ti.textureCompression = TextureImporterCompression.CompressedHQ;
            ti.sRGBTexture = f.EndsWith("_albedo") || f.EndsWith("_spec");   // Spiegelfarbe ist eine Farbe (sRGB), Alpha bleibt linear
            ti.textureType = f.EndsWith("_normal") ? TextureImporterType.NormalMap : TextureImporterType.Default;
            ti.alphaSource = f.EndsWith("_spec") ? TextureImporterAlphaSource.FromInput : TextureImporterAlphaSource.None;
            ti.anisoLevel = 8;
            ti.mipmapEnabled = true;
            if (f == "agx_lut")
            {
                ti.sRGBTexture = false;          // Werte sind Anzeige-sRGB, der Shader dekodiert selbst
                ti.mipmapEnabled = false;
                ti.textureCompression = TextureImporterCompression.Uncompressed;
                ti.npotScale = TextureImporterNPOTScale.None;
                ti.wrapMode = TextureWrapMode.Clamp;
                ti.filterMode = FilterMode.Bilinear;
                ti.anisoLevel = 0;
                ti.isReadable = true;            // EditMode-Test liest Gitterpunkte
            }
        }

        void OnPreprocessModel()
        {
            if (!assetPath.StartsWith("Assets/Ballon/Generated/")) return;
            var mi = (ModelImporter)assetImporter;
            BallonSetup.Configure(mi);
        }

        /// <summary>Lage der Knoten aus ego.json statt aus dem FBX: Mit „Apply Transform“ (bake_space_transform) kommen die Netze
        /// richtig umgerechnet an (EditMode-Test FBX_Import_passt_zur_Achsumrechnung), die Lagen der Kindknoten der Waffe aber nicht
        /// (gemessen beim ersten Import: bis 90° Drehung am Magazin, bis 218 mm Versatz). In Blender sind alle Teile und Anker
        /// ungedreht und ihre Ruhelagen reine Verschiebungen; das Protokoll nennt die Abweichung bei jedem Import.</summary>
        void OnPostprocessModel(GameObject g)
        {
            if (!assetPath.StartsWith("Assets/Ballon/Generated/")) return;
            var json = System.IO.Path.Combine(System.IO.Path.GetDirectoryName(assetPath), "ego.json");
            if (!System.IO.File.Exists(json)) return;
            var D = EgoFile.Parse(System.IO.File.ReadAllText(json));
            var at = new Dictionary<string, Vector3>();       // Lage im Waffenrahmen (Blender, m)
            foreach (var p in D.weapon.parts) at[p.id] = BMath.V(p.rest);
            foreach (var a in D.weapon.anchors) at[a.id] = BMath.V(a.pos);
            int n = 0;
            float maxRot = 0, maxPos = 0;
            string worst = "";
            foreach (var t in g.GetComponentsInChildren<Transform>(true))
            {
                if (t == g.transform) continue;
                var before = (t.localPosition, t.localRotation);
                at.TryGetValue(t.name, out var self);
                var par = t.parent != null && t.parent != g.transform && at.TryGetValue(t.parent.name, out var pp) ? pp : Vector3.zero;
                t.localPosition = D.toUnity.MultiplyVector(self - par);
                t.localRotation = Quaternion.identity;
                t.localScale = Vector3.one;
                float dr = Quaternion.Angle(before.Item2, Quaternion.identity), dp = Vector3.Distance(before.Item1, t.localPosition);
                if (dr > maxRot) { maxRot = dr; worst = t.name; }
                maxPos = Mathf.Max(maxPos, dp);
                n++;
            }
            Debug.Log($"[Ballon] {assetPath}: {n} Knoten aus ego.json gesetzt (FBX wich ab: Drehung bis {maxRot:0.0}° bei {worst}, Lage bis {maxPos * 1000:0.0} mm)");
        }
    }

    public static class BallonSetup
    {
        public const string Gen = "Assets/Ballon/Generated";
        public const string Settings = "Assets/Ballon/Settings";
        public const string ScenePath = "Assets/Ballon/Scenes/Firstfeel.unity";
        public const string BuildPath = "Build/BallonFirstfeel.app";

        public static void Configure(ModelImporter mi)
        {
            mi.globalScale = 1f;
            mi.useFileScale = true;
            mi.bakeAxisConversion = false;
            mi.preserveHierarchy = true;
            mi.sortHierarchyByName = false;
            mi.materialImportMode = ModelImporterMaterialImportMode.None;
            mi.importAnimation = false;
            mi.animationType = ModelImporterAnimationType.None;
            mi.importCameras = false;
            mi.importLights = false;
            mi.importVisibility = false;
            mi.importBlendShapes = false;
            mi.importNormals = ModelImporterNormals.Import;
            mi.importTangents = ModelImporterTangents.CalculateMikk;
            mi.meshCompression = ModelImporterMeshCompression.Off;
            mi.isReadable = true;           // Tests lesen Netzgrenzen
            mi.addCollider = false;
        }

        [MenuItem("Ballon/Projekt einrichten")]
        public static void Run()
        {
            Directory.CreateDirectory(Settings);
            Directory.CreateDirectory(Gen + "/Materials");
            Directory.CreateDirectory("Assets/Ballon/Scenes");
            Pipeline();
            Layer();
            Player();
            foreach (var f in new[] { "BASIC-01-v2.1.fbx", "arms.fbx" })
            {
                var mi = (ModelImporter)AssetImporter.GetAtPath($"{Gen}/{f}");
                if (mi == null) throw new FileNotFoundException($"{Gen}/{f} fehlt – zuerst tools/export_unity.py");
                Configure(mi);
                mi.SaveAndReimport();
            }
            var mats = Materials();
            Scene(mats);
            AssetDatabase.SaveAssets();
            Debug.Log("[Ballon] Projekt eingerichtet");
        }

        static void Pipeline()
        {
            var path = Settings + "/URP.asset";
            var urp = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(path);
            if (urp == null)
            {
                var rd = ScriptableObject.CreateInstance<UniversalRendererData>();
                AssetDatabase.CreateAsset(rd, Settings + "/URP_Renderer.asset");
                urp = UniversalRenderPipelineAsset.Create(rd);
                AssetDatabase.CreateAsset(urp, path);
            }
            urp.msaaSampleCount = 4;
            urp.shadowDistance = 70f;
            urp.supportsHDR = true;                    // 0.7: lineares HDR bis zur AgX-Abbildung am Ende des Stapels
            urp.supportsCameraDepthTexture = false;
            foreach (var rd in new ScriptableRendererData[] { AssetDatabase.LoadAssetAtPath<UniversalRendererData>(Settings + "/URP_Renderer.asset") })
                if (rd is UniversalRendererData ud)
                {
                    ud.intermediateTextureMode = IntermediateTextureMode.Always;   // HDR-Zwischenpuffer, sonst Abschneiden bei 1 vor AgX
                    EditorUtility.SetDirty(ud);
                }
            var su = new SerializedObject(urp);
            Set(su, "m_AdditionalLightsRenderingMode", 1);      // Per Pixel
            Set(su, "m_AdditionalLightShadowsSupported", 1);
            Set(su, "m_AdditionalLightsShadowmapResolution", 2048);
            Set(su, "m_SoftShadowsSupported", 1);
            Set(su, "m_MainLightShadowmapResolution", 2048);
            // zweiter Renderer „Out“ für die Viewmodel-Kamera (letzte im Stapel): Vollbild-AgX wie Blender
            var outPath = Settings + "/URP_Renderer_Out.asset";
            var outRd = AssetDatabase.LoadAssetAtPath<UniversalRendererData>(outPath);
            if (outRd == null)
            {
                outRd = ScriptableObject.CreateInstance<UniversalRendererData>();
                AssetDatabase.CreateAsset(outRd, outPath);
            }
            outRd.intermediateTextureMode = IntermediateTextureMode.Always;
            var agxMat = Agx();
            var feat = outRd.rendererFeatures.OfType<FullScreenPassRendererFeature>().FirstOrDefault();
            if (feat == null)
            {
                feat = ScriptableObject.CreateInstance<FullScreenPassRendererFeature>();
                feat.name = "AgX";
                AssetDatabase.AddObjectToAsset(feat, outRd);
                outRd.rendererFeatures.Add(feat);
            }
            feat.passMaterial = agxMat;
            feat.injectionPoint = FullScreenPassRendererFeature.InjectionPoint.BeforeRenderingPostProcessing;
            feat.fetchColorBuffer = true;
            feat.SetActive(true);
            EditorUtility.SetDirty(feat);
            EditorUtility.SetDirty(outRd);
            AssetDatabase.SaveAssets();
            var so = new SerializedObject(outRd);
            var map = so.FindProperty("m_RendererFeatureMap");
            map.arraySize = outRd.rendererFeatures.Count;
            for (int i = 0; i < outRd.rendererFeatures.Count; i++)
                if (AssetDatabase.TryGetGUIDAndLocalFileIdentifier(outRd.rendererFeatures[i], out _, out long id))
                    map.GetArrayElementAtIndex(i).longValue = id;
            so.ApplyModifiedPropertiesWithoutUndo();
            var list = su.FindProperty("m_RendererDataList");
            if (list.arraySize < 2) list.arraySize = 2;
            list.GetArrayElementAtIndex(OutRenderer).objectReferenceValue = outRd;
            su.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(urp);
            GraphicsSettings.defaultRenderPipeline = urp;
            var names = QualitySettings.names;
            int cur = QualitySettings.GetQualityLevel();
            for (int i = 0; i < names.Length; i++)
            {
                QualitySettings.SetQualityLevel(i, false);
                QualitySettings.renderPipeline = urp;
            }
            QualitySettings.SetQualityLevel(cur, false);
        }

        public const int OutRenderer = 1;

        static void Set(SerializedObject so, string prop, int v)
        {
            var p = so.FindProperty(prop);
            if (p == null) { Debug.LogWarning($"[Ballon] URP-Einstellung {prop} fehlt"); return; }
            if (p.propertyType == SerializedPropertyType.Boolean) p.boolValue = v != 0; else p.intValue = v;
        }

        /// <summary>Material des AgX-Durchgangs mit der LUT aus Blender (tools/bake_unity.agx_lut).</summary>
        static Material Agx()
        {
            var path = $"{Gen}/Materials/Post_AgX.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (m == null)
            {
                m = new Material(Shader.Find("Ballon/AgX")) { name = "Post_AgX" };
                AssetDatabase.CreateAsset(m, path);
            }
            var D = EgoFile.Parse(File.ReadAllText($"{Gen}/ego.json"));
            var L = D.textures.lut;
            m.SetTexture("_Lut", AssetDatabase.LoadAssetAtPath<Texture2D>($"{Gen}/Textures/{L.file}"));
            m.SetVector("_LutParams", new Vector4(L.size, L.ev[0], L.ev[1], L.mid_grey));
            EditorUtility.SetDirty(m);
            return m;
        }

        static void Layer()
        {
            var tm = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/TagManager.asset")[0]);
            var layers = tm.FindProperty("layers");
            layers.GetArrayElementAtIndex(Bootstrap.ViewmodelLayer).stringValue = "Viewmodel";
            tm.ApplyModifiedProperties();
        }

        static void Player()
        {
            PlayerSettings.companyName = "Ballon";
            PlayerSettings.productName = "BALLON Firstfeel";
            PlayerSettings.colorSpace = ColorSpace.Linear;
            PlayerSettings.fullScreenMode = FullScreenMode.Windowed;
            PlayerSettings.defaultScreenWidth = 1280;
            PlayerSettings.defaultScreenHeight = 720;
            PlayerSettings.resizableWindow = true;
            PlayerSettings.runInBackground = true;
            PlayerSettings.SetApplicationIdentifier(UnityEditor.Build.NamedBuildTarget.Standalone, "local.ballon.firstfeel");
            var ps = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/ProjectSettings.asset")[0]);
            var ih = ps.FindProperty("activeInputHandler");
            if (ih != null) ih.intValue = 1;       // nur Input System
            ps.ApplyModifiedProperties();
        }

        static Color Hex(string h)
        {
            ColorUtility.TryParseHtmlString(h, out var c);
            return c;
        }

        static Material Lit(string name, Color c, float smooth, float metal)
        {
            var path = $"{Gen}/Materials/{name}.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (m == null)
            {
                m = new Material(Shader.Find("Universal Render Pipeline/Lit")) { name = name };
                AssetDatabase.CreateAsset(m, path);
            }
            m.SetColor("_BaseColor", c);
            m.SetFloat("_Smoothness", smooth);
            m.SetFloat("_Metallic", metal);
            EditorUtility.SetDirty(m);
            return m;
        }

        static void Transparent(Material m, float alpha)
        {
            var c = m.GetColor("_BaseColor");
            c.a = alpha;
            m.SetColor("_BaseColor", c);
            m.SetFloat("_Surface", 1);
            m.SetFloat("_Blend", 0);
            m.SetFloat("_ZWrite", 0);
            m.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
            m.SetFloat("_DstBlend", (float)BlendMode.OneMinusSrcAlpha);
            m.SetFloat("_SrcBlendAlpha", (float)BlendMode.One);
            m.SetFloat("_DstBlendAlpha", (float)BlendMode.OneMinusSrcAlpha);
            m.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
            m.renderQueue = (int)RenderQueue.Transparent;
            m.SetOverrideTag("RenderType", "Transparent");
        }

        static void Emission(Material m, Color c)
        {
            m.EnableKeyword("_EMISSION");
            m.globalIlluminationFlags = MaterialGlobalIlluminationFlags.None;
            m.SetColor("_EmissionColor", c);
        }

        /// <summary>URP Lit je Materialrolle aus ego.json (Farbe im AAA-Modus, Rauheit → Glätte, Metall), dazu Parcours-Materialien.</summary>
        static Dictionary<string, Material> Materials()
        {
            var D = EgoFile.Parse(File.ReadAllText($"{Gen}/ego.json"));
            var res = new Dictionary<string, Material>();
            foreach (var r in D.roles)
            {
                var m = Lit("Role_" + r.role, Hex(r.aaa_color), 1f - r.rough, r.metal);
                if (r.alpha < 1f) { m.SetFloat("_Smoothness", 0.96f); Transparent(m, 0.12f); }
                if (r.emit > 0f)          // wie kit.aaa_nodes: Stärke emit · 1,6, reine Leuchtteile ohne beleuchtete Grundfarbe
                {
                    Emission(m, Color.black);
                    var e = Hex(r.color).linear * (r.emit * 1.6f);
                    m.SetColor("_EmissionColor", new Color(e.r, e.g, e.b, 1).gamma);   // Materialfarben sind Gamma-Werte
                    if (r.emit_only) m.SetColor("_BaseColor", Color.black);
                }
                res["Role_" + r.role] = m;
            }
            foreach (var (key, A) in new[] { ("weapon", D.textures.weapon), ("arms", D.textures.arms) })   // 0.7: gebackene Atlanten
            {
                var m = Lit("Atlas_" + key, Color.white, 1f, 0f);
                Texture2D T(string f) => AssetDatabase.LoadAssetAtPath<Texture2D>($"{Gen}/Textures/{f}");
                m.SetTexture("_BaseMap", T(A.albedo));                 // Diffusfarbe = Grundfarbe · (1 − Metall)
                m.SetFloat("_WorkflowMode", 0f);                         // Spezular: Spiegelfarbe je Pixel wie Blender
                m.EnableKeyword("_SPECULAR_SETUP");
                m.SetTexture("_SpecGlossMap", T(A.spec));
                m.SetColor("_SpecColor", Color.white);
                m.SetFloat("_SmoothnessTextureChannel", 0f);             // Glätte im Alpha der Spiegelkarte
                m.SetTexture("_BumpMap", T(A.normal));
                m.SetTexture("_OcclusionMap", T(A.ao));
                m.SetFloat("_OcclusionStrength", 1f);
                m.SetFloat("_BumpScale", 1f);
                m.EnableKeyword("_METALLICSPECGLOSSMAP");
                m.EnableKeyword("_NORMALMAP");
                m.EnableKeyword("_OCCLUSIONMAP");
                res["Atlas_" + key] = m;
            }
            var bd = AssetDatabase.LoadAssetAtPath<Material>($"{Gen}/Materials/Studio_Backdrop.mat");
            if (bd == null)
            {
                bd = new Material(Shader.Find("Universal Render Pipeline/Unlit")) { name = "Studio_Backdrop" };
                AssetDatabase.CreateAsset(bd, $"{Gen}/Materials/Studio_Backdrop.mat");
            }
            res["backdrop"] = bd;
            res["floor"] = Lit("Range_Floor", Hex("#8A8E94"), 0.12f, 0);
            res["wall"] = Lit("Range_Wall", Hex("#A4A8AE"), 0.08f, 0);
            res["cover"] = Lit("Range_Cover", Hex("#6F747B"), 0.15f, 0);
            res["target"] = Lit("Range_Target", Hex("#E9E5DC"), 0.2f, 0);
            res["ring"] = Lit("Range_TargetRing", Hex("#E0651E"), 0.3f, 0);
            var fl = Lit("Range_Flash", Hex("#FFB070"), 0.3f, 0);
            Emission(fl, Hex("#FF8A3C") * 1.5f);
            res["flash"] = fl;
            res["post"] = Lit("Range_Post", Hex("#3A3D42"), 0.3f, 0.2f);
            res["decal"] = Lit("Range_Decal", Hex("#1E1F22"), 0.05f, 0);
            AssetDatabase.SaveAssets();
            return res;
        }

        static void Scene(Dictionary<string, Material> mats)
        {
            var sc = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var go = new GameObject("Firstfeel");
            var b = go.AddComponent<Bootstrap>();
            b.egoJson = AssetDatabase.LoadAssetAtPath<TextAsset>($"{Gen}/ego.json");
            b.weaponModel = AssetDatabase.LoadAssetAtPath<GameObject>($"{Gen}/BASIC-01-v2.1.fbx");
            b.armsModel = AssetDatabase.LoadAssetAtPath<GameObject>($"{Gen}/arms.fbx");
            b.roleMaterials = mats.Where(kv => kv.Key.StartsWith("Role_") || kv.Key.StartsWith("Atlas_")).Select(kv => kv.Value).ToArray();
            b.backdrop = mats["backdrop"];
            b.floor = mats["floor"];
            b.wall = mats["wall"];
            b.cover = mats["cover"];
            b.target = mats["target"];
            b.targetRing = mats["ring"];
            b.flash = mats["flash"];
            b.post = mats["post"];
            b.decal = mats["decal"];
            EditorSceneManager.SaveScene(sc, ScenePath);
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
        }

        [MenuItem("Ballon/macOS-Build")]
        public static void BuildMac()
        {
            var opt = new BuildPlayerOptions
            {
                scenes = new[] { ScenePath },
                locationPathName = BuildPath,
                target = BuildTarget.StandaloneOSX,
                options = BuildOptions.Development,
            };
            var rep = BuildPipeline.BuildPlayer(opt);
            Debug.Log($"[Ballon] Build {rep.summary.result}: {rep.summary.totalSize / 1e6:0.0} MB, {rep.summary.totalErrors} Fehler → {BuildPath}");
            if (rep.summary.result != BuildResult.Succeeded) EditorApplication.Exit(1);
        }
    }
}
