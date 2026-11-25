"""Tulā as a desktop unit, for the site's hero shot: the editor's own capture as the sloped front panel, real 3D knobs at real
height standing on the printed ones (each cap carries its own printed top and pointer), raised keys, a gold bezel and a glass
dome over the lotus, a crinkle wedge case on rubber feet, on the dark oak desk of the other heroes (the Noir studio's room and
lights). Replaces the old hero, a render of the site's GLB unit (tula_glb.py) in a black void with knobs 0.55 x their radius.

    CAP=<capture> [CYCLES_DEVICE=GPU] blender -b -noaudio -t 4 -P tula_desk.py -- <out.png> <samples> <res_x> <res_y>

The capture: tula_face_render <dir> (AudioCitraFree, headless), face_citra.png at 2x (1072 x 920 for the 536 x 460 editor), with
updateAutoCheck answered in the test data folder so no update strip shows (--manual: the same face with a drum loop playing
through four linked Tulās, so the lotus is lit; skins-citra.png, 958 x 822), and the resize grip in the corner painted out.
Positions come from skins/citra/layout.json (380 x 326 layout px, scaled to the editor). Env: LAYOUT = that layout.json;
KIT = a folder holding noir_plate_kit.py (default Agni's tools/skins); ROOM = the studio image the glossy parts mirror."""
import bpy, bmesh, json, math, os, sys
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
HOUT, HSAMP, RX, RY = os.path.abspath(argv[0]), int(argv[1]), int(argv[2]), int(argv[3])
CAP = os.environ["CAP"]
LAY = json.load(open(os.environ.get("LAYOUT", r"D:\AI\AudioCitraFree\skins\citra\layout.json"), encoding="utf-8"))
sys.path.insert(0, os.environ.get("KIT", r"D:\AI\Agni\tools\skins"))
import noir_plate_kit as K
W, H = 536, 460                                # editor px (the capture is 2x)
K.W, K.H = W, H
P, mat, box, bevel, smooth = K.P, K.mat, K.box, K.bevel, K.smooth
K.reset()
sc = bpy.context.scene
LK = W / LAY["size_1x"][0]                     # layout px -> editor px
CTL = {c["id"]: c for c in LAY["controls"]}
def rect(cid):
    x, y, w, h = CTL[cid]["rect"]; return x * LK, y * LK, (x + w) * LK, (y + h) * LK

MM_PER_PX = 240.0 / W                          # a desktop unit with a 240 mm face
MMU = 1.0 / MM_PER_PX / 100.0                  # scene units per mm
def knob_h(d_px):
    """the knob's height above the panel (scene units): 9 mm + 0.24 x its diameter, held to 12..20 mm"""
    return min(20.0, max(12.0, 9.0 + 0.24 * d_px * MM_PER_PX)) * MMU

# ---------- the capture ----------
img = bpy.data.images.load(CAP); cw, chh = img.size
pxs = np.empty(cw * chh * 4, np.float32); img.pixels.foreach_get(pxs); pxs = pxs.reshape(chh, cw, 4)
def ring_col(x, y, r0, r1):
    k = cw / W; yy, xx = np.mgrid[0:chh, 0:cw]; fy = (chh - 1 - yy) / k; fx = xx / k
    d2 = (fx - x) ** 2 + (fy - y) ** 2; m = (d2 >= r0 * r0) & (d2 <= r1 * r1)
    return tuple(float(v) for v in np.median(pxs[m][:, :3], axis=0))
def ring_col_rect(x0, y0, x1, y1):
    k = cw / W; a, b = int(x0 * k) + 2, int(x1 * k) - 2; c, d = int(y0 * k) + 2, int(y1 * k) - 2
    rows = pxs[chh - 1 - d:chh - 1 - c, a:b, :3]; edge = np.concatenate([rows[:3].reshape(-1, 3), rows[-3:].reshape(-1, 3)])
    return tuple(float(v) * 0.8 for v in np.median(edge, axis=0))
