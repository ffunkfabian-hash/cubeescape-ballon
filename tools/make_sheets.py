"""Konzept- und Baugruppenblätter (HTML, eigenständig mit eingebetteten Bildern) aus Renderings, views.json und Specs.

  python3 tools/make_sheets.py              → <OUT>/sheets/BASIC-NN.html und index.html (vollständig, lokal)
  python3 tools/make_sheets.py --gallery P  → eine kompakte Galerie-Seite P (Formstudie 01 + 17 Karten) zum Veröffentlichen
Alle Bilder stammen aus demselben Modell und denselben Frames (views/, motion/); Maße nur aus dem Spec.
"""
import base64
import glob
import html
import importlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools.paths import OUT, EVIDENCE  # noqa: E402
from basic import matrix  # noqa: E402
from tools.make_docs import shown_actions, static_status  # noqa: E402

E = html.escape
CACHE = os.path.join(OUT, '_webp')

CSS = """
/* Konstruktionsblatt: Schriftfeld rechts oben, große Hauptansicht, Ansichtsraster, Stückliste; Bilder auf hellen Tafeln */
:root{--paper:#E8EBE9;--ink:#1D2226;--muted:#58626A;--rule:#C3CAC7;--plate:#F5F6F4;--plate-ink:#1D2226;
--accent:#C9551A;--signal:#21808E;--chip:#DDE2DF;
--f-display:"Chakra Petch","Avenir Next Condensed","Arial Narrow",sans-serif;--f-body:"IBM Plex Sans","Helvetica Neue",Arial,sans-serif;
--f-mono:"IBM Plex Mono",Menlo,Consolas,monospace;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--paper:#14181A;--ink:#E2E6E4;--muted:#9AA5AA;--rule:#2D3639;
--plate:#DCE0DD;--chip:#232A2D;--accent:#EE7B3C;--signal:#5FCFDC;color-scheme:dark}}
:root[data-theme="dark"]{--paper:#14181A;--ink:#E2E6E4;--muted:#9AA5AA;--rule:#2D3639;--plate:#DCE0DD;--chip:#232A2D;
--accent:#EE7B3C;--signal:#5FCFDC;color-scheme:dark}
body{background:var(--paper);color:var(--ink);font:15px/1.55 var(--f-body);margin:0;
padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
main{max-width:1240px;margin:0 auto;padding-block:28px 64px;display:grid;gap:28px}
h1,h2,h3{font-family:var(--f-display);text-wrap:balance;margin:0;letter-spacing:.01em}
h1{font-size:clamp(28px,4vw,44px);line-height:1.05;font-weight:600}h2{font-size:22px;font-weight:600}h3{font-size:16px;font-weight:600}
p{margin:0;max-width:68ch}.muted{color:var(--muted)}
.eyebrow{font:600 12px/1 var(--f-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent)}
.head{display:grid;grid-template-columns:1fr minmax(260px,360px);gap:24px;align-items:start}
.titleblock{border:1.5px solid var(--ink);display:grid;grid-template-columns:auto 1fr;font:12.5px/1.35 var(--f-mono)}
.titleblock div{padding:5px 9px;border-bottom:1px solid var(--rule)}.titleblock div:nth-child(odd){color:var(--muted);border-right:1px solid var(--rule)}
.titleblock div:nth-last-child(-n+2){border-bottom:0}
figure{margin:0;display:grid;gap:6px}figure .plate{background:var(--plate);border:1px solid var(--rule);position:relative}
figure img,figure svg{display:block;width:100%;height:auto;max-width:100%}figure svg{position:absolute;inset:0;height:100%}
figcaption{font-size:13px;color:var(--muted)}figcaption b{color:var(--ink);font-weight:600}
.grid2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.grid4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}
@media (max-width:760px){.head,.grid2,.grid3{grid-template-columns:1fr}.grid4{grid-template-columns:repeat(2,minmax(0,1fr))}}
.tablewrap{overflow-x:auto;border:1px solid var(--rule)}
table{border-collapse:collapse;width:100%;font-size:13px;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:6px 9px;border-bottom:1px solid var(--rule);vertical-align:top}th{font:600 11.5px/1.3 var(--f-mono);
letter-spacing:.06em;text-transform:uppercase;color:var(--muted);background:var(--chip)}td code,.mono{font-family:var(--f-mono);font-size:12.5px}
.chips{display:flex;flex-wrap:wrap;gap:6px}.chip{font:600 11.5px/1 var(--f-mono);padding:5px 8px;border:1px solid var(--rule);background:var(--chip)}
.chip.ok{border-color:var(--signal);color:var(--signal)}.chip.no{border-color:var(--accent);color:var(--accent)}
.strip{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(150px,1fr);gap:8px;overflow-x:auto}
.strip figure figcaption{font:12px/1.3 var(--f-mono)}
pre.tree{font:12.5px/1.45 var(--f-mono);background:var(--chip);padding:12px 14px;overflow-x:auto;margin:0;border:1px solid var(--rule)}
section{display:grid;gap:14px}a{color:var(--signal)}a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.card{display:grid;gap:10px;padding-block:14px;border-top:1.5px solid var(--ink)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:22px}
.kv{display:flex;flex-wrap:wrap;gap:4px 14px;font:12.5px/1.4 var(--f-mono);color:var(--muted)}.kv b{color:var(--ink);font-weight:600}
"""
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600&family=IBM+Plex+Mono:wght@400;600'
         '&family=IBM+Plex+Sans:wght@400;600&display=swap">')

