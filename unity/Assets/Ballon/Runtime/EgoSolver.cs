// Ego-Auswertung in C#: Übertragung von tools/ego_build.py (pose_matrix, weapon_at, grip_hand, hand_target, blend_hand,
// blend_fingers, solve_arm, Scene.set_weapon, evaluate; Bewegung v2: curve/mats_curve, spring_step, secondary, Rückstoßfeder).
// Rechnet im Blender-Kameraraum; EgoRig wandelt nach Unity.
// Evaluate() ist die Referenz (gleiche Formeln wie Blender, von EditMode-Tests gegen ego_reference.json geprüft);
// EgoController setzt dieselben Schritte einzeln zusammen und ersetzt die geskripteten Ebenen durch live gerechnete.
using System;
using System.Collections.Generic;
using UnityEngine;
using static Ballon.Ego.BMath;

namespace Ballon.Ego
{
    /// <summary>Zusatzebenen auf der Waffenhaltung: Lage im Kameraraum, Drehung in Waffenachsen, Kamera-Nicken (Grad).</summary>
    public struct Layers
    {
        public Vector3 pos;
        public Matrix4x4 rot;
        public float camPitch;
        public float trigger, bolt, port;   // Mechanik beim Feuern, < 0 = aus der Aktion

        public static Layers None => new Layers { rot = Matrix4x4.identity, trigger = -1, bolt = -1, port = -1 };
    }

    public sealed class EgoOutput
    {
        public Matrix4x4 weapon;                                   // Socket_Hand-Rahmen der Waffe (WM)
        public readonly Dictionary<string, float> mech = new Dictionary<string, float>();
        public readonly Dictionary<string, Matrix4x4> movers = new Dictionary<string, Matrix4x4>();   // Weltmatrix bewegter Teile
        public bool magOverride, magHidden;
        public Matrix4x4 magWorld;
        public Matrix4x4 handL, handR;
        public float[] fingersL = new float[15], fingersR = new float[15];
        public Matrix4x4[] segL, segR;
        public float camPitch, wristBendMaxDeg;                    // camPitch: Viewmodel-Kamera (Hüfte: Kamera-Ruck)
        public float worldPitch, worldYaw;                         // Weltkamera gegen den Kopf (Grad): Grundbahn + Kamera-Ruck (live)
        public int overreach;
    }

    /// <summary>Zustand einer Aktionsauswertung (ego_build: state) – Magazin, Feder-Nachlauf, Rückstoßfeder.</summary>
    public sealed class EgoState
    {
        public bool hasRel;
        public Matrix4x4 rel;
        public bool hasSec;
        public Vector3 secP, secV, secAv;
        public Quaternion secQ;
        public float secF;
        public bool hasRec;
        public Vector3 recX, recV, recCx, recCv;
        public float recF;
    }

    public sealed class EgoSolver
    {
        public readonly EgoFile D;
        public readonly int fps;
        readonly Vector3 _eyeLocal, _palmCenter;
        readonly List<EgoPart> _movers = new List<EgoPart>();
        readonly Dictionary<string, int> _seg = new Dictionary<string, int>();
        readonly int[,] _fingerSeg;
        readonly int[] _thumbSeg;
        readonly Matrix4x4 _magRelLocal;

