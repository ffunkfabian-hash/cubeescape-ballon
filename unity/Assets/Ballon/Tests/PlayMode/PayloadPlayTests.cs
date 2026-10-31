// PlayMode (0.34 „Payload“): Wirkung der Waffen im Spieler (Projektile und Explosionen, Strahlen, Streuschuss, Einschläge, Löcher) und
// am Modell (Trommelschritt, Hülsen beim Nachladen, Gurtglieder, Füllstand von Gurt, Zählfenster und Trommel). Virtuelle Zeit (1/30 s
// je Bild über deltaOverride, Partikel über WeaponFx.Tick). Gegenprobe: BALLON_PAYLOAD_OFF=1 – dann scheitern alle Tests hier.
using System.Collections;
using System.Linq;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
using UnityEngine.TestTools.Constraints;
using Is = UnityEngine.TestTools.Constraints.Is;

namespace Ballon.Ego.Tests
{
    public class PayloadPlayTests
    {
        const float Dt = 1f / 30f;
        static EgoIntent Idle => new EgoIntent { grounded = true };
        static EgoIntent Fire => new EgoIntent { grounded = true, fire = true };

        [UnitySetUp]
        public IEnumerator LoadScene()
        {
            if (Object.FindAnyObjectByType<Bootstrap>() == null)
            {
                SceneManager.LoadScene("Firstfeel");
                yield return null;
                yield return null;
            }
            var p = Object.FindAnyObjectByType<Bootstrap>().Player;
            p.UseWeapon(0);
            p.fx?.Clear();
        }

        static Bootstrap Boot => Object.FindAnyObjectByType<Bootstrap>();

        static int Slot(string type)
        {
            int k = System.Array.FindIndex(Boot.Solvers, s => s.D.gameplay.weapon_type == type);
            Assert.GreaterOrEqual(k, 0, $"Klasse {type} fehlt");
            return k;
        }

        static EgoFile Class(string type) => Boot.Solvers[Slot(type)].D;

        /// <summary>Spieler mit der Waffe der Klasse bereit am Start, Blick +Z, Wand d Meter voraus (20 × 8 m); feste Bildzeit 1/30 s.</summary>
        static EgoPlayer Setup(string type, float d, out GameObject wall)
        {
            var p = Boot.Player;
            Assert.IsNotNull(p.fx, "Wirkung der Waffen (WeaponFx) fehlt");
            p.UseWeapon(Slot(type));
            p.C.ReadyNow();
            p.C.ammo = p.C.magSize;
            p.Teleport(new Vector3(0f, 0.01f, 1.6f), 0f);
            p.input = new ScriptedInput().Add(0, 1000);
            p.deltaOverride = () => Dt;
            var cam = p.worldCam.transform;
            wall = GameObject.CreatePrimitive(PrimitiveType.Cube);
            wall.name = "Testwand";
            wall.transform.SetPositionAndRotation(new Vector3(0, cam.position.y, cam.position.z + d), Quaternion.identity);
            wall.transform.localScale = new Vector3(20f, 8f, 0.2f);
            Physics.SyncTransforms();                        // sonst sieht der erste Strahl die Wand noch im Ursprung (bis zum nächsten Physikschritt)
            p.fx.Clear();
            return p;
        }

        static void Done(EgoPlayer p, GameObject wall)
        {
            p.input = new ScriptedInput().Add(0, 1000);
            p.deltaOverride = null;
            p.fx?.Clear();
            if (wall != null) wall.SetActive(false);         // Löcher hängen an der Wand und bleiben im Pool
            p.C.ReadyNow();
            p.C.ammo = p.C.magSize;
            p.UseWeapon(0);
        }

