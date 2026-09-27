# Head refinement milestone

The head uses curved overlapping fringe and side locks, a recessed rear hair volume, a smoother tapered jaw, almond-shaped eye surfaces with separate eyelids and irises, sculpted nose bridge/tip, ear folds, and lip accents. The body, 17-bone skeleton and four locomotion/action clips retain their existing design.

Neutral is the Basis shape. Focused narrows the eyes and lowers the inner brows. Shout adjusts the brows, jaw, lips, mouth cavity, teeth and tongue. These are stylized toy expression targets, not a production facial rig or lip-sync system. Hair stays weighted to the head; this milestone does not add strand physics.

`ToyBlockoutAnim` blends focused during movement/dodge and shout during the existing sword action. It fades back to neutral at rest. The importer requires both `Focused` and `Shout` morph targets.

## Rebuild and inspect

Run Blender with `--background --python Scripts/build_toy_blender.py -- --head-review` using an absolute script path. This regenerates the character FBXs and editable `Art/ToyBlockout/ToyBlockout.blend`, plus five head review renders. Omit `--head-review` to also render the older full-character studio views.

Run `Scripts/import_toy_blockout.py` through the installed Unreal Python commandlet, then build with `Scripts/build.sh`. Generation/import replaces the generated assets: preserve hand edits first. The pre-milestone local backup is in `Saved/HeadRefinementBackup`.

Run Blender with `--background --python Scripts/verify_toy_head.py` to check that morphs only deform head vertices, the 17-bone rig remains weighted, and the saved default is neutral. Run `python3 Scripts/preview_toy_head.py` for four Unreal captures and expression-weight checks: neutral, focused, shout, and return to neutral. These checks require the configured local ToyLab and imported assets.

Blender renders are in `Art/ToyBlockout/Head_*.png`. Runtime captures are in `Saved/Verification/Head`. The Blender review includes front, three-quarter and full-body/gameplay-scale views; the latter is a studio view, not an Unreal screenshot.

The source remains a local change for this milestone. Generated artwork and assets are not automatically published. Existing rights exclusions for the reference character still apply.

## Validation

Blender 4.5.9 generated 80,748 weighted vertices on the existing 17-bone rig. Both morph targets passed the head-only deformation check. Unreal 5.8.2 compiled and imported both targets. The final runtime capture reported neutral weights 0/0, focused 1/0, shout 0/0.995, and recovered neutral 0/0. The missing morph-material usage flags were corrected; the final runtime log no longer reports that warning.

The initial review found one missing eye white in Unreal caused by reversed triangle winding on the mirrored eye surface. The authorized follow-up corrected that winding and added an outward-normal assertion for both eyes. Regeneration, Unreal import and the four-state runtime preview passed (three follow-up verification runs). Focused and shout captures were visually inspected: both eye whites are visible, and the runtime log contains no missing morph-material warnings. This resolves the known visual blocker for the head milestone.
