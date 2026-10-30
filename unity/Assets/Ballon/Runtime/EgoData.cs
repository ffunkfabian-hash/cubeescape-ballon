// Ego-Daten im Format ballon-ego/10 (Salve und Bahnstufe je Klasse, Werkzeug mit Portalen, 0.22), erzeugt von tools/export_unity.py (nicht
// von Hand pflegen); ballon-ego/9 (0.20), /8 (0.18) und /7 (bis 0.17, eine Waffe) liest EgoFile.ParseAll weiter. Alle Vektoren stehen im Blender-Kameraraum (Meter, rechts −X, vorn −Y, oben +Z); Umrechnung
// nach Unity: axes.to_unity.
using System;
using System.Collections.Generic;
using UnityEngine;

namespace Ballon.Ego
{
    [Serializable] public class EgoCamera { public float h_fov_deg; public int[] aspect; public float near_m; }
    [Serializable]
    public class EgoGameplay
    {
        public int rpm; public int magazine; public string src;
        public string weapon_type, sight;               // 5 (0.13): Waffentyp und Visiertyp nach Visier-Standard 3
        public float world_zoom;                        // Weltzoom der Klasse beim Zielen (Bildmaßstab, Entscheidungsliste 1.2 A)
        public EgoZoom[] zoom_table;                    // Weltzoom je Waffentyp (Katalog basic/reticles.py)
        public EgoHip hip;                              // Hüft-Fadenkreuz (4.1 A / 4.2 A)
        public float zoom_start;                        // 9 (0.20): Anteil des Augenwegs, ab dem der Weltzoom beginnt (1d); 0 = 0,05
        public string fire_mode;                        // 9 (0.20): Feuerart aus der Spec (META fire): full_auto, semi_auto; leer (/7, /8) = full_auto
                                                        // 10 (0.22): burst (Salve), single (Werkzeug: ein Schuss je Klick)
        public int burst_shots, burst_rpm;              // 10: Salvenlänge (Spec burst_N) und Takt in der Salve; 0 = keine Salve
        public float path_up_h;                         // 10: Bahnstufe je Schuss (Anteil der Bildhöhe) je Klasse; /9: motion.recoil.path_up_h
        public float recover_delay_s, recover_hz;       // 10: Erholung der Bahn nach der Salve je Klasse; /9: motion.recoil
        public float kick;                              // 10: Modellkick, Kamera-Ruck und Hochziehen je Schuss relativ zu motion.recoil (Werkzeug 0,6); /9: 1
        public bool muzzle_flash;                       // 10: Mündungsfeuer (Werkzeug ohne); /7–/9: true
        public float ring_turn_s;                       // 10: Dauer der Ringdrehung je Schuss (Werkzeug)
        public EgoPortal[] portals;                     // 10: Portale des Werkzeugs (Taste, Rolle, Farbe, Ringrichtung); leer = Waffe
        public float range_m;                           // 10: Reichweite der Portalschüsse (Werkzeug); 0 = Waffe
        public float charge_s, charge_fade_s;           // 10 (0.33 P3): Aufladen bis zum Schuss und Abklingen der Ladung (Ladewaffe); 0 = ohne
        public float flash_scale;                       // 10 (0.33 P4): Maßstab des Mündungsfeuers je Klasse (Werfer); 0 (älterer Export) = 1
        public float FlashScale => flash_scale > 0 ? flash_scale : 1f;

