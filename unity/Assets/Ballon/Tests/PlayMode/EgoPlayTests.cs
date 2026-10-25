// PlayMode: jede Aktion endet und meldet ihre Marker in der Reihenfolge der Daten; Spielablauf (Feuer, Nachladen, Zielen,
// Betrachten, Wegstecken, Sprint-Übergänge); die Szene startet und reagiert auf einen Eingabeablauf.
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
using UnityEngine.TestTools.Constraints;
using Is = UnityEngine.TestTools.Constraints.Is;   // NUnit-Is plus AllocatingGCMemory

namespace Ballon.Ego.Tests
{
    public class EgoPlayTests
    {
        const float Dt = 1f / 60f;
        static EgoFile _d;

        static EgoFile D => _d;

        static EgoIntent Idle => new EgoIntent { grounded = true };

        static EgoController Ready(List<(string, string)> markers = null)
        {
            var c = new EgoController(new EgoSolver(D));
            if (markers != null) c.Marker += (a, m) => markers.Add((a, m));
            c.ReadyNow();
            c.Tick(Dt, Idle);
            return c;
        }

        static void Run(EgoController c, EgoIntent i, float seconds)
        {
            for (float t = 0; t < seconds; t += Dt) c.Tick(Dt, i);
        }

        [UnitySetUp]
        public IEnumerator LoadScene()
        {
            if (_d == null)
            {
                SceneManager.LoadScene("Firstfeel");
                yield return null;
                yield return null;
                _d = Object.FindAnyObjectByType<Bootstrap>().D;
            }
        }

        [Test]
        public void Jede_Aktion_endet_mit_Markern_in_Reihenfolge()
        {
            foreach (var A in D.actions)
            {
                var c = new EgoController(new EgoSolver(D));
                var got = new List<string>();
                bool ended = false;
                c.Marker += (a, m) => { if (a == A.name && !ended) got.Add(m); };
                c.PlayAction(A.name, scripted: true, onEnd: () => ended = true);
                int ticks = 0;
                while (!ended && ticks < A.frames * 2 + 10)
                {
                    c.Tick(1f / 30f, Idle);
                    ticks++;
                    foreach (var v in c.output.segR.Concat(c.output.segL))
                        Assert.IsFalse(float.IsNaN(v.m03) || float.IsNaN(v.m00), $"{A.name}: NaN");
                }
                Assert.IsTrue(ended, $"{A.name} endet nicht");
                Assert.LessOrEqual(ticks, A.frames + 1, $"{A.name}: {ticks} Bilder statt {A.frames}");
                CollectionAssert.AreEqual(A.events.Select(e => e.name).ToList(), got, $"{A.name}: Marker {string.Join(",", got)}");
            }
        }

        [Test]
        public void Dauerfeuer_mit_Kadenz_leert_das_Magazin()
        {
            var c = Ready();
            int shots = 0;
            c.Shot += () => shots++;
            Assert.AreEqual(D.gameplay.magazine, c.ammo);
            Run(c, new EgoIntent { grounded = true, fire = true }, 1.0f);
            float perS = D.gameplay.rpm / 60f;
            Assert.That(shots, Is.InRange((int)perS - 1, (int)perS + 1), "Schüsse in 1 s");
            Run(c, new EgoIntent { grounded = true, fire = true }, 3.0f);
            Assert.AreEqual(D.gameplay.magazine, shots, "ein Magazin");
            Assert.AreEqual(0, c.ammo);
        }

        [Test]
        public void Leeres_Nachladen_und_taktisches_Nachladen()
        {
            var m = new List<(string, string)>();
            var c = Ready(m);
            c.ammo = 0;
            c.Tick(Dt, new EgoIntent { grounded = true, reload = true });
            Assert.AreEqual("reload_empty", c.ActionName);
            Run(c, Idle, D.Action("reload_empty").frames / 30f + 0.3f);
            CollectionAssert.AreEqual(new[] { "HandOff", "MagOut", "MagIn", "Chamber", "HandOn", "Ready" },
                m.Where(x => x.Item1 == "reload_empty").Select(x => x.Item2).ToArray());
            Assert.AreEqual(D.gameplay.magazine, c.ammo);
            Assert.AreEqual("idle_hip", c.ActionName);
            c.ammo = 7;
            c.Tick(Dt, new EgoIntent { grounded = true, reload = true });
            Assert.AreEqual("reload_tactical", c.ActionName);
            Run(c, Idle, D.Action("reload_tactical").frames / 30f + 0.3f);
            Assert.AreEqual(D.gameplay.magazine, c.ammo);
            // Abzug bei leerem Magazin lädt selbst nach
            c.ammo = 0;
            c.Tick(Dt, Idle);
            c.Tick(Dt, new EgoIntent { grounded = true, fire = true });
            Assert.AreEqual("reload_empty", c.ActionName);
        }

