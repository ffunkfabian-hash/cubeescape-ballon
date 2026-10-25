// EditMode: JSON-Format, Achsumrechnung (Daten und FBX-Import), Armlängen, Handgelenkknick, Gleichheit mit der Blender-Referenz.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;
using static Ballon.Ego.BMath;

namespace Ballon.Ego.Tests
{
    public class EgoDataTests
    {
        const string Gen = "Assets/Ballon/Generated";
        static EgoFile _d;
        static EgoFile D => _d ?? (_d = EgoFile.Parse(File.ReadAllText($"{Gen}/ego.json")));

        [Serializable] class RefObj { public string name; public float[] m; }
        [Serializable] class RefSample { public string label, action; public int frame; public RefObj[] objects; }
        [Serializable] class RefFile { public string format; public float tolerance_m, tolerance_deg; public RefSample[] samples; }

        static Matrix4x4 M(float[] a)
        {
            var m = new Matrix4x4();
            for (int i = 0; i < 16; i++) m[i / 4, i % 4] = a[i];
            return m;
        }

        /// <summary>Größter Winkel zwischen gleichnamigen Achsen (atan2, genau auch unter 0,1°; Quaternion.Angle rundet darunter auf 0).</summary>
        static float RotDiffDeg(Matrix4x4 a, Matrix4x4 b)
        {
            double w = 0;
            for (int i = 0; i < 3; i++)
            {
                Vector3 x = Col(a, i), y = Col(b, i);
                w = Math.Max(w, Math.Atan2(Vector3.Cross(x, y).magnitude, Vector3.Dot(x, y)));
            }
            return (float)(w * 180 / Math.PI);
        }

        // ---------------------------------------------------------------- Format
        [Test]
        public void Format_und_Umfang()
        {
            Assert.AreEqual(EgoFile.Format, D.format);
            Assert.AreEqual(30, D.fps);
            Assert.AreEqual(75f, D.camera.h_fov_deg);
            Assert.AreEqual(10, D.poses.Length, "Haltungen");
            Assert.AreEqual(4, D.grips.Length, "Griffe");
            Assert.AreEqual(19, D.actions.Length, "Aktionen");
            Assert.GreaterOrEqual(D.weapon.parts.Length, 70, "Waffenteile (Pilot v2.1)");
            var meshes = new HashSet<string>(D.mesh_bounds.objects.Select(o => o.name));
            Assert.IsTrue(D.weapon.parts.All(p => meshes.Contains(p.id)), "jedes Teil hat ein Netz im Export");
            Assert.AreEqual(3, D.arm.rig_version);
            Assert.AreEqual(4, D.arm.finger_x.Length, "vier Finger");
            foreach (var f in D.finger_poses)
            {
                Assert.AreEqual(12, f.f.Length, f.name);
                Assert.AreEqual(3, f.t.Length, f.name);
            }
            foreach (var A in D.actions)
            {
                Assert.Greater(A.frames, 0, A.name);
                foreach (var k in A.weapon) Assert.DoesNotThrow(() => D.Pose(k.pose), A.name);
                foreach (var k in A.L.Concat(A.R)) Assert.DoesNotThrow(() => D.Grip(k.grip), A.name);
                foreach (var k in A.fL.Concat(A.fR)) Assert.DoesNotThrow(() => D.Fingers(k.pose), A.name);
                var fr = A.weapon.Select(k => k.f).ToArray();
                CollectionAssert.IsOrdered(fr, A.name);
                Assert.LessOrEqual(fr.Last(), A.frames, A.name);
                CollectionAssert.IsOrdered(A.events.Select(e => e.f).ToArray(), A.name + " Marker");
            }
            foreach (var n in new[] { "Socket_Hand", "Socket_SupportHand", "Socket_Sight", "Socket_Eye", "Socket_Charge" })
                Assert.DoesNotThrow(() => D.Anchor(n));
            Assert.Greater(D.gameplay.rpm, 0);
            Assert.Greater(D.gameplay.magazine, 0);
        }

