// EditMode: Parcours-Logik (CourseRun) ohne Szene: Start, Kontrollpunkte in Reihenfolge, Ziel, Zeit, Neustart, Zielscheiben-Treffer,
// Bestzeit, Anzeigetexte ohne Speicher je Bild und die Wegmarken.
using System.Collections.Generic;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools.Constraints;
using Is = UnityEngine.TestTools.Constraints.Is;   // NUnit-Is plus AllocatingGCMemory

namespace Ballon.Ego.Tests
{
    public class CourseTests
    {
        const string Fixture = "Assets/Ballon/Tests/EditMode/scene_fixture_v2.json";
        const float Dt = 0.5f;
        const string Key = "Ballon.Test.CourseTests";

        SceneCourse _c;
        readonly List<GameObject> _gos = new List<GameObject>();
        List<RangeTarget> _targets;
        CourseRun _run;
        Vector3 _spawn, _start, _cp1, _cp2, _finish, _off;
        readonly List<string> _markers = new List<string>();

        [SetUp]
        public void SetUp()
        {
            PlayerPrefs.DeleteKey(Key);
            _c = SceneFile.Parse(System.IO.File.ReadAllText(Fixture)).course;
            _targets = new List<RangeTarget>();
            for (int i = 0; i < 3; i++)
            {
                var g = new GameObject("Ziel " + i);
                _gos.Add(g);
                _targets.Add(g.AddComponent<RangeTarget>());
            }
            _run = new CourseRun("testkurs", _c, _targets, null);
            _markers.Clear();
            _run.Result += _markers.Add;
            _start = SceneConvert.Box(_c.start).center;
            _finish = SceneConvert.Box(_c.finish).center;
            _cp1 = SceneConvert.Box(_c.checkpoints[0]).center;
            _cp2 = SceneConvert.Box(_c.checkpoints[1]).center;
            _spawn = new Vector3(0, CourseRun.BodyCenter, -20);       // vor dem Start, in keinem Tor
            _off = new Vector3(0, CourseRun.BodyCenter, 0);           // Mitte der Halle, in keinem Tor
            Assert.IsFalse(SceneConvert.Box(_c.start).Contains(_spawn) || SceneConvert.Box(_c.finish).Contains(_off), "Fixture: Spawn und Mitte in keinem Tor");
        }

        [TearDown]
        public void TearDown()
        {
            foreach (var g in _gos) Object.DestroyImmediate(g);
            _gos.Clear();
            PlayerPrefs.DeleteKey(Key);
        }

        void At(Vector3 p, int ticks = 1) { for (int i = 0; i < ticks; i++) _run.Tick(p, Dt); }

        /// <summary>Spieler am Spawn (merkt sich den Stand), dann durch den Start.</summary>
        void BeginRun()
        {
            At(_spawn);
            At(_start);
        }

