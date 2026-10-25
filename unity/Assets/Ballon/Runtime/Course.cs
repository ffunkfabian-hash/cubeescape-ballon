// Parcours-Logik (0.9): Auslösequader für Start, Kontrollpunkte (in Reihenfolge) und Ziel, Laufzeit, Treffer an den Zielscheiben,
// Bestzeit (PlayerPrefs), Anzeigetexte ohne Speicher je Bild, Wegmarken am Boden. Reine Logik ohne Szenenbezug: Tick() bekommt den
// Körpermittelpunkt des Spielers und die Zeit des Schritts; so lässt sich alles im EditMode prüfen.
using System;
using System.Collections.Generic;
using System.Globalization;
using UnityEngine;

namespace Ballon.Ego
{
    public sealed class CourseRun
    {
        public enum Phase { Bereit, Lauf, Ziel }

        public const float BodyCenter = 0.9f;     // Höhe des Prüfpunkts über den Füßen (Mitte des stehenden Spielers)

        readonly Bounds _start, _finish;
        readonly Bounds[] _cps;
        readonly string[] _cpNames;
        readonly IList<RangeTarget> _targets;
        readonly int[] _baseHits;
        readonly string _prefsKey;
        bool _primed, _inS, _inF;
        int _next, _warned = -1;
        string _message = "";
        // Anzeigetexte: nur bei Änderung neu gebaut
        string _stateText = "", _info = "", _finalTime = "";
        int _sigCp = -1, _sigHit = -1, _sigMsg = -1;
        float _sigBest = -1f;

        public Phase State { get; private set; }
        /// <summary>Zeit seit dem Start (läuft nur im Lauf; nach dem Ziel die Laufzeit).</summary>
        public float Elapsed { get; private set; }
        public int CheckpointCount => _cps.Length;
        public int CheckpointsDone => _next;
        public int TargetCount => _targets?.Count ?? 0;
        public float ParTime { get; }
        /// <summary>Bestzeit in Sekunden; 0 = noch keine.</summary>
        public float BestTime { get; private set; }
        /// <summary>true, wenn der letzte Lauf gültig im Ziel endete.</summary>
        public bool LastValid { get; private set; }
        public float LastTime { get; private set; }
        public bool LastWasBest { get; private set; }
        public int RunsFinished { get; private set; }
        /// <summary>Marker des letzten Ergebnisses (auch als Debug.Log); leer, solange keins vorliegt.</summary>
        public string LastMarker { get; private set; } = "";
        public string Message => _message;
        public string SceneName { get; }

        /// <summary>Wird bei jedem Ergebnis (gültig oder Ziel ohne alle Kontrollpunkte) gerufen.</summary>
        public event Action<string> Result;

        /// <param name="prefsKey">PlayerPrefs-Schlüssel der Bestzeit; null = nur im Speicher</param>
        public CourseRun(string sceneName, SceneCourse c, IList<RangeTarget> targets, string prefsKey)
        {
            SceneName = sceneName;
            _start = SceneConvert.Box(c.start);
            _finish = SceneConvert.Box(c.finish);
            _cps = new Bounds[c.checkpoints.Length];
            _cpNames = new string[_cps.Length];
            for (int i = 0; i < _cps.Length; i++) { _cps[i] = SceneConvert.Box(c.checkpoints[i]); _cpNames[i] = c.checkpoints[i].name; }
            _targets = targets;
            _baseHits = new int[targets?.Count ?? 0];
            ParTime = c.par_time_s;
            _prefsKey = prefsKey;
            Tenths();                                    // Zeittabelle jetzt bauen (beim Laden der Szene), nicht im ersten Lauf-Bild
            if (prefsKey != null) BestTime = PlayerPrefs.GetFloat(prefsKey, 0f);
            Reset();
        }

        public static string PrefsKey(string sceneName) => "Ballon.Best." + sceneName;

        /// <summary>Lauf verwerfen (Taste T, Szenenwechsel): zurück in „bereit“; der nächste Schritt merkt sich nur, wo der Spieler steht.</summary>
        public void Reset()
        {
            State = Phase.Bereit;
            Elapsed = 0f;
            _next = 0;
            _warned = -1;
            _message = "";
            _primed = false;
            LastValid = false;
            LastWasBest = false;
            _finalTime = "";
            for (int i = 0; i < _baseHits.Length; i++) _baseHits[i] = _targets[i].hits;
            Refresh();
        }

        /// <summary>Zielscheiben, die im aktuellen Lauf getroffen wurden (mindestens ein Treffer seit dem Start); vor dem Start 0.</summary>
        public int TargetsHit
        {
            get
            {
                if (State == Phase.Bereit) return 0;
                int n = 0;
                for (int i = 0; i < _baseHits.Length; i++) if (_targets[i].hits > _baseHits[i]) n++;
                return n;
            }
        }

