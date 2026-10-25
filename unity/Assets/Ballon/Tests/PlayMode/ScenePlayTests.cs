// PlayMode: Szenenlader, Umschalten der Szene (Taste L) und der Lichtszene (Taste N), Parcours (Start, Kontrollpunkte, Ziel, Taste T).
// Die synthetische Szene „Testkurs“ (EditMode/scene_fixture_v2.json; ohne FBX-Datei: die Umgebung ist ein Satz Quader aus dem Test, die
// Atlanten sind kleine Testtexturen) prüft Lader, Zustand und Rückkehr in den Parcours immer; die echten exportierten Szenen
// (Generated/Scenes) prüft der letzte Test, falls vorhanden.
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
using UnityEngine.TestTools.Constraints;
using Is = UnityEngine.TestTools.Constraints.Is;   // NUnit-Is plus AllocatingGCMemory
using Object = UnityEngine.Object;

namespace Ballon.Ego.Tests
{
    public class ScenePlayTests
    {
        const string FixturePath = "Assets/Ballon/Tests/EditMode/scene_fixture_v2.json";
        static readonly string PrefsKey = CourseRun.PrefsKey("testkurs");
        static string Room => File.ReadAllText(FixturePath);

        static Bootstrap B => Object.FindAnyObjectByType<Bootstrap>();
        readonly List<Object> _made = new List<Object>();

        [UnitySetUp]
        public IEnumerator LoadScene()
        {
            PlayerPrefs.DeleteKey(PrefsKey);
            if (B == null)
            {
                SceneManager.LoadScene("Firstfeel");
                yield return null;
                yield return null;
            }
            if (B.CurrentScene != -1) B.ShowScene(-1);
        }

        /// <summary>Spieler nach jedem Test zurück auf Tastatur, echte Zeit und Parcours (Tests hängen nicht voneinander ab).</summary>
        [UnityTearDown]
        public IEnumerator Zuruecksetzen()
        {
            var b = Object.FindAnyObjectByType<Bootstrap>();
            if (b != null && b.Player != null)
            {
                b.Player.deltaOverride = null;
                b.Player.input = new DeviceInput();
                if (b.CurrentScene != -1) b.ShowScene(-1);
            }
            foreach (var o in _made) if (o != null) Object.DestroyImmediate(o);
            _made.Clear();
            PlayerPrefs.DeleteKey(PrefsKey);
            yield return null;
        }

        sealed class Snapshot
        {
            public UnityEngine.Rendering.AmbientMode mode;
            public Color sky, equator, ground, fogColor;
            public bool fog, sun, range;
            public float fogStart, fogEnd;
            public Color bg;
            public int mask, probeMask, probeRes;
            public Vector3 probePos, probeSize, probeCenter;
            public Color probeBg;
            public RangeTargets targets;
            public CourseRun course;
            public string hud;

            public static Snapshot Take(Bootstrap b) => new Snapshot
            {
                mode = RenderSettings.ambientMode, sky = RenderSettings.ambientSkyColor, equator = RenderSettings.ambientEquatorColor,
                ground = RenderSettings.ambientGroundColor, fogColor = RenderSettings.fogColor, fog = RenderSettings.fog,
                fogStart = RenderSettings.fogStartDistance, fogEnd = RenderSettings.fogEndDistance,
                sun = b.Sun.enabled, range = b.RangeRoot.gameObject.activeSelf,
                bg = b.Player.worldCam.backgroundColor, mask = b.Player.worldCam.cullingMask,
                probeMask = b.Probe.cullingMask, probeRes = b.Probe.resolution, probePos = b.Probe.transform.position,
                probeSize = b.Probe.size, probeCenter = b.Probe.center, probeBg = b.Probe.backgroundColor, targets = b.Player.range,
                course = b.Player.course,
            };

            public void AssertSame(Snapshot o, string what)
            {
                Assert.AreEqual(mode, o.mode, what + ": Umgebungslicht-Modus");
                Assert.AreEqual(sky, o.sky, what + ": Himmel");
                Assert.AreEqual(equator, o.equator, what + ": Horizont");
                Assert.AreEqual(ground, o.ground, what + ": Boden");
                Assert.AreEqual(fog, o.fog, what + ": Nebel");
                Assert.AreEqual(fogColor, o.fogColor, what + ": Nebelfarbe");
                Assert.AreEqual(fogStart, o.fogStart, what + ": Nebelanfang");
                Assert.AreEqual(fogEnd, o.fogEnd, what + ": Nebelende");
                Assert.AreEqual(sun, o.sun, what + ": Sonne");
                Assert.AreEqual(range, o.range, what + ": Parcours sichtbar");
                Assert.AreEqual(bg, o.bg, what + ": Kamerahintergrund");
                Assert.AreEqual(mask, o.mask, what + ": Kameramaske");
                Assert.AreEqual(probeMask, o.probeMask, what + ": Sondenmaske");
                Assert.AreEqual(probeRes, o.probeRes, what + ": Sondenauflösung");
                Assert.AreEqual(probePos, o.probePos, what + ": Sondenort");
                Assert.AreEqual(probeSize, o.probeSize, what + ": Sondengröße");
                Assert.AreEqual(probeCenter, o.probeCenter, what + ": Sondenmitte");
                Assert.AreEqual(probeBg, o.probeBg, what + ": Sondenhintergrund");
                Assert.AreSame(targets, o.targets, what + ": Zielscheiben");
                Assert.AreSame(course, o.course, what + ": Parcours-Lauf");
            }
        }

        /// <summary>Umgebung aus dem Test: je ein Quader mit dem Namen eines Objekts der Fixture (Boden und Kiste: Zone „nah“, Wand_N: „fern“).
        /// Trägt Renderer und Collider; der Lader kopiert sie und entfernt die Collider der Kopie.</summary>
        static GameObject MakeEnv()
        {
            var root = new GameObject("TestUmgebung");
            Cube(root, "Boden", new Vector3(0, -0.05f, 0), new Vector3(40, 0.1f, 60));
            Cube(root, "Kiste", new Vector3(-3, 0.5f, 4), new Vector3(1, 1, 2));
            Cube(root, "Wand_N", new Vector3(0, 2, 30.5f), new Vector3(40, 4, 1));
            return root;
        }

        static void Cube(GameObject parent, string name, Vector3 pos, Vector3 scale)
        {
            var g = GameObject.CreatePrimitive(PrimitiveType.Cube);
            g.name = name;
            g.transform.SetParent(parent.transform, false);
            g.transform.position = pos;
            g.transform.localScale = scale;
        }

