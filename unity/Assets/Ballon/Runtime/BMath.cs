// Rechnen im Blender-Kameraraum (rechtshändig, rechts −X, vorn −Y, oben +Z) mit Unitys Typen als reiner Mathematik.
// Quaternion.AngleAxis / Matrix4x4.Rotate / Vector3.Cross sind die üblichen Formeln, also gleich wie mathutils
// (Matrix.Rotation, Vector.cross). Nach Unity wird erst am Ende umgerechnet (ToUnity), mit der Matrix aus ego.json.
using UnityEngine;

namespace Ballon.Ego
{
    public static class BMath
    {
        public static Vector3 V(float[] a) => new Vector3(a[0], a[1], a[2]);

        public static float Ease(float x)
        {
            x = Mathf.Clamp01(x);
            return x * x * (3 - 2 * x);
        }

        /// <summary>tools/blender_build.ease(a, b, x)</summary>
        public static float Ease(float a, float b, float x) => b > a ? Ease((x - a) / (b - a)) : 1f;

        /// <summary>tools/blender_build.value_at</summary>
        public static float ValueAt(ValueKey[] keys, float f)
        {
            if (f <= keys[0].f) return keys[0].v;
            for (int i = 0; i + 1 < keys.Length; i++)
            {
                var k0 = keys[i];
                var k1 = keys[i + 1];
                if (k0.f <= f && f <= k1.f) return k0.v + (k1.v - k0.v) * Ease(k0.f, k1.f, f);
            }
            return keys[keys.Length - 1].v;
        }

        /// <summary>Drehung um eine Achse (Bogenmaß), Rechte-Hand-Regel wie mathutils.Matrix.Rotation.</summary>
        public static Matrix4x4 Rot(float rad, Vector3 axis) => Matrix4x4.Rotate(Quaternion.AngleAxis(rad * Mathf.Rad2Deg, axis.normalized));

        public static Matrix4x4 RotX(float rad) => Rot(rad, Vector3.right);
        public static Matrix4x4 RotY(float rad) => Rot(rad, Vector3.up);
        public static Matrix4x4 RotZ(float rad) => Rot(rad, Vector3.forward);
        public static Matrix4x4 T(Vector3 t) => Matrix4x4.Translate(t);
        public static float Rad(float deg) => deg * Mathf.Deg2Rad;

        /// <summary>Spalten x, y, z und Lage (wie ego_build.mat(Matrix((x, y, z)).transposed(), loc)).</summary>
        public static Matrix4x4 Cols(Vector3 x, Vector3 y, Vector3 z, Vector3 loc)
        {
            var m = Matrix4x4.identity;
            m.SetColumn(0, new Vector4(x.x, x.y, x.z, 0));
            m.SetColumn(1, new Vector4(y.x, y.y, y.z, 0));
            m.SetColumn(2, new Vector4(z.x, z.y, z.z, 0));
            m.SetColumn(3, new Vector4(loc.x, loc.y, loc.z, 1));
            return m;
        }

        /// <summary>ego_build.frame_from: +Z entlang z, +Y möglichst nach y_hint, x = y × z.</summary>
        public static Matrix4x4 FrameFrom(Vector3 z, Vector3 yHint, Vector3 loc = default)
        {
            z = z.normalized;
            var y = (yHint - z * Vector3.Dot(yHint, z)).normalized;
            var x = Vector3.Cross(y, z);
            return Cols(x, y, z, loc);
        }

        public static Vector3 Pos(Matrix4x4 m) => m.GetColumn(3);
        public static Vector3 Col(Matrix4x4 m, int i) => m.GetColumn(i);

        /// <summary>Nur Drehanteil (Lage null).</summary>
        public static Matrix4x4 Rot3(Matrix4x4 m)
        {
            m.SetColumn(3, new Vector4(0, 0, 0, 1));
            return m;
        }

        public static Matrix4x4 WithPos(Matrix4x4 m, Vector3 p)
        {
            m.SetColumn(3, new Vector4(p.x, p.y, p.z, 1));
            return m;
        }

        public static Quaternion Q(Matrix4x4 m) => QuatFrom(m);

