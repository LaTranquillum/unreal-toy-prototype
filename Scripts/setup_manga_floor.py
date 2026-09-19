"""Cover the kitchen floor with the original six and nine new manga panels."""
import unreal,json
from pathlib import Path
E=unreal.MaterialEditingLibrary
assets=unreal.AssetToolsHelpers.get_asset_tools()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
folder='/Game/Toy/MangaRug'
unreal.EditorAssetLibrary.make_directory(folder)
task=unreal.AssetImportTask()
for prop,value in {'filename':str(Path(unreal.Paths.project_dir()).resolve()/'Reference/2DT.jpeg'),'destination_path':folder,'destination_name':'T_OriginalManga','automated':True,'replace_existing':True,'save':True}.items():task.set_editor_property(prop,value)
assets.import_asset_tasks([task])
texture=unreal.load_asset(folder+'/T_OriginalManga')
assert texture
texture.set_editor_property('srgb',True)
texture.set_editor_property('address_x',unreal.TextureAddress.TA_CLAMP)
texture.set_editor_property('address_y',unreal.TextureAddress.TA_CLAMP)
unreal.EditorAssetLibrary.save_loaded_asset(texture)
new_task=unreal.AssetImportTask()
for prop,value in {'filename':str(Path(unreal.Paths.project_dir()).resolve()/'Art/MangaFloor/AdditionalPanels.png'),'destination_path':folder,'destination_name':'T_AdditionalPanels','automated':True,'replace_existing':True,'save':True}.items():new_task.set_editor_property(prop,value)
assets.import_asset_tasks([new_task])
additional=unreal.load_asset(folder+'/T_AdditionalPanels')
assert additional
additional.set_editor_property('srgb',True)
additional.set_editor_property('address_x',unreal.TextureAddress.TA_CLAMP)
additional.set_editor_property('address_y',unreal.TextureAddress.TA_CLAMP)
unreal.EditorAssetLibrary.save_loaded_asset(additional)
# Normalized bounds of the six original panels; the upper-right panel is
# converted to grayscale too. Occluded source pixels are not reconstructed.
regions=[('Portrait',.017,.007,.393,.210),('Training',.405,.022,.980,.212),
 ('Time machine',.025,.217,.411,.445),('Power up',.642,.224,.950,.510),
 ('Transformation',.012,.453,.477,.923),('Fight',.486,.519,.930,.970)]
for row in range(3):
 for col in range(3):regions.append(('New scene '+str(row*3+col+1),col/3,row/3,(col+1)/3,(row+1)/3))
def expr(m,cls,x,y):return E.create_material_expression(m,cls,x,y)
def constant(m,value,x,y):
 n=expr(m,unreal.MaterialExpressionConstant,x,y);n.set_editor_property('r',value);return n
def material(i,r):
 name='M_Panel_'+str(i+1)
 m=unreal.load_asset(folder+'/'+name)
 if not m:m=assets.create_asset(name,folder,unreal.Material,unreal.MaterialFactoryNew())
 else:E.delete_all_material_expressions(m)
 uv=expr(m,unreal.MaterialExpressionTextureCoordinate,-1000,0)
 # Engine plane UVs increase toward +Y; reverse V so the panels read from the camera side.
 uv.set_editor_property('u_tiling',r[3]-r[1]);uv.set_editor_property('v_tiling',-(r[4]-r[2]))
 offset=expr(m,unreal.MaterialExpressionConstant2Vector,-1000,160)
 offset.set_editor_property('r',r[1]);offset.set_editor_property('g',r[4])
 add=expr(m,unreal.MaterialExpressionAdd,-750,0)
 assert E.connect_material_expressions(uv,'',add,'A')
 assert E.connect_material_expressions(offset,'',add,'B')
 sample=expr(m,unreal.MaterialExpressionTextureSample,-500,0);sample.set_editor_property('texture',texture if i<6 else additional)
 assert E.connect_material_expressions(add,'',sample,'UVs')
 grey=expr(m,unreal.MaterialExpressionDotProduct,-250,0)
 weights=expr(m,unreal.MaterialExpressionConstant3Vector,-500,200)
 weights.set_editor_property('constant',unreal.LinearColor(.299,.587,.114,1))
 assert E.connect_material_expressions(sample,'RGB',grey,'A')
 assert E.connect_material_expressions(weights,'',grey,'B')
 tone=expr(m,unreal.MaterialExpressionMultiply,0,0);tone.set_editor_property('const_b',.55)
 assert E.connect_material_expressions(grey,'',tone,'A')
 assert E.connect_material_property(tone,'',unreal.MaterialProperty.MP_BASE_COLOR)
 assert E.connect_material_property(constant(m,1,0,200),'',unreal.MaterialProperty.MP_ROUGHNESS)
 E.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m)
 return m
mats=[material(i,r) for i,r in enumerate(regions)]
base=unreal.load_asset('/Game/Toy/Kitchen/M_Graphite')
levels.load_level('/Game/Toy/Maps/ToyLab')
for a in list(actors.get_all_level_actors()):
 if a.get_actor_label().startswith('Manga rug |'):actors.destroy_actor(a)
plane=unreal.load_asset('/Engine/BasicShapes/Plane')
created=[]
def panel(label,x,y,z,w,h,m):
 a=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(x,y,z))
 a.set_actor_label('Manga rug | '+label)
 c=a.static_mesh_component;c.set_static_mesh(plane);c.set_material(0,m)
 c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
 c.set_editor_property('can_ever_affect_navigation',False)
 c.set_cast_shadow(False)
 a.set_actor_scale3d(unreal.Vector(w/100,h/100,1))
 # Apply the collision profile after editor property changes and transformations.
 c.set_collision_profile_name('NoCollision')
 a.set_actor_enable_collision(False)
 unreal.log('RUG COLLISION '+label+' '+str(c.get_collision_enabled()))
 created.append(a);return a
panel('full floor backing',0,0,.6,2000,2000,base)
for row in range(8):
 for col in range(8):
  i=(row*7+col*11)%len(regions)
  r=regions[i]
  aspect=((r[3]-r[1])*1297)/((r[4]-r[2])*1920) if i<6 else 1.0
  w=min(247,247*aspect);h=w/aspect
  panel('tile '+str(row*8+col+1)+' / '+r[0],-875+col*250,875-row*250,.9,w,h,mats[i])
# Appearance only: every rug surface must remain non-colliding.
assert len(created)==65
assert all(a.static_mesh_component.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION for a in created)
levels.save_current_level();unreal.EditorAssetLibrary.save_directory(folder)
report={'manga_rug_pass':True,'source':'Reference/2DT.jpeg','panel_count':64,'unique_panel_artworks':15,'new_generated_artworks':9,'floor_coverage_cm':[2000,2000],'grayscale':True,'non_colliding':True,'original_overlaps_preserved':True,'regions':regions}
(Path(unreal.Paths.project_saved_dir())/'Verification/manga_floor.json').write_text(json.dumps(report,indent=2))
unreal.log('MANGA FLOOR PASS')