        static Material Unlit() => new Material(Shader.Find("Universal Render Pipeline/Unlit")) { name = "Test_Vorlage" };

        /// <summary>Atlanten [Lichtszene][Zone] als kleine Einfarbtexturen (alle verschieden), damit der Austausch sichtbar nachweisbar ist.</summary>
        Texture2D[][] Atlases(SceneFile f)
        {
            var r = new Texture2D[f.lightings.Length][];
            for (int li = 0; li < r.Length; li++)
            {
                r[li] = new Texture2D[f.zones.Length];
                for (int zi = 0; zi < f.zones.Length; zi++)
                {
                    var t = new Texture2D(2, 2) { name = $"Atlas {f.lightings[li].name}/{f.zones[zi].name}" };
                    t.SetPixels(new[] { Color.white, Color.white, Color.white, Color.white });
                    t.Apply();
                    _made.Add(t);
                    r[li][zi] = t;
                }
            }
            return r;
        }

        /// <summary>Bestzeiten der echten Szenen sichern und danach zurückschreiben (die Tests löschen sie, um frisch zu prüfen).</summary>
        sealed class KeepBest : IDisposable
        {
            readonly List<(string key, bool had, float value)> _saved = new List<(string, bool, float)>();

            public KeepBest(Bootstrap b)
            {
                for (int i = 0; i < b.SceneCount; i++)
                {
                    string k = CourseRun.PrefsKey(b.SceneDataAt(i).name);
                    _saved.Add((k, PlayerPrefs.HasKey(k), PlayerPrefs.GetFloat(k, 0f)));
                }
            }

            public void Dispose()
            {
                foreach (var s in _saved)
                    if (s.had) PlayerPrefs.SetFloat(s.key, s.value); else PlayerPrefs.DeleteKey(s.key);
                PlayerPrefs.Save();
            }
        }

        static void Idle(EgoPlayer p)
        {
            p.input = new ScriptedInput().Add(0, 1000);
            p.deltaOverride = () => 1f / 30f;
            p.C.ReadyNow();
        }

        /// <summary>Fixture-Szene anmelden und zeigen; die Original-Umgebung wird entfernt (nur die Kopie des Laders bleibt).</summary>
        int AddAndShow(out SceneFile f, out Texture2D[][] atlases)
        {
            var b = B;
            f = SceneFile.Parse(Room);
            atlases = Atlases(f);
            var env = MakeEnv();
            int idx = b.AddScene(f, env, Unlit(), atlases);
            b.ShowScene(idx);
            Object.DestroyImmediate(env);
            return idx;
        }

        /// <summary>Spieler in den Auslösequader stellen (Füße knapp über dem Boden des Quaders).</summary>
        static void Enter(EgoPlayer p, SceneBox box)
        {
            var bd = SceneConvert.Box(box);
            p.Teleport(new Vector3(bd.center.x, bd.min.y + 0.02f, bd.center.z), 0f, 0f);
        }

        sealed class LogCatcher : IDisposable
        {
            public readonly List<string> lines = new List<string>();
            public LogCatcher() { Application.logMessageReceived += On; }
            void On(string msg, string stack, LogType t) { lines.Add(msg); }
            public void Dispose() { Application.logMessageReceived -= On; }
            public string Find(string part) => lines.Find(l => l.Contains(part));
        }

        /// <summary>Tastatur für Tastenereignisse im Stapelbetrieb (ohne Fokus schaltet das Input System Tastaturen ab); stellt alles zurück.</summary>
        sealed class Kb : IDisposable
        {
            readonly Keyboard _kb;
            readonly bool _added;
            readonly InputSettings.BackgroundBehavior _oldBg;
#if UNITY_EDITOR
            readonly InputSettings.EditorInputBehaviorInPlayMode _oldEd;
#endif
            public Kb()
            {
                _oldBg = InputSystem.settings.backgroundBehavior;                 // globale Einstellungen sichern, in Dispose zurück
#if UNITY_EDITOR
                _oldEd = InputSystem.settings.editorInputBehaviorInPlayMode;
                InputSystem.settings.editorInputBehaviorInPlayMode = InputSettings.EditorInputBehaviorInPlayMode.AllDeviceInputAlwaysGoesToGameView;
#endif
                InputSystem.settings.backgroundBehavior = InputSettings.BackgroundBehavior.IgnoreFocus;
                _kb = Keyboard.current;
                if (_kb == null) { _kb = InputSystem.AddDevice<Keyboard>(); _added = true; }
                if (!_kb.enabled) InputSystem.EnableDevice(_kb);
            }
            public void Press(Key k) => InputSystem.QueueStateEvent(_kb, new KeyboardState(k));
            public void Release() => InputSystem.QueueStateEvent(_kb, new KeyboardState());
            public void Dispose()
            {
                if (_added) InputSystem.RemoveDevice(_kb);
                InputSystem.settings.backgroundBehavior = _oldBg;
#if UNITY_EDITOR
                InputSystem.settings.editorInputBehaviorInPlayMode = _oldEd;
#endif
            }
        }

