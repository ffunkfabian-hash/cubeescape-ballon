// Ruckelmessung (0.37 „Steadyframe“, -ballonStutter <csv>): fester Ablauf je Waffe in Echtzeit mit den Spieleinstellungen (VSync,
// höchstens 120/s) – Waffenwechsel, Hüftschuss, Dauerfeuer 3 s, Zielen, Nachladen. Zwei Durchgänge im selben Prozess: 1 = erster
// Einsatz nach dem Start, 2 = Wiederholung. Dazu je Waffe 3 s Bewegung (gehen, seitwärts, drehen; Nutzerbefund „auch beim Bewegen“). Je Bild Bildzeit, Hauptthread-Zeit, GC-Speicher und GC-Läufe in vorab angelegte Felder
// (die Messung selbst erzeugt keinen Speicher), CSV am Ende. Mit -ballonProfile <Ordner> zusätzlich das Profiler-Binärprotokoll je
// Durchgang und Waffe, jedes Bild mit Metadaten (Bildnummer, Durchgang, Waffe, Ereignis) für BallonSetup.ProfileSpikes im Editor.
using System;
using System.IO;
using System.Text;
using Unity.Profiling;
using UnityEngine;
using UnityEngine.Profiling;

namespace Ballon.Ego
{
    public sealed class StutterBench : MonoBehaviour
    {
        public static readonly string[] Events = { "start", "wechsel", "huefte", "dauerfeuer", "zielen", "nachladen", "bewegen", "ende" };
        /// <summary>Kennung der Bild-Metadaten im Profiler-Protokoll: int[4] = Time.frameCount, Durchgang, Waffe, Ereignis.</summary>
        public static readonly Guid MetaId = new Guid("6f1c8f3e-2b7a-4f0e-9d51-0b37a1e5c0de");
        const int Capacity = 120000;

        /// <summary>Eingabe der Messung: gehaltene Tasten und einmalige Tasten (im nächsten gelesenen Bild verbraucht).</summary>
        sealed class Pad : IEgoInput
        {
            public bool fire, aim, reload;
            public int select;
            public Vector2 move, lookPerS;
            public RawInput Read(float dt, float zoom)
            {
                var r = new RawInput { fire = fire, aim = aim, reload = reload, select = select, move = move, lookDeg = lookPerS * dt };
                reload = false;
                select = 0;
                return r;
            }
        }

        struct Seg { public float t0, t1, holdFire, holdAim; public int pass, weapon, ev; public bool walk; }

        Bootstrap _b;
        EgoPlayer P => _b.Player;
        string _csv, _profile;
        readonly Pad _pad = new Pad();
        Seg[] _plan;
        int _seg = -1;
        float _t;
        int _n, _lastEv, _lastPass, _lastWeapon, _gc0, _overflow;
        float[] _dt, _main;
        long[] _alloc;
        int[] _frame, _collect;
        short[] _pass, _weapon, _ev;
        ProfilerRecorder _gcRec, _mainRec;
        readonly int[] _meta = new int[4];

        public static StutterBench Start(Bootstrap b, string csv, string profileDir)
        {
            var s = b.gameObject.AddComponent<StutterBench>();
            s._b = b;
            s._csv = csv;
            s._profile = profileDir;
            return s;
        }

        void Awake()
        {
            _dt = new float[Capacity];
            _main = new float[Capacity];
            _alloc = new long[Capacity];
            _frame = new int[Capacity];
            _collect = new int[Capacity];
            _pass = new short[Capacity];
            _weapon = new short[Capacity];
            _ev = new short[Capacity];
        }

        void OnEnable()
        {
            _gcRec = ProfilerRecorder.StartNew(ProfilerCategory.Memory, "GC Allocated In Frame");
            _mainRec = ProfilerRecorder.StartNew(ProfilerCategory.Internal, "Main Thread", 1);
        }

        void OnDisable()
        {
            _gcRec.Dispose();
            _mainRec.Dispose();
        }

        void BuildPlan()
        {
            var plan = new System.Collections.Generic.List<Seg>();
            float t = 0;
            void Add(int pass, int w, int ev, float dur, float fire = 0, float aim = 0, bool walk = false)
            {
                plan.Add(new Seg { t0 = t, t1 = t + dur, holdFire = fire, holdAim = aim, pass = pass, weapon = w, ev = ev, walk = walk });
                t += dur;
            }
            int nw = _b.Solvers.Length;
            Add(0, 0, 0, 3f);                                                  // Ruhe nach dem Laden
            for (int pass = 0; pass < 2; pass++)
                for (int w = 0; w < nw; w++)
                {
                    var g = _b.Solvers[w].D.gameplay;
                    if (pass > 0 || w > 0) Add(pass, w, 1, 2.0f);                 // Waffenwechsel (Wegstecken, leere Sicht, Ziehen)
                    float tap = g.Draw ? 1.2f : g.charge_s > 0 ? 1.0f : 0.05f;     // Bogen spannen, Fusion aufladen, sonst ein Zug
                    Add(pass, w, 2, 2.0f, tap);                                   // Hüftschuss (mit Flug und Einschlag)
                    Add(pass, w, 3, 3.5f, 3f);                                    // Dauerfeuer 3 s
                    Add(pass, w, 4, 2.0f, 0, 1.5f);                               // Zielen
                    Add(pass, w, 5, 3.0f);                                        // Nachladen
                    Add(pass, w, 6, 3.0f, walk: true);                            // Bewegen: hin und zurück, seitwärts, drehen
                }
            Add(1, nw - 1, 7, 1f);
            _plan = plan.ToArray();
        }

