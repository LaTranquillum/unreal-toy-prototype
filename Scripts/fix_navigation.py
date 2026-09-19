import unreal
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.load_level('/Game/Toy/Maps/ToyLab')
found=False
for a in actors.get_all_level_actors():
    if isinstance(a,unreal.NavMeshBoundsVolume):unreal.log('TOY saved nav bounds '+str(a.get_actor_bounds(False)))
    if isinstance(a,unreal.RecastNavMesh):
        found=True
        for prop in ('runtime_generation','agent_radius','agent_height','can_be_main_nav_data','force_rebuild_on_load'):
            unreal.log('TOY Nav '+prop+' BEFORE '+str(a.get_editor_property(prop)))
        a.set_editor_property('runtime_generation',unreal.RuntimeGenerationType.DYNAMIC)
        a.set_editor_property('agent_radius',34.0)
        a.set_editor_property('agent_height',176.0)
        a.set_editor_property('can_be_main_nav_data',True)
        a.set_editor_property('force_rebuild_on_load',True)
assert found, 'No RecastNavMesh actor in saved level'
levels.save_current_level()
unreal.log('TOY navigation settings saved')