        public EgoSolver(EgoFile d)
        {
            D = d;
            fps = d.fps;
            _eyeLocal = V(d.Anchor("Socket_Eye").pos);
            _palmCenter = V(d.arm.palm_center);
            foreach (var p in d.weapon.parts)
                if (p.move.kind != "none" && string.IsNullOrEmpty(p.parent)) _movers.Add(p);
            foreach (var p in d.weapon.parts)
                if (p.move.kind != "none" && !string.IsNullOrEmpty(p.parent)) _movers.Add(p);
            foreach (var p in _movers)
                if (p.move.kind != "translate" && p.move.kind != "rotate" && p.move.kind != "glow")
                    throw new NotSupportedException($"Bewegungsart {p.move.kind} an {p.id}");
            for (int i = 0; i < d.arm.segments.Length; i++) _seg[d.arm.segments[i]] = i;
            _fingerSeg = new int[d.arm.finger_x.Length, d.arm.finger_links.Length];
            for (int i = 0; i < d.arm.finger_x.Length; i++)
                for (int j = 0; j < d.arm.finger_links.Length; j++) _fingerSeg[i, j] = _seg[$"f{i}_{j}"];
            _thumbSeg = new int[d.arm.thumb_links.Length];
            for (int j = 0; j < _thumbSeg.Length; j++) _thumbSeg[j] = _seg[$"t_{j}"];
            if (d.HasPart("magazine"))   // ego_build: rel = Hm⁻¹ · (WM · rest); WM kürzt sich heraus
                _magRelLocal = GripHand("mag", _ => Matrix4x4.identity, Vector3.zero).inverse * Rest("magazine");
        }

        public List<EgoPart> Movers => _movers;
        public int SegmentIndex(string s) => _seg[s];
        public EgoOutput NewOutput() => new EgoOutput { segL = new Matrix4x4[D.arm.segments.Length], segR = new Matrix4x4[D.arm.segments.Length] };

        // -------------------------------------------------------------- Waffe
        public Matrix4x4 PoseMatrix(string name, WeaponKey off = null)
        {
            var P = D.Pose(name);
            var d = (P.ads ? V(P.aim_dir) : V(P.aim) - V(P.pos)).normalized;
            var up = new Vector3(0, 0, 1);
            var u = (up - d * Vector3.Dot(up, d)).normalized;
            var left = Vector3.Cross(-d, u);
            var R = Cols(left, -d, u, Vector3.zero);
            float roll = P.roll + (off?.roll ?? 0);
            R = Rot(Rad(-roll), d) * R;
            R = R * RotX(Rad(-(off?.pitch ?? 0))) * RotZ(Rad(off?.yaw ?? 0));    // pitch + = Mündung hoch, yaw + = nach links
            var pos = P.ads ? V(P.eye) - R.MultiplyVector(_eyeLocal) : V(P.pos);
            if (off != null) pos += new Vector3(-off.right, off.back, off.up);
            return WithPos(R, pos);
        }

        public Matrix4x4 PoseMatrix(WeaponKey k) => PoseMatrix(k.pose, k);

        readonly Dictionary<WeaponKey, Matrix4x4> _poseCache = new Dictionary<WeaponKey, Matrix4x4>();

        Matrix4x4 PoseCached(WeaponKey k)
        {
            if (!_poseCache.TryGetValue(k, out var m)) _poseCache[k] = m = PoseMatrix(k);
            return m;
        }

        /// <summary>ego_build.weapon_at (v2): Kurve durch alle Schlüssel der Aktion.</summary>
        // Zwischenspeicher je Schlüsselliste (die Aktionen sind fest): keine Speicheranforderung im laufenden Bild
        readonly Dictionary<object, float[]> _ts = new Dictionary<object, float[]>();
        readonly Dictionary<WeaponKey[], Matrix4x4[]> _poseMs = new Dictionary<WeaponKey[], Matrix4x4[]>();
        readonly Dictionary<FingerKey[], float[][]> _fingerVs = new Dictionary<FingerKey[], float[][]>();
        readonly Dictionary<int, Matrix4x4[]> _handMs = new Dictionary<int, Matrix4x4[]>();
        readonly Dictionary<int, float[][]> _curveVs = new Dictionary<int, float[][]>();
        readonly float[] _curveOut = new float[7];

        float[] Times<TK>(TK[] keys, Func<TK, float> f)     // f ohne Erfassung: der Compiler hält den Delegaten fest
        {
            if (_ts.TryGetValue(keys, out var ts)) return ts;
            ts = new float[keys.Length];
            for (int i = 0; i < ts.Length; i++) ts[i] = f(keys[i]);
            return _ts[keys] = ts;
        }