        [Test]
        public void Zielen_hin_und_zurueck()
        {
            var m = new List<(string, string)>();
            var c = Ready(m);
            Run(c, new EgoIntent { grounded = true, aim = true }, 0.6f);
            Assert.AreEqual(EgoController.Stance.Ads, c.CurrentStance);
            Assert.AreEqual(1f, c.adsWeight, 1e-4f);
            Assert.Contains(("aim_in", "Aimed"), m);
            Run(c, Idle, 0.6f);
            Assert.AreEqual(EgoController.Stance.Hip, c.CurrentStance);
            Assert.Contains(("aim_out", "Ready"), m);
            Assert.AreEqual(0f, c.adsWeight, 1e-4f);
            // Augenpunkt liegt im Zielen auf der Kameraachse
            var c2 = Ready();
            Run(c2, new EgoIntent { grounded = true, aim = true }, 0.8f);
            var eye = c2.output.weapon.MultiplyPoint3x4(BMath.V(D.Anchor("Socket_Eye").pos));
            Assert.That(new Vector2(eye.x, eye.z).magnitude, Is.LessThan(0.004f), $"Auge {eye:F4}");
        }

        /// <summary>Live (EgoController, wie im Spiel und im feel-MP4): Zielen aus der Hüfte bringt das Absehen ohne Überschwingen auf die
        /// Mitte und hängt nach 0,45 s nicht mehr nach (0.10; Destiny 2 hat beim Zielen kein Überschwingen).</summary>
        [Test]
        public void Zielen_live_ohne_Ueberschwingen()
        {
            var c = Ready();
            var ret = BMath.V(D.Anchor("Socket_Reticle").pos);
            float first = float.NaN, worst = 0, at045 = 0;
            for (int k = 0; k < 60; k++)                           // 1 s bei 60 Bildern/s
            {
                c.Tick(Dt, new EgoIntent { grounded = true, aim = true });
                var t = c.output.weapon.MultiplyPoint3x4(ret);
                float az = Mathf.Atan2(-t.x, -t.y) * Mathf.Rad2Deg;   // Blender-Kameraraum: rechts −X, vorn −Y
                if (float.IsNaN(first)) first = az;
                worst = Mathf.Max(worst, -Mathf.Sign(first) * az);
                if (k == 26) at045 = Mathf.Abs(az);
            }
            TestContext.WriteLine($"live aim_in: Start {first:0.00}°, Überschwingen {worst:0.00}°, Rest nach 0,45 s {at045:0.00}°");
            Assert.Less(worst, 0.3f, $"Absehen schwingt {worst:0.00}° über die Mitte");
            Assert.Less(at045, 1.0f, $"Absehen hängt nach 0,45 s {at045:0.00}° nach");
        }

        /// <summary>Live-Sprint (EgoController.LiveLayers): vertikal 2,9–3,4 Hochpunkte je Sekunde, Hochpunkte an den Seitenumkehren
        /// (U-Bogen wie Destiny 2, Motiongen REF 0.23), nicht in der Mitte.</summary>
        [Test]
        public void Sprint_live_im_Destiny_Rhythmus()
        {
            var c = Ready();
            var sprint = new EgoIntent { grounded = true, sprint = true, move = new Vector2(0, 1), speed01 = 1.6f };
            Run(c, sprint, 1.5f);                                  // in die Schleife, Gewichte eingeschwungen
            int n = 180;                                           // 3 s
            var x = new float[n]; var z = new float[n];
            for (int k = 0; k < n; k++)
            {
                c.Tick(Dt, sprint);
                var p = c.output.weapon.GetColumn(3);
                x[k] = p.x; z[k] = p.z;
            }
            float mx = 0, mz = 0;
            for (int k = 0; k < n; k++) { mx += x[k] / n; mz += z[k] / n; }
            int peaks = 0;
            float atSide = 0, atMid = 0; int nSide = 0, nMid = 0;
            float ax = 0;
            for (int k = 0; k < n; k++) ax = Mathf.Max(ax, Mathf.Abs(x[k] - mx));
            for (int k = 1; k < n - 1; k++)
            {
                if (z[k] > z[k - 1] && z[k] >= z[k + 1] && z[k] > mz) peaks++;
                float s = Mathf.Abs(x[k] - mx) / ax;
                if (s > 0.8f) { atSide += z[k] - mz; nSide++; }
                if (s < 0.2f) { atMid += z[k] - mz; nMid++; }
            }
            float hz = peaks / (n * Dt);
            atSide /= Mathf.Max(1, nSide); atMid /= Mathf.Max(1, nMid);
            TestContext.WriteLine($"live sprint: {hz:0.00} Hochpunkte/s, Höhe an den Seiten {atSide * 1000:0.0} mm, in der Mitte {atMid * 1000:0.0} mm");
            Assert.That(hz, Is.InRange(2.9f, 3.4f), "Schritte je Sekunde");
            Assert.Greater(atSide, atMid, "U-Bogen: oben an den Seitenumkehren, unten in der Mitte");
        }

