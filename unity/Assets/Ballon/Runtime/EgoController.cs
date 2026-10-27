// Spielbare Ego-Zustandsmaschine: spielt die Aktionen aus ego.json als Spuren (Bilder bei 30 fps, Marker), hält Haltungen,
// blendet zwischen Spuren über und legt live gerechnete Ebenen darüber (Rückstoß, Kamera-Feedback, Pendeln, Wippen, Atmen).
// Reine C#-Klasse ohne Unity-Szene: PlayMode-Tests treiben sie direkt, EgoPlayer liefert Eingaben und wendet das Ergebnis an.
using System;
using System.Collections.Generic;
using UnityEngine;
using static Ballon.Ego.BMath;

namespace Ballon.Ego
{
    public struct EgoIntent
    {
        public bool fire, aim, sprint, crouch, grounded, nearWall;
        public bool reload, inspect, draw, holster, swap;   // gedrückt in diesem Bild (swap: Waffe wechseln, 6.1 A)
        public float speed01;                           // Laufgeschwindigkeit relativ zum Gehen (0 … ~1,6 im Sprint)
        public Vector2 look;                            // Mausbewegung in Grad in diesem Bild (x rechts, y hoch)
        public Vector2 move;                            // Bewegungsrichtung (x rechts, y vorn), Länge ≤ 1
    }

    /// <summary>Einstellwerte der Live-Ebenen (entworfen, am Spielgefühl eingestellt; Blender-Formeln wo vorhanden).</summary>
    [Serializable]
    public class EgoTuning
    {
        public float fadeFrames = 4f;          // Überblendung zwischen Spuren
        public float cancelFadeFrames = 6f;    // Abbruch (Betrachten)
        // Pendeln kritisch gedämpft wie der Visier-Anflug (Frage 3.3 A, Destiny: Rückkehr ≈ 0,3 s ohne Überschwingen):
        // 2,5 Hz bei ζ 1 → Rest ≈ 5 % nach 0,30 s
        public float swayPerDeg = 0.35f, swayMaxDeg = 3.0f, swayFreq = 2.5f, swayDamp = 1.0f, swayPos = 0.0035f;
        public float swayAds = 0.25f, bobAds = 0.2f, breatheAds = 0.35f;
        public float moveTiltDeg = 1.6f;
        public float boltOpenS = 0.05f;        // 1,5 Bilder wie in ego_build
    }

    public sealed class EgoController
    {
        public enum Stance { Hip, Ads, Sprint, Crouch, Air, Lowered }

        sealed class Track
        {
            public EgoAction A;
            public float frame, end;
            public int dir = 1;
            public float loopA = -1, loopB = -1;
            public bool busy;                  // blockiert Haltungswechsel (Nachladen, Ziehen …)
            public bool scripted;              // geskriptete Ebenen aus der Aktion (Referenz, Tests)
            public Stance? stance;             // Haltung, die diese Spur hält
            public Action<Track> onEnd;
            public bool ended;
            public readonly EgoState st = new EgoState();

            /// <summary>Für die Wiederverwendung (Spurpool, 0.18: kein Speicher je neuer Spur, auch nicht beim Wechsel).</summary>
            public void Reset()
            {
                A = null; frame = end = 0; dir = 1; loopA = loopB = -1; busy = scripted = ended = false; stance = null; onEnd = null;
                st.hasRel = st.hasSec = st.hasRec = false;
                if (st.shotSet != null) Array.Clear(st.shotSet, 0, st.shotSet.Length);
            }
        }
        // drei Spuren im Wechsel: die laufende, die vorige (Rückruf am Ende) und die nächste; Rückrufe einmal angelegt
        readonly Track[] _pool = { new Track(), new Track(), new Track() };
        int _poolNext;
        readonly Action<Track> _onReady, _onHolster, _onHolsterSwap, _onSwitchedOut;

        Track NextTrack()
        {
            var t = _pool[_poolNext];
            _poolNext = (_poolNext + 1) % _pool.Length;
            t.Reset();
            return t;
        }

        public readonly EgoSolver S;
        public readonly EgoTuning tune;
        public readonly EgoOutput output;
        public event Action<string, string> Marker;     // (Aktion, Marker)
        public event Action Shot;

        public int ammo, magSize;
        public float rpm;
        public bool holstered = true;
        public float adsWeight;            // 0 Hüfte … 1 Zielen (für FOV, Empfindlichkeit, Streuung); folgt dem Modell (1d)
        public long shots;
        public float worldZoom;            // Weltzoom der Klasse im Zielen (ego.json › gameplay.world_zoom)
        public float Zoom => Mathf.Lerp(1f, worldZoom, adsWeight);
        /// <summary>Grundbahn der Welt in Grad (x Gieren rechts, y Nicken hoch) – Messwert für Tests und Aufnahme.</summary>
        public Vector2 PathDeg => _path;
        /// <summary>Waffenhaltung nach dem Feder-Nachlauf, ohne Live-Ebenen (Wippen, Rückstoß) – daraus folgt der Zoom (1d).</summary>
        public Matrix4x4 BaseWeapon { get; private set; }

