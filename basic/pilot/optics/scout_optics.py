"""Scout v2.1 mit Kastenoptik statt Rohr – Vergleichsvarianten für die Designsprache der Visiere (Nutzer 24.10.2026).

Baut BASIC-03 v2.1 und ersetzt die Visier-Baugruppe; Ausgabe `BASIC-03-v2.1-<stil>`. Aufruf über `variant('prism'|'flat')`.
Die Kästen stehen auf dem flachen Gehäuse mit langer Schiene (Stand vor 0.19 „Saddle“), weil ihre Sockel für die Schiene auf
`TOP` ausgelegt sind; der Buckel des Rohrs würde sie durchdringen.
"""
import types

from basic.common import box_scope_v21
from basic.pilot import w03_scout_rifle_v21 as S


def variant(style):
    P, A, cu = box_scope_v21(-38, S.TOP + 2, style=style)
    flat = {'receiver': [S.receiver(seat=False)], 'rail': S.top_rail(seat=False)}
    parts = [q for p in S.PARTS if p['asm'] != 'sight' for q in flat.get(p['id'], [p])] + P
    anchors = {k: v for k, v in S.ANCHORS.items() if k not in ('Socket_Sight', 'Socket_Objective', 'Socket_Reticle', 'Socket_Eye')}
    anchors.update(A)
    return types.SimpleNamespace(META=dict(S.META, variant=f'v2.1-{style}', name=f'Fernblick v2.1 ({style})'),
                                 ASSEMBLIES=S.ASSEMBLIES, PARTS=parts, ANCHORS=anchors, ACTIONS=S.ACTIONS, EXPLODE=S.EXPLODE,
                                 BORE=S.BORE, __doc__=S.__doc__)
