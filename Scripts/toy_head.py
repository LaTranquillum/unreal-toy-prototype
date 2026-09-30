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
    # A continuous neck column with a broad root and a jaw insertion,
    # rather than an ellipsoid with pinched ends and a swollen middle.
    smooth(loft('neck',[
        (0,.016,1.325,.063,.045),
        (0,.016,1.350,.058,.044),
        (0,.015,1.377,.044,.039),
        (0,.014,1.410,.038,.036),
        (0,.012,1.444,.039,.037),
        (0,.010,1.470,.045,.041),
        (0,.008,1.487,.049,.044)],'Skin','head',48),2)
    # Dense continuous facial surface: nose and cheek planes are part of the head.
    rings=[(1.437,.018,.038,-.016),(1.451,.041,.063,-.014),
           (1.478,.077,.094,-.002),(1.505,.105,.109,.001),
           (1.532,.124,.118,.004),(1.558,.127,.118,.006),
           (1.588,.131,.122,.009),(1.632,.135,.121,.012),
           (1.681,.120,.110,.015),(1.718,.088,.087,.018),
           (1.740,.010,.012,.018)]
    dense=[]
    for i in range(len(rings)-1):
        a,b,c,d=[Vector(rings[max(0,min(len(rings)-1,k))]) for k in (i-1,i,i+1,i+2)]
        for j in range(8):
            t=j/8
            z,rx,ry,y=.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
            dense.append((0,y,z,rx,ry))
    z,rx,ry,y=rings[-1];dense.append((0,y,z,rx,ry))
    head=loft('sculpted_head',dense,'Skin','head',96)
    def gaussian(value,center,width):return math.exp(-((value-center)/width)**2)
    for v in head.data.vertices:
        x,y,z=v.co
        if y<-.025:
            front=max(0,min(1,(-y-.025)/.06))
            nose=.011*gaussian(x,0,.016)*gaussian(z,1.532,.020)
            bridge=.0025*gaussian(x,0,.020)*gaussian(z,1.562,.028)
            brow=.004*gaussian(abs(x),.061,.044)*gaussian(z,1.581,.010)
            cheek=.0025*gaussian(abs(x),.083,.033)*gaussian(z,1.529,.015)
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
            a=j*math.tau/40;x=s*(.058+.039*math.cos(a))
            z=1.554+.018*math.sin(a)+.005*math.cos(a)
            pts.append((x,surface_y(x)-.002,z))
        eye=poly('curved_almond_eye',[(s*.058,surface_y(.058)-.003,1.554)]+pts,
            # Mirroring X reverses winding: keep both eye fronts pointing toward -Y.
            [(0,j+1,(j+1)%40+1) if s>0 else (0,(j+1)%40+1,j+1)
             for j in range(40)],'White','head');tag(eye,'eye')
        assert all(face.normal.y < 0 for face in eye.data.polygons), 'Eye surface faces inward'
        for upper in (True,False):
            path=[]
            for j in range(17):
                a=(j/16*math.pi) if upper else (math.pi+j/16*math.pi)
                x=s*(.058+.039*math.cos(a));z=1.554+.018*math.sin(a)+.005*math.cos(a)
                path.append((x,surface_y(x)-.004,z))
            tag(line('upper_lid' if upper else 'lower_lid',path,.0019 if upper else .00065,
                'Eyes' if upper else 'SkinShade','head'),'upper_lid' if upper else 'lower_lid')
        # Skin eyelid sheet slides down over the iris during Blink.
        lidverts=[]
        for row in range(2):
            for j in range(41):
                a=j*math.pi/40;x=s*(.058+.039*math.cos(a))
                z=1.554+(.018+.009*row)*math.sin(a)+.005*math.cos(a)
                lidverts.append((x,surface_y(x)-.008+row*.005,z))
        lidfaces=[(41+j,42+j,j+1,j) if s>0 else (j,j+1,42+j,41+j) for j in range(40)]
        tag(poly('upper_eyelid_skin',lidverts,lidfaces,'Skin','head'),'blink_lid')
        x=s*.053;y=surface_y(x)-.004
        tag(ell('iris',(x,y,1.554),(.013,.0014,.014),'Iris','head'),'iris')
        tag(ell('pupil',(x,y-.0016,1.554),(.005,.0008,.010),'Eyes','head'),'iris')
        tag(ell('eye_glint',(x-s*.002,y-.0025,1.558),(.0018,.0007,.002),'White','head'),'iris')
        # The left brow has a slightly raised outer arch, not mirrored geometry.
        lift=.0035 if s>0 else -.0005
        browpts=[(s*.023,-.118,1.575),(s*.054,-.112,1.583+lift),(s*.094,-.096,1.585+lift*.6)]
        browverts=browpts+[(x,y-.0003,z+w) for (x,y,z),w in zip(browpts,(.0025,.004,.0004))]
        tag(poly('tapered_brow',browverts,[(0,1,4,3),(1,2,5,4)] if s>0 else [(3,4,1,0),(4,5,2,1)],'Eyes','head'),'brow')
        line('lid_crease',[(s*.031,-.116,1.577),(s*.066,-.110,1.580),
            (s*.096,-.096,1.575)],.0007,'SkinShade','head')
    # Nostril accents sit on the continuous nose surface.
    for s in (-1,1):
        ell('nostril',(s*.0055,-.129,1.521),(.0014,.0007,.0007),'SkinShade','head')
    # A restrained mouth sits on the lower facial surface rather than floating ahead of it.
    tag(ell('mouth_cavity',(0,-.104,1.493),(.021,.001,.0012),'Eyes','head'),'mouth')
    tag(line('upper_lip',[(-.021,-.103,1.494),(-.007,-.106,1.495),
        (0,-.1065,1.4945),(.008,-.106,1.495),(.021,-.103,1.494)],.0008,'SkinShade','head'),'upper_lip')
    tag(line('lower_lip',[(-.017,-.103,1.492),(0,-.106,1.491),(.017,-.103,1.492)],.0007,'Skin','head'),'lower_lip')
    tag(ell('upper_teeth',(0,-.103,1.493),(.016,.0007,.0004),'White','head'),'teeth')
    tag(ell('tongue',(0,-.103,1.493),(.013,.0006,.0004),'SkinShade','head'),'tongue')
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
            lock('fringe_layer',[(s*(.003+i*.019),-.025+i*.012,1.775-i*.004),
                (s*(.030+i*.027),-.101+i*.013,1.755-i*.011),
                (s*(.043+i*.026),-.129+i*.019,1.683-i*.008),
                (s*(.040+i*.029),-.139+i*.023,1.567+i*.017+(s+1)*.007)],
                [.008,.035-i*.002,.029-i*.002,.0007])
        for i in range(4):
            lock('side_layer',[(s*.104,.027+i*.027,1.739-i*.009),
                (s*.151,.028+i*.031,1.676-i*.008),
                (s*.156,.029+i*.029,1.594),
                (s*.130,.041+i*.026,1.530+i*.006)],[.014,.032,.025,.0007])
        lock('loose_fringe',[(s*.009,-.054,1.779),(s*.041,-.130,1.748),
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
                    seam=1.549+.005*(abs(x)-.058)/.039
                    if role=='eye':
                        p.z=seam+(z-seam)*.015
                    elif role in ('upper_lid','lower_lid'):
                        c=max(-1,min(1,(abs(x)-.058)/.039))
                        arch=.018*math.sqrt(max(0,1-c*c))
                        nominal=1.554+.005*c+(arch if role=='upper_lid' else -arch)
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
                    p.z=1.553+(z-1.553)*(.84 if name=='Focused' else .90)
                elif name=='Shout':
                    if role=='jaw':
                        if y<-.05:
                            p.y+=.016*math.exp(-(x/.029)**2-((z-1.491)/.018)**2)
                        p.z-=.019*max(0,min(1,(1.525-z)/.075))
                    elif role=='mouth':
                        p.x*=1.08;p.z=1.488+(z-1.493)*9;p.y-=.001
                    elif role=='upper_lip':p.z+=.006;p.y-=.001
                    elif role=='lower_lip':p.z-=.016;p.y-=.001
                    elif role=='teeth':p.z=1.495+(z-1.493)*5;p.y-=.002
                    elif role=='tongue':p.z=1.480+(z-1.493)*5;p.y-=.002
                v.co=inv@p


def reference_proportions(parts):
    """Apply matching proportions to Basis and all morphs to retain expression closure."""
    mouth_roles={'mouth','upper_lip','lower_lip','teeth','tongue'}
    for ob in parts:
        if not ob.vertex_groups.get('head'):continue
        role=ob.get('face_role','')
        hair=ob.name.startswith(('hair_back','fringe_layer','side_layer','loose_fringe','nape_layer'))
        inv=ob.matrix_world.inverted()
        for key in ob.data.shape_keys.key_blocks:
            for v in key.data:
                p=ob.matrix_world@v.co
                if ob.name!='neck' and p.z<1.554:
                    p.z=1.554+(p.z-1.554)*.96
                if role in mouth_roles:
                    p.x*=.88
                    p.z-=.003
                if hair:
                    p.x*=.93
                    if p.z>1.63:p.z+=.012*min(1,(p.z-1.63)/.09)
                v.co=inv@p
