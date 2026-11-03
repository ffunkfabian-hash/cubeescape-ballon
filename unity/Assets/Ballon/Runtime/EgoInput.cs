// Eingabequellen: Maus/Tastatur über das Input System oder ein Ablauf (Aufnahme, Tests).
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;

namespace Ballon.Ego
{
    public struct RawInput
    {
        public Vector2 lookDeg;         // Blickänderung in Grad (x rechts, y hoch)
        public Vector2 move;            // x rechts, y vorn
        public bool sprint, crouch, jump, fire, aim, reload, inspect, draw, holster, swap;   // swap: Waffe wechseln (6.1 A)
        public int select;              // Waffe 1 … n direkt wählen (0.18, EgoArsenal; 0 = keine): Menü, Aufnahmen, Tests
        public int slot;                // 0.42: Taste 1–9 der Leiste (0 = keine): Waffe des Platzes wählen, bei offenem Menü Platz belegen
        public MenuInput menu;          // 0.33 Ziel 2: Waffenmenü (Tab, Mausrad, Pfeile, Enter, Esc)
    }

    public interface IEgoInput
    {
        RawInput Read(float dt, float zoom);
    }

    /// <summary>Maus und Tastatur. Empfindlichkeit in Grad je Mauspunkt (Standard, später einstellbar), im Zielen durch den Zoom geteilt.</summary>
    public sealed class DeviceInput : IEgoInput
    {
        public float sensitivity = 0.08f;
        public bool invertY;
        /// <summary>Waffenmenü offen (EgoPlayer setzt es je Bild): Esc schließt das Menü statt den Mauszeiger freizugeben; der Mauszeiger ist
        /// frei (zeigen, klicken, auf die Leiste ziehen) und wird beim Schließen wieder gefangen, wenn er vorher gefangen war.</summary>
        public bool menuOpen;
        bool _menuWas, _lockedBefore;
        Vector2 _lastPointer;

        public RawInput Read(float dt, float zoom)
        {
            var r = new RawInput();
            var k = Keyboard.current;
            var m = Mouse.current;
            if (k == null || m == null) return r;
            r.menu.toggle = k.tabKey.wasPressedThisFrame;
            r.menu.cancel = k.escapeKey.wasPressedThisFrame && menuOpen;
            r.menu.confirm = menuOpen && (k.enterKey.wasPressedThisFrame || k.numpadEnterKey.wasPressedThisFrame);
            float wheel = m.scroll.ReadValue().y;
            r.menu.wheel = wheel < 0 ? 1 : wheel > 0 ? -1 : 0;           // Rad nach unten: nächste Waffe
            r.menu.arrows = new Vector2Int((k.rightArrowKey.wasPressedThisFrame ? 1 : 0) - (k.leftArrowKey.wasPressedThisFrame ? 1 : 0),
                                           (k.downArrowKey.wasPressedThisFrame ? 1 : 0) - (k.upArrowKey.wasPressedThisFrame ? 1 : 0));
            r.slot = 0;                         // 0.42: Tasten 1–9 = Plätze der Leiste (0.33–0.41: Waffe 1–9, 0 = zehnte nach ego.json)
            for (int d = 0; d < Digits.Length; d++)
                if (k[Digits[d]].wasPressedThisFrame || k[Numpad[d]].wasPressedThisFrame) { r.slot = d + 1; break; }
            if (menuOpen != _menuWas)                                    // 0.42: Menü frei bedienbar mit Maus/Trackpad
            {
                if (menuOpen)
                {
                    _lockedBefore = Cursor.lockState == CursorLockMode.Locked;
                    Cursor.lockState = CursorLockMode.None;
                }
                else if (_lockedBefore) Cursor.lockState = CursorLockMode.Locked;
                _menuWas = menuOpen;
            }
            if (menuOpen)
            {
                Cursor.visible = true;
                var p = m.position.ReadValue();
                r.menu.pointer = new Vector2(p.x, Screen.height - p.y);  // GUI-Pixel, Ursprung oben links
                r.menu.moved = (r.menu.pointer - _lastPointer).sqrMagnitude > 0.25f;
                _lastPointer = r.menu.pointer;
                r.menu.down = m.leftButton.wasPressedThisFrame;
                r.menu.up = m.leftButton.wasReleasedThisFrame;
                r.move = new Vector2((k.dKey.isPressed ? 1 : 0) - (k.aKey.isPressed ? 1 : 0), (k.wKey.isPressed ? 1 : 0) - (k.sKey.isPressed ? 1 : 0));
                if (r.move.sqrMagnitude > 1) r.move.Normalize();
                return r;                       // kein Blick, kein Feuer; Laufen bleibt
            }
            if (k.escapeKey.wasPressedThisFrame && !menuOpen) Cursor.lockState = CursorLockMode.None;
            if (m.leftButton.wasPressedThisFrame && Cursor.lockState != CursorLockMode.Locked)
            {
                Cursor.lockState = CursorLockMode.Locked;
                return r;            // erster Klick fängt nur den Mauszeiger
            }
            Cursor.visible = Cursor.lockState != CursorLockMode.Locked;
            bool locked = Cursor.lockState == CursorLockMode.Locked || Application.isEditor;
            if (locked)
            {
                var d = m.delta.ReadValue() * (sensitivity / Mathf.Max(1f, zoom));
                r.lookDeg = new Vector2(d.x, invertY ? -d.y : d.y);
                r.fire = m.leftButton.isPressed;
                r.aim = m.rightButton.isPressed;
            }
            r.move = new Vector2((k.dKey.isPressed ? 1 : 0) - (k.aKey.isPressed ? 1 : 0), (k.wKey.isPressed ? 1 : 0) - (k.sKey.isPressed ? 1 : 0));
            if (r.move.sqrMagnitude > 1) r.move.Normalize();
            r.sprint = k.leftShiftKey.isPressed || k.rightShiftKey.isPressed;
            r.crouch = k.leftCtrlKey.isPressed || k.rightCtrlKey.isPressed || k.cKey.isPressed;
            r.jump = k.spaceKey.wasPressedThisFrame;
            r.reload = k.rKey.wasPressedThisFrame;
            r.inspect = k.fKey.wasPressedThisFrame;
            r.select = 0;                       // 0.18: bis 0.17 1/2 Ziehen/Wegstecken; 0.20: 3 Scout; 0.22: 4/5; 0.33: Tasten 1–9, 0 nach ego.json; 0.42: r.slot
            r.swap = k.qKey.wasPressedThisFrame;
            return r;
        }

