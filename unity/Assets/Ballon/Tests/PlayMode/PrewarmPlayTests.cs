// PlayMode (0.38 „Prewarm“): Die Szene trägt die aufgezeichneten Shader-Zustände (ShaderWarmup.AssetPath) für Metal auf macOS, und
// jeder Shader, den die Welt beim Start zeichnet (Waffen, Arme, Parcours, Welteffekte), steht darin. Kommt ein Shader dazu (neuer
// Effekt, neues Material), scheitert der Test: dann `python3 tools/unity_run.py aufwaermen`. Varianten innerhalb eines Shaders
// (neue Schlüsselwörter) zeigt erst die kalte Ruckelmessung (`unity_run.py ruckeln <name> kalt`, Bild > 50 ms beim ersten Einsatz).
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace Ballon.Ego.Tests
{
    public class PrewarmPlayTests
    {
        [UnitySetUp]
        public IEnumerator LoadScene()
        {
            if (Object.FindAnyObjectByType<Bootstrap>() == null)
            {
                SceneManager.LoadScene("Firstfeel");
                yield return null;
                yield return null;
            }
        }

        [Test]
        public void Aufwaermen_Sammlung_deckt_alle_Shader_der_Welt()
        {
            var b = Object.FindAnyObjectByType<Bootstrap>();
            Assert.IsNotNull(b, "Szene Firstfeel ohne Bootstrap");
            var g = b.shaderWarmup;
            Assert.IsNotNull(g, $"Bootstrap.shaderWarmup leer – {ShaderWarmup.AssetPath} fehlt (python3 tools/unity_run.py aufwaermen)");
            Assert.AreEqual(GraphicsDeviceType.Metal, g.graphicsDeviceType, "Sammlung nicht für Metal aufgezeichnet");
            Assert.AreEqual(RuntimePlatform.OSXPlayer, g.runtimePlatform, "Sammlung nicht im macOS-Spieler aufgezeichnet");
            Assert.Greater(g.totalGraphicsStateCount, 0, "Sammlung ohne Zustände");

            var variants = new List<GraphicsStateCollection.ShaderVariant>();
            g.GetVariants(variants);
            var have = new HashSet<string>(variants.Where(v => v.shader != null).Select(v => v.shader.name));
            var mats = Object.FindObjectsByType<Renderer>(FindObjectsInactive.Include, FindObjectsSortMode.None)
                             .SelectMany(r => r.sharedMaterials)
                             .Concat(new[] { b.fxSpark, b.fxGlow, b.fxSmoke, b.fxRing, b.fxBeam, b.decal });
            var need = new SortedSet<string>(mats.Where(m => m != null && m.shader != null).Select(m => m.shader.name));
            var missing = need.Where(n => !have.Contains(n)).ToArray();
            TestContext.WriteLine($"{g.variantCount} Varianten, {g.totalGraphicsStateCount} Zustände; Shader der Welt: {string.Join(", ", need)}");
            Assert.IsEmpty(missing, $"Shader ohne aufgezeichnete Zustände: {string.Join(", ", missing)} – python3 tools/unity_run.py aufwaermen");
        }
    }
}
