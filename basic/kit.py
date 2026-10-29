"""BASIC-Baukasten für Blender (läuft in Blender 5.x, `bpy`).

Eine Waffe wird als Python-Modul beschrieben (`basic/weapons/wNN_*.py`): META, ASSEMBLIES, PARTS, ANCHORS, MOTIONS.
Dieses Modul baut daraus eine Szene mit der Hierarchie Waffe → Baugruppe → Bauteil.

Rahmen (wie Formgen-Geometrie-Spec v1 und Toolgen): Meter, vorn −Y, oben +Z, links +X, Ursprung Socket_Hand.
Autorenmaß in Millimetern: f = nach vorn (mm, wird −Y), u = nach oben (mm, +Z), x = nach links (mm, +X).

Bauteil-Formen (alle mit Bevel-Modifier, Radius `bevel` in mm, 2 Segmente, Winkelgrenze 30°):
  prof   Seitenprofil [(f,u) …] quer extrudiert, Breite w (mm), Mitte x
  box    Quader f0..f1, u0..u1, Breite w, Mitte x
  cyl    Zylinder entlang einer Achse ('f' längs, 'x' quer, 'u' hoch), optional hohl (r_in)
  plan   Draufsicht-Profil [(f,x) …] hochextrudiert u0..u1 (Bogen-Wurfarme quer, Glefenklinge)
  xprof  Querprofil [(x,u) …] um die Visierlinie cu, entlang f0..f1 extrudiert (Visier-Baukasten v3: Hauben, Sockel, Glas, Absehen);
         Durchbrüche als `cuts` mit derselben Form

Drehsinn beweglicher Teile (move.range_deg, verbindlich, geprüft von tools/test_motion.py über move.expect):
  axis 'x'  positiv = gegen den Uhrzeigersinn in der Seitenansicht mit vorn rechts und oben oben (wie common.rot):
            das untere Ende wandert nach vorn, das hintere Ende nach unten. Abzug ziehen = negativ.
  axis 'f'  Rechte-Hand-Regel um die Vorwärtsachse: positiv hebt die linke Seite (+X), senkt die rechte.
  axis 'u'  Rechte-Hand-Regel um oben (+Z): positiv schwenkt das hintere Ende nach rechts (−X).
"""
import math
import bpy
import bmesh
from mathutils import Vector, Matrix

MM = 0.001

