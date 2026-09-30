"""Bounded full-body visual and deformation review."""
import bpy,json,math,subprocess,shutil
from mathutils import Vector

def render_review(ns):
 rig,mesh,scene,camera,out=[ns[k] for k in ('rig','mesh','scene','camera','OUT')]
 rig.animation_data.action=None
 assert len(rig.data.bones)==49
 assert all(abs(sum(g.weight for g in v.groups)-1)<.001 for v in mesh.data.vertices)
 groups={g.index:g.name for g in mesh.vertex_groups}
 blended=sum(any(groups[g.group].startswith('thigh_') for g in v.groups) and any(groups[g.group].startswith('calf_') for g in v.groups) for v in mesh.data.vertices)
 assert blended>100,blended
 errors=[]
 for kind in ('Idle','Slash'):
  for t in (0,.22,.42,.55,.8,1):
   ns['pose'](kind,t);bpy.context.view_layer.update()
   for side,sign in [('l',1),('r',-1)]:
    errors.append((rig.pose.bones['foot_'+side].head-Vector((sign*.13,sign*.035,.13))).length)
 assert max(errors)<.001,max(errors)
 scene.render.resolution_x=720;scene.render.resolution_y=900;scene.cycles.samples=12
 camera.data.ortho_scale=2.15
 def aim():ns['aim'](camera,(0,0,.9))
 frames=out/'FighterTurntable';frames.mkdir(exist_ok=True)
 ns['pose']('Idle',0)
 for i in range(24):
  a=i*math.tau/24;camera.location=(3*math.sin(a),-3*math.cos(a),1.6);aim()
  scene.render.filepath=str(frames/f'fighter_{i:03d}.png');bpy.ops.render.render(write_still=True)
 ffmpeg=shutil.which('ffmpeg');assert ffmpeg,'ffmpeg must be on PATH'
 subprocess.run([ffmpeg,'-y','-loglevel','error','-framerate','12','-i',str(frames/'fighter_%03d.png'),'-c:v','libx264','-pix_fmt','yuv420p',str(out/'fighter_finish_turntable.mp4')],check=True)
 camera.location=(1.8,-3,1.6);aim()
 for label,kind,t in [('guard','Idle',0),('contact','Slash',.23/.55),('follow','Slash',.30/.55)]:
  ns['pose'](kind,t);scene.render.filepath=str(out/f'Fighter_{label}.png');bpy.ops.render.render(write_still=True)
 ns['pose']('Idle',0)
 bpy.ops.wm.save_as_mainfile(filepath=str(out/'ToyBlockout.blend'))
 (out/'fighter_finish_review.json').write_text(json.dumps({'bones':49,'blended_knee_vertices':blended,'max_ankle_error_m':max(errors),'normalized_weights':True,'turntable_frames':24},indent=2))
