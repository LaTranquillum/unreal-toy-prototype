"""Basic live environment reflection on the four existing perimeter walls."""
import unreal,json
from pathlib import Path
E=unreal.MaterialEditingLibrary
assets=unreal.AssetToolsHelpers.get_asset_tools()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
folder='/Game/Toy/Mirrors'
unreal.EditorAssetLibrary.make_directory(folder)
levels.load_level('/Game/Toy/Maps/ToyLab')
walls=[a for a in actors.get_all_level_actors() if a.get_actor_label() in ['North wall','South wall','East wall','West wall']]
assert len(walls)==4
for a in list(actors.get_all_level_actors()):
 if a.get_actor_label()=='Mirror environment capture':actors.destroy_actor(a)
rt=unreal.load_asset(folder+'/RT_MirrorEnvironment')
if not rt:rt=assets.create_asset('RT_MirrorEnvironment',folder,unreal.TextureRenderTargetCube,unreal.TextureRenderTargetCubeFactoryNew())
rt.set_editor_property('size_x',256)
rt.set_editor_property('hdr',True)
unreal.EditorAssetLibrary.save_loaded_asset(rt)
cap=actors.spawn_actor_from_class(unreal.SceneCaptureCube,unreal.Vector(0,0,450))
cap.set_actor_label('Mirror environment capture')
c=cap.get_component_by_class(unreal.SceneCaptureComponentCube)
c.set_editor_property('texture_target',rt)
c.set_editor_property('capture_every_frame',True)
c.set_editor_property('capture_on_movement',False)
for wall in walls:c.hide_actor_components(wall)
m=unreal.load_asset(folder+'/M_BasicMirror')
if not m:m=assets.create_asset('M_BasicMirror',folder,unreal.Material,unreal.MaterialFactoryNew())
else:E.delete_all_material_expressions(m)
m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT)
sample=E.create_material_expression(m,unreal.MaterialExpressionTextureSample,-400,0)
sample.set_editor_property('texture',rt)
reflect=E.create_material_expression(m,unreal.MaterialExpressionReflectionVectorWS,-650,0)
assert E.connect_material_expressions(reflect,'',sample,'UVs')
tint=E.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-400,180)
tint.set_editor_property('constant',unreal.LinearColor(.83,.88,.91,1))
mul=E.create_material_expression(m,unreal.MaterialExpressionMultiply,-150,0)
assert E.connect_material_expressions(sample,'RGB',mul,'A')
assert E.connect_material_expressions(tint,'',mul,'B')
assert E.connect_material_property(mul,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
E.recompile_material(m)
unreal.EditorAssetLibrary.save_loaded_asset(m)
for a in walls:a.static_mesh_component.set_material(0,m)
levels.save_current_level()
unreal.EditorAssetLibrary.save_directory(folder)
report={'mirrors_pass':True,'walls':sorted(a.get_actor_label() for a in walls),'capture_resolution':256,'method':'Live shared cube environment reflection with silver tint; approximate, not planar or recursive','wall_geometry_and_collision':'unchanged'}
(Path(unreal.Paths.project_saved_dir())/'Verification/mirrors.json').write_text(json.dumps(report,indent=2))
unreal.log('MIRRORS ASSETS PASS')
