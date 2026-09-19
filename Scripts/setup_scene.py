"""Run once with UnrealEditor-Cmd -run=pythonscript -script=<this path>."""
import unreal
import json
from pathlib import Path

ROOT='/Game/Toy'
assets=unreal.AssetToolsHelpers.get_asset_tools()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
for folder in ('Materials','Maps','Rig','Blueprints'):
    unreal.EditorAssetLibrary.make_directory(ROOT+'/'+folder)

palette={
    'Blue':(0.065,0.20,0.38), 'Dark':(0.025,0.033,0.052),
    'Purple':(0.38,0.14,0.64), 'Gold':(0.72,0.43,0.095),
    'Floor':(0.26,0.32,0.38), 'Obstacle':(0.085,0.11,0.17),
    'Line':(0.38,0.65,0.72)
}
mats={}
for name,color in palette.items():
    path=ROOT+'/Materials/M_'+name
    mat=unreal.load_asset(path)
    if not mat:
        mat=assets.create_asset('M_'+name,ROOT+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
        value=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-300,0)
        value.set_editor_property('constant',unreal.LinearColor(*color,1))
        unreal.MaterialEditingLibrary.connect_material_property(value,'',unreal.MaterialProperty.MP_BASE_COLOR)
        rough=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant,-300,200)
        rough.set_editor_property('r',0.38 if name in ('Blue','Purple','Gold') else 0.72)
        unreal.MaterialEditingLibrary.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
        unreal.MaterialEditingLibrary.recompile_material(mat)
        unreal.EditorAssetLibrary.save_loaded_asset(mat)
    if name in ('Blue','Dark'):
        mat.set_editor_property('used_with_skeletal_mesh',True)
        unreal.MaterialEditingLibrary.recompile_material(mat)
        unreal.EditorAssetLibrary.save_loaded_asset(mat)
    mats[name]=mat

map_path=ROOT+'/Maps/ToyLab'
assert levels.new_level(map_path), 'Could not create ToyLab map'
cube=unreal.load_asset('/Engine/BasicShapes/Cube')
cylinder=unreal.load_asset('/Engine/BasicShapes/Cylinder')

def block(label,loc,scale,mat='Obstacle',shape=None,collision=True):
    actor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*loc))
    actor.set_actor_label(label)
    comp=actor.static_mesh_component
    comp.set_static_mesh(shape or cube)
    comp.set_material(0,mats[mat])
    actor.set_actor_scale3d(unreal.Vector(*scale))
    if not collision:
        comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    return actor

block('Toy arena floor',(0,0,-25),(20,20,0.5),'Floor')
for label,loc,scale in [
    ('North wall',(0,960,60),(20,.3,1.2)),
    ('South wall',(0,-960,60),(20,.3,1.2)),
    ('East wall',(960,0,60),(.3,20,1.2)),
    ('West wall',(-960,0,60),(.3,20,1.2)),
    ('Navigation obstacle A',(170,160,70),(1.5,2.8,1.4)),
    ('Navigation obstacle B',(-400,250,45),(2.5,1.1,.9)),
]:block(label,loc,scale)
block('Round obstacle',(430,-250,50),(1.6,1.6,1),'Gold',cylinder)
for x in range(-900,901,150):block('Floor grid X', (x,0,.2),(.015,18,.003),'Line',collision=False)
for y in range(-900,901,150):block('Floor grid Y', (0,y,.2),(18,.015,.003),'Line',collision=False)

nav=actors.spawn_actor_from_class(unreal.NavMeshBoundsVolume,unreal.Vector(0,0,150))
nav.set_actor_label('NavMesh bounds - dynamic generation')
nav.set_actor_scale3d(unreal.Vector(11,11,4))
bounds=nav.get_actor_bounds(False)
unreal.log('TOY NavMesh bounds: '+str(bounds))
assert bounds[1].x>500, 'NavMesh volume has no brush extent'

light=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,600),unreal.Rotator(-55,-35,0))
light.light_component.set_editor_property('intensity',5.0)
light.light_component.set_editor_property('forward_shading_priority',1)
light.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
light.set_actor_label('Soft key light')
# A second broad fill avoids depending on a sky texture or an external HDRI.
fill=actors.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,600),unreal.Rotator(-35,145,0))
fill.light_component.set_editor_property('intensity',2.5)
fill.light_component.set_editor_property('forward_shading_priority',0)
fill.light_component.set_editor_property('cast_shadows',False)
fill.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)

