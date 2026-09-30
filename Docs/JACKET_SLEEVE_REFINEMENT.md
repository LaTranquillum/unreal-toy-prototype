# Jacket and sleeve refinement — steps 1–2

The jacket shell and sleeves are fused into one connected garment surface. The chest is flatter, the shoulders join the torso, the upper arms taper into shaped forearms, and the cuffs are slimmer. Restrained elbow and upper-arm folds are built into the surface. Existing pockets, stitching and edge details are fitted to the revised chest profile.

Skin weights blend spatially from the chest into the upper arms and through the elbows to the forearms. The torso retains spine/chest blending and the existing small hem influence. A connected-component assertion checks shoulder continuity before export. The review checks weight normalization and guard-to-strike pose continuity.

Five verification runs: two Blender build/reviews, two Unreal imports, and one Unreal action capture. A pocket-fitting correction followed the first side-view inspection. Both imports completed with zero errors and seven warnings, including the existing bind-pose warning. The final Blender review passed structural checks and produced a 24-frame close-up turntable plus guard, windup, contact and follow-through renders. Front, side, back and contact views were inspected. The four-second Unreal capture passed all three checkpoints (frames 20, 37 and 65); guard and strike screenshots were visually inspected.

Outputs: Art/ToyBlockout/jacket_turntable.mp4, Art/ToyBlockout/JacketTurntable, Art/ToyBlockout/UpperBody_*.png, and Saved/Videos/upper_body_fighter_4s.mp4. Backups: Saved/JacketSleeveBackup. Add --jacket-review alongside --fighter-review to generate the closer turntable.

Limitations: the fused garment is a dense prototype surface (144,852 vertices; full character 309,760 vertices), not optimized game topology or cloth simulation. Small accessories remain separate meshes. Hands, trousers, face and combat timings were not redesigned in this pass. No GitHub publication was performed.

## Mesh reduction — 2026-09-29

Applied collapse reduction to the fused garment before skin-weight assignment and shape-key creation. Jacket vertex count fell from 144,852 to 31,869 (78% reduction), with 63,734 triangles. Full character vertex count fell from 309,760 to 196,777. The maximum bidirectional vertex-to-surface distance against the dense garment was 0.0003294 m (0.33 mm in authored units); this is a vertex-based measurement, not a continuous Hausdorff bound. The generator rejects deviation above .003 m and disconnected garment components, then recomputes analytic skin weights.

Three verification runs passed: Blender build/turntable/pose checks, Unreal import (zero errors, seven existing warnings), and four-second Unreal capture (checkpoints 20, 37 and 65). Front and back Blender views and the Unreal strike frame were visually inspected. Report: Art/ToyBlockout/jacket_mesh_optimization.json. Source backup: Saved/MeshOptimizationBackup/toy_upper_body.py.

This supersedes the dense garment counts above. It is a prototype density reduction, not hand-authored deformation topology, LOD generation, or a measured frame-rate improvement. Other body meshes and facial proportions were preserved.
