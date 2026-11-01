// Szenendaten im Format ballon-scene/2, erzeugt von tools/scene_build.py (Vertrag: docs/szenen-format.md, nicht von Hand pflegen).
// Blender-Welt in Metern, Z oben, Spieler blickt beim Start nach −Y. Umrechnung nach Unity: (−x, z, −y), wie ego.json › axes.to_unity.
// Gelesen wird mit MiniJson (JsonUtility kann weder Wörterbücher noch Arrays von Arrays). Unbekannte Schlüssel werden übersehen.
using System;
using System.Collections.Generic;
using UnityEngine;

namespace Ballon.Ego
{
    public sealed class SceneZone { public string name; public string[] objects; public int size; public float texel_m; }
    public sealed class SceneCollider { public string name, surface; public float[] center, size; }   // surface (0.39): Untergrund für Einschläge, "" = keiner
    public sealed class SceneSpawn { public float[] pos; public float yaw_deg; }
    public sealed class SceneSky { public string color; public float strength; }
    public sealed class SceneLight
    {
        public string name, kind, color;      // kind: area | sun | point | spot
        public float[] pos, dir;              // dir = Leuchtrichtung
        public float power_w, size_m;
        public float angle_deg;               // Öffnungswinkel für spot (Blender spot_size), fehlt: 90
    }
    public sealed class SceneReference
    {
        public string png;
        public float[] camera_pos;
        public float yaw_deg, pitch_deg, h_fov_deg;
    }

    /// <summary>Eine Lichtszene: Atlanten je Zone, Himmel, Umgebungslicht, Lichter fürs Viewmodel.</summary>
    public sealed class SceneLighting
    {
        public string name, de;
        public string[] atlasZones, atlasFiles;      // gleiche Reihenfolge: atlases { "zone": "datei.png" }
        public float scale;                           // Atlas = Licht / scale
        public SceneSky sky, ambient;
        public SceneLight[] lights;
        public SceneReference reference;             // optional

        public string AtlasFile(string zone)
        {
            for (int i = 0; i < atlasZones.Length; i++) if (atlasZones[i] == zone) return atlasFiles[i];
            return null;
        }
    }

    /// <summary>Achsparalleler Auslösequader (Blender-Raum): Start, Ziel, Kontrollpunkt.</summary>
    public sealed class SceneBox { public string name; public float[] center, size; }
    public sealed class CourseTargetData { public string name; public float[] pos, normal; public float radius; }

    public sealed class SceneCourse
    {
        public SceneBox start, finish;
        public SceneBox[] checkpoints;
        public CourseTargetData[] targets;
        public float[][] route;
        public float par_time_s;
    }

    /// <summary>Zielscheibe ohne Strecke (Schießstand, optional, wie in /1).</summary>
    public sealed class SceneTarget { public float[] pos; public float distance; }

    public sealed class SceneFile
    {
        public string format, name, de, fbx;
        public SceneZone[] zones;
        public string[] objects;
        public SceneCollider[] colliders;
        public SceneSpawn spawn;
        public SceneLighting[] lightings;
        public SceneCourse course;               // optional
        public SceneTarget[] targets;

        public const string Format = "ballon-scene/2";

        public int ZoneIndex(string zone)
        {
            for (int i = 0; i < zones.Length; i++) if (zones[i].name == zone) return i;
            return -1;
        }

        public string LightingLabel(int i) => string.IsNullOrEmpty(lightings[i].de) ? lightings[i].name : lightings[i].de;

        public static SceneFile Parse(string json)
        {
            object rootNode;
            try { rootNode = MiniJson.Parse(json); }
            catch (FormatException e) { throw new FormatException($"Szene: {e.Message}"); }
            var d = rootNode as Dictionary<string, object>;
            string fmt = d != null && d.TryGetValue("format", out var fv) ? fv as string : null;
            if (fmt != Format)
                throw new FormatException($"Szene: Format {(fmt ?? (d == null ? "leer" : "fehlt"))} statt {Format} – neu bauen (tools/scene_build.py)");
            return new Reader(d).Read();
        }

        // ------------------------------------------------------------------------------------------------ Lesen und Prüfen
        sealed class Reader
        {
            readonly Dictionary<string, object> _root;
            string _n = "?";
            public Reader(Dictionary<string, object> root) { _root = root; }

            FormatException Bad(string path, string what) => new FormatException($"Szene {_n}: {path} {what}");

