// Hüft-Fadenkreuz (Entscheidungsliste 4.1 A / 4.2 A, Nutzer 25.10.2026): Form, Größe, Farbe und Aufgehen aus ego.json › gameplay.hip
// (Katalog basic/reticles.py › HIP, DEFAULTS, SPREAD). Nur in der Hüfte sichtbar; aus beim Zielen (schon im ersten Bild), im Sprint
// (Automatik: nur „^“), beim Nachladen, Ziehen, Wegstecken, Betrachten und bei gesenkter Waffe. Kein ständiges Kreuz wie in 0.9.
using UnityEngine;

namespace Ballon.Ego
{
    public sealed class HipReticle
    {
        public readonly EgoHip H;
        public float spread;                       // mm auf der Scheibe (reticles.SPREAD), wie reticles.simulate
        public bool Visible { get; private set; }
        public bool SprintForm { get; private set; }
        public string Reason { get; private set; } = "hip";     // warum sichtbar/aus (Aufnahme, Tests)
        EgoHipForm Form => SprintForm ? H.sprint : _hipForm;
        float Drawn => SprintForm ? 0 : spread;        // „^“ im Sprint bleibt geschlossen (Haltungszeichen, Glidepath), kein Aufgehen
        public string Kind => Form.kind;

        readonly EgoHipForm _hipForm;
        readonly string _sprintReason;
        readonly Color32 _color;
        Texture2D _tex;
        Color32[] _px;
        float _rSpread = -1, _rH = -1;
        bool _rSprint;

        public HipReticle(EgoHip h)
        {
            H = h;
            _hipForm = new EgoHipForm { kind = h.kind, share_h = h.share_h, extent_mm = h.extent_mm, prims = h.prims };
            ColorUtility.TryParseHtmlString(h.color, out var c);
            _color = c;
            spread = h.spread.@base;
            _sprintReason = "sprint_" + h.sprint?.kind;
        }

        /// <summary>Vor dem Feuern dieses Bilds: Abklingen zur Basis (+ Laufen) mit recover_s, wie reticles.simulate.</summary>
        public void Decay(float dt, float speed01)
        {
            var S = H.spread;
            float target = S.@base + S.move * Mathf.Clamp01(speed01);
            spread = target + (spread - target) * Mathf.Exp(-dt / Mathf.Max(1e-4f, S.recover_s));
        }

        /// <summary>Je Schuss: Impuls per_shot bis max.</summary>
        public void Kick() => spread = Mathf.Min(H.spread.max, spread + H.spread.per_shot);

        /// <summary>Sichtbarkeit nach dem Zustand dieses Bilds (nach EgoController.Tick).</summary>
        public void See(EgoController c)
        {
            SprintForm = false;
            Reason = c.Holstered ? "holstered" : c.Busy ? c.ActionName : c.CurrentStance == EgoController.Stance.Ads ? "ads"
                   : c.adsWeight > 0 ? "aim_out" : c.CurrentStance == EgoController.Stance.Lowered ? "lowered" : null;
            if (Reason == null && c.CurrentStance == EgoController.Stance.Sprint)
            {
                SprintForm = !string.IsNullOrEmpty(H.sprint?.kind);
                Reason = SprintForm ? _sprintReason : "sprint";
                Visible = SprintForm;
                return;
            }
            Visible = Reason == null;
            Reason ??= "hip";
        }

        /// <summary>Pixel je mm auf der Scheibe bei Bildhöhe h: Außenmaß der Form = share_h · h.</summary>
        public float PxPerMm(float h) => Form.share_h * h / Mathf.Max(1e-4f, Form.extent_mm);

        /// <summary>Außenmaß der gezeichneten Form in Pixeln (größere Seite des Rahmens um Linienmitten, Ringe, Punkte) – Messwert.</summary>
        public float ExtentPx(float h)
        {
            float sp = Drawn, k = PxPerMm(h), x0 = 1e9f, x1 = -1e9f, u0 = 1e9f, u1 = -1e9f;
            foreach (var p in Form.prims)
            {
                if (p.t == "line")
                {
                    float ax = p.a[0] + sp * p.d[0], au = p.a[1] + sp * p.d[1], bx = p.b[0] + sp * p.d[0], bu = p.b[1] + sp * p.d[1];
                    x0 = Mathf.Min(x0, Mathf.Min(ax, bx)); x1 = Mathf.Max(x1, Mathf.Max(ax, bx));
                    u0 = Mathf.Min(u0, Mathf.Min(au, bu)); u1 = Mathf.Max(u1, Mathf.Max(au, bu));
                }
                else
                {
                    float r = p.r + (p.t == "ring" ? sp * p.grow : 0);
                    x0 = Mathf.Min(x0, -r); x1 = Mathf.Max(x1, r); u0 = Mathf.Min(u0, -r); u1 = Mathf.Max(u1, r);
                }
            }
            return Mathf.Max(x1 - x0, u1 - u0) * k;
        }

