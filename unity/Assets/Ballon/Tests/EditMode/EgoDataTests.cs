// EditMode: JSON-Format, Achsumrechnung (Daten und FBX-Import), Armlängen, Handgelenkknick, Gleichheit mit der Blender-Referenz.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;
using static Ballon.Ego.BMath;

namespace Ballon.Ego.Tests
{
    public class EgoDataTests
    {
        const string Gen = "Assets/Ballon/Generated";
        static EgoFile[] _all;
        /// <summary>Alle spielbaren Waffen (0.18: ego.json › weapons, Taste 1, 2; 0.20: 3 Scout).</summary>
        static EgoFile[] All => _all ?? (_all = EgoFile.ParseAll(File.ReadAllText($"{Gen}/ego.json")));
        static EgoFile D => All[0];                     // Pilotwaffe BASIC-01 (Automatik)
        static EgoFile MP => All.First(d => d.gameplay.weapon_type == "submachine_gun");
        static EgoFile SR => All.First(d => d.gameplay.weapon_type == "scout_rifle");      // 0.20: Scout BASIC-03
        static EgoFile PR => All.First(d => d.gameplay.weapon_type == "pulse_rifle");      // 0.22: Impulsgewehr BASIC-02
        static EgoFile PC => All.First(d => d.gameplay.weapon_type == "portal_cannon");    // 0.22: Portalkanone BASIC-T01 (Werkzeug)

        [Serializable] class RefObj { public string name; public float[] m; }
        [Serializable] class RefSample { public string label, action; public int frame; public bool ads_hidden; public RefObj[] objects; }
        [Serializable] class RefFile { public string format; public float tolerance_m, tolerance_deg, tolerance_arm_deg; public RefSample[] samples; }

        static Matrix4x4 M(float[] a)
        {
            var m = new Matrix4x4();
            for (int i = 0; i < 16; i++) m[i / 4, i % 4] = a[i];
            return m;
        }

        /// <summary>Größter Winkel zwischen gleichnamigen Achsen (atan2, genau auch unter 0,1°; Quaternion.Angle rundet darunter auf 0).</summary>
        static float RotDiffDeg(Matrix4x4 a, Matrix4x4 b)
        {
            double w = 0;
            for (int i = 0; i < 3; i++)
            {
                Vector3 x = Col(a, i), y = Col(b, i);
                w = Math.Max(w, Math.Atan2(Vector3.Cross(x, y).magnitude, Vector3.Dot(x, y)));
            }
            return (float)(w * 180 / Math.PI);
        }

        // ---------------------------------------------------------------- Format
        [Test]
        public void Format_und_Umfang()
        {
            Assert.AreEqual(Playable.Length, All.Length, "spielbare Waffen (0.33 P3: Automatik, MP, Scout, Impuls, Portalkanone, "
                                                         + "Handfeuerwaffe, Seitenwaffe, Scharfschütze, Spurgewehr, MG, Schrotflinte, Fusion, lineare Fusion, Bogen, Granatwerfer, Raketenwerfer)");
            CollectionAssert.AreEqual(Playable.Select(p => p.id).ToArray(), All.Select(d => d.weapon.id).ToArray(), "Taste 1, 2, 3 …");
            CollectionAssert.AreEqual(Playable.Select(p => p.fire).ToArray(), All.Select(d => d.gameplay.fire_mode).ToArray(),
                                      "Feuerart aus der Spec (Spannabzug der Trommel als Einzelfeuer, Gurt als Dauerfeuer: ego.FIRE_ALIAS)");
            Assert.GreaterOrEqual(D.weapon.parts.Length, 70, "Waffenteile (Pilot v2.1)");
            foreach (var d in All) Umfang(d);
        }

        /// <summary>Spielbare Waffen in Tastenreihenfolge mit Klasse und Feuerart (export_unity.WEAPONS, ego.CLASSES); 0.33 „Armory“ P1–P3.</summary>
        static readonly (string id, string type, string fire)[] Playable =
        {
            ("BASIC-01-v2.1", "auto_rifle", "full_auto"), ("BASIC-06-v2.1", "submachine_gun", "full_auto"),
            ("BASIC-03-v2.1", "scout_rifle", "semi_auto"), ("BASIC-02-v2.1", "pulse_rifle", "burst"),
            ("BASIC-T01-v2.1", "portal_cannon", "single"), ("BASIC-04-v2.1", "hand_cannon", "semi_auto"),
            ("BASIC-05-v2.1", "sidearm", "semi_auto"), ("BASIC-09-v2.1", "sniper_rifle", "bolt_action"),
            ("BASIC-12-v2.1", "trace_rifle", "continuous_beam"), ("BASIC-15-v2.1", "machine_gun", "full_auto"),
            ("BASIC-08-v2.1", "shotgun", "pump_action"), ("BASIC-10-v2.1", "fusion_rifle", "charge_burst"),
            ("BASIC-11-v2.1", "linear_fusion_rifle", "charge_single"), ("BASIC-07-v2.1", "combat_bow", "draw_release"),
            ("BASIC-13-v2.1", "grenade_launcher", "semi_auto"), ("BASIC-14-v2.1", "rocket_launcher", "single_shot"),
        };

        /// <summary>0.33 „Armory“: jede übertragene Klasse steht vollständig in ego.json – Klasse, Herkunft je Haltung und Aktion, Spielwerte
        /// (Kadenz, Magazin bzw. unbegrenzt, Weltzoom, Hüft-Fadenkreuz), vier Griffe (Werkzeug zwei), Live-Teile, Atlanten. Scheitert mit dem
        /// Export vor 0.33 (ohne Handfeuerwaffe und Seitenwaffe).</summary>
        [Test]
        public void Klassen_vollstaendig_in_ego_json()
        {
            foreach (var (id, type, fire) in Playable)
            {
                var d = All.FirstOrDefault(x => x.weapon.id == id);
                Assert.IsNotNull(d, $"{id} ({type}) fehlt in ego.json");
                Assert.AreEqual(type, d.gameplay.weapon_type, $"{id}: Klasse");
                Assert.AreEqual(type, d.profile.type, $"{id}: Profil der Klasse");
                Assert.IsNotEmpty(d.profile.src, $"{id}: Herkunft der Klasse");
                Assert.Greater(d.gameplay.rpm, 0, $"{id}: Kadenz");
                Assert.GreaterOrEqual(d.gameplay.magazine, 0, $"{id}: Magazin");
                Assert.IsNotEmpty(d.gameplay.src, $"{id}: Herkunft der Spielwerte");
                Assert.GreaterOrEqual(d.gameplay.world_zoom, 1f, $"{id}: Weltzoom");
                Assert.IsNotEmpty(d.gameplay.hip.kind, $"{id}: Hüft-Fadenkreuz");
                foreach (var p in d.poses) Assert.IsNotEmpty(p.src, $"{id}: Herkunft der Haltung {p.name}");
                foreach (var a in d.actions)
                {
                    Assert.Greater(a.frames, 0, $"{id}: {a.name} ohne Dauer");
                    Assert.IsNotEmpty(a.src, $"{id}: Herkunft der Aktion {a.name}");
                }
                Assert.IsTrue(d.weaponTextures?.weapon != null, $"{id}: Atlanten gebacken");
                Umfang(d);
            }
        }

        static void Umfang(EgoFile D)
        {
            Assert.AreEqual(EgoFile.Format, D.format);
            Assert.AreEqual(30, D.fps);
            Assert.AreEqual(75f, D.camera.h_fov_deg);
            bool tool = D.gameplay.HasPortals;                // Werkzeug (0.22): ohne Zielen, Nachladen, Magazin und Visier
            Assert.AreEqual(tool ? 8 : 10, D.poses.Length, "Haltungen");
            if (tool) Assert.AreEqual(2, D.grips.Length, "Griffe");
            else foreach (var g in D.CanReload ? new[] { "grip", "support", "mag", "charge" } : new[] { "grip", "support" })   // 0.33: Klassen dürfen
                                                                                // weitere Griffe haben (MG: Deckel); ohne Nachladen (Bogen, P4) ohne mag/charge
                    Assert.DoesNotThrow(() => D.Grip(g), $"{D.weapon.id}: Griff {g}");
            foreach (var a in tool ? new string[0]
                     : D.gameplay.Draw ? new[] { "idle_hip", "draw", "holster", "aim_in", "aim_out", "fire_draw", "fire_draw_ads", "fire_release",
                                                 "fire_release_ads", "let_down", "let_down_ads", "inspect", "sprint", "lowered", "walk", "crouch",
                                                 "jump_land", "sprint_to_aim", "sprint_to_fire", "draw_aim", "draw_aim_in", "draw_aim_out" }   // Bogen (0.33 P4): ohne Nachladen
                     : new[] { "idle_hip", "draw", "holster", "aim_in", "aim_out", "fire_hip", "fire_ads",
                                                              "reload_tactical", "reload_empty", "inspect", "sprint", "lowered", "walk",
                                                              "crouch", "jump_land", "sprint_to_aim", "sprint_to_fire", "draw_aim",
                                                              "reload_to_switch" })
                Assert.IsTrue(D.HasAction(a), $"{D.weapon.id}: Aktion {a}");
            int shell = D.ShellReload ? (D.HasAction("reload_end_pump") ? 3 : 2) : 0;   // Trommel (0.33 P4): ohne reload_end_pump
            Assert.AreEqual(tool ? 12 : D.gameplay.Draw ? 22 : 19 + (D.gameplay.Cycles ? 2 : 0) + shell, D.actions.Length,
                            "Aktionen (Repetierer, Pumpe, Trommel 0.33: dazu fire_cycle, fire_cycle_ads; Einzelladen: reload_shell, reload_end, "
                            + "reload_end_pump; Bogen: 22 ohne Nachladen, mit Spannen, gespannt Zielen, Lösen, Entspannen)");
            if (D.gameplay.Cycles)
                foreach (var a in new[] { "fire_cycle", "fire_cycle_ads" }) Assert.IsTrue(D.HasAction(a), $"{D.weapon.id}: {a}");
            if (D.ShellReload)
                foreach (var a in new[] { "reload_shell", "reload_end" }) Assert.IsTrue(D.HasAction(a), $"{D.weapon.id}: {a}");   // reload_end_pump
                                                                                                    // nur mit Pumpe (Trommel 0.33 P4 ohne)
            bool shortArm = D.gameplay.weapon_type == "hand_cannon" || D.gameplay.weapon_type == "sidearm";   // Kurzwaffen (0.33): 20/25 Teile
            Assert.GreaterOrEqual(D.weapon.parts.Length, tool || shortArm ? 20 : 30, "Waffenteile (0.33 P3: Schrotflinte 36)");
            bool noBolt = D.gameplay.Cycles || D.gameplay.Beam || D.gameplay.Charge || D.gameplay.SingleShot;   // 0.33: Repetierer, Pumpe, Trommel
            // (fire_cycle), Strahl, Ladewaffe und Raketenwerfer ohne Verschluss je Schuss; Bogen (P4) ohne Abzug und Verschluss
            foreach (var n in D.gameplay.Draw ? new string[0] : tool ? new[] { D.weapon.live.trigger, D.weapon.live.ring }
                                   : noBolt ? new[] { D.weapon.live.trigger } : new[] { D.weapon.live.trigger, D.weapon.live.bolt })
                Assert.IsTrue(D.HasPart(n), $"{D.weapon.id}: Live-Teil {n}");
            foreach (var g in D.weapon.live.glow ?? new string[0])
                Assert.AreEqual("glow", D.Part(g).move.kind, $"{D.weapon.id}: Leuchtteil {g}");
            Assert.AreEqual(D.gameplay.Beam || D.gameplay.Charge, (D.weapon.live.glow?.Length ?? 0) > 0,
                            $"{D.weapon.id}: Leuchtteile genau beim Dauerstrahl und bei der Ladewaffe");
            Assert.IsTrue(string.IsNullOrEmpty(D.weapon.live.port) || D.HasPart(D.weapon.live.port),           // Pistolen, Trommel: ohne
                          $"{D.weapon.id}: Auswurfklappe {D.weapon.live.port}");                              // Auswurfklappe (0.33)
            var meshes = new HashSet<string>(D.mesh_bounds.objects.Select(o => o.name));
            Assert.IsTrue(D.weapon.parts.All(p => meshes.Contains(p.id)), "jedes Teil hat ein Netz im Export");
            Assert.AreEqual(3, D.arm.rig_version);
            Assert.AreEqual(4, D.arm.finger_x.Length, "vier Finger");
            foreach (var f in D.finger_poses)
            {
                Assert.AreEqual(12, f.f.Length, f.name);
                Assert.AreEqual(3, f.t.Length, f.name);
            }
            foreach (var A in D.actions)
            {
                Assert.Greater(A.frames, 0, A.name);
                foreach (var k in A.weapon) Assert.DoesNotThrow(() => D.Pose(k.pose), A.name);
                foreach (var k in A.L.Concat(A.R)) Assert.DoesNotThrow(() => D.Grip(k.grip), A.name);
                foreach (var k in A.fL.Concat(A.fR)) Assert.DoesNotThrow(() => D.Fingers(k.pose), A.name);
                var fr = A.weapon.Select(k => k.f).ToArray();
                CollectionAssert.IsOrdered(fr, A.name);
                Assert.LessOrEqual(fr.Last(), A.frames, A.name);
                CollectionAssert.IsOrdered(A.events.Select(e => e.f).ToArray(), A.name + " Marker");
            }
            foreach (var n in tool ? new[] { "Socket_Hand", "Socket_SupportHand", "Socket_Muzzle" }
                                   : new[] { "Socket_Hand", "Socket_SupportHand", "Socket_Sight", "Socket_Eye" })
                Assert.DoesNotThrow(() => D.Anchor(n));
            if (D.HasPart("charging_handle"))              // Ladehebel; Pistolen und Trommel laden am Schlitten bzw. ohne (0.33)
                Assert.DoesNotThrow(() => D.Anchor("Socket_Charge"));
            Assert.AreEqual(tool, !D.CanAim && !D.CanReload, $"{D.weapon.id}: Zielen und Nachladen nur mit Visier und Magazin");
            Assert.Greater(D.gameplay.rpm, 0);
            if (tool || D.gameplay.Draw) Assert.AreEqual(0, D.gameplay.magazine, "Werkzeug und Bogen (Vorrat, 0.33 P4) ohne Magazin (unbegrenzt)");
            else Assert.Greater(D.gameplay.magazine, 0);
        }

        [Test]
        public void Falsches_Format_wird_abgelehnt()
        {
            Assert.Throws<FormatException>(() => EgoFile.Parse("{\"format\":\"ballon-ego/1\"}"));    // alter Export ohne Texturen
            var ex = Assert.Throws<FormatException>(() => EgoFile.Parse("{\"format\":\"ballon-ego/2\"}"));   // 0.7: mask statt spec, keine Skins
            StringAssert.Contains("neu exportieren", ex.Message);
            ex = Assert.Throws<FormatException>(() => EgoFile.Parse("{\"format\":\"ballon-ego/3\"}"));          // 0.9: ohne secondary.aim_zeta
            StringAssert.Contains("neu exportieren", ex.Message);
            ex = Assert.Throws<FormatException>(() => EgoFile.Parse("{\"format\":\"ballon-ego/4\"}"));          // 0.12: ohne Weltzoom und Hüft-Fadenkreuz
            StringAssert.Contains("neu exportieren", ex.Message);
            ex = Assert.Throws<FormatException>(() => EgoFile.Parse("{\"format\":\"ballon-ego/5\"}"));          // 0.14: Rückstoß ohne Bahn, kein Wechsel
            StringAssert.Contains("neu exportieren", ex.Message);
            ex = Assert.Throws<FormatException>(() => EgoFile.Parse("{\"format\":\"ballon-ego/6\"}"));          // 0.15: ohne Mündungsfeuer und Hülsen
            StringAssert.Contains("neu exportieren", ex.Message);
            ex = Assert.Throws<FormatException>(() => EgoFile.Parse("{\"format\":\"ballon-ego/11\"}"));         // unbekannt (neuer als der Leser; /10 seit 0.22)
            StringAssert.Contains("neu exportieren", ex.Message);
        }

