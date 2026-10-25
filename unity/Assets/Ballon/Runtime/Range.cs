// Grauer Testparcours: Boden mit Meterraster, Wände, Deckung, Rampe, Säulen (Wandnähe), Zielscheiben in 10/25/50 m.
using System.Collections.Generic;
using System.Text;
using UnityEngine;

namespace Ballon.Ego
{
    public sealed class RangeTarget : MonoBehaviour
    {
        public float distance;
        public int hits;
        public Renderer face;
        public Material normal, flash;
        float _until;

        public void Hit(Vector3 p)
        {
            hits++;
            _until = Time.time + 0.12f;
            if (face != null) face.sharedMaterial = flash;
        }

        void Update()
        {
            if (face != null && face.sharedMaterial == flash && Time.time > _until) face.sharedMaterial = normal;
        }
    }

    public sealed class RangeTargets
    {
        public readonly List<RangeTarget> targets = new List<RangeTarget>();

        readonly List<float> _dist = new List<float>();

        /// <summary>Treffer je Entfernung, aufsteigend („10 m: 3   25 m: 0 …“); läuft nur bei geänderter Anzeige.</summary>
        public string Summary()
        {
            _dist.Clear();
            foreach (var t in targets)
            {
                bool known = false;
                foreach (var d in _dist) if (Mathf.Approximately(d, t.distance)) { known = true; break; }
                if (!known) _dist.Add(t.distance);
            }
            _dist.Sort();
            var b = new StringBuilder();
            foreach (var g in _dist)
            {
                int n = 0;
                foreach (var t in targets) if (Mathf.Approximately(t.distance, g)) n += t.hits;
                b.Append($"{g:0} m: {n}   ");
            }
            return b.ToString();
        }
    }

    public static class RangeBuilder
    {
        public sealed class Mats { public Material floor, wall, cover, target, targetRing, flash, post; }

        public static RangeTargets Build(Transform root, Mats m)
        {
            var R = new RangeTargets();
            var floorTex = Grid();
            var floor = Box(root, "Boden", new Vector3(0, -0.05f, 40), new Vector3(40, 0.1f, 100), m.floor);
            var fm = new Material(m.floor) { name = "Boden_Raster" };
            fm.SetTexture("_BaseMap", floorTex);
            fm.SetTextureScale("_BaseMap", new Vector2(40, 100));
            floor.GetComponent<Renderer>().sharedMaterial = fm;
            Box(root, "Wand links", new Vector3(-20.5f, 2, 40), new Vector3(1, 4, 100), m.wall);
            Box(root, "Wand rechts", new Vector3(20.5f, 2, 40), new Vector3(1, 4, 100), m.wall);
            Box(root, "Wand hinten", new Vector3(0, 2, -10.5f), new Vector3(42, 4, 1), m.wall);
            Box(root, "Kugelfang", new Vector3(0, 4, 90.5f), new Vector3(42, 8, 1), m.wall);
            // Standplatz: Brüstung, Säulen zum Testen der Wandnähe, Deckungsblöcke, Rampe mit Podest zum Springen
            Box(root, "Brüstung", new Vector3(0, 0.5f, 4), new Vector3(6, 1.0f, 0.3f), m.cover);
            Box(root, "Säule 1", new Vector3(-6, 1.5f, -2), new Vector3(0.8f, 3, 0.8f), m.cover);
            Box(root, "Säule 2", new Vector3(6, 1.5f, -2), new Vector3(0.8f, 3, 0.8f), m.cover);
            for (int i = 0; i < 4; i++)
                Box(root, $"Deckung {i + 1}", new Vector3(-12 + i * 8, 0.6f, 16 + (i % 2) * 6), new Vector3(2.2f, 1.2f, 0.8f), m.cover);
            var ramp = Box(root, "Rampe", new Vector3(-14, 0.75f, 2), new Vector3(3, 0.2f, 6.5f), m.cover);
            ramp.transform.rotation = Quaternion.Euler(-14, 0, 0);
            Box(root, "Podest", new Vector3(-14, 1.25f, 7.6f), new Vector3(3, 2.5f, 4), m.cover);
            Box(root, "Stufe 1", new Vector3(14, 0.25f, 0), new Vector3(3, 0.5f, 1.2f), m.cover);
            Box(root, "Stufe 2", new Vector3(14, 0.5f, 1.2f), new Vector3(3, 1.0f, 1.2f), m.cover);
            Box(root, "Stufe 3", new Vector3(14, 0.75f, 2.4f), new Vector3(3, 1.5f, 1.2f), m.cover);
            Box(root, "Durchgang Decke", new Vector3(0, 1.45f, -6), new Vector3(3, 0.2f, 2), m.cover);
            Box(root, "Durchgang links", new Vector3(-1.6f, 0.68f, -6), new Vector3(0.2f, 1.35f, 2), m.cover);
            Box(root, "Durchgang rechts", new Vector3(1.6f, 0.68f, -6), new Vector3(0.2f, 1.35f, 2), m.cover);
            float[] dist = { 10, 25, 50 };
            float[][] xs = { new[] { -3f, 0f, 3f }, new[] { -6f, 0f, 6f }, new[] { -8f, 0f, 8f } };
            for (int d = 0; d < 3; d++)
                foreach (var x in xs[d])
                    R.targets.Add(Target(root, new Vector3(x, 0, 4 + dist[d]), dist[d], 0.3f + 0.15f * d, m));
            return R;
        }

