"""Waffenübersicht, Leiste 1–9 und Standard-Skins (0.42 „Quickslot“) – Daten für das Unity-HUD, keine Waffen-IDs.

Nutzerwunsch (03.11.2026, Testbuild 0.41): „Ein passendes HUD mit den Waffen in Kategorien, und unten eine Leiste 1–9, auf die man die
Waffen legen kann. Außerdem die Waffen mit Farben anstelle von Weiß sehen.“ Alles hier hängt an der Waffenklasse (`EGO_PROFILE['type']`
der Module, in ego.json `weapons[].profile.type`); Formgen-Varianten erben die Klasse ihres Grundtyps. tools/export_unity.py schreibt
den Block als `ego.json › hud` (ballon-ego/12), Unity liest ihn (`EgoHud`), `--check` vergleicht.
"""

# Kategorien nach dem Destiny-Prinzip (Primär / Spezial / Schwer, Farbe wie die Munitionsart: weiß, grün, violett); die Portalkanone
# ist ein Werkzeug (Cube Escape) und steht für sich. Reihenfolge der Klassen = Reihenfolge in der Übersicht; Schwert und Glefe gibt es
# als Spielwaffe noch nicht (Formgen-Typen), sie stehen für spätere Varianten schon in ihrer Kategorie.
CATEGORIES = [
    dict(id='primary', de='Primär', color='#E8ECEF',
         classes=['auto_rifle', 'pulse_rifle', 'scout_rifle', 'hand_cannon', 'sidearm', 'submachine_gun', 'combat_bow']),
    dict(id='special', de='Spezial', color='#6FD68C',
         classes=['shotgun', 'sniper_rifle', 'fusion_rifle', 'grenade_launcher', 'trace_rifle']),
    dict(id='heavy', de='Schwer', color='#B48CF2',
         classes=['rocket_launcher', 'machine_gun', 'linear_fusion_rifle', 'sword', 'glaive']),
    dict(id='tool', de='Werkzeug', color='#5FD3E0', classes=['portal_cannon']),
]

# Standardbelegung der Leiste (Tasten 1–9): je Platz eine Klasse, belegt mit der ersten Waffe dieser Klasse in ego.json (BALLONs Waffen
# vor den Formgen-Varianten). Gemischt wie ein Destiny-Loadout; die Portalkanone bleibt auf 5 wie seit 0.22.
HOTBAR = ['auto_rifle', 'pulse_rifle', 'hand_cannon', 'scout_rifle', 'portal_cannon', 'shotgun', 'sniper_rifle', 'fusion_rifle',
          'rocket_launcher']

# Farbiger Standard-Skin je Klasse statt Cremeweiß (Namen aus kit.SKINS; Polar und Gebraucht sind hell bzw. creme und taugen nicht als
# „Farbe statt Weiß“). Fünf Farben für 16 Klassen: in der Übersicht (Klassen in der Reihenfolge von CATEGORIES, Varianten hinter ihrem
# Grundtyp) und auf der Standardleiste haben Nachbarn verschiedene Farben. Formgen-Varianten starten mit dem Skin ihrer Linie (ihr
# Atlas, ego.json › origin.skin).
DEFAULT_SKIN = {
    'auto_rifle': 'kobalt', 'submachine_gun': 'nacht', 'scout_rifle': 'tarnung', 'pulse_rifle': 'wueste', 'hand_cannon': 'eloxal',
    'sidearm': 'kobalt', 'combat_bow': 'wueste',
    'sniper_rifle': 'tarnung', 'trace_rifle': 'wueste', 'shotgun': 'eloxal', 'fusion_rifle': 'kobalt', 'grenade_launcher': 'nacht',
    'machine_gun': 'tarnung', 'linear_fusion_rifle': 'kobalt', 'rocket_launcher': 'wueste',
    'sword': 'nacht', 'glaive': 'eloxal',
    'portal_cannon': 'nacht',
}

SRC = ('Nutzer 03.11.2026 (Testbuild 0.41): Kategorien, Leiste 1–9, Farben statt Weiß; Kategorien nach Destiny (Primär/Spezial/Schwer), '
       'Portalkanone als Werkzeug; Standard-Skins E (gut unterscheidbar, aus kit.SKINS)')


def hud_data(classes=(), skins=()):
    """Block `ego.json › hud`. classes: Klassen der exportierten Waffen – jede muss genau einer Kategorie angehören; skins: Namen aus
    kit.SKINS (kit braucht bpy, der Export liest sie als Literal) – sonst ValueError."""
    seen = {}
    for c in CATEGORIES:
        for k in c['classes']:
            if k in seen:
                raise ValueError(f'Klasse {k} in zwei Kategorien ({seen[k]}, {c["id"]})')
            seen[k] = c['id']
    missing = sorted(set(classes) - set(seen))
    if missing:
        raise ValueError(f'Klassen ohne Kategorie: {", ".join(missing)} (basic/loadout.py › CATEGORIES)')
    bad = sorted(k for k in HOTBAR if k not in seen) + sorted(f'{k}:{s}' for k, s in DEFAULT_SKIN.items() if s not in skins)
    if bad or len(HOTBAR) != 9:
        raise ValueError(f'Leiste braucht 9 bekannte Klassen, Skins aus kit.SKINS: {", ".join(bad) or len(HOTBAR)}')
    return dict(categories=[dict(c) for c in CATEGORIES], hotbar=list(HOTBAR),
                default_skin=[dict(type=k, skin=s) for k, s in DEFAULT_SKIN.items()], src=SRC)