        public Matrix4x4 WeaponAt(WeaponKey[] keys, float f)
        {
            var ts = Times(keys, k => k.f);
            if (!_poseMs.TryGetValue(keys, out var ms))
            {
                ms = new Matrix4x4[keys.Length];
                for (int i = 0; i < keys.Length; i++) ms[i] = PoseCached(keys[i]);
                _poseMs[keys] = ms;
            }
            return MatsCurve(ts, ms, f);
        }

        // -------------------------------------------------------------- Kurven und Federn (Bewegung v2)
        /// <summary>ego_build.curve: monotone kubische Hermite-Kurve durch Schlüsselwerte; Tangente 0 an Halt, Umkehr und Enden.</summary>
        public static void Curve(float[] ts, float[][] vs, float f, float[] dst)
        {
            int n = ts.Length, m = dst.Length;
            if (f <= ts[0]) { Array.Copy(vs[0], dst, m); return; }
            if (f >= ts[n - 1]) { Array.Copy(vs[n - 1], dst, m); return; }
            int i = 0;
            for (int k = 0; k < n - 1; k++) if (ts[k] <= f) i = k;
            float h = ts[i + 1] - ts[i];
            if (h <= 0) { Array.Copy(vs[i + 1], dst, m); return; }
            float s = (f - ts[i]) / h, s2 = s * s, s3 = s2 * s;
            float h00 = 2 * s3 - 3 * s2 + 1, h10 = s3 - 2 * s2 + s, h01 = -2 * s3 + 3 * s2, h11 = s3 - s2;
            for (int c = 0; c < m; c++)
                dst[c] = h00 * vs[i][c] + h10 * h * Tan(ts, vs, i, c) + h01 * vs[i + 1][c] + h11 * h * Tan(ts, vs, i + 1, c);
        }

        static float Tan(float[] ts, float[][] vs, int k, int c)
        {
            int n = ts.Length;
            if (k == 0 || k == n - 1) return 0;
            float h0 = ts[k] - ts[k - 1], h1 = ts[k + 1] - ts[k];
            float d0 = h0 > 0 ? (vs[k][c] - vs[k - 1][c]) / h0 : 0, d1 = h1 > 0 ? (vs[k + 1][c] - vs[k][c]) / h1 : 0;
            if (d0 * d1 <= 0) return 0;
            float mm = (d0 + d1) / 2, lim = 3 * Mathf.Min(Mathf.Abs(d0), Mathf.Abs(d1));
            return Mathf.Clamp(mm, -lim, lim);
        }

        /// <summary>ego_build.mats_curve: Lage und Quaternion (auf eine Halbkugel gelegt) komponentenweise, normiert.</summary>
        public Matrix4x4 MatsCurve(float[] ts, Matrix4x4[] Ms, float f)
        {
            if (!_curveVs.TryGetValue(Ms.Length, out var vs))
            {
                vs = new float[Ms.Length][];
                for (int i = 0; i < vs.Length; i++) vs[i] = new float[7];
                _curveVs[Ms.Length] = vs;
            }
            Quaternion qp = default;
            for (int i = 0; i < Ms.Length; i++)
            {
                var q = QuatFrom(Ms[i]);
                if (i > 0 && Quaternion.Dot(q, qp) < 0) q = new Quaternion(-q.x, -q.y, -q.z, -q.w);
                qp = q;
                var p = Pos(Ms[i]);
                var r = vs[i];
                r[0] = p.x; r[1] = p.y; r[2] = p.z; r[3] = q.w; r[4] = q.x; r[5] = q.y; r[6] = q.z;
            }
            var v = _curveOut;
            Curve(ts, vs, f, v);
            var rq = new Quaternion(v[4], v[5], v[6], v[3]).normalized;
            return Matrix4x4.TRS(new Vector3(v[0], v[1], v[2]), rq, Vector3.one);
        }

