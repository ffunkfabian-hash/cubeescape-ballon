// Untergrund einer Fläche für Einschläge (0.39 „Scatter“): SceneLoader hängt ihn an jeden Kollisionsquader mit colliders[].surface
// (Szenengenerator, basic/scenes SURFACES); WeaponFx.Impact liest ihn am getroffenen Collider und ändert den Einschlagstil nach
// motion.payload.surfaces (ego.IMPACT_SURFACES). Flächen ohne Untergrund (Schießstand, Beton) zeigen den Stil unverändert.
using UnityEngine;

namespace Ballon.Ego
{
    public sealed class FxSurface : MonoBehaviour
    {
        public string kind = "";
    }
}