        [Test]
        public void Falsches_Format_wird_abgelehnt()
        {
            Assert.Throws<FormatException>(() => EgoFile.Parse("{\"format\":\"ballon-ego/1\"}"));    // alter Export ohne Texturen
            var ex = Assert.Throws<FormatException>(() => EgoFile.Parse("{\"format\":\"ballon-ego/2\"}"));   // 0.7: mask statt spec, keine Skins
            StringAssert.Contains("neu exportieren", ex.Message);
        }

        // ---------------------------------------------------------------- Achsen
        [Test]
        public void Achsumrechnung_Blender_nach_Unity()
        {
            var C = D.toUnity;
            Assert.AreEqual(-1f, C.determinant, 1e-6f, "Spiegelung rechts- → linkshändig");
            Assert.That(Vector3.Distance(C.MultiplyVector(new Vector3(0, -1, 0)), Vector3.forward), Is.LessThan(1e-6f), "vorn");
            Assert.That(Vector3.Distance(C.MultiplyVector(new Vector3(0, 0, 1)), Vector3.up), Is.LessThan(1e-6f), "oben");
            Assert.That(Vector3.Distance(C.MultiplyVector(new Vector3(-1, 0, 0)), Vector3.right), Is.LessThan(1e-6f), "rechts");
            // Autorenmaß: Mündung (f vorn, u oben) liegt in Unity vorn und oben
            var muz = C.MultiplyVector(V(D.Anchor("Socket_Muzzle").pos));
            Assert.Greater(muz.z, 0.5f);
            Assert.Greater(muz.y, 0.05f);
            Assert.AreEqual(0f, muz.x, 1e-6f);
            // Drehungen bleiben eigentliche Drehungen; Drehsinn: Rechte-Hand-Drehung in Blender ↔ gleiche Abbildung in Unity
            var R = Rot(Rad(30), new Vector3(0, 0, 1)) * Rot(Rad(-20), new Vector3(1, 0, 0));
            ToUnity(C, R, out _, out var q);
            var p = new Vector3(0.1f, -0.3f, 0.2f);
            Assert.That(Vector3.Distance(q * C.MultiplyVector(p), C.MultiplyVector(R.MultiplyVector(p))), Is.LessThan(1e-5f));
        }

        static Bounds UnityBounds(MeshBound b, Matrix4x4 C)
        {
            var mn = V(b.min);
            var mx = V(b.max);
            var bb = new Bounds(C.MultiplyVector(mn), Vector3.zero);
            for (int i = 0; i < 8; i++)
                bb.Encapsulate(C.MultiplyVector(new Vector3((i & 1) == 0 ? mn.x : mx.x, (i & 2) == 0 ? mn.y : mx.y, (i & 4) == 0 ? mn.z : mx.z)));
            return bb;
        }

        [Test]
        public void FBX_Import_passt_zur_Achsumrechnung()
        {
            var bounds = D.mesh_bounds.objects.ToDictionary(o => o.name);
            int n = 0;
            foreach (var f in new[] { D.weapon.fbx, D.arm.fbx })
            {
                var go = AssetDatabase.LoadAssetAtPath<GameObject>($"{Gen}/{f}");
                Assert.IsNotNull(go, f);
                foreach (var mf in go.GetComponentsInChildren<MeshFilter>(true))
                {
                    Assert.IsTrue(bounds.TryGetValue(mf.name, out var b), $"{mf.name} fehlt in mesh_bounds");
                    var want = UnityBounds(b, D.toUnity);
                    var got = mf.sharedMesh.bounds;
                    Assert.That(Vector3.Distance(got.min, want.min), Is.LessThan(5e-4f), $"{mf.name} min {got.min:F4} statt {want.min:F4}");
                    Assert.That(Vector3.Distance(got.max, want.max), Is.LessThan(5e-4f), $"{mf.name} max {got.max:F4} statt {want.max:F4}");
                    Assert.That(Vector3.Distance(mf.transform.localScale, Vector3.one), Is.LessThan(1e-5f), $"{mf.name} Skalierung");
                    n++;
                }
            }
            Assert.AreEqual(D.weapon.parts.Length + D.arm.pieces.Length * 2, n, "Netzobjekte");
        }

