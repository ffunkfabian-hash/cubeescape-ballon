"""Exportiert den Absehen-Katalog (basic/reticles.py) für die Laufzeit und erzeugt die Doku.

  python3 tools/export_reticles.py          → data/reticles.json, docs/absehen.md
  python3 tools/export_reticles.py --check  → Exit 1, wenn eine der Dateien veraltet ist (Teil von ./check)

JSON-Format `cubeescape-ballon/reticles` Version 1: Grundelemente in mm auf der Scheibe bei Größe 1,0 (Zielpunkt 0,0; x links,
u oben), Spreizrichtungen, Farben (sRGB-Hex), Linienstärken (Faktor auf LINE_R), Glasvarianten, Aufgehprofile, Vorgaben je
Waffentyp, Spieleroptionen. Unity zeichnet daraus Visierabsehen und Hüft-Fadenkreuz prozedural.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from basic import reticles as RT  # noqa: E402

JS = os.path.join(ROOT, 'data', 'reticles.json')
MD = os.path.join(ROOT, 'docs', 'absehen.md')


def data():
    return dict(format='cubeescape-ballon/reticles', format_version=1, units='mm auf der Scheibe bei Größe 1,0; x links, u oben',
                line_radius_mm=RT.LINE_R,
                reticles={k: dict(de=R['de'], en=R['en'], use=R['use'], prims=R['prims']) for k, R in RT.RETICLES.items()},
                colors={k: dict(de=v[0], hex=v[1], note=v[2]) for k, v in RT.COLORS.items()},
                weights={k: dict(de=v[0], factor=v[1]) for k, v in RT.WEIGHTS.items()},
                glass={k: dict(de=v[0], note=v[1]) for k, v in RT.GLASS.items()},
                spread=RT.SPREAD, defaults=RT.DEFAULTS, settings=RT.SETTINGS, sight_standard=RT.SIGHT, class_zoom=RT.CLASS_ZOOM,
                world_zoom={k: {s: RT.world_zoom(k, s) for s in ('reflex', 'scope')} for k in RT.CLASS_ZOOM},
                sight_kind=RT.SIGHT_KIND, sight_kind_de={str(k): v for k, v in RT.SIGHT_KIND_DE.items()}, ads_feedback=RT.ADS_FEEDBACK,
                spread_model='s ← base(+move) + (s − base)·exp(−dt/recover_s); je Schuss s ← min(max, s + per_shot); '
                             'beim Zielen s·ads; Linien wandern um s·d, Ringe wachsen um s·grow, Punkte bleiben')


def doc():
    L = ['# Absehen, Visierglas und Visier-Standard', '',
         '> Erzeugt aus `basic/reticles.py` mit `python3 tools/export_reticles.py` – nicht von Hand ändern.', '',
         'Eine Quelle für Blender (`basic/common.reticle`, Familienvisier `reflex_sight_v21`) und die Laufzeit (`data/reticles.json`). '
         'Katalogblatt: `python3 tools/reticle_sheet.py --sheet` (Belege `reticles.png`, Clip `clips/reticle_spread.mp4`).', '',
         '## Formen', '', '| ID | Name | Einsatz | Aufgehen |', '|---|---|---|---|']
    for k, R in RT.RETICLES.items():
        moves = any((p['t'] == 'line' and p['d'] != (0, 0)) or (p['t'] == 'ring' and p['grow']) for p in R['prims'])
        L.append(f"| `{k}` | {R['de']} | {R['use']} | {'ja' if moves else 'nein'} |")
    L += ['', 'Jede Form gibt es in jeder Farbe und jeder Linienstärke.', '', '## Farben', '', '| ID | Name | Hex | Hinweis |', '|---|---|---|---|']
    L += [f'| `{k}` | {v[0]} | `{v[1]}` | {v[2]} |' for k, v in RT.COLORS.items()]
    L += ['', '## Linienstärken', '', '| ID | Name | Faktor |', '|---|---|---|']
    L += [f'| `{k}` | {v[0]} | {v[1]} (Linie r = {RT.LINE_R * v[1]:.2f} mm) |' for k, v in RT.WEIGHTS.items()]
    L += ['', '## Glasvarianten (dezent)', '', '| ID | Name | Wirkung |', '|---|---|---|']
    L += [f'| `{k}` | {v[0]} | {v[1]} |' for k, v in RT.GLASS.items()]
    L += ['', '## Aufgehen beim Schießen', '', 'Spreizung s in mm auf der Scheibe (Größe 1,0): '
          'Abklingen zur Basis mit Zeitkonstante, Impuls je Schuss bis zum Maximum, Laufen addiert, Zielen multipliziert.', '',
          '| Profil | Name | Basis | je Schuss | Maximum | Abklingen | Laufen | Zielen |', '|---|---|---|---|---|---|---|---|']
    L += [f"| `{k}` | {S['de']} | {S['base']} | {S['per_shot']} | {S['max']} | {S['recover_s']} s | {S['move']} | ×{S['ads']} |"
          for k, S in RT.SPREAD.items()]
    L += ['', 'Profil `charge`: während des Aufladens schrumpft die Spreizung von `charge_from` auf die Basis.', '',
          '## Vorgabe je Waffentyp', '', '| Typ | Visier | Hüfte | Aufgehen |', '|---|---|---|---|']
    L += [f"| `{k}` | {('`' + v['optic'] + '`') if v['optic'] else '–'} | `{v['hip']}` | `{v['spread']}` |" for k, v in RT.DEFAULTS.items()]
    S = RT.SIGHT
    L += ['', '## Visier-Standard', '',
          f"Visierhöhe (Socket_Eye über der Laufachse) {S['height_mm']:.0f} ± {S['height_tol_mm']:.0f} mm. Socket_Eye ist der Augenpunkt "
          'beim Zielen, gemessen ab der vorderen Visieröffnung. Das Waffenmodell wird nicht vergrößert '
          f"(Viewmodel-Zoom ×{S['viewmodel_zoom']}); nur die Welt zoomt ({S['zoom_kind']}: tan(Bildwinkel/2) geteilt durch den Zoom), "
          f"Bezugsbildwinkel {S['fov_ref_deg']:.0f}° horizontal. Eine Kamera: das Glas zeigt dasselbe Weltbild; Teile mit `ads_hide` "
          '(Zielfernrohr-Rohr, Okular, Türme) sind beim Zielen ausgeblendet. Geprüft in `./check`. Herleitung: Destiny-Video, '
          'Motiongen-Messungen und REF 0.14 „Eyebox“ (`cubeescape-reference/docs/visiere.md`).', '',
          '| Visiertyp | Name | Augenabstand | gemessen ab | Visierbonus | Öffnung im Zielen (% Bildbreite) | Rahmen höchstens | Zielbild |',
          '|---|---|---|---|---|---|---|---|']
    for k, T in S['types'].items():
        if 'eye_relief_mm' in T:
            L.append(f"| `{k}` | {T['de']} | {T['eye_relief_mm']:.0f} mm | `{T['ref']}` | +{T['zoom_bonus']} | "
                     f"{T['target_share'][0] * 100:.0f}–{T['target_share'][1] * 100:.0f} % | {T['frame_max']} × Öffnung | {T['ads_view']} |")
        else:
            L.append(f"| `{k}` | {T['de']} | – | – | – | – | – | {T['ads_view']}: {T['note']} |")
    L += ['', '| Waffentyp | Visier (Designsprache v3) | Grundzoom | Status | Weltzoom Reflex | Weltzoom Zielfernrohr |', '|---|---|---|---|---|---|']
    L += [f"| `{k}` | {RT.SIGHT_KIND_DE[RT.SIGHT_KIND[k]]} | ×{z} | {RT.CLASS_ZOOM_STATUS.get(k, 'entworfen')} | "
          f"×{RT.world_zoom(k, 'reflex')} | ×{RT.world_zoom(k, 'scope')} |" for k, z in RT.CLASS_ZOOM.items()]
    F = RT.ADS_FEEDBACK
    L += ['', f"Im Zielen: Leuchtpunkt am Zielpunkt getrennt vom Glas ({F['hud_dot']['share_h'] * 100:.1f} % Bildhöhe), "
          f"kein Aufgehen (×{F['spread_in_ads']}), Schuss = kurzer Ring ({F['shot_ring']['share_h'] * 100:.0f} % Höhe, "
          f"{F['shot_ring']['frames']} Bild), Treffer = X ({F['hit_x']['share_h'] * 100:.1f} % Höhe, ≥ {F['hit_x']['min_s']} s)."]
    L += ['', '## Spieleroptionen', '', '| Option | Name | Werte | Vorgabe |', '|---|---|---|---|']
    for k, S in RT.SETTINGS.items():
        vals = ', '.join(f'`{v}`' for v in S['values']) if 'values' in S else f"{S['min']} – {S['max']}"
        L.append(f"| `{k}` | {S['de']} | {vals} | {S['default']} |")
    return '\n'.join(L) + '\n'


def main(check=False):
    want = {JS: json.dumps(data(), ensure_ascii=False, indent=1) + '\n', MD: doc()}
    stale = [p for p, txt in want.items() if not os.path.exists(p) or open(p, encoding='utf-8').read() != txt]
    if check:
        print('veraltet: ' + ', '.join(os.path.relpath(p, ROOT) for p in stale) if stale else 'Absehen-Export aktuell')
        return 1 if stale else 0
    for p, txt in want.items():
        open(p, 'w', encoding='utf-8').write(txt)
    print('geschrieben:', ', '.join(os.path.relpath(p, ROOT) for p in want))
    return 0


if __name__ == '__main__':
    sys.exit(main('--check' in sys.argv))