        Track _t;
        Stance _stance = Stance.Hip;
        bool _fireArmed;                   // Feuer nach sprint_to_fire erst ab Marker „Fire“
        float _shotClock, _boltT, _sinceShot = 99f;
        bool _portOpen, _triggerHeld;
        bool _semiPrev;                    // Einzelfeuer: Abzug im letzten Bild gedrückt (Zug = Flanke)
        float _semiQueue;                  // Einzelfeuer: Restzeit eines wartenden Zugs (s)
        const float SemiQueueS = 0.4f;     // E: ein Zug wartet höchstens so lange (Schussabstand 180/min = 0,33 s, Sprint → Feuer 0,23 s)
        Vector3 _recX, _recV, _recCx, _recCv;
        float _rClimb, _dt = 1f / 30f;
        Vector3 _path, _pathV, _pathTgt;   // Grundbahn der Welt (x Gieren, y Nicken, Grad), Ziel der Salve
        int _pathN, _burstLeft;            // Schuss in der Salve (feste Seitenfolge), Rest einer Salve (Salvenwaffen)
        float _worldPitch, _worldYaw;
        readonly float _tanH;              // tan des halben horizontalen Bildwinkels (ungezoomt)
        /// <summary>Seitenverhältnis des Bilds (EgoPlayer setzt es je Bild aus der Kamera): die Grundbahn rechnet in Anteilen der Bildhöhe.</summary>
        public float aspect;
        readonly Vector3 _eyeLocal;
        readonly float _dHip;              // Abstand Augenpunkt → Kamera in der Hüfte
        float _d0 = 1, _leaveT;
        bool _aimPrev, _leaving;
        bool _swapPending;                 // Wechsel: nach dem Wegstecken leere Sicht, dann Ziehen
        bool _switchedOut;                 // Wechsel auf eine andere Waffe (EgoArsenal): weggesteckt, die andere Waffe zieht
        float _emptyT, _drawEnters = -1;
        bool _hasSec;
        Vector3 _secP, _secV, _secAv;
        Quaternion _secQ;
        Vector3 _sway, _swayV;             // x Gieren, y Nicken (Grad), z ungenutzt
        float _bobPh, _bobW, _sprintW, _breatheW = 1, _breathePh, _tilt;
        float _fade = 1, _fadeLen;
        Matrix4x4 _fromBase, _fromRelL, _fromRelR;
        readonly float[] _fromFL = new float[15], _fromFR = new float[15];
        readonly Dictionary<string, float> _fromMech = new Dictionary<string, float>();
        Matrix4x4 _lastBase = Matrix4x4.identity;
        readonly Dictionary<string, float> _mech = new Dictionary<string, float>();
        readonly EgoAction _walk, _sprintA;
        bool _hasOutput, _firePrev;
        EgoIntent _intent;
        Func<string, Matrix4x4> _pf;
        // Mündungsfeuer (5.3 A): sichtbar flash.dur_s ab dem Schuss; Hülsen (5.4 A): fester Pool (Ring) mit motion.eject.max_live Plätzen
        float _flashLeft;
        int _flashShot, _pendingShells;
        readonly Matrix4x4[] _shW;
        readonly float[] _shAge;
        readonly int[] _shId;
        readonly bool[] _shOn;
        int _shNext;
        /// <summary>Schüsse seit dem Start, die eine Hülse auswarfen (Messwert für Tests).</summary>
        public long shellsEjected;
        // Werkzeug mit Portalen (0.22, gameplay.portals): Ring in Dritteln (live, folgt dem Ziel in ring_turn_s), letztes Portal, Zug je Taste
        float _ring, _ringFrom, _ringTgt, _ringT = 1;
        bool _portalPrevA, _portalPrevB;
        int _portalQueued = -1;
        /// <summary>Portal des letzten Schusses (Index in gameplay.portals), −1 bei Waffen ohne Portale.</summary>
        public int LastPortal { get; private set; } = -1;
        /// <summary>Ringdrehung des Werkzeugs in Dritteln (1 = 120°), wie sie das Modell gerade zeigt.</summary>
        public float RingTurns => _ring;
        /// <summary>Ziel der Ringdrehung in Dritteln (je Schuss ± 1).</summary>
        public float RingTarget => _ringTgt;

        public EgoController(EgoSolver s, EgoTuning tuning = null)
        {
            S = s;
            tune = tuning ?? new EgoTuning();
            output = s.NewOutput();
            magSize = ammo = s.D.gameplay.magazine;
            rpm = s.D.gameplay.rpm;
            worldZoom = s.D.gameplay.world_zoom;
            _tanH = Mathf.Tan(Rad(s.D.camera.h_fov_deg) / 2);
            aspect = s.D.camera.aspect[0] / (float)s.D.camera.aspect[1];
            _eyeLocal = V(s.D.Anchor(s.D.HasAnchor("Socket_Eye") ? "Socket_Eye" : "Socket_Muzzle").pos);   // Werkzeug ohne Visier (0.22)
            _dHip = s.PoseMatrix("hip").MultiplyPoint3x4(_eyeLocal).magnitude;
            _walk = s.D.Action("walk");
            _sprintA = s.D.Action("sprint");
            int cap = s.D.motion.eject.max_live;
            _shW = new Matrix4x4[cap];
            _shAge = new float[cap];
            _shId = new int[cap];
            _shOn = new bool[cap];
            _onReady = _ => Ready();
            _onHolster = _ => holstered = true;
            _onHolsterSwap = _ =>
            {
                holstered = true;
                _swapPending = true;                                    // Wechsel (6.1 A): Wegstecken, leere Sicht, Ziehen
                _emptyT = S.D.motion.@switch.empty_s;
                Marker?.Invoke("switch", "Empty");
            };
            _onSwitchedOut = _ =>
            {
                holstered = true;
                _switchedOut = true;
                Marker?.Invoke("switch", "Empty");
            };
            Hold("holster", Stance.Hip);
        }

        /// <summary>Wechsel (6.1 A): letztes Bild von draw, in dem weder Waffe noch Arme im Bild sind (Silhouette aus den Netzgrenzen). Beim
        /// Wechsel beginnt das Ziehen dort – der unsichtbare Anfang (≈ 0,35 s) fiele sonst in die leere Sicht; der sichtbare Teil bleibt wie
        /// beim Ziehen mit Taste 1. Der Controller rechnet es beim ersten Wechsel einmal (_drawEnters).</summary>
        public static float DrawEnters(EgoSolver s)
        {
            var E = new EgoScreen(s);
            var A = s.D.Action("draw");
            var st = new EgoState();
            var pts = new List<Vector2>();
            float hidden = 0;
            for (int f = 0; f <= A.frames; f++)
            {
                E.Silhouette(s.Evaluate(A, f, st), pts);
                if (pts.Count > 0) break;
                hidden = f;
            }
            return hidden;
        }