        // ------------------------------------------------------------------------------------------------ Lader
        [UnityTest]
        public IEnumerator Szene_laden_Zonen_Lichtszenen_Parcours_und_Start()
        {
            var b = B;
            var p = b.Player;
            var oldInput = p.input;
            Idle(p);
            int n0 = b.SceneCount;
            int idx = AddAndShow(out var f, out var atlases);
            Assert.AreEqual(n0 + 1, b.SceneCount);
            try
            {
                yield return null;                                       // Collider der Umgebungskopie sind weg (Destroy am Bildende)
                var L = b.LoadedSceneAt(idx);
                Assert.IsNotNull(L);
                Assert.AreEqual(idx, b.CurrentScene);
                Assert.AreEqual(0, b.CurrentLighting, "erste Lichtszene ist der Standard");
                Assert.AreEqual(2, b.LightingCount);
                Assert.IsTrue(L.root.gameObject.activeSelf);
                Assert.IsFalse(b.RangeRoot.gameObject.activeSelf, "Parcours aus");
                Assert.IsFalse(b.Sun.enabled, "Sonne aus");
                Assert.IsFalse(RenderSettings.fog, "kein Nebel");
                // Umgebung: je Zone ein eigenes Unlit-Material mit dem Atlas der aktiven Lichtszene, unbeleuchtet, ohne Schatten
                var umg = L.root.Find("Umgebung");
                var rs = umg.GetComponentsInChildren<Renderer>();
                Assert.AreEqual(3, rs.Length);
                Assert.AreEqual(2, L.zoneMats.Length);
                Assert.AreNotSame(L.zoneMats[0], L.zoneMats[1]);
                Assert.AreEqual("Zone testkurs/nah", L.zoneMats[0].name);
                foreach (var r in rs)
                {
                    int zi = f.ZoneIndex(r.name == "Wand_N" ? "fern" : "nah");
                    Assert.AreSame(L.zoneMats[zi], r.sharedMaterial, $"{r.name}: Material seiner Zone");
                    Assert.AreEqual(UnityEngine.Rendering.ShadowCastingMode.Off, r.shadowCastingMode, r.name);
                }
                Assert.AreEqual("Universal Render Pipeline/Unlit", L.zoneMats[0].shader.name);
                var tint = SceneConvert.Gamma(Color.white, 3f);
                for (int z = 0; z < 2; z++)
                {
                    Assert.AreSame(atlases[0][z], L.zoneMats[z].GetTexture("_BaseMap"), $"Zone {z}: Atlas der Lichtszene Tag");
                    Assert.AreEqual(tint.r, L.zoneMats[z].GetColor("_BaseColor").r, 1e-4f, $"Zone {z}: _BaseColor = scale (3,0) als Gamma-Wert");
                }
                Assert.IsNull(umg.GetComponentInChildren<Collider>(), "Kollision nur aus colliders");
                // Collider aus dem Format, Blender → Unity (−x, z, −y)
                Assert.AreEqual(2, L.colliders.Count);
                Assert.AreEqual(new Vector3(0, -0.05f, 0), L.colliders[0].transform.position);
                Assert.AreEqual(new Vector3(40, 0.1f, 60), L.colliders[0].size);
                Assert.AreEqual(new Vector3(-3, 0.5f, 4), L.colliders[1].transform.position);
                Assert.AreEqual(new Vector3(1, 1, 2), L.colliders[1].size);
                // Umgebungslicht, Himmel, Sonde aus der Lichtszene Tag
                Assert.AreEqual(UnityEngine.Rendering.AmbientMode.Flat, RenderSettings.ambientMode);
                Assert.AreEqual(SceneConvert.Gamma(SceneConvert.Linear("#8C96A3"), 0.45f).r, RenderSettings.ambientLight.r, 1e-4f, "Umgebungslicht = Farbe × Stärke");
                Assert.AreEqual(SceneConvert.Gamma(SceneConvert.Linear("#9FB4C8"), 1.3f).g, p.worldCam.backgroundColor.g, 1e-4f, "Himmel = Farbe × Stärke");
                Assert.AreEqual(0, p.worldCam.cullingMask & (1 << Bootstrap.StudioEmitLayer), "Lichtflächen nicht in der Weltkamera");
                Assert.AreEqual(0, p.worldCam.cullingMask & (1 << Bootstrap.ViewmodelLayer), "Viewmodel nicht in der Weltkamera");
                Assert.AreNotEqual(0, b.Probe.cullingMask & (1 << Bootstrap.StudioEmitLayer), "Sonde sieht Lichtflächen");
                Assert.AreEqual(0, b.Probe.cullingMask & (1 << Bootstrap.ViewmodelLayer), "Sonde sieht das Viewmodel nicht");
                Assert.IsTrue(b.Probe.bounds.Contains(L.spawnPos), "Sonde deckt den Startpunkt ab");
                Assert.AreEqual(p.worldCam.backgroundColor, b.Probe.backgroundColor, "Sonde: Himmel der Lichtszene");
                // Lichtgruppen: nur die der aktiven Lichtszene ist an; Lichter nur fürs Viewmodel, Flächenlicht zusätzlich als leuchtende Fläche
                Assert.AreEqual(2, L.lightings.Length);
                Assert.IsTrue(L.lightings[0].group.activeSelf);
                Assert.IsFalse(L.lightings[1].group.activeSelf);
                var tag = L.lightings[0];
                var nacht = L.lightings[1];
                Assert.AreEqual(2, tag.lights.Count);
                Assert.AreEqual(3, nacht.lights.Count);
                foreach (var l in tag.lights)
                {
                    Assert.AreEqual(1 << Bootstrap.ViewmodelLayer, l.cullingMask, l.name);
                    Assert.AreEqual(LightShadows.None, l.shadows, l.name);
                    Assert.IsTrue(l.gameObject.activeInHierarchy, l.name);
                }
                foreach (var l in nacht.lights) Assert.IsFalse(l.gameObject.activeInHierarchy, "Nacht-Lichter sind aus: " + l.name);
                Assert.AreEqual(LightType.Spot, tag.lights[0].type);
                Assert.AreEqual(800f / (Mathf.PI * Mathf.PI), tag.lights[0].intensity, 1e-3f, "Fläche P/π²");
                Assert.AreEqual(LightType.Directional, tag.lights[1].type);
                Assert.AreEqual(3f / Mathf.PI, tag.lights[1].intensity, 1e-3f, "Sonne S/π");
                Assert.AreEqual(70f, nacht.lights[0].spotAngle, 1e-4f, "Spot-Winkel aus den Daten");
                Assert.AreEqual(LightType.Point, nacht.lights[1].type);
                Assert.That(Vector3.Angle(tag.lights[0].transform.forward, Vector3.down), Is.LessThan(0.01f), "Leuchtrichtung nach unten");
                Assert.AreEqual(1, tag.emitters.Count, "nur das Flächenlicht hat eine Lichtfläche");
                Assert.AreEqual(1, nacht.emitters.Count);
                Assert.AreEqual(Bootstrap.StudioEmitLayer, tag.emitters[0].layer);
                Assert.IsNull(tag.emitters[0].GetComponent<Collider>());
                Assert.That(Vector3.Angle(-tag.emitters[0].transform.forward, Vector3.down), Is.LessThan(0.01f), "sichtbare Seite zeigt nach unten");
                // Zielscheiben des Parcours: Mitte, Ringseite entlang der Normalen, Radius, Pfosten bis zum Boden
                Assert.AreEqual(3, L.targets.targets.Count);
                var t1 = L.targets.targets[0];
                var t2 = L.targets.targets[1];
                var t3 = L.targets.targets[2];
                Assert.AreSame(L.targets, p.range, "Anzeige zählt die Treffer der Szene");
                Assert.That(Vector3.Distance(new Vector3(6, 1.6f, -8), t1.transform.position), Is.LessThan(1e-4f), "T01: Scheibenmitte");
                Assert.That(Vector3.Distance(new Vector3(-6, 1.6f, 2), t2.transform.position), Is.LessThan(1e-4f), "T02: Scheibenmitte");
                Assert.That(Vector3.Distance(new Vector3(0, 2.0f, 8), t3.transform.position), Is.LessThan(1e-4f), "T03: Scheibenmitte (2,0 m hoch)");
                Assert.That(Vector3.Angle(t1.FaceNormal, Vector3.back), Is.LessThan(0.1f), "T01: Ringseite entlang der Normalen");
                Assert.That(Vector3.Angle(t2.FaceNormal, Vector3.right), Is.LessThan(0.1f), "T02: Ringseite entlang der Normalen (−X Blender)");
                Assert.AreEqual(0.3f * 2, t1.transform.lossyScale.x, 1e-4f, "T01: Durchmesser");
                Assert.AreEqual(0.45f * 2, t2.transform.lossyScale.x, 1e-4f, "T02: Durchmesser");
                foreach (var t in L.targets.targets)
                    Assert.AreEqual(0f, t.transform.parent.position.y, 1e-4f, "Pfosten steht auf dem Boden");
                Assert.IsTrue(Physics.Raycast(t1.transform.position + Vector3.back * 2, Vector3.forward, out var th, 5f));
                Assert.AreSame(t1, th.collider.GetComponentInParent<RangeTarget>(), "Strahl trifft die Scheibe");
                t1.Hit(th.point);
                Assert.AreEqual(1, t1.hits);
                // Parcours: Quader, Lauf bereit, Wegmarken
                Assert.IsNotNull(L.course);
                Assert.AreSame(L.course, p.course);
                Assert.AreEqual(CourseRun.Phase.Bereit, L.course.State);
                Assert.AreEqual(2, L.course.CheckpointCount);
                Assert.AreEqual(45f, L.course.ParTime);
                Assert.IsNotNull(L.routeMarkers);
                var mesh = L.routeMarkers.GetComponent<MeshFilter>().sharedMesh;
                Assert.Greater(mesh.vertexCount, 7 * 10, "Pfeile entlang der Strecke");
                Assert.AreEqual(UnityEngine.Rendering.ShadowCastingMode.Off, L.routeMarkers.GetComponent<Renderer>().shadowCastingMode);
                // Start: Füße am Spawn, Blick nach Gier −30° (Blender 30° nach links = Unity −30°)
                var sp = SceneConvert.Point(f.spawn.pos);
                Assert.That(Vector2.Distance(new Vector2(sp.x, sp.z), new Vector2(p.transform.position.x, p.transform.position.z)), Is.LessThan(0.01f));
                Assert.That(Vector3.Angle(p.transform.forward, Quaternion.Euler(0, -30, 0) * Vector3.forward), Is.LessThan(0.1f), "Blick");
                Assert.IsTrue(Physics.Raycast(L.spawnPos + Vector3.up, Vector3.down, out var gh, 3f), "unter dem Startpunkt liegt Boden");
                Assert.IsTrue(gh.collider.transform.IsChildOf(L.root), "Boden ist ein Collider der Szene");
                for (int i = 0; i < 45; i++) yield return null;
                Assert.That(p.transform.position.y, Is.InRange(-0.05f, 0.1f), "Spieler steht auf dem Boden");
                Assert.IsTrue(p.GetComponent<CharacterController>().isGrounded, "Spieler hat Bodenkontakt");
                Assert.AreEqual(CourseRun.Phase.Bereit, L.course.State, "der Spawn liegt vor dem Start: es läuft keine Zeit");
                // Anzeige nennt Szene und Licht, baut ihren Text nur bei Änderung neu (kein GC je Bild)
                p.UpdateHudText();
                StringAssert.Contains("Szene Testkurs (L)", p.HudHitText);
                StringAssert.Contains("Licht Tag (N)", p.HudHitText);
                StringAssert.DoesNotContain("10 m:", p.HudHitText, "mit Parcours zählt die Lauf-Anzeige die Ziele");
                NUnit.Framework.Assert.That(() => { for (int k = 0; k < 200; k++) p.UpdateHudText(); }, Is.Not.AllocatingGCMemory(), "HUD");
            }
            finally
            {
                p.input = oldInput;
                b.RemoveScene(idx);
            }
            Assert.AreEqual(n0, b.SceneCount);
            Assert.AreEqual(-1, b.CurrentScene);
            Assert.AreEqual(-1, b.CurrentLighting);
            Assert.IsNull(p.course, "im Parcours läuft kein Lauf");
            Assert.IsTrue(b.RangeRoot.gameObject.activeSelf);
        }