        /// <summary>ego_build.spring_step: gedämpfte Feder, halbimplizit in Unterschritten.</summary>
        public static void SpringStep(ref Vector3 x, ref Vector3 v, Vector3 target, float w, float zeta, float dt, int sub = 4)
        {
            float h = dt / sub;
            for (int k = 0; k < sub; k++)
            {
                var a = (target - x) * (w * w) - v * (2 * zeta * w);
                v += a * h;
                x += v * h;
            }
        }

        /// <summary>Drehfeder: Quaternion q folgt qt (ego_build.secondary, Drehanteil) über dt in Unterschritten.</summary>
        public static void SpringRot(ref Quaternion q, ref Vector3 av, Quaternion qt, float w, float zeta, float dt, int sub = 4)
        {
            float h = dt / sub;
            for (int k = 0; k < sub; k++)
            {
                var dq = qt * Quaternion.Inverse(q);
                if (dq.w < 0) dq = new Quaternion(-dq.x, -dq.y, -dq.z, -dq.w);
                float ang = 2 * Mathf.Acos(Mathf.Clamp(dq.w, -1f, 1f));
                var err = Vector3.zero;
                if (ang > 1e-9f)
                {
                    float sn = Mathf.Sqrt(Mathf.Max(0, 1 - dq.w * dq.w));
                    if (sn > 1e-9f) err = new Vector3(dq.x, dq.y, dq.z) / sn * ang;
                }
                av += (err * (w * w) - av * (2 * zeta * w)) * h;
                float a = av.magnitude * h;
                if (a > 1e-12f) q = Quaternion.AngleAxis(a * Mathf.Rad2Deg, av.normalized) * q;
            }
        }

        /// <summary>ego_build.secondary: Waffe folgt ihrer Kurve über Federn (ganze Bilder, wie die Blender-Auswertung).</summary>
        public Matrix4x4 Secondary(Matrix4x4 target, float f, EgoState st, bool aim = false)
        {
            var S2 = D.motion.secondary;
            float w = 2 * Mathf.PI * (aim ? S2.aim_freq_hz : S2.freq_hz), z = aim ? S2.aim_zeta : S2.zeta, dt = 1f / fps;
            var qt = QuatFrom(target);
            var pos = Pos(target);
            if (!st.hasSec)
            {
                st.hasSec = true;
                st.secP = pos; st.secV = Vector3.zero; st.secQ = qt; st.secAv = Vector3.zero; st.secF = f;
                return target;
            }
            int steps = Mathf.Max(1, Mathf.RoundToInt(f - st.secF));
            for (int k = 0; k < steps; k++)
            {
                SpringStep(ref st.secP, ref st.secV, pos, w, z, dt);
                SpringRot(ref st.secQ, ref st.secAv, qt, w, z, dt);
            }
            st.secF = f;
            return Matrix4x4.TRS(st.secP, st.secQ, Vector3.one);
        }