LABEL_ASM = {'receiver': 'Gehäuse', 'barrel': 'Laufmodul', 'ammo': 'Munition', 'sight': 'Visier', 'grip_controls': 'Griff',
             'support': 'Stützbereich', 'stock': 'Schaft', 'mechanism': 'Mechanik', 'cooling': 'Kühlung', 'blade': 'Klinge',
             'guard': 'Parierblock', 'riser': 'Mittelstück', 'limbs': 'Wurfarme', 'string': 'Sehne', 'arrow': 'Pfeil',
             'shaft': 'Stange', 'shield': 'Schild'}
VIEW_DE = {'hero': 'Dreiviertelansicht rechts vorn', 'side': 'Seite rechts (orthografisch)', 'side_left': 'Seite links, Ego-Seite',
           'top': 'Draufsicht', 'front': 'Vorderansicht', 'rear': 'Rückansicht', 'ego': 'Blick von links hinten oben (Ego-nah)',
           'clay': 'Neutrale Materialansicht', 'silhouette': 'Silhouette rechts', 'exploded': 'Explosionsansicht (grafisch)',
           'sightline': 'Durchblick aus Socket_Eye', 'part_sight': 'Visier einzeln', 'part_ammo': 'Munitionsteil einzeln'}


def webp(png, width, q=80):
    os.makedirs(CACHE, exist_ok=True)
    key = png.replace(OUT, '').strip('/').replace('/', '_')
    out = os.path.join(CACHE, f'{key}_{width}.webp')
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(png):
        subprocess.run(['magick', png, '-resize', f'{width}x', '-quality', str(q), '-define', 'webp:alpha-quality=90', out], check=True)
    return 'data:image/webp;base64,' + base64.b64encode(open(out, 'rb').read()).decode()


def labels_svg(res, pts, ink='#1D2226', accent='#C9551A'):
    """Beschriftung mit Führungslinien: Punkte (Text, x, y) im Bildraster; Texte oben bzw. unten, nach x sortiert."""
    W, H = res
    fs = H * 0.034
    out = [f'<svg viewBox="0 0 {W} {H}" aria-hidden="true">']
    for band, sel in (('top', lambda y: y < H * 0.5), ('bottom', lambda y: y >= H * 0.5)):
        items = sorted([p for p in pts if sel(p[2])], key=lambda p: p[1])
        y_lab = H * 0.07 if band == 'top' else H * 0.95
        last = -1e9
        for txt, x, y in items:
            w = len(txt) * fs * 0.56
            lx = max(x, w / 2 + 6, last + fs * 0.6 + w / 2)
            lx = min(lx, W - w / 2 - 6) if lx + w / 2 > W else lx
            last = lx + w / 2
            ty = y_lab
            out.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{lx:.0f}" y2="{ty + (fs * 0.35 if band == "top" else -fs * 1.05):.0f}" '
                       f'stroke="{accent}" stroke-width="{H * 0.0022:.1f}"/>')
            out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{H * 0.006:.1f}" fill="{accent}"/>')
            out.append(f'<text x="{lx:.0f}" y="{ty:.0f}" text-anchor="middle" font-family="IBM Plex Sans,Helvetica,Arial,sans-serif" '
                       f'font-size="{fs:.0f}" font-weight="600" fill="{ink}">{E(txt)}</text>')
    out.append('</svg>')
    return ''.join(out)


