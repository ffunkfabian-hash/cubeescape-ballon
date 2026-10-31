// Bildlage im Ego-Bild (0.15): Punkte des Blender-Kameraraums in Prozent von Bildbreite/-höhe (Ursprung oben links, 75° horizontal,
// 16:9 wie die Ego-Stills) und die Silhouette von Waffe und Armen aus den Netzgrenzen (ego.json › mesh_bounds). Für Tests und
// Messungen (Hüftlage, Sprint-Hub, leere Sicht beim Wechsel, Visier im Zielen); das Spiel selbst nutzt es nicht.
using System.Collections.Generic;
using UnityEngine;
using static Ballon.Ego.BMath;

namespace Ballon.Ego
{
    public sealed class EgoScreen
    {
        readonly EgoSolver S;
        readonly float _tanH, _tanV;
        readonly List<(string id, Vector3 min, Vector3 max)> _parts = new List<(string, Vector3, Vector3)>();
        readonly List<(int seg, bool right, Vector3 min, Vector3 max)> _pieces = new List<(int, bool, Vector3, Vector3)>();
        public const int EdgeSteps = 8;

        public EgoScreen(EgoSolver s)
        {
            S = s;
            _tanH = Mathf.Tan(Rad(s.D.camera.h_fov_deg) / 2);
            _tanV = _tanH * s.D.camera.aspect[1] / s.D.camera.aspect[0];
            var mb = new Dictionary<string, MeshBound>();
            foreach (var b in s.D.mesh_bounds.objects) mb[b.name] = b;
            foreach (var p in s.D.weapon.parts)
                if (mb.TryGetValue(p.id, out var b)) _parts.Add((p.id, V(b.min), V(b.max)));
            foreach (var p in s.D.arm.pieces)
                foreach (bool r in new[] { true, false })
                    if (mb.TryGetValue((r ? "R_" : "L_") + p.id, out var b)) _pieces.Add((s.SegmentIndex(p.segment), r, V(b.min), V(b.max)));
        }

        /// <summary>Punkt im Blender-Kameraraum → (x % B, y % H von oben, Tiefe m); camPitch: Nicken der Kamera (Grad, hoch positiv).</summary>
        public Vector3 ToScreen(Vector3 p, float camPitch = 0)
        {
            if (camPitch != 0) p = RotX(Rad(-camPitch)).MultiplyPoint3x4(p);
            float depth = -p.y;
            return new Vector3(50 + 50 * (-p.x / depth) / _tanH, 50 - 50 * (p.z / depth) / _tanV, depth);
        }

        /// <summary>Kantenpunkte der Netzgrenzen von Waffe (und Armen) im Bild; nur Punkte vor der Kamera und im Bild (0–100 %).</summary>
        public void Silhouette(EgoOutput o, List<Vector2> dst, bool arms = true)
        {
            dst.Clear();
            foreach (var (id, mn, mx) in _parts)
            {
                if (id == S.MagPart && o.magHidden) continue;
                Box(S.World(o, id), mn, mx, o.camPitch, dst);
            }
            if (!arms) return;
            foreach (var (seg, right, mn, mx) in _pieces) Box((right ? o.segR : o.segL)[seg], mn, mx, o.camPitch, dst);
        }

        void Box(Matrix4x4 M, Vector3 mn, Vector3 mx, float pitch, List<Vector2> dst)
        {
            for (int i = 0; i < 8; i++)
                for (int k = 0; k < 3; k++)
                {
                    int j = i ^ (1 << k);
                    if (j < i) continue;
                    Vector3 a = Corner(mn, mx, i), b = Corner(mn, mx, j);
                    for (int t = 0; t <= EdgeSteps; t++)
                    {
                        var s = ToScreen(M.MultiplyPoint3x4(Vector3.Lerp(a, b, t / (float)EdgeSteps)), pitch);
                        if (s.z > 0.02f && s.x >= 0 && s.x <= 100 && s.y >= 0 && s.y <= 100) dst.Add(s);
                    }
                }
        }

        static Vector3 Corner(Vector3 mn, Vector3 mx, int i) =>
            new Vector3((i & 1) != 0 ? mx.x : mn.x, (i & 2) != 0 ? mx.y : mn.y, (i & 4) != 0 ? mx.z : mn.z);
    }
}