# Materialrollen des Designvertrags (docs/designvertrag.md). Farben sRGB-hex.
MATERIALS = {
    'shell':    dict(color='#D8CCB4', rough=0.55, metal=0.0, de='Lackiertes Gehäuse (Creme)'),
    'graphite': dict(color='#2C2E33', rough=0.75, metal=0.0, de='Griffpolymer / Graphit', aaa_color='#141518', spec=0.25),
    'metal':    dict(color='#8C9198', rough=0.38, metal=0.85, de='Funktionsmetall'),
    'dark_metal': dict(color='#4A4E55', rough=0.45, metal=0.8, de='Brüniertes Metall'),
    'accent':   dict(color='#E0651E', rough=0.5, metal=0.0, de='Akzent Orange (Bedienelement)'),
    'energy':   dict(color='#5FD3E0', rough=0.3, metal=0.0, emit=3.0, de='Energieanzeige (leuchtend)'),
    'glass':    dict(color='#BFE3EA', rough=0.0, metal=0.0, alpha=0.12, de='Visierglas'),
    # Glasvarianten (Nutzerwunsch 24.10.2026: „Muster und Formen, Risse, Körner … leicht und dezent“); Wirkung in aaa_nodes
    'glass_dust':    dict(color='#BFE3EA', rough=0.0, metal=0.0, alpha=0.12, glass_fx=('dust',), de='Visierglas mit Staubkörnern'),
    'glass_scratch': dict(color='#BFE3EA', rough=0.0, metal=0.0, alpha=0.12, glass_fx=('scratch',), de='Visierglas mit feinen Kratzern'),
    'glass_crack':   dict(color='#BFE3EA', rough=0.0, metal=0.0, alpha=0.12, glass_fx=('crack',), de='Visierglas mit Riss in der Ecke'),
    'glass_cells':   dict(color='#BFE3EA', rough=0.0, metal=0.0, alpha=0.12, glass_fx=('cells',), de='Visierglas mit Zellvergütung'),
    'glass_scope':   dict(color='#BFE3EA', rough=0.0, metal=0.0, alpha=0.12, no_coat=True, de='Linse im Zielfernrohr (ohne Klarlack-Spiegelung)'),
    'glass_worn':    dict(color='#BFE3EA', rough=0.0, metal=0.0, alpha=0.12, glass_fx=('dust', 'scratch'), de='Visierglas benutzt'),
    'string':   dict(color='#1E2024', rough=0.6, metal=0.0, de='Sehne'),
    # v2 (AAA-Pilot): zusätzliche Rollen für Materialbruch
    'rubber':   dict(color='#1A1B1E', rough=0.85, metal=0.0, de='Gummi mit Stippling', aaa_color='#111214', spec=0.2),
    'trim':     dict(color='#C9CDD2', rough=0.22, metal=1.0, de='Blanke Zierkante', aniso=0.6),
    'anodized': dict(color='#202227', rough=0.4, metal=0.6, de='Schwarz eloxiert'),
    # Visierteile (0.21, Nutzerwahl A zur Abriebmaske): wie eloxiert, feines Relief, Abrieb mit 1,2 mm Messradius (WEAR_RADIUS) –
    # mit 4 mm galten 2–4 mm dünne Hauben, Ringe und Sockel ganz als Kante (hellgrau-marmoriert); Skins wie `anodized`
    'sight_anod': dict(color='#202227', rough=0.4, metal=0.6, de='Visier eloxiert (Abrieb für dünne Teile)', skin_as='anodized'),
    'brass':    dict(color='#B8913E', rough=0.3, metal=1.0, de='Messing (Patronen)'),
    'decal':    dict(color='#ECE8DF', rough=0.5, metal=0.0, de='Markierung hell'),
    # Absehen-Farben (basic/reticles.COLORS): gedämpfte Leuchtstärke (AgX bleicht helle Lichter zu Weiß), damit dünne Linien ihre Farbe behalten
    'reticle_cyan':  dict(color='#5FD3E0', rough=0.3, metal=0.0, emit=0.6, emit_only=True, de='Absehen Cyan'),
    'reticle_red':   dict(color='#FF3D2E', rough=0.3, metal=0.0, emit=0.6, emit_only=True, de='Absehen Rot'),
    'reticle_green': dict(color='#38E06E', rough=0.3, metal=0.0, emit=0.6, emit_only=True, de='Absehen Grün'),
    'reticle_amber': dict(color='#FFB01F', rough=0.3, metal=0.0, emit=0.6, emit_only=True, de='Absehen Bernstein'),
    'reticle_white': dict(color='#EEF2F5', rough=0.3, metal=0.0, emit=0.5, emit_only=True, de='Absehen Weiß'),
    # Gezeichnete Leuchtkontur am Visier (0.21, H2 „Pille“): wie Absehen Cyan, aber kein Absehen – Unity blendet `reticle_*` aus
    'sight_line':    dict(color='#5FD3E0', rough=0.3, metal=0.0, emit=0.6, emit_only=True, de='Leuchtkontur am Visier'),
}
# Rollen mit Lack auf Metall: im AAA-Modus Kantenabrieb zum blanken Metall
WEAR = {'shell': 1.0, 'accent': 0.8, 'graphite': 0.15, 'anodized': 0.3, 'dark_metal': 0.25, 'sight_anod': 0.3}   # dunkle Teile dezent (schlicht)
WEAR_RADIUS = {'sight_anod': 0.0012}   # Messradius der Kantenmaske (m), sonst 4 mm (größer als die Modellfase)
# Farb- und Texturvarianten (Skins): überschreiben je Materialrolle die Farbe, skalieren Abrieb/Schmutz, optional Muster.
# Form und Bauteile bleiben gleich; nur im AAA-Modus wirksam. Regeln: docs/stilhandbuch.md › Skins.
SKINS = {
    'standard': dict(de='Standard', kind='Farbe', roles={}),
    'nacht':    dict(de='Nachtschicht', kind='Farbe', roles={'shell': '#2B2E34', 'graphite': '#111214'}, wear=1.4),
    'polar':    dict(de='Polar', kind='Farbe', roles={'shell': '#E8EBEE', 'graphite': '#59606A', 'anodized': '#8F959D',
                                                       'accent': '#2FA9BC'}, wear=0.6),
    'kobalt':   dict(de='Kobalt', kind='Farbe', roles={'shell': '#26385A', 'graphite': '#14161A'}),
    'wueste':   dict(de='Wüste', kind='Farbe', roles={'shell': '#B8A27E', 'graphite': '#3F4034', 'accent': '#B8452A'}),
    'tarnung':  dict(de='Tarnung', kind='Textur', roles={'graphite': '#2B2D27'}, pattern=('#6F7360', '#B8AE90', '#3E4235')),
    'gebraucht': dict(de='Gebraucht', kind='Textur', roles={'shell': '#CBBFA4'}, wear=3.2, grime=2.2),
    'eloxal':   dict(de='Eloxal', kind='Textur', roles={'shell': '#5B6876'}, metal_shell=True),
}
SKIN = dict(name='standard')   # aktiver Skin (tools/blender_build.py --skin)

GRIME = {'shell': 0.45, 'accent': 0.35, 'decal': 0.3, 'anodized': 0.25, 'sight_anod': 0.25}
SCRATCH = {'sight_anod': 0.0}   # feine Kratzer (Standard 0,55); Visier ohne: quer zur Rohrachse wirken sie als weiße Sprenkel (0.21)
BUMP = {'rubber': ('voronoi', 2600.0, 0.5), 'graphite': ('noise', 900.0, 0.12), 'shell': ('noise', 400.0, 0.04),
        'dark_metal': ('noise', 1200.0, 0.05), 'sight_anod': ('noise', 1200.0, 0.04)}


def hex_rgba(h, a=1.0):
    h = h.lstrip('#')
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    return (*lin, a)


def to_xyz(f, u, x=0.0):
    """Autorenmaß (mm) → Blender-Meter."""
    return Vector((x * MM, -f * MM, u * MM))


# ------------------------------------------------------------------ Szene

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.scale_length = 1.0
    return sc


