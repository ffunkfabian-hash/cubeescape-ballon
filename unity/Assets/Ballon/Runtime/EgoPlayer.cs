// Spielfigur: Bewegung (CharacterController), Blick, zwei Kameras (Welt mit eigenem Bildwinkel und Zoom, Viewmodel mit festen 75° horizontal),
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
            public Texture2D icon;              // 0.33 Ziel 2: Waffensymbol (Generated/Icons, tools/make_icons.py) für HUD und Waffenmenü
            public int skin;
        }

        public EgoArsenal arsenal;                  // Waffen (Tasten 1/2/3, Q), je Waffe ein Controller
        EgoMenu _menu;
        /// <summary>Waffenmenü über alle Waffen des Arsenals (0.33 Ziel 2).</summary>
        public EgoMenu menu => _menu ?? (_menu = new EgoMenu(arsenal.C.Length));
        public Loadout[] loadouts;
        public EgoController C => arsenal.Current;  // aktive Waffe
        public EgoRig rig => loadouts[arsenal.Active].rig;
        public Loadout Current => loadouts[arsenal.Active];
        public IEgoInput input = new DeviceInput();
        public MoveTuning move = new MoveTuning();
        public Camera worldCam, viewCam;
        /// <summary>Bildwinkel der Welt waagrecht (Spieleinstellung, -ballonFov; Vorgabe der Bezugsbildwinkel): nur die Weltkamera folgt
        /// ihm, im Zielen geteilt durch den Weltzoom der Klasse. Waffe und Arme bleiben bei ViewmodelHFovDeg (A9).</summary>
        public float worldHFovDeg;
        public const float WorldFovMinDeg = 50f, WorldFovMaxDeg = 120f;   // erlaubter Welt-Bildwinkel waagrecht (-ballonFov)
        /// <summary>A9 (A-R11, 0.32): Waffe und Arme immer mit dem Bezugsbildwinkel von Visier-Standard 3 (ego.json › camera.h_fov_deg,
        /// 75° waagrecht wie die Blender-Stills), unabhängig vom Welt-Bildwinkel und vom Weltzoom.</summary>
        public float ViewmodelHFovDeg => C.S.D.camera.h_fov_deg;
        public Transform head;
        public string lastMarker = "";
        public float lastMarkerTime;
        public int hits;
        /// <summary>Portalschüsse des Werkzeugs mit Treffermarke (Fläche in Reichweite, 0.22).</summary>
        public int portalHits;
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
        /// <summary>Wirkung der Waffen in der Welt (0.34 „Payload“): Einschläge, Projektile, Strahlen, Explosionen; Bootstrap legt sie an.</summary>
        public WeaponFx fx;
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
                             "F Betrachten · 1–0 Waffe, Tab/Mausrad Waffenmenü (Q wechseln; 5 Portalkanone: LMT Portal A, RMT Portal B) · K Skin · ";
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
            p.worldHFovDeg = S.D.camera.h_fov_deg;
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
            // eigener Tiefenbereich (A9): die Overlay-Kamera leert die Tiefe (URP-Vorgabe, clearDepth nur lesbar) und zeichnet von near_m bis
            // 6 m – eine nahe Wand schneidet Waffe und Arme nicht (PlayMode-Test Nahe_Wand_schneidet_die_Waffe_nicht)
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
                    p.loadouts[k].sight = new HipReticle(Ss[k].D.gameplay.SightHip);   // 0.33: Absehen im Glas (sight_form)
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
            if (HitXVisible) AdsFeedback.Stamp(tex, AdsFeedback.X, AdsFeedback.HitXShareH * tex.height, HitColor);
            tex.Apply(false);
        }

        public void Step(float dt)
        {
            if (_ringFrames > 0) _ringFrames--;           // vor dem Feuern: ein neuer Schuss setzt den Ring für dieses Bild
            _hitX = Mathf.Max(0, _hitX - dt);
            if (input is DeviceInput di) di.menuOpen = menu.IsOpen;
            var r = input.Read(dt, Zoom);
            bool menuWasOpen = menu.IsOpen;
            int pick = menu.Step(r.menu, arsenal.Active);       // Waffenmenü (0.33 Ziel 2): Wahl wie eine Zifferntaste
            if (pick > 0) r.select = pick;
            if (menuWasOpen || menu.IsOpen)                       // offen (und im Bild des Schließens): die Maus bedient das Menü
                EgoMenu.Filter(ref r, C.IsDrawing);
            Look(r);
            Move(r, dt);
            var it = new EgoIntent
            {
                fire = r.fire, aim = r.aim, sprint = r.sprint, crouch = r.crouch, grounded = _airT < 0.12f,   // kurze Luftphasen (Stufen) zählen nicht
                reload = r.reload, inspect = r.inspect, draw = r.draw, holster = r.holster, swap = r.swap,
                speed01 = new Vector2(_vel.x, _vel.z).magnitude / move.walk, look = r.lookDeg, move = r.move,
                nearWall = NearWall(),
            };
            // vor den Schüssen dieses Bilds, wie reticles.simulate; 0.36: Bogen ungespannt offen, schließt mit dem Auszug
            hipReticle?.Decay(dt, it.speed01, C.S.D.gameplay.Draw ? 1 - C.DrawLevel : 0);
            C.aspect = worldCam.aspect > 0 ? worldCam.aspect : 16f / 9f;   // Grundbahn in Anteilen der Bildhöhe
            var o = arsenal.Tick(dt, it, r.select);            // Tasten 1/2: Waffe wählen (Wechsel 6.1 A über holster/draw)
            hipReticle?.See(C);
            rig.Apply(o);
            // Welt: Grundbahn und Kamera-Ruck; Viewmodel: nur der Ruck in der Hüfte (im Zielen steht das Visier, 5.1 A)
            worldCam.transform.localRotation = rig.WorldKick(o.worldPitch, o.worldYaw);
            viewCam.transform.localRotation = rig.CameraKick(o.camPitch);
            float aspect = worldCam.aspect > 0 ? worldCam.aspect : 16f / 9f;
            viewCam.fieldOfView = Camera.HorizontalToVerticalFieldOfView(ViewmodelHFovDeg, aspect);
            float wv = Camera.HorizontalToVerticalFieldOfView(worldHFovDeg, aspect);
            worldCam.fieldOfView = 2 * Mathf.Atan(Mathf.Tan(wv * Mathf.Deg2Rad / 2) / Zoom) * Mathf.Rad2Deg;
            fx?.Tick(dt, arsenal.Active, BeamOn, HitMask);       // 0.34: nach Kamera und Modell (Strahl und Rauch an der Mündung dieses Bilds)
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

        /// <summary>Farbe der Treffermarke: Familienfarbe Orange, beim Werkzeug die Farbe des Portals des letzten Schusses (0.22).</summary>
        public Color HitColor { get; private set; } = AdsFeedback.Orange;

        /// <summary>Farbe eines Portals aus gameplay.portals[].color (#RRGGBB).</summary>
        public static Color PortalColor(EgoPortal p) => ColorUtility.TryParseHtmlString(p.color, out var c) ? c : AdsFeedback.Orange;

        void OnShot()
        {
            var G = C.S.D.gameplay;
            var F = G.fx;
            var Rc = C.S.D.motion.recoil;                // Streuung um den Zielpunkt, getrennt von der Grundbahn (5.2 A)
            // Werkzeug (0.22): Portale gehen ohne Streuung auf den Zielpunkt (Cube Escape: Sichtlinie zum Fadenkreuz, Q-CE-15)
            float spread = G.HasPortals ? 0 : Mathf.Lerp(Rc.spread_hip_deg, Rc.spread_ads_deg, C.adsWeight);
            double a = _rng.NextDouble() * Math.PI * 2, rr = Math.Sqrt(_rng.NextDouble()) * spread;
            var cam = worldCam.transform;
            var dir = Quaternion.AngleAxis((float)(rr * Math.Cos(a)), cam.up) *
                      Quaternion.AngleAxis((float)(rr * Math.Sin(a)), cam.right) * cam.forward;
            if (C.adsWeight > 0.5f) _ringFrames = AdsFeedback.ShotRingFrames;
            hipReticle?.Kick();
            int k = arsenal.Active;
            fx?.MuzzleShot(k, F);
            if (F.Projectile && fx != null)                 // Granate, Rakete, Pfeil (0.34): eigene Flugbahn, Treffer beim Aufschlag
            {
                fx.Launch(k, dir, F, HitMask);
                return;
            }
            float range = G.HasPortals && G.range_m > 0 ? G.range_m : 300f;
            if (F.kind == "pellets")                        // Streuschuss (0.34): Kugeln gleichmäßig im Kegel um die Schussrichtung
            {
                float cone = F.cone_deg * Mathf.Lerp(1, F.cone_ads, C.adsWeight);
                float turn = (float)(_rng.NextDouble() * 360);
                bool any = false;
                for (int i = 0; i < F.pellets; i++)             // shot_impacts 1 (0.34.1): alle Kugeln treffen, sichtbar nur die mittlere
                {
                    var d = PelletDir(dir, cam.up, cam.right, i, F.pellets, cone, turn);
                    any |= Bullet(d, range, F, k, i == 0 || !any, F.shot_impacts <= 0 || i < F.shot_impacts);
                }
                return;
            }
            Bullet(dir, range, F, k, true);
        }

        int HitMask => ~(1 << PlayerLayer | 1 << rig.weaponRoot.gameObject.layer);

        /// <summary>Richtung der Kugel i von n im Streukegel (halber Öffnungswinkel cone, Grad): eine in der Mitte, die übrigen auf zwei
        /// Ringen (0,5 und 1,0 · cone) gleichmäßig verteilt, das ganze Muster um turn gedreht (ego.PAYLOAD shotgun).</summary>
        public static Vector3 PelletDir(Vector3 dir, Vector3 up, Vector3 right, int i, int n, float cone, float turn)
        {
            if (i == 0 || n <= 1) return dir;
            int inner = Mathf.Max(1, (n - 1) / 3), outer = n - 1 - inner;
            bool inRing = i <= inner;
            int j = inRing ? i - 1 : i - 1 - inner, m = inRing ? inner : outer;
            float ang = turn + 360f * j / m + (inRing ? 0 : 180f / m), rad = cone * (inRing ? 0.5f : 1f);
            return Quaternion.AngleAxis(rad * Mathf.Cos(ang * Mathf.Deg2Rad), up) * Quaternion.AngleAxis(rad * Mathf.Sin(ang * Mathf.Deg2Rad), right) * dir;
        }

        /// <summary>Ein Strahl ohne Flugzeit (Kugel, Schrotkugel, Strahl, Bolzen): Treffer an der Scheibe, Einschlag, je Klasse der Strahl
        /// oder Bolzen dazu. count = Treffer zählen (Schrot: einmal je Schuss); visible = Einschlag zeigen (Schrot 0.34.1: nur die mittlere
        /// Kugel). true, wenn eine Scheibe getroffen wurde.</summary>
        bool Bullet(Vector3 dir, float range, EgoFx F, int k, bool count, bool visible = true)
        {
            var G = C.S.D.gameplay;
            var cam = worldCam.transform;
            bool hitSome = Physics.Raycast(cam.position, dir, out var hit, range, HitMask, QueryTriggerInteraction.Ignore);
            var end = hitSome ? hit.point : cam.position + dir * range;
            var nrm = hitSome ? hit.normal : -dir;
            var energy = fx != null ? fx.Energy(k) : Color.cyan;
            if (fx != null)
            {
                var muzzle = fx.MuzzleWorld(k);
                if (F.kind == "beam") fx.BeamShot(end, nrm, hitSome);
                else if (F.kind == "rail") fx.Rail(muzzle, end, F, energy);
                else if (F.kind == "bolts")
                {
                    fx.Streak(muzzle, end, nrm, F.speed_mps, F.length_m, F.width_m, energy, hitSome ? C.S.D.Impact(F.impact) : null,
                              hitSome ? hit.collider.transform : null, false);
                }
                else if (F.tracer_every > 0 && C.shots % F.tracer_every == 0)   // Leuchtspur jeder n-te Schuss
                    fx.Streak(muzzle, end, nrm, F.tracer_mps, F.tracer_m, F.tracer_w_m, fx.Tracer(k), null, null, true);
            }
            if (!hitSome) return false;
            if (G.HasPortals && C.LastPortal >= 0)
            {
                // Werkzeug: Treffermarke in Portalfarbe auf jeder Fläche in Reichweite (die Portale selbst sind nicht Teil von 0.22)
                HitColor = PortalColor(G.portals[C.LastPortal]);
                _hitX = AdsFeedback.HitXMinS;
                portalHits++;
                return false;
            }
            HitColor = AdsFeedback.Orange;
            var t = hit.collider.GetComponentInParent<RangeTarget>();
            if (t != null)
            {
                t.Hit(hit.point);
                if (count) hits++;
                _hitX = AdsFeedback.HitXMinS;
            }
            if (fx != null && visible && F.kind != "bolts" && F.kind != "none")     // Bolzen schlagen erst bei der Ankunft ein (WeaponFx)
            {
                var I = C.S.D.Impact(F.impact);
                if (F.kind == "beam" && F.scorch_every > 1 && C.shots % F.scorch_every != 0)                 // Dauerstrahl: Brand je n. Schuss
                    fx.Impact(I, hit.point, hit.normal, dir, energy, true, null);
                else fx.Impact(I, hit.point, hit.normal, dir, energy, I != null && I.decal == "scorch", hit.collider.transform);
            }
            return t != null;
        }

        /// <summary>Dauerstrahl läuft (Spurgewehr, 0.34): Abzug gezogen und der letzte Schuss liegt weniger als gameplay.fx.beam_s zurück.</summary>
        public bool BeamOn => C.S.D.gameplay.Beam && C.TriggerHeld && C.SinceShot < C.S.D.gameplay.fx.beam_s && C.shots > 0;

        /// <summary>Treffer eines Projektils oder einer Explosion an einer Scheibe (WeaponFx): zählt wie ein Treffer mit Treffer-X.</summary>
        public void ProjectileHit()
        {
            hits++;
            HitColor = AdsFeedback.Orange;
            _hitX = AdsFeedback.HitXMinS;
        }

        /// <summary>Kantenlänge des Einschusslochs in m und Größe des Pools (motion.payload.decal, WeaponFx setzt sie beim Start).</summary>
        public static float DecalSize = 0.05f;
        public static int DecalMax = 96;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        static void ResetStatics() { DecalSize = 0.05f; DecalMax = 96; }   // ohne Domain-Reload (Richter 0.34)

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
                if (HitXVisible) Mark(AdsFeedback.X, cx, cy, AdsFeedback.HitXShareH * Screen.height, HitColor);
            }
            var big = _big ?? (_big = new GUIStyle(GUI.skin.label) { fontSize = 34, alignment = TextAnchor.LowerRight, fontStyle = FontStyle.Bold });
            var small = _small ?? (_small = new GUIStyle(GUI.skin.label) { fontSize = 14 });
            big.normal.textColor = C.ammo == 0 && !C.S.D.gameplay.Unlimited ? new Color(1f, 0.5f, 0.3f) : Color.white;
            UpdateHudText();
            WeaponHud(big);
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
            if (menu.IsOpen) MenuGui();
        }

        // -------------------------------------------------------------- HUD und Waffenmenü (0.33 „Armory“, Ziel 2)
        // Maße als Anteil der Bildhöhe (gleich bei jeder Auflösung, Sichtprüfung 1470 × 956); beschriftet mit der Waffenklasse (Spec type_de). Texte und Stile werden einmal gebaut (kein
        // Speicher je Bild); die Symbole sind weiß und werden über GUI.color eingefärbt.
        public const float HudIconH = 0.055f, HudIconMaxW = 0.17f, MenuCellW = 0.25f, MenuCellH = 0.13f;
        static readonly Color HudWhite = new Color(1, 1, 1, 0.92f), MenuPanel = new Color(0.03f, 0.05f, 0.07f, 0.78f),
                              MenuCell = new Color(1, 1, 1, 0.06f), MenuSel = new Color(0.37f, 0.83f, 0.88f, 0.30f),
                              MenuEdge = new Color(0.37f, 0.83f, 0.88f, 0.95f), MenuDim = new Color(1, 1, 1, 0.55f);
        GUIStyle _name, _menuName, _menuKey, _menuTitle;
        string[] _menuLabels, _menuKeys;
        int _fontH = -1;

        void Styles()
        {
            int h = Screen.height;
            if (_fontH == h && _name != null) return;
            _fontH = h;
            _name = new GUIStyle(GUI.skin.label) { fontSize = Mathf.RoundToInt(0.018f * h), alignment = TextAnchor.LowerRight };
            _name.normal.textColor = MenuDim;
            _menuName = new GUIStyle(GUI.skin.label) { fontSize = Mathf.RoundToInt(0.017f * h), alignment = TextAnchor.LowerCenter, wordWrap = false };
            _menuName.normal.textColor = Color.white;
            _menuKey = new GUIStyle(GUI.skin.label) { fontSize = Mathf.RoundToInt(0.018f * h), fontStyle = FontStyle.Bold, alignment = TextAnchor.UpperLeft };
            _menuKey.normal.textColor = MenuDim;
            _menuTitle = new GUIStyle(GUI.skin.label) { fontSize = Mathf.RoundToInt(0.026f * h), fontStyle = FontStyle.Bold, alignment = TextAnchor.UpperLeft };
            _menuTitle.normal.textColor = Color.white;
            if (_menuLabels == null)
            {
                int n = arsenal.C.Length;
                _menuLabels = new string[n];
                _menuKeys = new string[n];
                for (int k = 0; k < n; k++)
                {
                    var D = arsenal.C[k].S.D;
                    _menuLabels[k] = string.IsNullOrEmpty(D.weapon.type_de) ? D.weapon.name : D.weapon.type_de;   // Klasse statt Modellname
                    _menuKeys[k] = k < 10 ? ((k + 1) % 10).ToString() : "";          // Taste 1 … 9, 0; weitere nur im Menü
                }
            }
        }

        /// <summary>Unten rechts: Symbol der aktiven Waffe, darunter ihr Name und die Munition (unbegrenzt: ∞).</summary>
        void WeaponHud(GUIStyle big)
        {
            Styles();
            float H = Screen.height, W = Screen.width, m = 0.03f * H;
            var ammo = new Rect(W - m - 0.25f * H, H - m - 0.06f * H, 0.25f * H, 0.06f * H);
            GUI.Label(ammo, _ammoText, big);
            var name = new Rect(W - m - 0.5f * H, ammo.y - 0.028f * H, 0.5f * H, 0.028f * H);
            GUI.Label(name, _menuLabels[arsenal.Active], _name);
            var ic = Current.icon;
            if (ic != null && Event.current.type == EventType.Repaint)
            {
                float ih = HudIconH * H * (ic.height > ic.width ? 1.8f : 1f);      // hohe Symbole (Bogen) größer, sonst kaum lesbar
                float iw = Mathf.Min(HudIconMaxW * H, ih * ic.width / ic.height);
                ih = iw * ic.height / ic.width;
                var old = GUI.color;
                GUI.color = HudWhite;
                GUI.DrawTexture(new Rect(W - m - iw, name.y - 0.008f * H - ih, iw, ih), ic, ScaleMode.ScaleToFit);
                GUI.color = old;
            }
        }

        /// <summary>Rechteck einer Zelle k im Waffenmenü (Bildpunkte, Ursprung oben links) – auch für die Sichtprüfung.</summary>
        public Rect MenuCellRect(int k)
        {
            float H = Screen.height, W = Screen.width, cw = MenuCellW * H, ch = MenuCellH * H, gap = 0.012f * H;
            int cols = menu.columns, rows = menu.Rows;
            float tw = cols * cw + (cols - 1) * gap, th = rows * ch + (rows - 1) * gap;
            float x0 = (W - tw) / 2, y0 = (H - th) / 2 + 0.03f * H;
            return new Rect(x0 + (k % cols) * (cw + gap), y0 + (k / cols) * (ch + gap), cw, ch);
        }

        void Fill(Rect r, Color c)
        {
            var old = GUI.color;
            GUI.color = c;
            GUI.DrawTexture(r, Texture2D.whiteTexture);
            GUI.color = old;
        }

        void MenuGui()
        {
            Styles();
            float H = Screen.height;
            var first = MenuCellRect(0);
            var last = MenuCellRect(menu.Rows * menu.columns - 1);
            var panel = new Rect(first.x - 0.02f * H, first.y - 0.07f * H, last.xMax - first.x + 0.04f * H, last.yMax - first.y + 0.09f * H);
            if (Event.current.type == EventType.Repaint) Fill(panel, MenuPanel);
            GUI.Label(new Rect(panel.x + 0.02f * H, panel.y + 0.012f * H, panel.width, 0.04f * H), "Waffe wählen", _menuTitle);
            GUI.Label(new Rect(panel.x, panel.y + 0.016f * H, panel.width - 0.02f * H, 0.03f * H),
                      "Mausrad/Pfeile · Enter oder Klick wählen · Esc schließen", _name);
            for (int k = 0; k < arsenal.C.Length; k++)
            {
                var r = MenuCellRect(k);
                bool sel = k == menu.Index;
                if (Event.current.type == EventType.Repaint)
                {
                    Fill(r, sel ? MenuSel : MenuCell);
                    if (sel)
                    {
                        float e = Mathf.Max(2, 0.003f * H);
                        Fill(new Rect(r.x, r.y, r.width, e), MenuEdge);
                        Fill(new Rect(r.x, r.yMax - e, r.width, e), MenuEdge);
                        Fill(new Rect(r.x, r.y, e, r.height), MenuEdge);
                        Fill(new Rect(r.xMax - e, r.y, e, r.height), MenuEdge);
                    }
                    if (k == arsenal.Active) Fill(new Rect(r.xMax - 0.018f * H, r.y + 0.01f * H, 0.008f * H, 0.008f * H), MenuEdge);   // aktive Waffe
                    var ic = loadouts[k].icon;
                    if (ic != null)
                    {
                        var old = GUI.color;
                        GUI.color = sel ? Color.white : MenuDim;
                        GUI.DrawTexture(new Rect(r.x + 0.1f * r.width, r.y + 0.14f * r.height, 0.8f * r.width, 0.56f * r.height), ic, ScaleMode.ScaleToFit);
                        GUI.color = old;
                    }
                }
                GUI.Label(new Rect(r.x + 0.06f * H * 0.2f + 4, r.y + 2, r.width, 0.03f * H), _menuKeys[k], _menuKey);
                GUI.Label(new Rect(r.x, r.yMax - 0.034f * H, r.width, 0.03f * H), _menuLabels[k], _menuName);
            }
        }

        // Anzeigetexte nur bei geänderten Werten neu bauen (kein Speicher je Bild)
        string _ammoText = "", _stateText = "", _hitText = "";
        public string HudHitText => _hitText;
        int _hAmmo = -1, _hFrame = -1, _hHits = -1, _hWeapon = -1;
        string _hAction, _hMarker;

        /// <summary>Anzeigetexte aktualisieren; baut nur bei geänderten Werten neu (öffentlich für den GC-Test).</summary>
        public void UpdateHudText()
        {
            if (C.ammo != _hAmmo || arsenal.Active != _hWeapon)
            {
                _hAmmo = C.ammo;
                _ammoText = C.S.D.gameplay.Unlimited ? "∞" : $"{C.ammo} / {C.magSize}";   // Werkzeug ohne Magazin (0.22)
            }
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
