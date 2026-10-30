"""GPU für Cycles wählen (0.33 „Armory“, Nutzer 30.10.2026: RTX 4060 am Wochenende): OptiX, sonst CUDA, HIP, oneAPI, Metal – die erste
Geräteart, die dieser Blender kennt und für die er ein Gerät findet. Ohne passendes Gerät ein Fehler statt still auf der CPU zu rechnen
(GPU-Läufe nur unter `ce lock gpu`). Nur in Blender (bpy).
"""
ORDER = ('OPTIX', 'CUDA', 'HIP', 'ONEAPI', 'METAL')


def enable(scene):
    """Aktiviert die Geräte der ersten verfügbaren Art aus ORDER und stellt `scene` auf GPU. Liefert (Art, [Gerätenamen])."""
    import bpy
    pr = bpy.context.preferences.addons['cycles'].preferences
    for kind in ORDER:
        try:
            pr.compute_device_type = kind
        except TypeError:                       # Art in diesem Blender nicht vorhanden (z. B. OptiX auf dem Mac)
            continue
        pr.get_devices()
        found = [d for d in pr.devices if d.type == kind]
        if found:
            for d in pr.devices:
                d.use = d.type == kind
            scene.cycles.device = 'GPU'
            return kind, [d.name for d in found]
    raise RuntimeError(f'keine GPU für Cycles gefunden ({", ".join(ORDER)})')
