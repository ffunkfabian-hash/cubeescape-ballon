// EditMode: Szenenformat ballon-scene/2 (kleine Fixture ohne FBX und Atlanten: 2 Zonen, 2 Lichtszenen, Kurs mit 2 Kontrollpunkten und
// 3 Zielen), Ablehnung von ballon-scene/1 und lückenhaften Dateien, Umrechnung Blender → Unity für Collider, Startpunkt, Richtungen,
// Lichter und Auslösequader.
using System;
using System.IO;
using NUnit.Framework;
using UnityEngine;

namespace Ballon.Ego.Tests
{
    public class SceneDataTests
    {
        const string Fixture = "Assets/Ballon/Tests/EditMode/scene_fixture_v2.json";
        const string FixtureV1 = "Assets/Ballon/Tests/EditMode/scene_fixture_v1.json";
        static string Json => File.ReadAllText(Fixture);
        static SceneFile F => SceneFile.Parse(Json);

        static void Near(Vector3 want, Vector3 got, string what, float tol = 1e-5f) =>
            Assert.That(Vector3.Distance(want, got), Is.LessThan(tol), $"{what}: {got:F4} statt {want:F4}");

        /// <summary>Erstes Vorkommen ersetzen; schlägt der Test fehl, wenn die Fixture den Text nicht (mehr) enthält.</summary>
        static string First(string s, string old, string nw)
        {
            int i = s.IndexOf(old, StringComparison.Ordinal);
            Assert.GreaterOrEqual(i, 0, $"Fixture enthält '{old}' nicht");
            return s.Remove(i, old.Length).Insert(i, nw);
        }

        static void Rejects(string json, string what)
        {
            var e = Assert.Throws<FormatException>(() => SceneFile.Parse(json), what);
            StringAssert.StartsWith("Szene", e.Message, what);
        }

        [Test]
        public void Szene_Format_und_Umfang()
        {
            var f = F;
            Assert.AreEqual(SceneFile.Format, f.format);
            Assert.AreEqual("ballon-scene/2", SceneFile.Format);
            Assert.AreEqual("testkurs", f.name);
            Assert.AreEqual("testkurs.fbx", f.fbx);
            Assert.AreEqual(2, f.zones.Length);
            Assert.AreEqual("nah", f.zones[0].name);
            Assert.AreEqual(1024, f.zones[0].size);
            Assert.AreEqual(0.08f, f.zones[1].texel_m, 1e-6f);
            CollectionAssert.AreEqual(new[] { "Boden", "Kiste" }, f.zones[0].objects);
            CollectionAssert.AreEqual(new[] { "Boden", "Kiste", "Wand_N" }, f.objects);
            Assert.AreEqual(1, f.ZoneIndex("fern"));
            Assert.AreEqual(-1, f.ZoneIndex("gibtsnicht"));
            Assert.AreEqual(2, f.colliders.Length);
            Assert.AreEqual(30f, f.spawn.yaw_deg);
            Assert.AreEqual(0, f.targets.Length, "targets (Schießstand) bleibt optional und leer");
            Assert.AreEqual(2, f.lightings.Length);
            Assert.AreEqual("Tag", f.LightingLabel(0));
            Assert.AreEqual("Nacht", f.LightingLabel(1));
        }

        [Test]
        public void Lichtszenen_Atlas_je_Zone_Himmel_Lichter()
        {
            var f = F;
            var tag = f.lightings[0];
            var nacht = f.lightings[1];
            Assert.AreEqual("testkurs_tag_nah.png", tag.AtlasFile("nah"));
            Assert.AreEqual("testkurs_tag_fern.png", tag.AtlasFile("fern"));
            Assert.AreEqual("testkurs_nacht_fern.png", nacht.AtlasFile("fern"));
            Assert.IsNull(nacht.AtlasFile("gibtsnicht"));
            Assert.AreEqual(3.0f, tag.scale);
            Assert.AreEqual(1.5f, nacht.scale);
            Assert.AreEqual(1.3f, tag.sky.strength, 1e-6f);
            Assert.AreEqual("#10182A", nacht.sky.color);
            Assert.AreEqual(0.3f, nacht.ambient.strength, 1e-6f);
            Assert.AreEqual(2, tag.lights.Length);
            Assert.AreEqual(3, nacht.lights.Length);
            Assert.AreEqual(70f, nacht.lights[0].angle_deg);
            Assert.IsNotNull(tag.reference);
            Assert.AreEqual(75f, tag.reference.h_fov_deg);
            Assert.IsNull(nacht.reference, "Referenzbild ist optional");
        }

