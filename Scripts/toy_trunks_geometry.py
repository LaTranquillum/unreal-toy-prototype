"""Reference-inspired toy geometry; shares the existing 17-bone blockout rig."""
import bpy, math
from mathutils import Vector

def build(ns):
 globals().update({k:ns[k] for k in ['finish','ell','box','segment','bones','mats']})
 def poly(name,verts,faces,mat,b):
  me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
  ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
  bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
  return finish(ob,name,mat,b)
 def loft(name,rings,mat,b,n=16):
  # rings: center x,y,z and elliptical radii x,y
  verts=[(x+rx*math.cos(i*2*math.pi/n),y+ry*math.sin(i*2*math.pi/n),z) for x,y,z,rx,ry in rings for i in range(n)]
  faces=[tuple(reversed(range(n))),tuple((len(rings)-1)*n+i for i in range(n))]
  for j in range(len(rings)-1):
   for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
  return poly(name,verts,faces,mat,b)
 def line(name,points,r,mat,b):
  curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=12;curve.bevel_depth=r;curve.bevel_resolution=2
  spl=curve.splines.new('BEZIER');spl.bezier_points.add(len(points)-1)
  for p,co in zip(spl.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
  ob=bpy.data.objects.new(name,curve);bpy.context.collection.objects.link(ob)
  bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
  return finish(bpy.context.object,name,mat,b)
 def plate(name,points,depth,mat,b):
  v=list(points)+[(x,y+depth,z) for x,y,z in points];n=len(points)
  f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
  ob=poly(name,v,f,mat,b)
  mod=ob.modifiers.new('Rounded seam','BEVEL');mod.width=.003;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
  for f in ob.data.polygons:f.use_smooth=False
  return ob
 # Fuller clothing silhouette, rigid articulated segments.
 loft('waist_hips',[(0,0,.77,.15,.095),(0,0,.85,.19,.12),(0,0,.94,.16,.105)],'Pants','pelvis')
 loft('black_tank_top',[(0,0,.95,.15,.095),(0,0,1.11,.175,.105),(0,0,1.27,.21,.12),(0,0,1.35,.14,.08)],'Pants','spine')
 box('cropped_jacket_back',(0,.075,1.225),(.46,.125,.32),'Jacket','chest')
 for s in [-1,1]:
  plate('open_jacket_panel',[(s*.225,-.10,1.36),(s*.095,-.135,1.335),(s*.075,-.135,1.085),(s*.215,-.10,1.075)],.045,'Jacket','chest')
  plate('raised_collar',[(s*.08,-.08,1.34),(s*.075,-.04,1.45),(s*.19,-.035,1.425),(s*.175,-.125,1.305)],.025,'Jacket','chest')
  line('collar_edge',[(s*.08,-.084,1.34),(s*.075,-.044,1.45),(s*.19,-.04,1.425)],.006,'Trim','chest')
  box('breast_pocket',(s*.159,-.145,1.215),(.085,.017,.092),'Jacket','chest')
  box('pocket_flap',(s*.159,-.158,1.253),(.09,.015,.021),'Trim','chest')
  ell('pocket_snap',(s*.159,-.169,1.247),(.007,.004,.007),'Steel','chest')
  line('jacket_hem',[(s*.075,-.159,1.085),(s*.21,-.127,1.08)],.008,'Trim','chest')
  line('front_seam',[(s*.088,-.163,1.105),(s*.10,-.161,1.29)],.004,'Trim','chest')
 box('belt',(0,-.01,.951),(.35,.245,.055),'Boots','pelvis')
 box('belt_buckle',(0,-.144,.951),(.078,.026,.065),'Steel','pelvis')
 box('buckle_inset',(0,-.160,.951),(.047,.008,.037),'Pants','pelvis')
 # Strap is split at chest/spine articulation; scabbard stays on chest.
 plate('shoulder_strap',[(-.182,-.174,1.37),(-.13,-.174,1.39),(.10,-.165,1.12),(.053,-.165,1.10)],.012,'Leather','chest')
 plate('strap_tail',[(.055,-.145,1.10),(.10,-.145,1.12),(.18,-.132,.99),(.135,-.132,.975)],.01,'Leather','spine')
 box('strap_buckle',(.056,-.189,1.135),(.067,.021,.07),'Steel','chest')
 box('strap_buckle_inner',(.056,-.204,1.135),(.041,.008,.046),'Leather','chest')
 segment('empty_scabbard',(.27,.16,.78),(-.23,.16,1.46),.048,'Leather','chest')
 segment('scabbard_rim',(-.207,.16,1.43),(-.23,.16,1.46),.057,'Boots','chest')
 # Angular jaw, smaller nose, readable serious eyes.
 ell('neck',(0,0,1.417),(.07,.066,.09),'Skin','head')
 loft('sculpted_head',[(0,-.025,1.435,.048,.056),(0,-.025,1.465,.088,.09),(0,-.015,1.535,.135,.117),(0,0,1.635,.14,.125),(0,.015,1.705,.11,.105),(0,.015,1.73,.055,.06)],'Skin','head',20)
 for s in [-1,1]:
  ell('ear',(s*.137,.0,1.553),(.025,.03,.05),'Skin','head')
  ell('ear_inner',(s*.151,-.023,1.553),(.012,.009,.026),'SkinShade','head')
  # Eyelids slope toward nose; use flat inlaid anime eyes.
  plate('eye_outline',[(s*.025,-.135,1.562),(s*.101,-.119,1.577),(s*.099,-.121,1.543),(s*.028,-.138,1.540)],.006,'Eyes','head')
  plate('eye_white',[(s*.028,-.142,1.560),(s*.096,-.128,1.574),(s*.094,-.131,1.546),(s*.031,-.144,1.542)],.002,'White','head')
  ell('iris',(s*.052,-.146,1.552),(.011,.002,.015),'Iris','head')
  ell('pupil',(s*.052,-.149,1.552),(.004,.0015,.011),'Eyes','head')
  line('eyebrow',[(s*.022,-.142,1.583),(s*.068,-.137,1.598),(s*.108,-.118,1.6)],.0045,'HairShade','head')
 poly('nose',[(0,-.133,1.576),(-.016,-.144,1.508),(.016,-.144,1.508),(0,-.178,1.52)],[(0,1,3),(0,3,2),(1,2,3),(0,2,1)],'Skin','head')
 line('mouth',[(-.032,-.13,1.483),(0,-.139,1.478),(.028,-.13,1.482)],.0018,'SkinShade','head')
 # Center-parted bob: sculpted tapered locks, rather than a spherical cap.
 loft('hair_back',[(0,.055,1.515,.135,.082),(0,.035,1.59,.159,.13),(0,.025,1.695,.16,.132),(0,.016,1.762,.10,.09),(0,.016,1.778,.025,.035)],'Hair','head',20)
 def lock(name,points,widths,mat):
  # Catmull-Rom samples keep the original silhouette but round the lock bends.
  old=[Vector(p) for p in points];ww=widths;points=[];widths=[]
  for j in range(len(old)-1):
   a,b,c,d=old[max(0,j-1)],old[j],old[j+1],old[min(len(old)-1,j+2)]
   for k in range(6):
    t=k/6;points.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t));widths.append(ww[j]*(1-t)+ww[j+1]*t)
  points.append(old[-1]);widths.append(ww[-1])
  verts=[];n=10
  for j,p in enumerate(points):
   p=Vector(p);d=Vector(points[min(j+1,len(points)-1)])-Vector(points[max(0,j-1)])
   tangent=d.normalized();across=Vector((0,-1,0)).cross(tangent).normalized();normal=tangent.cross(across).normalized()
   for i in range(n):
    a=i*2*math.pi/n;verts.append(p+across*(widths[j]*math.cos(a))+normal*(widths[j]*.38*math.sin(a)))
  faces=[tuple(reversed(range(n))),tuple((len(points)-1)*n+i for i in range(n))]
  for j in range(len(points)-1):
   for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
  poly(name,verts,faces,mat,'head')
 for s in [-1,1]:
  for i in range(6):
   pts=[(s*(.007+i*.010),-.045+i*.013,1.773-i*.003),(s*(.054+i*.017),-.108+i*.009,1.738),(s*(.094+i*.012),-.135+i*.012,1.665),(s*(.074+i*.018),-.146+i*.014,1.568+i*.008)]
   lock('parted_bang',pts,[.018,.027,.023,.0015],'Hair' if i%2 else 'HairLight')
   line('hair_groove',[(x,y-.008,z) for x,y,z in pts[:-1]],.0012,'HairShade','head')
  for i in range(3):
   lock('side_bob',[(s*.13,.015+i*.037,1.7),(s*.162,.01+i*.035,1.63),(s*.145,.025+i*.03,1.535)], [.028,.032,.003],'Hair')
 # Sleeves, folds, cuffs and tapered baggy trousers.
 for side,s in [('l',1),('r',-1)]:
  for bn,r in [('upperarm',.098),('lowerarm',.082)]:
   name=bn+'_'+side;a,b=bones[name];segment('sleeve_'+name,a,b,r,'Jacket',name)
  for bn in ['upperarm','lowerarm','thigh','calf']:
   name=bn+'_'+side;ell('joint_'+name,bones[name][0],(.062,)*3,'Pants',name)
  segment('cuff',bones['lowerarm_'+side][1]+Vector((0,0,.025)),bones['lowerarm_'+side][1]-Vector((0,0,.015)),.081,'Trim','lowerarm_'+side)
  ell('hand',(s*.374,-.032,.824),(.054,.048,.066),'Skin','hand_'+side)
  for j in range(3):line('finger_crease',[(s*.403,-.075,.84-j*.017),(s*.377,-.081,.84-j*.017)],.002,'SkinShade','hand_'+side)
  ell('thumb',(s*.337,-.062,.843),(.026,.027,.04),'Skin','hand_'+side)
  x=s*.12
  loft('baggy_thigh',[(x,0,.485,.085,.088),(x,0,.57,.117,.11),(x,0,.75,.119,.114),(x,0,.86,.103,.10)],'Pants','thigh_'+side)
  loft('baggy_shin',[(s*.13,0,.22,.073,.072),(s*.13,0,.32,.104,.10),(s*.13,0,.405,.099,.10),(s*.13,0,.49,.087,.087)],'Pants','calf_'+side)
  for z in [.34,.42]:line('trouser_fold',[(x-.065,-.075,z+.025),(x,-.104,z),(x+.067,-.076,z+.01)],.006,'PantsFold','calf_'+side)
  # Tall boots with black toes, gold inset panels and straps.
  loft('boot_shaft',[(s*.13,0,.10,.09,.091),(s*.13,0,.25,.082,.08),(s*.13,0,.30,.085,.083)],'Boots','foot_'+side)
  ell('boot_foot',(s*.13,-.085,.094),(.091,.166,.079),'Boots','foot_'+side)
  ell('black_toe',(s*.13,-.195,.075),(.087,.075,.06),'Pants','foot_'+side)
  box('sole',(s*.13,-.071,.026),(.18,.32,.037),'Pants','foot_'+side)
  for z in [.135,.235]:box('boot_strap',(s*.13,-.09,z),(.17,.022,.029),'Leather','foot_'+side)
  box('boot_front_panel',(s*.13,-.091,.187),(.092,.025,.063),'BootLight','foot_'+side)
  box('boot_cuff',(s*.13,0,.291),(.183,.178,.027),'BootLight','foot_'+side)
 # Capsule-style sleeve badge on the outward left arm, constructed as mesh curves.
 ell('badge_border',(.323,-.038,1.264),(.012,.063,.063),'Eyes','upperarm_l')
 ell('badge_red',(.339,-.039,1.264),(.008,.054,.054),'Badge','upperarm_l')
 # Fine raised concentric C emblem on the shoulder patch.
 for radius in [.039,.027]:
  line('capsule_C',[(.351,-.039+radius*math.cos(a),1.264+radius*math.sin(a)) for a in [math.radians(40+i*28) for i in range(11)]],.0035,'White','upperarm_l')
 line('capsule_bar',[(.352,-.015,1.264),(.352,.002,1.264)],.0035,'White','upperarm_l')

 # A flat diamond-section blade with a pointed tip, not a round rod.
 segment('sword_grip',(-.37,-.035,.835),(-.37,-.18,.835),.025,'HairShade','hand_r')
 for j in range(5):segment('grip_wrap',(-.37,-.045-j*.025,.835),(-.37,-.052-j*.025,.835),.027,'Steel','hand_r')
 ell('pommel',(-.37,-.016,.835),(.033,.027,.033),'Boots','hand_r')
 box('sword_guard',(-.37,-.197,.835),(.20,.034,.044),'Boots','hand_r')
 verts=[]
 for y,w in [(-.22,.032),(-.76,.028),(-.91,.001)]:verts.extend([(-.37-w,y,.835),(-.37,y,.847),(-.37+w,y,.835),(-.37,y,.823)])
 poly('diamond_blade',verts,[(0,3,2,1)]+[(j*4+i,j*4+(i+1)%4,(j+1)*4+(i+1)%4,(j+1)*4+i) for j in range(2) for i in range(4)],'Steel','hand_r')

 # Fine construction details modeled at toy scale; all follow existing bones.
 def stitch(name,a,b,bone,mat='Trim',count=12):
  a,b=Vector(a),Vector(b)
  for j in range(count):
   p=a.lerp(b,(j+.12)/count);q=a.lerp(b,(j+.62)/count)
   segment(name,p,q,.0009,mat,bone)
 def text_mesh(name,text,loc,size,bone):
  cu=bpy.data.curves.new(name,'FONT');cu.body=text;cu.size=size;cu.align_x='CENTER';cu.extrude=.00035;cu.resolution_u=3
  ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);ob.location=loc
  ob.rotation_euler=(math.pi/2,0,math.pi/2)
  bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
  finish(bpy.context.object,name,'White',bone)
 text_mesh('capsule_lettering','CAPSULE',(.349,-.039,1.22),.010,'upperarm_l')
 for s,side in [(-1,'r'),(1,'l')]:
  # Collar snaps, pocket topstitching and shoulder piping.
  ell('collar_snap',(s*.153,-.145,1.331),(.006,.003,.006),'Steel','chest')
  stitch('pocket_left_stitch',(s*.12,-.166,1.17),(s*.12,-.166,1.245),'chest',count=8)
  stitch('pocket_right_stitch',(s*.197,-.146,1.17),(s*.197,-.146,1.245),'chest',count=8)
  stitch('pocket_bottom_stitch',(s*.12,-.167,1.172),(s*.197,-.147,1.172),'chest',count=8)
  stitch('jacket_hem_stitch',(s*.089,-.166,1.097),(s*.21,-.127,1.092),'chest',count=14)
  line('shoulder_seam',[(s*.13,.055,1.382),(s*.22,.048,1.368),(s*.28,.015,1.32)],.003,'Trim','upperarm_'+side)
  line('sleeve_outer_seam',[(s*.326,-.092,1.27),(s*.363,-.083,1.16),(s*.368,-.073,1.12)],.002,'Trim','upperarm_'+side)
  line('forearm_fold',[(s*.31,-.060,1.045),(s*.355,-.084,1.025),(s*.39,-.065,1.018)],.0025,'Trim','lowerarm_'+side)
  ell('cuff_snap',(s*.398,-.088,.904),(.006,.004,.006),'Steel','lowerarm_'+side)
  # Belt loops and hanging keeper, matching the gold/black reference contrast.
  for x in [s*.085,s*.15]:box('belt_loop',(x,-.135,.951),(.017,.021,.073),'Pants','pelvis')
  # Boot inset frame, grooves, side clasp and sole treads.
  x=s*.13;bn='foot_'+side
  line('boot_panel_outline',[(x-.046,-.109,.151),(x-.046,-.11,.219),(x+.046,-.11,.219),(x+.046,-.109,.151)],.003,'Leather',bn)
  for z in [.169,.182,.195,.208]:line('boot_inset_groove',[(x-.032,-.108,z),(x+.032,-.108,z)],.0014,'Leather',bn)
  box('boot_strap_clasp',(x+s*.078,-.087,.235),(.022,.029,.037),'Steel',bn)
  box('boot_clasp_center',(x+s*.078,-.104,.235),(.012,.006,.022),'Leather',bn)
  for y in [-.18,-.13,-.08,-.03,.02,.06]:
   box('sole_tread',(x,y,.014),(.176,.014,.013),'Eyes',bn)
  line('boot_toe_seam',[(x-.072,-.191,.104),(x,-.226,.125),(x+.072,-.191,.104)],.0018,'BootLight',bn)
  # Knuckle separations are short recessed-color marks, not independent fingers.
  for j in range(3):ell('knuckle',(s*.38,-.067,.851-j*.018),(.021,.017,.012),'Skin','hand_'+side)
 # Belt holes, buckle prong and strap stitching.
 for x in [.035,.056,.077]:ell('belt_hole',(x,-.147,.951),(.0028,.002,.0028),'Eyes','pelvis')
 segment('buckle_prong',(-.025,-.163,.951),(.015,-.163,.951),.002,'Steel','pelvis')
 for dx in [-.013,.013]:stitch('strap_stitch',(-.153+dx,-.191,1.375),(.074+dx,-.183,1.125),'chest','BootLight',24)
 # Back yoke and garment seams visible in turnarounds.
 line('back_yoke',[(-.215,.142,1.30),(0,.149,1.285),(.215,.142,1.30)],.003,'Trim','chest')
 for s in [-1,1]:stitch('back_hem',(s*.018,.142,1.079),(s*.205,.142,1.079),'chest',count=18)
 # Scabbard ferrule and mounting bands, plus sword's fine central fuller.
 aa=Vector((.27,.16,.78));bb=Vector((-.23,.16,1.46))
 for u in [.04,.38,.78]:segment('scabbard_band',aa.lerp(bb,u),aa.lerp(bb,u+.025),.052,'Boots','chest')
 segment('scabbard_tip',aa,aa.lerp(bb,.055),.053,'BootLight','chest')
 line('blade_fuller',[(-.37,-.25,.849),(-.37,-.50,.849),(-.37,-.73,.849)],.0013,'Trim','hand_r')
 for s in [-1,1]:ell('guard_end',(-.37+s*.092,-.197,.835),(.022,.021,.026),'BootLight','hand_r')