def scalebar_svg(res, ortho, mm=100):
    W, H = res
    px = W / ortho * mm / 1000
    x0, y0 = W * 0.04, H * 0.93
    return (f'<svg viewBox="0 0 {W} {H}" aria-hidden="true"><line x1="{x0:.0f}" y1="{y0:.0f}" x2="{x0 + px:.0f}" y2="{y0:.0f}" '
            f'stroke="#1D2226" stroke-width="{H * 0.006:.1f}"/><text x="{x0:.0f}" y="{y0 - H * 0.02:.0f}" font-family="IBM Plex Mono,Menlo,monospace" '
            f'font-size="{H * 0.035:.0f}" fill="#1D2226">{mm} mm</text></svg>')


def fig(src, alt, caption, overlay='', aspect=None):
    style = f' style="aspect-ratio:{aspect}"' if aspect else ''
    return (f'<figure><div class="plate"{style}><img src="{src}" alt="{E(alt)}" loading="lazy">{overlay}</div>'
            f'<figcaption>{caption}</figcaption></figure>')


def load(wid):
    for f in glob.glob(os.path.join(ROOT, 'basic', 'weapons', 'w*.py')):
        W = importlib.import_module('basic.weapons.' + os.path.basename(f)[:-3])
        if W.META['id'] == wid:
            d = os.path.join(OUT, wid)
            S = json.load(open(os.path.join(d, f'{wid}.spec.json'), encoding='utf-8'))
            V = json.load(open(os.path.join(d, 'views', 'views.json'), encoding='utf-8'))
            return W, S, V, d


def asm_points(W, V, view):
    lab = V['views'][view]['labels']['assemblies']
    return [(LABEL_ASM.get(a, a), *lab[a]) for a in lab]


def view_img(d, V, view, width, caption, labels=None, scale=False):
    png = os.path.join(d, 'views', f'{view}.png')
    if not os.path.exists(png):
        return ''
    res = V['views'][view].get('resolution', V['resolution'])
    ov = ''
    if labels:
        ov = labels_svg(res, labels)
    elif scale and 'ortho_scale' in V['views'][view]:
        ov = scalebar_svg(res, V['views'][view]['ortho_scale'])
    return fig(webp(png, width), f'{VIEW_DE.get(view, view)}', caption, ov, f'{res[0]}/{res[1]}')


def head(W, S, title=None, sub=None):
    m, dm = W.META, S['dimensions']
    tb = [('Blatt', m['id']), ('Typ', f"{m['type_de']} · {m['type_en']}"), ('Entwurf', f"„{m['name']}“"),
          ('Maße (Modell)', f"L {dm['length_m'] * 1000:.0f} · H {dm['height_m'] * 1000:.0f} · B {dm['width_m'] * 1000:.0f} mm"),
          ('Bauteile', f"{S['counts']['parts']} in {S['counts']['assemblies']} Baugruppen · {S['counts']['triangles']} Dreiecke"),
          ('Rahmen', 'm · vorn −Y · oben +Z · links +X · Ursprung Socket_Hand'),
          ('Stand', f'Entwurf · {static_status(W)} · Mechanik gesichtet {len(shown_actions(W))}/{len(W.ACTIONS)} · exportiert · '
                    'nicht im Spiel angebunden'),
          ('Datum', '24.10.2026 · cubeescape-ballon 0.1.0')]
    tbh = ''.join(f'<div>{E(k)}</div><div>{E(v)}</div>' for k, v in tb)
    return (f'<header class="head"><div style="display:grid;gap:10px"><span class="eyebrow">BASIC · {E(m["id"])}</span>'
            f'<h1>{E(title or m["type_de"] + " " + chr(8211) + " " + m["name"])}</h1>'
            f'{"<p class=muted>" + E(sub) + "</p>" if sub else ""}<p>{E(m["summary"])}</p></div>'
            f'<div class="titleblock" role="table" aria-label="Schriftfeld">{tbh}</div></header>')