        /// <summary>Ein Schritt: p = Körpermittelpunkt des Spielers (Unity-Welt), dt = Dauer des Schritts.</summary>
        public void Tick(Vector3 p, float dt)
        {
            bool inS = _start.Contains(p), inF = _finish.Contains(p);
            if (!_primed)                                   // erster Schritt nach Reset: nur den Stand merken (Spawn im Tor startet nichts)
            {
                _primed = true;
                _inS = inS;
                _inF = inF;
                Refresh();
                return;
            }
            bool enterS = inS && !_inS, enterF = inF && !_inF;
            _inS = inS;
            _inF = inF;
            if (State == Phase.Lauf)
            {
                Elapsed += dt;
                while (_next < _cps.Length && _cps[_next].Contains(p)) { _next++; _warned = -1; _message = ""; }
                if (_next < _cps.Length)                     // ein späterer Kontrollpunkt zuerst: Hinweis, keine Wertung
                    for (int j = _next + 1; j < _cps.Length; j++)
                        if (_cps[j].Contains(p) && _warned != j)
                        {
                            _warned = j;
                            _message = $"Kontrollpunkt {_next + 1} ({_cpNames[_next]}) fehlt";
                        }
            }
            if (State == Phase.Lauf && _next == _cps.Length && enterF) Finish();
            else if (enterS) StartRun();
            else if (State == Phase.Lauf && enterF) Reject();
            Refresh();
        }

        void StartRun()
        {
            State = Phase.Lauf;
            Elapsed = 0f;
            _next = 0;
            _warned = -1;
            _message = "";
            LastValid = false;
            LastWasBest = false;
            for (int i = 0; i < _baseHits.Length; i++) _baseHits[i] = _targets[i].hits;
        }

        void Finish()
        {
            State = Phase.Ziel;
            LastValid = true;
            LastTime = Elapsed;
            RunsFinished++;
            LastWasBest = BestTime <= 0f || Elapsed < BestTime;
            if (LastWasBest)
            {
                BestTime = Elapsed;
                if (_prefsKey != null) { PlayerPrefs.SetFloat(_prefsKey, BestTime); PlayerPrefs.Save(); }
            }
            _finalTime = TimeText(Elapsed, true);
            _message = LastWasBest ? "Neue Bestzeit" : "";
            Emit(string.Format(CultureInfo.InvariantCulture, "[Ballon] Lauf: gültig szene={0} zeit={1:0.000} kontrollpunkte={2}/{3} treffer={4}/{5} richtzeit={6:0.0} bestzeit={7:0.000} neue_bestzeit={8}",
                 SceneName, Elapsed, _next, _cps.Length, TargetsHit, TargetCount, ParTime, BestTime, LastWasBest ? "ja" : "nein"));
        }

        void Reject()
        {
            _message = $"Ziel nicht gewertet: Kontrollpunkt {_next + 1} ({_cpNames[_next]}) fehlt";
            Emit(string.Format(CultureInfo.InvariantCulture, "[Ballon] Lauf: ungültig szene={0} kontrollpunkte={1}/{2} treffer={3}/{4}",
                 SceneName, _next, _cps.Length, TargetsHit, TargetCount));
        }

        void Emit(string marker)
        {
            LastMarker = marker;
            Debug.Log(marker);
            Result?.Invoke(marker);
        }

        // ------------------------------------------------------------------------------------------------ Anzeige (ohne GC je Bild)
        // Zeit in Zehntelsekunden aus einer Tabelle (einmal gebaut), alles andere nur bei geänderten Werten.
        static string[] _tenths;
        const int TenthsMax = 15 * 60 * 10;          // 15 min

        static string[] Tenths()
        {
            if (_tenths != null) return _tenths;
            var t = new string[TenthsMax + 1];
            for (int i = 0; i < t.Length; i++)
            {
                int m = i / 600;
                float s = (i % 600) / 10f;
                t[i] = m > 0 ? string.Format(CultureInfo.InvariantCulture, "{0}:{1:00.0}", m, s) : string.Format(CultureInfo.InvariantCulture, "{0:0.0} s", s);
            }
            t[TenthsMax] = "15:00+";
            return _tenths = t;
        }

        /// <summary>Zeit als Text; `exact` mit Hundertstel. Allokiert: nur für Ergebnis und Bestzeit gedacht, nicht je Bild.</summary>
        public static string TimeText(float seconds, bool exact)
        {
            var inv = CultureInfo.InvariantCulture;
            int m = (int)(seconds / 60f);
            float s = seconds - m * 60f;
            return m > 0 ? m.ToString(inv) + ":" + s.ToString(exact ? "00.00" : "00.0", inv) : s.ToString(exact ? "0.00" : "0.0", inv) + " s";
        }