        /// <summary>0.21 „Ironsight“ (Visier-Baukasten v3): nur die ausdrücklich benannten Visierfelder werden normiert, alle übrigen Teile
        /// (auch die unveränderten Visierteile mit Bewegung und Elternbezug) bleiben Feld für Feld gleich. Alle Waffen: Visierteile mit
        /// Rolle anodized → sight_anod (Abriebmaske A). MP (H2 „Pille“ statt Holo): in der alten Datei entfallen Haube und Haubenkante,
        /// die Scheibe ist glass_scope und der Augenpunkt hängt an der Scheibe; in der neuen Datei fehlen dafür nur die drei neuen
        /// H2-Teile (Emitterblock, Leuchtkontur, Statuspunkte – geprüft in Visier_v3). Teile nach ID sortiert (H2 ordnet anders).</summary>
        static readonly string[] H2_Neu = { "sight_block", "sight_line", "sight_status" };
        static readonly string[] H2_Entfallen = { "sight_frame", "sight_frame_trim" };

        static string Visier_0_21(EgoWeapon w, bool alt)
        {
            var c = JsonUtility.FromJson<EgoWeapon>(JsonUtility.ToJson(w));
            foreach (var p in c.parts)
                if (p.asm == "sight" && p.role == "anodized") p.role = "sight_anod";
            if (c.id == "BASIC-06-v2.1" && alt)
            {
                Assert.IsTrue(H2_Entfallen.All(id => c.parts.Any(p => p.id == id)), "alte MP hatte Haube und Haubenkante");
                c.parts = c.parts.Where(p => !H2_Entfallen.Contains(p.id)).ToArray();
                foreach (var p in c.parts) if (p.id == "sight_glass") p.role = "glass_scope";
                foreach (var a in c.anchors) if (a.id == "Socket_Eye") a.part = "sight_glass";
            }
            else if (c.id == "BASIC-06-v2.1")
                c.parts = c.parts.Where(p => !H2_Neu.Contains(p.id)).ToArray();
            c.parts = c.parts.OrderBy(p => p.id, StringComparer.Ordinal).ToArray();
            return JsonUtility.ToJson(c);
        }

        static void Visier_v3(EgoWeapon w)
        {
            var s = w.parts.Where(p => p.asm == "sight").ToArray();
            Assert.IsFalse(s.Any(p => p.role == "anodized"), $"{w.id}: Visierteile in der Rolle sight_anod (0.21, Abriebmaske A)");
            Assert.IsTrue(s.Any(p => p.role == "sight_anod"), $"{w.id}: Visier eloxiert als sight_anod");
            if (w.id == "BASIC-06-v2.1")
            {
                CollectionAssert.IsSubsetOf(H2_Neu, s.Select(p => p.id).ToArray(), "MP: H2 „Pille“");
                foreach (var p in s.Where(p => H2_Neu.Contains(p.id)))
                    Assert.AreEqual("sight_mount", p.parent, $"{p.id} hängt am Klemmfuß (folgt dem Abnehmen)");
                Assert.AreEqual("sight_anod", s.Single(p => p.id == "sight_block").role, "Emitterblock eloxiert");
                Assert.AreEqual("energy", s.Single(p => p.id == "sight_status").role, "Statuspunkte leuchten");
                Assert.IsFalse(s.Any(p => p.id == "sight_frame"), "MP: H2 ohne Haube");
                Assert.AreEqual("sight_line", s.Single(p => p.id == "sight_line").role, "Pillenkontur als Leuchtrolle, nicht als Absehen (bleibt sichtbar)");
            }
        }

        /// <summary>0.18 Formatwechsel ballon-ego/7 → /8: der Leser erkennt die alte Datei (Stand 0.17, eine Waffe; Kopie unter
        /// Tests/EditMode/Data) und liefert für die Pilotwaffe dieselben Daten wie die neue Datei – Haltungen, Griffe, Aktionen, Spielwerte,
        /// Teile, Anker, Hülsen, Bewegung, Atlanten; die Live-Teile, die bis 0.17 fest im Code standen, setzt er wie damals. Seit 0.21 mit
        /// den bewusst geänderten Visierwerten (Visier_0_21).</summary>
        [Test]
        public void Altes_Format_7_wird_gelesen()
        {
            var old = EgoFile.ParseAll(File.ReadAllText("Assets/Ballon/Tests/EditMode/Data/ego_v7.json"));
            Assert.AreEqual(1, old.Length, "/7: eine Waffe");
            var o = old[0];
            Assert.AreEqual(EgoFile.FormatLegacy, o.format);
            Assert.AreEqual(EgoFile.Format, D.format);
            Assert.AreEqual("bolt_carrier", o.weapon.live.bolt);
            Assert.AreEqual("weapon", o.atlas);
            Assert.AreEqual("full_auto", o.gameplay.fire_mode, "/7 ohne Feuerart: Dauerfeuer (Migration im Leser, 0.20)");
            Assert.AreEqual(0f, o.motion.ads_hide.eye_m, "/7 ohne Zielfernrohr-Regel: nie aus");
            string J(object x) => JsonUtility.ToJson(x);
            o.motion.ads_hide = D.motion.ads_hide;                // neu in /9; die Pilotwaffe hat keine Teile mit ads_hide
            foreach (var (name, a, b) in new (string, object, object)[] {
                ("gameplay", BowZoom(o, D).gameplay, D.gameplay), ("motion", o.motion, D.motion), ("camera", o.camera, D.camera), ("arm", o.arm, D.arm),
                ("textures.arms", o.textures.arms, D.textures.arms) })
                Assert.AreEqual(J(a), J(b), name);
            // Waffenatlas: gleiche Teile und Backgröße; die Dateien liegen seit 0.20 nach TEXTURE_STORE (97 A, albedo als JPG)
            CollectionAssert.AreEqual(o.textures.weapon.objects, D.textures.weapon.objects, "Atlasobjekte");
            Assert.AreEqual(o.textures.weapon.size, D.textures.weapon.size);
            foreach (var (a, b) in new[] { (o.textures.weapon.albedo, D.textures.weapon.albedo), (o.textures.weapon.spec, D.textures.weapon.spec),
                                           (o.textures.weapon.normal, D.textures.weapon.normal), (o.textures.weapon.ao, D.textures.weapon.ao) })
                Assert.AreEqual(Path.GetFileNameWithoutExtension(a), Path.GetFileNameWithoutExtension(b), "gleicher Dateiname ohne Endung");
            o.weapon.type_de = D.weapon.type_de;                   // neu in 0.33 (Klasse für HUD und Menü)
            Assert.AreEqual(Visier_0_21(o.weapon, true), Visier_0_21(D.weapon, false), "weapon (Teile, Anker, Hülsen, Live-Teile; Visierrolle 0.21)");
            Visier_v3(D.weapon);
            CollectionAssert.AreEqual(o.poses.Select(J), D.poses.Select(J), "Haltungen");
            CollectionAssert.AreEqual(o.grips.Select(J), D.grips.Select(J), "Griffe");
            CollectionAssert.AreEqual(o.actions.Select(J), D.actions.Select(J), "Aktionen");
            CollectionAssert.AreEqual(o.textures.skins.Select(s => s.name + s.kind), D.textures.skins.Select(s => s.name + s.kind), "Skins");
            // 0.21: das Absehen ändert seine Netzgrenzen (Röhren → flach in der Glasebene); 0.32: der Griff mit R_SOFT (A5, −0,013 mm,
            // mit 0,05 mm Toleranz); alle übrigen Teile bleiben gleich
            CollectionAssert.AreEquivalent(o.mesh_bounds.objects.Where(b => b.name != "sight_reticle" && b.name != "grip").Select(J),
                                           D.mesh_bounds.objects.Where(b => b.name != "sight_reticle" && b.name != "grip").Select(J),
                                           "Netzgrenzen (ohne Absehen 0.21 und Griff 0.32)");
            var g0 = o.mesh_bounds.objects.First(b => b.name == "grip");
            var g1 = D.mesh_bounds.objects.First(b => b.name == "grip");
            for (int i = 0; i < 3; i++)
            {
                Assert.AreEqual(g0.min[i], g1.min[i], 5e-5f, $"Griff min[{i}] (0.32: R_SOFT)");
                Assert.AreEqual(g0.max[i], g1.max[i], 5e-5f, $"Griff max[{i}] (0.32: R_SOFT)");
            }
            var S7 = new EgoSolver(o);
            var S8 = new EgoSolver(D);
            var A = D.Action("fire_hip");
            var a7 = S7.Evaluate(o.Action("fire_hip"), 12, new EgoState());
            var a8 = S8.Evaluate(A, 12, new EgoState());
            Assert.AreEqual(a7.weapon, a8.weapon, "gleiche Auswertung");
        }

        /// <summary>0.20 Formatwechsel /8 → /9: der Leser liest die Datei von main (0.19 „Saddle“, Kopie Tests/EditMode/Data/ego_v8.json)
        /// weiter und setzt Dauerfeuer und keine Zielfernrohr-Regel. Automatik und MP sind in /9 Feld für Feld gleich – Haltungen, Griffe,
        /// Aktionen, Spielwerte, Teile, Profil, Bewegung (bis auf die neue Regel motion.ads_hide): Automatik und MP unverändert.</summary>
        [Test]
        public void Altes_Format_8_wird_gelesen_Automatik_und_MP_unveraendert()
        {
            var old = EgoFile.ParseAll(File.ReadAllText("Assets/Ballon/Tests/EditMode/Data/ego_v8.json"));
            Assert.AreEqual(2, old.Length, "/8 von main: Automatik und MP");
            string J(object x) => JsonUtility.ToJson(x);
            foreach (var o in old)
            {
                var n = All.Single(d => d.weapon.id == o.weapon.id);
                Assert.AreEqual(EgoFile.Format8, o.format);
                Assert.AreEqual("full_auto", o.gameplay.fire_mode, $"{o.weapon.id}: /8 ohne Feuerart → Dauerfeuer");
                Assert.AreEqual(0f, o.motion.ads_hide.eye_m, "/8: keine Teile im Zielen aus");
                BowZoom(o, n);
                Assert.AreEqual(J(o.gameplay), J(n.gameplay), $"{o.weapon.id}: Spielwerte");
                o.weapon.type_de = n.weapon.type_de;               // neu in 0.33 (Klasse für HUD und Menü)
                Assert.AreEqual(Visier_0_21(o.weapon, true), Visier_0_21(n.weapon, false), $"{o.weapon.id}: Teile, Anker, Hülsen, Live-Teile (Visier 0.21)");
                Visier_v3(n.weapon);
                Assert.IsFalse(n.weapon.parts.Any(p => p.ads_hide), $"{o.weapon.id}: kein Teil mit ads_hide");
                Assert.AreEqual(J(o.profile), J(n.profile), $"{o.weapon.id}: Klassenprofil");
                CollectionAssert.AreEqual(o.poses.Select(J), n.poses.Select(J), $"{o.weapon.id}: Haltungen");
                CollectionAssert.AreEqual(o.grips.Select(J), n.grips.Select(J), $"{o.weapon.id}: Griffe");
                CollectionAssert.AreEqual(o.actions.Select(J), n.actions.Select(J), $"{o.weapon.id}: Aktionen");
                var m = JsonUtility.FromJson<Motion>(J(o.motion));
                m.ads_hide = n.motion.ads_hide;
                Assert.AreEqual(J(m), J(n.motion), "Bewegung (ohne die neue Regel ads_hide)");
            }
        }

        // ---------------------------------------------------------------- Scout BASIC-03 0.20 (Entscheidungsliste Schritt 6, Visier-Standard 3)
        /// <summary>Werte der Klasse Scout aus den Daten (ego.CLASSES › scout_rifle, keine Sonderlogik nach Waffen-ID): Einzelfeuer aus der
        /// Spec, 180/min und 15 Schuss (Tone Patrol), Weltzoom 2,0 (1.2 A), Hüft-Fadenkreuz aus dem Katalog, Anflug 7 Bilder bei 30/s (4d,
        /// am Unity-Bild 15–20 bei 60/s), aim_out 5; Sprint wie die Automatik (lange Waffe, 2.1 A / 3.2 A), eigene Hüfte nach huefte.json (0.33); Schussbilder der Clips in
        /// der Klassenkadenz; die übrigen Aktionen wie die Automatik; Teile mit ads_hide sind Okular, Rohr, Türme, Okularlinse, Spannband.</summary>
        [Test]
        public void Werte_des_Scouts()
        {
            string J(object x) => JsonUtility.ToJson(x);
            Assert.AreEqual("scout_rifle", SR.profile.type);
            Assert.AreEqual("semi_auto", SR.gameplay.fire_mode, "Feuerart aus der Spec (META fire)");
            Assert.IsTrue(SR.gameplay.Semi);
            Assert.IsFalse(D.gameplay.Semi || MP.gameplay.Semi, "Automatik und MP: Dauerfeuer");
            Assert.AreEqual(180, SR.gameplay.rpm);
            Assert.AreEqual(15, SR.gameplay.magazine);
            Assert.AreEqual(2.0f, SR.gameplay.world_zoom, 1e-6f, "Weltzoom Scout 2,0 (1.2 A, seit 0.13)");
            Assert.AreEqual(0.2f, SR.gameplay.zoom_start, 1e-6f, "Zoom ab 20 % des Augenwegs (1d, am Unity-Bild gemessen)");
            Assert.AreEqual(0f, D.gameplay.zoom_start + MP.gameplay.zoom_start, "Automatik und MP: 5 % wie bisher");
            Assert.AreEqual("scope", SR.gameplay.sight);
            Assert.AreEqual("cross", SR.gameplay.hip.kind, "Hüft-Fadenkreuz aus basic/reticles.py (DEFAULTS scout_rifle)");
            Assert.AreEqual("", SR.gameplay.hip.sprint.kind, "im Sprint aus");
            Assert.AreEqual(9, SR.Action("aim_in").frames, "aim_in 9 Bilder bei 30/s (0.33.2: Gapfill ein 18–20 bei 60/s)");
            Assert.AreEqual(8, SR.Action("aim_out").frames, "aim_out 8 Bilder (0.33.2: Gapfill aus 16–18 bei 60/s)");
            Assert.AreEqual(22, SR.Action("draw").frames, "draw 22 Bilder (0.33.2: Gapfill erstes Modellbild → ruhig 42–44 bei 60/s)");
            CollectionAssert.AreEqual(new[] { 2, 12, 22 }, SR.Action("fire_hip").fire, "180/min = alle 10 Bilder bei 30/s");
            CollectionAssert.AreEqual(new[] { 2, 12, 22 }, SR.Action("fire_ads").fire);
            CollectionAssert.AreEqual(new[] { 7, 17 }, SR.Action("sprint_to_fire").fire);
            foreach (var n in new[] { "sprint", "ads", "reload" })      // 0.33: eigene Hüfte nach huefte.json (crouch, air, lowered folgen ihr)
            {
                EgoPose a = D.Pose(n), b = SR.Pose(n);
                Assert.AreEqual(J(a.pos) + J(a.aim) + a.roll + J(a.eye), J(b.pos) + J(b.aim) + b.roll + J(b.eye), $"Haltung {n} wie die Automatik");
            }
            Assert.AreNotEqual(J(D.Pose("hip")), J(SR.Pose("hip")), "eigene Hüfte (0.33, Abgleich mit cubeescape-reference huefte.json)");
            foreach (var k in new[] { "crouch", "air", "lowered" })        // FOLLOW_HIP: gleicher Versatz zur Hüfte wie bei der Automatik
            {
                EgoPose a = D.Pose(k), b = SR.Pose(k), ha = D.Pose("hip"), hb = SR.Pose("hip");
                for (int i = 0; i < 3; i++)
                {
                    Assert.AreEqual(a.pos[i] - ha.pos[i], b.pos[i] - hb.pos[i], 1e-3f, $"{k} folgt der Hüfte (Lage)");
                    Assert.AreEqual(a.aim[i] - ha.aim[i], b.aim[i] - hb.aim[i], 1e-3f, $"{k} folgt der Hüfte (Zielpunkt)");
                }
                Assert.AreEqual(a.roll - ha.roll, b.roll - hb.roll, 1e-3f, $"{k} folgt der Hüfte (Rollen)");
            }
            StringAssert.Contains("Visier 68,4/56,0", SR.Pose("hip").src, "Herkunft der Hüfte am Scout");
            foreach (var A in SR.actions)
            {
                if (new[] { "aim_in", "aim_out", "fire_hip", "fire_ads", "sprint_to_fire", "draw" }.Contains(A.name)) continue;   // draw: 0.33.2 eigene Dauer
                var B = D.Action(A.name);
                Assert.AreEqual(J(B.weapon) + J(B.L) + J(B.R) + J(B.fL) + J(B.fR) + J(B.mech) + J(B.events) + J(B.bob) + B.frames,
                                J(A.weapon) + J(A.L) + J(A.R) + J(A.fL) + J(A.fR) + J(A.mech) + J(A.events) + J(A.bob) + A.frames, A.name);
            }
            Assert.IsTrue(SR.weapon.eject.enabled, "Scout wirft Hülsen aus (Feld EJECT)");
            Assert.AreEqual("rifle", SR.weapon.eject.@case);
            Assert.AreEqual("bolt", SR.weapon.live.bolt);
            CollectionAssert.AreEquivalent(new[] { "scope_eye_trim", "scope_eyepiece", "scope_ocular_glass", "scope_strap", "scope_tube", "scope_turret",
                                                   "scope_turret_w" }, SR.weapon.parts.Where(p => p.ads_hide).Select(p => p.id), "Teile mit ads_hide");
            Assert.AreEqual(0.06f, SR.motion.ads_hide.eye_m, 1e-6f, "Augenabstand Okularende 30 mm + near 30 mm");
        }