        // ------------------------------------------------------------------------------------------------ Projektile und Explosionen
        /// <summary>Granatwerfer: ein Schuss startet eine sichtbare Granate an der Mündung, die mit gameplay.fx.speed_mps fliegt und mit
        /// gravity_mps2 fällt; an der Wand (12 m) explodiert sie: Blitz und Feuer (Licht), Druckring, Licht, Funken, Rauch, Brandfleck. Aus
        /// dem Lauf steigt Rauch. Weiterrechnen der Wirkung (Flug, Partikel) ohne Speicher je Bild.</summary>
        [UnityTest]
        public IEnumerator Granatwerfer_Granate_fliegt_im_Bogen_und_explodiert()
        {
            var p = Setup("grenade_launcher", 12f, out var wall);
            var F = p.C.S.D.gameplay.fx;
            try
            {
                Assert.AreEqual("projectile", F.kind);
                Assert.IsTrue(F.Explodes);
                yield return null;
                p.input = new ScriptedInput().Add(0, 0.1f, hold: "fire").Add(0.1f, 1000);
                for (int f = 0; f < 60 && p.fx.launched == 0; f++) yield return null;
                Assert.AreEqual(1, p.fx.launched, "Granate gestartet");
                Assert.IsTrue(p.fx.FirstProjectile(out var p0, out var v0), $"Granate fliegt (Explosionen {p.fx.explosions}, Einschläge {p.fx.impacts}, steckt {p.fx.ProjectilesStuck})");
                var muzzle = p.worldCam.WorldToViewportPoint(p.fx.LastLaunch);
                var want = p.viewCam.WorldToViewportPoint(p.rig.AnchorWorld("Socket_Muzzle"));
                TestContext.WriteLine($"Start im Bild {muzzle.x:0.000}/{muzzle.y:0.000}, Mündung {want.x:0.000}/{want.y:0.000}, v {v0.magnitude:0.0} m/s");
                Assert.AreEqual(F.speed_mps, v0.magnitude, 0.5f, "Startgeschwindigkeit");
                Assert.Less(Vector2.Distance(muzzle, want), 0.08f, "Granate erscheint an der Mündung (Bildlage; der Kick bewegt die Waffe danach im selben Bild)");
                Assert.That(() => p.fx.Tick(Dt, p.arsenal.Active, false, ~(1 << EgoPlayer.PlayerLayer | 1 << Bootstrap.ViewmodelLayer)),
                            Is.Not.AllocatingGCMemory(), "Flug und Partikel ohne Speicher");
                yield return null;
                Assert.IsTrue(p.fx.FirstProjectile(out var p1, out var v1));
                Assert.Less(v1.y, v0.y - 0.5f * F.gravity_mps2 * Dt, "Fallkurve: senkrechte Geschwindigkeit nimmt ab");
                Assert.Greater(p.fx.MuzzleSmoke(p.arsenal.Active), 0, "Rauch aus dem Lauf");
                for (int f = 0; f < 30 && p.fx.explosions == 0; f++) yield return null;
                Assert.AreEqual(1, p.fx.explosions, "Explosion an der Wand");
                Assert.AreEqual(0, p.fx.ProjectilesFlying);
                Assert.AreEqual(1, p.fx.RingsShown, "Druckring");
                Assert.AreEqual(1, p.fx.LightsShown, "Licht");
                Assert.AreEqual(1, p.fx.ScorchShown, "Brandfleck");
                Assert.Greater(p.fx.Sparks, 10, "Funken");
                Assert.Greater(p.fx.Smoke, 5, "Rauch");
                Assert.Greater(p.fx.Glow, 0, "Blitz und Feuer");
                Assert.That(() => p.fx.Tick(Dt, p.arsenal.Active, false, ~(1 << EgoPlayer.PlayerLayer | 1 << Bootstrap.ViewmodelLayer)),
                            Is.Not.AllocatingGCMemory(), "Ring, Licht, Rauch, Brandfleck ohne Speicher");
                for (int f = 0; f < 20; f++) yield return null;
                Assert.AreEqual(0, p.fx.RingsShown, "Ring nach ring_s aus");
                Assert.AreEqual(0, p.fx.LightsShown, "Licht nach light_s aus");
                Assert.Greater(p.fx.Smoke, 0, "Rauch hält länger");
            }
            finally { Done(p, wall); }
        }