        [UnityTest]
        public IEnumerator Schiessstand_Ziele_ohne_Parcours_zeigen_die_Treffer_je_Entfernung()
        {
            var b = B;
            var p = b.Player;
            Idle(p);
            var json = Room;
            int a = json.IndexOf("\"course\": {", StringComparison.Ordinal);
            int e = json.IndexOf("\"targets\": []", StringComparison.Ordinal);
            json = json.Remove(a, e - a).Replace("\"targets\": []", "\"targets\": [{\"pos\": [0, -8, 1.45], \"distance\": 10}]");
            var f = SceneFile.Parse(json);
            var env = MakeEnv();
            int idx = b.AddScene(f, env, Unlit(), Atlases(f));
            try
            {
                b.ShowScene(idx);
                Object.DestroyImmediate(env);
                yield return null;
                var L = b.LoadedSceneAt(idx);
                Assert.IsNull(L.course);
                Assert.IsNull(p.course);
                Assert.IsNull(L.routeMarkers);
                Assert.AreEqual(1, L.targets.targets.Count);
                p.UpdateHudText();
                StringAssert.Contains("10 m:", p.HudHitText, "Zähler je Entfernung wie im Parcours");
            }
            finally { b.RemoveScene(idx); }
        }

        // ------------------------------------------------------------------------------------------------ Lichtszenen (Taste N)
        [UnityTest]
        public IEnumerator Lichtszene_wechseln_tauscht_nur_Atlas_Himmel_Lichter_und_Sonde()
        {
            var b = B;
            var p = b.Player;
            Idle(p);
            int idx = AddAndShow(out var f, out var atlases);
            try
            {
                yield return null;
                var L = b.LoadedSceneAt(idx);
                var umg = L.root.Find("Umgebung");
                int childCount = L.root.childCount, renderers = umg.GetComponentsInChildren<Renderer>(true).Length;
                var zm0 = L.zoneMats[0];
                var zm1 = L.zoneMats[1];
                var r0 = umg.Find("Boden").GetComponent<Renderer>();
                b.NextLighting();                                   // wie Taste N
                yield return null;
                Assert.AreEqual(1, b.CurrentLighting);
                for (int z = 0; z < 2; z++)
                {
                    Assert.AreSame(atlases[1][z], L.zoneMats[z].GetTexture("_BaseMap"), $"Zone {z}: Atlas der Lichtszene Nacht");
                    Assert.AreEqual(SceneConvert.Gamma(Color.white, 1.5f).r, L.zoneMats[z].GetColor("_BaseColor").r, 1e-4f, $"Zone {z}: scale 1,5");
                }
                Assert.AreEqual(SceneConvert.Gamma(SceneConvert.Linear("#10182A"), 0.6f).b, p.worldCam.backgroundColor.b, 1e-4f, "Himmel Nacht");
                Assert.AreEqual(SceneConvert.Gamma(SceneConvert.Linear("#2A3550"), 0.3f).b, RenderSettings.ambientLight.b, 1e-4f, "Umgebungslicht Nacht");
                Assert.AreEqual(p.worldCam.backgroundColor, b.Probe.backgroundColor, "Sonde: Himmel Nacht");
                Assert.IsFalse(L.lightings[0].group.activeSelf);
                Assert.IsTrue(L.lightings[1].group.activeSelf);
                foreach (var l in L.lightings[1].lights) Assert.IsTrue(l.gameObject.activeInHierarchy, l.name);
                foreach (var l in L.lightings[0].lights) Assert.IsFalse(l.gameObject.activeInHierarchy, l.name);
                p.UpdateHudText();
                StringAssert.Contains("Licht Nacht (N)", p.HudHitText);
                // Geometrie, Materialinstanzen und Zielscheiben bleiben dieselben (kein Neuaufbau)
                Assert.AreSame(umg, L.root.Find("Umgebung"));
                Assert.AreEqual(childCount, L.root.childCount);
                Assert.AreEqual(renderers, umg.GetComponentsInChildren<Renderer>(true).Length);
                Assert.AreSame(zm0, L.zoneMats[0]);
                Assert.AreSame(zm1, L.zoneMats[1]);
                Assert.AreSame(zm0, r0.sharedMaterial);
                Assert.AreSame(L, b.LoadedSceneAt(idx));
                Assert.AreEqual(3, L.targets.targets.Count);
                // zurück auf Tag (die Reihe läuft rund)
                b.NextLighting();
                yield return null;
                Assert.AreEqual(0, b.CurrentLighting);
                Assert.AreSame(atlases[0][0], L.zoneMats[0].GetTexture("_BaseMap"));
                Assert.AreEqual(SceneConvert.Gamma(SceneConvert.Linear("#9FB4C8"), 1.3f).g, p.worldCam.backgroundColor.g, 1e-4f);
                // nach dem ersten Mal kein Speicher je Bild (Spielschritt mit Lauf-Prüfung, Anzeige)
                p.UpdateHudText();
                NUnit.Framework.Assert.That(() => { for (int k = 0; k < 120; k++) L.course.Tick(p.transform.position + Vector3.up * CourseRun.BodyCenter, 1f / 30f); },
                    Is.Not.AllocatingGCMemory(), "Lauf-Prüfung nach dem Umschalten");
                p.UpdateHudText();
                NUnit.Framework.Assert.That(() => { for (int k = 0; k < 120; k++) p.UpdateHudText(); }, Is.Not.AllocatingGCMemory(), "Anzeige nach dem Umschalten");
                // die zuletzt gezeigte Lichtszene bleibt bei Szenenwechsel erhalten
                b.ShowLighting(1);
                b.ShowScene(-1);
                Assert.AreEqual(-1, b.CurrentLighting, "Parcours hat keine Lichtszene");
                b.NextLighting();                                   // im Parcours ohne Wirkung
                Assert.AreEqual(-1, b.CurrentLighting);
                Assert.Throws<InvalidOperationException>(() => b.ShowLighting(0));
                b.ShowScene(idx);
                Assert.AreEqual(1, b.CurrentLighting, "Szene erinnert sich an Nacht");
                Assert.AreSame(atlases[1][1], L.zoneMats[1].GetTexture("_BaseMap"));
                Assert.Throws<ArgumentOutOfRangeException>(() => b.ShowLighting(2));
            }
            finally { b.RemoveScene(idx); }
        }

