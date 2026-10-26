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
        // Mündungsfeuer und Hülsenpool (0.16): einmal angelegt, je Bild nur Lage und Sichtbarkeit
        readonly Transform _flash;
        readonly Renderer _flashR;
        readonly Transform[] _shells;
        readonly Renderer[] _shellR;

        /// <summary>Materialname des gebackenen Waffenatlas (ego.json › weapons[].atlas): „Atlas_weapon“ für die Pilotwaffe.</summary>
        public string WeaponAtlas => "Atlas_" + S.D.atlas;

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
                foreach (var nm in s.D.textures.weapon.objects) role[nm] = WeaponAtlas;     // je Waffe „Atlas_<atlas>“ (0.18)
                foreach (var nm in s.D.textures.arms.objects) role[nm] = "Atlas_arms";
            }
            foreach (var r in w.GetComponentsInChildren<Renderer>(true))
            {
                Dress(r, role, roles, layer);
                if (role.TryGetValue(r.name, out var ro) && ro == WeaponAtlas) _atlasWeapon.Add(r);
            }
            foreach (var r in a.GetComponentsInChildren<Renderer>(true)) Dress(r, role, roles, layer);
            foreach (var p in s.D.weapon.parts)                // Zielfernrohr (0.20): Teile mit ads_hide schaltet Apply im Zielen aus
                if (p.ads_hide && _parts[p.id].TryGetComponent<Renderer>(out var hr)) _adsHide.Add(hr);
            foreach (var p in s.D.weapon.parts)                // Absehen (0.20, Nutzer 26.10.2026): gezeichnet statt Modellteil (EgoPlayer, SightReticle)
                if (p.role.StartsWith("reticle") && _parts[p.id].TryGetComponent<Renderer>(out var rr))
                {
                    rr.enabled = false;
                    ReticleRole = p.role;
                }
            foreach (var t in w.GetComponentsInChildren<Transform>(true)) t.gameObject.layer = layer;
            foreach (var t in a.GetComponentsInChildren<Transform>(true)) t.gameObject.layer = layer;
            var fx = new GameObject("Fx").transform;
            fx.SetParent(space, false);
            fx.gameObject.layer = layer;
            var F = s.D.motion.flash;
            var fm = BuildMesh("MuzzleFlash", F.verts, F.core_tris, F.flame_tris);
            _flash = FxObject("MuzzleFlash", fx, fm, new[] { RoleMat(roles, F.core_role), RoleMat(roles, F.flame_role) }, layer, false, out _flashR);
            int pool = s.Ejects ? s.D.motion.eject.max_live : 0;
            _shells = new Transform[pool];
            _shellR = new Renderer[pool];
            if (pool > 0)
            {
                var cm = BuildMesh("Shell", s.D.weapon.eject.verts, s.D.weapon.eject.tris);
                var bm = new[] { RoleMat(roles, s.D.motion.eject.role) };
                for (int k = 0; k < pool; k++) _shells[k] = FxObject($"Shell_{k}", fx, cm, bm, layer, true, out _shellR[k]);
            }
        }

        static Material RoleMat(IDictionary<string, Material> roles, string role)
        {
            if (roles.TryGetValue(role, out var m)) return m;
            Debug.LogWarning($"[Ballon] keine Materialrolle für {role} (unity_run.py setup nach dem Export)");
            return null;
        }

        /// <summary>Netz aus ego.json (Blender-Rahmen, m, flach) nach Unity: Punkte über axes, Dreiecke gewendet, wenn die Achsen spiegeln.</summary>
        Mesh BuildMesh(string name, float[] verts, params int[][] subs)
        {
            var v = new Vector3[verts.Length / 3];
            for (int i = 0; i < v.Length; i++) v[i] = PointToUnity(_axes, new Vector3(verts[3 * i], verts[3 * i + 1], verts[3 * i + 2]));
            var m = new Mesh { name = name, vertices = v, subMeshCount = subs.Length };
            bool flip = _axes.determinant < 0;
            for (int k = 0; k < subs.Length; k++)
            {
                var t = (int[])subs[k].Clone();
                if (flip) for (int i = 0; i < t.Length; i += 3) (t[i + 1], t[i + 2]) = (t[i + 2], t[i + 1]);
                m.SetTriangles(t, k);
            }
            m.RecalculateNormals();
            m.RecalculateBounds();
            return m;
        }

        static Transform FxObject(string name, Transform parent, Mesh mesh, Material[] mats, int layer, bool shadows, out Renderer r)
        {
            var go = new GameObject(name) { layer = layer };
            go.transform.SetParent(parent, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var mr = go.AddComponent<MeshRenderer>();
            mr.sharedMaterials = mats;
            mr.shadowCastingMode = shadows ? ShadowCastingMode.On : ShadowCastingMode.Off;   // Blitz wirft wie in Blender keinen Schatten
            mr.receiveShadows = shadows;
            mr.lightProbeUsage = LightProbeUsage.Off;
            mr.reflectionProbeUsage = ReflectionProbeUsage.BlendProbes;
            mr.enabled = false;
            r = mr;
            return go.transform;
        }

        /// <summary>Anzahl der Hülsen im Pool (0: Waffe ohne Auswurf); für Tests.</summary>
        public int ShellPool => _shells.Length;
        /// <summary>Blitz gerade gezeichnet (Tests, Aufnahme).</summary>
        public bool FlashShown => _flashR.enabled;
        public Transform FlashTransform => _flash;

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

        readonly List<Renderer> _atlasWeapon = new List<Renderer>();
        readonly List<Renderer> _adsHide = new List<Renderer>();
        bool _adsHidden;
        /// <summary>Teile mit ads_hide sind gerade aus (Zielfernrohr im Zielen, 0.20).</summary>
        public bool AdsHidden => _adsHidden;
        /// <summary>Anzahl der Teile mit ads_hide (Okular, Rohr, Türme, Spannband).</summary>
        public int AdsHideCount => _adsHide.Count;

        /// <summary>Waffen-Skin setzen: alle Teile mit dem Waffenatlas bekommen dessen Skin-Material (Arme bleiben).</summary>
        public void SetSkin(Material m)
        {
            if (m == null) return;
            foreach (var r in _atlasWeapon) r.sharedMaterial = m;
        }

        public Material WeaponAtlasMaterial => _atlasWeapon.Count > 0 ? _atlasWeapon[0].sharedMaterial : null;

        public Transform Part(string id) => _parts[id];

        /// <summary>Materialrolle des Absehens im Modell (Farbe des gezeichneten Absehens), leer ohne Absehen.</summary>
        public string ReticleRole { get; private set; } = "";

        /// <summary>Weltlage eines Ankers (Blender-Waffenrahmen → Unity über axes.to_unity, nach dem letzten Apply).</summary>
        public Vector3 AnchorWorld(string id) => weaponRoot.TransformPoint(_axes.MultiplyPoint3x4(V(S.D.Anchor(id).pos)));
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
            if (_adsHidden != o.adsHidden)
            {
                _adsHidden = o.adsHidden;
                for (int k = 0; k < _adsHide.Count; k++) _adsHide[k].enabled = !o.adsHidden;
            }
            for (int i = 0; i < _segR.Length; i++)
            {
                Set(_segR[i], o.segR[i]);
                Set(_segL[i], o.segL[i]);
            }
            if (_flashR.enabled != o.flashOn) _flashR.enabled = o.flashOn;
            if (o.flashOn) Set(_flash, o.flash);
            for (int k = 0; k < _shells.Length; k++)
            {
                bool on = k < o.shellCount;
                if (_shellR[k].enabled != on) _shellR[k].enabled = on;
                if (on) Set(_shells[k], o.shells[k]);
            }
        }

        /// <summary>Weltkamera (5.1 A / 5.2 A): Grundbahn und Kamera-Ruck in Grad (Nicken hoch, Gieren rechts positiv) als Unity-Drehung
        /// im Kopfrahmen; das Viewmodel hängt am Kopf und bleibt davon unberührt.</summary>
        public Quaternion WorldKick(float pitchDeg, float yawDeg)
        {
            ToUnity(_axes, Rot(Rad(yawDeg), new Vector3(0, 0, -1)) * Rot(Rad(pitchDeg), new Vector3(-1, 0, 0)), out _, out var q);
            return q;
        }

        /// <summary>Kamera-Feedback (Grad, Mündung hoch = Kamera hoch) als Unity-Drehung im Kopfrahmen.</summary>
        public Quaternion CameraKick(float pitchDeg)
        {
            ToUnity(_axes, Rot(Rad(pitchDeg), new Vector3(-1, 0, 0)), out _, out var q);   // cam_base · Rx = Rot um Kamera-Rechts (−X)
            return q;
        }
    }
}