        /// <summary>Raketenwerfer: die Rakete fliegt gerade (Fall 0) als Glühpunkt ohne Rauchzopf (0.34.1, REF 0.36), aus dem Rohr steigt
        /// Rauch, an der Wand (15 m) die Explosion.</summary>
        [UnityTest]
        public IEnumerator Raketenwerfer_Rakete_gerade_ohne_Rauchzopf_und_Explosion()
        {
            var p = Setup("rocket_launcher", 15f, out var wall);
            var F = p.C.S.D.gameplay.fx;
            try
            {
                Assert.AreEqual(0, F.gravity_mps2, "Rakete ohne Fall");
                yield return null;
                p.input = new ScriptedInput().Add(0, 0.1f, hold: "fire").Add(0.1f, 1000);
                for (int f = 0; f < 60 && p.fx.launched == 0; f++) yield return null;
                Assert.AreEqual(1, p.fx.launched);
                Assert.IsTrue(p.fx.FirstProjectile(out _, out var v0));
                int smoke0 = p.fx.Smoke;
                for (int f = 0; f < 5; f++) yield return null;
                Assert.IsTrue(p.fx.FirstProjectile(out _, out var v1), "Rakete fliegt noch");
                Assert.AreEqual(v0.y, v1.y, 1e-3f, "gerade Bahn");
                Assert.AreEqual(0, p.fx.Smoke, "kein Rauchzopf (trail_life_s 0)");
                Assert.Greater(p.fx.Glow, 0, "Glühpunkt am Heck");
                Assert.Greater(p.fx.MuzzleSmoke(p.arsenal.Active), 0, "Rauch aus dem Rohr");
                for (int f = 0; f < 30 && p.fx.explosions == 0; f++) yield return null;
                Assert.AreEqual(1, p.fx.explosions);
                Assert.AreEqual(1, p.fx.RingsShown);
            }
            finally { Done(p, wall); }
        }

        // ------------------------------------------------------------------------------------------------ Strahlen
        /// <summary>Spurgewehr: solange der Abzug zieht, läuft ein Strahl von der Mündung (gleicher Bildpunkt wie Socket_Muzzle in der
        /// Viewmodel-Kamera) bis zum Einschlag an der Wand; dort Licht und Funken, an der Waffe Mündungslicht; losgelassen ist er weg.</summary>
        [UnityTest]
        public IEnumerator Spurgewehr_Dauerstrahl_vom_Lauf_zum_Einschlag()
        {
            var p = Setup("trace_rifle", 8f, out var wall);
            try
            {
                yield return null;
                p.input = new ScriptedInput().Add(0, 0.6f, hold: "fire").Add(0.6f, 1000);
                for (int f = 0; f < 12; f++) yield return null;
                Assert.IsTrue(p.fx.BeamShown, "Strahl sichtbar beim Feuern");
                var s = p.worldCam.WorldToViewportPoint(p.fx.BeamStart);
                var m = p.viewCam.WorldToViewportPoint(p.rig.AnchorWorld("Socket_Muzzle"));
                TestContext.WriteLine($"Strahl ab {s.x:0.000}/{s.y:0.000}, Mündung {m.x:0.000}/{m.y:0.000}, Ende z {p.fx.BeamEnd.z:0.00}");
                Assert.Less(Vector2.Distance(s, m), 0.01f, "Strahl beginnt an der Mündung");
                Assert.AreEqual(wall.transform.position.z - 0.1f, p.fx.BeamEnd.z, 0.05f, "Strahl endet an der Wand");
                Assert.Greater(p.fx.Glow, 0, "Licht am Einschlag");
                Assert.Greater(p.fx.MuzzleGlow(p.arsenal.Active), 0, "Mündungslicht");
                Assert.That(() => p.fx.Tick(Dt, p.arsenal.Active, true, ~(1 << EgoPlayer.PlayerLayer | 1 << Bootstrap.ViewmodelLayer)),
                            Is.Not.AllocatingGCMemory(), "Dauerstrahl ohne Speicher je Bild");
                for (int f = 0; f < 12; f++) yield return null;
                Assert.IsFalse(p.fx.BeamShown, "losgelassen: kein Strahl");
            }
            finally { Done(p, wall); }
        }