        [Test]
        public void FBX_Ruhelagen_und_Anker_wie_in_den_Daten()
        {
            var go = AssetDatabase.LoadAssetAtPath<GameObject>($"{Gen}/{D.weapon.fbx}");
            var all = go.GetComponentsInChildren<Transform>(true).ToDictionary(t => t.name);
            var root = all[D.weapon.root];
            Assert.That(root.localPosition.magnitude, Is.LessThan(1e-6f), "Wurzel im Ursprung");
            Assert.That(Quaternion.Angle(root.localRotation, Quaternion.identity), Is.LessThan(0.01f), "Wurzel ohne Drehung (Achsen gebacken)");
            foreach (var p in D.weapon.parts)
            {
                var want = D.toUnity.MultiplyVector(V(p.rest));
                var got = root.InverseTransformPoint(all[p.id].position);
                Assert.That(Vector3.Distance(got, want), Is.LessThan(1e-4f), $"{p.id}: {got:F4} statt {want:F4}");
                Assert.That(Quaternion.Angle(Quaternion.Inverse(root.rotation) * all[p.id].rotation, Quaternion.identity), Is.LessThan(0.01f), p.id);
            }
            foreach (var a in D.weapon.anchors)
            {
                var want = D.toUnity.MultiplyVector(V(a.pos));
                var got = root.InverseTransformPoint(all[a.id].position);
                Assert.That(Vector3.Distance(got, want), Is.LessThan(1e-4f), $"{a.id}: {got:F4} statt {want:F4}");
            }
            var arms = AssetDatabase.LoadAssetAtPath<GameObject>($"{Gen}/{D.arm.fbx}");
            var at = arms.GetComponentsInChildren<Transform>(true).ToDictionary(t => t.name);
            foreach (var s in D.arm.segments)
                foreach (var side in new[] { "R_", "L_" })
                    Assert.That(at[side + s].position.magnitude, Is.LessThan(1e-5f), side + s);
        }

        // ---------------------------------------------------------------- Material (0.7)
        [Test]
        public void Gebackene_Atlanten_und_UVs()
        {
            Assert.IsNotNull(D.textures?.weapon, "textures fehlt (Export mit Backen)");
            int n = 0;
            foreach (var (fbx, A) in new[] { (D.weapon.fbx, D.textures.weapon), (D.arm.fbx, D.textures.arms) })
            {
                foreach (var f in new[] { A.albedo, A.spec, A.normal, A.ao })
                {
                    var t = AssetDatabase.LoadAssetAtPath<Texture2D>($"{Gen}/Textures/{f}");
                    Assert.IsNotNull(t, f);
                    Assert.AreEqual(A.size, t.width, f);
                }
                var baked = new HashSet<string>(A.objects);
                var go = AssetDatabase.LoadAssetAtPath<GameObject>($"{Gen}/{fbx}");
                foreach (var mf in go.GetComponentsInChildren<MeshFilter>(true))
                {
                    if (!baked.Contains(mf.name)) continue;
                    var uv = mf.sharedMesh.uv;
                    Assert.AreEqual(mf.sharedMesh.vertexCount, uv.Length, $"{mf.name}: UVs");
                    Assert.IsTrue(uv.All(u => u.x >= -1e-3f && u.x <= 1.001f && u.y >= -1e-3f && u.y <= 1.001f), $"{mf.name}: UV im Atlas");
                    n++;
                }
                var m = AssetDatabase.LoadAssetAtPath<Material>($"{Gen}/Materials/Atlas_{(fbx == D.weapon.fbx ? "weapon" : "arms")}.mat");
                Assert.IsNotNull(m.GetTexture("_BaseMap"));
                Assert.IsNotNull(m.GetTexture("_SpecGlossMap"));
                Assert.AreEqual(0f, m.GetFloat("_WorkflowMode"), "Spezular-Modus");
                Assert.IsNotNull(m.GetTexture("_BumpMap"));
                Assert.IsNotNull(m.GetTexture("_OcclusionMap"));
            }
            Assert.Greater(n, 150, "gebackene Netzobjekte");
        }