        /// <summary>Einzelfeuer: ein Schuss je Zug des Abzugs (Feuerart semi_auto, Werkzeug single, Repetierer bolt_action; ego.SEMI_MODES).</summary>
        public bool Semi => fire_mode == "semi_auto" || fire_mode == "single" || SingleShot || Cycles;
        /// <summary>Repetierer (0.33, bolt_action): nach jedem Schuss mit Restmunition die Klassenaktion fire_cycle (im Zielen fire_cycle_ads).</summary>
        public bool BoltAction => fire_mode == "bolt_action";
        /// <summary>Vorderschaftrepetierer (0.33 P3, pump_action): wie der Repetierer, die Klassenaktion fire_cycle pumpt.</summary>
        public bool Pump => fire_mode == "pump_action";
        /// <summary>Nach jedem Schuss mit Restmunition die Klassenaktion fire_cycle (Repetierer, Pumpe); die Hülse fliegt beim Marker Eject.</summary>
        public bool Cycles => BoltAction || Pump || cycle;
        /// <summary>Klasse mit Klassenaktion fire_cycle ohne eigene Feuerart (0.33 P4, Granatwerfer: Trommel dreht nach dem Schuss); beim Laden aus
        /// den Aktionen gesetzt, nicht Teil von ego.json.</summary>
        [NonSerialized] public bool cycle;
        /// <summary>Bogen (0.33 P4, draw_release): Abzug halten spannt (Klassenaktion fire_draw), voller Auszug hält, Loslassen löst
        /// (fire_release), vorher entspannt der Bogen (let_down).</summary>
        public bool Draw => fire_mode == "draw_release";
        /// <summary>Einzelschuss mit Magazin 1 (0.33 P4, single_shot, Raketenwerfer): ein Schuss je Zug, danach sofort nachladen.</summary>
        public bool SingleShot => fire_mode == "single_shot";
        /// <summary>Ladewaffe (0.33 P3, charge_burst/charge_single, ego.CHARGE_MODES): Abzug halten lädt in charge_s, bei voller Ladung
        /// schießt sie (Salve oder ein Schuss); Loslassen vorher bricht ab. Leuchtteile weapon.live.glow folgen der Ladung.</summary>
        public bool Charge => fire_mode == "charge_burst" || fire_mode == "charge_single";
        /// <summary>Dauerstrahl (0.33, continuous_beam): Dauerfeuer, Leuchtteile weapon.live.glow an, solange der Abzug zieht.</summary>
        public bool Beam => fire_mode == "continuous_beam";
        /// <summary>Salvenwaffe: burst_shots Schuss je Zug, gehalten Salve um Salve (Feuerart burst; Ladewaffe charge_burst je Ladung).</summary>
        public bool Burst => burst_shots > 0;
        /// <summary>Ohne Magazin (Werkzeug): unbegrenzt, kein Nachladen.</summary>
        public bool Unlimited => magazine <= 0;
        /// <summary>Werkzeug mit Portalen: Linksklick und Rechtsklick lösen je ein Portal aus (kein Zielen).</summary>
        public bool HasPortals => portals != null && portals.Length > 0;

        /// <summary>Weltzoom eines Waffentyps aus der Tabelle (NaN, wenn unbekannt).</summary>
        public float ZoomFor(string type)
        {
            if (zoom_table != null) foreach (var z in zoom_table) if (z.type == type) return z.zoom;
            return float.NaN;
        }
    }

    [Serializable] public class EgoZoom { public string type; public float zoom; }

    /// <summary>Portal des Werkzeugs (10, 0.22, ego.CLASSES['portal_cannon']): Eingabe fire (Linksklick) oder aim (Rechtsklick), Leuchtrolle,
    /// Farbe (#RRGGBB) und Richtung der Ringdrehung (+1 im Uhrzeigersinn von hinten).</summary>
    [Serializable] public class EgoPortal { public string name, input, role, color; public int ring; }

    /// <summary>Grundelement aus basic/reticles.py in mm auf der Scheibe (x links, u oben): line a→b mit Spreizrichtung d,
    /// ring r/ri mit grow, dot r.</summary>
    [Serializable] public class EgoPrim { public string t; public float[] a, b, d; public float r, ri, grow; }

    [Serializable] public class EgoSpread { public string id; public float @base, per_shot, max, recover_s, move; }

    [Serializable] public class EgoHipForm { public string kind; public float share_h, extent_mm; public EgoPrim[] prims; }

    [Serializable]
    public class EgoHip
    {
        public string kind, status, color, src;
        public float share_h, extent_mm, weight, line_r_mm, opacity, min_line_px;
        public EgoPrim[] prims;
        public EgoSpread spread;
        public EgoHipForm sprint;                       // kind leer: im Sprint aus
    }