        /// <summary>Fusionsgewehr: nach dem Aufladen fliegt je Strahl der Salve ein Bolzen (burst_shots), sichtbar fliegend, Einschlag
        /// bei der Ankunft (nicht im Schussbild).</summary>
        [UnityTest]
        public IEnumerator Fusion_Salve_aus_Bolzen()
        {
            var p = Setup("fusion_rifle", 20f, out var wall);
            var G = p.C.S.D.gameplay;
            try
            {
                yield return null;
                p.input = new ScriptedInput().Add(0, 1.2f, hold: "fire").Add(1.2f, 1000);
                int seen = 0;
                for (int f = 0; f < 40 && p.fx.bolts < G.burst_shots; f++)
                {
                    yield return null;
                    seen = Mathf.Max(seen, p.fx.LinesShown);
                }
                Assert.AreEqual(G.burst_shots, p.fx.bolts, "ein Bolzen je Strahl der Salve");
                Assert.Greater(seen, 0, "Bolzen sichtbar im Flug");
                for (int f = 0; f < 15; f++) yield return null;
                Assert.GreaterOrEqual(p.fx.impacts, G.burst_shots, "jeder Bolzen schlägt ein");
                Assert.AreEqual(0, p.fx.LinesShown, "alle angekommen");
            }
            finally { Done(p, wall); }
        }

        /// <summary>Lineares Fusionsgewehr: ein scharfer Strahl je Schuss, sichtbar beam_s, danach weg; Mündungslicht beim Schuss.</summary>
        [UnityTest]
        public IEnumerator Lineare_Fusion_ein_scharfer_Strahl()
        {
            var p = Setup("linear_fusion_rifle", 12f, out var wall);
            var F = p.C.S.D.gameplay.fx;
            try
            {
                yield return null;
                p.input = new ScriptedInput().Add(0, 1.0f, hold: "fire").Add(1.0f, 1000);
                for (int f = 0; f < 40 && p.fx.rails == 0; f++) yield return null;
                Assert.AreEqual(1, p.fx.rails, "ein Strahl");
                Assert.AreEqual(1, p.fx.LinesShown);
                Assert.Greater(p.fx.MuzzleGlow(p.arsenal.Active), 0, "Mündungslicht");
                Assert.GreaterOrEqual(p.fx.impacts, 1, "Einschlag sofort");
                for (int f = 0; f < Mathf.CeilToInt(F.beam_s / Dt) + 2; f++) yield return null;
                Assert.AreEqual(0, p.fx.LinesShown, "nach beam_s aus");
            }
            finally { Done(p, wall); }
        }

        /// <summary>Bogen: Spannen, Lösen – Lichtpuls an der Auflage, der Pfeil fliegt (Fall), schlägt ein und steckt stick_s.</summary>
        [UnityTest]
        public IEnumerator Bogen_Pfeil_loest_fliegt_und_steckt()
        {
            var p = Setup("combat_bow", 10f, out var wall);
            var F = p.C.S.D.gameplay.fx;
            try
            {
                yield return null;
                p.input = new ScriptedInput().Add(0, 1.2f, hold: "fire").Add(1.2f, 1000);
                int glow = 0;
                for (int f = 0; f < 60 && p.fx.launched == 0; f++) yield return null;
                Assert.AreEqual(1, p.fx.launched, "Pfeil beim Lösen");
                glow = p.fx.MuzzleGlow(p.arsenal.Active);
                Assert.Greater(glow, 0, "Lichtpuls beim Lösen");
                for (int f = 0; f < 15 && p.fx.ProjectilesStuck == 0; f++) yield return null;
                Assert.AreEqual(1, p.fx.ProjectilesStuck, "Pfeil steckt");
                Assert.GreaterOrEqual(p.fx.impacts, 1, "Einschlag");
                for (int f = 0; f < Mathf.CeilToInt(F.stick_s / Dt) + 3; f++) yield return null;
                Assert.AreEqual(0, p.fx.ProjectilesStuck, "nach stick_s weg");
            }
            finally { Done(p, wall); }
        }

