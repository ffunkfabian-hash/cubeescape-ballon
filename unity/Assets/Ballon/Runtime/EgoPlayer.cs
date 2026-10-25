// Spielfigur: Bewegung (CharacterController), Blick, zwei Kameras (Welt mit Zoom, Viewmodel mit festen 75° horizontal),
// Treffer per Strahl, Fadenkreuz und Munitionszähler. Die Ego-Bewegung selbst kommt aus EgoController.
using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace Ballon.Ego
{
    [Serializable]
    public class MoveTuning     // entworfen (Spielgefühl), nicht aus Blender
    {
        public float walk = 4.2f, sprint = 6.8f, crouch = 2.4f, aimMove = 2.8f;
        public float accelGround = 12f, accelAir = 2.5f, jumpSpeed = 5.0f, gravity = 16f;
        public float height = 1.8f, crouchHeight = 1.15f, eye = 1.62f, crouchEye = 1.0f, radius = 0.32f;
        public float adsZoom = 1.35f;                // Welt-FOV im Zielen (Viewmodel bleibt 75°)
        public float spreadHipDeg = 1.1f, spreadAdsDeg = 0.12f;
        public float climbView = 0.18f;              // bleibendes Hochziehen des Blicks je Schuss (Grad, Hüfte)
        public float wallCheck = 0.75f;
    }

    public sealed class EgoPlayer : MonoBehaviour
    {
        public const int PlayerLayer = 2;           // eingebaute Ebene „Ignore Raycast“
        public EgoController C;
        public EgoRig rig;
        public IEgoInput input = new DeviceInput();
        public MoveTuning move = new MoveTuning();
        public Camera worldCam, viewCam;
        public Transform head;
        public string lastMarker = "";
        public float lastMarkerTime;
        public int hits;
        public readonly List<string> log = new List<string>();
        public bool hud = true;
        public Func<float> deltaOverride;          // Aufnahme: feste Zeitschritte

        CharacterController _cc;
        GUIStyle _big, _small;
        float _yaw, _pitch, _vy, _eye, _landDip, _landV, _hitFlash, _airT;
        Vector3 _vel;
        bool _grounded = true, _wasGrounded = true;
        float _viewClimb;
        System.Random _rng = new System.Random(7);
        readonly Queue<GameObject> _decals = new Queue<GameObject>();
        public Material decalMat;
        public Material[] skins;
        public string[] skinNames;
        public int skin;

        /// <summary>Waffen-Skin i (0 = Standard) setzen.</summary>
        public void SetSkin(int i)
        {
            if (skins == null || skins.Length == 0) return;
            skin = ((i % skins.Length) + skins.Length) % skins.Length;
            rig.SetSkin(skins[skin]);
            _hHits = -1;                     // Anzeige neu bauen
        }
        public RangeTargets range;

        public static EgoPlayer Create(EgoSolver S, GameObject weaponModel, GameObject armsModel, IDictionary<string, Material> roles,
                                       int vmLayer, Vector3 at, float yaw)
        {
            var go = new GameObject("Player") { layer = PlayerLayer };   // Strahlen für Wandnähe und Treffer übergehen den eigenen Collider
            go.transform.SetPositionAndRotation(at, Quaternion.Euler(0, yaw, 0));
            var p = go.AddComponent<EgoPlayer>();
            p._yaw = yaw;
            p._cc = go.AddComponent<CharacterController>();
            p._cc.height = p.move.height;
            p._cc.radius = p.move.radius;
            p._cc.center = new Vector3(0, p.move.height / 2, 0);
            p._cc.stepOffset = 0.35f;
            p._cc.skinWidth = 0.03f;
            p._eye = p.move.eye;
            p.head = new GameObject("Head").transform;
            p.head.SetParent(go.transform, false);
            p.head.localPosition = new Vector3(0, p._eye, 0);
            var vmSpace = new GameObject("Viewmodel").transform;
            vmSpace.SetParent(p.head, false);
            p.worldCam = NewCam("WorldCam", p.head, ~(1 << vmLayer), 0.05f, 400f);
            p.viewCam = NewCam("ViewCam", p.head, 1 << vmLayer, S.D.camera.near_m, 6f);
            var wd = p.worldCam.GetUniversalAdditionalCameraData();
            wd.renderType = CameraRenderType.Base;
            wd.renderPostProcessing = false;
            wd.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            var vd = p.viewCam.GetUniversalAdditionalCameraData();
            vd.renderType = CameraRenderType.Overlay;
            vd.SetRenderer(Bootstrap.OutRenderer);          // letzte Kamera im Stapel: AgX-Abbildung wie Blender
            vd.renderPostProcessing = false;
            wd.cameraStack.Add(p.viewCam);
            p.worldCam.clearFlags = CameraClearFlags.SolidColor;
            p.worldCam.backgroundColor = new Color(0.62f, 0.66f, 0.70f);
            p.C = new EgoController(S);
            p.rig = new EgoRig(S, vmSpace, weaponModel, armsModel, roles, vmLayer);
            p.C.Marker += (a, m) => { p.lastMarker = $"{a} › {m}"; p.lastMarkerTime = Time.time; p.log.Add($"{Time.frameCount} {a} {m}"); };
            p.C.Shot += p.OnShot;
            return p;
        }

        static Camera NewCam(string name, Transform parent, int mask, float near, float far)
        {
            var c = new GameObject(name).AddComponent<Camera>();
            c.transform.SetParent(parent, false);
            c.cullingMask = mask;
            c.nearClipPlane = near;
            c.farClipPlane = far;
            return c;
        }

        float Zoom => Mathf.Lerp(1f, move.adsZoom, C.adsWeight);

        void Update()
        {
            float dt = deltaOverride?.Invoke() ?? Mathf.Min(Time.deltaTime, 0.05f);
            Step(dt);
        }

        public void Step(float dt)
        {
            var r = input.Read(dt, Zoom);
            Look(r);
            Move(r, dt);
            var it = new EgoIntent
            {
                fire = r.fire, aim = r.aim, sprint = r.sprint, crouch = r.crouch, grounded = _airT < 0.12f,   // kurze Luftphasen (Stufen) zählen nicht
                reload = r.reload, inspect = r.inspect, draw = r.draw, holster = r.holster,
                speed01 = new Vector2(_vel.x, _vel.z).magnitude / move.walk, look = r.lookDeg, move = r.move,
                nearWall = NearWall(),
            };
            var o = C.Tick(dt, it);
            rig.Apply(o);
            var kick = rig.CameraKick(o.camPitch);
            worldCam.transform.localRotation = kick;
            viewCam.transform.localRotation = kick;
            float h = C.S.D.camera.h_fov_deg;
            float aspect = worldCam.aspect > 0 ? worldCam.aspect : 16f / 9f;
            float v = Camera.HorizontalToVerticalFieldOfView(h, aspect);
            viewCam.fieldOfView = v;
            worldCam.fieldOfView = 2 * Mathf.Atan(Mathf.Tan(v * Mathf.Deg2Rad / 2) / Zoom) * Mathf.Rad2Deg;
            _hitFlash = Mathf.Max(0, _hitFlash - dt);
            _viewClimb *= Mathf.Exp(-dt * 3f);
        }

        void Look(RawInput r)
        {
            _yaw += r.lookDeg.x;
            _pitch = Mathf.Clamp(_pitch - r.lookDeg.y, -85f, 85f);
            transform.rotation = Quaternion.Euler(0, _yaw, 0);
            head.localRotation = Quaternion.Euler(_pitch, 0, 0);
        }

        void Move(RawInput r, float dt)
        {
            bool crouch = r.crouch && _grounded;
            float target = r.move.magnitude < 0.01f ? 0 :
                C.CurrentStance == EgoController.Stance.Sprint ? move.sprint :
                r.aim ? move.aimMove : crouch ? move.crouch : move.walk;
            var wish = transform.TransformDirection(new Vector3(r.move.x, 0, r.move.y)) * target;
            float acc = _grounded ? move.accelGround : move.accelAir;
            var hv = Vector3.Lerp(new Vector3(_vel.x, 0, _vel.z), wish, 1 - Mathf.Exp(-acc * dt));
            if (_grounded && r.jump && !C.Holstered) _vy = move.jumpSpeed;
            else if (_grounded && r.jump) _vy = move.jumpSpeed;
            _vy -= move.gravity * dt;
            _vel = new Vector3(hv.x, _vy, hv.z);
            float hgt = Mathf.Lerp(_cc.height, crouch ? move.crouchHeight : move.height, 1 - Mathf.Exp(-12 * dt));
            if (!crouch && hgt > _cc.height && Physics.SphereCast(transform.position + Vector3.up * _cc.height * 0.5f, move.radius * 0.9f,
                    Vector3.up, out _, _cc.height * 0.5f + 0.05f, ~0, QueryTriggerInteraction.Ignore))
                hgt = _cc.height;                 // unter einer Decke geduckt bleiben
            _cc.height = hgt;
            _cc.center = new Vector3(0, hgt / 2, 0);
            var flags = _cc.Move(_vel * dt);
            _wasGrounded = _grounded;
            _grounded = (flags & CollisionFlags.Below) != 0;
            float air = _airT;
            _airT = _grounded ? 0 : _airT + dt;
            if (_grounded && _vy < 0)
            {
                if (!_wasGrounded && air > 0.12f) _landV -= Mathf.Clamp(-_vy * 0.012f, 0, 0.08f);   // Landefeder des Kopfes (entworfen)
                _vy = -1f;
            }
            if ((flags & CollisionFlags.Above) != 0 && _vy > 0) _vy = 0;
            float k = 120f, z = 2 * Mathf.Sqrt(k) * 0.7f;
            _landV += (-k * _landDip - z * _landV) * dt;
            _landDip += _landV * dt;
            float eye = Mathf.Lerp(move.crouchEye, move.eye, (hgt - move.crouchHeight) / (move.height - move.crouchHeight));
            head.localPosition = new Vector3(0, eye + _landDip, 0);
        }

        public bool NearWall()
        {
            var o = head.position;
            return Physics.SphereCast(o, 0.12f, head.forward, out var hit, move.wallCheck, ~(1 << PlayerLayer | 1 << rig.weaponRoot.gameObject.layer),
                                      QueryTriggerInteraction.Ignore) && hit.collider.gameObject != gameObject;
        }

        void OnShot()
        {
            float spread = Mathf.Lerp(move.spreadHipDeg, move.spreadAdsDeg, C.adsWeight);
            double a = _rng.NextDouble() * Math.PI * 2, rr = Math.Sqrt(_rng.NextDouble()) * spread;
            var dir = Quaternion.AngleAxis((float)(rr * Math.Cos(a)), worldCam.transform.up) *
                      Quaternion.AngleAxis((float)(rr * Math.Sin(a)), worldCam.transform.right) * worldCam.transform.forward;
            float climb = move.climbView * Mathf.Lerp(1f, 0.5f, C.adsWeight);
            _pitch -= climb;           // bleibendes Hochziehen (Spieler gleicht aus)
            _viewClimb += climb;
            if (Physics.Raycast(worldCam.transform.position, dir, out var hit, 300f, ~(1 << PlayerLayer | 1 << rig.weaponRoot.gameObject.layer), QueryTriggerInteraction.Ignore))
            {
                var t = hit.collider.GetComponentInParent<RangeTarget>();
                if (t != null)
                {
                    t.Hit(hit.point);
                    hits++;
                    _hitFlash = 0.12f;
                }
                Decal(hit);
            }
        }

        void Decal(RaycastHit hit)
        {
            if (decalMat == null) return;
            GameObject d;
            if (_decals.Count >= 80) d = _decals.Dequeue();
            else
            {
                d = GameObject.CreatePrimitive(PrimitiveType.Quad);
                Destroy(d.GetComponent<Collider>());
                d.GetComponent<Renderer>().sharedMaterial = decalMat;
                d.name = "Einschlag";
            }
            d.transform.SetPositionAndRotation(hit.point + hit.normal * 0.004f, Quaternion.LookRotation(-hit.normal));
            d.transform.localScale = Vector3.one * 0.05f;
            d.transform.SetParent(hit.collider.transform, true);
            _decals.Enqueue(d);
        }

        public void Teleport(Vector3 pos, float yaw, float pitch = 0)
        {
            _cc.enabled = false;
            transform.position = pos;
            _cc.enabled = true;
            _yaw = yaw;
            _pitch = pitch;
            _vel = Vector3.zero;
            Look(new RawInput());
        }

        void OnGUI()
        {
            if (!hud) return;
            float cx = Screen.width / 2f, cy = Screen.height / 2f;
            float gap = Mathf.Lerp(10f, 3f, C.adsWeight) + Mathf.Lerp(move.spreadHipDeg, move.spreadAdsDeg, C.adsWeight) * 4f;
            var col = _hitFlash > 0 ? new Color(1f, 0.45f, 0.2f) : new Color(1, 1, 1, 0.9f);
            Rect(cx - gap - 8, cy - 1, 8, 2, col);
            Rect(cx + gap, cy - 1, 8, 2, col);
            Rect(cx - 1, cy - gap - 8, 2, 8, col);
            Rect(cx - 1, cy + gap, 2, 8, col);
            if (_hitFlash > 0)
            {
                Rect(cx - 7, cy - 7, 4, 4, col);
                Rect(cx + 3, cy - 7, 4, 4, col);
                Rect(cx - 7, cy + 3, 4, 4, col);
                Rect(cx + 3, cy + 3, 4, 4, col);
            }
            var big = _big ?? (_big = new GUIStyle(GUI.skin.label) { fontSize = 34, alignment = TextAnchor.LowerRight, fontStyle = FontStyle.Bold });
            var small = _small ?? (_small = new GUIStyle(GUI.skin.label) { fontSize = 14 });
            big.normal.textColor = C.ammo == 0 ? new Color(1f, 0.5f, 0.3f) : Color.white;
            UpdateHudText();
            GUI.Label(new Rect(Screen.width - 260, Screen.height - 80, 230, 60), _ammoText, big);
            small.normal.textColor = new Color(1, 1, 1, 0.85f);
            GUI.Label(new Rect(16, 12, 900, 22), _stateText, small);
            GUI.Label(new Rect(16, 32, 900, 22), _hitText, small);
            if (Time.time < 12f || Cursor.lockState != CursorLockMode.Locked)
                GUI.Label(new Rect(16, Screen.height - 46, 1200, 40),
                    "Maus umsehen · WASD · Shift Sprint · Strg/C Ducken · Leertaste Springen · LMT Feuer · RMT Zielen · R Nachladen · " +
                    "F Betrachten · 1/2 Ziehen/Wegstecken · K Skin · Esc Maus frei · H Anzeige", small);
        }

        // Anzeigetexte nur bei geänderten Werten neu bauen (kein Speicher je Bild)
        string _ammoText = "", _stateText = "", _hitText = "";
        int _hAmmo = -1, _hFrame = -1, _hHits = -1;
        string _hAction, _hMarker;

        void UpdateHudText()
        {
            if (C.ammo != _hAmmo) { _hAmmo = C.ammo; _ammoText = $"{C.ammo} / {C.magSize}"; }
            string mk = Time.time - lastMarkerTime < 1.2f ? lastMarker : "";
            int fr = (int)C.Frame;
            if (fr != _hFrame || !ReferenceEquals(C.ActionName, _hAction) || !ReferenceEquals(mk, _hMarker))
            {
                _hFrame = fr; _hAction = C.ActionName; _hMarker = mk;
                _stateText = $"BASIC-01 v2.1 · {C.ActionName} {fr}  ·  {mk}";
            }
            if (hits != _hHits)
            {
                _hHits = hits;
                string sk = skinNames != null && skinNames.Length > 0 ? $"   Skin {skinNames[skin]} (K)" : "";
                _hitText = $"Treffer {hits}   {(range != null ? range.Summary() : "")}{sk}";
            }
        }

        static void Rect(float x, float y, float w, float h, Color c)
        {
            var old = GUI.color;
            GUI.color = c;
            GUI.DrawTexture(new Rect(x, y, w, h), Texture2D.whiteTexture);
            GUI.color = old;
        }

        void LateUpdate()
        {
            var k = UnityEngine.InputSystem.Keyboard.current;
            if (k != null && k.hKey.wasPressedThisFrame) hud = !hud;
            if (k != null && k.kKey.wasPressedThisFrame) SetSkin(skin + 1);
        }
    }
}