def material(role, mode='color'):
    """mode: color (Gestaltung), clay (neutral grau), black (Silhouette)."""
    key = f'MT_{role}_{mode}' + (f"_{SKIN['name']}" if mode == 'aaa' else '')
    m = bpy.data.materials.get(key)
    if m:
        return m
    d = MATERIALS[role]
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    bsdf = m.node_tree.nodes['Principled BSDF']
    if mode == 'color':
        bsdf.inputs['Base Color'].default_value = hex_rgba(d['color'])
        bsdf.inputs['Roughness'].default_value = d['rough']
        bsdf.inputs['Metallic'].default_value = d['metal']
        if d.get('emit'):
            bsdf.inputs['Emission Color'].default_value = hex_rgba(d['color'])
            bsdf.inputs['Emission Strength'].default_value = d['emit']
        if d.get('alpha') is not None:
            bsdf.inputs['Alpha'].default_value = d['alpha']
            bsdf.inputs['Transmission Weight'].default_value = 1.0
    elif mode == 'clay':
        bsdf.inputs['Base Color'].default_value = hex_rgba('#B9BBBE')
        bsdf.inputs['Roughness'].default_value = 0.7
        bsdf.inputs['Metallic'].default_value = 0.0
        if d.get('alpha') is not None:
            bsdf.inputs['Alpha'].default_value = 0.35
    elif mode == 'aaa':
        aaa_nodes(m, role, d)
        m['basic_skin'] = SKIN['name']
    else:  # black
        bsdf.inputs['Base Color'].default_value = (0, 0, 0, 1)
        bsdf.inputs['Roughness'].default_value = 1.0
        bsdf.inputs['Specular IOR Level'].default_value = 0.0
    m.diffuse_color = hex_rgba(d['color'])
    m['basic_role'] = role
    return m


GLASS_FX_STRENGTH = 0.15    # höchste zusätzliche Deckkraft an der Maske (v3: dezent, Mitte klar – REF 0.14 › 8)


def glass_fx(N, L, b, fx):
    """Dezente Glasoberfläche: Maske aus Staub (Körner), Kratzern (gestreckte Linien), Riss (Zellkanten, nur eine Ecke) und
    Zellvergütung (Zellkanten, sehr schwach); an der Maske wird das Glas etwas matter und deckender. v3: nur am Rand, Mitte klar."""
    tc = N.new('ShaderNodeTexCoord')
    parts = []

    def ramp(sock, lo, hi, out=1.0, out0=0.0):
        r = N.new('ShaderNodeMapRange')
        r.inputs['From Min'].default_value, r.inputs['From Max'].default_value = lo, hi
        r.inputs['To Min'].default_value, r.inputs['To Max'].default_value = out0, out
        L.new(sock, r.inputs['Value'])
        return r.outputs['Result']

    def mul(a, c):
        m = N.new('ShaderNodeMath')
        m.operation = 'MULTIPLY'
        L.new(a, m.inputs[0])
        L.new(c, m.inputs[1])
        return m.outputs['Value']
    if 'dust' in fx:        # Körner ~0,3 mm, nur jede siebte Zelle
        v = N.new('ShaderNodeTexVoronoi')
        v.inputs['Scale'].default_value = 1400.0
        L.new(tc.outputs['Object'], v.inputs['Vector'])
        sep = N.new('ShaderNodeSeparateColor')
        L.new(v.outputs['Color'], sep.inputs['Color'])
        parts.append(mul(ramp(v.outputs['Distance'], 0.22, 0.12), ramp(sep.outputs['Red'], 0.84, 0.86)))
    if 'scratch' in fx:     # feine Kratzer: Rauschen stark gestreckt und gedreht, schmale Schwelle
        mp = N.new('ShaderNodeMapping')
        mp.inputs['Rotation'].default_value = (0.0, 0.42, 0.0)
        mp.inputs['Scale'].default_value = (2600.0, 30.0, 40.0)
        L.new(tc.outputs['Object'], mp.inputs['Vector'])
        nz = N.new('ShaderNodeTexNoise')
        nz.inputs['Scale'].default_value = 1.0
        nz.inputs['Detail'].default_value = 2.0
        L.new(mp.outputs['Vector'], nz.inputs['Vector'])
        parts.append(ramp(nz.outputs['Fac'], 0.70, 0.74, 0.8))
    if 'crack' in fx:       # Rissnetz aus Zellkanten, nur in der oberen linken Ecke (Generated-Koordinaten)
        v = N.new('ShaderNodeTexVoronoi')
        v.feature = 'DISTANCE_TO_EDGE'
        v.inputs['Scale'].default_value = 160.0
        L.new(tc.outputs['Object'], v.inputs['Vector'])
        sep = N.new('ShaderNodeSeparateXYZ')
        L.new(tc.outputs['Generated'], sep.inputs['Vector'])
        cx = N.new('ShaderNodeCombineXYZ')
        L.new(sep.outputs['X'], cx.inputs['X'])
        L.new(sep.outputs['Z'], cx.inputs['Y'])
        dist = N.new('ShaderNodeVectorMath')
        dist.operation = 'DISTANCE'
        dist.inputs[1].default_value = (0.92, 0.9, 0.0)
        L.new(cx.outputs['Vector'], dist.inputs[0])
        parts.append(mul(ramp(v.outputs['Distance'], 0.035, 0.0), ramp(dist.outputs['Value'], 0.42, 0.1)))
    if 'cells' in fx:       # Zellvergütung: sehr schwache Zellkanten über die ganze Scheibe
        v = N.new('ShaderNodeTexVoronoi')
        v.feature = 'DISTANCE_TO_EDGE'
        v.inputs['Scale'].default_value = 420.0
        L.new(tc.outputs['Object'], v.inputs['Vector'])
        parts.append(ramp(v.outputs['Distance'], 0.05, 0.0, 0.35))
    mask = parts[0]
    for q in parts[1:]:
        m = N.new('ShaderNodeMath')
        m.operation = 'MAXIMUM'
        L.new(mask, m.inputs[0])
        L.new(q, m.inputs[1])
        mask = m.outputs['Value']
    # v3: Gebrauchsspuren nur am Rand – zur Scheibenmitte (Generated x/z) auf null ausblenden
    sg = N.new('ShaderNodeSeparateXYZ')
    L.new(tc.outputs['Generated'], sg.inputs['Vector'])
    cg = N.new('ShaderNodeCombineXYZ')
    L.new(sg.outputs['X'], cg.inputs['X'])
    L.new(sg.outputs['Z'], cg.inputs['Y'])
    dc = N.new('ShaderNodeVectorMath')
    dc.operation = 'DISTANCE'
    dc.inputs[1].default_value = (0.5, 0.5, 0.0)
    L.new(cg.outputs['Vector'], dc.inputs[0])
    mask = mul(mask, ramp(dc.outputs['Value'], 0.26, 0.46))
    L.new(ramp(mask, 0.0, 1.0, 0.08 + GLASS_FX_STRENGTH, 0.08), b.inputs['Alpha'])
    L.new(ramp(mask, 0.0, 1.0, 0.45, 0.02), b.inputs['Roughness'])