        // ------------------------------------------------------------------------------------------------ Einschläge
        /// <summary>Schrotflinte (0.34.1, REF 0.36: im Bild ein Einschlag je Schuss, Nutzerentscheid 181): ein Schuss zeigt EINEN dichten
        /// Einschlag (Funkenball, Rauchball) mit einem Loch; die 12 Kugeln liegen im Streukegel (cone_deg), gestreut statt in einem Punkt,
        /// und treffen (eine Scheibe neben der Mitte zählt als Treffer).</summary>
        [UnityTest]
        public IEnumerator Schrot_ein_Einschlag_je_Schuss_Kugeln_im_Kegel()
        {
            var p = Setup("shotgun", 8f, out var wall);
            var F = p.C.S.D.gameplay.fx;
            GameObject side = null;
            try
            {
                Assert.AreEqual(12, F.pellets);
                Assert.AreEqual(1, F.shot_impacts, "ein sichtbarer Einschlag je Schuss");
                var cam = p.worldCam.transform;
                float widest = 0;
                for (int i = 1; i < F.pellets; i++)
                    widest = Mathf.Max(widest, Vector3.Angle(cam.forward, EgoPlayer.PelletDir(cam.forward, cam.up, cam.right, i, F.pellets, F.cone_deg, 17f)));
                Assert.LessOrEqual(widest, F.cone_deg + 1e-3f, "Kugeln im Kegel");
                Assert.Greater(widest, 0.5f * F.cone_deg, "gestreut, nicht ein Punkt");
                // Scheibe neben der Mitte (außerhalb der mittleren Kugel, im äußeren Ring): nur die Kugeln treffen sie
                side = GameObject.CreatePrimitive(PrimitiveType.Cube);
                side.transform.SetPositionAndRotation(cam.position + cam.forward * 6f + cam.right * 0.36f, cam.rotation);
                side.transform.localScale = new Vector3(0.28f, 1.2f, 0.05f);   // x 0,22–0,50 m: äußerer Ring (0,31 m), nicht die Mitte
                side.AddComponent<RangeTarget>();
                Physics.SyncTransforms();
                yield return null;
                int holes0 = wall.transform.childCount, hits0 = p.hits;
                p.input = new ScriptedInput().Add(0, 0.1f, hold: "fire").Add(0.1f, 1000);
                for (int f = 0; f < 60 && p.fx.impacts == 0; f++) yield return null;
                TestContext.WriteLine($"Schrot: {p.fx.impacts} Einschlag, {wall.transform.childCount - holes0} Loch, Funken {p.fx.Sparks}, Treffer {p.hits - hits0}");
                Assert.AreEqual(1, p.fx.impacts, "ein Einschlag je Schuss");
                Assert.AreEqual(1, wall.transform.childCount - holes0, "ein Loch");
                Assert.GreaterOrEqual(p.fx.Sparks, 20, "dichter Funkenball");
                Assert.AreEqual(1, p.hits - hits0, "die Kugeln treffen die Scheibe neben der Mitte (einmal gezählt)");
            }
            finally
            {
                if (side != null) side.SetActive(false);
                Done(p, wall);
            }
        }