            Dictionary<string, object> Obj(Dictionary<string, object> d, string key, string path, bool need = true)
            {
                if (d.TryGetValue(key, out var v) && v is Dictionary<string, object> o) return o;
                if (!need && (!d.TryGetValue(key, out v) || v == null)) return null;
                throw Bad($"{path}{key}", "fehlt oder ist kein Objekt");
            }

            List<object> Arr(Dictionary<string, object> d, string key, string path, bool need = true)
            {
                if (d.TryGetValue(key, out var v) && v is List<object> a) return a;
                if (!need && (!d.TryGetValue(key, out v) || v == null)) return null;
                throw Bad($"{path}{key}", "fehlt oder ist keine Liste");
            }

            string Str(Dictionary<string, object> d, string key, string path, bool need = true)
            {
                if (d.TryGetValue(key, out var v) && v is string s && s.Length > 0) return s;
                if (!need && (!d.TryGetValue(key, out v) || v == null)) return null;
                throw Bad($"{path}{key}", "fehlt oder ist keine Zeichenkette");
            }

            float Num(Dictionary<string, object> d, string key, string path, bool need, float dflt = 0f)
            {
                if (d.TryGetValue(key, out var v) && v is double x) return (float)x;
                if (!need && (!d.TryGetValue(key, out v) || v == null)) return dflt;
                throw Bad($"{path}{key}", "fehlt oder ist keine Zahl");
            }

            float[] Nums(object v, string path, int n)
            {
                if (!(v is List<object> a) || a.Count != n) throw Bad(path, $"braucht {n} Werte");
                var r = new float[n];
                for (int i = 0; i < n; i++)
                {
                    if (!(a[i] is double x)) throw Bad(path, "enthält eine Nichtzahl");
                    r[i] = (float)x;
                }
                return r;
            }

            float[] Vec3(Dictionary<string, object> d, string key, string path, bool need = true)
            {
                if (!d.TryGetValue(key, out var v) || v == null)
                {
                    if (need) throw Bad($"{path}{key}", "braucht 3 Werte");
                    return null;
                }
                return Nums(v, $"{path}{key}", 3);
            }

            string Color(Dictionary<string, object> d, string key, string path)
            {
                string c = Str(d, key, path);
                if (!SceneConvert.TryColor(c, out _)) throw Bad($"{path}{key}", "ist keine Farbe (#RRGGBB)");
                return c;
            }

            SceneBox Box(Dictionary<string, object> d, string key, string path)
            {
                var o = Obj(d, key, path);
                var b = new SceneBox { name = Str(o, "name", $"{path}{key}.", false), center = Vec3(o, "center", $"{path}{key}."), size = Vec3(o, "size", $"{path}{key}.") };
                if (b.size[0] <= 0 || b.size[1] <= 0 || b.size[2] <= 0) throw Bad($"{path}{key}.size", "muss positiv sein");
                return b;
            }

            string[] StrList(List<object> a, string path)
            {
                var r = new string[a.Count];
                for (int i = 0; i < r.Length; i++)
                    r[i] = a[i] as string ?? throw Bad($"{path}[{i}]", "ist keine Zeichenkette");
                return r;
            }

