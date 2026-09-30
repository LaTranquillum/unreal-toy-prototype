"""Two targeted views for the shoulder and hair continuation."""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parents[1];sys.path.insert(0,str(p/'Scripts'))
from toy_motion import pose
bpy.ops.wm.open_mainfile(filepath=str(p/'Art/ToyBlockout/ToyBlockout.blend'))
rig=bpy.data.objects['ToyRig'];rig.animation_data.action=None
mesh=bpy.data.objects['SK_ToyBlockout'];assert len(rig.data.bones)==49
assert all(abs(sum(g.weight for g in v.groups)-1)<.001 for v in mesh.data.vertices)
assert {'Focused','Shout','Blink'}.issubset(mesh.data.shape_keys.key_blocks.keys())
pose(rig,'Idle',0)
s=bpy.context.scene;s.cycles.samples=12;s.render.resolution_x=720;s.render.resolution_y=900
c=s.camera;c.data.ortho_scale=1.25
for name,loc in [('front',(1.3,-3,1.65)),('rear',(-1.3,3,1.65))]:
 c.location=loc;c.rotation_euler=(Vector((0,0,1.28))-c.location).to_track_quat('-Z','Y').to_euler()
 s.render.filepath=str(p/f'Art/ToyBlockout/ShoulderHair_{name}.png');bpy.ops.render.render(write_still=True)
print('SHOULDER HAIR PASS: 49 bones, normalized weights, three expressions retained')