        /// <summary>Einschlag je Kugelklasse (Automatik, Scout, MP, Impuls, Handfeuerwaffe, Seitenwaffe, Scharfschütze, MG): Funken,
        /// Staub, Lichtpunkt und ein Loch; Handfeuerwaffe und Scharfschütze mit dem schweren Stil. Das Loch blendet nach life_s aus.</summary>
        [UnityTest]
        public IEnumerator Einschlag_Funken_Staub_Loch_und_Ausblenden()
        {
            foreach (var type in new[] { "auto_rifle", "scout_rifle", "submachine_gun", "pulse_rifle", "hand_cannon", "sidearm", "sniper_rifle", "machine_gun" })
            {
                var p = Setup(type, 2.5f, out var wall);           // vor den Scheiben und der Brüstung
                var F = p.C.S.D.gameplay.fx;
                try
                {
                    Assert.AreEqual("hitscan", F.kind, type);
                    Assert.AreEqual(type == "hand_cannon" || type == "sniper_rifle" ? "heavy" : "bullet", F.impact, type);
                    yield return null;
                    p.input = new ScriptedInput().Add(0, 0.05f, hold: "fire").Add(0.05f, 1000);
                    for (int f = 0; f < 60 && p.fx.impacts == 0; f++) yield return null;
                    Assert.GreaterOrEqual(p.fx.impacts, 1, $"{type}: Einschlag");
                    Assert.Greater(p.fx.Sparks, 0, $"{type}: Funken (Staub {p.fx.Dust}, Licht {p.fx.Glow}, Einschläge {p.fx.impacts})");
                    Assert.Greater(p.fx.Dust, 0, $"{type}: Staub");
                    var hp = p.fx.HoleTransform(0).parent;
                    Assert.IsTrue(hp == wall.transform, $"{type}: Loch an der Wand (hängt an {(hp != null ? hp.name : "nichts")}, Schüsse {p.C.shots})");
                    Assert.AreEqual(1f, p.fx.HoleAlpha(0), 1e-4f, $"{type}: Loch deckt");
                    if (type == "machine_gun")                      // Ausblenden vor dem Aufräumen (Clear blendet alle Löcher aus)
                    {
                        var q = p;
                        var Dc = q.C.S.D.motion.payload.decal;
                        int mask = ~(1 << EgoPlayer.PlayerLayer | 1 << Bootstrap.ViewmodelLayer);
                        for (float t = 0; t < Dc.life_s - Dc.fade_s * 0.5f; t += 0.25f) q.fx.Tick(0.25f, 0, false, mask);
                        float mid = q.fx.HoleAlpha(0);
                        for (float t = 0; t < Dc.fade_s; t += 0.25f) q.fx.Tick(0.25f, 0, false, mask);
                        TestContext.WriteLine($"Loch: nach {Dc.life_s - Dc.fade_s * 0.5f:0.0} s Deckung {mid:0.00}, nach {Dc.life_s + Dc.fade_s * 0.5f:0.0} s {q.fx.HoleAlpha(0):0.00}");
                        Assert.That(mid, Is.InRange(0.2f, 0.8f), "blendet aus");
                        Assert.AreEqual(0, q.fx.HoleAlpha(0), "ausgeblendet");
                        Assert.LessOrEqual(q.fx.HoleCount, Dc.max, "Pool hält die Obergrenze");
                    }
                }
                finally { Done(p, wall); }
            }
        }

        // ------------------------------------------------------------------------------------------------ Modell: Hülsen, Füllstand
        /// <summary>Handfeuerwaffe: die Trommel dreht nach jedem Schuss eine Kammer weiter (index 0 → 1 in IndexFrames), beim Schuss fällt
        /// keine Hülse; beim Nachladen (Marker Eject) fallen so viele Hülsen, wie verschossen sind, aus der ausgeschwenkten Trommel.</summary>
        [Test]
        public void Handfeuerwaffe_Trommel_dreht_je_Schuss_Huelsen_beim_Nachladen()
        {
            var HC = Class("hand_cannon");
            CollectionAssert.AreEqual(new[] { "cylinder" }, HC.weapon.live.index);
            Assert.AreEqual("reload", HC.weapon.eject.on);
            Assert.AreEqual("cylinder", HC.weapon.eject.part);
            var c = new EgoController(new EgoSolver(HC));
            c.ReadyNow();
            for (int k = 0; k < 10; k++) c.Tick(Dt, Idle);
            long sh0 = c.shellsEjected;
            for (int s = 0; s < 4; s++)
            {
                c.Tick(Dt, Fire);
                c.output.mech.TryGetValue("cylinder", out float at);
                Assert.AreEqual(0f, at, 0.01f, "im Schussbild steht die Kammer");
                for (int k = 0; k < 4; k++) c.Tick(Dt, Idle);
                c.output.mech.TryGetValue("cylinder", out float after);
                Assert.AreEqual(1f, after, 0.01f, "eine Kammer weiter");
                for (int k = 0; k < 12; k++) c.Tick(Dt, Idle);
            }
            Assert.AreEqual(4, c.shots);
            Assert.AreEqual(sh0, c.shellsEjected, "keine Hülse beim Schuss");
            c.Tick(Dt, new EgoIntent { grounded = true, reload = true });
            int most = 0;
            for (int k = 0; k < 120 && c.Busy; k++)
            {
                c.Tick(Dt, Idle);
                most = Mathf.Max(most, c.output.shellCount);
            }
            TestContext.WriteLine($"Handfeuerwaffe: {c.reloadShells} Hülsen beim Nachladen, höchstens {most} zugleich");
            Assert.AreEqual(4, c.reloadShells, "je verschossene Kammer eine Hülse");
            Assert.AreEqual(4, most, "fallen zusammen");
            Assert.AreEqual(c.magSize, c.ammo);
        }

