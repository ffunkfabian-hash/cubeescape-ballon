"""Haltungs- und Animationsmatrix (reines Python): Zeilen, Anwendbarkeit je Typ, Status je Waffe.

Status-Werte (Auftrag › 7): 'dargestellt', 'nicht anwendbar' (mit Grund), 'offen' (mit konkreter Lücke). Keine leeren Felder.
scope 'weapon' = nur Waffenmechanik nötig (Darstellung ohne Hände vollständig); 'body' = Hände/Arme/Kamera nötig.
layer = Ebene in Cube Escape (Q-CE-07): Posendaten, Clip, prozedural, gemischt.
"""

GUN = {'auto_rifle', 'pulse_rifle', 'scout_rifle', 'hand_cannon', 'sidearm', 'submachine_gun', 'shotgun', 'sniper_rifle',
       'fusion_rifle', 'linear_fusion_rifle', 'trace_rifle', 'grenade_launcher', 'rocket_launcher', 'machine_gun'}
AUTO = {'auto_rifle', 'submachine_gun', 'machine_gun', 'trace_rifle'}
SINGLE = {'scout_rifle', 'hand_cannon', 'sidearm', 'shotgun', 'sniper_rifle', 'grenade_launcher', 'rocket_launcher'}
CHARGE = {'fusion_rifle', 'linear_fusion_rifle'}
CYCLE = {'auto_rifle': 'Ladehebel', 'pulse_rifle': 'Ladehebel', 'scout_rifle': 'Ladehebel', 'hand_cannon': 'Hahn spannen',
         'sidearm': 'Schlitten', 'submachine_gun': 'Ladehebel', 'shotgun': 'Pumpe', 'sniper_rifle': 'Kammerstängel',
         'grenade_launcher': 'Kipplauf', 'rocket_launcher': 'Heckverschluss', 'machine_gun': 'Zuführdeckel/Spannhebel'}
FEED = {'auto_rifle': 'Magazin', 'pulse_rifle': 'Magazin', 'scout_rifle': 'Magazin', 'hand_cannon': 'Trommel (Einzelpatronen)',
        'sidearm': 'Magazin im Griff', 'submachine_gun': 'Magazin im Griff', 'shotgun': 'Einzelpatronen', 'sniper_rifle': 'Magazin',
        'fusion_rifle': 'Energiezelle', 'linear_fusion_rifle': 'Energiezelle', 'trace_rifle': 'Energiezelle (seitlich)',
        'grenade_launcher': 'eine Granate', 'rocket_launcher': 'eine Rakete', 'machine_gun': 'Munitionskasten und Gurt',
        'glaive': 'Energiezelle'}
CE_CLASS = {'auto_rifle': 'rifle', 'pulse_rifle': 'rifle', 'scout_rifle': 'rifle', 'hand_cannon': 'sidearm (Vorschlag)',
            'sidearm': 'sidearm', 'submachine_gun': 'submachine_gun', 'combat_bow': 'keine (Bogen nicht in CE)',
            'shotgun': 'shotgun', 'sniper_rifle': 'sniper', 'fusion_rifle': 'rifle (Annahme, Profil ungeprüft)',
            'linear_fusion_rifle': 'sniper (Vorschlag)', 'trace_rifle': 'rifle (Annahme, Profil ungeprüft)',
            'grenade_launcher': 'heavy (Vorschlag)', 'rocket_launcher': 'heavy', 'machine_gun': 'heavy (Vorschlag)',
            'sword': 'keine (Nahkampfprofil fehlt)', 'glaive': 'keine (Nahkampfprofil fehlt)'}


def _na(reason):
    return ('nicht anwendbar', reason)


def ap_gun(t):
    return None if t in GUN or t == 'glaive' else _na('Typ ohne Schusswaffenablauf (eigene Zeilen für Bogen bzw. Schwert)')


def ap_all(t):
    return None


def ap_aim(t):
    return _na('Schwert hat keinen Zielmodus; Blocken übernimmt die Haltung') if t == 'sword' else None