        /// <summary>Entscheidungsliste 2.1 A, lange Waffe: Mündung des Scouts im Destiny-Band x 54–59 / y 60–71 % (Destiny-Scout Tone Patrol
        /// ≈ 57/63), hinteres Okularende 7–34 pp rechts der Mündung, Kontur bis zum rechten und unteren Rand – gemessen wie das Ego-Still.</summary>
        [Test]
        public void Hueftlage_des_Scouts_im_Band()
        {
            var S = new EgoSolver(SR);
            var E = new EgoScreen(S);
            var o = S.Evaluate(S.StillAction("hip"), 0, new EgoState());
            Vector3 At(string a) => E.ToScreen(o.weapon.MultiplyPoint3x4(V(SR.Anchor(a).pos)));
            Vector3 m = At("Socket_Muzzle"), s = At("Socket_Sight"), r = At("Socket_Reticle");
            var pts = new List<Vector2>();
            E.Silhouette(o, pts, arms: false);
            TestContext.WriteLine($"Scout-Hüfte: Mündung x {m.x:0.0} / y {m.y:0.0} %, Okularende x {s.x:0.0} / y {s.y:0.0} % ({s.x - m.x:0.0} pp rechts), " +
                                  $"Absehen x {r.x:0.0} / y {r.y:0.0} %; Waffe x {pts.Min(p => p.x):0.0}–{pts.Max(p => p.x):0.0}, y {pts.Min(p => p.y):0.0}–{pts.Max(p => p.y):0.0} %");
            Assert.That(m.x, Is.InRange(54f, 59f), "Mündung x (lange Waffen 54–59 %)");
            Assert.That(m.y, Is.InRange(60f, 71f), "Mündung y (lange Waffen 60–71 %)");
            Assert.That(s.x - m.x, Is.InRange(7f, 34f), "Okularende 7–34 pp rechts der Mündung");
            Assert.Greater(pts.Max(p => p.x), 99f, "Kontur reicht bis zum rechten Rand");
            Assert.Greater(pts.Max(p => p.y), 99f, "Kontur reicht bis zum unteren Rand");
        }

        /// <summary>0.33: Weltzoom in der Zoomtabelle angeglichen – Bogen 1,8 → 2,2 (Imperial Needle gemessen), Scharfschütze 5,5 → 4,0 (Far
        /// Future ≈ 4×), kurze Fusion 1,8 → 1,45 und lineare Fusion 3,8 → 3,0 (REF 0.34 „Gapfill“); sonst ist die Tabelle gleich.
        /// Die alten Dateien tragen die alten Werte – für den Vergleich übernommen, die übrigen
        /// Einträge geprüft. Ebenso sight_form (0.33, Absehen im Glas): alte Dateien setzen es beim Lesen auf die Hüftform.</summary>
        static EgoFile BowZoom(EgoFile o, EgoFile n)
        {
            var a = o.gameplay.zoom_table; var b = n.gameplay.zoom_table;
            Assert.AreEqual(a.Length, b.Length, "Zoomtabelle");
            for (int k = 0; k < a.Length; k++)
                if (a[k].type == "combat_bow") Assert.AreEqual(2.2f, b[k].zoom, 1e-4f, "Bogen 2,2×");
                else if (a[k].type == "sniper_rifle") Assert.AreEqual(4.0f, b[k].zoom, 1e-4f, "Scharfschütze 4×");
                else if (a[k].type == "fusion_rifle") Assert.AreEqual(1.45f, b[k].zoom, 1e-4f, "kurze Fusion 1,45× (Gapfill)");
                else if (a[k].type == "linear_fusion_rifle") Assert.AreEqual(3.0f, b[k].zoom, 1e-4f, "lineare Fusion 3,0× (Gapfill)");
                else Assert.AreEqual(a[k].zoom, b[k].zoom, 1e-6f, a[k].type);
            o.gameplay.zoom_table = b;
            return Payload034(o, n);
        }

        /// <summary>0.34 „Payload“ (ohne neues Format): ein älterer Export kennt Wirkung, Schrittteile, Füllstand und Glieder nicht – der
        /// Leser setzt die alte Wirkung (Kugel mit Einschlag) und leere Listen; für den Vergleich übernimmt die alte Datei die neuen Felder.</summary>
        static EgoFile Payload034(EgoFile o, EgoFile n)
        {
            Assert.AreEqual("vor 0.34", o.gameplay.fx.src, "älterer Export: Wirkung aus dem Leser");
            Assert.AreEqual(o.gameplay.HasPortals ? "none" : "hitscan", o.gameplay.fx.kind);
            Assert.AreEqual(0, o.weapon.live.index.Length + o.weapon.live.fill.Length + o.weapon.live.rounds.sets.Length, "ohne Schrittteile, Füllstand");
            Assert.Greater(o.motion.payload.decal.max, 0, "Rückfall der Löcher (JsonUtility legt leere Objekte an, Richter 0.34)");
            Assert.Greater(o.motion.payload.explosion.sparks, 0, "Rückfall der Explosion");
            Assert.Greater(o.motion.payload.muzzle_smoke.rate_hz, 0, "Rückfall des Laufrauchs");
            o.gameplay.fx = n.gameplay.fx;
            o.motion.index = n.motion.index;
            o.motion.payload = n.motion.payload;
            o.weapon.live.index = n.weapon.live.index;
            o.weapon.live.fill = n.weapon.live.fill;
            o.weapon.live.rounds = n.weapon.live.rounds;
            if (o.weapon.eject != null && n.weapon.eject != null)
            {
                o.weapon.eject.links = n.weapon.eject.links;
                o.weapon.eject.part = n.weapon.eject.part;
                o.weapon.eject.ring_m = n.weapon.eject.ring_m;
                o.weapon.eject.ring_n = n.weapon.eject.ring_n;
                o.weapon.eject.speed_k = n.weapon.eject.speed_k;
            }
            return o;
        }

        // ---------------------------------------------------------------- Impuls BASIC-02 und Portalkanone BASIC-T01 0.22 (Schritt 6)
        /// <summary>0.22 Formatwechsel /9 → /10: der Leser liest die Datei von main (0.21 „Ironsight“, Kopie Tests/EditMode/Data/ego_v9.json)
        /// weiter und setzt Salve, Bahnstufe, Mündungsfeuer und Portale wie bisher (keine Salve, gemeinsame Bahnstufe, mit Blitz, ohne Portale).
        /// Automatik, MP und Scout sind in /10 Feld für Feld gleich: Spielwerte, Teile, Profil, Haltungen, Griffe, Aktionen, Bewegung – außer
        /// der Hüfte des Scouts und den an ihr hängenden Haltungen (0.33, eigene Hüfte nach cubeescape-reference huefte.json).</summary>
        [Test]
        public void Altes_Format_9_wird_gelesen_drei_Waffen_unveraendert()
        {
            var old = EgoFile.ParseAll(File.ReadAllText("Assets/Ballon/Tests/EditMode/Data/ego_v9.json"));
            Assert.AreEqual(3, old.Length, "/9 von main: Automatik, MP, Scout");
            string J(object x) => JsonUtility.ToJson(x);
            foreach (var o in old)
            {
                var n = All.Single(d => d.weapon.id == o.weapon.id);
                Assert.AreEqual(EgoFile.Format9, o.format);
                Assert.AreEqual(0, o.gameplay.burst_shots, "/9: keine Salve");
                Assert.IsTrue(o.gameplay.muzzle_flash, "/9: Mündungsfeuer");
                Assert.AreEqual(o.motion.recoil.path_up_h, o.gameplay.path_up_h, "/9: Bahnstufe aus motion.recoil");
                BowZoom(o, n);
                Assert.AreEqual(J(o.gameplay), J(n.gameplay), $"{o.weapon.id}: Spielwerte");
                o.weapon.type_de = n.weapon.type_de;               // neu in 0.33 (Klasse für HUD und Menü)
                Assert.AreEqual(J(o.weapon), J(n.weapon), $"{o.weapon.id}: Teile, Anker, Hülsen, Live-Teile");
                // 0.33: der Scout hat eine eigene Hüfte nach cubeescape-reference huefte.json (crouch, air, lowered folgen ihr); die übrigen Haltungen gleich
                var hipBound = new[] { "hip", "crouch", "air", "lowered" };
                bool refit = o.weapon.id == "BASIC-03-v2.1";
                if (!refit) Assert.AreEqual(J(o.profile), J(n.profile), $"{o.weapon.id}: Klassenprofil");
                else CollectionAssert.AreEqual(new[] { "hip" }, n.profile.poses, "Scout: eigene Hüfte im Klassenprofil");
                CollectionAssert.AreEqual(o.poses.Where(q => !refit || !hipBound.Contains(q.name)).Select(J),
                                          n.poses.Where(q => !refit || !hipBound.Contains(q.name)).Select(J), $"{o.weapon.id}: Haltungen");
                CollectionAssert.AreEqual(o.grips.Select(J), n.grips.Select(J), $"{o.weapon.id}: Griffe");
                // 0.33.2: Zielen und Ziehen des Scouts nach Gapfill (eigene Bildzahlen, Werte_des_Scouts); die übrigen Aktionen gleich
                var retimed = new[] { "draw", "aim_in", "aim_out" };
                CollectionAssert.AreEqual(o.actions.Where(a => !refit || !retimed.Contains(a.name)).Select(J),
                                          n.actions.Where(a => !refit || !retimed.Contains(a.name)).Select(J), $"{o.weapon.id}: Aktionen");
                Assert.AreEqual(J(o.motion), J(n.motion), "Bewegung");
            }
        }

        /// <summary>Werte der Klasse Impuls aus den Daten (ego.CLASSES › pulse_rifle, keine Sonderlogik nach Waffen-ID): Salve aus der Spec
        /// (burst_3), 900/min in der Salve, 540/min gemittelt (Gridskipper), Magazin 36, Bahnstufe 1,33 % H je Schuss (≈ 4 pp je Salve),
        /// Weltzoom 2,0 (Holo), Hüftform ring_dot, Anflug 10 Bilder bei 30/s wie die Automatik (Destiny 20 bei 60/s), Sprint wie die Automatik,
        /// eigene Hüfte; Schussbilder der Clips in ganzen Salven; Hülsen, Verschluss und Klappe aus dem Modul.</summary>
        [Test]
        public void Werte_des_Impulses()
        {
            string J(object x) => JsonUtility.ToJson(x);
            var G = PR.gameplay;
            Assert.AreEqual("pulse_rifle", PR.profile.type);
            Assert.AreEqual("burst", G.fire_mode, "Feuerart aus der Spec (META fire burst_3)");
            Assert.IsTrue(G.Burst && !G.Semi);
            Assert.AreEqual(3, G.burst_shots, "Salvenlänge aus der Spec");
            Assert.AreEqual(900, G.burst_rpm, "4 Bilder bei 60/s in der Salve");
            Assert.AreEqual(540, G.rpm, "Gridskipper 540/min");
            Assert.AreEqual(36, G.magazine);
            Assert.AreEqual(0.0133f, G.path_up_h, 1e-6f, "≈ 4 pp H je Salve");
            Assert.AreEqual(0.010f, D.gameplay.path_up_h, 1e-6f, "Automatik unverändert");
            Assert.AreEqual(0.10f, G.recover_delay_s, 1e-6f, "Erholung nach 1,5 Takten");
            Assert.AreEqual(5.0f, G.recover_hz, 1e-6f, "≈ 80 % zurück in der Pause (Gridskipper)");
            foreach (var d in new[] { D, MP, SR })
            {
                Assert.AreEqual(d.motion.recoil.recover_delay_s, d.gameplay.recover_delay_s, 1e-6f, $"{d.weapon.id}: gemeinsame Erholung wie bisher");
                Assert.AreEqual(d.motion.recoil.recover_hz, d.gameplay.recover_hz, 1e-6f, $"{d.weapon.id}: gemeinsame Erholung wie bisher");
            }
            Assert.IsFalse(D.gameplay.Burst || MP.gameplay.Burst || SR.gameplay.Burst, "keine andere Klasse feuert Salven");
            Assert.AreEqual(2.0f, G.world_zoom, 1e-6f, "Weltzoom Impuls 2,0 (Holo, seit 0.13)");
            Assert.AreEqual("reflex", G.sight);
            Assert.AreEqual("ring_dot", G.hip.kind, "Hüftform ring_dot");
            Assert.AreEqual(10, PR.Action("aim_in").frames, "aim_in 10 Bilder wie die Automatik (4d: Impuls 20 bei 60/s)");
            Assert.AreEqual(8, PR.Action("aim_out").frames);
            CollectionAssert.AreEqual(new[] { 2, 4, 6, 12, 14, 16, 22, 24, 26 }, PR.Action("fire_hip").fire, "drei Salven: 2 Bilder Takt, 10 Bilder Folge");
            CollectionAssert.AreEqual(PR.Action("fire_hip").fire, PR.Action("fire_ads").fire);
            CollectionAssert.AreEqual(new[] { 7, 9, 11, 17, 19, 21 }, PR.Action("sprint_to_fire").fire);
            foreach (var n in new[] { "sprint", "ads", "reload" })
            {
                EgoPose a = D.Pose(n), b = PR.Pose(n);
                Assert.AreEqual(J(a.pos) + J(a.aim) + a.roll + J(a.eye), J(b.pos) + J(b.aim) + b.roll + J(b.eye), $"Haltung {n} wie die Automatik");
            }
            Assert.AreNotEqual(J(D.Pose("hip")), J(PR.Pose("hip")), "eigene Hüfte");
            StringAssert.Contains("Visier 73,4/55,2", PR.Pose("hip").src, "Herkunft der Hüfte (0.33, Abgleich mit huefte.json)");
            Assert.IsTrue(PR.weapon.eject.enabled, "Hülsen über EJECT");
            Assert.AreEqual("rifle", PR.weapon.eject.@case);
            Assert.AreEqual("bolt_carrier", PR.weapon.live.bolt);
            Assert.AreEqual("", PR.weapon.live.ring);
        }

