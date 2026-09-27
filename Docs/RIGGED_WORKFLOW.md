# Rigged toy, motion, environment and showcase workflow

The default combat mode can now use a Blender-generated, 49-bone fighter rig with idle, run, dodge and sword clips. Capsule movement remains authoritative. Missing or incompatible assets retain the original appearance; `-Toy2D` explicitly selects that fallback. Secondary physics is disabled for this rig, and there is no fitted Physics Asset, runtime foot IK, cloth simulation, or balance controller.

## Generate and import

The scripts were exercised with Blender 4.5.9 LTS and Unreal Engine 5.8.2 on macOS. Start with the configured ToyLab described in the README; this is not a complete fresh-checkout asset bootstrap.

Back up custom work before running these scripts. Blender generation replaces the scene and writes `Art/ToyBlockout/`; Unreal import replaces assets under `/Game/Toy/Blockout/`. Generated content stays ignored by Git.

```sh
/path/to/Blender --background --python Scripts/build_toy_blender.py
/path/to/UnrealEditor-Cmd "$PWD/ToyPrototype.uproject" \
  -run=pythonscript -script="$PWD/Scripts/import_toy_blockout.py" \
  -unattended -nosound -nullrhi
zsh Scripts/build.sh
```

`toy_trunks_geometry.py` constructs a stylized reference-inspired character. It includes curved hair, garment seams and stitching, belt hardware, sleeve emblem, boot details and sword/scabbard fittings. All vertices have weights; the current vertex count is recorded by each build in `Art/ToyBlockout/asset_report.json`. `toy_motion.py` supplies continuous poses with run counter-rotation, staged dodge recovery and sword anticipation/follow-through. The in-place clips remain simplified; clothing intersections and foot sliding during locomotion can occur. Guard and strike have baked planted-foot poses, not runtime ground adaptation.

The scripts are original code; the MIT license does not grant rights to the Trunks character, Capsule insignia, or third-party reference artwork. No reference image, generated mesh, Blender file, screenshot or video is distributed here. Adapt the geometry and branding for your own character as appropriate.

## Environment

After optional kitchen setup, run `Scripts/polish_environment.py` through the same Unreal Python commandlet. It saves ToyLab with warm stone, satin cabinets, metallic trim, mirror frames and a counter light. New decorative meshes have no collision; original static-mesh transforms are checked before saving. Back up the map first.

Mirror frames retain the existing shared cubemap reflection. This is approximate, not planar or recursive, and is understated from the combat camera. Glass remains a simple translucent material. No rendering-performance claim is made.

## Video

```sh
python3 Scripts/make_showcase_video.py
```

With ffmpeg on PATH and assets configured, this launches `-ToyShowcase` and writes `Saved/Videos/trunks_3d_showcase_15s.mp4`: silent H.264, 720 x 1280, 30 fps, 450 frames. The camera follows a scripted idle/run/dodge/sword sequence with the HUD hidden. This is a presentation mode, not autonomous combat. The previous 2D montage remains available through `make_action_video.py` and requires separate artwork. `UNREAL_ENGINE_ROOT` overrides the default macOS engine path for these exporters.

Offline rendering takes longer than 15 seconds. Both exporters validate the frame sequence before encoding. The showcase has a 900-second render timeout and 120-second encoding timeout. Five sample frames remain beside the output.

## Validation and limits

In the configured local project: the Unreal editor target built successfully; the refined mesh and four clips imported; all 19 fixed-30-Hz combat/rig assertions passed after the final character update. `Scripts/verify_toy_motion.py`, run through Blender, checks continuous pose endpoints and bounded pose changes. `python3 Scripts/verify_arena.py` checks movement, combat, collisions, resets and rig motion, rather than physical keyboard input.

The showcase generated and ffprobe decoded 450 frames at 720 x 1280 and exactly 15 seconds. That video predates the final intricate-detail geometry pass and was not regenerated afterward. Studio close-ups and gameplay poses were separately inspected for the final geometry. These results do not establish fresh-checkout playability, variable-frame-hitch robustness, deterministic physics, or final cinematic quality.

Development and validation were assisted by OpenAI Codex. No independent review, external maintainer endorsement, or contributor-program eligibility is claimed.


## Current character review commands

Generate the character before importing and reviewing it. Use `-- --head-review`
for facial renders or `-- --finish-review` for a full-body turntable and planted-foot
checks with the Blender generation command above. Install ffmpeg on PATH for video
encoding. Run `Scripts/review_shoulder_hair.py` through Blender for two targeted
views after generation. `python3 Scripts/capture_upper_body.py` runs a four-second
Unreal guard/strike capture; `python3 Scripts/preview_toy_head.py` checks expression
states and a natural blink. Both require the configured ToyLab and compiled module.

Blender has procedural cloth microtexture and sheen; Unreal receives shared base
color, roughness, metallic and specular values, not those procedural nodes.
The milestone documents preserve the checks performed at each stage, including
older bone counts; the current rig has 49 bones. Refer to the face, upper-body,
fighter-finish and shoulder/hair notes for remaining limitations.