        /// <summary>Wechsel auf eine andere Waffe (Tasten 1/2, EgoArsenal, 0.18): Wegstecken wie beim Wechsel mit Q (holster, beim Nachladen
        /// reload_to_switch), danach bleibt diese Waffe weggesteckt; SwitchedOut meldet das Ende (Marker switch › Empty). Ist sie schon
        /// weggesteckt, gilt sie sofort als draußen.</summary>
        public void SwitchOut()
        {
            _swapPending = false;
            if (holstered && _t.ended) { _switchedOut = true; return; }
            bool reloading = (_t.A.name == "reload_tactical" || _t.A.name == "reload_empty") && !_t.ended;
            if (_t.A.name == "holster" || _t.A.name == "reload_to_switch")    // läuft schon: nur das Ende umleiten
            {
                _t.onEnd = _onSwitchedOut;
                return;
            }
            Play(reloading ? "reload_to_switch" : "holster", busy: true, fade: reloading ? 3 : -1, onEnd: _onSwitchedOut);
            holstered = false;
        }

        /// <summary>Diese Waffe ist nach SwitchOut weggesteckt (die leere Sicht läuft beim Arsenal).</summary>
        public bool SwitchedOut => _switchedOut;

        /// <summary>Zweite Hälfte des Wechsels auf diese Waffe: im nächsten Tick ziehen wie beim Wechsel mit Q (draw ab dem ersten sichtbaren
        /// Bild, bei gehaltenem Zielen draw_aim); die leere Sicht hat das Arsenal schon abgewartet.</summary>
        public void SwitchIn()
        {
            _switchedOut = false;
            holstered = true;
            if (!_t.ended || _t.A.name != "holster") Hold("holster", Stance.Hip);
            _swapPending = true;
            _emptyT = 0;
        }

        /// <summary>DrawEnters einmal vorab rechnen (sonst beim ersten Wechsel: Speicher im laufenden Bild).</summary>
        public void Prepare() { if (_drawEnters < 0) _drawEnters = DrawEnters(S); }

        public string ActionName => _t.A.name;
        public float Frame => _t.frame;
        public bool Busy => _t.busy && !_t.ended;
        public Stance CurrentStance => _stance;
        /// <summary>Pendeln in Grad (x Gieren, y Nicken) – Messwert für Aufnahme und Bericht.</summary>
        public Vector2 SwayDeg => _sway;
        public bool Holstered => holstered;

        // -------------------------------------------------------------- Spuren
        Track Play(string name, float from = 0, float to = -1, int dir = 1, bool busy = false, Stance? stance = null,
                   float fade = -1, Action<Track> onEnd = null, bool scripted = false)
        {
            var A = S.D.Action(name);
            if (_hasOutput)
            {
                _fromBase = _lastBase;
                _fromRelL = output.weapon.inverse * output.handL;
                _fromRelR = output.weapon.inverse * output.handR;
                Array.Copy(output.fingersL, _fromFL, 15);
                Array.Copy(output.fingersR, _fromFR, 15);
                _fromMech.Clear();
                foreach (var kv in output.mech) _fromMech[kv.Key] = kv.Value;
                _fadeLen = fade < 0 ? tune.fadeFrames : fade;
                _fade = _fadeLen > 0 ? 0 : 1;
            }
            var t = NextTrack();
            t.A = A; t.frame = from; t.end = to < 0 ? A.frames : to; t.dir = dir; t.busy = busy; t.stance = stance; t.onEnd = onEnd;
            t.scripted = scripted;
            _t = t;
            if (dir > 0) Emit(from - 0.001f, from);
            return _t;
        }

        void Hold(string name, Stance st, float at = -1)
        {
            var A = S.D.Action(name);
            var t = NextTrack();
            t.A = A; t.frame = t.end = at < 0 ? A.frames : at; t.ended = true; t.stance = st;
            _t = t;
        }

        /// <summary>Sofort bereit an der Hüfte (Aufnahme, Tests).</summary>
        public void ReadyNow() => Ready();

        /// <summary>Eine Aktion vollständig abspielen (Tests, Vorführung), danach Haltung halten.</summary>
        public void PlayAction(string name, bool scripted = true, Action onEnd = null)
        {
            holstered = false;
            Play(name, busy: true, fade: 0, scripted: scripted, onEnd: _ => onEnd?.Invoke());
        }

        void Emit(float f0, float f1)
        {
            foreach (var m in _t.A.events)
                if (m.f > f0 && m.f <= f1)
                {
                    if (m.name == "MagIn") ammo = magSize;
                    if (m.name == "Fire") _fireArmed = true;
                    Marker?.Invoke(_t.A.name, m.name);
                }
        }

        void Advance(float df)
        {
            if (_t.ended) return;
            float f0 = _t.frame;
            float f1 = f0 + df * _t.dir;
            if (_t.loopA >= 0 && _t.dir > 0 && f1 >= _t.loopB)
            {
                Emit(f0, _t.loopB);
                f1 = _t.loopA + (f1 - _t.loopB) % (_t.loopB - _t.loopA);
                _t.frame = f1;
                return;
            }
            bool done = _t.dir > 0 ? f1 >= _t.end : f1 <= _t.end;
            if (done) f1 = _t.end;
            if (_t.dir > 0) Emit(f0, f1);
            _t.frame = f1;
            if (done)
            {
                _t.ended = true;
                var cb = _t.onEnd;
                _t.onEnd = null;
                cb?.Invoke(_t);
            }
        }

        // -------------------------------------------------------------- Zustände
        void Ready()
        {
            var i = _intent;
            holstered = false;
            if (_t.A.EndsInAds)                                         // draw_aim, sprint_to_aim: im Zielen ankommen
            {
                _stance = Stance.Ads;
                _t.stance = Stance.Ads;
                _t.busy = false;
                if (!i.aim) EnterStance(Stance.Hip, i);
                return;
            }
            _stance = Stance.Hip;
            Hold("idle_hip", Stance.Hip, 0);
            _t.ended = false;
            _t.loopA = 0;
            _t.loopB = _t.A.frames;
            _t.end = _t.A.frames;
            if (i.aim && S.D.CanAim) EnterStance(Stance.Ads, i);
        }

