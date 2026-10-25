// Vorführlauf durch den Parcours (MP4, Tests): läuft `course.route` ab, springt vor niedrigen Hindernissen, duckt unter
// Balken und schießt auf Scheiben in Sichtweite. Entworfen für den Beleg, kein Spielerersatz.
using System.Collections.Generic;
using UnityEngine;

namespace Ballon.Ego
{
    public sealed class RouteRunner : IEgoInput
    {
        public float reach = 0.7f;            // Wegpunkt erreicht (waagrechter Abstand, m)
        public float turnDegPerS = 240f;      // Drehrate beim Laufen
        public float aimDegPerS = 160f;       // Drehrate beim Anvisieren
        public float shootRange = 20f;        // Scheiben bis zu dieser Entfernung werden beschossen
        public float shootCone = 55f;         // nur Scheiben in diesem Winkel zur Laufrichtung
        public float maxTime = 120f;

        readonly EgoPlayer _p;
        readonly List<Vector3> _route;
        readonly IList<RangeTarget> _targets;
        int _i;
        float _t, _stuckT, _jumpCool, _aimT;
        Vector3 _lastPos;
        RangeTarget _aim;

        public int Waypoint => _i;
        public bool Done => _i >= _route.Count || _t > maxTime;

        public RouteRunner(EgoPlayer p, List<Vector3> route, IList<RangeTarget> targets)
        {
            _p = p;
            _route = route;
            _targets = targets;
            _lastPos = p.transform.position;
        }

        public RawInput Read(float dt, float zoom)
        {
            var r = new RawInput();
            _t += dt;
            _jumpCool -= dt;
            if (Done) return r;
            var tr = _p.transform;
            var pos = tr.position;
            var to = _route[_i] - pos;
            to.y = 0;
            while (to.magnitude < reach && ++_i < _route.Count) { to = _route[_i] - pos; to.y = 0; }
            if (Done) return r;

            float yaw = tr.eulerAngles.y;
            float wantYaw = Mathf.Atan2(to.x, to.z) * Mathf.Rad2Deg;
            float wantPitch = 4f;                                    // leicht nach unten, wie ein Läufer
            var cam = _p.worldCam.transform;
            _aim = PickTarget(cam.position, to);
            if (_aim != null)
            {
                var d = _aim.transform.position - cam.position;
                wantYaw = Mathf.Atan2(d.x, d.z) * Mathf.Rad2Deg;
                wantPitch = -Mathf.Atan2(d.y, new Vector2(d.x, d.z).magnitude) * Mathf.Rad2Deg;
                float err = Vector3.Angle(cam.forward, d);
                r.aim = true;
                _aimT += dt;
                r.fire = err < 1.2f && _aimT > 0.25f;
            }
            else _aimT = 0;
            float rate = (_aim != null ? aimDegPerS : turnDegPerS) * dt;
            float pitch = _p.head.localEulerAngles.x;
            if (pitch > 180) pitch -= 360;
            r.lookDeg = new Vector2(Mathf.Clamp(Mathf.DeltaAngle(yaw, wantYaw), -rate, rate),
                                    -Mathf.Clamp(wantPitch - pitch, -rate, rate));

            // vorwärts relativ zur Blickrichtung in die Richtung des Wegpunkts
            var local = Quaternion.Euler(0, -yaw, 0) * to.normalized;
            r.move = new Vector2(local.x, local.z);
            r.sprint = _aim == null && Mathf.Abs(Mathf.DeltaAngle(yaw, wantYaw)) < 10f && to.magnitude > 6f;
            if (_p.C.ammo == 0) r.reload = true;

            var fwd = to.normalized;
            int mask = ~(1 << EgoPlayer.PlayerLayer);
            bool low = Physics.Raycast(pos + Vector3.up * 0.45f, fwd, 0.9f, mask, QueryTriggerInteraction.Ignore);
            bool knee = Physics.Raycast(pos + Vector3.up * 0.9f, fwd, 1.0f, mask, QueryTriggerInteraction.Ignore);
            bool head = Physics.Raycast(pos + Vector3.up * 1.5f, fwd, 1.4f, mask, QueryTriggerInteraction.Ignore);
            bool roof = Physics.Raycast(pos + Vector3.up * 0.6f, Vector3.up, 1.15f, mask, QueryTriggerInteraction.Ignore);
            r.crouch = (head && !knee) || roof;                       // Balken in Kopfhöhe oder schon darunter
            if (low && !r.crouch && _jumpCool <= 0) { r.jump = true; _jumpCool = 0.5f; }
            // feststecken: nach 1,2 s ohne Fortschritt springen
            if ((pos - _lastPos).magnitude > 0.5f) { _lastPos = pos; _stuckT = 0; }
            else if ((_stuckT += dt) > 1.2f && _jumpCool <= 0) { r.jump = true; _jumpCool = 0.6f; _stuckT = 0; }
            return r;
        }

        RangeTarget PickTarget(Vector3 eye, Vector3 runDir)
        {
            if (_targets == null) return null;
            if (_aim != null && _aim.hits == 0 && Visible(eye, _aim) && _aimT < 2.5f) return _aim;   // dranbleiben, höchstens 2,5 s
            RangeTarget best = null;
            float bestD = shootRange;
            foreach (var t in _targets)
            {
                if (t.hits > 0 || t == _aim) continue;
                var d = t.transform.position - eye;
                if (d.magnitude > bestD || Vector3.Angle(new Vector3(d.x, 0, d.z), runDir) > shootCone) continue;
                if (Vector3.Dot(t.FaceNormal, -d) <= 0 || !Visible(eye, t)) continue;   // Ringseite zum Läufer, freie Sicht
                best = t;
                bestD = d.magnitude;
            }
            if (best != _aim) _aimT = 0;
            return best;
        }

        static bool Visible(Vector3 eye, RangeTarget t)
        {
            var d = t.transform.position - eye;
            return !Physics.Raycast(eye, d.normalized, out var h, d.magnitude, ~(1 << EgoPlayer.PlayerLayer), QueryTriggerInteraction.Ignore)
                   || h.collider.GetComponentInParent<RangeTarget>() == t;
        }
    }
}