        static Texture2D Grid()
        {
            const int n = 256;
            var t = new Texture2D(n, n, TextureFormat.RGBA32, true) { wrapMode = TextureWrapMode.Repeat, filterMode = FilterMode.Trilinear, anisoLevel = 8 };
            var px = new Color32[n * n];
            for (int y = 0; y < n; y++)
                for (int x = 0; x < n; x++)
                {
                    bool line = x < 3 || y < 3;
                    bool half = (x >= n / 2 - 1 && x <= n / 2) || (y >= n / 2 - 1 && y <= n / 2);
                    byte v = line ? (byte)88 : half ? (byte)118 : (byte)128;
                    px[y * n + x] = new Color32(v, v, (byte)(v + 3), 255);
                }
            t.SetPixels32(px);
            t.Apply(true);
            return t;
        }

        static GameObject Box(Transform root, string name, Vector3 c, Vector3 size, Material m)
        {
            var g = GameObject.CreatePrimitive(PrimitiveType.Cube);
            g.name = name;
            g.transform.SetParent(root, false);
            g.transform.localPosition = c;
            g.transform.localScale = size;
            g.GetComponent<Renderer>().sharedMaterial = m;
            return g;
        }

        /// <summary>Radius der Scheibe nach Entfernung: 0,30 m bis ≈ 17 m, 0,45 m bis ≈ 37 m, sonst 0,60 m (wie die Parcours-Stufen 10/25/50).</summary>
        public static float TargetRadius(float distance) => distance < 17.5f ? 0.3f : distance < 37.5f ? 0.45f : 0.6f;

        public static RangeTarget Target(Transform root, Vector3 at, float distance, float radius, Mats m)
        {
            float h = 1.45f;
            var post = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            post.name = $"Pfosten {distance:0} m";
            post.transform.SetParent(root, false);
            post.transform.localPosition = at + new Vector3(0, h / 2, 0.05f);
            post.transform.localScale = new Vector3(0.06f, h / 2, 0.06f);
            post.GetComponent<Renderer>().sharedMaterial = m.post;
            var disc = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            disc.name = $"Scheibe {distance:0} m";
            disc.transform.SetParent(root, false);
            disc.transform.localPosition = at + new Vector3(0, h, 0);
            disc.transform.localRotation = Quaternion.Euler(90, 0, 0);
            disc.transform.localScale = new Vector3(radius * 2, 0.02f, radius * 2);
            Object.Destroy(disc.GetComponent<Collider>());
            disc.AddComponent<MeshCollider>().sharedMesh = disc.GetComponent<MeshFilter>().sharedMesh;
            var r = disc.GetComponent<Renderer>();
            r.sharedMaterial = m.target;
            var ring = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            ring.name = "Mitte";
            Object.Destroy(ring.GetComponent<Collider>());
            ring.transform.SetParent(disc.transform, false);
            ring.transform.localPosition = new Vector3(0, -0.6f, 0);
            ring.transform.localScale = new Vector3(0.36f, 0.3f, 0.36f);
            ring.GetComponent<Renderer>().sharedMaterial = m.targetRing;
            var t = disc.AddComponent<RangeTarget>();
            t.distance = distance;
            t.face = r;
            t.normal = m.target;
            t.flash = m.flash;
            return t;
        }
    }
}