        /// <summary>Werte der Portalkanone (Werkzeug, ego.CLASSES › portal_cannon): kein Visier, kein Zielen, kein Nachladen (die Aktionen
        /// fehlen in den Daten), Magazin 0 = unbegrenzt, ohne Mündungsfeuer und Hülsen, Bahnstufe 0; Bedienung nach Nutzerwahl A (27.10.2026):
        /// Linksklick Portal A (Cyan, Ring im Uhrzeigersinn), Rechtsklick Portal B (Orange, gegen den Uhrzeigersinn), Abklingzeit 0,25 s, 24 m;
        /// Ring 120° je Schuss in 10 Bildern bei 30/s (fire_a/fire_b wie das Modul).</summary>
        [Test]
        public void Werte_der_Portalkanone()
        {
            var G = PC.gameplay;
            Assert.AreEqual("portal_cannon", PC.profile.type);
            Assert.AreEqual("single", G.fire_mode);
            Assert.IsTrue(G.Semi && G.HasPortals && G.Unlimited && !G.Burst);
            Assert.AreEqual(240, G.rpm, "Abklingzeit 0,25 s");
            Assert.AreEqual(24f, G.range_m, 1e-6f);
            Assert.AreEqual("none", G.sight);
            Assert.AreEqual(1f, G.world_zoom, 1e-6f);
            Assert.IsFalse(G.muzzle_flash, "ohne Mündungsfeuer");
            Assert.AreEqual(0f, G.path_up_h, "ohne Bahnstufe");
            Assert.IsFalse(PC.weapon.eject.enabled, "ohne Hülsen");
            Assert.AreEqual(2, G.portals.Length);
            Assert.AreEqual("A fire portal_a #1AD9FF 1", $"{G.portals[0].name} {G.portals[0].input} {G.portals[0].role} {G.portals[0].color} {G.portals[0].ring}");
            Assert.AreEqual("B aim portal_b #FF7314 -1", $"{G.portals[1].name} {G.portals[1].input} {G.portals[1].role} {G.portals[1].color} {G.portals[1].ring}");
            Assert.AreEqual(10f / 30f, G.ring_turn_s, 1e-5f);
            Assert.IsFalse(PC.CanAim, "kein Zielen");
            Assert.IsFalse(PC.CanReload, "kein Nachladen");
            foreach (var a in new[] { "aim_in", "aim_out", "fire_ads", "fire_hip", "reload_tactical", "reload_empty", "sprint_to_aim", "draw_aim", "reload_to_switch" })
                Assert.IsFalse(PC.HasAction(a), a);
            Assert.IsFalse(PC.HasPose("ads") || PC.HasPose("reload"));
            Assert.IsFalse(PC.HasAnchor("Socket_Eye"));
            Assert.AreEqual("emitter_ring", PC.weapon.live.ring);
            Assert.AreEqual(0.6f, G.kick, 1e-6f, "Kick je Klasse (Werkzeug 0,6)");
            foreach (var a in new[] { "fire_a", "fire_b", "sprint_to_fire" })
                Assert.AreEqual(G.kick, PC.Action(a).kick, 1e-6f, $"{a}: Clip-Kick = gameplay.kick");
            foreach (var d in new[] { D, MP, SR, PR }) Assert.AreEqual(1f, d.gameplay.kick, $"{d.weapon.id}: Kick wie bisher");
            foreach (var core in new[] { "core_a", "core_b", "core_glass" })               // Leuchtkerne und Glas mit eigenem Material (wie Absehen)
                CollectionAssert.DoesNotContain(PC.textures.weapon.objects, core, $"{core} nicht im Atlas");
            foreach (var q in G.portals)
                Assert.IsTrue(PC.Role(q.role).emit_only && PC.Role(q.role).emit > 0, $"{q.role}: reine Emission");
            Assert.AreEqual("", PC.weapon.live.bolt + PC.weapon.live.port, "ohne Verschluss und Klappe");
            var ring = PC.weapon.parts.Single(p => p.id == "emitter_ring").move;
            Assert.AreEqual(120f, ring.a1 - ring.a0, 1e-4f, "eine Dritteldrehung je Wert 1");
            foreach (var (n, sign) in new[] { ("fire_a", 1f), ("fire_b", -1f) })
            {
                var A = PC.Action(n);
                CollectionAssert.AreEqual(new[] { 2 }, A.fire, n);
                var tr = A.mech.Single(m => m.part == "emitter_ring");
                Assert.AreEqual(sign, tr.keys.Last().v, n);
                Assert.AreEqual(10f, tr.keys.First(k => Mathf.Abs(k.v) > 0.99f).f - tr.keys.Last(k => k.v == 0).f, 1e-4f, n + ": 10 Bilder");
            }
            Assert.AreEqual("foregrip", PC.Grip("support").fingers_pose, "Stützhand am Vordergriff (Faust wie an der MP)");
        }

        /// <summary>2.1 A, lange Waffe: Mündung des Impulses im Destiny-Band x 54–59 / y 60–71 % (Gridskipper ≈ 57/61), Kontur bis zum
        /// rechten und unteren Rand. Mit der Hüfte der Automatik lag sie bei x 59,7 % (außerhalb).</summary>
        [Test]
        public void Hueftlage_des_Impulses_im_Band()
        {
            var S = new EgoSolver(PR);
            var E = new EgoScreen(S);
            var o = S.Evaluate(S.StillAction("hip"), 0, new EgoState());
            Vector3 At(string a) => E.ToScreen(o.weapon.MultiplyPoint3x4(V(PR.Anchor(a).pos)));
            Vector3 m = At("Socket_Muzzle"), r = At("Socket_Reticle");
            var pts = new List<Vector2>();
            E.Silhouette(o, pts, arms: false);
            TestContext.WriteLine($"Impuls-Hüfte: Mündung x {m.x:0.0} / y {m.y:0.0} %, Absehen x {r.x:0.0} / y {r.y:0.0} %; " +
                                  $"Waffe x {pts.Min(p => p.x):0.0}–{pts.Max(p => p.x):0.0}, y {pts.Min(p => p.y):0.0}–{pts.Max(p => p.y):0.0} %");
            Assert.That(m.x, Is.InRange(54f, 59f), "Mündung x (lange Waffen 54–59 %)");
            Assert.That(m.y, Is.InRange(60f, 71f), "Mündung y (lange Waffen 60–71 %)");
            Assert.Greater(pts.Max(p => p.x), 99f, "Kontur reicht bis zum rechten Rand");
            Assert.Greater(pts.Max(p => p.y), 99f, "Kontur reicht bis zum unteren Rand");
        }

        /// <summary>Werkzeug-Hüfte nach Portal 2 (M, cubeescape-reference portal2.md): vorderes Rohrende ≈ 57/75 %, beim Gehen 54–63 / 68–75 %;
        /// die Kerbe (Leitkante) oben auf der Schale ist im Bild; die Stützhand hält den Vordergriff unter der Unterlippe.</summary>
        [Test]
        public void Hueftlage_der_Portalkanone()
        {
            var S = new EgoSolver(PC);
            var E = new EgoScreen(S);
            var o = S.Evaluate(S.StillAction("hip"), 0, new EgoState());
            Vector3 m = E.ToScreen(o.weapon.MultiplyPoint3x4(V(PC.Anchor("Socket_Muzzle").pos)));
            Vector3 kerbe = E.ToScreen(o.weapon.MultiplyPoint3x4(new Vector3(0, 0.070f, 0.174f)));     // f −70, u 174 (Blender: x, −f, u)
            var sup = Pos(o.handL);
            var fg = o.weapon.MultiplyPoint3x4(V(PC.Anchor("Socket_SupportHand").pos));
            TestContext.WriteLine($"Portalkanone-Hüfte: Achskrone x {m.x:0.0} / y {m.y:0.0} %, Kerbe x {kerbe.x:0.0} / y {kerbe.y:0.0} %, " +
                                  $"Stützhand {Vector3.Distance(sup, fg) * 1000:0} mm von Socket_SupportHand");
            Assert.That(m.x, Is.InRange(54f, 63f), "Rohrende x (Portal 2: 54–63 %)");
            Assert.That(m.y, Is.InRange(68f, 76f), "Rohrende y (Portal 2: 68–75 %)");
            Assert.That(kerbe.x, Is.InRange(0f, 100f), "Kerbe im Bild");
            Assert.That(kerbe.y, Is.InRange(0f, 100f), "Kerbe im Bild");
            Assert.Less(Vector3.Distance(sup, fg), 0.08f, "Stützhand am Vordergriff");
        }

        /// <summary>Visier-Standard 3 am Scout in Unity: eine Kamera, das Modell bleibt ungezoomt; im Zielen (Augenpunkt 90 mm hinter dem
        /// Objektivring, 75°) misst die lichte Öffnung (Objektivlinse) 20–26 % der Bildbreite; Okular, Rohr und Türme (ads_hide) sind im
        /// Zielen aus und in der Hüfte da; das Absehen chevron liegt auf der Bildmitte; der Weg dorthin: aim_in schaltet einmal um.</summary>
        [Test]
        public void Zielfernrohr_Oeffnung_und_Teile_im_Zielen()
        {
            var S = new EgoSolver(SR);
            var E = new EgoScreen(S);
            var ads = S.Evaluate(S.StillAction("ads"), 0, new EgoState());
            var hip = S.Evaluate(S.StillAction("hip"), 0, new EgoState());
            Assert.IsTrue(ads.adsHidden, "Zielen: Teile mit ads_hide aus");
            Assert.IsFalse(hip.adsHidden, "Hüfte: Zielfernrohr ganz");
            var g = SR.mesh_bounds.objects.First(b => b.name == "scope_glass");       // Objektivlinse im Waffenrahmen
            Vector3 c = (V(g.min) + V(g.max)) / 2, hx = new Vector3((g.max[0] - g.min[0]) / 2, 0, 0);
            Vector3 l = E.ToScreen(ads.weapon.MultiplyPoint3x4(c + hx)), rr = E.ToScreen(ads.weapon.MultiplyPoint3x4(c - hx));
            float share = Mathf.Abs(l.x - rr.x);
            Vector3 ret = E.ToScreen(ads.weapon.MultiplyPoint3x4(V(SR.Anchor("Socket_Reticle").pos)));
            TestContext.WriteLine($"Scout im Zielen: lichte Öffnung {share:0.0} % B (Glas Ø {(g.max[0] - g.min[0]) * 1000:0.0} mm), Absehen x {ret.x:0.00} / y {ret.y:0.00} %");
            Assert.That(share, Is.InRange(20f, 26f), "Öffnung im Zielen 20–26 % B (Visier-Standard 3, Zielfernrohr)");
            Assert.AreEqual(50f, ret.x, 0.5f, "Absehen auf der Bildmitte (±0,5 %: Atmen und Feder im Standbild)");
            Assert.AreEqual(50f, ret.y, 0.5f);
            Assert.AreEqual("reticle_cyan", SR.Part("sight_reticle").role, "Absehen im Glas Cyan (chevron fein aus reticles.DEFAULTS, Teil des Modells)");
            Assert.IsFalse(SR.Part("sight_reticle").ads_hide || SR.Part("scope_glass").ads_hide, "Absehen und Objektivlinse bleiben im Zielen");
            var A = SR.Action("aim_in");
            var st = new EgoState();
            var seq = new List<bool>();
            for (int f = 0; f <= A.frames + 12; f++) seq.Add(S.Evaluate(A, Mathf.Min(f, A.frames), st).adsHidden);
            int at = seq.IndexOf(true);
            TestContext.WriteLine($"aim_in (Clip, 30/s): Teile aus ab Bild {at} von {A.frames}");
            Assert.IsFalse(seq[0]);
            Assert.Greater(at, 0, "aim_in: Zielfernrohr wird umgeschaltet");
            Assert.IsTrue(seq.Skip(at).All(x => x), "einmal umschalten, kein Flackern");
        }

        /// <summary>Einzelfeuer im Clip (0.20, ego.trigger_on): beim Scout wird der Abzug je Schuss gezogen und dazwischen losgelassen (ein
        /// Zug je Schuss), bei Automatik und MP bleibt er über die ganze Salve gezogen.</summary>
        [Test]
        public void Einzelfeuer_im_Clip_ein_Zug_je_Schuss()
        {
            foreach (var d in new[] { D, MP, SR, PR })
            {
                var S = new EgoSolver(d);
                var A = d.Action("fire_hip");
                var st = new EgoState();
                int pulls = 0;
                float prev = 0;
                for (int f = 0; f <= A.frames; f++)
                {
                    float t = S.Evaluate(A, f, st).mech[d.weapon.live.trigger];
                    if (t > 0.5f && prev <= 0.5f) pulls++;
                    prev = t;
                }
                TestContext.WriteLine($"{d.weapon.id}: {A.fire.Length} Schüsse, {pulls} Züge am Abzug");
                Assert.AreEqual(d.gameplay.Semi ? A.fire.Length : 1, pulls, d.weapon.id);
            }
        }

        /// <summary>Entscheidung 97 A (Nutzer 26.10.2026: „A“): Waffenatlanten und Skins je Waffe unter der Grenze (≈ ¼ von BASIC-06 vorher,
        /// 191 MB), abgelegt nach export_unity.TEXTURE_STORE (albedo JPG 4096, spec PNG 2048, normal PNG 8 bit 4096, ao PNG 2048); Unity
        /// importiert die Dateien in dieser Größe.</summary>
        [Test]
        public void Texturen_je_Waffe_unter_der_Grenze()
        {
            foreach (var d in All)
            {
                var T = d.weaponTextures;
                Assert.IsNotNull(T?.store, $"{d.weapon.id}: Ablage (textures.store) fehlt");
                Assert.AreEqual(4, T.store.Length);
                Assert.That(T.limit_mb, Is.InRange(1f, 50f), "Grenze ≤ 50 MB je Waffe");
                var files = new HashSet<string> { T.weapon.albedo, T.weapon.spec, T.weapon.normal, T.weapon.ao };
                foreach (var s in T.skins) { files.Add(s.albedo); files.Add(s.spec); }
                long bytes = files.Sum(f => new FileInfo($"{Gen}/Textures/{f}").Length);
                TestContext.WriteLine($"{d.weapon.id}: {files.Count} Dateien, {bytes / 1e6:0.0} MB (Grenze {T.limit_mb} MB)");
                Assert.LessOrEqual(bytes / 1e6, T.limit_mb, $"{d.weapon.id}: Texturen über der Grenze");
                foreach (var st in T.store)
                {
                    string f = st.kind == "albedo" ? T.weapon.albedo : st.kind == "spec" ? T.weapon.spec : st.kind == "normal" ? T.weapon.normal : T.weapon.ao;
                    StringAssert.EndsWith("." + st.ext, f, $"{d.weapon.id} {st.kind}");
                    var tex = AssetDatabase.LoadAssetAtPath<Texture2D>($"{Gen}/Textures/{f}");
                    Assert.IsNotNull(tex, f);
                    Assert.AreEqual(st.size, tex.width, $"{f}: Kantenlänge");
                }
            }
        }

