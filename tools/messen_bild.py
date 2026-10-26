"""Messung am Bild (Patch „messen“, Entscheidungsliste 1a, 1d, 2.1, 3.1): nur Auswertung, ändert keine Werte. Reines Python plus `magick`.

  python3 tools/messen_bild.py grid <in.png> <out.png> [name:x%:y% …]   Mittenkreuz + 10-%-Raster (+ Marken) über ein Standbild
  python3 tools/messen_bild.py ring <rohr_ziel.png> [zeile]             Ring außen / Öffnung an einer Bildzeile (Helligkeitsprofil)
  python3 tools/messen_bild.py key <ordner> [fps]                       Waffenmaske je Bild (Aufnahme mit -ballonKey 1) → Kennzahlen
  python3 tools/messen_bild.py sprint <ordner> <fps> <t0> <t1>          Sprint-Hub (vertikal % H, seitlich % B) und Frequenz aus der Maske
  python3 tools/messen_bild.py zoom <ordner> <fps> <t0> <dauer>         Modell gegen Weltzoom Bild für Bild (zoom.csv + Bildbewegung)

Die Maske ist „nicht die Schlüsselfarbe der Bildecke (Magenta)“ in einem auf 640 × 360 verkleinerten Bild (1 px ≈ 0,16 % B / 0,28 % H).
"""
import csv
import os
import statistics
import subprocess
import sys

W, H = 640, 360


def raw(path):
    d = subprocess.run(['magick', path, '-filter', 'Box', '-resize', f'{W}x{H}!', '-depth', '8', 'rgb:-'], capture_output=True,
                       check=True).stdout
    return d[0::3], d[1::3], d[2::3]


def mask_stats(path):
    r, g, b = raw(path)
    kr, kg, kb = r[0], g[0], b[0]                  # Schlüsselfarbe = Ecke oben links (Magenta nach dem Tonemapping)
    sx = sy = n = 0
    x0 = y0 = 10 ** 6
    x1 = y1 = -1
    for i in range(W * H):
        if abs(r[i] - kr) < 14 and abs(g[i] - kg) < 14 and abs(b[i] - kb) < 14:
            continue
        x, y = i % W, i // W
        sx += x
        sy += y
        n += 1
        x0, x1, y0, y1 = min(x0, x), max(x1, x), min(y0, y), max(y1, y)
    if not n:
        return None
    return dict(cx=sx / n / W * 100, cy=sy / n / H * 100, x0=x0 / W * 100, x1=(x1 + 1) / W * 100, y0=y0 / H * 100,
                y1=(y1 + 1) / H * 100, area=n / (W * H) * 100)


def frames(d):
    return sorted(f for f in os.listdir(d) if f[:4].isdigit() and f.endswith('.png'))


def series(d, cache='mask.csv'):
    p = os.path.join(d, cache)
    if os.path.exists(p):
        return [{k: float(v) for k, v in r.items()} for r in csv.DictReader(open(p))]
    rows = []
    for i, f in enumerate(frames(d)):
        s = mask_stats(os.path.join(d, f)) or {}
        rows.append(dict(i=i, **s))
    keys = list(rows[0])
    with open(p, 'w', newline='') as fh:
        w = csv.DictWriter(fh, keys)
        w.writeheader()
        w.writerows(rows)
    return rows


def peaks(v, t, minsep):
    """lokale Maxima/Minima mit Mindestabstand; liefert (Index, Wert, Art)."""
    sm = [statistics.mean(v[max(0, i - 1):i + 2]) for i in range(len(v))]
    out = []
    for i in range(2, len(sm) - 2):
        if sm[i] >= max(sm[i - 2:i + 3]) and sm[i] > min(sm[i - 2:i + 3]) + 1e-9:
            k = 'max'
        elif sm[i] <= min(sm[i - 2:i + 3]) and sm[i] < max(sm[i - 2:i + 3]) - 1e-9:
            k = 'min'
        else:
            continue
        if out and out[-1][2] == k:
            if (k == 'max') == (sm[i] > out[-1][1]):
                out[-1] = (i, sm[i], k)
        elif not out or i - out[-1][0] >= minsep:
            out.append((i, sm[i], k))
    return out


def sprint(d, fps, t0, t1):
    rows = series(d)
    a, b = int(t0 * fps), int(t1 * fps)
    print(f'Sprint {t0}–{t1} s = Bild {a}–{b} bei {fps}/s, {len(frames(d))} Bilder')
    for key, label in (('cy', 'Schwerpunkt vertikal (% H)'), ('y0', 'Oberkante vertikal (% H)'), ('cx', 'Schwerpunkt seitlich (% B)'),
                       ('x0', 'linke Kante seitlich (% B)')):
        v = [r[key] for r in rows][a:b]
        pk = peaks(v, None, int(fps / 3.16 / 3))
        ext = [p for p in pk]
        pp = [abs(ext[i + 1][1] - ext[i][1]) for i in range(len(ext) - 1)]
        per = [(ext[i + 2][0] - ext[i][0]) / fps for i in range(len(ext) - 2) if ext[i][2] == ext[i + 2][2]]
        print(f'  {label}: Extrema {len(ext)}, Spitze-Spitze Median {statistics.median(pp):.2f} (min {min(pp):.2f}, max {max(pp):.2f})'
              f' → Hub ±{statistics.median(pp) / 2:.2f}' + (f', Periode Median {statistics.median(per):.3f} s = {1 / statistics.median(per):.2f} Hz'
                                                            if per else ''))
        print('    Bilder der Extrema:', ' '.join(f'{a + p[0]}{"▲" if p[2] == "max" else "▼"}' for p in ext))