        static readonly Key[] Digits =
        {
            Key.Digit1, Key.Digit2, Key.Digit3,
            Key.Digit4, Key.Digit5, Key.Digit6,
            Key.Digit7, Key.Digit8, Key.Digit9,   // 0.42: Leiste 1–9 (0 ist frei; bis 0.41 zehnte Waffe)
        };
        static readonly Key[] Numpad =
        {
            Key.Numpad1, Key.Numpad2, Key.Numpad3, Key.Numpad4, Key.Numpad5, Key.Numpad6, Key.Numpad7, Key.Numpad8, Key.Numpad9,
        };
    }

    /// <summary>Zeitplan aus Abschnitten (Sekunden): gehaltene Tasten, einmalige Tasten, Blickbewegung je Sekunde.</summary>
    public sealed class ScriptedInput : IEgoInput
    {
        public sealed class Step
        {
            public float t0, t1;
            public string[] hold;          // z. B. {"aim", "fire"}
            public string[] press;         // einmalig bei t0
            public Vector2 move, lookPerS;
        }

        public readonly List<Step> steps = new List<Step>();
        public float time;
        public float Duration { get { float d = 0; foreach (var s in steps) d = Mathf.Max(d, s.t1); return d; } }

        public ScriptedInput Add(float t0, float t1, string hold = "", string press = "", Vector2 move = default, Vector2 lookPerS = default)
        {
            steps.Add(new Step { t0 = t0, t1 = t1, hold = hold.Split(' '), press = press.Split(' '), move = move, lookPerS = lookPerS });
            return this;
        }

        public RawInput Read(float dt, float zoom)
        {
            float t0 = time, t1 = time + dt;
            time = t1;
            var r = new RawInput();
            foreach (var s in steps)
            {
                if (s.t0 <= t0 && t0 < s.t1)
                {
                    r.move += s.move;
                    r.lookDeg += s.lookPerS * dt;
                    foreach (var h in s.hold) Set(ref r, h);
                }
                if (t0 <= s.t0 && s.t0 < t1)
                    foreach (var p in s.press) Set(ref r, p);
            }
            return r;
        }

        /// <summary>Zahl aus den Ziffern ab Stelle i (0.37: ohne Substring – kein Speicher je Taste), −1 ohne Ziffern.</summary>
        static int Digits(string s, int i)
        {
            int n = 0;
            if (i >= s.Length) return -1;
            for (; i < s.Length; i++)
            {
                if (s[i] < '0' || s[i] > '9') return -1;
                n = n * 10 + (s[i] - '0');
            }
            return n;
        }

        static void Set(ref RawInput r, string k)
        {
            switch (k)
            {
                case "sprint": r.sprint = true; break;
                case "crouch": r.crouch = true; break;
                case "jump": r.jump = true; break;
                case "fire": r.fire = true; break;
                case "aim": r.aim = true; break;
                case "reload": r.reload = true; break;
                case "inspect": r.inspect = true; break;
                case "draw": r.draw = true; break;
                case "holster": r.holster = true; break;
                case "swap": r.swap = true; break;
                case "weapon1": r.select = 1; break;
                case "weapon2": r.select = 2; break;
                case "weapon3": r.select = 3; break;
                case "weapon4": r.select = 4; break;
                case "weapon5": r.select = 5; break;
                case var w when w.StartsWith("weapon", System.StringComparison.Ordinal) && Digits(w, 6) > 0: r.select = Digits(w, 6); break;   // 0.34: alle Waffen
                case var w when w.StartsWith("slot", System.StringComparison.Ordinal) && Digits(w, 4) > 0: r.slot = Digits(w, 4); break;       // 0.42: Taste der Leiste
                case "menu": r.menu.toggle = true; break;          // 0.33 Ziel 2: Waffenmenü (Aufnahme, Tests)
                case "menu_next": r.menu.wheel = 1; break;
                case "menu_prev": r.menu.wheel = -1; break;
                case "menu_down": r.menu.arrows.y = 1; break;
                case "menu_up": r.menu.arrows.y = -1; break;
                case "menu_right": r.menu.arrows.x = 1; break;
                case "menu_left": r.menu.arrows.x = -1; break;
                case "menu_ok": r.menu.confirm = true; break;
                case "menu_esc": r.menu.cancel = true; break;
            }
        }
    }
}