        // ---------------------------------------------------------------- Ego-Übertrag je Klasse 0.18 (Entscheidungsliste Schritt 6)
        /// <summary>Werte je Klasse aus den Daten (ego.CLASSES), keine Sonderlogik nach Waffen-ID: die MP fliegt in 3 Bildern bei 30/s ins
        /// Zielen (4d: Destiny-MP 8–12 Bilder bei 60/s bis Ruhe), aim_out im selben Verhältnis; die Automatik bleibt bei 0,33 s (Destiny 20
        /// Bilder). Spielwerte und Weltzoom kommen aus der Klasse, das Hüft-Fadenkreuz der MP aus dem Katalog (Ring mit vier Marken, 6,1 % H).</summary>
        [Test]
        public void Werte_je_Klasse()
        {
            Assert.AreEqual(10, D.Action("aim_in").frames, "Automatik aim_in 10 Bilder bei 30/s");
            Assert.AreEqual(10f / 30f, D.Action("aim_in").frames / (float)D.fps, 1e-6f, "Automatik 0,33 s wie bisher");
            Assert.AreEqual(8, D.Action("aim_out").frames, "Automatik aim_out wie bisher");
            Assert.AreEqual("auto_rifle", D.profile.type);
            Assert.AreEqual("submachine_gun", MP.profile.type);
            var ai = MP.Action("aim_in");
            Assert.AreEqual(3, ai.frames, "MP aim_in 3 Bilder bei 30/s");
            Assert.LessOrEqual(ai.weapon.Last(k => k.pose == "ads").f, 3f);
            Assert.AreEqual(2.7f, ai.weapon.First(k => k.pose == "ads").f, 1e-4f, "Schlüssel mitgestreckt");
            Assert.AreEqual(3, ai.events.Single(e => e.name == "Aimed").f);
            Assert.AreEqual(2.4f, MP.Action("aim_out").weapon.Last().f, 1e-4f, "aim_out 8 → 2,4 Bilder");
            string J(object x) => JsonUtility.ToJson(x);
            string Hold = MP.Grip("support").fingers_pose;
            Assert.AreEqual("foregrip", Hold, "Stützhand am Vordergriff");
            foreach (var A in MP.actions)                         // sonst alles wie die Automatik; die Stützhand hält mit der Fingerstellung ihres Griffs
            {
                if (A.name == "aim_in" || A.name == "aim_out") continue;
                var B = D.Action(A.name);
                Assert.AreEqual(J(B.weapon) + J(B.L) + J(B.R) + J(B.fR) + J(B.mech) + J(B.events) + J(B.bob) + B.frames + string.Join(",", B.fire),
                                J(A.weapon) + J(A.L) + J(A.R) + J(A.fR) + J(A.mech) + J(A.events) + J(A.bob) + A.frames + string.Join(",", A.fire), A.name);
                CollectionAssert.AreEqual(B.fL.Select(k => k.pose == "underhand" ? Hold : k.pose == "open" ? "foregrip_open" : k.pose),
                                          A.fL.Select(k => k.pose), A.name + " fL (Griff-Ersetzungen underhand → foregrip, open → foregrip_open)");
            }
            Assert.AreEqual(1.45f, MP.gameplay.world_zoom, 1e-6f, "Weltzoom MP (1.2 A)");
            Assert.AreEqual(1.9f, D.gameplay.world_zoom, 1e-6f, "Weltzoom Automatik");
            Assert.AreEqual(720, MP.gameplay.rpm);
            Assert.AreEqual(30, MP.gameplay.magazine);
            Assert.AreEqual("circle_cross", MP.gameplay.hip.kind, "Hüftform MP (4.2 A: bleibt circle_cross)");
            Assert.AreEqual(0.061f, MP.gameplay.hip.share_h, 1e-6f, "5,9–6,3 % H (Glidepath)");
            Assert.AreEqual("", MP.gameplay.hip.sprint.kind, "im Sprint aus");
            Assert.IsTrue(MP.weapon.eject.enabled, "MP wirft Hülsen aus (Feld EJECT)");
            Assert.AreEqual("pistol", MP.weapon.eject.@case);
            Assert.AreEqual("bolt", MP.weapon.live.bolt);
            foreach (var n in new[] { "hip", "sprint", "crouch", "air", "lowered", "ads", "reload" })
                StringAssert.DoesNotContain("submachine", D.Pose(n).src, "Automatik unverändert");
            Assert.AreNotEqual(JsonUtility.ToJson(D.Pose("hip")), JsonUtility.ToJson(MP.Pose("hip")), "MP hat eine eigene Hüfte");
        }

        /// <summary>Hält die Hand im Bild f ganz am Griff g (Schlüssel davor und danach sind g ohne Versatz)?</summary>
        static bool AtGrip(HandKey[] keys, float f, string g)
        {
            bool At(HandKey k) => k.kind == "grip" && k.grip == g && k.offset.All(v => v == 0);
            var before = keys.LastOrDefault(k => k.f <= f + 1e-4f) ?? keys[0];
            var after = keys.FirstOrDefault(k => k.f >= f - 1e-4f) ?? keys[keys.Length - 1];
            return At(before) && At(after);
        }

        /// <summary>Nutzerhinweis 26.10.2026 („Der Daumen bei der MP sitzt irgendwie ungünstig“): mit der Fingerstellung underhand stand die
        /// Daumenspitze der Stützhand 12–15 mm über dem Vorbau (durch ihn hindurch). Mit foregrip liegt sie in allen Bildern, in denen die
        /// Hand am Vordergriff hält, unter der Vorbau-Oberkante und nicht im Vorbau.</summary>
        [Test]
        public void Daumen_der_Stuetzhand_nicht_im_Vorbau()
        {
            var S = new EgoSolver(MP);
            var sh = MP.mesh_bounds.objects.First(b => b.name == "shroud");
            Vector3 mn = V(sh.min), mx = V(sh.max);
            int it = S.SegmentIndex("t_2"), n = 0;
            float worst = float.MinValue;
            string at = "";
            void Check(string lab, EgoOutput o)
            {
                var tip = o.weapon.inverse.MultiplyPoint3x4(o.segL[it].MultiplyPoint3x4(new Vector3(0, 0, MP.arm.thumb_links.Last())));
                bool inside = tip.x > mn.x && tip.x < mx.x && tip.y > mn.y && tip.y < mx.y && tip.z > mn.z && tip.z < mx.z;
                Assert.IsFalse(inside, $"{lab}: Daumenspitze im Vorbau ({tip * 1000:F0} mm)");
                Assert.Less(tip.z, mx.z, $"{lab}: Daumenspitze über dem Vorbau ({tip.z * 1000:0} mm, Oberkante {mx.z * 1000:0} mm)");
                if (tip.z > worst) { worst = tip.z; at = lab; }
                n++;
            }
            foreach (var p in new[] { "hip", "ads", "sprint", "crouch", "lowered" })
                Check("Haltung " + p, S.Evaluate(S.StillAction(p), 0, new EgoState()));
            foreach (var A in MP.actions)
            {
                var st = new EgoState();
                for (int f = 0; f <= A.frames; f++)
                {
                    var o = S.Evaluate(A, f, st);
                    if (AtGrip(A.L, f, "support")) Check($"{A.name}:{f}", o);
                }
            }
            TestContext.WriteLine($"{n} Bilder mit der Stützhand am Vordergriff; Daumenspitze höchstens {worst * 1000:0} mm (Vorbau {mn.z * 1000:0}–{mx.z * 1000:0} mm) bei {at}");
        }

        /// <summary>Entscheidungsliste 2b / 2.1 A: Hüftlage der MP im Band der Kurzwaffen (x 53–71 / y 59–84 %, Destiny-MP Mündung ≈ 57/61 und
        /// 58/62, Holo ≈ 62–68/57–58), gemessen wie das Ego-Still; die Automatik bleibt im Band der langen Waffen.</summary>
        [Test]
        public void Hueftlage_der_MP_im_Band()
        {
            var S = new EgoSolver(MP);
            var E = new EgoScreen(S);
            var o = S.Evaluate(S.StillAction("hip"), 0, new EgoState());
            Vector3 At(string a) => E.ToScreen(o.weapon.MultiplyPoint3x4(V(MP.Anchor(a).pos)));
            Vector3 m = At("Socket_Muzzle"), r = At("Socket_Reticle");
            var pts = new List<Vector2>();
            E.Silhouette(o, pts, arms: false);
            TestContext.WriteLine($"MP-Hüfte: Mündung x {m.x:0.0} / y {m.y:0.0} %, Absehen x {r.x:0.0} / y {r.y:0.0} %; Waffe x {pts.Min(p => p.x):0.0}–" +
                                  $"{pts.Max(p => p.x):0.0}, y {pts.Min(p => p.y):0.0}–{pts.Max(p => p.y):0.0} %");
            Assert.That(m.x, Is.InRange(53f, 71f), "Mündung x (Kurzwaffen 53–71 %)");
            Assert.That(m.y, Is.InRange(59f, 84f), "Mündung y (Kurzwaffen 59–84 %)");
            Assert.That(m.x, Is.InRange(55f, 61f), "Mündung x nahe Destiny-MP 57–58 %");
            Assert.That(m.y, Is.InRange(59f, 66f), "Mündung y nahe Destiny-MP 61–62 %");
            Assert.That(r.x, Is.InRange(60f, 70f), "Absehen x nahe Destiny-Holo 62–68 %");
            Assert.Greater(pts.Max(p => p.y), 99f, "Kontur reicht bis zum unteren Rand");
        }

        /// <summary>Entscheidungsliste 3b / 3.2 A: Sprint-Trageform je Klasse – die MP tief und nach links gerollt (Oberseite zeigt im Bild nach
        /// links, Destiny-MP Mündung ≈ 43/80, Holo ≈ 52/72), die Automatik quer mit der Oberseite nach rechts (−35°, wie bisher).</summary>
        [Test]
        public void Sprint_Rollrichtung_je_Klasse()
        {
            foreach (var d in All)
            {
                var S = new EgoSolver(d);
                var E = new EgoScreen(S);
                var o = S.Evaluate(S.StillAction("sprint"), 0, new EgoState());
                var up = o.weapon.MultiplyVector(new Vector3(0, 0, 1));           // Oberseite der Waffe im Blender-Kameraraum (+X = links)
                Vector3 m = E.ToScreen(o.weapon.MultiplyPoint3x4(V(d.Anchor("Socket_Muzzle").pos)));
                Vector3 r = E.ToScreen(o.weapon.MultiplyPoint3x4(V(d.Anchor(d.HasAnchor("Socket_Reticle") ? "Socket_Reticle" : "Socket_Muzzle").pos)));
                float roll = Mathf.Atan2(up.x, up.z) * Mathf.Rad2Deg;            // > 0: Oberseite nach links geneigt
                TestContext.WriteLine($"{d.weapon.id} Sprint: Oberseite {roll:0.0}° (links +), Mündung {m.x:0.0}/{m.y:0.0} %, Absehen {r.x:0.0}/{r.y:0.0} %");
                if (d.profile.type == "submachine_gun")
                {
                    Assert.Greater(roll, 20f, "MP nach links gerollt");
                    Assert.That(m.x, Is.InRange(38f, 48f), "Mündung x nahe Destiny-MP 43 %");
                    Assert.That(m.y, Is.InRange(75f, 85f), "Mündung y nahe Destiny-MP 80 %");
                    Assert.That(r.y, Is.InRange(66f, 78f), "Holo tief, nahe Destiny-MP 72 %");
                }
                else if (d.profile.type == "portal_cannon")
                {
                    Assert.Greater(roll, 15f, "Werkzeug wie Kurzwaffen nach links gerollt (E, Klasse Werkzeug)");
                    Assert.That(m.x, Is.InRange(38f, 50f), "Achskrone tief links wie die MP-Mündung");
                    Assert.That(m.y, Is.InRange(74f, 86f));
                }
                else if (d.profile.type == "combat_bow")
                {
                    // Bogen (0.33 P4, cubeescape-reference destiny2:221): Riser ≈ 20° nach rechts geneigt – im Bild, nicht als Rollwinkel (der
                    // Bogen zeigt im Sprint steil nach unten)
                    Vector3 g = E.ToScreen(o.weapon.MultiplyPoint3x4(Vector3.zero)), t = E.ToScreen(o.weapon.MultiplyPoint3x4(new Vector3(0, 0, 0.3f)));
                    Assert.Greater(t.x, g.x, "Bogen: Riser oben nach rechts geneigt");
                }
                else Assert.Less(roll, -10f, "Gewehre: Oberseite nach rechts (quer, wie bisher)");
            }
            Assert.AreEqual(JsonUtility.ToJson(D.Action("sprint").bob), JsonUtility.ToJson(MP.Action("sprint").bob), "Frequenz und Hub wie bisher (3c)");
        }

        // ---------------------------------------------------------------- Weltzoom und Hüft-Fadenkreuz 0.13
        /// <summary>Entscheidungsliste 1.2 A: Weltzoom (Bildmaßstab, Visier-Standard 3) nach Glidepath – Scout 2,0 statt 2,9, Handfeuerwaffe
        /// 1,15 statt 1,5, MP 1,45 statt 1,25, übrige Klassen unverändert; die Pilot-Automatik zoomt mit ihrem Klassenwert 1,9 (vorher
        /// fest 1,35 für alle) und das Spiel nutzt ihn.</summary>
        [Test]
        public void Weltzoom_je_Klasse()
        {
            var G = D.gameplay;
            var want = new Dictionary<string, float> { ["scout_rifle"] = 2.0f, ["hand_cannon"] = 1.15f, ["submachine_gun"] = 1.45f,
                ["auto_rifle"] = 1.9f, ["pulse_rifle"] = 2.0f, ["machine_gun"] = 1.9f, ["sidearm"] = 1.25f, ["grenade_launcher"] = 1.4f,
                ["linear_fusion_rifle"] = 3.0f, ["fusion_rifle"] = 1.45f, ["trace_rifle"] = 1.8f,
                ["sniper_rifle"] = 4.0f };   // 0.33: Scharfschütze ≈ 4× (Far Future, destiny2:496); Fusionen nach Gapfill (REF 0.34)
            foreach (var kv in want) Assert.AreEqual(kv.Value, G.ZoomFor(kv.Key), 1e-4f, kv.Key);
            Assert.AreEqual(17, G.zoom_table.Length, "alle Waffentypen");
            Assert.AreEqual("auto_rifle", G.weapon_type);
            Assert.AreEqual("reflex", G.sight);
            Assert.AreEqual(G.ZoomFor(G.weapon_type), G.world_zoom, 1e-6f, "Pilot zoomt mit dem Wert seiner Klasse");
            foreach (var d in All)
                Assert.AreEqual(d.gameplay.sight == "none" ? 1f : d.gameplay.ZoomFor(d.gameplay.weapon_type), d.gameplay.world_zoom, 1e-6f, d.weapon.id);
            TestContext.WriteLine($"Weltzoom Pilot {G.world_zoom}, Scout {G.ZoomFor("scout_rifle")}, " +
                                  $"Handfeuerwaffe {G.ZoomFor("hand_cannon")}, MP {G.ZoomFor("submachine_gun")}");
        }

