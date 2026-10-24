# Lahari hero render: a chassis whose face is the plugin's own capture (3x), with real 3D knobs placed from the skin spec.
# blender -b --factory-startup --python lahari_hero.py -- skin=analog cap=<dir> spec=<dir> out=<file> samples=64 [preview=1]
import bpy, sys, json, math, os
from mathutils import Vector

A = dict(a.split('=', 1) for a in sys.argv[sys.argv.index('--') + 1:])
SKIN = A['skin']; CAP = A['cap']; SPEC = json.load(open(os.path.join(A['spec'], SKIN + '.spec.json'), encoding='utf-8'))
W, H = SPEC['size']; S = 1.0 / W          # 1 unit = panel width
D = 0.07 if A['skin'] == 'pedal' else 0.045    # chassis depth (the pedal is a deep die-cast box)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

def mat(name, col, metal=0.0, rough=0.4, img=None, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Metallic'].default_value = metal; b.inputs['Roughness'].default_value = rough
    if img:
        t = m.node_tree.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(img); t.interpolation = 'Cubic'
        N, Lk = m.node_tree.nodes, m.node_tree.links
        g = N.new('ShaderNodeNewGeometry'); sx = N.new('ShaderNodeSeparateXYZ'); cx = N.new('ShaderNodeCombineXYZ')
        mu = N.new('ShaderNodeMath'); mu.operation = 'MULTIPLY_ADD'; mu.inputs[1].default_value = 1.0; mu.inputs[2].default_value = 0.5
        mv = N.new('ShaderNodeMath'); mv.operation = 'MULTIPLY_ADD'; mv.inputs[1].default_value = 1.0 / (H * S); mv.inputs[2].default_value = 0.5
        Lk.new(g.outputs['Position'], sx.inputs[0]); Lk.new(sx.outputs[0], mu.inputs[0]); Lk.new(sx.outputs[1], mv.inputs[0])
        Lk.new(mu.outputs[0], cx.inputs[0]); Lk.new(mv.outputs[0], cx.inputs[1]); Lk.new(cx.outputs[0], t.inputs['Vector'])
        m.node_tree.links.new(t.outputs['Color'], b.inputs['Base Color'])
        if emit:  # displays/lamps read as lit: a little of the capture as emission
            m.node_tree.links.new(t.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = emit
    return m

def px(x, y):  # panel pixel -> world (panel centred at origin, top face at z=0)
    return Vector(((x - W / 2) * S, (H / 2 - y) * S, 0))

# chassis: bevelled box, face slightly inset
bpy.ops.mesh.primitive_cube_add(size=1)
body = bpy.context.object; body.scale = (1.0 + 0.012, H * S + 0.012, D); body.location.z = -D / 2 - 0.0005
bv = body.modifiers.new('b', 'BEVEL'); bv.width = 0.022 if SKIN == 'pedal' else 0.006; bv.segments = 8
body.data.materials.append(mat('body', {'analog': (0.03, 0.028, 0.026), 'pedal': (0.05, 0.05, 0.055)}.get(SKIN, (0.04, 0.04, 0.045)), 0.6, 0.35))
bpy.ops.object.shade_smooth()

bpy.ops.mesh.primitive_plane_add(size=1)
face = bpy.context.object; face.scale = (1.0, H * S, 1)
face_m = mat('face', (1, 1, 1), 0.0, 0.42, os.path.join(CAP, SKIN + '.png'), emit=0.08 if SKIN == 'analog' else 0.15)
face_m.node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value = 0.5 if SKIN == 'analog' else 0.25
face.data.materials.append(face_m)

# knobs from the spec: every rotary control, sized from its bounds
DEF = {'rate': 0.5, 'depth': 0.5, 'delay': 0.5, 'feedback': 0.5, 'width': 0.5, 'tone': 1.0, 'mix': 0.5, 'output': 24 / 36}
cap_m = mat('cap', (0.78, 0.78, 0.8), 1.0, 0.22)
skirt_m = mat('skirt', {'analog': (0.02, 0.02, 0.02)}.get(SKIN, (0.62, 0.63, 0.66)), 1.0 if SKIN != 'analog' else 0.0, 0.3)
ptr_m = mat('ptr', (0.9, 0.08, 0.04) if SKIN == 'pedal' else (0.95, 0.93, 0.88), 0.0, 0.4)
for c in SPEC['controls']:
    if c.get('type') not in ('rotary', 'stepped') or 'centre' not in c and c.get('type') == 'stepped' and False: continue
    x, y, w, h = c['bounds']; cx, cy = c.get('centre', (x + w / 2, y + h / 2)); r = (0.34 if c.get('type') == 'rotary' else 0.30) * min(w, h) * S
    p = px(cx, cy)
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=r, depth=r * 0.4, location=(p.x, p.y, r * 0.2))
    sk = bpy.context.object; sk.data.materials.append(skirt_m)
    m = sk.modifiers.new('b', 'BEVEL'); m.width = r * 0.08; m.segments = 4; bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=r * 0.7, depth=r * 0.3, location=(p.x, p.y, r * 0.4 + r * 0.15))
    cp = bpy.context.object; cp.data.materials.append(cap_m)
    m = cp.modifiers.new('b', 'BEVEL'); m.width = r * 0.1; m.segments = 5; bpy.ops.object.shade_smooth()
    a = math.radians(135 - 270 * DEF.get(c['id'], 0.5))    # 0 -> -135 deg (left), 1 -> +135 deg
    bpy.ops.mesh.primitive_cube_add(size=1, location=(p.x, p.y, r * 0.7 + 0.0004))
    pt = bpy.context.object; pt.scale = (r * 0.08, r * 0.55, 0.0008); pt.rotation_euler.z = a - math.pi / 2 + math.pi / 2
    pt.location.x += -math.sin(a) * r * 0.36 * 0 + math.cos(a + math.pi / 2) * r * 0.36
    pt.location.y += math.sin(a + math.pi / 2) * r * 0.36
    pt.rotation_euler.z = a; pt.data.materials.append(ptr_m)


