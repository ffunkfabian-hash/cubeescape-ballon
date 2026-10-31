// Wirkung der Waffen (0.34 „Payload“): Einschläge (Funken, Staub, Licht, Loch), Projektile mit eigener Flugbahn, Explosionen (Blitz,
// Druckring, Funken, Rauch, Licht), Strahlen (Dauerstrahl, scharfer Strahl, Bolzen), Leuchtspur, an der Waffe Mündungsrauch und
// Mündungslicht. Werte je Klasse aus ego.json › gameplay.fx, gemeinsame aus motion.payload (basic/arms/ego.py › PAYLOAD, IMPACTS, DECAL,
// EXPLOSION, MUZZLE_SMOKE). Alles liegt in festen Pools, die beim Start angelegt werden; je Bild nur Lage, Farbe und Sichtbarkeit.
// Partikel laufen angehalten und werden mit der Spielzeit des Spielers weitergerechnet (Simulate), damit Aufnahmen und Tests mit
// virtueller Zeit dieselben Bilder sehen. Kein Speicher je Bild.
using UnityEngine;
using UnityEngine.Rendering;

namespace Ballon.Ego
{
    public sealed class WeaponFx
    {
        /// <summary>Materialien (BallonSetup, Shader Ballon/Fx): Funke, Licht, Rauch, Ring, Loch, Strahl; Körper der Projektile.</summary>
        public struct Mats { public Material spark, glow, smoke, ring, decal, beam, body; }

        /// <summary>Gegenprobe (BALLON_PAYLOAD_OFF=1): ohne Wirkung, Schrittteile, Füllstand, Glieder und Hülsen beim Nachladen – die
        /// PlayMode-Tests von 0.34 müssen dann scheitern.</summary>
        public static readonly bool Off = System.Environment.GetEnvironmentVariable("BALLON_PAYLOAD_OFF") == "1";

        public const int ProjectilePool = 8, LinePool = 24, RingPool = 4, LightPool = 2, ScorchPool = 8, MaxHits = 32;

        readonly EgoPlayer _p;
        readonly Mats _m;
        readonly Transform _root;
        readonly ParticleSystem _sparks, _dust, _smoke, _glow;
        readonly ParticleSystem[] _vmSmoke, _vmGlow;               // je Waffe in der Viewmodel-Ebene (Raum der Waffe)
        readonly float[] _vmSmokeLeft, _vmSmokeAcc;
        readonly Color[] _energy;                                   // Leuchtfarbe je Waffe
        readonly MaterialPropertyBlock _mpb = new MaterialPropertyBlock();
        readonly Collider[] _overlap = new Collider[MaxHits];
        readonly RangeTarget[] _hitOnce = new RangeTarget[MaxHits];
        uint _rng = 0x9E3779B9u;

        // Einschusslöcher (Ring, der älteste wird wiederverwendet) und Brandflecken
        readonly Transform[] _holes;
        readonly Renderer[] _holeR;
        readonly float[] _holeAge, _holeSeed;
        readonly bool[] _holeScorch;
        int _holeNext, _holeCount;
        readonly Transform[] _scorch;
        readonly Renderer[] _scorchR;
        readonly float[] _scorchAge;
        int _scorchNext;

        // Projektile
        readonly Transform[] _proj;
        readonly Renderer[] _projR;
        readonly MeshFilter[] _projF;
        readonly Vector3[] _projV;
        readonly float[] _projAge, _projStuck, _projTrail;
        readonly bool[] _projOn;
        readonly EgoFx[] _projFx;
        readonly int[] _projWeapon;
        readonly Mesh _sphere, _capsule, _cylinder;

        // Linien: rail (scharfer Strahl, blendet aus), bolt (fliegender Bolzen, Einschlag bei Ankunft), tracer (Leuchtspur), arrow (Spur
        // hinter dem Pfeil)
        enum LineKind { Off, Rail, Bolt, Tracer }
        readonly LineRenderer[] _lines;
        readonly LineKind[] _lineKind;
        readonly Vector3[] _lineA, _lineB, _lineN;
        readonly float[] _lineAge, _lineLife, _lineSpeed, _lineLen, _lineW;
        readonly Color[] _lineColor;
        readonly EgoImpact[] _lineImpact;
        readonly Transform[] _lineHit;
        int _lineNext;
        readonly LineRenderer _beam;                                 // Dauerstrahl (Spurgewehr)
        Vector3 _beamEnd, _beamNormal;
        bool _beamHit;
        float _beamFlicker, _beamSparkAcc;

        // Druckringe und Lichter der Explosionen
        readonly Transform[] _rings;
        readonly Renderer[] _ringR;
        readonly float[] _ringAge, _ringSize;
        int _ringNext;
        readonly Light[] _lights;
        readonly float[] _lightAge, _lightK;
        int _lightNext;

        /// <summary>Messwerte für Tests: Explosionen, Einschläge (je Strahl, Kugel, Bolzen, Pfeil), gestartete Projektile.</summary>
        public int explosions, impacts, launched, bolts, rails, tracers;
        /// <summary>Treffer auf Scheiben durch Explosionen (je Scheibe und Explosion einmal).</summary>
        public int explosionHits;