        /// <summary>Drehmatrix → Quaternion (Shepperd), unabhängig von Unitys Zerlegung mit Skalierung.</summary>
        public static Quaternion QuatFrom(Matrix4x4 m)
        {
            float tr = m.m00 + m.m11 + m.m22;
            float x, y, z, w;
            if (tr > 0)
            {
                float s = Mathf.Sqrt(tr + 1f) * 2f;
                w = 0.25f * s; x = (m.m21 - m.m12) / s; y = (m.m02 - m.m20) / s; z = (m.m10 - m.m01) / s;
            }
            else if (m.m00 > m.m11 && m.m00 > m.m22)
            {
                float s = Mathf.Sqrt(1f + m.m00 - m.m11 - m.m22) * 2f;
                w = (m.m21 - m.m12) / s; x = 0.25f * s; y = (m.m01 + m.m10) / s; z = (m.m02 + m.m20) / s;
            }
            else if (m.m11 > m.m22)
            {
                float s = Mathf.Sqrt(1f + m.m11 - m.m00 - m.m22) * 2f;
                w = (m.m02 - m.m20) / s; x = (m.m01 + m.m10) / s; y = 0.25f * s; z = (m.m12 + m.m21) / s;
            }
            else
            {
                float s = Mathf.Sqrt(1f + m.m22 - m.m00 - m.m11) * 2f;
                w = (m.m10 - m.m01) / s; x = (m.m02 + m.m20) / s; y = (m.m12 + m.m21) / s; z = 0.25f * s;
            }
            return new Quaternion(x, y, z, w).normalized;
        }

        /// <summary>Drehung (Slerp) und Lage (linear) zwischen zwei starren Matrizen.</summary>
        public static Matrix4x4 Blend(Matrix4x4 a, Matrix4x4 b, float t)
        {
            var q = QSlerp(QuatFrom(a), QuatFrom(b), t);
            return Matrix4x4.TRS(Vector3.Lerp(Pos(a), Pos(b), t), q, Vector3.one);
        }

        /// <summary>Slerp über den kürzeren Weg (wie Blender interp_qt_qtqt).</summary>
        public static Quaternion QSlerp(Quaternion a, Quaternion b, float t)
        {
            float cos = a.x * b.x + a.y * b.y + a.z * b.z + a.w * b.w;
            if (cos < 0) { b = new Quaternion(-b.x, -b.y, -b.z, -b.w); cos = -cos; }
            float w0, w1;
            if (1f - cos > 1e-4f)
            {
                float om = Mathf.Acos(Mathf.Min(cos, 1f)), s = Mathf.Sin(om);
                w0 = Mathf.Sin((1 - t) * om) / s;
                w1 = Mathf.Sin(t * om) / s;
            }
            else { w0 = 1 - t; w1 = t; }
            return new Quaternion(w0 * a.x + w1 * b.x, w0 * a.y + w1 * b.y, w0 * a.z + w1 * b.z, w0 * a.w + w1 * b.w).normalized;
        }

        /// <summary>mathutils Vector.slerp für Richtungen (Ergebnis Einheitsvektor).</summary>
        public static Vector3 SlerpDir(Vector3 a, Vector3 b, float t)
        {
            a = a.normalized;
            b = b.normalized;
            float cos = Mathf.Clamp(Vector3.Dot(a, b), -1f, 1f);
            float om = Mathf.Acos(cos);
            if (om < 1e-6f) return a;
            float s = Mathf.Sin(om);
            return a * (Mathf.Sin((1 - t) * om) / s) + b * (Mathf.Sin(t * om) / s);
        }

        /// <summary>Winkel zwischen Richtungen im Bogenmaß (mathutils Vector.angle).</summary>
        public static float Angle(Vector3 a, Vector3 b) => Mathf.Acos(Mathf.Clamp(Vector3.Dot(a.normalized, b.normalized), -1f, 1f));

        /// <summary>Starre Blender-Matrix → Unity (M · B · Mᵀ); Lage und Drehung für Transform.localPosition/localRotation.</summary>
        public static void ToUnity(Matrix4x4 axes, Matrix4x4 b, out Vector3 pos, out Quaternion rot)
        {
            var u = axes * b * axes.transpose;
            pos = u.GetColumn(3);
            rot = QuatFrom(u);
        }

        public static Vector3 PointToUnity(Matrix4x4 axes, Vector3 b) => axes.MultiplyVector(b);
    }
}