        [UnityTest]
        public IEnumerator Tasten_N_und_T_schalten_Licht_und_zurueck_zum_Start()
        {
            var b = B;
            var p = b.Player;
            Idle(p);
            int idx = AddAndShow(out var f, out var atlases);
            using (var kb = new Kb())
            {
                try
                {
                    yield return null;
                    var L = b.LoadedSceneAt(idx);
                    Assert.AreEqual(0, b.CurrentLighting);
                    kb.Press(Key.N);
                    yield return null;
                    kb.Release();
                    yield return null;
                    Assert.AreEqual(1, b.CurrentLighting, "N: nächste Lichtszene");
                    Assert.AreSame(atlases[1][0], L.zoneMats[0].GetTexture("_BaseMap"));
                    kb.Press(Key.N);
                    yield return null;
                    kb.Release();
                    yield return null;
                    Assert.AreEqual(0, b.CurrentLighting, "N: wieder die erste");
                    // T: zurück zum Start, ein laufender Lauf wird verworfen
                    yield return null;
                    Enter(p, f.course.start);
                    yield return null;
                    Enter(p, f.course.checkpoints[0]);
                    yield return null;
                    Assert.AreEqual(CourseRun.Phase.Lauf, L.course.State);
                    kb.Press(Key.T);
                    yield return null;
                    kb.Release();
                    yield return null;
                    Assert.AreEqual(CourseRun.Phase.Bereit, L.course.State, "T verwirft den Lauf");
                    Assert.AreEqual(0, L.course.CheckpointsDone);
                    var sp = SceneConvert.Point(f.spawn.pos);
                    Assert.That(Vector2.Distance(new Vector2(sp.x, sp.z), new Vector2(p.transform.position.x, p.transform.position.z)), Is.LessThan(0.05f), "T: am Startpunkt");
                    Assert.That(Vector3.Angle(p.transform.forward, Quaternion.Euler(0, -30, 0) * Vector3.forward), Is.LessThan(0.1f), "T: Blick wie beim Start");
                    Assert.AreEqual(0, b.CurrentLighting, "T ändert die Lichtszene nicht");
                    // N im Parcours: ohne Wirkung; T im Parcours: Parcours-Start
                    b.ShowScene(-1);
                    p.Teleport(new Vector3(5, 0.01f, 9), 40f);
                    kb.Press(Key.N);
                    yield return null;
                    kb.Release();
                    yield return null;
                    Assert.AreEqual(-1, b.CurrentLighting);
                    kb.Press(Key.T);
                    yield return null;
                    kb.Release();
                    yield return null;
                    Assert.That(Vector2.Distance(new Vector2(Bootstrap.ParcoursStart.x, Bootstrap.ParcoursStart.z), new Vector2(p.transform.position.x, p.transform.position.z)), Is.LessThan(0.05f), "T im Parcours: Start");
                }
                finally { b.RemoveScene(idx); }
            }
        }

