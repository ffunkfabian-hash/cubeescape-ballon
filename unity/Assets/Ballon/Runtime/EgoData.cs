// Ego-Daten im Format ballon-ego/7, erzeugt von tools/export_unity.py (nicht von Hand pflegen).
// Alle Vektoren stehen im Blender-Kameraraum (Meter, rechts −X, vorn −Y, oben +Z); Umrechnung nach Unity: axes.to_unity.
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

        /// <summary>Weltzoom eines Waffentyps aus der Tabelle (NaN, wenn unbekannt).</summary>
        public float ZoomFor(string type)
        {
            if (zoom_table != null) foreach (var z in zoom_table) if (z.type == type) return z.zoom;
            return float.NaN;
        }
    }

    [Serializable] public class EgoZoom { public string type; public float zoom; }

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
    public class EgoPart { public string id, asm, role, parent; public float[] rest; public EgoMove move; }

    [Serializable] public class EgoAnchor { public string id, part; public float[] pos; }

    /// <summary>Hülsenauswurf der Waffe (7, 0.16, Entscheidungsliste 5.4 A; Modul-Feld EJECT): Startlage im Auswurffenster, Richtung (Einheit,
    /// Blender-Waffenrahmen) und Hülsennetz (flach: Punkte in m, Dreiecke). enabled false: Waffe ohne Hülsen.</summary>
    [Serializable]
    public class WeaponEject { public bool enabled; public string @case, src; public float[] pos, dir, verts; public int[] tris; }

    [Serializable]
    public class EgoWeapon { public string id, root, name, fbx; public EgoPart[] parts; public EgoAnchor[] anchors; public WeaponEject eject; }

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
        public int burst_shots, burst_rpm;
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

    /// <summary>Bewegungsgefühl v2 (basic/arms/ego.py: INTERP, SECONDARY, BREATHE_ALL, RECOIL, SWITCH, FLASH, EJECT, TIME_SCALE).</summary>
    [Serializable]
    public class Motion { public string interp, de; public float time_scale; public string[] keep_time; public Spring secondary;
                          public BreatheAll breathe_all; public Recoil recoil; public Switch @switch; public Flash flash; public Eject eject; }

    [Serializable] public class Atlas { public int size; public string[] objects; public string albedo, spec, normal, ao; }
    [Serializable] public class Lut { public string file, view, look, de; public int size; public float[] ev; public float mid_grey; }

    /// <summary>Gebackene Atlanten (tools/bake_unity.py) und die AgX-LUT der Blender-Ansicht.</summary>
    [Serializable] public class Skin { public string name, de, kind, albedo, spec; }
    [Serializable] public class EgoTextures { public string de; public Atlas weapon, arms; public Lut lut; public Skin[] skins; }

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

        public const string Format = "ballon-ego/7";     // 7: motion.flash, motion.eject, weapon.eject, Rollen flash_* (0.16); 6: motion.recoil (Bahn, Kamera, Modellkick, Erholung, Salven, Streuung) und motion.switch (0.15); 5: gameplay.weapon_type/world_zoom/zoom_table/hip (0.13); 4: secondary.aim_freq_hz/aim_zeta (0.10); 3: spec statt mask, skins (0.7.1/0.7.2); 2: Atlanten, AgX-LUT (0.7); ältere neu exportieren

        Dictionary<string, EgoPose> _poses;
        Dictionary<string, EgoGrip> _grips;
        Dictionary<string, EgoFingerPose> _fingers;
        Dictionary<string, EgoAction> _actions;
        Dictionary<string, EgoPart> _parts;
        Dictionary<string, EgoAnchor> _anchors;

        public static EgoFile Parse(string json)
        {
            var f = JsonUtility.FromJson<EgoFile>(json);
            if (f == null || f.format != Format)
                throw new FormatException($"ego.json: Format {(f == null ? "leer" : f.format)} statt {Format} – neu exportieren (tools/export_unity.py)");
            f.toUnity = ParseAxes(json);
            f.Index();
            return f;
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
        }

        public EgoPose Pose(string n) => _poses.TryGetValue(n, out var p) ? p : throw new KeyError("Haltung", n);
        public EgoGrip Grip(string n) => _grips.TryGetValue(n, out var p) ? p : throw new KeyError("Griff", n);
        public EgoFingerPose Fingers(string n) => _fingers.TryGetValue(n, out var p) ? p : throw new KeyError("Fingerstellung", n);
        public EgoAction Action(string n) => _actions.TryGetValue(n, out var p) ? p : throw new KeyError("Aktion", n);
        public bool HasAction(string n) => _actions.ContainsKey(n);
        public EgoPart Part(string n) => _parts.TryGetValue(n, out var p) ? p : throw new KeyError("Bauteil", n);
        public bool HasPart(string n) => _parts.ContainsKey(n);
        public EgoAnchor Anchor(string n) => _anchors.TryGetValue(n, out var p) ? p : throw new KeyError("Anker", n);
        public EgoRole Role(string n) => Array.Find(roles, r => r.role == n) ?? throw new KeyError("Materialrolle", n);

        public class KeyError : KeyNotFoundException
        {
            public KeyError(string what, string name) : base($"ego.json: {what} '{name}' fehlt") { }
        }
    }
}
