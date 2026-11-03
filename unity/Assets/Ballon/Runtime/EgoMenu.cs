// Waffenmenü (0.33 „Armory“, Ziel 2): Auswahl aller spielbaren Waffen in einem Raster (Reihenfolge wie ego.json › weapons, Taste 1 … 0
// für die ersten zehn). Öffnen mit Tab oder dem Mausrad, bewegen mit Mausrad und Pfeiltasten, wählen mit Enter oder Linksklick,
// schließen ohne Wahl mit Esc oder Tab. Die Wahl geht als RawInput.select an das Arsenal: aktive Waffe wegstecken (holster, beim
// Nachladen reload_to_switch), leere Sicht, neue Waffe ziehen – wie die Zifferntasten. Solange das Menü offen ist, schießen, zielen und
// blicken die Waffe und die Kamera nicht (die Maus bedient das Menü); Laufen bleibt. Reine C#-Klasse, kein Speicher je Bild.
// 0.42 „Quickslot“: Spalten nach Kategorien (HudLayout: Primär, Spezial, Schwer/Werkzeug), Pfeile hoch/runter in der Spalte, links/rechts
// in die Nachbarspalte; Zahl 1–9 legt die markierte Waffe auf diesen Platz der Leiste (Tastatur-Weg, Trackpad); mit der Maus zeigen,
// klicken (wählen) oder auf einen Platz der Leiste ziehen. Der Raster-Konstruktor bleibt (Tests seit 0.33).
using UnityEngine;

namespace Ballon.Ego
{
    /// <summary>Eingaben des Menüs aus einem Bild (DeviceInput füllt sie aus Tastatur und Maus).</summary>
    public struct MenuInput
    {
        public bool toggle, confirm, cancel;   // Tab, Enter, Esc
        public int wheel;                      // Mausrad: +1 nächste, −1 vorige Waffe
        public Vector2Int arrows;              // Pfeiltasten: x rechts, y unten (Raster)
        public int digit;                      // 0.42: Taste 1–9 bei offenem Menü – markierte Waffe auf diesen Platz der Leiste (0 = keine)
        // 0.42 Maus, roh aus DeviceInput: Zeiger (GUI-Pixel, Ursprung oben links), bewegt, Taste gedrückt/losgelassen in diesem Bild
        public Vector2 pointer;
        public bool moved, down, up;
        // daraus EgoPlayer (trifft die Rechtecke): Waffe + 1 unter dem Zeiger beim Zeigen/Drücken/Loslassen (0 = nichts, release −1 =
        // daneben losgelassen), Platz + 1 der Leiste beim Loslassen
        public int hover, press, release, releaseSlot;
    }

    public sealed class EgoMenu
    {
        public readonly int count, columns;
        public bool IsOpen { get; private set; }
        /// <summary>Markierte Waffe (Index) im offenen Menü.</summary>
        public int Index { get; private set; }
        /// <summary>Platz (0–8) und Waffe, die dieses Bild auf die Leiste gelegt werden sollen (Zahl oder Ziehen); sonst −1.</summary>
        public int AssignSlot { get; private set; } = -1;
        public int AssignWeapon { get; private set; } = -1;
        /// <summary>Waffe, die gerade mit der Maus gezogen wird, sonst −1.</summary>
        public int Dragging { get; private set; } = -1;
        /// <summary>Spalten (Waffenindizes von oben nach unten) und Lesereihenfolge (Mausrad).</summary>
        public readonly int[][] cols;
        readonly int[] _order, _col, _row, _pos;

        /// <summary>Raster wie seit 0.33: Waffen 0 … count−1 zeilenweise in columns Spalten.</summary>
        public EgoMenu(int count, int columns = 4) : this(Grid(Mathf.Max(1, count), Mathf.Clamp(columns, 1, Mathf.Max(1, count))), null) { }

        /// <summary>Spalten nach Kategorien (HudLayout.columns); order: Lesereihenfolge, null = Index-Reihenfolge.</summary>
        public EgoMenu(int[][] columns, int[] order)
        {
            cols = columns;
            int n = 0;
            foreach (var c in cols) n += c.Length;
            count = Mathf.Max(1, n);
            this.columns = cols.Length;
            _col = new int[count];
            _row = new int[count];
            _pos = new int[count];
            for (int c = 0; c < cols.Length; c++)
                for (int r = 0; r < cols[c].Length; r++) { _col[cols[c][r]] = c; _row[cols[c][r]] = r; }
            _order = order ?? new int[count];
            if (order == null) for (int k = 0; k < count; k++) _order[k] = k;
            for (int k = 0; k < count; k++) _pos[_order[k]] = k;
        }

