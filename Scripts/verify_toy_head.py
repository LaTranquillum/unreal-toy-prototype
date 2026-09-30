"""Run in Blender after build_toy_blender.py; checks facial deformation scope."""
import bpy,json
from pathlib import Path
p=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(p/'Art/ToyBlockout/ToyBlockout.blend'))
mesh=bpy.data.objects['SK_ToyBlockout'];keys=mesh.data.shape_keys.key_blocks
assert set(keys.keys())=={'Basis','Focused','Shout','Blink'}
head=mesh.vertex_groups['head'].index
report={}
for name in ('Focused','Shout','Blink'):
    moved=[]
    for i,(a,b) in enumerate(zip(keys['Basis'].data,keys[name].data)):
        distance=(a.co-b.co).length
        if distance>1e-7:
            assert any(g.group==head and g.weight>.99 for g in mesh.data.vertices[i].groups), (name,i,'non-head deformation')
            moved.append(distance)
    assert len(moved)>100 and max(moved)>.005,(name,'empty or imperceptible target')
    assert keys[name].value==0,(name,'saved non-neutral default')
    report[name]={'moved_vertices':len(moved),'max_displacement_m':max(moved)}
# Finger bones may be added without changing the original head rig.
assert {'root','pelvis','spine','chest','head'}.issubset(bpy.data.objects['ToyRig'].data.bones.keys())
assert all(v.groups for v in mesh.data.vertices)
for view in ('front_neutral','threequarter_neutral','front_focused','threequarter_shout','gameplay_distance'):
    assert (p/('Art/ToyBlockout/Head_'+view+'.png')).is_file(),view
out=p/'Saved/Verification/head-blender.json';out.parent.mkdir(exist_ok=True,parents=True)
out.write_text(json.dumps(report,indent=2));print('HEAD VALIDATION PASSED',report)