camera=actors.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(1100,-1400,1150))
camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(camera.get_actor_location(),unreal.Vector(-100,-80,35)),False)
camera.camera_component.set_editor_property('field_of_view',55)
camera.set_actor_label('Toy Lab overview camera')

factory=unreal.BlueprintFactory()
factory.set_editor_property('parent_class',unreal.ToyCharacter)
bp=unreal.load_asset(ROOT+'/Blueprints/BP_ToyFigure')
if not bp:bp=assets.create_asset('BP_ToyFigure',ROOT+'/Blueprints',unreal.Blueprint,factory)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_loaded_asset(bp)
figure_class=unreal.EditorAssetLibrary.load_blueprint_class(ROOT+'/Blueprints/BP_ToyFigure')
figure=actors.spawn_actor_from_class(figure_class,unreal.Vector(-350,-250,90),unreal.Rotator(0,35,0))
figure.set_actor_label('TOY - RIGGED MANNEQUIN PLACEHOLDER - edit Toy settings')
pa_path=ROOT+'/Rig/PA_ToyPlaceholder'
pa=unreal.load_asset(pa_path)
if not pa:pa=assets.duplicate_asset('PA_ToyPlaceholder',ROOT+'/Rig',unreal.load_asset('/Game/Mannequin/Character/Mesh/SK_Mannequin_PhysicsAsset'))
figure.mesh.set_physics_asset(pa)
unreal.EditorAssetLibrary.save_loaded_asset(pa)
figure.mesh.set_material(0,mats['Blue'])
figure.mesh.set_material(1,mats['Dark'])
for comp in figure.get_components_by_class(unreal.StaticMeshComponent):
    comp.set_material(0,mats['Purple' if 'Hair' in comp.get_name() else 'Gold'])
    if 'Scabbard' in comp.get_name():
        pos=unreal.MathLibrary.transform_location(figure.mesh.get_world_transform(),unreal.Vector(0,-18,132))
        rot=unreal.MathLibrary.compose_rotators(unreal.Rotator(25,0,0),figure.mesh.get_world_rotation())
        comp.set_world_location_and_rotation(pos,rot,False,True)
figure.set_editor_property('drive_damping',140.0)
figure.set_editor_property('body_damping',10.0)

# Explicit supported-agent dimensions are also configured in DefaultEngine.ini.
for nav_data in actors.get_all_level_actors():
    if isinstance(nav_data,unreal.RecastNavMesh):
        nav_data.set_editor_property('runtime_generation',unreal.RuntimeGenerationType.DYNAMIC)
        nav_data.set_editor_property('agent_radius',34.0)
        nav_data.set_editor_property('agent_height',176.0)
        nav_data.set_editor_property('force_rebuild_on_load',True)

levels.save_current_level()
unreal.EditorAssetLibrary.save_directory(ROOT)
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation())
mesh=figure.mesh.get_skeletal_mesh_asset()
bones=[str(figure.mesh.get_bone_name(i)) for i in range(figure.mesh.get_num_bones())]
audit={
    'engine':unreal.SystemLibrary.get_engine_version(),
    'mesh':mesh.get_path_name(),
    'skeleton':str(mesh.get_editor_property('skeleton').get_path_name()),
    'physics_asset':pa.get_path_name(),
    'bones':bones,
    'required_secondary_bones_present':all(b in bones for b in ('lowerarm_l','lowerarm_r','hand_l','hand_r')),
    'idle':unreal.load_asset('/Game/Mannequin/Animations/ThirdPersonIdle').get_path_name(),
    'walk':unreal.load_asset('/Game/Mannequin/Animations/ThirdPersonWalk').get_path_name(),
    'reference_matching_model_available':False,
    'reference_specific_rig_available':False,
    'reference_fitted_physics_asset_available':False,
    'tailored_locomotion_and_gestures_available':False,
}
report=Path(unreal.Paths.project_saved_dir())/'Verification'/'asset_audit.json'
report.parent.mkdir(parents=True,exist_ok=True)
report.write_text(json.dumps(audit,indent=2))
unreal.log('TOY SETUP COMPLETE: '+str(report))