            public SceneFile Read()
            {
                var d = _root;
                var f = new SceneFile { format = Format };
                f.name = Str(d, "name", "");
                _n = f.name;
                f.de = Str(d, "de", "", false);
                f.fbx = Str(d, "fbx", "");
                var objs = Arr(d, "objects", "", false);
                f.objects = objs == null ? new string[0] : StrList(objs, "objects");

                // Zonen: jedes Objekt gehört zu genau einer Zone
                var za = Arr(d, "zones", "");
                if (za.Count == 0) throw Bad("zones", "braucht mindestens eine Zone");
                f.zones = new SceneZone[za.Count];
                var owner = new Dictionary<string, string>();
                for (int i = 0; i < za.Count; i++)
                {
                    if (!(za[i] is Dictionary<string, object> zo)) throw Bad($"zones[{i}]", "ist kein Objekt");
                    var z = new SceneZone { name = Str(zo, "name", $"zones[{i}]."), size = (int)Num(zo, "size", $"zones[{i}].", false), texel_m = Num(zo, "texel_m", $"zones[{i}].", false) };
                    var zl = Arr(zo, "objects", $"zones[{i}].", false);
                    z.objects = zl == null ? new string[0] : StrList(zl, $"zones[{i}].objects");
                    for (int k = 0; k < i; k++) if (f.zones[k].name == z.name) throw Bad($"zones[{i}].name", $"'{z.name}' kommt doppelt vor");
                    foreach (var o in z.objects)
                    {
                        if (owner.TryGetValue(o, out var other)) throw Bad($"zones[{i}].objects", $"'{o}' liegt schon in Zone '{other}' (genau eine Zone je Objekt)");
                        owner[o] = z.name;
                    }
                    f.zones[i] = z;
                }
                foreach (var o in f.objects)
                    if (!owner.ContainsKey(o)) throw Bad("objects", $"'{o}' gehört zu keiner Zone (genau eine Zone je Objekt)");

                var ca = Arr(d, "colliders", "", false);
                f.colliders = new SceneCollider[ca?.Count ?? 0];
                for (int i = 0; i < f.colliders.Length; i++)
                {
                    if (!(ca[i] is Dictionary<string, object> co)) throw Bad($"colliders[{i}]", "ist kein Objekt");
                    f.colliders[i] = new SceneCollider { name = Str(co, "name", $"colliders[{i}].", false), center = Vec3(co, "center", $"colliders[{i}]."), size = Vec3(co, "size", $"colliders[{i}]."),
                                                         surface = co.TryGetValue("surface", out var sv) && sv is string ss ? ss : "" };   // 0.39: "" = keiner, fehlt in älteren Szenen
                }

                var so = Obj(d, "spawn", "");
                f.spawn = new SceneSpawn { pos = Vec3(so, "pos", "spawn."), yaw_deg = Num(so, "yaw_deg", "spawn.", false) };

                // Lichtszenen: eigene Atlanten je Zone, Himmel, Umgebung, Lichter
                var la = Arr(d, "lightings", "");
                if (la.Count == 0) throw Bad("lightings", "braucht mindestens eine Lichtszene");
                f.lightings = new SceneLighting[la.Count];
                for (int i = 0; i < la.Count; i++) f.lightings[i] = ReadLighting(la[i], i, f);

                var co2 = Obj(d, "course", "", false);
                if (co2 != null) f.course = ReadCourse(co2);

                var ta = Arr(d, "targets", "", false);
                f.targets = new SceneTarget[ta?.Count ?? 0];
                for (int i = 0; i < f.targets.Length; i++)
                {
                    if (!(ta[i] is Dictionary<string, object> to)) throw Bad($"targets[{i}]", "ist kein Objekt");
                    f.targets[i] = new SceneTarget { pos = Vec3(to, "pos", $"targets[{i}]."), distance = Num(to, "distance", $"targets[{i}].", false) };
                }
                return f;
            }

            SceneLighting ReadLighting(object node, int i, SceneFile f)
            {
                string p = $"lightings[{i}].";
                if (!(node is Dictionary<string, object> lo)) throw Bad($"lightings[{i}]", "ist kein Objekt");
                var L = new SceneLighting { name = Str(lo, "name", p), de = Str(lo, "de", p, false) };
                for (int k = 0; k < i; k++) if (f.lightings[k].name == L.name) throw Bad($"{p}name", $"'{L.name}' kommt doppelt vor");
                L.scale = Num(lo, "scale", p, true);
                if (L.scale <= 0f) throw Bad($"{p}scale", "muss größer als 0 sein");
                var at = Obj(lo, "atlases", p);
                var zones = new List<string>();
                var files = new List<string>();
                foreach (var kv in at)
                {
                    if (f.ZoneIndex(kv.Key) < 0) throw Bad($"{p}atlases", $"nennt die unbekannte Zone '{kv.Key}'");
                    if (!(kv.Value is string fn) || fn.Length == 0) throw Bad($"{p}atlases.{kv.Key}", "braucht einen Dateinamen");
                    zones.Add(kv.Key);
                    files.Add(fn);
                }
                foreach (var z in f.zones)
                    if (!zones.Contains(z.name)) throw Bad($"{p}atlases", $"hat keinen Atlas für die Zone '{z.name}'");
                L.atlasZones = zones.ToArray();
                L.atlasFiles = files.ToArray();
                var sky = Obj(lo, "sky", p);
                L.sky = new SceneSky { color = Color(sky, "color", $"{p}sky."), strength = Num(sky, "strength", $"{p}sky.", false, 1f) };
                var amb = Obj(lo, "ambient", p);
                L.ambient = new SceneSky { color = Color(amb, "color", $"{p}ambient."), strength = Num(amb, "strength", $"{p}ambient.", false, 1f) };
                var ll = Arr(lo, "lights", p, false);
                L.lights = new SceneLight[ll?.Count ?? 0];
                for (int k = 0; k < L.lights.Length; k++) L.lights[k] = ReadLight(ll[k], $"{p}lights[{k}].");
                var ro = Obj(lo, "reference", p, false);
                if (ro != null)
                    L.reference = new SceneReference { png = Str(ro, "png", $"{p}reference.", false), camera_pos = Vec3(ro, "camera_pos", $"{p}reference.", false),
                        yaw_deg = Num(ro, "yaw_deg", $"{p}reference.", false), pitch_deg = Num(ro, "pitch_deg", $"{p}reference.", false),
                        h_fov_deg = Num(ro, "h_fov_deg", $"{p}reference.", false, 75f) };
                return L;
            }