        void EnterStance(Stance target, EgoIntent i)
        {
            var from = _stance;
            if (target == from && _t.stance == target) return;
            switch (target)
            {
                case Stance.Ads:
                    if (from == Stance.Sprint) Play("sprint_to_aim", stance: Stance.Ads);
                    else if (_t.A.name == "aim_out" && !_t.ended)          // umkehren an gleicher Stelle
                        Play("aim_in", from: (1 - _t.frame / _t.A.frames) * K("aim_in", 1), stance: Stance.Ads, fade: 2);
                    else Play("aim_in", stance: Stance.Ads, fade: AimFade("aim_in"));
                    break;
                case Stance.Sprint:                                         // Beginn, Schleife zwischen Schlüssel 1 und 2, Ende
                    var s = Play("sprint", stance: Stance.Sprint);
                    s.loopA = K("sprint", 1);
                    s.loopB = K("sprint", 2);
                    break;
                case Stance.Crouch: Play("crouch", 0, K("crouch", 1), stance: Stance.Crouch); break;
                case Stance.Air: Play("jump_land", 0, K("jump_land", 2), stance: Stance.Air); break;
                case Stance.Lowered: Play("lowered", 0, K("lowered", 2), stance: Stance.Lowered); break;
                default: // Hip: Rückweg je nach Ausgangshaltung
                    Track r;
                    if (from == Stance.Ads)
                    {
                        if (_t.A.name == "aim_in" && !_t.ended)
                            r = Play("aim_out", from: (1 - Mathf.Clamp01(_t.frame / K("aim_in", 1))) * S.D.Action("aim_out").frames,
                                     stance: Stance.Hip, fade: 2);
                        else r = Play("aim_out", stance: Stance.Hip, fade: AimFade("aim_out"));
                    }
                    else if (from == Stance.Sprint && _t.A.name == "sprint" && _t.frame >= K("sprint", 1))
                    {
                        r = _t;            // Sprint-Ende aus der Schleife ohne Überblendung
                        r.loopA = r.loopB = -1;
                        r.frame = Mathf.Max(r.frame, K("sprint", 2));
                        r.stance = Stance.Hip;
                    }
                    else if (from == Stance.Crouch && _t.A.name == "crouch")
                        r = Play("crouch", Mathf.Min(_t.frame, K("crouch", 1)), 0, dir: -1, stance: Stance.Hip, fade: 0);
                    else if (from == Stance.Air) r = Play("jump_land", K("jump_land", 2), stance: Stance.Hip);
                    else if (from == Stance.Lowered && _t.A.name == "lowered")
                        r = Play("lowered", Mathf.Max(K("lowered", 2), _t.frame), stance: Stance.Hip);
                    else r = Play("idle_hip", 0, 0, stance: Stance.Hip);
                    r.onEnd = _onReady;
                    break;
            }
            _stance = target;
        }

        /// <summary>Überblendung beim Zielen ein/aus höchstens die halbe Aktionsdauer (0.18): der kurze MP-Anflug (4 Bilder, 4d) würde sonst
        /// fast ganz überblendet und langsamer (gemessen 14 statt ≤ 12 Bilder bei 60/s); Automatik (10/8 Bilder) bleibt bei fadeFrames.</summary>
        float AimFade(string action) => Mathf.Min(tune.fadeFrames, 0.5f * S.D.Action(action).frames);

        /// <summary>Bild des Waffenschlüssels i einer Aktion (Haltung erreicht/gehalten; nach TIME_SCALE gestreckt).</summary>
        float K(string action, int i) => S.D.Action(action).weapon[i].f;

        /// <summary>Nachladen möglich: Waffe mit Magazin und Nachladeaktion, nicht voll (Werkzeug: nie, 0.22).</summary>
        bool CanReload => S.D.CanReload && ammo < magSize;

        /// <summary>Werkzeug (0.22): Rechtsklick (aim) löst Portal B aus statt zu zielen.</summary>
        bool PortalB(EgoIntent i) => i.aim && S.D.gameplay.HasPortals;

        Stance Wanted(EgoIntent i)
        {
            if (i.sprint && i.move.y > 0.3f && i.grounded && !i.aim && !i.fire) return Stance.Sprint;
            if (i.aim && S.D.CanAim) return Stance.Ads;
            if (!i.grounded) return Stance.Air;
            if (i.nearWall && !i.fire && !PortalB(i)) return Stance.Lowered;
            if (i.crouch) return Stance.Crouch;
            return Stance.Hip;
        }

        void Cancel(EgoIntent i)
        {
            Play("idle_hip", 0, 0, fade: tune.cancelFadeFrames, onEnd: _onReady);
        }

        // -------------------------------------------------------------- Bild
        public EgoOutput Tick(float dt, EgoIntent i)
        {
            _intent = i;
            float df = dt * S.fps;
            bool inspecting = _t.A.name == "inspect" && !_t.ended;
            bool reloading = (_t.A.name == "reload_tactical" || _t.A.name == "reload_empty") && !_t.ended;

            // Eingaben, die Spuren starten
            if (holstered)
            {
                if (_swapPending && _t.ended) _emptyT -= dt;            // Wechsel: leere Sicht läuft
                if ((i.draw || (_swapPending && _emptyT <= 0)) && _t.ended && _t.A.name != "draw")
                {
                    bool swap = _swapPending;
                    if (swap)
                    {
                        Marker?.Invoke("switch", "Draw");
                        _hasSec = false;                                // Feder-Nachlauf ab der übersprungenen Stelle neu
                    }
                    _swapPending = false;
                    Play(i.aim && S.D.CanAim ? "draw_aim" : "draw", from: swap ? (_drawEnters >= 0 ? _drawEnters : _drawEnters = DrawEnters(S)) : 0, busy: true, fade: 0, onEnd: _onReady);
                }
            }
            else if ((i.holster || i.swap) && _t.A.name != "holster" && _t.A.name != "reload_to_switch")
            {
                Play(reloading ? "reload_to_switch" : "holster", busy: true, fade: reloading ? 3 : -1, onEnd: i.swap ? _onHolsterSwap : _onHolster);
                holstered = false;
            }
            else if (inspecting && (i.fire || i.aim || i.reload || (i.sprint && i.move.y > 0.3f)))
            {
                if (i.reload && CanReload) StartReload(i);          // R beim Betrachten: gleich nachladen
                else Cancel(i);
            }
            else if (!Busy)
            {
                if (i.reload && CanReload)
                    StartReload(i);
                else if (i.fire && !_firePrev && ammo == 0 && !reloading && CanReload)     // Abzug bei leerem Magazin: selbst nachladen
                    StartReload(i);
                else if (i.inspect && _stance != Stance.Sprint)
                    Play("inspect", busy: true, fade: 2, onEnd: _onReady);
                else if (_stance == Stance.Sprint && (i.fire || PortalB(i)))
                {
                    _fireArmed = false;
                    Play("sprint_to_fire", stance: Stance.Hip, onEnd: _onReady);
                    _stance = Stance.Hip;
                }
                else if ((_t.stance.HasValue || _t.ended) && !SemiShotWaits)
                {
                    var w = Wanted(i);
                    if (w != _stance) EnterStance(w, i);
                }
            }

            _firePrev = i.fire;
            Advance(df);
            if (_fade < 1) _fade = Mathf.Min(1, _fade + df / Mathf.Max(1e-3f, _fadeLen));
            UpdateLive(dt, i);
            return Compose();
        }

