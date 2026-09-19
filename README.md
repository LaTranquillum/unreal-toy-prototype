# Unreal Toy Prototype

Source code for a local autonomous toy-character prototype in Unreal Engine 5.8.2 on macOS. Includes local intent selection, AIController/NavMesh movement, path-failure and stuck recovery, capsule collision, and optional camera-facing 2D pose actions. No runtime language-model service is required.

This is a **source-only repository**, not a standalone game download. The original demonstration's character artwork, screenshots, maps, mannequin assets, and generated binary assets are deliberately excluded. No Unreal Engine source or binaries are distributed.

## Build

Install Unreal Engine 5.8 and its macOS development prerequisites. Run `./Scripts/build.sh`; for a custom engine installation use `UNREAL_ENGINE_ROOT="/path/to/UE_5.8" ./Scripts/build.sh`.

## Asset setup

Before running `Scripts/setup_scene.py` through Unreal's Python commandlet, supply a compatible mannequin and animations under `/Game/Mannequin/Character/Mesh/SK_Mannequin`, `/Game/Mannequin/Character/Mesh/SK_Mannequin_PhysicsAsset`, `/Game/Mannequin/Animations/ThirdPersonIdle` and `/Game/Mannequin/Animations/ThirdPersonWalk`. Obtain assets separately under their own licenses. The setup script then generates ToyLab. It overwrites that generated level, so back up manual changes first.

Kitchen and mirror setup scripts are optional. The image-cutout, action-pose and manga-floor import scripts require separately supplied artwork at their documented Art/Reference paths. Those images are not included or licensed by this repository. A fresh source checkout has not been validated as a complete game installation.

## Controls

1 Stop, 2 Wander, 3 Look, 4 Sway, 5 Jump, 6 Bend, 7 Crawl, 8 Sword swing, 0/A Auto. Image poses require the optional artwork. Crawl retains the full-height collision capsule; sword swing is visual and has no damage system. Physical animation does not implement balance recovery.

## Verification

`Scripts/verify.sh` exercises navigation, recovery and collisions in a configured ToyLab. `python3 Scripts/verify_controls.py` checks command dispatch and optional image actions. `Scripts/capture.sh` saves gameplay renders. These scripts currently use the standard macOS engine path; the build entry point accepts an override. Run them only after supplying assets and generating the level.

## License and provenance

Original project code and documentation are MIT licensed. Unreal Engine and third-party assets are not covered. Development was assisted by OpenAI Codex; maintainers remain responsible for reviewing changes. No independent human review or eligibility certification is implied.
