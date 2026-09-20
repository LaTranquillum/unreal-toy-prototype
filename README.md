# Unreal Toy Prototype

Source code for a local autonomous toy-character prototype in Unreal Engine 5.8.2 on macOS. Includes local intent selection, AIController/NavMesh movement, path-failure and stuck recovery, capsule collision, and optional camera-facing 2D pose actions. No runtime language-model service is required.

This is a **source-only repository**, not a standalone game download. The original demonstration's character artwork, screenshots, maps, mannequin assets, and generated binary assets are deliberately excluded. No Unreal Engine source or binaries are distributed.

## Build

Install Unreal Engine 5.8 and its macOS development prerequisites. Run `zsh Scripts/build.sh`; for a custom engine installation use `UNREAL_ENGINE_ROOT="/path/to/UE_5.8" zsh Scripts/build.sh`.

## Asset setup

Before running `Scripts/setup_scene.py` through Unreal's Python commandlet, supply a compatible mannequin and animations under `/Game/Mannequin/Character/Mesh/SK_Mannequin`, `/Game/Mannequin/Character/Mesh/SK_Mannequin_PhysicsAsset`, `/Game/Mannequin/Animations/ThirdPersonIdle` and `/Game/Mannequin/Animations/ThirdPersonWalk`. Obtain assets separately under their own licenses. The setup script then generates ToyLab. It overwrites that generated level, so back up manual changes first.

Kitchen and mirror setup scripts are optional. The image-cutout, action-pose and manga-floor import scripts require separately supplied artwork at their documented Art/Reference paths. Those images are not included or licensed by this repository. A fresh source checkout has not been validated as a complete game installation.

## Autonomous demo controls (`-ToyDemo`)

1 Stop, 2 Wander, 3 Look, 4 Sway, 5 Jump, 6 Bend, 7 Crawl, 8 Sword swing, 0/A Auto. Image poses require the optional artwork. Crawl retains the full-height collision capsule; sword swing is visual and has no damage system. Physical animation does not implement balance recovery.

The compact bottom toolbar can be collapsed with **Tab** or its show/hide label. Keyboard actions remain available while collapsed.

## Verification

`Scripts/verify.sh` exercises navigation, recovery and collisions in a configured ToyLab. `python3 Scripts/verify_controls.py` checks command dispatch and optional image actions. `Scripts/capture.sh` saves gameplay renders. These scripts currently use the standard macOS engine path; the build entry point accepts an override. Run them only after supplying assets and generating the level.

## License and provenance

Original project code and documentation are MIT licensed. Unreal Engine and third-party assets are not covered. Development was assisted by OpenAI Codex; maintainers remain responsible for reviewing changes. No independent human review or eligibility certification is implied.

## Compact toolbar validation (2026-09-19)

Validated in the configured local Unreal 5.8.2 project: native build passed; injected Tab collapsed controls; keys 1–8 worked while collapsed; the toggle HUD callback expanded controls; Auto callback passed. A 1280 × 900 gameplay render confirmed the bottom layout. Physical OS clicks and keyboard focus were not simulated. Five checks including two builds, two input runs, and one render run; all passed. Source-only fresh-checkout gameplay remains unverified because third-party assets are intentionally excluded.

On systems where shell script executable bits are absent, invoke them using `zsh Scripts/build.sh`, `zsh Scripts/verify.sh`, and `zsh Scripts/capture.sh`.

## Portrait presentation (autonomous demo and captures)

The demo follow camera uses a closer 9:16 composition. In a landscape Play window,
Unreal adds side bars; the capture script requests a 720 × 1280 portrait window.

After generating ToyLab, optionally run `Scripts/setup_kitchen.py`, then apply
`Scripts/polish_video.py` using Unreal's Python commandlet. For example on macOS:

```sh
"/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor-Cmd" \
  "$PWD/ToyPrototype.uproject" -run=pythonscript \
  -script="$PWD/Scripts/polish_video.py" -unattended -nosound -nullrhi
zsh Scripts/capture.sh
```

Back up the level before applying the script. It saves ToyLab, replaces the existing
manga-floor actors with three non-colliding inset panels, gives the arena floor a
warm-grey material, and adjusts the directional lights plus two broad fill lights.
Running it again replaces its panels and fill lights rather than duplicating them.

Manga materials are optional: `/Game/Toy/MangaRug/M_Panel_1`, `M_Panel_4`, and
`M_Panel_5`. Missing materials produce labeled plain insets and warnings. No image
imports are performed. A missing ToyLab produces an actionable error before edits.
Artwork, generated maps, and gameplay screenshots remain excluded from this repo.

The configured Unreal 5.8.2 project built successfully and rendered the existing
action sequence at 720 × 1280. Framing, floor layout, and lighting were visually
inspected; this does not validate a complete game installation from a fresh checkout.

An isolated minimal Unreal scene also verified missing-map errors, plain-material
fallback without artwork, non-colliding panels, portrait camera settings, and
repeat application without duplicate actors. That check reused the locally built
module; it was not a fresh-checkout build or a full gameplay test.

## Kitchen combat slice

ToyLab now starts a 60-second single-player combat round: WASD movement, mouse aim, click/8 sword attack, Shift dodge, Space jump, and R restart. A shooting drone, health pickup, score, and adaptive camera provide a small arena loop. See [controls, setup context, and validation](Docs/COMBAT_SLICE.md). Run `zsh Scripts/play_arena.sh -ToyDemo` for the original autonomous demo.

This remains a source-only repository. Generate ToyLab and supply the previously documented assets first; the local Trunks artwork and generated maps are not included. The combat drone uses engine primitive shapes.
