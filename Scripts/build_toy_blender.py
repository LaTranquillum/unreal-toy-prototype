"""Original segmented toy, rigid skinning and four authored animations. Blender 4.5."""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector, Quaternion
OUT=Path(__file__).resolve().parents[1]/'Art/ToyBlockout'
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene.render.fps=30
colors={'Jacket':(.13,.25,.39,1),'Pants':(.035,.045,.07,1),'Skin':(.72,.43,.25,1),'Hair':(.33,.12,.55,1),'Boots':(.67,.39,.09,1),'Steel':(.55,.65,.73,1),'Eyes':(.015,.025,.04,1),'White':(.9,.93,.95,1)}
colors.update({'Trim':(.22,.35,.48,1),'Leather':(.31,.15,.045,1),'SkinShade':(.29,.12,.07,1),'HairShade':(.14,.075,.24,1),'HairLight':(.47,.31,.62,1),'Iris':(.08,.30,.32,1),'PantsFold':(.052,.061,.075,1),'BootLight':(.74,.49,.19,1),'Badge':(.58,.055,.07,1)})
colors['Skin']=(.72,.47,.30,1)
colors['Hair']=(.32,.19,.45,1)
mats={}
for name,color in colors.items():
 m=bpy.data.materials.new(name);m.diffuse_color=color;m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=.52 if name in ('Jacket','Pants','Trim','PantsFold') else .36
 if name=='Steel':bs.inputs['Metallic'].default_value=.7
 mats[name]=m
bpy.ops.object.armature_add();rig=bpy.context.object;rig.name='ToyRig'
bpy.ops.object.mode_set(mode='EDIT');rig.data.edit_bones.remove(rig.data.edit_bones[0])
bones={}
def bone(name,h,t,parent=None):
 b=rig.data.edit_bones.new(name);b.head=h;b.tail=t
 if parent:b.parent=rig.data.edit_bones[parent]
 bones[name]=(Vector(h),Vector(t))
bone('root',(0,0,0),(0,0,.12))
bone('pelvis',(0,0,.84),(0,0,1.0),'root')
bone('spine',(0,0,1.0),(0,0,1.23),'pelvis')
bone('chest',(0,0,1.23),(0,0,1.4),'spine')
bone('head',(0,0,1.4),(0,0,1.68),'chest')
for side,x in [('l',1),('r',-1)]:
 bone('upperarm_'+side,(x*.24,0,1.34),(x*.33,0,1.09),'chest')
 bone('lowerarm_'+side,(x*.33,0,1.09),(x*.37,-.025,.88),'upperarm_'+side)
 bone('hand_'+side,(x*.37,-.025,.88),(x*.38,-.045,.77),'lowerarm_'+side)
 bone('thigh_'+side,(x*.115,0,.87),(x*.13,0,.49),'pelvis')
 bone('calf_'+side,(x*.13,0,.49),(x*.13,0,.13),'thigh_'+side)
 bone('foot_'+side,(x*.13,0,.13),(x*.13,-.20,.08),'calf_'+side)
bpy.ops.object.mode_set(mode='OBJECT')
parts=[]
def finish(o,name,mat,b):
 o.name=name;o.data.materials.append(mats[mat]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for f in o.data.polygons:f.use_smooth=True
 group=o.vertex_groups.new(name=b);group.add(list(range(len(o.data.vertices))),1,'REPLACE')
 parts.append(o);return o
def ell(name,loc,scale,mat,b):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=loc)
 o=bpy.context.object;o.scale=scale;return finish(o,name,mat,b)
def box(name,loc,scale,mat,b):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.scale=scale
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 mod=o.modifiers.new('Soft toy edges','BEVEL');mod.width=.022;mod.segments=3
 bpy.ops.object.modifier_apply(modifier=mod.name)
 return finish(o,name,mat,b)
def segment(name,a,b,r,mat,bn):
 a,b=Vector(a),Vector(b)
 bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=r*.85,radius2=r,depth=(b-a).length,location=(a+b)/2)
 o=bpy.context.object;o.rotation_mode='QUATERNION';o.rotation_quaternion=(b-a).to_track_quat('Z','Y')
 return finish(o,name,mat,bn)