        [Test]
        public void Skins_gebacken_mit_Materialien()
        {
            var sk = D.textures.skins;
            Assert.AreEqual(8, sk.Length, "kit.SKINS: 8 Skins");
            Assert.AreEqual("standard", sk[0].name);
            var names = new HashSet<string>();
            foreach (var s in sk)
            {
                Assert.IsTrue(names.Add(s.name), s.name);
                foreach (var f in new[] { s.albedo, s.spec })
                {
                    var t = AssetDatabase.LoadAssetAtPath<Texture2D>($"{Gen}/Textures/{f}");
                    Assert.IsNotNull(t, f);
                    Assert.AreEqual(D.textures.weapon.size, t.width, f);
                }
                if (s.name == "standard") continue;
                var m = AssetDatabase.LoadAssetAtPath<Material>($"{Gen}/Materials/Atlas_weapon_{s.name}.mat");
                Assert.IsNotNull(m, s.name);
                Assert.AreEqual(s.albedo, m.GetTexture("_BaseMap").name + ".png", s.name);
                Assert.IsNotNull(m.GetTexture("_BumpMap"), s.name + ": Normale wie Standard");
            }
        }

        [Test]
        public void AgX_LUT_wie_Blender()
        {
            var L = D.textures.lut;
            var t = AssetDatabase.LoadAssetAtPath<Texture2D>($"{Gen}/Textures/{L.file}");
            Assert.AreEqual(L.size * L.size, t.width);
            Assert.AreEqual(L.size, t.height);
            // Mittelgrau 0,18 → Gitterpunkt u = −ev0 / (ev1 − ev0) (genau 20 bei 34 Punkten); Blender AgX „Medium High Contrast“: 0,461
            float gi = -L.ev[0] / (L.ev[1] - L.ev[0]) * (L.size - 1);
            Assert.AreEqual(Mathf.Round(gi), gi, 1e-4f, "Mittelgrau auf dem Gitter");
            Assert.AreEqual(16.29f, L.mid_grey * Mathf.Pow(2, L.ev[1]), 0.05f, "obere Grenze wie AgX (log2 +4,03)");
            int i = Mathf.RoundToInt(gi);
            var c = t.GetPixel(i + i * L.size, i);
            Assert.AreEqual(0.461f, c.r, 0.01f, "Mittelgrau (Blender AgX MHC: 0,18 → 0,461)");
            Assert.AreEqual(c.r, c.g, 0.005f);
            Assert.Less(t.GetPixel(0, 0).r, 0.01f, "Schwarz");
            Assert.Greater(t.GetPixel(t.width - 1, t.height - 1).r, 0.9f, "Weiß");
        }

        // ---------------------------------------------------------------- Arme
        static IEnumerable<(string, EgoOutput)> AllFrames()
        {
            var S = new EgoSolver(D);
            foreach (var p in D.poses)
                yield return ("Haltung " + p.name, S.Evaluate(S.StillAction(p.name), 0, new EgoState()));
            foreach (var A in D.actions)
            {
                var st = new EgoState();
                for (int f = 0; f <= A.frames; f++) yield return ($"{A.name}:{f}", S.Evaluate(A, f, st));
            }
        }

