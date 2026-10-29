# Spanda hero render: a dark chassis whose face is the plug-in's own capture (full editor at 150%).
# blender -b --factory-startup --python spanda_hero.py -- cap=<png> out=<png> [tx=0.5 ty=0.5 dist=1.6 az=-28 el=24 lens=50 samples=48 w=1280 h=720]
# tx/ty = camera target on the face (0..1 from top-left); dist = camera distance in panel widths.
import bpy, sys, math
from mathutils import Vector

A = dict(a.split('=', 1) for a in sys.argv[sys.argv.index('--') + 1:])
f = lambda k, d: float(A.get(k, d))
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
img = bpy.data.images.load(A['cap']); W, H = img.size; AR = H / W; D = 0.06

def mat(name, col, metal=0.0, rough=0.4):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Metallic'].default_value = metal; b.inputs['Roughness'].default_value = rough
    return m

# chassis: bevelled dark-anodised box, face plate sits just proud of it
bpy.ops.mesh.primitive_cube_add(size=1); body = bpy.context.object
body.scale = (1.03, AR + 0.03, D); body.location.z = -D / 2
bv = body.modifiers.new('b', 'BEVEL'); bv.width = 0.008; bv.segments = 8
body.data.materials.append(mat('body', (0.025, 0.025, 0.03), 0.8, 0.3)); bpy.ops.object.shade_smooth()

bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.0004)); face = bpy.context.object; face.scale = (1, AR, 1)
m = mat('face', (1, 1, 1), 0.0, 0.55); N, L = m.node_tree.nodes, m.node_tree.links; b = N['Principled BSDF']
t = N.new('ShaderNodeTexImage'); t.image = img; t.interpolation = 'Cubic'
L.new(t.outputs['Color'], b.inputs['Base Color']); L.new(t.outputs['Color'], b.inputs['Emission Color'])
b.inputs['Emission Strength'].default_value = 0.8; b.inputs['Coat Weight'].default_value = 0.0; b.inputs['Specular IOR Level'].default_value = 0.15; b.inputs['Coat Roughness'].default_value = 0.08
face.data.materials.append(m)

# four corner screws
chrome = mat('chrome', (0.8, 0.8, 0.82), 1.0, 0.18)
for sx in (-1, 1):
    for sy in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.006, depth=0.002, location=(sx * 0.508, sy * (AR / 2 + 0.008), 0.0))
        bpy.context.object.data.materials.append(chrome); bpy.ops.object.shade_smooth()

bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, -D - 0.001))
bpy.context.object.data.materials.append(mat('floor', (0.006, 0.006, 0.008), 0.3, 0.25))

def area(loc, power, size, col):
    bpy.ops.object.light_add(type='AREA', location=loc); l = bpy.context.object; l.data.energy = power; l.data.size = size; l.data.color = col
    l.rotation_euler = (-Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
area((-1.0, 0.8, 1.1), 40, 1.4, (1, 0.94, 0.86))
area((1.1, -0.3, 0.6), 8, 1.0, (0.8, 0.88, 1))
area((0.0, 1.4, 0.4), 30, 2.0, (1, 0.88, 0.8))

tgt = Vector(((f('tx', .5) - .5), (.5 - f('ty', .5)) * AR, 0))
az, el, dist = math.radians(f('az', -28)), math.radians(f('el', 24)), f('dist', 1.6)
d = Vector((math.sin(-az) * math.sin(el), -math.cos(az) * math.sin(el), math.cos(el)))  # el=0 straight down, 90 = grazing
bpy.ops.object.camera_add(location=tgt + dist * d); cam = bpy.context.object; sc.camera = cam
cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = f('lens', 50); cam.data.dof.use_dof = True; cam.data.dof.focus_distance = dist; cam.data.dof.aperture_fstop = f('fstop', 4)

w = sc.world = bpy.data.worlds.new('w'); w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.02
sc.render.engine = 'CYCLES'; sc.cycles.samples = int(f('samples', 48)); sc.cycles.use_denoising = True
sc.render.threads_mode = 'FIXED'; sc.render.threads = 4
sc.render.resolution_x, sc.render.resolution_y = int(f('w', 1280)), int(f('h', 720))
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
sc.render.filepath = A['out']; sc.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)