def print_mat(name, side, rough=0.3, coat=0.6, metal=0.0, emit=0.0):
    """the capture on every face that looks up (a knob's top, the panel), a plain side colour on the rest"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough; b.inputs["Coat Weight"].default_value = coat; b.inputs["Metallic"].default_value = metal
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = img; t.interpolation = "Cubic"
    tc = nt.nodes.new("ShaderNodeTexCoord"); sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Normal"], sp.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.93; mr.inputs["From Max"].default_value = 0.99
    nt.links.new(sp.outputs["Z"], mr.inputs["Value"])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; nt.links.new(mr.outputs[0], mx.inputs[0])
    mx.inputs[6].default_value = (*side, 1); nt.links.new(t.outputs["Color"], mx.inputs[7]); nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    if emit:
        e = nt.nodes.new("ShaderNodeMath"); e.operation = "MULTIPLY"; e.inputs[1].default_value = emit; nt.links.new(mr.outputs[0], e.inputs[0])
        nt.links.new(t.outputs["Color"], b.inputs["Emission Color"]); nt.links.new(e.outputs[0], b.inputs["Emission Strength"])
    return m
def planar_uv(o):
    uv = o.data.uv_layers[0] if o.data.uv_layers else o.data.uv_layers.new()
    for poly in o.data.polygons:
        for li in poly.loop_indices:
            v = o.matrix_world @ o.data.vertices[o.data.loops[li].vertex_index].co
            uv.data[li].uv = (v.x / (W / 100) + 0.5, v.y / (H / 100) + 0.5)
def upd(o): bpy.context.view_layer.update(); planar_uv(o); return o

# ---------- the panel (built face up at z = 0; the rig tilts it onto the case below) ----------
M_FACE = print_mat("face", (0.018, 0.012, 0.008), rough=0.55, coat=0.03, emit=0.1)
M_FACE.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.3   # a satin panel: the softbox must not grey it
PANEL = ring_col_rect(4, 4, W - 4, 10)
M_EDGE = mat("panel_edge", tuple(v / 0.8 for v in PANEL), rough=0.42, coat=0.4)
PW, PH = W / 100 + 0.04, H / 100 + 0.04
edge = box(0, 0, PW, PH, -3 * MMU, -0.002); edge.data.materials.append(M_EDGE); bevel(edge, 0.8 * MMU, 3, 40)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0)); face = bpy.context.object
face.scale = (W / 100, H / 100, 1); bpy.ops.object.transform_apply(scale=True); face.data.materials.append(M_FACE); planar_uv(face)

# ---------- the knobs: a gold skirt (the printed gold ring stands with it) under a black glass cap ----------
M_GOLD_SIDE = (0.55, 0.36, 0.14)
# Citra v2 (build 114): a wide black cap inside a thin bronze rim, measured on the capture: rim 0.87-0.955 of the knob's radius
for cid, (fr, fc) in (("trim", (0.555, 0.505)), ("out", (0.555, 0.505)), ("target", (0.555, 0.505)), ("width", (0.555, 0.505)), ("pan", (0.555, 0.505))):
    x0, y0, x1, y1 = rect(cid); x, y = (x0 + x1) / 2, (y0 + y1) / 2; d = x1 - x0
    rs, rc = d * fr * 0.86, d * fc * 0.86           # the gold ring's outer edge, the black cap's
    top = knob_h(2 * rs); hs = min(top * 0.3, 4 * MMU)
    cx, cy = P(x, y)
    bpy.ops.mesh.primitive_cylinder_add(vertices=160, radius=rs / 100, depth=hs, location=(cx, cy, hs / 2)); s = bpy.context.object
    s.data.materials.append(print_mat("skirt", M_GOLD_SIDE, rough=0.25, coat=0.3, metal=1.0)); bevel(s, rs / 100 * 0.06, 3); smooth(s); planar_uv(s)
    bpy.ops.mesh.primitive_cylinder_add(vertices=160, radius=rc / 100, depth=top - hs, location=(cx, cy, hs + (top - hs) / 2)); k = bpy.context.object
    k.data.materials.append(print_mat("knob", (0.012, 0.010, 0.016), rough=0.22, coat=0.9)); bevel(k, rc / 100 * 0.16, 8); smooth(k); planar_uv(k)

# ---------- the keys, the selectors' tracks, the lamps, the lotus window ----------
def key(x0, y0, x1, y1, h_mm, rad=None, side=None, rough=0.35, coat=0.5, metal=0.0, emit=0.0):
    side = side or ring_col_rect(x0, y0, x1, y1)
    rad = (y1 - y0) / 2 - 0.5 if rad is None else rad
    o = K.rrect(x0, y0, x1, y1, rad, 0.0, h_mm * MMU, "key"); o.data.materials.append(print_mat("keym", side, rough, coat, metal, emit))
    bevel(o, min(1.0 * MMU, (min(x1 - x0, y1 - y0) / 100.0) * 0.18), 3, 40); smooth(o, 40); return upd(o)
def dome(cx_, cy_, r, h_mm, emit=0.0):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=r / 100, location=(*P(cx_, cy_), 0)); o = bpy.context.object
    o.scale.z = h_mm * MMU / (r / 100); smooth(o, 80)
    o.data.materials.append(print_mat("domem", ring_col(cx_, cy_, r * 0.8, r), 0.15, 1.0, 0.0, emit)); return upd(o)
def ring(cx_, cy_, r0, r1, h_mm, metal=0.0, rough=0.3, side=None):
    side = side or ring_col(cx_, cy_, r0, r1)
    o = K.lathe([(r0 / 100, 0.0), (r1 / 100, 0.0), (r1 / 100, h_mm * MMU), (r0 / 100, h_mm * MMU)], 256, "ring")
    o.location = (*P(cx_, cy_), 0); o.data.materials.append(print_mat("ringm", side, rough, 0.5, metal)); bevel(o, 0.5 * MMU, 3, 40); smooth(o, 40)
    return upd(o)

# v2: LAW, ADV, FX, PHASE and MAP are bare words on the panel, printed flat
for cid in ("listen", "listen_all", "match", "mono", "link", "ab"):
    x0, y0, x1, y1 = rect(cid); key(x0 + 1, y0 + 1, x1 - 1, y1 - 1, 4.0)
for cid in ("detection", "pan_shape"):                     # the selector tracks stand low; their lit segment is printed on top
    x0, y0, x1, y1 = rect(cid)
    key(x0, y0, x1, y1, 2.0)
x0, y0, x1, y1 = rect("menu"); mc = ((x0 + x1) / 2, (y0 + y1) / 2)   # the lotus menu key: a round black key, no rim in v2
bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=(x1 - x0) / 2 / 100, depth=4 * MMU, location=(*P(*mc), 2 * MMU)); mk = bpy.context.object
mk.data.materials.append(print_mat("menukey", (0.02, 0.018, 0.026), 0.3, 0.6)); bevel(mk, 0.8 * MMU, 3); smooth(mk); upd(mk)
for cid in ("mono_lamp", "link_lamp"):
    x0, y0, x1, y1 = rect(cid); dome((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 + 0.5, 2.0, emit=0.4)
hx0, hy0, hx1, hy1 = rect("hero"); hc = ((hx0 + hx1) / 2, (hy0 + hy1) / 2)
ring(*hc, 117.5, 126.0, 4.0, metal=1.0, rough=0.22, side=M_GOLD_SIDE)   # the lotus window's gold bezel
M_GLASS = bpy.data.materials.new("glass"); M_GLASS.use_nodes = True; _g = M_GLASS.node_tree
for _n in list(_g.nodes): _g.nodes.remove(_n)
_tr = _g.nodes.new("ShaderNodeBsdfTransparent"); _gl = _g.nodes.new("ShaderNodeBsdfGlossy"); _gl.inputs["Roughness"].default_value = 0.12
_fr = _g.nodes.new("ShaderNodeFresnel"); _fr.inputs["IOR"].default_value = 1.5; _mx = _g.nodes.new("ShaderNodeMixShader"); _go = _g.nodes.new("ShaderNodeOutputMaterial")
_g.links.new(_fr.outputs[0], _mx.inputs[0]); _g.links.new(_tr.outputs[0], _mx.inputs[1]); _g.links.new(_gl.outputs[0], _mx.inputs[2]); _g.links.new(_mx.outputs[0], _go.inputs["Surface"])
bpy.ops.mesh.primitive_circle_add(vertices=256, radius=117.5 / 100, fill_type="NGON", location=(*P(*hc), 0.0005))   # the display glows behind the glass
disp = bpy.context.object; disp.data.materials.append(print_mat("display", (0, 0, 0), rough=0.6, coat=0.0, emit=float(os.environ.get("LOTUS_GLOW", "0.9")))); upd(disp)
bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=117.5 / 100, location=(*P(*hc), 0))
gd = bpy.context.object; gd.scale.z = 3.0 * MMU / 1.175; smooth(gd, 80); gd.data.materials.append(M_GLASS); gd.visible_shadow = False

# ---------- the case: a crinkle wedge under the sloped panel, rubber feet ----------
U = W / 1280.0                                 # the Noir studio's lights were sized for a 1280 px face
TILT = math.radians(float(os.environ.get("TILT", "32")))
FOOT = 4 * MMU; FRONT = 22 * MMU               # the case's front edge height above the feet
T = 3 * MMU                                    # the panel's thickness above the case top
M_CRINKLE = mat("crinkle", (0.012, 0.011, 0.014), rough=0.55)
nt = M_CRINKLE.node_tree; bs = nt.nodes["Principled BSDF"]
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 260; nz.inputs["Detail"].default_value = 6
bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.35
nt.links.new(nz.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], bs.inputs["Normal"])
M_RUBBER = mat("rubber", (0.01, 0.01, 0.01), rough=0.8)
rig = bpy.data.objects.new("rig", None); bpy.context.collection.objects.link(rig)
for o in list(bpy.data.objects):
    if o is not rig and o.parent is None: o.parent = rig
rig.rotation_euler = (TILT, 0, 0)
ca, sa = math.cos(TILT), math.sin(TILT)
MARGIN = 6 * MMU                               # the case stands this far round the panel
LB = PH / 2 + MARGIN
# local (y, z) -> world: y' = Y0 + y cos - z sin, z' = Z0 + y sin + z cos. The case top is local z = -T.
Y0 = 0.0; Z0 = FOOT + FRONT + LB * sa + T * ca
rig.location = (0, Y0, Z0)
def wpt(y, z): return (Y0 + y * ca - z * sa, Z0 + y * sa + z * ca)
fy, fz = wpt(-LB, -T); by, bz = wpt(LB, -T)
prof = [(fy, FOOT), (by, FOOT), (by, bz), (fy, fz)]
XW = PW / 2 + MARGIN
me = bpy.data.meshes.new("case"); bm = bmesh.new()
L_ = [bm.verts.new((-XW, y, z)) for y, z in prof]; R_ = [bm.verts.new((XW, y, z)) for y, z in prof]
bm.faces.new(L_[::-1]); bm.faces.new(R_)
for i in range(4):
    j = (i + 1) % 4; bm.faces.new((L_[i], L_[j], R_[j], R_[i]))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
case = bpy.data.objects.new("case", me); bpy.context.collection.objects.link(case); case.data.materials.append(M_CRINKLE)
bevel(case, 2.5 * MMU, 4, 40); smooth(case, 40)
for xx in (-XW + 14 * MMU, XW - 14 * MMU):
    for yy in (fy + 14 * MMU, by - 14 * MMU):
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=7 * MMU, depth=FOOT, location=(xx, yy, FOOT / 2))
        bpy.context.object.data.materials.append(M_RUBBER); bevel(bpy.context.object, 1 * MMU, 3); smooth(bpy.context.object)

# ---------- light and room (the Noir rack shots' studio), the oak desk ----------
K.room_and_lights(os.environ.get("ROOM", r"D:\AI\Galana\tools\noir\noir_room.png"), 4.0 * U, (1.0, 0.8, 0.62))
for o in bpy.data.objects:
    if o.type != "LIGHT": continue
    o.visible_camera = False
    if o.data.name == "cool": o.data.energy = 0
    if o.data.name == "key":                   # the key above the panel, from the upper left, tilted with it
        o.parent = rig; o.location = (-7 * U, 9 * U, 9 * U); o.data.energy = 900 * U * U; o.rotation_euler = (math.radians(-35), math.radians(-25), 0)
for o in bpy.data.objects:
    if o.active_material is not None and o.active_material.name == "room":
        o.parent = rig; o.active_material.node_tree.nodes["Emission"].inputs["Strength"].default_value = 0.35
M_GROUND = bpy.data.materials.new("ground"); M_GROUND.use_nodes = True; _dt = M_GROUND.node_tree; _db = _dt.nodes["Principled BSDF"]
_nz = _dt.nodes.new("ShaderNodeTexNoise"); _nz.inputs["Scale"].default_value = 1.0; _nz.inputs["Detail"].default_value = 12.0; _nz.inputs["Roughness"].default_value = 0.62
_tc = _dt.nodes.new("ShaderNodeTexCoord"); _mp = _dt.nodes.new("ShaderNodeMapping"); _mp.inputs["Scale"].default_value = (0.16 / U * 0.7, 4.5 / U * 0.7, 1.0)
_dt.links.new(_tc.outputs["Object"], _mp.inputs["Vector"]); _dt.links.new(_mp.outputs["Vector"], _nz.inputs["Vector"])
_cr = _dt.nodes.new("ShaderNodeValToRGB"); _cr.color_ramp.elements[0].color = (0.005, 0.003, 0.002, 1); _cr.color_ramp.elements[1].color = (0.020, 0.012, 0.008, 1)
_dt.links.new(_nz.outputs["Fac"], _cr.inputs["Fac"]); _dt.links.new(_cr.outputs["Color"], _db.inputs["Base Color"])
_db.inputs["Roughness"].default_value = 0.6; _db.inputs["Specular IOR Level"].default_value = 0.25
bpy.ops.mesh.primitive_plane_add(size=300, location=(0, 0, 0)); bpy.context.object.data.materials.append(M_GROUND)
def warea(name, loc, size, power, color, target=(0, 6, 3)):
    loc = tuple(v * U for v in loc); target = tuple(v * U for v in target)
    dl = bpy.data.lights.new(name, "AREA"); dl.shape = "RECTANGLE"; dl.size = size[0] * U; dl.size_y = size[1] * U; dl.energy = power * U * U; dl.color = color
    o = bpy.data.objects.new(name, dl); o.location = loc; bpy.context.collection.objects.link(o); o.visible_camera = False
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(); return o
warea("top", (0, 4, 16), (16, 10), 2000, (1.0, 0.93, 0.85), target=(0, 2, 2))
warea("rimR", (16, 18, 7), (2, 9), 900, (1.0, 0.75, 0.65), target=(0, 4, 2))
warea("rimL", (-16, 14, 5), (2, 7), 350, (0.6, 0.75, 1.0), target=(0, 4, 2))
_desk = bpy.data.collections.new("desk_only")
for _o in bpy.data.objects:
    if _o.type == "MESH" and _o.active_material is not None and _o.active_material.name == "ground": _desk.objects.link(_o)
for _o in bpy.data.objects:
    if _o.type == "LIGHT" and _o.name in ("rimR", "rimL", "top"):
        _o.light_linking.receiver_collection = _desk
        for _c in _desk.collection_objects: _c.light_linking.link_state = "EXCLUDE"
sc.view_settings.exposure = float(os.environ.get("EXPOSURE", "0.35"))
wn = sc.world.node_tree; N = wn.nodes; Lk = wn.links
bg = N["Background"]; lp = N.new("ShaderNodeLightPath"); env = N.new("ShaderNodeBackground"); env.inputs[0].default_value = (0.55, 0.45, 0.36, 1)
mxw = N.new("ShaderNodeMixShader"); Lk.new(lp.outputs["Is Glossy Ray"], mxw.inputs[0]); Lk.new(bg.outputs[0], mxw.inputs[1]); Lk.new(env.outputs[0], mxw.inputs[2])
Lk.new(mxw.outputs[0], N["World Output"].inputs["Surface"])
tcw = N.new("ShaderNodeTexCoord"); spw = N.new("ShaderNodeSeparateXYZ"); mrw = N.new("ShaderNodeMapRange")
mrw.inputs["From Min"].default_value = -0.6; mrw.inputs["From Max"].default_value = 0.9; mrw.inputs["To Min"].default_value = 0.06; mrw.inputs["To Max"].default_value = 0.35
Lk.new(tcw.outputs["Generated"], spw.inputs[0]); Lk.new(spw.outputs["Z"], mrw.inputs["Value"]); Lk.new(mrw.outputs["Result"], env.inputs[1])

# ---------- camera: front left, a little above the panel's slope ----------
cd = bpy.data.cameras.new("cam"); cd.dof.use_dof = True; cd.dof.aperture_fstop = 8; cd.lens = float(os.environ.get("LENS", "50"))
cam = bpy.data.objects.new("cam", cd); bpy.context.collection.objects.link(cam); sc.camera = cam
centre = Vector((0, *wpt(0, 0)))
cam.location = centre + Vector([float(v) for v in os.environ.get("CAMOFF", "-5.6,-14.5,8.2").split(",")])
target = centre + Vector((0.15, 0.0, -0.25))
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
cd.dof.focus_distance = (target - cam.location).length

sc.render.engine = "CYCLES"; sc.cycles.samples = HSAMP; sc.cycles.use_denoising = True; sc.cycles.use_adaptive_sampling = True
sc.cycles.sample_clamp_indirect = 3.0
sc.cycles.device = "CPU"; sc.render.threads_mode = "FIXED"; sc.render.threads = 4
if os.environ.get("CYCLES_DEVICE") == "GPU":
    cp = bpy.context.preferences.addons["cycles"].preferences; cp.compute_device_type = "OPTIX"; cp.get_devices()
    for dv in cp.devices: dv.use = dv.type == "OPTIX"
    sc.cycles.device = "GPU"
sc.render.resolution_x, sc.render.resolution_y = RX, RY; sc.render.resolution_percentage = 100
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
sc.render.filepath = HOUT
bpy.ops.render.render(write_still=True)