    [Serializable]
    public class EgoMove { public string kind; public float[] vec; public float[] axis; public float a0, a1; }

    [Serializable]
    public class EgoPart { public string id, asm, role, parent; public float[] rest; public EgoMove move;
                           public bool ads_hide; }       // 9 (0.20): im Zielen aus (Zielfernrohr, motion.ads_hide)

    [Serializable] public class EgoAnchor { public string id, part; public float[] pos; }

    /// <summary>Hülsenauswurf der Waffe (7, 0.16, Entscheidungsliste 5.4 A; Modul-Feld EJECT): Startlage im Auswurffenster, Richtung (Einheit,
    /// Blender-Waffenrahmen) und Hülsennetz (flach: Punkte in m, Dreiecke). enabled false: Waffe ohne Hülsen.</summary>
    [Serializable]
    public class WeaponEject { public bool enabled; public string @case, src; public float[] pos, dir, verts; public int[] tris;
                               public string on; }    // 0.33 P4: 'reload' = Hülse nur beim Marker Eject (Trommel), sonst je Schuss

    /// <summary>Live-Teile im laufenden Feuer (8, 0.18; ego.LIVE bzw. Modul-Feld EGO_LIVE): Abzug, Verschluss, Auswurfklappe.</summary>
    [Serializable] public class WeaponLive { public string trigger, bolt, port, ring; public string[] glow; }    // 10: ring (Werkzeug); leer = Teil fehlt; glow (0.33): Leuchtteile beim Feuern

    [Serializable]
    // type_de (0.33 Ziel 2): Klasse auf Deutsch für HUD und Menü
    public class EgoWeapon { public string id, root, name, type_de, fbx; public EgoPart[] parts; public EgoAnchor[] anchors; public WeaponEject eject;
                             public WeaponLive live; }

    /// <summary>Ego-Profil der Klasse (8, 0.18, ego.CLASSES): Waffentyp, Haltungen und gestreckte Aktionen der Klasse, Herkunft.</summary>
    [Serializable] public class ProfileFrames { public string action; public float frames; }
    [Serializable] public class EgoProfile { public string type, src, frames_src; public string[] poses; public ProfileFrames[] frames; }

    [Serializable] public class EgoPiece { public string id, segment, role; }

    [Serializable]
    public class EgoArm
    {
        public int rig_version;
        public float upper_m, fore_m;
        public float[] shoulder_R, shoulder_L, elbow_pole;
        public float wrist_limit_deg, wrist_target_deg;
        public float[] forearm_pref, palm_center;
        public float knuckle_z;
        public float[] finger_x, finger_scale, finger_links, thumb_base, thumb_dir, thumb_links;
        public string[] segments;
        public string fbx, src;
        public EgoPiece[] pieces;
    }

    [Serializable]
    public class EgoPose
    {
        public string name, src;
        public bool ads;
        public float roll;
        public float[] pos, aim, eye, aim_dir;
    }

    [Serializable]
    public class EgoGrip { public string name, part, fingers_pose, src; public float[] contact, palm, fingers; }

    [Serializable] public class EgoFingerPose { public string name; public float[] f, t; }

    [Serializable] public class WeaponKey { public float f; public string pose; public float roll, yaw, pitch, up, right, back; }
    [Serializable] public class HandKey { public float f; public string kind, grip; public float[] point, offset; }
    [Serializable] public class FingerKey { public float f; public string pose; }
    [Serializable] public class ValueKey { public float f; public float v; }
    [Serializable] public class MechTrack { public string part; public ValueKey[] keys; }
    [Serializable] public class FrameRange { public float a, b; }
    [Serializable] public class Bob { public bool enabled, u; public float start, end, period; public float[] amp; public float roll; }   // u: U-Bogen (−cos 2φ) statt liegender Acht (sin 2φ)
    [Serializable] public class Marker { public int f; public string name; }

    [Serializable]
    public class EgoAction
    {
        public string name, de, src;
        public int frames;
        public float time_scale;
        public WeaponKey[] weapon;
        public HandKey[] L, R;
        public FingerKey[] fL, fR;
        public MechTrack[] mech;
        public FrameRange[] carry;
        public FrameRange drop;
        public int[] fire;
        public float kick;

