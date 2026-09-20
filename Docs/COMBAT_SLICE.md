# Kitchen arena combat slice

Play ToyLab to start a 60-second single-player round. For a fresh standalone process after building, run `zsh Scripts/play_arena.sh`. Restart an already-open editor to load the rebuilt C++ module.

- WASD: camera-relative movement.
- Mouse: aim on the character's horizontal plane.
- Left click or 8: sword slash (windup 0.12s, active through 0.30s, recovery through 0.55s).
- Shift: directional dodge, using movement direction or aim when standing; 1s cooldown and 0.18s damage immunity.
- Space: jump.
- R: restart the round.

The drone approaches, strafes at firing distance, and draws an orange warning line before firing a projectile along that locked direction. Sword hits require range, facing, and an unobstructed line to the drone; each swing deals damage at most once. Three hits defeat a drone for 100 points; another appears after 2.5 seconds. Enemy projectiles sweep against scene collision and deal 20 damage. The gold pickup in the open southern lane restores 35 health and reappears after 8 seconds. Health reaching zero or time expiring ends the round.

The kitchen's existing islands create routes and block the capsule and projectiles. The wider combat camera follows the player and partially includes the opponent. The HUD shows health, score, round time, and dodge availability. Trails, sparks, a telegraph, damage flash, restrained camera shake, and synthesized sound cues provide combat feedback.

This slice retains the existing billboard character and two sword poses. It does not add a rig, full running animation, multiplayer, a player ranged weapon, or tactical autonomous Trunks combat. `-ToyDemo` starts the original autonomous command demo; existing `-ToyCapture`, `-ToyVerify`, and `-ToyControlVerify` also retain their prior behavior. The game is capsule-driven; no ragdoll balance is claimed.

`-ArenaVerify` runs a bounded Unreal integration scenario and writes `Saved/Verification/arena.json` and `arena.png`. It exercises gameplay handlers and movement, not physical keyboard/mouse focus. Validation results are reported separately after running it.

Run `python3 Scripts/verify_arena.py` for one bounded verification invocation (180-second process timeout, with the JSON result checked explicitly). The camera widens with fighter separation; respawns choose a distant predefined open location. Drone geometry is an explicitly simple placeholder built from engine shapes. Audio uses short synthesized tones rather than supplied sound assets.

## Validation — 2026-09-20

Built successfully with Unreal Engine 5.8.2. The final staged runtime scenario passed all assertions for movement, dodge displacement/cooldown, one sword hit per swing, scoring, drone respawn, projectile damage, pickup healing, jump/landing, island collision, round expiry, restart, and defeat. The final 1280×800 capture was inspected for fighter framing, HUD readability, and removal of the placeholder label.

Nine build/runtime invocations total: six builds (one initial compiler failure, five successful) and three runtime scenarios (one initial failure, two successful). The first runtime failure led to collision-channel and startup-speed fixes and replacement of fixed-timestamp checks with staged verification. No physical keyboard/mouse focus test or subjective audio playback review was performed; movement animation still uses the original image cutout and bobbing.
