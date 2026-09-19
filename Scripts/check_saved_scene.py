import unreal,json
from pathlib import Path
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
path='/Game/Toy/Maps/ToyLab'
def inspect():
    result=[]
    for a in actors.get_all_level_actors():
        if isinstance(a,unreal.RecastNavMesh):
            result.append({'name':a.get_name(),'radius':a.get_editor_property('agent_radius'),'height':a.get_editor_property('agent_height'),'dynamic':a.get_editor_property('runtime_generation')==unreal.RuntimeGenerationType.DYNAMIC,'rebuild_on_load':a.get_editor_property('force_rebuild_on_load')})
    assert result, 'No NavMesh actor after load'
    assert all(r['radius']==34 and r['height']==176 and r['dynamic'] for r in result), str(result)
    return result
assert levels.load_level(path)
before=inspect()
for a in actors.get_all_level_actors():
    if isinstance(a,unreal.RecastNavMesh):a.set_editor_property('force_rebuild_on_load',True)
levels.save_current_level()
assert levels.load_level('/Engine/Maps/Entry')
assert levels.load_level(path)
after=inspect()
assert all(r['rebuild_on_load'] for r in after)
materials={n:unreal.load_asset('/Game/Toy/Materials/M_'+n).get_editor_property('used_with_skeletal_mesh') for n in ('Blue','Dark')}
assert all(materials.values())
report={'save_reload_pass':True,'before':before,'after':after,'skeletal_material_usage':materials}
out=Path(unreal.Paths.project_saved_dir())/'Verification/scene_persistence.json'
out.write_text(json.dumps(report,indent=2))
unreal.log('TOY SAVE/RELOAD PASS '+json.dumps(report))