        /// <summary>MG: je Schuss eine Hülse und ein Gurtglied, der Gurt zieht nach (index belt); der Gurt leert sich von unten (Sätze aus
        /// bei weniger Patronen), das Zählfenster zeigt den Anteil (Zellen), nach dem Nachladen ist alles voll. Im Spieler zeigt das Modell
        /// den Füllstand (Renderer aus).</summary>
        [UnityTest]
        public IEnumerator MG_Glieder_Gurtvorschub_und_Fuellstand()
        {
            var MG = Class("machine_gun");
            Assert.IsTrue(MG.weapon.eject.links.enabled, "Gliederauswurf");
            CollectionAssert.AreEqual(new[] { "belt" }, MG.weapon.live.index);
            Assert.AreEqual("line", MG.weapon.live.rounds.mode);
            Assert.AreEqual(5, MG.weapon.live.fill.Length);
            var c = new EgoController(new EgoSolver(MG));
            c.ReadyNow();
            for (int k = 0; k < 10; k++) c.Tick(Dt, Idle);
            c.Tick(Dt, Fire);
            Assert.GreaterOrEqual(c.output.shellCount, 1);
            Assert.AreEqual(c.output.shellCount, c.output.linkCount, "Glied mit jeder Hülse");
            c.Tick(Dt, Idle);
            c.Tick(Dt, Idle);
            c.output.mech.TryGetValue("belt", out float belt);
            Assert.AreEqual(1f, belt, 0.01f, "Gurt eine Gliedteilung nachgezogen");
            c.ammo = 2;
            c.Tick(Dt, Idle);
            CollectionAssert.AreEqual(new[] { true, true, false, false }, c.output.roundOn, "Gurt leert sich von unten");
            c.ammo = c.magSize / 2;
            c.Tick(Dt, Idle);
            var cells = MG.weapon.live.fill.Select(q => c.output.mech[q]).ToArray();
            TestContext.WriteLine($"Zählzellen halb voll: {string.Join(" ", cells.Select(v => v.ToString("0.00")))}");
            Assert.AreEqual(1f, cells[0], 1e-4f);
            Assert.AreEqual(1f, cells[1], 1e-4f);
            Assert.That(cells[2], Is.InRange(0.3f, 0.7f));
            Assert.AreEqual(0f, cells[4], 1e-4f);
            c.ammo = 0;
            c.Tick(Dt, Idle);
            Assert.IsTrue(c.output.roundOn.All(b => !b), "leer: kein Gurt");
            c.Tick(Dt, new EgoIntent { grounded = true, reload = true });
            for (int k = 0; k < 400 && c.Busy; k++) c.Tick(Dt, Idle);
            Assert.AreEqual(c.magSize, c.ammo);
            Assert.IsTrue(c.output.roundOn.All(b => b), "nachgeladen: voller Gurt");
            // im Spieler am Modell
            var p = Setup("machine_gun", 6f, out var wall);
            try
            {
                p.C.ammo = 1;
                yield return null;
                yield return null;
                Assert.IsTrue(p.rig.RoundShown(0));
                Assert.IsFalse(p.rig.RoundShown(1), "Modell: zweite Gurtpatrone aus");
                Assert.AreEqual(0f, p.rig.GlowLevel("counter_cell_5"), 1e-4f, "Modell: letzte Zelle dunkel");
                p.C.ammo = p.C.magSize;
                yield return null;
                Assert.IsTrue(p.rig.RoundShown(1));
                Assert.AreEqual(1f, p.rig.GlowLevel("counter_cell_5"), 1e-4f);
            }
            finally { Done(p, wall); }
        }

