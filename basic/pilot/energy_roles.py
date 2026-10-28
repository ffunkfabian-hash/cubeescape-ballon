"""Leuchtrollen der Energiewaffen v2.1 (0.26 „Kindle“, BASIC-10/11): Ladekern als reine Emission.

Der Ladekern mit der Familienrolle `energy` (beleuchtete Grundfarbe, Stärke 3 × 1,6) bleichte unter AgX zu Weißblau und las sich als
Leuchtröhre (Zwischenstopp, Nutzerwahl „a … Kern weniger grell“). Wie die Portalfarben von BASIC-T01: `emit_only` mit Stärke 0,7 für
Cyan. Die Rolle liegt hier statt in `basic/kit.py`, weil kit.py im Unity-Quellenhash steht (Umzug mit dem Ego-Übertrag); beim
Aufladen setzt die Bewegung `glow` die Leuchtstärke wie bei jeder Anzeige (tools/blender_build.apply_move).
"""
CHARGE_ROLES = {
    'charge_core': dict(color='#5FD3E0', rough=0.3, metal=0.0, emit=0.7, emit_only=True,
                        de='Ladekern Cyan (reine Emission, leuchtet beim Aufladen auf)'),
}
try:                                   # in Blender: Rollen ergänzen (ohne bpy, z. B. ./check, reicht die Tabelle)
    from basic import kit
    for _k, _v in CHARGE_ROLES.items():
        kit.MATERIALS.setdefault(_k, _v)
except ImportError:
    pass