        // ------------------------------------------------------------------------------------------------ Parcours-Lauf
        [UnityTest]
        public IEnumerator Parcours_Start_Kontrollpunkte_Ziel_ergibt_gueltige_Zeit_und_Bestzeit()
        {
            var b = B;
            var p = b.Player;
            Idle(p);
            int idx = AddAndShow(out var f, out _);
            using (var log = new LogCatcher())
            {
                try
                {
                    yield return null;
                    yield return null;                                    // Lauf merkt sich den Stand am Spawn
                    var L = b.LoadedSceneAt(idx);
                    var run = L.course;
                    Assert.AreEqual(CourseRun.Phase.Bereit, run.State);
                    Assert.AreEqual("", run.TimeLabel);
                    Enter(p, f.course.start);
                    yield return null;
                    Assert.AreEqual(CourseRun.Phase.Lauf, run.State, "Start durchschritten");
                    // Treffer unterwegs: echter Schuss auf T01 aus 3 m Abstand (Ringseite zeigt nach −Z, der Schütze steht davor)
                    var t1 = L.targets.targets[0];
                    p.Teleport(new Vector3(6f, 0.02f, -11f), 0f, 0f);
                    p.input = new ScriptedInput().Add(0, 0.6f, hold: "fire");
                    p.C.ReadyNow();
                    p.C.ammo = 9;
                    for (int i = 0; i < 25; i++) yield return null;
                    Idle(p);
                    Assert.Greater(t1.hits, 0, "Schuss trifft T01");
                    Assert.AreEqual(1, run.TargetsHit, "genau eine Scheibe getroffen");
                    Enter(p, f.course.checkpoints[0]);
                    yield return null;
                    yield return null;
                    Assert.AreEqual(1, run.CheckpointsDone);
                    Enter(p, f.course.checkpoints[1]);
                    yield return null;
                    yield return null;
                    Assert.AreEqual(2, run.CheckpointsDone);
                    Assert.AreEqual(CourseRun.Phase.Lauf, run.State, "ohne Ziel läuft die Zeit weiter");
                    float before = run.Elapsed;
                    Assert.Greater(before, 0.5f, "Zeit läuft (Schuss und Kontrollpunkte)");
                    Enter(p, f.course.finish);
                    yield return null;
                    Assert.AreEqual(CourseRun.Phase.Ziel, run.State, "Ziel erreicht");
                    Assert.IsTrue(run.LastValid);
                    Assert.Greater(run.LastTime, before, "Zeit lief bis zum Ziel");
                    Assert.AreEqual(Mathf.Round(run.LastTime * 30f), run.LastTime * 30f, 0.02f, "ganze Bilder à 1/30 s");
                    Assert.AreEqual(run.LastTime, run.BestTime, 1e-6f);
                    Assert.AreEqual(run.LastTime, PlayerPrefs.GetFloat(PrefsKey), 1e-6f, "Bestzeit in PlayerPrefs");
                    var m = log.Find("[Ballon] Lauf: gültig");
                    Assert.IsNotNull(m, "Ergebnis-Marker im Log: " + string.Join(" | ", log.lines));
                    StringAssert.Contains("szene=testkurs", m);
                    StringAssert.Contains("kontrollpunkte=2/2", m);
                    StringAssert.Contains("treffer=1/3", m);
                    StringAssert.Contains("richtzeit=45.0", m);
                    float stopped = run.Elapsed;
                    for (int i = 0; i < 10; i++) yield return null;
                    Assert.AreEqual(stopped, run.Elapsed, 1e-6f, "im Ziel steht die Zeit");
                    string time = run.TimeLabel;
                    StringAssert.Contains(" s", time);
                    StringAssert.Contains("Bestzeit", run.InfoText);
                    // Neustart durch erneutes Durchschreiten des Starts: Spieler verlässt das Ziel, tritt in den Start
                    p.Teleport(L.spawnPos, L.spawnYaw, 0);
                    yield return null;
                    Enter(p, f.course.start);
                    yield return null;
                    Assert.AreEqual(CourseRun.Phase.Lauf, run.State, "Start startet einen neuen Lauf");
                    Assert.AreEqual(0, run.CheckpointsDone);
                    Assert.AreEqual(0, run.TargetsHit, "Treffer des alten Laufs zählen nicht");
                    Assert.Less(run.Elapsed, 0.2f);
                    Assert.AreEqual(run.LastTime, run.BestTime, 1e-6f, "Bestzeit bleibt");
                }
                finally { b.RemoveScene(idx); }
            }
        }