ROWS = [
    # Grundhaltungen und Bewegung
    ('pose_rest', 'Ruhehaltung', 'Rest pose', 'Grundhaltung', 'body', 'Posendaten', ap_all),
    ('pose_hip', 'Hüftfeuerhaltung', 'Hip pose', 'Grundhaltung', 'body', 'Posendaten',
     lambda t: _na('Schwert: Bereitschaftshaltung statt Hüftfeuer (Zeile sword_ready)') if t == 'sword' else None),
    ('pose_aim', 'Zielhaltung (Visier/Zielfernrohr)', 'Aim pose (ADS)', 'Grundhaltung', 'body', 'Posendaten', ap_aim),
    ('tr_hip_aim', 'Hüfte → Zielen', 'Hip to aim', 'Grundhaltung', 'body', 'Clip', ap_aim),
    ('tr_aim_hip', 'Zielen → Hüfte', 'Aim to hip', 'Grundhaltung', 'body', 'Clip', ap_aim),
    ('pose_lowered', 'Gesenkte Haltung / Wandnähe', 'Lowered / wall', 'Grundhaltung', 'body', 'Posendaten', ap_all),
    ('tr_lowered_return', 'Rückkehr aus gesenkter Haltung', 'Lowered return', 'Grundhaltung', 'body', 'Posendaten', ap_all),
    ('move_walk', 'Gehen', 'Walk', 'Bewegung', 'body', 'prozedural', ap_all),
    ('move_strafe', 'Seitwärts', 'Strafe', 'Bewegung', 'body', 'prozedural', ap_all),
    ('move_back', 'Rückwärts', 'Backward', 'Bewegung', 'body', 'prozedural', ap_all),
    ('sprint_in', 'Sprintbeginn', 'Sprint in', 'Bewegung', 'body', 'Clip', ap_all),
    ('sprint_loop', 'Sprintschleife', 'Sprint loop', 'Bewegung', 'body', 'Posendaten', ap_all),
    ('sprint_out', 'Sprintende', 'Sprint out', 'Bewegung', 'body', 'Clip', ap_all),
    ('crouch', 'Ducken', 'Crouch', 'Bewegung', 'body', 'Posendaten', ap_all),
    ('crouch_move', 'Geduckte Bewegung', 'Crouch move', 'Bewegung', 'body', 'prozedural', ap_all),
    ('jump_start', 'Sprungbeginn', 'Jump start', 'Bewegung', 'body', 'prozedural', ap_all),
    ('air', 'Luftphase', 'Air', 'Bewegung', 'body', 'Posendaten', ap_all),
    ('land', 'Landung', 'Land', 'Bewegung', 'body', 'prozedural', ap_all),
    ('slide', 'Rutschen', 'Slide', 'Bewegung', 'body', '–',
     lambda t: _na('kein Zustand in CE `EquipmentPoseState.cs` (Walk, Sprint, Crouch, Air, Lowered; Q-CE-07)')),
    ('climb', 'Klettern', 'Climb', 'Bewegung', 'body', '–',
     lambda t: _na('kein Zustand in CE `EquipmentPoseState.cs` (Q-CE-07)')),
    ('sway', 'Nachschwingen beim Umsehen', 'Look sway', 'Bewegung', 'body', 'prozedural', ap_all),
    ('inertia', 'Bewegungsträgheit', 'Inertia', 'Bewegung', 'body', 'prozedural', ap_all),
    ('regrip', 'Griffkorrektur', 'Regrip', 'Bewegung', 'body', 'gemischt', ap_all),
    # Waffenaktionen
    ('draw', 'Ziehen', 'Draw', 'Aktion', 'body', 'Clip', ap_all),
    ('ready', 'Einsatzbereitschaft', 'Ready', 'Aktion', 'body', 'Posendaten', ap_all),
    ('holster', 'Wegstecken', 'Holster', 'Aktion', 'body', 'Clip', ap_all),
    ('switch', 'Waffenwechsel', 'Switch', 'Aktion', 'body', 'gemischt', ap_all),
    ('fire_single', 'Einzelschuss', 'Single shot', 'Aktion', 'weapon', 'Clip',
     lambda t: None if t in SINGLE or t == 'glaive' else _na('anderer Feuermodus (Salve, Dauerfeuer, Aufladen oder Nahkampf)')),
    ('fire_burst', 'Salve', 'Burst', 'Aktion', 'weapon', 'Clip',
     lambda t: None if t == 'pulse_rifle' else _na('nur das Impulsgewehr feuert Salven (Burst-Rahmen anderer Typen zurückgestellt, EXT-12)')),
    ('fire_auto', 'Dauerfeuer / Dauerstrahl', 'Full auto / beam', 'Aktion', 'weapon', 'Clip',
     lambda t: None if t in AUTO else _na('kein Dauerfeuer bei diesem Typ')),
    ('recoil_mech', 'Rückstoß und Mechanik, Rückkehr', 'Recoil and mechanism', 'Aktion', 'body', 'prozedural', ap_gun),
    ('recoil_camera', 'Kamera-Feedback (getrennt)', 'Camera feedback', 'Aktion', 'body', 'prozedural', ap_gun),
    ('charge', 'Aufladen', 'Charge', 'Aktion', 'weapon', 'Clip',
     lambda t: None if t in CHARGE else _na('kein Aufladen bei diesem Typ (Bogen: Auszug in eigenen Zeilen)')),
    ('charge_hold', 'Ladung halten', 'Charge hold', 'Aktion', 'weapon', 'Clip',
     lambda t: None if t in CHARGE else _na('kein Aufladen bei diesem Typ')),
    ('charge_release', 'Ladung auslösen', 'Charge release', 'Aktion', 'weapon', 'Clip',
     lambda t: None if t in CHARGE else _na('kein Aufladen bei diesem Typ')),
    ('charge_cancel', 'Aufladen abbrechen', 'Charge cancel', 'Aktion', 'weapon', 'Clip',
     lambda t: None if t in CHARGE else _na('kein Aufladen bei diesem Typ')),
    ('reload_partial', 'Nachladen mit Restmunition', 'Tactical reload', 'Aktion', 'body', 'Clip',
     lambda t: _na('einschüssig: kein Teilnachladen') if t in ('grenade_launcher', 'rocket_launcher')
     else None if t in GUN or t == 'glaive' else _na('keine nachladbare Munition (Bogen: Pfeil, Schwert: Ladungen)')),
    ('reload_empty', 'Nachladen aus leerem Zustand', 'Empty reload', 'Aktion', 'body', 'Clip', ap_gun),
    ('reload_feed', 'Munitionszufuhr (Magazin, Trommel, Gurt, Zelle, Einzelpatrone)', 'Feed', 'Aktion', 'weapon', 'Clip', ap_gun),
    ('cycle', 'Repetieren / Spannen / Verschluss / Auswurf', 'Cycle action', 'Aktion', 'weapon', 'Clip',
     lambda t: None if t in CYCLE else _na('kein Verschluss zu betätigen (Energiewaffe, Bogen oder Nahkampf)')),
    ('inspect', 'Betrachten', 'Inspect', 'Aktion', 'body', 'Clip', ap_all),
    ('inspect_return', 'Rückkehr aus Betrachten', 'Inspect return', 'Aktion', 'body', 'Clip', ap_all),
    ('displace', 'Verdrängung (Interaktion, Nahkampf, Fähigkeit)', 'Displacement', 'Aktion', 'body', 'gemischt', ap_all),
]
TYPE_ROWS = {
    'combat_bow': [('bow_nock', 'Pfeil auflegen'), ('bow_draw', 'Ausziehen'), ('bow_hold', 'Halten'), ('bow_release', 'Lösen'),
                   ('bow_letdown', 'Entspannen'), ('bow_renock', 'Erneut auflegen')],
    'sword': [('sword_ready', 'Bereitschaft'), ('sword_light', 'Leichter Angriff'), ('sword_heavy', 'Schwerer Angriff'),
              ('sword_combo', 'Kombination'), ('sword_block', 'Blocken'), ('sword_recover', 'Erholung')],
    'glaive': [('glaive_shot', 'Schuss'), ('glaive_reload', 'Nachladen'), ('glaive_shield', 'Schild'),
               ('glaive_melee', 'Stiche/Hiebe'), ('glaive_switch', 'Wechsel zwischen Aktionen')],
}
# Aktion des Waffenmoduls → Matrixzeilen, deren Mechanik sie darstellt
ACTION_ROWS = {
    'fire_auto': ['fire_auto', 'recoil_mech'], 'fire_burst': ['fire_burst', 'recoil_mech'], 'fire_semi': ['fire_single', 'recoil_mech'],
    'fire_da': ['fire_single', 'cycle'], 'fire_pump': ['fire_single', 'cycle'], 'fire_cycle': ['fire_single', 'cycle'],
    'fire': ['fire_single', 'glaive_shot'], 'reload_tactical': ['reload_partial', 'reload_feed'],
    'reload_empty': ['reload_empty', 'reload_feed', 'cycle'], 'reload': ['reload_empty', 'reload_feed', 'glaive_reload'],
    'load_shell': ['reload_feed', 'reload_partial'], 'charge_fire': ['charge', 'charge_hold', 'charge_release'],
    'charge_cancel': ['charge_cancel'], 'beam': ['fire_auto'], 'draw_hold_release': ['bow_draw', 'bow_hold', 'bow_release'],
    'let_down': ['bow_letdown'], 'guard_charge': ['sword_block'], 'shield': ['glaive_shield'],
}

