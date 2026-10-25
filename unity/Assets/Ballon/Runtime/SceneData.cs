// Szenendaten im Format ballon-scene/1, erzeugt von tools/scene_build.py (Vertrag: docs/szenen-format.md, nicht von Hand pflegen).
// Blender-Welt in Metern, Z oben, Spieler blickt beim Start nach −Y. Umrechnung nach Unity: (−x, z, −y), wie ego.json › axes.to_unity.
using System;
using UnityEngine;

namespace Ballon.Ego
{
    [Serializable] public class SceneAtlasInfo { public string file; public int size; public float scale; public string de; }
    [Serializable] public class SceneCollider { public string name; public float[] center, size; }
    [Serializable] public class SceneSpawn { public float[] pos; public float yaw_deg; }
    [Serializable] public class SceneSky { public string color; public float strength; }
    [Serializable]
    public class SceneLight
    {
        public string name, kind, color;      // kind: area | sun | point | spot
        public float[] pos, dir;              // dir = Leuchtrichtung
        public float power_w, size_m;
        public float angle_deg;          // Öffnungswinkel für spot (Blender spot_size), fehlt: 90
    }
    [Serializable] public class SceneTarget { public float[] pos; public float distance; }

    [Serializable]
    public class SceneFile
    {
        public string format, name, de, fbx;
        public SceneAtlasInfo light_atlas;
        public string[] objects;
        public SceneCollider[] colliders;
        public SceneSpawn spawn;
        public SceneSky sky, ambient;
        public SceneLight[] lights;
        public SceneTarget[] targets;

        public const string Format = "ballon-scene/1";

        public static SceneFile Parse(string json)
        {
            var f = string.IsNullOrEmpty(json) ? null : JsonUtility.FromJson<SceneFile>(json);
            if (f == null || f.format != Format)
                throw new FormatException($"Szene: Format {(f == null ? "leer" : f.format)} statt {Format} – neu erzeugen (tools/scene_build.py)");
            string n = string.IsNullOrEmpty(f.name) ? "?" : f.name;
            void Need(bool ok, string what) { if (!ok) throw new FormatException($"Szene {n}: {what}"); }
            Need(!string.IsNullOrEmpty(f.name), "name fehlt");
            Need(!string.IsNullOrEmpty(f.fbx), "fbx fehlt");
            Need(f.light_atlas != null && !string.IsNullOrEmpty(f.light_atlas.file), "light_atlas.file fehlt");
            Need(f.spawn != null && f.spawn.pos != null && f.spawn.pos.Length == 3, "spawn.pos braucht 3 Werte");
            Need(f.sky != null && SceneConvert.TryColor(f.sky.color, out _), "sky.color fehlt oder ist keine Farbe (#RRGGBB)");
            Need(f.ambient != null && SceneConvert.TryColor(f.ambient.color, out _), "ambient.color fehlt oder ist keine Farbe (#RRGGBB)");
            f.colliders = f.colliders ?? new SceneCollider[0];
            f.lights = f.lights ?? new SceneLight[0];
            f.targets = f.targets ?? new SceneTarget[0];
            f.objects = f.objects ?? new string[0];
            foreach (var c in f.colliders)
                Need(c.center != null && c.center.Length == 3 && c.size != null && c.size.Length == 3, $"Collider {c.name}: center und size brauchen je 3 Werte");
            foreach (var l in f.lights)
            {
                Need(l.pos != null && l.pos.Length == 3, $"Licht {l.name}: pos braucht 3 Werte");
                Need(l.kind == "area" || l.kind == "sun" || l.kind == "point" || l.kind == "spot", $"Licht {l.name}: kind '{l.kind}' unbekannt");
                Need(l.kind == "point" || (l.dir != null && l.dir.Length == 3 && new Vector3(l.dir[0], l.dir[1], l.dir[2]).sqrMagnitude > 1e-8f),
                     $"Licht {l.name}: dir braucht 3 Werte");
                Need(SceneConvert.TryColor(l.color, out _), $"Licht {l.name}: color ist keine Farbe (#RRGGBB)");
                Need(l.power_w >= 0f, $"Licht {l.name}: power_w negativ");
                Need(l.kind != "area" || l.size_m > 0f, $"Licht {l.name}: size_m fehlt (Flächenlicht)");
            }
            foreach (var t in f.targets)
                Need(t.pos != null && t.pos.Length == 3, "Ziel: pos braucht 3 Werte");
            return f;
        }
    }

    /// <summary>Umrechnung Blender → Unity und Lichtmaßstab für Szenen (reine Funktionen, im EditMode getestet).</summary>
    public static class SceneConvert
    {
        /// <summary>Punkt oder Richtung: Unity = (−x, z, −y), dieselbe Matrix wie ego.json › axes.to_unity.</summary>
        public static Vector3 Point(float[] b) => new Vector3(-b[0], b[2], -b[1]);
        public static Vector3 Point(Vector3 b) => new Vector3(-b.x, b.z, -b.y);

        /// <summary>Kantenlängen einer achsparallelen Box: Blender (x, y, z) → Unity (x, z, y), ohne Vorzeichen.</summary>
        public static Vector3 Size(float[] b) => new Vector3(Mathf.Abs(b[0]), Mathf.Abs(b[2]), Mathf.Abs(b[1]));

        /// <summary>Blick-Gierwinkel: 0 = nach −Y (Blender) = +Z (Unity). Blender dreht gegen den Uhrzeigersinn positiv (nach links),
        /// Unity im Uhrzeigersinn (nach rechts): Vorzeichen umkehren.</summary>
        public static float Yaw(float blenderYawDeg) => -blenderYawDeg;

        /// <summary>#RRGGBB als lineare Farbe (Cycles rechnet linear).</summary>
        public static Color Linear(string hex)
        {
            TryColor(hex, out var c);
            return c.linear;
        }

        public static bool TryColor(string hex, out Color c)
        {
            c = Color.black;
            return !string.IsNullOrEmpty(hex) && hex[0] == '#' && ColorUtility.TryParseHtmlString(hex, out c);
        }

        /// <summary>Lineare Farbe mal Stärke als Gamma-Wert für Material-, Licht- und Hintergrundfarben (Unity linearisiert sie wieder).</summary>
        public static Color Gamma(Color linear, float scale = 1f) => new Color(linear.r * scale, linear.g * scale, linear.b * scale, 1f).gamma;

        /// <summary>Unity-Intensität aus der Blender-Leistung P: Flächenlicht P/π² (Lambert-Fläche, wie Bootstrap.StudioLike), Punkt-
        /// und Spotlicht P/(4π²) (Strahlstärke P/4π, durch π für URP ohne 1/π im Diffusanteil), Sonne S/π (Bestrahlungsstärke S).</summary>
        public static float Intensity(string kind, float powerW)
        {
            switch (kind)
            {
                case "sun": return powerW / Mathf.PI;
                case "area": return powerW / (Mathf.PI * Mathf.PI);
                default: return powerW / (4f * Mathf.PI * Mathf.PI);
            }
        }

        /// <summary>Strahldichte einer Lichtfläche (Kantenlänge size_m) für die Reflexionssonde: P / (π · A).</summary>
        public static float Radiance(float powerW, float sizeM) => powerW / (Mathf.PI * sizeM * sizeM);
    }
}
