// Waffen der Spielfigur (0.18 „Quickdraw“): je Waffe ein EgoController mit eigener Munition und eigenem Zustand, aktiv ist einer.
// Wechsel mit den Tasten 1/2 (und Q zur anderen Waffe) wie der Wechsel 6.1 A: aktive Waffe wegstecken (holster, beim Nachladen
// reload_to_switch), leere Sicht motion.switch.empty_s, neue Waffe ziehen (draw ab dem ersten sichtbaren Bild bzw. draw_aim). Die
// weggesteckte Waffe steht still (kein Tick): ihre Munition bleibt. Reine C#-Klasse wie der Controller; kein Speicher je Bild.
using System;
using UnityEngine;

namespace Ballon.Ego
{
    public sealed class EgoArsenal
    {
        public readonly EgoController[] C;
        public int Active { get; private set; }
        /// <summary>Ziel eines laufenden Wechsels (Index), sonst −1.</summary>
        public int Target { get; private set; } = -1;
        public EgoController Current => C[Active];
        public bool Switching => Target >= 0;
        /// <summary>(alte, neue Waffe), sobald die neue Waffe zu ziehen beginnt (EgoPlayer schaltet dann das Modell um).</summary>
        public event Action<int, int> Switched;

        float _empty;
        bool _out;

        public EgoArsenal(params EgoController[] controllers)
        {
            if (controllers == null || controllers.Length == 0) throw new ArgumentException("mindestens eine Waffe");
            C = controllers;
            foreach (var c in C) c.Prepare();                   // DrawEnters vorab (kein Speicher beim ersten Wechsel)
        }

        /// <summary>Waffe k sofort aktiv (Aufnahme, Vergleich, Tests), ohne Wechselablauf; ein laufender Wechsel entfällt.</summary>
        public void Select(int k)
        {
            if (k < 0 || k >= C.Length) throw new ArgumentOutOfRangeException(nameof(k));
            int from = Active;
            Active = k;
            Target = -1;
            _out = false;
            if (from != k) Switched?.Invoke(from, k);
        }

        /// <summary>Ein Bild. select: Taste 1 … n (0 = keine). Taste der aktiven Waffe zieht sie, wenn sie weggesteckt ist; Taste einer
        /// anderen Waffe wechselt; Q (intent.swap) wechselt bei mehreren Waffen zur nächsten, mit einer Waffe wie bisher (6.1 A).</summary>
        public EgoOutput Tick(float dt, EgoIntent i, int select = 0)
        {
            if (i.swap && C.Length > 1)
            {
                select = (Active + 1) % C.Length + 1;
                i.swap = false;
            }
            int want = select - 1;
            if (want >= 0 && want < C.Length && !Switching)
            {
                if (want != Active)
                {
                    Target = want;
                    _out = false;
                    Current.SwitchOut();
                }
                else if (Current.Holstered) i.draw = true;
            }
            if (Switching)
            {
                if (!_out && Current.SwitchedOut)              // im letzten Bild weggesteckt: leere Sicht läuft ab diesem Bild
                {
                    _out = true;
                    _empty = Current.S.D.motion.@switch.empty_s;
                }
                if (_out && (_empty -= dt) <= 0)               // wie EgoController beim Wechsel mit Q: nach empty_s im selben Bild ziehen
                {
                    int from = Active;
                    Active = Target;
                    Target = -1;
                    _out = false;
                    Current.SwitchIn();
                    Switched?.Invoke(from, Active);
                }
                i.draw = false;
            }
            return Current.Tick(dt, i);
        }
    }
}