        /// <summary>Einzelfeuer aus dem Sprint (Richter 0.20): ein kurzer Klick bei gehaltenem Sprint wartet in sprint_to_fire auf den Marker
        /// „Fire“; ohne diese Sperre wählte Wanted() nach dem Loslassen wieder den Sprint und der Zug verfiel ohne Schuss.</summary>
        bool SemiShotWaits => _semiQueue > 0 && _t.A.name == "sprint_to_fire" && !_t.ended && HasAmmo;

        /// <summary>Munition da (Werkzeug ohne Magazin: immer, 0.22).</summary>
        bool HasAmmo => S.D.gameplay.Unlimited || ammo > 0;

        void StartReload(EgoIntent i)
        {
            _stance = Stance.Hip;
            Play(ammo == 0 ? "reload_empty" : "reload_tactical", busy: true, fade: 3, onEnd: _onReady);
        }

        bool CanFire => !holstered && !Busy && HasAmmo && (_t.A.name != "sprint_to_fire" || _fireArmed) && _stance != Stance.Sprint
                        && !(_t.A.name == "sprint" && _t.frame < K("sprint", 2)) && _t.A.name != "draw" && _t.A.name != "holster";

        /// <summary>Abstand zum nächsten Schuss: Dauerfeuer 60/rpm; Salvenwaffe (gameplay.burst_shots n > 0, 0.22 je Klasse) in der Salve
        /// 60/burst_rpm, danach bis zur nächsten Salve der Rest der Salvenfolge n · 60/rpm (rpm wie das Destiny-Menü: Schuss je Minute über
        /// die Salvenfolge gemittelt; bis 0.21 Salven je Minute).</summary>
        float ShotInterval()
        {
            var G = S.D.gameplay;
            if (!G.Burst) return 60f / rpm;
            float inBurst = 60f / G.burst_rpm;
            return _burstLeft > 0 ? inBurst : Mathf.Max(inBurst, G.burst_shots * 60f / rpm - (G.burst_shots - 1) * inBurst);
        }

        /// <summary>Ende einer Salve: kein Schuss seit recover_delay_s, mindestens 1,5 Schussabstände in der Salve (5.2 A, zweistufig).</summary>
        float RecoverDelay
        {
            get
            {
                var G = S.D.gameplay;
                return Mathf.Max(G.recover_delay_s, 1.5f * (G.Burst ? 60f / G.burst_rpm : 60f / rpm));   // je Klasse (0.22)
            }
        }

