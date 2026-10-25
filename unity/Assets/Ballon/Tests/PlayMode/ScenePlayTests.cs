// PlayMode: Szenenlader und Umschalten (Taste L). Die synthetische Szene („Testraum“, ohne FBX-Datei: die Umgebung ist ein Quader aus
// dem Test) prüft Lader, Zustand und Rückkehr in den Parcours immer; die echten exportierten Szenen (Generated/Scenes) prüft der letzte
// Test, falls vorhanden.
using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
using UnityEngine.TestTools.Constraints;
using Is = UnityEngine.TestTools.Constraints.Is;   // NUnit-Is plus AllocatingGCMemory

namespace Ballon.Ego.Tests
{
    public class ScenePlayTests
    {
        const string Room = @"{
          ""format"": ""ballon-scene/1"", ""name"": ""testraum"", ""de"": ""Testraum"", ""fbx"": ""testraum.fbx"",
          ""light_atlas"": {""file"": ""testraum_light.png"", ""size"": 64, ""de"": ""Test""},
          ""objects"": [""Boden""],
          ""colliders"": [{""name"": ""Boden"", ""center"": [0, 0, -0.05], ""size"": [20, 30, 0.1]},
                          {""name"": ""Wand_N"", ""center"": [0, -14.5, 2], ""size"": [20, 1, 4]}],
          ""spawn"": {""pos"": [0, 10, 0], ""yaw_deg"": 30},
          ""sky"": {""color"": ""#9FB4C8"", ""strength"": 1.0},
          ""ambient"": {""color"": ""#8C96A3"", ""strength"": 0.45},
          ""lights"": [{""name"": ""Strahler"", ""kind"": ""area"", ""pos"": [0, 0, 6], ""dir"": [0, 0, -1], ""power_w"": 800, ""size_m"": 1.5, ""color"": ""#FFF2E0""},
                       {""name"": ""Spot"", ""kind"": ""spot"", ""pos"": [3, 3, 4], ""dir"": [0, 0, -1], ""power_w"": 400, ""size_m"": 0.1, ""color"": ""#FFFFFF""}],
          ""targets"": [{""pos"": [0, -8, 1.45], ""distance"": 10}]
        }";

        static Bootstrap B => Object.FindAnyObjectByType<Bootstrap>();

        [UnitySetUp]
        public IEnumerator LoadScene()
        {
            if (B == null)
            {
                SceneManager.LoadScene("Firstfeel");
                yield return null;
                yield return null;
            }
            if (B.CurrentScene != -1) B.ShowScene(-1);
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
            }
        }

        static GameObject MakeEnv()
        {
            var g = GameObject.CreatePrimitive(PrimitiveType.Cube);    // Boden aus dem Test: trägt Renderer und (eigenen) Collider, den der Lader entfernt
            g.name = "TestUmgebung";
            g.transform.localScale = new Vector3(20, 0.1f, 30);
            g.transform.position = new Vector3(0, -0.05f, 0);
            return g;
        }

        static Material Unlit() => new Material(Shader.Find("Universal Render Pipeline/Unlit")) { name = "Test_Atlas" };

        static void Idle(EgoPlayer p)
        {
            p.input = new ScriptedInput().Add(0, 1000);
            p.deltaOverride = () => 1f / 30f;
            p.C.ReadyNow();
        }

        [UnityTest]
        public IEnumerator Szene_laden_Spieler_steht_am_Start_auf_Boden()
        {
            var b = B;
            var p = b.Player;
            var oldInput = p.input;
            var f = SceneFile.Parse(Room);
            var env = MakeEnv();
            int n0 = b.SceneCount;
            int idx = b.AddScene(f, env, Unlit());
            Assert.AreEqual(n0 + 1, b.SceneCount);
            try
            {
                Idle(p);
                b.ShowScene(idx);
                Object.DestroyImmediate(env);
                yield return null;                                       // Collider der Umgebungskopie sind weg (Destroy am Bildende)
                var L = b.LoadedSceneAt(idx);
                Assert.IsNotNull(L);
                Assert.AreEqual(idx, b.CurrentScene);
                Assert.IsTrue(L.root.gameObject.activeSelf);
                Assert.IsFalse(b.RangeRoot.gameObject.activeSelf, "Parcours aus");
                Assert.IsFalse(b.Sun.enabled, "Sonne aus");
                Assert.IsFalse(RenderSettings.fog, "kein Nebel");
                // Umgebung: ein Material für alle Renderer, unbeleuchtet, ohne Schatten
                var rs = L.root.Find("Umgebung").GetComponentsInChildren<Renderer>();
                Assert.AreEqual(1, rs.Length);
                Assert.AreEqual("Test_Atlas", rs[0].sharedMaterial.name);
                Assert.AreEqual(UnityEngine.Rendering.ShadowCastingMode.Off, rs[0].shadowCastingMode);
                Assert.IsNull(L.root.Find("Umgebung").GetComponentInChildren<Collider>(), "Kollision nur aus colliders");
                // Collider aus dem Format, Blender → Unity (−x, z, −y)
                Assert.AreEqual(2, L.colliders.Count);
                Assert.AreEqual(new Vector3(0, -0.05f, 0), L.colliders[0].transform.position);
                Assert.AreEqual(new Vector3(20, 0.1f, 30), L.colliders[0].size);
                Assert.AreEqual(new Vector3(0, 2, 14.5f), L.colliders[1].transform.position);
                Assert.AreEqual(new Vector3(20, 4, 1), L.colliders[1].size);
                // Umgebungslicht, Himmel, Sonde
                Assert.AreEqual(UnityEngine.Rendering.AmbientMode.Flat, RenderSettings.ambientMode);
                var amb = (SceneConvert.Linear("#8C96A3") * 0.45f);
                Assert.AreEqual(new Color(amb.r, amb.g, amb.b, 1).gamma.r, RenderSettings.ambientLight.r, 1e-4f, "Umgebungslicht = Farbe × Stärke");
                Assert.AreEqual(SceneConvert.Gamma(SceneConvert.Linear("#9FB4C8")).g, p.worldCam.backgroundColor.g, 1e-4f, "Himmel");
                Assert.AreEqual(0, p.worldCam.cullingMask & (1 << Bootstrap.StudioEmitLayer), "Lichtflächen nicht in der Weltkamera");
                Assert.AreEqual(0, p.worldCam.cullingMask & (1 << Bootstrap.ViewmodelLayer), "Viewmodel nicht in der Weltkamera");
                Assert.AreNotEqual(0, b.Probe.cullingMask & (1 << Bootstrap.StudioEmitLayer), "Sonde sieht Lichtflächen");
                Assert.AreEqual(0, b.Probe.cullingMask & (1 << Bootstrap.ViewmodelLayer), "Sonde sieht das Viewmodel nicht");
                Assert.IsTrue(b.Probe.bounds.Contains(L.spawnPos), "Sonde deckt den Startpunkt ab");
                // Lichter nur fürs Viewmodel; Flächenlicht zusätzlich als leuchtende Fläche für die Sonde
                Assert.AreEqual(2, L.lights.Count);
                foreach (var l in L.lights)
                {
                    Assert.AreEqual(1 << Bootstrap.ViewmodelLayer, l.cullingMask, l.name);
                    Assert.AreEqual(LightShadows.None, l.shadows, l.name);
                    Assert.AreEqual(LightType.Spot, l.type, l.name);
                }
                Assert.AreEqual(800f / (Mathf.PI * Mathf.PI), L.lights[0].intensity, 1e-3f, "Fläche P/π²");
                Assert.AreEqual(400f / (4 * Mathf.PI * Mathf.PI), L.lights[1].intensity, 1e-3f, "Spot P/(4π²)");
                Assert.That(Vector3.Angle(L.lights[0].transform.forward, Vector3.down), Is.LessThan(0.01f), "Leuchtrichtung nach unten");
                Assert.AreEqual(1, L.emitters.Count, "nur das Flächenlicht hat eine Lichtfläche");
                Assert.AreEqual(Bootstrap.StudioEmitLayer, L.emitters[0].layer);
                Assert.IsNull(L.emitters[0].GetComponent<Collider>());
                Assert.That(Vector3.Angle(-L.emitters[0].transform.forward, Vector3.down), Is.LessThan(0.01f), "sichtbare Seite zeigt nach unten");
                // Zielscheibe an targets (Scheibenmitte 1,45 m), Treffer zählt
                Assert.AreEqual(1, L.targets.targets.Count);
                var t = L.targets.targets[0];
                Assert.AreSame(L.targets, p.range, "Anzeige zählt die Treffer der Szene");
                Assert.That(Vector3.Distance(new Vector3(0, 1.45f, 8), t.transform.position), Is.LessThan(1e-4f), "Scheibenmitte");
                Assert.IsTrue(Physics.Raycast(t.transform.position + Vector3.back * 2, Vector3.forward, out var th, 5f));
                Assert.AreSame(t, th.collider.GetComponentInParent<RangeTarget>(), "Strahl trifft die Scheibe");
                t.Hit(th.point);
                Assert.AreEqual(1, t.hits);
                // Start: Füße am Spawn, Blick nach Gier −30° (Blender 30° nach links = Unity −30°)
                var sp = SceneConvert.Point(f.spawn.pos);
                Assert.That(Vector2.Distance(new Vector2(sp.x, sp.z), new Vector2(p.transform.position.x, p.transform.position.z)), Is.LessThan(0.01f));
                Assert.That(Vector3.Angle(p.transform.forward, Quaternion.Euler(0, -30, 0) * Vector3.forward), Is.LessThan(0.1f), "Blick");
                Assert.IsTrue(Physics.Raycast(L.spawnPos + Vector3.up, Vector3.down, out var gh, 3f), "unter dem Startpunkt liegt Boden");
                Assert.IsTrue(gh.collider.transform.IsChildOf(L.root), "Boden ist ein Collider der Szene");
                for (int i = 0; i < 45; i++) yield return null;
                Assert.That(p.transform.position.y, Is.InRange(-0.05f, 0.1f), "Spieler steht auf dem Boden");
                Assert.IsTrue(p.GetComponent<CharacterController>().isGrounded, "Spieler hat Bodenkontakt");
                // Anzeige nennt die Szene, baut ihren Text nur bei Änderung neu (kein GC je Bild)
                p.UpdateHudText();
                StringAssert.Contains("Testraum", p.HudHitText);
                StringAssert.Contains("10 m:", p.HudHitText, "Zähler der Szene");
                NUnit.Framework.Assert.That(() => { for (int k = 0; k < 200; k++) p.UpdateHudText(); }, Is.Not.AllocatingGCMemory(), "HUD");
            }
            finally
            {
                p.input = oldInput;
                b.RemoveScene(idx);
            }
            Assert.AreEqual(n0, b.SceneCount);
            Assert.AreEqual(-1, b.CurrentScene);
            Assert.IsTrue(b.RangeRoot.gameObject.activeSelf);
        }

        [UnityTest]
        public IEnumerator Umschalten_hin_und_zurueck_laesst_den_Parcours_unveraendert()
        {
            var b = B;
            var p = b.Player;
            var oldInput = p.input;
            var env = MakeEnv();
            int idx = b.AddScene(SceneFile.Parse(Room), env, Unlit());
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
            var env = MakeEnv();
            int idx = b.AddScene(SceneFile.Parse(Room), env, Unlit());
            Keyboard kb = null;
            bool added = false;
            try
            {
#if UNITY_EDITOR
                InputSystem.settings.editorInputBehaviorInPlayMode = InputSettings.EditorInputBehaviorInPlayMode.AllDeviceInputAlwaysGoesToGameView;
#endif
                InputSystem.settings.backgroundBehavior = InputSettings.BackgroundBehavior.IgnoreFocus;     // Stapelbetrieb: Fenster hat keinen Fokus
                kb = Keyboard.current;
                if (kb == null) { kb = InputSystem.AddDevice<Keyboard>(); added = true; }
                if (!kb.enabled) InputSystem.EnableDevice(kb);       // ohne Fokus schaltet das Input System Tastaturen ab
                int expect = -1;
                for (int round = 0; round < b.SceneCount + 1; round++)
                {
                    InputSystem.QueueStateEvent(kb, new KeyboardState(Key.L));
                    yield return null;
                    TestContext.WriteLine($"Runde {round}: Tastatur {kb.name} aktiv {kb.enabled}, aktuell {Keyboard.current == kb}, L gedrückt {kb.lKey.isPressed}, Szene {b.CurrentScene}");
                    InputSystem.QueueStateEvent(kb, new KeyboardState());
                    yield return null;
                    expect = expect + 1 >= b.SceneCount ? -1 : expect + 1;
                    Assert.AreEqual(expect, b.CurrentScene, $"nach {round + 1}× L");
                    if (round == 0) Object.DestroyImmediate(env);
                }
                Assert.AreEqual(-1, b.CurrentScene, "nach einer vollen Runde im Parcours");
            }
            finally
            {
                if (added) InputSystem.RemoveDevice(kb);
                b.RemoveScene(idx);
            }
        }

        [UnityTest]
        public IEnumerator Exportierte_Szenen_laden_und_Spieler_steht_auf_Boden()
        {
            var b = B;
            if (b.SceneCount == 0) Assert.Ignore("keine Szene exportiert");
            var p = b.Player;
            var oldInput = p.input;
            Idle(p);
            var before = Snapshot.Take(b);
            try
            {
                for (int i = 0; i < b.SceneCount; i++)
                {
                    b.ShowScene(i);
                    yield return null;
                    var L = b.LoadedSceneAt(i);
                    Assert.IsNotNull(L, b.SceneName(i));
                    Assert.IsTrue(L.root.Find("Umgebung").GetComponentsInChildren<Renderer>().Length > 0, $"{b.SceneName(i)}: Umgebung hat Renderer");
                    Assert.IsTrue(Physics.Raycast(L.spawnPos + Vector3.up, Vector3.down, out var h, 3f), $"{b.SceneName(i)}: Boden unter dem Startpunkt");
                    Assert.IsTrue(h.collider.transform.IsChildOf(L.root), $"{b.SceneName(i)}: Boden ist ein Collider der Szene");
                    for (int k = 0; k < 45; k++) yield return null;
                    Assert.That(p.transform.position.y, Is.InRange(L.spawnPos.y - 0.2f, L.spawnPos.y + 0.2f), $"{b.SceneName(i)}: Spieler bleibt am Boden");
                    Assert.AreEqual(L.data.targets.Length, L.targets.targets.Count, $"{b.SceneName(i)}: Ziele");
                }
                int steps = 0;
                do { b.NextScene(); steps++; yield return null; } while (b.CurrentScene != -1 && steps <= b.SceneCount + 1);
                Assert.AreEqual(-1, b.CurrentScene);
                before.AssertSame(Snapshot.Take(b), "Parcours danach");
            }
            finally
            {
                p.input = oldInput;
                if (b.CurrentScene != -1) b.ShowScene(-1);
            }
        }
    }
}