        [UnityTest]
        public IEnumerator Parcours_falsche_Reihenfolge_ergibt_keine_Zeit()
        {
            var b = B;
            var p = b.Player;
            Idle(p);
            int idx = AddAndShow(out var f, out _);
            using (var log = new LogCatcher())
            {
                try
                {
                    yield return null;
                    yield return null;
                    var run = b.LoadedSceneAt(idx).course;
                    Enter(p, f.course.start);
                    yield return null;
                    Enter(p, f.course.checkpoints[1]);                    // zweiter vor dem ersten
                    yield return null;
                    yield return null;
                    Assert.AreEqual(0, run.CheckpointsDone, "falsche Reihenfolge zählt nicht");
                    Enter(p, f.course.checkpoints[0]);
                    yield return null;
                    yield return null;
                    Assert.AreEqual(1, run.CheckpointsDone);
                    Enter(p, f.course.finish);                            // Ziel mit nur einem Kontrollpunkt
                    yield return null;
                    yield return null;
                    Assert.AreEqual(CourseRun.Phase.Lauf, run.State, "Lauf endet nicht");
                    Assert.IsFalse(run.LastValid, "keine gültige Zeit");
                    Assert.AreEqual(0f, run.BestTime, "keine Bestzeit");
                    Assert.IsFalse(PlayerPrefs.HasKey(PrefsKey), "nichts gespeichert");
                    var m = log.Find("[Ballon] Lauf: ungültig");
                    Assert.IsNotNull(m, "Marker: " + string.Join(" | ", log.lines));
                    StringAssert.Contains("kontrollpunkte=1/2", m);
                    Assert.IsNull(log.Find("[Ballon] Lauf: gültig"));
                    StringAssert.Contains("Rechts hinten", run.Message, "nennt den fehlenden Kontrollpunkt");
                }
                finally { b.RemoveScene(idx); }
            }
        }

        [UnityTest]
        public IEnumerator Parcours_kein_GC_je_Bild_im_Lauf()
        {
            var b = B;
            var p = b.Player;
            Idle(p);
            int idx = AddAndShow(out var f, out _);
            try
            {
                yield return null;
                yield return null;
                var run = b.LoadedSceneAt(idx).course;
                Enter(p, f.course.start);
                yield return null;
                Assert.AreEqual(CourseRun.Phase.Lauf, run.State);
                p.input = new ScriptedInput().Add(0, 1000, move: new Vector2(0, 0.2f));       // langsam laufen
                for (int i = 0; i < 40; i++) yield return null;                               // warmlaufen (Zwischenspeicher, Zeittabelle)
                string info = run.InfoText;
                int warm = (run.TimeLabel + run.StateText + run.InfoText).Length;      // erster Aufruf der Getter (Übersetzung) außerhalb der Messung
                Assert.Greater(warm, 0);
                NUnit.Framework.Assert.That(() =>
                {
                    for (int k = 0; k < 150; k++)
                    {
                        p.Step(1f / 30f);                                  // Bewegung, Lauf-Tor-Prüfung, Zeit
                        var a = run.TimeLabel; var s = run.StateText; var c = run.InfoText;      // Texte, die OnGUI je Bild liest
                    }
                }, Is.Not.AllocatingGCMemory(), "Spielbild im laufenden Lauf (Zeit läuft, Anzeige)");
                Assert.AreSame(info, run.InfoText, "Info nur bei Änderung neu");
                Assert.AreEqual(CourseRun.Phase.Lauf, run.State);
            }
            finally { b.RemoveScene(idx); }
        }

        // ------------------------------------------------------------------------------------------------ Szenenwechsel
        [UnityTest]
        public IEnumerator Umschalten_hin_und_zurueck_laesst_den_Parcours_unveraendert()
        {
            var b = B;
            var p = b.Player;
            var oldInput = p.input;
            var f = SceneFile.Parse(Room);
            var env = MakeEnv();
            int idx = b.AddScene(f, env, Unlit(), Atlases(f));
            try
            {
                Idle(p);
                p.Teleport(new Vector3(5, 0.01f, 5), 40f);
                yield return null;
                var before = Snapshot.Take(b);
                int steps = 0;
                b.NextScene();                                           // wie Taste L
                Object.DestroyImmediate(env);
                yield return null;
                Assert.AreNotEqual(-1, b.CurrentScene, "L verlässt den Parcours");
                var inScene = Snapshot.Take(b);
                Assert.AreNotEqual(before.bg, inScene.bg, "Himmel der Szene");
                b.ShowLighting(1);                                       // Licht der Szene ändert nichts am Parcours
                yield return null;
                do { b.NextScene(); steps++; yield return null; } while (b.CurrentScene != -1 && steps <= b.SceneCount + 1);
                Assert.AreEqual(-1, b.CurrentScene, "L kehrt nach allen Szenen in den Parcours zurück");
                var after = Snapshot.Take(b);
                before.AssertSame(after, "Parcours danach");
                Assert.That(Vector3.Distance(Bootstrap.ParcoursStart, p.transform.position), Is.LessThan(0.01f), "Spieler am Parcours-Start");
                for (int i = 0; i < 30; i++) yield return null;
                Assert.That(p.transform.position.y, Is.InRange(-0.05f, 0.1f), "Spieler steht im Parcours");
                p.UpdateHudText();
                StringAssert.Contains("Szene Parcours", p.HudHitText);
                StringAssert.Contains("50 m:", p.HudHitText);
                StringAssert.DoesNotContain("Licht ", p.HudHitText, "im Parcours keine Lichtszene");
            }
            finally
            {
                p.input = oldInput;
                b.RemoveScene(idx);
            }
        }

        [UnityTest]
        public IEnumerator Taste_L_schaltet_die_Szene()
        {
            var b = B;
            var f = SceneFile.Parse(Room);
            var env = MakeEnv();
            int idx = b.AddScene(f, env, Unlit(), Atlases(f));
            using (var kb = new Kb())
            {
                try
                {
                    int expect = -1;
                    for (int round = 0; round < b.SceneCount + 1; round++)
                    {
                        kb.Press(Key.L);
                        yield return null;
                        kb.Release();
                        yield return null;
                        expect = expect + 1 >= b.SceneCount ? -1 : expect + 1;
                        Assert.AreEqual(expect, b.CurrentScene, $"nach {round + 1}× L");
                        if (round == 0) Object.DestroyImmediate(env);
                    }
                    Assert.AreEqual(-1, b.CurrentScene, "nach einer vollen Runde im Parcours");
                }
                finally { b.RemoveScene(idx); }
            }
        }