        [Test]
        public void Betrachten_bricht_beim_Feuern_ab()
        {
            var c = Ready();
            c.Tick(Dt, new EgoIntent { grounded = true, inspect = true });
            Assert.AreEqual("inspect", c.ActionName);
            Run(c, Idle, 0.5f);
            int shots = 0;
            c.Shot += () => shots++;
            Run(c, new EgoIntent { grounded = true, fire = true }, 0.6f);
            Assert.AreNotEqual("inspect", c.ActionName);
            Assert.Greater(shots, 0, "nach dem Abbruch wird gefeuert");
            // ein einzelner R-Druck beim Betrachten bricht ab und lädt nach
            Run(c, Idle, 1.0f);
            c.Tick(Dt, new EgoIntent { grounded = true, inspect = true });
            Run(c, Idle, 0.3f);
            c.Tick(Dt, new EgoIntent { grounded = true, reload = true });
            Assert.AreEqual("reload_tactical", c.ActionName);
        }

        [Test]
        public void Wegstecken_beim_Nachladen_und_Ziehen()
        {
            var m = new List<(string, string)>();
            var c = Ready(m);
            c.ammo = 5;
            c.Tick(Dt, new EgoIntent { grounded = true, reload = true });
            Run(c, Idle, 0.15f);
            c.Tick(Dt, new EgoIntent { grounded = true, holster = true });
            Assert.AreEqual("reload_to_switch", c.ActionName);
            Run(c, Idle, D.Action("reload_to_switch").frames / 30f + 0.3f);
            Assert.IsTrue(c.Holstered);
            Assert.AreEqual(5, c.ammo, "Abbruch vor MagIn lässt die Munition");
            Assert.Contains(("reload_to_switch", "Cancel"), m);
            Assert.Contains(("reload_to_switch", "Holstered"), m);
            int shots = 0;
            c.Shot += () => shots++;
            Run(c, new EgoIntent { grounded = true, fire = true }, 0.3f);
            Assert.AreEqual(0, shots, "weggesteckt feuert nicht");
            c.Tick(Dt, new EgoIntent { grounded = true, draw = true });
            Assert.AreEqual("draw", c.ActionName);
            Run(c, Idle, D.Action("draw").frames / 30f + 0.3f);
            Assert.IsFalse(c.Holstered);
            Assert.Contains(("draw", "Ready"), m);
        }

        [Test]
        public void Sprint_Schleife_und_Uebergaenge()
        {
            var m = new List<(string, string)>();
            var c = Ready(m);
            var sprint = new EgoIntent { grounded = true, sprint = true, move = new Vector2(0, 1), speed01 = 1.6f };
            Run(c, sprint, 2.0f);
            Assert.AreEqual(EgoController.Stance.Sprint, c.CurrentStance);
            Assert.AreEqual("sprint", c.ActionName);
            var sk = D.Action("sprint").weapon;
            Assert.That(c.Frame, Is.InRange(sk[1].f, sk[2].f), "Schleife");
            Assert.Contains(("sprint", "SprintLoop"), m);
            var toAim = sprint;
            toAim.aim = true;
            c.Tick(Dt, toAim);
            Assert.AreEqual("sprint_to_aim", c.ActionName);
            Run(c, toAim, 0.8f);
            Assert.Contains(("sprint_to_aim", "Aimed"), m);
            Assert.AreEqual(EgoController.Stance.Ads, c.CurrentStance);
            Run(c, Idle, 0.6f);
            Run(c, sprint, 1.0f);
            int shots = 0;
            c.Shot += () => shots++;
            var toFire = sprint;
            toFire.fire = true;
            c.Tick(Dt, toFire);
            Assert.AreEqual("sprint_to_fire", c.ActionName);
            Assert.AreEqual(0, shots, "erst nach dem Marker Fire");
            Run(c, toFire, 0.6f);
            Assert.Contains(("sprint_to_fire", "Fire"), m);
            Assert.Greater(shots, 0);
            // Sprint loslassen beendet die Schleife über 38 → 48
            var c2 = Ready(m);
            Run(c2, sprint, 1.0f);
            Run(c2, Idle, 0.6f);
            Assert.AreEqual(EgoController.Stance.Hip, c2.CurrentStance);
            Assert.Contains(("sprint", "Ready"), m);
        }

