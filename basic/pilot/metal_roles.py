"""Materialrollen für große runde Eloxalteile der Familie v2.1 (0.28 „Breech“): Trommel des Granatwerfers, Schellen des Raketenwerfers.

Feine Kratzer (`kit.SCRATCH`, gestreckte Noise) wirken quer zur Rundung eines metallischen Rings als weiße Sprenkel (Lehre 0.21 am
Visier, Vollrendering 0.28 an Trommel und Schellen). `ring_anod` ist `anodized` ohne feine Kratzer, Skins wie `anodized`. Die Rolle liegt
hier statt in `basic/kit.py`, weil kit.py im Unity-Quellenhash steht (Umzug mit dem Ego-Übertrag), wie `energy_roles.py`.
"""
RING_ROLES = {
    'ring_anod': dict(color='#202227', rough=0.4, metal=0.6, skin_as='anodized', de='Eloxiert, rund (ohne feine Kratzer)'),
}
try:                                   # in Blender: Rollen ergänzen (ohne bpy, z. B. ./check, reicht die Tabelle)
    from basic import kit
    for _k, _v in RING_ROLES.items():
        kit.MATERIALS.setdefault(_k, _v)
        kit.WEAR.setdefault(_k, kit.WEAR['anodized'])
        kit.GRIME.setdefault(_k, kit.GRIME['anodized'])
        kit.SCRATCH.setdefault(_k, 0.0)
except ImportError:
    pass
