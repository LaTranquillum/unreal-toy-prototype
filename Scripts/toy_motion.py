"""Authored in-place toy motion, with continuous anticipation and recovery."""
import math
from mathutils import Vector,Quaternion

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
  rot('lowerarm_l',(3*breath,0,0));rot('lowerarm_r',(1.5*breath,0,0))
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
  lift=curve([(0,0),(wind,65),(contact,72),(follow,48),(.78,20),(1,0)])
  sweep=curve([(0,0),(wind,-48),(contact,22),(follow,52),(.78,22),(1,0)])
  torso=curve([(0,0),(wind,-22),(contact,15),(follow,28),(.78,10),(1,0)])
  settle=curve([(0,0),(wind,.35),(contact,1),(follow,.75),(1,0)])
  rot('pelvis',(0,0,torso*.22));rot('spine',(5*settle,0,torso*.25));rot('chest',(0,0,torso*.53));rot('head',(-3*settle,0,-torso*.35))
  rot('upperarm_r',(lift,-8*settle,sweep));rot('lowerarm_r',(curve([(0,0),(wind,38),(contact,9),(follow,12),(1,0)]),0,0))
  rot('hand_r',(0,0,-sweep*.15));rot('upperarm_l',(-18*settle,0,-15*settle));rot('lowerarm_l',(25*settle,0,0))
  move('pelvis',(0,0,-.018*settle));rot('thigh_l',(7*settle,0,0));rot('calf_l',(-12*settle,0,0));rot('thigh_r',(6*settle,0,0));rot('calf_r',(-10*settle,0,0))
