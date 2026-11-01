// Hüft-Fadenkreuz (Entscheidungsliste 4.1 A / 4.2 A, Nutzer 25.10.2026): Form, Größe, Farbe und Aufgehen aus ego.json › gameplay.hip
// (Katalog basic/reticles.py › HIP, DEFAULTS, SPREAD). Nur in der Hüfte sichtbar; aus beim Zielen (schon im ersten Bild), im Sprint
// (Automatik: nur „^“), beim Nachladen, Ziehen, Wegstecken, Betrachten und bei gesenkter Waffe. Kein ständiges Kreuz wie in 0.9.
// 0.36: an beim Spannen, Lösen und Entspannen des Bogens aus der Hüfte (shown_in), dabei schließt es sich mit dem Auszug.
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
        sealed class Raster { public Texture2D tex; public Color32[] px; public float s = -1, h = -1; }
        readonly Raster _rHip = new Raster(), _rSpr = new Raster();      // je Form eine Textur: Sprintwechsel legt nichts neu an

        public HipReticle(EgoHip h)
        {
            H = h;
            _hipForm = new EgoHipForm { kind = h.kind, share_h = h.share_h, extent_mm = h.extent_mm, prims = h.prims };
            ColorUtility.TryParseHtmlString(h.color, out var c);
            _color = c;
            spread = h.spread.@base;
            _sprintReason = "sprint_" + h.sprint?.kind;
        }

        /// <summary>Vor dem Feuern dieses Bilds: Abklingen zur Basis (+ Laufen) mit recover_s, wie reticles.simulate; `open` 0 … 1 öffnet
        /// zusätzlich um charge_from (0.36, Bogen: 1 − Auszug – ungespannt offen, voll gespannt geschlossen; reticles.simulate kennt den
        /// Öffnungsanteil noch nicht).</summary>
        public void Decay(float dt, float speed01, float open = 0)
        {
            var S = H.spread;
            float target = S.@base + S.move * Mathf.Clamp01(speed01) + S.charge_from * Mathf.Clamp01(open);
            spread = target + (spread - target) * Mathf.Exp(-dt / Mathf.Max(1e-4f, S.recover_s));
        }

        /// <summary>Je Schuss: Impuls per_shot bis max.</summary>
        public void Kick() => spread = Mathf.Min(H.spread.max, spread + H.spread.per_shot);

        /// <summary>Sichtbarkeit nach dem Zustand dieses Bilds (nach EgoController.Tick).</summary>
        public void See(EgoController c)
        {
            SprintForm = false;
            Reason = c.Holstered ? "holstered" : c.Busy && !ShownIn(c.ActionName) ? c.ActionName : c.CurrentStance == EgoController.Stance.Ads ? "ads"
                   : c.adsWeight > 0 ? "aim_out" : c.CurrentStance == EgoController.Stance.Lowered ? "lowered" : null;
            if (Reason == null && c.CurrentStance == EgoController.Stance.Sprint)
            {
                SprintForm = !string.IsNullOrEmpty(H.sprint?.kind);
                Reason = SprintForm ? _sprintReason : "sprint";
                Visible = SprintForm;
                return;
            }
            Visible = Reason == null && H.prims != null && H.prims.Length > 0;   // 0.33: Raketenwerfer ohne Hüftzeichen (Form 'none')
            Reason ??= H.prims != null && H.prims.Length > 0 ? "hip" : "none";
        }

        /// <summary>0.36: blockierende Aktion, in der das Hüftzeichen an bleibt (reticles.HIP shown_in: Bogen spannen, lösen, entspannen).</summary>
        bool ShownIn(string action)
        {
            if (H.shown_in != null)
                foreach (var a in H.shown_in) if (a == action) return true;
            return false;
        }

        /// <summary>Pixel je mm auf der Scheibe bei Bildhöhe h: sichtbares Außenmaß der Form (mit Linienstärke) = share_h · h.</summary>
        public float PxPerMm(float h) => Form.share_h * h / Mathf.Max(1e-4f, Form.extent_mm);

        /// <summary>Sichtbares Außenmaß der gezeichneten Form in Pixeln bei Bildhöhe h (größere Seite des Rahmens, mit Linienstärke
        /// wie in Mask) – Messwert; bei Spreizung 0 gleich share_h · h, solange min_line_px nicht greift.</summary>
        public float ExtentPx(float h)
        {
            if (Form.prims == null || Form.prims.Length == 0) return 0;    // Form 'none' (Raketenwerfer): nichts zu zeichnen
            float sp = Drawn, k = PxPerMm(h), w = H.weight, lw = Mathf.Max(H.line_r_mm * w * k, H.min_line_px);
            float x0 = 1e9f, x1 = -1e9f, y0 = 1e9f, y1 = -1e9f;
            foreach (var p in Form.prims)
            {
                if (p.t == "line")
                {
                    float ax = (p.a[0] + sp * p.d[0]) * k, ay = (p.a[1] + sp * p.d[1]) * k, bx = (p.b[0] + sp * p.d[0]) * k, by = (p.b[1] + sp * p.d[1]) * k;
                    x0 = Mathf.Min(x0, Mathf.Min(ax, bx) - lw); x1 = Mathf.Max(x1, Mathf.Max(ax, bx) + lw);
                    y0 = Mathf.Min(y0, Mathf.Min(ay, by) - lw); y1 = Mathf.Max(y1, Mathf.Max(ay, by) + lw);
                }
                else
                {
                    float r = Radius(p, sp, k);
                    x0 = Mathf.Min(x0, -r); x1 = Mathf.Max(x1, r); y0 = Mathf.Min(y0, -r); y1 = Mathf.Max(y1, r);
                }
            }
            return Mathf.Max(x1 - x0, y1 - y0);
        }

        /// <summary>Außenradius eines Rings (innen fest, Dicke · weight, mindestens 2·min_line_px) oder Punkts (· (0,5 + 0,5·weight)) in px.</summary>
        float Radius(EgoPrim p, float sp, float k)
        {
            float w = H.weight;
            if (p.t == "ring") return (p.ri + sp * p.grow) * k + Mathf.Max((p.r - p.ri) * w * k, 2 * H.min_line_px);
            return Mathf.Max(p.r * (0.5f + 0.5f * w) * k, H.min_line_px);
        }

        /// <summary>Weiße Maske der aktuellen Form bei Bildhöhe h (Kantenlänge = Texturbreite in Pixeln, 1:1 zeichnen); nur neu
        /// gerastert, wenn sich Spreizung oder Bildhöhe ändern (je Form eine Textur). Linienstärke wie basic/common.reticle: Linie
        /// LINE_R·weight, Ringdicke ·weight (innen fest), Punkt ·(0,5 + 0,5·weight); Linien mindestens 2·min_line_px breit.</summary>
        public Texture2D Mask(float h)
        {
            float sp = Drawn;
            var R = SprintForm ? _rSpr : _rHip;
            if (R.tex != null && Mathf.Abs(R.s - sp) < 1e-3f && R.h == h) return R.tex;
            float k = PxPerMm(h), w = H.weight, minPx = H.min_line_px;
            float reach = 0;
            foreach (var p in Form.prims)
                reach = Mathf.Max(reach, p.t == "line" ? Mathf.Max(Mathf.Max(Mathf.Abs(p.a[0]), Mathf.Abs(p.a[1])), Mathf.Max(Mathf.Abs(p.b[0]), Mathf.Abs(p.b[1]))) : p.r);
            int half = Mathf.CeilToInt((reach + H.spread.max + 2 * H.line_r_mm) * k + 2 * minPx) + 2;
            int n = 2 * half;
            if (R.tex == null || R.tex.width != n)
            {
                Free(R.tex);
                R.tex = new Texture2D(n, n, TextureFormat.RGBA32, false) { filterMode = FilterMode.Point, wrapMode = TextureWrapMode.Clamp };
                R.px = new Color32[n * n];
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
                            float inner = (p.ri + sp * p.grow) * k, outer = Radius(p, sp, k);
                            d = Mathf.Min(d, Mathf.Abs(Mathf.Sqrt(px * px + py * py) - (inner + outer) / 2) - (outer - inner) / 2);
                        }
                        else d = Mathf.Min(d, Mathf.Sqrt(px * px + py * py) - Radius(p, sp, k));
                    }
                    float a = Mathf.Clamp01(0.5f - d);
                    R.px[y * n + x] = new Color32(255, 255, 255, (byte)(op * a));
                }
            R.tex.SetPixels32(R.px);
            R.tex.Apply(false);                    // lesbar lassen: die Aufnahme stempelt per GetPixelBilinear
            R.s = sp; R.h = h;
            return R.tex;
        }

        /// <summary>Texturen freigeben (EgoPlayer.OnDestroy, Tests).</summary>
        public void Release()
        {
            Free(_rHip.tex); Free(_rSpr.tex);
            _rHip.tex = _rSpr.tex = null;
            _rHip.s = _rSpr.s = -1;
        }

        static void Free(Texture2D t)
        {
            if (t == null) return;
            if (Application.isPlaying) Object.Destroy(t); else Object.DestroyImmediate(t);
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