def aaa_nodes(m, role, d):
    """PBR-Material (Cycles): Grundfarbe, Rauheitsvariation, Mikrorelief, Kantenabrieb über den Bevel-Knoten."""
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N['Principled BSDF']
    sk = SKINS[SKIN['name']]
    d = dict(d)
    if d.get('skin_as', role) in sk['roles']:
        d['color'] = d['aaa_color'] = sk['roles'][d.get('skin_as', role)]
    if role == 'shell' and sk.get('metal_shell'):
        d.update(metal=0.85, rough=0.32)
    col = hex_rgba(d.get('aaa_color', d['color']))
    b.inputs['Base Color'].default_value = col
    b.inputs['Metallic'].default_value = d['metal']
    b.inputs['Roughness'].default_value = d['rough']
    if d.get('spec') is not None:
        b.inputs['Specular IOR Level'].default_value = d['spec']
    if d.get('aniso'):
        b.inputs['Anisotropic'].default_value = d['aniso']
    if d.get('emit'):
        b.inputs['Emission Color'].default_value = col
        b.inputs['Emission Strength'].default_value = d['emit'] * 1.6
        if d.get('emit_only'):          # Absehen: nur Leuchten, keine beleuchtete Grundfarbe (sonst wirkt die Farbe pastellig)
            b.inputs['Base Color'].default_value = (0.0, 0.0, 0.0, 1)
            b.inputs['Specular IOR Level'].default_value = 0.0
    if d.get('alpha') is not None:
        b.inputs['Alpha'].default_value = 0.08
        b.inputs['Transmission Weight'].default_value = 1.0
        b.inputs['Roughness'].default_value = 0.02
        b.inputs['Coat Weight'].default_value = 0.6
        b.inputs['Coat Tint'].default_value = (0.75, 0.95, 1.0, 1)
        if d.get('no_coat'):            # Linsen im Rohr: Studiolichter spiegeln sonst als grelle Flächen über dem Absehen
            b.inputs['Coat Weight'].default_value = 0.0
            b.inputs['Specular IOR Level'].default_value = 0.05
            b.inputs['Alpha'].default_value = 0.04
        if d.get('glass_fx'):
            glass_fx(N, L, b, d['glass_fx'])
        return
    tc = N.new('ShaderNodeTexCoord')
    # Rauheitsvariation (großflächig, Objektraum in m)
    nz = N.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 60.0
    nz.inputs['Detail'].default_value = 6.0
    L.new(tc.outputs['Object'], nz.inputs['Vector'])
    rmap = N.new('ShaderNodeMapRange')
    rmap.inputs['To Min'].default_value = d['rough'] * 0.85
    rmap.inputs['To Max'].default_value = min(1.0, d['rough'] * 1.15)
    L.new(nz.outputs['Fac'], rmap.inputs['Value'])
    rough = rmap.outputs['Result']
    # Mikrorelief
    bp = BUMP.get(role)
    if bp:
        kind, scale, strength = bp
        tx = N.new('ShaderNodeTexVoronoi' if kind == 'voronoi' else 'ShaderNodeTexNoise')
        tx.inputs['Scale'].default_value = scale
        L.new(tc.outputs['Object'], tx.inputs['Vector'])
        bump = N.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = strength
        bump.inputs['Distance'].default_value = 0.0004
        L.new(tx.outputs['Distance' if kind == 'voronoi' else 'Fac'], bump.inputs['Height'])
        L.new(bump.outputs['Normal'], b.inputs['Normal'])
    w = WEAR.get(role)
    if w:
        w = min(1.0, w * sk.get('wear', 1.0))
    if role == 'shell' and sk.get('pattern'):
        # Tarnmuster: zwei Schwellen auf großem Noise, harte Kanten (lackierte Flächen)
        pa = N.new('ShaderNodeTexNoise')
        pa.inputs['Scale'].default_value = 9.0
        pa.inputs['Detail'].default_value = 3.0
        pa.inputs['Roughness'].default_value = 0.45
        L.new(tc.outputs['Object'], pa.inputs['Vector'])
        ramp = N.new('ShaderNodeValToRGB')
        ramp.color_ramp.interpolation = 'CONSTANT'
        e = ramp.color_ramp.elements
        e[0].color = hex_rgba(sk['pattern'][0])
        e[1].position = 0.47
        e[1].color = hex_rgba(sk['pattern'][1])
        e3 = e.new(0.58)
        e3.color = hex_rgba(sk['pattern'][2])
        L.new(pa.outputs['Fac'], ramp.inputs['Fac'])
        col_socket = ramp.outputs['Color']
    else:
        col_socket = None
    if w:
        # Kantenmaske: Abweichung zwischen echter Normale und gerundeter Bevel-Normale
        bev = N.new('ShaderNodeBevel')
        bev.samples = 8
        # Messradius größer als die Modellfase (3–5 mm), sonst findet die Maske keine Kante
        bev.inputs['Radius'].default_value = WEAR_RADIUS.get(role, 0.004) * (1.75 if sk.get('wear', 1.0) > 2 else 1.0)
        geo = N.new('ShaderNodeNewGeometry')
        dot = N.new('ShaderNodeVectorMath')
        dot.operation = 'DOT_PRODUCT'
        L.new(bev.outputs['Normal'], dot.inputs[0])
        L.new(geo.outputs['Normal'], dot.inputs[1])
        edge = N.new('ShaderNodeMapRange')
        edge.inputs['From Min'].default_value = 0.985 - 0.01 * max(0.0, SKINS[SKIN['name']].get('wear', 1.0) - 1.0)
        edge.inputs['From Max'].default_value = 0.9995
        edge.inputs['To Min'].default_value = 1.0
        edge.inputs['To Max'].default_value = 0.0
        L.new(dot.outputs['Value'], edge.inputs['Value'])
        brk = N.new('ShaderNodeTexNoise')
        brk.inputs['Scale'].default_value = 420.0
        brk.inputs['Detail'].default_value = 8.0
        L.new(tc.outputs['Object'], brk.inputs['Vector'])
        mul = N.new('ShaderNodeMath')
        mul.operation = 'MULTIPLY'
        L.new(edge.outputs['Result'], mul.inputs[0])
        L.new(brk.outputs['Fac'], mul.inputs[1])
        thr = N.new('ShaderNodeMapRange')
        cov = max(0.0, sk.get('wear', 1.0) - 1.0) * 0.08     # Skins mit mehr Abrieb: größere Abriebfläche
        thr.inputs['From Min'].default_value = 0.30 - cov
        thr.inputs['From Max'].default_value = 0.42 - cov
        thr.inputs['To Max'].default_value = w
        L.new(mul.outputs['Value'], thr.inputs['Value'])
        mask = thr.outputs['Result']
        mc = N.new('ShaderNodeMix')
        mc.data_type = 'RGBA'
        mc.inputs['A'].default_value = col
        if col_socket is not None:
            L.new(col_socket, mc.inputs['A'])
        mc.inputs['B'].default_value = hex_rgba('#9EA3A9')
        L.new(mask, mc.inputs['Factor'])
        L.new(mc.outputs['Result'], b.inputs['Base Color'])
        mm = N.new('ShaderNodeMix')
        mm.inputs['A'].default_value = d['metal']
        mm.inputs['B'].default_value = 1.0
        L.new(mask, mm.inputs['Factor'])
        L.new(mm.outputs['Result'], b.inputs['Metallic'])
        mr = N.new('ShaderNodeMix')
        L.new(rough, mr.inputs['A'])
        mr.inputs['B'].default_value = 0.28
        L.new(mask, mr.inputs['Factor'])
        rough = mr.outputs['Result']
    L.new(rough, b.inputs['Roughness'])
    if role in GRIME:
        # Schmutz in Vertiefungen (AO) und feine Kratzer (gestreckte Noise) auf der Grundfarbe
        ao = N.new('ShaderNodeAmbientOcclusion')
        ao.samples = 8
        ao.inputs['Distance'].default_value = 0.006
        gm = N.new('ShaderNodeMapRange')
        gm.inputs['From Min'].default_value = 0.35
        gm.inputs['From Max'].default_value = 0.9
        gm.inputs['To Min'].default_value = min(0.9, GRIME[role] * sk.get('grime', 1.0))
        gm.inputs['To Max'].default_value = 0.0
        L.new(ao.outputs['AO'], gm.inputs['Value'])
        base = b.inputs['Base Color'].links[0].from_socket if b.inputs['Base Color'].links else None
        dirt = N.new('ShaderNodeMix')
        dirt.data_type = 'RGBA'
        if base:
            L.new(base, dirt.inputs['A'])
        else:
            dirt.inputs['A'].default_value = col
        dirt.inputs['B'].default_value = hex_rgba('#3B3329')
        L.new(gm.outputs['Result'], dirt.inputs['Factor'])
        sc = N.new('ShaderNodeTexNoise')
        sc.inputs['Scale'].default_value = 900.0
        sc.inputs['Detail'].default_value = 2.0
        mp = N.new('ShaderNodeMapping')
        mp.inputs['Scale'].default_value = (0.04, 1.0, 1.0)
        L.new(tc.outputs['Object'], mp.inputs['Vector'])
        L.new(mp.outputs['Vector'], sc.inputs['Vector'])
        sr = N.new('ShaderNodeMapRange')
        sr.inputs['From Min'].default_value = 0.70
        sr.inputs['From Max'].default_value = 0.74
        sr.inputs['To Max'].default_value = SCRATCH.get(role, 0.55)
        L.new(sc.outputs['Fac'], sr.inputs['Value'])
        scr = N.new('ShaderNodeMix')
        scr.data_type = 'RGBA'
        L.new(dirt.outputs['Result'], scr.inputs['A'])
        scr.inputs['B'].default_value = hex_rgba('#A7ACB2')
        L.new(sr.outputs['Result'], scr.inputs['Factor'])
        L.new(scr.outputs['Result'], b.inputs['Base Color'])