        /// <summary>Endet in der Haltung „ads“ (ego.ends_in_ads): Feder-Nachlauf dann mit aim_zeta.</summary>
        public bool EndsInAds => weapon != null && weapon.Length > 0 && weapon[weapon.Length - 1].pose == "ads";
        public bool breathe;
        public Bob bob;
        public Marker[] events;
    }

    [Serializable]
    public class EgoRole
    {
        public string role, color, aaa_color, de;
        public float rough, metal, alpha, emit, spec;
        public bool emit_only;
        public bool no_coat;          // 9 (0.20): Linse im Zielfernrohr (kit: ohne Klarlack, Alpha 0,04, kaum Glanz)
    }

    [Serializable] public class Spring { public float freq_hz, zeta, aim_freq_hz, aim_zeta; }     // aim_*: Aktionen, die im Zielen enden (ego.ends_in_ads)
    [Serializable] public class BreatheAll { public float period_s, up_m, pitch_deg; }

    /// <summary>Rückstoß (ego.RECOIL, 6 ab 0.15): Modellkick (Feder, im Zielen ads_back/ads_pitch), Kamera-Ruck (Hüfte samt Viewmodel,
    /// Zielen nur Welt: ads_cam), Grundbahn (path_up_h je Schuss, feste Seitenfolge path_side_b, Anteile des Weltbilds), Erholung nach der
    /// Salve (recover_delay_s, recover_hz), Salvenwaffen (burst_shots, burst_rpm; 0 = Dauerfeuer) und Streuung (Grad).</summary>
    [Serializable]
    public class Recoil
    {
        public float freq_hz, zeta, back_mps, pitch_dps, climb_deg, ads_back, ads_pitch;
        public float cam_freq_hz, cam_zeta, cam_dps, ads_cam;
        public float path_up_h, path_hz;
        public float[] path_side_b;
        public float recover_delay_s, recover_hz;
        public int burst_shots, burst_rpm;              // bis /9 (immer 0); seit /10 je Klasse in gameplay
        public float spread_hip_deg, spread_ads_deg;
    }

    /// <summary>Waffenwechsel (ego.SWITCH, 6.1 A): Pause ohne Waffe zwischen Wegstecken und Ziehen.</summary>
    [Serializable] public class Switch { public float empty_s; public string src; }

    /// <summary>Mündungsfeuer (ego.FLASH, 7 ab 0.16, Entscheidungsliste 5.3 A): sichtbar dur_s ab dem Schuss (1 Bild bei 30/s), Netz relativ
    /// zu Socket_Muzzle (Blender-Waffenrahmen, m; flach), Kern- und Flammendreiecke, Drehung je Schuss um die Laufachse (roll_deg).</summary>
    [Serializable]
    public class Flash { public float dur_s; public float[] verts, roll_deg; public int[] core_tris, flame_tris; public string core_role, flame_role, src; }

    /// <summary>Hülsenbahn (ego.EJECT, 7 ab 0.16, 5.4 A): Geschwindigkeit, Schwerkraft im Kameraraum, Drehung um spin_axis der Waffe, sichtbar
    /// ab delay_frames (30/s) für life_s, höchstens max_live gleichzeitig.</summary>
    [Serializable]
    public class Eject { public float speed_mps, gravity_mps2, spin_dps, life_s; public float[] spin_axis; public int max_live, delay_frames;
                         public string role, src; }

    /// <summary>Zielfernrohr (ego.ADS_HIDE, 9 ab 0.20): Teile mit ads_hide sind aus, solange Socket_Eye der Grundhaltung näher als eye_m an
    /// der Kamera liegt. /8 und /7: 0 (nie aus; keine Waffe hatte solche Teile).</summary>
    [Serializable] public class AdsHide { public float eye_m; public string src; }

    /// <summary>Bewegungsgefühl v2 (basic/arms/ego.py: INTERP, SECONDARY, BREATHE_ALL, RECOIL, SWITCH, FLASH, EJECT, ADS_HIDE, TIME_SCALE).</summary>
    [Serializable]
    public class Motion { public string interp, de; public float time_scale; public string[] keep_time; public Spring secondary;
                          public BreatheAll breathe_all; public Recoil recoil; public Switch @switch; public Flash flash; public Eject eject;
                          public AdsHide ads_hide; }