        /// <summary>Entscheidungsliste 4.2 A: Hüftform der Automatik `ring_dot` (vorher `cross`) mit 3,2 % H nach Glidepath, weiß, fein;
        /// im Sprint nur „^“ (`caret`) mit 1,5 % H; Aufgehprofil `auto`. Das gezeichnete Außenmaß trifft die Größe auf 0,5 px.</summary>
        [Test]
        public void Hueftform_der_Automatik_aus_dem_Katalog()
        {
            var H = D.gameplay.hip;
            Assert.AreEqual("ring_dot", H.kind);
            Assert.AreEqual(0.032f, H.share_h, 1e-6f);
            Assert.AreEqual("#EEF2F5", H.color, "weiß");
            Assert.AreEqual(0.65f, H.weight, 1e-6f, "Linienstärke fein");
            Assert.AreEqual("caret", H.sprint.kind);
            Assert.AreEqual(0.015f, H.sprint.share_h, 1e-6f);
            Assert.AreEqual("auto", H.spread.id);
            var R = new HipReticle(H);
            foreach (float h in new[] { 720f, 1080f })
            {
                Assert.AreEqual(H.share_h * h, R.ExtentPx(h), 0.5f, $"Außenmaß gerechnet bei {h} px Höhe");
                var mh = R.Mask(h);                              // unabhängig: Rahmen der Maskenpixel mit Deckung ≥ 50 %
                int x0 = int.MaxValue, x1 = -1, y0 = int.MaxValue, y1 = -1;
                for (int y = 0; y < mh.height; y++)
                    for (int x = 0; x < mh.width; x++)
                        if (mh.GetPixel(x, y).a >= 0.5f * H.opacity) { x0 = Mathf.Min(x0, x); x1 = Mathf.Max(x1, x); y0 = Mathf.Min(y0, y); y1 = Mathf.Max(y1, y); }
                float seen = Mathf.Max(x1 - x0 + 1, y1 - y0 + 1);
                TestContext.WriteLine($"Außenmaß bei {h} px Höhe: Soll {H.share_h * h:0.0} px, Maske {seen} px");
                Assert.AreEqual(H.share_h * h, seen, 1.0f, $"Außenmaß in der Maske bei {h} px Höhe");
            }
            R.Release();
            var m = R.Mask(1080);
            Assert.Greater(m.GetPixel(m.width / 2, m.height / 2).a, 0.8f, "Punkt in der Mitte");
            var ring = H.prims.First(p => p.t == "ring");        // Ringmitte bei Linienstärke fein (innen fest, Dicke · weight)
            float ringR = (ring.ri + (ring.r - ring.ri) * H.weight / 2) * R.PxPerMm(1080);
            Assert.Greater(m.GetPixel(m.width / 2 + Mathf.FloorToInt(ringR), m.height / 2).a / 0.9f, 0.6f, "Ring");
            Assert.Less(m.GetPixel(m.width / 2 + Mathf.FloorToInt(ringR * 0.55f), m.height / 2).a, 0.05f, "frei zwischen Ring und Punkt");
            R.Release();
        }

        /// <summary>Entscheidungsliste 4.1 A: das Hüft-Fadenkreuz geht beim Schießen nach `reticles.SPREAD` auf – Impuls per_shot je
        /// Schuss bis max, Abklingen mit recover_s, Laufen addiert move (reticles.simulate); vorher gab es kein Aufgehen.</summary>
        [Test]
        public void Hueft_Fadenkreuz_geht_nach_SPREAD_auf()
        {
            var H = D.gameplay.hip;
            var S = H.spread;
            var R = new HipReticle(H);
            float e0 = R.ExtentPx(1080);
            Assert.AreEqual(S.@base, R.spread, 1e-6f);
            R.Kick();
            Assert.AreEqual(S.@base + S.per_shot, R.spread, 1e-5f, "ein Schuss");
            Assert.AreEqual(e0 + 2 * S.per_shot * R.PxPerMm(1080), R.ExtentPx(1080), 0.01f, "Ring wächst um per_shot (grow 1)");
            const float dt = 1f / 60f;
            R.Decay(dt, 0);
            Assert.AreEqual(S.@base + S.per_shot * Mathf.Exp(-dt / S.recover_s), R.spread, 1e-5f, "Abklingen");
            for (int k = 0; k < 20; k++) R.Kick();
            Assert.AreEqual(S.max, R.spread, 1e-6f, "begrenzt");
            for (int k = 0; k < 600; k++) R.Decay(dt, 0);
            Assert.AreEqual(S.@base, R.spread, 1e-3f, "zurück zur Basis");
            for (int k = 0; k < 600; k++) R.Decay(dt, 1);
            Assert.AreEqual(S.@base + S.move, R.spread, 1e-3f, "Laufen");
            // wie reticles.simulate('auto', Schüsse bei 720/min, 30/s): je Bild erst abklingen, dann die Schüsse des Bilds
            var R2 = new HipReticle(H);
            float s = S.@base, t = 0;
            int shot = 0;
            for (int i = 0; i <= 30; i++, t = i / 30f)
            {
                R2.Decay(1f / 30f, 0);
                s = S.@base + (s - S.@base) * Mathf.Exp(-(1f / 30f) / S.recover_s);
                while (shot < 6 && shot * 60f / 720f <= t) { R2.Kick(); s = Mathf.Min(S.max, s + S.per_shot); shot++; }
                Assert.AreEqual(s, R2.spread, 1e-5f, $"Bild {i}");
            }
            TestContext.WriteLine($"auto: Außenmaß {e0:0.0} px → nach 6 Schuss {R2.ExtentPx(1080) - 0:0.0} px bei 1080 px Höhe; max {S.max} mm");
        }

        // ---------------------------------------------------------------- Bewegungsgefühl 0.10
        /// <summary>Jede Aktion, die im Zielen endet, bringt das Absehen von seiner Seite auf die Mitte, ohne darüber hinaus zu schwingen
        /// (0.9: 3,3° über die Mitte bei aim_in, „Wippen kurz vor dem Visier“). Gemessen wie in Blender: Richtung Auge → Socket_Reticle.</summary>
        [Test]
        public void Zielen_landet_ohne_Ueberschwingen()
        {
            var S = new EgoSolver(D);
            Vector3 ret = Vector3.zero;
            foreach (var a in D.weapon.anchors) if (a.id == "Socket_Reticle") ret = new Vector3(a.pos[0], a.pos[1], a.pos[2]);
            int n = 0;
            foreach (var A in D.actions)
            {
                if (!A.EndsInAds || A.name == "fire_ads") continue;
                var st = new EgoState();
                float first = float.NaN, worst = 0, atEnd = 0;
                for (int f = 0; f <= A.frames + 20; f++)
                {
                    var t = S.Evaluate(A, Mathf.Min(f, A.frames), st).weapon.MultiplyPoint3x4(ret);
                    float az = Mathf.Atan2(-t.x, -t.y) * Mathf.Rad2Deg;             // Blender-Kameraraum: rechts −X, vorn −Y
                    if (float.IsNaN(first)) first = az;
                    worst = Mathf.Max(worst, -Mathf.Sign(first) * az);            // Ausschlag über die Mitte zur anderen Seite
                    if (f == A.frames) atEnd = Mathf.Abs(az);
                }
                TestContext.WriteLine($"{A.name}: Start {first:0.00}°, Überschwingen {worst:0.00}°, Rest am Ende {atEnd:0.00}°");
                Assert.Less(worst, 0.3f, $"{A.name}: Absehen schwingt {worst:0.00}° über die Mitte (Start {first:0.0}°)");
                Assert.Less(atEnd, 1.5f, $"{A.name}: Absehen hängt am Ende der Aktion {atEnd:0.0}° hinterher");
                n++;
            }
            Assert.GreaterOrEqual(n, 3, "aim_in, sprint_to_aim, draw_aim");
        }

        /// <summary>Sprint-Wippen: vertikal ein Hub je Schritt (2 je Periode), wie Destiny 2 ≈ 3,16 Schritte/s – vorher 6/s („tapsig“).
        /// Hub (3.1 A, 0.15) gemessen wie in Schritt 2 am Bild, hier an der Silhouette von Waffe und Armen (Kanten der Netzgrenzen) über
        /// die Sprintschleife: Oberkante vertikal ≈ 10 % H, linke Kante seitlich ≈ 13 % B wie die Destiny-Automatik (10–11 % H / 13 % B);
        /// bis 0.14 am Unity-Bild 5,1–5,7 % H / 7,0–8,7 % B.</summary>
        [Test]
        public void Sprintschritt_wie_ein_Laeufer()
        {
            var B = D.Action("sprint").bob;
            float steps = 2f * D.fps / B.period;
            Assert.That(steps, Is.InRange(2.9f, 3.4f), $"Sprint: {steps:0.00} Schritte/s (Destiny 2: 3,16 Hz, Motiongen REF 0.23)");
            Assert.IsTrue(B.u, "Sprint-Bahn als U-Bogen (oben an den Seitenumkehren) wie Destiny 2");
            var W = D.Action("walk").bob;
            Assert.Less(2f * D.fps / W.period, steps, "Gehen langsamer als Sprint");

            var S = new EgoSolver(D);
            var E = new EgoScreen(S);
            var A = D.Action("sprint");
            var st = new EgoState();
            var pts = new List<Vector2>();
            float t0 = float.MaxValue, t1 = float.MinValue, l0 = float.MaxValue, l1 = float.MinValue;
            for (int f = 0; f <= A.frames; f++)
            {
                var o = S.Evaluate(A, f, st);
                if (f < B.start + 4 || f > B.end - 4) continue;              // volle Wipp-Weite (4 Bilder Ein-/Ausblenden)
                E.Silhouette(o, pts);
                float top = pts.Min(p => p.y), left = pts.Min(p => p.x);
                t0 = Mathf.Min(t0, top); t1 = Mathf.Max(t1, top); l0 = Mathf.Min(l0, left); l1 = Mathf.Max(l1, left);
            }
            Assert.GreaterOrEqual(B.end - B.start - 8, B.period, "mindestens eine ganze Seitenperiode ausgewertet");
            TestContext.WriteLine($"Sprint-Hub an der Silhouette: Oberkante {t1 - t0:0.0} % H (y {t0:0.0}–{t1:0.0}), linke Kante " +
                                  $"{l1 - l0:0.0} % B (x {l0:0.0}–{l1:0.0}); Hub {B.amp[0] * 1000:0} / {B.amp[1] * 1000:0} mm, Rollen ±{B.roll}°");
            Assert.That(t1 - t0, Is.InRange(8.5f, 12.5f), "vertikal ≈ 10 % H (Destiny-Automatik 10–11 % H)");
            Assert.That(l1 - l0, Is.InRange(11f, 15.5f), "seitlich ≈ 13 % B (Destiny-Automatik 13 % B)");
        }

        // ---------------------------------------------------------------- Haltung 0.15
        /// <summary>Entscheidungsliste 2.1 A: in der Hüfte liegt die Mündung rechts unter der Mitte wie bei Destiny (lange Waffen, 21
        /// Beispiele, Motiongen huefte › 4): x 54–59 / y 60–71 %, die hintere Visieröffnung 7–34 pp rechts der Mündung, die Kontur reicht
        /// bis zum rechten und unteren Rand. Gemessen wie das Ego-Still (Bild 0). Bis 0.14 Mündung x 58,8 / y 49,6 % (10 pp zu hoch).</summary>
        [Test]
        public void Hueftlage_im_Destiny_Band()
        {
            var S = new EgoSolver(D);
            var E = new EgoScreen(S);
            var o = S.Evaluate(S.StillAction("hip"), 0, new EgoState());
            Vector3 At(string a) => E.ToScreen(o.weapon.MultiplyPoint3x4(V(D.Anchor(a).pos)));
            Vector3 m = At("Socket_Muzzle"), s = At("Socket_Sight"), r = At("Socket_Reticle");
            var pts = new List<Vector2>();
            E.Silhouette(o, pts, arms: false);
            TestContext.WriteLine($"Hüfte: Mündung x {m.x:0.0} / y {m.y:0.0} %, Visier hinten x {s.x:0.0} / y {s.y:0.0} % ({s.x - m.x:0.0} pp rechts), " +
                                  $"Absehen x {r.x:0.0} / y {r.y:0.0} %; Waffe x {pts.Min(p => p.x):0.0}–{pts.Max(p => p.x):0.0}, y {pts.Min(p => p.y):0.0}–{pts.Max(p => p.y):0.0} %");
            Assert.That(m.x, Is.InRange(54f, 59f), "Mündung x (Destiny 54–59 %)");
            Assert.That(m.y, Is.InRange(60f, 71f), "Mündung y (Destiny 60–71 %)");
            Assert.That(s.x - m.x, Is.InRange(7f, 34f), "hintere Visieröffnung rechts der Mündung (Destiny 7–34 pp)");
            Assert.Greater(pts.Max(p => p.x), 99f, "Kontur reicht bis zum rechten Rand");
            Assert.Greater(pts.Max(p => p.y), 99f, "Kontur reicht bis zum unteren Rand");
        }

        // ---------------------------------------------------------------- Mündungsfeuer und Hülsen 0.16
        /// <summary>Entscheidungsliste 5.3 A / 5.4 A in den Clips (wie ego_build): jeder Schuss zeigt genau ein Blitzbild bei 30/s, im
        /// Schussbild; jede Hülse erscheint genau einmal, im Schussbild, und fliegt danach im Bild nach rechts, zuletzt nach unten.</summary>
        [Test]
        public void Clips_Blitz_ein_Bild_und_Huelse_je_Schuss()
        {
            var S = new EgoSolver(D);
            var E = new EgoScreen(S);
            Assert.AreEqual(1f / 30, D.motion.flash.dur_s, 1e-5f, "1 Bild bei 30/s");
            Assert.IsTrue(S.Ejects, "BASIC-01 wirft Hülsen aus (weapon.eject)");
            foreach (var name in new[] { "fire_hip", "fire_ads", "sprint_to_fire" })
            {
                var A = D.Action(name);
                var st = new EgoState();
                var flashes = new int[A.fire.Length];
                var first = Enumerable.Repeat(-1, A.fire.Length).ToArray();
                var path = A.fire.Select(_ => new List<Vector3>()).ToArray();
                for (int f = 0; f <= A.frames; f++)
                {
                    var o = S.Evaluate(A, f, st);
                    if (o.flashOn)
                    {
                        flashes[o.flashShot]++;
                        Assert.AreEqual(A.fire[o.flashShot], f, $"{name}: Blitz {o.flashShot} im Bild {f}");
                    }
                    for (int k = 0; k < o.shellCount; k++)
                    {
                        int id = o.shellIds[k];
                        if (first[id] < 0) first[id] = f;
                        path[id].Add(Pos(o.shells[k]));                 // Kameraraum (im Zielen fliegt die Hülse hinter die Kamera)
                    }
                }
                CollectionAssert.AreEqual(Enumerable.Repeat(1, A.fire.Length).ToArray(), flashes, $"{name}: ein Blitzbild je Schuss");
                CollectionAssert.AreEqual(A.fire.Select(x => x + D.motion.eject.delay_frames).ToArray(), first, $"{name}: Hülse im Schussbild");
                for (int k = 0; k < path.Length; k++)
                {
                    var pth = path[k];
                    int want = Mathf.Min(Mathf.CeilToInt(D.motion.eject.life_s * D.fps - 1e-3f), A.frames - first[k] + 1);   // Clipende schneidet ab
                    Assert.AreEqual(want, pth.Count, $"{name}: Hülse {k} life_s lang sichtbar");
                    if (pth.Count < 4) continue;
                    Vector3 s0 = E.ToScreen(pth[0], 0), s1 = E.ToScreen(pth[1], 0);
                    if (s0.z > D.camera.near_m && s1.z > D.camera.near_m) Assert.Greater(s1.x, s0.x, $"{name}: Hülse fliegt im Bild nach rechts");
                    Assert.Less(pth[pth.Count - 1].x, pth[0].x - 0.1f, $"{name}: Hülse fliegt nach rechts (Blender −X)");
                    Assert.Less(pth[pth.Count - 1].z, pth.Max(p => p.z) - 0.05f, $"{name}: Hülse fällt zuletzt nach unten");
                }
            }
        }