sys.path.insert(0,str(Path(__file__).resolve().parent))
from toy_trunks_geometry import build
build(globals())
# Join skinned parts; preserve rigid vertex groups and material slots.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();mesh=bpy.context.object;mesh.name='SK_ToyBlockout'
mesh.parent=rig;mod=mesh.modifiers.new('Toy skin','ARMATURE');mod.object=rig
rig.animation_data_create()
def rotate(name,axis,degrees):
 pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION'
 local=rig.data.bones[name].matrix_local.to_quaternion().inverted()@Vector(axis)
 pb.rotation_quaternion=Quaternion(local,math.radians(degrees))
def offset(name,world):
 rig.pose.bones[name].location=rig.data.bones[name].matrix_local.to_quaternion().inverted()@Vector(world)
def reset():
 for pb in rig.pose.bones:pb.location=(0,0,0);pb.rotation_mode='QUATERNION';pb.rotation_quaternion=(1,0,0,0);pb.scale=(1,1,1)
from toy_motion import pose as authored_pose
def pose(kind,t):authored_pose(rig,kind,t)
lengths={'Idle':60,'Run':24,'Dodge':12,'Slash':17}
actions={}
for kind,n in lengths.items():
 act=bpy.data.actions.new('A_Toy'+kind);rig.animation_data.action=act
 for f in range(n+1):
  pose(kind,f/n)
  for pb in rig.pose.bones:
   pb.keyframe_insert('rotation_quaternion',frame=f+1);pb.keyframe_insert('location',frame=f+1)
 actions[kind]=act
rig.animation_data.action=None;reset();scene.frame_set(1)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);mesh.select_set(True);bpy.context.view_layer.objects.active=rig
common=dict(use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,mesh_smooth_type='FACE',axis_forward='-Y',axis_up='Z',apply_unit_scale=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0)
bpy.ops.export_scene.fbx(filepath=str(OUT/'SK_ToyBlockout.fbx'),bake_anim=False,**common)
for kind,n in lengths.items():
 rig.animation_data.action=actions[kind];scene.frame_start=1;scene.frame_end=n+1
 bpy.ops.export_scene.fbx(filepath=str(OUT/('A_Toy'+kind+'.fbx')),bake_anim=True,**common)
rig.animation_data.action=actions['Idle'];scene.frame_start=1;scene.frame_end=61;scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ToyBlockout.blend'))
report={'motion_revision':'staged anticipation and recovery','bones':len(rig.data.bones),'vertices':len(mesh.data.vertices),'materials':list(colors),'material_colors':colors,'revision':'Intricate reference detail pass','actions':list(lengths),'original_geometry':True,'all_vertices_weighted':all(len(v.groups)>0 for v in mesh.data.vertices)}
(OUT/'asset_report.json').write_text(json.dumps(report,indent=2));print('TOY BLENDER COMPLETE',report)

# A reusable studio view saved with the editable source, after FBX export.
scene.render.engine='CYCLES';scene.cycles.samples=32
scene.render.resolution_x=1000;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.world.color=(.18,.18,.18)
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(2.8,-5.5,2.6));camera=bpy.context.object;camera.name='PreviewCamera';camera.data.type='ORTHO';camera.data.ortho_scale=2.3;aim(camera,(0,0,.91));scene.camera=camera
for name,loc,power,size in [('Key',(-3,-4,5),450,4),('Fill',(4,-2,3),280,3),('Rim',(0,3,4),500,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.name=name;light.data.energy=power;light.data.shape='DISK';light.data.size=size;aim(light,(0,0,1))
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.003));floor=bpy.context.object;floor.name='PreviewGround'
fm=bpy.data.materials.new('StudioGround');fm.diffuse_color=(.08,.095,.12,1);floor.data.materials.append(fm)
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'Trunks_detail_preview.png')
bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ToyBlockout.blend'))
bpy.ops.render.render(write_still=True)

rig.animation_data.action=actions['Slash'];scene.frame_set(8);scene.render.filepath=str(OUT/'Trunks_slash_preview.png');bpy.ops.render.render(write_still=True)

rig.animation_data.action=actions['Idle'];scene.frame_set(1);camera.location=(1.3,-3,1.9);camera.data.ortho_scale=.90;aim(camera,(0,-.01,1.37));scene.render.filepath=str(OUT/'Trunks_detail_closeup.png');bpy.ops.render.render(write_still=True)
