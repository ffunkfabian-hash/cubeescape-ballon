// Wirkung der Waffen (0.34 „Payload“): ein unbeleuchteter Shader für alle Welteffekte, Form aus der UV statt aus Texturen.
// _Mode 0 weicher Fleck (Licht, Staub, Rauch mit Rauschen), 1 Ring (Druckwelle), 2 Einschussloch (dunkler Kern, heller aufgeworfener
// Rand, Rußhof; _Kind 1 = Brandfleck ohne Loch), 3 Strahl (Gauß quer zur Länge, v = quer), 4 Funke (gestreckter Punkt).
// Farbe = _BaseColor · Vertexfarbe (Partikel, Linien); _Alpha und _Seed je Renderer (MaterialPropertyBlock, Löcher). Mischung über
// _SrcBlend/_DstBlend: additiv (One One) für Licht, Funken, Strahlen, Ring; Alpha (SrcAlpha OneMinusSrcAlpha) für Rauch, Staub, Löcher.
Shader "Ballon/Fx"
{
    Properties
    {
        _BaseColor ("Farbe", Color) = (1, 1, 1, 1)
        _Mode ("Form", Float) = 0
        _Kind ("Art (Loch 0, Brand 1)", Float) = 0
        _Seed ("Form-Saat", Float) = 0
        _Alpha ("Deckung", Float) = 1
        _Noise ("Rauschen", Float) = 0
        [Enum(UnityEngine.Rendering.BlendMode)] _SrcBlend ("Quelle", Float) = 1
        [Enum(UnityEngine.Rendering.BlendMode)] _DstBlend ("Ziel", Float) = 1
        _OffsetUnits ("Tiefenversatz", Float) = 0
    }
    SubShader
    {
        Tags { "RenderType" = "Transparent" "Queue" = "Transparent" "RenderPipeline" = "UniversalPipeline" "IgnoreProjector" = "True" }
        Pass
        {
            Name "Fx"
            Tags { "LightMode" = "UniversalForward" }
            Blend [_SrcBlend] [_DstBlend]
            ZWrite Off
            Cull Off
            Offset -1, [_OffsetUnits]
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                float4 _BaseColor;
                float _Mode, _Kind, _Seed, _Alpha, _Noise, _SrcBlend, _DstBlend, _OffsetUnits;
            CBUFFER_END

            struct Attributes { float4 pos : POSITION; float2 uv : TEXCOORD0; float4 color : COLOR; };
            struct Varyings { float4 pos : SV_POSITION; float2 uv : TEXCOORD0; float4 color : COLOR; };

            Varyings Vert(Attributes a)
            {
                Varyings o;
                o.pos = TransformObjectToHClip(a.pos.xyz);
                o.uv = a.uv;
                o.color = a.color;
                return o;
            }

            float Hash(float2 p) { return frac(sin(dot(p, float2(127.1, 311.7))) * 43758.5453); }

            float Noise(float2 p)
            {
                float2 i = floor(p), f = frac(p);
                float2 u = f * f * (3 - 2 * f);
                return lerp(lerp(Hash(i), Hash(i + float2(1, 0)), u.x), lerp(Hash(i + float2(0, 1)), Hash(i + float2(1, 1)), u.x), u.y);
            }

            // Einschussloch: Radius r vom Mittelpunkt, Winkel a; Rand unregelmäßig je Saat
            float4 Hole(float2 c, float seed)
            {
                float r = length(c) * 2, a = atan2(c.y, c.x);
                float wob = 0.06 * sin(a * 5 + seed * 6.28) + 0.04 * sin(a * 9 + seed * 17.0) + 0.05 * (Noise(float2(a * 2.2, seed * 9)) - 0.5);
                float rr = r + wob;
                float soot = (1 - smoothstep(0.30, 1.0, rr)) * (0.55 + 0.45 * Noise(c * 9 + seed * 13));
                if (_Kind > 0.5)                                   // Brandfleck: nur Ruß, dunkler zur Mitte
                {
                    float burn = (1 - smoothstep(0.0, 1.0, rr)) * (0.5 + 0.5 * Noise(c * 6 + seed * 5));
                    return float4(0.035, 0.032, 0.03, saturate(burn * 1.15));
                }
                float core = 1 - smoothstep(0.16, 0.21, rr);       // dunkler Kern (das Loch)
                float rim = smoothstep(0.18, 0.24, rr) * (1 - smoothstep(0.26, 0.36, rr));   // heller aufgeworfener Rand
                float3 col = lerp(float3(0.06, 0.055, 0.05), float3(0.55, 0.52, 0.48), rim);
                col = lerp(col, float3(0.012, 0.012, 0.012), core);
                float alpha = saturate(max(core, max(rim * 0.85, soot * 0.6)));
                return float4(col, alpha);
            }

            half4 Frag(Varyings i) : SV_Target
            {
                float2 c = i.uv - 0.5;
                float4 col = _BaseColor * i.color;
                float k = 1;
                if (_Mode < 0.5)                                   // weicher Fleck
                {
                    float r = length(c) * 2;
                    k = 1 - smoothstep(0, 1, r);                     // voller Kern, weicher Rand (auch vor hellem Grund lesbar)
                    if (_Noise > 0) k *= saturate(0.55 + 0.9 * (Noise(i.uv * 5 + _Seed + i.color.a * 3) - 0.35)) * 1.2;
                }
                else if (_Mode < 1.5)                              // Ring
                {
                    float r = length(c) * 2;
                    k = saturate(1 - abs(r - 0.82) / 0.16);
                    k *= k;
                }
                else if (_Mode < 2.5)                              // Einschussloch, Brandfleck
                {
                    float4 h = Hole(c, _Seed);
                    return half4(h.rgb * col.rgb, h.a * _Alpha * col.a);
                }
                else if (_Mode < 3.5)                              // Strahl: hell in der Mitte, weich zum Rand (v quer)
                {
                    float v = abs(i.uv.y - 0.5) * 2;
                    k = exp(-v * v * 6) + 0.6 * exp(-v * v * 60);
                }
                else                                               // Funke
                {
                    float r = length(float2(c.x * 0.6, c.y * 2.2)) * 2;
                    k = saturate(1 - r);
                }
                float a = col.a * k * _Alpha;
                if (_DstBlend < 1.5) return half4(col.rgb * a, a);     // additiv (One One): Deckung steckt in der Farbe
                return half4(col.rgb, a);                              // Alpha (SrcAlpha OneMinusSrcAlpha)
            }
            ENDHLSL
        }
    }
}