        void UpdateLive(float dt, EgoIntent i)
        {
            // Blitz und Hülsen altern vor den Schüssen dieses Bilds: ein neuer Schuss ist im selben Bild sichtbar
            _flashLeft = Mathf.Max(0, _flashLeft - dt);
            var Ej = S.D.motion.eject;
            for (int k = 0; k < _shOn.Length; k++)
                if (_shOn[k] && (_shAge[k] += dt) - Ej.delay_frames / (float)S.fps >= Ej.life_s) _shOn[k] = false;
            // Feuer mit fester Kadenz; eine angefangene Salve läuft zu Ende
            _triggerHeld = i.fire && CanFire;
            _sinceShot += dt;
            float interval = ShotInterval();
            if (S.D.gameplay.Semi)
            {
                // Einzelfeuer (0.20, Feuerart semi_auto): ein Schuss je Zug. Ein Zug vor Ablauf des Schussabstands (oder im Übergang aus dem
                // Sprint) wartet höchstens SemiQueueS und fällt dann, sobald geschossen werden darf; gehaltener Abzug schießt nicht nach.
                if (i.fire && !_semiPrev) _semiQueue = SemiQueueS;
                _semiPrev = i.fire;
                if (S.D.gameplay.HasPortals)
                {
                    // Werkzeug (0.22): je Taste ein Portal (gameplay.portals[].input: fire = Linksklick, aim = Rechtsklick); der jüngste Zug gilt
                    if (i.fire && !_portalPrevA) { _portalQueued = PortalIndex("fire"); _semiQueue = SemiQueueS; }
                    if (i.aim && !_portalPrevB) { _portalQueued = PortalIndex("aim"); _semiQueue = SemiQueueS; }
                    _portalPrevA = i.fire;
                    _portalPrevB = i.aim;
                }
                if (_semiQueue > 0 && CanFire && _sinceShot >= interval && HasAmmo)
                {
                    _semiQueue = 0;
                    FireOne();
                }
                _semiQueue = Mathf.Max(0, _semiQueue - dt);
                _shotClock = 0;
            }
            else if (_triggerHeld || (_burstLeft > 0 && CanFire))
            {
                _shotClock += dt;
                // erster Schuss sofort; Max statt Setzen behält im Dauerfeuer den Übertrag (sonst bei 30/s 3 Bilder = 600 statt 720/min)
                if (_sinceShot >= interval && _shotClock > 0) _shotClock = Mathf.Max(_shotClock, interval);
                while (_shotClock >= interval && HasAmmo)
                {
                    _shotClock -= interval;
                    FireOne();
                    interval = ShotInterval();
                }
            }
            else _shotClock = 0;

            // Rückstoß (ego.RECOIL): Modellkick und Kamera-Ruck als Federn (kritisch gedämpft: kein Unterschwingen), Hochziehen des
            // Modells klingt nach dem Feuern ab; die Grundbahn steigt in der Salve und kehrt danach kritisch gedämpft zurück (5.2 A)
            var Rc = S.D.motion.recoil;
            EgoSolver.SpringStep(ref _recX, ref _recV, Vector3.zero, 2 * Mathf.PI * Rc.freq_hz, Rc.zeta, dt);
            EgoSolver.SpringStep(ref _recCx, ref _recCv, Vector3.zero, 2 * Mathf.PI * Rc.cam_freq_hz, Rc.cam_zeta, dt);
            if (_sinceShot > interval * 1.5f) _rClimb *= Mathf.Exp(-dt * S.fps / 8f);
            bool salvo = _sinceShot <= RecoverDelay;
            if (!salvo)
            {
                _pathTgt = Vector3.zero;
                _pathN = 0;
            }
            EgoSolver.SpringStep(ref _path, ref _pathV, _pathTgt, 2 * Mathf.PI * (salvo ? Rc.path_hz : S.D.gameplay.recover_hz), 1f, dt);
            // Kamera-Ruck: in der Hüfte Kamera samt Viewmodel, im Zielen nur die Welt (das Visier bleibt stehen, 5.1 A)
            _worldPitch = _path.y + _recCx.x * Mathf.Lerp(1f, Rc.ads_cam, adsWeight);
            _worldYaw = _path.x;
            _boltT = Mathf.Max(0, _boltT - dt);
            if (_ringT < 1)                                 // Ringdrehung (Werkzeug): weich vom alten zum neuen Drittel in ring_turn_s
            {
                _ringT = Mathf.Min(1, _ringT + dt / Mathf.Max(1e-3f, S.D.gameplay.ring_turn_s));
                _ring = Mathf.Lerp(_ringFrom, _ringTgt, Smooth(_ringT));
            }

            // Pendeln aus der Mausbewegung: dieselbe Feder wie Feder-Nachlauf und Visier-Anflug (EgoSolver.SpringStep)
            Vector3 target = Vector2.ClampMagnitude(-i.look * tune.swayPerDeg, tune.swayMaxDeg) * Mathf.Lerp(1, tune.swayAds, adsWeight);
            int sub = Mathf.Max(1, Mathf.CeilToInt(dt / 0.004f));             // stabil auch bei 30 fps und Rucklern bis 50 ms
            EgoSolver.SpringStep(ref _sway, ref _swayV, target, 2 * Mathf.PI * tune.swayFreq, tune.swayDamp, dt, sub);
            _tilt = Mathf.Lerp(_tilt, -i.move.x * tune.moveTiltDeg * (1 - adsWeight), 1 - Mathf.Exp(-dt * 8));

            // Wippen aus der Laufgeschwindigkeit (walk / sprint), Atmen in Ruhe
            bool sprinting = _stance == Stance.Sprint && _t.A.name == "sprint" && _t.frame >= K("sprint", 1);
            float moveW = i.grounded ? Mathf.Clamp01(i.speed01) : 0;
            _bobW = Mathf.Lerp(_bobW, sprinting ? 0 : moveW, 1 - Mathf.Exp(-dt * 10));
            _sprintW = Mathf.Lerp(_sprintW, sprinting ? 1 : 0, 1 - Mathf.Exp(-dt * 10));
            float period = Mathf.Lerp(_walk.bob.period, _sprintA.bob.period, _sprintW);
            _bobPh += 2 * Mathf.PI * dt * S.fps / period * Mathf.Max(0.35f, Mathf.Max(moveW, _sprintW));
            _breatheW = Mathf.Lerp(_breatheW, (1 - moveW) * (sprinting ? 0 : 1), 1 - Mathf.Exp(-dt * 3));
            _breathePh += dt * S.fps;
            _dt = dt;
        }

        /// <summary>Index des Portals für eine Eingabe (fire, aim), −1 ohne.</summary>
        int PortalIndex(string input)
        {
            var P = S.D.gameplay.portals;
            for (int k = 0; k < P.Length; k++) if (P[k].input == input) return k;
            return -1;
        }

        static float Smooth(float t) => t * t * (3 - 2 * t);

        void FireOne()
        {
            if (!S.D.gameplay.Unlimited) ammo--;
            shots++;
            _sinceShot = 0;
            _boltT = tune.boltOpenS;
            _portOpen = true;
            var Rc = S.D.motion.recoil;
            float w = adsWeight;
            // Modellkick: im Zielen klein (Visier < 1 % H), ohne Hochziehen; Kamera-Ruck gleich, er wird erst beim Anwenden verteilt
            _recV += new Vector3(Rc.back_mps * Mathf.Lerp(1f, Rc.ads_back, w), Rc.pitch_dps * Mathf.Lerp(1f, Rc.ads_pitch, w), 0);
            _recCv += new Vector3(Rc.cam_dps, 0, 0);
            _rClimb += Rc.climb_deg * (1 - w);
            // Grundbahn: fester Schritt nach oben und feste Seitenfolge, als Anteil des Weltbilds (im Zielen kleinerer Winkel)
            float th = _tanH / Zoom, tv = th / aspect;
            _pathN++;
            _pathTgt.y += Mathf.Atan(S.D.gameplay.path_up_h * 2 * tv) * Mathf.Rad2Deg;   // Bahnstufe je Klasse (0.22)
            if (Rc.path_side_b != null && Rc.path_side_b.Length > 0)
                _pathTgt.x = Mathf.Atan(Rc.path_side_b[_pathN % Rc.path_side_b.Length] * 2 * th) * Mathf.Rad2Deg;
            if (S.D.gameplay.Burst) _burstLeft = _burstLeft > 0 ? _burstLeft - 1 : S.D.gameplay.burst_shots - 1;
            if (S.D.gameplay.muzzle_flash)
            {
                _flashLeft = S.D.motion.flash.dur_s;      // Mündungsfeuer nur aus einem echten Schuss (Munition, Kadenz, kein Nachladen)
                _flashShot = (int)(shots - 1);
            }
            LastPortal = -1;
            if (S.D.gameplay.HasPortals)                  // Werkzeug: Ring dreht je Schuss ein Drittel in Richtung des Portals
            {
                LastPortal = _portalQueued >= 0 ? _portalQueued : 0;
                _portalQueued = -1;
                if (Mathf.Abs(_ringTgt) >= 3) { float wrap = 3 * Mathf.Sign(_ringTgt); _ringTgt -= wrap; _ring -= wrap; }   // Drehung ist 3-periodisch
                _ringFrom = _ring;
                _ringTgt += S.D.gameplay.portals[LastPortal].ring;
                _ringT = 0;
            }
            if (S.Ejects) _pendingShells++;               // Hülse startet in Compose mit der Waffe dieses Bilds
            Shot?.Invoke();
        }

