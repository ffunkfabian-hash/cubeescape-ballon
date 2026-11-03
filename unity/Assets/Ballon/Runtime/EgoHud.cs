// Waffenübersicht nach Kategorien, Leiste 1–9 und Standard-Skins (0.42 „Quickslot“, Nutzer 03.11.2026: „Ein passendes HUD mit den Waffen in
// Kategorien, und unten eine Leiste 1–9, auf die man die Waffen legen kann. Außerdem die Waffen mit Farben anstelle von Weiß sehen.“).
// Alles kommt aus ego.json › hud (basic/loadout.py): Kategorie über die Klasse (profile.type), Standardleiste als Klassen, Standard-Skin je
// Klasse; Formgen-Varianten stehen hinter ihrem Grundtyp und tragen den Skin ihrer Linie. Keine Waffen-IDs im Code. Die Belegung der
// Leiste und der Skin je Waffe bleiben über Neustarts (LoadoutStore, Format ballon-loadout/1). Reine C#-Klassen, kein Speicher je Bild.
using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace Ballon.Ego
{
    /// <summary>Waffen geordnet nach Kategorien (Spalten der Übersicht) und Standardwerte der Leiste und der Skins.</summary>
    public sealed class HudLayout
    {
        public sealed class Category
        {
            public string id, de;
            public Color color;
            public int[] weapons;               // Indizes in ego.json › weapons
        }

        public const int Slots = 9;
        public readonly Category[] categories;
        /// <summary>Kategorie je Waffe (Index in categories).</summary>
        public readonly int[] categoryOf;
        /// <summary>Spalten der Übersicht (Waffenindizes von oben nach unten): Primär, Spezial, Schwer mit Werkzeug und Weiteren darunter; eine
        /// Spalte mit mehr als MaxRows Waffen wird geteilt (künftige Formgen-Varianten).</summary>
        public readonly int[][] columns;
        public const int MaxRows = 9;
        readonly EgoFile[] _d;

        public HudLayout(EgoFile[] d)
        {
            _d = d;
            var hud = d.Length > 0 ? d[0].hud : null;
            var cats = new List<Category>();
            categoryOf = new int[d.Length];
            for (int i = 0; i < d.Length; i++) categoryOf[i] = -1;
            if (hud?.categories != null)
                foreach (var c in hud.categories)
                {
                    var list = new List<int>();
                    foreach (var cls in c.classes ?? new string[0])
                    {
                        for (int i = 0; i < d.Length; i++)          // Grundtyp vor seinen Varianten (ego.json: BALLONs Waffen zuerst)
                            if (!d[i].IsVariant && Type(i) == cls && categoryOf[i] < 0) { list.Add(i); categoryOf[i] = cats.Count; }
                        for (int i = 0; i < d.Length; i++)
                            if (d[i].IsVariant && Type(i) == cls && categoryOf[i] < 0) { list.Add(i); categoryOf[i] = cats.Count; }
                    }
                    ColorUtility.TryParseHtmlString(c.color ?? "#FFFFFF", out var col);
                    if (list.Count > 0) cats.Add(new Category { id = c.id, de = c.de, color = col, weapons = list.ToArray() });
                }
            var rest = new List<int>();                              // /11 ohne hud oder Klasse ohne Kategorie: nichts geht verloren
            for (int i = 0; i < d.Length; i++)
                if (categoryOf[i] < 0) { rest.Add(i); categoryOf[i] = cats.Count; }
            if (rest.Count > 0)
                cats.Add(new Category { id = "other", de = hud == null ? "Waffen" : "Weitere", color = Color.white, weapons = rest.ToArray() });
            categories = cats.ToArray();
            var cols = new List<int[]>();
            for (int c = 0; c < categories.Length; c++)
            {
                var col = new List<int>(categories[c].weapons);
                if (c == 2) for (int k = 3; k < categories.Length; k++) col.AddRange(categories[k].weapons);   // Werkzeug unter Schwer
                for (int r = 0; r < col.Count; r += MaxRows) cols.Add(col.GetRange(r, Mathf.Min(MaxRows, col.Count - r)).ToArray());
                if (c == 2) break;
            }
            columns = cols.ToArray();
        }

        /// <summary>Waffen in der Lesereihenfolge der Übersicht (Spalte für Spalte): Mausrad und Tests.</summary>
        public int[] Order()
        {
            var o = new List<int>();
            foreach (var c in columns) o.AddRange(c);
            return o.ToArray();
        }

        string Type(int i) => _d[i].profile?.type ?? _d[i].gameplay.weapon_type;

        /// <summary>Standardbelegung: je Platz die erste Waffe der Klasse aus hud.hotbar (BALLONs Waffen vor Varianten); ohne hud die Waffen
        /// 1–9 aus ego.json wie bis 0.41. Platz ohne passende Waffe: leer (−1).</summary>
        public int[] DefaultSlots()
        {
            var s = new int[Slots];
            var hb = _d.Length > 0 ? _d[0].hud?.hotbar : null;
            for (int k = 0; k < Slots; k++)
            {
                s[k] = -1;
                if (hb == null) { s[k] = k < _d.Length ? k : -1; continue; }
                if (k >= hb.Length) continue;
                for (int i = 0; i < _d.Length && s[k] < 0; i++)
                    if (!_d[i].IsVariant && Type(i) == hb[k]) s[k] = i;
                for (int i = 0; i < _d.Length && s[k] < 0; i++)
                    if (Type(i) == hb[k]) s[k] = i;
            }
            return s;
        }

        /// <summary>Name des Standard-Skins der Waffe i: Formgen-Variante = ihr einziger Atlas (Skin der Linie, Index 0), sonst
        /// hud.default_skin der Klasse; ohne Eintrag „standard“.</summary>
        public string DefaultSkin(int i)
        {
            if (_d[i].IsVariant) return SkinName(i, 0);
            var ds = _d[i].hud?.default_skin;
            if (ds != null) foreach (var e in ds) if (e.type == Type(i)) return e.skin;
            return "standard";
        }

        /// <summary>Wie die Waffe beim Start aussieht (Skin-Name aus kit.SKINS): Formgen-Variante = Skin ihrer Linie (origin.skin; im Atlas
        /// heißt er „standard“), sonst DefaultSkin – für den Vergleich der Nachbarn in Übersicht und Leiste.</summary>
        public string SkinLook(int i) => _d[i].IsVariant && !string.IsNullOrEmpty(_d[i].origin?.skin) ? _d[i].origin.skin : DefaultSkin(i);

        /// <summary>Index des Skins name der Waffe i (textures.skins), −1 wenn er nicht gebacken ist.</summary>
        public int SkinIndex(int i, string name)
        {
            var sk = _d[i].textures?.skins;
            if (sk == null || name == null) return -1;
            for (int k = 0; k < sk.Length; k++) if (sk[k].name == name) return k;
            return -1;
        }

        public string SkinName(int i, int k)
        {
            var sk = _d[i].textures?.skins;
            return sk != null && k >= 0 && k < sk.Length ? sk[k].name : "standard";
        }

        /// <summary>Anzeigename der Skins: Variante „Eloxal“ statt „Skin der Linie: Eloxal“.</summary>
        public string SkinLabel(int i, int k)
        {
            var sk = _d[i].textures?.skins;
            if (sk == null || k < 0 || k >= sk.Length) return "";
            var de = sk[k].de ?? sk[k].name;
            int c = de.IndexOf(": ", StringComparison.Ordinal);
            return c >= 0 ? de.Substring(c + 2) : de;
        }

        /// <summary>Zeile unter dem Klassennamen: Modellname bzw. „Variante BD01“ (Formgen).</summary>
        public string Subtitle(int i) => _d[i].IsVariant ? $"Variante {_d[i].weapon.id}" : _d[i].weapon.name;

        public string Id(int i) => _d[i].weapon.id;
    }

    /// <summary>Leiste mit neun Plätzen (Tasten 1–9). Eine Waffe liegt höchstens auf einem Platz: wer sie auf einen anderen Platz legt,
    /// tauscht die beiden Plätze (die Leiste bleibt voll).</summary>
    public sealed class Hotbar
    {
        public readonly int[] slots = new int[HudLayout.Slots];
        /// <summary>Zählt jede Änderung (Anzeige und Speichern bauen nur bei Änderung neu).</summary>
        public int Version { get; private set; }

        public Hotbar(int[] init)
        {
            for (int k = 0; k < slots.Length; k++) slots[k] = init != null && k < init.Length ? init[k] : -1;
        }

        public int SlotOf(int weapon)
        {
            if (weapon < 0) return -1;
            for (int k = 0; k < slots.Length; k++) if (slots[k] == weapon) return k;
            return -1;
        }

        /// <summary>Waffe auf Platz slot (0–8) legen; lag sie schon auf einem anderen Platz, wandert der bisherige Inhalt dorthin.</summary>
        public void Assign(int slot, int weapon)
        {
            if (slot < 0 || slot >= slots.Length || weapon < 0) return;
            int from = SlotOf(weapon);
            if (from == slot) return;
            if (from >= 0) slots[from] = slots[slot];
            slots[slot] = weapon;
            Version++;
        }

        /// <summary>Waffe hinter Taste key (1–9), −1 bei leerem Platz.</summary>
        public int WeaponAt(int key) => key >= 1 && key <= slots.Length ? slots[key - 1] : -1;
    }

    /// <summary>Gespeicherte Leiste und Skins je Waffe (JSON in Application.persistentDataPath, Format ballon-loadout/1). Waffen und Skins
    /// stehen mit ihrer ID bzw. ihrem Namen in der Datei, damit eine neue Waffe in ego.json die Belegung nicht verschiebt.</summary>
    public sealed class LoadoutStore
    {
        public const string Format = "ballon-loadout/1";
        [Serializable] public class SkinEntry { public string weapon, skin; }
        [Serializable] public class FileData { public string format; public string[] slots; public SkinEntry[] skins; }

        public readonly string path;
        public LoadoutStore(string path) { this.path = path; }

        /// <summary>Datei lesen: Plätze (Index je Platz, −1 leer/unbekannt) und Skin-Namen je Waffe (null = Standard). false ohne Datei oder
        /// bei falschem Format (dann bleibt die Standardbelegung; eine kaputte Datei meldet eine Warnung).</summary>
        public bool Load(HudLayout L, int weapons, out int[] slots, out string[] skins)
        {
            slots = null;
            skins = new string[weapons];
            if (string.IsNullOrEmpty(path) || !File.Exists(path)) return false;
            FileData f;
            try { f = JsonUtility.FromJson<FileData>(File.ReadAllText(path)); }
            catch (Exception e) { Debug.LogWarning($"[Ballon] Leiste {path} unlesbar ({e.Message}) – Standardbelegung"); return false; }
            if (f == null || f.format != Format)
            {
                Debug.LogWarning($"[Ballon] Leiste {path}: Format {f?.format ?? "leer"} statt {Format} – Standardbelegung");
                return false;
            }
            var ids = new Dictionary<string, int>();
            for (int i = 0; i < weapons; i++) ids[L.Id(i)] = i;
            slots = new int[HudLayout.Slots];
            for (int k = 0; k < slots.Length; k++)
                slots[k] = f.slots != null && k < f.slots.Length && f.slots[k] != null && ids.TryGetValue(f.slots[k], out int w) ? w : -1;
            for (int k = 0; k < slots.Length; k++)                   // doppelt (von Hand bearbeitet): nur der erste Platz zählt
                for (int j = 0; j < k; j++)
                    if (slots[k] >= 0 && slots[j] == slots[k]) slots[k] = -1;
            if (f.skins != null)
                foreach (var e in f.skins)
                    if (e?.weapon != null && ids.TryGetValue(e.weapon, out int w)) skins[w] = e.skin;
            return true;
        }

        public void Save(HudLayout L, Hotbar bar, string[] skins)
        {
            if (string.IsNullOrEmpty(path)) return;
            var f = new FileData { format = Format, slots = new string[bar.slots.Length] };
            for (int k = 0; k < bar.slots.Length; k++) f.slots[k] = bar.slots[k] >= 0 ? L.Id(bar.slots[k]) : "";
            var list = new List<SkinEntry>();
            for (int i = 0; i < skins.Length; i++) if (skins[i] != null) list.Add(new SkinEntry { weapon = L.Id(i), skin = skins[i] });
            f.skins = list.ToArray();
            try
            {
                Directory.CreateDirectory(Path.GetDirectoryName(path));
                File.WriteAllText(path, JsonUtility.ToJson(f, true));
            }
            catch (Exception e) { Debug.LogWarning($"[Ballon] Leiste nicht gespeichert ({path}): {e.Message}"); }
        }
    }
}