        [UnityTest]
        public IEnumerator Exportierte_Szenen_laden_Lichtszenen_wechseln_und_Parcours_laeuft()
        {
            var b = B;
            if (b.SceneCount == 0) Assert.Ignore("keine Szene exportiert (ballon-scene/2: tools/scene_build.py)");
            var p = b.Player;
            var oldInput = p.input;
            Idle(p);
            var before = Snapshot.Take(b);
            var keep = new KeepBest(b);
            try
            {
                for (int i = 0; i < b.SceneCount; i++)
                {
                    b.ShowScene(i);
                    yield return null;
                    var L = b.LoadedSceneAt(i);
                    string nm = b.SceneName(i);
                    Assert.IsNotNull(L, nm);
                    Assert.IsTrue(L.root.Find("Umgebung").GetComponentsInChildren<Renderer>().Length > 0, $"{nm}: Umgebung hat Renderer");
                    Assert.IsTrue(Physics.Raycast(L.spawnPos + Vector3.up, Vector3.down, out var h, 3f), $"{nm}: Boden unter dem Startpunkt");
                    Assert.IsTrue(h.collider.transform.IsChildOf(L.root), $"{nm}: Boden ist ein Collider der Szene");
                    for (int k = 0; k < 45; k++) yield return null;
                    Assert.That(p.transform.position.y, Is.InRange(L.spawnPos.y - 0.2f, L.spawnPos.y + 0.2f), $"{nm}: Spieler bleibt am Boden");
                    Assert.AreEqual(L.data.targets.Length + (L.data.course?.targets.Length ?? 0), L.targets.targets.Count, $"{nm}: Ziele");
                    // jede Lichtszene: Atlas in jeder Zone, Himmel, genau eine Lichtgruppe an
                    for (int li = 0; li < b.LightingCount; li++)
                    {
                        b.ShowLighting(li);
                        yield return null;
                        for (int z = 0; z < L.zoneMats.Length; z++)
                            Assert.IsNotNull(L.zoneMats[z].GetTexture("_BaseMap"), $"{nm}/{L.data.lightings[li].name}: Atlas der Zone {L.data.zones[z].name}");
                        Assert.AreEqual(L.lightings[li].skyGamma, p.worldCam.backgroundColor, $"{nm}/{L.data.lightings[li].name}: Himmel");
                        for (int k = 0; k < L.lightings.Length; k++) Assert.AreEqual(k == li, L.lightings[k].group.activeSelf, $"{nm}: Lichtgruppe {k}");
                    }
                    b.ShowLighting(0);
                    // Parcours: der Reihe nach durch Start, Kontrollpunkte, Ziel
                    if (L.data.course != null)
                    {
                        using (var log = new LogCatcher())
                        {
                            PlayerPrefs.DeleteKey(CourseRun.PrefsKey(L.data.name));
                            L.course.Reset();
                            yield return null;
                            yield return null;
                            Enter(p, L.data.course.start);
                            yield return null;
                            Assert.AreEqual(CourseRun.Phase.Lauf, L.course.State, $"{nm}: Start");
                            foreach (var cp in L.data.course.checkpoints)
                            {
                                Enter(p, cp);
                                yield return null;
                                yield return null;
                            }
                            Assert.AreEqual(L.data.course.checkpoints.Length, L.course.CheckpointsDone, $"{nm}: Kontrollpunkte");
                            Enter(p, L.data.course.finish);
                            yield return null;
                            Assert.IsTrue(L.course.LastValid, $"{nm}: Ziel gültig; Log: {string.Join(" | ", log.lines)}");
                            PlayerPrefs.DeleteKey(CourseRun.PrefsKey(L.data.name));
                        }
                    }
                }
                int steps = 0;
                do { b.NextScene(); steps++; yield return null; } while (b.CurrentScene != -1 && steps <= b.SceneCount + 1);
                Assert.AreEqual(-1, b.CurrentScene);
                before.AssertSame(Snapshot.Take(b), "Parcours danach");
            }
            finally
            {
                p.input = oldInput;
                keep.Dispose();
                if (b.CurrentScene != -1) b.ShowScene(-1);
            }
        }

        /// <summary>Der Vorführlauf (RouteRunner: Route, Springen, Ducken) schafft jeden exportierten Parcours gültig unter der Richtzeit –
        /// fällt ein Hindernis aus der Reichweite der Bewegungen (Sprunghöhe, Kapselhöhe), schlägt dieser Test fehl.</summary>
        [UnityTest]
        public IEnumerator Vorfuehrlauf_schafft_jeden_Parcours()
        {
            var b = B;
            var p = b.Player;
            int ran = 0;
            var keep = new KeepBest(b);
            try
            {
                for (int i = 0; i < b.SceneCount; i++)
                {
                    b.ShowScene(i);
                    yield return null;
                    var L = b.LoadedSceneAt(i);
                    if (L.data.course?.route == null) continue;
                    PlayerPrefs.DeleteKey(CourseRun.PrefsKey(L.data.name));
                    L.course.Reset();
                    p.C.ReadyNow();
                    p.Teleport(L.spawnPos, L.spawnYaw, 4f);
                    var route = new List<Vector3>();
                    foreach (var r in L.data.course.route) route.Add(SceneConvert.Point(r));
                    var runner = new RouteRunner(p, route, L.targets.targets);
                    p.input = runner;
                    p.enabled = false;                          // Schritte hier mit fester Zeit, unabhängig von der Bildrate
                    const float dt = 1f / 30f;
                    int runs0 = L.course.RunsFinished;          // zählt über Reset hinweg (frühere Tests)
                    for (int n = 0; n < 120 * 30 && L.course.RunsFinished == runs0 && !runner.Done; n++)
                    {
                        p.Step(dt);
                        if (n % 30 == 0) yield return null;
                    }
                    p.enabled = true;
                    Assert.IsTrue(L.course.LastValid, $"{L.data.name}: Lauf gültig (Wegpunkt {runner.Waypoint}/{route.Count}, " +
                                                      $"Kontrollpunkte {L.course.CheckpointsDone}/{L.course.CheckpointCount}, Spieler {p.transform.position})");
                    Assert.Less(L.course.LastTime, L.course.ParTime, $"{L.data.name}: unter der Richtzeit");
                    Debug.Log($"[Ballon] Vorführlauf {L.data.name}: {L.course.LastTime:0.0} s, Treffer {L.course.TargetsHit}/{L.course.TargetCount}");
                    PlayerPrefs.DeleteKey(CourseRun.PrefsKey(L.data.name));
                    ran++;
                }
                if (ran == 0) Assert.Ignore("keine Szene mit Parcours exportiert");
            }
            finally
            {
                p.enabled = true;
                keep.Dispose();
                if (b.CurrentScene != -1) b.ShowScene(-1);
            }
        }
    }
}