        [Test]
        public void Ducken_Springen_Wandnaehe()
        {
            var m = new List<(string, string)>();
            var c = Ready(m);
            Run(c, new EgoIntent { grounded = true, crouch = true }, 0.5f);
            Assert.AreEqual(EgoController.Stance.Crouch, c.CurrentStance);
            Assert.Contains(("crouch", "Crouched"), m);
            Run(c, Idle, 0.5f);
            Assert.AreEqual(EgoController.Stance.Hip, c.CurrentStance);
            Run(c, new EgoIntent { grounded = false }, 0.6f);
            Assert.AreEqual(EgoController.Stance.Air, c.CurrentStance);
            Assert.Contains(("jump_land", "Air"), m);
            Run(c, Idle, 0.6f);
            Assert.Contains(("jump_land", "Land"), m);
            Run(c, new EgoIntent { grounded = true, nearWall = true }, 0.6f);
            Assert.AreEqual(EgoController.Stance.Lowered, c.CurrentStance);
            Assert.Contains(("lowered", "Lowered"), m);
            Run(c, Idle, 0.6f);
            Assert.Contains(("lowered", "Ready"), m);
        }

        [Test]
        public void Kein_GC_Muell_im_laufenden_Bild()
        {
            var c = Ready();
            var states = new[]
            {
                new EgoIntent { grounded = true, look = new Vector2(0.4f, -0.2f), move = new Vector2(0.3f, 1), speed01 = 1 },
                new EgoIntent { grounded = true, aim = true, fire = true, look = new Vector2(-0.3f, 0.1f) },
                new EgoIntent { grounded = true, sprint = true, move = new Vector2(0, 1), speed01 = 1.6f },
            };
            foreach (var st in states)
            {
                c.ammo = 1000;
                c.magSize = 1000;
                Run(c, st, 1.5f);                     // Haltung erreicht, Zwischenspeicher gefüllt
                var s = st;
                NUnit.Framework.Assert.That(() => { for (int k = 0; k < 30; k++) c.Tick(Dt, s); },
                    Is.Not.AllocatingGCMemory(), $"{c.ActionName}");
            }
            var demo = Bootstrap.DemoScript();                   // Eingabeablauf der Aufnahme
            demo.Read(Dt, 1);
            NUnit.Framework.Assert.That(() => { for (int k = 0; k < 300; k++) demo.Read(Dt, 1); }, Is.Not.AllocatingGCMemory(), "ScriptedInput");
        }

        [UnityTest]
        public IEnumerator Wandnaehe_im_Parcours_senkt_die_Waffe()
        {
            var p = Object.FindAnyObjectByType<Bootstrap>().Player;
            p.input = new ScriptedInput().Add(0, 100);
            p.deltaOverride = () => 1f / 30f;
            p.C.ReadyNow();
            p.Teleport(new Vector3(-6f, 0.01f, -2.95f), 0f);     // vor Säule 1 (Vorderseite bei z −2,4)
            for (int i = 0; i < 30; i++) yield return null;
            Assert.IsTrue(p.NearWall(), "Säule vor dem Kopf erkannt");
            Assert.AreEqual(EgoController.Stance.Lowered, p.C.CurrentStance);
            p.Teleport(new Vector3(0f, 0.01f, 1.5f), 0f);         // frei: zurück zur Hüfte
            for (int i = 0; i < 45; i++) yield return null;
            Assert.IsFalse(p.NearWall());
            Assert.AreEqual(EgoController.Stance.Hip, p.C.CurrentStance);
        }

