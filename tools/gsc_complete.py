"""Shader-Zustände für das Aufwärmen vervollständigen (0.38 „Prewarm“).

URP fasst die Durchgänge der Weltkamera je nach Bildinhalt zu verschiedenen nativen Renderpässen zusammen (z. B. mit oder ohne
eigenes Auflöse-Ziel). Eine Aufzeichnung (GraphicsStateCollection, JSON) sieht jede Variante nur in den Pässen, in denen sie dort
zufällig gezeichnet wurde: Im nächsten Lauf kam dieselbe Variante im anderen Pass als Fehlzugriff und Hänger wieder (diag_mit:
MP-Wechsel 100 ms, 4 von 4 Spitzen > 50 ms mit neuem Zustand). Darum gilt: Pässe mit gleichem ersten Ziel (Format, Abtastung,
Laden/Speichern) sind eine Familie; jeder aufgezeichnete Zustand (Netzformat, Renderzustand) wird für alle Pässe seiner Familie ergänzt.

    python3 tools/gsc_complete.py <datei.graphicsstate> [--check]     # ergänzen (schreibt die Datei) bzw. nur prüfen (Exit 1)
    python3 tools/gsc_complete.py <datei> --merge <fehlzugriffe.graphicsstate>   # Fehlzugriffe eines Laufs dazunehmen, dann ergänzen
"""
import json
import sys


def _family(rp):
    """Erstes Ziel des Passes (Format, Abtastung, Laden/Speichern): Pässe mit gleichem Hauptziel zeichnen dieselben Objekte."""
    return json.dumps(rp['attachments'][0], sort_keys=True)


def complete(d):
    """Ergänzt fehlende Zustände je Familie in d (geladenes JSON); gibt die Zahl der neuen Zustände zurück."""
    fam = {}
    for e in d['m_RenderPassInfoMap']:
        fam.setdefault(_family(e['second']), []).append(e['first'])
    of = {h: k for k, hs in fam.items() for h in hs}
    added = 0
    for v in d['m_VariantInfoMap']:
        states = v['second']['graphicsStateInfoSet']
        have = {json.dumps(s, sort_keys=True) for s in states}
        for s in list(states):
            for rp in fam.get(of.get(s['renderPass']), []):
                t = dict(s, renderPass=rp)
                key = json.dumps(t, sort_keys=True)
                if key not in have:
                    have.add(key)
                    states.append(t)
                    added += 1
    return added


def merge(d, extra):
    """Varianten, Netzformate, Pässe und Renderzustände aus extra (Fehlzugriffe eines Laufs) übernehmen."""
    n = 0
    for k in ('m_VertexLayoutInfoMap', 'm_RenderPassInfoMap', 'm_RenderStateMap'):
        known = {e['first'] for e in d[k]}
        d[k] += [e for e in extra[k] if e['first'] not in known]
    var = {json.dumps(v['first'], sort_keys=True): v for v in d['m_VariantInfoMap']}
    for v in extra['m_VariantInfoMap']:
        key = json.dumps(v['first'], sort_keys=True)
        if key not in var:
            var[key] = v
            d['m_VariantInfoMap'].append(v)
            n += len(v['second']['graphicsStateInfoSet'])
            continue
        mine = var[key]['second']['graphicsStateInfoSet']
        have = {json.dumps(s, sort_keys=True) for s in mine}
        for s in v['second']['graphicsStateInfoSet']:
            if json.dumps(s, sort_keys=True) not in have:
                mine.append(s)
                n += 1
    return n


def count(d):
    return sum(len(v['second']['graphicsStateInfoSet']) for v in d['m_VariantInfoMap'])


def main(argv):
    path = argv[0]
    d = json.load(open(path, encoding='utf-8'))
    before = count(d)
    merged = 0
    if '--merge' in argv:
        merged = merge(d, json.load(open(argv[argv.index('--merge') + 1], encoding='utf-8')))
    added = complete(d)
    if '--check' in argv:
        if added:
            print(f'{path}: {added} Zustände fehlen in ihrer Pass-Familie – python3 tools/gsc_complete.py {path}')
            return 1
        print(f'{path}: vollständig ({before} Zustände, {len(d["m_VariantInfoMap"])} Varianten)')
        return 0
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=4)                     # wie Unity: 4 Leerzeichen, ohne Zeilenende am Schluss
    print(f'{path}: {before} → {count(d)} Zustände ({merged} aus Fehlzugriffen, {added} je Pass-Familie ergänzt)')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