        [Test]
        public void Alte_Formate_werden_mit_Hinweis_abgelehnt()
        {
            var v1 = File.ReadAllText(FixtureV1);
            StringAssert.Contains("ballon-scene/1", v1, "die alte Fixture ist wirklich /1");
            var e = Assert.Throws<FormatException>(() => SceneFile.Parse(v1));
            StringAssert.Contains("ballon-scene/1", e.Message);
            StringAssert.Contains("ballon-scene/2", e.Message);
            StringAssert.Contains("neu bauen (tools/scene_build.py)", e.Message);
            e = Assert.Throws<FormatException>(() => SceneFile.Parse(Json.Replace("ballon-scene/2", "ballon-scene/0")));
            StringAssert.Contains("neu bauen (tools/scene_build.py)", e.Message);
            e = Assert.Throws<FormatException>(() => SceneFile.Parse("{}"));
            StringAssert.Contains("neu bauen (tools/scene_build.py)", e.Message);
            Assert.Throws<FormatException>(() => SceneFile.Parse(""), "leer");
            Assert.Throws<FormatException>(() => SceneFile.Parse("{\"format\": \"ballon-scene/2\""), "abgeschnittenes JSON");
            Assert.Throws<FormatException>(() => SceneFile.Parse("[1, 2]"), "kein Objekt");
        }

        [Test]
        public void Luecken_und_Widersprueche_werden_abgelehnt()
        {
            var j = Json;
            Rejects(First(j, "\"pos\": [0, 20, 0]", "\"pos\": [0, 20]"), "spawn mit 2 Werten");
            Rejects(First(j, "\"size\": [1, 2, 1]", "\"size\": [1, 2]"), "Collider mit 2 Werten");
            Rejects(First(j, "\"kind\": \"spot\"", "\"kind\": \"laser\""), "unbekannte Lichtart");
            Rejects(First(j, "#9FB4C8", "blau"), "Himmelsfarbe");
            Rejects(First(j, "\"fbx\": \"testkurs.fbx\",", ""), "fbx fehlt");
            Rejects(First(j, "\"scale\": 1.5", "\"scale\": 0"), "scale 0");
            Rejects(First(j, "\"name\": \"nacht\"", "\"name\": \"tag\""), "doppelter Lichtszenenname");
            Rejects(First(j, ", \"fern\": \"testkurs_nacht_fern.png\"", ""), "Zone ohne Atlas in einer Lichtszene");
            Rejects(First(j, "\"fern\": \"testkurs_nacht_fern.png\"", "\"hof\": \"testkurs_nacht_fern.png\""), "Atlas für unbekannte Zone");
            Rejects(First(j, "\"objects\": [\"Wand_N\"]", "\"objects\": [\"Wand_N\", \"Boden\"]"), "Objekt in zwei Zonen");
            Rejects(First(j, "\"objects\": [\"Boden\", \"Kiste\", \"Wand_N\"]", "\"objects\": [\"Boden\", \"Kiste\", \"Wand_N\", \"Waise\"]"), "Objekt ohne Zone");
            Rejects(First(j, "\"zones\": [", "\"zonen\": ["), "zones fehlt");
            Rejects(First(j, "\"lightings\": [", "\"lichter\": ["), "lightings fehlt");
            Rejects(First(j, "[0, 16, 1.2]", "[0, 16]"), "Startbox mit 2 Werten");
            Rejects(First(j, "\"size\": [6, 0.4, 2.4]", "\"size\": [0, 0.4, 2.4]"), "Startbox ohne Ausdehnung");
            Rejects(First(j, "\"normal\": [0, 1, 0]", "\"normal\": [0, 0, 0]"), "Normale null");
            Rejects(First(j, "\"radius\": 0.45", "\"radius\": -1"), "Radius negativ");
            Rejects(First(j, "[0, 16, 0]", "[0, 16]"), "Streckenpunkt mit 2 Werten");
            Rejects(First(j, "\"power_w\": 800", "\"power_w\": -3"), "Leistung negativ");
        }