def parts_table(W, S):
    P = {p['id']: p for p in S['parts']}
    rows = []
    for p in W.PARTS:
        s = P[p['id']]
        mv = s['moving']
        mvs = '–'
        if mv:
            if mv['kind'] in ('translate', 'segment'):
                mvs = f"{mv['kind']} {mv['travel_mm']:.0f} mm"
            elif mv['kind'] == 'rotate':
                mvs = f"dreht {mv['range_deg'][0]}…{mv['range_deg'][1]}° um {mv['axis_blender']}"
            else:
                mvs = 'Leuchten'
            mvs += f" · {mv.get('event') or ''}"
        rows.append(f"<tr><td><code>{E(p['id'])}</code></td><td>{E(p['de'])}</td><td>{E(LABEL_ASM.get(p['asm'], p['asm']))}</td>"
                    f"<td>{E(p['mat'])}</td><td class=mono>{'×'.join(f'{v:.0f}' for v in s['size_mm'])}</td><td>{E(mvs)}</td>"
                    f"<td>{E(p.get('iface') or '–')}</td><td>{E(p['func'])}</td></tr>")
    return ('<div class="tablewrap"><table><thead><tr><th>ID</th><th>Bauteil</th><th>Baugruppe</th><th>Material</th>'
            '<th>X×Y×Z mm</th><th>Bewegung</th><th>Schnittstelle</th><th>Funktion</th></tr></thead><tbody>' + ''.join(rows) +
            '</tbody></table></div>')


def anchors_table(S):
    rows = ''.join(f"<tr><td><code>{E(k)}</code></td><td class=mono>{', '.join(f'{v:+.3f}' for v in a['position_m'])}</td>"
                   f"<td>{E(a.get('part') or '–')}</td><td>{E(a.get('note') or '–')}</td></tr>" for k, a in S['anchors'].items())
    return ('<div class="tablewrap"><table><thead><tr><th>Anker</th><th>X, Y, Z (m)</th><th>Teil</th><th>Hinweis</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')


def motion_strips(W, d, width=320):
    out = []
    for act, A in W.ACTIONS.items():
        src = os.path.join(d, 'motion', act)
        frames = sorted(glob.glob(os.path.join(src, '*.png')))
        if not frames:
            continue
        step = A.get('step', 2)
        keys = [0] + [f for f, _ in A.get('events', [])] + [A['frames']]
        names = {f: n for f, n in A.get('events', [])}
        picked = []
        for k in keys:
            fr = min(frames, key=lambda p: abs(int(os.path.basename(p)[:4]) - k))
            if fr not in [x[0] for x in picked]:
                picked.append((fr, k))
        cells = ''.join(fig(webp(fr, width, 72), f"{W.META['id']} {act} Bild {k}",
                            f"Bild {int(os.path.basename(fr)[:4])} · {int(os.path.basename(fr)[:4]) * 1000 / 30:.0f} ms"
                            f"{' · ' + E(names[k]) if k in names else (' · Start' if k == 0 else ' · Ende')}", aspect='854/480')
                        for fr, k in picked[:6])
        clip = os.path.join(EVIDENCE, 'clips', f"{W.META['id']}_{act}.mp4")
        link = f' · <a href="file://{E(clip)}">Clip (MP4)</a>' if os.path.exists(clip) else ''
        out.append(f'<div style="display:grid;gap:8px"><h3>{E(A["de"])} <span class="muted mono">{E(act)} · {A["frames"]} Bilder, '
                   f'{A["frames"] / 30:.2f} s{link}</span></h3><div class="strip">{cells}</div></div>')
    return ''.join(out)