        /// <summary>Entscheidungsliste 5.3 A: im Zielen bedeckt der Blitz bei der Automatik (Holo) höchstens ≈ 20 % der lichten Öffnung (Destiny
        /// Chroma Rush ≈ 20 %, Motiongen muendung › 6). Gemessen an jedem Blitzbild von fire_ads: Netz des Blitzes ins Bild projiziert und
        /// gerastert, Öffnung = Glasfenster an seiner Rückseite geschnitten mit demselben Fenster in der Ebene der Haubenkante (wie
        /// ego.flash_cover_ads in ./check); Verdeckung durch die Waffe zählt nicht (obere Schranke).</summary>
        [Test]
        public void Muendungsfeuer_im_Zielen_hoechstens_20_Prozent_der_Oeffnung()
        {
            var S = new EgoSolver(D);
            var E = new EgoScreen(S);
            var A = D.Action("fire_ads");
            var st = new EgoState();
            var F = D.motion.flash;
            var gb = D.mesh_bounds.objects.First(b => b.name == "sight_glass");
            var tb = D.mesh_bounds.objects.First(b => b.name == "sight_frame_trim");
            float worst = 0, sum = 0;
            int n = 0;
            const int N = 120;
            var q = new Vector3[F.verts.Length / 3];
            for (int f = 0; f <= A.frames; f++)
            {
                var o = S.Evaluate(A, f, st);
                if (!o.flashOn) continue;
                var Wg = S.World(o, "sight_glass");
                float x0 = 0, x1 = 100, y0 = 0, y1 = 100;
                foreach (float y in new[] { gb.max[1], tb.min[1] })       // Rückseite des Glases (+Y hinten) und Stirn der Haubenkante (vorn −Y)
                {
                    var a = E.ToScreen(Wg.MultiplyPoint3x4(new Vector3(gb.max[0], y, gb.max[2])), o.camPitch);
                    var b = E.ToScreen(Wg.MultiplyPoint3x4(new Vector3(gb.min[0], y, gb.min[2])), o.camPitch);
                    x0 = Mathf.Max(x0, Mathf.Min(a.x, b.x)); x1 = Mathf.Min(x1, Mathf.Max(a.x, b.x));
                    y0 = Mathf.Max(y0, Mathf.Min(a.y, b.y)); y1 = Mathf.Min(y1, Mathf.Max(a.y, b.y));
                }
                for (int i = 0; i < q.Length; i++)
                    q[i] = E.ToScreen(o.flash.MultiplyPoint3x4(new Vector3(F.verts[3 * i], F.verts[3 * i + 1], F.verts[3 * i + 2])), o.camPitch);
                int hit = 0;
                for (int i = 0; i < N; i++)
                    for (int j = 0; j < N; j++)
                    {
                        float px = x0 + (i + 0.5f) / N * (x1 - x0), py = y0 + (j + 0.5f) / N * (y1 - y0);
                        if (In(F.core_tris) || In(F.flame_tris)) hit++;
                        bool In(int[] t)
                        {
                            for (int k = 0; k < t.Length; k += 3)
                                if (InTri(px, py, q[t[k]], q[t[k + 1]], q[t[k + 2]])) return true;
                            return false;
                        }
                    }
                float c = hit / (float)(N * N);
                worst = Mathf.Max(worst, c);
                sum += c;
                n++;
                if (n == 1) TestContext.WriteLine($"Öffnung im Zielen x {x0:0.0}–{x1:0.0} / y {y0:0.0}–{y1:0.0} %");
            }
            TestContext.WriteLine($"Blitz im Zielen: {n} Blitzbilder, Öffnung bedeckt höchstens {worst * 100:0.0} %, im Mittel {sum / n * 100:0.0} %");
            Assert.AreEqual(A.fire.Length, n, "jedes Schussbild zeigt den Blitz");
            Assert.LessOrEqual(worst, 0.20f, "höchstens 20 % der Holo-Öffnung (5.3 A)");
            Assert.Greater(worst, 0.05f, "der Blitz ist im Visier sichtbar");
        }

        static bool InTri(float x, float y, Vector3 a, Vector3 b, Vector3 c)
        {
            float S(Vector3 p, Vector3 q) => (x - q.x) * (p.y - q.y) - (p.x - q.x) * (y - q.y);
            float d1 = S(a, b), d2 = S(b, c), d3 = S(c, a);
            return !((d1 < 0 || d2 < 0 || d3 < 0) && (d1 > 0 || d2 > 0 || d3 > 0));
        }

        // ---------------------------------------------------------------- Achsen
        [Test]
        public void Achsumrechnung_Blender_nach_Unity()
        {
            var C = D.toUnity;
            Assert.AreEqual(-1f, C.determinant, 1e-6f, "Spiegelung rechts- → linkshändig");
            Assert.That(Vector3.Distance(C.MultiplyVector(new Vector3(0, -1, 0)), Vector3.forward), Is.LessThan(1e-6f), "vorn");
            Assert.That(Vector3.Distance(C.MultiplyVector(new Vector3(0, 0, 1)), Vector3.up), Is.LessThan(1e-6f), "oben");
            Assert.That(Vector3.Distance(C.MultiplyVector(new Vector3(-1, 0, 0)), Vector3.right), Is.LessThan(1e-6f), "rechts");
            // Autorenmaß: Mündung (f vorn, u oben) liegt in Unity vorn und oben
            var muz = C.MultiplyVector(V(D.Anchor("Socket_Muzzle").pos));
            Assert.Greater(muz.z, 0.5f);
            Assert.Greater(muz.y, 0.05f);
            Assert.AreEqual(0f, muz.x, 1e-6f);
            // Drehungen bleiben eigentliche Drehungen; Drehsinn: Rechte-Hand-Drehung in Blender ↔ gleiche Abbildung in Unity
            var R = Rot(Rad(30), new Vector3(0, 0, 1)) * Rot(Rad(-20), new Vector3(1, 0, 0));
            ToUnity(C, R, out _, out var q);
            var p = new Vector3(0.1f, -0.3f, 0.2f);
            Assert.That(Vector3.Distance(q * C.MultiplyVector(p), C.MultiplyVector(R.MultiplyVector(p))), Is.LessThan(1e-5f));
        }

        static Bounds UnityBounds(MeshBound b, Matrix4x4 C)
        {
            var mn = V(b.min);
            var mx = V(b.max);
            var bb = new Bounds(C.MultiplyVector(mn), Vector3.zero);
            for (int i = 0; i < 8; i++)
                bb.Encapsulate(C.MultiplyVector(new Vector3((i & 1) == 0 ? mn.x : mx.x, (i & 2) == 0 ? mn.y : mx.y, (i & 4) == 0 ? mn.z : mx.z)));
            return bb;
        }

        [Test]
        public void FBX_Import_passt_zur_Achsumrechnung()
        {
            foreach (var d in All) FbxImport(d);
        }

        static void FbxImport(EgoFile D)
        {
            var bounds = D.mesh_bounds.objects.ToDictionary(o => o.name);
            int n = 0;
            foreach (var f in new[] { D.weapon.fbx, D.arm.fbx })
            {
                var go = AssetDatabase.LoadAssetAtPath<GameObject>($"{Gen}/{f}");
                Assert.IsNotNull(go, f);
                foreach (var mf in go.GetComponentsInChildren<MeshFilter>(true))
                {
                    Assert.IsTrue(bounds.TryGetValue(mf.name, out var b), $"{mf.name} fehlt in mesh_bounds");
                    var want = UnityBounds(b, D.toUnity);
                    var got = mf.sharedMesh.bounds;
                    Assert.That(Vector3.Distance(got.min, want.min), Is.LessThan(5e-4f), $"{mf.name} min {got.min:F4} statt {want.min:F4}");
                    Assert.That(Vector3.Distance(got.max, want.max), Is.LessThan(5e-4f), $"{mf.name} max {got.max:F4} statt {want.max:F4}");
                    Assert.That(Vector3.Distance(mf.transform.localScale, Vector3.one), Is.LessThan(1e-5f), $"{mf.name} Skalierung");
                    n++;
                }
            }
            Assert.AreEqual(D.weapon.parts.Length + D.arm.pieces.Length * 2, n, "Netzobjekte");
        }

        /// <summary>A6 (A-R13, 0.32): die gewichteten Normalen der Fase (kit.add_bevel, harden_normals) kommen im FBX an und Unity nutzt sie
        /// (Normals „Import“). Am Griff jeder Waffe: Fasen weich (Ecknormale ≠ Flächennormale), Originalflächen flach, und die Normalen
        /// weichen von lageweise geglätteten ab („Calculate“ glättet über die Fase in die Großflächen). Rot mit dem Export vor 0.32
        /// (der Weighted-Normal-Modifikator machte die Griff-Fasen flach: 36 % der Dreiecke weich) und mit Calculate (0 % flach).
        /// Gemessen am Griff (alle Waffen dasselbe Netz BGM-1); harte Teile und Arme nutzen dieselbe Fase (kit.add_bevel).</summary>
        [Test]
        public void FBX_Normalen_gewichtet_an_gefasten_Teilen()
        {
            foreach (var d in All)
            {
                var mi = (ModelImporter)AssetImporter.GetAtPath($"{Gen}/{d.weapon.fbx}");
                Assert.AreEqual(ModelImporterNormals.Import, mi.importNormals, d.weapon.fbx);
                var go = AssetDatabase.LoadAssetAtPath<GameObject>($"{Gen}/{d.weapon.fbx}");
                var mf = go.GetComponentsInChildren<MeshFilter>(true).First(m => m.name == "grip");
                var (soft, flat, dev) = NormalShares(mf.sharedMesh);
                TestContext.WriteLine($"{d.weapon.id} Griff: weich {soft:P0}, flach {flat:P0}, neben geglättet {dev:P0}");
                Assert.That(soft, Is.GreaterThan(0.5f), $"{d.weapon.id} Griff: nur {soft:P0} der Dreiecke weich (Fasen flach)");
                Assert.That(flat, Is.GreaterThan(0.08f), $"{d.weapon.id} Griff: nur {flat:P0} der Dreiecke flach (Großflächen verbogen)");
                Assert.That(dev, Is.GreaterThan(0.25f), $"{d.weapon.id} Griff: nur {dev:P0} der Ecken neben geglätteten Normalen");
            }
        }

        /// <summary>(Anteil der Dreiecke mit einer Ecknormale > 1° neben der Flächennormale, Anteil der Dreiecke mit allen Ecknormalen
        /// ≤ 0,5° daneben, Anteil der Ecken > 2° neben der flächengewichtet je Lage geglätteten Normale).</summary>
        public static (float soft, float flat, float dev) NormalShares(Mesh m)
        {
            var v = m.vertices;
            var n = m.normals;
            var t = m.triangles;
            var acc = new Dictionary<Vector3Int, Vector3>();
            Vector3Int K(Vector3 p) => Vector3Int.RoundToInt(p * 1e5f);          // Lage auf 0,01 mm
            int soft = 0, flat = 0, dev = 0;
            for (int i = 0; i < t.Length; i += 3)
            {
                var c = Vector3.Cross(v[t[i + 1]] - v[t[i]], v[t[i + 2]] - v[t[i]]);   // Länge = doppelte Fläche
                float worst = 0;
                for (int k = 0; k < 3; k++)
                {
                    worst = Mathf.Max(worst, Vector3.Angle(c, n[t[i + k]]));
                    var key = K(v[t[i + k]]);
                    acc[key] = (acc.TryGetValue(key, out var a) ? a : Vector3.zero) + c;
                }
                if (worst > 1f) soft++;
                if (worst <= 0.5f) flat++;
            }
            for (int i = 0; i < t.Length; i++)
                if (Vector3.Angle(n[t[i]], acc[K(v[t[i]])]) > 2f) dev++;
            return (soft / (t.Length / 3f), flat / (t.Length / 3f), dev / (float)t.Length);
        }

        [Test]
        public void FBX_Ruhelagen_und_Anker_wie_in_den_Daten()
        {
            foreach (var d in All) FbxRest(d);
        }

        static void FbxRest(EgoFile D)
        {
            var go = AssetDatabase.LoadAssetAtPath<GameObject>($"{Gen}/{D.weapon.fbx}");
            var all = go.GetComponentsInChildren<Transform>(true).ToDictionary(t => t.name);
            var root = all[D.weapon.root];
            Assert.That(root.localPosition.magnitude, Is.LessThan(1e-6f), "Wurzel im Ursprung");
            Assert.That(Quaternion.Angle(root.localRotation, Quaternion.identity), Is.LessThan(0.01f), "Wurzel ohne Drehung (Achsen gebacken)");
            foreach (var p in D.weapon.parts)
            {
                var want = D.toUnity.MultiplyVector(V(p.rest));
                var got = root.InverseTransformPoint(all[p.id].position);
                Assert.That(Vector3.Distance(got, want), Is.LessThan(1e-4f), $"{p.id}: {got:F4} statt {want:F4}");
                Assert.That(Quaternion.Angle(Quaternion.Inverse(root.rotation) * all[p.id].rotation, Quaternion.identity), Is.LessThan(0.01f), p.id);
            }
            foreach (var a in D.weapon.anchors)
            {
                var want = D.toUnity.MultiplyVector(V(a.pos));
                var got = root.InverseTransformPoint(all[a.id].position);
                Assert.That(Vector3.Distance(got, want), Is.LessThan(1e-4f), $"{a.id}: {got:F4} statt {want:F4}");
            }
            var arms = AssetDatabase.LoadAssetAtPath<GameObject>($"{Gen}/{D.arm.fbx}");
            var at = arms.GetComponentsInChildren<Transform>(true).ToDictionary(t => t.name);
            foreach (var s in D.arm.segments)
                foreach (var side in new[] { "R_", "L_" })
                    Assert.That(at[side + s].position.magnitude, Is.LessThan(1e-5f), side + s);
        }

        // ---------------------------------------------------------------- Material (0.7)
        [Test]
        public void Gebackene_Atlanten_und_UVs()
        {
            foreach (var d in All) Atlanten(d);
        }