        [Test]
        public void Gueltiger_Lauf_zaehlt_Zeit_Kontrollpunkte_und_Treffer()
        {
            At(_spawn, 2);
            Assert.AreEqual(CourseRun.Phase.Bereit, _run.State, "vor dem Start läuft keine Zeit");
            Assert.AreEqual(0f, _run.Elapsed);
            At(_start);
            Assert.AreEqual(CourseRun.Phase.Lauf, _run.State);
            Assert.AreEqual(0f, _run.Elapsed, "der Start-Schritt selbst zählt nicht");
            At(_off, 3);                                  // 1,5 s unterwegs
            Assert.AreEqual(1.5f, _run.Elapsed, 1e-5f);
            _targets[0].Hit(Vector3.zero);
            _targets[0].Hit(Vector3.zero);                // zweiter Treffer an derselben Scheibe zählt nicht doppelt
            _targets[2].Hit(Vector3.zero);
            At(_cp1);                                     // +0,5 s
            Assert.AreEqual(1, _run.CheckpointsDone);
            At(_off);
            At(_cp2);
            Assert.AreEqual(2, _run.CheckpointsDone);
            Assert.AreEqual(CourseRun.Phase.Lauf, _run.State, "Ziel noch nicht erreicht");
            At(_finish);                                  // Elapsed: 1,5 + 4 × 0,5 = 3,5 s
            Assert.AreEqual(CourseRun.Phase.Ziel, _run.State);
            Assert.IsTrue(_run.LastValid);
            Assert.AreEqual(3.5f, _run.LastTime, 1e-5f);
            Assert.AreEqual(3.5f, _run.Elapsed, 1e-5f);
            Assert.AreEqual(2, _run.TargetsHit);
            Assert.AreEqual(3, _run.TargetCount);
            Assert.AreEqual(3.5f, _run.BestTime, 1e-5f, "erste Zeit ist die Bestzeit");
            Assert.IsTrue(_run.LastWasBest);
            Assert.AreEqual(1, _markers.Count, "ein Ergebnis-Marker");
            StringAssert.StartsWith("[Ballon] Lauf: gültig", _markers[0]);
            StringAssert.Contains("szene=testkurs", _markers[0]);
            StringAssert.Contains("zeit=3.500", _markers[0]);
            StringAssert.Contains("kontrollpunkte=2/2", _markers[0]);
            StringAssert.Contains("treffer=2/3", _markers[0]);
            StringAssert.Contains("richtzeit=45.0", _markers[0]);
            Assert.AreEqual(_markers[0], _run.LastMarker);
            // nach dem Ziel steht die Zeit still
            At(_off, 4);
            Assert.AreEqual(3.5f, _run.Elapsed, 1e-5f);
            Assert.AreEqual("3.50 s", _run.TimeLabel);
        }

        [Test]
        public void Falsche_Reihenfolge_ergibt_keine_Zeit()
        {
            BeginRun();
            At(_cp2);                                     // zweiter Kontrollpunkt vor dem ersten: keine Wertung, Hinweis
            Assert.AreEqual(0, _run.CheckpointsDone);
            StringAssert.Contains("Links", _run.Message, "nennt den fehlenden Kontrollpunkt");
            At(_off);
            At(_finish);                                  // Ziel ohne Kontrollpunkte
            Assert.AreEqual(CourseRun.Phase.Lauf, _run.State, "ohne alle Kontrollpunkte endet der Lauf nicht");
            Assert.IsFalse(_run.LastValid);
            Assert.AreEqual(0f, _run.BestTime, "keine Zeit gewertet");
            Assert.AreEqual(1, _markers.Count);
            StringAssert.StartsWith("[Ballon] Lauf: ungültig", _markers[0]);
            StringAssert.Contains("kontrollpunkte=0/2", _markers[0]);
            // erster, dann zweiter, dann Ziel: jetzt gültig (der Lauf war nicht beendet)
            At(_cp1);
            At(_off);
            At(_cp2);
            At(_off);
            At(_finish);
            Assert.AreEqual(CourseRun.Phase.Ziel, _run.State);
            Assert.IsTrue(_run.LastValid);
            Assert.AreEqual(2, _markers.Count);
        }

        [Test]
        public void Nur_ein_Kontrollpunkt_reicht_nicht()
        {
            BeginRun();
            At(_cp1);
            At(_off);
            At(_finish);
            Assert.IsFalse(_run.LastValid);
            Assert.AreEqual(1, _run.CheckpointsDone);
            StringAssert.Contains("Rechts hinten", _run.Message);
        }