TRANSITIONS = [
    # id, Start → Ende, Auslöser, Priorität (Q-CE-06), Unterbrechung, Ereignisse, Dauer (Quelle)
    ('tr_sprint_aim', 'Sprint → Zielen', 'Zieltaste im Sprint', 'ADS > Sprint', 'Sprint endet sofort', 'SprintOut, Aimed',
     'vorgeschlagen 0,25–0,35 s (ADS-Messungen Q-REF)'),
    ('tr_sprint_fire', 'Sprint → Feuer', 'Abzug im Sprint', 'Fire > Sprint', 'Sprint endet; Feuer nach SprintOut', 'SprintOut, Fire',
     'vorgeschlagen 0,15–0,25 s'),
    ('tr_draw_aimheld', 'Ziehen bei gehaltenem Zielen', 'Wechsel mit gehaltener Zieltaste', 'Draw > ADS', 'Draw nicht unterbrechbar; ADS danach',
     'Ready, Aimed', 'Ziehen gemessen 0,18–0,60 s je Typ (Q-REF)'),
    ('tr_reload_switch', 'Nachladen → Wechsel', 'Waffenwechsel während Reload', 'Holster/Draw > Reload', 'Reload bricht ab (CancelReason Switch)',
     'MagOut ohne MagIn → Magazin bleibt draußen (Regel offen)', 'Holster ab aktueller Stellung (Q-CE-06)'),
    ('tr_reload_cancel', 'Erlaubter Nachladeabbruch', 'Sprint oder Wechsel', 'Reload bis MagIn geschützt', 'nach MagIn gilt Nachladen als erfolgt',
     'MagIn, Chamber', 'abhängig vom Reload-Clip'),
    ('tr_charge_cancel', 'Aufladen abbrechen', 'Abzug loslassen vor Vollladung', 'Fire', 'jederzeit vor Auslösen', 'charge_start, cancel',
     'Fusion: Laden bis Strahl 0,52–0,87 s (Q-REF)'),
    ('tr_inspect_cancel', 'Betrachten abbrechen', 'jede Eingabe', 'Inspect niedrigste Priorität', 'sofort', 'End', 'vorgeschlagen 0,15 s'),
    ('tr_fire_move', 'Feuer während Bewegung', 'Abzug beim Gehen', 'Fire > Walk', 'Bob gedämpft', 'Fire', 'prozedural'),
    ('tr_fire_air', 'Feuer in der Luft', 'Abzug in Luftphase', 'Fire > Air', 'Landefeder läuft weiter', 'Fire', 'prozedural'),
    ('tr_wall', 'Wandabsenkung und Rückkehr', 'Abstand zur Wand unter Waffenlänge', 'Lowered', 'Feuer gesperrt', 'Lowered', 'vorgeschlagen 0,2 s'),
    ('tr_quick_switch', 'Schneller erneuter Wechsel', 'zweiter Wechsel während Draw', 'Holster/Draw', 'Holster ab aktueller Stellung', 'Holstered, Ready',
     'Waffenwechsel V06/V07 (Q-REF)'),
    ('tr_view', 'Ego-/ISO-Wechsel', 'Ansichtswechsel', 'View', 'CancelReason View', '–', 'Schwert: 0,15 + 0,33 s (Q-REF Sword)'),
]


