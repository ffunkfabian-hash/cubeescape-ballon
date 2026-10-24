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
        public bool reload, inspect, draw, holster;     // gedrückt in diesem Bild
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
        public float kickHip = 1.0f, kickAds = 0.45f;   // fire_hip.kick / fire_ads.kick
        public float swayPerDeg = 0.35f, swayMaxDeg = 3.0f, swayFreq = 9f, swayDamp = 0.55f, swayPos = 0.0035f;
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
        }

        public readonly EgoSolver S;
        public readonly EgoTuning tune;
        public readonly EgoOutput output;
        public event Action<string, string> Marker;     // (Aktion, Marker)
        public event Action Shot;

        public int ammo, magSize;
        public float rpm;
        public bool holstered = true;
        public float adsWeight;            // 0 Hüfte … 1 Zielen (für FOV, Empfindlichkeit, Streuung)
        public long shots;

        Track _t;
        Stance _stance = Stance.Hip;
        bool _fireArmed;                   // Feuer nach sprint_to_fire erst ab Marker „Fire“
        float _shotClock, _boltT, _sinceShot = 99f;
        bool _portOpen, _triggerHeld;
        Vector3 _recX, _recV, _recCx, _recCv;
        float _rClimb, _dt = 1f / 30f;
        bool _hasSec;
        Vector3 _secP, _secV, _secAv;
        Quaternion _secQ;
        Vector2 _sway, _swayV;
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

        public EgoController(EgoSolver s, EgoTuning tuning = null)
        {
            S = s;
            tune = tuning ?? new EgoTuning();
            output = s.NewOutput();
            magSize = ammo = s.D.gameplay.magazine;
            rpm = s.D.gameplay.rpm;
            _walk = s.D.Action("walk");
            _sprintA = s.D.Action("sprint");
            Hold("holster", Stance.Hip);
        }

        public string ActionName => _t.A.name;
        public float Frame => _t.frame;
        public bool Busy => _t.busy && !_t.ended;
        public Stance CurrentStance => _stance;
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
            _t = new Track { A = A, frame = from, end = to < 0 ? A.frames : to, dir = dir, busy = busy, stance = stance, onEnd = onEnd,
                             scripted = scripted };
            if (dir > 0) Emit(from - 0.001f, from);
            return _t;
        }

        void Hold(string name, Stance st, float at = -1)
        {
            var A = S.D.Action(name);
            _t = new Track { A = A, frame = at < 0 ? A.frames : at, end = at < 0 ? A.frames : at, ended = true, stance = st };
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
            if (_t.A.weapon[_t.A.weapon.Length - 1].pose == "ads")      // draw_aim, sprint_to_aim: im Zielen ankommen
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
            if (i.aim) EnterStance(Stance.Ads, i);
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
                    else Play("aim_in", stance: Stance.Ads);
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
                        else r = Play("aim_out", stance: Stance.Hip);
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
                    r.onEnd = _ => Ready();
                    break;
            }
            _stance = target;
        }

        /// <summary>Bild des Waffenschlüssels i einer Aktion (Haltung erreicht/gehalten; nach TIME_SCALE gestreckt).</summary>
        float K(string action, int i) => S.D.Action(action).weapon[i].f;

        Stance Wanted(EgoIntent i)
        {
            if (i.sprint && i.move.y > 0.3f && i.grounded && !i.aim && !i.fire) return Stance.Sprint;
            if (i.aim) return Stance.Ads;
            if (!i.grounded) return Stance.Air;
            if (i.nearWall && !i.fire) return Stance.Lowered;
            if (i.crouch) return Stance.Crouch;
            return Stance.Hip;
        }

        void Cancel(EgoIntent i)
        {
            Play("idle_hip", 0, 0, fade: tune.cancelFadeFrames, onEnd: _ => Ready());
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
                if (i.draw && _t.ended && _t.A.name != "draw")
                    Play(i.aim ? "draw_aim" : "draw", busy: true, fade: 0, onEnd: _ => Ready());
            }
            else if (i.holster && _t.A.name != "holster" && _t.A.name != "reload_to_switch")
            {
                Play(reloading ? "reload_to_switch" : "holster", busy: true, onEnd: _ => holstered = true,
                     fade: reloading ? 3 : -1);
                holstered = false;
            }
            else if (inspecting && (i.fire || i.aim || i.reload || (i.sprint && i.move.y > 0.3f)))
                Cancel(i);
            else if (!Busy)
            {
                if (i.reload && ammo < magSize)
                    StartReload(i);
                else if (i.fire && !_firePrev && ammo == 0 && !reloading)     // Abzug bei leerem Magazin: selbst nachladen
                    StartReload(i);
                else if (i.inspect && _stance != Stance.Sprint)
                    Play("inspect", busy: true, fade: 2, onEnd: _ => Ready());
                else if (_stance == Stance.Sprint && i.fire)
                {
                    _fireArmed = false;
                    Play("sprint_to_fire", stance: Stance.Hip, onEnd: _ => Ready());
                    _stance = Stance.Hip;
                }
                else if (_t.stance.HasValue || _t.ended)
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

        void StartReload(EgoIntent i)
        {
            _stance = Stance.Hip;
            Play(ammo == 0 ? "reload_empty" : "reload_tactical", busy: true, fade: 3, onEnd: _ => Ready());
        }

        bool CanFire => !holstered && !Busy && ammo > 0 && (_t.A.name != "sprint_to_fire" || _fireArmed) && _stance != Stance.Sprint
                        && !(_t.A.name == "sprint" && _t.frame < K("sprint", 2)) && _t.A.name != "draw" && _t.A.name != "holster";

        void UpdateLive(float dt, EgoIntent i)
        {
            // Zielen-Anteil (aim_in 9 Bilder)
            float adsTarget = (_stance == Stance.Ads && (_t.A.name != "sprint_to_aim" || _t.frame >= K("sprint_to_aim", 1) * 0.5f)) ? 1 : 0;
            adsWeight = Mathf.MoveTowards(adsWeight, adsTarget, dt * S.fps / K("aim_in", 1));

            // Feuer mit fester Kadenz
            _triggerHeld = i.fire && CanFire;
            _sinceShot += dt;
            float interval = 60f / rpm;
            if (_triggerHeld)
            {
                _shotClock += dt;
                if (_sinceShot >= interval && _shotClock > 0) _shotClock = interval;   // erster Schuss sofort
                while (_shotClock >= interval && ammo > 0)
                {
                    _shotClock -= interval;
                    FireOne();
                }
            }
            else _shotClock = 0;

            // Rückstoß: Impuls je Schuss in gedämpfte Federn (ego.RECOIL), Kamera getrennt; Hochziehen klingt nach dem Feuern ab
            var Rc = S.D.motion.recoil;
            EgoSolver.SpringStep(ref _recX, ref _recV, Vector3.zero, 2 * Mathf.PI * Rc.freq_hz, Rc.zeta, dt);
            EgoSolver.SpringStep(ref _recCx, ref _recCv, Vector3.zero, 2 * Mathf.PI * Rc.cam_freq_hz, Rc.cam_zeta, dt);
            if (_sinceShot > interval * 1.5f) _rClimb *= Mathf.Exp(-dt * S.fps / 8f);
            _boltT = Mathf.Max(0, _boltT - dt);

            // Pendeln aus der Mausbewegung (gedämpfte Feder)
            var target = Vector2.ClampMagnitude(-i.look * tune.swayPerDeg, tune.swayMaxDeg) * Mathf.Lerp(1, tune.swayAds, adsWeight);
            float w = 2 * Mathf.PI * tune.swayFreq, z = tune.swayDamp;
            int sub = Mathf.Max(1, Mathf.CeilToInt(dt / 0.004f));             // stabil auch bei 30 fps und Rucklern bis 50 ms
            for (int k = 0; k < sub; k++)
            {
                var acc = (target - _sway) * (w * w) - _swayV * (2 * z * w);
                _swayV += acc * (dt / sub);
                _sway += _swayV * (dt / sub);
            }
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

        void FireOne()
        {
            ammo--;
            shots++;
            _sinceShot = 0;
            _boltT = tune.boltOpenS;
            _portOpen = true;
            float k = Mathf.Lerp(tune.kickHip, tune.kickAds, adsWeight);
            var Rc = S.D.motion.recoil;
            _recV += new Vector3(Rc.back_mps * k, Rc.pitch_dps * k, 0);
            _recCv += new Vector3(Rc.cam_dps * k, 0, 0);
            _rClimb += Rc.climb_deg * k;
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
            var ampW = new Vector2(_walk.bob.amp[0], _walk.bob.amp[1]) * _bobW + new Vector2(_sprintA.bob.amp[0], _sprintA.bob.amp[1]) * _sprintW;
            float rollW = _walk.bob.roll * _bobW + _sprintA.bob.roll * _sprintW;
            L.pos += new Vector3(ampW.x * Mathf.Sin(_bobPh), 0, ampW.y * Mathf.Sin(2 * _bobPh)) * bobK;
            L.rot = L.rot * RotY(Rad(rollW * Mathf.Sin(_bobPh) * bobK + _tilt));
            // Pendeln: Gieren um die Hochachse der Waffe, Nicken um die Querachse, leichte Lageverschiebung
            L.rot = L.rot * RotZ(Rad(_sway.x)) * RotX(Rad(_sway.y));
            L.pos += new Vector3(-_sway.x, 0, _sway.y) * tune.swayPos;
            // Rückstoß
            L.pos += R.MultiplyVector(new Vector3(0, _recX.x, 0));
            L.rot = L.rot * RotX(Rad(-(_recX.y + _rClimb)));
            L.camPitch = _recCx.x;
            L.trigger = _triggerHeld ? 1 : 0;
            L.bolt = _boltT > 0 ? 1 : 0;
            L.port = _portOpen ? 1 : 0;
            return L;
        }

        /// <summary>Feder-Nachlauf (ego.SECONDARY) in Echtzeit über alle Spuren hinweg: glättet auch Spurwechsel.</summary>
        Matrix4x4 SecondaryLive(Matrix4x4 target)
        {
            var S2 = S.D.motion.secondary;
            var qt = QuatFrom(target);
            if (!_hasSec)
            {
                _hasSec = true;
                _secP = Pos(target); _secV = Vector3.zero; _secQ = qt; _secAv = Vector3.zero;
                return target;
            }
            float w = 2 * Mathf.PI * S2.freq_hz;
            EgoSolver.SpringStep(ref _secP, ref _secV, Pos(target), w, S2.zeta, _dt);
            EgoSolver.SpringRot(ref _secQ, ref _secAv, qt, w, S2.zeta, _dt);
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
            baseW = _t.scripted ? S.Secondary(baseW, f, _t.st) : SecondaryLive(baseW);
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
            _hasOutput = true;
            return o;
        }
    }
}
