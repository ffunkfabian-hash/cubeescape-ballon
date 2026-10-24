# Projekt cubeescape-ballon: Bedarf, Zuständigkeit, Schnittstellen

Stand 24.10.2026 · Version 0.1.0 „First Light“ · lokales Repo ohne Remote (Remote, Push und Veröffentlichung sind nicht beauftragt).

## Bedarf

- **Entscheidung des Nutzers (24.10.2026):** Die Waffenreihe BASIC bekommt ein eigenes Projekt („Nein, ich möchte das ein eigenes
  Projekt erstellt wird!“), wie im Auftrag › 11 unter dem Namen `cubeescape-ballon` erlaubt.
- **Fachlicher Grund:** Formgen baut seine Konzeptmodelle als 2,5D-Profilprismen für einen eigenen Rasterizer
  (`claude/generator/eng.py`, Blattvarianten C–J). BASIC verlangt dagegen echte 3D-Baugruppen mit Drehpunkten, Entnahmewegen,
  Explosionsansichten, Visierlinienprüfung und Bewegungsvorschauen. Das leistet Blender direkt. Ein zweiter Bauweg in Formgen würde
  dessen abgenommene Pipeline (150 Blätter, Golden-Hashes) berühren.
- **Keine doppelte Pipeline:** BASIC kopiert keinen Formgen-Code und keine Formgen-Daten. Bezugslängen werden mit Quelle zitiert
  (Formgen `wtypes.py`, Spec-Einheiten); die Formgen-Variante G und ihre IDs (KG01 …) bleiben unverändert und werden nicht umgedeutet.

## Zuständigkeit

| System | Zuständig | Hier |
|---|---|---|
| BASIC-Entwürfe, Modelle, Bauteilstruktur, Specs, Blätter, Bewegungsvorschauen der Mechanik | **cubeescape-ballon** | ja |
| Formgen-Konzeptblätter, Geometrie-Spec v1, Visier-Serie VS01–VS09 | Formgen | nur lesen |
| Spielassets, Fasen, UV, LOD, Ego-Arme, Use-/Ego-Clips, Roboter-Variante | Toolgen | nur lesen |
| Ego-Haltungen, Zustandsmaschine, Spielanbindung | Cube Escape | nur lesen |
| Referenzmessungen Destiny 2 | Motiongen (Repo `cubeescape-reference`) | nur lesen |

## Schnittstellen

| Richtung | Format | Status |
|---|---|---|
| Ausgabe Modell | `BASIC-NN.blend`, `BASIC-NN.glb` (Hierarchie Waffe → `ASM_<baugruppe>` → Bauteil, Anker als Empties `Socket_*`) | **exportiert** (lokal, `~/Library/Caches/CubeEscapeBallon/out/`) |
| Ausgabe Daten | `data/specs/BASIC-NN.spec.json`, Format `cubeescape-ballon/basic-spec` v1 ([spec.md](spec.md)) | **exportiert**, im Repo |
| Rahmen | Meter, vorn −Y, oben +Z, links +X, Ursprung `Socket_Hand` – identisch mit Formgen-Geometrie-Spec v1 und Toolgen | festgelegt |
| Toolgen-Import | Toolgen liest heute `cubeescape-design/geometry-spec` v1 mit Herkunftsnachweis (`concept_spec.py`, `data/concepts/provenance.json`) | **offen**: Export `BASIC-NN.geo.json` in diesem Format fehlt; Netze sind vorhanden |
| Anker-Namen | `Socket_Hand`, `Socket_SupportHand`, `Socket_Muzzle`, `Socket_CenterOfMass`, `Socket_Sight`, `Socket_Reticle`, `Socket_Eye` (Toolgen Vertrag 4/5); Bogen `Socket_Nock`, `Socket_ArrowTip` | übernommen |
| Clipnamen | Toolgen `<Name>_Use` und Ego-Suffixe (Idle, Fire, Reload …) | nicht erzeugt; Bewegungen hier sind Mechanik-Vorschauen |
| Nexogen-Register | `repos.json` kennt dieses Projekt noch nicht | **offen**, Änderung in Nexogen braucht Freigabe |

## Datenfluss

```
basic/weapons/wNN_*.py  (Entwurf: Bauteile, Baugruppen, Anker, Bewegungen; einzige Quelle)
        │  tools/blender_build.py  (Blender 5.2, bpy)
        ▼
<OUT>/BASIC-NN/  .blend · .glb · .spec.json · views/*.png · motion/<aktion>/*.png
        │  tools/sync_specs.py → data/specs/      tools/make_docs.py → docs/abdeckung.md, docs/haltungen.md, docs/bauteile/
        │  tools/make_sheets.py → <OUT>/sheets/*.html      tools/make_clips.py → <EVIDENCE>/clips/*.mp4
        ▼
Blätter, Kontaktbögen, Clips (Belege außerhalb des Repos)
```

Maßzahlen in Blättern und Dokumenten stammen ausschließlich aus dem gebauten Modell (`spec.json` › `dimensions`, `parts[].size_mm`).