        /// <summary>Atmen, Gehwippen und Feuer aus der Aktion (ego_build.evaluate v2), R = Waffendrehung nach dem Feder-Nachlauf.</summary>
        public Layers Scripted(EgoAction A, float f, Matrix4x4 R, EgoState st)
        {
            var L = Layers.None;
            var Bz = D.motion.breathe_all;
            float phb = 2 * Mathf.PI * f / (Bz.period_s * fps);
            L.pos.z += Bz.up_m * Mathf.Sin(phb);
            L.rot = RotX(Rad(-Bz.pitch_deg * Mathf.Sin(phb + 0.8f)));
            if (A.breathe)
            {
                L.pos.z += 0.0015f * Mathf.Sin(2 * Mathf.PI * f / 60);
                L.rot = RotX(Rad(-0.25f * Mathf.Sin(2 * Mathf.PI * f / 60 + 1)));
            }
            if (A.bob != null && A.bob.enabled && A.bob.start <= f && f <= A.bob.end)
            {
                var B = A.bob;
                float w = Mathf.Min(1f, Mathf.Min((f - B.start) / 4f, (B.end - f) / 4f));
                float ph = 2 * Mathf.PI * (f - B.start) / B.period;
                float up = B.u ? -Mathf.Cos(2 * ph) : Mathf.Sin(2 * ph);   // u: oben an den Seitenumkehren (ego_build.evaluate)
                L.pos += new Vector3(B.amp[0] * Mathf.Sin(ph) * w, 0, B.amp[1] * up * w);
                L.rot = L.rot * RotY(Rad(B.roll * Mathf.Sin(ph) * w));
            }
            if (A.fire != null && A.fire.Length > 0)
            {
                var Rc = D.motion.recoil;
                float k = A.kick, dt = 1f / fps;
                // Zielen (5.1 A, wie ego_build): kleiner Modellkick, kein Hochziehen, der Kamera-Ruck geht nur in die Welt
                bool ads = A.EndsInAds;
                float kb = ads ? Rc.ads_back : 1, kp = ads ? Rc.ads_pitch : 1, kc = ads ? 0 : 1, kl = ads ? 0 : 1;
                if (!st.hasRec) { st.hasRec = true; st.recX = st.recV = st.recCx = st.recCv = Vector3.zero; st.recF = f - 1; }
                for (int fr = (int)st.recF + 1; fr <= (int)f; fr++)
                {
                    foreach (var s in A.fire)
                        if (fr - 1 < s && s <= fr)
                        {
                            st.recV += new Vector3(Rc.back_mps * k * kb, Rc.pitch_dps * k * kp, 0);
                            st.recCv += new Vector3(Rc.cam_dps * k * kc, 0, 0);
                        }
                    SpringStep(ref st.recX, ref st.recV, Vector3.zero, 2 * Mathf.PI * Rc.freq_hz, Rc.zeta, dt);
                    SpringStep(ref st.recCx, ref st.recCv, Vector3.zero, 2 * Mathf.PI * Rc.cam_freq_hz, Rc.cam_zeta, dt);
                }
                st.recF = f;
                int n = 0, last = -1;
                foreach (var s in A.fire) if (s <= f) { n++; last = s; }
                float climb = Rc.climb_deg * k * kl * n * Mathf.Exp(-Mathf.Max(0, f - A.fire[A.fire.Length - 1]) / 8f);
                L.camPitch = st.recCx.x;
                L.pos += R.MultiplyVector(new Vector3(0, st.recX.x, 0));
                L.rot = L.rot * RotX(Rad(-(st.recX.y + climb)));          // Mündung steigt
                L.trigger = (A.fire[0] - 1 <= f && f <= A.fire[A.fire.Length - 1] + 1) ? 1 : 0;
                L.bolt = (n > 0 && f - last < 1.5f) ? 1 : 0;
                L.port = n > 0 ? 1 : 0;
            }
            return L;
        }

        public static Matrix4x4 Apply(Matrix4x4 baseW, Layers L)
        {
            var R2 = Rot3(baseW) * L.rot;
            return WithPos(R2, Pos(baseW) + L.pos);
        }

        public void MechAt(EgoAction A, float f, Layers L, Dictionary<string, float> mech)
        {
            mech.Clear();
            if (A.mech != null)
                foreach (var tr in A.mech) mech[tr.part] = ValueAt(tr.keys, f);
            if (L.trigger >= 0) mech["trigger"] = L.trigger;
            if (L.bolt >= 0) mech["bolt_carrier"] = L.bolt;
            if (L.port >= 0) mech["port_cover"] = L.port;
        }

        public Matrix4x4 Rest(string pid) => T(V(D.Part(pid).rest));