        public WeaponFx(EgoPlayer p, Mats m)
        {
            _p = p;
            _m = m;
            var D = p.loadouts[0].rig.S.D;
            var P = D.motion.payload;
            EgoPlayer.DecalMax = P.decal.max;
            EgoPlayer.DecalSize = P.decal.size_m;
            _root = new GameObject("Wirkung").transform;
            _sparks = Ps("Funken", m.spark, 1024, _root, 0, true, 0.6f, 1.2f);
            _dust = Ps("Staub", m.smoke, 384, _root, 0, false, 2.4f, -0.02f);
            _smoke = Ps("Rauch", m.smoke, 384, _root, 0, false, 3.2f, -0.05f);
            _glow = Ps("Licht", m.glow, 256, _root, 0, false, 0.5f, 0);
            int n = p.loadouts.Length;
            _vmSmoke = new ParticleSystem[n];
            _vmGlow = new ParticleSystem[n];
            _vmSmokeLeft = new float[n];
            _vmSmokeAcc = new float[n];
            _energy = new Color[n];
            for (int k = 0; k < n; k++)
            {
                var rig = p.loadouts[k].rig;
                _vmSmoke[k] = Ps("Muendungsrauch", m.smoke, 96, rig.space, Bootstrap.ViewmodelLayer, false, rig.S.D.motion.payload.muzzle_smoke.grow, 0);
                _vmGlow[k] = Ps("Muendungslicht", m.glow, 32, rig.space, Bootstrap.ViewmodelLayer, false, 0.6f, 0);
                _energy[k] = EnergyColor(rig.S.D);
            }
            int hn = P.decal.max;
            _holes = new Transform[hn];
            _holeR = new Renderer[hn];
            _holeAge = new float[hn];
            _holeSeed = new float[hn];
            _holeScorch = new bool[hn];
            _scorch = new Transform[ScorchPool];
            _scorchR = new Renderer[ScorchPool];
            _scorchAge = new float[ScorchPool];
            for (int k = 0; k < ScorchPool; k++)
            {
                _scorch[k] = Quad("Brandfleck", m.decal, _root, out _scorchR[k]);
                _scorchAge[k] = 1e9f;
            }
            _sphere = PrimitiveMesh(PrimitiveType.Sphere);
            _capsule = PrimitiveMesh(PrimitiveType.Capsule);
            _cylinder = PrimitiveMesh(PrimitiveType.Cylinder);
            _proj = new Transform[ProjectilePool];
            _projR = new Renderer[ProjectilePool];
            _projF = new MeshFilter[ProjectilePool];
            _projV = new Vector3[ProjectilePool];
            _projAge = new float[ProjectilePool];
            _projStuck = new float[ProjectilePool];
            _projTrail = new float[ProjectilePool];
            _projOn = new bool[ProjectilePool];
            _projFx = new EgoFx[ProjectilePool];
            _projWeapon = new int[ProjectilePool];
            for (int k = 0; k < ProjectilePool; k++)
            {
                var go = new GameObject("Projektil");
                go.transform.SetParent(_root, false);
                _projF[k] = go.AddComponent<MeshFilter>();
                var r = go.AddComponent<MeshRenderer>();
                r.sharedMaterial = m.body;
                r.shadowCastingMode = ShadowCastingMode.On;
                r.enabled = false;
                _projR[k] = r;
                _proj[k] = go.transform;
            }
            _lines = new LineRenderer[LinePool];
            _lineKind = new LineKind[LinePool];
            _lineA = new Vector3[LinePool];
            _lineB = new Vector3[LinePool];
            _lineN = new Vector3[LinePool];
            _lineAge = new float[LinePool];
            _lineLife = new float[LinePool];
            _lineSpeed = new float[LinePool];
            _lineLen = new float[LinePool];
            _lineW = new float[LinePool];
            _lineColor = new Color[LinePool];
            _lineImpact = new EgoImpact[LinePool];
            _lineHit = new Transform[LinePool];
            for (int k = 0; k < LinePool; k++) _lines[k] = Line("Strahl", m.beam, _root);
            _beam = Line("Dauerstrahl", m.beam, _root);
            _rings = new Transform[RingPool];
            _ringR = new Renderer[RingPool];
            _ringAge = new float[RingPool];
            _ringSize = new float[RingPool];
            for (int k = 0; k < RingPool; k++)
            {
                _rings[k] = Quad("Druckring", m.ring, _root, out _ringR[k]);
                _ringAge[k] = 1e9f;
            }
            _lights = new Light[LightPool];
            _lightAge = new float[LightPool];
            _lightK = new float[LightPool];
            for (int k = 0; k < LightPool; k++)
            {
                _lights[k] = new GameObject("Explosionslicht").AddComponent<Light>();
                _lights[k].transform.SetParent(_root, false);
                _lights[k].type = LightType.Point;
                _lights[k].shadows = LightShadows.None;
                _lights[k].enabled = false;
                _lightAge[k] = 1e9f;
            }
        }

        // ------------------------------------------------------------------------------------------------ Aufbau
        static ParticleSystem Ps(string name, Material m, int max, Transform parent, int layer, bool stretch, float grow, float gravity)
        {
            var go = new GameObject(name) { layer = layer };
            go.transform.SetParent(parent, false);
            var ps = go.AddComponent<ParticleSystem>();
            ps.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear);
            var main = ps.main;
            main.playOnAwake = false;
            main.maxParticles = max;
            main.simulationSpace = ParticleSystemSimulationSpace.Local;
            main.startSpeed = 0;
            main.startLifetime = 1;
            main.gravityModifier = gravity;
            main.scalingMode = ParticleSystemScalingMode.Hierarchy;
            var em = ps.emission;
            em.enabled = false;
            var sh = ps.shape;
            sh.enabled = false;
            var col = ps.colorOverLifetime;
            col.enabled = true;
            var g = new Gradient();
            g.SetKeys(new[] { new GradientColorKey(Color.white, 0), new GradientColorKey(Color.white, 1) },
                      new[] { new GradientAlphaKey(stretch ? 1 : 0.0f, 0), new GradientAlphaKey(1, stretch ? 0.5f : 0.12f), new GradientAlphaKey(0, 1) });
            col.color = new ParticleSystem.MinMaxGradient(g);
            var sz = ps.sizeOverLifetime;
            sz.enabled = true;
            sz.size = new ParticleSystem.MinMaxCurve(1, AnimationCurve.EaseInOut(0, 1, 1, grow));
            var r = go.GetComponent<ParticleSystemRenderer>();
            r.sharedMaterial = m;
            r.renderMode = stretch ? ParticleSystemRenderMode.Stretch : ParticleSystemRenderMode.Billboard;
            r.velocityScale = stretch ? 0.035f : 0;
            r.lengthScale = stretch ? 2.5f : 1;
            r.shadowCastingMode = ShadowCastingMode.Off;
            r.receiveShadows = false;
            r.lightProbeUsage = LightProbeUsage.Off;
            r.reflectionProbeUsage = ReflectionProbeUsage.Off;
            r.sortingFudge = stretch ? -10 : 0;
            ps.Pause();
            return ps;
        }

