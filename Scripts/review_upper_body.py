"""Upper-body turntable and structural checks in the authored Blender scene."""
import json,math,shutil,subprocess,sys
from pathlib import Path
import bpy
from mathutils import Vector


def render_review(ns):
    rig,mesh,scene,camera,aim,pose,OUT=[ns[k] for k in ('rig','mesh','scene','camera','aim','pose','OUT')]
    rig.animation_data.action=None;pose('Idle',0);bpy.context.view_layer.update()
    finger_bones=[b.name for b in rig.data.bones if any(b.name.startswith(n+'_') for n in ('index','middle','ring','pinky','thumb'))]
    assert len(finger_bones)==28
    assert all(abs(sum(g.weight for g in v.groups)-1)<.002 for v in mesh.data.vertices),'Non-normalized skin weights'
    groupnames={g.index:g.name for g in mesh.vertex_groups}
    blended=sum(1 for v in mesh.data.vertices if len(v.groups)>1 and any(groupnames[g.group].startswith(('upperarm','lowerarm')) for g in v.groups))
    assert blended>500,blended
    assert {'Focused','Shout'}.issubset(mesh.data.shape_keys.key_blocks.keys())
    # Guard endpoints and strike endpoints should match on the right arm.
    pose('Idle',0);guard={b.name:b.rotation_quaternion.copy() for b in rig.pose.bones}
    pose('Slash',0)
    for name in ('upperarm_r','lowerarm_r','hand_r','upperarm_l','lowerarm_l'):
        assert guard[name].rotation_difference(rig.pose.bones[name].rotation_quaternion).angle<.001,name
    report={'bones':len(rig.data.bones),'finger_bones':len(finger_bones),'blended_arm_vertices':blended,'weights_normalized':True,'guard_to_strike_boundary':True}
    (OUT/'upper_body_report.json').write_text(json.dumps(report,indent=2))
    scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True
    scene.render.resolution_x=720;scene.render.resolution_y=720;scene.render.resolution_percentage=100
    jacket_review="--jacket-review" in sys.argv
    camera.data.ortho_scale=1.35 if jacket_review else 1.70
    folder=OUT/('JacketTurntable' if jacket_review else 'UpperBodyTurntable');folder.mkdir(exist_ok=True)
    pose('Idle',0);bpy.context.view_layer.update()
    frames=24 if jacket_review else 36
    for i in range(frames):
        a=math.tau*i/frames
        camera.location=(2.8*math.sin(a),-2.8*math.cos(a),1.75);aim(camera,(0,-.15,1.31))
        scene.render.filepath=str(folder/f'frame_{i:03d}.png');bpy.ops.render.render(write_still=True)
    for name,t in [('guard',0),('windup',.12/.55),('contact',.23/.55),('followthrough',.30/.55)]:
        pose('Idle' if name=='guard' else 'Slash',t);bpy.context.view_layer.update()
        camera.location=(1.0,-2.8,1.70);camera.data.ortho_scale=1.80;aim(camera,(0,-.09,1.24))
        scene.render.filepath=str(OUT/f'UpperBody_{name}.png');bpy.ops.render.render(write_still=True)
    pose('Idle',0);bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ToyBlockout.blend'))
    ffmpeg=shutil.which('ffmpeg')
    if ffmpeg:
        subprocess.run([ffmpeg,'-y','-loglevel','error','-framerate',str(frames//3),'-i',str(folder/'frame_%03d.png'),'-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/('jacket_turntable.mp4' if jacket_review else 'upper_body_turntable.mp4'))],check=True,timeout=60)
    print('UPPER BODY REVIEW COMPLETE',report)