    [Serializable] public class Atlas { public int size; public string[] objects; public string albedo, spec, normal, ao; }
    [Serializable] public class Lut { public string file, view, look, de; public int size; public float[] ev; public float mid_grey; }

    /// <summary>Gebackene Atlanten (tools/bake_unity.py) und die AgX-LUT der Blender-Ansicht.</summary>
    [Serializable] public class Skin { public string name, de, kind, albedo, spec; }
    [Serializable] public class EgoTextures { public string de; public Atlas weapon, arms; public Lut lut; public Skin[] skins; }
    /// <summary>Ablage eines Kanals (9, 0.20, export_unity.TEXTURE_STORE): Kantenlänge und Dateiformat.</summary>
    [Serializable] public class TexStore { public string kind, ext, de; public int size; }
    [Serializable] public class WeaponTextures { public Atlas weapon; public Skin[] skins; public TexStore[] store; public float limit_mb; }

    [Serializable] public class MeshBound { public string name; public float[] min, max; public int tris; }
    [Serializable] public class MeshBounds { public string de; public MeshBound[] objects; }

    [Serializable]
    public class EgoFile
    {
        public string format, generated_by;
        public int fps;
        public Motion motion;
        public EgoCamera camera;
        public EgoGameplay gameplay;
        public EgoWeapon weapon;
        public EgoArm arm;
        public EgoPose[] poses;
        public EgoGrip[] grips;
        public EgoFingerPose[] finger_poses;
        public EgoAction[] actions;
        public EgoRole[] roles;
        public MeshBounds mesh_bounds;
        public EgoTextures textures;
        [NonSerialized] public Matrix4x4 toUnity;   // aus axes.to_unity (JsonUtility kann keine verschachtelten Felder)
        // je Waffe (8): Klassenprofil, Schlüssel des Waffenatlas (Material „Atlas_<atlas>“) und Name der Blender-Referenz; /7 setzt die Werte der Pilotwaffe
        [NonSerialized] public EgoProfile profile;
        [NonSerialized] public string atlas = "weapon", reference = "ego_reference.json";
        [NonSerialized] public int slot;            // Platz in weapons[] (Taste slot + 1)
        [NonSerialized] public WeaponTextures weaponTextures;   // je Waffe mit Ablage (store, limit_mb; 9); /7: null

        public const string Format = "ballon-ego/10";    // 10: gameplay.burst_shots/burst_rpm/path_up_h/muzzle_flash/portals/ring_turn_s, weapon.live.ring, Klassen ohne Zielen/Nachladen (0.22)
        public const string Format9 = "ballon-ego/9";    // 9: gameplay.fire_mode, parts[].ads_hide, motion.ads_hide, textures.store/limit_mb (0.20)
        public const string Format8 = "ballon-ego/8";    // 8: weapons[] je Waffe (gameplay, weapon mit live, poses, grips, actions, profile, Atlanten, Netzgrenzen, Referenz), gemeinsam Bewegung, Kamera, Arme, Rollen (0.18)
        public const string FormatLegacy = "ballon-ego/7";   // 7: motion.flash, motion.eject, weapon.eject, Rollen flash_* (0.16); 6: motion.recoil (Bahn, Kamera, Modellkick, Erholung, Salven, Streuung) und motion.switch (0.15); 5: gameplay.weapon_type/world_zoom/zoom_table/hip (0.13); 4: secondary.aim_freq_hz/aim_zeta (0.10); 3: spec statt mask, skins (0.7.1/0.7.2); 2: Atlanten, AgX-LUT (0.7); ältere neu exportieren

        Dictionary<string, EgoPose> _poses;
        Dictionary<string, EgoGrip> _grips;
        Dictionary<string, EgoFingerPose> _fingers;
        Dictionary<string, EgoAction> _actions;
        Dictionary<string, EgoPart> _parts;
        Dictionary<string, EgoAnchor> _anchors;