        /// <summary>AgX-Durchgang im gerenderten Bild: lineare Werte einer unbeleuchteten Fläche kommen wie Blender-AgX an
        /// (0,18 → ≈ 0,44; ohne Abbildung würden 1 und 4 beide als 1,0 abgeschnitten).</summary>
        [UnityTest]
        public IEnumerator AgX_Tonwerte_im_Bild()
        {
            var b = Object.FindAnyObjectByType<Bootstrap>();
            var cam = b.Player.worldCam;
            var q = GameObject.CreatePrimitive(PrimitiveType.Quad);
            Object.Destroy(q.GetComponent<Collider>());
            var m = new Material(b.backdrop);
            q.GetComponent<Renderer>().sharedMaterial = m;
            q.transform.SetParent(cam.transform, false);
            q.transform.localPosition = new Vector3(0, 0, 0.5f);
            q.transform.localScale = new Vector3(3, 3, 1);
            var rt = Bootstrap.HdrTarget(64, 36, 1);
            var old = cam.targetTexture;
            cam.targetTexture = rt;
            var tex = new Texture2D(64, 36, TextureFormat.RGB24, false);
            var got = new Dictionary<float, float>();
            foreach (var v in new[] { 0.18f, 1f, 4f })
            {
                m.SetColor("_BaseColor", new Color(v, v, v, 1).gamma);    // linear v (Materialfarben sind Gamma-Werte)
                yield return null;                             // WaitForEndOfFrame kommt im Stapelbetrieb nicht
                yield return null;
                Bootstrap.ReadBack(rt, tex);
                got[v] = tex.GetPixel(12, 28).r;               // oben links: kein Viewmodel davor
                TestContext.WriteLine($"Wert {v}: Mitte {tex.GetPixel(32, 18)} oben links {tex.GetPixel(12, 28)} unten rechts {tex.GetPixel(52, 6)}");
            }
            var vd = UnityEngine.Rendering.Universal.CameraExtensions.GetUniversalAdditionalCameraData(b.Player.viewCam);
            TestContext.WriteLine($"HDR {cam.allowHDR}, rt {rt.format}, Stapel {vd.renderType}, Quad-Ebene {q.layer}, Maske {cam.cullingMask}, " +
                                  $"Nebel {RenderSettings.fog} {RenderSettings.fogStartDistance}, Kamera {cam.transform.position} → {cam.transform.forward}");
            cam.targetTexture = old;
            Object.Destroy(q);
            Assert.AreEqual(0.461f, got[0.18f], 0.02f, "Mittelgrau (Blender AgX MHC: 0,18 → 0,461)");
            Assert.That(got[1f], Is.InRange(0.65f, 0.92f), "1,0 wird abgebildet, nicht abgeschnitten");
            Assert.Greater(got[4f], got[1f] + 0.03f, "Spitzlichter über 1 bleiben unterscheidbar");
            Assert.Less(got[4f], 0.995f);
        }

        [UnityTest]
        public IEnumerator Skin_wechseln_nur_an_der_Waffe()
        {
            var p = Object.FindAnyObjectByType<Bootstrap>().Player;
            Assert.AreEqual(8, p.skins.Length);
            var arm = p.rig.SegR("hand").GetComponentInChildren<Renderer>().sharedMaterial;
            var before = p.rig.WeaponAtlasMaterial;
            p.SetSkin(3);
            yield return null;
            Assert.AreSame(p.skins[3], p.rig.WeaponAtlasMaterial, "Waffe trägt den Skin");
            Assert.AreSame(arm, p.rig.SegR("hand").GetComponentInChildren<Renderer>().sharedMaterial, "Arme bleiben");
            p.SetSkin(0);
            Assert.AreSame(before, p.rig.WeaponAtlasMaterial);
        }

        [UnityTest]
        public IEnumerator Szene_startet_und_spielt_den_Ablauf()
        {
            var b = Object.FindAnyObjectByType<Bootstrap>();
            Assert.IsNotNull(b, "Bootstrap in der Szene");
            var p = b.Player;
            Assert.IsNotNull(p);
            Assert.IsTrue(p.rig.weaponRoot.gameObject.activeInHierarchy);
            Assert.AreEqual(Bootstrap.ViewmodelLayer, p.rig.weaponRoot.gameObject.layer);
            int shots = 0;
            p.C.Shot += () => shots++;
            p.C.ReadyNow();
            p.C.ammo = 9;
            p.input = Bootstrap.DemoScript();
            p.deltaOverride = () => 1f / 30f;
            for (int i = 0; i < 30 * 8 && i < 1000; i++) yield return null;
            Assert.Greater(shots, 0, "Feuerstoß");
            Assert.IsTrue(p.log.Any(l => l.Contains("reload_empty MagIn")), "leeres Nachladen: " + string.Join(" | ", p.log));
            Assert.IsTrue(p.log.Any(l => l.Contains("inspect Start")), "Betrachten");
            Assert.Greater(p.C.ammo, 0);
        }
    }
}