# ---- the rest of the hardware: raised keys, bezels and glass, lamps, switches, jacks ----
chrome = mat('chrome', (0.85, 0.85, 0.87), 1.0, 0.12)
bezel_m = mat('bezel', (0.05, 0.05, 0.05), 0.3, 0.35) if SKIN == 'analog' else chrome
def glassm():
    m = bpy.data.materials.new('glass'); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.9, 0.92, 0.95, 1); b.inputs['Roughness'].default_value = 0.05
    b.inputs['Alpha'].default_value = 0.10; b.inputs['Specular IOR Level'].default_value = 0.25; return m
glass = glassm()
def box(x, y, w, h, z0, z1, m, bev=0.0015):
    p = px(x + w / 2, y + h / 2)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(p.x, p.y, (z0 + z1) / 2)); o = bpy.context.object
    o.scale = (w * S, h * S, z1 - z0); o.data.materials.append(m)
    if bev: b = o.modifiers.new('b', 'BEVEL'); b.width = bev; b.segments = 3; b.limit_method = 'NONE'
    return o
def key(x, y, w, h, hgt=0.006, side=None, bev=None):   # a raised part: solid body, its printed art on a thin cap
    b = min(w, h) * S * 0.12 if bev is None else bev
    if side is None: box(x, y, w, h, -0.001, hgt, face_m, bev=b); return
    box(x, y, w, h, -0.001, hgt - 0.0004, side, bev=b)
    i = b / S * 0.9; box(x + i, y + i, w - 2 * i, h - 2 * i, hgt - 0.0012, hgt, face_m, bev=0)
def frame(x, y, w, h, t, hgt, m):   # four bars round a window
    box(x - t, y - t, w + 2 * t, t, 0, hgt, m); box(x - t, y + h, w + 2 * t, t, 0, hgt, m)
    box(x - t, y, t, h, 0, hgt, m); box(x + w, y, t, h, 0, hgt, m)