def sheet(wid, full=True):
    W, S, V, d = load(wid)
    m = W.META
    st = matrix.status(m, shown_actions(W), '', defined=list(W.ACTIONS))
    cnt = {k: sum(1 for _, s, _ in st if s == k) for k in ('dargestellt', 'nicht anwendbar', 'offen')}
    hero = view_img(d, V, 'hero', 1400, f"<b>{m['id']} · {VIEW_DE['hero']}.</b> Baugruppen beschriftet; Farben nach Designvertrag.",
                    asm_points(W, V, 'hero'))
    orth = ''.join(view_img(d, V, v, 800, f"<b>{VIEW_DE[v]}.</b> Maßstabsbalken aus dem Modell.", scale=True)
                   for v in ('side', 'side_left', 'top', 'front'))
    check = ''.join(view_img(d, V, v, 800, f"<b>{VIEW_DE[v]}.</b> {txt}") for v, txt in (
        ('silhouette', 'Form muss ohne Farbe tragen.'), ('clay', 'Ohne Material; Flächen und Fugen.'),
        ('ego', 'Sichtbare Seite im Ego-Bild (ohne Hände).'),
        ('sightline', 'Freie Durchsicht entlang der Visierlinie, Mündung unten im Feld.')))
    expl = asm_points(W, V, 'exploded')
    exploded = view_img(d, V, 'exploded', 1400, '<b>Explosionsansicht aus dem Modell.</b> Grafische Auseinanderziehung je Baugruppe; '
                        'der tatsächliche Demontageweg steht in der Bauteilliste (Bewegung/Entnahme).', expl)
    parts = ''.join(view_img(d, V, v, 700, f"<b>{VIEW_DE[v]}.</b> Dieselben Objekte wie in der Hauptansicht, übrige Teile ausgeblendet.")
                    for v in ('part_ammo', 'part_sight'))
    tree = [m['id']]
    for a in W.ASSEMBLIES:
        ps = [p for p in W.PARTS if p['asm'] == a['id']]
        if ps:
            tree.append(f"├─ {a['de']} ({a['en']})")
            tree += [f"│   {'└' if p.get('parent_part') else '├'}─ {p['id']}  {p['de']}" for p in ps]
    body = [head(W, S), hero,
            f'<section><h2>Orthografische Ansichten</h2><div class="grid2">{orth}</div></section>',
            f'<section><h2>Form- und Sichtprüfung</h2><div class="grid2">{check}</div></section>',
            f'<section><h2>Explosionsansicht und Einzelteile</h2>{exploded}<div class="grid2">{parts}</div></section>',
            f'<section><h2>Baugruppenbaum</h2><pre class="tree">{E(chr(10).join(tree))}</pre></section>',
            f'<section><h2>Bauteilliste</h2>{parts_table(W, S)}</section>',
            f'<section><h2>Anker</h2>{anchors_table(S)}</section>']
    if full:
        body.append(f'<section><h2>Bewegungsabläufe der Mechanik</h2><p class="muted">Bildfolgen aus dem Modell, 30 fps; Hände '
                    f'und Arme sind noch nicht dargestellt.</p>{motion_strips(W, d)}</section>')
    body.append(f'<section><h2>Haltungs- und Aktionsmatrix</h2><div class="chips"><span class="chip ok">dargestellt {cnt["dargestellt"]}</span>'
                f'<span class="chip">nicht anwendbar {cnt["nicht anwendbar"]}</span><span class="chip no">offen {cnt["offen"]}</span></div>'
                '<p class="muted">Vollständige Zeilen mit Gründen und Lücken: docs/haltungen.md im Repo.</p></section>')
    return W, S, V, d, '\n'.join(body)


def page(title, body, desc=''):
    return (f'<meta charset="utf-8"><title>{E(title)}</title><meta name="claude:viewport-fit-sides" content="cover"><meta name="description" content="{E(desc)}">'
            f'{FONTS}<style>{CSS}</style><main>{body}</main>')


def formstudie(gallery=False):
    W, S, V, d = load('BASIC-01')
    asm = V['views']['hero']['labels']['assemblies']
    want = [('Gehäuse', 'receiver'), ('Laufmodul', 'barrel'), ('Magazin', 'ammo'), ('Visier', 'sight'), ('Griff', 'grip_controls'),
            ('Schaft', 'stock')]
    pts = [(n, *asm[a]) for n, a in want]
    P = {p['id']: p for p in S['parts']}
    mag, win = P['magazine']['size_mm'], P['sight_frame']['size_mm']
    hero = view_img(d, V, 'hero', 1500, '<b>Montierte Dreiviertelansicht.</b> Baugruppen: Gehäuse, Laufmodul, Magazin, Visier, Griff, Schaft.', pts)
    sep = (view_img(d, V, 'part_ammo', 700, f'<b>Magazin, identisches Objekt.</b> Gemessen {mag[1]:.0f} × {mag[2]:.0f} × {mag[0]:.0f} mm '
                    '(L × H × B, mit Boden und Patrone als Kinder nicht eingerechnet).')
           + view_img(d, V, 'part_sight', 700, f'<b>Reflexvisier, identisches Objekt.</b> Haubenrahmen außen {win[0]:.0f} × {win[2]:.0f} mm '
                      '(B × H, gemessen); freie Durchsicht geprüft.')
           + view_img(d, V, 'silhouette', 700, '<b>Neutrale Seitenansicht (Silhouette).</b> Prüft die Form ohne Farbe.'))
    body = (head(W, S, 'BASIC / Formstudie 01', 'Sturmgewehr') + hero + f'<div class="grid3">{sep}</div>' +
            '<section><h2>Herkunft und Prüfstatus</h2><div class="kv"><span>Quelle <b>Inspiriert von Formgen KG02 „Kantenläufer“</b></span>'
            '<span>Modell <b>basic/weapons/w01_auto_rifle.py</b></span><span>Status <b>Entwurf · ' + E(static_status(W)) + ' · exportiert · '
            'nicht angebunden</b></span></div><p class="muted">Übernommen: lange lesbare Hauptform, Creme/Graphit. Geändert: zweiteiliges '
            'Gehäuse mit Fuge, Graphit an allen Griffflächen, Orange nur an Ladehebel, Feuerwahl und Magazinhalter, keine Leuchtzeichen, '
            'kleines Reflexvisier mit Klemmfuß auf Schiene. Spielasset-Entwurf, keine Fertigungszeichnung; alle Maße aus dem Modell.</p></section>')
    return body


