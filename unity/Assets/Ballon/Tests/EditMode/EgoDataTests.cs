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
            ex = Assert.Throws<FormatException>(() => EgoFile.Parse("{\"format\":\"ballon-ego/3\"}"));          // 0.9: ohne secondary.aim_zeta
            StringAssert.Contains("neu exportieren", ex.Message);
            ex = Assert.Throws<FormatException>(() => EgoFile.Parse("{\"format\":\"ballon-ego/4\"}"));          // 0.12: ohne Weltzoom und Hüft-Fadenkreuz
            StringAssert.Contains("neu exportieren", ex.Message);
            ex = Assert.Throws<FormatException>(() => EgoFile.Parse("{\"format\":\"ballon-ego/5\"}"));          // 0.14: Rückstoß ohne Bahn, kein Wechsel
            StringAssert.Contains("neu exportieren", ex.Message);
        }

        // ---------------------------------------------------------------- Weltzoom und Hüft-Fadenkreuz 0.13
        /// <summary>Entscheidungsliste 1.2 A: Weltzoom (Bildmaßstab, Visier-Standard 3) nach Glidepath – Scout 2,0 statt 2,9, Handfeuerwaffe
        /// 1,15 statt 1,5, MP 1,45 statt 1,25, übrige Klassen unverändert; die Pilot-Automatik zoomt mit ihrem Klassenwert 1,9 (vorher
        /// fest 1,35 für alle) und das Spiel nutzt ihn.</summary>
        [Test]
        public void Weltzoom_je_Klasse()
        {
            var G = D.gameplay;
            var want = new Dictionary<string, float> { ["scout_rifle"] = 2.0f, ["hand_cannon"] = 1.15f, ["submachine_gun"] = 1.45f,
                ["auto_rifle"] = 1.9f, ["pulse_rifle"] = 2.0f, ["machine_gun"] = 1.9f, ["sidearm"] = 1.25f, ["grenade_launcher"] = 1.4f,
                ["linear_fusion_rifle"] = 3.8f, ["sniper_rifle"] = 5.5f };
            foreach (var kv in want) Assert.AreEqual(kv.Value, G.ZoomFor(kv.Key), 1e-4f, kv.Key);
            Assert.AreEqual(17, G.zoom_table.Length, "alle Waffentypen");
            Assert.AreEqual("auto_rifle", G.weapon_type);
            Assert.AreEqual("reflex", G.sight);
            Assert.AreEqual(G.ZoomFor(G.weapon_type), G.world_zoom, 1e-6f, "Pilot zoomt mit dem Wert seiner Klasse");
            TestContext.WriteLine($"Weltzoom Pilot {G.world_zoom}, Scout {G.ZoomFor("scout_rifle")}, " +
                                  $"Handfeuerwaffe {G.ZoomFor("hand_cannon")}, MP {G.ZoomFor("submachine_gun")}");
        }

        /// <summary>Entscheidungsliste 4.2 A: Hüftform der Automatik `ring_dot` (vorher `cross`) mit 3,2 % H nach Glidepath, weiß, fein;
        /// im Sprint nur „^“ (`caret`) mit 1,5 % H; Aufgehprofil `auto`. Das gezeichnete Außenmaß trifft die Größe auf 0,5 px.</summary>
        [Test]
        public void Hueftform_der_Automatik_aus_dem_Katalog()
        {
            var H = D.gameplay.hip;
            Assert.AreEqual("ring_dot", H.kind);
            Assert.AreEqual(0.032f, H.share_h, 1e-6f);
            Assert.AreEqual("#EEF2F5", H.color, "weiß");
            Assert.AreEqual(0.65f, H.weight, 1e-6f, "Linienstärke fein");
            Assert.AreEqual("caret", H.sprint.kind);
            Assert.AreEqual(0.015f, H.sprint.share_h, 1e-6f);
            Assert.AreEqual("auto", H.spread.id);
            var R = new HipReticle(H);
            foreach (float h in new[] { 720f, 1080f })
            {
                Assert.AreEqual(H.share_h * h, R.ExtentPx(h), 0.5f, $"Außenmaß gerechnet bei {h} px Höhe");
                var mh = R.Mask(h);                              // unabhängig: Rahmen der Maskenpixel mit Deckung ≥ 50 %
                int x0 = int.MaxValue, x1 = -1, y0 = int.MaxValue, y1 = -1;
                for (int y = 0; y < mh.height; y++)
                    for (int x = 0; x < mh.width; x++)
                        if (mh.GetPixel(x, y).a >= 0.5f * H.opacity) { x0 = Mathf.Min(x0, x); x1 = Mathf.Max(x1, x); y0 = Mathf.Min(y0, y); y1 = Mathf.Max(y1, y); }
                float seen = Mathf.Max(x1 - x0 + 1, y1 - y0 + 1);
                TestContext.WriteLine($"Außenmaß bei {h} px Höhe: Soll {H.share_h * h:0.0} px, Maske {seen} px");
                Assert.AreEqual(H.share_h * h, seen, 1.0f, $"Außenmaß in der Maske bei {h} px Höhe");
            }
            R.Release();
            var m = R.Mask(1080);
            Assert.Greater(m.GetPixel(m.width / 2, m.height / 2).a, 0.8f, "Punkt in der Mitte");
            var ring = H.prims.First(p => p.t == "ring");        // Ringmitte bei Linienstärke fein (innen fest, Dicke · weight)
            float ringR = (ring.ri + (ring.r - ring.ri) * H.weight / 2) * R.PxPerMm(1080);
            Assert.Greater(m.GetPixel(m.width / 2 + Mathf.FloorToInt(ringR), m.height / 2).a / 0.9f, 0.6f, "Ring");
            Assert.Less(m.GetPixel(m.width / 2 + Mathf.FloorToInt(ringR * 0.55f), m.height / 2).a, 0.05f, "frei zwischen Ring und Punkt");
            R.Release();
        }

        /// <summary>Entscheidungsliste 4.1 A: das Hüft-Fadenkreuz geht beim Schießen nach `reticles.SPREAD` auf – Impuls per_shot je
        /// Schuss bis max, Abklingen mit recover_s, Laufen addiert move (reticles.simulate); vorher gab es kein Aufgehen.</summary>
        [Test]
        public void Hueft_Fadenkreuz_geht_nach_SPREAD_auf()
        {
            var H = D.gameplay.hip;
            var S = H.spread;
            var R = new HipReticle(H);
            float e0 = R.ExtentPx(1080);
            Assert.AreEqual(S.@base, R.spread, 1e-6f);
            R.Kick();
            Assert.AreEqual(S.@base + S.per_shot, R.spread, 1e-5f, "ein Schuss");
            Assert.AreEqual(e0 + 2 * S.per_shot * R.PxPerMm(1080), R.ExtentPx(1080), 0.01f, "Ring wächst um per_shot (grow 1)");
            const float dt = 1f / 60f;
            R.Decay(dt, 0);
            Assert.AreEqual(S.@base + S.per_shot * Mathf.Exp(-dt / S.recover_s), R.spread, 1e-5f, "Abklingen");
            for (int k = 0; k < 20; k++) R.Kick();
            Assert.AreEqual(S.max, R.spread, 1e-6f, "begrenzt");
            for (int k = 0; k < 600; k++) R.Decay(dt, 0);
            Assert.AreEqual(S.@base, R.spread, 1e-3f, "zurück zur Basis");
            for (int k = 0; k < 600; k++) R.Decay(dt, 1);
            Assert.AreEqual(S.@base + S.move, R.spread, 1e-3f, "Laufen");
            // wie reticles.simulate('auto', Schüsse bei 720/min, 30/s): je Bild erst abklingen, dann die Schüsse des Bilds
            var R2 = new HipReticle(H);
            float s = S.@base, t = 0;
            int shot = 0;
            for (int i = 0; i <= 30; i++, t = i / 30f)
            {
                R2.Decay(1f / 30f, 0);
                s = S.@base + (s - S.@base) * Mathf.Exp(-(1f / 30f) / S.recover_s);
                while (shot < 6 && shot * 60f / 720f <= t) { R2.Kick(); s = Mathf.Min(S.max, s + S.per_shot); shot++; }
                Assert.AreEqual(s, R2.spread, 1e-5f, $"Bild {i}");
            }
            TestContext.WriteLine($"auto: Außenmaß {e0:0.0} px → nach 6 Schuss {R2.ExtentPx(1080) - 0:0.0} px bei 1080 px Höhe; max {S.max} mm");
        }

        // ---------------------------------------------------------------- Bewegungsgefühl 0.10
        /// <summary>Jede Aktion, die im Zielen endet, bringt das Absehen von seiner Seite auf die Mitte, ohne darüber hinaus zu schwingen
        /// (0.9: 3,3° über die Mitte bei aim_in, „Wippen kurz vor dem Visier“). Gemessen wie in Blender: Richtung Auge → Socket_Reticle.</summary>
        [Test]
        public void Zielen_landet_ohne_Ueberschwingen()
        {
            var S = new EgoSolver(D);
            Vector3 ret = Vector3.zero;
            foreach (var a in D.weapon.anchors) if (a.id == "Socket_Reticle") ret = new Vector3(a.pos[0], a.pos[1], a.pos[2]);
            int n = 0;
            foreach (var A in D.actions)
            {
                if (!A.EndsInAds || A.name == "fire_ads") continue;
                var st = new EgoState();
                float first = float.NaN, worst = 0, atEnd = 0;
                for (int f = 0; f <= A.frames + 20; f++)
                {
                    var t = S.Evaluate(A, Mathf.Min(f, A.frames), st).weapon.MultiplyPoint3x4(ret);
                    float az = Mathf.Atan2(-t.x, -t.y) * Mathf.Rad2Deg;             // Blender-Kameraraum: rechts −X, vorn −Y
                    if (float.IsNaN(first)) first = az;
                    worst = Mathf.Max(worst, -Mathf.Sign(first) * az);            // Ausschlag über die Mitte zur anderen Seite
                    if (f == A.frames) atEnd = Mathf.Abs(az);
                }
                TestContext.WriteLine($"{A.name}: Start {first:0.00}°, Überschwingen {worst:0.00}°, Rest am Ende {atEnd:0.00}°");
                Assert.Less(worst, 0.3f, $"{A.name}: Absehen schwingt {worst:0.00}° über die Mitte (Start {first:0.0}°)");
                Assert.Less(atEnd, 1.5f, $"{A.name}: Absehen hängt am Ende der Aktion {atEnd:0.0}° hinterher");
                n++;
            }
            Assert.GreaterOrEqual(n, 3, "aim_in, sprint_to_aim, draw_aim");
        }

        /// <summary>Sprint-Wippen: vertikal ein Hub je Schritt (2 je Periode), wie Destiny 2 ≈ 3,16 Schritte/s – vorher 6/s („tapsig“).
        /// Hub (3.1 A, 0.15) gemessen wie in Schritt 2 am Bild, hier an der Silhouette von Waffe und Armen (Kanten der Netzgrenzen) über
        /// die Sprintschleife: Oberkante vertikal ≈ 10 % H, linke Kante seitlich ≈ 13 % B wie die Destiny-Automatik (10–11 % H / 13 % B);
        /// bis 0.14 am Unity-Bild 5,1–5,7 % H / 7,0–8,7 % B.</summary>
        [Test]
        public void Sprintschritt_wie_ein_Laeufer()
        {
            var B = D.Action("sprint").bob;
            float steps = 2f * D.fps / B.period;
            Assert.That(steps, Is.InRange(2.9f, 3.4f), $"Sprint: {steps:0.00} Schritte/s (Destiny 2: 3,16 Hz, Motiongen REF 0.23)");
            Assert.IsTrue(B.u, "Sprint-Bahn als U-Bogen (oben an den Seitenumkehren) wie Destiny 2");
            var W = D.Action("walk").bob;
            Assert.Less(2f * D.fps / W.period, steps, "Gehen langsamer als Sprint");

            var S = new EgoSolver(D);
            var E = new EgoScreen(S);
            var A = D.Action("sprint");
            var st = new EgoState();
            var pts = new List<Vector2>();
            float t0 = float.MaxValue, t1 = float.MinValue, l0 = float.MaxValue, l1 = float.MinValue;
            for (int f = 0; f <= A.frames; f++)
            {
                var o = S.Evaluate(A, f, st);
                if (f < B.start + 4 || f > B.end - 4) continue;              // volle Wipp-Weite (4 Bilder Ein-/Ausblenden)
                E.Silhouette(o, pts);
                float top = pts.Min(p => p.y), left = pts.Min(p => p.x);
                t0 = Mathf.Min(t0, top); t1 = Mathf.Max(t1, top); l0 = Mathf.Min(l0, left); l1 = Mathf.Max(l1, left);
            }
            Assert.GreaterOrEqual(B.end - B.start - 8, B.period, "mindestens eine ganze Seitenperiode ausgewertet");
            TestContext.WriteLine($"Sprint-Hub an der Silhouette: Oberkante {t1 - t0:0.0} % H (y {t0:0.0}–{t1:0.0}), linke Kante " +
                                  $"{l1 - l0:0.0} % B (x {l0:0.0}–{l1:0.0}); Hub {B.amp[0] * 1000:0} / {B.amp[1] * 1000:0} mm, Rollen ±{B.roll}°");
            Assert.That(t1 - t0, Is.InRange(8.5f, 12.5f), "vertikal ≈ 10 % H (Destiny-Automatik 10–11 % H)");
            Assert.That(l1 - l0, Is.InRange(11f, 15.5f), "seitlich ≈ 13 % B (Destiny-Automatik 13 % B)");
        }

        // ---------------------------------------------------------------- Haltung 0.15
        /// <summary>Entscheidungsliste 2.1 A: in der Hüfte liegt die Mündung rechts unter der Mitte wie bei Destiny (lange Waffen, 21
        /// Beispiele, Motiongen huefte › 4): x 54–59 / y 60–71 %, die hintere Visieröffnung 7–34 pp rechts der Mündung, die Kontur reicht
        /// bis zum rechten und unteren Rand. Gemessen wie das Ego-Still (Bild 0). Bis 0.14 Mündung x 58,8 / y 49,6 % (10 pp zu hoch).</summary>
        [Test]
        public void Hueftlage_im_Destiny_Band()
        {
            var S = new EgoSolver(D);
            var E = new EgoScreen(S);
            var o = S.Evaluate(S.StillAction("hip"), 0, new EgoState());
            Vector3 At(string a) => E.ToScreen(o.weapon.MultiplyPoint3x4(V(D.Anchor(a).pos)));
            Vector3 m = At("Socket_Muzzle"), s = At("Socket_Sight"), r = At("Socket_Reticle");
            var pts = new List<Vector2>();
            E.Silhouette(o, pts, arms: false);
            TestContext.WriteLine($"Hüfte: Mündung x {m.x:0.0} / y {m.y:0.0} %, Visier hinten x {s.x:0.0} / y {s.y:0.0} % ({s.x - m.x:0.0} pp rechts), " +
                                  $"Absehen x {r.x:0.0} / y {r.y:0.0} %; Waffe x {pts.Min(p => p.x):0.0}–{pts.Max(p => p.x):0.0}, y {pts.Min(p => p.y):0.0}–{pts.Max(p => p.y):0.0} %");
            Assert.That(m.x, Is.InRange(54f, 59f), "Mündung x (Destiny 54–59 %)");
            Assert.That(m.y, Is.InRange(60f, 71f), "Mündung y (Destiny 60–71 %)");
            Assert.That(s.x - m.x, Is.InRange(7f, 34f), "hintere Visieröffnung rechts der Mündung (Destiny 7–34 pp)");
            Assert.Greater(pts.Max(p => p.x), 99f, "Kontur reicht bis zum rechten Rand");
            Assert.Greater(pts.Max(p => p.y), 99f, "Kontur reicht bis zum unteren Rand");
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