        [Serializable] class FormatOnly { public string format; }

        /// <summary>Erste Waffe (Taste 1); bei /7 die einzige.</summary>
        public static EgoFile Parse(string json) => ParseAll(json)[0];

        /// <summary>Alle Waffen der Datei, je Waffe ein EgoFile mit dem gemeinsamen Teil (Bewegung, Kamera, Arme, Rollen, Armatlas, LUT) und
        /// den Waffenfeldern. Liest ballon-ego/8 und das alte ballon-ego/7 (eine Waffe, Live-Teile und Atlas der Pilotwaffe); andere Formate
        /// werden abgelehnt.</summary>
        public static EgoFile[] ParseAll(string json)
        {
            var fmt = JsonUtility.FromJson<FormatOnly>(json)?.format;
            if (fmt == FormatLegacy)
            {
                var f = JsonUtility.FromJson<EgoFile>(json);
                if (f.weapon.live == null || string.IsNullOrEmpty(f.weapon.live.trigger))
                    f.weapon.live = new WeaponLive { trigger = "trigger", bolt = "bolt_carrier", port = "port_cover" };   // bis 0.17 fest im Code
                f.profile = new EgoProfile { type = f.gameplay.weapon_type, src = FormatLegacy, poses = new string[0], frames = new ProfileFrames[0] };
                Migrate9(f);
                Migrate10(f);
                f.toUnity = ParseAxes(json);
                f.Index();
                return new[] { f };
            }
            if (fmt != Format && fmt != Format9 && fmt != Format8)
                throw new FormatException($"ego.json: Format {fmt ?? "leer"} statt {Format} (oder {Format9}, {Format8}, {FormatLegacy}) – neu exportieren (tools/export_unity.py)");
            var s = JsonUtility.FromJson<EgoFile8>(json);
            if (s.weapons == null || s.weapons.Length == 0) throw new FormatException("ego.json: weapons leer");
            var axes = ParseAxes(json);
            var res = new EgoFile[s.weapons.Length];
            for (int k = 0; k < res.Length; k++)
            {
                var e = s.weapons[k];
                var bounds = new List<MeshBound>(s.mesh_bounds?.objects ?? new MeshBound[0]);
                if (e.mesh_bounds?.objects != null) bounds.AddRange(e.mesh_bounds.objects);
                var f = new EgoFile
                {
                    format = s.format, generated_by = s.generated_by, fps = s.fps, motion = s.motion, camera = s.camera, gameplay = e.gameplay,
                    weapon = e.weapon, arm = s.arm, poses = e.poses, grips = e.grips, finger_poses = s.finger_poses, actions = e.actions,
                    roles = s.roles, mesh_bounds = new MeshBounds { de = e.mesh_bounds?.de ?? s.mesh_bounds?.de, objects = bounds.ToArray() },
                    textures = s.textures == null ? null : new EgoTextures { de = s.textures.de, arms = s.textures.arms, lut = s.textures.lut,
                                                                            weapon = e.textures?.weapon, skins = e.textures?.skins },
                    weaponTextures = e.textures,
                    toUnity = axes, profile = e.profile, atlas = e.atlas, reference = e.reference, slot = k,
                };
                if (f.weapon == null || f.weapon.live == null || (string.IsNullOrEmpty(f.weapon.live.trigger) && !f.gameplay.Draw))
                    throw new FormatException($"ego.json: weapons[{k}] ({e.id}) ohne weapon.live");      // Bogen (0.33 P4): ohne Abzug
                if (fmt != Format8 && (string.IsNullOrEmpty(f.gameplay.fire_mode) || f.motion.ads_hide == null || f.motion.ads_hide.eye_m <= 0))
                    throw new FormatException($"ego.json: weapons[{k}] ({e.id}) ohne gameplay.fire_mode oder motion.ads_hide ({fmt})");
                if (fmt == Format && ((f.gameplay.kick <= 0 && !f.gameplay.Beam) || f.gameplay.recover_hz <= 0))   // Dauerstrahl (0.33): Kick 0
                    throw new FormatException($"ego.json: weapons[{k}] ({e.id}) ohne gameplay.kick oder recover_hz ({Format})");
                if (fmt == Format && f.gameplay.Charge != (f.gameplay.charge_s > 0))
                    throw new FormatException($"ego.json: weapons[{k}] ({e.id}) Feuerart {f.gameplay.fire_mode} passt nicht zu charge_s {f.gameplay.charge_s}");
                if (fmt == Format && f.gameplay.Burst != (f.gameplay.fire_mode == "burst" || f.gameplay.fire_mode == "charge_burst"))
                    throw new FormatException($"ego.json: weapons[{k}] ({e.id}) Feuerart {f.gameplay.fire_mode} passt nicht zu burst_shots {f.gameplay.burst_shots}");
                if (fmt == Format8) Migrate9(f);
                if (fmt != Format) Migrate10(f);
                f.Index();
                res[k] = f;
            }
            return res;
        }