# ------------------------------------------------------------------ Netze

def _mesh_obj(name, bm):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _area2(pts):
    return sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts))) / 2


def mesh_prof(name, pts, w, x=0.0):
    """Seitenprofil (f,u) in mm, Breite w quer (X)."""
    bm = bmesh.new()
    if _area2(pts) < 0:
        pts = pts[::-1]
    a = [bm.verts.new(to_xyz(f, u, x - w / 2)) for f, u in pts]
    b = [bm.verts.new(to_xyz(f, u, x + w / 2)) for f, u in pts]
    n = len(pts)
    bm.faces.new(a)
    bm.faces.new(b[::-1])
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    return _mesh_obj(name, bm)


def mesh_plan(name, pts, u0, u1):
    """Draufsicht-Profil (f,x) in mm, hochextrudiert u0..u1."""
    bm = bmesh.new()
    a = [bm.verts.new(to_xyz(f, u0, x)) for f, x in pts]
    b = [bm.verts.new(to_xyz(f, u1, x)) for f, x in pts]
    n = len(pts)
    bm.faces.new(a)
    bm.faces.new(b[::-1])
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    return _mesh_obj(name, bm)


def mesh_xprof(name, pts, f0, f1, cu, cx=0.0):
    """Querprofil [(x, u) …] in mm (u relativ zu cu, Blick von hinten), entlang der Laufachse f0..f1 extrudiert (Visier-Baukasten v3)."""
    if _area2(pts) < 0:
        pts = pts[::-1]
    bm = bmesh.new()
    a = [bm.verts.new(to_xyz(f0, cu + u, cx + x)) for x, u in pts]
    b = [bm.verts.new(to_xyz(f1, cu + u, cx + x)) for x, u in pts]
    n = len(pts)
    bm.faces.new(a)
    bm.faces.new(b[::-1])
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    return _mesh_obj(name, bm)