        [Test]
        public void Ohne_Parcours_gueltig()
        {
            var j = Json;
            int a = j.IndexOf("\"course\": {", StringComparison.Ordinal);
            int b = j.IndexOf("\"targets\": []", StringComparison.Ordinal);
            var f = SceneFile.Parse(j.Remove(a, b - a));
            Assert.IsNull(f.course, "course ist optional");
            Assert.AreEqual(2, f.lightings.Length);
        }

        [Test]
        public void Umrechnung_wie_ego_json_axes_to_unity()
        {
            // dieselbe Matrix wie in ego.json › axes.to_unity: Unity = (−x, z, −y)
            var D = EgoFile.Parse(File.ReadAllText("Assets/Ballon/Generated/ego.json"));
            foreach (var v in new[] { new Vector3(1, 2, 3), new Vector3(0, 20, 0), new Vector3(-7.5f, 0.25f, 13), Vector3.zero })
                Near(BMath.PointToUnity(D.toUnity, v), SceneConvert.Point(v), $"Punkt {v}");
            Near(new Vector3(-1, 3, -2), SceneConvert.Point(new float[] { 1, 2, 3 }), "float[]");
        }

        [Test]
        public void Collider_und_Startpunkt_nach_Unity()
        {
            var f = F;
            Near(new Vector3(0, -0.05f, 0), SceneConvert.Point(f.colliders[0].center), "Boden Mitte");
            Near(new Vector3(40, 0.1f, 60), SceneConvert.Size(f.colliders[0].size), "Boden Größe (x, z, y)");
            Near(new Vector3(-3, 0.5f, 4), SceneConvert.Point(f.colliders[1].center), "Kiste Mitte");
            Near(new Vector3(1, 1, 2), SceneConvert.Size(f.colliders[1].size), "Kiste Größe");
            Near(new Vector3(0, 0, -20), SceneConvert.Point(f.spawn.pos), "Startpunkt");
            Assert.AreEqual(-30f, SceneConvert.Yaw(f.spawn.yaw_deg), "Blender dreht nach links positiv, Unity nach rechts");
            // Blick nach −Y (Blender) ist +Z (Unity); 90° nach links (Blender: nach +X) ist −X in Unity
            Near(Vector3.forward, SceneConvert.Point(new Vector3(0, -1, 0)), "Blick 0°");
            Near(Vector3.left, Quaternion.Euler(0, SceneConvert.Yaw(90), 0) * Vector3.forward, "90° nach links", 1e-5f);
            Near(Vector3.left, SceneConvert.Point(new Vector3(1, 0, 0)), "Blender +X = Unity links");
        }

        [Test]
        public void Parcours_Daten_nach_Unity()
        {
            var c = F.course;
            Assert.IsNotNull(c);
            Assert.AreEqual(2, c.checkpoints.Length);
            Assert.AreEqual("Rechts hinten", c.checkpoints[1].name);
            Assert.AreEqual(3, c.targets.Length);
            Assert.AreEqual(45f, c.par_time_s);
            Assert.AreEqual(5, c.route.Length);
            // Auslösequader: Mitte (−x, z, −y), Kantenlängen (x, z, y)
            var s = SceneConvert.Box(c.start);
            Near(new Vector3(0, 1.2f, -16), s.center, "Start Mitte");
            Near(new Vector3(6, 2.4f, 0.4f), s.size, "Start Größe");
            Near(new Vector3(8, 1.2f, -4), SceneConvert.Box(c.checkpoints[0]).center, "Kontrollpunkt 1");
            Near(new Vector3(0, 1.2f, 12), SceneConvert.Box(c.finish).center, "Ziel Mitte");
            Assert.IsTrue(s.Contains(new Vector3(0, 0.9f, -16)));
            Assert.IsFalse(s.Contains(new Vector3(0, 0.9f, -15.5f)), "0,4 m dick");
            // Zielscheibe: Mitte, Normale (Blender +Y = Unity −Z), Radius
            Near(new Vector3(6, 1.6f, -8), SceneConvert.Point(c.targets[0].pos), "T01 Mitte");
            Near(Vector3.back, SceneConvert.Point(c.targets[0].normal), "T01 Normale");
            Near(Vector3.right, SceneConvert.Point(c.targets[1].normal), "T02 Normale (Blender −X = Unity +X)");
            Assert.AreEqual(0.45f, c.targets[1].radius);
            Near(new Vector3(-6, 0, 6), SceneConvert.Point(c.route[3]), "Strecke Punkt 4");
        }

