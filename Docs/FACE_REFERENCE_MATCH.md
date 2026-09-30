# Reference face refinement

Reference: the user-provided trunks.jpg figurine photograph. This pass follows its compact lower face, tiny nose and mouth, angled teal eyes and fuller lavender curtain fringe. The lower face is shortened, the mouth narrowed, the nose and bridge reduced, the brows angled and the bangs brought closer to the center. A slimmer neck supports these proportions. The changes apply consistently to Basis, Focused, Shout and Blink morphs.

Rebuilt the Blender model and exported mesh and four animation clips, then imported into Unreal 5.8. The original source is backed up in Saved/FaceReferenceBackup.

Five verification runs: initial build/render, final build/render with neck refinement, head morph validation, Unreal import, and Unreal runtime expression preview. Morph checks passed; import completed with zero errors and seven warnings, including the existing bind-pose warning. Runtime neutral, focused, shout, recovery and closed-blink checkpoints passed. Blender neutral and blink renders and Unreal neutral and closed-blink captures were visually inspected.

This is an approximation of the photographed figurine, not an exact sculpt. The layered hair still has a stylized toy finish and the mouth/shout remain simplified. This was a face-focused review, not a full gameplay regression. No GitHub publication was performed for this pass.

## Rounder eye correction

In response to the reference comparison, increased eye aperture height from .0105 to .018 and half-width from .037 to .039; reduced the outer-corner tilt from .009 to .005. Enlarged the teal irises and pupils while retaining their slightly inward placement. The Focused morph now preserves 84% of eye height rather than 72%, keeping a rounder silhouette beneath the lowered brows. Updated eyelid sheets and blink closure formulas to match.

Four verification runs for this correction: Blender build/render, head morph validation, Unreal import, and runtime expression capture. All passed; import retained seven warnings and no errors. Inspected the neutral and closed-blink Blender renders and the focused Unreal capture. Saved prior source as Saved/FaceReferenceBackup/toy_head_before_round_eyes.py.

## Lower jaw, mouth and neck correction

Reduced the excessive lower-face compression: the vertical proportion factor below eye level is now .96 rather than .79. Widened the mouth group from .68 to .88 of its authored width and lowered it .003 m before the proportion transform, restoring nose/lip/chin spacing. Replaced the ellipsoidal neck with a subdivided seven-ring loft: broad root inside the shirt, narrower middle, and wider insertion under the jaw. The neck remains weighted to the existing head bone.

Four verification runs: Blender build/render, morph validation, Unreal import, and Unreal expression capture. All passed. Import completed with zero errors and the seven existing warnings. Inspected neutral and shout Blender renders and the Unreal neutral close-up; runtime neutral, focused, shout, recovery and full-blink checkpoints passed. This is a proportion correction, not a new anatomical or facial rig. Backup: Saved/FaceReferenceBackup/toy_head_before_jaw_neck.py.