def window(x, y, w, h, t=5, hgt=0.006, glazed=True, m=None):
    frame(x, y, w, h, t, hgt, m or bezel_m)
    if glazed: box(x, y, w, h, hgt * 0.8, hgt * 0.8 + 0.0006, glass, bev=0)
def lamp(cx, cy, r, col, lit):
    p = px(cx, cy)
    bpy.ops.mesh.primitive_torus_add(major_radius=r * S, minor_radius=r * S * 0.22, location=(p.x, p.y, r * S * 0.15))
    bpy.context.object.data.materials.append(chrome); bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r * S * 0.85, location=(p.x, p.y, 0)); d = bpy.context.object
    d.scale.z = 0.7; m = mat('lamp', col, 0.0, 0.15); b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Coat Weight'].default_value = 1.0
    if lit: b.inputs['Emission Color'].default_value = (*col, 1); b.inputs['Emission Strength'].default_value = 6.0
    d.data.materials.append(m); bpy.ops.object.shade_smooth()
def bat(cx, cy, up=True):
    p = px(cx, cy)
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.011, depth=0.004, location=(p.x, p.y, 0.002)); bpy.context.object.data.materials.append(chrome)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.0035, depth=0.03, location=(p.x, p.y + (0.007 if up else -0.007), 0.016))
    l = bpy.context.object; l.rotation_euler.x = math.radians(-25 if up else 25); l.data.materials.append(chrome); bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0048, location=(p.x, p.y + (0.0135 if up else -0.0135), 0.03)); bpy.context.object.data.materials.append(chrome); bpy.ops.object.shade_smooth()

C = {c['id']: c for c in SPEC['controls']}
def B(i): return C[i]['bounds']
if SKIN == 'analog':
    bake0 = mat('bakelite0', (0.86, 0.83, 0.75), 0.0, 0.3)
    for i in ('presetPrev', 'presetNext'): key(*B(i), 0.008, bake0, 0.0016)
    x, y, w, h = B('program'); kh = (h - 2 * 8) / 3
    bake = mat('bakelite', (0.86, 0.83, 0.75), 0.0, 0.3)
    for k in range(3): key(x, y + k * (kh + 8), w, kh, 0.009, bake, 0.0016)
    window(*B('presetDisplay'), t=4, glazed=False)
    for i in ('meterIn', 'meterOut'):
        x, y, w, h = B(i); window(x + 8, y + 8, w - 16, h - 16, t=7, hgt=0.008)
    x, y, w, h = B('logo'); frame(x + 2, y + 2, w - 4, h - 4, 3, 0.004, mat('brass', (0.8, 0.6, 0.3), 1.0, 0.25))
    x, y, w, h = B('bypassLamp'); lamp(x + w / 2, y + h / 2, w * 0.42, (1.0, 0.08, 0.05), True)
    x, y, w, h = B('lfoLamp'); lamp(x + w / 2, y + h / 2, w * 0.40, (1.0, 0.35, 0.12), True)
    x, y, w, h = B('bypass'); bat(x + w / 2, y + h / 2, True)
