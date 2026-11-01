"""Tabelle der Ruckelmessung (0.37 „Steadyframe“) aus `unity_run.py ruckeln`: je Durchgang (1 = erster Einsatz, 2 = Wiederholung)
und Ereignis Bildzeit p50/p95/p99/max, GC-Speicher je Bild, GC-Läufe, Bilder > 25 ms und Anteil der Bilder neben dem
Anzeigetakt (±2 ms: ungleichmäßige Bewegung); dazu die zehn größten Spitzen mit Waffe.
Mit spikes.json (Lauf mit „profil“) je Spitze die teuersten Proben und Speicherquellen.

  python3 tools/stutter_report.py <Ordner> [<Ordner> …]      # mehrere Ordner: Läufe zusammengefasst (abwechselnde Messung)
  python3 tools/stutter_report.py --weapons <Ordner>          # zusätzlich je Waffe und Ereignis
"""
import csv
import json
import os
import sys

SPIKE_MS = 25.0
FRAME_MS = 1000 / 60      # Bildtakt des Messrechners (VSync); main() setzt ihn aus frames.json › refresh_hz, 60 Hz ist der Rückfallwert
EVENTS = ['start', 'wechsel', 'huefte', 'dauerfeuer', 'zielen', 'nachladen', 'bewegen']
PROJECTILE = {'grenade_launcher', 'rocket_launcher', 'combat_bow'}


def load(dirs):
    rows = []
    for d in dirs:
        with open(os.path.join(d, 'frames.csv')) as f:
            miss = 0
            for r in csv.DictReader(f):
                m = int(r.get('warmup_miss') or 0)       # 0.38: Zustände außerhalb der Aufwärm-Sammlung, kumuliert
                r['miss_new'] = m - miss
                miss = m
                r['dt_unity'] = float(r['dt_ms'])
                r['dt_ms'] = float(r['real_ms']) if r.get('real_ms') else r['dt_unity']   # 0.38: Echtzeit je Bild, sonst Unitys Wert
                r['gc_alloc_b'] = int(r['gc_alloc_b'])
                r['gc_collect'] = int(r['gc_collect'])
                r['run'] = os.path.basename(d.rstrip('/'))
                rows.append(r)
    return rows


def pct(v, q):
    v = sorted(v)
    return v[min(len(v) - 1, int(q * len(v)))] if v else float('nan')


def stats(rs):
    dt = [r['dt_ms'] for r in rs]
    return {'n': len(rs), 'p50': pct(dt, .5), 'p95': pct(dt, .95), 'p99': pct(dt, .99), 'max': max(dt) if dt else float('nan'),
            'gc_kb': sum(r['gc_alloc_b'] for r in rs) / max(1, len(rs)) / 1024, 'gc_runs': sum(r['gc_collect'] for r in rs),
            'spikes': sum(1 for x in dt if x > SPIKE_MS), 'jitter': 100 * sum(1 for x in dt if abs(x - FRAME_MS) > 2) / max(1, len(dt))}


def table(rows, key, label):
    print(f'| {label} | Bilder | p50 ms | p95 ms | p99 ms | max ms | GC KB/Bild | GC-Läufe | > 25 ms | Takt ±2 ms verfehlt |')
    print('|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|')
    groups = {}
    for r in rows:
        groups.setdefault(key(r), []).append(r)
    for k in sorted(groups, key=lambda k: [str(x) for x in k] if isinstance(k, tuple) else str(k)):
        s = stats(groups[k])
        name = ' · '.join(str(x) for x in k) if isinstance(k, tuple) else k
        print(f"| {name} | {s['n']} | {s['p50']:.1f} | {s['p95']:.1f} | {s['p99']:.1f} | {s['max']:.1f} | {s['gc_kb']:.2f} | "
              f"{s['gc_runs']} | {s['spikes']} | {s['jitter']:.1f} % |")


def ev_name(r):
    e = r['event']
    if e in ('huefte', 'dauerfeuer') and r['type'] in PROJECTILE:
        return e + ' (Pfeil/Rakete/Granate)'
    return e


