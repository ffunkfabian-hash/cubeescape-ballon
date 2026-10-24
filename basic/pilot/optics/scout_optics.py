"""Scout v2.1 mit Kastenoptik statt Rohr – Vergleichsvarianten für die Designsprache der Visiere (Nutzer 24.10.2026).

Baut BASIC-03 v2.1 und ersetzt nur die Visier-Baugruppe; Ausgabe `BASIC-03-v2.1-<stil>`. Aufruf über `variant('prism'|'flat')`.
"""
import types

from basic.common import box_scope_v21
from basic.pilot import w03_scout_rifle_v21 as S


def variant(style):
    P, A, cu = box_scope_v21(-38, S.TOP + 2, style=style)
    parts = [p for p in S.PARTS if p['asm'] != 'sight'] + P
    anchors = {k: v for k, v in S.ANCHORS.items() if k not in ('Socket_Sight', 'Socket_Objective', 'Socket_Reticle', 'Socket_Eye')}
    anchors.update(A)
    return types.SimpleNamespace(META=dict(S.META, variant=f'v2.1-{style}', name=f'Fernblick v2.1 ({style})'),
                                 ASSEMBLIES=S.ASSEMBLIES, PARTS=parts, ANCHORS=anchors, ACTIONS=S.ACTIONS, EXPLODE=S.EXPLODE,
                                 BORE=S.BORE, __doc__=S.__doc__)
