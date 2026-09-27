"""Continuous tailored trousers, small clothing hardware and authored secondary joints."""
import math
import bpy
from mathutils import Vector


def add_bones(bone):
    for side,s in [('l',1),('r',-1)]:
        bone('hair_tip_'+side,(s*.10,-.02,1.64),(s*.12,-.02,1.54),'head')
        bone('jacket_hem_'+side,(s*.16,0,1.16),(s*.16,0,1.07),'chest')


def build(ns):
    parts,finish,ell,box= [ns[k] for k in ('parts','finish','ell','box')]
    def smoothstep(a,b,x):
        t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
    for ob in list(parts):
        if ob.name.startswith(('waist_hips','baggy_thigh','baggy_shin','joint_thigh','joint_calf','trouser_fold')):
            parts.remove(ob);bpy.data.objects.remove(ob,do_unlink=True)
    # Join intersecting garment volumes before remeshing: no separate knee spheres.
    garment=[ell('trouser_hips',(0,.006,.846),(.177,.108,.111),'Pants','pelvis')]
    for side,s in [('l',1),('r',-1)]:
        verts=[];n=32;rows=37
        for j in range(rows):
            t=j/(rows-1);z=.273+.597*t;x=s*(.13-.014*t);y=.006
            r=.061+.026*math.sin(t*math.pi*.85)
            # Broad tension folds at knee and boot opening, not inflated limb segments.
            knee=.0035*math.sin((z-.49)*83)*math.exp(-((z-.49)/.068)**2)
            ankle=.002*math.sin((z-.30)*115)*math.exp(-((z-.30)/.04)**2)
            for i in range(n):
                a=math.tau*i/n;fold=(knee+ankle)*(.3+.7*max(0,-math.sin(a)))
                verts.append((x+(r+fold)*math.cos(a),y+(r*1.10+fold)*math.sin(a),z))
        faces=[tuple(reversed(range(n))),tuple((rows-1)*n+i for i in range(n))]
        faces += [(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(rows-1) for i in range(n)]
        data=bpy.data.meshes.new('Tailored trousers');data.from_pydata(verts,[],faces);data.update()
        ob=bpy.data.objects.new('trouser_leg_'+side,data);bpy.context.collection.objects.link(ob)
        bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
        garment.append(finish(ob,ob.name,'Pants','thigh_'+side))
    bpy.ops.object.select_all(action='DESELECT')
    for ob in garment:ob.select_set(True);parts.remove(ob)
    bpy.context.view_layer.objects.active=garment[0];bpy.ops.object.join();pants=bpy.context.object;pants.name='continuous_tailored_trousers'
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    remesh=pants.modifiers.new('Seamless garment volume','REMESH');remesh.mode='VOXEL';remesh.voxel_size=.006;remesh.use_smooth_shade=True
    bpy.ops.object.modifier_apply(modifier=remesh.name)
    sm=pants.modifiers.new('Cloth surface relaxation','SMOOTH');sm.factor=.7;sm.iterations=3;bpy.ops.object.modifier_apply(modifier=sm.name)
    parts.append(pants);pants.vertex_groups.clear()
    for v in pants.data.vertices:
        side='l' if v.co.x>=0 else 'r';z=v.co.z
        pelvis=smoothstep(.75,.875,z);calf=1-smoothstep(.425,.56,z)
        for name,w in [('pelvis',pelvis),('thigh_'+side,(1-pelvis)*(1-calf)),('calf_'+side,(1-pelvis)*calf)]:
            if w>0:
                g=pants.vertex_groups.get(name) or pants.vertex_groups.new(name=name);g.add([v.index],w,'REPLACE')
    # Add small zipper teeth along the jacket opening and flatter hem fasteners.
    for s in (-1,1):
        for j in range(16):
            z=1.11+j*.012
            box('zipper_tooth',(s*.078,-.128,z),(.005,.004,.003),'Steel','chest')
        box('hem_fastener',(s*.176,-.119,1.096),(.021,.009,.011),'Steel','chest')
    # Replace overlarge raised piping with a narrower construction edge.
    for ob in parts:
        if ob.name.startswith(('collar_edge','jacket_hem','front_seam')):
            center=sum((v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices)
            for v in ob.data.vertices:v.co.y=center.y+(v.co.y-center.y)*.45
        if ob.name.startswith('continuous_sleeve'):
            for v in ob.data.vertices:v.co.y*=.90
        if ob.name.startswith(('side_layer','loose_fringe')):
            ob.vertex_groups.clear()
            for v in ob.data.vertices:
                p=ob.matrix_world@v.co;side='l' if p.x>0 else 'r'
                w=.45*(1-smoothstep(1.54,1.66,p.z))
                for name,weight in [('head',1-w),('hair_tip_'+side,w)]:
                    if weight>0:
                        g=ob.vertex_groups.get(name) or ob.vertex_groups.new(name=name);g.add([v.index],weight,'REPLACE')
        if ob.name=='tailored_jacket_shell':
            # Preserve existing torso weights while adding a small hem influence.
            for v in ob.data.vertices:
                w=.30*(1-smoothstep(1.075,1.16,v.co.z));side='l' if v.co.x>0 else 'r'
                if w>0:
                    for vg in list(v.groups):ob.vertex_groups[vg.group].add([v.index],vg.weight*(1-w),'REPLACE')
                    g=ob.vertex_groups.get('jacket_hem_'+side) or ob.vertex_groups.new(name='jacket_hem_'+side);g.add([v.index],w,'REPLACE')