        static void Atlanten(EgoFile D)
        {
            Assert.IsNotNull(D.textures?.weapon, "textures fehlt (Export mit Backen)");
            int n = 0;
            foreach (var (fbx, A) in new[] { (D.weapon.fbx, D.textures.weapon), (D.arm.fbx, D.textures.arms) })
            {
                foreach (var (kind, f) in new[] { ("albedo", A.albedo), ("spec", A.spec), ("normal", A.normal), ("ao", A.ao) })
                {
                    var t = AssetDatabase.LoadAssetAtPath<Texture2D>($"{Gen}/Textures/{f}");
                    Assert.IsNotNull(t, f);
                    Assert.AreEqual(fbx == D.weapon.fbx ? Stored(D, kind) : A.size, t.width, f);   // Waffe: Ablage je Kanal (0.20), Arme: Backgröße
                }
                var baked = new HashSet<string>(A.objects);
                var go = AssetDatabase.LoadAssetAtPath<GameObject>($"{Gen}/{fbx}");
                foreach (var mf in go.GetComponentsInChildren<MeshFilter>(true))
                {
                    if (!baked.Contains(mf.name)) continue;
                    var uv = mf.sharedMesh.uv;
                    Assert.AreEqual(mf.sharedMesh.vertexCount, uv.Length, $"{mf.name}: UVs");
                    Assert.IsTrue(uv.All(u => u.x >= -1e-3f && u.x <= 1.001f && u.y >= -1e-3f && u.y <= 1.001f), $"{mf.name}: UV im Atlas");
                    n++;
                }
                var m = AssetDatabase.LoadAssetAtPath<Material>($"{Gen}/Materials/Atlas_{(fbx == D.weapon.fbx ? D.atlas : "arms")}.mat");
                Assert.IsNotNull(m.GetTexture("_BaseMap"));
                Assert.IsNotNull(m.GetTexture("_SpecGlossMap"));
                Assert.AreEqual(0f, m.GetFloat("_WorkflowMode"), "Spezular-Modus");
                Assert.IsNotNull(m.GetTexture("_BumpMap"));
                Assert.IsNotNull(m.GetTexture("_OcclusionMap"));
            }
            Assert.Greater(n, D.slot == 0 ? 150 : 120, $"{D.weapon.id}: gebackene Netzobjekte (Pilot wie bisher > 150)");
        }

        /// <summary>Kantenlänge, mit der ein Kanal des Waffenatlas abgelegt ist (0.20, textures.store), sonst die Backgröße.</summary>
        static int Stored(EgoFile D, string kind) =>
            D.weaponTextures?.store?.FirstOrDefault(s => s.kind == kind)?.size ?? D.textures.weapon.size;

        [Test]
        public void Skins_gebacken_mit_Materialien()
        {
            foreach (var d in All) Skins(d);
        }

        static void Skins(EgoFile D)
        {
            var sk = D.textures.skins;
            // kit.SKINS: 8 Skins; 0.33 P2 „Skins nur bei Bedarf“ (export_unity.SKIN_WEAPONS): neue Waffen zuerst nur der Standard-Atlas
            Assert.That(sk.Length, Is.EqualTo(8).Or.EqualTo(1), $"{D.weapon.id}: 8 Skins oder nur standard");
            Assert.AreEqual("standard", sk[0].name);
            var names = new HashSet<string>();
            foreach (var s in sk)
            {
                Assert.IsTrue(names.Add(s.name), s.name);
                foreach (var (kind, f) in new[] { ("albedo", s.albedo), ("spec", s.spec) })
                {
                    var t = AssetDatabase.LoadAssetAtPath<Texture2D>($"{Gen}/Textures/{f}");
                    Assert.IsNotNull(t, f);
                    Assert.AreEqual(Stored(D, kind), t.width, f);
                }
                if (s.name == "standard") continue;
                var m = AssetDatabase.LoadAssetAtPath<Material>($"{Gen}/Materials/Atlas_{D.atlas}_{s.name}.mat");
                Assert.IsNotNull(m, s.name);
                Assert.AreEqual(Path.GetFileNameWithoutExtension(s.albedo), m.GetTexture("_BaseMap").name, s.name);
                Assert.IsNotNull(m.GetTexture("_BumpMap"), s.name + ": Normale wie Standard");
            }
        }

        [Test]
        public void AgX_LUT_wie_Blender()
        {
            var L = D.textures.lut;
            var t = AssetDatabase.LoadAssetAtPath<Texture2D>($"{Gen}/Textures/{L.file}");
            Assert.AreEqual(L.size * L.size, t.width);
            Assert.AreEqual(L.size, t.height);
            // Mittelgrau 0,18 → Gitterpunkt u = −ev0 / (ev1 − ev0) (genau 20 bei 34 Punkten); Blender AgX „Medium High Contrast“: 0,461
            float gi = -L.ev[0] / (L.ev[1] - L.ev[0]) * (L.size - 1);
            Assert.AreEqual(Mathf.Round(gi), gi, 1e-4f, "Mittelgrau auf dem Gitter");
            Assert.AreEqual(16.29f, L.mid_grey * Mathf.Pow(2, L.ev[1]), 0.05f, "obere Grenze wie AgX (log2 +4,03)");
            int i = Mathf.RoundToInt(gi);
            var c = t.GetPixel(i + i * L.size, i);
            Assert.AreEqual(0.461f, c.r, 0.01f, "Mittelgrau (Blender AgX MHC: 0,18 → 0,461)");
            Assert.AreEqual(c.r, c.g, 0.005f);
            Assert.Less(t.GetPixel(0, 0).r, 0.01f, "Schwarz");
            Assert.Greater(t.GetPixel(t.width - 1, t.height - 1).r, 0.9f, "Weiß");
        }

        // ---------------------------------------------------------------- Arme
        static IEnumerable<(string, EgoOutput)> AllFrames() => All.SelectMany(AllFrames);

        static IEnumerable<(string, EgoOutput)> AllFrames(EgoFile D)
        {
            var S = new EgoSolver(D);
            foreach (var p in D.poses)
                yield return ($"{D.weapon.id} Haltung " + p.name, S.Evaluate(S.StillAction(p.name), 0, new EgoState()));
            foreach (var A in D.actions)
            {
                var st = new EgoState();
                for (int f = 0; f <= A.frames; f++) yield return ($"{D.weapon.id} {A.name}:{f}", S.Evaluate(A, f, st));
            }
        }

        [Test]
        public void Armlaengen_in_allen_Bildern()
        {
            var S = new EgoSolver(D);                         // Segmentreihenfolge gleich für alle Waffen (gemeinsame Arme)
            int iu = S.SegmentIndex("upper"), ifo = S.SegmentIndex("fore"), ih = S.SegmentIndex("hand");
            int n = 0;
            foreach (var (lab, o) in AllFrames())
                foreach (var seg in new[] { o.segR, o.segL })
                {
                    Assert.AreEqual(D.arm.upper_m, Vector3.Distance(Pos(seg[iu]), Pos(seg[ifo])), 1e-4f, lab + " Oberarm");
                    Assert.AreEqual(D.arm.fore_m, Vector3.Distance(Pos(seg[ifo]), Pos(seg[ih])), 1e-4f, lab + " Unterarm");
                    n++;
                }
            Assert.AreEqual(0.32f, D.arm.upper_m, 1e-6f);
            Assert.AreEqual(0.30f, D.arm.fore_m, 1e-6f);
            Assert.Greater(n, 1000);
        }

        [Test]
        public void Handgelenkknick_hoechstens_45_Grad()
        {
            float worst = 0;
            string at = "";
            foreach (var (lab, o) in AllFrames())
                if (o.wristBendMaxDeg > worst) { worst = o.wristBendMaxDeg; at = lab; }
            Assert.AreEqual(45f, D.arm.wrist_target_deg);
            Assert.LessOrEqual(worst, D.arm.wrist_target_deg + 0.01f, $"größter Knick {worst:0.0}° bei {at}");
            TestContext.WriteLine($"größter Handgelenkknick {worst:0.0}° ({at})");
        }

        /// <summary>0.34 „Payload“: jede Klasse hat ihre Wirkung aus ego.PAYLOAD (Art, Einschlagstil vorhanden, Projektile mit
        /// Geschwindigkeit, Schrot mit Kugeln und Kegel, Strahlen mit Breite); gemeinsame Werte in motion.payload.</summary>
        [Test]
        public void Wirkung_je_Klasse_in_ego_json()
        {
            var want = new Dictionary<string, string> {
                ["auto_rifle"] = "hitscan", ["submachine_gun"] = "hitscan", ["scout_rifle"] = "hitscan", ["pulse_rifle"] = "hitscan",
                ["hand_cannon"] = "hitscan", ["sidearm"] = "hitscan", ["sniper_rifle"] = "hitscan", ["machine_gun"] = "hitscan",
                ["shotgun"] = "pellets", ["grenade_launcher"] = "projectile", ["rocket_launcher"] = "projectile", ["trace_rifle"] = "beam",
                ["fusion_rifle"] = "bolts", ["linear_fusion_rifle"] = "rail", ["combat_bow"] = "arrow", ["portal_cannon"] = "none" };
            foreach (var d in All)
            {
                var F = d.gameplay.fx;
                Assert.AreEqual(want[d.gameplay.weapon_type], F.kind, d.weapon.id);
                Assert.IsFalse(string.IsNullOrEmpty(F.src), $"{d.weapon.id}: Herkunft");
                if (F.kind == "none") continue;
                if (F.Explodes) Assert.Greater(F.radius_m, 0, d.weapon.id);
                else Assert.IsNotNull(d.Impact(F.impact), $"{d.weapon.id}: Einschlagstil {F.impact}");
                if (F.Projectile) Assert.Greater(F.speed_mps, 0, d.weapon.id);
                if (F.kind == "pellets") { Assert.Greater(F.pellets, 1); Assert.Greater(F.cone_deg, 0); }
                if (F.kind == "beam" || F.kind == "rail" || F.kind == "bolts") Assert.Greater(F.width_m, 0, d.weapon.id);
            }
            var P = D.motion.payload;
            Assert.AreEqual(5, P.impacts.Length, "Stile bullet, heavy, pellet, energy, arrow");
            Assert.Greater(P.decal.max, 0);
            Assert.Greater(P.explosion.sparks, 0);
            Assert.Greater(P.muzzle_smoke.rate_hz, 0);
        }

        // ---------------------------------------------------------------- Referenz
        [Test]
        public void Gleich_wie_Blender_Referenz()
        {
            foreach (var d in All) Referenz(d);
        }

        static void Referenz(EgoFile D)
        {
            var R = JsonUtility.FromJson<RefFile>(File.ReadAllText($"{Gen}/{D.reference}"));
            Assert.AreEqual(EgoFile.Format + "-reference", R.format);
            var S = new EgoSolver(D);
            var byAction = R.samples.Where(s => !s.label.StartsWith("still:")).GroupBy(s => s.action).ToDictionary(g => g.Key, g => g.ToDictionary(s => s.frame));
            float worstP = 0, worstR = 0, worstA = 0;
            string wp = "", wr = "", wa = "";
            Assert.That(R.tolerance_arm_deg, Is.InRange(0.1f, 0.2f), "Armgrenze aus der Lagetoleranz (atan 2 · 0,5 mm / 0,32 m)");
            int checks = 0;
            void Compare(RefSample s, EgoOutput o)
            {
                int fx = 0;
                foreach (var ob in s.objects)
                {
                    Matrix4x4 got;
                    if (ob.name == "flash")                    // Mündungsfeuer und Hülsen (0.16): nur sichtbare stehen in der Referenz
                    {
                        Assert.IsTrue(o.flashOn, $"{s.label}: Blitz fehlt");
                        got = o.flash;
                        fx++;
                    }
                    else if (ob.name.StartsWith("shell_") && int.TryParse(ob.name.Substring(6), out int sid))   // Hülse; Bauteil shell_round (0.33 P3) nicht
                    {
                        int j = Array.IndexOf(o.shellIds, sid, 0, o.shellCount);
                        Assert.GreaterOrEqual(j, 0, $"{s.label}: {ob.name} fehlt");
                        got = o.shells[j];
                        fx++;
                    }
                    else if (ob.name.StartsWith("link_") && int.TryParse(ob.name.Substring(5), out int lid))   // Gurtglied (0.34)
                    {
                        int j = Array.IndexOf(o.linkIds, lid, 0, o.linkCount);
                        Assert.GreaterOrEqual(j, 0, $"{s.label}: {ob.name} fehlt");
                        got = o.links[j];
                        fx++;
                    }
                    else if (ob.name == "weapon") got = o.weapon;
                    else if (ob.name == "camera") got = RotX(Rad(o.camPitch));
                    else if (ob.name.StartsWith("R_")) got = o.segR[S.SegmentIndex(ob.name.Substring(2))];
                    else if (ob.name.StartsWith("L_")) got = o.segL[S.SegmentIndex(ob.name.Substring(2))];
                    else got = S.World(o, ob.name);
                    var want = M(ob.m);
                    float dp = Vector3.Distance(Pos(got), Pos(want)), dr = RotDiffDeg(got, want);
                    if (dp > worstP) { worstP = dp; wp = $"{s.label} {ob.name}"; }
                    bool arm = ob.name.EndsWith("_upper") || ob.name.EndsWith("_fore");    // Richtung zwischen zwei gelösten Punkten
                    if (arm) { if (dr > worstA) { worstA = dr; wa = $"{s.label} {ob.name}"; } }
                    else if (dr > worstR) { worstR = dr; wr = $"{s.label} {ob.name}"; }
                    checks++;
                }
                Assert.AreEqual(fx, (o.flashOn ? 1 : 0) + o.shellCount + o.linkCount, $"{s.label}: Blitz/Hülsen/Glieder sichtbar in Unity, nicht in Blender");
                Assert.AreEqual(s.ads_hidden, o.adsHidden, $"{s.label}: Zielfernrohr-Teile (ads_hide) wie Blender");
            }
            foreach (var s in R.samples.Where(s => s.label.StartsWith("still:")))
                Compare(s, S.Evaluate(S.StillAction(s.label.Substring(6)), 0, new EgoState()));
            foreach (var A in D.actions)
            {
                Assert.IsTrue(byAction.TryGetValue(A.name, out var frames), $"Referenz für {A.name} fehlt");
                var st = new EgoState();
                for (int f = 0; f <= A.frames; f++)
                {
                    var o = S.Evaluate(A, f, st);
                    if (frames.TryGetValue(f, out var s)) Compare(s, o);
                }
            }
            TestContext.WriteLine($"{D.weapon.id}: {checks} Matrizen, größte Abweichung {worstP * 1000:0.000} mm ({wp}), {worstR:0.000}° ({wr}), Ober-/Unterarm {worstA:0.000}° ({wa})");
            Assert.LessOrEqual(worstP, R.tolerance_m, $"Lage {worstP * 1000:0.000} mm bei {wp}");
            Assert.LessOrEqual(worstR, R.tolerance_deg, $"Drehung {worstR:0.000}° bei {wr}");
            // Drehgrenze aus dem kürzeren Glied (0.33 P4): der Export rechnet sie mit dem Oberarm (320 mm), der Unterarm (300 mm) darf bei
            // denselben 0,5 mm je Punkt 0,191° abweichen (Bogen fire_release_ads: 0,185°)
            float tolA = Mathf.Max(R.tolerance_arm_deg, Mathf.Atan2(2 * R.tolerance_m, Mathf.Min(D.arm.upper_m, D.arm.fore_m)) * Mathf.Rad2Deg);
            Assert.LessOrEqual(worstA, tolA, $"Arm {worstA:0.000}° bei {wa}");
            Assert.Greater(checks, D.slot == 0 ? 5000 : D.gameplay.HasPortals ? 3000 : 4000, "Matrizen (Pilot wie bisher > 5000; Werkzeug: 12 Aktionen, 22 Objekte)");
        }
    }
}