def mesh_cyl(name, axis, c, a0, a1, r, segs=24, r_in=None, r1=None):
    """Zylinder/Rohr/Kegel. axis 'f','x','u'; c = Mitte der beiden anderen Achsen in mm; a0..a1 entlang der Achse.
    r1: Radius am Ende a1 (Kegel), r_in: hohl."""
    r1 = r if r1 is None else r1

    def P(t, ang, rad):
        s, co = math.sin(ang) * rad, math.cos(ang) * rad
        if axis == 'f':
            return to_xyz(t, c[0] + co, c[1] + s)      # c=(u,x)
        if axis == 'x':
            return to_xyz(c[0] + co, c[1] + s, t)      # c=(f,u)
        return to_xyz(c[0] + co, t, c[1] + s)          # axis u, c=(f,x)
    bm = bmesh.new()
    angs = [2 * math.pi * k / segs + math.pi / segs for k in range(segs)]
    o0 = [bm.verts.new(P(a0, g, r)) for g in angs]
    o1 = [bm.verts.new(P(a1, g, r1)) for g in angs]
    for k in range(segs):
        j = (k + 1) % segs
        bm.faces.new((o0[k], o0[j], o1[j], o1[k]))
    if r_in:
        i0 = [bm.verts.new(P(a0, g, r_in)) for g in angs]
        i1 = [bm.verts.new(P(a1, g, r_in * r1 / r)) for g in angs]
        for k in range(segs):
            j = (k + 1) % segs
            bm.faces.new((i0[k], i1[k], i1[j], i0[j]))
            bm.faces.new((o0[k], i0[k], i0[j], o0[j]))
            bm.faces.new((o1[k], o1[j], i1[j], i1[k]))
    else:
        bm.faces.new(o0)
        bm.faces.new(o1[::-1])
    return _mesh_obj(name, bm)


def _rrect(cx, cu, w, h, r, n=4):
    """Abgerundetes Rechteck in der X-U-Ebene (mm), gegen den Uhrzeigersinn."""
    if r <= 0:
        return [(cx - w / 2, cu - h / 2), (cx + w / 2, cu - h / 2), (cx + w / 2, cu + h / 2), (cx - w / 2, cu + h / 2)]
    pts = []
    for (sx, su, a0) in ((1, -1, -90), (1, 1, 0), (-1, 1, 90), (-1, -1, 180)):
        ox, ou = cx + sx * (w / 2 - r), cu + su * (h / 2 - r)
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((ox + r * math.cos(a), ou + r * math.sin(a)))
    return pts