def runs(dirs, rows):
    """Je Lauf: Ladezeit bis zum ersten Bild, Shader-Aufwärmen (0.38) und die großen Bilder."""
    print('### Je Lauf\n')
    print('| Lauf | Bildzeit aus | erstes Bild s | Ruhe max ms | Aufwärmen | fertig s (Dauer) | Zustände | Fehlzugriffe | > 25 ms | > 50 ms | max ms |')
    print('|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|')
    for d in dirs:
        run = os.path.basename(d.rstrip('/'))
        f = os.path.join(d, 'frames.json')
        m = json.load(open(f)) if os.path.exists(f) else {}
        dt = [r['dt_ms'] for r in rows if r['run'] == run and r['event'] != 'start']    # ab dem ersten Ereignis
        rest = [r['dt_ms'] for r in rows if r['run'] == run and r['event'] == 'start']  # 3 s Ruhe nach dem Laden (erstes Bild inbegriffen)
        warm = m.get('warmup', '–')
        took = m.get('warmup_done_s', -1) - m.get('warmup_started_s', -1)
        done = f"{m['warmup_done_s']:.2f} (+{took:.2f})" if warm == 'on' and m.get('warmup_done_s', -1) >= 0 else '–'
        mine = [r for r in rows if r['run'] == run]
        hz = m.get('refresh_hz', 60) or 60
        stuck = sum(abs(r['dt_unity'] - 1000 / hz) < 0.0005 for r in mine) / max(1, len(mine))   # Unitys Ersatzwert (Fenster verdeckt)
        src = 'Echtzeit' if mine and mine[0].get('real_ms') else 'Unity'
        if stuck > 0.5:
            src += f' (Unity {stuck:.0%} Ersatzwert{"" if src.startswith("Echt") else " – ungültig"})'
        med = sorted(r['dt_ms'] for r in mine)[len(mine) // 2] if mine else 0
        if med > 1.3 * 1000 / hz:                    # Fenster verdeckt oder Bildschirm gesperrt: macOS drosselt das Spiel (0.38: 38 ms im Mittel)
            src += f' – gedrosselt (Median {med:.0f} ms), ungültig'
        print(f"| {run} | {src} | {m.get('first_frame_s', float('nan')):.2f} | {max(rest, default=0):.0f} | {warm} | {done} | {m.get('warmup_states', 0)} | "
              f"{m.get('warmup_misses', 0)} | {sum(x > SPIKE_MS for x in dt)} | {sum(x > 50 for x in dt)} | {max(dt, default=0):.0f} |")
    print()


def main(argv):
    per_weapon = '--weapons' in argv
    dirs = [a for a in argv if not a.startswith('--')]
    rows = [r for r in load(dirs) if r['event'] != 'ende']
    meta = [json.load(open(os.path.join(d, 'frames.json'))) for d in dirs if os.path.exists(os.path.join(d, 'frames.json'))]
    if meta:
        m = meta[0]
        global FRAME_MS
        if m.get('refresh_hz', 0) > 0:
            FRAME_MS = 1000 / m['refresh_hz']
        print(f"Läufe: {', '.join(os.path.basename(d.rstrip('/')) for d in dirs)} · {m['width']}×{m['height']}, {m['gpu']}, "
              f"{m.get('refresh_hz', 0):.0f} Hz, VSync {m['vsync']}, Ziel {m['target_fps']}/s, Profiler {m['profiler']}, Unity {m['unity']}\n")
    runs(dirs, rows)
    for p, title in (('1', 'Durchgang 1 – erster Einsatz'), ('2', 'Durchgang 2 – Wiederholung')):
        if not any(r['pass'] == p for r in rows):     # „einmal“: nur Durchgang 1 (0.38)
            continue
        print(f'### {title}\n')
        table([r for r in rows if r['pass'] == p], ev_name, 'Ereignis')
        print()
    if per_weapon:
        for p in ('1', '2'):
            print(f'### Durchgang {p} je Waffe\n')
            table([r for r in rows if r['pass'] == p and r['event'] != 'start'], lambda r: (f"{int(r['weapon']):02d} {r['type']}", r['event']),
                  'Waffe · Ereignis')
            print()
    top = sorted(rows, key=lambda r: -r['dt_ms'])[:10]
    print('### Größte Bilder\n')
    print('| ms | Durchgang | Waffe | Ereignis | GC KB | GC-Lauf | neue Zustände | Bild | Lauf |')
    print('|---:|---:|---|---|---:|---:|---:|---:|---|')
    for r in top:
        print(f"| {r['dt_ms']:.1f} | {r['pass']} | {int(r['weapon']):02d} {r['type']} | {r['event']} | {r['gc_alloc_b'] / 1024:.1f} | "
              f"{r['gc_collect']} | {r['miss_new']} | {r['frame']} | {r['run']} |")
    for d in dirs:
        f = os.path.join(d, 'spikes.json')
        if not os.path.exists(f):
            continue
        sp = json.load(open(f))
        print(f'\n### Ursachen ({os.path.basename(d.rstrip("/"))}, Profiler, {len(sp)} Bilder ≥ {SPIKE_MS:.0f} ms)\n')
        for s in sorted(sp, key=lambda s: -s['ms'])[:25]:
            main_self = ', '.join(f"{x['name']} {x['self_ms']:.1f}" for x in s.get('main_self', [])[:6])
            print(f"- {s['ms']:.1f} ms · D{s['pass']} W{s['weapon']:02d} {s['event']} · GC {s.get('main_gc_kb', 0):.1f} KB · {main_self}")
            for a in s.get('main_alloc', [])[:3]:
                print(f"    alloc {a['kb']:.1f} KB ×{a['calls']}: {a['path'][-160:]}")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