        /// <summary>tools/blender_build.move_matrix: Lage des Teils im Waffenrahmen bei Anteil t.</summary>
        public Matrix4x4 MoveMatrix(EgoPart p, float t)
        {
            var rest = T(V(p.rest));
            var m = p.move;
            switch (m.kind)
            {
                case "translate": return T(V(m.vec) * t) * rest;
                case "rotate":
                    var piv = V(p.rest);
                    return T(piv) * Rot(Rad(m.a0 + (m.a1 - m.a0) * t), V(m.axis)) * T(-piv) * rest;
                default: return rest;
            }
        }

        /// <summary>Scene.set_weapon: Weltmatrizen der bewegten Teile (ohne Magazin tragen/fallen).</summary>
        public void SetWeapon(EgoOutput o, Matrix4x4 WM, Dictionary<string, float> mech)
        {
            o.weapon = WM;
            o.magOverride = o.magHidden = false;
            if (!ReferenceEquals(mech, o.mech))
            {
                o.mech.Clear();
                foreach (var kv in mech) o.mech[kv.Key] = kv.Value;
            }
            o.movers.Clear();
            foreach (var p in _movers)
            {
                o.mech.TryGetValue(p.id, out float t);
                var Ml = MoveMatrix(p, t);
                o.movers[p.id] = string.IsNullOrEmpty(p.parent) ? WM * Ml : World(o, p.parent) * Rest(p.parent).inverse * Ml;
            }
        }

        /// <summary>Aktuelle Weltmatrix eines Teils (bewegt oder der Hierarchie folgend).</summary>
        public Matrix4x4 World(EgoOutput o, string pid)
        {
            if (pid == "magazine" && o.magOverride) return o.magWorld;
            if (o.movers.TryGetValue(pid, out var m)) return m;
            var p = D.Part(pid);
            if (!string.IsNullOrEmpty(p.parent)) return World(o, p.parent) * Rest(p.parent).inverse * Rest(pid);
            return o.weapon * Rest(pid);
        }

        /// <summary>Scene.part_world: Bewegung des Teils relativ zur Ruhelage, mal Waffe.</summary>
        public Matrix4x4 PartFrame(EgoOutput o, string pid) => string.IsNullOrEmpty(pid) ? o.weapon : World(o, pid) * Rest(pid).inverse;

        // -------------------------------------------------------------- Hände
        public Matrix4x4 GripHand(string gname, Func<string, Matrix4x4> partFrame, Vector3 offset)
        {
            var G = D.Grip(gname);
            var M = partFrame(G.part);
            var c = M.MultiplyPoint3x4(V(G.contact)) + M.MultiplyVector(offset);
            var palm = M.MultiplyVector(V(G.palm)).normalized;
            var fing = M.MultiplyVector(V(G.fingers)).normalized;
            var R = FrameFrom(fing, -palm);
            return WithPos(R, c - R.MultiplyVector(_palmCenter));
        }

        public Matrix4x4 HandTarget(HandKey k, Func<string, Matrix4x4> partFrame)
        {
            if (k.kind == "cam")
            {
                var H = GripHand("support", partFrame, Vector3.zero);
                return WithPos(Rot3(H), V(k.point) - H.MultiplyVector(_palmCenter));
            }
            return GripHand(k.grip, partFrame, V(k.offset));
        }

        /// <summary>ego_build.blend_hand (v2): Kurve durch die Handziele aller Schlüssel.</summary>
        public Matrix4x4 BlendHand(HandKey[] keys, float f, Func<string, Matrix4x4> partFrame)
        {
            if (keys.Length == 1) return HandTarget(keys[0], partFrame);
            var ts = Times(keys, k => k.f);
            if (!_handMs.TryGetValue(keys.Length, out var ms)) _handMs[keys.Length] = ms = new Matrix4x4[keys.Length];
            for (int i = 0; i < keys.Length; i++) ms[i] = HandTarget(keys[i], partFrame);
            return MatsCurve(ts, ms, f);
        }