def mesh_frame(name, f0, f1, cu, ow, oh, iw, ih, r_out, r_in, cx=0.0):
    """Platte oder Rahmen quer zur Laufachse (X-U-Ebene), Dicke f0..f1. iw=0 → volle Platte."""
    bm = bmesh.new()
    out = _rrect(cx, cu, ow, oh, r_out)
    o0 = [bm.verts.new(to_xyz(f0, u, x)) for x, u in out]
    o1 = [bm.verts.new(to_xyz(f1, u, x)) for x, u in out]
    n = len(out)
    for k in range(n):
        j = (k + 1) % n
        bm.faces.new((o0[k], o0[j], o1[j], o1[k]))
    if iw > 0:
        inn = _rrect(cx, cu, iw, ih, r_in)
        assert len(inn) == n
        i0 = [bm.verts.new(to_xyz(f0, u, x)) for x, u in inn]
        i1 = [bm.verts.new(to_xyz(f1, u, x)) for x, u in inn]
        for k in range(n):
            j = (k + 1) % n
            bm.faces.new((i0[k], i1[k], i1[j], i0[j]))
            bm.faces.new((o0[k], i0[k], i0[j], o0[j]))
            bm.faces.new((o1[k], o1[j], i1[j], i1[k]))
    else:
        bm.faces.new(o0)
        bm.faces.new(o1[::-1])
    return _mesh_obj(name, bm)


def add_bevel(ob, r_mm, segs=2):
    if r_mm <= 0:
        return
    m = ob.modifiers.new('BASIC_Bevel', 'BEVEL')
    m.width = r_mm * MM
    m.segments = segs
    m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(30)
    m.harden_normals = True        # gewichtete Normalen (A6): Originalflächen flach, Fasenflächen weich; kommen so im FBX an
    m.use_clamp_overlap = True
    # Kein Weighted-Normal-Modifikator mehr (0.32): auf den flach schattierten Teilen behandelte er mit keep_sharp jede Kante als hart
    # und machte die weichen Fasen-Normalen wieder flach (BASIC-01: 45 % statt 99 % der Fasenflächen weich, Griff 1 %, Magazin facettiert)


def set_origin(ob, world_pt):
    """Ursprung eines Objekts auf einen Punkt legen (Drehpunkt), Geometrie bleibt."""
    off = world_pt - ob.matrix_world.translation
    ob.data.transform(Matrix.Translation(-off))
    ob.matrix_world.translation += off


# ------------------------------------------------------------------ Bau

def build_shape(name, p):
    """Netzobjekt einer Form (ohne Material/Bevel)."""
    k = p['shape']
    if k == 'multi':   # mehrere Formen zu einem Bauteil vereinigt (Schrauben, Rippen, Lochgitter)
        obs = [build_shape(f'{name}_{i}', dict(q, shape=q.get('shape', 'box'))) for i, q in enumerate(p['items'])]
        bm = bmesh.new()
        for o in obs:
            bm.from_mesh(o.data)
            bpy.data.objects.remove(o)
        return _mesh_obj(name, bm)
    if k == 'tube':    # Leitung entlang Polylinie (f,u,x) mm mit Radius r
        cu = bpy.data.curves.new(name, 'CURVE')
        cu.dimensions = '3D'
        cu.bevel_depth = p['r'] * MM
        cu.bevel_resolution = 3
        sp = cu.splines.new('BEZIER')
        sp.bezier_points.add(len(p['path']) - 1)
        for bp, pt in zip(sp.bezier_points, p['path']):
            bp.co = to_xyz(*pt)
            bp.handle_left_type = bp.handle_right_type = 'AUTO'
        cu.use_fill_caps = True
        co = bpy.data.objects.new(name + '_c', cu)
        bpy.context.scene.collection.objects.link(co)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(co.evaluated_get(dg))
        bpy.data.objects.remove(co)
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
        return ob
    if k == 'text':    # Schriftzug als Geometrie auf einer Seitenfläche (side +1 links, −1 rechts) oder oben (side 0)
        cu = bpy.data.curves.new(name, 'FONT')
        cu.body = p['text']
        cu.size = p['size'] * MM
        cu.extrude = p.get('depth', 0.15) * MM
        cu.align_x = p.get('align', 'LEFT')
        co = bpy.data.objects.new(name + '_c', cu)
        bpy.context.scene.collection.objects.link(co)
        s = p.get('side', 1)
        if s == 0:      # oben lesbar von hinten nach vorn
            R = Matrix(((0, 1, 0), (-1, 0, 0), (0, 0, 1)))
        else:
            R = Matrix(((0, 0, s), (s, 0, 0), (0, 1, 0)))
        co.matrix_world = Matrix.Translation(to_xyz(p['f'], p['u'], p.get('x', 0))) @ R.to_4x4()
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(co.evaluated_get(dg))
        me.transform(co.matrix_world)
        bpy.data.objects.remove(co)
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
        return ob
    if k == 'prof':
        ob = mesh_prof(name, p['pts'], p['w'], p.get('x', 0))
    elif k == 'box':
        f0, f1, u0, u1 = p['f0'], p['f1'], p['u0'], p['u1']
        ob = mesh_prof(name, [(f0, u0), (f1, u0), (f1, u1), (f0, u1)], p['w'], p.get('x', 0))
    elif k == 'cyl':
        ob = mesh_cyl(name, p['axis'], p['c'], p['a0'], p['a1'], p['r'], p.get('segs', 24), p.get('r_in'), p.get('r1'))
    elif k == 'plan':
        ob = mesh_plan(name, p['pts'], p['u0'], p['u1'])
    elif k == 'xprof':
        ob = mesh_xprof(name, p['pts'], p['f0'], p['f1'], p['cu'], p.get('cx', 0))
    elif k == 'xbox':
        ob = mesh_frame(name, p['f0'], p['f1'], p['cu'], p['ww'], p['hh'], 0, 0, 0, 0, p.get('cx', 0))
    elif k == 'frame':
        ob = mesh_frame(name, p['f0'], p['f1'], p['cu'], p['ow'], p['oh'], p['iw'], p['ih'], p['r_out'], p['r_in'],
                        p.get('cx', 0))
    else:
        raise KeyError(k)
    return ob


