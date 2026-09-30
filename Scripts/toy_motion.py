"""Authored in-place toy motion, with continuous anticipation and recovery."""
import math
from mathutils import Vector,Quaternion,Matrix
import bpy

def pose(rig,kind,t):
 def rot(name,angles):
  pb=rig.pose.bones[name];q=Quaternion((1,0,0,0))
  basis=rig.data.bones[name].matrix_local.to_quaternion().inverted()
  for axis,deg in zip([(1,0,0),(0,1,0),(0,0,1)],angles):q=Quaternion(basis@Vector(axis),math.radians(deg))@q
  pb.rotation_quaternion=q
 def move(name,xyz):rig.pose.bones[name].location=rig.data.bones[name].matrix_local.to_quaternion().inverted()@Vector(xyz)
 def curve(keys):
  for (ta,a),(tb,b) in zip(keys,keys[1:]):
   if t<=tb:
    u=max(0,min(1,(t-ta)/(tb-ta)));u=u*u*(3-2*u);return a+(b-a)*u
  return keys[-1][1]
 for pb in rig.pose.bones:pb.location=(0,0,0);pb.rotation_mode='QUATERNION';pb.rotation_quaternion=(1,0,0,0);pb.scale=(1,1,1)
 if kind=='Idle':
  breath=math.sin(t*math.tau)
  rot('chest',(1.1*breath,0,0));rot('head',(-.45*breath,0,1.3*breath))
  rot('upperarm_r',(-20-breath,-12,-12));rot('lowerarm_r',(-46-1.5*breath,0,0));rot('hand_r',(-8,0,5))
  rot('upperarm_l',(-12,8,18));rot('lowerarm_l',(-62-3*breath,0,-12))
 elif kind=='Run':
  phase=t*math.tau;s=math.sin(phase)
  move('pelvis',(0,0,.012*(1-math.cos(2*phase))))
  rot('pelvis',(0,2*s,4*s));rot('spine',(7,-1.5*s,-3*s));rot('chest',(0,0,-4*s));rot('head',(-3,0,2*s))
  for side,sign in [('l',1),('r',-1)]:
   stride=sign*s;recovery=max(0,-stride)
   rot('thigh_'+side,(30*stride,0,0));rot('calf_'+side,(-7-52*recovery,0,0))
   rot('foot_'+side,(-8*stride+9*recovery,0,0))
   rot('upperarm_'+side,((-23 if side=='l' else -13)*stride,0,0))
   rot('lowerarm_'+side,(24+7*stride if side=='l' else 16+4*stride,0,0))
 elif kind=='Dodge':
  crouch=curve([(0,0),(.18,1),(.55,.95),(1,0)])
  lean=curve([(0,0),(.25,1),(.63,.65),(1,0)])
  move('pelvis',(0,0,-.11*crouch));rot('spine',(27*lean,0,0));rot('head',(-15*lean,0,0))
  rot('thigh_l',(42*crouch,0,0));rot('calf_l',(-59*crouch,0,0));rot('foot_l',(15*crouch,0,0))
  rot('thigh_r',(18*crouch,0,0));rot('calf_r',(-42*crouch,0,0));rot('foot_r',(18*crouch,0,0))
  rot('upperarm_l',(-22*lean,0,-12*lean));rot('lowerarm_l',(35*crouch,0,0))
  rot('upperarm_r',(-12*lean,0,5*lean));rot('lowerarm_r',(18*crouch,0,0))
 elif kind=='Slash':
  # Normalized times map to .12s windup and .30s end of active window.
  wind=.12/.55;contact=.23/.55;follow=.30/.55
  lift=curve([(0,20),(wind,53),(contact,25),(follow,-8),(.78,8),(1,20)])
  sweep=curve([(0,-12),(wind,-40),(contact,18),(follow,42),(.78,8),(1,-12)])
  torso=curve([(0,0),(wind,-22),(contact,15),(follow,28),(.78,10),(1,0)])
  settle=curve([(0,0),(wind,.35),(contact,1),(follow,.75),(1,0)])
  rot('pelvis',(0,0,torso*.22));rot('spine',(5*settle,0,torso*.25));rot('chest',(0,0,torso*.53));rot('head',(-3*settle,0,-torso*.35))
  rot('upperarm_r',(-lift,-12-8*settle,sweep));rot('lowerarm_r',(-curve([(0,46),(wind,68),(contact,22),(follow,15),(.78,35),(1,46)]),0,0))
  rot('hand_r',(-8-7*settle,0,5-sweep*.12-1.44));rot('upperarm_l',(-12+18*settle,8,18-15*settle));rot('lowerarm_l',(-62+22*settle,0,-12))
  move('pelvis',(0,0,-.018*settle));rot('thigh_l',(7*settle,0,0));rot('calf_l',(-12*settle,0,0));rot('thigh_r',(6*settle,0,0));rot('calf_r',(-10*settle,0,0))

 # Small finger articulation keeps the right grip closed; the free hand breathes.
 for side in ('l','r'):
  for name in ('index','middle','ring','pinky'):
   bn=f'{name}_2_{side}'
   if bn in rig.pose.bones:
    degrees=(1.2 if side=='r' else 3.0)*math.sin(t*math.tau)**2
    rot(bn,(0,degrees,0))

 # Two-bone solve keeps the guard/strike ankles planted while the pelvis turns.
 if kind in ('Idle','Slash'):
  rig.pose.bones['pelvis'].location += rig.data.bones['pelvis'].matrix_local.to_quaternion().inverted()@Vector((0,0,-.026))
  bpy.context.view_layer.update()
  for side,sign in [('l',1),('r',-1)]:
   thigh=rig.pose.bones['thigh_'+side];calf=rig.pose.bones['calf_'+side];foot=rig.pose.bones['foot_'+side]
   hip=thigh.head.copy();ankle=Vector((sign*.13,sign*.035,.13))
   axis=ankle-hip;distance=axis.length;axis.normalize()
   a=thigh.bone.length;b=calf.bone.length
   along=(a*a-b*b+distance*distance)/(2*distance)
   pole=Vector((0,-1,0));pole=(pole-axis*pole.dot(axis)).normalized()
   knee=hip+axis*along+pole*math.sqrt(max(0,a*a-along*along))
   for pb,start,end in [(thigh,hip,knee),(calf,knee,ankle)]:
    rest=pb.bone.tail_local-pb.bone.head_local
    q=rest.rotation_difference(end-start)@pb.bone.matrix_local.to_quaternion()
    pb.matrix=Matrix.LocRotScale(start,q,Vector((1,1,1)))
    bpy.context.view_layer.update()
   foot.matrix=Matrix.LocRotScale(ankle,foot.bone.matrix_local.to_quaternion(),Vector((1,1,1)))
   bpy.context.view_layer.update()
 for side,sign in [('l',1),('r',-1)]:
  for prefix,amount in [('hair_tip_',2.0),('jacket_hem_',3.0)]:
   if prefix+side in rig.pose.bones:
    rot(prefix+side,(amount*math.sin(t*math.tau)*math.sin(t*math.pi)**2,sign*amount*.3*math.sin(t*math.tau),0))