        public void FingerPose(string name, float[] dst)
        {
            var p = D.Fingers(name);
            Array.Copy(p.f, dst, 12);
            Array.Copy(p.t, 0, dst, 12, 3);
        }

        /// <summary>ego_build.blend_fingers (v2): Kurve über alle 15 Gelenkwinkel.</summary>
        public void BlendFingers(FingerKey[] keys, float f, float[] dst)
        {
            var ts = Times(keys, k => k.f);
            if (!_fingerVs.TryGetValue(keys, out var vs))
            {
                vs = new float[keys.Length][];
                for (int i = 0; i < keys.Length; i++) { vs[i] = new float[15]; FingerPose(keys[i].pose, vs[i]); }
                _fingerVs[keys] = vs;
            }
            Curve(ts, vs, f, dst);
        }

        /// <summary>ego_build.solve_arm: Unterarm folgt der Hand (Knick ≤ wrist_target), Oberarm zur Schulter, Finger aus Gelenkwinkeln.</summary>
        public void SolveArm(bool right, Matrix4x4 H, float[] fp, Matrix4x4[] seg, EgoOutput o)
        {
            var A = D.arm;
            float sx = right ? 1 : -1;
            var Wp = Pos(H);
            float a = A.upper_m, b = A.fore_m;
            var back = -Col(H, 2).normalized;
            var pref = new Vector3(sx * A.forearm_pref[0], A.forearm_pref[1], A.forearm_pref[2]).normalized;
            var fdir = (back * 0.55f + pref * 0.45f).normalized;
            float lim = Rad(A.wrist_target_deg);
            if (Angle(fdir, back) > lim)
            {
                float ab = Angle(back, pref);
                fdir = ab > 1e-6f ? SlerpDir(back, pref, lim / Mathf.Max(1e-6f, ab)) : back;
            }
            var E = Wp + fdir * b;
            var S0 = V(right ? A.shoulder_R : A.shoulder_L);
            var S = E + (S0 - E).normalized * a;
            var view = -(E + Wp) / 2;
            var hint = view.magnitude > 1e-6f ? view.normalized : Col(H, 1);
            seg[_seg["upper"]] = FrameFrom(E - S, hint, S);
            seg[_seg["fore"]] = FrameFrom(Wp - E, hint, E);
            seg[_seg["hand"]] = H;
            float bend = Angle((Wp - E).normalized, Col(H, 2)) * Mathf.Rad2Deg;
            o.wristBendMaxDeg = Mathf.Max(o.wristBendMaxDeg, bend);
            if ((S - S0).magnitude > 0.25f) o.overreach++;
            int nf = A.finger_x.Length, nl = A.finger_links.Length;
            for (int i = 0; i < nf; i++)
            {
                var M = H * T(new Vector3(sx * A.finger_x[i], 0, A.knuckle_z));
                for (int j = 0; j < nl; j++)
                {
                    M = M * RotX(Rad(fp[i * nl + j]));
                    seg[_fingerSeg[i, j]] = M;
                    M = M * T(new Vector3(0, 0, A.finger_links[j] * A.finger_scale[i]));
                }
            }
            var tb = new Vector3(sx * A.thumb_base[0], A.thumb_base[1], A.thumb_base[2]);
            var td = new Vector3(sx * A.thumb_dir[0], A.thumb_dir[1], A.thumb_dir[2]);
            float flex = fp[12], outw = fp[13], tip = fp[14];
            var Tm = H * FrameFrom(td, Vector3.up, tb) * RotY(Rad(-sx * (outw - 30)));
            for (int j = 0; j < A.thumb_links.Length; j++)
            {
                Tm = Tm * RotX(Rad(j == 0 ? flex : j == 1 ? tip * 0.6f : tip));
                seg[_thumbSeg[j]] = Tm;
                Tm = Tm * T(new Vector3(0, 0, A.thumb_links[j]));
            }
        }