        /// <summary>Granatwerfer: die Trommel zeigt je Kammer geladen oder leer. Ein Schuss leert die Laufkammer; springt die Trommel nach
        /// fire_cycle zurück, liegt die leere Kammer eine weiter. Drei Schuss → drei leere Kammern; Nachladen füllt Kammer für Kammer, voll
        /// sind alle sichtbar.</summary>
        [Test]
        public void Granatwerfer_Trommel_zeigt_geladene_und_leere_Kammern()
        {
            var GL = Class("grenade_launcher");
            Assert.AreEqual("drum", GL.weapon.live.rounds.mode);
            Assert.AreEqual(6, GL.weapon.live.rounds.sets.Length);
            var c = new EgoController(new EgoSolver(GL));
            c.ReadyNow();
            for (int k = 0; k < 10; k++) c.Tick(Dt, Idle);
            Assert.IsTrue(c.output.roundOn.All(b => b), "voll");
            c.Tick(Dt, Fire);
            c.Tick(Dt, Idle);
            Assert.IsFalse(c.output.roundOn[0], "Laufkammer nach dem Schuss leer");
            Assert.That(() => { for (int k = 0; k < 12; k++) c.Tick(Dt, Idle); }, Is.Not.AllocatingGCMemory(),
                        "Trommel dreht weiter, Füllstand rückt mit – ohne Speicher");
            for (int k = 0; k < 30 && c.Busy; k++) c.Tick(Dt, Idle);
            Assert.IsFalse(c.output.roundOn[1], "nach dem Zurückspringen: leere Kammer eine weiter");
            Assert.IsTrue(c.output.roundOn[0], "nächste Granate im Lauf");
            for (int s = 0; s < 2; s++)
            {
                for (int k = 0; k < 15; k++) c.Tick(Dt, Idle);
                c.Tick(Dt, Fire);
                for (int k = 0; k < 30 && c.Busy; k++) c.Tick(Dt, Idle);
            }
            Assert.AreEqual(3, c.ammo);
            Assert.AreEqual(3, c.output.roundOn.Count(b => b), "drei geladen");
            c.Tick(Dt, new EgoIntent { grounded = true, reload = true });
            int prev = 3;
            bool grew = true;
            for (int k = 0; k < 900 && c.Busy; k++)
            {
                c.Tick(Dt, Idle);
                if (c.ActionName == "reload_end") continue;
                int n = c.output.roundOn.Count(b => b);
                if (n < prev - 1) grew = false;
                prev = n;
            }
            for (int k = 0; k < 5; k++) c.Tick(Dt, Idle);
            Assert.IsTrue(grew, "Füllstand sinkt beim Nachladen nicht");
            Assert.AreEqual(c.magSize, c.ammo);
            Assert.IsTrue(c.output.roundOn.All(b => b), "voll nachgeladen");
            // teilweises Nachladen (3 → 4, Abbruch mit dem Abzug), danach schießen: nach dem ersten Weiterdrehen liegen die geladenen
            // Kammern in Schussfolge, jeder weitere Schuss leert die Laufkammer
            for (int s = 0; s < 3; s++)
            {
                for (int k = 0; k < 15; k++) c.Tick(Dt, Idle);
                c.Tick(Dt, Fire);
                for (int k = 0; k < 30 && c.Busy; k++) c.Tick(Dt, Idle);
            }
            Assert.AreEqual(3, c.ammo);
            c.Tick(Dt, new EgoIntent { grounded = true, reload = true });
            for (int k = 0; k < 400 && c.ammo < 4; k++) c.Tick(Dt, Idle);
            Assert.AreEqual(4, c.ammo, "eine Granate geladen");
            for (int k = 0; k < 400 && c.Busy; k++) c.Tick(Dt, k % 2 == 0 ? Fire : Idle);   // Abbruch mit dem Abzug
            for (int k = 0; k < 400 && c.Busy; k++) c.Tick(Dt, Idle);
            int R(int k) => ((GL.weapon.live.rounds.barrel - k) % 6 + 6) % 6;
            for (int s = 0; s < 3 && c.ammo > 0; s++)
            {
                for (int k = 0; k < 15; k++) c.Tick(Dt, Idle);
                int before = c.ammo;
                c.Tick(Dt, Fire);
                if (c.ammo == before) { c.Tick(Dt, Fire); }
                c.Tick(Dt, Idle);
                if (s > 0) Assert.IsFalse(c.output.roundOn[GL.weapon.live.rounds.barrel], $"Schuss {s + 1}: Laufkammer leer");
                for (int k = 0; k < 30 && c.Busy; k++) c.Tick(Dt, Idle);
                for (int k = 0; k < 6; k++)
                    Assert.AreEqual(R(k) < c.ammo, c.output.roundOn[k], $"nach Schuss {s + 1} (Munition {c.ammo}): Kammer {k} in Schussfolge");
            }
        }
    }
}
