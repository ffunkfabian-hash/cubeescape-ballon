// Waffenmenü (0.33 „Armory“, Ziel 2): Auswahl aller spielbaren Waffen in einem Raster (Reihenfolge wie ego.json › weapons, Taste 1 … 0
// für die ersten zehn). Öffnen mit Tab oder dem Mausrad, bewegen mit Mausrad und Pfeiltasten, wählen mit Enter oder Linksklick,
// schließen ohne Wahl mit Esc oder Tab. Die Wahl geht als RawInput.select an das Arsenal: aktive Waffe wegstecken (holster, beim
// Nachladen reload_to_switch), leere Sicht, neue Waffe ziehen – wie die Zifferntasten. Solange das Menü offen ist, schießen, zielen und
// blicken die Waffe und die Kamera nicht (die Maus bedient das Menü); Laufen bleibt. Reine C#-Klasse, kein Speicher je Bild.
using UnityEngine;

namespace Ballon.Ego
{
    /// <summary>Eingaben des Menüs aus einem Bild (DeviceInput füllt sie aus Tastatur und Maus).</summary>
    public struct MenuInput
    {
        public bool toggle, confirm, cancel;   // Tab, Enter/Linksklick, Esc
        public int wheel;                      // Mausrad: +1 nächste, −1 vorige Waffe
        public Vector2Int arrows;              // Pfeiltasten: x rechts, y unten (Raster)
    }

    public sealed class EgoMenu
    {
        public readonly int count, columns;
        public bool IsOpen { get; private set; }
        /// <summary>Markierte Waffe (Index) im offenen Menü.</summary>
        public int Index { get; private set; }

        public EgoMenu(int count, int columns = 4)
        {
            this.count = Mathf.Max(1, count);
            this.columns = Mathf.Clamp(columns, 1, this.count);
        }

        public int Rows => (count + columns - 1) / columns;

        /// <summary>Ein Bild: Menü öffnen, bewegen, schließen. Rückgabe: gewählte Waffe als Taste 1 … n (RawInput.select), sonst 0.
        /// active = aktive Waffe (Markierung beim Öffnen).</summary>
        public int Step(MenuInput m, int active)
        {
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
                return 0;
            }
            if (m.wheel != 0) Move(m.wheel);
            if (m.arrows.x != 0) Move(m.arrows.x);
            if (m.arrows.y != 0)
            {
                int k = Index + m.arrows.y * columns;               // Spalte halten, an den Enden umlaufen
                if (k < 0) k += Rows * columns;
                if (k >= Rows * columns) k -= Rows * columns;
                Index = Mathf.Min(k, count - 1);
            }
            if (m.confirm)
            {
                IsOpen = false;
                return Index + 1;
            }
            return 0;
        }

        void Move(int d) => Index = ((Index + d) % count + count) % count;

        /// <summary>Menü schließen ohne Wahl (Tod, Szenenwechsel, Tests).</summary>
        public void Close() => IsOpen = false;
    }
}