        static int[][] Grid(int count, int columns)
        {
            var g = new int[columns][];
            for (int c = 0; c < columns; c++)
            {
                g[c] = new int[(count - c + columns - 1) / columns];
                for (int r = 0; r < g[c].Length; r++) g[c][r] = r * columns + c;
            }
            return g;
        }

        public int Rows
        {
            get { int r = 0; foreach (var c in cols) r = Mathf.Max(r, c.Length); return r; }
        }

        /// <summary>Ein Bild: Menü öffnen, bewegen, schließen. Rückgabe: gewählte Waffe als Taste 1 … n (RawInput.select), sonst 0.
        /// active = aktive Waffe (Markierung beim Öffnen).</summary>
        public int Step(MenuInput m, int active)
        {
            AssignSlot = AssignWeapon = -1;
            if (!IsOpen)
            {
                if (m.toggle || m.wheel != 0)
                {
                    IsOpen = true;
                    Index = Mathf.Clamp(active, 0, count - 1);
                    if (m.wheel != 0) Move(m.wheel);              // Mausrad öffnet und zeigt gleich die nächste bzw. vorige Waffe
                }
                return 0;
            }
            if (m.cancel || m.toggle)
            {
                IsOpen = false;
                Dragging = -1;
                return 0;
            }
            if (m.wheel != 0) Move(m.wheel);
            if (m.arrows.x != 0)                                     // Nachbarspalte, Zeile halten (kürzere Spalte: letzte Zeile)
            {
                int c = ((_col[Index] + m.arrows.x) % cols.Length + cols.Length) % cols.Length;
                Index = cols[c][Mathf.Min(_row[Index], cols[c].Length - 1)];
            }
            if (m.arrows.y != 0)                                     // in der Spalte, an den Enden umlaufen
            {
                var col = cols[_col[Index]];
                Index = col[((_row[Index] + m.arrows.y) % col.Length + col.Length) % col.Length];
            }
            if (m.hover > 0 && m.hover <= count) Index = m.hover - 1;
            if (m.digit >= 1 && m.digit <= HudLayout.Slots)          // Tastatur: markierte Waffe auf Platz digit
            {
                AssignSlot = m.digit - 1;
                AssignWeapon = Index;
            }
            if (m.press > 0 && m.press <= count)
            {
                Dragging = m.press - 1;
                Index = Dragging;
            }
            if (m.release != 0 || m.releaseSlot > 0)                 // losgelassen: auf einem Platz, auf einer Waffe oder daneben (−1)
            {
                int w = Dragging;
                Dragging = -1;
                if (w >= 0 && m.releaseSlot > 0)                     // auf einen Platz der Leiste gezogen
                {
                    AssignSlot = m.releaseSlot - 1;
                    AssignWeapon = w;
                }
                else if (w >= 0 && m.release == w + 1)               // Klick: auf derselben Waffe losgelassen – wählen
                {
                    IsOpen = false;
                    return w + 1;
                }
            }
            if (m.confirm)
            {
                IsOpen = false;
                return Index + 1;
            }
            return 0;
        }

        void Move(int d) => Index = _order[((_pos[Index] + d) % count + count) % count];

        /// <summary>Eingaben eines Bilds, solange das Menü offen ist (oder im Bild des Schließens): die Maus bedient das Menü – kein Feuer,
        /// kein Zielen, kein Blick. Beim gespannten Bogen hieße „kein Feuer“ Loslassen und damit einen Schuss (Richter 0.33, 4a): das Menü
        /// entspannt ihn stattdessen wie die Nachladen-Taste.</summary>
        public static void Filter(ref RawInput r, bool drawing)
        {
            if (drawing && r.fire) r.reload = true;
            r.fire = r.aim = false;
            r.lookDeg = Vector2.zero;
        }

        /// <summary>Menü öffnen bei Waffe active (Sichtprüfung -ballonMenu, Tests).</summary>
        public void Open(int active)
        {
            IsOpen = true;
            Index = Mathf.Clamp(active, 0, count - 1);
        }

        /// <summary>Menü schließen ohne Wahl (Tod, Szenenwechsel, Tests).</summary>
        public void Close()
        {
            IsOpen = false;
            Dragging = -1;
        }
    }
}
