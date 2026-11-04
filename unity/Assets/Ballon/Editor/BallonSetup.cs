// Projekt einrichten und bauen (Stapelbetrieb):
//   Unity -batchmode -quit -projectPath unity -executeMethod Ballon.Ego.Editor.BallonSetup.Run      (URP, Ebene, Eingabe, Materialien, Szene)
//   Unity -batchmode -quit -projectPath unity -executeMethod Ballon.Ego.Editor.BallonSetup.BuildMac (Entwicklungsbuild macOS)
//   Unity -batchmode -quit -projectPath unity -executeMethod Ballon.Ego.Editor.BallonSetup.AttachWarmup (Shader-Zustände in die Szene, 0.38)
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
            if (assetPath.StartsWith("Assets/Ballon/Generated/Scenes/") && assetPath.EndsWith(".png") && !assetPath.EndsWith("_ref.png") && !assetPath.EndsWith("_view.png"))
            {
                var li = (TextureImporter)assetImporter;     // Lichtatlas einer Zone und Lichtszene (ballon-scene/2; nicht Referenzbild _ref, nicht _view): sRGB-Farbe, im Shader unbeleuchtet
                li.textureType = TextureImporterType.Default;
                li.sRGBTexture = true;
                li.alphaSource = TextureImporterAlphaSource.None;
                li.maxTextureSize = 4096;
                li.textureCompression = TextureImporterCompression.CompressedHQ;
                li.mipmapEnabled = true;
                li.anisoLevel = 8;
                li.wrapMode = TextureWrapMode.Clamp;
                return;
            }
            if (!assetPath.StartsWith("Assets/Ballon/Generated/Textures/") && !BallonSetup.IsVariantTexture(assetPath)) return;
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
            if (assetPath.StartsWith("Assets/Ballon/Generated/Scenes/")) return;      // Szenen setzen ihre Lagen selbst (SceneLoader)
            var json = BallonSetup.EgoJson;                                            // 0.41: auch für Formgen-Pakete unter Generated/Formgen/<ID>/; 0.43: Serien
            if (!System.IO.File.Exists(json)) return;
            var all = EgoFile.ParseAll(System.IO.File.ReadAllText(json));
            var rel = assetPath.Substring(BallonSetup.Gen.Length + 1);
            var D = System.Array.Find(all, d => d.AssetPath(d.weapon.fbx) == rel);      // Waffe dieses FBX
            if (D == null && rel != "arms.fbx")
            {
                Debug.LogWarning($"[Ballon] {assetPath}: kein Eintrag in ego.json (Formgen-Paket ohne Export? tools/export_unity.py --formgen) – Knoten unverändert");
                return;
            }
            D = D ?? all[0];                                                           // Arme: beliebige Waffe (gemeinsamer Teil)
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
        public const string FormgenDir = Gen + "/Formgen/";            // 0.41: Formgen-Pakete (tools/formgen_import.py)
        // 0.43 „Kiln“: Design-Serien aus Formgen v2, lokal erzeugt (tools/series_packages.py bei `unity_run.py setup`), nicht im Repo. Alles
        // Lokale liegt unter diesem einen gitignorierten Ordner, die Szene kennt die Serien nicht: sie kommen zur Laufzeit über SeriesAssets.
        public const string SeriesDir = Gen + "/FormgenSeries/";
        public const string SeriesJson = SeriesDir + "Resources/ego_series.json";
        public const string SeriesAsset = SeriesDir + "Resources/" + SeriesAssets.ResourceName + ".asset";
        /// <summary>ego.json samt Serien, wenn sie lokal erzeugt sind (gleiche Form wie ego.json, Serien hinter den übrigen Waffen).</summary>
        public static string EgoJson => File.Exists(SeriesJson) ? SeriesJson : $"{Gen}/ego.json";
        public static bool IsSeries(EgoFile d) => d.dir.StartsWith("FormgenSeries/");

        /// <summary>Atlas eines Formgen-Pakets: Generated/Formgen/&lt;ID&gt;/textures/* bzw. Generated/FormgenSeries/&lt;ID&gt;/textures/*.</summary>
        public static bool IsVariantTexture(string path) => (path.StartsWith(FormgenDir) || path.StartsWith(SeriesDir)) && path.Contains("/textures/");

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
            var fbx = EgoFile.ParseAll(File.ReadAllText(EgoJson)).Select(d => d.AssetPath(d.weapon.fbx)).Append("arms.fbx");   // je Waffe (0.18), Formgen-Pakete in ihrem Ordner (0.41)
            foreach (var f in fbx)
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

        static Material Lit(string name, Color c, float smooth, float metal, string dir = Gen + "/Materials")
        {
            var path = $"{dir}/{name}.mat";
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

        /// <summary>Material für die Wirkung der Waffen (0.34, Shader Ballon/Fx): Form (_Mode), additiv oder Alpha, Rauschen, Tiefenversatz.</summary>
        static Material FxMat(string name, int mode, bool additive, Color c, float noise, float offset)
        {
            var path = $"{Gen}/Materials/{name}.mat";
            var sh = Shader.Find("Ballon/Fx");
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (m == null)
            {
                m = new Material(sh) { name = name };
                AssetDatabase.CreateAsset(m, path);
            }
            m.shader = sh;
            m.SetColor("_BaseColor", c);
            m.SetFloat("_Mode", mode);
            m.SetFloat("_Noise", noise);
            m.SetFloat("_SrcBlend", additive ? (float)UnityEngine.Rendering.BlendMode.One : (float)UnityEngine.Rendering.BlendMode.SrcAlpha);
            m.SetFloat("_DstBlend", additive ? (float)UnityEngine.Rendering.BlendMode.One : (float)UnityEngine.Rendering.BlendMode.OneMinusSrcAlpha);
            m.SetFloat("_OffsetUnits", offset);
            m.renderQueue = (int)UnityEngine.Rendering.RenderQueue.Transparent + (mode == 2 ? -10 : 0);
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
            m.SetFloat("_BlendModePreserveSpecular", 0);   // 0.20: sonst setzt URPs Materialprüfung beim Import SrcBlend One (vormultipliert,
                                                           // Glanz bleibt voll) und das Glas wird milchig
            m.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
            m.renderQueue = (int)RenderQueue.Transparent;
            m.SetOverrideTag("RenderType", "Transparent");
        }

        static void Emission(Material m, Color c)
        {
            m.EnableKeyword("_EMISSION");
            // 0.20: URPs Materialprüfung (BaseShaderGUI.SetMaterialKeywords, beim Reimport) lässt _EMISSION nur mit einem Emissive-Flag stehen;
            // mit None verlor das Absehen beim Import 0.20 sein Leuchten (schwarz). Szenen haben keine GI, Realtime ist folgenlos
            m.globalIlluminationFlags = MaterialGlobalIlluminationFlags.RealtimeEmissive;
            m.SetColor("_EmissionColor", c);
        }

        /// <summary>URP Lit je Materialrolle aus ego.json (Farbe im AAA-Modus, Rauheit → Glätte, Metall), dazu Parcours-Materialien.</summary>
        static Dictionary<string, Material> Materials()
        {
            var all = EgoFile.ParseAll(File.ReadAllText(EgoJson));
            var D = all[0];
            var res = new Dictionary<string, Material>();
            var series = new HashSet<string>(all.Where(IsSeries).Select(d => d.atlas));
            if (series.Count > 0) Directory.CreateDirectory(SeriesDir + "Materials");
            foreach (var r in D.roles)
            {
                var m = Lit("Role_" + r.role, Hex(r.aaa_color), 1f - r.rough, r.metal);
                if (r.alpha < 1f) { m.SetFloat("_Smoothness", 0.96f); Transparent(m, r.no_coat ? 0.04f : 0.12f); }
                if (r.alpha < 1f && r.no_coat)  // 0.20 Zielfernrohr: wie kit.aaa_nodes (no_coat: Alpha 0,04, Specular 0,05, kein Klarlack) – Glas ≤ 5 % getönt
                {
                    m.SetFloat("_SpecularHighlights", 0f);
                    m.EnableKeyword("_SPECULARHIGHLIGHTS_OFF");
                    m.SetFloat("_EnvironmentReflections", 0f);
                    m.EnableKeyword("_ENVIRONMENTREFLECTIONS_OFF");
                }
                if (r.emit > 0f)          // wie kit.aaa_nodes: Stärke emit · 1,6, reine Leuchtteile ohne beleuchtete Grundfarbe
                {
                    Emission(m, Color.black);
                    var e = Hex(r.color).linear * (r.emit * 1.6f);
                    m.SetColor("_EmissionColor", new Color(e.r, e.g, e.b, 1).gamma);   // Materialfarben sind Gamma-Werte
                    if (r.emit_only) m.SetColor("_BaseColor", Color.black);
                    if (r.emit_only && r.spec <= 0f)      // Mündungsfeuer (0.16): wie Blender ohne Glanz und Spiegelung (sonst blass)
                    {
                        m.SetFloat("_Smoothness", 0f);
                        m.SetFloat("_SpecularHighlights", 0f);
                        m.EnableKeyword("_SPECULARHIGHLIGHTS_OFF");
                        m.SetFloat("_EnvironmentReflections", 0f);
                        m.EnableKeyword("_ENVIRONMENTREFLECTIONS_OFF");
                    }
                }
                res["Role_" + r.role] = m;
            }
            // 0.7: gebackene Atlanten, 0.18 je Waffe; 0.41: Formgen-Pakete mit eigenem Texturordner (EgoFile.TexturePath)
            var atl = all.Select(d => (d.atlas, d.textures.weapon, (System.Func<string, string>)d.TexturePath)).Append(("arms", D.textures.arms, f => $"Textures/{f}"));
            foreach (var (key, A, path) in atl)
            {
                var m = series.Contains(key) ? Lit("Atlas_" + key, Color.white, 1f, 0f, SeriesDir + "Materials") : Lit("Atlas_" + key, Color.white, 1f, 0f);
                Texture2D T(string f) => Need($"{Gen}/{path(f)}");
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
            // Skins je Waffe (kit.SKINS): eigene Farb- und Glanzkarte, Normale und AO wie Standard; Schlüssel „Skin_<atlas>_<skin>“
            foreach (var d in all)
                foreach (var sk in d.textures.skins)
                {
                    string at = "Atlas_" + d.atlas;
                    if (sk.name == "standard") { res[$"Skin_{d.atlas}_standard"] = res[at]; continue; }
                    var m = new Material(res[at]);
                    var path = $"{Gen}/Materials/{at}_{sk.name}.mat";
                    var old = AssetDatabase.LoadAssetAtPath<Material>(path);
                    if (old != null) { old.CopyPropertiesFromMaterial(m); m = old; } else { m.name = $"{at}_{sk.name}"; AssetDatabase.CreateAsset(m, path); }
                    m.SetTexture("_BaseMap", Need($"{Gen}/{d.TexturePath(sk.albedo)}"));
                    m.SetTexture("_SpecGlossMap", Need($"{Gen}/{d.TexturePath(sk.spec)}"));
                    EditorUtility.SetDirty(m);
                    res[$"Skin_{d.atlas}_{sk.name}"] = m;
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
            res["decal"] = FxMat("Fx_Decal", 2, false, Color.white, 0, -2);      // 0.34: Einschussloch mit Rand und Ruß (Shader Ballon/Fx)
            res["fx_spark"] = FxMat("Fx_Spark", 4, true, Color.white, 0, 0);
            res["fx_glow"] = FxMat("Fx_Glow", 0, true, Color.white, 0, 0);
            res["fx_smoke"] = FxMat("Fx_Smoke", 0, false, Color.white, 1, 0);
            res["fx_ring"] = FxMat("Fx_Ring", 1, true, Hex("#FFE2B8"), 0, -1);
            res["fx_beam"] = FxMat("Fx_Beam", 3, true, Color.white, 0, 0);
            AssetDatabase.SaveAssets();
            return res;
        }

        /// <summary>Szenen aus Generated/Scenes/*/scene_*.json (Blender, tools/scene_build.py, ballon-scene/2): JSON, FBX der Umgebung, eine
        /// Unlit-Vorlage und alle Lichtatlanten (flach: Lichtszene · Zonenzahl + Zone, Reihenfolge wie im JSON). Unvollständige oder falsch
        /// formatierte Szenen (auch ältere Formate: „neu bauen“) werden übersprungen (Warnung), Fehlen aller ist normal.</summary>
        static List<(TextAsset json, GameObject prefab, Material mat, Texture2D[] atlases)> SceneAssets()
        {
            var res = new List<(TextAsset, GameObject, Material, Texture2D[])>();
            var dir = Gen + "/Scenes";
            if (!Directory.Exists(dir)) return res;
            var files = Directory.GetFiles(dir, "scene_*.json", SearchOption.AllDirectories).Select(f => f.Replace('\\', '/')).ToList();
            files.Sort(System.StringComparer.Ordinal);
            foreach (var path in files)
            {
                SceneFile f;
                try { f = SceneFile.Parse(File.ReadAllText(path)); }
                catch (System.Exception e) { Debug.LogWarning($"[Ballon] {path} übersprungen: {e.Message}"); continue; }
                var d = Path.GetDirectoryName(path).Replace('\\', '/');
                var atlasPaths = new List<string>();
                foreach (var l in f.lightings)
                    foreach (var z in f.zones)
                        atlasPaths.Add($"{d}/{l.AtlasFile(z.name)}");
                foreach (var a in new[] { path, $"{d}/{f.fbx}" }.Concat(atlasPaths))
                    if (File.Exists(a)) AssetDatabase.ImportAsset(a, ImportAssetOptions.ForceSynchronousImport);
                var json = AssetDatabase.LoadAssetAtPath<TextAsset>(path);
                var prefab = AssetDatabase.LoadAssetAtPath<GameObject>($"{d}/{f.fbx}");
                var atlases = atlasPaths.Select(a => AssetDatabase.LoadAssetAtPath<Texture2D>(a)).ToArray();
                if (json == null || prefab == null || atlases.Any(a => a == null))
                {
                    var missing = atlasPaths.Where(a => AssetDatabase.LoadAssetAtPath<Texture2D>(a) == null).Select(a => Path.GetFileName(a));
                    Debug.LogWarning($"[Ballon] {path} übersprungen: FBX {f.fbx} oder Lichtatlas fehlt ({string.Join(", ", missing)})");
                    continue;
                }
                var mp = $"{Gen}/Materials/Scene_{f.name}.mat";
                var m = AssetDatabase.LoadAssetAtPath<Material>(mp);
                if (m == null)
                {
                    m = new Material(Shader.Find("Universal Render Pipeline/Unlit")) { name = $"Scene_{f.name}" };
                    AssetDatabase.CreateAsset(m, mp);
                }
                // Vorlage ohne Atlas: der Lader kopiert sie je Zone und setzt Atlas (_BaseMap) und Helligkeit (_BaseColor = scale) je Lichtszene
                EditorUtility.SetDirty(m);
                res.Add((json, prefab, m, atlases));
            }
            return res;
        }

        /// <summary>Textur, die es geben muss (Atlas, Skin): fehlt sie, bricht der Aufbau mit dem Pfad ab statt still ohne Karte.</summary>
        static Texture2D Need(string path)
        {
            var t = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            if (t == null) throw new FileNotFoundException($"[Ballon] Textur fehlt: {path}");
            return t;
        }

        /// <summary>Waffensymbol (0.33 Ziel 2, tools/make_icons.py) als GUI-Textur ohne Mipmaps; fehlt es, bleibt das HUD ohne Symbol.
        /// Formgen-Varianten (0.41): Symbol aus dem FBX (VariantIcon), gleiche Form wie die Silhouetten-Symbole.</summary>
        static Texture2D Icon(EgoFile d)
        {
            var path = d.IsVariant ? VariantIcon(d) : $"{Gen}/Icons/{d.weapon.id}.png";   // Serien (0.43): Symbole unter FormgenSeries/Icons
            if (AssetImporter.GetAtPath(path) is TextureImporter ti && (ti.textureType != TextureImporterType.GUI || ti.mipmapEnabled))
            {
                ti.textureType = TextureImporterType.GUI;
                ti.mipmapEnabled = false;
                ti.alphaIsTransparency = true;
                ti.textureCompression = TextureImporterCompression.Uncompressed;
                ti.SaveAndReimport();
            }
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }

        public const int IconLength = 320, IconBorder = 4;       // wie tools/make_icons.py: Silhouetten auf 320 px Länge normiert, 4 px Rand

        /// <summary>Symbol einer Formgen-Variante (0.41): Seitenansicht des FBX (Mündung rechts) als weiße Silhouette mit Alpha, auf
        /// IconLength normiert, um 1 px verdickt, knapp beschnitten mit IconBorder Rand – wie make_icons.py aus data/silhouettes.json, aber
        /// aus den Dreiecken gerastert (ohne Kamera, gleiche Bytes bei gleichem Netz). Nach Generated/Icons/&lt;ID&gt;.png; neu nur, wenn sich
        /// das FBX ändert (SHA-256 in Icons/formgen_icons.json).</summary>
        static string VariantIcon(EgoFile d)
        {
            var dir = IsSeries(d) ? SeriesDir + "Icons" : $"{Gen}/Icons";
            var path = $"{dir}/{d.weapon.id}.png";
            var fbx = $"{Gen}/{d.AssetPath(d.weapon.fbx)}";
            var metaPath = $"{dir}/formgen_icons.json";
            string sha;
            using (var h = System.Security.Cryptography.SHA256.Create())
                sha = System.BitConverter.ToString(h.ComputeHash(File.ReadAllBytes(fbx))).Replace("-", "").ToLowerInvariant();
            var meta = File.Exists(metaPath) ? File.ReadAllText(metaPath) : "";
            var line = $"\"{d.weapon.id}\": \"{sha}\"";
            if (File.Exists(path) && meta.Contains(line)) return path;
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(fbx);
            var png = SilhouettePng(model);
            Directory.CreateDirectory(dir);
            File.WriteAllBytes(path, png);
            var lines = meta.Split('\n').Where(l => l.Contains(": \"") && !l.Contains($"\"{d.weapon.id}\":")).Select(l => l.Trim().TrimEnd(','))
                .Append(line).OrderBy(l => l, System.StringComparer.Ordinal).ToList();
            File.WriteAllText(metaPath, "{\n " + string.Join(",\n ", lines) + "\n}\n");
            AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceSynchronousImport);
            Debug.Log($"[Ballon] Symbol {path} aus {fbx}");
            return path;
        }

        /// <summary>Weiße Silhouette (RGBA-PNG) der Seitenansicht eines Modells: Unity z (vorn) nach rechts, y nach oben.</summary>
        public static byte[] SilhouettePng(GameObject model)
        {
            var root = model.transform.worldToLocalMatrix;
            var tris = new List<Vector2>();
            foreach (var mf in model.GetComponentsInChildren<MeshFilter>(true))
            {
                var m = mf.sharedMesh;
                if (m == null) continue;
                var M = root * mf.transform.localToWorldMatrix;
                var v = m.vertices;
                var idx = m.triangles;
                for (int i = 0; i < idx.Length; i++)
                {
                    var p = M.MultiplyPoint3x4(v[idx[i]]);
                    tris.Add(new Vector2(p.z, p.y));
                }
            }
            if (tris.Count == 0) throw new System.InvalidOperationException($"[Ballon] {model.name}: keine Dreiecke für das Symbol");
            float x0 = tris.Min(p => p.x), x1 = tris.Max(p => p.x), y0 = tris.Min(p => p.y), y1 = tris.Max(p => p.y);
            float k = (IconLength - 1) / (x1 - x0);
            int w = IconLength, hgt = Mathf.CeilToInt((y1 - y0) * k) + 1;
            var px = new bool[w, hgt];
            for (int t = 0; t + 2 < tris.Count; t += 3)        // Dreiecke rastern (Pixelmitte im Dreieck), y nach unten
            {
                var a = Map(tris[t]); var b = Map(tris[t + 1]); var c = Map(tris[t + 2]);
                int ia = Mathf.Max(0, Mathf.FloorToInt(Mathf.Min(a.x, Mathf.Min(b.x, c.x)))), ib = Mathf.Min(w - 1, Mathf.CeilToInt(Mathf.Max(a.x, Mathf.Max(b.x, c.x))));
                int ja = Mathf.Max(0, Mathf.FloorToInt(Mathf.Min(a.y, Mathf.Min(b.y, c.y)))), jb = Mathf.Min(hgt - 1, Mathf.CeilToInt(Mathf.Max(a.y, Mathf.Max(b.y, c.y))));
                float area = Edge(a, b, c);
                if (Mathf.Abs(area) < 1e-9f)
                {
                    px[Mathf.Clamp(Mathf.RoundToInt(a.x), 0, w - 1), Mathf.Clamp(Mathf.RoundToInt(a.y), 0, hgt - 1)] = true;   // entartet: ein Punkt
                    continue;
                }
                for (int i = ia; i <= ib; i++)
                    for (int j = ja; j <= jb; j++)
                    {
                        var q = new Vector2(i, j);
                        float e0 = Edge(b, c, q) / area, e1 = Edge(c, a, q) / area, e2 = Edge(a, b, q) / area;
                        if (e0 >= -1e-4f && e1 >= -1e-4f && e2 >= -1e-4f) px[i, j] = true;
                    }
            }
            Vector2 Map(Vector2 p) => new Vector2((p.x - x0) * k, (y1 - p.y) * k);
            // um 1 px verdicken (Kreuz, wie ImageMagick Dilate Disk:1), dann knapp beschneiden und Rand
            var thick = new bool[w, hgt];
            for (int i = 0; i < w; i++)
                for (int j = 0; j < hgt; j++)
                    thick[i, j] = px[i, j] || (i > 0 && px[i - 1, j]) || (i < w - 1 && px[i + 1, j]) || (j > 0 && px[i, j - 1]) || (j < hgt - 1 && px[i, j + 1]);
            int minI = w, maxI = -1, minJ = hgt, maxJ = -1;
            for (int i = 0; i < w; i++)
                for (int j = 0; j < hgt; j++)
                    if (thick[i, j]) { minI = Mathf.Min(minI, i); maxI = Mathf.Max(maxI, i); minJ = Mathf.Min(minJ, j); maxJ = Mathf.Max(maxJ, j); }
            int tw = maxI - minI + 1 + 2 * IconBorder, th = maxJ - minJ + 1 + 2 * IconBorder;
            var tex = new Texture2D(tw, th, TextureFormat.RGBA32, false);
            var cols = new Color32[tw * th];
            for (int i = minI; i <= maxI; i++)
                for (int j = minJ; j <= maxJ; j++)
                    if (thick[i, j]) cols[(th - 1 - (j - minJ + IconBorder)) * tw + (i - minI + IconBorder)] = new Color32(255, 255, 255, 255);
            tex.SetPixels32(cols);
            tex.Apply();
            var png = tex.EncodeToPNG();
            Object.DestroyImmediate(tex);
            return png;
        }

        static float Edge(Vector2 a, Vector2 b, Vector2 p) => (b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x);

        static void Scene(Dictionary<string, Material> mats)
        {
            var sc = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var go = new GameObject("Firstfeel");
            var b = go.AddComponent<Bootstrap>();
            b.egoJson = AssetDatabase.LoadAssetAtPath<TextAsset>($"{Gen}/ego.json");
            var all = EgoFile.ParseAll(File.ReadAllText(EgoJson));
            Bootstrap.WeaponAssets Assets(EgoFile d) => new Bootstrap.WeaponAssets
            {
                id = d.weapon.id,
                model = AssetDatabase.LoadAssetAtPath<GameObject>($"{Gen}/{d.AssetPath(d.weapon.fbx)}"),
                skins = d.textures.skins.Select(sk => mats[$"Skin_{d.atlas}_{sk.name}"]).ToArray(),
                icon = Icon(d),
            };
            b.weapons = all.Where(d => !IsSeries(d)).Select(Assets).ToArray();
            Series(all.Where(IsSeries).ToArray(), Assets, mats);
            var seriesAtlas = new HashSet<string>(all.Where(IsSeries).Select(d => "Atlas_" + d.atlas));
            b.armsModel = AssetDatabase.LoadAssetAtPath<GameObject>($"{Gen}/arms.fbx");
            b.roleMaterials = mats.Where(kv => (kv.Key.StartsWith("Role_") || kv.Key.StartsWith("Atlas_")) && !seriesAtlas.Contains(kv.Key)).Select(kv => kv.Value).ToArray();
            b.backdrop = mats["backdrop"];
            b.floor = mats["floor"];
            b.wall = mats["wall"];
            b.cover = mats["cover"];
            b.target = mats["target"];
            b.targetRing = mats["ring"];
            b.flash = mats["flash"];
            b.post = mats["post"];
            b.decal = mats["decal"];
            b.fxSpark = mats["fx_spark"];
            b.fxGlow = mats["fx_glow"];
            b.fxSmoke = mats["fx_smoke"];
            b.fxRing = mats["fx_ring"];
            b.fxBeam = mats["fx_beam"];
            b.shaderWarmup = Warmup();
            var scenes = SceneAssets();
            b.sceneJson = scenes.Select(x => x.json).ToArray();
            b.scenePrefabs = scenes.Select(x => x.prefab).ToArray();
            b.sceneMaterials = scenes.Select(x => x.mat).ToArray();
            b.sceneAtlases = scenes.Select(x => new Bootstrap.SceneAssetSet { textures = x.atlases }).ToArray();
            Debug.Log($"[Ballon] {scenes.Count} Szene(n) in {ScenePath}: {string.Join(", ", scenes.Select(x => x.json.name))}");
            EditorSceneManager.SaveScene(sc, ScenePath);
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
        }

        /// <summary>Serien (0.43): Modelle, Materialien und Daten in ein lokales Asset unter Resources – die Szene im Repo bleibt unverändert,
        /// Bootstrap lädt das Asset, wenn es da ist. Ohne Serien nichts anlegen.</summary>
        static void Series(EgoFile[] series, System.Func<EgoFile, Bootstrap.WeaponAssets> assets, Dictionary<string, Material> mats)
        {
            if (series.Length == 0) { AssetDatabase.DeleteAsset(SeriesAsset); return; }
            AssetDatabase.ImportAsset(SeriesJson, ImportAssetOptions.ForceSynchronousImport);
            var s = AssetDatabase.LoadAssetAtPath<SeriesAssets>(SeriesAsset);
            if (s == null)
            {
                s = ScriptableObject.CreateInstance<SeriesAssets>();
                AssetDatabase.CreateAsset(s, SeriesAsset);
            }
            s.egoJson = AssetDatabase.LoadAssetAtPath<TextAsset>(SeriesJson);
            s.weapons = series.Select(assets).ToArray();
            s.atlases = series.Select(d => mats["Atlas_" + d.atlas]).ToArray();
            EditorUtility.SetDirty(s);
            Debug.Log($"[Ballon] Serien: {series.Length} Waffen in {SeriesAsset}");
        }

        /// <summary>Aufgezeichnete Shader-Zustände (tools/unity_run.py aufwaermen); fehlen sie, startet die Build ohne Aufwärmen.</summary>
        static GraphicsStateCollection Warmup()
        {
            AssetDatabase.ImportAsset(ShaderWarmup.AssetPath, ImportAssetOptions.ForceUpdate);
            var g = AssetDatabase.LoadAssetAtPath<GraphicsStateCollection>(ShaderWarmup.AssetPath);
            if (g == null) Debug.LogWarning($"[Ballon] {ShaderWarmup.AssetPath} fehlt – Build ohne Shader-Aufwärmen (python3 tools/unity_run.py aufwaermen)");
            else Debug.Log($"[Ballon] Aufwärmen: {g.variantCount} Varianten, {g.totalGraphicsStateCount} Zustände ({g.graphicsDeviceType}, {g.runtimePlatform}, {g.qualityLevelName})");
            return g;
        }

        /// <summary>Nur die Sammlung in die vorhandene Szene setzen (ohne den vollen Aufbau von Run).</summary>
        public static void AttachWarmup()
        {
            var sc = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var b = Object.FindFirstObjectByType<Bootstrap>();
            var g = Warmup();
            if (b == null || g == null) { Debug.LogError("[Ballon] Aufwärmen: Bootstrap oder Sammlung fehlt"); EditorApplication.Exit(1); return; }
            b.shaderWarmup = g;
            EditorUtility.SetDirty(b);
            EditorSceneManager.SaveScene(sc);
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
