// Tonwertabbildung wie Blender (Ansicht AgX, Look „Medium High Contrast“): log2-Formung der linearen Szenenfarbe, 3D-LUT aus
// tools/bake_unity.agx_lut (Streifen n² × n, x = R + B·n, y = G), Ausgabe linear, damit das sRGB-Ziel richtig kodiert.
// Läuft als Vollbild-Durchgang am Ende des Kamerastapels (Renderer „Out“ der Viewmodel-Kamera), kein Bloom.
Shader "Ballon/AgX"
{
    Properties
    {
        _Lut ("LUT (Anzeige-sRGB)", 2D) = "white" {}
        _LutParams ("n, ev0, ev1, Mittelgrau", Vector) = (33, -12.47393, 4.026069, 0.18)
        _Exposure ("Belichtung (Blenden)", Float) = 0
    }
    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" }
        ZWrite Off Cull Off ZTest Always
        Pass
        {
            Name "AgX"
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.core/Runtime/Utilities/Blit.hlsl"

            TEXTURE2D(_Lut);
            SAMPLER(sampler_Lut);
            float4 _LutParams;
            float _Exposure;

            float3 SampleLut(float3 u)
            {
                float n = _LutParams.x;
                float3 c = saturate(u) * (n - 1);
                float b0 = floor(c.b);
                float b1 = min(b0 + 1, n - 1);
                float fb = c.b - b0;
                float2 uv0 = float2((c.r + 0.5 + b0 * n) / (n * n), (c.g + 0.5) / n);
                float2 uv1 = float2((c.r + 0.5 + b1 * n) / (n * n), (c.g + 0.5) / n);
                return lerp(SAMPLE_TEXTURE2D_LOD(_Lut, sampler_Lut, uv0, 0).rgb, SAMPLE_TEXTURE2D_LOD(_Lut, sampler_Lut, uv1, 0).rgb, fb);
            }

            half4 Frag(Varyings i) : SV_Target
            {
                float3 c = SAMPLE_TEXTURE2D_X(_BlitTexture, sampler_LinearClamp, i.texcoord).rgb * exp2(_Exposure);
                float3 ev = log2(max(c, 1e-10) / _LutParams.w);
                float3 u = (ev - _LutParams.y) / (_LutParams.z - _LutParams.y);
                return half4(SRGBToLinear(SampleLut(u)), 1);
            }
            ENDHLSL
        }
    }
}