def rows_for(t):
    out = []
    for rid, de, en, cat, scope, layer, ap in ROWS:
        out.append(dict(id=rid, de=de, en=en, cat=cat, scope=scope, layer=layer, na=ap(t)))
    for rid, de in TYPE_ROWS.get(t, []):
        out.append(dict(id=rid, de=de, en=rid, cat='Typaktion', scope='body' if rid not in ('glaive_shield',) else 'weapon',
                        layer='Clip', na=None))
    return out


def status(meta, actions, clips_dir_hint, defined=()):
    """Liste (row, status, detail) für eine Waffe. actions = gesichtete Aktionen (Clip vorhanden und geprüft),
    defined = im Modell definierte Aktionen (Bildfolge ggf. noch nicht gesichtet)."""
    t = meta['type']
    shown = {}
    for a in actions:
        for r in ACTION_ROWS.get(a, []):
            shown.setdefault(r, []).append(a)
    res = []
    for r in rows_for(t):
        if r['na']:
            res.append((r, 'nicht anwendbar', r['na'][1]))
            continue
        acts = shown.get(r['id'])
        if acts and r['scope'] == 'weapon':
            res.append((r, 'dargestellt', f"Mechanik ohne Hände: Aktion {', '.join(acts)} ({clips_dir_hint})"))
        elif acts:
            res.append((r, 'offen', f"Mechanik dargestellt ({', '.join(acts)}); Hand-/Armbewegung fehlt: Ego-Rig liegt in Toolgen, "
                                    'BASIC hat noch keinen Toolgen-Import'))
        elif r['scope'] == 'weapon':
            pend = [a for a in defined if r['id'] in ACTION_ROWS.get(a, [])]
            res.append((r, 'offen', f"Mechanik definiert ({', '.join(pend)}), Clip noch nicht gesichtet" if pend
                        else 'Mechanik dieser Aktion im Modell nicht animiert'))
        elif r['layer'] in ('Posendaten', 'prozedural'):
            res.append((r, 'offen', f"{r['layer']} der CE-Klasse „{CE_CLASS[t]}“ nicht für das BASIC-Modell geprüft "
                                    '(fehlender Import, Q-CE-07)'))
        else:
            res.append((r, 'offen', 'Clip mit Händen nicht erstellt (Toolgen-Ego-Clips, Q-CE-09)'))
    return res
