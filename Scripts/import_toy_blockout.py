"""Import Blender blockout + clips into UE5.8 without editing ToyLab."""
import unreal,json
from pathlib import Path
source=Path(unreal.Paths.project_dir())/'Art/ToyBlockout'
folder='/Game/Toy/Blockout'
unreal.EditorAssetLibrary.make_directory(folder)
tools=unreal.AssetToolsHelpers.get_asset_tools()
def imp(name,animation=False,skeleton=None):
 ui=unreal.FbxImportUI();ui.set_editor_property('automated_import_should_detect_type',False)
 ui.set_editor_property('import_as_skeletal',True);ui.set_editor_property('import_mesh',not animation)
 ui.set_editor_property('mesh_type_to_import',unreal.FBXImportType.FBXIT_ANIMATION if animation else unreal.FBXImportType.FBXIT_SKELETAL_MESH)
 ui.set_editor_property('import_animations',animation);ui.set_editor_property('import_materials',False);ui.set_editor_property('import_textures',False)
 ui.set_editor_property('create_physics_asset',not animation)
 if skeleton:ui.set_editor_property('skeleton',skeleton)
 data=ui.anim_sequence_import_data if animation else ui.skeletal_mesh_import_data
 data.set_editor_property('convert_scene',True);data.set_editor_property('convert_scene_unit',True)
 data.set_editor_property('force_front_x_axis',False)
 if animation:
  data.set_editor_property('animation_length',unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
 task=unreal.AssetImportTask();task.filename=str(source/(name+'.fbx'));task.destination_path=folder;task.destination_name=name
 task.automated=True;task.replace_existing=True;task.save=True;task.options=ui
 tools.import_asset_tasks([task]);unreal.log('TOY IMPORT '+str(task.imported_object_paths))
 asset=unreal.load_asset(folder+'/'+name)
 if not asset:
  for path in task.imported_object_paths:
   candidate=unreal.load_asset(path)
   if isinstance(candidate,unreal.AnimSequence if animation else unreal.SkeletalMesh):
    asset=candidate;break
 assert asset,'Import failed: '+name
 if asset.get_path_name().split('.')[-1]!=name:
  assert unreal.EditorAssetLibrary.rename_asset(asset.get_path_name(),folder+'/'+name)
 return asset
mesh=imp('SK_ToyBlockout');skeleton=mesh.get_editor_property('skeleton')
clips={n:imp('A_Toy'+n,True,skeleton) for n in ['Idle','Run','Dodge','Slash']}
colors={'Jacket':(.07,.27,.51),'Pants':(.035,.045,.07),'Skin':(.72,.43,.25),'Hair':(.33,.12,.55),'Boots':(.67,.39,.09),'Steel':(.55,.65,.73),'Eyes':(.015,.025,.04),'White':(.9,.93,.95)}
colors.update(json.loads((source/'asset_report.json').read_text()).get('material_colors',{}))
colors={k:tuple(v[:3]) for k,v in colors.items()}
E=unreal.MaterialEditingLibrary
slots=list(mesh.get_editor_property('materials'))
for i,slot in enumerate(slots):
 name=str(slot.get_editor_property('material_slot_name'));color=colors.get(name,(.4,.4,.4))
 m=unreal.load_asset(folder+'/M_'+name)
 if not m:m=tools.create_asset('M_'+name,folder,unreal.Material,unreal.MaterialFactoryNew())
 else:E.delete_all_material_expressions(m)
 c=E.create_material_expression(m,unreal.MaterialExpressionConstant3Vector);c.set_editor_property('constant',unreal.LinearColor(*color,1));E.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
 for value,prop in [(.52 if name in ('Jacket','Pants','Trim','PantsFold') else .36,unreal.MaterialProperty.MP_ROUGHNESS),(.7 if name=='Steel' else 0,unreal.MaterialProperty.MP_METALLIC)]:
  a=E.create_material_expression(m,unreal.MaterialExpressionConstant);a.set_editor_property('r',value);E.connect_material_property(a,'',prop)
 E.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH)
 E.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m)
 slot.set_editor_property('material_interface',m)
 slots[i]=slot
mesh.set_editor_property('materials',slots);unreal.EditorAssetLibrary.save_loaded_asset(mesh)
unreal.EditorAssetLibrary.save_directory(folder)
report={'mesh':mesh.get_path_name(),'skeleton':skeleton.get_path_name(),'physics_asset':str(mesh.get_editor_property('physics_asset')),'clips':{n:{'path':a.get_path_name(),'duration':a.get_editor_property('sequence_length')} for n,a in clips.items()},'material_slots':[str(s.material_slot_name) for s in slots]}
(Path(unreal.Paths.project_saved_dir())/'Verification/toy-import.json').write_text(json.dumps(report,indent=2));unreal.log('TOY IMPORT COMPLETE '+str(report))
