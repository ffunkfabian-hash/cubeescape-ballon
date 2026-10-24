// Bindet die importierten Modelle (Waffe, Arme) an die Auswertung: Teile und Segmente per Name, Materialien je Rolle,
// Ebene „Viewmodel“. Apply() setzt die lokalen Transformationen aus einer EgoOutput (Blender-Kameraraum → Unity).
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using static Ballon.Ego.BMath;

namespace Ballon.Ego
{
    public sealed class EgoRig
    {
        public readonly EgoSolver S;
        public readonly Transform space;               // Ursprung = Blender-Kamera (ohne Kamera-Feedback)
        public readonly Transform weaponRoot;
        readonly Dictionary<string, Transform> _parts = new Dictionary<string, Transform>();
        readonly Transform[] _segL, _segR;
        readonly Matrix4x4 _axes;
        Transform _mag;

        public EgoRig(EgoSolver s, Transform space, GameObject weaponModel, GameObject armsModel, IDictionary<string, Material> roles, int layer)
        {
            S = s;
            this.space = space;
            _axes = s.D.toUnity;
            var w = Object.Instantiate(weaponModel, space, false);
            w.name = "Weapon";
            var a = Object.Instantiate(armsModel, space, false);
            a.name = "Arms";
            Reset(w.transform);
            Reset(a.transform);
            var all = new Dictionary<string, Transform>();
            foreach (var t in w.GetComponentsInChildren<Transform>(true)) all[t.name] = t;
            foreach (var t in a.GetComponentsInChildren<Transform>(true)) all[t.name] = t;
            weaponRoot = Find(all, s.D.weapon.root);
            foreach (var p in s.D.weapon.parts) _parts[p.id] = Find(all, p.id);
            _mag = _parts.TryGetValue("magazine", out var m) ? m : null;
            int n = s.D.arm.segments.Length;
            _segL = new Transform[n];
            _segR = new Transform[n];
            for (int i = 0; i < n; i++)
            {
                _segR[i] = Find(all, "R_" + s.D.arm.segments[i]);
                _segL[i] = Find(all, "L_" + s.D.arm.segments[i]);
                _segR[i].SetParent(a.transform, false);
                _segL[i].SetParent(a.transform, false);
            }
            var role = new Dictionary<string, string>();
            foreach (var p in s.D.weapon.parts) role[p.id] = p.role;
            foreach (var p in s.D.arm.pieces) { role["R_" + p.id] = p.role; role["L_" + p.id] = p.role; }
            if (s.D.textures?.weapon?.objects != null)        // gebackene Teile nehmen den Atlas statt der Rolle (0.7)
            {
                foreach (var nm in s.D.textures.weapon.objects) role[nm] = "Atlas_weapon";
                foreach (var nm in s.D.textures.arms.objects) role[nm] = "Atlas_arms";
            }
            foreach (var r in w.GetComponentsInChildren<Renderer>(true)) Dress(r, role, roles, layer);
            foreach (var r in a.GetComponentsInChildren<Renderer>(true)) Dress(r, role, roles, layer);
            foreach (var t in w.GetComponentsInChildren<Transform>(true)) t.gameObject.layer = layer;
            foreach (var t in a.GetComponentsInChildren<Transform>(true)) t.gameObject.layer = layer;
        }

        static void Reset(Transform t)
        {
            t.localPosition = Vector3.zero;
            t.localRotation = Quaternion.identity;
            t.localScale = Vector3.one;
        }

        static Transform Find(Dictionary<string, Transform> all, string name) =>
            all.TryGetValue(name, out var t) ? t : throw new KeyNotFoundException($"Modell: Objekt '{name}' fehlt im FBX");

        static void Dress(Renderer r, Dictionary<string, string> role, IDictionary<string, Material> mats, int layer)
        {
            if (role.TryGetValue(r.name, out var ro) && mats.TryGetValue(ro, out var m)) r.sharedMaterial = m;
            else Debug.LogWarning($"[Ballon] keine Materialrolle für {r.name}");
            r.shadowCastingMode = ShadowCastingMode.On;      // Eigenschatten (Arm auf Waffe) wie in Cycles; die Weltkamera sieht die Ebene nicht
            r.receiveShadows = true;
            r.lightProbeUsage = LightProbeUsage.Off;
            r.reflectionProbeUsage = ReflectionProbeUsage.BlendProbes;
        }

        public Transform Part(string id) => _parts[id];
        public Transform SegR(string s) => _segR[S.SegmentIndex(s)];
        public Transform SegL(string s) => _segL[S.SegmentIndex(s)];

        void Set(Transform t, Matrix4x4 b)
        {
            ToUnity(_axes, b, out var p, out var q);
            t.localPosition = p;
            t.localRotation = q;
        }

        public void Apply(EgoOutput o)
        {
            Set(weaponRoot, o.weapon);
            var inv = o.weapon.inverse;
            foreach (var p in S.Movers)
            {
                var parent = string.IsNullOrEmpty(p.parent) ? inv : S.World(o, p.parent).inverse;
                var world = (p.id == "magazine" && o.magOverride) ? o.magWorld : o.movers[p.id];
                Set(_parts[p.id], parent * world);
            }
            if (_mag != null && _mag.gameObject.activeSelf == o.magHidden) _mag.gameObject.SetActive(!o.magHidden);
            for (int i = 0; i < _segR.Length; i++)
            {
                Set(_segR[i], o.segR[i]);
                Set(_segL[i], o.segL[i]);
            }
        }

        /// <summary>Kamera-Feedback (Grad, Mündung hoch = Kamera hoch) als Unity-Drehung im Kopfrahmen.</summary>
        public Quaternion CameraKick(float pitchDeg)
        {
            ToUnity(_axes, Rot(Rad(pitchDeg), new Vector3(-1, 0, 0)), out _, out var q);   // cam_base · Rx = Rot um Kamera-Rechts (−X)
            return q;
        }
    }
}