        /// <summary>Weiße Maske der aktuellen Form bei Bildhöhe h (Kantenlänge = Texturbreite in Pixeln, 1:1 zeichnen); nur neu
        /// gerastert, wenn sich Spreizung, Form oder Bildhöhe ändern. Linienstärke wie basic/common.reticle: Linie LINE_R·weight,
        /// Ringdicke ·weight (innen fest), Punkt ·(0,5 + 0,5·weight); Linien mindestens 2·min_line_px breit.</summary>
        public Texture2D Mask(float h)
        {
            float sp = Drawn;
            if (_tex != null && Mathf.Abs(_rSpread - sp) < 1e-3f && _rH == h && _rSprint == SprintForm) return _tex;
            float k = PxPerMm(h), w = H.weight, minPx = H.min_line_px;
            float reach = 0;
            foreach (var p in Form.prims)
                reach = Mathf.Max(reach, p.t == "line" ? Mathf.Max(Mathf.Max(Mathf.Abs(p.a[0]), Mathf.Abs(p.a[1])), Mathf.Max(Mathf.Abs(p.b[0]), Mathf.Abs(p.b[1]))) : p.r);
            int half = Mathf.CeilToInt((reach + H.spread.max + 2 * H.line_r_mm) * k) + 2;
            int n = 2 * half;
            if (_tex == null || _tex.width != n)
            {
                if (_tex != null) { if (Application.isPlaying) Object.Destroy(_tex); else Object.DestroyImmediate(_tex); }
                _tex = new Texture2D(n, n, TextureFormat.RGBA32, false) { filterMode = FilterMode.Point, wrapMode = TextureWrapMode.Clamp };
                _px = new Color32[n * n];
            }
            float lw = Mathf.Max(H.line_r_mm * w * k, minPx);
            byte op = (byte)Mathf.RoundToInt(255 * H.opacity);
            for (int y = 0; y < n; y++)
                for (int x = 0; x < n; x++)
                {
                    float px = x + 0.5f - half, py = y + 0.5f - half;       // Pixel rechts/oben von der Mitte
                    float d = 1e9f;
                    foreach (var p in Form.prims)
                    {
                        if (p.t == "line")                                 // x der Scheibe zeigt nach links
                        {
                            float ax = -(p.a[0] + sp * p.d[0]) * k, ay = (p.a[1] + sp * p.d[1]) * k;
                            float bx = -(p.b[0] + sp * p.d[0]) * k, by = (p.b[1] + sp * p.d[1]) * k;
                            d = Mathf.Min(d, Segment(px, py, ax, ay, bx, by) - lw);
                        }
                        else if (p.t == "ring")
                        {
                            float g = sp * p.grow, inner = (p.ri + g) * k, outer = inner + Mathf.Max((p.r - p.ri) * w * k, 2 * minPx);
                            d = Mathf.Min(d, Mathf.Abs(Mathf.Sqrt(px * px + py * py) - (inner + outer) / 2) - (outer - inner) / 2);
                        }
                        else d = Mathf.Min(d, Mathf.Sqrt(px * px + py * py) - Mathf.Max(p.r * (0.5f + 0.5f * w) * k, minPx));
                    }
                    float a = Mathf.Clamp01(0.5f - d);
                    _px[y * n + x] = new Color32(255, 255, 255, (byte)(op * a));
                }
            _tex.SetPixels32(_px);
            _tex.Apply(false);                     // lesbar lassen: die Aufnahme stempelt per GetPixelBilinear
            _rSpread = sp; _rH = h; _rSprint = SprintForm;
            return _tex;
        }

        public Color Color => _color;

        static float Segment(float px, float py, float ax, float ay, float bx, float by)
        {
            float vx = bx - ax, vy = by - ay, l2 = vx * vx + vy * vy;
            float t = l2 > 0 ? Mathf.Clamp01(((px - ax) * vx + (py - ay) * vy) / l2) : 0;
            float dx = px - ax - t * vx, dy = py - ay - t * vy;
            return Mathf.Sqrt(dx * dx + dy * dy);
        }
    }
}
