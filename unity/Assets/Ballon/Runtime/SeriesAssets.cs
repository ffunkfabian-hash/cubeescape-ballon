// Design-Serien aus Formgen v2 (0.43 „Kiln“): lokal erzeugtes Asset unter Generated/FormgenSeries/Resources (BallonSetup), nicht im Repo.
// Die Szene im Repo nennt nur die festen Waffen; Bootstrap hängt die Serien beim Start an, wenn dieses Asset da ist.
using UnityEngine;

namespace Ballon.Ego
{
    public sealed class SeriesAssets : ScriptableObject
    {
        public const string ResourceName = "BallonSeries";
        /// <summary>ego.json samt Serien (tools/series_packages.py).</summary>
        public TextAsset egoJson;
        /// <summary>Nur die Serienwaffen, Reihenfolge wie in egoJson hinter den festen Waffen.</summary>
        public Bootstrap.WeaponAssets[] weapons;
        /// <summary>Atlas-Materialien der Serien (Atlas_formgen_&lt;ID&gt;).</summary>
        public Material[] atlases;
    }
}