        static Transform Quad(string name, Material m, Transform parent, out Renderer r)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Quad);
            Object.DestroyImmediate(go.GetComponent<Collider>());     // sofort: sonst treffen die übrigen Schrotkugeln desselben Bilds das Loch
            go.name = name;
            go.transform.SetParent(parent, false);
            r = go.GetComponent<Renderer>();
            r.sharedMaterial = m;
            r.shadowCastingMode = ShadowCastingMode.Off;
            r.receiveShadows = false;
            r.lightProbeUsage = LightProbeUsage.Off;
            r.reflectionProbeUsage = ReflectionProbeUsage.Off;
            r.enabled = false;
            return go.transform;
        }

        static LineRenderer Line(string name, Material m, Transform parent)
        {
            var l = new GameObject(name).AddComponent<LineRenderer>();
            l.transform.SetParent(parent, false);
            l.sharedMaterial = m;
            l.useWorldSpace = true;
            l.positionCount = 2;
            l.alignment = LineAlignment.View;
            l.textureMode = LineTextureMode.Stretch;
            l.numCapVertices = 2;
            l.shadowCastingMode = ShadowCastingMode.Off;
            l.receiveShadows = false;
            l.lightProbeUsage = LightProbeUsage.Off;
            l.reflectionProbeUsage = ReflectionProbeUsage.Off;
            l.enabled = false;
            return l;
        }

        static Mesh PrimitiveMesh(PrimitiveType t)
        {
            var go = GameObject.CreatePrimitive(t);
            var mesh = go.GetComponent<MeshFilter>().sharedMesh;
            Object.Destroy(go);
            return mesh;
        }

        /// <summary>Leuchtfarbe der Waffe: gameplay.fx.color, sonst die Rolle des ersten Leuchtteils (weapon.live.glow), sonst Familien-Cyan.</summary>
        public static Color EnergyColor(EgoFile D)
        {
            if (!string.IsNullOrEmpty(D.gameplay.fx.color) && ColorUtility.TryParseHtmlString(D.gameplay.fx.color, out var c)) return c;
            var g = D.weapon.live.glow;
            if (g != null && g.Length > 0 && D.HasPart(g[0]))
            {
                var role = System.Array.Find(D.roles, r => r.role == D.Part(g[0]).role);
                if (role != null && ColorUtility.TryParseHtmlString(role.color, out c)) return c;
            }
            return new Color(0.373f, 0.827f, 0.878f);                  // #5FD3E0 Familienfarbe Cyan (ego.FLASH flash_flame)
        }

        static Color Hex(string h, Color fallback) => !string.IsNullOrEmpty(h) && ColorUtility.TryParseHtmlString(h, out var c) ? c : fallback;

        // ------------------------------------------------------------------------------------------------ Zufall (ohne Speicher)
        float R01()
        {
            _rng ^= _rng << 13;
            _rng ^= _rng >> 17;
            _rng ^= _rng << 5;
            return (_rng & 0xFFFFFF) / 16777216f;
        }

        float R(float a, float b) => a + (b - a) * R01();

        Vector3 Hemi(Vector3 n, float spread)
        {
            var d = new Vector3(R(-1, 1), R(-1, 1), R(-1, 1));
            return (n + d * spread).normalized;
        }

        // ------------------------------------------------------------------------------------------------ Einschläge
        /// <summary>Einschlag nach Stil (motion.payload.impacts): Funken, Staub, Lichtpunkt und – an Flächen – ein Loch bzw. Brandfleck.
        /// energy färbt Funken und Licht in der Leuchtfarbe der Waffe. hitT: Träger des Lochs (Collider), null = ohne Loch.</summary>
        public void Impact(EgoImpact I, Vector3 point, Vector3 normal, Vector3 incoming, Color energy, bool energyColor, Transform hitT)
        {
            if (I == null) return;
            impacts++;
            var refl = Vector3.Reflect(incoming.normalized, normal);
            var warm = new Color(1f, 0.78f, 0.45f);
            var sc = energyColor ? energy * 4f : warm * 5f;
            var ep = new ParticleSystem.EmitParams();
            for (int k = 0; k < I.sparks; k++)
            {
                ep.position = point + normal * 0.01f;
                ep.velocity = Hemi(Vector3.Lerp(normal, refl, 0.6f).normalized, 0.9f) * I.spark_mps * R(0.45f, 1.2f);
                ep.startLifetime = I.spark_s * R(0.6f, 1.2f);
                ep.startSize = R(0.02f, 0.035f);
                ep.startColor = sc;
                _sparks.Emit(ep, 1);
            }
            var dc = new Color(0.62f, 0.62f, 0.62f, 0.75f);
            for (int k = 0; k < I.dust; k++)
            {
                ep.position = point + normal * R(0.02f, 0.06f);
                ep.velocity = Hemi(normal, 0.5f) * R(0.3f, 0.9f);
                ep.startLifetime = I.dust_s * R(0.7f, 1.2f);
                ep.startSize = I.dust_m * R(0.6f, 1.1f);
                ep.startColor = dc;
                ep.rotation = R(0, 360);
                _dust.Emit(ep, 1);
            }
            ep.position = point + normal * 0.03f;
            ep.velocity = Vector3.zero;
            ep.startLifetime = I.glow_s;
            ep.startSize = I.glow_m;
            ep.startColor = sc;
            _glow.Emit(ep, 1);
            if (hitT != null && I.decal != "") Hole(point, normal, hitT, I.decal == "scorch");
        }

        /// <summary>Einschussloch bzw. Brandfleck aus dem Pool (der älteste wird wiederverwendet): erst lösen, dann Lage und Größe in
        /// Weltmaßen, dann an den Träger hängen (Patch einschuss: sonst galt die Größe im Maßstab des alten Trägers).</summary>
        public void Hole(Vector3 point, Vector3 normal, Transform hitT, bool scorch)
        {
            int k = _holeNext;
            _holeNext = (_holeNext + 1) % _holes.Length;
            if (_holes[k] == null)
            {
                _holes[k] = Quad("Einschlag", _m.decal, null, out _holeR[k]);
                _holeCount++;
            }
            var t = _holes[k];
            t.SetParent(null, false);
            t.SetPositionAndRotation(point + normal * 0.004f, Quaternion.LookRotation(-normal) * Quaternion.Euler(0, 0, R(0, 360)));
            t.localScale = Vector3.one * EgoPlayer.DecalSize;
            t.SetParent(hitT, true);
            _holeAge[k] = 0;
            _holeSeed[k] = Mathf.Floor(R(0, _p.loadouts[0].rig.S.D.motion.payload.decal.variants)) + 0.37f;
            _holeScorch[k] = scorch;
            SetDecal(_holeR[k], _holeSeed[k], scorch ? 1 : 0, 1);
            _holeR[k].enabled = true;
        }

        void SetDecal(Renderer r, float seed, float kind, float alpha)
        {
            r.GetPropertyBlock(_mpb);
            _mpb.SetFloat("_Seed", seed);
            _mpb.SetFloat("_Kind", kind);
            _mpb.SetFloat("_Alpha", alpha);
            r.SetPropertyBlock(_mpb);
        }

        /// <summary>Löcher im Pool (angelegt), höchstens motion.payload.decal.max.</summary>
        public int HoleCount => _holeCount;
        /// <summary>Deckung des Lochs, das zuletzt entstand (Tests: Ausblenden).</summary>
        public float HoleAlpha(int ageRank)
        {
            int k = ((_holeNext - 1 - ageRank) % _holes.Length + _holes.Length) % _holes.Length;
            if (_holes[k] == null) return -1;
            var D = _p.loadouts[0].rig.S.D.motion.payload.decal;
            return _holeR[k].enabled ? Mathf.Clamp01((D.life_s - _holeAge[k]) / D.fade_s) : 0;
        }
        public Transform HoleTransform(int ageRank) => _holes[((_holeNext - 1 - ageRank) % _holes.Length + _holes.Length) % _holes.Length];

        // ------------------------------------------------------------------------------------------------ Schüsse
        /// <summary>Mündung der Waffe k in der Welt: Socket_Muzzle durch die Viewmodel-Kamera auf denselben Bildpunkt der Weltkamera
        /// (gleiche Tiefe) – Strahlen und Projektile beginnen sichtbar am Lauf, obwohl die Waffe mit eigenem Bildwinkel gezeichnet wird.</summary>
        public Vector3 MuzzleWorld(int k)
        {
            var s = _p.viewCam.WorldToViewportPoint(_p.loadouts[k].rig.AnchorWorld("Socket_Muzzle"));
            return _p.worldCam.ViewportToWorldPoint(new Vector3(s.x, s.y, Mathf.Max(0.1f, s.z)));
        }

        /// <summary>An der Waffe beim Schuss: Mündungslicht (Energie, Bogen) und Rauch aus dem Rohr (Werfer).</summary>
        public void MuzzleShot(int k, EgoFx fx)
        {
            if (fx.smoke_s > 0) { _vmSmokeLeft[k] = fx.smoke_s; _vmSmokeAcc[k] = 1; }      // erster Ballen gleich im Schussbild
            if (fx.muzzle_glow_m > 0) VmGlow(k, fx.muzzle_glow_m * 2.2f, 0.10f);
        }

        void VmGlow(int k, float size, float life)
        {
            var rig = _p.loadouts[k].rig;
            var ep = new ParticleSystem.EmitParams
            {
                position = rig.space.InverseTransformPoint(rig.AnchorWorld("Socket_Muzzle")),
                velocity = Vector3.zero, startLifetime = life, startSize = size, startColor = _energy[k] * 4.0f,
            };
            _vmGlow[k].Emit(ep, 1);
        }

        /// <summary>Dauerstrahl (Spurgewehr): Ende des Strahls in diesem Schuss; der Strahl selbst läuft in Tick, solange der Abzug zieht.</summary>
        public void BeamShot(Vector3 end, Vector3 normal, bool hit)
        {
            _beamEnd = end;
            _beamNormal = normal;
            _beamHit = hit;
        }

        /// <summary>Scharfer Strahl (lineare Fusion): sichtbar fx.beam_s, wird schmaler und blasser.</summary>
        public void Rail(Vector3 a, Vector3 b, EgoFx fx, Color c)
        {
            int k = NextLine();
            _lineKind[k] = LineKind.Rail;
            _lineA[k] = a;
            _lineB[k] = b;
            _lineAge[k] = 0;
            _lineLife[k] = fx.beam_s;
            _lineW[k] = fx.width_m;
            _lineColor[k] = c;
            rails++;
        }

        /// <summary>Bolzen (Fusion) bzw. Leuchtspur: ein Strich der Länge len fliegt mit speed von a nach b; ein Bolzen schlägt bei der
        /// Ankunft mit Stil I ein (Loch am Träger hitT).</summary>
        public void Streak(Vector3 a, Vector3 b, Vector3 n, float speed, float len, float w, Color c, EgoImpact I, Transform hitT, bool tracer)
        {
            int k = NextLine();
            _lineKind[k] = tracer ? LineKind.Tracer : LineKind.Bolt;
            _lineA[k] = a;
            _lineB[k] = b;
            _lineN[k] = n;
            _lineAge[k] = 0;
            _lineSpeed[k] = speed;
            _lineLen[k] = len;
            _lineW[k] = w;
            _lineColor[k] = c;
            _lineImpact[k] = I;
            _lineHit[k] = hitT;
            if (tracer) tracers++; else bolts++;
        }

        int NextLine()
        {
            int k = _lineNext;
            _lineNext = (_lineNext + 1) % LinePool;
            if (_lineKind[k] == LineKind.Bolt) FinishBolt(k);          // überschrieben: der Bolzen schlägt sofort ein
            return k;
        }

        void FinishBolt(int k)
        {
            if (_lineImpact[k] != null) Impact(_lineImpact[k], _lineB[k], _lineN[k], _lineB[k] - _lineA[k], _lineColor[k], true, _lineHit[k]);
            _lineImpact[k] = null;
            _lineKind[k] = LineKind.Off;
            _lines[k].enabled = false;
        }

        /// <summary>Projektil der Waffe k (Granate, Rakete, Pfeil) mit eigener Flugbahn ab der Mündung: Geschwindigkeit fx.speed_mps längs
        /// dir, Fall fx.gravity_mps2; ein Hindernis zwischen Kamera und Mündung trifft sofort.</summary>
        public void Launch(int k, Vector3 dir, EgoFx fx, int ignoreMask)
        {
            var cam = _p.worldCam.transform.position;
            var a = MuzzleWorld(k);
            int j = -1;
            for (int i = 0; i < ProjectilePool; i++) if (!_projOn[i]) { j = i; break; }
            if (j < 0)                                                   // Pool voll: das älteste weiter fliegende ersetzen
            {
                float old = -1;
                for (int i = 0; i < ProjectilePool; i++) if (_projAge[i] > old) { old = _projAge[i]; j = i; }
            }
            launched++;
            LastLaunch = a;
            _projOn[j] = true;
            _projAge[j] = 0;
            _projStuck[j] = -1;
            _projTrail[j] = 0;
            _projFx[j] = fx;
            _projWeapon[j] = k;
            _projV[j] = dir.normalized * fx.speed_mps;
            var t = _proj[j];
            t.SetParent(_root, false);
            _projF[j].sharedMesh = fx.kind == "arrow" ? _cylinder : fx.trail == "rocket" ? _capsule : _sphere;
            t.localScale = fx.kind == "arrow" ? new Vector3(fx.width_m, fx.length_m / 2, fx.width_m)
                         : fx.trail == "rocket" ? new Vector3(fx.width_m, fx.length_m / 2, fx.width_m) : Vector3.one * fx.width_m * 2;
            t.SetPositionAndRotation(a, Quaternion.FromToRotation(Vector3.up, _projV[j]));
            _projR[j].enabled = true;
            if (Physics.Linecast(cam, a, out var hit, ignoreMask, QueryTriggerInteraction.Ignore)) Land(j, hit);
        }

        /// <summary>Startpunkt des letzten Projektils (Mündung in der Welt, Tests).</summary>
        public Vector3 LastLaunch { get; private set; }
        public int ProjectilesFlying { get { int n = 0; for (int i = 0; i < ProjectilePool; i++) if (_projOn[i] && _projStuck[i] < 0) n++; return n; } }
        /// <summary>Lage und Geschwindigkeit des ersten fliegenden Projektils (Tests), false ohne.</summary>
        public bool FirstProjectile(out Vector3 pos, out Vector3 vel)
        {
            for (int i = 0; i < ProjectilePool; i++)
                if (_projOn[i] && _projStuck[i] < 0) { pos = _proj[i].position; vel = _projV[i]; return true; }
            pos = vel = Vector3.zero;
            return false;
        }

        void Land(int j, RaycastHit hit)
        {
            var fx = _projFx[j];
            var D = _p.loadouts[_projWeapon[j]].rig.S.D;
            if (fx.Explodes)
            {
                Explode(hit.point, hit.normal, fx.radius_m, D, hit.collider.transform);
                _projOn[j] = false;
                _projR[j].enabled = false;
                return;
            }
            var t = hit.collider.GetComponentInParent<RangeTarget>();     // Pfeil: Treffer an der Scheibe, steckt stick_s
            if (t != null) { t.Hit(hit.point); _p.ProjectileHit(); }
            Impact(D.Impact(fx.impact), hit.point, hit.normal, _projV[j], _energy[_projWeapon[j]], true, hit.collider.transform);
            _projStuck[j] = fx.stick_s;
            var tr = _proj[j];
            tr.position = hit.point - _projV[j].normalized * fx.length_m * 0.35f;
            tr.SetParent(hit.collider.transform, true);
        }

        /// <summary>Explosion: Blitz, Feuerkugeln, Druckring auf der Fläche, Funken, Rauch, kurzes Licht, Brandfleck; Scheiben im Radius
        /// zählen je einmal als Treffer.</summary>
        public void Explode(Vector3 p, Vector3 n, float radius, EgoFile D, Transform surface)
        {
            var X = D.motion.payload.explosion;
            explosions++;
            var core = Hex(X.core_color, Color.white);
            var fire = Hex(X.fire_color, new Color(1f, 0.54f, 0.24f));
            var smoke = Hex(X.smoke_color, Color.gray);
            var ep = new ParticleSystem.EmitParams();
            ep.position = p + n * radius * 0.15f;
            ep.velocity = Vector3.zero;
            ep.startLifetime = X.flash_s;
            ep.startSize = radius * X.flash_k * 2;
            ep.startColor = core * 10f;
            _glow.Emit(ep, 1);
            for (int k = 0; k < X.fire; k++)                              // Feuerkugeln um den Kern
            {
                ep.position = p + Hemi(n, 1.2f) * radius * R(0.1f, 0.4f) + n * radius * 0.15f;
                ep.velocity = Hemi(n, 1f) * radius * R(0.5f, 1.4f);
                ep.startLifetime = X.fire_s * R(0.7f, 1.2f);
                ep.startSize = radius * X.fire_k * R(0.6f, 1.1f);
                ep.startColor = fire * R(4f, 7f);
                _glow.Emit(ep, 1);
            }
            for (int k = 0; k < X.sparks; k++)
            {
                ep.position = p + n * 0.05f;
                ep.velocity = Hemi(n, 1.1f) * X.spark_mps * R(0.35f, 1.1f);
                ep.startLifetime = X.spark_s * R(0.5f, 1.2f);
                ep.startSize = R(0.02f, 0.035f);
                ep.startColor = fire * 3f;
                _sparks.Emit(ep, 1);
            }
            for (int k = 0; k < X.smoke; k++)
            {
                ep.position = p + Hemi(n, 1.3f) * radius * R(0.05f, 0.35f) + n * radius * 0.2f;
                ep.velocity = Hemi(n, 0.9f) * R(0.4f, 1.4f) + n * 0.6f;
                ep.startLifetime = X.smoke_s * R(0.7f, 1.2f);
                ep.startSize = radius * X.smoke_k * R(0.6f, 1.1f);
                ep.startColor = new Color(smoke.r, smoke.g, smoke.b, R(0.55f, 0.8f));
                ep.rotation = R(0, 360);
                _smoke.Emit(ep, 1);
            }
            int r = _ringNext;
            _ringNext = (_ringNext + 1) % RingPool;
            _rings[r].SetPositionAndRotation(p + n * 0.05f, Quaternion.LookRotation(-n));
            _ringAge[r] = 0;
            _ringSize[r] = radius * X.ring_k * 2;
            _ringR[r].enabled = true;
            int l = _lightNext;
            _lightNext = (_lightNext + 1) % LightPool;
            _lights[l].transform.position = p + n * radius * 0.4f;
            _lights[l].color = fire;
            _lights[l].range = radius * 3;
            _lightAge[l] = 0;
            _lightK[l] = X.light_k;
            _lights[l].enabled = true;
            int s = _scorchNext;
            _scorchNext = (_scorchNext + 1) % ScorchPool;
            var st = _scorch[s];
            st.SetParent(null, false);
            st.SetPositionAndRotation(p + n * 0.006f, Quaternion.LookRotation(-n) * Quaternion.Euler(0, 0, R(0, 360)));
            st.localScale = Vector3.one * D.motion.payload.decal.scorch_m * radius / 3f;
            if (surface != null) st.SetParent(surface, true);
            _scorchAge[s] = 0;
            SetDecal(_scorchR[s], R(0, 4), 1, 1);
            _scorchR[s].enabled = true;
            int m = Physics.OverlapSphereNonAlloc(p, radius, _overlap, ~0, QueryTriggerInteraction.Ignore);
            int once = 0;
            for (int k = 0; k < m; k++)
            {
                var t = _overlap[k].GetComponentInParent<RangeTarget>();
                if (t == null) continue;
                bool seen = false;
                for (int q = 0; q < once; q++) if (_hitOnce[q] == t) { seen = true; break; }
                if (seen || once >= MaxHits) continue;
                _hitOnce[once++] = t;
                t.Hit(p);
                explosionHits++;
                _p.ProjectileHit();
            }
        }

        // ------------------------------------------------------------------------------------------------ je Bild
        /// <summary>Alles um dt weiterrechnen (Spielzeit des Spielers). active = Waffe in der Hand; beamOn = Dauerstrahl läuft.</summary>
        public void Tick(float dt, int active, bool beamOn, int ignoreMask)
        {
            var D0 = _p.loadouts[0].rig.S.D.motion.payload;
            // Projektile
            for (int j = 0; j < ProjectilePool; j++)
            {
                if (!_projOn[j]) continue;
                var fx = _projFx[j];
                _projAge[j] += dt;
                if (_projStuck[j] >= 0)
                {
                    _projStuck[j] -= dt;
                    if (_projStuck[j] < 0) { _projOn[j] = false; _projR[j].enabled = false; _proj[j].SetParent(_root, false); }
                    continue;
                }
                var t = _proj[j];
                var p0 = t.position;
                var v = _projV[j] + Vector3.down * fx.gravity_mps2 * dt;
                var p1 = p0 + (_projV[j] + v) * 0.5f * dt;
                _projV[j] = v;
                if (Physics.Linecast(p0, p1, out var hit, ignoreMask, QueryTriggerInteraction.Ignore))
                {
                    t.position = hit.point;
                    Land(j, hit);
                    continue;
                }
                t.SetPositionAndRotation(p1, Quaternion.FromToRotation(Vector3.up, v));
                Trail(j, p0, p1, dt);
                if (_projAge[j] > fx.life_s)
                {
                    if (fx.Explodes) Explode(p1, -v.normalized, fx.radius_m, _p.loadouts[_projWeapon[j]].rig.S.D, null);
                    _projOn[j] = false;
                    _projR[j].enabled = false;
                }
            }
            // Linien
            for (int k = 0; k < LinePool; k++)
            {
                if (_lineKind[k] == LineKind.Off) continue;
                var L = _lines[k];
                _lineAge[k] += dt;
                if (_lineKind[k] == LineKind.Rail)
                {
                    float u = _lineAge[k] / _lineLife[k];
                    if (u >= 1) { _lineKind[k] = LineKind.Off; L.enabled = false; continue; }
                    L.SetPosition(0, _lineA[k]);
                    L.SetPosition(1, _lineB[k]);
                    L.widthMultiplier = _lineW[k] * (1 - 0.7f * u);
                    var c = _lineColor[k] * (9f * (1 - u) * (1 - u));
                    L.startColor = L.endColor = new Color(c.r, c.g, c.b, 1);
                    L.enabled = true;
                    continue;
                }
                var ab = _lineB[k] - _lineA[k];
                float dist = ab.magnitude, head = _lineAge[k] * _lineSpeed[k];
                if (head - _lineLen[k] >= dist)
                {
                    if (_lineKind[k] == LineKind.Bolt) FinishBolt(k);
                    else { _lineKind[k] = LineKind.Off; L.enabled = false; }
                    continue;
                }
                if (_lineKind[k] == LineKind.Bolt && head >= dist && _lineImpact[k] != null)
                {
                    Impact(_lineImpact[k], _lineB[k], _lineN[k], ab, _lineColor[k], true, _lineHit[k]);
                    _lineImpact[k] = null;
                }
                var dir = dist > 1e-4f ? ab / dist : Vector3.forward;
                L.SetPosition(0, _lineA[k] + dir * Mathf.Clamp(head - _lineLen[k], 0, dist));
                L.SetPosition(1, _lineA[k] + dir * Mathf.Clamp(head, 0, dist));
                L.widthMultiplier = _lineW[k];
                var cc = _lineColor[k] * (_lineKind[k] == LineKind.Bolt ? 8f : 4f);
                L.startColor = new Color(cc.r, cc.g, cc.b, 0.25f);
                L.endColor = new Color(cc.r, cc.g, cc.b, 1);
                L.enabled = true;
            }
            // Dauerstrahl der aktiven Waffe
            var fxA = _p.loadouts[active].rig.S.D.gameplay.fx;
            if (beamOn && fxA.kind == "beam")
            {
                _beamFlicker += dt * 37f;
                float fl = 0.82f + 0.18f * Mathf.Sin(_beamFlicker) * Mathf.Sin(_beamFlicker * 0.37f + 1.3f);
                _beam.SetPosition(0, MuzzleWorld(active));
                _beam.SetPosition(1, _beamEnd);
                _beam.widthMultiplier = fxA.width_m * fl;
                var c = _energy[active] * 7f * fl;
                _beam.startColor = _beam.endColor = new Color(c.r, c.g, c.b, 1);
                _beam.enabled = true;
                VmGlow(active, fxA.muzzle_glow_m * 2 * fl, 0.06f);
                if (_beamHit)
                {
                    _beamSparkAcc += dt * 40f;
                    var ep = new ParticleSystem.EmitParams { position = _beamEnd + _beamNormal * 0.03f, velocity = Vector3.zero, startLifetime = 0.06f,
                                                             startSize = 0.22f * fl, startColor = _energy[active] * 3f };
                    _glow.Emit(ep, 1);
                    for (; _beamSparkAcc >= 1; _beamSparkAcc--)
                    {
                        ep.velocity = Hemi(_beamNormal, 0.9f) * R(1.5f, 4.5f);
                        ep.startLifetime = R(0.12f, 0.3f);
                        ep.startSize = R(0.01f, 0.018f);
                        ep.startColor = _energy[active] * 2.5f;
                        _sparks.Emit(ep, 1);
                    }
                }
            }
            else if (_beam.enabled) _beam.enabled = false;
            // Mündungsrauch je Waffe (Werfer nach dem Schuss)
            var Sm = D0.muzzle_smoke;
            for (int k = 0; k < _vmSmoke.Length; k++)
            {
                if (_vmSmokeLeft[k] > 0)
                {
                    float fx = _p.loadouts[k].rig.S.D.gameplay.fx.smoke_s;
                    float strength = fx > 0 ? _vmSmokeLeft[k] / fx : 0;
                    _vmSmokeLeft[k] -= dt;
                    _vmSmokeAcc[k] += dt * Sm.rate_hz * (0.4f + 0.6f * strength);
                    var rig = _p.loadouts[k].rig;
                    var at = rig.space.InverseTransformPoint(rig.AnchorWorld("Socket_Muzzle"));
                    var col = Hex(Sm.color, Color.white);
                    for (; _vmSmokeAcc[k] >= 1; _vmSmokeAcc[k]--)
                    {
                        var ep = new ParticleSystem.EmitParams
                        {
                            position = at + new Vector3(R(-0.01f, 0.01f), R(-0.01f, 0.01f), R(-0.01f, 0.01f)),
                            velocity = new Vector3(R(-0.03f, 0.03f), Sm.rise_mps * R(0.6f, 1.4f), R(-0.03f, 0.03f)),
                            startLifetime = Sm.life_s * R(0.7f, 1.2f), startSize = Sm.puff_m * R(0.7f, 1.3f), rotation = R(0, 360),
                            startColor = new Color(col.r, col.g, col.b, Sm.alpha * (0.5f + 0.5f * strength)),
                        };
                        _vmSmoke[k].Emit(ep, 1);
                    }
                }
                _vmSmoke[k].Simulate(dt, false, false, false);
                _vmGlow[k].Simulate(dt, false, false, false);
            }
            // Druckringe, Lichter
            var X = D0.explosion;
            for (int k = 0; k < RingPool; k++)
            {
                if (!_ringR[k].enabled) continue;
                _ringAge[k] += dt;
                float u = _ringAge[k] / X.ring_s;
                if (u >= 1) { _ringR[k].enabled = false; continue; }
                float e = 1 - (1 - u) * (1 - u) * (1 - u);
                _rings[k].localScale = Vector3.one * _ringSize[k] * (0.15f + 0.85f * e);
                _ringR[k].GetPropertyBlock(_mpb);
                _mpb.SetFloat("_Alpha", (1 - u) * 2.5f);
                _ringR[k].SetPropertyBlock(_mpb);
            }
            for (int k = 0; k < LightPool; k++)
            {
                if (!_lights[k].enabled) continue;
                _lightAge[k] += dt;
                float u = _lightAge[k] / X.light_s;
                if (u >= 1) { _lights[k].enabled = false; continue; }
                _lights[k].intensity = _lightK[k] * (1 - u) * (1 - u) * 8;
            }
            // Löcher und Brandflecken altern und blenden aus
            var Dc = D0.decal;
            for (int k = 0; k < _holes.Length; k++)
            {
                if (_holes[k] == null || !_holeR[k].enabled) continue;
                _holeAge[k] += dt;
                if (_holeAge[k] < Dc.life_s - Dc.fade_s) continue;
                float a = Mathf.Clamp01((Dc.life_s - _holeAge[k]) / Dc.fade_s);
                if (a <= 0) { _holeR[k].enabled = false; continue; }
                SetDecal(_holeR[k], _holeSeed[k], _holeScorch[k] ? 1 : 0, a);
            }
            for (int k = 0; k < ScorchPool; k++)
            {
                if (!_scorchR[k].enabled) continue;
                _scorchAge[k] += dt;
                float a = Mathf.Clamp01((Dc.life_s - _scorchAge[k]) / Dc.fade_s);
                if (a <= 0) _scorchR[k].enabled = false;
                else if (_scorchAge[k] >= Dc.life_s - Dc.fade_s) SetDecal(_scorchR[k], 1.3f, 1, a);
            }
            _sparks.Simulate(dt, false, false, false);
            _dust.Simulate(dt, false, false, false);
            _smoke.Simulate(dt, false, false, false);
            _glow.Simulate(dt, false, false, false);
        }

        /// <summary>Spur hinter dem Projektil: Rakete Rauch und Flamme, Granate dünne helle Spur, Pfeil Lichtspur.</summary>
        void Trail(int j, Vector3 p0, Vector3 p1, float dt)
        {
            var fx = _projFx[j];
            var ep = new ParticleSystem.EmitParams();
            float step = fx.trail == "rocket" ? 0.18f : fx.kind == "arrow" ? 0.35f : 0.30f;
            _projTrail[j] += (p1 - p0).magnitude;
            var dir = (p1 - p0).normalized;
            var col = _energy[_projWeapon[j]];
            if (fx.trail == "rocket")
            {
                ep.position = p1 - dir * fx.length_m * 0.55f;
                ep.velocity = -dir * 2f;
                ep.startLifetime = 0.05f;
                ep.startSize = fx.width_m * R(3f, 4.5f);
                ep.startColor = new Color(1f, 0.6f, 0.3f) * 4f;
                _glow.Emit(ep, 1);
            }
            for (; _projTrail[j] >= step; _projTrail[j] -= step)
            {
                float back = _projTrail[j] - step;
                ep.position = p1 - dir * (back + (fx.trail == "rocket" ? fx.length_m * 0.6f : 0));
                ep.velocity = new Vector3(R(-0.15f, 0.15f), R(0.05f, 0.25f), R(-0.15f, 0.15f));
                ep.rotation = R(0, 360);
                if (fx.trail == "rocket")
                {
                    ep.startLifetime = R(1.4f, 2.2f);
                    ep.startSize = R(0.18f, 0.28f);
                    ep.startColor = new Color(0.78f, 0.79f, 0.81f, R(0.35f, 0.5f));
                    _smoke.Emit(ep, 1);
                }
                else if (fx.kind == "arrow")
                {
                    ep.velocity = Vector3.zero;
                    ep.startLifetime = 0.18f;
                    ep.startSize = 0.05f;
                    ep.startColor = col * 1.8f;
                    _glow.Emit(ep, 1);
                }
                else
                {
                    ep.startLifetime = R(0.5f, 0.8f);
                    ep.startSize = R(0.06f, 0.1f);
                    ep.startColor = new Color(0.85f, 0.86f, 0.88f, 0.28f);
                    _smoke.Emit(ep, 1);
                    ep.velocity = Vector3.zero;
                    ep.startLifetime = 0.12f;
                    ep.startSize = 0.07f;
                    ep.startColor = new Color(1f, 0.85f, 0.6f) * 1.5f;
                    _glow.Emit(ep, 1);
                }
            }
        }

        /// <summary>Lebende Partikel (Tests): Funken, Staub, Rauch, Licht; Mündungsrauch und -licht der Waffe k.</summary>
        public int Sparks => _sparks.particleCount;
        public int Dust => _dust.particleCount;
        public int Smoke => _smoke.particleCount;
        public int Glow => _glow.particleCount;
        public int MuzzleSmoke(int k) => _vmSmoke[k].particleCount;
        public int MuzzleGlow(int k) => _vmGlow[k].particleCount;
        public bool BeamShown => _beam.enabled;
        public Vector3 BeamStart => _beam.GetPosition(0);
        public Vector3 BeamEnd => _beam.GetPosition(1);
        public int LinesShown { get { int n = 0; foreach (var l in _lines) if (l.enabled) n++; return n; } }
        public int RingsShown { get { int n = 0; foreach (var r in _ringR) if (r.enabled) n++; return n; } }
        public int LightsShown { get { int n = 0; foreach (var l in _lights) if (l.enabled) n++; return n; } }
        public int ScorchShown { get { int n = 0; foreach (var r in _scorchR) if (r.enabled) n++; return n; } }
        public int ProjectilesStuck { get { int n = 0; for (int i = 0; i < ProjectilePool; i++) if (_projOn[i] && _projStuck[i] >= 0) n++; return n; } }
        public Color Energy(int k) => _energy[k];

        /// <summary>Alles sofort aus und Messwerte auf 0 (Szenenwechsel, Tests).</summary>
        public void Clear()
        {
            explosions = impacts = launched = bolts = rails = tracers = explosionHits = 0;
            for (int j = 0; j < ProjectilePool; j++) { _projOn[j] = false; _projR[j].enabled = false; _proj[j].SetParent(_root, false); }
            for (int k = 0; k < LinePool; k++) { _lineKind[k] = LineKind.Off; _lineImpact[k] = null; _lines[k].enabled = false; }
            _beam.enabled = false;
            for (int k = 0; k < RingPool; k++) _ringR[k].enabled = false;
            for (int k = 0; k < LightPool; k++) _lights[k].enabled = false;
            for (int k = 0; k < _vmSmoke.Length; k++) { _vmSmokeLeft[k] = 0; _vmSmoke[k].Clear(); _vmGlow[k].Clear(); }
            _sparks.Clear();
            _dust.Clear();
            _smoke.Clear();
            _glow.Clear();
        }
    }
}