def gallery(path):
    cards = []
    for sp in sorted(glob.glob(os.path.join(OUT, 'BASIC-*', 'BASIC-*.spec.json'))):
        wid = os.path.basename(sp)[:-10]
        W, S, V, d = load(wid)
        m, dm = W.META, S['dimensions']
        st = matrix.status(m, shown_actions(W), '', defined=list(W.ACTIONS))
        off = sum(1 for _, s, _ in st if s == 'offen')
        imgs = (view_img(d, V, 'hero', 900, f"<b>{m['id']}</b> Dreiviertelansicht", asm_points(W, V, 'hero'))
                + f'<div class="grid2">{view_img(d, V, "exploded", 560, "Explosionsansicht")}'
                f'{view_img(d, V, "silhouette", 560, "Silhouette", scale=False)}</div>')
        cards.append(f'<article class="card"><span class="eyebrow">{E(m["id"])} · {E(m["type_en"])}</span>'
                     f'<h2>{E(m["type_de"])} – {E(m["name"])}</h2>{imgs}<p>{E(m["summary"])}</p>'
                     f'<div class="kv"><span>L <b>{dm["length_m"] * 1000:.0f} mm</b></span><span>Teile <b>{S["counts"]["parts"]}</b></span>'
                     f'<span>Dreiecke <b>{S["counts"]["triangles"]}</b></span><span>Mechanik <b>{E(", ".join(W.ACTIONS))}</b></span>'
                     f'<span>Matrix offen <b>{off}</b></span></div></article>')
    body = (formstudie(True) + '<section><span class="eyebrow">Erste Etappe · 17 Grundtypen</span><h2>Die BASIC-Reihe</h2>'
            '<p class="muted">Alle Ansichten aus den Blender-Modellen in cubeescape-ballon 0.1.0. Hände, Ego-Haltungen und Spielanbindung '
            'sind offen; die Mechanik jeder Waffe ist als Bildfolge belegt.</p></section>' + f'<div class="cards">{"".join(cards)}</div>')
    open(path, 'w', encoding='utf-8').write(page('BASIC-Waffenreihe', body, 'Formstudie 01 und 17 BASIC-Grundtypen'))
    print(path, f'{os.path.getsize(path) / 1e6:.1f} MB')