def energy(d, a, b):
    """Bewegung des Modells je Bild: Summe |Bild i − Bild i−1| der Waffenaufnahme (Schlüsselfarbe), auf 0…100 des Maximums normiert."""
    prev = b''.join(map(bytes, zip(*raw(os.path.join(d, frames(d)[a - 1])))))
    out = []
    for i in range(a, b):
        cur = b''.join(map(bytes, zip(*raw(os.path.join(d, frames(d)[i])))))
        out.append(sum(abs(x - y) for x, y in zip(cur, prev)))
        prev = cur
    m = max(out)
    return [v / m * 100 for v in out]


def zoom(d, fps, t0, dur):
    """Modell gegen Weltzoom ab Eingabezeit t0 (s) über dur Sekunden; Weltzoom aus zoom.csv (FOV je Bild), Modell aus der Bildbewegung."""
    import math
    zrows = [list(map(float, r)) for r in csv.reader(open(os.path.join(d, 'zoom.csv')))]
    a, b = int(round(t0 * fps)), int(round((t0 + dur) * fps))
    fov = [r[2] for r in zrows]
    ch = [i for i in range(a, b) if abs(fov[i] - fov[i - 1]) > 1e-4]
    zs, ze = ch[0], ch[-1]
    t = lambda f: math.tan(math.radians(f / 2))
    print(f'Eingabe bei Bild {a} (t={t0} s); Weltzoom Bild {zs}–{ze} (FOV {fov[zs - 1]:.3f}° → {fov[ze]:.3f}°, Zoom x{t(fov[zs - 1]) / t(fov[ze]):.3f})')
    e = energy(d, a, b)
    print('  Modellbewegung (% vom Maximum) je 2 Bilder ab Eingabe:', ' '.join(f'{x:.0f}' for x in e[:60:2]))
    for thr in (5, 10, 20):
        idx = [a + k for k, x in enumerate(e) if x > thr]
        ms, me = idx[0], idx[-1]
        print(f'  Schwelle {thr:>2} %: Modell Bild {ms}–{me} ({(me - ms + 1) / fps * 1000:.0f} ms)  Zoom minus Modell: Start {zs - ms:+d}, '
              f'Ende {ze - me:+d} Bilder')


def grid(src, dst, marks):
    cmd = ['magick', src]
    w, h = map(int, subprocess.run(['magick', 'identify', '-format', '%w %h', src], capture_output=True, text=True).stdout.split())
    for k in range(1, 10):
        x, y = w * k / 10, h * k / 10
        wd = 2 if k == 5 else 1
        col = '#FFFFFF90' if k != 5 else '#FFE000'
        cmd += ['-stroke', col, '-strokewidth', str(wd), '-draw', f'line {x:.1f},0 {x:.1f},{h}', '-draw', f'line 0,{y:.1f} {w},{y:.1f}']
        cmd += ['-stroke', 'none', '-fill', '#FFFFFF', '-pointsize', str(max(12, h // 45)), '-annotate', f'+{x + 3:.0f}+{h // 45 + 2}',
                f'{k * 10}', '-annotate', f'+3+{y - 3:.0f}', f'{k * 10}']
    for m in marks:
        n, x, y = m.split(':')
        px, py = float(x) / 100 * w, float(y) / 100 * h
        cmd += ['-stroke', '#FF2020', '-strokewidth', '2', '-fill', 'none', '-draw', f'circle {px:.1f},{py:.1f} {px + 8:.1f},{py:.1f}',
                '-stroke', 'none', '-fill', '#FF2020', '-pointsize', str(max(14, h // 40)), '-annotate', f'+{px + 12:.0f}+{py - 8:.0f}',
                f'{n} {float(x):.1f}/{float(y):.1f}']
    subprocess.run(cmd + [dst], check=True)


def ring(src, y):
    out = subprocess.run(['magick', src, '-crop', f'{960}x1+0+{y}', '-colorspace', 'Gray', '-depth', '8', 'txt:-'], capture_output=True,
                         text=True).stdout.splitlines()[1:]
    r = [int(ln.split('(')[1].split(',')[0].split(')')[0]) for ln in out]
    bg = r[10]
    xs = [x for x in range(300, 660) if abs(r[x] - bg) > 6]
    dk = [x for x in range(300, 660) if r[x] < 80]
    gl = [x for x in range(dk[0], dk[-1]) if r[x] >= 100]
    o, f, g = xs[-1] - xs[0] + 1, dk[-1] - dk[0] + 1, gl[-1] - gl[0] + 1
    print(f'Zeile {y}: außen {xs[0]}–{xs[-1]} = {o} px; dunkle Innenwand {dk[0]}–{dk[-1]} = {f} px; Glas {gl[0]}–{gl[-1]} = {g} px')
    print(f'  außen ÷ Ringinnenkante {o / f:.2f}; außen ÷ lichtes Glas {o / g:.2f}; außen {o / 9.6:.1f} % B, Innenkante {f / 9.6:.1f} % B')


if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'grid':
        grid(sys.argv[2], sys.argv[3], sys.argv[4:])
    elif c == 'ring':
        ring(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 270)
    elif c == 'key':
        series(sys.argv[2])
    elif c == 'sprint':
        sprint(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]))
    elif c == 'zoom':
        zoom(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]))
