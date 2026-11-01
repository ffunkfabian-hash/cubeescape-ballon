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
            for r in csv.DictReader(f):
                r['dt_ms'] = float(r['dt_ms'])
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
    for p, title in (('1', 'Durchgang 1 – erster Einsatz'), ('2', 'Durchgang 2 – Wiederholung')):
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
    print('| ms | Durchgang | Waffe | Ereignis | GC KB | GC-Lauf | Bild | Lauf |')
    print('|---:|---:|---|---|---:|---:|---:|---|')
    for r in top:
        print(f"| {r['dt_ms']:.1f} | {r['pass']} | {int(r['weapon']):02d} {r['type']} | {r['event']} | {r['gc_alloc_b'] / 1024:.1f} | "
              f"{r['gc_collect']} | {r['frame']} | {r['run']} |")
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