        Layers LiveLayers(Matrix4x4 R)
        {
            var L = Layers.None;
            // Atmen: dezent immer (ego.BREATHE_ALL), dazu die idle_hip-Formel in Ruhe, im Zielen gedämpft
            var Bz = S.D.motion.breathe_all;
            float phb = 2 * Mathf.PI * _breathePh / (Bz.period_s * S.fps);
            float bw = _breatheW * Mathf.Lerp(1, tune.breatheAds, adsWeight);
            L.pos.z += Bz.up_m * Mathf.Sin(phb) + 0.0015f * bw * Mathf.Sin(2 * Mathf.PI * _breathePh / 60);
            L.rot = RotX(Rad(-Bz.pitch_deg * Mathf.Sin(phb + 0.8f) - 0.25f * bw * Mathf.Sin(2 * Mathf.PI * _breathePh / 60 + 1)));
            // Wippen (liegende Acht) aus walk und sprint
            float bobK = Mathf.Lerp(1, tune.bobAds, adsWeight);
            float side = _walk.bob.amp[0] * _bobW + _sprintA.bob.amp[0] * _sprintW;
            float s2 = Mathf.Sin(2 * _bobPh), u2 = -Mathf.Cos(2 * _bobPh);           // liegende Acht bzw. U-Bogen je Aktion (Bob.u)
            float up = _walk.bob.amp[1] * _bobW * (_walk.bob.u ? u2 : s2) + _sprintA.bob.amp[1] * _sprintW * (_sprintA.bob.u ? u2 : s2);
            float rollW = _walk.bob.roll * _bobW + _sprintA.bob.roll * _sprintW;
            L.pos += new Vector3(side * Mathf.Sin(_bobPh), 0, up) * bobK;
            L.rot = L.rot * RotY(Rad(rollW * Mathf.Sin(_bobPh) * bobK + _tilt));
            // Pendeln: Gieren um die Hochachse der Waffe, Nicken um die Querachse, leichte Lageverschiebung
            L.rot = L.rot * RotZ(Rad(_sway.x)) * RotX(Rad(_sway.y));
            L.pos += new Vector3(-_sway.x, 0, _sway.y) * tune.swayPos;
            // Rückstoß
            L.pos += R.MultiplyVector(new Vector3(0, _recX.x, 0));
            L.rot = L.rot * RotX(Rad(-(_recX.y + _rClimb)));
            L.camPitch = _recCx.x * (1 - adsWeight);           // Viewmodel-Kamera: Ruck nur in der Hüfte (im Zielen nur die Welt)
            L.trigger = _triggerHeld ? 1 : 0;
            L.bolt = _boltT > 0 ? 1 : 0;
            L.port = _portOpen ? 1 : 0;
            if (S.D.gameplay.HasPortals) L.ring = _ring;
            return L;
        }

        // Weltzoom gegen Modell (1d): der Zoom beginnt, wenn der Augenpunkt AdsStart seines Wegs zur Kamera zurückgelegt hat, und ist
        // bei AdsEnd ganz da; dazwischen folgt er dem Modell. Destiny-Holo: Zoom beginnt 0–2 Bilder nach dem Modell, Ende ±1 Bild.
        // AdsEnd nah an 1: am Bild bewegen sich nahe Teile noch, wenn der Augenpunkt fast da ist (gemessen: Ende 0,99 → 3 Bilder zu früh)
        // AdsStart je Klasse (0.20, gameplay.zoom_start): der Scout bewegt den Augenpunkt anfangs mehr als die Waffe im Bild, mit 5 % begann
        // sein Zoom 2 Bilder vor dem Modell
        const float AdsStartDefault = 0.05f, AdsEnd = 0.9985f, LeaveGraceS = 0.1f, LeaveMaxS = 0.5f;
        float AdsStart => S.D.gameplay.zoom_start > 0 ? S.D.gameplay.zoom_start : AdsStartDefault;

        float Remap(float p) => Mathf.Clamp01((p - AdsStart) / (AdsEnd - AdsStart));

