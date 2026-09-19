"""Apply a pared-back kitchen to the existing ToyLab; preserve AI and capsule."""
import unreal
from pathlib import Path
import json
E=unreal.MaterialEditingLibrary
assets=unreal.AssetToolsHelpers.get_asset_tools()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
folder='/Game/Toy/Kitchen'
unreal.EditorAssetLibrary.make_directory(folder)
def material(name,color,roughness=.6,metallic=0,opacity=None):
 m=unreal.load_asset(folder+'/M_'+name)
 if not m:m=assets.create_asset('M_'+name,folder,unreal.Material,unreal.MaterialFactoryNew())
 else:E.delete_all_material_expressions(m)
 if opacity is not None:
  m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT)
  m.set_editor_property('two_sided',True)
  m.set_editor_property('translucency_lighting_mode',unreal.TranslucencyLightingMode.TLM_SURFACE)
 c=E.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-300,0)
 c.set_editor_property('constant',unreal.LinearColor(*color,1))
 assert E.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
 for i,(value,prop) in enumerate([(roughness,unreal.MaterialProperty.MP_ROUGHNESS),(metallic,unreal.MaterialProperty.MP_METALLIC)]+([] if opacity is None else [(opacity,unreal.MaterialProperty.MP_OPACITY)])):
  n=E.create_material_expression(m,unreal.MaterialExpressionConstant,-300,100+i*100)
  n.set_editor_property('r',value)
  assert E.connect_material_property(n,'',prop)
 E.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m)
 return m
mats={
 'Plaster':material('WarmPlaster',(.68,.65,.59),.85),
 'Floor':material('StoneFloor',(.45,.44,.40),.72),
 'Cabinet':material('IvoryCabinet',(.77,.76,.69),.46),
 'Stone':material('PaleStone',(.64,.63,.58),.24),
 'Dark':material('Graphite',(.035,.041,.043),.34),
 'Steel':material('BrushedSteel',(.28,.31,.32),.28,.8),
 'Glass':material('TemperedGlass',(.42,.63,.59),.10,0,.23),
 'GlassEdge':material('GlassEdge',(.12,.28,.24),.16,.1),
}
levels.load_level('/Game/Toy/Maps/ToyLab')
for a in list(actors.get_all_level_actors()):
 label=a.get_actor_label()
 if label.startswith('Kitchen |') or label.startswith('Floor grid'):
  actors.destroy_actor(a)
 elif isinstance(a,unreal.StaticMeshActor):
  if label=='Toy arena floor':a.static_mesh_component.set_material(0,mats['Floor'])
  elif label in ['North wall','West wall']:
   a.static_mesh_component.set_material(0,mats['Plaster'])
   loc=a.get_actor_location();loc.z=155;a.set_actor_location(loc,False,True)
   scale=a.get_actor_scale3d();scale.z=3.1;a.set_actor_scale3d(scale)
  elif label in ['South wall','East wall']:a.static_mesh_component.set_material(0,mats['Plaster'])
  elif label.startswith('Navigation obstacle'):a.static_mesh_component.set_material(0,mats['Cabinet'])
  elif label=='Round obstacle':a.static_mesh_component.set_material(0,mats['Dark'])
cube=unreal.load_asset('/Engine/BasicShapes/Cube')
cylinder=unreal.load_asset('/Engine/BasicShapes/Cylinder')
def block(label,loc,size,mat,shape=None,collision=True):
 a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*loc))
 a.set_actor_label('Kitchen | '+label)
 c=a.static_mesh_component;c.set_static_mesh(shape or cube);c.set_material(0,mats[mat])
 a.set_actor_scale3d(unreal.Vector(*(v/100 for v in size)))
 if not collision:c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
 return a
# Simple solid cabinet fronts, fine seams, and a continuous pale stone worktop.
for i,x in enumerate(range(-750,651,200)):
 block('base cabinet '+str(i),(x,780,48),(197,90,96),'Cabinet')
 block('recessed toe kick '+str(i),(x,738,6),(197,3,12),'Dark',collision=False)
block('rear stone counter',(-50,778,99),(1604,100,6),'Stone')
block('glass backsplash',(-50,832,163),(1600,2,120),'Glass',collision=False)
block('glass bottom edge',(-50,831,105),(1600,2.5,1),'GlassEdge',collision=False)
for i,x in enumerate(range(-750,451,200)):
 block('floating wall cabinet '+str(i),(x,870,255),(197,65,65),'Cabinet')
block('tall pantry',(765,812,145),(130,130,290),'Cabinet')
block('oven face',(765,744,116),(94,3,64),'Dark',collision=False)
block('oven glass',(765,741,112),(77,1,42),'Glass',collision=False)
block('oven handle',(765,737,140),(70,5,3),'Steel',collision=False)
# Reuse both original obstacle footprints as kitchen work islands.
block('island A stone top',(170,160,143),(158,288,6),'Stone',collision=False)
block('island B stone top',(-400,250,93),(258,118,6),'Stone',collision=False)
block('island hob',(-400,250,97),(80,65,2),'Dark',collision=False)
for x in [-425,-375]:
 for y in [233,267]:block('hob ring',(x,y,98.5),(22,22,1),'Steel',cylinder,False)
block('sink rim',(-450,778,103),(105,60,2),'Steel',collision=False)
block('sink basin',(-450,778,104),(92,48,2),'Dark',collision=False)
block('tap stem',(-450,809,119),(5,5,35),'Steel',cylinder,False)
block('tap spout',(-450,798,136),(5,26,5),'Steel',collision=False)
# Glass divider with a slim frame, safely outside the main wandering area.
block('tempered glass divider',(-850,570,140),(2,280,260),'Glass')
for y in [430,710]:block('glass divider frame',(-850,y,140),(3,3,260),'Steel',collision=False)
block('glass divider cap',(-850,570,270),(3,283,3),'Steel',collision=False)
# Broad shadow-free fill keeps the pared-back surfaces readable indoors.
for i,yaw in enumerate([55,-125]):
 light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,600),unreal.Rotator(-55,yaw,0))
 light.set_actor_label('Kitchen | soft fill '+str(i))
 light.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
 light.light_component.set_editor_property('intensity',2.0)
 light.light_component.set_editor_property('cast_shadows',False)
 light.light_component.set_editor_property('forward_shading_priority',0)
levels.save_current_level();unreal.EditorAssetLibrary.save_directory(folder)
report=Path(unreal.Paths.project_saved_dir())/'Verification/kitchen_assets.json'
report.write_text(json.dumps({'kitchen_assets_pass':True,'material_count':len(mats),'style':'Pared-back ivory cabinets, pale stone, graphite and tempered-glass finish','glass':'Translucent, two-sided, roughness 0.10, opacity 0.23','map':'/Game/Toy/Maps/ToyLab'},indent=2))
unreal.log('KITCHEN ASSETS PASS')
