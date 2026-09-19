import unreal
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for name in ('Blue','Dark'):
    material=unreal.load_asset('/Game/Toy/Materials/M_'+name)
    material.set_editor_property('used_with_skeletal_mesh',True)
    unreal.MaterialEditingLibrary.recompile_material(material)
    unreal.EditorAssetLibrary.save_loaded_asset(material)
levels.load_level('/Game/Toy/Maps/ToyLab')
for a in actors.get_all_level_actors():
    if isinstance(a,unreal.SkyLight):actors.destroy_actor(a)
    elif isinstance(a,unreal.DirectionalLight):
        key=a.get_actor_label()=='Soft key light'
        a.light_component.set_editor_property('intensity',5.0 if key else 2.5)
        a.light_component.set_editor_property('forward_shading_priority',1 if key else 0)
    elif isinstance(a,unreal.ToyCharacter):
        a.set_editor_property('drive_damping',140.0)
        a.set_editor_property('body_damping',10.0)
        for comp in a.get_components_by_class(unreal.StaticMeshComponent):
            if 'Scabbard' in comp.get_name():
                pos=unreal.MathLibrary.transform_location(a.mesh.get_world_transform(),unreal.Vector(0,-18,132))
                rot=unreal.MathLibrary.compose_rotators(unreal.Rotator(25,0,0),a.mesh.get_world_rotation())
                comp.set_world_location_and_rotation(pos,rot,False,True)
                unreal.log('TOY scabbard relative transform: '+str(comp.get_editor_property('relative_location'))+' '+str(comp.get_editor_property('relative_rotation')))

levels.save_current_level()
unreal.log('TOY scene lighting and damping updated')
