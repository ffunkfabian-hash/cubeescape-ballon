// PlayMode (Patch uebersicht-text): jede Beschriftung der Waffenübersicht passt ganz in ihr Rechteck – alle Waffen, alle Skins, mit und ohne Taste.
// OnGUI läuft im Batchmode nicht; gemessen wird mit MenuCard, den Zahlen des Zeichnens. Ohne lokale Serien dieselbe Rechnung mit sechs Spalten.
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace Ballon.Ego.Tests
{
    public class MenuTextTests
    {
        const int MinColumns = 6;
        static readonly Vector2Int[] Sizes = { new Vector2Int(1470, 956), new Vector2Int(1280, 720), new Vector2Int(1920, 1080) };

        [UnityTest]
        public IEnumerator Alle_Texte_der_Uebersicht_passen()
        {
            if (Object.FindAnyObjectByType<Bootstrap>() == null)
            {
                SceneManager.LoadScene("Firstfeel");
                yield return null;
                yield return null;
            }
            var b = Object.FindAnyObjectByType<Bootstrap>();
            var L = b.Player.layout;
            var all = b.Solvers.Select(s => s.D).ToArray();
            var bad = new List<string>();
            int texts = 0, smallest = int.MaxValue;
            void Check(GUIStyle st, string s, Rect r, int H)
            {
                int size = MenuCard.Fit(st, s, r, H), full = st.fontSize;
                st.fontSize = size;
                var z = st.CalcSize(new GUIContent(s));
                st.fontSize = full;
                texts++;
                if (H == Sizes[0].y) smallest = Mathf.Min(smallest, size);
                if (z.x > r.width || z.y > r.height)
                    bad.Add($"{H}p „{s.Replace('\n', '/')}“ {size} px: {z.x:F0} × {z.y:F0} in {r.width:F0} × {r.height:F0}");
            }
            foreach (var size in Sizes)
            {
                int H = size.y;
                var name = MenuCard.NameStyle(new GUIStyle(), H);
                var sub = MenuCard.SubStyle(new GUIStyle(), H);
                float cw = HudLayout.ColumnWidth(size.x, H, Mathf.Max(L.columns.Length, MinColumns));
                for (int i = 0; i < all.Length; i++)
                {
                    bool variant = L.RowUnits(i) < 1f;
                    var card = new Rect(0, 0, cw, EgoPlayer.RowH * H * L.RowUnits(i));
                    if (!variant) Check(name, L.Title(i), MenuCard.NameRect(card, H), H);
                    foreach (bool keyed in new[] { false, true })
                        for (int k = 0; k < Mathf.Max(1, all[i].textures?.skins?.Length ?? 0); k++)
                            Check(sub, L.CardSub(i, k, MenuCard.TwoLines(card, variant, H)), MenuCard.SubRect(card, variant, keyed, H), H);
                }
            }
            TestContext.WriteLine($"{all.Length} Waffen, {L.columns.Length} Spalten, {texts} Texte, kleinste Schrift bei {Sizes[0].x} × {Sizes[0].y}: {smallest} px");
            Assert.IsEmpty(bad, $"{bad.Count} von {texts} Texten zu groß:\n" + string.Join("\n", bad.Distinct().Take(40)));
            Assert.GreaterOrEqual(smallest, Mathf.RoundToInt(MenuCard.MinFont * Sizes[0].y), "Schrift nicht unter der Lesegrenze");
        }
    }
}
