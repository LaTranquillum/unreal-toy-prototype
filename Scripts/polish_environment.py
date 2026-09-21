"""Presentation-only kitchen pass. Preserve actor transforms and collision."""
import unreal,json
from pathlib import Path
E=unreal.MaterialEditingLibrary
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
T=unreal.AssetToolsHelpers.get_asset_tools()
folder='/Game/Toy/EnvironmentPolish';unreal.EditorAssetLibrary.make_directory(folder)
L.load_level('/Game/Toy/Maps/ToyLab')
def mat(name,color,rough,metal=0,emission=0):
 m=unreal.load_asset(folder+'/'+name) or T.create_asset(name,folder,unreal.Material,unreal.MaterialFactoryNew())
 E.delete_all_material_expressions(m)
 c=E.create_material_expression(m,unreal.MaterialExpressionConstant3Vector);c.set_editor_property('constant',unreal.LinearColor(*color,1));E.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
 for v,p in [(rough,unreal.MaterialProperty.MP_ROUGHNESS),(metal,unreal.MaterialProperty.MP_METALLIC)]:
  n=E.create_material_expression(m,unreal.MaterialExpressionConstant);n.set_editor_property('r',v);E.connect_material_property(n,'',p)
 if emission:
  e=E.create_material_expression(m,unreal.MaterialExpressionConstant3Vector);e.set_editor_property('constant',unreal.LinearColor(*(x*emission for x in color),1));E.connect_material_property(e,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 E.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m);return m
mats={'floor':mat('M_WarmStone',(.22,.205,.18),.66),'cabinet':mat('M_SatinIvory',(.58,.56,.50),.36),'stone':mat('M_StoneCounter',(.37,.39,.38),.25),'dark':mat('M_Graphite',(.026,.032,.036),.31),'metal':mat('M_ChampagneMetal',(.36,.29,.19),.28,.75),'light':mat('M_WarmStrip',(.95,.72,.43),.3,0,2)}
cube=unreal.load_asset('/Engine/BasicShapes/Cube')
def detail(name,loc,size,material):
 a=A.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*loc));a.set_actor_label('Environment polish | '+name)
 c=a.static_mesh_component;c.set_static_mesh(cube);c.set_material(0,mats[material]);c.set_collision_profile_name('NoCollision');c.set_editor_property('can_ever_affect_navigation',False)
 a.set_actor_enable_collision(False);a.set_actor_scale3d(unreal.Vector(*(v/100 for v in size)));return a
for a in list(A.get_all_level_actors()):
 if a.get_actor_label().startswith('Environment polish |'):A.destroy_actor(a)
originals=list(A.get_all_level_actors());before={a.get_actor_label():str(a.get_actor_transform()) for a in originals if isinstance(a,unreal.StaticMeshActor)}
changed=[]
for a in originals:
 label=a.get_actor_label()
 if isinstance(a,unreal.StaticMeshActor):
  material=None
  if label=='Toy arena floor':material='floor'
  elif 'cabinet' in label or label=='Kitchen | tall pantry' or label.startswith('Navigation obstacle'):material='cabinet'
  elif 'stone top' in label or 'stone counter' in label:material='stone'
  elif label=='Round obstacle':material='dark'
  if material:a.static_mesh_component.set_material(0,mats[material]);changed.append(label)
  if label.startswith('Kitchen | base cabinet'):
   p=a.get_actor_location();detail(label+' handle',(p.x,p.y-46,82),(125,2,1.3),'metal')
  if label in ['North wall','South wall','East wall','West wall']:
   p=a.get_actor_location();scale=a.get_actor_scale3d();sx,sy,sz=abs(scale.x)*100,abs(scale.y)*100,abs(scale.z)*100
   # Thin interior frame; preserve every original wall and its collision.
   along_x=sx>sy;face=p.y if along_x else p.x
   sign=-1 if face>0 else 1
   for z in [p.z-sz/2+2,p.z+sz/2-2]:
    loc=(p.x,p.y+sign*(sy/2+1),z) if along_x else (p.x+sign*(sx/2+1),p.y,z)
    detail(label+' horizontal '+str(z),loc,(sx,2,3) if along_x else (2,sy,3),'metal')
   for end in [-1,1]:
    loc=(p.x+end*(sx/2-2),p.y+sign*(sy/2+1),p.z) if along_x else (p.x+sign*(sx/2+1),p.y+end*(sy/2-2),p.z)
    detail(label+' vertical '+str(end),loc,(3,2,sz) if along_x else (2,3,sz),'metal')
 elif isinstance(a,unreal.DirectionalLight):
  key=label=='Soft key light';c=a.light_component
  c.set_editor_property('intensity',1.15 if key else .12);c.set_editor_property('light_source_angle',6.0);c.set_editor_property('cast_shadows',key)
  c.set_light_color(unreal.LinearColor(1,.92,.81,1) if key else unreal.LinearColor(.82,.90,1,1))
# Small visual reveal lines give the existing islands an intentional base and top.
for label,p,size in [('island A toe',(170,160,5),(142,272,8)),('island B toe',(-400,250,5),(242,102,8))]:detail(label,p,size,'dark')
for label,p,size in [('island A trim',(170,160,139),(159,289,1.3)),('island B trim',(-400,250,89),(259,119,1.3))]:detail(label,p,size,'metal')
detail('under cabinet light',(-150,835,221),(1390,3,2),'light')
detail('counter front reveal',(-50,726,96),(1598,2,1.2),'metal')
# A restrained rectangular light makes the rear counter readable; no new geometry collision.
light=A.spawn_actor_from_class(unreal.RectLight,unreal.Vector(-150,740,225),unreal.Rotator(-65,90,0));light.set_actor_label('Environment polish | counter light')
c=light.light_component;c.set_mobility(unreal.ComponentMobility.MOVABLE);c.set_editor_property('intensity_units',unreal.LightUnits.LUMENS);c.set_editor_property('intensity',350);c.set_editor_property('attenuation_radius',700);c.set_editor_property('source_width',1000);c.set_editor_property('source_height',40);c.set_editor_property('cast_shadows',False);c.set_light_color(unreal.LinearColor(1,.83,.64,1))
after={a.get_actor_label():str(a.get_actor_transform()) for a in originals if isinstance(a,unreal.StaticMeshActor)}
assert before==after,'Original geometry transform changed'
L.save_current_level();unreal.EditorAssetLibrary.save_directory(folder)
report={'saved':True,'original_mesh_transforms_preserved':before==after,'material_assignments':changed,'new_details_have_no_collision':True,'mirror_method':'Existing shared live cubemap retained; frames only, not planar mirrors'}
(Path(unreal.Paths.project_saved_dir())/'Verification/environment-polish.json').write_text(json.dumps(report,indent=2))
unreal.log('ENVIRONMENT POLISH SAVED')
