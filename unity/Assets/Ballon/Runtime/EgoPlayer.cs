// Spielfigur: Bewegung (CharacterController), Blick, zwei Kameras (Welt mit Zoom, Viewmodel mit festen 75° horizontal),
// Treffer per Strahl, Hüft-Fadenkreuz (HipReticle), Rückmeldung im Zielen und Munitionszähler. Die Ego-Bewegung selbst kommt aus EgoController.
using System;
using System.Collections.Generic;
using System.Linq;
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
        public float wallCheck = 0.75f;
        // Weltzoom (gameplay.world_zoom), Streuung und Hochziehen des Blicks (Grundbahn) kommen seit 0.15 aus ego.json (ego.RECOIL)
    }

    /// <summary>Rückmeldung nach Visier-Standard 3 §6 (`reticles.ADS_FEEDBACK`, Entscheidungsliste Frage 4.3 A): Schuss-Ring im Zielen
    /// für ein Bild, Treffer-X mindestens 0,17 s, in Familienfarbe Orange (`kit.MATERIALS['accent']`) statt Destiny-Rot. Größen als
    /// Anteil der Bildhöhe (Durchmesser bzw. Breite). Der HUD-Punkt wartet auf Motiongen (Widerspruch 3).</summary>
    public static class AdsFeedback
    {
        public const float ShotRingShareH = 0.02f, HitXShareH = 0.045f, HitXMinS = 0.17f;
        public const int ShotRingFrames = 1;
        public static readonly Color Orange = new Color32(0xE0, 0x65, 0x1E, 0xFF);

        static Texture2D _ring, _x;
        public static Texture2D Ring => _ring ? _ring : (_ring = Make((u, v) => Mathf.Abs(Mathf.Sqrt(u * u + v * v) - 0.9f) - 0.09f));
        // vier Striche auf den Diagonalen mit freier Mitte (wie Destiny)
        public static Texture2D X => _x ? _x : (_x = Make((u, v) =>
        {
            float au = Mathf.Abs(u), av = Mathf.Abs(v), along = (au + av) * 0.5f;
            return Mathf.Max(Mathf.Abs(au - av) * 0.7071f - 0.06f, Mathf.Max(0.35f - along, along - 0.97f));
        }));

        /// <summary>Marke in ein ausgelesenes Bild stempeln (Aufnahme: das OnGUI-HUD liegt nicht in der Render-Textur); c in sRGB.</summary>
        public static void Stamp(Texture2D dst, Texture2D mask, float size, Color c) => Stamp(dst, mask, size, c, dst.width / 2f, dst.height / 2f);

        /// <summary>Wie Stamp, Mitte der Marke bei (cx, cy) in Bildpixeln (Ursprung unten links wie die Textur).</summary>
        public static void Stamp(Texture2D dst, Texture2D mask, float size, Color c, float cx, float cy)
        {
            int w = dst.width, h = dst.height, x0 = Mathf.FloorToInt(cx - size / 2), y0 = Mathf.FloorToInt(cy - size / 2);
            for (int y = Mathf.Max(0, y0); y <= Mathf.Min(h - 1, y0 + size + 1); y++)
                for (int x = Mathf.Max(0, x0); x <= Mathf.Min(w - 1, x0 + size + 1); x++)
                {
                    float a = mask.GetPixelBilinear((x + 0.5f - (cx - size / 2)) / size, (y + 0.5f - (cy - size / 2)) / size).a;
                    if (a > 0) dst.SetPixel(x, y, Color.Lerp(dst.GetPixel(x, y), c, a));
                }
        }

        /// <summary>Weiße Maske 128 px aus einem Abstandsfeld (≤ 0 innen), Kanten über ein Texel geglättet; einmal je Lauf gebaut.</summary>
        static Texture2D Make(Func<float, float, float> sdf)
        {
            const int n = 128;
            var t = new Texture2D(n, n, TextureFormat.RGBA32, false) { filterMode = FilterMode.Bilinear, wrapMode = TextureWrapMode.Clamp };
            var px = new Color32[n * n];
            for (int y = 0; y < n; y++)
                for (int x = 0; x < n; x++)
                {
                    float d = sdf((x + 0.5f) / n * 2 - 1, (y + 0.5f) / n * 2 - 1);
                    px[y * n + x] = new Color32(255, 255, 255, (byte)(255 * Mathf.Clamp01(0.5f - d * n / 2)));
                }
            t.SetPixels32(px);
            t.Apply(false);                        // lesbar lassen: die Aufnahme stempelt per GetPixelBilinear
            return t;
        }
    }

    public sealed class EgoPlayer : MonoBehaviour
    {
        public const int PlayerLayer = 2;           // eingebaute Ebene „Ignore Raycast“

        /// <summary>Eine Waffe der Spielfigur (0.18): Modell mit Armen, Hüft-Fadenkreuz und Skins; der Controller liegt im Arsenal.</summary>
        public sealed class Loadout
        {
            public EgoRig rig;
            public HipReticle hip;
            public HipReticle sight;            // 0.20: gezeichnetes Absehen im Visier = Form des Hüft-Fadenkreuzes (ohne Aufgehen)
            public Color sightColor;            // Farbe der Absehen-Rolle des Modells (Cyan)
            public Material[] skins;
            public string[] skinNames;
            public int skin;
        }

        public EgoArsenal arsenal;                  // Waffen (Tasten 1/2/3, Q), je Waffe ein Controller
        public Loadout[] loadouts;
        public EgoController C => arsenal.Current;  // aktive Waffe
        public EgoRig rig => loadouts[arsenal.Active].rig;
        public Loadout Current => loadouts[arsenal.Active];
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
        public HipReticle hipReticle => Current.hip;   // Hüft-Fadenkreuz der aktiven Waffe (Entscheidungsliste 4.1 A / 4.2 A)

        CharacterController _cc;
        GUIStyle _big, _small, _time;
        float _yaw, _pitch, _vy, _eye, _landDip, _landV, _hitX, _airT;
        int _ringFrames;
        Vector3 _vel;
        bool _grounded = true, _wasGrounded = true;
        System.Random _rng = new System.Random(7);
        readonly Queue<GameObject> _decals = new Queue<GameObject>();
        public Material decalMat;
        public Material[] skins { get => Current.skins; set => Current.skins = value; }          // Skins der aktiven Waffe
        public string[] skinNames { get => Current.skinNames; set => Current.skinNames = value; }
        public int skin => Current.skin;

        /// <summary>Waffen-Skin i (0 = Standard) der aktiven Waffe setzen.</summary>
        public void SetSkin(int i)
        {
            var L = Current;
            if (L.skins == null || L.skins.Length == 0) return;
            L.skin = ((i % L.skins.Length) + L.skins.Length) % L.skins.Length;
            L.rig.SetSkin(L.skins[L.skin]);
            _hHits = -1;                     // Anzeige neu bauen
        }
        public RangeTargets range;
        public CourseRun course;         // Parcours der gezeigten Szene (null: keiner); Step prüft die Tore, die Anzeige zeigt den Lauf
        public string sceneLabel;        // null = keine Szenen vorhanden, dann nennt die Anzeige keine
        public string lightLabel;        // gezeigte Lichtszene (null im Parcours)
        int _lightCount;
        const string HelpA = "Maus umsehen · WASD · Shift Sprint · Strg/C Ducken · Leertaste Springen · LMT Feuer · RMT Zielen · R Nachladen · " +
                             "F Betrachten · 1/2/3 Waffe (Q wechseln) · K Skin · ";
        const string HelpB = "Esc Maus frei · H Anzeige";
        string _help = HelpA + HelpB;

        /// <summary>Szene (Name für die Anzeige), ihre Zielscheiben und ihren Parcours setzen; die Anzeige baut ihren Text neu.</summary>
        public void SetScene(string label, RangeTargets targets, CourseRun courseRun = null)
        {
            sceneLabel = label;
            lightLabel = null;
            _lightCount = 0;
            _help = HelpA + "L Szene · T Start · " + HelpB;
            range = targets;
            course = courseRun;
            _hHits = -1;
        }

        /// <summary>Lichtszene für die Anzeige (Name, Anzahl der Lichtszenen der Szene).</summary>
        public void SetLighting(string label, int count)
        {
            lightLabel = label;
            _lightCount = count;
            _help = HelpA + (count > 1 ? "L Szene · N Licht · T Start · " : "L Szene · T Start · ") + HelpB;
            _hHits = -1;
        }

        public static EgoPlayer Create(EgoSolver S, GameObject weaponModel, GameObject armsModel, IDictionary<string, Material> roles,
                                       int vmLayer, Vector3 at, float yaw) =>
            Create(new[] { S }, new[] { weaponModel }, armsModel, roles, vmLayer, at, yaw);

        /// <summary>Spielfigur mit mehreren Waffen (0.18): je Waffe Solver, Modell (eigene Arme), Controller und Hüft-Fadenkreuz; Waffe 1 aktiv.</summary>
        public static EgoPlayer Create(EgoSolver[] Ss, GameObject[] weaponModels, GameObject armsModel, IDictionary<string, Material> roles,
                                       int vmLayer, Vector3 at, float yaw)
        {
            var S = Ss[0];
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
            var cs = new EgoController[Ss.Length];
            p.loadouts = new Loadout[Ss.Length];
            for (int k = 0; k < Ss.Length; k++)
            {
                var sp = new GameObject("Weapon_" + Ss[k].D.weapon.id).transform;      // eigener Raum je Waffe: nur die aktive ist sichtbar
                sp.SetParent(vmSpace, false);
                cs[k] = new EgoController(Ss[k]);
                cs[k].Marker += (a, m) => { p.lastMarker = $"{a} › {m}"; p.lastMarkerTime = Time.time; p.log.Add($"{Time.frameCount} {a} {m}"); };
                cs[k].Shot += p.OnShot;
                var rig = new EgoRig(Ss[k], sp, weaponModels[k], armsModel, roles, vmLayer);
                p.loadouts[k] = new Loadout { rig = rig, hip = new HipReticle(Ss[k].D.gameplay.hip) };
                if (rig.ReticleRole != "" && Ss[k].D.weapon.anchors.Any(a => a.id == "Socket_Reticle"))
                {
                    p.loadouts[k].sight = new HipReticle(Ss[k].D.gameplay.hip);
                    ColorUtility.TryParseHtmlString(Ss[k].D.Role(rig.ReticleRole).color, out p.loadouts[k].sightColor);
                }
                sp.gameObject.SetActive(k == 0);
            }
            p.arsenal = new EgoArsenal(cs);
            p.arsenal.Switched += (from, to) =>                 // neue Waffe zieht: Modell umschalten (kein Speicher)
            {
                p.loadouts[from].rig.space.gameObject.SetActive(false);
                p.loadouts[to].rig.space.gameObject.SetActive(true);
            };
            return p;
        }

        /// <summary>Waffe k (0-basiert) sofort aktiv, ohne Wechselablauf (Aufnahme, Vergleich): Modell umschalten, Anzeige neu.</summary>
        public void UseWeapon(int k)
        {
            arsenal.Select(k);
            _hHits = -1;
        }

        void OnDestroy()
        {
            if (loadouts != null) foreach (var L in loadouts) { L.hip?.Release(); L.sight?.Release(); }
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

        float Zoom => C.Zoom;                       // Weltzoom der Klasse (1.2 A), folgt dem Modell (1d)

        void Update()
        {
            float dt = deltaOverride?.Invoke() ?? Mathf.Min(Time.deltaTime, 0.05f);
            Step(dt);
        }

        /// <summary>Schuss-Ring im nächsten gezeichneten Bild sichtbar (nur im Zielen, ein Bild je Schuss).</summary>
        public bool ShotRingVisible => _ringFrames > 0;
        /// <summary>Treffer-X sichtbar (mindestens AdsFeedback.HitXMinS nach dem letzten Treffer).</summary>
        public bool HitXVisible => _hitX > 0;
        /// <summary>Hüft-Fadenkreuz im nächsten gezeichneten Bild sichtbar (nur in der Hüfte; im Sprint der Automatik nur „^“).</summary>
        public bool HipVisible => hipReticle != null && hipReticle.Visible;

        /// <summary>Gezeichnetes Absehen (0.20, Nutzer 26.10.2026: „lieber etwas Gezeichnetes … im Bestfall das Fadenkreuz vom Hüftfeuer im
        /// Visier“): die Hüftform der Klasse ohne Aufgehen in der Farbe des Modell-Absehens, sobald das Visier angekommen ist (Zielen-Anteil
        /// über SightFrom; beim Zielfernrohr erst im Linsenbild), an der Bildlage von Socket_Reticle.</summary>
        public bool SightVisible => Current.sight != null && !C.Busy && C.adsWeight >= SightFrom && (rig.AdsHideCount == 0 || rig.AdsHidden);
        public const float SightFrom = 0.9f;

        /// <summary>Bildlage des Absehens (Pixel, Ursprung unten links) in der Viewmodel-Kamera.</summary>
        public Vector2 SightScreen()
        {
            var s = viewCam.WorldToScreenPoint(rig.AnchorWorld("Socket_Reticle"));
            return new Vector2(s.x, s.y);
        }

        /// <summary>Hüft-Fadenkreuz, Schuss-Ring und Treffer-X wie in OnGUI in ein Aufnahmebild zeichnen.</summary>
        public void StampFeedback(Texture2D tex)
        {
            if (HipVisible)
            {
                var m = hipReticle.Mask(tex.height);
                AdsFeedback.Stamp(tex, m, m.width, hipReticle.Color);
            }
            if (SightVisible)
            {
                var m = Current.sight.Mask(tex.height);
                var s = SightScreen() * (tex.height / (float)viewCam.pixelHeight);
                AdsFeedback.Stamp(tex, m, m.width, Current.sightColor, s.x, s.y);
            }
            if (ShotRingVisible) AdsFeedback.Stamp(tex, AdsFeedback.Ring, AdsFeedback.ShotRingShareH * tex.height, Color.white);
            if (HitXVisible) AdsFeedback.Stamp(tex, AdsFeedback.X, AdsFeedback.HitXShareH * tex.height, AdsFeedback.Orange);
            tex.Apply(false);
        }

        public void Step(float dt)
        {
            if (_ringFrames > 0) _ringFrames--;           // vor dem Feuern: ein neuer Schuss setzt den Ring für dieses Bild
            _hitX = Mathf.Max(0, _hitX - dt);
            var r = input.Read(dt, Zoom);
            Look(r);
            Move(r, dt);
            var it = new EgoIntent
            {
                fire = r.fire, aim = r.aim, sprint = r.sprint, crouch = r.crouch, grounded = _airT < 0.12f,   // kurze Luftphasen (Stufen) zählen nicht
                reload = r.reload, inspect = r.inspect, draw = r.draw, holster = r.holster, swap = r.swap,
                speed01 = new Vector2(_vel.x, _vel.z).magnitude / move.walk, look = r.lookDeg, move = r.move,
                nearWall = NearWall(),
            };
            hipReticle?.Decay(dt, it.speed01);            // vor den Schüssen dieses Bilds, wie reticles.simulate
            C.aspect = worldCam.aspect > 0 ? worldCam.aspect : 16f / 9f;   // Grundbahn in Anteilen der Bildhöhe
            var o = arsenal.Tick(dt, it, r.select);            // Tasten 1/2: Waffe wählen (Wechsel 6.1 A über holster/draw)
            hipReticle?.See(C);
            rig.Apply(o);
            // Welt: Grundbahn und Kamera-Ruck; Viewmodel: nur der Ruck in der Hüfte (im Zielen steht das Visier, 5.1 A)
            worldCam.transform.localRotation = rig.WorldKick(o.worldPitch, o.worldYaw);
            viewCam.transform.localRotation = rig.CameraKick(o.camPitch);
            float h = C.S.D.camera.h_fov_deg;
            float aspect = worldCam.aspect > 0 ? worldCam.aspect : 16f / 9f;
            float v = Camera.HorizontalToVerticalFieldOfView(h, aspect);
            viewCam.fieldOfView = v;
            worldCam.fieldOfView = 2 * Mathf.Atan(Mathf.Tan(v * Mathf.Deg2Rad / 2) / Zoom) * Mathf.Rad2Deg;
            course?.Tick(transform.position + Vector3.up * CourseRun.BodyCenter, dt);
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
            var Rc = C.S.D.motion.recoil;                // Streuung um den Zielpunkt, getrennt von der Grundbahn (5.2 A)
            float spread = Mathf.Lerp(Rc.spread_hip_deg, Rc.spread_ads_deg, C.adsWeight);
            double a = _rng.NextDouble() * Math.PI * 2, rr = Math.Sqrt(_rng.NextDouble()) * spread;
            var dir = Quaternion.AngleAxis((float)(rr * Math.Cos(a)), worldCam.transform.up) *
                      Quaternion.AngleAxis((float)(rr * Math.Sin(a)), worldCam.transform.right) * worldCam.transform.forward;
            if (C.adsWeight > 0.5f) _ringFrames = AdsFeedback.ShotRingFrames;
            hipReticle?.Kick();
            if (Physics.Raycast(worldCam.transform.position, dir, out var hit, 300f, ~(1 << PlayerLayer | 1 << rig.weaponRoot.gameObject.layer), QueryTriggerInteraction.Ignore))
            {
                var t = hit.collider.GetComponentInParent<RangeTarget>();
                if (t != null)
                {
                    t.Hit(hit.point);
                    hits++;
                    _hitX = AdsFeedback.HitXMinS;
                }
                Decal(hit);
            }
        }

        public const float DecalSize = 0.05f;       // Einschussloch, Kantenlänge in m
        public const int DecalMax = 80;             // danach wird das älteste wiederverwendet

        void Decal(RaycastHit hit)
        {
            if (decalMat == null) return;
            GameObject d;
            if (_decals.Count >= DecalMax) d = _decals.Dequeue();
            else
            {
                d = GameObject.CreatePrimitive(PrimitiveType.Quad);
                Destroy(d.GetComponent<Collider>());
                d.GetComponent<Renderer>().sharedMaterial = decalMat;
                d.name = "Einschlag";
            }
            // Erst lösen, dann Lage und Größe in Weltmaßen setzen: ein wiederverwendetes Loch hing noch am alten Träger, localScale 0,05
            // galt in dessen Maßstab (Wand 20 m breit → Loch 1 m breit), danach behielt SetParent diese Weltgröße (Patch einschuss)
            d.transform.SetParent(null, false);
            d.transform.SetPositionAndRotation(hit.point + hit.normal * 0.004f, Quaternion.LookRotation(-hit.normal));
            d.transform.localScale = Vector3.one * DecalSize;
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
            // kein ständiges Fadenkreuz (Nutzer 25.10.2026): in der Hüfte das ausblendende Hüft-Fadenkreuz (4.1 A), im Zielen
            // gezielt über das Visier mit Schuss-Ring und Treffer-X (AdsFeedback)
            if (Event.current.type == EventType.Repaint)
            {
                if (HipVisible)
                {
                    var m = hipReticle.Mask(Screen.height);
                    var old = GUI.color;
                    GUI.color = hipReticle.Color;
                    GUI.DrawTexture(new Rect(Mathf.Round(cx) - m.width / 2, Mathf.Round(cy) - m.height / 2, m.width, m.height), m);
                    GUI.color = old;
                }
                if (SightVisible)
                {
                    var m = Current.sight.Mask(Screen.height);
                    var s = SightScreen();
                    var old = GUI.color;
                    GUI.color = Current.sightColor;
                    GUI.DrawTexture(new Rect(Mathf.Round(s.x) - m.width / 2, Mathf.Round(Screen.height - s.y) - m.height / 2, m.width, m.height), m);
                    GUI.color = old;
                }
                if (ShotRingVisible) Mark(AdsFeedback.Ring, cx, cy, AdsFeedback.ShotRingShareH * Screen.height, Color.white);
                if (HitXVisible) Mark(AdsFeedback.X, cx, cy, AdsFeedback.HitXShareH * Screen.height, AdsFeedback.Orange);
            }
            var big = _big ?? (_big = new GUIStyle(GUI.skin.label) { fontSize = 34, alignment = TextAnchor.LowerRight, fontStyle = FontStyle.Bold });
            var small = _small ?? (_small = new GUIStyle(GUI.skin.label) { fontSize = 14 });
            big.normal.textColor = C.ammo == 0 ? new Color(1f, 0.5f, 0.3f) : Color.white;
            UpdateHudText();
            GUI.Label(new Rect(Screen.width - 260, Screen.height - 80, 230, 60), _ammoText, big);
            small.normal.textColor = new Color(1, 1, 1, 0.85f);
            GUI.Label(new Rect(16, 12, 900, 22), _stateText, small);
            GUI.Label(new Rect(16, 32, 900, 22), _hitText, small);
            if (course != null)
            {
                var tm = _time ?? (_time = new GUIStyle(GUI.skin.label) { fontSize = 26, fontStyle = FontStyle.Bold });
                tm.normal.textColor = course.State == CourseRun.Phase.Ziel && course.LastValid ? new Color(0.55f, 1f, 0.6f) : Color.white;
                GUI.Label(new Rect(16, 54, 150, 34), course.TimeLabel, tm);
                GUI.Label(new Rect(170, 62, 900, 22), course.StateText, small);
                GUI.Label(new Rect(16, 90, 1200, 22), course.InfoText, small);
            }
            if (Time.time < 12f || Cursor.lockState != CursorLockMode.Locked)
                GUI.Label(new Rect(16, Screen.height - 46, 1200, 40), _help, small);
        }

        // Anzeigetexte nur bei geänderten Werten neu bauen (kein Speicher je Bild)
        string _ammoText = "", _stateText = "", _hitText = "";
        public string HudHitText => _hitText;
        int _hAmmo = -1, _hFrame = -1, _hHits = -1, _hWeapon = -1;
        string _hAction, _hMarker;

        /// <summary>Anzeigetexte aktualisieren; baut nur bei geänderten Werten neu (öffentlich für den GC-Test).</summary>
        public void UpdateHudText()
        {
            if (C.ammo != _hAmmo) { _hAmmo = C.ammo; _ammoText = $"{C.ammo} / {C.magSize}"; }
            string mk = Time.time - lastMarkerTime < 1.2f ? lastMarker : "";
            int fr = (int)C.Frame;
            if (arsenal.Active != _hWeapon) _hHits = -1;          // Waffenwechsel: Skin-Name der neuen Waffe
            if (fr != _hFrame || !ReferenceEquals(C.ActionName, _hAction) || !ReferenceEquals(mk, _hMarker) || arsenal.Active != _hWeapon)
            {
                _hFrame = fr; _hAction = C.ActionName; _hMarker = mk; _hWeapon = arsenal.Active;
                _stateText = $"{arsenal.Active + 1} {C.S.D.weapon.name} · {C.ActionName} {fr}  ·  {mk}";
            }
            if (hits != _hHits)
            {
                _hHits = hits;
                string sk = skinNames != null && skinNames.Length > 0 ? $"   Skin {skinNames[skin]} (K)" : "";
                string sz = sceneLabel != null ? $"   Szene {sceneLabel} (L)" : "";
                string lt = lightLabel != null ? (_lightCount > 1 ? $"   Licht {lightLabel} (N)" : $"   Licht {lightLabel}") : "";
                string rs = course == null && range != null ? range.Summary() : "";          // mit Parcours zählt die Lauf-Anzeige die Ziele
                _hitText = $"Treffer {hits}   {rs}{sk}{sz}{lt}";
            }
        }

        static void Mark(Texture2D tex, float cx, float cy, float size, Color c)
        {
            var old = GUI.color;
            GUI.color = c;
            GUI.DrawTexture(new Rect(cx - size / 2, cy - size / 2, size, size), tex);
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