        [Test]
        public void Erneutes_Durchschreiten_des_Starts_startet_neu()
        {
            BeginRun();
            _targets[1].Hit(Vector3.zero);
            At(_cp1);
            At(_off, 2);
            Assert.AreEqual(1, _run.CheckpointsDone);
            Assert.AreEqual(1, _run.TargetsHit);
            At(_spawn);                                   // Start verlassen …
            At(_start);                                   // … und wieder betreten
            Assert.AreEqual(CourseRun.Phase.Lauf, _run.State);
            Assert.AreEqual(0, _run.CheckpointsDone, "Kontrollpunkte zurückgesetzt");
            Assert.AreEqual(0f, _run.Elapsed, "Zeit neu");
            Assert.AreEqual(0, _run.TargetsHit, "Treffer des alten Laufs zählen nicht mehr");
            _targets[1].Hit(Vector3.zero);
            Assert.AreEqual(1, _run.TargetsHit);
            At(_start, 3);                                // im Tor stehenbleiben startet nicht erneut
            Assert.AreEqual(1.5f, _run.Elapsed, 1e-5f);
        }

        [Test]
        public void Nach_dem_Ziel_beginnt_ein_neuer_Lauf_am_Start()
        {
            BeginRun();
            At(_cp1);
            At(_cp2);
            At(_finish);
            Assert.AreEqual(CourseRun.Phase.Ziel, _run.State);
            At(_off);
            At(_start);
            Assert.AreEqual(CourseRun.Phase.Lauf, _run.State);
            Assert.AreEqual(0, _run.CheckpointsDone);
        }

        [Test]
        public void Spawn_im_Startquader_startet_nichts_und_Reset_verwirft_den_Lauf()
        {
            At(_start, 3);                                // erster Schritt merkt sich nur, wo der Spieler steht
            Assert.AreEqual(CourseRun.Phase.Bereit, _run.State);
            At(_off);
            At(_start);
            Assert.AreEqual(CourseRun.Phase.Lauf, _run.State, "aus dem Tor und wieder hinein startet");
            At(_cp1);
            _run.Reset();                                 // Taste T
            Assert.AreEqual(CourseRun.Phase.Bereit, _run.State);
            Assert.AreEqual(0, _run.CheckpointsDone);
            Assert.AreEqual(0f, _run.Elapsed);
            Assert.AreEqual("", _run.TimeLabel);
            At(_start, 2);                                // nach Reset gilt der erste Schritt wieder nur als Stand
            Assert.AreEqual(CourseRun.Phase.Bereit, _run.State);
        }

        [Test]
        public void Treffer_vor_dem_Start_zaehlen_nicht()
        {
            _targets[0].Hit(Vector3.zero);
            BeginRun();
            Assert.AreEqual(0, _run.TargetsHit);
            _targets[0].Hit(Vector3.zero);
            Assert.AreEqual(1, _run.TargetsHit);
        }

        [Test]
        public void Bestzeit_nur_wenn_besser_und_in_PlayerPrefs()
        {
            var run = new CourseRun("testkurs", _c, _targets, Key);
            Assert.AreEqual(0f, run.BestTime);
            void Lap(int idleTicks)
            {
                run.Tick(_spawn, Dt);
                run.Tick(_start, Dt);
                for (int i = 0; i < idleTicks; i++) run.Tick(_off, Dt);
                run.Tick(_cp1, Dt);
                run.Tick(_cp2, Dt);
                run.Tick(_finish, Dt);
                run.Tick(_spawn, Dt);
            }
            Lap(4);                                       // 4 × 0,5 + 3 × 0,5 = 3,5 s
            Assert.AreEqual(3.5f, run.BestTime, 1e-5f);
            Assert.AreEqual(3.5f, PlayerPrefs.GetFloat(Key), 1e-5f);
            Lap(8);                                       // langsamer: Bestzeit bleibt
            Assert.AreEqual(5.5f, run.LastTime, 1e-5f);
            Assert.IsFalse(run.LastWasBest);
            Assert.AreEqual(3.5f, run.BestTime, 1e-5f);
            Lap(0);                                       // schneller: 1,5 s
            Assert.AreEqual(1.5f, run.BestTime, 1e-5f);
            Assert.IsTrue(run.LastWasBest);
            StringAssert.Contains("Bestzeit 1.50 s", run.InfoText);
            StringAssert.Contains("Richtzeit 45.0 s", run.InfoText);
            // neue Sitzung liest die Bestzeit
            Assert.AreEqual(1.5f, new CourseRun("testkurs", _c, _targets, Key).BestTime, 1e-5f);
            Assert.AreEqual(3, run.RunsFinished);
        }