        /// <summary>Große Zeitanzeige: im Lauf Zehntel (Tabelle, kein GC), nach dem Ziel die genaue Zeit, sonst leer.</summary>
        public string TimeLabel
        {
            get
            {
                if (State == Phase.Lauf) return Tenths()[Mathf.Min((int)(Elapsed * 10f), TenthsMax)];
                return State == Phase.Ziel && LastValid ? _finalTime : "";
            }
        }

        /// <summary>Zustand in Worten („Lauf“, „Ziel“, „Start durchlaufen“).</summary>
        public string StateText => _stateText;
        /// <summary>Kontrollpunkte, Treffer, Richtzeit, Bestzeit und Hinweis in einer Zeile.</summary>
        public string InfoText => _info;

        void Refresh()
        {
            string st = State == Phase.Lauf ? "Lauf" : State == Phase.Ziel ? (LastValid ? "Ziel erreicht" : "Ziel") : "Start durchlaufen, um zu beginnen";
            _stateText = st;
            int cp = _next, hit = TargetsHit, msg = _message.Length == 0 ? 0 : _message.GetHashCode();
            if (cp == _sigCp && hit == _sigHit && msg == _sigMsg && Mathf.Approximately(BestTime, _sigBest) && _info.Length > 0) return;
            _sigCp = cp; _sigHit = hit; _sigMsg = msg; _sigBest = BestTime;
            var inv = CultureInfo.InvariantCulture;
            string par = ParTime > 0f ? string.Format(inv, "   Richtzeit {0}", TimeText(ParTime, false)) : "";
            string best = BestTime > 0f ? string.Format(inv, "   Bestzeit {0}", TimeText(BestTime, true)) : "   Bestzeit –";
            _info = string.Format(inv, "Kontrollpunkte {0}/{1}   Ziele {2}/{3}{4}{5}{6}", cp, _cps.Length, hit, TargetCount, par, best,
                _message.Length > 0 ? "   · " + _message : "");
        }
    }

    /// <summary>Wegmarken am Boden entlang der Strecke: flache Pfeile aus Unlit-Dreiecken in einem Netz.</summary>
    public static class RouteMarkers
    {
        public const float Spacing = 1.5f;        // Abstand der Pfeile entlang der Strecke (m)
        public const float Lift = 0.03f;          // über dem Boden, gegen Z-Fighting

        /// <summary>Anzahl der Pfeile für diese Strecke (Unity-Punkte).</summary>
        public static int Count(IList<Vector3> route)
        {
            int n = 0;
            for (int i = 0; i + 1 < route.Count; i++) n += Mathf.Max(1, Mathf.FloorToInt((route[i + 1] - route[i]).magnitude / Spacing));
            return n;
        }

        public static Mesh BuildMesh(IList<Vector3> route)
        {
            var v = new List<Vector3>();
            var tri = new List<int>();
            for (int i = 0; i + 1 < route.Count; i++)
            {
                var a = route[i];
                var d = route[i + 1] - a;
                float len = d.magnitude;
                if (len < 1e-3f) continue;
                var dir = d / len;
                int n = Mathf.Max(1, Mathf.FloorToInt(len / Spacing));
                for (int k = 0; k < n; k++)
                {
                    var c = a + dir * ((k + 0.5f) * len / n);
                    var flat = new Vector3(dir.x, 0, dir.z);
                    flat = flat.sqrMagnitude < 1e-6f ? Vector3.forward : flat.normalized;
                    var side = Vector3.Cross(Vector3.up, flat);
                    c.y += Lift;
                    // Pfeilspitze (Dreieck, 0,5 m lang, 0,5 m breit) mit Schaft (0,12 m breit) dahinter
                    int b0 = v.Count;
                    v.Add(c + flat * 0.25f);
                    v.Add(c - flat * 0.05f + side * 0.25f);
                    v.Add(c - flat * 0.05f - side * 0.25f);
                    v.Add(c - flat * 0.05f + side * 0.06f);
                    v.Add(c - flat * 0.05f - side * 0.06f);
                    v.Add(c - flat * 0.3f + side * 0.06f);
                    v.Add(c - flat * 0.3f - side * 0.06f);
                    // im Uhrzeigersinn von oben gesehen: Normalen zeigen nach oben (Unlit schneidet Rückseiten)
                    tri.AddRange(new[] { b0, b0 + 1, b0 + 2, b0 + 4, b0 + 3, b0 + 5, b0 + 4, b0 + 5, b0 + 6 });
                }
            }
            var m = new Mesh { name = "Wegmarken" };
            m.SetVertices(v);
            m.SetTriangles(tri, 0);
            m.RecalculateNormals();
            m.RecalculateBounds();
            return m;
        }
    }
}