        /// <summary>Zielen-Anteil aus dem Weg des Augenpunkts (Socket_Eye nach dem Feder-Nachlauf, ohne Live-Ebenen) statt einer eigenen
        /// Zeitkurve: Hüfte/Sprint → Zielen über den Abstand beim Beginn, Zielen → Hüfte über den Hüftabstand; Sprünge (Abbruch mitten
        /// im Anflug) laufen über mindestens drei Bilder bei 30/s. Das Verlassen dauert höchstens LeaveMaxS (die Grenze greift erst nach
        /// LeaveGraceS, beim normalen aim_out nie): aus dem Zielen direkt ins
        /// Nachladen oder Betrachten liegt das Auge näher an der Kamera als in der Hüfte (Nachladen 0,37 statt 0,41 m), sonst bliebe Zoom.</summary>
        void FollowModel(Matrix4x4 baseW)
        {
            float d = baseW.MultiplyPoint3x4(_eyeLocal).magnitude;
            bool aiming = _stance == Stance.Ads || (_t.A.name == "draw_aim" && !_t.ended && _t.frame >= K("draw_aim", 1));
            if (aiming && !_aimPrev) _d0 = Mathf.Max(_dHip, d);
            if (!aiming && _aimPrev) { _leaving = true; _leaveT = 0; }
            _aimPrev = aiming;
            float target = 0;
            if (aiming) target = Mathf.Max(adsWeight, Remap(1 - d / _d0));
            else if (_leaving)
            {
                _leaveT += _dt;
                float cap = 1 - Mathf.Max(0, _leaveT - LeaveGraceS) / (LeaveMaxS - LeaveGraceS);   // greift erst nach LeaveGraceS
                target = Mathf.Min(Mathf.Min(adsWeight, Remap(1 - d / _dHip)), cap);
                if (target <= 0) _leaving = false;
            }
            adsWeight = Mathf.MoveTowards(adsWeight, target, _dt * 30f / 3f);
        }

        /// <summary>Blitz und Hülsen im laufenden Spiel (gleiche Formeln wie FxScripted): neue Hülsen starten mit der Waffe dieses Bilds und
        /// belegen den ältesten Platz des Pools; keine Speicheranforderung je Bild.</summary>
        void LiveFx(EgoOutput o, Matrix4x4 WM)
        {
            o.flashOn = _flashLeft > 1e-4f;
            if (o.flashOn) { o.flashShot = _flashShot; o.flash = S.FlashMatrix(WM, _flashShot); }
            for (; _pendingShells > 0; _pendingShells--)
            {
                _shW[_shNext] = WM;
                _shAge[_shNext] = 0;
                _shId[_shNext] = (int)(shots - _pendingShells);
                _shOn[_shNext] = true;
                _shNext = (_shNext + 1) % _shOn.Length;
                shellsEjected++;
            }
            var Ej = S.D.motion.eject;
            o.shellCount = 0;
            for (int k = 0; k < _shOn.Length; k++)
            {
                if (!_shOn[k]) continue;
                float t = _shAge[k] - Ej.delay_frames / (float)S.fps;
                if (t < 0) continue;
                o.shells[o.shellCount] = S.ShellMatrix(_shW[k], t);
                o.shellIds[o.shellCount++] = _shId[k];
            }
        }

        /// <summary>Feder-Nachlauf (ego.SECONDARY) in Echtzeit über alle Spuren hinweg: glättet auch Spurwechsel.</summary>
        Matrix4x4 SecondaryLive(Matrix4x4 target, bool aim)
        {
            var S2 = S.D.motion.secondary;
            float z = aim ? S2.aim_zeta : S2.zeta;            // im Zielen ankommen: kritisch gedämpft (kein Überschwingen am Visier)
            var qt = QuatFrom(target);
            if (!_hasSec)
            {
                _hasSec = true;
                _secP = Pos(target); _secV = Vector3.zero; _secQ = qt; _secAv = Vector3.zero;
                return target;
            }
            float w = 2 * Mathf.PI * (aim ? S2.aim_freq_hz : S2.freq_hz);
            EgoSolver.SpringStep(ref _secP, ref _secV, Pos(target), w, z, _dt);
            EgoSolver.SpringRot(ref _secQ, ref _secAv, qt, w, z, _dt);
            return Matrix4x4.TRS(_secP, _secQ, Vector3.one);
        }

        EgoOutput Compose()
        {
            var o = output;
            var A = _t.A;
            float f = _t.frame;
            var baseW = S.WeaponAt(A.weapon, f);
            float e = Ease(_fade);
            if (e < 1) baseW = Blend(_fromBase, baseW, e);
            _lastBase = baseW;
            baseW = _t.scripted ? S.Secondary(baseW, f, _t.st, A.EndsInAds) : SecondaryLive(baseW, A.EndsInAds);
            BaseWeapon = baseW;
            o.adsHidden = S.AdsHidden(baseW);           // Zielfernrohr (0.20): Okular, Rohr, Türme im Zielen aus
            FollowModel(baseW);
            var L = _t.scripted ? S.Scripted(A, f, Rot3(baseW), _t.st) : LiveLayers(Rot3(baseW));
            var WM = EgoSolver.Apply(baseW, L);
            S.MechAt(A, f, L, _mech);
            if (e < 1)
                foreach (var kv in _fromMech)
                {
                    _mech.TryGetValue(kv.Key, out float v);
                    _mech[kv.Key] = kv.Value + (v - kv.Value) * e;
                }
            S.SetWeapon(o, WM, _mech);
            var pf = _pf ?? (_pf = pid => S.PartFrame(output, pid));
            o.handL = S.BlendHand(A.L, f, pf);
            o.handR = S.BlendHand(A.R, f, pf);
            if (e < 1)
            {
                o.handL = Blend(WM * _fromRelL, o.handL, e);
                o.handR = Blend(WM * _fromRelR, o.handR, e);
            }
            S.Magazine(o, A, f, o.handL, _t.st);
            S.BlendFingers(A.fL, f, o.fingersL);
            S.BlendFingers(A.fR, f, o.fingersR);
            if (e < 1)
                for (int k = 0; k < 15; k++)
                {
                    o.fingersL[k] = _fromFL[k] + (o.fingersL[k] - _fromFL[k]) * e;
                    o.fingersR[k] = _fromFR[k] + (o.fingersR[k] - _fromFR[k]) * e;
                }
            o.wristBendMaxDeg = 0;
            o.overreach = 0;
            S.SolveArm(true, o.handR, o.fingersR, o.segR, o);
            S.SolveArm(false, o.handL, o.fingersL, o.segL, o);
            o.camPitch = L.camPitch;
            o.worldPitch = _t.scripted ? L.camPitch : _worldPitch;
            o.worldYaw = _t.scripted ? 0 : _worldYaw;
            if (_t.scripted) S.FxScripted(A, f, WM, _t.st, o);
            else LiveFx(o, WM);
            _hasOutput = true;
            return o;
        }
    }
}
