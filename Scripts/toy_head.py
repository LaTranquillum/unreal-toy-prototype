"""Sculpted anime toy face with expressions and independent eyelid closure; neutral is Basis."""
import math
import bpy
from mathutils import Vector


def build_head(ns):
    ell, loft, line, poly = (ns[k] for k in ('ell', 'loft', 'line', 'poly'))
    def tag(ob, role):
        ob['face_role'] = role
        return ob
    def smooth(ob, levels=1):
        bpy.context.view_layer.objects.active=ob
        mod=ob.modifiers.new('Sculpted surface','SUBSURF');mod.levels=levels
        bpy.ops.object.modifier_apply(modifier=mod.name)
        return ob
    ell('neck',(0,0,1.417),(.07,.066,.09),'Skin','head')
    # Dense continuous facial surface: nose and cheek planes are part of the head.
    rings=[(1.431,.014,.033,-.021),(1.444,.036,.062,-.022),
           (1.468,.074,.089,-.012),(1.505,.108,.109,.001),
           (1.532,.132,.118,.004),(1.558,.127,.118,.006),
           (1.588,.131,.122,.009),(1.632,.135,.121,.012),
           (1.681,.120,.110,.015),(1.718,.088,.087,.018),
           (1.740,.010,.012,.018)]
    dense=[]
    for a,b in zip(rings,rings[1:]):
        for j in range(6):
            t=j/6;z,rx,ry,y=[a[k]*(1-t)+b[k]*t for k in range(4)]
            dense.append((0,y,z,rx,ry))
    z,rx,ry,y=rings[-1];dense.append((0,y,z,rx,ry))
    head=loft('sculpted_head',dense,'Skin','head',96)
    def gaussian(value,center,width):return math.exp(-((value-center)/width)**2)
    for v in head.data.vertices:
        x,y,z=v.co
        if y<-.025:
            front=max(0,min(1,(-y-.025)/.06))
            nose=.026*gaussian(x,0,.012)*gaussian(z,1.530,.026)
            bridge=.007*gaussian(x,0,.017)*gaussian(z,1.562,.028)
            brow=.004*gaussian(abs(x),.061,.044)*gaussian(z,1.581,.010)
            cheek=.006*gaussian(abs(x),.083,.033)*gaussian(z,1.529,.015)
            socket=.004*gaussian(abs(x),.059,.028)*gaussian(z,1.554,.014)
            v.co.y+=front*(socket-nose-bridge-brow-cheek)
    tag(smooth(head,1),'jaw')
    # Eye fronts now sit close to the sockets rather than on raised plates.
    def surface_y(x):return -.112 + .027*(abs(x)/.105)**2
    for s in (-1,1):
        smooth(ell('ear',(s*.132,.007,1.546),(.023,.030,.045),'Skin','head'))
        ell('ear_concha',(s*.144,-.015,1.545),(.011,.009,.024),'SkinShade','head')
        line('ear_helix',[(s*.145,-.022,1.522),(s*.154,-.019,1.55),
            (s*.144,-.015,1.578),(s*.130,-.014,1.564)],.004,'Skin','head')
        line('ear_inner_fold',[(s*.143,-.026,1.528),(s*.137,-.028,1.549),
            (s*.145,-.023,1.560)],.0025,'Skin','head')
        pts=[]
        for j in range(40):
            a=j*math.tau/40;x=s*(.061+.042*math.cos(a))
            z=1.554+.012*math.sin(a)+.004*math.cos(a)
            pts.append((x,surface_y(x)-.002,z))
        eye=poly('curved_almond_eye',[(s*.061,surface_y(.061)-.003,1.554)]+pts,
            # Mirroring X reverses winding: keep both eye fronts pointing toward -Y.
            [(0,j+1,(j+1)%40+1) if s>0 else (0,(j+1)%40+1,j+1)
             for j in range(40)],'White','head');tag(eye,'eye')
        assert all(face.normal.y < 0 for face in eye.data.polygons), 'Eye surface faces inward'
        for upper in (True,False):
            path=[]
            for j in range(17):
                a=(j/16*math.pi) if upper else (math.pi+j/16*math.pi)
                x=s*(.061+.042*math.cos(a));z=1.554+.012*math.sin(a)+.004*math.cos(a)
                path.append((x,surface_y(x)-.004,z))
            tag(line('upper_lid' if upper else 'lower_lid',path,.0026 if upper else .0012,
                'Eyes' if upper else 'SkinShade','head'),'upper_lid' if upper else 'lower_lid')
        # Skin eyelid sheet slides down over the iris during Blink.
        lidverts=[]
        for row in range(2):
            for j in range(41):
                a=j*math.pi/40;x=s*(.061+.042*math.cos(a))
                z=1.554+(.012+.010*row)*math.sin(a)+.004*math.cos(a)
                lidverts.append((x,surface_y(x)-.008+row*.005,z))
        lidfaces=[(41+j,42+j,j+1,j) if s>0 else (j,j+1,42+j,41+j) for j in range(40)]
        tag(poly('upper_eyelid_skin',lidverts,lidfaces,'Skin','head'),'blink_lid')
        x=s*.053;y=surface_y(x)-.004
        tag(ell('iris',(x,y,1.554),(.008,.0014,.010),'Iris','head'),'iris')
        tag(ell('pupil',(x,y-.0016,1.554),(.0035,.0008,.0075),'Eyes','head'),'iris')
        tag(ell('eye_glint',(x-s*.002,y-.0025,1.558),(.0018,.0007,.002),'White','head'),'iris')
        # The left brow has a slightly raised outer arch, not mirrored geometry.
        lift=.0035 if s>0 else -.0005
        tag(line('brow',[(s*.022,-.119,1.579),(s*.058,-.112,1.587+lift),
            (s*.098,-.094,1.589+lift*.6)],.0028,'HairShade','head'),'brow')
        line('lid_crease',[(s*.031,-.116,1.577),(s*.066,-.110,1.580),
            (s*.096,-.096,1.575)],.0007,'SkinShade','head')
    # Nostril accents sit on the continuous nose surface.
    for s in (-1,1):
        ell('nostril',(s*.007,-.137,1.517),(.0023,.001,.001),'SkinShade','head')
    # Closed slit in Basis expands into a rounded open mouth in Shout.
    tag(ell('mouth_cavity',(0,-.120,1.487),(.027,.0015,.0018),'Eyes','head'),'mouth')
    tag(line('upper_lip',[(-.027,-.121,1.488),(-.009,-.124,1.490),
        (0,-.125,1.489),(.009,-.124,1.490),(.027,-.121,1.488)],.0013,'SkinShade','head'),'upper_lip')
    tag(line('lower_lip',[(-.024,-.121,1.486),(0,-.125,1.484),(.024,-.121,1.486)],.0011,'SkinShade','head'),'lower_lip')
    # Teeth and tongue are collapsed behind the slit in neutral and exposed by the target.
    tag(ell('upper_teeth',(0,-.119,1.487),(.022,.0007,.0005),'White','head'),'teeth')
    tag(ell('tongue',(0,-.119,1.487),(.016,.0006,.0005),'SkinShade','head'),'tongue')
    # A smooth rear volume supports three overlapping layers of tapered locks.
    back=smooth(loft('hair_back',[(0,.055,1.522,.096,.059),(0,.051,1.552,.135,.086),
        (0,.035,1.63,.143,.113),(0,.019,1.71,.145,.119),
        (0,.012,1.757,.11,.097),(0,.012,1.785,.048,.047),
        (0,.012,1.789,.007,.009)],'Hair','head',40),2)
    # Recess the hidden front of the rear volume so the part reveals forehead.
    for v in back.data.vertices:
        x,y,z=v.co
        if y<0 and z<1.756:
            v.co.y+=.115*max(0,1-abs(x)/.13)*min(1,(1.756-z)/.025)
    def lock(name,controls,widths):
        ps=[Vector(p) for p in controls];points=[];ws=[]
        for j in range(len(ps)-1):
            a,b,c,d=ps[max(0,j-1)],ps[j],ps[j+1],ps[min(len(ps)-1,j+2)]
            for k in range(10):
                t=k/10
                points.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
                u=t*t*(3-2*t);ws.append(widths[j]*(1-u)+widths[j+1]*u)
        points.append(ps[-1]);ws.append(widths[-1]);verts=[];n=16
        for j,p in enumerate(points):
            tangent=(points[min(j+1,len(points)-1)]-points[max(j-1,0)]).normalized()
            across=Vector((0,-1,0)).cross(tangent).normalized();normal=tangent.cross(across).normalized()
            for i in range(n):
                a=math.tau*i/n
                verts.append(p+across*(ws[j]*math.cos(a))+normal*(ws[j]*.30*math.sin(a)))
        faces=[tuple(reversed(range(n))),tuple((len(points)-1)*n+i for i in range(n))]
        faces += [(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i)
            for j in range(len(points)-1) for i in range(n)]
        smooth(poly(name,verts,faces,'Hair','head'))
    # Overlapping nape locks break up the smooth helmet edge from rear angles.
    for i in range(9):
        x=(i-4)*.028
        lock('nape_layer',[(x*.70,.094,1.742),(x*.94,.148,1.659),
            (x,.139,1.566),(x*1.02,.105,1.512+.009*(i%3))],
            [.008,.026,.021,.0006])
    for s in (-1,1):
        # Broad asymmetric fringe sweeps away from a readable center part.
        for i in range(4):
            lock('fringe_layer',[(s*(.006+i*.019),-.025+i*.012,1.775-i*.004),
                (s*(.049+i*.027),-.101+i*.013,1.755-i*.011),
                (s*(.070+i*.026),-.129+i*.019,1.683-i*.008),
                (s*(.064+i*.029),-.139+i*.023,1.567+i*.017+(s+1)*.007)],
                [.008,.035-i*.002,.029-i*.002,.0007])
        for i in range(4):
            lock('side_layer',[(s*.104,.027+i*.027,1.739-i*.009),
                (s*.151,.028+i*.031,1.676-i*.008),
                (s*.156,.029+i*.029,1.594),
                (s*.130,.041+i*.026,1.530+i*.006)],[.014,.032,.025,.0007])
        lock('loose_fringe',[(s*.014,-.054,1.779),(s*.041,-.130,1.748),
            (s*.063,-.154,1.667),(s*.053,-.151,1.592)],[.005,.011,.008,.0003])


