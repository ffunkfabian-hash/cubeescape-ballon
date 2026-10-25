// EditMode: Szenenformat ballon-scene/1 (kleine Fixture ohne FBX und Atlas) und die Umrechnung Blender → Unity für Collider,
// Startpunkt, Richtungen und Lichter.
using System;
using System.IO;
using NUnit.Framework;
using UnityEngine;

namespace Ballon.Ego.Tests
{
    public class SceneDataTests
    {
        const string Fixture = "Assets/Ballon/Tests/EditMode/scene_fixture.json";
        static string Json => File.ReadAllText(Fixture);
        static SceneFile F => SceneFile.Parse(Json);

        static void Near(Vector3 want, Vector3 got, string what, float tol = 1e-5f) =>
            Assert.That(Vector3.Distance(want, got), Is.LessThan(tol), $"{what}: {got:F4} statt {want:F4}");

        [Test]
        public void Szene_Format_und_Umfang()
        {
            var f = F;
            Assert.AreEqual(SceneFile.Format, f.format);
            Assert.AreEqual("testraum", f.name);
            Assert.AreEqual("testraum.fbx", f.fbx);
            Assert.AreEqual("testraum_light.png", f.light_atlas.file);
            Assert.AreEqual(1024, f.light_atlas.size);
            CollectionAssert.AreEqual(new[] { "Boden", "Wand_N" }, f.objects);
            Assert.AreEqual(2, f.colliders.Length);
            Assert.AreEqual(4, f.lights.Length);
            Assert.AreEqual(2, f.targets.Length);
            Assert.AreEqual(30f, f.spawn.yaw_deg);
            Assert.AreEqual(0.45f, f.ambient.strength, 1e-6f);
            Assert.AreEqual(10f, f.targets[0].distance);
        }

        [Test]
        public void Falsches_Format_und_Luecken_werden_abgelehnt()
        {
            Assert.Throws<FormatException>(() => SceneFile.Parse(Json.Replace("ballon-scene/1", "ballon-scene/2")), "andere Version");
            Assert.Throws<FormatException>(() => SceneFile.Parse(""), "leer");
            Assert.Throws<FormatException>(() => SceneFile.Parse("{}"), "kein Format");
            Assert.Throws<FormatException>(() => SceneFile.Parse(Json.Replace("\"pos\": [0, 20, 0]", "\"pos\": [0, 20]")), "spawn mit 2 Werten");
            Assert.Throws<FormatException>(() => SceneFile.Parse(Json.Replace("\"size\": [1, 2, 1]", "\"size\": [1, 2]")), "Collider mit 2 Werten");
            Assert.Throws<FormatException>(() => SceneFile.Parse(Json.Replace("\"kind\": \"spot\"", "\"kind\": \"laser\"")), "unbekannte Lichtart");
            Assert.Throws<FormatException>(() => SceneFile.Parse(Json.Replace("#9FB4C8", "blau")), "Himmelsfarbe");
            Assert.Throws<FormatException>(() => SceneFile.Parse(Json.Replace("\"fbx\": \"testraum.fbx\",", "")), "fbx fehlt");
            var e = Assert.Throws<FormatException>(() => SceneFile.Parse(Json.Replace("ballon-scene/1", "ballon-scene/0")));
            StringAssert.Contains("ballon-scene/1", e.Message);
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
        public void Lichter_Intensitaet_Farbe_und_Richtung()
        {
            var f = F;
            Assert.AreEqual(800f / (Mathf.PI * Mathf.PI), SceneConvert.Intensity("area", 800f), 1e-4f, "Fläche P/π²");
            Assert.AreEqual(400f / (4 * Mathf.PI * Mathf.PI), SceneConvert.Intensity("spot", 400f), 1e-4f, "Spot P/(4π²)");
            Assert.AreEqual(SceneConvert.Intensity("spot", 100f), SceneConvert.Intensity("point", 100f), 1e-6f);
            Assert.AreEqual(3f / Mathf.PI, SceneConvert.Intensity("sun", 3f), 1e-6f, "Sonne S/π");
            Assert.AreEqual(800f / (Mathf.PI * 1.5f * 1.5f), SceneConvert.Radiance(800f, 1.5f), 1e-3f, "Strahldichte P/(π·A)");
            Near(Vector3.down, SceneConvert.Point(f.lights[0].dir), "Strahler leuchtet nach unten");
            var c = SceneConvert.Linear("#808080");
            Assert.AreEqual(0.2159f, c.r, 1e-3f, "sRGB 0x80 linear");
            var g = SceneConvert.Gamma(c, 1f);
            Assert.AreEqual(128f / 255f, g.r, 2e-3f, "Gamma-Wert für Materialfarben");
            Assert.AreEqual(1f, g.a);
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
    }
}
