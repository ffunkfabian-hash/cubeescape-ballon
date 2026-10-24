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
        public bool sprint, crouch, jump, fire, aim, reload, inspect, draw, holster;
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

        public RawInput Read(float dt, float zoom)
        {
            var r = new RawInput();
            var k = Keyboard.current;
            var m = Mouse.current;
            if (k == null || m == null) return r;
            if (k.escapeKey.wasPressedThisFrame) Cursor.lockState = CursorLockMode.None;
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
            r.draw = k.digit1Key.wasPressedThisFrame;
            r.holster = k.digit2Key.wasPressedThisFrame;
            return r;
        }
    }

    /// <summary>Zeitplan aus Abschnitten (Sekunden): gehaltene Tasten, einmalige Tasten, Blickbewegung je Sekunde.</summary>
    public sealed class ScriptedInput : IEgoInput
    {
        public sealed class Step
        {
            public float t0, t1;
            public string hold = "";       // z. B. "aim fire"
            public string press = "";      // einmalig bei t0
            public Vector2 move, lookPerS;
        }

        public readonly List<Step> steps = new List<Step>();
        public float time;
        public float Duration { get { float d = 0; foreach (var s in steps) d = Mathf.Max(d, s.t1); return d; } }

        public ScriptedInput Add(float t0, float t1, string hold = "", string press = "", Vector2 move = default, Vector2 lookPerS = default)
        {
            steps.Add(new Step { t0 = t0, t1 = t1, hold = hold, press = press, move = move, lookPerS = lookPerS });
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
                    foreach (var h in s.hold.Split(' ')) Set(ref r, h);
                }
                if (t0 <= s.t0 && s.t0 < t1)
                    foreach (var p in s.press.Split(' ')) Set(ref r, p);
            }
            return r;
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
            }
        }
    }
}