        [Test]
        public void Armlaengen_in_allen_Bildern()
        {
            var S = new EgoSolver(D);
            int iu = S.SegmentIndex("upper"), ifo = S.SegmentIndex("fore"), ih = S.SegmentIndex("hand");
            int n = 0;
            foreach (var (lab, o) in AllFrames())
                foreach (var seg in new[] { o.segR, o.segL })
                {
                    Assert.AreEqual(D.arm.upper_m, Vector3.Distance(Pos(seg[iu]), Pos(seg[ifo])), 1e-4f, lab + " Oberarm");
                    Assert.AreEqual(D.arm.fore_m, Vector3.Distance(Pos(seg[ifo]), Pos(seg[ih])), 1e-4f, lab + " Unterarm");
                    n++;
                }
            Assert.AreEqual(0.32f, D.arm.upper_m, 1e-6f);
            Assert.AreEqual(0.30f, D.arm.fore_m, 1e-6f);
            Assert.Greater(n, 1000);
        }

        [Test]
        public void Handgelenkknick_hoechstens_45_Grad()
        {
            float worst = 0;
            string at = "";
            foreach (var (lab, o) in AllFrames())
                if (o.wristBendMaxDeg > worst) { worst = o.wristBendMaxDeg; at = lab; }
            Assert.AreEqual(45f, D.arm.wrist_target_deg);
            Assert.LessOrEqual(worst, D.arm.wrist_target_deg + 0.01f, $"größter Knick {worst:0.0}° bei {at}");
            TestContext.WriteLine($"größter Handgelenkknick {worst:0.0}° ({at})");
        }

        // ---------------------------------------------------------------- Referenz
        [Test]
        public void Gleich_wie_Blender_Referenz()
        {
            var R = JsonUtility.FromJson<RefFile>(File.ReadAllText($"{Gen}/ego_reference.json"));
            Assert.AreEqual(EgoFile.Format + "-reference", R.format);
            var S = new EgoSolver(D);
            var byAction = R.samples.Where(s => !s.label.StartsWith("still:")).GroupBy(s => s.action).ToDictionary(g => g.Key, g => g.ToDictionary(s => s.frame));
            float worstP = 0, worstR = 0;
            string wp = "", wr = "";
            int checks = 0;
            void Compare(RefSample s, EgoOutput o)
            {
                foreach (var ob in s.objects)
                {
                    Matrix4x4 got;
                    if (ob.name == "weapon") got = o.weapon;
                    else if (ob.name == "camera") got = RotX(Rad(o.camPitch));
                    else if (ob.name.StartsWith("R_")) got = o.segR[S.SegmentIndex(ob.name.Substring(2))];
                    else if (ob.name.StartsWith("L_")) got = o.segL[S.SegmentIndex(ob.name.Substring(2))];
                    else got = S.World(o, ob.name);
                    var want = M(ob.m);
                    float dp = Vector3.Distance(Pos(got), Pos(want)), dr = RotDiffDeg(got, want);
                    if (dp > worstP) { worstP = dp; wp = $"{s.label} {ob.name}"; }
                    if (dr > worstR) { worstR = dr; wr = $"{s.label} {ob.name}"; }
                    checks++;
                }
            }
            foreach (var s in R.samples.Where(s => s.label.StartsWith("still:")))
                Compare(s, S.Evaluate(S.StillAction(s.label.Substring(6)), 0, new EgoState()));
            foreach (var A in D.actions)
            {
                Assert.IsTrue(byAction.TryGetValue(A.name, out var frames), $"Referenz für {A.name} fehlt");
                var st = new EgoState();
                for (int f = 0; f <= A.frames; f++)
                {
                    var o = S.Evaluate(A, f, st);
                    if (frames.TryGetValue(f, out var s)) Compare(s, o);
                }
            }
            TestContext.WriteLine($"{checks} Matrizen, größte Abweichung {worstP * 1000:0.000} mm ({wp}), {worstR:0.000}° ({wr})");
            Assert.LessOrEqual(worstP, R.tolerance_m, $"Lage {worstP * 1000:0.000} mm bei {wp}");
            Assert.LessOrEqual(worstR, R.tolerance_deg, $"Drehung {worstR:0.000}° bei {wr}");
            Assert.Greater(checks, 5000);
        }
    }
}
