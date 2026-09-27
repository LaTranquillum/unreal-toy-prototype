"""Shared material finish values for Blender and Unreal; no external textures."""
FINISH={
 'Jacket':(.72,0,.32),'Trim':(.65,0,.32),'Pants':(.84,0,.24),'PantsFold':(.84,0,.24),
 'Leather':(.57,0,.36),'Boots':(.49,0,.38),'BootLight':(.46,0,.38),
 'Steel':(.25,.85,.50),'Hair':(.30,0,.46),'HairLight':(.30,0,.46),'HairShade':(.34,0,.42),
 'Skin':(.57,0,.28),'SkinShade':(.60,0,.25),'White':(.25,0,.38),'Iris':(.20,0,.45),'Eyes':(.32,0,.30),'Badge':(.75,0,.28)}
FABRIC={'Jacket','Trim','Pants','PantsFold','Badge'}

def blender_materials(mats):
    for name,mat in mats.items():
        bs=mat.node_tree.nodes.get('Principled BSDF');rough,metal,spec=FINISH.get(name,(.5,0,.35))
        bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
        bs.inputs['Specular IOR Level'].default_value=spec
        if name in FABRIC:bs.inputs['Sheen Weight'].default_value=.16
        if name.startswith('Hair') and bs.inputs.get('Anisotropic'):bs.inputs['Anisotropic'].default_value=.25
        if name in FABRIC or name in ('Leather','Boots','BootLight','Steel'):
            nodes=mat.node_tree.nodes;links=mat.node_tree.links
            tex=nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=260 if name in FABRIC else 90
            tex.inputs['Detail'].default_value=2
            coord=nodes.new('ShaderNodeTexCoord');links.new(coord.outputs['UV'],tex.inputs['Vector'])
            ramp=nodes.new('ShaderNodeMapRange');ramp.inputs['To Min'].default_value=rough-.035;ramp.inputs['To Max'].default_value=rough+.035
            links.new(tex.outputs['Fac'],ramp.inputs['Value']);links.new(ramp.outputs['Result'],bs.inputs['Roughness'])
            bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.10;bump.inputs['Distance'].default_value=.0003
            links.new(tex.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],bs.inputs['Normal'])