def main(argv):
    if '--gallery' in argv:
        return gallery(argv[argv.index('--gallery') + 1])
    if '--pilot' in argv:
        return pilot(argv[argv.index('--pilot') + 1], *(argv[argv.index('--pilot') + 2:argv.index('--pilot') + 3]))
    dst = os.path.join(OUT, 'sheets')
    os.makedirs(dst, exist_ok=True)
    links = []
    sel = [a for a in argv if a.startswith('BASIC-')]
    for sp in sorted(glob.glob(os.path.join(OUT, 'BASIC-*', 'BASIC-*.spec.json'))):
        wid = os.path.basename(sp)[:-10]
        if sel and wid not in sel:
            continue
        W, S, V, d, body = sheet(wid)
        if wid == 'BASIC-01':
            open(os.path.join(dst, 'BASIC-01-Formstudie.html'), 'w', encoding='utf-8').write(
                page('BASIC Formstudie 01', formstudie(), 'Formstudie 01 Sturmgewehr'))
        open(os.path.join(dst, f'{wid}.html'), 'w', encoding='utf-8').write(page(f'{wid} {W.META["type_de"]}', body))
        links.append(f'<li><a href="{wid}.html">{wid} {E(W.META["type_de"])} – {E(W.META["name"])}</a></li>')
    idx = ('<header><span class="eyebrow">cubeescape-ballon 0.1.0</span><h1>BASIC-Blätter</h1></header>'
           f'<p><a href="BASIC-01-Formstudie.html">BASIC / Formstudie 01</a></p><ul>{"".join(links)}</ul>')
    open(os.path.join(dst, 'index.html'), 'w', encoding='utf-8').write(page('BASIC-Blätter', idx))
    print(f'{len(links)} Blätter in {dst}')


