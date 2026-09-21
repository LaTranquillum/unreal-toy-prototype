"""Check authored pose boundaries and continuity in Blender, before Unreal import."""
import bpy,sys,json,math
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'Scripts'))
from toy_motion import pose
bpy.ops.wm.open_mainfile(filepath=str(root/'Art/ToyBlockout/ToyBlockout.blend'))
rig=bpy.data.objects['ToyRig'];rig.animation_data.action=None
report={}
def snapshot():return {b.name:(b.rotation_quaternion.copy(),b.location.copy()) for b in rig.pose.bones}
for kind in ['Idle','Run','Dodge','Slash']:
 pose(rig,kind,0);first=last=snapshot();max_angle=max_translation=0
 for i in range(1,601):
  pose(rig,kind,i/600);current=snapshot()
  for name,(q,p) in current.items():
   angle=last[name][0].rotation_difference(q).angle;angle=min(angle,math.tau-angle)
   max_angle=max(max_angle,math.degrees(angle));max_translation=max(max_translation,(p-last[name][1]).length)
  last=current
 seam=max(min(first[n][0].rotation_difference(last[n][0]).angle,math.tau-first[n][0].rotation_difference(last[n][0]).angle) for n in first)
 assert seam<.001,(kind,'endpoint discontinuity',seam)
 assert max_angle<3,(kind,'rotation jump',max_angle)
 assert max_translation<.01,(kind,'translation jump',max_translation)
 report[kind]={'continuous_endpoints':True,'max_rotation_step_degrees':max_angle,'max_translation_step_m':max_translation}
report['passed']=True
(root/'Saved/Verification/motion-continuity.json').write_text(json.dumps(report,indent=2))
print('MOTION CONTINUITY PASS',report)
