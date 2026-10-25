// Szenenlader (0.8 Hangar, 0.9 Parcours): baut aus ballon-scene/2 (SceneFile), dem FBX und den Lichtatlanten eine spielbare Umgebung.
//   - Die Umgebung ist unbeleuchtet: jede Zone hat EIN URP-Unlit-Material (Kopie der Vorlage), das den Atlas der aktiven Lichtszene
//     in _BaseMap trägt (Cycles-Licht ist im Atlas, _BaseColor = scale), ohne Schatten. Alle Renderer eines Objekts bekommen das
//     Material seiner Zone; die UVs sind für alle Lichtszenen gleich, Umschalten tauscht nur die Texturen.
//   - Kollision aus „colliders“ (BoxCollider), nicht aus dem FBX.
//   - Je Lichtszene eine Gruppe Lichter, die nur das Viewmodel beleuchten (Light.cullingMask); Flächenlichter erscheinen zusätzlich
//     als leuchtende Flächen auf der Ebene StudioEmitLayer, die nur die Reflexionssonde sieht (Strahldichte P / (π · A)).
//     Alle Gruppen entstehen beim Laden (ausgeschaltet), Umschalten schaltet nur um.
//   - Parcours: Zielscheiben an „course.targets“ (Mitte, Normale, Radius), Auslöse-Logik in CourseRun, Wegmarken entlang „route“.
// Umgebungslicht, Himmel, Sonde und Spieler setzt Bootstrap (ShowScene, ShowLighting), weil sie den Zustand der ganzen Szene betreffen.
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace Ballon.Ego
{
    /// <summary>Eine gebaute Lichtszene: Lichter und Lichtflächen (als Gruppe ein-/ausschaltbar) und die Farben für Himmel und Umgebung.</summary>
    public sealed class LoadedLighting
    {
        public SceneLighting data;
        public GameObject group;
        public readonly List<Light> lights = new List<Light>();
        public readonly List<GameObject> emitters = new List<GameObject>();
        public Color ambientGamma, skyGamma;
        public Color atlasTint;           // Material-_BaseColor: scale als Gamma-Wert
    }

    public sealed class LoadedScene
    {
        public SceneFile data;
        public Transform root;
        public RangeTargets targets;
        public Material[] zoneMats;       // je Zone ein Unlit-Material (Index wie data.zones)
        public Texture2D[][] atlases;     // [Lichtszene][Zone]; null-Einträge lassen das Material unverändert
        public LoadedLighting[] lightings;
        public CourseRun course;          // null ohne course
        public GameObject routeMarkers;
        public readonly List<BoxCollider> colliders = new List<BoxCollider>();
        public Bounds bounds;
        public Vector3 spawnPos;       // Füße, Unity
        public float spawnYaw;         // Unity-Grad

        static readonly int BaseMap = Shader.PropertyToID("_BaseMap"), BaseColor = Shader.PropertyToID("_BaseColor");

        /// <summary>Atlanten und Helligkeit der Lichtszene li in die Zonenmaterialien schreiben (kein Neuaufbau der Geometrie).</summary>
        public void ApplyAtlas(int li)
        {
            var tint = lightings[li].atlasTint;
            for (int z = 0; z < zoneMats.Length; z++)
            {
                var t = atlases != null && li < atlases.Length && atlases[li] != null && z < atlases[li].Length ? atlases[li][z] : null;
                if (t != null) zoneMats[z].SetTexture(BaseMap, t);
                zoneMats[z].SetColor(BaseColor, tint);
            }
        }
    }

    public static class SceneLoader
    {
        public const float SpawnLift = 0.02f;      // Füße knapp über dem Boden, wie im Parcours (0,01 m)
        public const float TargetHeight = 1.45f;   // Höhe der Scheibenmitte über den Füßen des Pfostens (RangeBuilder.Target)

        static Material UnlitFallback() => new Material(Shader.Find("Universal Render Pipeline/Unlit"));

        /// <param name="env">importierter FBX (Prefab); null erlaubt (nur Collider, Lichter, Ziele – etwa im Test)</param>
        /// <param name="template">URP-Unlit-Material; je Zone entsteht eine Kopie, die den Atlas der aktiven Lichtszene trägt</param>
        /// <param name="atlases">[Lichtszene][Zone] Texturen; null erlaubt (Zonenmaterialien bleiben ohne Atlas)</param>
        /// <param name="emit">Unlit-Material für Lichtflächen und Wegmarken (wird je Verwendung kopiert)</param>
        public static LoadedScene Build(SceneFile f, GameObject env, Material template, Texture2D[][] atlases, Material emit, RangeBuilder.Mats targetMats)
        {
            var L = new LoadedScene { data = f, atlases = atlases };
            L.root = new GameObject("Szene " + f.name).transform;
            L.zoneMats = new Material[f.zones.Length];
            for (int z = 0; z < f.zones.Length; z++)
                L.zoneMats[z] = new Material(template != null ? template : UnlitFallback()) { name = $"Zone {f.name}/{f.zones[z].name}" };
            var zoneOf = new Dictionary<string, int>();
            for (int z = 0; z < f.zones.Length; z++) foreach (var o in f.zones[z].objects) zoneOf[o] = z;
            var bounds = new Bounds();
            bool haveBounds = false;
            if (env != null)
            {
                var e = Object.Instantiate(env, L.root, false);
                e.name = "Umgebung";
                int unmatched = 0;
                string firstUnmatched = null;
                foreach (var r in e.GetComponentsInChildren<Renderer>(true))
                {
                    int zi = -1;
                    for (var t = r.transform; t != null && zi < 0; t = t == e.transform ? null : t.parent)      // Objektname oder ein Elternknoten
                        if (zoneOf.TryGetValue(t.name, out int z)) zi = z;
                    if (zi < 0) { zi = 0; unmatched++; firstUnmatched = firstUnmatched ?? r.name; }
                    var mats = r.sharedMaterials;
                    for (int k = 0; k < mats.Length; k++) mats[k] = L.zoneMats[zi];
                    r.sharedMaterials = mats;
                    r.shadowCastingMode = ShadowCastingMode.Off;
                    r.receiveShadows = false;
                    r.lightProbeUsage = LightProbeUsage.Off;
                    r.reflectionProbeUsage = ReflectionProbeUsage.Off;
                    r.gameObject.layer = 0;
                    if (haveBounds) bounds.Encapsulate(r.bounds); else { bounds = r.bounds; haveBounds = true; }
                }
                if (unmatched > 0)
                    Debug.LogWarning($"[Ballon] Szene {f.name}: {unmatched} Renderer ohne Zone (z. B. {firstUnmatched}) – bekommen die Zone {f.zones[0].name}");
                foreach (var c in e.GetComponentsInChildren<Collider>(true)) Object.Destroy(c);     // Kollision nur aus „colliders“
            }
            var colRoot = new GameObject("Collider").transform;
            colRoot.SetParent(L.root, false);
            foreach (var c in f.colliders)
            {
                var g = new GameObject(string.IsNullOrEmpty(c.name) ? "Collider" : c.name);
                g.transform.SetParent(colRoot, false);
                g.transform.localPosition = SceneConvert.Point(c.center);
                var b = g.AddComponent<BoxCollider>();
                b.size = SceneConvert.Size(c.size);
                L.colliders.Add(b);
                var cb = new Bounds(g.transform.localPosition, b.size);
                if (haveBounds) bounds.Encapsulate(cb); else { bounds = cb; haveBounds = true; }
            }
            if (!haveBounds) bounds = new Bounds(SceneConvert.Point(f.spawn.pos), Vector3.one * 10f);
            L.bounds = bounds;
            L.lightings = new LoadedLighting[f.lightings.Length];
            for (int i = 0; i < f.lightings.Length; i++) L.lightings[i] = BuildLighting(L, f.lightings[i], emit);
            L.spawnPos = SceneConvert.Point(f.spawn.pos) + Vector3.up * SpawnLift;
            L.spawnYaw = SceneConvert.Yaw(f.spawn.yaw_deg);
            L.targets = new RangeTargets();
            var tRoot = new GameObject("Ziele").transform;
            tRoot.SetParent(L.root, false);
            // Schießstand-Ziele (targets): pos = Scheibenmitte; Füße des Pfostens liegen TargetHeight tiefer, Ringseite zum Startpunkt
            foreach (var t in f.targets)
            {
                var foot = SceneConvert.Point(t.pos) - Vector3.up * TargetHeight;
                var away = Vector3.ProjectOnPlane(foot - L.spawnPos, Vector3.up);
                var pivot = new GameObject($"Ziel {t.distance:0} m").transform;
                pivot.SetParent(tRoot, false);
                pivot.localPosition = foot;
                if (away.sqrMagnitude > 1e-4f) pivot.localRotation = Quaternion.LookRotation(away);
                L.targets.targets.Add(RangeBuilder.Target(pivot, Vector3.zero, t.distance, RangeBuilder.TargetRadius(t.distance), targetMats));
            }
            if (f.course != null)
            {
                BuildCourseTargets(L, f.course, tRoot, targetMats);
                L.course = new CourseRun(f.name, f.course, L.targets.targets, CourseRun.PrefsKey(f.name));
                BuildRoute(L, f.course, emit);
            }
            L.ApplyAtlas(0);
            return L;
        }

        /// <summary>Zielscheiben des Parcours: Mitte `pos`, Ringseite entlang `normal` (waagerecht), Radius `radius`. Der Pfosten reicht bis
        /// zur Oberkante des höchsten Colliders darunter (Kiste, Podest, Boden); ohne Collider gilt die Standardhöhe.</summary>
        static void BuildCourseTargets(LoadedScene L, SceneCourse c, Transform tRoot, RangeBuilder.Mats mats)
        {
            foreach (var t in c.targets)
            {
                var mid = SceneConvert.Point(t.pos);
                float ground = float.NegativeInfinity;
                foreach (var col in L.data.colliders)
                {
                    var cb = new Bounds(SceneConvert.Point(col.center), SceneConvert.Size(col.size));
                    float top = cb.max.y;
                    if (top <= mid.y - 0.2f && mid.x >= cb.min.x && mid.x <= cb.max.x && mid.z >= cb.min.z && mid.z <= cb.max.z && top > ground) ground = top;
                }
                float h = float.IsNegativeInfinity(ground) ? TargetHeight : Mathf.Clamp(mid.y - ground, 0.3f, 4f);
                h = Mathf.Max(h, t.radius + 0.1f);                      // Scheibe ragt nicht in den Boden
                var n = SceneConvert.Point(t.normal);
                var flat = new Vector3(n.x, 0, n.z);
                var pivot = new GameObject("Ziel " + t.name).transform;
                pivot.SetParent(tRoot, false);
                pivot.localPosition = mid - Vector3.up * h;
                if (flat.sqrMagnitude > 1e-4f) pivot.localRotation = Quaternion.LookRotation(-flat.normalized);       // −Z des Pfostens = Ringseite
                else
                {
                    var away = Vector3.ProjectOnPlane(pivot.localPosition - L.spawnPos, Vector3.up);        // senkrechte Normale: zum Startpunkt gedreht
                    if (away.sqrMagnitude > 1e-4f) pivot.localRotation = Quaternion.LookRotation(away);
                }
                var spawnFlat = Vector3.ProjectOnPlane(mid - L.spawnPos, Vector3.up);
                L.targets.targets.Add(RangeBuilder.Target(pivot, Vector3.zero, spawnFlat.magnitude, t.radius, mats, h));
            }
        }

        /// <summary>Wegmarken: flache Pfeile entlang `route`, dezent (Unlit, ein Netz).</summary>
        static void BuildRoute(LoadedScene L, SceneCourse c, Material emit)
        {
            if (c.route == null || c.route.Length < 2) return;
            var pts = new Vector3[c.route.Length];
            for (int i = 0; i < pts.Length; i++) pts[i] = SceneConvert.Point(c.route[i]);
            var go = new GameObject("Wegmarken");
            go.transform.SetParent(L.root, false);
            go.AddComponent<MeshFilter>().sharedMesh = RouteMarkers.BuildMesh(pts);
            var m = new Material(emit != null ? emit : UnlitFallback()) { name = "Wegmarken" };
            m.SetColor("_BaseColor", SceneConvert.Gamma(SceneConvert.Linear("#7FD6E8"), 0.55f));      // Materialfarben sind Gamma-Werte
            var r = go.AddComponent<MeshRenderer>();
            r.sharedMaterial = m;
            r.shadowCastingMode = ShadowCastingMode.Off;
            r.receiveShadows = false;
            L.routeMarkers = go;
        }

        static LoadedLighting BuildLighting(LoadedScene L, SceneLighting s, Material emit)
        {
            var LL = new LoadedLighting { data = s };
            LL.group = new GameObject("Licht " + s.name);
            LL.group.transform.SetParent(L.root, false);
            foreach (var l in s.lights) AddLight(LL, l, emit);
            LL.ambientGamma = SceneConvert.Gamma(SceneConvert.Linear(s.ambient.color), s.ambient.strength);
            LL.skyGamma = SceneConvert.Gamma(SceneConvert.Linear(s.sky.color), s.sky.strength);
            LL.atlasTint = SceneConvert.Gamma(Color.white, s.scale);       // Atlas = Licht / scale; Materialfarben sind Gamma-Werte
            LL.group.SetActive(false);                                       // Bootstrap.ShowLighting schaltet die aktive Gruppe ein
            return LL;
        }

        static void AddLight(LoadedLighting L, SceneLight s, Material emit)
        {
            var lin = SceneConvert.Linear(s.color);
            var pos = SceneConvert.Point(s.pos);
            var dir = s.dir != null && s.dir.Length == 3 ? SceneConvert.Point(s.dir).normalized : Vector3.down;
            var go = new GameObject("Licht " + s.name);
            go.transform.SetParent(L.group.transform, false);
            go.transform.localPosition = pos;
            go.transform.localRotation = Quaternion.LookRotation(dir);
            var l = go.AddComponent<Light>();
            l.color = lin.gamma;
            l.intensity = SceneConvert.Intensity(s.kind, s.power_w);
            l.shadows = LightShadows.None;                               // Cycles-Flächenlichter dieser Größe werfen kaum sichtbare Schatten
            l.cullingMask = 1 << Bootstrap.ViewmodelLayer;               // nur Viewmodel; die Umgebung ist unbeleuchtet
            switch (s.kind)
            {
                case "sun": l.type = LightType.Directional; break;
                case "point": l.type = LightType.Point; l.range = 60f; break;
                case "spot":
                    l.type = LightType.Spot;
                    l.spotAngle = s.angle_deg > 0f ? s.angle_deg : 90f;     // aus den Szenendaten, wie Blender spot_size
                    l.innerSpotAngle = l.spotAngle * 0.6f;
                    l.range = 60f;
                    break;
                default: l.type = LightType.Spot; l.spotAngle = 150f; l.innerSpotAngle = 60f; l.range = 60f; break;   // Fläche wie StudioLike
            }
            L.lights.Add(l);
            if (s.kind != "area" || emit == null) return;
            // Spiegelbild der Lichtfläche für die Reflexionssonde: leuchtende Fläche, Strahldichte P / (π · A)
            var q = GameObject.CreatePrimitive(PrimitiveType.Quad);
            Object.Destroy(q.GetComponent<Collider>());
            q.name = "Lichtfläche " + s.name;
            q.layer = Bootstrap.StudioEmitLayer;
            var m = new Material(emit) { name = "Lichtfläche " + s.name };
            m.SetColor("_BaseColor", SceneConvert.Gamma(lin, SceneConvert.Radiance(s.power_w, s.size_m)));   // Materialfarben sind Gamma-Werte
            var r = q.GetComponent<Renderer>();
            r.sharedMaterial = m;
            r.shadowCastingMode = ShadowCastingMode.Off;
            q.transform.SetParent(L.group.transform, false);
            q.transform.localPosition = pos;
            q.transform.localRotation = Quaternion.LookRotation(-dir);       // sichtbare Seite (−Z der Fläche) zeigt in Leuchtrichtung
            q.transform.localScale = new Vector3(s.size_m, s.size_m, 1f);
            L.emitters.Add(q);
        }
    }
}
