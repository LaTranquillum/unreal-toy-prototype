# Face refinement

This local pass shortens the geometry above the brow region by 22%, draws the inner fringe inward, narrows the chin and jaw, and defines the cheekbone planes. The nose bridge and tip are sculpted into the continuous head surface rather than added as a separate mesh. Eye surfaces sit closer to the facial sockets, with upper eyelid skin and subtly asymmetric brows.

The new `Blink` morph closes the eye aperture and lowers the upper eyelid. Neutral, Focused and Shout remain available. Unreal evaluates a local 0.24-second blink every 4.2 seconds and suppresses it during sword attacks and dodges. Focused eye narrowing fades out during closure to prevent additive over-closing. This is a simple authored blink, not eye tracking or a full facial animation system.

The upper-body rig, hands, jacket, sword grip and combat timings are unchanged. Regeneration uses `Scripts/build_toy_blender.py -- --head-review`; the existing importer now requires `Blink` as well as `Focused` and `Shout`. `Scripts/preview_toy_head.py` captures natural full closure alongside the existing four expression checkpoints. `Scripts/verify_toy_head.py` checks that all three morphs affect only head-weighted vertices.

Review images are in `Art/ToyBlockout/Head_*.png` and `Face_blink_*.png`. Unreal captures are in `Saved/Verification/Head`. The pre-pass local backup is `Saved/FaceRefinementBackup`. This repository publishes original source and documentation only; generated assets remain local.

Validation completed: Blender face renders were reviewed at neutral, half blink and full closure. The initial morph-scope check passed for Focused, Shout and Blink. Unreal compilation and imports succeeded. The final runtime preview passed neutral, focused, shout, recovery and Blink checks; the full-closure screenshot was visually inspected with both eyes closed. The preview capture threshold was adjusted to avoid capturing the preceding transition frame. Ten verification runs were used across this pass. The later eyelid-depth correction was verified visually in Blender and Unreal; the morph-scope script was not repeated after that correction.

The face remains deliberately stylized, with angular cheek planes and graphic eyelid edges. The importer retained its existing bind-pose matrix warning; no gross deformation was visible in the reviewed face states. This is not a full-game regression test.
