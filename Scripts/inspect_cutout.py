import unreal
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/Toy/Maps/ToyLab')
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if isinstance(actor,unreal.ToyCharacter):
  c=actor.get_editor_property('image_cutout')
  unreal.log('CUTOUT DEBUG '+str(c.get_editor_property('static_mesh'))+' parent='+str(c.get_attach_parent())+' transform='+str(c.get_world_transform()))
  for prop in ['visible','hidden_in_game','render_in_main_pass','owner_no_see','only_owner_see']:
   unreal.log('CUTOUT DEBUG '+prop+'='+str(c.get_editor_property(prop)))
