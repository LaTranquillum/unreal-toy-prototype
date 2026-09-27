"""Continuous weighted sleeves and articulated hands fitted around the sword grip."""
import math
import bpy
from mathutils import Vector


def finger_paths(side):
    s=1 if side=='l' else -1
    # Four fingers wrap around the handle's Y axis. Rest geometry is already gripping.
    paths={}
    for i,name in enumerate(('index','middle','ring','pinky')):
        y=-.058-i*.026
        radius=.036-(.002 if i==3 else 0)
        paths[name]=[Vector((s*(.37+radius*math.cos(a)),y,.835+radius*math.sin(a)))
                     for a in (.95,.0,-1.15,-2.25)]
    paths['thumb']=[Vector((s*.400,-.035,.862)),Vector((s*.355,-.048,.878)),Vector((s*.344,-.085,.858))]
    return paths


def add_bones(bone):
    for side in ('l','r'):
        for name,points in finger_paths(side).items():
            parent='hand_'+side
            for j,(a,b) in enumerate(zip(points,points[1:])):
                bn=f'{name}_{j+1}_{side}';bone(bn,a,b,parent);parent=bn


def build(ns):
    parts,finish,ell,bones= [ns[k] for k in ('parts','finish','ell','bones')]
    def mesh(name,verts,faces,mat,bone):
        data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
        ob=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(ob)
        bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
        return finish(ob,name,mat,bone)
    def subdiv(ob):
        bpy.context.view_layer.objects.active=ob
        m=ob.modifiers.new('Tailored curvature','SUBSURF');m.levels=1;bpy.ops.object.modifier_apply(modifier=m.name)
        return ob
    def weights(ob,fn):
        ob.vertex_groups.clear()
        for v in ob.data.vertices:
            for name,value in fn(ob.matrix_world@v.co).items():
                if value>0:
                    group=ob.vertex_groups.get(name) or ob.vertex_groups.new(name=name)
                    group.add([v.index],value,'REPLACE')
    def smoothstep(a,b,x):
        t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
    def arm_weights(p,side):
        z=p.z
        if z>1.30:
            chest=.65*smoothstep(1.30,1.40,z)
            return {'chest':chest,'upperarm_'+side:1-chest}
        lower=1-smoothstep(1.025,1.16,z)
        hand=.25*(1-smoothstep(.875,.92,z))
        return {'upperarm_'+side:1-lower,'lowerarm_'+side:lower*(1-hand),'hand_'+side:lower*hand}
    remove=('cropped_jacket_back','open_jacket_panel','sleeve_','joint_upperarm','joint_lowerarm',
            'cuff','hand','thumb','finger_crease','knuckle','shoulder_seam','sleeve_outer_seam','forearm_fold')
    for ob in list(parts):
        if ob.name.startswith(remove):parts.remove(ob);bpy.data.objects.remove(ob,do_unlink=True)
    # Tailored open shell: front panels wrap continuously around sides and back.
    verts=[];rings=13;n=48
    for j in range(rings):
        t=j/(rings-1);z=1.075+t*.305
        rx=.207+.024*math.sin(t*math.pi)-.027*t**4
        ry=.119+.018*math.sin(t*math.pi)
        for i in range(n+1):
            angle=.34+(math.tau-.68)*i/n
            # Opening is at negative Y; smooth diagonal tension folds toward side seams.
            fold=.0028*math.sin(t*17+angle*3)*math.sin(t*math.pi)
            verts.append(((rx+fold)*math.sin(angle),-(ry+fold)*math.cos(angle),z))
    faces=[(j*(n+1)+i,j*(n+1)+i+1,(j+1)*(n+1)+i+1,(j+1)*(n+1)+i)
           for j in range(rings-1) for i in range(n)]
    jacket=subdiv(mesh('tailored_jacket_shell',verts,faces,'Jacket','chest'))
    mod=jacket.modifiers.new('Cloth thickness','SOLIDIFY');mod.thickness=.009
    bpy.ops.object.modifier_apply(modifier=mod.name)
    weights(jacket,lambda p:{'chest':smoothstep(1.09,1.23,p.z),'spine':1-smoothstep(1.09,1.23,p.z)})
    for side,s in [('l',1),('r',-1)]:
        verts=[];n=28;rings=25
        for j in range(rings):
            t=j/(rings-1);z=1.393-.505*t
            x=s*(.214+.158*t**.7);y=-.025*t*t
            # Flatter sleeve cap and tapered upper arm instead of a balloon shoulder.
            r=.042+.049*math.sin(min(1,t/.14)*math.pi/2)
            r*=1-.29*t
            # Restrained elbow compression creases integrated in the surface.
            fold=.004*math.sin((z-1.085)*105)*math.exp(-((z-1.085)/.075)**2)
            for i in range(n):
                a=math.tau*i/n
                cap_fold=.0022*math.cos(a*3+t*18)*math.exp(-((t-.24)/.15)**2)
                radius=r+cap_fold+fold*(.4+.6*max(0,-math.sin(a)))
                verts.append((x+radius*math.cos(a),y+radius*.92*math.sin(a),z))
        faces=[tuple(range(n-1,-1,-1)),tuple((rings-1)*n+i for i in range(n))]
        faces += [(j*n+i,(j+1)*n+i,(j+1)*n+(i+1)%n,j*n+(i+1)%n) for j in range(rings-1) for i in range(n)]
        sleeve=subdiv(mesh('continuous_sleeve_'+side,verts,faces,'Jacket','upperarm_'+side))
        weights(sleeve,lambda p:arm_weights(p,side))
        # Slim, rounded cuff instead of a separate large cone.
        cuff=ell('tailored_cuff_'+side,(s*.370,-.025,.899),(.068,.063,.023),'Trim','lowerarm_'+side)
        weights(cuff,lambda p:arm_weights(p,side))
        palm=ell('palm_'+side,(s*.407,-.089,.866),(.026,.063,.033),'Skin','hand_'+side)
        # Dense tubes carry smoothly blended weights across each phalanx.
        for name,points in finger_paths(side).items():
            verts=[];count=25;n=12
            for j in range(count):
                u=(len(points)-1)*j/(count-1);k=min(len(points)-2,int(u));t=u-k
                a,b=points[k],points[k+1];center=a.lerp(b,t)
                tangent=(b-a).normalized();across=Vector((0,1,0));normal=tangent.cross(across).normalized()
                r=(.012 if name=='thumb' else .0108)*(1-.24*j/(count-1))
                if j in (0,count-1):r*=.70
                for i in range(n):
                    angle=math.tau*i/n;verts.append(center+across*(math.cos(angle)*r)+normal*(math.sin(angle)*r))
            faces=[tuple(reversed(range(n))),tuple((count-1)*n+i for i in range(n))]
            faces += [(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(count-1) for i in range(n)]
            ob=mesh('finger_'+name+'_'+side,verts,faces,'Skin','hand_'+side)
            ob.vertex_groups.clear()
            for j in range(count):
                u=(len(points)-1)*j/(count-1)
                center=max(0,min(len(points)-2,u-.5));a=int(center);b=min(len(points)-2,a+1);f=center-a
                for k,w in ((a,1-f),(b,f)):
                    if w<=0:continue
                    bn=f'{name}_{k+1}_{side}';g=ob.vertex_groups.get(bn) or ob.vertex_groups.new(name=bn)
                    g.add(list(range(j*n,(j+1)*n)),w,'ADD')
            subdiv(ob)
            end=ell('fingertip_'+name+'_'+side,points[-1],(.008,.009,.009),'Skin',f'{name}_{len(points)-1}_{side}')
        # A discreet seam is a geometric inset, not an extra shoulder joint.
        for j in range(3):
            ell('cuff_button_'+side,(s*.397,-.080,.900+j*.004),(.003,.002,.003),'Steel','lowerarm_'+side)