            SceneLight ReadLight(object node, string p)
            {
                if (!(node is Dictionary<string, object> o)) throw Bad(p.TrimEnd('.'), "ist kein Objekt");
                var l = new SceneLight { name = Str(o, "name", p, false) ?? "?", kind = Str(o, "kind", p), pos = Vec3(o, "pos", p) };
                if (l.kind != "area" && l.kind != "sun" && l.kind != "point" && l.kind != "spot") throw Bad($"{p}kind", $"'{l.kind}' unbekannt");
                l.dir = Vec3(o, "dir", p, l.kind != "point");
                if (l.dir != null && new Vector3(l.dir[0], l.dir[1], l.dir[2]).sqrMagnitude < 1e-8f) throw Bad($"{p}dir", "darf nicht null sein");
                l.color = Color(o, "color", p);
                l.power_w = Num(o, "power_w", p, true);
                if (l.power_w < 0f) throw Bad($"{p}power_w", "ist negativ");
                l.size_m = Num(o, "size_m", p, l.kind == "area");
                if (l.kind == "area" && l.size_m <= 0f) throw Bad($"{p}size_m", "fehlt (Flächenlicht)");
                l.angle_deg = Num(o, "angle_deg", p, false);
                return l;
            }

            SceneCourse ReadCourse(Dictionary<string, object> o)
            {
                var c = new SceneCourse { start = Box(o, "start", "course."), finish = Box(o, "finish", "course.") };
                var cp = Arr(o, "checkpoints", "course.", false);
                c.checkpoints = new SceneBox[cp?.Count ?? 0];
                for (int i = 0; i < c.checkpoints.Length; i++)
                {
                    if (!(cp[i] is Dictionary<string, object> co)) throw Bad($"course.checkpoints[{i}]", "ist kein Objekt");
                    var holder = new Dictionary<string, object> { ["b"] = co };
                    c.checkpoints[i] = Box(holder, "b", $"course.checkpoints[{i}]");
                    c.checkpoints[i].name = Str(co, "name", $"course.checkpoints[{i}].", false) ?? $"Kontrollpunkt {i + 1}";
                }
                var ta = Arr(o, "targets", "course.", false);
                c.targets = new CourseTargetData[ta?.Count ?? 0];
                for (int i = 0; i < c.targets.Length; i++)
                {
                    string p = $"course.targets[{i}].";
                    if (!(ta[i] is Dictionary<string, object> to)) throw Bad(p.TrimEnd('.'), "ist kein Objekt");
                    var t = new CourseTargetData { name = Str(to, "name", p, false) ?? $"Z{i + 1:00}", pos = Vec3(to, "pos", p), normal = Vec3(to, "normal", p), radius = Num(to, "radius", p, true) };
                    if (new Vector3(t.normal[0], t.normal[1], t.normal[2]).sqrMagnitude < 1e-8f) throw Bad($"{p}normal", "darf nicht null sein");
                    if (t.radius <= 0f) throw Bad($"{p}radius", "muss positiv sein");
                    c.targets[i] = t;
                }
                var ra = Arr(o, "route", "course.", false);
                c.route = new float[ra?.Count ?? 0][];
                for (int i = 0; i < c.route.Length; i++) c.route[i] = Nums(ra[i], $"course.route[{i}]", 3);
                c.par_time_s = Num(o, "par_time_s", "course.", false);
                return c;
            }
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

        /// <summary>Auslösequader (Mitte, Kantenlängen in Blender) als Unity-Bounds.</summary>
        public static Bounds Box(SceneBox b) => new Bounds(Point(b.center), Size(b.size));

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
