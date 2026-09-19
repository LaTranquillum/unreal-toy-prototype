"""Closer portrait composition, a restrained manga inset, and soft kitchen light."""
import unreal
E=unreal.MaterialEditingLibrary
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not unreal.EditorAssetLibrary.does_asset_exist('/Game/Toy/Maps/ToyLab'):
    raise RuntimeError('ToyLab is missing. Supply the documented mannequin assets and run setup_scene.py first.')
if not levels.load_level('/Game/Toy/Maps/ToyLab'):
    raise RuntimeError('Could not load ToyLab; no visual changes were applied.')
folder='/Game/Toy/Kitchen';name='M_VideoWarmFloor'
unreal.EditorAssetLibrary.make_directory(folder)
m=unreal.load_asset(folder+'/'+name)
if not m:m=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,folder,unreal.Material,unreal.MaterialFactoryNew())
else:E.delete_all_material_expressions(m)
c=E.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-200,0)
c.set_editor_property('constant',unreal.LinearColor(.32,.30,.27,1))
E.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
r=E.create_material_expression(m,unreal.MaterialExpressionConstant,-200,100);r.set_editor_property('r',.85)
E.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS)
E.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m)
all_actors=list(actors.get_all_level_actors())
for a in all_actors:
 label=a.get_actor_label()
 if label.startswith('Manga rug |') or label.startswith('Video softbox |'):actors.destroy_actor(a)
 elif label=='Toy arena floor':a.static_mesh_component.set_material(0,m)
 elif isinstance(a,unreal.DirectionalLight):
  key=label=='Soft key light'
  a.light_component.set_editor_property('intensity',.9 if key else .2)
  a.light_component.set_editor_property('light_source_angle',8.0)
  a.light_component.set_editor_property('cast_shadows',key)
 elif isinstance(a,unreal.CameraActor):
  a.camera_component.set_editor_property('aspect_ratio',9/16)
  a.camera_component.set_editor_property('constrain_aspect_ratio',True)
  a.camera_component.set_editor_property('field_of_view',32)
  a.set_actor_label('Portrait follow camera')
plane=unreal.load_asset('/Engine/BasicShapes/Plane')
for i,(panel,w,h) in enumerate([(1,195,205),(4,150,205),(5,170,205)]):
 a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(-550+i*210,-250,.9))
 a.set_actor_label('Manga rug | curated inset '+str(i+1))
 c=a.static_mesh_component;c.set_static_mesh(plane)
 art_path='/Game/Toy/MangaRug/M_Panel_'+str(panel)
 art=unreal.load_asset(art_path) if unreal.EditorAssetLibrary.does_asset_exist(art_path) else None
 c.set_material(0,art or m)
 if not art:
  a.set_actor_label('Manga rug | plain placeholder '+str(i+1))
  unreal.log_warning('Optional manga material missing: '+art_path+'; using a plain inset.')
 c.set_collision_profile_name('NoCollision');c.set_editor_property('can_ever_affect_navigation',False);c.set_cast_shadow(False)
 a.set_actor_enable_collision(False);a.set_actor_scale3d(unreal.Vector(w/100,h/100,1))
for i,(pos,power,color) in enumerate([((100,-650,650),400,(1,.93,.84)),((-650,100,550),300,(.85,.90,1))]):
 rot=unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*pos),unreal.Vector(-250,100,70))
 a=actors.spawn_actor_from_class(unreal.RectLight,unreal.Vector(*pos),rot)
 a.set_actor_label('Video softbox | '+str(i))
 c=a.light_component;c.set_mobility(unreal.ComponentMobility.MOVABLE)
 c.set_editor_property('intensity_units',unreal.LightUnits.LUMENS);c.set_editor_property('intensity',power);c.set_editor_property('attenuation_radius',2200)
 c.set_editor_property('source_width',700);c.set_editor_property('source_height',500)
 c.set_editor_property('cast_shadows',False)
 c.set_light_color(unreal.LinearColor(*color,1))
levels.save_current_level()
unreal.log('VIDEO POLISH SAVED: portrait camera, three inset panels, soft lighting')