        /// <summary>/7 und /8 nach /9 (0.20): bis dahin schossen alle Waffen Dauerfeuer, keine hatte Teile mit ads_hide.</summary>
        static void Migrate9(EgoFile f)
        {
            if (string.IsNullOrEmpty(f.gameplay.fire_mode)) f.gameplay.fire_mode = "full_auto";
            if (f.motion.ads_hide == null || f.motion.ads_hide.eye_m <= 0)
                f.motion.ads_hide = new AdsHide { eye_m = 0, src = "vor ballon-ego/9: keine Teile im Zielen aus" };
        }

        /// <summary>/7–/9 nach /10 (0.22): Salve und Bahnstufe standen gemeinsam in motion.recoil, alle Waffen hatten Mündungsfeuer, Verschluss
        /// und Auswurfklappe, keine Portale.</summary>
        static void Migrate10(EgoFile f)
        {
            var g = f.gameplay;
            g.burst_shots = f.motion.recoil.burst_shots;
            g.burst_rpm = f.motion.recoil.burst_rpm;
            g.path_up_h = f.motion.recoil.path_up_h;
            g.recover_delay_s = f.motion.recoil.recover_delay_s;
            g.recover_hz = f.motion.recoil.recover_hz;
            g.kick = 1;
            g.muzzle_flash = true;
            g.ring_turn_s = 0;
            g.portals = new EgoPortal[0];
            if (f.weapon.live.ring == null) f.weapon.live.ring = "";
        }

        [Serializable]
        class EgoWeaponEntry
        {
            public string id, atlas, reference;
            public EgoProfile profile;
            public EgoGameplay gameplay;
            public EgoWeapon weapon;
            public EgoPose[] poses;
            public EgoGrip[] grips;
            public EgoAction[] actions;
            public WeaponTextures textures;
            public MeshBounds mesh_bounds;
        }

        [Serializable]
        class EgoFile8
        {
            public string format, generated_by;
            public int fps;
            public Motion motion;
            public EgoCamera camera;
            public EgoArm arm;
            public EgoFingerPose[] finger_poses;
            public EgoRole[] roles;
            public EgoTextures textures;              // gemeinsam: arms, lut
            public MeshBounds mesh_bounds;            // gemeinsam: Armteile
            public EgoWeaponEntry[] weapons;
        }

        // axes.to_unity ist eine 3×3-Liste; JsonUtility liest keine verschachtelten Listen, darum hier von Hand.
        static Matrix4x4 ParseAxes(string json)
        {
            int i = json.IndexOf("\"to_unity\"", StringComparison.Ordinal);
            if (i < 0) throw new FormatException("ego.json: axes.to_unity fehlt");
            int a = json.IndexOf('[', i), depth = 0, b = a;
            for (; b < json.Length; b++)
            {
                if (json[b] == '[') depth++;
                else if (json[b] == ']' && --depth == 0) break;
            }
            var nums = json.Substring(a, b - a + 1).Replace("[", " ").Replace("]", " ").Split(new[] { ',', ' ', '\n', '\r', '\t' },
                StringSplitOptions.RemoveEmptyEntries);
            if (nums.Length != 9) throw new FormatException($"ego.json: axes.to_unity hat {nums.Length} statt 9 Werte");
            var m = Matrix4x4.identity;
            for (int k = 0; k < 9; k++)
                m[k / 3, k % 3] = float.Parse(nums[k], System.Globalization.CultureInfo.InvariantCulture);
            return m;
        }

