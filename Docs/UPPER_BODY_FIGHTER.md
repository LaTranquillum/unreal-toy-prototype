# Upper-body fighter pass

This pass replaces separate sleeve segments with continuous curved sleeves and a tailored open jacket shell. Shoulder, elbow and wrist regions use normalized blended skin weights. The existing lower-body geometry is unchanged.

The skeleton retains its original 17 bones and adds 28 finger bones (three per finger, two per thumb on each hand), for 45 total. The right-hand geometry wraps around the sword's existing handle. Both hands have separate fingers and thumbs with small authored articulation; the sword remains attached to the right hand. This is an authored grip, not runtime finger IK or an arbitrary-object grasp system.

Idle now uses a breathing sword guard. Slash starts and ends in that guard, with windup, extension, follow-through and recovery. The existing 0.55-second Unreal action duration and damage timing are preserved. Capsule movement remains authoritative. Cloth simulation and new lower-body work are outside this pass.

## Review assets

- `Art/ToyBlockout/upper_body_turntable.mp4`: 36-view, 3-second Blender turntable at 12 fps.
- `Art/ToyBlockout/UpperBody_guard.png`, `UpperBody_windup.png`, `UpperBody_contact.png`, `UpperBody_followthrough.png`: pose review images.
- `Saved/Videos/upper_body_fighter_4s.mp4`: 120-frame Unreal capture at 30 fps, with two demonstrations of the same sword strike.
- `Art/ToyBlockout/upper_body_report.json`: finger count, normalized weights, blended arm vertices and guard/strike boundary checks.

Regenerate with Blender `--background --python /absolute/path/to/Scripts/build_toy_blender.py -- --fighter-review`. The build replaces generated Blender and FBX assets. Import with the existing Unreal `Scripts/import_toy_blockout.py`, compile with `Scripts/build.sh`, then run `python3 Scripts/capture_upper_body.py`.

A pre-pass backup is stored locally at `Saved/UpperBodyBackup`. These changes are local and have not been published. The character-reference rights exclusions remain unchanged.

Validation completed with Blender 4.5.9 and Unreal 5.8.2: 45 bones, 28 finger bones, 2,998 vertices using blended arm weights, normalized weights, and matching guard/strike entry poses. Motion continuity checks passed for all four clips. Unreal compiled and imported successfully; the three runtime checkpoints confirmed finger bones, capsule authority and expression transitions. Both video frame counts and durations were verified.

Reviewed front, side and rear turntable views, plus Unreal guard, strike and recovery frames. No gross hand/sleeve distortion was visible despite the FBX importer reporting differing bind-pose matrices. The fingers remain fitted around the handle through the reviewed poses. The result retains a stylized toy appearance; it is not a production anatomical hand rig or cloth simulation. This pass does not establish full-game regression coverage.

Seven verification runs were used, including the initial render interrupted to correct the elbow direction. No repeated full gameplay suite was run.