        // -------------------------------------------------------------- Magazin
        /// <summary>Magazin fallen lassen (leer) oder in der linken Hand tragen, wie ego_build.evaluate.</summary>
        public void Magazine(EgoOutput o, EgoAction A, float f, Matrix4x4 HL, EgoState st)
        {
            bool hasCarry = A.carry != null && A.carry.Length > 0;
            if (A.drop != null && A.drop.a >= 0 && hasCarry && A.drop.a <= f && f < A.carry[0].a)
            {
                float t = (f - A.drop.a) / fps;
                var mag0 = o.weapon * Rest("magazine");
                o.magOverride = true;
                if (f >= A.drop.b)
                {
                    o.magWorld = T(new Vector3(0, 0, -5)) * mag0;
                    o.magHidden = true;
                }
                else
                    o.magWorld = T(new Vector3(0.02f * t, -0.05f * t, -0.5f * 9.81f * t * t - 0.3f * t)) * mag0 * RotX(Rad(-140 * t));
                return;
            }
            if (!hasCarry) return;
            foreach (var c in A.carry)
                if (c.a <= f && f <= c.b)
                {
                    if (!st.hasRel) { st.rel = _magRelLocal; st.hasRel = true; }
                    o.magOverride = true;
                    o.magWorld = HL * st.rel;
                }
        }

        public Matrix4x4 MagCarry(Matrix4x4 HL) => HL * _magRelLocal;

        // -------------------------------------------------------------- Referenz
        /// <summary>Ein Bild einer Aktion genau wie tools/ego_build.evaluate (geskriptete Ebenen).</summary>
        public EgoOutput Evaluate(EgoAction A, float f, EgoState st, EgoOutput o = null)
        {
            o = o ?? NewOutput();
            var baseW = Secondary(WeaponAt(A.weapon, f), f, st, A.EndsInAds);
            var L = Scripted(A, f, Rot3(baseW), st);
            var WM = Apply(baseW, L);
            MechAt(A, f, L, o.mech);
            SetWeapon(o, WM, o.mech);
            Func<string, Matrix4x4> pf = pid => PartFrame(o, pid);
            o.handL = BlendHand(A.L, f, pf);
            o.handR = BlendHand(A.R, f, pf);
            Magazine(o, A, f, o.handL, st);
            BlendFingers(A.fL, f, o.fingersL);
            BlendFingers(A.fR, f, o.fingersR);
            SolveArm(true, o.handR, o.fingersR, o.segR, o);
            SolveArm(false, o.handL, o.fingersL, o.segL, o);
            o.camPitch = L.camPitch;
            return o;
        }

        /// <summary>Standbild einer Haltung mit der Handbelegung aus ego_build.main (--stills).</summary>
        public EgoAction StillAction(string pose)
        {
            HandKey Grip(string g) => new HandKey { f = 0, kind = "grip", grip = g, point = new float[3], offset = new float[3] };
            var A = new EgoAction
            {
                name = "still:" + pose, frames = 0, time_scale = 1,
                weapon = new[] { new WeaponKey { f = 0, pose = pose } },
                L = new[] { Grip("support") }, R = new[] { Grip("grip") },
                fL = new[] { new FingerKey { f = 0, pose = "underhand" } }, fR = new[] { new FingerKey { f = 0, pose = "trigger" } },
                mech = new MechTrack[0], carry = new FrameRange[0], drop = new FrameRange { a = -1, b = -1 }, fire = new int[0],
                kick = 1, bob = new Bob { enabled = false, amp = new float[2] }, events = new Marker[0],
            };
            if (pose == "inspect_r")      // linke Hand unter dem Bild wie in der Aktion inspect (ego.OFF_L)
                A.L = new[] { Array.Find(D.Action("inspect").L, k => k.kind == "cam") };
            if (pose == "reload")
            {
                A.L = new[] { Grip("mag") };
                A.fL = new[] { new FingerKey { f = 0, pose = "mag_hold" } };
            }
            return A;
        }
    }
}