def add_expressions(parts):
    """Create the same keys before join so Blender retains all facial deltas."""
    for ob in parts:
        # Reduce upper-face height by 22%; apply to head-bound geometry only.
        if ob.vertex_groups.get('head'):
            inv=ob.matrix_world.inverted()
            for v in ob.data.vertices:
                p=ob.matrix_world@v.co
                if p.z>1.595:p.z=1.595+(p.z-1.595)*.78
                v.co=inv@p
        ob.shape_key_add(name='Basis')
        role=ob.get('face_role','')
        inv=ob.matrix_world.inverted()
        for name in ('Focused','Shout','Blink'):
            key=ob.shape_key_add(name=name)
            if not role:continue
            for index,v in enumerate(key.data):
                p=ob.matrix_world@v.co;x,y,z=p
                if name=='Blink':
                    seam=1.548+.004*(abs(x)-.061)/.042
                    if role=='eye':
                        p.z=seam+(z-seam)*.015
                    elif role in ('upper_lid','lower_lid'):
                        c=max(-1,min(1,(abs(x)-.061)/.042))
                        arch=.012*math.sqrt(max(0,1-c*c))
                        nominal=1.554+.004*c+(arch if role=='upper_lid' else -arch)
                        p.z+=seam-nominal;p.y-=.003
                    elif role=='iris':
                        p.z=seam+(z-seam)*.015;p.y+=.006
                    elif role=='blink_lid' and index<41:
                        p.z=seam;p.y+=.006
                    v.co=inv@p
                    continue
                if role=='brow':
                    p.z -= (.007 if name=='Focused' else .011)*max(0,1-abs(x)/.115)
                elif role in ('eye','iris','upper_lid','lower_lid','blink_lid'):
                    p.z=1.553+(z-1.553)*(.72 if name=='Focused' else .85)
                elif name=='Shout':
                    if role=='jaw':
                        p.z-=.019*max(0,min(1,(1.525-z)/.075))
                    elif role=='mouth':
                        p.x*=1.1;p.z=1.481+(z-1.487)*12;p.y-=.011
                    elif role=='upper_lip':p.z+=.010;p.y-=.009
                    elif role=='lower_lip':p.z-=.025;p.y-=.008
                    elif role=='teeth':p.z=1.496+(z-1.487)*7;p.y-=.014
                    elif role=='tongue':p.z=1.467+(z-1.487)*6;p.y-=.014
                v.co=inv@p
