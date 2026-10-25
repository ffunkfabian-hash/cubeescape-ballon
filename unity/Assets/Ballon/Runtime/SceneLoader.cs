// Szenenlader (0.8 Hangar): baut aus ballon-scene/1 (SceneFile), dem FBX und dem Lichtatlas eine spielbare Umgebung.
//   - Die Umgebung ist unbeleuchtet: alle Renderer teilen EIN URP-Unlit-Material mit dem Lichtatlas in _BaseMap (Cycles-Licht ist
//     im Atlas), ohne Schatten.
//   - Kollision aus „colliders“ (BoxCollider), nicht aus dem FBX.
//   - Lichter beleuchten nur das Viewmodel (Light.cullingMask); Flächenlichter erscheinen zusätzlich als leuchtende Flächen auf
//     der Ebene StudioEmitLayer, die nur die Reflexionssonde sieht (Strahldichte P / (π · A), wie Bootstrap.StudioLike).
//   - Zielscheiben an „targets“ wie im Parcours, gedreht zum Startpunkt.
// Umgebungslicht, Himmel, Sonde und Spieler setzt Bootstrap (ApplyScene), weil sie den Zustand der ganzen Szene betreffen.
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace Ballon.Ego
{
    public sealed class LoadedScene
    {
        public SceneFile data;
        public Transform root;
        public RangeTargets targets;
        public readonly List<Light> lights = new List<Light>();
        public readonly List<GameObject> emitters = new List<GameObject>();
        public readonly List<BoxCollider> colliders = new List<BoxCollider>();
        public Bounds bounds;
        public Vector3 spawnPos;       // Füße, Unity
        public float spawnYaw;         // Unity-Grad
        public Color ambientGamma, skyGamma;
    }

    public static class SceneLoader
    {
        public const float SpawnLift = 0.02f;      // Füße knapp über dem Boden, wie im Parcours (0,01 m)
        public const float TargetHeight = 1.45f;   // Höhe der Scheibenmitte über den Füßen des Pfostens (RangeBuilder.Target)

        /// <param name="env">importierter FBX (Prefab); null erlaubt (nur Collider, Lichter, Ziele – etwa im Test)</param>
        /// <param name="atlas">URP-Unlit-Material mit dem Lichtatlas; wird allen Renderern der Umgebung zugewiesen</param>
        /// <param name="emit">Unlit-Material für die Lichtflächen der Sonde (wird je Fläche kopiert)</param>
        public static LoadedScene Build(SceneFile f, GameObject env, Material atlas, Material emit, RangeBuilder.Mats targetMats)
        {
            var L = new LoadedScene { data = f };
            L.root = new GameObject("Szene " + f.name).transform;
            var bounds = new Bounds();
            bool haveBounds = false;
            if (env != null)
            {
                var e = Object.Instantiate(env, L.root, false);
                e.name = "Umgebung";
                foreach (var r in e.GetComponentsInChildren<Renderer>(true))
                {
                    r.sharedMaterial = atlas;
                    r.shadowCastingMode = ShadowCastingMode.Off;
                    r.receiveShadows = false;
                    r.lightProbeUsage = LightProbeUsage.Off;
                    r.reflectionProbeUsage = ReflectionProbeUsage.Off;
                    r.gameObject.layer = 0;
                    if (haveBounds) bounds.Encapsulate(r.bounds); else { bounds = r.bounds; haveBounds = true; }
                }
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
            foreach (var l in f.lights) AddLight(L, l, emit);
            // Zielscheiben: pos = Scheibenmitte (Blender); Füße des Pfostens liegen TargetHeight tiefer. Zur Ringseite gedreht: Blick vom Startpunkt.
            L.spawnPos = SceneConvert.Point(f.spawn.pos) + Vector3.up * SpawnLift;
            L.spawnYaw = SceneConvert.Yaw(f.spawn.yaw_deg);
            L.targets = new RangeTargets();
            var tRoot = new GameObject("Ziele").transform;
            tRoot.SetParent(L.root, false);
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
            L.ambientGamma = SceneConvert.Gamma(SceneConvert.Linear(f.ambient.color), f.ambient.strength);
            L.skyGamma = SceneConvert.Gamma(SceneConvert.Linear(f.sky.color), f.sky.strength);
            return L;
        }

        static void AddLight(LoadedScene L, SceneLight s, Material emit)
        {
            var lin = SceneConvert.Linear(s.color);
            var pos = SceneConvert.Point(s.pos);
            var dir = s.dir != null && s.dir.Length == 3 ? SceneConvert.Point(s.dir).normalized : Vector3.down;
            var go = new GameObject("Licht " + s.name);
            go.transform.SetParent(L.root, false);
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
                case "spot": l.type = LightType.Spot; l.spotAngle = 90f; l.innerSpotAngle = 54f; l.range = 60f; break;
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
            q.transform.SetParent(L.root, false);
            q.transform.localPosition = pos;
            q.transform.localRotation = Quaternion.LookRotation(-dir);       // sichtbare Seite (−Z der Fläche) zeigt in Leuchtrichtung
            q.transform.localScale = new Vector3(s.size_m, s.size_m, 1f);
            L.emitters.Add(q);
        }
    }
}
