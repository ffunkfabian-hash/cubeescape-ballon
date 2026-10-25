// Kleiner JSON-Leser für das Szenenformat ballon-scene/2. JsonUtility kann weder Wörterbücher (atlases je Zone) noch Arrays von
// Arrays (course.route) lesen. Ergebnis: Dictionary<string, object>, List<object>, double, string, bool oder null.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace Ballon.Ego
{
    public static class MiniJson
    {
        public static object Parse(string s)
        {
            if (string.IsNullOrWhiteSpace(s)) throw new FormatException("JSON leer");
            int i = 0;
            var v = Value(s, ref i);
            Skip(s, ref i);
            if (i != s.Length) throw Err(s, i, "Text nach dem Wert");
            return v;
        }

        static FormatException Err(string s, int i, string what)
        {
            int line = 1;
            for (int k = 0; k < i && k < s.Length; k++) if (s[k] == '\n') line++;
            return new FormatException($"JSON ungültig (Zeile {line}, Zeichen {i}): {what}");
        }

        static void Skip(string s, ref int i)
        {
            while (i < s.Length && char.IsWhiteSpace(s[i])) i++;
        }

        static object Value(string s, ref int i)
        {
            Skip(s, ref i);
            if (i >= s.Length) throw Err(s, i, "Wert erwartet");
            char c = s[i];
            if (c == '{') return Obj(s, ref i);
            if (c == '[') return Arr(s, ref i);
            if (c == '"') return Str(s, ref i);
            if (Word(s, ref i, "true")) return true;
            if (Word(s, ref i, "false")) return false;
            if (Word(s, ref i, "null")) return null;
            return Num(s, ref i);
        }

        static bool Word(string s, ref int i, string w)
        {
            if (string.CompareOrdinal(s, i, w, 0, w.Length) != 0) return false;
            i += w.Length;
            return true;
        }

        static Dictionary<string, object> Obj(string s, ref int i)
        {
            var d = new Dictionary<string, object>();
            i++;
            Skip(s, ref i);
            if (i < s.Length && s[i] == '}') { i++; return d; }
            while (true)
            {
                Skip(s, ref i);
                if (i >= s.Length || s[i] != '"') throw Err(s, i, "Schlüssel erwartet");
                string k = Str(s, ref i);
                Skip(s, ref i);
                if (i >= s.Length || s[i] != ':') throw Err(s, i, "':' erwartet");
                i++;
                d[k] = Value(s, ref i);
                Skip(s, ref i);
                if (i < s.Length && s[i] == ',') { i++; continue; }
                if (i < s.Length && s[i] == '}') { i++; return d; }
                throw Err(s, i, "',' oder '}' erwartet");
            }
        }

        static List<object> Arr(string s, ref int i)
        {
            var l = new List<object>();
            i++;
            Skip(s, ref i);
            if (i < s.Length && s[i] == ']') { i++; return l; }
            while (true)
            {
                l.Add(Value(s, ref i));
                Skip(s, ref i);
                if (i < s.Length && s[i] == ',') { i++; continue; }
                if (i < s.Length && s[i] == ']') { i++; return l; }
                throw Err(s, i, "',' oder ']' erwartet");
            }
        }

        static string Str(string s, ref int i)
        {
            var b = new StringBuilder();
            i++;
            while (i < s.Length)
            {
                char c = s[i++];
                if (c == '"') return b.ToString();
                if (c != '\\') { b.Append(c); continue; }
                if (i >= s.Length) break;
                char e = s[i++];
                switch (e)
                {
                    case 'n': b.Append('\n'); break;
                    case 't': b.Append('\t'); break;
                    case 'r': b.Append('\r'); break;
                    case 'b': b.Append('\b'); break;
                    case 'f': b.Append('\f'); break;
                    case 'u':
                        if (i + 4 > s.Length || !int.TryParse(s.Substring(i, 4), NumberStyles.HexNumber, CultureInfo.InvariantCulture, out int cp))
                            throw Err(s, i, "\\u braucht 4 Hexziffern");
                        b.Append((char)cp);
                        i += 4;
                        break;
                    default: b.Append(e); break;        // \" \\ \/
                }
            }
            throw Err(s, i, "Zeichenkette nicht beendet");
        }

        static double Num(string s, ref int i)
        {
            int st = i;
            while (i < s.Length && (char.IsDigit(s[i]) || s[i] == '-' || s[i] == '+' || s[i] == '.' || s[i] == 'e' || s[i] == 'E')) i++;
            if (i == st || !double.TryParse(s.Substring(st, i - st), NumberStyles.Float, CultureInfo.InvariantCulture, out double d))
                throw Err(s, st, "Zahl, Zeichenkette, Objekt oder Array erwartet");
            return d;
        }
    }
}