def apply_cuts(ob, cuts):
    """Durchbrüche/Fugen: Boolesche Differenz mit Schneidkörpern, sofort angewandt (kein Restobjekt)."""
    if not cuts:
        return
    cutters = [build_shape(f'{ob.name}_cut{i}', c) for i, c in enumerate(cuts)]
    bm = bmesh.new()
    for c in cutters:
        bm.from_mesh(c.data)
        bpy.data.objects.remove(c)
    cut = _mesh_obj(ob.name + '_cutall', bm)
    mod = ob.modifiers.new('BASIC_Cut', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.use_self = True            # Schneidkörper dürfen sich überlappen
    mod.use_hole_tolerant = True
    mod.object = cut
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    ob.modifiers.remove(mod)
    if len(me.vertices) < 8:
        raise RuntimeError(f'Durchbruch an {ob.name} ergibt ein leeres Netz – Schneidkörper prüfen')
    old = ob.data
    ob.data = me
    bpy.data.meshes.remove(old)
    bpy.data.objects.remove(cut)


def build_part(p):
    name = p['id']
    ob = build_shape(name, p)
    apply_cuts(ob, p.get('cuts'))
    m = material(p['mat'])
    if p.get('move', {}).get('kind') == 'glow':
        m = m.copy()
        m.name = f"MT_{p['mat']}_glow_{name}"
    ob.data.materials.clear()      # aus Kurven erzeugte Netze bringen einen leeren Slot mit
    ob.data.materials.append(m)
    add_bevel(ob, p.get('bevel', 1.0), p.get('segs_bevel', 2))
    if p['shape'] in ('cyl', 'tube') or p.get('smooth'):
        for poly in ob.data.polygons:
            poly.use_smooth = True
    return ob


def build(W, mode='color'):
    """Baut Waffe W (Modul) in die aktuelle Szene. Gibt (root, objs, anchors) zurück."""
    sc = bpy.context.scene
    col_root = bpy.data.collections.new(W.META['id'])
    sc.collection.children.link(col_root)
    root = bpy.data.objects.new(W.META['id'], None)
    root.empty_display_type = 'ARROWS'
    root.empty_display_size = 0.05
    col_root.objects.link(root)
    asm = {}
    for a in W.ASSEMBLIES:
        e = bpy.data.objects.new(f"ASM_{a['id']}", None)
        e.empty_display_size = 0.02
        col_root.objects.link(e)
        e.parent = root
        e['basic_assembly'] = a['id']
        asm[a['id']] = e
    objs = {}
    for p in W.PARTS:
        ob = build_part(p)
        sc.collection.objects.unlink(ob)
        col_root.objects.link(ob)
        ob.parent = asm[p['asm']]
        ob['basic_part'] = p['id']
        ob['basic_assembly'] = p['asm']
        mv = p.get('move')
        if mv and mv.get('pivot') is not None:
            set_origin(ob, to_xyz(*mv['pivot']))
        objs[p['id']] = ob
    # Kinder an bewegte Teile hängen (z. B. Patronen am Magazin)
    for p in W.PARTS:
        if p.get('parent_part'):
            ob = objs[p['id']]
            mw = ob.matrix_world.copy()
            ob.parent = objs[p['parent_part']]
            ob.matrix_world = mw
    anchors = {}
    for k, v in W.ANCHORS.items():
        e = bpy.data.objects.new(k, None)
        e.empty_display_type = 'SPHERE'
        e.empty_display_size = 0.006
        e.location = to_xyz(*v['at'])
        col_root.objects.link(e)
        e.parent = objs[v['part']] if v.get('part') in objs else root
        e.matrix_parent_inverse = e.parent.matrix_world.inverted()
        anchors[k] = e
    if mode != 'color':
        set_mode(objs, mode)
    return root, objs, anchors


def set_mode(objs, mode):
    for ob in objs.values():
        role = ob.data.materials[0]['basic_role']
        if mode == 'color' and ob.get('glow_mat'):
            ob.data.materials[0] = bpy.data.materials[ob['glow_mat']]
            continue
        if ob.data.materials[0].name.startswith(f'MT_{role}_glow_'):
            ob['glow_mat'] = ob.data.materials[0].name
        m = material(role, mode)
        if ob.get('glow_mat') and mode == 'aaa':   # Leuchtteile behalten ein eigenes Material (Animation)
            m = m.copy()
            m.name = f'MT_{role}_aaa_glow_{ob.name}'
        ob.data.materials[0] = m


def eval_tris(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    e = ob.evaluated_get(dg)
    me = e.to_mesh()
    n = sum(len(p.vertices) - 2 for p in me.polygons)
    e.to_mesh_clear()
    return n


def world_bounds(obs):
    dg = bpy.context.evaluated_depsgraph_get()
    lo = Vector((1e9,) * 3)
    hi = Vector((-1e9,) * 3)
    for ob in obs:
        e = ob.evaluated_get(dg)
        me = e.to_mesh()
        for v in me.vertices:
            w = e.matrix_world @ v.co
            lo = Vector(map(min, lo, w))
            hi = Vector(map(max, hi, w))
        e.to_mesh_clear()
    return lo, hi