else:
    alu = mat('alu', (0.78, 0.78, 0.8), 1.0, 0.32); teal = mat('teal', (0.08, 0.32, 0.36), 0.2, 0.35)
    key(44, 20, 812, 314, 0.0045, alu, 0.0015)          # the brushed control plate, a separate screwed-on panel
    key(44, 344, 812, 82, 0.0025, teal, 0.0008)         # the printed label band
    blk = mat('blk', (0.015, 0.015, 0.015), 0.2, 0.35)
    x, y, w, h = B('program'); cxs = [x + w * f for f in (1 / 6, 1 / 2, 5 / 6)]
    for cxk in cxs:
        frame(cxk - 13, y + 22, 26, 26, 2.5, 0.0065, chrome); key(cxk - 13, y + 22, 26, 26, 0.009, blk, 0.0012)
    # the footswitch treadle: chrome frame, ribbed rubber pad on a hinge
    key(286, 438, 328, 108, 0.012, chrome, 0.004)
    rub = mat('rubber', (0.025, 0.025, 0.027), 0.0, 0.85)
    box(304, 460, 292, 76, 0.011, 0.02, rub, bev=0.003)
    for k in range(7):
        p0 = px(450, 470 + k * 9.6)
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.0022, depth=284 * S, location=(p0.x, p0.y, 0.0205))
        o = bpy.context.object; o.rotation_euler.y = math.pi / 2; o.data.materials.append(rub); bpy.ops.object.shade_smooth()
    p0 = px(450, 446)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.004, depth=318 * S, location=(p0.x, p0.y, 0.013))
    o = bpy.context.object; o.rotation_euler.y = math.pi / 2; o.data.materials.append(chrome); bpy.ops.object.shade_smooth()
    # LED ladders: a recessed black bar, twelve real LED segments (seven lit, as captured)
    cols = [(0.1, 1, 0.25)] * 8 + [(1, 0.55, 0.05)] * 2 + [(1, 0.08, 0.04)] * 2
    for x0 in (58, 624):
        box(x0, 471, 216, 18, -0.001, 0.0035, blk, bev=0.001)
        for k in range(12):
            c = cols[k]; lit = k < 7
            m = mat('led', tuple(v * (1 if lit else 0.035) for v in c), 0.0, 0.2)
            if lit: b = m.node_tree.nodes['Principled BSDF']; b.inputs['Emission Color'].default_value = (*c, 1); b.inputs['Emission Strength'].default_value = 5
            box(x0 + 4 + k * 17.6, 476, 13.5, 8, 0.002, 0.0048, m, bev=0.0006)
    x, y, w, h = B('checkLed'); frame(x, y, w, h, 3, 0.004, chrome); box(x, y, w, h, 0, 0.003, mat('led', (1, 0.15, 0.05), 0, 0.2), bev=0.0005)
    C2 = C['rateLed']; lamp(*C2['centre'], 7, (1.0, 0.2, 0.05), True)
    for i in ('jackIn', 'jackOut'):
        x, y, w, h = B(i); p = px(x + w / 2, y + h / 2)
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.012, depth=0.02, location=(p.x + (0.012 if i == 'jackIn' else -0.012), p.y, -D / 2))
        o = bpy.context.object; o.rotation_euler.y = math.pi / 2; o.data.materials.append(chrome)

# floor, lights, camera
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -D - 0.001))
bpy.context.object.data.materials.append(mat('floor', (0.004, 0.004, 0.005), 0.0, 0.6))
def area(loc, power, size, col=(1, 1, 1)):
    bpy.ops.object.light_add(type='AREA', location=loc); L = bpy.context.object; L.data.energy = power; L.data.size = size; L.data.color = col
    L.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
area((-0.9, 0.7, 1.0), 45, 1.2, (1, 0.95, 0.88))       # key, upper left (the spec's light source)
area((1.0, -0.2, 0.5), 8, 0.8, (0.8, 0.9, 1))         # cool fill
area((0.0, 1.2, 0.35), 25, 1.6, (1, 0.9, 0.8))        # rim along the back edge

bpy.ops.object.camera_add(location=(0.55, -1.38, 0.86))
cam = bpy.context.object; sc.camera = cam
cam.rotation_euler = (Vector((0.0, 0.02, -0.03)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 58; cam.data.dof.use_dof = True; cam.data.dof.focus_distance = (cam.location - Vector((0.05, -0.05, 0))).length; cam.data.dof.aperture_fstop = 5.6

w = sc.world = bpy.data.worlds.new('w'); w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.02
sc.render.engine = 'CYCLES'; sc.cycles.samples = int(A.get('samples', 64)); sc.cycles.use_denoising = True
sc.render.threads_mode = 'FIXED'; sc.render.threads = 4
sc.render.resolution_x, sc.render.resolution_y = (960, 540) if A.get('preview') else (1920, 1080)
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
sc.render.filepath = A['out']; sc.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