        [Test]
        public void Lichter_Intensitaet_Farbe_und_Richtung()
        {
            var f = F;
            Assert.AreEqual(800f / (Mathf.PI * Mathf.PI), SceneConvert.Intensity("area", 800f), 1e-4f, "Fläche P/π²");
            Assert.AreEqual(400f / (4 * Mathf.PI * Mathf.PI), SceneConvert.Intensity("spot", 400f), 1e-4f, "Spot P/(4π²)");
            Assert.AreEqual(SceneConvert.Intensity("spot", 100f), SceneConvert.Intensity("point", 100f), 1e-6f);
            Assert.AreEqual(3f / Mathf.PI, SceneConvert.Intensity("sun", 3f), 1e-6f, "Sonne S/π");
            Assert.AreEqual(800f / (Mathf.PI * 1.5f * 1.5f), SceneConvert.Radiance(800f, 1.5f), 1e-3f, "Strahldichte P/(π·A)");
            Near(Vector3.down, SceneConvert.Point(f.lightings[0].lights[0].dir), "Strahler leuchtet nach unten");
            var c = SceneConvert.Linear("#808080");
            Assert.AreEqual(0.2159f, c.r, 1e-3f, "sRGB 0x80 linear");
            var g = SceneConvert.Gamma(c, 1f);
            Assert.AreEqual(128f / 255f, g.r, 2e-3f, "Gamma-Wert für Materialfarben");
            Assert.AreEqual(1f, g.a);
            // Atlas-Helligkeit: scale als lineare Zahl → Gamma-Wert; Unity linearisiert sie wieder zu scale
            var tint = SceneConvert.Gamma(Color.white, 3f);
            Assert.AreEqual(3f, tint.linear.r, 3e-2f, "_BaseColor = scale (linear gelesen)");
            Assert.IsFalse(SceneConvert.TryColor("rot", out _));
            Assert.IsFalse(SceneConvert.TryColor(null, out _));
        }

        [Test]
        public void Zielscheiben_Radius_wie_im_Parcours()
        {
            Assert.AreEqual(0.3f, RangeBuilder.TargetRadius(10f), 1e-6f);
            Assert.AreEqual(0.45f, RangeBuilder.TargetRadius(25f), 1e-6f);
            Assert.AreEqual(0.6f, RangeBuilder.TargetRadius(50f), 1e-6f);
        }

        [Test]
        public void MiniJson_liest_Zahlen_Texte_und_Verschachtelung()
        {
            var o = (System.Collections.Generic.Dictionary<string, object>)MiniJson.Parse(
                "{\"a\": [1, -2.5e1, [3, 4]], \"s\": \"x\\\"y\\n\\u00e4\", \"t\": true, \"n\": null, \"o\": {}}");
            var a = (System.Collections.Generic.List<object>)o["a"];
            Assert.AreEqual(1.0, (double)a[0]);
            Assert.AreEqual(-25.0, (double)a[1]);
            Assert.AreEqual(4.0, (double)((System.Collections.Generic.List<object>)a[2])[1]);
            Assert.AreEqual("x\"y\nä", (string)o["s"]);
            Assert.AreEqual(true, o["t"]);
            Assert.IsNull(o["n"]);
            Assert.Throws<FormatException>(() => MiniJson.Parse("{\"a\": }"));
            Assert.Throws<FormatException>(() => MiniJson.Parse("{\"a\": 1} x"));
        }
    }
}