        void Index()
        {
            _poses = new Dictionary<string, EgoPose>();
            foreach (var p in poses) _poses[p.name] = p;
            _grips = new Dictionary<string, EgoGrip>();
            foreach (var g in grips) _grips[g.name] = g;
            _fingers = new Dictionary<string, EgoFingerPose>();
            foreach (var p in finger_poses) _fingers[p.name] = p;
            _actions = new Dictionary<string, EgoAction>();
            foreach (var a in actions) _actions[a.name] = a;
            _parts = new Dictionary<string, EgoPart>();
            foreach (var p in weapon.parts) _parts[p.id] = p;
            _anchors = new Dictionary<string, EgoAnchor>();
            foreach (var a in weapon.anchors) _anchors[a.id] = a;
            gameplay.cycle = _actions.ContainsKey("fire_cycle");
            if (gameplay.flash_scale <= 0) gameplay.flash_scale = 1;      // vor 0.33 P4: Blitz in Familiengröße
            if (weapon.eject != null && weapon.eject.enabled && string.IsNullOrEmpty(weapon.eject.on)) weapon.eject.on = "shot";   // vor 0.33 P4: je Schuss    // 0.33 P4: Trommel dreht nach dem Schuss wie Repetierer und Pumpe
        }

        public EgoPose Pose(string n) => _poses.TryGetValue(n, out var p) ? p : throw new KeyError("Haltung", n);
        public EgoGrip Grip(string n) => _grips.TryGetValue(n, out var p) ? p : throw new KeyError("Griff", n);
        public EgoFingerPose Fingers(string n) => _fingers.TryGetValue(n, out var p) ? p : throw new KeyError("Fingerstellung", n);
        public EgoAction Action(string n) => _actions.TryGetValue(n, out var p) ? p : throw new KeyError("Aktion", n);
        public bool HasAction(string n) => _actions.ContainsKey(n);
        public EgoPart Part(string n) => _parts.TryGetValue(n, out var p) ? p : throw new KeyError("Bauteil", n);
        public bool HasPart(string n) => _parts.ContainsKey(n);
        public EgoAnchor Anchor(string n) => _anchors.TryGetValue(n, out var p) ? p : throw new KeyError("Anker", n);
        public bool HasAnchor(string n) => _anchors.ContainsKey(n);
        public bool HasPose(string n) => _poses.ContainsKey(n);
        /// <summary>Waffe mit Zielen (Visier, Aktion aim_in); das Werkzeug ohne Visier hat keine (0.22).</summary>
        public bool CanAim => _actions.ContainsKey("aim_in");
        /// <summary>Bauteil, das das Nachladen trägt oder fallen lässt (carry/drop): das Teil des Griffs 'mag' (Magazin, Energiezelle; 0.33),
        /// ohne Griff 'magazine' – wie ego.profile › mag.</summary>
        public string MagPart => _grips.TryGetValue("mag", out var g) && !string.IsNullOrEmpty(g.part) ? g.part : "magazine";
        /// <summary>Nachladen je Patrone (0.33 P3, Schrotflinte): reload_tactical/reload_empty laden die erste, reload_shell je eine weitere
        /// (Marker ShellIn), reload_end bzw. reload_end_pump (nach leerem Beginn) führen zurück.</summary>
        public bool ShellReload => _actions.ContainsKey("reload_shell");
        /// <summary>Waffe mit Nachladen (Magazin); das Werkzeug hat keins (0.22).</summary>
        public bool CanReload => _actions.ContainsKey("reload_tactical") && !gameplay.Unlimited;
        public EgoRole Role(string n) => Array.Find(roles, r => r.role == n) ?? throw new KeyError("Materialrolle", n);

        public class KeyError : KeyNotFoundException
        {
            public KeyError(string what, string name) : base($"ego.json: {what} '{name}' fehlt") { }
        }
    }
}