        [Test]
        public void Anzeige_Zeit_aus_Tabelle_und_Info_nur_bei_Aenderung()
        {
            Assert.AreEqual("", _run.TimeLabel, "vor dem Start keine Zeit");
            StringAssert.Contains("Start durchlaufen", _run.StateText);
            StringAssert.Contains("Kontrollpunkte 0/2", _run.InfoText);
            StringAssert.Contains("Ziele 0/3", _run.InfoText);
            StringAssert.Contains("Bestzeit –", _run.InfoText);
            BeginRun();
            At(_off, 5);                                  // 2,5 s
            Assert.AreEqual("2.5 s", _run.TimeLabel);
            Assert.AreEqual("Lauf", _run.StateText);
            At(_off, 200);                                // 102,5 s
            Assert.AreEqual("1:42.5", _run.TimeLabel);
            Assert.AreEqual("1:05.50", CourseRun.TimeText(65.5f, true));
            Assert.AreEqual("7.2 s", CourseRun.TimeText(7.24f, false));
            // Zeit, Zustand und Info allokieren im laufenden Lauf nicht
            At(_off);
            string t0 = _run.TimeLabel, i0 = _run.InfoText;
            NUnit.Framework.Assert.That(() =>
            {
                for (int k = 0; k < 300; k++)
                {
                    _run.Tick(k % 2 == 0 ? _off : _spawn, 0.016f);
                    var a = _run.TimeLabel; var b = _run.StateText; var c = _run.InfoText;
                }
            }, Is.Not.AllocatingGCMemory(), "Tick und Anzeigetexte im Lauf");
            Assert.AreSame(i0, _run.InfoText, "Info unverändert, gleiche Zeichenkette");
            Assert.AreNotEqual(t0, _run.TimeLabel);
        }

        [Test]
        public void Wegmarken_Pfeile_liegen_flach_nach_oben_entlang_der_Strecke()
        {
            var pts = new List<Vector3>();
            foreach (var r in _c.route) pts.Add(SceneConvert.Point(r));
            int n = RouteMarkers.Count(pts);
            float len = 0;
            for (int i = 0; i + 1 < pts.Count; i++) len += (pts[i + 1] - pts[i]).magnitude;
            Assert.That(n, Is.InRange(Mathf.FloorToInt(len / RouteMarkers.Spacing) - pts.Count, Mathf.CeilToInt(len / RouteMarkers.Spacing) + pts.Count), "Pfeile etwa alle 1,5 m");
            var m = RouteMarkers.BuildMesh(pts);
            try
            {
                Assert.AreEqual(n * 7, m.vertexCount, "7 Punkte je Pfeil");
                Assert.AreEqual(n * 9, m.triangles.Length, "3 Dreiecke je Pfeil");
                foreach (var v in m.vertices) Assert.That(v.y, Is.EqualTo(RouteMarkers.Lift).Within(1e-4f), "knapp über dem Boden");
                var tri = m.triangles;
                var vs = m.vertices;
                for (int i = 0; i < tri.Length; i += 3)
                {
                    var nrm = Vector3.Cross(vs[tri[i + 1]] - vs[tri[i]], vs[tri[i + 2]] - vs[tri[i]]);
                    Assert.Greater(nrm.y, 0f, "Vorderseite zeigt nach oben (Dreieck " + i / 3 + ")");
                }
                Assert.That(m.bounds.size.y, Is.LessThan(0.01f), "flach");
            }
            finally { Object.DestroyImmediate(m); }
        }
    }
}