def pilot(path, variant='v2.1'):
    """Vergleichsseite Formstudie 01: v1 (Illustration) gegen den Pilot (Destiny-Detaildichte, AAA-Material, schlicht)."""
    d1, d2 = os.path.join(OUT, 'BASIC-01'), os.path.join(OUT, f'BASIC-01-{variant}')
    S1 = json.load(open(os.path.join(d1, 'BASIC-01.spec.json'), encoding='utf-8'))
    S2 = json.load(open(os.path.join(d2, f'BASIC-01-{variant}.spec.json'), encoding='utf-8'))
    V2 = json.load(open(os.path.join(d2, 'views', 'views.json'), encoding='utf-8'))
    V1 = json.load(open(os.path.join(d1, 'views', 'views.json'), encoding='utf-8'))
    lab = V2['views']['hero']['labels']['assemblies']
    pts = [(LABEL_ASM.get(a, a), *lab[a]) for a in ('receiver', 'barrel', 'ammo', 'sight', 'grip_controls', 'stock', 'support')]
    v2 = lambda v, w, cap, ov='': fig(webp(os.path.join(d2, 'views', f'{v}.png'), w, 90), VIEW_DE.get(v, v), cap, ov,  # noqa: E731
                                     '{}/{}'.format(*V2['views'][v].get('resolution', V2['resolution'])))
    hero1 = fig(webp(os.path.join(d1, 'views', 'hero.png'), 900), 'Formstudie 01 v1', '<b>v1 · Illustration.</b> '
                f"{S1['counts']['parts']} Teile, {S1['counts']['triangles']} Dreiecke, flache Farben mit Kontur.",
                aspect='{}/{}'.format(*V1['resolution']))
    hero2 = v2('hero', 900, f"<b>{variant} · Destiny-Detaildichte, AAA-Material, schlicht.</b> {S2['counts']['parts']} Teile, "
                            f"{S2['counts']['triangles']} Dreiecke, PBR mit Kantenabrieb, ohne Bloom.")
    sk_cells = ''
    for name, de, kind in (('standard', 'Standard', 'Farbe'), ('nacht', 'Nachtschicht', 'Farbe'), ('polar', 'Polar', 'Farbe'),
                           ('kobalt', 'Kobalt', 'Farbe'), ('wueste', 'Wüste', 'Farbe'), ('tarnung', 'Tarnung', 'Textur'),
                           ('gebraucht', 'Gebraucht', 'Textur'), ('eloxal', 'Eloxal', 'Textur')):
        png = os.path.join(d2, 'views', f'skin_{name}_hero.png')
        if os.path.exists(png):
            sk_cells += fig(webp(png, 640, 88), f'Skin {de}', f'<b>{de}</b> · {kind}variante', aspect='16/9')
    rules = ''.join(f'<li><b>{E(a)}</b> {E(b)}</li>' for a, b in (
        ('Drei Detailebenen.', 'Große ruhige Schalen, mittlere Gliederung (Fugen, Stufen, Einsätze), feine Akzente gebündelt an Mechanik und Mündung.'),
        ('Negativraum.', 'Skelettierter Schaft mit Lochgitter, Fenster im Handschutz, Sichtfenster im Magazin.'),
        ('Schichtung.', 'Laufhaube, Seitenpanzer und Deckplatte liegen mit 2–3 mm Stufe auf dem Grundkörper; blanke Zierkanten.'),
        ('Materialbruch.', 'Satinierter Lack mit Kantenabrieb, schwarzes Polymer mit Stippling, eloxierte Einsätze, Messing, Leuchtleiste, Decals.'),
        ('Lesbare Front.', 'Gerändelter Kompensator mit Schlitzen, kannelierter Lauf, sichtbarer Verschluss im Auswurffenster.'),
        ('Schlicht bleibt Leitlinie.', 'Ein Blickfang (Energiekern), ein Grafikelement (Chevronband), eine Schrift; Leuchten nur an drei Funktionen; kein Bloom.')))
    body = (head(load('BASIC-01')[0], S2, f'Formstudie 01 · {variant}', 'Pilot: Destiny-Detaildichte, AAA-Material, schlicht') +
            f'<div class="grid2">{hero1}{hero2}</div>' +
            v2('hero_p', 1500, '<b>Produktansicht.</b> Perspektive 70 mm, grauer Studio-Verlauf, ohne Glanzeffekt.') +
            ('<section><h2>Neu in v2.1</h2><ul style="display:grid;gap:6px;max-width:80ch">'
             '<li><b>Unterteil</b> mit angeformtem Magazintrichter und schräger Front, blanke Einführlippe.</li>'
             '<li><b>Griff</b> mit Fingerauflagen, Handballenwölbung und ausgestelltem Boden.</li>'
             '<li><b>Magazin</b> leicht gekrümmt, Bodenband und Zuführlippen aus Metall.</li>'
             '<li><b>Visierhaube</b> nach vorn verjüngt, blanke Stirnkante.</li>'
             '<li><b>Handschutz</b> nach vorn schmaler, schräge Unterkante, unter der Haube angeschmiegt.</li>'
             '<li>Abrieb an dunklen Teilen halbiert (ruhiger auf Grau).</li></ul></section>'
             if variant == 'v2.1' else '') +
            v2('hero', 1500, '<b>v2 Hauptansicht.</b> Baugruppen beschriftet.', labels_svg(V2['resolution'], pts, ink='#E9ECEF')) +
            '<section><h2>Farb- und Texturvarianten</h2><p class="muted">Gleiche Form, gleiche Bauteile; nur Farben und Oberflächen der '
            'Materialrollen wechseln (Skins in <code>basic/kit.py › SKINS</code>).</p>'
            f'<div class="grid4">{sk_cells}</div></section>' +
            '<section><h2>Gestaltungsregeln v2</h2><p class="muted">Abgeleitet aus Bungie-Inspektionsbildern gewöhnlicher Legendary-Waffen '
            '(Shadow Price, Kibou AR3, Inaugural Address); übernommen werden Prinzipien, keine Formen, Namen oder Logos.</p>'
            f'<ul style="display:grid;gap:6px;max-width:80ch">{rules}</ul></section>' +
            '<section><h2>Ansichten v2</h2><div class="grid2">' +
            v2('side_left', 800, '<b>Linke Seite (Ego-Seite).</b> Anzeige, Leuchtleiste, Ladehebel, Schaftleitung.') +
            v2('ego', 800, '<b>Ego-nahe Ansicht.</b> Haube, Visier und Oberseite.') +
            v2('exploded', 800, '<b>Explosionsansicht.</b> Schichten und Baugruppen getrennt.') +
            v2('clay', 800, '<b>Neutrale Materialansicht.</b> Form ohne Material.') +
            v2('part_ammo', 700, '<b>Magazin einzeln.</b> Rippen, Sichtfenster, Patronen.') +
            v2('part_sight', 700, '<b>Reflexvisier einzeln.</b> Klemmhebel, Verstellung, Batteriedeckel, beschichtetes Glas.') +
            '</div></section>' +
            '<section><h2>Stand</h2><p>Pilot in eigenem Modul (<code>basic/pilot/w01_auto_rifle_v21.py</code>, Vorgänger v2 erhalten); die Reihe ist unverändert. '
            'Mechanik und Anker wie v1. Toolgen-Budgets bewusst ignoriert (Vorgabe des Nutzers). Nach Freigabe folgen die übrigen 16.</p></section>')
    open(path, 'w', encoding='utf-8').write(page('Formstudie 01 v2', body, 'Pilot Destiny-Detaildichte und AAA-Material'))
    print(path, f'{os.path.getsize(path) / 1e6:.1f} MB')


if __name__ == '__main__':
    main(sys.argv[1:])
