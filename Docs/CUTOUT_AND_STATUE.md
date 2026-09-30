# Cutout player and rotating display statue

Normal arena play now uses the original camera-facing Trunks cutout with existing directional flipping and action artwork. The rigged character is reserved for explicit Toy3D or ToyShowcase runs.

A separate life-size skeletal display (authored approximately 1.8 m tall) holds the guard pose on a collision-enabled pedestal in the east-side lounge corner. The statue has no physics or character controller. It rotates around its vertical axis at 15 degrees/second, completing a turn every 24 seconds. A simple ivory sofa marks the lounge corner within the existing kitchen map; this is not a separate furnished living-room level. The rotation continues after the arena round ends.

Five verification runs: two successful C++ builds, two arena checks, and one full-turn display check. The first arena check failed the dodge-cooldown assertion while the cutout/statue and other gameplay checks passed; the second arena check passed all checks. This intermittent assertion was not treated as a proven fixed bug. DisplayVerify ran for 26 seconds and confirmed cutout visibility, statue loading, more than 360 degrees of accumulated rotation and three capture requests. All three screenshots were generated; front/back statue views were inspected.

Review images: Saved/Verification/display_0.png, display_1.png, display_2.png. Runtime evidence: Saved/Verification/arena.json and display.txt. Source backup: Saved/CutoutStatueBackup. No GitHub publication performed.