        void Update()
        {
            if (_plan == null)
            {
                BuildPlan();
                P.input = _pad;
                P.hud = true;
                _gc0 = GC.CollectionCount(0);
                _lastPass = _lastWeapon = _lastEv = 0;
                _t = 0;
                if (_profile != null)
                {
                    Directory.CreateDirectory(_profile);
                    Profiler.maxUsedMemory = 256 * 1024 * 1024;
                }
            }
            else
            {
                Record();
                _t += Time.unscaledDeltaTime;
            }
            while (_seg + 1 < _plan.Length && _t >= _plan[_seg + 1].t0) Enter(_seg + 1);
            if (_t >= _plan[_plan.Length - 1].t1)
            {
                Finish();
                return;
            }
            var s = _plan[_seg];
            float e = _t - s.t0;
            _pad.fire = e < s.holdFire;
            _pad.aim = e < s.holdAim;
            // Bewegen: 1,5 s vorwärts und rechts mit Drehung nach rechts, dann zurück (die Figur endet am Ausgangspunkt)
            float dir = e < 1.5f ? 1f : -1f;
            _pad.move = s.walk ? new Vector2(0.6f * dir, 0.8f * dir) : Vector2.zero;
            _pad.lookPerS = s.walk ? new Vector2(60f * dir, 0) : Vector2.zero;
            _meta[0] = Time.frameCount;
            _meta[1] = s.pass + 1;
            _meta[2] = s.weapon + 1;
            _meta[3] = s.ev;
            if (_profile != null) Profiler.EmitFrameMetaData(MetaId, 0, _meta);
            _lastPass = s.pass;
            _lastWeapon = s.weapon;
            _lastEv = s.ev;
        }

        void Enter(int k)
        {
            var prev = _seg >= 0 ? _plan[_seg] : default;
            _seg = k;
            var s = _plan[k];
            var c = P.arsenal.C[s.weapon];
            if (s.ev == 1) _pad.select = s.weapon + 1;
            if (s.ev == 2 || s.ev == 3) c.ammo = c.magSize;                  // jeder Schuss soll fallen (nicht das Nachladen messen)
            if (s.ev == 5) _pad.reload = true;
            if (_profile != null && (_seg == 0 || s.pass != prev.pass || s.weapon != prev.weapon))
            {
                Profiler.enabled = false;
                Profiler.logFile = Path.Combine(_profile, $"p{s.pass + 1}_w{s.weapon + 1:00}");
                Profiler.enableBinaryLog = true;
                Profiler.enabled = true;
            }
        }

        void Record()
        {
            if (_n >= Capacity) { _overflow++; return; }
            _dt[_n] = Time.unscaledDeltaTime * 1000f;
            _main[_n] = _mainRec.Valid ? _mainRec.LastValue * 1e-6f : -1f;
            _alloc[_n] = _gcRec.Valid ? _gcRec.LastValue : -1;
            int gc = GC.CollectionCount(0);
            _collect[_n] = gc - _gc0;
            _gc0 = gc;
            _frame[_n] = Time.frameCount - 1;
            _pass[_n] = (short)(_lastPass + 1);
            _weapon[_n] = (short)(_lastWeapon + 1);
            _ev[_n] = (short)_lastEv;
            _n++;
        }

        void Finish()
        {
            enabled = false;
            if (_profile != null)
            {
                Profiler.enabled = false;
                Profiler.enableBinaryLog = false;
                Profiler.logFile = "";
            }
            var I = System.Globalization.CultureInfo.InvariantCulture;
            var sb = new StringBuilder("frame,pass,weapon,type,event,dt_ms,main_ms,gc_alloc_b,gc_collect\n");
            for (int i = 0; i < _n; i++)
                sb.Append(_frame[i]).Append(',').Append(_pass[i]).Append(',').Append(_weapon[i]).Append(',')
                  .Append(_b.Solvers[_weapon[i] - 1].D.gameplay.weapon_type).Append(',').Append(Events[_ev[i]]).Append(',')
                  .Append(_dt[i].ToString("0.000", I)).Append(',').Append(_main[i].ToString("0.000", I)).Append(',')
                  .Append(_alloc[i]).Append(',').Append(_collect[i]).Append('\n');
            File.WriteAllText(_csv, sb.ToString());
            File.WriteAllText(Path.ChangeExtension(_csv, ".json"), string.Format(I,
                "{{\"frames\": {0}, \"width\": {1}, \"height\": {2}, \"gpu\": \"{3}\", \"refresh_hz\": {4:0.0}, \"vsync\": {5}, \"target_fps\": {6}, " +
                "\"profiler\": {7}, \"development\": {8}, \"unity\": \"{9}\", \"not_recorded\": {10}}}\n", _n, Screen.width, Screen.height, SystemInfo.graphicsDeviceName,
                Screen.currentResolution.refreshRateRatio.value, QualitySettings.vSyncCount, Application.targetFrameRate,
                _profile != null ? "true" : "false", Debug.isDebugBuild ? "true" : "false", Application.unityVersion, _overflow));
            if (_overflow > 0) Debug.LogWarning($"[Ballon] Ruckelmessung: {_overflow} Bilder über {Capacity} nicht aufgezeichnet");
            Debug.Log($"[Ballon] Ruckelmessung: {_n} Bilder → {_csv}");
            Application.Quit();
        }
    }
}
